# A07 · M17 Device & Asset Registry — surfaces, packs and KPIs over the device
# master, warranties, ownership, history and the new estates, PM, condition,
# identity, custody and component models. Warranty is declared by M01's surface
# and read through the merge (single-owner rule).
import datetime

from odoo import fields
from odoo.addons.cd_device_registry.models.fix_device import (
    CUSTODY_EVIDENCE_TYPES,
    TRANSFER_EVIDENCE_TYPES,
)

from ..p03_service_order_api import _company_domain


def _evidence_picker(types):
    """Evidence of these types that is unfiled or already about a device. The
    server decides the rest: filed on this device, and not used before."""
    return [
        ("document_type", "in", list(types)),
        "|",
        ("res_model", "=", False),
        ("res_model", "=", "fix.device"),
    ]


# A07 operability (2026-11-07) M17-6: every list here read as superuser with at
# best a company fence, so any internal user listed every unit's owners, IMEIs and
# custody. "rules" reads as the caller: the company and operating-unit rules of
# the device, and of each row through its device, decide.
SURFACES = {
    "fix.device": {
        "order": "id desc",
        "limit": 400,
        "rules": True,
        "pickers": {"transfer_evidence_document_id": _evidence_picker(TRANSFER_EVIDENCE_TYPES)},
        # A07 audit M17-8: the lifecycle moves only through these. Scrap is a
        # routed M63 decision (Device Quality Manager, never the requester);
        # here it is only requested. A Branch Manager other than the flagger
        # clears a lost flag. A07 P1 (2026-11-04): the governed ownership
        # transfer (agent, reason, evidence staged on the form), the
        # provisional identity confirmation and the lifecycle decisions.
        "actions": {
            "action_mark_lost",
            "action_clear_lost",
            "action_request_approval",
            "action_recall_approval",
            "action_transfer_ownership",
            "action_correct_identifier",
            "action_confirm_identity",
            # M17 capture pass 2, FR-AST-002: the Add Identifier form
            "action_add_identifier",
            "action_set_vintage",
            "action_set_end_of_support",
            "action_set_obsolete",
            "action_return_to_active",
        },
    },
    # fix.device.history is declared by M01 — read through the merge.
    "fix.device.ownership": {
        "order": "transfer_date desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": set(),
    },
    "fix.device.estate": {"order": "name", "limit": 200, "rules": True, "actions": set()},
    "fix.device.pm": {
        "order": "next_due",
        "limit": 300,
        "rules": True,
        "actions": {"action_complete", "action_reschedule", "action_pause", "action_resume"},
    },
    "fix.device.condition": {
        "order": "graded_on desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": {"action_confirm"},
    },
    "fix.device.identity": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "rules": True,
        # A07 audit M17-3: the merge is decided from the M63 approval inbox by a
        # Tier 2 holder who neither raised nor requested it; here it is only
        # routed. action_merge is the engine's apply method, not a button.
        "actions": {"action_request_approval", "action_recall_approval", "action_reject"},
    },
    "fix.device.custody": {
        "order": "event_date desc, id desc",
        "limit": 400,
        "rules": True,
        "pickers": {
            "evidence_document_id": _evidence_picker(CUSTODY_EVIDENCE_TYPES),
            "condition_id": [("state", "=", "confirmed")],
        },
        "actions": set(),
    },
    "fix.device.component": {
        "order": "installed_on desc, id desc",
        "limit": 400,
        "rules": True,
        "actions": {
            "action_remove",
            "action_record_disposition",
            "action_dispose_returned",
            "action_dispose_scrapped",
            "action_dispose_harvested",
            "action_dispose_returned_to_brand",
        },
    },
    # A07 P2 (2026-11-04): the identifier history (read-only; a Branch Manager
    # records the NEIR result of an IMEI) and the merge lineage (a Device
    # Quality Manager reverses a merge inside its window).
    "fix.device.identifier": {
        "order": "device_id, identifier_type, captured_at desc, id desc",
        "limit": 400,
        "rules": True,
        "actions": {"action_neir_registered", "action_neir_deregistered", "action_neir_blocked"},
    },
    "fix.device.merge": {
        "order": "merged_at desc, id desc",
        "limit": 200,
        "rules": True,
        "actions": {"action_reverse"},
    },
    "fix.device.part.compatibility": {
        "order": "id desc",
        "limit": 400,
        "rules": True,
        "actions": set(),
    },
    # A07 operability (2026-11-07) BRU-AST-09: the hold M17's lost/stolen flag puts
    # on each open M01 order. Only the event consumers write it; a person reads it.
    "fix.service.order.device.hold": {
        "order": "state, id desc",
        "limit": 300,
        "rules": True,
        "actions": set(),
    },
    # M17 capture audit (2026-11-13), FR-AST-039 / BRU-AST-18: an estate is
    # registered from a file. Uploading validates it; Commit as a Set (Device
    # Registry Agent) registers every row or none. The lines are the reject
    # report, written only by the validation.
    "fix.device.bulk.load": {
        "order": "id desc",
        "limit": 200,
        "rules": True,
        "actions": {"action_validate", "action_commit"},
    },
    "fix.device.bulk.line": {
        "order": "load_id desc, row_no",
        "limit": 2000,
        "rules": True,
        "actions": set(),
    },
    # M17 capture pass 2 (2026-11-19): the records the spec places on pages
    # 1, 2, 3, 8, 10 and 11 that no model held. Users create them; the
    # registry writes their states, closures and the device fields they move.
    "fix.device.label": {
        "order": "applied_on desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": set(),
    },
    "fix.device.accessory": {
        "order": "state, received_on desc, id desc",
        "limit": 400,
        "rules": True,
        "actions": {"action_return", "action_report_missing"},
    },
    "fix.device.configuration": {
        "order": "device_id, attribute, effective_from desc, id desc",
        "limit": 400,
        "rules": True,
        "actions": set(),
    },
    "fix.device.population.change": {
        "order": "recorded_at desc, id desc",
        "limit": 300,
        "rules": True,
        "actions": set(),
    },
    "fix.device.estate.node": {
        "order": "estate_id, complete_name, id",
        "limit": 400,
        "rules": True,
        "actions": set(),
    },
    "fix.device.estate.placement": {
        "order": "placed_from desc, id desc",
        "limit": 400,
        "rules": True,
        "actions": set(),
    },
    "fix.device.eol.decision": {
        "order": "id desc",
        "limit": 200,
        "rules": True,
        # a Branch Manager who neither raised nor requested it decides it
        "actions": {"action_request", "action_approve", "action_reject"},
    },
    "fix.device.quality.issue": {
        "order": "escalated desc, severity_rank, raised_at, id",
        "limit": 400,
        "rules": True,
        "actions": {"action_start", "action_resolve"},
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


def _visible_device_ids(env):
    """The devices the caller may open: their own record rules decide
    (company AND operating unit). Superuser reads see every device."""
    return env["fix.device"].search([]).ids


def _scoped(env, model, domain=None):
    """sudo() read for a report or KPI, fenced to what the caller may see.

    A07 audit (2026-11-03) M17-6: every pack read `sudo().search([])`, so a
    user of one company saw another company's devices, owners and IMEIs.
    A07 P1 (2026-11-04): the company fence still let an OU2 clerk read an OU1
    customer's device and owner in Asset 360 and count it in the KPIs. Device
    rows and satellite rows now follow the devices the caller's own record
    rules let him open; other models keep the company fence."""
    Model = env[model].sudo()
    if model == "fix.device":
        fence = [("id", "in", _visible_device_ids(env))]
    elif "device_id" in Model._fields:
        fence = [("device_id", "in", _visible_device_ids(env))]
    else:
        fence = _company_domain(env, model)
    return Model.search(list(domain or []) + fence)


def _devices(env):
    return _scoped(env, "fix.device")


def _history(env):
    return _scoped(env, "fix.device.history")


def asset_360(env, date_from=None, date_to=None, **params):
    warranties = _scoped(env, "fix.warranty")
    history = _history(env)
    custody = _scoped(env, "fix.device.custody")
    # single-pass counts: 691 devices × 3,000 events must not be O(N×M)
    w_counts, w_active, h_counts, last_custody = {}, {}, {}, {}
    today = fields.Date.context_today(env.user)
    for warranty in warranties:
        dev_id = warranty.device_id.id
        w_counts[dev_id] = w_counts.get(dev_id, 0) + 1
        if (
            warranty.status == "active"
            and warranty.start_date
            and warranty.end_date
            and warranty.start_date <= today <= warranty.end_date
        ):
            w_active[dev_id] = w_active.get(dev_id, 0) + 1
    for event in history:
        h_counts[event.device_id.id] = h_counts.get(event.device_id.id, 0) + 1
    for event in custody.sorted("event_date"):
        last_custody[event.device_id.id] = event.event
    rows = []
    for device in _devices(env):
        rows.append(
            {
                "device": device.name,
                "serial": device.serial_number or "—",
                "model": device.device_model_id.name if device.device_model_id else "—",
                "owner": device.owner_id.name if device.owner_id else "—",
                "state": dict(device._fields["state"].selection).get(device.state),
                "warranties": w_counts.get(device.id, 0),
                "warranty_active": w_active.get(device.id, 0),
                "history": h_counts.get(device.id, 0),
                "last_custody": dict(env["fix.device.custody"]._fields["event"].selection).get(
                    last_custody.get(device.id)
                )
                if last_custody.get(device.id)
                else "—",
                "estate": device.estate_id.name if device.estate_id else "—",
            }
        )
    rows.sort(key=lambda r: str(r["device"]), reverse=True)
    total = len(rows)
    rows = rows[:300]
    return _pack(
        "Asset 360 — one row per device with warranty, history and custody",
        [
            "device",
            "serial",
            "model",
            "owner",
            "state",
            "warranties",
            "warranty_active",
            "history",
            "last_custody",
            "estate",
        ],
        {
            "device": "Device",
            "serial": "Serial",
            "model": "Model",
            "owner": "Owner",
            "state": "State",
            "warranties": "Warranties",
            "warranty_active": "Active",
            "history": "History",
            "last_custody": "Last Custody",
            "estate": "Estate",
        },
        rows,
        [
            "Counts are single-pass aggregates over the warranty, history and custody "
            "records. Showing %d of %d devices, sorted by device name." % (len(rows), total)
        ],
        empty="No devices registered yet.",
    )


def identifiers(env, date_from=None, date_to=None, **params):
    rows = []
    for device in _devices(env):
        present = [
            bool(device.serial_number),
            bool(device.imei_1),
            bool(device.imei_2),
            bool(device.mac_address),
            bool(device.legacy_reference),
        ]
        rows.append(
            {
                "device": device.name,
                "serial": device.serial_number or "—",
                "imei_1": device.imei_1 or "—",
                "imei_2": device.imei_2 or "—",
                "mac": device.mac_address or "—",
                "legacy": device.legacy_reference or "—",
                "identifiers_present": sum(present),
                "missing": 5 - sum(present),
            }
        )
    rows.sort(key=lambda r: -r["missing"])
    return _pack(
        "Multi-Identifier Model — five identifiers per device",
        ["device", "serial", "imei_1", "imei_2", "mac", "legacy", "identifiers_present", "missing"],
        {
            "device": "Device",
            "serial": "Serial",
            "imei_1": "IMEI 1",
            "imei_2": "IMEI 2",
            "mac": "MAC",
            "legacy": "Legacy Ref",
            "identifiers_present": "Present",
            "missing": "Missing",
        },
        rows,
        [
            "Missing counts the identifiers a device could carry but does not "
            "(desktop devices legitimately have no IMEI) — read it per device type."
        ],
        totals={
            "device": "Total",
            "identifiers_present": sum(r["identifiers_present"] for r in rows),
            "missing": sum(r["missing"] for r in rows),
        },
        empty="No devices registered yet.",
    )


def parts_genealogy(env, date_from=None, date_to=None, **params):
    rows = []
    for component in _scoped(env, "fix.device.component"):
        rows.append(
            {
                "device": component.device_id.name,
                "part": component.part_name,
                "serial": component.serial_no or "—",
                "installed_on": str(component.installed_on),
                "removed_on": str(component.removed_on) if component.removed_on else "—",
                "source": component.source_ref or "—",
                "state": dict(component._fields["state"].selection).get(component.state),
            }
        )
    rows.sort(key=lambda r: r["installed_on"], reverse=True)
    return _pack(
        "Parts Genealogy — installed and removed components per device",
        ["device", "part", "serial", "installed_on", "removed_on", "source", "state"],
        {
            "device": "Device",
            "part": "Component",
            "serial": "Serial",
            "installed_on": "Installed",
            "removed_on": "Removed",
            "source": "Source Order",
            "state": "State",
        },
        rows,
        [
            "A component row records the installation; removal is an explicit action "
            "with its own date."
        ],
        empty="No installed components recorded yet.",
    )


def repeat_fault(env, date_from=None, date_to=None, **params):
    events_by_device, last_event = {}, {}
    for event in _history(env).filtered(
        lambda h: h.event_type in ("service_order", "repair", "qc")
    ):
        dev_id = event.device_id.id
        events_by_device[dev_id] = events_by_device.get(dev_id, 0) + 1
        if event.date and (dev_id not in last_event or event.date > last_event[dev_id]):
            last_event[dev_id] = event.date
    rows = []
    for device in _devices(env):
        count = events_by_device.get(device.id, 0)
        if count < 2:
            continue
        rows.append(
            {
                "device": device.name,
                "model": device.device_model_id.name if device.device_model_id else "—",
                "owner": device.owner_id.name if device.owner_id else "—",
                "events": count,
                "last_event": str(last_event.get(device.id) or "—")[:16],
                "state": dict(device._fields["state"].selection).get(device.state),
            }
        )
    rows.sort(key=lambda r: -r["events"])
    return _pack(
        "Repeat-Fault Pareto — devices with two or more service/repair events",
        ["device", "model", "owner", "events", "last_event", "state"],
        {
            "device": "Device",
            "model": "Model",
            "owner": "Owner",
            "events": "Events",
            "last_event": "Last Event",
            "state": "State",
        },
        rows,
        [
            "Counts service-order, repair and QC history events in a single pass; two "
            "or more is a repeat. This is a frequency view, not a root-cause claim."
        ],
        totals={"device": "Total", "events": sum(r["events"] for r in rows)},
        empty="No device has two or more service events.",
    )


def installed_base(env, date_from=None, date_to=None, **params):
    buckets = {}
    for device in _devices(env):
        model = device.device_model_id.name if device.device_model_id else "Unassigned model"
        brand = (
            device.device_model_id.brand_id.name
            if device.device_model_id and device.device_model_id.brand_id
            else "Unassigned brand"
        )
        key = (brand, model)
        row = buckets.setdefault(key, {"brand": brand, "model": model, "devices": 0, "active": 0})
        row["devices"] += 1
        if device.active:
            row["active"] += 1
    rows = sorted(buckets.values(), key=lambda r: -r["devices"])
    return _pack(
        "Installed Base by Brand/Model",
        ["brand", "model", "devices", "active"],
        {"brand": "Brand", "model": "Model", "devices": "Devices", "active": "Active"},
        rows,
        ["Every registered device counts once under its model's brand."],
        totals={
            "brand": "Total",
            "devices": sum(r["devices"] for r in rows),
            "active": sum(r["active"] for r in rows),
        },
        empty="No devices registered yet.",
    )


def estate_coverage(env, date_from=None, date_to=None, **params):
    devices = _devices(env)
    estates = _scoped(env, "fix.device.estate")
    rows = []
    for estate in estates:
        linked = devices.filtered(lambda d, e=estate: d.estate_id.id == e.id)
        rows.append(
            {
                "estate": estate.name,
                "client": estate.client_id.name,
                "site": estate.site or "—",
                "manager": estate.manager_id.name if estate.manager_id else "—",
                "devices": len(linked),
            }
        )
    unassigned = devices.filtered(lambda d: not d.estate_id)
    rows.append(
        {
            "estate": "— No estate —",
            "client": "—",
            "site": "—",
            "manager": "—",
            "devices": len(unassigned),
        }
    )
    rows.sort(key=lambda r: -r["devices"])
    covered = len(devices) - len(unassigned)
    return _pack(
        "Estate Coverage by Client — devices per estate",
        ["estate", "client", "site", "manager", "devices"],
        {
            "estate": "Estate",
            "client": "Client",
            "site": "Site",
            "manager": "Manager",
            "devices": "Devices",
        },
        rows,
        [
            "%d of %d devices sit in a corporate estate; the rest are listed "
            "explicitly rather than hidden." % (covered, len(devices))
        ],
        totals={"estate": "Total", "devices": sum(r["devices"] for r in rows)},
        empty="No devices registered yet.",
    )


def _custody_assessment(event):
    """What a lost or found event means now: the device's state decides, because
    only a Branch Manager's clearance ends a lost flag (BRU-AST-09)."""
    if event.device_id.state != "lost":
        return "flag cleared"
    return "open: flagged lost" if event.event == "lost" else "recovered: flag not yet cleared"


def custody_exceptions(env, date_from=None, date_to=None, **params):
    custody = _scoped(env, "fix.device.custody")
    labels = dict(env["fix.device.custody"]._fields["event"].selection)
    rows = []
    for event in custody.filtered(lambda c: c.event in ("lost", "found")):
        rows.append(
            {
                "device": event.device_id.name,
                "reference": event.name,
                "event": labels.get(event.event),
                "from": event.from_party_id.name if event.from_party_id else "—",
                "to": event.to_party_id.name if event.to_party_id else "—",
                "date": str(event.event_date),
                "note": _custody_assessment(event),
            }
        )
    # A device flagged before the registry wrote its flag into the chain.
    charted = set(custody.filtered(lambda c: c.event == "lost").device_id.ids)
    for device in _scoped(env, "fix.device", [("state", "=", "lost")]):
        if device.id not in charted:
            rows.append(
                {
                    "device": device.name,
                    "reference": "Registry flag",
                    "event": labels["lost"],
                    "from": "—",
                    "to": "—",
                    "date": str(fields.Date.to_date(device.lost_flagged_at) or "—"),
                    "note": "open: flagged lost",
                }
            )
    rows.sort(key=lambda r: r["date"], reverse=True)
    return _pack(
        "Custody Exceptions — lost devices and recoveries",
        ["device", "reference", "event", "from", "to", "date", "note"],
        {
            "device": "Device",
            "reference": "Event",
            "event": "Kind",
            "from": "From",
            "to": "To",
            "date": "Date",
            "note": "Assessment",
        },
        rows,
        [
            "The assessment reads the device: it stays open until a Branch Manager clears the "
            "lost flag, even after a Recovered event."
        ],
        empty="No custody exceptions recorded.",
    )


def data_quality(env, date_from=None, date_to=None, **params):
    conditions = _scoped(env, "fix.device.condition", [("state", "=", "confirmed")])
    conditioned = set(conditions.mapped("device_id").ids)
    rows = []
    for device in _devices(env):
        problems = []
        if not device.serial_number:
            problems.append("no serial")
        if not device.device_model_id:
            problems.append("no model")
        if not device.owner_id:
            problems.append("no owner")
        # An estate is a corporate customer's structure (FR-AST-038): an individual
        # has none to be in.
        if not device.estate_id and device.owner_id.commercial_partner_id.is_company:
            problems.append("no estate")
        if device.id not in conditioned:
            problems.append("no condition grade")
        score = max(100 - len(problems) * 20, 0)
        rows.append(
            {
                "device": device.name,
                "model": device.device_model_id.name if device.device_model_id else "—",
                "issues": len(problems),
                "problems": ", ".join(problems) or "—",
                "score_pct": score,
            }
        )
    rows.sort(key=lambda r: r["score_pct"])
    average = round(sum(r["score_pct"] for r in rows) / len(rows), 1) if rows else 0.0
    return _pack(
        "Data Quality Scorecard — completeness per device",
        ["device", "model", "issues", "problems", "score_pct"],
        {
            "device": "Device",
            "model": "Model",
            "issues": "Issues",
            "problems": "Problems",
            "score_pct": "Score %",
        },
        rows,
        [
            "Score = 100 − 20 per missing element (serial, model, owner, confirmed condition, "
            "and an estate for a corporate owner); average %.1f%%." % average
        ],
        empty="No devices registered yet.",
    )


def bulk_registration(env, date_from=None, date_to=None, **params):
    conditions = _scoped(env, "fix.device.condition", [("state", "=", "confirmed")])
    conditioned = set(conditions.mapped("device_id").ids)
    rows = []
    for device in _devices(env):
        missing = []
        if not device.estate_id:
            missing.append("estate")
        if device.id not in conditioned:
            missing.append("condition")
        rows.append(
            {
                "device": device.name,
                "serial": device.serial_number or "—",
                "model": device.device_model_id.name if device.device_model_id else "—",
                "estate": device.estate_id.name if device.estate_id else "—",
                "missing": ", ".join(missing) or "—",
                "ready": not missing,
            }
        )
    rows.sort(key=lambda r: (r["ready"], str(r["device"])))
    ready = len([r for r in rows if r["ready"]])
    return _pack(
        "Bulk Registration — estate and condition readiness",
        ["device", "serial", "model", "estate", "missing", "ready"],
        {
            "device": "Device",
            "serial": "Serial",
            "model": "Model",
            "estate": "Estate",
            "missing": "Missing",
            "ready": "Bulk-ready",
        },
        rows,
        [
            "A device is bulk-ready when it has an estate and a confirmed condition "
            "grade: %d of %d." % (ready, len(rows))
        ],
        empty="No devices registered yet.",
    )


REPORTS = {
    "asset_360": asset_360,
    "bulk_registration": bulk_registration,
    "identifiers": identifiers,
    "parts_genealogy": parts_genealogy,
    "repeat_fault": repeat_fault,
    "installed_base": installed_base,
    "estate_coverage": estate_coverage,
    "custody_exceptions": custody_exceptions,
    "data_quality": data_quality,
}


def kpis(env):
    devices = _devices(env)
    # The business date (Dhaka), not the server machine's: the A04 date-basis rule.
    today = fields.Date.context_today(env.user)
    horizon = today + datetime.timedelta(days=30)
    pms = _scoped(env, "fix.device.pm", [("state", "=", "active")])
    conditions = _scoped(env, "fix.device.condition", [("state", "=", "confirmed")])
    # Cover running today, not every row still marked `active`: 53 such rows had
    # all ended by 1 Oct 2026, so the KPI read 53 against a true 0 (M17-5).
    warranties = _scoped(
        env,
        "fix.warranty",
        [("status", "=", "active"), ("start_date", "<=", today), ("end_date", ">=", today)],
    )
    return {
        "devices_active": len(devices.filtered(lambda d: d.active)),
        "estates": len(_scoped(env, "fix.device.estate")),
        "pm_due_30d": len(pms.filtered(lambda p: p.next_due and p.next_due <= horizon)),
        # The device's state: custody rows alone missed a registry flag and
        # read a cleared flag as still lost (A07 operability M17-12).
        "custody_open_lost": len(devices.filtered(lambda d: d.state == "lost")),
        "without_condition": len(devices) - len(set(conditions.mapped("device_id").ids)),
        "warranty_active": len(warranties),
    }
