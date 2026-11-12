# fix_import_proforma_detail — the import proforma as the supplier's actual
# document (user request, 12 Nov 2026).
#
# The proforma carried a number, a currency and one amount: no item lines, no
# copy of the supplier's PI, none of the terms the bank needs to open the LC.
# A Bangladeshi bank opens an LC on a PI that names each item with its HS code,
# quantity and price, the incoterm, the ports, the latest shipment date,
# partial shipment / transshipment and the beneficiary's bank. Now:
#   - the proforma has item lines (part, the supplier's item code, description,
#     HS code, quantity, unit, unit price, line total); left empty they are
#     copied from the import order, to be adjusted to the supplier's PI;
#   - freight, insurance and other charges sit beside the lines, and the PI
#     total must add up to lines + charges before it is approved;
#   - every line names a part of the order, and the PI never asks for more of
#     a part than the order does;
#   - the supplier's PI is attached, and the LC terms and beneficiary bank are
#     recorded; all of it is pinned once the proforma is decided;
#   - the proforma is in the order's currency (USD, EUR, CNY, …) or BDT.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

PAYMENT_TERMS = [
    ("lc_sight", "LC at sight"),
    ("lc_usance", "LC usance (deferred)"),
    ("tt_advance", "TT in advance"),
    ("cad", "Cash against documents"),
    ("open_account", "Open account"),
]

DETAIL_TERMS = (
    "payment_terms",
    "payment_terms_note",
    "port_of_loading",
    "port_of_discharge",
    "latest_shipment_date",
    "partial_shipment",
    "transshipment",
    "beneficiary_bank",
    "beneficiary_swift",
    "beneficiary_account",
    "freight_amount",
    "insurance_amount",
    "other_charges",
    "pi_file",
    "pi_filename",
    "line_ids",
)


class FixImportProformaDetail(models.Model):
    _inherit = "fix.import.proforma"

    _PINNED = (
        "order_id",
        "proforma_no",
        "currency_id",
        "amount",
        "issued_on",
        "valid_until",
        *DETAIL_TERMS,
    )

    # the order decides the currency; BDT stays allowed (a local-currency PI)
    currency_id = fields.Many2one(default=None)
    supplier_id = fields.Many2one(related="order_id.supplier_id", string="Supplier")
    incoterm = fields.Selection(related="order_id.incoterm", string="Incoterm")
    country_origin = fields.Many2one(related="order_id.country_origin", string="Country of Origin")
    payment_terms = fields.Selection(PAYMENT_TERMS, string="Payment Terms", default="lc_sight")
    payment_terms_note = fields.Char(string="Payment Terms (as on the PI)")
    port_of_loading = fields.Char(string="Port of Loading")
    port_of_discharge = fields.Char(string="Port of Discharge", default="Chattogram, Bangladesh")
    latest_shipment_date = fields.Date(string="Latest Shipment Date")
    partial_shipment = fields.Boolean(string="Partial Shipment Allowed", default=True)
    transshipment = fields.Boolean(string="Transshipment Allowed", default=True)
    beneficiary_bank = fields.Char(string="Beneficiary Bank")
    beneficiary_swift = fields.Char(string="Beneficiary Bank SWIFT")
    beneficiary_account = fields.Char(string="Beneficiary Account No")
    pi_file = fields.Binary(string="Supplier's PI (copy)", attachment=True, copy=False)
    pi_filename = fields.Char(string="PI File Name", copy=False)
    line_ids = fields.One2many(
        "fix.import.proforma.line", "proforma_id", string="PI Lines", copy=True
    )
    lines_total = fields.Monetary(
        string="Lines Total",
        currency_field="currency_id",
        compute="_compute_lines_total",
        store=True,
    )
    freight_amount = fields.Monetary(string="Freight", currency_field="currency_id")
    insurance_amount = fields.Monetary(string="Insurance", currency_field="currency_id")
    other_charges = fields.Monetary(string="Other Charges", currency_field="currency_id")
    computed_total = fields.Monetary(
        string="Lines + Charges",
        currency_field="currency_id",
        compute="_compute_lines_total",
        store=True,
    )

    @api.depends("line_ids.subtotal", "freight_amount", "insurance_amount", "other_charges")
    def _compute_lines_total(self):
        for rec in self:
            rec.lines_total = sum(rec.line_ids.mapped("subtotal"))
            rec.computed_total = (
                rec.lines_total
                + (rec.freight_amount or 0.0)
                + (rec.insurance_amount or 0.0)
                + (rec.other_charges or 0.0)
            )

    @api.constrains("currency_id", "order_id")
    def _check_proforma_currency(self):
        for rec in self.sudo():
            allowed = rec.order_id.currency_id | rec.env.ref("base.BDT")
            if rec.currency_id and rec.currency_id not in allowed:
                raise ValidationError(
                    "Proforma %s is in %s: record it in the order's currency %s or in BDT."
                    % (rec.proforma_no, rec.currency_id.name, rec.order_id.currency_id.name)
                )

    @api.constrains("latest_shipment_date", "issued_on")
    def _check_shipment_date(self):
        for rec in self:
            if (
                rec.latest_shipment_date
                and rec.issued_on
                and rec.latest_shipment_date < rec.issued_on
            ):
                raise ValidationError("The latest shipment date cannot precede the PI date.")

    @api.model_create_multi
    def create(self, vals_list):
        Order = self.env["fix.import.order"]
        for vals in vals_list:
            order = Order.browse(vals.get("order_id")).sudo() if vals.get("order_id") else Order
            if order and not vals.get("currency_id"):
                vals["currency_id"] = order.currency_id.id
            # no lines given: start from the order's, in its own currency
            if (
                order
                and not vals.get("line_ids")
                and vals.get("currency_id") == order.currency_id.id
            ):
                vals["line_ids"] = [
                    (
                        0,
                        0,
                        {
                            "order_line_id": line.id,
                            "part_id": line.part_id.id,
                            "description": line.description or line.part_id.name,
                            "hs_code": line.hs_id.hs_code or False,
                            "supplier_part_no": line.supplier_part_no or False,
                            "uom": line.uom or "Pcs",
                            "quantity": line.quantity,
                            "unit_price": line.unit_price,
                        },
                    )
                    for line in order.line_ids
                ]
                if "freight_amount" not in vals and order.incoterm in ("cfr", "cif", "ddp"):
                    vals["freight_amount"] = order.freight_cost or 0.0
                if "insurance_amount" not in vals and order.incoterm in ("cif", "ddp"):
                    vals["insurance_amount"] = order.insurance_cost or 0.0
        return super().create(vals_list)

    def _import_check_proforma_detail(self):
        """At approval: the PI adds up, names only the order's parts, never
        asks for more of a part than the order does, and has a valid shape."""
        super()._import_check_proforma_detail()
        for rec in self:
            label = "Proforma %s" % rec.proforma_no
            rec.order_id._import_check_po_issued("Approving %s" % label)
            if not rec.line_ids:
                raise UserError(
                    "%s has no item lines: enter the supplier's PI lines (or start from the "
                    "order's) before it is approved." % label
                )
            if abs((rec.amount or 0.0) - rec.computed_total) > 0.01:
                raise UserError(
                    "%s does not add up: its total %.2f %s, but lines %.2f + freight %.2f + "
                    "insurance %.2f + other charges %.2f = %.2f."
                    % (
                        label,
                        rec.amount or 0.0,
                        rec.currency_id.name,
                        rec.lines_total,
                        rec.freight_amount or 0.0,
                        rec.insurance_amount or 0.0,
                        rec.other_charges or 0.0,
                        rec.computed_total,
                    )
                )
            order = rec.order_id.sudo()
            ordered = {}
            for line in order.line_ids:
                ordered[line.part_id.id] = ordered.get(line.part_id.id, 0.0) + line.quantity
            asked = {}
            for line in rec.line_ids:
                if line.part_id.id not in ordered:
                    raise UserError(
                        "%s lists %s, which is not on import order %s."
                        % (label, line.part_id.display_name, order.name)
                    )
                asked[line.part_id.id] = asked.get(line.part_id.id, 0.0) + line.quantity
            for part_id, qty in asked.items():
                if qty > ordered[part_id] + 1e-6:
                    part = rec.env["fix.spare.part"].sudo().browse(part_id)
                    raise UserError(
                        "%s asks for %g of %s; import order %s orders %g."
                        % (label, qty, part.display_name, order.name, ordered[part_id])
                    )
        return True


class FixImportProformaLine(models.Model):
    """One item of the supplier's proforma invoice."""

    _name = "fix.import.proforma.line"
    _description = "Import Proforma Line"
    _order = "proforma_id, sequence, id"

    proforma_id = fields.Many2one(
        "fix.import.proforma", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(related="proforma_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="proforma_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="proforma_id.currency_id")
    order_line_id = fields.Many2one(
        "fix.import.order.line", string="Order Line", ondelete="set null", copy=False
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    supplier_part_no = fields.Char(string="Supplier's Item Code")
    description = fields.Char(required=True)
    hs_code = fields.Char(string="HS Code (as on the PI)")
    quantity = fields.Float(required=True, default=1.0)
    uom = fields.Char(string="Unit", default="Pcs")
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id", required=True)
    subtotal = fields.Monetary(
        string="Line Total", currency_field="currency_id", compute="_compute_subtotal", store=True
    )

    _qty_positive = models.Constraint(
        "CHECK (quantity > 0)", "A proforma line needs a positive quantity"
    )
    _price_non_negative = models.Constraint(
        "CHECK (unit_price >= 0)", "A unit price cannot be negative"
    )

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (line.quantity or 0.0) * (line.unit_price or 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        Part = self.env["fix.spare.part"]
        for vals in vals_list:
            if not vals.get("description") and vals.get("part_id"):
                vals["description"] = Part.browse(vals["part_id"]).sudo().name
        records = super().create(vals_list)
        records._refuse_on_decided("added")
        return records

    def write(self, vals):
        self._refuse_on_decided("changed")
        return super().write(vals)

    def unlink(self):
        self._refuse_on_decided("removed")
        return super().unlink()

    def _refuse_on_decided(self, what):
        for line in self.sudo():
            if line.proforma_id.state in ("approved", "rejected"):
                raise UserError(
                    "Proforma %s is decided: its lines cannot be %s. Record a new proforma."
                    % (line.proforma_id.proforma_no, what)
                )
