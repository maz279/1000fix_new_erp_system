# cd_hr_core — the exit lifecycles round 1 left open (A09 report §6 P2
# "missing lifecycles"; benchmark §2.1 item 10 and §2.3 items 7-8, Verified [45]).
#
#   * s.27(3A) absence without leave: a worker absent more than 10 days without
#     leave is served a notice giving 10 days to explain or rejoin, then 7 more
#     days for self-defence, then is deemed released from the first day of
#     absence. A fix.hr.abandonment case runs that timeline: HR serves the
#     notice (only once the absence is long enough and no approved leave or
#     punch covers it), a daily cron moves the case through its windows, and
#     the deemed resignation is a ROUTED decision (the officer who ran the case
#     and the worker never decide it). Its decision opens the 'abandonment'
#     exit, which then clears and settles like any other. An abandonment exit
#     cannot be confirmed by hand. The day counts are company settings holding
#     the verified 2013 text.
#   * s.31 service certificate: generated on a cleared or settled exit, issued
#     by HR, never by the leaver, once per exit; unsigned until its signed scan
#     is verified (fix.hr.document).
#   * s.19 death in service: an exit type whose settlement goes to the
#     nominees. Payroll computes the figure (I1, cd_payroll_bd); the split
#     across the nominee records already kept (fix.hr.dependant, or the
#     employee's primary nominee) must total 100% and is pinned with the
#     settlement, so a nominee changed after routing voids nothing silently:
#     the settle step refuses it.
import base64
import json

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_hr_controls_common import EXECUTIVE, OFFICER, digest

OPEN_CASE = ("draft", "noticed", "hearing", "decision")


class FixHrAbandonment(models.Model):
    """BLA s.27(3A): absence of more than 10 days without leave."""

    _name = "fix.hr.abandonment"
    _description = "Absence Without Leave Case (BLA s.27(3A))"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "fix.people.approval.mixin",
        "fix.hr.control.mixin",
    ]
    _order = "id desc"

    # Losing employment is decided by the employer's executive role, as the
    # disciplinary punishment is; the officer who ran the case never decides.
    _approval_domain = "hr_exit"
    _approval_apply_method = "action_deem_resigned"
    _approval_group = EXECUTIVE

    name = fields.Char(default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True, ondelete="restrict")
    absence_start_date = fields.Date(
        string="First Day of Absence", required=True, help="Deemed released from this day"
    )
    absent_days = fields.Integer(compute="_compute_absent_days", string="Days Absent")
    notes = fields.Text(string="Attempts to Contact")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("noticed", "Notice Served (to explain or rejoin)"),
            ("hearing", "Self-Defence Window"),
            ("decision", "Awaiting Decision"),
            ("deemed", "Deemed Resigned"),
            ("explained", "Explained / Rejoined"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    notice_date = fields.Date(readonly=True, copy=False)
    reply_days = fields.Integer(readonly=True, copy=False, string="Days to Explain")
    reply_due = fields.Date(compute="_compute_due", store=True, string="Explanation Due")
    hearing_notice_date = fields.Date(readonly=True, copy=False, string="Second Notice On")
    hearing_days = fields.Integer(readonly=True, copy=False, string="Days for Self-Defence")
    hearing_due = fields.Date(compute="_compute_due", store=True, string="Self-Defence Due")
    explanation = fields.Text(string="Worker's Explanation")
    explanation_received_on = fields.Date(readonly=True, copy=False)
    handled_by_id = fields.Many2one("res.users", string="Case Officer", readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Date(readonly=True, copy=False)
    exit_id = fields.Many2one("fix.hr.exit", string="Exit", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "notice_date",
            "reply_days",
            "hearing_notice_date",
            "hearing_days",
            "explanation_received_on",
            "handled_by_id",
            "decided_by_id",
            "decided_on",
            "exit_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"employee_id", "absence_start_date"}
        if self and self.state not in ("noticed", "hearing"):
            locked.add("explanation")
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.hr.abandonment") or "HAB/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = {"employee_id", "absence_start_date"} & set(vals)
            if frozen and any(r.state != "draft" for r in self.filtered("id")):
                raise UserError("A served notice is never re-dated; cancel the case instead.")
        return super().write(vals)

    @api.depends("absence_start_date")
    def _compute_absent_days(self):
        today = fields.Date.context_today(self)
        for rec in self:
            start = rec.absence_start_date
            rec.absent_days = (today - start).days if start and start <= today else 0

    @api.depends("notice_date", "reply_days", "hearing_notice_date", "hearing_days")
    def _compute_due(self):
        for rec in self:
            rec.reply_due = (
                rec.notice_date + relativedelta(days=rec.reply_days) if rec.notice_date else False
            )
            rec.hearing_due = (
                rec.hearing_notice_date + relativedelta(days=rec.hearing_days)
                if rec.hearing_notice_date
                else False
            )

    @api.constrains("absence_start_date")
    def _check_start(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.absence_start_date and rec.absence_start_date > today:
                raise ValidationError("An absence cannot start in the future.")

    @api.constrains("employee_id", "state")
    def _check_one_open_case(self):
        for rec in self.filtered(lambda r: r.state in OPEN_CASE):
            if self.sudo().search_count(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("state", "in", OPEN_CASE),
                    ("id", "!=", rec.id),
                ]
            ):
                raise ValidationError("%s already has an open absence case." % rec.employee_id.name)

    def _approval_preparers(self):
        return self.mapped("handled_by_id")

    def _fix_officer(self, what):
        self._hr_require(OFFICER, what)
        if not self.env.su and self.env.user in self._hr_subject_users():
            raise UserError("You cannot run an absence case about yourself.")

    # ---- what covers the absence --------------------------------------------------
    def _fix_absence_covered(self):
        """Why the absence is not unauthorised, or '' (approved leave, a punch)."""
        self.ensure_one()
        today = fields.Date.context_today(self)
        leave = (
            self.env["fix.leave.request"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("state", "=", "approved"),
                    ("date_from", "<", today),
                    ("date_to", ">=", self.absence_start_date),
                ],
                limit=1,
            )
        )
        if leave:
            return "approved leave %s to %s covers part of the absence" % (
                leave.date_from,
                leave.date_to,
            )
        if "fix.attendance.record" in self.env:
            punch = (
                self.env["fix.attendance.record"]
                .sudo()
                .search(
                    [
                        ("employee_id", "=", self.employee_id.id),
                        ("check_in", ">=", fields.Datetime.to_datetime(self.absence_start_date)),
                    ],
                    limit=1,
                )
            )
            if punch:
                return "attendance is recorded on %s" % punch.check_in.date()
        return ""

    # ---- the timeline -------------------------------------------------------------
    def action_issue_notice(self):
        """Serve the s.27(3A) notice: explain or rejoin within the reply window."""
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Serve the notice of a draft case.")
            rec._fix_officer("Serving an absence notice")
            company = rec.company_id or self.env.company
            threshold = company.fix_hr_abandon_absence_days
            if rec.absent_days <= threshold:
                raise UserError(
                    "%s has been absent %d day(s): the s.27(3A) notice follows an absence of "
                    "more than %d days." % (rec.employee_id.name, rec.absent_days, threshold)
                )
            covered = rec._fix_absence_covered()
            if covered:
                raise UserError("Not an absence without leave: %s." % covered)
            rec._guarded().write(
                {
                    "state": "noticed",
                    "notice_date": today,
                    "reply_days": company.fix_hr_abandon_reply_days,
                    "handled_by_id": self.env.uid,
                }
            )
            rec.message_post(
                body="Notice served (BLA s.27(3A)): explain the absence or rejoin by %s."
                % rec.reply_due
            )
        return True

    def action_record_explanation(self):
        """The worker explained or rejoined: the clock stops and no resignation
        is deemed. Any misconduct is then a disciplinary case (s.23/24)."""
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state not in ("noticed", "hearing", "decision"):
                raise UserError("An explanation answers a served notice.")
            rec._fix_officer("Recording an explanation")
            if not (rec.explanation or "").strip():
                raise UserError("Enter the worker's explanation (or the date they rejoined).")
            req = rec.approval_request_id.sudo()
            if rec.approval_state == "pending" and req.state == "pending":
                req._finish("recalled", "recalled", self.env.user, record_state="none")
            rec._guarded().write({"state": "explained", "explanation_received_on": today})
        return True

    def _fix_open_hearing(self):
        today = fields.Date.context_today(self)
        for rec in self:
            days = (rec.company_id or self.env.company).fix_hr_abandon_hearing_days
            rec._guarded().write(
                {"state": "hearing", "hearing_notice_date": today, "hearing_days": days}
            )
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Absence case %s: second notice" % rec.name,
                note="No explanation by %s. Serve the second notice: %d more days for "
                "self-defence (BLA s.27(3A)), until %s." % (rec.reply_due, days, rec.hearing_due),
                user_id=(rec.handled_by_id or self.env.ref("base.user_admin")).id,
            )

    def action_request_approval(self, justification=None):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state not in ("hearing", "decision") or not rec.hearing_due:
                raise UserError("The decision follows the self-defence window (s.27(3A)).")
            if today <= rec.hearing_due:
                raise UserError(
                    "The worker has until %s for self-defence: the decision cannot come first."
                    % rec.hearing_due
                )
            if rec.state == "hearing":
                rec._guarded().write({"state": "decision"})
        return super().action_request_approval(justification=justification)

    def action_deem_resigned(self):
        """The employer's decision (approval inbox only): the worker is deemed
        released from the first day of absence; the abandonment exit opens."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        today = fields.Date.context_today(self)
        Exit = self.env["fix.hr.exit"].sudo()
        for rec in self:
            if rec.state != "decision":
                raise UserError("Decide a case whose self-defence window has passed.")
            last_day = rec.absence_start_date - relativedelta(days=1)
            ex = Exit._guarded().create(
                {
                    "employee_id": rec.employee_id.id,
                    "company_id": rec.company_id.id,
                    "exit_type": "abandonment",
                    "last_working_day": last_day,
                    "reason": "Deemed resigned under BLA s.27(3A) (%s): absent from %s without "
                    "leave, notices of %s and %s unanswered."
                    % (rec.name, rec.absence_start_date, rec.notice_date, rec.hearing_notice_date),
                    "abandonment_id": rec.id,
                }
            )
            ex._guarded().write({"state": "notice", "contract_id": ex._fix_active_contract().id})
            rec._guarded().write(
                {
                    "state": "deemed",
                    "decided_by_id": rec._people_decider().id,
                    "decided_on": today,
                    "exit_id": ex.id,
                }
            )
            ex.message_post(body="Opened by the s.27(3A) decision on %s." % rec.name)
        return True

    def _approval_on_rejected(self, comment):
        # the employer declined to deem a resignation: the case closes
        for rec in self:
            rec._guarded().write({"state": "cancelled"})
            rec.message_post(body="Deemed resignation declined: %s" % (comment or ""))

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "noticed", "hearing", "decision"):
                raise UserError("Only an open absence case is cancelled.")
            rec._fix_officer("Cancelling an absence case")
            req = rec.approval_request_id.sudo()
            if rec.approval_state == "pending" and req.state == "pending":
                req._finish("recalled", "recalled", self.env.user, record_state="none")
            rec._guarded().write({"state": "cancelled"})
        return True

    @api.model
    def _cron_abandonment_timeline(self):
        """Daily: an unanswered notice opens the self-defence window; a passed
        self-defence window routes the deemed-resignation decision. Idempotent."""
        today = fields.Date.context_today(self)
        Case = self.sudo()
        to_hearing = Case.search([("state", "=", "noticed"), ("reply_due", "<", today)])
        to_hearing._fix_open_hearing()
        routed = 0
        for rec in Case.search([("state", "=", "hearing"), ("hearing_due", "<", today)]):
            try:
                with self.env.cr.savepoint():
                    rec.action_request_approval(
                        justification="BLA s.27(3A): notices of %s and %s unanswered."
                        % (rec.notice_date, rec.hearing_notice_date)
                    )
                routed += 1
            except UserError as exc:  # e.g. no approver holds the role yet
                rec.message_post(body="The decision could not be routed: %s" % exc)
        return {"hearing": len(to_hearing), "routed": routed}


class FixHrExitLifecycles(models.Model):
    _inherit = "fix.hr.exit"

    exit_type = fields.Selection(
        selection_add=[("death", "Death in Service (s.19)")],
        ondelete={"death": "set default"},
    )
    abandonment_id = fields.Many2one(
        "fix.hr.abandonment", string="Absence Case (s.27(3A))", readonly=True, copy=False
    )
    death_at_work = fields.Boolean(
        string="Death at Work or from a Work Accident",
        help="BLA s.19: 45 days' wages per completed year instead of 30",
    )
    death_certificate_file = fields.Binary(string="Death Certificate", attachment=True)
    death_certificate_filename = fields.Char()
    nominee_payout_lines = fields.Text(
        readonly=True, copy=False, help="The pinned nominee split of the settlement (JSON)"
    )
    service_certificate_id = fields.Many2one(
        "fix.hr.document", string="Service Certificate (s.31)", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "abandonment_id",
            "nominee_payout_lines",
            "service_certificate_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"death_at_work", "death_certificate_file"}
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = {"death_at_work", "death_certificate_file"} & set(vals)
            if frozen and any(r.state != "draft" for r in self.filtered("id")):
                raise UserError("A confirmed exit keeps its terms; cancel it and raise a new one.")
        return super().write(vals)

    # ---- s.27(3A) and s.19 at confirmation ----------------------------------------
    def action_confirm_notice(self):
        for rec in self:
            if rec.exit_type == "abandonment":
                raise UserError(
                    "An abandonment exit is opened by the decision on its absence case "
                    "(BLA s.27(3A)), never confirmed by hand."
                )
            if rec.exit_type == "death":
                if not rec.death_certificate_file:
                    raise UserError(
                        "Attach the death certificate (the last working day is the date of death)."
                    )
                rec._fix_nominee_shares()
        return super().action_confirm_notice()

    @api.depends("exit_type", "notice_date", "last_working_day", "employee_id", "contract_id")
    def _compute_notice(self):
        super()._compute_notice()
        for rec in self.filtered(lambda r: r.exit_type == "death"):
            rec.notice_required_days = 0
            rec.notice_shortfall_days = 0
            rec.notice_basis = "BLA s.19 (death in service): no notice; benefits to the nominee"

    # ---- s.19: the nominees --------------------------------------------------------
    def _fix_nominee_shares(self):
        """[(dependant id or False, name, relation, share %)] totalling 100%."""
        self.ensure_one()
        emp = self.employee_id.sudo()
        nominees = (
            self.env["fix.hr.dependant"]
            .sudo()
            .search([("employee_id", "=", emp.id), ("is_nominee", "=", True)], order="id")
        )
        shares = [(d.id, d.name, d.relation, float(d.nominee_pct or 0.0)) for d in nominees]
        if not shares and emp.nominee_name:
            shares = [
                (False, emp.nominee_name, emp.nominee_relation, float(emp.nominee_pct or 0.0))
            ]
        total = round(sum(s[3] for s in shares), 2)
        if not shares or abs(total - 100.0) > 0.01:
            raise UserError(
                "BLA s.19 pays the death benefit to the nominee: %s's nominee shares total "
                "%.2f%%. Record nominees (Dependants & Nominees) totalling 100%%."
                % (emp.name, total)
            )
        return shares

    def _fix_nominee_split(self, net):
        self.ensure_one()
        shares = self._fix_nominee_shares()
        payees, paid = [], 0.0
        for index, (dep_id, name, relation, pct) in enumerate(shares):
            last = index == len(shares) - 1
            amount = round(net - paid, 2) if last else round(net * pct / 100.0, 2)
            paid += amount
            payees.append(
                {
                    "dependant_id": dep_id,
                    "name": name,
                    "relation": relation,
                    "share_pct": pct,
                    "amount": amount,
                }
            )
        return payees

    def _fix_breakdown(self):
        lines, net, basis, pin = super()._fix_breakdown()
        if self.exit_type == "death":
            pin = digest({"settlement": pin, "payees": self._fix_nominee_split(net)})
        return lines, net, basis, pin

    def action_compute_settlement(self):
        result = super().action_compute_settlement()
        for rec in self.filtered(lambda r: r.exit_type == "death"):
            rec._guarded().write(
                {"nominee_payout_lines": json.dumps(rec._fix_nominee_split(rec.settlement_amount))}
            )
        return result

    def _fix_nominee_payees(self):
        """For payroll (I1 payment): the pinned nominee payees of a death exit."""
        self.ensure_one()
        return json.loads(self.nominee_payout_lines or "[]")

    # ---- s.31: the service certificate ----------------------------------------------
    def action_issue_service_certificate(self):
        """Generate the s.31 certificate of service (HR, never the leaver)."""
        today = fields.Date.context_today(self)
        docs = self.env["fix.hr.document"]
        for rec in self:
            if rec.state not in ("cleared", "settled"):
                raise UserError("The service certificate is issued on a cleared exit (s.31).")
            rec._hr_require(OFFICER, "Issuing a service certificate")
            if not self.env.su and self.env.user in rec._hr_subject_users():
                raise UserError("A service certificate is never self-issued.")
            if rec.service_certificate_id:
                raise UserError(
                    "%s already has service certificate %s."
                    % (rec.name, rec.service_certificate_id.name)
                )
            emp = rec.employee_id.sudo()
            joined = emp.joining_date or emp.joined_date
            text = (
                "1000FiX SERVICES LTD - CERTIFICATE OF SERVICE (BLA 2006 s.31)\n"
                f"Name: {emp.name}\nName (Bengali): {emp.name_bn or ''}\n"
                f"Employee Code: {emp.employee_code or ''}\n"
                f"Designation: {emp.job_title or (emp.position_id.name or '')}\n"
                f"Service: from {joined or ''} to {rec.last_working_day}\n"
                f"Issued: {today}\n"
            ).encode()
            doc = (
                self.env["fix.hr.document"]
                .sudo()
                ._guarded()
                .create(
                    {
                        "employee_id": emp.id,
                        "company_id": rec.company_id.id,
                        "doc_type": "service_certificate",
                        "reference": "S31/%s" % rec.name,
                        "issued_on": today,
                        "generated": True,
                        "file_name": "ServiceCertificate_%s.txt" % (emp.employee_code or emp.id),
                        "file_data": base64.b64encode(text),
                        "notes": "Issued by %s" % self.env.user.name,
                    }
                )
            )
            rec._guarded().write({"service_certificate_id": doc.id})
            docs |= doc
        return {"documents": docs.ids}


class FixHrDocumentServiceCertificate(models.Model):
    _inherit = "fix.hr.document"

    doc_type = fields.Selection(
        selection_add=[("service_certificate", "Certificate of Service (s.31)")],
        ondelete={"service_certificate": "set default"},
    )
