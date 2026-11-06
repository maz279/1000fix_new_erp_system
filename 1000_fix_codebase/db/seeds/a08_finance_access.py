# ruff: noqa: F821 - runs inside odoo-bin shell, which provides env
"""a08_finance_access.py - close the accidental finance administrators (A08 S5).

Run inside `odoo-bin shell -c <conf> -d <db>` (superuser), after
appoint_approvers.py. Idempotent.

A database built with demo data carries Odoo's demo default: the "Default
access for new users" template implies account.group_account_manager
(account/demo/account_demo.xml). Every user created without explicit groups
then became an Accounting Administrator, who can approve and release payments.
That makes the A08 two-person rules meaningless: on fix_dev 27 people held the
role, including the Knowledge Publisher and the Whistleblowing Intake seat.

This script:
1. takes the finance groups off the default template, so new users start with
   no finance duty;
2. removes the finance groups from synthetic seed logins that are not finance
   staff. It touches only `seed.*@1000fix.local` logins, whose access is
   synthetic by definition; any other holder is listed for a person to review
   and left as it is.

FIX_A08_COMMIT=1 commits; otherwise the transaction is rolled back and the
output says what would have changed.
"""

import json
import os

FINANCE_GROUPS = (
    "account.group_account_manager",
    "account.group_account_user",
    "account.group_account_invoice",
)
FINANCE_STAFF = {
    "seed.fin.billing@1000fix.local",
    "seed.fin.accountant1@1000fix.local",
    "seed.fin.accountant2@1000fix.local",
    "seed.fin.admin@1000fix.local",
    "seed.fin.treasury@1000fix.local",
    "seed.fin.cfo@1000fix.local",
}
SEED_RE = ("seed.", "@1000fix.local")

groups = env["res.groups"]
for xmlid in FINANCE_GROUPS:
    group = env.ref(xmlid, raise_if_not_found=False)
    if group:
        groups |= group

template = env.ref("base.default_user_group", raise_if_not_found=False)
template_removed = []
if template:
    drop = template.implied_ids & groups
    template_removed = drop.mapped("full_name") if "full_name" in drop._fields else drop.ids
    if drop:
        template.write({"implied_ids": [(3, g.id) for g in drop]})

revoked, review = [], []
users = env["res.users"].with_context(active_test=False).search([("group_ids", "in", groups.ids)])
for user in users:
    held = user.group_ids & groups
    is_seed = user.login.startswith(SEED_RE[0]) and user.login.endswith(SEED_RE[1])
    if user.login in FINANCE_STAFF:
        continue
    if is_seed:
        user.write({"group_ids": [(3, g.id) for g in held]})
        revoked.append(user.login)
    else:
        review.append({"login": user.login, "active": user.active, "groups": held.ids})

result = {
    "template_finance_groups_removed": template_removed,
    "seed_logins_revoked": revoked,
    "other_holders_for_review": review,
}
print(json.dumps(result, indent=2, default=str))
if os.environ.get("FIX_A08_COMMIT") == "1":
    env.cr.commit()
    print("committed")
else:
    env.cr.rollback()
    print("rolled back: nothing changed (set FIX_A08_COMMIT=1 to commit)")
