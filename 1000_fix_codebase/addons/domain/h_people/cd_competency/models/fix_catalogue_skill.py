# M37 capture audit, third pass (2026-11-19), FR-CAT-015 / BRU-CAT-06: a
# service declares the competency (skill profile) and, through it, the
# certification class a technician must hold; M02 and M31 gate dispatch on
# it. A repair operation cannot leave Draft without its skill profile.
# Declared here, not in cd_catalogue: the competency master is M22's, and
# cd_competency already depends on the catalogue.
#
# A09 R2 (M22-F10): the gate only fired for item_type 'labour', and the
# estate's repair operations are typed 'service' (76 approved on the real
# snapshot, 0 with a required competency, 0 labour items) — BRU-CAT-06 was
# dead on real data. 'service' now declares its skill profile too. The rule
# applies at the Draft -> In Review -> Active transitions only, never
# retroactively: the 76 approved items are untouched until they are revised.
from odoo import fields, models

OPERATION_TYPES = ("labour", "service")


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
