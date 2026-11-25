# fix.brand extension — the P08 brand partner identity link (R01 re-audit 2026-10-22).
# The brand partner API resolves the acting brand from the authenticated user
# through this link; a request parameter never selects the brand.
#
# A04 ERP audit M09-F1 / X4 (20 Nov 2026): the OEM claim receivable needs the
# brand's BILLING partner. fix.brand (M37 catalogue data) had none, so the
# warranty_claim.decided hand-off looked for a res.partner whose ref equals
# the brand code - 0 of fix_real's 161 brands matched and every receivable
# dead-lettered. partner_id is that link (kept here, so the catalogue module
# is untouched). Creating the 161 OEM partners is master data the owner
# approves: action_create_billing_partner does it, one brand at a time, for a
# system administrator only; nothing runs it on upgrade.
from odoo import fields, models
from odoo.exceptions import AccessError, UserError


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
    partner_id = fields.Many2one(
        "res.partner",
        string="OEM Billing Partner",
        index=True,
        ondelete="restrict",
        help="The legal entity the brand's warranty claims are invoiced to (M20 OEM "
        "receivable). Without it an approved claim raises no receivable.",
    )

    def billing_partner(self):
        """The OEM billing partner of this brand: its partner link, else the
        one res.partner whose ref is the brand code (the legacy key). Empty
        when neither resolves to exactly one partner."""
        self.ensure_one()
        if self.partner_id:
            return self.partner_id
        if not self.code:
            return self.env["res.partner"]
        found = self.env["res.partner"].sudo().search([("ref", "=", self.code)], limit=2)
        return found if len(found) == 1 else self.env["res.partner"]

    def action_create_billing_partner(self):
        """Create the OEM billing partner of each brand that has none. Master
        data the owner approves (M09-F1): a system administrator runs it, and
        it never runs on install or upgrade."""
        if not self.env.su and not self.env.user.has_group("base.group_system"):
            raise AccessError(
                "Creating OEM billing partners is master data the owner approves: a system "
                "administrator runs it."
            )
        Partner = self.env["res.partner"].sudo()
        for brand in self:
            if brand.partner_id:
                continue
            if not (brand.code or "").strip():
                raise UserError("Brand %s has no code to key its billing partner." % brand.name)
            existing = Partner.search([("ref", "=", brand.code)], limit=2)
            if len(existing) > 1:
                raise UserError(
                    "Brand %s: %d partners carry the ref %s; link the right one by hand."
                    % (brand.name, len(existing), brand.code)
                )
            partner = existing or Partner.create(
                {"name": brand.name, "ref": brand.code, "is_company": True}
            )
            brand.sudo().write({"partner_id": partner.id})
        return True
