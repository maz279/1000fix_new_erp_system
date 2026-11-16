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
    APPROVER,
    OFFICER,
    changes,
    import_account,
    import_journal,
    post_import_move,
    refuse_locked,
    require_group,
    schedule_alert,
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
    ("closed", "Closed"),
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
    m16_receipt_id = fields.Many2one(
        "fix.purchase.receipt", string="M16 Goods Receipt", readonly=True, copy=False
    )
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    closed_on = fields.Date(string="Closed On", readonly=True, copy=False)
    state = fields.Selection(ORDER_STATES, default="draft", required=True, tracking=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "receipt_id",
            "m16_receipt_id",
            "received_by_id",
            "received_on",
            "goods_move_id",
            "customs_duty",
            "landed_cost",
            "closed_by_id",
            "closed_on",
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
            # a draft IMPORT purchase order may be linked while the two are
            # raised from each other (12 Nov 2026); it must be issued before
            # the proforma is approved or the goods are received
            # (fix_import_purchase_link)
            draft_import = po.state == "draft" and po.purchase_type == "import"
            if po.state not in PO_LINKABLE_STATES and not draft_import:
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
                # BRU-ITC-14: a source or date never recorded can still be
                # recorded (they were optional); once held they are pinned.
                locked -= {f for f in ("fx_rate_source", "fx_rate_date") if not self[f]}
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

    # ---- commitment gates -----------------------------------------------------
    def _import_check_fx(self, what):
        """BRU-ITC-14: a foreign-currency order carries the commitment rate
        with its source and date before it leaves draft. 1.0 is the field's
        default, not a rate anyone recorded."""
        bdt = self.env.ref("base.BDT")
        for rec in self:
            if rec.currency_id == bdt:
                continue
            missing = []
            if (rec.fx_rate or 0.0) <= 0 or rec.fx_rate == 1.0:
                missing.append("the commitment FX rate")
            if not (rec.fx_rate_source or "").strip():
                missing.append("the rate source")
            if not rec.fx_rate_date:
                missing.append("the rate date")
            if missing:
                raise UserError(
                    "%s: order %s is in %s and has no %s (BRU-ITC-14)."
                    % (what, rec.name, rec.currency_id.name, ", ".join(missing))
                )
            if rec.fx_rate_date > today(rec):
                raise UserError("%s: the FX rate date of %s is in the future." % (what, rec.name))

    def _import_check_instrument(self, what):
        """A consignment ships against a payment instrument: an opened LC or
        an approved advance (scorecard 24)."""
        su = self.env(su=True)
        for rec in self:
            lcs = su["fix.import.lc"].search_count(
                [("order_id", "=", rec.id), ("state", "in", ("opened", "amended", "closed"))]
            )
            advances = su["fix.import.advance"].search_count(
                [("order_id", "=", rec.id), ("state", "=", "approved")]
            )
            if not lcs and not advances:
                raise UserError(
                    "%s: order %s has neither an opened LC nor an approved advance: record the "
                    "payment instrument first." % (what, rec.name)
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
            # M44-7: the state alone is not evidence: a Bill of Entry reversed
            # after clearance must not let the goods in.
            live = rec.sudo().boe_ids.filtered(lambda b: b.state != "reversed")
            if not live.filtered(lambda b: b.state == "paid") or live.filtered(
                lambda b: b.state != "paid"
            ):
                raise UserError(
                    "Import order %s cannot be received: every live Bill of Entry must be paid, "
                    "and at least one must exist." % rec.name
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
            m16_receipt = rec._import_post_m16_receipt()
            # A PO-linked import's M15 receipt names its M16 GRN as source, as
            # the M16 bridge's own receipts do: an inspection rejection on the
            # GRN then finds this stock and moves it to quarantine.
            for key, value in (
                ("source_model", m16_receipt._name if m16_receipt else rec._name),
                ("source_res_id", m16_receipt.id if m16_receipt else rec.id),
                ("source_ref", m16_receipt.name if m16_receipt else rec.name),
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
                    "m16_receipt_id": m16_receipt.id or False,
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

    def _import_post_m16_receipt(self):
        """M44-1 + M52: the AP three-way match reads posted M16 receipt lines,
        so a PO-linked import also posts its M16 GRN. The import's own M15
        receipt and GRNI entry carry the stock and the GL; the GRN is marked
        with this order and the M16 -> M15 bridge skips a marked GRN, so
        neither is posted twice. M16's own rules apply: quantity within the
        PO, the requester and buyer never receive (SOD-02), and the inspection
        decides the accepted quantity."""
        self.ensure_one()
        Receipt = self.env(su=True)["fix.purchase.receipt"]
        po = self.purchase_order_id.sudo()
        if not po:
            return Receipt
        remaining = {
            pol.id: max((pol.qty_ordered or 0.0) - (pol.qty_received or 0.0), 0.0)
            for pol in po.line_ids
        }
        lines = []
        for line in self.line_ids:
            product = line.part_id.sudo().product_id
            if not product:
                raise UserError(
                    "%s has no purchasing product, so it cannot be matched to PO %s."
                    % (line.part_id.display_name, po.name)
                )
            qty = line.quantity
            for pol in po.line_ids.filtered(lambda p, pr=product: p.product_id == pr):
                take = min(qty, remaining[pol.id])
                if take > 0:
                    lines.append((0, 0, {"po_line_id": pol.id, "qty_received": take}))
                    remaining[pol.id] -= take
                    qty -= take
            if qty > 1e-6:
                raise UserError(
                    "PO %s has %.2f less of %s left to receive than import %s brings."
                    % (po.name, qty, product.display_name, self.name)
                )
        receipt = Receipt.create(
            {
                "purchase_order_id": po.id,
                "delivery_note_ref": self.name,
                "notes": "Import receipt %s (M44)" % self.name,
                "line_ids": lines,
            }
        )
        receipt._guarded().write({"import_order_id": self.id})
        if not self.env.su and self.env.user in receipt._a06_conflicted_receivers():
            raise UserError(
                "Segregation of duties (SOD-02): you requested or bought PO %s and cannot "
                "record its goods receipt." % po.name
            )
        receipt.action_post()
        return receipt

    # ---- close --------------------------------------------------------------
    def action_close(self):
        """BRU-ITC-18: a fully received, finally costed order is closed by an
        Import Approver, with nothing left open against it. Unreconciled cost
        documents (agent, port, bank bills) are refused by the
        fix_import_capture override (BRU-ITC-16)."""
        require_group(self.env, APPROVER, "Closing an import order")
        for rec in self:
            su = rec.sudo()
            if rec.state != "landed":
                raise UserError(
                    "Import order %s is %s: close it once it is received and its final landed "
                    "cost is applied." % (rec.name, dict(ORDER_STATES)[rec.state])
                )
            blockers = []
            sheets = su.env["fix.import.landed"].search([("order_id", "=", rec.id)])
            finals = sheets.filtered(lambda s: s.sheet_type == "final")
            if not finals.filtered(lambda s: s.state == "finalised"):
                blockers.append("no final landed-cost sheet")
            if finals.filtered(lambda s: s.state == "draft"):
                blockers.append("a draft landed-cost sheet")
            if su.boe_ids.filtered(lambda b: b.state in ("draft", "assessed")):
                blockers.append("an unpaid Bill of Entry")
            lcs = su.env["fix.import.lc"].search([("order_id", "=", rec.id)])
            if lcs.filtered(lambda lc: lc.state in ("applied", "opened", "amended")):
                blockers.append("an LC not yet closed")
            if blockers:
                raise UserError(
                    "Import order %s cannot close: %s (BRU-ITC-18)."
                    % (rec.name, ", ".join(blockers))
                )
            rec.sudo()._guarded().write(
                {"state": "closed", "closed_by_id": rec.env.user.id, "closed_on": today(rec)}
            )
        return True

    # ---- event consumers ----------------------------------------------------
    @api.model
    def consume_irc_expired(self, event):
        """import.irc_expired: every open order of that importer is told that
        nothing progresses until a valid IRC is recorded."""
        irc = self.env["fix.import.irc"].sudo().browse(event.get("aggregate_id") or 0).exists()
        if not irc:
            return 0
        orders = self.sudo().search(
            [
                ("company_id", "=", irc.company_id.id),
                ("state", "not in", ("received", "landed", "closed")),
            ]
        )
        note = (
            "IRC %s has expired: this order's proforma, LC, B/L and Bill of Entry steps are "
            "refused until a valid certificate is recorded." % irc.irc_no
        )
        for order in orders:
            order.message_post(body=note)
            schedule_alert(order, "IRC expired", note, order.create_uid)
        return len(orders)


class FixPurchaseReceiptImport(models.Model):
    """The mark that keeps an import's M16 GRN from posting stock a second
    time: its goods entered M15 and the GL through the import receipt."""

    _inherit = "fix.purchase.receipt"

    import_order_id = fields.Many2one(
        "fix.import.order",
        string="Import Order (M44)",
        readonly=True,
        copy=False,
        index=True,
        ondelete="restrict",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"import_order_id"}

    def _fix_post_to_m15(self):
        self.ensure_one()
        if self.import_order_id:
            return self.env["fix.stock.receipt"]
        return super()._fix_post_to_m15()


class FixImportOrderLine(models.Model):
    """What is being imported: the part, quantity and supplier price. The
    receipt, the Bill of Entry's assessable value and the landed-cost
    allocation all read these lines."""

    _name = "fix.import.order.line"
    _description = "Import Order Line"
    _order = "order_id, id"
    _inherit = ["fix.guarded.mixin"]
    _rec_names_search = ["order_id.name", "part_id.name", "part_id.part_number", "description"]

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

    @api.depends("order_id.name", "part_id.name", "description", "quantity")
    def _compute_display_name(self):
        """A picker names the order: the Bill of Entry's line list is not
        filtered to its own order (the form's domains are static)."""
        for rec in self:
            rec.display_name = "%s / %s x %g" % (
                rec.order_id.name or "?",
                rec.part_id.sudo().name or rec.description or "?",
                rec.quantity or 0.0,
            )

    @api.constrains("hs_id", "part_id")
    def _check_hs_of_part(self):
        """M44-10: a line is classified by its own part's ruling, so another
        product's lower-duty ruling cannot be used. fix.import.hs is one row
        per product.product; a spare part names its product in M15."""
        for rec in self.sudo():
            rec._import_check_hs_of_part()

    def _import_check_hs_of_part(self, what=None):
        self.ensure_one()
        if not self.hs_id:
            return
        product = self.part_id.sudo().product_id
        prefix = "%s: " % what if what else ""
        if not product:
            raise ValidationError(
                "%s%s has no purchasing product in M15, so HS %s cannot be shown to be its "
                "classification. Name the product on the spare part first."
                % (prefix, self.part_id.display_name, self.hs_id.hs_code)
            )
        if self.hs_id.sudo().product_id != product:
            raise ValidationError(
                "%sHS %s is the ruling for %s, not for %s (M44-10)."
                % (
                    prefix,
                    self.hs_id.hs_code,
                    self.hs_id.sudo().product_id.display_name,
                    product.display_name,
                )
            )

    @api.depends(
        "quantity",
        "unit_price",
        "order_id.incoterm",
        "order_id.freight_cost",
        "order_id.insurance_cost",
        "order_id.insurance_ids.state",
        "order_id.insurance_ids.premium",
        "order_id.insurance_ids.currency_id",
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
            # BRU-ITC-13: the verified cover's premium is the insurance in the CIF
            insurance = order._import_insurance_for_cif() if order else 0.0
            if order.incoterm in ("fob", "exw", False):
                extra = (order.freight_cost or 0.0) + insurance
            elif order.incoterm == "cfr":
                extra = insurance
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
