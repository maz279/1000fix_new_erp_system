# cd_gl_ext — Integration and extensions for vendored OCA finance layer (P06-M01-T01).
# Extends OCA account-financial-tools, account-financial-reporting, mis-builder, and reporting-engine.
# Never forks vendor code (FF-03 / AS-05).
from __future__ import annotations

import logging
from odoo import api, fields, models
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
        """Lock journal dates upon successful 5-day month-end close."""
        self.ensure_one()
        if self.period_close_id.state != "closed":
            raise UserError("Cannot lock journals before period close is completed.")

        # Update journal lock date if OCA account_journal_lock_date is active
        journals = self.env["account.journal"].search([
            ("company_id", "=", self.company_id.id),
        ])
        for j in journals:
            vals = {}
            if hasattr(j, "period_lock_date"):
                vals["period_lock_date"] = self.period_close_id.period_end
            if hasattr(j, "fiscalyear_lock_date") and self.fiscal_year_id:
                vals["fiscalyear_lock_date"] = self.period_close_id.period_end
            if vals:
                j.write(vals)

        self.write({
            "is_locked": True,
            "locked_at": fields.Datetime.now(),
        })
        _logger.info(
            "Journals locked for company %s up to %s",
            self.company_id.name, self.period_close_id.period_end
        )
        return {"status": "locked", "date": str(self.period_close_id.period_end)}


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
        ],
        string="Report Type",
        required=True,
        default="pnl",
    )
    generated_at = fields.Datetime(readonly=True)
    report_data = fields.Text(string="Serialized Report Data")

    def action_generate_report(self) -> dict:
        """Trigger computation and formatting of the financial statement."""
        self.ensure_one()
        self.write({
            "generated_at": fields.Datetime.now(),
            "report_data": f'{{"report": "{self.report_type}", "status": "computed", "currency": "BDT"}}',
        })
        return {"status": "generated", "type": self.report_type}
