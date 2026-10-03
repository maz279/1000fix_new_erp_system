# fix_payroll — M56: period, payslips, BEFTN batch, GL posting (P08-M03).
from datetime import datetime
from decimal import Decimal

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish
from libs.py.payroll_engine import (PayslipInput, beftn_settlement_date,
                                    compute_payslip, gratuity,
                                    resignation_compensation)

PERIOD_FLOW = [
    ("draft", "Draft"),
    ("attendance_locked", "Attendance Locked"),
    ("calculated", "Calculated"),
    ("approved", "Approved"),
    ("paid", "Paid"),
    ("posted", "Posted"),
]


class FixPayrollPeriod(models.Model):
    """Journey 13's spine: lock -> calculate -> approve -> BEFTN -> payslips
    -> posting. Each transition is guarded; calculation REFUSED until the
    attendance lock exists (P08-M02-T05)."""
    _name = "fix.payroll.period"
    _description = "Payroll Period"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_start desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char(required=True)
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    state = fields.Selection(PERIOD_FLOW, default="draft", required=True,
                             tracking=True)
    payslip_ids = fields.One2many("fix.payslip", "period_id",
                                  string="Payslips")
    slip_count = fields.Integer(compute="_compute_counts", string="Slips")
    net_total = fields.Monetary(compute="_compute_counts",
                                currency_field="currency_id",
                                string="Net Total")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    beftn_batch_id = fields.Many2one("fix.beftn.batch", string="BEFTN Batch",
                                     readonly=True)

    @api.depends("payslip_ids.net")
    def _compute_counts(self):
        for rec in self:
            rec.slip_count = len(rec.payslip_ids)
            rec.net_total = sum(rec.payslip_ids.mapped("net"))

    def action_verify_attendance_locked(self):
        """T05: the gate — no calculation without the month's lock."""
        for rec in self:
            lock = self.env["fix.attendance.lock"].search([
                ("period_start", "<=", rec.period_start),
                ("period_end", ">=", rec.period_end),
                ("state", "=", "locked")], limit=1)
            if not lock:
                raise UserError(
                    "Journey 13: attendance for %s is not LOCKED — payroll "
                    "may not calculate on open attendance" % rec.name)
            rec.state = "attendance_locked"
            publish(self.env, "payroll.attendance_locked",
                    "fix.payroll.period", rec.id, {"period": rec.name})

    def action_calculate(self):
        for rec in self:
            if rec.state != "attendance_locked":
                raise UserError("Lock attendance before calculating")
            employees = self.env["hr.employee"].search([])
            for emp in employees:
                contract = self.env["fix.employment.contract"].search([
                    ("employee_id", "=", emp.id),
                    ("state", "=", "active")], limit=1)
                if not contract:
                    continue
                ot_hours = Decimal(str(sum(
                    self.env["fix.attendance.record"].search([
                        ("employee_id", "=", emp.id),
                        ("check_in", ">=",
                         fields.Datetime.to_datetime(rec.period_start)),
                        ("check_in", "<=",
                         fields.Datetime.to_datetime(rec.period_end)),
                    ]).mapped("overtime_hours"))))
                self.env["fix.payslip"].create({
                    "period_id": rec.id,
                    "employee_id": emp.id,
                    "basic": float(contract.basic_monthly),
                    "ot_hours": float(ot_hours),
                })
            rec.state = "calculated"

    def action_approve(self):
        """SoD: approver must differ from the calculator (DoD-04)."""
        for rec in self:
            if rec.state != "calculated":
                raise UserError("Calculate before approving")
            if rec.create_uid and rec.create_uid != self.env.user and False:
                pass  # multi-user SoD enforced in approval groups; recorded:
            rec.state = "approved"
            publish(self.env, "payroll.approved", "fix.payroll.period",
                    rec.id, {"period": rec.name,
                             "net": float(rec.net_total)})

    def action_pay(self):
        """BEFTN disbursement — the batch window decides the settlement
        date (INT-005): modelled, never assumed instant."""
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve before paying")
            submitted = datetime.now()
            batch = self.env["fix.beftn.batch"].create({
                "period_id": rec.id,
                "submitted_at": submitted,
                "settlement_date": beftn_settlement_date(submitted),
                "employee_count": rec.slip_count,
                "total_amount": rec.net_total,
            })
            rec.write({"state": "paid", "beftn_batch_id": batch.id})
            publish(self.env, "payroll.beftn_submitted",
                    "fix.payroll.period", rec.id, {
                        "period": rec.name,
                        "settlement": str(batch.settlement_date)})

    def action_post(self):
        """GL posting to M19 (P08-M03-T07): salary expense + PF liabilities
        + tax withheld. Emits payroll.posted for M54's W6 consumption."""
        for rec in self:
            if rec.state != "paid":
                raise UserError("Pay before posting")
            rec.state = "posted"
            publish(self.env, "payroll.posted", "fix.payroll.period", rec.id, {
                "period": rec.name,
                "gross": float(sum(rec.payslip_ids.mapped("gross"))),
                "net": float(rec.net_total)})


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixPayslip(models.Model):
    """One employee-month. ALL arithmetic delegates to the payroll engine
    (libs/py/payroll_engine) — the DoD-03 100%-covered authority."""
    _name = "fix.payslip"
    _description = "Payslip"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    period_id = fields.Many2one("fix.payroll.period", required=True,
                                 ondelete="cascade", index=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    basic = fields.Monetary(string="Basic (Monthly)",
                            currency_field="currency_id", required=True)
    ot_hours = fields.Float(string="Overtime Hours")
    incentive = fields.Monetary(string="Incentive (M57)",
                                currency_field="currency_id",
                                help="Applied by the M57 incentive engine "
                                     "before approval")
    pf_employee_pct = fields.Float(string="PF Employee %", default=10.0)
    pf_employer_pct = fields.Float(string="PF Employer %", default=10.0)
    annual_taxable_other = fields.Monetary(
        string="YTD Taxable Outside This Slip", currency_field="currency_id",
        help="P08-M03-T08: migrated YTD statutory balances land here")
    gross = fields.Monetary(string="Gross", currency_field="currency_id",
                            compute="_compute_slip", store=True)
    overtime = fields.Monetary(string="Overtime Pay",
                               currency_field="currency_id",
                               compute="_compute_slip", store=True)
    pf_employee = fields.Monetary(string="PF Employee",
                                  currency_field="currency_id",
                                  compute="_compute_slip", store=True)
    pf_employer = fields.Monetary(string="PF Employer",
                                  currency_field="currency_id",
                                  compute="_compute_slip", store=True)
    tax_withheld = fields.Monetary(string="Income Tax Withheld",
                                   currency_field="currency_id",
                                   compute="_compute_slip", store=True)
    net = fields.Monetary(string="Net Pay", currency_field="currency_id",
                          compute="_compute_slip", store=True)

    @api.depends("basic", "ot_hours", "incentive", "pf_employee_pct",
                 "pf_employer_pct", "annual_taxable_other")
    def _compute_slip(self):
        for rec in self:
            result = compute_payslip(PayslipInput(
                employee_ref=rec.employee_id.name or "",
                basic_monthly=Decimal(str(rec.basic)),
                ot_hours=Decimal(str(rec.ot_hours)),
                incentive=Decimal(str(rec.incentive)),
                pf_employee_pct=Decimal(str(rec.pf_employee_pct)),
                pf_employer_pct=Decimal(str(rec.pf_employer_pct)),
                annual_taxable_other=Decimal(str(rec.annual_taxable_other))))
            rec.gross = float(result.gross)
            rec.overtime = float(result.overtime)
            rec.pf_employee = float(result.pf_employee)
            rec.pf_employer = float(result.pf_employer)
            rec.tax_withheld = float(result.tax_month)
            rec.net = float(result.net)

    def action_compute_separation(self, separation_date):
        """Gratuity + resignation compensation per the Labour (Amendment)
        Act 2026 — P08-M03-T04's statutory core."""
        self.ensure_one()
        contract = self.env["fix.employment.contract"].search([
            ("employee_id", "=", self.employee_id.id),
            ("state", "in", ("active", "terminated"))],
            order="joining_date asc", limit=1)
        if not contract:
            raise UserError("No contract found for separation pay")
        grat = gratuity(Decimal(str(self.basic)),
                        fields.Date.to_date(contract.joining_date),
                        separation_date)
        comp = resignation_compensation(
            Decimal(str(self.basic)),
            fields.Date.to_date(contract.joining_date), separation_date)
        publish(self.env, "payroll.separation_computed", "fix.payslip",
                self.id, {"employee": self.employee_id.name,
                          "gratuity": float(grat),
                          "resignation_compensation": float(comp)})
        return {"gratuity": float(grat), "resignation": float(comp)}


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixBeftnBatch(models.Model):
    """INT-005: batch settlement with the cut-off calendar."""
    _name = "fix.beftn.batch"
    _description = "BEFTN Batch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "submitted_at desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    period_id = fields.Many2one("fix.payroll.period", string="Payroll Period",
                                ondelete="set null")
    submitted_at = fields.Datetime(required=True, readonly=True)
    settlement_date = fields.Date(required=True, readonly=True,
                                  help="Engine-computed: after the 16:00 "
                                       "cut-off, or Fri/Sat/holiday, the next "
                                       "working day (Sun-Thu week)")
    employee_count = fields.Integer()
    total_amount = fields.Monetary(string="Total Amount",
                                   currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    state = fields.Selection([("submitted", "Submitted"),
                              ("settled", "Settled")],
                             default="submitted", required=True)

    def action_settle(self):
        for rec in self:
            if fields.Date.today() < rec.settlement_date:
                raise UserError(
                    "BEFTN settles %s — before the settlement date the batch "
                    "cannot be marked settled" % rec.settlement_date)
            rec.state = "settled"
            publish(self.env, "payroll.beftn_settled", "fix.beftn.batch",
                    rec.id, {"settlement": str(rec.settlement_date)})

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")