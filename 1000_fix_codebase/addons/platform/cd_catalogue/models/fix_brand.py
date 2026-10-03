# fix.brand — the brand master (P03-M06-T05).
# 17+ brand partners; the master must exist before devices are registered (M17).
from odoo import api, fields, models


class FixBrand(models.Model):
    """A brand partner (Samsung, Apple, Xiaomi, etc.).

    The brand master is referenced by:
    - fix.catalogue.item (which brand's products this item covers)
    - fix.device.model (M17 — which brand makes this device)
    - M08 agreements (brand authorisation terms)
    """
    _name = "fix.brand"
    _description = "Brand Master"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _name_unique = models.Constraint('UNIQUE (name)', 'Brand name must be unique')

    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    code = fields.Char(string="Brand Code", required=True, size=10,
                       help="Short code, e.g. SAMS, APPL")
    logo = fields.Binary()
    website = fields.Char()
    support_url = fields.Char(string="Support Portal URL")
    authorised = fields.Boolean(
        string="1000FiX Authorised", default=False, tracking=True,
        help="Whether 1000FiX is currently brand-authorised for repairs")
    authorisation_expiry = fields.Date(
        string="Authorisation Expiry",
        help="If lapsed without escalation, work requiring this brand's "
             "authorisation cannot be performed (BRU-PCM-08)")
    device_model_ids = fields.One2many("fix.device.model", "brand_id",
                                       string="Device Models")
    model_count = fields.Integer(compute="_compute_model_count", store=True)
    active = fields.Boolean(default=True, tracking=True)

    @api.depends("device_model_ids")
    def _compute_model_count(self):
        for rec in self:
            rec.model_count = len(rec.device_model_ids)
