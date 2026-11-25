# fix.token.queue — the token queue (P04-M02-T01).
# Walk-in customers get a token; the queue drives the front-desk display.
#
# A02 audit M04-9: the token state and its stamps were writable (a waiting
# token was written "completed" with no call or serve), and the wait SLA was a
# stored compute on now() with no cron: frozen at the last write, 5 tokens
# breached and 0 escalated. The state now moves only through the actions, and
# a cron re-evaluates waiting tokens and escalates the breaches.
import logging

from odoo import api, fields, models

from libs.py.fix_events import publish  # FF-28

from .fix_cash_shift import dhaka_today, fill_operating_unit

logger = logging.getLogger(__name__)

# G1-02 wait-time target in seconds; a policy number (today's value: 180).
WAIT_SLA_PARAM = "cd_front_desk.wait_sla_seconds"
DEFAULT_WAIT_SLA = 180

# BRU-FRD-07: the queue lanes, most urgent highest. A token is called by lane
# first, then by the time it was issued (fix_workstation_ext call-next).
LANE_RANK = {"normal": 0, "warranty_express": 1, "senior_citizen": 2, "vip_corporate": 3}
# one advisory-lock class for the per-branch daily numbering
_TOKEN_LOCK_CLASS = 4042


class FixTokenQueue(models.Model):
    """A token in the branch service queue."""

    _name = "fix.token.queue"
    _description = "Token Queue"
    # A09 audit trail: the chatter + activity mixins of every sibling business
    # model, so queue state changes (tracking=True) are logged and followed up.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    # A02 ERP audit M04-F12: the queue reads in the order it is served: the
    # day, the priority lane, then first-come (it was branch + number, so the
    # priority rules placed a token in a lane nothing ever read).
    _order = "branch_id, queue_date desc, priority_rank desc, issued_at, id"

    # A02 ERP audit M04-F12: numbers restart every Dhaka business day per
    # branch and are unique within it (they ran on forever, unconstrained).
    _token_number_daily_unique = models.Constraint(
        "UNIQUE(branch_id, queue_date, token_number)",
        "A branch issues each token number once a day.",
    )

    def _fix_guarded_fields(self) -> set:
        # A02 audit M04-9 (P04-12): only the queue actions move a token.
        return super()._fix_guarded_fields() | {
            "state",
            "issued_at",
            "called_at",
            "served_at",
            "wait_sla_breached",
            "supervisor_escalated",
            "escalated_at",
            "service_order_id",
        }

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)

    branch_id = fields.Many2one("fix.branch", string="Branch", required=True, ondelete="cascade")
    token_number = fields.Integer(readonly=True)
    token_display = fields.Char(compute="_compute_display", store=True)

    customer_id = fields.Many2one("res.partner", string="Customer")
    service_type = fields.Selection(
        [
            ("drop_off", "Device Drop-off"),
            ("pick_up", "Device Pick-up"),
            ("enquiry", "Enquiry"),
            ("payment", "Payment"),
            ("other", "Other"),
        ],
        required=True,
        default="drop_off",
    )

    state = fields.Selection(
        [
            ("waiting", "Waiting"),
            ("called", "Called"),
            ("serving", "Serving"),
            ("completed", "Completed"),
            ("no_show", "No Show"),
            ("cancelled", "Cancelled"),
        ],
        default="waiting",
        required=True,
        tracking=True,
        index=True,
    )

    issued_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    queue_date = fields.Date(
        string="Queue Day",
        compute="_compute_queue_date",
        store=True,
        index=True,
        help="The Bangladesh business day (Asia/Dhaka) the token was issued on: token "
        "numbers restart each day.",
    )
    priority_rank = fields.Integer(
        string="Lane Rank",
        compute="_compute_priority_rank",
        store=True,
        index=True,
        help="BRU-FRD-07: the lane's place in the calling order (higher is called first).",
    )
    called_at = fields.Datetime(readonly=True)
    served_at = fields.Datetime(readonly=True)
    counter_number = fields.Integer(string="Counter #")

    # Link to the service order created from this token
    service_order_id = fields.Many2one("fix.service.order", string="Service Order", readonly=True)

    # --- A02 Enterprise Data Capture & G1-02 Wait-Time SLA (FLAW-04.1) ---
    priority_level = fields.Selection(
        [
            ("normal", "Standard Walk-in"),
            ("vip_corporate", "VIP / Corporate SLA"),
            ("warranty_express", "Express Warranty Lane"),
            ("senior_citizen", "Senior Citizen / Accessibility Priority"),
        ],
        string="Queue Priority Lane",
        default="normal",
        required=True,
        tracking=True,
    )
    customer_phone = fields.Char(
        related="customer_id.phone",
        string="Customer Mobile",
        readonly=True,
    )
    # Live, not stored: a stored compute on now() froze at the last write
    # (A02 audit M04-9). The breach flag below is what the cron stamps.
    wait_seconds = fields.Integer(
        string="Wait Time (Seconds)",
        compute="_compute_wait_seconds",
        help="Elapsed queue wait time in seconds from issued_at to called_at (or current time).",
    )
    wait_sla_breached = fields.Boolean(
        string="Wait SLA Breached (> 180s)",
        readonly=True,
        tracking=True,
        help="FLAW-04.1 / G1-02: set by the wait-SLA evaluation (cron and Call) when the "
        "walk-in customer waited longer than the target.",
    )
    supervisor_escalated = fields.Boolean(
        string="Escalated to Branch Supervisor",
        default=False,
        readonly=True,
        tracking=True,
    )
    escalated_at = fields.Datetime(string="Escalated At", readonly=True)
    notes = fields.Char(string="Counter Routing Notes")

    def _elapsed_wait(self, now=None) -> int:
        self.ensure_one()
        if not self.issued_at:
            return 0
        end_ts = self.called_at or self.served_at or now or fields.Datetime.now()
        return max(0, int((end_ts - self.issued_at).total_seconds()))

    @api.depends("issued_at", "called_at", "served_at", "state")
    def _compute_wait_seconds(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.wait_seconds = rec._elapsed_wait(now)

    def _wait_sla_seconds(self) -> int:
        raw = self.env["ir.config_parameter"].sudo().get_param(WAIT_SLA_PARAM)
        try:
            return int(raw) if raw not in (None, False, "") else DEFAULT_WAIT_SLA
        except ValueError:
            return DEFAULT_WAIT_SLA

    @api.depends("token_number", "branch_id")
    def _compute_display(self):
        for rec in self:
            prefix = rec.branch_id.code[:3].upper() if rec.branch_id else "TK"
            rec.token_display = f"{prefix}-{rec.token_number:03d}"

    @api.depends("issued_at")
    def _compute_queue_date(self):
        for rec in self:
            rec.queue_date = dhaka_today(rec, rec.issued_at) if rec.issued_at else False

    @api.depends("priority_level")
    def _compute_priority_rank(self):
        for rec in self:
            rec.priority_rank = LANE_RANK.get(rec.priority_level or "normal", 0)

    @api.model_create_multi
    def create(self, vals_list):
        # Auto-assign the next token number per branch and Dhaka business day
        # (A02 ERP audit M04-F12: it never reset). The counter is carried per
        # branch across the batch: searching the table for every vals gave two
        # tokens created in one call the SAME number; a transaction-scoped
        # advisory lock per branch serialises two counters issuing at once
        # (the UNIQUE constraint refuses whatever still collides).
        # the branch decides the unit: the Token Issue form never asks
        fill_operating_unit(self.env, vals_list)
        next_number = {}
        for vals in vals_list:
            if vals.get("token_number"):
                continue
            branch_id = vals.get("branch_id")
            stamp = vals.get("issued_at")
            day = dhaka_today(self, fields.Datetime.to_datetime(stamp) if stamp else None)
            key = (branch_id, day)
            if key not in next_number:
                if branch_id:
                    self.env.cr.execute(
                        "SELECT pg_advisory_xact_lock(%s, %s)", [_TOKEN_LOCK_CLASS, branch_id]
                    )
                self.flush_model(["token_number", "queue_date", "branch_id"])
                last = self.sudo().search(
                    [("branch_id", "=", branch_id), ("queue_date", "=", day)],
                    order="token_number desc",
                    limit=1,
                )
                next_number[key] = (last.token_number + 1) if last else 1
            vals["token_number"] = next_number[key]
            next_number[key] += 1
        records = super().create(vals_list)
        for rec in records:
            # A02 audit B2: a literal publish() so FF-48 sees the event
            publish(self.env, "token.issued", "fix.token.queue", rec.id, rec._token_payload())
        return records

    def action_call(self):
        for rec in self:
            rec._guarded().write({"state": "called", "called_at": fields.Datetime.now()})
        # the wait ends at the call: stamp a breach the cron has not seen yet
        self._evaluate_wait_sla()

    def action_serving(self):
        for rec in self:
            rec._guarded().write({"state": "serving", "served_at": fields.Datetime.now()})

    def action_complete(self):
        for rec in self:
            rec._guarded().write({"state": "completed"})

    def _evaluate_wait_sla(self):
        """FLAW-04.1 / A02 audit M04-9: stamp the breach flag from the real
        timestamps and escalate each breached token once, to the branch
        manager (chatter, an activity when the branch names a manager, and
        the token.sla_breached event)."""
        now = fields.Datetime.now()
        target = self._wait_sla_seconds()
        for rec in self:
            elapsed = rec._elapsed_wait(now)
            breached = elapsed > target
            vals = {}
            if breached != rec.wait_sla_breached:
                vals["wait_sla_breached"] = breached
            if breached and not rec.supervisor_escalated:
                vals.update(supervisor_escalated=True, escalated_at=now)
            if not vals:
                continue
            rec._guarded().write(vals)
            if vals.get("supervisor_escalated"):
                rec.message_post(
                    body=f"G1-02 Wait-Time SLA breached ({elapsed}s > {target}s). "
                    "Escalated to Branch Supervisor."
                )
                manager = rec.branch_id.manager_id
                if manager:
                    rec.sudo().activity_schedule(
                        "mail.mail_activity_data_todo",
                        summary="Queue wait SLA breached: %s" % rec.token_display,
                        user_id=manager.id,
                    )
                publish(
                    self.env,
                    "token.sla_breached",
                    "fix.token.queue",
                    rec.id,
                    rec._token_payload(),
                )

    def action_evaluate_wait_sla(self):
        """FLAW-04.1: Evaluate the selected tokens against the G1-02 wait SLA."""
        self._evaluate_wait_sla()
        return True

    @api.model
    def _cron_evaluate_wait_sla(self):
        """A02 audit M04-9: the scheduled job the SLA never had. Waiting and
        no-show tokens are re-evaluated; called ones were stamped at the call."""
        tokens = self.search(
            [("state", "in", ("waiting", "no_show")), ("supervisor_escalated", "=", False)]
        )
        tokens._evaluate_wait_sla()
        return len(tokens)

    def _token_payload(self) -> dict:
        self.ensure_one()
        return {
            "token": self.token_display,
            "branch": self.branch_id.name,
            "service_type": self.service_type,
        }
