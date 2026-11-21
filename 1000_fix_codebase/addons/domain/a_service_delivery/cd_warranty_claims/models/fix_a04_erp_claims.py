# A04 ERP audit (20 Nov 2026), M09: the brand claim's value, uniqueness and
# window, and the protection plan's limits.
#
# M09-F4: the claim asked the OEM for the customer's estimate INCLUDING VAT
#   (2,300) while the M11 brand reimbursement rate said 3,000; nothing called
#   the rate API. The claim is now valued at the brand's released rate in
#   force on the service date (labour + parts x (1 + markup)), ex-VAT, and the
#   rate is pinned on the claim. A brand with no released rate is valued at
#   the approved estimate's VAT-exclusive amount, flagged as such; the owner
#   may switch that fallback off (cd_warranty_claims.require_brand_rate = 1),
#   and a claim then claims nothing until the brand's rate is released.
# M09-F5: a second claim on the same order was accepted, and a claim could
#   not be cancelled.
# M09-F10: a claim submitted 20 days after the brand's window closed was
#   accepted, and nothing marked it lapsed.
# M09-F6: two protection claims approved before either settled overran the
#   aggregate limit (15,000 paid on 10,000) and the reserve top-up covered one.
# M09-F15 (part): a sold policy's terms stayed writable after activation.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_m09_capture import _not_same, _today
from .fix_warranty_claims import CLERK_GROUP, OFFICER_GROUP, OPEN_STATES, _assert_role

PARAM_REQUIRE_BRAND_RATE = "cd_warranty_claims.require_brand_rate"
PARAM_REQUIRE_AUTHORISATION = "cd_warranty_claims.require_brand_authorisation"
CTX_REPAIR_LEVEL = "fix_claim_repair_level"
DEAD_CLAIM_STATES = ("cancelled",)
REPAIR_LEVELS = [
    ("l1", "Level 1 - Modular / Quick Fix"),
    ("l2", "Level 2 - Component / Soldering"),
    ("l3", "Level 3 - Chip-Level / Advanced Depot"),
]
_ALL_STORED_EXEMPT = ("message_", "activity_", "website_message")


class FixWarrantyClaimValuation(models.Model):
    _inherit = "fix.warranty.claim"

    state = fields.Selection(
        selection_add=[("lapsed", "Lapsed (window closed)"), ("cancelled", "Cancelled")],
        ondelete={"lapsed": "set default", "cancelled": "set default"},
    )
    repair_level = fields.Selection(
        REPAIR_LEVELS,
        string="Repair Level",
        default="l1",
        required=True,
        help="The workshop repair level the brand's reimbursement rate is read for.",
    )
    rate_id = fields.Many2one(
        "fix.brand.reimbursement.rate",
        string="Brand Rate Applied",
        readonly=True,
        copy=False,
        help="M11: the released brand reimbursement rate in force on the service date that "
        "valued this claim (pinned when the claim was raised or refreshed).",
    )
    valuation_basis = fields.Selection(
        [
            ("brand_rate", "M11 brand reimbursement rate"),
            ("estimate", "Approved estimate, VAT excluded (the brand has no released rate)"),
            ("system", "Set by the intake service"),
        ],
        string="Valued By",
        readonly=True,
        copy=False,
    )
    parts_value = fields.Monetary(
        string="Parts Value (ex-VAT)", currency_field="currency_id", readonly=True, copy=False
    )
    cancel_reason = fields.Char(readonly=True, copy=False)
    cancelled_by_id = fields.Many2one("res.users", string="Cancelled By", readonly=True, copy=False)
    cancelled_at = fields.Datetime(readonly=True, copy=False)
    lapsed_at = fields.Datetime(string="Lapsed On", readonly=True, copy=False)
    deadline_extended_by_id = fields.Many2one(
        "res.users", string="Window Extended By", readonly=True, copy=False
    )
    deadline_extension_reason = fields.Char(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "rate_id",
            "valuation_basis",
            "parts_value",
            "cancel_reason",
            "cancelled_by_id",
            "cancelled_at",
            "lapsed_at",
            "deadline_extended_by_id",
            "deadline_extension_reason",
        }

    def _fix_frozen_fields(self) -> set:
        frozen = super()._fix_frozen_fields()
        if self.state not in OPEN_STATES:
            frozen |= {"repair_level"}
        if self.state in ("lapsed", "cancelled"):
            frozen |= {
                name
                for name, field in self._fields.items()
                if field.store and not name.startswith(_ALL_STORED_EXEMPT)
            }
        return frozen

    # ---- M09-F4: the claim's value -------------------------------------------
    @api.model
    def _fix_claim_valuation(self, order, brand=None, repair_level=None, on_date=None):
        """{amount, rate_id, basis, parts}: what the OEM owes for `order`."""
        est = order._fix_governing_estimate().filtered(lambda e: e.state == "approved")[:1]
        brand = brand or order.device_id.brand_id
        level = repair_level or self.env.context.get(CTX_REPAIR_LEVEL) or "l1"
        parts = round(est.parts_total or 0.0, 2) if est else 0.0
        day = on_date or (
            fields.Date.to_date(order.create_date) if order.create_date else _today(self.env)
        )
        if brand and "fix.rate.card" in self.env:
            priced = self.env["fix.rate.card"].reimbursement_for(
                brand,
                repair_level=level,
                parts_cost=parts,
                on_date=day,
                company=order.company_id or self.env.company,
            )
            if priced.get("amount") is not None:
                return {
                    "amount": round(priced["amount"], 2),
                    "rate_id": priced.get("rate_id") or False,
                    "basis": "brand_rate",
                    "parts": parts,
                }
        if self.env["ir.config_parameter"].sudo().get_param(PARAM_REQUIRE_BRAND_RATE) == "1":
            return {"amount": 0.0, "rate_id": False, "basis": False, "parts": parts}
        taxable = round((est.grand_total or 0.0) - (est.vat_amount or 0.0), 2) if est else 0.0
        return {"amount": taxable, "rate_id": False, "basis": "estimate", "parts": parts}

    @api.model
    def _approved_estimate_amount(self, order) -> float:
        """The claim amount the base create / refresh / AUT-018 read: the M11
        valuation (ex-VAT), not the VAT-inclusive estimate total."""
        return self._fix_claim_valuation(order.sudo())["amount"]

    def _fix_stamp_valuation(self):
        for claim in self:
            order = claim.service_order_id.sudo()
            val = claim._fix_claim_valuation(order, claim.brand_id, claim.repair_level)
            matches = abs((claim.claim_amount or 0.0) - val["amount"]) <= 0.005
            claim._guarded().write(
                {
                    "rate_id": val["rate_id"] if matches else False,
                    "valuation_basis": (val["basis"] or False) if matches else "system",
                    "parts_value": val["parts"],
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            for vals in vals_list:
                # M09-F5: one live claim per warranty job
                order_id = vals.get("service_order_id")
                if order_id and self.sudo().search_count(
                    [
                        ("service_order_id", "=", order_id),
                        ("state", "not in", list(DEAD_CLAIM_STATES)),
                    ]
                ):
                    raise ValidationError(
                        "Order %s already has a warranty claim: one claim recovers one job "
                        "(cancel the existing claim first)."
                        % self.env["fix.service.order"].sudo().browse(order_id).name
                    )
        claims = self.browse()
        for vals in vals_list:
            level = vals.get("repair_level") or "l1"
            claims |= super(
                FixWarrantyClaimValuation, self.with_context(**{CTX_REPAIR_LEVEL: level})
            ).create([vals])
        claims = self.browse(claims.ids)
        claims._fix_stamp_valuation()
        return claims

    def write(self, vals):
        result = super().write(vals)
        if "repair_level" in vals:
            for claim in self.filtered(lambda c: c.state in OPEN_STATES):
                order = claim.service_order_id.sudo()
                amount = claim._fix_claim_valuation(order, claim.brand_id, claim.repair_level)[
                    "amount"
                ]
                claim._guarded().write({"claim_amount": amount})
                claim._fix_stamp_valuation()
        return result

    def action_refresh_amount(self):
        for claim in self:
            super(
                FixWarrantyClaimValuation,
                claim.with_context(**{CTX_REPAIR_LEVEL: claim.repair_level or "l1"}),
            ).action_refresh_amount()
        self._fix_stamp_valuation()
        return True

    # ---- M09-F5: cancel -------------------------------------------------------
    def action_cancel(self, reason=None):
        """Withdraw a claim before the brand decides it: a clerk while it is
        being prepared (or lapsed), a Claim Decision Officer once the brand
        has it. The job may then be claimed again."""
        if not (reason or "").strip():
            raise UserError("Say why the claim is cancelled.")
        for claim in self:
            if claim.state in OPEN_STATES or claim.state == "lapsed":
                _assert_role(self.env, CLERK_GROUP, "Cancelling a warranty claim")
            elif claim.state in ("submitted", "in_review"):
                _assert_role(self.env, OFFICER_GROUP, "Withdrawing a claim from the brand")
                if claim.approval_state == "pending":
                    raise UserError(
                        "Claim %s has a decision awaiting the officer: recall it first."
                        % claim.claim_no
                    )
            else:
                raise UserError(
                    "Claim %s is %s: a decided claim is not cancelled (an unrecoverable "
                    "balance is written off)." % (claim.claim_no, claim.state)
                )
            claim._guarded().write(
                {
                    "state": "cancelled",
                    "cancel_reason": reason.strip()[:250],
                    "cancelled_by_id": self.env.uid,
                    "cancelled_at": fields.Datetime.now(),
                }
            )
            claim.message_post(body="Cancelled by %s: %s" % (self.env.user.name, reason.strip()))
            publish(
                self.env,
                "warranty_claim.cancelled",
                "fix.warranty.claim",
                claim.id,
                {"claim_no": claim.claim_no, "reason": reason.strip()[:250]},
            )
        return True

    # ---- M09-F10: the brand's window ------------------------------------------
    def action_submit(self):
        now = fields.Datetime.now()
        # B5 / M40 (BRU-PCM-08): a claim is submitted only for a brand 1000FiX
        # holds a valid authorisation for. fix_real holds none yet, so the gate
        # is the owner's switch (cd_warranty_claims.require_brand_authorisation).
        params = self.env["ir.config_parameter"].sudo()
        gate = params.get_param(PARAM_REQUIRE_AUTHORISATION) == "1"
        Auth = self.env.get("fix.partner.authorisation")
        for claim in self:
            if gate and Auth is not None and hasattr(Auth, "fix_assert_brand_authorised"):
                Auth.sudo().fix_assert_brand_authorised(
                    claim.brand_id, "Submitting warranty claim %s" % claim.claim_no
                )
            if claim.state == "lapsed" or (
                claim.state in OPEN_STATES
                and claim.submission_deadline
                and now > claim.submission_deadline
            ):
                raise UserError(
                    "Claim %s missed the brand's submission window (closed %s): it has lapsed. "
                    "A Claim Decision Officer extends the window (Extend Window) only when the "
                    "brand accepts a late claim." % (claim.claim_no, claim.submission_deadline)
                )
        return super().action_submit()

    def action_extend_deadline(self, new_deadline=None, reason=None):
        """The escalation: an officer who did not raise the claim records that
        the brand accepts it late, with the new window."""
        _assert_role(self.env, OFFICER_GROUP, "Extending a claim's submission window")
        if not (reason or "").strip():
            raise UserError("Record the brand's acceptance of the late claim (reference).")
        deadline = fields.Datetime.to_datetime(new_deadline) if new_deadline else False
        if not deadline or deadline <= fields.Datetime.now():
            raise UserError("The new window ends in the future.")
        for claim in self:
            if claim.state not in ("lapsed", *OPEN_STATES):
                raise UserError("Claim %s is %s." % (claim.claim_no, claim.state))
            _not_same(self.env, claim.create_uid, "extending the window of %s" % claim.claim_no)
            claim._guarded().write(
                {
                    "state": "ready" if claim.evidence_complete else "draft",
                    "submission_deadline": deadline,
                    "lapsed_at": False,
                    "overdue_escalated_at": False,
                    "deadline_extended_by_id": self.env.uid,
                    "deadline_extension_reason": reason.strip()[:250],
                }
            )
            claim.message_post(
                body="Window extended to %s by %s: %s" % (deadline, self.env.user.name, reason)
            )
        return True

    @api.model
    def cron_claim_overdue_escalation(self) -> int:
        """Escalate once (as before), then lapse every claim still unsubmitted
        past its window: it is out of the brand's time and is either extended
        by an officer or cancelled."""
        escalated = super().cron_claim_overdue_escalation()
        now = fields.Datetime.now()
        overdue = self.sudo().search(
            [("state", "in", list(OPEN_STATES)), ("submission_deadline", "<", now)], limit=500
        )
        for claim in overdue:
            claim._guarded().write({"state": "lapsed", "lapsed_at": now})
            claim.message_post(
                body="Lapsed: the brand's submission window closed on %s."
                % claim.submission_deadline
            )
            publish(
                self.env,
                "warranty_claim.lapsed",
                "fix.warranty.claim",
                claim.id,
                {"claim_no": claim.claim_no, "deadline": str(claim.submission_deadline)},
            )
        return escalated


# ==========================================================================
# M09-F6 / F15: protection limits count what is approved, and terms freeze
# ==========================================================================
COMMITTED_PCLAIM_STATES = ("approved", "settled")
POLICY_TERMS = ("product_id", "partner_id", "device_id", "premium", "term_start", "sale_ref")


class FixProtectionPolicyLimits(models.Model):
    _inherit = "fix.protection.policy"

    committed_amount = fields.Monetary(
        string="Approved + Settled Claims",
        currency_field="currency_id",
        compute="_compute_limits",
        help="BRU-WTY-14: approved claims count against the aggregate limit as soon as they "
        "are approved, not only once settled.",
    )
    outstanding_claims = fields.Monetary(
        string="Approved, Not Yet Settled",
        currency_field="currency_id",
        compute="_compute_limits",
    )

    @api.depends(
        "claim_ids.state", "claim_ids.approved_amount", "reserve_ids.amount", "claim_limit"
    )
    def _compute_limits(self):
        super()._compute_limits()
        for policy in self:
            committed = policy.claim_ids.filtered(lambda c: c.state in COMMITTED_PCLAIM_STATES)
            used = sum(committed.mapped("approved_amount"))
            policy.committed_amount = used
            policy.outstanding_claims = sum(
                committed.filtered(lambda c: c.state == "approved").mapped("approved_amount")
            )
            policy.remaining_limit = (
                max(policy.claim_limit - used, 0.0) if policy.claim_limit else 0.0
            )

    def write(self, vals):
        if not self._fix_guard_open():
            touched = set(POLICY_TERMS) & set(vals)
            for policy in self.filtered(lambda p: p.state != "sold"):
                if any(policy._fix_guard_differs(n, vals[n], policy[n]) for n in touched):
                    raise UserError(
                        "Policy %s is %s: the cover the customer bought is fixed (product, "
                        "device, premium, start). Cancel it and sell a new one."
                        % (policy.name, policy.state)
                    )
        return super().write(vals)


class FixProtectionClaimLimits(models.Model):
    _inherit = "fix.protection.claim"

    def action_approve(self):
        """The base check reads remaining_limit, which now nets every approved
        claim. The reserve is then topped up to cover ALL incurred (approved,
        unsettled) claims of the policy, not just this one (FR-WTY-036)."""
        result = super().action_approve()
        for claim in self:
            policy = claim.policy_id
            policy.invalidate_recordset(["outstanding_claims", "reserve_balance"])
            target = round(policy.outstanding_claims, 2)
            short = round(target - policy.reserve_balance, 2)
            if short > 0.005:
                policy._reserve(
                    "adjust",
                    short,
                    "Top-up to the %.2f of approved, unsettled claims (%s)" % (target, claim.name),
                    claim,
                )
        return result

    def action_settle(self):
        """Re-check the aggregate limit at settlement: what the plan has paid
        and committed, including this claim, never exceeds it."""
        for claim in self:
            policy = claim.policy_id
            if policy.claim_limit:
                policy.invalidate_recordset(["committed_amount"])
                if policy.committed_amount > policy.claim_limit + 0.005:
                    raise UserError(
                        "Settling %s would take policy %s to %.2f of claims on a %.2f aggregate "
                        "limit (BRU-WTY-14): re-assess or reject a claim first."
                        % (claim.name, policy.name, policy.committed_amount, policy.claim_limit)
                    )
        return super().action_settle()


class FixBrandRemittanceLineLock(models.Model):
    """M09-F14: a matched remittance's lines are what the bank paid on which
    claim; they stayed editable after matching."""

    _inherit = "fix.brand.remittance.line"

    def _fix_refuse_if_matched(self, remittances):
        if self.env.su:
            return
        if remittances.filtered(lambda r: r.state != "draft"):
            raise UserError(
                "Remittance %s is matched: its lines are a record of what the brand paid."
                % ", ".join(remittances.filtered(lambda r: r.state != "draft").mapped("name"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = [v.get("remittance_id") for v in vals_list if v.get("remittance_id")]
        self._fix_refuse_if_matched(self.env["fix.brand.remittance"].browse(ids).exists())
        return super().create(vals_list)

    def write(self, vals):
        self._fix_refuse_if_matched(self.mapped("remittance_id"))
        return super().write(vals)

    def unlink(self):
        self._fix_refuse_if_matched(self.mapped("remittance_id"))
        return super().unlink()
