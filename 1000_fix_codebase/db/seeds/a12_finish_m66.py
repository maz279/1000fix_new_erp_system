# ruff: noqa: F821, UP031, B023 - runs inside odoo-bin shell, which provides env
"""a12_finish_m66.py - bring the live M66 rows into line with the finished controls.

Run inside `odoo-bin shell -c <conf> -d <db>` (superuser), after -u cd_itsm.
Idempotent. FIX_A12F_COMMIT=1 commits; otherwise the transaction is rolled back and
the output says what would have changed. Never run it on fix_dev by hand: the lead
runs it after a rehearsal on a copy.

What it does, and what it refuses to do:

- 158 of 159 tickets sit `new`, unassigned, with nobody told. Synthetic service desk
  agents classify and assign a sensible number (FIX_A12F_TICKETS, default 24, highest
  priority first, oldest first) through the real actions. Nothing is resolved: nobody
  knows those faults were fixed, and a resolution would be invented. The rest stay
  visibly in the queue, each with an activity on the agent the queue rotates it to.
- Rows that contradict a control move to an honest state with a chatter note:
  a change reading `approved` with no approval goes back to draft; an emergency change
  implemented with no trail gets a real retro approval task and a PIR due; a known
  error with no workaround goes back to investigation; a resolved problem with no
  root cause too; an in-service asset with no acceptance reads as awaiting it.
- Each workflow is walked once on rows labelled SYNTHETIC, as real users, so the
  screens show real state: template, standard, normal, emergency, major incident,
  catalogue approval, write-off, over-use.

Synthetic appointments use seed.*@1000fix.local and say so in their names. No password
is set: they exist to hold a role and own a task. Anything needing a person is listed
under `for_a_person` in the output.
"""

import json
import os

from odoo import fields

MARK = "SYNTHETIC (A12 finish seed)"
AGENT = "cd_itsm.group_itsm_agent"
CM = "cd_itsm.group_itsm_change_manager"
CAB = "cd_itsm.group_itsm_cab_member"
TICKET_QUOTA = int(os.environ.get("FIX_A12F_TICKETS") or 24)
REQUEST_WORDS = ("request", "new laptop", "install", "access to", "licen", "provision", "onboard")
IMPACT_URGENCY = {
    "urgent": ("high", "high"),
    "high": ("high", "medium"),
    "medium": ("medium", "medium"),
    "low": ("low", "medium"),
}

result = {
    "appointed": [],
    "tickets_classified_assigned": 0,
    "tickets_started": 0,
    "tickets_awaiting_user": 0,
    "tickets_in_queue": 0,
    "tickets_typed_request": 0,
    "changes_returned_to_draft": [],
    "emergency_retro_opened": [],
    "problems_returned_to_investigation": [],
    "problems_verifying": [],
    "assets_awaiting_acceptance": [],
    "dependencies_linked": 0,
    "dead_letter_incidents": 0,
    "synthetic_walks": [],
    "for_a_person": [],
}

Ticket = env["fix.itsm.ticket"]
Change = env["fix.itsm.change"]
Template = env["fix.itsm.change.template"]
Problem = env["fix.itsm.problem"]
Asset = env["fix.itsm.asset"]
Licence = env["fix.itsm.licence"]
Catalogue = env["fix.itsm.catalogue"]
Employee = env["hr.employee"].sudo()
Users = env["res.users"].sudo().with_context(no_reset_password=True, active_test=False)
unit = env["operating.unit"].sudo().search([], limit=1)


def appoint(login, name, xmlids):
    """A synthetic seat: find or create the login, link an employee, grant the role."""
    groups = [env.ref(x).id for x in xmlids]
    user = Users.search([("login", "=", login)], limit=1)
    if not user:
        vals = {"login": login, "name": "%s (synthetic)" % name, "group_ids": [(6, 0, groups)]}
        if unit:
            vals["assigned_operating_unit_ids"] = [(6, 0, unit.ids)]
            vals["default_operating_unit_id"] = unit.id
        user = Users.create(vals)
        result["appointed"].append(login)
    else:
        user.write({"active": True, "group_ids": [(4, g) for g in groups]})
    employee = Employee.with_context(active_test=False).search([("user_id", "=", user.id)], limit=1)
    if not employee:
        employee = Employee.create({"name": "%s (synthetic)" % name, "user_id": user.id})
    return user, employee


agent1, agent1_e = appoint("seed.it.agent1@1000fix.local", "IT Service Desk Agent 1", [AGENT])
agent2, agent2_e = appoint("seed.it.agent2@1000fix.local", "IT Service Desk Agent 2", [AGENT])
cm1, cm1_e = appoint("seed.it.change.manager@1000fix.local", "IT Change Manager", [CM])
cm2, cm2_e = appoint("seed.it.change.manager2@1000fix.local", "IT Change Manager 2", [CM])
cab1, cab1_e = appoint("seed.it.cab1@1000fix.local", "CAB Member 1", [CAB])
cab2, cab2_e = appoint("seed.it.cab2@1000fix.local", "CAB Member 2", [CAB])
staff, staff_e = appoint("seed.it.requester@1000fix.local", "Staff Requester", ["base.group_user"])


def decide(record, approver):
    tasks = record.sudo().approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    tasks.with_user(approver).action_approve(comment="%s: synthetic decision." % MARK)
    return bool(tasks)


# ---- repair: rows that contradict a control ----------------------------------------
def note(record, text):
    record.sudo().message_post(body="A12 finish seed: %s" % text)


for change in Change.search([("state", "=", "approved"), ("approval_state", "=", "none")]):
    change._guarded().write({"state": "draft"})
    note(
        change,
        "this change read as approved with no approval on record and no M63 request behind "
        "it. It is a draft again: complete its plans and submit it.",
    )
    result["changes_returned_to_draft"].append(change.name)
    result["for_a_person"].append("%s: write its plans and submit it." % change.name)

legacy_emergency = Change.search(
    [
        ("change_type", "=", "emergency"),
        ("state", "=", "implemented"),
        ("emergency_path", "=", False),
    ]
)
for change in legacy_emergency.filtered(lambda c: c.approval_state != "approved"):
    change._guarded().write(
        {
            "emergency_path": True,
            "emergency_reason": "Not recorded: this change predates the emergency path.",
            "retro_approval_state": "pending",
            "pir_due_on": fields.Date.context_today(change),
        }
    )
    note(
        change,
        "this emergency change is implemented with no approval, implementer or review on "
        "record. That history cannot be recreated, so a retro approval task is open and the "
        "review is due now.",
    )
    change._retro_route()
    result["emergency_retro_opened"].append(change.name)
    if not change.implementer_id:
        result["for_a_person"].append(
            "%s: nobody knows who implemented it. Say who in its review." % change.name
        )

for problem in Problem.search([("state", "=", "known_error")]):
    if not (problem.workaround or "").strip() or not (problem.root_cause or "").strip():
        problem._guarded().write({"state": "investigating", "known_error": False})
        note(problem, "a known error documents its root cause and workaround; this one did not.")
        result["problems_returned_to_investigation"].append(problem.name)
        result["for_a_person"].append("%s: document the workaround." % problem.name)

for problem in Problem.search([("state", "=", "resolved")]):
    if not (problem.root_cause or "").strip():
        problem._guarded().write({"state": "investigating", "resolved_on": False})
        note(problem, "a resolved problem names its root cause; this one did not.")
        result["problems_returned_to_investigation"].append(problem.name)
        result["for_a_person"].append("%s: record the root cause." % problem.name)
    else:
        problem.with_user(agent1).action_verify()
        result["problems_verifying"].append(problem.name)

for asset in Asset.search([("state", "=", "in_service"), ("acceptance_state", "=", "none")]):
    asset._guarded().write({"acceptance_state": "pending"})
    note(asset, "no acceptance is on record for this allocation; the holder has to accept it.")
    result["assets_awaiting_acceptance"].append(asset.asset_tag)
    if not asset.assigned_to_id.user_id:
        result["for_a_person"].append(
            "%s: %s has no login. Record the signed acceptance form."
            % (asset.asset_tag, asset.assigned_to_id.name)
        )

# depends_on was typed keys: link what still resolves (the old column stays, unread).
env.cr.execute(
    "SELECT data_type FROM information_schema.columns "
    "WHERE table_name = 'fix_itsm_ci' AND column_name = 'depends_on'"
)
if env.cr.fetchone():
    env.cr.execute("SELECT id, depends_on FROM fix_itsm_ci WHERE COALESCE(depends_on, '') != ''")
    for ci_id, typed in env.cr.fetchall():
        keys = [k.strip() for k in (typed or "").split(",") if k.strip()]
        ci = env["fix.itsm.ci"].browse(ci_id)
        upstream = env["fix.itsm.ci"].search(
            [("ci_key", "in", keys), ("company_id", "=", ci.company_id.id)]
        )
        if upstream - ci.depends_on:
            ci.write({"depends_on": [(4, u.id) for u in upstream]})
            result["dependencies_linked"] += 1

# ---- the queue: a sensible number taken on through the real actions ----------------
new_tickets = Ticket.search([("state", "=", "new")])
for ticket in new_tickets:
    title = (ticket.title or "").lower()
    if ticket.ticket_type == "incident" and (
        ticket.catalogue_id or any(word in title for word in REQUEST_WORDS)
    ):
        ticket.write({"ticket_type": "request"})
        result["tickets_typed_request"] += 1

taken = Ticket.search_count([("assigned_user_id", "in", (agent1 | agent2).ids)])
rank = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
blocked = new_tickets.filtered(
    lambda t: t.catalogue_id.requires_approval and t.approval_state != "approved"
)
candidates = (new_tickets - blocked).sorted(lambda t: (rank.get(t.priority, 9), t.id))
for index, ticket in enumerate(candidates[: max(0, TICKET_QUOTA - taken)]):
    agent = agent1 if index % 2 == 0 else agent2
    impact, urgency = IMPACT_URGENCY.get(ticket.priority, ("medium", "medium"))
    worker = ticket.with_user(agent)
    worker.action_classify(impact=impact, urgency=urgency)
    worker.action_assign()
    result["tickets_classified_assigned"] += 1
    if index % 2 == 0:
        worker.action_start()
        result["tickets_started"] += 1
    if index % 6 == 0 and ticket.requester_id:
        worker.action_await_user(reason="This was raised some time ago: is it still happening?")
        result["tickets_awaiting_user"] += 1

for ticket in Ticket.search([("state", "=", "new")]):
    owner = ticket._queue_owner()
    summary = "SLA breach on %s" % ticket.name if ticket.escalated else "In queue: %s" % ticket.name
    if owner and not ticket.activity_ids.filtered(
        lambda a: a.user_id == owner and a.summary == summary
    ):
        ticket.activity_schedule(
            "mail.mail_activity_data_todo",
            date_deadline=fields.Date.context_today(ticket),
            summary=summary,
            note="This ticket is in the service desk queue with no agent on it.",
            user_id=owner.id,
        )
    result["tickets_in_queue"] += 1

result["dead_letter_incidents"] = len(Ticket.cron_dead_letter_incidents())


# ---- one walk of each workflow, labelled, as real users -----------------------------
def walked(name):
    result["synthetic_walks"].append(name)


def once(model, domain):
    return env[model].with_context(active_test=False).search(domain, limit=1)


today = fields.Date.context_today(Change)
title = "%s ticket walk" % MARK
if not once("fix.itsm.ticket", [("title", "=", title)]):
    raised = Ticket.with_user(staff).create(
        {"title": title, "description": "Printer offline on the 3rd floor.", "category": "hardware"}
    )
    raised.with_user(agent1).action_assign()
    raised.with_user(agent1).action_start()
    raised.with_user(agent1).action_resolve(resolution="%s: driver reinstalled." % MARK)
    raised.with_user(staff).action_close()
    walked("ticket: raised by an employee, worked, closed by him")

title = "%s major incident" % MARK
if not once("fix.itsm.ticket", [("title", "=", title)]):
    major = Ticket.with_user(staff).create(
        {"title": title, "description": "Email down for one branch.", "category": "network"}
    )
    major.with_user(agent2).action_assign()
    major.with_user(agent2).action_declare_major(manager=cm1.login)
    major.with_user(agent2).action_major_update(note="%s: vendor engaged." % MARK)
    walked("major incident with a named manager")

item = Catalogue.search([("requires_approval", "=", True)], limit=1)
title = "%s catalogue request" % MARK
if item and not once("fix.itsm.ticket", [("title", "=", title)]):
    request = Ticket.with_user(staff).create(
        {"title": title, "description": "As per the catalogue.", "catalogue_id": item.id}
    )
    if request.approval_state == "pending":
        decide(request, cm1)
        request.with_user(agent1).action_assign()
        walked("catalogue request approved through M63, then assigned")

code = "SYNTH-STD-01"
template = Template.search([("code", "=", code)], limit=1)
if not template:
    template = Template.with_user(agent1).create(
        {
            "code": code,
            "name": "%s rotate an application log" % MARK,
            "implementation_plan": "Rotate the log with logrotate.",
            "test_plan": "Tail the new log file.",
            "rollback_plan": "Restore the previous log file.",
            "risk_probability": "1",
            "risk_impact": "2",
            "max_window_hours": 2,
        }
    )
    template.with_user(cm1).action_authorise()
    walked("standard change template authorised by a Change Manager")

title = "%s standard change" % MARK
if not once("fix.itsm.change", [("title", "=", title)]):
    standard = Change.with_user(agent1).create(
        {
            "title": title,
            "template_id": template.id,
            "requested_by_id": agent1_e.id,
            "implementer_id": agent2_e.id,
            "planned_on": today,
        }
    )
    standard.with_user(agent1).action_submit()
    standard.with_user(agent2).action_implement()
    walked("standard change pre-approved by its template and implemented")

title = "%s normal change" % MARK
if not once("fix.itsm.change", [("title", "=", title)]):
    normal = Change.with_user(agent1).create(
        {
            "title": title,
            "requested_by_id": agent1_e.id,
            "implementer_id": agent2_e.id,
            "planned_on": today,
            "implementation_plan": "Patch the print server.",
            "test_plan": "Print a test page.",
            "rollback_plan": "Remove the patch.",
        }
    )
    normal.with_user(agent1).action_submit()
    decide(normal, cm1)
    normal.with_user(agent2).action_implement()
    normal.with_user(agent1).action_record_pir(pir_notes="%s: worked as planned." % MARK)
    walked("normal change through the Change Manager to reviewed")

title = "%s emergency change" % MARK
if not once("fix.itsm.change", [("title", "=", title)]):
    emergency = Change.with_user(agent1).create(
        {
            "title": title,
            "change_type": "emergency",
            "risk": "high",
            "requested_by_id": agent1_e.id,
            "implementer_id": agent2_e.id,
            "planned_on": today,
            "implementation_plan": "Restart the failed gateway on the spare node.",
            "rollback_plan": "Fail back to the primary node.",
        }
    )
    emergency.with_user(agent2).action_emergency_implement(reason="%s: gateway down." % MARK)
    walked("emergency change implemented first; its retro approval and review stay open")

tag = "SYNTH-LT-01"
if not Asset.search([("asset_tag", "=", tag)], limit=1):
    laptop = Asset.with_user(agent1).create(
        {"name": "%s laptop" % MARK, "asset_tag": tag, "asset_kind": "laptop"}
    )
    laptop.with_user(agent1).action_allocate(assigned_to=staff_e.id)
    laptop.with_user(staff).action_accept()
    walked("asset allocated and accepted by its holder")

tag = "SYNTH-LT-02"
if not Asset.search([("asset_tag", "=", tag)], limit=1):
    old = Asset.with_user(agent1).create(
        {"name": "%s old laptop" % MARK, "asset_tag": tag, "asset_kind": "laptop"}
    )
    old.with_user(agent1).action_retire(wipe_certificate="SYNTH-WIPE-0001")
    walked("asset write-off recorded and left awaiting a second person")

name = "%s licence" % MARK
licence = Licence.search([("name", "=", name)], limit=1)
if not licence:
    licence = Licence.with_user(agent1).create(
        {"name": name, "vendor": "Synthetic", "seats_owned": 1}
    )
    licence.with_user(agent1).action_assign_seat(employee=staff_e.id)
    licence.with_user(agent2).action_record_overuse(employee=agent1_e.id)
    walked("licence seat assigned; over-use opened a compliance exception")

Licence.cron_refresh_licences()
Ticket.browse().env.flush_all()

result["counts"] = {
    "tickets_by_state": {
        s: Ticket.search_count([("state", "=", s)])
        for s in ("new", "assigned", "in_progress", "awaiting_user", "resolved", "closed")
    },
    "tickets_unassigned_with_no_activity": len(
        Ticket.search([("state", "=", "new")]).filtered(lambda t: not t.activity_ids)
    ),
    "licence_exceptions_open": env["fix.itsm.licence.exception"].search_count(
        [("state", "=", "open")]
    ),
}
if blocked:
    result["for_a_person"].append("%d request(s) await their catalogue approval." % len(blocked))

print(json.dumps(result, indent=2, default=str))
if os.environ.get("FIX_A12F_COMMIT") == "1":
    env.cr.commit()
    print("committed")
else:
    env.cr.rollback()
    print("rolled back: nothing changed (set FIX_A12F_COMMIT=1 to commit)")
