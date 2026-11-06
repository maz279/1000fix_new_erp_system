# IFRS 9 expected-credit-loss provision for receivables. The ageing is measured from
# the real invoice due dates; the provision is loss-rate x exposure per bucket and is
# posted as an impairment entry (Dr impairment expense / Cr provision).
#
# A08 remediation (B4, F6 / M20-5): the run belonged to every internal user
# (base.group_user create/write) — a plain user created a "posted" run that the
# P03 ECL report displayed, a typed `existing_provision` drove a BDT 994,250
# release to the GL, and one accountant set the rates and posted. Now:
#   * finance roles only (ACL); state, figures, lines and stamps are guarded;
#   * the bucket lines and `existing_provision` are MEASURED by Compute (the
#     provision already booked is read from the GL, and read again at Post);
#   * the rates are frozen once computed; posting is a review by an
#     Accounting Administrator who neither created nor computed the run;
#   * the entry posts through the M19 API (BRU-ARB-23), source "impairment".
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_finance_approval import GROUP_ACCOUNTANT, GROUP_ADMINISTRATOR, require_role

BUCKETS = [
    ("current", "Current", 0, 0),
    ("d1_30", "1-30 days", 1, 30),
    ("d31_60", "31-60 days", 31, 60),
    ("d61_90", "61-90 days", 61, 90),
    ("d90_plus", "90+ days", 91, 100000),
]

RUN_INPUTS = (
    "as_of",
    "journal_id",
    "expense_account_id",
    "provision_account_id",
    "rate_current",
    "rate_1_30",
    "rate_31_60",
    "rate_61_90",
    "rate_90_plus",
    "company_id",
    "currency_id",
)


class FixArImpairment(models.Model):
    _name = "fix.ar.impairment"
    _description = "AR Impairment (IFRS 9 ECL)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
        readonly=True,
        help="Measured by Compute (and again at Post) from the posted balance of the "
        "provision account at the as-of date. Never typed.",
    )
    movement = fields.Monetary(compute="_compute_totals", store=True, currency_field="currency_id")
    move_id = fields.Many2one("account.move", string="Posted entry", readonly=True, copy=False)
    computed_by_id = fields.Many2one("res.users", string="Computed By", readonly=True, copy=False)
    computed_at = fields.Datetime(string="Computed On", readonly=True, copy=False)
    posted_by_id = fields.Many2one(
        "res.users", string="Reviewed & Posted By", readonly=True, copy=False
    )
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("posted", "Posted")],
        required=True,
        default="draft",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "move_id",
            "existing_provision",
            "line_ids",
            "computed_by_id",
            "computed_at",
            "posted_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(RUN_INPUTS)
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            touched = set(RUN_INPUTS) & set(vals)
            if touched and self.filtered(lambda r: r.state != "draft"):
                raise UserError(
                    "Run %s is computed: its rates, accounts and date are fixed. Open a new run "
                    "to provision on other terms." % ", ".join(self.mapped("name"))
                )
        return super().write(vals)

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
                    self.env["ir.sequence"].sudo().next_by_code("fix.ar.impairment") or "ECL/New"
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

    def _booked_provision(self):
        """The credit balance of the provision account at the as-of date (GL)."""
        self.ensure_one()
        if not self.provision_account_id:
            return 0.0
        lines = (
            self.env["account.move.line"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("parent_state", "=", "posted"),
                    ("account_id", "=", self.provision_account_id.id),
                    ("date", "<=", self.as_of),
                ]
            )
        )
        return -round(sum(lines.mapped("balance")), 2)

    def action_compute(self):
        """Age every open invoice by (as-of - due date) and apply the bucket rate."""
        self.ensure_one()
        require_role(self.env, GROUP_ACCOUNTANT, "Computing the IFRS 9 provision")
        if self.state == "posted":
            raise UserError("Run %s is posted; open a new run" % self.name)
        self.line_ids.sudo().unlink()
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
        Line = self.env["fix.ar.impairment.line"].sudo()
        for key, label, _lo, _hi in BUCKETS:
            exposure = round(totals[key], 2)
            rate = self._rate_for(key)
            Line.create(
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
        self._guarded().write(
            {
                "existing_provision": self._booked_provision(),
                "state": "computed",
                "computed_by_id": self.env.uid,
                "computed_at": fields.Datetime.now(),
            }
        )

    def action_post(self):
        """The review: an Accounting Administrator who neither created nor
        computed the run posts the movement through the M19 API."""
        self.ensure_one()
        if self.state != "computed":
            raise UserError("Compute the provision before posting it")
        if not self.env.su:
            require_role(self.env, GROUP_ADMINISTRATOR, "Posting the IFRS 9 provision")
            if self.env.user in (self.create_uid | self.computed_by_id):
                raise UserError(
                    "Segregation of duties: you prepared or computed %s; another Accounting "
                    "Administrator reviews and posts it." % self.name
                )
        if not (self.expense_account_id and self.provision_account_id):
            raise UserError("Set the impairment expense and provision accounts first")
        if self.move_id:
            raise UserError("This provision run is already posted")
        # the GL may have moved since Compute (a write-off used the allowance):
        # the booked figure is read again, never carried from a typed value
        booked = self._booked_provision()
        if abs(booked - (self.existing_provision or 0.0)) > 0.005:
            self._guarded().write({"existing_provision": booked})
        if abs(self.movement) < 0.01:
            raise UserError("The provision is unchanged — nothing to post")
        amount = abs(self.movement)
        expense = self.expense_account_id
        provision = self.provision_account_id
        if self.movement > 0:
            debit, credit = expense, provision
        else:
            debit, credit = provision, expense
        dims = self.env["fix.ar.invoice"]._ar_posting_dims()
        move_vals = {
            "move_type": "entry",
            "journal_id": self.journal_id.id,
            "company_id": self.company_id.id,
            "date": self.as_of,
            "ref": "IFRS 9 ECL provision %s" % self.name,
            "line_ids": [
                (0, 0, {"account_id": debit.id, "debit": amount, "name": "ECL provision movement"}),
                (
                    0,
                    0,
                    {"account_id": credit.id, "credit": amount, "name": "ECL provision movement"},
                ),
            ],
        }
        Move = self.env["account.move"]
        if hasattr(Move, "_fix_post_via_m19"):
            move = Move._fix_post_via_m19(
                move_vals, "impairment", source_ref=self.name, dimension_by_line={0: dims, 1: dims}
            )
        else:
            from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

            move, _dims = post_with_dimensions(self.env, move_vals, {0: dims, 1: dims}, source="ar")
        self._guarded().write(
            {"move_id": move.id, "state": "posted", "posted_by_id": self.env.uid}
        )
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
