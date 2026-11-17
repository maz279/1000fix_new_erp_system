# The commercial document line standard (17 Nov 2026).
#
# The estimate, the quotation, the customer (local) proforma and the AR tax
# invoice used four different line shapes: the invoice line had no quantity,
# unit price, unit, discount, type or item code at all, and the estimate knew
# three line types. A 1000 FiX document mixes stocked items with charges -
# spare parts, components and finished products next to service, labour,
# support, diagnostic, call-out, transport and installation charges - so every
# document line now shares one standard:
#
#   SL | type | item code | description (+ serial / IMEI) | qty | unit |
#   unit price | discount | amount (excl. VAT) | VAT | total
#
# Two kinds of line, one rule each:
#   * STOCK lines (part, accessory, finished goods) are inventory items - a
#     storable product.product whose part number (default_code) is the code.
#   * CHARGE lines (service, labour, support, transport ...) never touch
#     inventory: their code is a fix.charge.code, a non-stock (service)
#     product. A charge line typed with no code takes the generic code of
#     its type, so no line on a document is ever without a code.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

STOCK_LINE_TYPES = ("part", "accessory", "goods")

LINE_TYPES = [
    # stock (inventory) lines
    ("part", "Spare Part / Component"),
    ("accessory", "Accessory"),
    ("goods", "Finished Product / Goods"),
    # charge (non-stock) lines
    ("service", "Service Charge"),
    ("labour", "Labour"),
    ("support", "Support Charge"),
    ("diagnostic", "Diagnostic / Inspection"),
    ("callout", "Call-out / Visit"),
    ("transport", "Transport / Delivery"),
    ("installation", "Installation / Commissioning"),
    ("recurring", "AMC / Recurring Service"),
    ("subscription", "Subscription Plan"),
    ("rental", "Rental"),
    ("subcontract", "Third-Party / Subcontract"),
    ("warranty_ext", "Warranty Extension"),
    ("fee", "Fee / Other Charge"),
]
LINE_TYPE_LABELS = dict(LINE_TYPES)
CHARGE_LINE_TYPES = tuple(k for k, _label in LINE_TYPES if k not in STOCK_LINE_TYPES)

# The generic charge code of each charge type (data/fix_charge_code_data.xml).
GENERIC_CHARGE_XMLID = {t: "cd_catalogue.charge_code_%s" % t for t in CHARGE_LINE_TYPES}

# Catalogue item type -> stock line type, for a picked inventory item.
ITEM_TYPE_LINE = {"accessory": "accessory", "finished_good": "goods"}


def line_kind(line_type):
    """'stock' or 'charge' for a line type (empty = charge)."""
    return "stock" if line_type in STOCK_LINE_TYPES else "charge"


class FixChargeCode(models.Model):
    """A non-stock charge code: service, labour, support, transport, fees.

    Each code owns a service-type product.product (never storable), so the
    estimate, quotation, proforma and invoice lines reference charges the same
    way they reference parts, the M11 rate card prices them by code, and M51
    determines their VAT by code - with no stock movement, ever."""

    _name = "fix.charge.code"
    _description = "Service & Charge Code"
    _inherit = ["mail.thread"]
    _order = "charge_type, code"
    _rec_name = "name"
    _code_unique = models.Constraint("UNIQUE (code)", "A charge code is unique.")

    code = fields.Char(required=True, tracking=True, help="Printed on every document line.")
    name = fields.Char(string="Charge Name", required=True, tracking=True, translate=False)
    name_bn = fields.Char(string="Charge Name (Bengali)")
    charge_type = fields.Selection(
        [(k, v) for k, v in LINE_TYPES if k in CHARGE_LINE_TYPES],
        required=True,
        default="service",
        tracking=True,
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Charged Per",
        help="Hour, visit, km, job, month... Empty: per unit (job).",
    )
    default_rate = fields.Monetary(
        string="Standard Rate (excl. VAT)",
        currency_field="currency_id",
        tracking=True,
        help="The price a line takes when no M11 rate card covers the code. Zero: the "
        "price is entered on each document line.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    description = fields.Text(help="What the charge covers; printed under the line if set.")
    is_generic = fields.Boolean(
        string="Generic Code",
        readonly=True,
        help="The fallback code of its charge type: a charge line typed without a code "
        "takes it.",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Non-stock Item",
        readonly=True,
        copy=False,
        ondelete="restrict",
        help="The service (non-inventory) item the documents reference.",
    )
    active = fields.Boolean(default=True)

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "[%s] %s" % (rec.code, rec.name) if rec.code else rec.name

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            code = (rec.code or "").strip()
            if not code or " " in code:
                raise ValidationError("A charge code is one word with no spaces, e.g. SVC-LAB-HR.")
            clash = (
                self.env["product.product"]
                .sudo()
                .with_context(active_test=False)
                .search(
                    [("default_code", "=", code), ("id", "!=", rec.product_id.id or 0)], limit=1
                )
            )
            if clash:
                raise ValidationError(
                    "Code %s already belongs to the item %s; a charge code may not reuse a part "
                    "number." % (code, clash.display_name)
                )

    @api.constrains("default_rate")
    def _check_rate(self):
        if any((r.default_rate or 0.0) < 0 for r in self):
            raise ValidationError("A standard rate cannot be negative.")

    def _product_vals(self):
        self.ensure_one()
        vals = {
            "name": self.name,
            "default_code": self.code.strip(),
            "type": "service",
            "sale_ok": True,
            "purchase_ok": False,
            "list_price": self.default_rate or 0.0,
            "active": self.active,
            "description_sale": self.description or False,
        }
        if self.uom_id:
            vals["uom_id"] = self.uom_id.id
        if "is_storable" in self.env["product.product"]._fields:
            vals["is_storable"] = False
        if "name_bn" in self.env["product.template"]._fields:
            vals["name_bn"] = self.name_bn or False
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        Product = self.env["product.product"].sudo()
        for rec in records:
            # the charge-code ACL is the gate: the item behind it is the
            # catalogue's to create, not the user's
            if rec.product_id:
                # an existing item adopted as this charge (see _adopt_items):
                # converted to non-stock, keeping its id, code and history
                rec.product_id.with_context(active_test=False).write(rec._product_vals())
            else:
                rec.sudo().product_id = Product.create(rec._product_vals())
        return records

    @api.model
    def _adopt_items(self, products, charge_type_of):
        """Turn items that were migrated as stocked parts but are services
        (e.g. the legacy "AC Installation-PC53867") into charge codes.

        The item keeps its record, part number and every reference; it
        becomes a non-stock service item behind a fix.charge.code. Refused
        for an item that holds stock or has stock moves: a physical item is
        never re-typed. `charge_type_of(product)` names the charge type.
        Returns the charge codes (one per item; an adopted item is skipped)."""
        Product = self.env["product.product"].sudo().with_context(active_test=False)
        Quant = self.env.get("stock.quant")
        Move = self.env.get("stock.move")
        codes = self.browse()
        for product in Product.browse(products.ids):
            if product.fix_charge_code_id:
                codes |= product.fix_charge_code_id[:1]
                continue
            if Quant is not None and Quant.sudo().search_count(
                [("product_id", "=", product.id), ("quantity", "!=", 0)]
            ):
                raise UserError("%s holds stock: it is not re-typed." % product.display_name)
            if Move is not None and Move.sudo().search_count([("product_id", "=", product.id)]):
                raise UserError("%s has stock moves: it is not re-typed." % product.display_name)
            code = (product.default_code or "").strip().replace(" ", "-") or "CHG-%s" % product.id
            codes |= self.sudo().create(
                {
                    "code": code,
                    "name": product.name,
                    "name_bn": getattr(product, "name_bn", False) or False,
                    "charge_type": charge_type_of(product),
                    "default_rate": product.lst_price
                    if product.lst_price and product.lst_price > 1.0
                    else 0.0,
                    "product_id": product.id,
                    "description": "Converted from a stocked item (legacy migration) on %s."
                    % fields.Date.context_today(self),
                }
            )
            item = product.product_tmpl_id.catalogue_item_id[:1].sudo()
            if item and "item_type" in item._fields:
                new_type = "inspection" if charge_type_of(product) == "diagnostic" else "service"
                writer = item._guarded() if hasattr(item, "_guarded") else item
                try:
                    with self.env.cr.savepoint():
                        writer.write({"item_type": new_type})
                except (UserError, ValidationError):
                    # the catalogue's own governance keeps its type; the
                    # charge code still rules the document lines
                    pass
        return codes

    def write(self, vals):
        res = super().write(vals)
        if {"code", "name", "name_bn", "default_rate", "uom_id", "active", "description"} & set(
            vals
        ):
            for rec in self.filtered("product_id"):
                rec.product_id.sudo().with_context(active_test=False).write(rec._product_vals())
        return res

    def unlink(self):
        if self.filtered("is_generic"):
            raise UserError("A generic charge code is kept; archive a specific one instead.")
        products = self.mapped("product_id")
        res = super().unlink()
        products.sudo().write({"active": False})
        return res

    @api.model
    def _generic_product(self, line_type):
        """The non-stock item of the generic code of a charge type (or empty)."""
        xmlid = GENERIC_CHARGE_XMLID.get(line_type)
        code = self.env.ref(xmlid, raise_if_not_found=False) if xmlid else None
        return code.sudo().product_id if code else self.env["product.product"]


class ProductProductCommercial(models.Model):
    _inherit = "product.product"

    fix_charge_code_id = fields.One2many(
        "fix.charge.code", "product_id", string="Charge Code (non-stock)"
    )

    def _fix_is_stock_item(self):
        """True for an inventory item (spare part, component, finished good)."""
        self.ensure_one()
        if "is_storable" in self._fields:
            return bool(self.is_storable)
        return self.type == "product"

    def _fix_line_type_for(self):
        """The document line type an item implies."""
        self.ensure_one()
        charge = self.sudo().fix_charge_code_id[:1]
        if charge:
            return charge.charge_type
        if self._fix_is_stock_item():
            item = self.sudo().product_tmpl_id.catalogue_item_id[:1]
            return ITEM_TYPE_LINE.get(item.item_type if item else "", "part")
        return "service"


class FixCommercialLineMixin(models.AbstractModel):
    """The shared document line: item code, kind, unit, serial / IMEI and the
    stock-or-charge rule. Estimate, quotation, proforma and invoice lines
    inherit it; each keeps its own amount logic."""

    _name = "fix.commercial.line.mixin"
    _description = "Commercial Document Line Standard"

    # Each document line model declares its own line_type / product_id /
    # description (defaults and labels differ); these are the shared shape.
    line_type = fields.Selection(LINE_TYPES, string="Type", default="service")
    product_id = fields.Many2one("product.product", string="Item / Charge Code")
    description = fields.Char()
    item_code = fields.Char(
        string="Item Code",
        compute="_compute_item_code",
        store=True,
        help="Part number of a stocked item, or the charge code of a service / charge.",
    )
    line_kind = fields.Selection(
        [("stock", "Inventory item"), ("charge", "Service / charge")],
        string="Kind",
        compute="_compute_line_kind",
        store=True,
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit",
        compute="_compute_uom_id",
        store=True,
        readonly=False,
        precompute=True,
    )
    serial_ref = fields.Char(
        string="Serial / IMEI",
        help="Serial number or IMEI of the item sold or serviced; printed under the line.",
    )

    @api.depends("product_id", "product_id.default_code")
    def _compute_item_code(self):
        for line in self:
            line.item_code = line.product_id.default_code or False

    @api.depends("line_type")
    def _compute_line_kind(self):
        for line in self:
            line.line_kind = line_kind(line.line_type)

    @api.depends("product_id")
    def _compute_uom_id(self):
        for line in self:
            if line.product_id and (not line.uom_id or line._origin.product_id != line.product_id):
                line.uom_id = line.product_id.uom_id
            elif not line.product_id and not line.uom_id:
                line.uom_id = False

    def _fix_is_display_line(self):
        self.ensure_one()
        return bool("display_type" in self._fields and self.display_type)

    @api.model
    def _fix_commercial_prepare(self, vals):
        """Fill a new line's type from its item, and give a charge line typed
        without an item its type's generic code: every line carries a code."""
        if vals.get("display_type"):
            return vals
        Product = self.env["product.product"]
        product = (
            Product.browse(vals.get("product_id")).exists() if vals.get("product_id") else Product
        )
        if product and not vals.get("line_type"):
            vals["line_type"] = product._fix_line_type_for()
        line_type = vals.get("line_type") or self._fields["line_type"].default(self)
        if not product and line_kind(line_type) == "charge":
            generic = self.env["fix.charge.code"]._generic_product(line_type)
            if generic:
                vals["product_id"] = generic.id
        return vals

    @api.constrains("product_id", "line_type")
    def _check_commercial_item_kind(self):
        """A stock line names an inventory item, never a non-stock charge; a
        charge line never names a stocked item.

        Odoo 19 runs constraints as superuser (_validate_fields sudo()s the
        records), so an `if self.env.su: return` guard here would switch the
        check off for everyone - it always runs."""
        for line in self:
            if line._fix_is_display_line() or not line.product_id:
                continue
            product = line.product_id.sudo()
            stock_item = product._fix_is_stock_item()
            label = LINE_TYPE_LABELS.get(line.line_type, line.line_type)
            if line.line_kind == "stock" and product.type == "service":
                raise ValidationError(
                    "%s is a %s line: pick an inventory item by its part number, not the "
                    "non-stock charge %s." % (label, label.lower(), line.product_id.display_name)
                )
            if line.line_kind == "charge" and stock_item:
                raise ValidationError(
                    "%s is an inventory item (part number %s); a %s line takes a service / "
                    "charge code. Change the line type to Spare Part, Accessory or Finished "
                    "Product, or pick a charge code."
                    % (line.product_id.display_name, line.product_id.default_code or "-", label)
                )

    def _fix_print_description(self):
        """Description as printed: the text, then serial / IMEI."""
        self.ensure_one()
        text = self.description or self.product_id.name or ""
        if self.serial_ref:
            text = "%s\nS/N: %s" % (text, self.serial_ref)
        return text


# ---------------------------------------------------------------------------
# The document header standard: who the customer is and what each kind of
# customer must state. One list for the estimate, quotation, proforma and
# invoice (the quotation's commercial `segment` stays its pricing playbook).
CUSTOMER_CATEGORIES = [
    ("individual", "Individual Consumer"),
    ("walk_in", "Walk-in Customer"),
    ("cash", "Cash Customer"),
    ("corporate", "Corporate (B2B)"),
    ("dealer", "Dealer / Partner"),
    ("government", "Government / Tender"),
]
CATEGORY_LABELS = dict(CUSTOMER_CATEGORIES)
# Categories that pay at the point of sale: the document is due on its date.
PAY_NOW_CATEGORIES = ("walk_in", "cash")
# Categories whose documents state the buyer's BIN (Mushak 6.3 buyer block).
BIN_CATEGORIES = ("corporate", "dealer", "government")
WALK_IN_PARTNER_XMLID = "cd_billing_engine.partner_walk_in"


class FixCommercialDocumentMixin(models.AbstractModel):
    """Header fields every customer document captures and prints.

    A concrete document names its customer with `_fix_doc_partner()`; the
    category follows the customer's party class (walk-in for the shared
    walk-in party) until a user picks another, e.g. Cash Customer."""

    _name = "fix.commercial.document.mixin"
    _description = "Commercial Document Header Standard"

    customer_category = fields.Selection(
        CUSTOMER_CATEGORIES,
        string="Customer Category",
        compute="_compute_customer_category",
        store=True,
        readonly=False,
        precompute=True,
        help="Individual, walk-in, cash, corporate, dealer or government: decides what "
        "the document must state (walk-in name and phone, buyer BIN, PO) and whether it "
        "is due at once.",
    )
    bill_to_name = fields.Char(
        string="Bill-to Name",
        help="Printed as the customer. Walk-in: the person's name as given at the counter.",
    )
    bill_to_phone = fields.Char(string="Bill-to Phone")
    bill_to_address = fields.Text(string="Bill-to Address")
    customer_bin = fields.Char(
        string="Buyer BIN / e-TIN",
        help="The buyer's VAT registration (BIN) printed on the Mushak 6.3; defaults "
        "from the customer.",
    )
    customer_po_ref = fields.Char(string="Customer PO / Ref No.")
    customer_po_date = fields.Date(string="Customer PO Date")
    salesperson_id = fields.Many2one(
        "res.users", string="Sales Person", default=lambda self: self.env.user
    )
    delivery_address = fields.Text(
        string="Delivery / Service Address",
        help="Where the goods go or the work is done (Mushak 6.3: final destination).",
    )
    vehicle_no = fields.Char(
        string="Vehicle No.", help="Vehicle type and number carrying the goods (Mushak 6.3)."
    )
    challan_ref = fields.Char(string="Delivery Challan No.")
    service_item = fields.Char(
        string="Service Item",
        help="The customer's device or equipment the document is for (brand, model, serial).",
    )
    remarks = fields.Text(string="Remarks")

    # ---- hooks a document implements ------------------------------------
    def _fix_doc_partner(self):
        """The customer res.partner of the document (may be empty)."""
        return self.env["res.partner"]

    def _fix_doc_lines(self):
        """The priced lines, in print order (no sections / notes)."""
        return self.env["fix.commercial.line.mixin"]

    # ---- category -------------------------------------------------------
    @api.model
    def _fix_walk_in_partner(self):
        return (
            self.env.ref(WALK_IN_PARTNER_XMLID, raise_if_not_found=False) or self.env["res.partner"]
        )

    @api.model
    def _fix_category_for_partner(self, partner):
        if not partner:
            return "walk_in"
        if partner == self._fix_walk_in_partner():
            return "walk_in"
        cls = partner.commercial_partner_id.party_class if "party_class" in partner._fields else ""
        if cls in ("corporate", "dealer", "government"):
            return cls
        if partner.commercial_partner_id.is_company:
            return "corporate"
        return "individual"

    def _compute_customer_category(self):
        """Follows the customer; documents add @api.depends on their customer
        field. A category the user picks (e.g. Cash Customer) stays until the
        customer changes."""
        for doc in self:
            doc.customer_category = doc._fix_category_for_partner(doc._fix_doc_partner())

    # ---- what each category must state ----------------------------------
    def _fix_doc_problems(self):
        """What the document still lacks for its customer category."""
        self.ensure_one()
        problems = []
        partner = self._fix_doc_partner()
        cat = self.customer_category
        if cat == "walk_in" and not (self.bill_to_name or "").strip():
            problems.append("A walk-in document names the customer (bill-to name).")
        if cat == "walk_in" and not (self.bill_to_phone or (partner and partner.phone)):
            problems.append("A walk-in document records the customer's phone number.")
        if cat in BIN_CATEGORIES and not (self.customer_bin or (partner and partner.vat)):
            problems.append(
                "A %s document states the buyer's BIN / e-TIN." % CATEGORY_LABELS[cat].lower()
            )
        if cat in ("corporate", "government") and not self._fix_doc_lines():
            problems.append("List what is supplied: add at least one line.")
        return problems

    # ---- print helpers ----------------------------------------------------
    def _fix_doc_party(self):
        """{name, address, phone, email, bin} printed in the Bill To block."""
        self.ensure_one()
        partner = self._fix_doc_partner()
        walk_in = partner and partner == self._fix_walk_in_partner()
        if partner and not walk_in:
            address = ", ".join(
                p
                for p in (
                    partner.street,
                    partner.street2,
                    partner.city,
                    partner.zip,
                    partner.country_id.name if partner.country_id else "",
                )
                if p
            )
        else:
            address = ""
        code = ""
        if partner and not walk_in:
            code = getattr(partner, "legacy_reference", "") or partner.ref or ""
        return {
            "name": (self.bill_to_name or "").strip()
            or (partner.name if partner and not walk_in else "")
            or "Walk-in Customer",
            "code": code,
            "address": (self.bill_to_address or "").strip() or address,
            "phone": (self.bill_to_phone or "").strip()
            or (partner.phone if partner and not walk_in else "")
            or "",
            "email": partner.email if partner and not walk_in else "",
            "bin": (self.customer_bin or "").strip()
            or (partner.vat if partner and not walk_in else "")
            or "",
            "category": CATEGORY_LABELS.get(self.customer_category or "", ""),
        }

    def _fix_doc_totals(self):
        """The document footer: item count, quantity, gross, discount, taxable,
        VAT, grand total (documents override the money figures they own)."""
        self.ensure_one()
        lines = self._fix_doc_lines()
        gross = sum(
            (ln.gross_amount if "gross_amount" in ln._fields else ln.quantity * ln.unit_price)
            for ln in lines
        )
        disc = sum(ln.discount_amount for ln in lines) if "discount_amount" in lines._fields else 0
        return {
            "items": len(lines),
            "quantity": sum(lines.mapped("quantity")),
            "gross": round(gross, 2),
            "discount": round(disc, 2),
        }
