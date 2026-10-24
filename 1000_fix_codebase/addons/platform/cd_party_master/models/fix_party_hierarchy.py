# fix.party.hierarchy — party-to-party relations (P03-M05, M33).
# Households, corporate groups, guarantor links: ONE res.partner may be
# related to another for a NAMED reason with a validity window. The dedup
# engine (M64) reads hierarchies so a merge never orphans a relation.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixPartyHierarchy(models.Model):
    """A named, dated relation between two parties."""

    _name = "fix.party.hierarchy"
    _description = "Party Hierarchy"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    parent_id = fields.Many2one(
        "res.partner", string="Parent Party", required=True, ondelete="cascade", index=True
    )
    child_id = fields.Many2one(
        "res.partner", string="Child Party", required=True, ondelete="cascade", index=True
    )
    relation_type = fields.Selection(
        [
            ("household", "Household Member"),
            ("corporate", "Corporate Group"),
            ("guarantor", "Guarantor"),
            ("care_of", "Care-Of Address"),
        ],
        string="Relation",
        required=True,
        default="household",
    )
    date_from = fields.Date(string="Since", default=fields.Date.today)
    date_to = fields.Date(
        string="Until",
        help="Empty = current — MIG-03: legacy relations " "close with a date, never a delete",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _parent_child_type_unique = models.Constraint(
        "UNIQUE (parent_id, child_id, relation_type)",
        "The same relation between the same parties exists once",
    )

    @api.constrains("parent_id", "child_id")
    def _check_no_self(self):
        for link in self:
            if link.parent_id == link.child_id:
                raise ValidationError("A party cannot relate to itself")
