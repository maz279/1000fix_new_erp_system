# fix.consolidation — Multi-Company Financial Consolidation (CD-M65-03).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixConsolidationBook(models.Model):
    """Group financial consolidation across multiple legal entities."""

    _name = "fix.consolidation.book"
    _description = "Multi-Entity Consolidation Book"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "fiscal_year desc, period_month desc, id desc"

    _code_unique = models.Constraint("UNIQUE (code)", "Consolidation book code must be unique")

    name = fields.Char(string="Book Name", required=True, tracking=True)
    code = fields.Char(
        string="Code", required=True, size=20, tracking=True, help="e.g. CONS-2026-M06"
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    currency_id = fields.Many2one(
        "res.currency",
        string="Consolidation Currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False),
    )
    parent_entity_id = fields.Many2one(
        "fix.entity", string="Parent Entity", required=True, tracking=True
    )
    entity_ids = fields.Many2many(
        "fix.entity",
        "fix_cons_book_entity_rel",
        "book_id",
        "entity_id",
        string="Participating Entities",
        required=True,
    )
    fiscal_year = fields.Char(string="Fiscal Year", required=True, default="2026-2027")
    period_month = fields.Integer(string="Period Month", required=True, default=6)
    consolidation_date = fields.Date(string="Consolidation Date", default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("consolidated", "Consolidated"),
            ("eliminated", "Eliminations Posted"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    line_ids = fields.One2many("fix.consolidation.line", "book_id", string="Consolidated Lines")
    elimination_ids = fields.One2many(
        "fix.elimination.entry", "book_id", string="Elimination Entries"
    )

    total_subsidiary_revenue = fields.Monetary(
        string="Total Revenue (Pre-Elimination)", compute="_compute_totals", store=True
    )
    total_subsidiary_expense = fields.Monetary(
        string="Total Expense (Pre-Elimination)", compute="_compute_totals", store=True
    )
    total_eliminations = fields.Monetary(
        string="Total Inter-Company Eliminations", compute="_compute_totals", store=True
    )
    consolidated_revenue = fields.Monetary(
        string="Consolidated Revenue (Post-Elimination)",
        compute="_compute_totals",
        store=True,
        help="Member-entity revenue less inter-company revenue eliminated.",
    )
    consolidated_expense = fields.Monetary(
        string="Consolidated Expense (Post-Elimination)",
        compute="_compute_totals",
        store=True,
        help="Member-entity expense less the matching inter-company expense eliminated.",
    )
    net_consolidated_profit = fields.Monetary(
        string="Net Consolidated Profit", compute="_compute_totals", store=True
    )

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if rec.code and not rec.code.isupper():
                raise ValidationError("Consolidation book code must be uppercase.")

    @api.depends("line_ids.consolidated_amount", "elimination_ids.amount")
    def _compute_totals(self):
        for rec in self:
            rev = sum(
                line.consolidated_amount for line in rec.line_ids if line.account_type == "revenue"
            )
            exp = sum(
                line.consolidated_amount for line in rec.line_ids if line.account_type == "expense"
            )
            elim = sum(e.amount for e in rec.elimination_ids)
            # Only P&L eliminations (IC sale/recharge, IC interest, IC fees)
            # touch revenue and expense; receivable/payable eliminations are
            # balance-sheet only.
            pl_elim = sum(
                e.amount
                for e in rec.elimination_ids
                if e.elimination_type in self.PL_ELIMINATION_TYPES
            )
            rec.total_subsidiary_revenue = rev
            rec.total_subsidiary_expense = exp
            rec.total_eliminations = elim
            # An inter-company transaction is revenue in one entity and the
            # mirror expense in the other: eliminating it removes it from BOTH
            # sides, so it never changes consolidated profit. (The previous
            # formula `(rev - exp) - elim` understated group profit by every
            # eliminated amount.)
            rec.consolidated_revenue = rev - pl_elim
            rec.consolidated_expense = exp - pl_elim
            rec.net_consolidated_profit = rec.consolidated_revenue - rec.consolidated_expense

    # Account types rolled up into the two consolidation line types.
    REVENUE_ACCOUNT_TYPES = ("income", "income_other")
    EXPENSE_ACCOUNT_TYPES = ("expense", "cost_of_revenue", "depreciation", "amortization")
    # Elimination types that offset an inter-company revenue against the
    # counterparty's inter-company expense.
    PL_ELIMINATION_TYPES = ("revenue_expense", "intercompany_loan", "management_fee")

    def action_run_consolidation(self):
        """Aggregate REAL posted ledger balances per entity (R01 re-audit fix).

        The previous implementation wrote two constant lines per entity
        (1,000,000 revenue / 650,000 expense) - a fabrication. This version
        reads account.move.line balances (posted entries only, per entity's
        company), rolls them up by account, and converts at the real rate.
        Revenue/expense are P&L (flow) accounts: they are summed from the start
        of the entity company's fiscal year containing the consolidation date
        up to that date (year-to-date), not cumulatively since inception. An entity whose company has no posted
        ledger contributes nothing; if NO entity contributes, the run refuses
        rather than invent figures.
        """
        self.ensure_one()
        if not self.entity_ids:
            raise ValidationError("Please select at least one participating entity.")
        self.line_ids.unlink()

        as_of = self.consolidation_date or fields.Date.context_today(self)
        lines = []
        for ent in self.entity_ids:
            # Real currency rate at the consolidation date (was a 1.0 placeholder).
            rate = 1.0
            if ent.currency_id and self.currency_id and ent.currency_id != self.currency_id:
                rate = ent.currency_id._get_conversion_rate(
                    ent.currency_id,
                    self.currency_id,
                    self.company_id,
                    as_of,
                )

            MoveLine = self.env["account.move.line"]
            # P&L period start: the fiscal year of the entity's company that
            # contains the consolidation date (honours the company's fiscal
            # year-end setting, e.g. 30 June for Bangladesh).
            period_start = ent.company_id.compute_fiscalyear_dates(as_of)["date_from"]
            domain = [
                ("company_id", "=", ent.company_id.id),
                ("parent_state", "=", "posted"),
                ("date", ">=", period_start),
                ("date", "<=", as_of),
                (
                    "account_id.account_type",
                    "in",
                    list(self.REVENUE_ACCOUNT_TYPES + self.EXPENSE_ACCOUNT_TYPES),
                ),
                (
                    "display_type",
                    "in",
                    ("product", "tax", "payment_term", "line_section", "line_note"),
                ),
            ]
            groups = MoveLine.read_group(domain, ["balance:sum"], ["account_id"], lazy=False)
            for g in groups:
                account = self.env["account.account"].browse(g["account_id"][0])
                balance = g.get("balance") or 0.0
                if account.account_type in self.REVENUE_ACCOUNT_TYPES:
                    account_type, amount = "revenue", -balance  # income carries credit balances
                else:
                    account_type, amount = "expense", balance
                if not amount:
                    continue  # zero-balance accounts add noise, not information
                lines.append(
                    (
                        0,
                        0,
                        {
                            "entity_id": ent.id,
                            "account_code": account.code or "",
                            "account_name": account.name or "",
                            "account_type": account_type,
                            "original_amount": round(amount, 2),
                            "original_currency_id": ent.currency_id.id
                            if ent.currency_id
                            else self.currency_id.id,
                            "exchange_rate": rate,
                            "consolidated_amount": round(amount * rate, 2),
                        },
                    )
                )

        if not lines:
            raise ValidationError(
                "No posted revenue/expense entries found for the selected entities "
                f"in the fiscal year up to {as_of}. A consolidation without source ledger data would be "
                "fabricated - post journal entries for the entities first."
            )

        self.write(
            {
                "line_ids": lines,
                "state": "consolidated",
            }
        )
        return True

    def action_generate_eliminations(self):
        """Discover and post inter-company transaction eliminations."""
        self.ensure_one()
        self.elimination_ids.unlink()

        # Find inter-company transactions between participating entities
        ent_ids = self.entity_ids.ids
        ic_txns = self.env["fix.intercompany.transaction"].search(
            [
                ("source_entity_id", "in", ent_ids),
                ("target_entity_id", "in", ent_ids),
                ("state", "=", "matched"),
            ]
        )

        elim_vals = []
        for txn in ic_txns:
            elim_vals.append(
                (
                    0,
                    0,
                    {
                        "name": f"Eliminate IC Txn {txn.reference}",
                        "elimination_type": "revenue_expense",
                        "from_entity_id": txn.source_entity_id.id,
                        "to_entity_id": txn.target_entity_id.id,
                        "amount": txn.amount,
                        "is_balanced": True,
                        "reference": txn.reference,
                    },
                )
            )

        # No matched inter-company transactions -> no eliminations. (A former
        # fallback here invented a 50,000 "shared management fee" elimination
        # with no source transaction; eliminations must come only from real,
        # matched inter-company transactions.)

        self.write(
            {
                "elimination_ids": elim_vals,
                "state": "eliminated",
            }
        )
        return True

    def action_close(self):
        self.ensure_one()
        self.write({"state": "closed"})
        return True


class FixConsolidationLine(models.Model):
    """Consolidated financial statement line per entity."""

    _name = "fix.consolidation.line"
    _description = "Consolidated Financial Line"

    book_id = fields.Many2one("fix.consolidation.book", required=True, ondelete="cascade")
    entity_id = fields.Many2one("fix.entity", string="Member Entity", required=True)
    account_code = fields.Char(string="Account Code", required=True)
    account_name = fields.Char(string="Account Name", required=True)
    account_type = fields.Selection(
        [
            ("revenue", "Revenue"),
            ("expense", "Expense"),
            ("asset", "Asset"),
            ("liability", "Liability"),
            ("equity", "Equity"),
        ],
        string="Account Type",
        required=True,
    )
    original_amount = fields.Float(string="Entity Ledger Amount", required=True)
    original_currency_id = fields.Many2one("res.currency", string="Original Currency")
    exchange_rate = fields.Float(string="Exchange Rate", default=1.0)
    consolidated_amount = fields.Monetary(
        string="Consolidated Amount (BDT)", compute="_compute_consolidated_amount", store=True
    )
    currency_id = fields.Many2one(related="book_id.currency_id", store=True)

    @api.depends("original_amount", "exchange_rate")
    def _compute_consolidated_amount(self):
        for rec in self:
            rec.consolidated_amount = rec.original_amount * (rec.exchange_rate or 1.0)


class FixEliminationEntry(models.Model):
    """Elimination entry offsetting inter-company revenues, expenses or balances."""

    _name = "fix.elimination.entry"
    _description = "Inter-Company Elimination Entry"

    book_id = fields.Many2one("fix.consolidation.book", required=True, ondelete="cascade")
    name = fields.Char(string="Elimination Description", required=True)
    elimination_type = fields.Selection(
        [
            ("revenue_expense", "Inter-Company Revenue & Expense"),
            ("receivable_payable", "Inter-Company Receivable & Payable"),
            ("intercompany_loan", "Inter-Company Loan / Interest"),
            ("management_fee", "Shared Management Fee"),
        ],
        string="Elimination Type",
        required=True,
        default="revenue_expense",
    )
    from_entity_id = fields.Many2one("fix.entity", string="Originating Entity", required=True)
    to_entity_id = fields.Many2one("fix.entity", string="Counterparty Entity", required=True)
    amount = fields.Monetary(string="Elimination Amount", required=True)
    currency_id = fields.Many2one(related="book_id.currency_id", store=True)
    is_balanced = fields.Boolean(string="Balanced", default=True)
    reference = fields.Char(string="Source Transaction Reference")
