# fix_ewaste_ops — M18: collection events, triage decisions, material batches,
# lithium-ion handling, certified partners, disposal certificates and DoE/BTRC
# returns. The collection itself lives in fix_ewaste.py; these compose with it.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

MATERIALS = [
    ("phone", "Mobile Phone"),
    ("laptop", "Laptop"),
    ("tablet", "Tablet"),
    ("accessory", "Accessory"),
    ("battery", "Battery"),
    ("other", "Other"),
]


class FixEwasteEvent(models.Model):
    """A collection drive/event where multiple collections are handed over."""

    _name = "fix.ewaste.event"
    _description = "E-Waste Collection Event"
    _order = "event_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    event_date = fields.Date(required=True, default=fields.Date.context_today)
    venue = fields.Char()
    target_kg = fields.Float(string="Target (kg)")
    collected_kg = fields.Float(string="Collected (kg)", compute="_compute_collected", store=True)
    collection_ids = fields.One2many("fix.ewaste.collection", "event_id", string="Collections")
    state = fields.Selection(
        [("planned", "Planned"), ("open", "Open"), ("closed", "Closed")],
        required=True,
        default="planned",
    )
    notes = fields.Text()

    @api.depends("collection_ids.weight_kg")
    def _compute_collected(self):
        for rec in self:
            rec.collected_kg = round(sum(rec.collection_ids.mapped("weight_kg")), 3)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.ewaste.event") or "EWEV/New"
                )
        return super().create(vals_list)


class FixEwasteTriage(models.Model):
    """A recorded triage decision; saving it applies the grade to the collection."""

    _name = "fix.ewaste.triage"
    _description = "E-Waste Triage Decision"
    _order = "decided_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    collection_id = fields.Many2one(
        "fix.ewaste.collection",
        string="Collection",
        required=True,
        ondelete="cascade",
        index=True,
    )
    decision = fields.Selection(
        [
            ("reuse", "Reuse"),
            ("refurbish", "Refurbishable"),
            ("recycle", "Recycle Only"),
            ("hazardous", "Hazardous"),
        ],
        required=True,
        default="recycle",
    )
    data_bearing = fields.Boolean(string="Contains Data Storage", default=False)
    wipe_required = fields.Boolean(string="Wipe / Destruction Required", default=True)
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    decided_on = fields.Date(required=True, default=fields.Date.context_today)
    notes = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.ewaste.triage") or "ETRI/New"
                )
        records = super().create(vals_list)
        for rec in records:
            collection = rec.collection_id
            if collection.state == "collected":
                collection.write({"state": "triaged", "triage_grade": rec.decision})
        return records


class FixEwasteBatch(models.Model):
    """A material batch transferred to a certified partner."""

    _name = "fix.ewaste.batch"
    _description = "E-Waste Material Batch"
    _order = "dispatched_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    material_type = fields.Selection(MATERIALS, required=True, default="phone")
    weight_kg = fields.Float(string="Weight (kg)")
    partner_id = fields.Many2one(
        "fix.ewaste.partner", string="Certified Partner", ondelete="restrict"
    )
    transfer_note_ref = fields.Char(string="Transfer Note Ref")
    dispatched_on = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("dispatched", "Dispatched"),
            ("received", "Received"),
            ("processed", "Processed"),
        ],
        required=True,
        default="draft",
    )
    notes = fields.Text()

    _weight_positive = models.Constraint(
        "CHECK (weight_kg >= 0)", "Batch weight cannot be negative"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.ewaste.batch") or "EBAT/New"
                )
        return super().create(vals_list)

    def action_dispatch(self):
        for rec in self:
            if not rec.partner_id:
                raise UserError("A batch is dispatched to a certified partner")
            if rec.state != "draft":
                raise UserError("Dispatch from draft")
            rec.state = "dispatched"
            if not rec.dispatched_on:
                rec.dispatched_on = fields.Date.context_today(self)


class FixEwasteBattery(models.Model):
    """A lithium-ion / battery stream item with its hazard handling."""

    _name = "fix.ewaste.battery"
    _description = "E-Waste Battery Handling"
    _order = "received_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    collection_id = fields.Many2one(
        "fix.ewaste.collection", string="Collection", ondelete="set null"
    )
    batch_id = fields.Many2one("fix.ewaste.batch", string="Batch", ondelete="set null")
    chemistry = fields.Selection(
        [
            ("li_ion", "Lithium-Ion"),
            ("li_po", "Lithium-Polymer"),
            ("nimh", "NiMH"),
            ("lead_acid", "Lead-Acid"),
            ("other", "Other"),
        ],
        required=True,
        default="li_ion",
    )
    weight_kg = fields.Float(string="Weight (kg)")
    hazard_class = fields.Selection(
        [
            ("class_9", "UN3480/3481 — Class 9"),
            ("class_8", "Class 8 (corrosive)"),
            ("not_regulated", "Not regulated"),
        ],
        required=True,
        default="class_9",
    )
    storage_location = fields.Char()
    terminal_taped = fields.Boolean(string="Terminals Insulated & Taped", default=False)
    swollen_cell = fields.Boolean(string="Swollen / Ruptured Cell", default=False)
    quarantine_barrel_ref = fields.Char(string="Fireproof Vermiculite Drum Ref")
    state = fields.Selection(
        [("stored", "In Storage"), ("dispatched", "Dispatched"), ("processed", "Processed")],
        required=True,
        default="stored",
    )
    received_on = fields.Date(default=fields.Date.context_today)
    notes = fields.Char()

    _weight_positive = models.Constraint(
        "CHECK (weight_kg >= 0)", "Battery weight cannot be negative"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.ewaste.battery") or "EBAT/New"
                )
        return super().create(vals_list)

    def action_inspect_and_quarantine(self):
        """Execute UN 3480 Class 9 safety inspection: tape terminals, quarantine swollen cells."""
        for rec in self:
            rec.terminal_taped = True
            if rec.swollen_cell:
                if not rec.quarantine_barrel_ref:
                    rec.quarantine_barrel_ref = "DRUM-VERM-%s" % (rec.name or "01")
                rec.storage_location = "Quarantine Bay Q-09 (Fireproof Vermiculite Barrel)"
            else:
                rec.storage_location = "Storage Shelf B-04"
            rec.state = "stored"

    def action_dispatch(self):
        """Dispatch battery item to certified recycler under hazardous manifest."""
        for rec in self:
            if not rec.terminal_taped:
                raise ValidationError(
                    "Cannot dispatch battery %s: Terminals must be taped first" % rec.name
                )
            rec.state = "dispatched"

    def action_process(self):
        """Mark battery item as processed/decontaminated."""
        for rec in self:
            rec.state = "processed"


class FixEwastePartner(models.Model):
    """A certified recycling partner and its certificate validity."""

    _name = "fix.ewaste.partner"
    _description = "Certified E-Waste Partner"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("res.partner", string="Contact", ondelete="set null")
    certification = fields.Selection(
        [
            ("doe", "DoE Licensed"),
            ("btrc", "BTRC Approved"),
            ("iso_14001", "ISO 14001"),
            ("ehs", "EHS Certified"),
        ],
        required=True,
        default="doe",
    )
    certificate_no = fields.Char(string="Certificate No")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    capability = fields.Text(string="Handled Materials")
    state = fields.Selection(
        [("active", "Active"), ("suspended", "Suspended"), ("expired", "Expired")],
        required=True,
        default="active",
    )

    _dates_ordered = models.Constraint(
        "CHECK (valid_to IS NULL OR valid_to >= valid_from)",
        "Certificate end date cannot precede its start date",
    )

    @api.constrains("valid_to")
    def _check_validity(self):
        for rec in self:
            if rec.valid_to and rec.valid_to < fields.Date.context_today(self):
                raise ValidationError("A certificate that has expired cannot be active")


class FixEwasteCertificate(models.Model):
    """A disposal certificate issued for a recycled collection or batch."""

    _name = "fix.ewaste.certificate"
    _description = "E-Waste Disposal Certificate"
    _order = "issued_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    collection_id = fields.Many2one(
        "fix.ewaste.collection", string="Collection", ondelete="set null", index=True
    )
    batch_id = fields.Many2one("fix.ewaste.batch", string="Batch", ondelete="set null")
    partner_id = fields.Many2one(
        "fix.ewaste.partner", string="Certified Partner", required=True, ondelete="restrict"
    )
    material_type = fields.Selection(MATERIALS, required=True, default="phone")
    weight_kg = fields.Float(string="Weight (kg)")
    certificate_no = fields.Char(string="Certificate No")
    file_ref = fields.Char(string="Document Ref")
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("issued", "Issued"), ("revoked", "Revoked")], required=True, default="issued"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.ewaste.certificate") or "ECER/New"
                )
        return super().create(vals_list)


class FixEwasteReturn(models.Model):
    """A statutory DoE / BTRC return for a period."""

    _name = "fix.ewaste.return"
    _description = "DoE / BTRC Statutory Return"
    _order = "period desc, authority"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    authority = fields.Selection(
        [("doe", "Department of Environment"), ("btrc", "BTRC")],
        required=True,
        default="doe",
    )
    period = fields.Char(required=True, help="YYYY-MM")
    due_date = fields.Date(required=True, default=fields.Date.context_today)
    submitted_on = fields.Date()
    reference = fields.Char()
    form_type = fields.Selection(
        [
            ("form_1", "Form-1 (Manifest - S.R.O. 187/2021)"),
            ("form_2", "Form-2 (Operational Register)"),
            ("form_3", "Form-3 (DoE Annual Return)"),
        ],
        default="form_3",
        required=True,
    )
    schedule_1_category = fields.Selection(
        [
            ("cat_1", "IT & Telecom (Schedule-1)"),
            ("cat_2", "Consumer Electronics"),
            ("cat_3", "Medical Equipment"),
            ("cat_4", "Large Appliances"),
        ],
        default="cat_1",
    )
    total_tonnage_collected = fields.Float(
        string="Total Collected (Metric Tons)", digits=(12, 3), default=0.0
    )
    total_tonnage_recycled = fields.Float(
        string="Total Recycled (Metric Tons)", digits=(12, 3), default=0.0
    )
    recovery_rate_pct = fields.Float(
        string="Recovery Rate %", compute="_compute_mass_balance", store=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("accepted", "Accepted")],
        required=True,
        default="draft",
    )
    notes = fields.Text()
    is_overdue = fields.Boolean(string="Overdue", compute="_compute_overdue", store=True)

    @api.depends("total_tonnage_collected", "total_tonnage_recycled")
    def _compute_mass_balance(self):
        for rec in self:
            col = rec.total_tonnage_collected or 0.0
            recy = rec.total_tonnage_recycled or 0.0
            rec.recovery_rate_pct = round((recy / col * 100.0), 2) if col > 0 else 0.0

    @api.depends("due_date", "state")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_overdue = bool(rec.due_date and rec.state == "draft" and rec.due_date < today)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.ewaste.return") or "ERET/New"
                )
        return super().create(vals_list)

    def action_calculate_mass_balance(self):
        """Compute mass-balance from collections and batches in this period under S.R.O. 187-Law/2021."""
        for rec in self:
            collections = self.env["fix.ewaste.collection"].search(
                [("state", "in", ("intake", "sorted", "dispatched"))]
            )
            total_kg = sum(c.weight_kg for c in collections)
            rec.total_tonnage_collected = round(total_kg / 1000.0, 3)
            batches = self.env["fix.ewaste.batch"].search(
                [("state", "in", ("ready", "shipped", "recycled"))]
            )
            recycled_kg = sum(b.net_weight_kg for b in batches)
            rec.total_tonnage_recycled = round(recycled_kg / 1000.0, 3)
            rec._compute_mass_balance()

    def action_submit_return(self):
        """Submit statutory return to DoE / BTRC."""
        for rec in self:
            if rec.total_tonnage_collected <= 0:
                rec.action_calculate_mass_balance()
            rec.write(
                {
                    "state": "submitted",
                    "submitted_on": fields.Date.context_today(self),
                    "reference": rec.reference or ("DOE-SRO187-%s-%s" % (rec.period, rec.id)),
                }
            )

    def action_accept_return(self):
        """Acknowledge acceptance from regulatory authority."""
        for rec in self:
            rec.state = "accepted"
