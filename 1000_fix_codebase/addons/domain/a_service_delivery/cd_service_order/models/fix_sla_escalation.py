# M01 capture audit (2026-11-17): the SLA escalation matrix.
#
# FR-SRM-049 asks for escalations "at 50%, 75%, 90% and 100% of SLA to
# defined roles, with acknowledgement tracking", and the spec lists
# fix.escalation.rule (sla_policy_id, threshold_pct, role_id, action) among
# M01's owned entities. The estate had one near-breach warning per SLA item
# and one breach to-do for the branch's Service Supervisors - no matrix, no
# role per level and nothing to acknowledge. The "Escalation Rules" screen
# listed SLA POLICIES (with a mail template column), so the page could not
# capture a rule because no rule record existed.
#
# A rule says: on this policy (optionally one KPI of it), when the clock has
# used <threshold>% of its target, escalate to the holders of <role> in the
# record's branch. The SLA cron raises a fix.escalation.event once per rule
# per clock SERIES (a pause/resume creates a successor instance; it must not
# escalate the same level again), gives each holder a to-do, and keeps the
# event open until one of them acknowledges it.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

SLA_SUPERVISOR_GROUP = "cd_service_order.group_so_supervisor"
# a breached clock is still escalated by a 100% rule; looking further back
# than a day would rescan every breach the estate ever had (T-07)
BREACH_LOOKBACK = timedelta(days=1)


class FixEscalationRule(models.Model):
    """One level of an SLA policy's escalation matrix."""

    _name = "fix.escalation.rule"
    _description = "SLA Escalation Rule"
    _order = "policy_id, threshold_pct, sequence, id"

    policy_id = fields.Many2one(
        "fix.sla.policy", string="SLA Policy", required=True, ondelete="cascade", index=True
    )
    kpi_code = fields.Char(
        string="KPI Code",
        help="Only clocks measuring this KPI (e.g. 'resolution'). Empty: every clock of the policy.",
    )
    threshold_pct = fields.Integer(
        string="Escalate At % Of Target",
        required=True,
        default=75,
        help="The share of the target, in business time, the clock has used. "
        "The spec's matrix is 50, 75, 90 and 100 (breach).",
    )
    group_id = fields.Many2one(
        "res.groups",
        string="Escalate To (Role)",
        required=True,
        ondelete="restrict",
        help="Every active holder of this role in the record's branch gets a to-do.",
    )
    requires_ack = fields.Boolean(
        string="Acknowledgement Required",
        default=True,
        help="The escalation stays open until one of the notified people acknowledges it.",
    )
    note = fields.Text(string="Instruction To The Escalation Owner")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(related="policy_id.company_id", store=True, index=True)

    @api.depends("policy_id", "threshold_pct", "group_id", "kpi_code")
    def _compute_display_name(self):
        for rule in self:
            rule.display_name = "%s %s%% -> %s%s" % (
                rule.policy_id.code or "",
                rule.threshold_pct or 0,
                rule.group_id.name or "",
                " (%s)" % rule.kpi_code if rule.kpi_code else "",
            )

    @api.constrains("threshold_pct")
    def _check_threshold(self):
        for rule in self:
            if not 1 <= rule.threshold_pct <= 100:
                raise ValidationError(
                    "An escalation threshold is a share of the SLA target: 1 to 100 percent "
                    "(100 = at breach)."
                )

    @api.constrains("policy_id", "kpi_code", "threshold_pct", "group_id", "active")
    def _check_unique_level(self):
        for rule in self.filtered("active"):
            twin = self.search_count(
                [
                    ("id", "!=", rule.id),
                    ("active", "=", True),
                    ("policy_id", "=", rule.policy_id.id),
                    ("kpi_code", "=", rule.kpi_code or False),
                    ("threshold_pct", "=", rule.threshold_pct),
                    ("group_id", "=", rule.group_id.id),
                ]
            )
            if twin:
                raise ValidationError(
                    "Policy %s already escalates to %s at %s%%."
                    % (rule.policy_id.code, rule.group_id.name, rule.threshold_pct)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("kpi_code"):
                vals["kpi_code"] = vals["kpi_code"].strip()
        return super().create(vals_list)


class FixSlaPolicyEscalation(models.Model):
    _inherit = "fix.sla.policy"

    escalation_rule_ids = fields.One2many(
        "fix.escalation.rule", "policy_id", string="Escalation Matrix"
    )


class FixEscalationEvent(models.Model):
    """An escalation the SLA clock raised: who was told, and who acknowledged."""

    _name = "fix.escalation.event"
    _description = "SLA Escalation Raised"
    _order = "fired_at desc, id desc"

    rule_id = fields.Many2one(
        "fix.escalation.rule", string="Rule", required=True, ondelete="restrict", index=True
    )
    instance_id = fields.Many2one(
        "fix.sla.kpi.instance", string="SLA Clock", required=True, ondelete="cascade", index=True
    )
    series_root_id = fields.Many2one(
        "fix.sla.kpi.instance",
        string="Clock Series",
        required=True,
        ondelete="cascade",
        index=True,
        help="The first instance of the pause/resume chain: one escalation per level per chain.",
    )
    policy_id = fields.Many2one(related="rule_id.policy_id", store=True, string="SLA Policy")
    group_id = fields.Many2one(related="rule_id.group_id", store=True, string="Escalated To")
    res_model = fields.Char(string="Record Model", required=True, index=True)
    res_id = fields.Integer(string="Record ID", required=True, index=True)
    record_ref = fields.Char(string="Record")
    kpi_code = fields.Char(string="KPI")
    threshold_pct = fields.Integer(string="Level %")
    elapsed_pct = fields.Float(string="Target Used %", digits=(6, 1))
    fired_at = fields.Datetime(string="Raised At", required=True, index=True)
    notified_user_ids = fields.Many2many("res.users", string="Notified")
    state = fields.Selection(
        [
            ("open", "Awaiting Acknowledgement"),
            ("acknowledged", "Acknowledged"),
            ("no_owner", "No Role Holder In Branch"),
            ("info", "Notified (No Acknowledgement Needed)"),
        ],
        required=True,
        default="open",
        index=True,
    )
    acknowledged_by = fields.Many2one("res.users", string="Acknowledged By")
    acknowledged_at = fields.Datetime(string="Acknowledged At")
    ack_note = fields.Text(string="Acknowledgement Note")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    _one_per_level = models.Constraint(
        "UNIQUE (series_root_id, rule_id)",
        "This escalation level was already raised for this SLA clock.",
    )

    @api.depends("record_ref", "threshold_pct", "kpi_code")
    def _compute_display_name(self):
        for event in self:
            event.display_name = "%s %s%% (%s)" % (
                event.record_ref or "",
                event.threshold_pct or 0,
                event.kpi_code or "",
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError(
                "An escalation is raised by the SLA clock when it reaches a rule's level; "
                "it is never typed in."
            )
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError(
                "An escalation is evidence of who was told and when: it changes only by "
                "Acknowledge."
            )
        return super().write(vals)

    def action_acknowledge(self, note=None):
        """One of the notified people (or a Service Supervisor) takes it."""
        user = self.env.user
        for event in self:
            if event.state != "open":
                raise UserError(
                    "Escalation %s is not awaiting acknowledgement." % event.display_name
                )
            if user not in event.notified_user_ids and not user.has_group(SLA_SUPERVISOR_GROUP):
                raise AccessError(
                    "Only a person this escalation was sent to, or a Service Supervisor, "
                    "can acknowledge it."
                )
            now = fields.Datetime.now()
            event.sudo().write(
                {
                    "state": "acknowledged",
                    "acknowledged_by": user.id,
                    "acknowledged_at": now,
                    "ack_note": (note or "").strip() or False,
                }
            )
            record = event._fix_record()
            if record is not None:
                activities = (
                    self.env["mail.activity"]
                    .sudo()
                    .search(
                        [
                            ("res_model", "=", event.res_model),
                            ("res_id", "=", event.res_id),
                            ("summary", "=", event._fix_summary()),
                        ]
                    )
                )
                if activities:
                    activities.action_feedback(
                        feedback="Acknowledged by %s%s"
                        % (user.name, ": %s" % note.strip() if note and note.strip() else "")
                    )
                if hasattr(record, "message_post"):
                    record.sudo().message_post(
                        body="SLA escalation %s%% acknowledged by %s."
                        % (event.threshold_pct, user.name)
                    )
        return True

    def _fix_record(self):
        self.ensure_one()
        if self.res_model not in self.env:
            return None
        record = self.env[self.res_model].sudo().browse(self.res_id).exists()
        return record or None

    def _fix_summary(self):
        self.ensure_one()
        return "SLA escalation %s%%: %s (%s)" % (
            self.threshold_pct,
            self.record_ref or "",
            self.kpi_code or "",
        )


class FixSlaKpiInstanceEscalation(models.Model):
    _inherit = "fix.sla.kpi.instance"

    escalation_event_ids = fields.One2many(
        "fix.escalation.event", "instance_id", string="Escalations Raised"
    )

    @api.model
    def cron_flag_breaches(self):
        """The existing breach/near-breach pass, then the escalation matrix.
        One cron (data/fix_sla_instance_cron.xml) drives both."""
        result = super().cron_flag_breaches()
        result["escalated"] = self._fire_escalation_rules()
        return result

    def _fix_series_root(self):
        self.ensure_one()
        root, seen = self, {self.id}
        while root.supersedes_id and root.supersedes_id.id not in seen:
            root = root.supersedes_id
            seen.add(root.id)
        return root

    def _fix_elapsed_pct(self, now):
        """Share of the target used, in business time, across the whole
        series: a successor keeps the original target_hours and a target_at
        moved by the hold, so the remaining time says how much was used."""
        self.ensure_one()
        if self.state == "breached" or now >= self.target_at:
            return 100.0
        target_minutes = (self.target_hours or 0.0) * 60.0
        if target_minutes <= 0:
            return 100.0
        remaining = self.business_minutes_between(now, self.target_at, self.calendar_id or None)
        used = max(0.0, target_minutes - remaining)
        return round(min(100.0, used / target_minutes * 100.0), 1)

    def _fix_escalation_users(self, record, group):
        if not group:
            return self.env["res.users"]
        if record is not None and hasattr(record, "_fix_branch_users"):
            return record._fix_branch_users(group)
        company = self.company_id
        return group.sudo().all_user_ids.filtered(
            lambda u: u.active and not u.share and company in u.company_ids
        )

    @api.model
    def _fire_escalation_rules(self, now=None):
        rules = self.env["fix.escalation.rule"].sudo().search([("active", "=", True)])
        if not rules:
            return 0
        now = now or fields.Datetime.now()
        instances = self.sudo().search(
            [
                ("policy_id", "in", rules.policy_id.ids),
                "|",
                ("state", "=", "in_progress"),
                "&",
                ("state", "=", "breached"),
                ("breached_at", ">=", now - BREACH_LOOKBACK),
            ]
        )
        Event = self.env["fix.escalation.event"].sudo()
        fired = 0
        for inst in instances:
            applicable = rules.filtered(
                lambda r, i=inst: r.policy_id == i.policy_id
                and (not r.kpi_code or r.kpi_code == i.kpi_code)
            )
            if not applicable:
                continue
            record = None
            if inst.res_model in self.env:
                record = self.env[inst.res_model].sudo().browse(inst.res_id).exists() or None
            if record is None:
                continue
            if inst.res_model == "fix.service.order" and record.state in (
                "delivered",
                "closed",
                "cancelled",
            ):
                continue
            pct = inst._fix_elapsed_pct(now)
            root = inst._fix_series_root()
            raised = set(Event.search([("series_root_id", "=", root.id)]).rule_id.ids)
            for rule in applicable.sorted("threshold_pct"):
                if rule.threshold_pct > pct or rule.id in raised:
                    continue
                users = inst._fix_escalation_users(record, rule.group_id)
                state = "open" if rule.requires_ack else "info"
                if not users:
                    state = "no_owner"
                event = Event.create(
                    {
                        "rule_id": rule.id,
                        "instance_id": inst.id,
                        "series_root_id": root.id,
                        "res_model": inst.res_model,
                        "res_id": inst.res_id,
                        "record_ref": record.display_name,
                        "kpi_code": inst.kpi_code,
                        "threshold_pct": rule.threshold_pct,
                        "elapsed_pct": pct,
                        "fired_at": now,
                        "notified_user_ids": [(6, 0, users.ids)],
                        "state": state,
                        "company_id": inst.company_id.id,
                    }
                )
                summary = event._fix_summary()
                note = "Target used: %.1f%% (deadline %s). %s" % (
                    pct,
                    inst.target_at,
                    rule.note or "",
                )
                if users and hasattr(record, "activity_schedule"):
                    for user in users:
                        record.activity_schedule(
                            "mail.mail_activity_data_todo",
                            summary=summary,
                            note=note.strip(),
                            user_id=user.id,
                        )
                elif hasattr(record, "message_post"):
                    record.message_post(
                        body="%s. No holder of %s in this branch to escalate to."
                        % (summary, rule.group_id.name)
                    )
                publish(
                    self.env,
                    "sla.escalated",
                    "fix.escalation.event",
                    event.id,
                    {
                        "res_model": inst.res_model,
                        "res_id": inst.res_id,
                        "kpi": inst.kpi_code,
                        "policy": inst.policy_id.code,
                        "threshold_pct": rule.threshold_pct,
                        "elapsed_pct": pct,
                        "notified": len(users),
                    },
                )
                raised.add(rule.id)
                fired += 1
        return fired
