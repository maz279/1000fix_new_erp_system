# fix.bd.address extension — the party-side address (M33, FR-CPM-014/016).
# The platform model (cd_entity_config) carries the governed BD parts; M33
# adds what the party master needs: the OWNING party, the use tag, and GPS
# coordinates captured from the app or map picker.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixBdAddressExt(models.Model):
    _inherit = "fix.bd.address"

    party_id = fields.Many2one(
        "res.partner",
        string="Party",
        index=True,
        ondelete="cascade",
        help="FR-CPM-014: unlimited tagged addresses per party",
    )
    address_tag = fields.Selection(
        [
            ("home", "Home"),
            ("office", "Office"),
            ("factory", "Factory"),
            ("branch", "Branch"),
            ("site", "Site"),
        ],
        string="Tag",
        help="The purpose this address serves for the party",
    )
    latitude = fields.Float(
        string="Latitude",
        digits=(10, 7),
        help="FR-CPM-016: GPS captured from the mobile app or map picker",
    )
    longitude = fields.Float(
        string="Longitude",
        digits=(10, 7),
    )

    @api.constrains("latitude", "longitude")
    def _check_coordinates(self):
        for address in self:
            if address.latitude and not -90 <= address.latitude <= 90:
                raise ValidationError("Latitude must be between -90 and 90")
            if address.longitude and not -180 <= address.longitude <= 180:
                raise ValidationError("Longitude must be between -180 and 180")
