# fix.walkin.intake — the 3-minute walk-in intake flow (P04-M02-T02/T03).
# Gate criterion: walk-in intake in under 3 minutes, demonstrated by branch staff.
#
# A02 audit M04-8: an intake without a device died on a raw NotNullViolation at
# hand-off; the customer acknowledgement was ticked True with no proof; and a
# plain write of state="completed" closed an intake with no service order (10
# of 12 live completed intakes had none). The hand-off now refuses a missing
# device in plain words, needs the customer's signed receipt, and the state
# moves only through the actions.
#
# A02 audit M04-P2: the device was required only at the hand-off, so an intake
# with no device at all sat in the queue; the diagnostic fee never reached the
# drawer (52 of 52 live fees "waived", with no one deciding that). An intake is
# now created with a device or a scanned serial, a cash fee is posted to the
# branch's open shift at the hand-off, and a waived fee needs a Branch
# Manager's approval, routed through M63 like the other M04 approvals.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

from .fix_cash_shift import GROUP_MANAGER, fill_operating_unit
from .fix_service_order_drawer import fd_cash_requires_shift

logger = logging.getLogger(__name__)

# The diagnostic fee a waiver gives away when the intake shows none: a policy
# number. Today's value 0 means a waived intake with no fee needs no approval.
STANDARD_FEE_PARAM = "cd_front_desk.standard_diagnostic_fee_bdt"


class FixWalkinIntake(models.Model):
    """A walk-in intake record: device identification, fault capture, attachments.

    The 3-minute target (G1-02) is measured from intake_start to handover_complete.
    """

    _name = "fix.walkin.intake"
    _description = "Walk-in Intake"
    # fix.approvable.mixin brings fix.guarded.mixin with it (A02 audit M04-P2)
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "create_date desc"

    # A02 audit M04-P2: a fee waiver is approved from the manager's inbox
    _approval_domain = "diagnostic_fee_waiver"
    _approval_apply_method = "action_approve_fee_waiver"
    _approval_group = GROUP_MANAGER
    _approval_routed = True

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
            # A02 audit M04-P2: the waiver decision and the drawer posting
            "fee_waiver_approved_by_id",
            "fee_waiver_approved_amount",
            "fee_waiver_approved_at",
            "diagnostic_fee_shift_id",
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

    @api.model_create_multi
    def create(self, vals_list):
        """BRU-FRD-12 (A02 audit M04-P2): an intake starts with the device,
        either selected or as the scanned serial / IMEI. A scanned serial that
        matches a registered device is linked at once; one that does not is
        kept, and the hand-off still refuses until the device is registered."""
        # the branch decides the unit: the Walk-in Intake form never asks
        fill_operating_unit(self.env, vals_list)
        if not self.env.su:
            for vals in vals_list:
                serial = (vals.get("device_serial_input") or "").strip()
                if not vals.get("device_id") and not serial:
                    raise UserError(
                        "A walk-in intake needs the device: select it, or scan its serial "
                        "/ IMEI (BRU-FRD-12)."
                    )
                if not vals.get("device_id"):
                    device = self._fd_find_device(serial)
                    if device:
                        vals["device_id"] = device.id
        return super().create(vals_list)

    @api.model
    def _fd_find_device(self, code):
        # A merged duplicate's identifier resolves to the surviving device.
        return self.env["fix.device"].resolve_identifier(code)

    def write(self, vals):
        if not self.env.su and {"device_id", "device_serial_input"} & set(vals):
            for rec in self:
                device = vals.get("device_id", rec.device_id.id)
                serial = vals.get("device_serial_input", rec.device_serial_input)
                if not device and not (serial or "").strip():
                    raise UserError(
                        "Intake %s needs the device: it cannot be left with neither a "
                        "device nor a scanned serial (BRU-FRD-12)." % (rec.display_name or rec.id)
                    )
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
    # A02 audit M04-P2: the waiver decision, pinned to the amount waived, and
    # the drawer the cash fee went into.
    fee_waiver_approved_by_id = fields.Many2one(
        "res.users", string="Fee Waiver Approved By", readonly=True, copy=False, tracking=True
    )
    fee_waiver_approved_amount = fields.Monetary(
        string="Fee Waiver Approved (BDT)",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    fee_waiver_approved_at = fields.Datetime(
        string="Fee Waiver Approved At", readonly=True, copy=False
    )
    diagnostic_fee_shift_id = fields.Many2one(
        "fix.cash.shift",
        string="Fee Posted To Shift",
        readonly=True,
        copy=False,
        help="The branch cash shift the cash diagnostic fee was posted to.",
    )

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
            device = rec._fd_find_device(rec.device_serial_input) or Device.browse()
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

    # ------------------------------------------------------------ the fee

    def _fd_waived_amount(self) -> float:
        """What a waiver gives away: the fee entered, else the standard fee."""
        self.ensure_one()
        if self.payment_channel != "waived":
            return 0.0
        if self.diagnostic_fee_bdt and self.diagnostic_fee_bdt > 0:
            return self.diagnostic_fee_bdt
        raw = self.env["ir.config_parameter"].sudo().get_param(STANDARD_FEE_PARAM)
        try:
            return max(float(raw), 0.0) if raw not in (None, False, "") else 0.0
        except ValueError:
            return 0.0

    def _fd_waiver_covered(self) -> bool:
        self.ensure_one()
        waived = self._fd_waived_amount()
        if waived <= 0:
            return True
        return bool(self.fee_waiver_approved_by_id) and (
            self.fee_waiver_approved_amount + 0.005 >= waived
        )

    def _approval_amount(self) -> float:
        return self._fd_waived_amount() if len(self) == 1 else 0.0

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.state != "completed" and not self._fd_waiver_covered()

    def _fd_request_fee_waiver(self):
        """Route a waiver that no approval covers to a Branch Manager."""
        for rec in self:
            if rec._approval_needed() and rec.approval_state != "pending":
                rec.action_request_approval(
                    justification="Diagnostic fee of BDT %.2f waived at intake."
                    % rec._fd_waived_amount()
                )

    def action_approve_fee_waiver(self):
        """A Branch Manager who did not take the intake approves the waiver of
        its diagnostic fee, for exactly the amount waived. Runs only from the
        manager's M63 inbox (A02 audit M04-P2)."""
        self._approval_assert_routed()
        if not (self.env.su or self.env.user.has_group(GROUP_MANAGER)):
            raise UserError("Only a Branch Manager may approve a diagnostic fee waiver.")
        for rec in self:
            if rec.state == "completed":
                raise UserError("Intake %s is already handed over." % (rec.display_name or rec.id))
            waived = rec._fd_waived_amount()
            if waived <= 0:
                raise UserError("Intake %s waives no fee." % (rec.display_name or rec.id))
            if not self.env.su and self.env.user == rec.create_uid:
                raise UserError(
                    "You took intake %s, so you cannot approve its fee waiver."
                    % (rec.display_name or rec.id)
                )
            rec._guarded().write(
                {
                    "fee_waiver_approved_by_id": self.env.uid,
                    "fee_waiver_approved_amount": waived,
                    "fee_waiver_approved_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Diagnostic fee waiver of BDT %.2f approved by %s."
                % (waived, self.env.user.name)
            )
        return True

    def _fd_settle_diagnostic_fee(self):
        """At the hand-off: a waiver needs its approval, a cash fee goes into
        the branch's open drawer, an MFS or card fee needs its TrxID."""
        Shift = self.env["fix.cash.shift"]
        for rec in self:
            label = rec.display_name or rec.id
            if not rec._fd_waiver_covered():
                raise UserError(
                    "Intake %s waives a diagnostic fee of BDT %.2f: a Branch Manager must "
                    "approve the waiver first (Submit for Handover requests it)."
                    % (label, rec._fd_waived_amount())
                )
            fee = rec.diagnostic_fee_bdt or 0.0
            if fee <= 0 or rec.payment_channel == "waived":
                continue
            if rec.payment_channel != "cash":
                if not (rec.payment_trx_ref or "").strip():
                    raise UserError(
                        "Intake %s: enter the receipt / TrxID of the BDT %.2f diagnostic fee."
                        % (label, fee)
                    )
                continue
            if rec.diagnostic_fee_shift_id:
                continue  # already in a drawer
            shift = Shift._fd_open_shift_for(rec.branch_id, rec.company_id)
            if not shift:
                if fd_cash_requires_shift(self.env):
                    raise UserError(
                        "Branch %s has no open cash shift to take the diagnostic fee of "
                        "intake %s. Open the cash shift first."
                        % (rec.branch_id.display_name, label)
                    )
                rec.message_post(
                    body="Cash diagnostic fee of BDT %.2f taken with no open cash shift: it is "
                    "not in any drawer." % fee
                )
                continue
            shift._post_cash_movement(
                "cash_payments", fee, reference="Diagnostic fee, intake %s" % label
            )
            rec._guarded().write({"diagnostic_fee_shift_id": shift.id})

    def action_complete_handover(self):
        """Complete the handover with customer acknowledgement (T03)."""
        self._check_accessory_bag_gate()
        self._resolve_device()
        self._check_handover_proof()
        self._fd_settle_diagnostic_fee()
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
            # A02 audit B2: a literal publish() so FF-48 sees the event
            publish(
                self.env,
                "handover.completed",
                "fix.walkin.intake",
                rec.id,
                {
                    "intake_id": rec.id,
                    "branch": rec.branch_id.name,
                    "duration_seconds": rec.intake_duration_seconds,
                },
            )

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
