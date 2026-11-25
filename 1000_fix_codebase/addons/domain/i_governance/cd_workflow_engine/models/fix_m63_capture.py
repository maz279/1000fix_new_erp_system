# fix_m63_capture — M63 sub-module capture audit (2026-11-18).
#
# The user saw M63 pages with no relevant capture. Evaluated with the engine's
# own fregCreate / fregPanels, three pages were short of a record the
# specification (M63 §5, §9, §10.1) says they hold:
#
#   * page 4 "Business Rules": its "Rule Simulation" screen showed the
#     automation-rate report. Nothing simulated a rule change against history
#     (FR-BPA-007, BRU-BPA-04 H "a rule change must be simulated against
#     historical transactions before activation", entity fix.rule.simulation).
#     The routing rules the engine actually reads are the DoA matrix rows, so
#     a simulation runs one of them over a past period, with no side effect;
#   * page 7 "Audit & Performance": its "+ New" typed a workflow instance by
#     hand (nothing in the code starts one, and a typed instance fed the
#     automation-rate and STP KPIs). What the page is for was missing: the
#     register of routine work that is the denominator of the 85% automation
#     target (AUT-BPA-21, AC-25, Q-02, entity fix.automation.register), and a
#     recorded manual intervention on a stuck instance (FR-BPA-008,
#     BRU-BPA-15/23): Complete / Mark Failed / Escalate changed an instance
#     with no reason and no record of who did it;
#   * page 1 "Workflow Engine": an automation could declare only "manual
#     fallback" or "retry"; FR-BPA-004 (P0) names five behaviours.
#
# Loaded last: it extends fix.automation, fix.workflow.instance and
# fix.approval.matrix from the other model files.
from datetime import datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_approval_engine import DEFAULT_RULE

DOA_ADMIN = "cd_workflow_engine.group_doa_administrator"
PLATFORM_ADMIN = "cd_entity_config.group_platform_admin"

# FR-BPA-004: block, retry, escalate, fall back, compensate. The register's
# two existing values are kept ("fall back" = manual_fallback).
FAILURE_ADD = [
    ("block", "Block (refuse and alert the owner)"),
    ("escalate", "Escalate to the process owner"),
    ("compensate", "Compensate (undo the completed steps)"),
]

# A simulation reads at most this many historical records per run, newest
# first, and says so when the period held more.
SIMULATION_CAP = 5000
SAMPLE_LINES = 20

# What a matrix row decides about HOW an approval runs. Two rules that agree on
# all of these route a record the same way, whatever their names.
RULE_TERMS = (
    "approval_policy",
    "sla_hours",
    "max_escalations",
    "final_action",
    "approver_group_id",
    "escalate_to_id",
    "calendar_id",
)


class FixAutomation(models.Model):
    _inherit = "fix.automation"

    failure_policy = fields.Selection(
        selection_add=FAILURE_ADD,
        ondelete={key: "set default" for key, _label in FAILURE_ADD},
    )

    @api.depends("code", "trigger")
    def _compute_display_name(self):
        # The register has no name field: a picker showed "fix.automation,7".
        for rec in self:
            trigger = (rec.trigger or "").strip()
            rec.display_name = "%s · %s" % (rec.code, trigger[:60]) if trigger else rec.code


# =========================================================== rule simulation
class FixApprovalMatrix(models.Model):
    _inherit = "fix.approval.matrix"

    simulation_ids = fields.One2many("fix.rule.simulation", "matrix_id", readonly=True)
    simulation_count = fields.Integer(compute="_compute_simulation_state")
    last_simulated_at = fields.Datetime(
        string="Last Simulated", compute="_compute_simulation_state"
    )

    @api.depends("name", "decision_domain", "res_model", "date_from")
    def _compute_display_name(self):
        # fix_real's six rows carry no name: the simulation picker and every
        # "rule X" message showed "fix.approval.matrix,12".
        domains = dict(self._fields["decision_domain"].selection)
        for row in self:
            if row.name:
                row.display_name = row.name
                continue
            label = domains.get(row.decision_domain, row.decision_domain or "Rule")
            if row.res_model:
                label = "%s · %s" % (label, row.res_model)
            if row.date_from:
                label = "%s (from %s)" % (label, row.date_from)
            row.display_name = label

    @api.depends("simulation_ids.run_at")
    def _compute_simulation_state(self):
        for row in self:
            runs = row.sudo().simulation_ids
            row.simulation_count = len(runs)
            row.last_simulated_at = max(runs.mapped("run_at")) if runs else False

    @api.model
    def _rules_in_force_never_simulated(self):
        """Rows in force today with no simulation on record (spec §15 target 0)."""
        today = fields.Date.context_today(self)
        rows = self.sudo().search(
            [
                "|",
                ("date_from", "=", False),
                ("date_from", "<=", today),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", today),
            ]
        )
        return rows.filtered(lambda r: not r.simulation_ids)

    def _rule_terms(self):
        """The settings this row routes with, or the built-in default rule."""
        if not self:
            return (
                DEFAULT_RULE["approval_policy"],
                DEFAULT_RULE["sla_hours"],
                DEFAULT_RULE["max_escalations"],
                DEFAULT_RULE["final_action"],
                0,
                0,
                0,
            )
        self.ensure_one()
        return tuple(
            (self[name].id or 0) if self._fields[name].type == "many2one" else self[name]
            for name in RULE_TERMS
        )

    def _rule_terms_text(self):
        policy, sla, escalations, final, group, target, calendar = self._rule_terms()
        text = "%s, %s h, %s escalation(s), then %s" % (
            "all approve" if policy == "all" else "any one approves",
            sla,
            escalations,
            "auto-reject" if final == "reject" else "stays pending",
        )
        if group:
            text += ", group %s" % self.env["res.groups"].sudo().browse(group).name
        if target:
            text += ", escalates to %s" % self.env["res.users"].sudo().browse(target).name
        if calendar:
            text += ", %s" % self.env["fix.working.calendar"].sudo().browse(calendar).name
        return text


class FixRuleSimulation(models.Model):
    """One run of a DoA matrix rule over the records of a past period.

    It answers, before the rule governs anything, "what would have changed":
    for every record of the period its condition selects, how the approval
    would run under this rule against how it ran (the rule its request
    pinned) or would run today (the rule book as it stands). It reads only:
    no request, task, notification or posting is made (BRU-BPA-22, T-12).
    The run happens when the simulation is saved, and the result is evidence:
    it is never edited or deleted.
    """

    _name = "fix.rule.simulation"
    _description = "Approval Rule Simulation"
    _inherit = ["fix.guarded.mixin"]
    _order = "run_at desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    matrix_id = fields.Many2one(
        "fix.approval.matrix",
        string="Candidate Rule",
        required=True,
        index=True,
        ondelete="restrict",
        context={"active_test": False},
    )
    date_from = fields.Date(
        string="Period From",
        required=True,
        default=lambda self: fields.Date.context_today(self) - timedelta(days=90),
    )
    date_to = fields.Date(
        string="Period To", required=True, default=lambda self: fields.Date.context_today(self)
    )
    # ---- the result: set by the run, never typed --------------------------
    rule_snapshot = fields.Text(string="Rule as Simulated", readonly=True)
    target_models = fields.Char(string="Records Of", readonly=True)
    run_by_id = fields.Many2one("res.users", string="Run By", readonly=True)
    run_at = fields.Datetime(string="Run At", readonly=True)
    evaluated_count = fields.Integer(string="Records Evaluated", readonly=True)
    matched_count = fields.Integer(string="Selected by the Rule", readonly=True)
    changed_count = fields.Integer(string="Would Route Differently", readonly=True)
    unreached_count = fields.Integer(string="Kept by a More Specific Rule", readonly=True)
    truncated = fields.Boolean(string="Capped", readonly=True)
    summary = fields.Text(string="Outcome", readonly=True)
    sample_differences = fields.Text(string="Sample Differences", readonly=True)

    _period_ordered = models.Constraint(
        "CHECK (date_to >= date_from)", "A simulation period cannot end before it starts"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "rule_snapshot",
            "target_models",
            "run_by_id",
            "run_at",
            "evaluated_count",
            "matched_count",
            "changed_count",
            "unreached_count",
            "truncated",
            "summary",
            "sample_differences",
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.rule.simulation") or "RSIM/New"
                )
        sims = super().create(vals_list)
        for sim in sims:
            sim._run()
        return sims

    def write(self, vals):
        if self and not self.env.su and not self._fix_guard_has_token():
            raise UserError(
                "Simulation %s is evidence of what the rule would have done: it is "
                "never changed. Run a new simulation." % ", ".join(self.mapped("name"))
            )
        return super().write(vals)

    def unlink(self):
        raise UserError("A rule simulation is evidence and is never deleted.")

    # ---- the run ------------------------------------------------------------
    def _period_bounds(self):
        """The period's days in the user's time zone, as stored (UTC) bounds.

        The dates are Dhaka dates (UTC+6): a record made at 03:00 on the 18th
        is stored as 21:00 on the 17th, and a UTC midnight would leave it out
        of "the 18th" (found by the live test, 2026-11-18)."""
        tz = pytz.timezone(self.env.context.get("tz") or self.env.user.tz or "Asia/Dhaka")

        def utc(day):
            local = tz.localize(datetime.combine(day, time.min))
            return local.astimezone(pytz.UTC).replace(tzinfo=None)

        return utc(self.date_from), utc(self.date_to + timedelta(days=1))

    def _can_read(self, record):
        """Name a record in the sample only to someone who may open it (§13)."""
        try:
            return self.env[record._name].browse(record.id).has_access("read")
        except Exception:  # an unreadable model reads as "no"
            return False

    def _governing_rule(self, record):
        """The rule that routed `record` (its request pins it), or would now."""
        request = getattr(record, "approval_request_id", False)
        if request and request.sudo().matrix_id:
            return request.sudo().matrix_id, "routed"
        return self.env["fix.approval.matrix"].sudo()._match(record), "today"

    def _run(self):
        self.ensure_one()
        rule = self.matrix_id.sudo()
        names = rule._condition_models()
        if not names:
            raise UserError(
                "Rule %s applies to no model on this database (model %r, decision "
                "domain %r): there is nothing to simulate it against."
                % (rule.display_name, rule.res_model, rule.decision_domain)
            )
        condition = rule._parse_condition() if rule.condition else []
        start, end = self._period_bounds()
        evaluated = matched = changed = unreached = 0
        truncated = False
        samples, moved_from = [], {}
        new_terms = rule._rule_terms()
        for name in names:
            Model = self.env[name].sudo().with_context(active_test=False)
            period = [("create_date", ">=", start), ("create_date", "<", end)]
            remaining = SIMULATION_CAP - evaluated
            if remaining <= 0:
                truncated = True
                break
            total = Model.search_count(period)
            records = Model.search(period, order="id desc", limit=remaining)
            truncated = truncated or total > len(records)
            evaluated += len(records)
            hits = records.filtered_domain(condition) if condition else records
            matched += len(hits)
            for record in hits:
                try:
                    current, how = self._governing_rule(record)
                except UserError as exc:  # a legacy row with a broken condition
                    current, how = self.env["fix.approval.matrix"], "error: %s" % exc
                if current == rule:
                    continue
                if current and current.res_model and not rule.res_model:
                    # A row for the record's own model outranks a domain row.
                    unreached += 1
                    continue
                if current._rule_terms() == new_terms:
                    continue
                changed += 1
                label = current.display_name if current else "the built-in default rule"
                moved_from[label] = moved_from.get(label, 0) + 1
                if len(samples) < SAMPLE_LINES:
                    who = (
                        record.display_name
                        if self._can_read(record)
                        else "%s #%s"
                        % (
                            record._description,
                            record.id,
                        )
                    )
                    samples.append(
                        "%s (%s): %s [%s] -> %s"
                        % (
                            who,
                            str(record.create_date)[:10],
                            label,
                            current._rule_terms_text(),
                            "routed" if how == "routed" else "governs today",
                        )
                    )
        lines = [
            "%d record(s) of %s created %s to %s were evaluated; the rule's condition "
            "selects %d." % (evaluated, ", ".join(names), self.date_from, self.date_to, matched),
            "%d would route differently under this rule (%s)." % (changed, rule._rule_terms_text()),
        ]
        if unreached:
            lines.append(
                "%d stay with a rule written for their own model, which outranks this "
                "decision-domain rule." % unreached
            )
        for label, count in sorted(moved_from.items(), key=lambda kv: -kv[1]):
            lines.append("  from %s: %d" % (label, count))
        if truncated:
            lines.append(
                "The period held more records than one run reads (%d, newest first): "
                "narrow the period for a complete answer." % SIMULATION_CAP
            )
        if not changed:
            lines.append("No approval in the period would have run differently.")
        self.sudo()._guarded().write(
            {
                "rule_snapshot": "%s: %s%s"
                % (
                    rule.display_name,
                    rule._rule_terms_text(),
                    "; condition %s" % rule.condition if rule.condition else "",
                ),
                "target_models": ", ".join(names),
                "run_by_id": self.env.uid,
                "run_at": fields.Datetime.now(),
                "evaluated_count": evaluated,
                "matched_count": matched,
                "changed_count": changed,
                "unreached_count": unreached,
                "truncated": truncated,
                "summary": "\n".join(lines),
                "sample_differences": "\n".join(samples) or False,
            }
        )


# ===================================================== routine work register
class FixAutomationRegister(models.Model):
    """The register of routine operational work: the 85% target's denominator.

    One row is one recurring task, its monthly volume, and whether an
    automation does it. A claim of automation names the AUT row that does it
    (an automation nobody runs automates nothing), and the share that runs
    straight through. The automation rate is the automated volume over the
    whole registered volume (AUT-BPA-21, AC-25).
    """

    _name = "fix.automation.register"
    _description = "Routine Work Register Entry"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "process_area, name"

    name = fields.Char(string="Routine Task", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    process_area = fields.Char(string="Process Area", required=True, tracking=True)
    owning_module = fields.Char(string="Owning Module", help="For example M19 or M01.")
    volume_per_month = fields.Integer(string="Volume per Month", required=True, tracking=True)
    automated = fields.Boolean(string="Automated", tracking=True)
    automation_id = fields.Many2one(
        "fix.automation", string="Automated By", tracking=True, context={"active_test": False}
    )
    stp_rate = fields.Float(
        string="Straight-Through %",
        default=100.0,
        tracking=True,
        help="The share of the volume the automation completes with no human step.",
    )
    automated_volume = fields.Float(
        string="Automated Volume", compute="_compute_automated_volume", store=True
    )
    notes = fields.Text()
    active = fields.Boolean(default=True)
    last_reviewed_on = fields.Date(string="Last Reviewed", readonly=True, copy=False)
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"last_reviewed_on", "reviewed_by_id"}

    @api.depends("automated", "volume_per_month", "stp_rate")
    def _compute_automated_volume(self):
        for row in self:
            row.automated_volume = (
                row.volume_per_month * (row.stp_rate or 0.0) / 100.0 if row.automated else 0.0
            )

    @api.constrains("volume_per_month", "stp_rate", "automated", "automation_id")
    def _check_entry(self):
        for row in self:
            if row.volume_per_month <= 0:
                raise ValidationError(
                    "%s: the monthly volume must be above zero; a task that never "
                    "happens is not routine work." % row.name
                )
            if not 0.0 <= (row.stp_rate or 0.0) <= 100.0:
                raise ValidationError("%s: the straight-through share is 0-100%%." % row.name)
            if row.automated and not row.automation_id:
                raise ValidationError(
                    "%s is marked automated: name the automation (AUT register row) "
                    "that does it." % row.name
                )
            if row.automated and not row.automation_id.sudo().active:
                raise ValidationError(
                    "%s cannot count as automated by %s: that automation is "
                    "switched off." % (row.name, row.automation_id.sudo().code)
                )

    def action_mark_reviewed(self):
        self.check_access("write")
        for row in self:
            row._guarded().write(
                {
                    "last_reviewed_on": fields.Date.context_today(self),
                    "reviewed_by_id": self.env.uid,
                }
            )
        return True

    @api.model
    def _automation_rate(self):
        """(rate %, automated volume, total volume) over the active register."""
        rows = self.sudo().search([])
        total = sum(rows.mapped("volume_per_month"))
        automated = sum(rows.mapped("automated_volume"))
        return (round(automated / total * 100.0, 1) if total else 0.0, automated, total)


# =================================================== manual intervention
INTERVENTIONS = [
    ("complete", "Complete"),
    ("fail", "Mark Failed"),
    ("escalate", "Escalate"),
    ("terminate", "Terminate"),
]


class FixWorkflowIntervention(models.Model):
    """An operator's manual action on a workflow instance, recorded for good.

    FR-BPA-008 / BRU-BPA-23: only an authorised operator (a DoA Administrator
    or a Platform Admin) intervenes, always with a reason; the record is
    append-only (BRU-BPA-15). Spec §13: the operator cannot complete an
    instance they started themself - nobody unsticks a process into the
    outcome they wanted.
    """

    _name = "fix.workflow.intervention"
    _description = "Workflow Manual Intervention"
    _inherit = ["fix.guarded.mixin"]
    _order = "at desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    instance_id = fields.Many2one(
        "fix.workflow.instance",
        string="Workflow Instance",
        required=True,
        index=True,
        ondelete="restrict",
    )
    action = fields.Selection(INTERVENTIONS, string="Intervention", required=True)
    reason = fields.Text(required=True)
    operator_id = fields.Many2one("res.users", string="Operator", readonly=True)
    at = fields.Datetime(string="At", readonly=True)
    state_before = fields.Char(string="State Before", readonly=True)
    state_after = fields.Char(string="State After", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "operator_id",
            "at",
            "state_before",
            "state_after",
        }

    @api.model
    def _may_intervene(self):
        user = self.env.user
        return self.env.su or user.has_group(DOA_ADMIN) or user.has_group(PLATFORM_ADMIN)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._may_intervene():
            raise AccessError(
                "Only a DoA Administrator or a Platform Admin intervenes on a workflow instance."
            )
        Instance = self.env["fix.workflow.instance"].sudo()
        labels = dict(Instance._fields["state"].selection)
        prepared = []
        for vals in vals_list:
            reason = (vals.get("reason") or "").strip()
            if len(reason) < 10:
                raise UserError(
                    "State why the instance needs a manual intervention (at least a "
                    "sentence): the reason is kept with the record for audit."
                )
            instance = Instance.browse(vals.get("instance_id") or 0).exists()
            if not instance:
                raise UserError("Choose the workflow instance to intervene on.")
            action = vals.get("action")
            if action in ("complete", "fail", "terminate") and instance.state != "running":
                raise UserError(
                    "%s is %s: only a running instance can be %s."
                    % (
                        instance.name,
                        labels.get(instance.state, instance.state),
                        dict(INTERVENTIONS).get(action, action).lower(),
                    )
                )
            if action == "complete" and not self.env.su and instance.create_uid == self.env.user:
                raise UserError(
                    "You started %s: completing it by hand is for another operator "
                    "(segregation of duties)." % instance.name
                )
            vals.update(
                {
                    "reason": reason,
                    "company_id": vals.get("company_id") or instance.company_id.id,
                    "operator_id": self.env.uid,
                    "at": fields.Datetime.now(),
                    "state_before": labels.get(instance.state, instance.state),
                }
            )
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.workflow.intervention")
                    or "WFX/New"
                )
            prepared.append((vals, instance, action))
        records = super(FixWorkflowIntervention, self._guarded()).create(vals_list)
        for record, (_vals, instance, action) in zip(records, prepared, strict=True):
            instance._apply_intervention(action)
            record.sudo()._guarded().write(
                {"state_after": labels.get(instance.state, instance.state)}
            )
        return self.browse(records.ids)

    def write(self, vals):
        if self and not self._fix_guard_has_token():
            raise UserError("A manual intervention is recorded for good and never changed.")
        return super().write(vals)

    def unlink(self):
        raise UserError("A manual intervention is recorded for good and never deleted.")


class FixWorkflowInstance(models.Model):
    _inherit = "fix.workflow.instance"

    intervention_ids = fields.One2many(
        "fix.workflow.intervention", "instance_id", string="Interventions", readonly=True
    )
    intervention_count = fields.Integer(compute="_compute_intervention_count")

    @api.depends("intervention_ids")
    def _compute_intervention_count(self):
        for rec in self:
            rec.intervention_count = len(rec.sudo().intervention_ids)

    def _apply_intervention(self, action):
        """The transition itself; called only by a recorded intervention."""
        now = fields.Datetime.now()
        for rec in self.sudo():
            if action == "complete":
                rec._guarded().write({"state": "completed", "finished_at": now})
            elif action == "fail":
                rec._guarded().write({"state": "failed", "finished_at": now})
            elif action == "terminate":
                rec._guarded().write({"state": "cancelled", "finished_at": now})
            elif action == "escalate":
                rec._guarded().write({"escalated": True})

    def _intervene(self, action, reason):
        Intervention = self.env["fix.workflow.intervention"]
        if not Intervention._may_intervene():
            raise AccessError(
                "Only a DoA Administrator or a Platform Admin intervenes on a workflow instance."
            )
        for rec in self:
            Intervention.create({"instance_id": rec.id, "action": action, "reason": reason})
        return True

    # The monitor's buttons: every one is now a recorded intervention.
    def action_complete(self, reason=None):
        return self._intervene("complete", reason)

    def action_fail(self, reason=None):
        return self._intervene("fail", reason)

    def action_escalate(self, reason=None):
        return self._intervene("escalate", reason)

    def action_terminate(self, reason=None):
        return self._intervene("terminate", reason)
