# A12 · M67 Projects & Portfolio — projects (6 registry types), milestones,
# tasks, stage-gate reviews and portfolio packs.
import datetime

SURFACES = {
    "fix.project": {
        "order": "id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.project.milestone": {
        "order": "due_date, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.project.task": {
        "order": "id desc",
        "limit": 500,
        "actions": set(),
    },
    "fix.project.template": {
        "order": "project_type, name",
        "limit": 100,
        "actions": {"action_instantiate"},
    },
    "fix.project.billing": {
        "order": "due_on desc, id desc",
        "limit": 400,
        "actions": {"action_mark_ready", "action_mark_invoiced"},
    },
    "fix.project.risk": {
        "order": "opened_on desc, id desc",
        "limit": 400,
        "actions": {"action_mitigate", "action_close"},
    },
    "fix.project.gate": {
        "order": "review_on desc, id desc",
        "limit": 300,
        "actions": {"action_hold", "action_close"},
    },
}


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty,
    }


def portfolio_status(env, date_from=None, date_to=None, **params):
    projects = env["fix.project"].sudo().search([])
    rows = [
        {
            "project": p.name,
            "code": p.code or "—",
            "type": dict(p._fields["project_type"].selection).get(p.project_type),
            "manager": p.manager_id.name if p.manager_id else "—",
            "budget": round(float(p.budget or 0.0), 2),
            "actual": round(float(p.actual_cost or 0.0), 2),
            "variance": round(float(p.budget_variance or 0.0), 2),
            "state": dict(p._fields["state"].selection).get(p.state, p.state)
            if "state" in p._fields
            else "—",
        }
        for p in projects
    ]
    return _pack(
        "Portfolio Status — %d project(s)" % len(rows),
        ["project", "code", "type", "manager", "budget", "actual", "variance", "state"],
        {
            "project": "Project",
            "code": "Code",
            "type": "Type",
            "manager": "Manager",
            "budget": "Budget",
            "actual": "Actual",
            "variance": "Variance",
            "state": "State",
        },
        rows,
        ["Variance is the project's own computed budget minus actual."],
        totals={
            "project": "Total",
            "budget": round(sum(r["budget"] for r in rows), 2),
            "actual": round(sum(r["actual"] for r in rows), 2),
            "variance": round(sum(r["variance"] for r in rows), 2),
        },
        empty="No projects registered.",
    )


def milestone_tracker(env, date_from=None, date_to=None, **params):
    milestones = env["fix.project.milestone"].sudo().search([])
    today = datetime.date.today()
    rows = []
    for m in milestones:
        days = (m.due_date - today).days if m.due_date else None
        rows.append(
            {
                "milestone": m.name,
                "project": m.project_id.name,
                "due": str(m.due_date or "—"),
                "days_left": days if days is not None else "—",
                "state": dict(m._fields["state"].selection).get(m.state, m.state)
                if "state" in m._fields
                else "—",
            }
        )
    rows.sort(key=lambda r: r["days_left"] if isinstance(r["days_left"], int) else 9999)
    return _pack(
        "Milestone Tracker",
        ["milestone", "project", "due", "days_left", "state"],
        {
            "milestone": "Milestone",
            "project": "Project",
            "due": "Due",
            "days_left": "Days Left",
            "state": "State",
        },
        rows,
        ["Sorted by days left; negative means overdue."],
        empty="No milestones defined.",
    )


def task_workload(env, date_from=None, date_to=None, **params):
    tasks = env["fix.project.task"].sudo().search([])
    groups = {}
    for t in tasks:
        key = t.assigned_to.name if getattr(t, "assigned_to", False) else "Unassigned"
        groups.setdefault(key, {"open": 0, "done": 0})
        if t.state in ("done", "cancelled"):
            groups[key]["done"] += 1
        else:
            groups[key]["open"] += 1
    rows = [
        {"assignee": k, **v, "total": v["open"] + v["done"]}
        for k, v in sorted(groups.items(), key=lambda kv: -kv[1]["open"])
    ]
    return _pack(
        "Task Workload by Assignee",
        ["assignee", "open", "done", "total"],
        {"assignee": "Assignee", "open": "Open", "done": "Done", "total": "Total"},
        rows,
        ["Counts the recorded tasks; unassigned work is visible in its own row."],
        empty="No project tasks.",
    )


def gate_compliance(env, date_from=None, date_to=None, **params):
    gates = env["fix.project.gate"].sudo().search([])
    rows = [
        {
            "gate": g.name,
            "project": g.project_id.name,
            "gate_stage": dict(g._fields["gate"].selection).get(g.gate),
            "review_on": str(g.review_on),
            "decision": dict(g._fields["decision"].selection).get(g.decision)
            if g.decision
            else "—",
            "checklist": "Passed" if g.checklist_passed else "Not passed",
            "state": dict(g._fields["state"].selection).get(g.state, g.state),
        }
        for g in gates
    ]
    return _pack(
        "Stage-Gate Compliance",
        ["gate", "project", "gate_stage", "review_on", "decision", "checklist", "state"],
        {
            "gate": "Review",
            "project": "Project",
            "gate_stage": "Gate",
            "review_on": "Review On",
            "decision": "Decision",
            "checklist": "Checklist",
            "state": "State",
        },
        rows,
        ["Holding a review requires the decision to be recorded first (model gate)."],
        empty="No stage-gate reviews.",
    )


def budget_vs_actual(env, date_from=None, date_to=None, **params):
    projects = env["fix.project"].sudo().search([])
    rows = [
        {
            "project": p.name,
            "budget": round(float(p.budget or 0.0), 2),
            "actual": round(float(p.actual_cost or 0.0), 2),
            "variance": round(float(p.budget_variance or 0.0), 2),
            "burn_pct": round(float(p.actual_cost or 0.0) / float(p.budget or 1.0) * 100.0, 1),
        }
        for p in projects
        if (p.budget or 0.0)
    ]
    rows.sort(key=lambda r: -r["burn_pct"])
    return _pack(
        "Budget vs Actual",
        ["project", "budget", "actual", "variance", "burn_pct"],
        {
            "project": "Project",
            "budget": "Budget",
            "actual": "Actual",
            "variance": "Variance",
            "burn_pct": "Burn %",
        },
        rows,
        ["Burn = actual over budget; projects with no budget are not shown."],
        empty="No projects with a budget.",
    )


def earned_value(env, date_from=None, date_to=None, **params):
    """Earned value from the project's own budget/actual and milestone state:
    PV = budget x planned time elapsed, EV = budget x completed milestones,
    AC = actual cost. SPI/CPI are stated only where the divisor is non-zero."""
    today = datetime.date.today()
    projects = env["fix.project"].sudo().search([])
    rows = []
    for p in projects:
        if not p.budget:
            continue
        planned_pct = 0.0
        if p.date_start and p.date_end:
            total = (p.date_end - p.date_start).days or 1
            elapsed = (today - p.date_start).days
            planned_pct = max(0.0, min(1.0, elapsed / float(total)))
        milestones = env["fix.project.milestone"].sudo().search([("project_id", "=", p.id)])
        done = len(milestones.filtered(lambda m: m.state == "done"))
        earned_pct = (done / float(len(milestones))) if milestones else 0.0
        pv = round(float(p.budget) * planned_pct, 2)
        ev = round(float(p.budget) * earned_pct, 2)
        ac = round(float(p.actual_cost or 0.0), 2)
        rows.append(
            {
                "project": p.name,
                "budget": round(float(p.budget), 2),
                "pv": pv,
                "ev": ev,
                "ac": ac,
                "spi": round(ev / pv, 2) if pv else None,
                "cpi": round(ev / ac, 2) if ac else None,
            }
        )
    return _pack(
        "Earned Value - %d project(s) with a budget" % len(rows),
        ["project", "budget", "pv", "ev", "ac", "spi", "cpi"],
        {
            "project": "Project",
            "budget": "Budget",
            "pv": "Planned Value",
            "ev": "Earned Value",
            "ac": "Actual Cost",
            "spi": "SPI",
            "cpi": "CPI",
        },
        rows,
        [
            "EV uses the milestone completion ratio (the only progress measure the model holds). "
            "Projects without a budget are excluded rather than shown as zero."
        ],
        empty="No projects with a budget.",
    )


def project_pnl(env, date_from=None, date_to=None, **params):
    projects = env["fix.project"].sudo().search([])
    rows = []
    for p in projects:
        budget = round(float(p.budget or 0.0), 2)
        actual = round(float(p.actual_cost or 0.0), 2)
        variance = round(budget - actual, 2)
        rows.append(
            {
                "project": p.name,
                "type": dict(p._fields["project_type"].selection).get(p.project_type),
                "budget": budget,
                "actual": actual,
                "variance": variance,
                "consumed_pct": round(100.0 * actual / budget, 1) if budget else None,
                "state": dict(p._fields["state"].selection).get(p.state, p.state),
            }
        )
    rows.sort(key=lambda r: -(r["variance"] or 0.0))
    return _pack(
        "Project P&L - budget vs actual",
        ["project", "type", "budget", "actual", "variance", "consumed_pct", "state"],
        {
            "project": "Project",
            "type": "Type",
            "budget": "Budget",
            "actual": "Actual",
            "variance": "Variance",
            "consumed_pct": "Consumed %",
            "state": "State",
        },
        rows,
        [
            "Variance = budget - actual. Consumed % is actual over budget; a project with no "
            "budget shows no percentage."
        ],
        totals={
            "project": "Total",
            "budget": round(sum(r["budget"] for r in rows), 2),
            "actual": round(sum(r["actual"] for r in rows), 2),
            "variance": round(sum(r["variance"] for r in rows), 2),
        },
        empty="No projects.",
    )


def resource_utilisation(env, date_from=None, date_to=None, **params):
    """Resource utilisation: planned vs actual hours per assignee across the task
    board. Utilisation = actual / planned; an assignee with no planned hours shows
    no percentage rather than an assumed 100%."""
    tasks = env["fix.project.task"].sudo().search([])
    groups = {}
    for t in tasks:
        name = t.assigned_to.name if getattr(t, "assigned_to", False) else "Unassigned"
        g = groups.setdefault(name, {"tasks": 0, "planned": 0.0, "actual": 0.0, "open": 0})
        g["tasks"] += 1
        g["planned"] += t.planned_hours or 0.0
        g["actual"] += t.actual_hours or 0.0
        if t.state not in ("done", "cancelled"):
            g["open"] += 1
    rows = [
        {
            "assignee": k,
            "tasks": v["tasks"],
            "open_tasks": v["open"],
            "planned_hours": round(v["planned"], 1),
            "actual_hours": round(v["actual"], 1),
            "variance_hours": round(v["actual"] - v["planned"], 1),
            "utilisation_pct": round(100.0 * v["actual"] / v["planned"], 1)
            if v["planned"]
            else None,
        }
        for k, v in groups.items()
    ]
    rows.sort(key=lambda r: -(r["actual_hours"] or 0))
    return _pack(
        "Resource Utilisation - %d assignee(s), planned vs actual hours" % len(rows),
        [
            "assignee",
            "tasks",
            "open_tasks",
            "planned_hours",
            "actual_hours",
            "variance_hours",
            "utilisation_pct",
        ],
        {
            "assignee": "Assignee",
            "tasks": "Tasks",
            "open_tasks": "Open",
            "planned_hours": "Planned (h)",
            "actual_hours": "Actual (h)",
            "variance_hours": "Variance (h)",
            "utilisation_pct": "Utilisation %",
        },
        rows,
        [
            "Utilisation = actual / planned hours from the task board. An assignee with no "
            "planned hours shows no percentage rather than an assumed 100%."
        ],
        empty="No project tasks recorded.",
    )


def benefits_realisation(env, date_from=None, date_to=None, **params):
    """Benefits realisation: what each project was budgeted, what it has consumed
    and how much of its delivery is complete. A project with no benefit baseline
    recorded says so - the platform does not invent a promised benefit."""
    projects = env["fix.project"].sudo().search([])
    Milestone = env["fix.project.milestone"].sudo()
    rows = []
    for p in projects:
        budget = round(float(p.budget or 0.0), 2)
        actual = round(float(p.actual_cost or 0.0), 2)
        milestones = Milestone.search([("project_id", "=", p.id)])
        done = len(milestones.filtered(lambda m: m.state == "done"))
        deliver_pct = round(100.0 * done / len(milestones), 1) if milestones else None
        rows.append(
            {
                "project": p.name,
                "type": dict(p._fields["project_type"].selection).get(p.project_type),
                "budget": budget,
                "actual": actual,
                "saved": round(budget - actual, 2),
                "milestones_done": "%d/%d" % (done, len(milestones)) if milestones else "-",
                "delivery_pct": deliver_pct,
                "benefit_baseline": "not recorded",
            }
        )
    rows.sort(key=lambda r: -(r["saved"] or 0.0))
    return _pack(
        "Benefits Realisation - %d project(s), delivery against budget" % len(rows),
        [
            "project",
            "type",
            "budget",
            "actual",
            "saved",
            "milestones_done",
            "delivery_pct",
            "benefit_baseline",
        ],
        {
            "project": "Project",
            "type": "Type",
            "budget": "Budget",
            "actual": "Actual",
            "saved": "Budget not consumed",
            "milestones_done": "Milestones",
            "delivery_pct": "Delivery %",
            "benefit_baseline": "Benefit baseline",
        },
        rows,
        [
            "Scope note: the platform records cost and delivery, not a promised benefit figure. "
            "'Budget not consumed' is what the project has not spent, and every row states that no "
            "benefit baseline is recorded rather than presenting spend as a benefit."
        ],
        totals={
            "project": "Total",
            "budget": round(sum(r["budget"] for r in rows), 2),
            "actual": round(sum(r["actual"] for r in rows), 2),
            "saved": round(sum(r["saved"] for r in rows), 2),
        },
        empty="No projects registered.",
    )


REPORTS = {
    "resource_utilisation": resource_utilisation,
    "benefits_realisation": benefits_realisation,
    "portfolio_status": portfolio_status,
    "milestone_tracker": milestone_tracker,
    "task_workload": task_workload,
    "gate_compliance": gate_compliance,
    "budget_vs_actual": budget_vs_actual,
}

REPORTS["earned_value"] = earned_value
REPORTS["project_pnl"] = project_pnl


def kpis(env):
    projects = env["fix.project"].sudo().search([])
    milestones = env["fix.project.milestone"].sudo().search([])
    tasks = env["fix.project.task"].sudo().search([])
    gates = env["fix.project.gate"].sudo().search([])
    today = datetime.date.today()
    return {
        "projects_active": len(
            projects.filtered(
                lambda p: "state" in p._fields and p.state in ("active", "in_progress", "open")
            )
        ),
        "projects_total": len(projects),
        "milestones_due_30d": len(
            milestones.filtered(
                lambda m: m.due_date and today <= m.due_date <= today + datetime.timedelta(days=30)
            )
        ),
        "tasks_open": len(tasks.filtered(lambda t: t.state not in ("done", "cancelled"))),
        "gates_scheduled": len(gates.filtered(lambda g: g.state == "scheduled")),
        "portfolio_budget": round(sum(float(p.budget or 0.0) for p in projects), 2),
    }
