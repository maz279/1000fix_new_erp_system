# fix_equipment_ops — M45: kits, issue/return custody, transfers, physical
# verification, out-of-service enforcement, PM/corrective jobs and usage capture.
# The equipment register and calibration records live in fix_equipment.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixEquipmentExtend(models.Model):
    _inherit = "fix.equipment"

    operational_status = fields.Selection(
        [
            ("available", "Available"),
            ("issued", "Issued"),
            ("out_of_service", "Out of Service"),
            ("retired", "Retired"),
        ],
        required=True,
        default="available",
        index=True,
    )


class FixCalibrationExtend(models.Model):
    _inherit = "fix.calibration"

    certificate_ref = fields.Char(string="Certificate Reference")
    trace_no = fields.Char(string="Trace Number")


class FixEquipmentKit(models.Model):
    _name = "fix.equipment.kit"
    _description = "Equipment Kit"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    description = fields.Text()
    line_ids = fields.One2many("fix.equipment.kit.line", "kit_id", string="Equipment")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("UNIQUE (code)", "Kit code must be unique")


class FixEquipmentKitLine(models.Model):
    _name = "fix.equipment.kit.line"
    _description = "Kit Line"
    _order = "kit_id, id"

    kit_id = fields.Many2one("fix.equipment.kit", required=True, ondelete="cascade", index=True)
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade"
    )

    _unique_equipment = models.Constraint(
        "UNIQUE (kit_id, equipment_id)", "An equipment item appears once per kit"
    )


class FixEquipmentIssue(models.Model):
    _name = "fix.equipment.issue"
    _description = "Equipment Issue / Return"
    _order = "issued_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    custodian_id = fields.Many2one("hr.employee", string="Custodian", required=True)
    reference = fields.Char(string="Job / Ticket Ref")
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    due_on = fields.Date()
    returned_on = fields.Date()
    condition_out = fields.Char()
    condition_in = fields.Char()
    state = fields.Selection(
        [("issued", "Issued"), ("returned", "Returned")], required=True, default="issued"
    )
    is_overdue = fields.Boolean(compute="_compute_overdue", store=True)

    @api.depends("due_on", "state")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_overdue = bool(rec.due_on and rec.state == "issued" and rec.due_on < today)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.issue") or "EISS/New"
                )
        records = super().create(vals_list)
        for rec in records:
            rec.equipment_id.operational_status = "issued"
        return records

    def action_return(self):
        for rec in self:
            if rec.state != "issued":
                raise UserError("Return an issued item")
            rec.write({"state": "returned", "returned_on": fields.Date.context_today(self)})
            rec.equipment_id.operational_status = "available"


class FixEquipmentTransfer(models.Model):
    _name = "fix.equipment.transfer"
    _description = "Equipment Transfer"
    _order = "transfer_date desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    from_branch_id = fields.Many2one("fix.branch", string="From Branch")
    to_branch_id = fields.Many2one("fix.branch", string="To Branch", required=True)
    from_custodian_id = fields.Many2one("hr.employee", string="From Custodian")
    to_custodian_id = fields.Many2one("hr.employee", string="To Custodian")
    transfer_date = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("posted", "Posted"), ("cancelled", "Cancelled")], required=True, default="posted"
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.transfer") or "ETRF/New"
                )
        return super().create(vals_list)


class FixEquipmentVerification(models.Model):
    _name = "fix.equipment.verification"
    _description = "Equipment Physical Verification"
    _order = "verified_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    campaign_ref = fields.Char(string="Campaign", required=True)
    verified_on = fields.Date(required=True, default=fields.Date.context_today)
    location = fields.Char()
    found = fields.Boolean(default=True)
    condition = fields.Char()
    verifier_id = fields.Many2one("hr.employee", string="Verifier")
    state = fields.Selection(
        [("verified", "Verified"), ("missing", "Missing")], required=True, default="verified"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.verification") or "EVER/New"
                )
            if vals.get("found") is False:
                vals["state"] = "missing"
        return super().create(vals_list)


class FixEquipmentOutOfService(models.Model):
    _name = "fix.equipment.oos"
    _description = "Out-of-Service Record"
    _order = "started_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    reason = fields.Char(required=True)
    started_on = fields.Date(required=True, default=fields.Date.context_today)
    resolved_on = fields.Date()
    state = fields.Selection(
        [("open", "Open"), ("resolved", "Resolved")], required=True, default="open"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.oos") or "EOOS/New"
                )
        records = super().create(vals_list)
        for rec in records:
            rec.equipment_id.operational_status = "out_of_service"
        return records

    def action_resolve(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Resolve an open out-of-service record")
            rec.write({"state": "resolved", "resolved_on": fields.Date.context_today(self)})
            rec.equipment_id.operational_status = "available"


class FixEquipmentPm(models.Model):
    _name = "fix.equipment.pm"
    _description = "Equipment PM / Corrective Job"
    _order = "scheduled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    pm_type = fields.Selection(
        [("preventive", "Preventive"), ("corrective", "Corrective")],
        required=True,
        default="preventive",
    )
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    done_on = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cost = fields.Monetary(currency_field="currency_id")
    state = fields.Selection([("open", "Open"), ("done", "Done")], required=True, default="open")
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.equipment.pm") or "EPM/New"
        return super().create(vals_list)

    def action_done(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Complete an open job")
            rec.write({"state": "done", "done_on": fields.Date.context_today(self)})


class FixEquipmentUsage(models.Model):
    _name = "fix.equipment.usage"
    _description = "Equipment Usage per Job"
    _order = "used_on desc, id desc"

    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    job_ref = fields.Char(string="Job / Work Order", required=True)
    service_order_ref = fields.Char(string="Service Order")
    used_on = fields.Date(required=True, default=fields.Date.context_today)
    uses = fields.Integer(string="Uses", default=1)
    qc_result = fields.Selection(
        [("pass", "Pass"), ("fail", "Fail"), ("na", "Not a QC use")],
        required=True,
        default="na",
    )
    notes = fields.Char()

    _uses_positive = models.Constraint("CHECK (uses > 0)", "Usage count must be positive")
