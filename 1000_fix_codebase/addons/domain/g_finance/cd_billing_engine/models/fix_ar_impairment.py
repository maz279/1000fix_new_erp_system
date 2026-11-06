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
#   * the entry posts through the M19 API (BRU-ARB-23), source "impairment";
#   * M20-5: the rates come from fix.ar.ecl.rate, an effective-dated master
#     approved by a second person, stamped onto the run by Compute; a run with
#     no approved set in force is refused rather than given rates.
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
    "company_id",
    "currency_id",
)
RATE_FIELDS = ("rate_current", "rate_1_30", "rate_31_60", "rate_61_90", "rate_90_plus")


class FixArEclRate(models.Model):
    """The approved IFRS 9 loss rates (M20-5): effective-dated master data set
    by finance and approved by an Accounting Administrator who did not prepare
    it. Nothing is seeded: the rates are the company's own estimate."""

    _name = "fix.ar.ecl.rate"
    _description = "ECL Loss-Rate Set (IFRS 9)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    date_from = fields.Date(string="Effective From", required=True, tracking=True)
    date_to = fields.Date(string="Effective To", tracking=True)
    rate_current = fields.Float(
        string="Rate current (%)", digits=(6, 3), required=True, tracking=True
    )
    rate_1_30 = fields.Float(string="Rate 1-30 (%)", digits=(6, 3), required=True, tracking=True)
    rate_31_60 = fields.Float(string="Rate 31-60 (%)", digits=(6, 3), required=True, tracking=True)
    rate_61_90 = fields.Float(string="Rate 61-90 (%)", digits=(6, 3), required=True, tracking=True)
    rate_90_plus = fields.Float(string="Rate 90+ (%)", digits=(6, 3), required=True, tracking=True)
    basis_note = fields.Text(
        string="Basis", required=True, help="The loss history or policy these rates come from."
    )
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(string="Approved On", readonly=True, copy=False)

    _LOCKED = (*RATE_FIELDS, "date_from", "company_id", "basis_note")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by_id", "approved_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self._LOCKED)
        return locked

    def write(self, vals):
        locked = set(self._LOCKED) & set(vals)
        if locked and not self._fix_guard_open() and self.filtered(lambda r: r.state != "draft"):
            raise UserError(
                "An approved rate set is fixed: retire it and approve a new one from the date "
                "the rates change."
            )
        return super().write(vals)

    @api.constrains(*RATE_FIELDS, "date_from", "date_to")
    def _check_rates(self):
        for rec in self:
            if not all(0.0 <= rec[f] <= 100.0 for f in RATE_FIELDS):
                raise UserError("A loss rate is a percentage between 0 and 100.")
            if rec.date_to and rec.date_to < rec.date_from:
                raise UserError("A rate set cannot end before it starts.")

    def _overlapping(self):
        self.ensure_one()
        for other in self.search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("state", "=", "approved"),
            ]
        ):
            if (not self.date_to or other.date_from <= self.date_to) and (
                not other.date_to or self.date_from <= other.date_to
            ):
                return other
        return self.browse()

    def action_approve(self):
        """The checker: an Accounting Administrator who did not prepare the set."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft rate set is approved.")
            if not self.env.su:
                require_role(self.env, GROUP_ADMINISTRATOR, "Approving IFRS 9 loss rates")
                if rec.create_uid == self.env.user:
                    raise UserError(
                        "Segregation of duties: you prepared %s; another Accounting "
                        "Administrator approves it." % rec.name
                    )
            clash = rec._overlapping()
            if clash:
                raise UserError(
                    "%s overlaps the approved set %s: end that one first." % (rec.name, clash.name)
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_retire(self, reason=""):
        """End an approved set; new runs need another one in force."""
        require_role(self.env, GROUP_ADMINISTRATOR, "Retiring IFRS 9 loss rates")
        if not (reason or "").strip():
            raise UserError("State why the rate set is retired.")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved rate set is retired.")
            rec._guarded().write({"state": "retired"})
            rec.message_post(body="Retired by %s: %s" % (self.env.user.name, reason))
        return True

    @api.model
    def _fix_in_force(self, company, on_date):
        return self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("state", "=", "approved"),
                ("date_from", "<=", on_date),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", on_date),
            ],
            order="date_from desc",
            limit=1,
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
    # IFRS 9 simplified approach: a loss rate per ageing bucket, stamped by
    # Compute from the approved master in force at the as-of date (M20-5)
    rate_set_id = fields.Many2one(
        "fix.ar.ecl.rate", string="Approved Loss Rates", readonly=True, copy=False
    )
    rate_current = fields.Float(string="Rate current (%)", readonly=True, digits=(6, 3))
    rate_1_30 = fields.Float(string="Rate 1-30 (%)", readonly=True, digits=(6, 3))
    rate_31_60 = fields.Float(string="Rate 31-60 (%)", readonly=True, digits=(6, 3))
    rate_61_90 = fields.Float(string="Rate 61-90 (%)", readonly=True, digits=(6, 3))
    rate_90_plus = fields.Float(string="Rate 90+ (%)", readonly=True, digits=(6, 3))
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
            "rate_set_id",
            *RATE_FIELDS,
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
        rates = self.env["fix.ar.ecl.rate"]._fix_in_force(self.company_id, self.as_of)
        if not rates:
            raise UserError(
                "No approved ECL loss-rate set is in force for %s on %s: Finance prepares one "
                "and a second Accounting Administrator approves it (M20 ECL Loss Rates)."
                % (self.company_id.name, self.as_of)
            )
        self._guarded().write({"rate_set_id": rates.id, **{f: rates[f] for f in RATE_FIELDS}})
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
        self._guarded().write({"move_id": move.id, "state": "posted", "posted_by_id": self.env.uid})
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
