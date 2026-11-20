# fix_marketplace — M12: sellers, orders, quotes, scoring, commission events.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

ORDER_STATES = [
    ("open", "Open for Quotes"), ("quoted", "Quotes Received"),
    ("selected", "Seller Selected"), ("in_progress", "Job In Progress"),
    ("completed", "Completed"), ("reviewed", "Reviewed"),
    ("commissioned", "Commission Earned"), ("paid", "Payout Complete"),
    ("cancelled", "Cancelled"),
]


class FixMarketplaceSeller(models.Model):
    """A seller is a PARTY ROLE on M33 — one res.partner may hold
    both customer and seller roles simultaneously."""
    _name = "fix.marketplace.seller"
    _description = "Marketplace Seller"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M12",
        "form": "Seller Application",
        "fields": ["name", "partner_id", "kyc_status", "kyc_ref"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", string="Party (M33)",
                                  required=True, ondelete="restrict",
                                  help="The party master record — a seller may "
                                       "also be a customer")
    kyc_status = fields.Selection(
        [("pending", "KYC Pending"), ("verified", "KYC Verified"),
         ("rejected", "KYC Rejected")],
        default="pending", required=True, tracking=True,
        help="INT-034 L6 KYC; seller identity documents are S3 "
             "residency data routed to Z4")
    kyc_ref = fields.Char(string="KYC Reference",
                          help="The KYC provider's reference; documents "
                               "never land here (Z4 only)")
    rating = fields.Float(string="Rating (0-5)", default=0.0)
    total_jobs = fields.Integer(default=0)
    active = fields.Boolean(default=True)

    def action_verify_kyc(self):
        for rec in self:
            rec.kyc_status = "verified"
            publish(self.env, "seller.kyc_verified",
                    "fix.marketplace.seller", rec.id,
                    {"seller": rec.name})


class FixMarketplaceOrder(models.Model):
    """Journey 7: marketplace order -> seller quote -> selection -> job
    -> review -> commission -> payout."""
    _name = "fix.marketplace.order"
    _description = "Marketplace Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True,
                       default=lambda self: "New")
    customer_id = fields.Many2one("res.partner", string="Customer",
                                  required=True, index=True)
    service_order_id = fields.Many2one("fix.service.order",
                                       string="Service Order (M01)",
                                       ondelete="set null")
    description = fields.Text(required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    budget = fields.Monetary(string="Customer Budget",
                             currency_field="currency_id")
    state = fields.Selection(ORDER_STATES, default="open",
                             required=True, tracking=True)
    quote_ids = fields.One2many("fix.seller.quote", "marketplace_order_id",
                                 string="Seller Quotes")
    selected_quote_id = fields.Many2one("fix.seller.quote",
                                        string="Selected Quote",
                                        readonly=True)
    commission_amount = fields.Monetary(string="Commission Earned",
                                        currency_field="currency_id",
                                        readonly=True,
                                        help="Set when commission.earned is "
                                             "published (the M53 engine "
                                             "consumes the event)")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fix.marketplace.order") or "MKT/New"
        recs = super().create(vals_list)
        for rec in recs:
            publish(self.env, "marketplace_order.created",
                    "fix.marketplace.order", rec.id,
                    {"order": rec.name, "budget": float(rec.budget)})
        return recs

    def action_select_quote(self, quote):
        """Transparent selection: the seller sees WHY they were selected."""
        for rec in self:
            if rec.state != "quoted":
                raise UserError("Select from 'Quotes Received'")
            if quote.marketplace_order_id.id != rec.id:
                raise UserError("Quote does not belong to this order")
            rec.write({"state": "selected",
                       "selected_quote_id": quote.id})
            publish(self.env, "order.selected", "fix.marketplace.order",
                    rec.id, {"seller": quote.seller_id.name,
                             "price": float(quote.quoted_price)})

    def action_complete(self):
        """Job completion: triggers the commission calculation."""
        for rec in self:
            if not rec.selected_quote_id:
                raise UserError("No seller selected")
            rec.state = "completed"

    def action_earn_commission(self):
        """THE M12<->M53 BREAK: M12 PUBLISHES commission.earned; it NEVER
        calls M53. The settlement engine consumes the event (pair 12)."""
        for rec in self:
            if rec.state != "reviewed":
                raise UserError("Review before commission")
            quote = rec.selected_quote_id
            commission = quote.quoted_price * 0.10  # 10% platform commission
            rec.write({"state": "commissioned",
                       "commission_amount": commission})
            # THE EVENT — M53's commission engine consumes this.
            # M12 has NO dependency on M53; the break is enforced here.
            publish(self.env, "commission.earned",
                    "fix.marketplace.order", rec.id, {
                        "seller_id": quote.seller_id.id,
                        "order": rec.name,
                        "gross": float(quote.quoted_price),
                        "commission": float(commission)})


class FixSellerQuote(models.Model):
    """A seller's response to a marketplace order."""
    _name = "fix.seller.quote"
    _description = "Seller Quote"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    marketplace_order_id = fields.Many2one("fix.marketplace.order",
                                            required=True,
                                            ondelete="cascade", index=True)
    seller_id = fields.Many2one("fix.marketplace.seller", required=True,
                                 ondelete="restrict", index=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    quoted_price = fields.Monetary(string="Quoted Price",
                                   currency_field="currency_id", required=True)
    eta_days = fields.Integer(string="ETA (days)", required=True, default=3)
    notes = fields.Text()
    state = fields.Selection([("submitted", "Submitted"),
                              ("selected", "Selected"),
                              ("not_selected", "Not Selected")],
                             default="submitted", required=True)

    @api.constrains("quoted_price")
    def _check_price(self):
        for rec in self:
            if rec.quoted_price <= 0:
                raise UserError("Quoted price must be positive")

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            publish(self.env, "seller.quoted", "fix.seller.quote", rec.id,
                    {"seller": rec.seller_id.name,
                     "price": float(rec.quoted_price)})
        return recs


class FixSellerScore(models.Model):
    """Transparent scoring — the named adoption mitigation for sellers."""
    _name = "fix.seller.score"
    _description = "Seller Score"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    seller_id = fields.Many2one("fix.marketplace.seller", required=True,
                                 ondelete="cascade", index=True)
    period = fields.Char(required=True, help="YYYY-MM")
    acceptance_rate = fields.Float(string="Acceptance Rate (0-1)")
    on_time_rate = fields.Float(string="On-Time Delivery (0-1)")
    review_rating = fields.Float(string="Review Rating (0-5)")
    dispute_rate = fields.Float(string="Dispute Rate (0-1)")
    composite = fields.Float(compute="_compute_composite", store=True)

    @api.depends("acceptance_rate", "on_time_rate", "review_rating",
                 "dispute_rate")
    def _compute_composite(self):
        for rec in self:
            rec.composite = round(
                (rec.acceptance_rate * 0.3
                 + rec.on_time_rate * 0.3
                 + (rec.review_rating / 5.0) * 0.25
                 - rec.dispute_rate * 0.15), 4)

    def action_publish(self):
        for rec in self:
            publish(self.env, "seller.scored", "fix.seller.score", rec.id,
                    {"seller": rec.seller_id.name,
                     "composite": rec.composite})
