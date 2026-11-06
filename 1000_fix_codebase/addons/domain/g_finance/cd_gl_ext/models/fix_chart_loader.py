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


# The COA unification map (FR-FIN-002): Odoo posting-chart code -> MD-035
# statutory account code. Only semantically certain pairs are linked — an
# arbitrary link is worse than none because it turns on the posting rules
# (FR-FIN-011) for that account. Codes measured in fix_dev's generic
# Bangladeshi chart template; extend as accounts are configured.
ODOO_CHART_MAPPING = {
    "101401": "1-10-20-010",  # Bank -> Operating bank account - BDT
    "101402": "1-10-99-998",  # Bank suspense -> POS payment clearing
    "121000": "1-20-10-010",  # Account Receivable -> Trade receivables - retail repair
    "128000": "1-20-20-020",  # Prepaid Expenses -> Security deposits and prepayments
    "211000": "2-10-10-010",  # Account Payable -> Trade payables - spare parts suppliers
    "131000": "2-30-20-010",  # Tax Paid -> Input VAT credit deductible
    "230000": "2-40-10-010",  # Salary Payable -> Accrued employee salaries and wages
    "212000": "2-40-20-010",  # Deferred Revenue -> Customer advance repair deposits
    "251000": "2-30-10-010",  # Tax Received -> VAT payable - output Mushak 6.3 15%
    "252000": "2-30-30-010",  # Tax Payable -> TDS payable - supplier withholding
    "400000": "4-10-10-010",  # Product Sales -> Service revenue - out of warranty repair
    "450000": "4-90-10-010",  # Other Income -> Other income - scrap and e-waste
    "500000": "5-10-10-010",  # Cost of Goods Sold -> Direct spare parts consumed
    "612000": "5-20-10-010",  # Rent -> Branch rent and premises
    "620000": "5-20-40-010",  # Bank Fees -> Bank and payment gateway fees
    "630000": "5-20-20-010",  # Salary Expenses -> Office staff salaries and allowances
    "962000": "5-20-30-010",  # Sales Expenses -> Marketing and customer outreach
}


def _split_dimensions(value: str | bool) -> set[str]:
    """'branch;cost_centre' -> {'branch', 'cost_centre'} (blank items dropped)."""
    return {d.strip() for d in (value or "").split(";") if d.strip()}


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
        "UNIQUE (company_id, account_code)", "Account code must be unique per company"
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

    # Every field the per-account rules read re-triggers them: a write of
    # account_type / control flags / dimensions must not bypass validation.
    @api.constrains(
        "account_code",
        "account_type",
        "is_postable",
        "is_control_account",
        "control_subledger",
        "requires_dimension",
        "statutory_group",
    )
    def _check_coa_rules(self):
        for acc in self:
            rec = coa_logic.AccountRecord(
                account_code=acc.account_code,
                entity_code="EN-01",
                account_name=acc.name,
                account_type=acc.account_type,
                account_subtype=acc.account_subtype or "",
                is_postable=acc.is_postable,
                is_control_account=acc.is_control_account,
                control_subledger=acc.control_subledger or None,
                requires_dimension=_split_dimensions(acc.requires_dimension),
                statutory_group=acc.statutory_group or "",
                active=acc.active,
            )
            try:
                coa_logic.validate_account_structure(rec)
                coa_logic.validate_leaf_postable(rec)
            except coa_logic.CoaValidationError as e:
                raise ValidationError(str(e)) from e

    # Natural sign per account type: the ledger balance (debit - credit) is
    # positive for assets/expenses, negated for liabilities/equity/income.
    _NATURAL_SIGN = {"asset": 1, "expense": 1, "liability": -1, "equity": -1, "income": -1}

    def _ledger_balances(self) -> dict:
        """{statutory account id: natural-sign posted ledger balance} for the
        accounts linked to an Odoo account (unlinked accounts are absent)."""
        result = {}
        for company in self.mapped("company_id"):
            linked = self.filtered(lambda a, c=company: a.company_id == c and a.odoo_account_id)
            if not linked:
                continue
            groups = (
                self.env["account.move.line"]
                .sudo()
                ._read_group(
                    [
                        ("company_id", "=", company.id),
                        ("parent_state", "=", "posted"),
                        ("account_id", "in", linked.mapped("odoo_account_id").ids),
                    ],
                    ["account_id"],
                    ["balance:sum"],
                )
            )
            by_account = {account.id: balance or 0.0 for account, balance in groups}
            for acc in linked:
                raw = by_account.get(acc.odoo_account_id.id, 0.0)
                result[acc.id] = round(raw * self._NATURAL_SIGN[acc.account_type], 2)
        return result

    def action_archive(self):
        """Archive account enforcing COA-04: zero-balance guard, on both the
        recorded balance and the posted ledger balance of the linked account."""
        ledger = self._ledger_balances()
        for acc in self:
            for label, value in (("balance", acc.balance), ("ledger balance", ledger.get(acc.id))):
                if value:
                    raise UserError(
                        f"Cannot archive account {acc.account_code} with non-zero {label} "
                        f"{value:.2f} BDT (COA-04)"
                    )
            acc.write({"active": False})


class FixChartLoader(models.Model):
    """Loader and Reconciler for Bangladesh Chart of Accounts (MD-035)."""

    _name = "fix.chart.loader"
    _description = "Chart of Accounts Loader"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    _LOADER_GUARDED = frozenset(
        {
            "state",
            "loaded_at",
            "account_count",
            "postable_count",
            "control_count",
            "checksum",
            "reconciled_at",
            "recon_discrepancy",
            "unmapped_ledger_count",
            "unmapped_ledger_balance",
        }
    )

    def _fix_guarded_fields(self) -> set:
        # the load and reconcile results are measured, never typed
        return super()._fix_guarded_fields() | self._LOADER_GUARDED

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
        tracking=True,
    )
    name = fields.Char(compute="_compute_name")
    currency_id = fields.Many2one(related="company_id.currency_id")
    linked_count = fields.Integer(
        string="Linked to Ledger",
        readonly=True,
        help="Statutory accounts linked to an Odoo account",
    )
    reconciled_at = fields.Datetime(string="Last Reconciliation", readonly=True)
    recon_discrepancy = fields.Monetary(
        string="Equation Discrepancy",
        readonly=True,
        help="Assets - (liabilities + equity + income - expense) over the linked ledger balances",
    )
    unmapped_ledger_count = fields.Integer(
        string="Unmapped Ledger Accounts",
        readonly=True,
        help="Odoo accounts with a posted balance that no statutory account is linked to",
    )
    unmapped_ledger_balance = fields.Monetary(
        string="Unmapped Ledger Balance (absolute)", readonly=True
    )

    @api.depends("company_id")
    def _compute_name(self):
        for loader in self:
            loader.name = "MD-035 CoA - %s" % (loader.company_id.name or "")

    def action_load_from_csv(self, csv_text: str | None = None) -> dict:
        """Load Chart of Accounts from CSV text or file path."""
        self.ensure_one()
        # The statutory master file is governed content (AF-09): an Accounting
        # Administrator's reload of it may move control flags. A custom CSV
        # never does; that change is a fix.chart.control.change (M19-8).
        master_reload = not csv_text and (
            self.env.su or self.env.user.has_group("account.group_account_manager")
        )
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
        try:
            result = coa_logic.validate_coa_rules(records)
        except coa_logic.CoaValidationError as e:
            # nothing is written: a chart that breaks MD-035 loads not at all
            raise UserError(str(e)) from e

        # active_test=False: an account archived under COA-04 still owns its
        # code (codes are never reused, MD-035 §3) — a reload must update it,
        # not collide with it on the (company, code) unique key.
        acc_model = self.env["fix.chart.account"].with_context(active_test=False)
        for rec in records:
            existing = acc_model.search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("account_code", "=", rec.account_code),
                ],
                limit=1,
            )

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
                if master_reload:
                    from .fix_gl_posting_control import control_change_context

                    existing = existing.with_context(**control_change_context())
                existing.write(vals)
            else:
                acc_model.create(vals)

        self._guarded().write(
            {
                "state": "loaded",
                "loaded_at": fields.Datetime.now(),
                "account_count": result["account_count"],
                "postable_count": result["postable_count"],
                "control_count": result["control_count"],
                "checksum": sha256,
            }
        )

        publish(
            self.env,
            "coa.loaded",
            "fix.chart.loader",
            self.id,
            {
                "company_id": self.company_id.id,
                "account_count": result["account_count"],
                "postable_count": result["postable_count"],
                "sha256": sha256,
            },
        )
        return {
            "status": "loaded",
            "account_count": result["account_count"],
            "postable_count": result["postable_count"],
            "sha256": sha256,
        }

    def action_reconcile_chart(self) -> dict:
        """Reconcile the statutory chart with the POSTED ledger (MD-035 s.6).

        Balances are the posted ledger balances of the Odoo accounts each
        statutory account is linked to (never a typed-in figure). The chart
        is reconciled only when (a) the accounting equation holds over those
        balances and (b) no posted ledger balance sits on an Odoo account the
        chart does not cover. Otherwise it stays loaded and the result says
        why."""
        self.ensure_one()
        accounts = self.env["fix.chart.account"].search([("company_id", "=", self.company_id.id)])
        if not accounts:
            raise UserError("No accounts loaded for company")

        ledger = accounts._ledger_balances()
        acc_records = []
        balances = {}
        for a in accounts:
            # Monetary is a float column: str() keeps the 2dp value exact
            bal_dec = Decimal(str(ledger.get(a.id, 0.0)))
            acc_records.append(
                coa_logic.AccountRecord(
                    account_code=a.account_code,
                    entity_code="EN-01",
                    account_name=a.name,
                    account_type=a.account_type,
                    account_subtype=a.account_subtype or "",
                    is_postable=a.is_postable,
                    is_control_account=a.is_control_account,
                    control_subledger=a.control_subledger or None,
                    requires_dimension=_split_dimensions(a.requires_dimension),
                    statutory_group=a.statutory_group,
                    active=a.active,
                    balance=bal_dec,
                )
            )
            balances[a.account_code] = bal_dec

        recon_res = coa_logic.reconcile_trial_balance(balances, acc_records)

        # Posted balances on Odoo accounts outside the statutory chart.
        linked_ids = accounts.mapped("odoo_account_id").ids
        groups = (
            self.env["account.move.line"]
            .sudo()
            ._read_group(
                [
                    ("company_id", "=", self.company_id.id),
                    ("parent_state", "=", "posted"),
                    ("account_id", "not in", linked_ids),
                ],
                ["account_id"],
                ["balance:sum"],
            )
        )
        unmapped = [(account, balance) for account, balance in groups if round(balance or 0.0, 2)]
        recon_res["linked_accounts"] = len(linked_ids)
        recon_res["unmapped_ledger_accounts"] = len(unmapped)
        recon_res["unmapped_ledger_balance"] = round(sum(abs(b) for _a, b in unmapped), 2)
        recon_res["unmapped_codes"] = sorted(a.code for a, _b in unmapped)[:20]
        recon_res["reconciled"] = bool(recon_res["reconciled"] and not unmapped)

        vals = {
            "reconciled_at": fields.Datetime.now(),
            "linked_count": len(linked_ids),
            "recon_discrepancy": recon_res["discrepancy"],
            "unmapped_ledger_count": len(unmapped),
            "unmapped_ledger_balance": recon_res["unmapped_ledger_balance"],
        }
        # An unbalanced or incomplete chart never earns the reconciled state.
        if recon_res["reconciled"]:
            vals["state"] = "reconciled"
        elif self.state == "reconciled":
            vals["state"] = "loaded"
        self._guarded().write(vals)
        return recon_res

    def action_link_odoo_accounts(self) -> dict:
        """COA unification (FR-FIN-002): populate ``odoo_account_id`` on the
        statutory chart from the ODOO_CHART_MAPPING pairs that exist in the
        company's Odoo chart. The link is what turns on the MD-035 posting
        rules (FR-FIN-011) and the live ledger balance on the CoA screen —
        a statutory account is only ever linked to an account that EXISTS in
        the company chart, never invented."""
        self.ensure_one()
        chart_model = self.env["fix.chart.account"].with_context(active_test=False)
        Account = self.env["account.account"].with_company(self.company_id)
        linked, missing = 0, []
        for odoo_code, statutory_code in ODOO_CHART_MAPPING.items():
            odoo_account = Account.search(
                [
                    *Account._check_company_domain(self.company_id),
                    ("code", "=", odoo_code),
                ],
                limit=1,
            )
            if not odoo_account:
                missing.append(odoo_code)
                continue
            statutory = chart_model.search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("account_code", "=", statutory_code),
                ],
                limit=1,
            )
            if not statutory:
                missing.append(statutory_code)
                continue
            statutory.write({"odoo_account_id": odoo_account.id})
            linked += 1
        self._guarded().write(
            {
                "linked_count": chart_model.search_count(
                    [("company_id", "=", self.company_id.id), ("odoo_account_id", "!=", False)]
                )
            }
        )
        _logger.info(
            "COA unification: %d statutory accounts linked for %s (unmatched: %s)",
            linked,
            self.company_id.name,
            missing or "none",
        )
        return {"status": "linked", "linked": linked, "unmatched": missing}
