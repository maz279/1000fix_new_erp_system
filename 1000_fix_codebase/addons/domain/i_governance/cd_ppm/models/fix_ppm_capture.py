# M67 capture audit (2026-11-18): the records the specification makes M67 own
# that no page could capture because no model held them.
#
#   - fix.project.deliverable (FR-PPM-004 P0, §8.2): every deliverable with its
#     acceptance criteria and evidence, submitted by the delivery team and
#     accepted or sent back by a reviewer who did not submit it. A milestone
#     with deliverables completes only when they are all accepted (BRU-PPM-11).
#   - fix.project.change (FR-PPM-013 P0, BRU-PPM-06 H): a scope change priced
#     for cost and schedule, decided by a sponsor who does not deliver the
#     project. An approved cost impact on a running project becomes the
#     Requested Budget, which re-baselines only through the DOFA approval the
#     project already routes (BRU-PPM-05/07): the change never edits the budget.
#   - fix.project.budget.line (FR-PPM-024 P0): the budget by cost category. The
#     lines never exceed the project budget and freeze when it is baselined.
#   - fix.project.lesson (FR-PPM-032 P0, BRU-PPM-14 H): lessons learned, passed
#     to Quality (M23) as an event. A project closes only with one passed.
#   - fix.project.benefit (FR-PPM-032 P0, BRU-PPM-15 H): the benefit an internal
#     initiative was justified by, and its measurement by a sponsor who does not
#     deliver it. An internal initiative closes only with a benefit measured.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_ppm import PM_GROUP, SPONSOR_GROUP

BUDGET_CATEGORIES = [
    ("labour", "Labour"),
    ("parts", "Parts"),
    ("subcontract", "Subcontract"),
    ("travel", "Travel"),
    ("equipment", "Equipment"),
    ("overhead", "Overhead"),
]

LESSON_CATEGORIES = [
    ("scope", "Scope"),
    ("schedule", "Schedule"),
    ("cost", "Cost"),
    ("quality", "Quality"),
    ("resource", "Resourcing"),
    ("vendor", "Vendor / Subcontractor"),
    ("client", "Client"),
    ("other", "Other"),
]


def _is_delivery_team(env):
    return env.su or env.user.has_group(PM_GROUP) or env.user.has_group(SPONSOR_GROUP)


def _refuse_unless_superuser(records, what):
    if not records.env.su:
        raise UserError("%s is evidence: it cannot be deleted." % what)


class FixProjectDeliverable(models.Model):
    _name = "fix.project.deliverable"
    _description = "Project Deliverable"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "project_id, id"

    name = fields.Char(string="Reference", required=True, default="New", copy=False)
    title = fields.Char(string="Deliverable", required=True, tracking=True)
    project_id = fields.Many2one(
        "fix.project", string="Project", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="project_id.company_id", store=True, index=True)
    milestone_id = fields.Many2one(
        "fix.project.milestone",
        string="Milestone",
        ondelete="set null",
        help="The milestone whose acceptance this deliverable is part of.",
    )
    acceptance_criteria = fields.Text(required=True)
    evidence_requirement = fields.Char(
        string="Evidence Required", help="What must be attached for the reviewer to accept."
    )
    reviewer_id = fields.Many2one(
        "res.users", string="Reviewer", help="Who accepts it. Never the person who submits it."
    )
    evidence_file = fields.Binary(string="Evidence", attachment=True, copy=False)
    evidence_filename = fields.Char(copy=False)
    submitted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    submitted_on = fields.Datetime(readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("accepted", "Accepted"),
            ("rework", "Sent Back"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "submitted_by_id",
            "submitted_on",
            "decided_by_id",
            "decided_on",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state in ("submitted", "accepted"):
            locked |= {
                "title",
                "project_id",
                "milestone_id",
                "acceptance_criteria",
                "evidence_requirement",
                "reviewer_id",
                "evidence_file",
                "evidence_filename",
            }
        return locked

    @api.constrains("milestone_id", "project_id")
    def _check_milestone_project(self):
        for rec in self:
            if rec.milestone_id and rec.milestone_id.project_id != rec.project_id:
                raise ValidationError(
                    "Milestone %s belongs to another project." % rec.milestone_id.display_name
                )

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        # the reference is a stamp: written by the server, never sent by a form
        for rec in recs:
            rec._guarded().write(
                {
                    "name": self.env["ir.sequence"].next_by_code("fix.project.deliverable")
                    or "DLV/New"
                }
            )
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                frozen = rec._fix_form_locked_fields() - rec._fix_guarded_fields()
                changed = [
                    n for n in frozen & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "Deliverable %s is %s: what the reviewer judges cannot change. Send it "
                        "back to rework it." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda d: d.state != "draft"):
            _refuse_unless_superuser(self, "A submitted deliverable")
        return super().unlink()

    def action_submit(self):
        if not _is_delivery_team(self.env):
            raise AccessError("A project manager submits a deliverable for acceptance.")
        for rec in self:
            if rec.state not in ("draft", "rework"):
                raise UserError("Only a draft or sent-back deliverable is submitted.")
            if not rec.evidence_file:
                raise UserError(
                    "Attach the evidence of %s before it is submitted: the reviewer accepts "
                    "against it." % rec.name
                )
            if not rec.reviewer_id:
                raise UserError("Name the reviewer of %s before it is submitted." % rec.name)
            if rec.reviewer_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you are the reviewer of %s, so someone else "
                    "submits it." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by_id": self.env.user.id,
                    "submitted_on": fields.Datetime.now(),
                    "rejection_reason": False,
                }
            )

    def _deliverable_assert_reviewer(self):
        """The named reviewer, or a sponsor, who did not submit it."""
        self.check_access("read")
        if self.env.su:
            return self
        user = self.env.user
        for rec in self.sudo():
            if user == rec.submitted_by_id:
                raise UserError(
                    "Segregation of duties: %s was submitted by you, so another person "
                    "accepts it." % rec.name
                )
            if user != rec.reviewer_id and not user.has_group(SPONSOR_GROUP):
                raise AccessError(
                    "%s is decided by its reviewer %s or a project sponsor."
                    % (rec.name, rec.reviewer_id.name or "-")
                )
        return self.sudo()

    def action_accept(self):
        for rec in self._deliverable_assert_reviewer():
            if rec.state != "submitted":
                raise UserError("Only a submitted deliverable is accepted.")
            rec._guarded().write(
                {
                    "state": "accepted",
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Accepted by %s." % self.env.user.name)

    def action_send_back(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why the deliverable is sent back: the team reworks against it.")
        for rec in self._deliverable_assert_reviewer():
            if rec.state != "submitted":
                raise UserError("Only a submitted deliverable is sent back.")
            rec._guarded().write(
                {
                    "state": "rework",
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "rejection_reason": reason.strip(),
                }
            )
            rec.message_post(body="Sent back by %s: %s" % (self.env.user.name, reason.strip()))


class FixProjectMilestoneDeliverables(models.Model):
    _inherit = "fix.project.milestone"

    deliverable_ids = fields.One2many(
        "fix.project.deliverable", "milestone_id", string="Deliverables"
    )

    def action_complete(self):
        # BRU-PPM-11, §8.2: a milestone is complete when what it delivers is accepted.
        for rec in self:
            open_items = rec.sudo().deliverable_ids.filtered(lambda d: d.state != "accepted")
            if open_items:
                raise UserError(
                    "%d deliverable(s) of milestone %s are not accepted yet: %s."
                    % (len(open_items), rec.name, ", ".join(open_items.mapped("name")))
                )
        return super().action_complete()


class FixProjectChange(models.Model):
    _name = "fix.project.change"
    _description = "Project Scope Change"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Reference", required=True, default="New", copy=False)
    project_id = fields.Many2one(
        "fix.project", string="Project", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="project_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="project_id.currency_id")
    title = fields.Char(string="Change", required=True)
    description = fields.Text(string="Scope Change", required=True)
    justification = fields.Text(required=True)
    cost_impact = fields.Monetary(
        currency_field="currency_id",
        help="Added cost (negative for a saving). An approved increase on a running project "
        "becomes its Requested Budget, approved under DOFA at the tier of the new total.",
    )
    schedule_impact_days = fields.Integer(
        string="Schedule Impact (days)", help="Days the planned end moves when approved."
    )
    resource_impact = fields.Text()
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    submitted_on = fields.Datetime(readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Text(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("withdrawn", "Withdrawn"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "requested_by_id",
            "submitted_on",
            "decided_by_id",
            "decided_on",
            "decision_note",
        }

    PRICED = (
        "project_id",
        "title",
        "description",
        "justification",
        "cost_impact",
        "schedule_impact_days",
        "resource_impact",
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self.PRICED)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        # the reference and the author are stamps: written by the server only
        for rec in recs:
            rec._guarded().write(
                {
                    "name": self.env["ir.sequence"].next_by_code("fix.project.change") or "PCR/New",
                    "requested_by_id": self.env.user.id,
                }
            )
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda c: c.state != "draft"):
                changed = [
                    n
                    for n in set(self.PRICED) & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "%s is %s: the change that was priced and decided cannot be rewritten. "
                        "Raise a new change." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda c: c.state != "draft"):
            _refuse_unless_superuser(self, "A submitted scope change")
        return super().unlink()

    def action_submit(self):
        if not _is_delivery_team(self.env):
            raise AccessError("A project manager submits a scope change.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft change is submitted.")
            if rec.project_id.state in ("completed", "cancelled"):
                raise UserError("Project %s is closed." % rec.project_id.display_name)
            rec._guarded().write({"state": "submitted", "submitted_on": fields.Datetime.now()})

    def action_withdraw(self):
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError("Only an undecided change is withdrawn.")
            user = self.env.user
            if not (self.env.su or user == rec.requested_by_id or user.has_group(PM_GROUP)):
                raise AccessError("The requester or a project manager withdraws a change.")
            rec._guarded().write({"state": "withdrawn"})

    def _decide(self, state, note):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted change is decided.")
            rec.project_id._ppm_assert_sponsor("Deciding a scope change")
            if not self.env.su and self.env.user == rec.requested_by_id:
                raise UserError("Segregation of duties: you raised %s." % rec.name)
            rec.sudo()._guarded().write(
                {
                    "state": state,
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "decision_note": note,
                }
            )

    def action_approve(self, note=None):
        self._decide("approved", (note or "").strip() or False)
        for rec in self:
            project = rec.project_id.sudo()
            consequences = []
            if rec.schedule_impact_days and project.date_end:
                new_end = fields.Date.add(project.date_end, days=rec.schedule_impact_days)
                project.write({"date_end": new_end})
                consequences.append("planned end moved to %s" % new_end)
            if rec.cost_impact > 0 and project.state in ("active", "on_hold"):
                requested = max(project.budget_requested or 0.0, project.budget or 0.0)
                project.write({"budget_requested": requested + rec.cost_impact})
                consequences.append(
                    "Requested Budget set to %.2f: the project manager requests its budget "
                    "approval, which re-baselines the project when granted"
                    % project.budget_requested
                )
            elif rec.cost_impact and project.state == "draft":
                consequences.append(
                    "the project is still in draft: its budget is set on the project before the "
                    "budget approval"
                )
            project.message_post(
                body="Scope change %s approved by %s%s"
                % (
                    rec.name,
                    self.env.user.name,
                    (": " + "; ".join(consequences) + ".") if consequences else ".",
                )
            )
            publish(
                self.env,
                "project.change_approved",
                "fix.project.change",
                rec.id,
                {
                    "change": rec.name,
                    "project": project.name,
                    "cost_impact": rec.cost_impact,
                    "schedule_impact_days": rec.schedule_impact_days,
                },
            )

    def action_reject(self, note=None):
        if not (note or "").strip():
            raise UserError("State why the change is rejected.")
        self._decide("rejected", note.strip())


class FixProjectBudgetLine(models.Model):
    _name = "fix.project.budget.line"
    _description = "Project Budget by Category"
    _order = "project_id, category"

    project_id = fields.Many2one(
        "fix.project", string="Project", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="project_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="project_id.currency_id")
    category = fields.Selection(BUDGET_CATEGORIES, required=True)
    amount = fields.Monetary(currency_field="currency_id", required=True)
    note = fields.Char()

    _category_unique = models.Constraint(
        "UNIQUE (project_id, category)", "One budget line per category and project."
    )

    @api.constrains("amount", "project_id", "category")
    def _check_within_budget(self):
        for project in self.mapped("project_id"):
            lines = self.search([("project_id", "=", project.id)])
            if any(line.amount < 0 for line in lines):
                raise ValidationError("A budget line cannot be negative.")
            total = sum(lines.mapped("amount"))
            ceiling = project.budget or 0.0
            if total > ceiling + 0.005:
                raise ValidationError(
                    "The category lines of %s add up to %.2f, above its budget of %.2f. Raise "
                    "the budget (or request an overrun) first."
                    % (project.display_name, total, ceiling)
                )

    def _refuse_baselined(self, projects):
        if self.env.su:
            return
        frozen = projects.filtered(lambda p: p.state != "draft")
        if frozen:
            raise UserError(
                "The budget of %s is baselined: its category split froze at activation "
                "(BRU-PPM-05)." % ", ".join(frozen.mapped("display_name"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = [v.get("project_id") for v in vals_list if v.get("project_id")]
        self._refuse_baselined(self.env["fix.project"].browse(ids))
        return super().create(vals_list)

    def write(self, vals):
        projects = self.mapped("project_id")
        if vals.get("project_id"):
            projects |= self.env["fix.project"].browse(vals["project_id"])
        self._refuse_baselined(projects)
        return super().write(vals)

    def unlink(self):
        self._refuse_baselined(self.mapped("project_id"))
        return super().unlink()


class FixProjectLesson(models.Model):
    _name = "fix.project.lesson"
    _description = "Project Lesson Learned"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Reference", required=True, default="New", copy=False)
    project_id = fields.Many2one(
        "fix.project", string="Project", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="project_id.company_id", store=True, index=True)
    category = fields.Selection(LESSON_CATEGORIES, required=True, default="other")
    observation = fields.Text(string="What Happened", required=True)
    recommendation = fields.Text(string="What To Do Next Time", required=True)
    recorded_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    shared_by_id = fields.Many2one("res.users", string="Passed By", readonly=True, copy=False)
    shared_on = fields.Datetime(string="Passed to Quality On", readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Recorded"), ("shared", "Passed to Quality (M23)")],
        default="draft",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "recorded_by_id",
            "shared_by_id",
            "shared_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state == "shared":
            locked |= {"project_id", "category", "observation", "recommendation"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        # the reference and the author are stamps: written by the server only
        for rec in recs:
            rec._guarded().write(
                {
                    "name": self.env["ir.sequence"].next_by_code("fix.project.lesson") or "LSN/New",
                    "recorded_by_id": self.env.user.id,
                }
            )
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state == "shared"):
                text = {"project_id", "category", "observation", "recommendation"}
                if [n for n in text & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])]:
                    raise UserError(
                        "Lesson %s was passed to Quality: record a new lesson instead." % rec.name
                    )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda r: r.state == "shared"):
            _refuse_unless_superuser(self, "A lesson passed to Quality")
        return super().unlink()

    def action_share(self):
        """BRU-PPM-14: the lesson reaches Quality (M23) as project.lesson_recorded."""
        if not _is_delivery_team(self.env):
            raise AccessError("A project manager or sponsor passes a lesson to Quality.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Lesson %s was already passed to Quality." % rec.name)
            rec._guarded().write(
                {
                    "state": "shared",
                    "shared_by_id": self.env.user.id,
                    "shared_on": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "project.lesson_recorded",
                "fix.project.lesson",
                rec.id,
                {
                    "lesson": rec.name,
                    "project": rec.project_id.name,
                    "category": rec.category,
                    "observation": rec.observation,
                    "recommendation": rec.recommendation,
                },
            )


class FixProjectBenefit(models.Model):
    _name = "fix.project.benefit"
    _description = "Project Benefit Realisation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "project_id, id"

    name = fields.Char(string="Benefit", required=True)
    project_id = fields.Many2one(
        "fix.project", string="Project", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="project_id.company_id", store=True, index=True)
    business_case_target = fields.Float(
        string="Business Case Target", required=True, help="The figure the initiative promised."
    )
    unit = fields.Char(
        required=True, help="What the target counts, e.g. BDT per year, hours saved per month."
    )
    measurement_method = fields.Text(required=True)
    owner_id = fields.Many2one("res.users", string="Benefit Owner")
    measured_value = fields.Float(readonly=True, copy=False)
    measured_on = fields.Date(readonly=True, copy=False)
    measured_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    measurement_evidence = fields.Text(readonly=True, copy=False)
    realised_pct = fields.Float(string="Realised %", compute="_compute_realised", store=True)
    state = fields.Selection(
        [("planned", "Planned"), ("measured", "Measured")],
        default="planned",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "measured_value",
            "measured_on",
            "measured_by_id",
            "measurement_evidence",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state == "measured":
            locked |= {"project_id", "business_case_target", "unit", "measurement_method"}
        return locked

    @api.depends("measured_value", "business_case_target", "state")
    def _compute_realised(self):
        for rec in self:
            if rec.state == "measured" and rec.business_case_target:
                rec.realised_pct = round(100.0 * rec.measured_value / rec.business_case_target, 1)
            else:
                rec.realised_pct = 0.0

    @api.constrains("project_id")
    def _check_internal(self):
        for rec in self:
            if rec.project_id.project_type != "internal":
                raise ValidationError(
                    "Benefit realisation is measured for internal initiatives; %s is a %s project "
                    "and is judged by its margin."
                    % (
                        rec.project_id.display_name,
                        dict(rec.project_id._fields["project_type"].selection)[
                            rec.project_id.project_type
                        ],
                    )
                )

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state == "measured"):
                pinned = {"project_id", "business_case_target", "unit", "measurement_method"}
                if [n for n in pinned & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])]:
                    raise UserError(
                        "%s was measured against this target: the target cannot move." % rec.name
                    )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda r: r.state == "measured"):
            _refuse_unless_superuser(self, "A measured benefit")
        return super().unlink()

    def action_record_measurement(self, measured_value=None, evidence=None):
        """A sponsor who does not deliver the initiative measures its benefit."""
        try:
            value = float(measured_value)
        except (TypeError, ValueError):
            raise UserError("Enter the measured value as a number.") from None
        if not (evidence or "").strip():
            raise UserError("State the evidence of the measurement (report, data source, period).")
        for rec in self:
            if rec.state != "planned":
                raise UserError("%s is already measured." % rec.name)
            rec.project_id._ppm_assert_sponsor("Measuring a project's benefit")
            rec.sudo()._guarded().write(
                {
                    "state": "measured",
                    "measured_value": value,
                    "measured_on": fields.Date.context_today(rec),
                    "measured_by_id": self.env.user.id,
                    "measurement_evidence": evidence.strip(),
                }
            )


class FixProjectClosureRecords(models.Model):
    _inherit = "fix.project"

    deliverable_ids = fields.One2many(
        "fix.project.deliverable", "project_id", string="Deliverables"
    )
    change_ids = fields.One2many("fix.project.change", "project_id", string="Scope Changes")
    budget_line_ids = fields.One2many(
        "fix.project.budget.line", "project_id", string="Budget by Category"
    )
    lesson_ids = fields.One2many("fix.project.lesson", "project_id", string="Lessons Learned")
    benefit_ids = fields.One2many("fix.project.benefit", "project_id", string="Benefits")

    def _ppm_closure_records_ready(self):
        """Called by action_complete once delivery, billing and gates pass."""
        for rec in self:
            project = rec.sudo()
            pending = project.change_ids.filtered(lambda c: c.state == "submitted")
            if pending:
                raise UserError(
                    "%d scope change(s) of %s wait for a decision: decide or withdraw them before "
                    "closure." % (len(pending), rec.display_name)
                )
            if not project.lesson_ids.filtered(lambda r: r.state == "shared"):
                raise UserError(
                    "%s has no lesson learned passed to Quality: a project closes only with its "
                    "lessons recorded and passed to M23 (BRU-PPM-14)." % rec.display_name
                )
            if project.project_type == "internal" and not project.benefit_ids.filtered(
                lambda b: b.state == "measured"
            ):
                raise UserError(
                    "%s is an internal initiative with no benefit measured against its business "
                    "case: record the benefit and its measurement before closure (BRU-PPM-15)."
                    % rec.display_name
                )
