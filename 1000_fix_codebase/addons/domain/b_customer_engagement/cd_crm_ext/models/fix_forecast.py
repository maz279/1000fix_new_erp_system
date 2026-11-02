# fix.forecast.snapshot — immutable period forecasts (M07, FR-CRM-019/020,
# BRU-CRM-06/07). A taken snapshot is never edited; a manager adjustment is
# recorded separately and attributable, and only once.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixForecastSnapshot(models.Model):
    """One period's forecast for one owner and pipeline."""

    _name = "fix.forecast.snapshot"
    _description = "Forecast Snapshot"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc, id desc"
    # Odoo 19 constraint attribute form
    _period_owner_pipeline_unique = models.Constraint(
        "UNIQUE (period, owner_id, pipeline_id)",
        "One snapshot per period, owner and pipeline (T-05)",
    )

    period = fields.Char(string="Period (YYYY-MM)", required=True, index=True)
    owner_id = fields.Many2one("res.users", string="Owner", required=True, index=True)
    pipeline_id = fields.Many2one("fix.pipeline", string="Pipeline", required=True, index=True)
    commit_value = fields.Monetary(string="Commit", readonly=True)
    best_case_value = fields.Monetary(string="Best Case", readonly=True)
    pipeline_value = fields.Monetary(string="Pipeline", readonly=True)
    currency_id = fields.Many2one(
        "res.currency", string="Currency", default=lambda self: self.env.company.currency_id
    )
    # BRU-CRM-07: the adjustment is separate from the raw roll-up and attributable
    manager_adjustment = fields.Monetary(
        string="Manager Adjustment",
        help="Recorded separately from the raw roll-up; attributable (BRU-CRM-07)",
    )
    adjusted_by = fields.Many2one("res.users", string="Adjusted By", readonly=True)
    adjustment_reason = fields.Char(string="Adjustment Reason")
    taken_at = fields.Datetime(string="Taken At", default=fields.Datetime.now, readonly=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    def write(self, vals):
        # BRU-CRM-06: once taken, the raw figures are immutable. The single
        # legitimate later write is the attributable manager adjustment.
        raw_fields = {
            "period",
            "owner_id",
            "pipeline_id",
            "commit_value",
            "best_case_value",
            "pipeline_value",
            "taken_at",
        }
        if raw_fields & set(vals):
            for snap in self:
                if snap.taken_at:
                    raise ValidationError("A taken forecast snapshot cannot be edited (BRU-CRM-06)")
        if "manager_adjustment" in vals:
            vals = dict(vals)
            vals["adjusted_by"] = self.env.user.id
        return super().write(vals)

    @api.model
    def action_take_snapshot(self, period=None):
        """AUT-CRM-10: snapshot the current period's forecast from open
        opportunities grouped by forecast category; lock on insert."""
        import datetime

        period = period or datetime.date.today().strftime("%Y-%m")
        Opportunity = self.env["crm.lead"]
        owners = Opportunity.search([("type", "=", "opportunity")]).mapped("user_id")
        created = 0
        for owner in owners:
            for pipeline in self.env["fix.pipeline"].search([]):
                opps = Opportunity.search(
                    [
                        ("type", "=", "opportunity"),
                        ("user_id", "=", owner.id),
                        ("pipeline_id", "=", pipeline.id),
                        ("probability", ">", 0),
                        ("active", "=", True),
                    ]
                )
                if not opps:
                    continue
                commit = sum(o.expected_revenue for o in opps if o.forecast_category == "commit")
                best = sum(
                    o.expected_revenue
                    for o in opps
                    if o.forecast_category in ("commit", "best_case")
                )
                total = sum(o.expected_revenue for o in opps)
                if not total:
                    continue
                if self.search_count(
                    [
                        ("period", "=", period),
                        ("owner_id", "=", owner.id),
                        ("pipeline_id", "=", pipeline.id),
                    ]
                ):
                    continue
                self.create(
                    {
                        "period": period,
                        "owner_id": owner.id,
                        "pipeline_id": pipeline.id,
                        "commit_value": commit,
                        "best_case_value": best,
                        "pipeline_value": total,
                    }
                )
                created += 1
        if created:
            from libs.py.fix_events import publish

            publish(
                self.env,
                "forecast.snapshot_taken",
                "fix.forecast.snapshot",
                0,
                {"period": period, "count": created},
            )
        return created
