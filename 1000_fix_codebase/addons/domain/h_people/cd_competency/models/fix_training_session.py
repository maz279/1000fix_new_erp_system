# fix_training_session — M22: the scheduled delivery of a course and its
# attendance (FR-LMS-020 session scheduling, FR-LMS-021 enrolment against a
# session with capacity, FR-LMS-023 attendance, FR-LMS-029 external training).
#
# M22 capture audit (2026-11-13): the "Schedule & Attendance" screen and the
# Training Delivery page captured an enrolment that had no session, no date,
# no trainer, no venue and no attendance, so nothing a training coordinator
# schedules or a trainer records on the day could be entered anywhere. A
# session now carries the course, trainer (internal employee or an external
# provider), venue, window and capacity; an enrolment may name its session and
# the trainer records attendance on it. An absent trainee is not passed.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_competency import TRAINING, changed_fields, guard_first, require_group


class FixTrainingSession(models.Model):
    _name = "fix.training.session"
    _description = "Training Session"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    course_id = fields.Many2one(
        "fix.training.course", required=True, ondelete="restrict", tracking=True
    )
    delivery_mode = fields.Selection(
        [
            ("classroom", "Classroom"),
            ("practical", "Practical / Bench"),
            ("online", "Online"),
            ("external", "External Provider"),
        ],
        required=True,
        default="classroom",
        tracking=True,
    )
    trainer_id = fields.Many2one("hr.employee", string="Trainer", tracking=True)
    # FR-LMS-029: training delivered by an outside provider
    vendor_id = fields.Many2one("res.partner", string="External Provider")
    external_trainer = fields.Char(string="External Trainer")
    venue = fields.Char(tracking=True)
    date_start = fields.Datetime(string="Starts", required=True, tracking=True)
    date_end = fields.Datetime(string="Ends", required=True, tracking=True)
    capacity = fields.Integer(help="Seats in the session (0 = no limit).")
    enrollment_ids = fields.One2many("fix.training.enrollment", "session_id", string="Enrolments")
    seats_taken = fields.Integer(compute="_compute_seats", string="Seats Taken")
    attended_count = fields.Integer(compute="_compute_seats", string="Attended")
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("scheduled", "Scheduled"),
            ("done", "Held"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="planned",
        tracking=True,
    )
    notes = fields.Text()
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _capacity_positive = models.Constraint(
        "CHECK (capacity >= 0)", "A session's capacity is zero (no limit) or more."
    )

    # a held or cancelled session is the training record: who, where, when
    _FROZEN_WHEN_HELD = frozenset(
        {
            "course_id",
            "delivery_mode",
            "trainer_id",
            "vendor_id",
            "external_trainer",
            "venue",
            "date_start",
            "date_end",
            "capacity",
            "company_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        # the session moves through its actions, never by typing the state
        return super()._fix_guarded_fields() | {"state"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state in ("done", "cancelled") for rec in self):
            locked = locked | self._FROZEN_WHEN_HELD
        return locked

    @api.depends("enrollment_ids", "enrollment_ids.attendance", "enrollment_ids.state")
    def _compute_seats(self):
        for rec in self:
            # a withdrawn trainee gives the seat back (FR-LMS-021)
            rec.seats_taken = len(rec._fix_seated())
            rec.attended_count = len(
                rec.enrollment_ids.filtered(lambda e: e.attendance == "attended")
            )

    def _fix_seated(self):
        self.ensure_one()
        return self.enrollment_ids.filtered(lambda e: e.state != "withdrawn")

    @api.constrains("date_start", "date_end")
    def _check_window(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end <= rec.date_start:
                raise ValidationError("A session ends after it starts.")

    @api.constrains("trainer_id", "vendor_id", "external_trainer", "delivery_mode")
    def _check_trainer(self):
        for rec in self:
            if rec.delivery_mode == "external" and not (rec.vendor_id or rec.external_trainer):
                raise ValidationError(
                    "An external session names its provider or trainer (FR-LMS-029)."
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, TRAINING, "Scheduling a training session")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.training.session") or "TRS/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.state in ("done", "cancelled")),
                vals,
                self._FROZEN_WHEN_HELD,
            )
            if frozen:
                raise UserError(
                    "A held or cancelled session is final (%s)." % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def action_schedule(self):
        """Planned -> Scheduled: published so the trainees' availability can be
        taken out of the roster (FR-LMS-022, BRU-LMS-08)."""
        require_group(self.env, TRAINING, "Scheduling a training session")
        for rec in self:
            if rec.state != "planned":
                raise UserError("Only a planned session is scheduled (%s)." % rec.name)
            if rec.delivery_mode != "external" and not rec.trainer_id:
                raise UserError("Name the trainer before scheduling %s." % rec.name)
            if rec.delivery_mode in ("classroom", "practical") and not rec.venue:
                raise UserError("Name the venue before scheduling %s." % rec.name)
            rec._guarded().write({"state": "scheduled"})
            publish(
                self.env,
                "training.session.scheduled",
                "fix.training.session",
                rec.id,
                {
                    "course": rec.course_id.code,
                    "start": fields.Datetime.to_string(rec.date_start),
                    "end": fields.Datetime.to_string(rec.date_end),
                    "employee_ids": rec._fix_seated().mapped("employee_id").ids,
                },
            )
        return True

    def action_mark_held(self):
        """Scheduled -> Held, once the trainer has recorded every attendance."""
        require_group(self.env, TRAINING, "Closing a training session")
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("Only a scheduled session is marked held (%s)." % rec.name)
            open_rows = rec._fix_seated().filtered(lambda e: e.attendance == "pending")
            if open_rows:
                raise UserError(
                    "Record the attendance of %s before closing %s (FR-LMS-023)."
                    % (", ".join(open_rows.mapped("employee_id.name")), rec.name)
                )
            rec._guarded().write({"state": "done"})
        return True

    def action_cancel(self):
        require_group(self.env, TRAINING, "Cancelling a training session")
        for rec in self:
            if rec.state in ("done", "cancelled"):
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if rec.enrollment_ids.filtered(lambda e: e.attendance == "attended"):
                raise UserError("%s has recorded attendance; it is not cancelled." % rec.name)
            rec._guarded().write({"state": "cancelled"})
        return True


class FixTrainingEnrollmentSession(models.Model):
    _inherit = "fix.training.enrollment"

    session_id = fields.Many2one(
        "fix.training.session",
        string="Session",
        ondelete="restrict",
        index=True,
        domain="[('course_id', '=', course_id), ('state', 'in', ('planned', 'scheduled'))]",
    )
    attendance = fields.Selection(
        [("pending", "Not Recorded"), ("attended", "Attended"), ("absent", "Absent")],
        required=True,
        default="pending",
        tracking=True,
    )
    attendance_by_id = fields.Many2one("res.users", string="Attendance Recorded By", readonly=True)

    def _fix_guarded_fields(self) -> set:
        # FR-LMS-023: the trainer records attendance through the actions
        return super()._fix_guarded_fields() | {"attendance", "attendance_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "enrolled" or rec.attendance != "pending" for rec in self):
            locked = locked | {"session_id"}
        return locked

    @api.constrains("session_id", "course_id")
    def _check_session(self):
        for rec in self:
            sess = rec.session_id
            if not sess:
                continue
            if sess.course_id != rec.course_id:
                raise ValidationError(
                    "Session %s delivers %s, not %s."
                    % (sess.name, sess.course_id.code, rec.course_id.code)
                )
            if sess.capacity and len(sess._fix_seated()) > sess.capacity:
                raise ValidationError(
                    "Session %s is full (%d seats, FR-LMS-021)." % (sess.name, sess.capacity)
                )

    @api.model_create_multi
    def create(self, vals_list):
        Session = self.env["fix.training.session"]
        for vals in vals_list:
            if vals.get("session_id"):
                sess = Session.browse(vals["session_id"])
                if sess.state not in ("planned", "scheduled"):
                    raise UserError(
                        "Session %s is %s; it takes no enrolment." % (sess.name, sess.state)
                    )
                # a session delivers one course: the enrolment follows it
                vals.setdefault("course_id", sess.course_id.id)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("session_id"):
            sess = self.env["fix.training.session"].browse(vals["session_id"])
            if sess.state not in ("planned", "scheduled"):
                raise UserError(
                    "Session %s is %s; it takes no enrolment." % (sess.name, sess.state)
                )
        return super().write(vals)

    def _fix_record_attendance(self, value):
        require_group(self.env, TRAINING, "Recording attendance")
        for rec in self:
            if not rec.session_id:
                raise UserError("%s is not on a session." % rec.display_name)
            if rec.session_id.state != "scheduled":
                raise UserError(
                    "Attendance is recorded on a scheduled session (%s is %s)."
                    % (rec.session_id.name, rec.session_id.state)
                )
            if rec.state != "enrolled":
                raise UserError("%s is already decided." % rec.display_name)
            if not self.env.su and rec.employee_id.sudo().user_id == self.env.user:
                raise UserError("You cannot record your own attendance.")
            rec._guarded().write({"attendance": value, "attendance_by_id": self.env.user.id})
        return True

    def action_mark_attended(self):
        return self._fix_record_attendance("attended")

    def action_mark_absent(self):
        return self._fix_record_attendance("absent")

    def action_pass(self):
        for rec in self:
            if rec.session_id and rec.attendance != "attended":
                raise UserError(
                    "%s has no attendance recorded on %s; an absent trainee is not passed."
                    % (rec.employee_id.name, rec.session_id.name)
                )
        return super().action_pass()
