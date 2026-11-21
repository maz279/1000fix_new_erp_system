# A06 · M41 Warehouse Management — surfaces, packs and KPIs over the structure
# models and the slotting/dock/put-away/wave/packing/staging/task models.
# Stock totals are M15's ledger; a bin slot is a breakdown of it, moved only
# by put-away, pick and approved counts (BRU-WMS-01).
#
# A06 audit (2026-11-03): the KPIs read sudo().search([]) across companies
# and counted forged tasks and typed picks; the surface served fix.spare.part
# and the valuation suspense with their quantity and status open to writes.
# Every read below is the CALLER's, in env.companies; productivity and pick
# accuracy count only work the system recorded as executed (a done task with
# its operative, a line picked by the wave). The M15 records served here are
# read-only through this surface (their forms offer no ledger field).
import datetime

from odoo import fields

SURFACES = {
    "fix.warehouse.bin": {
        "order": "zone_id, name",
        "limit": 400,
        "actions": {"action_block", "action_unblock", "action_report_block"},
    },
    "fix.warehouse.zone": {"order": "warehouse_id, name", "limit": 200, "actions": set()},
    "fix.wms.slot": {
        "order": "bin_id, part_id",
        "limit": 400,
        "actions": {
            "action_block",
            "action_unblock",
            "action_raise_replenishment",
            "action_report_block",
        },
    },
    "fix.wms.dock": {
        "order": "slot_start desc, id desc",
        "limit": 200,
        "actions": {"action_check_in", "action_start_unload", "action_complete", "action_cancel"},
    },
    "fix.wms.putaway": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_complete",
            "action_direct",
            "action_approve_override",
            "action_reject_override",
            "action_report_exception",
            "action_cancel",
        },
    },
    "fix.wms.wave": {
        "order": "wave_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_release",
            "action_pick_all",
            "action_accept_short",
            "action_packed",
            "action_stage",
            "action_ship",
            "action_cancel",
        },
    },
    "fix.wms.wave.line": {
        "order": "wave_id, id",
        "limit": 400,
        "actions": {"action_scan_pick", "action_scan_short_pick"},
    },
    "fix.wms.carton": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_seal"},
    },
    "fix.wms.stage": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_load", "action_dispatch"},
    },
    "fix.wms.task": {
        "order": "create_date desc, id desc",
        "limit": 400,
        "actions": {"action_claim", "action_assign", "action_done", "action_cancel"},
    },
    "fix.wms.floor.count": {
        "order": "counted_on desc, id desc",
        "limit": 300,
        "actions": {"action_post"},
    },
    "fix.wms.wave.template": {"order": "name", "limit": 200, "actions": set()},
    "fix.wms.packing.station": {"order": "name", "limit": 200, "actions": set()},
    "fix.stock.location": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_set_active", "action_set_inactive", "action_audit_van_stock"},
    },
    # F32 (A06 ERP audit): no cost in M41 (spec section 13): the valuation
    # suspense list and the standard-cost action are M15's, not this surface's
    "fix.warehouse": {"order": "id desc", "limit": 400, "actions": {"action_propose_slotting"}},
    # capture audit 2026-11-14: internal moves, RF devices, operatives, equipment
    "fix.wms.move": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_confirm", "action_cancel"},
    },
    "fix.wms.device": {
        "order": "warehouse_id, device_code",
        "limit": 200,
        "actions": {"action_deactivate", "action_reactivate"},
    },
    "fix.wms.operative": {"order": "warehouse_id, employee_id", "limit": 300, "actions": set()},
    "fix.wms.equipment": {"order": "warehouse_id, code", "limit": 300, "actions": set()},
    # capture pass 2 (2026-11-19): the spec records behind the buttons
    "fix.wms.bin.block.log": {"order": "at desc, id desc", "limit": 300, "actions": set()},
    "fix.wms.putaway.exception": {
        "order": "reported_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.wms.dock.door": {"order": "warehouse_id, code", "limit": 200, "actions": set()},
    "fix.wms.handling.unit": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_close", "action_store", "action_dissolve"},
    },
    "fix.wms.handling.unit.line": {"order": "hu_id, id", "limit": 400, "actions": set()},
    "fix.wms.crossdock": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_confirm", "action_dispatch", "action_cancel"},
    },
    "fix.wms.return.receipt": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_dispose"},
    },
    "fix.wms.outbound.demand": {
        "order": "state, priority desc, cutoff_at, id",
        "limit": 400,
        "actions": {"action_build_wave", "action_cancel"},
    },
    "fix.wms.count.plan": {
        "order": "planned_on desc, id desc",
        "limit": 200,
        "actions": {"action_generate", "action_close", "action_cancel"},
    },
    "fix.wms.time.standard": {
        "order": "warehouse_id, task_type, zone_id",
        "limit": 200,
        "actions": set(),
    },
    "fix.wms.productivity.run": {
        "order": "date_to desc, id desc",
        "limit": 200,
        "actions": {"action_compute"},
    },
    "fix.wms.productivity": {
        "order": "date desc, operative_id, task_type",
        "limit": 400,
        "actions": set(),
    },
    # part 2 (2026-11-20): substitution, slotting proposals, scan log, RF journal
    "fix.wms.substitution": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_reject"},
    },
    "fix.wms.slot.proposal": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_accept", "action_reject"},
    },
    "fix.wms.scan.event": {"order": "occurred_at desc, id desc", "limit": 500, "actions": set()},
    "fix.wms.rf.journal": {"order": "processed_at desc, id desc", "limit": 400, "actions": set()},
    # A06 ERP audit O2 / F07: the supervisor's opening bin positions
    "fix.wms.slot.load": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_load", "action_cancel"},
    },
}


DHAKA = datetime.timedelta(hours=6)  # Asia/Dhaka wall time = UTC + 6, no DST
EPS = 1e-6
SHIFTS = (("Morning (06–14)", 6, 14), ("Afternoon (14–22)", 14, 22))


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


def _mine(env, model, domain=None, **kw):
    """The caller's records of this model in the companies they work in."""
    records = env[model]
    company = [("company_id", "in", env.companies.ids)] if "company_id" in records._fields else []
    return records.search(company + list(domain or []), **kw)


def _day(value):
    if not value:
        return None
    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        return value
    return datetime.date.fromisoformat(str(value)[:10])


def _period(field, date_from=None, date_to=None):
    """F14: ``field`` (a UTC datetime) within the Dhaka days date_from..date_to."""
    domain = []
    start, end = _day(date_from), _day(date_to)
    if start:
        domain.append((field, ">=", datetime.datetime.combine(start, datetime.time.min) - DHAKA))
    if end:
        stop = datetime.datetime.combine(end + datetime.timedelta(days=1), datetime.time.min)
        domain.append((field, "<", stop - DHAKA))
    return domain


def _period_note(date_from=None, date_to=None):
    if not (date_from or date_to):
        return "Period: all dates (Asia/Dhaka days)."
    return "Period: %s to %s (Asia/Dhaka days)." % (date_from or "start", date_to or "today")


def _local(dt):
    """The Dhaka wall time of a stored UTC datetime."""
    return dt + DHAKA if dt else dt


def _shift(dt):
    hour = _local(dt).hour
    for label, start, stop in SHIFTS:
        if start <= hour < stop:
            return label
    return "Night (22–06)"


def _executed(tasks):
    """Tasks the system recorded as done by an operative, that moved or counted
    something (F27: a typed task closed with nothing behind it is not work)."""
    return tasks.filtered(
        lambda t: t.state == "done"
        and t.done_at
        and t.done_by_id
        and (t.wave_line_id or t.putaway_id or t.move_id or t.floor_count_id)
    )


def _requested(line):
    return line.requested_qty or line.qty or 0.0


def _picked_lines(env, date_from=None, date_to=None):
    """Wave lines the wave itself picked (picked_by / picked_at set)."""
    waves = _mine(env, "fix.wms.wave")
    return env["fix.wms.wave.line"].search(
        [
            ("wave_id", "in", waves.ids),
            ("picked_at", "!=", False),
            *_period("picked_at", date_from, date_to),
        ]
    )


def _state(record, field="state"):
    return dict(record._fields[field].selection).get(record[field])


def _hours(start, stop):
    if not (start and stop) or stop < start:
        return None
    return round((stop - start).total_seconds() / 3600.0, 2)


def throughput_by_shift(env, date_from=None, date_to=None, **params):
    tasks = _executed(_mine(env, "fix.wms.task", _period("done_at", date_from, date_to)))
    buckets = {}
    for task in tasks:
        key = (str(_local(task.done_at).date()), _shift(task.done_at))
        row = buckets.setdefault(key, {"date": key[0], "shift": key[1], "tasks": 0, "qty": 0.0})
        row["tasks"] += 1
        row["qty"] += task.qty or 0.0
    rows = []
    for row in buckets.values():
        row["qty"] = round(row["qty"], 3)
        rows.append(row)
    rows.sort(key=lambda r: (r["date"], r["shift"]), reverse=True)
    return _pack(
        "Throughput by Shift — completed warehouse tasks",
        ["date", "shift", "tasks", "qty"],
        {"date": "Date (Dhaka)", "shift": "Shift", "tasks": "Tasks", "qty": "Quantity"},
        rows,
        [
            "Shift buckets are the Dhaka hour the task was done (06–14, 14–22, 22–06); only "
            "tasks that moved or counted stock.",
            _period_note(date_from, date_to),
        ],
        totals={
            "date": "Total",
            "tasks": sum(r["tasks"] for r in rows),
            "qty": round(sum(r["qty"] for r in rows), 3),
        },
        empty="No completed warehouse tasks in the period.",
    )


def pick_accuracy(env, date_from=None, date_to=None, **params):
    """F14: against what the line FIRST asked for (requested_qty), which no
    accepted short, re-source or substitution rewrites."""
    lines = _picked_lines(env, date_from, date_to)
    rows = []
    exact = 0
    for line in lines:
        asked = _requested(line)
        picked = line.picked_qty or 0.0
        ok = abs(picked - asked) <= EPS and not line.resourced_from_id
        exact += 1 if ok else 0
        rows.append(
            {
                "wave": line.wave_id.name,
                "part": line.part_id.part_number,
                "bin": line.bin_id.name if line.bin_id else "—",
                "requested": round(asked, 3),
                "picked": round(picked, 3),
                "short": round(max(asked - picked, 0.0), 3),
                "accuracy_pct": round((picked / asked) * 100.0, 1) if asked else 0.0,
                "exact": "yes" if ok else "no",
                "state": _state(line),
            }
        )
    rows.sort(key=lambda r: r["accuracy_pct"])
    total_req = sum(r["requested"] for r in rows)
    total_picked = sum(r["picked"] for r in rows)
    return _pack(
        "Pick Accuracy Trend — picked against what each line asked for",
        ["wave", "part", "bin", "requested", "picked", "short", "accuracy_pct", "exact", "state"],
        {
            "wave": "Wave",
            "part": "Part",
            "bin": "Bin",
            "requested": "Requested",
            "picked": "Picked",
            "short": "Short",
            "accuracy_pct": "Fill %",
            "exact": "Picked Exactly",
            "state": "State",
        },
        rows,
        [
            "Line accuracy: %.1f%% of %d picked lines were picked exactly as first requested; "
            "quantity fill %.1f%%. A short that was accepted, re-sourced or substituted still "
            "counts against the original request."
            % (
                (exact / len(lines)) * 100.0 if lines else 0.0,
                len(lines),
                (total_picked / total_req) * 100.0 if total_req else 0.0,
            ),
            _period_note(date_from, date_to),
        ],
        totals={
            "wave": "Total",
            "requested": round(total_req, 3),
            "picked": round(total_picked, 3),
            "short": round(total_req - total_picked, 3),
        },
        empty="No picked wave lines in the period.",
    )


def wave_cycle_time(env, date_from=None, date_to=None, **params):
    waves = _mine(env, "fix.wms.wave", _period("released_at", date_from, date_to))
    rows = []
    for wave in waves:
        hours = _hours(wave.released_at, wave.shipped_at)
        rows.append(
            {
                "wave": wave.name,
                "date": str(wave.wave_date),
                "strategy": _state(wave, "strategy"),
                "lines": len(wave.line_ids),
                "short": len(
                    wave.line_ids.filtered(
                        lambda ln: ln.picked_at and (ln.picked_qty or 0.0) + EPS < _requested(ln)
                    )
                ),
                "released": str(_local(wave.released_at))[:16] if wave.released_at else "—",
                "shipped": str(_local(wave.shipped_at))[:16] if wave.shipped_at else "—",
                "cycle_hours": "—" if hours is None else hours,
                "state": _state(wave),
            }
        )
    rows.sort(key=lambda r: str(r["wave"]), reverse=True)
    return _pack(
        "Wave Cycle Time — released to shipped",
        [
            "wave",
            "date",
            "strategy",
            "lines",
            "short",
            "released",
            "shipped",
            "cycle_hours",
            "state",
        ],
        {
            "wave": "Wave",
            "date": "Date",
            "strategy": "Strategy",
            "lines": "Lines",
            "short": "Lines Short",
            "released": "Released (Dhaka)",
            "shipped": "Shipped (Dhaka)",
            "cycle_hours": "Cycle (h)",
            "state": "State",
        },
        rows,
        [
            "Cycle hours = shipped − released; an open wave shows '—'. Waves released in the "
            "period.",
            _period_note(date_from, date_to),
        ],
        empty="No waves released in the period.",
    )


def labour_productivity(env, date_from=None, date_to=None, **params):
    rows = []
    by_emp = {}
    for task in _executed(_mine(env, "fix.wms.task", _period("done_at", date_from, date_to))):
        key = task.assignee_id.name if task.assignee_id else "Unassigned"
        row = by_emp.setdefault(key, {"assignee": key, "tasks": 0, "qty": 0.0})
        row["tasks"] += 1
        row["qty"] += task.qty or 0.0
    for row in by_emp.values():
        row["qty"] = round(row["qty"], 3)
        rows.append(row)
    rows.sort(key=lambda r: -r["tasks"])
    return _pack(
        "Labour Productivity — completed tasks per operator",
        ["assignee", "tasks", "qty"],
        {"assignee": "Operator", "tasks": "Tasks Done", "qty": "Quantity Moved"},
        rows,
        [
            "Completed tasks that moved or counted stock; a task without an assignee counts "
            "under Unassigned.",
            _period_note(date_from, date_to),
        ],
        totals={
            "assignee": "Total",
            "tasks": sum(r["tasks"] for r in rows),
            "qty": round(sum(r["qty"] for r in rows), 3),
        },
        empty="No completed tasks with an operator in the period.",
    )


def _bins(env):
    return env["fix.warehouse.bin"].search(
        [("zone_id.warehouse_id.company_id", "in", env.companies.ids)]
    )


def bin_utilisation(env, date_from=None, date_to=None, **params):
    bins = _bins(env)
    slots = env["fix.wms.slot"].search([("bin_id", "in", bins.ids)])
    rows = []
    for bin_record in bins:
        bin_slots = slots.filtered(lambda s, bid=bin_record.id: s.bin_id.id == bid)
        qty = sum(bin_slots.mapped("qty"))
        capacity = bin_record.capacity_qty or 0.0
        rows.append(
            {
                "bin": bin_record.name,
                "zone": bin_record.zone_id.name,
                "capacity": round(capacity, 3) if capacity else "unconstrained",
                "slotted_qty": round(qty, 3),
                "skus": len(bin_slots),
                "utilisation_pct": round((qty / capacity) * 100.0, 1) if capacity else "—",
            }
        )
    rows.sort(
        key=lambda r: -(r["utilisation_pct"] if isinstance(r["utilisation_pct"], float) else -1)
    )
    constrained = [r for r in rows if isinstance(r["capacity"], float)]
    cap_total = sum(r["capacity"] for r in constrained)
    held = sum(r["slotted_qty"] for r in constrained)
    return _pack(
        "Bin Utilisation Heatmap — slotted quantity against capacity",
        ["bin", "zone", "capacity", "slotted_qty", "skus", "utilisation_pct"],
        {
            "bin": "Bin",
            "zone": "Zone",
            "capacity": "Capacity",
            "slotted_qty": "Slotted Qty",
            "skus": "SKUs",
            "utilisation_pct": "Utilisation %",
        },
        rows,
        [
            "F14: utilisation is measured over the %d bins that have a capacity (%.1f%%); "
            "unconstrained bins are listed but never averaged in."
            % (len(constrained), (held / cap_total) * 100.0 if cap_total else 0.0),
            "As at now (a bin's contents have no history).",
        ],
        totals={
            "bin": "Total (constrained bins)",
            "capacity": round(cap_total, 3),
            "slotted_qty": round(held, 3),
            "skus": sum(r["skus"] for r in rows),
        },
        empty="No bins yet.",
    )


def pick_strategy(env, date_from=None, date_to=None, **params):
    slots = env["fix.wms.slot"].search([("bin_id", "in", _bins(env).ids)])
    tasks = _mine(
        env, "fix.wms.task", [("task_type", "=", "pick"), ("state", "in", ("open", "assigned"))]
    )
    rows = []
    for slot in slots:
        open_picks = tasks.filtered(
            lambda t, s=slot: t.part_id.id == s.part_id.id and t.bin_id.id == s.bin_id.id
        )
        rows.append(
            {
                "zone": slot.bin_id.zone_id.name,
                "bin": slot.bin_id.name,
                "part": slot.part_id.part_number,
                "velocity": _state(slot, "velocity"),
                "slot_type": _state(slot, "slot_type"),
                "open_picks": len(open_picks),
            }
        )
    rows.sort(key=lambda r: (r["zone"], r["bin"]))
    return _pack(
        "Pick Strategies — slot layout against open pick work",
        ["zone", "bin", "part", "velocity", "slot_type", "open_picks"],
        {
            "zone": "Zone",
            "bin": "Bin",
            "part": "Part",
            "velocity": "Velocity",
            "slot_type": "Slot Type",
            "open_picks": "Open Picks",
        },
        rows,
        [
            "Strategy view: fast movers should sit in pick-face bins; the open pick count is "
            "live from the task queue. Quantities are not shown: floor counts are blind.",
        ],
        empty="No slots yet.",
    )


def rf_queue(env, date_from=None, date_to=None, **params):
    tasks = _mine(env, "fix.wms.task", [("state", "in", ("open", "assigned"))])
    rows = []
    for task in tasks:
        rows.append(
            {
                "task": task.name,
                "type": _state(task, "task_type"),
                "ref": task.ref or "—",
                "part": task.part_id.part_number if task.part_id else "—",
                "bin": task.bin_id.name if task.bin_id else "—",
                "qty": round(task.qty or 0.0, 3),
                "assignee": task.assignee_id.name if task.assignee_id else "—",
                "state": _state(task),
            }
        )
    rows.sort(key=lambda r: (r["state"], r["task"]))
    return _pack(
        "RF Queue — open and assigned tasks for the handheld",
        ["task", "type", "ref", "part", "bin", "qty", "assignee", "state"],
        {
            "task": "Task",
            "type": "Type",
            "ref": "Reference",
            "part": "Part",
            "bin": "Bin",
            "qty": "Qty",
            "assignee": "Assignee",
            "state": "State",
        },
        rows,
        ["This is the RF device's work list: open tasks first, then assigned ones. As at now."],
        empty="No open warehouse tasks.",
    )


def scan_violations(env, date_from=None, date_to=None, **params):
    """Spec section 14 "Ownership-class segregation": the scans the floor
    REFUSED, by rule and operative (BRU-WMS-03 class, -05 wrong bin or item,
    -11 hazard, -12 blocked bin ...), from the scan log."""
    events = _mine(
        env,
        "fix.wms.scan.event",
        [("accepted", "=", False), *_period("occurred_at", date_from, date_to)],
    )
    buckets = {}
    for ev in events:
        key = (ev.rule or "refused", ev.user_name or "-")
        row = buckets.setdefault(
            key,
            {"rule": key[0], "operative": key[1], "attempts": 0, "last": "", "example": ""},
        )
        row["attempts"] += 1
        stamp = str(_local(ev.occurred_at) or "")
        if stamp > row["last"]:
            row["last"], row["example"] = stamp[:16], (ev.message or "")[:120]
    rows = sorted(buckets.values(), key=lambda r: (-r["attempts"], r["rule"], r["operative"]))
    return _pack(
        "Attempted Violations - scans the floor refused",
        ["rule", "operative", "attempts", "last", "example"],
        {
            "rule": "Rule",
            "operative": "Operative",
            "attempts": "Attempts",
            "last": "Last Attempt (Dhaka)",
            "example": "Last Reason",
        },
        rows,
        [
            "BRU-WMS-03 is the ownership-class segregation the spec's report counts; "
            "BRU-WMS-05 a wrong bin or item scan; BRU-WMS-11 hazard; BRU-WMS-12 a blocked bin.",
            "Refused attempts are logged in their own transaction, so they survive the refusal.",
            _period_note(date_from, date_to),
        ],
        totals={"rule": "Total", "attempts": sum(r["attempts"] for r in rows)},
        empty="No refused scan in the period.",
    )


# ------------------------------------------------------------------ F15
def override_report(env, date_from=None, date_to=None, **params):
    """BRU-WMS-06: the daily override report: every put-away that went to
    another bin than the directive's, with its reason and who approved it."""
    putaways = _mine(
        env,
        "fix.wms.putaway",
        [("override_state", "!=", "none"), *_period("create_date", date_from, date_to)],
    )
    reasons = dict(env["fix.wms.putaway"]._fields["override_reason"].selection)
    rows = [
        {
            "date": str(_local(pa.create_date).date()),
            "putaway": pa.name,
            "part": pa.part_id.part_number,
            "directed": pa.directed_bin_id.name or "(none)",
            "actual": pa.to_bin_id.name or "—",
            "reason": reasons.get(pa.override_reason, "—"),
            "note": pa.override_note or "",
            "by": pa.override_by_id.name or "—",
            "approved_by": pa.override_approved_by_id.name or "—",
            "state": _state(pa, "override_state"),
        }
        for pa in putaways
    ]
    rows.sort(key=lambda r: (r["date"], r["putaway"]), reverse=True)
    return _pack(
        "Daily Override Report — put-aways against the directive (BRU-WMS-06)",
        [
            "date",
            "putaway",
            "part",
            "directed",
            "actual",
            "reason",
            "note",
            "by",
            "approved_by",
            "state",
        ],
        {
            "date": "Date (Dhaka)",
            "putaway": "Put-Away",
            "part": "Part",
            "directed": "Directed Bin",
            "actual": "Actual Bin",
            "reason": "Reason",
            "note": "Note",
            "by": "Overridden By",
            "approved_by": "Approved By",
            "state": "Override",
        },
        rows,
        [_period_note(date_from, date_to)],
        totals={"date": "Total", "putaway": len(rows)},
        empty="No override in the period.",
    )


def short_pick_rate(env, date_from=None, date_to=None, **params):
    lines = _picked_lines(env, date_from, date_to)
    days = {}
    for line in lines:
        key = str(_local(line.picked_at).date())
        row = days.setdefault(key, {"date": key, "lines": 0, "short": 0, "short_qty": 0.0})
        row["lines"] += 1
        gap = _requested(line) - (line.picked_qty or 0.0)
        if gap > EPS:
            row["short"] += 1
            row["short_qty"] += gap
    rows = []
    for row in days.values():
        row["rate_pct"] = round(100.0 * row["short"] / row["lines"], 1) if row["lines"] else 0.0
        row["short_qty"] = round(row["short_qty"], 3)
        rows.append(row)
    rows.sort(key=lambda r: r["date"], reverse=True)
    total, short = sum(r["lines"] for r in rows), sum(r["short"] for r in rows)
    return _pack(
        "Short-Pick Rate — lines picked short of their request",
        ["date", "lines", "short", "short_qty", "rate_pct"],
        {
            "date": "Date (Dhaka)",
            "lines": "Lines Picked",
            "short": "Lines Short",
            "short_qty": "Quantity Short",
            "rate_pct": "Short-Pick Rate %",
        },
        rows,
        [
            "Overall %.1f%% of %d lines." % (100.0 * short / total if total else 0.0, total),
            _period_note(date_from, date_to),
        ],
        totals={"date": "Total", "lines": total, "short": short},
        empty="No picked lines in the period.",
    )


def cycle_times(env, date_from=None, date_to=None, **params):
    """Spec section 14 inbound cycle time and wave analysis: dock arrival to
    completion, receipt posting to put-away, wave release to shipment."""
    rows = []
    for dock in _mine(env, "fix.wms.dock", _period("arrived_at", date_from, date_to)):
        rows.append(
            {
                "stage": "Dock: arrival to unloaded",
                "ref": dock.name,
                "start": str(_local(dock.arrived_at))[:16],
                "end": str(_local(dock.completed_at))[:16] if dock.completed_at else "—",
                "hours": _hours(dock.arrived_at, dock.completed_at),
            }
        )
    for pa in _mine(
        env,
        "fix.wms.putaway",
        [("state", "=", "done"), *_period("done_at", date_from, date_to)],
    ):
        posted = pa.receipt_line_id.receipt_id.posted_at
        rows.append(
            {
                "stage": "Receipt posted to put away",
                "ref": pa.name,
                "start": str(_local(posted))[:16] if posted else "—",
                "end": str(_local(pa.done_at))[:16],
                "hours": _hours(posted, pa.done_at),
            }
        )
    for wave in _mine(env, "fix.wms.wave", _period("shipped_at", date_from, date_to)):
        rows.append(
            {
                "stage": "Wave released to shipped",
                "ref": wave.name,
                "start": str(_local(wave.released_at))[:16] if wave.released_at else "—",
                "end": str(_local(wave.shipped_at))[:16],
                "hours": _hours(wave.released_at, wave.shipped_at),
            }
        )
    notes = []
    for stage in (
        "Dock: arrival to unloaded",
        "Receipt posted to put away",
        "Wave released to shipped",
    ):
        values = [r["hours"] for r in rows if r["stage"] == stage and r["hours"] is not None]
        notes.append(
            "%s: %d measured, average %.2f h."
            % (stage, len(values), sum(values) / len(values) if values else 0.0)
        )
    for row in rows:
        if row["hours"] is None:
            row["hours"] = "—"
    notes.append(_period_note(date_from, date_to))
    return _pack(
        "Cycle Times — inbound, put-away and outbound",
        ["stage", "ref", "start", "end", "hours"],
        {
            "stage": "Stage",
            "ref": "Record",
            "start": "Start (Dhaka)",
            "end": "End (Dhaka)",
            "hours": "Hours",
        },
        rows,
        notes,
        empty="Nothing completed in the period.",
    )


def putaway_compliance(env, date_from=None, date_to=None, **params):
    putaways = _mine(
        env, "fix.wms.putaway", [("state", "=", "done"), *_period("done_at", date_from, date_to)]
    )
    exceptions = _mine(env, "fix.wms.putaway.exception", _period("reported_at", date_from, date_to))
    days = {}
    for pa in putaways:
        key = str(_local(pa.done_at).date())
        row = days.setdefault(
            key, {"date": key, "done": 0, "directed": 0, "overridden": 0, "exceptions": 0}
        )
        row["done"] += 1
        if pa.override_state == "none" and pa.to_bin_id == pa.directed_bin_id:
            row["directed"] += 1
        else:
            row["overridden"] += 1
    for exc in exceptions:
        key = str(_local(exc.reported_at).date())
        row = days.setdefault(
            key, {"date": key, "done": 0, "directed": 0, "overridden": 0, "exceptions": 0}
        )
        row["exceptions"] += 1
    rows = []
    for row in days.values():
        row["compliance_pct"] = (
            round(100.0 * row["directed"] / row["done"], 1) if row["done"] else 0.0
        )
        rows.append(row)
    rows.sort(key=lambda r: r["date"], reverse=True)
    causes = {}
    labels = dict(env["fix.wms.putaway.exception"]._fields["cause"].selection)
    for exc in exceptions:
        causes[labels.get(exc.cause, exc.cause)] = (
            causes.get(labels.get(exc.cause, exc.cause), 0) + 1
        )
    done = sum(r["done"] for r in rows)
    directed = sum(r["directed"] for r in rows)
    return _pack(
        "Put-Away Compliance — directive adherence, overrides and exceptions",
        ["date", "done", "directed", "overridden", "exceptions", "compliance_pct"],
        {
            "date": "Date (Dhaka)",
            "done": "Put-Aways",
            "directed": "To the Directed Bin",
            "overridden": "Overridden",
            "exceptions": "Exceptions",
            "compliance_pct": "Compliance %",
        },
        rows,
        [
            "Directive compliance %.1f%% (target 99%%)."
            % (100.0 * directed / done if done else 0.0),
            "Exception causes: %s."
            % (", ".join("%s %d" % (k, v) for k, v in sorted(causes.items())) or "none"),
            _period_note(date_from, date_to),
        ],
        totals={
            "date": "Total",
            "done": done,
            "directed": directed,
            "overridden": sum(r["overridden"] for r in rows),
            "exceptions": sum(r["exceptions"] for r in rows),
        },
        empty="No put-away in the period.",
    )


def crossdock_utilisation(env, date_from=None, date_to=None, **params):
    docks = _mine(env, "fix.wms.crossdock", _period("staged_at", date_from, date_to))
    sources = dict(env["fix.wms.outbound.demand"]._fields["source_type"].selection)
    rows = [
        {
            "crossdock": xd.name,
            "receipt": xd.receipt_line_id.receipt_id.name,
            "demand": xd.demand_id.name or "—",
            "source": sources.get(xd.demand_id.source_type, "—"),
            "part": xd.part_id.part_number,
            "qty": round(xd.qty, 3),
            "staged": str(_local(xd.staged_at))[:16] if xd.staged_at else "—",
            "dispatched": str(_local(xd.dispatched_at))[:16] if xd.dispatched_at else "—",
            "state": _state(xd),
        }
        for xd in docks
    ]
    return _pack(
        "Cross-Dock Utilisation — lines sent straight to waiting demand",
        [
            "crossdock",
            "receipt",
            "demand",
            "source",
            "part",
            "qty",
            "staged",
            "dispatched",
            "state",
        ],
        {
            "crossdock": "Cross-Dock",
            "receipt": "Receipt",
            "demand": "Demand",
            "source": "Demand Type",
            "part": "Part",
            "qty": "Qty",
            "staged": "Staged (Dhaka)",
            "dispatched": "Dispatched (Dhaka)",
            "state": "State",
        },
        rows,
        [_period_note(date_from, date_to)],
        totals={"crossdock": "Total", "qty": round(sum(r["qty"] for r in rows), 3)},
        empty="No cross-dock in the period.",
    )


def device_health(env, date_from=None, date_to=None, **params):
    devices = _mine(env, "fix.wms.device")
    journal = _mine(env, "fix.wms.rf.journal", _period("processed_at", date_from, date_to))
    rows = []
    for device in devices:
        mine = journal.filtered(lambda j, d=device: j.device_id == d)
        rows.append(
            {
                "device": device.device_code,
                "warehouse": device.warehouse_id.name,
                "operative": device.operative_id.name or "NOT ISSUED",
                "state": _state(device),
                "last_seen": str(_local(device.last_seen_at))[:16]
                if device.last_seen_at
                else "never",
                "confirmations": len(mine.filtered("ok")),
                "refused": len(mine.filtered(lambda j: not j.ok)),
                "offline": len(mine.filtered("offline")),
            }
        )
    rows.sort(key=lambda r: (r["state"], r["device"]))
    return _pack(
        "Device and Connectivity Health — RF handhelds",
        [
            "device",
            "warehouse",
            "operative",
            "state",
            "last_seen",
            "confirmations",
            "refused",
            "offline",
        ],
        {
            "device": "Device",
            "warehouse": "Warehouse",
            "operative": "Issued To",
            "state": "State",
            "last_seen": "Last Seen (Dhaka)",
            "confirmations": "Confirmed",
            "refused": "Refused",
            "offline": "Offline Replays",
        },
        rows,
        [
            "A device not issued to a named operative is refused by the RF API (T-15).",
            _period_note(date_from, date_to),
        ],
        empty="No RF device enrolled.",
    )


def slot_ledger_recon(env, date_from=None, date_to=None, **params):
    """AC-01 / BRU-WMS-01: the bins against M15. For every part and class at a
    location a warehouse breaks down, what the bins hold against the
    unrestricted on-hand the ledger holds there. Slotted above on-hand is a
    defect; the rest is stock no bin holds yet."""
    warehouses = env["fix.warehouse"].search(
        [("company_id", "in", env.companies.ids), ("stock_location_id", "!=", False)]
    )
    slots = env["fix.wms.slot"].search([("bin_id.zone_id.warehouse_id", "in", warehouses.ids)])
    Onhand = env["fix.stock.onhand"]
    keys = {}
    for slot in slots:
        wh = slot.bin_id.zone_id.warehouse_id
        key = (wh.id, slot.part_id.id, slot.ownership_class or "owned")
        keys[key] = keys.get(key, 0.0) + (slot.qty or 0.0)
    rows = []
    over = 0
    for (wh_id, part_id, cls), slotted in keys.items():
        wh = env["fix.warehouse"].browse(wh_id)
        part = env["fix.spare.part"].browse(part_id)
        location = wh.stock_location_id
        ledger_cls = "van" if cls == "owned" and location.location_type == "van" else cls
        bucket = Onhand._bucket(part, location, ledger_cls)
        on_hand = bucket.qty if bucket else 0.0
        gap = round(on_hand - slotted, 4)
        if gap < -EPS:
            over += 1
        rows.append(
            {
                "warehouse": wh.name,
                "location": location.code,
                "part": part.part_number,
                "class": cls,
                "on_hand": round(on_hand, 3),
                "slotted": round(slotted, 3),
                "unslotted": gap,
                "status": "SLOTS EXCEED LEDGER" if gap < -EPS else "ok",
            }
        )
    rows.sort(key=lambda r: (r["status"] == "ok", r["warehouse"], r["part"]))
    return _pack(
        "Slot vs Ledger Reconciliation (AC-01)",
        ["warehouse", "location", "part", "class", "on_hand", "slotted", "unslotted", "status"],
        {
            "warehouse": "Warehouse",
            "location": "M15 Location",
            "part": "Part",
            "class": "Class",
            "on_hand": "M15 Unrestricted",
            "slotted": "In Bins",
            "unslotted": "Outside Bins",
            "status": "Status",
        },
        rows,
        [
            "%d part/class line(s) where the bins hold more than M15: each is a defect to "
            "count back. As at now." % over,
            "Stock outside the bins is slotted by put-away or a supervisor's opening slot load.",
        ],
        empty="No slotted stock.",
    )


REPORTS = {
    "throughput_by_shift": throughput_by_shift,
    "pick_accuracy": pick_accuracy,
    "wave_cycle_time": wave_cycle_time,
    "labour_productivity": labour_productivity,
    "bin_utilisation": bin_utilisation,
    "pick_strategy": pick_strategy,
    "rf_queue": rf_queue,
    "scan_violations": scan_violations,
    "override_report": override_report,
    "short_pick_rate": short_pick_rate,
    "cycle_times": cycle_times,
    "putaway_compliance": putaway_compliance,
    "crossdock_utilisation": crossdock_utilisation,
    "device_health": device_health,
    "slot_ledger_recon": slot_ledger_recon,
}


def kpis(env):
    """Read as the caller, in the caller's companies, from executed work only;
    'today' is the Dhaka day (F14)."""
    tasks = _mine(env, "fix.wms.task")
    waves = _mine(env, "fix.wms.wave")
    bins = _bins(env)
    slots = env["fix.wms.slot"].search([("bin_id", "in", bins.ids)])
    lines = _picked_lines(env)
    exact = len(
        lines.filtered(
            lambda ln: abs((ln.picked_qty or 0.0) - _requested(ln)) <= EPS
            and not ln.resourced_from_id
        )
    )
    today = (fields.Datetime.now() + DHAKA).date()
    docks = _mine(env, "fix.wms.dock", _period("slot_start", today, today))
    constrained = bins.filtered(lambda b: (b.capacity_qty or 0.0) > 0)
    capacity = sum(constrained.mapped("capacity_qty"))
    slotted = sum(slots.filtered(lambda s: s.bin_id in constrained).mapped("qty"))
    return {
        "open_tasks": len(tasks.filtered(lambda t: t.state in ("open", "assigned"))),
        "waves_in_progress": len(
            waves.filtered(lambda w: w.state in ("released", "picking", "packed", "staged"))
        ),
        "bins_slotted": len(slots.filtered(lambda s: (s.qty or 0.0) > 0)),
        "pick_accuracy_pct": round((exact / len(lines)) * 100.0, 1) if lines else 0.0,
        "docks_today": len(docks),
        "bin_utilisation_pct": round((slotted / capacity) * 100.0, 1) if capacity else 0.0,
    }
