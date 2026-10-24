# cd_gl_ext — Integration and extensions for vendored OCA finance layer (P06-M01-T01).
# Extends OCA account-financial-tools, account-financial-reporting, mis-builder, and reporting-engine.
# Never forks vendor code (FF-03 / AS-05).
from __future__ import annotations

import json
import logging
from decimal import Decimal

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


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
        """Posted journal items of the company summed per account.

        ``date_from`` None = from inception (balance-sheet accounts carry
        their balance forward); ``pl_accounts`` True/False restricts to
        P&L / balance-sheet accounts, None = all accounts."""
        domain = [
            ("company_id", "=", self.company_id.id),
            ("parent_state", "=", "posted"),
            ("date", "<=", date_to),
        ]
        if date_from:
            domain.append(("date", ">=", date_from))
        if pl_accounts is not None:
            domain.append(
                ("account_id.internal_group", "in" if pl_accounts else "not in", self.PL_GROUPS)
            )
        groups = self.env["account.move.line"]._read_group(
            domain, ["account_id"], ["debit:sum", "credit:sum", "balance:sum"]
        )
        rows = []
        for account, debit, credit, balance in groups:
            rows.append(
                {
                    "account_code": account.with_company(self.company_id).code or "",
                    "account_name": account.name or "",
                    "internal_group": account.internal_group or "",
                    "debit": round(debit or 0.0, 2),
                    "credit": round(credit or 0.0, 2),
                    "balance": round(balance or 0.0, 2),
                }
            )
        return sorted(rows, key=lambda r: r["account_code"])

    @staticmethod
    def _sum(rows: list[dict], key: str) -> float:
        return float(sum((Decimal(str(r[key])) for r in rows), Decimal("0")))

    def action_generate_report(self) -> dict:
        """Compute the statement from POSTED journal items of the fiscal year.

        - trial_balance: per-account debit / credit / balance movements of
          the fiscal year (all accounts); debits must equal credits.
        - pnl: income and expense accounts, fiscal-year movements; net profit
          = -(sum of balances) (income is credit-normal).
        - balance_sheet: asset / liability / equity accounts cumulative to the
          fiscal-year end, plus the unclosed P&L to date, which together
          must sum to zero.
        cash_flow and vat_subledger are not computed here and are refused.
        (This action used to write the constant {"status": "computed"} without
        reading the ledger.)"""
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
        data = {
            "report": self.report_type,
            "company": self.company_id.name,
            "fiscal_year": fy.name,
            "date_from": str(fy.date_from),
            "date_to": str(fy.date_to),
            "currency": self.company_id.currency_id.name,
            "basis": "posted account.move.line",
        }
        if self.report_type == "trial_balance":
            rows = self._ledger_balances(fy.date_from, fy.date_to, None)
            data.update(
                lines=rows,
                total_debit=self._sum(rows, "debit"),
                total_credit=self._sum(rows, "credit"),
            )
            data["balanced"] = round(data["total_debit"] - data["total_credit"], 2) == 0
        elif self.report_type == "pnl":
            rows = self._ledger_balances(fy.date_from, fy.date_to, True)
            data.update(lines=rows, net_profit=round(-self._sum(rows, "balance"), 2))
        else:  # balance_sheet
            rows = self._ledger_balances(None, fy.date_to, False)
            pl_to_date = self._ledger_balances(None, fy.date_to, True)
            unclosed_pl = round(-self._sum(pl_to_date, "balance"), 2)
            data.update(
                lines=rows,
                unclosed_profit_and_loss=unclosed_pl,
                balanced=round(self._sum(rows, "balance") - unclosed_pl, 2) == 0,
            )
        self.write({"generated_at": fields.Datetime.now(), "report_data": json.dumps(data)})
        return {"status": "generated", "type": self.report_type, "line_count": len(rows)}
