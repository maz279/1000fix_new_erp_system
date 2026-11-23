# fix_performance_ops — M57: goals, review cycles, PIPs, recognition and
# succession plans. Scorecards, incentive runs/lines and compensation bands
# live in fix_performance.py.
#
# A09 workflow audit (M57-F4/F7/F8/F11/F13): one HR Manager ran a review on
# himself (reviewer = employee, 5/5, calibrated, closed), the employee could
# not record a self-assessment and the line manager could not rate a report;
# a closed review reopened and a rating of 42 was accepted on a 1-5 scale;
# goals were never agreed and weighed 270 %; a draft PIP closed 'exit'; a
# BDT 1,000,000 self-awarded recognition prize needed no approval.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_performance import APPROVER, CALIBRATOR, HR_MANAGER, changed_fields, guard_first


def _is_hr(env):
    return env.su or env.user.has_group(HR_MANAGER)


def _require_hr(env, what):
    if not _is_hr(env):
        raise AccessError("%s is an HR Manager decision." % what)


HR_OFFICER = "cd_hr_core.group_hr_officer"


def _require_hr_or_officer(env, what):
    """M57-F14: the HR Officer (spec R31 - create, read, update, cycle
    administration) runs the set-up: the cycle, its reviews, goals, PIPs and
    feedback. The decisions (closing a cycle or a PIP, awarding, approving)
    stay on the groups that decide."""
    if not (_is_hr(env) or env.su or env.user.has_group(HR_OFFICER)):
        raise AccessError("%s is an HR Manager's or an HR Officer's task." % what)


def _user_of(employee):
    return employee.sudo().user_id


class FixPerfGoal(models.Model):
    _name = "fix.performance.goal"
    _description = "Performance Goal"
    _inherit = ["fix.guarded.mixin"]
    _order = "period desc, employee_id"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    parent_goal_id = fields.Many2one(
        "fix.performance.goal", string="Cascaded From", ondelete="set null"
    )
    period = fields.Char(required=True, help="YYYY-MM")
    weight = fields.Float(string="Weight %", default=20.0)
    target_value = fields.Float(string="Target")
    actual_value = fields.Float(string="Actual")
    unit = fields.Char(string="Unit")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("achieved", "Achieved"), ("missed", "Missed")],
        required=True,
        default="draft",
    )
    employee_agreed_by_id = fields.Many2one("res.users", string="Agreed by Employee", readonly=True)
    employee_agreed_at = fields.Datetime(string="Employee Agreed At", readonly=True)
    manager_agreed_by_id = fields.Many2one("res.users", string="Agreed by Manager", readonly=True)
    manager_agreed_at = fields.Datetime(string="Manager Agreed At", readonly=True)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)
    closed_at = fields.Datetime(string="Closed At", readonly=True)

    _weight_range = models.Constraint(
        "CHECK (weight >= 0 AND weight <= 100)", "Goal weight is a 0-100 percentage"
    )

    _FROZEN_WHEN_ACTIVE = frozenset(
        {"name", "employee_id", "period", "weight", "target_value", "unit", "company_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "employee_agreed_by_id",
            "employee_agreed_at",
            "manager_agreed_by_id",
            "manager_agreed_at",
            "closed_by_id",
            "closed_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._FROZEN_WHEN_ACTIVE
        if self and any(rec.state in ("achieved", "missed") for rec in self):
            locked = locked | {"actual_value"}
        return locked

    def _fix_period_weight(self):
        self.ensure_one()
        goals = self.sudo().search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("period", "=", self.period),
                ("company_id", "=", self.company_id.id),
            ]
        )
        return round(sum(goals.mapped("weight")), 4)

    @api.constrains("weight", "employee_id", "period")
    def _check_weights_total(self):
        for rec in self:
            total = rec._fix_period_weight()
            if total > 100.0001:
                raise ValidationError(
                    "The goals of %s for %s weigh %.1f%%; they must total 100%% at most."
                    % (rec.employee_id.name, rec.period, total)
                )

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.state != "draft"), vals, self._FROZEN_WHEN_ACTIVE
            ) | changed_fields(
                self.filtered(lambda r: r.state in ("achieved", "missed")), vals, {"actual_value"}
            )
            if frozen:
                raise UserError(
                    "An agreed goal keeps its terms, and a closed goal its result (%s)."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def action_agree(self):
        """FR-PIC-003: the employee and the line manager each record agreement."""
        user = self.env.user
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft goal is agreed.")
            vals = {}
            if _user_of(rec.employee_id) == user:
                vals.update(employee_agreed_by_id=user.id, employee_agreed_at=fields.Datetime.now())
            manager = rec.employee_id.sudo().parent_id
            if (manager and _user_of(manager) == user) or (
                not manager and _is_hr(self.env) and _user_of(rec.employee_id) != user
            ):
                vals.update(manager_agreed_by_id=user.id, manager_agreed_at=fields.Datetime.now())
            if not vals:
                raise AccessError(
                    "Only %s or their line manager can agree this goal." % rec.employee_id.name
                )
            rec.sudo()._guarded().write(vals)
        return True

    def action_activate(self):
        for rec in self:
            manager = rec.employee_id.sudo().parent_id
            if not (_is_hr(self.env) or (manager and _user_of(manager) == self.env.user)):
                raise AccessError("A goal is activated by HR or the employee's line manager.")
            if rec.state != "draft":
                raise UserError("Only a draft goal is activated.")
            if not (rec.employee_agreed_by_id and rec.manager_agreed_by_id):
                raise UserError(
                    "FR-PIC-003: %s and their line manager must both agree the goal "
                    "before it is activated." % rec.employee_id.name
                )
            total = rec._fix_period_weight()
            if abs(total - 100.0) > 0.0001:
                raise UserError(
                    "The goals of %s for %s weigh %.1f%%; agree goals totalling 100%% "
                    "before activating them." % (rec.employee_id.name, rec.period, total)
                )
            rec.sudo()._guarded().write({"state": "active"})
        return True

    def action_close(self):
        for rec in self:
            manager = rec.employee_id.sudo().parent_id
            if not (_is_hr(self.env) or (manager and _user_of(manager) == self.env.user)):
                raise AccessError("A goal is closed by HR or the employee's line manager.")
            if rec.state != "active":
                raise UserError("Only an active goal is closed; a closed goal is final.")
            if _user_of(rec.employee_id) == self.env.user and not self.env.su:
                raise UserError("You cannot close your own goal.")
            reached = rec.actual_value >= rec.target_value
            rec.sudo()._guarded().write(
                {
                    "state": "achieved" if reached else "missed",
                    "closed_by_id": self.env.user.id,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True


class FixPerfReview(models.Model):
    _name = "fix.performance.review"
    _description = "Performance Review Cycle"
    _inherit = ["mail.thread", "fix.people.approval.mixin"]
    _order = "period desc, employee_id"

    _approval_domain = "hr_review"
    _approval_apply_method = "action_calibrate"
    _approval_group = CALIBRATOR

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    reviewer_id = fields.Many2one(
        "hr.employee", string="Reviewer", help="The employee's line manager (FR-PIC-019)."
    )
    period = fields.Char(required=True, help="YYYY-MM or YYYY-Qn")
    self_rating = fields.Float(string="Self Rating (1-5)")
    manager_rating = fields.Float(string="Manager Rating (1-5)")
    calibrated_rating = fields.Float(string="Calibrated Rating (1-5)", readonly=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("self_review", "Self Review"),
            ("manager_review", "Manager Review"),
            ("calibrated", "Calibrated"),
            ("closed", "Closed"),
        ],
        required=True,
        default="draft",
    )
    self_submitted_at = fields.Datetime(string="Self-Assessment Submitted", readonly=True)
    manager_rated_by_id = fields.Many2one("res.users", string="Rated By", readonly=True)
    manager_rated_at = fields.Datetime(string="Rated At", readonly=True)
    calibrated_by_id = fields.Many2one("res.users", string="Calibrated By", readonly=True)
    calibrated_at = fields.Datetime(string="Calibrated At", readonly=True)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)
    closed_at = fields.Datetime(string="Closed At", readonly=True)

    _ratings_on_scale = models.Constraint(
        "CHECK ((self_rating = 0 OR self_rating BETWEEN 1 AND 5) "
        "AND (manager_rating = 0 OR manager_rating BETWEEN 1 AND 5) "
        "AND (calibrated_rating = 0 OR calibrated_rating BETWEEN 1 AND 5))",
        "Ratings are on the 1-5 scale.",
    )

    _HR_FIELDS = frozenset({"name", "employee_id", "reviewer_id", "period", "company_id"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "calibrated_rating",
            "self_submitted_at",
            "manager_rated_by_id",
            "manager_rated_at",
            "calibrated_by_id",
            "calibrated_at",
            "closed_by_id",
            "closed_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._HR_FIELDS
        if self and any(
            rec.state in ("calibrated", "closed") or rec.approval_state == "pending" for rec in self
        ):
            locked = locked | {"self_rating", "manager_rating"}
        return locked

    # ---- approval declarations ---------------------------------------------
    def _approval_preparers(self):
        return self.mapped("manager_rated_by_id") | self.mapped("reviewer_id.user_id")

    def _approval_on_rejected(self, comment):
        # Calibration sends the rating back to the manager.
        self.message_post(body="Calibration returned the rating to the manager: %s" % comment)

    # ---- validation -----------------------------------------------------------
    @api.constrains("self_rating", "manager_rating", "calibrated_rating")
    def _check_scale(self):
        for rec in self:
            for name in ("self_rating", "manager_rating", "calibrated_rating"):
                value = rec[name] or 0.0
                if value and not 1 <= value <= 5:
                    raise ValidationError(
                        "%s is on the 1-5 scale (got %s)." % (rec._fields[name].string, value)
                    )

    @api.constrains("employee_id", "reviewer_id")
    def _check_reviewer(self):
        for rec in self:
            if not rec.reviewer_id:
                continue
            if rec.reviewer_id == rec.employee_id:
                raise ValidationError("An employee cannot review themself.")
            manager = rec.employee_id.sudo().parent_id
            if manager and rec.reviewer_id != manager:
                raise ValidationError(
                    "The reviewer of %s is their line manager, %s."
                    % (rec.employee_id.name, manager.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.performance.review") or "PRV/New"
                )
            if not vals.get("reviewer_id") and vals.get("employee_id"):
                manager = self.env["hr.employee"].sudo().browse(vals["employee_id"]).parent_id
                if manager:
                    vals["reviewer_id"] = manager.id
        if not _is_hr(self.env):
            raise AccessError("A review cycle is opened by HR.")
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            self._fix_check_review_write(vals)
        return super().write(vals)

    def _fix_check_review_write(self, vals):
        """Who may change what, by state: the employee their self rating, the
        line manager their rating, HR the cycle's set-up, nobody a closed one."""
        user = self.env.user
        for rec in self:
            changed = changed_fields(rec, vals, set(vals))
            if not changed:
                continue
            if rec.state == "closed":
                raise UserError("%s is closed; a closed review is final." % rec.name)
            open_for_rating = rec.state in ("draft", "self_review", "manager_review") and (
                rec.approval_state != "pending"
            )
            for name in changed:
                if name == "self_rating":
                    if _user_of(rec.employee_id) != user:
                        raise AccessError(
                            "Only %s records their self-assessment." % rec.employee_id.name
                        )
                    if rec.state not in ("draft", "self_review"):
                        raise UserError("The self-assessment of %s is submitted." % rec.name)
                elif name == "manager_rating":
                    if not rec.reviewer_id or _user_of(rec.reviewer_id) != user:
                        raise AccessError(
                            "Only the reviewer of %s (their line manager) rates it." % rec.name
                        )
                    if not open_for_rating:
                        raise UserError(
                            "%s is in calibration or calibrated; the rating is fixed." % rec.name
                        )
                else:
                    if not _is_hr(self.env):
                        raise AccessError("Only HR changes the set-up of a review cycle.")
                    if rec.state != "draft":
                        raise UserError(
                            "%s has started; its employee, reviewer and period are fixed."
                            % rec.name
                        )

    # ---- ratings (no write access needed: the action checks who rates) ------
    def _fix_rate(self, field, rating):
        try:
            rating = float(rating)
        except (TypeError, ValueError):
            raise UserError("A rating is a number from 1 to 5.") from None
        vals = {field: rating}
        self.check_access("read")  # record rules: own and direct reports only
        for rec in self:
            rec._fix_check_review_write(vals)
            rec.sudo().write(vals)
        return True

    def action_record_self_rating(self, rating=None):
        """FR-PIC-018: the employee records their self-assessment."""
        return self._fix_rate("self_rating", rating)

    def action_record_manager_rating(self, rating=None):
        """FR-PIC-019: the line manager rates their report."""
        return self._fix_rate("manager_rating", rating)

    # ---- transitions ----------------------------------------------------------
    def action_start(self):
        """HR opens the self-assessment."""
        _require_hr_or_officer(self.env, "Starting a review cycle")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft review is started.")
            if not rec.reviewer_id:
                raise UserError("Name the reviewer (the line manager) of %s first." % rec.name)
            rec._guarded().write({"state": "self_review"})
        return True

    def action_submit_self_assessment(self):
        """The employee submits their self rating (HR moves it on for an
        employee who has no user account)."""
        for rec in self:
            if rec.state != "self_review":
                raise UserError("%s is not awaiting a self-assessment." % rec.name)
            emp_user = _user_of(rec.employee_id)
            if emp_user:
                if emp_user != self.env.user and not self.env.su:
                    raise AccessError(
                        "Only %s submits their self-assessment." % rec.employee_id.name
                    )
                if not rec.self_rating:
                    raise UserError("Record your self rating (1-5) first.")
            elif not _is_hr(self.env):
                raise AccessError("HR moves on a review whose employee has no user account.")
            rec.sudo()._guarded().write(
                {"state": "manager_review", "self_submitted_at": fields.Datetime.now()}
            )
        return True

    def _fix_assert_reviewer(self, what):
        """The line manager named as reviewer, on a review their record rules
        let them read (own and direct reports), and nobody else."""
        self.check_access("read")
        for rec in self:
            if self.env.su:
                continue
            if not rec.reviewer_id or _user_of(rec.reviewer_id) != self.env.user:
                raise AccessError(
                    "Only the reviewer of %s (their line manager) may %s it." % (rec.name, what)
                )

    def action_manager_review(self):
        """The line manager submits their rating and requests calibration."""
        return self.action_request_calibration()

    def action_request_calibration(self):
        """The line manager routes their rating to a calibrator who is neither
        the manager nor the employee (BRU-PIC-13).

        A line manager holds no write access to review records (RAP X-02: no
        A09 model is writable by base.group_user), so this method is the one
        narrow way in: it checks the caller is the reviewer of a review they
        may read, and only then lets the engine stamp the request on the
        record. The request is raised in the manager's name, so the manager
        is its requester and can never decide it."""
        self._fix_assert_reviewer("request calibration of")
        for rec in self:
            if rec.state != "manager_review":
                raise UserError("%s is not awaiting the manager's rating." % rec.name)
            if rec.approval_state == "pending":
                raise UserError("%s is already in calibration." % rec.name)
            if not rec.manager_rating:
                raise UserError("Record the manager rating first")
            rec.sudo()._guarded().write(
                {"manager_rated_by_id": self.env.user.id, "manager_rated_at": fields.Datetime.now()}
            )
        # env.uid stays the manager under sudo(): requested_by_id is the manager.
        return self.sudo().action_request_approval()

    def action_recall_calibration(self):
        """The manager who requested calibration withdraws it (to change the
        rating) while no calibrator has decided."""
        self._fix_assert_reviewer("recall the calibration of")
        for rec in self:
            req = rec.sudo().approval_request_id
            if rec.approval_state != "pending" or not req or req.state != "pending":
                raise UserError("%s has no pending calibration to recall." % rec.name)
            if not self.env.su and req.requested_by_id != self.env.user:
                raise AccessError("Only the manager who requested the calibration recalls it.")
        return self.sudo().action_recall_approval()

    def action_propose_compensation(
        self,
        proposal=None,
        proposed_basic=None,
        justification=None,
        proposal_type="merit",
        effective_date=None,
    ):
        """BRU-PIC-17: from a closed review, the line manager proposes a merit
        increase for the report. ``proposal`` is the workspace prompt's one
        string: '<proposed monthly basic> <justification>'."""
        self.ensure_one()
        self._fix_assert_reviewer("propose compensation from")
        if self.state != "closed":
            raise UserError("A merit proposal follows a closed (calibrated) review.")
        Proposal = self.env["fix.compensation.proposal"]
        if proposal not in (None, False, ""):
            proposed_basic, justification = Proposal._fix_parse_amount_note(proposal)
            if proposed_basic is None:
                raise UserError("Give the proposal as: <proposed monthly basic> <justification>.")
        rec = Proposal._fix_propose(
            self.employee_id,
            proposed_basic,
            justification,
            proposal_type=proposal_type,
            effective_date=effective_date,
            review=self,
        )
        return {"proposal_id": rec.id}

    def action_calibrate(self):
        """The approval engine runs this from the calibrator's inbox task
        (BRU-PIC-13): the rating is calibrated by someone other than the
        manager who gave it and the employee it is about."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "manager_review":
                raise UserError("Calibrate a review in manager review")
            rec._guarded().write(
                {
                    "state": "calibrated",
                    "calibrated_rating": rec.manager_rating,
                    "calibrated_by_id": rec._people_decider().id,
                    "calibrated_at": fields.Datetime.now(),
                }
            )
        return True

    def action_close(self):
        for rec in self:
            if not (_is_hr(self.env) or self.env.user.has_group(CALIBRATOR)):
                raise AccessError("A review is closed by HR or a calibrator.")
            if rec.state != "calibrated":
                raise UserError("Close a calibrated review")
            if _user_of(rec.employee_id) == self.env.user and not self.env.su:
                raise UserError("You cannot close your own review.")
            rec.sudo()._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.user.id,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True


class FixPerfPip(models.Model):
    _name = "fix.performance.pip"
    _description = "Performance Improvement Plan"
    _inherit = ["fix.guarded.mixin"]
    _order = "start_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    mentor_id = fields.Many2one("hr.employee", string="Mentor")
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True)
    reason = fields.Text()
    outcome = fields.Selection(
        [("improved", "Improved"), ("extended", "Extended"), ("exit", "Exit")],
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("closed", "Closed")],
        required=True,
        default="draft",
    )
    started_by_id = fields.Many2one("res.users", string="Started By", readonly=True)
    started_at = fields.Datetime(string="Started At", readonly=True)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)
    closed_at = fields.Datetime(string="Closed At", readonly=True)

    _dates_ordered = models.Constraint(
        "CHECK (end_date >= start_date)", "PIP end cannot precede its start"
    )

    _FROZEN_WHEN_ACTIVE = frozenset({"employee_id", "start_date", "reason", "company_id"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "started_by_id",
            "started_at",
            "closed_by_id",
            "closed_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._FROZEN_WHEN_ACTIVE
        if self and any(rec.state == "closed" for rec in self):
            locked = locked | set(self._fields) - {"id"}
        return locked

    @api.constrains("employee_id", "mentor_id")
    def _check_mentor(self):
        for rec in self:
            if rec.mentor_id and rec.mentor_id == rec.employee_id:
                raise ValidationError("An employee cannot mentor their own PIP.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.performance.pip") or "PIP/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            closed = changed_fields(self.filtered(lambda r: r.state == "closed"), vals, set(vals))
            frozen = changed_fields(
                self.filtered(lambda r: r.state == "active"), vals, self._FROZEN_WHEN_ACTIVE
            )
            if closed or frozen:
                raise UserError(
                    "A PIP keeps its terms once started, and is final once closed (%s)."
                    % ", ".join(sorted(closed | frozen))
                )
        return super().write(vals)

    def action_start(self):
        _require_hr_or_officer(self.env, "Starting a PIP")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft PIP is started; a closed PIP is final.")
            if not (rec.reason or "").strip():
                raise UserError("State the performance gaps and milestones before starting.")
            if _user_of(rec.employee_id) == self.env.user and not self.env.su:
                raise UserError("You cannot start your own PIP.")
            rec._guarded().write(
                {
                    "state": "active",
                    "started_by_id": self.env.user.id,
                    "started_at": fields.Datetime.now(),
                }
            )
        return True

    def action_close(self):
        _require_hr(self.env, "Closing a PIP")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "active":
                raise UserError(
                    "Only an active PIP is closed: BRU-PIC-15 relies on a plan that ran."
                )
            if not rec.outcome:
                raise UserError("Record the PIP outcome before closing")
            if rec.outcome == "exit" and rec.end_date > today:
                raise UserError(
                    "An 'exit' outcome is recorded when the plan has run to its end date (%s)."
                    % rec.end_date
                )
            if _user_of(rec.employee_id) == self.env.user and not self.env.su:
                raise UserError("You cannot close your own PIP.")
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.user.id,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True


class FixPerfRecognition(models.Model):
    _name = "fix.performance.recognition"
    _description = "Recognition Award"
    _inherit = ["mail.thread", "fix.people.approval.mixin"]
    _order = "awarded_on desc, id desc"

    _approval_domain = "hr_incentive"
    _approval_apply_method = "action_approve"
    _approval_group = APPROVER

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    award_type = fields.Selection(
        [
            ("spot", "Spot Award"),
            ("monthly", "Employee of the Month"),
            ("quarterly", "Quarterly Excellence"),
            ("values", "Values Champion"),
        ],
        required=True,
        default="spot",
    )
    awarded_on = fields.Date(required=True, default=fields.Date.context_today)
    citation = fields.Char()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    prize_amount = fields.Monetary(currency_field="currency_id", string="Prize")
    state = fields.Selection(
        [("draft", "Draft"), ("awarded", "Awarded"), ("cancelled", "Cancelled")],
        required=True,
        default="draft",
        tracking=True,
    )
    awarded_by_id = fields.Many2one("res.users", string="Awarded By", readonly=True)
    awarded_at = fields.Datetime(string="Awarded At", readonly=True)
    approved_prize = fields.Monetary(
        string="Approved Prize", currency_field="currency_id", readonly=True
    )

    _prize_not_negative = models.Constraint(
        "CHECK (prize_amount IS NULL OR prize_amount >= 0)", "A prize cannot be negative."
    )

    _FROZEN_WHEN_AWARDED = frozenset(
        {"employee_id", "award_type", "awarded_on", "prize_amount", "currency_id", "company_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "awarded_by_id",
            "awarded_at",
            "approved_prize",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" or rec.approval_state == "pending" for rec in self):
            locked = locked | self._FROZEN_WHEN_AWARDED
        return locked

    def _approval_amount(self) -> float:
        return float(self.prize_amount or 0.0)

    def _approval_needed(self) -> bool:
        return self.state == "draft" and (self.prize_amount or 0.0) > 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.performance.recognition")
                    or "RECG/New"
                )
        records = super().create(vals_list)
        # M57-39: an HR Manager awarded himself BDT 1,000,000.
        records._fix_assert_not_self()
        return records

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.state != "draft"), vals, self._FROZEN_WHEN_AWARDED
            )
            if frozen:
                raise UserError(
                    "An awarded recognition keeps what was awarded (%s)."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def _fix_assert_not_self(self):
        for rec in self:
            if not self.env.su and _user_of(rec.employee_id) == self.env.user:
                raise UserError("You cannot award yourself.")

    def action_award(self):
        """A non-monetary award is given by HR; a prize is routed for approval."""
        _require_hr(self.env, "Awarding a recognition")
        self._fix_assert_not_self()
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already awarded or cancelled." % rec.name)
            if (rec.prize_amount or 0.0) > 0:
                raise UserError(
                    "A recognition with a prize of %.2f is a payment: use Request Approval; "
                    "the Incentive Approver decides it." % rec.prize_amount
                )
            rec._guarded().write(
                {
                    "state": "awarded",
                    "awarded_by_id": self.env.user.id,
                    "awarded_at": fields.Datetime.now(),
                }
            )
        return True

    def action_request_approval(self, justification=None):
        _require_hr(self.env, "Requesting a recognition prize")
        self._fix_assert_not_self()
        for rec in self:
            if rec.state != "draft" or (rec.prize_amount or 0.0) <= 0:
                raise UserError("Only a draft recognition with a prize needs approval.")
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """Run by the approval engine from the approver's inbox task."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not awaiting a decision." % rec.name)
            rec._guarded().write(
                {
                    "state": "awarded",
                    "awarded_by_id": rec._people_decider().id,
                    "awarded_at": fields.Datetime.now(),
                    "approved_prize": rec.prize_amount,
                }
            )
            # The prize is salary income: payroll pays and withholds it (M56).
            publish(
                self.env,
                "recognition.awarded",
                "fix.performance.recognition",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "amount": rec.prize_amount,
                    "recognition_id": rec.id,
                    "reason": rec.citation or rec.award_type,
                },
            )
        return True

    def action_cancel(self):
        _require_hr(self.env, "Cancelling a recognition")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft recognition is cancelled.")
            if rec.approval_state == "pending":
                rec._approval_void("the recognition was cancelled")
            rec._guarded().write({"state": "cancelled"})
        return True


class FixSuccessionPlan(models.Model):
    _name = "fix.succession.plan"
    _description = "Succession Plan"
    _order = "position_name, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    position_name = fields.Char(string="Key Position", required=True)
    incumbent_id = fields.Many2one("hr.employee", string="Incumbent")
    successor_id = fields.Many2one("hr.employee", string="Ready Successor")
    readiness = fields.Selection(
        [("ready_now", "Ready Now"), ("1_2_years", "1-2 Years"), ("2_3_years", "2-3 Years")],
        required=True,
        default="1_2_years",
    )
    risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    notes = fields.Char()

    @api.constrains("incumbent_id", "successor_id")
    def _check_successor(self):
        for rec in self:
            if rec.successor_id and rec.successor_id == rec.incumbent_id:
                raise ValidationError("The incumbent cannot be their own successor.")


class ResUsersPerformance(models.Model):
    _inherit = "res.users"

    # The payroll roles read the incentive MONEY records, not the ratings.
    PAYROLL_READERS = (
        "cd_payroll_bd.group_payroll_officer",
        "cd_payroll_bd.group_payroll_manager",
    )

    def fix_reads_all_performance(self):
        """M57-F15: HR and the M57 roles that decide performance records (an
        approver or calibrator reads what it decides) read every scorecard,
        goal, review, PIP and feedback row. Payroll's groups are deliberately
        NOT here - ratings and "who said what" are S2 (spec §13, R41); payroll
        reads the money records through fix_reads_all_payroll_money."""
        self.ensure_one()
        for xmlid in (
            "hr.group_hr_user",
            "cd_hr_core.group_hr_officer",
            "cd_performance.group_performance_officer",
            APPROVER,
            CALIBRATOR,
        ):
            group = self.env.ref(xmlid, raise_if_not_found=False)
            if group and group in self.sudo().all_group_ids:
                return True
        return False

    def fix_reads_all_payroll_money(self):
        """The incentive money records (lines, adjustments, clawbacks, disputes,
        recognition awards): payroll reads every one, and so do the performance
        readers."""
        self.ensure_one()
        if self.fix_reads_all_performance():
            return True
        for xmlid in self.PAYROLL_READERS:
            group = self.env.ref(xmlid, raise_if_not_found=False)
            if group and group in self.sudo().all_group_ids:
                return True
        return False
