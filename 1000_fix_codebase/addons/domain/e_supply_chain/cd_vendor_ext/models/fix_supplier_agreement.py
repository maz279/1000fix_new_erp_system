# cd_vendor_ext — M42 agreements, agreed prices and price-change
# governance (FR-SRM2-021/022/023/026, CD-M42-01).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_supplier_profile import G_MANAGER, check_sod, require_group

# FR-SRM2-026: warn this many days ahead of agreement expiry.
AGREEMENT_RENEWAL_WARNING_DAYS = 90


class FixSupplierAgreement(models.Model):
    """FR-SRM2-021: a framework, supply, consignment, service or courier
    agreement — term, commitments, service levels, penalties, rebates."""

    _name = "fix.supplier.agreement"
    _description = "Supplier Agreement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "term_to, id"
    _p03_capture = {
        "module": "M42",
        "form": "Supplier Agreement",
        "fields": ["profile_id", "name", "agreement_type", "term_from", "term_to",
                   "currency_id", "committed_value", "committed_volume",
                   "service_levels", "penalties", "rebate_terms", "notice_days",
                   "renewal_mode"],
    }

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="restrict")
    name = fields.Char(string="Agreement Reference", required=True, tracking=True)
    agreement_type = fields.Selection(
        [("framework", "Framework"), ("supply", "Supply"),
         ("consignment", "Consignment"), ("service", "Service"),
         ("courier", "Courier")],
        string="Agreement Type", required=True, default="framework")
    term_from = fields.Date(string="Term From", required=True)
    term_to = fields.Date(string="Term To", required=True, tracking=True)
    currency_id = fields.Many2one("res.currency", string="Currency", required=True,
                                  default=lambda self: self.env.company.currency_id)
    committed_value = fields.Monetary(string="Committed Value",
                                      currency_field="currency_id")
    committed_volume = fields.Float(string="Committed Volume")
    service_levels = fields.Text(string="Service Levels")
    penalties = fields.Text(string="Penalties")
    rebate_terms = fields.Text(string="Rebate Terms")
    notice_days = fields.Integer(string="Notice Period (days)", default=30)
    renewal_mode = fields.Selection(
        [("manual", "Manual Renewal"), ("auto", "Auto-Renew"),
         ("retender", "Re-Tender")],
        string="Renewal Mode", required=True, default="manual")
    price_list_ids = fields.One2many("fix.supplier.price.list", "agreement_id",
                                     string="Agreed Prices")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("expiring", "Expiring"),
         ("expired", "Expired"), ("terminated", "Terminated")],
        string="Status", default="draft", required=True, tracking=True)

    @api.constrains("term_from", "term_to", "notice_days")
    def _check_term(self):
        for agreement in self:
            if agreement.term_to < agreement.term_from:
                raise ValidationError("An agreement cannot end before it starts")
            if agreement.notice_days < 0:
                raise ValidationError("The notice period cannot be negative")

    def action_activate(self):
        """Agreement execution is a Procurement Manager right (§13)."""
        require_group(self.env, G_MANAGER,
                      "Only a Procurement Manager can execute an agreement")
        for agreement in self:
            if agreement.state != "draft":
                raise UserError("Only a draft agreement can be activated")
            if agreement.profile_id.state in ("suspended", "blocked"):
                raise UserError("Cannot activate an agreement with a suspended "
                                "or blocked supplier")
            agreement.state = "active"
            publish(self.env, "supplier.agreement_activated", "fix.supplier.agreement",
                    agreement.id, {"profile_id": agreement.profile_id.id,
                                   "agreement_type": agreement.agreement_type,
                                   "term_to": str(agreement.term_to)})

    def action_terminate(self):
        require_group(self.env, G_MANAGER,
                      "Only a Procurement Manager can terminate an agreement")
        self.write({"state": "terminated"})

    @api.model
    def _cron_agreement_expiry(self):
        """FR-SRM2-026: flag agreements nearing expiry and lapse those past
        their term — never a silent lapse into uncontracted spend."""
        today = fields.Date.today()
        horizon = today + timedelta(days=AGREEMENT_RENEWAL_WARNING_DAYS)
        expiring = self.search([("state", "=", "active"), ("term_to", "<=", horizon),
                                ("term_to", ">=", today)])
        expiring.write({"state": "expiring"})
        lapsed = self.search([("state", "in", ("active", "expiring")),
                              ("term_to", "<", today)])
        lapsed.write({"state": "expired"})
        for agreement in lapsed:
            publish(self.env, "supplier.agreement_expired", "fix.supplier.agreement",
                    agreement.id, {"profile_id": agreement.profile_id.id})
        return len(expiring), len(lapsed)


class FixSupplierPriceList(models.Model):
    """FR-SRM2-022: agreed prices per part per supplier — the authority for
    M16 call-off. Rows change only through an approved price change."""

    _name = "fix.supplier.price.list"
    _description = "Supplier Agreed Price"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "product_id, valid_from desc"

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    agreement_id = fields.Many2one("fix.supplier.agreement", string="Agreement",
                                   index=True, ondelete="cascade")
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Part", required=True,
                                 index=True)
    currency_id = fields.Many2one("res.currency", string="Currency", required=True,
                                  default=lambda self: self.env.company.currency_id)
    price = fields.Monetary(string="Agreed Price", currency_field="currency_id",
                            required=True, tracking=True)
    moq = fields.Float(string="Minimum Order Qty", default=1.0)
    lead_time_days = fields.Integer(string="Lead Time (days)")
    valid_from = fields.Date(string="Valid From", required=True,
                             default=fields.Date.today)
    valid_to = fields.Date(string="Valid To")
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True)

    # FR-SRM2-023: rows are written only by an approved price change (or by
    # a system administrator loading the opening price book, §16.4).
    _GOVERNED = {"price", "product_id", "profile_id", "valid_from", "currency_id"}

    def _check_governed(self):
        if not (self.env.context.get("fix_price_change_approval")
                or self.env.user.has_group("base.group_system")):
            raise UserError("Agreed prices change only through an approved price "
                            "change request (FR-SRM2-023)")

    @api.model_create_multi
    def create(self, vals_list):
        self._check_governed()
        return super().create(vals_list)

    def write(self, vals):
        if self._GOVERNED & set(vals):
            self._check_governed()
        return super().write(vals)

    @api.constrains("price", "valid_from", "valid_to")
    def _check_price(self):
        for row in self:
            if row.price < 0:
                raise ValidationError("An agreed price cannot be negative")
            if row.valid_to and row.valid_to < row.valid_from:
                raise ValidationError("A price cannot expire before it is valid")


class FixSupplierPriceChange(models.Model):
    """FR-SRM2-023: a supplier price increase is submitted, justified and
    approved before it takes effect; M16 cannot order at an unapproved price."""

    _name = "fix.supplier.price.change"
    _description = "Supplier Price Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"
    _p03_capture = {
        "module": "M42",
        "form": "Price Change Request",
        "fields": ["profile_id", "agreement_id", "product_id", "currency_id",
                   "old_price", "proposed_price", "effective_from", "justification"],
    }

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="restrict")
    agreement_id = fields.Many2one("fix.supplier.agreement", string="Agreement",
                                   index=True)
    product_id = fields.Many2one("product.product", string="Part", required=True)
    currency_id = fields.Many2one("res.currency", string="Currency", required=True,
                                  default=lambda self: self.env.company.currency_id)
    old_price = fields.Monetary(string="Current Price", currency_field="currency_id")
    proposed_price = fields.Monetary(string="Proposed Price",
                                     currency_field="currency_id", required=True)
    variance_pct = fields.Float(string="Variance %", compute="_compute_variance",
                                store=True)
    effective_from = fields.Date(string="Effective From", required=True)
    justification = fields.Text(string="Justification", required=True)
    decided_by = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(string="Decided At", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"),
         ("rejected", "Rejected")],
        string="Status", default="draft", required=True, tracking=True)

    @api.depends("old_price", "proposed_price")
    def _compute_variance(self):
        for change in self:
            change.variance_pct = (
                round(100.0 * (change.proposed_price - change.old_price)
                      / change.old_price, 2) if change.old_price else 0.0)

    @api.constrains("proposed_price", "old_price")
    def _check_prices(self):
        for change in self:
            if change.proposed_price < 0 or change.old_price < 0:
                raise ValidationError("Prices cannot be negative")

    @api.constrains("agreement_id", "profile_id")
    def _check_agreement_supplier(self):
        for change in self:
            if change.agreement_id and change.agreement_id.profile_id != change.profile_id:
                raise ValidationError("The agreement belongs to a different supplier")

    def action_submit(self):
        self.filtered(lambda r: r.state == "draft").write({"state": "submitted"})

    def action_approve(self):
        """Approval publishes the new agreed price row; the old row closes
        the day before the new one takes effect."""
        require_group(self.env, G_MANAGER,
                      "Only a Procurement Manager can approve a price change")
        PriceList = self.env["fix.supplier.price.list"].with_context(
            fix_price_change_approval=True)
        for change in self:
            if change.state != "submitted":
                raise UserError("Only a submitted price change can be approved")
            check_sod(change, "create_uid", self.env.user,
                      "The requester of a price change cannot approve it")
            current = PriceList.search([
                ("profile_id", "=", change.profile_id.id),
                ("product_id", "=", change.product_id.id),
                ("valid_from", "<", change.effective_from),
                "|", ("valid_to", "=", False),
                ("valid_to", ">=", change.effective_from)])
            current.write({"valid_to": change.effective_from - timedelta(days=1)})
            PriceList.create({
                "profile_id": change.profile_id.id,
                "agreement_id": change.agreement_id.id,
                "product_id": change.product_id.id,
                "currency_id": change.currency_id.id,
                "price": change.proposed_price,
                "valid_from": change.effective_from,
                "approved_by": self.env.user.id,
            })
            change.write({"state": "approved", "decided_by": self.env.user.id,
                          "decided_at": fields.Datetime.now()})
            publish(self.env, "supplier.price_approved", "fix.supplier.price.change",
                    change.id, {"profile_id": change.profile_id.id,
                                "product_id": change.product_id.id,
                                "price": change.proposed_price,
                                "effective_from": str(change.effective_from)})

    def action_reject(self):
        require_group(self.env, G_MANAGER,
                      "Only a Procurement Manager can reject a price change")
        for change in self:
            if change.state != "submitted":
                raise UserError("Only a submitted price change can be rejected")
        self.write({"state": "rejected", "decided_by": self.env.user.id,
                    "decided_at": fields.Datetime.now()})
