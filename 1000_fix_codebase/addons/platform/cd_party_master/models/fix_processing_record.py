# fix.processing.record — the PDPA record of processing (M33, FR-CPM-044,
# BRU-CPM-15, spec section 10.1). M33 capture audit 2026-11-14: the spec's
# P0 register did not exist anywhere in the estate, so the "Consent & DSR"
# page could not show what personal data was processed, for which purpose,
# on which lawful basis, shared with whom and kept for how long.
#
# The record is evidence, so it is append-only: nobody edits a row, and a row
# is never deleted inside the five-year statutory period, even when the party
# itself is erased (the party link is cleared, the party id is kept).
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_party_security import DPO_GROUP, require_group

# BRU-CPM-15: retained a minimum of five years, independently of erasure.
RETENTION_YEARS = 5

# The bases evidenced in this programme: consent (BRU-CPM-07), contract and
# legal obligation (fix.party.import.batch). Legitimate interest is not an
# enumerated basis under the PDPA 2026 (Act 63 of 2026).
LAWFUL_BASES = [
    ("consent", "Consent"),
    ("contract", "Contractual necessity"),
    ("legal_obligation", "Legal obligation"),
]

PURPOSES = [
    ("service_updates", "Service Updates"),
    ("marketing", "Marketing"),
    ("research", "Research & Analytics"),
    ("collections", "Debt Collection"),
    ("profiling", "Profiling"),
    ("call_recording", "Call Recording"),
    ("service_delivery", "Service Delivery"),
    ("billing", "Billing & Accounts"),
    ("statutory", "Statutory Reporting"),
]


class FixProcessingRecord(models.Model):
    """One processing activity on one party's personal data."""

    _name = "fix.processing.record"
    _description = "Record of Processing (PDPA)"
    _order = "occurred_at desc, id desc"

    party_id = fields.Many2one(
        "res.partner",
        string="Party",
        index=True,
        ondelete="set null",
        help="Cleared if the party record is ever removed; the party id below stays",
    )
    party_ref_id = fields.Integer(
        string="Party Id",
        readonly=True,
        index=True,
        help="The party's id at capture, kept after erasure (BRU-CPM-15)",
    )
    purpose = fields.Selection(PURPOSES, string="Purpose", required=True)
    lawful_basis = fields.Selection(LAWFUL_BASES, string="Lawful Basis", required=True)
    consent_id = fields.Many2one(
        "fix.consent",
        string="Consent Relied On",
        index=True,
        ondelete="set null",
        help="Required when the lawful basis is consent: the granted consent "
        "this processing relies on",
    )
    categories = fields.Char(
        string="Data Categories",
        required=True,
        help="e.g. name, mobile number, service address, device serial",
    )
    recipients = fields.Char(
        string="Recipients / Transfers",
        help="Who receives the data: an internal module, a courier, a brand OEM. "
        "Empty means it stays inside 1000FiX.",
    )
    retention_months = fields.Integer(
        string="Retention (months)",
        required=True,
        default=RETENTION_YEARS * 12,
        help="How long the processed data is kept",
    )
    occurred_at = fields.Datetime(
        string="Occurred At", required=True, default=fields.Datetime.now, index=True
    )
    source = fields.Selection(
        [
            ("manual", "Recorded by the Data Protection Officer"),
            ("consent_capture", "Consent captured"),
            ("consent_withdrawal", "Consent withdrawn"),
        ],
        string="Recorded From",
        required=True,
        default="manual",
        readonly=True,
    )
    note = fields.Text(string="Note")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("party_id", "purpose", "occurred_at")
    def _compute_display_name(self):
        labels = dict(PURPOSES)
        for rec in self:
            rec.display_name = "%s · %s" % (
                labels.get(rec.purpose, rec.purpose or "?"),
                rec.party_id.display_name or ("party #%s" % rec.party_ref_id),
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            require_group(self.env, DPO_GROUP, "Recording a processing activity")
            for vals in vals_list:
                # the automatic sources are the system's to write
                vals["source"] = "manual"
        for vals in vals_list:
            if vals.get("party_id"):
                vals["party_ref_id"] = vals["party_id"]
        return super().create(vals_list)

    @api.constrains("lawful_basis", "consent_id", "party_id", "purpose")
    def _check_consent_basis(self):
        for rec in self:
            if rec.lawful_basis != "consent":
                continue
            if not rec.consent_id:
                raise ValidationError(
                    "Processing on the basis of consent must name the consent it relies "
                    "on (BRU-CPM-07)."
                )
            if rec.party_id and rec.consent_id.partner_id != rec.party_id:
                raise ValidationError("The consent relied on belongs to another party.")

    @api.constrains("retention_months")
    def _check_retention(self):
        for rec in self:
            if rec.retention_months <= 0:
                raise ValidationError("The retention period must be at least one month.")

    def write(self, vals):
        # Erasing a party clears the link (ondelete set null): the only change
        # the record ever takes.
        if not self.env.su and set(vals) - {"party_id"}:
            raise UserError(
                "A processing record is evidence and cannot be edited. Record a new "
                "activity instead (FR-CPM-044)."
            )
        if "party_id" in vals and vals["party_id"] and not self.env.su:
            raise UserError("A processing record cannot be moved to another party.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError(
                "A processing record is retained for at least %d years and cannot be "
                "deleted (BRU-CPM-15)." % RETENTION_YEARS
            )
        limit = fields.Datetime.now() - relativedelta(years=RETENTION_YEARS)
        if any(rec.occurred_at and rec.occurred_at > limit for rec in self):
            raise UserError(
                "A processing record is kept for %d years from the activity, independently "
                "of party erasure (BRU-CPM-15)." % RETENTION_YEARS
            )
        return super().unlink()

    @api.model
    def _record_from_consent(self, consent, source):
        """AUT-CPM-06: a consent capture or withdrawal is itself a processing
        activity on the party's contact data, recorded by the system."""
        return self.sudo().create(
            {
                "party_id": consent.partner_id.id,
                "purpose": consent.purpose,
                "lawful_basis": "consent",
                "consent_id": consent.id,
                "categories": "contact preference (%s)" % consent.channel,
                "occurred_at": fields.Datetime.now(),
                "source": source,
                "company_id": consent.company_id.id,
            }
        )
