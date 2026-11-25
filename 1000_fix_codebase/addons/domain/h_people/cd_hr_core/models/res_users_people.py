# res.users — who may read every employee's people data (A09 audit A5).
from odoo import models

# Roles that work on the whole workforce. Payroll's groups are named here
# rather than in cd_payroll_bd so the privacy rules below need no reverse
# dependency; a group that is not installed simply grants nothing.
PEOPLE_ALL_READERS = (
    "hr.group_hr_user",
    "cd_hr_core.group_hr_officer",
    "cd_payroll_bd.group_payroll_officer",
    "cd_payroll_bd.group_payroll_manager",
)


class ResUsersPeople(models.Model):
    _inherit = "res.users"

    def fix_reads_all_people(self):
        """True when this user reads every employee's contract and performance
        record; everyone else reads their own and their direct reports'.

        Used by the GLOBAL privacy rules (fix_a09_privacy_rules.xml): a group
        rule cannot narrow what the generated operating-unit rule on the same
        group already grants, because group rules combine with OR."""
        self.ensure_one()
        groups = [self.env.ref(x, raise_if_not_found=False) for x in PEOPLE_ALL_READERS]
        return any(g and g in self.sudo().all_group_ids for g in groups)
