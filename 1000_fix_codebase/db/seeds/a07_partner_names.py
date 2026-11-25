# ruff: noqa: F821 - runs inside odoo-bin shell, which provides env
"""a07_partner_names.py - fill res.partner.complete_name where a bulk load left it empty.

Run once inside `odoo-bin shell -c <conf> -d <db>`. Every picker searches a partner by
complete_name first, and partners loaded straight into the table have none, so those
customers cannot be found by name anywhere in the workspace. It only computes what Odoo
would have stored; no name changes. Safe to repeat.
Set FIX_A07_COMMIT=1 to keep the result; otherwise it rolls back and reports.
"""

import os

Partner = env["res.partner"].sudo().with_context(active_test=False)
empty = Partner.search([("complete_name", "=", False), ("name", "!=", False)])
print("a07-partner-names: empty before:", len(empty))
field = Partner._fields["complete_name"]
for start in range(0, len(empty), 1000):
    batch = empty[start : start + 1000]
    env.add_to_compute(field, batch)
    batch.flush_recordset(["complete_name"])
    env.invalidate_all()
print(
    "  empty after:", Partner.search_count([("complete_name", "=", False), ("name", "!=", False)])
)
if os.environ.get("FIX_A07_COMMIT") == "1":
    env.cr.commit()
    print("committed")
else:
    env.cr.rollback()
    print("rolled back (set FIX_A07_COMMIT=1 to keep)")
