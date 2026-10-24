# fix.warranty — warranty status model (P04-M01-T04).
# Built in the registry so M09 reads rather than duplicates.
from odoo import fields, models


class FixWarranty(models.Model):
    """A warranty claim/status record for a device."""

    _name = "fix.warranty"
    _description = "Warranty"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "device_id, start_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )

    warranty_type = fields.Selection(
        [
            ("manufacturer", "Manufacturer Warranty"),
            ("extended", "Extended/1000FiX"),
            ("brand_auth", "Brand Authorisation"),
            ("none", "No Warranty"),
        ],
        required=True,
        default="manufacturer",
        tracking=True,
    )
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True, tracking=True)
    status = fields.Selection(
        [
            ("active", "Active"),
            ("expired", "Expired"),
            ("voided", "Voided"),
            ("pending", "Pending Verification"),
        ],
        default="active",
        required=True,
        tracking=True,
    )

    # Warranty terms
    coverage_details = fields.Text()
    deductible = fields.Monetary(string="Deductible", currency_field="currency_id", default=0.0)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )

    # Proof
    proof_document_id = fields.Many2one(
        "fix.document",
        string="Proof Document",
        help="Purchase receipt or warranty card via the M24-core API",
    )
    verified_by = fields.Many2one("res.users", readonly=True)
    verified_at = fields.Datetime(readonly=True)
