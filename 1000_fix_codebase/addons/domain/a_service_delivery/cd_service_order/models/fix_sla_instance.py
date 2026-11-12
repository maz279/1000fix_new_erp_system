# S9 — the SLA KPI instance engine (A03 gap-plan Part IV, service S9).
#
# fix.sla.policy held response and resolution targets in business hours, and a
# comment said the clock engine would consume them. Nothing did: M27 computed
# service level by subtracting timestamps after the fact, and M34's complaint
# acknowledgement SLA was implied rather than measured. There were no instance
# objects anywhere, so there was nothing to pause, nothing to breach and
# nothing to show an agent mid-call.
#
# FOUR SEMANTICS re-researched against Microsoft Learn in November 2026. Each
# changes the data model, and the first pass had none of them:
#
#   1. Pause/resume and work hours are configurable at BOTH the SLA-KPI level
#      AND the SLA-item level, so different items can run against different
#      calendars by priority. Hence fix.sla.item, and hence the calendar
#      resolution order in _effective_calendar().
#
#   2. A RESUME DOES NOT RESTART A TIMER. It CANCELS the instance and creates
#      a new one. Instances are therefore an append-only SERIES per record,
#      not a mutable row — which is why this model has supersedes_id /
#      superseded_by_id and why resume() returns a different record than the
#      one it was called on. Getting this wrong would have produced a single
#      mutable row whose history could not be reconstructed.
#
#   3. The clock derives from a business-hours schedule PLUS business
#      closures. With no schedule assigned the default is all-day-every-day.
#      Whether hold time counts depends on whether the pause and the resume
#      fell inside working hours. fix.working.calendar already carries both
#      the weekly lines and the holiday ranges, so no new closure model was
#      needed -- using it is the non-duplicating choice.
#
#   4. Changing a schedule does NOT retroactively affect running instances
#      unless the record is paused/resumed or its SLA is updated. So the
#      calendar is STAMPED on the instance at creation and read from there.
#
# Each instance also records Elapsed Time (minutes paused), which Dataverse
# exposes on slakpiinstance and which nothing in the estate was tracking.
from datetime import datetime, time, timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

# A day has 1440 minutes; walking a business-hours calendar minute by minute
# over a long target would be slow, so the walk is per-day and per-line.
MAX_CALENDAR_DAYS = 400

# fix.working.calendar.line.weekday is a Selection of these keys, NOT the
# integers date.weekday() returns. Comparing against str(weekday()) matched
# nothing, so every calendar read as closed and every target computation
# raised -- the kind of defect that is invisible on re-reading the code and
# obvious the first time a test runs.
WEEKDAY_KEYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")

# A02 audit B3: pausing, resuming, succeeding or cancelling a customer's SLA
# clock by hand is a supervisor's decision (security/fix_service_order_groups.xml).
SLA_SUPERVISOR_GROUP = "cd_service_order.group_so_supervisor"


class FixSlaItem(models.Model):
    """One measurable promise inside a policy.

    D365's SLA Items. A policy says "urgent on-site repair"; its items say
    "acknowledge within 1 business hour" and "resolve within 8", each with
    its own calendar and its own pause rules if they differ.
    """

    _name = "fix.sla.item"
    _description = "SLA Item"
    _order = "policy_id, sequence, id"

    policy_id = fields.Many2one("fix.sla.policy", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(string="Order", required=True, default=10)
    name = fields.Char(string="Item", required=True)
    kpi_code = fields.Char(
        string="KPI Code",
        required=True,
        help="The KPI this item measures, e.g. 'first_response' or "
        "'resolution'. Instances are grouped and reported by this.",
    )
    target_hours = fields.Float(
        string="Target (business hours)",
        required=True,
        help="Target in BUSINESS hours against the item's calendar.",
    )
    calendar_id = fields.Many2one(
        "fix.working.calendar",
        string="Business Hours",
        help="Overrides the policy calendar for this item. Empty inherits. "
        "Empty everywhere means all-day-every-day, which is Microsoft's "
        "documented default and not an error.",
    )
    pausable = fields.Boolean(
        default=True,
        help="Whether this item's clock may be paused at all. An "
        "acknowledgement promise is usually not pausable; a resolution "
        "promise usually is.",
    )
    warn_at_pct = fields.Float(
        string="Warn At % Of Target",
        default=80.0,
        help="Raise a near-breach warning at this percentage of the target.",
    )
    active = fields.Boolean(default=True)

    _policy_kpi_unique = models.Constraint(
        "UNIQUE (policy_id, kpi_code)",
        "A policy measures each KPI once; use two policies for two targets.",
    )

    @api.constrains("target_hours", "warn_at_pct")
    def _check_targets(self):
        for rec in self:
            if rec.target_hours <= 0:
                raise ValidationError("An SLA item target must be positive.")
            if not (0 < rec.warn_at_pct <= 100):
                raise ValidationError("The warning threshold must be between 0 and 100 percent.")


class FixSlaPolicyItems(models.Model):
    """Attach items and a default calendar to the existing policy."""

    _inherit = "fix.sla.policy"

    item_ids = fields.One2many("fix.sla.item", "policy_id", string="SLA Items")
    calendar_id = fields.Many2one(
        "fix.working.calendar",
        string="Default Business Hours",
        help="The calendar items inherit. Empty means all-day-every-day.",
    )
    item_count = fields.Integer(compute="_compute_item_count")

    @api.depends("item_ids")
    def _compute_item_count(self):
        for rec in self:
            rec.item_count = len(rec.item_ids)


class FixSlaKpiInstance(models.Model):
    """One running (or finished) SLA clock against one record.

    Append-only as a SERIES: a pause/resume produces a new instance that
    supersedes the old one, exactly as Dataverse does it.
    """

    _name = "fix.sla.kpi.instance"
    _description = "SLA KPI Instance"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "started_at desc, id desc"
    _rec_name = "display_label"

    def _fix_guarded_fields(self) -> set:
        # A02 audit B3: any user marked an SLA Succeeded from P03 (or wrote
        # state='succeeded' through /p03/model/write). The clock and its
        # outcome move only through start_for / pause / resume / succeed /
        # cancel and the breach cron; superuser service code is trusted.
        return super()._fix_guarded_fields() | {
            "state",
            "res_model",
            "res_id",
            "policy_id",
            "item_id",
            "kpi_code",
            "calendar_id",
            "target_hours",
            "started_at",
            "target_at",
            "warn_at",
            "paused_at",
            "pause_reason",
            "elapsed_pause_minutes",
            "succeeded_at",
            "breached_at",
            "warned_at",
            "cancelled_reason",
            "supersedes_id",
            "superseded_by_id",
            "series_index",
        }

    def _fix_assert_clock_supervisor(self, verb: str) -> None:
        """Service code (the order's own transitions, the contact centre, the
        complaint lifecycle) calls these as superuser; a person needs the
        Service Supervisor role."""
        if self.env.su or self.env.user.has_group(SLA_SUPERVISOR_GROUP):
            return
        raise UserError(
            "Only a Service Supervisor can %s an SLA clock by hand; the clock otherwise "
            "follows the record's own workflow." % verb
        )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    res_model = fields.Char(required=True, index=True, string="Record Model")
    res_id = fields.Integer(required=True, index=True, string="Record ID")
    partner_id = fields.Many2one("res.partner", string="Customer", index=True)
    policy_id = fields.Many2one("fix.sla.policy", required=True, ondelete="restrict")
    item_id = fields.Many2one("fix.sla.item", ondelete="restrict")
    kpi_code = fields.Char(string="KPI", required=True, index=True)
    display_label = fields.Char(string="Instance", compute="_compute_display_label", store=True)

    calendar_id = fields.Many2one(
        "fix.working.calendar",
        string="Business Hours Used",
        help="STAMPED at creation. A later edit to the calendar does not "
        "retroactively move this instance's target, which is Microsoft's "
        "documented behaviour and the reason this is a stored field rather "
        "than a lookup.",
    )
    target_hours = fields.Float(string="Target (hours)", required=True)
    started_at = fields.Datetime(
        string="Started", required=True, default=fields.Datetime.now, index=True
    )
    target_at = fields.Datetime(
        string="Deadline", required=True, index=True, help="The deadline, in calendar time."
    )
    warn_at = fields.Datetime(index=True)

    state = fields.Selection(
        [
            ("in_progress", "In progress"),
            ("paused", "Paused"),
            ("succeeded", "Succeeded"),
            ("breached", "Breached"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="in_progress",
        index=True,
        tracking=True,
    )
    paused_at = fields.Datetime(readonly=True)
    pause_reason = fields.Char(readonly=True)
    elapsed_pause_minutes = fields.Float(
        string="Elapsed Time (min)",
        default=0.0,
        readonly=True,
        help="Total BUSINESS minutes this record spent on hold. Dataverse "
        "exposes this on slakpiinstance; nothing in the estate tracked it.",
    )
    succeeded_at = fields.Datetime(readonly=True)
    breached_at = fields.Datetime(readonly=True)
    warned_at = fields.Datetime(readonly=True)
    cancelled_reason = fields.Char(readonly=True)

    # The append-only series
    supersedes_id = fields.Many2one(
        "fix.sla.kpi.instance", string="Supersedes", readonly=True, index=True
    )
    superseded_by_id = fields.Many2one(
        "fix.sla.kpi.instance", string="Superseded By", readonly=True, index=True
    )
    series_index = fields.Integer(
        default=1,
        readonly=True,
        help="Position in the pause/resume chain for this record and KPI.",
    )

    @api.depends("res_model", "res_id", "kpi_code", "series_index")
    def _compute_display_label(self):
        for rec in self:
            rec.display_label = "%s#%s · %s (#%d)" % (
                rec.res_model or "?",
                rec.res_id or 0,
                rec.kpi_code or "?",
                rec.series_index or 1,
            )

    # ------------------------------------------------------------------
    # Business-hours arithmetic
    # ------------------------------------------------------------------
    @api.model
    def _calendar_windows_for_day(self, calendar, day):
        """[(start_dt, end_dt)] of working time on this date, or [] if closed.

        A holiday range on the calendar is a BUSINESS CLOSURE and removes the
        whole day. With no calendar at all the day is open end to end, which
        is Microsoft's documented default.
        """
        if not calendar:
            start = datetime.combine(day, time.min)
            return [(start, start + timedelta(days=1))]
        closed = calendar.holiday_ids.filtered(lambda h: h.date_from <= day <= h.date_to)
        if closed:
            return []
        weekday = WEEKDAY_KEYS[day.weekday()]
        windows = []
        for line in calendar.line_ids.filtered(lambda line: line.weekday == weekday):
            start = datetime.combine(day, time.min) + timedelta(hours=line.hour_from)
            end = datetime.combine(day, time.min) + timedelta(hours=line.hour_to)
            if end > start:
                windows.append((start, end))
        return sorted(windows)

    @api.model
    def add_business_hours(self, start, hours, calendar=None):
        """The datetime `hours` of WORKING time after `start`."""
        remaining = timedelta(hours=max(0.0, hours))
        if remaining <= timedelta(0):
            return start
        cursor = start
        for _ in range(MAX_CALENDAR_DAYS):
            windows = self._calendar_windows_for_day(calendar, cursor.date())
            for win_start, win_end in windows:
                if win_end <= cursor:
                    continue
                effective_start = max(cursor, win_start)
                available = win_end - effective_start
                if available >= remaining:
                    return effective_start + remaining
                remaining -= available
            cursor = datetime.combine(cursor.date() + timedelta(days=1), time.min)
        raise UserError(
            "The SLA target of %.2f business hours does not fall within %d days "
            "of calendar '%s'. Check the calendar's working hours — an empty "
            "calendar has no working time at all."
            % (hours, MAX_CALENDAR_DAYS, calendar.name if calendar else "none")
        )

    @api.model
    def business_minutes_between(self, start, end, calendar=None):
        """Working minutes between two datetimes.

        This is what decides whether hold time counts: a pause at 18:00 and a
        resume at 09:00 the next morning spans fifteen clock hours and, on a
        9-to-6 calendar, zero business minutes. Charging the customer's clock
        for the night would be wrong, and charging nothing for a pause taken
        at 10:00 and lifted at 15:00 would be equally wrong.
        """
        if not end or not start or end <= start:
            return 0.0
        total = 0.0
        cursor = start
        for _ in range(MAX_CALENDAR_DAYS):
            if cursor.date() > end.date():
                break
            for win_start, win_end in self._calendar_windows_for_day(calendar, cursor.date()):
                overlap_start = max(win_start, start)
                overlap_end = min(win_end, end)
                if overlap_end > overlap_start:
                    total += (overlap_end - overlap_start).total_seconds() / 60.0
            cursor = datetime.combine(cursor.date() + timedelta(days=1), time.min)
        return round(total, 2)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    @api.model
    def _effective_calendar(self, policy, item):
        """Item calendar, else policy calendar, else none (24/7)."""
        if item and item.calendar_id:
            return item.calendar_id
        return policy.calendar_id if policy else None

    @api.model
    def start_for(self, record, policy, kpi_code, item=None, partner=None, started_at=None):
        """Open an SLA clock on a record. Idempotent per (record, KPI).

        An instance already running for this record and KPI is returned
        unchanged rather than duplicated: two live clocks on one promise is
        not a state anyone can report on.
        """
        policy_rec = policy if hasattr(policy, "id") else self.env["fix.sla.policy"].browse(policy)
        if not policy_rec or not policy_rec.exists():
            raise ValidationError("An SLA instance needs a real policy.")
        item_rec = item
        if item_rec is None:
            item_rec = policy_rec.item_ids.filtered(lambda i: i.kpi_code == kpi_code and i.active)[
                :1
            ]
        if item_rec and not item_rec.active:
            raise ValidationError(
                "SLA item '%s' is inactive and cannot start a clock." % item_rec.name
            )
        existing = self.sudo().search(
            [
                ("res_model", "=", record._name),
                ("res_id", "=", record.id),
                ("kpi_code", "=", kpi_code),
                ("state", "in", ("in_progress", "paused")),
            ],
            limit=1,
        )
        if existing:
            return existing

        hours = (
            item_rec.target_hours
            if item_rec
            else (
                policy_rec.response_hours
                if kpi_code == "first_response"
                else policy_rec.resolution_hours
            )
        )
        calendar = self._effective_calendar(policy_rec, item_rec)
        start = started_at or fields.Datetime.now()
        target = self.add_business_hours(start, hours, calendar)
        warn_pct = item_rec.warn_at_pct if item_rec else 80.0
        warn = self.add_business_hours(start, hours * warn_pct / 100.0, calendar)
        instance = self.sudo().create(
            {
                "res_model": record._name,
                "res_id": record.id,
                "partner_id": getattr(partner, "id", partner)
                or (getattr(record, "customer_id", False) and record.customer_id.id)
                or False,
                "policy_id": policy_rec.id,
                "item_id": item_rec.id if item_rec else False,
                "kpi_code": kpi_code,
                "calendar_id": calendar.id if calendar else False,
                "target_hours": hours,
                "started_at": start,
                "target_at": target,
                "warn_at": warn,
            }
        )
        publish(
            self.env,
            "sla.instance_started",
            "fix.sla.kpi.instance",
            instance.id,
            {
                "res_model": record._name,
                "res_id": record.id,
                "kpi": kpi_code,
                "policy": policy_rec.code,
                "target_at": str(target),
                "target_hours": hours,
            },
        )
        return instance

    def pause(self, reason=""):
        """Hold the clock. Records when, so resume can price the hold."""
        self._fix_assert_clock_supervisor("pause")
        for rec in self:
            if rec.state != "in_progress":
                raise UserError(
                    "Only a running SLA clock can be paused (this one is %s)." % rec.state
                )
            if rec.item_id and not rec.item_id.pausable:
                raise UserError(
                    "SLA item '%s' is not pausable — an acknowledgement promise "
                    "that can be paused is not a promise." % rec.item_id.name
                )
            if not (reason or "").strip():
                raise UserError("Pausing an SLA clock requires a stated reason.")
            rec._guarded().write(
                {
                    "state": "paused",
                    "paused_at": fields.Datetime.now(),
                    "pause_reason": reason,
                }
            )
            publish(
                self.env,
                "sla.instance_paused",
                "fix.sla.kpi.instance",
                rec.id,
                {
                    "res_model": rec.res_model,
                    "res_id": rec.res_id,
                    "kpi": rec.kpi_code,
                    "reason": reason,
                },
            )
        return True

    def resume(self):
        """Resume by CANCELLING this instance and creating its successor.

        This is the semantic that surprised the re-audit and it is not a
        stylistic choice: Dataverse does not restart a paused timer, it ends
        the instance and starts a new one. Modelling it as a mutable row
        would lose the history of how many times a case was held and for how
        long, which is exactly what a disputed SLA claim turns on.

        The successor's target is recomputed from NOW plus the business time
        that was left when the pause began, so the hold costs the customer
        nothing and costs us nothing either.
        """
        self._fix_assert_clock_supervisor("resume")
        successors = self.browse()
        for rec in self:
            if rec.state != "paused":
                raise UserError(
                    "Only a paused SLA clock can be resumed (this one is %s)." % rec.state
                )
            calendar = rec.calendar_id or None
            held = self.business_minutes_between(rec.paused_at, fields.Datetime.now(), calendar)
            remaining_minutes = self.business_minutes_between(
                rec.paused_at, rec.target_at, calendar
            )
            now = fields.Datetime.now()
            new_target = self.add_business_hours(now, remaining_minutes / 60.0, calendar)
            warn_pct = rec.item_id.warn_at_pct if rec.item_id else 80.0
            new_warn = self.add_business_hours(
                now, (remaining_minutes / 60.0) * warn_pct / 100.0, calendar
            )
            successor = self.sudo().create(
                {
                    "res_model": rec.res_model,
                    "res_id": rec.res_id,
                    "partner_id": rec.partner_id.id,
                    "policy_id": rec.policy_id.id,
                    "item_id": rec.item_id.id,
                    "kpi_code": rec.kpi_code,
                    "calendar_id": rec.calendar_id.id,
                    "target_hours": rec.target_hours,
                    "started_at": now,
                    "target_at": new_target,
                    "warn_at": new_warn,
                    "elapsed_pause_minutes": rec.elapsed_pause_minutes + held,
                    "supersedes_id": rec.id,
                    "series_index": rec.series_index + 1,
                }
            )
            rec._guarded().write(
                {
                    "state": "cancelled",
                    "cancelled_reason": "Resumed after a %.1f business-minute "
                    "hold; superseded by instance %d." % (held, successor.id),
                    "superseded_by_id": successor.id,
                    "elapsed_pause_minutes": rec.elapsed_pause_minutes + held,
                }
            )
            publish(
                self.env,
                "sla.instance_resumed",
                "fix.sla.kpi.instance",
                successor.id,
                {
                    "res_model": rec.res_model,
                    "res_id": rec.res_id,
                    "kpi": rec.kpi_code,
                    "held_business_minutes": held,
                    "supersedes": rec.id,
                    "new_target_at": str(new_target),
                },
            )
            successors |= successor
        return successors

    def succeed(self, when=None):
        """The promise was met."""
        self._fix_assert_clock_supervisor("succeed")
        for rec in self:
            if rec.state not in ("in_progress", "paused"):
                continue
            rec._guarded().write(
                {"state": "succeeded", "succeeded_at": when or fields.Datetime.now()}
            )
            publish(
                self.env,
                "sla.instance_succeeded",
                "fix.sla.kpi.instance",
                rec.id,
                {
                    "res_model": rec.res_model,
                    "res_id": rec.res_id,
                    "kpi": rec.kpi_code,
                    "elapsed_pause_minutes": rec.elapsed_pause_minutes,
                },
            )
        return True

    def cancel(self, reason=""):
        self._fix_assert_clock_supervisor("cancel")
        for rec in self:
            if rec.state in ("succeeded", "breached", "cancelled"):
                continue
            rec._guarded().write(
                {
                    "state": "cancelled",
                    "cancelled_reason": reason or "cancelled by %s" % self.env.user.name,
                }
            )
        return True

    @api.model
    def for_record(self, record, kpi_code=None, live_only=True):
        """The instances attached to a record, newest first."""
        domain = [("res_model", "=", record._name), ("res_id", "=", record.id)]
        if kpi_code:
            domain.append(("kpi_code", "=", kpi_code))
        if live_only:
            domain.append(("state", "in", ("in_progress", "paused")))
        return self.sudo().search(domain)

    # ------------------------------------------------------------------
    # Crons
    # ------------------------------------------------------------------
    @api.model
    def cron_flag_breaches(self):
        """Breach and near-breach, published rather than merely coloured."""
        now = fields.Datetime.now()
        breached = self.sudo().search([("state", "=", "in_progress"), ("target_at", "<=", now)])
        for rec in breached:
            rec._guarded().write({"state": "breached", "breached_at": now})
            publish(
                self.env,
                "sla.instance_breached",
                "fix.sla.kpi.instance",
                rec.id,
                {
                    "res_model": rec.res_model,
                    "res_id": rec.res_id,
                    "kpi": rec.kpi_code,
                    "policy": rec.policy_id.code,
                    "target_at": str(rec.target_at),
                    "overdue_minutes": round((now - rec.target_at).total_seconds() / 60.0, 1),
                    "partner_id": rec.partner_id.id or None,
                },
            )
        warning = self.sudo().search(
            [
                ("state", "=", "in_progress"),
                ("warn_at", "!=", False),
                ("warn_at", "<=", now),
                ("warned_at", "=", False),
            ]
        )
        for rec in warning:
            rec._guarded().write({"warned_at": now})
            publish(
                self.env,
                "sla.instance_near_breach",
                "fix.sla.kpi.instance",
                rec.id,
                {
                    "res_model": rec.res_model,
                    "res_id": rec.res_id,
                    "kpi": rec.kpi_code,
                    "target_at": str(rec.target_at),
                    "partner_id": rec.partner_id.id or None,
                },
            )
        return {"breached": len(breached), "warned": len(warning)}

    @api.model
    def consume_sla_instance_breached(self, event: dict) -> dict:
        """R8 consumer of sla.instance_breached (A02 audit B3): a breached
        service-order clock was published and then nothing happened. Each
        Service Supervisor of the order's branch gets a to-do on the order,
        once per breached instance."""
        if not self.env.su:
            raise AccessError("SLA event consumers run only from the event relay.")
        payload = event.get("payload") or {}
        if payload.get("res_model") != "fix.service.order":
            return {"escalated": 0, "reason": "not a service-order clock"}
        order = self.env["fix.service.order"].sudo().browse(int(payload.get("res_id") or 0))
        order = order.exists()
        if not order or order.state in ("closed", "cancelled"):
            return {"escalated": 0, "reason": "no open service order"}
        group = self.env.ref(SLA_SUPERVISOR_GROUP, raise_if_not_found=False)
        users = order._fix_branch_users(group)
        summary = "SLA breached: %s (%s)" % (order.name, payload.get("kpi") or "resolution")
        if not users:
            order.message_post(
                body="%s. No Service Supervisor is appointed for this branch to escalate to."
                % summary
            )
            return {"escalated": 0, "reason": "no supervisor"}
        Activity = self.env["mail.activity"].sudo()
        escalated = 0
        for user in users:
            if Activity.search_count(
                [
                    ("res_model", "=", order._name),
                    ("res_id", "=", order.id),
                    ("user_id", "=", user.id),
                    ("summary", "=", summary),
                ]
            ):
                continue  # the relay redelivered: escalate once
            order.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=summary,
                note="Overdue by %s minutes against policy %s (target %s)."
                % (
                    payload.get("overdue_minutes"),
                    payload.get("policy") or "-",
                    payload.get("target_at") or "-",
                ),
                user_id=user.id,
            )
            escalated += 1
        return {"escalated": escalated}

    def write(self, vals):
        """A finished instance is evidence; its clock fields do not move."""
        frozen = {"started_at", "target_at", "target_hours", "calendar_id", "kpi_code"}
        touched = frozen & set(vals)
        if touched:
            for rec in self:
                if rec.state in ("succeeded", "breached", "cancelled"):
                    raise UserError(
                        "Cannot change %s on a finished SLA instance — the "
                        "series is the evidence of what was promised." % ", ".join(sorted(touched))
                    )
        return super().write(vals)
