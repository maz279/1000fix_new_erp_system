# fix.branch — operational branch, the OU isolation unit (P03-M04-T01).
# 51+ branches; every transactional model carries operating_unit_id (AS-03).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixBranch(models.Model):
    """An operational branch — the isolation unit for OU-based record rules."""
    _name = "fix.branch"
    _description = "Branch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "entity_id, code"
    _sql_constraints = [
        ("code_entity_unique", "unique(code, entity_id)", "Branch code must be unique within an entity"),
    ]

    code = fields.Char(string="Branch Code", required=True, size=10, tracking=True)
    name = fields.Char(string="Branch Name", required=True, tracking=True)
    name_bn = fields.Char(string="Branch Name (Bengali)",
                          help="Bengali branch name — DE-17")
    # AS-03: company_id (derived from entity's company)
    company_id = fields.Many2one(related="entity_id.company_id", store=True,
                                 string="Company")
    entity_id = fields.Many2one("fix.entity", string="Entity", required=True,
                                ondelete="cascade")
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", required=True,
        ondelete="restrict",
        help="AS-03: every transactional model carries operating_unit_id. "
             "This is the isolation mechanism OCA operating-unit provides.")
    zone_id = fields.Many2one("fix.zone", string="Dispatch Zone",
                              help="Consumed by M02 dispatch in Phase 5")
    address_id = fields.Many2one("fix.bd.address", string="Address",
                                 help="Bangladesh address hierarchy")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    manager_id = fields.Many2one("hr.employee", string="Branch Manager")
    active = fields.Boolean(default=True, tracking=True)
    calendar_id = fields.Many2one("fix.working.calendar", string="Working Calendar",
                                  help="M02's W2 availability stub reads this")

    @api.onchange("entity_id")
    def _onchange_entity(self):
        if self.entity_id and self.entity_id.company_id:
            return {"domain": {"operating_unit_id": [
                ("company_id", "=", self.entity_id.company_id.id)]}}
