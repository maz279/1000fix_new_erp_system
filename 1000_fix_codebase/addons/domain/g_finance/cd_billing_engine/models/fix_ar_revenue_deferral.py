# fix_ar_revenue_deferral — A05 FIN-14 / M13-17: revenue earned over a
# service period is deferred at issue and released straight-line over it.
#
# A rental invoiced at hand-over for a 30-day hire credited the whole rental
# to revenue on the issue day (fix_billing_engine.py `_revenue_role`: only
# subscription / contract sources deferred). IFRS 15.35(a): the customer
# consumes the hire as it runs, so the revenue is recognised over the period.
#
# Generic and opt-in (the billing engine knows no rental model):
#   * the SOURCE model opts in with the class attribute
#       _fix_defer_revenue = True
#   * each invoice LINE that is earned over a period carries
#       service_period_start / service_period_end (dates, both inclusive)
#     (`_fix_ar_invoice_from_source` / `_fix_draft_invoice_from_source` take
#     them as keys of each line dict).
# At issue, the ordinary issue entry credits the invoice's revenue account
# (e.g. the rental income account the caller passed as credit_account); a
# deferral entry then moves the period lines' ex-VAT value to the contract
# liability (cd_billing_engine.account_code.deferred_revenue — fail closed),
# one fix.ar.revenue.deferral per line. The daily job releases each one
# straight-line by day up to the Dhaka business day: Dr contract liability /
# Cr the invoice's revenue account. A credit note releases its revenue share
# at once (it debited revenue); a cancellation releases what is left (the
# cancellation reversed revenue in full). Lines with no period (a late fee,
# a damage charge) stay recognised at issue.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from . import fix_billing_engine  # noqa: F401 - load order (extends its models)

DHAKA = "Asia/Dhaka"


def _round(value) -> float:
    return round(float(value or 0.0) + 0.0, 2)


class FixArInvoiceLineServicePeriod(models.Model):
    _inherit = "fix.ar.invoice.line"

    service_period_start = fields.Date(
        string="Service Period From",
        help="Revenue earned over a period (a rental hire): first day of the period. With "
        "the end date and a source that defers revenue, the line's value is released "
        "straight-line over the period.",
    )
    service_period_end = fields.Date(string="Service Period To")

    @api.constrains("service_period_start", "service_period_end")
    def _check_service_period(self):
        for line in self:
            start, end = line.service_period_start, line.service_period_end
            if bool(start) != bool(end):
                raise ValidationError(
                    "Line '%s': a service period has both a first and a last day."
                    % (line.description or line.id)
                )
            if start and end < start:
                raise ValidationError(
                    "Line '%s': the service period ends (%s) before it starts (%s)."
                    % (line.description or line.id, end, start)
                )


class FixArInvoiceRevenueDeferral(models.Model):
    _inherit = "fix.ar.invoice"

    revenue_deferral_ids = fields.One2many(
        "fix.ar.revenue.deferral", "invoice_id", string="Revenue Deferrals", readonly=True
    )

    def _fix_defers_by_period(self) -> bool:
        """The source opted in (class attribute _fix_defer_revenue) and the
        invoice is not already a contract-liability invoice."""
        self.ensure_one()
        model = self.source_model or ""
        if model in self.DEFERRED_SOURCES or model not in self.env:
            return False
        return bool(getattr(type(self.env[model]), "_fix_defer_revenue", False))

    def _fix_deferrable_lines(self):
        self.ensure_one()
        return self.line_ids.filtered(
            lambda ln: ln.service_period_start and ln.service_period_end and ln.taxable_amount > 0
        )

    def _post_issue_gl(self):
        result = super()._post_issue_gl()
        for inv in self:
            if inv.posted_move_id and inv._fix_defers_by_period():
                inv._fix_defer_period_revenue()
        return result

    def _fix_defer_period_revenue(self):
        """Move the period lines' value from revenue to the contract
        liability, once (idempotent on the invoice line)."""
        from .fix_ar_engine import _ar_account, _ar_journal, _post_ar_move

        self.ensure_one()
        Deferral = self.env["fix.ar.revenue.deferral"].sudo()
        lines = self._fix_deferrable_lines() - Deferral.search(
            [("invoice_line_id", "in", self.line_ids.ids)]
        ).mapped("invoice_line_id")
        if not lines:
            return Deferral
        company = self.company_id
        deferred = _ar_account(self.env, company, "deferred_revenue")
        revenue = self._revenue_account()
        if not (deferred and revenue):
            raise UserError(
                "Invoice %s bills a service period, so its revenue is deferred over the period "
                "(IFRS 15), but company %s has no contract-liability account: set the system "
                "parameter cd_billing_engine.account_code.deferred_revenue. Nothing is "
                "recognised up front instead." % (self.name, company.name)
            )
        # loyalty reduces revenue, never VAT first (same split as the issue)
        revenue_credit = max(self.total_payable - self.vat_amount, 0.0)
        scale = (revenue_credit / self.taxable_amount) if self.taxable_amount > 0 else 0.0
        scale = min(scale, 1.0)
        created = Deferral
        for line in lines:
            amount = _round(line.taxable_amount * scale)
            if amount <= 0:
                continue
            created |= Deferral.create(
                {
                    "invoice_id": self.id,
                    "invoice_line_id": line.id,
                    "company_id": company.id,
                    "operating_unit_id": self.operating_unit_id.id,
                    "branch_id": self.branch_id.id or False,
                    "currency_id": self.currency_id.id,
                    "deferred_account_id": deferred.id,
                    "revenue_account_id": revenue.id,
                    "start_date": line.service_period_start,
                    "end_date": line.service_period_end,
                    "amount": amount,
                }
            )
        total = _round(sum(created.mapped("amount")))
        if total <= 0:
            return created
        if not _ar_journal(self.env, company):
            raise UserError(
                "Revenue deferral refused: company %s has no general journal." % company.name
            )
        move, note = _post_ar_move(
            self.env,
            company,
            self.invoice_date,
            "DEFER INV %s — revenue over the service period" % self.name,
            [
                (revenue.id, "Revenue deferred over the service period", total, 0.0, False),
                (deferred.id, "Contract liability (service period)", 0.0, total, False),
            ],
            dict.fromkeys(range(2), created[:1]._fix_dims()),
            source="ar",
        )
        if not move:
            raise UserError("Revenue deferral of %s refused: %s" % (self.name, note))
        for deferral in created:
            deferral._log(move, "defer", deferral.amount, self.invoice_date)
        # the part of the period already run is earned now
        created._fix_release()
        return created

    def action_cancel(self, reason=""):
        result = super().action_cancel(reason=reason)
        for inv in self.filtered(lambda i: i.state == "cancelled"):
            inv.revenue_deferral_ids.sudo()._fix_close("cancel")
        return result


class FixCreditNoteRevenueDeferral(models.Model):
    _inherit = "fix.credit.note"

    def _post_credit_gl(self, *args, **kwargs):
        # A02 pass 2 gave the base an on_date (Dhaka GL date): pass it through
        result = super()._post_credit_gl(*args, **kwargs)
        for note in self:
            invoice = note.invoice_id
            deferrals = invoice.revenue_deferral_ids.sudo().filtered(lambda d: d.state == "active")
            if not (note.posted_move_id and deferrals):
                continue
            revenue_part, _vat = note._vat_split()
            # the credit's share of the period lines (a credit of a late fee
            # line leaves the hire's deferral alone in proportion)
            invoice_revenue = max(invoice.total_payable - invoice.vat_amount, 0.0)
            deferred_total = sum(invoice.revenue_deferral_ids.sudo().mapped("amount"))
            share = (
                revenue_part * min(deferred_total / invoice_revenue, 1.0)
                if invoice_revenue > 0
                else 0.0
            )
            deferrals._fix_credit(_round(share), note)
        return result


class FixArRevenueDeferral(models.Model):
    """One invoice line's revenue, deferred over its service period."""

    _name = "fix.ar.revenue.deferral"
    _description = "AR Revenue Deferral (service period)"
    _inherit = ["mail.thread"]
    _order = "start_date desc, id desc"

    _line_unique = models.Constraint(
        "UNIQUE (invoice_line_id)", "An invoice line is deferred once."
    )

    invoice_id = fields.Many2one(
        "fix.ar.invoice", required=True, index=True, ondelete="restrict", readonly=True
    )
    invoice_line_id = fields.Many2one(
        "fix.ar.invoice.line", required=True, index=True, ondelete="restrict", readonly=True
    )
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", index=True, readonly=True)
    branch_id = fields.Many2one("fix.branch", readonly=True)
    currency_id = fields.Many2one("res.currency", required=True, readonly=True)
    deferred_account_id = fields.Many2one("account.account", required=True, readonly=True)
    revenue_account_id = fields.Many2one("account.account", required=True, readonly=True)
    start_date = fields.Date(required=True, readonly=True)
    end_date = fields.Date(required=True, readonly=True)
    amount = fields.Monetary(
        string="Deferred", currency_field="currency_id", required=True, readonly=True
    )
    state = fields.Selection(
        [("active", "Releasing"), ("done", "Fully Released"), ("cancelled", "Closed by Cancel")],
        default="active",
        required=True,
        readonly=True,
    )
    log_ids = fields.One2many(
        "fix.ar.revenue.deferral.log", "deferral_id", string="Postings", readonly=True
    )
    released_amount = fields.Monetary(
        string="Released", currency_field="currency_id", compute="_compute_balances", store=True
    )
    credited_amount = fields.Monetary(
        string="Credited", currency_field="currency_id", compute="_compute_balances", store=True
    )
    balance = fields.Monetary(
        string="Still Deferred",
        currency_field="currency_id",
        compute="_compute_balances",
        store=True,
    )

    @api.depends("amount", "log_ids.amount", "log_ids.kind")
    def _compute_balances(self):
        for rec in self:
            released = sum(rec.log_ids.filtered(lambda lg: lg.kind == "release").mapped("amount"))
            credited = sum(
                rec.log_ids.filtered(lambda lg: lg.kind in ("credit", "cancel")).mapped("amount")
            )
            rec.released_amount = _round(released)
            rec.credited_amount = _round(credited)
            rec.balance = _round(rec.amount - released - credited)

    def _fix_dims(self):
        self.ensure_one()
        dims = dict(self.invoice_id._ar_posting_dims(self.branch_id.id))
        unit = self.operating_unit_id
        branch_unit = self.branch_id.operating_unit_id
        if unit and not dims.get("operating_unit_id") and (not branch_unit or branch_unit == unit):
            dims["operating_unit_id"] = unit.id
        return dims

    def _log(self, move, kind, amount, on_date):
        self.ensure_one()
        return (
            self.env["fix.ar.revenue.deferral.log"]
            .sudo()
            .create(
                {
                    "deferral_id": self.id,
                    "kind": kind,
                    "date": on_date,
                    "amount": amount,
                    "move_id": move.id if move else False,
                }
            )
        )

    def _post(self, amount, on_date, ref, kind):
        """Dr contract liability / Cr revenue (a release); written once."""
        from .fix_ar_engine import _post_ar_move

        self.ensure_one()
        move, note = _post_ar_move(
            self.env,
            self.company_id,
            on_date,
            ref,
            [
                (self.deferred_account_id.id, "Contract liability released", amount, 0.0, False),
                (self.revenue_account_id.id, "Revenue earned (service period)", 0.0, amount, False),
            ],
            dict.fromkeys(range(2), self._fix_dims()),
            source="ar",
        )
        if not move:
            raise UserError("Revenue release of %s refused: %s" % (self.invoice_id.name, note))
        self._log(move, kind, amount, on_date)
        return move

    def _earned_until(self, as_of) -> float:
        """Straight-line target (by day, both ends inclusive) of what is
        earned by `as_of`, on the value not credited."""
        self.ensure_one()
        if as_of < self.start_date:
            return 0.0
        term = (self.end_date - self.start_date).days + 1
        run = (min(as_of, self.end_date) - self.start_date).days + 1
        base = self.amount - self.credited_amount
        return _round(base * run / term) if run < term else _round(base)

    def _fix_release(self, as_of=None):
        """Release each active deferral up to `as_of` (default: the Dhaka
        business day). Cumulative and idempotent: a re-run releases nothing
        new."""
        today = fields.Date.context_today(self.with_context(tz=DHAKA))
        as_of = as_of or today
        for rec in self.sudo().filtered(lambda d: d.state == "active"):
            delta = _round(min(rec._earned_until(as_of), rec.amount - rec.credited_amount))
            delta = _round(delta - rec.released_amount)
            if delta > 0:
                on_date = max(min(as_of, rec.end_date), rec.invoice_id.invoice_date)
                rec._post(
                    delta,
                    on_date,
                    "REV-REL INV %s — %s..%s" % (rec.invoice_id.name, rec.start_date, on_date),
                    "release",
                )
                rec.invalidate_recordset(["released_amount", "credited_amount", "balance"])
            if rec.balance <= 0.005:
                rec.write({"state": "done"})
        return True

    def _fix_credit(self, revenue_part, note):
        """A credit note debited revenue: release that much of what is still
        deferred, at once, so the liability never outlives the revenue."""
        left = revenue_part
        for rec in self.filtered(lambda d: d.state == "active"):
            if left <= 0:
                break
            part = _round(min(left, rec.balance))
            if part <= 0:
                continue
            rec._post(
                part,
                fields.Date.context_today(rec.with_context(tz=DHAKA)),
                "REV-CN INV %s — credit note #%s" % (rec.invoice_id.name, note.id),
                "credit",
            )
            rec.invalidate_recordset(["released_amount", "credited_amount", "balance"])
            left = _round(left - part)
            if rec.balance <= 0.005:
                rec.write({"state": "done"})

    def _fix_close(self, kind):
        """The invoice was cancelled (its revenue reversed in full): release
        what is still deferred, so revenue and the liability both net to 0."""
        for rec in self.filtered(lambda d: d.state == "active"):
            if rec.balance > 0.005:
                rec._post(
                    rec.balance,
                    fields.Date.context_today(rec.with_context(tz=DHAKA)),
                    "REV-CANCEL INV %s" % rec.invoice_id.name,
                    kind,
                )
            rec.write({"state": "cancelled"})

    @api.model
    def _cron_release(self):
        """Daily: release every active deferral up to today (Dhaka)."""
        done = 0
        for rec in self.sudo().search([("state", "=", "active")]):
            try:
                with self.env.cr.savepoint():
                    rec._fix_release()
                    done += 1
            except UserError as exc:
                rec.message_post(body="Revenue release refused: %s" % exc)
        return done


class FixArRevenueDeferralLog(models.Model):
    """One posting of a deferral: the deferral itself, a release, a credit
    note's share or the cancellation close."""

    _name = "fix.ar.revenue.deferral.log"
    _description = "AR Revenue Deferral Posting"
    _order = "date desc, id desc"

    deferral_id = fields.Many2one(
        "fix.ar.revenue.deferral", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="deferral_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="deferral_id.operating_unit_id", store=True)
    currency_id = fields.Many2one(related="deferral_id.currency_id")
    kind = fields.Selection(
        [
            ("defer", "Deferred at Issue"),
            ("release", "Released (straight-line)"),
            ("credit", "Released by Credit Note"),
            ("cancel", "Released by Cancellation"),
        ],
        required=True,
    )
    date = fields.Date(required=True)
    amount = fields.Monetary(currency_field="currency_id", required=True)
    move_id = fields.Many2one("account.move", string="GL Entry")

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("Revenue deferral postings are written by the billing engine only.")
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("A revenue deferral posting is never edited.")
