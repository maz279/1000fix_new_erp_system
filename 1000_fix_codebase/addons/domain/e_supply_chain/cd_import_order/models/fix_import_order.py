# fix_import_order — M44: the import order (consignment) and its lines.
#
# A06 workflow audit (2026-11-03): the order's state was moved by nothing but
# action_receive and direct writes; action_receive ran from draft, twice, and
# created no stock (M44-6, M44-13); the commitment FX rate was rewritten after
# the LC was opened (BRU-ITC-14); customs_duty and landed_cost were typed and
# never met the Bill of Entry (o06). Now the state is driven by the children's
# transitions, the commercial terms are pinned once the proforma is approved,
# and the receipt posts an M15 goods receipt through B1's contract.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_import_common import (
    OFFICER,
    changes,
    import_account,
    import_journal,
    post_import_move,
    refuse_locked,
    require_group,
    today,
)

# An M16 purchase order an import may be raised against: issued, not void.
PO_LINKABLE_STATES = ("sent", "acknowledged", "partially_received", "received")

ORDER_STATES = [
    ("draft", "Draft"),
    ("shipped", "Shipped"),
    ("customs", "In Customs"),
    ("cleared", "Cleared by Customs"),
    ("received", "Received"),
    ("landed", "Landed Cost Applied"),
]

# Pinned once a proforma is approved or an LC leaves draft: the commitment.
TERMS_FIELDS = (
    "currency_id",
    "fob_value",
    "fx_rate",
    "fx_rate_source",
    "fx_rate_date",
    "incoterm",
    "supplier_id",
    "purchase_order_id",
)
# Pinned once a Bill of Entry is assessed: they feed the assessable value.
CIF_FIELDS = ("freight_cost", "insurance_cost")


class FixImportOrder(models.Model):
    """M44: import, trade compliance, landed cost."""

    _name = "fix.import.order"
    _description = "Import Order"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    supplier_id = fields.Many2one("res.partner", string="Supplier")
    purchase_order_id = fields.Many2one(
        "fix.purchase.order",
        string="Purchase Order (M16)",
        index=True,
        ondelete="restrict",
        help="The M16 purchase order this consignment fulfils. The import receipt is "
        "recorded against it and posts the goods value to GRNI once (M44-1).",
    )
    country_origin = fields.Many2one("res.country", string="Country of Origin")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.USD")
    )
    incoterm = fields.Selection(
        [
            ("fob", "FOB — Free on Board"),
            ("cif", "CIF — Cost, Insurance & Freight"),
            ("cfr", "CFR — Cost & Freight"),
            ("exw", "EXW — Ex Works"),
            ("ddp", "DDP — Delivered Duty Paid"),
        ],
        default="fob",
    )
    fx_rate = fields.Float(string="FX Rate (BDT per unit)", default=1.0, tracking=True)
    fx_rate_source = fields.Char(
        string="FX Rate Source",
        help="Where the commitment rate came from (bank contract, BB rate of the day). "
        "BRU-ITC-14: the rate is recorded once with its source and never re-derived.",
    )
    fx_rate_date = fields.Date(string="FX Rate Date")
    shipment_mode = fields.Selection(
        [("sea", "Sea Freight"), ("air", "Air Freight"), ("courier", "Courier")],
        default="sea",
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Receiving Location", ondelete="restrict"
    )
    line_ids = fields.One2many("fix.import.order.line", "order_id", string="Lines")
    fob_value = fields.Monetary(string="FOB Value", currency_field="currency_id", tracking=True)
    freight_cost = fields.Monetary(string="Freight", currency_field="currency_id")
    insurance_cost = fields.Monetary(string="Insurance", currency_field="currency_id")
    boe_ids = fields.One2many("fix.import.boe", "order_id", string="Bills of Entry")
    customs_duty = fields.Monetary(
        string="Customs Duty (CD+RD+SD)",
        currency_field="currency_id",
        compute="_compute_customs_duty",
        store=True,
        help="Inventoriable duty of the paid Bills of Entry, in the order currency at the "
        "recorded FX rate. Computed, never typed.",
    )
    landed_cost = fields.Monetary(
        compute="_compute_landed", string="Landed Cost", currency_field="currency_id", store=True
    )
    receipt_id = fields.Many2one(
        "fix.stock.receipt", string="M15 Goods Receipt", readonly=True, copy=False
    )
    received_by_id = fields.Many2one("res.users", string="Received By", readonly=True, copy=False)
    received_on = fields.Date(string="Received On", readonly=True, copy=False)
    goods_move_id = fields.Many2one(
        "account.move", string="Goods Receipt Entry", readonly=True, copy=False
    )
    state = fields.Selection(ORDER_STATES, default="draft", required=True, tracking=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "receipt_id",
            "received_by_id",
            "received_on",
            "goods_move_id",
            "customs_duty",
            "landed_cost",
        }

    @api.constrains("purchase_order_id", "supplier_id", "company_id")
    def _check_purchase_order(self):
        for rec in self.filtered("purchase_order_id"):
            po = rec.purchase_order_id.sudo()
            if po.company_id != rec.company_id:
                raise ValidationError(
                    "Purchase order %s belongs to another company." % po.display_name
                )
            if rec.supplier_id and po.vendor_id != rec.supplier_id:
                raise ValidationError(
                    "Import %s is from %s but purchase order %s is with %s."
                    % (rec.name, rec.supplier_id.name, po.display_name, po.vendor_id.name)
                )
            if po.state not in PO_LINKABLE_STATES:
                raise ValidationError(
                    "Purchase order %s is %s: an import is raised against an issued order."
                    % (po.display_name, po.state)
                )

    def _import_terms_locked(self) -> bool:
        self.ensure_one()
        if not isinstance(self.id, int):
            return False
        su = self.env(su=True)
        approved = su["fix.import.proforma"].search_count(
            [("order_id", "=", self.id), ("state", "=", "approved")]
        )
        lcs = su["fix.import.lc"].search_count(
            [("order_id", "=", self.id), ("state", "!=", "draft")]
        )
        return bool(approved or lcs or self.state != "draft")

    def _import_cif_locked(self) -> bool:
        self.ensure_one()
        if not isinstance(self.id, int):
            return False
        return bool(
            self.env(su=True)["fix.import.boe"].search_count(
                [("order_id", "=", self.id), ("state", "!=", "draft")]
            )
        )

    def _import_locked_names(self) -> set:
        locked = set()
        if len(self) == 1 and isinstance(self.id, int):
            if self._import_terms_locked():
                locked |= set(TERMS_FIELDS) | {"line_ids"}
            if self._import_cif_locked():
                locked |= set(CIF_FIELDS)
            if self.state != "draft":
                locked |= {"company_id", "operating_unit_id"}
        return locked

    def _fix_form_locked_fields(self) -> set:
        return super()._fix_form_locked_fields() | self._import_locked_names()

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: r._import_locked_names(),
            "the commercial terms are pinned once the proforma is approved or an LC is "
            "applied for, and freight and insurance once a Bill of Entry is assessed "
            "(BRU-ITC-14).",
        )
        return super().write(vals)

    @api.depends(
        "boe_ids.state",
        "boe_ids.cd_amount",
        "boe_ids.rd_amount",
        "boe_ids.sd_amount",
        "fx_rate",
    )
    def _compute_customs_duty(self):
        for rec in self:
            paid = rec.boe_ids.filtered(lambda b: b.state == "paid")
            bdt = sum(b.cd_amount + b.rd_amount + b.sd_amount for b in paid)
            rate = rec.fx_rate or 0.0
            rec.customs_duty = round(bdt / rate, 2) if rate else 0.0

    @api.depends("fob_value", "freight_cost", "insurance_cost", "customs_duty")
    def _compute_landed(self):
        for rec in self:
            rec.landed_cost = (
                rec.fob_value + rec.freight_cost + rec.insurance_cost + rec.customs_duty
            )

    # ---- values ------------------------------------------------------------
    def _invoice_value(self) -> float:
        """The supplier's invoice value under the incoterm, in the order
        currency: FOB/EXW = goods only; CFR adds freight; CIF/DDP add both."""
        self.ensure_one()
        value = self.fob_value or 0.0
        if self.incoterm == "cfr":
            value += self.freight_cost or 0.0
        elif self.incoterm in ("cif", "ddp"):
            value += (self.freight_cost or 0.0) + (self.insurance_cost or 0.0)
        return value

    def _to_bdt(self, amount, currency):
        """An amount in `currency` (the order currency or BDT) in BDT."""
        self.ensure_one()
        bdt = self.env.ref("base.BDT")
        if not currency or currency == bdt:
            return amount
        if currency == self.currency_id:
            return amount * (self.fx_rate or 0.0)
        raise UserError(
            "%s is neither BDT nor the order currency %s: record it in one of them."
            % (currency.name, self.currency_id.name)
        )

    def _to_order_ccy(self, amount, currency):
        self.ensure_one()
        if not currency or currency == self.currency_id:
            return amount
        if currency == self.env.ref("base.BDT"):
            return amount / self.fx_rate if self.fx_rate else 0.0
        raise UserError(
            "%s is neither BDT nor the order currency %s: record it in one of them."
            % (currency.name, self.currency_id.name)
        )

    def _import_set_state(self, state, allowed):
        """A child transition moves the order. Run as superuser: the child's
        own action already checked the user's role."""
        for rec in self.sudo():
            if rec.state in allowed:
                rec._guarded().write({"state": state})

    # ---- receipt into M15 -----------------------------------------------------
    def action_receive(self):
        """Receive the cleared consignment into M15 at its provisional landed
        cost (goods at the recorded FX rate plus the posted estimate, if any).
        Once only, from Cleared only (M44-13)."""
        require_group(self.env, OFFICER, "Receiving an import into stock")
        for rec in self:
            if rec.state != "cleared":
                raise UserError(
                    "Import order %s cannot be received: it is %s. Receive it once customs "
                    "has released it (a cleared arrival with a paid Bill of Entry)."
                    % (rec.name, dict(ORDER_STATES)[rec.state])
                )
            if rec.receipt_id:
                raise UserError(
                    "Import order %s is already received (%s)." % (rec.name, rec.receipt_id.name)
                )
            if not rec.line_ids:
                raise UserError("Import order %s has no lines to receive." % rec.name)
            if not rec.location_id:
                raise UserError("Set the receiving location of import order %s first." % rec.name)
            if not rec.supplier_id:
                raise UserError("Import order %s has no supplier." % rec.name)
            # M44-1: the goods value reaches the GL once, at receipt (Dr stock
            # valuation / Cr GRNI). Accounts are resolved before anything moves.
            company = rec.company_id
            stock_account = import_account(rec.env, company, "inventory")
            grni_account = import_account(rec.env, company, "grni")
            journal = import_journal(rec.env, company)
            su = rec.sudo()
            estimate = su.env["fix.import.landed"].search(
                [
                    ("order_id", "=", rec.id),
                    ("sheet_type", "=", "estimate"),
                    ("state", "=", "estimated"),
                ],
                limit=1,
            )
            per_line = {al.order_line_id.id: al.amount for al in estimate.line_ids}
            if estimate:
                import_account(rec.env, company, "landed_accrual")
            receipt_lines = []
            for line in rec.line_ids:
                provisional = line._goods_value_bdt() + per_line.get(line.id, 0.0)
                receipt_lines.append(
                    (
                        0,
                        0,
                        {
                            "part_id": line.part_id.id,
                            "qty_received": line.quantity,
                            "qty_accepted": line.quantity,
                            "unit_cost": round(provisional / line.quantity, 4),
                        },
                    )
                )
            Receipt = su.env["fix.stock.receipt"]
            receipt_vals = {
                "company_id": rec.company_id.id,
                "operating_unit_id": rec.operating_unit_id.id or False,
                "partner_id": rec.supplier_id.id,
                "location_id": rec.location_id.id,
                "received_on": today(rec),
                "inspection_notes": "Import %s (M44)" % rec.name,
                "line_ids": receipt_lines,
            }
            if rec.purchase_order_id and "purchase_order_id" in Receipt._fields:
                receipt_vals["purchase_order_id"] = rec.purchase_order_id.id
            for key, value in (
                ("source_model", rec._name),
                ("source_res_id", rec.id),
                ("source_ref", rec.name),
            ):
                if key in Receipt._fields:
                    receipt_vals[key] = value
            receipt = Receipt.create(receipt_vals)
            if receipt.state == "draft":
                receipt.action_inspect()
            receipt.action_post()
            goods = round(sum(line._goods_value_bdt() for line in rec.line_ids), 2)
            ref = "Import receipt %s (%s)" % (rec.name, receipt.name)
            goods_move = post_import_move(
                rec.env,
                company,
                journal,
                today(rec),
                ref,
                [
                    (stock_account, "Goods received %s" % rec.name, goods),
                    (grni_account, "GRNI %s" % (rec.purchase_order_id.name or rec.name), -goods),
                ],
                operating_unit=rec.operating_unit_id,
            )
            if estimate:
                estimate._landed_post_estimate_entry(receipt)
            rec._guarded().write(
                {
                    "state": "received",
                    "goods_move_id": goods_move.id or False,
                    "receipt_id": receipt.id,
                    "received_by_id": rec.env.user.id,
                    "received_on": today(rec),
                }
            )
            publish(
                rec.env,
                "goods.received",
                "fix.import.order",
                rec.id,
                {
                    "order": rec.name,
                    "receipt": receipt.name,
                    "receipt_id": receipt.id,
                    "vendor_id": rec.supplier_id.id,
                    "purchase_order_id": rec.purchase_order_id.id or None,
                    "value": float(rec.fob_value),
                    "provisional_value_bdt": round(
                        sum(line._goods_value_bdt() for line in rec.line_ids)
                        + (estimate.total_landed if estimate else 0.0),
                        2,
                    ),
                },
            )
        return True


class FixImportOrderLine(models.Model):
    """What is being imported: the part, quantity and supplier price. The
    receipt, the Bill of Entry's assessable value and the landed-cost
    allocation all read these lines."""

    _name = "fix.import.order.line"
    _description = "Import Order Line"
    _order = "order_id, id"
    _inherit = ["fix.guarded.mixin"]

    order_id = fields.Many2one("fix.import.order", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="order_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="order_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="order_id.currency_id")
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    description = fields.Char()
    hs_id = fields.Many2one("fix.import.hs", string="HS Classification", ondelete="restrict")
    quantity = fields.Float(required=True, default=1.0)
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id")
    fob_amount = fields.Monetary(
        string="Line Value", currency_field="currency_id", compute="_compute_values", store=True
    )
    cif_amount = fields.Monetary(
        string="CIF Value",
        currency_field="currency_id",
        compute="_compute_values",
        store=True,
        help="Line value plus its share (by value) of the freight and insurance the "
        "incoterm leaves to the importer.",
    )

    _qty_positive = models.Constraint(
        "CHECK (quantity > 0)", "An import line needs a positive quantity"
    )
    _price_non_negative = models.Constraint(
        "CHECK (unit_price >= 0)", "A unit price cannot be negative"
    )

    @api.depends(
        "quantity",
        "unit_price",
        "order_id.incoterm",
        "order_id.freight_cost",
        "order_id.insurance_cost",
        "order_id.line_ids.quantity",
        "order_id.line_ids.unit_price",
    )
    def _compute_values(self):
        for rec in self:
            rec.fob_amount = round((rec.quantity or 0.0) * (rec.unit_price or 0.0), 2)
        for rec in self:
            order = rec.order_id
            total = sum((ln.quantity or 0.0) * (ln.unit_price or 0.0) for ln in order.line_ids)
            share = (rec.fob_amount / total) if total else 0.0
            extra = 0.0
            if order.incoterm in ("fob", "exw", False):
                extra = (order.freight_cost or 0.0) + (order.insurance_cost or 0.0)
            elif order.incoterm == "cfr":
                extra = order.insurance_cost or 0.0
            rec.cif_amount = round(rec.fob_amount + extra * share, 2)

    def _goods_value_bdt(self) -> float:
        self.ensure_one()
        return round(self.fob_amount * (self.order_id.fx_rate or 0.0), 2)

    def _line_locked(self) -> bool:
        return any(rec.order_id._import_terms_locked() for rec in self.sudo())

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"fob_amount", "cif_amount"}

    _PINNED = "The lines of an import order are pinned once its proforma is approved or an LC is applied for."

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.su and records._line_locked():
            raise UserError(self._PINNED)
        return records

    def write(self, vals):
        if self and not self.env.su and self._line_locked() and changes(self, vals):
            raise UserError(self._PINNED)
        return super().write(vals)

    def unlink(self):
        if not self.env.su and self._line_locked():
            raise UserError(self._PINNED)
        return super().unlink()
