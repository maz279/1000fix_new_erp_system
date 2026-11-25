# fix_hse_ops — M59: hazard register, JSA, lone-worker check-ins, road-safety
# checks, drills and occupational health / return-to-work. Incidents,
# inspections, committees, statutory registers and PPE live in fix_hse.py.
#
# A09 audit M59-F6/F9/F10/F11/F16: a lone worker four hours overdue was never
# escalated (no cron, no method) and a colleague could check them out; the
# JSA author approved their own JSA with no approver stamped and blanked its
# controls afterwards; a risk-25 hazard closed with no controls; road checks
# passed by default; drills completed with nobody present.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_hse import _group_users, _int_param, _is_hse, _param, _require_hse

DISPATCHER_GROUP = "cd_field_service.group_fix_field_service_manager"
ACTIVE_ORDER_STATES = ("dispatched", "accepted", "en_route", "arrived", "in_progress")
OCC_HEALTH = "cd_hse.group_occupational_health"
FITNESS_TO_STATUS = {"fit": "fit", "fit_restricted": "restricted", "unfit": "unfit"}


def _risk_band(env, score):
    """Bands of the 5x5 matrix. The bounds are a company convention (a
    setting), not a statutory figure."""
    raw = _param(env, "cd_hse.risk_band_bounds", "4,9,16")
    try:
        low, medium, high = (int(x) for x in raw.split(","))
    except (ValueError, AttributeError):
        low, medium, high = 4, 9, 16
    if score <= low:
        return "low"
    if score <= medium:
        return "medium"
    if score <= high:
        return "high"
    return "critical"


class FixHseHazard(models.Model):
    _name = "fix.hse.hazard"
    _description = "Hazard Register Entry"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "risk_score desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    hazard_type = fields.Selection(
        [
            ("electrical", "Electrical"),
            ("chemical", "Chemical"),
            ("ergonomic", "Ergonomic"),
            ("slip_trip", "Slip / Trip"),
            ("height", "Work at Height"),
            ("road", "Road / Driving"),
            ("battery", "Battery / Thermal"),
            ("other", "Other"),
        ],
        required=True,
        default="electrical",
    )
    likelihood = fields.Integer(string="Likelihood (1-5)", default=3)
    severity = fields.Integer(string="Severity (1-5)", default=3)
    risk_score = fields.Integer(string="Risk Score", compute="_compute_risk", store=True)
    controls = fields.Text(string="Existing Controls")
    residual_likelihood = fields.Integer(string="Residual Likelihood (1-5)")
    residual_severity = fields.Integer(string="Residual Severity (1-5)")
    residual_score = fields.Integer(compute="_compute_risk", store=True)
    # A09 audit: residual risk was typed ("low" on a 25 with no controls).
    residual_risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        compute="_compute_risk",
        store=True,
    )
    controlled_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    controlled_on = fields.Datetime(readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    last_reviewed_on = fields.Date(readonly=True, copy=False)
    next_review_date = fields.Date(readonly=True, copy=False)
    review_due = fields.Boolean(readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("controlled", "Controlled"), ("closed", "Closed")],
        required=True,
        default="open",
    )

    _score_range = models.Constraint(
        "CHECK (likelihood >= 1 AND likelihood <= 5 AND severity >= 1 AND severity <= 5)",
        "Likelihood and severity are 1-5",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "risk_score",
            "residual_score",
            "residual_risk",
            "controlled_by_id",
            "controlled_on",
            "closed_by_id",
            "last_reviewed_on",
            "next_review_date",
            "review_due",
        }

    @api.constrains("residual_likelihood", "residual_severity")
    def _check_residual(self):
        for rec in self:
            for value in (rec.residual_likelihood, rec.residual_severity):
                if value and not 1 <= value <= 5:
                    raise ValidationError("Residual likelihood and severity are 1-5.")

    @api.depends("likelihood", "severity", "residual_likelihood", "residual_severity")
    def _compute_risk(self):
        for rec in self:
            rec.risk_score = (rec.likelihood or 1) * (rec.severity or 1)
            if rec.residual_likelihood and rec.residual_severity:
                rec.residual_score = rec.residual_likelihood * rec.residual_severity
            else:
                # uncontrolled: the residual risk IS the inherent risk
                rec.residual_score = rec.risk_score
            rec.residual_risk = _risk_band(rec.env, rec.residual_score)

    def _fix_next_review(self):
        days = _int_param(self.env, "cd_hse.hazard_review_days", 0)
        return fields.Date.context_today(self) + timedelta(days=days) if days else False

    def action_control(self):
        _require_hse(self.env, "record a hazard's controls")
        for rec in self:
            if rec.state != "open":
                raise UserError("Control an open hazard.")
            if not (rec.controls or "").strip():
                raise UserError("Record the controls of %s." % rec.name)
            if not (rec.residual_likelihood and rec.residual_severity):
                raise UserError("Score the residual likelihood and severity of %s." % rec.name)
            if rec.residual_score > rec.risk_score:
                raise UserError("The residual risk of %s exceeds its inherent risk." % rec.name)
            rec._guarded().write(
                {
                    "state": "controlled",
                    "controlled_by_id": self.env.user.id,
                    "controlled_on": fields.Datetime.now(),
                    "next_review_date": rec._fix_next_review(),
                    "review_due": False,
                }
            )
        return True

    def action_review(self):
        """BRU-HSE-16: the periodic review of a controlled hazard."""
        _require_hse(self.env, "review a hazard")
        for rec in self:
            if rec.state != "controlled":
                raise UserError("Review a controlled hazard.")
            rec._guarded().write(
                {
                    "last_reviewed_on": fields.Date.context_today(rec),
                    "next_review_date": rec._fix_next_review(),
                    "review_due": False,
                }
            )
        return True

    def action_close(self):
        """Closed by an HSE Officer other than the one who recorded the controls."""
        _require_hse(self.env, "close a hazard")
        for rec in self:
            if rec.state != "controlled":
                raise UserError("A hazard is closed once its controls are recorded.")
            if not self.env.su and self.env.user == rec.controlled_by_id:
                raise UserError(
                    "You recorded the controls of %s; another HSE Officer reviews and closes it."
                    % rec.name
                )
            rec._guarded().write({"state": "closed", "closed_by_id": self.env.user.id})
        return True

    @api.model
    def cron_flag_hazard_reviews(self):
        """Controlled hazards past their review date are flagged. Idempotent; superuser."""
        due = self.sudo().search(
            [
                ("state", "=", "controlled"),
                ("next_review_date", "!=", False),
                ("next_review_date", "<", fields.Date.context_today(self)),
                ("review_due", "=", False),
            ]
        )
        for rec in due:
            rec._guarded().write({"review_due": True})
            for user in _group_users(self.env, "cd_hse.group_hse_officer", rec.company_id):
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Hazard review due: %s" % rec.name,
                    user_id=user.id,
                )
        return len(due)


class FixHseJsa(models.Model):
    """A JSA is approved by an HSE Officer other than its author, from the M63
    inbox; an approved JSA changes only through a new revision."""

    _name = "fix.hse.jsa"
    _description = "Job Safety Analysis"
    _inherit = ["mail.thread", "fix.people.approval.mixin"]
    _order = "job_type, id"

    _approval_domain = "hr_hse"
    _approval_apply_method = "action_approve"
    _approval_group = "cd_hse.group_hse_officer"

    _CONTENT = ("name", "job_type", "steps", "hazards", "controls", "ppe_required", "company_id")

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    job_type = fields.Char(string="Job / Task Type", required=True)
    steps = fields.Text(string="Job Steps")
    hazards = fields.Text(string="Hazards per Step")
    controls = fields.Text(string="Controls per Step")
    ppe_required = fields.Char(string="PPE Required")
    revision = fields.Integer(default=1, readonly=True, copy=False)
    previous_id = fields.Many2one("fix.hse.jsa", string="Supersedes", readonly=True, copy=False)
    approved_by_id = fields.Many2one("hr.employee", string="Approved By", readonly=True, copy=False)
    approved_user_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_on = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_user_id",
            "approved_on",
            "revision",
            "previous_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" or r.approval_state == "pending" for r in self):
            locked |= set(self._CONTENT)
        return locked

    def write(self, vals):
        content = set(self._CONTENT) & set(vals)
        if content and not self._fix_guard_open():
            for rec in self:
                locked = rec.state != "draft" or rec.approval_state == "pending"
                if (
                    rec.id
                    and locked
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in content)
                ):
                    raise UserError(
                        "JSA %s is %s; its content changes only through a new revision."
                        % (rec.name, "awaiting approval" if rec.state == "draft" else rec.state)
                    )
        return super().write(vals)

    def action_request_approval(self, justification=None):
        _require_hse(self.env, "submit a JSA")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Submit a draft JSA.")
            if not all((rec[f] or "").strip() for f in ("steps", "hazards", "controls")):
                raise UserError("JSA %s needs its steps, hazards and controls." % rec.name)
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """Routed apply method: an HSE Officer other than the author approves."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft JSA")
            decider = rec._people_decider()
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_user_id": decider.id,
                    "approved_by_id": decider.employee_ids[:1].id or False,
                    "approved_on": fields.Date.context_today(rec),
                }
            )
            if rec.previous_id and rec.previous_id.state == "approved":
                rec.previous_id._guarded().write({"state": "retired"})
        return True

    def action_revise(self):
        """A change to an approved JSA is a new draft revision."""
        _require_hse(self.env, "revise a JSA")
        new = self.browse()
        for rec in self:
            if rec.state != "approved":
                raise UserError("Revise an approved JSA.")
            new |= rec._guarded().copy(
                {"revision": rec.revision + 1, "previous_id": rec.id, "state": "draft"}
            )
        return {"ids": new.ids}

    def action_retire(self):
        _require_hse(self.env, "retire a JSA")
        self.filtered(lambda r: r.state == "approved")._guarded().write({"state": "retired"})
        return True


class FixHseLoneWorker(models.Model):
    _name = "fix.hse.loneworker"
    _description = "Lone-Worker Check-In"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "checkin_time desc, id desc"

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one(
        "hr.employee",
        required=True,
        ondelete="cascade",
        index=True,
        default=lambda self: self.env.user.employee_id,
    )
    checkin_time = fields.Datetime(required=True, default=fields.Datetime.now)
    expected_end = fields.Datetime(string="Expected End")
    location = fields.Char()
    buddy_id = fields.Many2one("hr.employee", string="Emergency Contact")
    # Round 2: a dispatcher opens the session for the technician they sent,
    # on the field order that sent them (FR-HSE-022: M02's job flow).
    field_order_id = fields.Many2one(
        "fix.field.order", string="Field Order", index=True, ondelete="set null"
    )
    opened_by_id = fields.Many2one(
        "res.users", string="Opened By", readonly=True, default=lambda self: self.env.user
    )
    checked_out_at = fields.Datetime(readonly=True, copy=False)
    escalated_on = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("checked_in", "Checked In"),
            ("checked_out", "Checked Out"),
            ("escalated", "Escalated"),
            ("missed", "Missed Check-Out"),
        ],
        required=True,
        default="checked_in",
    )
    notes = fields.Char()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "checked_out_at",
            "escalated_on",
            "opened_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"employee_id", "checkin_time", "field_order_id"}
        return locked

    def _fix_is_dispatcher(self):
        group = self.env.ref(DISPATCHER_GROUP, raise_if_not_found=False)
        return bool(group) and group in self.env.user.all_group_ids

    def _fix_check_dispatch(self, vals):
        """A dispatcher opens a session only for the technician of an active
        field order they can see (their own operating units and companies)."""
        if not self._fix_is_dispatcher():
            raise AccessError("You check in for yourself only.")
        order_id = vals.get("field_order_id")
        if not order_id:
            raise AccessError(
                "A dispatcher opens a session for a technician on the field order that "
                "dispatched them: name the field order."
            )
        Order = self.env["fix.field.order"]
        order = Order.browse(order_id).exists()
        if not order or not order._filtered_access("read"):
            raise AccessError("That field order is not one you dispatch.")
        order = order.sudo()
        if order.technician_id.id != vals.get("employee_id"):
            raise AccessError(
                "Field order %s is dispatched to %s, not to this employee."
                % (order.name, order.technician_id.name or "nobody")
            )
        if order.state not in ACTIVE_ORDER_STATES:
            raise UserError("Field order %s is not active (%s)." % (order.name, order.state))

    @api.constrains("expected_end", "checkin_time")
    def _check_window(self):
        for rec in self:
            if not rec.expected_end or rec.expected_end <= rec.checkin_time:
                raise ValidationError(
                    "A lone-worker check-in needs an expected end after the check-in: the "
                    "missed check-out escalation runs from it (BRU-HSE-09)."
                )

    @api.model_create_multi
    def create(self, vals_list):
        own = self.env.user.employee_id
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.hse.loneworker") or "LW/New"
                )
            if not _is_hse(self.env) and vals.get("employee_id", own.id) != own.id:
                self._fix_check_dispatch(vals)
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open() and {"employee_id", "checkin_time", "expected_end"} & set(
            vals
        ):
            for rec in self:
                if rec.id and rec.state != "checked_in":
                    raise UserError("Session %s is closed." % rec.name)
                if rec.id and any(
                    rec._fix_guard_differs(n, vals[n], rec[n])
                    for n in {"employee_id", "checkin_time"} & set(vals)
                ):
                    raise UserError("Who checked in, and when, is a record.")
        return super().write(vals)

    def action_checkout(self):
        """Only the worker checks themselves out (or an HSE Officer who has
        reached them): a colleague cannot silence an overdue session."""
        for rec in self:
            if not (_is_hse(self.env) or rec.employee_id.user_id == self.env.user):
                raise AccessError("Only %s checks out of this session." % rec.employee_id.name)
            if rec.state == "checked_out":
                raise UserError("Check out a checked-in lone worker")
            rec._guarded().write({"state": "checked_out", "checked_out_at": fields.Datetime.now()})
            if rec.escalated_on:
                rec.message_post(body="Checked out after escalation: the worker is safe.")
        return True

    def action_escalate(self):
        """Escalate now: the buddy, the dispatcher who opened the session or an
        HSE Officer raises the alarm."""
        for rec in self:
            if not (
                _is_hse(self.env)
                or rec.buddy_id.user_id == self.env.user
                or (rec.field_order_id and rec.opened_by_id == self.env.user)
            ):
                raise AccessError(
                    "The emergency contact, the dispatcher or an HSE Officer escalates a session."
                )
        self._fix_escalate()
        return True

    def _fix_escalate(self):
        for rec in self:
            if rec.state not in ("checked_in", "missed"):
                continue
            rec._guarded().write({"state": "escalated", "escalated_on": fields.Datetime.now()})
            publish(
                self.env,
                "hse.loneworker.escalated",
                "fix.hse.loneworker",
                rec.id,
                {
                    "employee": rec.employee_id.name,
                    "location": rec.location or "",
                    "buddy": rec.buddy_id.name if rec.buddy_id else "",
                },
            )

    @api.model
    def cron_escalate_missed_checkouts(self):
        """AUT-HSE-05 / BRU-HSE-09: a session past its expected end plus the
        tolerance escalates by itself. Idempotent (each session once); superuser."""
        tolerance = _int_param(self.env, "cd_hse.loneworker_tolerance_minutes", 0)
        cutoff = fields.Datetime.now() - timedelta(minutes=tolerance)
        due = self.sudo().search(
            [
                ("state", "=", "checked_in"),
                ("expected_end", "!=", False),
                ("expected_end", "<", cutoff),
            ]
        )
        due._guarded().write({"state": "missed"})
        due._fix_escalate()
        return len(due)

    @api.model
    def consume_loneworker_escalated(self, event):
        """The contact chain: the buddy, then every HSE Officer, get an alert."""
        rec = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not rec or rec.activity_ids.filtered(
            lambda a: (a.summary or "").startswith("LONE WORKER")
        ):
            return False
        users = rec.buddy_id.user_id | _group_users(
            self.env, "cd_hse.group_hse_officer", rec.company_id
        )
        if rec.field_order_id and rec.opened_by_id != rec.employee_id.user_id:
            users |= rec.opened_by_id
        for user in users.filtered(lambda u: u.active):
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=fields.Date.context_today(rec),
                summary="LONE WORKER overdue: %s" % rec.employee_id.name,
                note="Expected end %s at %s; contact them now and open an incident if they "
                "cannot be reached." % (rec.expected_end, rec.location or "unknown location"),
                user_id=user.id,
            )
        return True


class FixHseRoadCheck(models.Model):
    """A driver's pre-journey check. It needs a valid driving licence record
    (fix.driver: number, class and expiry), read from the register, never
    typed (BRU-HSE-07, FR-HSE-019)."""

    _name = "fix.hse.roadcheck"
    _description = "Road & Vehicle Safety Check"
    _inherit = ["fix.guarded.mixin"]
    _order = "checked_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one(
        "hr.employee", string="Driver", default=lambda self: self.env.user.employee_id
    )
    vehicle_ref = fields.Char(string="Vehicle / Plate")
    checked_on = fields.Date(required=True, default=fields.Date.context_today)
    # A09 audit M59-36: every item defaulted to OK. An item passes only when
    # the driver ticks it.
    tyres_ok = fields.Boolean(string="Tyres OK", default=False)
    brakes_ok = fields.Boolean(string="Brakes OK", default=False)
    lights_ok = fields.Boolean(string="Lights OK", default=False)
    documents_ok = fields.Boolean(string="Fitness / Insurance OK", default=False)
    driver_id = fields.Many2one("fix.driver", string="Licence Record", readonly=True)
    licence_number = fields.Char(string="Driving Licence No.", readonly=True)
    licence_class = fields.Char(string="Licence Class", readonly=True)
    licence_expiry = fields.Date(string="Licence Valid Until", readonly=True)
    defects = fields.Char()
    passed = fields.Boolean(string="Passed", compute="_compute_passed", store=True)

    @api.depends(
        "tyres_ok", "brakes_ok", "lights_ok", "documents_ok", "licence_expiry", "checked_on"
    )
    def _compute_passed(self):
        for rec in self:
            licence_valid = bool(rec.licence_expiry and rec.licence_expiry >= rec.checked_on)
            rec.passed = bool(
                rec.tyres_ok
                and rec.brakes_ok
                and rec.lights_ok
                and rec.documents_ok
                and licence_valid
            )

    _LICENCE = ("driver_id", "licence_number", "licence_class", "licence_expiry")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._LICENCE)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"employee_id", "checked_on"}
        return locked

    def write(self, vals):
        # `passed` is computed from the checklist and the licence.
        if "passed" in vals and not self.env.su:
            raise UserError("Passed is computed and cannot be set directly.")
        if not self._fix_guard_open() and {"employee_id", "checked_on"} & set(vals):
            for rec in self:
                if any(
                    rec._fix_guard_differs(n, vals[n], rec[n])
                    for n in {"employee_id", "checked_on"} & set(vals)
                ):
                    raise UserError("Whose check it is, and when, is a record.")
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        own = self.env.user.employee_id
        Employee = self.env["hr.employee"].sudo()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.hse.roadcheck") or "RCK/New"
                )
            if not _is_hse(self.env) and vals.get("employee_id", own.id) != own.id:
                raise AccessError("A road check is recorded by its driver or an HSE Officer.")
            driver = Employee.browse(vals.get("employee_id", own.id))
            day = fields.Date.to_date(vals.get("checked_on")) or fields.Date.context_today(self)
            licence, reason = driver._fix_driving_licence(day)
            if not licence:
                raise UserError("Road check refused: %s (BRU-HSE-07)." % reason)
            vals.update(
                {
                    "driver_id": licence.id,
                    "licence_number": licence.license_no,
                    "licence_class": licence.license_class,
                    "licence_expiry": licence.license_expiry,
                }
            )
        return super(FixHseRoadCheck, self._guarded()).create(vals_list)


class FixHseDrill(models.Model):
    _name = "fix.hse.drill"
    _description = "Emergency Drill"
    _inherit = ["fix.guarded.mixin"]
    _order = "scheduled_on desc, id desc"

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    branch_id = fields.Many2one("fix.branch", string="Branch")
    drill_type = fields.Selection(
        [
            ("fire", "Fire Evacuation"),
            ("earthquake", "Earthquake"),
            ("first_aid", "First Aid"),
            ("chemical", "Chemical Spill"),
            ("battery", "Battery Thermal Incident"),
        ],
        required=True,
        default="fire",
    )
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    completed_on = fields.Date(readonly=True)
    participants = fields.Integer()
    duration_min = fields.Integer(string="Duration (minutes)")
    findings = fields.Char()
    state = fields.Selection(
        [("planned", "Planned"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        required=True,
        default="planned",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "completed_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "planned" for r in self):
            locked |= {"participants", "duration_min", "findings", "drill_type", "scheduled_on"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.hse.drill") or "DRL/New"
        return super().create(vals_list)

    def write(self, vals):
        frozen = {"participants", "duration_min", "findings", "drill_type", "scheduled_on"} & set(
            vals
        )
        if frozen and not self._fix_guard_open():
            for rec in self:
                if (
                    rec.id
                    and rec.state != "planned"
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen)
                ):
                    raise UserError("Drill %s is %s; its record is frozen." % (rec.name, rec.state))
        return super().write(vals)

    def action_complete(self):
        _require_hse(self.env, "complete a drill")
        for rec in self:
            if rec.state != "planned":
                raise UserError("Complete a planned drill")
            if (rec.participants or 0) <= 0 or (rec.duration_min or 0) <= 0:
                raise UserError(
                    "Record the participants and duration of drill %s before completing it."
                    % rec.name
                )
            rec._guarded().write(
                {"state": "completed", "completed_on": fields.Date.context_today(self)}
            )
        return True

    def action_cancel(self):
        _require_hse(self.env, "cancel a drill")
        self.filtered(lambda r: r.state == "planned")._guarded().write({"state": "cancelled"})
        return True


class FixHseHealth(models.Model):
    """Occupational health records: Occupational Health only (ACL), with a
    full change trail (A09 audit M59-43: an 'unfit' rewritten to 'fit' left
    no trace)."""

    _name = "fix.hse.health"
    _description = "Occupational Health / Return-to-Work"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "record_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    record_type = fields.Selection(
        [
            ("medical", "Periodic Medical"),
            ("return_to_work", "Return to Work"),
            ("restriction", "Work Restriction"),
            ("vaccination", "Vaccination"),
        ],
        required=True,
        default="medical",
        tracking=True,
    )
    record_date = fields.Date(required=True, default=fields.Date.context_today, tracking=True)
    valid_until = fields.Date(tracking=True)
    fitness = fields.Selection(
        [
            ("fit", "Fit for Duty"),
            ("fit_restricted", "Fit with Restrictions"),
            ("unfit", "Unfit"),
            ("pending", "Pending Review"),
        ],
        required=True,
        default="pending",
        tracking=True,
    )
    restrictions = fields.Char(string="Medical Restrictions (clinical)", tracking=True)
    # BRU-HSE-15 / T-06: what scheduling and the manager may see. Functional
    # only ("no ladder work"), never the diagnosis.
    work_restriction = fields.Char(
        string="Work Restriction (shareable)",
        tracking=True,
        help="Published with the fitness status. Functional terms only, never a diagnosis.",
    )
    fitness_status_id = fields.Many2one(
        "fix.hse.fitness.status", string="Published Fitness Status", readonly=True, copy=False
    )
    clinician = fields.Char(tracking=True)
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], required=True, default="open", tracking=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "fitness_status_id"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.hse.health") or "OH/New"
        return super().create(vals_list)

    def action_publish_fitness(self):
        """Occupational Health publishes the decision as a fitness status:
        fit, restricted or unfit, with the functional restriction only. HSE,
        the line manager and return-to-work read that, never this record."""
        if not (self.env.su or self.env.user.has_group(OCC_HEALTH)):
            raise AccessError("Only Occupational Health publishes a fitness status.")
        Status = self.env["fix.hse.fitness.status"].sudo()
        for rec in self:
            if rec.fitness == "pending":
                raise UserError("%s has no fitness decision yet." % rec.name)
            status = FITNESS_TO_STATUS[rec.fitness]
            if status == "restricted" and not (rec.work_restriction or "").strip():
                raise UserError(
                    "State the work restriction to publish (functional terms, no diagnosis)."
                )
            new = Status._fix_publish(
                rec.employee_id,
                status,
                (rec.work_restriction or "").strip() if status == "restricted" else False,
                rec.record_date,
                rec.valid_until,
                health=rec,
                decided_by=self.env.user,
            )
            rec._guarded().write({"fitness_status_id": new.id})
        return True

    def write(self, vals):
        if (
            not self._fix_guard_open()
            and self.filtered(lambda r: r.id and r.state == "closed")
            and set(vals) - {"message_main_attachment_id"}
        ):
            raise UserError("A closed health record is a record; open a new one.")
        return super().write(vals)

    def action_close(self):
        if not (self.env.su or self.env.user.has_group("cd_hse.group_occupational_health")):
            raise AccessError("Only Occupational Health closes a health record.")
        self._guarded().write({"state": "closed"})
        return True
