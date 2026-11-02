# M36 quotations & tenders: the versioned quotation over an estimate, its
# internal review loop, and public tenders with their bonds. Estimates and
# counter-sales already exist in cd_service_order / cd_quotation.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixQuotation(models.Model):
    _name = "fix.quotation"
    _description = "Quotation"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    estimate_id = fields.Many2one("fix.estimate", string="Estimate", index=True)
    customer_id = fields.Many2one("res.partner", string="Customer", index=True, ondelete="restrict")
    version = fields.Integer(required=True, default=1)
    value = fields.Monetary(string="Quotation Value", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # Statutory Margin Calculation & TDS (ITA 2023 s.89/90 / FLAW-36.1)
    cost_amount = fields.Monetary(
        string="Estimated Direct Cost", currency_field="currency_id", default=0.0
    )
    vat_rate = fields.Float(string="VAT Rate (%)", default=15.0)
    vat_amount = fields.Monetary(
        string="Mushak VAT Amount",
        currency_field="currency_id",
        compute="_compute_statutory_margins",
        store=True,
    )
    tds_rate = fields.Float(string="Withholding Tax TDS Rate (%)", default=5.0)
    tds_amount = fields.Monetary(
        string="TDS Deduction (ITA 2023 s.89/90)",
        currency_field="currency_id",
        compute="_compute_statutory_margins",
        store=True,
    )
    pretax_margin_bdt = fields.Monetary(
        string="Pre-Tax Operational Margin",
        currency_field="currency_id",
        compute="_compute_statutory_margins",
        store=True,
    )
    net_cash_margin_bdt = fields.Monetary(
        string="Net Cash Margin (After-Tax)",
        currency_field="currency_id",
        compute="_compute_statutory_margins",
        store=True,
    )
    net_cash_margin_pct = fields.Float(
        string="Net Cash Margin (%)",
        compute="_compute_statutory_margins",
        store=True,
    )
    margin_pct = fields.Float(
        string="Margin %",
        compute="_compute_statutory_margins",
        store=True,
        readonly=False,
    )

    @api.depends("value", "cost_amount", "vat_rate", "tds_rate")
    def _compute_statutory_margins(self):
        for rec in self:
            val = rec.value or 0.0
            cost = rec.cost_amount or 0.0
            rec.vat_amount = round(val * (rec.vat_rate / 100.0), 2)
            rec.tds_amount = round(val * (rec.tds_rate / 100.0), 2)
            rec.pretax_margin_bdt = round(val - cost, 2)
            net_cash = round(val - cost - rec.tds_amount, 2)
            rec.net_cash_margin_bdt = net_cash
            rec.net_cash_margin_pct = round((net_cash / val) * 100.0, 2) if val else 0.0
            if val:
                rec.margin_pct = round(((val - cost) / val) * 100.0, 2)

    valid_until = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("accepted", "Accepted"),
            ("declined", "Declined"),
            ("expired", "Expired"),
        ],
        required=True,
        default="draft",
    )
    esign_state = fields.Selection(
        [
            ("none", "Not requested"),
            ("sent", "Signature requested"),
            ("signed", "Signed"),
            ("declined", "Signature declined"),
        ],
        required=True,
        default="none",
    )
    signed_at = fields.Datetime(readonly=True)
    decline_reason = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                seq = self.env["ir.sequence"].sudo().next_by_code("fix.quotation")
                vals["name"] = seq or "QTN/%s/%s" % (
                    fields.Date.today().year,
                    self.search_count([]) + 1,
                )
        return super().create(vals_list)


class FixQuoteReview(models.Model):
    _name = "fix.quote.review"
    _description = "Quotation Internal Review"
    _order = "reviewed_at desc, id desc"

    quotation_id = fields.Many2one("fix.quotation", required=True, ondelete="cascade", index=True)
    reviewer_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    decision = fields.Selection(
        [("approved", "Approved"), ("rejected", "Rejected"), ("revision", "Revision requested")],
        required=True,
        default="approved",
    )
    notes = fields.Char()
    reviewed_at = fields.Datetime(required=True, default=fields.Datetime.now)


class FixTender(models.Model):
    _name = "fix.tender"
    _description = "Tender"
    _order = "due_date, id"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    client_name = fields.Char(string="Tendering Client", required=True)
    due_date = fields.Date(required=True)
    estimated_value = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    compliance_pct = fields.Float(string="Compliance %", default=0.0)
    bonds_required = fields.Boolean()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("won", "Won"),
            ("lost", "Lost"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    outcome_note = fields.Char()

    # Tender lifecycle (A04 zero-trust audit 2026-10-31, DISC-36.2): the model
    # was a passive stub. Governed transitions: submit requires a due date in
    # the future; recording a WIN with bonds_required demands an ACTIVE bond.
    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft tender can be submitted")
            if rec.due_date and rec.due_date < fields.Date.today():
                raise UserError(
                    "Tender %s: submission deadline %s is already in the past"
                    % (rec.name, rec.due_date)
                )
            rec.state = "submitted"

    def action_record_outcome(self, won, note=""):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(
                    "Tender %s is %s — only a submitted tender can be decided"
                    % (rec.name, rec.state)
                )
            if won and rec.bonds_required:
                active_bond = self.env["fix.tender.bond"].search_count(
                    [("tender_id", "=", rec.id), ("state", "=", "active")]
                )
                if not active_bond:
                    raise UserError(
                        "Tender %s requires an ACTIVE bid bond before a Won outcome "
                        "can be recorded (PPA 2006 / PPR 2008 tender security)" % rec.name
                    )
            rec.write(
                {
                    "state": "won" if won else "lost",
                    "outcome_note": note or rec.outcome_note,
                }
            )

    def action_cancel(self):
        for rec in self:
            if rec.state in ("won", "lost"):
                raise UserError("Tender %s is already decided (%s)" % (rec.name, rec.state))
            rec.state = "cancelled"


class FixTenderBond(models.Model):
    _name = "fix.tender.bond"
    _description = "Tender Bond"
    _order = "expires_on, id"

    tender_id = fields.Many2one("fix.tender", required=True, ondelete="cascade", index=True)
    bond_type = fields.Selection(
        [
            ("bid", "Bid bond"),
            ("performance", "Performance bond"),
            ("advance", "Advance payment guarantee"),
        ],
        required=True,
        default="bid",
    )
    amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    bank = fields.Char()
    expires_on = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("released", "Released"),
            ("claimed", "Claimed"),
        ],
        required=True,
        default="draft",
    )
    # Bank Guarantee Lifecycle & 30-Day Expiry Alert (FLAW-36.2)
    is_expiring_soon = fields.Boolean(
        string="Expiring Soon (30d)",
        compute="_compute_expiry_alert",
        store=True,
        help="Alert flag when active bank bond is within 30 days of statutory expiry",
    )

    @api.depends("expires_on", "state")
    def _compute_expiry_alert(self):
        today = fields.Date.today()
        for rec in self:
            if rec.state == "active" and rec.expires_on:
                rec.is_expiring_soon = (rec.expires_on - today).days <= 30
            else:
                rec.is_expiring_soon = False

    def action_activate(self):
        for rec in self:
            rec.state = "active"

    def action_release(self):
        for rec in self:
            rec.state = "released"

    def action_claim(self):
        for rec in self:
            rec.state = "claimed"
