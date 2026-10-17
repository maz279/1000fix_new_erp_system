# cd_gl_ext — Bangladesh Chart of Accounts (MD-035) Odoo Integration & Master Data Loader.
from __future__ import annotations

import hashlib
import logging
from decimal import Decimal
from pathlib import Path
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish
from . import coa_logic

_logger = logging.getLogger(__name__)


class FixChartAccount(models.Model):
    """Statutory Bangladesh Chart of Accounts Account Model (MD-035 / CD-M19-01).
    
    Represents an account in the standardized 4-block format T-GG-SS-NNN,
    tracking control subledger bindings and dimensional tagging rules.
    """

    _name = "fix.chart.account"
    _description = "Bangladesh Statutory Chart Account"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "account_code, company_id"

    _unique_company_code = models.Constraint(
        "UNIQUE (company_id, account_code)",
        "Account code must be unique per company"
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )
    account_code = fields.Char(
        string="Account Code",
        required=True,
        index=True,
        help="Four-block structure: T-GG-SS-NNN",
    )
    name = fields.Char(
        string="Account Name",
        required=True,
        index=True,
    )
    account_type = fields.Selection(
        [
            ("asset", "Asset"),
            ("liability", "Liability"),
            ("equity", "Equity"),
            ("income", "Income"),
            ("expense", "Expense"),
        ],
        string="Account Type",
        required=True,
        index=True,
    )
    account_subtype = fields.Char(
        string="Account Subtype",
        help="current_asset, fixed_asset, receivable, payable, bank, cash, stock, tax, revenue, cogs, opex",
    )
    is_postable = fields.Boolean(
        string="Postable",
        default=True,
        help="Only leaf accounts may be postable (COA-01)",
    )
    is_control_account = fields.Boolean(
        string="Control Account",
        default=False,
        help="A control account may not be posted to directly (COA-02)",
    )
    control_subledger = fields.Selection(
        [
            ("receivable", "Accounts Receivable"),
            ("payable", "Accounts Payable"),
            ("stock", "Inventory Stock"),
            ("fixed_asset", "Fixed Assets"),
            ("tax", "Statutory Tax & VAT"),
        ],
        string="Control Subledger",
    )
    requires_dimension = fields.Char(
        string="Requires Dimension",
        help="Semicolon-separated dimensions: branch;cost_centre;business_line (COA-03)",
    )
    statutory_group = fields.Char(
        string="Statutory Group",
        required=True,
        help="Mandatory reporting group line (COA-05)",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT"),
    )
    balance = fields.Monetary(
        string="Current Balance",
        currency_field="currency_id",
        default=0.0,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    odoo_account_id = fields.Many2one(
        "account.account",
        string="Linked Odoo Account",
        ondelete="set null",
    )

    @api.constrains("account_code", "is_postable", "statutory_group")
    def _check_coa_rules(self):
        for acc in self:
            rec = coa_logic.AccountRecord(
                account_code=acc.account_code,
                entity_code=acc.company_id.code if hasattr(acc.company_id, "code") else "EN-01",
                account_name=acc.name,
                account_type=acc.account_type,
                account_subtype=acc.account_subtype or "",
                is_postable=acc.is_postable,
                is_control_account=acc.is_control_account,
                control_subledger=acc.control_subledger,
                requires_dimension=set(acc.requires_dimension.split(";")) if acc.requires_dimension else set(),
                statutory_group=acc.statutory_group or "",
                active=acc.active,
            )
            try:
                coa_logic.validate_account_structure(rec)
                if acc.is_postable:
                    parts = acc.account_code.split("-")
                    if len(parts) == 4 and parts[3] == "000":
                        raise coa_logic.CoaValidationError(
                            acc.account_code,
                            "Non-leaf summary account cannot be postable (COA-01)",
                            "ERR-COA-001"
                        )
            except coa_logic.CoaValidationError as e:
                raise ValidationError(str(e))

    def action_archive(self):
        """Archive account enforcing COA-04: zero-balance guard."""
        for acc in self:
            if acc.balance != 0.0:
                raise UserError(
                    f"Cannot archive account {acc.account_code} with non-zero balance {acc.balance:.2f} BDT (COA-04)"
                )
            acc.write({"active": False})


class FixChartLoader(models.Model):
    """Loader and Reconciler for Bangladesh Chart of Accounts (MD-035)."""

    _name = "fix.chart.loader"
    _description = "Chart of Accounts Loader"
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
    source_file = fields.Char(
        string="Source File",
        default="project_content/02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.csv",
    )
    loaded_at = fields.Datetime(readonly=True)
    account_count = fields.Integer(readonly=True)
    postable_count = fields.Integer(readonly=True)
    control_count = fields.Integer(readonly=True)
    checksum = fields.Char(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("loaded", "Loaded"), ("reconciled", "Reconciled")],
        default="draft",
        required=True,
    )

    def action_load_from_csv(self, csv_text: str | None = None) -> dict:
        """Load Chart of Accounts from CSV text or file path."""
        self.ensure_one()
        if not csv_text:
            candidates = [
                Path(__file__).resolve().parents[4] / self.source_file,
                Path(__file__).resolve().parents[5] / self.source_file,
                Path(__file__).resolve().parents[6] / self.source_file,
            ]
            csv_path = next((p for p in candidates if p.exists()), candidates[0])
            if not csv_path.exists():
                raise UserError(f"Master data file not found: {csv_path}")
            csv_text = csv_path.read_text(encoding="utf-8")

        sha256 = hashlib.sha256(csv_text.encode("utf-8")).hexdigest()
        records = coa_logic.parse_coa_csv(csv_text)
        result = coa_logic.validate_coa_rules(records)

        acc_model = self.env["fix.chart.account"]
        for rec in records:
            existing = acc_model.search([
                ("company_id", "=", self.company_id.id),
                ("account_code", "=", rec.account_code),
            ], limit=1)

            vals = {
                "company_id": self.company_id.id,
                "operating_unit_id": self.operating_unit_id.id if self.operating_unit_id else False,
                "account_code": rec.account_code,
                "name": rec.account_name,
                "account_type": rec.account_type,
                "account_subtype": rec.account_subtype,
                "is_postable": rec.is_postable,
                "is_control_account": rec.is_control_account,
                "control_subledger": rec.control_subledger,
                "requires_dimension": ";".join(sorted(rec.requires_dimension)),
                "statutory_group": rec.statutory_group,
                "active": rec.active,
            }
            if existing:
                existing.write(vals)
            else:
                acc_model.create(vals)

        self.write({
            "state": "loaded",
            "loaded_at": fields.Datetime.now(),
            "account_count": result["account_count"],
            "postable_count": result["postable_count"],
            "control_count": result["control_count"],
            "checksum": sha256,
        })

        publish(self.env, "coa.loaded", "fix.chart.loader", self.id, {
            "company_id": self.company_id.id,
            "account_count": result["account_count"],
            "postable_count": result["postable_count"],
            "sha256": sha256,
        })
        return {
            "status": "loaded",
            "account_count": result["account_count"],
            "postable_count": result["postable_count"],
            "sha256": sha256,
        }

    def action_reconcile_chart(self) -> dict:
        """Execute trial balance reconciliation check across loaded accounts."""
        self.ensure_one()
        accounts = self.env["fix.chart.account"].search([
            ("company_id", "=", self.company_id.id),
        ])
        if not accounts:
            raise UserError("No accounts loaded for company")

        acc_records = []
        balances = {}
        for a in accounts:
            val = getattr(a, "balance", 0.0)
            bal_dec = coa_logic.Decimal(str(val)) if isinstance(val, (int, float, Decimal)) else coa_logic.Decimal("0.00")
            rec = coa_logic.AccountRecord(
                account_code=a.account_code,
                entity_code="EN-01",
                account_name=a.name,
                account_type=a.account_type,
                account_subtype=a.account_subtype or "",
                is_postable=a.is_postable,
                is_control_account=a.is_control_account,
                control_subledger=a.control_subledger,
                requires_dimension=set(a.requires_dimension.split(";")) if a.requires_dimension else set(),
                statutory_group=a.statutory_group,
                active=a.active,
                balance=bal_dec,
            )
            acc_records.append(rec)
            balances[a.account_code] = bal_dec

        recon_res = coa_logic.reconcile_trial_balance(balances, acc_records)
        self.write({"state": "reconciled"})
        return recon_res
