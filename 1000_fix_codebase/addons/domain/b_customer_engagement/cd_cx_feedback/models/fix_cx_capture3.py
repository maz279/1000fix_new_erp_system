# M34 capture audit, third pass (19 Nov 2026).
#
# The user still saw M34 pages without a relevant capture after the 13 and 14
# Nov passes. Read against the spec (sections 5, 9, 10.1, 11), these records
# were missing or could not be captured by anyone:
#
#   page 1  survey triggers, delay and sampling (FR-CXM-002/003/004, AUT-01)
#   page 2  response provenance (FR-CXM-009, BRU-CXM-15 hard block),
#           score attribution at capture (FR-CXM-016, BRU-CXM-10 hard block),
#           response anomaly investigation (FR-CXM-019, BRU-CXM-11 hard
#           block, AUT-CXM-11, SOD-21)
#   page 3  the conversation rating (FR-CXM-015, spec entity fix.rating)
#   page 4  the 24-hour contact deadline and its escalation (FR-CXM-022/025,
#           BRU-CXM-05 hard block, AUT-CXM-04)
#   page 5  customer status updates (FR-CXM-033, BRU-CXM-07 hard block,
#           spec entity fix.complaint.update); the channel a staff-keyed
#           complaint came through (FR-CXM-028) and regulator / brand-partner
#           referrals (FR-CXM-038)
#   page 6  the SLA by customer tier (FR-CXM-031)
#   page 8  journey definitions (FR-CXM-039) and coded VoC themes (FR-CXM-041)
#
# Every record here is read by something: a trigger decides how the next
# survey is sent, an anomaly removes scores from the M57 incentive feed, a
# complaint update is queued on the S1 delivery service, a tiered SLA binding
# sets the complaint clock, a journey stage is measured from its instrument's
# responses, and a theme counts the verbatims coded to it.
import hashlib
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_cx_feedback import DETRACTOR_MAX_RATING

SUPERVISOR_GROUP = "cd_contact_centre.group_cc_supervisor"

# How a response reached us (FR-CXM-009). A survey answered by the customer's
# own channel and one keyed by staff from a phone call are different evidence
# for the integrity checks of FR-CXM-019, so the channel is never optional.
RESPONSE_CHANNELS = [
    ("phone_call", "Phone Call (keyed by staff)"),
    ("counter", "At the Counter (keyed by staff)"),
    ("field_visit", "Technician Visit (keyed by staff)"),
    ("sms_reply", "SMS Reply"),
    ("whatsapp", "WhatsApp Reply"),
    ("email", "E-mail Reply"),
    ("ivr", "Post-call IVR"),
    ("web_link", "Survey Link"),
    ("in_app", "Customer App"),
    ("system", "System / Integration"),
]
STAFF_KEYED = ("phone_call", "counter", "field_visit")

RATING_1_5 = [
    ("1", "1 · খুব খারাপ / Very Poor"),
    ("2", "2 · খারাপ / Poor"),
    ("3", "3 · মোটামুটি / Fair"),
    ("4", "4 · ভালো / Good"),
    ("5", "5 · খুব ভালো / Excellent"),
]

PARAM_LOOP_CONTACT_HOURS = "cd_cx_feedback.loop_contact_hours"
PARAM_LOOP_ESCALATION_USER = "cd_cx_feedback.loop_escalation_user"
DEFAULT_LOOP_CONTACT_HOURS = 24


def _is_supervisor(env):
    return env.su or env.user.has_group(SUPERVISOR_GROUP) or env.user.has_group("base.group_system")


# ---------------------------------------------------------------------------
# Page 1: survey triggers, delay and sampling (FR-CXM-002/003/004)
# ---------------------------------------------------------------------------
class FixSurveyTrigger(models.Model):
    """When, after what delay and for what share of eligible orders a
    survey goes out, and on which instrument (spec 10.1 fix.survey.trigger).

    Read by fix.survey.consume_order_closed: with no active trigger the
    estate keeps its old behaviour (every closed order, at once, no
    instrument). The most specific active trigger wins: one naming the
    order's branch, then one naming its service type, then the default."""

    _name = "fix.survey.trigger"
    _description = "Survey Trigger"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    trigger_event = fields.Selection(
        # Only events a consumer actually reads. Device collection, contract
        # renewal and membership anniversary have no survey consumer yet; a
        # trigger naming them would be configuration nothing reads.
        [("service_order_closed", "Service Order Closed")],
        required=True,
        default="service_order_closed",
        tracking=True,
    )
    template_id = fields.Many2one(
        "fix.survey.template",
        string="Instrument",
        required=True,
        ondelete="restrict",
        tracking=True,
        domain=[("state", "=", "published")],
        help="The published instrument the customer is asked.",
    )
    delay_minutes = fields.Integer(
        string="Delay (minutes)",
        default=0,
        tracking=True,
        help="FR-CXM-003: time between the event and the invitation. 0 sends at once.",
    )
    sampling_rate = fields.Integer(
        string="Sample (%)",
        default=100,
        tracking=True,
        help="FR-CXM-004: share of eligible orders surveyed. The choice is a fixed "
        "hash of the order, so it is repeatable and cannot be steered by staff.",
    )
    branch_id = fields.Many2one("fix.branch", string="Only for Branch", help="Empty: every branch.")
    service_type = fields.Char(
        string="Only for Service Type",
        help="The service order's service type key (walk_in, onsite, collection...). "
        "Empty: every type.",
    )
    eligibility_note = fields.Text(string="Eligibility Criteria")
    survey_count = fields.Integer(compute="_compute_counts", string="Surveys Raised")
    not_sampled_count = fields.Integer(compute="_compute_counts", string="Not Sampled")

    def _compute_counts(self):
        Survey = self.env["fix.survey"].sudo()
        for rec in self:
            rec.survey_count = (
                Survey.search_count([("trigger_id", "=", rec.id), ("state", "!=", "not_sampled")])
                if rec.id
                else 0
            )
            rec.not_sampled_count = (
                Survey.search_count([("trigger_id", "=", rec.id), ("state", "=", "not_sampled")])
                if rec.id
                else 0
            )

    @api.constrains("sampling_rate", "delay_minutes")
    def _check_numbers(self):
        for rec in self:
            if not 1 <= rec.sampling_rate <= 100:
                raise ValidationError("The sample must be between 1 and 100 percent.")
            if rec.delay_minutes < 0:
                raise ValidationError("The delay cannot be negative.")
            if rec.delay_minutes > 60 * 24 * 30:
                raise ValidationError(
                    "A delay over 30 days asks the customer about a repair they no longer recall."
                )

    @api.constrains("service_type")
    def _check_service_type(self):
        Order = self.env["fix.service.order"]
        keys = (
            dict(Order._fields["service_type"].selection) if "service_type" in Order._fields else {}
        )
        for rec in self:
            if rec.service_type and keys and rec.service_type not in keys:
                raise ValidationError(
                    "'%s' is not a service type. Use one of: %s."
                    % (rec.service_type, ", ".join(sorted(keys)))
                )

    @api.constrains("code", "company_id")
    def _check_code_unique(self):
        for rec in self:
            if self.search_count(
                [
                    ("code", "=", rec.code),
                    ("company_id", "=", rec.company_id.id),
                    ("id", "!=", rec.id),
                ]
            ):
                raise ValidationError("Trigger code %s is already used." % rec.code)

    @api.constrains("template_id")
    def _check_template_published(self):
        for rec in self:
            if rec.template_id.state != "published":
                raise ValidationError(
                    "Instrument %s is not published: publish it first, so every "
                    "customer is asked the same frozen questions." % rec.template_id.display_name
                )

    @api.model
    def _for_order(self, order, event="service_order_closed"):
        """The trigger that governs a closed order, or an empty set."""
        # A retired instrument stops its trigger: nobody is asked a frozen
        # questionnaire the business has withdrawn.
        triggers = self.sudo().search(
            [
                ("trigger_event", "=", event),
                ("company_id", "in", [order.company_id.id, False]),
                ("template_id.state", "=", "published"),
            ]
        )
        branch = order.branch_id
        stype = order.service_type if "service_type" in order._fields else False
        eligible = triggers.filtered(
            lambda t: (not t.branch_id or t.branch_id == branch)
            and (not t.service_type or t.service_type == stype)
        )
        for candidate in (
            eligible.filtered(lambda t: t.branch_id and t.service_type),
            eligible.filtered(lambda t: t.branch_id and not t.service_type),
            eligible.filtered(lambda t: not t.branch_id and t.service_type),
            eligible.filtered(lambda t: not t.branch_id and not t.service_type),
        ):
            if candidate:
                return candidate[:1]
        return self.browse()

    def _sampled(self, order):
        """Deterministic: the same order is always in or always out."""
        self.ensure_one()
        if self.sampling_rate >= 100:
            return True
        digest = hashlib.sha256(("%s:%s" % (self.code, order.id)).encode()).hexdigest()
        return int(digest[:8], 16) % 100 < self.sampling_rate


# ---------------------------------------------------------------------------
# Pages 2 and 3: provenance, attribution, sampling state on the survey
# ---------------------------------------------------------------------------
class FixSurveyCapture3(models.Model):
    _inherit = "fix.survey"

    state = fields.Selection(
        selection_add=[("not_sampled", "Not Sampled")],
        ondelete={"not_sampled": "set default"},
    )
    trigger_id = fields.Many2one(
        "fix.survey.trigger", string="Trigger", readonly=True, copy=False, index=True
    )
    dispatch_after = fields.Datetime(
        string="Send After",
        readonly=True,
        copy=False,
        help="FR-CXM-003: the invitation waits until this time.",
    )
    # FR-CXM-009 / BRU-CXM-15: provenance of the response.
    response_channel = fields.Selection(
        RESPONSE_CHANNELS, string="Response Received Through", copy=False, tracking=True
    )
    response_device = fields.Char(
        string="From Number / Device",
        copy=False,
        help="The phone number, e-mail or device the answer came from, for the "
        "device-reuse check of FR-CXM-019.",
    )
    responded_at = fields.Datetime(readonly=True, copy=False)
    response_recorded_by_id = fields.Many2one(
        "res.users", string="Response Recorded By", readonly=True, copy=False
    )
    # FR-CXM-016 / BRU-CXM-10: who and what the score is about, FROZEN at
    # capture. A related field would move last month's score to whoever the
    # order is reassigned to today.
    branch_id = fields.Many2one(
        "fix.branch", string="Branch", readonly=True, copy=False, index=True
    )
    technician_id = fields.Many2one(
        "hr.employee", string="Technician", readonly=True, copy=False, index=True
    )
    service_type = fields.Char(string="Service Type", readonly=True, copy=False)
    # BRU-CXM-11: a response under an open or upheld anomaly is kept out of the
    # M57 technician CSAT feed until the investigation clears it.
    anomaly_id = fields.Many2one(
        "fix.cx.response.anomaly",
        string="Under Anomaly Review",
        readonly=True,
        copy=False,
        index=True,
    )
    incentive_excluded = fields.Boolean(
        string="Kept Out of Incentives",
        readonly=True,
        copy=False,
        index=True,
        help="BRU-CXM-11: set while an anomaly covering this response is open or "
        "was upheld; cleared when the investigation clears it.",
    )

    def _attribution_vals(self, order):
        return {
            "branch_id": order.branch_id.id or False,
            "technician_id": order.technician_id.id or False,
            "service_type": order.service_type or False
            if "service_type" in order._fields
            else False,
        }

    @api.model
    def consume_order_closed(self, event):
        """Apply the trigger (instrument, sampling, delay) and freeze the
        attribution. Without a trigger the old path runs unchanged."""
        if event.get("aggregate") not in (None, "fix.service.order"):
            return None
        order_id = event.get("aggregate_id") or (event.get("payload") or {}).get("order_id")
        order = self.env["fix.service.order"].browse(int(order_id)).exists() if order_id else None
        trigger = self.env["fix.survey.trigger"]._for_order(order) if order else None
        if order and trigger and not self.search_count([("service_order_id", "=", order.id)]):
            sampled = trigger._sampled(order)
            vals = {
                "service_order_id": order.id,
                "operating_unit_id": (
                    order.operating_unit_id or order.branch_id.operating_unit_id
                ).id,
                "source_event_id": event.get("event_id", ""),
                "state": "pending" if sampled else "not_sampled",
                "trigger_id": trigger.id,
                "template_id": trigger.template_id.id,
            }
            if not sampled:
                vals["dispatch_suppressed_reason"] = (
                    "Not sampled: trigger %s surveys %d%% of eligible orders (FR-CXM-004)."
                    % (trigger.code, trigger.sampling_rate)
                )
            elif trigger.delay_minutes:
                vals["dispatch_after"] = fields.Datetime.now() + timedelta(
                    minutes=trigger.delay_minutes
                )
            survey = self.create(vals)
            if sampled and not trigger.delay_minutes:
                survey.action_dispatch_invitation()
            elif not sampled:
                publish(
                    self.env,
                    "survey.not_sampled",
                    "fix.survey",
                    survey.id,
                    {"trigger": trigger.code, "service_order_id": order.id},
                )
            return survey
        return super().consume_order_closed(event)

    @api.model_create_multi
    def create(self, vals_list):
        Order = self.env["fix.service.order"].sudo()
        for vals in vals_list:
            if vals.get("service_order_id"):
                order = Order.browse(vals["service_order_id"])
                for key, value in self._attribution_vals(order).items():
                    vals.setdefault(key, value)
            if vals.get("rating") or vals.get("answer_ids") or vals.get("state") == "responded":
                self._require_channel(vals.get("response_channel"))
                vals.setdefault("responded_at", fields.Datetime.now())
                vals.setdefault("response_recorded_by_id", self.env.user.id)
        return super().create(vals_list)

    @api.model
    def _require_channel(self, channel):
        if not channel:
            raise ValidationError(
                "Say how the response arrived (Response Received Through): every "
                "response records its provenance (BRU-CXM-15)."
            )

    def write(self, vals):
        if vals.get("rating") or vals.get("answer_ids"):
            becoming = self.filtered(lambda s: s.state in ("pending", "sent"))
            if becoming:
                if self.filtered(lambda s: s.state == "not_sampled"):
                    raise UserError(
                        "This order was not sampled for a survey: there is nothing to answer."
                    )
                channel = vals.get("response_channel") or (
                    becoming[:1].response_channel if len(becoming) == 1 else False
                )
                self._require_channel(channel)
            elif self.filtered(lambda s: s.state == "not_sampled"):
                raise UserError(
                    "This order was not sampled for a survey (FR-CXM-004): a response "
                    "cannot be recorded against it."
                )
        if "response_channel" in vals:
            locked = self.filtered(lambda s: s.state == "responded" and s.response_channel)
            if locked and any(s.response_channel != vals["response_channel"] for s in locked):
                raise UserError("The provenance of a recorded response cannot be changed.")
        pending = self.filtered(lambda s: s.state in ("pending", "sent"))
        result = super().write(vals)
        just = pending.filtered(lambda s: s.state == "responded")
        if just:
            stamp = {
                "responded_at": fields.Datetime.now(),
                "response_recorded_by_id": self.env.user.id,
            }
            for survey in just:
                missing = {k: v for k, v in stamp.items() if not survey[k]}
                if not survey.branch_id and survey.service_order_id:
                    missing.update(self._attribution_vals(survey.service_order_id.sudo()))
                if missing:
                    super(FixSurveyCapture3, survey).write(missing)
            just._flag_open_anomalies()
        return result

    def record_answers(self, answers, channel=None, device=None):
        """The programmatic response path names its channel too."""
        self.ensure_one()
        if self.state == "not_sampled":
            raise UserError("This order was not sampled for a survey: there is nothing to answer.")
        channel = channel or self.response_channel
        self._require_channel(channel)
        if self.response_channel != channel or (device and not self.response_device):
            vals = {"response_channel": channel}
            if device:
                vals["response_device"] = device
            super().write(vals)
        return super().record_answers(answers)

    def action_dispatch_invitation(self):
        """Hold an invitation until its trigger's delay has passed."""
        now = fields.Datetime.now()
        ready = self.filtered(
            lambda s: s.state != "not_sampled" and (not s.dispatch_after or s.dispatch_after <= now)
        )
        return super(FixSurveyCapture3, ready).action_dispatch_invitation()

    @api.model
    def cron_dispatch_delayed_invitations(self, limit=500):
        """FR-CXM-003: send the invitations whose delay has run out."""
        due = self.sudo().search(
            [
                ("state", "=", "pending"),
                ("dispatch_after", "!=", False),
                ("dispatch_after", "<=", fields.Datetime.now()),
                ("dispatch_delivery_id", "=", False),
                ("dispatch_suppressed_reason", "=", False),
            ],
            limit=limit,
        )
        due.action_dispatch_invitation()
        return len(due)

    def _flag_open_anomalies(self):
        """A response arriving inside an open anomaly's scope joins it."""
        Anomaly = self.env["fix.cx.response.anomaly"].sudo()
        open_ones = Anomaly.search([("state", "in", ("open", "investigating", "upheld"))])
        for anomaly in open_ones:
            hits = self.sudo().filtered(lambda s, a=anomaly: a._covers(s) and not s.anomaly_id)
            if hits:
                hits.write({"anomaly_id": anomaly.id, "incentive_excluded": True})


# ---------------------------------------------------------------------------
# Page 2: response anomaly investigation (FR-CXM-019, BRU-CXM-11, SOD-21)
# ---------------------------------------------------------------------------
class FixCxResponseAnomaly(models.Model):
    """A suspected manipulation of scores, and its investigation.

    Raising one takes every response in its scope and period out of the M57
    incentive feed (AUT-CXM-11) until it is cleared. The person whose scores
    are under investigation can neither investigate nor decide it (SOD-21)."""

    _name = "fix.cx.response.anomaly"
    _description = "Survey Response Anomaly"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    detection_type = fields.Selection(
        [
            ("clustering", "Clustered Top Scores"),
            ("timing", "Answered Too Fast / Odd Hours"),
            ("device_reuse", "Same Number or Device for Many Customers"),
            ("distribution", "Unusual Score Distribution"),
            ("staff_keyed", "Unusual Share Keyed by One Person"),
            ("other", "Other"),
        ],
        required=True,
        tracking=True,
    )
    scope_type = fields.Selection(
        [
            ("technician", "Technician"),
            ("branch", "Branch"),
            ("recorder", "Person Keying Responses"),
        ],
        required=True,
        default="technician",
        tracking=True,
    )
    technician_id = fields.Many2one("hr.employee", string="Technician", tracking=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", tracking=True)
    recorder_id = fields.Many2one("res.users", string="Person Keying Responses", tracking=True)
    period_from = fields.Date(required=True, tracking=True)
    period_to = fields.Date(required=True, tracking=True)
    evidence = fields.Text(required=True, help="What was seen: counts, times, numbers.")
    state = fields.Selection(
        [
            ("open", "Open"),
            ("investigating", "Investigating"),
            ("cleared", "Cleared"),
            ("upheld", "Upheld"),
        ],
        default="open",
        required=True,
        readonly=True,
        tracking=True,
    )
    raised_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, string="Raised By"
    )
    investigator_id = fields.Many2one("res.users", readonly=True, tracking=True)
    investigation_started_at = fields.Datetime(readonly=True)
    outcome = fields.Text(readonly=True, tracking=True)
    decided_by_id = fields.Many2one("res.users", readonly=True)
    decided_at = fields.Datetime(readonly=True)
    survey_ids = fields.One2many("fix.survey", "anomaly_id", string="Held Responses")
    held_count = fields.Integer(compute="_compute_held_count", string="Responses Held")

    @api.depends("detection_type", "scope_type", "technician_id", "branch_id", "recorder_id")
    def _compute_name(self):
        types = dict(self._fields["detection_type"].selection)
        for rec in self:
            subject = rec.technician_id.name or rec.branch_id.name or rec.recorder_id.name or "?"
            rec.name = "%s · %s" % (types.get(rec.detection_type, ""), subject)

    def _compute_held_count(self):
        for rec in self:
            rec.held_count = len(rec.survey_ids)

    @api.constrains(
        "scope_type", "technician_id", "branch_id", "recorder_id", "period_from", "period_to"
    )
    def _check_scope(self):
        need = {"technician": "technician_id", "branch": "branch_id", "recorder": "recorder_id"}
        for rec in self:
            field = need[rec.scope_type]
            if not rec[field]:
                raise ValidationError(
                    "Name the %s the anomaly is about." % rec._fields[field].string.lower()
                )
            others = [f for f in need.values() if f != field and rec[f]]
            if others:
                raise ValidationError(
                    "An anomaly is about one subject: the scope is %s, so leave %s empty."
                    % (rec.scope_type, ", ".join(rec._fields[f].string for f in others))
                )
            if rec.period_from > rec.period_to:
                raise ValidationError("The period ends before it starts.")

    def _fix_guarded_fields(self) -> set:
        # Moved only by Start Investigation / Clear / Uphold.
        return super()._fix_guarded_fields() | {
            "state",
            "investigator_id",
            "investigation_started_at",
            "outcome",
            "decided_by_id",
            "decided_at",
            "raised_by_id",
        }

    def _subject_users(self):
        """The people whose scores are under investigation (SOD-21)."""
        self.ensure_one()
        if self.scope_type == "technician":
            return self.technician_id.user_id
        if self.scope_type == "recorder":
            return self.recorder_id
        return self.env["res.users"]

    def _covers(self, survey):
        self.ensure_one()
        stamp = survey.responded_at or survey.create_date
        day = fields.Date.to_date(stamp) if stamp else None
        if not day or not (self.period_from <= day <= self.period_to):
            return False
        if self.scope_type == "technician":
            return survey.technician_id == self.technician_id
        if self.scope_type == "branch":
            return survey.branch_id == self.branch_id
        return survey.response_recorded_by_id == self.recorder_id

    def _hold_scope(self):
        Survey = self.env["fix.survey"].sudo()
        for rec in self:
            domain = [("state", "=", "responded"), ("anomaly_id", "=", False)]
            if rec.scope_type == "technician":
                domain.append(("technician_id", "=", rec.technician_id.id))
            elif rec.scope_type == "branch":
                domain.append(("branch_id", "=", rec.branch_id.id))
            else:
                domain.append(("response_recorded_by_id", "=", rec.recorder_id.id))
            hits = Survey.search(domain).filtered(rec._covers)
            hits.write({"anomaly_id": rec.id, "incentive_excluded": True})

    @api.model_create_multi
    def create(self, vals_list):
        # Checked BEFORE the insert: a refusal raised after it would leave the
        # row behind in the caller's transaction.
        if not self.env.su:
            me = self.env.user
            for vals in vals_list:
                scope = vals.get("scope_type") or "technician"
                tech = self.env["hr.employee"].sudo().browse(vals.get("technician_id") or 0)
                if (scope == "technician" and tech.exists() and tech.user_id == me) or (
                    scope == "recorder" and vals.get("recorder_id") == me.id
                ):
                    raise UserError(
                        "You cannot raise an anomaly about your own scores (SOD-21): "
                        "ask the Customer Service Manager."
                    )
        records = super().create(vals_list)
        records._hold_scope()
        for rec in records:
            rec.message_post(
                body="Raised: %d response(s) in scope are kept out of incentive "
                "calculation until the investigation decides (BRU-CXM-11)." % rec.held_count
            )
            publish(
                self.env,
                "cx.response_anomaly_flagged",
                "fix.cx.response.anomaly",
                rec.id,
                {
                    "detection_type": rec.detection_type,
                    "scope_type": rec.scope_type,
                    "technician_id": rec.technician_id.id or None,
                    "branch_id": rec.branch_id.id or None,
                    "recorder_id": rec.recorder_id.id or None,
                    "held": rec.held_count,
                },
            )
        return records

    def write(self, vals):
        scope = {
            "scope_type",
            "technician_id",
            "branch_id",
            "recorder_id",
            "period_from",
            "period_to",
        }
        if scope & set(vals) and self.filtered(lambda r: r.state != "open"):
            raise UserError("The scope is fixed once the investigation has started.")
        result = super().write(vals)
        if scope & set(vals):
            for rec in self:
                rec.survey_ids.sudo().write({"anomaly_id": False, "incentive_excluded": False})
            self._hold_scope()
        return result

    def _refuse_subject(self, act):
        for rec in self:
            if self.env.user in rec._subject_users():
                raise UserError(
                    "%s: the person whose scores are under investigation cannot take "
                    "part in it (SOD-21)." % act
                )

    def action_start_investigation(self):
        if not _is_supervisor(self.env):
            raise UserError(
                "Only the Customer Service Manager (Contact Centre Supervisor) investigates."
            )
        self._refuse_subject("Start Investigation")
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open anomaly can be taken for investigation.")
            rec._guarded().write(
                {
                    "state": "investigating",
                    "investigator_id": self.env.user.id,
                    "investigation_started_at": fields.Datetime.now(),
                }
            )
        return True

    def _decide(self, state, outcome, act):
        outcome = (outcome or "").strip()
        if not outcome:
            raise UserError("Write what the investigation found.")
        if not _is_supervisor(self.env):
            raise UserError(
                "Only the Customer Service Manager (Contact Centre Supervisor) decides."
            )
        self._refuse_subject(act)
        for rec in self:
            if rec.state != "investigating":
                raise UserError("Start the investigation before deciding it.")
            rec._guarded().write(
                {
                    "state": state,
                    "outcome": outcome,
                    "decided_by_id": self.env.user.id,
                    "decided_at": fields.Datetime.now(),
                }
            )
        return True

    def action_clear(self, outcome=None):
        """Not manipulation: the held responses return to the incentive feed."""
        self._decide("cleared", outcome, "Clear")
        for rec in self:
            rec.survey_ids.sudo().write({"incentive_excluded": False})
            rec.message_post(body="Cleared: %d response(s) released." % len(rec.survey_ids))
        return True

    def action_uphold(self, outcome=None):
        """Manipulation found: the responses stay out of incentives for good."""
        self._decide("upheld", outcome, "Uphold")
        for rec in self:
            publish(
                self.env,
                "cx.response_anomaly_upheld",
                "fix.cx.response.anomaly",
                rec.id,
                {"held": len(rec.survey_ids), "technician_id": rec.technician_id.id or None},
            )
        return True


# ---------------------------------------------------------------------------
# Page 3: the conversation rating (FR-CXM-014/015, spec fix.rating)
# ---------------------------------------------------------------------------
class FixCxRating(models.Model):
    """The multi-parameter rating a customer gives at the close of a
    contact-centre conversation. A service order is rated by its survey; a
    conversation had nothing to record the score on."""

    _name = "fix.cx.rating"
    _description = "Conversation Rating"
    _inherit = ["mail.thread"]
    _order = "captured_at desc, id desc"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    conversation_id = fields.Many2one(
        "fix.conversation", string="Conversation", required=True, ondelete="restrict", index=True
    )
    customer_id = fields.Many2one(
        "res.partner", compute="_compute_attribution", store=True, string="Customer"
    )
    # BRU-CXM-10: who handled it and through what, frozen at capture.
    agent_id = fields.Many2one(
        "res.users", compute="_compute_attribution", store=True, string="Agent", index=True
    )
    channel = fields.Char(compute="_compute_attribution", store=True, string="Conversation Channel")
    operating_unit_id = fields.Many2one(
        "operating.unit", compute="_compute_attribution", store=True, index=True
    )
    overall = fields.Selection(RATING_1_5, string="Overall", required=True)
    timeliness = fields.Selection(RATING_1_5, string="Timeliness")
    professionalism = fields.Selection(RATING_1_5, string="Professionalism")
    behaviour = fields.Selection(RATING_1_5, string="Behaviour")
    comment = fields.Text(string="Customer's Words")
    captured_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    response_channel = fields.Selection(RESPONSE_CHANNELS, string="Received Through", required=True)
    recorded_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, string="Recorded By"
    )
    followup_id = fields.Many2one(
        "fix.cx.followup", string="Recovery Task", readonly=True, copy=False
    )

    _conversation_unique = models.Constraint(
        "UNIQUE (conversation_id)", "A conversation is rated once."
    )

    @api.depends("conversation_id", "overall")
    def _compute_name(self):
        for rec in self:
            rec.name = "Rating %s · %s" % (
                rec.overall or "?",
                rec.conversation_id.display_name or "",
            )

    @api.depends("conversation_id")
    def _compute_attribution(self):
        for rec in self:
            conv = rec.conversation_id.sudo()
            # Frozen: computed once at capture; the depends key never changes.
            rec.customer_id = conv.customer_id
            rec.agent_id = conv.agent_id
            rec.channel = conv.channel or False
            rec.operating_unit_id = conv.operating_unit_id

    @api.constrains("conversation_id")
    def _check_conversation_closed(self):
        for rec in self:
            if rec.conversation_id.state not in ("resolved_ai", "resolved_agent", "abandoned"):
                raise ValidationError(
                    "Conversation %s is still open: it is rated at its close (FR-CXM-015)."
                    % rec.conversation_id.display_name
                )

    def write(self, vals):
        frozen = {
            "conversation_id",
            "overall",
            "timeliness",
            "professionalism",
            "behaviour",
            "response_channel",
        }
        if frozen & set(vals) and not self.env.su:
            raise UserError("A recorded rating is the customer's words: it is not edited.")
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        # Said in words before the insert; the unique constraint stays as the
        # backstop for a race.
        convs = [v.get("conversation_id") for v in vals_list if v.get("conversation_id")]
        if len(convs) != len(set(convs)) or self.sudo().search_count(
            [("conversation_id", "in", convs)]
        ):
            raise ValidationError("This conversation has already been rated: it is rated once.")
        records = super().create(vals_list)
        for rec in records:
            if int(rec.overall) <= DETRACTOR_MAX_RATING:
                rec._spawn_followup()
        return records

    def _spawn_followup(self):
        """BRU-CXM-03: a low conversation rating opens a loop case too."""
        self.ensure_one()
        owner = self.conversation_id.agent_id
        followup = (
            self.env["fix.cx.followup"]
            .sudo()
            .create(
                {
                    "rating_id": self.id,
                    "reason": "low_rating",
                    "due_date": fields.Date.add(fields.Date.context_today(self), days=2),
                    "owner_id": False,
                    "company_id": self.company_id.id,
                    "notes": "Raised automatically from conversation rating %s (overall %s)."
                    % (self.id, self.overall),
                }
            )
        )
        self.sudo().write({"followup_id": followup.id})
        publish(
            self.env,
            "conversation.low_rating_flagged",
            "fix.cx.rating",
            self.id,
            {
                "conversation_id": self.conversation_id.id,
                "agent_id": owner.id or None,
                "overall": int(self.overall),
                "followup_id": followup.id,
            },
        )


# ---------------------------------------------------------------------------
# Page 4: the loop case can come from a rating; 24-hour contact deadline and
# its escalation (FR-CXM-022/025, BRU-CXM-05, AUT-CXM-04)
# ---------------------------------------------------------------------------
class FixCxFollowupCapture3(models.Model):
    # mail.thread + activities: an escalation is a to-do in the escalated
    # person's inbox, and the case keeps its own history.
    _name = "fix.cx.followup"
    _inherit = ["fix.cx.followup", "mail.thread", "mail.activity.mixin"]

    survey_id = fields.Many2one(required=False)
    rating_id = fields.Many2one(
        "fix.cx.rating", string="Conversation Rating", ondelete="cascade", index=True
    )
    customer_id = fields.Many2one(
        "res.partner",
        related=False,
        compute="_compute_customer",
        store=True,
        string="Customer",
    )
    contact_due = fields.Datetime(
        string="Contact By",
        readonly=True,
        copy=False,
        help="FR-CXM-022: first contact with the detractor is due within this window "
        "(24 hours by default, parameter cd_cx_feedback.loop_contact_hours).",
    )
    escalation_level = fields.Selection(
        [("0", "Not Escalated"), ("1", "Branch Manager"), ("2", "Operations Director")],
        default="0",
        readonly=True,
        copy=False,
        string="Escalated To Level",
    )
    escalated_to_id = fields.Many2one("res.users", readonly=True, copy=False, string="Escalated To")
    escalated_at = fields.Datetime(readonly=True, copy=False)

    @api.depends("survey_id.customer_id", "rating_id.customer_id")
    def _compute_customer(self):
        for rec in self:
            rec.customer_id = rec.survey_id.customer_id or rec.rating_id.customer_id

    @api.depends("survey_id", "rating_id")
    def _compute_name(self):
        for rec in self:
            if rec.rating_id:
                rec.name = "Follow-up · %s" % (
                    rec.rating_id.conversation_id.display_name or rec.rating_id.id
                )
            else:
                rec.name = "Follow-up · %s" % (
                    rec.survey_id.service_order_id.name or rec.survey_id.id
                )

    @api.constrains("survey_id", "rating_id")
    def _check_one_source(self):
        for rec in self:
            if bool(rec.survey_id) == bool(rec.rating_id):
                raise ValidationError(
                    "A follow-up comes from exactly one response: a survey or a conversation rating."
                )

    @api.model
    def _contact_hours(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(PARAM_LOOP_CONTACT_HOURS)
        try:
            hours = int(raw) if raw else DEFAULT_LOOP_CONTACT_HOURS
        except ValueError:
            hours = DEFAULT_LOOP_CONTACT_HOURS
        return max(1, hours)

    @api.model_create_multi
    def create(self, vals_list):
        due = fields.Datetime.now() + timedelta(hours=self._contact_hours())
        for vals in vals_list:
            vals.setdefault("contact_due", due)
        return super().create(vals_list)

    def _open_complaint_for_order(self):
        self.ensure_one()
        if self.rating_id:
            return (
                self.env["fix.complaint"]
                .sudo()
                .search(
                    [
                        ("conversation_id", "=", self.rating_id.conversation_id.id),
                        ("state", "not in", ("closed", "rejected")),
                    ],
                    limit=1,
                )
            )
        return super()._open_complaint_for_order()

    def action_raise_complaint(self):
        Complaint = self.env["fix.complaint"]
        for rec in self.filtered(lambda r: r.rating_id and not r.complaint_id):
            existing = rec._open_complaint_for_order()
            if existing:
                rec._link(existing)
                continue
            rating = rec.rating_id
            conv = rating.conversation_id.sudo()
            if not rating.customer_id:
                raise UserError(
                    "The conversation has no identified customer to raise a complaint for."
                )
            complaint = Complaint._intake_create(
                {
                    "name": "Low conversation rating: %s" % conv.display_name,
                    "description": (rating.comment or rec.notes or "").strip()
                    or "Low rating on conversation %s." % conv.id,
                    "category": "service_quality",
                    "severity": "minor",
                    "customer_id": rating.customer_id.id,
                    "operating_unit_id": conv.operating_unit_id.id,
                    "company_id": rating.company_id.id,
                    "intake_channel": "contact_centre",
                    "intake_ref": "followup:%d" % rec.id,
                }
            )
            rec._link(complaint)
        return super(
            FixCxFollowupCapture3, self.filtered(lambda r: not r.rating_id)
        ).action_raise_complaint()

    def _branch_manager(self):
        self.ensure_one()
        branch = self.survey_id.service_order_id.branch_id
        manager = branch.manager_id if branch and "manager_id" in branch._fields else False
        return manager if manager and manager.active else self.env["res.users"]

    def _operations_director(self):
        Users = self.env["res.users"].sudo()
        params = self.env["ir.config_parameter"].sudo()
        for key in (PARAM_LOOP_ESCALATION_USER, "cd_cx_feedback.escalation_user"):
            ref = (params.get_param(key) or "").strip()
            if ref:
                user = Users.search([("login", "=", ref)], limit=1)
                if not user and ref.isdigit():
                    user = Users.browse(int(ref)).exists()
                if user and user.active and not user.share:
                    return user
        group = self.env.ref("cd_entity_config.group_dofa_tier_4", raise_if_not_found=False)
        holders = (
            group.sudo().all_user_ids.filtered(lambda u: u.active and not u.share)
            if group
            else Users
        )
        return holders.sorted("id")[:1]

    def _escalate_to(self, level, user, reason):
        self.ensure_one()
        vals = {
            "escalation_level": level,
            "escalated_to_id": user.id or False,
            "escalated_at": fields.Datetime.now(),
        }
        self.sudo().write(vals)
        target = (
            user.name
            if user
            else "NOBODY (no branch manager, no escalation user, no DOFA Tier 4 holder)"
        )
        self.sudo().write({"notes": self._note_line("Escalated", "%s to %s" % (reason, target))})
        if user:
            self.env["mail.activity"].sudo().create(
                {
                    "res_model_id": self.env["ir.model"]._get_id("fix.cx.followup"),
                    "res_id": self.id,
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "summary": "Detractor not contacted: %s" % self.name,
                    "note": reason,
                    "user_id": user.id,
                    "date_deadline": fields.Date.context_today(self),
                }
            )
        publish(
            self.env,
            "cx.loop_escalated",
            "fix.cx.followup",
            self.id,
            {"level": int(level), "escalated_to_id": user.id or None, "reason": reason},
        )

    @api.model
    def cron_escalate_uncontacted(self):
        """AUT-CXM-04: contact deadline passed -> branch manager; a further
        window later -> operations director. Escalation repeats only by level."""
        now = fields.Datetime.now()
        window = timedelta(hours=self._contact_hours())
        open_ones = self.sudo().search(
            [("state", "=", "open"), ("contact_due", "!=", False), ("contact_due", "<", now)]
        )
        moved = 0
        for rec in open_ones:
            overdue = now - rec.contact_due
            if rec.escalation_level == "0":
                manager = rec._branch_manager()
                if manager:
                    rec._escalate_to(
                        "1",
                        manager,
                        "No contact within %d hours (BRU-CXM-05)." % self._contact_hours(),
                    )
                else:
                    rec._escalate_to(
                        "2",
                        rec._operations_director(),
                        "No contact within %d hours and no branch manager (BRU-CXM-05)."
                        % self._contact_hours(),
                    )
                moved += 1
            elif rec.escalation_level == "1" and overdue >= window:
                rec._escalate_to(
                    "2",
                    rec._operations_director(),
                    "Still not contacted %d hours after the branch manager escalation."
                    % self._contact_hours(),
                )
                moved += 1
        return moved


# ---------------------------------------------------------------------------
# Page 5: status communications, intake channel, external referrals
# ---------------------------------------------------------------------------
STAFF_INTAKE_CHANNELS = [
    ("counter", "Branch Counter"),
    ("phone", "Phone Call to Branch"),
    ("email", "E-mail"),
    ("letter", "Letter"),
    ("social", "Social Media"),
    ("regulator", "Regulator / Consumer Body Referral"),
    ("brand_partner", "Brand Partner Escalation"),
]
EXTERNAL_CHANNELS = ("regulator", "brand_partner")


class FixComplaintCapture3(models.Model):
    _inherit = "fix.complaint"

    intake_channel = fields.Selection(
        selection_add=STAFF_INTAKE_CHANNELS,
        ondelete={key: "set default" for key, _label in STAFF_INTAKE_CHANNELS},
    )
    received_via = fields.Selection(
        STAFF_INTAKE_CHANNELS,
        string="Received Via",
        copy=False,
        help="FR-CXM-028: for a complaint keyed by staff, the channel the customer used.",
    )
    external_body = fields.Char(
        string="Referring Body",
        copy=False,
        help="FR-CXM-038: the regulator, consumer body or brand partner that referred it.",
    )
    external_reference = fields.Char(string="Their Reference", copy=False)
    external_response_due = fields.Date(string="Their Response Deadline", copy=False)
    update_ids = fields.One2many("fix.complaint.update", "complaint_id", string="Customer Updates")
    update_count = fields.Integer(compute="_compute_update_stats", store=True)
    last_update_at = fields.Datetime(
        compute="_compute_update_stats", store=True, string="Customer Last Updated"
    )

    @api.depends("update_ids.sent_at", "update_ids.state")
    def _compute_update_stats(self):
        for rec in self:
            sent = rec.update_ids.filtered(lambda u: u.state == "sent" and u.sent_at)
            rec.update_count = len(sent)
            rec.last_update_at = max(sent.mapped("sent_at")) if sent else False

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked = locked | {"received_via"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.received_via and rec.intake_channel == "manual":
                rec._guarded().write({"intake_channel": rec.received_via})
        return records

    def write(self, vals):
        if "received_via" in vals and not self.env.su:
            changed = self.filtered(lambda r: r.received_via != vals["received_via"])
            if changed:
                raise UserError("The channel a complaint came through is recorded at intake.")
        return super().write(vals)

    @api.constrains("received_via", "external_body", "external_reference")
    def _check_external(self):
        for rec in self:
            if rec.received_via in EXTERNAL_CHANNELS and not (
                (rec.external_body or "").strip() and (rec.external_reference or "").strip()
            ):
                raise ValidationError(
                    "A complaint referred by a regulator, consumer body or brand partner "
                    "names the body and its reference (FR-CXM-038)."
                )


UPDATE_TYPES = [
    ("acknowledgement", "Acknowledgement"),
    ("progress", "Progress Update"),
    ("delay", "Delay Notice"),
    ("information_request", "Information Needed From Customer"),
    ("resolution_proposed", "Resolution Proposed"),
    ("reopened", "Reopened"),
    ("closure", "Closure Notice"),
]
ELECTRONIC = ("sms", "email", "whatsapp")


class FixComplaintUpdate(models.Model):
    """One status communication to the customer (spec fix.complaint.update,
    FR-CXM-033, BRU-CXM-07). An SMS, e-mail or WhatsApp update is queued on
    the S1 delivery service, which applies consent and the BTRC window; a
    call, letter or visit is recorded as made."""

    _name = "fix.complaint.update"
    _description = "Complaint Customer Update"
    _order = "sent_at desc, id desc"

    complaint_id = fields.Many2one("fix.complaint", required=True, ondelete="cascade", index=True)
    customer_id = fields.Many2one(related="complaint_id.customer_id", store=True)
    update_type = fields.Selection(UPDATE_TYPES, required=True, default="progress")
    channel = fields.Selection(
        [
            ("sms", "SMS"),
            ("email", "E-mail"),
            ("whatsapp", "WhatsApp"),
            ("phone_call", "Phone Call"),
            ("letter", "Letter"),
            ("in_person", "In Person"),
        ],
        required=True,
        default="sms",
    )
    content = fields.Text(required=True, string="What the Customer Is Told")
    to_address = fields.Char(
        string="Sent To", help="Number or e-mail; empty uses the customer's own on file."
    )
    state = fields.Selection(
        [("sent", "Sent / Made"), ("suppressed", "Not Sent")],
        readonly=True,
        default="sent",
    )
    not_sent_reason = fields.Char(readonly=True)
    sent_at = fields.Datetime(readonly=True)
    sent_by_id = fields.Many2one("res.users", readonly=True, string="Sent By")
    delivery_id = fields.Many2one("fix.notif.delivery", readonly=True, string="Delivery Row")

    @api.model_create_multi
    def create(self, vals_list):
        Complaint = self.env["fix.complaint"]
        for vals in vals_list:
            complaint = Complaint.browse(vals.get("complaint_id")).exists()
            if not complaint:
                raise ValidationError("Name the complaint this update is about.")
            if not (vals.get("content") or "").strip():
                raise ValidationError("Write what the customer is told.")
            utype = vals.get("update_type") or "progress"
            if complaint.state in ("closed", "rejected") and utype not in ("closure", "reopened"):
                raise ValidationError(
                    "Complaint %s is %s: only a closure notice can still be sent."
                    % (complaint.name, complaint.state)
                )
            vals["sent_by_id"] = self.env.user.id
            vals["sent_at"] = fields.Datetime.now()
        records = super().create(vals_list)
        records._deliver()
        return records

    def write(self, vals):
        if not self.env.su and set(vals) - {"delivery_id", "state", "not_sent_reason"}:
            raise UserError("A customer update is a record of what was said: it is not edited.")
        return super().write(vals)

    def _deliver(self):
        Delivery = self.env["fix.notif.delivery"]
        for rec in self:
            complaint = rec.complaint_id.sudo()
            if rec.channel not in ELECTRONIC:
                complaint.message_post(
                    body="Customer updated by %s (%s): %s"
                    % (rec.channel.replace("_", " "), rec.update_type, rec.content)
                )
                continue
            partner = complaint.customer_id
            address = (rec.to_address or "").strip()
            if not address:
                if rec.channel == "email":
                    address = (partner.email or "").strip()
                else:
                    address = (getattr(partner, "mobile", False) or partner.phone or "").strip()
            if not address:
                rec.sudo().write(
                    {
                        "state": "suppressed",
                        "not_sent_reason": "No %s address on file." % rec.channel,
                    }
                )
                continue
            delivery = Delivery.sudo().queue(
                channel=rec.channel,
                purpose="service_updates",
                partner=partner or None,
                to_address=address,
                body="1000FiX: %s (%s)। %s" % (complaint.name, rec.update_type, rec.content),
                subject="1000FiX complaint %s" % complaint.name,
                lawful_basis="contract",
                source_model="fix.complaint.update",
                source_id=rec.id,
                dedup_key="complaint-update:%d" % rec.id,
                operating_unit=complaint.operating_unit_id,
                company=complaint.company_id,
            )
            vals = {"delivery_id": delivery.id}
            if delivery.state == "suppressed":
                vals.update({"state": "suppressed", "not_sent_reason": delivery.consent_reason})
            rec.sudo().write(vals)
            complaint.message_post(
                body="Customer update %s by %s: %s"
                % (
                    "queued" if vals.get("state") != "suppressed" else "NOT sent",
                    rec.channel,
                    rec.content,
                )
            )
        return True


# ---------------------------------------------------------------------------
# Page 6: SLA by customer tier (FR-CXM-031)
# ---------------------------------------------------------------------------
class FixComplaintSlaRuleTier(models.Model):
    _inherit = "fix.complaint.sla.rule"

    loyalty_tier_id = fields.Many2one(
        "fix.loyalty.tier",
        string="Customer Tier",
        index=True,
        help="FR-CXM-031: applies to complaints from customers holding this membership "
        "tier. Empty: every customer.",
    )

    @api.model
    def _customer_tier(self, complaint):
        partner = complaint.customer_id
        if not partner or "fix.loyalty.account" not in self.env:
            return self.env["fix.loyalty.tier"]
        account = (
            self.env["fix.loyalty.account"]
            .sudo()
            .search([("partner_id", "=", partner.id), ("state", "=", "active")], limit=1)
        )
        return account.tier_id

    @api.model
    def _match(self, complaint):
        """The tier refines each scope: within the same scope a binding for the
        customer's tier wins over the tier-less one; a binding for another tier
        never applies."""
        tier = self._customer_tier(complaint)
        rules = self.search(
            [("severity", "=", complaint.severity), ("policy_id.active", "=", True)]
        ).filtered(lambda r: not r.loyalty_tier_id or (tier and r.loyalty_tier_id == tier))
        branch = complaint.service_order_id.branch_id
        unit = complaint.operating_unit_id
        for scoped in (
            rules.filtered(lambda r: r.branch_id and r.branch_id == branch),
            rules.filtered(lambda r: not r.branch_id and r.operating_unit_id == unit and unit),
            rules.filtered(lambda r: not r.branch_id and not r.operating_unit_id),
        ):
            for candidate in (
                scoped.filtered(lambda r: r.loyalty_tier_id),
                scoped.filtered(lambda r: not r.loyalty_tier_id),
            ):
                if candidate:
                    return candidate[:1]
        return self.browse()


# ---------------------------------------------------------------------------
# Page 8: journeys (FR-CXM-039) and coded VoC themes (FR-CXM-041)
# ---------------------------------------------------------------------------
class FixJourneyDefinition(models.Model):
    """A customer journey and its stages. Each stage names the instrument
    that measures it; the Journey Measurement report scores the stage from
    that instrument's responses (spec fix.journey.definition)."""

    _name = "fix.journey.definition"
    _description = "Customer Journey"
    _inherit = ["mail.thread"]
    _order = "code, id"

    code = fields.Char(required=True, tracking=True)
    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)", required=True, help="DE-17")
    description = fields.Text()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    stage_ids = fields.One2many("fix.journey.stage", "journey_id", string="Stages")
    stage_count = fields.Integer(compute="_compute_stage_count")

    def _compute_stage_count(self):
        for rec in self:
            rec.stage_count = len(rec.stage_ids)

    @api.constrains("code", "company_id")
    def _check_code_unique(self):
        for rec in self:
            if self.search_count(
                [
                    ("code", "=", rec.code),
                    ("company_id", "=", rec.company_id.id),
                    ("id", "!=", rec.id),
                ]
            ):
                raise ValidationError("Journey code %s is already used." % rec.code)


class FixJourneyStage(models.Model):
    _name = "fix.journey.stage"
    _description = "Customer Journey Stage"
    _order = "journey_id, sequence, id"

    journey_id = fields.Many2one(
        "fix.journey.definition", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, string="Stage")
    name_bn = fields.Char(string="Stage (Bengali)")
    touchpoint = fields.Char(
        help="Where the customer meets us at this stage (counter, SMS, visit...)."
    )
    template_id = fields.Many2one(
        "fix.survey.template",
        string="Measured By Instrument",
        ondelete="restrict",
        help="Empty: the stage is defined but not yet measured.",
    )
    effort_question_code = fields.Char(
        string="Effort Question Code",
        help="Optional: the instrument question that measures effort here.",
    )

    @api.constrains("template_id", "effort_question_code")
    def _check_effort_question(self):
        for rec in self:
            if rec.effort_question_code and not rec.template_id:
                raise ValidationError("An effort question needs the instrument it belongs to.")
            if (
                rec.effort_question_code
                and rec.effort_question_code not in rec.template_id.question_ids.mapped("code")
            ):
                raise ValidationError(
                    "Instrument %s has no question %s."
                    % (rec.template_id.display_name, rec.effort_question_code)
                )


class FixVocTheme(models.Model):
    """A theme coded from customer verbatims for a period (spec
    fix.voc.theme, FR-CXM-041). Until an M26 model extracts themes, the
    Customer Service Manager codes them; the frequency is the number of
    responses and complaints coded to it, never typed."""

    _name = "fix.voc.theme"
    _description = "Voice-of-Customer Theme"
    _inherit = ["mail.thread"]
    _order = "period desc, frequency desc, id"

    period = fields.Char(required=True, size=7, help="YYYY-MM", tracking=True)
    theme = fields.Char(required=True, tracking=True)
    theme_bn = fields.Char(string="Theme (Bengali)", required=True, help="DE-17")
    sentiment = fields.Selection(
        [("positive", "Positive"), ("neutral", "Neutral"), ("negative", "Negative")],
        required=True,
        default="negative",
    )
    driver = fields.Selection(
        [
            ("timeliness", "Timeliness"),
            ("professionalism", "Professionalism"),
            ("behaviour", "Staff Behaviour"),
            ("price", "Price / Billing"),
            ("quality", "Repair Quality"),
            ("parts", "Parts Availability"),
            ("communication", "Communication"),
            ("other", "Other"),
        ],
        string="Operational Driver",
    )
    survey_ids = fields.Many2many(
        "fix.survey",
        "fix_voc_theme_survey_rel",
        "theme_id",
        "survey_id",
        string="Survey Verbatims",
        domain=[("comment", "!=", False)],
    )
    complaint_ids = fields.Many2many(
        "fix.complaint",
        "fix_voc_theme_complaint_rel",
        "theme_id",
        "complaint_id",
        string="Complaints",
    )
    frequency = fields.Integer(compute="_compute_frequency", store=True)
    notes = fields.Text(string="Coding Notes")
    coded_by_id = fields.Many2one("res.users", readonly=True, default=lambda self: self.env.user)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    @api.depends("survey_ids", "complaint_ids")
    def _compute_frequency(self):
        for rec in self:
            rec.frequency = len(rec.survey_ids) + len(rec.complaint_ids)

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            p = rec.period or ""
            if (
                len(p) != 7
                or p[4] != "-"
                or not (p[:4].isdigit() and p[5:].isdigit())
                or not 1 <= int(p[5:]) <= 12
            ):
                raise ValidationError("The period is a month written YYYY-MM.")

    @api.constrains("survey_ids")
    def _check_verbatims(self):
        for rec in self:
            silent = rec.survey_ids.filtered(lambda s: not (s.comment or "").strip())
            if silent:
                raise ValidationError(
                    "A theme is coded from what customers wrote: %d linked response(s) have no comment."
                    % len(silent)
                )
