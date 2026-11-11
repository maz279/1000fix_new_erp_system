# cd_gl_ext — Integration and extensions for vendored OCA finance layer (P06-M01-T01).
# Extends OCA account-financial-tools, account-financial-reporting, mis-builder, and reporting-engine.
# Never forks vendor code (FF-03 / AS-05).
#
# The statement computations live as module-level pure functions so the
# /p03/gl endpoints (and anything else) can compute a statement for any date
# range without a bridge record; the fix.financial.report.bridge model
# delegates to them, unchanged in behaviour.
from __future__ import annotations

import json
import logging
from decimal import Decimal

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pure statement computations — every figure from POSTED account.move.line.
# ---------------------------------------------------------------------------
def ledger_balances(env, company, date_from, date_to, pl_accounts: bool | None) -> list[dict]:
    """Posted journal items of the company summed per account.

    ``date_from`` None = from inception (balance-sheet accounts carry their
    balance forward); ``pl_accounts`` True/False restricts to P&L /
    balance-sheet accounts, None = all accounts."""
    domain = [
        ("company_id", "=", company.id),
        ("parent_state", "=", "posted"),
        ("date", "<=", date_to),
    ]
    if date_from:
        domain.append(("date", ">=", date_from))
    if pl_accounts is not None:
        domain.append(
            ("account_id.internal_group", "in" if pl_accounts else "not in", ("income", "expense"))
        )
    groups = env["account.move.line"]._read_group(
        domain, ["account_id"], ["debit:sum", "credit:sum", "balance:sum"]
    )
    rows = []
    for account, debit, credit, balance in groups:
        rows.append(
            {
                "account_code": account.with_company(company).code or "",
                "account_name": account.name or "",
                "internal_group": account.internal_group or "",
                "debit": round(debit or 0.0, 2),
                "credit": round(credit or 0.0, 2),
                "balance": round(balance or 0.0, 2),
            }
        )
    return sorted(rows, key=lambda r: r["account_code"])


def sum_rows(rows: list[dict], key: str) -> float:
    return float(sum((Decimal(str(r[key])) for r in rows), Decimal("0")))


PL_GROUPS = ("income", "expense")


def _posted_sums(env, company, domain) -> dict:
    """{account: (debit, credit, balance)} of the company's posted journal items."""
    groups = env["account.move.line"]._read_group(
        [("company_id", "=", company.id), ("parent_state", "=", "posted"), *domain],
        ["account_id"],
        ["debit:sum", "credit:sum", "balance:sum"],
    )
    return {
        account: (debit or 0.0, credit or 0.0, balance or 0.0)
        for account, debit, credit, balance in groups
    }


def opening_balances(env, company, date_from) -> tuple[dict, float]:
    """What the accounts bring into a period that starts on ``date_from``.

    Balance-sheet accounts carry everything before it. Income and expense
    accounts carry this fiscal year only. The profit or loss of earlier years
    belongs to no income or expense account any more: it is returned apart,
    for the undistributed-earnings line. Returns ({account: balance}, that)."""
    date_from = fields.Date.to_date(date_from)
    fy_start = company.compute_fiscalyear_dates(date_from)["date_from"]
    before = ("date", "<", date_from)
    opening = {
        account: sums[2]
        for account, sums in _posted_sums(
            env, company, [before, ("account_id.internal_group", "not in", PL_GROUPS)]
        ).items()
    }
    if fy_start < date_from:
        this_year = [
            before,
            ("date", ">=", fy_start),
            ("account_id.internal_group", "in", PL_GROUPS),
        ]
        for account, sums in _posted_sums(env, company, this_year).items():
            opening[account] = sums[2]
    earlier = _posted_sums(
        env, company, [("date", "<", fy_start), ("account_id.internal_group", "in", PL_GROUPS)]
    )
    return opening, round(sum(sums[2] for sums in earlier.values()), 2)


def compute_trial_balance(env, company, date_from, date_to) -> dict:
    """Opening + movement = closing per account. ``debit`` / ``credit`` are the
    movement of the window, ``balance`` is the closing balance. The window alone
    used to be summed, so a dated trial balance dropped every brought-forward
    balance (the bank read its month's movement, equity read nothing)."""
    window = [("date", "<=", date_to)]
    if date_from:
        window.append(("date", ">=", date_from))
    movement = _posted_sums(env, company, window)
    opening, earlier_years = opening_balances(env, company, date_from) if date_from else ({}, 0.0)

    Account = env["account.account"].with_company(company)
    extra_row = None
    if earlier_years:
        unaffected = Account.search(
            [*Account._check_company_domain(company), ("account_type", "=", "equity_unaffected")],
            limit=1,
        )
        if unaffected:
            opening[unaffected] = opening.get(unaffected, 0.0) + earlier_years
        else:
            # no undistributed-earnings account on this chart: say what it is
            extra_row = {
                "account_code": "",
                "account_name": "Profit and loss of earlier fiscal years (undistributed)",
                "internal_group": "equity",
                "opening_balance": earlier_years,
                "debit": 0.0,
                "credit": 0.0,
                "balance": earlier_years,
            }

    rows = [extra_row] if extra_row else []
    for account in set(movement) | set(opening):
        debit, credit, _balance = movement.get(account, (0.0, 0.0, 0.0))
        brought = round(opening.get(account, 0.0), 2)
        if not (brought or debit or credit):
            continue
        rows.append(
            {
                "account_code": account.with_company(company).code or "",
                "account_name": account.name or "",
                "internal_group": account.internal_group or "",
                "opening_balance": brought,
                "debit": round(debit, 2),
                "credit": round(credit, 2),
                "balance": round(brought + round(debit, 2) - round(credit, 2), 2),
            }
        )
    rows.sort(key=lambda r: r["account_code"])
    total_debit = sum_rows(rows, "debit")
    total_credit = sum_rows(rows, "credit")
    closing_debit = float(
        sum((Decimal(str(r["balance"])) for r in rows if r["balance"] > 0), Decimal("0"))
    )
    closing_credit = float(
        -sum((Decimal(str(r["balance"])) for r in rows if r["balance"] < 0), Decimal("0"))
    )
    return {
        "report": "trial_balance",
        "company": company.name,
        "date_from": str(date_from),
        "date_to": str(date_to),
        "currency": company.currency_id.name,
        "basis": "posted account.move.line; opening balance brought forward "
        "(income and expense from the start of the fiscal year)",
        "lines": rows,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "total_opening_balance": sum_rows(rows, "opening_balance"),
        "total_closing_debit": closing_debit,
        "total_closing_credit": closing_credit,
        "balanced": round(total_debit - total_credit, 2) == 0
        and round(closing_debit - closing_credit, 2) == 0,
    }


def compute_pnl(env, company, date_from, date_to) -> dict:
    rows = ledger_balances(env, company, date_from, date_to, True)
    return {
        "report": "pnl",
        "company": company.name,
        "date_from": str(date_from),
        "date_to": str(date_to),
        "currency": company.currency_id.name,
        "basis": "posted account.move.line",
        "lines": rows,
        "net_profit": round(-sum_rows(rows, "balance"), 2),
    }


def compute_balance_sheet(env, company, date_to) -> dict:
    rows = ledger_balances(env, company, None, date_to, False)
    pl_to_date = ledger_balances(env, company, None, date_to, True)
    unclosed_pl = round(-sum_rows(pl_to_date, "balance"), 2)
    return {
        "report": "balance_sheet",
        "company": company.name,
        "date_from": None,
        "date_to": str(date_to),
        "currency": company.currency_id.name,
        "basis": "posted account.move.line",
        "lines": rows,
        "unclosed_profit_and_loss": unclosed_pl,
        "balanced": round(sum_rows(rows, "balance") - unclosed_pl, 2) == 0,
    }


# Cash-flow category of a journal entry, judged by its NON-cash counterpart
# lines (direct method lite). Entries whose counterparts are all cash
# accounts are internal transfers; anything unrecognised is reported as
# "Unclassified" — never forced into a category it does not evidence.
def _cash_flow_category(move, cash_account_ids) -> str:
    counterparts = [ln for ln in move.line_ids if ln.account_id.id not in cash_account_ids]
    if not counterparts:
        return "Internal Transfers"
    groups = {ln.account_id.internal_group for ln in counterparts}
    types = {ln.account_id.account_type for ln in counterparts}
    if groups & {"income", "expense"} or types & {
        "asset_receivable",
        "liability_payable",
        "asset_current",
        "liability_current",
    }:
        return "Operating Activities"
    if types & {"asset_fixed", "asset_non_current"}:
        return "Investing Activities"
    if groups & {"equity"} or types & {"liability_non_current"}:
        return "Financing Activities"
    return "Unclassified"


def compute_cash_flow(env, company, date_from, date_to) -> dict:
    """Direct-method cash flow (lite) from the POSTED movement of the
    company's cash & bank accounts (account_type asset_cash), categorised by
    each entry's counterpart lines. When the GL cash accounts carry no
    movement in the window the report falls back to M50 payment executions —
    listed by method and explicitly marked uncategorised, because the
    execution seam carries no operating/investing/financing tag (nothing is
    invented to fill a section)."""
    Account = env["account.account"].with_company(company)
    cash_accounts = Account.search(
        [*Account._check_company_domain(company), ("account_type", "=", "asset_cash")]
    )
    cash_ids = set(cash_accounts.ids)

    opening = 0.0
    if cash_ids:
        domain_before = [
            ("company_id", "=", company.id),
            ("parent_state", "=", "posted"),
            ("account_id", "in", list(cash_ids)),
            ("date", "<", date_from),
        ]
        groups = env["account.move.line"]._read_group(domain_before, [], ["balance:sum"])
        opening = round(sum(g[0] or 0.0 for g in groups), 2)

    domain = [
        ("company_id", "=", company.id),
        ("parent_state", "=", "posted"),
        ("account_id", "in", list(cash_ids)),
        ("date", ">=", date_from),
        ("date", "<=", date_to),
    ]
    lines = env["account.move.line"].search(domain)
    categories: dict[str, float] = {}
    basis = "posted cash/bank account.move.line (direct method)"
    if lines:
        for move in lines.mapped("move_id"):
            category = _cash_flow_category(move, cash_ids)
            movement = round(
                sum(ln.balance for ln in move.line_ids if ln.account_id.id in cash_ids),
                2,
            )
            categories[category] = round(categories.get(category, 0.0) + movement, 2)
    else:
        # M50 fallback — honest about what it is.
        basis = "M50 payment executions (no GL cash movement in window)"
        Payment = env["fix.payment.execution"].sudo()
        payments = Payment.search(
            [
                ("company_id", "=", company.id),
                ("state", "=", "executed"),
                ("executed_at", ">=", fields.Datetime.to_datetime(date_from)),
            ]
        )
        for payment in payments:
            label = "Payments Executed — %s (uncategorised)" % dict(
                Payment._fields["method"].selection
            ).get(payment.method, payment.method)
            categories[label] = round(categories.get(label, 0.0) + payment.amount, 2)

    net = round(sum(categories.values()), 2)
    return {
        "report": "cash_flow",
        "company": company.name,
        "date_from": str(date_from),
        "date_to": str(date_to),
        "currency": company.currency_id.name,
        "basis": basis,
        "categories": [{"category": c, "amount": a} for c, a in sorted(categories.items())],
        "opening_cash": opening,
        "net_movement": net,
        "closing_cash": round(opening + net, 2),
    }


def compute_consolidated(env, date_from, date_to, report_type="pnl") -> dict:
    """Consolidation lite: the same statement computed for EVERY company and
    summed. Per-company results are reported next to the combined figure —
    an aggregation, not a full consolidation: intercompany eliminations and
    currency translation remain a future phase and the report says so."""
    companies = env["res.company"].search([])
    per_company = []
    combined_lines: dict[str, dict] = {}
    totals = {"net_profit": 0.0}
    for company in companies:
        if report_type == "pnl":
            report = compute_pnl(env, company, date_from, date_to)
            totals["net_profit"] = round(totals["net_profit"] + report["net_profit"], 2)
        elif report_type == "balance_sheet":
            report = compute_balance_sheet(env, company, date_to)
        else:
            report = compute_trial_balance(env, company, date_from, date_to)
        per_company.append(
            {
                "company": company.name,
                "net_profit": report.get("net_profit"),
                "line_count": len(report["lines"]),
                "balanced": report.get("balanced"),
            }
        )
        for row in report["lines"]:
            key = row["account_code"]
            agg = combined_lines.setdefault(
                key,
                {
                    "account_code": key,
                    "account_name": row["account_name"],
                    "internal_group": row["internal_group"],
                    "debit": 0.0,
                    "credit": 0.0,
                    "balance": 0.0,
                },
            )
            agg["debit"] = round(agg["debit"] + row["debit"], 2)
            agg["credit"] = round(agg["credit"] + row["credit"], 2)
            agg["balance"] = round(agg["balance"] + row["balance"], 2)
    return {
        "report": "consolidated_%s" % report_type,
        "date_from": str(date_from),
        "date_to": str(date_to),
        "basis": "aggregation across companies — eliminations not applied here; the "
        "Consolidation Books (Group & Inter-Branch) apply inter-company eliminations",
        "company_count": len(companies),
        "per_company": per_company,
        "lines": sorted(combined_lines.values(), key=lambda r: r["account_code"]),
        **({"net_profit": totals["net_profit"]} if report_type == "pnl" else {}),
    }


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class FixFiscalYearIntegration(models.Model):
    """Extension connecting Odoo/OCA fiscal periods with 1000FiX 5-day close (CD-M19-01).

    The close itself sets the company lock date (fix.period.close.action_close);
    this bridge re-applies it idempotently and shows it. ``is_locked`` is READ from
    the company lock date — it used to be a free tick shown as "locked" on the
    Periods screen while nothing was locked (A08 M19-16)."""

    _name = "fix.fiscal.period.bridge"
    _description = "Fiscal Year and Period Close Bridge"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
    )
    fiscal_year_id = fields.Many2one(
        "account.fiscal.year",
        string="OCA Fiscal Year",
        ondelete="set null",
        help="Linked fiscal year from OCA account_fiscal_year",
    )
    period_close_id = fields.Many2one(
        "fix.period.close",
        string="1000FiX Period Close",
        required=True,
        ondelete="cascade",
    )
    is_locked = fields.Boolean(
        string="Journals Locked",
        compute="_compute_is_locked",
        help="True when the company Global Lock Date covers the period end.",
    )
    locked_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"locked_at"}

    @api.depends("company_id.fiscalyear_lock_date", "period_close_id.period_end")
    def _compute_is_locked(self):
        for bridge in self:
            lock = bridge.company_id.sudo().fiscalyear_lock_date
            end = bridge.period_close_id.period_end
            bridge.is_locked = bool(lock and end and lock >= end)

    def action_lock_journals(self) -> dict:
        """Lock journal dates upon successful 5-day month-end close.

        Odoo 19 keeps lock dates on the COMPANY (account.journal carries no
        lock field), so the close sets the company's Global Lock Date
        (fiscalyear_lock_date): no journal can post on or before the closed
        period end. The lock only ever moves FORWARD — re-locking an older
        period must not unlock periods closed after it. Accounting
        Administrator only, and only for a genuinely closed period that has
        ended (a forged 2099 close used to freeze the ledger, M19-6)."""
        self.ensure_one()
        if self.period_close_id.state != "closed":
            raise UserError("Cannot lock journals before period close is completed.")
        if not self.env.su and not self.env.user.has_group("account.group_account_manager"):
            raise AccessError("Locking the ledger needs the Accounting Administrator role.")
        if self.period_close_id.company_id != self.company_id:
            raise UserError("The bridge and the close belong to different companies.")
        period_end = self.period_close_id.period_end
        if period_end >= fields.Date.context_today(self):
            raise UserError("Period %s has not ended; it cannot be locked." % period_end)
        lock = self.period_close_id._fix_set_company_lock()
        self._guarded().write({"locked_at": fields.Datetime.now()})
        _logger.info("Journals locked for company %s up to %s", self.company_id.name, lock)
        return {
            "status": "locked",
            "date": str(period_end),
            "lock_date": str(lock),
        }


class FixMisReportBridge(models.Model):
    """Bridge linking 1000FiX KPIs with OCA mis-builder and account-financial-reporting."""

    _name = "fix.financial.report.bridge"
    _description = "Financial Reporting Bridge"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
    )
    name = fields.Char(
        string="Report Name",
        required=True,
    )
    report_type = fields.Selection(
        [
            ("pnl", "Income Statement / Profit & Loss"),
            ("balance_sheet", "Balance Sheet (Financial Position)"),
            ("cash_flow", "Statement of Cash Flows"),
            ("vat_subledger", "VAT Sub-Ledger Statement"),
            ("trial_balance", "Trial Balance"),
        ],
        string="Report Type",
        required=True,
        default="pnl",
    )
    fiscal_year_id = fields.Many2one(
        "account.fiscal.year",
        string="Fiscal Year",
        help="The fiscal year the statement is computed for (required to generate).",
    )
    date_from = fields.Date(
        string="From", help="Used when no fiscal year is selected (balance sheet: ignored)"
    )
    date_to = fields.Date(string="To", help="Used when no fiscal year is selected")
    generated_at = fields.Datetime(readonly=True)
    generated_by_id = fields.Many2one("res.users", string="Generated By", readonly=True)
    report_data = fields.Text(string="Serialized Report Data", readonly=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    line_count = fields.Integer(string="Lines", readonly=True)
    headline_amount = fields.Monetary(
        string="Headline Figure",
        readonly=True,
        help="Net profit (P&L), total assets (balance sheet) or total debits (trial balance)",
    )
    is_balanced = fields.Boolean(string="Balanced", readonly=True)

    PL_GROUPS = ("income", "expense")
    # Report types this bridge computes from the ledger. The others need a
    # dedicated engine (OCA mis-builder / the VAT return's sub-ledger
    # reconciliation) and are refused rather than answered with a stub.
    SUPPORTED_TYPES = ("pnl", "balance_sheet", "trial_balance")

    def _ledger_balances(self, date_from, date_to, pl_accounts: bool | None) -> list[dict]:
        return ledger_balances(self.env, self.company_id, date_from, date_to, pl_accounts)

    @staticmethod
    def _sum(rows: list[dict], key: str) -> float:
        return sum_rows(rows, key)

    def action_generate_report(self) -> dict:
        """Compute the statement from POSTED journal items of the fiscal year
        (delegates to the module-level pure computations — same outputs)."""
        self.ensure_one()
        if self.report_type not in self.SUPPORTED_TYPES:
            raise UserError(
                "%s is not computed by this bridge — use the dedicated report "
                "(mis-builder statement / VAT return sub-ledger reconciliation)."
                % dict(self._fields["report_type"].selection)[self.report_type]
            )
        fy = self.fiscal_year_id
        if fy:
            if fy.company_id and fy.company_id != self.company_id:
                raise UserError(
                    "Fiscal year %s belongs to %s, not %s."
                    % (fy.name, fy.company_id.name, self.company_id.name)
                )
            date_from, date_to, label = fy.date_from, fy.date_to, fy.name
        elif self.date_to and (self.date_from or self.report_type == "balance_sheet"):
            date_from, date_to = self.date_from, self.date_to
            label = "%s - %s" % (date_from or "", date_to)
        else:
            raise UserError(
                "Select the fiscal year (or a From/To period) to compute %s for." % self.name
            )
        if date_from and date_to and date_from > date_to:
            raise UserError("The period start must not be after its end.")
        if self.report_type == "trial_balance":
            data = compute_trial_balance(self.env, self.company_id, date_from, date_to)
            headline = data["total_debit"]
        elif self.report_type == "pnl":
            data = compute_pnl(self.env, self.company_id, date_from, date_to)
            headline = data["net_profit"]
        else:  # balance_sheet
            data = compute_balance_sheet(self.env, self.company_id, date_to)
            headline = round(
                sum(r["balance"] for r in data["lines"] if r["internal_group"] == "asset"), 2
            )
        data["fiscal_year"] = label
        rows = data["lines"]
        self.write(
            {
                "generated_at": fields.Datetime.now(),
                "generated_by_id": self.env.user.id,
                "report_data": json.dumps(data),
                "line_count": len(rows),
                "headline_amount": headline,
                "is_balanced": bool(data.get("balanced", True)),
            }
        )
        return {"status": "generated", "type": self.report_type, "line_count": len(rows)}
