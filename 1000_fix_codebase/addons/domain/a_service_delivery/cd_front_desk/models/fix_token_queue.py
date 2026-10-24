# fix.token.queue — the token queue (P04-M02-T01).
# Walk-in customers get a token; the queue drives the front-desk display.
import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class FixTokenQueue(models.Model):
    """A token in the branch service queue."""

    _name = "fix.token.queue"
    _description = "Token Queue"
    # A09 audit trail: the chatter + activity mixins of every sibling business
    # model, so queue state changes (tracking=True) are logged and followed up.
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "branch_id, token_number"

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
            rec.state = "called"
            rec.called_at = fields.Datetime.now()

    def action_serving(self):
        self.state = "serving"
        self.served_at = fields.Datetime.now()

    def action_complete(self):
        self.state = "completed"

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
