# fix_procurement_capture — M16 second capture audit (2026-11-19).
#
# The first pass (13 Nov) gave every M16 sub-module page a button. Read
# against the specification (FR-PRO-001..038, BRU-PRO-01..20) several of those
# buttons captured a record that lacked what the requirement is about, and one
# record the spec makes a hard rule had no model at all:
#
#   * FR-PRO-001/002 (P0): a requisition did not say where the demand came
#     from (branch request, M15 replenishment, M43 plan, job backorder,
#     project, facilities, IT, marketing), what it refers to, its budget
#     reference, or whether it buys stock, non-stock goods or a service.
#   * FR-PRO-009 (P0): no approved-source list per part. Added as
#     fix.procurement.approved.source: priority, agreed price, MOQ, lead time
#     and validity, approved by a Procurement Approver other than its
#     preparer. It fills an RFQ's invitations and the vendor of a requisition
#     submitted without one.
#   * FR-PRO-011 (P0): an RFQ had no invited suppliers and no response
#     deadline, so it was "issued" to nobody. Opening one now needs both; a bid
#     comes only from an invited supplier, before the deadline; an invitation
#     is never withdrawn once the RFQ is open (FR-PRO-016 audit trail).
#   * FR-PRO-012/013 (P0): a bid carried a price and a lead time only. It now
#     carries the warranty, MOQ, payment terms, incoterm and the supplier's
#     quotation document, all sealed with the price once the RFQ closes.
#   * FR-PRO-017 (P0): a purchase order had no payment terms or incoterm. Both
#     are on the order, pinned with its other terms, carried from the award's
#     bid and onto a change order.
#   * FR-PRO-026 (P0): a goods receipt line recorded no condition or
#     discrepancy. A line received other than in good condition needs a note.
#   * FR-PRO-037 / BRU-PRO-19 (H): no service-entry confirmation. A service or
#     non-stock line is now confirmed by fix.purchase.service.entry, by the
#     requester (never the buyer), with evidence; that is its only receipt, and
#     the three-way match reads it as one.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_procurement_ops import FixProcurementBid
from .fix_requisition import (
    GROUP_APPROVER,
    GROUP_BUYER,
    RECEIVABLE_PO_STATES,
    FixPurchaseOrder,
    bdt_rate,
    has_role,
    over_receipt_ceiling,
    require_role,
)

INCOTERMS = [
    ("exw", "EXW - Ex Works"),
    ("fca", "FCA - Free Carrier"),
    ("fob", "FOB - Free on Board"),
    ("cfr", "CFR - Cost and Freight"),
    ("cif", "CIF - Cost, Insurance and Freight"),
    ("cpt", "CPT - Carriage Paid To"),
    ("cip", "CIP - Carriage and Insurance Paid To"),
    ("dap", "DAP - Delivered at Place"),
    ("dpu", "DPU - Delivered at Place Unloaded"),
    ("ddp", "DDP - Delivered Duty Paid"),
]

DEMAND_SOURCES = [
    ("branch", "Branch Request"),
    ("replenishment", "M15 Replenishment Alert"),
    ("planned_order", "M43 Planned Order"),
    ("job", "Job Backorder"),
    ("project", "Project / Capital"),
    ("facilities", "Facilities"),
    ("it", "IT"),
    ("marketing", "Marketing"),
]
# the demand names the document it comes from (alert, plan, job, project)
SOURCE_REF_NEEDED = {"replenishment", "planned_order", "job", "project"}

PURCHASE_KINDS = [
    ("stock", "Stock Parts / Goods"),
    ("non_stock", "Non-Stock Goods"),
    ("service", "Service"),
]

RECEIPT_CONDITIONS = [
    ("good", "Good"),
    ("damaged", "Damaged"),
    ("wrong_item", "Wrong Item"),
    ("short", "Short (less than the challan)"),
    ("excess", "Excess (more than the challan)"),
]

# the context key with which a confirmed service entry posts its receipt
CTX_SERVICE_ENTRY = "fix_service_entry_post"


# ============================================================ requisition
class FixRequisitionCapture(models.Model):
    _inherit = "fix.requisition"

    demand_source = fields.Selection(
        DEMAND_SOURCES,
        string="Demand Source",
        required=True,
        default="branch",
        tracking=True,
        help="Where the demand comes from (FR-PRO-001).",
    )
    source_ref = fields.Char(
        string="Source Reference",
        help="The alert, planned order, job or project this demand comes from.",
    )
    budget_ref = fields.Char(string="Budget Reference")
    purchase_kind = fields.Selection(
        PURCHASE_KINDS,
        string="What Is Bought",
        required=True,
        default="stock",
        help="A service or non-stock purchase is confirmed by a service entry, not a goods "
        "receipt (BRU-PRO-19).",
    )

    REQ_SOURCE_FIELDS = ("demand_source", "source_ref", "budget_ref", "purchase_kind")

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state in ("converted", "cancelled") for r in self):
            locked |= set(self.REQ_SOURCE_FIELDS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        # a requisition M43 raises from an approved plan is a planned order
        if "demand_plan_id" in self._fields:
            for vals in vals_list:
                if vals.get("demand_plan_id") and not vals.get("demand_source"):
                    vals["demand_source"] = "planned_order"
        return super().create(vals_list)

    # A06 P07: who asked, for which unit and branch, and whether it is stock or
    # a service decide who may approve, receive and confirm it: once submitted
    # they are pinned in the model (the form lock alone was a screen rule; a
    # colleague repointed requested_by to themselves and confirmed the service).
    REQ_IDENTITY = (
        "requested_by",
        "operating_unit_id",
        "branch_id",
        "purchase_kind",
        "company_id",
    )

    def write(self, vals):
        if not self._fix_guard_has_token() and set(self.REQ_SOURCE_FIELDS) & set(vals):
            for rec in self:
                if rec.state in ("converted", "cancelled"):
                    raise UserError(
                        "Requisition %s is %s: where its demand comes from and what it buys "
                        "are part of the record." % (rec.display_name, rec.state)
                    )
        pinned = set(self.REQ_IDENTITY) & set(vals)
        if pinned and not self._fix_guard_has_token():
            for rec in self:
                if rec.state == "draft" and not rec.emergency_state:
                    continue
                changed = [n for n in pinned if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed:
                    raise UserError(
                        "Requisition %s is %s: its %s is fixed once it is submitted."
                        % (
                            rec.display_name,
                            rec.state,
                            ", ".join(rec._fields[n].string.lower() for n in sorted(changed)),
                        )
                    )
        return super().write(vals)

    def _a06_intake_problems(self):
        problems = super()._a06_intake_problems()
        if "demand_plan_id" in self._fields and self.demand_plan_id:
            return problems
        if self.demand_source in SOURCE_REF_NEEDED and not (self.source_ref or "").strip():
            label = dict(DEMAND_SOURCES)[self.demand_source]
            problems.append("the source reference (the %s it comes from)" % label.lower())
        if self.demand_source == "project" and not (self.budget_ref or "").strip():
            problems.append("the budget reference of the project")
        return problems

    def action_submit(self, justification=None):
        """FR-PRO-009: a requisition submitted without a preferred vendor is
        bought from the part's first approved source, when there is one. It
        is filled in before approval, so the approver sees the vendor (a
        vendor changed after approval sends it back to draft)."""
        Source = self.env["fix.procurement.approved.source"]
        for req in self:
            if req.vendor_id or not req.product_id or req.state != "draft":
                continue
            source = Source._sources_for(req.product_id, company=req.company_id)[:1]
            if source:
                req.write({"vendor_id": source.vendor_id.id})
                req.message_post(
                    body="Vendor %s taken from approved source %s (priority %d)."
                    % (source.vendor_id.display_name, source.name, source.priority)
                )
        return super().action_submit(justification=justification)

    def action_convert_to_po(self):
        result = super().action_convert_to_po()
        for req in self:
            order = req.purchase_order_id
            if order and order.state == "draft":
                order._a06_apply_reference_prices()
            if order and req.purchase_kind != "stock":
                order.message_post(
                    body="Requisition %s buys %s: confirm it with a service entry, not a goods "
                    "receipt (BRU-PRO-19)."
                    % (req.display_name, dict(PURCHASE_KINDS)[req.purchase_kind].lower())
                )
        return result


# ======================================================= approved sources
class FixProcurementApprovedSource(models.Model):
    """FR-PRO-009: a supplier approved to supply a part, with its priority,
    agreed price, MOQ and lead time. Approved by a Procurement Approver other
    than its preparer, then fixed; a change is a new row and the old one is
    withdrawn."""

    _name = "fix.procurement.approved.source"
    _description = "Approved Source"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "product_id, priority, agreed_price, id"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    product_id = fields.Many2one("product.product", string="Part", required=True, index=True)
    vendor_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, index=True, ondelete="restrict"
    )
    priority = fields.Integer(required=True, default=1, help="1 = first choice.")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    agreed_price = fields.Monetary(string="Agreed Unit Price", currency_field="currency_id")
    moq = fields.Float(string="Minimum Order Qty", default=1.0)
    lead_time_days = fields.Integer(string="Lead Time (days)")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("withdrawn", "Withdrawn")],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    withdrawn_reason = fields.Char(readonly=True, copy=False)

    SOURCE_TERMS = (
        "product_id",
        "vendor_id",
        "priority",
        "currency_id",
        "agreed_price",
        "moq",
        "lead_time_days",
        "valid_from",
        "valid_to",
        "company_id",
    )

    _priority_positive = models.Constraint("CHECK (priority >= 1)", "Priority starts at 1")
    _price_not_negative = models.Constraint(
        "CHECK (agreed_price IS NULL OR agreed_price >= 0)", "An agreed price cannot be negative"
    )
    _moq_positive = models.Constraint("CHECK (moq > 0)", "The minimum order quantity is positive")
    _dates_ordered = models.Constraint(
        "CHECK (valid_to IS NULL OR valid_to >= valid_from)",
        "An approved source cannot end before it starts",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_at",
            "withdrawn_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.SOURCE_TERMS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_BUYER, "Proposing an approved source")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.approved.source")
                    or "APSRC/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        terms = set(self.SOURCE_TERMS) & set(vals)
        if terms and not self._fix_guard_has_token():
            for rec in self:
                if rec.state != "draft" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in terms
                ):
                    raise UserError(
                        "Approved source %s is %s: its terms are fixed. Withdraw it and propose "
                        "a new one." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def unlink(self):
        if any(r.state != "draft" for r in self):
            raise UserError("An approved or withdrawn source is a record; it cannot be deleted.")
        return super().unlink()

    def action_approve(self):
        Order = self.env["fix.purchase.order"]
        for rec in self:
            require_role(self.env, GROUP_APPROVER, "Approving a source")
            if rec.state != "draft":
                raise UserError("Approve a draft source (%s is %s)." % (rec.name, rec.state))
            if not self.env.su and self.env.user == rec.create_uid:
                raise UserError(
                    "Segregation of duties: you proposed source %s; another Procurement "
                    "Approver approves it." % rec.name
                )
            Order._fix_vendor_gate(rec.vendor_id, "Approving source %s" % rec.name)
            twin = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("state", "=", "approved"),
                    ("company_id", "=", rec.company_id.id),
                    ("product_id", "=", rec.product_id.id),
                    ("vendor_id", "=", rec.vendor_id.id),
                ],
                limit=1,
            )
            if twin:
                raise UserError(
                    "%s is already an approved source of %s (%s). Withdraw it first."
                    % (rec.vendor_id.display_name, rec.product_id.display_name, twin.name)
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_withdraw(self, reason=None):
        for rec in self:
            if not (has_role(self.env, GROUP_BUYER) or has_role(self.env, GROUP_APPROVER)):
                require_role(self.env, GROUP_BUYER, "Withdrawing an approved source")
            if rec.state != "approved":
                raise UserError("Withdraw an approved source (%s is %s)." % (rec.name, rec.state))
            if not (reason or "").strip():
                raise UserError("State why source %s is withdrawn." % rec.name)
            rec._guarded().write({"state": "withdrawn", "withdrawn_reason": reason.strip()})
        return True

    @api.model
    def _sources_for(self, product, company=None, on_date=None):
        """The approved, valid sources of `product`, first choice first."""
        day = on_date or fields.Date.context_today(self)
        domain = [
            ("state", "=", "approved"),
            ("product_id", "=", product.id),
            ("valid_from", "<=", day),
            "|",
            ("valid_to", "=", False),
            ("valid_to", ">=", day),
        ]
        if company:
            domain.append(("company_id", "=", company.id))
        return self.sudo().search(domain, order="priority, agreed_price, id")


# ================================================================ RFQ
class FixProcurementRfqCapture(models.Model):
    _inherit = "fix.procurement.rfq"

    invited_vendor_ids = fields.Many2many(
        "res.partner",
        "fix_procurement_rfq_invited_rel",
        "rfq_id",
        "partner_id",
        string="Invited Suppliers",
        copy=False,
        help="The suppliers asked to quote (FR-PRO-011). Only they can bid. Suppliers can be "
        "added while the RFQ is open, never removed.",
    )
    response_deadline = fields.Date(
        string="Response Deadline",
        help="No bid is received after this day. It can be extended while the RFQ is open.",
    )
    invited_count = fields.Integer(compute="_compute_invited_count", string="Invited")

    @api.depends("invited_vendor_ids")
    def _compute_invited_count(self):
        for rec in self:
            rec.invited_count = len(rec.invited_vendor_ids)

    def write(self, vals):
        before = {}
        guarded = self._fix_guard_has_token()
        if not guarded and {"invited_vendor_ids", "response_deadline"} & set(vals):
            for rec in self:
                if rec.state in ("closed", "awarded"):
                    raise UserError(
                        "RFQ %s is %s: its invitations and deadline are part of the event record."
                        % (rec.name, rec.state)
                    )
                if rec.state == "open":
                    before[rec.id] = set(rec.invited_vendor_ids.ids)
                    if "response_deadline" in vals:
                        new = fields.Date.to_date(vals["response_deadline"])
                        if not new or (rec.response_deadline and new < rec.response_deadline):
                            raise UserError(
                                "RFQ %s is open: its deadline can be extended, never brought "
                                "forward or removed." % rec.name
                            )
        result = super().write(vals)
        for rec in self.filtered(lambda r: r.id in before):
            dropped = before[rec.id] - set(rec.invited_vendor_ids.ids)
            if dropped:
                raise UserError(
                    "RFQ %s is open: an invited supplier cannot be withdrawn (%s)."
                    % (
                        rec.name,
                        ", ".join(self.env["res.partner"].browse(list(dropped)).mapped("name")),
                    )
                )
        return result

    def action_invite_approved_sources(self):
        """Invite every approved, valid source of the RFQ's part."""
        Source = self.env["fix.procurement.approved.source"]
        for rec in self:
            require_role(self.env, GROUP_BUYER, "Inviting suppliers to an RFQ")
            if rec.state not in ("draft", "open"):
                raise UserError(
                    "Invite suppliers to a draft or open RFQ (%s is %s)." % (rec.name, rec.state)
                )
            sources = Source._sources_for(rec.product_id, company=rec.company_id)
            if not sources:
                raise UserError(
                    "%s has no approved source. Record one on Approved Sources, or choose the "
                    "suppliers on the RFQ yourself." % rec.product_id.display_name
                )
            rec.write({"invited_vendor_ids": [(4, v.id) for v in sources.mapped("vendor_id")]})
        return True

    def action_open(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "draft":
                continue
            if not rec.invited_vendor_ids:
                raise UserError(
                    "RFQ %s invites no supplier. Choose the suppliers to quote (or Invite Approved "
                    "Sources) before opening it (FR-PRO-011)." % rec.name
                )
            if not rec.response_deadline:
                raise UserError("RFQ %s needs a response deadline before it opens." % rec.name)
            if rec.response_deadline < today:
                raise UserError(
                    "RFQ %s: the response deadline %s has already passed."
                    % (rec.name, rec.response_deadline)
                )
        return super().action_open()


# ================================================================ bids
class FixProcurementBidCapture(models.Model):
    _inherit = "fix.procurement.bid"

    warranty_months = fields.Integer(string="Warranty (months)")
    moq = fields.Float(string="Minimum Order Qty")
    payment_terms = fields.Char(string="Payment Terms")
    incoterm = fields.Selection(INCOTERMS, string="Incoterm")
    quote_file = fields.Binary(string="Supplier's Quotation", attachment=True, copy=False)
    quote_filename = fields.Char(string="Quotation File Name", copy=False)
    total_price = fields.Monetary(
        string="Total for the RFQ Quantity",
        currency_field="currency_id",
        compute="_compute_total_price",
    )

    BID_FIXED = (
        *FixProcurementBid.BID_FIXED,
        "warranty_months",
        "moq",
        "payment_terms",
        "incoterm",
        "quote_file",
        "quote_filename",
    )

    @api.depends("unit_price", "rfq_id.qty")
    def _compute_total_price(self):
        for bid in self:
            bid.total_price = round((bid.unit_price or 0.0) * (bid.rfq_id.sudo().qty or 0.0), 2)

    @api.model_create_multi
    def create(self, vals_list):
        Rfq = self.env["fix.procurement.rfq"].sudo()
        Partner = self.env["res.partner"].sudo()
        today = fields.Date.context_today(self)
        for vals in vals_list:
            rfq = Rfq.browse(vals.get("rfq_id")).exists()
            if not rfq or rfq.state != "open":
                continue  # the base create refuses it with its own message
            if rfq.response_deadline and today > rfq.response_deadline:
                raise UserError(
                    "RFQ %s closed for responses on %s; no bid is received after the deadline."
                    % (rfq.name, rfq.response_deadline)
                )
            vendor = Partner.browse(vals.get("vendor_id")).exists()
            invited = rfq.invited_vendor_ids.mapped("commercial_partner_id")
            if rfq.invited_vendor_ids and vendor.commercial_partner_id not in invited:
                raise UserError(
                    "%s was not invited to RFQ %s. Only invited suppliers bid (FR-PRO-011); add "
                    "the supplier to the invitations while the RFQ is open."
                    % (vendor.display_name or "This supplier", rfq.name)
                )
        return super().create(vals_list)


# ============================================================ award -> PO
class FixProcurementAwardCapture(models.Model):
    _inherit = "fix.procurement.award"

    def action_create_po(self):
        result = super().action_create_po()
        for rec in self:
            order, bid = rec.purchase_order_id, rec.bid_id.sudo()
            if order and order.state == "draft":
                order._guarded().write(
                    {"payment_terms": bid.payment_terms, "incoterm": bid.incoterm}
                )
        return result


# ======================================================= purchase order
class FixPurchaseOrderCapture(models.Model):
    _inherit = "fix.purchase.order"

    payment_terms = fields.Char(string="Payment Terms")
    incoterm = fields.Selection(INCOTERMS, string="Incoterm")
    service_entry_ids = fields.One2many(
        "fix.purchase.service.entry", "purchase_order_id", string="Service Entries"
    )

    PO_PINNED = (*FixPurchaseOrder.PO_PINNED, "payment_terms", "incoterm")

    # ---- A06 P27: the order price comes from what was agreed --------------
    def _a06_reference_price(self, line):
        """(unit price in the order currency, source text) for `line`: the
        supplier's approved source for the part (cd_vendor_portal puts the M42
        agreed price list first); (None, None) when nothing was agreed."""
        self.ensure_one()
        sources = self.env["fix.procurement.approved.source"]._sources_for(
            line.product_id, company=self.company_id
        )
        vendor = self.vendor_id.commercial_partner_id
        source = sources.filtered(
            lambda s: s.vendor_id.commercial_partner_id == vendor and s.agreed_price
        )[:1]
        if not source:
            return None, None
        price = source.agreed_price
        if source.currency_id != self.currency_id:
            bdt = price * bdt_rate(self.env, source.currency_id, self.company_id)
            price = round(bdt / bdt_rate(self.env, self.currency_id, self.company_id), 6)
        return price, "approved source %s" % source.name

    def _a06_apply_reference_prices(self):
        """A converted requisition's line took its price from the requester's
        estimate; an agreed price for the supplier and part replaces it."""
        for order in self:
            for line in order.line_ids:
                price, source = order._a06_reference_price(line)
                if price is None or abs(price - line.unit_price) < 0.005:
                    continue
                old = line.unit_price
                line.write({"unit_price": price})
                order.message_post(
                    body="%s priced at %s %.2f from the %s (the requisition estimated %.2f)."
                    % (line.product_id.display_name, order.currency_id.name, price, source, old)
                )

    def action_create_change_order(self):
        result = super().action_create_change_order()
        for new in self.browse((result or {}).get("change_order_ids") or []):
            old = new.revision_of_id
            new._guarded().write({"payment_terms": old.payment_terms, "incoterm": old.incoterm})
        return result


class FixPurchaseOrderLineCapture(models.Model):
    _inherit = "fix.purchase.order.line"

    def _fix_needs_service_entry(self) -> bool:
        """BRU-PRO-19: a service, or a line of a non-stock / service
        requisition, is confirmed by a service entry, never a goods receipt."""
        self.ensure_one()
        line = self.sudo()
        if line.product_id.type == "service":
            return True
        return line.order_id.requisition_id.purchase_kind in ("non_stock", "service")


# ============================================================ goods receipt
class FixPurchaseReceiptCapture(models.Model):
    _inherit = "fix.purchase.receipt"

    def action_post(self):
        trusted = self.env.su and self.env.context.get(CTX_SERVICE_ENTRY)
        for rec in self:
            lines = rec.line_ids.filtered(lambda ln: ln.qty_received > 0)
            if not trusted:
                service = lines.filtered(lambda ln: ln.po_line_id._fix_needs_service_entry())
                if service:
                    raise UserError(
                        "BRU-PRO-19: %s on receipt %s is a service or non-stock purchase. It is "
                        "confirmed by a Service Entry from the requester, not a goods receipt."
                        % (", ".join(service.mapped("product_id.display_name")), rec.name)
                    )
            for line in lines:
                if (
                    line.condition
                    and line.condition != "good"
                    and not (line.discrepancy_note or "").strip()
                ):
                    raise UserError(
                        "Receipt %s: %s arrived %s. Describe the discrepancy on the line."
                        % (
                            rec.name,
                            line.product_id.display_name,
                            dict(RECEIPT_CONDITIONS)[line.condition].lower(),
                        )
                    )
        return super().action_post()


class FixPurchaseReceiptLineCapture(models.Model):
    _inherit = "fix.purchase.receipt.line"

    condition = fields.Selection(
        RECEIPT_CONDITIONS, string="Condition", default="good", required=True
    )
    discrepancy_note = fields.Char(string="Discrepancy")


# ============================================================ service entry
class FixPurchaseServiceEntry(models.Model):
    """FR-PRO-037 / BRU-PRO-19: the confirmation that a service (or non-stock
    goods) was delivered, which replaces the goods receipt. Confirmed by the
    requester of the purchase (the cost-centre owner), never by its buyer, with
    evidence; confirming it posts the receipt the three-way match reads."""

    _name = "fix.purchase.service.entry"
    _description = "Service Entry Confirmation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "service_date desc, id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    purchase_order_id = fields.Many2one(
        "fix.purchase.order",
        string="Purchase Order",
        required=True,
        index=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(
        related="purchase_order_id.company_id", store=True, index=True, readonly=True
    )
    operating_unit_id = fields.Many2one(
        related="purchase_order_id.operating_unit_id", store=True, readonly=True
    )
    vendor_id = fields.Many2one(
        related="purchase_order_id.vendor_id", store=True, readonly=True, string="Supplier"
    )
    po_line_id = fields.Many2one(
        "fix.purchase.order.line", string="Order Line", required=True, ondelete="restrict"
    )
    product_id = fields.Many2one(
        related="po_line_id.product_id", store=True, readonly=True, string="Service / Item"
    )
    qty_ordered = fields.Float(related="po_line_id.qty_ordered", string="Ordered")
    qty_done_before = fields.Float(related="po_line_id.qty_received", string="Already Confirmed")
    qty_confirmed = fields.Float(string="Quantity / Milestone Units Delivered", required=True)
    service_period = fields.Char(string="Period or Milestone")
    service_date = fields.Date(
        string="Delivered On", required=True, default=fields.Date.context_today
    )
    description = fields.Text(string="What Was Delivered")
    evidence_file = fields.Binary(string="Evidence (job sheet, report, photos)", attachment=True)
    evidence_filename = fields.Char(string="Evidence File Name")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        required=True,
        default="draft",
        tracking=True,
    )
    confirmed_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True, copy=False)
    confirmed_at = fields.Datetime(readonly=True, copy=False)
    receipt_id = fields.Many2one(
        "fix.purchase.receipt", string="Receipt", readonly=True, copy=False
    )

    _qty_positive = models.Constraint(
        "CHECK (qty_confirmed > 0)", "A service entry confirms a positive quantity"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "confirmed_by_id",
            "confirmed_at",
            "receipt_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {
                "purchase_order_id",
                "po_line_id",
                "qty_confirmed",
                "service_period",
                "service_date",
                "description",
                "evidence_file",
                "evidence_filename",
            }
        return locked

    @api.constrains("po_line_id", "purchase_order_id")
    def _check_line(self):
        for rec in self:
            line = rec.po_line_id.sudo()
            if line.order_id != rec.purchase_order_id:
                raise ValidationError(
                    "Service entry %s: the line is not on purchase order %s."
                    % (rec.name, rec.purchase_order_id.name)
                )
            if not line._fix_needs_service_entry():
                raise ValidationError(
                    "%s on %s is stock goods: it is received on a PO Goods Receipt, not a "
                    "service entry." % (line.product_id.display_name, rec.purchase_order_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.purchase.service.entry") or "SRVE/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        frozen = any(r.state != "draft" for r in self) and set(vals) - {
            "message_main_attachment_id"
        }
        if frozen and not self._fix_guard_has_token():
            raise UserError("A confirmed or cancelled service entry is final.")
        return super().write(vals)

    def unlink(self):
        if any(r.state == "confirmed" for r in self):
            raise UserError("A confirmed service entry is evidence and cannot be deleted.")
        return super().unlink()

    def _confirmers(self):
        """Who confirms: the requester of the purchase (its cost-centre
        owner). A PO raised on a documented no-requisition exception is
        confirmed by a Procurement Approver."""
        self.ensure_one()
        reqs = self.purchase_order_id.sudo()._fix_all_requisitions()  # A06 P40
        return reqs.requested_by.user_id | reqs.submitted_by_id | reqs.create_uid if reqs else None

    def action_confirm(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Confirm a draft service entry (%s is %s)." % (rec.name, rec.state))
            order = rec.purchase_order_id.sudo()
            if order.state not in RECEIVABLE_PO_STATES:
                raise UserError(
                    "Purchase order %s is %s: a service is confirmed against a sent or "
                    "acknowledged order." % (order.name, order.state)
                )
            if not self.env.su:
                if self.env.user in (order.buyer_id | order.create_uid):
                    raise UserError(
                        "Segregation of duties (SOD-02): you bought purchase order %s and cannot "
                        "confirm what it delivered." % order.name
                    )
                confirmers = rec._confirmers()
                if confirmers is None:
                    require_role(
                        self.env, GROUP_APPROVER, "Confirming a service without a requisition"
                    )
                elif self.env.user not in confirmers:
                    raise UserError(
                        "BRU-PRO-19: service entry %s is confirmed by the requester of %s (%s), "
                        "the cost-centre owner."
                        % (
                            rec.name,
                            order.requisition_id.display_name,
                            ", ".join(confirmers.mapped("name")) or "nobody",
                        )
                    )
            if not rec.evidence_file and not (rec.description or "").strip():
                raise UserError(
                    "Service entry %s: attach the evidence or describe what was delivered."
                    % rec.name
                )
            line = rec.po_line_id.sudo()
            ceiling = over_receipt_ceiling(self.env, line.qty_ordered)
            if line.qty_received + rec.qty_confirmed > ceiling + 1e-6:
                raise UserError(
                    "Service entry %s confirms %.2f on top of %.2f already confirmed; %s orders "
                    "%.2f."
                    % (rec.name, rec.qty_confirmed, line.qty_received, order.name, line.qty_ordered)
                )
            receipt = (
                self.env["fix.purchase.receipt"]
                .sudo()
                .create(
                    {
                        "purchase_order_id": order.id,
                        "delivery_note_ref": rec.name,
                        "notes": "Service entry %s%s"
                        % (
                            rec.name,
                            (": %s" % rec.service_period) if rec.service_period else "",
                        ),
                        "line_ids": [
                            (0, 0, {"po_line_id": line.id, "qty_received": rec.qty_confirmed})
                        ],
                    }
                )
            )
            receipt.with_context(**{CTX_SERVICE_ENTRY: True}).action_post()
            # a service is judged by the requester's confirmation, not inspected
            receipt.line_ids._guarded().write({"inspection_required": False})
            receipt._guarded().write({"receiver_id": self.env.uid})
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "confirmed_by_id": self.env.uid,
                    "confirmed_at": fields.Datetime.now(),
                    "receipt_id": receipt.id,
                }
            )
            order.message_post(
                body="Service entry %s confirmed %.2f of %s by %s."
                % (rec.name, rec.qty_confirmed, line.product_id.display_name, self.env.user.name)
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft service entry is cancelled (%s is %s)." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "cancelled"})
        return True
