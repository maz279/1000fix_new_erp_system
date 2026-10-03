# fix.country.pack — Bangladesh reference data pack (P03-M04-T06, AF-09).
# The 8 divisions, 64 districts and moon-dependent public holidays are DATA,
# not code (05-06 §9): they load as pack lines so a new district or a revised
# holiday date is a data change, never a deployment. The W1 subset ships the
# structure; the full 64-district pack is MD-005 master data (AF-09-funded).
from odoo import fields, models


class FixCountryPack(models.Model):
    """The Bangladesh reference-data pack: divisions, districts, holidays."""
    _name = "fix.country.pack"
    _description = "Country Data Pack"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _sql_constraints = [
        ("code_unique", "unique(code)", "Pack code must be unique"),
    ]

    name = fields.Char(string="Pack Name", required=True, tracking=True)
    code = fields.Char(string="Pack Code", required=True, size=16,
                       help="e.g. BD-DIV-2026, BD-HOL-2026")
    kind = fields.Selection(
        [("divisions", "Divisions & Districts"), ("holidays", "Public Holidays"),
         ("postcodes", "Postcodes")],
        string="Kind", required=True, default="divisions")
    version = fields.Char(string="Version", required=True, default="2026.1")
    loaded_at = fields.Datetime(string="Loaded At", readonly=True)
    line_ids = fields.One2many("fix.country.pack.line", "pack_id", string="Lines")
    active = fields.Boolean(default=True)

    def action_load(self):
        """Mark the pack loaded — the actual rows are master data (AF-09),
        loaded by the data pipeline, never hard-coded in this module."""
        self.write({"loaded_at": fields.Datetime.now()})
        return True


class FixCountryPackLine(models.Model):
    """One entry of a data pack — a division, district, holiday or postcode."""

    _name = "fix.country.pack.line"
    _description = "Country Data Pack Line"

    pack_id = fields.Many2one("fix.country.pack", required=True, ondelete="cascade")
    parent_code = fields.Char(string="Parent Code",
                              help="District lines point at their division code")
    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name (English)", required=True)
    name_bn = fields.Char(string="Name (Bengali)", required=True,
                          help="DE-17: Bengali is not optional for place names")
    date_value = fields.Date(string="Date (holiday packs)")
    _sql_constraints = [
        ("pack_code_unique", "unique(pack_id, code)",
         "Code appears once per pack"),
    ]
