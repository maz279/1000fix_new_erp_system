# fix.bd.address — Bangladesh address hierarchy (P03-M04-T06, BN-007 §4).
# Division -> district -> upazila/thana -> union/ward -> street/house, postcode
# last — the INVERSE of Western order. The parts are validated against the
# country pack (fix.country.pack); rendering joins them in this exact order.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixBdAddress(models.Model):
    """A Bangladesh address stored as its governed parts, not one free string."""
    _name = "fix.bd.address"
    _description = "Bangladesh Address"

    division = fields.Char(string="Division", required=True)
    division_bn = fields.Char(string="Division (Bengali)")
    district = fields.Char(string="District", required=True)
    district_bn = fields.Char(string="District (Bengali)")
    upazila = fields.Char(string="Upazila/Thana")
    upazila_bn = fields.Char(string="Upazila/Thana (Bengali)")
    union_or_ward = fields.Char(string="Union/Ward")
    street = fields.Char(string="Street/Road")
    house = fields.Char(string="House/Building")
    postcode = fields.Char(string="Postcode", size=4,
                           help="Bangladesh postcodes are 4 digits")
    landmark = fields.Char(
        string="Landmark",
        help="Field dispatch relies on landmarks; the GPS geocode lives on the geofence, not here")

    @api.constrains("postcode")
    def _check_postcode(self):
        for address in self:
            if address.postcode and not (address.postcode.isdigit()
                                         and len(address.postcode) == 4):
                raise ValidationError("Bangladesh postcode must be exactly 4 digits")

    def format_bn(self) -> str:
        """BN-007 §4 — joined in Bangladeshi order with Bengali part names."""
        parts = [
            f"বাড়ি {self.house}" if self.house else "",
            f"রোড {self.street}" if self.street else "",
            self.upazila_bn or self.upazila or "",
            self.district_bn or self.district,
        ]
        line = ", ".join(p for p in parts if p)
        if self.postcode:
            line += f" {self.postcode}"
        return line

    def name_get(self):
        return [(address.id, address.format_bn() or address.district) for address in self]
