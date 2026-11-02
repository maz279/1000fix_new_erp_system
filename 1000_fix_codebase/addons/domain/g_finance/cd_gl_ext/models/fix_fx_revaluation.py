# IFRS / IAS 21 foreign-currency revaluation for the GL. Bangladesh service companies
# carry USD import and licence liabilities, so open foreign-currency balances must be
# restated at the closing rate with the difference posted as an unrealized gain/loss.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixFxRevaluation(models.Model):
    _name = "fix.fx.revaluation"
    _description = "FX Revaluation Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
    gain_account_id = fields.Many2one("account.account", string="Unrealized FX gain account")
    loss_account_id = fields.Many2one("account.account", string="Unrealized FX loss account")
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
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("posted", "Posted")],
        required=True,
        default="draft",
        tracking=True,
    )

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

    def action_compute(self):
        """Restate every open foreign-currency AR/AP line at the closing rate.

        The comparison is base-currency balance now (already booked) vs the same
        foreign balance at the closing rate — the difference is the unrealized
        gain/loss. Fully reconciled lines (amount_currency = 0) are skipped: there
        is nothing left to restate."""
        Line = self.env["account.move.line"]
        company_currency = self.company_id.currency_id
        for run in self:
            run.line_ids.unlink()
            domain = [
                ("company_id", "=", run.company_id.id),
                ("parent_state", "=", "posted"),
                ("account_id.account_type", "in", ("asset_receivable", "liability_payable")),
                ("amount_currency", "!=", 0.0),
                ("currency_id", "!=", company_currency.id),
                ("reconciled", "=", False),
            ]
            Foreign = self.env["res.currency"]
            rows = Line.search(domain)
            for line in rows:
                foreign = line.currency_id
                closing = foreign._get_conversion_rate(
                    foreign, company_currency, run.company_id, run.rate_date
                )
                new_base = round(line.amount_currency * closing, 2)
                old_base = round(line.balance, 2)
                self.env["fix.fx.revaluation.line"].create(
                    {
                        "run_id": run.id,
                        "move_line_id": line.id,
                        "account_id": line.account_id.id,
                        "partner_id": line.partner_id.id,
                        "foreign_currency_id": foreign.id,
                        "foreign_balance": round(line.amount_currency, 2),
                        "old_base": old_base,
                        "closing_rate": closing,
                        "new_base": new_base,
                        "gain_loss": round(new_base - old_base, 2),
                    }
                )
            run.state = "computed"
            _ = Foreign  # keep the reference for readers

    def action_post(self):
        """Post the net difference as one journal entry (unrealized FX)."""
        self.ensure_one()
        if self.state != "computed":
            raise UserError("Compute the revaluation before posting it")
        if not self.line_ids:
            raise UserError("There is no open foreign-currency balance to revalue")
        if not (self.gain_account_id and self.loss_account_id):
            raise UserError("Set both the unrealized FX gain and loss accounts first")
        if abs(self.net_amount) < 0.01:
            raise UserError("The revaluation nets to zero — nothing to post")
        if self.move_id:
            raise UserError("This run is already posted")
        entries = []
        # per account, so each GL account carries its own revaluation
        by_account = {}
        for line in self.line_ids:
            if abs(line.gain_loss) < 0.01:
                continue
            bucket = by_account.setdefault(line.account_id, 0.0)
            by_account[line.account_id] = bucket + line.gain_loss
        for account, amount in by_account.items():
            # The run records (new base - old base) per balance-sheet account, so the
            # adjustment moves that account in the SAME direction: a positive
            # difference is a debit (a receivable rises / a payable falls), a negative
            # one is a credit. The gain/loss account takes the opposite side below.
            entries.append(
                (
                    0,
                    0,
                    {
                        "account_id": account.id,
                        "debit": amount if amount > 0 else 0.0,
                        "credit": -amount if amount < 0 else 0.0,
                        "name": "FX revaluation %s" % self.name,
                    },
                )
            )
        if self.net_amount > 0:
            entries.append(
                (
                    0,
                    0,
                    {
                        "account_id": self.gain_account_id.id,
                        "credit": self.net_amount,
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
                        "debit": -self.net_amount,
                        "name": "Unrealized FX loss",
                    },
                )
            )
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": self.journal_id.id,
                "date": self.rate_date,
                "ref": "FX revaluation %s" % self.name,
                "line_ids": entries,
            }
        )
        move.action_post()
        self.write({"move_id": move.id, "state": "posted"})
        return move


class FixFxRevaluationLine(models.Model):
    _name = "fix.fx.revaluation.line"
    _description = "FX Revaluation Line"
    _order = "id"

    run_id = fields.Many2one("fix.fx.revaluation", required=True, ondelete="cascade", index=True)
    move_line_id = fields.Many2one("account.move.line", string="Journal item", ondelete="set null")
    account_id = fields.Many2one("account.account", string="Account", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    foreign_currency_id = fields.Many2one("res.currency", string="Currency")
    foreign_balance = fields.Monetary(
        string="Foreign balance", currency_field="foreign_currency_id"
    )
    old_base = fields.Monetary(string="Booked (BDT)", currency_field="currency_id")
    closing_rate = fields.Float(string="Closing rate", digits=(12, 6))
    new_base = fields.Monetary(string="Restated (BDT)", currency_field="currency_id")
    gain_loss = fields.Monetary(string="Gain / (loss)", currency_field="currency_id")
    currency_id = fields.Many2one(related="run_id.currency_id", store=True)
