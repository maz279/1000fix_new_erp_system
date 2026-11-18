# fix_ewaste_ops - M18: collection events, triage decisions, material batches,
# lithium-ion handling, certified partners, disposal certificates and DoE/BTRC
# returns. The collection itself lives in fix_ewaste.py; these compose with it.
#
# A05 workflow audit (2026-11-03): every one of these records was a free-form
# table. A clerk created an 'issued' disposal certificate, a 'processed' batch
# of 9999 kg, an active "DoE licensed" recycler, and "accepted" his own DoE
# return, which always computed 0 t. Each lifecycle is now a guarded state
# machine whose gate runs in write() for the target state, with the role and
# segregation-of-duties checks of spec §13.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from . import ewaste_common as c

MATERIALS = [
    ("phone", "Mobile Phone"),
    ("laptop", "Laptop"),
    ("tablet", "Tablet"),
    ("accessory", "Accessory"),
    ("battery", "Battery"),
    ("other", "Other"),
]


def _seq(env, code, fallback):
    return env["ir.sequence"].sudo().next_by_code(code) or fallback


class FixEwasteEvent(models.Model):
    """A collection drive/event where multiple collections are handed over."""

    _name = "fix.ewaste.event"
    _description = "E-Waste Collection Event"
    _inherit = ["fix.guarded.mixin"]
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

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"state", "collected_kg"}

    @api.depends("collection_ids.weight_kg")
    def _compute_collected(self):
        for rec in self:
            rec.collected_kg = round(sum(rec.collection_ids.mapped("weight_kg")), 3)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.ewaste.event", "EWEV/New")
        return super().create(vals_list)

    def action_open(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Only a planned drive opens.")
            rec._guarded().write({"state": "open"})

    def action_close(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open drive closes.")
            rec._guarded().write({"state": "closed"})


class FixEwasteTriage(models.Model):
    """The assessor's triage decision. Write-once (BRU-ESG-09 / T-04); saving
    it applies the grade to the collection and routes the item."""

    _name = "fix.ewaste.triage"
    _description = "E-Waste Triage Decision"
    _inherit = ["fix.guarded.mixin"]
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
            ("harvest", "Parts Harvest (M14 / M15)"),
            ("donate", "Donation"),
        ],
        required=True,
        default="recycle",
    )
    data_bearing = fields.Boolean(string="Contains Data Storage", default=False)
    wipe_required = fields.Boolean(string="Wipe / Destruction Required", default=True)
    inspector_id = fields.Many2one("hr.employee", string="Assessor")
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_on = fields.Date(required=True, default=fields.Date.context_today)
    notes = fields.Text()
    # M18 capture pass 2 (FR-ESG-006/007, BRU-ESG-09): the assessment against
    # the published criteria in force, with its evidence - all write-once
    criteria_id = fields.Many2one(
        "fix.ewaste.triage.criteria",
        string="Criteria Applied",
        readonly=True,
        ondelete="restrict",
        help="The published triage criteria in force when the decision was made.",
    )
    functional_result = fields.Selection(
        [
            ("pass", "Fully Functional"),
            ("partial", "Partly Functional"),
            ("fail", "Not Functional"),
        ],
        string="Functional Test",
    )
    cosmetic_result = fields.Selection(
        [
            ("a", "A - Like New"),
            ("b", "B - Light Wear"),
            ("c", "C - Heavy Wear"),
            ("d", "D - Broken"),
        ],
        string="Cosmetic Grade",
    )
    market_value_estimate = fields.Float(string="Market Value Estimate (BDT)")
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Assessment Evidence", readonly=True, ondelete="restrict"
    )
    evidence_file = fields.Binary(string="Upload Assessment Photo", store=False)
    evidence_filename = fields.Char(string="Evidence File Name", store=False)

    _WRITE_ONCE = frozenset(
        {
            "collection_id",
            "decision",
            "data_bearing",
            "wipe_required",
            "inspector_id",
            "decided_by_id",
            "decided_on",
            "company_id",
            "name",
            "criteria_id",
            "functional_result",
            "cosmetic_result",
            "market_value_estimate",
            "evidence_attachment_id",
            "evidence_file",
            "evidence_filename",
            "notes",
        }
    )

    def _fix_guarded_fields(self) -> set:
        # decided_on: a decision is dated the day it is made (no back-dating)
        # criteria_id is set by create() itself from the set in force (any
        # typed value is refused there) and is write-once afterwards
        return set(super()._fix_guarded_fields()) | {
            "decided_by_id",
            "decided_on",
            "evidence_attachment_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked |= self._WRITE_ONCE
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        trusted = self._fix_guard_open()
        if not trusted:
            c.require_group(self.env, c.G_ASSESSOR, "E-Waste Triage Assessor", "triage e-waste")
        own = c.employee_of(self.env)
        # the evidence is attached to the decision itself once it exists
        staged = [
            (vals.pop("evidence_file", None), (vals.pop("evidence_filename", None) or "").strip())
            for vals in vals_list
        ]
        Criteria = self.env["fix.ewaste.triage.criteria"]
        for vals, (data, _fname) in zip(vals_list, staged, strict=True):
            col = self.env["fix.ewaste.collection"].sudo().browse(vals.get("collection_id"))
            company = col.company_id if col.exists() else self.env.company
            criteria = Criteria._fix_in_force(company)
            if not trusted:
                if vals.get("criteria_id") and vals["criteria_id"] != criteria.id:
                    raise UserError("A triage applies the criteria in force, not another set.")
                criteria._fix_check_assessment(vals, bool(data))
            vals["criteria_id"] = criteria.id or False
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.ewaste.triage", "ETRI/New")
            if not trusted:
                # the assessor is the user deciding, never a typed name
                if vals.get("inspector_id") and vals["inspector_id"] != own.id:
                    raise UserError("A triage decision is recorded by its own assessor.")
                if not own:
                    raise UserError(
                        "Triage is recorded by a named assessor: link your user to an "
                        "employee record first."
                    )
                vals["inspector_id"] = own.id
            if vals.get("data_bearing"):
                vals["wipe_required"] = True
        records = super().create(vals_list)
        for rec, (data, fname) in zip(records, staged, strict=True):
            if data:
                att = self.env["ir.attachment"].create(
                    {
                        "name": fname or "%s - assessment evidence" % rec.name,
                        "datas": data,
                        "res_model": rec._name,
                        "res_id": rec.id,
                    }
                )
                rec.sudo()._guarded().write({"evidence_attachment_id": att.id})
        for rec in records:
            if not trusted:
                rec.sudo()._guarded().write({"decided_by_id": self.env.uid})
            collection = rec.collection_id
            if collection.state != "collected":
                raise UserError(
                    "%s is already %s: a triage decision is made once, on a collected item."
                    % (collection.name, collection.state)
                )
            collection._fix_apply_triage(rec)
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                changed = c.changed_fields(rec, vals, self._WRITE_ONCE)
                if changed:
                    c.frozen_refuse(rec, changed, "is a recorded triage decision")
        return super().write(vals)


class FixEwasteBatch(models.Model):
    """A material batch transferred to a licensed recycler. Itemised: its
    weight is the sum of its items (BRU-ESG-05), and each step needs the
    recycler's evidence (M18-7)."""

    _name = "fix.ewaste.batch"
    _description = "E-Waste Material Batch"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "dispatched_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    material_type = fields.Selection(MATERIALS, required=True, default="phone")
    collection_ids = fields.One2many("fix.ewaste.collection", "batch_id", string="Items")
    battery_ids = fields.One2many("fix.ewaste.battery", "batch_id", string="Battery Items")
    item_count = fields.Integer(compute="_compute_weight", store=True)
    weight_kg = fields.Float(
        string="Weight (kg)",
        compute="_compute_weight",
        store=True,
        readonly=True,
        help="The sum of the items' weights, never typed (BRU-ESG-05).",
    )
    partner_id = fields.Many2one(
        "fix.ewaste.partner", string="Certified Partner", ondelete="restrict"
    )
    destination_country_id = fields.Many2one(
        "res.country",
        string="Destination Country",
        default=lambda self: self.env.ref("base.bd", raise_if_not_found=False),
    )
    basel_pic_id = fields.Many2one("fix.ewaste.basel.pic", string="Basel PIC")
    manifest_id = fields.Many2one("fix.ewaste.manifest", string="Manifest", readonly=True)
    transfer_note_ref = fields.Char(string="Transfer Note Ref", readonly=True)
    dispatched_on = fields.Date(readonly=True)
    dispatched_by_id = fields.Many2one("res.users", readonly=True)
    received_weight_kg = fields.Float(string="Recycler Weighbridge (kg)")
    recycler_receipt_ref = fields.Char(string="Recycler Receipt Ref")
    received_on = fields.Date(readonly=True)
    received_by_id = fields.Many2one("res.users", readonly=True)
    processing_evidence_id = fields.Many2one(
        "ir.attachment", string="Recycler Processing Evidence", ondelete="restrict"
    )
    processing_file = fields.Binary(string="Upload Processing Evidence", store=False)
    processing_filename = fields.Char(string="Evidence File Name", store=False)
    processed_weight_kg = fields.Float(readonly=True)
    processed_on = fields.Date(readonly=True)
    processed_by_id = fields.Many2one("res.users", readonly=True)
    certificate_ids = fields.One2many("fix.ewaste.certificate", "batch_id", string="Certificates")
    exception_ids = fields.One2many(
        "fix.ewaste.certificate.exception", "batch_id", string="Certificate Exceptions"
    )
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

    _GUARDED = frozenset(
        {
            "state",
            "weight_kg",
            "item_count",
            "manifest_id",
            "transfer_note_ref",
            "dispatched_on",
            "dispatched_by_id",
            "received_on",
            "received_by_id",
            "processed_weight_kg",
            "processed_on",
            "processed_by_id",
        }
    )
    # editable only in the state named (the step's evidence input)
    _EDIT_IN = {
        "partner_id": ("draft",),
        "material_type": ("draft",),
        "destination_country_id": ("draft",),
        "basel_pic_id": ("draft",),
        "company_id": ("draft",),
        "received_weight_kg": ("dispatched",),
        "recycler_receipt_ref": ("dispatched",),
        "processing_evidence_id": ("received",),
    }

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    _UPLOADS = {"processing_evidence_id": ("processing_file", "processing_filename")}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        for name, states in self._EDIT_IN.items():
            if (self and any(r.state not in states for r in self)) or (
                not self and "draft" not in states
            ):
                locked.add(name)
        return c.lock_uploads(locked, self._UPLOADS)

    @api.depends("collection_ids.weight_kg", "battery_ids.weight_kg")
    def _compute_weight(self):
        for rec in self:
            rec.weight_kg = round(
                sum(rec.collection_ids.mapped("weight_kg"))
                + sum(rec.battery_ids.mapped("weight_kg")),
                3,
            )
            rec.item_count = len(rec.collection_ids) + len(rec.battery_ids)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            c.require_group(self.env, c.G_DISPATCH, "E-Waste Dispatcher", "open a batch")
        staged = c.stage_uploads(vals_list, self._UPLOADS)
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.ewaste.batch", "EBAT/New")
        targets = [vals.pop("state", None) or "draft" for vals in vals_list]
        recs = super().create(vals_list)
        for rec, target in zip(recs, targets, strict=True):
            if target != "draft":
                if not self._fix_guard_open():
                    rec._fix_guard_refuse(["state"])
                rec._guarded().write({"state": target})
        c.attach_staged(recs, staged)
        return recs

    def write(self, vals):
        vals = c.lift_uploads(self, vals, self._UPLOADS)
        if self and not self._fix_guard_open():
            for rec in self:
                names = {n for n, states in self._EDIT_IN.items() if rec.state not in states}
                changed = c.changed_fields(rec, vals, names)
                if changed:
                    c.frozen_refuse(rec, changed, "is %s" % rec.state)
        if "state" in vals:
            for rec in self:
                rec._check_target_state(vals["state"])
        return super().write(vals)

    # ------------------------------------------------------------ gates
    def _check_target_state(self, new_state):
        self.ensure_one()
        old = self.state
        if new_state == old:
            return
        allowed = {"draft": "dispatched", "dispatched": "received", "received": "processed"}
        if allowed.get(old) != new_state:
            raise UserError("Batch %s cannot move from %s to %s." % (self.name, old, new_state))
        if new_state == "dispatched":
            self._check_dispatch()
        elif new_state == "received":
            self._check_receipt()
        elif new_state == "processed" and not self.processing_evidence_id:
            raise UserError(
                "Batch %s: attach the recycler's processing evidence first (M18-7)." % self.name
            )

    def _check_partner_licence(self):
        """BRU-ESG-02 / M18-3: licence currency re-checked at the moment of
        transfer, on every path."""
        self.ensure_one()
        partner = self.partner_id.sudo()
        if not partner:
            raise UserError("A batch is dispatched to a certified partner")
        today = c.today(self.env)
        if partner.state != "active" or not partner.approved_by_id:
            raise UserError(
                "Recycler %s is %s: only an approved, active recycler receives e-waste."
                % (partner.name, partner.state)
            )
        if not partner.valid_to or partner.valid_to < today:
            raise UserError(
                "Recycler %s's licence %s is not in date (valid to %s)."
                % (partner.name, partner.certificate_no or "-", partner.valid_to or "unset")
            )
        if not partner.certificate_no or not partner.licence_attachment_id:
            raise UserError("Recycler %s has no licence number and evidence." % partner.name)
        wanted = c.panel(self.env)
        if partner.certification not in wanted:
            raise UserError(
                "Recycler %s holds %s; the recycler panel requires %s (%s)."
                % (partner.name, partner.certification, ", ".join(sorted(wanted)), c.P_PANEL)
            )
        return partner

    def _check_dispatch(self):
        self.ensure_one()
        partner = self._check_partner_licence()
        if not self.env.su and partner.approved_by_id == self.env.user:
            raise UserError(
                "You qualified recycler %s: the person who approves a recycler does not "
                "dispatch to it (spec §13)." % partner.name
            )
        items = self.sudo().collection_ids
        batteries = self.sudo().battery_ids
        if not items and not batteries:
            raise UserError("Batch %s lists no items: load the ready items first." % self.name)
        for item in items:
            if item.state != "recycled":
                raise UserError("%s is %s, not ready for the recycler." % (item.name, item.state))
            denial = item._fix_wipe_denial()
            if denial:
                # S4: the M06 approval re-checked at the consequence
                raise UserError("%s cannot leave: %s" % (item.name, denial))
        for bat in batteries:
            if bat.state != "stored" or not bat.terminal_taped or not bat.inspected_by_id:
                raise UserError(
                    "Battery %s has no HSE inspection on record (terminals taped by a "
                    "named inspector)." % bat.name
                )
        if batteries and len(set(batteries.mapped("swollen_cell"))) > 1:
            raise UserError(
                "Batch %s mixes swollen and sound cells (BRU-ESG-08): ship them apart." % self.name
            )
        bd = self.env.ref("base.bd", raise_if_not_found=False)
        if self.destination_country_id and self.destination_country_id != bd:
            pic = self.sudo().basel_pic_id
            today = c.today(self.env)
            if (
                not pic
                or pic.state != "consented"
                or pic.partner_id != partner
                or pic.destination_country_id != self.destination_country_id
                or (pic.valid_to and pic.valid_to < today)
                or (pic.max_weight_kg and self.weight_kg > pic.max_weight_kg)
            ):
                raise UserError(
                    "A transfer to %s needs a consented, in-date Basel prior-informed-"
                    "consent record for %s covering this weight (BRU-ESG-06)."
                    % (self.destination_country_id.name, partner.name)
                )

    def _check_receipt(self):
        self.ensure_one()
        if not (self.recycler_receipt_ref or "").strip() or self.received_weight_kg <= 0:
            raise UserError(
                "Batch %s: record the recycler's receipt reference and weighbridge weight."
                % self.name
            )
        tol = c.param_float(self.env, c.P_TOLERANCE, c.DEFAULT_TOLERANCE)
        expected = self.weight_kg
        if expected <= 0 or abs(self.received_weight_kg - expected) > expected * tol / 100.0:
            raise UserError(
                "Batch %s left at %.3f kg and the recycler weighed %.3f kg: outside the "
                "%.1f%% tolerance (T-05). Investigate before receiving it."
                % (self.name, expected, self.received_weight_kg, tol)
            )

    # ------------------------------------------------------------ actions
    def action_load_ready_items(self):
        """Load the items ready for this batch: destroyed items of its
        material, or inspected battery cells for a battery batch."""
        c.require_group(self.env, c.G_DISPATCH, "E-Waste Dispatcher", "load a batch")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft batch is loaded.")
            if rec.material_type == "battery":
                cells = self.env["fix.ewaste.battery"].search(
                    [
                        ("company_id", "=", rec.company_id.id),
                        ("state", "=", "stored"),
                        ("batch_id", "=", False),
                        ("terminal_taped", "=", True),
                    ]
                )
                cells._guarded().write({"batch_id": rec.id})
            else:
                items = self.env["fix.ewaste.collection"].search(
                    [
                        ("company_id", "=", rec.company_id.id),
                        ("state", "=", "recycled"),
                        ("batch_id", "=", False),
                        ("material_type", "=", rec.material_type),
                    ]
                )
                items._guarded().write({"batch_id": rec.id})
        return True

    def action_dispatch(self):
        c.require_group(self.env, c.G_DISPATCH, "E-Waste Dispatcher", "dispatch a batch")
        for rec in self:
            if not rec.partner_id:
                raise UserError("A batch is dispatched to a certified partner")
            if rec.state != "draft":
                raise UserError("Dispatch from draft")
            rec._check_dispatch()
            manifest = self.env["fix.ewaste.manifest"].sudo()._fix_issue_for(rec)
            rec._guarded().write(
                {
                    "state": "dispatched",
                    "dispatched_on": c.today(rec.env),
                    "dispatched_by_id": rec.env.uid,
                    "manifest_id": manifest.id,
                    "transfer_note_ref": manifest.name,
                }
            )
            rec.battery_ids._guarded().write({"state": "dispatched"})
            rec.message_post(
                body="Dispatched to %s under manifest %s." % (rec.partner_id.name, manifest.name)
            )
        return True

    def action_receive(self):
        c.require_group(self.env, c.G_DISPATCH, "E-Waste Dispatcher", "receive a batch")
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Receive from dispatched")
            rec._guarded().write(
                {
                    "state": "received",
                    "received_on": c.today(rec.env),
                    "received_by_id": rec.env.uid,
                }
            )
        return True

    def action_process(self):
        c.require_group(self.env, c.G_DISPATCH, "E-Waste Dispatcher", "record processing")
        for rec in self:
            if rec.state != "received":
                raise UserError("Process from received")
            rec._guarded().write(
                {
                    "state": "processed",
                    # what the recycler weighed in is what it processed
                    "processed_weight_kg": rec.received_weight_kg,
                    "processed_on": c.today(rec.env),
                    "processed_by_id": rec.env.uid,
                }
            )
            for bat in rec.battery_ids:
                bat._guarded().write({"state": "processed"})
                bat._fix_close_collection()
        return True

    def action_record_certificate(self):
        """Open the recycler's disposal certificate for this processed batch
        (draft: the certificate number and evidence are entered, then a
        compliance officer issues it)."""
        c.require_group(
            self.env, c.G_DISPATCH, "E-Waste Dispatcher", "record a recycler certificate"
        )
        out = self.env["fix.ewaste.certificate"]
        for rec in self:
            if rec.state != "processed":
                raise UserError("A disposal certificate is recorded for a processed batch.")
            live = rec.certificate_ids.filtered(lambda x: x.state in ("draft", "issued"))
            if live.filtered(lambda x: x.state == "draft"):
                raise UserError("Batch %s already has a draft certificate." % rec.name)
            # a supplementary certificate is recorded for the items an earlier
            # one left out (open exceptions, FR-ESG-013)
            if live and not rec.exception_ids.filtered(lambda e: e.state == "open"):
                raise UserError("Batch %s already has its certificate." % rec.name)
            out |= out._guarded().create({"batch_id": rec.id})
        return True


class FixEwasteBattery(models.Model):
    """A lithium-ion / battery stream item with its hazard handling."""

    _name = "fix.ewaste.battery"
    _description = "E-Waste Battery Handling"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
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
            # FR-ESG-015 (capture pass 2): the other hazardous fractions the
            # spec names, each with its own storage ceiling class
            ("crt", "CRT Glass (lead)"),
            ("mercury_lamp", "Mercury-Containing Lamp"),
            ("refrigerant", "Refrigerant-Bearing Equipment"),
            ("toner", "Toner / Ink Cartridge"),
            ("other", "Other"),
        ],
        string="Hazardous Fraction",
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
    inspection_evidence_id = fields.Many2one(
        "ir.attachment", string="Inspection Photo / Evidence", ondelete="restrict"
    )
    inspection_file = fields.Binary(string="Upload Inspection Photo", store=False)
    inspection_filename = fields.Char(string="Photo File Name", store=False)
    inspected_by_id = fields.Many2one("res.users", string="HSE Inspector", readonly=True)
    inspected_on = fields.Datetime(readonly=True)
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

    _GUARDED = frozenset(
        {"state", "terminal_taped", "inspected_by_id", "inspected_on", "batch_id", "received_on"}
    )
    # the cell as inspected: frozen once the HSE inspection is recorded
    _FROZEN_AFTER_INSPECTION = frozenset(
        {
            "swollen_cell",
            "chemistry",
            "hazard_class",
            "weight_kg",
            "quarantine_barrel_ref",
            "inspection_evidence_id",
            "collection_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    _UPLOADS = {"inspection_evidence_id": ("inspection_file", "inspection_filename")}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.inspected_by_id for r in self):
            locked |= self._FROZEN_AFTER_INSPECTION
        if self and any(r.state != "stored" for r in self):
            locked.add("storage_location")
        return c.lock_uploads(locked, self._UPLOADS)

    @api.model_create_multi
    def create(self, vals_list):
        staged = c.stage_uploads(vals_list, self._UPLOADS)
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.ewaste.battery", "EBAT/New")
        recs = super().create(vals_list)
        recs._check_location_ceiling()
        c.attach_staged(recs, staged)
        return recs

    def write(self, vals):
        vals = c.lift_uploads(self, vals, self._UPLOADS)
        if self and not self._fix_guard_open():
            for rec in self:
                names = set(self._FROZEN_AFTER_INSPECTION) if rec.inspected_by_id else set()
                if rec.state != "stored":
                    names.add("storage_location")
                changed = c.changed_fields(rec, vals, names)
                if changed:
                    c.frozen_refuse(rec, changed, "is inspected")
        if "state" in vals:
            for rec in self:
                rec._check_target_state(vals["state"])
        res = super().write(vals)
        if {"storage_location", "weight_kg"} & set(vals):
            self._check_location_ceiling()
        return res

    def _check_location_ceiling(self):
        """BRU-ESG-07: the battery mass held at one location is capped."""
        ceiling = c.param_float(self.env, c.P_BATTERY_CEILING, c.DEFAULT_BATTERY_CEILING)
        if ceiling <= 0:
            return
        for loc, company in {
            (r.storage_location, r.company_id) for r in self if r.storage_location
        }:
            held = self.sudo().search(
                [
                    ("storage_location", "=", loc),
                    ("company_id", "=", company.id),
                    ("state", "=", "stored"),
                ]
            )
            total = sum(held.mapped("weight_kg"))
            if total > ceiling + 1e-6:
                raise ValidationError(
                    "Location %s would hold %.1f kg of batteries; the ceiling is %.1f kg "
                    "(%s)." % (loc, total, ceiling, c.P_BATTERY_CEILING)
                )

    def _check_target_state(self, new_state):
        self.ensure_one()
        old = self.state
        if new_state == old:
            return
        if (old, new_state) not in (("stored", "dispatched"), ("dispatched", "processed")):
            raise UserError("Battery %s cannot move from %s to %s." % (self.name, old, new_state))
        if new_state == "dispatched":
            batch = self.sudo().batch_id
            if not self.terminal_taped or not self.inspected_by_id:
                raise ValidationError(
                    "Cannot dispatch battery %s: Terminals must be taped first, by an HSE "
                    "inspection on record" % self.name
                )
            if not batch or batch.state not in ("draft", "dispatched"):
                raise UserError(
                    "Battery %s leaves only with a batch under a hazardous manifest." % self.name
                )
        if new_state == "processed":
            batch = self.sudo().batch_id
            if not batch or batch.state not in ("received", "processed"):
                raise UserError(
                    "Battery %s is processed only once the recycler received its batch." % self.name
                )

    def action_inspect_and_quarantine(self):
        """UN 3480 Class 9 inspection, recorded by an HSE inspector with
        evidence (E8 / M18-8): the inspector attests the taping; a swollen
        cell goes to the vermiculite drum."""
        c.require_group(self.env, c.G_HSE, "E-Waste HSE Officer", "record a battery inspection")
        for rec in self:
            if rec.state != "stored":
                raise UserError("Battery %s is not in storage." % rec.name)
            if rec.inspected_by_id:
                raise UserError("Battery %s is already inspected." % rec.name)
            if not rec.inspection_evidence_id:
                raise UserError(
                    "Attach the inspection photo of battery %s (taped terminals) first." % rec.name
                )
            vals = {
                "terminal_taped": True,
                "inspected_by_id": rec.env.uid,
                "inspected_on": fields.Datetime.now(),
            }
            if rec.swollen_cell:
                if not rec.quarantine_barrel_ref:
                    vals["quarantine_barrel_ref"] = "DRUM-VERM-%s" % (rec.name or "01")
                vals["storage_location"] = "Quarantine Bay Q-09 (Fireproof Vermiculite Barrel)"
            elif not rec.storage_location:
                vals["storage_location"] = "Storage Shelf B-04"
            rec._guarded().write(vals)
        return True

    def action_dispatch(self):
        """Dispatch battery item to certified recycler under hazardous manifest:
        it travels with its batch (the batch dispatch moves it)."""
        for rec in self:
            if not rec.terminal_taped:
                raise ValidationError(
                    "Cannot dispatch battery %s: Terminals must be taped first" % rec.name
                )
            if rec.state != "stored":
                raise UserError("Battery %s is %s, not in storage." % (rec.name, rec.state))
            if not rec.batch_id:
                raise UserError("Battery %s is not in a batch." % rec.name)
            rec.batch_id.action_dispatch()
        return True

    def action_process(self):
        """Mark battery item as processed/decontaminated (from its received batch)."""
        c.require_group(self.env, c.G_DISPATCH, "E-Waste Dispatcher", "record processing")
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Battery %s is processed only after dispatch." % rec.name)
            rec._guarded().write({"state": "processed"})
            rec._fix_close_collection()
        return True

    def _fix_close_collection(self):
        for rec in self:
            col = rec.sudo().collection_id
            if (
                col
                and col.state == "hazmat"
                and all(b.state == "processed" for b in col.battery_ids)
            ):
                col._guarded().write({"state": "disposed"})


class FixEwastePartner(models.Model):
    """A certified recycling partner and its licence. Registered by anyone,
    approved through M63 by a Recycler Approver who is not the registrant
    (E5 / M18-3); its licence is re-checked at every dispatch."""

    _name = "fix.ewaste.partner"
    _description = "Certified E-Waste Partner"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "name"

    _approval_domain = "ewaste_recycler"
    _approval_apply_method = "action_approve_partner"
    _approval_group = c.G_RECYCLER_APPROVER
    _approval_routed = True

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
            ("r2v3", "R2v3"),
            ("e_stewards", "e-Stewards"),
        ],
        required=True,
        default="doe",
    )
    certificate_no = fields.Char(string="Certificate No")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    licence_attachment_id = fields.Many2one(
        "ir.attachment", string="Licence Evidence", ondelete="restrict"
    )
    licence_file = fields.Binary(string="Upload Licence Scan", store=False)
    licence_filename = fields.Char(string="Licence File Name", store=False)
    capability = fields.Text(string="Handled Materials")
    state = fields.Selection(
        [
            ("draft", "Pending Approval"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("expired", "Expired"),
        ],
        required=True,
        default="draft",
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(readonly=True)
    expiry_warned_on = fields.Date(readonly=True)

    _dates_ordered = models.Constraint(
        "CHECK (valid_to IS NULL OR valid_to >= valid_from)",
        "Certificate end date cannot precede its start date",
    )

    _LICENCE = frozenset(
        {
            "name",
            "certification",
            "certificate_no",
            "valid_from",
            "valid_to",
            "licence_attachment_id",
            "company_id",
            "partner_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "state",
            "approved_by_id",
            "approved_on",
            "expiry_warned_on",
        }

    _UPLOADS = {"licence_attachment_id": ("licence_file", "licence_filename")}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" or r.approval_state == "pending" for r in self):
            locked |= self._LICENCE
        return c.lock_uploads(locked, self._UPLOADS)

    def _approval_pinned_fields(self) -> set:
        return set(super()._approval_pinned_fields()) | (self._LICENCE - {"name"})

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.state == "draft"

    @api.constrains("valid_to", "state")
    def _check_validity(self):
        """M18-17: an ACTIVE recycler needs an in-date licence; an expired one
        may be recorded with its real, past expiry."""
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state == "active" and rec.valid_to and rec.valid_to < today:
                raise ValidationError("A certificate that has expired cannot be active")
            if rec.state == "active" and not rec.valid_to:
                raise ValidationError("An active recycler's licence has an expiry date.")

    @api.model_create_multi
    def create(self, vals_list):
        staged = c.stage_uploads(vals_list, self._UPLOADS)
        recs = super().create(vals_list)
        c.attach_staged(recs, staged)
        return recs

    def write(self, vals):
        vals = c.lift_uploads(self, vals, self._UPLOADS)
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft":
                    changed = c.changed_fields(rec, vals, self._LICENCE)
                    if changed:
                        c.frozen_refuse(
                            rec,
                            changed,
                            "is %s (renew the licence to change it)" % rec.state,
                        )
        return super().write(vals)

    def action_approve_partner(self):
        """Apply the routed approval (M63): only from the approver's inbox."""
        self._approval_assert_routed()
        c.require_group(
            self.env, c.G_RECYCLER_APPROVER, "E-Waste Recycler Approver", "approve a recycler"
        )
        today = c.today(self.env)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Recycler %s is not awaiting approval." % rec.name)
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError("The registrant of a recycler does not approve it.")
            if not (rec.certificate_no or "").strip() or not rec.licence_attachment_id:
                raise UserError(
                    "Recycler %s needs its licence number and licence evidence." % rec.name
                )
            if not rec.valid_to or rec.valid_to < today:
                raise UserError("Recycler %s's licence is not in date." % rec.name)
            rec._guarded().write(
                {
                    "state": "active",
                    "approved_by_id": rec.env.uid,
                    "approved_on": fields.Datetime.now(),
                    "expiry_warned_on": False,
                }
            )
            rec.message_post(body="Recycler approved by %s." % rec.env.user.name)
        return True

    def action_suspend(self):
        c.require_group(
            self.env, c.G_RECYCLER_APPROVER, "E-Waste Recycler Approver", "suspend a recycler"
        )
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active recycler is suspended.")
            rec._guarded().write({"state": "suspended"})
        return True

    def action_renew(self):
        """Back to draft to record a renewed licence; it needs a new approval."""
        if not (
            self.env.su
            or self.env.user.has_group(c.G_RECYCLER_APPROVER)
            or self.env.user.has_group(c.G_DISPATCH)
        ):
            raise UserError("Only a Recycler Approver or a Dispatcher starts a licence renewal.")
        for rec in self:
            if rec.state == "draft":
                raise UserError("Recycler %s is already pending approval." % rec.name)
            rec._guarded().write(
                {
                    "state": "draft",
                    "approved_by_id": False,
                    "approved_on": False,
                    "approval_state": "none",
                }
            )
        return True

    @api.model
    def cron_licence_expiry(self):
        """E12: expire lapsed recycler licences, warn ahead of expiry, and
        expire Basel consents and DoE registrations. Safe to re-run."""
        today = c.today(self.env)
        warn = c.param_int(self.env, c.P_LICENCE_WARNING_DAYS, c.DEFAULT_REMINDER_DAYS)
        Partner = self.sudo()
        lapsed = Partner.search([("state", "=", "active"), ("valid_to", "<", today)])
        for rec in lapsed:
            rec._guarded().write({"state": "expired"})
            c.notify(
                rec,
                "Recycler licence expired",
                "Recycler %s's licence %s expired on %s: no batch may be dispatched to it."
                % (rec.name, rec.certificate_no or "-", rec.valid_to),
                c.G_RECYCLER_APPROVER,
            )
        soon = Partner.search(
            [
                ("state", "=", "active"),
                ("valid_to", ">=", today),
                ("valid_to", "<=", today + timedelta(days=warn)),
                ("expiry_warned_on", "=", False),
            ]
        )
        for rec in soon:
            rec._guarded().write({"expiry_warned_on": today})
            c.notify(
                rec,
                "Recycler licence expiring",
                "Recycler %s's licence expires on %s: renew it." % (rec.name, rec.valid_to),
                c.G_RECYCLER_APPROVER,
            )
        self.env["fix.ewaste.basel.pic"].sudo()._fix_expire(today)
        self.env["fix.ewaste.registration"].sudo()._fix_expire(today)
        return len(lapsed)


class FixEwasteCertificate(models.Model):
    """The recycler's disposal certificate for a processed batch, reconciled
    item by item (FR-ESG-013 / T-03). Draft -> issued (by a compliance
    officer, from the recycler's evidence) -> revoked (terminal)."""

    _name = "fix.ewaste.certificate"
    _description = "E-Waste Disposal Certificate"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "issued_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    collection_id = fields.Many2one(
        "fix.ewaste.collection", string="Collection", ondelete="set null", index=True
    )
    collection_ids = fields.Many2many(
        "fix.ewaste.collection",
        "fix_ewaste_certificate_collection_rel",
        "certificate_id",
        "collection_id",
        string="Certified Items",
        readonly=True,
    )
    batch_id = fields.Many2one("fix.ewaste.batch", string="Batch", ondelete="restrict")
    partner_id = fields.Many2one(
        "fix.ewaste.partner", string="Certified Partner", required=True, ondelete="restrict"
    )
    material_type = fields.Selection(MATERIALS, required=True, default="phone")
    weight_kg = fields.Float(
        string="Certified Weight (kg)",
        readonly=True,
        help="The weight of the items the certificate lists (set at issue).",
    )
    recycler_stated_weight_kg = fields.Float(string="Weight Stated by Recycler (kg)")
    certificate_no = fields.Char(string="Certificate No")
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Recycler Certificate (scan)", ondelete="restrict"
    )
    evidence_file = fields.Binary(string="Upload Recycler Certificate", store=False)
    evidence_filename = fields.Char(string="Certificate File Name", store=False)
    file_ref = fields.Char(string="Document Ref")
    issued_on = fields.Date(readonly=True)
    issued_by_id = fields.Many2one("res.users", readonly=True)
    revoke_reason = fields.Text()
    revoked_by_id = fields.Many2one("res.users", readonly=True)
    revoked_on = fields.Date(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("issued", "Issued"), ("revoked", "Revoked")],
        required=True,
        default="draft",
    )
    # M18 capture pass 2 (FR-ESG-013 / T-03 / BRU-ESG-04, AC-07): the items of
    # the batch the recycler's certificate does NOT list. They are left
    # uncertified, each with an open exception, until a supplementary
    # certificate covers it or an investigation closes it.
    uncovered_collection_ids = fields.Many2many(
        "fix.ewaste.collection",
        "fix_ewaste_certificate_uncovered_rel",
        "certificate_id",
        "collection_id",
        string="Items NOT on the Recycler's Certificate",
    )
    exception_ids = fields.One2many(
        "fix.ewaste.certificate.exception", "certificate_id", string="Exceptions Raised"
    )

    _GUARDED = frozenset(
        {
            "state",
            "weight_kg",
            "collection_ids",
            "collection_id",
            "issued_on",
            "issued_by_id",
            "revoked_by_id",
            "revoked_on",
            "batch_id",
            "partner_id",
            "company_id",
        }
    )
    _DRAFT_INPUT = frozenset(
        {
            "recycler_stated_weight_kg",
            "certificate_no",
            "evidence_attachment_id",
            "file_ref",
            "material_type",
            "uncovered_collection_ids",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    _UPLOADS = {"evidence_attachment_id": ("evidence_file", "evidence_filename")}

    def _fix_scope(self):
        """The batch items this certificate is about: those not yet certified
        (a supplementary certificate covers what an earlier one left out)."""
        self.ensure_one()
        return self.sudo().batch_id.collection_ids.filtered(lambda i: i.state == "recycled")

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._DRAFT_INPUT
        if not self or any(r.state != "issued" for r in self):
            locked.add("revoke_reason")
        return c.lock_uploads(locked, self._UPLOADS)

    @api.model_create_multi
    def create(self, vals_list):
        trusted = self._fix_guard_open()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.ewaste.certificate", "ECER/New")
            if vals.get("batch_id"):
                batch = self.env["fix.ewaste.batch"].sudo().browse(vals["batch_id"])
                vals.setdefault("partner_id", batch.partner_id.id)
                vals.setdefault("material_type", batch.material_type)
                vals.setdefault("company_id", batch.company_id.id)
        if not trusted:
            # M18-4: a certificate comes from a processed batch's action
            raise UserError(
                "A disposal certificate is recorded from its processed recycler batch "
                "(Record Certificate), never typed in."
            )
        return super().create(vals_list)

    def write(self, vals):
        vals = c.lift_uploads(self, vals, self._UPLOADS)
        if self and not self._fix_guard_open():
            for rec in self:
                names = set(self._DRAFT_INPUT) if rec.state != "draft" else set()
                if rec.state != "issued":
                    names.add("revoke_reason")
                changed = c.changed_fields(rec, vals, names)
                if changed:
                    c.frozen_refuse(rec, changed, "is %s" % rec.state)
        if vals.get("state"):
            for rec in self:
                ok = {("draft", "issued"), ("issued", "revoked")}
                if rec.state != vals["state"] and (rec.state, vals["state"]) not in ok:
                    raise UserError(
                        "Certificate %s cannot move from %s to %s (a revoked certificate "
                        "is never re-issued)." % (rec.name, rec.state, vals["state"])
                    )
        return super().write(vals)

    def action_issue(self):
        """Issue from the recycler's evidence and certify every item it lists."""
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "issue a disposal certificate"
        )
        tol = c.param_float(self.env, c.P_TOLERANCE, c.DEFAULT_TOLERANCE)
        for rec in self:
            batch = rec.sudo().batch_id
            if rec.state != "draft":
                raise UserError("Certificate %s is %s." % (rec.name, rec.state))
            if not batch or batch.state != "processed":
                raise UserError("Certificate %s: its batch is not processed." % rec.name)
            if rec.partner_id != batch.partner_id:
                raise UserError("Certificate %s names another recycler than its batch." % rec.name)
            if not (rec.certificate_no or "").strip() or not rec.evidence_attachment_id:
                raise UserError(
                    "Certificate %s: enter the recycler's certificate number and attach it."
                    % rec.name
                )
            scope = rec._fix_scope()
            uncovered = rec.sudo().uncovered_collection_ids
            if uncovered - scope:
                raise UserError(
                    "Certificate %s: %s %s not awaiting a certificate in batch %s."
                    % (
                        rec.name,
                        ", ".join((uncovered - scope).mapped("name")),
                        "is" if len(uncovered - scope) == 1 else "are",
                        batch.name,
                    )
                )
            items = scope - uncovered
            earlier = batch.certificate_ids.filtered(
                lambda x, r=rec: x != r and x.state == "issued"
            )
            if earlier and not items:
                raise UserError(
                    "Certificate %s covers nothing: batch %s has no item left awaiting a "
                    "certificate." % (rec.name, batch.name)
                )
            if uncovered and not items:
                raise UserError(
                    "Certificate %s lists none of the batch's items: record the exception "
                    "on the batch instead of issuing an empty certificate." % rec.name
                )
            if earlier or uncovered:
                # a partial or supplementary certificate states what it covers
                expected, basis = (
                    round(sum(items.mapped("weight_kg")), 3),
                    "the %d item(s) it covers" % len(items),
                )
            else:
                expected, basis = batch.processed_weight_kg, "batch %s processed" % batch.name
            if expected <= 0 or abs(rec.recycler_stated_weight_kg - expected) > (
                expected * tol / 100.0
            ):
                raise UserError(
                    "Certificate %s states %.3f kg; %s weigh %.3f kg (tolerance %.1f%%)."
                    % (rec.name, rec.recycler_stated_weight_kg, basis, expected, tol)
                )
            rec._guarded().write(
                {
                    "state": "issued",
                    "issued_on": c.today(rec.env),
                    "issued_by_id": rec.env.uid,
                    "collection_ids": [(6, 0, items.ids)],
                    "collection_id": items[:1].id if len(items) == 1 else False,
                    "weight_kg": round(
                        sum(items.mapped("weight_kg"))
                        + (0.0 if earlier else sum(batch.battery_ids.mapped("weight_kg"))),
                        3,
                    ),
                }
            )
            Exc = rec.env["fix.ewaste.certificate.exception"].sudo()
            Exc._fix_resolve(items, rec)
            Exc._fix_raise(uncovered, rec)
            for item in items:
                item._guarded().write(
                    {
                        "disposal_certificate_id": rec.id,
                        "disposal_certificate_ref": "%s / %s" % (rec.name, rec.certificate_no),
                    }
                )
                item._guarded().write({"state": "certified"})
                publish(
                    rec.env,
                    "ewaste.certificate_issued",
                    "fix.ewaste.collection",
                    item.id,
                    {
                        "certificate": item.disposal_certificate_ref,
                        "co2_saved": item.esg_co2_saved_kg,
                    },
                )
        return True

    def action_revoke(self):
        """Revoke (e.g. the recycler failed audit). Terminal: never re-issued;
        the items return to 'recycled' awaiting a replacement certificate."""
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "revoke a certificate"
        )
        for rec in self:
            if rec.state != "issued":
                raise UserError("Only an issued certificate is revoked.")
            if not (rec.revoke_reason or "").strip():
                raise UserError("Enter the reason for revoking %s first." % rec.name)
            rec._guarded().write(
                {"state": "revoked", "revoked_by_id": rec.env.uid, "revoked_on": c.today(rec.env)}
            )
            returned = rec.collection_ids.filtered(lambda i: i.state == "certified")
            for item in returned:
                item._guarded().write({"state": "recycled"})
                item._guarded().write(
                    {"disposal_certificate_id": False, "disposal_certificate_ref": False}
                )
            others = rec.sudo().batch_id.certificate_ids.filtered(
                lambda x, r=rec: x != r and x.state == "issued"
            )
            if others and returned:
                # the batch keeps another certificate: the returned items are
                # uncovered again and are tracked until a new one covers them
                rec.env["fix.ewaste.certificate.exception"].sudo()._fix_raise(
                    returned, rec, kind="revoked"
                )
        return True


class FixEwasteReturn(models.Model):
    """A statutory DoE / BTRC return for a period."""

    _name = "fix.ewaste.return"
    _description = "DoE / BTRC Statutory Return"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    submitted_on = fields.Date(readonly=True)
    submitted_by_id = fields.Many2one("res.users", readonly=True)
    reference = fields.Char()
    authority_ack_ref = fields.Char(string="Authority Acknowledgement No")
    accepted_by_id = fields.Many2one("res.users", readonly=True)
    accepted_on = fields.Date(readonly=True)
    nil_return_reason = fields.Text(
        string="Nil Return Reason", help="Required to submit a return of 0 t."
    )
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
        string="Total Collected (Metric Tons)", digits=(12, 3), default=0.0, readonly=True
    )
    total_tonnage_recycled = fields.Float(
        string="Total Recycled (Metric Tons)", digits=(12, 3), default=0.0, readonly=True
    )
    recovery_rate_pct = fields.Float(
        string="Recovery Rate %", compute="_compute_mass_balance", store=True
    )
    registration_id = fields.Many2one("fix.ewaste.registration", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("accepted", "Accepted")],
        required=True,
        default="draft",
    )
    notes = fields.Text()
    is_overdue = fields.Boolean(string="Overdue", compute="_compute_overdue", store=True)
    reminder_sent_on = fields.Date(readonly=True)

    _GUARDED = frozenset(
        {
            "state",
            "total_tonnage_collected",
            "total_tonnage_recycled",
            "submitted_on",
            "submitted_by_id",
            "accepted_by_id",
            "accepted_on",
            "registration_id",
            "reminder_sent_on",
        }
    )
    _FILING = frozenset(
        {
            "company_id",
            "authority",
            "period",
            "due_date",
            "reference",
            "form_type",
            "schedule_1_category",
            "nil_return_reason",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    def _frozen_for(self):
        self.ensure_one()
        if self.state == "draft":
            return set()
        names = set(self._FILING)
        if self.state == "accepted":
            names.add("authority_ack_ref")
        return names

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        for rec in self:
            locked |= rec._frozen_for()
        return locked

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

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if not c.period_bounds(rec.period):
                raise ValidationError(
                    "Return period %r is not YYYY, YYYY-MM or YYYY-Qn." % rec.period
                )

    @api.constrains("company_id", "authority", "period", "form_type")
    def _check_unique_period(self):
        """M18-6: one return per authority, period and form."""
        for rec in self:
            dup = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("authority", "=", rec.authority),
                    ("period", "=", rec.period),
                    ("form_type", "=", rec.form_type),
                ]
            )
            if dup:
                raise ValidationError(
                    "A %s %s return for %s already exists."
                    % (rec.authority.upper(), rec.form_type, rec.period)
                )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            c.require_group(
                self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "prepare a return"
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.ewaste.return", "ERET/New")
        # a user's return is born draft (the guard refuses any other state);
        # trusted code may load a historical filing as it stands.
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                changed = c.changed_fields(rec, vals, rec._frozen_for())
                if changed:
                    c.frozen_refuse(rec, changed, "is %s" % rec.state)
        if vals.get("state"):
            for rec in self:
                rec._check_target_state(vals["state"], vals)
        return super().write(vals)

    def _check_target_state(self, new_state, vals):
        old = self.state
        if new_state == old:
            return
        if (old, new_state) not in (("draft", "submitted"), ("submitted", "accepted")):
            raise UserError("Return %s cannot move from %s to %s." % (self.name, old, new_state))
        if new_state == "submitted":
            collected = vals.get("total_tonnage_collected", self.total_tonnage_collected)
            reason = vals.get("nil_return_reason", self.nil_return_reason)
            if collected <= 0 and not (reason or "").strip():
                raise UserError(
                    "Return %s reports 0 t collected: a nil return needs its reason "
                    "(M18-6)." % self.name
                )
        if (
            new_state == "accepted"
            and not (vals.get("authority_ack_ref", self.authority_ack_ref) or "").strip()
        ):
            raise UserError(
                "Return %s is accepted on the authority's acknowledgement: enter its "
                "number first." % self.name
            )

    def _fix_mass_balance(self):
        """S.R.O. 187/2021 Form-3 mass balance for this company and period, from
        the real states and fields (M18-6: it always returned 0 t)."""
        self.ensure_one()
        start, end = c.period_bounds(self.period)
        Col = self.env["fix.ewaste.collection"].sudo()
        received = Col.search(
            [
                ("company_id", "=", self.company_id.id),
                ("collected_on", ">=", start),
                ("collected_on", "<=", end),
            ]
        )
        batches = (
            self.env["fix.ewaste.batch"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("state", "=", "processed"),
                    ("processed_on", ">=", start),
                    ("processed_on", "<=", end),
                ]
            )
        )
        return (
            round(sum(received.mapped("weight_kg")) / 1000.0, 3),
            round(sum(batches.mapped("processed_weight_kg")) / 1000.0, 3),
        )

    def action_calculate_mass_balance(self):
        """Compute mass-balance from collections and batches in this period under S.R.O. 187-Law/2021."""
        c.require_group(self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "compute a return")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Return %s is %s: its figures are filed." % (rec.name, rec.state))
            collected, recycled = rec._fix_mass_balance()
            rec._guarded().write(
                {"total_tonnage_collected": collected, "total_tonnage_recycled": recycled}
            )
        return True

    def action_submit_return(self):
        """Submit statutory return to DoE / BTRC (always on fresh figures)."""
        c.require_group(self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "submit a return")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Return %s is already %s." % (rec.name, rec.state))
            registration = (
                self.env["fix.ewaste.registration"]
                .sudo()
                ._fix_active_for(rec.company_id, rec.authority)
            )
            if (
                rec.authority == "doe"
                and not registration
                and c.param_on(rec.env, c.P_RETURN_NEEDS_REGISTRATION, "1")
            ):
                raise UserError(
                    "%s has no active DoE e-waste registration: a DoE return is filed "
                    "under it (%s)." % (rec.company_id.name, c.P_RETURN_NEEDS_REGISTRATION)
                )
            collected, recycled = rec._fix_mass_balance()
            rec._guarded().write(
                {
                    "total_tonnage_collected": collected,
                    "total_tonnage_recycled": recycled,
                    "registration_id": registration.id or False,
                }
            )
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_on": c.today(rec.env),
                    "submitted_by_id": rec.env.uid,
                    "reference": rec.reference or ("DOE-SRO187-%s-%s" % (rec.period, rec.id)),
                }
            )
        return True

    def action_accept_return(self):
        """Record the authority's acknowledgement: from 'submitted', by the
        finance approver (CFO), never by whoever prepared or submitted it."""
        c.require_group(self.env, c.G_FINANCE, "E-Waste Finance Approver (CFO)", "accept a return")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted return is accepted.")
            if not self.env.su and self.env.user in (rec.submitted_by_id | rec.create_uid):
                raise UserError(
                    "You prepared or submitted return %s: someone else records its "
                    "acceptance." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "accepted",
                    "accepted_by_id": rec.env.uid,
                    "accepted_on": c.today(rec.env),
                }
            )
        return True

    @api.model
    def cron_return_due(self):
        """E12: DoE annual-return due date. Reminds the compliance officer
        ahead of the due date, and flags a late return. Safe to re-run."""
        today = c.today(self.env)
        days = c.param_int(self.env, c.P_RETURN_REMINDER_DAYS, c.DEFAULT_REMINDER_DAYS)
        Return = self.sudo()
        drafts = Return.search([("state", "=", "draft")])
        # the stored flag follows the clock, not only edits
        drafts._compute_overdue()
        for rec in drafts:
            if rec.due_date < today:
                summary, note = (
                    "Statutory return overdue",
                    "Return %s (%s %s) was due on %s and is not filed: a late filing is a "
                    "compliance event (BRU-ESG-17)."
                    % (rec.name, rec.authority.upper(), rec.period, rec.due_date),
                )
            elif rec.due_date <= today + timedelta(days=days):
                summary, note = (
                    "Statutory return due",
                    "Return %s (%s %s) is due on %s."
                    % (rec.name, rec.authority.upper(), rec.period, rec.due_date),
                )
            else:
                continue
            c.notify(rec, summary, note, c.G_COMPLIANCE)
            rec._guarded().write({"reminder_sent_on": today})
        return True
