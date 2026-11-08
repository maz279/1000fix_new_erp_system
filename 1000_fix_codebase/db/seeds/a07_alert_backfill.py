# ruff: noqa: F821 - runs inside odoo-bin shell, which provides env
"""a07_alert_backfill.py - hand the expiry events already raised to the A07 alert queue.

Run once inside `odoo-bin shell -c <conf> -d <db>`, after the upgrade that adds
fix.asset.alert. A new consumer hears only events raised after it was registered, so
the warnings the crons already announced would stay invisible until their next date.
This replays only the alert consumers. Safe to repeat: an event delivered once is not
delivered again, and a repeat of an open alert raises its count instead of a new row.
Set FIX_A07_COMMIT=1 to keep the result; otherwise it rolls back and reports.
"""

import os

consumers = env["fix.event.consumer"].sudo().search([("method", "=", "consume_asset_alert")])
before = env["fix.asset.alert"].sudo().search_count([])
consumers.action_backfill()
handled = total = 0
Outbox = env["fix.event.outbox"].sudo()
# the replay reopens only these consumers' events: walk them until none is left
while True:
    handled = Outbox.cron_relay(limit=500)
    total += handled
    if not handled:
        break
Alert = env["fix.asset.alert"].sudo()
print("a07-alert-backfill: events handled", total, "alerts", before, "->", Alert.search_count([]))
for row in Alert.read_group([], ["module", "event_type"], ["module", "event_type"], lazy=False):
    print(" ", row["module"], row["event_type"], row["__count"])
print("  with nobody to act:", Alert.search_count([("no_holder", "=", True)]))
if os.environ.get("FIX_A07_COMMIT") == "1":
    env.cr.commit()
    print("committed")
else:
    env.cr.rollback()
    print("rolled back (set FIX_A07_COMMIT=1 to keep)")
