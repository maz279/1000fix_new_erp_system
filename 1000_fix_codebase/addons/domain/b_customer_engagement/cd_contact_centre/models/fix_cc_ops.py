# M27 Contact Centre operations: queues, dispositions, routing rules, IVR
# flows, outbound lists, notification templates, QA evaluations and WFM
# shifts. Each is a real configuration/record model the workspace screens and
# the service-level / AHT / QA reports read.
import math
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

CHANNELS = [
    ("voice", "Voice (hotline 16743)"),
    ("whatsapp", "WhatsApp"),
    ("chat", "Web Chat"),
    ("email", "E-mail"),
    ("in_app", "In-App"),
]


class FixCcQueue(models.Model):
    _name = "fix.cc.queue"
    _description = "Contact Centre Queue"
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    channel = fields.Selection(CHANNELS, required=True, default="voice")
    target_answer_seconds = fields.Integer(string="Service-Level Target (s)", default=20)
    active = fields.Boolean(default=True)
    max_agent_concurrency = fields.Integer(
        string="Max Agent Concurrency", default=1, help="Max simultaneous interactions per agent"
    )
    wrapup_seconds = fields.Integer(
        string="Wrap-Up Grace Period (s)",
        default=60,
        help="Grace time after call before new call routing",
    )

    # --- REQ-27.4 Erlang-C capacity & abandonment alerting ---------------
    abandonment_alert_pct = fields.Float(
        string="Abandonment Alert Threshold (%)",
        default=5.0,
        help="REQ-27.4: above this abandonment rate the duty supervisor is alerted.",
    )
    queue_wait_alert_seconds = fields.Integer(
        string="Queue Wait Alert Threshold (s)",
        default=60,
        help="REQ-27.4: above this average wait the duty supervisor is alerted.",
    )

    @api.model
    def erlang_c_probability(self, arrival_rate_per_sec, aht_seconds, agents):
        """P_w — the chance an arriving call has to wait.

            A = lambda * AHT                     (offered load, in Erlangs)
            P_w = (A^N/N! * N/(N-A)) / (sum_{k<N} A^k/k! + A^N/N! * N/(N-A))

        Returns 1.0 when N <= A: an understaffed queue is unstable and every
        caller eventually waits.
        """
        load = float(arrival_rate_per_sec) * float(aht_seconds)
        n = int(agents)
        if n <= 0:
            return 1.0
        if load <= 0:
            return 0.0
        if n <= load:
            return 1.0
        top = (load**n / math.factorial(n)) * (n / (n - load))
        bottom = sum(load**k / math.factorial(k) for k in range(n)) + top
        return top / bottom if bottom else 1.0

    @api.model
    def erlang_c_asa(self, arrival_rate_per_sec, aht_seconds, agents):
        """Average Speed of Answer = P_w * AHT / (N - A)."""
        load = float(arrival_rate_per_sec) * float(aht_seconds)
        n = int(agents)
        if n <= load:
            return float("inf")
        pw = self.erlang_c_probability(arrival_rate_per_sec, aht_seconds, agents)
        return pw * float(aht_seconds) / (n - load)

    def required_agents(self, arrival_rate_per_sec, aht_seconds, max_wait_probability=0.20):
        """Smallest N that holds P_w at or under the target (default 20%,
        i.e. the 80/20 service level this hotline is sized to)."""
        self.ensure_one()
        load = float(arrival_rate_per_sec) * float(aht_seconds)
        n = max(1, int(math.floor(load)) + 1)
        while n < 500:
            if (
                self.erlang_c_probability(arrival_rate_per_sec, aht_seconds, n)
                <= max_wait_probability
            ):
                return n
            n += 1
        return n

    def evaluate_service_level(self, window_minutes=60):
        """REQ-27.4: measure the live queue and alert the duty supervisor when
        average wait or abandonment breaches its threshold."""
        since = fields.Datetime.now() - timedelta(minutes=window_minutes)
        results = []
        for queue in self:
            convs = self.env["fix.conversation"].search(
                [("queue_id", "=", queue.id), ("started_at", ">=", since)]
            )
            total = len(convs)
            abandoned = len(convs.filtered(lambda c: c.state == "abandoned"))
            waits = [
                c.queued_at and c.answered_at and (c.answered_at - c.queued_at).total_seconds()
                for c in convs
            ]
            waits = [w for w in waits if w]
            avg_wait = sum(waits) / len(waits) if waits else 0.0
            abandon_pct = (abandoned / total * 100.0) if total else 0.0
            breaches = []
            if avg_wait > queue.queue_wait_alert_seconds:
                breaches.append(
                    "average wait %.0fs exceeds %ds" % (avg_wait, queue.queue_wait_alert_seconds)
                )
            if abandon_pct > queue.abandonment_alert_pct:
                breaches.append(
                    "abandonment %.1f%% exceeds %.1f%%" % (abandon_pct, queue.abandonment_alert_pct)
                )
            if breaches:
                publish(
                    self.env,
                    "contact_centre.service_level_breach",
                    "fix.cc.queue",
                    queue.id,
                    {
                        "queue": queue.name,
                        "calls": total,
                        "avg_wait_seconds": round(avg_wait, 1),
                        "abandonment_pct": round(abandon_pct, 2),
                        "breaches": breaches,
                    },
                )
            results.append(
                {
                    "queue_id": queue.id,
                    "calls": total,
                    "avg_wait_seconds": round(avg_wait, 1),
                    "abandonment_pct": round(abandon_pct, 2),
                    "breaches": breaches,
                }
            )
        return results

    @api.model
    def cron_monitor_service_level(self):
        return self.search([("active", "=", True)]).evaluate_service_level()

    def get_available_agent(self):
        """FLAW-27.3: Evaluates live agent concurrency and wrap-up status."""
        self.ensure_one()
        agents = self.env["res.users"].search([("share", "=", False)], limit=10)
        for agent in agents:
            active_count = self.env["fix.conversation"].search_count(
                [("agent_id", "=", agent.id), ("state", "=", "with_agent")]
            )
            if active_count < self.max_agent_concurrency:
                return agent
        return None


class FixCcDisposition(models.Model):
    _name = "fix.cc.disposition"
    _description = "Contact Centre Disposition Code"
    _order = "code"

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    category = fields.Selection(
        [
            ("resolved", "Resolved at first contact"),
            ("followup", "Follow-up required"),
            ("escalated", "Escalated"),
            ("spam", "Spam / wrong number"),
        ],
        required=True,
        default="resolved",
    )
    is_resolved = fields.Boolean(default=True)
    active = fields.Boolean(default=True)


class FixCcRoutingRule(models.Model):
    _name = "fix.cc.routing.rule"
    _description = "Contact Centre Routing Rule"
    _order = "priority, id"

    name = fields.Char(required=True)
    queue_id = fields.Many2one("fix.cc.queue", required=True, ondelete="cascade")
    channel = fields.Selection(CHANNELS, required=True, default="voice")
    priority = fields.Integer(required=True, default=10)
    skill = fields.Char(help="Required skill tag (free text, matched by the routing engine).")
    active = fields.Boolean(default=True)


class FixCcIvrFlow(models.Model):
    _name = "fix.cc.ivr.flow"
    _description = "Contact Centre IVR Flow"
    _order = "name"

    name = fields.Char(required=True)
    channel = fields.Selection(CHANNELS, required=True, default="voice")
    version = fields.Integer(required=True, default=1)
    flow_json = fields.Text(help="Menu tree as JSON (the telephony engine's contract).")
    active = fields.Boolean(default=True)


class FixCcOutboundList(models.Model):
    _name = "fix.cc.outbound.list"
    _description = "Contact Centre Outbound List"
    _order = "priority, id"

    name = fields.Char(required=True)
    campaign_key = fields.Char(help="Source campaign/batch key.")
    queue_id = fields.Many2one("fix.cc.queue", string="Queue")
    priority = fields.Integer(required=True, default=10)
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("paused", "Paused"), ("done", "Completed")],
        required=True,
        default="draft",
    )
    contact_count = fields.Integer(readonly=True, default=0)


# A03 audit W7: a "transactional" template is sent on the contract basis and
# skips the marketing-consent and DND checks (fix_cc_productivity,
# fix_journey_runtime), so the class is a compliance decision, not a label.
# Only a contact-centre supervisor may classify a template transactional or
# change what a transactional template says; anyone may down-classify to
# marketing, which only adds checks.
TEMPLATE_SUPERVISOR_GROUP = "cd_contact_centre.group_cc_supervisor"
TEMPLATE_CONTENT = frozenset({"channel", "subject", "subject_bn", "body", "body_bn"})


class FixCcNotifTemplate(models.Model):
    _name = "fix.cc.notif.template"
    _description = "Notification Template"
    _order = "name"

    def _fix_may_classify(self) -> bool:
        return self.env.su or self.env.user.has_group(TEMPLATE_SUPERVISOR_GROUP)

    def _default_consent_class(self) -> str:
        return "transactional" if self._fix_may_classify() else "marketing"

    def _fix_form_locked_fields(self) -> set:
        # The class stays open: down-classifying is allowed, and write()
        # refuses an up-classification with the reason.
        if self._fix_may_classify() or not any(r.consent_class == "transactional" for r in self):
            return set()
        return set(TEMPLATE_CONTENT)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_may_classify() and any(
            vals.get("consent_class") == "transactional" for vals in vals_list
        ):
            raise UserError(
                "Only a Contact Centre Supervisor can classify a template as transactional: "
                "transactional messages are sent without marketing consent."
            )
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_may_classify():
            if vals.get("consent_class") == "transactional" and self.filtered(
                lambda r: r.consent_class != "transactional"
            ):
                raise UserError(
                    "Only a Contact Centre Supervisor can classify a template as "
                    "transactional: transactional messages are sent without marketing consent."
                )
            if (
                TEMPLATE_CONTENT & set(vals)
                and vals.get("consent_class") != "marketing"
                and self.filtered(lambda r: r.consent_class == "transactional")
            ):
                raise UserError(
                    "Template %s is transactional: only a Contact Centre Supervisor can "
                    "change its content. Down-classify it to marketing to edit it yourself."
                    % ", ".join(self.mapped("name"))
                )
        return super().write(vals)

    name = fields.Char(required=True)
    name_bn = fields.Char(string="Template Name (Bengali)", help="DE-17")
    channel = fields.Selection(
        [("sms", "SMS"), ("email", "E-mail"), ("whatsapp", "WhatsApp")],
        required=True,
        default="sms",
    )
    subject = fields.Char()
    subject_bn = fields.Char(string="Subject (Bengali)", help="DE-17")
    body = fields.Text(required=True, help="Template body; placeholders in {{braces}}.")
    body_bn = fields.Text(
        string="Body (Bengali)",
        help="DE-17. This is the field that matters: a template whose NAME is "
        "translated and whose BODY is not sends English to a Bengali-speaking "
        "customer while looking compliant on a configuration screen. The S1 "
        "delivery service picks this when the recipient's preferred_language "
        "is Bengali.",
    )
    consent_class = fields.Selection(
        [("transactional", "Transactional"), ("marketing", "Marketing")],
        required=True,
        default=lambda self: self._default_consent_class(),
    )
    active = fields.Boolean(default=True)


class FixCcQaEvaluation(models.Model):
    _name = "fix.cc.qa.evaluation"
    _description = "Contact Centre QA Evaluation"
    _order = "evaluated_at desc, id desc"

    conversation_id = fields.Many2one(
        "fix.conversation", required=True, ondelete="cascade", index=True
    )
    agent_id = fields.Many2one("res.users", string="Agent", required=True)
    score = fields.Integer(required=True, help="0–100 QA score.")
    criteria_json = fields.Text(string="Criteria Breakdown (JSON)")
    notes = fields.Char()
    evaluated_at = fields.Datetime(required=True, default=fields.Datetime.now)


class FixCcWfmShift(models.Model):
    _name = "fix.cc.wfm.shift"
    _description = "Contact Centre WFM Shift"
    _order = "shift_date, start_hour"

    agent_id = fields.Many2one("res.users", string="Agent", required=True, index=True)
    queue_id = fields.Many2one("fix.cc.queue", string="Queue")
    shift_date = fields.Date(required=True)
    start_hour = fields.Integer(required=True, default=9)
    end_hour = fields.Integer(required=True, default=18)
    state = fields.Selection(
        [("planned", "Planned"), ("confirmed", "Confirmed"), ("absent", "Absent")],
        required=True,
        default="planned",
    )
