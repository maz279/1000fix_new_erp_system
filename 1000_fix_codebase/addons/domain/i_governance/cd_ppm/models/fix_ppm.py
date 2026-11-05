# fix_ppm — M67: project, program, portfolio management (P10-M05 / R08-M03).
#
# A12 workflow audit (2026-11-04) P1-3 / M67-3 / M67-4 / M67-5 / M67-6:
# every state on these models was a plain write, a project went active with
# no budget approval and a failed G1 behind it, and the PM completed and
# billed his own milestones with nothing recorded. Now:
#   - fix.project routes its BUDGET through M63 + DOFA (fix.dofa.mixin):
#     activation needs a value-based approval, the approved budget is
#     baselined and cannot be raised above the baseline without a new
#     approval (BRU-PPM-03/04/05/07);
#   - action_activate refuses when any gate failed and requires the G1 gate
#     closed pass/conditional when the project has one;
#   - states are guarded (fix.guarded.mixin) — they change only through the
#     actions below, from the state the lifecycle allows;
#   - a milestone completes only with tasks done AND an acceptance recorded
#     by someone who is not the project manager (BRU-PPM-11);
#   - tasks and billing lines may not point at another project's milestone.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

# Budget bands for the DOFA ladder (business decision, report §7 "05-04 §7
# authority matrix"). Same ladder as the estate cost decisions
# (cd_facility ESTATE_COST_DOFA_THRESHOLDS): Tier 2 up to BDT 250,000,
# Tier 3 up to 1,000,000, Tier 4 (CFO) above. An unbudgeted project is
# Tier 0 and needs no DOFA approval.
PROJECT_BUDGET_DOFA_THRESHOLDS = [
    (0.0, "tier_0"),
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]

SPONSOR_GROUP = "cd_ppm.group_ppm_sponsor"


class FixProject(models.Model):
    _name = "fix.project"
    _description = "Project"
    # fix.dofa.mixin brings fix.approvable.mixin and fix.guarded.mixin; the
    # DOFA stamp is applied by the M63 engine in the approver's inbox.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "date_start desc"

    # M63 routing: the record's own DOFA approve method applies the stamp.
    _approval_domain = "other"
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    code = fields.Char(string="Project Code", readonly=True, copy=False)
    project_type = fields.Selection(
        [
            ("internal", "Internal"),
            ("client", "Client Project"),
            ("infrastructure", "Infrastructure"),
        ],
        required=True,
        default="internal",
    )
    manager_id = fields.Many2one("hr.employee", string="Project Manager")
    date_start = fields.Date()
    date_end = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    budget = fields.Monetary(string="Budget", currency_field="currency_id")
    # M67-2: the billing ceiling. Zero means "no contract value recorded" and
    # the constraint does not apply (the DOFA budget approval still does).
    contract_value = fields.Monetary(
        string="Contract Value",
        currency_field="currency_id",
        help="The approved contract/billing ceiling: the sum of all billing lines "
        "of this project may not exceed it (BRU-PPM billing ceiling).",
    )
    baseline_budget = fields.Monetary(
        string="Baselined Budget",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The budget as approved when the project was activated. Raising the "
        "budget above the baseline needs a new DOFA approval (BRU-PPM-05/07).",
    )
    actual_cost = fields.Monetary(string="Actual Cost", currency_field="currency_id")
    budget_variance = fields.Monetary(
        compute="_compute_variance",
        string="Budget Variance",
        currency_field="currency_id",
        store=True,
    )
    variance_pct = fields.Float(compute="_compute_variance", string="Variance %", store=True)
    progress_pct = fields.Float(string="Progress %", default=0.0)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("on_hold", "On Hold"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    template_id = fields.Many2one(
        "fix.project.template",
        string="Created From Template",
        readonly=True,
        copy=False,
        help="M67-10/BRU-PPM-19: the template the project was instantiated from.",
    )
    template_version = fields.Char(readonly=True, copy=False)
    milestone_ids = fields.One2many("fix.project.milestone", "project_id", string="Milestones")
    task_ids = fields.One2many("fix.project.task", "project_id", string="Tasks")
    billing_ids = fields.One2many("fix.project.billing", "project_id", string="Billing Lines")
    # NOTE: gate_ids (fix.project.gate reverse relation) is declared in
    # cd_itsm/models/fix_itsm_ops.py, next to the gate model: cd_itsm depends
    # on cd_ppm (the gate's project_id), so this module cannot reference
    # fix.project.gate at load time. The field resolves by name, so
    # self.gate_ids below works unchanged.

    # ---- guarded workflow fields (M67-5) ---------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "baseline_budget"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            # BRU-PPM-05: once delivery starts the baseline and the manager
            # the gates were reviewed against are frozen.
            locked |= {"baseline_budget", "manager_id"}
        return locked

    # ---- DOFA / M63 hooks (P1-3) ------------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.budget or 0.0

    def _dofa_thresholds(self):
        return PROJECT_BUDGET_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (project budget)" % self._dofa_amount()

    @api.depends("budget")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_excluded(self):
        # §13 SoD: the project manager never approves the budget they will
        # spend (BRU-PPM-04). The engine already excludes requester/creator.
        excluded = super()._approval_excluded()
        if self.manager_id:
            excluded |= self.manager_id.sudo().user_id
        return excluded.sudo()

    def _approval_pinned_fields(self) -> set:
        # The approval covers the budget AND who runs the project.
        return super()._approval_pinned_fields() | {"manager_id", "contract_value"}

    # ---- computed ----------------------------------------------------------
    @api.depends("budget", "actual_cost")
    def _compute_variance(self):
        for rec in self:
            rec.budget_variance = (rec.budget or 0.0) - (rec.actual_cost or 0.0)
            rec.variance_pct = ((rec.budget_variance / rec.budget) * 100.0) if rec.budget else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["code"] = self.env["ir.sequence"].next_by_code("fix.project") or "PRJ/New"
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "project.created",
                "fix.project",
                rec.id,
                {"name": rec.name, "type": rec.project_type},
            )
        return recs

    def write(self, vals):
        # BRU-PPM-05/07 (M67-4, pj_09): the approved budget is the baseline.
        # Raising it above the baseline after activation is an overrun that
        # needs approval at the new band — not a field edit.
        if "budget" in vals and not self._fix_guard_open():
            for rec in self:
                if rec.baseline_budget and (vals["budget"] or 0.0) > rec.baseline_budget + 0.005:
                    raise UserError(
                        "The budget of %s was baselined at BDT %.2f when it was approved "
                        "and activated. Raising it above the baseline is an overrun that "
                        "needs a new approval: lower it back, or raise a new approval for "
                        "the new amount." % (rec.display_name, rec.baseline_budget)
                    )
        return super().write(vals)

    # ---- lifecycle (M67-5: every transition checks its from-state) --------
    def _gate_entry_ready(self):
        """A failed gate blocks delivery; a recorded G1 must have passed."""
        self.ensure_one()
        failed = self.gate_ids.filtered(lambda g: g.decision == "fail")
        if failed:
            raise UserError(
                "Gate %s of this project closed as FAIL: a failed stage gate "
                "blocks the next phase (BRU-PPM-16)." % ", ".join(failed.mapped("name"))
            )
        g1 = self.gate_ids.filtered(lambda g: g.gate == "g1_initiation")
        open_g1 = g1.filtered(
            lambda g: g.state != "closed" or g.decision not in ("pass", "conditional")
        )
        if g1 and open_g1:
            raise UserError(
                "Gate G1 (Initiation) is not closed with a pass/conditional pass: "
                "activate the project after its initiation gate (BRU-PPM-03)."
            )
        return True

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft project's budget can be sent for approval.")
        return super().action_request_approval(justification=justification)

    def action_activate(self):
        """Delivery starts only with an approved budget and a passing gate."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft project can be activated.")
            rec._dofa_assert_approved("Activation of project %s" % rec.display_name)
            rec._gate_entry_ready()
            rec._guarded().write(
                {
                    "state": "active",
                    "baseline_budget": rec.budget,
                    "date_start": rec.date_start or fields.Date.context_today(rec),
                }
            )
            rec.message_post(
                body="Project activated. Budget baselined at BDT %.2f under %s."
                % (rec.baseline_budget, rec.dofa_approved_tier or "no DOFA tier")
            )

    def action_hold(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active project can be put on hold.")
            rec._guarded().write({"state": "on_hold"})

    def action_resume(self):
        for rec in self:
            if rec.state != "on_hold":
                raise UserError("Only a project on hold can be resumed.")
            rec._guarded().write({"state": "active"})

    def action_cancel(self):
        for rec in self:
            if rec.state in ("completed", "cancelled"):
                raise UserError("This project is already %s." % rec.state)
            rec._guarded().write({"state": "cancelled"})

    def action_complete(self):
        """A project with open milestones or unraised billing does NOT close."""
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active project can be completed.")
            open_ms = rec.milestone_ids.filtered(lambda m: m.state != "done")
            if open_ms:
                raise UserError("%d milestone(s) still open" % len(open_ms))
            unbilled = rec.billing_ids.filtered(lambda b: b.state in ("planned", "ready"))
            if unbilled:
                raise UserError(
                    "%d billing line(s) are not invoiced yet: raise or cancel them "
                    "before closing the project (BRU-PPM-13)." % len(unbilled)
                )
            rec._guarded().write({"state": "completed"})
            publish(self.env, "project.completed", "fix.project", rec.id, {"name": rec.name})

    # ---- event consumers (A12 P2 hand-offs; FF-48) -------------------------
    # Registered in data/fix_a12_event_consumers.xml. The relay calls them as
    # superuser with the event dict; they must stay idempotent.
    @api.model
    def consume_project_created(self, event):
        """project.created: keep the project's own trail of its hand-off."""
        project = self.browse(event.get("aggregate_id") or 0).exists()
        if project:
            project.message_post(
                body="Project creation handed to downstream consumers (event %s)."
                % event.get("event_id")
            )
        return True

    @api.model
    def consume_project_completed(self, event):
        """project.completed: record the closure hand-off on the project."""
        project = self.browse(event.get("aggregate_id") or 0).exists()
        if project:
            project.message_post(
                body="Project closure handed to downstream consumers (event %s)."
                % event.get("event_id")
            )
        return True


class FixProjectMilestone(models.Model):
    _name = "fix.project.milestone"
    _description = "Project Milestone"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    project_id = fields.Many2one("fix.project", required=True, ondelete="cascade")
    due_date = fields.Date()
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done")], default="pending", required=True, tracking=True
    )
    overdue = fields.Boolean(
        readonly=True,
        copy=False,
        help="Set by the overdue-milestone cron (M67-11/R3): a pending milestone "
        "past its due date.",
    )
    accepted_by_id = fields.Many2one(
        "res.users", string="Accepted By", readonly=True, copy=False, tracking=True
    )
    accepted_on = fields.Datetime(string="Accepted On", readonly=True, copy=False)
    acceptance_note = fields.Char(
        string="Acceptance Evidence",
        copy=False,
        help="BRU-PPM-11: the evidence reference (client sign-off, UAT report) "
        "for the milestone's acceptance.",
    )
    task_ids = fields.One2many("fix.project.task", "milestone_id", string="Milestone Tasks")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "overdue",
            "accepted_by_id",
            "accepted_on",
        }

    def action_accept(self, acceptance_note=None):
        """The sponsor (never the PM) accepts the delivered milestone."""
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending milestone can be accepted.")
            if not (acceptance_note or "").strip():
                raise UserError("Record the acceptance evidence (sign-off reference).")
            if not self.env.su:
                manager_user = rec.project_id.manager_id.sudo().user_id
                if manager_user and manager_user == self.env.user:
                    raise UserError(
                        "Segregation of duties: the project manager cannot accept "
                        "their own milestone (BRU-PPM-11). The sponsor or the client "
                        "records the acceptance."
                    )
            rec._guarded().write(
                {
                    "accepted_by_id": self.env.user.id,
                    "accepted_on": fields.Datetime.now(),
                    "acceptance_note": acceptance_note,
                }
            )
            rec.message_post(
                body="Milestone accepted by %s (evidence: %s)."
                % (self.env.user.name, acceptance_note)
            )

    def action_complete(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("This milestone is already %s." % rec.state)
            if not rec.accepted_by_id:
                raise UserError(
                    "The milestone has no recorded acceptance: the sponsor accepts the "
                    "delivered milestone before it completes (BRU-PPM-11)."
                )
            open_tasks = rec.task_ids.filtered(lambda t: t.state not in ("done", "cancelled"))
            if open_tasks:
                raise UserError("%d task(s) still open in milestone" % len(open_tasks))
            rec._guarded().write({"state": "done"})
            publish(
                self.env,
                "project.milestone_completed",
                "fix.project.milestone",
                rec.id,
                {"milestone": rec.name, "project": rec.project_id.name},
            )

    @api.model
    def cron_flag_overdue_milestones(self):
        """R3/M67-11: flag pending milestones past their due date."""
        today = fields.Date.context_today(self)
        overdue = self.sudo().search(
            [("state", "=", "pending"), ("overdue", "=", False), ("due_date", "<", today)]
        )
        for milestone in overdue:
            milestone.sudo()._guarded().write({"overdue": True})
            milestone.message_post(
                body="Milestone is past its due date %s and still pending." % milestone.due_date
            )
        return True

    @api.model
    def consume_project_milestone_completed(self, event):
        """project.milestone_completed: progress becomes the computed ratio of
        completed milestones (M67-7: computed, not typed)."""
        milestone = self.browse(event.get("aggregate_id") or 0).exists()
        if not milestone or milestone.state != "done":
            return True
        project = milestone.project_id
        total = len(project.milestone_ids)
        done = len(project.milestone_ids.filtered(lambda m: m.state == "done"))
        project.sudo().write({"progress_pct": round(100.0 * done / total, 2) if total else 0.0})
        return True


class FixProjectTask(models.Model):
    _name = "fix.project.task"
    _description = "Project Task"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id asc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    project_id = fields.Many2one("fix.project", required=True, ondelete="cascade")
    milestone_id = fields.Many2one("fix.project.milestone", string="Milestone", ondelete="set null")
    assigned_to = fields.Many2one("hr.employee", string="Assigned To")
    planned_hours = fields.Float(string="Planned Hours", default=0.0)
    actual_hours = fields.Float(string="Actual Hours", default=0.0)
    state = fields.Selection(
        [
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="todo",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    @api.constrains("project_id", "milestone_id")
    def _check_milestone_project(self):
        # M67-6 (ms_05): a task of project A may not link to project B's
        # milestone — the milestone gate would count another project's work.
        for task in self:
            if task.milestone_id and task.milestone_id.project_id != task.project_id:
                raise ValidationError(
                    "The milestone %s belongs to another project: a task may only "
                    "link to a milestone of its own project." % task.milestone_id.display_name
                )

    def action_start(self):
        for rec in self:
            if rec.state != "todo":
                raise UserError("Only a to-do task can be started.")
            rec._guarded().write({"state": "in_progress"})

    def action_done(self):
        for rec in self:
            if rec.state not in ("todo", "in_progress"):
                raise UserError("A %s task cannot be marked done." % rec.state)
            rec._guarded().write({"state": "done"})

    def action_cancel(self):
        for rec in self:
            if rec.state in ("done", "cancelled"):
                raise UserError("This task is already %s." % rec.state)
            rec._guarded().write({"state": "cancelled"})
