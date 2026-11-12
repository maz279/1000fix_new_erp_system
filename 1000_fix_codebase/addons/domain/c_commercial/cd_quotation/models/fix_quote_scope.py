# M36 quotation scope and commercial terms (quote-to-cash review P1,
# 12 Nov 2026).
#
# The quotation said nothing about WHAT it quoted: one `value`, plus a link
# to an M01 repair estimate that only a consumer repair has. A corporate,
# AMC or goods quote could not list its contents, and the contract it
# became had no scope. A quotation now carries its own lines (sections,
# notes, optional lines), its value is the sum of its lines less a header
# discount (nobody types it), each line is priced from the M11 rate card or
# the catalogue list price, and a discount below that price raises the
# approval tier by the one discount ladder (D3-03). The quotation also
# states its commercial terms: payment term, the payment methods offered,
# an advance, delivery and warranty terms, and the customer's PO.
#
# Lines change only while the quotation is a draft or approved; a change to
# any line moves the quotation's scope digest, a term the approval covered,
# so an approved quotation goes back for approval. An issued version is
# immutable (revise it).
import hashlib
import json

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_quotation import SPEC_DISCOUNT_LADDER

LINE_TYPES = [
    ("part", "Part / Material"),
    ("goods", "Goods (sale & delivery)"),
    ("labour", "Labour"),
    ("service", "Fixed-Price Service"),
    ("diagnostic", "Diagnostic / Inspection"),
    ("callout", "Call-out / Travel / Transport"),
    ("installation", "Installation / Commissioning"),
    ("recurring", "AMC / Recurring Service"),
    ("subscription", "Subscription Plan"),
    ("rental", "Rental"),
    ("subcontract", "Third-Party / Subcontract"),
    ("warranty_ext", "Warranty Extension"),
    ("fee", "Fee"),
]

PRICE_SOURCES = [
    ("rate_card", "M11 rate card"),
    ("list", "Catalogue list price"),
    ("estimate", "M01 estimate"),
    ("manual", "Entered"),
]

EDITABLE_STATES = ("draft", "approved")

# Context key set only by the estimate pull, so its lines record their source.
FROM_ESTIMATE = "fix_quote_from_estimate"


class FixQuotationLine(models.Model):
    _name = "fix.quotation.line"
    _description = "Quotation Line"
    _order = "quotation_id, sequence, id"

    quotation_id = fields.Many2one("fix.quotation", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="quotation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="quotation_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="quotation_id.currency_id")
    sequence = fields.Integer(default=10)
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        help="A section heading or a note: no price, not in the total.",
    )
    line_type = fields.Selection(LINE_TYPES, string="Type", default="service")
    product_id = fields.Many2one("product.product", string="Item / Service")
    description = fields.Char(required=True)
    quantity = fields.Float(default=1.0, digits="Product Unit of Measure")
    unit_price = fields.Monetary(currency_field="currency_id")
    discount_pct = fields.Float(string="Discount (%)")
    subtotal = fields.Monetary(
        string="Amount (excl. VAT)",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
    )
    list_price = fields.Monetary(
        string="List / Rate Price",
        currency_field="currency_id",
        readonly=True,
        help="The M11 rate card or catalogue price when the line was priced; a lower "
        "price is a discount the approval tier covers.",
    )
    list_subtotal = fields.Monetary(
        currency_field="currency_id", compute="_compute_amounts", store=True
    )
    price_source = fields.Selection(PRICE_SOURCES, readonly=True)
    cost_unit = fields.Monetary(string="Unit Cost", currency_field="currency_id")
    is_optional = fields.Boolean(
        string="Optional",
        help="Offered as an option: shown to the customer, not in the total. To take it, "
        "revise the quotation with the line made firm.",
    )

    @api.depends("quantity", "unit_price", "discount_pct", "list_price", "display_type")
    def _compute_amounts(self):
        for line in self:
            if line.display_type:
                line.subtotal = line.list_subtotal = 0.0
                continue
            qty = line.quantity or 0.0
            price = line.unit_price or 0.0
            line.subtotal = round(qty * price * (1.0 - (line.discount_pct or 0.0) / 100.0), 2)
            # A price above the list is not a negative discount on another line.
            line.list_subtotal = round(qty * max(line.list_price or 0.0, price), 2)

    @api.constrains("quantity", "unit_price", "discount_pct", "cost_unit")
    def _check_numbers(self):
        for line in self.filtered(lambda r: not r.display_type):
            if (line.quantity or 0.0) < 0 or (line.unit_price or 0.0) < 0:
                raise ValidationError(
                    "Quotation line '%s' cannot have a negative quantity or price; give a "
                    "discount instead, which the approval tier covers." % line.description
                )
            if not 0.0 <= (line.discount_pct or 0.0) <= 100.0:
                raise ValidationError("A line discount is between 0 and 100%.")
            if (line.cost_unit or 0.0) < 0:
                raise ValidationError("A unit cost cannot be negative.")

    # ---- pricing -----------------------------------------------------------
    def _resolve_price(self, product):
        """(price, source) for a product: the released M11 rate card for its
        code, else its catalogue list price. None when there is no product."""
        if not product:
            return None, "manual"
        Card = self.env.get("fix.rate.card")
        if Card is not None and product.default_code:
            card = Card._resolve(product.default_code)
            if card:
                return card.unit_price, "rate_card"
        return product.lst_price, "list"

    def _priced_vals(self, vals, product):
        """Price a line: an empty price takes the resolved one; a typed price
        (zero included) is kept, and marked as entered when it differs."""
        price, source = self._resolve_price(product)
        typed = vals.get("unit_price")
        blank = typed is None or typed is False or typed == ""
        if blank and price is not None:
            vals["unit_price"] = price
            vals["price_source"] = source
        elif self.env.context.get(FROM_ESTIMATE):
            vals["price_source"] = "estimate"
        elif price is not None and not blank and abs(float(typed) - price) <= 0.005:
            vals["price_source"] = source
        else:
            vals["price_source"] = "manual"
        unit = vals.get("unit_price") or 0.0
        vals["list_price"] = price if price is not None else unit
        return vals

    # ---- guards ------------------------------------------------------------
    @api.model
    def _assert_editable(self, quotations):
        frozen = quotations.filtered(lambda q: q.state not in EDITABLE_STATES)
        if frozen:
            raise UserError(
                "Quotation %s is %s: its lines are frozen (BRU-QTE-02). Revise it to make a "
                "new version." % (frozen[0].name, frozen[0].state)
            )

    def _check_sellable(self):
        """The one selling check (product._fix_check_sale: catalogue lifecycle
        and the M11 floor) on every priced line, as the acting user."""
        if self.env.su:
            return
        for line in self.filtered(lambda r: r.product_id and not r.display_type):
            product = line.product_id
            if hasattr(product, "_fix_check_sale"):
                product._fix_check_sale(unit_price=line.unit_price or 0.0, channel="quotation")

    @api.model_create_multi
    def create(self, vals_list):
        Quote = self.env["fix.quotation"]
        self._assert_editable(Quote.browse({v.get("quotation_id") for v in vals_list} - {None}))
        Product = self.env["product.product"]
        for vals in vals_list:
            vals.pop("list_price", None)
            vals.pop("price_source", None)
            if vals.get("display_type"):
                vals.update({"quantity": 0.0, "unit_price": 0.0, "discount_pct": 0.0})
                continue
            product = Product.browse(vals.get("product_id")).exists()
            if product and not vals.get("description"):
                vals["description"] = product.display_name
            self._priced_vals(vals, product)
        lines = super().create(vals_list)
        lines._check_sellable()
        lines.quotation_id._sync_from_lines()
        return lines

    def write(self, vals):
        self._assert_editable(self.quotation_id)
        if not self.env.su:
            vals.pop("list_price", None)
            vals.pop("price_source", None)
        if "quotation_id" in vals and any(
            line.quotation_id.id != vals["quotation_id"] for line in self
        ):
            raise UserError("A quotation line never moves to another quotation.")
        before = self.quotation_id
        if "product_id" in vals or "unit_price" in vals:
            for line in self:
                line_vals = dict(vals)
                product = (
                    self.env["product.product"].browse(vals["product_id"]).exists()
                    if "product_id" in vals
                    else line.product_id
                )
                if "product_id" in vals and "unit_price" not in vals:
                    line_vals["unit_price"] = False
                line._priced_vals(line_vals, product)
                super(FixQuotationLine, line).write(line_vals)
        else:
            super().write(vals)
        self._check_sellable()
        (before | self.quotation_id)._sync_from_lines()
        return True

    def unlink(self):
        quotations = self.quotation_id
        self._assert_editable(quotations)
        res = super().unlink()
        quotations.exists()._sync_from_lines()
        return res


class FixQuotationScope(models.Model):
    _inherit = "fix.quotation"

    line_ids = fields.One2many(
        "fix.quotation.line", "quotation_id", string="Quoted Lines", copy=True
    )
    discount_amount = fields.Monetary(
        string="Overall Discount (BDT)",
        currency_field="currency_id",
        help="A discount on the whole quotation, before VAT.",
    )
    lines_total = fields.Monetary(
        string="Lines Total (excl. VAT)",
        currency_field="currency_id",
        compute="_compute_scope_totals",
        store=True,
    )
    list_total = fields.Monetary(
        string="At List / Rate Prices",
        currency_field="currency_id",
        compute="_compute_scope_totals",
        store=True,
    )
    discount_pct = fields.Float(
        string="Discount off List (%)",
        compute="_compute_scope_totals",
        store=True,
        help="How far the quoted value is below the rate card / list prices; the discount "
        "ladder may raise the approval tier.",
    )
    scope_digest = fields.Char(
        readonly=True,
        copy=False,
        help="Fingerprint of the lines and overall discount the approval covered.",
    )
    # ---- commercial terms -------------------------------------------------
    payment_term_id = fields.Many2one("account.payment.term", string="Payment Terms")
    payment_method_ids = fields.Many2many(
        "fix.payment.method",
        "fix_quotation_payment_method_rel",
        "quotation_id",
        "method_id",
        string="Payment Methods Accepted",
        default=lambda self: self._default_payment_methods(),
    )
    advance_pct = fields.Float(string="Advance Required (%)")
    advance_amount = fields.Monetary(
        string="Advance Required (BDT)",
        currency_field="currency_id",
        compute="_compute_advance",
        store=True,
    )
    delivery_terms = fields.Text(help="Delivery / completion period, place, installation.")
    warranty_terms = fields.Text()
    customer_po_ref = fields.Char(string="Customer PO No.")
    customer_po_date = fields.Date(string="Customer PO Date")

    @api.model
    def _default_payment_methods(self):
        Method = self.env.get("fix.payment.method")
        return [(6, 0, Method.search([]).ids)] if Method is not None else False

    @api.depends(
        "line_ids.subtotal",
        "line_ids.list_subtotal",
        "line_ids.is_optional",
        "line_ids.display_type",
        "value",
    )
    def _compute_scope_totals(self):
        for rec in self:
            priced = rec._scope_lines()
            rec.lines_total = round(sum(priced.mapped("subtotal")), 2)
            rec.list_total = round(sum(priced.mapped("list_subtotal")), 2)
            value = rec.value or 0.0
            if priced and rec.list_total > 0.0 and value < rec.list_total:
                rec.discount_pct = round((rec.list_total - value) / rec.list_total * 100.0, 2)
            else:
                rec.discount_pct = 0.0

    @api.depends("advance_pct", "amount_total")
    def _compute_advance(self):
        for rec in self:
            rec.advance_amount = round(
                (rec.amount_total or 0.0) * (rec.advance_pct or 0.0) / 100, 2
            )

    @api.constrains("advance_pct", "discount_amount")
    def _check_terms(self):
        for rec in self:
            if not 0.0 <= (rec.advance_pct or 0.0) <= 100.0:
                raise ValidationError("An advance is between 0 and 100% of the total.")
            if (rec.discount_amount or 0.0) < 0:
                raise ValidationError("An overall discount cannot be negative.")
            if rec._scope_lines() and (rec.discount_amount or 0.0) > rec.lines_total + 0.005:
                raise ValidationError(
                    "The overall discount (%.2f) cannot exceed the lines total (%.2f)."
                    % (rec.discount_amount, rec.lines_total)
                )

    @api.constrains("value", "line_ids", "discount_amount")
    def _check_value_is_the_lines(self):
        for rec in self:
            priced = rec._scope_lines()
            if not priced:
                continue
            expected = round(sum(priced.mapped("subtotal")) - (rec.discount_amount or 0.0), 2)
            if abs((rec.value or 0.0) - expected) > 0.005:
                raise ValidationError(
                    "Quotation %s quotes BDT %.2f but its lines come to BDT %.2f; the value "
                    "is the sum of the lines less the overall discount."
                    % (rec.name, rec.value or 0.0, expected)
                )

    # ---- lines -> value ----------------------------------------------------
    def _scope_lines(self):
        """The lines that make the price: not sections, notes or options."""
        self.ensure_one()
        return self.line_ids.filtered(lambda r: not r.display_type and not r.is_optional)

    def _scope_fingerprint(self) -> str:
        self.ensure_one()
        rows = [
            [
                line.sequence,
                line.display_type or "",
                line.line_type or "",
                line.product_id.id or 0,
                line.description or "",
                round(line.quantity or 0.0, 4),
                round(line.unit_price or 0.0, 2),
                round(line.discount_pct or 0.0, 4),
                bool(line.is_optional),
            ]
            for line in self.line_ids.sorted(lambda r: (r.sequence, r.id))
        ]
        payload = json.dumps(
            {"lines": rows, "discount": round(self.discount_amount or 0.0, 2)}, sort_keys=True
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def _sync_from_lines(self):
        """The value follows the lines; the digest records what was priced.
        Both are terms the approval covered, so a change after approval
        withdraws it."""
        for rec in self.exists():
            vals = {}
            digest = rec._scope_fingerprint()
            if digest != (rec.scope_digest or ""):
                vals["scope_digest"] = digest
            priced = rec._scope_lines()
            if priced:
                value = round(sum(priced.mapped("subtotal")) - (rec.discount_amount or 0.0), 2)
                if abs(value - (rec.value or 0.0)) > 0.005:
                    vals["value"] = value
            if vals:
                rec._guarded().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        # A typed value that is not the estimate's is refused by
        # _check_value_matches_estimate (A04 audit M36-11) before any pull.
        records = super().create(vals_list)
        for rec in records:
            if rec.estimate_id and not rec.line_ids:
                rec._pull_estimate_lines()
            else:
                rec._sync_from_lines()
        return records

    def write(self, vals):
        if "discount_amount" in vals and "value" not in vals:
            # the value follows in the same write, or the lines constraint
            # would see a new discount against the old value
            for rec in self:
                priced = rec._scope_lines()
                if priced:
                    value = round(
                        sum(priced.mapped("subtotal")) - (vals["discount_amount"] or 0.0), 2
                    )
                    super(FixQuotationScope, rec).write(dict(vals, value=value))
                else:
                    super(FixQuotationScope, rec).write(vals)
            self._sync_from_lines()
            return True
        res = super().write(vals)
        if "line_ids" in vals:
            self._sync_from_lines()
        return res

    # ---- the estimate as a source of lines ---------------------------------
    def _pull_estimate_lines(self):
        """Copy the M01 estimate's lines and discount: the quotation then
        prices exactly what the customer's estimate says."""
        self.ensure_one()
        est = self.estimate_id.sudo()
        if not est:
            raise UserError("Link the M01 estimate to pull its lines from.")
        Line = self.env["fix.quotation.line"].with_context(**{FROM_ESTIMATE: True})
        self.line_ids.unlink()
        Line.create(
            [
                {
                    "quotation_id": self.id,
                    "sequence": (i + 1) * 10,
                    "line_type": src.line_type,
                    "product_id": src.product_id.id or False,
                    "description": src.description,
                    "quantity": src.quantity,
                    "unit_price": src.unit_price,
                }
                for i, src in enumerate(est.line_ids.sorted(lambda r: r.id))
            ]
        )
        vals = {}
        if abs((self.discount_amount or 0.0) - (est.discount or 0.0)) > 0.005:
            vals["discount_amount"] = est.discount or 0.0
        if abs((self.vat_rate or 0.0) - (est.vat_rate or 0.0)) > 0.0001:
            vals["vat_rate"] = est.vat_rate
        if vals:
            self.write(vals)
        self._sync_from_lines()

    def action_pull_estimate_lines(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Lines are pulled into a draft quotation only.")
            rec._pull_estimate_lines()
        return True

    # ---- approval: the discount ladder can raise the tier ------------------
    def _discount_tier(self, pct):
        company = self.company_id[:1] or self.env.company
        Policy = self.env.get("fix.discount.policy")
        if Policy is not None and hasattr(Policy, "tier_for_discount"):
            return Policy.sudo().tier_for_discount(pct, company)
        for bound, tier in SPEC_DISCOUNT_LADDER:
            if pct <= bound:
                return tier
        return SPEC_DISCOUNT_LADDER[-1][1]

    def _dofa_current_tier(self) -> str:
        tier = super()._dofa_current_tier()
        pct = self.discount_pct or 0.0
        if pct > 0.0:
            by_discount = self._discount_tier(pct)
            if self._dofa_tier_rank(by_discount) > self._dofa_tier_rank(tier):
                tier = by_discount
        return tier

    @api.depends("value", "discount_pct")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    # ---- readiness, snapshot, form locks -----------------------------------
    def _readiness_problems(self) -> list:
        problems = super()._readiness_problems()
        if not self._scope_lines():
            problems.append(
                "List what is quoted: add at least one priced line (or pull the estimate's)."
            )
        if not self.payment_term_id:
            problems.append("State the payment terms.")
        if not self.payment_method_ids:
            problems.append("Offer at least one payment method.")
        for line in self.line_ids.filtered(lambda r: r.product_id and not r.display_type):
            product = line.product_id.with_env(self.env)
            if not hasattr(product, "_fix_check_sale"):
                break
            try:
                product._fix_check_sale(unit_price=line.unit_price or 0.0, channel="quotation")
            except (UserError, ValidationError) as exc:
                problems.append(
                    "%s: %s" % (line.product_id.display_name, exc.args[0] if exc.args else exc)
                )
        return problems

    def _snapshot(self) -> str:
        data = json.loads(super()._snapshot())
        data.update(
            {
                "scope": self._scope_fingerprint(),
                "payment_term_id": self.payment_term_id.id or False,
                "payment_methods": sorted(self.payment_method_ids.ids),
                "advance_pct": round(self.advance_pct or 0.0, 4),
                "delivery_terms": self.delivery_terms or "",
                "warranty_terms": self.warranty_terms or "",
            }
        )
        return json.dumps(data, sort_keys=True)

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(q.state not in EDITABLE_STATES for q in self):
            locked.add("line_ids")
        return locked
