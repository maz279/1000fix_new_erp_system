# fix_onboarding_task — M58: onboarding as owned, dated tasks (FR-TAO-027,
# FR-TAO-033, T-07, AC-08).
#
# A09 audit M58-F8: onboarding completed on four hand-ticked booleans, with no
# tasks, owners or due dates. A template's task set is generated at hire;
# each task has one owner, a due date and its completion evidence; only the
# owner completes it; a mandatory task is never cancelled, and the plan
# completes only when every mandatory task is done.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .fix_talent import _is_recruiter, _require_recruiter

FUNCTIONS = [
    ("hr", "HR"),
    ("it", "IT / Identity (M29)"),
    ("stores", "Tools, Equipment & Van Stock (M17/M03)"),
    ("facilities", "Facilities & ID Card"),
    ("safety", "Safety (M59)"),
    ("branch", "Branch / Mentor"),
]
OWNER_EDITABLE = ("evidence_note", "evidence_file", "evidence_filename")


def guard_first(records, vals):
    """Refuse a changing write of a guarded field with the guard's own
    message, before any role check speaks (the control suite reads it)."""
    if records._fix_guard_open():
        return
    touched = records._fix_guarded_fields() & set(vals)
    changed = {n for r in records for n in touched if r._fix_guard_differs(n, vals[n], r[n])}
    if changed:
        records._fix_guard_refuse(changed)


class FixOnboardingTemplate(models.Model):
    _name = "fix.onboarding.template"
    _description = "Onboarding Task Template"
    _order = "is_default desc, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", index=True, help="Empty: the template serves every company."
    )
    is_default = fields.Boolean(
        string="Default Template", help="Used for a hire whose requisition names no template."
    )
    active = fields.Boolean(default=True)
    line_ids = fields.One2many("fix.onboarding.template.line", "template_id", string="Tasks")


class FixOnboardingTemplateLine(models.Model):
    _name = "fix.onboarding.template.line"
    _description = "Onboarding Template Task"
    _order = "template_id, sequence, id"

    template_id = fields.Many2one(
        "fix.onboarding.template", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    function = fields.Selection(FUNCTIONS, required=True, default="hr")
    owner_user_id = fields.Many2one(
        "res.users",
        string="Owner",
        help="Empty: the requisition's hiring manager, else the recruiter making the hire.",
    )
    due_offset_days = fields.Integer(
        string="Due (days from joining)",
        default=0,
        help="Days from the joining date; negative is before it.",
    )
    mandatory = fields.Boolean(default=True, help="The plan completes only when it is done.")
    evidence_required = fields.Boolean(
        string="File Evidence Required", default=False, help="A file, not only a note."
    )
    field_role_only = fields.Boolean(
        string="Field Roles Only", help="Generated only for a field / in-home role."
    )


class FixOnboardingTask(models.Model):
    _name = "fix.onboarding.task"
    _description = "Onboarding Task"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "due_date, id"

    plan_id = fields.Many2one("fix.onboarding.plan", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="plan_id.company_id", store=True, string="Company")
    employee_id = fields.Many2one(related="plan_id.employee_id", string="New Hire")
    template_line_id = fields.Many2one(
        "fix.onboarding.template.line", readonly=True, ondelete="set null"
    )
    name = fields.Char(required=True)
    function = fields.Selection(FUNCTIONS, required=True, default="hr")
    owner_id = fields.Many2one(
        "res.users", string="Owner", required=True, index=True, tracking=True
    )
    due_date = fields.Date(required=True, tracking=True)
    mandatory = fields.Boolean(readonly=True, default=True)
    evidence_required = fields.Boolean(readonly=True)
    evidence_note = fields.Text(string="Completion Evidence")
    evidence_file = fields.Binary(string="Evidence File", attachment=True, copy=False)
    evidence_filename = fields.Char(copy=False)
    overdue = fields.Boolean(compute="_compute_overdue")
    completed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    completed_on = fields.Datetime(readonly=True, copy=False)
    cancel_reason = fields.Char(readonly=True, copy=False)
    # AUT-TAO-13: 0 none, 1 the owner was told on the due date, 2 overdue and
    # escalated to the hiring manager (or HR). Each level once per task.
    alert_level = fields.Integer(string="Due-Date Alert Level", readonly=True, copy=False)
    alerted_on = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("done", "Done"), ("cancelled", "Cancelled")],
        required=True,
        default="open",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "completed_by_id",
            "completed_on",
            "cancel_reason",
            "alert_level",
            "alerted_on",
            "mandatory",
            "evidence_required",
            "plan_id",
            "template_line_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "open" for r in self):
            locked |= {"name", "function", "owner_id", "due_date", *OWNER_EDITABLE}
        return locked

    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.overdue = bool(rec.state == "open" and rec.due_date and rec.due_date < today)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            _require_recruiter(self.env, "add an onboarding task")
            guarded = self._fix_guarded_fields() - {"plan_id"}
            for vals in vals_list:
                touched = guarded & set(vals)
                if touched:
                    self._fix_guard_refuse(touched)
                # an ad-hoc task is optional; mandatory tasks come from the template
                vals["mandatory"] = False
            return super(FixOnboardingTask, self._guarded()).create(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            if any(r.state != "open" for r in self):
                raise UserError("A done or cancelled onboarding task is a record.")
            if not _is_recruiter(self.env):
                other = set(vals) - set(OWNER_EDITABLE)
                if other or any(r.owner_id != self.env.user for r in self):
                    raise AccessError(
                        "The task owner records the evidence; Recruitment plans the task."
                    )
        return super().write(vals)

    def action_done(self):
        """The owner completes the task, on its evidence."""
        for rec in self:
            if not self.env.su and rec.owner_id != self.env.user:
                raise AccessError("Only %s completes %s." % (rec.owner_id.name, rec.name))
            if rec.state != "open":
                raise UserError("%s is not open." % rec.name)
            if rec.plan_id.sudo().state not in ("draft", "in_progress"):
                raise UserError("The onboarding plan of %s is closed." % rec.name)
            if not (rec.evidence_note or "").strip():
                raise UserError("Record what was done for %s (the completion evidence)." % rec.name)
            if rec.evidence_required and not rec.evidence_file:
                raise UserError("%s needs its evidence file." % rec.name)
            rec._guarded().write(
                {
                    "state": "done",
                    "completed_by_id": self.env.uid,
                    "completed_on": fields.Datetime.now(),
                }
            )
        return True

    @api.model
    def cron_notify_due_tasks(self):
        """AUT-TAO-13: on its due date an open task's owner is told (level 1);
        once it is overdue it escalates to the requisition's hiring manager, or
        to the HR managers when there is none (level 2). Each level once per
        task: idempotent. Superuser."""
        today = fields.Date.context_today(self)
        tasks = self.sudo().search(
            [
                ("state", "=", "open"),
                ("due_date", "<=", today),
                ("alert_level", "<", 2),
                ("plan_id.state", "in", ("draft", "in_progress")),
            ]
        )
        hr = (
            self.env.ref("hr.group_hr_manager")
            .sudo()
            .all_user_ids.filtered(lambda u: u.active and not u.share)
        )
        raised = 0
        for task in tasks:
            level = 2 if task.due_date < today else 1
            if task.alert_level >= level:
                continue
            plan = task.plan_id.sudo()
            if level == 1:
                users = task.owner_id
                what = "is due today"
            else:
                manager = plan.requisition_id.hiring_manager_id
                users = manager or hr.filtered(lambda u, p=plan: p.company_id in u.company_ids)
                what = "is OVERDUE since %s (owner %s)" % (task.due_date, task.owner_id.name)
            note = "Onboarding task %s for %s %s." % (task.name, plan.name, what)
            for user in users.filtered(lambda u: u.active and not u.share):
                task.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=today,
                    summary="Onboarding task: %s" % task.name,
                    note=note,
                    user_id=user.id,
                )
            task.message_post(body=note)
            task._guarded().write({"alert_level": level, "alerted_on": fields.Datetime.now()})
            raised += 1
        return raised

    def action_cancel(self, reason=None):
        _require_recruiter(self.env, "cancel an onboarding task")
        if not (reason or "").strip():
            raise UserError("Say why the task is cancelled.")
        for rec in self:
            if rec.mandatory:
                raise UserError("%s is mandatory; it is done, never cancelled." % rec.name)
            if rec.state != "open":
                raise UserError("%s is not open." % rec.name)
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason.strip()})
        return True
