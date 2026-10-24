# fix_metric_registry — M62: data catalogue, lineage, DQ, stewardship (P11-M02).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixDataEntity(models.Model):
    """M62: the data catalogue over 1,335 owned entities (DA-002).
    Every entity has an owner, a classification, and a retention."""

    _name = "fix.data.entity"
    _description = "Data Entity (Catalogue)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, index=True)
    entity_type = fields.Selection(
        [
            ("table", "Database Table"),
            ("api", "API Resource"),
            ("event", "Event Stream"),
            ("report", "Report/KPI"),
            ("document", "Document Type"),
        ],
        required=True,
        default="table",
    )
    owner_module = fields.Char(
        string="Owning Module", help="The cd_* module that owns this entity (FF-27)"
    )
    steward_id = fields.Many2one(
        "hr.employee", string="Data Steward", help="DA-003: named people, not named roles"
    )
    classification = fields.Selection(
        [
            ("public", "Public"),
            ("internal", "Internal"),
            ("confidential", "Confidential"),
            ("residency_classified", "Residency-Classified (S3)"),
        ],
        required=True,
        default="internal",
        help="DA-005 classification; S3 entities must NEVER appear in the "
        "analytical warehouse (NFR-086c)",
    )
    retention_policy = fields.Char(
        string="Retention Policy", help="DA-006: how long this data lives"
    )
    description = fields.Text()

    @api.constrains("classification", "entity_type")
    def _check_warehouse_safety(self):
        """NFR-086c: no residency-classified data in the analytical store."""
        for rec in self:
            if (
                rec.classification == "residency_classified"
                and rec.entity_type == "table"
                and "warehouse" in (rec.name or "").lower()
            ):
                raise UserError(
                    "NFR-086c: residency-classified data must not appear "
                    "in the analytical warehouse"
                )


class FixDataLineage(models.Model):
    """M62: data-lineage tracking from source to dashboard (DA-003).
    A KPI whose lineage is unknown is a KPI nobody trusts."""

    _name = "fix.data.lineage"
    _description = "Data Lineage"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    source_entity_id = fields.Many2one(
        "fix.data.entity", string="Source", required=True, ondelete="cascade"
    )
    target_entity_id = fields.Many2one(
        "fix.data.entity", string="Target", required=True, ondelete="cascade"
    )
    transformation = fields.Text(
        string="Transformation Logic",
        help="What happens between source and target (the dbt model, the "
        "event handler, the aggregation)",
    )
    lineage_order = fields.Integer(
        string="Order", help="The position in the lineage chain (1=source, N=dashboard)"
    )


class FixDataQualityRule(models.Model):
    """M62: DA-008 data quality monitoring with thresholds."""

    _name = "fix.data.quality.rule"
    _description = "Data Quality Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    entity_id = fields.Many2one(
        "fix.data.entity", string="Entity", required=True, ondelete="cascade"
    )
    rule_type = fields.Selection(
        [
            ("completeness", "Completeness (% non-null)"),
            ("uniqueness", "Uniqueness (no duplicates)"),
            ("timeliness", "Timeliness (freshness)"),
            ("accuracy", "Accuracy (value match)"),
            ("consistency", "Consistency (cross-source)"),
        ],
        required=True,
        default="completeness",
    )
    threshold = fields.Float(string="Threshold %", default=95.0, help="Below this, the rule fires")
    active = fields.Boolean(default=True)
    last_checked = fields.Datetime(readonly=True)
    last_result = fields.Float(string="Last Result %", readonly=True)
    state = fields.Selection(
        [("passing", "Passing"), ("failing", "Failing")],
        default="passing",
        required=True,
        tracking=True,
    )

    def action_check(self, result_pct):
        """Run the check: below threshold = failing + alert event."""
        for rec in self:
            failing = result_pct < rec.threshold
            rec.write(
                {
                    "last_checked": fields.Datetime.now(),
                    "last_result": result_pct,
                    "state": "failing" if failing else "passing",
                }
            )
            if failing:
                publish(
                    self.env,
                    "data_quality.failing",
                    "fix.data.quality.rule",
                    rec.id,
                    {
                        "entity": rec.entity_id.name,
                        "result": result_pct,
                        "threshold": rec.threshold,
                    },
                )
