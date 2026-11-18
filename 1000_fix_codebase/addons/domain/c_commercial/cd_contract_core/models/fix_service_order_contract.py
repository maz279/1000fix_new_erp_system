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
#
# A04 build (2026-11-04) M08-5/C8: M01 granted an AMC zero-charge on ANY
# linked contract (a draft one, another customer's, one that does not cover
# the device, an exhausted one) and never drew the entitlement down. The
# basis is now the contract's own entitlement: in force on the day, the
# order's customer, the device covered, a line with quantity left. The
# entitlement is consumed when the order is approved, once, and the link to
# the contract freezes once the order has been taken in.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_contract import IN_FORCE

# The order states after which the contract an order is delivered under is fixed.
_CONTRACT_OPEN_STATES = ("draft", "intake")


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
    contract_entitlement_id = fields.Many2one(
        "fix.contract.entitlement",
        string="Entitlement Drawn",
        readonly=True,
        copy=False,
        help="The contract entitlement line this order consumed at approval.",
    )
    contract_entitlement_qty = fields.Float(string="Quantity Drawn", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "contract_entitlement_id",
            "contract_entitlement_qty",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state not in _CONTRACT_OPEN_STATES:
            locked.add("contract_id")
        return locked

    def write(self, vals):
        if "contract_id" in vals and self and not self._fix_guard_open():
            for order in self:
                if order.state not in _CONTRACT_OPEN_STATES and (
                    (vals["contract_id"] or False) != (order.contract_id.id or False)
                ):
                    raise UserError(
                        "Order %s was taken in under its contract; the contract it is "
                        "delivered under cannot change now." % order.name
                    )
        return super().write(vals)

    # ---- the AMC entitlement basis (BRU-SRM-03) ------------------------------
    def _fix_pm_visit(self):
        self.ensure_one()
        return (
            self.env["fix.contract.pm.visit"]
            .sudo()
            .search([("service_order_id", "=", self.id)], limit=1)
        )

    def _fix_entitlement_types(self):
        """The entitlement an order draws: a PM visit draws a visit; a repair
        an incident (labour-hour lines are drawn by the hours worked, which
        M01 does not yet report, so they do not open a zero-charge order)."""
        return ("visits",) if self._fix_pm_visit() else ("incidents",)

    def _fix_contract_entitlement_line(self):
        """The entitlement line that covers this order, or an empty recordset."""
        self.ensure_one()
        Line = self.env["fix.contract.entitlement"].sudo()
        if self.contract_entitlement_id:
            return self.contract_entitlement_id.sudo()  # already drawn for this order
        contract = self.contract_id.sudo()
        if not contract or not self.device_id:
            return Line
        if not contract._contract_in_force_on(fields.Date.context_today(self)):
            return Line
        customer = (self.customer_id.commercial_partner_id or self.customer_id).sudo()
        if contract.customer_id.commercial_partner_id != customer:
            return Line
        if not contract._contract_covers_device(self.device_id, fields.Date.context_today(self)):
            return Line
        lines = contract.entitlement_ids.filtered(
            lambda e: e.entitlement_type in self._fix_entitlement_types()
            and e.device_id.id in (False, self.device_id.id)
            and (e.quantity_included == 0 or e.quantity_remaining >= 1)
        )
        # counted lines before unlimited ones, device-specific before estate-wide
        return lines.sorted(
            key=lambda e: (1 if e.quantity_included == 0 else 0, 0 if e.device_id else 1, e.id)
        )[:1]

    def _fix_msp_covers(self) -> bool:
        """An entitled M05 MSP layer on this contract monitors the order's
        device, for the order's customer. Read softly: M05 is optional."""
        self.ensure_one()
        Asset = self.env.get("fix.monitored.asset")
        contract = self.contract_id.sudo()
        if Asset is None or not contract or not self.device_id:
            return False
        if contract.state not in IN_FORCE or contract.customer_id.commercial_partner_id != (
            self.customer_id.commercial_partner_id or self.customer_id
        ):
            return False
        assets = Asset.sudo().search(
            [
                ("device_id", "=", self.device_id.id),
                ("msp_contract_id.contract_id", "=", contract.id),
            ]
        )
        return any(getattr(a.msp_contract_id, "entitled", True) for a in assets)

    def _fix_zero_charge_basis(self) -> str:
        basis = super()._fix_zero_charge_basis()
        if self.order_category != "amc" or not basis.startswith("AMC contract "):
            return basis
        line = self._fix_contract_entitlement_line()
        if line:
            return "AMC contract %s (%s entitlement)" % (
                self.contract_id.display_name,
                line.entitlement_type,
            )
        if self._fix_msp_covers():
            # a managed-services contract covers its MONITORED assets (M05),
            # paid by the per-device fee rather than drawn from a line
            return "AMC contract %s (managed asset under MSP)" % self.contract_id.display_name
        # the contract does not cover this order: only an approved goodwill
        # or a confirmed rework still waives the charge
        if self.is_goodwill and self.goodwill_approved_by:
            return "goodwill approved by %s" % self.goodwill_approved_by.name
        if self.is_rework and self.rework_approved_by:
            return "rework confirmed by %s" % self.rework_approved_by.name
        return ""

    def _fix_consume_contract_entitlement(self):
        """Draw one unit of the covering entitlement, once per order."""
        for order in self:
            if order.order_category != "amc" or order.contract_entitlement_id:
                continue
            if not order._fix_zero_charge_basis().startswith("AMC contract "):
                continue
            line = order._fix_contract_entitlement_line()
            if not line:
                continue
            if not line.sudo().consume(1.0, source_ref=order.name or str(order.id)):
                raise UserError(
                    "Order %s: the contract entitlement was used up before the order "
                    "was approved. Price the work as standard service." % order.name
                )
            order.sudo()._guarded().write(
                {"contract_entitlement_id": line.id, "contract_entitlement_qty": 1.0}
            )

    def action_approve(self):
        result = super().action_approve()
        self.filtered(lambda o: o.state == "approved")._fix_consume_contract_entitlement()
        return result

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
