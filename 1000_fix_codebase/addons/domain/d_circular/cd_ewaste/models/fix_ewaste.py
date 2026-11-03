# fix_ewaste — M18: e-waste, recycling, ESG (P11-M05).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

EWASTE_STATES = [
    ("collected", "Collected"),
    ("triaged", "Triaged"),
    ("destruction", "Secure Destruction"),
    ("recycled", "Recycled"),
    ("disposed", "Disposed"),
    ("certified", "Certificate Issued"),
]


class FixEwasteCollection(models.Model):
    """M18: e-waste collection (journey 10: collection -> triage ->
    destruction -> recycling -> disposal certificate)."""

    _name = "fix.ewaste.collection"
    _description = "E-Waste Collection"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    device_id = fields.Many2one("fix.device", string="Device", ondelete="set null")
    event_id = fields.Many2one(
        "fix.ewaste.event", string="Collection Event", ondelete="set null", index=True
    )
    batch_id = fields.Many2one(
        "fix.ewaste.batch", string="Material Batch", ondelete="set null", index=True
    )
    material_type = fields.Selection(
        [
            ("phone", "Mobile Phone"),
            ("laptop", "Laptop"),
            ("tablet", "Tablet"),
            ("accessory", "Accessory"),
            ("battery", "Battery"),
            ("other", "Other"),
        ],
        required=True,
        default="phone",
    )
    weight_kg = fields.Float(string="Weight (kg)")
    state = fields.Selection(EWASTE_STATES, default="collected", required=True, tracking=True)
    triage_grade = fields.Selection(
        [
            ("reuse", "Reusable"),
            ("refurbish", "Refurbishable"),
            ("recycle", "Recycle Only"),
            ("hazardous", "Hazardous"),
        ],
        string="Triage Grade",
        help="Composes M14's grading; hazardous materials route differently",
    )
    wipe_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate",
        string="Data Wipe Certificate",
        ondelete="set null",
        help="M06's secure wipe; REQUIRED before destruction",
    )
    disposal_certificate_ref = fields.Char(
        string="Disposal Certificate Ref",
        readonly=True,
        help="M24's document reference for the disposal certificate",
    )
    esg_co2_saved_kg = fields.Float(
        string="CO2 Saved (kg)", help="M18/M25: the ESG metric this collection contributes"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("fix.ewaste.collection") or "EW/New"
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "ewaste.collected",
                "fix.ewaste.collection",
                rec.id,
                {"customer": rec.customer_id.name, "type": rec.material_type},
            )
        return recs

    def action_triage(self, grade):
        for rec in self:
            if rec.state != "collected":
                raise UserError("Triage from collected state")
            rec.write({"state": "triaged", "triage_grade": grade})
            publish(self.env, "ewaste.triaged", "fix.ewaste.collection", rec.id, {"grade": grade})

    def action_secure_destruction(self):
        """Secure destruction through M06 — the wipe certificate must
        exist before destruction begins (journey 10's gate)."""
        for rec in self:
            if rec.state != "triaged":
                raise UserError("Destruction from triaged state")
            if not rec.wipe_certificate_id:
                Wipe = self.env["fix.data.wipe.certificate"]
                wipe = Wipe.create(
                    {
                        "device_id": rec.device_id.id,
                        "method": "physical_destruction",
                        # A02 audit M06-1: bound to the one item it certifies
                        "serial_number": Wipe._fix_media_serial(rec.device_id) or rec.name,
                    }
                )
                rec.write({"wipe_certificate_id": wipe.id, "state": "destruction"})
            else:
                rec.state = "destruction"
            publish(self.env, "ewaste.destruction_started", "fix.ewaste.collection", rec.id, {})

    def action_recycle(self, co2_saved):
        for rec in self:
            if rec.state != "destruction":
                raise UserError("Recycle from destruction state")
            # The destruction certificate opened above starts pending: the
            # operator's evidence must be verified in M06 before the device
            # leaves for recycling.
            # A02 audit M06-1: verified through M06, its log unchanged since,
            # and bound to this item (the device serial, else this collection)
            cert = rec.wipe_certificate_id
            denial = cert._fix_certify_denial(cert._fix_media_serial(rec.device_id) or rec.name)
            if denial:
                raise UserError(
                    "Recycle needs a verified M06 destruction certificate (%s)" % denial
                )
            rec.write({"state": "recycled", "esg_co2_saved_kg": co2_saved})

    def action_issue_certificate(self):
        """Journey 10's ending: the disposal certificate through M24."""
        for rec in self:
            if rec.state != "recycled":
                raise UserError("Certificate from recycled state")
            cert_ref = "DISPOSE/%s/%s" % (fields.Date.today().strftime("%Y%m"), rec.name)
            rec.write({"state": "certified", "disposal_certificate_ref": cert_ref})
            publish(
                self.env,
                "ewaste.certificate_issued",
                "fix.ewaste.collection",
                rec.id,
                {"certificate": cert_ref, "co2_saved": rec.esg_co2_saved_kg},
            )

    def action_triage_reuse(self):
        self.action_triage("reuse")

    def action_triage_refurbish(self):
        self.action_triage("refurbish")

    def action_triage_recycle(self):
        self.action_triage("recycle")

    def action_triage_hazardous(self):
        self.action_triage("hazardous")

    def action_recycle_estimated(self):
        """Recycle with the CO2 saving estimated at 1.5 kg CO2e per kg of
        e-waste — the documented factor, not a hidden number."""
        for rec in self:
            rec.action_recycle(round((rec.weight_kg or 0.0) * 1.5, 3))


class FixEsgMetric(models.Model):
    """M18: ESG metrics feeding M25's reporting (BM-004)."""

    _name = "fix.esg.metric"
    _description = "ESG Metric"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    metric_type = fields.Selection(
        [
            ("co2_saved", "CO2 Saved (kg)"),
            ("ewaste_collected", "E-Waste Collected (kg)"),
            ("devices_refurbished", "Devices Refurbished"),
            ("energy_saved", "Energy Saved (kWh)"),
        ],
        required=True,
        default="co2_saved",
    )
    period = fields.Char(required=True, help="YYYY-MM")
    value = fields.Float(required=True)
    # stored compute (not an onchange-only value): metrics created by the API,
    # a seed or an import must carry their unit too, not just the web form
    unit = fields.Char(compute="_compute_unit", store=True, readonly=True)

    @api.depends("metric_type")
    def _compute_unit(self):
        units = {
            "co2_saved": "kg",
            "ewaste_collected": "kg",
            "devices_refurbished": "count",
            "energy_saved": "kWh",
        }
        for rec in self:
            rec.unit = units.get(rec.metric_type, "")
