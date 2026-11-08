"""A07 D8: replay the risk-register deliveries that died before the consumer was fixed.

Run in `odoo-bin shell`. Until the fix, `fix.risk.register.consume_project_risk_escalated`
read the payload's `project` as a dict and died on the string M67 really sends, so those
deliveries sit dead-lettered and the relay never hands them over again. This replays only
those, through the relay's own savepointed delivery, and marks each one done when it now
succeeds. A delivery that still fails stays dead with its new error.

Set FIX_A07_COMMIT=1 to keep the result; otherwise it rolls back and reports.
"""

import os

from odoo import fields

METHOD = "consume_project_risk_escalated"
Delivery = env["fix.event.consumer.delivery"].sudo()  # noqa: F821
Outbox = env["fix.event.outbox"].sudo()  # noqa: F821
dead = Delivery.search([("state", "=", "dead"), ("subscription_id.method", "=", METHOD)])
print("a07-replay-dead-risk: dead before:", len(dead))
fixed = still = 0
for delivery in dead:
    error = Outbox._relay_deliver(delivery.subscription_id, delivery.event_id)
    if error:
        still += 1
        delivery.write({"last_error": error, "attempts": delivery.attempts + 1})
        print("  still failing:", delivery.id, error[:160])
    else:
        fixed += 1
        delivery.write(
            {
                "state": "done",
                "attempts": delivery.attempts + 1,
                "last_error": False,
                "delivered_at": fields.Datetime.now(),
            }
        )
print("  delivered now:", fixed, "still dead:", still)
if os.environ.get("FIX_A07_COMMIT") == "1":
    env.cr.commit()  # noqa: F821
    print("committed")
else:
    env.cr.rollback()  # noqa: F821
    print("rolled back (set FIX_A07_COMMIT=1 to keep)")
