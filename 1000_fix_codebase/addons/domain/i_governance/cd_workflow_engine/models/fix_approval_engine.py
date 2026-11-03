# fix_approval_engine — M63 as the single approval workflow (A03 audit R7).
#
# Before this, A03 had three approval idioms: the DOFA mixin (sound rules,
# called directly by whoever pressed the button), bespoke flags, and an M63
# inbox nothing fed. An approval had no request, no named approver, no
# deadline, no delegate and no history; "approved" was whatever the record
# said. This makes an approval a request that the engine routes:
#
#   record.action_request_approval()
#     1. rule      = fix.approval.matrix._match(record)      single DoA register
#     2. approvers = tier group (DOFA ladder on the live amount) or the rule's
#                    group, operating unit first, minus requester and creator
#     3. active fix.approval.substitution -> the delegate decides "on behalf"
#     4. one fix.workflow.task per approver, a mail.activity, an
#        approval.requested event; the record reads approval_state=pending
#   task.action_approve() in the APPROVER's environment
#     -> the record's own approve method runs with the task in context, so the
#        DOFA tier group, segregation of duties and justification still apply
#   cron: overdue -> reminder -> escalation to the next tier -> final action
#
# Every step appends to fix.approval.history, which cannot be edited.
#
# A model opts in by inheriting fix.approvable.mixin. Every fix.dofa.mixin
# model inherits it below, so the 9 DOFA tables get the engine with no change
# of their own. `_approval_routed = True` makes the engine the ONLY way in:
# the record's approve method then refuses unless a task is deciding it.
import statistics
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.models import BaseModel
from odoo.tools.safe_eval import safe_eval

from libs.py.fix_events import publish

TASK_KEY = "fix_approval_task"

APPROVAL_STATES = [
    ("none", "Not Requested"),
    ("pending", "Pending Approval"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("returned", "Returned for Information"),
]

REQUEST_STATES = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("returned", "Returned for Information"),
    ("recalled", "Recalled by Requester"),
    ("voided", "Voided by a Change"),
]

HISTORY_EVENTS = [
    ("requested", "Requested"),
    ("task_approved", "Approved (one approver)"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("returned", "Returned for Information"),
    ("recalled", "Recalled"),
    ("voided", "Voided by a Change"),
    ("reminded", "Reminder Sent"),
    ("escalated", "Escalated"),
    ("expired", "Final Action on Expiry"),
]

TIER_ORDER = ["tier_0", "tier_1", "tier_2", "tier_3", "tier_4", "tier_5"]
TIER_GROUP = {
    "tier_1": "cd_entity_config.group_dofa_tier_1",
    "tier_2": "cd_entity_config.group_dofa_tier_2",
    "tier_3": "cd_entity_config.group_dofa_tier_3",
    "tier_4": "cd_entity_config.group_dofa_tier_4",
    "tier_5": "cd_entity_config.group_dofa_tier_5",
}

# The built-in rule when no matrix row matches: any one holder decides,
# 24-hour SLA, one escalation to the next tier, then the request stays open.
DEFAULT_RULE = {
    "approval_policy": "any",
    "sla_hours": 24,
    "max_escalations": 1,
    "final_action": "keep",
}


class FixApprovalMatrix(models.Model):
    """The DoA register becomes the rule book the engine reads.

    It held six thresholds nothing read. A row now matches a record by model
    or decision domain, an optional condition and its effective dates, and
    says how the approval runs: voting policy, SLA, escalation, final action.
    The DOFA ladder still sets the TIER; a row may name a group instead for
    approvals that carry no amount (registration, merge, content...).
    """

    _inherit = "fix.approval.matrix"
    _order = "res_model, decision_domain, date_from desc, id"

    _domain_threshold_unique = models.Constraint(
        "UNIQUE (decision_domain, currency_id, res_model, date_from)",
        "One rule per decision domain, model, currency and effective date",
    )

    name = fields.Char(string="Rule Name")
    decision_domain = fields.Selection(
        selection_add=[
            ("concession", "Service-Recovery Concession"),
            ("campaign_budget", "Campaign Budget"),
            ("loyalty_adjustment", "Loyalty Point Adjustment"),
            ("loyalty_scheme", "Loyalty Scheme Activation"),
            ("loyalty_release", "Loyalty Fraud-Freeze Release"),
            ("party_registration", "Party Registration"),
            ("party_merge", "Party Merge"),
            ("kyc", "KYC Verification"),
            ("dataset_release", "AI Dataset / Model Release"),
            ("creative", "Campaign Creative Content"),
            ("contract_verification", "Opportunity Contract Verification"),
            ("other", "Other"),
        ],
        ondelete={
            key: "cascade"
            for key in (
                "concession",
                "campaign_budget",
                "loyalty_adjustment",
                "loyalty_scheme",
                "loyalty_release",
                "party_registration",
                "party_merge",
                "kyc",
                "dataset_release",
                "creative",
                "contract_verification",
                "other",
            )
        },
    )
    threshold = fields.Monetary(required=False)
    approver_role = fields.Char(required=False)
    res_model = fields.Char(
        string="Applies to Model",
        index=True,
        help="Technical model name. Empty: the row applies to every model of its decision domain.",
    )
    condition = fields.Char(
        string="Condition",
        help="Optional Odoo domain the record must match, e.g. [('severity', '=', 'critical')]",
    )
    approver_group_id = fields.Many2one(
        "res.groups",
        string="Approver Group",
        help="For approvals with no DOFA amount. A DOFA record's tier group always applies.",
    )
    approval_policy = fields.Selection(
        [("any", "Any one approver"), ("all", "Every approver (unanimous)")],
        default="any",
        required=True,
    )
    sla_hours = fields.Integer(string="SLA (hours)", default=24, required=True)
    max_escalations = fields.Integer(default=1, required=True)
    escalate_to_id = fields.Many2one(
        "res.users",
        string="Escalate To",
        help="Named escalation target. Empty: the next DOFA tier's holders.",
    )
    final_action = fields.Selection(
        [("keep", "Keep pending (flag only)"), ("reject", "Auto-reject")],
        default="keep",
        required=True,
        help="What happens once every escalation has also run out of time",
    )
    date_from = fields.Date(string="Effective From")
    date_to = fields.Date(string="Effective To")
    active = fields.Boolean(default=True)

    @api.model
    def _match(self, record):
        """The rule in force for `record`, or an empty recordset (default rule).

        A row for the record's model beats a row for its decision domain; the
        most recent effective date wins. Rows are versioned by date, not
        edited in place: a new ruling is a new row."""
        today = fields.Date.context_today(self)
        domain_key = getattr(record, "_approval_domain", None)
        rows = self.sudo().search(
            [
                "|",
                ("res_model", "=", record._name),
                "&",
                ("res_model", "=", False),
                ("decision_domain", "=", domain_key or "__none__"),
                "|",
                ("date_from", "=", False),
                ("date_from", "<=", today),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", today),
                ("company_id", "in", (record.env.company | record.env.companies).ids),
            ]
        )
        rows = rows.sorted(
            lambda r: (not r.res_model, -(r.date_from.toordinal() if r.date_from else 0))
        )
        for row in rows:
            if not row.condition:
                return row
            if record.sudo().filtered_domain(safe_eval(row.condition)):
                return row
        return self.browse()

    def action_test_rule(self, res_id=None):
        """Simulation: who WOULD this rule route record `res_id` to? Creates nothing."""
        self.ensure_one()
        if not self.res_model or not res_id:
            raise UserError("Set the rule's model and give a record id to test against.")
        record = self.env[self.res_model].browse(int(res_id)).exists()
        if not record:
            raise UserError("No %s with id %s." % (self.res_model, res_id))
        return record.approval_simulate()


class FixApprovableMixin(models.AbstractModel):
    """A record whose approval is a routed request (M63)."""

    _name = "fix.approvable.mixin"
    _inherit = ["fix.guarded.mixin"]
    _description = "Routed Approval (M63)"

    # Per-model declarations.
    _approval_domain = None  # fix.approval.matrix decision_domain key
    _approval_apply_method = None  # the record's own approve method
    _approval_group = None  # xmlid of the deciding group when there is no DOFA tier
    _approval_routed = False  # True: the approve method only runs from a task

    approval_state = fields.Selection(
        APPROVAL_STATES, string="Approval", default="none", readonly=True, copy=False, index=True
    )
    approval_request_id = fields.Many2one(
        "fix.approval.request", string="Approval Request", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"approval_state", "approval_request_id"}

    # ---- per-model hooks --------------------------------------------------
    def _approval_amount(self) -> float:
        return 0.0

    def _approval_tier(self):
        """The DOFA tier the record needs now, or False when it has none."""
        return False

    def _approval_needed(self) -> bool:
        return True

    def _approval_group_xmlid(self):
        return self._approval_group

    def _approval_apply(self):
        """Run the record's own approve method. Called with the deciding task
        in context and in the approver's environment."""
        if not self._approval_apply_method:
            raise UserError("%s declares no approve method for the engine." % self._description)
        return getattr(self, self._approval_apply_method)()

    def _approval_on_rejected(self, comment):
        """Hook: what a rejection does to the record beyond its approval state."""
        return None

    # ---- the deciding task ------------------------------------------------
    def _approval_task(self):
        task = self.env.context.get(TASK_KEY)
        # An object, never a flag: JSON-RPC cannot put a recordset in context.
        if isinstance(task, BaseModel) and task._name == "fix.workflow.task":
            return task
        return self.env["fix.workflow.task"]

    def _approval_authority_user(self):
        """Whose authority covers this decision: the absent approver when a
        delegate decides on their behalf, otherwise the deciding user."""
        task = self._approval_task()
        return task.on_behalf_of_id or self.env.user

    def _approval_acting_users(self):
        task = self._approval_task()
        return self.env.user | task.on_behalf_of_id

    def _approval_assert_routed(self):
        if not self._approval_routed or self.env.su:
            return
        task = self._approval_task()
        # One task decides one record: it cannot carry a second one through.
        if not task or task.res_model != self._name or self.ids != [task.res_id]:
            raise UserError(
                "%s is approved from the approver's inbox, not directly. Use Request "
                "Approval: the approval engine (M63) routes it to someone who holds "
                "the required authority." % self._description
            )

    # ---- resolution -------------------------------------------------------
    def _approval_rule(self):
        return self.env["fix.approval.matrix"]._match(self)

    def _approval_rule_value(self, rule, key):
        return rule[key] if rule else DEFAULT_RULE[key]

    def _approval_group_for(self, rule, tier):
        if rule.approver_group_id:
            return rule.approver_group_id
        xmlid = TIER_GROUP.get(tier) if tier else self._approval_group_xmlid()
        return self.env.ref(xmlid, raise_if_not_found=False) if xmlid else None

    def _approval_excluded(self):
        """Requester and creator never decide their own record."""
        self.ensure_one()
        return (self.env.user | self.create_uid).sudo()

    def _approval_holders(self, group):
        self.ensure_one()
        if not group:
            return self.env["res.users"]
        company = (
            self.company_id
            if "company_id" in self._fields and self.company_id
            else self.env.company
        )
        users = group.sudo().all_user_ids.filtered(
            lambda u: u.active and not u.share and company in u.company_ids
        )
        ou = self.operating_unit_id if "operating_unit_id" in self._fields else None
        if ou and "operating_unit_ids" in users._fields:
            # The record's own unit first; if no holder sits there, the company's.
            local = users.filtered(lambda u: ou in u.operating_unit_ids)
            users = local or users
        return users - self._approval_excluded()

    def _approval_substitutes(self, users):
        """[(assignee, on_behalf_of or None)] after today's active substitutions."""
        today = fields.Date.context_today(self)
        subs = (
            self.env["fix.approval.substitution"]
            .sudo()
            .search(
                [
                    ("state", "=", "active"),
                    ("start_date", "<=", today),
                    ("end_date", ">=", today),
                ]
            )
        )
        delegate_of = {}
        for sub in subs:
            absent = sub.absent_approver_id.user_id
            delegate = sub.delegate_id.user_id
            if absent and delegate and delegate.active:
                delegate_of[absent.id] = delegate
        excluded = self._approval_excluded()
        out, seen = [], set()
        for user in users:
            delegate = delegate_of.get(user.id)
            pair = (delegate, user) if delegate and delegate not in excluded else (user, None)
            if pair[0].id not in seen:
                seen.add(pair[0].id)
                out.append(pair)
        return out

    def _approval_lowest_competent(self, users, tier):
        """Tier groups imply the tiers below, so a Tier 2 group's users include
        every director and the MD. Route to the people whose authority is this
        tier, not above it; only if there are none does it go higher. The next
        level is what escalation is for."""
        if tier not in TIER_ORDER or tier == "tier_5":
            return users
        above = self.env.ref(
            TIER_GROUP[TIER_ORDER[TIER_ORDER.index(tier) + 1]], raise_if_not_found=False
        )
        exact = users - above.sudo().all_user_ids if above else users
        return exact or users

    def _approval_resolve(self, rule, tier):
        users = self._approval_holders(self._approval_group_for(rule, tier))
        if tier and not rule.approver_group_id:
            users = self._approval_lowest_competent(users, tier)
        return self._approval_substitutes(users)

    def approval_simulate(self):
        """Who a request would go to now, without creating anything."""
        self.ensure_one()
        rule = self._approval_rule()
        tier = self._approval_tier()
        return {
            "rule": rule.display_name if rule else "(default rule)",
            "tier": tier or None,
            "needed": bool(self._approval_needed()),
            "approvers": [
                "%s (on behalf of %s)" % (u.name, b.name) if b else u.name
                for u, b in self._approval_resolve(rule, tier)
            ],
        }

    # ---- requester actions ------------------------------------------------
    def action_request_approval(self, justification=None):
        """Route this record to the people who may approve it."""
        Request = self.env["fix.approval.request"].sudo()
        for rec in self:
            if rec.approval_state == "pending":
                raise UserError("%s is already awaiting approval." % rec.display_name)
            if not rec._approval_needed():
                raise UserError("Nothing to approve: %s needs no approval." % rec.display_name)
            if justification and "dofa_justification" in rec._fields:
                rec.write({"dofa_justification": justification})
            rule = rec._approval_rule()
            tier = rec._approval_tier()
            approvers = rec._approval_resolve(rule, tier)
            if not approvers:
                raise UserError(
                    "No one can approve %s: nobody other than you and the record's "
                    "creator holds %s. Appoint an approver (DOFA tier membership) first."
                    % (
                        rec.display_name,
                        dict(rec.env["fix.approval.request"]._fields["tier"].selection).get(tier)
                        if tier
                        else "the approving group",
                    )
                )
            req = Request.create(
                {
                    "res_model": rec._name,
                    "res_id": rec.id,
                    "res_name": rec.display_name,
                    "matrix_id": rule.id or False,
                    "decision_domain": rec._approval_domain or False,
                    "tier": tier or False,
                    "amount": rec._approval_amount(),
                    "requested_by_id": rec.env.user.id,
                    "record_creator_id": rec.create_uid.id,
                    "justification": justification or False,
                    "approval_policy": rec._approval_rule_value(rule, "approval_policy"),
                    "company_id": (rec.company_id.id if "company_id" in rec._fields else False)
                    or rec.env.company.id,
                }
            )
            req._open_tasks(approvers)
            rec._guarded().write({"approval_state": "pending", "approval_request_id": req.id})
            req._log("requested", comment=justification)
            publish(
                rec.env,
                "approval.requested",
                rec._name,
                rec.id,
                {
                    "request": req.name,
                    "tier": tier or None,
                    "amount": req.amount,
                    "approver_ids": [u.id for u, _b in approvers],
                },
            )
            if hasattr(rec, "message_post"):
                rec.message_post(
                    body="Approval requested (%s); routed to %s."
                    % (req.name, ", ".join(u.name for u, _b in approvers))
                )
        return True

    def action_recall_approval(self):
        """The requester withdraws a pending request."""
        for rec in self:
            req = rec.approval_request_id
            if rec.approval_state != "pending" or not req or req.state != "pending":
                raise UserError("Only a pending approval request can be recalled.")
            if req.requested_by_id != rec.env.user and not rec.env.su:
                raise UserError("Only the person who requested the approval can recall it.")
            req._finish("recalled", "recalled", rec.env.user, record_state="none")
        return True

    def _approval_void(self, reason):
        """A change the approval did not cover: withdraw it, keep the trail."""
        for rec in self.filtered(lambda r: r.approval_state in ("pending", "approved")):
            req = rec.approval_request_id.sudo()
            if req and req.state == "pending":
                req._finish("voided", "voided", rec.env.user, comment=reason, record_state="none")
            else:
                rec._guarded().write({"approval_state": "none"})
                if req:
                    req._log("voided", comment=reason)

    def write(self, vals):
        pending = self.filtered(lambda r: r.approval_state == "pending")
        before = {rec.id: rec._approval_amount() for rec in pending}
        result = super().write(vals)
        for rec in pending:
            if (
                abs(rec._approval_amount() - before[rec.id]) > 0.005
                and rec.approval_state == "pending"
            ):
                rec._approval_void(
                    "the amount changed from %.2f to %.2f while approval was pending; "
                    "request it again." % (before[rec.id], rec._approval_amount())
                )
        return result


class FixDofaMixin(models.AbstractModel):
    """Every DOFA record gets the routed request; the DOFA rules decide it."""

    _name = "fix.dofa.mixin"
    # The approvable mixin goes FIRST: it already sits in front of the guard
    # mixin, and listing it after fix.dofa.mixin (whose bases end with the
    # guard) gives Python no consistent method order.
    _inherit = ["fix.approvable.mixin", "fix.dofa.mixin"]

    _approval_apply_method = "action_dofa_approve"

    def _approval_amount(self) -> float:
        return abs(self._dofa_amount() or 0.0)

    def _approval_tier(self):
        return self._dofa_current_tier()

    def _approval_needed(self) -> bool:
        return self._dofa_current_tier() != "tier_0"

    def _dofa_route_guard(self):
        self._approval_assert_routed()

    def _dofa_authority_user(self):
        return self._approval_authority_user()

    def _dofa_acting_users(self):
        return self._approval_acting_users()

    def _dofa_void_approval(self, reason: str):
        self._approval_void(reason)
        return super()._dofa_void_approval(reason)


class FixApprovalRequest(models.Model):
    """One round of approval for one record."""

    _name = "fix.approval.request"
    _description = "Approval Request"
    _order = "requested_at desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    res_model = fields.Char(string="Record Model", required=True, index=True, readonly=True)
    res_id = fields.Integer(string="Record ID", required=True, index=True, readonly=True)
    res_name = fields.Char(string="Record", readonly=True)
    matrix_id = fields.Many2one("fix.approval.matrix", string="Rule", readonly=True)
    decision_domain = fields.Char(readonly=True)
    tier = fields.Selection(
        [
            ("tier_0", "Tier 0"),
            ("tier_1", "Tier 1 — Team Lead / Supervisor"),
            ("tier_2", "Tier 2 — Branch / Operations Manager"),
            ("tier_3", "Tier 3 — CX / Commercial Director"),
            ("tier_4", "Tier 4 — CFO / CCO / COO"),
            ("tier_5", "Tier 5 — Managing Director / Board"),
        ],
        readonly=True,
    )
    amount = fields.Float(readonly=True)
    requested_by_id = fields.Many2one("res.users", required=True, readonly=True, index=True)
    record_creator_id = fields.Many2one("res.users", readonly=True)
    requested_at = fields.Datetime(required=True, default=fields.Datetime.now, readonly=True)
    justification = fields.Text(readonly=True)
    approval_policy = fields.Selection(
        [("any", "Any one approver"), ("all", "Every approver")], default="any", readonly=True
    )
    state = fields.Selection(
        REQUEST_STATES, default="pending", required=True, index=True, readonly=True
    )
    decided_at = fields.Datetime(readonly=True)
    decided_by_id = fields.Many2one("res.users", readonly=True)
    on_behalf_of_id = fields.Many2one("res.users", readonly=True)
    cycle_hours = fields.Float(string="Cycle Time (h)", readonly=True)
    reminded_at = fields.Datetime(readonly=True)
    escalation_level = fields.Integer(default=0, readonly=True)
    final_action_done = fields.Boolean(readonly=True)
    task_ids = fields.One2many("fix.workflow.task", "request_id", readonly=True)
    history_ids = fields.One2many("fix.approval.history", "request_id", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.approval.request") or "APR/New"
                )
        return super().create(vals_list)

    def unlink(self):
        raise UserError("Approval requests are evidence and cannot be deleted.")

    def _record(self, env=None):
        self.ensure_one()
        return (env or self.env)[self.res_model].browse(self.res_id).exists()

    def _rule_value(self, key):
        return self.matrix_id[key] if self.matrix_id else DEFAULT_RULE[key]

    def _open_tasks(self, approvers, level=0):
        """One inbox task (and to-do activity) per approver."""
        self.ensure_one()
        due = fields.Datetime.now() + timedelta(hours=max(self._rule_value("sla_hours"), 1))
        record = self._record(self.env(su=True))
        Task = self.env["fix.workflow.task"].sudo()._guarded()
        tasks = Task
        for user, behalf in approvers:
            vals = {
                "name": "New",
                "company_id": self.company_id.id,
                "task_type": "approval",
                "request_id": self.id,
                "res_model": self.res_model,
                "res_id": self.res_id,
                "assigned_user_id": user.id,
                "assigned_to_id": user.employee_ids[:1].id or False,
                "on_behalf_of_id": behalf.id if behalf else False,
                "due_at": due,
                "escalation_level": level,
            }
            if record and hasattr(record, "activity_schedule"):
                activity = record.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=due.date(),
                    summary="Approve %s" % self.name,
                    note="%s awaits your decision in the M63 approval inbox." % self.res_name,
                    user_id=user.id,
                )
                vals["activity_id"] = activity.id
            task = Task.create(vals)
            tasks |= task
            if behalf:
                self._log("requested", user=behalf, comment="routed to delegate %s" % user.name)
        return tasks

    def _log(self, event, user=None, task=None, comment=None):
        self.ensure_one()
        return (
            self.env["fix.approval.history"]
            .sudo()
            .create(
                {
                    "request_id": self.id,
                    "res_model": self.res_model,
                    "res_id": self.res_id,
                    "event": event,
                    "user_id": (user or self.env.user).id,
                    "on_behalf_of_id": task.on_behalf_of_id.id if task else False,
                    "tier": self.tier or False,
                    "amount": self.amount,
                    "comment": comment or False,
                }
            )
        )

    def _close_tasks(self, except_task=None):
        for task in self.task_ids.filtered(lambda t: t.state == "pending" and t != except_task):
            task._guarded().write({"state": "cancelled"})
            if task.activity_id:
                task.activity_id.sudo().unlink()

    def _finish(self, state, event, user, task=None, comment=None, record_state=None):
        """Close this request: decide it, cancel open tasks, stamp the record."""
        self.ensure_one()
        now = fields.Datetime.now()
        self.sudo().write(
            {
                "state": state,
                "decided_at": now,
                "decided_by_id": user.id,
                "on_behalf_of_id": task.on_behalf_of_id.id if task else False,
                "cycle_hours": round((now - self.requested_at).total_seconds() / 3600.0, 2),
            }
        )
        self._close_tasks(except_task=task)
        self._log(event, user=user, task=task, comment=comment)
        record = self._record(self.env(su=True))
        if record and record_state and record.approval_request_id == self:
            record._guarded().write({"approval_state": record_state})
        if record and hasattr(record, "message_post"):
            record.message_post(
                body="Approval %s %s by %s%s%s."
                % (
                    self.name,
                    dict(REQUEST_STATES)[state].lower(),
                    user.name,
                    " on behalf of %s" % task.on_behalf_of_id.name
                    if task and task.on_behalf_of_id
                    else "",
                    ": %s" % comment if comment else "",
                )
            )
        publish(
            self.env,
            "approval.decided",
            self.res_model,
            self.res_id,
            {"request": self.name, "state": state, "decided_by": user.id},
        )

    def _task_approved(self, task, comment=None):
        self.ensure_one()
        self._log("task_approved", user=self.env.user, task=task, comment=comment)
        open_tasks = self.task_ids.filtered(lambda t: t.state == "pending" and t != task)
        if self.approval_policy == "all" and open_tasks:
            return
        self._finish(
            "approved",
            "approved",
            self.env.user,
            task=task,
            comment=comment,
            record_state="approved",
        )

    # ---- escalation --------------------------------------------------------
    def _next_tier_holders(self, record):
        target = self.matrix_id.escalate_to_id
        if target:
            return [(target, None)] if target not in record._approval_excluded() else []
        if self.tier not in TIER_ORDER or self.tier == "tier_5":
            return []
        nxt = TIER_ORDER[TIER_ORDER.index(self.tier) + 1]
        group = self.env.ref(TIER_GROUP[nxt], raise_if_not_found=False)
        assigned = self.task_ids.mapped("assigned_user_id") | self.task_ids.mapped(
            "on_behalf_of_id"
        )
        users = record._approval_lowest_competent(record._approval_holders(group), nxt) - assigned
        return record._approval_substitutes(users)

    @api.model
    def cron_escalate_overdue(self):
        """Overdue: remind once, then escalate up to the rule's limit, then
        apply its final action. Wall-clock hours (no working calendar yet)."""
        now = fields.Datetime.now()
        overdue = (
            self.sudo()
            .search([("state", "=", "pending"), ("final_action_done", "=", False)])
            .filtered(
                lambda r: any(
                    t.state == "pending" and t.due_at and t.due_at < now for t in r.task_ids
                )
            )
        )
        for req in overdue:
            record = req._record(self.env(su=True))
            if not record:
                continue
            sla = timedelta(hours=max(req._rule_value("sla_hours"), 1))
            pending_tasks = req.task_ids.filtered(lambda t: t.state == "pending")
            if not req.reminded_at:
                req.write({"reminded_at": now})
                pending_tasks._guarded().write({"due_at": now + sla})
                req._log("reminded", user=self.env.user, comment="approval overdue; reminder sent")
                publish(
                    self.env, "approval.reminder", req.res_model, req.res_id, {"request": req.name}
                )
                continue
            if req.escalation_level < req._rule_value("max_escalations"):
                targets = req._next_tier_holders(record)
                if targets:
                    level = req.escalation_level + 1
                    req.write({"escalation_level": level})
                    req._open_tasks(targets, level=level)
                    pending_tasks._guarded().write({"due_at": now + sla})
                    req._log(
                        "escalated",
                        user=self.env.user,
                        comment="escalated to %s" % ", ".join(u.name for u, _b in targets),
                    )
                    publish(
                        self.env,
                        "approval.escalated",
                        req.res_model,
                        req.res_id,
                        {"request": req.name, "level": level, "to": [u.id for u, _b in targets]},
                    )
                    continue
            req.write({"final_action_done": True})
            if req._rule_value("final_action") == "reject":
                req._finish(
                    "rejected",
                    "expired",
                    self.env.user,
                    comment="auto-rejected: no decision after every escalation",
                    record_state="rejected",
                )
                record._approval_on_rejected("auto-rejected on expiry")
            else:
                req._log(
                    "expired", user=self.env.user, comment="no decision after every escalation"
                )

    # ---- KPIs (R11) --------------------------------------------------------
    @api.model
    def approval_kpis(self):
        reqs = self.sudo().search([])
        now = fields.Datetime.now()
        pending = reqs.filtered(lambda r: r.state == "pending")
        ages = [(now - r.requested_at).total_seconds() / 3600.0 for r in pending]
        approved = reqs.filtered(lambda r: r.state == "approved")
        history = self.env["fix.approval.history"].sudo().search([])
        decided = reqs.filtered(lambda r: r.cycle_hours and r.state in ("approved", "rejected"))
        by_tier = {}
        for r in approved:
            by_tier[r.tier or "none"] = by_tier.get(r.tier or "none", 0) + 1
        return {
            "pending": len(pending),
            "pending_under_24h": sum(1 for a in ages if a < 24),
            "pending_24_72h": sum(1 for a in ages if 24 <= a < 72),
            "pending_over_72h": sum(1 for a in ages if a >= 72),
            "approved_by_tier": by_tier,
            # Should always be 0: the engine never routes to the creator.
            "approver_is_creator": len(
                approved.filtered(
                    lambda r: r.decided_by_id and r.decided_by_id == r.record_creator_id
                )
            ),
            "voided_by_change": len(history.filtered(lambda h: h.event == "voided")),
            "escalations": len(history.filtered(lambda h: h.event == "escalated")),
            "median_cycle_hours": round(statistics.median(decided.mapped("cycle_hours")), 2)
            if decided
            else 0.0,
        }


class FixApprovalHistory(models.Model):
    """Append-only trail: who did what to an approval, when, for whom."""

    _name = "fix.approval.history"
    _description = "Approval History"
    _order = "at desc, id desc"

    request_id = fields.Many2one(
        "fix.approval.request", required=True, index=True, ondelete="restrict", readonly=True
    )
    res_model = fields.Char(required=True, index=True, readonly=True)
    res_id = fields.Integer(required=True, index=True, readonly=True)
    event = fields.Selection(HISTORY_EVENTS, required=True, readonly=True)
    user_id = fields.Many2one("res.users", required=True, readonly=True)
    on_behalf_of_id = fields.Many2one("res.users", string="On Behalf Of", readonly=True)
    tier = fields.Char(readonly=True)
    amount = fields.Float(readonly=True)
    comment = fields.Text(readonly=True)
    at = fields.Datetime(required=True, default=fields.Datetime.now, readonly=True)

    def write(self, vals):
        raise UserError("Approval history is append-only and cannot be edited.")

    def unlink(self):
        raise UserError("Approval history is append-only and cannot be deleted.")


class FixWorkflowTask(models.Model):
    """The inbox task becomes the only place a routed approval is decided."""

    _name = "fix.workflow.task"
    _inherit = ["fix.workflow.task", "fix.guarded.mixin"]

    request_id = fields.Many2one(
        "fix.approval.request",
        string="Approval Request",
        index=True,
        ondelete="cascade",
        readonly=True,
    )
    assigned_user_id = fields.Many2one("res.users", string="Approver", index=True, readonly=True)
    on_behalf_of_id = fields.Many2one("res.users", string="On Behalf Of", readonly=True)
    activity_id = fields.Many2one("mail.activity", readonly=True, ondelete="set null")
    escalation_level = fields.Integer(default=0, readonly=True)
    comment = fields.Text(string="Decision Comment", readonly=True)
    res_name = fields.Char(related="request_id.res_name", string="Record")
    amount = fields.Float(related="request_id.amount")
    tier = fields.Selection(related="request_id.tier")
    requested_by_id = fields.Many2one(related="request_id.requested_by_id")
    is_mine = fields.Boolean(compute="_compute_is_mine", search="_search_is_mine")

    def _fix_guarded_fields(self) -> set:
        # A task that could be created, reassigned or marked done by hand
        # would be an approval anyone can type (A03 audit, M63 row).
        return super()._fix_guarded_fields() | {
            "state",
            "decision",
            "decided_at",
            "request_id",
            "assigned_user_id",
            "on_behalf_of_id",
            "res_model",
            "res_id",
            "due_at",
            "escalation_level",
            "comment",
        }

    def _compute_is_mine(self):
        for task in self:
            task.is_mine = task.assigned_user_id == self.env.user or (
                not task.assigned_user_id and task.assigned_to_id.user_id == self.env.user
            )

    def _search_is_mine(self, operator, value):
        mine = (operator in ("=", "==") and value) or (operator in ("!=", "<>") and not value)
        dom = [
            "|",
            ("assigned_user_id", "=", self.env.uid),
            "&",
            ("assigned_user_id", "=", False),
            ("assigned_to_id.user_id", "=", self.env.uid),
        ]
        return dom if mine else ["!", *dom]

    def _decide_check(self):
        self.ensure_one()
        if self.state != "pending":
            raise UserError("Decide a pending task")
        assignee = self.assigned_user_id or self.assigned_to_id.user_id
        if assignee != self.env.user:
            raise UserError(
                "This task is assigned to %s. Only the assignee decides it."
                % (assignee.name or "nobody")
            )
        if self.request_id and self.request_id.state != "pending":
            raise UserError("The approval request is no longer pending.")

    def _decide(self, decision, comment):
        self._guarded().write(
            {
                "state": "done",
                "decision": decision,
                "decided_at": fields.Datetime.now(),
                "comment": comment or False,
            }
        )
        if self.activity_id:
            self.activity_id.sudo().unlink()

    def action_approve(self, comment=None):
        for task in self:
            task._decide_check()
            req = task.request_id.sudo()
            if req:
                record = req._record()
                if not record:
                    raise UserError("The record this approval was for no longer exists.")
                # The record's own approve method, in the approver's env, with
                # the task in context: DOFA tier, SoD and justification apply.
                record.with_context(**{TASK_KEY: task})._approval_apply()
            task._decide("approved", comment)
            if req:
                req.with_user(self.env.user)._task_approved(task, comment)
        return True

    def action_reject(self, comment=None):
        for task in self:
            task._decide_check()
            req = task.request_id.sudo()
            if req and not (comment or "").strip():
                raise UserError("State why this approval is rejected.")
            task._decide("rejected", comment)
            if req:
                req.with_user(self.env.user)._finish(
                    "rejected",
                    "rejected",
                    self.env.user,
                    task=task,
                    comment=comment,
                    record_state="rejected",
                )
                record = req._record()
                if record:
                    record.with_context(**{TASK_KEY: task})._approval_on_rejected(comment)
        return True

    def action_return(self, comment=None):
        """Send it back to the requester for more information."""
        for task in self:
            task._decide_check()
            if not task.request_id:
                raise UserError("Only a routed approval can be returned for information.")
            if not (comment or "").strip():
                raise UserError("Say what information is needed.")
            task._decide("returned", comment)
            task.request_id.sudo().with_user(self.env.user)._finish(
                "returned",
                "returned",
                self.env.user,
                task=task,
                comment=comment,
                record_state="returned",
            )
        return True
