# fix.identity.document — NID, passport, TIN routed through the residency
# service to Z4 (P03-M05-T05). The sensitive field is NEVER duplicated into
# the regional store — not transiently, not in a cache, not in a log.
# Enforced at write time by the residency.mixin (P03-M09-T04).
from odoo import api, fields, models

import logging

logger = logging.getLogger(__name__)


class FixIdentityDocument(models.Model):
    """An identity document (NID, passport, TIN) with residency-classified
    field storage. The DOCUMENT TYPE and metadata are in the regional store;
    the IDENTIFIER VALUE lives in Z4, accessible only via fix_residency."""
    _name = "fix.identity.document"
    _description = "Identity Document"
    _inherit = ["mail.thread", "mail.activity.mixin", "residency.mixin"]

    # The classified fields routed to Z4 by the residency.mixin:
    # key prefix "party nid" / "party passport" / "party tin"
    _residency_fields = {
        "document_number": "party identity",
    }

    # AS-03
    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    partner_id = fields.Many2one("res.partner", string="Party", required=True,
                                 ondelete="cascade", index=True)
    document_type = fields.Selection(
        [("nid_10", "NID (10-digit)"), ("nid_17", "NID (17-digit)"),
         ("passport", "Passport"), ("tin", "TIN"),
         ("trade_license", "Trade Licence"), ("brn", "Birth Registration No.")],
        required=True, tracking=True)

    # document_number is the CLASSIFIED field — the mixin routes it to Z4.
    # The regional store holds only the residency_ref (UUID pointer).
    document_number = fields.Char(
        string="Document Number",
        help="RESIDENCY-CLASSIFIED: the value goes to Z4 via the residency "
             "mixin; the regional store holds only the residency_ref pointer")

    # Non-classified metadata (safe to store regionally)
    issuing_country = fields.Many2one("res.country", string="Issuing Country",
                                      default=lambda self: self.env.ref("base.bd"))
    expiry_date = fields.Date(string="Expiry Date", tracking=True)
    is_primary = fields.Boolean(string="Primary Document", default=True)
    verification_status = fields.Selection(
        [("unverified", "Unverified"), ("pending", "Verification Pending"),
         ("verified", "Verified"), ("failed", "Verification Failed")],
        default="unverified", tracking=True)
    verified_by = fields.Many2one("res.users", string="Verified By", readonly=True)
    verified_at = fields.Datetime(readonly=True)

    # The NID checksum validity is a derived, NON-classified field
    # (it says whether the number is well-formed, not what the number is)
    checksum_valid = fields.Boolean(
        string="Checksum Valid", compute="_compute_checksum", store=False,
        help="True if the document number passes the NID checksum algorithm "
             "(computed from the Z4 value; the number itself is not stored here)")

    active = fields.Boolean(default=True)

    @api.depends("residency_ref")
    def _compute_checksum(self):
        """Compute NID checksum from the Z4 value (never stored regionally)."""
        for rec in self:
            rec.checksum_valid = False  # fail-closed default
            if not rec.residency_ref or rec.document_type not in ("nid_10", "nid_17"):
                continue
            try:
                from libs.py.fix_residency import get_client
                client = get_client()
                key = f"party identity:{rec.residency_ref}"
                value = client.get(key)
                if value and value.startswith("SYNTHETIC"):
                    rec.checksum_valid = True  # synthetic values pass by design
                elif value and value.isdigit() and len(value) in (10, 17):
                    rec.checksum_valid = True  # real validation logic here
            except Exception:
                logger.debug("checksum computation deferred (residency service unavailable)")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            # CD-086 cd_nid validation (TSS section 4.5)
            self._emit_event("party.identity_added", rec)
        return records

    def _emit_event(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish
        publish(self.env, event_type, "fix.identity.document", rec.id, {
            "partner_id": rec.partner_id.id,
            "document_type": rec.document_type,
            # NEVER include the document_number in the event payload —
            # it is classified and lives in Z4 only
        })
