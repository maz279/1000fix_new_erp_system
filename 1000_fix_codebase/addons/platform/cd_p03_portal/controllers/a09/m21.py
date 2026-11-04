# A09 · M21 Core HR & Lifecycle — surfaces, packs and KPIs over the employee
# master, positions, contracts, movements, exits, statutory documents and
# dependants. First module of the A09 area package.
import datetime

SURFACES = {
    "hr.employee": {
        "order": "name",
        "limit": 500,
        # A09 P0-b: the leaver and the KPI-090 confirmation are on screen
        # (HR / HR manager only, checked by the methods). Form 6(a) is a
        # report pack (REPORTS["form6a_register"]): the action's list result
        # was dropped by the endpoint.
        "actions": {
            "action_generate_form7_service_book",
            "action_generate_form6_appointment",
            "action_generate_id_card",
            "action_record_psr_submission",
            "action_verify_psr",
            "action_mark_psr_exempt",
            "action_mark_left",
            "action_confirm_keycloak_deprovisioned",
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
        # The legal sign-off is decided from Legal Counsel's approval inbox
        # (routed); a contract ends through its exit, never "Terminate".
        "actions": {
            "action_request_legal_signoff",
            "action_recall_approval",
            "action_activate",
            "action_new_version",
            "action_confirm_probation",
            "action_extend_probation",
            "action_generate_contract_document",
        },
    },
    "fix.hr.transfer": {
        "order": "effective_date desc, id desc",
        "limit": 300,
        # The executive approval (action_approve) runs from the inbox only.
        "actions": {
            "action_recommend",
            "action_concur",
            "action_tech_eval",
            "action_hr_audit",
            "action_finance_approve",
            "action_request_approval",
            "action_recall_approval",
            "action_tick_open_jobs",
            "action_tick_toolkit",
            "action_tick_spare_parts",
            "action_tick_storekeeper",
            "action_tick_imprest",
            "action_clear_handover",
            "action_apply",
            "action_cancel",
            "action_reset_draft",
        },
    },
    "fix.hr.exit": {
        "order": "last_working_day desc, id desc",
        "limit": 300,
        # Finance settles from the approval inbox (action_settle is routed).
        "actions": {
            "action_confirm_notice",
            "action_clear_it",
            "action_clear_finance",
            "action_clear_hr",
            "action_clear_assets",
            "action_clear",
            "action_compute_settlement",
            "action_request_approval",
            "action_recall_approval",
            "action_cancel",
            # defined by cd_payroll_bd (M56): pays the pinned settlement
            "action_create_settlement_payment",
        },
    },
    "fix.hr.document": {
        "order": "doc_type, employee_id",
        "limit": 400,
        "actions": {"action_verify", "action_unverify", "action_acknowledge"},
    },
    "fix.hr.dependant": {
        "order": "employee_id, name",
        "limit": 400,
        "actions": set(),
    },
    "fix.hr.education": {
        "order": "passing_year desc, employee_id",
        "limit": 500,
        "actions": {"action_verify_online", "action_verify_physical", "action_flag_discrepancy"},
    },
    "fix.hr.experience": {
        "order": "end_date desc, employee_id",
        "limit": 500,
        "actions": {
            "action_reference_positive",
            "action_reference_neutral",
            "action_reference_negative",
            "action_reference_unreachable",
        },
    },
    # A09 P0-b: the routed master change and the disciplinary case.
    "fix.hr.master.change": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_submit", "action_cancel"},
    },
    "fix.hr.disciplinary.case": {
        "order": "id desc",
        "limit": 300,
        "actions": {
            "action_charge",
            "action_record_explanation",
            "action_hold_hearing",
            "action_start_enquiry",
            "action_conclude_enquiry",
            "action_request_approval",
            "action_suspend",
            "action_end_suspension",
            "action_withdraw",
        },
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
            "BLA s.4(8): probation is 6 months (clerical) or 3 (others, +3 for a skilled "
            "worker); a worker not decided by the end is deemed permanent by the daily cron."
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
        sanctioned = position.headcount or 0
        rows.append(
            {
                "position": position.name,
                "grade": position.grade or "—",
                "parent": position.parent_id.name if position.parent_id else "—",
                "sanctioned": sanctioned,
                "filled": heads,
                "vacant": max(sanctioned - heads, 0),
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
            "Sanctioned is the position's headcount (BRU-HCM-10: no holder beyond it); "
            "filled counts the employees currently holding it."
        ],
        totals={
            "position": "Total",
            "sanctioned": sum(r["sanctioned"] for r in rows),
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


def form6a_register(env, date_from=None, date_to=None, **params):
    """Form 6(a) worker register (BLR 2015 r.20 / BLA s.9), read as the caller:
    the NID column is HR-only, so a non-HR caller is refused, not served."""
    rows = env["hr.employee"].action_export_form6a_register()
    cols = [
        "serial",
        "employee_code",
        "name",
        "father_name",
        "mother_name",
        "nid_number",
        "department",
        "designation",
        "employment_type",
        "joining_date",
        "service_book_number",
    ]
    return _pack(
        "Form 6(a) Worker Register — %d workers" % len(rows),
        cols,
        {
            "serial": "Sl.",
            "employee_code": "Code",
            "name": "Name",
            "father_name": "Father's Name",
            "mother_name": "Mother's Name",
            "nid_number": "NID",
            "department": "Department",
            "designation": "Designation",
            "employment_type": "Employment Nature",
            "joining_date": "Joining Date",
            "service_book_number": "Service Book No",
        },
        rows,
        ["Labour Rules 2015 r.20: the register of workers (Form 6(a))."],
        empty="No employees registered.",
    )


REPORTS = {
    "form6a_register": form6a_register,
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
    # A09 M21-13: this counted documents (+4 for one employee). It is the
    # number of employees with a verified service book.
    documents = env["fix.hr.document"].search(
        [("doc_type", "=", "service_book"), ("verified", "=", True)]
    )
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
        "open_positions": max(sum(positions.mapped("headcount")) - filled, 0),
        "probation_ending_30d": probation_due,
        "service_books_complete": len(documents.mapped("employee_id") & employees),
    }
