# fix_competency_capture2 - M22 capture audit, second pass (2026-11-19).
#
# The first pass (13 Nov) gave every M22 sub-module page a "+ New". Read
# against the spec (FR-LMS-001..040, lifecycle 8.2, entities 10.1), several
# decisions a person makes on those pages still had nowhere to be recorded:
#
# * page 1 Competency Framework: a learning path held ONE minimum level for
#   all its competencies and named its role as free text, so the role
#   requirement (FR-LMS-002: competency + minimum level + mandatory +
#   effective date, per role / position) could not be expressed, and the gap
#   analysis (FR-LMS-005) had nothing to compare against;
# * pages 2 and 4: no training need existed (FR-LMS-031, BRU-LMS-13, the
#   first step of lifecycle 8.2), and no training plan (FR-LMS-032);
# * page 4: no participant feedback (FR-LMS-036); an enrolment could never be
#   withdrawn or substituted (FR-LMS-021), so a wrong seat stayed committed to
#   the budget for good;
# * page 5 "OJT & Mentoring": no mentoring record at all (FR-LMS-028);
# * page 6 Evidence & Analytics: no effectiveness evaluation (FR-LMS-035,
#   BRU-LMS-15, AUT-LMS-12) - the "Training Effectiveness" report counted
#   pass rates, not the operational measure the training targeted.
#
# No new domain events: they would need contract registration; outcomes go to
# the chatter and to-dos, as in the M07/M21 second passes.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_competency import TRAINING, changed_fields, guard_first, require_group
from .fix_training_budget import BUDGET_APPROVER

LEVELS = [
    ("l1", "L1 - Aware"),
    ("l2", "L2 - Assisted"),
    ("l3", "L3 - Independent"),
    ("l4", "L4 - Expert / Trainer"),
]
RANK = {"l1": 1, "l2": 2, "l3": 3, "l4": 4}
RATINGS = [
    ("1", "1 - Poor"),
    ("2", "2 - Fair"),
    ("3", "3 - Good"),
    ("4", "4 - Very good"),
    ("5", "5 - Excellent"),
]
NEED_SOURCES = [
    ("competency_gap", "Role competency gap (gap analysis)"),
    ("performance", "Performance gap (M57)"),
    ("quality", "Quality non-conformance (M23)"),
    ("safety", "Safety incident / near miss (M59)"),
    ("new_product", "New product line (M17)"),
    ("new_brand", "New brand / service scope (M08)"),
    ("role_change", "Hire or role change (M21)"),
    ("certification", "Certification expiry / lapse"),
    ("manager", "Manager / supervisor request"),
]
OPEN_NEED = ("identified", "planned", "enrolled")


def _reason(reason, what="Give the reason."):
    reason = (reason or "").strip()
    if not reason:
        raise UserError(what)
    return reason


def _own_employee_user(employee):
    return employee.sudo().user_id


# ---------------------------------------------------------------------------
# Page 1 - the role requirement (FR-LMS-002) and the gap analysis (FR-LMS-005)
# ---------------------------------------------------------------------------
class FixRoleCompetency(models.Model):
    _name = "fix.role.competency"
    _description = "Role Competency Requirement"
    _order = "path_id, mandatory desc, competency_id"

    path_id = fields.Many2one(
        "fix.learning.path", string="Role / Learning Path", required=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="path_id.company_id", store=True, index=True)
    competency_id = fields.Many2one("fix.competency", required=True, ondelete="restrict")
    min_level = fields.Selection(LEVELS, string="Minimum Level", required=True, default="l2")
    mandatory = fields.Boolean(default=True)
    effective_from = fields.Date(required=True, default=fields.Date.context_today)

    _one_per_path = models.Constraint(
        "UNIQUE (path_id, competency_id)", "A role names each competency once."
    )

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, TRAINING, "Setting a role competency requirement")
        return super().create(vals_list)

    def write(self, vals):
        require_group(self.env, TRAINING, "Changing a role competency requirement")
        return super().write(vals)

    def unlink(self):
        require_group(self.env, TRAINING, "Removing a role competency requirement")
        return super().unlink()


class FixLearningPathRole(models.Model):
    _inherit = "fix.learning.path"

    position_ids = fields.Many2many(
        "fix.org.position",
        "fix_learning_path_position_rel",
        "path_id",
        "position_id",
        string="Applies to Positions",
        help="The employees holding these positions are measured against the requirements.",
    )
    requirement_ids = fields.One2many(
        "fix.role.competency", "path_id", string="Competency Requirements"
    )
    requirement_count = fields.Integer(compute="_compute_requirement_count")

    @api.depends("requirement_ids")
    def _compute_requirement_count(self):
        for rec in self:
            rec.requirement_count = len(rec.requirement_ids)

    def _fix_held_levels(self, employees, competencies):
        """{(employee id, competency id): level} the evidence supports: the
        latest PASSED assessment by an independent assessor, and a granted
        certification in date counts as L3 (as the skill-gap heatmap does).
        Read in the caller's environment, so S2 (BRU-LMS-12) still holds."""
        held = {}
        if not employees or not competencies:
            return held
        rows = self.env["fix.competency.assessment"].search(
            [
                ("employee_id", "in", employees.ids),
                ("competency_id", "in", competencies.ids),
                ("passed", "=", True),
                ("assessor_id", "!=", False),
            ],
            order="assessed_on desc, id desc",
        )
        for row in rows:
            if row.assessor_id == row.employee_id:
                continue  # BRU-LMS-06: never self-declared
            held.setdefault((row.employee_id.id, row.competency_id.id), row.level)
        certs = self.env["fix.certification"].search(
            [
                ("employee_id", "in", employees.ids),
                ("competency_id", "in", competencies.ids),
                ("state", "=", "valid"),
                ("status", "!=", "expired"),
            ]
        )
        for cert in certs:
            key = (cert.employee_id.id, cert.competency_id.id)
            if RANK.get(held.get(key), 0) < RANK["l3"]:
                held[key] = "l3"
        return held

    def _fix_gap_rows(self):
        """FR-LMS-005: every employee in a path's positions, against every
        requirement in force; one row per requirement not met."""
        today = fields.Date.context_today(self)
        Need = self.env["fix.training.need"].sudo()
        rows = []
        for path in self.filtered("active"):
            reqs = path.requirement_ids.filtered(
                lambda r: not r.effective_from or r.effective_from <= today
            )
            if not reqs or not path.position_ids:
                continue
            employees = self.env["hr.employee"].search(
                [("position_id", "in", path.position_ids.ids)]
            )
            held = path._fix_held_levels(employees, reqs.mapped("competency_id"))
            for emp in employees:
                for req in reqs:
                    level = held.get((emp.id, req.competency_id.id))
                    if RANK.get(level, 0) >= RANK[req.min_level]:
                        continue
                    open_need = Need.search_count(
                        [
                            ("employee_id", "=", emp.id),
                            ("competency_id", "=", req.competency_id.id),
                            ("state", "in", OPEN_NEED),
                        ]
                    )
                    rows.append(
                        {
                            "path": path,
                            "requirement": req,
                            "employee": emp,
                            "held": level or False,
                            "gap": RANK[req.min_level] - RANK.get(level, 0),
                            "open_need": bool(open_need),
                        }
                    )
        return rows

    def action_raise_gap_needs(self):
        """FR-LMS-005 -> FR-LMS-031: a training need for every gap that has none."""
        require_group(self.env, TRAINING, "Raising training needs")
        Need = self.env["fix.training.need"]
        Course = self.env["fix.training.course"]
        created = Need
        for row in self._fix_gap_rows():
            if row["open_need"]:
                continue
            req, emp, path = row["requirement"], row["employee"], row["path"]
            course = path.course_ids.filtered(
                lambda c, comp=req.competency_id: c.competency_id == comp
            )[:1] or Course.search([("competency_id", "=", req.competency_id.id)], limit=1)
            created |= Need.create(
                {
                    "employee_id": emp.id,
                    "competency_id": req.competency_id.id,
                    "course_id": course.id or False,
                    "source": "competency_gap",
                    "source_ref": path.name,
                    "priority": "high" if req.mandatory else "medium",
                    "description": "%s holds %s in %s; the %s role requires %s."
                    % (
                        emp.name,
                        dict(LEVELS).get(row["held"], "no assessed level"),
                        req.competency_id.name,
                        path.target_role or path.name,
                        dict(LEVELS)[req.min_level],
                    ),
                    "company_id": path.company_id.id,
                }
            )
        return {"raised": len(created), "need_ids": created.ids}


# ---------------------------------------------------------------------------
# Pages 2 and 4 - the training need (FR-LMS-031) and the plan (FR-LMS-032)
# ---------------------------------------------------------------------------
class FixTrainingNeed(models.Model):
    _name = "fix.training.need"
    _description = "Training Need"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "raised_on desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True, tracking=True)
    competency_id = fields.Many2one("fix.competency", ondelete="restrict", tracking=True)
    course_id = fields.Many2one(
        "fix.training.course", string="Course to Close It", ondelete="restrict", tracking=True
    )
    source = fields.Selection(NEED_SOURCES, required=True, default="manager", tracking=True)
    source_ref = fields.Char(string="Source Reference", help="NC, incident, review or job no.")
    priority = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("mandatory", "Mandatory")],
        required=True,
        default="medium",
        tracking=True,
    )
    description = fields.Text(string="Need Statement", required=True)
    raised_on = fields.Date(required=True, default=fields.Date.context_today)
    due_date = fields.Date(string="Needed By")
    raised_by_id = fields.Many2one(
        "res.users", string="Raised By", readonly=True, default=lambda self: self.env.user
    )
    plan_id = fields.Many2one(
        "fix.training.plan", string="Training Plan", ondelete="set null", index=True
    )
    enrollment_id = fields.Many2one(
        "fix.training.enrollment", string="Enrolment", readonly=True, ondelete="set null"
    )
    state = fields.Selection(
        [
            ("identified", "Identified"),
            ("planned", "Planned"),
            ("enrolled", "Enrolled"),
            ("closed", "Closed (trained)"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="identified",
        tracking=True,
    )
    closed_on = fields.Date(readonly=True)
    cancel_reason = fields.Char(readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _FROZEN_WHEN_DONE = frozenset(
        {"employee_id", "competency_id", "course_id", "source", "priority", "company_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "enrollment_id",
            "closed_on",
            "cancel_reason",
            "raised_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state in ("enrolled", "closed", "cancelled") for rec in self):
            locked = locked | self._FROZEN_WHEN_DONE | {"plan_id"}
        return locked

    @api.constrains("competency_id", "course_id")
    def _check_subject(self):
        for rec in self:
            if not (rec.competency_id or rec.course_id):
                raise ValidationError("A training need names the competency or the course.")

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, TRAINING, "Raising a training need")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.training.need") or "TNR/New"
                )
            # AUT-LMS-07: a safety incident raises a MANDATORY need
            if vals.get("source") == "safety":
                vals["priority"] = "mandatory"
            if vals.get("course_id") and not vals.get("competency_id"):
                course = self.env["fix.training.course"].browse(vals["course_id"])
                vals["competency_id"] = course.competency_id.id or False
        recs = super().create(vals_list)
        for rec in recs.filtered("plan_id"):
            rec._fix_check_plan_open(rec.plan_id)
            rec._guarded().write({"state": "planned"})
        return recs

    def _fix_check_plan_open(self, plan):
        if plan and plan.state != "draft":
            raise UserError(
                "Plan %s is %s; needs join a plan while it is a draft." % (plan.name, plan.state)
            )

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            done = self.filtered(lambda r: r.state in ("enrolled", "closed", "cancelled"))
            frozen = changed_fields(done, vals, self._FROZEN_WHEN_DONE | {"plan_id"})
            if frozen:
                raise UserError(
                    "An enrolled, closed or cancelled need is final (%s)."
                    % ", ".join(sorted(frozen))
                )
            if "plan_id" in vals:
                Plan = self.env["fix.training.plan"]
                for rec in self:
                    rec._fix_check_plan_open(rec.plan_id)  # leaving a plan
                self._fix_check_plan_open(Plan.browse(vals["plan_id"] or []))  # joining one
            if vals.get("source") == "safety" or (
                "priority" in vals
                and any((vals.get("source") or rec.source) == "safety" for rec in self)
            ):
                vals = dict(vals, priority="mandatory")
        res = super().write(vals)
        if "plan_id" in vals and not self._fix_guard_open():
            for rec in self:
                state = "planned" if rec.plan_id else "identified"
                if rec.state in ("identified", "planned") and rec.state != state:
                    rec._guarded().write({"state": state})
        return res

    def action_enrol(self):
        """Lifecycle 8.2 PLANNED -> ENROLLED: the need is closed by training."""
        require_group(self.env, TRAINING, "Enrolling against a training need")
        Enrollment = self.env["fix.training.enrollment"]
        for rec in self:
            if rec.state not in ("identified", "planned"):
                raise UserError("%s is %s; it is not enrolled." % (rec.name, rec.state))
            if rec.plan_id and rec.plan_id.state != "approved":
                raise UserError(
                    "%s sits in plan %s, which is not approved yet (the budget check of "
                    "lifecycle 8.2)." % (rec.name, rec.plan_id.name)
                )
            course = rec.course_id or self.env["fix.training.course"].search(
                [("competency_id", "=", rec.competency_id.id)], limit=1
            )
            if not course:
                raise UserError("Name the course that closes %s." % rec.name)
            enrolment = Enrollment.create(
                {
                    "course_id": course.id,
                    "employee_id": rec.employee_id.id,
                    "company_id": rec.company_id.id,
                }
            )
            rec._guarded().write(
                {"state": "enrolled", "enrollment_id": enrolment.id, "course_id": course.id}
            )
            rec.message_post(body="Enrolled on %s (%s)." % (course.name, enrolment.display_name))
        return True

    def action_cancel(self, reason=None):
        require_group(self.env, TRAINING, "Cancelling a training need")
        reason = _reason(reason, "Give the reason the need is cancelled.")
        for rec in self:
            if rec.state in ("closed", "cancelled"):
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if rec.state == "enrolled" and rec.enrollment_id.state == "enrolled":
                raise UserError(
                    "%s has an open enrolment (%s); withdraw it first."
                    % (rec.name, rec.enrollment_id.display_name)
                )
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason})
        return True

    def _fix_follow_enrolment(self, enrolment):
        """AUT-LMS-10: a passed enrolment closes its need; a failed or
        withdrawn one sends it back to be planned again."""
        for rec in self.sudo().search(
            [("enrollment_id", "in", enrolment.ids), ("state", "=", "enrolled")]
        ):
            enr = rec.enrollment_id
            if enr.state == "passed":
                rec._guarded().write({"state": "closed", "closed_on": fields.Date.today()})
                rec.message_post(
                    body="Closed: %s passed %s." % (enr.employee_id.name, enr.course_id.name)
                )
            elif enr.state in ("failed", "withdrawn"):
                rec._guarded().write(
                    {"state": "planned" if rec.plan_id else "identified", "enrollment_id": False}
                )
                rec.message_post(
                    body="Re-opened: enrolment %s was %s." % (enr.display_name, enr.state)
                )


class FixTrainingPlan(models.Model):
    _name = "fix.training.plan"
    _description = "Training Plan"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "year desc, quarter, id desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Branch / Operating Unit")
    period = fields.Selection(
        [("annual", "Annual"), ("quarterly", "Quarterly")], required=True, default="annual"
    )
    year = fields.Integer(required=True, default=lambda self: fields.Date.today().year)
    quarter = fields.Selection([("q1", "Q1"), ("q2", "Q2"), ("q3", "Q3"), ("q4", "Q4")])
    target_role = fields.Char(string="Role / Population")
    currency_id = fields.Many2one(related="company_id.currency_id")
    budget = fields.Monetary(string="Plan Budget", currency_field="currency_id", tracking=True)
    need_ids = fields.One2many("fix.training.need", "plan_id", string="Needs")
    need_count = fields.Integer(compute="_compute_totals")
    planned_cost = fields.Monetary(
        string="Planned Cost", currency_field="currency_id", compute="_compute_totals"
    )
    notes = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(readonly=True)
    return_reason = fields.Char(readonly=True)

    _FROZEN = frozenset(
        {"name", "company_id", "operating_unit_id", "period", "year", "quarter", "budget"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_by_id",
            "approved_by_id",
            "approved_at",
            "return_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._FROZEN
        return locked

    @api.depends("need_ids", "need_ids.course_id", "need_ids.course_id.cost_per_seat")
    def _compute_totals(self):
        for rec in self:
            live = rec.need_ids.filtered(lambda n: n.state != "cancelled")
            rec.need_count = len(live)
            # one seat per need: a course shared by two needs costs twice
            rec.planned_cost = sum(n.course_id.cost_per_seat or 0.0 for n in live)

    @api.constrains("period", "quarter")
    def _check_period(self):
        for rec in self:
            if rec.period == "quarterly" and not rec.quarter:
                raise ValidationError("A quarterly plan names its quarter.")

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, TRAINING, "Drafting a training plan")
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(self.filtered(lambda r: r.state != "draft"), vals, self._FROZEN)
            if frozen:
                raise UserError(
                    "A submitted or decided plan is final (%s)." % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def action_submit(self):
        require_group(self.env, TRAINING, "Submitting a training plan")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft plan is submitted (%s)." % rec.name)
            live = rec.need_ids.filtered(lambda n: n.state != "cancelled")
            if not live:
                raise UserError("%s holds no training need." % rec.name)
            uncosted = live.filtered(lambda n: not n.course_id)
            if uncosted:
                raise UserError(
                    "Name the course of %s so the plan can be costed."
                    % ", ".join(uncosted.mapped("name"))
                )
            if rec.budget and rec.planned_cost > rec.budget + 0.005:
                raise UserError(
                    "%s costs %.2f against its %.2f budget (BRU-LMS-10)."
                    % (rec.name, rec.planned_cost, rec.budget)
                )
            rec._guarded().write(
                {"state": "submitted", "submitted_by_id": self.env.user.id, "return_reason": False}
            )
        return True

    def _fix_assert_approver(self):
        require_group(self.env, BUDGET_APPROVER, "Deciding a training plan")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted plan is decided (%s)." % rec.name)
            if not self.env.su and rec.submitted_by_id == self.env.user:
                raise UserError("The person who submitted %s does not decide it." % rec.name)

    def action_approve(self):
        self._fix_assert_approver()
        for rec in self:
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_return(self, reason=None):
        self._fix_assert_approver()
        reason = _reason(reason, "Say why the plan is returned.")
        for rec in self:
            rec._guarded().write({"state": "draft", "return_reason": reason})
        return True

    def action_cancel(self):
        require_group(self.env, TRAINING, "Cancelling a training plan")
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError("%s is %s; it is not cancelled." % (rec.name, rec.state))
            rec._guarded().write({"state": "cancelled"})
            # its open needs go back to the register, unplanned
            needs = rec.need_ids.filtered(lambda n: n.state in ("identified", "planned"))
            needs.sudo()._guarded().write({"plan_id": False, "state": "identified"})
        return True


# ---------------------------------------------------------------------------
# Page 4 - feedback (FR-LMS-036), withdrawal and substitution (FR-LMS-021)
# ---------------------------------------------------------------------------
class FixTrainingFeedback(models.Model):
    _name = "fix.training.feedback"
    _description = "Training Participant Feedback"
    _order = "submitted_on desc, id desc"

    enrollment_id = fields.Many2one(
        "fix.training.enrollment", string="Enrolment", required=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="enrollment_id.company_id", store=True, index=True)
    employee_id = fields.Many2one(related="enrollment_id.employee_id", store=True, index=True)
    course_id = fields.Many2one(related="enrollment_id.course_id", store=True)
    session_id = fields.Many2one(related="enrollment_id.session_id", store=True)
    trainer_id = fields.Many2one(related="enrollment_id.session_id.trainer_id", store=True)
    rating_content = fields.Selection(RATINGS, string="Content Rating", required=True)
    rating_trainer = fields.Selection(RATINGS, string="Trainer Rating", required=True)
    rating_applicability = fields.Selection(
        RATINGS, string="Applicability to My Work", required=True
    )
    would_recommend = fields.Boolean(string="Would Recommend")
    comments = fields.Text()
    submitted_on = fields.Datetime(readonly=True, default=fields.Datetime.now)
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.user
    )

    _one_per_enrolment = models.Constraint("UNIQUE (enrollment_id)", "One feedback per enrolment.")

    @api.model_create_multi
    def create(self, vals_list):
        Enrollment = self.env["fix.training.enrollment"].sudo()
        user = self.env.user
        for vals in vals_list:
            enr = Enrollment.browse(vals.get("enrollment_id")).exists()
            if not enr:
                raise UserError("Name the enrolment the feedback is about.")
            if self.sudo().search_count([("enrollment_id", "=", enr.id)]):
                raise UserError(
                    "%s has already given feedback on %s."
                    % (enr.employee_id.name, enr.course_id.name)
                )
            if (
                enr.state == "withdrawn"
                or (enr.session_id and enr.attendance != "attended")
                or (not enr.session_id and enr.state == "enrolled")
            ):
                raise UserError(
                    "Feedback follows the training: %s has not attended %s yet."
                    % (enr.employee_id.name, enr.course_id.name)
                )
            if not self.env.su:
                trainee = _own_employee_user(enr.employee_id)
                if trainee and trainee != user:
                    raise AccessError("Only %s gives this feedback." % enr.employee_id.name)
                if not trainee and not user.has_group(TRAINING):
                    raise AccessError(
                        "A Training Manager records the feedback of a trainee with no account."
                    )
            vals["recorded_by_id"] = user.id
            vals["submitted_on"] = fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("Submitted feedback is not changed.")
        return super().write(vals)


class FixTrainingEnrollmentWithdraw(models.Model):
    _inherit = "fix.training.enrollment"

    state = fields.Selection(
        selection_add=[("withdrawn", "Withdrawn")], ondelete={"withdrawn": "set default"}
    )
    withdraw_reason = fields.Char(string="Withdrawal Reason", readonly=True)
    withdrawn_by_id = fields.Many2one("res.users", string="Withdrawn By", readonly=True)
    substitute_of_id = fields.Many2one(
        "fix.training.enrollment", string="Substitute For", readonly=True, ondelete="set null"
    )
    feedback_ids = fields.One2many("fix.training.feedback", "enrollment_id", string="Feedback")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "withdraw_reason",
            "withdrawn_by_id",
            "substitute_of_id",
        }

    def _fix_withdraw(self, reason):
        require_group(self.env, TRAINING, "Withdrawing an enrolment")
        for rec in self:
            if rec.state != "enrolled" or rec.attendance != "pending":
                raise UserError(
                    "%s is decided or its attendance is recorded; it is not withdrawn."
                    % rec.display_name
                )
            # the seat leaves the session and its cost leaves the budget
            rec._guarded().write(
                {
                    "state": "withdrawn",
                    "cost": 0.0,
                    "withdraw_reason": reason,
                    "withdrawn_by_id": self.env.user.id,
                }
            )
            rec.message_post(body="Withdrawn: %s" % reason)
        self.env["fix.training.need"]._fix_follow_enrolment(self)
        return True

    def action_withdraw(self, reason=None):
        return self._fix_withdraw(_reason(reason, "Give the reason for the withdrawal."))

    def action_substitute(self, employee=None):
        """FR-LMS-021: the seat passes to another employee on the same course
        and session; the substitute goes through the budget and capacity rules
        like any enrolment."""
        require_group(self.env, TRAINING, "Substituting a trainee")
        self.ensure_one()
        sub = self._fix_resolve_employee(employee)
        if sub == self.employee_id:
            raise UserError("The substitute is a different employee.")
        session, course, company = self.session_id, self.course_id, self.company_id
        self._fix_withdraw("Substituted by %s" % sub.name)
        new = self.create(
            {
                "course_id": course.id,
                "session_id": session.id or False,
                "employee_id": sub.id,
                "company_id": company.id,
            }
        )
        new._guarded().write({"substitute_of_id": self.id})
        return {"enrollment_id": new.id}

    def _fix_resolve_employee(self, employee):
        Employee = self.env["hr.employee"]
        if isinstance(employee, int) or (isinstance(employee, str) and employee.strip().isdigit()):
            found = Employee.browse(int(employee)).exists()
        else:
            text = (employee or "").strip()
            found = text and Employee.search(
                ["|", ("name", "=ilike", text), ("barcode", "=", text)], limit=2
            )
            if found and len(found) > 1:
                raise UserError("More than one employee is called %s; give the id." % text)
        if not found:
            raise UserError("Name the substitute (employee id, name or badge).")
        return found

    def action_pass(self):
        res = super().action_pass()
        self.env["fix.training.need"]._fix_follow_enrolment(self)
        return res

    def action_fail(self):
        res = super().action_fail()
        self.env["fix.training.need"]._fix_follow_enrolment(self)
        return res


# ---------------------------------------------------------------------------
# Page 5 - mentoring (FR-LMS-028)
# ---------------------------------------------------------------------------
class FixMentoring(models.Model):
    _name = "fix.mentoring"
    _description = "Mentoring Assignment"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    mentee_id = fields.Many2one("hr.employee", string="Mentee", required=True, index=True)
    mentor_id = fields.Many2one("hr.employee", string="Mentor", required=True, index=True)
    competency_id = fields.Many2one("fix.competency", string="Focus Competency")
    objectives = fields.Text(required=True)
    date_start = fields.Date(string="Starts", required=True, default=fields.Date.context_today)
    date_end = fields.Date(string="Planned End")
    interaction_ids = fields.One2many(
        "fix.mentoring.interaction", "mentoring_id", string="Interactions"
    )
    interaction_count = fields.Integer(compute="_compute_interactions")
    hours_logged = fields.Float(compute="_compute_interactions")
    last_interaction_on = fields.Date(compute="_compute_interactions")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    outcome = fields.Selection(
        [
            ("achieved", "Objectives Achieved"),
            ("partly", "Partly Achieved"),
            ("not_achieved", "Not Achieved"),
        ],
        readonly=True,
    )
    closing_note = fields.Char(readonly=True)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _FROZEN = frozenset({"mentee_id", "mentor_id", "competency_id", "date_start", "company_id"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "outcome",
            "closing_note",
            "closed_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._FROZEN
        return locked

    @api.depends("interaction_ids.date", "interaction_ids.duration_hours")
    def _compute_interactions(self):
        for rec in self:
            rows = rec.interaction_ids
            rec.interaction_count = len(rows)
            rec.hours_logged = sum(rows.mapped("duration_hours"))
            rec.last_interaction_on = max(rows.mapped("date")) if rows else False

    @api.constrains("mentee_id", "mentor_id", "date_start", "date_end")
    def _check_pair(self):
        for rec in self:
            if rec.mentor_id == rec.mentee_id:
                raise ValidationError("A mentee is not their own mentor.")
            if rec.date_end and rec.date_start and rec.date_end < rec.date_start:
                raise ValidationError("A mentoring ends after it starts.")
            twin = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("mentee_id", "=", rec.mentee_id.id),
                    ("mentor_id", "=", rec.mentor_id.id),
                    ("state", "in", ("draft", "active")),
                ]
            )
            if twin and rec.state in ("draft", "active"):
                raise ValidationError(
                    "%s already mentors %s." % (rec.mentor_id.name, rec.mentee_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, TRAINING, "Assigning a mentor")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.mentoring") or "MEN/New"
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(self.filtered(lambda r: r.state != "draft"), vals, self._FROZEN)
            if frozen:
                raise UserError(
                    "A started mentoring keeps its pair (%s)." % ", ".join(sorted(frozen))
                )
            if self.filtered(lambda r: r.state in ("closed", "cancelled")):
                raise UserError("A closed or cancelled mentoring is final.")
        return super().write(vals)

    def action_start(self):
        require_group(self.env, TRAINING, "Starting a mentoring")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft mentoring is started (%s)." % rec.name)
            rec._guarded().write({"state": "active"})
            mentor_user = _own_employee_user(rec.mentor_id)
            if mentor_user:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=mentor_user.id,
                    date_deadline=rec.date_start,
                    summary="Mentor %s" % rec.mentee_id.name,
                    note=rec.objectives,
                )
        return True

    def action_close(self, outcome=None):
        """The mentor (or a Training Manager) closes it on the record of the
        interactions; never the mentee."""
        outcome = (outcome or "").strip().lower().replace(" ", "_")
        aliases = {"partly_achieved": "partly", "not": "not_achieved"}
        outcome = aliases.get(outcome, outcome)
        valid = {"achieved", "partly", "not_achieved"}
        if outcome not in valid:
            raise UserError("The outcome is one of: achieved, partly, not_achieved.")
        user = self.env.user
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active mentoring is closed (%s)." % rec.name)
            if not self.env.su:
                if _own_employee_user(rec.mentee_id) == user:
                    raise AccessError("A mentee does not close their own mentoring.")
                if _own_employee_user(rec.mentor_id) != user and not user.has_group(TRAINING):
                    raise AccessError("Only the mentor or a Training Manager closes %s." % rec.name)
            if not rec.interaction_ids:
                raise UserError(
                    "%s has no recorded interaction; a mentoring closes on its record "
                    "(FR-LMS-028)." % rec.name
                )
            rec.sudo()._guarded().write(
                {"state": "closed", "outcome": outcome, "closed_by_id": user.id}
            )
        return True

    def action_cancel(self, reason=None):
        require_group(self.env, TRAINING, "Cancelling a mentoring")
        reason = _reason(reason, "Give the reason the mentoring is cancelled.")
        for rec in self:
            if rec.state not in ("draft", "active"):
                raise UserError("%s is %s; it is not cancelled." % (rec.name, rec.state))
            rec._guarded().write({"state": "cancelled", "closing_note": reason})
        return True


class FixMentoringInteraction(models.Model):
    _name = "fix.mentoring.interaction"
    _description = "Mentoring Interaction"
    _order = "date desc, id desc"

    mentoring_id = fields.Many2one(
        "fix.mentoring", string="Mentoring", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="mentoring_id.company_id", store=True, index=True)
    mentee_id = fields.Many2one(related="mentoring_id.mentee_id", store=True, index=True)
    mentor_id = fields.Many2one(related="mentoring_id.mentor_id", store=True, index=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    duration_hours = fields.Float(string="Duration (hours)")
    mode = fields.Selection(
        [
            ("in_person", "In person"),
            ("field", "Field ride-along"),
            ("workshop", "Workshop / bench"),
            ("phone", "Phone"),
            ("online", "Online"),
        ],
        required=True,
        default="in_person",
    )
    topics = fields.Text(string="Topics Covered", required=True)
    actions_agreed = fields.Text(string="Actions Agreed")
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.user
    )

    def _fix_assert_recorder(self, mentoring):
        if mentoring.state != "active":
            raise UserError(
                "Interactions are recorded on an active mentoring (%s is %s)."
                % (mentoring.name, mentoring.state)
            )
        if self.env.su:
            return
        user = self.env.user
        if _own_employee_user(mentoring.mentee_id) == user:
            raise AccessError("A mentee does not record their own mentoring.")
        if _own_employee_user(mentoring.mentor_id) != user and not user.has_group(TRAINING):
            raise AccessError(
                "The mentor, %s, records the interactions." % mentoring.mentor_id.name
            )

    @api.constrains("date", "duration_hours", "mentoring_id")
    def _check_date(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date > today:
                raise ValidationError("An interaction is recorded after it happens.")
            if rec.mentoring_id.date_start and rec.date < rec.mentoring_id.date_start:
                raise ValidationError("The interaction predates the mentoring.")
            if rec.duration_hours < 0:
                raise ValidationError("The duration is zero or more.")

    @api.model_create_multi
    def create(self, vals_list):
        Mentoring = self.env["fix.mentoring"].sudo()
        for vals in vals_list:
            self._fix_assert_recorder(Mentoring.browse(vals.get("mentoring_id")))
            vals["recorded_by_id"] = self.env.user.id
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            for rec in self:
                self._fix_assert_recorder(rec.mentoring_id.sudo())
                if rec.recorded_by_id != self.env.user:
                    raise AccessError("Only the person who recorded an interaction corrects it.")
            if {"mentoring_id", "recorded_by_id"} & set(vals):
                raise UserError("An interaction stays on its mentoring.")
        return super().write(vals)


# ---------------------------------------------------------------------------
# Page 6 - effectiveness evaluation (FR-LMS-035, BRU-LMS-15, AUT-LMS-12)
# ---------------------------------------------------------------------------
class FixTrainingEffectiveness(models.Model):
    _name = "fix.training.effectiveness"
    _description = "Training Effectiveness Evaluation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    course_id = fields.Many2one("fix.training.course", required=True, ondelete="restrict")
    session_id = fields.Many2one(
        "fix.training.session", string="Session Evaluated", ondelete="restrict"
    )
    target_measure = fields.Char(
        string="Operational Measure Targeted",
        required=True,
        help="e.g. first-time-fix rate, repeat visits, NC count for the trained group",
    )
    measure_unit = fields.Char(string="Unit")
    better_when = fields.Selection(
        [("higher", "Higher is better"), ("lower", "Lower is better")],
        required=True,
        default="higher",
    )
    baseline_value = fields.Float(string="Before", required=True)
    baseline_period = fields.Char(string="Before - Period", required=True)
    after_value = fields.Float(string="After")
    after_period = fields.Char(string="After - Period")
    change = fields.Float(compute="_compute_result", store=True)
    result = fields.Selection(
        [("improved", "Improved"), ("unchanged", "No change"), ("worse", "Worse")],
        compute="_compute_result",
        store=True,
    )
    conclusion = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("evaluated", "Evaluated")],
        required=True,
        default="draft",
        tracking=True,
    )
    evaluated_by_id = fields.Many2one("res.users", string="Evaluated By", readonly=True)
    evaluated_on = fields.Date(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "evaluated_by_id", "evaluated_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state == "evaluated" for rec in self):
            locked = locked | set(self._fields) - {"id", "display_name"}
        return locked

    @api.depends("baseline_value", "after_value", "better_when", "after_period")
    def _compute_result(self):
        for rec in self:
            if not rec.after_period:
                rec.change = 0.0
                rec.result = False
                continue
            rec.change = (rec.after_value or 0.0) - (rec.baseline_value or 0.0)
            gain = rec.change if rec.better_when == "higher" else -rec.change
            rec.result = "improved" if gain > 1e-9 else ("worse" if gain < -1e-9 else "unchanged")

    @api.constrains("session_id", "course_id")
    def _check_session(self):
        for rec in self:
            sess = rec.session_id
            if sess and sess.course_id != rec.course_id:
                raise ValidationError("Session %s delivered another course." % sess.name)
            if sess and sess.state != "done":
                raise ValidationError(
                    "Session %s has not been held; there is nothing to evaluate yet." % sess.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, TRAINING, "Recording a training evaluation")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.training.effectiveness") or "TEV/New"
                )
            if vals.get("session_id") and not vals.get("course_id"):
                sess = self.env["fix.training.session"].browse(vals["session_id"])
                vals["course_id"] = sess.course_id.id
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open() and self.filtered(lambda r: r.state == "evaluated"):
            raise UserError("An evaluated record is final; record a new evaluation.")
        return super().write(vals)

    def action_evaluate(self):
        """BRU-LMS-15: the before / after on the targeted measure, with a
        conclusion, by someone other than the session's trainer."""
        require_group(self.env, TRAINING, "Evaluating training effectiveness")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already evaluated." % rec.name)
            if not rec.after_period:
                raise UserError("Record the after-value and its period on %s." % rec.name)
            if not (rec.conclusion or "").strip():
                raise UserError("Write the conclusion of %s." % rec.name)
            trainer_user = _own_employee_user(rec.session_id.trainer_id)
            if not self.env.su and trainer_user and trainer_user == self.env.user:
                raise UserError("The trainer does not evaluate their own session.")
            rec._guarded().write(
                {
                    "state": "evaluated",
                    "evaluated_by_id": self.env.user.id,
                    "evaluated_on": fields.Date.context_today(self),
                }
            )
        return True
