# A08 · M54 Costing, Budget & FP&A — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
SURFACES = {
    "fix.budget": {"order": "fiscal_year desc, id desc", "limit": 100, "actions": set()},
    "fix.cost.allocation": {"order": "id desc", "limit": 100, "actions": set()},
}
