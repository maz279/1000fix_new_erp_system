# A07 · M45 Enterprise Assets & Test Equipment — surfaces, packs and KPIs over
# the equipment register/calibration plus kits, issue/return, transfers,
# verification, out-of-service, PM and usage.
import datetime

from odoo import fields

from ..p03_service_order_api import _company_domain

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
        "actions": {"action_return"},
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
    "fix.equipment.category": {"order": "classification, code", "limit": 200, "actions": set()},
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
        "actions": {"action_recover", "action_send_to_repair", "action_request_writeoff"},
    },
    "fix.equipment.audit": {
        "order": "scheduled_for desc, id desc",
        "limit": 300,
        "actions": {"action_start", "action_complete"},
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


def _scoped(env, model, domain=None):
    """sudo() read for a report or KPI, fenced to the caller's companies.

    A07 audit (2026-11-03) M45-10: every pack read `sudo().search([])`, so the
    calibration schedule of one company listed another company's instruments.
    The ops models (issue, OOS, PM, usage, verification) carry no company_id;
    they follow their equipment."""
    Model = env[model].sudo()
    if "company_id" in Model._fields:
        fence = _company_domain(env, model)
    else:
        fence = [
            "|",
            ("equipment_id.company_id", "=", False),
            ("equipment_id.company_id", "in", env.user.company_ids.ids),
        ]
    return Model.search(list(domain or []) + fence)


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
    today = datetime.date.today()
    rows = []
    for equipment in _equipment(env):
        days = (equipment.next_calibration - today).days if equipment.next_calibration else None
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
    usages = _scoped(env, "fix.equipment.usage")
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


def calibration_compliance(env, date_from=None, date_to=None, **params):
    today = fields.Date.context_today(env["fix.equipment"])
    horizon = today + datetime.timedelta(days=30)
    rows = []
    for equipment in _equipment(env):
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
            "Status counts: " + ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items())),
            "From the latest calibration only: failed, overdue, rejected, awaiting a usage "
            "decision and never calibrated are not current, and the fitness gate refuses them.",
        ],
        empty="No equipment registered yet.",
    )


def utilisation(env, date_from=None, date_to=None, **params):
    usages = _scoped(env, "fix.equipment.usage")
    rows = []
    for equipment in _equipment(env):
        uses = usages.filtered(lambda u, eid=equipment.id: u.equipment_id.id == eid)
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "uses": len(uses),
                "total_uses": sum(uses.mapped("uses")),
                "qc_uses": len(uses.filtered(lambda u: u.qc_result != "na")),
                "last_used": str(max(uses.mapped("used_on"))) if uses else "—",
                "status": equipment.operational_status,
            }
        )
    rows.sort(key=lambda r: -r["total_uses"])
    return _pack(
        "Equipment Utilisation — recorded uses per item",
        ["code", "name", "uses", "total_uses", "qc_uses", "last_used", "status"],
        {
            "code": "Code",
            "name": "Equipment",
            "uses": "Usage Rows",
            "total_uses": "Total Uses",
            "qc_uses": "QC Uses",
            "last_used": "Last Used",
            "status": "Status",
        },
        rows,
        [
            "Counts recorded usage rows only; an item with no usage rows shows 0 — "
            "absence of data is not evidence of no use."
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
    verifications = _scoped(env, "fix.equipment.verification", [("state", "=", "missing")])
    losses = _scoped(env, "fix.equipment.loss")
    status = dict(env["fix.equipment"]._fields["operational_status"].selection)
    rows = []
    for record in verifications:
        rows.append(
            {
                "code": record.equipment_id.code,
                "name": record.equipment_id.name,
                "source": "Count %s" % record.campaign_ref,
                "on": str(record.verified_on),
                "custodian": record.verifier_id.name if record.verifier_id else "—",
                "value": record.equipment_id.acquisition_cost or 0.0,
                "decision": "missing at count",
                "status": status.get(record.equipment_id.operational_status),
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
    pms = _scoped(env, "fix.equipment.pm")
    calibrations = _scoped(env, "fix.calibration")
    rows = []
    for equipment in _equipment(env):
        equipment_pm = pms.filtered(lambda p, eid=equipment.id: p.equipment_id.id == eid)
        rows.append(
            {
                "code": equipment.code,
                "name": equipment.name,
                "pm_jobs": len(equipment_pm),
                "pm_cost": round(sum(equipment_pm.mapped("cost")), 2),
                "downtime": round(sum(equipment_pm.mapped("downtime_hours")), 1),
                "calibrations": len(
                    calibrations.filtered(lambda c, eid=equipment.id: c.equipment_id.id == eid)
                ),
                "status": equipment.operational_status,
            }
        )
    rows.sort(key=lambda r: -r["pm_cost"])
    return _pack(
        "Cost of Ownership — recorded PM cost and calibration count",
        ["code", "name", "pm_jobs", "pm_cost", "downtime", "calibrations", "status"],
        {
            "code": "Code",
            "name": "Equipment",
            "pm_jobs": "PM Jobs",
            "pm_cost": "PM Cost",
            "downtime": "Downtime (h)",
            "calibrations": "Calibrations",
            "status": "Status",
        },
        rows,
        [
            "Only recorded PM cost is summed. The acquisition cost on the register is "
            "the write-off basis, and calibration, repair and downtime costs are not "
            "recorded, so total cost of ownership is not claimed."
        ],
        totals={
            "code": "Total",
            "pm_jobs": sum(r["pm_jobs"] for r in rows),
            "pm_cost": round(sum(r["pm_cost"] for r in rows), 2),
            "calibrations": sum(r["calibrations"] for r in rows),
        },
        empty="No equipment registered yet.",
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
}


def kpis(env):
    equipment = _equipment(env)
    in_use = equipment.filtered(lambda e: e.operational_status != "retired")
    return {
        "equipment_total": len(equipment),
        "calibration_overdue": len(equipment.filtered(lambda e: e.calibration_overdue)),
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
        "issued_out": len(_scoped(env, "fix.equipment.issue", [("state", "=", "issued")])),
        "kits": len(_scoped(env, "fix.equipment.kit", [("active", "=", True)])),
        "pm_open": len(_scoped(env, "fix.equipment.pm", [("state", "=", "open")])),
        # A07 P1/P2 (2026-11-04)
        "missing": len(equipment.filtered(lambda e: e.operational_status == "missing")),
        "impact_open": len(_scoped(env, "fix.calibration.impact", [("state", "=", "open")])),
        "custody_overdue": len(_scoped(env, "fix.equipment.issue", [("is_overdue", "=", True)])),
        # capture audit 2026-11-16
        "loss_open": len(
            _scoped(
                env, "fix.equipment.loss", [("state", "in", ("reported", "writeoff_requested"))]
            )
        ),
    }
