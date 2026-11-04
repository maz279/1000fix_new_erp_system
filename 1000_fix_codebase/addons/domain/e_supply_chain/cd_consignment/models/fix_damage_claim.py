# fix_damage_claim — M03 damage claims against a consignment. The claim records
# what was damaged in transit, the claimed value and the adjudication; it is the
# record behind the Damage & Claims report.
#
# A02 audit (2026-11-03) M03-5/6: the payout approval had no group, no
# segregation of duties, a decorative tier, no ceiling and no pin — a plain
# user approved a BDT 200,000 Tier-4 claim, BDT 900,000 was approved on a
# BDT 10,000 claim declared at BDT 5,000, and an amount approved at 4,000 was
# raised to 400,000 and settled. The approval now runs through fix.dofa.mixin
# (the tier is derived from the amount, the approver must hold the tier and
# the claim-approver role, and must not be the claim's creator), the payout
# is capped at the claim and at the insured value, the approved amount is
# pinned, and settlement publishes the amount for finance.
#
# A02 audit B1 (P1): the payout approval is a routed M63 request. The claim
# handler asks for it (Request Approval); the engine routes it to the claim
# approvers who hold the DOFA tier of the payout, and action_approve runs only
# from the approver's inbox. Segregation of duties, the ceiling and the pin
# are unchanged.
from odoo import api, fields, models
from odoo.addons.cd_entity_config.models.fix_dofa import DOFA_TIERS
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

GROUP_CLAIM_APPROVER = "cd_consignment.group_fix_damage_claim_approver"
GROUP_MANAGER = "cd_consignment.group_fix_logistics_manager"

# Fields fixed once the claim has been decided (approved, rejected, settled):
# the approval covered THIS claim on THIS consignment.
DECIDED_LOCKED = frozenset(
    {
        "consignment_id",
        "claimed_amount",
        "requested_payout",
        "currency_id",
        "claimant",
        "damage_kind",
        "liability",
    }
)


class FixApprovalMatrixClaim(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("damage_claim", "Consignment Damage-Claim Payout")],
        ondelete={"damage_claim": "cascade"},
    )


class FixDamageClaim(models.Model):
    _name = "fix.damage.claim"
    _description = "Consignment Damage Claim"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "claimed_on desc, id desc"

    # A02 audit B1: approved from the inbox, never by pressing Approve.
    _approval_domain = "damage_claim"
    _approval_apply_method = "action_approve"
    _approval_routed = True

    # The payout ladder from the M03 spec: Tier 2 up to BDT 15,000, Tier 3 up
    # to BDT 50,000, Tier 4 above. Thresholds are policy numbers (today's).
    _DOFA_CLAIM_THRESHOLDS = [
        (15000.0, "tier_2"),
        (50000.0, "tier_3"),
        (float("inf"), "tier_4"),
    ]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", required=True)
    consignment_id = fields.Many2one(
        "fix.consignment", string="Consignment", required=True, ondelete="cascade", index=True
    )
    claimed_on = fields.Date(required=True, default=fields.Date.context_today)
    claimant = fields.Selection(
        [
            ("customer", "Customer"),
            ("branch", "Branch"),
            ("rider", "Rider"),
            ("courier", "Courier Partner"),
        ],
        required=True,
        default="customer",
    )
    damage_kind = fields.Selection(
        [
            ("physical", "Physical Damage"),
            ("missing", "Missing / Short"),
            ("water", "Water / Liquid"),
            ("packaging", "Packaging Failure"),
            ("other", "Other"),
        ],
        required=True,
        default="physical",
    )
    description = fields.Text(required=True)
    claimed_amount = fields.Monetary(currency_field="currency_id")
    # A02 audit B1: the inbox approves what was put to it. The handler states
    # the payout asked for (blank = the amount claimed) before requesting.
    requested_payout = fields.Monetary(
        currency_field="currency_id",
        string="Payout Requested",
        copy=False,
        help="The payout put to the approver. Blank: the amount claimed. Cannot "
        "exceed the claim; a change while approval is pending withdraws the request.",
    )
    approved_amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The payout the approver signed off. Set only by the approve action.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    evidence_ref = fields.Char(help="Photo / scan reference for the damage.")
    liability = fields.Selection(
        [
            ("pending", "Pending"),
            ("carrier", "Carrier"),
            ("branch", "Branch"),
            ("customer", "Customer"),
            ("shared", "Shared"),
        ],
        required=True,
        default="pending",
    )
    state = fields.Selection(
        [
            ("open", "Open"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("settled", "Settled"),
        ],
        required=True,
        default="open",
        tracking=True,
        readonly=True,
        copy=False,
    )

    # --- A02 Enterprise Data Capture & DOFA Adjudication Tier ---
    # A02 audit M03-5: this tier was a stored compute nothing read. It now
    # shows the tier the DOFA gate enforces (dofa_tier_required).
    dofa_tier = fields.Selection(
        DOFA_TIERS,
        string="DOFA Adjudication Tier",
        compute="_compute_dofa_tier",
        store=True,
    )
    approved_by_id = fields.Many2one(
        "res.users",
        string="DOFA Adjudication Approver",
        readonly=True,
        copy=False,
    )
    approved_at = fields.Datetime(string="Approved At", readonly=True, copy=False)
    rejected_by_id = fields.Many2one("res.users", string="Rejected By", readonly=True, copy=False)
    rejection_reason = fields.Char(readonly=True, copy=False)
    settled_amount = fields.Monetary(
        currency_field="currency_id", string="Settled Amount", readonly=True, copy=False
    )
    settled_at = fields.Datetime(string="Settled At", readonly=True, copy=False)
    settled_by_id = fields.Many2one("res.users", string="Settled By", readonly=True, copy=False)
    incident_photo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Transit Damage Photo / Forensic Report",
    )

    # ------------------------------------------------------------ DOFA hooks
    def _dofa_amount(self) -> float:
        """The payout at risk: the approved amount once one is set, else the
        payout requested, else the amount claimed."""
        self.ensure_one()
        return self.approved_amount or self.requested_payout or self.claimed_amount or 0.0

    def _dofa_thresholds(self):
        return self._DOFA_CLAIM_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "damage claim %s payout of BDT %.2f" % (self.name, self._dofa_amount())

    def _claim_ceiling(self) -> float:
        """What the consignment was insured for: its declared value, else the
        carrier's transit liability cap. 0 means no insured basis."""
        self.ensure_one()
        consignment = self.consignment_id.sudo()
        if consignment.declared_value_bdt > 0:
            return consignment.declared_value_bdt
        return consignment.courier_partner_id.insurance_max_bdt or 0.0

    def _dofa_current_tier(self) -> str:
        """A02 audit M03-5: a payout above the insured value (declared value,
        else the carrier's cap) needs one tier more than its amount, and never
        less than Tier 4 (CFO / COO). A consignment with no insured basis is
        treated as insured for 0."""
        tier = super()._dofa_current_tier()
        if tier == "tier_0":
            return tier
        amount = abs(self._dofa_amount() or 0.0)
        if amount > self._claim_ceiling() + 0.005:
            order = [t[0] for t in DOFA_TIERS]
            bumped = max(order.index(tier) + 1, order.index("tier_4"))
            tier = order[min(bumped, len(order) - 1)]
        return tier

    @api.depends(
        "claimed_amount",
        "requested_payout",
        "approved_amount",
        "consignment_id.declared_value_bdt",
        "consignment_id.courier_partner_id.insurance_max_bdt",
    )
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    @api.depends(
        "claimed_amount",
        "requested_payout",
        "approved_amount",
        "consignment_id.declared_value_bdt",
        "consignment_id.courier_partner_id.insurance_max_bdt",
    )
    def _compute_dofa_tier(self):
        for rec in self:
            rec.dofa_tier = rec._dofa_current_tier()

    @api.constrains("requested_payout", "claimed_amount")
    def _check_requested_payout(self):
        for rec in self:
            if rec.requested_payout < 0:
                raise UserError("The payout requested cannot be negative.")
            if rec.requested_payout > (rec.claimed_amount or 0.0) + 0.005:
                raise UserError(
                    "The payout requested (BDT %.2f) cannot exceed the amount claimed "
                    "(BDT %.2f)." % (rec.requested_payout, rec.claimed_amount or 0.0)
                )

    # ------------------------------------------------------------ routing
    def _approval_holders(self, group):
        """A02 audit B1: the DOFA ladder picks the tier group; only its members
        who also hold the claim-approver role may decide a payout."""
        users = super()._approval_holders(group)
        approvers = self.env.ref(GROUP_CLAIM_APPROVER, raise_if_not_found=False)
        return users & approvers.sudo().all_user_ids if approvers else users.browse()

    def _approval_on_rejected(self, comment):
        """An inbox rejection decides the claim: rejected, with the reason."""
        for rec in self.filtered(lambda r: r.state == "open"):
            rec._guarded().write(
                {
                    "state": "rejected",
                    "rejected_by_id": self.env.user.id,
                    "rejection_reason": comment or False,
                }
            )

    # ------------------------------------------------------------ the guard
    def _fix_guarded_fields(self) -> set:
        # A02 audit M03-1/5: the decision, the decided amounts and their
        # stamps change only through approve / reject / settle.
        return super()._fix_guarded_fields() | {
            "state",
            "approved_amount",
            "approved_by_id",
            "approved_at",
            "rejected_by_id",
            "rejection_reason",
            "settled_amount",
            "settled_at",
            "settled_by_id",
            "dofa_tier",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state != "open":
            locked |= DECIDED_LOCKED | {"dofa_justification"}
            if rec.state in ("rejected", "settled"):
                locked |= {
                    "description",
                    "evidence_ref",
                    "incident_photo_attachment_id",
                    "claimed_on",
                    "operating_unit_id",
                }
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "open"):
                locked = rec._fix_form_locked_fields() - rec._fix_guarded_fields()
                changed = [
                    n for n in locked & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "%s cannot be changed on %s: the claim is %s (A02 audit M03-5)."
                        % (
                            ", ".join(sorted(rec._fields[n].string or n for n in changed)),
                            rec.name,
                            rec.state,
                        )
                    )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.damage.claim") or "DMC/New"
        return super().create(vals_list)

    # ------------------------------------------------------------ decisions
    def _claim_require_approver(self, what):
        if self.env.su or self.env.user.has_group(GROUP_CLAIM_APPROVER):
            return
        holders = self.env.ref(GROUP_CLAIM_APPROVER, raise_if_not_found=False)
        nobody = not holders or not holders.sudo().all_user_ids.filtered("active")
        raise UserError(
            "%s needs the Damage Claim Approver role.%s"
            % (
                what,
                " No one holds it yet: a manager must appoint the claim approvers."
                if nobody
                else "",
            )
        )

    def _claim_assert_not_creator(self, what):
        if not self.env.su and self.create_uid == self.env.user:
            raise UserError(
                "Segregation of duties: you raised %s, so %s must be done by a different "
                "claim approver." % (self.name, what)
            )

    @staticmethod
    def _parse_amount(value, label):
        if value in (None, False, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            raise UserError("%s must be a number." % label) from None

    def action_approve(self):
        """Approve the payout requested (blank: the amount claimed). Runs only
        from the approver's inbox task (A02 audit B1). The approver holds the
        claim-approver role and the DOFA tier the amount needs, is not the
        claim's creator, and a written justification is on the claim. The
        payout is capped at the amount claimed; above the insured value it
        needs a higher tier."""
        self._approval_assert_routed()
        self._claim_require_approver("Approving a damage claim")
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open claim can be approved")
            rec._claim_assert_not_creator("approving it")
            amount = rec.requested_payout or rec.claimed_amount
            if not amount or amount <= 0:
                raise UserError("Enter the approved amount before approving the claim")
            if amount > (rec.claimed_amount or 0.0) + 0.005:
                raise UserError(
                    "The approved payout (BDT %.2f) cannot exceed the amount claimed "
                    "(BDT %.2f)." % (amount, rec.claimed_amount or 0.0)
                )
            rec._guarded().write({"approved_amount": amount})
            # tier group, segregation of duties, justification, amount pin
            rec.action_dofa_approve()
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        self._claim_require_approver("Rejecting a damage claim")
        reason = (str(reason).strip() if reason else "") or False
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open claim can be rejected")
            rec._claim_assert_not_creator("rejecting it")
            if rec.approval_state == "pending":
                # the payout request is moot once the claim itself is rejected
                rec._approval_void("the claim was rejected by %s" % self.env.user.name)
            rec._guarded().write(
                {
                    "state": "rejected",
                    "rejected_by_id": self.env.user.id,
                    "rejection_reason": reason,
                }
            )
        return True

    def action_settle(self, settled_amount=None):
        """Record the payout of an approved claim, at no more than the amount
        approved, and publish it so finance can raise the payable (A02 audit
        M03-6; the consumer is a later phase)."""
        if not (self.env.su or self.env.user.has_group(GROUP_MANAGER)):
            raise UserError("Settling a damage claim needs the Logistics Manager role.")
        amount_in = self._parse_amount(settled_amount, "The settled amount")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Settle an approved claim")
            rec._dofa_assert_approved("Damage-claim settlement")
            amount = amount_in if amount_in is not None else rec.approved_amount
            ceiling = min(rec.approved_amount or 0.0, rec.dofa_approved_amount or 0.0)
            if not amount or amount <= 0:
                raise UserError("Enter the amount paid out.")
            if amount > ceiling + 0.005:
                raise UserError(
                    "The settlement (BDT %.2f) exceeds the approved payout (BDT %.2f)."
                    % (amount, ceiling)
                )
            now = fields.Datetime.now()
            rec._guarded().write(
                {
                    "state": "settled",
                    "settled_amount": amount,
                    "settled_at": now,
                    "settled_by_id": self.env.user.id,
                }
            )
            publish(
                rec.env,
                "damage.claim.settled",
                "fix.damage.claim",
                rec.id,
                {
                    "claim": rec.name,
                    "consignment": rec.consignment_id.name,
                    "amount": amount,
                    "currency": rec.currency_id.name,
                    "claimant": rec.claimant,
                    "liability": rec.liability,
                    "courier_partner_id": rec.consignment_id.courier_partner_id.id or None,
                    "approved_by": rec.approved_by_id.id,
                    "settled_by": self.env.user.id,
                    "settled_at": fields.Datetime.to_string(now),
                },
            )
        return True

    def _dofa_void_approval(self, reason: str):
        """An approval that no longer covers the payout sends the claim back
        to open: it is decided again, by an approver, at the new amount."""
        approved = self.filtered(lambda r: r.state == "approved")
        result = super()._dofa_void_approval(reason)
        approved._guarded().write({"state": "open", "approved_by_id": False, "approved_at": False})
        return result
