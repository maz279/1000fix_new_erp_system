# ruff: noqa: F821, UP031 - runs inside odoo-bin shell, which provides env
"""a12_finish_m67.py - M67 Projects: move the rows that contradict the controls to an
honest state, redeliver the dead hand-offs, and walk one project to a posted invoice.

Run inside `odoo-bin shell -c <conf> -d <db>` (superuser), after appoint_approvers.py
and a08_finance_access.py. Idempotent. FIX_A12_COMMIT=1 commits; otherwise the
transaction is rolled back and the output says what would have changed.

Nothing here forges a state, an approval, an invoice or a signature:
- A row that cannot be justified moves back with a chatter note saying why. Line 6 cited
  INV/2026/00031, which exists nowhere: it moves back to planned and no invoice is made.
- Approvals go through the real engine. A request is decided only when its inbox task
  sits with a synthetic seed.*@1000fix.local holder; otherwise it stays pending and is
  listed for a person.
- Gates whose reviewer was the project's own manager lose that decision. They stay
  scheduled for a real sponsor, so the projects they gate stay on hold.
- The figures a person must settle (billing above a ceiling, the hourly cost rate) are
  listed, never invented.

Synthetic appointments follow the seed convention and say so in their names.
"""

import json
import os

from odoo.exceptions import UserError

PM_LOGIN = "seed.ppm.pm@1000fix.local"
SPONSOR_LOGIN = "seed.ppm.sponsor@1000fix.local"
ENGINEER_LOGIN = "seed.ppm.engineer@1000fix.local"
FINANCE_LOGIN = "seed.fin.billing@1000fix.local"
REQUIRED_LOGINS = (
    FINANCE_LOGIN,
    "seed.dofa.t2@1000fix.local",
    "seed.dofa.t3@1000fix.local",
    "seed.dofa.t4@1000fix.local",
)
PM_GROUP = "cd_ppm.group_ppm_project_manager"
SPONSOR_GROUP = "cd_ppm.group_ppm_sponsor"
SYNTHETIC = "Synthetic seed appointment"
WALK_DONE = "A12 Walk: Mirpur Hub Network Upgrade"
WALK_RUNNING = "A12 Walk: Uttara Depot Fit-Out"
SEED_TAG = "A12 finish seed"
PAYMENT_NOT_DONE = "the customer payment could not be registered"


def _person(env, login, name, group_xmlid=None):
    """A synthetic user with an employee record, reused when it exists."""
    Users = env["res.users"].with_context(no_reset_password=True, active_test=False)
    companies = env["res.company"].search([])
    groups = [env.ref("base.group_user").id]
    if group_xmlid:
        groups.append(env.ref(group_xmlid).id)
    user = Users.search([("login", "=", login)], limit=1)
    if not user:
        user = Users.create(
            {
                "name": name,
                "login": login,
                "password": login,
                "group_ids": [(6, 0, groups)],
                "company_id": env.ref("base.main_company").id,
                "company_ids": [(6, 0, companies.ids)],
            }
        )
    else:
        user.write({"group_ids": [(4, g) for g in groups]})
    employee = env["hr.employee"].sudo().search([("user_id", "=", user.id)], limit=1)
    if not employee:
        employee = env["hr.employee"].sudo().create({"name": name, "user_id": user.id})
    return user, employee


def _note(record, text):
    """Post once: a second run finds the same note and adds nothing."""
    marked = "%s: %s" % (SEED_TAG, text)
    posted = (
        record.env["mail.message"]
        .sudo()
        .search_count(
            [
                ("model", "=", record._name),
                ("res_id", "=", record.id),
                ("body", "ilike", marked[:120]),
            ]
        )
    )
    if not posted:
        record.sudo().message_post(body=marked)


def _is_seed_login(user):
    return user.login.startswith("seed.") and user.login.endswith("@1000fix.local")


def repair_codes(env, out):
    for project in env["fix.project"].search(["|", ("code", "=", False), ("code", "=", "PRJ/New")]):
        code = env["ir.sequence"].next_by_code("fix.project")
        project.write({"code": code})
        _note(project, "the project had no real code (PRJ/New); numbered from the sequence.")
        out["codes"].append(code)


def repair_tasks(env, out):
    """A task of project A pointing at project B's milestone counted in B's gate."""
    for task in env["fix.project.task"].search([("milestone_id", "!=", False)]):
        if task.milestone_id.project_id != task.project_id:
            foreign = task.milestone_id.display_name
            task.write({"milestone_id": False})
            _note(
                task,
                "the milestone link was cleared: %s belongs to another project. The project "
                "manager links the task to a milestone of its own project." % foreign,
            )
            out["tasks_unlinked"].append(task.id)


def repair_milestones(env, out):
    for milestone in env["fix.project.milestone"].search(
        [("state", "=", "done"), ("accepted_by_id", "=", False)]
    ):
        milestone._guarded().write({"state": "pending"})
        _note(
            milestone,
            "moved back to pending: it was marked done with no recorded acceptance. A sponsor "
            "accepts it with the client's sign-off.",
        )
        out["milestones_reopened"].append(milestone.id)


def repair_gates(env, sponsor_employee, out):
    """A manager reviewing his own project decided nothing."""
    for gate in env["fix.project.gate"].search([("reviewer_id", "!=", False)]):
        if gate.reviewer_id != gate.project_id.manager_id:
            continue
        said = "%s, %s" % (gate.decision or "no decision", gate.state)
        gate.write(
            {
                "reviewer_id": sponsor_employee.id,
                "decision": False,
                "checklist_passed": False,
                "state": "scheduled",
            }
        )
        _note(
            gate,
            "the reviewer was the project's own manager (%s), so the review is void and goes "
            "back to scheduled under a synthetic sponsor for a real decision." % said,
        )
        out["gates_reset"].append(gate.name)


def _invoice_exists(env, reference):
    if not reference:
        return False
    if env["account.move"].search_count([("name", "=", reference)]):
        return True
    return (
        "fix.ar.invoice" in env
        and env["fix.ar.invoice"].search_count([("name", "=", reference)]) > 0
    )


def repair_billing(env, out):
    Billing = env["fix.project.billing"]
    # The earlier build called a draft move "invoiced". Nothing posted it, so no revenue
    # exists: the line goes back to Finance's queue, which posts that same draft.
    for line in Billing.search(
        [("state", "in", ("invoiced", "paid")), ("invoice_id", "!=", False)]
    ):
        if line.invoice_id.state != "posted":
            line._guarded().write({"state": "ready", "invoice_ref": False, "invoiced_on": False})
            _note(line, "moved back to ready: its invoice was never posted, so nothing was billed.")
            out["billing_moved_back"].append(line.name)
    for line in Billing.search([("state", "in", ("invoiced", "paid")), ("invoice_id", "=", False)]):
        reference = line.invoice_ref
        if _invoice_exists(env, reference):
            # A real document exists under this number: a person links it.
            out["for_a_person"].append(
                "%s cites %s, which exists but is not linked to the line." % (line.name, reference)
            )
            continue
        line._guarded().write({"state": "planned", "invoice_ref": False, "invoiced_on": False})
        _note(
            line,
            "moved back to planned: it read invoiced citing %s, which exists in neither the "
            "ledger nor the AR register. No invoice was created." % (reference or "no reference"),
        )
        out["billing_moved_back"].append(line.name)
    for line in Billing.search([("state", "=", "ready")]):
        milestone = line.milestone_id
        accepted = milestone.state == "done" and milestone.accepted_by_id
        if line.billing_type == "milestone" and not accepted:
            line._guarded().write({"state": "planned"})
            _note(
                line,
                "moved back to planned: it was ready to invoice with no accepted milestone%s."
                % ("" if line.customer_id else " and no customer"),
            )
            out["billing_moved_back"].append(line.name)
        elif not line.customer_id:
            line._guarded().write({"state": "planned"})
            _note(line, "moved back to planned: it was ready to invoice with no customer.")
            out["billing_moved_back"].append(line.name)


def report_over_ceiling(env, out):
    """A figure only a person can settle. These lines stay planned: mark_ready refuses
    them until the amount falls or the contract is approved higher."""
    for project in env["fix.project"].search([]):
        committed = project._billing_committed()
        ceiling = project._billing_ceiling()
        if committed > ceiling + 0.005:
            text = (
                "planned billing of BDT %.2f stands above the ceiling of BDT %.2f. The lines "
                "cannot go ready: lower them, cancel them, or request a contract variation."
                % (committed, ceiling)
            )
            _note(project, text)
            out["for_a_person"].append("%s: %s" % (project.code, text))


def _decide_if_synthetic(project, comment, out):
    """Approve through the inbox only when the task is with a synthetic holder."""
    request = project.sudo().approval_request_id
    tasks = request.task_ids.filtered(lambda t: t.state == "pending")
    seed_task = tasks.filtered(lambda t: _is_seed_login(t.assigned_user_id))[:1]
    if not seed_task:
        out["for_a_person"].append(
            "%s: approval %s is pending with %s, who is not a synthetic holder."
            % (project.code, request.name, ", ".join(tasks.mapped("assigned_user_id.login")))
        )
        return False
    seed_task.with_user(seed_task.assigned_user_id).action_approve(comment=comment)
    return True


def regularise_projects(env, pm_user, pm_employee, sponsor_user, out):
    """Active with no baseline and no DOFA approval: delivery never had authority. Held
    until it has, approved through the engine, and held still until its gates pass."""
    legacy = env["fix.project"].search(
        [
            ("state", "=", "active"),
            ("budget", ">", 0.0),
            "|",
            ("baseline_budget", "=", False),
            ("baseline_budget", "=", 0.0),
            ("dofa_approved", "=", False),
        ]
    )
    for project in legacy:
        if not project.manager_id:
            project.write({"manager_id": pm_employee.id})
            _note(project, "no manager was named; %s stands in (synthetic)." % pm_employee.name)
        project._guarded().write({"state": "on_hold"})
        _note(
            project,
            "put on hold: it was active with no approved budget and no baseline. It resumes "
            "once its budget is approved and gates G1 and G2 have passed.",
        )
        out["held"].append(project.code)
        if project.approval_state != "pending":
            project.with_user(pm_user).action_request_approval(
                justification="Regularising %s: delivery started before the budget approval "
                "existed. %s." % (project.code, SYNTHETIC)
            )
        _decide_if_synthetic(
            project, "Regularisation decided by a synthetic DOFA holder (seed).", out
        )
        for key in ("g1_initiation", "g2_planning"):
            if not project.gate_ids.filtered(lambda g, k=key: g.gate == k):
                env["fix.project.gate"].with_user(sponsor_user).create(
                    {"project_id": project.id, "gate": key}
                )
        out["for_a_person"].append(
            "%s is on hold: a sponsor decides gates G1 and G2 before it resumes." % project.code
        )


def note_typed_cost(env, out):
    """The old column survives the field's move to a computed value: read it once so the
    note can say what was discarded."""
    env.cr.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = 'fix_project' AND column_name = 'actual_cost'"
    )
    if not env.cr.fetchone():
        return
    env.cr.execute("SELECT id, actual_cost FROM fix_project WHERE actual_cost <> 0")
    for project_id, typed in env.cr.fetchall():
        project = env["fix.project"].browse(project_id).exists()
        if project:
            _note(
                project,
                "a typed actual cost of BDT %.2f is no longer shown: it was not measured from "
                "anything. Cost now comes from ledger postings and task hours." % float(typed),
            )
            out["typed_cost_discarded"].append(project.code)


def replay_dead_handoffs(env, out):
    """The cd_grc consumer dead-lettered every project.risk_escalated on a bug now fixed.
    Reset those deliveries and let the real relay deliver them."""
    consumer = env.ref("cd_grc.consumer_project_risk_escalated", raise_if_not_found=False)
    if not consumer:
        return
    Delivery = env["fix.event.consumer.delivery"].sudo()
    Outbox = env["fix.event.outbox"].sudo()
    Register = env["fix.risk.register"].sudo()
    dead = Delivery.search([("subscription_id", "=", consumer.id), ("state", "=", "dead")])
    events = dead.mapped("event_id")
    before = Register.search_count([])
    if dead:
        dead.write({"state": "failed", "attempts": 0})
        events.write({"relayed_at": False})
    Outbox.cron_relay(limit=5000)
    after = Delivery.search([("subscription_id", "=", consumer.id), ("event_id", "in", events.ids)])
    out["handoffs_redelivered"] = {
        "dead_found": len(dead),
        "now_done": len(after.filtered(lambda d: d.state == "done")),
        "still_not_done": after.filtered(lambda d: d.state != "done").mapped("last_error"),
        "register_rows_added": Register.search_count([]) - before,
    }
    for event in events:
        risk = env["fix.project.risk"].browse(event.aggregate_id).exists()
        if risk:
            _note(
                risk,
                "an earlier note here said the escalation was delivered. It was not: the "
                "register's consumer had failed. It has now been redelivered.",
            )


def _customer(env):
    Partner = env["res.partner"]
    name = "A12 Walk Customer (synthetic)"
    return Partner.search([("name", "=", name)], limit=1) or Partner.create({"name": name})


def _passed_gate(env, project, key, pm_user, sponsor_user):
    gate = (
        env["fix.project.gate"].with_user(pm_user).create({"project_id": project.id, "gate": key})
    )
    gate = gate.with_user(sponsor_user)
    gate.action_record_decision(
        decision="pass",
        checklist_passed=True,
        findings="%s. Reviewed by the synthetic sponsor for the seeded walk." % SYNTHETIC,
    )
    gate.action_hold()
    gate.action_close()


def _walk_to_active(env, name, budget, contract, pm_user, pm_employee, sponsor_user, out):
    """PM raises it, a synthetic tier holder approves it, the sponsor passes its gates."""
    project = (
        env["fix.project"]
        .with_user(pm_user)
        .create(
            {
                "name": name,
                "project_type": "client",
                "manager_id": pm_employee.id,
                "budget": budget,
                "contract_value": contract,
            }
        )
    )
    project.action_request_approval(
        justification="%s: the seeded end-to-end walk of the project lifecycle." % SYNTHETIC
    )
    if not _decide_if_synthetic(project.sudo(), "Decided by a synthetic DOFA holder (seed).", out):
        return None
    _passed_gate(env, project, "g1_initiation", pm_user, sponsor_user)
    _passed_gate(env, project, "g2_planning", pm_user, sponsor_user)
    project.action_activate()
    return project


def _delivered_milestone(env, project, name, pm_user, sponsor_user, engineer, engineer_user):
    milestone = (
        env["fix.project.milestone"]
        .with_user(pm_user)
        .create({"name": name, "project_id": project.id})
    )
    task = (
        env["fix.project.task"]
        .with_user(pm_user)
        .create(
            {
                "name": "%s: build" % name,
                "project_id": project.id,
                "milestone_id": milestone.id,
                "assigned_to": engineer.id,
                "planned_hours": 40.0,
            }
        )
    )
    worker = task.with_user(engineer_user)
    worker.action_start()
    worker.action_log_hours(hours=36.0)
    worker.action_done()
    milestone.with_user(sponsor_user).action_accept(
        acceptance_note="Client sign-off (synthetic walk)"
    )
    milestone.with_user(pm_user).action_complete()
    return milestone


def walk_closed_project(env, pm, sponsor, engineer, finance_user, out):
    """One project from request to a posted invoice, paid and closed, as the real roles."""
    pm_user, pm_employee = pm
    sponsor_user = sponsor[0]
    engineer_user, engineer_employee = engineer
    if env["fix.project"].search_count([("name", "=", WALK_DONE)]):
        out["walk_closed"] = "already walked"
        return
    project = _walk_to_active(
        env, WALK_DONE, 200000.0, 500000.0, pm_user, pm_employee, sponsor_user, out
    )
    if not project:
        return
    milestone = _delivered_milestone(
        env, project, "Network live", pm_user, sponsor_user, engineer_employee, engineer_user
    )
    risk = (
        env["fix.project.risk"]
        .with_user(pm_user)
        .create(
            {
                "project_id": project.id,
                "title": "Cutover falls in the peak service window",
                "probability": "high",
                "impact": "high",
                "owner_id": pm_user.id,
            }
        )
    )
    risk.action_mitigate(mitigation="Cutover moved to a night window with the vendor on call.")
    env["fix.event.outbox"].sudo().cron_relay(limit=5000)
    risk.with_user(sponsor_user).action_close()
    line = (
        env["fix.project.billing"]
        .with_user(pm_user)
        .create(
            {
                "project_id": project.id,
                "milestone_id": milestone.id,
                "customer_id": _customer(env).id,
                "billing_type": "milestone",
                "amount": 150000.0,
                "retention_pct": 10.0,
            }
        )
    )
    line.action_mark_ready()
    try:
        with env.cr.savepoint():
            line.with_user(finance_user).action_mark_invoiced()
    except UserError as exc:
        # The estate refuses to post an invoice it cannot make lawful (a company
        # with no BIN cannot issue a Mushak 6.3). Never invent the missing fact:
        # stop the walk at "ready for Finance" and say what a person must supply.
        out["walk_closed"] = "stopped at ready: invoicing refused"
        out["for_a_person"].append(
            "Project %s line %s is ready to invoice, but posting was refused: %s"
            % (project.name, line.name, exc)
        )
        return
    move = line.sudo().invoice_id
    try:
        with env.cr.savepoint():
            register = (
                env["account.payment.register"]
                .with_context(active_model="account.move", active_ids=move.ids)
                .create({})
            )
            register._create_payments()
            env.flush_all()
    except Exception as exc:  # the walk still proves the invoice; say why it stopped there
        out["for_a_person"].append("%s for %s: %s" % (PAYMENT_NOT_DONE, move.name, exc))
    line.invalidate_recordset()
    project.with_user(finance_user).action_confirm_billing()
    project.with_user(sponsor_user).action_complete()
    out["walk_closed"] = {
        "project": project.code,
        "state": project.state,
        "invoice": move.name,
        "invoice_state": move.state,
        "invoice_total": move.amount_total,
        "billing_state": line.state,
        "risk_on_register": env["fix.risk.register"].search_count([("name", "like", risk.name)]),
    }


def walk_running_project(env, pm, sponsor, engineer, out):
    """One project left mid-flight, so the screens show work waiting for each role: a
    line ready for Finance, a milestone waiting for its sponsor, a gate to decide."""
    pm_user, pm_employee = pm
    sponsor_user = sponsor[0]
    engineer_user, engineer_employee = engineer
    if env["fix.project"].search_count([("name", "=", WALK_RUNNING)]):
        out["walk_running"] = "already walked"
        return
    project = _walk_to_active(
        env, WALK_RUNNING, 800000.0, 1200000.0, pm_user, pm_employee, sponsor_user, out
    )
    if not project:
        return
    delivered = _delivered_milestone(
        env, project, "Racks installed", pm_user, sponsor_user, engineer_employee, engineer_user
    )
    line = (
        env["fix.project.billing"]
        .with_user(pm_user)
        .create(
            {
                "project_id": project.id,
                "milestone_id": delivered.id,
                "customer_id": _customer(env).id,
                "billing_type": "milestone",
                "amount": 300000.0,
            }
        )
    )
    line.action_mark_ready()
    env["fix.project.milestone"].with_user(pm_user).create(
        {"name": "Depot handed over", "project_id": project.id}
    )
    env["fix.project.gate"].with_user(pm_user).create(
        {"project_id": project.id, "gate": "g3_execution"}
    )
    env["fix.project.task"].with_user(pm_user).create(
        {
            "name": "Depot handed over: snag list",
            "project_id": project.id,
            "assigned_to": engineer_employee.id,
            "planned_hours": 16.0,
        }
    )
    out["walk_running"] = {
        "project": project.code,
        "state": project.state,
        "billing_ready_for_finance": line.name,
    }


def run(env):
    """Everything, in dependency order. Returns what changed."""
    missing = [
        login
        for login in REQUIRED_LOGINS
        if not env["res.users"].search_count([("login", "=", login)])
    ]
    if missing:
        raise SystemExit("Run appoint_approvers.py first; missing: %s" % ", ".join(missing))
    out = {
        "codes": [],
        "tasks_unlinked": [],
        "milestones_reopened": [],
        "gates_reset": [],
        "billing_moved_back": [],
        "held": [],
        "typed_cost_discarded": [],
        "handoffs_redelivered": {},
        "walk_closed": None,
        "walk_running": None,
        "for_a_person": [],
    }
    pm = _person(env, PM_LOGIN, "সাকিব হোসেন (Project Manager, synthetic)", PM_GROUP)
    sponsor = _person(env, SPONSOR_LOGIN, "নুসরাত জাহান (Project Sponsor, synthetic)", SPONSOR_GROUP)
    engineer = _person(env, ENGINEER_LOGIN, "রুবেল মিয়া (Project Engineer, synthetic)")
    finance = env["res.users"].search([("login", "=", FINANCE_LOGIN)], limit=1)

    repair_codes(env, out)
    repair_tasks(env, out)
    repair_milestones(env, out)
    repair_gates(env, sponsor[1], out)
    repair_billing(env, out)
    regularise_projects(env, pm[0], pm[1], sponsor[0], out)
    report_over_ceiling(env, out)
    note_typed_cost(env, out)
    replay_dead_handoffs(env, out)
    walk_closed_project(env, pm, sponsor, engineer, finance, out)
    walk_running_project(env, pm, sponsor, engineer, out)
    if not env["ir.config_parameter"].sudo().get_param("fix_ppm.cost_rate_per_hour"):
        out["for_a_person"].append(
            "fix_ppm.cost_rate_per_hour is unset: Finance decides the hourly cost rate. Until "
            "then a project with no tagged ledger postings shows cost as not measured."
        )
    return out


if "env" in globals():
    result = run(env)
    print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
    if os.environ.get("FIX_A12_COMMIT") == "1":
        env.cr.commit()
        print("committed")
    else:
        env.cr.rollback()
        print("rolled back: nothing changed (set FIX_A12_COMMIT=1 to commit)")
