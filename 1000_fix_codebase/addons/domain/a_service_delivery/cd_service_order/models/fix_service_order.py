# fix.service.order — the flagship model (P04-M03-T02, CD-M01-01).
# Full state machine per AS-06 (declared in ONE place, DP-01).
# SLA computation delegated to services/sla-engine/ (AR-007 section 3.1).
import logging
import uuid
from datetime import timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from . import fix_otp_util

logger = logging.getLogger(__name__)

# A02 workflow audit (A1): an order may be BORN only in these states. create()
# ran no transition check, so an order was created 'closed', or 'ready' with no
# QC, by the ORM and by /p03/model/write (M01-3).
_BIRTH_STATES = ("draft", "intake")
# The in-process token that lets create() pass a legitimate birth state through
# the field guard. An object, like the guard's own token: an RPC caller can put
# any key in the context but cannot put this object there.
_BIRTH_KEY = "fix_so_birth_state"
_BIRTH_TOKEN = object()

# The states before the customer's approval; an estimate's send/approve drives
# the order through them (A02 audit M01-2: two unlinked state machines).
_PRE_APPROVAL_STATES = ("diagnostic", "estimate_pending", "estimate_sent", "awaiting_approval")

# FLAW-01.1 / M01-1: the settlement sources the API accepts, and what each
# needs before the delivery gate opens (documented on _fix_record_settlement).
SETTLEMENT_SOURCES = [
    ("m20_receipt", "M20 Receipt"),
    ("field_collection", "Field Collection (M02)"),
    ("counter", "Branch Counter (Cashier)"),
    # A02 pass 2 (D1): cash on delivery - the rider / courier collects the
    # amount due at the doorstep. Recorded UNVERIFIED at proof of delivery;
    # the rider settlement or the courier remittance (an M20 receipt with its
    # reference) verifies it. It opens the delivery gate (the device and the
    # cash change hands together), never the close gate.
    ("cod", "Cash on Delivery (Rider / Courier)"),
]
_SETTLEMENT_SOURCE_KEYS = {key for key, _label in SETTLEMENT_SOURCES}

# M01-12: cancellation reason codes (spec §5 exceptions).
CANCEL_REASONS = [
    ("customer_declined", "Customer Declined the Repair"),
    ("estimate_declined", "Customer Rejected the Estimate"),
    ("duplicate", "Duplicate Order"),
    ("unrepairable", "Unrepairable"),
    ("customer_unreachable", "Customer Unreachable"),
    ("abandoned", "Device Abandoned (Uncollected)"),
    ("other", "Other (note required)"),
]
_CANCEL_REASON_KEYS = {key for key, _label in CANCEL_REASONS}

# Roles (security/fix_service_order_groups.xml).
GROUP_CASHIER = "cd_service_order.group_so_cashier"
GROUP_QC_INSPECTOR = "cd_service_order.group_so_qc_inspector"
GROUP_COMMERCIAL_APPROVER = "cd_service_order.group_so_commercial_approver"
# A02 audit B3: holds, SLA clock decisions and breach escalations.
GROUP_SUPERVISOR = "cd_service_order.group_so_supervisor"
# who may propose / confirm a beyond-economic-repair write-off (BRU-SRM-12)
BER_TECHNICAL_GROUPS = (
    "cd_workshop.group_fix_workshop_user",
    "cd_workshop.group_fix_workshop_qc_inspector",
    "cd_workshop.group_fix_workshop_manager",
    "cd_field_service.group_fix_field_service_user",
    "cd_field_service.group_fix_field_service_manager",
    "cd_service_order.group_so_qc_inspector",
    GROUP_SUPERVISOR,
)
# A02 audit B3: the clock every order gets when no policy matches its
# channel and priority (data/fix_sla_default_policy.xml).
DEFAULT_SLA_POLICY = "cd_service_order.sla_policy_m01_default"
# A02 audit M01-P2 (abandoned path): days after Ready before an uncollected
# device is flagged abandoned. "0" (the default) switches it off - how long a
# branch keeps a device is a business decision.
ABANDON_AFTER_DAYS_PARAM = "cd_service_order.abandon_after_days"
# A02 pass 2 (D13, M01-13): the uncollected-device schedule. Reminders on these
# days after Ready (the last one is the formal notice); disposal only after
# ABANDON_AFTER_DAYS_PARAM days (data: 90) with a manager's approval. The ONE
# source every screen reads (fix.service.order._fix_uncollected_policy()).
UNCOLLECTED_REMINDER_DAYS_PARAM = "cd_service_order.uncollected_reminder_days"
UNCOLLECTED_REMINDER_DAYS_DEFAULT = "3,7,15,30"
ABANDON_AFTER_DAYS_DEFAULT = "90"
# A02 pass 2 (M01-12, owner decision O6): the repair warranty every order
# carries, in days. The order's period is derived from it, never typed.
REPAIR_WARRANTY_DAYS_PARAM = "cd_service_order.repair_warranty_days"
REPAIR_WARRANTY_DAYS_DEFAULT = 90
# A02 pass 2 (M01-13): a device left uncollected is disposed of with a
# branch manager's approval (DOFA Tier 2).
GROUP_BRANCH_MANAGER = "cd_entity_config.group_dofa_tier_2"
# States where the resolution clock has already finished: no hold applies.
_SLA_FINISHED_STATES = ("ready", "delivered", "closed", "cancelled")

# Business switches (ir.config_parameter). Each defaults fail-closed where it is
# a control, or to today's behaviour where it is commercial policy.
#  - delivery evidence (verified OTP + recipient + signed report): a control,
#    default "1". "0" only where the SMS service cannot be wired.
DELIVERY_EVIDENCE_PARAM = "cd_service_order.delivery_evidence_required"
#  - warranty cover must be VERIFIED to give a zero-charge job: commercial
#    policy, default "0" (today: live unverified cover still counts).
WARRANTY_VERIFIED_PARAM = "cd_service_order.warranty_requires_verified"
#  - an AMC zero-charge job needs its contract on the order: a control, "1".
AMC_CONTRACT_PARAM = "cd_service_order.amc_requires_contract"
#  - A02 ERP audit M01-F14: liquid damage (a tripped LCI) or a customer-induced
#    fault (a coded fault in the 'physical' category, "Physical / Liquid
#    Damage") voids warranty zero-charge. Default "1" (exclude), as warranty
#    terms commonly do; the business confirms (OWNER).
WARRANTY_EXCLUDES_DAMAGE_PARAM = "cd_service_order.warranty_excludes_customer_damage"
_CUSTOMER_INDUCED_CATEGORIES = ("physical",)
#  - A02 ERP audit M01-F19 / BRU-SRM-10: the priority a loyalty tier marked
#    "Priority Diagnostics" (M10 fix.loyalty.tier.priority_diagnostic) gets at
#    intake. "off" (any value that is not a priority) switches it off. Which
#    level is "priority-1" is the CCO's call (OWNER); default 'urgent'.
LOYALTY_PRIORITY_PARAM = "cd_service_order.loyalty_priority"
# A02 ERP audit M01-F8: who may read a customer's unlock code (OWNER: confirm).
# Owner decision (20 Nov 2026): the repair technicians (workshop and field)
# read the passcode to test the device; it stays masked to everyone else and
# is purged at hand-over.
PASSCODE_READERS = (
    "cd_service_order.group_so_qc_inspector,cd_service_order.group_so_supervisor,"
    "cd_workshop.group_fix_workshop_user,cd_field_service.group_fix_field_service_user,"
    "base.group_system"
)
# A02 ERP audit M01-F20: the KPI code of the response clock (fix.sla.item
# kpi_code; the policy's response_hours when no item names it).
RESPONSE_KPI = "first_response"
# Priority order, lowest first (a loyalty tier never LOWERS a priority).
_PRIORITY_RANK = {"normal": 0, "high": 1, "urgent": 2, "emergency": 3}
# A02 ERP audit M01-F11: the order states in which parts are issued to it.
PARTS_ISSUE_STATES = ("approved", "in_repair", "qc_failed")
# A02 ERP audit M01-F11: the order states in which a technician's work order
# is live work (shown on the technician's queue): not delivered, closed or
# cancelled.
WORK_ORDER_LIVE_ORDER_STATES = (
    "draft",
    "intake",
    "diagnostic",
    "estimate_pending",
    "estimate_sent",
    "awaiting_approval",
    "approved",
    "in_repair",
    "qc_pending",
    "qc_failed",
)

# Fields frozen once the order is handed over or cancelled (A1): the record of
# what was repaired, for whom, and the handover evidence.
_FROZEN_WHEN_DONE = frozenset(
    {
        "device_id",
        "customer_id",
        "branch_id",
        "service_type",
        "technician_id",
        "fault_description",
        "service_warranty_days",
        "recipient_name",
        "recipient_nid_phone",
        "service_report_attachment_id",
        "intake_photo_attachment_id",
        "after_repair_photo_attachment_id",
    }
)
# Fields set at intake and changed afterwards only through their action
# (M01-1 re-classification to warranty; FR-SRM-080 priority override).
_SET_AT_INTAKE = frozenset({"order_category", "priority"})
# Evidence files uploaded for the order (bound to it, _fix_bind_evidence).
_ORDER_EVIDENCE_FIELDS = frozenset(
    {
        "service_report_attachment_id",
        "intake_photo_attachment_id",
        "after_repair_photo_attachment_id",
    }
)
# A02 pass 2 (M01-02/07/15): who the job is for, which device it is, its
# liquid-damage finding and its branch are fixed once the order leaves Draft.
# The customer's OTPs, the collector check and the estimate approvals are
# bound to them; each changes only through its supervisor correction action
# (Correct Customer / Device, Correct LCI Finding, Transfer Branch).
_FROZEN_AFTER_INTAKE = frozenset({"customer_id", "device_id", "lci_tripped", "branch_id"})
_FROZEN_AFTER_INTAKE_ACTION = {
    "customer_id": "Correct Customer / Device",
    "device_id": "Correct Customer / Device",
    "lci_tripped": "Correct LCI Finding",
    "branch_id": "Transfer Branch",
}


_DHAKA = pytz.timezone("Asia/Dhaka")


def _dhaka_date(stamp=None):
    """The Asia/Dhaka business date of a naive-UTC datetime (now if empty)."""
    stamp = stamp or fields.Datetime.now()
    return pytz.utc.localize(stamp).astimezone(_DHAKA).date()


def _param_on(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key, default)
    return str(raw).strip().lower() not in ("0", "false", "no", "off", "")


# AS-06: the ONE place the state machine is declared (DP-01)
SERVICE_ORDER_STATES = [
    ("draft", "Draft"),
    ("intake", "Intake — Walk-in/Collection"),
    ("diagnostic", "Diagnostic"),
    ("estimate_pending", "Estimate Pending"),
    ("estimate_sent", "Estimate Sent to Customer"),
    ("awaiting_approval", "Awaiting Customer Approval"),
    ("approved", "Approved — Queued for Repair"),
    ("in_repair", "In Repair"),
    ("qc_pending", "QC Pending"),
    ("qc_failed", "QC Failed — Rework"),
    ("ready", "Ready for Collection"),
    ("delivered", "Delivered"),
    ("closed", "Closed"),
    ("cancelled", "Cancelled"),
]

# State transition map (DP-01: the single authority)
VALID_TRANSITIONS = {
    "draft": {"intake"},
    "intake": {"diagnostic", "cancelled"},
    "diagnostic": {"estimate_pending", "cancelled"},
    "estimate_pending": {"estimate_sent", "cancelled"},
    "estimate_sent": {"awaiting_approval", "cancelled"},
    "awaiting_approval": {"approved", "cancelled"},
    "approved": {"in_repair", "cancelled"},
    "in_repair": {"qc_pending", "cancelled"},
    # A02 audit M01-P2: an order can be cancelled after repair too (the
    # customer declines to collect, or QC proves it unrepairable), with a
    # reason; a settled amount is then handed to M20 for refund.
    "qc_pending": {"ready", "qc_failed", "cancelled"},
    "qc_failed": {"in_repair", "cancelled"},
    "ready": {"delivered", "cancelled"},
    "delivered": {"closed"},
    "closed": set(),
    "cancelled": set(),
}


class FixServiceOrder(models.Model):
    """A service order — the primary transacting record of the business.

    Every device that enters a 1000FiX branch gets a service order. The
    full lifecycle from intake to delivery is tracked through this model.
    """

    _name = "fix.service.order"
    _description = "Service Order"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    # A02 workflow audit (A1, M01-1/3/10, M01-7): every one of these was
    # writable by any internal user, by the ORM and by /p03/model/write: a
    # clerk "settled" an order, ticked goodwill and named the approver, ticked
    # the delivery OTP and paused the SLA clock. Only the order's own actions
    # change them now.
    _GUARDED = frozenset(
        {
            "state",
            "payment_settlement_state",
            "amount_settled_bdt",
            "invoice_ref",
            "settlement_source",
            "settlement_recorded_by",
            "settlement_verified",
            "settlement_verified_by",
            "settlement_verified_at",
            "is_goodwill",
            "goodwill_approved_by",
            "goodwill_approved_at",
            "goodwill_reason",
            "goodwill_cost_attribution_bdt",
            "is_rework",
            "rework_of_id",
            "rework_approved_by",
            "rework_approved_at",
            "rework_reason",
            "warranty_cover_unverified",
            "delivery_otp_verified",
            "delivery_otp_verified_at",
            "delivery_otp_verified_by",
            "delivery_otp_sent_at",
            "delivery_otp_expires_at",
            "delivery_otp_attempts",
            "sla_clock_paused",
            "sla_paused_at",
            "sla_total_paused_minutes",
            "sla_response_deadline",
            "sla_resolution_deadline",
            "sla_response_at",
            "sla_resolution_at",
            "priority_override_reason",
            "priority_override_user_id",
            "service_warranty_until",
            "service_warranty_issued_by",
            "repair_completed_by",
            "intake_completed_at",
            "delivered_at",
            "closed_at",
            "cancel_reason_code",
            "cancel_note",
            "cancelled_by",
            # A02 audit B3: a hold pauses the SLA clock, so it is set only by
            # Defer / Resume (a supervisor), never by ticking a box.
            "is_deferred_block",
            "deferred_reason",
            # A02 audit M01-P2: the abandoned flag and the Ready stamp it
            # is measured from.
            "ready_at",
            "is_abandoned",
            "abandoned_at",
            "abandon_reason",
            # A02 ERP audit (2026-11-19): the QC round (M01-F4), the pinned
            # rework amount (M01-F2), the BER evidence (M01-F9) and the
            # customer's unlock code and its consent (M01-F8).
            "qc_round",
            "rework_approved_amount_bdt",
            "ber_proposed_by",
            "ber_proposed_at",
            "ber_reason",
            "ber_confirmed_by",
            "ber_confirmed_at",
            "passcode_value",
            "passcode_consent_at",
            "passcode_consent_by",
            "passcode_purged_at",
            # A02 pass 2: the repair warranty period comes from the policy
            # (M01-12); the uncollected-device reminders the cron sent
            # (M01-13); the part payments and what of them is verified (D3);
            # the on-site completion that stood as QC and delivery (D4).
            "service_warranty_days",
            "uncollected_reminder_stage",
            "uncollected_notice_at",
            "amount_verified_bdt",
            "onsite_completed_at",
            "onsite_field_order_ref",
        }
    )

    def _fix_guarded_fields(self) -> set:
        guarded = set(super()._fix_guarded_fields()) | self._GUARDED
        if self.env.context.get(_BIRTH_KEY) is _BIRTH_TOKEN:
            # create() already refused every state but draft/intake.
            guarded.discard("state")
        return guarded

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            # An existing order: category and priority change only through
            # their actions; a handed-over order is frozen.
            locked |= _SET_AT_INTAKE
            if any(o.state != "draft" for o in self):
                locked |= _FROZEN_AFTER_INTAKE
            if any(o.state in ("delivered", "closed", "cancelled") for o in self):
                locked |= _FROZEN_WHEN_DONE
        return locked

    # AS-03
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)

    # Identity
    name = fields.Char(
        string="Order Reference",
        readonly=True,
        index=True,
        copy=False,
        help="Assigned from the fix.service.order sequence in create(); a missing "
        "sequence is an error, never a shared placeholder reference.",
    )
    idempotency_key = fields.Char(
        string="Idempotency Key",
        index=True,
        copy=False,
        help="DI-04: a retried POST must not create two orders",
    )

    # The device (M17 registry)
    device_id = fields.Many2one(
        "fix.device",
        string="Device",
        required=True,
        ondelete="restrict",
        index=True,
        tracking=True,
    )
    device_serial = fields.Char(related="device_id.serial_number", store=True, string="S/N")

    # The customer (M33 party kernel)
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        ondelete="restrict",
        index=True,
        tracking=True,
    )
    customer_phone = fields.Char(related="customer_id.phone", string="Phone")

    # Branch and assignment
    branch_id = fields.Many2one(
        "fix.branch", string="Branch", required=True, ondelete="restrict", tracking=True
    )
    technician_id = fields.Many2one("hr.employee", string="Assigned Technician")

    # State machine (AS-06/DP-01: the declared transitions above are the authority)
    state = fields.Selection(
        SERVICE_ORDER_STATES,
        default="draft",
        required=True,
        tracking=True,
        index=True,
        group_expand="_read_group_states",
    )

    # Service details
    service_type = fields.Selection(
        [
            ("walk_in", "Walk-in Counter"),
            ("collection", "Collection/Delivery"),
            ("onsite", "On-site"),
            ("mail_in", "Mail-in"),
            ("corporate", "Corporate/Bulk"),
            # FR-SRM-001: the twelve spec channels — the digital/assisted
            # ones arrive via their owning modules (P01 portal, P04 app,
            # M27 WhatsApp, M32 AI, M12 marketplace, M40 partner, M05 MSP,
            # M08 preventive); the ORDER carries its true source channel.
            ("web_portal", "Web Portal (P01)"),
            ("mobile_app", "Customer Mobile App (P04)"),
            ("whatsapp", "WhatsApp (M27)"),
            ("ai_assistant", "AI Assistant (M32)"),
            ("hotline", "Hotline 16743"),
            ("email", "Email Intake"),
            ("b2b_bulk", "B2B Portal Bulk Upload"),
            ("marketplace", "Marketplace (M12)"),
            ("partner_referral", "Partner Referral (M40)"),
            ("msp_alert", "MSP Alert (M05)"),
            ("pm_schedule", "Contract Preventive Schedule (M08)"),
        ],
        required=True,
        default="walk_in",
        tracking=True,
    )
    # BRU-SRM-02/03: the commercial classification gating creation
    order_category = fields.Selection(
        [
            ("standard", "Standard (Paid)"),
            ("warranty", "Warranty"),
            ("amc", "AMC / Contract"),
            ("rework", "Rework"),
            ("rental", "Rental Asset Service"),
            ("refurbishment", "Refurbishment Intake"),
            ("recycling", "Recycling / E-Waste"),
            ("goodwill", "Goodwill (Zero-Charge)"),
        ],
        string="Order Category",
        default="standard",
        required=True,
        tracking=True,
        help="Commercial classification gating order workflow (BRU-SRM-02/03 & W2 business lines)",
    )
    warranty_cover_unverified = fields.Boolean(
        string="Cover Unverified",
        readonly=True,
        copy=False,
        tracking=True,
        help="Set when this warranty order was accepted on warranty cover "
        "whose purchase proof nobody has checked. The order still proceeds - "
        "withdrawing live cover is a commercial decision - but the exposure is "
        "recorded here so it can be filtered, costed and cleared instead of "
        "staying invisible (A04 audit 2026-11-01: 53 of 55 live warranties "
        "were active and unverified).",
    )
    is_rework = fields.Boolean(
        string="Rework",
        default=False,
        readonly=True,
        copy=False,
        tracking=True,
        help="BRU-SRM-06: auto-flagged when the same device returns with the same "
        "fault within 30 days; linked to the original order",
    )
    rework_of_id = fields.Many2one(
        "fix.service.order", string="Rework Of", copy=False, index=True, readonly=True
    )
    fault_description = fields.Text(string="Fault Description", required=True, tracking=True)
    catalog_item_id = fields.Many2one("fix.catalogue.item", string="Service Catalogue Item")

    # A04 ERP audit (20 Nov 2026) M37-F4: intake took any catalogue item - a
    # discontinued, archived or out-of-scope one included. The item's own
    # sale check now runs when the order names it; an order on a device a
    # live contract covers may still use a Discontinued item (BRU-CAT-10).
    @api.constrains("catalog_item_id")
    def _check_catalog_item_lifecycle(self):
        for order in self.filtered("catalog_item_id"):
            contract = order["contract_id"] if "contract_id" in order._fields else None
            channel = "service_contract" if contract else "service"
            order.catalog_item_id._fix_assert_sellable(channel)

    priority = fields.Selection(
        [("normal", "Normal"), ("high", "High"), ("urgent", "Urgent"), ("emergency", "Emergency")],
        default="normal",
        required=True,
        tracking=True,
    )

    # FR-SRM-080: Priority Override Logging
    priority_override_reason = fields.Text(
        string="Priority Override Justification", tracking=True, readonly=True, copy=False
    )
    priority_override_user_id = fields.Many2one(
        "res.users", string="Priority Overridden By", readonly=True, copy=False
    )

    # FR-SRM-081: Customer-Preferred Technician
    preferred_technician_id = fields.Many2one("hr.employee", string="Customer-Preferred Technician")

    # FR-SRM-082: Repeat-Visit Case Linkage
    parent_case_id = fields.Many2one(
        "fix.service.order", string="Parent Customer Problem Case", index=True
    )
    linked_order_ids = fields.One2many(
        "fix.service.order", "parent_case_id", string="Linked Visit Orders"
    )

    # Currency
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )

    # --- W2 Business-Line Extensions (FR-SRM-063..088) ---
    # FR-SRM-063: Rental Service Intake
    is_rental = fields.Boolean(string="Rental Intake", default=False, tracking=True)
    rental_agreement_ref = fields.Char(string="Rental Agreement Ref", tracking=True)
    rental_deposit_bdt = fields.Monetary(
        string="Rental Deposit (BDT)", currency_field="currency_id", default=0.0
    )
    rental_liability_bdt = fields.Monetary(
        string="Rental Liability (BDT)", currency_field="currency_id", default=0.0
    )
    rental_start_date = fields.Date(string="Rental Start Date")
    rental_end_date = fields.Date(string="Rental End Date")

    # FR-SRM-064: Rental Swap-Out
    is_swap_out = fields.Boolean(string="Swap-Out Triggered", default=False, tracking=True)
    swap_device_id = fields.Many2one("fix.device", string="Replacement Swap Device", tracking=True)
    swap_reason = fields.Selection(
        [
            ("unrepairable", "Irreparable Fault"),
            ("sla_breach_risk", "Expedited SLA Swap"),
            ("customer_request", "Customer Preference"),
        ],
        string="Swap Reason",
    )
    swap_condition_grade = fields.Selection(
        [
            ("grade_a", "Grade A (Like New)"),
            ("grade_b", "Grade B (Minor Blemishes)"),
            ("grade_c", "Grade C (Functional)"),
        ],
        string="Swap Condition Grade",
    )
    swap_logistics_status = fields.Selection(
        [
            ("pending", "Pending Dispatch"),
            ("dispatched", "In Transit"),
            ("completed", "Device Swapped & Signed"),
        ],
        string="Swap Logistics Status",
        default="pending",
    )

    # Deferred Repair Block
    is_deferred_block = fields.Boolean(
        string="Deferred Repair Hold", default=False, readonly=True, copy=False, tracking=True
    )
    deferred_reason = fields.Selection(
        readonly=True,
        copy=False,
        selection=[
            ("parts_backorder", "Parts Backorder (Supply Chain Hold)"),
            ("customer_travel", "Customer Unavailable / Travel"),
            ("disputed_liability", "Liability / Estimate Dispute"),
            ("third_party_vendor", "OEM Escalation Hold"),
        ],
        string="Deferred Reason",
    )
    deferred_until = fields.Date(string="Deferred Resumption Date", tracking=True)
    deferred_notes = fields.Text(string="Deferred Hold Justification")
    # A02 audit M01-P2: a device left uncollected after Ready
    # (ABANDON_AFTER_DAYS_PARAM). Flagged by the cron, never typed.
    ready_at = fields.Datetime(string="Ready Since", readonly=True, copy=False)
    is_abandoned = fields.Boolean(string="Abandoned (Uncollected)", readonly=True, copy=False)
    abandoned_at = fields.Datetime(readonly=True, copy=False)
    abandon_reason = fields.Char(string="Abandonment Reason", readonly=True, copy=False)

    # Repair warranty (M01 Quality & Release): the service guarantee 1000FiX
    # issues on completed repairs. Complements the device entitlement in
    # cd_device_registry — that warranty is the BRAND's contract; this one
    # is ours.
    # Owner decision (20 Nov 2026): 90 days on every repair, all categories.
    # A02 pass 2 (M01-12): derived from REPAIR_WARRANTY_DAYS_PARAM, never typed
    # (any clerk wrote 365 days, or 0 to issue none).
    service_warranty_days = fields.Integer(
        string="Repair Warranty (Days)",
        default=lambda self: self._fix_policy_warranty_days(),
        readonly=True,
        tracking=True,
        help="Service guarantee period issued on this repair (the company's repair warranty "
        "policy, cd_service_order.repair_warranty_days).",
    )
    service_warranty_until = fields.Date(
        string="Repair Warranty Valid Until", readonly=True, copy=False
    )
    service_warranty_issued_by = fields.Many2one(
        "res.users", string="Repair Warranty Issued By", readonly=True, copy=False
    )

    # A02 ERP audit M01-F4: each entry to QC Pending opens a new QC round; the
    # Ready gate reads the newest inspection of the current round, so one
    # failed inspection no longer blocks the order for ever.
    qc_round = fields.Integer(string="QC Round", readonly=True, copy=False, default=0)

    # A02 ERP audit M01-F9 / BRU-SRM-12: beyond economic repair needs photo
    # evidence and a second technician's confirmation.
    ber_photo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="BER Photo Evidence",
        copy=False,
        help="Photograph proving the device is beyond economic repair (BRU-SRM-12). "
        "Attach it before proposing the BER; it is frozen once proposed.",
    )
    ber_proposed_by = fields.Many2one(
        "res.users", string="BER Proposed By", readonly=True, copy=False
    )
    ber_proposed_at = fields.Datetime(string="BER Proposed At", readonly=True, copy=False)
    ber_reason = fields.Text(string="BER Reason", readonly=True, copy=False)
    ber_confirmed_by = fields.Many2one(
        "res.users", string="BER Confirmed By (Second Technician)", readonly=True, copy=False
    )
    ber_confirmed_at = fields.Datetime(string="BER Confirmed At", readonly=True, copy=False)

    # FR-SRM-065: Data Services Case Intake
    is_data_service = fields.Boolean(string="Data Recovery / Migration", default=False)
    data_confidentiality_level = fields.Selection(
        [
            ("standard", "Standard Commercial"),
            ("confidential", "Confidential"),
            ("strict_nda", "Strict NDA / Legal Hold"),
        ],
        default="standard",
        string="Confidentiality Level",
    )
    data_retention_days = fields.Integer(string="Data Retention Window (Days)", default=14)

    # FR-SRM-066: Refurbishment Work Order Intake
    is_refurbishment = fields.Boolean(string="Refurbishment Intake", default=False)
    refurb_source = fields.Selection(
        [
            ("trade_in", "Customer Trade-in"),
            ("unrepairable_scrap", "Unrepairable Conversion"),
            ("rental_retirement", "Rental Fleet Retirement"),
        ],
        string="Refurbishment Source",
    )
    target_grade = fields.Selection(
        [("grade_a", "Grade A"), ("grade_b", "Grade B"), ("grade_c", "Grade C")],
        string="Target Grade",
    )

    # FR-SRM-067: Recycling Intake
    is_recycling = fields.Boolean(string="E-Waste / Recycling Intake", default=False)
    disposition_triage = fields.Selection(
        [
            ("parts_harvest", "Component / Parts Harvesting"),
            ("metals_recovery", "Metals & PCB Recovery"),
            ("safe_destruction", "Certified Data & Device Destruction"),
        ],
        string="Disposition Triage",
    )
    e_waste_cert_ref = fields.Char(string="E-Waste Green Certificate Ref")

    # FR-SRM-075: Goodwill Repair
    is_goodwill = fields.Boolean(
        string="Goodwill Repair (Zero-Charge)",
        default=False,
        readonly=True,
        copy=False,
        tracking=True,
    )
    goodwill_cost_attribution_bdt = fields.Monetary(
        string="Goodwill Cost Absorbed (BDT)",
        currency_field="currency_id",
        default=0.0,
        readonly=True,
        copy=False,
    )
    goodwill_approved_by = fields.Many2one(
        "res.users",
        string="Goodwill Approved By",
        readonly=True,
        copy=False,
        help="Stamped by Approve Goodwill with the approving user (never typed).",
    )
    goodwill_approved_at = fields.Datetime(readonly=True, copy=False)
    goodwill_reason = fields.Text(string="Goodwill Reason", readonly=True, copy=False)
    # BRU-SRM-06: an auto-flagged rework is zero-charge only once a commercial
    # approver confirms it (A02 audit M01-1: 413 of 930 orders were flagged).
    rework_approved_by = fields.Many2one(
        "res.users", string="Zero-Charge Rework Confirmed By", readonly=True, copy=False
    )
    rework_approved_at = fields.Datetime(readonly=True, copy=False)
    rework_reason = fields.Text(string="Rework Confirmation Reason", readonly=True, copy=False)
    # A02 ERP audit M01-F2: the amount the zero-charge rework confirmation
    # covers, pinned when it is given; a higher amount due voids it.
    rework_approved_amount_bdt = fields.Monetary(
        string="Rework Waiver Covers (BDT)",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )

    # FR-SRM-076: Loan Device Management
    loan_device_id = fields.Many2one("fix.device", string="Temporary Loan Device")
    loan_issued_at = fields.Datetime(string="Loan Issued At")
    loan_returned_at = fields.Datetime(string="Loan Returned At")
    loan_condition = fields.Char(string="Loan Device Return Condition")

    # FR-SRM-077: Multi-Fault Handling Lines
    fault_line_ids = fields.One2many(
        "fix.service.order.fault", "order_id", string="Fault Diagnosis Lines"
    )

    # --- A02 Enterprise Data Capture Extensions (M01 D365 6-Tab Specification) ---
    promised_delivery_date = fields.Datetime(
        string="Promised Delivery Timestamp",
        tracking=True,
        help="Target completion & collection timestamp promised to customer at intake.",
    )
    passcode_type = fields.Selection(
        [
            ("none", "None / Unlocked"),
            ("pin", "Numeric PIN"),
            ("pattern", "Android Pattern Grid"),
            ("alphanumeric", "Alphanumeric Password"),
            ("biometric_disabled", "Biometric Disabled / Bypass"),
        ],
        string="Device Passcode Type",
        default="none",
        tracking=True,
    )
    # A02 ERP audit M01-F8 / BRU-SRM-20: the customer's unlock code was plain
    # text any user read and wrote, and it outlived the job. It is captured
    # only with the customer's explicit consent (Record Passcode), read only
    # by the roles that test the device, and purged at handover/cancel.
    passcode_value = fields.Char(
        string="Diagnostic Passcode / Pattern",
        copy=False,
        groups=PASSCODE_READERS,
        help="The customer's unlock code, captured with consent (Record Passcode) "
        "and purged when the device is handed over or the order is cancelled.",
    )
    passcode_on_file = fields.Boolean(
        string="Passcode On File",
        compute="_compute_passcode_on_file",
        compute_sudo=True,
        help="Shown instead of the code: whether one is held for this order.",
    )
    passcode_consent_at = fields.Datetime(
        string="Passcode Consent Given At", readonly=True, copy=False
    )
    passcode_consent_by = fields.Many2one(
        "res.users", string="Passcode Consent Recorded By", readonly=True, copy=False
    )
    passcode_purged_at = fields.Datetime(string="Passcode Purged At", readonly=True, copy=False)
    cosmetic_condition_notes = fields.Text(
        string="Cosmetic Condition Matrix",
        help="4-angle housing, screen, bezel, and port scratch/dent inspection log.",
    )
    lci_tripped = fields.Boolean(
        string="Liquid Contact Indicator (LCI) Tripped",
        default=False,
        tracking=True,
        # A02 pass 2 (M01-07): recorded at intake; afterwards only Correct LCI
        # Finding (a supervisor, with photo evidence) changes it - it decides
        # whether the warranty covers the job (M01-F14).
        help="True if internal or SIM-tray liquid contact indicator is red/tripped.",
    )
    accessory_bag_barcode = fields.Char(
        string="Barcoded Accessory Bag ID",
        tracking=True,
        help="Sealed barcoded pouch ID holding charger, adapter, stylus, or case.",
    )
    sim_memory_removed = fields.Boolean(
        string="SIM & Memory Card Returned to Customer",
        default=True,
        help="Mandatory PDPA & physical security check at intake.",
    )
    intake_photo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="4-Angle Intake Photo Evidence",
        tracking=True,
        help="Uploaded composite or primary photo evidence of pre-existing cosmetic state. "
        "A walk-in intake's photo is copied onto the order (BRU-SRM-17).",
    )
    # A02 pass 2 (M01-06, BRU-SRM-17): the device after the repair. A warranty
    # order does not close without both photos, uploaded on the order itself.
    after_repair_photo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="After-Repair Photo Evidence",
        copy=False,
        tracking=True,
        help="Photo of the device after the repair (BRU-SRM-17).",
    )
    # A02 pass 2 (M01-13, D13): the uncollected-device reminders sent (the
    # largest reminder day reached) and the formal notice.
    uncollected_reminder_stage = fields.Integer(
        string="Uncollected Reminder Sent (Day)", readonly=True, copy=False
    )
    uncollected_notice_at = fields.Datetime(
        string="Formal Uncollected Notice Issued", readonly=True, copy=False
    )
    # A02 pass 2 (D4): an on-site job completed in the field stands as QC and
    # delivery: the field order whose sign-off and post-work photo did.
    onsite_completed_at = fields.Datetime(string="Completed On Site At", readonly=True, copy=False)
    onsite_field_order_ref = fields.Char(
        string="On-Site Completion (Field Order)", readonly=True, copy=False
    )

    # Tab 3: Diagnosis, Faults & Triage Routing
    symptom_reproducibility = fields.Selection(
        [
            ("always", "Consistent / Always Reproducible"),
            ("intermittent", "Intermittent Fault"),
            ("thermal_load", "Under Thermal / Heavy Load Only"),
            ("unverified", "Customer Reported — Unverified at Counter"),
        ],
        string="Symptom Reproducibility",
        default="always",
    )
    triage_verdict = fields.Selection(
        [
            ("bench_l1", "Branch L1/L2 Quick Repair"),
            ("depot_l3", "Central L3/L4 Micro-Soldering Depot (M31)"),
            ("field_onsite", "On-Site Field Engineer Dispatch (M02)"),
            ("data_recovery", "Cleanroom Forensic Data Recovery (M06)"),
            ("warranty_swap", "Warranty Whole-Unit Swap"),
            ("nff", "No Fault Found (NFF)"),
        ],
        string="Technical Triage Routing Verdict",
        default="bench_l1",
        tracking=True,
    )
    diagnostic_engineer_id = fields.Many2one(
        "hr.employee", string="Diagnostic Engineer", tracking=True
    )
    diagnostic_notes = fields.Text(
        string="Engineering Root-Cause Findings",
        help="Detailed multimeter, DC power-rail, or board-level diagnostic notes.",
    )

    # SLA (T04: clocks and escalation — computation in services/sla-engine/)
    sla_policy_id = fields.Many2one("fix.sla.policy", string="SLA Policy")
    sla_response_deadline = fields.Datetime(readonly=True)
    sla_resolution_deadline = fields.Datetime(readonly=True)
    sla_response_at = fields.Datetime(readonly=True)
    sla_resolution_at = fields.Datetime(readonly=True)
    sla_clock_paused = fields.Boolean(
        default=False,
        readonly=True,
        tracking=True,
        help="Clock paused during customer approval hold or parts wait (FLAW-01.3).",
    )
    sla_paused_at = fields.Datetime(
        string="SLA Clock Paused At",
        readonly=True,
        copy=False,
    )
    sla_total_paused_minutes = fields.Float(
        string="Cumulative SLA Hold (Minutes)",
        default=0.0,
        readonly=True,
        copy=False,
        help="Total elapsed customer-wait/hold minutes excluded from net SLA resolution time.",
    )

    # Tab 6: Settlement, Handover & Repair Warranty (FLAW-01.1)
    payment_settlement_state = fields.Selection(
        [
            ("unpaid", "Unpaid / Settlement Pending"),
            ("settled", "Invoice Paid & Settled"),
            ("covered_zero_charge", "Zero-Charge Covered (Warranty / AMC / Goodwill)"),
            ("credit_approved", "Corporate B2B Credit Approved"),
            # M01-12: a settled order that is cancelled owes the customer
            # money; the refund/credit hand-off event carries it to M20.
            ("refund_due", "Refund / Credit Due"),
            # A02 pass 2 (D3): part of the amount due received (an on-site
            # part payment); the rest stays due.
            ("partial", "Part Paid (balance due)"),
        ],
        string="Financial Settlement Status",
        default="unpaid",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        help="FLAW-01.1: Hard gate before transitioning to Delivered.",
    )
    invoice_ref = fields.Char(
        string="M19 Invoice / Receipt Reference",
        readonly=True,
        copy=False,
        tracking=True,
        help="POS Receipt, MFS TrxID, or M19 Tax Invoice reference.",
    )
    amount_settled_bdt = fields.Monetary(
        string="Amount Settled (BDT)",
        currency_field="currency_id",
        default=0.0,
        readonly=True,
        copy=False,
        tracking=True,
    )
    # FLAW-01.1 / M01-15: where the settlement came from and whether anyone
    # has checked it. A typed TrxID is a claim, not money: the delivery gate
    # opens only on a VERIFIED settlement (see _fix_record_settlement).
    settlement_source = fields.Selection(
        SETTLEMENT_SOURCES, string="Settlement Source", readonly=True, copy=False
    )
    settlement_recorded_by = fields.Many2one(
        "res.users", string="Settlement Recorded By", readonly=True, copy=False
    )
    settlement_verified = fields.Boolean(
        string="Settlement Verified", readonly=True, copy=False, tracking=True
    )
    settlement_verified_by = fields.Many2one(
        "res.users", string="Settlement Verified By", readonly=True, copy=False
    )
    settlement_verified_at = fields.Datetime(readonly=True, copy=False)
    # A02 pass 2 (D3): of amount_settled_bdt, what a cashier (or an M20
    # receipt) has verified. A part payment taken on top of a verified one is
    # unverified until it is checked; voiding it keeps the verified part.
    amount_verified_bdt = fields.Monetary(
        string="Amount Verified (BDT)",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    # A5 / M01-10: set only by Verify Delivery OTP, when the code the
    # notification service sent to the customer's phone is read back.
    delivery_otp_verified = fields.Boolean(
        string="Handover OTP / Signature Verified",
        default=False,
        readonly=True,
        copy=False,
        tracking=True,
    )
    delivery_otp_verified_at = fields.Datetime(readonly=True, copy=False)
    delivery_otp_verified_by = fields.Many2one(
        "res.users", string="Handover OTP Checked By", readonly=True, copy=False
    )
    delivery_otp_sent_at = fields.Datetime(readonly=True, copy=False)
    delivery_otp_expires_at = fields.Datetime(readonly=True, copy=False)
    delivery_otp_attempts = fields.Integer(readonly=True, copy=False)
    # Keyed digest only, never the code; not readable by internal users.
    delivery_otp_digest = fields.Char(readonly=True, copy=False, groups="base.group_system")
    intake_completed_at = fields.Datetime(string="Intake Completed At", readonly=True, copy=False)
    delivered_at = fields.Datetime(string="Delivered At", readonly=True, copy=False)
    closed_at = fields.Datetime(string="Closed At", readonly=True, copy=False)
    # BRU-SRM-18 / SOD-07: who completed the repair, so the QC inspector can
    # be checked against them.
    repair_completed_by = fields.Many2one(
        "res.users", string="Repair Completed By", readonly=True, copy=False
    )
    # M01-12: a cancellation carries its reason.
    cancel_reason_code = fields.Selection(
        CANCEL_REASONS, string="Cancellation Reason", readonly=True, copy=False
    )
    cancel_note = fields.Text(string="Cancellation Note", readonly=True, copy=False)
    cancelled_by = fields.Many2one("res.users", readonly=True, copy=False)
    recipient_name = fields.Char(string="Collecting Recipient Name")
    recipient_nid_phone = fields.Char(string="Recipient Phone / NID Reference")
    service_report_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Signed Service Delivery Report (PDF)",
        help="Signed customer collection slip and QC certificate.",
    )

    # Related records
    estimate_ids = fields.One2many("fix.estimate", "order_id", string="Estimates")
    work_order_ids = fields.One2many("fix.work.order", "order_id", string="Work Orders")
    qc_checklist_ids = fields.One2many("fix.qc.checklist", "order_id", string="QC Checklists")

    # MIG-03: legacy reference (permanent)
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        help="MIG-03: the legacy system's order number, permanently retained",
    )

    active = fields.Boolean(default=True)

    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _idempotency_key_unique = models.Constraint(
        "UNIQUE (idempotency_key)",
        "An order with this idempotency key already exists (DI-04 idempotency).",
    )
    _name_unique = models.Constraint(
        "UNIQUE (name)",
        "Service order references must be unique.",
    )

    @api.model
    def _read_group_states(self, states, domain, order):
        return [state[0] for state in SERVICE_ORDER_STATES]

    @api.depends("passcode_value")
    def _compute_passcode_on_file(self):
        for order in self:
            order.passcode_on_file = bool(order.sudo().passcode_value)

    # --- State machine enforcement (AS-06/DP-01) ---
    def _validate_transition(self, new_state: str) -> None:
        self.ensure_one()
        old = self.state
        if new_state == old:
            return
        valid_targets = VALID_TRANSITIONS.get(old, set())
        if new_state not in valid_targets:
            raise ValidationError(
                f"Invalid state transition: {old} -> {new_state}. "
                f"Valid transitions from '{old}': {', '.join(sorted(valid_targets)) or '(terminal state)'}"
            )
        if new_state == "approved":
            # A02 audit M01-2: 'approved' needs an approved estimate or a
            # zero-charge entitlement - the order approved with no estimate,
            # or with a REJECTED one.
            self._check_commercial_clearance()
        if new_state == "ready":
            # BRU-SRM-04 (H): the QC hard gate lives in the transition check
            # so NO write path (action, controller, sync, RPC) reaches Ready
            # without a passed checklist.
            self._check_qc_gate()
        if new_state == "delivered":
            # FLAW-01.1: Financial settlement & zero-charge gate before handover
            self._check_delivery_settlement_gate()
            # A5 / M01-10: handover evidence (verified OTP, recipient, report)
            self._check_delivery_evidence()
        if new_state == "closed":
            # M01-11: close only once the money is settled (or credit
            # approved), or the job is a zero-charge entitlement.
            self._check_close_gate()

    def _fix_release_checklist(self):
        """The inspection that decides Ready: the newest checklist of the
        current QC round (A02 ERP audit M01-F4).

        Every checklist used to have to pass, and a completed one is frozen
        evidence (no unlink), so ONE failed inspection blocked the order for
        ever, through every rework. Each entry to QC Pending opens a round
        (qc_round); a checklist belongs to the round it was completed in, and
        one completed in an earlier round no longer decides.
        An inspection started after the newest one (pending / in progress) is
        the newest one, so Ready waits for it."""
        self.ensure_one()
        # an inspection completed in an EARLIER round is history. One never
        # stamped (round 0) counts by recency only on a legacy order that has
        # never entered a QC round (A02 pass 2, M01-09: a checklist completed
        # before round 1 opened Ready); a pending one always counts.
        checklists = self.qc_checklist_ids.filtered(
            lambda c: not (c.qc_round and c.qc_round < self.qc_round)
            and not (not c.qc_round and self.qc_round and c.state in ("passed", "failed"))
        )
        return checklists.sorted(lambda c: c.id)[-1:] if checklists else checklists

    def _fix_qc_gate_passes(self) -> bool:
        self.ensure_one()
        newest = self._fix_release_checklist()
        return bool(newest) and newest.state == "passed" and (bool(newest.item_ids) or self.env.su)

    def _check_qc_gate(self) -> None:
        """BRU-SRM-04 (H): an order cannot reach Ready without a PASSED
        quality checklist — a hard gate, not a warning."""
        self.ensure_one()
        newest = self._fix_release_checklist()
        if not newest:
            raise UserError(
                "Order %s has no QC checklist for this QC round — Ready requires one "
                "(BRU-SRM-04)" % self.name
            )
        if newest.state != "passed":
            raise UserError(
                "Order %s cannot be Ready: its latest QC checklist is %s, not passed "
                "(BRU-SRM-04)" % (self.name, newest.state)
            )
        # A02 audit M01-6: 5 of 8 live passed checklists had no items - a
        # checklist with nothing checked is not an inspection. (Only trusted
        # superuser code can still write such a row: the state is guarded.)
        if not self.env.su and not newest.item_ids:
            raise UserError(
                "Order %s cannot be Ready: its passed QC checklist has no inspection "
                "items (BRU-SRM-04)" % self.name
            )

    # --- commercial basis: what is due, and what makes a job zero-charge ---
    def _fix_governing_estimate(self):
        """The estimate the money is decided on: the latest approved version,
        else the latest one with the customer (sent). Earlier versions are
        superseded by a revision; summing them double-counted."""
        self.ensure_one()
        for states in (("approved",), ("sent",)):
            ests = self.estimate_ids.filtered(lambda e, s=states: e.state in s)
            if ests:
                return ests.sorted(lambda e: (e.version, e.id))[-1]
        return self.env["fix.estimate"]

    def _fix_extra_charges(self) -> list:
        """Customer charges of this order outside its estimate, each a dict
        {code, line_type, description, net}: ``code`` the catalogue charge
        code, ``net`` the price before VAT. M02 adds unwaived wasted-visit
        fees (D21), M03 the pick-and-drop tariff charges (D22). The billing
        engine adds their VAT to the amount due and bills them on the
        repair's tax invoice."""
        self.ensure_one()
        return []

    def _fix_amount_due(self) -> float:
        self.ensure_one()
        est = self._fix_governing_estimate()
        return max(est.grand_total, 0.0) if est else 0.0

    def _fix_zero_charge_basis(self) -> str:
        """Why this job is not charged to the customer, or '' if it is.

        A02 audit M01-1: the settlement gate skipped any order whose CATEGORY
        said warranty/amc/goodwill/rework, and whose is_goodwill / is_rework
        flag any clerk could set. A zero-charge basis is now an entitlement the
        system can check, or an approval stamped by a commercial approver."""
        self.ensure_one()
        category = self.order_category
        if category == "warranty" and not self._fix_warranty_exclusion():
            day = (self.create_date or fields.Datetime.now()).date()
            require = _param_on(self.env, WARRANTY_VERIFIED_PARAM, "0")
            if self.device_id.is_under_warranty(day, require_verified=require):
                return "warranty cover"
        if category == "amc":
            if not _param_on(self.env, AMC_CONTRACT_PARAM, "1"):
                return "AMC contract"
            if "contract_id" in self._fields and self.contract_id:
                return "AMC contract %s" % self.contract_id.display_name
        # A recycling / refurbishment category is NOT a basis: any clerk sets
        # it (create, Change Category) and it waived the estimate and the
        # settlement gates. Such an intake is free on a commercial approver's
        # stamp, like any other zero-charge job (Request Goodwill).
        return self._fix_approved_waiver_basis()

    def _fix_approved_waiver_basis(self) -> str:
        """A goodwill approval or a rework confirmation, while it still covers
        the amount due (A02 ERP audit M01-F2).

        The approval was pinned at the amount due when it was requested -
        BDT 0 before any estimate - and then waived ANY later amount: a
        goodwill granted at intake made a BDT 50,000 repair free. The basis
        now holds only while the amount due is within what was approved; a
        higher amount voids it (request again on the new amount)."""
        self.ensure_one()
        due = None
        if self.is_goodwill and self.goodwill_approved_by:
            due = self._fix_amount_due()
            if due <= (self.goodwill_cost_attribution_bdt or 0.0) + 0.005:
                return "goodwill approved by %s" % self.goodwill_approved_by.name
        if self.is_rework and self.rework_approved_by:
            due = self._fix_amount_due() if due is None else due
            if due <= (self.rework_approved_amount_bdt or 0.0) + 0.005:
                return "rework confirmed by %s" % self.rework_approved_by.name
        return ""

    def _fix_warranty_exclusion(self) -> str:
        """Why the warranty does not cover this job, or '' (A02 ERP audit
        M01-F14): a tripped liquid-contact indicator, or a coded fault of a
        customer-induced category (Physical / Liquid Damage). Behind
        WARRANTY_EXCLUDES_DAMAGE_PARAM (default on)."""
        self.ensure_one()
        if not _param_on(self.env, WARRANTY_EXCLUDES_DAMAGE_PARAM, "1"):
            return ""
        if self.lci_tripped:
            return "liquid contact indicator tripped"
        codes = [c for c in self.fault_line_ids.mapped("fault_code") if c]
        if codes:
            induced = (
                self.env["fix.fault.code"]
                .sudo()
                .with_context(active_test=False)
                .search([("code", "in", codes), ("category", "in", _CUSTOMER_INDUCED_CATEGORIES)])
            )
            if induced:
                return "customer-induced fault %s" % ", ".join(induced.mapped("code"))
        return ""

    def _check_commercial_clearance(self) -> None:
        """M01-2: the customer's approval of the price, or an entitlement."""
        self.ensure_one()
        if self.env.su:
            return  # trusted service code (crons, data loads) decides itself
        if self._fix_zero_charge_basis():
            return
        approved = self.estimate_ids.filtered(lambda e: e.state == "approved")
        if not approved:
            raise UserError(
                "Order %s cannot be approved: it has no approved estimate and no "
                "warranty, AMC or approved goodwill entitlement. Send the estimate "
                "and record the customer's approval first." % self.name
            )

    def _fix_settlement_covers(self, due: float) -> bool:
        return (
            self.payment_settlement_state == "settled"
            and (self.amount_settled_bdt or 0.0) + 0.005 >= due
            and (self.settlement_verified or self._fix_try_verify_from_receipt())
        )

    def _check_delivery_settlement_gate(self) -> None:
        """FLAW-01.1: Prevent handover/delivery of chargeable orders when an
        approved estimate exists with payable balance > 0 and payment is unpaid."""
        self.ensure_one()
        if self._fix_zero_charge_basis():
            return
        approved_estimates = self.estimate_ids.filtered(
            lambda e: e.state == "approved" and e.grand_total > 0
        )
        # what is still DUE decides, not the estimate's face value: advances
        # already received (the walk-in diagnostic fee) can cover it in full
        if (
            approved_estimates
            and self.payment_settlement_state in ("unpaid", "partial")
            and self._fix_amount_due() > 0.005
        ):
            total_due = self._fix_amount_due()
            raise UserError(
                f"FLAW-01.1 Financial Settlement Gate: Order {self.name} has an approved "
                f"chargeable estimate of BDT {total_due:.2f} that is still 'unpaid'. "
                "Settle the invoice or record payment before delivering the device."
            )
        if self.env.su:
            return
        due = self._fix_amount_due()
        if due <= 0 or self._fix_credit_covers(due):
            return
        if self.payment_settlement_state == "credit_approved":
            raise UserError(
                f"Order {self.name} was released on credit for BDT "
                f"{self._fix_credit_released_amount():.2f}; BDT {due:.2f} is due now. A Finance "
                "Manager releases it on credit again for the new amount, or it is paid."
            )
        if self._fix_cod_covers(due):
            return  # D1: the rider hands the device over as the cash is taken
        if not self._fix_settlement_covers(due):
            raise UserError(
                f"FLAW-01.1 Financial Settlement Gate: Order {self.name} owes BDT {due:.2f}. "
                "The device is released only on a verified settlement that covers it "
                f"(recorded: BDT {self.amount_settled_bdt or 0.0:.2f}, "
                f"{'verified' if self.settlement_verified else 'not verified'})."
            )

    def _fix_credit_released_amount(self) -> float:
        """What a credit release covers (cd_billing_engine pins it)."""
        self.ensure_one()
        if "credit_released_amount" not in self._fields:
            return 0.0
        return self.credit_released_amount or 0.0

    def _fix_credit_covers(self, due: float) -> bool:
        """A02 pass 2 (M01-04): an order released on credit is honoured up to
        the amount the Finance Manager released; a higher amount due is not
        covered (the release was for the price at the time)."""
        self.ensure_one()
        if self.payment_settlement_state != "credit_approved":
            return False
        if "credit_released_amount" not in self._fields:
            return True  # no billing engine: nothing pins a release
        return due <= self._fix_credit_released_amount() + 0.005

    def _fix_cod_covers(self, due: float) -> bool:
        """D1: a cash-on-delivery collection recorded at the doorstep that
        covers the amount due (unverified until the rider settles it)."""
        self.ensure_one()
        return (
            self.payment_settlement_state == "settled"
            and self.settlement_source == "cod"
            and (self.amount_settled_bdt or 0.0) + 0.005 >= due
        )

    def _fix_delivery_leg_allowed(self):
        """D1 contract with M03 (stream S3): may the device go out on a
        delivery leg now? ``(ok, reason)``. Only a Ready order, and only one
        that owes nothing, or whose credit release or VERIFIED settlement
        covers what it owes. When this refuses for money, the leg may still go
        as a cash-on-delivery leg (the rider collects the amount due)."""
        self.ensure_one()
        order = self.sudo()
        if order.state != "ready":
            return False, "Order %s is %s: only a Ready order goes out for delivery." % (
                order.name,
                order.state,
            )
        if order._fix_zero_charge_basis():
            return True, ""
        due = order._fix_amount_due()
        if due <= 0.005:
            return True, ""
        if order._fix_credit_covers(due):
            return True, ""
        if order._fix_settlement_covers(due):
            return True, ""
        return False, (
            "Order %s owes BDT %.2f and has no verified payment or credit release that covers "
            "it: send it as a cash-on-delivery leg, or take the payment first." % (order.name, due)
        )

    def _check_delivery_evidence(self) -> None:
        """A5 / M01-10: 0 of 47 delivered orders had an OTP, a recipient or a
        signed report. Behind DELIVERY_EVIDENCE_PARAM (default on)."""
        self.ensure_one()
        if self.env.su or not _param_on(self.env, DELIVERY_EVIDENCE_PARAM, "1"):
            return
        missing = []
        if not self.delivery_otp_verified:
            missing.append("the customer's handover OTP (Send / Verify Delivery OTP)")
        if not (self.recipient_name or "").strip():
            missing.append("the collecting recipient's name")
        if not self.service_report_attachment_id:
            missing.append("the signed service delivery report")
        elif not self._fix_own_attachment(self.service_report_attachment_id):
            # A02 pass 2 (M01-12): any attachment (another order's report)
            # passed as this handover's signed report
            missing.append("the signed service delivery report uploaded on this order itself")
        if missing:
            raise UserError(
                "Order %s cannot be delivered without %s." % (self.name, "; ".join(missing))
            )

    def _check_close_gate(self) -> None:
        """The close gate (see _fix_close_problem); trusted code decides
        itself."""
        self.ensure_one()
        if self.env.su:
            return
        problem = self._fix_close_problem()
        if problem:
            raise UserError(problem)

    def _fix_close_problem(self) -> str:
        """M01-11: settled (verified, covering the amount due), a paid M20
        invoice, or credit approved; or a zero-charge entitlement.

        A02 audit M01-P2: a warranty job's OEM claim was raised only AFTER the
        close (AUT-018 consumed service_order.closed), so a job could close
        with no claim ever raised. action_close now raises it first
        (_fix_raise_warranty_claim) and the gate refuses a warranty job with
        no claim while cd_warranty_claims is installed.

        A02 pass 2: the reason the order cannot close, or '' - evaluated the
        same way for a person and for the close cron (M01-05), which runs as
        the system and must not skip it. A warranty order needs its before
        and after photos on the order (M01-06, BRU-SRM-17); credit counts only
        up to the amount released (M01-04)."""
        self.ensure_one()
        if self.order_category == "warranty":
            self._fix_adopt_intake_photo()
            missing = [
                label
                for label, att in (
                    ("the intake photo", self.intake_photo_attachment_id),
                    ("the after-repair photo", self.after_repair_photo_attachment_id),
                )
                if not self._fix_own_attachment(att, image=True)
            ]
            if missing:
                return (
                    "Warranty order %s cannot be closed without %s uploaded on the order "
                    "(BRU-SRM-17: the OEM claim needs the device before and after)."
                    % (self.name, " and ".join(missing))
                )
        basis = self._fix_zero_charge_basis()
        if basis:
            Claim = self.env.get("fix.warranty.claim")
            if (
                self.order_category == "warranty"
                and Claim is not None
                and not Claim.sudo().search_count([("service_order_id", "=", self.id)])
            ):
                return (
                    "Warranty order %s cannot be closed before its OEM warranty claim is "
                    "raised (the claim could not be created: check the device's brand and "
                    "the order's branch)." % self.name
                )
            return ""
        due = self._fix_amount_due()
        if due <= 0 or self._fix_credit_covers(due):
            return ""
        if (
            self.settlement_source == "cod"
            and self.payment_settlement_state == "settled"
            and not self.settlement_verified
        ):
            # D1 (A02 pass 2 review): the COD receipt pays the invoice in the
            # books at the door, which read as a paid invoice here; the cash is
            # still with the rider or courier until it is handed in
            return (
                "Order %s cannot be closed: BDT %.2f of its payments (cash on delivery %s, or a "
                "part payment before it) is not verified yet; the rider settlement or courier "
                "remittance confirms the cash on delivery, a cashier the rest."
                % (
                    self.name,
                    (self.amount_settled_bdt or 0.0) - (self.amount_verified_bdt or 0.0),
                    self.invoice_ref or "-",
                )
            )
        if not (self._fix_settlement_covers(due) or self._fix_paid_invoice(due)):
            return (
                "Order %s cannot be closed: BDT %.2f is due and no verified settlement, "
                "paid invoice or approved credit covers it." % (self.name, due)
            )
        return ""

    def _fix_adopt_intake_photo(self) -> None:
        """A02 pass 2 (M01-06): the walk-in intake (M04) takes the 4-angle
        photo, and the order never had it. The intake's photo is copied onto
        the order (read through the registry: M01 does not depend on M04)."""
        Intake = self.env.get("fix.walkin.intake")
        if Intake is None:
            return
        for order in self.filtered(lambda o: not o.intake_photo_attachment_id):
            intake = Intake.sudo().search(
                [("service_order_id", "=", order.id), ("intake_photo_attachment_id", "!=", False)],
                order="id desc",
                limit=1,
            )
            if not intake:
                continue
            photo = intake.intake_photo_attachment_id.sudo().copy(
                {"res_model": order._name, "res_id": order.id}
            )
            order.sudo().write({"intake_photo_attachment_id": photo.id})
            order.message_post(
                body="Intake photo %s copied from walk-in intake %s." % (photo.name, intake.name)
            )

    def _fix_paid_invoice(self, due: float) -> bool:
        """A paid M20 invoice raised for this order that covers ``due``."""
        self.ensure_one()
        Invoice = self.env.get("fix.ar.invoice")
        if Invoice is None:
            return False
        paid = Invoice.sudo().search(
            [
                ("source_model", "=", self._name),
                ("source_id", "=", self.id),
                ("state", "=", "paid"),
            ]
        )
        return sum(paid.mapped("total_payable")) + 0.005 >= due if paid else False

    def _fix_raise_warranty_claim(self) -> None:
        """Raise the OEM claim of a warranty job before it closes (A02 audit
        M01-P2). cd_warranty_claims' own entry point, idempotent per order;
        a failure leaves the close gate to refuse with the reason."""
        Claim = self.env.get("fix.warranty.claim")
        if Claim is None:
            return
        for order in self.filtered(lambda o: o.order_category == "warranty"):
            try:
                with self.env.cr.savepoint():
                    Claim.sudo().consume_order_completed(
                        {
                            "aggregate_id": order.id,
                            "payload": {"completed_at": fields.Datetime.now()},
                        }
                    )
            except Exception as exc:  # a NOT NULL from the claim module too
                logger.warning("Warranty claim not raised for %s: %s", order.name, exc)

    def write(self, vals):
        if self and not self._fix_guard_open():
            # The guard runs FIRST, so a forged state is refused as a forgery
            # rather than as a bad transition.
            self._fix_refuse_direct_changes(vals)
        old_states = {}
        if "state" in vals:
            for rec in self:
                rec._validate_transition(vals["state"])
                old_states[rec.id] = rec.state
        result = super().write(vals)
        evidence = _ORDER_EVIDENCE_FIELDS & set(vals)
        if evidence:
            self._fix_bind_evidence(evidence)
        if "state" in vals:
            for rec in self:
                rec._on_state_change(vals["state"], old_states[rec.id])
        if "order_category" in vals:
            # M01-1 / BRU-SRM-02: a re-classification re-runs the warranty gate
            # (it only ran in create, so a standard order became 'warranty').
            self._check_warranty_gate()
        if vals.get("technician_id"):
            # A02 ERP audit M01-F15/F20: assigning the technician is the
            # response (spec: "assignment to first action"). A draft order has
            # no clock yet: stamping it there made intake skip the response
            # clock, and the order fell out of response-SLA reporting.
            self.filtered(
                lambda o: o.state not in _SLA_FINISHED_STATES and o.state != "draft"
            )._fix_mark_response()
        return result

    def _fix_refuse_direct_changes(self, vals) -> None:
        guarded = self._fix_guarded_fields() & set(vals)
        # read through sudo: a guarded field may also be group-restricted
        # (passcode_value), and the refusal must be the guard's, not a read error
        changed = {
            name
            for rec in self
            for name in guarded
            if rec._fix_guard_differs(name, vals[name], rec.sudo()[name])
        }
        if changed:
            self._fix_guard_refuse(changed)
        if "ber_photo_attachment_id" in vals:
            for rec in self.filtered("ber_proposed_at"):
                if rec._fix_guard_differs(
                    "ber_photo_attachment_id",
                    vals["ber_photo_attachment_id"],
                    rec.ber_photo_attachment_id,
                ):
                    raise UserError(
                        "The BER of order %s is proposed: its photo evidence is frozen." % rec.name
                    )
        for rec in self:
            if rec.state == "draft":
                continue
            for name in set(vals) & _FROZEN_AFTER_INTAKE:
                if rec._fix_guard_differs(name, vals[name], rec[name]):
                    raise UserError(
                        "%s of order %s is fixed once the order is taken in: the customer's "
                        "codes and approvals are bound to it. A Service Supervisor changes it "
                        "with %s, which records the reason."
                        % (
                            self._fields[name].string or name,
                            rec.name,
                            _FROZEN_AFTER_INTAKE_ACTION[name],
                        )
                    )
        for rec in self:
            frozen = rec.state in ("delivered", "closed", "cancelled")
            names = set(vals) & (_SET_AT_INTAKE | (_FROZEN_WHEN_DONE if frozen else set()))
            for name in names:
                if not rec._fix_guard_differs(name, vals[name], rec[name]):
                    continue
                label = self._fields[name].string or name
                if frozen:
                    raise UserError(
                        "Order %s is %s: %s is part of the handover record and can no "
                        "longer change." % (rec.name, rec.state, label)
                    )
                action = "Change Category" if name == "order_category" else "Override Priority"
                raise UserError(
                    "%s of order %s is set at intake. Change it with %s, which records "
                    "the reason and who changed it." % (label, rec.name, action)
                )

    def _fix_bind_evidence(self, names) -> None:
        """A02 pass 2 (M01-06/12): an evidence file uploaded for the order and
        attached to no record yet is bound to the order; one that belongs to
        another record stays where it is (the gates then refuse it: the
        evidence is uploaded on the order itself)."""
        for order in self:
            for name in names:
                attachment = order[name].sudo()
                if attachment and not attachment.res_model:
                    attachment.write({"res_model": order._name, "res_id": order.id})

    def _fix_own_attachment(self, attachment, image=False) -> bool:
        """``attachment`` is a file uploaded on this order (an image when
        ``image``)."""
        self.ensure_one()
        att = attachment.sudo() if attachment else attachment
        if not att or att.res_model != self._name or att.res_id != self.id:
            return False
        return not image or (att.mimetype or "").startswith("image/")

    def _on_state_change(self, new_state: str, old_state: str) -> None:
        """Hook for side effects on state changes. ``old_state`` is captured
        before the write: reading ``self.state`` here (after it) recorded every
        history entry as "<new> -> <new>"."""
        self._fix_publish_state(new_state)
        self.device_id.add_history(
            "service_order", f"Order {self.name}: {old_state} -> {new_state}", order_id=self.id
        )
        now = fields.Datetime.now()
        stamps = {}

        # SLA clock events. A02 ERP audit M01-F15: the resolution promise is
        # "intake to ready" (fix.sla.policy.resolution_hours), and the
        # resolution clock succeeds at Ready, so Ready is the resolution time
        # (it was stamped at delivery, so the compliance report and TAT counted
        # the customer's collection delay against the repair). The response
        # is the first diagnostic action or assignment (_fix_mark_response),
        # not the start of repair.
        if new_state == "ready":
            stamps["ready_at"] = now
            if not self.sla_resolution_at:
                stamps["sla_resolution_at"] = now
        if new_state == "intake" and not self.intake_completed_at:
            stamps["intake_completed_at"] = now
        if new_state in ("delivered", "closed") and not self.sla_resolution_at:
            stamps["sla_resolution_at"] = now  # a legacy order that never stamped Ready
        if new_state == "delivered" and not self.delivered_at:
            stamps["delivered_at"] = now
        if new_state == "closed" and not self.closed_at:
            stamps["closed_at"] = now
        if new_state == "qc_pending":
            # A02 ERP audit M01-F4: a new QC round
            stamps["qc_round"] = (self.qc_round or 0) + 1
        if stamps:
            self._guarded().write(stamps)
        if new_state == "intake":
            self._fix_start_sla()
            if self.technician_id:
                # assigned while still a draft: the response is met as the
                # clock starts, and the clock exists to record it
                self._fix_mark_response()
        if new_state == "diagnostic":
            self._fix_mark_response()
        if new_state == "delivered":
            # A02 ERP audit M01-F21 (FR-SRM-020/045): OUR repair warranty is
            # issued with the handover, from the order's warranty days.
            self._fix_auto_issue_repair_warranty()
        if new_state in ("delivered", "cancelled"):
            # A02 ERP audit M01-F8 / BRU-SRM-20: purged at handover
            self._fix_purge_passcode()
        if new_state in _SLA_FINISHED_STATES:
            if self.sla_clock_paused:
                self._guarded().write(self._fix_resume_stamps(now))
            self._fix_sla_instances("succeed" if new_state != "cancelled" else "cancel")
        else:
            # FLAW-01.3 / A02 audit B3: the hold is derived from the order's
            # state and system-set facts, never from a field a user edits.
            self._fix_sync_sla_pause()

    def _fix_publish_state(self, new_state: str) -> None:
        """One LITERAL publish per state (A02 audit B2): the old
        _emit(f"service_order.{state}") hid every lifecycle event from the
        event-registry tooling, which reads publish() call sites."""
        env, agg, payload = self.env, "fix.service.order", self._fix_event_payload()
        if new_state == "intake":
            publish(env, "service_order.intake", agg, self.id, payload)
        elif new_state == "diagnostic":
            publish(env, "service_order.diagnostic", agg, self.id, payload)
        elif new_state == "estimate_pending":
            publish(env, "service_order.estimate_pending", agg, self.id, payload)
        elif new_state == "estimate_sent":
            publish(env, "service_order.estimate_sent", agg, self.id, payload)
        elif new_state == "awaiting_approval":
            publish(env, "service_order.awaiting_approval", agg, self.id, payload)
        elif new_state == "approved":
            publish(env, "service_order.approved", agg, self.id, payload)
        elif new_state == "in_repair":
            publish(env, "service_order.in_repair", agg, self.id, payload)
        elif new_state == "qc_pending":
            publish(env, "service_order.qc_pending", agg, self.id, payload)
        elif new_state == "qc_failed":
            publish(env, "service_order.qc_failed", agg, self.id, payload)
        elif new_state == "ready":
            publish(env, "service_order.ready", agg, self.id, payload)
        elif new_state == "delivered":
            publish(env, "service_order.delivered", agg, self.id, payload)
        elif new_state == "closed":
            publish(env, "service_order.closed", agg, self.id, payload)
        elif new_state == "cancelled":
            publish(env, "service_order.cancelled", agg, self.id, payload)

    def _fix_event_payload(self) -> dict:
        self.ensure_one()
        return {
            "order_id": self.id,
            "service_order_id": self.id,
            "name": self.name,
            "device_id": self.device_id.id,
            "customer_id": self.customer_id.id,
            "state": self.state,
        }

    # --- SLA hold (FLAW-01.3, A02 audit B3) ---
    def _fix_live_pickup_legs(self):
        """Pickup consignments still bringing the device to us (cd_consignment,
        read through the registry: M01 does not depend on M03)."""
        self.ensure_one()
        if "consignment_ids" not in self._fields:
            return self.env["fix.service.order"].browse()
        return self.sudo().consignment_ids.filtered(
            lambda c: c.consignment_type == "pickup"
            and c.state in ("draft", "confirmed", "in_transit", "held")
        )

    def _fix_sla_hold_reason(self) -> str:
        """Why the resolution clock waits now, or '' when it runs.

        ServiceNow-style pause conditions: awaiting the customer (estimate
        decision), awaiting parts (a supervisor's deferred hold), awaiting
        pickup (a live pickup leg). Each is a state or a fact the system
        sets; none is a box a user ticks."""
        self.ensure_one()
        if self.state in _SLA_FINISHED_STATES:
            return ""
        if self.state in ("estimate_sent", "awaiting_approval"):
            return "Awaiting the customer's estimate decision"
        if self.is_deferred_block:
            if self.deferred_reason == "parts_backorder":
                return "Awaiting parts (deferred hold)"
            label = dict(self._fields["deferred_reason"]._description_selection(self.env)).get(
                self.deferred_reason, self.deferred_reason or "hold"
            )
            return "Deferred hold: %s" % label
        legs = self._fix_live_pickup_legs()
        if legs:
            return "Awaiting pickup (%s)" % ", ".join(legs.mapped("name"))
        return ""

    def _fix_sync_sla_pause(self) -> None:
        """Pause or resume the clock to match _fix_sla_hold_reason()."""
        now = fields.Datetime.now()
        for order in self:
            reason = order._fix_sla_hold_reason()
            if reason:
                if not order.sla_clock_paused:
                    order._guarded().write({"sla_clock_paused": True, "sla_paused_at": now})
                # also catches a clock started while the order was already held
                order._fix_sla_instances("pause", reason)
            elif order.sla_clock_paused:
                order._guarded().write(order._fix_resume_stamps(now))
                order._fix_sla_instances("resume")

    def _fix_sla_target_moved(self, instance) -> None:
        """Called by fix.sla.kpi.instance when a resumed clock gets its new
        deadline: the order's own deadline follows it (see
        _fix_notify_target_moved for why that matters)."""
        field = {
            "resolution": "sla_resolution_deadline",
            RESPONSE_KPI: "sla_response_deadline",
        }.get(instance.kpi_code)
        if not field:
            return
        for order in self:
            if order[field] != instance.target_at:
                order._guarded().write({field: instance.target_at})

    def _fix_resume_stamps(self, now) -> dict:
        minutes = self.sla_total_paused_minutes or 0.0
        if self.sla_paused_at:
            minutes += max(0.0, (now - self.sla_paused_at).total_seconds() / 60.0)
        return {
            "sla_clock_paused": False,
            "sla_paused_at": False,
            "sla_total_paused_minutes": round(minutes, 2),
        }

    # --- SLA (M01-7: no clock ran on any of 930 orders) ---
    def _fix_start_sla(self) -> None:
        """Start the resolution clock at intake from the order's policy (or
        the active policy for its channel and priority). Best effort: a policy
        problem is logged, never blocks the intake."""
        Instance = self.env["fix.sla.kpi.instance"].sudo()
        for order in self:
            policy = order.sla_policy_id.sudo() or order._fix_match_sla_policy(order.priority)
            if not policy:
                # A02 audit B3: an order whose channel or priority matched no
                # policy got no clock at all (0 of 930 had a deadline).
                policy = self.env.ref(DEFAULT_SLA_POLICY, raise_if_not_found=False)
                policy = policy.sudo() if policy and policy.active else None
            if not policy:
                logger.warning("No SLA policy for %s, and the default is archived", order.name)
                continue
            try:
                with self.env.cr.savepoint():
                    start = order.intake_completed_at or fields.Datetime.now()
                    inst = Instance.start_for(order, policy, "resolution", started_at=start)
                    vals = {"sla_resolution_deadline": inst.target_at}
                    # A02 ERP audit M01-F20: the response promise is a clock of
                    # its own (it was a deadline nothing ever measured).
                    if not order.sla_response_at:
                        response = Instance.start_for(order, policy, RESPONSE_KPI, started_at=start)
                        vals["sla_response_deadline"] = response.target_at
                    if not order.sla_policy_id:
                        order.sudo().sla_policy_id = policy.id
                    order._guarded().write(vals)
            except (UserError, ValidationError) as exc:
                logger.warning("SLA clock not started for %s: %s", order.name, exc)

    def _fix_match_sla_policy(self, priority):
        """The active repair SLA policy for this order's channel and
        ``priority``, or an empty recordset."""
        self.ensure_one()
        return (
            self.env["fix.sla.policy"]
            .sudo()
            .search(
                [
                    ("service_type", "=", self.service_type),
                    ("priority", "=", priority),
                    ("active", "=", True),
                    ("company_id", "in", [self.company_id.id, False]),
                    # the contact centre's per-queue answer targets (CC-*)
                    # are walk_in/normal too; they are not repair promises
                    ("code", "not =like", "CC-%"),
                ],
                order="id",
                limit=1,
            )
        )

    def _fix_mark_response(self) -> None:
        """A02 ERP audit M01-F15/F20: the first response - the diagnostic
        starts or a technician is assigned, whichever is first - is stamped
        once and ends the response clock (met or breached against its
        target, fix.sla.kpi.instance.succeed)."""
        now = fields.Datetime.now()
        Instance = self.env["fix.sla.kpi.instance"].sudo()
        for order in self.filtered(lambda o: not o.sla_response_at):
            order._guarded().write({"sla_response_at": now})
            for inst in Instance.for_record(order, kpi_code=RESPONSE_KPI):
                try:
                    with self.env.cr.savepoint():
                        inst.succeed(when=now)
                except (UserError, ValidationError) as exc:
                    logger.warning("Response clock of %s not closed: %s", order.name, exc)

    def _fix_reselect_sla(self, reason: str) -> None:
        """A02 ERP audit M01-F19: a priority change re-selects the SLA policy
        for the new priority and moves the live clocks to it. The business
        time already used is kept: the new deadline is the new target minus
        the time used, from now (a held clock stays held)."""
        Instance = self.env["fix.sla.kpi.instance"].sudo()
        for order in self:
            policy = order._fix_match_sla_policy(order.priority)
            if not policy or policy == order.sla_policy_id:
                continue
            old_policy = order.sla_policy_id
            order.sudo().sla_policy_id = policy.id
            vals = {}
            for inst in Instance.for_record(order):
                if inst.kpi_code not in ("resolution", RESPONSE_KPI):
                    continue
                # the same target a fresh start would take (start_for): the
                # policy's item for the KPI when it has one, else the header
                item = policy.item_ids.filtered(
                    lambda i, code=inst.kpi_code: i.kpi_code == code and i.active
                )[:1]
                new_hours = (
                    item.target_hours
                    if item
                    else (
                        policy.resolution_hours
                        if inst.kpi_code == "resolution"
                        else policy.response_hours
                    )
                )
                warn_pct = (item.warn_at_pct if item else 0.0) or 80.0
                calendar = Instance._effective_calendar(policy, item or None)
                old_calendar = inst.calendar_id or None
                now = fields.Datetime.now()
                upto = inst.paused_at if inst.state == "paused" else now
                left = Instance.business_minutes_between(upto, inst.target_at, old_calendar) / 60.0
                used = max(0.0, (inst.target_hours or 0.0) - left)
                remaining = max(0.0, new_hours - used)
                was_paused = inst.state == "paused"
                inst.cancel(
                    "Priority changed to %s: re-selected policy %s (was %s). %s"
                    % (order.priority, policy.code, old_policy.code or "-", reason)
                )
                target = Instance.add_business_hours(now, remaining, calendar)
                successor = Instance.create(
                    {
                        "res_model": order._name,
                        "res_id": order.id,
                        "partner_id": inst.partner_id.id,
                        "policy_id": policy.id,
                        "kpi_code": inst.kpi_code,
                        "calendar_id": calendar.id if calendar else False,
                        "target_hours": new_hours,
                        "started_at": now,
                        "target_at": target,
                        "warn_at": Instance.add_business_hours(
                            now, remaining * warn_pct / 100.0, calendar
                        ),
                        "elapsed_pause_minutes": inst.elapsed_pause_minutes,
                        "supersedes_id": inst.id,
                        "series_index": inst.series_index + 1,
                    }
                )
                inst._guarded().write({"superseded_by_id": successor.id})
                if was_paused:
                    successor.pause(inst.pause_reason or "held")
                field = (
                    "sla_resolution_deadline"
                    if inst.kpi_code == "resolution"
                    else "sla_response_deadline"
                )
                vals[field] = target
            if vals:
                order._guarded().write(vals)
            order.message_post(
                body="SLA policy re-selected for priority %s: %s (was %s)."
                % (order.priority, policy.display_name, old_policy.display_name or "-")
            )

    def _fix_sla_instances(self, verb: str, reason: str = "") -> None:
        Instance = self.env["fix.sla.kpi.instance"].sudo()
        for order in self:
            for inst in Instance.for_record(order):
                try:
                    with self.env.cr.savepoint():
                        if verb == "pause" and inst.state == "in_progress":
                            inst.pause(reason)
                        elif verb == "resume" and inst.state == "paused":
                            inst.resume()
                        elif verb == "succeed" and inst.state in ("in_progress", "paused"):
                            inst.succeed()
                        elif verb == "cancel" and inst.state in ("in_progress", "paused"):
                            inst.cancel("Order %s cancelled" % order.name)
                except (UserError, ValidationError) as exc:
                    logger.warning("SLA %s skipped for %s: %s", verb, order.name, exc)

    # --- transitions: every one writes state through the guard token ---
    def _fix_advance(self, new_state: str, extra=None) -> None:
        """The one way an action moves an order: the transition check and its
        gates run in write(); the token lets the guarded field through."""
        for order in self:
            if order.state == new_state:
                continue
            vals = dict(extra or {}, state=new_state)
            order._guarded().write(vals)

    # The action that owns each target state (M31 sync, M04 consoles and the
    # P03 stage button call action_transition instead of writing state).
    _ACTION_FOR_STATE = {
        "intake": "action_intake",
        "diagnostic": "action_start_diagnostic",
        "estimate_pending": "action_request_estimate",
        "estimate_sent": "action_send_estimate",
        "awaiting_approval": "action_await_approval",
        "approved": "action_approve",
        "in_repair": "action_start_repair",
        "qc_pending": "action_submit_qc",
        "qc_failed": "action_qc_fail",
        "ready": "action_ready",
        "delivered": "action_deliver",
        "closed": "action_close",
        "cancelled": "action_cancel",
    }

    def action_transition(self, new_state, **kwargs):
        """Move to ``new_state`` through the action that owns it, so its own
        checks apply. For callers outside M01 that used to write state."""
        method = self._ACTION_FOR_STATE.get(new_state)
        if not method:
            raise UserError("Unknown service order state: %s" % new_state)
        for order in self:
            if order.state != new_state:
                getattr(order, method)(**kwargs)
        return True

    def action_intake(self):
        self._fix_advance("intake")

    def action_start_diagnostic(self):
        self._fix_advance("diagnostic")

    def action_request_estimate(self):
        """Diagnosis done: the fault is coded, the estimate is being prepared.
        The fault is known now, so the rework check runs again (BRU-SRM-06)."""
        self._fix_advance("estimate_pending")
        self._flag_rework()

    def action_send_estimate(self):
        """Send the prepared estimate; sending it moves the order on.

        A02 audit M01-P2: with no estimate at all the order still moved to
        'estimate_sent' and paused its SLA clock on a quote nobody had. It
        now needs a draft estimate to send, or one already with the customer
        (a zero-charge entitlement job has no price to send)."""
        for order in self:
            drafts = order.estimate_ids.filtered(lambda e: e.state == "draft")
            if drafts and order.state in ("diagnostic", "estimate_pending"):
                drafts.sorted(lambda e: (e.version, e.id))[-1].action_send()
            elif not (
                order.estimate_ids.filtered(lambda e: e.state == "sent")
                # a warranty / AMC / approved-goodwill job has no price to send
                or order._fix_zero_charge_basis()
                # trusted service code decides itself, as at approval
                or self.env.su
            ):
                raise UserError(
                    "Order %s has no estimate to send. Prepare the estimate (parts, labour, "
                    "diagnostic lines) first." % order.name
                )
            order._fix_advance("estimate_sent")

    def action_await_approval(self):
        """The customer has the estimate and its decision is awaited.

        A02 audit M01-P2: this checked nothing. It needs an estimate that is
        with the customer (sent), still valid, and priced."""
        today = fields.Date.context_today(self)
        for order in self:
            sent = order.estimate_ids.filtered(
                lambda e: e.state == "sent"
                and e.line_ids
                and not (e.expiry_date and e.expiry_date < today)
            )
            if not (sent or order._fix_zero_charge_basis() or self.env.su):
                raise UserError(
                    "Order %s is not awaiting a decision: it has no valid estimate with the "
                    "customer. Send (or revise and re-send) the estimate first." % order.name
                )
            order._fix_advance("awaiting_approval")

    def action_approve(self):
        self._fix_advance("approved")

    def action_start_repair(self):
        self._fix_advance("in_repair")

    def action_submit_qc(self):
        for order in self:
            order._fix_advance("qc_pending", {"repair_completed_by": self.env.user.id})

    def action_qc_fail(self):
        self._fix_advance("qc_failed")

    def action_fail_qc(self):
        """qc_pending -> qc_failed: the name the M31 workshop sync calls."""
        return self.action_qc_fail()

    def action_mark_unrepairable(self, reason=None):
        """Beyond economic repair (M31 BER confirmation, spec §5 exceptions):
        the order leaves through the cancellation path with reason
        'unrepairable', so its estimate, field order and workshop job are
        closed and a settled amount is handed to M20 for refund.

        A02 ERP audit M01-F9 / BRU-SRM-12 (H): a BER needs photographic
        evidence and a SECOND technician's confirmation; one press with a
        reason wrote the device off. Now two steps:
          1. a technician proposes it, with the photo attached
             (ber_photo_attachment_id) and the reason;
          2. another technician confirms it: the order is cancelled.
        A BER the workshop (M31) already proposed with evidence and had
        confirmed by a second technician closes the order at once."""
        for order in self:
            if order.state not in ("diagnostic", "in_repair", "qc_pending", "qc_failed"):
                raise UserError(
                    "Order %s is %s: it is marked unrepairable from diagnosis, repair or QC."
                    % (order.name, order.state)
                )
            if order._fix_ber_evidenced():
                order.action_cancel(
                    reason_code="unrepairable",
                    note=(reason or "").strip() or order.ber_reason or "Beyond economic repair",
                )
            elif not order.ber_proposed_at:
                order._fix_propose_ber(reason)
            else:
                order._fix_confirm_ber(reason)
        return True

    def _fix_m31_ber_job(self):
        """A workshop job of this order whose BER M31 proposed (with its
        evidence) and a different person confirmed (cd_workshop, read through
        the registry: M01 does not depend on M31)."""
        self.ensure_one()
        if "workshop_job_ids" not in self._fields:
            return None
        return self.sudo().workshop_job_ids.filtered(
            lambda j: j.ber_proposed_at
            and j.ber_confirmed_at
            and j.ber_confirmed_by_id
            and j.ber_confirmed_by_id != j.ber_proposed_by_id
        )[:1]

    def _fix_ber_evidenced(self) -> bool:
        """BRU-SRM-12 is satisfied: confirmed here by a second technician, or
        confirmed in the workshop, or trusted service code decides."""
        self.ensure_one()
        return bool(self.env.su or self.ber_confirmed_at or self._fix_m31_ber_job())

    def _fix_is_technical(self, user) -> bool:
        """BRU-SRM-12's "technician": the order's assigned technician, or a
        holder of a technical role. Being an employee was enough, so a
        front-desk clerk could be the second technician and write the device
        off (A02 ERP review, 20 Nov 2026). The workshop and field groups are
        read by xmlid: M01 does not depend on M31 / M02."""
        self.ensure_one()
        if self.env.su:
            return True
        employee = user.employee_id
        if employee and self.technician_id and employee == self.technician_id:
            return True
        for xmlid in BER_TECHNICAL_GROUPS:
            if self.env.ref(xmlid, raise_if_not_found=False) and user.has_group(xmlid):
                return True
        return False

    def _fix_propose_ber(self, reason) -> None:
        self.ensure_one()
        if not (reason or "").strip():
            raise UserError("Give the reason the device cannot be repaired.")
        photo = self.ber_photo_attachment_id
        if not photo or not (photo.sudo().mimetype or "").startswith("image/"):
            raise UserError(
                "BRU-SRM-12: a beyond-economic-repair proposal needs photographic evidence. "
                "Attach the photo of the device (BER Photo Evidence) to order %s first." % self.name
            )
        if photo.sudo().res_model != self._name or photo.sudo().res_id != self.id:
            raise UserError(
                "BRU-SRM-12: upload the BER photo on order %s itself; a file attached to another "
                "record is not this device's evidence." % self.name
            )
        if not self._fix_is_technical(self.env.user):
            raise UserError(
                "BRU-SRM-12: a BER is proposed by a technician (the order's own, a workshop or "
                "field technician, a QC inspector or a Service Supervisor)."
            )
        self._guarded().write(
            {
                "ber_proposed_by": self.env.user.id,
                "ber_proposed_at": fields.Datetime.now(),
                "ber_reason": reason.strip(),
            }
        )
        self.message_post(
            body="Beyond economic repair proposed by %s: %s. A second technician confirms it "
            "(Mark Unrepairable) before the order is closed (BRU-SRM-12)."
            % (self.env.user.name, reason.strip())
        )

    def _fix_confirm_ber(self, reason) -> None:
        self.ensure_one()
        user = self.env.user
        if user == self.ber_proposed_by or (
            user.employee_id and user.employee_id == self.ber_proposed_by.employee_id
        ):
            raise UserError(
                "BRU-SRM-12: the BER of order %s was proposed by you; a second technician "
                "confirms it." % self.name
            )
        if not self._fix_is_technical(user):
            raise UserError(
                "BRU-SRM-12: a second TECHNICIAN (a workshop or field technician, a QC "
                "inspector or a Service Supervisor) confirms the BER of order %s." % self.name
            )
        self._guarded().write(
            {"ber_confirmed_by": user.id, "ber_confirmed_at": fields.Datetime.now()}
        )
        note = self.ber_reason or ""
        if (reason or "").strip():
            note = "%s (confirmed: %s)" % (note, reason.strip())
        self.action_cancel(reason_code="unrepairable", note=note)

    def action_ready(self):
        """BRU-SRM-04 (H): an order cannot reach Ready without a PASSED
        quality checklist — a hard gate, not a warning. Enforced by
        _validate_transition (write), so every path shares the one gate."""
        for order in self:
            order._check_qc_gate()
            order._fix_advance("ready")

    def action_deliver(self):
        for order in self:
            order._check_delivery_settlement_gate()
            extra = {}
            if order.payment_settlement_state == "unpaid" and order._fix_zero_charge_basis():
                extra["payment_settlement_state"] = "covered_zero_charge"
            order._fix_advance("delivered", extra)

    # --- settlement (FLAW-01.1, M01-1/15): the contract with M02, M04, M20 ---
    def _fix_record_settlement(self, amount_bdt, reference, source):
        """Record that the money for this order was taken. The ONE writer of
        the settlement fields (M02's field completion calls it; so does Mark
        Settled).

        ``source`` and what it needs before the DELIVERY gate opens:

        * ``m20_receipt``: a CONFIRMED fix.ar.receipt for this customer whose
          number or reference is ``reference`` and whose amount covers
          ``amount_bdt``, not already used by another order. Verified at once;
          refused when no such receipt exists.
        * ``counter``: taken at the branch counter by a Service Order Cashier,
          who is accountable for it in the cash shift. Verified at once;
          refused for anyone else.
        * ``field_collection``: cash or an MFS TrxID taken on site (M02). The
          technician's typed TrxID is a claim, not money, so it is recorded
          UNVERIFIED. The device stays held until a cashier who did not
          record it verifies it (Verify Settlement), or an M20 receipt with
          that reference is confirmed.

        Refused: an unknown source, a missing reference, an amount that does
        not cover the amount due, a closed or cancelled order."""
        self.ensure_one()
        if source not in _SETTLEMENT_SOURCE_KEYS:
            raise UserError(
                "Unknown settlement source '%s' (expected one of: %s)."
                % (source, ", ".join(sorted(_SETTLEMENT_SOURCE_KEYS)))
            )
        reference = (reference or "").strip()
        if not reference:
            raise UserError(
                "A settlement needs the receipt or transaction reference that proves "
                "the payment (M01-15: no made-up INV/<order> reference)."
            )
        try:
            amount = float(amount_bdt)
        except (TypeError, ValueError):
            raise UserError("Enter the amount received for order %s." % self.name) from None
        if self.state in ("closed", "cancelled"):
            raise UserError("Order %s is %s; it takes no settlement." % (self.name, self.state))
        if self.payment_settlement_state == "settled" and self.settlement_verified:
            raise UserError("Order %s is already settled and verified." % self.name)
        due = self._fix_amount_due()
        if amount <= 0 or amount + 0.005 < due:
            raise UserError(
                "BDT %.2f does not settle order %s: BDT %.2f is due on its estimate."
                % (amount, self.name, due)
            )
        verified = False
        if source == "m20_receipt":
            receipt = self._fix_find_m20_receipt(reference, amount)
            if not receipt:
                raise UserError(
                    "No confirmed M20 receipt '%s' of at least BDT %.2f exists for %s."
                    % (reference, amount, self.customer_id.display_name)
                )
            verified = True
        elif source == "counter":
            if not (self.env.su or self.env.user.has_group(GROUP_CASHIER)):
                raise UserError(
                    "Only a Service Order Cashier records a counter settlement. "
                    "Ask the cashier to take the payment."
                )
            verified = True
        now = fields.Datetime.now()
        vals = {
            "payment_settlement_state": "settled",
            "invoice_ref": reference,
            "amount_settled_bdt": amount,
            "settlement_source": source,
            "settlement_recorded_by": self.env.user.id,
            "settlement_verified": verified,
            "settlement_verified_by": self.env.user.id if verified else False,
            "settlement_verified_at": now if verified else False,
            "amount_verified_bdt": amount if verified else 0.0,
        }
        self._guarded().write(vals)
        self.message_post(
            body="Settlement recorded (%s): %s, BDT %.2f%s."
            % (
                dict(SETTLEMENT_SOURCES)[source],
                reference,
                amount,
                "" if verified else " - NOT YET VERIFIED, the device stays held",
            )
        )
        return True

    def _fix_find_m20_receipt(self, reference, amount):
        """A confirmed M20 receipt for this customer matching ``reference``
        that covers ``amount`` and backs no other order's settlement."""
        self.ensure_one()
        if "fix.ar.receipt" not in self.env:
            return False
        partner = self.customer_id.commercial_partner_id
        receipts = (
            self.env["fix.ar.receipt"]
            .sudo()
            .search(
                [
                    ("state", "=", "confirmed"),
                    "|",
                    ("name", "=", reference),
                    ("reference", "=", reference),
                ]
            )
            .filtered(
                lambda r: r.customer_id.commercial_partner_id == partner
                and (r.amount or 0.0) + 0.005 >= amount
            )
        )
        # A receipt the finance bridge already tied to an order (a settlement
        # or top-up of another order, or any order's advance such as the
        # diagnostic fee) is not free money: it released a device or is netted
        # from an amount due already (A02 ERP review, 20 Nov 2026).
        fields_ = receipts._fields
        if "source_order_id" in fields_:
            receipts = receipts.filtered(
                lambda r: r.source_order_id.id in (False, self.id)
                and not ("is_order_advance" in fields_ and r.is_order_advance)
            )
        # One receipt settles one order. It is found by its number OR its
        # reference, so another order may already hold it under either key
        # (checking only the key typed here let one receipt release two devices).
        Order = self.sudo()
        for receipt in receipts:
            keys = [key for key in (receipt.name, receipt.reference) if key]
            used = Order.search_count(
                [
                    ("id", "!=", self.id),
                    ("invoice_ref", "in", keys),
                    ("settlement_verified", "=", True),
                    ("payment_settlement_state", "in", ("settled", "refund_due")),
                ]
            )
            if not used:
                return receipt
        return False

    def _fix_try_verify_from_receipt(self) -> bool:
        """An unverified field collection becomes verified once an M20
        receipt with its reference is confirmed."""
        self.ensure_one()
        if self.settlement_verified or not self.invoice_ref:
            return bool(self.settlement_verified)
        if self.settlement_source == "cod":
            # D1 (A02 pass 2 review): the COD receipt is booked at the door
            # (Dr COD clearing) while the rider or courier still holds the
            # cash, so it found itself here and verified the collection on
            # the spot. COD is verified when that cash is handed in: the rider
            # settlement or courier remittance (action_confirm_cod_remitted).
            return False
        unverified = (self.amount_settled_bdt or 0.0) - (self.amount_verified_bdt or 0.0)
        receipt = self._fix_find_m20_receipt(self.invoice_ref, max(unverified, 0.0))
        if not receipt:
            return False
        self._guarded().write(
            {
                "settlement_verified": True,
                "settlement_verified_by": self.env.user.id,
                "settlement_verified_at": fields.Datetime.now(),
                "amount_verified_bdt": self.amount_settled_bdt,
            }
        )
        self.message_post(body="Settlement verified against M20 receipt %s." % receipt.name)
        return True

    def action_verify_settlement(self):
        """A cashier confirms a field collection: the cash is in the shift,
        or the MFS TrxID shows in the merchant statement. Never the person
        who recorded it, never the order's technician."""
        for order in self:
            # A02 pass 2 (D3): a part payment taken on site is verified too
            if order.payment_settlement_state not in ("settled", "partial"):
                raise UserError("Order %s has no settlement to verify." % order.name)
            if order.settlement_verified:
                continue
            if order._fix_try_verify_from_receipt():
                continue
            user = self.env.user
            if not (self.env.su or user.has_group(GROUP_CASHIER)):
                raise UserError("Only a Service Order Cashier verifies a collection.")
            if user == order.settlement_recorded_by or (
                order.technician_id and order.technician_id.user_id == user
            ):
                raise UserError(
                    "Segregation of duties: the person who collected or recorded the "
                    "payment cannot verify it."
                )
            order._guarded().write(
                {
                    "settlement_verified": True,
                    "settlement_verified_by": user.id,
                    "settlement_verified_at": fields.Datetime.now(),
                    "amount_verified_bdt": order.amount_settled_bdt,
                }
            )
            order.message_post(
                body="Collection %s verified by %s." % (order.invoice_ref, user.name)
            )
        return True

    def action_mark_settled(
        self, invoice_ref=None, amount_bdt=None, source="counter", reference=None
    ):
        """FLAW-01.1: Record financial invoice settlement before device handover.

        Goes through _fix_record_settlement: no default INV/<order>
        reference and no amount other than one that covers the amount due.
        From an M20 receipt the amount is the receipt's own."""
        reference = reference or invoice_ref
        for order in self:
            amount = amount_bdt
            if amount is None and source == "m20_receipt" and reference:
                receipt = order._fix_find_m20_receipt(reference, 0.0)
                if not receipt:
                    raise UserError(
                        "No confirmed M20 receipt '%s' for %s that another order has not "
                        "already used." % (reference, order.customer_id.display_name)
                    )
                amount = receipt.amount
            if amount is None:
                raise UserError(
                    "Enter the amount received for order %s (BDT %.2f is due)."
                    % (order.name, order._fix_amount_due())
                )
            order._fix_record_settlement(amount, reference, source)
        return True

    def action_close(self):
        # A02 audit M01-P2: the OEM claim is raised before the close gate
        # checks for it, not after the order is already closed.
        self.filtered(lambda o: o.state == "delivered")._fix_raise_warranty_claim()
        self._fix_advance("closed")

    # --- comeback within the repair warranty (BRU-SRM-19, A02 M01-P2) ---
    def action_reopen_comeback(self, reason=None):
        """The customer is back with the same problem while OUR repair
        warranty runs: open a linked rework order. service_warranty_until was
        written and never read, so a comeback was charged as a new job.

        The rework is flagged and linked; it is free only once a commercial
        approver confirms it (Request Rework Approval), as any rework."""
        if not (reason or "").strip():
            raise UserError("Describe the problem the customer came back with.")
        today = fields.Date.context_today(self)
        created = self.browse()
        for order in self:
            if order.state not in ("delivered", "closed"):
                raise UserError(
                    "Order %s is %s: a comeback is opened on a delivered or closed order."
                    % (order.name, order.state)
                )
            if not order.service_warranty_until:
                raise UserError(
                    "Order %s has no repair warranty issued; raise a new order instead."
                    % order.name
                )
            if today > order.service_warranty_until:
                raise UserError(
                    "The repair warranty of order %s ended on %s; the comeback is a new, "
                    "chargeable order." % (order.name, order.service_warranty_until)
                )
            # A02 pass 2 (M01-10): the user's record rules hid a comeback opened
            # at another branch; the search is the system's, fenced to the company
            live = self.sudo().search(
                [
                    ("rework_of_id", "=", order.id),
                    ("state", "not in", ("closed", "cancelled")),
                    ("company_id", "=", order.company_id.id),
                ],
                limit=1,
            )
            if live:
                raise UserError(
                    "Order %s already has an open comeback (%s)." % (order.name, live.name)
                )
            rework = self.create(
                {
                    "device_id": order.device_id.id,
                    "customer_id": order.customer_id.id,
                    "branch_id": order.branch_id.id,
                    "service_type": order.service_type,
                    "order_category": "rework",
                    "fault_description": reason.strip(),
                    "parent_case_id": (order.parent_case_id or order).id,
                    "state": "intake",
                }
            )
            rework._guarded().write({"is_rework": True, "rework_of_id": order.id})
            rework._fix_publish_rework(order, "comeback")
            rework.message_post(
                body="Comeback within the repair warranty of %s (valid until %s): %s"
                % (order.name, order.service_warranty_until, reason.strip())
            )
            order.message_post(body="Comeback opened as %s: %s" % (rework.name, reason.strip()))
            created |= rework
        return created.ids

    def action_cancel(self, reason_code=None, note=None, reason=None):
        """M01-12: a cancellation needs a reason code. It cancels the open
        estimate, field order and workshop job, and a settled order raises
        the refund/credit hand-off (service_order.refund_requested) for M20.

        ``reason`` (one prompt on the workspace) may be "code: note"."""
        if reason and not reason_code:
            head, _sep, tail = str(reason).partition(":")
            if head.strip() in _CANCEL_REASON_KEYS:
                reason_code, note = head.strip(), (tail.strip() or note)
            else:
                reason_code, note = "other", str(reason).strip()
        if reason_code not in _CANCEL_REASON_KEYS:
            raise UserError(
                "Give a cancellation reason: %s." % ", ".join(k for k, _l in CANCEL_REASONS)
            )
        if reason_code == "other" and not (note or "").strip():
            raise UserError("Describe the reason when cancelling for 'Other'.")
        if reason_code == "unrepairable":
            # A02 ERP audit M01-F9: Cancel with reason 'unrepairable' was the
            # second door around BRU-SRM-12.
            for order in self:
                if not order._fix_ber_evidenced():
                    raise UserError(
                        "Order %s: 'unrepairable' needs the BER evidence and a second "
                        "technician's confirmation (BRU-SRM-12). Use Mark Unrepairable."
                        % order.name
                    )
        self._fix_check_post_repair_cancel(reason_code)
        for order in self:
            refund = (
                order.payment_settlement_state in ("settled", "partial")
                and order.amount_settled_bdt > 0
                # D6: a repaired device the customer refuses still owes the
                # approved estimate; the money taken pays its invoice
                and not order._fix_refusal_billed()
            )
            order._fix_cancel_downstream(reason_code, note)
            extra = {
                "cancel_reason_code": reason_code,
                "cancel_note": note or False,
                "cancelled_by": self.env.user.id,
            }
            if refund:
                extra["payment_settlement_state"] = "refund_due"
            order._fix_advance("cancelled", extra)
            if refund:
                publish(
                    self.env,
                    "service_order.refund_requested",
                    "fix.service.order",
                    order.id,
                    {
                        "order_id": order.id,
                        "name": order.name,
                        "customer_id": order.customer_id.id,
                        "amount_bdt": order.amount_settled_bdt,
                        "reference": order.invoice_ref,
                        "settlement_source": order.settlement_source,
                        "reason_code": reason_code,
                    },
                )
            order.message_post(
                body="Order cancelled (%s)%s%s."
                % (
                    dict(CANCEL_REASONS)[reason_code],
                    ": %s" % note if note else "",
                    "; BDT %.2f refund/credit requested" % order.amount_settled_bdt
                    if refund
                    else "",
                )
            )
        return True

    # D6: the states where the repair is done (or being inspected)
    _POST_REPAIR_STATES = ("qc_pending", "qc_failed", "ready")
    _DECLINE_REASON_CODES = ("customer_declined", "estimate_declined")

    def _fix_check_post_repair_cancel(self, reason_code) -> None:
        """A02 pass 2 (M01-03, owner decision D6): a repaired device was
        cancelled by any clerk as 'customer declined', and the customer was
        charged only the diagnostic fee for a repair already done.

        From QC or Ready only a Service Supervisor cancels (a BER confirmed by
        a second technician keeps its own two-person path; a device abandoned
        after the disposal period is cancelled with a branch manager's
        approval, M01-13). A refusal of the finished repair ('customer
        declined' / 'estimate declined') still owes the approved estimate: it
        is refused until that estimate is billed (Bill Refused Repair) or
        waived by an approved goodwill."""
        if self.env.su:
            return
        user = self.env.user
        for order in self.filtered(lambda o: o.state in self._POST_REPAIR_STATES):
            if reason_code == "unrepairable" and order._fix_ber_evidenced():
                continue
            if reason_code == "abandoned":
                order._fix_assert_disposal_allowed()
                continue
            if not user.has_group(GROUP_SUPERVISOR):
                raise UserError(
                    "Order %s is %s: the repair is done, so only a Service Supervisor cancels "
                    "it." % (order.name, order.state)
                )
            if reason_code in self._DECLINE_REASON_CODES and not (
                order._fix_zero_charge_basis() or order._fix_refusal_billed()
            ):
                raise UserError(
                    "Order %s is repaired: a customer who refuses it still owes the approved "
                    "estimate (BDT %.2f). Bill it first (Bill Refused Repair), or have a "
                    "goodwill waiver approved, then cancel." % (order.name, order._fix_amount_due())
                )

    def _fix_refusal_billed(self) -> bool:
        """D6: the approved estimate of a refused repair is billed - a customer
        invoice raised for this order (cd_billing_engine) covers it."""
        self.ensure_one()
        if self.state not in self._POST_REPAIR_STATES or self.cancel_reason_code:
            return False
        Invoice = self.env.get("fix.ar.invoice")
        if Invoice is None:
            return False
        return bool(
            Invoice.sudo().search_count(
                [
                    ("source_model", "=", self._name),
                    ("source_id", "=", self.id),
                    ("state", "in", ("issued", "paid")),
                ]
            )
        )

    def _fix_assert_disposal_allowed(self) -> None:
        """M01-13 (D13): an uncollected device is disposed of (cancelled as
        'abandoned') only once it is flagged abandoned - the disposal period
        after Ready has passed - and only with a branch manager's approval."""
        self.ensure_one()
        if self.env.su:
            return
        if self.state == "ready" and not self.is_abandoned:
            raise UserError(
                "Order %s is not abandoned: a Ready device is disposed of only after %d days "
                "uncollected (the reminders and the formal notice go first)."
                % (self.name, self._fix_uncollected_policy()["dispose_after"])
            )
        if not self.env.user.has_group(GROUP_BRANCH_MANAGER):
            raise UserError(
                "Disposing of the uncollected device of order %s needs a branch manager's "
                "approval (DOFA Tier 2)." % self.name
            )

    @api.model
    def _fix_uncollected_policy(self) -> dict:
        """D13: the ONE uncollected-device schedule: the reminder days after
        Ready (the last is the formal notice) and the disposal day."""
        params = self.env["ir.config_parameter"].sudo()
        raw = params.get_param(UNCOLLECTED_REMINDER_DAYS_PARAM, UNCOLLECTED_REMINDER_DAYS_DEFAULT)
        days = []
        for part in str(raw or "").split(","):
            try:
                value = int(part.strip())
            except ValueError:
                continue
            if value > 0:
                days.append(value)
        days = sorted(set(days)) or [3, 7, 15, 30]
        try:
            dispose = int(params.get_param(ABANDON_AFTER_DAYS_PARAM, ABANDON_AFTER_DAYS_DEFAULT))
        except (TypeError, ValueError):
            dispose = int(ABANDON_AFTER_DAYS_DEFAULT)
        return {"reminders": days, "notice": days[-1], "dispose_after": dispose}

    @api.model
    def _fix_policy_warranty_days(self) -> int:
        """M01-12 (O6): the repair warranty period of the company's policy."""
        raw = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(REPAIR_WARRANTY_DAYS_PARAM, REPAIR_WARRANTY_DAYS_DEFAULT)
        )
        try:
            return max(int(raw), 0)
        except (TypeError, ValueError):
            return REPAIR_WARRANTY_DAYS_DEFAULT

    def _fix_cancel_downstream(self, reason_code, note) -> None:
        """Cancel what still runs for this order (M01-12, A02 ho_06/can_02):
        the customer could still approve its estimate, and a technician was
        still dispatched on its field order."""
        self.ensure_one()
        label = "Order %s cancelled (%s)" % (self.name, reason_code)
        open_estimates = self.estimate_ids.filtered(lambda e: e.state in ("draft", "sent"))
        if open_estimates:
            open_estimates._guarded().write({"state": "rejected"})
            for est in open_estimates:
                est.message_post(body="%s: estimate withdrawn." % label)
        # The cascade is the order's own system transition: the downstream
        # records are found and cancelled with the order, whoever may see them.
        if "field_order_ids" in self._fields:
            live = self.sudo().field_order_ids.filtered(
                lambda f: f.state not in ("completed", "cancelled", "declined")
            )
            for field_order in live:
                field_order.action_cancel(reason="%s%s" % (label, ": %s" % note if note else ""))
        if "workshop_job_ids" in self._fields:
            # A job already confirmed beyond economic repair (M31 BER) has
            # left the bench; cancelling the order does not touch it (S2).
            live = self.sudo().workshop_job_ids.filtered(
                lambda j: j.state not in ("delivered", "cancelled", "unrepairable")
            )
            for job in live:
                if job.state in ("burn_in", "qc_pending", "ready"):
                    raise UserError(
                        "Order %s cannot be cancelled while workshop job %s is %s: "
                        "finish or fail the bench work first." % (self.name, job.name, job.state)
                    )
                job.action_cancel()
        self._fix_cancel_work_orders(label, reason_code)
        self._fix_cancel_consignments(label, note)

    # A02 ERP audit M01-F11: why an M15 issue of a cancelled order goes back.
    _PART_RETURN_REASON = {
        "customer_declined": "customer_refusal",
        "estimate_declined": "customer_refusal",
        "unrepairable": "wrong_diagnosis",
    }

    def _fix_cancel_work_orders(self, label, reason_code) -> None:
        """A02 ERP audit M01-F11: the technicians' work orders were left live
        on a cancelled order (still on their queue, still able to draw van
        stock). Each unfinished one is cancelled, and the parts M15 issued to
        it go back to the location they came from (M15's own return). A part
        issued to a COMPLETED work order is fitted in the device: it is
        reported on the order for the store to decide, not returned blindly."""
        self.ensure_one()
        work_orders = self.sudo().work_order_ids
        live = work_orders.filtered(lambda w: w.state not in ("completed", "failed", "cancelled"))
        if live:
            live._guarded().write({"state": "cancelled", "end_time": fields.Datetime.now()})
        returned, kept, stuck = [], [], []
        why = self._PART_RETURN_REASON.get(reason_code, "excess_draw")
        for line in work_orders.mapped("parts_consumed_ids"):
            issue = line.m15_consumption_id if "m15_consumption_id" in line._fields else None
            if not issue or issue.state != "consumed":
                continue
            if line.work_order_id.state == "completed":
                kept.append(issue.name)
                continue
            try:
                with self.env.cr.savepoint():
                    issue.action_return_part(reason=why, notes=label)
                returned.append(issue.name)
            except (UserError, ValidationError) as exc:
                stuck.append("%s (%s)" % (issue.name, exc))
        notes = []
        if live:
            notes.append("work order(s) %s cancelled" % ", ".join(live.mapped("name")))
        if returned:
            notes.append("parts returned to stock: %s" % ", ".join(returned))
        if kept:
            notes.append(
                "parts fitted on completed work: %s - return them through M15 if removed"
                % ", ".join(kept)
            )
        if stuck:
            notes.append("parts NOT returned (return them in M15): %s" % "; ".join(stuck))
        if notes:
            self.message_post(body="%s: %s." % (label, "; ".join(notes)))

    def _fix_cancel_consignments(self, label, note) -> None:
        """A02 audit M01-P2: a cancelled order left its pick&drop legs live,
        so a rider still collected or delivered for it. Each live leg leaves
        through cd_consignment's own method: its cancel if it has one, else
        Return (a confirmed, in-transit or held leg goes back to origin with
        the reason). A draft leg has no exit there; it is reported on the
        order rather than written to."""
        self.ensure_one()
        if "consignment_ids" not in self._fields:
            return
        reason = "%s%s" % (label, ": %s" % note if note else "")
        stuck = []
        for leg in self.sudo().consignment_ids:
            if leg.state not in ("draft", "confirmed", "in_transit", "held"):
                continue
            cancel = getattr(leg, "action_cancel", None)
            if cancel is not None:
                cancel(reason=reason)
            elif leg.state != "draft":
                leg.action_return(reason=reason)
            else:
                stuck.append(leg.name or str(leg.id))
        if stuck:
            self.message_post(
                body="Draft logistics leg(s) %s were never confirmed; nothing was "
                "dispatched for them, but they remain on the order." % ", ".join(stuck)
            )

    def _fix_assert_no_live_handoff(self, downstream, label) -> None:
        """A6 / M01-13: one live downstream record per order. Repeat presses
        created duplicates (30 orders with 2 workshop jobs on fix_dev)."""
        self.ensure_one()
        if downstream:
            raise UserError(
                "Order %s already has a live %s (%s). Cancel or finish it before "
                "handing the order over again."
                % (self.name, label, ", ".join(downstream.mapped("display_name")))
            )

    # --- the zero-charge approvals (M01-1, A3; routed through M63, A02 B1) ---
    def action_request_goodwill(self, reason=None):
        """Ask a Service Commercial Approver for a goodwill (zero-charge)
        repair. The request is routed to the approver's M63 inbox; the
        approver's decision runs action_approve_goodwill."""
        if not (reason or "").strip():
            raise UserError("Give the reason for the goodwill repair.")
        for order in self:
            if order.state in ("delivered", "closed", "cancelled"):
                raise UserError("Order %s is %s." % (order.name, order.state))
            self.env["fix.so.approval"]._fix_open("goodwill", order, reason.strip())
        return True

    def action_request_rework_approval(self, reason=None):
        """Ask a commercial approver to confirm a detected rework is free."""
        if not (reason or "").strip():
            raise UserError("Give the reason the rework is free of charge.")
        for order in self:
            if not order.is_rework:
                raise UserError(
                    "Order %s is not a detected rework (same device and fault category "
                    "within 30 days)." % order.name
                )
            self.env["fix.so.approval"]._fix_open("rework", order, reason.strip())
        return True

    def _fix_assert_commercial_approver(self, what: str) -> None:
        self.ensure_one()
        Approval = self.env["fix.so.approval"]
        # A delegate decides on the absent approver's authority (M63).
        authority = Approval._fix_authority_user()
        if not (self.env.su or authority.has_group(GROUP_COMMERCIAL_APPROVER)):
            raise UserError(
                "%s needs a Service Commercial Approver. No one may approve their own "
                "zero-charge job; ask an appointed approver." % what
            )
        if self.create_uid in Approval._fix_acting_users() and not self.env.su:
            raise UserError(
                "Segregation of duties: the person who raised order %s cannot approve "
                "its %s." % (self.name, what.lower())
            )

    def action_approve_goodwill(self, reason=None):
        """FR-SRM-075: a goodwill (zero-charge) repair, approved and pinned
        to the amount it waives."""
        if not (reason or "").strip():
            raise UserError("Give the reason for the goodwill repair.")
        for order in self:
            # A02 audit B1: decided from the approver's M63 inbox only.
            self.env["fix.so.approval"]._fix_assert_routed(order, "goodwill")
            if order.state in ("delivered", "closed", "cancelled"):
                raise UserError("Order %s is %s." % (order.name, order.state))
            order._fix_assert_commercial_approver("Goodwill")
            order._guarded().write(
                {
                    "is_goodwill": True,
                    "goodwill_approved_by": self.env.user.id,
                    "goodwill_approved_at": fields.Datetime.now(),
                    "goodwill_reason": reason.strip(),
                    "goodwill_cost_attribution_bdt": order._fix_amount_due(),
                }
            )
            order.message_post(
                body="Goodwill approved by %s: %s" % (self.env.user.name, reason.strip())
            )
        return True

    def action_approve_rework(self, reason=None):
        """BRU-SRM-06: a rework flagged by the system (same device AND fault
        category within 30 days) is free only once an approver confirms it."""
        if not (reason or "").strip():
            raise UserError("Give the reason the rework is free of charge.")
        for order in self:
            self.env["fix.so.approval"]._fix_assert_routed(order, "rework")
            if not order.is_rework:
                raise UserError(
                    "Order %s is not a detected rework (same device and fault category "
                    "within 30 days)." % order.name
                )
            order._fix_assert_commercial_approver("Zero-charge rework")
            order._guarded().write(
                {
                    "rework_approved_by": self.env.user.id,
                    "rework_approved_at": fields.Datetime.now(),
                    "rework_reason": reason.strip(),
                    # M01-F2: the confirmation covers this amount, no more
                    "rework_approved_amount_bdt": order._fix_amount_due(),
                }
            )
            order.message_post(
                body="Zero-charge rework confirmed by %s: %s" % (self.env.user.name, reason.strip())
            )
        return True

    def action_change_category(self, category=None, reason=None):
        """Re-classify an order before the customer has approved a price.
        Re-runs the warranty gate (M01-1: a post-create switch to warranty
        skipped both gates)."""
        valid = dict(self._fields["order_category"]._description_selection(self.env))
        if category not in valid:
            raise UserError("Unknown order category: %s." % category)
        if not (reason or "").strip():
            raise UserError("Give the reason for the re-classification.")
        for order in self:
            if order.state not in ("draft", "intake", "diagnostic", "estimate_pending"):
                raise UserError(
                    "Order %s is %s: its category can no longer change. Cancel and "
                    "re-raise it instead." % (order.name, order.state)
                )
            old = order.order_category
            order._guarded().write({"order_category": category})
            order.message_post(
                body="Category changed %s -> %s by %s: %s"
                % (old, category, self.env.user.name, reason.strip())
            )
        return True

    def action_override_priority(self, priority=None, reason=None):
        """FR-SRM-080: a priority override is logged with its reason and the
        user (19 non-normal priorities on fix_dev had no reason)."""
        valid = dict(self._fields["priority"]._description_selection(self.env))
        if priority not in valid:
            raise UserError("Unknown priority: %s." % priority)
        if not (reason or "").strip():
            raise UserError("Give the justification for the priority override.")
        # A02 ERP audit M01-F19 / FR-SRM-080: "authorised roles" - any user
        # re-prioritised any order. A priority moves the SLA promise, so it is
        # the Service Supervisor's call, as a hold is.
        self._fix_assert_supervisor("Overriding an order's priority")
        for order in self:
            if order.state in ("delivered", "closed", "cancelled"):
                raise UserError("Order %s is %s." % (order.name, order.state))
            order._guarded().write(
                {
                    "priority": priority,
                    "priority_override_reason": reason.strip(),
                    "priority_override_user_id": self.env.user.id,
                }
            )
            # ... and the SLA follows the new priority (it kept the old clock)
            if order.state not in _SLA_FINISHED_STATES and order.state != "draft":
                order._fix_reselect_sla(reason.strip())
        return True

    def _fix_apply_loyalty_priority(self) -> None:
        """BRU-SRM-10 (C): a member whose M10 tier is marked Priority
        Diagnostics gets the priority-1 SLA automatically, whatever the
        service type (the rule was a comment on fix.sla.policy). Read through
        the registry: cd_loyalty depends on this module. The level is
        LOYALTY_PRIORITY_PARAM; a priority already higher is kept."""
        Account = self.env.get("fix.loyalty.account")
        if Account is None or "priority_diagnostic" not in self.env["fix.loyalty.tier"]._fields:
            return
        level = (
            self.env["ir.config_parameter"].sudo().get_param(LOYALTY_PRIORITY_PARAM, "urgent") or ""
        ).strip()
        if level not in _PRIORITY_RANK:
            return
        for order in self:
            if _PRIORITY_RANK.get(order.priority, 0) >= _PRIORITY_RANK[level]:
                continue
            partner = order.customer_id.commercial_partner_id or order.customer_id
            account = Account.sudo().search(
                [
                    ("partner_id", "in", (partner | order.customer_id).ids),
                    ("state", "=", "active"),
                    ("tier_id.priority_diagnostic", "=", True),
                ],
                limit=1,
            )
            if not account:
                continue
            order._guarded().write({"priority": level})
            order.message_post(
                body="BRU-SRM-10: priority set to %s for %s member %s."
                % (level, account.tier_id.display_name, account.name)
            )

    # --- delivery handover OTP (A5, M01-10) ---
    def action_send_delivery_otp(self):
        """Send a one-time code to the customer's phone. The staff member
        never sees it; the collector reads it back from the customer's phone."""
        for order in self:
            if order.state != "ready":
                raise UserError("The handover code is sent when order %s is Ready." % order.name)
            phone = fix_otp_util.bd_mobile(order.customer_id)
            if not phone:
                raise UserError(
                    "Customer %s has no valid Bangladesh mobile number for the handover "
                    "code." % order.customer_id.display_name
                )
            code = fix_otp_util.issue_code()
            fix_otp_util.dispatch_otp(phone, code, fix_otp_util.OTP_TTL_SECONDS)
            now = fields.Datetime.now()
            order.sudo().write(
                {
                    "delivery_otp_digest": fix_otp_util.digest(
                        self.env, "so_delivery", order.id, code
                    ),
                    "delivery_otp_sent_at": now,
                    "delivery_otp_expires_at": now
                    + timedelta(seconds=fix_otp_util.OTP_TTL_SECONDS),
                    "delivery_otp_attempts": 0,
                    "delivery_otp_verified": False,
                }
            )
            order.message_post(
                body="Handover code sent to the customer's phone %s." % fix_otp_util.mask(phone)
            )
        return True

    def action_verify_delivery_otp(self, otp=None, code=None):
        """Read back the handover code. A wrong code is COUNTED and returned
        as not verified rather than raised: a raise would roll the counter
        back, and an unlimited number of guesses defeats a 6-digit code. Five
        misses burn the code."""
        code = (otp or code or "").strip()
        result = {"verified": True}
        for order in self:
            if order.state != "ready":
                raise UserError("Order %s is not Ready for handover." % order.name)
            stored = order.sudo().delivery_otp_digest
            if not stored or not order.delivery_otp_expires_at:
                raise UserError("Send the handover code to the customer first.")
            if fields.Datetime.now() > order.delivery_otp_expires_at:
                raise UserError("The handover code has expired. Send a new one.")
            if not fix_otp_util.matches(self.env, "so_delivery", order.id, code, stored):
                attempts = order.delivery_otp_attempts + 1
                burnt = attempts >= fix_otp_util.OTP_MAX_ATTEMPTS
                order.sudo().write(
                    {
                        "delivery_otp_attempts": attempts,
                        "delivery_otp_digest": False if burnt else stored,
                    }
                )
                order.message_post(
                    body="Wrong handover code entered by %s (attempt %d)%s."
                    % (self.env.user.name, attempts, "; the code is burnt" if burnt else "")
                )
                result = {
                    "verified": False,
                    "error": "That handover code is not correct."
                    + (" Too many attempts: send a new code." if burnt else ""),
                }
                continue
            order.sudo().write(
                {
                    "delivery_otp_digest": False,
                    "delivery_otp_verified": True,
                    "delivery_otp_verified_at": fields.Datetime.now(),
                    "delivery_otp_verified_by": self.env.user.id,
                }
            )
            order.message_post(body="Handover code verified by %s." % self.env.user.name)
        return result

    def action_issue_repair_warranty(self):
        """M01 Quality & Release: issue OUR repair-service warranty. Allowed
        once the repair is proven done (delivered/closed); one issuance per
        order, evidenced on the device history."""
        for order in self:
            if order.state not in ("delivered", "closed"):
                raise UserError(
                    "Repair warranty can only be issued after delivery "
                    "(current state: %s)." % order.state
                )
            if order.service_warranty_until:
                raise UserError(
                    "Repair warranty for %s was already issued (valid until %s)."
                    % (order.name, order.service_warranty_until)
                )
            order._fix_issue_repair_warranty()

    def _fix_auto_issue_repair_warranty(self) -> None:
        """A02 ERP audit M01-F21 (FR-SRM-020/045): the warranty was issued
        only when someone pressed Issue Repair Warranty, and a comeback was
        refused on every order nobody pressed it for. It is issued at the
        handover now, from the order's warranty days (default 30; the period
        by device category / repair level is spec question Q-03, OWNER)."""
        for order in self.filtered(lambda o: not o.service_warranty_until):
            if (order.service_warranty_days or 0) <= 0:
                continue
            order._fix_issue_repair_warranty()

    def _fix_issue_repair_warranty(self) -> None:
        """Issue the repair warranty from the handover day (Dhaka)."""
        for order in self:
            days = order.service_warranty_days or 30
            # A04 ERP round 2 M37-F5 (FR-CAT-018): the catalogue service's own
            # repair warranty, where it is longer than the company policy
            item = order.sudo().catalog_item_id
            if item and hasattr(item, "_fix_repair_warranty_days"):
                days = item._fix_repair_warranty_days(days)
            # the warranty runs from the handover; the resolution (Ready) day
            # is only the fallback of a legacy order with no delivery stamp
            base = _dhaka_date(order.delivered_at or order.sla_resolution_at)
            vals = {
                "service_warranty_until": base + timedelta(days=days),
                "service_warranty_issued_by": order.env.user.id,
            }
            if days != order.service_warranty_days:
                vals["service_warranty_days"] = days
            order._guarded().write(vals)
            order.device_id.add_history(
                "warranty",
                "Repair warranty issued with order %s: %d days" % (order.name, days),
                order_id=order.id,
            )
            order.message_post(
                body="Repair warranty issued: %d days (valid until %s)."
                % (days, order.service_warranty_until)
            )
            publish(
                self.env,
                "service_order.warranty_issued",
                "fix.service.order",
                order.id,
                order._fix_event_payload(),
            )

    # --- W2 Business-Line Actions ---
    def action_swap_device(self, replacement_device_id, reason="unrepairable", grade="grade_a"):
        """FR-SRM-064: Convert an irreparable fault or SLA risk into an asset swap."""
        self.ensure_one()
        replacement = self.env["fix.device"].browse(replacement_device_id)
        if not replacement.exists():
            raise UserError("Selected replacement swap device does not exist.")
        self.write(
            {
                "is_swap_out": True,
                "swap_device_id": replacement.id,
                "swap_reason": reason,
                "swap_condition_grade": grade,
                "swap_logistics_status": "dispatched",
            }
        )
        self.message_post(
            body=f"FR-SRM-064: Asset swap triggered. Replacement device {replacement.name} "
            f"assigned with reason '{reason}' and condition '{grade}'."
        )
        publish(
            self.env,
            "service_order.device_swapped",
            "fix.service.order",
            self.id,
            self._fix_event_payload(),
        )

    def _fix_assert_supervisor(self, what: str) -> None:
        """A02 audit B3: a hold stops the customer's SLA clock, so it is a
        supervisor's decision, not any user's."""
        if self.env.su or self.env.user.has_group(GROUP_SUPERVISOR):
            return
        raise UserError("%s needs a Service Supervisor." % what)

    def action_defer_order(self, reason="parts_backorder", resume_date=None, notes=None):
        """Put the order on a deferred hold (awaiting parts, customer away,
        dispute, OEM): the SLA clock pauses while it lasts."""
        self.ensure_one()
        self._fix_assert_supervisor("Placing an order on a deferred hold")
        valid = dict(self._fields["deferred_reason"]._description_selection(self.env))
        if reason not in valid:
            raise UserError("Unknown hold reason: %s (expected %s)." % (reason, ", ".join(valid)))
        if self.state in _SLA_FINISHED_STATES:
            raise UserError("Order %s is %s; it cannot be put on hold." % (self.name, self.state))
        self._guarded().write(
            {
                "is_deferred_block": True,
                "deferred_reason": reason,
                "deferred_until": resume_date,
                "deferred_notes": notes,
            }
        )
        # A02 audit sla_02: the hold set no pause time, so it was never timed.
        self._fix_sync_sla_pause()
        self.message_post(
            body="Deferred repair hold by %s: %s. Resumption target: %s."
            % (self.env.user.name, valid[reason], resume_date or "Indefinite")
        )
        publish(
            self.env,
            "service_order.deferred",
            "fix.service.order",
            self.id,
            self._fix_event_payload(),
        )

    def action_resume_order(self):
        """Lift the deferred hold; the SLA clock runs again unless another
        hold (customer decision, pickup) still applies."""
        self.ensure_one()
        self._fix_assert_supervisor("Lifting a deferred hold")
        if not self.is_deferred_block:
            raise UserError("Order %s is not on a deferred hold." % self.name)
        self._guarded().write({"is_deferred_block": False})
        self._fix_sync_sla_pause()
        self.message_post(
            body="Deferred repair hold lifted by %s - order processing resumed."
            % self.env.user.name
        )
        publish(
            self.env,
            "service_order.resumed",
            "fix.service.order",
            self.id,
            self._fix_event_payload(),
        )

    @api.model
    def _cron_resume_deferred(self):
        """A02 ERP audit M01-F18 / BRU-SRM-15 ("resumes automatically on
        release"): deferred_until was read by nothing, so a hold never ended
        and its SLA clock stayed paused for ever. A hold whose resumption
        date has come (Dhaka business day) is lifted, as the system."""
        today = _dhaka_date()
        due = self.sudo().search(
            [
                ("is_deferred_block", "=", True),
                ("deferred_until", "!=", False),
                ("deferred_until", "<=", today),
                ("state", "not in", _SLA_FINISHED_STATES),
            ]
        )
        resumed = 0
        for order in due:
            try:
                with self.env.cr.savepoint():
                    order._fix_lift_hold(
                        "Deferred hold lifted automatically: its resumption date %s has come."
                        % order.deferred_until
                    )
                    resumed += 1
            except Exception:
                logger.exception("Deferred hold of %s not lifted", order.name)
        return resumed

    def _fix_lift_hold(self, message) -> None:
        """Lift the deferred hold as the system (cron, parts arrival)."""
        for order in self.sudo():
            if not order.is_deferred_block:
                continue
            order._guarded().write({"is_deferred_block": False})
            order._fix_sync_sla_pause()
            order.message_post(body=message)
            publish(
                self.env,
                "service_order.resumed",
                "fix.service.order",
                order.id,
                order._fix_event_payload(),
            )

    # --- the customer's unlock code (A02 ERP audit M01-F8, BRU-SRM-20) ---
    def action_record_passcode(self, passcode=None, consent=None):
        """Record the customer's unlock code for diagnosis and QC, only with
        the customer's explicit consent. Any desk user records it; only the
        roles in PASSCODE_READERS read it back, and it is purged at handover.

        No fix.consent purpose covers device data access (M33 lists service
        updates, marketing, research, collections, profiling, call recording):
        the consent is recorded on the order (who, when) - OWNER: add a
        purpose to the M33 consent register if it must live there."""
        code = (passcode or "").strip()
        if not code:
            raise UserError("Enter the unlock code the customer gave.")
        if str(consent or "").strip().lower() not in ("1", "true", "yes", "y"):
            raise UserError(
                "BRU-SRM-20: the unlock code is captured only with the customer's explicit "
                "consent. Ask the customer, and answer 'yes' to record it."
            )
        for order in self:
            if order.state in ("delivered", "closed", "cancelled"):
                raise UserError(
                    "Order %s is %s: an unlock code is no longer needed."
                    % (order.name, order.state)
                )
            order.sudo()._guarded().write(
                {
                    "passcode_value": code,
                    "passcode_consent_at": fields.Datetime.now(),
                    "passcode_consent_by": self.env.user.id,
                    "passcode_purged_at": False,
                }
            )
            order.message_post(
                body="Customer unlock code recorded with the customer's consent by %s (not "
                "shown; purged at handover)." % self.env.user.name
            )
        return True

    def _fix_purge_passcode(self) -> None:
        for order in self.sudo().filtered("passcode_value"):
            order._guarded().write(
                {"passcode_value": False, "passcode_purged_at": fields.Datetime.now()}
            )
            order.message_post(body="Customer unlock code purged at %s (BRU-SRM-20)." % order.state)

    # --- Idempotency (T08, DI-04) ---
    @api.model_create_multi
    def create(self, vals_list):
        # A02 audit M01-3: refuse a late state at birth (an order was created
        # 'closed', or 'ready' with no QC). Superuser code (imports, data
        # loads, migrations) is trusted, as by the field guard.
        if not self.env.su:
            for vals in vals_list:
                if vals.get("state", "draft") not in _BIRTH_STATES:
                    raise UserError(
                        "A service order starts as Draft or Intake; '%s' is reached only "
                        "through the order's workflow actions." % vals.get("state")
                    )
        # DI-04: a vals whose idempotency key already exists yields the existing
        # order instead of a new one. Per vals, in input order: the old body
        # RETURNED on the first replayed key, silently dropping every other vals
        # of the batch.
        # A03 audit W5 (M33-3): the draft-party switch. A no-op under the
        # default 'allow' (cd_party_master.draft_party_policy).
        Partner = self.env["res.partner"]
        if hasattr(Partner, "_fix_assert_party_usable_downstream"):
            Partner.browse(
                {vals["customer_id"] for vals in vals_list if vals.get("customer_id")}
            )._fix_assert_party_usable_downstream("a service order")
        result_ids = []  # existing order id, or None for "created below"
        to_create = []
        for vals in vals_list:
            key = vals.get("idempotency_key")
            existing = key and self.search([("idempotency_key", "=", key)], limit=1)
            if existing:
                result_ids.append(existing.id)
                continue
            if not key:
                vals["idempotency_key"] = str(uuid.uuid4())
            if not vals.get("name"):
                # The old field default fell back to the literal "NEW" when the
                # sequence was missing: 825 orders in fix_dev shared that
                # reference. A missing sequence must stop the create instead.
                ref = self.env["ir.sequence"].next_by_code("fix.service.order")
                if not ref:
                    raise UserError(
                        "The 'fix.service.order' sequence is missing — cannot assign "
                        "a service order reference."
                    )
                vals["name"] = ref
            result_ids.append(None)
            to_create.append(vals)
        records = super(FixServiceOrder, self.with_context(**{_BIRTH_KEY: _BIRTH_TOKEN})).create(
            to_create
        )
        records = records.with_context(**{_BIRTH_KEY: False})
        for rec in records:
            rec._fix_bind_evidence(_ORDER_EVIDENCE_FIELDS)
            rec._check_warranty_gate()
            rec._flag_rework()
            # BRU-SRM-10, before the clock starts so it runs on the new priority
            rec._fix_apply_loyalty_priority()
            if rec.state == "intake":
                rec._guarded().write({"intake_completed_at": fields.Datetime.now()})
                rec._fix_start_sla()
                if rec.technician_id:
                    rec._fix_mark_response()
            publish(
                self.env,
                "service_order.created",
                "fix.service.order",
                rec.id,
                rec._fix_event_payload(),
            )
        created = iter(records.ids)
        return self.browse([rid or next(created) for rid in result_ids])

    def _check_warranty_gate(self):
        """BRU-SRM-02 / WTY-01 (H): a warranty-type order can only be
        created while the device's warranty is ACTIVE at the request date,
        decided by the device (fix.device.is_under_warranty).

        The gate used to compare fix.device.warranty_status with "active", a
        value that field never takes ("in_warranty", "out_of_warranty",
        "extended", "unknown"): EVERY warranty order was refused - from the P01
        customer booking and the P04 corporate request alike (R01 re-audit
        2026-10-22).

        It runs at create AND on every re-classification (A02 audit M01-1)."""
        request_date = fields.Date.context_today(self)
        require_verified = _param_on(self.env, WARRANTY_VERIFIED_PARAM, "0")
        for order in self:
            if order.order_category != "warranty":
                if order.warranty_cover_unverified:
                    order._guarded().write({"warranty_cover_unverified": False})
                continue
            device = order.device_id
            if not device.is_under_warranty(request_date, require_verified=require_verified):
                raise UserError(
                    "BRU-SRM-02: device %s has no active warranty on %s (warranty status "
                    "'%s') — a warranty order needs an ACTIVE warranty at the request date"
                    % (device.display_name, request_date, device.warranty_status or "unknown")
                )
            # The gate above honours cover that NOBODY HAS VERIFIED. That is
            # deliberate (withdrawing live cover is a commercial call), but it
            # must not be silent: record it on the order so the exposure is
            # filterable and attributable instead of invisible.
            unverified = device.unverified_warranty_cover(request_date)
            order._guarded().write({"warranty_cover_unverified": bool(unverified)})
            if unverified:
                order.message_post(
                    body=(
                        "Warranty order accepted on UNVERIFIED cover: no purchase "
                        "proof has been checked for warranty %s on %s. Raised by %s. "
                        "Verify the proof (Warranty → Verify) or void the cover."
                    )
                    % (
                        ", ".join(unverified.mapped("display_name")) or "(unnamed)",
                        device.display_name,
                        self.env.user.name,
                    )
                )

    def _fix_publish_rework(self, original, basis) -> None:
        """A02 pass 2 (M01-14): rework.detected was documented and never
        published, so the quality loop (M23 CAPA, the technician's rework KPI)
        never heard of a rework. One literal publish per detection."""
        self.ensure_one()
        publish(
            self.env,
            "rework.detected",
            "fix.service.order",
            self.id,
            {
                "service_order_id": self.id,
                "name": self.name,
                "original_order_id": original.id,
                "original_name": original.sudo().name,
                "device_id": self.device_id.id,
                "customer_id": self.customer_id.id,
                "branch_id": self.branch_id.id,
                "original_technician_id": original.sudo().technician_id.id or False,
                "basis": basis,
            },
        )

    def _fix_fault_categories(self) -> set:
        """The fault categories this order is about: its coded fault lines'
        categories, plus its catalogue service item."""
        self.ensure_one()
        codes = [c for c in self.fault_line_ids.mapped("fault_code") if c]
        cats = set()
        if codes:
            cats = set(
                self.env["fix.fault.code"]
                .sudo()
                .with_context(active_test=False)
                .search([("code", "in", codes)])
                .mapped("category")
            )
        if self.catalog_item_id:
            cats.add("catalogue:%d" % self.catalog_item_id.id)
        return cats

    def _flag_rework(self):
        """BRU-SRM-06 (C): a new order for the same device with the same
        fault within 30 days is auto-flagged as rework and linked.

        Same device AND same fault category (A02 audit M01-1: the device alone
        flagged 413 of 930 orders, an unrelated cracked screen included). An
        order with no coded fault yet is checked again when diagnosis ends.

        A02 ERP audit M01-F21: the 30 days counted from the earlier order's
        CREATION (a repair that took three weeks left a one-week window) and
        a draft or a still-open order counted as the "original". The window
        runs from the handover of a delivered (or closed) repair."""
        cutoff = fields.Datetime.now() - timedelta(days=30)
        for order in self:
            if order.is_rework:
                continue
            categories = order._fix_fault_categories()
            if not categories:
                continue
            # A02 pass 2 (M01-10): searched with the user's record rules, a
            # repair delivered at another branch (operating unit) was invisible,
            # so a comeback there was never flagged. The detection is the
            # system's, fenced to the order's company.
            candidates = self.sudo().search(
                [
                    ("device_id", "=", order.device_id.id),
                    ("company_id", "=", order.company_id.id),
                    ("id", "!=", order.id),
                    ("state", "in", ("delivered", "closed")),
                    "|",
                    ("delivered_at", ">=", cutoff),
                    "&",
                    ("delivered_at", "=", False),
                    ("closed_at", ">=", cutoff),
                ],
                order="delivered_at desc, id desc",
            )
            original = next((c for c in candidates if c._fix_fault_categories() & categories), None)
            if original:
                order._guarded().write({"is_rework": True, "rework_of_id": original.id})
                order._fix_publish_rework(original, "same_fault_30_days")
                order.message_post(
                    body=(
                        "BRU-SRM-06: flagged as rework — device returned within 30 "
                        "days with the same fault (linked to %s). It is charged unless "
                        "a commercial approver confirms the rework." % original.name
                    )
                )
