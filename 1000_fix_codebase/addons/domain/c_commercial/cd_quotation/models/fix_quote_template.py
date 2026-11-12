# M36 quote-to-cash P3 (13 Nov 2026): the customer's choice and the starting
# point of a quotation.
#
# - Good / better / best: lines that share an option group are alternatives
#   (e.g. OEM, compatible or refurbished part). The quotation shows them all;
#   exactly one per group is chosen and only the chosen one is priced. The
#   approval covers the dearest choice, so the customer may switch between
#   the approved options without a new approval, up to acceptance.
# - Templates per segment (walk-in repair, corporate AMC, goods & works,
#   government tender): the lines, options and commercial terms a new
#   quotation starts from.
# - The document language: the PDF prints in English or Bangla.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_quote_scope import LINE_TYPES, FixQuotationLine
from .fix_quote_supply import SEGMENTS

OPTION_CHOICE = "fix_quote_option_choice"


class FixQuotationLineOption(models.Model):
    _inherit = "fix.quotation.line"

    alternative_group = fields.Char(
        string="Option Group",
        help="Lines with the same group are alternatives (good / better / best): the "
        "customer takes one, and only the chosen one is priced.",
    )
    is_selected = fields.Boolean(string="Chosen", default=True)

    def write(self, vals):
        if self.env.context.get(OPTION_CHOICE) and set(vals) == {"is_selected"}:
            # The customer's choice between approved alternatives: allowed up to
            # acceptance, and it changes neither the scope nor the approval.
            quotes = self.quotation_id
            frozen = quotes.filtered(lambda q: q.state not in ("draft", "approved", "sent"))
            if frozen:
                raise UserError(
                    "Quotation %s is %s: its options are final." % (frozen[0].name, frozen[0].state)
                )
            res = super(FixQuotationLine, self).write(vals)
            quotes._sync_from_lines()
            return res
        return super().write(vals)


class FixQuotationOptions(models.Model):
    _inherit = "fix.quotation"

    template_id = fields.Many2one("fix.quotation.template", string="Started From Template")
    document_lang = fields.Selection(
        [("en_US", "English"), ("bn_BD", "বাংলা (Bangla)")],
        string="Document Language",
        default="en_US",
        help="The language the quotation PDF is printed in.",
    )
    has_options = fields.Boolean(compute="_compute_has_options")

    @api.depends("line_ids.alternative_group")
    def _compute_has_options(self):
        for rec in self:
            rec.has_options = any(rec.line_ids.mapped("alternative_group"))

    # ---- what is priced: the chosen alternative of each group -----------------
    def _scope_lines(self):
        self.ensure_one()
        return (
            super()._scope_lines().filtered(lambda ln: not ln.alternative_group or ln.is_selected)
        )

    @api.depends(
        "line_ids.subtotal",
        "line_ids.list_subtotal",
        "line_ids.is_optional",
        "line_ids.display_type",
        "line_ids.is_selected",
        "line_ids.alternative_group",
        "value",
    )
    def _compute_scope_totals(self):
        return super()._compute_scope_totals()

    def _option_groups(self):
        self.ensure_one()
        groups = {}
        for ln in self.line_ids.filtered(
            lambda r: r.alternative_group and not r.display_type and not r.is_optional
        ):
            groups.setdefault(ln.alternative_group.strip().lower(), self.env["fix.quotation.line"])
            groups[ln.alternative_group.strip().lower()] |= ln
        return groups

    def _value_ceiling(self) -> float:
        """The value at the dearest choice of every option group: what the
        approval covers."""
        self.ensure_one()
        groups = self._option_groups()
        firm = super()._scope_lines().filtered(lambda ln: not ln.alternative_group)
        total = sum(firm.mapped("subtotal")) + sum(
            max(lines.mapped("subtotal") or [0.0]) for lines in groups.values()
        )
        return round(total - (self.discount_amount or 0.0), 2)

    def _scope_fingerprint(self) -> str:
        import hashlib

        base = super()._scope_fingerprint()
        groups = "|".join(
            "%s:%s" % (ln.id, (ln.alternative_group or "").strip().lower())
            for ln in self.line_ids.sorted("id")
        )
        return hashlib.sha256(("%s#%s" % (base, groups)).encode()).hexdigest()

    def _snapshot(self) -> str:
        import json

        data = json.loads(super()._snapshot())
        if self._option_groups():
            # the choice between approved options is the customer's
            data["value"] = self._value_ceiling()
        return json.dumps(data, sort_keys=True)

    def _dofa_amount(self) -> float:
        self.ensure_one()
        if self._option_groups():
            return self._value_ceiling()
        return super()._dofa_amount()

    def _approval_pinned_fields(self) -> set:
        pinned = super()._approval_pinned_fields()
        if self and all(rec.line_ids for rec in self):
            # with lines the value follows them; the lines (scope digest) and
            # the overall discount are what the approval pins
            pinned = pinned - {"value"}
        return pinned

    def _readiness_problems(self) -> list:
        problems = super()._readiness_problems()
        groups = self._option_groups()
        if groups and self.estimate_id:
            problems.append(
                "A quotation of an M01 estimate prices the estimate; offer the options on the "
                "estimate's revision instead."
            )
        for key, lines in groups.items():
            chosen = lines.filtered("is_selected")
            if len(lines) < 2:
                problems.append("Option group '%s' has only one line: it is not a choice." % key)
            if len(chosen) != 1:
                problems.append(
                    "Option group '%s' must have exactly one chosen line (has %d)."
                    % (key, len(chosen))
                )
        return problems

    def _accept(self, method, ref):
        self.ensure_one()
        for key, lines in self._option_groups().items():
            if len(lines.filtered("is_selected")) != 1:
                raise UserError(
                    "Record which option the customer takes in group '%s' before acceptance." % key
                )
        return super()._accept(method, ref)

    def action_choose_option(self, choice=None):
        """The customer's choice: `choice` is the chosen line's description
        (or its id). Every other line of that option group is unchosen."""
        for rec in self:
            text = (str(choice or "")).strip()
            if not text:
                raise UserError("Name the option the customer chose.")
            candidates = rec.line_ids.filtered("alternative_group")
            line = candidates.filtered(lambda ln, t=text: str(ln.id) == t)
            if not line:
                wanted = text.lower()
                line = candidates.filtered(
                    lambda ln, t=wanted: (ln.description or "").strip().lower() == t
                )
            if len(line) != 1:
                raise UserError(
                    "No single option line is called '%s'. Options: %s"
                    % (text, ", ".join(candidates.mapped("description")) or "none")
                )
            group = (line.alternative_group or "").strip().lower()
            siblings = candidates.filtered(
                lambda ln, g=group: (ln.alternative_group or "").strip().lower() == g
            )
            ctx = {OPTION_CHOICE: True}
            (siblings - line).filtered("is_selected").with_context(**ctx).write(
                {"is_selected": False}
            )
            if not line.is_selected:
                line.with_context(**ctx).write({"is_selected": True})
            rec.message_post(
                body="Customer chose option '%s' (group %s)." % (line.description, group)
            )
        return True

    # ---- templates ------------------------------------------------------------
    def action_apply_template(self):
        for rec in self:
            tpl = rec.template_id
            if not tpl:
                raise UserError("Choose the template to start from.")
            if rec.state != "draft":
                raise UserError("A template is applied to a draft quotation only.")
            if rec.estimate_id:
                raise UserError(
                    "This quotation prices its M01 estimate; a template would replace it."
                )
            rec.line_ids.unlink()
            rec.billing_line_ids.unlink()
            vals = {
                "line_ids": [(0, 0, tl._quote_line_vals()) for tl in tpl.line_ids],
            }
            for name in ("payment_term_id", "picking_type_id"):
                if tpl[name]:
                    vals[name] = tpl[name].id
            if tpl.payment_method_ids:
                vals["payment_method_ids"] = [(6, 0, tpl.payment_method_ids.ids)]
            for name in ("advance_pct", "delivery_terms", "warranty_terms", "expected_vds_rate"):
                if tpl[name]:
                    vals[name] = tpl[name]
            if tpl.segment:
                vals["segment"] = tpl.segment
            if tpl.quote_type:
                vals["quote_type"] = tpl.quote_type
            if tpl.validity_days:
                vals["valid_until"] = fields.Date.context_today(rec) + timedelta(
                    days=tpl.validity_days
                )
            rec.write(vals)
            if tpl.billing_line_ids:
                self.env["fix.quotation.billing.line"].create(
                    [
                        {
                            "quotation_id": rec.id,
                            "sequence": b.sequence,
                            "kind": b.kind,
                            "pct": b.pct,
                            "due_days": b.due_days,
                            "note": b.note or False,
                        }
                        for b in tpl.billing_line_ids
                    ]
                )
        return True

    @api.model_create_multi
    def create(self, vals_list):
        Partner = self.env["res.partner"]
        for vals in vals_list:
            if "document_lang" not in vals:
                partner = Partner.browse(vals.get("customer_id")).exists()
                vals["document_lang"] = "bn_BD" if partner.lang == "bn_BD" else "en_US"
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list, strict=True):
            if vals.get("template_id") and not vals.get("line_ids") and not rec.estimate_id:
                rec.action_apply_template()
        return records


class FixQuotationTemplate(models.Model):
    _name = "fix.quotation.template"
    _description = "Quotation Template"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", index=True)
    segment = fields.Selection(SEGMENTS)
    quote_type = fields.Selection(
        lambda self: self.env["fix.quotation"]._fields["quote_type"].selection,
        string="Converts Into",
    )
    validity_days = fields.Integer(default=15)
    payment_term_id = fields.Many2one("account.payment.term", string="Payment Terms")
    payment_method_ids = fields.Many2many(
        "fix.payment.method",
        "fix_quotation_template_payment_method_rel",
        "template_id",
        "method_id",
        string="Payment Methods",
    )
    advance_pct = fields.Float(string="Advance Required (%)")
    expected_vds_rate = fields.Float(string="Expected VDS (%)")
    delivery_terms = fields.Text()
    warranty_terms = fields.Text()
    picking_type_id = fields.Many2one(
        "stock.picking.type", string="Deliver From", domain="[('code', '=', 'outgoing')]"
    )
    note = fields.Char(help="When to use this template.")
    line_ids = fields.One2many("fix.quotation.template.line", "template_id", copy=True)
    billing_line_ids = fields.One2many("fix.quotation.template.billing", "template_id", copy=True)

    @api.constrains("advance_pct", "validity_days", "billing_line_ids")
    def _check_template(self):
        for tpl in self:
            if not 0.0 <= (tpl.advance_pct or 0.0) <= 100.0:
                raise ValidationError("An advance is between 0 and 100%.")
            if (tpl.validity_days or 0) < 0:
                raise ValidationError("Validity days cannot be negative.")
            if tpl.billing_line_ids and abs(sum(tpl.billing_line_ids.mapped("pct")) - 100.0) > 0.01:
                raise ValidationError("A template's billing plan adds up to 100%.")


class FixQuotationTemplateLine(models.Model):
    _name = "fix.quotation.template.line"
    _description = "Quotation Template Line"
    _order = "template_id, sequence, id"

    template_id = fields.Many2one(
        "fix.quotation.template", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    display_type = fields.Selection([("line_section", "Section"), ("line_note", "Note")])
    line_type = fields.Selection(LINE_TYPES, string="Type", default="service")
    product_id = fields.Many2one("product.product", string="Item / Service")
    description = fields.Char(required=True, translate=True)
    quantity = fields.Float(default=1.0, digits="Product Unit of Measure")
    unit_price = fields.Float(
        help="Empty: the line takes the M11 rate card / catalogue price when applied."
    )
    discount_pct = fields.Float(string="Discount (%)")
    is_optional = fields.Boolean(string="Optional")
    alternative_group = fields.Char(string="Option Group")
    is_selected = fields.Boolean(string="Chosen", default=True)

    def _quote_line_vals(self):
        self.ensure_one()
        vals = {
            "sequence": self.sequence,
            "display_type": self.display_type or False,
            "line_type": self.line_type,
            "product_id": self.product_id.id or False,
            "description": self.description,
            "quantity": self.quantity,
            "discount_pct": self.discount_pct,
            "is_optional": self.is_optional,
            "alternative_group": self.alternative_group or False,
            "is_selected": self.is_selected,
        }
        if self.unit_price:
            vals["unit_price"] = self.unit_price
        return vals


class FixQuotationTemplateBilling(models.Model):
    _name = "fix.quotation.template.billing"
    _description = "Quotation Template Billing Share"
    _order = "template_id, sequence, id"

    template_id = fields.Many2one(
        "fix.quotation.template", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    kind = fields.Selection(
        lambda self: self.env["fix.quotation.billing.line"]._fields["kind"].selection,
        required=True,
    )
    pct = fields.Float(string="Share (%)", required=True)
    due_days = fields.Integer()
    note = fields.Char()
