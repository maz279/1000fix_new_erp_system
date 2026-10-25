# A08 · M50 Treasury & Banking — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
SURFACES = {
    "fix.payment.execution": {"order": "id desc", "limit": 200, "actions": {"action_execute"}},
    "fix.bank.statement.line": {
        "order": "date desc, id desc",
        "limit": 200,
        "actions": {"auto_match"},
    },
    "fix.cash.position": {"order": "as_of desc, id desc", "limit": 50, "actions": set()},
}
