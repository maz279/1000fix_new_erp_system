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
    # A02 ERP audit pass 2 M02-06: a failed visit's follow-up brings the
    # device in (M03 pickup leg) and, for a workshop transfer, flags the
    # order for the workshop (M31)
    field_pickup_requested = fields.Boolean(
        string="Field Visit Converted To Pickup", readonly=True, copy=False
    )
    field_workshop_transfer = fields.Boolean(
        string="Field Visit Transferred To Workshop", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "field_pickup_requested",
            "field_workshop_transfer",
        }

    def _fix_extra_charges(self) -> list:
        """D21: an unwaived wasted-visit fee is billed with the repair
        (CHG-CALLOUT); a dispatcher's waiver takes it off."""
        charges = super()._fix_extra_charges()
        # read as the system: whoever settles or closes the order (a counter
        # clerk) need not read field orders to be charged their fees
        field_orders = self.sudo().field_order_ids
        if not field_orders:
            return charges
        visits = (
            self.env["fix.field.visit.exception"]
            .sudo()
            .search(
                [
                    ("field_order_id", "in", field_orders.ids),
                    ("wasted_fee_bdt", ">", 0),
                    ("fee_waived_by_id", "=", False),
                ],
                order="id",
            )
        )
        for visit in visits:
            charges.append(
                {
                    "code": "CHG-CALLOUT",
                    "line_type": "callout",
                    "description": "Wasted visit %s (%s)"
                    % (
                        visit.name,
                        dict(visit._fields["exception_type"].selection).get(
                            visit.exception_type, visit.exception_type
                        ),
                    ),
                    "net": round(visit.wasted_fee_bdt, 2),
                }
            )
        return charges

    def _fix_field_pickup_requested(self) -> bool:
        """cd_consignment asks this to start an on-site order with a pickup."""
        self.ensure_one()
        return bool(self.field_pickup_requested)

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
                    # A02 ERP audit M02-F18: the visit was scheduled AT the SLA
                    # deadline (or "now"), so every job looked due at its
                    # breach. The appointment is the dispatcher's to agree with
                    # the customer; until then the order is unscheduled.
                    "scheduled_start": False,
                    "sla_deadline": order.sla_resolution_deadline,
                    "customer_address": address or None,
                    # A02 ERP audit pass 2 M02-05: the site position the
                    # failed-visit evidence and the suggestion engine measure
                    # against (it was never set, so both checks were inert)
                    "latitude": partner.partner_latitude
                    if "partner_latitude" in partner._fields
                    else 0.0,
                    "longitude": partner.partner_longitude
                    if "partner_longitude" in partner._fields
                    else 0.0,
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
