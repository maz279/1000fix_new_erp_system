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
            # A09 round 2: BLA s.31, issued by HR on a cleared exit
            "action_issue_service_certificate",
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
            "action_recall_approval",
            "action_suspend",
            "action_end_suspension",
            "action_withdraw",
        },
    },
    # A09 round 2: BLA s.27(3A) absence without leave. The deemed resignation
    # (action_deem_resigned) is decided from the executive's approval inbox.
    "fix.hr.abandonment": {
        "order": "id desc",
        "limit": 300,
        "actions": {
            "action_issue_notice",
            "action_record_explanation",
            "action_request_approval",
            "action_recall_approval",
            "action_cancel",
        },
    },
    # M21 capture audit 2026-11-17: the departments and job profiles every
    # employee belongs to were on no screen (FR-HCM-020/022).
    "hr.department": {
        # (complete_name is computed, not stored: it cannot order a search)
        "order": "name",
        "limit": 300,
        "actions": set(),
    },
    "hr.job": {
        "order": "name",
        "limit": 500,
        "actions": set(),
    },
    # the employment privacy-notice acknowledgement (FR-HCM-044, BRU-HCM-12)
    "fix.hr.notice.ack": {
        "order": "acknowledged_on desc, id desc",
        "limit": 600,
        "actions": {"action_withdraw"},
    },
    # the structured exit interview (FR-HCM-038)
    "fix.hr.exit.interview": {
        "order": "interview_date desc, id desc",
        "limit": 300,
        "actions": {"action_record"},
    },
    # M21 capture pass 2 (2026-11-19). The line manager's probation review
    # (FR-HCM-029): only an employee on an active probation is offered; the
    # server resolves the contract.
    "fix.hr.probation.review": {
        "order": "review_date desc, id desc",
        "limit": 400,
        "pickers": {"employee_id": [("fix_on_probation", "=", True)]},
        "actions": {"action_submit"},
    },
    # dual role, acting charge, dotted-line manager (FR-HCM-024, BRU-HCM-10):
    # a frozen position takes no dual role
    "fix.hr.additional.assignment": {
        "order": "date_from desc, id desc",
        "limit": 400,
        "pickers": {"position_id": [("frozen", "=", False)]},
        "actions": {"action_approve", "action_end", "action_cancel"},
    },
    # the leaver's knowledge handover (FR-HCM-036): only a live exit is offered
    "fix.hr.exit.handover": {
        "order": "handover_date desc, id desc",
        "limit": 300,
        "pickers": {"exit_id": [("state", "in", ("draft", "notice"))]},
        "actions": {"action_hand_over", "action_accept"},
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


def _today(env):
    from odoo import fields

    return fields.Date.context_today(env.user.with_context(tz=env.user.tz or "Asia/Dhaka"))


def _employees(env, as_of=None):
    """The employees on the books at `as_of` (default today): a leaver keeps
    an active record with `left_date` (the exit records it), so a plain
    search counted every leaver in the headcount (M21 audit)."""
    as_of = as_of or _today(env)
    return env["hr.employee"].search(["|", ("left_date", "=", False), ("left_date", ">", as_of)])


def _period(env, date_from, date_to):
    today = _today(env)
    start = (
        datetime.date.fromisoformat(str(date_from)) if date_from else today.replace(month=1, day=1)
    )
    end = datetime.date.fromisoformat(str(date_to)) if date_to else today
    if end < start:
        start, end = end, start
    return start, end


def _joined_on(env, employees):
    """{employee id: joining date or None}: the master's date, else the
    earliest contract that ran (a contract VERSION is never a joining)."""
    out = {e.id: e.joining_date for e in employees}
    missing = [i for i, d in out.items() if not d]
    if missing:
        contracts = env["fix.employment.contract"].search(
            [
                ("employee_id", "in", missing),
                ("previous_contract_id", "=", False),
                ("state", "in", ("active", "terminated", "expired", "superseded")),
            ],
            order="joining_date asc",
        )
        for c in contracts:
            if not out.get(c.employee_id.id):
                out[c.employee_id.id] = c.joining_date
    return out


def _unit_name(unit) -> str:
    """An operating unit's display name for a report's branch column.

    Read sudo, the NAME only: the caller may read just their own units (record
    rule "Allowed operating units") while the employees they are entitled to
    count sit in branch units, and reading the label as the caller raised an
    AccessError that took the whole aggregate down. Which employees are
    counted is still decided by the caller's own search above — this widens
    nothing but the label."""
    return unit.sudo().name if unit else "Unassigned"


def headcount_movement(env, date_from=None, date_to=None, **params):
    """Headcount and movement for the period, by branch: opening, joiners,
    leavers, transfers in and out, closing.

    It took today's headcount as the closing for any period, counted every
    contract (drafts, versions) as a joiner and ignored transfers out, so the
    columns never reconciled (M21 audit). Now closing = opening + joiners -
    leavers + transfers in - transfers out, row by row."""
    start, end = _period(env, date_from, date_to)
    people = env["hr.employee"].with_context(active_test=False).search([])
    joined = _joined_on(env, people)
    undated = 0
    branches = {}

    def row(key):
        return branches.setdefault(
            key, {"opening": 0, "joiners": 0, "leavers": 0, "t_in": 0, "t_out": 0, "closing": 0}
        )

    for emp in people:
        j = joined.get(emp.id)
        left = emp.left_date
        if not j:
            undated += 1
        if not emp.active and not left:
            continue  # archived without a leaving date: not on the books
        r = row(_unit_name(emp.operating_unit_id))
        if (not j or j < start) and (not left or left >= start):
            r["opening"] += 1
        if j and start <= j <= end:
            r["joiners"] += 1
        if left and start <= left <= end:
            r["leavers"] += 1
        if (not j or j <= end) and (not left or left > end):
            r["closing"] += 1
    moves = env["fix.hr.transfer"].search(
        [("state", "=", "applied"), ("effective_date", ">=", start), ("effective_date", "<=", end)]
    )
    for m in moves:
        src, dst = m.from_operating_unit_id, m.to_operating_unit_id
        if src and dst and src != dst:
            row(_unit_name(dst))["t_in"] += 1
            row(_unit_name(src))["t_out"] += 1
    rows = []
    for key, v in sorted(branches.items()):
        if not any(v.values()):
            continue
        # the branch is today's: a transfer in the period moved the person, so
        # the opening is restated from the closing to keep the row balanced
        opening = v["closing"] - v["joiners"] + v["leavers"] - v["t_in"] + v["t_out"]
        rows.append(
            {
                "branch": key,
                "opening": opening,
                "joiners": v["joiners"],
                "leavers": v["leavers"],
                "transfers_in": v["t_in"],
                "transfers_out": v["t_out"],
                "closing": v["closing"],
            }
        )
    notes = [
        "Closing = opening + joiners - leavers + transfers in - transfers out for each branch. "
        "A leaver counts up to the last working day. A contract version is not a joiner."
    ]
    if undated:
        notes.append(
            "%d employee(s) have no joining date on record or on a contract: they are counted "
            "as present throughout and never as joiners." % undated
        )
    cols = ["branch", "opening", "joiners", "leavers", "transfers_in", "transfers_out", "closing"]
    return _pack(
        "Headcount & Movement — %s to %s" % (start, end),
        cols,
        {
            "branch": "Branch",
            "opening": "Opening",
            "joiners": "Joiners",
            "leavers": "Leavers",
            "transfers_in": "Transfers In",
            "transfers_out": "Transfers Out",
            "closing": "Closing",
        },
        rows,
        notes,
        totals=dict({"branch": "Total"}, **{c: sum(r[c] for r in rows) for c in cols[1:]}),
        empty="No employees registered.",
    )


def attrition_analysis(env, date_from=None, date_to=None, **params):
    """Attrition for the period (default: year to date) by exit type.

    It ignored the period the screen offers and divided by today's headcount,
    which leaves out the very people who left (M21 audit). Now: exits whose
    last working day falls in the period (and has passed), over the average
    of the opening and closing headcount."""
    start, end = _period(env, date_from, date_to)
    today = _today(env)
    exits = env["fix.hr.exit"].search(
        [
            ("state", "in", ("notice", "cleared", "settled")),
            ("last_working_day", ">=", start),
            ("last_working_day", "<=", min(end, today)),
        ]
    )
    opening = len(_employees(env, start - datetime.timedelta(days=1)))
    closing = len(_employees(env, end))
    average = (opening + closing) / 2.0
    groups = {}
    for rec in exits:
        g = groups.setdefault(rec.exit_type, {"count": 0, "branches": set()})
        g["count"] += 1
        if rec.employee_id.operating_unit_id:
            # counted, never shown: the id is enough (no label read as the caller)
            g["branches"].add(rec.employee_id.operating_unit_id.id)
    labels = dict(env["fix.hr.exit"]._fields["exit_type"]._description_selection(env))
    rows = [
        {
            "exit_type": labels.get(k, k),
            "exits": v["count"],
            "branches": len(v["branches"]),
            "share": round(v["count"] / average * 100.0, 1) if average else 0.0,
        }
        for k, v in sorted(groups.items(), key=lambda kv: -kv[1]["count"])
    ]
    total = sum(r["exits"] for r in rows)
    notes = [
        "Leavers are confirmed exits whose last working day fell in the period. The rate "
        "is over the average of the opening (%d) and closing (%d) headcount." % (opening, closing)
    ]
    # the reason for leaving, from the recorded exit interviews (FR-HCM-038)
    # (exit interviews are restricted to HR: a caller who cannot read them
    # gets the rate without the reasons)
    can_read = env["fix.hr.exit.interview"].has_access("read")
    interviews = (
        env["fix.hr.exit.interview"].search(
            [("exit_id", "in", exits.ids), ("state", "=", "recorded")]
        )
        if can_read
        else env["fix.hr.exit.interview"]
    )
    if exits and can_read:
        reasons = dict(
            env["fix.hr.exit.interview"]._fields["primary_reason"]._description_selection(env)
        )
        tally = {}
        for interview in interviews:
            tally[interview.primary_reason] = tally.get(interview.primary_reason, 0) + 1
        notes.append(
            "Main reason for leaving, from %d recorded exit interview(s) of %d leaver(s): %s."
            % (
                len(interviews),
                len(exits),
                "; ".join(
                    "%s %d" % (reasons.get(k, k), n)
                    for k, n in sorted(tally.items(), key=lambda kv: -kv[1])
                )
                or "none recorded",
            )
        )
    return _pack(
        "Attrition Analysis — %s to %s" % (start, end),
        ["exit_type", "exits", "branches", "share"],
        {
            "exit_type": "Exit Type",
            "exits": "Leavers",
            "branches": "Branches Affected",
            "share": "% of Average Headcount",
        },
        rows,
        notes,
        totals={
            "exit_type": "Total",
            "exits": total,
            "share": round(total / average * 100.0, 1) if average else 0.0,
        },
        empty="No leavers in the period.",
    )


def probation_conversion(env, date_from=None, date_to=None, **params):
    """Probation contracts and their conversion window (next 90 days), and the
    employees recorded as probationary who have no probation contract (they
    were invisible to this report and to the KPI)."""
    today = _today(env)
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
    rows.sort(key=lambda r: (r["days_left"] == "—", r["days_left"] if r["days_left"] != "—" else 0))
    on_contract = contracts.mapped("employee_id")
    unrecorded = _employees(env).filtered(
        lambda e: e.employment_type == "probationary" and e not in on_contract
    )
    for emp in unrecorded.sorted("name"):
        rows.append(
            {
                "employee": emp.name,
                "contract": "No probation contract on record",
                "joining": str(emp.joining_date or "—"),
                "probation_end": "—",
                "days_left": "—",
                "due_window": "Unknown",
            }
        )
    due = len([r for r in rows if r["due_window"] == "Yes"])
    notes = [
        "BLA s.4(8): probation is 6 months (clerical) or 3 (others, +3 for a skilled "
        "worker); a worker not decided by the end is deemed permanent by the daily cron."
    ]
    if unrecorded:
        notes.append(
            "%d employee(s) are recorded as probationary with no probation contract: their "
            "probation end cannot be tracked until the contract is recorded." % len(unrecorded)
        )
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
        notes,
        empty="No active probation contracts.",
    )


def establishment_register(env, date_from=None, date_to=None, **params):
    """Establishment register: sanctioned seats vs holders per position, with
    the holders beyond the sanction shown (BRU-HCM-10). Vacant was clipped at
    0, so a position with 1 seat and 133 holders read as simply 'full'."""
    positions = env["fix.org.position"].search([])
    employees = _employees(env)
    rows = []
    for position in positions:
        heads = len(employees.filtered(lambda e, p=position.id: e.position_id.id == p))
        # an approved, current dual role holds a seat too (BRU-HCM-10)
        heads += len(position._fix_dual_role_holders() & employees)
        sanctioned = position.headcount or 0
        empty = max(sanctioned - heads, 0)
        rows.append(
            {
                "position": position.name,
                "grade": position.grade or "—",
                "parent": position.parent_id.name if position.parent_id else "—",
                "sanctioned": sanctioned,
                "filled": heads,
                # a frozen position's empty seats are not vacancies (FR-HCM-023)
                "vacant": 0 if position.frozen else empty,
                "frozen": empty if position.frozen else 0,
                "over": max(heads - sanctioned, 0),
            }
        )
    rows.sort(key=lambda r: (-r["over"], r["position"]))
    over = [r for r in rows if r["over"]]
    notes = [
        "Sanctioned is the position's headcount (BRU-HCM-10: no holder beyond it); "
        "filled counts the employees currently holding it, as their own position or "
        "through an approved dual role. The empty seats of a frozen "
        "position are shown as frozen, not vacant."
    ]
    if over:
        notes.append(
            "%d position(s) hold %d employee(s) beyond their sanctioned seats: the sanctioned "
            "establishment is the business's to set." % (len(over), sum(r["over"] for r in over))
        )
    return _pack(
        "Establishment Register — positions and holders",
        ["position", "grade", "parent", "sanctioned", "filled", "vacant", "frozen", "over"],
        {
            "position": "Position",
            "grade": "Grade",
            "parent": "Reports To",
            "sanctioned": "Sanctioned",
            "filled": "Filled",
            "vacant": "Vacant",
            "frozen": "Frozen Seats",
            "over": "Over Establishment",
        },
        rows,
        notes,
        totals={
            "position": "Total",
            "sanctioned": sum(r["sanctioned"] for r in rows),
            "filled": sum(r["filled"] for r in rows),
            "vacant": sum(r["vacant"] for r in rows),
            "frozen": sum(r["frozen"] for r in rows),
            "over": sum(r["over"] for r in rows),
        },
        empty="No positions defined.",
    )


def org_distribution(env, date_from=None, date_to=None, **params):
    """Org distribution: headcount by branch and position."""
    employees = _employees(env)
    groups = {}
    for emp in employees:
        branch = _unit_name(emp.operating_unit_id)
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


def identity_access_log(env, date_from=None, date_to=None, **params):
    """Who read which employee's NID, birth registration or e-TIN (BRU-HCM-07),
    read as the caller: the log is the HR Manager's, others are refused."""
    from odoo.addons.cd_p03_portal.controllers.p03_generic_api import (
        _datetime_to_local,
        _datetime_to_utc,
    )

    # the dates are the reader's calendar days (UTC+6), the column is UTC
    domain = []
    if date_from:
        domain.append(("read_at", ">=", _datetime_to_utc(env, "%s 00:00:00" % date_from)))
    if date_to:
        domain.append(("read_at", "<=", _datetime_to_utc(env, "%s 23:59:59" % date_to)))
    logs = env["fix.hr.identity.access.log"].search(domain, limit=2000)
    labels = dict(env["fix.hr.identity.access.log"]._fields["field_name"].selection)
    rows = [
        {
            "read_at": _datetime_to_local(env, log.read_at)[:16],
            "user": log.user_id.name,
            "employee": log.employee_name or "",
            "field": labels.get(log.field_name, log.field_name),
            "purpose": log.purpose or "",
            "superuser": "Yes" if log.as_superuser else "No",
        }
        for log in logs
    ]
    return _pack(
        "Identity Read Log — %d reads" % len(rows),
        ["read_at", "user", "employee", "field", "purpose", "superuser"],
        {
            "read_at": "Read At",
            "user": "Read By",
            "employee": "Employee",
            "field": "Identifier",
            "purpose": "Purpose",
            "superuser": "System Context",
        },
        rows,
        [
            "BRU-HCM-07: every read of an NID, birth registration or e-TIN value is logged; "
            "the log is append-only and never shows the value."
        ],
        empty="No identity value was read in the period.",
    )


def data_cleanup(env, date_from=None, date_to=None, **params):
    """Data clean-up findings for the business to decide (read-only)."""
    rows = env["hr.employee"].fix_data_cleanup_findings()
    counts = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    return _pack(
        "Data Clean-up Findings — %d" % len(rows),
        ["category", "employee", "records", "detail"],
        {
            "category": "Finding",
            "employee": "Employee",
            "records": "Records",
            "detail": "Detail",
        },
        [{k: r[k] for k in ("category", "employee", "records", "detail")} for r in rows],
        [
            "Read-only: nothing is changed. Which record survives, which leave is "
            "cancelled and who re-verifies a flag is the business's decision.",
            "; ".join("%s: %d" % kv for kv in sorted(counts.items())) or "No findings.",
        ],
        empty="No clean-up findings.",
    )


REPORTS = {
    "form6a_register": form6a_register,
    "identity_access_log": identity_access_log,
    "data_cleanup": data_cleanup,
    "headcount_movement": headcount_movement,
    "attrition_analysis": attrition_analysis,
    "probation_conversion": probation_conversion,
    "establishment_register": establishment_register,
    "org_distribution": org_distribution,
}


def _technicians(env, employees):
    """The M02 dispatch pool: the Field Service / Technician group's own
    members (the rule the dispatch suggestion uses) — a dispatcher or manager
    the group is implied into, and the Administrator, are not technicians. It
    counted positions whose name contains "tech" (a Technology Head counted, a
    Service Engineer did not)."""
    group = env.ref("cd_field_service.group_fix_field_service_user", raise_if_not_found=False)
    if not group:
        return 0
    users = group.sudo().user_ids.filtered(lambda u: u.active and not u.share)
    return len(employees.filtered(lambda e: e.user_id and e.user_id in users))


def kpis(env):
    employees = _employees(env)
    today = _today(env)
    positions = env["fix.org.position"].search([])
    contracts = env["fix.employment.contract"].search(
        [("contract_type", "=", "probation"), ("state", "=", "active")]
    )
    # A09 M21-13: this counted documents (+4 for one employee). It is the
    # number of employees with a verified service book.
    documents = env["fix.hr.document"].search(
        [("doc_type", "=", "service_book"), ("verified", "=", True)]
    )
    year_start = today.replace(month=1, day=1)
    exits = env["fix.hr.exit"].search(
        [
            ("state", "in", ("notice", "cleared", "settled")),
            ("last_working_day", ">=", year_start),
            ("last_working_day", "<=", today),
        ]
    )
    horizon = today + datetime.timedelta(days=30)
    probation_due = len(
        [c for c in contracts if c.probation_end and today <= c.probation_end <= horizon]
    )
    headcount = len(employees)
    average = (len(_employees(env, year_start - datetime.timedelta(days=1))) + headcount) / 2.0
    holders = {}
    for emp in employees.filtered("position_id"):
        holders[emp.position_id.id] = holders.get(emp.position_id.id, 0) + 1
    # an approved, current dual role takes a seat too (BRU-HCM-10)
    for position in positions:
        dual = position._fix_dual_role_holders() & employees
        if dual:
            holders[position.id] = holders.get(position.id, 0) + len(dual)
    out = {
        "headcount": headcount,
        # leavers YTD over the average headcount (as the Attrition report)
        "attrition_ytd": round(len(exits) / average * 100.0, 1) if average else 0.0,
        "technicians": _technicians(env, employees),
        # vacant seats summed per position: over-filled positions no longer
        # cancel out another position's vacancies
        # (a frozen position's empty seats are not vacancies, FR-HCM-023)
        "open_positions": sum(
            max((p.headcount or 0) - holders.get(p.id, 0), 0) for p in positions if not p.frozen
        ),
        "probation_ending_30d": probation_due,
        "service_books_complete": len(documents.mapped("employee_id") & employees),
    }
    # BRU-HCM-12: employees on the books with no live acknowledgement of the
    # employment privacy notice in force. Withheld (not zero) from a caller
    # who cannot read the acknowledgements.
    if env["fix.hr.notice.ack"].has_access("read"):
        out["privacy_notice_pending"] = len(employees - employees.fix_privacy_notice_acknowledged())
    # KPI-218: probations ending within 30 days with no submitted review from
    # the line manager (FR-HCM-029). Withheld from a caller who cannot read
    # the reviews.
    if env["fix.hr.probation.review"].has_access("read"):
        reviewed = (
            env["fix.hr.probation.review"]
            .search([("contract_id", "in", contracts.ids), ("state", "=", "submitted")])
            .mapped("contract_id")
        )
        out["probation_unreviewed_30d"] = len(
            [
                c
                for c in contracts - reviewed
                if c.probation_end and today <= c.probation_end <= horizon
            ]
        )
    return out
