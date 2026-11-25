# A05 · M18 E-Waste & Circular Economy — surfaces, packs and KPIs over the
# collection/ESG models and the event, triage, batch, battery, partner,
# certificate, statutory-return, manifest, Basel PIC, DoE registration and
# settlement models.
#
# A05 workflow audit (2026-11-03) M18-11 / E2: every report and KPI read with
# sudo().search([]), so a clerk's figures counted every company. Each read is
# now the user's own (record rules apply) AND filtered on env.companies. The
# figures are what the records say: CO2 avoided is an estimate reported apart
# from the inventory, counted only once a recycler certificate covers the
# item; the ESG report lists computed metrics only.
import datetime

SURFACES = {
    "fix.ewaste.collection": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_triage_reuse",
            "action_triage_refurbish",
            "action_triage_recycle",
            "action_triage_hazardous",
            "action_secure_destruction",
            "action_recycle_estimated",
            "action_issue_certificate",
            "action_remove_from_batch",
            "action_apply_storage_extension",
            "action_route_harvest",
        },
    },
    "fix.ewaste.event": {
        "order": "event_date desc, id desc",
        "limit": 200,
        "actions": {"action_open", "action_close"},
    },
    "fix.ewaste.triage": {"order": "decided_on desc, id desc", "limit": 300, "actions": set()},
    "fix.ewaste.batch": {
        "order": "dispatched_on desc, id desc",
        "limit": 300,
        "actions": {
            "action_load_ready_items",
            "action_dispatch",
            "action_receive",
            "action_process",
            "action_record_certificate",
        },
    },
    "fix.ewaste.battery": {
        "order": "received_on desc, id desc",
        "limit": 300,
        "actions": {"action_inspect_and_quarantine", "action_dispatch", "action_process"},
    },
    "fix.ewaste.partner": {
        "order": "name",
        "limit": 200,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_suspend",
            "action_renew",
        },
    },
    "fix.ewaste.certificate": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        "actions": {"action_issue", "action_revoke"},
    },
    "fix.ewaste.return": {
        "order": "period desc, authority",
        "limit": 200,
        "actions": {
            "action_calculate_mass_balance",
            "action_submit_return",
            "action_accept_return",
        },
    },
    "fix.esg.metric": {"order": "id desc", "limit": 400, "actions": {"action_recompute"}},
    "fix.ewaste.manifest": {"order": "issued_on desc, id desc", "limit": 300, "actions": set()},
    "fix.ewaste.basel.pic": {
        "order": "valid_to desc, id desc",
        "limit": 200,
        "actions": {"action_record_consent", "action_withdraw"},
    },
    "fix.ewaste.registration": {
        "order": "valid_to desc, id desc",
        "limit": 200,
        "actions": {"action_activate"},
    },
    "fix.ewaste.settlement": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_request_approval", "action_recall_approval", "action_cancel"},
    },
    # M18 capture pass 2 (19 Nov 2026): the records the spec names on the
    # sub-module pages that had no model (models/fix_m18_capture.py)
    "fix.ewaste.collection.point": {
        "order": "name",
        "limit": 300,
        "actions": {"action_activate", "action_reopen", "action_close"},
    },
    "fix.ewaste.corporate.disposal": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_confirm", "action_close"},
    },
    "fix.ewaste.corporate.disposal.line": {
        "order": "disposal_id desc, id",
        "limit": 500,
        "actions": {"action_accept_exception"},
    },
    "fix.ewaste.triage.criteria": {
        "order": "effective_from desc, id desc",
        "limit": 100,
        "actions": {"action_publish"},
    },
    "fix.ewaste.donation": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_approve", "action_hand_over", "action_cancel"},
    },
    "fix.ewaste.partner.downstream": {
        "order": "partner_id, material_class",
        "limit": 300,
        "actions": {"action_verify", "action_withdraw"},
    },
    "fix.ewaste.certificate.exception": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_close"},
    },
    "fix.ewaste.material.recovery": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_raise_income"},
    },
    "fix.esg.factor.set": {"order": "id desc", "limit": 100, "actions": {"action_activate"}},
    "fix.ewaste.obligation": {
        "order": "next_review, id",
        "limit": 300,
        "actions": {"action_activate", "action_review", "action_retire"},
    },
}

_MATERIAL_LABELS = {
    "phone": "Mobile Phone",
    "laptop": "Laptop",
    "tablet": "Tablet",
    "accessory": "Accessory",
    "battery": "Battery",
    "other": "Other",
}
_TRIAGE_LABELS = {
    "reuse": "Reusable",
    "refurbish": "Refurbishable",
    "recycle": "Recycle Only",
    "hazardous": "Hazardous",
    "harvest": "Parts Harvest",
    "donate": "Donation",
}
# GRI 306-4 "diverted from disposal" (preparation for reuse): the M14 routes,
# parts harvesting and donation (capture pass 2, FR-ESG-008/023)
_DIVERTED = ("reuse", "refurbish", "harvest", "donate")
_CO2_NOTE = (
    "CO2e avoided is an ESTIMATE (weight x the configured factor, version stamped), "
    "counted only for items a recycler certificate covers, and reported apart from "
    "the inventory: it is not a reduction of the company's own emissions."
)


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


def _mine(env, model, domain=None, order=None):
    """The user's own read (record rules apply), inside the user's companies."""
    return env[model].search(
        [("company_id", "in", env.companies.ids), *(domain or [])], order=order
    )


def _collections(env):
    return _mine(env, "fix.ewaste.collection")


def _month_key(value):
    return value.strftime("%Y-%m") if value else "—"


def _certified_co2(recs):
    return sum(r.esg_co2_saved_kg or 0.0 for r in recs if r.state == "certified")


def collection_volume(env, date_from=None, date_to=None, **params):
    by_key = {}
    for rec in _collections(env):
        key = (_month_key(rec.collected_on or rec.create_date), rec.material_type or "other")
        row = by_key.setdefault(
            key,
            {
                "period": key[0],
                "material": _MATERIAL_LABELS.get(key[1], key[1]),
                "collections": 0,
                "weight_kg": 0.0,
                "co2_avoided_kg": 0.0,
            },
        )
        row["collections"] += 1
        row["weight_kg"] += rec.weight_kg or 0.0
        row["co2_avoided_kg"] += _certified_co2(rec)
    rows = sorted(by_key.values(), key=lambda r: (r["period"], r["material"]))
    for row in rows:
        row["weight_kg"] = round(row["weight_kg"], 2)
        row["co2_avoided_kg"] = round(row["co2_avoided_kg"], 2)
    return _pack(
        "Collection Volume Trend — collections by month and material",
        ["period", "material", "collections", "weight_kg", "co2_avoided_kg"],
        {
            "period": "Period",
            "material": "Material",
            "collections": "Collections",
            "weight_kg": "Weight (kg)",
            "co2_avoided_kg": "CO2e Avoided (kg, estimate)",
        },
        rows,
        ["Every collection counts at its intake month (inventory).", _CO2_NOTE],
        totals={
            "period": "Total",
            "collections": sum(r["collections"] for r in rows),
            "weight_kg": round(sum(r["weight_kg"] for r in rows), 2),
            "co2_avoided_kg": round(sum(r["co2_avoided_kg"] for r in rows), 2),
        },
        empty="No collections recorded yet.",
    )


def disposition_mix(env, date_from=None, date_to=None, **params):
    by_grade = {}
    for rec in _collections(env):
        key = rec.triage_grade or "untriaged"
        row = by_grade.setdefault(
            key,
            {
                "disposition": _TRIAGE_LABELS.get(key, "Untriaged"),
                "collections": 0,
                "weight_kg": 0.0,
            },
        )
        row["collections"] += 1
        row["weight_kg"] += rec.weight_kg or 0.0
    rows = []
    total_weight = sum(r["weight_kg"] for r in by_grade.values())
    for row in by_grade.values():
        row["weight_kg"] = round(row["weight_kg"], 2)
        row["share_pct"] = (
            round((row["weight_kg"] / total_weight) * 100.0, 1) if total_weight else 0.0
        )
        rows.append(row)
    order = [*list(_TRIAGE_LABELS.values()), "Untriaged"]
    rows.sort(key=lambda r: order.index(r["disposition"]) if r["disposition"] in order else 99)
    return _pack(
        "Disposition Mix — where the collected weight went",
        ["disposition", "collections", "weight_kg", "share_pct"],
        {
            "disposition": "Disposition",
            "collections": "Collections",
            "weight_kg": "Weight (kg)",
            "share_pct": "Share %",
        },
        rows,
        [
            "Disposition is the assessor's recorded triage decision (write-once); "
            "untriaged collections stay visible until a decision is made."
        ],
        totals={
            "disposition": "Total",
            "collections": sum(r["collections"] for r in rows),
            "weight_kg": round(total_weight, 2),
        },
        empty="No collections recorded yet.",
    )


def material_recovery(env, date_from=None, date_to=None, **params):
    collections = _collections(env)
    batches = _mine(env, "fix.ewaste.batch")
    rows = []
    for key, label in _MATERIAL_LABELS.items():
        col = collections.filtered(lambda r, k=key: r.material_type == k)
        bat = batches.filtered(lambda r, k=key: r.material_type == k)
        processed = bat.filtered(lambda r: r.state == "processed")
        collected_kg = sum(col.mapped("weight_kg"))
        batch_kg = sum(bat.mapped("weight_kg"))
        processed_kg = sum(processed.mapped("processed_weight_kg"))
        rows.append(
            {
                "material": label,
                "collections": len(col),
                "collected_kg": round(collected_kg, 2),
                "batch_kg": round(batch_kg, 2),
                "processed_kg": round(processed_kg, 2),
                "recovery_pct": round((processed_kg / collected_kg) * 100.0, 1)
                if collected_kg
                else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["collected_kg"])
    return _pack(
        "Material Recovery — collected vs batched vs processed",
        ["material", "collections", "collected_kg", "batch_kg", "processed_kg", "recovery_pct"],
        {
            "material": "Material",
            "collections": "Collections",
            "collected_kg": "Collected (kg)",
            "batch_kg": "Batched (kg)",
            "processed_kg": "Processed (kg)",
            "recovery_pct": "Recovery %",
        },
        rows,
        [
            "Batched weight is the sum of the batch's items; processed weight is the "
            "recycler's weighbridge at receipt, within tolerance of what left. Recovery = "
            "processed ÷ collected for the same material; unbatched weight is the gap."
        ],
        totals={
            "material": "Total",
            "collections": sum(r["collections"] for r in rows),
            "collected_kg": round(sum(r["collected_kg"] for r in rows), 2),
            "batch_kg": round(sum(r["batch_kg"] for r in rows), 2),
            "processed_kg": round(sum(r["processed_kg"] for r in rows), 2),
        },
        empty="No collections recorded yet.",
    )


def compliance_pack(env, date_from=None, date_to=None, **params):
    returns = _mine(env, "fix.ewaste.return")
    partners = _mine(env, "fix.ewaste.partner")
    certificates = _mine(env, "fix.ewaste.certificate", [("state", "=", "issued")])
    rows = []
    for rec in returns:
        rows.append(
            {
                "return": rec.name,
                "authority": dict(rec._fields["authority"].selection).get(rec.authority),
                "period": rec.period,
                "due": str(rec.due_date),
                "submitted": str(rec.submitted_on) if rec.submitted_on else "—",
                "tonnage": round(rec.total_tonnage_collected or 0.0, 3),
                "state": dict(rec._fields["state"].selection).get(rec.state),
                "overdue": rec.is_overdue,
            }
        )
    rows.sort(key=lambda r: (not r["overdue"], r["period"]), reverse=True)
    today = datetime.date.today()
    valid_partners = len(
        partners.filtered(
            lambda p: p.state == "active"
            and p.approved_by_id
            and p.valid_to
            and p.valid_to >= today
        )
    )
    return _pack(
        "Compliance Evidence Pack — DoE / BTRC returns",
        ["return", "authority", "period", "due", "submitted", "tonnage", "state", "overdue"],
        {
            "return": "Return",
            "authority": "Authority",
            "period": "Period",
            "due": "Due",
            "submitted": "Submitted",
            "tonnage": "Collected (t)",
            "state": "State",
            "overdue": "Overdue",
        },
        rows,
        [
            "Evidence in one place: %d statutory returns, %d recycler certificates issued, "
            "%d approved recycler(s) with an in-date licence today."
            % (len(returns), len(certificates), valid_partners)
        ],
        empty="No statutory returns recorded yet.",
    )


def impact_diversion(env, date_from=None, date_to=None, **params):
    collections = _collections(env)
    rows = []
    total_weight = 0.0
    total_co2 = 0.0
    diverted = 0.0
    for key, label in [*list(_TRIAGE_LABELS.items()), ("untriaged", "Untriaged")]:
        if key == "untriaged":
            recs = collections.filtered(lambda r: not r.triage_grade)
        else:
            recs = collections.filtered(lambda r, k=key: r.triage_grade == k)
        weight = sum(recs.mapped("weight_kg"))
        co2 = _certified_co2(recs)
        total_weight += weight
        total_co2 += co2
        if key in _DIVERTED:
            diverted += weight
        rows.append(
            {
                "disposition": label,
                "collections": len(recs),
                "weight_kg": round(weight, 2),
                "co2_avoided_kg": round(co2, 2),
                "share_pct": 0.0,
            }
        )
    for row in rows:
        row["share_pct"] = (
            round((row["weight_kg"] / total_weight) * 100.0, 1) if total_weight else 0.0
        )
    return _pack(
        "Impact & Diversion — diverted vs recycled vs hazardous",
        ["disposition", "collections", "weight_kg", "co2_avoided_kg", "share_pct"],
        {
            "disposition": "Disposition",
            "collections": "Collections",
            "weight_kg": "Weight (kg)",
            "co2_avoided_kg": "CO2e Avoided (kg, estimate)",
            "share_pct": "Share %",
        },
        rows,
        [
            "Diversion rate = (reuse + refurbish) weight ÷ total weight = %.1f%%."
            % ((diverted / total_weight) * 100.0 if total_weight else 0.0),
            _CO2_NOTE,
        ],
        totals={
            "disposition": "Total",
            "collections": sum(r["collections"] for r in rows),
            "weight_kg": round(total_weight, 2),
            "co2_avoided_kg": round(total_co2, 2),
        },
        empty="No collections recorded yet.",
    )


def esg_report(env, date_from=None, date_to=None, **params):
    metrics = _mine(
        env, "fix.esg.metric", [("computed", "=", True)], order="period desc, metric_type"
    )
    typed = len(_mine(env, "fix.esg.metric", [("computed", "=", False)]))
    rows = []
    for rec in metrics:
        rows.append(
            {
                "metric": rec.name,
                "type": dict(rec._fields["metric_type"].selection).get(rec.metric_type),
                "scope": dict(rec._fields["scope"].selection).get(rec.scope),
                "period": rec.period,
                "value": round(rec.value, 3),
                "unit": rec.unit or "",
                "factor": rec.factor_version or "",
                "sources": rec.source_count,
            }
        )
    notes = [
        "Every metric is computed from the e-waste collections of its company and "
        "period (BRU-ESG-11); none can be typed. Inventory and avoided figures are "
        "separate rows and are never added together.",
        _CO2_NOTE,
    ]
    if typed:
        notes.append(
            "%d metric row(s) typed before the A05 audit are excluded from this report." % typed
        )
    return _pack(
        "Sustainability Reporting — computed ESG metrics",
        ["metric", "type", "scope", "period", "value", "unit", "factor", "sources"],
        {
            "metric": "Metric",
            "type": "Type",
            "scope": "Scope",
            "period": "Period",
            "value": "Value",
            "unit": "Unit",
            "factor": "Factor Version",
            "sources": "Source Records",
        },
        rows,
        notes,
        empty="No computed ESG metrics yet (Recompute, or wait for the daily job).",
    )


REPORTS = {
    "collection_volume": collection_volume,
    "disposition_mix": disposition_mix,
    "material_recovery": material_recovery,
    "compliance_pack": compliance_pack,
    "impact_diversion": impact_diversion,
    "esg_report": esg_report,
}


def kpis(env):
    collections = _collections(env)
    today = datetime.date.today()
    month_start = today.replace(day=1)
    open_states = ("collected", "triaged", "destruction", "recycled", "hazmat")
    weight_mtd = sum(
        r.weight_kg or 0.0
        for r in collections
        if (r.collected_on or (r.create_date and r.create_date.date()) or today) >= month_start
    )
    total = sum(r.weight_kg or 0.0 for r in collections)
    diverted = sum(r.weight_kg or 0.0 for r in collections if r.triage_grade in _DIVERTED)
    recycled = sum(r.weight_kg or 0.0 for r in collections if r.state in ("recycled", "certified"))
    returns = _mine(env, "fix.ewaste.return", [("state", "=", "draft")])
    due = returns.filtered(
        lambda r: r.due_date and r.due_date <= today + datetime.timedelta(days=30)
    )
    certs = len(_mine(env, "fix.ewaste.certificate", [("state", "=", "issued")]))
    co2 = round(_certified_co2(collections), 2)
    return {
        "open_collections": len(collections.filtered(lambda r: r.state in open_states)),
        "weight_mtd": round(weight_mtd, 2),
        "diverted_kg": round(diverted, 2),
        "co2_saved_kg": co2,
        "certificates_issued": certs,
        "returns_due_30d": len(due),
        # the module home's tiles (static/src/a05/m18.js)
        "total_intake_kg": round(total, 2),
        "recycled_kg": round(recycled, 2),
        "certs_issued": certs,
        "diversion_rate": round((diverted / total) * 100.0, 1) if total else 0.0,
        "storage_overdue": len(collections.filtered(lambda r: r.storage_overdue)),
    }
