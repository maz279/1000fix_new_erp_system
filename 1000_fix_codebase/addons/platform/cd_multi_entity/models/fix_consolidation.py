# fix.consolidation — Multi-Company Financial Consolidation (CD-M65-03).
#
# Every figure comes from POSTED ledger lines of the member entities'
# companies and from matched inter-company transactions; nothing is invented
# (a former fallback minted a 50,000 "shared management fee" elimination with
# no source transaction — removed in bfe3855f and must stay removed).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


def _bd_fiscal_year_label(day):
    """'2026-2027' for any date in the July-June fiscal year starting 2026."""
    start = day.year if day.month >= 7 else day.year - 1
    return "%d-%d" % (start, start + 1)


class FixConsolidationBook(models.Model):
    """Group financial consolidation across multiple legal entities."""

    _name = "fix.consolidation.book"
    _description = "Multi-Entity Consolidation Book"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "consolidation_date desc, id desc"

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
    consolidation_date = fields.Date(
        string="Consolidation Date",
        required=True,
        default=fields.Date.context_today,
        help="Balance-sheet cut-off; P&L is the fiscal year to date up to this date.",
    )
    fiscal_year = fields.Char(
        string="Fiscal Year", compute="_compute_period", store=True, help="July-June"
    )
    period_month = fields.Integer(string="Period Month", compute="_compute_period", store=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("consolidated", "Consolidated"),
            ("eliminated", "Eliminations Applied"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    run_by_id = fields.Many2one("res.users", string="Consolidated By", readonly=True, copy=False)
    run_at = fields.Datetime(string="Consolidated At", readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)

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
    total_assets = fields.Monetary(
        string="Total Assets (Pre-Elimination)", compute="_compute_totals", store=True
    )
    total_liabilities = fields.Monetary(
        string="Total Liabilities (Pre-Elimination)", compute="_compute_totals", store=True
    )
    consolidated_assets = fields.Monetary(
        string="Consolidated Assets",
        compute="_compute_totals",
        store=True,
        help="Member-entity assets less open inter-company receivables eliminated.",
    )
    consolidated_liabilities = fields.Monetary(
        string="Consolidated Liabilities",
        compute="_compute_totals",
        store=True,
        help="Member-entity liabilities less the matching inter-company payables eliminated.",
    )

    # Account types rolled up into the consolidation line types.
    REVENUE_ACCOUNT_TYPES = ("income", "income_other")
    EXPENSE_ACCOUNT_TYPES = (
        "expense",
        "expense_other",
        "expense_depreciation",
        "expense_direct_cost",
    )
    ASSET_ACCOUNT_TYPES = (
        "asset_receivable",
        "asset_cash",
        "asset_current",
        "asset_non_current",
        "asset_prepayments",
        "asset_fixed",
    )
    LIABILITY_ACCOUNT_TYPES = (
        "liability_payable",
        "liability_credit_card",
        "liability_current",
        "liability_non_current",
    )
    EQUITY_ACCOUNT_TYPES = ("equity", "equity_unaffected")
    # Elimination types that offset an inter-company revenue against the
    # counterparty's inter-company expense.
    PL_ELIMINATION_TYPES = ("revenue_expense", "intercompany_loan", "management_fee")
    # rule.transaction_type -> P&L elimination type
    ELIMINATION_TYPE_BY_CATEGORY = {
        "sale_purchase": "revenue_expense",
        "shared_service": "revenue_expense",
        "management_fee": "management_fee",
        "loan_interest": "intercompany_loan",
    }

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if rec.code and not rec.code.isupper():
                raise ValidationError("Consolidation book code must be uppercase.")

    @api.depends("consolidation_date")
    def _compute_period(self):
        for rec in self:
            day = rec.consolidation_date
            rec.fiscal_year = _bd_fiscal_year_label(day) if day else False
            rec.period_month = day.month if day else 0

    @api.depends(
        "line_ids.consolidated_amount",
        "line_ids.account_type",
        "elimination_ids.amount",
        "elimination_ids.elimination_type",
    )
    def _compute_totals(self):
        for rec in self:

            def total(kind, rec=rec):
                return sum(
                    line.consolidated_amount for line in rec.line_ids if line.account_type == kind
                )

            rev, exp = total("revenue"), total("expense")
            elim = sum(e.amount for e in rec.elimination_ids)
            # Only P&L eliminations (IC sale/recharge, IC interest, IC fees)
            # touch revenue and expense; receivable/payable eliminations are
            # balance-sheet only.
            pl_elim = sum(
                e.amount
                for e in rec.elimination_ids
                if e.elimination_type in self.PL_ELIMINATION_TYPES
            )
            bs_elim = sum(
                e.amount for e in rec.elimination_ids if e.elimination_type == "receivable_payable"
            )
            rec.total_subsidiary_revenue = rev
            rec.total_subsidiary_expense = exp
            rec.total_eliminations = elim
            # An inter-company transaction is revenue in one entity and the
            # mirror expense in the other: eliminating it removes it from BOTH
            # sides, so it never changes consolidated profit.
            rec.consolidated_revenue = rev - pl_elim
            rec.consolidated_expense = exp - pl_elim
            rec.net_consolidated_profit = rec.consolidated_revenue - rec.consolidated_expense
            assets, liabilities = total("asset"), total("liability")
            rec.total_assets = assets
            rec.total_liabilities = liabilities
            rec.consolidated_assets = assets - bs_elim
            rec.consolidated_liabilities = liabilities - bs_elim

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _line_type(self, account_type):
        if account_type in self.REVENUE_ACCOUNT_TYPES:
            return "revenue", -1  # income carries credit balances
        if account_type in self.EXPENSE_ACCOUNT_TYPES:
            return "expense", 1
        if account_type in self.ASSET_ACCOUNT_TYPES:
            return "asset", 1
        if account_type in self.LIABILITY_ACCOUNT_TYPES:
            return "liability", -1
        if account_type in self.EQUITY_ACCOUNT_TYPES:
            return "equity", -1
        return None, 0

    def _member_companies(self):
        companies = self.entity_ids.mapped("company_id")
        if not self.env.su:
            missing = companies - self.env.user.company_ids
            if missing:
                raise UserError(
                    "You need access to every member company to consolidate (missing: %s)."
                    % ", ".join(missing.mapped("name"))
                )
        return companies

    def _rate(self, entity, day):
        if entity.currency_id and self.currency_id and entity.currency_id != self.currency_id:
            return entity.currency_id._get_conversion_rate(
                entity.currency_id, self.currency_id, self.company_id, day
            )
        return 1.0

    # ------------------------------------------------------------------
    # workflow
    # ------------------------------------------------------------------
    def action_run_consolidation(self):
        """Aggregate REAL posted ledger balances per entity.

        P&L accounts are summed from the start of the entity company's fiscal
        year containing the consolidation date up to that date (year to
        date); balance-sheet accounts are cumulative up to that date. Each
        entity is translated at the real rate on the consolidation date. An
        entity whose company has no posted ledger contributes nothing; if NO
        entity contributes, the run refuses rather than invent figures."""
        self.ensure_one()
        if not self.entity_ids:
            raise ValidationError("Please select at least one participating entity.")
        if self.state == "closed":
            raise UserError("A closed consolidation book cannot be re-run.")
        companies = self._member_companies()
        as_of = self.consolidation_date or fields.Date.context_today(self)
        MoveLine = self.env["account.move.line"].with_context(allowed_company_ids=companies.ids)
        pl_types = list(self.REVENUE_ACCOUNT_TYPES + self.EXPENSE_ACCOUNT_TYPES)
        bs_types = list(
            self.ASSET_ACCOUNT_TYPES + self.LIABILITY_ACCOUNT_TYPES + self.EQUITY_ACCOUNT_TYPES
        )

        lines = []
        for ent in self.entity_ids:
            rate = self._rate(ent, as_of)
            period_start = ent.company_id.compute_fiscalyear_dates(as_of)["date_from"]
            base = [
                ("company_id", "=", ent.company_id.id),
                ("parent_state", "=", "posted"),
                ("date", "<=", as_of),
            ]
            groups = MoveLine._read_group(
                [*base, ("date", ">=", period_start), ("account_id.account_type", "in", pl_types)],
                ["account_id"],
                ["balance:sum"],
            ) + MoveLine._read_group(
                [*base, ("account_id.account_type", "in", bs_types)],
                ["account_id"],
                ["balance:sum"],
            )
            for account, balance in groups:
                line_type, sign = self._line_type(account.account_type)
                amount = round((balance or 0.0) * sign, 2)
                if not line_type or not amount:
                    continue  # zero-balance accounts add noise, not information
                lines.append(
                    (
                        0,
                        0,
                        {
                            "entity_id": ent.id,
                            "account_code": account.code or "",
                            "account_name": account.name or "",
                            "account_type": line_type,
                            "original_amount": amount,
                            "original_currency_id": ent.currency_id.id
                            if ent.currency_id
                            else self.currency_id.id,
                            "exchange_rate": rate,
                        },
                    )
                )

        if not lines:
            raise ValidationError(
                "No posted ledger entries found for the selected entities "
                f"up to {as_of}. A consolidation without source ledger data would be "
                "fabricated - post journal entries for the entities first."
            )
        self.line_ids.unlink()
        self.elimination_ids.unlink()
        self.write(
            {
                "line_ids": lines,
                "state": "consolidated",
                "run_by_id": self.env.user.id,
                "run_at": fields.Datetime.now(),
            }
        )
        return True

    def action_generate_eliminations(self):
        """Eliminate inter-company activity between member entities, from
        matched (or settled) inter-company transactions only:

        - P&L: transactions dated in the fiscal year to date are removed
          from revenue AND expense (group profit is unchanged);
        - balance sheet: transactions still open (matched, not settled) at
          the consolidation date have their due-from/due-to removed.

        Inter-branch transactions net inside one entity's own books and are
        never eliminated here. No matched transaction -> no elimination."""
        self.ensure_one()
        if self.state not in ("consolidated", "eliminated"):
            raise UserError("Run the consolidation before generating eliminations.")
        as_of = self.consolidation_date
        period_start = self.parent_entity_id.company_id.compute_fiscalyear_dates(as_of)["date_from"]
        ent_ids = self.entity_ids.ids
        ic_txns = self.env["fix.intercompany.transaction"].search(
            [
                ("scope", "=", "intercompany"),
                ("source_entity_id", "in", ent_ids),
                ("target_entity_id", "in", ent_ids),
                ("state", "in", ("matched", "settled")),
                ("target_move_id", "!=", False),  # posted through the mirror, not typed
                ("transaction_date", "<=", as_of),
            ]
        )

        elim_vals = []
        for txn in ic_txns:
            common = {
                "from_entity_id": txn.source_entity_id.id,
                "to_entity_id": txn.target_entity_id.id,
                "is_balanced": True,
                "reference": txn.reference,
                "transaction_id": txn.id,
            }
            if txn.transaction_date >= period_start:
                category = txn.rule_id.transaction_type or "shared_service"
                elim_vals.append(
                    (
                        0,
                        0,
                        {
                            **common,
                            "name": f"Eliminate IC Txn {txn.reference}",
                            "elimination_type": self.ELIMINATION_TYPE_BY_CATEGORY[category],
                            "amount": txn.currency_id._convert(
                                txn.amount, self.currency_id, self.company_id, txn.transaction_date
                            ),
                        },
                    )
                )
            if txn.state == "matched":
                elim_vals.append(
                    (
                        0,
                        0,
                        {
                            **common,
                            "name": f"Eliminate IC balance {txn.reference}",
                            "elimination_type": "receivable_payable",
                            "amount": txn.currency_id._convert(
                                txn.amount, self.currency_id, self.company_id, as_of
                            ),
                        },
                    )
                )

        self.elimination_ids.unlink()
        self.write({"elimination_ids": elim_vals, "state": "eliminated"})
        return True

    def action_close(self):
        """Close the book — an approval: accounting manager only, and never
        the user who ran the consolidation (segregation of duties)."""
        self.ensure_one()
        if self.state != "eliminated":
            raise UserError("Generate (or review) the eliminations before closing the book.")
        if not self.env.su:
            if not self.env.user.has_group("account.group_account_manager"):
                raise UserError("Only an accounting manager can close a consolidation book.")
            if self.run_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: %s ran this consolidation and cannot also "
                    "close it." % self.env.user.name
                )
        self.write({"state": "closed", "closed_by_id": self.env.user.id})
        return True


class FixConsolidationLine(models.Model):
    """Consolidated financial statement line per entity."""

    _name = "fix.consolidation.line"
    _description = "Consolidated Financial Line"

    book_id = fields.Many2one("fix.consolidation.book", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="book_id.company_id", store=True)
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
            rec.consolidated_amount = round(rec.original_amount * (rec.exchange_rate or 1.0), 2)


class FixEliminationEntry(models.Model):
    """Elimination entry offsetting inter-company revenues, expenses or balances."""

    _name = "fix.elimination.entry"
    _description = "Inter-Company Elimination Entry"
    _order = "book_id desc, id"

    book_id = fields.Many2one("fix.consolidation.book", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="book_id.company_id", store=True)
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
    transaction_id = fields.Many2one(
        "fix.intercompany.transaction", string="Source Transaction", ondelete="restrict"
    )
