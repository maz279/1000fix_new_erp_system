# M36 quote-to-cash P2 (12-13 Nov 2026): what an accepted quotation becomes,
# and how it is billed and paid.
#
# - Segments (consumer, corporate, government / private tender, dealer) set
#   the defaults a quotation starts with: payment term, payment methods
#   offered, the customer's expected withholding (VDS, TDS) and the expected
#   net receipt.
# - A corporate customer can require its purchase order: acceptance is then
#   refused without the PO number (above the customer's threshold).
# - Each line says how it is fulfilled. On acceptance the quotation's
#   fulfilment plan creates the documents: draft deliveries (stock.picking)
#   for goods, M01 service orders for work on a named device, an M08
#   contract WITH its scope lines for AMC / recurring lines, and a to-do for
#   work that has no device yet. Every document lands in the hand-off log.
# - A billing plan (milestones, on delivery, on completion, recurring,
#   retention) totals 100% and drafts the AR invoices Finance issues. An
#   advance is not an invoice: it is a customer receipt linked to the
#   quotation, and it is applied to the quotation's invoices as they are
#   issued.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

SEGMENTS = [
    ("consumer", "Consumer / Walk-in"),
    ("corporate", "Corporate (B2B)"),
    ("gov_tender", "Government Tender (e-GP)"),
    ("private_tender", "Private Tender / RFQ"),
    ("dealer", "Dealer / Partner"),
]
B2B_SEGMENTS = ("corporate", "gov_tender", "private_tender")

# The payment term a segment starts with (xml ids; the first that exists).
SEGMENT_TERM = {
    "consumer": ("account.account_payment_term_immediate",),
    "dealer": ("account.account_payment_term_15days",),
    "corporate": ("account.account_payment_term_30days",),
    "private_tender": ("account.account_payment_term_30days",),
    "gov_tender": (
        "cd_billing_engine.payment_term_bd_tender_retention",
        "account.account_payment_term_30days",
    ),
}
# Which payment-method channel flag a segment offers.
SEGMENT_CHANNEL = {
    "consumer": ("for_counter", "for_portal", "for_field"),
    "dealer": ("for_counter", "for_portal", "for_corporate"),
    "corporate": ("for_corporate",),
    "private_tender": ("for_corporate",),
    "gov_tender": ("for_corporate",),
}

FULFILMENT = [
    ("service_order", "M01 service order (repair / on-site job)"),
    ("delivery", "Delivery from stock"),
    ("contract", "M08 contract scope (AMC / recurring)"),
    ("subscription", "M39 subscription"),
    ("schedule", "To schedule (no device / third party)"),
    ("none", "Billed only (fee, warranty extension)"),
]
TYPE_FULFILMENT = {
    "part": "delivery",
    "goods": "delivery",
    "labour": "service_order",
    "service": "service_order",
    "diagnostic": "service_order",
    "callout": "service_order",
    "installation": "service_order",
    "recurring": "contract",
    "rental": "contract",
    "subscription": "subscription",
    "subcontract": "schedule",
    "warranty_ext": "none",
    "fee": "none",
}

BILLING_KINDS = [
    ("milestone", "Milestone"),
    ("on_delivery", "On delivery"),
    ("on_completion", "On completion / acceptance"),
    ("recurring", "Recurring (contract / subscription billing)"),
    ("retention", "Retention release"),
]
# Invoiced by their own engines, never drafted from the plan.
ENGINE_BILLED = {
    "service": "the closed M01 service order (auto-invoice)",
    "contract": "the M08 contract billing",
    "subscription": "the M39 subscription charges",
}


class FixQuotationLineSupply(models.Model):
    _inherit = "fix.quotation.line"

    device_id = fields.Many2one(
        "fix.device", string="Device", help="The customer's device the work is on."
    )
    site_id = fields.Many2one(
        "res.partner",
        string="Site",
        help="Where it is delivered or done: one of the customer's addresses.",
    )
    fulfilment = fields.Selection(
        FULFILMENT,
        compute="_compute_fulfilment",
        store=True,
        readonly=False,
        help="How the line is fulfilled when the quotation is accepted.",
    )

    @api.depends("line_type", "display_type", "quotation_id.quote_type")
    def _compute_fulfilment(self):
        for line in self:
            if line.display_type:
                line.fulfilment = False
            elif line.quotation_id.quote_type == "service":
                # a repair quotation: everything is the M01 order's
                line.fulfilment = "service_order"
            else:
                line.fulfilment = TYPE_FULFILMENT.get(line.line_type or "", "none")

    @api.constrains("site_id", "quotation_id")
    def _check_site(self):
        for line in self.filtered("site_id"):
            customer = line.quotation_id.customer_id.commercial_partner_id
            if line.site_id.commercial_partner_id != customer:
                raise ValidationError(
                    "Site %s is not one of %s's addresses."
                    % (line.site_id.display_name, line.quotation_id.customer_id.display_name)
                )


class FixQuotationHandoff(models.Model):
    _name = "fix.quotation.handoff"
    _description = "Quotation Hand-off"
    _order = "quotation_id, id"

    quotation_id = fields.Many2one("fix.quotation", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="quotation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="quotation_id.operating_unit_id", store=True, index=True
    )
    kind = fields.Selection(
        [
            ("service_order", "Service order"),
            ("delivery", "Delivery"),
            ("contract", "Contract"),
            ("subscription", "Subscription"),
            ("task", "To schedule"),
            ("invoice", "Invoice"),
            ("receipt", "Advance receipt"),
        ],
        required=True,
    )
    res_model = fields.Char(readonly=True)
    res_id = fields.Many2oneReference(model_field="res_model", readonly=True)
    ref = fields.Char(string="Document", readonly=True)
    state = fields.Selection(
        [("created", "Created"), ("pending", "Pending"), ("failed", "Failed")],
        default="created",
        required=True,
    )
    note = fields.Char()
    line_ids = fields.Many2many("fix.quotation.line", string="Lines")

    def write(self, vals):
        if not self.env.su:
            raise UserError("The hand-off log is written by the conversion only.")
        return super().write(vals)


class FixQuotationBillingLine(models.Model):
    _name = "fix.quotation.billing.line"
    _description = "Quotation Billing Plan Line"
    _order = "quotation_id, sequence, id"

    quotation_id = fields.Many2one("fix.quotation", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="quotation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="quotation_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="quotation_id.currency_id")
    sequence = fields.Integer(default=10)
    kind = fields.Selection(BILLING_KINDS, required=True, default="on_completion")
    pct = fields.Float(string="Share (%)", required=True)
    amount = fields.Monetary(
        string="Amount (excl. VAT)",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
    )
    due_days = fields.Integer(string="Due (days after invoice)")
    note = fields.Char(string="Trigger / Milestone")
    state = fields.Selection(
        [("planned", "Planned"), ("invoiced", "Invoiced")],
        default="planned",
        required=True,
        readonly=True,
    )
    invoice_id = fields.Many2one("fix.ar.invoice", readonly=True, copy=False)

    @api.depends("pct", "quotation_id.value")
    def _compute_amount(self):
        for line in self:
            line.amount = round((line.quotation_id.value or 0.0) * (line.pct or 0.0) / 100.0, 2)

    @api.constrains("pct")
    def _check_pct(self):
        for line in self:
            if not 0.0 < (line.pct or 0.0) <= 100.0:
                raise ValidationError("A billing share is above 0 and at most 100%.")

    @api.model_create_multi
    def create(self, vals_list):
        Quote = self.env["fix.quotation"]
        quotes = Quote.browse({v.get("quotation_id") for v in vals_list} - {None})
        if not self.env.context.get("fix_billing_plan_default"):
            self.env["fix.quotation.line"]._assert_editable(quotes)
        for vals in vals_list:
            vals.pop("state", None)
            vals.pop("invoice_id", None)
        lines = super().create(vals_list)
        lines.quotation_id._sync_from_lines()
        return lines

    def write(self, vals):
        if set(vals) - {"state", "invoice_id"}:
            self.env["fix.quotation.line"]._assert_editable(self.quotation_id)
        if ({"state", "invoice_id"} & set(vals)) and not self.env.su:
            raise UserError("A billing line is invoiced by its action only.")
        res = super().write(vals)
        if set(vals) - {"state", "invoice_id"}:
            self.quotation_id._sync_from_lines()
        return res

    def unlink(self):
        quotes = self.quotation_id
        self.env["fix.quotation.line"]._assert_editable(quotes)
        if self.filtered("invoice_id"):
            raise UserError("An invoiced billing line stays on the plan.")
        res = super().unlink()
        quotes.exists()._sync_from_lines()
        return res

    def action_invoice(self):
        """Draft the AR invoice for this share; Finance issues it (number,
        Mushak 6.3, GL). Shares billed by their own engine are refused."""
        Invoice = self.env["fix.ar.invoice"]
        for line in self:
            quote = line.quotation_id
            if quote.state != "accepted":
                raise UserError("Only an accepted quotation's billing plan is invoiced.")
            if line.state != "planned":
                raise UserError("Billing line %s is already invoiced." % line.display_name)
            engine = ENGINE_BILLED.get(quote.quote_type)
            if engine or line.kind == "recurring":
                raise UserError(
                    "This share is invoiced by %s, not from the plan."
                    % (engine or "the contract / subscription billing")
                )
            invoice = Invoice.sudo()._fix_draft_invoice_from_source(
                "fix.quotation.billing.line",
                "%s v%d / %s" % (quote.name, quote.version, line.id),
                quote.customer_id,
                [
                    {
                        "description": "%s v%d - %s %.4g%%%s"
                        % (
                            quote.name,
                            quote.version,
                            dict(BILLING_KINDS)[line.kind],
                            line.pct,
                            (": " + line.note) if line.note else "",
                        ),
                        "taxable_amount": line.amount,
                    }
                ],
                "Quotation %s billing plan (%s)" % (quote.name, dict(BILLING_KINDS)[line.kind]),
                company=quote.company_id,
                operating_unit=quote.operating_unit_id or None,
            )
            line.sudo().write({"state": "invoiced", "invoice_id": invoice.id})
            quote._log_handoff("invoice", invoice, note=dict(BILLING_KINDS)[line.kind])
        return True


class FixQuotationSupply(models.Model):
    _inherit = "fix.quotation"

    quote_type = fields.Selection(
        selection_add=[("project", "Goods & works order (deliveries + service jobs)")],
        ondelete={"project": "set default"},
    )
    segment = fields.Selection(SEGMENTS, help="Sets the starting payment term and methods.")
    expected_vds_rate = fields.Float(
        string="Expected VDS (%)",
        help="VAT the customer deducts at source (Mushak 6.6), as a % of the value.",
    )
    expected_vds_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_expected_net", store=True
    )
    expected_net_receipt = fields.Monetary(
        string="Expected Cash Receipt",
        currency_field="currency_id",
        compute="_compute_expected_net",
        store=True,
        help="Total payable less the VDS and TDS the customer withholds.",
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Deliver From",
        domain="[('code', '=', 'outgoing')]",
        help="The delivery operation goods lines leave by.",
    )
    billing_line_ids = fields.One2many(
        "fix.quotation.billing.line", "quotation_id", string="Billing Plan", copy=True
    )
    handoff_ids = fields.One2many("fix.quotation.handoff", "quotation_id", string="Hand-offs")
    advance_receipt_ids = fields.One2many(
        "fix.ar.receipt", "quotation_id", string="Advance Receipts"
    )
    advance_received = fields.Monetary(
        currency_field="currency_id", compute="_compute_advance_received"
    )
    advance_outstanding = fields.Monetary(
        currency_field="currency_id", compute="_compute_advance_received"
    )
    # inputs for "Record Advance Received" (not terms; cleared by the action)
    advance_entry_amount = fields.Monetary(
        string="Advance Amount Received", currency_field="currency_id"
    )
    advance_entry_method_id = fields.Many2one("fix.payment.method", string="Received By")
    advance_entry_ref = fields.Char(string="Payment Reference (TrxID / cheque no.)")

    @api.depends(
        "amount_total", "vat_amount", "value", "expected_vds_rate", "tds_amount", "segment"
    )
    def _compute_expected_net(self):
        for rec in self:
            vds = min(
                rec.vat_amount or 0.0,
                round((rec.value or 0.0) * (rec.expected_vds_rate or 0.0) / 100.0, 2),
            )
            rec.expected_vds_amount = vds
            tds = rec.tds_amount if rec.segment in B2B_SEGMENTS else 0.0
            rec.expected_net_receipt = round((rec.amount_total or 0.0) - vds - (tds or 0.0), 2)

    @api.depends("advance_receipt_ids.amount", "advance_receipt_ids.state", "advance_amount")
    def _compute_advance_received(self):
        for rec in self:
            got = sum(
                r.amount for r in rec.advance_receipt_ids if r.state not in ("draft", "reversed")
            )
            rec.advance_received = got
            rec.advance_outstanding = max(0.0, round((rec.advance_amount or 0.0) - got, 2))

    @api.constrains("expected_vds_rate")
    def _check_vds_rate(self):
        for rec in self:
            if not 0.0 <= (rec.expected_vds_rate or 0.0) <= 100.0:
                raise ValidationError("An expected VDS rate is between 0 and 100%.")

    # ---- segment defaults ---------------------------------------------------
    @api.model
    def _segment_defaults(self, segment):
        vals = {}
        for xmlid in SEGMENT_TERM.get(segment, ()):
            term = self.env.ref(xmlid, raise_if_not_found=False)
            if term:
                vals["payment_term_id"] = term.id
                break
        Method = self.env.get("fix.payment.method")
        if Method is not None:
            flags = SEGMENT_CHANNEL.get(segment, ())
            methods = Method.search([]).filtered(lambda m: any(m[f] for f in flags))
            vals["payment_method_ids"] = [(6, 0, methods.ids)]
        if segment not in B2B_SEGMENTS:
            vals["tds_rate"] = 0.0
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        Partner = self.env["res.partner"]
        for vals in vals_list:
            if not vals.get("segment"):
                partner = Partner.browse(vals.get("customer_id")).exists()
                vals["segment"] = "corporate" if partner.is_company else "consumer"
            for key, value in self._segment_defaults(vals["segment"]).items():
                vals.setdefault(key, value)
            if not vals.get("picking_type_id"):
                company = vals.get("company_id") or self.env.company.id
                ptype = self.env["stock.picking.type"].search(
                    [("code", "=", "outgoing"), ("company_id", "in", (company, False))], limit=1
                )
                if ptype:
                    vals["picking_type_id"] = ptype.id
        return super().create(vals_list)

    # ---- the scope digest also covers the billing plan ------------------------
    def _scope_fingerprint(self) -> str:
        import hashlib

        base = super()._scope_fingerprint()
        plan = "|".join(
            "%s:%s:%.4f:%s:%s" % (b.sequence, b.kind, b.pct or 0.0, b.due_days or 0, b.note or "")
            for b in self.billing_line_ids.sorted(lambda r: (r.sequence, r.id))
        )
        return hashlib.sha256(("%s#%s" % (base, plan)).encode()).hexdigest()

    def _snapshot(self) -> str:
        import json

        data = json.loads(super()._snapshot())
        data.update(
            {
                "segment": self.segment or "",
                "expected_vds_rate": round(self.expected_vds_rate or 0.0, 4),
                "picking_type_id": self.picking_type_id.id or False,
            }
        )
        return json.dumps(data, sort_keys=True)

    # ---- default billing plan ----------------------------------------------
    def _default_billing_plan(self):
        """The plan a quotation gets when the author gives none: engine-billed
        types bill once by their engine; a goods & works order bills the goods
        on delivery and the work on completion; a government tender keeps the
        retention back."""
        self.ensure_one()
        if self.quote_type in ("contract", "subscription"):
            return [("recurring", 100.0, "")]
        retention = 10.0 if self.segment == "gov_tender" else 0.0
        if self.quote_type == "service":
            return [("on_completion", 100.0, "")]
        priced = self._scope_lines()
        goods = sum(ln.subtotal for ln in priced if ln.fulfilment == "delivery")
        total = sum(priced.mapped("subtotal")) or 0.0
        plan = []
        if total and 0.0 < goods < total:
            goods_pct = round(goods / total * 100.0, 2)
            plan.append(("on_delivery", goods_pct, "Goods delivered"))
            plan.append(
                ("on_completion", round(100.0 - goods_pct - retention, 2), "Work completed")
            )
        else:
            kind = "on_delivery" if goods and goods >= total else "on_completion"
            plan.append((kind, round(100.0 - retention, 2), ""))
        if retention:
            plan.append(("retention", retention, "Released after the warranty period"))
        return [p for p in plan if p[1] > 0]

    def _ensure_billing_plan(self):
        Billing = self.env["fix.quotation.billing.line"].with_context(fix_billing_plan_default=True)
        for rec in self.filtered(lambda q: not q.billing_line_ids):
            Billing.create(
                [
                    {
                        "quotation_id": rec.id,
                        "sequence": (i + 1) * 10,
                        "kind": kind,
                        "pct": pct,
                        "note": note or False,
                    }
                    for i, (kind, pct, note) in enumerate(rec._default_billing_plan())
                ]
            )

    def action_submit(self, justification=None):
        self._ensure_billing_plan()
        return super().action_submit(justification=justification)

    def _readiness_problems(self) -> list:
        problems = super()._readiness_problems()
        plan = self.billing_line_ids
        if plan and abs(sum(plan.mapped("pct")) - 100.0) > 0.01:
            problems.append(
                "The billing plan shares add up to %.2f%%, not 100%%." % sum(plan.mapped("pct"))
            )
        if self.quote_type == "project":
            if not self.operating_unit_id:
                problems.append("Set the operating unit the orders and deliveries belong to.")
            if any(ln.fulfilment == "delivery" for ln in self._scope_lines()) and not (
                self.picking_type_id
            ):
                problems.append("Choose the delivery operation the goods leave by.")
        return problems

    # ---- acceptance: the customer's purchase order ---------------------------
    def _po_required(self) -> bool:
        partner = self.customer_id.commercial_partner_id
        if not partner.fix_po_required:
            return False
        return (self.amount_total or 0.0) > (partner.fix_po_required_above or 0.0)

    def _accept(self, method, ref):
        self.ensure_one()
        if self._po_required() and not (self.customer_po_ref or "").strip():
            raise UserError(
                "%s requires its purchase order before work starts: record the customer PO "
                "number on quotation %s first."
                % (self.customer_id.commercial_partner_id.name, self.name)
            )
        return super()._accept(method, ref)

    # ---- the fulfilment plan -------------------------------------------------
    def _log_handoff(self, kind, record, state="created", note="", lines=None):
        self.ensure_one()
        return (
            self.env["fix.quotation.handoff"]
            .sudo()
            .create(
                {
                    "quotation_id": self.id,
                    "kind": kind,
                    "res_model": record._name if record else False,
                    "res_id": record.id if record else 0,
                    "ref": record.display_name if record else False,
                    "state": state,
                    "note": note or False,
                    "line_ids": [(6, 0, lines.ids)] if lines else False,
                }
            )
        )

    def _branch(self):
        Branch = self.env["fix.branch"].sudo()
        return (
            Branch.search([("operating_unit_id", "=", self.operating_unit_id.id)], limit=1)
            if self.operating_unit_id
            else Branch.browse()
        )

    def _fulfil_deliveries(self):
        lines = self._scope_lines().filtered(
            lambda ln: ln.fulfilment == "delivery" and ln.product_id and ln.quantity > 0
        )
        if not lines:
            return
        ptype = self.picking_type_id
        if not ptype:
            self._log_handoff("delivery", None, "failed", "No delivery operation chosen", lines)
            return
        Picking = self.env["stock.picking"].sudo()
        customer_loc = self.env.ref("stock.stock_location_customers")
        src = ptype.default_location_src_id
        for site in lines.mapped(lambda ln: ln.site_id or self.customer_id):
            group = lines.filtered(lambda ln, s=site: (ln.site_id or self.customer_id) == s)
            try:
                with self.env.cr.savepoint():
                    picking = Picking.create(
                        {
                            "picking_type_id": ptype.id,
                            "partner_id": site.id,
                            "origin": "%s v%d" % (self.name, self.version),
                            "location_id": src.id,
                            "location_dest_id": customer_loc.id,
                            "move_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": ln.product_id.id,
                                        "product_uom_qty": ln.quantity,
                                        "product_uom": ln.product_id.uom_id.id,
                                        "location_id": src.id,
                                        "location_dest_id": customer_loc.id,
                                        "description_picking": ln.description,
                                    },
                                )
                                for ln in group
                            ],
                        }
                    )
                    picking.action_confirm()
                self._log_handoff("delivery", picking, lines=group)
            except (UserError, ValidationError) as exc:
                self._log_handoff(
                    "delivery", None, "failed", str(exc.args[0] if exc.args else exc)[:250], group
                )

    def _fulfil_service_orders(self, contract=None):
        lines = self._scope_lines().filtered(lambda ln: ln.fulfilment == "service_order")
        if self.quote_type == "service" or not lines:
            return
        branch = self._branch()
        Order = self.env["fix.service.order"].sudo()
        with_device = lines.filtered("device_id")
        for device in with_device.mapped("device_id"):
            group = with_device.filtered(lambda ln, d=device: ln.device_id == d)
            if not branch:
                self._log_handoff(
                    "service_order", None, "failed", "No branch for the operating unit", group
                )
                continue
            vals = {
                "device_id": device.id,
                "customer_id": self.customer_id.id,
                "branch_id": branch.id,
                "service_type": "corporate" if self.segment in B2B_SEGMENTS else "onsite",
                "order_category": "amc" if contract else "standard",
                "fault_description": "\n".join(
                    "%s x %g" % (ln.description, ln.quantity or 1.0) for ln in group
                )
                + "\n(quotation %s v%d)" % (self.name, self.version),
            }
            if contract and "contract_id" in Order._fields:
                vals["contract_id"] = contract.id
            try:
                with self.env.cr.savepoint():
                    order = Order.create(vals)
                self._log_handoff("service_order", order, lines=group)
            except (UserError, ValidationError) as exc:
                self._log_handoff(
                    "service_order",
                    None,
                    "failed",
                    str(exc.args[0] if exc.args else exc)[:250],
                    group,
                )
        self._schedule(lines - with_device)

    def _schedule(self, lines):
        """Work with no device or by a third party: a to-do on the quotation
        for whoever plans it, logged as pending."""
        if not lines:
            return
        user = self.create_uid if self.create_uid and self.create_uid.active else self.env.user
        self.sudo().activity_schedule(
            "mail.mail_activity_data_todo",
            date_deadline=fields.Date.context_today(self) + timedelta(days=2),
            summary="Schedule the accepted work of %s" % self.name,
            note="<br/>".join(
                "%s x %g%s"
                % (
                    ln.description,
                    ln.quantity or 1.0,
                    (" @ " + ln.site_id.name) if ln.site_id else "",
                )
                for ln in lines
            ),
            user_id=user.id,
        )
        self._log_handoff(
            "task", None, "pending", "Work to schedule (no device on the line)", lines
        )

    def _fulfil_contract_scope(self, contract):
        if not contract:
            return
        lines = self._scope_lines()
        Scope = self.env["fix.contract.scope.line"].sudo()
        Scope.create(
            [
                {
                    "contract_id": contract.id,
                    "quotation_line_id": ln.id,
                    "line_type": ln.line_type,
                    "product_id": ln.product_id.id or False,
                    "device_id": ln.device_id.id or False,
                    "site_id": ln.site_id.id or False,
                    "description": ln.description,
                    "quantity": ln.quantity,
                    "unit_price": ln.unit_price,
                    "discount_pct": ln.discount_pct,
                    "subtotal": ln.subtotal,
                }
                for ln in lines
            ]
        )
        contract.sudo().write(
            {"quotation_id": self.id, "payment_term_id": self.payment_term_id.id or False}
        )

    def _convert(self):
        self.ensure_one()
        if self.converted_res_id:
            return self.converted_res_model, self.converted_res_id
        if self.quote_type == "project":
            self._fulfil_deliveries()
            self._fulfil_service_orders()
            self._schedule(
                self._scope_lines().filtered(lambda ln: ln.fulfilment in ("schedule", "contract"))
            )
            handoffs = self.handoff_ids
            first = handoffs[:1]
            summary = ", ".join(
                "%d %s" % (len(handoffs.filtered(lambda h, k=k: h.kind == k)), label.lower())
                for k, label in self.env["fix.quotation.handoff"]._fields["kind"].selection
                if handoffs.filtered(lambda h, k=k: h.kind == k)
            )
            self._guarded().write(
                {
                    "converted_res_model": "fix.quotation.handoff",
                    "converted_res_id": first.id or 0,
                    "converted_ref": summary or "nothing to fulfil",
                    "converted_at": fields.Datetime.now(),
                }
            )
            return "fix.quotation.handoff", first.id
        model, res_id = super()._convert()
        target = self.env[model].browse(res_id)
        if self.quote_type == "service":
            self._log_handoff("service_order", target, lines=self._scope_lines())
        elif self.quote_type == "contract":
            self._log_handoff(
                "contract",
                target,
                lines=self._scope_lines().filtered(lambda ln: ln.fulfilment == "contract"),
            )
            self._fulfil_contract_scope(target)
            self._fulfil_deliveries()
            self._fulfil_service_orders(contract=target)
            self._schedule(self._scope_lines().filtered(lambda ln: ln.fulfilment == "schedule"))
        return model, res_id

    # ---- advances -------------------------------------------------------------
    def action_record_advance(self):
        """Record the advance the customer paid as a DRAFT receipt linked to
        the quotation; Finance confirms it (GL), and it is applied to the
        quotation's invoices as they are issued."""
        for rec in self:
            if rec.state not in ("sent", "accepted"):
                raise UserError("An advance is taken on an issued or accepted quotation.")
            amount = rec.advance_entry_amount or 0.0
            method = rec.advance_entry_method_id
            if amount <= 0.0 or not method:
                raise UserError("Enter the advance amount received and how it was paid.")
            if method not in rec.payment_method_ids:
                raise UserError("%s is not a payment method this quotation offers." % method.name)
            if not method.receipt_method:
                raise UserError("%s is not a way to receive money now." % method.name)
            if amount > (rec.amount_total or 0.0) - rec.advance_received + 0.005:
                raise UserError("An advance cannot exceed what the quotation still asks for.")
            receipt = (
                self.env["fix.ar.receipt"]
                .sudo()
                .create(
                    {
                        "company_id": rec.company_id.id,
                        "operating_unit_id": rec.operating_unit_id.id or False,
                        "customer_id": rec.customer_id.commercial_partner_id.id,
                        "currency_id": rec.currency_id.id,
                        "amount": amount,
                        "method": method.receipt_method,
                        "reference": (rec.advance_entry_ref or "%s advance" % rec.name)[:64],
                        "quotation_id": rec.id,
                    }
                )
            )
            if "payment_method_id" in receipt._fields:
                receipt.sudo().write({"payment_method_id": method.id})
            rec._log_handoff(
                "receipt", receipt, "pending", "Advance %.2f by %s" % (amount, method.name)
            )
            rec.write(
                {
                    "advance_entry_amount": 0.0,
                    "advance_entry_method_id": False,
                    "advance_entry_ref": False,
                }
            )
        return True

    def _apply_advances(self, invoice):
        """Apply this quotation's confirmed, unapplied advance receipts to an
        issued invoice, oldest first."""
        self.ensure_one()
        Allocation = self.env["fix.ar.allocation"].sudo()
        residual = invoice.amount_residual if "amount_residual" in invoice._fields else 0.0
        for receipt in self.advance_receipt_ids.sorted("id"):
            if residual <= 0.005:
                break
            if receipt.state != "confirmed" or receipt.unapplied_amount <= 0.005:
                continue
            amount = round(min(receipt.unapplied_amount, residual), 2)
            Allocation.create(
                {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": amount}
            )
            residual = round(residual - amount, 2)
            invoice.message_post(
                body="Advance %s applied: BDT %.2f (quotation %s)."
                % (receipt.name, amount, self.name)
            )


class ResPartnerPo(models.Model):
    _inherit = "res.partner"

    fix_po_required = fields.Boolean(
        string="Requires Its Purchase Order",
        help="Quotations are accepted only with the customer's PO number.",
    )
    fix_po_required_above = fields.Monetary(
        string="PO Required Above (BDT)",
        currency_field="fix_po_currency_id",
        help="Total payable above which the PO is required; 0 = always.",
    )
    fix_po_currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
    )


class FixArReceiptQuotation(models.Model):
    _inherit = "fix.ar.receipt"

    quotation_id = fields.Many2one(
        "fix.quotation", string="Advance For Quotation", index=True, readonly=True
    )


class FixArInvoiceAdvance(models.Model):
    _inherit = "fix.ar.invoice"

    def _fix_quotation_for_advances(self):
        """The accepted quotation an issued invoice bills: a billing-plan
        invoice names its line; a closed service order's invoice its order."""
        self.ensure_one()
        Quote = self.env["fix.quotation"].sudo()
        if self.source_model == "fix.quotation.billing.line" and self.source_ref:
            line = (
                self.env["fix.quotation.billing.line"]
                .sudo()
                .search([("invoice_id", "=", self.id)], limit=1)
            )
            return line.quotation_id
        if self.source_model == "fix.service.order" and self.source_id:
            return Quote.search(
                [("service_order_id", "=", self.source_id), ("state", "=", "accepted")],
                order="accepted_at desc, id desc",
                limit=1,
            )
        return Quote.browse()

    def action_issue(self):
        res = super().action_issue()
        for inv in self.filtered(lambda i: i.state != "draft"):
            quote = inv._fix_quotation_for_advances()
            if quote:
                quote._apply_advances(inv)
        return res

    def from_closed_service_order(self, order, closed_event_at):
        invoice = super().from_closed_service_order(order, closed_event_at)
        if invoice and invoice.state != "draft":
            quote = invoice._fix_quotation_for_advances()
            if quote:
                quote._apply_advances(invoice)
        return invoice


class FixContractScope(models.Model):
    _inherit = "fix.contract"

    quotation_id = fields.Many2one("fix.quotation", string="From Quotation", readonly=True)
    payment_term_id = fields.Many2one("account.payment.term", string="Payment Terms")
    scope_line_ids = fields.One2many(
        "fix.contract.scope.line", "contract_id", string="Contracted Scope"
    )


class FixContractScopeLine(models.Model):
    _name = "fix.contract.scope.line"
    _description = "Contract Scope Line"
    _order = "contract_id, id"

    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="contract_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="contract_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="contract_id.currency_id")
    quotation_line_id = fields.Many2one("fix.quotation.line", readonly=True)
    line_type = fields.Selection(
        lambda self: self.env["fix.quotation.line"]._fields["line_type"].selection,
        string="Type",
    )
    product_id = fields.Many2one("product.product")
    device_id = fields.Many2one("fix.device")
    site_id = fields.Many2one("res.partner", string="Site")
    description = fields.Char(required=True)
    quantity = fields.Float(digits="Product Unit of Measure")
    unit_price = fields.Monetary(currency_field="currency_id")
    discount_pct = fields.Float(string="Discount (%)")
    subtotal = fields.Monetary(string="Amount (excl. VAT)", currency_field="currency_id")

    def write(self, vals):
        if not self.env.su:
            raise UserError("The contracted scope is what the quotation said; amend the contract.")
        return super().write(vals)
