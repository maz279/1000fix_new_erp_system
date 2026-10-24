# fix.brand extension — the P08 brand partner identity link (R01 re-audit 2026-10-22).
# The brand partner API resolves the acting brand from the authenticated user
# through this link; a request parameter never selects the brand.
from odoo import fields, models


class FixBrandApiUsers(models.Model):
    _inherit = "fix.brand"

    api_user_ids = fields.Many2many(
        "res.users",
        "fix_brand_api_user_rel",
        "brand_id",
        "user_id",
        string="Brand Partner Users",
        help="P08: the users (portal accounts / integration API keys) acting for this brand "
        "on the brand partner API. They see and decide only this brand's claims.",
    )
