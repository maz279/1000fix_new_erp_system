# fix_import_purchase_link — the import purchase order and the import order,
# raised from either side (user request, 12 Nov 2026).
#
# Purchasing has two formats: a LOCAL purchase order (M16, taka or US dollars)
# and an IMPORT purchase order (M16, the supplier's currency) that an M44
# import order fulfils. Either comes first:
#   - "Create Import Order" on an import purchase order raises the import order
#     with the PO's supplier, currency and lines (each product as its spare
#     part), linked to the PO;
#   - "Create Purchase Order" on an import order with no PO raises a draft
#     import purchase order from the import order's lines and links it.
# The PO still needs its requisition (or a manager's exception) and the routed
# approval before it is sent; the import order still needs its proforma, FX,
# HS and IRC before anything ships. Nothing here bypasses either.
# The import order's lines also carry the supplier's item code and unit, and
# the order carries a copy of its source document (indent or signed PO).
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_import_common import OFFICER, require_group

GROUP_BUYER = "cd_requisition.group_fix_procurement_buyer"
LIVE_PO_STATES = ("draft", "sent", "acknowledged", "partially_received", "received")


class FixPurchaseOrderImportLink(models.Model):
    _inherit = "fix.purchase.order"

    import_order_ids = fields.One2many(
        "fix.import.order", "purchase_order_id", string="Import Orders"
    )
    import_order_refs = fields.Char(string="Import Orders", compute="_compute_import_order_refs")

    @api.depends("import_order_ids.name", "import_order_ids.state")
    def _compute_import_order_refs(self):
        for po in self:
            po.import_order_refs = ", ".join(
                "%s (%s)" % (o.name, o.state) for o in po.sudo().import_order_ids
            )

    def action_create_import_order(self):
        """Raise the M44 import order this import purchase order is fulfilled by."""
        require_group(self.env, OFFICER, "Creating an import order")
        Part = self.env["fix.spare.part"].sudo()
        Order = self.env["fix.import.order"]
        for po in self:
            if po.purchase_type != "import":
                raise UserError(
                    "%s is a local purchase order: an import order is raised from an import "
                    "purchase order." % po.name
                )
            if po.state not in LIVE_PO_STATES:
                raise UserError("Purchase order %s is %s." % (po.name, po.state))
            if po.sudo().import_order_ids:
                raise UserError(
                    "Purchase order %s already has import order %s."
                    % (po.name, ", ".join(po.sudo().import_order_ids.mapped("name")))
                )
            if not po.line_ids:
                raise UserError("Purchase order %s has no lines to import." % po.name)
            lines, missing = [], []
            for line in po.line_ids:
                part = Part.search([("product_id", "=", line.product_id.id)], limit=1)
                if not part:
                    missing.append(line.product_id.display_name)
                    continue
                lines.append(
                    (
                        0,
                        0,
                        {
                            "part_id": part.id,
                            "description": line.description or part.name,
                            "quantity": line.qty_ordered,
                            "unit_price": line.unit_price,
                        },
                    )
                )
            if missing:
                raise UserError(
                    "These products have no spare part in M15, so they cannot be imported: %s. "
                    "Create the spare part (naming the product) first." % ", ".join(missing)
                )
            Order.create(
                {
                    "name": "IMP-%s" % po.name,
                    "supplier_id": po.vendor_id.id,
                    "purchase_order_id": po.id,
                    "operating_unit_id": po.operating_unit_id.id,
                    "currency_id": po.currency_id.id,
                    "fob_value": sum(po.line_ids.mapped("line_total")),
                    "line_ids": lines,
                }
            )
        return True


class FixImportOrderPurchaseLink(models.Model):
    _inherit = "fix.import.order"

    order_file = fields.Binary(
        string="Order Document (copy)",
        attachment=True,
        copy=False,
        help="The supplier's indent or the signed purchase order this import rests on.",
    )
    order_filename = fields.Char(string="Order Document Name", copy=False)

    def _import_check_po_issued(self, what):
        """A linked purchase order raised alongside the import (still a draft)
        must be approved and sent before money or goods move against it."""
        for order in self:
            po = order.sudo().purchase_order_id
            if po and po.state == "draft":
                raise UserError(
                    "%s: purchase order %s is still a draft. Have it approved and send it to "
                    "the supplier first." % (what, po.name)
                )

    def action_receive(self):
        self._import_check_po_issued("Receiving the import")
        return super().action_receive()

    def action_create_purchase_order(self):
        """Raise the draft import purchase order this import order fulfils."""
        if not (self.env.su or self.env.user.has_group(GROUP_BUYER)):
            raise UserError(
                "Creating a purchase order needs the Procurement Buyer role, which you do not hold."
            )
        Po = self.env["fix.purchase.order"]
        for order in self:
            if order.purchase_order_id:
                raise UserError(
                    "Import order %s already has purchase order %s."
                    % (order.name, order.purchase_order_id.name)
                )
            if order.state != "draft":
                raise UserError("Import order %s is %s." % (order.name, order.state))
            if not order.supplier_id:
                raise UserError("Name the supplier of import order %s first." % order.name)
            if not order.line_ids:
                raise UserError("Import order %s has no lines to order." % order.name)
            missing = [
                line.part_id.display_name
                for line in order.line_ids
                if not line.part_id.sudo().product_id
            ]
            if missing:
                raise UserError(
                    "These spare parts name no purchasing product in M15: %s. "
                    "Name the product on the spare part first." % ", ".join(missing)
                )
            ou = order.operating_unit_id or self.env.user.default_operating_unit_id
            if not ou:
                raise UserError("Name the operating unit of import order %s first." % order.name)
            po = Po.create(
                {
                    "vendor_id": order.supplier_id.id,
                    "operating_unit_id": ou.id,
                    "purchase_type": "import",
                    "currency_id": order.currency_id.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": line.part_id.sudo().product_id.id,
                                "description": line.description or line.part_id.name,
                                "qty_ordered": line.quantity,
                                "unit_price": line.unit_price or 0.0,
                            },
                        )
                        for line in order.line_ids
                    ],
                }
            )
            # the buyer's role is checked above; the link is written for them
            order.sudo().write({"purchase_order_id": po.id})
        return True


class FixImportOrderLineDetail(models.Model):
    _inherit = "fix.import.order.line"

    supplier_part_no = fields.Char(string="Supplier's Item Code")
    uom = fields.Char(string="Unit", default="Pcs")
