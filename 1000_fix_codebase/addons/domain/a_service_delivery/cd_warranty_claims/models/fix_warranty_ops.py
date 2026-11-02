# M09 warranty operations: warranty transfers, recall campaigns and claim
# appeals on top of fix.warranty / .claim / .evidence / .product / .provision.
from odoo import fields, models


class FixWarrantyTransfer(models.Model):
    _name = "fix.warranty.transfer"
    _description = "Warranty Transfer"
    _order = "effective_date desc, id desc"

    name = fields.Char(required=True)
    warranty_id = fields.Many2one("fix.warranty", required=True, ondelete="cascade", index=True)
    from_partner_id = fields.Many2one("res.partner", string="From Customer")
    to_partner_id = fields.Many2one("res.partner", string="To Customer")
    effective_date = fields.Date(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("effective", "Effective"),
            ("void", "Void"),
        ],
        required=True,
        default="draft",
    )
    note = fields.Char()


class FixWarrantyRecall(models.Model):
    _name = "fix.warranty.recall"
    _description = "Warranty Recall Campaign"
    _order = "launched_on desc, id desc"

    name = fields.Char(required=True)
    brand_id = fields.Many2one("fix.brand", string="Brand", index=True)
    product_ref = fields.Char(string="Product / Model Reference")
    affected_units = fields.Integer(required=True, default=0)
    covered_units = fields.Integer(
        default=0, help="Units actually contacted / serviced under the recall."
    )
    launched_on = fields.Date()
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="planned",
    )
    note = fields.Char()


class FixClaimAppeal(models.Model):
    _name = "fix.claim.appeal"
    _description = "Warranty Claim Appeal"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True)
    claim_id = fields.Many2one("fix.warranty.claim", required=True, ondelete="cascade", index=True)
    reason = fields.Text(required=True)
    decision = fields.Selection(
        [
            ("pending", "Pending"),
            ("upheld", "Upheld (claim re-opened)"),
            ("rejected", "Appeal rejected"),
        ],
        required=True,
        default="pending",
    )
    decided_at = fields.Datetime(readonly=True)
