# A08 · M53 Revenue Recognition & Settlement — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
SURFACES = {
    "fix.revenue.schedule": {"order": "start_date desc, id desc", "limit": 200, "actions": set()},
    "fix.commission.ledger": {"order": "id desc", "limit": 200, "actions": {"action_post_to_gl"}},
    "fix.payout.run": {
        "order": "id desc",
        "limit": 100,
        "actions": {
            "action_approve",
            "action_submit_payout",
            "action_generate_beftn",
            "action_confirm_bank_settlement",
        },
    },
    "fix.seller.statement": {"order": "period desc, id desc", "limit": 100, "actions": set()},
}
