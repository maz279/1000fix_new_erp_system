# fix.zone — dispatch zone grouping branches for M02 (P03-M04-T03).
# Zones carry geofences (Phase 5 dispatch consumes both); branches point at
# their zone (fix.branch.zone_id). AS-03 note: a zone is master data shared
# across OUs — company scoping comes from its branches, not from the zone.
from odoo import fields, models


class FixZone(models.Model):
    """A dispatch zone: a geographic grouping of branches for field service."""
    _name = "fix.zone"
    _description = "Dispatch Zone"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint('UNIQUE (code)', 'Zone code must be unique')

    name = fields.Char(string="Zone Name", required=True, tracking=True)
    name_bn = fields.Char(string="Zone Name (Bengali)", help="DE-17 Bengali-first")
    code = fields.Char(string="Zone Code", required=True, size=8)
    description = fields.Char(string="Description")
    active = fields.Boolean(default=True, tracking=True)
    branch_ids = fields.One2many("fix.branch", "zone_id", string="Branches")
    geofence_ids = fields.One2many("fix.geofence", "zone_id", string="Geofences")

    def name_get(self):
        # Bengali name in the bn locale, Latin fallback — never machine-translated.
        return [(zone.id, zone.name_bn or zone.name) for zone in self]
