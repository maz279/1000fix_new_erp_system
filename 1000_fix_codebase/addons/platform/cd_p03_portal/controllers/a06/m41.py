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

SURFACES = {
    "fix.warehouse.bin": {
        "order": "zone_id, name",
        "limit": 400,
        "actions": {"action_block", "action_unblock"},
    },
    "fix.warehouse.zone": {"order": "warehouse_id, name", "limit": 200, "actions": set()},
    "fix.wms.slot": {
        "order": "bin_id, part_id",
        "limit": 400,
        "actions": {"action_block", "action_unblock", "action_raise_replenishment"},
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
    "fix.inventory.valuation.suspense": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.spare.part": {
        "order": "id desc",
        "limit": 400,
        "actions": {
            "action_discontinue",
            "action_mark_obsolete",
            "action_reactivate",
            "action_set_standard_cost",
        },
    },
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


def _mine(env, model, domain=None, **kw):
    """The caller's records of this model in the companies they work in."""
    records = env[model]
    company = [("company_id", "in", env.companies.ids)] if "company_id" in records._fields else []
    return records.search(company + list(domain or []), **kw)


def _tasks(env):
    return _mine(env, "fix.wms.task")


def _executed(tasks):
    """Tasks the system recorded as done by an operative (not typed)."""
    return tasks.filtered(lambda t: t.state == "done" and t.done_at and t.done_by_id)


def _picked_lines(env):
    """Wave lines the wave itself picked (picked_by / picked_at set)."""
    waves = _mine(env, "fix.wms.wave")
    return env["fix.wms.wave.line"].search(
        [("wave_id", "in", waves.ids), ("picked_at", "!=", False)]
    )


def throughput_by_shift(env, date_from=None, date_to=None, **params):
    rows = []
    buckets = {}
    for task in _executed(_tasks(env)):
        hour = task.done_at.hour
        shift = (
            "Morning (06–14)"
            if 6 <= hour < 14
            else ("Afternoon (14–22)" if 14 <= hour < 22 else "Night (22–06)")
        )
        key = (str(task.done_at.date()), shift)
        row = buckets.setdefault(
            key,
            {
                "date": key[0],
                "shift": shift,
                "tasks": 0,
                "qty": 0.0,
            },
        )
        row["tasks"] += 1
        row["qty"] += task.qty or 0.0
    for row in buckets.values():
        row["qty"] = round(row["qty"], 3)
        rows.append(row)
    rows.sort(key=lambda r: (r["date"], r["shift"]), reverse=True)
    return _pack(
        "Throughput by Shift — completed warehouse tasks",
        ["date", "shift", "tasks", "qty"],
        {"date": "Date", "shift": "Shift", "tasks": "Tasks", "qty": "Quantity"},
        rows,
        ["Shift buckets are the task's done hour (06–14, 14–22, 22–06)."],
        totals={
            "date": "Total",
            "tasks": sum(r["tasks"] for r in rows),
            "qty": round(sum(r["qty"] for r in rows), 3),
        },
        empty="No completed warehouse tasks yet.",
    )


def pick_accuracy(env, date_from=None, date_to=None, **params):
    lines = _picked_lines(env)
    rows = []
    for line in lines:
        qty = line.qty or 0.0
        picked = line.picked_qty or 0.0
        rows.append(
            {
                "wave": line.wave_id.name,
                "part": line.part_id.part_number,
                "bin": line.bin_id.name if line.bin_id else "—",
                "qty": round(qty, 3),
                "picked": round(picked, 3),
                "short": round(max(qty - picked, 0.0), 3),
                "accuracy_pct": round((picked / qty) * 100.0, 1) if qty else 0.0,
                "state": dict(line._fields["state"].selection).get(line.state),
            }
        )
    rows.sort(key=lambda r: r["accuracy_pct"])
    total_qty = sum(r["qty"] for r in rows)
    total_picked = sum(r["picked"] for r in rows)
    return _pack(
        "Pick Accuracy Trend — picked quantity against wave quantity",
        ["wave", "part", "bin", "qty", "picked", "short", "accuracy_pct", "state"],
        {
            "wave": "Wave",
            "part": "Part",
            "bin": "Bin",
            "qty": "Wave Qty",
            "picked": "Picked",
            "short": "Short",
            "accuracy_pct": "Accuracy %",
            "state": "State",
        },
        rows,
        [
            "Accuracy = picked ÷ wave quantity over lines the wave actually picked; "
            "overall %.1f%% across %d lines."
            % ((total_picked / total_qty) * 100.0 if total_qty else 0.0, len(lines))
        ],
        totals={
            "wave": "Total",
            "qty": round(total_qty, 3),
            "picked": round(total_picked, 3),
            "short": round(total_qty - total_picked, 3),
        },
        empty="No wave lines yet.",
    )


def wave_cycle_time(env, date_from=None, date_to=None, **params):
    waves = _mine(env, "fix.wms.wave")
    rows = []
    for wave in waves:
        hours = "—"
        if wave.released_at and wave.shipped_at:
            hours = round((wave.shipped_at - wave.released_at).total_seconds() / 3600.0, 2)
        rows.append(
            {
                "wave": wave.name,
                "date": str(wave.wave_date),
                "strategy": dict(wave._fields["strategy"].selection).get(wave.strategy),
                "lines": len(wave.line_ids),
                "released": str(wave.released_at)[:16] if wave.released_at else "—",
                "shipped": str(wave.shipped_at)[:16] if wave.shipped_at else "—",
                "cycle_hours": hours,
                "state": dict(wave._fields["state"].selection).get(wave.state),
            }
        )
    rows.sort(key=lambda r: str(r["wave"]), reverse=True)
    return _pack(
        "Wave Cycle Time — released to shipped",
        ["wave", "date", "strategy", "lines", "released", "shipped", "cycle_hours", "state"],
        {
            "wave": "Wave",
            "date": "Date",
            "strategy": "Strategy",
            "lines": "Lines",
            "released": "Released",
            "shipped": "Shipped",
            "cycle_hours": "Cycle (h)",
            "state": "State",
        },
        rows,
        ["Cycle hours = shipped − released; an open wave shows '—'."],
        empty="No waves yet.",
    )


def labour_productivity(env, date_from=None, date_to=None, **params):
    rows = []
    by_emp = {}
    for task in _executed(_tasks(env)):
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
        ["Completed tasks only; a task without an assignee counts under Unassigned."],
        totals={
            "assignee": "Total",
            "tasks": sum(r["tasks"] for r in rows),
            "qty": round(sum(r["qty"] for r in rows), 3),
        },
        empty="No completed tasks with an operator yet.",
    )


def bin_utilisation(env, date_from=None, date_to=None, **params):
    bins = env["fix.warehouse.bin"].search(
        [("zone_id.warehouse_id.company_id", "in", env.companies.ids)]
    )
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
                "capacity": round(capacity, 3),
                "slotted_qty": round(qty, 3),
                "skus": len(bin_slots),
                "utilisation_pct": round((qty / capacity) * 100.0, 1) if capacity else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["utilisation_pct"])
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
            "Bins with capacity 0 are unconstrained and report 0% — the capacity is "
            "not invented for them."
        ],
        totals={
            "bin": "Total",
            "capacity": round(sum(r["capacity"] for r in rows), 3),
            "slotted_qty": round(sum(r["slotted_qty"] for r in rows), 3),
            "skus": sum(r["skus"] for r in rows),
        },
        empty="No bins yet.",
    )


def pick_strategy(env, date_from=None, date_to=None, **params):
    bins = env["fix.warehouse.bin"].search(
        [("zone_id.warehouse_id.company_id", "in", env.companies.ids)]
    )
    slots = env["fix.wms.slot"].search([("bin_id", "in", bins.ids)])
    tasks = _mine(
        env, "fix.wms.task", [("task_type", "=", "pick"), ("state", "in", ("open", "assigned"))]
    )
    rows = []
    for slot in slots:
        open_picks = tasks.filtered(lambda t, s=slot: t.part_id.id == s.part_id.id)
        rows.append(
            {
                "zone": slot.bin_id.zone_id.name,
                "bin": slot.bin_id.name,
                "part": slot.part_id.part_number,
                "velocity": dict(slot._fields["velocity"].selection).get(slot.velocity),
                "slot_type": dict(slot._fields["slot_type"].selection).get(slot.slot_type),
                "qty": round(slot.qty or 0.0, 3),
                "open_picks": len(open_picks),
            }
        )
    rows.sort(key=lambda r: (r["zone"], r["bin"]))
    return _pack(
        "Pick Strategies — slot layout against open pick work",
        ["zone", "bin", "part", "velocity", "slot_type", "qty", "open_picks"],
        {
            "zone": "Zone",
            "bin": "Bin",
            "part": "Part",
            "velocity": "Velocity",
            "slot_type": "Slot Type",
            "qty": "Bin Qty",
            "open_picks": "Open Picks",
        },
        rows,
        [
            "Strategy view: fast movers should sit in pick-face bins; the open pick "
            "count is live from the task queue."
        ],
        empty="No slots yet.",
    )


def rf_queue(env, date_from=None, date_to=None, **params):
    tasks = _tasks(env).filtered(lambda t: t.state in ("open", "assigned"))
    rows = []
    for task in tasks:
        rows.append(
            {
                "task": task.name,
                "type": dict(task._fields["task_type"].selection).get(task.task_type),
                "ref": task.ref or "—",
                "part": task.part_id.part_number if task.part_id else "—",
                "bin": task.bin_id.name if task.bin_id else "—",
                "qty": round(task.qty or 0.0, 3),
                "assignee": task.assignee_id.name if task.assignee_id else "—",
                "state": dict(task._fields["state"].selection).get(task.state),
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
        ["This is the RF device's work list: open tasks first, then assigned ones."],
        empty="No open warehouse tasks.",
    )


def scan_violations(env, date_from=None, date_to=None, **params):
    """Spec section 14 "Ownership-class segregation": the scans the floor
    REFUSED, by rule and operative (BRU-WMS-03 class, -05 wrong bin or item,
    -11 hazard, -12 blocked bin ...), from the scan log."""
    events = _mine(env, "fix.wms.scan.event", [("accepted", "=", False)])
    buckets = {}
    for ev in events:
        key = (ev.rule or "refused", ev.user_name or "-")
        row = buckets.setdefault(
            key,
            {"rule": key[0], "operative": key[1], "attempts": 0, "last": "", "example": ""},
        )
        row["attempts"] += 1
        stamp = str(ev.occurred_at or "")
        if stamp > row["last"]:
            row["last"], row["example"] = stamp, (ev.message or "")[:120]
    rows = sorted(buckets.values(), key=lambda r: (-r["attempts"], r["rule"], r["operative"]))
    return _pack(
        "Attempted Violations - scans the floor refused",
        ["rule", "operative", "attempts", "last", "example"],
        {
            "rule": "Rule",
            "operative": "Operative",
            "attempts": "Attempts",
            "last": "Last Attempt (UTC)",
            "example": "Last Reason",
        },
        rows,
        [
            "BRU-WMS-03 is the ownership-class segregation the spec's report counts; "
            "BRU-WMS-05 a wrong bin or item scan; BRU-WMS-11 hazard; BRU-WMS-12 a blocked bin.",
            "Refused attempts are logged in their own transaction, so they survive the refusal.",
        ],
        totals={"rule": "Total", "attempts": sum(r["attempts"] for r in rows)},
        empty="No refused scan.",
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
}


def kpis(env):
    """Read as the caller, in the caller's companies, from executed work only."""
    tasks = _tasks(env)
    waves = _mine(env, "fix.wms.wave")
    bins = env["fix.warehouse.bin"].search(
        [("zone_id.warehouse_id.company_id", "in", env.companies.ids)]
    )
    slots = env["fix.wms.slot"].search([("bin_id", "in", bins.ids)])
    lines = _picked_lines(env)
    total_qty = sum(line.qty or 0.0 for line in lines)
    picked = sum(line.picked_qty or 0.0 for line in lines)
    today = datetime.date.today()
    docks = _mine(
        env,
        "fix.wms.dock",
        [("slot_start", ">=", datetime.datetime.combine(today, datetime.time.min))],
    )
    capacity = sum(bins.mapped("capacity_qty"))
    slotted = sum(slots.mapped("qty"))
    return {
        "open_tasks": len(tasks.filtered(lambda t: t.state in ("open", "assigned"))),
        "waves_in_progress": len(
            waves.filtered(lambda w: w.state in ("released", "picking", "packed", "staged"))
        ),
        "bins_slotted": len(slots.filtered(lambda s: (s.qty or 0.0) > 0)),
        "pick_accuracy_pct": round((picked / total_qty) * 100.0, 1) if total_qty else 0.0,
        "docks_today": len(docks),
        "bin_utilisation_pct": round((slotted / capacity) * 100.0, 1) if capacity else 0.0,
    }
