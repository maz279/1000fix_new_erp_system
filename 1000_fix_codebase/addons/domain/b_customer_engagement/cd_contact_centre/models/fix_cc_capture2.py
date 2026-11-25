# cd_contact_centre — M27 capture audit, second pass (19 Nov 2026).
#
# The 14 Nov pass gave every M27 sub-module page a "+ New". Read against the
# spec (§5 FR-CCE-001..058, §9 BRU-CCE, §10.1 owned entities, §11 AUT-CCE),
# the records the pages exist to produce still had no model:
#
#   page 1  fix.cc.callback        FR-CCE-003: a callback offered in place of
#                                  queueing, honoured inside the promised window
#           fix.cc.voicemail       FR-CCE-007 / AUT-CCE-11: out-of-hours
#                                  voicemail, queued as a conversation, with a
#                                  next-business-day commitment
#           fix.cc.oncall.rota     FR-CCE-008: who takes 16743 out of hours; the
#                                  queue's closed-hours diversion names them
#   page 6  fix.cc.contact.forecast  FR-CCE-050 (spec 10.1 fix.contact.forecast):
#                                  volume by channel and interval, scored
#                                  against the contacts that actually arrived
#   page 7  fix.cc.qa.calibration  FR-CCE-055: several evaluators score one
#                                  interaction; the spread shows consistency
#           fix.cc.qa.coaching     FR-CCE-056: coaching from an evaluation, and
#                                  the agent's later QA scores as the improvement
#   page 8  fix.cc.notif.throttle  FR-CCE-044 / BRU-CCE-15 / AUT-CCE-13: the
#                                  per-party volume ceiling, enforced at send
#   page 9  fix.cc.channel.preference  FR-CCE-046 / BRU-CCE-13 (spec 10.1
#                                  fix.channel.preference): per-category opt-out,
#                                  never for a mandatory transactional category,
#                                  enforced at send
#           fix.cc.urgency.challenge   FR-CCE-041 / BRU-CCE-04: a message's
#                                  classification challenged and decided by
#                                  someone other than the challenger
#
# Times are stored UTC; the contact centre works in Bangladesh Standard Time.
from __future__ import annotations

from datetime import datetime, time, timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_cc_queue_ops import BST_OFFSET_HOURS

SUPERVISOR = "cd_contact_centre.group_cc_supervisor"

# Delivery purposes (fix.notif.delivery.purpose) a customer may NOT switch
# off: BRU-CCE-13 "mandatory transactional notifications cannot be disabled".
MANDATORY_CATEGORIES = frozenset({"service_updates", "collections", "call_recording"})
PREFERENCE_CATEGORIES = [
    ("service_updates", "Service Updates (mandatory)"),
    ("collections", "Payment & Collection Notices (mandatory)"),
    ("marketing", "Offers & Promotions"),
    ("research", "Surveys & Research"),
    ("profiling", "Personalised Recommendations"),
]
PREFERENCE_CHANNELS = [
    ("sms", "SMS"),
    ("whatsapp", "WhatsApp"),
    ("email", "E-mail"),
    ("push", "App Notification"),
    ("voice", "Phone Call"),
]
# Urgency classes (FR-CCE-041) and the delivery purposes that carry them.
URGENCY_CLASSES = [
    ("transactional_urgent", "Transactional - urgent"),
    ("transactional_routine", "Transactional - routine"),
    ("promotional", "Promotional"),
]
PURPOSE_CLASS = {
    "service_updates": "transactional_routine",
    "collections": "transactional_routine",
    "call_recording": "transactional_routine",
    "marketing": "promotional",
    "research": "promotional",
    "profiling": "promotional",
}


def _bst(dt):
    return dt + timedelta(hours=BST_OFFSET_HOURS) if dt else dt


def _utc_from_bst(day, hour):
    return datetime.combine(day, time(0)) + timedelta(hours=hour - BST_OFFSET_HOURS)


def _is_supervisor(env):
    return env.su or env.user.has_group(SUPERVISOR)


def _require_supervisor(env, what):
    if not _is_supervisor(env):
        raise AccessError("%s is a Contact Centre Supervisor decision." % what)


# =================================================================== page 1
class FixCcCallback(models.Model):
    """A callback promised to a caller instead of keeping them queued (FR-CCE-003).

    The promise is the window. Each attempt is logged; reaching the customer
    closes it, and a window that passes with nobody reached is marked missed
    by the hourly sweep, which is what the callback service level counts."""

    _name = "fix.cc.callback"
    _description = "Contact Centre Callback Request"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "promised_by, id"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    phone = fields.Char(string="Number To Call", required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Customer", ondelete="set null")
    conversation_id = fields.Many2one(
        "fix.conversation", string="From Conversation", ondelete="set null", index=True
    )
    queue_id = fields.Many2one("fix.cc.queue", string="Queue")
    reason = fields.Char(string="What It Is About", required=True)
    language = fields.Selection([("bn", "Bengali"), ("en", "English")], default="bn")
    promised_from = fields.Datetime(string="Call From", required=True, tracking=True)
    promised_by = fields.Datetime(string="Call By", required=True, tracking=True)
    assigned_user_id = fields.Many2one("res.users", string="Assigned Agent", tracking=True)
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("attempted", "Attempted - not reached"),
            ("completed", "Completed"),
            ("missed", "Missed - window passed"),
            ("cancelled", "Cancelled"),
        ],
        default="requested",
        required=True,
        tracking=True,
    )
    attempt_count = fields.Integer(readonly=True, copy=False)
    last_attempt_at = fields.Datetime(readonly=True, copy=False)
    last_attempt_note = fields.Char(readonly=True, copy=False)
    completed_at = fields.Datetime(readonly=True, copy=False)
    completed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    within_window = fields.Boolean(
        string="Honoured In Window",
        readonly=True,
        copy=False,
        help="Reached between Call From and Call By.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "attempt_count",
            "last_attempt_at",
            "last_attempt_note",
            "completed_at",
            "completed_by_id",
            "within_window",
        }

    @api.depends("phone", "promised_by")
    def _compute_name(self):
        for rec in self:
            when = _bst(rec.promised_by)
            rec.name = "Callback %s by %s" % (
                rec.phone or "?",
                when.strftime("%d %b %H:%M") if when else "?",
            )

    @api.constrains("promised_from", "promised_by")
    def _check_window(self):
        for rec in self:
            if rec.promised_from and rec.promised_by and rec.promised_by <= rec.promised_from:
                raise ValidationError("A callback's Call By must be after its Call From.")

    def action_log_attempt(self, reached=False, note=""):
        """One attempt to call back. Reached closes it; not reached keeps it open."""
        now = fields.Datetime.now()
        for rec in self:
            if rec.state not in ("requested", "attempted"):
                raise UserError(
                    "Only an open callback can be attempted (this one is %s)." % rec.state
                )
            if not reached and not (note or "").strip():
                raise UserError("Say what happened on an attempt that did not reach the customer.")
            vals = {
                "attempt_count": rec.attempt_count + 1,
                "last_attempt_at": now,
                "last_attempt_note": (note or "").strip() or "Reached",
            }
            if reached:
                vals.update(
                    state="completed",
                    completed_at=now,
                    completed_by_id=self.env.user.id,
                    within_window=bool(rec.promised_from <= now <= rec.promised_by),
                )
            else:
                vals["state"] = "attempted"
            rec._guarded().write(vals)
        return True

    def action_mark_reached(self):
        return self.action_log_attempt(reached=True)

    def action_log_failed_attempt(self, note=""):
        return self.action_log_attempt(reached=False, note=note)

    def action_cancel(self, reason=""):
        for rec in self:
            if rec.state not in ("requested", "attempted"):
                raise UserError("Only an open callback can be cancelled.")
            rec._guarded().write(
                {"state": "cancelled", "last_attempt_note": (reason or "").strip()}
            )
        return True

    @api.model
    def _cron_mark_missed(self):
        late = self.sudo().search(
            [
                ("state", "in", ("requested", "attempted")),
                ("promised_by", "<", fields.Datetime.now()),
            ]
        )
        late._guarded().write({"state": "missed"})
        return len(late)


class FixCcVoicemail(models.Model):
    """A voicemail left out of hours (FR-CCE-007, AUT-CCE-11).

    Until the telephony layer posts voicemail itself, the agent who clears the
    voicemail box logs each message here. Queuing it opens a conversation in
    the voice queue, so it is answered and measured like any other contact;
    the commitment is the next business day (Friday and Saturday are not)."""

    _name = "fix.cc.voicemail"
    _description = "Contact Centre Voicemail"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "received_at desc, id desc"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Contact Centre Operating Unit", required=True, index=True
    )
    caller_number = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Customer", ondelete="set null")
    received_at = fields.Datetime(required=True, default=fields.Datetime.now)
    duration_seconds = fields.Integer(string="Length (seconds)")
    queue_id = fields.Many2one("fix.cc.queue", string="Queue")
    language = fields.Selection([("bn", "Bengali"), ("en", "English")], default="bn")
    transcript = fields.Text(help="What the caller said, typed or transcribed.")
    respond_by = fields.Date(
        string="Respond By",
        compute="_compute_respond_by",
        store=True,
        help="The next business day after the message (BST), skipping Friday and Saturday.",
    )
    state = fields.Selection(
        [("new", "New"), ("queued", "Queued as a conversation"), ("discarded", "Discarded")],
        default="new",
        required=True,
        tracking=True,
    )
    conversation_id = fields.Many2one(
        "fix.conversation", string="Conversation", readonly=True, copy=False, ondelete="set null"
    )
    conversation_state = fields.Selection(
        related="conversation_id.state", string="Conversation State"
    )
    discard_reason = fields.Char(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "conversation_id", "discard_reason"}

    @api.depends("caller_number", "received_at")
    def _compute_name(self):
        for rec in self:
            when = _bst(rec.received_at)
            rec.name = "Voicemail %s %s" % (
                rec.caller_number or "?",
                when.strftime("%d %b %H:%M") if when else "",
            )

    @api.depends("received_at")
    def _compute_respond_by(self):
        for rec in self:
            if not rec.received_at:
                rec.respond_by = False
                continue
            day = _bst(rec.received_at).date() + timedelta(days=1)
            while day.weekday() in (4, 5):  # Friday, Saturday
                day += timedelta(days=1)
            rec.respond_by = day

    def action_queue_as_conversation(self):
        """Open the voicemail as a voice conversation in its queue."""
        Conversation = self.env["fix.conversation"]
        for rec in self:
            if rec.state != "new":
                raise UserError("This voicemail is already %s." % rec.state)
            text = (rec.transcript or "").strip()
            conv = Conversation.create(
                {
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "channel": "voice",
                    "contact_identity": rec.caller_number,
                    "customer_id": rec.partner_id.id or False,
                    "queue_id": rec.queue_id.id or False,
                    "started_at": rec.received_at,
                    "intent": ("Voicemail: %s" % text[:80]) if text else "Voicemail",
                }
            )
            if text:
                self.env["fix.conversation.turn"].create(
                    {
                        "conversation_id": conv.id,
                        "speaker": "customer",
                        "text": text,
                        "lang": rec.language or "bn",
                    }
                )
            rec._guarded().write({"state": "queued", "conversation_id": conv.id})
        return True

    def action_discard(self, reason=""):
        for rec in self:
            if rec.state != "new":
                raise UserError("Only a new voicemail can be discarded.")
            if not (reason or "").strip():
                raise UserError("Say why the voicemail is discarded (silent, wrong number...).")
            rec._guarded().write({"state": "discarded", "discard_reason": reason.strip()})
        return True


class FixCcOncallRota(models.Model):
    """Who takes the hotline out of hours (FR-CCE-008, 24/7 support model).

    One primary per queue at a time. While a queue is shut, its diversion
    names the primary on call, so the closed-hours route reaches a person."""

    _name = "fix.cc.oncall.rota"
    _description = "Contact Centre On-Call Rota"
    _inherit = ["mail.thread"]
    _order = "start_at desc, queue_id"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    queue_id = fields.Many2one("fix.cc.queue", string="Queue", required=True, index=True)
    user_id = fields.Many2one("res.users", string="On Call", required=True, tracking=True)
    on_call_phone = fields.Char(string="On-Call Number", required=True)
    role = fields.Selection(
        [("primary", "Primary"), ("backup", "Backup")], default="primary", required=True
    )
    start_at = fields.Datetime(string="From", required=True, tracking=True)
    end_at = fields.Datetime(string="Until", required=True, tracking=True)
    note = fields.Char()
    active = fields.Boolean(default=True)

    @api.depends("queue_id", "user_id", "start_at", "role")
    def _compute_name(self):
        for rec in self:
            when = _bst(rec.start_at)
            rec.name = "%s on call for %s from %s (%s)" % (
                rec.user_id.name or "?",
                rec.queue_id.name or "?",
                when.strftime("%d %b %H:%M") if when else "?",
                rec.role or "",
            )

    @api.constrains("start_at", "end_at", "queue_id", "role", "active")
    def _check_cover(self):
        for rec in self:
            if rec.end_at <= rec.start_at:
                raise ValidationError("An on-call slot must end after it starts.")
            if rec.role != "primary" or not rec.active:
                continue
            clash = self.search(
                [
                    ("id", "!=", rec.id),
                    ("queue_id", "=", rec.queue_id.id),
                    ("role", "=", "primary"),
                    ("start_at", "<", rec.end_at),
                    ("end_at", ">", rec.start_at),
                ],
                limit=1,
            )
            if clash:
                raise ValidationError(
                    "%s already has a primary on call for part of that time (%s)."
                    % (rec.queue_id.name, clash.name)
                )

    @api.model
    def on_call_for(self, queue, at=None):
        """The primary on call for the queue at a moment, else the backup."""
        at = at or fields.Datetime.now()
        rows = self.sudo().search(
            [("queue_id", "=", queue.id), ("start_at", "<=", at), ("end_at", ">", at)],
            order="role desc",  # 'primary' sorts after 'backup': desc puts it first
        )
        return rows[:1]


class FixCcQueueOncall(models.Model):
    _inherit = "fix.cc.queue"

    def current_diversion(self):
        res = super().current_diversion()
        if res and not self.is_open_now():
            duty = self.env["fix.cc.oncall.rota"].on_call_for(self)
            if duty:
                res = dict(
                    res,
                    oncall_user=duty.user_id,
                    oncall_phone=duty.on_call_phone,
                    reason="%s On call: %s (%s)."
                    % (res["reason"], duty.user_id.name, duty.on_call_phone),
                )
        return res


# =================================================================== page 6
class FixCcContactForecast(models.Model):
    """Forecast contact volume for one channel, queue and hour (FR-CCE-050).

    The actual is counted from the conversations that arrived in that hour,
    and the history baseline is the same hour on the four previous same
    weekdays: a forecast is only worth keeping if it is scored."""

    _name = "fix.cc.contact.forecast"
    _description = "Contact Volume Forecast"
    _order = "forecast_date desc, interval_hour, channel"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    channel = fields.Selection(
        selection=lambda self: self.env["fix.conversation"]._fields["channel"].selection,
        required=True,
        default="voice",
    )
    queue_id = fields.Many2one("fix.cc.queue", string="Queue / Skill")
    forecast_date = fields.Date(required=True)
    interval_hour = fields.Integer(string="Hour (BST, 0-23)", required=True, default=9)
    forecast_volume = fields.Integer(string="Forecast Contacts", required=True)
    basis = fields.Selection(
        [
            ("history", "History of the same hour"),
            ("driver", "Known driver (campaign, outage, holiday)"),
            ("judgement", "Planner judgement"),
        ],
        default="history",
        required=True,
    )
    driver_note = fields.Char(string="Known Driver")
    actual_volume = fields.Integer(string="Actual Contacts", compute="_compute_actuals")
    history_baseline = fields.Float(string="Same-Hour History (4 wks)", compute="_compute_actuals")
    variance_pct = fields.Float(string="Forecast Error %", compute="_compute_actuals")

    @api.depends("channel", "forecast_date", "interval_hour", "queue_id")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s %s %02d:00%s" % (
                rec.channel or "?",
                rec.forecast_date or "?",
                rec.interval_hour or 0,
                (" " + rec.queue_id.name) if rec.queue_id else "",
            )

    @api.constrains("interval_hour", "forecast_volume", "channel", "queue_id", "forecast_date")
    def _check_values(self):
        for rec in self:
            if not 0 <= rec.interval_hour <= 23:
                raise ValidationError("The interval hour is 0 to 23 (BST).")
            if rec.forecast_volume < 0:
                raise ValidationError("A forecast cannot be negative.")
            # Not an SQL unique: Postgres treats an empty queue as distinct,
            # so two "all queues" forecasts for one hour would both be kept.
            if self.search_count(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("channel", "=", rec.channel),
                    ("queue_id", "=", rec.queue_id.id or False),
                    ("forecast_date", "=", rec.forecast_date),
                    ("interval_hour", "=", rec.interval_hour),
                ]
            ):
                raise ValidationError(
                    "That channel, queue and hour already has a forecast: change it instead."
                )

    def _count(self, day):
        start = _utc_from_bst(day, self.interval_hour)
        domain = [
            ("company_id", "=", self.company_id.id),
            ("channel", "=", self.channel),
            ("started_at", ">=", start),
            ("started_at", "<", start + timedelta(hours=1)),
        ]
        if self.queue_id:
            domain.append(("queue_id", "=", self.queue_id.id))
        return self.env["fix.conversation"].sudo().search_count(domain)

    @api.depends("channel", "forecast_date", "interval_hour", "queue_id", "forecast_volume")
    def _compute_actuals(self):
        for rec in self:
            if not (rec.forecast_date and rec.channel):
                rec.actual_volume = 0
                rec.history_baseline = 0.0
                rec.variance_pct = 0.0
                continue
            rec.actual_volume = rec._count(rec.forecast_date)
            past = [rec._count(rec.forecast_date - timedelta(weeks=w)) for w in range(1, 5)]
            rec.history_baseline = sum(past) / 4.0
            if rec.actual_volume:
                rec.variance_pct = round(
                    (rec.forecast_volume - rec.actual_volume) * 100.0 / rec.actual_volume, 1
                )
            else:
                rec.variance_pct = 0.0


# =================================================================== page 7
class FixCcQaCalibration(models.Model):
    """A calibration session (FR-CCE-055): several evaluators score the same
    interaction so their scoring can be compared.

    The spread (highest minus lowest) is the consistency measure. A supervisor
    closes the session with the agreed score; at least two evaluators must have
    scored, and the agent who handled the interaction is never one of them."""

    _name = "fix.cc.qa.calibration"
    _description = "QA Calibration Session"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "session_date desc, id desc"

    name = fields.Char(string="Session", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    conversation_id = fields.Many2one(
        "fix.conversation", string="Interaction Scored", required=True, ondelete="restrict"
    )
    rubric_id = fields.Many2one("fix.cc.qa.rubric", string="Scorecard")
    facilitator_id = fields.Many2one(
        "res.users", string="Facilitator", required=True, default=lambda self: self.env.user
    )
    session_date = fields.Date(required=True, default=fields.Date.context_today)
    tolerance = fields.Integer(
        string="Tolerance (points)",
        default=10,
        required=True,
        help="Scores within this many points of each other count as consistent.",
    )
    line_ids = fields.One2many(
        "fix.cc.qa.calibration.line", "session_id", string="Evaluator Scores"
    )
    spread = fields.Integer(compute="_compute_spread", store=True)
    mean_score = fields.Float(compute="_compute_spread", store=True)
    consistent = fields.Boolean(compute="_compute_spread", store=True)
    agreed_score = fields.Integer(readonly=True, copy=False)
    outcome_note = fields.Text(readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], default="open", required=True, tracking=True
    )
    closed_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "agreed_score",
            "outcome_note",
            "closed_by_id",
        }

    @api.depends("line_ids.score", "tolerance")
    def _compute_spread(self):
        for rec in self:
            scores = rec.line_ids.mapped("score")
            rec.spread = (max(scores) - min(scores)) if scores else 0
            rec.mean_score = round(sum(scores) / len(scores), 1) if scores else 0.0
            rec.consistent = bool(len(scores) >= 2 and rec.spread <= rec.tolerance)

    def write(self, vals):
        if (
            self.filtered(lambda r: r.state == "closed")
            and not self._fix_guard_has_token()
            and set(vals) - {"message_main_attachment_id"}
        ):
            raise UserError("A closed calibration session is kept as evidence.")
        return super().write(vals)

    def action_close(self, agreed_score=None, note=""):
        _require_supervisor(self.env, "Closing a calibration session")
        for rec in self:
            if rec.state != "open":
                raise UserError("This session is already closed.")
            if len(rec.line_ids) < 2:
                raise UserError("A calibration needs at least two evaluators' scores.")
            raw = rec.mean_score if agreed_score in (None, False, "") else agreed_score
            try:
                score = int(round(float(str(raw).strip())))
            except ValueError as exc:
                raise UserError("The agreed score is a number from 0 to 100.") from exc
            if not 0 <= score <= 100:
                raise UserError("The agreed score is 0 to 100.")
            rec._guarded().write(
                {
                    "state": "closed",
                    "agreed_score": score,
                    "outcome_note": (note or "").strip(),
                    "closed_by_id": self.env.user.id,
                }
            )
        return True


class FixCcQaCalibrationLine(models.Model):
    _name = "fix.cc.qa.calibration.line"
    _description = "QA Calibration Score"
    _order = "session_id, id"

    session_id = fields.Many2one(
        "fix.cc.qa.calibration", required=True, ondelete="cascade", index=True
    )
    evaluator_id = fields.Many2one("res.users", string="Evaluator", required=True)
    score = fields.Integer(required=True)
    note = fields.Char()

    _sql_constraints = [
        (
            "evaluator_once",
            "unique(session_id, evaluator_id)",
            "Each evaluator scores a session once.",
        )
    ]

    @api.constrains("score", "evaluator_id")
    def _check_line(self):
        for rec in self:
            if not 0 <= rec.score <= 100:
                raise ValidationError("A calibration score is 0 to 100.")
            if rec.evaluator_id and rec.evaluator_id == rec.session_id.conversation_id.agent_id:
                raise ValidationError("The agent who handled the interaction cannot calibrate it.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            session = self.env["fix.cc.qa.calibration"].browse(vals.get("session_id"))
            if session.exists() and session.state == "closed":
                raise UserError("A closed calibration session takes no more scores.")
            evaluator = vals.get("evaluator_id")
            if evaluator and evaluator != self.env.uid and not _is_supervisor(self.env):
                raise AccessError("An evaluator enters their own calibration score.")
            # checked before the insert: a refusal must leave no row behind
            if evaluator and session.exists() and evaluator == session.conversation_id.agent_id.id:
                raise ValidationError("The agent who handled the interaction cannot calibrate it.")
        return super().create(vals_list)

    def write(self, vals):
        if self.filtered(lambda r: r.session_id.state == "closed"):
            raise UserError("A closed calibration session is kept as evidence.")
        return super().write(vals)


class FixCcQaCoaching(models.Model):
    """Coaching recorded from an evaluation (FR-CCE-056).

    The baseline is the evaluation's score; the improvement is the agent's
    average QA score on evaluations made after the session. The agent
    acknowledges it; the coach is never the agent."""

    _name = "fix.cc.qa.coaching"
    _description = "QA Coaching Session"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "session_date desc, id desc"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    agent_id = fields.Many2one(
        "res.users", string="Agent", required=True, index=True, tracking=True
    )
    evaluation_id = fields.Many2one(
        "fix.cc.qa.evaluation", string="From Evaluation", ondelete="set null"
    )
    coach_id = fields.Many2one(
        "res.users", string="Coach", required=True, default=lambda self: self.env.user
    )
    session_date = fields.Date(required=True, default=fields.Date.context_today)
    focus_area = fields.Char(string="Focus", required=True)
    agreed_actions = fields.Text(string="Agreed Actions", required=True)
    follow_up_date = fields.Date(string="Review On")
    baseline_score = fields.Integer(compute="_compute_scores", store=True)
    later_score = fields.Float(string="Average Score Since", compute="_compute_later")
    later_count = fields.Integer(string="Evaluations Since", compute="_compute_later")
    improvement = fields.Float(compute="_compute_later")
    state = fields.Selection(
        [("planned", "Recorded"), ("acknowledged", "Acknowledged by the agent")],
        default="planned",
        required=True,
        tracking=True,
    )
    acknowledged_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "acknowledged_at"}

    @api.depends("agent_id", "focus_area", "session_date")
    def _compute_name(self):
        for rec in self:
            rec.name = "Coaching %s: %s (%s)" % (
                rec.agent_id.name or "?",
                rec.focus_area or "?",
                rec.session_date or "",
            )

    @api.depends("evaluation_id.score")
    def _compute_scores(self):
        for rec in self:
            rec.baseline_score = rec.evaluation_id.score if rec.evaluation_id else 0

    @api.depends("agent_id", "session_date", "baseline_score")
    def _compute_later(self):
        Eval = self.env["fix.cc.qa.evaluation"].sudo()
        for rec in self:
            later = Eval.browse()
            if rec.agent_id and rec.session_date:
                later = Eval.search(
                    [
                        ("agent_id", "=", rec.agent_id.id),
                        ("evaluated_at", ">", datetime.combine(rec.session_date, time.max)),
                    ]
                )
            scores = later.mapped("score")
            rec.later_count = len(scores)
            rec.later_score = round(sum(scores) / len(scores), 1) if scores else 0.0
            rec.improvement = (
                round(rec.later_score - rec.baseline_score, 1)
                if scores and rec.evaluation_id
                else 0.0
            )

    @api.constrains("agent_id", "coach_id", "evaluation_id")
    def _check_parties(self):
        for rec in self:
            if rec.agent_id == rec.coach_id:
                raise ValidationError("An agent does not coach themselves.")
            if rec.evaluation_id and rec.evaluation_id.agent_id != rec.agent_id:
                raise ValidationError("The evaluation coached from is another agent's.")

    def action_acknowledge(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Already acknowledged.")
            if self.env.user != rec.agent_id and not self.env.su:
                raise AccessError("Only the coached agent acknowledges the coaching.")
            rec._guarded().write(
                {"state": "acknowledged", "acknowledged_at": fields.Datetime.now()}
            )
        return True


# =================================================================== page 8
class FixCcNotifThrottle(models.Model):
    """The per-party volume ceiling for one purpose (FR-CCE-044, BRU-CCE-15).

    At send, a party who has already been sent the maximum for the period has
    the new message deferred until the oldest one in the window ages out
    (AUT-CCE-13). Service updates are never throttled: a repair milestone is
    not fatigue."""

    _name = "fix.cc.notif.throttle"
    _description = "Notification Volume Throttle"
    _inherit = ["mail.thread"]
    _order = "purpose, channel"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    purpose = fields.Selection(
        [
            ("marketing", "Marketing"),
            ("research", "Research & Analytics"),
            ("profiling", "Profiling"),
            ("collections", "Debt Collection"),
        ],
        required=True,
        tracking=True,
    )
    channel = fields.Selection(
        PREFERENCE_CHANNELS, string="Channel (empty = every channel)", tracking=True
    )
    max_messages = fields.Integer(
        string="Maximum Messages", required=True, default=3, tracking=True
    )
    period_hours = fields.Integer(string="Per (hours)", required=True, default=168, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    note = fields.Char(string="Why This Ceiling")

    @api.depends("purpose", "channel", "max_messages", "period_hours")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s%s: %d per %dh" % (
                rec.purpose or "?",
                (" / " + rec.channel) if rec.channel else "",
                rec.max_messages or 0,
                rec.period_hours or 0,
            )

    @api.constrains("max_messages", "period_hours", "purpose", "channel", "active", "company_id")
    def _check_rule(self):
        for rec in self:
            if rec.max_messages < 1 or rec.period_hours < 1:
                raise ValidationError("A throttle allows at least 1 message per at least 1 hour.")
            if rec.active and self.search_count(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("purpose", "=", rec.purpose),
                    ("channel", "=", rec.channel or False),
                ]
            ):
                raise ValidationError("That purpose and channel already has an active throttle.")

    @api.model
    def rule_for(self, purpose, channel, company):
        rules = self.sudo().search(
            [("purpose", "=", purpose), ("company_id", "in", [company.id, False])]
        )
        return (
            rules.filtered(lambda r: r.channel == channel)[:1]
            or rules.filtered(lambda r: not r.channel)[:1]
        )


class FixNotifDeliveryCapture2(models.Model):
    _inherit = "fix.notif.delivery"

    preference_id = fields.Many2one(
        "fix.cc.channel.preference",
        string="Customer Preference Applied",
        readonly=True,
        ondelete="set null",
    )
    throttle_id = fields.Many2one(
        "fix.cc.notif.throttle", string="Throttle Applied", readonly=True, ondelete="set null"
    )
    throttled_until = fields.Datetime(readonly=True)

    @api.model
    def _fix_preference_verdict(self, partner, purpose, channel, verdict):
        verdict = super()._fix_preference_verdict(partner, purpose, channel, verdict)
        if not verdict.get("allowed") or not partner or purpose in MANDATORY_CATEGORIES:
            return verdict
        pref = self.env["fix.cc.channel.preference"].preference_for(partner, purpose)
        if pref and pref.opted_out:
            return dict(
                verdict,
                allowed=False,
                decision="preference_opt_out",
                reason="The customer opted out of %s messages in the preference centre "
                "(recorded %s, %s)." % (purpose, pref.recorded_at, pref.source),
                preference_id=pref.id,
            )
        return verdict

    @api.model
    def _fix_throttle_vals(self, vals, partner, address):
        vals = super()._fix_throttle_vals(vals, partner, address)
        company = self.env["res.company"].browse(vals.get("company_id")) or self.env.company
        rule = self.env["fix.cc.notif.throttle"].rule_for(vals["purpose"], vals["channel"], company)
        if not rule:
            return vals
        window_start = fields.Datetime.now() - timedelta(hours=rule.period_hours)
        domain = [
            ("purpose", "=", vals["purpose"]),
            ("state", "in", ("queued", "sent", "delivered", "dry_run")),
            ("queued_at", ">=", window_start),
        ]
        if rule.channel:
            domain.append(("channel", "=", rule.channel))
        if partner:
            domain.append(("partner_id", "=", partner.id))
        else:
            domain.append(("to_address", "=", address))
        recent = self.sudo().search(domain, order="queued_at")
        if len(recent) < rule.max_messages:
            return vals
        oldest = recent[len(recent) - rule.max_messages]
        until = (oldest.queued_at or fields.Datetime.now()) + timedelta(hours=rule.period_hours)
        current = vals.get("next_attempt_at") or fields.Datetime.now()
        return dict(
            vals,
            next_attempt_at=max(current, until),
            throttle_id=rule.id,
            throttled_until=until,
        )

    @api.model
    def queue(self, channel, purpose, *args, **kwargs):
        rec = super().queue(channel, purpose, *args, **kwargs)
        # The preference that suppressed it is the evidence; stamp it.
        if (
            rec.state == "suppressed"
            and rec.consent_decision == "preference_opt_out"
            and rec.partner_id
        ):
            pref = self.env["fix.cc.channel.preference"].preference_for(rec.partner_id, purpose)
            if pref and not rec.preference_id:
                rec.sudo().write({"preference_id": pref.id})
        return rec


# =================================================================== page 9
class FixCcChannelPreference(models.Model):
    """A customer's preference for one notification category (FR-CCE-046).

    Opting out is honoured at send for the optional categories. Service
    updates and payment notices are mandatory (BRU-CCE-13): a customer can
    say which channel they prefer for them, never switch them off. Consent
    (M33) still decides whether a promotional message may go at all; this
    record can only narrow what consent allows."""

    _name = "fix.cc.channel.preference"
    _description = "Customer Notification Preference"
    _inherit = ["mail.thread"]
    _order = "partner_id, category"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True, ondelete="cascade"
    )
    category = fields.Selection(PREFERENCE_CATEGORIES, required=True, tracking=True)
    mandatory = fields.Boolean(compute="_compute_mandatory", store=True)
    preferred_channel = fields.Selection(PREFERENCE_CHANNELS, tracking=True)
    opted_out = fields.Boolean(string="Opted Out", tracking=True)
    source = fields.Selection(
        [
            ("hotline", "Told the hotline (16743)"),
            ("branch", "At a branch"),
            ("portal", "Customer portal / app"),
            ("written", "In writing"),
        ],
        required=True,
        default="hotline",
    )
    recorded_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    recorded_by_id = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "one_per_category",
            "unique(partner_id, category, active)",
            "The customer already has a preference for that category: change it.",
        )
    ]

    @api.depends("partner_id", "category", "opted_out", "preferred_channel")
    def _compute_name(self):
        labels = dict(PREFERENCE_CATEGORIES)
        for rec in self:
            rec.name = "%s - %s: %s" % (
                rec.partner_id.name or "?",
                labels.get(rec.category, rec.category or "?"),
                "opted out" if rec.opted_out else (rec.preferred_channel or "any channel"),
            )

    @api.depends("category")
    def _compute_mandatory(self):
        for rec in self:
            rec.mandatory = rec.category in MANDATORY_CATEGORIES

    @api.constrains("category", "opted_out")
    def _check_mandatory(self):
        for rec in self:
            if rec.opted_out and rec.category in MANDATORY_CATEGORIES:
                raise ValidationError(
                    "Service updates and payment notices are mandatory (BRU-CCE-13): the "
                    "customer can choose the channel, not switch them off."
                )

    def write(self, vals):
        if {"opted_out", "preferred_channel", "category"} & set(vals):
            vals = dict(vals, recorded_at=fields.Datetime.now(), recorded_by_id=self.env.user.id)
        return super().write(vals)

    @api.model
    def preference_for(self, partner, category):
        return self.sudo().search(
            [("partner_id", "=", partner.id), ("category", "=", category)], limit=1
        )


class FixCcUrgencyChallenge(models.Model):
    """A challenge to how a message was classified (FR-CCE-041, BRU-CCE-04).

    The classification decides whether consent, DND and the overnight window
    apply, so labelling a promotion as a transactional update bypasses all
    three. Anyone may challenge a sent message; a supervisor who did not raise
    the challenge decides it, and an upheld challenge is a disciplinary
    matter for the module that raised the message."""

    _name = "fix.cc.urgency.challenge"
    _description = "Notification Classification Challenge"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "raised_at desc, id desc"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    delivery_id = fields.Many2one(
        "fix.notif.delivery", string="Message Challenged", required=True, ondelete="restrict"
    )
    claimed_purpose = fields.Selection(related="delivery_id.purpose", string="Sent As")
    claimed_class = fields.Selection(URGENCY_CLASSES, compute="_compute_claimed", store=True)
    source_model = fields.Char(related="delivery_id.source_model", string="Raised By Module")
    proposed_class = fields.Selection(URGENCY_CLASSES, string="Should Have Been", required=True)
    reason = fields.Text(string="Why", required=True)
    raised_by_id = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)
    raised_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    state = fields.Selection(
        [("open", "Open"), ("upheld", "Upheld - misclassified"), ("rejected", "Rejected")],
        default="open",
        required=True,
        tracking=True,
    )
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_at = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Text(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "decided_by_id",
            "decided_at",
            "decision_note",
            "raised_by_id",
            "raised_at",
        }

    @api.depends("delivery_id", "proposed_class")
    def _compute_name(self):
        for rec in self:
            rec.name = "Challenge: delivery %s should be %s" % (
                rec.delivery_id.id or "?",
                rec.proposed_class or "?",
            )

    @api.depends("delivery_id.purpose")
    def _compute_claimed(self):
        for rec in self:
            rec.claimed_class = PURPOSE_CLASS.get(rec.delivery_id.purpose) or False

    @api.constrains("proposed_class", "claimed_class")
    def _check_differs(self):
        for rec in self:
            if rec.claimed_class and rec.proposed_class == rec.claimed_class:
                raise ValidationError("The challenge must propose a different classification.")

    def _decide(self, state, note):
        _require_supervisor(self.env, "Deciding a classification challenge")
        for rec in self:
            if rec.state != "open":
                raise UserError("This challenge is already decided.")
            if rec.raised_by_id == self.env.user and not self.env.su:
                raise UserError(
                    "Segregation of duties: whoever raised a challenge does not decide it."
                )
            if not (note or "").strip():
                raise UserError("Record why the challenge is decided this way.")
            rec._guarded().write(
                {
                    "state": state,
                    "decided_by_id": self.env.user.id,
                    "decided_at": fields.Datetime.now(),
                    "decision_note": note.strip(),
                }
            )
        return True

    def action_uphold(self, note=""):
        return self._decide("upheld", note)

    def action_reject(self, note=""):
        return self._decide("rejected", note)
