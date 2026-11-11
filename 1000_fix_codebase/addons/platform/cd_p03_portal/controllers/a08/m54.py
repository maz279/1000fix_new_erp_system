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
        # Approval is decided from the M63 inbox (fix.workflow.task), never here.
        "actions": {
            "action_submit",
            "action_reject",
            "action_reset_draft",
            "action_create_revision",
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
    # A pool gathers nothing without elements; each names GL accounts, so it has
    # its own form (the form engine's child grid has no many2many input).
    "fix.cost.element": {"order": "pool_id, code", "limit": 400, "actions": set()},
    # Every planned line across budgets; edited on the budget's own grid.
    "fix.budget.line": {"order": "date_from desc, id desc", "limit": 400, "actions": set()},
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

    # The approved version in force, plan and actual both measured over the
    # fiscal year to date (M54-6).
    lines = engine.approved_budget_lines(d_from, today)
    actuals = engine.line_actuals(lines, d_from, today)

    def _var(ln):
        planned = engine.planned_in_window(ln, d_from, today)
        actual = actuals.get(ln.id, 0.0)
        return (actual - planned) if ln.is_revenue else (planned - actual)

    # A variance needs a plan to vary from: None while no approved budget line
    # falls in the window (the same rule as a ratio with no denominator).
    out["fpa_budget_variance_fytd"] = round(sum(_var(ln) for ln in lines), 2) if lines else None

    league, _unassigned = engine.branch_league(d_from, today)
    active = [r for r in league if r["revenue"] or r["direct"] or r["opex"]]
    # A count reads 0 on an empty year; the league leader says so in words.
    out["fpa_branch_top"] = active[0]["branch"] if active else "No branch activity yet"
    out["fpa_negative_branches"] = sum(1 for r in active if r["contribution"] < 0)

    jobs = engine.job_costs(d_from, today)
    out["fpa_job_costing_coverage"] = (
        "%s%%" % pct(sum(1 for j in jobs if j["complete"]), len(jobs)) if jobs else None
    )

    # The whole-budget position (moved from the finance route so the module
    # owns every tile metric the workspace renders).
    try:
        budgets = env["fix.budget"].search([])
        out["budget_total_variance"] = round(sum(budgets.mapped("variance")), 2)
        out["budgets_count"] = len(budgets)
    except Exception:
        out["budget_total_variance"] = out["budgets_count"] = None
    return out
