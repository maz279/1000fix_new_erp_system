# fix.walkin.intake — the 3-minute walk-in intake flow (P04-M02-T02/T03).
# Gate criterion: walk-in intake in under 3 minutes, demonstrated by branch staff.
from odoo import api, fields, models

import logging

logger = logging.getLogger(__name__)


class FixWalkinIntake(models.Model):
    """A walk-in intake record: device identification, fault capture, attachments.

    The 3-minute target (G1-02) is measured from intake_start to handover_complete.
    """
    _name = "fix.walkin.intake"
    _description = "Walk-in Intake"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)

    token_id = fields.Many2one("fix.token.queue", string="Token", index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)

    # Customer (quick identification or creation via party kernel)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    customer_phone = fields.Char(related="customer_id.phone")

    # Device (quick identification or creation via device registry)
    device_id = fields.Many2one("fix.device", string="Device")
    device_serial_input = fields.Char(string="S/N or IMEI (Input)",
                                      help="Quick lookup by serial/IMEI")

    # Fault capture
    fault_description = fields.Text(required=True)
    customer_statement = fields.Text(string="Customer Statement (verbatim)")

    # Timing (the 3-minute gate)
    intake_start = fields.Datetime(default=fields.Datetime.now, readonly=True)
    handover_complete = fields.Datetime(readonly=True)
    intake_duration_seconds = fields.Integer(compute="_compute_duration", store=True,
                                              help="G1-02: target under 180 seconds")

    # Handover with customer acknowledgement (T03)
    handover_acknowledged = fields.Boolean(default=False, readonly=True)
    handover_acknowledged_at = fields.Datetime(readonly=True)
    handover_method = fields.Selection(
        [("signature", "Digital Signature"), ("otp", "OTP Confirmation"),
         ("witness", "Staff Witness")],
        string="Acknowledgement Method")

    # The created service order
    service_order_id = fields.Many2one("fix.service.order", readonly=True)

    # Documents (through the M24-core attachment API)
    document_ids = fields.One2many("fix.document", "res_id",
                                   domain=[("res_model", "=", "fix.walkin.intake")])

    state = fields.Selection(
        [("in_progress", "In Progress"), ("handover_pending", "Handover Pending"),
         ("completed", "Completed")],
        default="in_progress", required=True, tracking=True)

    @api.depends("intake_start", "handover_complete")
    def _compute_duration(self):
        for rec in self:
            if rec.intake_start and rec.handover_complete:
                delta = rec.handover_complete - rec.intake_start
                rec.intake_duration_seconds = int(delta.total_seconds())
            else:
                rec.intake_duration_seconds = 0

    def action_complete_handover(self):
        """Complete the handover with customer acknowledgement (T03)."""
        for rec in self:
            rec.handover_complete = fields.Datetime.now()
            rec.handover_acknowledged = True
            rec.handover_acknowledged_at = fields.Datetime.now()
            rec.state = "completed"
            # Create the service order from this intake
            if not rec.service_order_id:
                order = rec._create_service_order()
                rec.service_order_id = order.id
            self._emit("handover.completed", rec)

    def _create_service_order(self):
        """Create the service order from the intake data."""
        order = self.env["fix.service.order"].create({
            "device_id": self.device_id.id,
            "customer_id": self.customer_id.id,
            "branch_id": self.branch_id.id,
            "service_type": "walk_in",
            "fault_description": self.fault_description,
            "state": "intake",
            "operating_unit_id": self.operating_unit_id.id,
        })
        return order

    def _emit(self, event: str, rec):
        from libs.py.fix_events import publish
        publish(self.env, event, "fix.walkin.intake", rec.id, {
            "intake_id": rec.id, "branch": rec.branch_id.name,
            "duration_seconds": rec.intake_duration_seconds,
        })
