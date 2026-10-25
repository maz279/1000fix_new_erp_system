# A08 · M51 Tax & Regulatory (BD) — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
SURFACES = {
    "fix.mushak.register": {
        "order": "invoice_date desc, id desc",
        "limit": 200,
        "actions": {"action_mark_posted", "action_rebuild_from_events"},
    },
    "fix.vat.return": {
        "order": "period desc, id desc",
        "limit": 100,
        "actions": {"action_prepare_period", "action_file"},
    },
    "fix.tds.return": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_prepare_quarter", "action_file"},
    },
    "fix.vat.treatment": {"order": "code", "limit": 200, "actions": set()},
    "fix.withholding.certificate": {"order": "id desc", "limit": 200, "actions": {"action_issue"}},
}
