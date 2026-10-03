# fix.isolation.tier — the six data isolation tiers T0-T5 (P03-M02-T03).
# Each tier carries the record-rule domain that enforces it; every tier is
# negative-tested per role (DoD-07).
from odoo import fields, models


class FixIsolationTier(models.Model):
    """A data isolation tier (05-04 section 4, AR-001 section 8.2).

    T0 = public (no restriction)
    T1 = internal (all employees)
    T2 = branch-scoped (operating_unit_id)
    T3 = role-scoped (fix.role membership)
    T4 = management zone Z5 (no standing access, privileged sessions recorded)
    T5 = residency-classified (Z4 only, step-up auth, per-read logged)
    """
    _name = "fix.isolation.tier"
    _description = "Data Isolation Tier"
    _order = "code"
    _sql_constraints = [
        ("code_unique", "unique(code)", "Tier code must be unique"),
    ]

    code = fields.Selection(
        [("T0", "T0 - Public"), ("T1", "T1 - Internal"),
         ("T2", "T2 - Branch-scoped"), ("T3", "T3 - Role-scoped"),
         ("T4", "T4 - Management (Z5)"), ("T5", "T5 - Residency-classified (Z4)")],
        required=True, string="Tier")
    name = fields.Char(compute="_compute_name", store=True)
    description = fields.Text()
    record_rule_domain = fields.Char(
        string="Record Rule Domain",
        help="The domain filter that enforces this tier; empty for T0 (no filter). "
             "T2: [('operating_unit_id','in',user.branch_ids.operating_unit_id.ids)]")
    requires_step_up = fields.Boolean(
        default=False,
        help="T5 only: human access requires step-up authentication (NFR-065)")
    requires_audit = fields.Boolean(
        default=False,
        help="T4/T5: every access is logged (NFR-070/SC-010)")
    role_ids = fields.Many2many("fix.role", string="Roles with Access")

    def _compute_name(self):
        mapping = dict(self._fields["code"].selection)
        for rec in self:
            rec.name = mapping.get(rec.code, rec.code)
