# cd_hr_core — suspension and disciplinary procedure (A09 workflow audit
# M21-11 / §1.2 row 14: "absent in all of h_people"; P2 "missing lifecycles").
#
# BLA s.23 / s.24, as the A09 benchmark gives them (Verified [45]):
#   * a written allegation (the charge);
#   * at least 7 days for the worker to explain;
#   * a hearing;
#   * an enquiry committee with equal numbers of employer and worker
#     representatives, concluded within 60 days;
#   * the punishment decided by the employer or manager - here a routed M63
#     approval: the officer who ran the case, the employee and the case's
#     creator never decide it;
#   * suspension pending enquiry at most 60 days, with a subsistence allowance
#     (its rate is a company setting labour counsel must rule).
# Payroll and attendance learn of the suspension and of the decision through
# events (employee.suspended, employee.suspension_ended, disciplinary.decided).
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_hr_controls_common import (
    DISCIPLINARY_ENQUIRY_DAYS,
    DISCIPLINARY_REPLY_DAYS,
    EXECUTIVE,
    OFFICER,
    SUSPENSION_MAX_DAYS,
)

OUTCOMES = [
    ("exonerated", "Exonerated"),
    ("warning", "Warning"),
    ("censure", "Censure"),
    ("withhold_increment", "Withholding of Increment"),
    ("demotion", "Demotion"),
    ("discharge", "Discharge (s.22)"),
    ("dismissal", "Dismissal for Misconduct (s.23)"),
]


class FixHrDisciplinaryCase(models.Model):
    _name = "fix.hr.disciplinary.case"
    _description = "Disciplinary Case (BLA s.23/24)"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "fix.people.approval.mixin",
        "fix.hr.control.mixin",
    ]
    _order = "id desc"

    _approval_domain = "hr_disciplinary"
    _approval_apply_method = "action_decide"
    _approval_group = EXECUTIVE

    name = fields.Char(default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True, ondelete="restrict")
    allegation = fields.Text(required=True, help="The written charge served on the worker")
    misconduct_category = fields.Selection(
        [
            ("insubordination", "Wilful insubordination or disobedience"),
            ("theft_fraud", "Theft, fraud or dishonesty"),
            ("bribe", "Taking or giving a bribe"),
            ("absence", "Habitual absence without leave"),
            ("lateness", "Habitual late attendance"),
            ("rules_breach", "Habitual breach of rules"),
            ("disorderly", "Riotous or disorderly behaviour"),
            ("negligence", "Habitual negligence or neglect of work"),
            ("other", "Other misconduct (s.23(4))"),
        ],
        required=True,
        default="other",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("charged", "Charge Served"),
            ("explained", "Explanation Received"),
            ("hearing", "Hearing Held"),
            ("enquiry", "Enquiry"),
            ("concluded", "Enquiry Concluded"),
            ("decided", "Decided"),
            ("cancelled", "Withdrawn"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    charge_date = fields.Date()
    reply_days = fields.Integer(default=DISCIPLINARY_REPLY_DAYS, string="Days to Explain")
    explanation_due = fields.Date(compute="_compute_due", store=True)
    explanation = fields.Text()
    explanation_received_on = fields.Date()
    hearing_date = fields.Date()
    hearing_notes = fields.Text()
    enquiry_started_on = fields.Date(readonly=True, copy=False)
    enquiry_due = fields.Date(compute="_compute_due", store=True)
    enquiry_concluded_on = fields.Date(readonly=True, copy=False)
    enquiry_overdue = fields.Boolean(readonly=True, copy=False)
    employer_rep_ids = fields.Many2many(
        "hr.employee",
        "fix_hr_disc_employer_rep_rel",
        "case_id",
        "employee_id",
        string="Employer Representatives",
    )
    worker_rep_ids = fields.Many2many(
        "hr.employee",
        "fix_hr_disc_worker_rep_rel",
        "case_id",
        "employee_id",
        string="Worker Representatives",
    )
    findings = fields.Text()
    proposed_outcome = fields.Selection(OUTCOMES)
    outcome = fields.Selection(OUTCOMES, readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Date(readonly=True, copy=False)
    handled_by_id = fields.Many2one("res.users", string="Case Officer", readonly=True, copy=False)
    # suspension pending enquiry (s.24)
    suspended = fields.Boolean(readonly=True, copy=False)
    suspended_from = fields.Date(readonly=True, copy=False)
    suspended_until = fields.Date(readonly=True, copy=False)
    suspension_ended_on = fields.Date(readonly=True, copy=False)
    subsistence_pct = fields.Float(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "outcome",
            "decided_by_id",
            "decided_on",
            "handled_by_id",
            "enquiry_started_on",
            "enquiry_concluded_on",
            "enquiry_overdue",
            "suspended",
            "suspended_from",
            "suspended_until",
            "suspension_ended_on",
            "subsistence_pct",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {
                "employee_id",
                "allegation",
                "misconduct_category",
                "charge_date",
                "reply_days",
            }
        if self and self.state in ("concluded", "decided", "cancelled"):
            locked |= {"findings", "proposed_outcome", "employer_rep_ids", "worker_rep_ids"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.hr.disciplinary.case")
                    or "HDC/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = {
                "employee_id",
                "allegation",
                "misconduct_category",
                "charge_date",
                "reply_days",
            }
            if frozen & set(vals) and any(r.state != "draft" for r in self.filtered("id")):
                raise UserError(
                    "A served charge is never rewritten; withdraw it and serve a new one."
                )
            late = {"findings", "proposed_outcome", "employer_rep_ids", "worker_rep_ids"}
            if late & set(vals) and any(
                r.state in ("concluded", "decided", "cancelled") for r in self.filtered("id")
            ):
                raise UserError("The enquiry is concluded: its findings are frozen.")
        return super().write(vals)

    @api.depends("charge_date", "reply_days", "enquiry_started_on")
    def _compute_due(self):
        for rec in self:
            rec.explanation_due = (
                rec.charge_date + relativedelta(days=rec.reply_days or 0)
                if rec.charge_date
                else False
            )
            rec.enquiry_due = (
                rec.enquiry_started_on + relativedelta(days=DISCIPLINARY_ENQUIRY_DAYS)
                if rec.enquiry_started_on
                else False
            )

    @api.constrains("reply_days")
    def _check_reply_days(self):
        for rec in self:
            if rec.reply_days < DISCIPLINARY_REPLY_DAYS:
                raise ValidationError(
                    "The worker has at least %d days to explain (BLA s.24)."
                    % DISCIPLINARY_REPLY_DAYS
                )

    def _approval_preparers(self):
        return self.mapped("handled_by_id")

    def _fix_officer(self, what):
        """The case officer runs the procedure; never on their own case. The
        DECISION is routed and excludes the officer and the creator."""
        self._hr_require(OFFICER, what)
        if not self.env.su and self.env.user in self._hr_subject_users():
            raise UserError("You cannot run a disciplinary case about yourself.")

    # ---- the procedure ----------------------------------------------------------
    def action_charge(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Serve the charge of a draft case.")
            rec._fix_officer("Serving a charge")
            if not (rec.allegation or "").strip():
                raise UserError("The charge is a written allegation (s.24).")
            # The charge is served today: a typed earlier date shortened the
            # worker's s.24 seven days to explain (M21 audit E6).
            rec._guarded().write(
                {
                    "state": "charged",
                    "charge_date": fields.Date.context_today(self),
                    "handled_by_id": self.env.uid,
                }
            )
        return True

    def action_record_explanation(self):
        for rec in self:
            if rec.state != "charged":
                raise UserError("Record the explanation of a served charge.")
            rec._fix_officer("Recording an explanation")
            if not (rec.explanation or "").strip():
                raise UserError("Enter the worker's explanation.")
            today = fields.Date.context_today(self)
            received = rec.explanation_received_on or today
            if received > today or (rec.charge_date and received < rec.charge_date):
                raise UserError(
                    "The explanation is received between the charge (%s) and today."
                    % rec.charge_date
                )
            rec._guarded().write({"state": "explained", "explanation_received_on": received})
        return True

    def action_hold_hearing(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state not in ("charged", "explained"):
                raise UserError("A hearing follows the charge.")
            rec._fix_officer("Holding a hearing")
            if rec.state == "charged" and today < rec.explanation_due:
                raise UserError(
                    "The worker has until %s to explain (at least %d days, s.24); the hearing "
                    "cannot come first." % (rec.explanation_due, DISCIPLINARY_REPLY_DAYS)
                )
            held = rec.hearing_date or today
            if held > today:
                raise UserError("Record the hearing on or after the day it is held.")
            if rec.explanation_due and held < rec.explanation_due and rec.state == "charged":
                raise UserError(
                    "The hearing cannot be dated before the worker's explanation window "
                    "closes on %s (s.24)." % rec.explanation_due
                )
            if rec.charge_date and held < rec.charge_date:
                raise UserError("The hearing cannot be dated before the charge.")
            rec._guarded().write({"state": "hearing", "hearing_date": held})
        return True

    def action_start_enquiry(self):
        for rec in self:
            if rec.state != "hearing":
                raise UserError("The enquiry follows the hearing.")
            rec._fix_officer("Starting an enquiry")
            employer, worker = rec.employer_rep_ids, rec.worker_rep_ids
            if not employer or len(employer) != len(worker):
                raise UserError(
                    "The enquiry committee has equal numbers of employer and worker "
                    "representatives (s.24)."
                )
            if rec.employee_id in employer | worker:
                raise UserError("The worker cannot sit on their own enquiry committee.")
            rec._guarded().write(
                {"state": "enquiry", "enquiry_started_on": fields.Date.context_today(self)}
            )
        return True

    def action_conclude_enquiry(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "enquiry":
                raise UserError("Conclude a running enquiry.")
            rec._fix_officer("Concluding an enquiry")
            if not (rec.findings or "").strip() or not rec.proposed_outcome:
                raise UserError("Record the findings and the proposed outcome.")
            rec._guarded().write(
                {
                    "state": "concluded",
                    "enquiry_concluded_on": today,
                    "enquiry_overdue": bool(rec.enquiry_due and today > rec.enquiry_due),
                }
            )
        return True

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "concluded":
                raise UserError("The decision is requested once the enquiry is concluded.")
        return super().action_request_approval(justification=justification)

    def _fix_open_dismissal_exit(self):
        """A dismissal decision opens the employee's draft dismissal exit (s.23),
        linked to this case; HR confirms it. Nothing followed the decision
        before: the dismissed worker stayed on the books (M21 audit E12)."""
        self.ensure_one()
        Exit = self.env["fix.hr.exit"].sudo()
        open_exit = Exit.search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("state", "not in", ("cancelled", "settled")),
            ],
            limit=1,
        )
        if open_exit:
            self.message_post(
                body="Dismissal decided; %s already has exit %s open: link it to this case."
                % (self.employee_id.name, open_exit.name)
            )
            return open_exit
        ex = Exit.create(
            {
                "employee_id": self.employee_id.id,
                "company_id": self.company_id.id or self.env.company.id,
                "exit_type": "dismissal",
                "disciplinary_case_id": self.id,
                "last_working_day": fields.Date.context_today(self),
                "reason": "Dismissal for misconduct decided on %s (BLA s.23)." % self.name,
            }
        )
        self.message_post(body="Dismissal exit %s opened for HR to confirm." % ex.name)
        return ex

    def action_decide(self):
        """The employer's decision (approval inbox only)."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "concluded":
                raise UserError("Decide a concluded enquiry.")
            decider = rec._people_decider()
            rec._guarded().write(
                {
                    "state": "decided",
                    "outcome": rec.proposed_outcome,
                    "decided_by_id": decider.id,
                    "decided_on": fields.Date.context_today(self),
                }
            )
            if rec.suspended:
                rec._fix_end_suspension()
            if rec.outcome == "dismissal":
                rec._fix_open_dismissal_exit()
            publish(
                self.env,
                "disciplinary.decided",
                "fix.hr.disciplinary.case",
                rec.id,
                {"employee_id": rec.employee_id.id, "case": rec.name, "outcome": rec.outcome},
            )
        return True

    def _approval_on_rejected(self, comment):
        # the decision is sent back: the enquiry's findings stay, the outcome is reconsidered
        for rec in self:
            rec._guarded().write({"state": "enquiry"})
            rec.message_post(body="Decision returned: %s" % (comment or ""))

    def action_withdraw(self):
        for rec in self:
            if rec.state in ("decided", "cancelled"):
                raise UserError("A decided case is not withdrawn.")
            rec._fix_officer("Withdrawing a case")
            if rec.suspended:
                rec._fix_end_suspension()
            rec._guarded().write({"state": "cancelled"})
        return True

    # ---- suspension pending enquiry (s.24) --------------------------------------
    def action_suspend(self, days=SUSPENSION_MAX_DAYS):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state not in ("charged", "explained", "hearing", "enquiry"):
                raise UserError("A suspension is pending enquiry of a served charge.")
            if rec.suspended or rec.suspended_from:
                raise UserError("%s was already suspended once." % rec.name)
            rec._fix_officer("Suspending a worker")
            days = int(days or SUSPENSION_MAX_DAYS)
            if not 0 < days <= SUSPENSION_MAX_DAYS:
                raise UserError("A suspension lasts at most %d days (s.24)." % SUSPENSION_MAX_DAYS)
            pct = (rec.company_id or self.env.company).fix_hr_suspension_subsistence_pct
            if not pct:
                # M21-F20 readiness note: the rate is the owner's (labour
                # counsel to rule, BLA s.24). The setting sits at 0 = not
                # ruled, so NO suspension can start until it is set.
                raise UserError(
                    "The subsistence allowance rate for a suspended worker is not ruled: "
                    "the company setting fix_hr_suspension_subsistence_pct "
                    "(Settings, Companies, Suspense & Separation figures) is 0, so no "
                    "suspension can start until labour counsel rules the rate (OWNER "
                    "decision, BLA s.24)."
                )
            until = today + relativedelta(days=days - 1)
            rec._guarded().write(
                {
                    "suspended": True,
                    "suspended_from": today,
                    "suspended_until": until,
                    "subsistence_pct": pct,
                }
            )
            publish(
                self.env,
                "employee.suspended",
                "hr.employee",
                rec.employee_id.id,
                {
                    "employee_id": rec.employee_id.id,
                    "case": rec.name,
                    "from": str(today),
                    "until": str(until),
                    "subsistence_pct": pct,
                },
            )
        return True

    def action_end_suspension(self):
        for rec in self:
            if not rec.suspended:
                raise UserError("%s has no running suspension." % rec.name)
            rec._fix_officer("Ending a suspension")
            rec._fix_end_suspension()
        return True

    def _fix_end_suspension(self):
        today = fields.Date.context_today(self)
        for rec in self.filtered("suspended"):
            rec._guarded().write({"suspended": False, "suspension_ended_on": today})
            publish(
                self.env,
                "employee.suspension_ended",
                "hr.employee",
                rec.employee_id.id,
                {"employee_id": rec.employee_id.id, "case": rec.name, "ended_on": str(today)},
            )

    @api.model
    def _cron_disciplinary_deadlines(self):
        """Daily: end suspensions at their 60-day limit; flag late enquiries."""
        today = fields.Date.context_today(self)
        Case = self.sudo()
        Case.search(
            [("suspended", "=", True), ("suspended_until", "<", today)]
        )._fix_end_suspension()
        late = Case.search(
            [
                ("state", "=", "enquiry"),
                ("enquiry_due", "<", today),
                ("enquiry_overdue", "=", False),
            ]
        )
        for rec in late:
            rec._guarded().write({"enquiry_overdue": True})
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Enquiry overdue: %s" % rec.name,
                note="The enquiry was due by %s (60 days, s.24)." % rec.enquiry_due,
            )
        return len(late)
