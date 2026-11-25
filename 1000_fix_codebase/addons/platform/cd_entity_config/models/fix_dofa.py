# cd_entity_config — 5-Tier Delegation of Financial Authority mixin.
#
# A03 zero-trust audit (2026-10-31): approval across Area A03 was a Boolean the
# requester set on themselves. This mixin makes an approval mean three things
# that a Boolean cannot:
#   1. the tier is DERIVED from the amount, not chosen by the approver;
#   2. the approver must hold that tier's group;
#   3. the approver must not be the person who raised the record.
#
# A model mixes it in and declares `_dofa_thresholds` (ascending) plus
# `_dofa_amount`; everything else is inherited.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

DOFA_TIERS = [
    ("tier_0", "Tier 0 — No Approval Required"),
    ("tier_1", "Tier 1 — Team Lead / Supervisor"),
    ("tier_2", "Tier 2 — Branch / Operations Manager"),
    ("tier_3", "Tier 3 — CX / Commercial Director"),
    ("tier_4", "Tier 4 — CFO / CCO / COO"),
    ("tier_5", "Tier 5 — Managing Director / Board"),
]

TIER_GROUP = {
    "tier_1": "cd_entity_config.group_dofa_tier_1",
    "tier_2": "cd_entity_config.group_dofa_tier_2",
    "tier_3": "cd_entity_config.group_dofa_tier_3",
    "tier_4": "cd_entity_config.group_dofa_tier_4",
    "tier_5": "cd_entity_config.group_dofa_tier_5",
}


DOFA_APPROVAL_FIELDS = {
    "dofa_approved",
    "dofa_approved_by",
    "dofa_approved_at",
    "dofa_approved_tier",
    "dofa_approved_amount",
}


class FixDofaMixin(models.AbstractModel):
    """Derives the approval tier from the amount at risk and enforces it."""

    _name = "fix.dofa.mixin"
    _inherit = ["fix.guarded.mixin"]
    _description = "5-Tier Delegation of Financial Authority"

    def _fix_guarded_fields(self) -> set:
        # The approval stamp is evidence. Only action_dofa_approve (and the
        # voiding path) may write it — a stamp anyone can type is not one.
        return super()._fix_guarded_fields() | DOFA_APPROVAL_FIELDS

    dofa_tier_required = fields.Selection(
        DOFA_TIERS,
        string="DOFA Tier Required",
        compute="_compute_dofa_tier_required",
        store=True,
        help="Derived from the amount at risk. Never set by hand.",
    )
    dofa_approved = fields.Boolean(string="DOFA Approved", readonly=True, copy=False, tracking=True)
    dofa_approved_by = fields.Many2one(
        "res.users", string="DOFA Approver", readonly=True, copy=False, tracking=True
    )
    dofa_approved_at = fields.Datetime(string="DOFA Approved On", readonly=True, copy=False)
    dofa_approved_tier = fields.Selection(
        DOFA_TIERS,
        string="Tier Actually Approved",
        readonly=True,
        copy=False,
        help="The tier in force when approval was granted. If the amount later "
        "rises above it, the approval no longer covers the record.",
    )
    dofa_approved_amount = fields.Float(
        string="Amount Approved",
        readonly=True,
        copy=False,
        help="The amount at risk the approver actually signed off. An approval "
        "covers this amount, not whatever the record is later edited to.",
    )
    dofa_justification = fields.Text(
        string="DOFA Justification",
        copy=False,
        help="Written business justification. Mandatory for Tier 2 and above.",
    )

    # ---- per-model hooks -------------------------------------------------
    def _dofa_amount(self) -> float:
        """The amount at risk that the tier is derived from. Override."""
        self.ensure_one()
        return 0.0

    def _dofa_thresholds(self):
        """[(upper_bound_inclusive, tier), ...] ascending; the last entry is the
        ceiling tier applied above every bound. Override."""
        return [(0.0, "tier_0")]

    def _dofa_amount_label(self) -> str:
        """How the amount reads in refusal messages. Override for points etc."""
        self.ensure_one()
        return "BDT %.2f" % self._dofa_amount()

    # ---- derivation ------------------------------------------------------
    def _dofa_tier_for_amount(self, amount: float) -> str:
        thresholds = self._dofa_thresholds()
        for bound, tier in thresholds:
            if amount <= bound:
                return tier
        return thresholds[-1][1] if thresholds else "tier_0"

    def _dofa_current_tier(self) -> str:
        """The tier the record needs NOW, derived from its live amount.

        Decisions use this, never the stored column. The column used to carry
        @api.depends_context("uid"), which gives a stored field one cache slot
        per user; on flush Odoo writes whichever slot it finds first, so a
        record raised by an ordinary user stored NULL. The approver was then
        told "nothing to approve" while _dofa_assert_approved read NULL as
        tier_0 and let the record through (A03 audit, 2026-11-03). A gate must
        not depend on a cached copy of its own input.
        """
        self.ensure_one()
        amount = abs(self._dofa_amount() or 0.0)
        if amount <= 0.0:
            # Nothing at risk, nothing to authorise.
            return "tier_0"
        return self._dofa_tier_for_amount(amount)

    def _compute_dofa_tier_required(self):
        """Concrete models re-declare @api.depends on their own amount field.

        No depends_context: the tier depends on the amount and the ruled
        ladder, not on who happens to be reading the record.
        """
        for rec in self:
            rec.dofa_tier_required = rec._dofa_current_tier()

    # ---- enforcement -----------------------------------------------------
    def _dofa_tier_rank(self, tier: str) -> int:
        order = [t[0] for t in DOFA_TIERS]
        return order.index(tier) if tier in order else 0

    def _dofa_route_guard(self):
        """Hook: refuse an approval that must arrive through a workflow task.
        No-op here; the M63 engine (cd_workflow_engine) overrides it."""
        return None

    def _dofa_authority_user(self):
        """The user whose DOFA tier group must cover the approval. The M63
        engine returns the absent approver when a delegate decides on their
        behalf."""
        return self.env.user

    def _dofa_acting_users(self):
        """Everyone who must not be the record's creator (segregation of
        duties): the approver, and the person they act for."""
        return self.env.user

    def action_dofa_approve(self):
        """Grant approval, if this user is actually allowed to grant it."""
        self._dofa_route_guard()
        for rec in self:
            tier = rec._dofa_current_tier()
            if tier == "tier_0":
                raise UserError(
                    "Nothing to approve: %s falls below the lowest DOFA threshold."
                    % rec._dofa_amount_label()
                )
            group = TIER_GROUP.get(tier)
            if group and not rec._dofa_authority_user().has_group(group):
                raise UserError(
                    "DOFA authority insufficient: %s requires %s. You do not hold "
                    "that approval authority." % (rec._dofa_amount_label(), dict(DOFA_TIERS)[tier])
                )
            # Segregation of duties: the person who raised it cannot clear it.
            if rec.create_uid and rec.create_uid in rec._dofa_acting_users():
                raise UserError(
                    "Segregation of duties: %s was raised by you and must be "
                    "approved by a different %s."
                    % (rec._dofa_amount_label(), dict(DOFA_TIERS)[tier])
                )
            if (
                self._dofa_tier_rank(tier) >= self._dofa_tier_rank("tier_2")
                and not (rec.dofa_justification or "").strip()
            ):
                raise ValidationError(
                    "A written DOFA justification is mandatory at %s." % dict(DOFA_TIERS)[tier]
                )
            rec._guarded().write(
                {
                    "dofa_approved": True,
                    "dofa_approved_by": self.env.user.id,
                    "dofa_approved_at": fields.Datetime.now(),
                    "dofa_approved_tier": tier,
                    "dofa_approved_amount": abs(rec._dofa_amount() or 0.0),
                }
            )
            if hasattr(rec, "message_post"):
                rec.message_post(
                    body="DOFA %s approval granted for %s by %s."
                    % (dict(DOFA_TIERS)[tier], rec._dofa_amount_label(), self.env.user.name)
                )

    def _dofa_assert_approved(self, what: str = "This transaction"):
        """Raise unless the record carries an approval that still covers it."""
        for rec in self:
            tier = rec._dofa_current_tier()
            if tier == "tier_0":
                continue
            if not rec.dofa_approved:
                raise ValidationError(
                    "%s of %s requires %s sign-off before it can proceed "
                    "(5-Tier DOFA governance)."
                    % (what, rec._dofa_amount_label(), dict(DOFA_TIERS)[tier])
                )
            # An approval granted at a lower tier does not cover a raised amount.
            if rec._dofa_tier_rank(rec.dofa_approved_tier or "tier_0") < rec._dofa_tier_rank(tier):
                raise ValidationError(
                    "%s was approved at %s but now stands at %s, which requires %s. "
                    "Re-approval is required."
                    % (
                        what,
                        dict(DOFA_TIERS).get(rec.dofa_approved_tier, "no tier"),
                        rec._dofa_amount_label(),
                        dict(DOFA_TIERS)[tier],
                    )
                )
            # ...and neither does an approval of a smaller amount within the
            # same tier: signing off BDT 3,000 is not signing off BDT 4,999.
            # Rows approved before the amount was recorded carry 0 and keep
            # the tier check only.
            approved_amount = rec.dofa_approved_amount or 0.0
            current = abs(rec._dofa_amount() or 0.0)
            if approved_amount and current > approved_amount + 0.005:
                raise ValidationError(
                    "%s was approved for %.2f but now stands at %s. An approval "
                    "covers the amount that was signed off; re-approval is required."
                    % (what, approved_amount, rec._dofa_amount_label())
                )

    def write(self, vals):
        """An approval covers the amount that was signed off, from the moment
        the amount moves past it — not only when a gate next looks.

        _dofa_assert_approved already refuses an exceeded approval at the
        point of consequence, but until then the record still read
        "approved" (A03 audit, R4). Raising the amount above what was
        approved now withdraws the approval at once and says so in the
        chatter; lowering it leaves the approval standing, since signing off
        BDT 5,000 covers BDT 3,000.
        """
        approved = self.filtered("dofa_approved")
        before = {rec.id: abs(rec._dofa_amount() or 0.0) for rec in approved}
        result = super().write(vals)
        for rec in approved:
            pinned = rec.dofa_approved_amount or before[rec.id]
            now = abs(rec._dofa_amount() or 0.0)
            if now > pinned + 0.005 and now != before[rec.id]:
                rec._dofa_void_approval(
                    "the amount rose from %.2f to %s after approval; re-approval "
                    "is required." % (pinned, rec._dofa_amount_label())
                )
        return result

    def _dofa_void_approval(self, reason: str):
        """Withdraw an approval that no longer covers the record."""
        for rec in self.filtered("dofa_approved"):
            rec._guarded().write(
                {
                    "dofa_approved": False,
                    "dofa_approved_by": False,
                    "dofa_approved_at": False,
                    "dofa_approved_tier": False,
                    "dofa_approved_amount": 0.0,
                }
            )
            if hasattr(rec, "message_post"):
                rec.message_post(body="DOFA approval withdrawn: %s" % reason)


class FixPiiAccessLog(models.Model):
    """REQ-33.3: an append-only record of who read unmasked customer PII.

    The group restriction on fix.partner.nid_number decides WHO may look; this
    records THAT they looked. Rows are never updated or deleted — a log that
    its own readers can edit is not evidence.
    """

    _name = "fix.pii.access.log"
    _description = "Unmasked PII Access Log"
    _order = "accessed_at desc, id desc"

    user_id = fields.Many2one(
        "res.users", required=True, index=True, default=lambda self: self.env.user
    )
    accessed_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    res_model = fields.Char(string="Record Model", required=True, index=True)
    res_id = fields.Integer(string="Record ID", required=True, index=True)
    field_name = fields.Char(string="Field", required=True)
    reason = fields.Char(string="Stated Reason")

    def write(self, vals):
        raise UserError("The PII access log is append-only and cannot be edited.")

    def unlink(self):
        raise UserError("The PII access log is append-only and cannot be deleted.")

    @api.model
    def record_access(self, res_model, res_id, field_name, reason=None):
        """Called when an unmasked identifier is served to a user."""
        return self.sudo().create(
            {
                "user_id": self.env.user.id,
                "res_model": res_model,
                "res_id": res_id,
                "field_name": field_name,
                "reason": reason or "",
            }
        )
