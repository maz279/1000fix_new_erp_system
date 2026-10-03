# fix.branch HR extension (P03-M08) — the employee-grade branch manager link.
# cd_entity_config keeps manager_id -> res.users because the PLATFORM layer
# cannot depend on Odoo hr (FF-17; live-install finding). The hr.employee
# pointer lives HERE, where hr is a declared dependency.
from odoo import fields, models


class FixBranchEmployeeExt(models.Model):
    _inherit = "fix.branch"

    employee_manager_id = fields.Many2one(
        "hr.employee", string="Branch Manager (Employee)",
        help="HR-grade manager record; manager_id (res.users) is the "
             "accountable login, this is the employment record.")
