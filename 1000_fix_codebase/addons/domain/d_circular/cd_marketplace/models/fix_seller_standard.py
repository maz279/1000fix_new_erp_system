# M12 seller standards and certifications (declared gap M12-training closed,
# 12 Nov 2026).
#
# Training and certification existed for staff only (fix.training.enrollment
# and fix.certification in cd_competency are keyed to hr.employee), so
# "Standards & Training" for marketplace sellers was a declared gap.
#
#   * fix.seller.standard - a standard, course or certificate a seller can
#     hold, with its validity and the service categories that REQUIRE it
#     (the category -> required-standard mapping, BRU-ECM-07 qualification).
#     Maintained by Marketplace Compliance Reviewers.
#   * fix.seller.certification - the seller's evidence of holding one:
#     draft -> submitted (with the evidence attached) -> verified by a
#     compliance reviewer who neither created nor submitted it and is not the
#     seller; or rejected (with a reason, resubmittable), revoked, or expired
#     by the daily cron once its date passes. State, submitter and verifier
#     are guarded; the certificate's terms are pinned once submitted.
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_marketplace import COMPLIANCE_GROUP, OPERATOR_GROUP, _assert_role, _seller_users

CERT_STATES = [
    ("draft", "Draft"),
    ("submitted", "Awaiting Verification"),
    ("verified", "Verified"),
    ("rejected", "Rejected"),
    ("expired", "Expired"),
    ("revoked", "Revoked"),
]
EDITABLE_STATES = ("draft", "rejected")
# A verified certificate inside this many days of its expiry is "expiring".
EXPIRY_WARNING_DAYS = 30
_TERMS = {
    "seller_id",
    "standard_id",
    "certificate_no",
    "issued_on",
    "expires_on",
    "evidence_attachment_id",
}


def dhaka_today(record):
    """Today on the reader's calendar; Asia/Dhaka when no zone is set (a cron)."""
    tz = record.env.context.get("tz") or record.env.user.tz or "Asia/Dhaka"
    return fields.Date.context_today(record.with_context(tz=tz))


class FixSellerStandard(models.Model):
    _name = "fix.seller.standard"
    _description = "Seller Standard / Course"
    _order = "code, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    kind = fields.Selection(
        [
            ("standard", "Service Standard"),
            ("course", "Training Course"),
            ("certificate", "External Certificate"),
        ],
        required=True,
        default="standard",
    )
    issuing_body = fields.Char(string="Issued By")
    validity_months = fields.Integer(
        string="Validity (months)",
        default=12,
        help="How long a certificate of this standard is valid; 0 means it does not expire.",
    )
    category_ids = fields.Many2many(
        "product.category",
        "fix_seller_standard_category_rel",
        "standard_id",
        "category_id",
        string="Required for Categories",
        help="A seller approved for one of these service categories must hold this standard.",
    )
    description = fields.Text()
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("UNIQUE (code)", "A standard code is unique.")

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "[%s] %s" % (rec.code, rec.name) if rec.code else rec.name

    @api.constrains("validity_months")
    def _check_validity(self):
        for rec in self:
            if rec.validity_months < 0:
                raise ValidationError("A validity cannot be negative.")


class FixSellerCertification(models.Model):
    _name = "fix.seller.certification"
    _description = "Seller Certification"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "seller_id, expires_on, id"

    company_id = fields.Many2one(
        "res.company", related="seller_id.company_id", store=True, index=True, readonly=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        related="seller_id.operating_unit_id",
        store=True,
        readonly=True,
    )
    seller_id = fields.Many2one(
        "fix.marketplace.seller", required=True, ondelete="cascade", index=True, tracking=True
    )
    standard_id = fields.Many2one(
        "fix.seller.standard",
        string="Standard / Course",
        required=True,
        ondelete="restrict",
        index=True,
        tracking=True,
    )
    certificate_no = fields.Char(string="Certificate No.", tracking=True)
    issued_on = fields.Date(required=True, tracking=True)
    expires_on = fields.Date(
        tracking=True,
        help="Defaults to the issue date plus the standard's validity; empty means no expiry.",
    )
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Evidence (certificate scan)", copy=False, ondelete="restrict"
    )
    state = fields.Selection(
        CERT_STATES, required=True, default="draft", readonly=True, tracking=True, copy=False
    )
    submitted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_at = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Text(string="Reviewer Note", readonly=True, copy=False)
    days_to_expiry = fields.Integer(compute="_compute_expiry")
    expiry_status = fields.Selection(
        [
            ("none", "No Expiry"),
            ("valid", "Valid"),
            ("expiring", "Expiring Soon"),
            ("expired", "Expired"),
        ],
        compute="_compute_expiry",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_by_id",
            "verified_by_id",
            "verified_at",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state not in EDITABLE_STATES:
            locked |= _TERMS
        return locked

    @api.depends("seller_id.name", "standard_id.code")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s — %s" % (
                rec.standard_id.code or "?",
                rec.seller_id.name or "?",
            )

    @api.depends("expires_on")
    def _compute_expiry(self):
        today = dhaka_today(self)
        for rec in self:
            if not rec.expires_on:
                rec.days_to_expiry = 0
                rec.expiry_status = "none"
                continue
            days = (rec.expires_on - today).days
            rec.days_to_expiry = days
            if days < 0:
                rec.expiry_status = "expired"
            elif days <= EXPIRY_WARNING_DAYS:
                rec.expiry_status = "expiring"
            else:
                rec.expiry_status = "valid"

    @api.constrains("issued_on", "expires_on")
    def _check_dates(self):
        for rec in self:
            if rec.expires_on and rec.issued_on and rec.expires_on <= rec.issued_on:
                raise ValidationError("A certificate expires after it is issued.")

    @api.model_create_multi
    def create(self, vals_list):
        _assert_role(self.env, OPERATOR_GROUP, "Recording a seller certification")
        standards = self.env["fix.seller.standard"].sudo()
        for vals in vals_list:
            if vals.get("expires_on") or not vals.get("issued_on"):
                continue
            standard = standards.browse(vals.get("standard_id")).exists()
            if standard and standard.validity_months:
                vals["expires_on"] = fields.Date.to_date(vals["issued_on"]) + relativedelta(
                    months=standard.validity_months
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state not in EDITABLE_STATES):
                changed = [
                    n for n in _TERMS & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "Certification %s is %s: its %s are pinned to what was submitted."
                        % (rec.display_name, rec.state, ", ".join(sorted(changed)))
                    )
        return super().write(vals)

    # ---- lifecycle --------------------------------------------------------
    def action_submit(self):
        _assert_role(self.env, OPERATOR_GROUP, "Submitting a seller certification")
        today = dhaka_today(self)
        for rec in self:
            if rec.state not in EDITABLE_STATES:
                raise UserError("Only a draft or rejected certification is submitted.")
            if not rec.evidence_attachment_id:
                raise UserError(
                    "Attach the certificate evidence before submitting %s." % rec.display_name
                )
            if rec.issued_on > today:
                raise UserError("A certificate issued in the future cannot be submitted.")
            if rec.expires_on and rec.expires_on < today:
                raise UserError("%s has already expired." % rec.display_name)
            rec._guarded().write(
                {"state": "submitted", "submitted_by_id": self.env.uid, "decision_note": False}
            )
        return True

    def action_verify(self):
        _assert_role(self.env, COMPLIANCE_GROUP, "Verifying a seller certification")
        today = dhaka_today(self)
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted certification is verified.")
            if not self.env.su and self.env.user in (
                rec.create_uid | rec.submitted_by_id | _seller_users(rec.seller_id)
            ):
                raise UserError(
                    "Segregation of duties: whoever recorded or submitted %s, or acts for the "
                    "seller, does not verify it." % rec.display_name
                )
            if not rec.evidence_attachment_id:
                raise UserError("%s has no evidence attached." % rec.display_name)
            if rec.expires_on and rec.expires_on < today:
                raise UserError("%s has expired: it cannot be verified." % rec.display_name)
            rec._guarded().write(
                {
                    "state": "verified",
                    "verified_by_id": self.env.uid,
                    "verified_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        _assert_role(self.env, COMPLIANCE_GROUP, "Rejecting a seller certification")
        if not (reason or "").strip():
            raise UserError("Give the reason the certification is rejected.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted certification is rejected.")
            rec._guarded().write({"state": "rejected", "decision_note": reason.strip()})
        return True

    def action_revoke(self, reason=None):
        _assert_role(self.env, COMPLIANCE_GROUP, "Revoking a seller certification")
        if not (reason or "").strip():
            raise UserError("Give the reason the certification is revoked.")
        for rec in self:
            if rec.state != "verified":
                raise UserError("Only a verified certification is revoked.")
            rec._guarded().write({"state": "revoked", "decision_note": reason.strip()})
        return True

    @api.model
    def cron_expire_certifications(self):
        """Daily: a verified certification past its expiry date is expired."""
        today = dhaka_today(self)
        lapsed = self.sudo().search(
            [("state", "=", "verified"), ("expires_on", "!=", False), ("expires_on", "<", today)]
        )
        for rec in lapsed:
            rec._guarded().write({"state": "expired"})
            rec.message_post(body="Expired on %s." % rec.expires_on)
        return len(lapsed)
