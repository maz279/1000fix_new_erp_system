# fix_vehicle — M46: fleet extension + dispatch vehicle assignment (P08-M08).
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from libs.py.fix_events import publish


class FleetVehicleCdExt(models.Model):
    _inherit = "fleet.vehicle"

    branch_id = fields.Many2one("fix.branch", string="Branch")
    # NOT driver_employee_id: hr_fleet defines that as a computed field
    fix_driver_id = fields.Many2one("fix.driver", string="Assigned Driver")
    fitness_expiry = fields.Date(string="Fitness Expiry")
    insurance_expiry = fields.Date(string="Insurance Expiry")
    compliance_ok = fields.Boolean(compute="_compute_compliance", string="Compliance OK")

    @api.depends("fitness_expiry", "insurance_expiry")
    def _compute_compliance(self):
        today = fields.Date.today()
        for rec in self:
            rec.compliance_ok = bool(
                rec.fitness_expiry
                and rec.fitness_expiry >= today
                and rec.insurance_expiry
                and rec.insurance_expiry >= today
            )

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    def action_assert_dispatchable(self):
        for rec in self:
            if not rec.compliance_ok:
                raise ValidationError(
                    "Vehicle %s is not dispatchable: fitness or insurance "
                    "expired" % (rec.name or rec.license_plate)
                )
        return True


class FixVehicleAssignment(models.Model):
    """The W2-deferred dispatch connection, delivered (P08-M08-T04): a
    vehicle on a service day. Overlaps refused — a van cannot be in two
    places."""

    _name = "fix.vehicle.assignment"
    _description = "Vehicle Assignment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    vehicle_id = fields.Many2one("fleet.vehicle", required=True, index=True)
    date = fields.Date(required=True)
    order_id = fields.Many2one("fix.service.order", string="Service Order", ondelete="set null")
    technician_id = fields.Many2one("hr.employee", string="Technician")

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec.vehicle_id.action_assert_dispatchable()
            overlaps = self.search_count(
                [
                    ("vehicle_id", "=", rec.vehicle_id.id),
                    ("date", "=", rec.date),
                    ("id", "!=", rec.id),
                ]
            )
            if overlaps:
                raise ValidationError(
                    "Vehicle %s already assigned on %s — overlaps are refused"
                    % (rec.vehicle_id.name or "vehicle", rec.date)
                )
            publish(
                self.env,
                "vehicle.assigned",
                "fix.vehicle.assignment",
                rec.id,
                {"vehicle": rec.vehicle_id.name or "", "date": str(rec.date)},
            )
        return recs
