# A09 · M21 Core HR & Lifecycle — surfaces, packs and KPIs over the employee
# master, positions, contracts, movements, exits, statutory documents and
# dependants. First module of the A09 area package.
import datetime

SURFACES = {
    "hr.employee": {
        "order": "name",
        "limit": 500,
        "actions": {
            "action_generate_form7_service_book",
            "action_generate_form6_appointment",
            "action_export_form6a_register",
        },
    },
    "fix.org.position": {
        "order": "name",
        "limit": 300,
        "actions": set(),
    },
    "fix.employment.contract": {
        "order": "employee_id, joining_date desc",
        "limit": 400,
        "actions": {
            "action_activate",
            "action_terminate",
            "action_request_legal_signoff",
            "action_approve_legal_signoff",
            "action_generate_contract_document",
        },
    },
    "fix.hr.transfer": {
        "order": "effective_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_recommend",
            "action_concur",
            "action_tech_eval",
            "action_hr_audit",
            "action_finance_approve",
            "action_approve",
            "action_clear_handover",
            "action_apply",
            "action_cancel",
            "action_reset_draft",
        },
    },
    "fix.hr.exit": {
        "order": "last_working_day desc, id desc",
        "limit": 300,
        "actions": {"action_clear", "action_settle", "action_cancel"},
    },
    "fix.hr.document": {
        "order": "doc_type, employee_id",
        "limit": 400,
        "actions": set(),
    },
    "fix.hr.dependant": {
        "order": "employee_id, name",
        "limit": 400,
        "actions": set(),
    },
    "fix.hr.education": {
        "order": "passing_year desc, employee_id",
        "limit": 500,
        "actions": set(),
    },
    "fix.hr.experience": {
        "order": "end_date desc, employee_id",
        "limit": 500,
        "actions": set(),
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


def _employees(env):
    return env["hr.employee"].search([])


def headcount_movement(env, date_from=None, date_to=None, **params):
    """Headcount and movement for the period: opening, joiners, leavers,
    closing, by branch."""
    today = datetime.date.today()
    start = date_from or str(today.replace(month=1, day=1))
    end = date_to or str(today)
    employees = _employees(env)
    contracts = env["fix.employment.contract"].search([])
    movement = env["fix.hr.transfer"].search(
        [
            ("state", "=", "applied"),
            ("effective_date", ">=", start),
            ("effective_date", "<=", end),
        ]
    )
    exits = env["fix.hr.exit"].search(
        [
            ("state", "in", ("cleared", "settled")),
            ("last_working_day", ">=", start),
            ("last_working_day", "<=", end),
        ]
    )
    rows = []
    branches = {}
    for emp in employees:
        key = emp.operating_unit_id.name if emp.operating_unit_id else "Unassigned"
        branches.setdefault(key, {"head": 0, "joiners": 0, "leavers": 0})
        branches[key]["head"] += 1
    for contract in contracts:
        if contract.joining_date and str(start) <= str(contract.joining_date) <= str(end):
            key = (
                contract.employee_id.operating_unit_id.name
                if contract.employee_id.operating_unit_id
                else "Unassigned"
            )
            branches.setdefault(key, {"head": 0, "joiners": 0, "leavers": 0})
            branches[key]["joiners"] += 1
    for exit_rec in exits:
        key = (
            exit_rec.employee_id.operating_unit_id.name
            if exit_rec.employee_id.operating_unit_id
            else "Unassigned"
        )
        branches.setdefault(key, {"head": 0, "joiners": 0, "leavers": 0})
        branches[key]["leavers"] += 1
    for key, v in sorted(branches.items()):
        opening = v["head"] - v["joiners"] + v["leavers"]
        rows.append(
            {
                "branch": key,
                "opening": max(opening, 0),
                "joiners": v["joiners"],
                "leavers": v["leavers"],
                "transfers": len(
                    movement.filtered(
                        lambda m, k=key: (m.to_operating_unit_id.name or "Unassigned") == k
                    )
                ),
                "closing": v["head"],
            }
        )
    return _pack(
        "Headcount & Movement — %s to %s" % (start, end),
        ["branch", "opening", "joiners", "leavers", "transfers", "closing"],
        {
            "branch": "Branch",
            "opening": "Opening",
            "joiners": "Joiners",
            "leavers": "Leavers",
            "transfers": "Inbound Transfers",
            "closing": "Closing",
        },
        rows,
        [
            "Opening is derived: current headcount minus joiners plus leavers in the period. "
            "Transfers are applied movements into the branch."
        ],
        totals={
            "branch": "Total",
            "opening": sum(r["opening"] for r in rows),
            "joiners": sum(r["joiners"] for r in rows),
            "leavers": sum(r["leavers"] for r in rows),
            "transfers": sum(r["transfers"] for r in rows),
            "closing": sum(r["closing"] for r in rows),
        },
        empty="No employees registered.",
    )


def attrition_analysis(env, date_from=None, date_to=None, **params):
    """Attrition YTD by exit type and branch."""
    today = datetime.date.today()
    year_start = today.replace(month=1, day=1)
    exits = env["fix.hr.exit"].search(
        [("state", "in", ("cleared", "settled")), ("last_working_day", ">=", year_start)]
    )
    head = len(_employees(env))
    groups = {}
    for rec in exits:
        key = rec.exit_type
        g = groups.setdefault(key, {"count": 0, "branches": set()})
        g["count"] += 1
        if rec.employee_id.operating_unit_id:
            g["branches"].add(rec.employee_id.operating_unit_id.name)
    rows = [
        {
            "exit_type": dict(env["fix.hr.exit"]._fields["exit_type"].selection).get(k),
            "exits": v["count"],
            "branches": len(v["branches"]),
            "share": round(v["count"] / head * 100.0, 1) if head else 0.0,
        }
        for k, v in sorted(groups.items(), key=lambda kv: -kv[1]["count"])
    ]
    return _pack(
        "Attrition Analysis — YTD %s" % today.year,
        ["exit_type", "exits", "branches", "share"],
        {
            "exit_type": "Exit Type",
            "exits": "Exits",
            "branches": "Branches Affected",
            "share": "% of Headcount",
        },
        rows,
        ["Attrition YTD = settled/cleared exits over the current headcount."],
        totals={"exit_type": "Total", "exits": sum(r["exits"] for r in rows)},
        empty="No exits recorded this year.",
    )


def probation_conversion(env, date_from=None, date_to=None, **params):
    """Probation contracts and their conversion window (next 90 days)."""
    today = datetime.date.today()
    contracts = env["fix.employment.contract"].search(
        [("contract_type", "=", "probation"), ("state", "=", "active")]
    )
    rows = []
    for contract in contracts:
        days_left = (contract.probation_end - today).days if contract.probation_end else None
        rows.append(
            {
                "employee": contract.employee_id.name,
                "contract": contract.name,
                "joining": str(contract.joining_date or "—"),
                "probation_end": str(contract.probation_end or "—"),
                "days_left": days_left if days_left is not None else "—",
                "due_window": "Yes" if (days_left is not None and 0 <= days_left <= 90) else "No",
            }
        )
    rows.sort(key=lambda r: (r["days_left"] == "—", r["days_left"]))
    due = len([r for r in rows if r["due_window"] == "Yes"])
    return _pack(
        "Probation Conversion — %d due in the next 90 days" % due,
        ["employee", "contract", "joining", "probation_end", "days_left", "due_window"],
        {
            "employee": "Employee",
            "contract": "Contract",
            "joining": "Joined",
            "probation_end": "Probation Ends",
            "days_left": "Days Left",
            "due_window": "Due (90d)",
        },
        rows,
        [
            "Labour Rules 2021 r.25: probation may not exceed 6 months; anything inside "
            "the 90-day window needs a conversion decision."
        ],
        empty="No active probation contracts.",
    )


def establishment_register(env, date_from=None, date_to=None, **params):
    """Establishment register: sanctioned positions vs heads per branch."""
    positions = env["fix.org.position"].search([])
    employees = _employees(env)
    rows = []
    for position in positions:
        heads = len(employees.filtered(lambda e, p=position.id: e.position_id.id == p))
        rows.append(
            {
                "position": position.name,
                "grade": position.grade or "—",
                "parent": position.parent_id.name if position.parent_id else "—",
                "sanctioned": 1,
                "filled": heads,
                "vacant": 1 - heads if heads < 1 else 0,
            }
        )
    rows.sort(key=lambda r: r["position"])
    return _pack(
        "Establishment Register — positions and holders",
        ["position", "grade", "parent", "sanctioned", "filled", "vacant"],
        {
            "position": "Position",
            "grade": "Grade",
            "parent": "Reports To",
            "sanctioned": "Sanctioned",
            "filled": "Filled",
            "vacant": "Vacant",
        },
        rows,
        [
            "One sanctioned head per position record (the model carries no headcount field); "
            "filled counts the employees currently holding it."
        ],
        totals={
            "position": "Total",
            "sanctioned": len(rows),
            "filled": sum(r["filled"] for r in rows),
            "vacant": sum(r["vacant"] for r in rows),
        },
        empty="No positions defined.",
    )


def org_distribution(env, date_from=None, date_to=None, **params):
    """Org distribution: headcount by branch and position."""
    employees = _employees(env)
    groups = {}
    for emp in employees:
        branch = emp.operating_unit_id.name if emp.operating_unit_id else "Unassigned"
        pos = emp.position_id.name if emp.position_id else "No position"
        key = (branch, pos)
        groups[key] = groups.get(key, 0) + 1
    rows = [{"branch": b, "position": p, "headcount": c} for (b, p), c in sorted(groups.items())]
    return _pack(
        "Org Distribution — headcount by branch and position",
        ["branch", "position", "headcount"],
        {"branch": "Branch", "position": "Position", "headcount": "Headcount"},
        rows,
        ["Every employee in one cell; 'No position' is shown honestly."],
        totals={"branch": "Total", "headcount": sum(r["headcount"] for r in rows)},
        empty="No employees registered.",
    )


REPORTS = {
    "headcount_movement": headcount_movement,
    "attrition_analysis": attrition_analysis,
    "probation_conversion": probation_conversion,
    "establishment_register": establishment_register,
    "org_distribution": org_distribution,
}


def kpis(env):
    employees = _employees(env)
    today = datetime.date.today()
    positions = env["fix.org.position"].search([])
    contracts = env["fix.employment.contract"].search(
        [("contract_type", "=", "probation"), ("state", "=", "active")]
    )
    documents = env["fix.hr.document"].search([("doc_type", "=", "service_book")])
    exits = env["fix.hr.exit"].search(
        [
            ("state", "in", ("cleared", "settled")),
            ("last_working_day", ">=", today.replace(month=1, day=1)),
        ]
    )
    horizon = today + datetime.timedelta(days=30)
    probation_due = len(
        [c for c in contracts if c.probation_end and today <= c.probation_end <= horizon]
    )
    filled = len(employees.filtered(lambda e: e.position_id))
    headcount = len(employees)
    return {
        "headcount": headcount,
        "attrition_ytd": round(len(exits) / headcount * 100.0, 1) if headcount else 0.0,
        "technicians": len(
            employees.filtered(
                lambda e: e.position_id and "tech" in (e.position_id.name or "").lower()
            )
        ),
        "open_positions": max(len(positions) - filled, 0),
        "probation_ending_30d": probation_due,
        "service_books_complete": len(documents),
    }
