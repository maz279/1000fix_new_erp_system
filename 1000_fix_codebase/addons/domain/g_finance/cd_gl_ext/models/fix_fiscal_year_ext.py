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

from odoo import fields, models
from odoo.exceptions import UserError

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


def compute_trial_balance(env, company, date_from, date_to) -> dict:
    rows = ledger_balances(env, company, date_from, date_to, None)
    total_debit = sum_rows(rows, "debit")
    total_credit = sum_rows(rows, "credit")
    return {
        "report": "trial_balance",
        "company": company.name,
        "date_from": str(date_from),
        "date_to": str(date_to),
        "currency": company.currency_id.name,
        "basis": "posted account.move.line",
        "lines": rows,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "balanced": round(total_debit - total_credit, 2) == 0,
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
        "basis": "aggregation across companies — eliminations not applied (future phase)",
        "company_count": len(companies),
        "per_company": per_company,
        "lines": sorted(combined_lines.values(), key=lambda r: r["account_code"]),
        **({"net_profit": totals["net_profit"]} if report_type == "pnl" else {}),
    }


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class FixFiscalYearIntegration(models.Model):
    """Extension connecting Odoo/OCA fiscal periods with 1000FiX 5-day close (CD-M19-01)."""

    _name = "fix.fiscal.period.bridge"
    _description = "Fiscal Year and Period Close Bridge"
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
        default=False,
    )
    locked_at = fields.Datetime(readonly=True)

    def action_lock_journals(self) -> dict:
        """Lock journal dates upon successful 5-day month-end close.

        Odoo 19 keeps lock dates on the COMPANY (account.journal carries no
        lock field), so the close sets the company's Global Lock Date
        (fiscalyear_lock_date): no journal can post on or before the closed
        period end. The lock only ever moves FORWARD — re-locking an older
        period must not unlock periods closed after it."""
        self.ensure_one()
        if self.period_close_id.state != "closed":
            raise UserError("Cannot lock journals before period close is completed.")

        period_end = self.period_close_id.period_end
        company = self.company_id.sudo()
        if not company.fiscalyear_lock_date or company.fiscalyear_lock_date < period_end:
            company.write({"fiscalyear_lock_date": period_end})

        self.write(
            {
                "is_locked": True,
                "locked_at": fields.Datetime.now(),
            }
        )
        _logger.info(
            "Journals locked for company %s up to %s",
            self.company_id.name,
            company.fiscalyear_lock_date,
        )
        return {
            "status": "locked",
            "date": str(period_end),
            "lock_date": str(company.fiscalyear_lock_date),
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
    generated_at = fields.Datetime(readonly=True)
    report_data = fields.Text(string="Serialized Report Data")

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
        if not fy:
            raise UserError("Select the fiscal year to compute %s for." % self.name)
        if fy.company_id and fy.company_id != self.company_id:
            raise UserError(
                "Fiscal year %s belongs to %s, not %s."
                % (fy.name, fy.company_id.name, self.company_id.name)
            )
        if self.report_type == "trial_balance":
            data = compute_trial_balance(self.env, self.company_id, fy.date_from, fy.date_to)
            data["fiscal_year"] = fy.name
        elif self.report_type == "pnl":
            data = compute_pnl(self.env, self.company_id, fy.date_from, fy.date_to)
            data["fiscal_year"] = fy.name
        else:  # balance_sheet
            data = compute_balance_sheet(self.env, self.company_id, fy.date_to)
            data["fiscal_year"] = fy.name
        rows = data["lines"]
        self.write({"generated_at": fields.Datetime.now(), "report_data": json.dumps(data)})
        return {"status": "generated", "type": self.report_type, "line_count": len(rows)}
