# res.users — who reads every HSE record (A09 audit M59-F2/F14).
from odoo import models

HSE_ALL_READERS = (
    "cd_hse.group_hse_officer",
    "cd_hse.group_statutory_notifier",
    "cd_hse.group_injury_compensation_approver",
)
OCC_HEALTH = "cd_hse.group_occupational_health"


class ResUsersHse(models.Model):
    _inherit = "res.users"

    def fix_hse_reads_all(self):
        """True for the HSE roles, which work on every incident, register
        entry and lone-worker session; everyone else reaches their own.

        Used by the GLOBAL rules in fix_a09_hse_rules.xml: a group rule cannot
        narrow what the generated operating-unit rule already grants."""
        self.ensure_one()
        groups = [self.env.ref(x, raise_if_not_found=False) for x in HSE_ALL_READERS]
        return any(g and g in self.sudo().all_group_ids for g in groups)

    def fix_hse_reads_fitness(self):
        """The HSE roles and Occupational Health read every fitness status;
        everyone else reads their own and their direct reports' (round 2)."""
        self.ensure_one()
        oh = self.env.ref(OCC_HEALTH, raise_if_not_found=False)
        return self.fix_hse_reads_all() or bool(oh and oh in self.sudo().all_group_ids)
