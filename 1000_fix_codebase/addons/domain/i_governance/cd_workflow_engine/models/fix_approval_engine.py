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
import logging
import statistics
from datetime import datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.models import BaseModel
from odoo.tools.safe_eval import safe_eval
from psycopg2.extensions import TransactionRollbackError

from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)

TASK_KEY = "fix_approval_task"

# The recorded interventions on a request belong to the DoA Administrator
# (A11 audit F09), like every other governance act in this module.
DOA_ADMIN = "cd_workflow_engine.group_doa_administrator"

# Company-wide default working calendar for approval SLAs (A03 audit R7, W2):
# the id of a fix.working.calendar. Used when neither the matrix row nor the
# record's branch names one; unset means wall-clock hours, today's behaviour.
CALENDAR_PARAM = "cd_workflow_engine.approval_calendar_id"
# fix.working.calendar.line.weekday keys, in date.weekday() order.
WEEKDAY_KEYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
# The walk gives up after this many days. A calendar whose every day is a
# holiday (or whose lines hold no time) would otherwise never end.
MAX_CALENDAR_DAYS = 400
# Writes of only these fields cannot move the amount at risk, so the mixin's
# write() does not re-read it (they are the engine's own bookkeeping).
_APPROVAL_BOOKKEEPING = frozenset(
    {"approval_state", "approval_request_id", "approval_amount_changed_by_id"}
)

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
    ("handed_back", "Handed Back by an Ended Delegation"),
    # A11 audit F09: a request whose tasks were lost says so when the cron
    # re-derives its approvers, instead of quietly counting as pending forever.
    ("requeued", "Re-Queued (Tasks Were Lost)"),
]

# A11 audit E4 (M63-6): an approval covers WHO is paid, in WHICH currency and
# WHAT kind of concession, as much as how much. After a BDT 800 refund to the
# customer was approved, the clerk re-pointed it to another partner and
# re-typed it a discount; the approval stood. Whichever of these a model
# stores is pinned by default (_approval_pinned_fields); a model adds its own.
APPROVAL_PINNED_DEFAULT = (
    "partner_id",
    "customer_id",
    "vendor_id",
    "supplier_id",
    "payee_id",
    "beneficiary_id",
    "counterparty_id",
    "currency_id",
    "concession_type",
)


class _VoteDryRun(Exception):
    """Rolls back the savepoint of a vote's dry run (_approval_check_vote)."""


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
        ondelete=dict.fromkeys(
            (
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
            ),
            "cascade",
        ),
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
    calendar_id = fields.Many2one(
        "fix.working.calendar",
        string="Working Calendar",
        help="The SLA counts working hours on this calendar (A03 audit R7). Empty: "
        "the record's branch calendar, then the company default "
        "(cd_workflow_engine.approval_calendar_id), then wall-clock hours.",
    )
    date_from = fields.Date(string="Effective From")
    date_to = fields.Date(string="Effective To")
    active = fields.Boolean(default=True)
    # ---- dead-rule visibility (A11 audit F05, flag only) --------------------
    # Three of the live estate's six rows (`write_off`, `estimate`, `expense`,
    # all with no res_model) can never match a record: _match pairs such a row
    # with records whose _approval_domain equals its decision_domain, and no
    # model declares those keys (their real keys are ar_writeoff,
    # inventory_writeoff, estimate_discount...). The rows are NOT changed and
    # _match is NOT changed — re-pointing a dormant row would change live
    # approval routing, which is an owner decision. These two fields just make
    # the dead rows say so on the rule book itself.
    matches_any_model = fields.Boolean(
        string="Can Match a Record",
        compute="_compute_matches_any_model",
        help="False when no document model can ever reach this rule: it never "
        "governed anything and never will until an owner re-points it.",
    )
    rule_note = fields.Char(
        string="Rule Note",
        compute="_compute_matches_any_model",
        help="Why this rule can never match, in one sentence.",
    )

    @api.depends("res_model", "decision_domain")
    def _compute_matches_any_model(self):
        # One registry pass serves every row: which decision domains some
        # non-abstract model actually declares.
        declared = {}
        for name, model in self.env.registry.items():
            if model._abstract or model._transient:
                continue  # a wizard is not a document anyone routes
            key = getattr(model, "_approval_domain", None)
            if key and key not in declared:
                declared[key] = name
        for row in self:
            if row.res_model:
                if row.res_model in self.env:
                    row.matches_any_model, row.rule_note = True, False
                else:
                    row.matches_any_model = False
                    row.rule_note = (
                        "The rule names model %r, which does not exist on this "
                        "database — it can never match." % row.res_model
                    )
            elif declared.get(row.decision_domain):
                row.matches_any_model, row.rule_note = True, False
            else:
                row.matches_any_model = False
                row.rule_note = (
                    "No document model declares the decision domain %r — this "
                    "rule can never match." % row.decision_domain
                )

    # ---- validation on save (A11 audit E1, M63-7) ---------------------------
    # A malformed condition crashed every request of its domain with a
    # SyntaxError, and a row pointed at an empty group left every record of
    # the domain with "No one can approve". Both are refused when saved.
    def _condition_models(self):
        """The models a row's condition is evaluated against."""
        self.ensure_one()
        if self.res_model:
            return [self.res_model] if self.res_model in self.env else []
        return [
            name
            for name, model in self.env.registry.items()
            if not model._abstract
            and not model._transient
            and getattr(model, "_approval_domain", None) == self.decision_domain
        ]

    def _parse_condition(self, record=None):
        """The row's condition as a domain; ValueError when it is not one."""
        self.ensure_one()
        try:
            domain = safe_eval(self.condition)
        except Exception as exc:  # any parse failure is a bad rule
            raise ValueError("it is not a valid domain (%s)" % exc) from exc
        if not isinstance(domain, list | tuple):
            raise ValueError("it must be a list such as [('severity', '=', 'critical')]")
        return list(domain)

    @api.constrains("condition", "res_model", "decision_domain")
    def _check_condition(self):
        for row in self.filtered("condition"):
            try:
                domain = row._parse_condition()
                for name in row._condition_models():
                    Model = self.env[name].sudo().with_context(active_test=False)
                    # Field names and operators are checked by building the
                    # query; a real row (if any) is evaluated in memory too.
                    Model.search_count(domain, limit=1)
                    Model.search([], limit=1).filtered_domain(domain)
            except ValueError as exc:
                raise ValidationError(
                    "Approval rule %s: the condition %r is refused: %s."
                    % (row.display_name, row.condition, exc)
                ) from exc
            except Exception as exc:
                raise ValidationError(
                    "Approval rule %s: the condition %r does not apply to the records it "
                    "targets (%s: %s)." % (row.display_name, row.condition, type(exc).__name__, exc)
                ) from exc

    @api.constrains("approver_group_id", "active")
    def _check_approver_group_holders(self):
        for row in self.filtered(lambda r: r.active and r.approver_group_id):
            holders = row.approver_group_id.sudo().all_user_ids.filtered(
                lambda u: u.active and not u.share
            )
            if not holders:
                raise ValidationError(
                    "Approval rule %s names %s as its approver group, which nobody "
                    "holds: every record it matches could not be approved. Appoint "
                    "the group's members first." % (row.display_name, row.approver_group_id.name)
                )

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
            try:
                hit = record.sudo().filtered_domain(row._parse_condition())
            except Exception as exc:  # a legacy row saved before validation
                _logger.warning("Approval rule %s has an invalid condition: %s", row.id, exc)
                raise UserError(
                    "Approval rule %s has an invalid condition (%r), so %s cannot be "
                    "routed. A DoA Administrator must correct the rule."
                    % (row.display_name, row.condition, record.display_name)
                ) from exc
            if hit:
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

    # ---- versioning (A11 audit G9, M63-8) -----------------------------------
    #
    # A dated row that has come into force is a FACT about the decisions
    # already routed under it — requests pin the row that governed them
    # (fix.approval.request.matrix_id), so what it said when it said it must
    # stay readable and provable. It is never edited in place: a new ruling
    # is a NEW row (action_new_version closes the current one and opens the
    # next). Only closing (date_to) and archiving remain writable on a row in
    # force — that is how a version is retired, and it rewrites nothing.
    _RULE_CONTENT_FIELDS = frozenset(
        {
            "res_model",
            "decision_domain",
            "threshold",
            "approver_role",
            "condition",
            "approver_group_id",
            "approval_policy",
            "sla_hours",
            "max_escalations",
            "escalate_to_id",
            "final_action",
            "calendar_id",
            "date_from",
        }
    )

    def write(self, vals):
        if not self.env.context.get("matrix_version_engine"):
            today = fields.Date.context_today(self)
            for row in self:
                if not row.date_from or row.date_from > today:
                    continue  # not yet in force: still a draft of a ruling
                touched = self._RULE_CONTENT_FIELDS & set(vals)
                if touched:
                    raise UserError(
                        "Rule %s has been in force since %s and is never edited "
                        "in place — %s would change what it ruled, and requests "
                        "already decided under it point back here. Use New "
                        "Version: the row is closed and a new one takes effect "
                        "from tomorrow (M63 G9)."
                        % (row.display_name, row.date_from, ", ".join(sorted(touched)))
                    )
        return super().write(vals)

    def action_new_version(self):
        """Close every selected row at today and open its successor from
        tomorrow. The successor is a copy the DoA Administrator edits freely —
        it is not in force until its date arrives, so the guard above does not
        apply to it."""
        today = fields.Date.context_today(self)
        tomorrow = today + timedelta(days=1)
        new_rows = self.env["fix.approval.matrix"]
        for row in self:
            if not row.date_from:
                raise UserError(
                    "Rule %s carries no effective date, so there is nothing to "
                    "version — set its Effective From first." % row.display_name
                )
            clash = self.sudo().search_count(
                [
                    ("decision_domain", "=", row.decision_domain or False),
                    ("currency_id", "=", row.currency_id.id or False),
                    ("res_model", "=", row.res_model or False),
                    ("date_from", "=", tomorrow),
                    ("id", "!=", row.id),
                ]
            )
            if clash:
                raise ValidationError(
                    "A rule for %s / %s already takes effect on %s — edit that "
                    "row instead of stacking versions on the same date."
                    % (row.decision_domain or row.res_model, row.currency_id.name, tomorrow)
                )
            row.with_context(matrix_version_engine=True).write({"date_to": today})
            new_rows |= row.copy(
                {
                    "name": "%s (from %s)" % (row.name or row.display_name, tomorrow),
                    "date_from": tomorrow,
                    "date_to": False,
                    "active": True,
                }
            )
        if not new_rows:
            return True
        return {
            "type": "ir.actions.act_window",
            "name": "New rule version",
            "res_model": "fix.approval.matrix",
            "res_id": new_rows.ids[0] if len(new_rows) == 1 else False,
            "views": [(False, "form")],
            "target": "current",
        }


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
    # A03 audit R7 (W3): "exclude anyone who last changed the amount". Whoever
    # set the figure must not be the one who signs it off: raising a refund
    # and then approving it is the same conflict as creating it.
    approval_amount_changed_by_id = fields.Many2one(
        "res.users",
        string="Amount Last Changed By",
        readonly=True,
        copy=False,
        help="The last user who changed the amount at risk. The approval engine "
        "never routes this record to them.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "approval_state",
            "approval_request_id",
            "approval_amount_changed_by_id",
        }

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

    def _approval_check_vote(self):
        """A vote that does not yet complete the request (policy 'all', other
        approvers still to decide) must still be one this approver may cast:
        the record's own approve method runs as a DRY RUN, so its tier,
        segregation-of-duties and justification checks apply to this voter,
        and is rolled back, so nothing is stamped before the quorum is met
        (A11 audit E4, M63-3)."""
        try:
            with self.env.cr.savepoint():
                self._approval_apply()
                raise _VoteDryRun()
        except _VoteDryRun:
            pass

    def _approval_clear_stamp(self, reason):
        """Hook: withdraw what the approve method stamped on the record. The
        DOFA models clear their DOFA stamp (and model flags tied to it)."""
        return None

    def _approval_pinned_fields(self) -> set:
        """Fields whose change voids a pending or granted approval, like the
        amount does (A11 audit E4, M63-6): the payee, counterparty, currency
        and type the approval was given for. Extend with super()."""
        return {
            name
            for name in APPROVAL_PINNED_DEFAULT
            if name in self._fields and self._fields[name].store
        }

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

    def _approval_authority_group(self, tier):
        """The CODE-declared group whose holders may decide: the DOFA tier's
        group, else the model's `_approval_group` / `_approval_group_xmlid()`.
        Never read from the rule book (A11 audit E3, M63-2)."""
        xmlid = TIER_GROUP.get(tier) if tier else self._approval_group_xmlid()
        group = self.env.ref(xmlid, raise_if_not_found=False) if xmlid else None
        return group if group and group._name == "res.groups" else None

    @api.model
    def _approval_group_narrows(self, group, authority):
        """True when every holder of `group` also holds `authority`: the
        group IS the authority, or implies it."""
        if not (group and authority):
            return False
        group = group.sudo()
        return group == authority or authority in group.all_implied_ids

    def _approval_group_for(self, rule, tier):
        """Who is asked. A11 audit E3 (M63-2): the matrix row being decided
        under used to name the group that both routed AND authorised the
        decision, so a salesperson pointed `contract_verification` at his own
        group and verified a colleague's contract. Now the authority is the
        coded group; a row's approver group may only NARROW it (a group that
        implies the coded one, e.g. one branch's managers), and is ignored
        otherwise."""
        authority = self._approval_authority_group(tier)
        narrower = rule.approver_group_id if rule else None
        if narrower and self._approval_group_narrows(narrower, authority):
            return narrower
        if narrower:
            _logger.info(
                "Approval rule %s names %s, which does not narrow %s; ignored.",
                rule.id,
                narrower.name,
                authority.name if authority else "no coded group",
            )
        return authority

    def _approval_excluded(self):
        """Requester, creator and whoever last changed the amount never
        decide the record (A03 audit R7, W3)."""
        self.ensure_one()
        return (self.env.user | self.create_uid | self.approval_amount_changed_by_id).sudo()

    def _approval_excluded_for(self, request):
        """Everyone who must not be handed `request`, whoever runs the code.

        A11 audit E4 (M63-4): `_approval_excluded()` reads env.user as the
        requester; the escalation cron runs as the superuser, so a Tier-2
        manager who requested a Tier-1 approval was escalated his own
        request and approved it. The request's stored requester, the
        record's creator, the amount-changer and everyone already assigned
        (or represented) on the request are excluded explicitly."""
        excluded = self._approval_excluded()
        if request:
            req = request.sudo()
            excluded |= (
                req.requested_by_id
                | req.record_creator_id
                | req.amount_changed_by_id
                | req.task_ids.mapped("assigned_user_id")
                | req.task_ids.mapped("on_behalf_of_id")
            )
        return excluded.sudo()

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

    def _approval_substitutes(self, users, excluded=None):
        """[(assignee, on_behalf_of or None)] after today's valid substitutions
        (active, in date, and a delegate the policy allows). A delegate who is
        excluded (creator, requester, amount-changer, already on the request)
        does not take the task: the absent approver keeps it."""
        delegate_of = self.env["fix.approval.substitution"].sudo()._active_delegates()
        if excluded is None:
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
        group = self._approval_group_for(rule, tier)
        users = self._approval_holders(group)
        if tier and group and group == self._approval_authority_group(tier):
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
            # Tier 2 and above needs a written justification to be approved. Saying
            # so here keeps a blank request from waiting on a vote that can only refuse.
            if (
                tier
                and "dofa_justification" in rec._fields
                and hasattr(rec, "_dofa_tier_rank")
                and rec._dofa_tier_rank(tier) >= rec._dofa_tier_rank("tier_2")
                and not (rec.dofa_justification or "").strip()
            ):
                raise UserError(
                    "Write the justification for %s: the approver cannot approve without one."
                    % rec.display_name
                )
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
                    "amount_changed_by_id": rec.sudo().approval_amount_changed_by_id.id,
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
            rec.sudo()._approval_clear_stamp("the approval request %s was recalled" % req.name)
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
            # A11 audit E4 (M63-3): a voided approval leaves no stamp behind.
            # The state is already 'none', so the DOFA void this triggers does
            # not come back here.
            rec.sudo()._approval_clear_stamp(reason)

    def write(self, vals):
        if set(vals) <= _APPROVAL_BOOKKEEPING:
            return super().write(vals)
        pending = self.filtered(lambda r: r.approval_state == "pending")
        # A11 audit E4 (M63-6): the payee, counterparty, currency and type are
        # pinned like the amount. Same trust split: a user's change voids a
        # pending or granted approval; superuser code voids a pending one.
        pinned = self._approval_pinned_fields() & set(vals) if self else set()
        watched = (
            (
                pending
                if self.env.su
                else self.filtered(lambda r: r.approval_state in ("pending", "approved"))
            )
            if pinned
            else self.browse()
        )
        terms_before = {rec.id: {f: rec.sudo()[f] for f in pinned} for rec in watched}
        # W3: a user's write is measured on every record, to learn who moved
        # the amount. Superuser code (crons, seeds, service calls) is trusted,
        # as the guard trusts it, and is measured only where a request is
        # pending. The amount is often a related or computed value of the
        # record's own fields (DOFA), so it is compared before and after the
        # whole write, the DOFA mixin's own write included. Read as sudo: a
        # user allowed to write the record must not be refused for reading
        # an amount field outside their groups.
        tracked = pending if self.env.su else self
        before = {rec.id: rec.sudo()._approval_amount() for rec in tracked}
        result = super().write(vals)
        changed = tracked.filtered(
            lambda r: abs(r.sudo()._approval_amount() - before[r.id]) > 0.005
        )
        if changed and not self.env.su:
            changed._guarded().write({"approval_amount_changed_by_id": self.env.uid})
        for rec in changed & pending:
            if rec.approval_state == "pending":
                rec._approval_void(
                    "the amount changed from %.2f to %.2f while approval was pending; "
                    "request it again." % (before[rec.id], rec.sudo()._approval_amount())
                )
        moved = {}
        for rec in watched:
            names = [f for f in pinned if rec.sudo()[f] != terms_before[rec.id][f]]
            if names:
                moved[rec] = names
        if moved and not self.env.su:
            # Whoever re-pointed the approval must not be the one to sign it off.
            self.browse([r.id for r in moved])._guarded().write(
                {"approval_amount_changed_by_id": self.env.uid}
            )
        for rec, names in moved.items():
            if rec.approval_state in ("pending", "approved"):
                labels = ", ".join(rec._fields[n].string or n for n in sorted(names))
                rec._approval_void(
                    "%s changed after the approval was %s; it covered the terms it was "
                    "given for. Request it again."
                    % (labels, "requested" if rec.approval_state == "pending" else "granted")
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

    def _approval_clear_stamp(self, reason):
        # Through the model's own void, so flags tied to the stamp (e.g. a
        # complaint's concession_approved) go with it.
        stamped = self.filtered("dofa_approved")
        if stamped:
            stamped._dofa_void_approval(reason)
        return super()._approval_clear_stamp(reason)


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
    amount_changed_by_id = fields.Many2one(
        "res.users",
        string="Amount / Terms Last Changed By",
        readonly=True,
        help="Who last changed the amount or a pinned term before the request. "
        "Never an approver of this request.",
    )
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

    # ---- business hours (A03 audit R7, W2) ---------------------------------
    # R7: escalation "uses the working calendar". A 24-hour SLA raised on a
    # Thursday evening fell due on Friday, the weekend, and escalated before
    # any approver was at work; an Eid closure did the same for days.
    def _approval_calendar(self, record=None):
        """The working calendar an SLA on this request counts, in order: the
        rule's own calendar, the record's branch calendar, the company default
        (config parameter), else none (wall-clock hours)."""
        Calendar = self.env["fix.working.calendar"].sudo()
        rule = self.matrix_id if len(self) == 1 else self.env["fix.approval.matrix"]
        if rule.calendar_id.active:
            return rule.calendar_id.sudo()
        if record is None and len(self) == 1:
            record = self._record(self.env(su=True))
        field = record._fields.get("branch_id") if record else None
        if field is not None and field.type == "many2one" and field.comodel_name == "fix.branch":
            calendar = record.sudo()[:1].branch_id.calendar_id
            if calendar.active:
                return calendar
        raw = self.env["ir.config_parameter"].sudo().get_param(CALENDAR_PARAM)
        try:
            calendar = Calendar.browse(int(raw)).exists() if raw else Calendar
        except (TypeError, ValueError):
            _logger.warning("%s is not a calendar id: %r", CALENDAR_PARAM, raw)
            calendar = Calendar
        return calendar if calendar.active else Calendar

    @api.model
    def _approval_calendar_rules(self, calendar):
        """({weekday: [(hour_from, hour_to)]}, [(date_from, date_to)]) for a
        calendar, with its template chain: the nearest calendar's lines for a
        weekday win; holidays add up."""
        lines, holidays, seen = {}, [], set()
        cal = calendar.sudo() if calendar else None
        while cal and cal.id not in seen:
            seen.add(cal.id)
            own = {}
            for line in cal.line_ids:
                own.setdefault(line.weekday, []).append((line.hour_from, line.hour_to))
            for weekday, windows in own.items():
                lines.setdefault(weekday, sorted(windows))
            holidays += [(h.date_from, h.date_to) for h in cal.holiday_ids]
            cal = cal.template_id
        return lines, holidays

    @api.model
    def _approval_add_business_hours(self, start_utc, hours, calendar):
        """The moment `hours` of working time after `start_utc`.

        Both datetimes are naive UTC (Odoo's convention). The calendar's
        windows are Dhaka local time, so the walk runs in the calendar's zone.
        Holidays close the whole day. With no calendar, or a calendar with no
        lines, the hours are wall-clock hours. A calendar with no working time
        in MAX_CALENDAR_DAYS also falls back to wall clock, with a warning: a
        deadline that is merely early beats a request that never falls due."""
        span = timedelta(hours=max(hours or 0.0, 0.0))
        lines, holidays = self._approval_calendar_rules(calendar)
        if not lines or span <= timedelta(0):
            return start_utc + span
        zone = pytz.timezone(calendar.timezone or "Asia/Dhaka")
        cursor = pytz.utc.localize(start_utc).astimezone(zone).replace(tzinfo=None)
        remaining = span
        for _ in range(MAX_CALENDAR_DAYS):
            day = cursor.date()
            if not any(d_from <= day <= d_to for d_from, d_to in holidays):
                midnight = datetime.combine(day, time.min)
                for hour_from, hour_to in lines.get(WEEKDAY_KEYS[day.weekday()], ()):
                    win_end = midnight + timedelta(hours=hour_to)
                    begin = max(cursor, midnight + timedelta(hours=hour_from))
                    if win_end <= begin:
                        continue
                    if win_end - begin >= remaining:
                        local = begin + remaining
                        return zone.localize(local).astimezone(pytz.utc).replace(tzinfo=None)
                    remaining -= win_end - begin
            cursor = datetime.combine(day + timedelta(days=1), time.min)
        _logger.warning(
            "Working calendar %r has no working time in %d days; approval SLA "
            "counted in wall-clock hours.",
            calendar.display_name,
            MAX_CALENDAR_DAYS,
        )
        return start_utc + span

    def _approval_due(self, start=None, record=None):
        """When an approver's task on this request falls due, from `start`."""
        self.ensure_one()
        return self._approval_add_business_hours(
            start or fields.Datetime.now(),
            max(self._rule_value("sla_hours"), 1),
            self._approval_calendar(record),
        )

    def _open_tasks(self, approvers, level=0):
        """One inbox task (and to-do activity) per approver."""
        self.ensure_one()
        record = self._record(self.env(su=True))
        due = self._approval_due(record=record)
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

    def _committed_state(self):
        """(state, decided_by_id) as COMMITTED, read through a cursor of its own.

        Odoo cursors run REPEATABLE READ (sql_db.py), so this transaction's
        own reads keep returning the snapshot taken when it began: a value
        another transaction committed afterwards is invisible here, however
        often the ORM cache is invalidated. Only a new transaction can say
        what the database now holds — which is exactly what a loser of the
        decide-path race needs to be told."""
        self.ensure_one()
        cr = self.env.registry.cursor()
        try:
            cr.execute(
                "SELECT state, decided_by_id FROM fix_approval_request WHERE id = %s",
                [self.id],
            )
            return cr.fetchone()
        finally:
            cr.close()

    def _decision_lock(self):
        """The request's row lock, and its state as COMMITTED, not cached.

        A11 audit F10 (the decide-path race): _decide_check read the request,
        the task and the assignee, and the writes happened later — two
        approvers acting in the same window both passed the check and both
        decisions then took effect, the second overturning the first with no
        refusal anywhere. Every decision now takes this lock first.

        Under REPEATABLE READ a row another transaction committed after this
        transaction's snapshot cannot be locked at all: PostgreSQL raises
        SerializationFailure instead of waiting (Odoo's HTTP layer retries
        such a request as a whole). That refusal is the loser signal, and it
        carries the one fact worth reporting — who decided first, read from
        the committed state. A failure that leaves the request still pending
        (the hourly cron bumped only reminded_at) is not a lost decision, so
        it is re-raised for Odoo's own retry rather than refused.

        The lock is held to the end of the transaction — releasing a
        savepoint would hand it back early."""
        self.ensure_one()
        try:
            with self.env.cr.savepoint():
                self.env.cr.execute(
                    "SELECT state, decided_by_id FROM fix_approval_request WHERE id = %s "
                    "FOR UPDATE",
                    [self.id],
                )
                row = self.env.cr.fetchone()
        except TransactionRollbackError:
            row = self._committed_state()
            if not row or row[0] != "pending":
                self._raise_already_decided(row)
            raise
        # What this environment cached about the request, its tasks and its
        # record may predate the locked read: drop it, so every later read of
        # this decision sees the locked truth.
        tasks = self.task_ids
        self.invalidate_recordset()
        tasks.invalidate_recordset()
        record = None
        if self.res_model in self.env:
            record = self.env[self.res_model].browse(self.res_id).exists()
        if record:
            record.invalidate_recordset()
        if row and row[0] != "pending":
            self._raise_already_decided(row)
        return row

    def _raise_already_decided(self, row):
        if not row:
            raise UserError(
                "This approval request no longer exists; the decision did not take effect."
            )
        state = dict(REQUEST_STATES).get(row[0], row[0]) or row[0]
        who = "another session"
        if row[1]:
            who = self.env["res.users"].sudo().browse(row[1]).name
        raise UserError(
            "This approval request was already decided by %s (it is now %s), so the "
            "decision you just made at the same moment did not take effect. Refresh "
            "your inbox." % (who, state)
        )

    def _finish(self, state, event, user, task=None, comment=None, record_state=None):
        """Close this request: decide it, cancel open tasks, stamp the record.

        A11 audit F10: the closing write is atomic against a concurrent
        decision. The task paths already hold the row lock from _decide_check;
        recall, void and the cron's final action never went through it, so the
        lock is re-taken here, inside a savepoint — a refused or failed finish
        leaves nothing half-written behind."""
        self.ensure_one()
        with self.env.cr.savepoint():
            self._decision_lock()
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

    def _completed_by(self, task):
        """True when approving `task` completes this request: policy 'any',
        or the last open task under 'all'."""
        self.ensure_one()
        open_tasks = self.task_ids.filtered(lambda t: t.state == "pending" and t != task)
        return self.approval_policy != "all" or not open_tasks

    def _task_approved(self, task, comment=None):
        self.ensure_one()
        self._log("task_approved", user=self.env.user, task=task, comment=comment)
        if not self._completed_by(task):
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
        # A11 audit E4 (M63-4): the cron runs as the superuser, so the
        # exclusions are read from the request, not from env.user.
        excluded = record._approval_excluded_for(self)
        target = self.matrix_id.escalate_to_id
        if target:
            return [(target, None)] if target not in excluded else []
        if self.tier not in TIER_ORDER or self.tier == "tier_5":
            return []
        nxt = TIER_ORDER[TIER_ORDER.index(self.tier) + 1]
        group = self.env.ref(TIER_GROUP[nxt], raise_if_not_found=False)
        users = record._approval_lowest_competent(record._approval_holders(group), nxt) - excluded
        return record._approval_substitutes(users, excluded)

    @api.model
    def cron_escalate_overdue(self):
        """Overdue: remind once, then escalate up to the rule's limit, then
        apply its final action. Every new deadline counts working hours on
        the request's calendar (_approval_calendar), else wall-clock hours."""
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
            try:
                with self.env.cr.savepoint():
                    self._escalate_one(req, now)
            except Exception:
                _logger.exception(
                    "M63 escalation failed for request %s; the other overdue requests "
                    "are still processed this run.",
                    req.name,
                )
        self._rescue_orphans(now)

    def _escalate_one(self, req, now):
        """One overdue request's remind / escalate / final-action step."""
        record = req._record(self.env(su=True))
        if not record:
            return
        due = req._approval_due(now, record)
        pending_tasks = req.task_ids.filtered(lambda t: t.state == "pending")
        if not req.reminded_at:
            req.write({"reminded_at": now})
            pending_tasks._guarded().write({"due_at": due})
            req._log("reminded", user=self.env.user, comment="approval overdue; reminder sent")
            publish(self.env, "approval.reminder", req.res_model, req.res_id, {"request": req.name})
            return
        if req.escalation_level < req._rule_value("max_escalations"):
            targets = req._next_tier_holders(record)
            if targets:
                level = req.escalation_level + 1
                req.write({"escalation_level": level})
                req._open_tasks(targets, level=level)
                pending_tasks._guarded().write({"due_at": due})
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
                return
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
            # A11 audit F08: the "keep pending" expiry used to be silent — one
            # history row nobody reads, no event, no notice, so a request could
            # die quietly in a full inbox (and a group-routed request, which
            # has no tier to escalate through, went straight here). The event
            # says who it still waits for; the contact centre's consumer turns
            # it into the last warning. The request itself stays pending — the
            # engine never auto-approves.
            req._log("expired", user=self.env.user, comment="no decision after every escalation")
            waiting = req.task_ids.filtered(lambda t: t.state == "pending").mapped(
                "assigned_user_id"
            )
            publish(
                self.env,
                "approval.expired",
                req.res_model,
                req.res_id,
                {
                    "request": req.name,
                    "record": req.res_name,
                    "rule": req.matrix_id.display_name or "the default rule",
                    "level": req.escalation_level,
                    "waiting_for": [u.id for u in waiting],
                },
            )

    # ---- orphaned requests (A11 audit F09) ---------------------------------
    @api.model
    def _rescue_orphans(self, now=None):
        """A pending request with no open task is no longer immortal.

        A helper of cron_escalate_overdue, not a cron of its own: the name
        deliberately avoids the cron_ prefix, because check_deployment_wiring
        treats every such method as a job that must own an ir.cron record.

        Whatever lost its tasks — a crash between the request's creation and
        _open_tasks, a deleted-task bug, a direct-ORM fixture — the request
        counted as pending and overdue forever: the cron above only ever
        looked at requests WITH a pending task past due, and only the
        requester could end it. Once such a request is older than its own
        SLA, the approvers are re-derived once: somebody gets the task again
        (with the trail saying so), or — when nobody can approve the record —
        the request is voided with the full trail instead of waiting forever.
        """
        now = now or fields.Datetime.now()
        orphans = (
            self.sudo()
            .search([("state", "=", "pending")])
            .filtered(lambda r: not r.task_ids.filtered(lambda t: t.state == "pending"))
        )
        for req in orphans:
            try:
                with self.env.cr.savepoint():
                    self._rescue_one_orphan(req, now)
            except Exception:
                _logger.exception(
                    "M63 orphan rescue failed for request %s; the other orphaned "
                    "requests are still processed this run.",
                    req.name,
                )

    def _rescue_one_orphan(self, req, now):
        record = req._record(self.env(su=True))
        if not record:
            return
        if req._approval_due(start=req.requested_at, record=record) > now:
            return  # inside its SLA: quiet, not orphaned
        # Re-derive on the request's own pinned rule, minus everyone the
        # request itself forbids (the requester, the creator, the
        # amount-changer, anyone already assigned to it).
        excluded = record._approval_excluded_for(req)
        approvers = [
            (user, behalf)
            for user, behalf in record._approval_resolve(req.matrix_id, req.tier)
            if user not in excluded
        ]
        if approvers:
            req._open_tasks(approvers, level=req.escalation_level)
            req._log(
                "requeued",
                user=self.env.user,
                comment="the request had no open task; approvers re-derived and routed "
                "again to %s" % ", ".join(u.name for u, _b in approvers),
            )
            publish(
                self.env,
                "approval.requested",
                req.res_model,
                req.res_id,
                {
                    "request": req.name,
                    "tier": req.tier or None,
                    "amount": req.amount,
                    "approver_ids": [u.id for u, _b in approvers],
                },
            )
            return
        req._finish(
            "voided",
            "voided",
            self.env.user,
            comment="no open task for an SLA past due and nobody can approve the record: "
            "voided by the overdue sweep so it cannot wait forever",
            record_state="none",
        )
        record.sudo()._approval_clear_stamp(
            "the request %s lost its tasks and had no approver left" % req.name
        )

    # ---- the DoA Administrator's recorded way out (A11 audit F09) -----------
    def action_void_request(self, reason=None):
        """Void a request that can no longer be decided, and record why.

        A pending request that lost its tasks, or was routed to people who
        have all left, used to be immortal: the cron ignored it and only the
        requester could recall it. This is the DoA Administrator's
        intervention — the requester keeps his recall, this is the
        administrator's. It is evidence: a reason of at least a sentence, an
        append-only history row with the actor, the time and the state before
        and after, the approval.decided event, and — mirroring what a recall
        clears — no stamp left on the record.
        """
        if not (self.env.su or self.env.user.has_group(DOA_ADMIN)):
            raise AccessError("Only a DoA Administrator voids an approval request.")
        for req in self:
            if req.state != "pending":
                raise UserError(
                    "Only a pending approval request can be voided: %s is %s."
                    % (req.name, dict(REQUEST_STATES).get(req.state, req.state) or req.state)
                )
            text = (reason or "").strip()
            if len(text) < 10:
                raise UserError(
                    "State why %s is voided (at least a sentence): the reason is kept "
                    "with the request for audit." % req.name
                )
            record = req._record(self.env(su=True))
            req._finish(
                "voided",
                "voided",
                self.env.user,
                comment="DoA intervention, pending -> voided: %s" % text,
                record_state="none",
            )
            if record:
                record.sudo()._approval_clear_stamp(
                    "the request %s was voided by %s" % (req.name, self.env.user.name)
                )
        return True

    # ---- event consumer (A11 audit F08) ------------------------------------
    @api.model
    def consume_approval_expired(self, event: dict) -> dict:
        """The keep-pending expiry's last warning, delivered in-module.

        A11 audit F08 required the expiry to stop being silent. The e-mail/SMS
        consumer for the other four approval.* events lives in
        cd_contact_centre; that module's files were being rewritten by another
        session while this fix was built (the edits reverted within seconds,
        twice), so the consumer ships here instead: the engine guarantees the
        notice itself — one to-do for the requester and a chatter note on the
        record — rather than publishing an event nobody consumes. Called only
        by the event relay; idempotent per request, so a replayed event adds
        nothing.
        """
        if not self.env.su:
            raise AccessError("Approval event consumers run only from the event relay.")
        payload = event.get("payload") or {}
        name = payload.get("request")
        req = self.sudo().search([("name", "=", name)], limit=1) if name else self.browse()
        if not req:
            return {"notified": 0, "reason": "request not found"}
        if not req.requested_by_id:
            return {"notified": 0, "reason": "no requester to notify"}
        record = req._record(self.env(su=True))
        if not record or not hasattr(record, "activity_schedule"):
            return {"notified": 0, "reason": "the routed record is gone"}
        waiting = req.task_ids.filtered(lambda t: t.state == "pending").mapped("assigned_user_id")
        summary = "Approval still pending: %s" % req.name
        # One to-do per request for its requester; a replayed event adds none.
        # The activity sits on the RECORD (the request model carries no
        # activity mixin) and names the request, so the requester opens the
        # document the approval is about.
        Activity = self.env["mail.activity"].sudo()
        existing = Activity.search_count(
            [
                ("res_model", "=", record._name),
                ("res_id", "=", record.id),
                ("summary", "=", summary),
                ("user_id", "=", req.requested_by_id.id),
            ]
        )
        if existing:
            return {"notified": 0, "reason": "already notified", "request": req.name}
        record.activity_schedule(
            "mail.mail_activity_data_todo",
            date_deadline=fields.Date.context_today(self),
            summary=summary,
            note="%s is still pending after %s escalation(s); it waits for %s (event %s)."
            % (
                req.res_name,
                payload.get("level") or 0,
                ", ".join(waiting.mapped("name")) or "no open task",
                event.get("event_id") or "-",
            ),
            user_id=req.requested_by_id.id,
        )
        if hasattr(record, "message_post"):
            record.message_post(
                body="Approval %s is still pending after every escalation: it waits for %s."
                % (req.name, ", ".join(waiting.mapped("name")) or "no open task")
            )
        return {"notified": 1, "request": req.name}

    # ---- KPIs (R11) --------------------------------------------------------
    def _decided_by_a_conflicted_user(self):
        """A11 audit E4 (M63-11): the decider, or whom he acted for, is the
        record's creator, the requester, or whoever changed the amount or a
        pinned term. A delegate of the requester counts as the requester."""
        self.ensure_one()
        conflicted = self.record_creator_id | self.requested_by_id | self.amount_changed_by_id
        record = self._record(self.env(su=True))
        if record and "approval_amount_changed_by_id" in record._fields:
            conflicted |= record.approval_amount_changed_by_id
        return bool((self.decided_by_id | self.on_behalf_of_id) & conflicted)

    @api.model
    def approval_kpis(self):
        """E6 (M63-11): every figure is read AS THE CALLER, under the caller's
        record rules and companies — the sudo reads put every company's
        requests and ages into any user's KPI strip."""
        reqs = self.search([])
        now = fields.Datetime.now()
        pending = reqs.filtered(lambda r: r.state == "pending")
        ages = [(now - r.requested_at).total_seconds() / 3600.0 for r in pending]
        approved = reqs.filtered(lambda r: r.state == "approved")
        history = self.env["fix.approval.history"].search([])
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
            # Should always be 0: the engine never routes to the creator, the
            # requester, the amount-changer, or a delegate acting for them.
            "approver_is_creator": len(
                approved.filtered(lambda r: r._decided_by_a_conflicted_user())
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
    # What the requester wrote: the approver decides on it, from the inbox.
    justification = fields.Text(related="request_id.justification")
    is_mine = fields.Boolean(compute="_compute_is_mine", search="_search_is_mine")

    def _fix_guarded_fields(self) -> set:
        # A task that could be created, reassigned or marked done by hand
        # would be an approval anyone can type (A03 audit, M63 row). A11
        # audit E1 (M63-10): the rest of the task was still open, so a plain
        # user re-typed a colleague's pending approval as a "review" (hiding
        # it from Approval Chains) and back-dated `created_at` (the cycle-time
        # KPI). Every field is now set by the engine; the decision comment is
        # written by the decision itself.
        return super()._fix_guarded_fields() | {
            "name",
            "company_id",
            "instance_id",
            "task_type",
            "created_at",
            "assigned_to_id",
            "state",
            "decision",
            "decided_at",
            "request_id",
            "assigned_user_id",
            "on_behalf_of_id",
            "activity_id",
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
        # Odoo 19 rewrites ('is_mine', '=', True) to ('in', [True]) before this runs. Reading
        # only "=" negated the domain: the inbox hid the user's tasks and listed everyone else's.
        if operator in ("in", "not in"):
            wanted = any(value) if isinstance(value, list | tuple | set) else bool(value)
            mine = wanted if operator == "in" else not wanted
        else:
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
        if self.request_id:
            # A11 audit F10 (decide-path race): the checks below run under the
            # request's row lock, on the state as committed — not on what this
            # transaction cached before another approver's decision committed.
            # A loser here is told who decided the request instead of quietly
            # overturning them a few statements later.
            self.request_id._decision_lock()
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
        if self.request_id:
            # A11 audit E4 (M63-4): whoever routed it here, the requester,
            # the record's creator and the amount-changer never decide it,
            # nor does a delegate acting for one of them.
            req = self.request_id.sudo()
            conflicted = req.requested_by_id | req.record_creator_id | req.amount_changed_by_id
            acting = self.env.user | self.on_behalf_of_id
            if conflicted & acting:
                raise UserError(
                    "Segregation of duties: %s requested, raised or changed %s and cannot "
                    "decide its approval." % ((conflicted & acting)[:1].name, req.res_name)
                )

    # ---- delegation at the moment of decision (A11 audit E2, M63-5) ----------
    def _delegation_lapsed(self) -> bool:
        """A task routed to a delegate is decided only while the delegation
        holds: active, in date, and a delegate the policy still allows."""
        self.ensure_one()
        if not self.on_behalf_of_id:
            return False
        Sub = self.env["fix.approval.substitution"].sudo()
        return not Sub._is_valid_delegation(self.on_behalf_of_id, self.assigned_user_id)

    def _approval_hand_back(self, reason):
        """Give a delegated task back to the absent approver it was routed for."""
        for task in self.sudo().filtered(lambda t: t.state == "pending" and t.on_behalf_of_id):
            principal = task.on_behalf_of_id
            delegate = task.assigned_user_id
            req = task.request_id
            if task.activity_id:
                task.activity_id.unlink()
            twin = req.task_ids.filtered(
                lambda t, p=principal: t.state == "pending" and t.assigned_user_id == p
            )
            if twin:
                # The absent approver already holds a task on this request.
                task._guarded().write({"state": "cancelled"})
            else:
                vals = {
                    "assigned_user_id": principal.id,
                    "assigned_to_id": principal.employee_ids[:1].id or False,
                    "on_behalf_of_id": False,
                    "activity_id": False,
                }
                record = req._record(self.env(su=True)) if req else None
                if record and hasattr(record, "activity_schedule"):
                    vals["activity_id"] = record.activity_schedule(
                        "mail.mail_activity_data_todo",
                        date_deadline=(task.due_at or fields.Datetime.now()).date(),
                        summary="Approve %s" % req.name,
                        note="%s awaits your decision in the M63 approval inbox (handed back "
                        "from %s)." % (req.res_name, delegate.name),
                        user_id=principal.id,
                    ).id
                task._guarded().write(vals)
            if req:
                req._log(
                    "handed_back",
                    user=principal,
                    comment="%s; task handed back from %s to %s"
                    % (reason, delegate.name, principal.name),
                )

    @api.model
    def _handed_back_notice(self, tasks):
        if not tasks:
            return True
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Delegation no longer valid",
                "message": "Your delegation for %s has ended or no longer qualifies; the "
                "task went back to %s and was not decided."
                % (
                    ", ".join(tasks.mapped("request_id.res_name"))
                    or ", ".join(tasks.mapped("name")),
                    ", ".join(tasks.sudo().mapped("assigned_user_id.name")),
                ),
                "type": "warning",
                "sticky": True,
            },
            "handed_back": tasks.ids,
        }

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
        handed = self.browse()
        for task in self:
            task._decide_check()
            if task._delegation_lapsed():
                task._approval_hand_back("the delegation for this approval is no longer valid")
                handed |= task
                continue
            req = task.request_id.sudo()
            if req:
                # In the approver's env, not the request's sudo one: an apply
                # method ran as superuser, so the guard and every env.su check
                # were open for each inbox decision (A03 audit W4 finding).
                record = req._record(self.env)
                if not record:
                    raise UserError("The record this approval was for no longer exists.")
                # The record's own approve method, in the approver's env, with
                # the task in context: DOFA tier, SoD and justification apply.
                # A11 audit E4 (M63-3): it is APPLIED only by the vote that
                # completes the request; an earlier vote under 'all' is a dry
                # run of the same checks.
                record = record.with_context(**{TASK_KEY: task})
                if req._completed_by(task):
                    record._approval_apply()
                else:
                    record._approval_check_vote()
            task._decide("approved", comment)
            if req:
                req.with_user(self.env.user)._task_approved(task, comment)
        return self._handed_back_notice(handed)

    def action_reject(self, comment=None):
        handed = self.browse()
        for task in self:
            task._decide_check()
            if task._delegation_lapsed():
                task._approval_hand_back("the delegation for this approval is no longer valid")
                handed |= task
                continue
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
                record = req._record(self.env)
                if record:
                    record.with_context(**{TASK_KEY: task})._approval_on_rejected(comment)
                    # A11 audit E4 (M63-3): a rejected request leaves no stamp.
                    record.sudo()._approval_clear_stamp("rejected in %s" % req.name)
        return self._handed_back_notice(handed)

    def action_return(self, comment=None):
        """Send it back to the requester for more information."""
        handed = self.browse()
        for task in self:
            task._decide_check()
            if not task.request_id:
                raise UserError("Only a routed approval can be returned for information.")
            if task._delegation_lapsed():
                task._approval_hand_back("the delegation for this approval is no longer valid")
                handed |= task
                continue
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
        return self._handed_back_notice(handed)
