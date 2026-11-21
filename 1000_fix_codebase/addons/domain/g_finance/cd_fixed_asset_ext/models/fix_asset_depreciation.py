# fix_asset_depreciation — M49 dual-book monthly depreciation run.
#
# Accounting book (IAS 16): straight-line over the remaining useful life,
# posted to the GL per category (Dr depreciation expense / Cr accumulated
# depreciation) on the category's journal and accounts, through M19.
# Tax book (ITA 2023 Third Schedule): reducing balance on the annual written-
# down value at the effective-dated class rate of the M51 master (BRU-FXA-13);
# a memo book (no GL) whose WDV feeds the deferred-tax difference.
# Idempotency: ONE line per asset, book and month (database constraint).
#
# A08 workflow audit (2026-11-04) M49-7: a run's state was written 'posted'
# with no journal entry; posted lines were edited and deleted; October 2027
# was depreciated today; an abandoned computed run held its month forever;
# a run into a locked period was silently re-dated by the ledger. The run's
# state and entries are guarded, lines are written by the run only and never
# change once posted, future months and closed periods are refused, and a
# month is held only by a POSTED line.
from collections import defaultdict

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import (
    USER_GROUP,
    assert_period_open,
    dhaka_today,
    month_end,
    month_start,
    post_entry,
    require_accounts,
    require_group,
)

BOOKS = [("book", "Accounting Book (IAS 16)"), ("tax", "Tax Book (ITA 2023)")]


def tax_depreciation_rate(env, code, on_date, company):
    """The Third Schedule rate of a class from the M51 master (BRU-FXA-13),
    refused while the row is flagged verify-with-adviser (A08 M49-8)."""
    try:
        rate = env["fix.tax.rate"].sudo().find_rate("depreciation", code, on_date, company)
    except UserError:
        return None
    if rate.verify_with_adviser:
        raise UserError(
            env._(
                "The tax depreciation rate of class %s (%s%%) is not yet confirmed by the tax "
                "adviser: record the adviser's confirmation on it (Tax Rate Master) before the "
                "tax book uses it.",
                code,
                rate.rate,
            )
        )
    return rate


class FixAssetDepreciationRun(models.Model):
    _name = "fix.asset.depreciation.run"
    _description = "Depreciation Run"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
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
        default=lambda self: month_start(dhaka_today(self.env)),
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

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "move_ids", "note"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state == "posted":
            locked |= {"book", "period_start", "asset_ids", "operating_unit_id", "company_id"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            posted = self.filtered(lambda r: r.state == "posted")
            scope = {"book", "period_start", "asset_ids", "operating_unit_id", "company_id"}
            if posted and set(vals) & scope:
                raise UserError(self.env._("A posted depreciation run cannot change."))
        return super().write(vals)

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

    def _assert_period(self):
        self.ensure_one()
        assert_period_open(
            self.env, self.company_id, month_end(self.period_start), "Depreciation %s" % self.name
        )

    def action_compute(self):
        """(Re)build the run's lines. Assets already charged for this book and
        month by a POSTED line are skipped — never charged twice; a line of
        another run that was computed and never posted is taken over."""
        require_group(self.env, USER_GROUP, "Computing depreciation")
        Line = self.env["fix.asset.depreciation.line"].sudo()
        for run in self:
            if run.state == "posted":
                raise UserError(self.env._("%s is already posted.", run.name))
            run._assert_period()
            run.sudo().line_ids.unlink()
            assets = run._candidate_assets()
            same_month = Line.search(
                [
                    ("asset_id", "in", assets.ids),
                    ("book", "=", run.book),
                    ("period_start", "=", run.period_start),
                ]
            )
            charged = same_month.filtered(lambda ln: ln.state == "posted").mapped("asset_id")
            abandoned = same_month.filtered(lambda ln: ln.state != "posted")
            taken_over = len(abandoned)
            abandoned.unlink()
            vals, skipped_zero, no_class, missing_rates = [], 0, 0, set()
            for asset in assets - charged:
                if run.book == "book":
                    amount = asset._book_amount(run.period_start)
                else:
                    code = asset.category_id.tax_rate_code
                    if not code:
                        no_class += 1
                        continue
                    rate = tax_depreciation_rate(self.env, code, run.period_start, run.company_id)
                    if not rate:
                        missing_rates.add(code)
                        continue
                    amount = asset._tax_amount(run.period_start, rate.rate)
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
                        "add it to the Tax Rate Master (M51, kind Tax depreciation).",
                        run.period_start,
                        ", ".join(sorted(missing_rates)),
                    )
                )
            Line.create(vals)
            notes = [self.env._("%s asset(s) charged.", len(vals))]
            if charged:
                notes.append(
                    self.env._("%s already charged for this month — skipped.", len(charged))
                )
            if taken_over:
                notes.append(self.env._("%s line(s) of an unposted run taken over.", taken_over))
            if skipped_zero:
                notes.append(self.env._("%s fully depreciated — nothing to charge.", skipped_zero))
            if no_class:
                notes.append(
                    self.env._(
                        "%s without a tax depreciation class — not in the tax book.", no_class
                    )
                )
            run._guarded().write({"state": "computed", "note": "\n".join(notes)})
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
            run._assert_period()
            if run.book == "book":
                run._post_book()
            run._guarded().write({"state": "posted"})
        return True

    def _post_book(self):
        """A07 FIN-01 (2026-11-20): the charge is posted on each asset's own
        branch. One Dr/Cr pair per category AND branch, every line carrying
        that branch as its operating unit; an asset without a branch is
        refused (it used to land on the company's first operating unit)."""
        self.ensure_one()
        by_key = defaultdict(lambda: self.env["fix.asset.depreciation.line"])
        for line in self.line_ids:
            asset = line.asset_id
            if not asset.category_id:
                raise UserError(
                    self.env._("Choose the asset category of %s first.", asset.display_name)
                )
            if not asset.operating_unit_id:
                raise UserError(
                    self.env._(
                        "%s has no branch: its depreciation is posted on the asset's own branch, "
                        "never on the company's first one. Record its branch (asset transfer) "
                        "first.",
                        asset.display_name,
                    )
                )
            by_key[(asset.category_id, asset.operating_unit_id)] |= line
        cats = {cat for cat, _ou in by_key}
        for cat in cats:
            require_accounts(
                cat,
                ["journal_id", "expense_account_id", "accumulated_account_id"],
                "Depreciation",
            )
        by_journal = defaultdict(list)
        for cat, ou in by_key:
            by_journal[cat.journal_id].append((cat, ou))
        moves = self.env["account.move"]
        for journal, keys in by_journal.items():
            entry = []
            for cat, ou in sorted(keys, key=lambda k: (k[0].id, k[1].id)):
                amount = sum(by_key[(cat, ou)].mapped("amount"))
                label = "%s — %s — %s" % (self.name, cat.name, ou.name)
                entry.append((cat.expense_account_id, amount, 0.0, label, ou))
                entry.append((cat.accumulated_account_id, 0.0, amount, label, ou))
            move = post_entry(
                self.env, self.company_id, journal, month_end(self.period_start), self.name, entry
            )
            for key in keys:
                by_key[key].sudo().write({"move_id": move.id})
            moves |= move
        self._guarded().write({"move_ids": [(4, m.id) for m in moves]})
        for line in self.line_ids:
            line.asset_id._publish_depreciation(line.amount, line.move_id)

    @api.model
    def _cron_prepare_monthly_runs(self):
        """A08 M49-11: prepare the month's run of each book, for a person to
        check and post. NEVER posts: no journal entry and no posted tax line
        comes from this job. A run that cannot be computed (a tax rate the
        adviser has not confirmed, a closed period) stays in draft with the
        reason in its notes. Idempotent per company, book and month; a month
        that has nothing to charge leaves no run behind."""
        Asset = self.env["fix.fixed.asset"].sudo()
        prepared = self.browse()
        for company in self.env["res.company"].sudo().search([]):
            if not Asset.search_count([("company_id", "=", company.id), ("state", "=", "active")]):
                continue
            today = fields.Date.context_today(self.with_context(tz="Asia/Dhaka"))
            period = month_start(today)
            Run = self.sudo().with_company(company)
            for book, _label in BOOKS:
                if Run.search_count(
                    [
                        ("company_id", "=", company.id),
                        ("book", "=", book),
                        ("period_start", "=", period),
                        # A05 FIN-15: a run scoped to a few assets (Accrue
                        # Month, a rental unit's capitalisation catch-up) is
                        # not the company's month run; those assets are
                        # skipped by it as already charged
                        ("asset_ids", "=", False),
                    ]
                ):
                    continue
                run = Run.create({"company_id": company.id, "book": book, "period_start": period})
                try:
                    with self.env.cr.savepoint():
                        run.action_compute()
                except UserError as exc:
                    run._guarded().write(
                        {"note": "Prepared by the monthly job, not computed: %s" % exc}
                    )
                else:
                    if not run.line_ids:
                        run.unlink()
                        continue
                prepared |= run
        return prepared

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
    """One asset's charge for one book and month. Written by its run only;
    a POSTED line is never edited nor deleted (A08 M49-7)."""

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

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError(self.env._("Depreciation lines are written by their run only."))
        return super().create(vals_list)

    def write(self, vals):
        if set(vals) - {"message_follower_ids"}:
            if not self.env.su:
                raise UserError(self.env._("Depreciation lines are written by their run only."))
            if any(ln.state == "posted" for ln in self) and set(vals) - {"move_id"}:
                raise UserError(self.env._("A posted depreciation line is never edited."))
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_never_posted(self):
        if any(ln.state == "posted" for ln in self):
            raise UserError(self.env._("A posted depreciation line is never deleted."))
        if not self.env.su:
            raise UserError(self.env._("Depreciation lines are removed by their run only."))
