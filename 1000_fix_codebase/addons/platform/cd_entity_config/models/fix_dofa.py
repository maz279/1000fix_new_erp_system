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


class FixDofaMixin(models.AbstractModel):
    """Derives the approval tier from the amount at risk and enforces it."""

    _name = "fix.dofa.mixin"
    _description = "5-Tier Delegation of Financial Authority"

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

    @api.depends_context("uid")
    def _compute_dofa_tier_required(self):
        """Concrete models re-declare @api.depends on their own amount field."""
        for rec in self:
            rec.dofa_tier_required = rec._dofa_tier_for_amount(abs(rec._dofa_amount() or 0.0))

    # ---- enforcement -----------------------------------------------------
    def _dofa_tier_rank(self, tier: str) -> int:
        order = [t[0] for t in DOFA_TIERS]
        return order.index(tier) if tier in order else 0

    def action_dofa_approve(self):
        """Grant approval, if this user is actually allowed to grant it."""
        for rec in self:
            tier = rec.dofa_tier_required or "tier_0"
            if tier == "tier_0":
                raise UserError(
                    "Nothing to approve: %s falls below the lowest DOFA threshold."
                    % rec._dofa_amount_label()
                )
            group = TIER_GROUP.get(tier)
            if group and not self.env.user.has_group(group):
                raise UserError(
                    "DOFA authority insufficient: %s requires %s. You do not hold "
                    "that approval authority." % (rec._dofa_amount_label(), dict(DOFA_TIERS)[tier])
                )
            # Segregation of duties: the person who raised it cannot clear it.
            if rec.create_uid and rec.create_uid.id == self.env.user.id:
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
            rec.write(
                {
                    "dofa_approved": True,
                    "dofa_approved_by": self.env.user.id,
                    "dofa_approved_at": fields.Datetime.now(),
                    "dofa_approved_tier": tier,
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
            tier = rec.dofa_tier_required or "tier_0"
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
