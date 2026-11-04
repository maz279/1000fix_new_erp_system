# fix_workflow_ops — M63: workflow instances, unified task inbox, business
# rules and approval substitution/OOO. The automation register (fix.automation)
# and the DoA matrix (fix.approval.matrix) live in fix_workflow_engine.py.
#
# A11 audit (2026-11-04) E1/E2: every one of these was writable by any
# internal user. A plain user typed a workflow instance "completed" (the
# automation-rate KPI), rewrote a business rule under another user's name,
# and, worst, recorded "Tier 1 holder X is out of office, I am the
# delegate", activated it himself and approved a colleague's concession on
# X's authority. The registers now belong to the DoA Administrator; a
# substitution is the absent approver's own act.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

DOA_ADMIN = "cd_workflow_engine.group_doa_administrator"
HR_MANAGER = "hr.group_hr_manager"
# Which authority a delegate must hold himself (A11 audit E2). Comma-separated
# res.groups xml ids; for every listed group the absent approver holds, the
# delegate must hold it too. The DOFA tiers imply downward, so the default
# means "the same tier or a higher one". A business decision: add a group
# (e.g. sales_team.group_sale_manager) to make its authority delegable only
# to its own holders.
SUBSTITUTION_GROUPS_PARAM = "cd_workflow_engine.substitution_authority_groups"
DEFAULT_SUBSTITUTION_GROUPS = (
    "cd_entity_config.group_dofa_tier_1",
    "cd_entity_config.group_dofa_tier_2",
    "cd_entity_config.group_dofa_tier_3",
    "cd_entity_config.group_dofa_tier_4",
    "cd_entity_config.group_dofa_tier_5",
)


class FixWorkflowInstance(models.Model):
    _name = "fix.workflow.instance"
    _description = "Workflow Instance"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "started_at desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # The automation-rate and STP KPIs count these; a typed "completed"
        # was an automation nobody ran (A11 audit M63-11, E39).
        return super()._fix_guarded_fields() | {"state", "started_at", "finished_at", "escalated"}

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    automation_id = fields.Many2one("fix.automation", string="Definition", index=True)
    res_model = fields.Char(string="Record Model", index=True)
    res_id = fields.Integer(string="Record ID", index=True)
    started_at = fields.Datetime(required=True, default=fields.Datetime.now)
    finished_at = fields.Datetime()
    escalated = fields.Boolean(default=False)
    state = fields.Selection(
        [
            ("running", "Running"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="running",
    )
    log = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.workflow.instance") or "WFI/New"
                )
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Complete a running instance")
            rec._guarded().write({"state": "completed", "finished_at": fields.Datetime.now()})

    def action_fail(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Fail a running instance")
            rec._guarded().write({"state": "failed", "finished_at": fields.Datetime.now()})

    def action_escalate(self):
        for rec in self:
            rec._guarded().write({"escalated": True})


class FixWorkflowTask(models.Model):
    _name = "fix.workflow.task"
    _description = "Unified Task Inbox Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "created_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    instance_id = fields.Many2one("fix.workflow.instance", string="Workflow Instance")
    task_type = fields.Selection(
        [
            ("approval", "Approval"),
            ("review", "Review"),
            ("data_entry", "Data Entry"),
            ("exception", "Exception Handling"),
        ],
        required=True,
        default="approval",
    )
    res_model = fields.Char(string="Record Model")
    res_id = fields.Integer(string="Record ID")
    assigned_to_id = fields.Many2one("hr.employee", string="Assigned To", index=True)
    created_at = fields.Datetime(required=True, default=fields.Datetime.now)
    due_at = fields.Datetime()
    decided_at = fields.Datetime()
    decision = fields.Selection(
        [("approved", "Approved"), ("rejected", "Rejected"), ("returned", "Returned for Info")],
    )
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done"), ("cancelled", "Cancelled")],
        required=True,
        default="pending",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.workflow.task") or "TSK/New"
                )
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Decide a pending task")
            rec.write(
                {"state": "done", "decision": "approved", "decided_at": fields.Datetime.now()}
            )

    def action_reject(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Decide a pending task")
            rec.write(
                {"state": "done", "decision": "rejected", "decided_at": fields.Datetime.now()}
            )


class FixBusinessRule(models.Model):
    _name = "fix.business.rule"
    _description = "Business Rule"
    _inherit = ["fix.guarded.mixin"]
    _order = "code"

    # A change to any of these is a change to the rule: it is stamped with who
    # made it and when; a change to what the rule says also bumps its version.
    _RULE_TERMS = frozenset(
        {
            "code",
            "name",
            "domain_area",
            "rule_type",
            "expression",
            "error_message",
            "automation_id",
            "active",
        }
    )
    _RULE_MEANING = ("expression", "rule_type")

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    domain_area = fields.Char(string="Process Area")
    rule_type = fields.Selection(
        [
            ("validation", "Validation"),
            ("derivation", "Derivation"),
            ("gate", "Gate / Hard Block"),
            ("escalation", "Escalation Trigger"),
        ],
        required=True,
        default="validation",
    )
    expression = fields.Text(string="Rule Expression", required=True)
    error_message = fields.Char(string="Refusal Message")
    automation_id = fields.Many2one("fix.automation", string="Linked Automation")
    active = fields.Boolean(default=True)
    version = fields.Integer(default=1, readonly=True)
    last_changed_by = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True
    )
    last_changed_on = fields.Datetime(default=fields.Datetime.now, readonly=True)

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A business rule code is unique per company"
    )

    def _fix_guarded_fields(self) -> set:
        # A11 audit M63-12 (E37): a plain user rewrote an admin's rule with a
        # forged "last changed by" and no new version. The stamp is set by
        # the change itself, never typed.
        return super()._fix_guarded_fields() | {"version", "last_changed_by", "last_changed_on"}

    def write(self, vals):
        terms = self._RULE_TERMS & set(vals)
        if not terms or self._fix_guard_has_token():
            return super().write(vals)
        before = {rec.id: tuple(rec[f] for f in self._RULE_MEANING) for rec in self}
        result = super().write(vals)
        now = fields.Datetime.now()
        for rec in self:
            stamp = {"last_changed_by": self.env.uid, "last_changed_on": now}
            if tuple(rec[f] for f in self._RULE_MEANING) != before[rec.id]:
                stamp["version"] = rec.version + 1
            rec._guarded().write(stamp)
        return result

    def action_new_version(self):
        self.check_access("write")
        for rec in self:
            rec._guarded().write(
                {
                    "version": rec.version + 1,
                    "last_changed_by": self.env.uid,
                    "last_changed_on": fields.Datetime.now(),
                }
            )


class FixApprovalSubstitution(models.Model):
    """An absent approver's out-of-office delegation (A11 audit E2).

    A delegation hands someone else the absent approver's AUTHORITY: the
    delegate decides "on behalf of" him, and the DOFA check reads the absent
    approver's tier. So it is his act, not anyone's:
      - only the absent approver records it for himself (or a DoA
        Administrator / HR manager does, for an approver who cannot);
      - it starts today or later, and is born a draft;
      - the absent approver or his manager activates it, never the delegate;
      - the delegate must hold the authority he receives (policy:
        SUBSTITUTION_GROUPS_PARAM, default the same DOFA tier or higher);
      - it is re-checked when the delegate decides, and a daily cron expires
        it after its end date, handing its open tasks back.
    """

    _name = "fix.approval.substitution"
    _description = "Approval Substitution / OOO"
    _inherit = ["fix.guarded.mixin"]
    _order = "start_date desc, id desc"

    # Who, for whom and when: fixed once the substitution leaves draft.
    _KEY_FIELDS = frozenset({"absent_approver_id", "delegate_id", "start_date", "end_date"})

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    absent_approver_id = fields.Many2one(
        "hr.employee", string="Absent Approver", required=True, index=True
    )
    delegate_id = fields.Many2one("hr.employee", string="Delegate", required=True)
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True)
    reason = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("expired", "Expired")],
        required=True,
        default="draft",
        readonly=True,
    )
    activated_by_id = fields.Many2one("res.users", string="Activated By", readonly=True, copy=False)
    activated_at = fields.Datetime(string="Activated On", readonly=True, copy=False)
    expired_by_id = fields.Many2one("res.users", string="Expired By", readonly=True, copy=False)

    _dates_ordered = models.Constraint(
        "CHECK (end_date >= start_date)", "Substitution end cannot precede its start"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_by_id",
            "activated_at",
            "expired_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked |= set(self._KEY_FIELDS)
        return locked

    # ---- who may do what ---------------------------------------------------
    @api.model
    def _sub_is_admin(self) -> bool:
        user = self.env.user
        return self.env.su or user.has_group(DOA_ADMIN) or user.has_group(HR_MANAGER)

    def _sub_parties(self):
        """(absent user, his manager's user, delegate user), read as sudo:
        a plain user may not read hr.employee directly."""
        self.ensure_one()
        rec = self.sudo()
        return (
            rec.absent_approver_id.user_id,
            rec.absent_approver_id.parent_id.user_id,
            rec.delegate_id.user_id,
        )

    @api.model
    def _authority_groups(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(SUBSTITUTION_GROUPS_PARAM)
        xmlids = [x.strip() for x in raw.split(",") if x.strip()] if raw else []
        groups = self.env["res.groups"].sudo()
        for xmlid in xmlids or DEFAULT_SUBSTITUTION_GROUPS:
            group = self.env.ref(xmlid, raise_if_not_found=False)
            if group and group._name == "res.groups":
                groups |= group.sudo()
        return groups

    @api.model
    def _delegate_policy_problem(self, absent_user, delegate_user):
        """Why `delegate_user` may not hold `absent_user`'s authority, or ''."""
        if not absent_user:
            return ""  # an approver with no login delegates nothing
        if not delegate_user or not delegate_user.active or delegate_user.share:
            return "The delegate has no active internal user account to decide with."
        if delegate_user == absent_user:
            return "An approver cannot be his own delegate."
        missing = self._authority_groups().filtered(
            lambda g: absent_user in g.all_user_ids and delegate_user not in g.all_user_ids
        )
        if missing:
            return (
                "%s cannot act for %s: the delegate must hold the authority he receives "
                "(%s). Choose a delegate at the same approval tier or above."
                % (delegate_user.name, absent_user.name, ", ".join(missing.mapped("name")))
            )
        return ""

    # ---- create / write ----------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        today = fields.Date.context_today(self)
        if not self.env.su:
            admin = self._sub_is_admin()
            Employee = self.env["hr.employee"].sudo()
            for vals in vals_list:
                absent = Employee.browse(vals.get("absent_approver_id") or 0).exists()
                if not admin and (not absent.user_id or absent.user_id != self.env.user):
                    raise UserError(
                        "Only the absent approver records his own out-of-office "
                        "substitution (or a DoA Administrator / HR manager, for an "
                        "approver who cannot). You cannot delegate %s's authority."
                        % (absent.name or "another approver")
                    )
                start = fields.Date.to_date(vals.get("start_date")) or today
                if start < today:
                    raise UserError(
                        "A substitution starts today or later; it cannot be back-dated "
                        "to %s." % start
                    )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.approval.substitution")
                    or "SUB/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self.env.su and not self._fix_guard_has_token():
            admin = self._sub_is_admin()
            key = self._KEY_FIELDS & set(vals)
            for rec in self:
                absent, _manager, _delegate = rec._sub_parties()
                if not admin and (not absent or absent != self.env.user):
                    raise UserError(
                        "Only the absent approver (or a DoA Administrator / HR manager) "
                        "changes substitution %s." % rec.name
                    )
                changed = [n for n in key if rec._fix_guard_differs(n, vals[n], rec[n])]
                if rec.state != "draft" and changed:
                    raise UserError(
                        "Substitution %s is %s: who, for whom and when are fixed. Expire "
                        "it and record a new one." % (rec.name, rec.state)
                    )
                if "start_date" in changed:
                    start = fields.Date.to_date(vals["start_date"])
                    if start and start < fields.Date.context_today(self):
                        raise UserError("A substitution cannot be back-dated to %s." % start)
        return super().write(vals)

    @api.constrains("absent_approver_id", "delegate_id", "state")
    def _check_delegate(self):
        for rec in self:
            absent, _manager, delegate = rec._sub_parties()
            if rec.absent_approver_id == rec.delegate_id or (absent and absent == delegate):
                raise ValidationError("An approver cannot be his own delegate.")
            if rec.state == "active":
                problem = self._delegate_policy_problem(absent, delegate)
                if problem:
                    raise ValidationError(problem)

    # ---- transitions -------------------------------------------------------
    def action_activate(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Activate a draft substitution")
            absent, manager, delegate = rec._sub_parties()
            if not self.env.su:
                if not (absent | manager) or self.env.user not in (absent | manager):
                    raise UserError(
                        "Substitution %s is activated by the absent approver (%s) or his "
                        "manager, not by %s." % (rec.name, absent.name or "-", self.env.user.name)
                    )
                if self.env.user == delegate:
                    raise UserError("The delegate cannot activate his own delegation.")
            if rec.end_date < today:
                raise UserError("Substitution %s already ended on %s." % (rec.name, rec.end_date))
            problem = self._delegate_policy_problem(absent, delegate)
            if problem:
                raise UserError(problem)
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                }
            )

    def action_expire(self):
        for rec in self:
            if rec.state == "expired":
                continue
            if not self._sub_is_admin():
                absent, manager, delegate = rec._sub_parties()
                if self.env.user not in (absent | manager | delegate):
                    raise UserError(
                        "Only the absent approver, his manager, the delegate or a DoA "
                        "Administrator ends substitution %s." % rec.name
                    )
            rec._guarded().write({"state": "expired", "expired_by_id": self.env.uid})
            rec._hand_back_tasks("substitution %s ended" % rec.name)

    def _hand_back_tasks(self, reason):
        """Open inbox tasks routed through this substitution go back to the
        absent approver: the delegate's authority ended with it."""
        Task = self.env["fix.workflow.task"].sudo()
        for rec in self:
            absent, _manager, delegate = rec._sub_parties()
            if not (absent and delegate):
                continue
            tasks = Task.search(
                [
                    ("state", "=", "pending"),
                    ("on_behalf_of_id", "=", absent.id),
                    ("assigned_user_id", "=", delegate.id),
                ]
            )
            for task in tasks:
                task._approval_hand_back(reason)

    # ---- engine queries ----------------------------------------------------
    @api.model
    def _active_delegates(self):
        """{absent user id: delegate user} for today's valid substitutions."""
        today = fields.Date.context_today(self)
        subs = self.sudo().search(
            [("state", "=", "active"), ("start_date", "<=", today), ("end_date", ">=", today)]
        )
        out = {}
        for sub in subs:
            absent, _manager, delegate = sub._sub_parties()
            if absent and not self._delegate_policy_problem(absent, delegate):
                out[absent.id] = delegate
        return out

    @api.model
    def _is_valid_delegation(self, absent_user, delegate_user) -> bool:
        """True when `delegate_user` may decide for `absent_user` today."""
        return self._active_delegates().get(absent_user.id) == delegate_user

    @api.model
    def cron_expire_substitutions(self):
        """Daily: an active substitution past its end date expires, and its
        open tasks go back to the absent approver."""
        today = fields.Date.context_today(self)
        stale = self.sudo().search([("state", "=", "active"), ("end_date", "<", today)])
        stale.action_expire()
        return len(stale)
