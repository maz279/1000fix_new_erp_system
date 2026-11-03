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

logger = logging.getLogger(__name__)

# G1-02 wait-time target in seconds; a policy number (today's value: 180).
WAIT_SLA_PARAM = "cd_front_desk.wait_sla_seconds"
DEFAULT_WAIT_SLA = 180


class FixTokenQueue(models.Model):
    """A token in the branch service queue."""

    _name = "fix.token.queue"
    _description = "Token Queue"
    # A09 audit trail: the chatter + activity mixins of every sibling business
    # model, so queue state changes (tracking=True) are logged and followed up.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "branch_id, token_number"

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

    @api.model_create_multi
    def create(self, vals_list):
        # Auto-assign the next token number per branch. The counter is carried per
        # branch across the batch: searching the table for every vals gave two
        # tokens created in one call the SAME number.
        next_number = {}
        for vals in vals_list:
            if not vals.get("token_number"):
                branch_id = vals.get("branch_id")
                if branch_id not in next_number:
                    last = self.search(
                        [("branch_id", "=", branch_id)], order="token_number desc", limit=1
                    )
                    next_number[branch_id] = (last.token_number + 1) if last else 1
                vals["token_number"] = next_number[branch_id]
                next_number[branch_id] += 1
        records = super().create(vals_list)
        for rec in records:
            self._emit("token.issued", rec)
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
                self._emit("token.sla_breached", rec)

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

    def _emit(self, event: str, rec):
        from libs.py.fix_events import publish

        publish(
            self.env,
            event,
            "fix.token.queue",
            rec.id,
            {
                "token": rec.token_display,
                "branch": rec.branch_id.name,
                "service_type": rec.service_type,
            },
        )
