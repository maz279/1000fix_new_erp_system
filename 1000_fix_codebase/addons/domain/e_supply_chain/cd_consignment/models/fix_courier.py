# Courier partners and bookings for M03 (pick & drop via Pathao / RedX / Steadfast).
# The consignment module previously had no courier master at all, so the courier
# screens could only show a placeholder.
#
# A02 audit (2026-11-03) M03-1/10: a booking was marked delivered with no POD
# and its state was a plain writable field. The state and the POD evidence are
# now guarded, and delivery needs proof: the consignment's verified POD, or the
# courier's POD scan recorded by the hub.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixCourierPartner(models.Model):
    _name = "fix.courier.partner"
    _description = "Courier Partner"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    service_area = fields.Char(help="Cities / zones the partner covers.")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    base_rate = fields.Monetary(string="Base rate", currency_field="currency_id")
    per_kg_rate = fields.Monetary(string="Per-kg rate", currency_field="currency_id")
    cod_supported = fields.Boolean(default=True)
    cod_cycle_days = fields.Integer(string="COD settlement cycle (days)", default=3)
    api_ref = fields.Char(
        string="API credential reference",
        help="Vault reference for the partner API key (vault://...). Keys are never stored here.",
    )
    active = fields.Boolean(default=True)

    # --- A02 Enterprise Data Capture & Volumetric Tariff Standards (FLAW-03.2) ---
    volumetric_divisor = fields.Float(
        string="Volumetric Divisor (cm³/kg)",
        default=5000.0,
        help="Standard air/courier volumetric divisor (L x W x H / 5000).",
    )
    contact_phone = fields.Char(string="Carrier Account Manager Phone")
    sla_delivery_hours = fields.Integer(
        string="Contractual Delivery SLA (Hours)",
        default=48,
    )
    insurance_max_bdt = fields.Monetary(
        string="Max Insured Transit Liability (BDT)",
        currency_field="currency_id",
        default=100000.0,
    )

    _code_unique = models.Constraint("UNIQUE (code, company_id)", "Courier code is unique")


class FixCourierBooking(models.Model):
    _name = "fix.courier.booking"
    _description = "Courier Booking"
    _inherit = ["fix.guarded.mixin"]
    _order = "booked_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("fix.courier.partner", string="Courier", required=True, index=True)
    consignment_id = fields.Many2one("fix.consignment", string="Consignment")
    awb_no = fields.Char(string="AWB / Tracking No", index=True)
    booked_on = fields.Date(required=True, default=fields.Date.context_today)
    weight_kg = fields.Float(string="Actual Scale Weight (kg)")
    length_cm = fields.Float(string="Package Length (cm)", default=0.0)
    width_cm = fields.Float(string="Package Width (cm)", default=0.0)
    height_cm = fields.Float(string="Package Height (cm)", default=0.0)
    volumetric_weight_kg = fields.Float(
        string="Volumetric Weight (kg)",
        compute="_compute_volumetric_booking",
        store=True,
    )
    chargeable_weight_kg = fields.Float(
        string="Chargeable Weight (kg)",
        compute="_compute_volumetric_booking",
        store=True,
    )
    charged_amount = fields.Monetary(currency_field="currency_id")
    cod_amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    pickup_attempts = fields.Integer(default=0)
    recipient_name = fields.Char(string="Recipient Name")
    recipient_phone = fields.Char(string="Recipient Phone")
    pod_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Signed Courier Waybill / POD Scan",
        readonly=True,
        help="Recorded by the hub with Record Courier POD.",
    )
    pod_recorded_by_id = fields.Many2one(
        "res.users", string="POD Recorded By", readonly=True, copy=False
    )
    state = fields.Selection(
        [
            ("booked", "Booked"),
            ("picked_up", "Picked Up"),
            ("delivered", "Delivered"),
            ("returned", "Returned"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="booked",
        index=True,
        readonly=True,
        copy=False,
    )
    delivered_on = fields.Date(readonly=True, copy=False)
    cod_settled_on = fields.Date(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        # A02 audit M03-1: the booking's lifecycle and its delivery evidence
        # change only through the actions below.
        return super()._fix_guarded_fields() | {
            "state",
            "delivered_on",
            "cod_settled_on",
            "pod_attachment_id",
            "pod_recorded_by_id",
            "volumetric_weight_kg",
            "chargeable_weight_kg",
        }

    @api.depends("weight_kg", "length_cm", "width_cm", "height_cm", "partner_id.volumetric_divisor")
    def _compute_volumetric_booking(self):
        for rec in self:
            divisor = (rec.partner_id.volumetric_divisor if rec.partner_id else 0.0) or 5000.0
            vol = 0.0
            if rec.length_cm > 0 and rec.width_cm > 0 and rec.height_cm > 0:
                vol = round((rec.length_cm * rec.width_cm * rec.height_cm) / divisor, 3)
            rec.volumetric_weight_kg = vol
            rec.chargeable_weight_kg = round(max(rec.weight_kg or 0.0, vol), 3)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.courier.booking") or "CBR/New"
                )
        return super().create(vals_list)

    def _courier_require_hub(self, what):
        if self.env.su or self.env.user.has_group("cd_consignment.group_fix_logistics_hub"):
            return
        raise UserError("%s needs the Logistics Hub Operator role." % what)

    def action_record_pod(self, attachment_id=None):
        """Record the courier's signed waybill / POD scan for a 3PL delivery."""
        self._courier_require_hub("Recording a courier POD")
        attachment = self.env["ir.attachment"].browse(int(attachment_id or 0)).exists()
        if not attachment:
            raise UserError("Attach the courier's signed POD scan.")
        for rec in self:
            if rec.state not in ("booked", "picked_up"):
                raise UserError("The POD is recorded before the booking is closed.")
            rec._guarded().write(
                {"pod_attachment_id": attachment.id, "pod_recorded_by_id": self.env.user.id}
            )
        return True

    def action_deliver(self):
        """Close the booking as delivered. A02 audit M03-10: it needs proof —
        the consignment's POD verified by the recipient or the receiving hub,
        or the courier's POD scan recorded by the hub."""
        self._courier_require_hub("Marking a courier booking delivered")
        for rec in self:
            if rec.state not in ("booked", "picked_up"):
                raise UserError("Only a booked or picked-up delivery can be marked delivered")
            if not (rec.consignment_id.pod_verified_at or rec.pod_attachment_id):
                raise UserError(
                    "%s has no proof of delivery: deliver its consignment with the POD "
                    "first, or record the courier's POD scan." % rec.name
                )
            rec._guarded().write(
                {"state": "delivered", "delivered_on": fields.Date.context_today(rec)}
            )
        return True
