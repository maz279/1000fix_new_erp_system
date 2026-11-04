# cd_demand_plan 19.0.0.2.0 (A06 audit M43-3 / M43-9): forecasts typed before
# the remediation carried method "moving_average" / source "history" although
# nothing computed them. forecast_qty is now computed (statistical value or a
# planner override with a rationale), so every forecast that was never
# computed from M15 history keeps its typed quantity as an explicit planner
# override and is relabelled "manual".
from odoo import SUPERUSER_ID, api

RATIONALE = (
    "Typed before the A06 remediation (no history computation existed); kept as a planner override."
)


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute(
        "SELECT id, COALESCE(forecast_qty, 0) FROM fix_demand_forecast WHERE computed_on IS NULL"
    )
    Forecast = env["fix.demand.forecast"]
    for fid, qty in cr.fetchall():
        Forecast.browse(fid).write(
            {"has_override": True, "override_qty": max(qty, 0.0), "override_rationale": RATIONALE}
        )
