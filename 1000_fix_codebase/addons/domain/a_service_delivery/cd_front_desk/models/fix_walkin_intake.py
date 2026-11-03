# fix.walkin.intake — the 3-minute walk-in intake flow (P04-M02-T02/T03).
# Gate criterion: walk-in intake in under 3 minutes, demonstrated by branch staff.
#
# A02 audit M04-8: an intake without a device died on a raw NotNullViolation at
# hand-off; the customer acknowledgement was ticked True with no proof; and a
# plain write of state="completed" closed an intake with no service order (10
# of 12 live completed intakes had none). The hand-off now refuses a missing
# device in plain words, needs the customer's signed receipt, and the state
# moves only through the actions.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class FixWalkinIntake(models.Model):
    """A walk-in intake record: device identification, fault capture, attachments.

    The 3-minute target (G1-02) is measured from intake_start to handover_complete.
    """

    _name = "fix.walkin.intake"
    _description = "Walk-in Intake"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    def _fix_guarded_fields(self) -> set:
        # A02 audit M04-8 (P04-10b, P04-11): the hand-off result and its
        # stamps are set only by action_complete_handover.
        return super()._fix_guarded_fields() | {
            "state",
            "handover_acknowledged",
            "handover_acknowledged_at",
            "handover_complete",
            "service_order_id",
            "intake_start",
        }

    # What the customer acknowledged: frozen once the hand-off completed.
    _FROZEN_WHEN_COMPLETED = frozenset(
        {
            "customer_id",
            "device_id",
            "handover_method",
            "customer_signature_attachment_id",
            "accessory_bag_barcode",
            "has_charger",
            "has_battery",
            "has_cable_stylus",
            "cosmetic_condition_matrix",
            "lci_status",
            "fault_description",
        }
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state == "completed" for rec in self):
            return locked | self._FROZEN_WHEN_COMPLETED
        return locked

    def write(self, vals):
        if not self.env.su:
            frozen = self._FROZEN_WHEN_COMPLETED & set(vals)
            for rec in self.filtered(lambda r: r.state == "completed"):
                changed = [n for n in frozen if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed:
                    raise UserError(
                        "Intake %s is handed over: what the customer acknowledged can no "
                        "longer be changed." % (rec.display_name or rec.id)
                    )
        return super().write(vals)

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
    # The proof behind a "signature" acknowledgement (A02 audit M04-8, M04-12:
    # the P03 form already posted this field; it never existed).
    customer_signature_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Customer Signed Intake Receipt",
        help="The customer's signed intake receipt. Required to complete the handover.",
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
                raise UserError(
                    "FLAW-04.3 Accessory Custody Gate: Retained accessories (charger/battery/cable) "
                    "require a Barcoded Accessory Bag ID before handover completion."
                )

    def _resolve_device(self):
        """BRU-FRD-12: the device is identified before the hand-off. A scanned
        serial / IMEI that matches a registered device is linked; otherwise
        the hand-off is refused in plain words (it crashed on a NotNull
        database error, A02 audit P04-10a)."""
        Device = self.env["fix.device"]
        for rec in self.filtered(lambda r: not r.device_id):
            code = (rec.device_serial_input or "").strip()
            device = Device.browse()
            if code:
                domain = [("serial_number", "=", code)]
                for name in ("imei_1", "imei_2"):
                    if name in Device._fields:
                        domain = ["|", *domain, (name, "=", code)]
                device = Device.search(domain, limit=1)
            if not device:
                raise UserError(
                    "Intake %s has no device. Identify the device (select it, or scan a "
                    "registered serial / IMEI) before the handover (BRU-FRD-12)."
                    % (rec.display_name or rec.id)
                )
            rec.device_id = device.id

    def _check_handover_proof(self):
        """BRU-FRD-05 (A02 audit M04-8): the acknowledgement is the customer's,
        so it needs their proof; it is never ticked on its own. A signed
        intake receipt is the proof accepted today. OTP needs the notification
        service's OTP channel, which M04 does not have yet (A02 P1); a staff
        witness is a colleague's word, not the customer's."""
        for rec in self:
            if rec.handover_method != "signature":
                raise UserError(
                    "Handover of intake %s needs the customer's acknowledgement: choose "
                    "'Digital Signature' and attach the signed intake receipt. OTP and "
                    "staff-witness acknowledgements are not accepted yet."
                    % (rec.display_name or rec.id)
                )
            attachment = rec.customer_signature_attachment_id.sudo()
            if not attachment or not (attachment.file_size or attachment.datas):
                raise UserError(
                    "Attach the customer's signed intake receipt to intake %s before "
                    "completing the handover." % (rec.display_name or rec.id)
                )

    def action_complete_handover(self):
        """Complete the handover with customer acknowledgement (T03)."""
        self._check_accessory_bag_gate()
        self._resolve_device()
        self._check_handover_proof()
        for rec in self:
            now = fields.Datetime.now()
            vals = {
                "handover_complete": now,
                "handover_acknowledged": True,
                "handover_acknowledged_at": now,
                "state": "completed",
            }
            # Create the service order from this intake
            if not rec.service_order_id:
                vals["service_order_id"] = rec._create_service_order().id
            rec._guarded().write(vals)
            self._emit("handover.completed", rec)

    def _create_service_order(self):
        """Create the service order from the intake data. The order is born in
        "intake": a legitimate system hand-off, so it goes through the order's
        own guard token when the order model carries one."""
        Order = self.env["fix.service.order"]
        if hasattr(Order, "_guarded"):
            Order = Order._guarded()
        order = Order.create(
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
