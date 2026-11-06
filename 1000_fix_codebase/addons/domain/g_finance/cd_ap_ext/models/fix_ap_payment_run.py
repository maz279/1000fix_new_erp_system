# cd_ap_ext — Payment Runs (CD-M52-01, A08 M52).
#
# proposal -> submitted -> approved (SoD) -> released: the run selects
# approved, POSTED, three-way-matched, unpaid bills due by the cut-off, nets
# the vendor's approved debit/credit notes, carries the TDS/VDS already
# deducted on each bill, and on release asks treasury (M50) for one pinned
# fix.payment.execution per vendor line on the chosen rail. Treasury
# prepares, authorises and releases each instruction to the bank under its
# own two-person rule (B1 contract _fix_request_payment). action_sync_bank_
# status reads the execution back: executed -> the payment is posted (Dr
# trade payables / Cr bank) and the bills are paid; failed -> the bills
# return to the open pool.
#
# A08 audit (2026-11-04) controls:
#   M52-1  the approval is a SNAPSHOT of every line: payee, bank account id,
#          account number, routing, amount, bills and notes. After submission
#          the lines are locked (no bank swap, no bill added); at release the
#          live figures must equal the snapshot and every payee account must
#          pass _fix_assert_payable_bank (confirmed, unchanged, cooled off).
#   M52-4  one live payment per bill (fix.ap.bill.payment unique index), and
#          the bill's payment_state is a guarded field.
#   M52-6  state / prepared_by / approved_by / released_by are guarded; the
#          preparer, the approver and the releaser are three people
#          (BRU-APE-06).
#   M52-2  only a bill with a POSTED liability is proposed.
import json
from collections import defaultdict

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_controls import GROUP_MANAGER, require_finance
from .fix_ap_ext import PAYABLE_MATCH_STATES, _q
from .fix_ap_payee_bank import _norm

RAILS = [
    ("beftn", "BEFTN (batch)"),
    ("rtgs", "BD-RTGS (real time, high value)"),
    ("npsb", "NPSB (instant)"),
    ("cheque", "Cheque"),
]

RUN_GUARDED = {
    "state",
    "prepared_by",
    "approved_by",
    "approved_at",
    "released_by",
    "approved_snapshot",
    "approved_total",
    "notes",
}
# the run's terms: fixed once it is submitted
RUN_TERMS = {"rail", "payment_date", "due_by", "currency_id", "company_id", "operating_unit_id"}
LINE_GUARDED = {"state", "skip_reason", "execution_id", "move_id", "reversal_move_id"}
LINE_TERMS = {
    "bill_ids",
    "note_ids",
    "bank_account_id",
    "partner_id",
    "operating_unit_id",
    "run_id",
}
OPEN_RUN_STATES = ("draft", "proposed")
FAILED_EXECUTION_STATES = ("failed", "cancelled")


class FixPaymentRun(models.Model):
    _name = "fix.payment.run"
    _description = "AP Payment Run"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "payment_date desc, id desc"

    name = fields.Char(readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", help="Empty = every operating unit's bills (one line per vendor and unit)"
    )
    rail = fields.Selection(RAILS, required=True, default="beftn", tracking=True)
    payment_date = fields.Date(required=True, default=fields.Date.context_today, tracking=True)
    due_by = fields.Date(
        string="Bills Due By", required=True, default=fields.Date.context_today, tracking=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("proposed", "Proposed"),
            ("to_approve", "To Approve"),
            ("approved", "Approved"),
            ("released", "Released to Bank"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.payment.run.line", "run_id", string="Vendor Lines")
    total_amount = fields.Monetary(
        string="To Pay", currency_field="currency_id", compute="_compute_totals", store=True
    )
    total_tds = fields.Monetary(
        string="TDS Withheld", currency_field="currency_id", compute="_compute_totals", store=True
    )
    total_vds = fields.Monetary(
        string="VDS Withheld", currency_field="currency_id", compute="_compute_totals", store=True
    )
    bill_count = fields.Integer(compute="_compute_totals", store=True)
    prepared_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    released_by = fields.Many2one("res.users", string="Released By", readonly=True, copy=False)
    approved_total = fields.Monetary(
        string="Approved Total", currency_field="currency_id", readonly=True, copy=False
    )
    approved_snapshot = fields.Text(
        readonly=True,
        copy=False,
        help="What the approver signed: per line the payee, bank account, account number, "
        "routing, amount, bills and notes. The release pays exactly this.",
    )
    notes = fields.Text(readonly=True)

    # ------------------------------------------------------------- guards --
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | RUN_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(run.state not in OPEN_RUN_STATES for run in self):
            locked |= RUN_TERMS
        return locked

    def write(self, vals):
        if RUN_TERMS & set(vals) and not self._fix_guard_open():
            fixed = self.filtered(lambda r: r.state not in OPEN_RUN_STATES)
            changed = [
                n
                for n in RUN_TERMS & set(vals)
                if any(r._fix_guard_differs(n, vals[n], r[n]) for r in fixed)
            ]
            if changed:
                raise UserError(
                    "Run %s is %s: its terms (%s) are fixed. Cancel it and propose a new run."
                    % (fixed[0].name, fixed[0].state, ", ".join(sorted(changed)))
                )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda r: r.state not in ("draft", "proposed", "cancelled")):
            raise UserError("A submitted, approved or released payment run is not deleted.")
        return super().unlink()

    @api.depends("line_ids.amount", "line_ids.tds_amount", "line_ids.vds_amount", "line_ids.state")
    def _compute_totals(self):
        for run in self:
            live = run.line_ids.filtered(lambda line: line.state != "skipped")
            run.total_amount = sum(live.mapped("amount"))
            run.total_tds = sum(live.mapped("tds_amount"))
            run.total_vds = sum(live.mapped("vds_amount"))
            run.bill_count = len(live.bill_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.payment.run") or "PRUN"
        return super().create(vals_list)

    # ------------------------------------------------------------ proposal --
    def _candidate_bills(self):
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("approval_state", "=", "approved"),
            ("payment_state", "=", "not_paid"),
            ("match_state", "in", PAYABLE_MATCH_STATES),
            ("due_date", "<=", self.due_by),
            # A08 M52-2/-26: a bill whose liability was never booked is not paid
            ("move_id.state", "=", "posted"),
            # BRU-APE-08: a run pays by bank rails; a non-bank bill went out at
            # the uplifted withholding and is not one of them
            ("payment_channel", "=", "bank"),
        ]
        if self.operating_unit_id:
            domain.append(("operating_unit_id", "=", self.operating_unit_id.id))
        Bill = self.env["fix.vendor.invoice"]
        Bill._ap_release_cancelled_requests(
            Bill.search([("company_id", "=", self.company_id.id), ("payment_state", "=", "in_run")])
        )
        bills = Bill.search(domain, order="due_date, id")
        live = (
            self.env["fix.ap.bill.payment"]
            .sudo()
            .search([("bill_id", "in", bills.ids), ("state", "in", ("open", "paid"))])
        )
        return bills - live.mapped("bill_id")

    @api.model
    def _payee_account(self, partner):
        """The vendor's account to pay: a confirmed one first."""
        banks = self.env["res.partner.bank"].sudo().search([("partner_id", "=", partner.id)])
        payable = banks.filtered(lambda b: not b._fix_payable_problem())
        return (payable or banks)[:1]

    def action_propose(self):
        """Build the proposal from the open pool (re-run replaces it)."""
        require_finance(self.env, "Proposing a payment run")
        for run in self:
            if run.state not in ("draft", "proposed"):
                raise UserError("Run %s is %s — cancel it to re-propose" % (run.name, run.state))
            run.line_ids._guarded().unlink()
            bills = run._candidate_bills()
            if not bills:
                raise UserError(
                    "No approved, matched, unpaid bills due by %s in %s"
                    % (run.due_by, run.company_id.name)
                )
            groups = defaultdict(lambda: self.env["fix.vendor.invoice"])
            for bill in bills:
                groups[(bill.vendor_id.commercial_partner_id, bill.operating_unit_id)] |= bill
            Note = self.env["fix.vendor.note"]
            Line = self.env["fix.payment.run.line"]._guarded()
            for (partner, ou), vendor_bills in groups.items():
                notes = Note.search(
                    [
                        ("company_id", "=", run.company_id.id),
                        ("vendor_id.commercial_partner_id", "=", partner.id),
                        ("operating_unit_id", "=", ou.id),
                        ("state", "=", "approved"),
                    ]
                )
                bank = run._payee_account(partner)
                Line.create(
                    {
                        "run_id": run.id,
                        "partner_id": partner.id,
                        "operating_unit_id": ou.id,
                        "bill_ids": [(6, 0, vendor_bills.ids)],
                        "note_ids": [(6, 0, notes.ids)],
                        "bank_account_id": bank.id or False,
                    }
                )
            run.line_ids._guarded()._apply_skip_rules()
            run._guarded().write({"state": "proposed"})
        return True

    def _line_problems(self, lines):
        Param = self.env["fix.tax.parameter"]
        problems = []
        for line in lines:
            run = line.run_id
            bank = line.bank_account_id.sudo()
            if run.rail != "cheque" and not bank:
                problems.append("%s: no bank account on file" % line.partner_id.name)
                continue
            if bank:
                if (
                    run.rail in ("beftn", "rtgs")
                    and "fix_routing_number" in bank._fields
                    and not bank.fix_routing_number
                ):
                    problems.append(
                        "%s: account %s has no routing number (BEFTN/RTGS need it)"
                        % (line.partner_id.name, bank.acc_number)
                    )
                problem = bank._fix_payable_problem()
                if problem:
                    problems.append("%s: %s" % (line.partner_id.name, problem))
            if run.rail == "rtgs":
                minimum = Param.get_value("rtgs_min_amount", run.payment_date, run.company_id)
                if line.amount < minimum:
                    problems.append(
                        "%s: BDT %.2f is below the BD-RTGS minimum %.2f"
                        % (line.partner_id.name, line.amount, minimum)
                    )
        return problems

    def action_submit(self):
        """Submit for approval: every payable line must be payable on the rail,
        to a confirmed payee account."""
        require_finance(self.env, "Submitting a payment run")
        for run in self:
            if run.state != "proposed":
                raise UserError("Propose the run first")
            payable = run.line_ids.filtered(lambda line: line.state == "proposed")
            if not payable:
                raise UserError("Nothing payable in run %s" % run.name)
            problems = run._line_problems(payable)
            if problems:
                raise UserError("Run %s cannot be submitted:\n%s" % (run.name, "\n".join(problems)))
            run._guarded().write({"state": "to_approve", "prepared_by": self.env.user.id})
        return True

    # ------------------------------------------------------------ approval --
    def _snapshot(self):
        self.ensure_one()
        rows = []
        for line in self.line_ids.filtered(lambda ln: ln.state == "proposed").sorted("id"):
            bank = line.bank_account_id.sudo()
            rows.append(
                {
                    "line_id": line.id,
                    "partner_id": line.partner_id.id,
                    "bank_id": bank.id or False,
                    "acc_number": _norm(bank.acc_number) if bank else "",
                    "routing": _norm(bank.fix_routing_number)
                    if bank and "fix_routing_number" in bank._fields
                    else "",
                    "amount": _q(line.amount),
                    "bill_ids": sorted(line.bill_ids.ids),
                    "note_ids": sorted(line.note_ids.ids),
                }
            )
        return rows

    def _run_conflicted(self):
        self.ensure_one()
        return (self.create_uid | self.prepared_by).sudo()

    def action_approve(self):
        """Approve (finance manager). SoD: neither the run's creator nor its
        preparer approves. The approval is a snapshot of what is paid."""
        for run in self:
            if run.state != "to_approve":
                raise UserError("Run %s is not awaiting approval" % run.name)
            if not (self.env.su or self.env.user.has_group(GROUP_MANAGER)):
                raise UserError("Payment runs are approved by an accounting manager")
            if self.env.user in run._run_conflicted():
                raise UserError("Segregation of duties: the preparer cannot approve the run")
            problems = run._line_problems(run.line_ids.filtered(lambda ln: ln.state == "proposed"))
            if problems:
                raise UserError("Run %s cannot be approved:\n%s" % (run.name, "\n".join(problems)))
            snapshot = run._snapshot()
            run._guarded().write(
                {
                    "state": "approved",
                    "approved_by": self.env.user.id,
                    "approved_at": fields.Datetime.now(),
                    "approved_snapshot": json.dumps(snapshot, sort_keys=True),
                    "approved_total": _q(sum(row["amount"] for row in snapshot)),
                }
            )
        return True

    def _assert_matches_snapshot(self):
        """M52-1: pay exactly what the approver signed."""
        self.ensure_one()
        try:
            signed = json.loads(self.approved_snapshot or "[]")
        except ValueError:
            signed = None
        live = self._snapshot()
        if not signed or signed != live:
            raise UserError(
                "Run %s changed after its approval (payee account, amount, bills or notes "
                "differ from what %s approved): nothing was released. Cancel the run and "
                "propose it again." % (self.name, self.approved_by.name or "the approver")
            )
        for line in self.line_ids.filtered(lambda ln: ln.state == "proposed"):
            for bill in line.bill_ids:
                if (
                    bill.approval_state != "approved"
                    or bill.payment_state != "not_paid"
                    or bill.move_id.state != "posted"
                    or bill.match_state not in PAYABLE_MATCH_STATES
                    or bill._ap_live_payment()
                ):
                    raise UserError(
                        "Bill %s is no longer payable (%s / %s / match %s): run %s is not "
                        "released."
                        % (
                            bill.invoice_ref,
                            bill.approval_state,
                            bill.payment_state,
                            bill.match_state,
                            self.name,
                        )
                    )

    # ------------------------------------------------------------- release --
    def action_release(self):
        """Hand the approved run to treasury: one pinned execution per line,
        created ONLY through treasury's contract _fix_request_payment (B1).
        BRU-APE-06: the releaser is neither the preparer nor the approver."""
        if "fix.payment.execution" not in self.env:
            raise UserError("Treasury (cd_cash_position) is not installed — nothing released")
        require_finance(self.env, "Releasing a payment run")
        Execution = self.env["fix.payment.execution"]
        Lock = self.env["fix.ap.bill.payment"].sudo()
        for run in self:
            if run.state != "approved":
                raise UserError("Only an approved run is released")
            if self.env.user in (run._run_conflicted() | run.approved_by):
                raise UserError(
                    "Segregation of duties (BRU-APE-06): the preparer, the approver and the "
                    "releaser of a payment run are three different people."
                )
            run._assert_matches_snapshot()
            Bank = self.env["res.partner.bank"]
            # the paying bank: the AP payment journal (fails closed when unset)
            journal = ap_journal(self.env, run.company_id, "payment")
            for line in run.line_ids.filtered(lambda line: line.state == "proposed"):
                if line.bank_account_id:
                    Bank._fix_assert_payable_bank(line.bank_account_id)
                method = "cheque" if run.rail == "cheque" else "bank_transfer"
                execution = Execution._fix_request_payment(
                    "fix.payment.run.line",
                    line.id,
                    line.partner_id,
                    line.bank_account_id,
                    line.amount,
                    run.currency_id,
                    "%s %s" % (run.name, line.partner_id.name),
                    run.approved_by,
                    method=method,
                    rail=run.rail,
                    journal_id=journal.id,
                    value_date=run.payment_date,
                    company_id=run.company_id.id,
                    operating_unit_id=line.operating_unit_id.id,
                    payee=line._payee_label(),
                )
                execution = execution.sudo()
                if abs((execution.amount or 0.0) - line.amount) > 0.005:
                    raise UserError(
                        "Treasury instruction %s carries %.2f, the approved line %.2f: refused."
                        % (execution.name, execution.amount, line.amount)
                    )
                for bill in line.bill_ids:
                    # the unique index refuses a second live payment of a bill
                    Lock.create(
                        {
                            "company_id": run.company_id.id,
                            "bill_id": bill.id,
                            "run_line_id": line.id,
                            "execution_id": execution.id,
                            "amount": bill.total_payable,
                        }
                    )
                line._guarded().write({"execution_id": execution.id, "state": "sent"})
                line.bill_ids._guarded().write({"payment_state": "in_run"})
                line.note_ids._guarded().write({"state": "applied", "payment_run_id": run.id})
            run._guarded().write({"state": "released", "released_by": self.env.user.id})
            publish(
                self.env,
                "payment_run.released",
                "fix.payment.run",
                run.id,
                {"name": run.name, "rail": run.rail, "amount": run.total_amount},
            )
        return True

    def action_sync_bank_status(self):
        """Read each execution back from treasury (M50):
        - pending / prepared / sent: still in flight, the line waits;
        - executed (with bank evidence): post the payment, the bills are paid;
        - failed or cancelled before execution: the bills return to the pool;
        - failed AFTER execution (a bounce after clearing): the run posted its
          own payment entry (source_posts_gl), so it reverses that entry and
          the bills return to the pool."""
        require_finance(self.env, "Reading the bank status of a payment run")
        Lock = self.env["fix.ap.bill.payment"].sudo()
        for run in self:
            if run.state not in ("released", "done"):
                raise UserError("Run %s has not been released" % run.name)
            for line in run.line_ids.filtered(lambda line: line.state in ("sent", "paid")):
                execution = line.execution_id.sudo()
                status = execution.state
                if line.state == "paid":
                    if status in FAILED_EXECUTION_STATES:
                        line._reverse_payment(execution)
                    continue
                # executed WITH bank evidence only: a caller-asserted (legacy)
                # execution is not a bank confirmation — the line keeps waiting
                asserted = (
                    "confirmation_source" in execution._fields
                    and execution.confirmation_source == "caller_asserted"
                )
                if status == "executed" and not asserted:
                    line._post_payment()
                    Lock.search([("run_line_id", "=", line.id), ("state", "=", "open")]).write(
                        {"state": "paid"}
                    )
                elif status in FAILED_EXECUTION_STATES:
                    line._return_bills()
                    line._guarded().write({"state": "failed"})
            if not run.line_ids.filtered(lambda line: line.state == "sent"):
                run._guarded().write({"state": "done"})
        return True

    def action_cancel(self):
        require_finance(self.env, "Cancelling a payment run")
        for run in self:
            if run.state in ("released", "done"):
                raise UserError("A released run is settled through treasury, not cancelled")
            run.line_ids._guarded().unlink()
            run._guarded().write({"state": "cancelled"})
        return True


class FixPaymentRunLine(models.Model):
    _name = "fix.payment.run.line"
    _description = "AP Payment Run Line"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "run_id, partner_id"

    run_id = fields.Many2one("fix.payment.run", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="run_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    currency_id = fields.Many2one(related="run_id.currency_id")
    partner_id = fields.Many2one("res.partner", string="Vendor", required=True, index=True)
    bank_account_id = fields.Many2one("res.partner.bank", string="Vendor Bank Account")
    bill_ids = fields.Many2many("fix.vendor.invoice", string="Bills")
    note_ids = fields.Many2many("fix.vendor.note", string="Debit / Credit Notes")
    gross_amount = fields.Monetary(
        string="Bills Gross", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    tds_amount = fields.Monetary(
        string="TDS", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    vds_amount = fields.Monetary(
        string="VDS", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    notes_amount = fields.Monetary(
        string="Notes Netted", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    amount = fields.Monetary(
        string="Net to Pay", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    state = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("skipped", "Skipped"),
            ("sent", "Sent to Bank"),
            ("paid", "Paid"),
            ("failed", "Failed"),
        ],
        default="proposed",
        required=True,
    )
    skip_reason = fields.Char(readonly=True)
    execution_id = fields.Many2one("fix.payment.execution", readonly=True)
    move_id = fields.Many2one("account.move", string="Payment GL Entry", readonly=True)
    reversal_move_id = fields.Many2one(
        "account.move",
        string="Payment Reversal Entry",
        readonly=True,
        help="Posted when the bank returned the payment after clearing.",
    )

    # ------------------------------------------------------------- guards --
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | LINE_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(line.run_id.state not in OPEN_RUN_STATES for line in self):
            locked |= LINE_TERMS
        return locked

    def _check_run_open(self, names=None):
        if self._fix_guard_open():
            return
        fixed = self.filtered(lambda line: line.run_id.state not in OPEN_RUN_STATES)
        if fixed:
            raise UserError(
                "Run %s is %s: its lines (%s) are fixed — the approval covers exactly them. "
                "Cancel the run and propose a new one."
                % (
                    fixed[0].run_id.name,
                    fixed[0].run_id.state,
                    ", ".join(sorted(names or [])) or "lines",
                )
            )

    @api.constrains("partner_id", "bank_account_id")
    def _check_payee_account(self):
        """A line pays the vendor's OWN account (M52-1: an accomplice's account
        was put on an approved line)."""
        for line in self:
            bank = line.bank_account_id.sudo()
            if (
                bank
                and bank.partner_id.commercial_partner_id != line.partner_id.commercial_partner_id
            ):
                raise ValidationError(
                    "Account %s belongs to %s, not to the payee %s."
                    % (bank.acc_number, bank.partner_id.display_name, line.partner_id.display_name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._check_run_open(["new line"])
        return lines

    def write(self, vals):
        terms = LINE_TERMS & set(vals)
        if terms:
            self._check_run_open(terms)
        return super().write(vals)

    def unlink(self):
        self._check_run_open(["delete"])
        return super().unlink()

    @api.depends("bill_ids.total_payable", "note_ids.signed_total")
    def _compute_amounts(self):
        for line in self:
            bills = line.bill_ids
            line.gross_amount = sum(bills.mapped("gross_amount"))
            line.tds_amount = sum(bills.mapped("tds_amount"))
            line.vds_amount = sum(bills.mapped("vds_amount"))
            line.notes_amount = sum(line.note_ids.mapped("signed_total"))
            line.amount = _q(sum(bills.mapped("total_payable")) + line.notes_amount)

    def _apply_skip_rules(self):
        for line in self:
            if line.amount <= 0:
                line._guarded().write(
                    {
                        "state": "skipped",
                        "skip_reason": "Notes netted exceed the bills (BDT %.2f) — the vendor "
                        "owes a refund" % line.amount,
                    }
                )

    def _payee_label(self):
        self.ensure_one()
        if self.bank_account_id:
            return "%s / %s" % (self.partner_id.name, self.bank_account_id.sudo().acc_number)
        return self.partner_id.name

    def _return_bills(self):
        """The payment did not happen (or came back): the bills and notes
        return to the open pool and the payment lock is released."""
        self.ensure_one()
        self.bill_ids._guarded().write({"payment_state": "not_paid"})
        self.note_ids._guarded().write({"state": "approved", "payment_run_id": False})
        self.env["fix.ap.bill.payment"].sudo().search(
            [("run_line_id", "=", self.id), ("state", "in", ("open", "paid"))]
        ).write({"state": "failed"})

    def _reverse_payment(self, execution):
        """A bounce after clearing: reverse the run's own payment entry
        (Dr bank / Cr trade payables) and reopen the bills."""
        self.ensure_one()
        if self.reversal_move_id:
            return
        run, env = self.run_id, self.env
        company = run.company_id
        original = self.move_id
        label = "Reversal of %s: %s returned by the bank (%s)" % (
            original.name or run.name,
            self.partner_id.name,
            execution.failure_reason or execution.state,
        )
        lines = [
            (ml.account_id, label, ml.credit, ml.debit, ml.partner_id)
            for ml in original.sudo().line_ids
        ]
        move = post_ap_move(
            env,
            company,
            original.journal_id,
            fields.Date.context_today(self),
            label,
            lines,
            self.operating_unit_id,
        )
        self._return_bills()
        self._guarded().write({"state": "failed", "reversal_move_id": move.id})
        run.message_post(body=label)

    def _post_payment(self):
        """Dr trade payables (the vendor) / Cr the payment bank journal, for
        the amount treasury actually paid (= the approved line)."""
        self.ensure_one()
        run, env = self.run_id, self.env
        company = run.company_id
        execution = self.execution_id.sudo()
        if abs((execution.amount or 0.0) - self.amount) > 0.005:
            raise UserError(
                "Line %s: treasury paid %.2f, the approved line is %.2f — reconcile before "
                "posting." % (self.partner_id.name, execution.amount, self.amount)
            )
        journal = (
            execution.journal_id
            if "journal_id" in execution._fields and execution.journal_id
            else ap_journal(env, company, "payment")
        )
        label = "%s %s" % (run.name, self.partner_id.name)
        move = post_ap_move(
            env,
            company,
            journal,
            run.payment_date,
            label,
            [
                (ap_account(env, company, "ap"), label, self.amount, 0.0, self.partner_id),
                (journal.default_account_id, label, 0.0, self.amount, self.partner_id),
            ],
            self.operating_unit_id,
        )
        self.bill_ids._guarded().write({"payment_state": "paid"})
        self._guarded().write({"state": "paid", "move_id": move.id})
