# A05 · M18 E-Waste & Circular Economy — surfaces, packs and KPIs over the
# existing collection/ESG models and the new event, triage, batch, battery,
# partner, certificate and statutory-return models. CO2 uses the documented
# 1.5 kg CO2e per kg e-waste factor (the recycle action's own basis).
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
        },
    },
    "fix.ewaste.event": {"order": "event_date desc, id desc", "limit": 200, "actions": set()},
    "fix.ewaste.triage": {"order": "decided_on desc, id desc", "limit": 300, "actions": set()},
    "fix.ewaste.batch": {
        "order": "dispatched_on desc, id desc",
        "limit": 300,
        "actions": {"action_dispatch"},
    },
    "fix.ewaste.battery": {"order": "received_on desc, id desc", "limit": 300, "actions": set()},
    "fix.ewaste.partner": {"order": "name", "limit": 200, "actions": set()},
    "fix.ewaste.certificate": {"order": "issued_on desc, id desc", "limit": 300, "actions": set()},
    "fix.ewaste.return": {"order": "period desc, authority", "limit": 200, "actions": set()},
    "fix.esg.metric": {"order": "id desc", "limit": 400, "actions": set()},
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
}
_DIVERTED = ("reuse", "refurbish")


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


def _collections(env):
    return env["fix.ewaste.collection"].sudo().search([])


def _month_key(value):
    return value.strftime("%Y-%m") if value else "—"


def collection_volume(env, date_from=None, date_to=None, **params):
    by_key = {}
    for rec in _collections(env):
        key = (_month_key(rec.create_date), rec.material_type or "other")
        row = by_key.setdefault(
            key,
            {
                "period": key[0],
                "material": _MATERIAL_LABELS.get(key[1], key[1]),
                "collections": 0,
                "weight_kg": 0.0,
                "co2_saved_kg": 0.0,
            },
        )
        row["collections"] += 1
        row["weight_kg"] += rec.weight_kg or 0.0
        row["co2_saved_kg"] += rec.esg_co2_saved_kg or 0.0
    rows = sorted(by_key.values(), key=lambda r: (r["period"], r["material"]))
    for row in rows:
        row["weight_kg"] = round(row["weight_kg"], 2)
        row["co2_saved_kg"] = round(row["co2_saved_kg"], 2)
    return _pack(
        "Collection Volume Trend — collections by month and material",
        ["period", "material", "collections", "weight_kg", "co2_saved_kg"],
        {
            "period": "Period",
            "material": "Material",
            "collections": "Collections",
            "weight_kg": "Weight (kg)",
            "co2_saved_kg": "CO2 Saved (kg)",
        },
        rows,
        [
            "Every collection counts at its intake month; CO2 is what the recycle "
            "action recorded (1.5 kg CO2e per kg)."
        ],
        totals={
            "period": "Total",
            "collections": sum(r["collections"] for r in rows),
            "weight_kg": round(sum(r["weight_kg"] for r in rows), 2),
            "co2_saved_kg": round(sum(r["co2_saved_kg"] for r in rows), 2),
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
            "Disposition is the recorded triage grade; untriaged collections stay "
            "visible until a decision is made."
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
    batches = env["fix.ewaste.batch"].sudo().search([])
    rows = []
    for key, label in _MATERIAL_LABELS.items():
        col = collections.filtered(lambda r, k=key: r.material_type == k)
        bat = batches.filtered(lambda r, k=key: r.material_type == k)
        processed = bat.filtered(lambda r: r.state == "processed")
        collected_kg = sum(col.mapped("weight_kg"))
        batch_kg = sum(bat.mapped("weight_kg"))
        processed_kg = sum(processed.mapped("weight_kg"))
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
            "Recovery = processed batch weight ÷ collected weight for the same "
            "material. Unbatched weight stays visible as the gap."
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
    returns = env["fix.ewaste.return"].sudo().search([])
    partners = env["fix.ewaste.partner"].sudo().search([])
    certificates = env["fix.ewaste.certificate"].sudo().search([])
    rows = []
    for rec in returns:
        rows.append(
            {
                "return": rec.name,
                "authority": dict(rec._fields["authority"].selection).get(rec.authority),
                "period": rec.period,
                "due": str(rec.due_date),
                "submitted": str(rec.submitted_on) if rec.submitted_on else "—",
                "state": dict(rec._fields["state"].selection).get(rec.state),
                "overdue": rec.is_overdue,
            }
        )
    rows.sort(key=lambda r: (not r["overdue"], r["period"]), reverse=True)
    today = datetime.date.today()
    valid_partners = len(
        partners.filtered(lambda p: p.state == "active" and (not p.valid_to or p.valid_to >= today))
    )
    return _pack(
        "Compliance Evidence Pack — DoE / BTRC returns",
        ["return", "authority", "period", "due", "submitted", "state", "overdue"],
        {
            "return": "Return",
            "authority": "Authority",
            "period": "Period",
            "due": "Due",
            "submitted": "Submitted",
            "state": "State",
            "overdue": "Overdue",
        },
        rows,
        [
            "Evidence in one place: %d statutory returns, %d certificates issued, "
            "%d certified partner(s) valid today."
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
        co2 = sum(recs.mapped("esg_co2_saved_kg"))
        total_weight += weight
        total_co2 += co2
        if key in _DIVERTED:
            diverted += weight
        rows.append(
            {
                "disposition": label,
                "collections": len(recs),
                "weight_kg": round(weight, 2),
                "co2_saved_kg": round(co2, 2),
                "share_pct": 0.0,
            }
        )
    for row in rows:
        row["share_pct"] = (
            round((row["weight_kg"] / total_weight) * 100.0, 1) if total_weight else 0.0
        )
    return _pack(
        "Impact & Diversion — diverted vs recycled vs hazardous",
        ["disposition", "collections", "weight_kg", "co2_saved_kg", "share_pct"],
        {
            "disposition": "Disposition",
            "collections": "Collections",
            "weight_kg": "Weight (kg)",
            "co2_saved_kg": "CO2 Saved (kg)",
            "share_pct": "Share %",
        },
        rows,
        [
            "Diversion rate = (reuse + refurbish) weight ÷ total weight = %.1f%%. "
            "CO2 is the recorded saving, not an estimate of this report."
            % ((diverted / total_weight) * 100.0 if total_weight else 0.0)
        ],
        totals={
            "disposition": "Total",
            "collections": sum(r["collections"] for r in rows),
            "weight_kg": round(total_weight, 2),
            "co2_saved_kg": round(total_co2, 2),
        },
        empty="No collections recorded yet.",
    )


def esg_report(env, date_from=None, date_to=None, **params):
    metrics = env["fix.esg.metric"].sudo().search([], order="period desc, metric_type")
    rows = []
    for rec in metrics:
        rows.append(
            {
                "metric": rec.name,
                "type": dict(rec._fields["metric_type"].selection).get(rec.metric_type),
                "period": rec.period,
                "value": round(rec.value, 3),
                "unit": rec.unit or "",
            }
        )
    collections = _collections(env)
    co2_recorded = round(sum(collections.mapped("esg_co2_saved_kg")), 2)
    metric_co2 = round(
        sum(metrics.filtered(lambda m: m.metric_type == "co2_saved").mapped("value")), 2
    )
    return _pack(
        "Sustainability Reporting — recorded ESG metrics",
        ["metric", "type", "period", "value", "unit"],
        {"metric": "Metric", "type": "Type", "period": "Period", "value": "Value", "unit": "Unit"},
        rows,
        [
            "Recorded ESG metrics: %d. Collections record %.2f kg CO2 saved; the "
            '"co2_saved" metric rows carry %.2f kg — both are shown, never reconciled '
            "silently." % (len(metrics), co2_recorded, metric_co2)
        ],
        empty="No ESG metrics recorded yet.",
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
    open_states = ("collected", "triaged", "destruction")
    weight_mtd = sum(
        r.weight_kg or 0.0
        for r in collections
        if r.create_date and r.create_date.date() >= month_start
    )
    diverted = sum(r.weight_kg or 0.0 for r in collections if r.triage_grade in _DIVERTED)
    returns = env["fix.ewaste.return"].sudo().search([])
    due = returns.filtered(
        lambda r: r.state == "draft"
        and r.due_date
        and r.due_date <= today + datetime.timedelta(days=30)
    )
    return {
        "open_collections": len(collections.filtered(lambda r: r.state in open_states)),
        "weight_mtd": round(weight_mtd, 2),
        "diverted_kg": round(diverted, 2),
        "co2_saved_kg": round(sum(collections.mapped("esg_co2_saved_kg")), 2),
        "certificates_issued": env["fix.ewaste.certificate"]
        .sudo()
        .search_count([("state", "=", "issued")]),
        "returns_due_30d": len(due),
    }
