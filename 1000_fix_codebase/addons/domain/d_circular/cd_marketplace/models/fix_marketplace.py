# fix_marketplace — M12: Marketplace at Seller Scale (P10-M01 & R08-M01).
#
# Covers:
# 1. Seller Onboarding with L6 KYC Decision (INT-034), Z4 Split-Residency (FF-09), and CFO Approval.
# 2. Journey 7 Order Lifecycle with Ephemeral Contact Masking (BRU-ECM-05) & Refurb Resale Wiring (BRU-TRF-04).
# 3. Transparent Seller Scoring, Tier Ranking (Platinum/Gold/Silver/At-Risk), and Dispute Handling with 48h SLA.
# 4. Strict M12 <-> M53 Event Break: M12 publishes commission.earned; NEVER calls M53 directly.
#
# A04 workflow audit (2026-11-03) M12-1..-14, C2-C13 build (2026-11-04):
# - KYC, CFO approval, tier, rating and the payout hold were plain fields
#   (2,050 live sellers CFO-approved by nobody) and verifying KYC ticked CFO
#   approval for the same clerk: they are guarded, KYC is a compliance
#   decision and CFO approval a routed M63 decision of a DOFA Tier 4 holder
#   who is not the KYC reviewer;
# - order state, dates, the awarded quote and the commission rate were
#   writable (a forged "reviewed" order was paid; 0.10 became 0.0001): they
#   are guarded, the price and rate are pinned when the quote is awarded and
#   the rate comes from the seller tier;
# - the escrow had a caller switch (skip_escrow_check) and the seller-level
#   payout hold was never read: both are gone / enforced, and the 7-day
#   escrow runs from the customer's delivery confirmation;
# - disputes had no state machine and the respondent ruled his own: a ruling
#   is now proposed by an operator and decided by an arbitrator from the M63
#   inbox, once, with the 48h SLA escalated by a cron.
import logging
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Domain
from odoo.tools import SQL

from libs.py.fix_events import publish

logger = logging.getLogger(__name__)

OPERATOR_GROUP = "cd_marketplace.group_marketplace_operator"
COMPLIANCE_GROUP = "cd_marketplace.group_marketplace_compliance"
ARBITRATOR_GROUP = "cd_marketplace.group_marketplace_arbitrator"
# BRU-ECM-01 "CFO approval": the estate's CFO authority is DOFA Tier 4
# (CFO / CCO / COO); no separate CFO group exists.
CFO_GROUP = "cd_entity_config.group_dofa_tier_4"

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
BIDDING_STATES = ("open", "quoted")
CLOSED_ORDER_STATES = ("paid", "cancelled")

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
RULING_STATES = ("arbitration", "escalated")

# System parameter holding the platform commission rate (0-1). Configuration,
# not code: an order without a rate and with no configured rate cannot earn.
COMMISSION_RATE_PARAM = "cd_marketplace.platform_commission_rate"
# A04 C6 (M12-8): the rate an order earns is the SELLER TIER's, pinned when
# the quote is awarded. Per-tier rates are system parameters
# cd_marketplace.commission_rate.<tier> (0-1); an unset tier earns the
# platform rate. DEFAULT THE BUSINESS MUST CONFIRM (§7 item 5): no tier
# differs from the platform rate until Finance sets one.
TIER_RATE_PARAM = "cd_marketplace.commission_rate.%s"
# FLAW-12.2 / Digital Commerce Guidelines 2021: the statutory inspection hold.
ESCROW_DAYS = 7


def _assert_role(env, xmlid, what):
    """Superuser service code is trusted; a user needs the role."""
    if env.su or env.user.has_group(xmlid):
        return
    group = env.ref(xmlid, raise_if_not_found=False)
    raise AccessError(
        "%s needs the %s role, which %s does not hold."
        % (what, group.sudo().name if group else xmlid, env.user.name)
    )


def _seller_users(seller):
    """The accounts that act for a seller (its party's users)."""
    return seller.sudo().partner_id.user_ids


class FixMarketplaceSeller(models.Model):
    """M12: Marketplace Seller Counterparty.
    A seller is a PARTY ROLE on M33 — one res.partner may hold
    both customer and seller roles simultaneously.
    Adheres strictly to AS-02 chatter mixin and AS-03 multi-company/OU."""

    _name = "fix.marketplace.seller"
    _description = "Marketplace Seller"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "name asc, id desc"

    # A04 C4/C9 (BRU-ECM-01): CFO approval is a routed decision of a DOFA
    # Tier 4 holder, from the M63 inbox, never the KYC reviewer.
    _approval_domain = "marketplace_seller_cfo"
    _approval_apply_method = "action_cfo_approve"
    _approval_group = CFO_GROUP
    _approval_routed = True

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
    kyc_submission_date = fields.Date(string="KYC Submission Date", readonly=True)
    kyc_verified_date = fields.Date(string="KYC Verification Date", readonly=True)
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
        readonly=True,
        help="INT-034 L6 KYC; seller identity documents are S3 residency data routed to Z4",
    )
    rejection_reason = fields.Text(string="Rejection Justification", readonly=True)

    # CFO Governance Approval (BRU-ECM-01)
    cfo_approved = fields.Boolean(
        string="CFO Operational Approval",
        default=False,
        tracking=True,
        readonly=True,
        help="Mandatory financial and operational sign-off before seller can quote",
    )
    cfo_approval_date = fields.Date(string="CFO Approval Date", readonly=True)
    cfo_approved_by = fields.Many2one("res.users", string="CFO Approved By", readonly=True)
    compliance_reviewer_id = fields.Many2one(
        "res.users", string="Compliance Reviewer", readonly=True
    )

    # Category Qualification & Accreditation (BRU-ECM-07)
    category_ids = fields.Many2many(
        "product.category",
        string="Approved Service Categories",
        help="Seller may quote/list ONLY in categories where verified/qualified",
    )

    # Performance, Tiering & Dispute Holds
    rating = fields.Float(string="Review Rating (0-5)", default=0.0, readonly=True)
    total_jobs = fields.Integer(string="Total Completed Jobs", default=0, readonly=True)
    # A seller has no tier until their performance is MEASURED (fix.seller.score)
    tier = fields.Selection(
        SELLER_TIERS, default="unrated", required=True, tracking=True, readonly=True
    )
    payout_hold = fields.Boolean(
        string="Payout Locked (Dispute Hold)",
        default=False,
        tracking=True,
        readonly=True,
        help="Hard payout lock enforced under BRU-BIL-03 while a dispute or chargeback is open",
    )
    active = fields.Boolean(default=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "kyc_status",
            "kyc_doc_z4_ref",
            "kyc_submission_date",
            "kyc_verified_date",
            "rejection_reason",
            "compliance_reviewer_id",
            "cfo_approved",
            "cfo_approval_date",
            "cfo_approved_by",
            "rating",
            "total_jobs",
            "tier",
            "payout_hold",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.kyc_status == "verified":
            locked |= {"nid_number", "trade_license_no", "tin_number", "partner_id"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            identity = {"nid_number", "trade_license_no", "tin_number"} & set(vals)
            for rec in self.filtered(lambda r: r.kyc_status == "verified"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in identity):
                    raise UserError(
                        "%s is KYC-verified: its identity documents change only through a new "
                        "KYC submission (reject, then re-submit)." % rec.name
                    )
        return super().write(vals)

    # ---- approval-engine hooks ----------------------------------------------
    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.kyc_status == "verified" and not self.cfo_approved

    def _approval_excluded(self):
        """The KYC reviewer and the seller's own accounts never approve."""
        excluded = super()._approval_excluded()
        return excluded | (self.compliance_reviewer_id | _seller_users(self)).sudo()

    def _approval_clear_stamp(self, reason):
        # A voided approval (e.g. the seller's party re-pointed) withdraws
        # the CFO approval it granted.
        for rec in self.filtered("cfo_approved"):
            rec.sudo()._guarded().write(
                {"cfo_approved": False, "cfo_approval_date": False, "cfo_approved_by": False}
            )
            rec.sudo().message_post(body="CFO approval withdrawn: %s" % reason)
        return super()._approval_clear_stamp(reason)

    def _recompute_payout_hold(self):
        """BRU-BIL-03: the hold is ON while the seller has an open dispute or
        an open chargeback, and only then."""
        Dispute = self.env["fix.marketplace.dispute"].sudo()
        Chargeback = self.env["fix.marketplace.chargeback"].sudo()
        for rec in self:
            hold = bool(
                Dispute.search_count(
                    [("seller_id", "=", rec.id), ("state", "in", list(OPEN_DISPUTE_STATES))]
                )
                or Chargeback.search_count(
                    [("seller_id", "=", rec.id), ("state", "in", ["received", "contested"])]
                )
            )
            if rec.payout_hold != hold:
                rec.sudo()._guarded().write({"payout_hold": hold})
        return True

    # ---- KYC ----------------------------------------------------------------
    def action_submit_kyc(
        self, nid_number=None, trade_license_no=None, tin_number=None, doc_payload=None
    ):
        """Submit seller identity documents. Routes S3 classified data through libs.py.fix_residency (FF-09)."""
        today = fields.Date.context_today(self)
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Submitting seller KYC")
            if rec.kyc_status == "verified":
                raise UserError("%s is already KYC-verified." % rec.name)
            identity = {}
            if nid_number:
                identity["nid_number"] = nid_number
            if trade_license_no:
                identity["trade_license_no"] = trade_license_no
            if tin_number:
                identity["tin_number"] = tin_number
            if identity:
                rec.write(identity)

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

            rec._guarded().write(
                {
                    "kyc_doc_z4_ref": z4_ref,
                    "kyc_submission_date": today,
                    "kyc_status": "in_review",
                    "rejection_reason": False,
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
        """CFO operational sign-off gate (BRU-ECM-01). The M63 apply method:
        a DOFA Tier 4 holder approves from the inbox, after KYC, and never
        the KYC reviewer or the seller himself (A04 M12-1)."""
        self._approval_assert_routed()
        trusted = self.env.su and not self._approval_task()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.kyc_status != "verified":
                raise UserError(
                    "%s is not KYC-verified (%s): CFO approval comes after KYC (BRU-ECM-01)."
                    % (rec.name, rec.kyc_status)
                )
            if rec.cfo_approved:
                raise UserError("%s is already CFO-approved." % rec.name)
            if not trusted:
                if not authority.has_group(CFO_GROUP):
                    raise UserError(
                        "Seller CFO approval needs DOFA Tier 4 (CFO / CCO / COO), which %s "
                        "does not hold." % authority.name
                    )
                if acting & (rec.compliance_reviewer_id | rec.create_uid | _seller_users(rec)):
                    raise UserError(
                        "Segregation of duties: the KYC reviewer, the person who onboarded "
                        "%s and its own accounts do not CFO-approve it." % rec.name
                    )
            rec._guarded().write(
                {
                    "cfo_approved": True,
                    "cfo_approval_date": today,
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
        return True

    def action_verify_kyc(self):
        """Compliance verifies the KYC documents. A04 M12-1: this used to
        tick CFO approval for the same user; CFO approval is now a separate
        decision by someone else (Request Approval)."""
        today = fields.Date.context_today(self)
        for rec in self:
            _assert_role(self.env, COMPLIANCE_GROUP, "Verifying seller KYC")
            allowed = ("in_review", "pending") if self.env.su else ("in_review",)
            if rec.kyc_status not in allowed:
                raise UserError(
                    "%s is %s: KYC is verified from compliance review (submit it first)."
                    % (rec.name, rec.kyc_status)
                )
            rec._guarded().write(
                {
                    "kyc_status": "verified",
                    "kyc_verified_date": today,
                    "compliance_reviewer_id": self.env.user.id,
                    "rejection_reason": False,
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

    def action_reject_kyc(self, reason="Document verification failed / invalid trade license"):
        """Reject seller KYC application (and withdraw any CFO approval)."""
        for rec in self:
            _assert_role(self.env, COMPLIANCE_GROUP, "Rejecting seller KYC")
            if not (reason or "").strip():
                raise UserError("Give the reason the KYC is rejected.")
            rec._guarded().write(
                {
                    "kyc_status": "rejected",
                    "rejection_reason": reason,
                    "compliance_reviewer_id": self.env.user.id,
                    "cfo_approved": False,
                    "cfo_approval_date": False,
                    "cfo_approved_by": False,
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

    def _tier_commission_rate(self) -> float:
        """The commission rate this seller's tier earns (A04 C6)."""
        self.ensure_one()
        Order = self.env["fix.marketplace.order"]
        raw = self.env["ir.config_parameter"].sudo().get_param(TIER_RATE_PARAM % (self.tier or ""))
        if raw:
            try:
                rate = float(raw)
            except ValueError:
                rate = 0.0
            if 0 < rate <= 1:
                return rate
            logger.warning("Ignoring commission rate %r for tier %s", raw, self.tier)
        return Order._default_commission_rate()


class FixMarketplaceOrder(models.Model):
    """Journey 7: marketplace order -> seller quote -> selection -> job
    -> review -> commission -> payout.
    Includes M14 Refurbished Resale Wiring and Ephemeral Customer Contact Masking (BRU-ECM-05)."""

    _name = "fix.marketplace.order"
    _description = "Marketplace Order"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    state = fields.Selection(
        ORDER_STATES, default="open", required=True, tracking=True, readonly=True
    )

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
    awarded_price = fields.Monetary(
        string="Awarded Price",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The selected quote's price, pinned at award (A04 M12-7): the gross the "
        "commission is earned on",
    )
    commission_amount = fields.Monetary(
        string="Commission Earned",
        currency_field="currency_id",
        readonly=True,
        help="Set when commission.earned is published (M53 settlement consumes this)",
    )
    commission_rate = fields.Float(
        string="Platform Commission Rate",
        digits=(5, 4),
        readonly=True,
        default=lambda self: self._default_commission_rate(),
        help="0-1. Pinned at award from the seller's tier (system parameters "
        + TIER_RATE_PARAM % "<tier>"
        + ", else "
        + COMMISSION_RATE_PARAM
        + "); never edited per order",
    )
    # Real performance evidence for seller scoring (fix.seller.score)
    started_at = fields.Datetime(string="Job Started", readonly=True, copy=False)
    completed_at = fields.Datetime(string="Job Completed", readonly=True, copy=False)
    delivery_confirmed_at = fields.Datetime(
        string="Customer Confirmed Delivery",
        readonly=True,
        copy=False,
        help="The customer's sign-off (Review): the delivery evidence the 7-day escrow "
        "runs from",
    )
    review_rating = fields.Integer(
        string="Customer Rating (1-5)",
        copy=False,
        readonly=True,
        help="0 = the customer gave no rating",
    )
    paid_at = fields.Datetime(string="Payout Released", readonly=True, copy=False)
    paid_by_id = fields.Many2one("res.users", string="Payout Released By", readonly=True)

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
        help="Statutory 7-day escrow hold after the customer confirmed delivery under "
        "Digital Commerce Guidelines 2021",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "customer_contact_revealed",
            "revealed_seller_id",
            "selected_quote_id",
            "awarded_price",
            "commission_amount",
            "commission_rate",
            "started_at",
            "completed_at",
            "delivery_confirmed_at",
            "review_rating",
            "paid_at",
            "paid_by_id",
        }

    def _fix_frozen_fields(self) -> set:
        self.ensure_one()
        if self.state in CLOSED_ORDER_STATES:
            return {
                n
                for n, f in self._fields.items()
                if f.store and not n.startswith(("message_", "activity_", "website_message"))
            }
        if self.state not in BIDDING_STATES:
            return {
                "budget",
                "customer_id",
                "category_id",
                "order_type",
                "currency_id",
                "graded_stock_id",
                "tradein_request_id",
            }
        return set()

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= self._fix_frozen_fields()
        return locked

    @api.depends("completed_at", "delivery_confirmed_at")
    def _compute_payout_escrow(self):
        for rec in self:
            basis = rec.delivery_confirmed_at or rec.completed_at
            if basis:
                rec.payout_available_date = (basis + timedelta(days=ESCROW_DAYS)).date()
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
        _assert_role(self.env, OPERATOR_GROUP, "Creating a marketplace order")
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

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                changed = {
                    n
                    for n in set(vals) & rec._fix_frozen_fields()
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                }
                if changed:
                    raise UserError(
                        "%s cannot be changed on %s: the order is %s."
                        % (
                            ", ".join(sorted(rec._fields[n].string or n for n in changed)),
                            rec.name,
                            dict(ORDER_STATES).get(rec.state),
                        )
                    )
        return super().write(vals)

    def action_select_quote(self, quote):
        """Transparent quote selection (BRU-ECM-05): award order and reveal ephemeral contact.
        A04 M12-7/-8: the awarded price and the seller tier's commission rate
        are pinned here; the category gate holds for a seller with no
        categories (BRU-ECM-07)."""
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Selecting a seller quote")
            if rec.state not in BIDDING_STATES:
                raise UserError("Quotes can only be selected from Open or Quoted states.")
            if quote.marketplace_order_id.id != rec.id:
                raise UserError("Selected quote does not belong to this marketplace order.")
            if quote.state != "submitted":
                raise UserError("Only a submitted quote can be selected (it is %s)." % quote.state)
            seller = quote.seller_id
            if seller.kyc_status != "verified" or not seller.cfo_approved:
                raise UserError("Cannot select an unverified or unapproved seller (BRU-ECM-01).")

            # Category qualification (BRU-ECM-07): a seller quotes ONLY where
            # qualified, so a seller with no approved categories is not.
            if rec.category_id and rec.category_id not in seller.category_ids:
                raise UserError(
                    f"Seller {seller.name} is not certified for category {rec.category_id.name} (BRU-ECM-07)."
                )

            # Update quote states
            rec.quote_ids.filtered(lambda q: q.id != quote.id)._guarded().write(
                {"state": "not_selected"}
            )
            quote._guarded().write({"state": "selected"})

            # Reveal ephemeral contact strictly for this awarded job (BRU-ECM-05)
            rec._guarded().write(
                {
                    "state": "selected",
                    "selected_quote_id": quote.id,
                    "awarded_price": quote.quoted_price,
                    "commission_rate": seller._tier_commission_rate(),
                    "customer_contact_revealed": True,
                    "revealed_seller_id": seller.id,
                }
            )
            publish(
                self.env,
                "order.selected",
                "fix.marketplace.order",
                rec.id,
                {
                    "seller": seller.name,
                    "seller_id": seller.id,
                    "price": float(quote.quoted_price),
                },
            )
            publish(
                self.env,
                "marketplace.contact_revealed",
                "fix.marketplace.order",
                rec.id,
                {
                    "seller_id": seller.id,
                    "order": rec.name,
                },
            )

    def action_start_job(self):
        """Move order to in_progress upon seller job execution."""
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Starting a marketplace job")
            if rec.state != "selected":
                raise UserError("Order must be selected before work commences.")
            rec._guarded().write({"state": "in_progress", "started_at": fields.Datetime.now()})

    def action_complete(self):
        """Job completion: closes the ephemeral contact window and advances to completed."""
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Completing a marketplace job")
            if not rec.selected_quote_id:
                raise UserError("No seller selected.")
            if rec.state != "in_progress":
                # Completing a reviewed/commissioned order again would re-open
                # the commission path and accrue commission twice.
                raise UserError("Only a job in progress can be completed.")
            rec._guarded().write(
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
        customer's 1-5 rating, when given, feeds the seller's measured score.
        The sign-off is the delivery evidence the escrow runs from."""
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Recording the customer's sign-off")
            if rec.state != "completed":
                raise UserError("Customer review requires completed job.")
            vals = {"state": "reviewed", "delivery_confirmed_at": fields.Datetime.now()}
            if rating not in (None, False, ""):
                vals["review_rating"] = int(rating)
            rec._guarded().write(vals)

    def action_earn_commission(self):
        """THE M12 <-> M53 BREAK (Appendix E Pair 12):
        M12 publishes commission.earned; M12 NEVER directly calls M53 settlement models.
        Strictly enforces BRU-BIL-03 payout lock if any dispute is active."""
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Earning marketplace commission")
            if rec.state != "reviewed":
                raise UserError("Review required before platform commission calculation.")
            if rec.has_open_dispute:
                raise UserError(
                    "Commission and payout blocked: order has active unresolved disputes (BRU-BIL-03)."
                )
            quote = rec.selected_quote_id
            if not quote:
                raise UserError("Order %s has no awarded seller to earn on." % rec.name)
            seller = quote.seller_id
            # Pinned at award; orders awarded before the pin read the tier now.
            rate = rec.commission_rate or seller._tier_commission_rate()
            if not 0 < rate <= 1:
                raise UserError(
                    "No platform commission rate is set on %s or in the system "
                    "parameter %s" % (rec.name, COMMISSION_RATE_PARAM)
                )
            gross_price = rec.awarded_price or quote.quoted_price
            commission = rec.currency_id.round(gross_price * rate)

            rec._guarded().write(
                {
                    "state": "commissioned",
                    "commission_amount": commission,
                    "commission_rate": rate,
                    "awarded_price": gross_price,
                }
            )

            # THE DECOUPLED OUTBOX EVENT — consumed asynchronously by M53 Settlement Engine
            publish(
                self.env,
                "commission.earned",
                "fix.marketplace.order",
                rec.id,
                {
                    "order_id": rec.id,
                    "seller_id": seller.id,
                    "seller_partner_id": seller.partner_id.id,
                    "seller_tier": seller.tier,
                    "order": rec.name,
                    "gross": float(gross_price),
                    "rate": float(rate),
                    "commission": float(commission),
                    "currency": rec.currency_id.name or "BDT",
                    "payout_available_date": str(rec.payout_available_date or ""),
                },
            )

    def action_paid(self):
        """Mark order as payout completed once settlement engine finishes disbursement (FLAW-12.2).

        A04 M12-5/-6: the 7-day escrow had a caller switch (skip_escrow_check)
        and could be passed by a backdated or missing completion date, and the
        seller-level payout hold was never read. None of it is a caller option
        now, for anyone: the payout needs a completed job, the customer's
        delivery confirmation 7 days ago, no open dispute and no seller hold."""
        today = fields.Date.context_today(self)
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Releasing a marketplace payout")
            if rec.state != "commissioned":
                raise UserError("Payout requires the commission to be earned first.")
            if not (rec.selected_quote_id and rec.completed_at and rec.payout_available_date):
                raise UserError(
                    "Order %s has no completed, customer-confirmed job to pay out." % rec.name
                )
            if rec.has_open_dispute:
                raise UserError("Cannot mark paid: order has open disputes (BRU-BIL-03).")
            seller = rec.selected_quote_id.seller_id
            if seller.payout_hold:
                raise UserError(
                    "Cannot mark paid: seller %s is under a payout hold (open dispute or "
                    "chargeback, BRU-BIL-03)." % seller.name
                )
            if rec.payout_available_date > today:
                raise UserError(
                    "Digital Commerce Operational Guidelines 2021 Escrow Hold: Payout blocked until %s "
                    "(mandatory 7-day post-delivery customer inspection window)."
                    % rec.payout_available_date
                )
            rec._guarded().write(
                {"state": "paid", "paid_at": fields.Datetime.now(), "paid_by_id": self.env.uid}
            )

    def action_cancel(self):
        """Cancel an order before the job starts."""
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Cancelling a marketplace order")
            if rec.state not in ("open", "quoted", "selected"):
                raise UserError("Only an order whose job has not started can be cancelled.")
            rec._guarded().write({"state": "cancelled", "customer_contact_revealed": False})
            rec.quote_ids.filtered(lambda q: q.state == "submitted")._guarded().write(
                {"state": "not_selected"}
            )

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
        _assert_role(self.env, OPERATOR_GROUP, "Listing a refurbished device")
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
    """A seller's quote on a marketplace order. A04 M12-7: the quote is the
    seller's offer; once submitted it is not edited (8,000 became 48,000 after
    award), and only the operator's selection changes its state."""

    _name = "fix.seller.quote"
    _description = "Seller Quote"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

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
        readonly=True,
    )

    _OFFER_FIELDS = frozenset(
        {"quoted_price", "eta_days", "seller_id", "marketplace_order_id", "currency_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= set(self._OFFER_FIELDS)
        return locked

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
            order = (
                self.env["fix.marketplace.order"].sudo().browse(vals.get("marketplace_order_id"))
            )
            if order and order.state not in BIDDING_STATES:
                raise UserError(
                    "Quotes are only accepted on open jobs (%s is %s)." % (order.name, order.state)
                )
        recs = super().create(vals_list)
        for rec in recs:
            if rec.marketplace_order_id.state == "open":
                # The first quote moves the job to "quoted": a system
                # transition, so the seller needs no write access on the order.
                rec.marketplace_order_id.sudo()._guarded().write({"state": "quoted"})
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

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                changed = [
                    n
                    for n in self._OFFER_FIELDS & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "A quote is the seller's offer and is not edited once submitted "
                        "(%s); the seller submits a new quote instead."
                        % ", ".join(rec._fields[n].string or n for n in changed)
                    )
        return super().write(vals)

    def action_select(self):
        """The operator awards the job to this quote."""
        for rec in self:
            rec.marketplace_order_id.action_select_quote(rec)
        return True


class FixSellerScore(models.Model):
    """Transparent scoring & tier ranking — the named adoption mitigation for sellers.
    A04 C5: the KPIs are MEASURED (action_measure), never typed."""

    _name = "fix.seller.score"
    _description = "Seller Score & Ranking"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

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
        readonly=True,
        help="Selected quotes / decided quotes (selected + not selected)",
    )
    on_time_rate = fields.Float(
        string="On-Time Delivery (0-1)",
        default=0.0,
        readonly=True,
        help="Jobs completed within the quoted ETA / timed jobs",
    )
    review_rating = fields.Float(
        string="Review Rating (0-5)",
        default=0.0,
        readonly=True,
        help="Mean customer rating of rated jobs",
    )
    dispute_rate = fields.Float(
        string="Dispute Rate (0-1)",
        default=0.0,
        readonly=True,
        help="Awarded jobs with a dispute / awarded jobs",
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

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "acceptance_rate",
            "on_time_rate",
            "review_rating",
            "dispute_rate",
            "quotes_decided",
            "orders_awarded",
            "orders_timed",
            "orders_rated",
            "metrics_measured",
        }

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
            _assert_role(self.env, OPERATOR_GROUP, "Measuring a seller score")
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
            rec._guarded().write(
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
            _assert_role(self.env, OPERATOR_GROUP, "Ranking a seller")
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

            rec.seller_id._guarded().write({"tier": tier})
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
    """M12: Transparent dispute resolution with 48h SLA and hard payout lock (BRU-BIL-03).

    A04 M12-3/-4 state machine: raised -> investigating -> arbitration ->
    resolved, with escalated (past the 48h SLA) still open. An operator
    proposes the ruling and sends it to arbitration; a Marketplace Dispute
    Arbitrator decides it from the M63 inbox; a resolved dispute is final."""

    _name = "fix.marketplace.dispute"
    _description = "Marketplace Dispute"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "create_date desc"

    _approval_domain = "marketplace_dispute_ruling"
    _approval_apply_method = "action_resolve"
    _approval_group = ARBITRATOR_GROUP
    _approval_routed = True

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
    escalated_at = fields.Datetime(readonly=True, copy=False)

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
        readonly=True,
    )
    investigator_id = fields.Many2one("res.users", string="Investigated By", readonly=True)

    # The ruling the investigating operator proposes to the arbitrator.
    proposed_resolution = fields.Selection(
        [
            ("refund_customer", "Full Refund to Customer"),
            ("payout_seller", "Dismissed - Release Full Payout to Seller"),
            ("split_settlement", "Split Settlement / Mutual Concession"),
            ("rework_order", "Free Warranty Rework Scheduled"),
        ],
        string="Proposed Ruling",
    )
    proposed_refund_amount = fields.Monetary(
        string="Proposed Refund to Customer",
        currency_field="currency_id",
        help="Full refund: the disputed amount. Split: the customer's part.",
    )
    proposed_by_id = fields.Many2one("res.users", string="Ruling Proposed By", readonly=True)
    resolution_type = fields.Selection(
        [
            ("refund_customer", "Full Refund to Customer"),
            ("payout_seller", "Dismissed - Release Full Payout to Seller"),
            ("split_settlement", "Split Settlement / Mutual Concession"),
            ("rework_order", "Free Warranty Rework Scheduled"),
        ],
        string="Resolution Ruling",
        tracking=True,
        readonly=True,
    )
    refund_amount = fields.Monetary(
        string="Refund Ruled",
        currency_field="currency_id",
        readonly=True,
        help="What the ruling refunds the customer (M19 credit / M53 forfeit, via the event)",
    )
    resolution_notes = fields.Text(string="Arbitration & Resolution Rationale")
    resolved_by = fields.Many2one("res.users", string="Arbitrated By", readonly=True)
    resolved_date = fields.Datetime(string="Resolution Timestamp", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "escalated_at",
            "investigator_id",
            "proposed_by_id",
            "resolution_type",
            "refund_amount",
            "resolved_by",
            "resolved_date",
        }

    def _fix_frozen_fields(self) -> set:
        self.ensure_one()
        if self.state == "resolved":
            return {
                n
                for n, f in self._fields.items()
                if f.store and not n.startswith(("message_", "activity_", "website_message"))
            }
        # the 48h SLA is set when the dispute is raised and never moved
        frozen = {"order_id", "seller_id", "customer_id", "currency_id", "sla_deadline"}
        if self.state == "arbitration":
            frozen |= {"proposed_resolution", "proposed_refund_amount", "resolution_notes"}
        return frozen

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= self._fix_frozen_fields()
        return locked

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
        _assert_role(self.env, OPERATOR_GROUP, "Raising a marketplace dispute")
        now = fields.Datetime.now()
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("fix.marketplace.dispute") or "DSP/New"
            )
            order = self.env["fix.marketplace.order"].sudo().browse(vals.get("order_id"))
            awarded = order.selected_quote_id.seller_id if order else None
            if awarded and vals.get("seller_id") and awarded.id != vals["seller_id"]:
                raise ValidationError(
                    "A dispute on %s is against the seller who was awarded it (%s)."
                    % (order.name, awarded.name)
                )
            if vals.get("sla_deadline") and not self.env.su:
                raise UserError("The 48-hour SLA deadline is set when the dispute is raised.")
            vals.setdefault("sla_deadline", now + timedelta(hours=48))
        recs = super().create(vals_list)
        for rec in recs:
            # Enforce hard payout lock on seller (BRU-BIL-03)
            rec.seller_id._recompute_payout_hold()
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

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                changed = {
                    n
                    for n in set(vals) & rec._fix_frozen_fields()
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                }
                if changed:
                    raise UserError(
                        "%s cannot be changed on %s: %s."
                        % (
                            ", ".join(sorted(rec._fields[n].string or n for n in changed)),
                            rec.name,
                            "a resolved dispute is final"
                            if rec.state == "resolved"
                            else "the ruling is with the arbitrator"
                            if rec.state == "arbitration"
                            else "a dispute stays on its order, seller and customer",
                        )
                    )
        return super().write(vals)

    # ---- approval-engine hooks ----------------------------------------------
    def _approval_amount(self) -> float:
        return abs(self.proposed_refund_amount or 0.0)

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.state in RULING_STATES and bool(self.proposed_resolution)

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {
            "proposed_resolution",
            "order_id",
            "seller_id",
        }

    def _approval_excluded(self):
        """The person who raised it, the one who proposed the ruling and the
        seller's own accounts never arbitrate it."""
        excluded = super()._approval_excluded()
        return excluded | (self.proposed_by_id | _seller_users(self.seller_id)).sudo()

    def _approval_on_rejected(self, comment):
        # The ruling goes back to the investigation (the request is already
        # closed, so this voids nothing).
        for rec in self.filtered(lambda r: r.state in RULING_STATES):
            rec.sudo()._guarded().write({"state": "investigating"})
            rec.sudo().message_post(
                body="Proposed ruling sent back by the arbitrator: %s" % (comment or "-")
            )

    def _refund_for(self, ruling, proposed):
        self.ensure_one()
        disputed = self.disputed_amount or 0.0
        if ruling == "refund_customer":
            return proposed or disputed
        if ruling == "split_settlement":
            return proposed or 0.0
        return 0.0

    # ---- lifecycle ----------------------------------------------------------
    def action_investigate(self):
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Investigating a dispute")
            if rec.state != "raised":
                raise UserError("Only a raised dispute goes under investigation.")
            rec._guarded().write({"state": "investigating", "investigator_id": self.env.uid})

    def action_arbitrate(self):
        """Send the proposed ruling to a Marketplace Dispute Arbitrator."""
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Sending a dispute to arbitration")
            if rec.state not in ("investigating", "escalated"):
                raise UserError(
                    "A dispute goes to arbitration from the investigation (it is %s)." % rec.state
                )
            ruling = rec.proposed_resolution
            if not ruling or not (rec.resolution_notes or "").strip():
                raise UserError(
                    "Propose the ruling and its rationale before sending %s to arbitration."
                    % rec.name
                )
            refund = rec._refund_for(ruling, rec.proposed_refund_amount)
            ceiling = rec.disputed_amount or rec.order_id.awarded_price or 0.0
            if refund < 0 or (ceiling and refund > ceiling + 0.005):
                raise UserError(
                    "The refund proposed (%.2f) must be between 0 and the disputed amount "
                    "(%.2f)." % (refund, ceiling)
                )
            if ruling == "split_settlement" and not refund:
                raise UserError("A split settlement names the customer's refund.")
            if rec.approval_state == "pending":
                raise UserError("%s is already with the arbitrator." % rec.name)
            rec._guarded().write(
                {
                    "state": "arbitration" if rec.state == "investigating" else rec.state,
                    "proposed_by_id": self.env.uid,
                    "proposed_refund_amount": refund,
                }
            )
            rec.action_request_approval(
                justification="Proposed ruling: %s (refund %.2f). %s"
                % (
                    dict(self._fields["proposed_resolution"].selection)[ruling],
                    refund,
                    rec.resolution_notes,
                )
            )
        return True

    def action_resolve(self, resolution_type=None, notes=None):
        """Resolve dispute, record ruling, and clear payout lock if no other disputes exist.

        The M63 apply method: an arbitrator decides the proposed ruling from
        the inbox (A04 M12-3). Superuser service code may pass the ruling;
        nobody re-rules a resolved dispute."""
        self._approval_assert_routed()
        trusted = self.env.su and not self._approval_task()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            if rec.state == "resolved":
                raise UserError("%s is resolved; a ruling is final." % rec.name)
            if rec.state not in OPEN_DISPUTE_STATES:
                raise UserError("%s is not an open dispute." % rec.name)
            if trusted:
                ruling = resolution_type or rec.proposed_resolution or "payout_seller"
                text = notes or rec.resolution_notes or "Arbitration complete"
            else:
                if rec.state not in RULING_STATES or not rec.proposed_resolution:
                    raise UserError("%s has no ruling in arbitration." % rec.name)
                if resolution_type and resolution_type != rec.proposed_resolution:
                    raise UserError("The arbitrator decides the ruling that was proposed.")
                if not authority.has_group(ARBITRATOR_GROUP):
                    raise UserError(
                        "A dispute is ruled by a Marketplace Dispute Arbitrator, which %s is "
                        "not." % authority.name
                    )
                if acting & (rec.create_uid | rec.proposed_by_id | _seller_users(rec.seller_id)):
                    raise UserError(
                        "Segregation of duties: whoever raised %s, proposed its ruling or acts "
                        "for the seller does not arbitrate it." % rec.name
                    )
                ruling = rec.proposed_resolution
                text = rec.resolution_notes
            refund = rec._refund_for(ruling, rec.proposed_refund_amount)
            rec._guarded().write(
                {
                    "state": "resolved",
                    "resolution_type": ruling,
                    "refund_amount": refund,
                    "resolution_notes": text,
                    "resolved_by": self.env.user.id,
                    "resolved_date": fields.Datetime.now(),
                }
            )
            rec.seller_id._recompute_payout_hold()
            unlocked = not rec.seller_id.payout_hold

            publish(
                self.env,
                "marketplace.dispute_resolved",
                "fix.marketplace.dispute",
                rec.id,
                {
                    "dispute": rec.name,
                    "order": rec.order_id.name,
                    "order_id": rec.order_id.id,
                    "seller": rec.seller_id.name,
                    "seller_id": rec.seller_id.id,
                    "seller_partner_id": rec.seller_id.partner_id.id,
                    "customer_id": rec.customer_id.id,
                    "resolution": ruling,
                    "disputed_amount": float(rec.disputed_amount or 0.0),
                    "refund_amount": float(refund),
                    "currency": rec.currency_id.name or "BDT",
                    "payout_unlocked": unlocked,
                },
            )
        return True

    def action_escalate(self):
        """Escalate unresolved dispute past 48h SLA to executive arbitration."""
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Escalating a dispute")
            if rec.state not in ("raised", "investigating", "arbitration"):
                raise UserError("Only an open, not yet escalated dispute is escalated.")
            rec._guarded().write({"state": "escalated", "escalated_at": fields.Datetime.now()})
            rec.seller_id._guarded().write({"tier": "at_risk"})
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

    @api.model
    def cron_dispute_sla_escalation(self) -> int:
        """C10 (A04 M12-12): the 48-hour SLA was a deadline nothing acted on.
        Every open dispute past it is escalated once (idempotent through
        escalated_at; an already escalated dispute is left alone)."""
        late = self.sudo().search(
            [
                ("state", "in", ["raised", "investigating", "arbitration"]),
                ("sla_deadline", "!=", False),
                ("sla_deadline", "<", fields.Datetime.now()),
                ("escalated_at", "=", False),
            ],
            limit=500,
        )
        for rec in late:
            rec.action_escalate()
        return len(late)


class FixApprovalMatrixMarketplace(models.Model):
    """A04 C9: the M12 routed decisions on the DoA register."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("marketplace_seller_cfo", "Marketplace Seller CFO Approval"),
            ("marketplace_listing", "Marketplace Listing Approval"),
            ("marketplace_dispute_ruling", "Marketplace Dispute Ruling"),
        ],
        ondelete={
            "marketplace_seller_cfo": "cascade",
            "marketplace_listing": "cascade",
            "marketplace_dispute_ruling": "cascade",
        },
    )
