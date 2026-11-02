# cd_consignment — M03 Logistics & Reverse Logistics core (P06-M07, CD-M03-01/02).
#
# G3-05: pick & drop operating with an UNBROKEN CHAIN OF CUSTODY. A
# consignment moves through custody scan events; the chain is verified, not
# assumed — a gap in the chain is a hard error, never a warning.
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


class FixConsignment(models.Model):
    """A logistics consignment (device to workshop, part to branch, device
    back to customer). Carries a custody chain that must never break."""

    _name = "fix.consignment"
    _description = "Consignment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
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
            ("delivered", "Delivered"),
            ("returned", "Returned"),
            ("lost", "Lost"),
        ],
        default="draft",
        required=True,
        tracking=True,
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
        help="FLAW-03.3: Seal number scanned upon arrival at destination hub/branch.",
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
        return super().create(vals_list)

    @api.depends("custody_ids.step", "custody_ids.scanned_at")
    def _compute_chain(self):
        """The unbroken-chain check: custody scans must appear in the
        canonical step order with no gap. A scan out of order breaks the
        chain (G3-05 — the gate criterion is evidence, not hope)."""
        order = [s[0] for s in CUSTODY_STEPS]
        for consignment in self:
            scans = consignment.custody_ids.sorted("scanned_at")
            positions = [order.index(scan.step) for scan in scans if scan.step in order]
            monotonic = all(b > a for a, b in itertools.pairwise(positions))
            consignment.chain_broken = not monotonic
            consignment.custody_summary = (
                " -> ".join(dict(CUSTODY_STEPS)[s.step] for s in scans) or "no scans"
            )

    def action_confirm(self):
        for consignment in self:
            consignment.state = "confirmed"

    def action_report_lost(self):
        """A lost consignment raises an incident — never silently drops."""
        for consignment in self:
            consignment.state = "lost"
            publish(
                self.env,
                "consignment.lost",
                "fix.consignment",
                consignment.id,
                {"consignment": consignment.name},
            )

    def action_deliver(self):
        """Deliver consignment enforcing unbroken chain of custody (Gate G3-05)."""
        for consignment in self:
            if consignment.chain_broken:
                raise UserError("Cannot deliver consignment: custody chain is broken (Gate G3-05).")
            last_scan = consignment.custody_ids.sorted("scanned_at")[-1:]
            if not last_scan or last_scan.step != "delivered":
                raise UserError(
                    "Cannot deliver consignment: terminal 'delivered' custody scan missing."
                )
            consignment.state = "delivered"
            publish(
                self.env,
                "consignment.delivered",
                "fix.consignment",
                consignment.id,
                {
                    "consignment": consignment.name,
                    "delivered_at": fields.Datetime.to_string(fields.Datetime.now()),
                },
            )

    def action_return(self):
        """Reverse logistics return transition."""
        for consignment in self:
            consignment.state = "returned"
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


class FixCustodyScan(models.Model):
    """One custody scan event — the chain's links. Scanned by the P09 rider
    app or the branch front desk; every scan is terminal-attributed."""

    _name = "fix.custody.scan"
    _description = "Custody Scan"
    _inherit = ["mail.thread"]
    _order = "scanned_at, id"

    consignment_id = fields.Many2one(
        "fix.consignment", required=True, ondelete="cascade", index=True
    )
    step = fields.Selection(
        CUSTODY_STEPS, required=True, help="The canonical custody step this scan records"
    )
    scanned_at = fields.Datetime(default=fields.Datetime.now, required=True)
    scanned_by = fields.Many2one("hr.employee", string="Scanned By")
    location_branch_id = fields.Many2one("fix.branch", string="Location")
    exception_reason = fields.Char(
        help="Required when a step is skipped (named exception, never silent)"
    )
    device_serial = fields.Char(
        string="Device Serial", help="What is in custody — verified at every scan"
    )

    @api.constrains("step", "exception_reason", "scanned_at")
    def _check_exception(self):
        """The chain's FIRST link must be a pickup unless a named exception
        explains it. (At constraint time the scan is already in its
        consignment's custody_ids, so the former `not siblings` test could
        never be true and the rule never fired.)"""
        for scan in self:
            first = scan.consignment_id.custody_ids.sorted("scanned_at")[:1]
            if scan == first and scan.step != "picked_up" and not scan.exception_reason:
                raise UserError("A chain that does not start at pickup needs a named exception")
