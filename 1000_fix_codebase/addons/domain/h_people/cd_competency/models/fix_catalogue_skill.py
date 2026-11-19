# M37 capture audit, third pass (2026-11-19), FR-CAT-015 / BRU-CAT-06: a
# service declares the competency (skill profile) and, through it, the
# certification class a technician must hold; M02 and M31 gate dispatch on
# it. A repair operation cannot leave Draft without its skill profile.
# Declared here, not in cd_catalogue: the competency master is M22's, and
# cd_competency already depends on the catalogue.
from odoo import fields, models

OPERATION_TYPES = ("labour",)


class FixCatalogueItemSkill(models.Model):
    _inherit = "fix.catalogue.item"

    required_competency_id = fields.Many2one(
        "fix.competency",
        string="Required Skill Profile",
        ondelete="restrict",
        help="The M22 competency a technician needs to perform this service.",
    )
    requires_certification = fields.Boolean(
        string="Certified Technician Only",
        help="The technician must hold a valid certification of that competency, not only "
        "the skill.",
    )

    def _completeness_problems(self):
        problems = super()._completeness_problems()
        if self.item_type in OPERATION_TYPES and not self.required_competency_id:
            problems.append("its required skill profile (BRU-CAT-06)")
        if self.requires_certification and not self.required_competency_id:
            problems.append("the competency its certification is of (FR-CAT-015)")
        return problems
