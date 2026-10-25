# fix_settlement_ext — M53 W7: commission ledger + payout runs (P10-M02 / R08-M02).
from __future__ import annotations

import base64
import uuid
from decimal import Decimal

from odoo import api, fields, models
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish
from libs.py.payout_rail import (
    INT007PayoutRail,
    PayoutBatchRequest,
    PayoutRecipient,
    PayoutStatus,
)

# Settlement GL accounts by role: (default code, label). The code is looked up
# in the company's chart; a database may override it with the system
# parameter ``cd_settlement_ext.account_code.<role>``.
# NOTE: 210100 is also the VAT Output Payable code cd_tax_engine_bd reconciles
# against; a chart that keeps TDS separate must override ``tds_payable``.
SETTLEMENT_ACCOUNTS = {
    "clearing": ("101000", "Customer Payment Clearing / Disbursement Bank"),
    "commission_revenue": ("400100", "Marketplace Commission Revenue"),
    "seller_payable": ("200200", "Marketplace Seller Payable"),
    "tds_payable": ("210100", "TDS Withheld Liability (ITA 2023 §52)"),
    # A08 M53 roles with NO default code: the chart has no semantically
    # certain account for them, so the system parameter must name one.
    "partner_commission_expense": (None, "Partner / Referral Commission Expense"),
    "partner_payable": (None, "Partner Commission Payable"),
    "clawback_recovery": (None, "Customer Refund Clearing (clawbacks / forfeited escrow)"),
    "warranty_expense": (None, "Workmanship Warranty Expense (IAS 37)"),
    "warranty_provision": (None, "Workmanship Warranty Provision (IAS 37)"),
}


def _configured_account(env, company, role):
    """The company's configured GL account for a settlement role.

    Never guessed, never created: the former helper fell back to ANY account
    of the same type (posting commission revenue to whichever income account
    came first) or created accounts on the fly. A missing account refuses the
    posting with the code that must be configured.

    Odoo 19: account.account is shared across companies (company_ids) and its
    code is company-dependent."""
    default_code, label = SETTLEMENT_ACCOUNTS[role]
    code = (
        env["ir.config_parameter"].sudo().get_param(f"cd_settlement_ext.account_code.{role}")
        or default_code
    )
    if not code:
        raise UserError(
            "Settlement posting refused: no GL account is configured for %s in company %s. "
            "Set system parameter cd_settlement_ext.account_code.%s to the account code to use."
            % (label, company.name, role)
        )
    accounts = env["account.account"].with_company(company)
    acc = accounts.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    if not acc:
        raise UserError(
            "Settlement posting refused: no GL account %s (%s) in company %s. Configure it in "
            "the chart of accounts, or set system parameter "
            "cd_settlement_ext.account_code.%s to the account code to use."
            % (code, label, company.name, role)
        )
    return acc


def _configured_journal(env, company):
    """The company's general journal for settlement postings — refused, not
    created, when the company has none."""
    journal = env["account.journal"].search(
        [("type", "=", "general"), ("company_id", "=", company.id)], limit=1
    )
    if not journal:
        raise UserError(
            "Settlement posting refused: company %s has no general (miscellaneous) journal."
            % company.name
        )
    return journal


def _bank_details(partner) -> tuple[str, str]:
    """(account number, routing number) of the partner's first bank account,
    exactly as recorded — empty strings when absent, never a default."""
    bank = partner.bank_ids[:1]
    return (bank.acc_number or "").strip(), (bank.bank_id.bic or "").strip()


def _is_routing(routing: str) -> bool:
    """A Bangladesh BEFTN routing number: exactly 9 ASCII digits."""
    return len(routing) == 9 and routing.isascii() and routing.isdigit()


class FixCommissionLedger(models.Model):
    """M53 W7: commission ledger consuming commission.earned events.
    The M12<->M53 break: M53 CONSUMES events; M12 never calls M53.
    Enforces FF-91: Marketplace gross is NEVER posted to revenue!"""

    _name = "fix.commission.ledger"
    _description = "Commission Ledger Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    seller_partner_id = fields.Many2one(
        "res.partner", string="Seller (Party)", required=True, index=True
    )
    source_ref = fields.Char(string="Source Reference")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    gross_amount = fields.Monetary(
        string="Gross Marketplace GMV", currency_field="currency_id", required=True
    )
    commission_rate = fields.Float(string="Commission Rate", default=0.10)
    commission_amount = fields.Monetary(
        string="Commission Earned (Revenue)",
        currency_field="currency_id",
        compute="_compute_commission",
        store=True,
    )
    tds_amount = fields.Monetary(string="TDS Withheld (ITA 2023 §52)", currency_field="currency_id")
    net_payable = fields.Monetary(
        string="Net Payable to Seller",
        currency_field="currency_id",
        compute="_compute_net",
        store=True,
    )
    state = fields.Selection(
        [
            ("earned", "Earned"),
            ("accrued", "Accrued / Posted to GL"),
            ("paid", "Disbursed / Paid"),
            ("forfeited", "Forfeited (dispute ruling)"),
        ],
        default="earned",
        required=True,
        tracking=True,
    )
    # A08 M53: one ledger for marketplace sellers AND channel partners —
    # both are paid through the same payout runs.
    source_type = fields.Selection(
        [("marketplace", "Marketplace Seller"), ("partner_referral", "Partner / Referral")],
        string="Payee Type",
        default="marketplace",
        required=True,
        index=True,
        tracking=True,
    )
    referral_id = fields.Many2one(
        "fix.referral", string="Referral", index=True, ondelete="restrict", copy=False
    )
    scheme_id = fields.Many2one("fix.commission.scheme", string="Commission Scheme")
    escrow_hold = fields.Boolean(
        string="Held in Escrow",
        readonly=True,
        copy=False,
        tracking=True,
        help="Held by an active escrow (open marketplace dispute): never collected into a payout",
    )

    # Four reconciliation keys required by LP-02 (IN-007 §5.1, §10.2)
    payment_id = fields.Char(string="Payment ID", copy=False, index=True)
    rail = fields.Char(string="Payment Rail", default="bKash")
    rail_transaction_id = fields.Char(string="Rail Transaction ID", copy=False, index=True)
    merchant_invoice_number = fields.Char(string="Merchant Invoice Ref", copy=False, index=True)

    gl_move_id = fields.Many2one(
        "account.move", string="General Ledger Move", readonly=True, copy=False
    )

    @api.depends("gross_amount", "commission_rate")
    def _compute_commission(self):
        for rec in self:
            rec.commission_amount = rec.gross_amount * rec.commission_rate

    @api.depends("gross_amount", "commission_amount", "tds_amount", "source_type")
    def _compute_net(self):
        for rec in self:
            if rec.source_type == "partner_referral":
                # A partner is owed its commission (an expense of 1000 FiX),
                # less the TDS withheld on it
                rec.net_payable = rec.commission_amount - (rec.tds_amount or 0.0)
            else:
                # Seller entitlement = Gross GMV - Commission Earned - TDS Withheld
                rec.net_payable = rec.gross_amount - rec.commission_amount - (rec.tds_amount or 0.0)

    def _payable_role(self) -> str:
        self.ensure_one()
        return "partner_payable" if self.source_type == "partner_referral" else "seller_payable"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.commission.ledger")
                    or f"COM/{fields.Date.today().year}/New"
                )
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list, strict=True):
            # the scheme's effective-dated TDS rate, unless a figure was given
            if rec.scheme_id and "tds_amount" not in vals:
                rec.tds_amount = rec.scheme_id.tds_on(rec.commission_amount, rec.gross_amount)
        return records

    def write(self, vals):
        for rec in self:
            if rec.state in ("accrued", "paid") and not self.env.su:
                # Reversible only by contra-posting per LP-07
                restricted_fields = {
                    "gross_amount",
                    "commission_rate",
                    "commission_amount",
                    "seller_partner_id",
                }
                if any(f in vals for f in restricted_fields):
                    raise UserError(
                        "LP-07 Violation: Accrued commission entries cannot be modified. Use contra-posting."
                    )
        return super().write(vals)

    def _post_partner_accrual(self):
        """Partner / referral commission is 1000 FiX's EXPENSE (it is the
        principal for the referred repair): Dr commission expense / Cr
        partner payable, the payable discharged by the payout run."""
        self.ensure_one()
        company = self.company_id
        journal = _configured_journal(self.env, company)
        expense = _configured_account(self.env, company, "partner_commission_expense")
        payable = _configured_account(self.env, company, "partner_payable")
        dims = {
            "branch_id": self.branch_id.id,
            "operating_unit_id": self.operating_unit_id.id,
            "cost_centre": "CC-PAY",
        }
        move, _ = post_with_dimensions(
            self.env,
            {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": fields.Date.context_today(self),
                "ref": f"COM-ACCRUAL-{self.name}",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": f"Partner commission: {self.name}",
                            "account_id": expense.id,
                            "debit": self.commission_amount,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": f"Partner commission payable: {self.name}",
                            "account_id": payable.id,
                            "partner_id": self.seller_partner_id.id,
                            "debit": 0.0,
                            "credit": self.commission_amount,
                        },
                    ),
                ],
            },
            {0: dims, 1: dims},
            source="settlement",
        )
        self.write({"state": "accrued", "gl_move_id": move.id})
        publish(
            self.env,
            "commission.accrued",
            "fix.commission.ledger",
            self.id,
            {
                "commission_ref": self.name,
                "seller": self.seller_partner_id.name,
                "payee_type": "partner_referral",
                "commission_amount": float(self.commission_amount),
                "move_id": move.id,
            },
        )

    def action_post_to_gl(self):
        """Post commission accrual to GL through M19 (cd_gl_ext).
        Strictly enforces FF-91 (MS-01):
        - Marketplace gross is NEVER booked to revenue!
        - Commission Earned is credited to Revenue (400100).
        - Seller Share is credited to Liability (200200).
        - Customer Clearing / Bank is debited (101000)."""
        for rec in self:
            if rec.state != "earned":
                continue
            if rec.source_type == "partner_referral":
                rec._post_partner_accrual()
                continue

            company = rec.company_id
            journal = _configured_journal(self.env, company)
            bank_clearing = _configured_account(self.env, company, "clearing")
            commission_rev = _configured_account(self.env, company, "commission_revenue")
            seller_payable = _configured_account(self.env, company, "seller_payable")

            gross = rec.gross_amount
            comm = rec.commission_amount
            seller_share = gross - comm

            move_vals = {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": fields.Date.context_today(rec),
                "ref": f"COM-ACCRUAL-{rec.name}",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": f"Customer Receipt Clearing: {rec.name}",
                            "account_id": bank_clearing.id,
                            "debit": gross,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": f"Commission Revenue (FF-91): {rec.name}",
                            "account_id": commission_rev.id,
                            "debit": 0.0,
                            "credit": comm,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": f"Seller Entitlement Liability: {rec.name}",
                            "account_id": seller_payable.id,
                            "partner_id": rec.seller_partner_id.id,
                            "debit": 0.0,
                            "credit": seller_share,
                        },
                    ),
                ],
            }

            dim_by_line = {
                0: {
                    "branch_id": rec.branch_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "cost_centre": "CC-MKT",
                },
                1: {
                    "branch_id": rec.branch_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "cost_centre": "CC-REV",
                },
                2: {
                    "branch_id": rec.branch_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "cost_centre": "CC-PAY",
                },
            }

            move, _ = post_with_dimensions(self.env, move_vals, dim_by_line, source="settlement")
            rec.write(
                {
                    "state": "accrued",
                    "gl_move_id": move.id,
                }
            )

            publish(
                self.env,
                "commission.accrued",
                "fix.commission.ledger",
                rec.id,
                {
                    "commission_ref": rec.name,
                    "seller": rec.seller_partner_id.name,
                    "gross": float(rec.gross_amount),
                    "commission_amount": float(rec.commission_amount),
                    "seller_share": float(seller_share),
                    "move_id": move.id,
                    "payment_id": rec.payment_id or "",
                    "rail": rec.rail or "",
                },
            )


class FixPayoutRun(models.Model):
    """Payout run: money to 500-2,000 sellers.
    Enforces two-person Segregation of Duties (SoD) gate, INT-007 multi-rail dispatch,
    7-day idempotency, first-class unknown state (FF-85), and BEFTN fallback."""

    _name = "fix.payout.run"
    _description = "Payout Run / পরিশোধ চক্র"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, default="New")
    period = fields.Char(string="Settlement Period", required=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_payable = fields.Monetary(
        compute="_compute_total",
        string="Total Net Payable",
        currency_field="currency_id",
        store=True,
    )
    total_tds = fields.Monetary(
        compute="_compute_total",
        string="Total Statutory TDS Withheld",
        currency_field="currency_id",
        store=True,
    )
    total_gross = fields.Monetary(
        compute="_compute_total", string="Total Gross GMV", currency_field="currency_id", store=True
    )
    seller_count = fields.Integer(compute="_compute_total", string="Seller Count", store=True)

    state = fields.Selection(
        [
            ("draft", "Draft / খসড়া"),
            ("approved", "Approved (SoD Verified) / অনুমোদিত"),
            ("executing", "Executing / চলমান"),
            ("file_generated", "BEFTN File Generated (Unconfirmed) / ফাইল তৈরি"),
            ("executed", "Executed / সমাপ্ত"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # Segregation of Duties fields
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_date = fields.Datetime(string="Approved Date", readonly=True)
    sod_verified = fields.Boolean(string="SoD Verified", readonly=True, default=False)

    commission_ids = fields.Many2many("fix.commission.ledger", string="Commissions")
    clawback_ids = fields.Many2many(
        "fix.settlement.adjustment",
        "fix_payout_run_clawback_rel",
        "run_id",
        "adjustment_id",
        string="Clawbacks to Recover",
        domain=[("adjustment_type", "=", "clawback"), ("state", "=", "active")],
    )
    recovery_ids = fields.One2many(
        "fix.settlement.recovery", "payout_run_id", string="Clawbacks Recovered"
    )
    total_clawback = fields.Monetary(
        compute="_compute_total",
        string="Clawback Deducted",
        currency_field="currency_id",
        store=True,
    )

    # INT-007 Payout Rail Integration Fields
    idempotency_key = fields.Char(string="Idempotency Key (7-Day TTL)", copy=False, readonly=True)
    rail_type = fields.Selection(
        [
            ("api", "Direct API (Mobile Money / Bank Gateway)"),
            ("beftn", "BEFTN Standard Batch File (128-byte)"),
        ],
        string="Disbursement Rail",
        default="api",
        required=True,
    )
    rail_status = fields.Selection(
        [
            ("draft", "Not Submitted"),
            ("executing", "Executing"),
            ("confirmed", "Confirmed"),
            ("unknown", "Unknown (Timed Out)"),
            ("pending_bank_confirmation", "Pending Bank Confirmation"),
            ("file_generated", "BEFTN File Generated (Not Confirmed)"),
            ("failed", "Failed"),
        ],
        string="Rail Confirmation Status",
        default="draft",
        tracking=True,
    )
    rail_batch_id = fields.Char(string="Rail Batch Reference", readonly=True, copy=False)
    bank_confirmation_ref = fields.Char(
        string="Bank Settlement Reference",
        copy=False,
        tracking=True,
        help="The reference the BANK issued for this disbursement (BEFTN settlement / "
        "bank statement reference), entered by a finance manager. Required to "
        "confirm a payout that has no confirmed rail response.",
    )
    bank_confirmed_by_id = fields.Many2one(
        "res.users", string="Bank Confirmation Recorded By", readonly=True, copy=False
    )
    bank_confirmed_at = fields.Datetime(string="Bank Confirmation Recorded At", readonly=True)
    beftn_file = fields.Binary(string="BEFTN Batch File Content", readonly=True)
    beftn_filename = fields.Char(string="BEFTN Filename", readonly=True)

    gl_move_id = fields.Many2one(
        "account.move", string="GL Disbursement Entry", readonly=True, copy=False
    )
    statement_ids = fields.One2many(
        "fix.seller.statement", "payout_run_id", string="Seller Statements"
    )
    reconciliation_ids = fields.One2many(
        "fix.payout.reconciliation", "payout_run_id", string="Reconciliation Runs"
    )

    @api.depends(
        "commission_ids.net_payable",
        "commission_ids.tds_amount",
        "commission_ids.gross_amount",
        "clawback_ids.remaining_amount",
        "recovery_ids.amount",
        "state",
    )
    def _compute_total(self):
        for rec in self:
            rec.total_clawback = sum(
                amount for pairs in rec._clawback_deductions().values() for _a, amount in pairs
            )
            rec.total_payable = sum(rec.commission_ids.mapped("net_payable")) - rec.total_clawback
            rec.total_tds = sum(rec.commission_ids.mapped("tds_amount"))
            rec.total_gross = sum(rec.commission_ids.mapped("gross_amount"))
            rec.seller_count = len(rec.commission_ids.mapped("seller_partner_id"))

    def _clawback_deductions(self) -> dict:
        """{payee: [(clawback, amount)]} deducted in this run. An executed
        run reports what it recovered; an open run projects each payee's
        open clawbacks against that payee's net in the run (never more)."""
        self.ensure_one()
        out: dict = {}
        if self.state == "executed":
            for line in self.recovery_ids:
                out.setdefault(line.adjustment_id.seller_partner_id, []).append(
                    (line.adjustment_id, line.amount)
                )
            return out
        for payee in self.commission_ids.mapped("seller_partner_id"):
            available = sum(
                self.commission_ids.filtered(lambda c, p=payee: c.seller_partner_id == p).mapped(
                    "net_payable"
                )
            )
            for claw in self.clawback_ids.filtered(
                lambda a, p=payee: a.seller_partner_id == p and a.state == "active"
            ).sorted("id"):
                take = round(min(available, claw.remaining_amount), 2)
                if take <= 0:
                    continue
                out.setdefault(payee, []).append((claw, take))
                available -= take
        return out

    def action_collect_accrued(self):
        """Fill a draft run with every accrued commission (sellers AND
        partners) not held in escrow and not already in another open run,
        plus the payees' open clawbacks."""
        Ledger = self.env["fix.commission.ledger"]
        for run in self:
            if run.state != "draft":
                raise UserError("Commissions are collected into a draft payout run only")
            busy = self.search(
                [
                    ("id", "!=", run.id),
                    ("state", "!=", "executed"),
                    ("company_id", "=", run.company_id.id),
                ]
            ).mapped("commission_ids")
            rows = Ledger.search(
                [
                    ("company_id", "=", run.company_id.id),
                    ("state", "=", "accrued"),
                    ("escrow_hold", "=", False),
                    ("id", "not in", busy.ids),
                ]
            )
            if not rows and not run.commission_ids:
                raise UserError(
                    "No accrued commissions are free to pay — accrue commissions to the GL first"
                )
            run.commission_ids = [(6, 0, (run.commission_ids | rows).ids)]
            claws = self.env["fix.settlement.adjustment"].search(
                [
                    ("company_id", "=", run.company_id.id),
                    ("adjustment_type", "=", "clawback"),
                    ("state", "=", "active"),
                    ("seller_partner_id", "in", run.commission_ids.mapped("seller_partner_id").ids),
                ]
            )
            run.clawback_ids = [(6, 0, claws.ids)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payout.run")
                    or f"PAY/{fields.Date.today().year}/New"
                )
        return super().create(vals_list)

    def action_approve(self):
        """Two-person Segregation of Duties (SoD) gate.
        Rule 1: Preparer cannot approve their own payout run.
        Rule 2: Approver must possess financial managerial authority."""
        for rec in self:
            if not rec.commission_ids:
                raise UserError("No commissions attached to this payout run.")
            held = rec.commission_ids.filtered("escrow_hold")
            if held:
                raise UserError(
                    "Payout run %s carries commissions held in escrow (%s) — remove them or "
                    "release the escrow first." % (rec.name, ", ".join(held.mapped("name")))
                )
            if rec.prepared_by_id and self.env.user.id == rec.prepared_by_id.id:
                raise UserError("SoD Violation: Preparer cannot approve their own payout run.")
            if not (
                self.env.user.has_group("account.group_account_manager")
                or self.env.user.has_group("base.group_system")
            ):
                raise AccessError("SoD Violation: Only Finance Managers can approve payout runs.")

            rec.write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_date": fields.Datetime.now(),
                    "sod_verified": True,
                }
            )
            publish(
                self.env,
                "payout.approved",
                "fix.payout.run",
                rec.id,
                {
                    "payout_run": rec.name,
                    "total_payable": float(rec.total_payable),
                    "total_tds": float(rec.total_tds),
                    "seller_count": rec.seller_count,
                    "approved_by": self.env.user.name,
                },
            )

    def action_execute(self):
        """Execute payout run (alias for action_submit_payout)."""
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve before executing")
        return self.action_submit_payout()

    def _check_bank_details(self) -> None:
        """Refuse the payout unless EVERY party has real bank details: the
        paying company (originating account) and each seller (beneficiary).

        Nothing is ever defaulted — the former fallbacks paid a seller with
        no account into a placeholder account through the sponsor routing
        number, and the rail's BEFTN header carried a library-default
        originating routing. All gaps are listed in one named error."""
        self.ensure_one()
        problems = []
        parties = [("company", self.company_id.partner_id, self.company_id.name)] + [
            ("seller", seller, seller.name)
            for seller in self.commission_ids.mapped("seller_partner_id")
        ]
        for role, partner, name in parties:
            acc_num, routing = _bank_details(partner)
            if not acc_num:
                problems.append("%s %s: no bank account" % (role, name))
            elif not _is_routing(routing):
                problems.append(
                    "%s %s: routing %r is not a 9-digit BEFTN routing number"
                    % (role, name, routing)
                )
        if problems:
            raise UserError(
                "Payout %s refused — bank details missing or invalid for: %s"
                % (self.name, "; ".join(problems))
            )

    def _default_rail(self) -> INT007PayoutRail:
        """The INT-007 rail originating from the company's OWN bank account."""
        company = self.company_id
        return INT007PayoutRail(
            originating_routing=_bank_details(company.partner_id)[1],
            company_name=company.name,
            company_id=company.company_registry or company.vat or str(company.id),
        )

    def _prepare_payout_recipients(self) -> list[PayoutRecipient]:
        self.ensure_one()
        self._check_bank_details()
        # Aggregate net payable per seller
        seller_totals: dict[models.Model, dict] = {}
        for c in self.commission_ids:
            seller = c.seller_partner_id
            if seller not in seller_totals:
                seller_totals[seller] = {
                    "net_payable": Decimal("0.00"),
                    "gross": Decimal("0.00"),
                    "tds": Decimal("0.00"),
                    "comm": Decimal("0.00"),
                }
            seller_totals[seller]["net_payable"] += Decimal(str(c.net_payable))
            seller_totals[seller]["gross"] += Decimal(str(c.gross_amount))
            seller_totals[seller]["tds"] += Decimal(str(c.tds_amount or 0.0))
            seller_totals[seller]["comm"] += Decimal(str(c.commission_amount))

        deductions = self._clawback_deductions()
        recipients = []
        for seller, amounts in seller_totals.items():
            amounts["net_payable"] -= sum(
                (Decimal(str(amt)) for _c, amt in deductions.get(seller, [])), Decimal("0.00")
            )
            if amounts["net_payable"] <= 0:
                continue  # fully recovered by a clawback: nothing to disburse
            acc_num, routing = _bank_details(seller)  # validated: never invented
            recipients.append(
                PayoutRecipient(
                    seller_ref=f"SLR-{seller.id:04d}",
                    seller_name=seller.name,
                    account_number=acc_num,
                    routing_number=routing,
                    amount_bdt=amounts["net_payable"],
                    disbursement_ref=f"DISB-{self.name}-{seller.id}",
                )
            )
        return recipients

    def action_submit_payout(self, simulate_timeout=False, rail_instance=None):
        """Submit payout batch to INT-007 seller payout rail with 7-day idempotency."""
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    "Payout run must be SoD-approved before dispatching to payout rail."
                )

            if not rec.idempotency_key:
                rec.idempotency_key = f"IDEMP-{rec.name}-{uuid.uuid4().hex[:12]}"

            recipients = rec._prepare_payout_recipients()
            req = PayoutBatchRequest(
                batch_ref=rec.name,
                period=rec.period,
                recipients=tuple(recipients),
                idempotency_key=rec.idempotency_key,
                total_amount=Decimal(str(rec.total_payable)),
                recipient_count=len(recipients),
            )

            rail = rail_instance or rec._default_rail()
            result = rail.submit_payout_batch(
                req, rail_type="api", simulate_timeout=simulate_timeout
            )

            rec.write(
                {
                    "rail_batch_id": result.rail_batch_id,
                    "rail_status": result.status.value,
                }
            )

            if result.status == PayoutStatus.CONFIRMED:
                rec._finalize_payout_execution()
            elif result.status == PayoutStatus.UNKNOWN:
                rec.state = "executing"
                # IN-007 §3.4: Customer/seller sees 'We are confirming payment', not 'failed'

    def action_query_status(self, rail_instance=None):
        """Read-back query resolving UNKNOWN state (IN-007 §5.4, FF-85).

        Only a REAL bank response may resolve the run. A rail exposes that as
        ``query_bank_status(batch_ref, rail_batch_id)`` returning an object
        with ``status`` (PayoutStatus) and ``bank_reference``. The INT-007
        library rail has no such bank query — its ``read_back_status`` takes
        the outcome from the CALLER (this method used to pass CONFIRMED and so
        finalised every timed-out payout as paid). Without a bank response the
        run stays ``pending_bank_confirmation`` until a finance manager
        records the bank's reference (action_confirm_bank_settlement)."""
        for rec in self:
            if not rec.rail_batch_id:
                raise UserError("No rail batch reference recorded to query.")

            rail = rail_instance or rec._default_rail()
            query = getattr(rail, "query_bank_status", None)
            response = query(rec.name, rec.rail_batch_id) if query else None
            status = getattr(response, "status", None)
            bank_ref = (getattr(response, "bank_reference", "") or "").strip()

            if status == PayoutStatus.CONFIRMED and bank_ref:
                rec.write({"rail_status": "confirmed", "bank_confirmation_ref": bank_ref})
                rec._finalize_payout_execution()
            elif status == PayoutStatus.FAILED:
                rec.rail_status = "failed"
            else:
                if rec.rail_status != "failed":
                    rec.rail_status = "pending_bank_confirmation"
                rec.message_post(
                    body="Read-back: no bank response available for rail batch %s — payout "
                    "remains pending bank confirmation (not marked paid)." % rec.rail_batch_id
                )

    def action_generate_beftn(self, rail_instance=None):
        """Generate the BEFTN standard 128-byte batch file (fallback rail).

        Generating the file disburses nothing: the file still has to be
        uploaded to the sponsor bank and settled through BEFTN. The run moves
        to ``file_generated`` — commissions stay unpaid and no disbursement is
        posted to the GL until a finance manager records the bank's settlement
        reference (action_confirm_bank_settlement). It previously marked the
        payout confirmed, commissions paid and posted the GL discharge."""
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve payout run before generating BEFTN fallback file.")

            if not rec.idempotency_key:
                rec.idempotency_key = f"IDEMP-BEFTN-{rec.name}-{uuid.uuid4().hex[:12]}"

            recipients = rec._prepare_payout_recipients()
            req = PayoutBatchRequest(
                batch_ref=rec.name,
                period=rec.period,
                recipients=tuple(recipients),
                idempotency_key=rec.idempotency_key,
                total_amount=Decimal(str(rec.total_payable)),
                recipient_count=len(recipients),
            )

            rail = rail_instance or rec._default_rail()
            result = rail.generate_beftn_fallback_batch(req)

            file_bytes = result.beftn_raw.encode("ascii")
            rec.write(
                {
                    "state": "file_generated",
                    "rail_type": "beftn",
                    "rail_status": "file_generated",
                    "rail_batch_id": result.rail_batch_id,
                    "beftn_file": base64.b64encode(file_bytes),
                    "beftn_filename": f"BEFTN_{rec.name.replace('/', '_')}.txt",
                }
            )

    def action_confirm_bank_settlement(self, bank_reference: str = ""):
        """Record the BANK's confirmation of a disbursement and finalise the run.

        The only route to ``executed`` for a payout without a confirmed rail
        response (BEFTN file runs, timed-out / pending API runs). Requires the
        bank-issued settlement reference — passed in, or entered on the run's
        ``bank_confirmation_ref`` field — and a finance manager."""
        if not (
            self.env.user.has_group("account.group_account_manager")
            or self.env.user.has_group("base.group_system")
        ):
            raise AccessError("Only Finance Managers can confirm a bank settlement.")
        for rec in self:
            if rec.state not in ("executing", "file_generated"):
                raise UserError(
                    "Payout %s is not awaiting bank confirmation (state: %s)."
                    % (rec.name, rec.state)
                )
            if rec.rail_status == "failed":
                raise UserError(
                    "The rail reported payout %s as FAILED; it cannot be confirmed." % rec.name
                )
            ref = (bank_reference or rec.bank_confirmation_ref or "").strip()
            if not ref:
                raise UserError(
                    "Enter the bank's settlement reference for payout %s before confirming "
                    "it — a disbursement is never confirmed without the bank's evidence." % rec.name
                )
            rec.write(
                {
                    "bank_confirmation_ref": ref,
                    "bank_confirmed_by_id": self.env.user.id,
                    "bank_confirmed_at": fields.Datetime.now(),
                    "rail_status": "confirmed",
                }
            )
            rec._finalize_payout_execution()

    def _finalize_payout_execution(self):
        """Finalize executed payout run: mark paid, generate bilingual statements, and post to GL."""
        self.ensure_one()
        # freeze the clawback recoveries BEFORE the run turns executed
        deductions = self._clawback_deductions()
        Recovery = self.env["fix.settlement.recovery"]
        for _payee, pairs in deductions.items():
            for claw, amount in pairs:
                Recovery.create(
                    {"adjustment_id": claw.id, "payout_run_id": self.id, "amount": amount}
                )
                if claw.remaining_amount <= 0.005:
                    claw.state = "recovered"
        self.state = "executed"
        self.commission_ids.write({"state": "paid"})

        # Generate bilingual statements for each seller
        stmt_model = self.env["fix.seller.statement"]
        seller_groups: dict[models.Model, list] = {}
        for c in self.commission_ids:
            seller_groups.setdefault(c.seller_partner_id, []).append(c)

        for seq, (seller, comms) in enumerate(seller_groups.items(), start=1):
            gross_tot = sum(c.gross_amount for c in comms)
            comm_tot = sum(c.commission_amount for c in comms)
            tds_tot = sum(c.tds_amount or 0.0 for c in comms)
            clawback_tot = sum(amt for _c, amt in deductions.get(seller, []))
            net_tot = sum(c.net_payable for c in comms) - clawback_tot
            cert_ref = f"NBR-TDS52-{fields.Date.today().year}-{seller.id:04d}-{seq:04d}"

            stmt_model.create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.operating_unit_id.id,
                    "seller_partner_id": seller.id,
                    "period": self.period,
                    "gross_gmv": gross_tot,
                    "commission_amount": comm_tot,
                    "tds_withheld": tds_tot,
                    "net_payable": net_tot,
                    "clawback_amount": clawback_tot,
                    "withholding_cert_ref": cert_ref,
                    "payout_run_id": self.id,
                    "state": "issued",
                }
            )

        # Post payout execution to General Ledger
        self.action_post_payout_to_gl()

        publish(
            self.env,
            "payout.executed",
            "fix.payout.run",
            self.id,
            {
                "payout_run": self.name,
                "rail_type": self.rail_type,
                "rail_status": self.rail_status,
                "sellers_paid": len(seller_groups),
                "total_disbursed": float(self.total_payable),
                "tds_withheld": float(self.total_tds),
            },
        )

    def action_post_payout_to_gl(self):
        """Post payout discharge and statutory TDS withholding to General Ledger through M19.

        Only an EXECUTED run (bank- or rail-confirmed) is discharged, once.
        Each payee type clears its own payable (sellers 200200, partners the
        configured partner payable); clawbacks recovered in the run credit
        the customer-refund clearing account they reimburse."""
        for rec in self:
            if rec.gl_move_id:
                continue
            if rec.state != "executed":
                raise UserError(
                    "Payout %s is %s — only a confirmed (executed) payout is discharged in the GL"
                    % (rec.name, rec.state)
                )

            company = rec.company_id
            journal = _configured_journal(self.env, company)
            # Account codes per SETTLEMENT_ACCOUNTS: seller payable 200200,
            # TDS 210100 (ITA 2023 §52), disbursement bank 101000.
            tds_payable = _configured_account(self.env, company, "tds_payable")
            disbursement_bank = _configured_account(self.env, company, "clearing")

            by_role: dict[str, float] = {}
            for c in rec.commission_ids:
                role = c._payable_role()
                by_role[role] = by_role.get(role, 0.0) + c.net_payable + (c.tds_amount or 0.0)
            net_disbursed = rec.total_payable
            tds_withheld = rec.total_tds
            labels = {
                "seller_payable": "Discharge Seller Liability",
                "partner_payable": "Discharge Partner Commission Liability",
            }
            debit_lines = [
                (
                    0,
                    0,
                    {
                        "name": f"{labels[role]}: {rec.name}",
                        "account_id": _configured_account(self.env, company, role).id,
                        "debit": amount,
                        "credit": 0.0,
                    },
                )
                for role, amount in sorted(
                    by_role.items(), key=lambda kv: kv[0] != "seller_payable"
                )
            ]
            clawback_lines = []
            if rec.total_clawback > 0.005:
                recovery_acc = _configured_account(self.env, company, "clawback_recovery")
                clawback_lines.append(
                    (
                        0,
                        0,
                        {
                            "name": f"Clawbacks recovered: {rec.name}",
                            "account_id": recovery_acc.id,
                            "debit": 0.0,
                            "credit": rec.total_clawback,
                        },
                    )
                )

            move_vals = {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": fields.Date.context_today(rec),
                "ref": f"PAYOUT-DISCHARGE-{rec.name}",
                "line_ids": debit_lines
                + clawback_lines
                + [
                    (
                        0,
                        0,
                        {
                            "name": f"Statutory TDS Withheld (ITA 2023 §52): {rec.name}",
                            "account_id": tds_payable.id,
                            "debit": 0.0,
                            "credit": tds_withheld,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": f"Net Disbursed Funds via {rec.rail_type}: {rec.name}",
                            "account_id": disbursement_bank.id,
                            "debit": 0.0,
                            "credit": net_disbursed,
                        },
                    ),
                ],
            }

            n_pay = len(debit_lines) + len(clawback_lines)
            dim_by_line = {
                i: {"operating_unit_id": rec.operating_unit_id.id, "cost_centre": "CC-PAY"}
                for i in range(n_pay)
            }
            dim_by_line[n_pay] = {
                "operating_unit_id": rec.operating_unit_id.id,
                "cost_centre": "CC-TAX",
            }
            dim_by_line[n_pay + 1] = {
                "operating_unit_id": rec.operating_unit_id.id,
                "cost_centre": "CC-TREAS",
            }

            move, _ = post_with_dimensions(self.env, move_vals, dim_by_line, source="settlement")
            rec.gl_move_id = move.id
