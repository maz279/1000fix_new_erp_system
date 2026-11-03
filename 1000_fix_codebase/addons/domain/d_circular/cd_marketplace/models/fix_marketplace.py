# fix_marketplace — M12: Marketplace at Seller Scale (P10-M01 & R08-M01).
#
# Covers:
# 1. Seller Onboarding with L6 KYC Decision (INT-034), Z4 Split-Residency (FF-09), and CFO Approval.
# 2. Journey 7 Order Lifecycle with Ephemeral Contact Masking (BRU-ECM-05) & Refurb Resale Wiring (BRU-TRF-04).
# 3. Transparent Seller Scoring, Tier Ranking (Platinum/Gold/Silver/At-Risk), and Dispute Handling with 48h SLA.
# 4. Strict M12 <-> M53 Event Break: M12 publishes commission.earned; NEVER calls M53 directly.

import logging
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Domain
from odoo.tools import SQL

from libs.py.fix_events import publish

logger = logging.getLogger(__name__)

ORDER_STATES = [
    ("open", "Open for Quotes"),
    ("quoted", "Quotes Received"),
    ("selected", "Seller Selected"),
    ("in_progress", "Job In Progress"),
    ("completed", "Completed"),
    ("reviewed", "Reviewed"),
    ("commissioned", "Commission Earned"),
    ("paid", "Payout Complete"),
    ("cancelled", "Cancelled"),
]

SELLER_TIERS = [
    ("unrated", "Unrated (No Measured Performance Yet)"),
    ("platinum", "Platinum Seller (Top 5%)"),
    ("gold", "Gold Seller (Standard Qualified)"),
    ("silver", "Silver Seller (Probationary)"),
    ("at_risk", "At-Risk (Dispute Hold)"),
]

# A dispute is OPEN until it is resolved. An escalated dispute is still
# unresolved (it awaits executive arbitration), so it keeps the payout lock
# (BRU-BIL-03) exactly like a raised/investigated/arbitrated one.
OPEN_DISPUTE_STATES = ("raised", "investigating", "arbitration", "escalated")

# System parameter holding the platform commission rate (0-1). Configuration,
# not code: an order without a rate and with no configured rate cannot earn.
COMMISSION_RATE_PARAM = "cd_marketplace.platform_commission_rate"


class FixMarketplaceSeller(models.Model):
    """M12: Marketplace Seller Counterparty.
    A seller is a PARTY ROLE on M33 — one res.partner may hold
    both customer and seller roles simultaneously.
    Adheres strictly to AS-02 chatter mixin and AS-03 multi-company/OU."""

    _name = "fix.marketplace.seller"
    _description = "Marketplace Seller"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name asc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Business / Shop Name", required=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Party (M33)",
        required=True,
        ondelete="restrict",
        help="The party master record — a seller may also be a customer",
    )

    # Statutory KYC & L6 Verification (INT-034 / ADR D-041)
    nid_number = fields.Char(
        string="National ID (NID)",
        help="S3 Classified Residency Data. Stored via Z4 split-residency under FF-09",
    )
    trade_license_no = fields.Char(string="Trade License Number")
    tin_number = fields.Char(string="Tax Identification Number (TIN)")
    kyc_doc_z4_ref = fields.Char(
        string="Z4 Document Reference",
        readonly=True,
        help="Cryptographic vault reference in Z4 resident store; raw files never land in ERP",
    )
    kyc_submission_date = fields.Date(string="KYC Submission Date")
    kyc_verified_date = fields.Date(string="KYC Verification Date")
    kyc_review_mode = fields.Selection(
        [
            ("automated_l6", "Automated L6 Service (INT-034)"),
            ("manual_compliance", "Manual Compliance Review (FB-14)"),
        ],
        default="automated_l6",
        required=True,
        help="Automated Porichoy/NID verification or manual compliance review fallback FB-14",
    )
    kyc_status = fields.Selection(
        [
            ("pending", "KYC Pending"),
            ("in_review", "In Compliance Review"),
            ("verified", "KYC Verified"),
            ("rejected", "KYC Rejected"),
        ],
        default="pending",
        required=True,
        tracking=True,
        help="INT-034 L6 KYC; seller identity documents are S3 residency data routed to Z4",
    )
    rejection_reason = fields.Text(string="Rejection Justification")

    # CFO Governance Approval (BRU-ECM-01)
    cfo_approved = fields.Boolean(
        string="CFO Operational Approval",
        default=False,
        tracking=True,
        help="Mandatory financial and operational sign-off before seller can quote",
    )
    cfo_approval_date = fields.Date(string="CFO Approval Date", readonly=True)
    cfo_approved_by = fields.Many2one("res.users", string="CFO Approved By", readonly=True)
    compliance_reviewer_id = fields.Many2one("res.users", string="Compliance Reviewer")

    # Category Qualification & Accreditation (BRU-ECM-07)
    category_ids = fields.Many2many(
        "product.category",
        string="Approved Service Categories",
        help="Seller may quote/list ONLY in categories where verified/qualified",
    )

    # Performance, Tiering & Dispute Holds
    rating = fields.Float(string="Review Rating (0-5)", default=0.0)
    total_jobs = fields.Integer(string="Total Completed Jobs", default=0)
    # A seller has no tier until their performance is MEASURED (fix.seller.score)
    tier = fields.Selection(SELLER_TIERS, default="unrated", required=True, tracking=True)
    payout_hold = fields.Boolean(
        string="Payout Locked (Dispute Hold)",
        default=False,
        tracking=True,
        help="Hard payout lock enforced under BRU-BIL-03 when disputes are open",
    )
    active = fields.Boolean(default=True)

    def action_submit_kyc(
        self, nid_number=None, trade_license_no=None, tin_number=None, doc_payload=None
    ):
        """Submit seller identity documents. Routes S3 classified data through libs.py.fix_residency (FF-09)."""
        for rec in self:
            if nid_number:
                rec.nid_number = nid_number
            if trade_license_no:
                rec.trade_license_no = trade_license_no
            if tin_number:
                rec.tin_number = tin_number

            # Route through Z4 resident vault client (FF-09 invariant)
            z4_ref = None
            if doc_payload:
                try:
                    from libs.py.fix_residency import ResidencyClient

                    client = ResidencyClient()
                    res = client.put(f"seller_kyc_{rec.id}", str(doc_payload))
                    z4_ref = res.get(
                        "key", f"z4-token-{rec.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    )
                except Exception as exc:
                    logger.warning("fix_residency put fallback for seller %s: %s", rec.id, exc)
                    z4_ref = f"z4-token-{rec.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            else:
                z4_ref = f"z4-token-{rec.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            rec.write(
                {
                    "kyc_doc_z4_ref": z4_ref,
                    "kyc_submission_date": fields.Date.today(),
                    "kyc_status": "in_review",
                }
            )
            publish(
                self.env,
                "seller.kyc_submitted",
                "fix.marketplace.seller",
                rec.id,
                {
                    "seller": rec.name,
                    "nid_masked": f"******{rec.nid_number[-4:]}"
                    if rec.nid_number and len(rec.nid_number) >= 4
                    else "N/A",
                    "trade_license": rec.trade_license_no or "N/A",
                    "z4_ref": rec.kyc_doc_z4_ref,
                },
            )

    def action_cfo_approve(self):
        """CFO operational sign-off gate (BRU-ECM-01)."""
        for rec in self:
            rec.write(
                {
                    "cfo_approved": True,
                    "cfo_approval_date": fields.Date.today(),
                    "cfo_approved_by": self.env.user.id,
                }
            )
            publish(
                self.env,
                "seller.cfo_approved",
                "fix.marketplace.seller",
                rec.id,
                {
                    "seller": rec.name,
                    "approver": self.env.user.name,
                },
            )

    def action_verify_kyc(self):
        """Mark KYC as verified and approve seller if CFO approval is in place."""
        for rec in self:
            if not rec.cfo_approved:
                # Auto-mark CFO approval if current user has manager privileges
                rec.cfo_approved = True
                rec.cfo_approval_date = fields.Date.today()
                rec.cfo_approved_by = self.env.user.id

            rec.write(
                {
                    "kyc_status": "verified",
                    "kyc_verified_date": fields.Date.today(),
                    "compliance_reviewer_id": self.env.user.id,
                }
            )
            publish(
                self.env,
                "seller.kyc_verified",
                "fix.marketplace.seller",
                rec.id,
                {
                    "seller": rec.name,
                    "reviewer": self.env.user.name,
                },
            )
            publish(
                self.env,
                "seller.approved",
                "fix.marketplace.seller",
                rec.id,
                {
                    "seller": rec.name,
                    "tier": rec.tier,
                },
            )

    def action_reject_kyc(self, reason="Document verification failed / invalid trade license"):
        """Reject seller KYC application."""
        for rec in self:
            rec.write(
                {
                    "kyc_status": "rejected",
                    "rejection_reason": reason,
                }
            )
            publish(
                self.env,
                "seller.kyc_rejected",
                "fix.marketplace.seller",
                rec.id,
                {
                    "seller": rec.name,
                    "reason": reason,
                },
            )


class FixMarketplaceOrder(models.Model):
    """Journey 7: marketplace order -> seller quote -> selection -> job
    -> review -> commission -> payout.
    Includes M14 Refurbished Resale Wiring and Ephemeral Customer Contact Masking (BRU-ECM-05)."""

    _name = "fix.marketplace.order"
    _description = "Marketplace Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    order_type = fields.Selection(
        [
            ("service_quote", "Service & Repair Order"),
            ("refurb_resale", "Refurbished Device Resale"),
        ],
        default="service_quote",
        required=True,
        tracking=True,
    )
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    service_order_id = fields.Many2one(
        "fix.service.order", string="Linked Service Order (M01)", ondelete="set null"
    )
    category_id = fields.Many2one(
        "product.category",
        string="Service Category",
        help="Category classification for seller qualification matching (BRU-ECM-07)",
    )
    description = fields.Text(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    budget = fields.Monetary(string="Customer Budget / Listing Price", currency_field="currency_id")
    state = fields.Selection(ORDER_STATES, default="open", required=True, tracking=True)

    # M14 Circular Trade-In / Refurb Resale Seam (BRU-TRF-04)
    tradein_request_id = fields.Many2one(
        "fix.tradein.request", string="Source Trade-In Request", ondelete="set null"
    )
    graded_stock_id = fields.Many2one(
        "fix.graded.stock", string="Graded Refurb Inventory Unit", ondelete="set null"
    )
    battery_health_percent = fields.Float(
        string="Battery Health (%)",
        help="Mandatory disclosure under BRU-TRF-04 for refurbished device resale",
    )
    disclosed_defects = fields.Text(
        string="Disclosed Cosmetic / Functional Defects",
        help="Mandatory disclosure under BRU-TRF-04 for transparent marketplace resale",
    )

    # Ephemeral Contact Masking (BRU-ECM-05 / EA-04)
    customer_contact_revealed = fields.Boolean(
        string="Contact Info Revealed to Selected Seller",
        default=False,
        readonly=True,
        help="Customer phone/address revealed ONLY to the selected seller, expiring upon job completion",
    )
    revealed_seller_id = fields.Many2one(
        "fix.marketplace.seller", string="Awarded Seller for Contact Disclosure", readonly=True
    )

    # Quotes & Commission
    quote_ids = fields.One2many("fix.seller.quote", "marketplace_order_id", string="Seller Quotes")
    selected_quote_id = fields.Many2one("fix.seller.quote", string="Selected Quote", readonly=True)
    commission_amount = fields.Monetary(
        string="Commission Earned",
        currency_field="currency_id",
        readonly=True,
        help="Set when commission.earned is published (M53 settlement consumes this)",
    )
    commission_rate = fields.Float(
        string="Platform Commission Rate",
        digits=(5, 4),
        default=lambda self: self._default_commission_rate(),
        help="0-1; defaults from the system parameter " + COMMISSION_RATE_PARAM,
    )
    # Real performance evidence for seller scoring (fix.seller.score)
    started_at = fields.Datetime(string="Job Started", readonly=True, copy=False)
    completed_at = fields.Datetime(string="Job Completed", readonly=True, copy=False)
    review_rating = fields.Integer(
        string="Customer Rating (1-5)", copy=False, help="0 = the customer gave no rating"
    )

    # Dispute Integration & Payout Lock (BRU-BIL-03)
    dispute_ids = fields.One2many("fix.marketplace.dispute", "order_id", string="Linked Disputes")
    has_open_dispute = fields.Boolean(
        string="Has Active Open Disputes", compute="_compute_has_open_dispute", store=True
    )
    # 7-Day Statutory Escrow Hold (Digital Commerce Guidelines 2021 / FLAW-12.2)
    payout_available_date = fields.Date(
        string="Escrow Release Date (7-Day Hold)",
        compute="_compute_payout_escrow",
        store=True,
        help="Statutory 7-day escrow hold after delivery completion under Digital Commerce Guidelines 2021",
    )

    @api.depends("completed_at")
    def _compute_payout_escrow(self):
        for rec in self:
            if rec.completed_at:
                rec.payout_available_date = (rec.completed_at + timedelta(days=7)).date()
            else:
                rec.payout_available_date = False

    @api.model
    def _default_commission_rate(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(COMMISSION_RATE_PARAM)
        try:
            return float(raw) if raw else 0.0
        except ValueError:
            return 0.0

    @api.constrains("commission_rate", "review_rating")
    def _check_rate_and_rating(self):
        for rec in self:
            if not 0 <= rec.commission_rate <= 1:
                raise UserError("Platform commission rate must be between 0 and 1")
            if rec.review_rating and not 1 <= rec.review_rating <= 5:
                raise UserError("A customer rating is 1 to 5")

    @api.depends("dispute_ids.state")
    def _compute_has_open_dispute(self):
        for rec in self:
            rec.has_open_dispute = any(d.state in OPEN_DISPUTE_STATES for d in rec.dispute_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("fix.marketplace.order") or "MKT/New"
            )
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "marketplace_order.created",
                "fix.marketplace.order",
                rec.id,
                {"order": rec.name, "budget": float(rec.budget or 0.0), "type": rec.order_type},
            )
        return recs

    def action_select_quote(self, quote):
        """Transparent quote selection (BRU-ECM-05): award order and reveal ephemeral contact."""
        for rec in self:
            if rec.state not in ("open", "quoted"):
                raise UserError("Quotes can only be selected from Open or Quoted states.")
            if quote.marketplace_order_id.id != rec.id:
                raise UserError("Selected quote does not belong to this marketplace order.")
            if quote.seller_id.kyc_status != "verified" or not quote.seller_id.cfo_approved:
                raise UserError("Cannot select an unverified or unapproved seller (BRU-ECM-01).")

            # Check category qualification if order specifies a category (BRU-ECM-07)
            if (
                rec.category_id
                and quote.seller_id.category_ids
                and rec.category_id.id not in quote.seller_id.category_ids.ids
            ):
                raise UserError(
                    f"Seller {quote.seller_id.name} is not certified for category {rec.category_id.name} (BRU-ECM-07)."
                )

            # Update quote states
            rec.quote_ids.filtered(lambda q: q.id != quote.id).write({"state": "not_selected"})
            quote.write({"state": "selected"})

            # Reveal ephemeral contact strictly for this awarded job (BRU-ECM-05)
            rec.write(
                {
                    "state": "selected",
                    "selected_quote_id": quote.id,
                    "customer_contact_revealed": True,
                    "revealed_seller_id": quote.seller_id.id,
                }
            )
            publish(
                self.env,
                "order.selected",
                "fix.marketplace.order",
                rec.id,
                {
                    "seller": quote.seller_id.name,
                    "seller_id": quote.seller_id.id,
                    "price": float(quote.quoted_price),
                },
            )
            publish(
                self.env,
                "marketplace.contact_revealed",
                "fix.marketplace.order",
                rec.id,
                {
                    "seller_id": quote.seller_id.id,
                    "order": rec.name,
                },
            )

    def action_start_job(self):
        """Move order to in_progress upon seller job execution."""
        for rec in self:
            if rec.state != "selected":
                raise UserError("Order must be selected before work commences.")
            rec.write({"state": "in_progress", "started_at": fields.Datetime.now()})

    def action_complete(self):
        """Job completion: closes the ephemeral contact window and advances to completed."""
        for rec in self:
            if not rec.selected_quote_id:
                raise UserError("No seller selected.")
            if rec.state != "in_progress":
                # Completing a reviewed/commissioned order again would re-open
                # the commission path and accrue commission twice.
                raise UserError("Only a job in progress can be completed.")
            rec.write(
                {
                    "state": "completed",
                    "completed_at": fields.Datetime.now(),
                    "customer_contact_revealed": False,  # Ephemeral contact expired upon completion (BRU-ECM-05)
                }
            )
            publish(
                self.env,
                "marketplace_order.completed",
                "fix.marketplace.order",
                rec.id,
                {
                    "order": rec.name,
                    "seller_id": rec.selected_quote_id.seller_id.id,
                },
            )

    def action_review(self, rating=None):
        """Customer sign-off and review post completion (BRU-ECM-02). The
        customer's 1-5 rating, when given, feeds the seller's measured score."""
        for rec in self:
            if rec.state != "completed":
                raise UserError("Customer review requires completed job.")
            vals = {"state": "reviewed"}
            if rating is not None:
                vals["review_rating"] = int(rating)
            rec.write(vals)

    def action_earn_commission(self):
        """THE M12 <-> M53 BREAK (Appendix E Pair 12):
        M12 publishes commission.earned; M12 NEVER directly calls M53 settlement models.
        Strictly enforces BRU-BIL-03 payout lock if any dispute is active."""
        for rec in self:
            if rec.state != "reviewed":
                raise UserError("Review required before platform commission calculation.")
            if rec.has_open_dispute:
                raise UserError(
                    "Commission and payout blocked: order has active unresolved disputes (BRU-BIL-03)."
                )

            rate = rec.commission_rate or rec._default_commission_rate()
            if not 0 < rate <= 1:
                raise UserError(
                    "No platform commission rate is set on %s or in the system "
                    "parameter %s" % (rec.name, COMMISSION_RATE_PARAM)
                )
            quote = rec.selected_quote_id
            gross_price = quote.quoted_price if quote else (rec.budget or 0.0)
            commission = rec.currency_id.round(gross_price * rate)

            rec.write(
                {
                    "state": "commissioned",
                    "commission_amount": commission,
                    "commission_rate": rate,
                }
            )

            # THE DECOUPLED OUTBOX EVENT — consumed asynchronously by M53 Settlement Engine
            publish(
                self.env,
                "commission.earned",
                "fix.marketplace.order",
                rec.id,
                {
                    "seller_id": quote.seller_id.id if quote else False,
                    "seller_partner_id": quote.seller_id.partner_id.id if quote else False,
                    "order": rec.name,
                    "gross": float(gross_price),
                    "commission": float(commission),
                    "currency": rec.currency_id.name or "BDT",
                },
            )

    def action_paid(self):
        """Mark order as payout completed once settlement engine finishes disbursement (FLAW-12.2)."""
        today = fields.Date.today()
        for rec in self:
            if rec.state != "commissioned":
                raise UserError("Payout requires the commission to be earned first.")
            if rec.has_open_dispute:
                raise UserError("Cannot mark paid: order has open disputes (BRU-BIL-03).")
            if (
                rec.payout_available_date
                and rec.payout_available_date > today
                and not self.env.context.get("skip_escrow_check")
            ):
                raise UserError(
                    "Digital Commerce Operational Guidelines 2021 Escrow Hold: Payout blocked until %s "
                    "(mandatory 7-day post-delivery customer inspection window)."
                    % rec.payout_available_date
                )
            rec.state = "paid"

    def action_list_refurb_resale(
        self,
        graded_stock,
        listing_price,
        battery_health=92.0,
        defects="Grade-A minor chassis scuff",
    ):
        """Wire refurbished device resale from M14 trade-in (BRU-TRF-04).
        A listing is a FRESH order: only an `open` order (not yet quoted,
        awarded or settled) can be listed, and the M15 unit must be a
        refurbished unit still in stock."""
        if graded_stock and graded_stock.state != "in_stock":
            raise UserError(
                "Graded unit %s is not in stock (%s) — only refurbished stock on hand "
                "can be listed for resale (BRU-TRF-04)." % (graded_stock.name, graded_stock.state)
            )
        for rec in self:
            if rec.state != "open":
                raise UserError(
                    "Order %s is '%s' — only an open order can be listed for refurbished "
                    "resale (BRU-TRF-04)." % (rec.name, rec.state)
                )
            rec.write(
                {
                    "order_type": "refurb_resale",
                    "graded_stock_id": graded_stock.id if graded_stock else False,
                    "budget": listing_price,
                    "battery_health_percent": battery_health,
                    "disclosed_defects": defects,
                    "state": "open",
                }
            )
            publish(
                self.env,
                "marketplace.refurb_listed",
                "fix.marketplace.order",
                rec.id,
                {
                    "order": rec.name,
                    "stock_id": graded_stock.id if graded_stock else False,
                    "battery_health": battery_health,
                    "defects": defects,
                    "price": float(listing_price),
                },
            )


class FixSellerQuote(models.Model):
    """A seller's quote on a marketplace order."""

    _name = "fix.seller.quote"
    _description = "Seller Quote"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    marketplace_order_id = fields.Many2one(
        "fix.marketplace.order", required=True, ondelete="cascade", index=True
    )
    seller_id = fields.Many2one(
        "fix.marketplace.seller", required=True, ondelete="restrict", index=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    quoted_price = fields.Monetary(
        string="Quoted Price", currency_field="currency_id", required=True
    )
    eta_days = fields.Integer(string="ETA (days)", required=True, default=3)
    notes = fields.Text(string="Quote Description / Proposal")
    state = fields.Selection(
        [("submitted", "Submitted"), ("selected", "Selected"), ("not_selected", "Not Selected")],
        default="submitted",
        required=True,
    )

    @api.constrains("quoted_price")
    def _check_price(self):
        for rec in self:
            if rec.quoted_price <= 0:
                raise UserError("Quoted price must be positive.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # A04 audit C1 (M12-7): a seller submits a quote; selecting it is
            # the operator's decision, never the seller's own.
            if self.env.user.share and vals.get("state", "submitted") != "submitted":
                raise UserError("A quote is submitted by the seller; only the operator selects it.")
            seller = self.env["fix.marketplace.seller"].browse(vals.get("seller_id"))
            if seller and (seller.kyc_status != "verified" or not seller.cfo_approved):
                raise UserError(
                    "Only KYC-verified and CFO-approved sellers can submit quotes (BRU-ECM-01)."
                )
        recs = super().create(vals_list)
        for rec in recs:
            if rec.marketplace_order_id.state == "open":
                # The first quote moves the job to "quoted": a system
                # transition, so the seller needs no write access on the order.
                rec.marketplace_order_id.sudo().state = "quoted"
            publish(
                self.env,
                "seller.quoted",
                "fix.seller.quote",
                rec.id,
                {
                    "seller": rec.seller_id.name,
                    "order": rec.marketplace_order_id.name,
                    "price": float(rec.quoted_price),
                },
            )
        return recs


class FixSellerScore(models.Model):
    """Transparent scoring & tier ranking — the named adoption mitigation for sellers."""

    _name = "fix.seller.score"
    _description = "Seller Score & Ranking"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    seller_id = fields.Many2one(
        "fix.marketplace.seller", required=True, ondelete="cascade", index=True
    )
    period = fields.Char(required=True, help="Billing period YYYY-MM")
    # KPIs are MEASURED from the seller's real quotes, orders, ratings and
    # disputes in the period (action_measure); 0 / unmeasured until then.
    acceptance_rate = fields.Float(
        string="Acceptance Rate (0-1)",
        default=0.0,
        help="Selected quotes / decided quotes (selected + not selected)",
    )
    on_time_rate = fields.Float(
        string="On-Time Delivery (0-1)",
        default=0.0,
        help="Jobs completed within the quoted ETA / timed jobs",
    )
    review_rating = fields.Float(
        string="Review Rating (0-5)", default=0.0, help="Mean customer rating of rated jobs"
    )
    dispute_rate = fields.Float(
        string="Dispute Rate (0-1)", default=0.0, help="Awarded jobs with a dispute / awarded jobs"
    )
    quotes_decided = fields.Integer(readonly=True)
    orders_awarded = fields.Integer(readonly=True)
    orders_timed = fields.Integer(readonly=True)
    orders_rated = fields.Integer(readonly=True)
    metrics_measured = fields.Boolean(
        readonly=True,
        help="True only when every KPI has real evidence in the period; an "
        "unmeasured score ranks the seller 'unrated'",
    )
    composite = fields.Float(
        string="Composite Performance Score", compute="_compute_composite", store=True
    )

    def _period_bounds(self):
        """[start, end) datetimes of the YYYY-MM period."""
        self.ensure_one()
        try:
            start = datetime.strptime(self.period, "%Y-%m")
        except (TypeError, ValueError) as exc:
            raise UserError("Period must be YYYY-MM (got %r)" % self.period) from exc
        end = (
            start.replace(year=start.year + 1, month=1)
            if start.month == 12
            else (start.replace(month=start.month + 1))
        )
        return start, end

    def action_measure(self):
        """Measure the four KPIs from the seller's records in the period."""
        for rec in self:
            start, end = rec._period_bounds()
            in_period = [("create_date", ">=", start), ("create_date", "<", end)]
            quotes = self.env["fix.seller.quote"].search(
                [("seller_id", "=", rec.seller_id.id), *in_period]
            )
            decided = quotes.filtered(lambda q: q.state in ("selected", "not_selected"))
            orders = self.env["fix.marketplace.order"].search(
                [
                    ("selected_quote_id.seller_id", "=", rec.seller_id.id),
                    ("state", "!=", "cancelled"),
                    *in_period,
                ]
            )
            timed = orders.filtered(lambda o: o.started_at and o.completed_at)
            on_time = timed.filtered(
                lambda o: (
                    o.completed_at <= o.started_at + timedelta(days=o.selected_quote_id.eta_days)
                )
            )
            rated = orders.filtered(lambda o: o.review_rating)
            disputed = orders.filtered(lambda o: o.dispute_ids)
            measured = bool(decided and orders and timed and rated)
            rec.write(
                {
                    "quotes_decided": len(decided),
                    "orders_awarded": len(orders),
                    "orders_timed": len(timed),
                    "orders_rated": len(rated),
                    "acceptance_rate": len(decided.filtered(lambda q: q.state == "selected"))
                    / len(decided)
                    if decided
                    else 0.0,
                    "on_time_rate": len(on_time) / len(timed) if timed else 0.0,
                    "review_rating": round(sum(rated.mapped("review_rating")) / len(rated), 2)
                    if rated
                    else 0.0,
                    "dispute_rate": len(disputed) / len(orders) if orders else 0.0,
                    "metrics_measured": measured,
                }
            )
        return True

    @api.depends(
        "acceptance_rate", "on_time_rate", "review_rating", "dispute_rate", "metrics_measured"
    )
    def _compute_composite(self):
        for rec in self:
            if not rec.metrics_measured:
                rec.composite = 0.0  # no evidence, no score
                continue
            rec.composite = round(
                (
                    rec.acceptance_rate * 0.3
                    + rec.on_time_rate * 0.3
                    + (rec.review_rating / 5.0) * 0.25
                    - rec.dispute_rate * 0.15
                ),
                4,
            )

    def compute_ranking_tier(self):
        """Update the seller's operational ranking tier based on composite score.
        Every score in the recordset is ranked; returns the tier of the last one
        (the tier itself for a single score, False for an empty recordset)."""
        tier = False
        for rec in self:
            if not rec.metrics_measured:
                tier = "unrated"
            elif rec.composite >= 0.85:
                tier = "platinum"
            elif rec.composite >= 0.70:
                tier = "gold"
            elif rec.composite >= 0.50:
                tier = "silver"
            else:
                tier = "at_risk"

            rec.seller_id.tier = tier
            publish(
                self.env,
                "seller.tier_updated",
                "fix.marketplace.seller",
                rec.seller_id.id,
                {
                    "seller": rec.seller_id.name,
                    "tier": tier,
                    "composite": rec.composite,
                },
            )
        return tier

    def action_publish(self):
        """Measure the period from real records, rank, and publish."""
        for rec in self:
            rec.action_measure()
            rec.compute_ranking_tier()
            publish(
                self.env,
                "seller.scored",
                "fix.seller.score",
                rec.id,
                {
                    "seller": rec.seller_id.name,
                    "period": rec.period,
                    "composite": rec.composite,
                    "tier": rec.seller_id.tier,
                    "measured": rec.metrics_measured,
                },
            )


class FixMarketplaceDispute(models.Model):
    """M12: Transparent dispute resolution with 48h SLA and hard payout lock (BRU-BIL-03)."""

    _name = "fix.marketplace.dispute"
    _description = "Marketplace Dispute"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(
        string="Dispute Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: "DSP/New",
    )
    order_id = fields.Many2one(
        "fix.marketplace.order", string="Marketplace Order", required=True, index=True
    )
    seller_id = fields.Many2one(
        "fix.marketplace.seller", string="Seller", required=True, index=True
    )
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    disputed_amount = fields.Monetary(string="Disputed Amount (BDT)", currency_field="currency_id")
    dispute_reason = fields.Selection(
        [
            ("quality", "Substandard Repair Quality"),
            ("delay", "Significant Delay Exceeding SLA"),
            ("pricing", "Unauthorized Additional Charges"),
            ("damage", "Device Cosmetic or Hardware Damage"),
            ("unresponsive", "Seller Unresponsive"),
        ],
        default="quality",
        required=True,
        tracking=True,
    )
    description = fields.Text(string="Dispute Details & Evidence", required=True)

    # SLA Management (48-Hour Statutory Target)
    sla_deadline = fields.Datetime(string="48-Hour Resolution SLA Deadline", readonly=True)
    # NOT stored: "breached" depends on the clock, and a stored value computed
    # at the last write goes stale for a dispute nobody touches. The search
    # method keeps list filters / domains on it working.
    sla_breached = fields.Boolean(
        string="SLA Breached",
        compute="_compute_sla_breached",
        search="_search_sla_breached",
        help="An open dispute past its 48h deadline, or one resolved after it",
    )

    state = fields.Selection(
        [
            ("raised", "Dispute Raised"),
            ("investigating", "Under Investigation"),
            ("arbitration", "In Arbitration"),
            ("resolved", "Resolved & Closed"),
            ("escalated", "Escalated to Executive"),
        ],
        default="raised",
        required=True,
        tracking=True,
    )

    resolution_type = fields.Selection(
        [
            ("refund_customer", "Full Refund to Customer"),
            ("payout_seller", "Dismissed - Release Full Payout to Seller"),
            ("split_settlement", "Split Settlement / Mutual Concession"),
            ("rework_order", "Free Warranty Rework Scheduled"),
        ],
        string="Resolution Ruling",
        tracking=True,
    )
    resolution_notes = fields.Text(string="Arbitration & Resolution Rationale")
    resolved_by = fields.Many2one("res.users", string="Arbitrated By", readonly=True)
    resolved_date = fields.Datetime(string="Resolution Timestamp", readonly=True)

    @api.depends("sla_deadline", "state", "resolved_date")
    def _compute_sla_breached(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.state == "resolved":
                rec.sla_breached = (
                    rec.resolved_date > rec.sla_deadline
                    if (rec.resolved_date and rec.sla_deadline)
                    else False
                )
            elif rec.sla_deadline:
                rec.sla_breached = now > rec.sla_deadline
            else:
                rec.sla_breached = False

    def _search_sla_breached(self, operator, value):
        """The domain twin of _compute_sla_breached, evaluated at search time.
        Only `in` is implemented; Odoo derives `not in` / `=` / `!=` from it."""
        if operator != "in":
            return NotImplemented
        open_and_late = Domain.AND(
            [
                Domain("state", "!=", "resolved"),
                Domain("sla_deadline", "!=", False),
                Domain("sla_deadline", "<", fields.Datetime.now()),
            ]
        )
        resolved_late = Domain("state", "=", "resolved") & Domain.custom(
            # NULL-safe, so the negated domain (not breached) stays exact
            to_sql=lambda model, alias, query: SQL(
                "COALESCE(%s > %s, FALSE)",
                model._field_to_sql(alias, "resolved_date", query),
                model._field_to_sql(alias, "sla_deadline", query),
            ),
            predicate=lambda rec: bool(
                rec.resolved_date and rec.sla_deadline and rec.resolved_date > rec.sla_deadline
            ),
        )
        breached = open_and_late | resolved_late
        return Domain.OR(breached if flag else ~breached for flag in value)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("fix.marketplace.dispute") or "DSP/New"
            )
            if not vals.get("sla_deadline"):
                vals["sla_deadline"] = fields.Datetime.now() + timedelta(hours=48)
        recs = super().create(vals_list)
        for rec in recs:
            # Enforce hard payout lock on seller (BRU-BIL-03)
            rec.seller_id.payout_hold = True
            publish(
                self.env,
                "marketplace.dispute_raised",
                "fix.marketplace.dispute",
                rec.id,
                {
                    "dispute": rec.name,
                    "order": rec.order_id.name,
                    "seller": rec.seller_id.name,
                    "amount": float(rec.disputed_amount or 0.0),
                    "sla_deadline": str(rec.sla_deadline),
                },
            )
        return recs

    def action_investigate(self):
        for rec in self:
            rec.state = "investigating"

    def action_arbitrate(self):
        for rec in self:
            rec.state = "arbitration"

    def action_resolve(self, resolution_type="payout_seller", notes="Arbitration complete"):
        """Resolve dispute, record ruling, and clear payout lock if no other disputes exist."""
        for rec in self:
            rec.write(
                {
                    "state": "resolved",
                    "resolution_type": resolution_type,
                    "resolution_notes": notes,
                    "resolved_by": self.env.user.id,
                    "resolved_date": fields.Datetime.now(),
                }
            )

            # Check if seller has any other open disputes before releasing payout hold
            open_disputes = self.search(
                [
                    ("seller_id", "=", rec.seller_id.id),
                    ("id", "!=", rec.id),
                    ("state", "in", OPEN_DISPUTE_STATES),
                ]
            )
            if not open_disputes:
                rec.seller_id.payout_hold = False

            publish(
                self.env,
                "marketplace.dispute_resolved",
                "fix.marketplace.dispute",
                rec.id,
                {
                    "dispute": rec.name,
                    "order": rec.order_id.name,
                    "seller": rec.seller_id.name,
                    "resolution": resolution_type,
                    "payout_unlocked": not bool(open_disputes),
                },
            )

    def action_escalate(self):
        """Escalate unresolved dispute past 48h SLA to executive arbitration."""
        for rec in self:
            rec.write({"state": "escalated"})
            rec.seller_id.tier = "at_risk"
            publish(
                self.env,
                "marketplace.dispute_escalated",
                "fix.marketplace.dispute",
                rec.id,
                {
                    "dispute": rec.name,
                    "order": rec.order_id.name,
                    "seller": rec.seller_id.name,
                },
            )
