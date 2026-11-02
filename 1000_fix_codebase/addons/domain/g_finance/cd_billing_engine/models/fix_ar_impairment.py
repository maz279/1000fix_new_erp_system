# IFRS 9 expected-credit-loss provision for receivables. The ageing is measured from
# the real invoice due dates; the provision is loss-rate x exposure per bucket and is
# posted as an impairment entry (Dr impairment expense / Cr provision).
from odoo import api, fields, models
from odoo.exceptions import UserError

BUCKETS = [
    ("current", "Current", 0, 0),
    ("d1_30", "1-30 days", 1, 30),
    ("d31_60", "31-60 days", 31, 60),
    ("d61_90", "61-90 days", 61, 90),
    ("d90_plus", "90+ days", 91, 100000),
]


class FixArImpairment(models.Model):
    _name = "fix.ar.impairment"
    _description = "AR Impairment (IFRS 9 ECL)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "as_of desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    as_of = fields.Date(required=True, default=fields.Date.context_today)
    journal_id = fields.Many2one("account.journal", string="Journal", required=True)
    expense_account_id = fields.Many2one("account.account", string="Impairment expense account")
    provision_account_id = fields.Many2one("account.account", string="Provision account")
    # IFRS 9 simplified approach: a loss rate per ageing bucket, stated on the run
    rate_current = fields.Float(string="Rate current (%)", default=0.5)
    rate_1_30 = fields.Float(string="Rate 1-30 (%)", default=2.0)
    rate_31_60 = fields.Float(string="Rate 31-60 (%)", default=10.0)
    rate_61_90 = fields.Float(string="Rate 61-90 (%)", default=25.0)
    rate_90_plus = fields.Float(string="Rate 90+ (%)", default=50.0)
    line_ids = fields.One2many("fix.ar.impairment.line", "run_id", string="Buckets")
    total_exposure = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    total_provision = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    existing_provision = fields.Monetary(
        string="Provision already booked",
        currency_field="currency_id",
        help="Balance on the provision account for this company at the as-of date.",
    )
    movement = fields.Monetary(compute="_compute_totals", store=True, currency_field="currency_id")
    move_id = fields.Many2one("account.move", string="Posted entry", readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("posted", "Posted")],
        required=True,
        default="draft",
        tracking=True,
    )

    @api.depends("line_ids.exposure", "line_ids.provision", "existing_provision")
    def _compute_totals(self):
        for run in self:
            run.total_exposure = round(sum(ln.exposure for ln in run.line_ids), 2)
            run.total_provision = round(sum(ln.provision for ln in run.line_ids), 2)
            run.movement = round(run.total_provision - (run.existing_provision or 0.0), 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.ar.impairment") or "ECL/New"
                )
        return super().create(vals_list)

    def _rate_for(self, key):
        return {
            "current": self.rate_current,
            "d1_30": self.rate_1_30,
            "d31_60": self.rate_31_60,
            "d61_90": self.rate_61_90,
            "d90_plus": self.rate_90_plus,
        }[key]

    def action_compute(self):
        """Age every open invoice by (as-of - due date) and apply the bucket rate."""
        self.ensure_one()
        self.line_ids.unlink()
        Invoice = self.env["fix.ar.invoice"].sudo()
        invoices = Invoice.search(
            [
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("issued", "part_paid", "overdue")),
            ]
        )
        totals = {k: 0.0 for k, *_ in BUCKETS}
        for inv in invoices:
            issued = inv.invoice_date
            if not issued:
                continue
            # due date = invoice date + the customer's own credit terms (same basis
            # the AR ageing uses, so the two figures cannot disagree)
            try:
                terms = inv._payment_terms_days()
            except Exception:
                terms = 0
            days = (self.as_of - issued).days - terms
            # not yet due (or due today) is 'current'; beyond 90 days is the tail
            if days <= 0:
                key = "current"
            else:
                key = next((k for k, _l, lo, hi in BUCKETS if lo <= days <= hi), "d90_plus")
            outstanding = inv.amount_residual or 0.0
            if outstanding <= 0:
                continue
            totals[key] += outstanding
        for key, label, _lo, _hi in BUCKETS:
            exposure = round(totals[key], 2)
            rate = self._rate_for(key)
            self.env["fix.ar.impairment.line"].create(
                {
                    "run_id": self.id,
                    "bucket": key,
                    "bucket_label": label,
                    "exposure": exposure,
                    "rate": rate,
                    "provision": round(exposure * rate / 100.0, 2),
                }
            )
        # what is already on the provision account (so the run posts only the movement)
        if self.provision_account_id:
            lines = self.env["account.move.line"].search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("parent_state", "=", "posted"),
                    ("account_id", "=", self.provision_account_id.id),
                    ("date", "<=", self.as_of),
                ]
            )
            self.existing_provision = -round(sum(lines.mapped("balance")), 2)
        self.state = "computed"

    def action_post(self):
        self.ensure_one()
        if self.state != "computed":
            raise UserError("Compute the provision before posting it")
        if not (self.expense_account_id and self.provision_account_id):
            raise UserError("Set the impairment expense and provision accounts first")
        if self.move_id:
            raise UserError("This provision run is already posted")
        if abs(self.movement) < 0.01:
            raise UserError("The provision is unchanged — nothing to post")
        amount = abs(self.movement)
        expense = self.expense_account_id
        provision = self.provision_account_id
        if self.movement > 0:
            debit, credit = expense, provision
        else:
            debit, credit = provision, expense
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": self.journal_id.id,
                "date": self.as_of,
                "ref": "IFRS 9 ECL provision %s" % self.name,
                "line_ids": [
                    (
                        0,
                        0,
                        {"account_id": debit.id, "debit": amount, "name": "ECL provision movement"},
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": credit.id,
                            "credit": amount,
                            "name": "ECL provision movement",
                        },
                    ),
                ],
            }
        )
        move.action_post()
        self.write({"move_id": move.id, "state": "posted"})
        return move


class FixArImpairmentLine(models.Model):
    _name = "fix.ar.impairment.line"
    _description = "AR Impairment Bucket"
    _order = "id"

    run_id = fields.Many2one("fix.ar.impairment", required=True, ondelete="cascade", index=True)
    bucket = fields.Char(required=True)
    bucket_label = fields.Char(required=True)
    exposure = fields.Monetary(currency_field="currency_id")
    rate = fields.Float(string="Loss rate (%)", digits=(6, 3))
    provision = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(related="run_id.currency_id", store=True)
