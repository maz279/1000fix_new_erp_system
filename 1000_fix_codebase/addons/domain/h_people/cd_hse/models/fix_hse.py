# fix_hse — M59: HSE incidents + Labour Rules safety (P09-M08).
#
# A09 workflow audit (2026-11-03), M59 findings F2-F15. A plain employee
# closed an un-notified reportable accident and downgraded a colleague's
# injury report; the same employee could not report a serious injury at all;
# an incident escalated after reporting never entered the Form 28 register;
# the DIFE notice was a typed "x"; the register's append-only rule fell to
# two writes; inspections and committees were compliant by default. Here:
#   * every state and stamp moves only through its transition, and the
#     original report is immutable (fix.guarded.mixin, BRU-HSE-02);
#   * the register entry is opened whenever an incident becomes reportable,
#     with sudo, so any employee can report (BRU-HSE-01);
#   * closure needs the investigation, the CAPA verified by someone else and,
#     for a reportable accident, the DIFE notice (BRU-HSE-04/05/06);
#   * the notice is dispatched by the notification authority with the Form 27
#     on file, lateness is recorded and a cron escalates the clock;
#   * injury compensation is approved from the M63 inbox and handed to
#     payroll as `hse.compensation.awarded` (I5).
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

REPORTABLE_TYPES = ("injury", "battery_thermal", "fire", "chemical_exposure")
SEVERITY_ORDER = ("low", "medium", "high")


def _param(env, key, default):
    return env["ir.config_parameter"].sudo().get_param(key, default)


def _int_param(env, key, default):
    try:
        return int(_param(env, key, default) or 0)
    except (TypeError, ValueError):
        return int(default)


def _is_hse(env):
    return env.su or env.user.has_group("cd_hse.group_hse_officer")


def _require_hse(env, what):
    if not _is_hse(env):
        raise AccessError("Only an HSE Officer may %s." % what)


def _group_users(env, xmlid, company=None):
    group = env.ref(xmlid, raise_if_not_found=False)
    if not group:
        return env["res.users"]
    users = group.sudo().all_user_ids.filtered(lambda u: u.active and not u.share)
    if company:
        users = users.filtered(lambda u: company in u.company_ids)
    return users


def _holiday_dates(env):
    if "fix.hr.holiday" in env:
        return set(env["fix.hr.holiday"].sudo().search([]).mapped("date"))
    return set()


def _add_bd_working_days(start_dt, working_days=2, holiday_dates=()):
    """Advance start_dt by N Bangladesh working days (skipping Fri/Sat and holidays, BLA s.80)."""
    cur = start_dt
    added = 0
    hol_set = set(holiday_dates or ())
    while added < working_days:
        cur = cur + timedelta(days=1)
        if cur.weekday() in (4, 5):  # Friday=4, Saturday=5
            continue
        if cur.date() in hol_set:
            continue
        added += 1
    return cur


def _sub_bd_working_days(start_dt, working_days=1, holiday_dates=()):
    """Step start_dt back by N Bangladesh working days."""
    cur = start_dt
    taken = 0
    hol_set = set(holiday_dates or ())
    while taken < working_days:
        cur = cur - timedelta(days=1)
        if cur.weekday() in (4, 5) or cur.date() in hol_set:
            continue
        taken += 1
    return cur


class FixHseIncident(models.Model):
    """M59: Workplace incident and near-miss tracking with automated event publication."""

    _name = "fix.hse.incident"
    _description = "HSE Incident"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    # The original report (BRU-HSE-02): set when reporting, never rewritten.
    # A reclassification is an HSE Officer's recorded act (action_reclassify).
    _REPORT = (
        "incident_type",
        "severity",
        "description",
        "accident_datetime",
        "injured_employee_id",
        "employee_id",
        "company_id",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    incident_type = fields.Selection(
        [
            ("injury", "Injury / First Aid"),
            ("near_miss", "Near Miss"),
            ("property_damage", "Property Damage"),
            ("fire", "Fire Outbreak"),
            ("battery_thermal", "Battery Thermal Runaway"),
            ("chemical_exposure", "Chemical / Fume Exposure"),
            ("environmental", "Environmental Spill"),
        ],
        required=True,
        default="near_miss",
        tracking=True,
    )
    severity = fields.Selection(
        [
            ("low", "Low (Minor / First Aid)"),
            ("medium", "Medium (Medical Treatment / Lost Time)"),
            ("high", "High (Critical / Hospitalization / DIFE Reportable)"),
        ],
        default="low",
        required=True,
        tracking=True,
    )
    branch_id = fields.Many2one("fix.branch", string="Branch")
    employee_id = fields.Many2one(
        "hr.employee",
        string="Reported By",
        default=lambda self: self.env.user.employee_id,
    )
    injured_employee_id = fields.Many2one("hr.employee", string="Injured Person")
    description = fields.Text(required=True)
    is_reportable = fields.Boolean(
        string="DIFE Reportable",
        compute="_compute_notice_due",
        store=True,
        help="Opens a Form 28 register entry and needs the DIFE notice before closure.",
    )
    # BRU-HSE-01 / T-10: an anonymous report keeps no link to its reporter:
    # it is written by the system user, with no reporter, no chatter author
    # and no follower (create()). Set at reporting, never changed.
    anonymous = fields.Boolean(
        string="Reported Anonymously",
        help="The system does not record or resolve the reporter's identity.",
    )
    triaged_by_id = fields.Many2one("res.users", string="Triaged By", readonly=True, copy=False)
    triaged_on = fields.Datetime(readonly=True, copy=False)
    triage_note = fields.Text(readonly=True, copy=False)
    # investigation (BRU-HSE-05) and CAPA (BRU-HSE-06), added, never
    # substituted. Round 2 (F8): the team, the root causes and the CAPA
    # actions are child records with owners, due dates and verification.
    investigation_findings = fields.Text()
    investigation_member_ids = fields.One2many(
        "fix.hse.investigation.member", "incident_id", string="Investigation Team"
    )
    root_cause_ids = fields.One2many("fix.hse.root.cause", "incident_id", string="Root Causes")
    capa_ids = fields.One2many("fix.hse.capa", "incident_id", string="CAPA Actions")
    capa_open_count = fields.Integer(compute="_compute_capa", string="CAPA Not Verified")
    capa_verified = fields.Boolean(compute="_compute_capa", string="Every CAPA Verified")
    investigated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    investigation_started_on = fields.Datetime(readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    closed_on = fields.Datetime(readonly=True, copy=False)
    alert_sent_on = fields.Datetime(string="Serious-Incident Alert Sent", readonly=True, copy=False)
    statutory_record_id = fields.Many2one(
        "fix.statutory.accident.register", string="Statutory Accident Record", readonly=True
    )
    state = fields.Selection(
        [
            ("reported", "Reported"),
            ("investigating", "Investigating"),
            ("action_taken", "Action Taken"),
            ("closed", "Closed"),
        ],
        default="reported",
        required=True,
        tracking=True,
    )
    reported_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    accident_datetime = fields.Datetime(string="Accident Date & Time", default=fields.Datetime.now)
    notice_due = fields.Datetime(
        string="DIFE Notice Deadline (Working Days, BLA s.80)",
        compute="_compute_notice_due",
        store=True,
    )
    notice_form = fields.Selection(
        [
            ("form_27", "Form 27 - Fatal / Lost-Time Accident Notice (BLR r.70)"),
            ("form_27a", "Form 27(a) - Dangerous Occurrence Notice (BLR r.70)"),
            ("form_27b", "Form 27(b) - Minor Injury Notice (BLR r.70)"),
            ("none", "Not Reportable"),
        ],
        string="Statutory DIFE Notice Form",
        compute="_compute_notice_due",
        store=True,
    )
    immediate_notification_required = fields.Boolean(
        string="Immediate Phone/Fax Notice Required (BLA s.80)",
        compute="_compute_notice_due",
        store=True,
    )
    dife_notice_ref = fields.Char(string="DIFE Form 27/27(a) Dispatch Ref", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "statutory_record_id",
            "dife_notice_ref",
            "investigated_by_id",
            "investigation_started_on",
            "triaged_by_id",
            "triaged_on",
            "triage_note",
            "closed_by_id",
            "closed_on",
            "alert_sent_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= set(self._REPORT) | {"anonymous"}
        if any(r.state == "closed" for r in self):
            locked |= {"investigation_findings"}
        return locked

    @api.depends("capa_ids.state")
    def _compute_capa(self):
        for rec in self:
            live = rec.sudo().capa_ids.filtered(lambda c: c.state != "cancelled")
            rec.capa_open_count = len(live.filtered(lambda c: c.state != "verified"))
            rec.capa_verified = bool(live) and not rec.capa_open_count

    @api.depends("accident_datetime", "reported_at", "incident_type", "severity")
    def _compute_notice_due(self):
        # The window is a decision for labour counsel (spec Q-04): a setting
        # that keeps the 2 working days the code has always used.
        days = _int_param(self.env, "cd_hse.dife_notice_working_days", 2)
        hol_dates = _holiday_dates(self.env)
        for rec in self:
            base_dt = rec.accident_datetime or rec.reported_at or fields.Datetime.now()
            if rec.incident_type in REPORTABLE_TYPES and rec.severity in ("medium", "high"):
                rec.notice_due = _add_bd_working_days(base_dt, days, hol_dates)
                if rec.incident_type == "injury":
                    rec.notice_form = "form_27"
                else:
                    rec.notice_form = "form_27a"
                rec.immediate_notification_required = rec.severity == "high"
                rec.is_reportable = True
            elif rec.incident_type == "injury" and rec.severity == "low":
                rec.notice_due = _add_bd_working_days(base_dt, days, hol_dates)
                rec.notice_form = "form_27b"
                rec.immediate_notification_required = False
                rec.is_reportable = False
            else:
                rec.notice_due = False
                rec.notice_form = "none"
                rec.immediate_notification_required = False
                rec.is_reportable = False

    # ---- reporting --------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        if any(v.get("anonymous") for v in vals_list) and self.env.uid != SUPERUSER_ID:
            return self._fix_create_anonymous(vals_list)
        own = self.env.user.employee_id
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("fix.hse.incident") or "HSE/New"
            if (
                not vals.get("anonymous")
                and not _is_hse(self.env)
                and vals.get("employee_id")
                and vals["employee_id"] != own.id
            ):
                raise AccessError("You report incidents in your own name.")
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "hse.incident_reported",
                "fix.hse.incident",
                rec.id,
                {"type": rec.incident_type, "severity": rec.severity},
            )
        recs._fix_open_register()
        return recs

    def _fix_create_anonymous(self, vals_list):
        """BRU-HSE-01 / T-10: file the report as the system user, so neither
        create_uid, the reporter, a chatter author nor a follower links it to
        the person who filed it. Returned in the system user's environment:
        the reporter keeps no access to what they filed."""
        if len(vals_list) != 1:
            raise UserError("File one anonymous report at a time.")
        if not self.env.user.has_group("base.group_user"):
            raise AccessError("Only an employee files an anonymous safety report.")
        vals = dict(vals_list[0])
        allowed = {
            "anonymous",
            "incident_type",
            "severity",
            "description",
            "branch_id",
            "operating_unit_id",
            "accident_datetime",
            "injured_employee_id",
            "company_id",
        }
        unknown = set(vals) - allowed
        if unknown:
            raise UserError(
                "An anonymous report carries what happened, where and when, and who was hurt; "
                "not %s." % ", ".join(sorted(unknown))
            )
        if vals.get("company_id") and vals["company_id"] not in self.env.user.company_ids.ids:
            raise AccessError("Report for a company you work for.")
        vals.setdefault("company_id", self.env.company.id)
        vals.update({"anonymous": True, "employee_id": False})
        system = self.with_user(SUPERUSER_ID).with_context(
            mail_create_nolog=True,
            mail_create_nosubscribe=True,
            mail_notrack=True,
            tracking_disable=True,
        )
        return system.create([vals])

    def write(self, vals):
        if not self._fix_guard_open():
            if "anonymous" in vals and any(
                r.id and r._fix_guard_differs("anonymous", vals["anonymous"], r.anonymous)
                for r in self
            ):
                raise UserError("Whether a report was anonymous is fixed when it is filed.")
            touched = set(self._REPORT) & set(vals)
            for rec in self:
                if not touched or not rec.id:
                    break
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in touched):
                    raise UserError(
                        "The original report of %s cannot be rewritten (BRU-HSE-02). An HSE "
                        "Officer reclassifies it, with a reason, from the incident." % rec.name
                    )
            if self.filtered(lambda r: r.id and r.state == "closed") and set(vals) - {
                "message_main_attachment_id"
            }:
                raise UserError("A closed incident no longer changes.")
        result = super().write(vals)
        if {"incident_type", "severity"} & set(vals):
            self.filtered("id")._fix_open_register()
        return result

    def _fix_open_register(self):
        """BLA s.90 / BLR r.73: a reportable incident has a Form 28 entry, opened
        whenever the incident becomes reportable (at report or on escalation).
        Opened with sudo: the reporter needs no right on the register."""
        Register = self.env["fix.statutory.accident.register"].sudo()
        for rec in self:
            if not rec.is_reportable or rec.statutory_record_id:
                continue
            worker = rec.injured_employee_id or rec.employee_id
            if not worker and rec.anonymous:
                # never refuse a safety report: the HSE Officer names the
                # injured worker at triage, which opens the register entry
                rec.message_post(
                    body="Reportable, filed anonymously with no injured worker named: triage "
                    "must name the worker to open the Form 28 entry."
                )
                continue
            if not worker:
                raise UserError(
                    "A %s-severity %s must name the injured worker or the reporter: "
                    "the BLA 2006 s.90 / BLR 2015 r.73 accident register records "
                    "the worker involved." % (rec.severity, rec.incident_type)
                )
            # The statutory register records the date the accident HAPPENED,
            # not the date it was keyed in.
            reg = Register.create(
                {
                    "name": f"BLA-Accident: {rec.name}",
                    "incident_id": rec.id,
                    "employee_id": worker.id,
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id or False,
                    "accident_date": (
                        fields.Datetime.to_datetime(rec.accident_datetime).date()
                        if rec.accident_datetime
                        else fields.Date.today()
                    ),
                    "nature_of_injury": rec.description,
                    "notice_form_type": rec.notice_form
                    if rec.notice_form in ("form_27", "form_27a")
                    else "form_27",
                }
            )
            rec.sudo().write({"statutory_record_id": reg.id})

    # ---- transitions ------------------------------------------------------
    def _needs_investigation(self):
        self.ensure_one()
        return self.is_reportable or self.severity in ("medium", "high")

    def action_investigate(self):
        _require_hse(self.env, "open an investigation")
        for rec in self:
            if rec.state != "reported":
                raise UserError("Investigate a reported incident.")
            rec._guarded().write(
                {
                    "state": "investigating",
                    "investigated_by_id": self.env.user.id,
                    "investigation_started_on": fields.Datetime.now(),
                }
            )
        return True

    def action_record_action_taken(self):
        _require_hse(self.env, "record the corrective action")
        for rec in self:
            if rec.state != "investigating":
                raise UserError("Record the action on an incident under investigation.")
            data = rec.sudo()
            live = data.capa_ids.filtered(lambda c: c.state != "cancelled")
            missing = []
            if not live:
                missing.append("at least one corrective / preventive action (CAPA)")
            elif live.filtered(lambda c: not c.owner_id or not c.due_date):
                missing.append("an owner and a due date on every CAPA")
            if rec._needs_investigation():
                if not data.root_cause_ids:
                    missing.append("the root cause (BRU-HSE-05)")
                if not data.investigation_member_ids:
                    missing.append("the investigation team")
            if missing:
                raise UserError("%s needs %s." % (rec.name, ", ".join(missing)))
            rec._guarded().write({"state": "action_taken"})
        return True

    def _fix_close_problems(self):
        self.ensure_one()
        problems = []
        if self.state != "action_taken":
            problems.append("the investigation and corrective action are not recorded")
        live = self.sudo().capa_ids.filtered(lambda c: c.state != "cancelled")
        if not live:
            problems.append("no corrective action")
        elif self._needs_investigation():
            if live.filtered(lambda c: c.state != "verified"):
                problems.append("a CAPA is not verified effective (BRU-HSE-06)")
        elif live.filtered(lambda c: c.state == "open"):
            problems.append("a CAPA is not done")
        if self.is_reportable and not self.statutory_record_id.dife_notified:
            problems.append(
                "BLA 2006 s.80 / BLR 2015 r.70: the DIFE Form 27/27(a) notice is not dispatched"
            )
        return problems

    def action_close(self):
        _require_hse(self.env, "close an incident")
        for rec in self:
            problems = rec._fix_close_problems()
            if problems:
                raise UserError("Cannot close %s: %s." % (rec.name, "; ".join(problems)))
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.user.id,
                    "closed_on": fields.Datetime.now(),
                }
            )
        return True

    def action_triage(self, note=None, injured_employee=None):
        """An HSE Officer triages a report (an anonymous one above all): the
        triage note, and the injured worker where the report did not name one,
        which opens the Form 28 entry."""
        _require_hse(self.env, "triage a report")
        if not (note or "").strip():
            raise UserError("Record the triage note.")
        for rec in self:
            if rec.state == "closed":
                raise UserError("%s is closed." % rec.name)
            vals = {
                "triaged_by_id": self.env.uid,
                "triaged_on": fields.Datetime.now(),
                "triage_note": note.strip(),
            }
            if injured_employee and not rec.injured_employee_id:
                emp = self.env["hr.employee"].sudo().browse(int(str(injured_employee).strip()))
                if not emp.exists():
                    raise UserError("No employee %s." % injured_employee)
                vals["injured_employee_id"] = emp.id
            rec._guarded().write(vals)
            rec._fix_open_register()
        return True

    def action_reclassify(self, severity=None, incident_type=None, reason=None):
        """An HSE Officer reclassifies the report, with a reason, on the record."""
        _require_hse(self.env, "reclassify an incident")
        if not (reason or "").strip():
            raise UserError("State why the incident is reclassified.")
        for rec in self:
            if rec.state == "closed":
                raise UserError("A closed incident is not reclassified.")
            vals = {}
            if severity and severity != rec.severity:
                vals["severity"] = severity
            if incident_type and incident_type != rec.incident_type:
                vals["incident_type"] = incident_type
            if not vals:
                raise UserError("Nothing to reclassify.")
            old = "%s / %s" % (rec.incident_type, rec.severity)
            rec._guarded().write(vals)
            rec.message_post(
                body="Reclassified from %s to %s by %s: %s"
                % (old, "%s / %s" % (rec.incident_type, rec.severity), self.env.user.name, reason)
            )
        return True

    def action_escalate(self, reason=None):
        """Raise the severity one step (the workspace's reclassification)."""
        for rec in self:
            idx = SEVERITY_ORDER.index(rec.severity)
            if idx == len(SEVERITY_ORDER) - 1:
                raise UserError("%s is already at the highest severity." % rec.name)
            rec.action_reclassify(severity=SEVERITY_ORDER[idx + 1], reason=reason)
        return True

    def action_dispatch_dife_notice(self, notice_ref=None):
        for rec in self:
            if not rec.statutory_record_id:
                raise UserError("%s is not a reportable accident." % rec.name)
            rec.statutory_record_id.action_notify_dife(notice_ref=notice_ref)
        return True

    def action_notify_dife(self, notice_ref=None):
        """The workspace's Notify DIFE button (A09 audit M59-20: it was missing)."""
        return self.action_dispatch_dife_notice(notice_ref=notice_ref)

    # ---- BRU-HSE-03: a serious incident alerts at once (relay consumer) ------
    @api.model
    def consume_incident_reported(self, event):
        rec = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not rec or rec.alert_sent_on:
            return False
        if not (rec.immediate_notification_required or rec.is_reportable):
            return False
        users = _group_users(self.env, "cd_hse.group_hse_officer", rec.company_id) | _group_users(
            self.env, "cd_hse.group_statutory_notifier", rec.company_id
        )
        for user in users:
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=fields.Date.context_today(rec),
                summary="Serious incident %s" % rec.name,
                note="%s / %s reported. DIFE notice due %s."
                % (rec.incident_type, rec.severity, rec.notice_due or "n/a"),
                user_id=user.id,
            )
        rec._guarded().write({"alert_sent_on": fields.Datetime.now()})
        return True


class FixSafetyInspection(models.Model):
    """M59: Branch and cleanroom safety compliance inspections."""

    _name = "fix.safety.inspection"
    _description = "Safety Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "inspected_on desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)
    inspected_on = fields.Date(required=True, default=fields.Date.today)
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    # A09 audit M59-34: every check defaulted to "OK", so an inspection the
    # form never answered completed 'done'. A check passes only when ticked.
    fire_extinguisher_ok = fields.Boolean(
        default=False, string="Fire Extinguisher Inspected & Valid"
    )
    emergency_exit_ok = fields.Boolean(default=False, string="Emergency Exits Unobstructed")
    first_aid_ok = fields.Boolean(default=False, string="First Aid Box Stocked (BLR Rule 67)")
    electrical_ok = fields.Boolean(default=False, string="Electrical Wiring & Grounding Safe")
    esd_grounding_ok = fields.Boolean(
        default=False, string="ESD Benches & Mats Grounded (ANSI/ESD S20.20)"
    )
    fume_extraction_ok = fields.Boolean(
        default=False, string="Soldering Fume Extractor Operational"
    )
    chemical_storage_ok = fields.Boolean(
        default=False, string="IPA & Solvents Stored in Flammable Cabinet"
    )
    findings = fields.Text()
    # Both counts are derived from the checklist so they cannot drift from it.
    # "Critical" is the life-safety subset (BLR r.55/r.57/r.67).
    findings_count = fields.Integer(string="Failed Checks", compute="_compute_findings", store=True)
    critical_findings = fields.Integer(
        string="Critical Failed Checks", compute="_compute_findings", store=True
    )
    completed_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    _CHECKS = (
        "fire_extinguisher_ok",
        "emergency_exit_ok",
        "first_aid_ok",
        "electrical_ok",
        "esd_grounding_ok",
        "fume_extraction_ok",
        "chemical_storage_ok",
    )
    _CRITICAL_CHECKS = (
        "fire_extinguisher_ok",
        "emergency_exit_ok",
        "first_aid_ok",
        "electrical_ok",
    )

    @api.depends(*_CHECKS)
    def _compute_findings(self):
        for rec in self:
            rec.findings_count = sum(1 for f in rec._CHECKS if not getattr(rec, f))
            rec.critical_findings = sum(1 for f in rec._CRITICAL_CHECKS if not getattr(rec, f))

    state = fields.Selection(
        [("scheduled", "Scheduled"), ("done", "Done"), ("follow_up", "Follow-up Required")],
        default="scheduled",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "completed_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state == "done" for r in self):
            locked |= set(self._CHECKS) | {"findings", "inspector_id", "inspected_on"}
        return locked

    def write(self, vals):
        frozen = (set(self._CHECKS) | {"inspector_id", "inspected_on"}) & set(vals)
        if frozen and not self._fix_guard_open():
            for rec in self:
                if (
                    rec.id
                    and rec.state == "done"
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen)
                ):
                    raise UserError("Inspection %s is done; schedule a new one." % rec.name)
        return super().write(vals)

    def action_complete(self):
        _require_hse(self.env, "complete an inspection")
        for rec in self:
            if rec.state == "done":
                raise UserError("Inspection %s is already done." % rec.name)
            if not rec.inspector_id:
                raise UserError("Name the inspector of %s." % rec.name)
            needs = bool(rec.findings_count)
            if needs and not (rec.findings or "").strip():
                raise UserError(
                    "%s has %d failed check(s): record the findings."
                    % (rec.name, rec.findings_count)
                )
            rec._guarded().write(
                {"state": "follow_up" if needs else "done", "completed_by_id": self.env.user.id}
            )
        return True


class FixSafetyCommittee(models.Model):
    """M59: Statutory Safety Committee established under Bangladesh Labour Act 2006 §90A
    and Bangladesh Labour Rules 2015 Rule 81."""

    _name = "fix.safety.committee"
    _description = "Statutory Safety Committee"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    _FREQUENCY_MONTHS = {"monthly": 1, "bimonthly": 2, "quarterly": 3}

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Committee Designation", required=True)
    branch_id = fields.Many2one("fix.branch", string="Service Centre / Branch", required=True)
    formation_date = fields.Date(string="Formation Date", default=fields.Date.today, required=True)
    chairperson_id = fields.Many2one(
        "hr.employee", string="Chairperson (Employer Rep)", required=True
    )
    secretary_id = fields.Many2one("hr.employee", string="Secretary (Worker Rep)", required=True)
    member_ids = fields.One2many("fix.safety.committee.member", "committee_id", string="Members")
    member_count = fields.Integer(
        string="Total Committee Members", compute="_compute_members", store=True
    )
    worker_rep_count = fields.Integer(compute="_compute_members", store=True)
    employer_rep_count = fields.Integer(compute="_compute_members", store=True)
    meeting_frequency = fields.Selection(
        [("monthly", "Monthly"), ("bimonthly", "Every 2 Months"), ("quarterly", "Quarterly")],
        default="monthly",
        required=True,
    )
    meeting_ids = fields.One2many("fix.safety.committee.meeting", "committee_id", string="Meetings")
    last_meeting_date = fields.Date(
        string="Last Meeting Conducted", compute="_compute_meetings", store=True
    )
    next_meeting_date = fields.Date(
        string="Next Meeting Due", compute="_compute_meetings", store=True
    )
    meeting_overdue = fields.Boolean(compute="_compute_overdue", string="Meeting Overdue")
    recent_minutes = fields.Text(
        string="Minutes of Latest Meeting", compute="_compute_meetings", store=True
    )
    # A09 audit M59-37: "DIFE Registered" defaulted to True for a committee
    # nobody had notified. It is recorded, with the evidence, by an action.
    dife_registered = fields.Boolean(string="DIFE Registered", default=False, readonly=True)
    dife_registration_ref = fields.Char(readonly=True)
    dife_registration_file = fields.Binary(attachment=True, copy=False)
    dife_registration_filename = fields.Char(copy=False)
    state = fields.Selection(
        [
            ("draft", "Being Constituted"),
            ("active", "Active & Compliant"),
            ("review_needed", "Reconstitution Needed"),
            ("dissolved", "Dissolved"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "dife_registered",
            "dife_registration_ref",
        }

    @api.depends("member_ids", "member_ids.side")
    def _compute_members(self):
        for rec in self:
            rec.member_count = len(rec.member_ids)
            rec.worker_rep_count = len(rec.member_ids.filtered(lambda m: m.side == "worker"))
            rec.employer_rep_count = len(rec.member_ids.filtered(lambda m: m.side == "employer"))

    @api.depends(
        "meeting_ids.meeting_date", "meeting_ids.minutes", "meeting_frequency", "formation_date"
    )
    def _compute_meetings(self):
        for rec in self:
            last = rec.meeting_ids.sorted("meeting_date")[-1:] if rec.meeting_ids else None
            rec.last_meeting_date = last.meeting_date if last else False
            rec.recent_minutes = last.minutes if last else False
            start = rec.last_meeting_date or rec.formation_date
            months = rec._FREQUENCY_MONTHS.get(rec.meeting_frequency, 1)
            rec.next_meeting_date = start + relativedelta(months=months) if start else False

    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.meeting_overdue = bool(
                rec.state in ("active", "review_needed")
                and rec.next_meeting_date
                and rec.next_meeting_date < today
            )

    def _fix_composition_problems(self):
        self.ensure_one()
        minimum = _int_param(self.env, "cd_hse.committee_min_members", 6)
        problems = []
        if self.member_count < minimum:
            problems.append(
                "%d member(s); the committee needs at least %d" % (self.member_count, minimum)
            )
        if self.chairperson_id == self.secretary_id:
            problems.append("the chairperson and the secretary are the same person")
        if not self.worker_rep_count or not self.employer_rep_count:
            problems.append("it needs both worker and employer representatives (BLR r.81)")
        members = self.member_ids.mapped("employee_id")
        if self.chairperson_id not in members or self.secretary_id not in members:
            problems.append("the chairperson and the secretary must be members")
        return problems

    def action_activate(self):
        _require_hse(self.env, "constitute a safety committee")
        for rec in self:
            if rec.state not in ("draft", "review_needed"):
                raise UserError("Constitute a committee being formed or reconstituted.")
            problems = rec._fix_composition_problems()
            if problems:
                raise UserError("%s cannot be active: %s." % (rec.name, "; ".join(problems)))
            rec._guarded().write({"state": "active"})
        return True

    def action_record_dife_registration(self, registration_ref=None):
        _require_hse(self.env, "record a DIFE registration")
        if not (registration_ref or "").strip():
            raise UserError("Enter the DIFE registration reference.")
        for rec in self:
            if not rec.dife_registration_file:
                raise UserError("Attach the DIFE acknowledgement of %s first." % rec.name)
            rec._guarded().write(
                {"dife_registered": True, "dife_registration_ref": registration_ref.strip()}
            )
        return True

    def action_record_meeting(self, minutes_text=""):
        """BRU-HSE-17: a meeting is a record with its minutes."""
        _require_hse(self.env, "record a committee meeting")
        if not (minutes_text or "").strip():
            raise UserError("Record the minutes of the meeting.")
        for rec in self:
            if rec.state not in ("active", "review_needed"):
                raise UserError("%s is not a constituted committee." % rec.name)
            self.env["fix.safety.committee.meeting"].create(
                {
                    "committee_id": rec.id,
                    "meeting_date": fields.Date.context_today(rec),
                    "minutes": minutes_text.strip(),
                }
            )
        return True

    def action_dissolve(self):
        _require_hse(self.env, "dissolve a committee")
        self._guarded().write({"state": "dissolved"})
        return True

    @api.model
    def cron_flag_overdue_meetings(self):
        """A committee whose meeting is overdue needs attention. Idempotent; superuser."""
        today = fields.Date.context_today(self)
        due = self.sudo().search([("state", "=", "active"), ("next_meeting_date", "<", today)])
        for rec in due:
            rec._guarded().write({"state": "review_needed"})
            rec.message_post(
                body="Safety committee meeting overdue since %s (BRU-HSE-17)."
                % rec.next_meeting_date
            )
            for user in _group_users(self.env, "cd_hse.group_hse_officer", rec.company_id):
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Safety committee meeting overdue: %s" % rec.name,
                    user_id=user.id,
                )
        return len(due)


class FixSafetyCommitteeMember(models.Model):
    _name = "fix.safety.committee.member"
    _description = "Safety Committee Member"

    committee_id = fields.Many2one(
        "fix.safety.committee", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="committee_id.company_id", store=True)
    employee_id = fields.Many2one("hr.employee", required=True)
    side = fields.Selection(
        [("employer", "Employer Representative"), ("worker", "Worker Representative")],
        required=True,
        default="worker",
    )
    term_start = fields.Date(default=fields.Date.today)

    _member_once = models.Constraint(
        "UNIQUE (committee_id, employee_id)", "An employee sits on a committee once"
    )


class FixSafetyCommitteeMeeting(models.Model):
    _name = "fix.safety.committee.meeting"
    _description = "Safety Committee Meeting"
    _order = "meeting_date desc, id desc"

    committee_id = fields.Many2one(
        "fix.safety.committee", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="committee_id.company_id", store=True)
    meeting_date = fields.Date(required=True, default=fields.Date.today)
    attendee_ids = fields.Many2many("hr.employee", string="Attendees")
    minutes = fields.Text(required=True)
    actions = fields.Text(string="Actions Agreed")
    minutes_file = fields.Binary(attachment=True)

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "hse.safety_committee_meeting",
                "fix.safety.committee",
                rec.committee_id.id,
                {
                    "committee": rec.committee_id.name,
                    "branch": rec.committee_id.branch_id.name or "",
                },
            )
        return recs

    def write(self, vals):
        if not self.env.su:
            raise UserError("Committee minutes are a record; add a new meeting instead.")
        return super().write(vals)


class FixStatutoryAccidentRegister(models.Model):
    """M59: Mandatory Accident and Dangerous Occurrence Register under
    Bangladesh Labour Act 2006 §80/§89/§90 & Bangladesh Labour Rules 2015 Rule 70 (Forms 27/27a/27b)
    and Rule 73 (Form 28; legacy ref Form 33/34)."""

    _name = "fix.statutory.accident.register"
    _description = "Statutory Accident Register (BLA s.80/s.90 Form 27/28 & Form 33/34)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.people.approval.mixin"]
    _order = "accident_date desc"

    # I5: injury compensation is approved from the M63 inbox, never by the
    # HSE Officer who assessed it, and then handed to payroll.
    _approval_domain = "hr_hse"
    _approval_apply_method = "action_approve_compensation"
    _approval_group = "cd_hse.group_injury_compensation_approver"

    _FACTS = ("employee_id", "accident_date", "nature_of_injury", "incident_id")
    _COMPENSATION_TERMS = ("compensation_proposed", "compensation_basis", "compensation_reason")

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Statutory Record ID", required=True)
    register_entry_no = fields.Char(string="Form 28 Register Serial No", default="New")
    incident_id = fields.Many2one("fix.hse.incident", string="Linked HSE Incident")
    employee_id = fields.Many2one("hr.employee", string="Worker Involved", required=True)
    accident_date = fields.Date(string="Date of Accident", default=fields.Date.today, required=True)
    nature_of_injury = fields.Text(string="Nature and Cause of Injury", required=True)
    affected_body_part = fields.Char(string="Affected Body Part (e.g. Eye, Hand, Respiratory)")
    lost_work_days = fields.Integer(string="Lost Work Days", default=0)
    notice_form_type = fields.Selection(
        [
            ("form_27", "Form 27 - Fatal / Lost-Time Accident (BLR r.70)"),
            ("form_27a", "Form 27(a) - Dangerous Occurrence (BLR r.70)"),
            ("form_27b", "Form 27(b) - Minor Injury Notice (BLR r.70)"),
        ],
        string="Notice Form Type (BLR r.70)",
        default="form_27",
    )
    notice_due = fields.Datetime(
        related="incident_id.notice_due", store=True, string="DIFE Notice Deadline"
    )
    dife_notified = fields.Boolean(
        string="DIFE Form 27 / 27(a) Notice Dispatched",
        default=False,
        readonly=True,
        tracking=True,
        help="Notice to DIFE within the statutory window for a reportable injury: "
        "BLA 2006 s.80 with BLR 2015 r.70 (Forms 27 / 27(a) / 27(b)). The "
        "register itself is kept under s.90 with r.73 (Form 28).",
    )
    dife_notification_date = fields.Date(string="DIFE Notice Date", readonly=True)
    dife_ack_ref = fields.Char(string="DIFE Acknowledgement Reference", readonly=True)
    dife_notice_file = fields.Binary(string="Form 27 / 27(a) as Dispatched", attachment=True)
    dife_notice_filename = fields.Char()
    dife_notified_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    notified_late = fields.Boolean(
        string="Notified After the Deadline", readonly=True, copy=False, tracking=True
    )
    notice_escalation_level = fields.Integer(
        readonly=True, copy=False, help="0 none, 1 due within a working day, 2 deadline passed."
    )
    half_year_return_due = fields.Date(
        string="Form 28 Half-Yearly Return Due Date",
        compute="_compute_half_year_due",
        store=True,
    )
    half_year_return_filed_on = fields.Date(string="Form 28 Return Filed On")
    return_to_work_date = fields.Date(
        string="Worker Returned to Work On",
        readonly=True,
        copy=False,
        help="Closes the lost-time period for the Form 28 return and the "
        "BLA 2006 Ch. XII compensation assessment. Recorded only against an "
        "Occupational Health fitness decision (action_record_return_to_work).",
    )
    return_fitness_id = fields.Many2one(
        "fix.hse.fitness.status", string="Return-to-Work Fitness", readonly=True, copy=False
    )
    return_fitness_status = fields.Selection(
        related="return_fitness_id.status", string="Returned As"
    )
    compensation_basis = fields.Selection(
        [
            ("temporary", "Temporary Disablement"),
            ("permanent_partial", "Permanent Partial Disablement"),
            ("permanent_total", "Permanent Total Disablement"),
            ("death", "Death"),
        ],
        string="Compensation Basis (BLA Ch. XII)",
    )
    compensation_proposed = fields.Float(
        string="Assessed Compensation (BDT)",
        help="The amount assessed under BLA 2006 Chapter XII. The schedule itself is not "
        "computed here (no verified source in the repository): the assessment is "
        "approved by someone other than the assessor.",
    )
    compensation_reason = fields.Text(string="Assessment Basis / Workings")
    statutory_compensation_bdt = fields.Float(
        string="Approved Statutory Compensation (BDT)",
        readonly=True,
        help="Compensation approved under BLA 2006 Chapter XII and handed to payroll.",
    )
    compensation_approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    compensation_approved_on = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("recorded", "Recorded"),
            ("dife_notified", "DIFE Notified"),
            ("compensation_settled", "Compensation Approved"),
            ("closed", "Closed"),
        ],
        default="recorded",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "dife_notified",
            "dife_notification_date",
            "dife_ack_ref",
            "dife_notified_by_id",
            "notified_late",
            "notice_escalation_level",
            "statutory_compensation_bdt",
            "compensation_approved_by_id",
            "compensation_approved_on",
            "return_to_work_date",
            "return_fitness_id",
        }

    def action_record_return_to_work(self, return_date=None):
        """The worker returns on the strength of Occupational Health's fitness
        decision: fit, or fit with restrictions, valid on the return date and
        made after the accident. HSE sees the status, never the medical record."""
        _require_hse(self.env, "record a return to work")
        day = fields.Date.to_date(return_date) if return_date else fields.Date.context_today(self)
        for rec in self:
            if rec.return_to_work_date:
                raise UserError("The return to work of %s is recorded." % rec.name)
            if day < rec.accident_date:
                raise UserError("A worker returns after the accident, not before it.")
            status = rec.employee_id._fix_fitness_status(day)
            if not status:
                raise UserError(
                    "%s has no Occupational Health fitness decision valid on %s: a return to "
                    "work needs one." % (rec.employee_id.name, day)
                )
            if status.status == "unfit":
                raise UserError(
                    "Occupational Health has %s unfit for work; the return is refused."
                    % rec.employee_id.name
                )
            if status.valid_from < rec.accident_date:
                raise UserError(
                    "The fitness decision of %s predates the accident: Occupational Health "
                    "assesses the worker again before the return." % rec.employee_id.name
                )
            rec._guarded().write({"return_to_work_date": day, "return_fitness_id": status.id})
            rec.message_post(
                body="Returned to work on %s as %s%s."
                % (
                    day,
                    dict(status._fields["status"].selection)[status.status],
                    ": %s" % status.work_restriction if status.work_restriction else "",
                )
            )
        return True

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.dife_notified or r.state != "recorded" for r in self):
            locked |= set(self._FACTS) | {"dife_notice_file", "dife_notice_filename"}
        if any(r.approval_state in ("pending", "approved") for r in self):
            locked |= set(self._COMPENSATION_TERMS)
        return locked

    @api.depends("accident_date")
    def _compute_half_year_due(self):
        from datetime import date as dt_date

        for rec in self:
            if rec.accident_date:
                d = fields.Date.to_date(rec.accident_date)
                if d.month <= 6:
                    rec.half_year_return_due = dt_date(d.year, 7, 15)
                else:
                    rec.half_year_return_due = dt_date(d.year + 1, 1, 15)
            else:
                rec.half_year_return_due = False

    @api.model_create_multi
    def create(self, vals_list):
        """Allocate the Form 28 serial (BLR 2015 r.73)."""
        for vals in vals_list:
            if vals.get("register_entry_no", "New") in ("New", False, ""):
                vals["register_entry_no"] = (
                    self.env["ir.sequence"].next_by_code("fix.statutory.accident.register") or "New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            facts = set(self._FACTS) & set(vals)
            terms = set(self._COMPENSATION_TERMS) & set(vals)
            for rec in self:
                if not rec.id:
                    continue
                # dife_notified / dife_ack_ref are guarded, so the old two-step
                # (un-notify, then edit) no longer opens the facts (M59-F7).
                frozen = rec.dife_notified or rec.dife_ack_ref or rec.state != "recorded"
                if (
                    facts
                    and frozen
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in facts)
                ):
                    raise UserError(
                        "BLA 2006 s.90 / BLR 2015 r.73: Statutory Form 28 Accident Register "
                        "is append-only; core accident facts cannot be modified after DIFE "
                        "notification."
                    )
                if "dife_notice_file" in vals and rec.dife_notified:
                    raise UserError("The Form 27 as dispatched is a record; it no longer changes.")
                if (
                    terms
                    and rec.approval_state == "approved"
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in terms)
                ):
                    raise UserError(
                        "The compensation of %s was approved and handed to payroll." % rec.name
                    )
        pending = self.filtered(lambda r: r.id and r.approval_state == "pending")
        before = {r.id: (r.compensation_basis, r.compensation_reason) for r in pending}
        result = super().write(vals)
        for rec in pending:
            if rec.approval_state == "pending" and before[rec.id] != (
                rec.compensation_basis,
                rec.compensation_reason,
            ):
                rec._approval_void("the compensation assessment changed while awaiting approval")
        return result

    def unlink(self):
        if self and not self.env.su:
            raise UserError(
                "BLA 2006 s.90 / BLR 2015 r.73: Statutory Form 28 Accident Register entries "
                "are append-only and cannot be deleted."
            )
        return super().unlink()

    # ---- the DIFE notice (BLA s.80 / BLR r.70) -------------------------------
    def action_notify_dife(self, notice_ref=None):
        """Record the dispatch of Form 27 / 27(a), by the notification authority,
        with the form on file. Lateness against the deadline is recorded."""
        if not (self.env.su or self.env.user.has_group("cd_hse.group_statutory_notifier")):
            raise AccessError(
                "Only the Statutory Notification Authority dispatches the DIFE notice."
            )
        if not (notice_ref or "").strip():
            raise UserError("Enter the DIFE dispatch / acknowledgement reference.")
        now = fields.Datetime.now()
        for rec in self:
            if rec.dife_notified:
                raise UserError("The DIFE notice for %s is already recorded." % rec.name)
            if not rec.dife_notice_file:
                raise UserError(
                    "Attach the Form 27 / 27(a) as dispatched to %s before recording the "
                    "notice." % rec.name
                )
            rec._guarded().write(
                {
                    "dife_notified": True,
                    "dife_notification_date": fields.Date.context_today(rec),
                    "dife_ack_ref": notice_ref.strip(),
                    "dife_notified_by_id": self.env.user.id,
                    "notified_late": bool(rec.notice_due and now > rec.notice_due),
                    "state": "dife_notified",
                }
            )
            if rec.incident_id:
                rec.incident_id.sudo().write({"dife_notice_ref": notice_ref.strip()})
            publish(
                self.env,
                "hse.dife_accident_reported",
                "fix.statutory.accident.register",
                rec.id,
                {
                    "worker": rec.employee_id.name,
                    "date": str(rec.accident_date),
                    "late": rec.notified_late,
                },
            )
        return True

    @api.model
    def cron_escalate_dife_notices(self):
        """The statutory clock escalates (BRU-HSE-04, AC-08): at T-1 working
        day before the deadline, and again when it passes. Idempotent (each
        level once); superuser."""
        # Reportable incidents without a register entry (escalated before the
        # register opened on escalation, live M59-F4) get theirs first.
        Incident = self.env["fix.hse.incident"].sudo()
        for inc in Incident.search(
            [("is_reportable", "=", True), ("statutory_record_id", "=", False)]
        ):
            if inc.injured_employee_id or inc.employee_id:
                inc._fix_open_register()
            else:
                inc.message_post(
                    body="Reportable, but no worker is named: the Form 28 register entry cannot "
                    "be opened. Record the injured worker."
                )
        now = fields.Datetime.now()
        hol = _holiday_dates(self.env)
        open_regs = self.sudo().search(
            [
                ("dife_notified", "=", False),
                ("notice_due", "!=", False),
                ("notice_escalation_level", "<", 2),
            ]
        )
        escalated = 0
        for rec in open_regs:
            if now >= rec.notice_due:
                level, what = 2, "has PASSED (deadline %s)" % rec.notice_due
            elif now >= _sub_bd_working_days(rec.notice_due, 1, hol):
                level, what = 1, "is due within one working day (deadline %s)" % rec.notice_due
            else:
                continue
            if rec.notice_escalation_level >= level:
                continue
            note = "DIFE notice for %s (%s) %s." % (rec.name, rec.employee_id.name, what)
            for user in _group_users(self.env, "cd_hse.group_statutory_notifier", rec.company_id):
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=fields.Date.context_today(rec),
                    summary="DIFE notice: %s" % rec.name,
                    note=note,
                    user_id=user.id,
                )
            rec.message_post(body=note)
            rec._guarded().write({"notice_escalation_level": level})
            escalated += 1
        return escalated

    # ---- injury compensation (BLA Ch. XII; I5) ----------------------------------
    def _approval_amount(self) -> float:
        return self.compensation_proposed or 0.0

    def action_request_approval(self, justification=None):
        _require_hse(self.env, "submit an injury compensation assessment")
        for rec in self:
            if rec.state != "dife_notified":
                raise UserError(
                    "Compensation for %s is assessed after the DIFE notice is recorded." % rec.name
                )
            if (rec.compensation_proposed or 0.0) <= 0 or not rec.compensation_basis:
                raise UserError("Assess the compensation basis and amount for %s." % rec.name)
            if not (rec.compensation_reason or "").strip():
                raise UserError("Record the workings behind the compensation for %s." % rec.name)
        return super().action_request_approval(justification=justification)

    def action_approve_compensation(self):
        """Routed apply method: approve the compensation and hand it to payroll."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "dife_notified":
                raise UserError("Approve compensation on a notified register entry.")
            amount = rec.compensation_proposed
            rec._guarded().write(
                {
                    "statutory_compensation_bdt": amount,
                    "compensation_approved_by_id": rec._people_decider().id,
                    "compensation_approved_on": fields.Datetime.now(),
                    "state": "compensation_settled",
                }
            )
            publish(
                self.env,
                "hse.compensation.awarded",
                "fix.statutory.accident.register",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "amount": amount,
                    "incident_id": rec.incident_id.id or None,
                    "reason": "%s: %s"
                    % (
                        dict(self._fields["compensation_basis"].selection)[rec.compensation_basis],
                        rec.compensation_reason,
                    ),
                },
            )
        return True

    def action_close(self):
        _require_hse(self.env, "close a register entry")
        for rec in self:
            if rec.state not in ("dife_notified", "compensation_settled"):
                raise UserError("Close a register entry once its DIFE notice is recorded.")
            if rec.approval_state == "pending":
                raise UserError("%s has a compensation awaiting approval." % rec.name)
            rec._guarded().write({"state": "closed"})
        return True


class FixPpeRegister(models.Model):
    """M59: Personal Protective Equipment standard register for workshop technicians."""

    _name = "fix.ppe.register"
    _description = "PPE Safety Equipment Register"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="PPE Item Name", required=True)
    item_type = fields.Selection(
        [
            ("esd_wristband", "Anti-Static / ESD Wristband"),
            ("goggles", "Impact & Chemical Safety Goggles"),
            ("fume_mask", "Soldering Fume Respirator / Activated Carbon Mask"),
            ("thermal_gloves", "Heat-Resistant SMD/BGA Rework Gloves"),
            ("lab_coat", "Anti-Static Workshop Lab Coat"),
            ("first_aid_kit", "First Aid Emergency Kit"),
        ],
        required=True,
        default="esd_wristband",
    )
    regulatory_standard = fields.Char(
        string="Applicable Standard", default="ANSI/ESD S20.20 / OSHA 1910.133"
    )
    stock_quantity = fields.Integer(string="Available In Stock", default=0)
    min_required_quantity = fields.Integer(string="Minimum Threshold", default=10)
    # A09 audit M59-30: the state changed only when a button was pressed, so
    # stock 0 / minimum 10 showed "adequate". It follows the stock now.
    state = fields.Selection(
        [("compliant", "Stock Adequate"), ("replenish", "Replenishment Required")],
        compute="_compute_state",
        store=True,
    )

    def write(self, vals):
        # `state` is computed; a direct write would stand until the next recompute.
        if "state" in vals and not self.env.su:
            raise UserError(
                "%s is computed and cannot be set directly." % self._fields["state"].string
            )
        return super().write(vals)

    @api.depends("stock_quantity", "min_required_quantity")
    def _compute_state(self):
        for rec in self:
            rec.state = (
                "replenish" if rec.stock_quantity <= rec.min_required_quantity else "compliant"
            )

    @api.constrains("stock_quantity", "min_required_quantity")
    def _check_quantities(self):
        for rec in self:
            if rec.stock_quantity < 0 or rec.min_required_quantity < 0:
                raise ValidationError("PPE quantities cannot be negative.")


class FixPpeIssue(models.Model):
    """BRU-HSE-12 / FR-HSE-031: PPE issued to a named employee, acknowledged
    by that employee before the work."""

    _name = "fix.ppe.issue"
    _description = "PPE Issue to Employee"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "issued_on desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    ppe_id = fields.Many2one("fix.ppe.register", string="PPE Item", required=True)
    quantity = fields.Integer(default=1, required=True)
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    replace_by = fields.Date(string="Replace By")
    issued_by_id = fields.Many2one("res.users", readonly=True, default=lambda self: self.env.user)
    acknowledged = fields.Boolean(readonly=True, copy=False, tracking=True)
    acknowledged_on = fields.Datetime(readonly=True, copy=False)
    # FR-HSE-032: replacement. A new issue that replaces this one closes it;
    # until then the cron alerts once the replace-by date is reached and
    # escalates once it is overdue.
    replaces_id = fields.Many2one(
        "fix.ppe.issue", string="Replaces Issue", ondelete="set null", copy=False
    )
    replaced = fields.Boolean(readonly=True, copy=False)
    replacement_alert_level = fields.Integer(
        readonly=True, copy=False, help="0 none, 1 replacement due, 2 overdue and escalated."
    )
    replacement_alerted_on = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "acknowledged",
            "acknowledged_on",
            "issued_by_id",
            "replaced",
            "replacement_alert_level",
            "replacement_alerted_on",
        }

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError("Issue at least one item.")

    @api.model_create_multi
    def create(self, vals_list):
        _require_hse(self.env, "issue PPE")
        recs = super().create(vals_list)
        for rec in recs:
            item = rec.ppe_id.sudo()
            if item.stock_quantity < rec.quantity:
                raise UserError("Only %d of %s in stock." % (item.stock_quantity, item.name))
            item.write({"stock_quantity": item.stock_quantity - rec.quantity})
            old = rec.replaces_id.sudo()
            if old:
                if old.employee_id != rec.employee_id or old.ppe_id != rec.ppe_id:
                    raise UserError("A replacement is the same item for the same employee.")
                if old.replaced:
                    raise UserError("%s was already replaced." % old.display_name)
                old._guarded().write({"replaced": True})
        return recs

    @api.model
    def cron_ppe_replacement_alerts(self):
        """FR-HSE-032 / BRU-HSE-12: PPE past its replace-by date alerts the
        holder and the HSE Officers (level 1); once it is overdue beyond the
        grace period it escalates to the line manager too (level 2). Each
        level once per issue: idempotent. Superuser."""
        today = fields.Date.context_today(self)
        grace = _int_param(self.env, "cd_hse.ppe_replacement_grace_days", 0)
        due = self.sudo().search(
            [
                ("replaced", "=", False),
                ("replace_by", "!=", False),
                ("replace_by", "<=", today),
                ("replacement_alert_level", "<", 2),
            ]
        )
        raised = 0
        for rec in due:
            overdue = (today - rec.replace_by).days > grace
            level = 2 if overdue else 1
            if rec.replacement_alert_level >= level:
                continue
            emp = rec.employee_id.sudo()
            users = _group_users(self.env, "cd_hse.group_hse_officer", rec.company_id)
            users |= emp.user_id
            if level == 2:
                users |= emp.parent_id.user_id
            what = (
                "is OVERDUE for replacement since %s" % rec.replace_by
                if level == 2
                else "is due for replacement (%s)" % rec.replace_by
            )
            note = "%s issued to %s %s." % (rec.ppe_id.name, emp.name, what)
            for user in users.filtered(lambda u: u.active and not u.share):
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=today,
                    summary="PPE replacement: %s" % emp.name,
                    note=note,
                    user_id=user.id,
                )
            rec.message_post(body=note)
            rec._guarded().write(
                {"replacement_alert_level": level, "replacement_alerted_on": fields.Datetime.now()}
            )
            raised += 1
        return raised

    def write(self, vals):
        if not self._fix_guard_open() and self.filtered(lambda r: r.id and r.acknowledged):
            raise UserError("An acknowledged PPE issue is a record; issue a replacement instead.")
        return super().write(vals)

    def action_acknowledge(self):
        """The employee who received the PPE acknowledges it, nobody else."""
        for rec in self:
            if not self.env.su and rec.employee_id.user_id != self.env.user:
                raise AccessError("Only %s acknowledges this PPE issue." % rec.employee_id.name)
            if rec.acknowledged:
                continue
            rec.sudo()._guarded().write(
                {"acknowledged": True, "acknowledged_on": fields.Datetime.now()}
            )
        return True


class FixHazardousSubstanceRegister(models.Model):
    """M59: Hazardous substance, chemical solvent, and battery management register."""

    _name = "fix.hazardous.substance.register"
    _description = "Hazardous Substance Register"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Chemical / Substance Name", required=True)
    un_number = fields.Char(string="UN Transport Number (e.g. UN 1219 for IPA, UN 3481 for Li-Ion)")
    storage_location = fields.Char(string="Approved Storage Location", required=True)
    max_allowable_litres = fields.Float(string="Max Permissible Storage Limit", default=50.0)
    current_stock_litres = fields.Float(string="Current Stock On-Hand", default=0.0)
    # A09 audit M59-33: the MSDS defaulted to "on file".
    msds_on_file = fields.Boolean(string="Safety Data Sheet (MSDS) Available", default=False)
    fire_suppression_type = fields.Char(
        string="Required Fire Extinguisher", default="Class B CO2 / Dry Chemical"
    )
    quarantined = fields.Boolean(readonly=True, copy=False, tracking=True)
    quarantine_reason = fields.Text(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("safe", "Normal / Safe"),
            ("threshold_exceeded", "Limit Exceeded"),
            ("no_msds", "Safety Data Sheet Missing"),
            ("quarantined", "Quarantined / Defective"),
        ],
        compute="_compute_state",
        store=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "quarantined", "quarantine_reason"}

    @api.depends("current_stock_litres", "max_allowable_litres", "msds_on_file", "quarantined")
    def _compute_state(self):
        for rec in self:
            if rec.quarantined:
                rec.state = "quarantined"
            elif rec.current_stock_litres > rec.max_allowable_litres:
                rec.state = "threshold_exceeded"
            elif not rec.msds_on_file:
                rec.state = "no_msds"
            else:
                rec.state = "safe"

    def action_quarantine(self, reason=None):
        """BRU-HSE-13: a damaged or swollen battery lot is quarantined, with the reason."""
        _require_hse(self.env, "quarantine a substance")
        if not (reason or "").strip():
            raise UserError("State why it is quarantined.")
        self._guarded().write({"quarantined": True, "quarantine_reason": reason.strip()})
        return True

    def action_release(self):
        _require_hse(self.env, "release a quarantined substance")
        for rec in self:
            rec.message_post(body="Released from quarantine (%s)." % (rec.quarantine_reason or ""))
        self._guarded().write({"quarantined": False, "quarantine_reason": False})
        return True
