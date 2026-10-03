# fix.device.model — the device model master (P03-M06-T05).
# Referenced by M17's device registry; must exist before devices are registered.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixDeviceModel(models.Model):
    """A device model: e.g. 'Samsung Galaxy S24 Ultra' under brand 'Samsung'.

    M17's device registry references this — a physical device is an instance
    of a fix.device.model. Without the master, M17 cannot register devices.
    """
    _name = "fix.device.model"
    _description = "Device Model"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "brand_id, name"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _brand_name_unique = models.Constraint('UNIQUE (brand_id, name)', 'Device model must be unique within a brand')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True,
                               ondelete="restrict", index=True)
    name = fields.Char(required=True, tracking=True,
                       help="Model name, e.g. 'Galaxy S24 Ultra'")
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    model_code = fields.Char(string="Model Code",
                             help="Manufacturer's model code, e.g. SM-S928B")
    device_type = fields.Selection(
        [("smartphone", "Smartphone"), ("tablet", "Tablet"),
         ("laptop", "Laptop"), ("desktop", "Desktop"),
         ("tv", "Television"), ("appliance_washer", "Washing Machine"),
         ("appliance_fridge", "Refrigerator"), ("appliance_ac", "Air Conditioner"),
         ("appliance_microwave", "Microwave"), ("other", "Other")],
        required=True, default="smartphone")
    release_year = fields.Integer()
    discontinued = fields.Boolean(
        default=False, tracking=True,
        help="True if the manufacturer no longer supports this model")

    # Parts/warranty metadata
    parts_available = fields.Boolean(
        default=True, tracking=True,
        help="Whether spare parts are still obtainable for this model")
    warranty_months_new = fields.Integer(
        string="New Warranty (months)",
        help="Standard manufacturer warranty period")
    active = fields.Boolean(default=True, tracking=True)

    @api.constrains("release_year")
    def _check_year(self):
        for rec in self:
            if rec.release_year and (rec.release_year < 1990 or rec.release_year > 2100):
                raise ValidationError(f"Release year {rec.release_year} is out of range.")
