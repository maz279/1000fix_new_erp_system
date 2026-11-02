# fix.walkin.intake — the 3-minute walk-in intake flow (P04-M02-T02/T03).
# Gate criterion: walk-in intake in under 3 minutes, demonstrated by branch staff.
import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class FixWalkinIntake(models.Model):
    """A walk-in intake record: device identification, fault capture, attachments.

    The 3-minute target (G1-02) is measured from intake_start to handover_complete.
    """

    _name = "fix.walkin.intake"
    _description = "Walk-in Intake"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)

    token_id = fields.Many2one("fix.token.queue", string="Token", index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)

    # Customer (quick identification or creation via party kernel)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    customer_phone = fields.Char(related="customer_id.phone")

    # Device (quick identification or creation via device registry)
    device_id = fields.Many2one("fix.device", string="Device")
    device_serial_input = fields.Char(
        string="S/N or IMEI (Input)", help="Quick lookup by serial/IMEI"
    )

    # Fault capture
    fault_description = fields.Text(required=True)
    customer_statement = fields.Text(string="Customer Statement (verbatim)")

    # --- A02 Enterprise Data Capture & Barcoded Accessory Bag Custody (FLAW-04.3) ---
    brand_name = fields.Char(string="Device Brand Name")
    model_name = fields.Char(string="Device Model Name")
    symptom_category = fields.Selection(
        [
            ("power_boot", "No Power / Boot Loop"),
            ("display_touch", "Display / Touch Digitizer"),
            ("liquid_damage", "Liquid Ingress / Corrosion"),
            ("battery_charging", "Battery / Charging Port"),
            ("motherboard_logic", "Logic Board / Micro-Component"),
            ("audio_camera", "Audio / Camera / Sensors"),
            ("software_os", "OS / Firmware / BitLocker"),
            ("other", "Other Hardware Symptom"),
        ],
        string="Primary Symptom Category",
        default="power_boot",
    )
    reproducibility = fields.Selection(
        [
            ("always", "Verified at Counter (Always)"),
            ("intermittent", "Intermittent / Load Dependent"),
            ("unverified", "Customer Reported Only"),
        ],
        string="Symptom Reproducibility",
        default="always",
    )
    passcode_provided = fields.Boolean(
        string="Diagnostic Unlock Code Provided",
        default=False,
    )
    cosmetic_condition_matrix = fields.Text(
        string="4-Angle Cosmetic Condition Matrix",
        help="Structured condition notes for Screen, Bezel, Back Housing, Ports & Hinge.",
    )
    lci_status = fields.Selection(
        [
            ("intact", "Intact (White/Clear)"),
            ("tripped", "Tripped (Red/Pink — Liquid Exposure)"),
            ("not_visible", "External LCI Not Visible"),
        ],
        string="Liquid Contact Indicator (LCI) Status",
        default="intact",
        tracking=True,
    )
    intake_photo_count = fields.Integer(
        string="Captured Angle Photos Count",
        default=4,
    )
    intake_photo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="4-Angle Condition Photo Sheet",
    )
    accessory_bag_barcode = fields.Char(
        string="Barcoded Accessory Bag ID",
        tracking=True,
        help="FLAW-04.3: Mandatory barcoded pouch identifier when any accessory is retained.",
    )
    has_charger = fields.Boolean(string="Original Charger / Power Brick Retained", default=False)
    has_battery = fields.Boolean(string="Removable Battery Retained", default=False)
    has_cable_stylus = fields.Boolean(
        string="Cable / Stylus / Carrying Case Retained", default=False
    )
    sim_memory_removed = fields.Boolean(
        string="SIM & SD Card Removed & Returned to Customer",
        default=True,
    )
    storage_bin_code = fields.Char(
        string="Branch Safe-Custody Bin / Shelf Code",
        tracking=True,
    )
    loaner_device_id = fields.Many2one(
        "fix.device",
        string="Issued Courtesy Loaner Device",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )
    diagnostic_fee_bdt = fields.Monetary(
        string="Upfront Diagnostic Fee (BDT)",
        currency_field="currency_id",
        default=0.0,
    )
    payment_channel = fields.Selection(
        [
            ("cash", "Cash Drawer"),
            ("bkash", "bKash MFS"),
            ("nagad", "Nagad MFS"),
            ("card", "POS Card Terminal"),
            ("waived", "Waived (Warranty / AMC / VIP)"),
        ],
        string="Diagnostic Fee Payment Channel",
        default="waived",
    )
    payment_trx_ref = fields.Char(string="Payment Receipt / MFS TrxID")

    # Timing (the 3-minute gate)
    intake_start = fields.Datetime(default=fields.Datetime.now, readonly=True)
    handover_complete = fields.Datetime(readonly=True)
    intake_duration_seconds = fields.Integer(
        compute="_compute_duration", store=True, help="G1-02: target under 180 seconds"
    )

    # Handover with customer acknowledgement (T03)
    handover_acknowledged = fields.Boolean(default=False, readonly=True)
    handover_acknowledged_at = fields.Datetime(readonly=True)
    handover_method = fields.Selection(
        [
            ("signature", "Digital Signature"),
            ("otp", "OTP Confirmation"),
            ("witness", "Staff Witness"),
        ],
        string="Acknowledgement Method",
    )

    # The created service order
    service_order_id = fields.Many2one("fix.service.order", readonly=True)

    # Documents (through the M24-core attachment API)
    document_ids = fields.One2many(
        "fix.document", "res_id", domain=[("res_model", "=", "fix.walkin.intake")]
    )

    state = fields.Selection(
        [
            ("in_progress", "In Progress"),
            ("handover_pending", "Handover Pending"),
            ("completed", "Completed"),
        ],
        default="in_progress",
        required=True,
        tracking=True,
    )

    @api.depends("intake_start", "handover_complete")
    def _compute_duration(self):
        for rec in self:
            if rec.intake_start and rec.handover_complete:
                delta = rec.handover_complete - rec.intake_start
                rec.intake_duration_seconds = int(delta.total_seconds())
            else:
                rec.intake_duration_seconds = 0

    def _check_accessory_bag_gate(self):
        """FLAW-04.3: If any physical accessory is retained at the counter, a
        barcoded accessory bag ID must be recorded before handover completes."""
        for rec in self:
            if (
                rec.has_charger or rec.has_battery or rec.has_cable_stylus
            ) and not rec.accessory_bag_barcode:
                from odoo.exceptions import UserError

                raise UserError(
                    "FLAW-04.3 Accessory Custody Gate: Retained accessories (charger/battery/cable) "
                    "require a Barcoded Accessory Bag ID before handover completion."
                )

    def action_complete_handover(self):
        """Complete the handover with customer acknowledgement (T03)."""
        self._check_accessory_bag_gate()
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
        order = self.env["fix.service.order"].create(
            {
                "device_id": self.device_id.id,
                "customer_id": self.customer_id.id,
                "branch_id": self.branch_id.id,
                "service_type": "walk_in",
                "fault_description": self.fault_description,
                "state": "intake",
                "operating_unit_id": self.operating_unit_id.id,
                "accessory_bag_barcode": self.accessory_bag_barcode,
                "cosmetic_condition_notes": self.cosmetic_condition_matrix,
                "lci_tripped": self.lci_status == "tripped",
                "sim_memory_removed": self.sim_memory_removed,
                "loan_device_id": self.loaner_device_id.id if self.loaner_device_id else False,
            }
        )
        return order

    def _emit(self, event: str, rec):
        from libs.py.fix_events import publish

        publish(
            self.env,
            event,
            "fix.walkin.intake",
            rec.id,
            {
                "intake_id": rec.id,
                "branch": rec.branch_id.name,
                "duration_seconds": rec.intake_duration_seconds,
            },
        )
