# fix.retention.class — the retention schedule model (P03-M07-T04/T05).
# Loaded as CONTENT (LG-009), not as a M60 dependency. The retention policy
# is needed; the GRC module is not.
from odoo import fields, models


class FixRetentionClass(models.Model):
    """A retention classification: how long documents of this class are kept.

    The retention schedule is loaded from content (db/seeds or a CSV import)
    per LG-009 — the GRC module (M60) does NOT govern this model.
    """
    _name = "fix.retention.class"
    _description = "Retention Class"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M24",
        "form": "Retention Policy",
        "fields": ["code", "name", "retention_years", "expiry_action", "description",
                   "regulatory_basis", "document_types"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint('UNIQUE (code)', 'Retention code must be unique')

    code = fields.Char(required=True, size=10,
                       help="Short code, e.g. FIN-7Y, HR-5Y, CUST-3Y")
    name = fields.Char(required=True, tracking=True)
    description = fields.Text()

    retention_years = fields.Integer(
        string="Retention Period (years)", required=True, default=7,
        help="How long documents of this class are retained from creation")
    regulatory_basis = fields.Char(
        string="Regulatory Basis",
        help="Which law or policy mandates this retention period, e.g. "
             "'Income Tax Ordinance 1984 §184' or 'PDPA 2026 §33'")

    # What happens at expiry
    expiry_action = fields.Selection(
        [("destroy", "Destroy (secure wipe)"),
         ("review", "Require Manual Review Before Destruction"),
         ("archive", "Archive to Cold Storage")],
        default="review", required=True,
        help="The action taken when retention expires")

    # Which document types use this class
    document_types = fields.Char(
        string="Applicable Document Types",
        help="Comma-separated list of fix.document document_type values")

    active = fields.Boolean(default=True)
