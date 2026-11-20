# cd_front_desk_finance — the drawer's cash-outs reach the GL.
#
# A02 pass 2 (M04-01 / X5-02, P0; owner decision D2, 20 Nov 2026): a petty
# expense, a staff advance or a safe drop posted from the drawer lowered the
# shift's expected cash and nothing else. The drawer account (100108) kept
# cash the drawer no longer held, the expense never reached the P&L, the
# advance was owed by nobody and the safe held nothing on the books; the M50
# deposit then credited the drawer for cash already gone.
#
# Posting a cash-out now posts one entry through M19, as the system on behalf
# of the cashier (she holds no accounting role):
#   petty expense   Dr expense by category / Cr drawer cash
#                     Miscellaneous  cd_front_desk_finance.account_code.petty_expense       500211
#                     Conveyance     cd_front_desk_finance.account_code.petty_conveyance    500002
#                     Entertainment  cd_front_desk_finance.account_code.petty_entertainment 500011
#   staff advance   Dr Advance Loan (Office Employee) with the employee's
#                   partner (cd_front_desk_finance.account_code.staff_advance, 100029)
#                   / Cr drawer cash
#   safe drop       Dr Cash in Safe (cd_cash_position.account_code.branch_safe,
#                   100112) / Cr drawer cash; the M50 deposit may bank the safe
#   field shortage  Dr payroll recovery with the employee's partner
#                   (cd_cash_position.account_code.rider_shortage_payroll, as
#                   the rider COD shortage) / Cr drawer cash (D20)
# on the Bangladesh day it was posted, with the branch's dimensions (the
# branch's operating unit) and the shift's company.
#
# Pending, never lost (the variance-posting pattern): an account that does not
# resolve rolls the entry back on its own savepoint; the cash-out stands, the
# movement is marked pending with the reason, and Retry Posting or the hourly
# job posts it once configured. The movement row is locked while it posts and
# the entry is linked before anything else can run, so nothing posts twice.
# Two refusals happen up front instead, because the cash would otherwise
# leave for a place the books cannot name: a safe drop when no safe account
# exists, and a staff advance whose employee has no partner to owe it.
from __future__ import annotations

import logging

from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_ar_engine import _ar_journal
from odoo.addons.cd_front_desk.models.fix_cash_movement import CASH_OUT_TYPES
from odoo.exceptions import UserError

from .fix_counter_sale_posting import RETRY_GROUPS, _message, resolve_account
from .fix_engine_ext import MOVEMENT_SOURCE
from .fix_order_cash_receipt import dhaka_today

_logger = logging.getLogger(__name__)

MOVEMENT_POSTING_STATES = [
    ("none", "Nothing to Post"),
    ("pending", "Pending Posting"),
    ("posted", "Posted"),
]
MOVEMENT_POSTING_FIELDS = {
    "posting_state",
    "posting_note",
    "posting_attempted_at",
    "move_id",
    "debit_account_id",
}
CATEGORY_ROLE = {
    "misc": "petty_expense",
    "conveyance": "petty_conveyance",
    "entertainment": "petty_entertainment",
}
# the roles whose line carries the employee as partner
PARTNER_ROLES = ("staff_advance", "payroll_recovery")


class FixCashMovementPosting(models.Model):
    _inherit = "fix.cash.movement"

    posting_state = fields.Selection(
        MOVEMENT_POSTING_STATES,
        string="In GL",
        default="none",
        required=True,
        readonly=True,
        copy=False,
        index=True,
        help="Whether the cash-out reached the GL (Dr expense / staff advance / safe / payroll "
        "recovery, Cr drawer cash). Pending: see the note; Retry Posting and the hourly job "
        "post it once the cause is fixed.",
    )
    posting_note = fields.Text(string="Posting Note", readonly=True, copy=False)
    posting_attempted_at = fields.Datetime(string="Last Posting Run", readonly=True, copy=False)
    move_id = fields.Many2one(
        "account.move", string="GL Entry", readonly=True, copy=False, index=True
    )
    debit_account_id = fields.Many2one(
        "account.account", string="Booked To", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        # the posting outcome is the system's: nobody types it
        return super()._fix_guarded_fields() | MOVEMENT_POSTING_FIELDS

    # ------------------------------------------------------------ roles
    def _cdff_debit_role(self) -> str:
        self.ensure_one()
        kind = self.movement_type
        if kind == "petty_expense":
            return CATEGORY_ROLE.get(self.expense_category or "misc", "petty_expense")
        if kind == "staff_advance":
            return "staff_advance"
        if kind == "safe_drop":
            return "branch_safe"
        if kind == "field_shortage":
            return "payroll_recovery"
        return ""

    def _cdff_partner(self):
        """The employee who owes the advance / shortage, as a ledger party."""
        self.ensure_one()
        employee = self.employee_id.sudo()
        partner = employee.work_contact_id or employee.user_id.partner_id
        if not partner:
            raise UserError(
                "%s has no work contact: an advance or a shortage is booked against the "
                "employee, so give the employee a work contact first."
                % (employee.name or "The staff member")
            )
        return partner

    # ------------------------------------------------------------ transitions
    def action_post(self):
        for rec in self:
            rec._cdff_check_before_cash_leaves()
        return super().action_post()

    def _cdff_check_before_cash_leaves(self):
        """The two cash-outs the books must be able to name before the cash
        leaves: the safe a drop goes into, the employee who owes an advance."""
        self.ensure_one()
        if self.movement_type == "safe_drop":
            company = self.shift_id.company_id
            safe, why = resolve_account(self.env, company, "branch_safe")
            if not safe:
                raise UserError(
                    "Safe drop refused: the branch safe has no GL account, so the cash would "
                    "leave the drawer for nowhere on the books. %s" % why
                )
        elif self.movement_type == "staff_advance" and self.employee_id:
            self._cdff_partner()

    def action_retry_posting(self):
        """Post a cash-out the GL still owes (idempotent)."""
        if not (self.env.su or any(self.env.user.has_group(g) for g in RETRY_GROUPS)):
            raise UserError("Only front-desk or finance staff may retry a cash-out's posting.")
        self._cdff_post_movements()
        return True

    @api.model
    def _cron_retry_movement_postings(self, limit=200):
        """Hourly: post every cash-out still pending (a movement posted before
        this bridge was installed is 'none' and left alone: its day may be in a
        closed period; finance books those by hand)."""
        moves = self.sudo().search(
            [("state", "=", "posted"), ("posting_state", "=", "pending")],
            order="posting_attempted_at asc, id asc",
            limit=limit,
        )
        moves._cdff_post_movements()
        return len(moves)

    # ---------------------------------------------------------------- engine
    def _cdff_owed(self) -> bool:
        self.ensure_one()
        return (
            self.state == "posted"
            and self.movement_type in CASH_OUT_TYPES
            and not self.move_id
            and round(self.amount or 0.0, 2) > 0
        )

    def _cdff_post_movements(self):
        for rec in self:
            if rec.state == "posted" and rec.movement_type in CASH_OUT_TYPES:
                rec._cdff_post_one()

    def _cdff_post_one(self):
        self.ensure_one()
        mv = self.sudo()
        self.env.flush_all()
        # one runner per movement: a concurrent retry waits, then finds nothing
        self.env.cr.execute("SELECT id FROM fix_cash_movement WHERE id = %s FOR UPDATE", [mv.id])
        mv.invalidate_recordset()
        problem = None
        if mv._cdff_owed():
            try:
                with self.env.cr.savepoint():
                    mv._cdff_post_move()
            except Exception as exc:
                if not isinstance(exc, UserError | ValueError):
                    _logger.exception("cash movement %s: posting failed", mv.id)
                problem = _message(exc)
        if mv.move_id:
            new = "posted"
        elif mv._cdff_owed():
            new = "pending"
        else:
            new = "none"
        note = ("GL entry: %s" % problem) if problem else False
        changed = (new, note) != (mv.posting_state, mv.posting_note or False)
        mv._guarded().write(
            {
                "posting_state": new,
                "posting_note": note,
                "posting_attempted_at": fields.Datetime.now(),
            }
        )
        if changed and new != "none":
            label = dict(MOVEMENT_POSTING_STATES)[new]
            shift = mv.shift_id
            shift.message_post(
                body="%s in GL: %s%s" % (mv.name, label, (" — %s" % note) if note else "")
            )

    def _cdff_post_move(self):
        shift = self.shift_id
        company = shift.company_id
        role = self._cdff_debit_role()
        target, target_why = resolve_account(self.env, company, role)
        drawer, drawer_why = resolve_account(self.env, company, "drawer_cash")
        missing = [why for why in (target_why, drawer_why) if why]
        if missing:
            raise UserError(" ".join(missing))
        journal = _ar_journal(self.env, company)
        if not journal:
            raise UserError("No general journal in %s to post the cash-out to." % company.name)
        partner = self._cdff_partner() if role in PARTNER_ROLES else self.env["res.partner"]
        amount = round(self.amount, 2)
        types = dict(self._fields["movement_type"].selection)
        label = "%s — %s" % (types.get(self.movement_type, ""), self.reason or "")
        ref = "Drawer cash-out %s, shift #%s %s — BDT %.2f (%s)" % (
            self.name,
            shift.id,
            shift.shift_date,
            amount,
            shift.branch_id.display_name or "",
        )
        lines = [
            (target, label, amount, 0.0, partner),
            (drawer, "Drawer cash out: %s" % self.name, 0.0, amount, self.env["res.partner"]),
        ]
        dims = self.env["fix.ar.invoice"]._ar_posting_dims(shift.branch_id.id)
        move = self.env["account.move"]._fix_post_via_m19(
            {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": self._cdff_day(),
                "ref": ref,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": acc.id,
                            "name": text,
                            "debit": dr,
                            "credit": cr,
                            "partner_id": who.id or False,
                        },
                    )
                    for acc, text, dr, cr, who in lines
                ],
            },
            MOVEMENT_SOURCE,
            source_ref="fix.cash.movement,%s" % self.id,
            dimension_by_line={i: dict(dims) for i in range(len(lines))},
        )
        self._guarded().write({"move_id": move.id, "debit_account_id": target.id})

    def _cdff_day(self):
        """The Bangladesh day the cash left the drawer."""
        if not self.posted_at:
            return dhaka_today()
        return fields.Date.context_today(
            self.with_context(tz="Asia/Dhaka"), timestamp=self.posted_at
        )


class FixCashShiftMovementPosting(models.Model):
    _inherit = "fix.cash.shift"

    def _post_cash_movement(self, field, amount, reference=None, movement=None):
        """A cash-out marked posted is booked in the same transaction."""
        result = super()._post_cash_movement(field, amount, reference=reference, movement=movement)
        if movement:
            movement.sudo()._cdff_post_movements()
        return result

    # ------------------------------------------------ D20: field cash shortage
    def _fix_book_field_cash_shortage(self, employee, amount, reference=None):
        """D20 (A02 pass 2): book a technician's field cash shortage for
        payroll recovery, like the rider COD shortage.

        On a shift (``shift._fix_book_field_cash_shortage(employee, amount,
        reference)``): the drawer took the declared field cash and less was
        handed in: the shortfall leaves the drawer (a field_shortage movement)
        and posts Dr payroll recovery (employee) / Cr drawer cash.

        On the model (``env["fix.cash.shift"]._fix_book_field_cash_shortage(
        recon, amount)``, a field cash reconciliation counting cash still with
        the technician): no drawer ever held the missing cash, so the entry is
        Dr payroll recovery (employee) / Cr cash shortage (the treasury's
        cash shortage / over account) — the loss is recognised and recovered
        from pay at once. ``employee`` may be the reconciliation record (its
        employee_id, name, company and operating unit are used).
        Idempotent on the reference. Returns the movement or the move."""
        recon = employee if employee and "employee_id" in employee._fields else None
        person = recon.employee_id if recon else employee
        ref = (reference or (recon.name if recon else "") or "").strip()
        if self:
            return super()._fix_book_field_cash_shortage(person, amount, ref)
        return self._cdff_book_field_shortage_gl(person, amount, ref, recon)

    @api.model
    def _cdff_book_field_shortage_gl(self, employee, amount, reference, recon=None):
        try:
            amount = round(float(amount or 0.0), 2)
        except (TypeError, ValueError):
            raise UserError("A field cash shortage is an amount.") from None
        if amount <= 0:
            raise UserError("A field cash shortage is a positive amount.")
        if not employee:
            raise UserError("Name the employee who owes the field cash shortage.")
        if not reference:
            raise UserError("A field cash shortage carries the reference of its reconciliation.")
        company = (recon.company_id if recon else False) or employee.company_id or self.env.company
        source_ref = "field_shortage:%s" % reference
        Log = self.env["fix.journal.posting.log"].sudo()
        done = Log.search(
            [("source", "=", MOVEMENT_SOURCE), ("source_ref", "=", source_ref)], limit=1
        )
        if done and done.move_id:
            return done.move_id
        payroll, payroll_why = resolve_account(self.env, company, "payroll_recovery")
        shortage, shortage_why = resolve_account(self.env, company, "cash_shortage")
        missing = [why for why in (payroll_why, shortage_why) if why]
        if missing:
            raise UserError(" ".join(missing))
        journal = _ar_journal(self.env, company)
        if not journal:
            raise UserError("No general journal in %s to book the shortage to." % company.name)
        employee = employee.sudo()
        partner = employee.work_contact_id or employee.user_id.partner_id
        if not partner:
            raise UserError(
                "%s has no work contact: the shortage is booked against the employee, so give "
                "the employee a work contact first." % employee.name
            )
        unit = recon.operating_unit_id if recon and "operating_unit_id" in recon._fields else False
        branch = (
            self.env["fix.branch"].sudo().search([("operating_unit_id", "=", unit.id)], limit=1)
            if unit
            else self.env["fix.branch"]
        )
        label = "Field cash short, recovered from %s's pay (%s)" % (employee.name, reference)
        dims = self.env["fix.ar.invoice"]._ar_posting_dims(branch.id or False)
        move = self.env["account.move"]._fix_post_via_m19(
            {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": dhaka_today(),
                "ref": "Field cash shortage %s — BDT %.2f" % (reference, amount),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": payroll.id,
                            "name": label,
                            "debit": amount,
                            "credit": 0.0,
                            "partner_id": partner.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": shortage.id,
                            "name": label,
                            "debit": 0.0,
                            "credit": amount,
                        },
                    ),
                ],
            },
            MOVEMENT_SOURCE,
            source_ref=source_ref,
            dimension_by_line={0: dict(dims), 1: dict(dims)},
        )
        if recon:
            recon.sudo().message_post(
                body="Shortage of BDT %.2f booked for payroll recovery from %s (%s)."
                % (amount, employee.name, move.display_name)
            )
        return move
