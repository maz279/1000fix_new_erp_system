# fix.service.order bridge (M02): the missing seam between the order book
# and the dispatch pipeline. 921 service orders existed with ZERO field
# orders — nothing ever created one. On-site jobs now hand over with one
# action; the field order inherits zone (branch), address (customer), the
# SLA deadline (from the order's policy where set) and stays linked for the
# round trip back to the order record.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixServiceOrderFieldBridge(models.Model):
    _inherit = "fix.service.order"

    field_order_ids = fields.One2many("fix.field.order", "order_id", string="Field Orders")
    field_order_count = fields.Integer(string="Field Orders", compute="_compute_field_order_count")

    @api.depends("field_order_ids")
    def _compute_field_order_count(self):
        for order in self:
            order.field_order_count = len(order.field_order_ids)

    def action_create_field_order(self):
        """Hand an on-site job to the dispatch pipeline (M02). Creates a
        DRAFT field order; dispatch itself stays a dispatcher action with
        the suggestion engine (action_suggest_technicians)."""
        FieldOrder = self.env["fix.field.order"]
        created = FieldOrder
        for order in self:
            if order.service_type != "onsite":
                raise UserError(
                    "Only on-site service orders go to field dispatch "
                    "(%s is %s)." % (order.name, order.service_type)
                )
            if order.state in ("closed", "cancelled"):
                raise UserError(
                    "Order %s is %s — it can no longer be dispatched." % (order.name, order.state)
                )
            # A02 audit M01-13 (M01-owned line): no second live field order.
            order._fix_assert_no_live_handoff(
                order.field_order_ids.filtered(
                    lambda f: f.state not in ("completed", "cancelled", "declined")
                ),
                "field order",
            )
            zone = order.branch_id.zone_id
            if not zone:
                raise UserError(
                    "Branch %s has no dispatch zone — set one before field dispatch."
                    % order.branch_id.name
                )
            partner = order.customer_id
            address = " ".join(
                p for p in [partner.street, partner.city, partner.state_id.name] if p
            )
            # an order's own OU is optional; its branch's is not (the M09
            # auto-create NOT NULL lesson, applied here too)
            ou = order.operating_unit_id or order.branch_id.operating_unit_id
            created |= FieldOrder.create(
                {
                    "order_id": order.id,
                    "zone_id": zone.id,
                    "operating_unit_id": ou.id,
                    # A02 audit M01-13 (bridge mapping owned by M01): the
                    # order's priorities are normal/high/urgent/emergency;
                    # the old '0'-'3' keys never matched, so an emergency went
                    # out as field priority '1'.
                    "priority": {
                        "normal": "1",
                        "high": "2",
                        "urgent": "3",
                        "emergency": "3",
                    }.get(order.priority or "normal", "1"),
                    "scheduled_start": (
                        order.sla_resolution_deadline and order.sla_resolution_deadline
                    )
                    or fields.Datetime.now(),
                    "sla_deadline": order.sla_resolution_deadline,
                    "customer_address": address or None,
                    "notes": order.fault_description or None,
                }
            )
        return created

    def action_view_field_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Field Orders",
            "res_model": "fix.field.order",
            "view_mode": "list,form",
            "domain": [("order_id", "=", self.id)],
        }
