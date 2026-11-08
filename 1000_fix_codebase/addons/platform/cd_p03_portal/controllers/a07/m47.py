# A07 · M47 Facility & Branch Infrastructure — surfaces, packs and KPIs over the
# site register, leases, licences, utilities, conditions, building PM, work
# orders, safety equipment, incidents and site projects.
import datetime

from odoo import fields

from ..p03_service_order_api import _company_domain

SURFACES = {
    # A07 P0 recipe (2026-11-03): workflow fields are guarded on the models;
    # every transition below checks its source state, and the approvals are
    # requested here and decided from the approver's M63 inbox.
    # A07 P1/P2 (2026-11-04): the readiness gate (Open), resumption, permit
    # to work, lease renewal decisions, utility anomaly review and the
    # operating-risk exception decisions; the rent schedule and the IFRS 16
    # extracts are read-only registers.
    # A07 operability (2026-11-07), M47-14: "rules" reads every estate record as
    # the caller, so security/fix_facility_scope_rules.xml decides. The default
    # sudo read showed another company's or unit's rent, deposits and licences.
    "fix.site": {
        "order": "name",
        "limit": 200,
        "rules": True,
        "actions": {
            "action_open",
            "action_resume",
            "action_close",
            "action_reopen",
            "action_request_approval",
            "action_request_closure",
            "action_recall_approval",
        },
    },
    "fix.site.condition": {
        "order": "inspected_on desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": set(),
    },
    "fix.site.asset": {
        "order": "site_id, asset_type, name",
        "limit": 400,
        "rules": True,
        "actions": {
            "action_maintenance",
            "action_restore",
            "action_retire",
            "action_request_approval",
            "action_recall_approval",
        },
    },
    "fix.site.lease": {
        "order": "end_date desc, id desc",
        "limit": 200,
        "rules": True,
        "actions": {
            "action_open_modification",
            "action_discard_modification",
            "action_request_approval",
            "action_recall_approval",
            "action_publish_ifrs16",
            "action_apply_modification",
            "action_expire",
            "action_terminate",
            "action_decide_renew",
            "action_decide_renegotiate",
            "action_decide_exit",
        },
    },
    "fix.site.lease.schedule": {
        "order": "lease_id, due_date",
        "limit": 600,
        "rules": True,
        "actions": {"action_send_to_ap"},
    },
    "fix.site.lease.extract": {
        "order": "lease_id, version desc",
        "limit": 300,
        "rules": True,
        "actions": set(),
    },
    "fix.site.risk.exception": {
        "order": "raised_at desc, id desc",
        "limit": 200,
        "rules": True,
        "actions": {"action_decide_continue", "action_decide_suspend"},
    },
    "fix.site.licence": {
        "order": "valid_to desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": set(),
    },
    "fix.site.utility": {
        "order": "period desc, id desc",
        "limit": 400,
        "rules": True,
        "actions": {"action_flag", "action_release", "action_confirm_anomaly", "action_send_to_ap"},
    },
    "fix.site.pm": {
        "order": "scheduled_on desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": {"action_done"},
    },
    "fix.facility.work.order": {
        "order": "scheduled_date desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": {
            "action_triage",
            "action_request_approval",
            "action_recall_approval",
            "action_schedule",
            "action_start",
            "action_complete",
            "action_verify",
            "action_reopen",
            "action_cancel",
            "action_approve_permit",
        },
    },
    "fix.site.safety": {
        "order": "next_check",
        "limit": 400,
        "rules": True,
        "actions": {"action_check_pass", "action_check_fail"},
    },
    "fix.site.incident": {
        "order": "occurred_on desc, id desc",
        "limit": 200,
        "rules": True,
        "actions": {"action_close"},
    },
    "fix.site.project": {
        "order": "planned_on desc, id desc",
        "limit": 200,
        "rules": True,
        "actions": {
            "action_start",
            "action_done",
            "action_request_approval",
            "action_recall_approval",
            "action_revise_budget",
        },
    },
    # A07 P1 work-order spine (cd_asset_workorder_spine): the queue of maintenance
    # demands that wait for a missing fact before they route.
    "fix.maintenance.demand": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_route", "action_dismiss"},
    },
    # A07 operability (2026-11-07): the bridge's hand-off queues had only backend
    # menus. The three finance queues are read company-wide as finance reads (the
    # ACL admits only the accounting groups); the hand-off problems are readable
    # by any internal user, so they keep to the caller's units.
    "fix.asset.cost.entry": {
        "order": "state, cost_date desc, id desc",
        "limit": 300,
        "actions": {"action_match_bill", "action_reject"},
        "pickers": {"match_invoice_id": [("approval_state", "!=", "rejected")]},
    },
    "fix.asset.finance.request": {
        "order": "state, create_date desc, id desc",
        "limit": 300,
        "actions": {"action_accept", "action_reject"},
        "pickers": {
            "acquisition_line_id": [("parent_state", "=", "posted"), ("debit", ">", 0)],
            "fixed_asset_id": [("state", "=", "active")],
        },
    },
    "fix.lease.modification.item": {
        "order": "state, create_date desc, id desc",
        "limit": 300,
        "actions": {"action_mark_remeasured", "action_mark_no_change"},
    },
    "fix.bridge.exception": {
        "order": "state, create_date desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": {"action_retry", "action_resolve"},
    },
    # The alerts of all five A07 modules; each module's screen filters its own.
    "fix.asset.alert": {
        "order": "state desc, last_raised_on desc, id desc",
        "limit": 200,
        "rules": True,
        "actions": {"action_acknowledge"},
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


def _read(env, model, domain=None):
    """What the caller may see of `model`: searched as the caller, so the
    company and operating-unit rules apply, and then read as sudo, so a report
    row can name an engineer without the reader holding an HR role.

    A07 audit (2026-11-03, M47-14): every KPI and report read with
    `sudo().search([])`, so a company-B user was shown company A's estate. The
    company fence stopped that; another unit's rent still showed until the
    search became the caller's (2026-11-07)."""
    scope = _company_domain(env, model) if "company_id" in env[model]._fields else []
    return env[model].search(scope + list(domain or [])).sudo()


def _sites(env):
    return _read(env, "fix.site")


# Work done: a completed (awaiting verification) or verified work order.
_WO_DONE = ("completed", "verified")


def _wo_spend(order):
    """What a work order has spent: its actual cost once the work is done.

    A07 audit (2026-11-03, M47-7): a completed WO with no actual cost was
    reported at its estimate, and open WOs' estimates were reported as spend.
    An estimate is a forecast; only completed work is spend."""
    return (order.actual_cost or 0.0) if order.state in _WO_DONE else 0.0


def _pm_spend(pm):
    """What a building PM job has spent on its own: its cost once done. An open
    job has spent nothing, and one done under a work order is that order's spend."""
    if pm.state != "done":
        return 0.0
    if pm.work_order_id and pm.work_order_id.state != "cancelled":
        return 0.0
    return pm.cost or 0.0


def _today(env):
    # the models derive validity and overdue status on the Dhaka date; the
    # figures here must use the same date, not the server's UTC one
    return fields.Date.context_today(env["fix.site"])


# BRU-FAC-01: every operational site holds a current trade licence, and a fire
# licence "where required by site type". No site-type requirement is recorded
# anywhere, so fire (and every other type) is a gap only where a licence of
# that type exists at the site and none of them is current. The rule is not
# guessed per site type.
_REQUIRED_LICENCE_TYPES = ("trade",)


def _licence_basis(licence, today):
    """Why a licence row is, or is not, valid today (one source for all packs)."""
    if not licence:
        return "Missing: no licence on record (required for every operational site)"
    if licence.state == "suspended":
        return "Suspended"
    if licence.state == "expired":
        return "Expired"
    if not licence.valid_to:
        return "No expiry date recorded: treated as not valid (AC-21)"
    if licence.valid_to < today:
        return "Lapsed on %s" % licence.valid_to
    return "Valid"


def _licence_gaps(env, sites, licences, today):
    """One gap per ACTIVE site and licence type with no current licence: a
    required type held by nobody, or a type whose rows have all lapsed. A
    lapsed licence that a current renewal of the same type supersedes is not
    a gap; a lapsed licence at a closed site is not either."""
    gaps = []
    for site in sites.filtered(lambda s: s.state == "active"):
        held = licences.filtered(lambda ln, sid=site.id: ln.site_id.id == sid)
        for ltype in sorted(set(_REQUIRED_LICENCE_TYPES) | set(held.mapped("licence_type"))):
            rows = held.filtered(lambda ln, t=ltype: ln.licence_type == t)
            if any(rows.mapped("is_valid")):
                continue
            latest = rows.sorted(
                key=lambda ln: (ln.valid_to or datetime.date.min, ln.id), reverse=True
            )[:1]
            gaps.append(
                {
                    "site": site,
                    "type": ltype,
                    "licence": latest,
                    "basis": _licence_basis(latest, today),
                }
            )
    return gaps


def _licence_type_label(env, ltype):
    return dict(env["fix.site.licence"]._fields["licence_type"].selection).get(ltype, ltype)


def critical_dates(env, date_from=None, date_to=None, **params):
    today = _today(env)
    horizon = today + datetime.timedelta(days=180)
    rows = []
    # An active lease past its end date stays listed (negative days-left)
    # until the daily job expires it; the renewal-notice deadline is listed
    # while no renewal decision is recorded (BRU-FAC-05).
    for lease in _read(env, "fix.site.lease", [("state", "=", "active")]):
        notice = lease.renewal_notice_date
        if notice and notice != lease.end_date and not lease.renewal_decision and notice <= horizon:
            rows.append(
                {
                    "date": str(notice),
                    "kind": "Lease renewal notice deadline (decision required)",
                    "site": lease.site_id.name,
                    "reference": lease.name,
                    "days_left": (notice - today).days,
                }
            )
        if lease.end_date and lease.end_date <= horizon:
            rows.append(
                {
                    "date": str(lease.end_date),
                    "kind": "Lease end" if lease.end_date >= today else "Lease ended, still active",
                    "site": lease.site_id.name,
                    "reference": lease.name,
                    "days_left": (lease.end_date - today).days,
                }
            )
    sites = _sites(env)
    licences = _read(env, "fix.site.licence")
    # current licences expiring inside 90 days ...
    for licence in licences.filtered(
        lambda ln: ln.is_valid and ln.valid_to <= today + datetime.timedelta(days=90)
    ):
        rows.append(
            {
                "date": str(licence.valid_to),
                "kind": "Licence expiry (%s)" % _licence_type_label(env, licence.licence_type),
                "site": licence.site_id.name,
                "reference": licence.name,
                "days_left": (licence.valid_to - today).days,
            }
        )
    # ... and every licence gap at an active site: lapsed, undated or missing
    for gap in _licence_gaps(env, sites, licences, today):
        licence = gap["licence"]
        dated = bool(licence and licence.valid_to)
        rows.append(
            {
                "date": str(licence.valid_to) if dated else "—",
                "kind": "Licence gap (%s): %s"
                % (_licence_type_label(env, gap["type"]), gap["basis"]),
                "site": gap["site"].name,
                "reference": licence.name if licence else "—",
                "days_left": (licence.valid_to - today).days if dated else "—",
            }
        )
    for safety in _read(env, "fix.site.safety"):
        if safety.next_check and safety.next_check <= today + datetime.timedelta(days=30):
            rows.append(
                {
                    "date": str(safety.next_check),
                    "kind": "Safety check (%s)" % safety.equipment_type,
                    "site": safety.site_id.name,
                    "reference": safety.name,
                    "days_left": (safety.next_check - today).days,
                }
            )
    # undated gaps (missing or open-ended licences) first, then by date
    rows.sort(key=lambda r: (r["date"] != "—", r["date"]))
    return _pack(
        "Critical-Date Control — leases (180d), licences (90d) and safety checks (30d)",
        ["date", "kind", "site", "reference", "days_left"],
        {
            "date": "Date",
            "kind": "Kind",
            "site": "Site",
            "reference": "Reference",
            "days_left": "Days Left",
        },
        rows,
        [
            "Negative days-left means the date has passed and the item is overdue. The "
            "daily job expires a lease past its end date (unless a modification is open) "
            "and raises an operating-risk exception for a lapsed licence at an operational "
            "site.",
            "Licence gaps: an operational site with no current trade licence, or a "
            "licence type held at the site whose every row has lapsed. A licence with no "
            "expiry date is not treated as valid.",
        ],
        empty="No critical date inside the horizons.",
    )


def branch_assets(env, date_from=None, date_to=None, **params):
    orders = _read(env, "fix.facility.work.order")
    rows = []
    for site in _sites(env):
        site_orders = orders.filtered(lambda o, sid=site.id: o.site_id.id == sid)
        # retired plant has left the register's count and value
        plant = site.asset_ids.filtered(lambda a: a.state != "retired")
        rows.append(
            {
                "site": site.name,
                "type": dict(site._fields["site_type"].selection).get(site.site_type),
                "branch": site.branch_id.name if site.branch_id else "—",
                "area_sqm": round(site.floor_area_sqm or 0.0, 2),
                "assets": len(plant),
                "asset_value": round(sum(plant.mapped("value")), 2),
                "work_orders": len(site_orders),
                "spend": round(sum(_wo_spend(o) for o in site_orders), 2),
            }
        )
    rows.sort(key=lambda r: -r["spend"])
    return _pack(
        "Branch Asset Register — plant, equipment and work-order spend per site",
        ["site", "type", "branch", "area_sqm", "assets", "asset_value", "work_orders", "spend"],
        {
            "site": "Site",
            "type": "Type",
            "branch": "Branch",
            "area_sqm": "Area (sqm)",
            "assets": "Plant Assets",
            "asset_value": "Asset Value",
            "work_orders": "Work Orders",
            "spend": "WO Spend",
        },
        rows,
        [
            "Plant assets are the site infrastructure register (HVAC, lift, generator, "
            "fire pump, UPS, CCTV), without retired plant; spend is the actual cost of "
            "completed and verified "
            "work orders (an open work order's estimate is not spend)."
        ],
        totals={
            "site": "Total",
            "assets": sum(r["assets"] for r in rows),
            "asset_value": round(sum(r["asset_value"] for r in rows), 2),
            "work_orders": sum(r["work_orders"] for r in rows),
            "spend": round(sum(r["spend"] for r in rows), 2),
        },
        empty="No sites registered yet.",
    )


def cost_per_site(env, date_from=None, date_to=None, **params):
    utilities = _read(env, "fix.site.utility")
    pms = _read(env, "fix.site.pm")
    orders = _read(env, "fix.facility.work.order")
    rows = []
    leases = _read(env, "fix.site.lease", [("state", "=", "active")])
    for site in _sites(env):
        utility = sum(
            utilities.filtered(lambda u, sid=site.id: u.site_id.id == sid).mapped("amount")
        )
        # FR-FAC-012: the scheduled (escalated) rent of the site's active
        # leases; the site record's own figure only where no lease exists
        site_leases = leases.filtered(lambda ln, sid=site.id: ln.site_id.id == sid)
        rent = (
            sum(site_leases.mapped("current_rent")) if site_leases else (site.monthly_rent or 0.0)
        )
        pm = sum(_pm_spend(p) for p in pms.filtered(lambda p, sid=site.id: p.site_id.id == sid))
        wo = sum(_wo_spend(o) for o in orders.filtered(lambda o, sid=site.id: o.site_id.id == sid))
        rows.append(
            {
                "site": site.name,
                "rent": round(rent, 2),
                "utilities": round(utility, 2),
                "pm": round(pm, 2),
                "work_orders": round(wo, 2),
                "total": round(rent + utility + pm + wo, 2),
            }
        )
    rows.sort(key=lambda r: -r["total"])
    return _pack(
        "Cost per Site / per Job — rent, utilities, PM and work orders",
        ["site", "rent", "utilities", "pm", "work_orders", "total"],
        {
            "site": "Site",
            "rent": "Monthly Rent",
            "utilities": "Utilities",
            "pm": "Building PM",
            "work_orders": "Work Orders",
            "total": "Total",
        },
        rows,
        [
            "Monthly rent is this month's scheduled rent of the site's active leases "
            "(escalated on each anniversary); the site record's figure is used only where "
            "no lease is recorded. Utilities, PM and work orders are the recorded records "
            "(no period filter applied here). Building PM counts jobs done without a work "
            "order; a job done under a work order is counted once, at that order's actual "
            "cost. Work orders count the actual cost of completed and verified work."
        ],
        totals={
            "site": "Total",
            "rent": round(sum(r["rent"] for r in rows), 2),
            "utilities": round(sum(r["utilities"] for r in rows), 2),
            "pm": round(sum(r["pm"] for r in rows), 2),
            "work_orders": round(sum(r["work_orders"] for r in rows), 2),
            "total": round(sum(r["total"] for r in rows), 2),
        },
        empty="No sites registered yet.",
    )


def lease_expiry(env, date_from=None, date_to=None, **params):
    today = _today(env)
    rows = []
    for lease in _read(env, "fix.site.lease"):
        rows.append(
            {
                "lease": lease.name,
                "site": lease.site_id.name,
                "lessor": lease.lessor_id.name,
                "start": str(lease.start_date),
                "end": str(lease.end_date),
                "rent": round(lease.current_rent, 2),
                "days_left": (lease.end_date - today).days if lease.end_date else "—",
                "decision": dict(lease._fields["renewal_decision"].selection).get(
                    lease.renewal_decision, "—"
                ),
                "state": (
                    "Active, past end date (no decision recorded)"
                    if lease.state == "active" and lease.end_date and lease.end_date < today
                    else dict(lease._fields["state"].selection).get(lease.state)
                ),
            }
        )
    rows.sort(key=lambda r: r["end"])
    return _pack(
        "Lease Expiry Register",
        ["lease", "site", "lessor", "start", "end", "rent", "days_left", "decision", "state"],
        {
            "lease": "Lease",
            "site": "Site",
            "lessor": "Lessor",
            "start": "Start",
            "end": "End",
            "rent": "Current Monthly Rent",
            "days_left": "Days Left",
            "decision": "Renewal Decision",
            "state": "State",
        },
        rows,
        [
            "Current monthly rent is this month's row of the rent schedule (the "
            "commencement rent escalated on each anniversary). Days-left is computed from "
            "the lease end date; the daily job expires a lease once it has passed."
        ],
        empty="No leases recorded.",
    )


def licence_compliance(env, date_from=None, date_to=None, **params):
    today = _today(env)
    licences = _read(env, "fix.site.licence")
    gaps = _licence_gaps(env, _sites(env), licences, today)
    rows = []
    for licence in licences:
        rows.append(
            {
                "licence": licence.name,
                "site": licence.site_id.name,
                "type": _licence_type_label(env, licence.licence_type),
                "number": licence.number or "—",
                "valid_to": str(licence.valid_to) if licence.valid_to else "—",
                "valid": licence.is_valid,
                "basis": _licence_basis(licence, today),
                "state": dict(licence._fields["state"].selection).get(licence.state),
            }
        )
    # a required licence that no row exists for is a gap the register must show
    for gap in gaps:
        if not gap["licence"]:
            rows.append(
                {
                    "licence": "—",
                    "site": gap["site"].name,
                    "type": _licence_type_label(env, gap["type"]),
                    "number": "—",
                    "valid_to": "—",
                    "valid": False,
                    "basis": gap["basis"],
                    "state": "Missing",
                }
            )
    rows.sort(key=lambda r: (r["valid"], r["valid_to"]))
    return _pack(
        "Licence Compliance — statutory licences per site",
        ["licence", "site", "type", "number", "valid_to", "valid", "basis", "state"],
        {
            "licence": "Licence",
            "site": "Site",
            "type": "Type",
            "number": "Number",
            "valid_to": "Valid To",
            "valid": "Valid Today",
            "basis": "Basis",
            "state": "State",
        },
        rows,
        [
            "Valid today = state Valid AND an end date is recorded AND it has not passed. "
            "A licence with no end date is not treated as valid (AC-21).",
            "%d licence gap(s) at operational sites: every operational site needs a current "
            "trade licence; fire and other types are a gap where the site holds that type "
            "and none is current (no site-type requirement is recorded)." % len(gaps),
        ],
        empty="No licences recorded.",
    )


def utilities_variance(env, date_from=None, date_to=None, **params):
    rows = []
    for utility in _read(env, "fix.site.utility"):
        rows.append(
            {
                "record": utility.name,
                "site": utility.site_id.name,
                "period": utility.period,
                "type": dict(utility._fields["utility_type"].selection).get(utility.utility_type),
                "amount": round(utility.amount, 2),
                "usage": round(utility.usage, 2),
                "unit": utility.unit or "—",
                "flagged": utility.flagged,
                "hold": dict(utility._fields["review_state"].selection).get(utility.review_state),
                "basis": utility.anomaly_basis or "—",
            }
        )
    rows.sort(key=lambda r: (r["site"], r["period"]))
    flagged = len([r for r in rows if r["flagged"]])
    return _pack(
        "Utilities Variance — recorded accounts and anomaly flags",
        [
            "record",
            "site",
            "period",
            "type",
            "amount",
            "usage",
            "unit",
            "flagged",
            "hold",
            "basis",
        ],
        {
            "record": "Account",
            "site": "Site",
            "period": "Period",
            "type": "Type",
            "amount": "Amount",
            "usage": "Usage",
            "unit": "Unit",
            "flagged": "Flagged",
            "hold": "Payment Hold",
            "basis": "Anomaly Basis",
        },
        rows,
        [
            "%d bill(s) flagged. A bill whose amount or usage reaches the configured multiple "
            "(cd_facility.utility_anomaly_factor, default 2.0 pending business confirmation) "
            "of its own average over up to the last 3 periods is held from payment until a "
            "Branch Operations Lead who did not record it releases or confirms it." % flagged
        ],
        totals={"record": "Total", "amount": round(sum(r["amount"] for r in rows), 2)},
        empty="No utility accounts recorded.",
    )


def work_order_performance(env, date_from=None, date_to=None, **params):
    orders = _read(env, "fix.facility.work.order")
    rows = []
    for order in orders:
        rows.append(
            {
                "order": order.name,
                "site": order.site_id.name,
                "type": dict(order._fields["work_type"].selection).get(order.work_type),
                "scheduled": str(order.scheduled_date) if order.scheduled_date else "—",
                "engineer": order.assigned_to.name if order.assigned_to else "—",
                "estimate": round(order.estimated_cost, 2),
                "actual": round(order.actual_cost, 2),
                "state": dict(order._fields["state"].selection).get(order.state),
            }
        )
    rows.sort(key=lambda r: str(r["scheduled"]), reverse=True)
    done = len(orders.filtered(lambda o: o.state in _WO_DONE))
    return _pack(
        "Facility Work Order Performance",
        ["order", "site", "type", "scheduled", "engineer", "estimate", "actual", "state"],
        {
            "order": "Work Order",
            "site": "Site",
            "type": "Type",
            "scheduled": "Scheduled",
            "engineer": "Engineer",
            "estimate": "Estimate",
            "actual": "Actual",
            "state": "State",
        },
        rows,
        ["%d of %d work orders completed or verified." % (done, len(rows))],
        totals={
            "order": "Total",
            "estimate": round(sum(r["estimate"] for r in rows), 2),
            "actual": round(sum(r["actual"] for r in rows), 2),
        },
        empty="No facility work orders recorded.",
    )


REPORTS = {
    "critical_dates": critical_dates,
    "branch_assets": branch_assets,
    "cost_per_site": cost_per_site,
    "lease_expiry": lease_expiry,
    "licence_compliance": licence_compliance,
    "utilities_variance": utilities_variance,
    "work_order_performance": work_order_performance,
}


_SQFT_PER_SQM = 10.7639


def _utilities_cost_per_sqft(utilities, today):
    """Utilities cost per sq ft for ONE month: the latest complete period.

    A07 audit (2026-11-03, M47-13): the KPI divided every bill ever recorded
    by the floor area, so it grew each month (live ৳41.11 for six months,
    about ৳6.9 a month). It now takes the latest period before the current
    month (the current month is still being billed) and divides that
    period's bills by the floor area of the sites billed in it, so an
    unbilled or area-less site neither inflates nor dilutes the figure."""
    current = today.strftime("%Y-%m")
    billed = utilities.filtered(
        lambda u: u.period and u.period < current and u.site_id.floor_area_sqm > 0
    )
    if not billed:
        return None, 0.0
    period = max(billed.mapped("period"))
    rows = billed.filtered(lambda u: u.period == period)
    sqft = sum(rows.mapped("site_id").mapped("floor_area_sqm")) * _SQFT_PER_SQM
    return period, (round(sum(rows.mapped("amount")) / sqft, 2) if sqft else 0.0)


def kpis(env):
    sites = _sites(env)
    today = _today(env)
    horizon = today + datetime.timedelta(days=90)
    leases = _read(env, "fix.site.lease", [("state", "=", "active")])
    licences = _read(env, "fix.site.licence")
    utilities = _read(env, "fix.site.utility")
    orders = _read(env, "fix.facility.work.order")
    safety = _read(env, "fix.site.safety")
    period, cost_per_sqft = _utilities_cost_per_sqft(utilities, today)
    return {
        "sites_active": len(sites.filtered(lambda s: s.state == "active")),
        # an active lease already past its end date is overdue for a decision,
        # not off the list (A07 audit 2026-11-03, M47-8): nothing expires it
        "leases_expiring_90d": len(leases.filtered(lambda ln: ln.end_date <= horizon)),
        "leases_past_end": len(leases.filtered(lambda ln: ln.end_date < today)),
        # gaps, not rows: lapsed / undated / missing per active site and type
        "licences_expired": len(_licence_gaps(env, sites, licences, today)),
        "utilities_flagged": len(utilities.filtered(lambda u: u.flagged)),
        "utilities_held": len(utilities.filtered(lambda u: u.review_state == "held")),
        "risk_exceptions_open": len(
            _read(
                env,
                "fix.site.risk.exception",
                [("state", "in", ("open", "continue", "suspend"))],
            )
        ),
        "sites_planned": len(sites.filtered(lambda s: s.state == "planned")),
        "sites_suspended": len(sites.filtered(lambda s: s.state == "suspended")),
        "utilities_cost_per_sqft": cost_per_sqft,
        "utilities_cost_period": period,
        "open_work_orders": len(orders.filtered(lambda o: o.state not in (*_WO_DONE, "cancelled"))),
        # derived from next_check, not a typed status (M47-9)
        "safety_overdue": len(safety.filtered(lambda s: s.state in ("overdue", "unfit"))),
        "safety_due": len(safety.filtered(lambda s: s.state in ("due", "overdue", "unfit"))),
    }
