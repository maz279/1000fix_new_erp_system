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
    is_default = fields.Boolean(
        string="Default for this Purpose",
        help="FR-CPM-014: the party's nominated address for this tag (one per tag)",
    )

    @api.constrains("party_id", "address_tag", "is_default")
    def _check_one_default_per_tag(self):
        for address in self.filtered(lambda a: a.is_default and a.party_id):
            clash = self.search_count(
                [
                    ("id", "!=", address.id),
                    ("party_id", "=", address.party_id.id),
                    ("address_tag", "=", address.address_tag),
                    ("is_default", "=", True),
                ]
            )
            if clash:
                raise ValidationError(
                    "%s already has a default %s address. Clear that one first."
                    % (address.party_id.display_name, address.address_tag or "untagged")
                )

    @api.constrains("latitude", "longitude")
    def _check_coordinates(self):
        for address in self:
            if address.latitude and not -90 <= address.latitude <= 90:
                raise ValidationError("Latitude must be between -90 and 90")
            if address.longitude and not -180 <= address.longitude <= 180:
                raise ValidationError("Longitude must be between -180 and 180")
