# cd_ap_ext — Payment Runs (CD-M52-01, A08 M52).
#
# proposal -> submitted -> approved (SoD) -> released: the run selects
# approved, three-way-matched, unpaid bills due by the cut-off, nets the
# vendor's approved debit/credit notes, carries the TDS/VDS already deducted
# on each bill, and on release creates one fix.payment.execution per vendor
# line on the chosen rail (M50 executes; the bank confirmation comes later).
# action_sync_bank_status reads the execution back: executed -> the payment
# is posted (Dr trade payables / Cr bank) and the bills are paid; failed ->
# the bills return to the open pool.
from collections import defaultdict

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_ext import PAYABLE_MATCH_STATES, _q

RAILS = [
    ("beftn", "BEFTN (batch)"),
    ("rtgs", "BD-RTGS (real time, high value)"),
    ("npsb", "NPSB (instant)"),
    ("cheque", "Cheque"),
]


class FixPaymentRun(models.Model):
    _name = "fix.payment.run"
    _description = "AP Payment Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
    notes = fields.Text(readonly=True)

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

    def _candidate_bills(self):
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("approval_state", "=", "approved"),
            ("payment_state", "=", "not_paid"),
            ("match_state", "in", PAYABLE_MATCH_STATES),
            ("due_date", "<=", self.due_by),
        ]
        if self.operating_unit_id:
            domain.append(("operating_unit_id", "=", self.operating_unit_id.id))
        return self.env["fix.vendor.invoice"].search(domain, order="due_date, id")

    def action_propose(self):
        """Build the proposal from the open pool (re-run replaces it)."""
        for run in self:
            if run.state not in ("draft", "proposed"):
                raise UserError("Run %s is %s — cancel it to re-propose" % (run.name, run.state))
            run.line_ids.unlink()
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
            for (partner, ou), vendor_bills in groups.items():
                notes = Note.search(
                    [
                        ("company_id", "=", run.company_id.id),
                        ("vendor_id.commercial_partner_id", "=", partner.id),
                        ("operating_unit_id", "=", ou.id),
                        ("state", "=", "approved"),
                    ]
                )
                bank = self.env["res.partner.bank"].search(
                    [("partner_id", "=", partner.id)], limit=1
                )
                self.env["fix.payment.run.line"].create(
                    {
                        "run_id": run.id,
                        "partner_id": partner.id,
                        "operating_unit_id": ou.id,
                        "bill_ids": [(6, 0, vendor_bills.ids)],
                        "note_ids": [(6, 0, notes.ids)],
                        "bank_account_id": bank.id or False,
                    }
                )
            run.line_ids._apply_skip_rules()
            run.state = "proposed"
        return True

    def action_submit(self):
        """Submit for approval: every payable line must be payable on the rail."""
        Param = self.env["fix.tax.parameter"]
        for run in self:
            if run.state != "proposed":
                raise UserError("Propose the run first")
            payable = run.line_ids.filtered(lambda line: line.state == "proposed")
            if not payable:
                raise UserError("Nothing payable in run %s" % run.name)
            problems = []
            for line in payable:
                bank = line.bank_account_id
                if run.rail != "cheque" and not bank:
                    problems.append("%s: no bank account on file" % line.partner_id.name)
                elif (
                    run.rail in ("beftn", "rtgs")
                    and "fix_routing_number" in bank._fields
                    and not bank.fix_routing_number
                ):
                    problems.append(
                        "%s: account %s has no routing number (BEFTN/RTGS need it)"
                        % (line.partner_id.name, bank.acc_number)
                    )
                if run.rail == "rtgs":
                    minimum = Param.get_value("rtgs_min_amount", run.payment_date, run.company_id)
                    if line.amount < minimum:
                        problems.append(
                            "%s: BDT %.2f is below the BD-RTGS minimum %.2f"
                            % (line.partner_id.name, line.amount, minimum)
                        )
            if problems:
                raise UserError("Run %s cannot be submitted:\n%s" % (run.name, "\n".join(problems)))
            run.write({"state": "to_approve", "prepared_by": self.env.user.id})
        return True

    def action_approve(self):
        """Approve (finance manager). SoD: the preparer cannot approve."""
        for run in self:
            if run.state != "to_approve":
                raise UserError("Run %s is not awaiting approval" % run.name)
            if not self.env.user.has_group("account.group_account_manager"):
                raise UserError("Payment runs are approved by an accounting manager")
            if run.prepared_by == self.env.user:
                raise UserError("Segregation of duties: the preparer cannot approve the run")
            run.write({"state": "approved", "approved_by": self.env.user.id})
        return True

    def action_release(self):
        """Create the payment executions on the rail (one per vendor line)."""
        if "fix.payment.execution" not in self.env:
            raise UserError("Treasury (cd_cash_position) is not installed — nothing released")
        Execution = self.env["fix.payment.execution"]
        efields = Execution._fields
        for run in self:
            if run.state != "approved":
                raise UserError("Only an approved run is released")
            # the paying bank: the AP payment journal (fails closed when unset);
            # treasury releases the instruction from it and the run posts on it
            journal = ap_journal(self.env, run.company_id, "payment")
            for line in run.line_ids.filtered(lambda line: line.state == "proposed"):
                vals = {
                    "company_id": run.company_id.id,
                    "operating_unit_id": line.operating_unit_id.id,
                    "source_model": "fix.payment.run.line",
                    "source_id": line.id,
                    "payee": line._payee_label(),
                    "currency_id": run.currency_id.id,
                    "amount": line.amount,
                    "method": "cheque" if run.rail == "cheque" else "bank_transfer",
                }
                # treasury's execution fields (M50): set each one only if it exists
                optional = {
                    "rail": run.rail,
                    "partner_id": line.partner_id.id,
                    "partner_bank_id": line.bank_account_id.id or False,
                    "journal_id": journal.id,
                    "value_date": run.payment_date,
                    # the run books its own payment entry (_post_payment):
                    # treasury must not credit the bank a second time
                    "source_posts_gl": True,
                }
                vals.update({k: v for k, v in optional.items() if k in efields})
                execution = Execution.create(vals)
                line.write({"execution_id": execution.id, "state": "sent"})
                line.bill_ids.with_context(ap_internal=True).write({"payment_state": "in_run"})
                line.note_ids.write({"state": "applied", "payment_run_id": run.id})
            run.state = "released"
            publish(
                self.env,
                "payment_run.released",
                "fix.payment.run",
                run.id,
                {"name": run.name, "rail": run.rail, "amount": run.total_amount},
            )
        return True

    def action_sync_bank_status(self):
        """Read each execution back from treasury: executed -> post the
        payment and mark the bills paid; failed -> return the bills."""
        for run in self:
            if run.state != "released":
                raise UserError("Run %s has not been released" % run.name)
            for line in run.line_ids.filtered(lambda line: line.state == "sent"):
                execution = line.execution_id
                status = execution.state
                # executed WITH bank evidence only: a caller-asserted (legacy)
                # execution is not a bank confirmation — the line keeps waiting
                asserted = (
                    "confirmation_source" in execution._fields
                    and execution.confirmation_source == "caller_asserted"
                )
                if status == "executed" and not asserted:
                    line._post_payment()
                elif status == "failed":
                    line.bill_ids.with_context(ap_internal=True).write(
                        {"payment_state": "not_paid"}
                    )
                    line.note_ids.write({"state": "approved", "payment_run_id": False})
                    line.state = "failed"
            if not run.line_ids.filtered(lambda line: line.state == "sent"):
                run.state = "done"
        return True

    def action_cancel(self):
        for run in self:
            if run.state in ("released", "done"):
                raise UserError("A released run is settled through treasury, not cancelled")
            run.line_ids.unlink()
            run.state = "cancelled"
        return True


class FixPaymentRunLine(models.Model):
    _name = "fix.payment.run.line"
    _description = "AP Payment Run Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
                line.write(
                    {
                        "state": "skipped",
                        "skip_reason": "Notes netted exceed the bills (BDT %.2f) — the vendor "
                        "owes a refund" % line.amount,
                    }
                )

    def _payee_label(self):
        self.ensure_one()
        if self.bank_account_id:
            return "%s / %s" % (self.partner_id.name, self.bank_account_id.acc_number)
        return self.partner_id.name

    def _post_payment(self):
        """Dr trade payables (the vendor) / Cr the payment bank journal."""
        self.ensure_one()
        run, env = self.run_id, self.env
        company = run.company_id
        execution = self.execution_id
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
        self.bill_ids.with_context(ap_internal=True).write({"payment_state": "paid"})
        self.write({"state": "paid", "move_id": move.id})
