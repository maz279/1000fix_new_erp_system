# res.partner extension — the party kernel's projection (P03-M05, M33).
# THE design rule: a SINGLE res.partner holds MULTIPLE roles simultaneously
# (fix.party.role) — customer, seller, vendor, rider are roles, never separate
# masters. This extension carries the kernel's Bengali-first fields and the
# language default the dispatcher and reports read.
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    name_bn = fields.Char(
        string="Name (Bengali)",
        help="DE-17/TR-07: authoritative in the bn locale; empty falls back to "
             "the Latin name — never machine-translated")
    preferred_language = fields.Selection(
        [("bn", "বাংলা (Bengali)"), ("en", "English")],
        string="Preferred Language", default="bn", required=True,
        help="MD-013: the notification language — Bengali is the default (PS-03)")
    role_ids = fields.One2many("fix.party.role", "partner_id", string="Party Roles")
    consent_ids = fields.One2many("fix.consent", "partner_id", string="Consent Records")
    hierarchy_parent_ids = fields.One2many(
        "fix.party.hierarchy", "child_id", string="Related Parties (as child)")
    hierarchy_child_ids = fields.One2many(
        "fix.party.hierarchy", "parent_id", string="Related Parties (as parent)")

    def _get_notification_language(self) -> str:
        """The dispatcher's language lookup: preferred_language, defaulting bn."""
        self.ensure_one()
        return self.preferred_language or "bn"
