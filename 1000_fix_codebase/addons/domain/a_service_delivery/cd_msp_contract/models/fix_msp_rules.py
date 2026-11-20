# fix_msp_rules — M05 capture audit (2026-11-13): what the sub-module pages
# "Metrics & Health Scoring", "Alerting Engine" and "MSP Service Desk" capture.
#
# Reported from the M05 workspace: those pages offered no data-capture button
# (or, on the Alerting Engine, the ticket form). The spec names three captures
# the estate had no input for:
#   FR-RMS-010/011  a health reading of an asset - agentless devices (SNMP,
#                   ICMP) and site checks are read by an engineer, not an agent
#   FR-RMS-015      alert rules: thresholds per metric, contract and severity
#                   (the "Alert Rules & Inbox" screen had no rule to show)
#   FR-RMS-026      client tickets by phone, email, portal or chat - an alert
#                   could only come from the collector
#
# A reading goes through the same path as the collector: the first unhealthy
# transition raises an alert unless a maintenance window suppresses it; then
# every active rule in scope is evaluated, one open alert per rule and asset
# (a flapping metric raises one alert, not fifty - spec T-10).
#
# FILE NAME IS LOAD-BEARING: imported last in models/__init__.py, after every
# file that defines the models it extends.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .msp_roles import GROUP_ENGINEER, require_role

METRICS = [
    ("cpu_utilization_pct", "CPU load (%)"),
    ("ram_utilization_pct", "Memory use (%)"),
    ("disk_free_gb", "Free disk (GB)"),
    ("uptime_hours", "Uptime since restart (hours)"),
]
PERCENT_METRICS = ("cpu_utilization_pct", "ram_utilization_pct")


class FixMspAlertRule(models.Model):
    """A threshold on one metric (FR-RMS-015). A rule scoped to a contract
    applies to that contract's estate only; an unscoped rule to every one."""

    _name = "fix.msp.alert.rule"
    _description = "MSP Alert Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "msp_contract_id, metric, id"

    name = fields.Char(string="Rule", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one(
        "fix.msp.contract",
        string="MSP Contract",
        index=True,
        ondelete="cascade",
        help="Empty: the rule applies to every MSP contract's estate.",
    )
    metric = fields.Selection(METRICS, required=True, tracking=True)
    operator = fields.Selection(
        [("above", "Above"), ("below", "Below")], required=True, default="above", tracking=True
    )
    threshold = fields.Float(required=True, tracking=True)
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major")], required=True, default="minor", tracking=True
    )
    active = fields.Boolean(default=True, tracking=True)
    alert_ids = fields.One2many("fix.msp.alert", "rule_id", string="Alerts Raised")
    alert_count = fields.Integer(compute="_compute_alert_count", string="Alerts Raised")

    @api.depends("alert_ids")
    def _compute_alert_count(self):
        for rule in self:
            rule.alert_count = len(rule.alert_ids)

    @api.constrains("metric", "threshold")
    def _check_threshold(self):
        for rule in self:
            if rule.threshold < 0:
                raise ValidationError("Rule %s: the threshold cannot be negative." % rule.name)
            if rule.metric in PERCENT_METRICS and rule.threshold > 100:
                raise ValidationError("Rule %s: a percentage threshold is at most 100." % rule.name)

    def _msp_breached(self, asset) -> bool:
        self.ensure_one()
        value = asset[self.metric] or 0.0
        if self.operator == "above":
            return value > self.threshold
        return value < self.threshold

    def _msp_message(self, asset) -> str:
        self.ensure_one()
        label = dict(METRICS)[self.metric]
        return "%s: %s %s %s (reading %s)" % (
            asset.hostname or asset.agent_id,
            label,
            dict(self._fields["operator"].selection)[self.operator].lower(),
            ("%g" % self.threshold),
            ("%g" % (asset[self.metric] or 0.0)),
        )


class FixMspAlertCapture(models.Model):
    _inherit = "fix.msp.alert"

    source = fields.Selection(
        [
            ("monitoring", "Monitoring (agent or rule)"),
            ("phone", "Phone"),
            ("email", "Email"),
            ("portal", "Client Portal"),
            ("chat", "Chat"),
        ],
        string="Reported Through",
        required=True,
        default="monitoring",
        help="Where the ticket came from (FR-RMS-026). A client report is "
        "logged on the MSP Service Desk; monitoring alerts are raised by the "
        "collector or an alert rule.",
    )
    rule_id = fields.Many2one(
        "fix.msp.alert.rule",
        string="Alert Rule",
        readonly=True,
        copy=False,
        ondelete="set null",
        help="The rule whose threshold the reading crossed. Set by the reading only.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"rule_id"}

    @api.constrains("asset_id", "msp_contract_id")
    def _check_asset_on_contract(self):
        # A ticket logged against an endpoint of another client's contract
        # would bill and report that client's incident to the wrong client.
        for alert in self:
            if alert.asset_id and alert.asset_id.msp_contract_id != alert.msp_contract_id:
                raise ValidationError(
                    "Asset %s is not covered by MSP contract %s - choose an asset of "
                    "the contract the ticket is logged under."
                    % (
                        alert.asset_id.hostname or alert.asset_id.agent_id,
                        alert.msp_contract_id.name,
                    )
                )


class FixMonitoredAssetReading(models.Model):
    _inherit = "fix.monitored.asset"

    last_reading_by_id = fields.Many2one(
        "res.users",
        string="Last Reading Recorded By",
        readonly=True,
        copy=False,
        help="Empty when the last reading came from the agent.",
    )

    def action_record_reading(
        self,
        health=None,
        cpu=None,
        ram=None,
        disk_free_gb=None,
        uptime_hours=None,
    ):
        """An engineer's reading of this asset: an agentless device (SNMP /
        ICMP) or a site check (FR-RMS-010/011). It updates the metrics and
        last_seen, then raises what the collector would: an alert on the first
        unhealthy transition, and one per alert rule the reading breaches -
        none while a maintenance window suppresses alerting."""
        self.ensure_one()
        require_role(self.env, [GROUP_ENGINEER], "Recording a health reading")
        health = health or self.health
        if health not in dict(self._fields["health"].selection):
            raise UserError("Health must be Healthy, Degraded or Offline.")
        metrics = {
            "cpu_utilization_pct": cpu,
            "ram_utilization_pct": ram,
            "disk_free_gb": disk_free_gb,
            "uptime_hours": uptime_hours,
        }
        vals = {}
        for name, raw in metrics.items():
            if raw in (None, "", False):
                continue
            try:
                value = float(raw)
            except (TypeError, ValueError) as err:
                raise UserError("%s: a number is required." % self._fields[name].string) from err
            if value < 0 or (name in PERCENT_METRICS and value > 100):
                raise UserError(
                    "%s: %g is not a possible reading." % (self._fields[name].string, value)
                )
            vals[name] = value
        if not vals and health == self.health:
            raise UserError("Enter at least one reading: health or a metric.")

        became_unhealthy = health != "healthy" and self.health == "healthy"
        now = fields.Datetime.now()
        vals.update({"health": health, "last_seen": now, "last_reading_by_id": self.env.uid})
        self.write(vals)
        self.message_post(body="Health reading recorded by %s." % self.env.user.name)

        if self.env["fix.msp.maintenance.window"].alerting_suppressed(self):
            if became_unhealthy or self._msp_breached_rules():
                publish(
                    self.env,
                    "msp.alert_suppressed_window",
                    "fix.monitored.asset",
                    self.id,
                    {"agent": self.agent_id, "health": health},
                )
            return {"warning": "Reading recorded. A maintenance window is open: no alert raised."}

        Alert = self.env["fix.msp.alert"]
        raised = Alert
        if became_unhealthy:
            raised |= Alert.create(
                {
                    "msp_contract_id": self.msp_contract_id.id,
                    "asset_id": self.id,
                    "severity": "major" if health == "offline" else "minor",
                    "message": "%s became %s" % (self.hostname or self.agent_id, health),
                }
            )
        for rule in self._msp_breached_rules():
            already = Alert.search_count(
                [
                    ("asset_id", "=", self.id),
                    ("rule_id", "=", rule.id),
                    ("state", "!=", "resolved"),
                ]
            )
            if already:
                continue
            raised |= (
                Alert._guarded()
                .create(
                    {
                        "msp_contract_id": self.msp_contract_id.id,
                        "asset_id": self.id,
                        "severity": rule.severity,
                        "message": rule._msp_message(self),
                        "rule_id": rule.id,
                    }
                )
                .with_env(self.env)
            )
        for alert in raised:
            publish(
                self.env,
                "msp.alert_raised",
                "fix.msp.alert",
                alert.id,
                {"agent": self.agent_id, "health": health},
            )
        if raised:
            return {
                "warning": "Reading recorded. %d alert(s) raised - see Alert Rules & Inbox."
                % len(raised)
            }
        return {"note": "Reading recorded. No threshold crossed."}

    def _msp_breached_rules(self):
        """Active rules in scope (this contract's, or unscoped) that the
        current reading breaches."""
        self.ensure_one()
        rules = self.env["fix.msp.alert.rule"].search(
            [
                ("company_id", "in", [self.company_id.id]),
                "|",
                ("msp_contract_id", "=", False),
                ("msp_contract_id", "=", self.msp_contract_id.id),
            ]
        )
        return rules.filtered(lambda r: r._msp_breached(self))


class FixMspContractReportOnce(models.Model):
    _inherit = "fix.msp.contract"

    def action_generate_monthly_report(self, period=None):
        """One report per contract and month: a second click made a second
        report of the same period, read twice by Client Reporting (the nightly
        run already skipped a period that had one). A02 ERP pass 2 (M05-S01):
        the check is in action_monthly_report, which recomputes a report that
        has no attainment figure instead of refusing it."""
        self.ensure_one()
        return super().action_generate_monthly_report(period=period)


# ---------------------------------------------------------------------------
# M05 bidirectional audit (2026-11-13)
# ---------------------------------------------------------------------------

COVERAGE_GAP_HOURS = 24
EVIDENCE_MIN = 10


class FixMspChangeRecordRollback(models.Model):
    _inherit = "fix.msp.change.record"

    def _msp_check_rollback(self):
        """BRU-RMS-08: a change to a client environment needs a rollback plan,
        whatever its risk. The check demanded one only for high risk, so a
        medium-risk firewall change could be approved and implemented with
        no way back. A problem record is analysis, not a change: exempt."""
        if self.kind == "change" and not (self.rollback_plan or "").strip():
            raise UserError(
                "Change %s has no rollback plan: document the backout and rollback "
                "plan before it is approved or implemented (BRU-RMS-08)." % self.name
            )


class FixMspRunbookLog(models.Model):
    _inherit = "fix.msp.runbook"

    def _msp_log_run(self, target, alert=None, outcome="success", evidence=""):
        """Record one execution of this runbook on ``target`` (spec T-08:
        target, outcome and output). A failed execution never resolves the
        alert; a successful one resolves it only when the runbook says so and
        the evidence is written down."""
        self.ensure_one()
        evidence = (evidence or "").strip()
        if not self.active:
            raise UserError("Runbook %s is archived — reactivate it first" % self.name)
        if outcome not in ("success", "failed"):
            raise UserError("The outcome of an execution is Success or Failed.")
        asset_name = target.hostname or target.agent_id
        if self.scope_contract_id and target.msp_contract_id != self.scope_contract_id:
            raise UserError(
                "Runbook %s is scoped to %s; asset %s belongs to %s."
                % (
                    self.name,
                    self.scope_contract_id.name,
                    asset_name,
                    target.msp_contract_id.name,
                )
            )
        if alert and alert.asset_id != target:
            raise UserError(
                "The alert was raised on %s, not on %s: log the execution on the "
                "asset the alert is about."
                % (alert.asset_id.hostname or alert.asset_id.agent_id, asset_name)
            )
        if outcome == "failed" and len(evidence) < EVIDENCE_MIN:
            raise UserError(
                "Write what failed in the execution of %s (at least %d characters)."
                % (self.name, EVIDENCE_MIN)
            )
        if outcome == "success" and self.auto_resolve_alert and len(evidence) < EVIDENCE_MIN:
            raise UserError(
                "Runbook %s resolves the asset's alert: record the evidence of the "
                "execution (what the steps showed, at least %d characters)."
                % (self.name, EVIDENCE_MIN)
            )
        now = fields.Datetime.now()
        run = (
            self.env["fix.msp.runbook.run"]
            ._guarded()
            .create(
                {
                    "runbook_id": self.id,
                    "asset_id": target.id,
                    "alert_id": alert.id if alert else False,
                    "outcome": outcome,
                    "state": outcome,
                    "started_at": now,
                    "finished_at": now,
                    "output_note": evidence or "Executed via workspace/ops console",
                    "operating_unit_id": self.operating_unit_id.id or False,
                }
            )
            .with_env(self.env)
        )
        if outcome == "success" and self.auto_resolve_alert:
            if not alert:
                alert = self.env["fix.msp.alert"].search(
                    [("asset_id", "=", target.id), ("state", "in", ("new", "acked"))], limit=1
                )
            # BRU-RMS-10: a recurring incident with no problem record stays open
            if alert and alert.state in ("new", "acked") and not alert._msp_needs_problem():
                alert.action_resolve(
                    note="Runbook '%s' executed (run #%s): %s" % (self.name, run.id, evidence)
                )
        publish(
            self.env,
            "msp.runbook_executed",
            "fix.msp.runbook.run",
            run.id,
            {"runbook": self.name, "asset": target.agent_id},
        )
        return run

    def action_execute(self, asset=None, alert_id=None, evidence=None, outcome="success"):
        """Record an execution against an EXPLICIT asset: the one named (id,
        agent id or hostname), else the alert's own asset, else the scope's
        only asset. It fell back to the first asset in scope, so an execution
        with evidence but no asset was logged on whatever device sorted
        first, and an alert's execution on another device than the alert's."""
        Asset = self.env["fix.monitored.asset"]
        alert = None
        if alert_id:
            alert = self.env["fix.msp.alert"].browse(int(alert_id)).exists()
            if not alert:
                raise UserError("Alert %s does not exist" % alert_id)
        for book in self:
            if isinstance(asset, str) and asset.strip():
                target = Asset.search(
                    ["|", ("agent_id", "=", asset.strip()), ("hostname", "=", asset.strip())],
                    limit=1,
                )
                if not target:
                    raise UserError("No monitored asset matches '%s'" % asset)
            elif isinstance(asset, int) and asset:
                target = Asset.browse(asset).exists()
                if not target:
                    raise UserError("Monitored asset %s does not exist" % asset)
            elif alert:
                target = alert.asset_id
            else:
                domain = (
                    [("msp_contract_id", "=", book.scope_contract_id.id)]
                    if book.scope_contract_id
                    else []
                )
                target = Asset.search(domain, limit=2)
                if len(target) != 1:
                    raise UserError(
                        "Name the asset the runbook %s was executed on%s."
                        % (book.name, "" if target else " (no monitored asset is in its scope)")
                    )
            book._msp_log_run(target, alert=alert, outcome=outcome, evidence=evidence)
        return True


class FixMspRunbookRunLog(models.Model):
    _inherit = "fix.msp.runbook.run"

    outcome = fields.Selection(
        [("success", "Success"), ("failed", "Failed")],
        string="Outcome",
        default="success",
        help="What the operator reports the execution achieved. Set when the "
        "execution is logged; the log is evidence and does not change after.",
    )
    logged_by_id = fields.Many2one(
        "res.users",
        string="Logged By",
        default=lambda self: self.env.user,
        readonly=True,
        copy=False,
        help="Who logged the execution: the engineer accountable for it (T-08).",
    )

    _LOGGED = ("runbook_id", "asset_id", "alert_id", "outcome", "output_note", "logged_by_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._LOGGED)

    def _fix_form_locked_fields(self) -> set:
        # a NEW execution is typed on the form; a logged one is evidence
        if not self:
            return {"state", "started_at", "finished_at"}
        return super()._fix_form_locked_fields()

    @api.model_create_multi
    def create(self, vals_list):
        """An execution typed on the workspace form goes through the same
        checks as the runbook's own button (scope, alert on the asset,
        evidence, alert resolution, event)."""
        if self._fix_guard_open():
            return super().create(vals_list)
        require_role(self.env, [GROUP_ENGINEER], "Logging a runbook execution")
        runs = self.browse()
        for vals in vals_list:
            book = self.env["fix.msp.runbook"].browse(vals.get("runbook_id") or 0).exists()
            target = self.env["fix.monitored.asset"].browse(vals.get("asset_id") or 0).exists()
            if not book or not target:
                raise UserError("Choose the runbook and the asset it was executed on.")
            alert = self.env["fix.msp.alert"].browse(vals.get("alert_id") or 0).exists() or None
            runs |= book._msp_log_run(
                target,
                alert=alert,
                outcome=vals.get("outcome") or "success",
                evidence=vals.get("output_note") or "",
            )
        return runs


class FixMspAlertCoverage(models.Model):
    _inherit = "fix.msp.alert"

    coverage_gap = fields.Boolean(
        string="Coverage Gap",
        readonly=True,
        copy=False,
        help="Raised because the asset's agent has not reported for 24 hours "
        "(BRU-RMS-04). Set by the coverage check only.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"coverage_gap"}


class FixMonitoredAssetCoverage(models.Model):
    _inherit = "fix.monitored.asset"

    @api.model
    def cron_coverage_gaps(self):
        """BRU-RMS-04: an asset whose agent has not reported for 24 hours is a
        coverage gap - a contractual failure, reported within the 24 hours.
        One open gap alert per asset; none while a maintenance window
        suppresses alerting. An asset never seen counts from its enrolment."""
        cutoff = fields.Datetime.now() - timedelta(hours=COVERAGE_GAP_HOURS)
        # A02 ERP pass 2 (M05-S07): an agent recorded as removed is not a gap,
        # and a contract no longer in service (offboarding / offboarded) or
        # whose M08 term is not in force raises nothing
        stale = self.sudo().search(
            [
                ("agent_removed_at", "=", False),
                ("msp_contract_id.lifecycle", "=", "in_service"),
                "|",
                ("last_seen", "<", cutoff),
                "&",
                ("last_seen", "=", False),
                ("create_date", "<", cutoff),
            ]
        )
        stale = stale.filtered(lambda a: not a.msp_contract_id._msp_entitlement_denial())
        Alert = self.env["fix.msp.alert"].sudo()
        Window = self.env["fix.msp.maintenance.window"].sudo()
        raised = 0
        for asset in stale:
            if Alert.search_count(
                [
                    ("asset_id", "=", asset.id),
                    ("coverage_gap", "=", True),
                    ("state", "!=", "resolved"),
                ]
            ):
                continue
            if Window.alerting_suppressed(asset):
                continue
            seen = (
                "last reported %s UTC" % fields.Datetime.to_string(asset.last_seen)
                if asset.last_seen
                else "never reported since enrolment"
            )
            alert = Alert._guarded().create(
                {
                    # the contract's company / OU (A02 ERP pass 2, M05-S11)
                    "msp_contract_id": asset.msp_contract_id.id,
                    "asset_id": asset.id,
                    "severity": "major",
                    "coverage_gap": True,
                    "message": "Coverage gap: %s has no agent report for %d hours (%s)"
                    % (asset.hostname or asset.agent_id, COVERAGE_GAP_HOURS, seen),
                }
            )
            publish(
                self.env,
                "msp.alert_raised",
                "fix.msp.alert",
                alert.id,
                {"agent": asset.agent_id, "health": asset.health},
            )
            raised += 1
        return raised


class FixMspBackupJob(models.Model):
    """FR-RMS-039 backup service oversight: one backup job outcome (and
    whether a restore was tested) on a client asset. The "Backup & Restore
    Test Log" report said "not built yet"; it now reads these. A job is
    evidence: recorded once, never edited."""

    _name = "fix.msp.backup.job"
    _description = "MSP Backup Job"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "run_at desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    asset_id = fields.Many2one("fix.monitored.asset", string="Asset", required=True, index=True)
    msp_contract_id = fields.Many2one(
        related="asset_id.msp_contract_id", store=True, string="MSP Contract", index=True
    )
    plan_ref = fields.Char(string="Backup Plan / Job", required=True)
    run_at = fields.Datetime(string="Run At", required=True, default=fields.Datetime.now)
    outcome = fields.Selection(
        [("success", "Succeeded"), ("partial", "Partial"), ("failed", "Failed")],
        required=True,
        default="success",
    )
    restore_tested = fields.Boolean(
        string="Restore Tested", help="A restore was performed and the data read back."
    )
    note = fields.Text(string="Note")
    alert_id = fields.Many2one(
        "fix.msp.alert", string="Alert Raised", readonly=True, copy=False, ondelete="set null"
    )
    consecutive_failures = fields.Integer(
        string="Failures in a Row",
        compute="_compute_consecutive_failures",
        help="Failed or partial jobs of this plan on this asset since its last success, "
        "counting this one.",
    )

    _LOGGED = ("asset_id", "plan_ref", "run_at", "outcome", "restore_tested", "note", "alert_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._LOGGED)

    def _fix_form_locked_fields(self) -> set:
        if not self:
            return {"alert_id"}
        return super()._fix_form_locked_fields()

    @api.depends("asset_id", "plan_ref", "run_at", "outcome")
    def _compute_consecutive_failures(self):
        for job in self:
            if not job.id or not job.asset_id:
                job.consecutive_failures = 0 if job.outcome == "success" else 1
                continue
            history = self.search(
                [
                    ("asset_id", "=", job.asset_id.id),
                    ("plan_ref", "=", job.plan_ref),
                    ("run_at", "<=", job.run_at),
                ],
                order="run_at desc, id desc",
            )
            count = 0
            for past in history:
                if past.outcome == "success":
                    break
                count += 1
            job.consecutive_failures = count

    @api.constrains("run_at")
    def _check_run_at(self):
        for job in self:
            if job.run_at and job.run_at > fields.Datetime.now() + timedelta(minutes=5):
                raise ValidationError("A backup job cannot be recorded for a future time.")

    @api.model_create_multi
    def create(self, vals_list):
        if self._fix_guard_open():
            return super().create(vals_list)
        require_role(self.env, [GROUP_ENGINEER], "Recording a backup job")
        for vals in vals_list:
            if (
                vals.get("outcome", "success") != "success"
                and len((vals.get("note") or "").strip()) < EVIDENCE_MIN
            ):
                raise UserError(
                    "Write what failed in the backup job (at least %d characters)." % EVIDENCE_MIN
                )
        # validated above: the logged fields are written once, here
        jobs = super(FixMspBackupJob, self._guarded()).create(vals_list).with_env(self.env)
        for job in jobs:
            job._msp_alert_on_failure()
        return jobs

    def _msp_alert_on_failure(self):
        """A failed or partial job raises one alert on its asset (driving the
        remediation), unless a maintenance window suppresses alerting or an
        alert for this plan is still open."""
        self.ensure_one()
        if self.outcome == "success":
            return
        Alert = self.env["fix.msp.alert"]
        if self.env["fix.msp.maintenance.window"].alerting_suppressed(self.asset_id):
            return
        open_alert = self.search(
            [
                ("asset_id", "=", self.asset_id.id),
                ("plan_ref", "=", self.plan_ref),
                ("alert_id.state", "!=", "resolved"),
                ("id", "!=", self.id),
            ],
            limit=1,
        ).alert_id
        if open_alert:
            self._guarded().write({"alert_id": open_alert.id})
            return
        label = dict(self._fields["outcome"].selection)[self.outcome].lower()
        alert = Alert.create(
            {
                # the contract's company / OU (A02 ERP pass 2, M05-S11)
                "msp_contract_id": self.asset_id.msp_contract_id.id,
                "asset_id": self.asset_id.id,
                "severity": "major" if self.outcome == "failed" else "minor",
                "message": "Backup %s on %s: %s"
                % (label, self.asset_id.hostname or self.asset_id.agent_id, self.plan_ref),
            }
        )
        self._guarded().write({"alert_id": alert.id})
        publish(
            self.env,
            "msp.alert_raised",
            "fix.msp.alert",
            alert.id,
            {"agent": self.asset_id.agent_id, "health": self.asset_id.health},
        )
