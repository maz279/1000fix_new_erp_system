# A08 · M52 AP & Employee Expense — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
SURFACES = {
    "fix.vendor.invoice": {
        "order": "invoice_date desc, id desc",
        "limit": 200,
        "actions": {"action_request_payment"},
    },
    "fix.expense.claim": {
        "order": "expense_date desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve"},
    },
}
