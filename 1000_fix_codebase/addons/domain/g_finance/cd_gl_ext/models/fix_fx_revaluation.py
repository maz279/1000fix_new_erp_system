# IFRS / IAS 21 foreign-currency revaluation for the GL. Bangladesh service companies
# carry USD import and licence liabilities, so open foreign-currency balances must be
# restated at the closing rate with the difference posted as an unrealized gain/loss.
#
# A08 remediation (B3, 4 Nov 2026; M19-3, -4, -11, P1-2, F6):
#   - each posted run is reversed on the first day after its closing date, so the
#     ledger carries only the latest restatement (monthly runs no longer
#     double-count);
#   - one posted run per company and closing date, and never one older than a run
#     already posted;
#   - the OPEN amount is restated (amount_residual / amount_residual_currency), so a
#     partly paid USD 100 receivable with USD 50 open is revalued on USD 50;
#   - the closing rate must be at most `cd_gl_ext.fx_rate_max_age_days` old;
#   - gain/loss go only to the company's configured exchange gain/loss accounts
#     (or the accounts listed in `cd_gl_ext.fx_gain_account_ids` /
#     `cd_gl_ext.fx_loss_account_ids`);
#   - the run is finance-only (no base.group_user access), its lines are written only
#     by the compute, the post recomputes them from the ledger and refuses a run that
#     no longer agrees, and the poster is an Accounting Administrator other than the
#     user who computed it.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

PARAM_RATE_AGE = "cd_gl_ext.fx_rate_max_age_days"
# BRU-FIN-07: "the official closing rate". A rate older than three days (a
# weekend plus a bank holiday) is not the closing rate of the date.
DEFAULT_RATE_AGE = 3
PARAM_GAIN_ACCOUNTS = "cd_gl_ext.fx_gain_account_ids"
PARAM_LOSS_ACCOUNTS = "cd_gl_ext.fx_loss_account_ids"
ACCOUNT_USER = "account.group_account_user"
ACCOUNT_MANAGER = "account.group_account_manager"


def _id_list(env, key):
    raw = env["ir.config_parameter"].sudo().get_param(key) or ""
    return {int(x) for x in raw.replace(";", ",").split(",") if x.strip().isdigit()}


class FixFxRevaluation(models.Model):
    _name = "fix.fx.revaluation"
    _description = "FX Revaluation Run"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "rate_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Company currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    rate_date = fields.Date(
        string="Closing rate date",
        required=True,
        default=fields.Date.context_today,
        help="The balances are restated at the rate effective on this date (IAS 21).",
    )
    journal_id = fields.Many2one("account.journal", string="Journal", required=True)
    gain_account_id = fields.Many2one(
        "account.account",
        string="Unrealized FX gain account",
        default=lambda self: self.env.company.income_currency_exchange_account_id,
    )
    loss_account_id = fields.Many2one(
        "account.account",
        string="Unrealized FX loss account",
        default=lambda self: self.env.company.expense_currency_exchange_account_id,
    )
    line_ids = fields.One2many("fix.fx.revaluation.line", "run_id", string="Open balances")
    total_gain = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    total_loss = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    net_amount = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    move_id = fields.Many2one("account.move", string="Posted entry", readonly=True, copy=False)
    reversal_move_id = fields.Many2one(
        "account.move", string="Reversal entry", readonly=True, copy=False
    )
    rate_used_date = fields.Date(string="Rate effective from", readonly=True, copy=False)
    computed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    computed_at = fields.Datetime(readonly=True, copy=False)
    posted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    posted_at = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("posted", "Posted")],
        required=True,
        default="draft",
        tracking=True,
    )

    _posted_date_unique = models.UniqueIndex(
        "(company_id, rate_date) WHERE state = 'posted'",
        "One FX revaluation is posted per company and closing date.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "move_id",
            "reversal_move_id",
            "rate_used_date",
            "computed_by_id",
            "computed_at",
            "posted_by_id",
            "posted_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | {"total_gain", "total_loss", "net_amount"}
        if any(r.state == "posted" for r in self):
            locked |= {
                "rate_date",
                "journal_id",
                "gain_account_id",
                "loss_account_id",
                "company_id",
            }
        return locked

    def write(self, vals):
        frozen = {"rate_date", "journal_id", "gain_account_id", "loss_account_id", "company_id"}
        if frozen & set(vals) and not self._fix_guard_open():
            if any(r.state == "posted" for r in self):
                raise UserError("A posted FX revaluation is frozen.")
            result = super().write(vals)
            # The computed figures belonged to the old parameters.
            self.filtered(lambda r: r.state == "computed")._fix_reset_computed()
            return result
        return super().write(vals)

    def _fix_reset_computed(self):
        for run in self:
            run.line_ids.sudo().unlink()
            run._guarded().write({"state": "draft", "computed_by_id": False, "computed_at": False})

    @api.depends("line_ids.gain_loss")
    def _compute_totals(self):
        for run in self:
            gains = sum(ln.gain_loss for ln in run.line_ids if ln.gain_loss > 0)
            losses = sum(-ln.gain_loss for ln in run.line_ids if ln.gain_loss < 0)
            run.total_gain = round(gains, 2)
            run.total_loss = round(losses, 2)
            run.net_amount = round(gains - losses, 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.fx.revaluation") or "FXR/New"
                )
        return super().create(vals_list)

    # ------------------------------------------------------------ computation
    def _require(self, xmlid, what):
        from .fix_gl_ext import has_role  # the administrator does the accountant's duties

        if not has_role(self.env, xmlid):
            raise AccessError("%s needs the %s role." % (what, self.env.ref(xmlid).name))

    def _closing_rate(self, foreign):
        """(rate, effective date) of `foreign` -> company currency on the
        closing date, refusing a rate older than the configured age."""
        self.ensure_one()
        Rate = self.env["res.currency.rate"].sudo()
        rate_row = Rate.search(
            [
                ("currency_id", "=", foreign.id),
                ("name", "<=", self.rate_date),
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.company_id.root_id.id),
            ],
            order="name desc",
            limit=1,
        )
        max_age = int(
            float(
                self.env["ir.config_parameter"].sudo().get_param(PARAM_RATE_AGE) or DEFAULT_RATE_AGE
            )
        )
        if not rate_row:
            raise UserError(
                "No %s rate exists on or before %s: load the official closing rate first."
                % (foreign.name, self.rate_date)
            )
        if (self.rate_date - rate_row.name).days > max_age:
            raise UserError(
                "The latest %s rate is dated %s, %d day(s) before the closing date %s; the "
                "revaluation needs the official closing rate (at most %d day(s) old, %s)."
                % (
                    foreign.name,
                    rate_row.name,
                    (self.rate_date - rate_row.name).days,
                    self.rate_date,
                    max_age,
                    PARAM_RATE_AGE,
                )
            )
        rate = foreign._get_conversion_rate(
            foreign, self.company_id.currency_id, self.company_id, self.rate_date
        )
        return rate, rate_row.name

    def _fix_revaluation_rows(self):
        """The restatement of every open foreign-currency AR/AP line, as dicts.
        Read as the CALLER: a user with no journal-item read is refused."""
        self.ensure_one()
        company_currency = self.company_id.currency_id
        Line = self.env["account.move.line"]
        domain = [
            ("company_id", "=", self.company_id.id),
            ("parent_state", "=", "posted"),
            ("date", "<=", self.rate_date),
            ("account_id.account_type", "in", ("asset_receivable", "liability_payable")),
            ("currency_id", "!=", company_currency.id),
            ("reconciled", "=", False),
            ("amount_residual_currency", "!=", 0.0),
        ]
        rows, rate_dates, rates = [], [], {}
        for line in Line.search(domain, order="id"):
            foreign = line.currency_id
            if foreign.id not in rates:
                rates[foreign.id] = self._closing_rate(foreign)
            closing, rate_from = rates[foreign.id]
            rate_dates.append(rate_from)
            open_foreign = round(line.amount_residual_currency, 2)
            old_base = round(line.amount_residual, 2)
            new_base = round(open_foreign * closing, 2)
            rows.append(
                {
                    "move_line_id": line.id,
                    "account_id": line.account_id.id,
                    "partner_id": line.partner_id.id,
                    "foreign_currency_id": foreign.id,
                    "foreign_balance": open_foreign,
                    "old_base": old_base,
                    "closing_rate": closing,
                    "new_base": new_base,
                    "gain_loss": round(new_base - old_base, 2),
                }
            )
        return rows, (min(rate_dates) if rate_dates else False)

    def action_compute(self):
        """Restate every OPEN foreign-currency AR/AP line at the closing rate.

        The comparison is the base-currency residual already booked vs the
        foreign residual at the closing rate — the difference is the
        unrealized gain/loss. Fully reconciled lines are skipped."""
        self._require(ACCOUNT_USER, "Computing an FX revaluation")
        for run in self:
            if run.state == "posted":
                raise UserError("FX revaluation %s is posted." % run.name)
            rows, rate_from = run._fix_revaluation_rows()
            run.line_ids.sudo().unlink()
            if rows:
                self.env["fix.fx.revaluation.line"].sudo().create(
                    [dict(row, run_id=run.id) for row in rows]
                )
            run._guarded().write(
                {
                    "state": "computed",
                    "computed_by_id": self.env.uid,
                    "computed_at": fields.Datetime.now(),
                    "rate_used_date": rate_from,
                }
            )
        return True

    def _fix_check_accounts(self):
        self.ensure_one()
        company = self.company_id
        gains = _id_list(self.env, PARAM_GAIN_ACCOUNTS) | set(
            company.income_currency_exchange_account_id.ids
        )
        losses = _id_list(self.env, PARAM_LOSS_ACCOUNTS) | set(
            company.expense_currency_exchange_account_id.ids
        )
        if not (self.gain_account_id and self.loss_account_id):
            raise UserError("Set both the unrealized FX gain and loss accounts first")
        if self.gain_account_id.id not in gains or self.gain_account_id.internal_group != "income":
            raise UserError(
                "%s is not a configured FX gain account (the company's exchange gain account or "
                "%s); unrealized gains go only to an FX income account (IAS 21)."
                % (self.gain_account_id.display_name, PARAM_GAIN_ACCOUNTS)
            )
        if (
            self.loss_account_id.id not in losses
            or self.loss_account_id.internal_group != "expense"
        ):
            raise UserError(
                "%s is not a configured FX loss account (the company's exchange loss account or "
                "%s); unrealized losses go only to an FX expense account (IAS 21)."
                % (self.loss_account_id.display_name, PARAM_LOSS_ACCOUNTS)
            )

    def action_post(self):
        """Post the net difference as one journal entry (unrealized FX) and
        its reversal on the day after the closing date."""
        from .fix_gl_ext import post_with_dimensions

        self.ensure_one()
        self._require(ACCOUNT_MANAGER, "Posting an FX revaluation")
        if self.state != "computed":
            raise UserError("Compute the revaluation before posting it")
        if self.move_id:
            raise UserError("This run is already posted")
        if not self.env.su and self.env.user in (self.computed_by_id | self.create_uid):
            raise UserError(
                "Segregation of duties: %s prepared or computed FX revaluation %s and cannot "
                "post it; another Accounting Administrator reviews and posts it."
                % (self.env.user.name, self.name)
            )
        if not self.line_ids:
            raise UserError("There is no open foreign-currency balance to revalue")
        self._fix_check_accounts()
        # The ledger, not the stored lines, decides what posts.
        rows, _rate_from = self._fix_revaluation_rows()
        stored = sorted(
            (ln.move_line_id.id, round(ln.gain_loss, 2), round(ln.foreign_balance, 2))
            for ln in self.line_ids.sudo()
        )
        fresh = sorted((r["move_line_id"], r["gain_loss"], r["foreign_balance"]) for r in rows)
        if stored != fresh:
            raise UserError(
                "The open balances or rates changed since %s was computed; compute it again "
                "before posting." % self.name
            )
        later = self.search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("state", "=", "posted"),
                ("rate_date", ">=", self.rate_date),
            ],
            limit=1,
        )
        if later:
            raise UserError(
                "FX revaluation %s is already posted for %s (on or after %s); a closing date is "
                "revalued once, in order." % (later.name, later.rate_date, self.rate_date)
            )
        net = round(sum(r["gain_loss"] for r in rows), 2)
        if abs(net) < 0.01:
            raise UserError("The revaluation nets to zero — nothing to post")
        entries = []
        # per account, so each GL account carries its own revaluation
        by_account = {}
        for row in rows:
            if abs(row["gain_loss"]) < 0.01:
                continue
            by_account[row["account_id"]] = (
                by_account.get(row["account_id"], 0.0) + row["gain_loss"]
            )
        for account_id, amount in by_account.items():
            # The run records (new base - old base) per balance-sheet account, so the
            # adjustment moves that account in the SAME direction: a positive
            # difference is a debit (a receivable rises / a payable falls), a negative
            # one is a credit. The gain/loss account takes the opposite side below.
            amount = round(amount, 2)
            entries.append(
                (
                    0,
                    0,
                    {
                        "account_id": account_id,
                        "debit": amount if amount > 0 else 0.0,
                        "credit": -amount if amount < 0 else 0.0,
                        "name": "FX revaluation %s" % self.name,
                    },
                )
            )
        if net > 0:
            entries.append(
                (
                    0,
                    0,
                    {
                        "account_id": self.gain_account_id.id,
                        "credit": net,
                        "name": "Unrealized FX gain",
                    },
                )
            )
        else:
            entries.append(
                (
                    0,
                    0,
                    {
                        "account_id": self.loss_account_id.id,
                        "debit": -net,
                        "name": "Unrealized FX loss",
                    },
                )
            )
        move, _dims = post_with_dimensions(
            self.env,
            {
                "move_type": "entry",
                "journal_id": self.journal_id.id,
                "company_id": self.company_id.id,
                "date": self.rate_date,
                "ref": "FX revaluation %s" % self.name,
                "line_ids": entries,
            },
            {},
            source="fx_revaluation",
            source_ref=self.name,
        )
        reversal_date = self.rate_date + timedelta(days=1)
        reversal, _rdims = post_with_dimensions(
            self.env,
            {
                "move_type": "entry",
                "journal_id": self.journal_id.id,
                "company_id": self.company_id.id,
                "date": reversal_date,
                "ref": "Reversal of FX revaluation %s" % self.name,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": vals["account_id"],
                            "debit": vals.get("credit", 0.0),
                            "credit": vals.get("debit", 0.0),
                            "name": "Reversal — %s" % vals["name"],
                        },
                    )
                    for _c, _i, vals in entries
                ],
            },
            {},
            source="fx_revaluation",
            source_ref="%s reversal" % self.name,
        )
        self._guarded().write(
            {
                "move_id": move.id,
                "reversal_move_id": reversal.id,
                "state": "posted",
                "posted_by_id": self.env.uid,
                "posted_at": fields.Datetime.now(),
            }
        )
        self.message_post(
            body="Posted %s (reversed on %s by %s) by %s."
            % (move.name, reversal_date, reversal.name, self.env.user.name)
        )
        return move


class FixFxRevaluationLine(models.Model):
    """One restated open balance. Written only by the run's compute (the
    ACL gives users read only); the post recomputes and compares."""

    _name = "fix.fx.revaluation.line"
    _description = "FX Revaluation Line"
    _order = "id"

    run_id = fields.Many2one("fix.fx.revaluation", required=True, ondelete="cascade", index=True)
    move_line_id = fields.Many2one("account.move.line", string="Journal item", ondelete="set null")
    account_id = fields.Many2one("account.account", string="Account", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    foreign_currency_id = fields.Many2one("res.currency", string="Currency")
    foreign_balance = fields.Monetary(
        string="Foreign balance (open)", currency_field="foreign_currency_id"
    )
    old_base = fields.Monetary(string="Booked open (BDT)", currency_field="currency_id")
    closing_rate = fields.Float(string="Closing rate", digits=(12, 6))
    new_base = fields.Monetary(string="Restated (BDT)", currency_field="currency_id")
    gain_loss = fields.Monetary(string="Gain / (loss)", currency_field="currency_id")
    currency_id = fields.Many2one(related="run_id.currency_id", store=True)
