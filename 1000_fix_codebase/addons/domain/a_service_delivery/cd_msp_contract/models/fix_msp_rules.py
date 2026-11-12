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

    def action_generate_monthly_report(self):
        """One report per contract and month: a second click made a second
        report of the same period, read twice by Client Reporting (the nightly
        run already skipped a period that had one)."""
        self.ensure_one()
        label = (fields.Date.today().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
        if self.env["fix.msp.service.report"].search_count(
            [("msp_contract_id", "=", self.id), ("period_label", "=", label)]
        ):
            raise UserError(
                "The %s service report of %s already exists - open it on Client Service "
                "Reviews (Regenerate Summary rewrites its text)." % (label, self.name)
            )
        return super().action_generate_monthly_report()
