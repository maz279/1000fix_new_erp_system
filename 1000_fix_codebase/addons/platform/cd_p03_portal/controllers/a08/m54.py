# A08 · M54 Costing, Budget & FP&A — models the generic workspace screens may read,
# the workflow methods they may call (/p03/model/records, /p03/model/action),
# the computed table reports (/p03/model/report) and the module KPI tiles.
# Each SURFACES entry: model -> {"order", "limit", "actions"}. Reads also need
# the user's own read access on the model (accounting groups apply). Every
# report reads through fix.fpa.engine (cd_fpa) with the caller's env.
from odoo import fields
from odoo.exceptions import UserError

SURFACES = {
    "fix.budget": {
        "order": "fiscal_year desc, id desc",
        "limit": 100,
        "actions": {"action_refresh_actuals"},
    },
    "fix.budget.version": {
        "order": "date_from desc, id desc",
        "limit": 100,
        "actions": {
            "action_submit",
            "action_approve",
            "action_reject",
            "action_reset_draft",
            "action_load_drivers",
            "action_generate_plan",
        },
    },
    "fix.cost.allocation": {
        "order": "date_to desc, id desc",
        "limit": 100,
        "actions": {"action_compute", "action_post", "action_reverse", "action_reset_draft"},
    },
    "fix.cost.pool": {"order": "code", "limit": 200, "actions": set()},
    "fix.business.line": {"order": "sequence, code", "limit": 100, "actions": set()},
    "fix.board.pack": {
        "order": "date_to desc, id desc",
        "limit": 100,
        "actions": {"action_assemble", "action_issue"},
    },
}


def _engine(env):
    if "fix.fpa.engine" not in env:
        raise UserError("The FP&A module (cd_fpa) is not installed on this database.")
    return env["fix.fpa.engine"]


def _report(method):
    def run(env, date_from=None, date_to=None, **params):
        return getattr(_engine(env), method)(date_from=date_from, date_to=date_to, **params)

    run.__name__ = method
    return run


REPORTS = {
    "job_costing": _report("report_job_costing"),
    "job_margin_distribution": _report("report_job_margin_distribution"),
    "technician_loaded_cost": _report("report_technician_loaded_cost"),
    "business_line_pnl": _report("report_business_line_pnl"),
    "branch_profitability": _report("report_branch_profitability"),
    "customer_profitability": _report("report_customer_profitability"),
    "unit_economics": _report("report_unit_economics"),
    "budget_variance": _report("report_budget_variance"),
    "rolling_forecast": _report("report_rolling_forecast"),
    "board_pack": _report("report_board_pack"),
}


def kpis(env):
    """Fiscal-year-to-date M54 tiles, all from posted / live records."""
    if "fix.fpa.engine" not in env:
        return {}
    from odoo.addons.cd_fpa.models.fix_fpa_engine import fy_window, pct

    engine = env["fix.fpa.engine"]
    today = fields.Date.context_today(env.user)
    d_from, _fy_to = fy_window(today)
    out = {}

    lines = engine.approved_budget_lines(d_from, today)
    actuals = engine.line_actuals(lines)
    out["fpa_budget_variance_fytd"] = (
        round(
            sum(
                (actuals.get(ln.id, 0.0) - ln.planned_amount)
                if ln.is_revenue
                else (ln.planned_amount - actuals.get(ln.id, 0.0))
                for ln in lines
            ),
            2,
        )
        if lines
        else None
    )

    league, _unassigned = engine.branch_league(d_from, today)
    active = [r for r in league if r["revenue"] or r["direct"] or r["opex"]]
    out["fpa_branch_top"] = active[0]["branch"] if active else None
    out["fpa_negative_branches"] = (
        sum(1 for r in active if r["contribution"] < 0) if active else None
    )

    jobs = engine.job_costs(d_from, today)
    out["fpa_job_costing_coverage"] = (
        "%s%%" % pct(sum(1 for j in jobs if j["complete"]), len(jobs)) if jobs else None
    )
    return out
