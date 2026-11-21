# A07 · M45 Enterprise Assets & Test Equipment — surfaces, packs and KPIs over
# the equipment register/calibration plus kits, issue/return, transfers,
# verification, out-of-service, PM and usage.
import datetime

from odoo import fields

SURFACES = {
    # A07 P0 recipe (2026-11-03): the write-off is requested here and decided
    # from the approver's M63 inbox (routed); the approve method is not offered.
    "fix.equipment": {
        "order": "code",
        "limit": 400,
        "actions": {
            "action_assert_usable",
            "action_request_approval",
            "action_recall_approval",
            # capture audit 2026-11-16: FR-EAM-029
            "action_recall_calibration",
        },
    },
    # A07 P2 (2026-11-04): the usage decision is taken by a Quality Manager
    # other than the recorder (SOD-07)
    "fix.calibration": {
        "order": "calibrated_on desc, id desc",
        "limit": 400,
        "actions": {"action_accept_calibration", "action_reject_calibration"},
        # BRU-EAM-04: only a registered calibration standard is offered
        "pickers": {"standard_equipment_id": [("classification", "=", "calibration_standard")]},
    },
    # the readings grid on the calibration form: no screen of its own and nothing
    # written here; the picker skips profiles that read no measurement points
    "fix.calibration.reading": {
        "order": "calibration_id, id",
        "limit": 300,
        "actions": set(),
        "pickers": {"point_id": [("profile_id.verification_only", "=", False)]},
    },
    # A07 P1 (2026-11-04) FR-EAM-007: a kit is issued and returned as one unit
    "fix.equipment.kit": {
        "order": "code",
        "limit": 200,
        "actions": {"action_issue_kit", "action_return_kit"},
    },
    # A07 P2 (2026-11-04): calibration profiles; an interval change is
    # requested here and approved from a Quality Manager's M63 inbox (routed)
    "fix.calibration.profile": {
        "order": "equipment_id",
        "limit": 400,
        "actions": {"action_request_approval", "action_recall_approval"},
    },
    # A07 P2 (2026-11-04) BRU-EAM-03: the retrospective impact assessments
    "fix.calibration.impact": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_close_impact"},
    },
    "fix.equipment.issue": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        # A07 ERP audit M45-01: the return date moves only through Extend Due
        "actions": {"action_return", "action_extend_due"},
    },
    "fix.equipment.transfer": {
        "order": "transfer_date desc, id desc",
        "limit": 300,
        "actions": {"action_dispatch", "action_receive", "action_cancel"},
    },
    "fix.equipment.verification": {
        "order": "verified_on desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.equipment.oos": {
        "order": "started_on desc, id desc",
        "limit": 300,
        "actions": {"action_resolve"},
    },
    "fix.equipment.pm": {
        "order": "scheduled_on desc, id desc",
        "limit": 300,
        "actions": {"action_done"},
    },
    "fix.equipment.usage": {"order": "used_on desc, id desc", "limit": 400, "actions": set()},
    # capture audit 2026-11-16: the spec records the pages could not capture
    # A07 ERP audit M45-04: switching calibration control off is routed (M63)
    "fix.equipment.category": {
        "order": "classification, code",
        "limit": 200,
        "actions": {"action_request_approval", "action_recall_approval"},
    },
    "fix.branch.equipment.profile": {
        "order": "branch_id, category_id",
        "limit": 400,
        "actions": set(),
    },
    "fix.equipment.pm.plan": {
        "order": "name desc",
        "limit": 300,
        "actions": {"action_raise_due_jobs"},
    },
    "fix.equipment.loss": {
        "order": "occurred_on desc, id desc",
        "limit": 300,
        # D9: HR decides the staff recharge
        "actions": {
            "action_recover",
            "action_send_to_repair",
            "action_request_writeoff",
            "action_hr_approve_recharge",
            "action_hr_reject_recharge",
        },
    },
    "fix.equipment.audit": {
        "order": "scheduled_for desc, id desc",
        "limit": 300,
        # M45-16: a count with items not found waits for a reviewer
        "actions": {"action_start", "action_complete", "action_approve_count"},
    },
    # the found-items grid of a count: no screen of its own
    "fix.equipment.audit.line": {"order": "audit_id, id", "limit": 500, "actions": set()},
    "fix.equipment.retirement": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_request", "action_dispose"},
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
    """A07 ERP audit M45-17: the Dhaka business day (not the server date)."""
    return fields.Date.context_today(env["fix.equipment"].with_context(tz="Asia/Dhaka"))


def _day(value):
    """A report period bound ("YYYY-MM-DD"), or None when not given."""
    try:
        return fields.Date.to_date(value) if value and value != "…" else None
    except (TypeError, ValueError):
        return None


def _period(field, date_from=None, date_to=None):
    """The domain of a report period on `field` (both bounds inclusive)."""
    domain = []
    start, end = _day(date_from), _day(date_to)
    if start:
        domain.append((field, ">=", start))
    if end:
        domain.append((field, "<=", end))
    return domain


def _ou_fence(env, Model):
    """The caller's operating units (the OU record rule, re-applied under sudo).
    An OU manager sees every unit; a superuser is not fenced."""
    if env.su:
        return []
    if "operating_unit_id" in Model._fields:
        path = "operating_unit_id"
    elif "equipment_id" in Model._fields:
        path = "equipment_id.operating_unit_id"
    else:
        return []
    units = env.user.operating_units() if hasattr(env.user, "operating_units") else None
    if units is None:
        return []
    return ["|", (path, "=", False), (path, "in", units.ids)]


def _scoped(env, model, domain=None):
    """sudo() read for a report or KPI, fenced to the caller's companies.

    A07 audit (2026-11-03) M45-10: every pack read `sudo().search([])`, so the
    calibration schedule of one company listed another company's instruments.
    A07 ERP audit (2026-11-20) M45-17: the fence is the ACTIVE companies
    (env.companies, the company switcher), not every company the user may
    open, and the caller's operating units, as the record rules would be."""
    Model = env[model].sudo()
    ids = env.companies.ids
    if "company_id" in Model._fields:
        fence = ["|", ("company_id", "=", False), ("company_id", "in", ids)]
    else:
        fence = [
            "|",
            ("equipment_id.company_id", "=", False),
            ("equipment_id.company_id", "in", ids),
        ]
    return Model.search(list(domain or []) + fence + _ou_fence(env, Model))


def _equipment(env):
    return _scoped(env, "fix.equipment")


def _calibration_label(equipment):
    return dict(equipment._fields["calibration_state"].selection).get(
        equipment.calibration_state, equipment.calibration_state
    )


def classification(env, date_from=None, date_to=None, **params):
    buckets = {}
    for equipment in _equipment(env):
        key = (
            equipment.category_id.name or equipment.category or "Unclassified",
            equipment.custodian_id.name if equipment.custodian_id else "No custodian",
        )
        row = buckets.setdefault(
            key,
            {
                "category": key[0],
                "custodian": key[1],
                "items": 0,
                "calibrated": 0,
                "overdue": 0,
            },
        )
        row["items"] += 1
        if equipment.last_calibration:
            row["calibrated"] += 1
        if equipment.calibration_overdue:
            row["overdue"] += 1
    rows = sorted(buckets.values(), key=lambda r: -r["items"])
    return _pack(
        "Classification — equipment by category and custodian",
        ["category", "custodian", "items", "calibrated", "overdue"],
        {
            "category": "Category",
            "custodian": "Custodian",
            "items": "Items",
            "calibrated": "Calibrated",
            "overdue": "Overdue",
        },
        rows,
        [
            "Calibrated = has at least one calibration record; overdue = the computed "
            "flag on the equipment."
        ],
        totals={
            "category": "Total",
            "items": sum(r["items"] for r in rows),
            "calibrated": sum(r["calibrated"] for r in rows),
            "overdue": sum(r["overdue"] for r in rows),
        },
        empty="No equipment registered yet.",
    )


def calibration_schedule(env, date_from=None, date_to=None, **params):
    today = _today(env)
    start, end = _day(date_from), _day(date_to)
    rows = []
    for equipment in _equipment(env).filtered(lambda e: e.operational_status != "retired"):
        due = equipment.next_calibration
        # the period selects the instruments falling due in it
        if (start or end) and (not due or (start and due < start) or (end and due > end)):
            continue
        days = (due - today).days if due else None
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "category": equipment.category_id.name or equipment.category or "—",
                "last_calibration": str(equipment.last_calibration)
                if equipment.last_calibration
                else "—",
                "next_calibration": str(equipment.next_calibration)
                if equipment.next_calibration
                else "—",
                "days_left": days if days is not None else "—",
                "overdue": equipment.calibration_overdue,
                "calibration": _calibration_label(equipment),
                "status": equipment.operational_status,
            }
        )
    rows.sort(key=lambda r: (r["next_calibration"] == "—", r["next_calibration"]))
    return _pack(
        "Calibration Schedule — next due per equipment",
        [
            "code",
            "name",
            "category",
            "last_calibration",
            "next_calibration",
            "days_left",
            "overdue",
            "calibration",
            "status",
        ],
        {
            "code": "Code",
            "name": "Equipment",
            "category": "Category",
            "last_calibration": "Last",
            "next_calibration": "Next Due",
            "days_left": "Days Left",
            "overdue": "Overdue",
            "calibration": "Calibration",
            "status": "Status",
        },
        rows,
        [
            "Days-left is negative when overdue; an equipment without a calibration "
            "shows '—' rather than a fabricated date.",
            "Last and Calibration come from the latest calibration only: a failed latest "
            "calibration has no next-due, because it certifies nothing.",
        ],
        empty="No equipment registered yet.",
    )


# a pass, or an adjustment that left every point in tolerance (A07 P2)
CERTIFYING = ("pass", "adjusted")


def _cal_key(calibration):
    return (calibration.calibrated_on, calibration.id)


def retrospective_impact(env, date_from=None, date_to=None, **params):
    """BRU-EAM-03 / ISO 9001 7.1.5.2: every measurement made since the
    instrument was last known good is suspect.

    A07 audit (2026-11-03) M45-3: the window started AT the failure, so the uses
    between the last pass and the fail (the drifting instrument's measurements)
    were missed: 1 of 3 suspect QC passes was reported. The window now runs
    from the last passing calibration before the latest fail up to the first
    pass after it (or stays open while the instrument has not passed again)."""
    usages = _scoped(env, "fix.equipment.usage", _period("used_on", date_from, date_to))
    # a superseded calibration was corrected by a later record: not evidence
    calibrations = _scoped(env, "fix.calibration", [("superseded_by_id", "=", False)])
    rows = []
    for equipment in _equipment(env):
        cals = calibrations.filtered(lambda c, eid=equipment.id: c.equipment_id.id == eid)
        cals = cals.sorted(_cal_key)
        failed = cals.filtered(lambda c: c.result == "fail")
        if not failed and not equipment.calibration_overdue:
            continue
        uses = usages.filtered(lambda u, eid=equipment.id: u.equipment_id.id == eid)
        last_fail = None
        if failed:
            fail = failed[-1]
            last_fail = fail.calibrated_on
            key = _cal_key(fail)
            before = cals.filtered(lambda c, k=key: c.result in CERTIFYING and _cal_key(c) < k)
            after = cals.filtered(lambda c, k=key: c.result in CERTIFYING and _cal_key(c) > k)
            since = before[-1].calibrated_on if before else None
            until = after[0].calibrated_on if after else None
            affected = uses.filtered(
                lambda u, a=since, b=until: (
                    (a is None or u.used_on >= a) and (b is None or u.used_on < b)
                )
            )
            window = "%s to %s" % (since or "first use", until or "open")
        else:
            # overdue, never failed: the uses made after the certificate lapsed
            lapsed = equipment.next_calibration
            affected = uses.filtered(lambda u, d=lapsed: u.used_on > d)
            window = "after %s (lapsed)" % lapsed
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "next_calibration": str(equipment.next_calibration)
                if equipment.next_calibration
                else "—",
                "overdue": equipment.calibration_overdue,
                "failed_calibrations": len(failed),
                "last_failure": str(last_fail) if last_fail else "—",
                "window": window,
                "affected_uses": len(affected),
            }
        )
    rows.sort(key=lambda r: -r["affected_uses"])
    return _pack(
        "Retrospective Impact — uses since the last good calibration",
        [
            "code",
            "name",
            "next_calibration",
            "overdue",
            "failed_calibrations",
            "last_failure",
            "window",
            "affected_uses",
        ],
        {
            "code": "Code",
            "name": "Equipment",
            "next_calibration": "Next Due",
            "overdue": "Overdue",
            "failed_calibrations": "Failed Cals",
            "last_failure": "Last Failure",
            "window": "Suspect Window",
            "affected_uses": "Suspect Uses",
        },
        rows,
        [
            "For a failed calibration the suspect window runs from the last PASSING "
            "calibration before the latest failure (the last time the instrument was "
            "known good) to the first pass after it, or stays open until it passes again.",
            "Overdue equipment with no failure lists the uses made after its certificate "
            "lapsed. Only recorded usage rows are counted.",
        ],
        empty="No equipment is overdue or has a failed calibration.",
    )


def _compliance(equipment):
    """(current, controlled) over the measurement-critical items in use: the
    Wave-5 gate metric (BRU-EAM-21, AC-17)."""
    controlled = equipment.filtered(
        lambda e: e.operational_status != "retired" and e.measurement_critical
    )
    current = controlled.filtered(lambda e: e.calibration_state == "current")
    return len(current), len(controlled)


def calibration_compliance(env, date_from=None, date_to=None, **params):
    today = _today(env)
    horizon = today + datetime.timedelta(days=30)
    rows = []
    register = _equipment(env).filtered(lambda e: e.operational_status != "retired")
    current, controlled = _compliance(register)
    for equipment in register:
        # A07 audit (2026-11-03) M45-1: a failed instrument showed as "current"
        # because only passing rows were read; the latest calibration decides
        state = equipment.calibration_state
        if state == "overdue":
            status = "overdue"
        elif state == "failed":
            status = "failed"
        elif state == "never":
            status = "never calibrated"
        elif state == "rejected":
            # a rejected calibration certifies nothing, so it has no next-due
            status = "rejected at usage decision"
        elif state == "pending":
            status = "awaiting usage decision"
        elif state == "not_required":
            # capture audit 2026-11-16: outside calibration control (FR-EAM-003)
            status = "not measurement-critical"
        elif equipment.next_calibration <= horizon:
            status = "due within 30 days"
        else:
            status = "current"
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "category": equipment.category_id.name or equipment.category or "—",
                "next_calibration": str(equipment.next_calibration)
                if equipment.next_calibration
                else "—",
                "status": status,
                "operational": equipment.operational_status,
            }
        )
    rows.sort(key=lambda r: r["status"])
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return _pack(
        "Calibration Compliance Report",
        ["code", "name", "category", "next_calibration", "status", "operational"],
        {
            "code": "Code",
            "name": "Equipment",
            "category": "Category",
            "next_calibration": "Next Due",
            "status": "Calibration Status",
            "operational": "Operational",
        },
        rows,
        [
            "Calibration compliance %s: current over measurement-critical items in use "
            "(%d of %d; target 100%%, BRU-EAM-21)."
            % (
                "%.1f%%" % (100.0 * current / controlled) if controlled else "not measurable",
                current,
                controlled,
            ),
            "Status counts: " + ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items())),
            "From the latest calibration only: failed, overdue, rejected, awaiting a usage "
            "decision and never calibrated are not current, and the fitness gate refuses them.",
        ],
        empty="No equipment registered yet.",
    )


def utilisation(env, date_from=None, date_to=None, **params):
    today = _today(env)
    end = _day(date_to) or today
    start = _day(date_from) or end - datetime.timedelta(days=29)
    period_days = max((end - start).days + 1, 1)
    usages = _scoped(env, "fix.equipment.usage", _period("used_on", start, end))
    rows = []
    for equipment in _equipment(env).filtered(lambda e: e.operational_status != "retired"):
        uses = usages.filtered(lambda u, eid=equipment.id: u.equipment_id.id == eid)
        days_used = len(set(uses.mapped("used_on")))
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "uses": len(uses),
                "total_uses": sum(uses.mapped("uses")),
                "qc_uses": len(uses.filtered(lambda u: u.qc_result != "na")),
                "days_used": days_used,
                "utilisation_pct": round(100.0 * days_used / period_days, 1),
                "last_used": str(max(uses.mapped("used_on"))) if uses else "—",
                "status": equipment.operational_status,
            }
        )
    rows.sort(key=lambda r: -r["total_uses"])
    return _pack(
        "Equipment Utilisation — recorded uses per item, %s to %s" % (start, end),
        [
            "code",
            "name",
            "uses",
            "total_uses",
            "qc_uses",
            "days_used",
            "utilisation_pct",
            "last_used",
            "status",
        ],
        {
            "code": "Code",
            "name": "Equipment",
            "uses": "Usage Rows",
            "total_uses": "Total Uses",
            "qc_uses": "QC Uses",
            "days_used": "Days Used",
            "utilisation_pct": "Utilisation %",
            "last_used": "Last Used",
            "status": "Status",
        },
        rows,
        [
            "Utilisation %% = days with at least one recorded use over the %d days of the "
            "period (default: the last 30 days)." % period_days,
            "Counts recorded usage rows only; an item with no usage rows shows 0 — "
            "absence of data is not evidence of no use.",
        ],
        totals={
            "code": "Total",
            "uses": sum(r["uses"] for r in rows),
            "total_uses": sum(r["total_uses"] for r in rows),
        },
        empty="No equipment registered yet.",
    )


def loss_writeoff(env, date_from=None, date_to=None, **params):
    """Every recorded loss: an item missing at a count, and (capture audit
    2026-11-16) every loss, theft or damage report with its accountability."""
    verifications = _scoped(
        env,
        "fix.equipment.verification",
        [("state", "=", "missing"), *_period("verified_on", date_from, date_to)],
    )
    losses = _scoped(env, "fix.equipment.loss", _period("occurred_on", date_from, date_to))
    status = dict(env["fix.equipment"]._fields["operational_status"].selection)
    reported = losses.filtered(lambda r: r.kind in ("lost", "stolen")).equipment_id
    rows = []
    for record in verifications:
        equipment = record.equipment_id
        # A07 ERP audit M45-17: a count's "missing" is listed while it is the
        # item's open loss (not once a later count recovered it), and once:
        # an item with its own loss report is listed by that report
        if equipment.missing_verification_id != record or equipment in reported:
            continue
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "source": "Count %s" % record.campaign_ref,
                "on": str(record.verified_on),
                "custodian": record.verifier_id.name if record.verifier_id else "—",
                "value": equipment._m45_writeoff_basis()[0],
                "decision": "missing at count",
                "status": status.get(equipment.operational_status),
            }
        )
    states = dict(env["fix.equipment.loss"]._fields["state"].selection)
    kinds = dict(env["fix.equipment.loss"]._fields["kind"].selection)
    for loss in losses:
        rows.append(
            {
                "code": loss.equipment_id.code,
                "name": loss.equipment_id.name,
                "source": "%s %s" % (kinds.get(loss.kind), loss.name),
                "on": str(loss.occurred_on),
                "custodian": loss.custodian_at_loss_id.name or "—",
                "value": loss.value_impact or 0.0,
                "decision": states.get(loss.state),
                "status": status.get(loss.equipment_id.operational_status),
            }
        )
    rows.sort(key=lambda r: r["on"], reverse=True)
    return _pack(
        "Tool Loss & Write-Off — missing at counts and reported losses",
        ["code", "name", "source", "on", "custodian", "value", "decision", "status"],
        {
            "code": "Code",
            "name": "Equipment",
            "source": "Recorded By",
            "on": "Date",
            "custodian": "Custodian / Verifier",
            "value": "Value (BDT)",
            "decision": "Decision",
            "status": "Operational",
        },
        rows,
        [
            "A count that does not find an item, and a lost or stolen report, make the item "
            "Lost / Missing until it is recovered or written off. A write-off is approved "
            "within the authority matrix and never by the person who reported the loss "
            "(BRU-EAM-12); Operational shows Retired once it is approved.",
            "A damaged item is out of service and goes to repair or write-off; it never "
            "returns straight to available (BRU-EAM-10).",
        ],
        totals={"code": "Total", "value": round(sum(r["value"] for r in rows), 2)},
        empty="No equipment was missing at a count and no loss was reported.",
    )


def register_completeness(env, date_from=None, date_to=None, **params):
    """FR-EAM-009/037, BRU-EAM-20: what each branch holds against its profile."""
    rows = []
    for line in _scoped(env, "fix.branch.equipment.profile", [("active", "=", True)]):
        rows.append(
            {
                "branch": line.branch_id.name,
                "category": line.category_id.name,
                "minimum": line.minimum_quantity,
                "held": line.held_count,
                "fit": line.fit_count,
                "shortfall": line.shortfall,
                "exception": line.capability_exception,
            }
        )
    rows.sort(key=lambda r: (not r["exception"], -r["shortfall"], r["branch"] or ""))
    required = sum(r["minimum"] for r in rows)
    met = sum(min(r["held"], r["minimum"]) for r in rows)
    return _pack(
        "Register Completeness — branch holdings against the profile",
        ["branch", "category", "minimum", "held", "fit", "shortfall", "exception"],
        {
            "branch": "Branch",
            "category": "Equipment Class",
            "minimum": "Minimum",
            "held": "Held",
            "fit": "Fit & Available",
            "shortfall": "Shortfall",
            "exception": "Capability Exception",
        },
        rows,
        [
            "Completeness %s: held (capped at the minimum) over the minimum the profiles ask "
            "for." % ("%.0f%%" % (100.0 * met / required) if required else "not measurable"),
            "A capability exception is a critical class with no fit, available item at the "
            "branch (BRU-EAM-20). Lost, missing and retired items are not held.",
        ],
        totals={"branch": "Total", "minimum": required, "held": sum(r["held"] for r in rows)},
        empty="No branch equipment profile is defined yet: the Quality Manager sets one per "
        "branch and class.",
    )


def cost_of_ownership(env, date_from=None, date_to=None, **params):
    pms = _scoped(env, "fix.equipment.pm", _period("scheduled_on", date_from, date_to))
    calibrations = _scoped(env, "fix.calibration", _period("calibrated_on", date_from, date_to))
    rows = []
    for equipment in _equipment(env):
        equipment_pm = pms.filtered(lambda p, eid=equipment.id: p.equipment_id.id == eid)
        cals = calibrations.filtered(lambda c, eid=equipment.id: c.equipment_id.id == eid)
        pm_cost = round(sum(equipment_pm.mapped("cost")), 2)
        cal_cost = round(sum(cals.mapped("calibration_cost")), 2)
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "pm_jobs": len(equipment_pm),
                "pm_cost": pm_cost,
                "downtime": round(sum(equipment_pm.mapped("downtime_hours")), 1),
                "calibrations": len(cals),
                "calibration_cost": cal_cost,
                "running_cost": round(pm_cost + cal_cost, 2),
                "status": equipment.operational_status,
            }
        )
    rows.sort(key=lambda r: -r["running_cost"])
    return _pack(
        "Cost of Ownership — recorded PM and calibration cost",
        [
            "code",
            "name",
            "pm_jobs",
            "pm_cost",
            "downtime",
            "calibrations",
            "calibration_cost",
            "running_cost",
            "status",
        ],
        {
            "code": "Code",
            "name": "Equipment",
            "pm_jobs": "PM Jobs",
            "pm_cost": "PM Cost",
            "downtime": "Downtime (h)",
            "calibrations": "Calibrations",
            "calibration_cost": "Calibration Cost",
            "running_cost": "PM + Calibration",
            "status": "Status",
        },
        rows,
        [
            "Recorded PM cost and the provider cost recorded on each calibration "
            "(M45-19; it reaches AP as an M52 cost entry). The acquisition cost is the "
            "write-off basis and depreciation is M49's, so total cost of ownership is "
            "not claimed."
        ],
        totals={
            "code": "Total",
            "pm_jobs": sum(r["pm_jobs"] for r in rows),
            "pm_cost": round(sum(r["pm_cost"] for r in rows), 2),
            "calibrations": sum(r["calibrations"] for r in rows),
            "calibration_cost": round(sum(r["calibration_cost"] for r in rows), 2),
            "running_cost": round(sum(r["running_cost"] for r in rows), 2),
        },
        empty="No equipment registered yet.",
    )


# ---- A07 ERP audit (2026-11-20) M45-18 / D18: the printable documents --------
# Each is a report pack, so the standard CSV / Excel / PDF / Email bar prints it.
def certificate_register(env, date_from=None, date_to=None, **params):
    """FR-EAM-024 / AC-08 / §14: every calibration certificate, with its hash."""
    cals = _scoped(env, "fix.calibration", _period("calibrated_on", date_from, date_to))
    results = dict(env["fix.calibration"]._fields["result"].selection)
    decisions = dict(env["fix.calibration"]._fields["decision_state"].selection)
    rows = [
        {
            "code": c.equipment_id.code,
            "name": c.equipment_id.name,
            "calibrated_on": str(c.calibrated_on),
            "result": results.get(c.result),
            "certificate": c.certificate_ref or "—",
            "provider": c.provider_id.name or c.performed_by or "—",
            "accredited": "yes (%s)" % (c.accreditation_ref or "-")
            if c.provider_accredited
            else ("NO" if c.non_accredited else "—"),
            "standard": c.standard_equipment_id.code or c.standard_ref or "—",
            "next_due": str(c.next_due),
            "decision": decisions.get(c.decision_state),
            "sha256": (c.certificate_hash or "—")[:16],
            "superseded": bool(c.superseded_by_id),
        }
        for c in cals.sorted(lambda c: (c.equipment_id.code or "", c.calibrated_on, c.id))
    ]
    return _pack(
        "Calibration Certificate Register",
        [
            "code",
            "name",
            "calibrated_on",
            "result",
            "certificate",
            "provider",
            "accredited",
            "standard",
            "next_due",
            "decision",
            "sha256",
            "superseded",
        ],
        {
            "code": "Code",
            "name": "Instrument",
            "calibrated_on": "Calibrated",
            "result": "Result",
            "certificate": "Certificate",
            "provider": "Provider",
            "accredited": "Accredited",
            "standard": "Reference Standard",
            "next_due": "Next Due",
            "decision": "Usage Decision",
            "sha256": "SHA-256 (first 16)",
            "superseded": "Superseded",
        },
        rows,
        [
            "The certificate file is kept on the calibration record; its SHA-256 was taken "
            "when it was recorded, so a replaced file would not match (AC-08).",
            "Non-accredited (NO): certified by an external provider without accreditation; "
            "the instrument cannot produce a QC result on it (BRU-EAM-05).",
        ],
        empty="No calibration recorded in the period.",
    )


def asset_tags(env, date_from=None, date_to=None, **params):
    """FR-EAM-004: the durable tag of each item, to print as labels. The QR /
    barcode carries the asset tag, which finds the item from any count."""
    rows = [
        {
            "asset_tag": e.asset_tag or "—",
            "qr": "FIX-EQ:%s" % (e.asset_tag or e.code),
            "code": e.code,
            "name": e.name,
            "serial": e.serial_no or "—",
            "category": e.category_id.name or e.category or "—",
            "branch": e.branch_id.name or "—",
            "calibration": "Calibration controlled" if e.measurement_critical else "—",
        }
        for e in _equipment(env).filtered(lambda e: e.operational_status != "retired")
    ]
    return _pack(
        "Asset Tag Labels",
        ["asset_tag", "qr", "code", "name", "serial", "category", "branch", "calibration"],
        {
            "asset_tag": "Asset Tag",
            "qr": "QR / Barcode",
            "code": "Code",
            "name": "Item",
            "serial": "Serial",
            "category": "Class",
            "branch": "Branch",
            "calibration": "Control",
        },
        rows,
        ["One label per item in use. The tag is permanent once registered."],
        empty="No equipment registered yet.",
    )


def custody_slips(env, date_from=None, date_to=None, **params):
    """BRU-EAM-08: the hand-over slip of each issue, signed by both parties."""
    issues = _scoped(env, "fix.equipment.issue", _period("issued_on", date_from, date_to))
    rows = [
        {
            "issue": i.name,
            "code": i.equipment_id.code,
            "name": i.equipment_id.name,
            "asset_tag": i.equipment_id.asset_tag or "—",
            "holder": i.custodian_id.name,
            "issued_on": str(i.issued_on),
            "due_on": str(i.due_on) if i.due_on else "—",
            "issued_by": i.create_uid.name,
            "condition_out": i.condition_out or "—",
            "returned_on": str(i.returned_on) if i.returned_on else "—",
            "holder_signature": "",
            "store_keeper_signature": "",
        }
        for i in issues.sorted(lambda i: (i.issued_on, i.id), reverse=True)
    ]
    return _pack(
        "Custody Hand-Over Slips",
        [
            "issue",
            "code",
            "name",
            "asset_tag",
            "holder",
            "issued_on",
            "due_on",
            "issued_by",
            "condition_out",
            "returned_on",
            "holder_signature",
            "store_keeper_signature",
        ],
        {
            "issue": "Issue",
            "code": "Code",
            "name": "Item",
            "asset_tag": "Tag",
            "holder": "Received By",
            "issued_on": "Issued",
            "due_on": "Return Due",
            "issued_by": "Issued By",
            "condition_out": "Condition Out",
            "returned_on": "Returned",
            "holder_signature": "Holder Signature",
            "store_keeper_signature": "Store Keeper Signature",
        },
        rows,
        [
            "Print the period's slips for signature: the holder accepts custody, the store "
            "keeper hands it over (BRU-EAM-08). A due date moved by Extend Due shows the "
            "current date; the first one is kept on the issue."
        ],
        empty="No equipment was issued in the period.",
    )


def writeoff_memos(env, date_from=None, date_to=None, **params):
    """BRU-EAM-11/16: the write-off and disposal memo of each retired item."""
    retired = _equipment(env).filtered(lambda e: e.operational_status == "retired")
    start, end = _day(date_from), _day(date_to)
    if start or end:
        retired = retired.filtered(
            lambda e: e.retired_on
            and (not start or e.retired_on >= start)
            and (not end or e.retired_on <= end)
        )
    retirements = _scoped(env, "fix.equipment.retirement", [("equipment_id", "in", retired.ids)])
    routes = dict(env["fix.equipment.retirement"]._fields["disposal_route"].selection)
    rows = []
    for equipment in retired.sorted(lambda e: (e.retired_on or datetime.date.min, e.id)):
        retirement = retirements.filtered(lambda r, e=equipment: r.equipment_id == e)[:1]
        amount, basis = equipment._m45_writeoff_basis()
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "retired_on": str(equipment.retired_on or "—"),
                "approved_by": equipment.retired_by_id.name or "—",
                "reason": (equipment.retirement_reason or "—")[:120],
                "basis": "%.2f (%s)" % (amount, basis),
                "route": routes.get(retirement.disposal_route) or "—",
                "disposal_ref": retirement.disposal_ref or "—",
                "sale_amount": retirement.sale_amount or 0.0,
                "buyer": retirement.buyer_partner_id.name or "—",
                "erasure": retirement.erasure_certificate_ref or "—",
                "disposed_on": str(retirement.disposed_on) if retirement.disposed_on else "—",
            }
        )
    return _pack(
        "Write-Off & Disposal Memos",
        [
            "code",
            "name",
            "retired_on",
            "approved_by",
            "reason",
            "basis",
            "route",
            "disposal_ref",
            "sale_amount",
            "buyer",
            "erasure",
            "disposed_on",
        ],
        {
            "code": "Code",
            "name": "Item",
            "retired_on": "Written Off",
            "approved_by": "Approved By",
            "reason": "Reason",
            "basis": "Amount Decided On",
            "route": "Disposal Route",
            "disposal_ref": "Batch / Sale Ref",
            "sale_amount": "Sale Proceeds",
            "buyer": "Buyer",
            "erasure": "M06 Erasure Certificate",
            "disposed_on": "Disposed",
        },
        rows,
        [
            "The write-off is decided on the M49 net book value when the item is "
            "capitalised, otherwise on its acquisition cost (decision D10)."
        ],
        totals={"code": "Total", "sale_amount": round(sum(r["sale_amount"] for r in rows), 2)},
        empty="No equipment was written off in the period.",
    )


REPORTS = {
    "classification": classification,
    "calibration_schedule": calibration_schedule,
    "retrospective_impact": retrospective_impact,
    "calibration_compliance": calibration_compliance,
    "utilisation": utilisation,
    "loss_writeoff": loss_writeoff,
    "register_completeness": register_completeness,
    "cost_of_ownership": cost_of_ownership,
    "certificate_register": certificate_register,
    "asset_tags": asset_tags,
    "custody_slips": custody_slips,
    "writeoff_memos": writeoff_memos,
}


def _availability_mttr_mtbf(env, in_use, today):
    """Over the last 365 days: availability = 1 - out-of-service days over item
    days; MTTR = mean downtime of completed corrective jobs; MTBF = item days
    per corrective job (FR-EAM-036)."""
    start = today - datetime.timedelta(days=364)
    item_days = len(in_use) * 365
    holds = _scoped(
        env,
        "fix.equipment.oos",
        [
            ("equipment_id", "in", in_use.ids),
            ("started_on", "<=", today),
            "|",
            ("state", "=", "open"),
            ("resolved_on", ">=", start),
        ],
    )
    down = 0
    for hold in holds:
        begin = max(hold.started_on, start)
        finish = hold.resolved_on or today
        down += max((finish - begin).days, 0)
    corrective = _scoped(
        env,
        "fix.equipment.pm",
        [
            ("equipment_id", "in", in_use.ids),
            ("pm_type", "=", "corrective"),
            ("scheduled_on", ">=", start),
        ],
    )
    done = corrective.filtered(lambda j: j.state == "done")
    availability = round(100.0 * (1 - down / item_days), 1) if item_days else None
    mttr = round(sum(done.mapped("downtime_hours")) / len(done), 1) if done else None
    mtbf = round(item_days / len(corrective), 1) if corrective else None
    return availability, mttr, mtbf


def kpis(env):
    equipment = _equipment(env)
    in_use = equipment.filtered(lambda e: e.operational_status != "retired")
    today = _today(env)
    current, controlled = _compliance(in_use)
    open_issues = _scoped(env, "fix.equipment.issue", [("state", "=", "issued")])
    overdue_issues = _scoped(env, "fix.equipment.issue", [("is_overdue", "=", True)])
    availability, mttr, mtbf = _availability_mttr_mtbf(env, in_use, today)
    return {
        "equipment_total": len(equipment),
        # A07 ERP audit M45-17: a retired item is not "overdue"
        "calibration_overdue": len(in_use.filtered(lambda e: e.calibration_overdue)),
        # the Wave-5 gate metric (BRU-EAM-21, AC-17)
        "calibration_compliance_pct": round(100.0 * current / controlled, 1)
        if controlled
        else None,
        "availability_pct": availability,
        "mttr_hours": mttr,
        "mtbf_days": mtbf,
        "custody_overdue_pct": round(100.0 * len(overdue_issues) / len(open_issues), 1)
        if open_issues
        else None,
        # A07 audit (2026-11-03) M45-1: failed and never-calibrated instruments
        # are not current either (retired items are no longer in use)
        "calibration_not_current": len(
            in_use.filtered(lambda e: e.calibration_state not in ("current", "not_required"))
        ),
        # a retired item is out of use for good, not waiting to return to service
        "oos_open": len(
            _scoped(
                env,
                "fix.equipment.oos",
                [("state", "=", "open"), ("equipment_id.operational_status", "!=", "retired")],
            )
        ),
        "issued_out": len(open_issues),
        "kits": len(_scoped(env, "fix.equipment.kit", [("active", "=", True)])),
        "pm_open": len(_scoped(env, "fix.equipment.pm", [("state", "=", "open")])),
        # A07 P1/P2 (2026-11-04)
        "missing": len(equipment.filtered(lambda e: e.operational_status == "missing")),
        "impact_open": len(_scoped(env, "fix.calibration.impact", [("state", "=", "open")])),
        "custody_overdue": len(overdue_issues),
        # capture audit 2026-11-16
        "loss_open": len(
            _scoped(
                env, "fix.equipment.loss", [("state", "in", ("reported", "writeoff_requested"))]
            )
        ),
    }
