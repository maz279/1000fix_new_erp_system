# fix_procurement_ops — M16: RFQ sourcing events with sealed bids and awards,
# blanket agreements, expediting and inspection outcomes. The requisition and
# PO themselves are in fix_requisition.py, the PO goods receipt in
# fix_purchase_receipt.py. The module loads before cd_inventory, so references
# use product.product (the basis of the PO lines), never fix.spare.part.
#
# A06 audit (2026-11-03), M16-5/7/9/10 and R7: bids were accepted on draft and
# closed RFQs, re-priced after close and readable by every user while open; an
# award went to a non-lowest bid with no rationale, on an open RFQ, twice, to
# an unregistered vendor's expired bid and on one bid (live: to the company's
# own partner record); a blanket cap was decorative; inspection outcomes were
# typed and editable after confirmation; every state was writable. Now each
# state moves only by its action (fix.guarded.mixin) and:
#   - bids are sealed until close (record rule), received only while the RFQ is
#     open, and fixed once it closes;
#   - an award goes to the lowest compliant bid, or carries a rationale that
#     a Procurement Approver other than the evaluator decides; fewer bids than
#     the minimum need a recorded exception decided the same way; one live
#     award per RFQ; never to the company's own partner; the PO is raised
#     from the award at no more than the awarded price;
#   - a blanket is activated by an approver, its cap and window fixed while
#     active, consumed only by call-offs linked to it, and expires by cron;
#   - an inspection belongs to a receipt line, its outcome is derived from
#     the quantities, and it is final once confirmed.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

from .fix_requisition import (
    GROUP_APPROVER,
    GROUP_BUYER,
    GROUP_RECEIVER,
    ISSUED_PO_STATES,
    bdt_rate,
    float_param,
    has_role,
    require_role,
)

# BRU-PRO-06: minimum compliant quotations for an award, and the value at or
# below which a single quotation suffices. Business decisions (A06 §7 B5):
# defaults 3 and 0 (every award needs three quotes or a recorded exception).
PARAM_MIN_BIDS = "cd_requisition.rfq_min_bids"
PARAM_COMPETITIVE_THRESHOLD = "cd_requisition.rfq_competitive_threshold"
# A06 D8 (owner decision 20 Nov 2026): three quotes above BDT 50,000.
DEFAULT_COMPETITIVE_THRESHOLD = 50000.0


class FixApprovalMatrixProcurement(models.Model):
    """M16 decision domains on the M63 DoA register."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("purchase_order", "Purchase Order")],
        ondelete={"purchase_order": "cascade"},
    )


class FixProcurementRfq(models.Model):
    _name = "fix.procurement.rfq"
    _description = "RFQ Event"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    description = fields.Char(required=True)
    requisition_id = fields.Many2one(
        "fix.requisition",
        string="Source Requisition",
        index=True,
        help="The approved requisition this sourcing event buys for; the award's PO converts it.",
    )
    # FR-PRO-006 (13 Nov 2026): one sourcing event for the same part requested
    # by several branches. The RFQ buys their total; the award's PO converts
    # every one of them, one line each, so each branch keeps its own line.
    requisition_ids = fields.Many2many(
        "fix.requisition",
        "fix_procurement_rfq_requisition_rel",
        "rfq_id",
        "requisition_id",
        string="Consolidated Requisitions",
        copy=False,
        help="Approved, unconverted requisitions for this product, from any branch. "
        "The RFQ quantity is their total.",
    )
    product_id = fields.Many2one("product.product", string="Product", required=True)
    qty = fields.Float(string="Quantity", default=1.0)
    required_by = fields.Date(string="Required By")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    target_price = fields.Monetary(string="Target Price", currency_field="currency_id")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open for Bids"),
            ("closed", "Closed"),
            ("awarded", "Awarded"),
        ],
        required=True,
        default="draft",
    )
    opened_at = fields.Datetime(readonly=True, copy=False)
    closed_at = fields.Datetime(readonly=True, copy=False)
    bid_ids = fields.One2many("fix.procurement.bid", "rfq_id", string="Bids")
    notes = fields.Text()

    RFQ_FIXED = ("product_id", "qty", "currency_id", "requisition_id", "requisition_ids")
    # an RFQ in these states still has its requisitions out to tender
    SOURCING_STATES = ("draft", "open", "closed")

    _qty_positive = models.Constraint("CHECK (qty > 0)", "RFQ quantity must be positive")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "opened_at", "closed_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.RFQ_FIXED)
        return locked

    def _sourced_requisitions(self):
        """Every requisition this event buys for: the single source and the
        consolidated ones."""
        self.ensure_one()
        return (self.requisition_id | self.requisition_ids).sudo()

    def _check_consolidation(self):
        """FR-PRO-006: only approved, unconverted requisitions for this RFQ's
        product, each out to tender on one live RFQ at a time."""
        for rec in self:
            reqs = rec.requisition_ids.sudo()
            if not reqs:
                continue
            for req in reqs:
                if req.state != "approved" or req.purchase_order_id:
                    raise UserError(
                        "Requisition %s is %s: only approved requisitions not yet converted "
                        "to a PO can be consolidated." % (req.display_name, req.state)
                    )
                if req.product_id != rec.product_id:
                    raise UserError(
                        "Requisition %s asks for %s, not %s: a consolidated RFQ buys one part."
                        % (
                            req.display_name,
                            req.product_id.display_name or "no product",
                            rec.product_id.display_name,
                        )
                    )
            busy = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("state", "in", self.SOURCING_STATES),
                    "|",
                    ("requisition_ids", "in", reqs.ids),
                    ("requisition_id", "in", reqs.ids),
                ],
                limit=1,
            )
            if busy:
                raise UserError(
                    "RFQ %s is already sourcing %s."
                    % (
                        busy.name,
                        ", ".join((busy._sourced_requisitions() & reqs).mapped("display_name")),
                    )
                )
            total = sum(reqs.mapped("qty")) + (
                rec.requisition_id.sudo().qty
                if rec.requisition_id and rec.requisition_id not in reqs
                else 0.0
            )
            if total > 0 and abs((rec.qty or 0.0) - total) > 1e-6:
                rec._guarded().write({"qty": total})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.rfq") or "RFQ/New"
                )
        records = super().create(vals_list)
        records.filtered("requisition_ids")._check_consolidation()
        return records

    def write(self, vals):
        fixed = set(self.RFQ_FIXED) & set(vals)
        if fixed and not self._fix_guard_has_token():
            for rec in self:
                if rec.state != "draft" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in fixed
                ):
                    raise UserError(
                        "RFQ %s is %s: what is being bought is fixed once bids are invited."
                        % (rec.name, rec.state)
                    )
        res = super().write(vals)
        if {"requisition_ids", "requisition_id", "product_id", "qty"} & set(vals):
            self.filtered("requisition_ids")._check_consolidation()
        return res

    def action_open(self):
        for rec in self:
            require_role(self.env, GROUP_BUYER, "Opening an RFQ")
            if rec.state != "draft":
                raise UserError("Open a draft RFQ")
            rec._guarded().write({"state": "open", "opened_at": fields.Datetime.now()})

    def action_close(self):
        for rec in self:
            require_role(self.env, GROUP_BUYER, "Closing an RFQ")
            if rec.state != "open":
                raise UserError("Close an open RFQ")
            if not rec.sudo().bid_ids:
                raise UserError("An RFQ cannot close without at least one bid")
            rec._a06_check_deadline_passed()
            rec._guarded().write({"state": "closed", "closed_at": fields.Datetime.now()})

    def _a06_check_deadline_passed(self):
        """A06 P22: the bid window closes at its deadline, not when a buyer who
        has seen one price chooses; before it, only once every invited
        supplier has answered."""
        self.ensure_one()
        deadline = self.response_deadline if "response_deadline" in self._fields else None
        if not deadline or fields.Date.context_today(self) > deadline:
            return
        invited = self.invited_vendor_ids.mapped("commercial_partner_id")
        answered = self.sudo().bid_ids.mapped("vendor_id.commercial_partner_id")
        if invited and not (invited - answered):
            return
        raise UserError(
            "RFQ %s is open for bids until %s and %d invited supplier(s) have not answered: "
            "it closes after the deadline." % (self.name, deadline, len(invited - answered))
        )

    @api.model
    def _cron_close_due_rfqs(self):
        """A06 P22: an open RFQ past its response deadline closes by itself
        (with at least one bid; one without stays open for the buyer to act)."""
        today = fields.Date.context_today(self)
        due = self.sudo().search(
            [
                ("state", "=", "open"),
                ("response_deadline", "!=", False),
                ("response_deadline", "<", today),
            ]
        )
        closed = self.browse()
        for rec in due.filtered("bid_ids"):
            rec._guarded().write({"state": "closed", "closed_at": fields.Datetime.now()})
            closed |= rec
        return closed


class FixProcurementBid(models.Model):
    _name = "fix.procurement.bid"
    _description = "Supplier Bid"
    _inherit = ["fix.guarded.mixin"]
    _order = "rfq_id, unit_price"

    name = fields.Char(required=True, default="New")
    rfq_id = fields.Many2one(
        "fix.procurement.rfq", string="RFQ", required=True, ondelete="cascade", index=True
    )
    vendor_id = fields.Many2one("res.partner", string="Vendor", required=True, ondelete="restrict")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id", required=True)
    # A06 P03 / D5: bids in different currencies are compared in BDT, at the
    # rate of the day the bid was received; the lowest bid, the competitive
    # threshold and the three-quote rule read this, never the raw price.
    unit_price_bdt = fields.Float(
        string="Unit Price (BDT)",
        digits=(16, 2),
        compute="_compute_unit_price_bdt",
        store=True,
        help="The bid price converted at the rate of the day it was received.",
    )
    lead_time_days = fields.Integer(string="Lead Time (days)", default=7)
    valid_until = fields.Date()
    received_at = fields.Datetime(readonly=True, copy=False, default=fields.Datetime.now)
    state = fields.Selection(
        [("received", "Received"), ("awarded", "Awarded"), ("lost", "Lost")],
        required=True,
        default="received",
    )
    notes = fields.Char()

    BID_FIXED = (
        "rfq_id",
        "vendor_id",
        "currency_id",
        "unit_price",
        "lead_time_days",
        "valid_until",
    )

    _price_positive = models.Constraint("CHECK (unit_price > 0)", "Bid price must be positive")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "received_at", "unit_price_bdt"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(b.rfq_id.state != "open" for b in self):
            locked |= set(self.BID_FIXED)
        return locked

    @api.depends("unit_price", "currency_id", "received_at", "rfq_id.company_id")
    def _compute_unit_price_bdt(self):
        for bid in self:
            company = bid.rfq_id.sudo().company_id or self.env.company
            # the Dhaka business day the bid arrived (received_at is UTC)
            day = (
                fields.Datetime.context_timestamp(bid, bid.received_at).date()
                if bid.received_at
                else None
            )
            rate = bdt_rate(self.env, bid.currency_id, company, day)
            bid.unit_price_bdt = round((bid.unit_price or 0.0) * rate, 2)

    @api.model_create_multi
    def create(self, vals_list):
        Rfq = self.env["fix.procurement.rfq"].sudo()
        for vals in vals_list:
            rfq = Rfq.browse(vals.get("rfq_id")).exists()
            if not rfq or rfq.state != "open":
                raise UserError(
                    "A bid is received only while its RFQ is open for bids (RFQ %s is %s)."
                    % (rfq.name or "?", rfq.state or "missing")
                )
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.bid") or "BID/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        fixed = set(self.BID_FIXED) & set(vals)
        if fixed and not self._fix_guard_has_token():
            for rec in self:
                if rec.sudo().rfq_id.state != "open" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in fixed
                ):
                    raise UserError(
                        "Bid %s is sealed: its RFQ is %s, so the price, vendor and terms are "
                        "final." % (rec.name, rec.sudo().rfq_id.state)
                    )
        return super().write(vals)


class FixProcurementAward(models.Model):
    """The award decision: one live award per RFQ, to the lowest compliant
    bid or with a rationale a second person approves."""

    _name = "fix.procurement.award"
    _description = "Award Decision"
    _inherit = ["fix.guarded.mixin"]
    _order = "decided_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rfq_id = fields.Many2one(
        "fix.procurement.rfq", string="RFQ", required=True, ondelete="restrict", index=True
    )
    bid_id = fields.Many2one(
        "fix.procurement.bid", string="Winning Bid", required=True, ondelete="restrict"
    )
    decided_on = fields.Date(required=True, default=fields.Date.context_today)
    rationale = fields.Char(help="Mandatory when the award is not to the lowest compliant bid.")
    exception_reason = fields.Char(
        string="Bid-Count Exception",
        help="Mandatory when fewer compliant bids than the minimum were received.",
    )
    state = fields.Selection(
        [("proposed", "Proposed"), ("decided", "Decided"), ("cancelled", "Cancelled")],
        required=True,
        default="proposed",
    )
    lowest_bid_id = fields.Many2one(
        "fix.procurement.bid", string="Lowest Compliant Bid", readonly=True, copy=False
    )
    is_lowest = fields.Boolean(string="Lowest Compliant", readonly=True, copy=False)
    compliant_bid_count = fields.Integer(readonly=True, copy=False)
    min_bids = fields.Integer(string="Minimum Bids", readonly=True, copy=False)
    needs_approval = fields.Boolean(readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_at = fields.Datetime(readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    purchase_order_id = fields.Many2one("fix.purchase.order", readonly=True, copy=False)
    cancel_reason = fields.Char(readonly=True, copy=False)

    AWARD_GUARDED = {
        "state",
        "lowest_bid_id",
        "is_lowest",
        "compliant_bid_count",
        "min_bids",
        "needs_approval",
        "decided_by_id",
        "decided_at",
        "approved_by_id",
        "purchase_order_id",
        "cancel_reason",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.AWARD_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"rfq_id", "bid_id", "decided_on"}
            if any(r.state != "proposed" for r in self):
                locked |= {"rationale", "exception_reason"}
        return locked

    # ---- compliance -------------------------------------------------------
    def _a06_bid_problems(self, bid):
        """Why `bid` cannot win: expired, the company's own partner, or a
        vendor M42 has not activated."""
        bid = bid.sudo()
        problems = []
        today = fields.Date.context_today(self)
        if bid.valid_until and bid.valid_until < today:
            problems.append("the bid expired on %s" % bid.valid_until)
        own = self.env["res.company"].sudo().search([]).mapped("partner_id.commercial_partner_id")
        if bid.vendor_id.commercial_partner_id in own:
            problems.append("the bidder is the company's own partner record")
        problems += self.env["fix.purchase.order"]._fix_vendor_blockers(bid.vendor_id)
        return problems

    def _a06_validate_proposal(self):
        self.ensure_one()
        rfq, bid = self.rfq_id.sudo(), self.bid_id.sudo()
        if bid.rfq_id != rfq:
            raise UserError("The winning bid must belong to the awarded RFQ")
        if rfq.state != "closed":
            raise UserError(
                "Award after the bid window closes (RFQ %s is %s)." % (rfq.name, rfq.state)
            )
        live = self.sudo().search_count(
            [
                ("rfq_id", "=", rfq.id),
                ("state", "in", ("proposed", "decided")),
                ("id", "!=", self.id),
            ]
        )
        if live:
            raise UserError(
                "RFQ %s already has a live award. Cancel it before proposing another." % rfq.name
            )
        problems = self._a06_bid_problems(bid)
        if problems:
            raise UserError("Bid %s cannot be awarded: %s." % (bid.name, "; ".join(problems)))
        compliant = rfq.bid_ids.filtered(lambda b: not self._a06_bid_problems(b))
        # A06 P03: ranked, thresholded and counted in BDT, whatever the bid currency
        lowest = compliant.sorted(lambda b: (b.unit_price_bdt, b.id))[:1]
        is_lowest = bid.unit_price_bdt <= lowest.unit_price_bdt + 0.005
        threshold = float_param(
            self.env, PARAM_COMPETITIVE_THRESHOLD, DEFAULT_COMPETITIVE_THRESHOLD
        )
        value = round((bid.unit_price_bdt or 0.0) * (rfq.qty or 0.0), 2)
        min_bids = 1 if value <= threshold else int(float_param(self.env, PARAM_MIN_BIDS, 3))
        if not is_lowest and not (self.rationale or "").strip():
            raise UserError(
                "BRU-PRO-07: bid %s (BDT %.2f) is not the lowest compliant bid (%s at BDT %.2f). "
                "Record the rationale; a Procurement Approver other than you decides it."
                % (bid.name, bid.unit_price_bdt, lowest.name, lowest.unit_price_bdt)
            )
        if len(compliant) < min_bids and not (self.exception_reason or "").strip():
            raise UserError(
                "BRU-PRO-06: RFQ %s has %d compliant bid(s); %d are required at BDT %.2f. "
                "Record the exception (e.g. single source); a Procurement Approver decides it."
                % (rfq.name, len(compliant), min_bids, value)
            )
        needs = (not is_lowest) or len(compliant) < min_bids
        self._guarded().write(
            {
                "lowest_bid_id": lowest.id,
                "is_lowest": is_lowest,
                "compliant_bid_count": len(compliant),
                "min_bids": min_bids,
                "needs_approval": needs,
            }
        )
        return needs

    def _a06_apply_decision(self):
        self.ensure_one()
        rfq = self.rfq_id.sudo()
        losers = rfq.bid_ids.filtered(lambda b, won=self.bid_id: b != won)
        losers._guarded().write({"state": "lost"})
        # A06 P23 (FR-PRO-014): every bidder hears the outcome
        for lost in losers:
            partner = lost.vendor_id.commercial_partner_id.sudo()
            partner.message_post(
                body="RFQ %s was awarded to another bid; your bid %s was not successful."
                % (rfq.name, lost.name),
                partner_ids=partner.ids,
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
        self.bid_id.sudo()._guarded().write({"state": "awarded"})
        rfq._guarded().write({"state": "awarded"})
        self._guarded().write(
            {
                "state": "decided",
                "decided_by_id": self.env.uid,
                "decided_at": fields.Datetime.now(),
                "approved_by_id": self.env.uid if self.needs_approval else False,
            }
        )
        publish(
            self.env,
            "rfq.awarded",
            "fix.procurement.award",
            self.id,
            {
                "rfq": rfq.name,
                "bid": self.bid_id.name,
                "vendor_id": self.bid_id.vendor_id.id,
                "unit_price": self.bid_id.unit_price,
                "lowest": self.is_lowest,
            },
        )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_BUYER, "Proposing an award")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.award") or "AWRD/New"
                )
        # A refused proposal leaves nothing behind (no orphan "live" award).
        with self.env.cr.savepoint():
            records = super().create(vals_list)
            for rec in records:
                if not rec._a06_validate_proposal():
                    rec._a06_apply_decision()
        return records

    def write(self, vals):
        if not self._fix_guard_has_token():
            if {"rfq_id", "bid_id"} & set(vals) and any(
                rec._fix_guard_differs(n, vals[n], rec[n])
                for rec in self
                for n in {"rfq_id", "bid_id"} & set(vals)
            ):
                raise UserError(
                    "An award's RFQ and winning bid are fixed; cancel it and propose again."
                )
            if {"rationale", "exception_reason"} & set(vals) and any(
                r.state != "proposed" for r in self
            ):
                raise UserError("A decided award's rationale is part of the record and is final.")
        return super().write(vals)

    def unlink(self):
        if any(r.state == "decided" for r in self):
            raise UserError("A decided award is evidence and cannot be deleted; cancel it.")
        return super().unlink()

    def action_decide(self):
        """Decide a proposed award. One that is not to the lowest compliant
        bid, or rests on fewer bids than the minimum, is decided by a
        Procurement Approver who did not propose it (the evaluator)."""
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Award %s is %s." % (rec.name, rec.state))
            if rec.needs_approval:
                require_role(self.env, GROUP_APPROVER, "Deciding this award")
                if not self.env.su and self.env.user == rec.create_uid:
                    raise UserError(
                        "Segregation of duties: you proposed award %s; another Procurement "
                        "Approver decides it." % rec.name
                    )
            else:
                require_role(self.env, GROUP_BUYER, "Deciding an award")
            problems = rec._a06_bid_problems(rec.bid_id)
            if problems:
                raise UserError(
                    "Bid %s cannot be awarded: %s." % (rec.bid_id.name, "; ".join(problems))
                )
            rec._a06_apply_decision()
        return True

    def action_cancel(self, reason=None):
        for rec in self:
            if rec.state == "cancelled":
                raise UserError("Award %s is already cancelled." % rec.name)
            if not (reason or "").strip():
                raise UserError("State why award %s is cancelled." % rec.name)
            if rec.state == "decided":
                if rec.purchase_order_id and rec.purchase_order_id.state != "cancelled":
                    raise UserError(
                        "Award %s has PO %s; cancel the PO first."
                        % (rec.name, rec.purchase_order_id.name)
                    )
                require_role(self.env, GROUP_APPROVER, "Cancelling a decided award")
                rfq = rec.rfq_id.sudo()
                rfq.bid_ids._guarded().write({"state": "received"})
                rfq._guarded().write({"state": "closed"})
            else:
                require_role(self.env, GROUP_BUYER, "Cancelling an award proposal")
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason.strip()})
        return True

    def action_create_po(self):
        """Raise the PO from the decided award, at the awarded price and the
        RFQ quantity; it converts the RFQ's approved requisition when there is
        one, and is approved like any PO before it is sent."""
        Order = self.env["fix.purchase.order"]
        for rec in self:
            require_role(self.env, GROUP_BUYER, "Raising a PO from an award")
            if rec.state != "decided":
                raise UserError(
                    "Raise the PO from a decided award (%s is %s)." % (rec.name, rec.state)
                )
            if rec.purchase_order_id and rec.purchase_order_id.state != "cancelled":
                raise UserError(
                    "Award %s already has PO %s." % (rec.name, rec.purchase_order_id.name)
                )
            rfq, bid = rec.rfq_id.sudo(), rec.bid_id.sudo()
            Order._fix_vendor_gate(bid.vendor_id, "Raising a PO from award %s" % rec.name)
            reqs = rfq._sourced_requisitions()
            for one in reqs:
                if one.state != "approved" or one.purchase_order_id:
                    raise UserError(
                        "Requisition %s behind RFQ %s is %s; it cannot be converted by this award."
                        % (one.display_name, rfq.name, one.state)
                    )
                one._dofa_assert_approved("Converting requisition %s" % one.display_name)
            # the PO's own requisition (BRU-PRO-01) is the single source, else
            # the first consolidated one; every one of them is converted below
            req = rfq.requisition_id or reqs[:1]
            if len(reqs) > 1:
                # FR-PRO-006: one line per requisition, so each branch keeps
                # its quantity and its own delivery on the order
                lines = [
                    (
                        0,
                        0,
                        {
                            "product_id": rfq.product_id.id,
                            "description": "%s · %s"
                            % (one.branch_id.name or "No branch", one.description),
                            "qty_ordered": one.qty,
                            "unit_price": bid.unit_price,
                        },
                    )
                    for one in reqs
                ]
            else:
                lines = [
                    (
                        0,
                        0,
                        {
                            "product_id": rfq.product_id.id,
                            "description": rfq.description,
                            "qty_ordered": rfq.qty,
                            "unit_price": bid.unit_price,
                        },
                    )
                ]
            branches = reqs.mapped("branch_id")
            ou = (
                req.operating_unit_id if req else False
            ) or self.env.user.default_operating_unit_id
            if not ou:
                ou = self.env["operating.unit"].search(
                    [("company_id", "=", rec.company_id.id)], limit=1
                )
            order = Order._guarded().create(
                {
                    "operating_unit_id": ou.id,
                    # several branches: delivered per line, no single branch
                    "branch_id": branches.id if len(branches) == 1 else False,
                    "vendor_id": bid.vendor_id.id,
                    "currency_id": bid.currency_id.id,
                    "award_id": rec.id,
                    "requisition_id": req.id if req else False,
                    "dofa_justification": (req.dofa_justification if req else False)
                    or "Award %s on RFQ %s: %s"
                    % (rec.name, rfq.name, rec.rationale or "lowest compliant bid"),
                    "line_ids": lines,
                }
            )
            if reqs:
                reqs._guarded().write({"state": "converted", "purchase_order_id": order.id})
                order._guarded().write({"source_requisition_ids": [(6, 0, reqs.ids)]})
            rec._guarded().write({"purchase_order_id": order.id})
        return True


class FixProcurementBlanket(models.Model):
    _name = "fix.procurement.blanket"
    _description = "Blanket Agreement"
    _inherit = ["fix.guarded.mixin"]
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    vendor_id = fields.Many2one("res.partner", string="Vendor", required=True, ondelete="restrict")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    cap_amount = fields.Monetary(string="Cap Amount", currency_field="currency_id")
    consumed_amount = fields.Monetary(
        string="Called Off",
        currency_field="currency_id",
        compute="_compute_consumed",
        help="Issued purchase orders linked to this agreement (drafts and cancellations excluded).",
    )
    remaining_amount = fields.Monetary(
        string="Remaining", currency_field="currency_id", compute="_compute_consumed"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    activated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    activated_at = fields.Datetime(readonly=True, copy=False)
    terms_changed_by_id = fields.Many2one(
        "res.users",
        string="Terms Last Changed By",
        readonly=True,
        copy=False,
        help="Never the one who activates the agreement.",
    )
    order_ids = fields.One2many("fix.purchase.order", "blanket_id", string="Call-Off Orders")

    BLANKET_TERMS = ("vendor_id", "cap_amount", "valid_from", "valid_to", "currency_id")

    _dates_ordered = models.Constraint(
        "CHECK (valid_to >= valid_from)", "The blanket end date cannot precede its start"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_by_id",
            "activated_at",
            "terms_changed_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.BLANKET_TERMS)
        return locked

    def _consumed_amount(self, exclude=None):
        """What the issued call-offs consumed, in the agreement's currency
        (A06 P39: a call-off in another currency is converted at its stamped
        rate, never added as it stands; a change order being sent replaces its
        original, so the original is not counted twice)."""
        self.ensure_one()
        orders = (
            self.env["fix.purchase.order"]
            .sudo()
            .search([("blanket_id", "=", self.id), ("state", "in", ISSUED_PO_STATES)])
        )
        if exclude:
            exclude = exclude.sudo()
            orders -= exclude | exclude.mapped("revision_of_id")
        return round(sum(self._a06_in_cap_currency(o, o.amount_total) for o in orders), 2)

    def _a06_in_cap_currency(self, order, amount):
        """`amount` of `order` in this agreement's currency."""
        self.ensure_one()
        if order.currency_id == self.currency_id:
            return amount or 0.0
        bdt = (amount or 0.0) * order._fix_rate_bdt()
        rate = bdt_rate(self.env, self.currency_id, self.company_id)
        return round(bdt / rate, 2) if rate else 0.0

    @api.depends("cap_amount", "order_ids.state", "order_ids.amount_total")
    def _compute_consumed(self):
        for rec in self:
            consumed = rec._consumed_amount() if rec.id else 0.0
            rec.consumed_amount = consumed
            rec.remaining_amount = round((rec.cap_amount or 0.0) - consumed, 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.blanket") or "BLKT/New"
                )
        records = super().create(vals_list)
        if not self.env.su:
            records._guarded().write({"terms_changed_by_id": self.env.uid})
        return records

    def write(self, vals):
        terms = set(self.BLANKET_TERMS) & set(vals)
        changed = self.browse()
        if terms and not self._fix_guard_has_token():
            for rec in self:
                if not any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in terms):
                    continue
                if rec.state != "draft":
                    raise UserError(
                        "Blanket agreement %s is %s: its vendor, cap and validity are fixed. "
                        "Revise it (back to draft, re-approved) to change them."
                        % (rec.name, rec.state)
                    )
                changed |= rec
        result = super().write(vals)
        if changed and not self.env.su:
            changed._guarded().write({"terms_changed_by_id": self.env.uid})
        return result

    def action_activate(self):
        """A Procurement Approver who neither created nor last changed the
        terms activates the agreement."""
        for rec in self:
            require_role(self.env, GROUP_APPROVER, "Activating a blanket agreement")
            if rec.state != "draft":
                raise UserError("Activate a draft agreement (%s is %s)." % (rec.name, rec.state))
            if not self.env.su and self.env.user in (rec.create_uid | rec.terms_changed_by_id):
                raise UserError(
                    "Segregation of duties: you created or changed blanket agreement %s; another "
                    "approver activates it." % rec.name
                )
            if (rec.cap_amount or 0.0) <= 0:
                raise UserError("Blanket agreement %s needs a positive cap." % rec.name)
            if rec.valid_to < fields.Date.context_today(rec):
                raise UserError("Blanket agreement %s ended on %s." % (rec.name, rec.valid_to))
            self.env["fix.purchase.order"]._fix_vendor_gate(
                rec.vendor_id, "Activating blanket agreement %s" % rec.name
            )
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                }
            )
        return True

    def action_revise(self):
        for rec in self:
            require_role(self.env, GROUP_BUYER, "Revising a blanket agreement")
            if rec.state != "active":
                raise UserError("Revise an active agreement (%s is %s)." % (rec.name, rec.state))
            rec._guarded().write(
                {"state": "draft", "activated_by_id": False, "activated_at": False}
            )
        return True

    def action_cancel(self):
        for rec in self:
            if not (has_role(self.env, GROUP_BUYER) or has_role(self.env, GROUP_APPROVER)):
                require_role(self.env, GROUP_BUYER, "Cancelling a blanket agreement")
            if rec.state == "cancelled":
                raise UserError("Blanket agreement %s is already cancelled." % rec.name)
            rec._guarded().write({"state": "cancelled"})
        return True

    @api.model
    def _cron_expire_blankets(self):
        today = fields.Date.context_today(self)
        expired = self.sudo().search([("state", "=", "active"), ("valid_to", "<", today)])
        expired._guarded().write({"state": "expired"})
        return expired


class FixProcurementExpedite(models.Model):
    _name = "fix.procurement.expedite"
    _description = "Expediting Case"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    purchase_order_id = fields.Many2one(
        "fix.purchase.order",
        string="Purchase Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    reason = fields.Char(required=True)
    promised_date = fields.Date()
    follow_up_date = fields.Date(readonly=True)
    resolved_on = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("chased", "Chased"), ("resolved", "Resolved")],
        required=True,
        default="open",
    )
    notes = fields.Text()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "follow_up_date", "resolved_on"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.expedite") or "EXPD/New"
                )
        return super().create(vals_list)

    def action_chase(self):
        for rec in self:
            require_role(self.env, GROUP_BUYER, "Chasing a vendor")
            if rec.state != "open":
                raise UserError("Chase an open case")
            rec._guarded().write(
                {"state": "chased", "follow_up_date": fields.Date.context_today(self)}
            )

    def action_resolve(self, note=None):
        for rec in self:
            require_role(self.env, GROUP_BUYER, "Resolving an expediting case")
            if rec.state == "resolved":
                raise UserError("This case is already resolved")
            text = (note or "").strip()
            if not text and not (rec.notes or "").strip():
                raise UserError("Record how case %s was resolved." % rec.name)
            vals = {"state": "resolved", "resolved_on": fields.Date.context_today(self)}
            if text:
                vals["notes"] = ((rec.notes or "") + "\n" + text).strip()
            rec._guarded().write(vals)


class FixProcurementInspection(models.Model):
    """The inspection outcome of a receipt line (BRU-PRO-11). The accepted
    quantity feeds the receipt line, and only accepted goods are matchable."""

    _name = "fix.procurement.inspection"
    _description = "Goods Inspection Outcome"
    _inherit = ["fix.guarded.mixin"]
    _order = "inspected_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    receipt_line_id = fields.Many2one(
        "fix.purchase.receipt.line",
        string="Receipt Line",
        index=True,
        ondelete="restrict",
        help="The goods receipt line this inspection judges.",
    )
    purchase_order_id = fields.Many2one(
        related="receipt_line_id.receipt_id.purchase_order_id",
        store=True,
        readonly=True,
        string="Purchase Order",
    )
    receipt_ref = fields.Char(string="Receipt Reference")
    product_id = fields.Many2one("product.product", string="Product", required=True)
    qty_received = fields.Float(string="Received")
    qty_accepted = fields.Float(string="Accepted")
    qty_rejected = fields.Float(string="Rejected", compute="_compute_rejected", store=True)
    outcome = fields.Selection(
        [("accepted", "Accepted"), ("partial", "Partially Accepted"), ("rejected", "Rejected")],
        compute="_compute_rejected",
        store=True,
        help="Derived from the quantities, never typed.",
    )
    inspected_on = fields.Date(required=True, default=fields.Date.context_today)
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    confirmed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    state = fields.Selection([("draft", "Draft"), ("done", "Done")], required=True, default="draft")
    notes = fields.Char()

    _qty_bounds = models.Constraint(
        "CHECK (qty_received >= 0 AND qty_accepted >= 0 AND qty_accepted <= qty_received)",
        "Accepted quantity must be between 0 and the received quantity",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "outcome", "confirmed_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.receipt_line_id for r in self):
            locked |= {"product_id", "qty_received", "receipt_ref"}
        if self and any(r.state == "done" for r in self):
            locked |= {
                "receipt_line_id",
                "receipt_ref",
                "product_id",
                "qty_received",
                "qty_accepted",
                "inspected_on",
                "inspector_id",
            }
        return locked

    @api.depends("qty_received", "qty_accepted")
    def _compute_rejected(self):
        for rec in self:
            received = rec.qty_received or 0.0
            accepted = rec.qty_accepted or 0.0
            rec.qty_rejected = round(received - accepted, 3)
            if received and accepted >= received - 1e-6:
                rec.outcome = "accepted"
            elif accepted <= 1e-6:
                rec.outcome = "rejected"
            else:
                rec.outcome = "partial"

    @api.model_create_multi
    def create(self, vals_list):
        Line = self.env["fix.purchase.receipt.line"].sudo()
        for vals in vals_list:
            line = Line.browse(vals.get("receipt_line_id")).exists()
            if line:
                vals["product_id"] = line.product_id.id
                vals["qty_received"] = line.qty_received
                vals["receipt_ref"] = line.receipt_id.name
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.inspection") or "INSP/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_has_token():
            if any(r.state == "done" for r in self) and set(vals) - {"notes"}:
                raise UserError("A confirmed inspection is final; only its notes can change.")
            if "receipt_line_id" in vals:
                line = (
                    self.env["fix.purchase.receipt.line"]
                    .sudo()
                    .browse(vals["receipt_line_id"])
                    .exists()
                )
                if line:
                    vals = dict(
                        vals,
                        product_id=line.product_id.id,
                        qty_received=line.qty_received,
                        receipt_ref=line.receipt_id.name,
                    )
            elif {"product_id", "qty_received"} & set(vals) and any(
                r.receipt_line_id for r in self
            ):
                raise UserError(
                    "An inspection of a receipt line takes its product and quantity from it."
                )
        return super().write(vals)

    def action_confirm(self):
        for rec in self:
            require_role(self.env, GROUP_RECEIVER, "Confirming an inspection outcome")
            if rec.state != "draft":
                raise UserError("Confirm a draft inspection")
            line = rec.receipt_line_id.sudo()
            if not line:
                raise UserError(
                    "Inspection %s judges no receipt line. Link the goods receipt line it "
                    "inspects." % rec.name
                )
            if line.receipt_id.state != "posted":
                raise UserError("Receipt %s is not posted." % line.receipt_id.name)
            # A06 P21: the receiver does not judge the goods they received
            if not self.env.su and self.env.user == line.receipt_id.receiver_id:
                raise UserError(
                    "Segregation of duties: you received %s; another person records its "
                    "inspection." % line.receipt_id.name
                )
            if line.inspection_ids.filtered(lambda i, me=rec: i != me and i.state == "done"):
                raise UserError(
                    "Receipt line %s already has a confirmed inspection." % line.display_name
                )
            rec._guarded().write(
                {
                    "state": "done",
                    "qty_received": line.qty_received,
                    "confirmed_by_id": self.env.uid,
                }
            )
            if rec.qty_rejected > 0:
                order = line.receipt_id.purchase_order_id
                # Hand-off to M15: rejected goods go to RTV or quarantine.
                publish(
                    self.env,
                    "inspection.rejected",
                    "fix.procurement.inspection",
                    rec.id,
                    {
                        "po_ref": order.name,
                        "vendor_id": order.vendor_id.commercial_partner_id.id,
                        "product_id": rec.product_id.id,
                        "qty_rejected": rec.qty_rejected,
                        "receipt_ref": line.receipt_id.name,
                    },
                )
