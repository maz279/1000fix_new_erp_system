# A07 · M47 Facility & Branch Infrastructure — surfaces, packs and KPIs over the
# site register, leases, licences, utilities, conditions, building PM, work
# orders, safety equipment, incidents and site projects.
import datetime

from odoo import fields

from ..p03_service_order_api import _company_domain
from .writable import WRITABLE

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
            # A07 ERP audit (2026-11-20) D6 / M47-04/08
            "action_activate",
            "action_request_termination",
            "action_withdraw_termination",
            "action_settle_deposit",
        },
    },
    "fix.site.lease.schedule": {
        "order": "lease_id, due_date",
        "limit": 600,
        "rules": True,
        "actions": {"action_send_to_ap"},
    },
    # A07 ERP audit (2026-11-20): deposits, advance rent, licence fees and
    # penalties (M47-08/10), project actual cost (M47-11), outage SLA impact (M47-17)
    "fix.site.charge": {
        "order": "charge_date desc, id desc",
        "limit": 400,
        "rules": True,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_confirm",
            "action_cancel",
        },
    },
    "fix.site.project.cost": {
        "order": "cost_date desc, id desc",
        "limit": 400,
        "rules": True,
        "actions": {"action_confirm", "action_cancel"},
        "pickers": {"project_id": [("state", "in", ("planned", "in_progress"))]},
    },
    "fix.site.outage.impact": {
        "order": "window_start desc, id desc",
        "limit": 400,
        "rules": True,
        "actions": set(),
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
        # M47-26: a suspension and its lifting are actions, never a field edit
        "actions": {"action_suspend", "action_reinstate"},
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
            "action_accept",
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
    # M47 capture audit (2026-11-17): the registers a page could not capture.
    "fix.site.type.profile": {
        "order": "site_type",
        "limit": 50,
        "actions": set(),
    },
    "fix.site.lease.event": {
        "order": "state, due_on, id",
        "limit": 300,
        "rules": True,
        "actions": {
            "action_decide_exercise",
            "action_decide_decline",
            "action_mark_met",
            "action_cancel",
        },
        "pickers": {
            "lease_id": [("state", "=", "active")],
            "responsible_id": [("share", "=", False)],
        },
    },
    "fix.site.licence.renewal": {
        "order": "initiated_on desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": {"action_submit", "action_complete", "action_cancel"},
        "pickers": {
            "licence_id": [("state", "!=", "suspended")],
            "new_licence_id": [("state", "=", "valid")],
            "responsible_id": [("share", "=", False)],
        },
    },
    "fix.site.utility.account": {
        "order": "site_id, utility_type, name",
        "limit": 400,
        "rules": True,
        "actions": {"action_close"},
    },
    "fix.site.outage": {
        "order": "started_at desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": {"action_end"},
        "pickers": {"asset_id": [("state", "!=", "retired")]},
    },
    "fix.site.power.test": {
        "order": "tested_on desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": set(),
        "pickers": {
            "asset_id": [("asset_type", "in", ("generator", "ups")), ("state", "!=", "retired")]
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
        "actions": {"action_new_remeasurement", "action_mark_remeasured", "action_mark_no_change"},
    },
    # A07 ERP audit (2026-11-20) FIN-07: the remeasurement document a
    # modification item needs before it may be marked remeasured; prepared by
    # one accountant, posted by another (the model enforces it).
    "fix.lease.remeasurement": {
        "order": "state, effective_date desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": {"action_post", "action_cancel"},
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


# A surface added by the A07 ERP audit (2026-11-20) is served once writable.py
# (generated from the workspace forms) lists it; until it is regenerated the
# package would refuse to load (a07/__init__.py reads WRITABLE[model] for each).
for _new in (
    "fix.site.charge",
    "fix.site.project.cost",
    "fix.site.outage.impact",
    "fix.lease.remeasurement",
):
    if _new not in WRITABLE:
        SURFACES.pop(_new)


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
    # figures here must use the same date, not the server's or the user's one
    return fields.Date.context_today(env["fix.site"].with_context(tz="Asia/Dhaka"))


def _dates(date_from, date_to):
    """A07 ERP audit (2026-11-20) M47-22: the period a pack is asked for, as
    dates (either end may be open)."""

    def as_date(value):
        try:
            return fields.Date.to_date(value) if value else None
        except ValueError:
            return None

    return as_date(date_from), as_date(date_to)


def _in(day, start, end):
    """True when `day` falls in [start, end] (an open end admits everything)."""
    if not day:
        return not (start or end)
    if isinstance(day, datetime.datetime):
        day = day.date()
    return (not start or day >= start) and (not end or day <= end)


def _dhaka_day(moment):
    """The Dhaka date of a UTC datetime."""
    if not moment:
        return None
    return (moment + datetime.timedelta(hours=6)).date()


def _last_closed_month(today):
    first = today.replace(day=1)
    end = first - datetime.timedelta(days=1)
    return end.replace(day=1), end


# BRU-FAC-01: every operational site holds a current trade licence, and a fire
# licence "where required by site type". The site-type profile (M47 capture
# audit 2026-11-17) records what each type requires; a type with no profile
# requires the trade licence only, and any other type is a gap only where a
# licence of that type exists at the site and none of them is current.
_REQUIRED_LICENCE_TYPES = ("trade",)


def _required_licence_types(env, site):
    types = env["fix.site.type.profile"].sudo()._m47_required_types(site.site_type)
    return tuple(types) if types is not None else _REQUIRED_LICENCE_TYPES


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
        required = set(_required_licence_types(env, site))
        for ltype in sorted(required | set(held.mapped("licence_type"))):
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
    # the lease's other dated obligations (FR-FAC-009): open ones inside the
    # horizon, and any open one already past its date
    labels = dict(env["fix.site.lease.event"]._fields["event_type"]._description_selection(env))
    for event in _read(env, "fix.site.lease.event", [("state", "=", "open")]):
        if event.due_on <= horizon:
            rows.append(
                {
                    "date": str(event.due_on),
                    "kind": "Lease %s (%s)"
                    % (labels.get(event.event_type, event.event_type).lower(), event.lease_id.name),
                    "site": event.site_id.name,
                    "reference": event.name,
                    "days_left": (event.due_on - today).days,
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
    # M47-22: a period narrows the dated rows (undated gaps always show)
    start, end = _dates(date_from, date_to)
    if start or end:
        rows = [
            r for r in rows if r["date"] == "—" or _in(fields.Date.to_date(r["date"]), start, end)
        ]
    # undated gaps (missing or open-ended licences) first, then by date
    rows.sort(key=lambda r: (r["date"] != "—", r["date"]))
    return _pack(
        "Critical-Date Control — leases and their events (180d), licences (90d) and "
        "safety checks (30d)",
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
    start, end = _dates(date_from, date_to)
    # M47-22: spend in the period = work completed in it (Dhaka day)
    orders = _read(env, "fix.facility.work.order").filtered(
        lambda o: _in(_dhaka_day(o.completed_at), start, end) if (start or end) else True
    )
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
    """A07 ERP audit (2026-11-20) M47-21: every column is the SAME period
    (default: the last closed month): rent and service charge falling due in
    it, its utility bills, the PM and work orders completed in it and the
    licence renewals completed in it."""
    start, end = _dates(date_from, date_to)
    if not (start or end):
        start, end = _last_closed_month(_today(env))
    start = start or datetime.date.min
    end = end or datetime.date.max
    first_period, last_period = start.strftime("%Y-%m"), end.strftime("%Y-%m")
    utilities = _read(env, "fix.site.utility").filtered(
        lambda u: u.period and first_period <= u.period <= last_period
    )
    pms = _read(env, "fix.site.pm").filtered(lambda p: _in(p.done_on, start, end))
    orders = _read(env, "fix.facility.work.order").filtered(
        lambda o: _in(_dhaka_day(o.completed_at), start, end)
    )
    renewals = _read(env, "fix.site.licence.renewal", [("state", "=", "completed")]).filtered(
        lambda r: _in(r.completed_on, start, end)
    )
    schedule = _read(env, "fix.site.lease.schedule").filtered(
        lambda r: not r.cancelled and _in(r.due_date, start, end)
    )
    rows = []
    for site in _sites(env):
        utility = sum(
            utilities.filtered(lambda u, sid=site.id: u.site_id.id == sid).mapped("amount")
        )
        # FR-FAC-012: the rent (and service charge) the schedule makes due in
        # the period, escalated; never a single month beside a period's costs
        due = schedule.filtered(lambda r, sid=site.id: r.site_id.id == sid)
        rent = sum(due.mapped("rent_due")) + sum(due.mapped("service_charge_due"))
        pm = sum(_pm_spend(p) for p in pms.filtered(lambda p, sid=site.id: p.site_id.id == sid))
        wo = sum(_wo_spend(o) for o in orders.filtered(lambda o, sid=site.id: o.site_id.id == sid))
        compliance = sum(
            renewals.filtered(lambda r, sid=site.id: r.site_id.id == sid).mapped("total_cost")
        )
        total = rent + utility + pm + wo + compliance
        area = site.floor_area_sqm or 0.0
        rows.append(
            {
                "site": site.name,
                "rent": round(rent, 2),
                "utilities": round(utility, 2),
                "pm": round(pm, 2),
                "work_orders": round(wo, 2),
                "compliance": round(compliance, 2),
                "total": round(total, 2),
                "per_sqft": round(total / (area * _SQFT_PER_SQM), 2) if area else "—",
            }
        )
    rows.sort(key=lambda r: -r["total"])
    return _pack(
        "Cost per Site — %s to %s" % (start, end),
        ["site", "rent", "utilities", "pm", "work_orders", "compliance", "total", "per_sqft"],
        {
            "site": "Site",
            "rent": "Rent & Service Charge",
            "utilities": "Utilities",
            "pm": "Building PM",
            "work_orders": "Work Orders",
            "compliance": "Licence Renewals",
            "total": "Total",
            "per_sqft": "Total per sq ft",
        },
        rows,
        [
            "Every column is the same period (default: the last closed month): rent and "
            "service charge are the schedule's payments falling due in it; utilities the "
            "bills for its months; building PM the jobs done in it without a work order; "
            "work orders the actual cost of work completed in it; licence renewals the "
            "fees, agent costs and penalties of renewals completed in it (FR-FAC-021).",
            "IFRS 16 interest and right-of-use depreciation of a commenced lease are M49's "
            "and are not added here.",
        ],
        totals={
            "site": "Total",
            "rent": round(sum(r["rent"] for r in rows), 2),
            "utilities": round(sum(r["utilities"] for r in rows), 2),
            "pm": round(sum(r["pm"] for r in rows), 2),
            "work_orders": round(sum(r["work_orders"] for r in rows), 2),
            "compliance": round(sum(r["compliance"] for r in rows), 2),
            "total": round(sum(r["total"] for r in rows), 2),
        },
        empty="No sites registered yet.",
    )


def lease_expiry(env, date_from=None, date_to=None, **params):
    today = _today(env)
    start, end = _dates(date_from, date_to)
    rows = []
    for lease in _read(env, "fix.site.lease").filtered(
        lambda ln: _in(ln.end_date, start, end) if (start or end) else True
    ):
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
    start, end = _dates(date_from, date_to)
    rows = []
    for licence in licences.filtered(
        lambda ln: _in(ln.valid_to, start, end) if (start or end) else True
    ):
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
            "trade licence and every licence its site-type profile requires (Site Register, "
            "Site Type Profiles); any other type is a gap where the site holds that type and "
            "none is current." % len(gaps),
        ],
        empty="No licences recorded.",
    )


def utilities_variance(env, date_from=None, date_to=None, **params):
    start, end = _dates(date_from, date_to)
    first = start.strftime("%Y-%m") if start else "0000-00"
    last = end.strftime("%Y-%m") if end else "9999-99"
    rows = []
    for utility in _read(env, "fix.site.utility").filtered(
        lambda u: first <= (u.period or "") <= last
    ):
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
    start, end = _dates(date_from, date_to)
    orders = _read(env, "fix.facility.work.order").filtered(
        lambda o: _in(o.scheduled_date, start, end) if (start or end) else True
    )
    rows = []
    for order in orders:
        rows.append(
            {
                "order": order.name,
                "site": order.site_id.name,
                "type": dict(order._fields["work_type"].selection).get(order.work_type),
                "priority": dict(order._fields["priority"].selection).get(order.priority, "—"),
                "scheduled": str(order.scheduled_date) if order.scheduled_date else "—",
                "engineer": order.assigned_to.name if order.assigned_to else "—",
                "estimate": round(order.estimated_cost, 2),
                "actual": round(order.actual_cost, 2),
                # M47-16: whether the restore clock was kept (D15)
                "sla": (
                    "—"
                    if not order.restore_due_at
                    else ("Breached" if order.sla_restore_breached else "Within SLA")
                ),
                "state": dict(order._fields["state"].selection).get(order.state),
            }
        )
    rows.sort(key=lambda r: str(r["scheduled"]), reverse=True)
    done = len(orders.filtered(lambda o: o.state in _WO_DONE))
    timed = orders.filtered(lambda o: o.state in _WO_DONE and o.restore_due_at)
    kept = len(timed.filtered(lambda o: not o.sla_restore_breached))
    return _pack(
        "Facility Work Order Performance",
        [
            "order",
            "site",
            "type",
            "priority",
            "scheduled",
            "engineer",
            "estimate",
            "actual",
            "sla",
            "state",
        ],
        {
            "order": "Work Order",
            "site": "Site",
            "type": "Type",
            "priority": "Priority",
            "scheduled": "Scheduled",
            "engineer": "Engineer",
            "estimate": "Estimate",
            "actual": "Actual",
            "sla": "Restore SLA",
            "state": "State",
        },
        rows,
        [
            "%d of %d work orders completed or verified." % (done, len(rows)),
            "%d of %d timed jobs done restored within their SLA (D15: emergency 8 h, high "
            "48 h, normal 5 days, low 15 days from triage)." % (kept, len(timed)),
        ],
        totals={
            "order": "Total",
            "estimate": round(sum(r["estimate"] for r in rows), 2),
            "actual": round(sum(r["actual"] for r in rows), 2),
        },
        empty="No facility work orders recorded.",
    )


_AVAILABILITY_DAYS = 90


def infrastructure_availability(env, date_from=None, date_to=None, **params):
    """FR-FAC-027 / §14 Infrastructure availability: building-service outages
    per site over the last 90 days, with the branch operating hours lost."""
    now = fields.Datetime.now()
    since = now - datetime.timedelta(days=_AVAILABILITY_DAYS)
    # M47-22: a period replaces the 90-day window
    start, end = _dates(date_from, date_to)
    if start:
        since = datetime.datetime.combine(start, datetime.time.min) - datetime.timedelta(hours=6)
    if end:
        now = min(
            now, datetime.datetime.combine(end, datetime.time.max) - datetime.timedelta(hours=6)
        )
    outages = _read(
        env,
        "fix.site.outage",
        ["|", ("state", "=", "open"), ("ended_at", ">=", since)],
    )
    tests = _read(env, "fix.site.power.test", [("tested_on", ">=", since.date())])
    labels = dict(env["fix.site.outage"]._fields["service"]._description_selection(env))
    rows = []
    for site in _sites(env).filtered(lambda s: s.state != "closed"):
        mine = outages.filtered(lambda o, sid=site.id: o.site_id.id == sid)
        ongoing = mine.filtered(lambda o: o.state == "open")
        down = sum(mine.mapped("duration_hours")) + sum(
            (now - o.started_at).total_seconds() / 3600.0 for o in ongoing
        )
        lost = sum(mine.mapped("operating_hours_lost")) + sum(
            (now - o.started_at).total_seconds() / 3600.0
            for o in ongoing.filtered("branch_stopped")
        )
        causes = {}
        for o in mine:
            causes[o.service] = causes.get(o.service, 0) + 1
        top = max(causes, key=causes.get) if causes else None
        failed = tests.filtered(lambda t, sid=site.id: t.site_id.id == sid and t.result == "fail")
        rows.append(
            {
                "site": site.name,
                "outages": len(mine),
                "ongoing": len(ongoing),
                "hours_down": round(down, 2),
                "hours_lost": round(lost, 2),
                "top_service": labels.get(top, "—") if top else "—",
                "power_tests_failed": len(failed),
            }
        )
    rows.sort(key=lambda r: (-r["hours_lost"], -r["hours_down"]))
    return _pack(
        "Infrastructure Availability — building-service outages, last %d days" % _AVAILABILITY_DAYS,
        [
            "site",
            "outages",
            "ongoing",
            "hours_down",
            "hours_lost",
            "top_service",
            "power_tests_failed",
        ],
        {
            "site": "Site",
            "outages": "Outages",
            "ongoing": "Ongoing Now",
            "hours_down": "Hours Down",
            "hours_lost": "Branch Operating Hours Lost",
            "top_service": "Most Frequent",
            "power_tests_failed": "Generator / UPS Tests Failed",
        },
        rows,
        [
            "An outage counts when it is ongoing or ended inside the window; an ongoing "
            "one counts up to now. Operating hours lost are the hours of outages that "
            "stopped the branch (the counter or workshop could not operate).",
            "Availability is measured on whether the branch kept working, not on whether a "
            "service visit happened (spec §4).",
        ],
        totals={
            "site": "Total",
            "outages": sum(r["outages"] for r in rows),
            "ongoing": sum(r["ongoing"] for r in rows),
            "hours_down": round(sum(r["hours_down"] for r in rows), 2),
            "hours_lost": round(sum(r["hours_lost"] for r in rows), 2),
            "power_tests_failed": sum(r["power_tests_failed"] for r in rows),
        },
        empty="No sites registered yet.",
    )


# ------------------------------------------------------------------ documents
# A07 ERP audit (2026-11-20) M47-30 / D18: the printable facility documents,
# built like M45's and M46's. Each is a pack with its own filter, so the report
# bar's CSV / Excel / PDF (the company document: letterhead, period, filters,
# notes) prints exactly what is on screen. Each reads only what the caller may
# see (the record rules, as the caller), fenced again to the companies selected
# in the session and the caller's operating units, so the fence also holds for
# a sudo (cron / e-mail) run. Dates and times are Dhaka's.
_NONE = "—"


def _doc_scope(env, model, domain=None):
    Model = env[model]
    company = "company_id" if "company_id" in Model._fields else "site_id.company_id"
    unit = (
        "operating_unit_id" if "operating_unit_id" in Model._fields else "site_id.operating_unit_id"
    )
    fence = [(company, "in", env.companies.ids)]
    if not env.su and "operating_unit_ids" in env.user._fields:
        fence += ["|", (unit, "=", False), (unit, "in", env.user.operating_unit_ids.ids)]
    return Model.search(fence + list(domain or [])).sudo()


def _label(record, field):
    """The display label of a selection value (— when unset)."""
    if not record or not record[field]:
        return _NONE
    return dict(record._fields[field].selection).get(record[field], record[field])


def _dhaka_dt(moment):
    """A UTC datetime as Dhaka's wall-clock time ("YYYY-MM-DD HH:MM")."""
    if not moment:
        return _NONE
    return (moment + datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")


def _choice(options, chosen):
    return chosen if chosen in options else None


def _yes(flag):
    return "Yes" if flag else "No"


def _money(amount):
    return "%.2f" % (amount or 0.0)


def _card(title, rows, notes, filters, empty=None):
    """A one-record document: label / value rows."""
    out = _pack(
        title,
        ["field", "value"],
        {"field": "", "value": ""},
        [{"field": f, "value": v} for f, v in rows],
        notes,
        empty=empty,
    )
    out["filters"] = filters
    return out


def _site_filter(env, sites=None):
    sites = sites if sites is not None else _doc_scope(env, "fix.site")
    return {"key": "site", "label": "Site", "options": ["All", *sorted(set(sites.mapped("name")))]}


def facility_job_sheet(env, date_from=None, date_to=None, work_order=None, **params):
    """FR-FAC-030..035: the job sheet of one facility work order, with its SLA,
    spend approval, permit to work, vendor, cost, completion and verifier."""
    start, end = _dates(date_from, date_to)
    period = [("scheduled_date", ">=", start)] if start else []
    period += [("scheduled_date", "<=", end)] if end else []
    orders = _doc_scope(env, "fix.facility.work.order", period)
    options = [_NONE, *sorted(orders.mapped("name"))[:500]]
    filters = [{"key": "work_order", "label": "Work order", "options": options}]
    name = _choice(options[1:], work_order)
    if not name:
        return _card(
            "Facility Work Order Job Sheet",
            [],
            ["Choose the work order in the filter above (the period narrows the list)."],
            filters,
            empty="Pick a work order in the filter above.",
        )
    o = orders.filtered(lambda x: x.name == name)[:1]
    if not o.restore_due_at:
        sla = "Not triaged yet"
    elif o.state in _WO_DONE:
        sla = "Breached" if o.sla_restore_breached else "Restored within SLA"
    else:
        sla = "Breached (still open)" if o.sla_restore_breached else "Open, within SLA"
    rows = [
        ("Work order", o.name),
        ("Site", o.site_id.name),
        ("Branch / operating unit", o.operating_unit_id.name or o.site_id.branch_id.name or _NONE),
        ("Work type", _label(o, "work_type")),
        ("Priority", _label(o, "priority")),
        ("Asset", o.site_asset_id.display_name or o.equipment_id.display_name or _NONE),
        ("Problem / scope", o.description or _NONE),
        ("Scheduled", str(o.scheduled_date or _NONE)),
        ("Triaged by / on", "%s / %s" % (o.triaged_by_id.name or _NONE, _dhaka_dt(o.triaged_on))),
        ("Response due", _dhaka_dt(o.response_due_at)),
        ("Restore due", _dhaka_dt(o.restore_due_at)),
        ("Restore SLA", sla),
        ("Done by", _label(o, "assigned_type")),
        ("Engineer", o.assigned_to.name or _NONE),
        ("Vendor", o.vendor_id.name or _NONE),
        ("Vendor invoice ref", o.invoice_ref or _NONE),
        ("Estimated cost (BDT)", _money(o.estimated_cost)),
        ("Actual cost (BDT)", _money(o.actual_cost) if o.state in _WO_DONE else "not completed"),
        ("Spend approval", _label(o, "approval_state")),
        (
            "Approved by / on / amount",
            "%s / %s / %s"
            % (
                o.dofa_approved_by.name or _NONE,
                _dhaka_dt(o.dofa_approved_at),
                _money(o.dofa_approved_amount) if o.dofa_approved else _NONE,
            ),
        ),
        (
            "Permit to work",
            "%s: %s, approved by %s, valid to %s"
            % (
                _label(o, "hazard_type"),
                o.permit_precautions or _NONE,
                o.permit_approved_by_id.name or _NONE,
                o.permit_valid_to or _NONE,
            )
            if o.high_risk
            else "Not a high-risk job",
        ),
        (
            "Accepted by / at",
            "%s / %s" % (o.accepted_by_id.name or _NONE, _dhaka_dt(o.accepted_at)),
        ),
        ("Completion evidence", o.completion_notes or _NONE),
        (
            "Completed by / at",
            "%s / %s" % (o.completed_by_id.name or _NONE, _dhaka_dt(o.completed_at)),
        ),
        (
            "Verified by / at",
            "%s / %s" % (o.verified_by_id.name or _NONE, _dhaka_dt(o.verified_at)),
        ),
        ("Verification notes", o.verification_notes or _NONE),
        ("State", _label(o, "state")),
        ("Engineer / vendor signature", ""),
        ("Site in-charge signature", ""),
    ]
    return _card(
        "Facility Work Order Job Sheet — %s" % o.name,
        rows,
        [
            "Restore SLA from triage (D15): emergency 8 h, high 48 h, normal 5 days, "
            "low 15 days. Times are Dhaka time.",
            "The verifier is never the person who completed the job (BRU-FAC-09).",
        ],
        filters,
    )


def site_handover(env, date_from=None, date_to=None, site=None, **params):
    """FR-FAC-005 / BRU-FAC-04/15: the site gate pass and key hand-over: the
    readiness gate an opening site passed, or the recovery checklist a closing
    site settled, with the sign-offs and the key-holders' signatures."""
    start, end = _dates(date_from, date_to)
    sites = _doc_scope(env, "fix.site")
    if start or end:
        sites = sites.filtered(
            lambda s: (s.opened_on and _in(s.opened_on, start, end))
            or any(
                s[f] and _in(_dhaka_day(s[f]), start, end)
                for f in (
                    "status_opsdir_approved_at",
                    "status_cfo_approved_at",
                    "status_ceo_approved_at",
                )
            )
        )
    options = [_NONE, *sorted(set(sites.mapped("name")))[:500]]
    filters = [{"key": "site", "label": "Site", "options": options}]
    name = _choice(options[1:], site)
    if not name:
        return _card(
            "Site Gate Pass & Key Hand-Over",
            [],
            [
                "Choose the site in the filter above (the period lists sites opened or "
                "signed off in it)."
            ],
            filters,
            empty="Pick a site in the filter above.",
        )
    s = sites.filtered(lambda x: x.name == name)[:1]
    leases = _doc_scope(env, "fix.site.lease", [("site_id", "=", s.id)])
    lease = leases.sorted(lambda ln: (ln.state == "active", ln.end_date or datetime.date.min))[-1:]
    closing = s.state == "closed" or s.closure_requested
    rows = [
        ("Site", s.name),
        ("Site type", _label(s, "site_type")),
        ("Branch / operating unit", s.branch_id.name or s.operating_unit_id.name or _NONE),
        ("Address", s.address or _NONE),
        ("State", _label(s, "state")),
        ("Hand-over", "Closing: premises and keys go back" if closing else "Opening: keys taken"),
        ("Key holder (accountable manager)", s.accountable_manager_id.name or _NONE),
        ("Lessor", lease.lessor_id.name or _NONE),
        ("Lease", "%s (%s)" % (lease.name, _label(lease, "state")) if lease else _NONE),
        ("Operational since", str(s.opened_on or _NONE)),
    ]
    if closing:
        rows += [
            ("Assets recovered (M45 / M15 / M46)", _yes(s.closure_assets_recovered)),
            ("Licences surrendered", _yes(s.closure_licences_surrendered)),
            ("Deposit recovered / written off", _yes(s.closure_deposit_settled)),
            ("Lease deposit outcome", _label(lease, "termination_deposit_outcome")),
            ("Recovery notes", s.closure_notes or _NONE),
        ]
    else:
        rows += [
            ("Power connected", _yes(s.ready_power)),
            ("Connectivity live", _yes(s.ready_connectivity)),
            ("Security arrangements in place", _yes(s.ready_security)),
            ("Equipment complement installed (M45)", _yes(s.ready_equipment)),
            ("Signage installed / permitted", _yes(s.ready_signage)),
            ("Readiness evidence", s.readiness_notes or _NONE),
        ]
    rows += [
        (
            "Operations Director",
            "%s / %s"
            % (
                s.status_opsdir_approved_by_id.name or _NONE,
                _dhaka_dt(s.status_opsdir_approved_at),
            ),
        ),
        (
            "CFO",
            "%s / %s"
            % (s.status_cfo_approved_by_id.name or _NONE, _dhaka_dt(s.status_cfo_approved_at)),
        ),
        (
            "CEO",
            "%s / %s"
            % (s.status_ceo_approved_by_id.name or _NONE, _dhaka_dt(s.status_ceo_approved_at)),
        ),
        ("Keys handed over by (signature)", ""),
        ("Keys received by (signature)", ""),
        ("Gate / security (signature)", ""),
    ]
    return _card(
        "Site Gate Pass & Key Hand-Over — %s" % s.name,
        rows,
        [
            "Opening: the keys pass to the accountable manager once the readiness gate is "
            "passed (BRU-FAC-04). Closing: they go back to the lessor once assets are "
            "recovered, licences surrendered and the deposit settled (BRU-FAC-15).",
            "Sign-off times are Dhaka time.",
        ],
        filters,
    )


def _schedule_status(row):
    if row.cancelled:
        return "Cancelled (lease ended)"
    if row.historical:
        return "History (paid outside the system)"
    if row.paid_on:
        return "Paid %s (%s)" % (row.paid_on, _money(row.paid_amount))
    if row.ap_requested_on:
        return "Sent to AP %s" % row.ap_requested_on
    if row.ap_block_reason:
        return "Not sent: %s" % row.ap_block_reason
    return "Not yet due / not sent"


def lease_summary(env, date_from=None, date_to=None, lease=None, **params):
    """FR-FAC-008..012: the lease abstract: terms, the rent schedule of the
    period, the deposit and advance balances and the approvals."""
    start, end = _dates(date_from, date_to)
    leases = _doc_scope(env, "fix.site.lease")
    if start or end:
        leases = leases.filtered(
            lambda ln: (not end or ln.start_date <= end) and (not start or ln.end_date >= start)
        )
    options = [_NONE, *sorted(leases.mapped("name"))[:500]]
    filters = [{"key": "lease", "label": "Lease", "options": options}]
    name = _choice(options[1:], lease)
    cols = ["section", "item", "value"]
    labels = {"section": "Section", "item": "Item", "value": "Value"}
    if not name:
        out = _pack(
            "Lease Summary",
            cols,
            labels,
            [],
            ["Choose the lease in the filter above (the period lists leases running in it)."],
            empty="Pick a lease in the filter above.",
        )
        out["filters"] = filters
        return out
    ln = leases.filtered(lambda x: x.name == name)[:1]
    rows = []

    def add(section, item, value):
        rows.append({"section": section, "item": item, "value": value})

    for item, value in (
        ("Lease", ln.name),
        ("Site", ln.site_id.name),
        ("Lessor", ln.lessor_id.name),
        ("Term", "%s to %s" % (ln.start_date, ln.end_date)),
        ("Payment frequency", _label(ln, "payment_frequency")),
        ("Monthly rent at commencement (BDT)", _money(ln.monthly_rent)),
        ("Current monthly rent (BDT)", _money(ln.current_rent)),
        ("Annual escalation %", "%.2f" % (ln.escalation_pct or 0.0)),
        ("Monthly service charge (BDT)", _money(ln.service_charge)),
        ("Notice period (days)", str(ln.notice_period_days or 0)),
        ("Renewal notice date", str(ln.renewal_notice_date or _NONE)),
        ("Total commitment (BDT)", _money(ln.total_commitment)),
        ("State", _label(ln, "state")),
    ):
        add("Terms", item, value)
    for item, value in (
        ("Security deposit (BDT)", _money(ln.deposit)),
        ("Deposit balance held by the lessor (BDT)", _money(ln.deposit_balance)),
        ("Advance rent paid (BDT)", _money(ln.advance_rent_amount)),
        ("Advance adjusted per month (BDT)", _money(ln.advance_adjust_monthly)),
        ("Advance balance still to adjust (BDT)", _money(ln.advance_balance)),
    ):
        add("Deposit & advance", item, value)
    for item, value in (
        ("Approval", _label(ln, "approval_state")),
        (
            "Approved by / on",
            "%s / %s" % (ln.dofa_approved_by.name or _NONE, _dhaka_dt(ln.dofa_approved_at)),
        ),
        (
            "Approved tier / amount",
            "%s / %s"
            % (
                _label(ln, "dofa_approved_tier"),
                _money(ln.dofa_approved_amount) if ln.dofa_approved else _NONE,
            ),
        ),
        (
            "Renewal decision",
            "%s (%s, %s)"
            % (
                _label(ln, "renewal_decision"),
                ln.renewal_decision_by_id.name or _NONE,
                ln.renewal_decision_on or _NONE,
            ),
        ),
        (
            "Termination",
            "%s effective %s, penalty %s, deposit %s"
            % (
                ln.terminated_reason or ln.termination_proposed_reason or "none",
                ln.termination_effective_date or _NONE,
                _money(ln.termination_penalty),
                _label(ln, "termination_deposit_outcome"),
            )
            if (ln.termination_requested or ln.state == "terminated")
            else "None",
        ),
    ):
        add("Approvals", item, value)
    schedule = ln.schedule_ids.filtered(
        lambda r: _in(r.due_date, start, end) if (start or end) else True
    )
    for r in schedule.sorted(lambda r: (r.due_date, r.id)):
        add(
            "Rent schedule",
            "%s (due %s)" % (r.period, r.due_date),
            "rent %s + service %s - advance %s = payable %s; %s"
            % (
                _money(r.rent_due),
                _money(r.service_charge_due),
                _money(r.advance_adjusted),
                _money(r.amount_payable),
                _schedule_status(r),
            ),
        )
    payable = sum(
        schedule.filtered(lambda r: not r.cancelled and not r.historical).mapped("amount_payable")
    )
    out = _pack(
        "Lease Summary — %s" % ln.name,
        cols,
        labels,
        rows,
        [
            _period_label(start, end),
            "Payable in the schedule shown (history and cancelled rows excluded): BDT %s."
            % _money(payable),
            "Deposit balance = deposits paid less refunds and write-offs (Deposits & Site "
            "Charges); advance balance = advance rent not yet adjusted against the rent.",
        ],
    )
    out["filters"] = filters
    return out


def _period_label(start, end):
    if not (start or end):
        return "Whole term."
    return "Rent schedule from %s to %s." % (start or "…", end or "…")


def _type_filter(model_field_selection, key, label):
    return {
        "key": key,
        "label": label,
        "options": ["All", *[lab for _v, lab in model_field_selection]],
    }


def _type_value(selection, chosen):
    for value, lab in selection:
        if chosen in (value, lab):
            return value
    return None


def licence_register(env, date_from=None, date_to=None, site=None, licence_type=None, **params):
    """FR-FAC-015..018 / BRU-FAC-01: the licence register: number, authority,
    expiry, fee and the latest renewal, per site."""
    today = _today(env)
    start, end = _dates(date_from, date_to)
    Licence = env["fix.site.licence"]
    selection = Licence._fields["licence_type"]._description_selection(env)
    sites = _doc_scope(env, "fix.site")
    filters = [
        _site_filter(env, sites),
        _type_filter(selection, "licence_type", "Licence type"),
    ]
    domain = [("valid_to", ">=", start)] if start else []
    domain += [("valid_to", "<=", end)] if end else []
    if site and site != "All":
        domain.append(("site_id.name", "=", site))
    ltype = _type_value(selection, licence_type)
    if ltype:
        domain.append(("licence_type", "=", ltype))
    rows = []
    for ln in _doc_scope(env, "fix.site.licence", domain).sorted(
        lambda x: (x.site_id.name or "", x.valid_to or datetime.date.max, x.id)
    ):
        renewal = (
            ln.renewal_ids.sorted(lambda r: r.id)[-1:] if "renewal_ids" in ln._fields else None
        )
        rows.append(
            {
                "licence": ln.name,
                "site": ln.site_id.name,
                "type": _licence_type_label(env, ln.licence_type),
                "number": ln.number or _NONE,
                "authority": ln.authority or _NONE,
                "issued": str(ln.issued_on) if ln.issued_on else _NONE,
                "valid_to": str(ln.valid_to) if ln.valid_to else _NONE,
                "days_left": (ln.valid_to - today).days if ln.valid_to else _NONE,
                "fee": round(ln.fee or 0.0, 2),
                "responsible": ln.responsible_id.name or _NONE,
                "renewal": "%s (%s)" % (renewal.name, _label(renewal, "state"))
                if renewal
                else _NONE,
                "renewal_cost": round(renewal.total_cost or 0.0, 2) if renewal else 0.0,
                "state": _label(ln, "state"),
                "basis": _licence_basis(ln, today),
            }
        )
    out = _pack(
        "Licence Register",
        [
            "licence",
            "site",
            "type",
            "number",
            "authority",
            "issued",
            "valid_to",
            "days_left",
            "fee",
            "responsible",
            "renewal",
            "renewal_cost",
            "state",
            "basis",
        ],
        {
            "licence": "Licence",
            "site": "Site",
            "type": "Type",
            "number": "Number",
            "authority": "Issuing Authority",
            "issued": "Issued",
            "valid_to": "Expires",
            "days_left": "Days Left",
            "fee": "Fee (BDT)",
            "responsible": "Responsible",
            "renewal": "Latest Renewal",
            "renewal_cost": "Renewal Cost (BDT)",
            "state": "State",
            "basis": "Valid Today?",
        },
        rows,
        [
            "The period filters on the expiry date. Days left are counted from today in "
            "Dhaka; a licence with no expiry is not treated as valid (AC-21)."
        ],
        totals={
            "licence": "Total",
            "fee": round(sum(r["fee"] for r in rows), 2),
            "renewal_cost": round(sum(r["renewal_cost"] for r in rows), 2),
        },
        empty="No licence matches the filter.",
    )
    out["filters"] = filters
    return out


def utility_bill_register(
    env, date_from=None, date_to=None, site=None, utility_type=None, **params
):
    """FR-FAC-019..021: every utility bill of the period, with its account, the
    anomaly review and where it stands with accounts payable."""
    start, end = _dates(date_from, date_to)
    first = start.strftime("%Y-%m") if start else "0000-00"
    last = end.strftime("%Y-%m") if end else "9999-99"
    Utility = env["fix.site.utility"]
    selection = Utility._fields["utility_type"]._description_selection(env)
    filters = [_site_filter(env), _type_filter(selection, "utility_type", "Utility")]
    domain = [("period", ">=", first), ("period", "<=", last)]
    if site and site != "All":
        domain.append(("site_id.name", "=", site))
    utype = _type_value(selection, utility_type)
    if utype:
        domain.append(("utility_type", "=", utype))
    rows = []
    for u in _doc_scope(env, "fix.site.utility", domain).sorted(
        lambda x: (x.site_id.name or "", x.period or "", x.id)
    ):
        account = u.account_id if "account_id" in u._fields else None
        rows.append(
            {
                "bill": u.name,
                "site": u.site_id.name,
                "period": u.period,
                "type": _label(u, "utility_type"),
                "account_no": (account.account_no if account else None) or _NONE,
                "provider": (account.provider_id.name if account else None) or _NONE,
                "meter": (account.meter_no if account else None) or _NONE,
                "usage": round(u.usage or 0.0, 2),
                "unit": u.unit or _NONE,
                "amount": round(u.amount or 0.0, 2),
                "review": _label(u, "review_state") + (" (flagged)" if u.flagged else ""),
                "sent_to_ap": str(u.ap_requested_on)
                if u.ap_requested_on
                else (u.ap_block_reason or _NONE),
                "invoice_ref": u.invoice_ref or _NONE,
                "paid": round(u.paid_amount or 0.0, 2),
                "paid_on": str(u.paid_on) if u.paid_on else _NONE,
            }
        )
    cols = [
        "bill",
        "site",
        "period",
        "type",
        "account_no",
        "provider",
        "meter",
        "usage",
        "unit",
        "amount",
        "review",
        "sent_to_ap",
        "invoice_ref",
        "paid",
        "paid_on",
    ]
    out = _pack(
        "Utility Bill Register",
        cols,
        {
            "bill": "Bill",
            "site": "Site",
            "period": "Period",
            "type": "Utility",
            "account_no": "Account No.",
            "provider": "Provider",
            "meter": "Meter",
            "usage": "Usage",
            "unit": "Unit",
            "amount": "Amount (BDT)",
            "review": "Anomaly Review",
            "sent_to_ap": "Sent to AP / Why Not",
            "invoice_ref": "Invoice Ref",
            "paid": "Paid (BDT)",
            "paid_on": "Paid On",
        },
        rows,
        [
            "The period filters on the billing month. A flagged bill is held from payment "
            "until a Branch Operations Lead who did not record it releases it."
        ],
        totals={
            "bill": "Total",
            "amount": round(sum(r["amount"] for r in rows), 2),
            "paid": round(sum(r["paid"] for r in rows), 2),
        },
        empty="No utility bill matches the filter.",
    )
    out["filters"] = filters
    return out


def outage_report(env, date_from=None, date_to=None, site=None, service=None, **params):
    """FR-FAC-027 / AUT-FAC-12: every infrastructure outage of the period, how
    long it lasted, the branch hours lost and the orders it stopped."""
    start, end = _dates(date_from, date_to)
    Outage = env["fix.site.outage"]
    selection = Outage._fields["service"]._description_selection(env)
    filters = [_site_filter(env), _type_filter(selection, "service", "Service lost")]
    domain = []
    if site and site != "All":
        domain.append(("site_id.name", "=", site))
    svc = _type_value(selection, service)
    if svc:
        domain.append(("service", "=", svc))
    outages = _doc_scope(env, "fix.site.outage", domain).filtered(
        lambda o: _in(_dhaka_day(o.started_at), start, end) if (start or end) else True
    )
    rows = []
    for o in outages.sorted(lambda x: (x.started_at, x.id), reverse=True):
        impacts = o.impact_ids if "impact_ids" in o._fields else []
        rows.append(
            {
                "outage": o.name,
                "site": o.site_id.name,
                "service": _label(o, "service"),
                "asset": o.asset_id.display_name or _NONE,
                "started": _dhaka_dt(o.started_at),
                "ended": _dhaka_dt(o.ended_at) if o.ended_at else "Ongoing",
                "hours": round(o.duration_hours or 0.0, 2),
                "hours_lost": round(o.operating_hours_lost or 0.0, 2),
                "stopped": _yes(o.branch_stopped),
                "cause": (o.cause or _NONE)[:160],
                "workaround": o.workaround or _NONE,
                "work_order": o.work_order_id.name or _NONE,
                "orders": len(impacts),
                "recorded_by": o.recorded_by_id.name or _NONE,
                "ended_by": o.ended_by_id.name or _NONE,
            }
        )
    out = _pack(
        "Infrastructure Outage Report",
        [
            "outage",
            "site",
            "service",
            "asset",
            "started",
            "ended",
            "hours",
            "hours_lost",
            "stopped",
            "cause",
            "workaround",
            "work_order",
            "orders",
            "recorded_by",
            "ended_by",
        ],
        {
            "outage": "Outage",
            "site": "Site",
            "service": "Service Lost",
            "asset": "Asset That Failed",
            "started": "Started (Dhaka)",
            "ended": "Ended (Dhaka)",
            "hours": "Duration (h)",
            "hours_lost": "Operating Hours Lost",
            "stopped": "Branch Stopped",
            "cause": "Cause",
            "workaround": "Workaround",
            "work_order": "Repair Work Order",
            "orders": "Orders Affected",
            "recorded_by": "Recorded By",
            "ended_by": "Ended By",
        },
        rows,
        [
            "The period filters on the Dhaka date the outage started. Operating hours lost "
            "count only while the branch could not operate, within its opening hours; the "
            "affected orders' SLA clocks are not charged for that window."
        ],
        totals={
            "outage": "Total",
            "hours": round(sum(r["hours"] for r in rows), 2),
            "hours_lost": round(sum(r["hours_lost"] for r in rows), 2),
            "orders": sum(r["orders"] for r in rows),
        },
        empty="No outage matches the filter.",
    )
    out["filters"] = filters
    return out


REPORTS = {
    "infrastructure_availability": infrastructure_availability,
    "critical_dates": critical_dates,
    "branch_assets": branch_assets,
    "cost_per_site": cost_per_site,
    "lease_expiry": lease_expiry,
    "licence_compliance": licence_compliance,
    "utilities_variance": utilities_variance,
    "work_order_performance": work_order_performance,
    # A07 ERP audit M47-30: the printable facility documents
    "facility_job_sheet": facility_job_sheet,
    "site_handover": site_handover,
    "lease_summary": lease_summary,
    "licence_register": licence_register,
    "utility_bill_register": utility_bill_register,
    "outage_report": outage_report,
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
        # A07 ERP audit (2026-11-20) M47-07: rent fallen due that is not with AP
        "rent_due_not_sent": len(
            _read(
                env,
                "fix.site.lease.schedule",
                env["fix.site.lease.schedule"]._schedule_due_domain(today),
            )
        ),
        # D6: leases awaiting the approval of their commitment
        "leases_awaiting_approval": len(_read(env, "fix.site.lease", [("state", "=", "draft")])),
        # M47-16: open jobs whose response or restore clock has run out
        "wo_sla_breached": len(
            orders.filtered(
                lambda o: o.state in ("draft", "scheduled", "in_progress")
                and (o.sla_response_breached or o.sla_restore_breached)
            )
        ),
    }
