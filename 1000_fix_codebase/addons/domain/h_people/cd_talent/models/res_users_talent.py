# res.users — who reads every M58 record (A09 audit M58-F7).
from odoo import models

TALENT_ALL_READERS = (
    "cd_talent.group_talent",
    "cd_talent.group_requisition_approver",
    "cd_talent.group_offer_approver",
    "cd_talent.group_background_verifier",
    "cd_entity_config.group_dofa_tier_4",
)


class ResUsersTalent(models.Model):
    _inherit = "res.users"

    def fix_talent_reads_all(self):
        """True for Recruitment and the M58 deciders, which work on every
        requisition and candidate; a Hiring Manager reaches only the
        requisitions that name them (and their candidates and plans).

        Used by the GLOBAL rules in fix_a09_talent_rules.xml: a group rule
        cannot narrow what the generated operating-unit rule already grants."""
        self.ensure_one()
        groups = [self.env.ref(x, raise_if_not_found=False) for x in TALENT_ALL_READERS]
        return any(g and g in self.sudo().all_group_ids for g in groups)
