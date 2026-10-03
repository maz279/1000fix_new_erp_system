# fix.entity — legal entity model on res.company (P03-M04-T01).
# One fix.entity per legal entity; branches reference it for isolation.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixEntity(models.Model):
    """A legal entity within the 1000FiX group (M65 multi-entity/multi-country)."""
    _name = "fix.entity"
    _description = "Legal Entity"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint('UNIQUE (code)', 'Entity code must be unique')

    # AS-02: chatter mixins mandatory
    # AS-03: company_id + operating_unit_id on transactional models
    # (fix.entity is a master, not transactional, but carries company_id for OU)

    code = fields.Char(string="Entity Code", required=True, size=10, tracking=True,
                       help="Short unique code, e.g. 1000FIX-BD")
    legal_name = fields.Char(string="Legal Name", required=True, tracking=True)
    legal_name_bn = fields.Char(string="Legal Name (Bengali)",
                                help="Bengali legal name — DE-17 Bengali-first")
    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 ondelete="restrict")
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Primary Operating Unit",
        help="The OU for this entity's headquarters operations (AS-03)")
    country_id = fields.Many2one("res.country", string="Country", required=True,
                                 default=lambda self: self.env.ref("base.bd"))
    currency_id = fields.Many2one("res.currency", string="Currency",
                                  default=lambda self: self.env.ref("base.BDT"))
    active = fields.Boolean(default=True, tracking=True)
    branch_ids = fields.One2many("fix.branch", "entity_id", string="Branches")
    branch_count = fields.Integer(compute="_compute_branch_count", store=True)

    _company_unique = models.Constraint("UNIQUE (company_id)",
        "Each res.company maps to exactly one fix.entity")

    @api.depends("branch_ids")
    def _compute_branch_count(self):
        for rec in self:
            rec.branch_count = len(rec.branch_ids)

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if not rec.code.isupper():
                raise ValidationError("Entity code must be uppercase.")
