# cd_contract_core — the contract link on the service order (FLAW-08.1).
#
# The A04 audit's F-1 finding was that contract P&L ignores delivery cost, and
# the M08 controller said why in its own comment: "Delivery COST is not linked
# to the contract in the data model". The remediation that followed added
# total_delivery_cost / contract_margin_bdt / contract_margin_pct to
# fix.contract but computed them from a hard-coded `delivery_cost = 0.0`, so
# every contract reported a 100% margin. The grep-based certification suite
# asserted the FIELDS existed and passed.
#
# This supplies the missing relation so the cost can actually be measured.
from odoo import api, fields, models


class FixServiceOrderContract(models.Model):
    """Adds the contract a service order was delivered under."""

    _inherit = "fix.service.order"

    contract_id = fields.Many2one(
        "fix.contract",
        string="Delivered Under Contract",
        index=True,
        ondelete="set null",
        tracking=True,
        help="The AMC/RAMC/managed contract this work was delivered under. "
        "Entitlement work costs the contract; chargeable work does not.",
    )

    delivery_cost_bdt = fields.Monetary(
        string="Delivery Cost",
        currency_field="currency_id",
        compute="_compute_delivery_cost_bdt",
        store=True,
        help="Parts plus labour actually consumed on this order, taken from "
        "its latest estimate. This is cost to serve, not what was billed.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    # The cost comes from the latest estimate, so it must follow the estimates:
    # depending on contract_id alone left it at whatever the first compute saw,
    # and an estimate raised or revised later never reached the contract margin
    # (found by the A02 second pass, when intake started computing it early).
    @api.depends(
        "contract_id",
        "estimate_ids.version",
        "estimate_ids.parts_total",
        "estimate_ids.labour_total",
    )
    def _compute_delivery_cost_bdt(self):
        Estimate = self.env["fix.estimate"]
        for order in self:
            estimate = Estimate.search(
                [("order_id", "=", order.id)], order="version desc, id desc", limit=1
            )
            # Parts and labour are the cost to serve. The diagnostic fee is a
            # charge line, not a consumed cost, so it is excluded.
            order.delivery_cost_bdt = (
                (estimate.parts_total or 0.0) + (estimate.labour_total or 0.0) if estimate else 0.0
            )
