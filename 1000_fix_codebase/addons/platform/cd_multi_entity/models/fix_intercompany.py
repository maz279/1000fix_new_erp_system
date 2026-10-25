# fix.intercompany — Inter-Company / Inter-Branch rules, real mirror postings
# and ledger-checked matching (CD-M65-03, M19 "Group & Inter-Branch").
#
# Nothing here invents an amount or a document number. A transaction is
# recorded by a user; "Generate Mirror" posts the two real journal entries
# (the originating side's due-from / recharge income and the counterparty's
# expense / due-to) on the accounts configured on the rule; "Match" compares
# the two POSTED due lines against the transaction; "Settle" only succeeds
# once both due lines are reconciled in the ledger. Missing configuration
# fails closed with a UserError.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

SCOPES = [
    ("intercompany", "Inter-Company (between legal entities)"),
    ("interbranch", "Inter-Branch (within one legal entity)"),
]


def _account_in_company(account, company) -> bool:
    """Odoo 19 accounts are shared across companies through company_ids."""
    return bool(account) and company in account.company_ids


class FixIntercompanyRule(models.Model):
    """How one entity (or branch) charges another: the transaction category,
    the accounts both sides post on, and the transfer-pricing evidence."""

    _name = "fix.intercompany.rule"
    _description = "Inter-Company Transaction Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    _code_unique = models.Constraint("UNIQUE (code)", "Intercompany rule code must be unique")

    name = fields.Char(string="Rule Name", required=True, tracking=True)
    code = fields.Char(string="Rule Code", required=True, size=20, tracking=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    scope = fields.Selection(
        SCOPES, string="Scope", required=True, default="intercompany", tracking=True
    )
    source_entity_id = fields.Many2one(
        "fix.entity", string="Selling / Supplying Entity", required=True, tracking=True
    )
    target_entity_id = fields.Many2one(
        "fix.entity", string="Purchasing / Receiving Entity", required=True, tracking=True
    )
    source_branch_id = fields.Many2one(
        "fix.branch", string="Supplying Branch", help="Inter-branch rules only"
    )
    target_branch_id = fields.Many2one(
        "fix.branch", string="Receiving Branch", help="Inter-branch rules only"
    )
    transaction_type = fields.Selection(
        [
            ("sale_purchase", "Goods Sale / Purchase"),
            ("shared_service", "Shared IT / Back-Office Service"),
            ("management_fee", "Management / Advisory Fee"),
            ("loan_interest", "Inter-Company Loan / Financing"),
        ],
        string="Transaction Category",
        required=True,
        default="shared_service",
        tracking=True,
    )

    # --- posting configuration (fails closed when missing) -----------------
    source_journal_id = fields.Many2one(
        "account.journal",
        string="Supplying Side Journal",
        help="Journal of the supplying entity's company (inter-branch: the entity's journal)",
    )
    source_receivable_account_id = fields.Many2one(
        "account.account",
        string="Due-From Account",
        help="Inter-company / inter-branch receivable booked by the supplying side",
    )
    source_income_account_id = fields.Many2one(
        "account.account",
        string="Recharge Income Account",
        help="Income (or cost-recovery) account credited by the supplying side",
    )
    target_journal_id = fields.Many2one(
        "account.journal",
        string="Receiving Side Journal",
        help="Journal of the receiving entity's company (not used for inter-branch rules)",
    )
    target_expense_account_id = fields.Many2one(
        "account.account",
        string="Recharge Expense Account",
        help="Expense (or asset) account debited by the receiving side",
    )
    target_payable_account_id = fields.Many2one(
        "account.account",
        string="Due-To Account",
        help="Inter-company / inter-branch payable booked by the receiving side",
    )

    auto_mirror = fields.Boolean(
        string="Auto-Mirror Generation",
        default=True,
        help="Post the counterparty side in the same step as the originating side",
    )
    markup_percent = fields.Float(
        string="Transfer Pricing Markup (%)",
        default=0.0,
        help="Agreed arm's length markup, from the transfer-pricing study on file. "
        "No default is assumed: verify the rate with the company's tax adviser.",
    )
    transfer_pricing_compliant = fields.Boolean(
        string="Transfer Pricing Documentation on File",
        default=False,
        tracking=True,
        help="Tick only when the arm's length documentation referenced below is held "
        "(verify the statutory requirement with the company's tax adviser).",
    )
    documentation_ref = fields.Char(string="TP Documentation Ref", tracking=True)
    active = fields.Boolean(default=True)

    @api.constrains("scope", "source_entity_id", "target_entity_id")
    def _check_different_entities(self):
        for rec in self:
            if not (rec.source_entity_id and rec.target_entity_id):
                continue
            same = rec.source_entity_id == rec.target_entity_id
            if rec.scope == "intercompany" and same:
                raise ValidationError("Source and target entities must be distinct legal entities.")
            if rec.scope == "interbranch" and not same:
                raise ValidationError(
                    "An inter-branch rule moves charges between branches of ONE legal entity: "
                    "the source and target entity must be the same."
                )

    @api.constrains("scope", "source_branch_id", "target_branch_id", "source_entity_id")
    def _check_branches(self):
        for rec in self:
            if rec.scope != "interbranch" or rec.source_entity_id != rec.target_entity_id:
                continue  # the entity rule above reports a cross-entity rule
            if not (rec.source_branch_id and rec.target_branch_id):
                raise ValidationError(
                    "An inter-branch rule needs a supplying and a receiving branch."
                )
            if rec.source_branch_id == rec.target_branch_id:
                raise ValidationError("The supplying and receiving branch must differ.")
            for branch in rec.source_branch_id | rec.target_branch_id:
                if branch.entity_id != rec.source_entity_id:
                    raise ValidationError(
                        "Branch %s does not belong to entity %s."
                        % (branch.name, rec.source_entity_id.code)
                    )

    def _posting_config_errors(self) -> list[str]:
        """Every missing or mis-companied posting setting, in words."""
        self.ensure_one()
        errors = []
        src_company = self.source_entity_id.company_id
        tgt_company = self.target_entity_id.company_id
        checks = [
            ("Supplying Side Journal", self.source_journal_id, src_company, "journal"),
            ("Due-From Account", self.source_receivable_account_id, src_company, "account"),
            ("Recharge Income Account", self.source_income_account_id, src_company, "account"),
            ("Recharge Expense Account", self.target_expense_account_id, tgt_company, "account"),
            ("Due-To Account", self.target_payable_account_id, tgt_company, "account"),
        ]
        if self.scope == "intercompany":
            checks.append(
                ("Receiving Side Journal", self.target_journal_id, tgt_company, "journal")
            )
        for label, value, company, kind in checks:
            if not value:
                errors.append("%s is not configured" % label)
            elif kind == "journal" and value.company_id != company:
                errors.append("%s must be a journal of %s" % (label, company.name))
            elif kind == "account" and not _account_in_company(value, company):
                errors.append("%s must be an account of %s" % (label, company.name))
        return errors


class FixIntercompanyTransaction(models.Model):
    """One inter-company / inter-branch charge, its two real postings and
    their match — the source of due-to/due-from balances and consolidation
    eliminations."""

    _name = "fix.intercompany.transaction"
    _description = "Inter-Company Transaction"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "transaction_date desc, id desc"

    _ref_unique = models.Constraint(
        "UNIQUE (reference)", "Intercompany transaction reference must be unique"
    )
    _amount_positive = models.Constraint(
        "CHECK (amount > 0)", "The transaction amount must be positive"
    )

    name = fields.Char(string="Description", required=True)
    reference = fields.Char(
        string="Transaction Ref",
        required=True,
        size=32,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("fix.intercompany.tx") or "/",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    rule_id = fields.Many2one("fix.intercompany.rule", string="Applicable Rule", tracking=True)
    scope = fields.Selection(SCOPES, string="Scope", compute="_compute_scope", store=True)
    source_entity_id = fields.Many2one("fix.entity", string="Originating Entity", required=True)
    target_entity_id = fields.Many2one("fix.entity", string="Counterparty Entity", required=True)
    source_branch_id = fields.Many2one(
        "fix.branch",
        string="Originating Branch",
        compute="_compute_branches",
        store=True,
        readonly=False,
    )
    target_branch_id = fields.Many2one(
        "fix.branch",
        string="Counterparty Branch",
        compute="_compute_branches",
        store=True,
        readonly=False,
    )
    transaction_date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    amount = fields.Monetary(string="Transaction Amount", required=True)
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending_matching", "Pending Counterparty Match"),
            ("matched", "Matched & Reconciled"),
            ("settled", "Settled"),
            ("disputed", "Disputed"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    source_move_id = fields.Many2one(
        "account.move", string="Originating Entry", readonly=True, copy=False
    )
    target_move_id = fields.Many2one(
        "account.move", string="Counterparty (Mirror) Entry", readonly=True, copy=False
    )
    source_due_line_id = fields.Many2one(
        "account.move.line", string="Due-From Journal Item", readonly=True, copy=False
    )
    target_due_line_id = fields.Many2one(
        "account.move.line", string="Due-To Journal Item", readonly=True, copy=False
    )
    matched_date = fields.Datetime(string="Matched Timestamp", readonly=True, copy=False)
    match_difference = fields.Monetary(
        string="Match Difference",
        readonly=True,
        copy=False,
        help="Due-from less due-to at the last match, in the transaction currency",
    )
    mirror_invoice_ref = fields.Char(string="Mirror Entry Number", readonly=True, copy=False)

    @api.depends("rule_id.scope", "source_entity_id", "target_entity_id")
    def _compute_scope(self):
        for rec in self:
            if rec.rule_id:
                rec.scope = rec.rule_id.scope
            elif rec.source_entity_id and rec.source_entity_id == rec.target_entity_id:
                rec.scope = "interbranch"
            else:
                rec.scope = "intercompany"

    @api.depends("rule_id")
    def _compute_branches(self):
        for rec in self:
            if rec.rule_id and rec.rule_id.scope == "interbranch":
                rec.source_branch_id = rec.rule_id.source_branch_id
                rec.target_branch_id = rec.rule_id.target_branch_id
            else:
                rec.source_branch_id = rec.source_branch_id
                rec.target_branch_id = rec.target_branch_id

    @api.onchange("rule_id")
    def _onchange_rule_id(self):
        if self.rule_id:
            self.source_entity_id = self.rule_id.source_entity_id
            self.target_entity_id = self.rule_id.target_entity_id

    @api.constrains("scope", "source_entity_id", "target_entity_id")
    def _check_entities(self):
        for rec in self:
            if rec.scope == "intercompany" and rec.source_entity_id == rec.target_entity_id:
                raise ValidationError(
                    "An inter-company transaction needs two distinct legal entities."
                )

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _company_amount(self, company) -> float:
        """The transaction amount in the company's own currency, at the
        transaction date's rate."""
        return self.currency_id._convert(
            self.amount, company.currency_id, company, self.transaction_date
        )

    def _line(self, company, account, label, signed_amount):
        """One journal item: positive = debit. Foreign-currency transactions
        carry the transaction currency on the line."""
        balance = self._company_amount(company) * (1 if signed_amount > 0 else -1)
        vals = {
            "account_id": account.id,
            "name": label,
            "debit": balance if balance > 0 else 0.0,
            "credit": -balance if balance < 0 else 0.0,
        }
        if self.currency_id != company.currency_id:
            vals.update(currency_id=self.currency_id.id, amount_currency=signed_amount)
        return vals

    def _check_company_access(self, companies):
        if self.env.su:
            return
        missing = companies - self.env.user.company_ids
        if missing:
            raise UserError(
                "You need access to %s to post this transaction's entries."
                % ", ".join(missing.mapped("name"))
            )

    def _post(self, company, journal, lines, dims):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        env = self.with_company(company).env
        move, _dims = post_with_dimensions(
            env,
            {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": self.transaction_date,
                "ref": "%s %s" % (self.reference, self.name),
                "line_ids": [(0, 0, vals) for vals in lines],
            },
            dims,
            source="intercompany",
        )
        return move

    @staticmethod
    def _due_line(move, account, debit_side: bool):
        return move.line_ids.filtered(
            lambda line: (
                line.account_id == account
                and (line.balance > 0 if debit_side else line.balance < 0)
            )
        )[:1]

    def _line_amount_in_txn_currency(self, line) -> float:
        if line.currency_id == self.currency_id:
            return line.amount_currency
        return line.company_currency_id._convert(
            line.balance, self.currency_id, line.company_id, self.transaction_date
        )

    # ------------------------------------------------------------------
    # workflow
    # ------------------------------------------------------------------
    def action_generate_mirror(self):
        """Post the originating entry and its counterparty mirror.

        Inter-company: Dr due-from / Cr recharge income in the supplying
        company, Dr recharge expense / Cr due-to in the receiving company.
        Inter-branch: one entry in the entity's company, each side tagged
        with its branch (the branch due-to/due-from dimension).
        Idempotent: a transaction already mirrored is left untouched."""
        self.ensure_one()
        if self.target_move_id:
            return True
        if self.state != "draft":
            raise UserError("Only a draft transaction can be mirrored.")
        rule = self.rule_id
        if not rule:
            raise UserError(
                "Select the inter-company rule: it holds the journals and accounts both "
                "sides post on."
            )
        if (rule.source_entity_id, rule.target_entity_id) != (
            self.source_entity_id,
            self.target_entity_id,
        ):
            raise UserError(
                "Rule %s is for %s -> %s, not for this transaction's entities."
                % (rule.code, rule.source_entity_id.code, rule.target_entity_id.code)
            )
        errors = rule._posting_config_errors()
        if errors:
            raise UserError("Rule %s cannot post yet: %s." % (rule.code, "; ".join(errors)))
        src_company = self.source_entity_id.company_id
        tgt_company = self.target_entity_id.company_id
        self._check_company_access(src_company | tgt_company)
        label = "%s %s" % (self.reference, self.name)
        amount = self.amount

        if self.scope == "interbranch":
            src_branch, tgt_branch = self.source_branch_id, self.target_branch_id
            if not (src_branch and tgt_branch):
                raise UserError("An inter-branch transaction needs both branches.")
            lines = [
                self._line(src_company, rule.source_receivable_account_id, label, amount),
                self._line(src_company, rule.source_income_account_id, label, -amount),
                self._line(src_company, rule.target_expense_account_id, label, amount),
                self._line(src_company, rule.target_payable_account_id, label, -amount),
            ]
            dims = {
                idx: {"branch_id": b.id, "operating_unit_id": b.operating_unit_id.id}
                for idx, b in enumerate((src_branch, src_branch, tgt_branch, tgt_branch))
            }
            move = self._post(src_company, rule.source_journal_id, lines, dims)
            source_move = target_move = move
        else:
            source_move = self._post(
                src_company,
                rule.source_journal_id,
                [
                    self._line(src_company, rule.source_receivable_account_id, label, amount),
                    self._line(src_company, rule.source_income_account_id, label, -amount),
                ],
                {},
            )
            target_move = self._post(
                tgt_company,
                rule.target_journal_id,
                [
                    self._line(tgt_company, rule.target_expense_account_id, label, amount),
                    self._line(tgt_company, rule.target_payable_account_id, label, -amount),
                ],
                {},
            )
        self.write(
            {
                "source_move_id": source_move.id,
                "target_move_id": target_move.id,
                "source_due_line_id": self._due_line(
                    source_move, rule.source_receivable_account_id, True
                ).id,
                "target_due_line_id": self._due_line(
                    target_move, rule.target_payable_account_id, False
                ).id,
                "mirror_invoice_ref": target_move.name,
                "state": "pending_matching",
            }
        )
        return True

    def action_match(self):
        """Match the two POSTED due lines against the transaction.

        Agreement (both sides equal the transaction amount) -> matched.
        Any difference, or a side reset to draft, -> disputed, with the
        difference recorded; the counterparty finance teams resolve it."""
        self.ensure_one()
        if self.state not in ("pending_matching", "disputed"):
            raise UserError("Generate the mirror entries before matching.")
        src, tgt = self.source_due_line_id, self.target_due_line_id
        if not (src and tgt):
            raise UserError("The due-from / due-to journal items are missing.")
        sudo_src, sudo_tgt = src.sudo(), tgt.sudo()
        not_posted = [
            line.move_id.name or str(line.move_id.id)
            for line in (sudo_src, sudo_tgt)
            if line.move_id.state != "posted"
        ]
        due_from = self._line_amount_in_txn_currency(sudo_src)
        due_to = -self._line_amount_in_txn_currency(sudo_tgt)
        currency = self.currency_id
        difference = currency.round(due_from - due_to)
        agrees = (
            not not_posted
            and currency.is_zero(due_from - self.amount)
            and currency.is_zero(due_to - self.amount)
        )
        if agrees:
            self.write(
                {
                    "state": "matched",
                    "matched_date": fields.Datetime.now(),
                    "match_difference": 0.0,
                }
            )
            return True
        self.write({"state": "disputed", "match_difference": difference})
        reason = (
            "entries not posted: %s" % ", ".join(not_posted)
            if not_posted
            else "due-from %.2f vs due-to %.2f (transaction %.2f)" % (due_from, due_to, self.amount)
        )
        self.message_post(body="Match failed — %s." % reason)
        return {"status": "disputed", "difference": difference, "reason": reason}

    def action_mark_settled(self):
        """Settled only when the ledger says so: both due lines fully
        reconciled against their settlement (bank transfer / netting)."""
        self.ensure_one()
        if self.state != "matched":
            raise UserError("Only a matched transaction can be settled.")
        open_sides = [
            line.account_id.display_name
            for line in (self.source_due_line_id.sudo(), self.target_due_line_id.sudo())
            if not line.reconciled
        ]
        if open_sides:
            raise UserError(
                "Not settled in the ledger yet: reconcile the settlement against %s first "
                "(the due accounts must allow reconciliation)." % ", ".join(open_sides)
            )
        self.write({"state": "settled"})
        return True
