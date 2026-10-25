# fix_asset_depreciation — M49 dual-book monthly depreciation run.
#
# Accounting book (IAS 16): straight-line over the remaining useful life,
# posted to the GL per category (Dr depreciation expense / Cr accumulated
# depreciation) on the category's journal and accounts.
# Tax book (ITA 2023 Third Schedule): reducing balance at the effective-dated
# class rate; a memo book (no GL) whose WDV feeds the deferred-tax
# difference. Idempotency: ONE line per asset, book and month (database
# constraint) — a re-run of a month skips assets already charged.
from collections import defaultdict

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import (
    USER_GROUP,
    month_end,
    month_start,
    post_entry,
    require_accounts,
    require_group,
)

BOOKS = [("book", "Accounting Book (IAS 16)"), ("tax", "Tax Book (ITA 2023)")]


class FixAssetDepreciationRun(models.Model):
    _name = "fix.asset.depreciation.run"
    _description = "Depreciation Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_start desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Branch Scope", help="Leave empty: every branch."
    )
    name = fields.Char(string="Run", compute="_compute_name", store=True)
    book = fields.Selection(BOOKS, string="Book", required=True, default="book", tracking=True)
    period_start = fields.Date(
        string="Period (Month)",
        required=True,
        default=lambda self: month_start(fields.Date.context_today(self)),
        tracking=True,
    )
    asset_ids = fields.Many2many(
        "fix.fixed.asset", string="Assets (Scope)", help="Leave empty: every active asset."
    )
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("posted", "Posted")],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.asset.depreciation.line", "run_id", string="Lines")
    currency_id = fields.Many2one(related="company_id.currency_id")
    total_amount = fields.Monetary(
        string="Total Depreciation", compute="_compute_total", store=True
    )
    asset_count = fields.Integer(string="Assets Charged", compute="_compute_total", store=True)
    move_ids = fields.Many2many("account.move", string="Journal Entries", readonly=True, copy=False)
    note = fields.Text(string="Run Notes", readonly=True)

    @api.depends("book", "period_start")
    def _compute_name(self):
        labels = dict(BOOKS)
        for rec in self:
            rec.name = "%s %s" % (
                labels.get(rec.book, ""),
                rec.period_start.strftime("%Y-%m") if rec.period_start else "",
            )

    @api.depends("line_ids.amount")
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped("amount"))
            rec.asset_count = len(rec.line_ids)

    @api.constrains("period_start")
    def _check_period(self):
        for rec in self:
            if rec.period_start and rec.period_start.day != 1:
                raise ValidationError(self.env._("A depreciation period starts on the 1st."))

    @api.ondelete(at_uninstall=False)
    def _unlink_unposted_only(self):
        if any(rec.state == "posted" for rec in self):
            raise UserError(self.env._("A posted depreciation run cannot be deleted."))

    def _candidate_assets(self):
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("state", "=", "active"),
            ("depreciation_start", "<=", self.period_start),
            ("purchase_date", "<=", month_end(self.period_start)),
        ]
        if self.operating_unit_id:
            domain.append(("operating_unit_id", "=", self.operating_unit_id.id))
        if self.asset_ids:
            domain.append(("id", "in", self.asset_ids.ids))
        return self.env["fix.fixed.asset"].search(domain)

    def action_compute(self):
        """(Re)build the run's lines. Assets already charged for this book and
        month (in this or any other run) are skipped — never charged twice."""
        require_group(self.env, USER_GROUP, "Computing depreciation")
        Line = self.env["fix.asset.depreciation.line"]
        Rate = self.env["fix.asset.tax.rate"]
        for run in self:
            if run.state == "posted":
                raise UserError(self.env._("%s is already posted.", run.name))
            run.line_ids.unlink()
            assets = run._candidate_assets()
            charged = Line.search(
                [
                    ("asset_id", "in", assets.ids),
                    ("book", "=", run.book),
                    ("period_start", "=", run.period_start),
                ]
            ).mapped("asset_id")
            vals, skipped_done, skipped_zero, no_class, missing_rates = [], charged, 0, 0, set()
            for asset in assets - charged:
                if run.book == "book":
                    amount = asset._book_amount(run.period_start)
                else:
                    code = asset.category_id.tax_rate_code
                    if not code:
                        no_class += 1
                        continue
                    rate = Rate.rate_for(code, run.period_start, run.company_id)
                    if not rate:
                        missing_rates.add(code)
                        continue
                    amount = asset._tax_amount(run.period_start, rate.rate_percent)
                if amount <= 0.0:
                    skipped_zero += 1
                    continue
                vals.append(
                    {
                        "run_id": run.id,
                        "asset_id": asset.id,
                        "book": run.book,
                        "period_start": run.period_start,
                        "amount": amount,
                    }
                )
            if missing_rates:
                raise UserError(
                    self.env._(
                        "No tax depreciation rate is in force on %s for class(es) %s — "
                        "add it under Tax Depreciation Rates (verify with the tax adviser).",
                        run.period_start,
                        ", ".join(sorted(missing_rates)),
                    )
                )
            Line.create(vals)
            notes = [
                self.env._("%s asset(s) charged.", len(vals)),
            ]
            if skipped_done:
                notes.append(
                    self.env._("%s already charged for this month — skipped.", len(skipped_done))
                )
            if skipped_zero:
                notes.append(self.env._("%s fully depreciated — nothing to charge.", skipped_zero))
            if no_class:
                notes.append(
                    self.env._(
                        "%s without a tax depreciation class — not in the tax book.", no_class
                    )
                )
            run.write({"state": "computed", "note": "\n".join(notes)})
        return True

    def action_post(self):
        """Post the computed run. Book: one GL entry per journal, one Dr/Cr
        pair per category, dated the month end. Tax: locks the memo book (the
        tax book never posts to the GL)."""
        require_group(self.env, USER_GROUP, "Posting depreciation")
        for run in self:
            if run.state != "computed":
                raise UserError(self.env._("Compute %s before posting it.", run.name))
            if not run.line_ids:
                raise UserError(self.env._("%s has nothing to post.", run.name))
            if run.book == "book":
                run._post_book()
            run.state = "posted"
        return True

    def _post_book(self):
        self.ensure_one()
        by_cat = defaultdict(lambda: self.env["fix.asset.depreciation.line"])
        for line in self.line_ids:
            if not line.asset_id.category_id:
                raise UserError(
                    self.env._("Choose the asset category of %s first.", line.asset_id.display_name)
                )
            by_cat[line.asset_id.category_id] |= line
        for cat in by_cat:
            require_accounts(
                cat,
                ["journal_id", "expense_account_id", "accumulated_account_id"],
                "Depreciation",
            )
        by_journal = defaultdict(list)
        for cat in by_cat:
            by_journal[cat.journal_id].append(cat)
        moves = self.env["account.move"]
        for journal, cats in by_journal.items():
            entry = []
            for cat in cats:
                amount = sum(by_cat[cat].mapped("amount"))
                label = "%s — %s" % (self.name, cat.name)
                entry.append((cat.expense_account_id, amount, 0.0, label))
                entry.append((cat.accumulated_account_id, 0.0, amount, label))
            move = post_entry(
                self.env, self.company_id, journal, month_end(self.period_start), self.name, entry
            )
            for cat in cats:
                by_cat[cat].write({"move_id": move.id})
            moves |= move
        self.move_ids = [(4, m.id) for m in moves]
        for line in self.line_ids:
            line.asset_id._publish_depreciation(line.amount)

    @api.model
    def _depreciate(self, assets, period, book="book"):
        """One-shot run for specific assets (the register's Accrue Month and
        the lease month posting). Refuses when nothing is left to charge for
        the month, so repeated calls never double-post."""
        runs = self.browse()
        for company in assets.mapped("company_id"):
            scoped = assets.filtered(lambda a, c=company: a.company_id == c)
            run = self.create(
                {
                    "company_id": company.id,
                    "book": book,
                    "period_start": period,
                    "asset_ids": [(6, 0, scoped.ids)],
                }
            )
            run.action_compute()
            if not run.line_ids:
                raise UserError(
                    self.env._(
                        "%s: already depreciated for %s (or fully depreciated).",
                        ", ".join(scoped.mapped("display_name")),
                        period.strftime("%Y-%m"),
                    )
                )
            run.action_post()
            runs |= run
        return runs


class FixAssetDepreciationLine(models.Model):
    _name = "fix.asset.depreciation.line"
    _description = "Depreciation Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_start desc, id desc"

    run_id = fields.Many2one(
        "fix.asset.depreciation.run", string="Run", required=True, ondelete="cascade", index=True
    )
    asset_id = fields.Many2one(
        "fix.fixed.asset", string="Asset", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="run_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="asset_id.operating_unit_id", store=True, string="Branch"
    )
    category_id = fields.Many2one(related="asset_id.category_id", store=True)
    book = fields.Selection(BOOKS, string="Book", required=True)
    period_start = fields.Date(string="Period (Month)", required=True, index=True)
    currency_id = fields.Many2one(related="run_id.currency_id")
    amount = fields.Monetary(string="Depreciation", required=True)
    state = fields.Selection(related="run_id.state", store=True)
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True)

    _asset_book_period_uniq = models.Constraint(
        "UNIQUE (asset_id, book, period_start)",
        "An asset is depreciated once per book and month.",
    )
