# cd_front_desk_finance — the drawer's counted variance reaches the GL.
#
# E2E2 flow 2 (11 Nov 2026, copy of fix_real): the blind count found shift #11
# BDT 350 short; a branch manager approved the -350 from the M63 inbox and a
# second manager reconciled the shift to "discrepancy". Nothing posted: the
# drawer cash account (100108) kept 350 the drawer did not hold, and 500902
# Cash Shortage stayed at zero.
#
# Reconciling a shift with a variance (beyond tolerance it is approved first,
# BRU-FRD-03; within tolerance it needs no approval, but the cash is still
# short or over) now posts one entry through M19, as the counter bridge posts
# a sale:
#   shortage  Dr cash shortage       / Cr drawer cash
#   overage   Dr drawer cash         / Cr cash overage
# on the Bangladesh day of the reconcile (the day the difference is accepted),
# with the branch's dimensions, as the system on behalf of the reconciling
# manager (he holds no accounting role).
#
# Accounts (the first key set decides; a code not in the chart fails closed):
#   drawer cash  cd_cash_position.account_code.branch_cash — the account the
#                counter sale debits and the M50 deposit credits — else the
#                billing engine's cash account
#   shortage     cd_front_desk_finance.account_code.cash_shortage, else
#                cd_cash_position.account_code.cash_shortage (500902 on
#                fix_real)
#   overage      cd_front_desk_finance.account_code.cash_overage, else the same
#                cd_cash_position cash_shortage account: the treasury role is
#                "Cash shortage / over" and the M50 deposit already books an
#                over-credit there. No overage / other-income parameter exists
#                on fix_real (owner decision: 400303 Excess In Till exists).
#
# Pending, never lost, never blocking: an account that does not resolve rolls
# the posting back on its own savepoint; the reconcile stands, the shift is
# marked pending with the reason, and Retry Variance Posting or the hourly job
# posts it once configured. The shift row is locked while it posts and the
# entry is linked before anything else can run, so nothing posts twice.
from __future__ import annotations

import logging

from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_ar_engine import _ar_journal
from odoo.addons.cd_front_desk.models.fix_cash_shift import FINAL_STATES
from odoo.exceptions import UserError

from .fix_counter_sale_posting import RETRY_GROUPS, _message, resolve_account
from .fix_engine_ext import SHIFT_SOURCE

_logger = logging.getLogger(__name__)

DHAKA = "Asia/Dhaka"
VARIANCE_POSTING_STATES = [
    ("none", "Nothing to Post"),
    ("pending", "Pending Posting"),
    ("posted", "Posted"),
]
VARIANCE_FIELDS = {
    "variance_posting_state",
    "variance_posting_note",
    "variance_posting_attempted_at",
    "variance_move_id",
    "variance_account_id",
}


class FixCashShiftPosting(models.Model):
    _inherit = "fix.cash.shift"

    variance_posting_state = fields.Selection(
        VARIANCE_POSTING_STATES,
        string="Variance in GL",
        default="none",
        required=True,
        readonly=True,
        copy=False,
        index=True,
        help="Whether the reconciled drawer variance reached the GL (Dr cash shortage / Cr "
        "drawer cash, or the reverse for an overage). Pending: see the note; Retry Variance "
        "Posting and the hourly job post it once the cause is fixed.",
    )
    variance_posting_note = fields.Text(string="Variance Posting Note", readonly=True, copy=False)
    variance_posting_attempted_at = fields.Datetime(
        string="Last Variance Posting Run", readonly=True, copy=False
    )
    variance_move_id = fields.Many2one(
        "account.move", string="Variance GL Entry", readonly=True, copy=False, index=True
    )
    variance_account_id = fields.Many2one(
        "account.account",
        string="Shortage / Overage Account",
        readonly=True,
        copy=False,
    )

    def _fix_guarded_fields(self) -> set:
        # the posting outcome is the system's: nobody types it
        return super()._fix_guarded_fields() | VARIANCE_FIELDS

    # ------------------------------------------------------------ transitions
    def action_reconcile(self):
        result = super().action_reconcile()
        self._cdff_post_variance()
        return result

    def action_retry_variance_posting(self):
        """Post a reconciled variance the GL still owes (idempotent)."""
        if not (self.env.su or any(self.env.user.has_group(g) for g in RETRY_GROUPS)):
            raise UserError(
                "Only front-desk or finance staff may retry a shift's variance posting."
            )
        self._cdff_post_variance()
        return True

    @api.model
    def _cron_retry_variance_postings(self, limit=200):
        """Hourly: post every reconciled variance still pending (a shift
        reconciled before this bridge was installed is left alone: its state
        is 'none' and its date may be in a closed period)."""
        shifts = self.sudo().search(
            [("state", "in", FINAL_STATES), ("variance_posting_state", "=", "pending")],
            order="variance_posting_attempted_at asc, id asc",
            limit=limit,
        )
        shifts._cdff_post_variance()
        return len(shifts)

    # ---------------------------------------------------------------- engine
    def _cdff_variance_owed(self) -> bool:
        self.ensure_one()
        return (
            self.state in FINAL_STATES
            and abs(round(self.variance or 0.0, 2)) >= 0.01
            and not self.variance_move_id
        )

    def _cdff_post_variance(self):
        for shift in self:
            if shift.state in FINAL_STATES:
                shift._cdff_post_variance_one()

    def _cdff_post_variance_one(self):
        self.ensure_one()
        shift = self.sudo().with_company(self.company_id)
        self.env.flush_all()
        # one runner per shift: a concurrent retry waits, then finds nothing to do
        self.env.cr.execute("SELECT id FROM fix_cash_shift WHERE id = %s FOR UPDATE", [shift.id])
        shift.invalidate_recordset()
        problem = None
        if shift._cdff_variance_owed():
            try:
                with self.env.cr.savepoint():
                    shift._cdff_post_variance_move()
            except Exception as exc:
                if not isinstance(exc, UserError | ValueError):
                    _logger.exception("cash shift %s: variance posting failed", shift.id)
                problem = _message(exc)
        if shift.variance_move_id:
            new = "posted"
        elif shift._cdff_variance_owed():
            new = "pending"
        else:
            new = "none"
        note = ("Variance GL entry: %s" % problem) if problem else False
        changed = (new, note) != (
            shift.variance_posting_state,
            shift.variance_posting_note or False,
        )
        shift._guarded().write(
            {
                "variance_posting_state": new,
                "variance_posting_note": note,
                "variance_posting_attempted_at": fields.Datetime.now(),
            }
        )
        if changed and new != "none":
            label = dict(VARIANCE_POSTING_STATES)[new]
            body = (
                "Variance in GL: %s." % label
                if not note
                else "Variance in GL: %s — %s"
                % (
                    label,
                    note,
                )
            )
            shift.message_post(body=body)

    def _cdff_shift_day(self):
        tz = self.company_id.partner_id.tz or DHAKA
        return fields.Date.context_today(
            self.with_context(tz=tz), timestamp=self.reconciled_at or fields.Datetime.now()
        )

    def _cdff_post_variance_move(self):
        variance = round(self.variance, 2)
        company = self.company_id
        role = "cash_shortage" if variance < 0 else "cash_overage"
        drawer, drawer_why = resolve_account(self.env, company, "drawer_cash")
        other, other_why = resolve_account(self.env, company, role)
        missing = [why for why in (drawer_why, other_why) if why]
        if missing:
            raise UserError(" ".join(missing))
        journal = _ar_journal(self.env, company)
        if not journal:
            raise UserError(
                "No general journal in %s to post the drawer variance to." % company.name
            )
        amount = abs(variance)
        ref = "Cash shift #%s %s — drawer %s BDT %.2f (%s)" % (
            self.id,
            self.shift_date,
            "short" if variance < 0 else "over",
            amount,
            self.branch_id.display_name or "",
        )
        if variance < 0:
            lines = [
                (other, "Drawer shortage, shift #%s" % self.id, amount, 0.0),
                (drawer, "Drawer shortage, shift #%s" % self.id, 0.0, amount),
            ]
        else:
            lines = [
                (drawer, "Drawer overage, shift #%s" % self.id, amount, 0.0),
                (other, "Drawer overage, shift #%s" % self.id, 0.0, amount),
            ]
        dims = self.env["fix.ar.invoice"]._ar_posting_dims(self.branch_id.id)
        move = self.env["account.move"]._fix_post_via_m19(
            {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": self._cdff_shift_day(),
                "ref": ref,
                "line_ids": [
                    (0, 0, {"account_id": acc.id, "name": label, "debit": dr, "credit": cr})
                    for acc, label, dr, cr in lines
                ],
            },
            SHIFT_SOURCE,
            source_ref="fix.cash.shift,%s" % self.id,
            dimension_by_line={i: dict(dims) for i in range(len(lines))},
        )
        self._guarded().write({"variance_move_id": move.id, "variance_account_id": other.id})
