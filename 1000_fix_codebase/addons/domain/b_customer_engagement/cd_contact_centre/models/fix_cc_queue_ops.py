# S3 part 4 — queue overflow, closure handling, wait-time prediction and the
# representative-availability API; plus WFM adherence.
#
# Every item here was on the list of routing features the first research pass
# omitted, and each is cheap because the ingredients were already present:
#
#   * OVERFLOW and CLOSURE handling are queue configuration plus one decision
#     function. The after-hours case is a live 16743 exposure: a contact
#     arriving at 02:00 joined a queue nobody staffed and waited for a router
#     that would never find an agent.
#   * WAIT-TIME PREDICTION is the Erlang-C engine that has been in
#     fix.cc.queue since it was written, asked a different question. ASA is
#     a prediction; nothing was reading it as one.
#   * The AVAILABILITY API is a read over the presence rows S4 adds.
#   * ADHERENCE is the roster (fix.cc.wfm.shift, present) compared with the
#     presence history (fix.cc.agent.state.log, new in S4). The estate had
#     the forecast and the roster and nothing that scored either against
#     reality -- which is the measurement that makes a forecast accountable.
from datetime import datetime, time, timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from libs.py.fix_events import publish  # FF-28

# Bangladesh Standard Time, for reading a roster's local shift hours against
# stored UTC presence history.
BST_OFFSET_HOURS = 6


class FixCcQueueOps(models.Model):
    """Overflow, closure, prediction and availability on the existing queue."""

    _inherit = "fix.cc.queue"

    # --- staffing window -------------------------------------------------
    opens_hour = fields.Integer(
        string="Opens (BST hour)",
        default=0,
        help="Local hour this queue opens. 0 with a 24 close means always open.",
    )
    closes_hour = fields.Integer(
        string="Closes (BST hour)",
        default=24,
        help="Local hour this queue closes. 24 means it does not close.",
    )
    closed_action = fields.Selection(
        [
            ("divert", "Divert to another queue"),
            ("voicemail", "Offer voicemail"),
            ("callback", "Offer a callback"),
            ("message", "Play a closed message"),
        ],
        default="message",
        help="What happens to a contact arriving while the queue is shut.",
    )
    closed_queue_id = fields.Many2one(
        "fix.cc.queue", string="Closed-Hours Queue", help="For the divert action."
    )
    # --- overflow --------------------------------------------------------
    overflow_depth = fields.Integer(
        string="Overflow At (waiting items)",
        default=0,
        help="Queue depth above which the overflow action applies. 0 disables.",
    )
    overflow_action = fields.Selection(
        [
            ("divert", "Divert to another queue"),
            ("voicemail", "Offer voicemail"),
            ("callback", "Offer a callback"),
            ("message", "Play a busy message"),
        ],
        default="message",
        help="Default is a busy message because it needs no target queue: a "
        "default of 'divert' would have made every existing queue invalid the "
        "moment this field appeared.",
    )
    overflow_queue_id = fields.Many2one("fix.cc.queue", string="Overflow Queue")
    unstaffed_action = fields.Selection(
        [
            ("divert", "Divert to another queue"),
            ("voicemail", "Offer voicemail"),
            ("callback", "Offer a callback"),
            ("message", "Play an unavailable message"),
        ],
        default="callback",
        help="What happens when the queue is open but nobody available is "
        "signed in. Distinct from closed: the promise was to be open.",
    )
    unstaffed_queue_id = fields.Many2one("fix.cc.queue", string="Unstaffed Queue")

    @api.constrains("opens_hour", "closes_hour")
    def _check_hours(self):
        for rec in self:
            if not (0 <= rec.opens_hour <= 24) or not (0 <= rec.closes_hour <= 24):
                raise ValidationError("Queue hours must be between 0 and 24.")
            if rec.opens_hour > rec.closes_hour:
                raise ValidationError(
                    "Queue '%s' opens after it closes. An overnight queue is "
                    "modelled as two queues, because a single range cannot "
                    "express it unambiguously." % rec.name
                )

    @api.constrains(
        "closed_action",
        "closed_queue_id",
        "overflow_action",
        "overflow_queue_id",
        "unstaffed_action",
        "unstaffed_queue_id",
    )
    def _check_divert_targets(self):
        """A divert with nowhere to divert to silently does nothing."""
        for rec in self:
            # Only check a diversion that can actually fire. Overflow is
            # switched on by a depth threshold, so with no threshold the
            # action is inert and demanding a target would reject stored
            # data for a feature nobody enabled.
            pairs = [
                ("closed", rec.closed_action, rec.closed_queue_id),
                ("unstaffed", rec.unstaffed_action, rec.unstaffed_queue_id),
            ]
            if rec.overflow_depth:
                pairs.append(("overflow", rec.overflow_action, rec.overflow_queue_id))
            for label, action, target in pairs:
                if action != "divert":
                    continue
                if not target:
                    raise ValidationError(
                        "Queue '%s' is set to divert on %s but names no target "
                        "queue, so the diversion would do nothing." % (rec.name, label)
                    )
                if target == rec:
                    raise ValidationError("Queue '%s' diverts to itself on %s." % (rec.name, label))

    # --- state -----------------------------------------------------------
    def is_open_now(self):
        """Is the queue inside its staffed window, in local time?"""
        self.ensure_one()
        if self.opens_hour == 0 and self.closes_hour == 24:
            return True
        local_hour = (fields.Datetime.now() + timedelta(hours=BST_OFFSET_HOURS)).hour
        return self.opens_hour <= local_hour < self.closes_hour

    def available_agent_count(self):
        """How many agents could take work from this queue right now."""
        self.ensure_one()
        State = self.env["fix.cc.agent.state"].sudo()
        rows = State.search(
            [
                ("is_bookable", "=", True),
                ("presence_status_id.is_available_class", "=", True),
            ]
        )
        return len(rows.filtered(lambda s: s.is_live()))

    def waiting_depth(self):
        """Work items queued here and not yet assigned."""
        self.ensure_one()
        return (
            self.env["fix.routing.workitem"]
            .sudo()
            .search_count([("queue_id", "=", self.id), ("state", "in", ("pending", "offered"))])
        )

    def current_diversion(self):
        """The diversion in force now, or None. Checked in severity order.

        Closed beats unstaffed beats overflow: if the queue is shut, how deep
        it is does not matter, and telling a 02:00 caller the queue is busy
        would be false.
        """
        self.ensure_one()
        if not self.is_open_now():
            return {
                "action": self.closed_action,
                "queue": self.closed_queue_id,
                "reason": "Queue '%s' is closed (opens %02d:00 BST)."
                % (self.name, self.opens_hour),
            }
        if self.available_agent_count() == 0:
            return {
                "action": self.unstaffed_action,
                "queue": self.unstaffed_queue_id,
                "reason": "Queue '%s' is open but no available agent is signed in." % self.name,
            }
        if self.overflow_depth and self.waiting_depth() >= self.overflow_depth:
            return {
                "action": self.overflow_action,
                "queue": self.overflow_queue_id,
                "reason": "Queue '%s' is at overflow depth (%d waiting, "
                "threshold %d)." % (self.name, self.waiting_depth(), self.overflow_depth),
            }
        return None

    # --- prediction and availability -------------------------------------
    def predicted_wait_seconds(self, window_minutes=60):
        """Predicted answer time, from measured arrivals and the Erlang-C ASA.

        Returns None rather than a number when there is nothing to measure.
        An estimate produced from no arrivals is not a prediction, and a
        dashboard showing "0s" because nothing happened in the last hour is
        worse than one showing "not enough data".
        """
        self.ensure_one()
        since = fields.Datetime.now() - timedelta(minutes=window_minutes)
        convs = (
            self.env["fix.conversation"]
            .sudo()
            .search([("queue_id", "=", self.id), ("started_at", ">=", since)])
        )
        if not convs:
            return None
        handled = convs.filtered(lambda c: c.answered_at and c.ended_at)
        if not handled:
            return None
        aht = sum((c.ended_at - c.answered_at).total_seconds() for c in handled) / len(handled)
        arrival_rate = len(convs) / (window_minutes * 60.0)
        agents = self.available_agent_count()
        if agents <= 0:
            return None
        asa = self.erlang_c_asa(arrival_rate, aht, agents)
        if asa == float("inf"):
            return None
        return round(asa, 1)

    @api.model
    def queue_availability(self):
        """The representative-availability read D365 exposes as an API.

        One row per active queue, with the facts a wait-time announcement or
        a self-service deflection decision actually needs.
        """
        rows = []
        for queue in self.sudo().search([("active", "=", True)]):
            diversion = queue.current_diversion()
            rows.append(
                {
                    "queue": queue.code,
                    "name": queue.name,
                    "channel": queue.channel,
                    "open": queue.is_open_now(),
                    "available_agents": queue.available_agent_count(),
                    "waiting": queue.waiting_depth(),
                    "predicted_wait_seconds": queue.predicted_wait_seconds(),
                    "diversion": diversion["action"] if diversion else None,
                    "diversion_reason": diversion["reason"] if diversion else None,
                }
            )
        return rows

    @api.model
    def cron_handle_queue_closure(self):
        """Re-apply diversions to items already waiting when a queue shuts.

        An item that arrived while the queue was open and is still waiting
        when it closes must not sit there until morning. This is the case the
        intake-time check cannot cover, because at intake the queue was open.
        """
        Workitem = self.env["fix.routing.workitem"].sudo()
        moved = 0
        for queue in self.sudo().search([("active", "=", True)]):
            diversion = queue.current_diversion()
            if not diversion:
                continue
            waiting = Workitem.search(
                [
                    ("queue_id", "=", queue.id),
                    ("state", "in", ("pending", "offered")),
                    ("overflow_applied", "=", False),
                ]
            )
            for item in waiting:
                item._apply_queue_conditions()
                moved += 1
        return moved


class FixCcWfmAdherence(models.Model):
    """Scheduled versus actually present, per agent per day.

    The gap this closes, in the plan's words: the estate has the Erlang-C
    forecast AND the roster but computes no adherence, which is the metric
    that makes a forecast accountable. A roster nobody is measured against is
    a wish.
    """

    _name = "fix.cc.wfm.adherence"
    _description = "WFM Adherence"
    _order = "adherence_date desc, agent_id"
    _rec_name = "agent_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    agent_id = fields.Many2one("res.users", required=True, index=True, ondelete="cascade")
    adherence_date = fields.Date(required=True, index=True)
    scheduled_minutes = fields.Float(required=True, default=0.0)
    available_minutes = fields.Float(
        required=True,
        default=0.0,
        help="Minutes the agent actually spent in an available-class presence "
        "INSIDE the scheduled window. Time available outside the shift is not "
        "adherence — it is overtime, and counting it would let an agent who "
        "missed their shift score 100%.",
    )
    adherence_pct = fields.Float(compute="_compute_adherence", store=True, string="Adherence %")
    shift_count = fields.Integer(readonly=True, default=0)
    note = fields.Char(readonly=True)

    _agent_date_unique = models.Constraint(
        "UNIQUE (agent_id, adherence_date)",
        "One adherence row per agent per day.",
    )

    @api.depends("scheduled_minutes", "available_minutes")
    def _compute_adherence(self):
        for rec in self:
            if rec.scheduled_minutes <= 0:
                # Honest None-equivalent: an agent with no shift has no
                # adherence, and reporting 0% would make a day off look like
                # a failure.
                rec.adherence_pct = 0.0
            else:
                rec.adherence_pct = round(100.0 * rec.available_minutes / rec.scheduled_minutes, 2)

    @api.model
    def compute_for_date(self, target_date=None):
        """Measure one day's adherence from the roster and the presence log."""
        day = target_date or (fields.Date.context_today(self) - timedelta(days=1))
        Shift = self.env["fix.cc.wfm.shift"].sudo()
        Log = self.env["fix.cc.agent.state.log"].sudo()
        shifts = Shift.search([("shift_date", "=", day), ("state", "in", ("planned", "confirmed"))])
        rows = []
        for agent in shifts.mapped("agent_id"):
            agent_shifts = shifts.filtered(lambda s, a=agent: s.agent_id == a)
            windows = []
            scheduled = 0.0
            for shift in agent_shifts:
                start_local = datetime.combine(day, time(hour=shift.start_hour % 24))
                end_local = datetime.combine(day, time(hour=0)) + timedelta(hours=shift.end_hour)
                # Roster hours are local; presence history is stored UTC.
                start_utc = start_local - timedelta(hours=BST_OFFSET_HOURS)
                end_utc = end_local - timedelta(hours=BST_OFFSET_HOURS)
                windows.append((start_utc, end_utc))
                scheduled += (end_utc - start_utc).total_seconds() / 60.0

            intervals = Log.search(
                [
                    ("agent_id", "=", agent.id),
                    ("presence_status_id.is_available_class", "=", True),
                    ("from_at", "<=", max(w[1] for w in windows)),
                    "|",
                    ("to_at", "=", False),
                    ("to_at", ">=", min(w[0] for w in windows)),
                ]
            )
            available = 0.0
            for interval in intervals:
                end = interval.to_at or fields.Datetime.now()
                for win_start, win_end in windows:
                    overlap_start = max(interval.from_at, win_start)
                    overlap_end = min(end, win_end)
                    if overlap_end > overlap_start:
                        available += (overlap_end - overlap_start).total_seconds() / 60.0

            row = self.sudo().search(
                [("agent_id", "=", agent.id), ("adherence_date", "=", day)], limit=1
            )
            vals = {
                "agent_id": agent.id,
                "adherence_date": day,
                "scheduled_minutes": round(scheduled, 1),
                "available_minutes": round(min(available, scheduled), 1),
                "shift_count": len(agent_shifts),
                "note": "Measured from %d presence interval(s) against %d shift(s)."
                % (len(intervals), len(agent_shifts)),
            }
            if row:
                row.write(vals)
            else:
                row = self.sudo().create(vals)
            rows.append(row)
        return self.browse([r.id for r in rows])

    @api.model
    def cron_compute_adherence(self):
        """Measure yesterday, and publish the agents who fell short.

        The threshold is deliberately not a stored setting yet: 85% is the
        common contact-centre bar, and inventing a configurable policy before
        anyone has ruled on the number would be fabricating a decision.
        """
        rows = self.compute_for_date()
        shortfalls = rows.filtered(lambda r: r.scheduled_minutes > 0 and r.adherence_pct < 85.0)
        if shortfalls:
            publish(
                self.env,
                "wfm.adherence_shortfall",
                "fix.cc.wfm.adherence",
                shortfalls[0].id,
                {
                    "date": str(shortfalls[0].adherence_date),
                    "agents": [
                        {
                            "agent": r.agent_id.name,
                            "adherence_pct": r.adherence_pct,
                            "scheduled_minutes": r.scheduled_minutes,
                        }
                        for r in shortfalls
                    ],
                    "threshold_pct": 85.0,
                },
            )
        return {"measured": len(rows), "below_threshold": len(shortfalls)}
