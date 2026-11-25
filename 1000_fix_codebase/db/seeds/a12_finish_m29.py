# ruff: noqa: F821 - runs inside odoo-bin shell, which provides env
"""a12_finish_m29.py - put M29's live data in line with its controls (A12 finish).

Run inside `odoo-bin shell -c <conf> -d <db>` (superuser), after -u cd_rbac_ext.
Idempotent. FIX_A12F_M29_COMMIT=1 commits; otherwise the transaction is rolled
back and the output says what would have changed. Not for fix_dev until the lead
has rehearsed it on a copy.

What it does, walking the sanctioned lifecycle as real users:
1. takes internal workspace groups off portal (share) users, which the model now
   refuses going forward, and writes one audit row per user;
2. appoints synthetic seed.* holders where a control has no holder: two Security
   Officers (severity needs two people), and an Access Approver if there is none;
3. leaves open incidents open. Containment is a statement of what was done, and
   nobody has said: each gets a to-do for an officer and a chatter note;
4. measures every SoD control through the real run, so the reports are current;
5. runs one certification campaign for the current quarter through its action;
6. walks one break-glass session end to end, so its screen shows a real history;
and, where Integration Admin or the CAB has fewer than two holders, gives a synthetic
user the role that carries the seat through a real access request (N-M28-6).

It does not touch: submitted access requests and pending JML events (a person
decides those; they are listed), any approval, any audit row.
"""

import json
import os

from odoo import fields

COMMIT = os.environ.get("FIX_A12F_M29_COMMIT") == "1"
ACCESS_APPROVER = "cd_rbac_ext.group_access_approver"
OFFICER = "cd_rbac_ext.group_security_officer"
BREAK_GLASS_REASON = "Synthetic walk: confirms the break-glass path on this environment"
report = {}


def synthetic_user(login, name, groups):
    """A seed.*@1000fix.local user, the repository's convention for synthetic staff."""
    Users = env["res.users"].with_context(active_test=False, no_reset_password=True)
    user = Users.search([("login", "=", login)], limit=1)
    if not user:
        user = Users.create(
            {
                "name": f"{name} (synthetic)",
                "login": login,
                "email": login,
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    user.write({"active": True, "group_ids": [(4, env.ref(g).id) for g in groups]})
    return user


# --- 1. portal users holding internal workspace groups
base = env.ref("cd_rbac_ext.group_fix_portal_user")
portal_cleaned = []
share_users = env["res.users"].with_context(active_test=False).search([("share", "=", True)])
for user in share_users.filtered(lambda u: base in u.all_group_ids):
    # one write: the model refuses a portal user left holding any of them
    internal = user.group_ids.filtered(lambda g: base in g.all_implied_ids)
    user.write({"group_ids": [(3, g.id) for g in internal]})
    env["fix.security.audit"].log_event(
        "portal_cleanup",
        f"res.users,{user.id}",
        f"internal workspace group(s) removed from portal user {user.login}: "
        + ", ".join(internal.mapped("name"))[:160],
    )
    portal_cleaned.append(user.login)
report["portal_users_cleaned"] = portal_cleaned

# --- 2. synthetic appointments where a control has no holder
officers = (
    env.ref(OFFICER).user_ids.filtered("active")
    | synthetic_user("seed.sec.officer1@1000fix.local", "Security Officer 1", [OFFICER])
    | synthetic_user("seed.sec.officer2@1000fix.local", "Security Officer 2", [OFFICER])
)
approvers = env.ref(ACCESS_APPROVER).user_ids.filtered("active")
if not approvers:
    approvers = synthetic_user(
        "seed.access.approver@1000fix.local", "Access Approver", [ACCESS_APPROVER]
    )
approver = approvers.sorted("id")[0]
requester = officers.sorted("id")[0]
report["security_officers"] = officers.mapped("login")
report["access_approver_used"] = approver.login

# --- 2b. two-person approval needs a second holder (N-M28-6): where a seat has fewer than
# two active holders, a synthetic user receives its role through a real access request
SEATS = (
    ("cd_itsm.group_integration_admin", "R-33", "seed.integration.admin", "Integration Admin"),
    ("cd_itsm.group_itsm_cab_member", "R-02", "seed.cab.member", "CAB Member"),
)
report["seats_filled"] = []
for group_xmlid, role_code, login, name in SEATS:
    group = env.ref(group_xmlid)
    role = env["fix.role"].search([("code", "=", role_code)], limit=1)
    for number in (1, 2):
        holders = group.all_user_ids.filtered("active")
        full_login = f"{login}{number}@1000fix.local"
        if len(holders) >= 2 or full_login in holders.mapped("login"):
            continue
        holder = synthetic_user(full_login, f"{name} {number}", [])
        filed_by = (officers - approver - holder).sorted("id")[0]
        request = (
            env["fix.access.request"]
            .with_user(filed_by)
            .create(
                {
                    "user_id": holder.id,
                    "role_id": role.id,
                    "request_type": "grant",
                    "reason": f"Synthetic appointment: {name}, a holder for two-person approval.",
                }
            )
        )
        request.with_user(approver).action_approve()
        request.with_user(approver).action_grant()
        group.invalidate_recordset(["all_user_ids"])
        report["seats_filled"].append(f"{holder.login} -> {role_code} ({request.name})")
report["seat_holders"] = {
    group_xmlid: env.ref(group_xmlid).all_user_ids.filtered("active").mapped("login")
    for group_xmlid, _role, _login, _name in SEATS
}

# --- 3. open incidents: nothing here can say what was contained, so ask a person
TODO = "Record what was done and move this incident through the workflow, or say why not."
waiting = []
for incident in env["fix.security.incident"].search([("state", "in", ("open", "contained"))]):
    waiting.append(
        {"incident": incident.name, "state": incident.state, "severity": incident.severity}
    )
    if incident.activity_ids.filtered(lambda a: a.summary == "Security officer review"):
        continue
    incident.message_post(
        body=f"M29 clean-up: no {'containment' if incident.state == 'open' else 'root cause'} "
        f"is recorded on this incident, and this script cannot supply one. It stays "
        f"{incident.state} until a Security Officer records what really happened."
    )
    incident.activity_schedule(
        "mail.mail_activity_data_todo",
        summary="Security officer review",
        note=TODO,
        user_id=requester.id,
        date_deadline=fields.Date.context_today(incident),
    )
report["incidents_waiting_for_a_person"] = waiting

# --- 4. measure the SoD register through the real run, once a day
SodTest = env["fix.sod.test"]
today = fields.Date.context_today(SodTest)
if not SodTest.search_count([("tested_on", "=", today)]):
    report["sod_controls_measured"] = SodTest.cron_run_sod_tests()
report["sod_controls_failing_today"] = sorted(
    set(
        SodTest.search([("tested_on", "=", today), ("result", "=", "fail")]).mapped(
            "control_id.code"
        )
    )
)

# --- 5. one certification campaign, generated by an Access Approver
period = f"{today.year}-Q{(today.month - 1) // 3 + 1}"
Campaign = env["fix.access.certification.campaign"]
campaign = Campaign.search([("period", "=", period)], limit=1)
if not campaign:
    campaign = Campaign.with_user(approver).create({"period": period})
if campaign.state == "draft":
    campaign.with_user(approver).action_generate()
report["campaign"] = {
    "period": period,
    "lines": campaign.line_count,
    "no_reviewer": campaign.no_reviewer_note,
}

# --- 6. one break-glass walk: requested, approved by a second person, opened, closed
Session = env["fix.privileged.session"]
if not Session.search_count([("reason", "=", BREAK_GLASS_REASON)]):
    holder = requester if requester != approver else officers.sorted("id")[1]
    session = Session.with_user(holder).create(
        {"access_kind": "sudo_admin", "reason": BREAK_GLASS_REASON, "duration_hours": 1}
    )
    session.with_user(approver).action_approve()
    session.with_user(holder).action_open()
    session.with_user(holder).action_close()
    report["break_glass_walk"] = session.name

# --- what is left for a person
report["requests_awaiting_a_decision"] = (
    env["fix.access.request"].search([("state", "=", "submitted")]).mapped("name")
)
report["jml_events_pending"] = (
    env["fix.jml.event"].search([("state", "=", "pending")]).mapped("name")
)
report["masking_rows_in_force"] = env["fix.sensitive.field"].search_count(
    [("masking_rule", "!=", "none"), ("active", "=", True)]
)
try:
    report["audit_chain"] = env["fix.security.audit"].action_verify_chain()["note"]
except Exception as exc:
    report["audit_chain"] = str(exc)

print(json.dumps(report, indent=2, default=str))
if COMMIT:
    env.cr.commit()
    print("COMMITTED")
else:
    env.cr.rollback()
    print("ROLLED BACK (set FIX_A12F_M29_COMMIT=1 to keep)")
