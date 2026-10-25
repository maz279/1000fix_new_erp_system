# A08 · M49 Fixed Assets & Capex — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
SURFACES = {
    "fix.fixed.asset": {
        "order": "purchase_date desc, id desc",
        "limit": 200,
        "actions": {"action_accrue_month", "action_dispose"},
    },
    "fix.cwip.entry": {"order": "id desc", "limit": 200, "actions": {"action_capitalise"}},
}
