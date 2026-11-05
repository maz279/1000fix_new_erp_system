# fix_hse_fitness — M59: the publishable fitness-for-work status, split from
# the medical record (A09 round 2; FR-HSE-037, BRU-HSE-14/15, T-06, AC-11),
# and the driving-licence eligibility (FR-HSE-019, BRU-HSE-07).
#
# Fitness: fix.hse.health is Occupational Health's alone (diagnosis,
# clinician, clinical restrictions). What the rest of the business needs is
# only "fit / restricted / unfit" and the functional restriction. That is
# this model: published by Occupational Health from a health record, read by
# the employee, their line manager and the HSE roles, written by nobody.
# Return to work reads it (fix.statutory.accident.register).
#
# Driving licence: the licence record is the fleet register's fix.driver
# (number, class, expiry; cd_vehicle_ext). A road check and a vehicle
# assignment are refused unless it is valid on the day.
from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError

STATUSES = [("fit", "Fit for Work"), ("restricted", "Fit with Restrictions"), ("unfit", "Unfit")]


class FixHseFitnessStatus(models.Model):
    _name = "fix.hse.fitness.status"
    _description = "Fitness-for-Work Status (publishable)"
    _inherit = ["fix.guarded.mixin"]
    _order = "valid_from desc, id desc"

    _CONTENT = (
        "employee_id",
        "company_id",
        "status",
        "work_restriction",
        "valid_from",
        "valid_until",
        "health_id",
        "decided_by_id",
        "migrated",
    )

    name = fields.Char(compute="_compute_name")
    employee_id = fields.Many2one("hr.employee", required=True, index=True, ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    status = fields.Selection(STATUSES, required=True)
    work_restriction = fields.Char(
        string="Work Restriction", help="Functional terms only; never a diagnosis."
    )
    valid_from = fields.Date(required=True)
    valid_until = fields.Date()
    # the medical record itself stays Occupational Health's
    health_id = fields.Many2one(
        "fix.hse.health",
        string="Source Health Record",
        groups="cd_hse.group_occupational_health",
        ondelete="set null",
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By (Occupational Health)")
    migrated = fields.Boolean(help="Published from a health record that predates the split.")
    state = fields.Selection(
        [("current", "Current"), ("superseded", "Superseded")],
        required=True,
        default="current",
        index=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._CONTENT) | {"state"}

    @api.depends("employee_id", "status", "valid_from")
    def _compute_name(self):
        labels = dict(STATUSES)
        for rec in self:
            rec.name = "%s: %s (%s)" % (
                rec.employee_id.sudo().name or "",
                labels.get(rec.status, ""),
                rec.valid_from or "",
            )

    @api.constrains("status", "work_restriction", "valid_from", "valid_until")
    def _check_status(self):
        for rec in self:
            if rec.status == "restricted" and not (rec.work_restriction or "").strip():
                raise ValidationError("A restricted fitness status states the restriction.")
            if rec.valid_until and rec.valid_until < rec.valid_from:
                raise ValidationError("A fitness status ends after it starts.")

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise AccessError(
                "A fitness status is published by Occupational Health from a health record."
            )
        return super().create(vals_list)

    def unlink(self):
        if not self.env.su:
            raise AccessError("A fitness status is superseded, never deleted.")
        return super().unlink()

    @api.model
    def _fix_publish(
        self, employee, status, restriction, valid_from, valid_until, health=None, decided_by=None
    ):
        """The one way in: supersede the current status, publish the new one."""
        Status = self.sudo()._guarded()
        Status.search([("employee_id", "=", employee.id), ("state", "=", "current")]).write(
            {"state": "superseded"}
        )
        return Status.create(
            {
                "employee_id": employee.id,
                "company_id": employee.sudo().company_id.id or self.env.company.id,
                "status": status,
                "work_restriction": restriction or False,
                "valid_from": valid_from,
                "valid_until": valid_until or False,
                "health_id": health.id if health else False,
                "decided_by_id": decided_by.id if decided_by else False,
            }
        )


class HrEmployeeHse(models.Model):
    _inherit = "hr.employee"

    def _fix_fitness_status(self, on_date=None):
        """The current fitness status valid on `on_date` (sudo; status only)."""
        self.ensure_one()
        day = fields.Date.to_date(on_date) or fields.Date.context_today(self)
        return (
            self.env["fix.hse.fitness.status"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", self.id),
                    ("state", "=", "current"),
                    ("valid_from", "<=", day),
                    "|",
                    ("valid_until", "=", False),
                    ("valid_until", ">=", day),
                ],
                limit=1,
            )
        )

    def _fix_driving_licence(self, on_date=None):
        """(fix.driver, reason): the employee's licence record if it is valid
        on `on_date` (active, with a class and an expiry on or after the day),
        else an empty record and why (BRU-HSE-07)."""
        self.ensure_one()
        Driver = self.env["fix.driver"].sudo()
        day = fields.Date.to_date(on_date) or fields.Date.context_today(self)
        driver = Driver.search([("employee_id", "=", self.id)], limit=1)
        if not driver:
            return Driver, "%s has no driving licence on record" % self.sudo().name
        if driver.state != "active":
            return Driver, "the driving licence record of %s is %s" % (
                self.sudo().name,
                driver.state,
            )
        if not driver.license_class:
            return Driver, "the driving licence of %s records no class" % self.sudo().name
        if not driver.license_expiry:
            return Driver, "the driving licence of %s records no expiry" % self.sudo().name
        if driver.license_expiry < day:
            return Driver, "the driving licence of %s expired on %s" % (
                self.sudo().name,
                driver.license_expiry,
            )
        return driver, ""


class FixVehicleAssignmentLicence(models.Model):
    """BRU-HSE-07 / FR-HSE-019: a lapsed driving licence blocks vehicle-based
    work. A vehicle is not assigned to a technician whose licence is not
    valid on the assignment day."""

    _inherit = "fix.vehicle.assignment"

    def _fix_check_licence(self):
        for rec in self.sudo():
            if not rec.technician_id:
                continue
            licence, reason = rec.technician_id._fix_driving_licence(rec.date)
            if not licence:
                raise ValidationError("Vehicle assignment refused: %s (BRU-HSE-07)." % reason)

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs._fix_check_licence()
        return recs

    def write(self, vals):
        result = super().write(vals)
        if {"technician_id", "date"} & set(vals):
            self._fix_check_licence()
        return result
