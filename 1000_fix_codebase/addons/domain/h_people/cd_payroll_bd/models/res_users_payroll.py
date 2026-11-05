# cd_payroll_bd — who reads every payslip (A09 audit M56-8 / FR-PAY-051).
from odoo import models

PAYSLIP_ALL_READERS = (
    "cd_payroll_bd.group_payroll_officer",
    "cd_payroll_bd.group_payroll_release",
)


class ResUsersPayroll(models.Model):
    _inherit = "res.users"

    def fix_reads_all_payslips(self):
        """True for payroll and the disbursement releaser; everyone else reads
        only their own PUBLISHED payslip. Used by the GLOBAL payslip rule (the
        generated operating-unit group rule would OR-widen a group rule)."""
        self.ensure_one()
        groups = [self.env.ref(x, raise_if_not_found=False) for x in PAYSLIP_ALL_READERS]
        return any(g and g in self.sudo().all_group_ids for g in groups)
