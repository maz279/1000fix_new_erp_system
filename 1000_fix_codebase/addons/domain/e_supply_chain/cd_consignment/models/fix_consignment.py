# cd_consignment — M03 Logistics & Reverse Logistics core (P06-M07, CD-M03-01/02).
#
# G3-05: pick & drop operating with an UNBROKEN CHAIN OF CUSTODY. A
# consignment moves through custody scan events; the chain is verified, not
# assumed — a gap in the chain is a hard error, never a warning.
#
# A02 audit (2026-11-03) M03-1/2/3/7: the state, the seal verdict and the POD
# stamps were plain writable fields, a skipped step passed as "unbroken", and
# a scan's time, serial and scanner could be rewritten after delivery. The
# lifecycle fields are now guarded (fix.guarded.mixin), the chain checks the
# REQUIRED steps of each leg type, scans are append-only and server-stamped,
# and delivered / lost / returned are terminal and frozen.
import itertools

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

# The custody chain, in order. A handover skips forward only with a named
# exception reason (e.g. customer absent -> returned to branch).
CUSTODY_STEPS = [
    ("picked_up", "Picked Up"),
    ("in_transit", "In Transit"),
    ("hub_scan", "Hub Scan"),
    ("out_for_delivery", "Out for Delivery"),
    ("delivered", "Delivered"),
    ("returned", "Returned"),
]
STEP_ORDER = [s[0] for s in CUSTODY_STEPS]

# A02 audit M03-2: the steps each leg type must record, in order. A leg that
# ends at a customer or vendor goes out for delivery and closes with the
# recipient's POD code; a leg that ends at one of our branches closes with a
# hub intake (seal and weight) and the receiving hub's receipt. A hub scan on
# a customer leg is optional (a branch-to-door run passes no hub). Skipping a
# required step needs a named exception on the next scan.
REQUIRED_STEPS = {
    "delivery": ("picked_up", "in_transit", "out_for_delivery", "delivered"),
    "return_to_vendor": ("picked_up", "in_transit", "out_for_delivery", "delivered"),
    "pickup": ("picked_up", "in_transit", "hub_scan", "delivered"),
    "branch_transfer": ("picked_up", "in_transit", "hub_scan", "delivered"),
}
# Legs whose recipient is outside the company: closed by the recipient's OTP.
POD_OTP_TYPES = ("delivery", "return_to_vendor")
# Legs that end at one of our branches: closed by the receiving hub.
RECEIPT_TYPES = ("pickup", "branch_transfer")

# A02 audit M03-7: these states end the consignment. Nothing moves out of
# them and the record no longer changes.
FROZEN_STATES = ("delivered", "lost", "returned")
# Dispatch evidence that the hub verifies against, and the leg type that
# decides the required chain: fixed once the consignment leaves the draft
# and confirmed states, so they cannot be edited to match what arrived.
TRANSIT_LOCKED = frozenset(
    {
        "consignment_type",
        "outbound_seal_number",
        "security_bag_barcode",
        "dispatch_weight_g",
        "declared_value_bdt",
        "service_order_id",
        "purchase_order_id",
        "origin_branch_id",
        "dest_branch_id",
    }
)

GROUP_RIDER = "cd_consignment.group_fix_logistics_rider"
GROUP_HUB = "cd_consignment.group_fix_logistics_hub"
GROUP_MANAGER = "cd_consignment.group_fix_logistics_manager"
GROUP_LABELS = {
    GROUP_RIDER: "Logistics Rider",
    GROUP_HUB: "Logistics Hub Operator",
    GROUP_MANAGER: "Logistics Manager",
}


def _scan_key(scan):
    # Ties (one transition stamps several scans in the same second) keep the
    # creation order; an unsaved scan in a form sorts by time alone.
    ident = scan.id if isinstance(scan.id, int) else 0
    return (scan.scanned_at or fields.Datetime.now(), ident)


def find_chain_problem(consignment_type, scans):
    """Why a chain of scans (already in time order) is broken, or None.

    A02 audit M03-2: the former check was monotonic order only, so
    picked_up -> delivered with three steps skipped read as unbroken. A
    chain is broken when a scan goes backwards, or when a required step of
    the leg type is skipped without a named exception on the next scan. A
    'returned' scan may follow any step: it is the exception path itself.
    """
    required = REQUIRED_STEPS.get(consignment_type, REQUIRED_STEPS["delivery"])
    labels = dict(CUSTODY_STEPS)
    for prev, cur in itertools.pairwise(scans):
        if prev.step not in STEP_ORDER or cur.step not in STEP_ORDER:
            continue
        a, b = STEP_ORDER.index(prev.step), STEP_ORDER.index(cur.step)
        if b <= a:
            return "%s is recorded after %s (out of order)." % (labels[cur.step], labels[prev.step])
        if cur.step == "returned" or cur.exception_reason:
            continue
        skipped = [s for s in required if a < STEP_ORDER.index(s) < b]
        if skipped:
            return "%s was skipped between %s and %s with no named exception." % (
                ", ".join(labels[s] for s in skipped),
                labels[prev.step],
                labels[cur.step],
            )
    return None


class FixConsignment(models.Model):
    """A logistics consignment (device to workshop, part to branch, device
    back to customer). Carries a custody chain that must never break."""

    _name = "fix.consignment"
    _description = "Consignment"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "scheduled_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    # M03 capture audit 2026-11-12: required with no default, and no form
    # showed it, so a consignment raised in the workspace could never save.
    operating_unit_id = fields.Many2one(
        "operating.unit",
        required=True,
        index=True,
        default=lambda self: self.env.user.default_operating_unit_id,
    )
    name = fields.Char(string="Consignment No.", readonly=True, index=True, copy=False)
    consignment_type = fields.Selection(
        [
            ("pickup", "Pickup (customer -> branch)"),
            ("delivery", "Delivery (branch -> customer)"),
            ("branch_transfer", "Branch Transfer"),
            ("return_to_vendor", "Return to Vendor"),
        ],
        required=True,
        default="pickup",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("in_transit", "In Transit"),
            # A02 audit M03-8: a seal or weight mismatch at hub intake holds
            # the consignment here; only a logistics manager releases it.
            ("held", "Exception Hold"),
            ("delivered", "Delivered"),
            ("returned", "Returned"),
            ("lost", "Lost"),
        ],
        default="draft",
        required=True,
        tracking=True,
        readonly=True,
        copy=False,
    )
    scheduled_date = fields.Datetime(required=True)
    origin_branch_id = fields.Many2one("fix.branch", string="Origin")
    dest_branch_id = fields.Many2one("fix.branch", string="Destination")
    rider_id = fields.Many2one("hr.employee", string="Rider", index=True)
    service_order_id = fields.Many2one("fix.service.order", string="Service Order", index=True)
    purchase_order_id = fields.Many2one("fix.purchase.order", string="Purchase Order", index=True)
    custody_ids = fields.One2many("fix.custody.scan", "consignment_id", string="Custody Chain")
    chain_broken = fields.Boolean(compute="_compute_chain", store=True, string="Chain Broken")
    custody_summary = fields.Char(compute="_compute_chain", store=True)
    chain_problem = fields.Char(
        compute="_compute_chain", store=True, string="Chain Problem", readonly=True
    )
    # A02 audit M03-13: the delivery moment, stamped by the transition (the
    # KPIs read write_date, which any later edit moved).
    delivered_at = fields.Datetime(string="Delivered At", readonly=True, copy=False)
    # A02 audit M03-8: the exception hold and its release, as evidence.
    hold_reason = fields.Char(string="Hold Reason", readonly=True, copy=False)
    hold_released_by_id = fields.Many2one(
        "res.users", string="Hold Released By", readonly=True, copy=False
    )
    hold_released_at = fields.Datetime(string="Hold Released At", readonly=True, copy=False)
    hold_release_reason = fields.Char(string="Hold Release Reason", readonly=True, copy=False)
    exception_note = fields.Char(
        string="Return / Loss Reason",
        readonly=True,
        copy=False,
        help="The named reason recorded by the return or lost transition.",
    )

    # --- A02 Enterprise Data Capture, Volumetric Weight & Tamper-Evident Security Seal (FLAW-03.2, FLAW-03.3) ---
    courier_partner_id = fields.Many2one(
        "fix.courier.partner",
        string="3PL Courier Partner",
        tracking=True,
    )
    vehicle_registration = fields.Char(
        string="Dispatch Vehicle / Bike Reg No.",
        tracking=True,
    )
    declared_value_bdt = fields.Float(
        string="Declared Insured Asset Value (BDT)",
        default=0.0,
        tracking=True,
    )
    packaging_type = fields.Selection(
        [
            ("esd_antistatic_box", "ESD Anti-Static Shielded Box"),
            ("pelican_hard_case", "Shockproof Pelican / Flight Case"),
            ("bubble_carton", "Double-Wall Bubble Carton"),
            ("tamper_polybag", "Serialized Tamper-Evident Security Pouch"),
        ],
        string="Protective Packaging Specification",
        default="esd_antistatic_box",
        tracking=True,
    )
    rto_flag = fields.Boolean(
        string="Return-to-Origin (RTO) Triggered",
        default=False,
        tracking=True,
    )
    # FLAW-03.2: Volumetric Weight & Freight Surcharge
    length_cm = fields.Float(string="Carton Length (cm)", default=0.0)
    width_cm = fields.Float(string="Carton Width (cm)", default=0.0)
    height_cm = fields.Float(string="Carton Height (cm)", default=0.0)
    actual_weight_kg = fields.Float(string="Actual Scale Weight (kg)", default=0.0)
    volumetric_divisor = fields.Float(
        string="Volumetric Divisor (cm³/kg)",
        default=5000.0,
        help="FLAW-03.2: Standard volumetric divisor (L x W x H / 5000).",
    )
    volumetric_weight_kg = fields.Float(
        string="Volumetric Weight (kg)",
        compute="_compute_volumetric_and_seal",
        store=True,
    )
    chargeable_weight_kg = fields.Float(
        string="Chargeable Weight (kg)",
        compute="_compute_volumetric_and_seal",
        store=True,
    )
    base_freight_bdt = fields.Float(
        string="Base Freight Charge (BDT)",
        compute="_compute_volumetric_and_seal",
        store=True,
    )
    volumetric_surcharge_bdt = fields.Float(
        string="Volumetric Weight Surcharge (BDT)",
        compute="_compute_volumetric_and_seal",
        store=True,
    )
    insurance_fee_bdt = fields.Float(
        string="Transit Insurance Fee (BDT)",
        compute="_compute_volumetric_and_seal",
        store=True,
    )
    # FLAW-03.3: Tamper-Evident Security Bag & Hub Weight Variance
    security_bag_barcode = fields.Char(
        string="Tamper-Evident Security Bag Barcode",
        tracking=True,
    )
    outbound_seal_number = fields.Char(
        string="Outbound Security Seal Number",
        tracking=True,
        help="FLAW-03.3: Serialized tamper-evident seal affixed at origin dispatch.",
    )
    inbound_seal_number = fields.Char(
        string="Inbound Hub Verified Seal Number",
        tracking=True,
        readonly=True,
        help="FLAW-03.3: Seal number scanned upon arrival at destination hub/branch. "
        "Recorded by the hub intake action only.",
    )
    seal_status = fields.Selection(
        [
            ("intact", "Sealed / Pending Hub Verification"),
            ("verified", "Seal Verified Match"),
            ("tampered_mismatch", "TAMPER ALERT — Seal Mismatch / Broken"),
        ],
        string="Security Seal Integrity Status",
        default="intact",
        tracking=True,
        readonly=True,
    )
    dispatch_weight_g = fields.Float(
        string="Origin Dispatch Scale Weight (g)",
        default=0.0,
        tracking=True,
    )
    receive_weight_g = fields.Float(
        string="Hub Receive Scale Weight (g)",
        default=0.0,
        tracking=True,
        readonly=True,
    )
    weight_variance_g = fields.Float(
        string="Scale Weight Variance (g)",
        compute="_compute_volumetric_and_seal",
        store=True,
        help="FLAW-03.3: Absolute difference between origin dispatch weight and hub receive weight (tolerance ±20g).",
    )
    shockwatch_triggered = fields.Boolean(
        string="ShockWatch / Tilt Indicator Tripped",
        default=False,
        tracking=True,
    )
    recipient_name = fields.Char(string="Verified Recipient Name")
    recipient_nid_last4 = fields.Char(string="Recipient NID / Phone Last 4 Digits")
    waybill_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Signed Consignment Waybill / Manifest (PDF)",
    )

    # ------------------------------------------------------------ the guard
    def _fix_guarded_fields(self) -> set:
        # A02 audit M03-1: the lifecycle, the hub verdict and the delivery
        # evidence change only through the transitions below. The computed
        # chain and freight figures are listed too, since a stored compute
        # without an inverse still accepts a write() until its next recompute.
        return super()._fix_guarded_fields() | {
            "state",
            "seal_status",
            "inbound_seal_number",
            "receive_weight_g",
            # pod_otp_hash is not listed: only system administrators can even
            # read it (groups=), and write() below refuses it outright.
            "pod_otp_issued_at",
            "pod_otp_channel",
            "pod_verified_at",
            "pod_verified_by",
            "delivered_at",
            "hold_reason",
            "hold_released_by_id",
            "hold_released_at",
            "hold_release_reason",
            "exception_note",
            # set by Return to Origin only (it was never set at all before)
            "rto_flag",
            "chain_broken",
            "chain_problem",
            "custody_summary",
            "volumetric_weight_kg",
            "chargeable_weight_kg",
            "base_freight_bdt",
            "volumetric_surcharge_bdt",
            "insurance_fee_bdt",
            "weight_variance_g",
        }

    def _fix_frozen_fields(self) -> set:
        """Every stored field a user could edit, for a record in a final state."""
        return {
            name
            for name, field in self._fields.items()
            if field.store
            and not name.startswith(("message_", "activity_"))
            and name not in models.MAGIC_COLUMNS
            and name not in ("id", "display_name")
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if not rec:
            return locked
        if rec.state in FROZEN_STATES:
            return locked | rec._fix_frozen_fields()
        if rec.state not in ("draft", "confirmed"):
            locked |= TRANSIT_LOCKED
        if rec.state != "draft":
            locked |= {"consignment_type"}
        return locked

    def write(self, vals):
        """A02 audit M03-7: a delivered, lost or returned consignment is a
        closed record; dispatch evidence is fixed once the consignment moves.
        Writing the value a field already has is allowed (the P03 form posts
        every field it shows)."""
        if self and not self._fix_guard_open():
            if "pod_otp_hash" in vals:
                # A02 audit M03-4: the POD code is issued to the recipient by
                # action_generate_otp, never typed onto the record.
                raise UserError(
                    "The POD code is issued to the recipient by Send POD Code; it cannot "
                    "be set on the record."
                )
            for rec in self:
                if rec.state in FROZEN_STATES:
                    names = rec._fix_frozen_fields() & set(vals)
                    reason = "it is %s and its record is closed" % rec.state
                elif rec.state not in ("draft", "confirmed"):
                    names = TRANSIT_LOCKED & set(vals)
                    reason = "it has left dispatch (%s)" % rec.state
                elif rec.state != "draft":
                    names = {"consignment_type"} & set(vals)
                    reason = "it is confirmed"
                else:
                    names = set()
                changed = [n for n in names if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed:
                    labels = ", ".join(sorted(rec._fields[n].string or n for n in changed))
                    raise UserError(
                        "%s cannot be changed on %s: %s (A02 audit M03-7)."
                        % (labels, rec.name, reason)
                    )
        return super().write(vals)

    # ------------------------------------------------------------ roles
    def _logistics_require(self, *groups, what="This step"):
        """Raise unless the acting user holds one of the logistics roles."""
        if self.env.su or any(self.env.user.has_group(g) for g in groups):
            return
        raise UserError(
            "%s needs the %s role. Ask a logistics manager to assign it."
            % (what, " or ".join(GROUP_LABELS.get(g, g) for g in groups))
        )

    def _is_logistics_manager(self) -> bool:
        return self.env.su or self.env.user.has_group(GROUP_MANAGER)

    # ------------------------------------------------------------ computes
    @api.depends(
        "length_cm",
        "width_cm",
        "height_cm",
        "actual_weight_kg",
        "volumetric_divisor",
        "courier_partner_id.base_rate",
        "courier_partner_id.per_kg_rate",
        "declared_value_bdt",
        "dispatch_weight_g",
        "receive_weight_g",
    )
    def _compute_volumetric_and_seal(self):
        for rec in self:
            divisor = rec.volumetric_divisor or 5000.0
            vol_kg = 0.0
            if rec.length_cm > 0 and rec.width_cm > 0 and rec.height_cm > 0:
                vol_kg = round((rec.length_cm * rec.width_cm * rec.height_cm) / divisor, 3)
            actual_kg = rec.actual_weight_kg or 0.0
            chargeable_kg = round(max(actual_kg, vol_kg), 3)
            rec.volumetric_weight_kg = vol_kg
            rec.chargeable_weight_kg = chargeable_kg

            base_rate = rec.courier_partner_id.base_rate if rec.courier_partner_id else 80.0
            per_kg = rec.courier_partner_id.per_kg_rate if rec.courier_partner_id else 40.0
            rec.base_freight_bdt = round(base_rate + actual_kg * per_kg, 2)
            excess_vol_kg = max(0.0, vol_kg - actual_kg)
            rec.volumetric_surcharge_bdt = round(excess_vol_kg * per_kg, 2)
            rec.insurance_fee_bdt = round((rec.declared_value_bdt or 0.0) * 0.01, 2)

            if rec.dispatch_weight_g > 0 and rec.receive_weight_g > 0:
                rec.weight_variance_g = round(abs(rec.receive_weight_g - rec.dispatch_weight_g), 2)
            else:
                rec.weight_variance_g = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.consignment") or (
                    "CSG/%s" % fields.Date.today()
                )
            if not vals.get("operating_unit_id"):
                ou = self._derive_operating_unit(vals)
                if ou:
                    vals["operating_unit_id"] = ou.id
        return super().create(vals_list)

    def _derive_operating_unit(self, vals):
        """The unit a consignment raised without one belongs to: its service
        order's, else its origin or destination branch's (the M01 hand-over
        rule), else the creator's default (a user with none gets the
        required-field message)."""
        order = self.env["fix.service.order"].browse(vals.get("service_order_id") or [])
        if order.operating_unit_id:
            return order.operating_unit_id
        for key in ("origin_branch_id", "dest_branch_id"):
            branch = self.env["fix.branch"].browse(vals.get(key) or [])
            if branch.operating_unit_id:
                return branch.operating_unit_id
        return self.env.user.default_operating_unit_id

    def _custody_chain(self):
        """The scans in time order (ties by creation order)."""
        self.ensure_one()
        return self.custody_ids.sorted(key=_scan_key)

    def _custody_chain_problem(self):
        """Why the chain is broken right now, or None. Gates call this rather
        than trust the stored flag (a stored copy of a gate's own input goes
        stale when the rules change)."""
        self.ensure_one()
        return find_chain_problem(self.consignment_type, self._custody_chain())

    @api.depends(
        "consignment_type",
        "custody_ids.step",
        "custody_ids.scanned_at",
        "custody_ids.exception_reason",
    )
    def _compute_chain(self):
        """The unbroken-chain check (G3-05): scans in the canonical order with
        every required step of the leg type present or explained by a named
        exception (A02 audit M03-2)."""
        labels = dict(CUSTODY_STEPS)
        for consignment in self:
            scans = consignment._custody_chain()
            problem = find_chain_problem(consignment.consignment_type, scans)
            consignment.chain_broken = bool(problem)
            consignment.chain_problem = problem or False
            consignment.custody_summary = (
                " -> ".join(labels[s.step] for s in scans if s.step in labels) or "no scans"
            )

    # ------------------------------------------------------------ transitions
    def action_confirm(self):
        """Confirm the leg for dispatch. Only drafts confirm (the old body
        accepted any state, so a delivered consignment could be 're-confirmed')."""
        self._logistics_require(GROUP_HUB, what="Confirming a consignment")
        for consignment in self:
            if consignment.state != "draft":
                raise UserError(
                    "Only draft consignments can be confirmed (current: %s)." % consignment.state
                )
            # BRU-LOG-12 (class H): the declared value is recorded before the
            # item leaves - it caps a damage payout and prices the insurance.
            # M03 bidirectional audit 2026-11-13: nothing enforced it.
            if consignment.declared_value_bdt <= 0:
                raise UserError(
                    "%s has no declared value. Record what the consignment is worth "
                    "(Seal for Dispatch or the consignment form) before confirming it "
                    "for dispatch (BRU-LOG-12)." % consignment.name
                )
            consignment._guarded().write({"state": "confirmed"})
        return True

    def action_report_lost(self, reason=None):
        """A lost consignment raises an incident — never silently drops.
        Lost is terminal (A02 audit M03-7): nothing delivers it afterwards."""
        self._logistics_require(GROUP_HUB, what="Reporting a consignment lost")
        for consignment in self:
            if consignment.state in FROZEN_STATES:
                raise UserError(
                    "%s is already %s — it cannot be reported lost."
                    % (consignment.name, consignment.state)
                )
            vals = {"state": "lost"}
            if reason and str(reason).strip():
                vals["exception_note"] = str(reason).strip()
            consignment._guarded().write(vals)
            publish(
                self.env,
                "consignment.lost",
                "fix.consignment",
                consignment.id,
                {"consignment": consignment.name},
            )
        return True

    def action_deliver(self):
        """Deliver the consignment (Gate G3-05).

        A02 audit M03-4/7: delivery needs a consignment in transit, a POD
        verified by the recipient's code or the receiving hub, and an
        unbroken chain that ends with the 'delivered' scan. The POD stamps
        are guarded, so only action_verify_pod and action_confirm_receipt can
        satisfy this; a 'delivered' scan alone no longer delivers anything."""
        for consignment in self:
            if consignment.state != "in_transit":
                raise UserError(
                    "Only a consignment in transit can be delivered (%s is %s)."
                    % (consignment.name, consignment.state)
                )
            if not consignment.pod_verified_at:
                raise UserError(
                    "Cannot deliver consignment %s: no verified proof of delivery. Close it "
                    "with the recipient's POD code, or with the receiving hub's receipt."
                    % consignment.name
                )
            problem = consignment._custody_chain_problem()
            if problem:
                raise UserError(
                    "Cannot deliver consignment: custody chain is broken (Gate G3-05). %s" % problem
                )
            last_scan = consignment._custody_chain()[-1:]
            if not last_scan or last_scan.step != "delivered":
                raise UserError(
                    "Cannot deliver consignment: terminal 'delivered' custody scan missing."
                )
            now = fields.Datetime.now()
            consignment._guarded().write({"state": "delivered", "delivered_at": now})
            # A02 audit B2: the M01 consumer (cd_service_order) moves the order
            # from this; service_order_id is the contract agreed with it.
            publish(
                self.env,
                "consignment.delivered",
                "fix.consignment",
                consignment.id,
                {
                    "consignment": consignment.name,
                    "consignment_type": consignment.consignment_type,
                    "service_order_id": consignment.service_order_id.id or None,
                    "delivered_at": fields.Datetime.to_string(now),
                },
            )
        return True

    def action_return(self, reason=None):
        """Reverse logistics: the leg goes back to origin with a named reason.

        A02 audit M03-7: only a consignment still on its way (confirmed, in
        transit or on exception hold) can be returned; a delivered one is
        closed, and reversing it needs a new return leg."""
        self._logistics_require(GROUP_HUB, what="Returning a consignment")
        reason = (str(reason).strip() if reason else "") or False
        if not reason:
            raise UserError("Give the reason for the return (customer absent, refused, …).")
        Scan = self.env["fix.custody.scan"]
        for consignment in self:
            if consignment.state not in ("confirmed", "in_transit", "held"):
                raise UserError(
                    "Only a consignment that is confirmed, in transit or on hold can be "
                    "returned (%s is %s)." % (consignment.name, consignment.state)
                )
            if consignment.custody_ids:
                Scan._guarded().create(
                    {
                        "consignment_id": consignment.id,
                        "step": "returned",
                        "exception_reason": reason,
                        "device_serial": consignment.service_order_id.device_serial or "",
                    }
                )
            consignment._guarded().write(
                {"state": "returned", "exception_note": reason, "rto_flag": True}
            )
            publish(
                self.env,
                "consignment.returned",
                "fix.consignment",
                consignment.id,
                {
                    "consignment": consignment.name,
                    "returned_at": fields.Datetime.to_string(fields.Datetime.now()),
                },
            )
        return True


class FixCustodyScan(models.Model):
    """One custody scan event — the chain's links. Scanned by the P09 rider
    app or the branch front desk; every scan is terminal-attributed.

    A02 audit M03-3: a scan is evidence. It is append-only (no field changes
    after create), and who scanned it and when are stamped by the server from
    the session and the clock, never taken from the caller."""

    _name = "fix.custody.scan"
    _description = "Custody Scan"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "scanned_at, id"

    consignment_id = fields.Many2one(
        "fix.consignment", required=True, ondelete="cascade", index=True
    )
    step = fields.Selection(
        CUSTODY_STEPS, required=True, help="The canonical custody step this scan records"
    )
    scanned_at = fields.Datetime(default=fields.Datetime.now, required=True, readonly=True)
    scanned_by = fields.Many2one("hr.employee", string="Scanned By", readonly=True)
    scanned_by_user_id = fields.Many2one(
        "res.users", string="Scanned By (User)", readonly=True, index=True
    )
    location_branch_id = fields.Many2one("fix.branch", string="Location")
    exception_reason = fields.Char(
        help="Required when a step is skipped (named exception, never silent)"
    )
    device_serial = fields.Char(
        string="Device Serial", help="What is in custody — verified at every scan"
    )

    _SCAN_FIELDS = frozenset(
        {
            "consignment_id",
            "step",
            "scanned_at",
            "scanned_by",
            "scanned_by_user_id",
            "location_branch_id",
            "exception_reason",
            "device_serial",
        }
    )
    _SERVER_STAMPS = ("scanned_at", "scanned_by", "scanned_by_user_id")

    def _fix_guarded_fields(self) -> set:
        # Append-only: once a scan exists none of its fields changes.
        return super()._fix_guarded_fields() | set(self._SCAN_FIELDS)

    @api.model_create_multi
    def create(self, vals_list):
        """Record a scan. The server stamps the scanner and the time; the
        caller supplies the step, the location and the serial. 'Delivered'
        and 'returned' are written only by their transitions (POD, receipt,
        return), and a closed or held consignment takes no further scans."""
        trusted = self._fix_guard_open()
        user = self.env.user
        now = fields.Datetime.now()
        Consignment = self.env["fix.consignment"]
        for vals in vals_list:
            if not self.env.su:
                supplied = [k for k in self._SERVER_STAMPS if vals.get(k)]
                if supplied:
                    raise UserError(
                        "A custody scan is stamped by the server with who scanned it and "
                        "when. %s cannot be supplied (A02 audit M03-3)."
                        % ", ".join(self._fields[k].string for k in supplied)
                    )
                consignment = Consignment.browse(vals.get("consignment_id"))
                step = vals.get("step")
                if step in ("delivered", "returned") and not trusted:
                    raise UserError(
                        "A '%s' scan is recorded by its transition (POD verification, hub "
                        "receipt or return), not entered directly." % step
                    )
                state = consignment.state
                if state in FROZEN_STATES or (state == "held" and step != "returned"):
                    raise UserError(
                        "%s is %s; its custody chain takes no further scans."
                        % (consignment.name, state)
                    )
                if state == "draft":
                    raise UserError(
                        "%s is still a draft; confirm it before scanning custody."
                        % consignment.name
                    )
            if self.env.su:
                vals.setdefault("scanned_at", now)
                vals.setdefault("scanned_by_user_id", user.id)
                vals.setdefault("scanned_by", user.employee_id.id or False)
            else:
                vals["scanned_at"] = now
                vals["scanned_by_user_id"] = user.id
                vals["scanned_by"] = user.employee_id.id or False
        # The checks above are the control; the guard's create check would
        # refuse the stamps the server itself just set.
        records = super(FixCustodyScan, self._guarded()).create(vals_list)
        return records.with_env(self.env)

    @api.constrains("step", "exception_reason", "scanned_at")
    def _check_exception(self):
        """The chain's FIRST link must be a pickup unless a named exception
        explains it. (At constraint time the scan is already in its
        consignment's custody_ids, so the former `not siblings` test could
        never be true and the rule never fired.)"""
        for scan in self:
            first = scan.consignment_id._custody_chain()[:1]
            if scan == first and scan.step != "picked_up" and not scan.exception_reason:
                raise UserError("A chain that does not start at pickup needs a named exception")
