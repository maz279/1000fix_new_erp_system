# fix_settlement_m53 — A08 M53 settlement depth (2026-10-26):
#
#   * fix.commission.scheme       — seller / partner commission rate tables
#                                   (effective-dated; TDS rate and base)
#   * fix.referral (inherited)    — partner / referral commissions accrued
#                                   into the commission ledger and paid in
#                                   payout runs
#   * fix.settlement.adjustment   — escrow holds (open marketplace disputes)
#                                   and clawbacks against future payouts
#   * fix.settlement.recovery     — what each payout run recovered
#   * fix.warranty.provision(.policy) — IAS 37 workmanship-warranty
#                                   provision per period, posted to the GL
#
# Technician incentives are NOT here: they moved to Payroll (A09).
import re
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_settlement_ext import _configured_account, _configured_journal

PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
OPEN_DISPUTE_STATES = ("raised", "investigating", "arbitration", "escalated")

PARTNER_TYPES = [
    ("referral", "Referral Partner"),
    ("reseller", "Reseller"),
    ("franchise", "Franchise"),
    ("alliance", "Strategic Alliance"),
]
SELLER_TIERS = [
    ("unrated", "Unrated (No Measured Performance Yet)"),
    ("platinum", "Platinum Seller (Top 5%)"),
    ("gold", "Gold Seller (Standard Qualified)"),
    ("silver", "Silver Seller (Probationary)"),
    ("at_risk", "At-Risk (Dispute Hold)"),
]


def _is_manager(env) -> bool:
    return env.user.has_group("account.group_account_manager") or env.user.has_group(
        "base.group_system"
    )


def _post_settlement_move(env, company, entry_date, ref, lines):
    """Post a balanced move [(account, name, debit, credit, partner)] through
    M19's engine with the AR posting dimensions. Refuses on missing config."""
    journal = _configured_journal(env, company)
    dims = env["fix.ar.invoice"]._ar_posting_dims()
    move, _ = post_with_dimensions(
        env,
        {
            "journal_id": journal.id,
            "company_id": company.id,
            "date": entry_date,
            "ref": ref,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": acc.id,
                        "name": name,
                        "debit": debit,
                        "credit": credit,
                        "partner_id": partner or False,
                    },
                )
                for acc, name, debit, credit, partner in lines
            ],
        },
        dict.fromkeys(range(len(lines)), dims),
        source="settlement",
    )
    return move


# ---------------------------------------------------------------------------
# Commission schemes (rate tables)
# ---------------------------------------------------------------------------
class FixCommissionScheme(models.Model):
    """An effective-dated commission rate table line for marketplace sellers
    or channel partners. The TDS rate is statutory master data: the seeded
    value carries a "verify with the tax adviser" note and is edited here,
    never in code."""

    _name = "fix.commission.scheme"
    _description = "Commission Scheme"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheme_type, date_from desc, id desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)
    scheme_type = fields.Selection(
        [("seller", "Marketplace Seller"), ("partner", "Partner / Referral")],
        string="Payee Type",
        required=True,
        default="partner",
        tracking=True,
    )
    partner_type = fields.Selection(
        PARTNER_TYPES, string="Partner Type", help="Empty = every partner type"
    )
    seller_tier = fields.Selection(SELLER_TIERS, string="Seller Tier", help="Empty = every tier")
    commission_rate = fields.Float(
        string="Commission Rate",
        digits=(5, 4),
        tracking=True,
        help="0-1. Zero = the rate agreed on the partner / marketplace order applies",
    )
    tds_rate = fields.Float(string="TDS Rate", digits=(5, 4), tracking=True, help="0-1")
    tds_base = fields.Selection(
        [("commission", "On the Commission"), ("gross", "On the Gross Amount")],
        string="TDS Base",
        required=True,
        default="commission",
    )
    tds_reference = fields.Char(
        string="Statutory Reference", help="Act / section / SRO the TDS rate comes from"
    )
    date_from = fields.Date(string="Effective From", required=True, tracking=True)
    date_to = fields.Date(string="Effective To", tracking=True)
    note = fields.Text(string="Notes")

    @api.constrains(
        "commission_rate",
        "tds_rate",
        "date_from",
        "date_to",
        "scheme_type",
        "partner_type",
        "seller_tier",
        "company_id",
        "active",
    )
    def _check_scheme(self):
        for scheme in self:
            if not (0 <= scheme.commission_rate <= 1 and 0 <= scheme.tds_rate <= 1):
                raise ValidationError("Commission and TDS rates are fractions between 0 and 1")
            if scheme.date_to and scheme.date_to < scheme.date_from:
                raise ValidationError("A scheme cannot end before it starts")
            if not scheme.active:
                continue
            for other in self.search(
                [
                    ("id", "!=", scheme.id),
                    ("company_id", "=", scheme.company_id.id),
                    ("scheme_type", "=", scheme.scheme_type),
                    ("partner_type", "=", scheme.partner_type),
                    ("seller_tier", "=", scheme.seller_tier),
                ]
            ):
                end_a = scheme.date_to or date.max
                end_b = other.date_to or date.max
                if scheme.date_from <= end_b and other.date_from <= end_a:
                    raise ValidationError(
                        "Scheme %s overlaps %s for the same payee type — end the old scheme "
                        "before the new one starts" % (scheme.name, other.name)
                    )

    @api.model
    def _find(self, scheme_type, on_date, company, partner_type=False, seller_tier=False):
        """The scheme in force on a date: the specific line (partner type /
        tier) wins over the generic one."""
        base = [
            ("company_id", "=", company.id),
            ("scheme_type", "=", scheme_type),
            ("date_from", "<=", on_date),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", on_date),
        ]
        key = "partner_type" if scheme_type == "partner" else "seller_tier"
        value = partner_type if scheme_type == "partner" else seller_tier
        if value:
            specific = self.search([*base, (key, "=", value)], limit=1)
            if specific:
                return specific
        return self.search([*base, (key, "=", False)], limit=1)

    def tds_on(self, commission, gross) -> float:
        self.ensure_one()
        base = commission if self.tds_base == "commission" else gross
        return round((base or 0.0) * self.tds_rate, 2)


# ---------------------------------------------------------------------------
# Partner / referral payouts
# ---------------------------------------------------------------------------
class FixReferral(models.Model):
    """Finance side of a commissioned referral: the commission is accrued
    into the M53 commission ledger (Dr expense / Cr partner payable) and
    paid in the next payout run."""

    _inherit = "fix.referral"

    commission_ledger_id = fields.Many2one(
        "fix.commission.ledger", string="Commission Ledger Entry", readonly=True, copy=False
    )
    payout_state = fields.Selection(
        related="commission_ledger_id.state", string="Payout State", readonly=True
    )

    def action_accrue_commission(self):
        Scheme = self.env["fix.commission.scheme"]
        Ledger = self.env["fix.commission.ledger"]
        today = fields.Date.context_today(self)
        for ref in self:
            if ref.state != "commissioned":
                raise UserError("Referral %s has not earned its commission yet" % ref.name)
            if ref.commission_ledger_id:
                raise UserError("Referral %s is already in the commission ledger" % ref.name)
            partner = ref.partner_id
            rate = partner.commission_rate
            if not 0 < rate <= 1:
                raise UserError(
                    "Partner %s has no valid agreed commission rate (%s)" % (partner.name, rate)
                )
            scheme = Scheme._find(
                "partner", today, ref.company_id, partner_type=partner.partner_type
            )
            if not scheme:
                raise UserError(
                    "No partner commission scheme is in force on %s for %s partners — "
                    "configure M53 Commission Schemes (TDS rate) first"
                    % (today, partner.partner_type)
                )
            if scheme.commission_rate:
                rate = scheme.commission_rate
            ledger = Ledger.create(
                {
                    "company_id": ref.company_id.id,
                    "operating_unit_id": ref.operating_unit_id.id,
                    "source_type": "partner_referral",
                    "seller_partner_id": partner.partner_id.id,
                    "source_ref": ref.name,
                    "referral_id": ref.id,
                    "scheme_id": scheme.id,
                    "gross_amount": ref.base_amount,
                    "commission_rate": rate,
                    "rail": "BEFTN",
                }
            )
            ref.commission_ledger_id = ledger
            ledger.action_post_to_gl()


# ---------------------------------------------------------------------------
# Escrow & clawbacks
# ---------------------------------------------------------------------------
class FixSettlementAdjustment(models.Model):
    """Escrow: commissions of a seller frozen while a marketplace dispute is
    open (never collected into a payout). Clawback: an amount owed BACK by a
    seller/partner, recovered from their future payouts."""

    _name = "fix.settlement.adjustment"
    _description = "Settlement Escrow / Clawback"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Reference", default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    adjustment_type = fields.Selection(
        [
            ("escrow", "Escrow Hold (open dispute)"),
            ("clawback", "Clawback (recover from future payouts)"),
        ],
        string="Type",
        required=True,
        default="escrow",
        tracking=True,
    )
    seller_partner_id = fields.Many2one(
        "res.partner", string="Seller / Partner", required=True, index=True, tracking=True
    )
    dispute_id = fields.Many2one(
        "fix.marketplace.dispute", string="Marketplace Dispute", index=True, tracking=True
    )
    commission_ids = fields.Many2many(
        "fix.commission.ledger",
        "fix_settlement_adjustment_commission_rel",
        "adjustment_id",
        "commission_id",
        string="Commissions Held",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", tracking=True)
    recovery_ids = fields.One2many("fix.settlement.recovery", "adjustment_id", string="Recoveries")
    recovered_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_recovered", store=True
    )
    remaining_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_recovered", store=True
    )
    reason = fields.Text(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Held / Open"),
            ("released", "Released to Payee"),
            ("forfeited", "Forfeited (refunded)"),
            ("recovered", "Recovered"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_at = fields.Datetime(string="Decided On", readonly=True, copy=False)
    move_id = fields.Many2one("account.move", string="GL Move", readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.settlement.adjustment") or "ADJ/New"
                )
        return super().create(vals_list)

    @api.depends("amount", "recovery_ids.amount")
    def _compute_recovered(self):
        for rec in self:
            rec.recovered_amount = sum(rec.recovery_ids.mapped("amount"))
            rec.remaining_amount = max(rec.amount - rec.recovered_amount, 0.0)

    @api.onchange("dispute_id")
    def _onchange_dispute(self):
        if self.dispute_id and self.dispute_id.seller_id.partner_id:
            self.seller_partner_id = self.dispute_id.seller_id.partner_id

    def _stamp(self, state):
        self.write(
            {"state": state, "decided_by_id": self.env.user.id, "decided_at": fields.Datetime.now()}
        )

    def action_activate(self):
        """Escrow: freeze the listed (unpaid) commissions. Clawback: open the
        claim — a finance manager other than the requester approves it, as it
        reduces what a payee is paid."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft adjustment can be activated")
            if rec.adjustment_type == "escrow":
                rows = rec.commission_ids
                if not rows:
                    raise UserError("List the commissions to hold in escrow")
                if rows.filtered(lambda c, r=rec: c.seller_partner_id != r.seller_partner_id):
                    raise UserError(
                        "Every held commission must belong to %s" % rec.seller_partner_id.name
                    )
                if rows.filtered(lambda c: c.state not in ("earned", "accrued")):
                    raise UserError("Only unpaid (earned / accrued) commissions can be held")
                in_flight = self.env["fix.payout.run"].search(
                    [("commission_ids", "in", rows.ids), ("state", "!=", "draft")]
                )
                if in_flight:
                    raise UserError(
                        "Commissions are already in approved payout run(s) %s"
                        % ", ".join(in_flight.mapped("name"))
                    )
                rows.write({"escrow_hold": True})
                rec.amount = sum(rows.mapped("net_payable"))
                rec._stamp("active")
            else:
                if rec.amount <= 0:
                    raise UserError("A clawback needs a positive amount")
                if not _is_manager(self.env):
                    raise AccessError("Only a finance manager can approve a clawback")
                if rec.requested_by_id == self.env.user:
                    raise AccessError(
                        "Segregation of duties: the requester cannot approve clawback %s" % rec.name
                    )
                rec._stamp("active")
            payload = {"ref": rec.name, "payee": rec.seller_partner_id.name, "amount": rec.amount}
            # one literal event type per branch, so the event contracts derive
            if rec.adjustment_type == "escrow":
                publish(
                    self.env,
                    "settlement.escrow_opened",
                    "fix.settlement.adjustment",
                    rec.id,
                    payload,
                )
            else:
                publish(
                    self.env,
                    "settlement.clawback_opened",
                    "fix.settlement.adjustment",
                    rec.id,
                    payload,
                )

    def action_release(self):
        """Release an escrow back into payouts once its dispute is resolved
        (a second person decides: segregation of duties)."""
        for rec in self:
            if rec.adjustment_type != "escrow" or rec.state != "active":
                raise UserError("Only an active escrow can be released")
            if rec.dispute_id and rec.dispute_id.state in OPEN_DISPUTE_STATES:
                raise UserError(
                    "Dispute %s is still open — the escrow stays until it is resolved"
                    % rec.dispute_id.name
                )
            if rec.requested_by_id == self.env.user:
                raise AccessError(
                    "Segregation of duties: the requester cannot release escrow %s" % rec.name
                )
            rec.commission_ids.write({"escrow_hold": False})
            rec._stamp("released")

    def action_forfeit(self):
        """The dispute was ruled for the customer: the held commissions are
        never paid. The seller liability they carried is moved to the
        customer-refund clearing account (Dr seller payable / Cr refund
        clearing). Finance manager, not the requester."""
        for rec in self:
            if rec.adjustment_type != "escrow" or rec.state != "active":
                raise UserError("Only an active escrow can be forfeited")
            if not _is_manager(self.env):
                raise AccessError("Only a finance manager can forfeit an escrow")
            if rec.requested_by_id == self.env.user:
                raise AccessError(
                    "Segregation of duties: the requester cannot forfeit escrow %s" % rec.name
                )
            move = False
            posted = rec.commission_ids.filtered(lambda c: c.state == "accrued")
            liability = sum(c.net_payable + (c.tds_amount or 0.0) for c in posted)
            if liability > 0.005:
                company = rec.company_id
                role = posted[:1]._payable_role()
                move = _post_settlement_move(
                    self.env,
                    company,
                    fields.Date.context_today(rec),
                    "ESCROW-FORFEIT-%s" % rec.name,
                    [
                        (
                            _configured_account(self.env, company, role),
                            "Forfeited payee liability %s" % rec.name,
                            liability,
                            0.0,
                            rec.seller_partner_id.id,
                        ),
                        (
                            _configured_account(self.env, company, "clawback_recovery"),
                            "Customer refund clearing %s" % rec.name,
                            0.0,
                            liability,
                            False,
                        ),
                    ],
                )
            rec.commission_ids.write({"state": "forfeited"})
            rec.move_id = move.id if move else False
            rec._stamp("forfeited")

    def action_cancel(self):
        for rec in self:
            if rec.state == "draft":
                rec.state = "cancelled"
                continue
            if rec.adjustment_type == "clawback" and rec.state == "active" and not rec.recovery_ids:
                if not _is_manager(self.env):
                    raise AccessError("Only a finance manager can cancel an open clawback")
                rec._stamp("cancelled")
                continue
            raise UserError("%s cannot be cancelled in state %s" % (rec.name, rec.state))


class FixSettlementRecovery(models.Model):
    """The part of a clawback a payout run deducted."""

    _name = "fix.settlement.recovery"
    _description = "Clawback Recovery"
    _order = "id desc"

    adjustment_id = fields.Many2one(
        "fix.settlement.adjustment", required=True, ondelete="restrict", index=True
    )
    payout_run_id = fields.Many2one(
        "fix.payout.run", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="adjustment_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="adjustment_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)


# ---------------------------------------------------------------------------
# IAS 37 workmanship warranty provision
# ---------------------------------------------------------------------------
class FixWarrantyProvisionPolicy(models.Model):
    """The estimate behind the workmanship-warranty provision: the warranty
    period the company gives on repairs, the claim-history window and the
    average cost of a rework as a share of the original repair revenue.
    Effective-dated master data, set by finance — nothing is seeded."""

    _name = "fix.warranty.provision.policy"
    _description = "Warranty Provision Policy (IAS 37)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)
    warranty_days = fields.Integer(
        string="Workmanship Warranty (days)", required=True, tracking=True
    )
    lookback_months = fields.Integer(
        string="Claim History Window (months)", required=True, default=12, tracking=True
    )
    cost_ratio = fields.Float(
        string="Rework Cost Ratio",
        digits=(5, 4),
        required=True,
        tracking=True,
        help="Average cost of one rework as a fraction of the original repair revenue (0-1)",
    )
    date_from = fields.Date(string="Effective From", required=True)
    date_to = fields.Date(string="Effective To")
    note = fields.Text(string="Basis of Estimate")

    @api.constrains("warranty_days", "lookback_months", "cost_ratio", "date_from", "date_to")
    def _check_policy(self):
        for policy in self:
            if policy.warranty_days <= 0 or policy.lookback_months <= 0:
                raise ValidationError("Warranty days and the history window must be positive")
            if not 0 <= policy.cost_ratio <= 1:
                raise ValidationError("The rework cost ratio is a fraction between 0 and 1")
            if policy.date_to and policy.date_to < policy.date_from:
                raise ValidationError("A policy cannot end before it starts")

    @api.model
    def _find(self, company, on_date):
        return self.search(
            [
                ("company_id", "=", company.id),
                ("date_from", "<=", on_date),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", on_date),
            ],
            limit=1,
        )


class FixWarrantyProvision(models.Model):
    """The period-end workmanship-warranty provision (IAS 37, assurance-type
    warranty): required balance = repair revenue still inside the warranty
    window x historical rework rate x rework cost ratio. The movement against
    the last posted balance is booked (increase: Dr warranty expense / Cr
    provision; release on expiry: the reverse)."""

    _name = "fix.warranty.provision"
    _description = "Warranty Provision (IAS 37)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc, id desc"

    _period_unique = models.Constraint(
        "UNIQUE (company_id, period)", "One warranty provision per company per period"
    )

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    period = fields.Char(string="Period (YYYY-MM)", required=True, index=True)
    period_end = fields.Date(compute="_compute_period_end", store=True)
    policy_id = fields.Many2one("fix.warranty.provision.policy", string="Policy", readonly=True)
    revenue_in_warranty = fields.Monetary(
        string="Repair Revenue in Warranty", currency_field="currency_id", readonly=True
    )
    lookback_orders = fields.Integer(string="Invoiced Repairs (history)", readonly=True)
    lookback_reworks = fields.Integer(string="Reworks (history)", readonly=True)
    rework_rate = fields.Float(string="Rework Rate", digits=(5, 4), readonly=True)
    cost_ratio = fields.Float(string="Rework Cost Ratio", digits=(5, 4), readonly=True)
    required_balance = fields.Monetary(
        string="Required Provision", currency_field="currency_id", readonly=True
    )
    opening_balance = fields.Monetary(
        string="Last Posted Provision", currency_field="currency_id", readonly=True
    )
    movement = fields.Monetary(string="Movement", currency_field="currency_id", readonly=True)
    move_id = fields.Many2one("account.move", string="GL Move", readonly=True, copy=False)
    computed_by_id = fields.Many2one("res.users", string="Computed By", readonly=True)
    computed_at = fields.Datetime(string="Computed On", readonly=True)
    posted_by_id = fields.Many2one("res.users", string="Posted By", readonly=True)
    note = fields.Text(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("posted", "Posted")],
        default="draft",
        required=True,
        tracking=True,
    )

    @api.depends("period")
    def _compute_name(self):
        for rec in self:
            rec.name = "WP/%s" % (rec.period or "")

    @api.depends("period")
    def _compute_period_end(self):
        for rec in self:
            if rec.period and PERIOD_RE.match(rec.period):
                y, m = (int(x) for x in rec.period.split("-"))
                rec.period_end = date(y, m, 1) + relativedelta(months=1) - timedelta(days=1)
            else:
                rec.period_end = False

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if not PERIOD_RE.match(rec.period or ""):
                raise ValidationError("The period must be written YYYY-MM (e.g. 2026-10)")

    def action_compute(self):
        """Measure the provision from posted data: AR repair invoices and
        the rework orders flagged by M01 (BRU-SRM-06)."""
        Invoice = self.env["fix.ar.invoice"]
        Order = self.env["fix.service.order"]
        for rec in self:
            if rec.state == "posted":
                raise UserError("Provision %s is posted" % rec.name)
            end = rec.period_end
            policy = self.env["fix.warranty.provision.policy"]._find(rec.company_id, end)
            if not policy:
                raise UserError(
                    "No warranty provision policy is in force on %s — set the warranty "
                    "period and rework cost ratio first" % end
                )
            repair = [
                ("company_id", "=", rec.company_id.id),
                ("source_model", "=", "fix.service.order"),
                ("state", "in", ("issued", "paid", "credited")),
            ]
            in_warranty = Invoice.search(
                [
                    *repair,
                    ("invoice_date", ">", end - timedelta(days=policy.warranty_days)),
                    ("invoice_date", "<=", end),
                ]
            )
            window_start = end - relativedelta(months=policy.lookback_months)
            history = Invoice.search_count(
                [*repair, ("invoice_date", ">", window_start), ("invoice_date", "<=", end)]
            )
            reworks = Order.search_count(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("is_rework", "=", True),
                    ("create_date", ">", fields.Datetime.to_datetime(window_start)),
                    ("create_date", "<", fields.Datetime.to_datetime(end + timedelta(days=1))),
                ]
            )
            rate = min(reworks / history, 1.0) if history else 0.0
            revenue = sum(in_warranty.mapped("taxable_amount"))
            required = round(revenue * rate * policy.cost_ratio, 2)
            last = self.search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "posted"),
                    ("period", "<", rec.period),
                ],
                order="period desc",
                limit=1,
            )
            opening = last.required_balance if last else 0.0
            notes = []
            if not history:
                notes.append("No invoiced repairs in the history window: rework rate 0.")
            rec.write(
                {
                    "policy_id": policy.id,
                    "revenue_in_warranty": revenue,
                    "lookback_orders": history,
                    "lookback_reworks": reworks,
                    "rework_rate": rate,
                    "cost_ratio": policy.cost_ratio,
                    "required_balance": required,
                    "opening_balance": opening,
                    "movement": round(required - opening, 2),
                    "computed_by_id": self.env.user.id,
                    "computed_at": fields.Datetime.now(),
                    "note": " ".join(notes) or False,
                    "state": "computed",
                }
            )

    def action_post(self):
        """Book the movement (finance manager, not the person who computed)."""
        for rec in self:
            if rec.state != "computed":
                raise UserError("Compute provision %s before posting it" % rec.name)
            if not _is_manager(self.env):
                raise AccessError("Only a finance manager can post the warranty provision")
            if rec.computed_by_id == self.env.user:
                raise AccessError(
                    "Segregation of duties: %s computed %s and cannot post it"
                    % (self.env.user.name, rec.name)
                )
            later = self.search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "posted"),
                    ("period", ">", rec.period),
                ],
                limit=1,
            )
            if later:
                raise UserError(
                    "A later period (%s) is already posted — post periods in order" % later.period
                )
            move = False
            amount = abs(rec.movement)
            if amount > 0.005:
                company = rec.company_id
                expense = _configured_account(self.env, company, "warranty_expense")
                provision = _configured_account(self.env, company, "warranty_provision")
                if rec.movement > 0:
                    lines = [
                        (expense, "Warranty provision charge %s" % rec.period, amount, 0.0, False),
                        (provision, "Warranty provision %s" % rec.period, 0.0, amount, False),
                    ]
                else:
                    lines = [
                        (
                            provision,
                            "Warranty provision release %s" % rec.period,
                            amount,
                            0.0,
                            False,
                        ),
                        (expense, "Warranty provision release %s" % rec.period, 0.0, amount, False),
                    ]
                move = _post_settlement_move(
                    self.env, company, rec.period_end, "WARRANTY-PROV-%s" % rec.period, lines
                )
            rec.write(
                {
                    "state": "posted",
                    "move_id": move.id if move else False,
                    "posted_by_id": self.env.user.id,
                }
            )
