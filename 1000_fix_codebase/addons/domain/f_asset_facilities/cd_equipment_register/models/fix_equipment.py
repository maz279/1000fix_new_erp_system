# fix_equipment — M45: test equipment + the deferred calibration (P08-M08).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixEquipment(models.Model):
    _name = "fix.equipment"
    _description = "Test Equipment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    category = fields.Char(string="Equipment Category",
                           help="e.g. multimeter, thermal camera, OTP programmer")
    maintenance_equipment_id = fields.Many2one(
        "maintenance.equipment", string="Maintenance Equipment",
        help="The Odoo maintenance link stays authoritative for work orders")
    custodian_id = fields.Many2one("hr.employee", string="Custodian")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    calibration_ids = fields.One2many("fix.calibration", "equipment_id",
                                      string="Calibrations")
    last_calibration = fields.Date(compute="_compute_calibration",
                                   string="Last Calibration")
    next_calibration = fields.Date(compute="_compute_calibration",
                                   string="Next Calibration")
    calibration_overdue = fields.Boolean(compute="_compute_calibration",
                                         string="Calibration Overdue")

    @api.depends("calibration_ids.calibrated_on", "calibration_ids.next_due")
    def _compute_calibration(self):
        today = fields.Date.today()
        for rec in self:
            done = rec.calibration_ids.filtered(lambda c: c.result == "pass")
            last = max(done.mapped("calibrated_on"), default=None)
            nxt = max(done.mapped("next_due"), default=None)
            rec.last_calibration = last
            rec.next_calibration = nxt
            rec.calibration_overdue = bool(nxt and nxt < today)

    def action_assert_usable(self):
        """ISO 9001 7.1.5: an overdue-calibration instrument is NOT usable.
        Service orders call this before measurement-dependent QC."""
        for rec in self:
            if rec.calibration_overdue:
                raise UserError(
                    "Calibration overdue on %s (due %s) — the instrument is "
                    "not usable until recalibrated"
                    % (rec.name, rec.next_calibration))
            return True


class FixCalibration(models.Model):
    """The M31-deferred capability, delivered (P08-M08-T02)."""
    _name = "fix.calibration"
    _description = "Calibration"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "calibrated_on desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    equipment_id = fields.Many2one("fix.equipment", required=True,
                                   ondelete="cascade", index=True)
    calibrated_on = fields.Date(required=True, default=fields.Date.today)
    standard_ref = fields.Char(
        string="Standard Reference",
        help="The traceable standard (ISO 9001 7.1.5: measurement traceability)",
        required=True)
    result = fields.Selection([("pass", "Pass"), ("fail", "Fail")],
                              required=True, default="pass")
    next_due = fields.Date(required=True)
    performed_by = fields.Char(string="Performed By")

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            publish(self.env, "equipment.calibration.recorded",
                    "fix.calibration", rec.id,
                    {"equipment": rec.equipment_id.code,
                     "result": rec.result,
                     "next_due": str(rec.next_due)})
            if rec.next_due < fields.Date.today():
                publish(self.env, "equipment.calibration.overdue",
                        "fix.calibration", rec.id,
                        {"equipment": rec.equipment_id.code})
        return recs

    @api.constrains("calibrated_on", "next_due")
    def _check_due_after(self):
        for rec in self:
            if rec.next_due < rec.calibrated_on:
                raise UserError("Next-due precedes the calibration date")

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")