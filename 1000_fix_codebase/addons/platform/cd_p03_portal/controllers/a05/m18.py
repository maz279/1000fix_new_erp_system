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
#
# A05 ERP audit (20 Nov 2026, XC-06/11/15/18/23, M18-09/10/23/25): every pack
# honours the period in Dhaka days on its own date (received, dispatched,
# processed, issued, return period), 'today' is Dhaka's, diversion is GRI
# 306-4 (recycling diverted, untriaged and in-process weight outside the
# rate; the M18 engine's method when installed), the material recovery report
# reads what the recyclers recovered, and the zero-target controls and the
# spec KPIs are added.
import datetime
import logging

from .m13 import (
    CONTROL_COLS,
    CONTROL_LABELS,
    _pack,
    control_row,
    dhaka_today,
    fenced,
    in_window,
    param_float,
    pct,
    period_note,
    to_dhaka_date,
    window,
)

_logger = logging.getLogger(__name__)

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
_CO2_NOTE = (
    "CO2e avoided is an ESTIMATE (weight x the configured factor, version stamped), "
    "counted only for items a recycler certificate covers, and reported apart from "
    "the inventory: it is not a reduction of the company's own emissions."
)


def _mine(env, model, domain=None, order=None):
    """The user's own read (company and OU record rules apply), inside the
    user's companies (A05 audit E2 / XC-23)."""
    found = fenced(env, model, domain, order=order)
    return found if found is not None else env["res.partner"].browse()


def _collections(env, start=None, end=None):
    recs = _mine(env, "fix.ewaste.collection")
    if start is None:
        return recs
    return recs.filtered(lambda r: in_window(r.collected_on or r.create_date, start, end))


def _month_key(value):
    value = to_dhaka_date(value)
    return value.strftime("%Y-%m") if value else "—"


def _certified_co2(recs):
    return sum(r.esg_co2_saved_kg or 0.0 for r in recs if r.state == "certified")


def _hazardous(rec):
    return rec.triage_grade == "hazardous" or rec.material_type == "battery"


# GRI 306-4 (A05 ERP audit M18-09 / XC-15): ONE diversion definition, the M18
# engine's (stream S3: fix.esg.metric._fix_gri_306_4(company, date_from,
# date_to)), used by the KPI, the ESG metric and this report. Cohort: the items
# triaged in the period; denominator: their weight; numerator: the items whose
# final route is reuse, refurbishment, parts harvest, certified recycling or
# donation. The fallback below applies the same definition when the engine
# method is not installed.
_DIVERTED_ROUTES = ("reuse", "refurbish", "harvest", "recycle", "donation")
_GRI_DEFINITION = (
    "GRI 306-4 diversion rate = weight of the items triaged in the period whose final "
    "route is reuse, refurbishment, parts harvest, certified recycling or donation, "
    "divided by the weight of all items triaged in the period."
)


def _final_route(col):
    if col.state == "routed":
        return {"reuse": "reuse", "refurbish": "refurbish", "harvest": "harvest"}.get(
            col.triage_grade, "in_process"
        )
    if col.state == "certified":
        return "recycle"
    if col.state == "donated":
        return "donation"
    if col.state == "disposed":
        return "disposal"
    return "in_process"


def _triaged_in(env, start, end):
    """The caller's items whose triage decision is dated in the period."""
    return _mine(env, "fix.ewaste.collection", [("triage_id", "!=", False)]).filtered(
        lambda c: c.triage_id.decided_on and start <= c.triage_id.decided_on <= end
    )


def _gri_fallback(cohort):
    by_operation = dict.fromkeys((*_DIVERTED_ROUTES, "disposal", "in_process"), 0.0)
    hazardous = {"diverted": 0.0, "disposal": 0.0}
    for col in cohort:
        route = _final_route(col)
        weight = col.weight_kg or 0.0
        by_operation[route] += weight
        if _hazardous(col):
            if route in _DIVERTED_ROUTES:
                hazardous["diverted"] += weight
            elif route == "disposal":
                hazardous["disposal"] += weight
    triaged = round(sum(cohort.mapped("weight_kg")), 3)
    diverted = round(sum(by_operation[r] for r in _DIVERTED_ROUTES), 3)
    return {
        "item_count": len(cohort),
        "triaged_kg": triaged,
        "diverted_kg": diverted,
        "directed_to_disposal_kg": round(by_operation["disposal"], 3),
        "in_process_kg": round(by_operation["in_process"], 3),
        "diversion_rate_pct": round(diverted / triaged * 100.0, 2) if triaged > 0 else 0.0,
        "by_operation": {k: round(v, 3) for k, v in by_operation.items()},
        "hazardous_diverted_kg": round(hazardous["diverted"], 3),
        "hazardous_disposal_kg": round(hazardous["disposal"], 3),
        "definition": _GRI_DEFINITION,
        "method": "report fallback (same definition)",
    }


_SUMMED = (
    "item_count",
    "triaged_kg",
    "diverted_kg",
    "directed_to_disposal_kg",
    "in_process_kg",
    "hazardous_diverted_kg",
    "hazardous_disposal_kg",
)


def gri_306(env, start, end):
    """The GRI 306-4 figures of the caller's companies for [start, end]: the
    M18 engine's method per company (summed), else the same definition here."""
    Metric = env.get("fix.esg.metric")
    method = getattr(Metric.sudo(), "_fix_gri_306_4", None) if Metric is not None else None
    if not callable(method):
        return _gri_fallback(_triaged_in(env, start, end))
    out = dict.fromkeys(_SUMMED, 0.0)
    out["by_operation"] = {}
    out["definition"] = _GRI_DEFINITION
    for company in env.companies:
        try:
            part = dict(method(company, start, end) or {})
        except Exception:  # the report falls back, never breaks
            _logger.exception("M18 GRI 306-4 engine method failed")
            return _gri_fallback(_triaged_in(env, start, end))
        for key in _SUMMED:
            out[key] += part.get(key) or 0.0
        for key, value in (part.get("by_operation") or {}).items():
            out["by_operation"][key] = out["by_operation"].get(key, 0.0) + (value or 0.0)
        out["definition"] = part.get("definition") or out["definition"]
    out["item_count"] = int(out["item_count"])
    triaged = out["triaged_kg"]
    out["diversion_rate_pct"] = (
        round(out["diverted_kg"] / triaged * 100.0, 2) if triaged > 0 else 0.0
    )
    out["method"] = "fix.esg.metric._fix_gri_306_4 (M18 engine)"
    return out


def collection_volume(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=365)
    by_key = {}
    for rec in _collections(env, start, end):
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
        "Collection Volume Trend — collected %s to %s" % (start, end),
        ["period", "material", "collections", "weight_kg", "co2_avoided_kg"],
        {
            "period": "Period",
            "material": "Material",
            "collections": "Collections",
            "weight_kg": "Weight (kg)",
            "co2_avoided_kg": "CO2e Avoided (kg, estimate)",
        },
        rows,
        [
            "Every collection counts at its intake month (inventory).",
            _CO2_NOTE,
            period_note(start, end, "date received"),
        ],
        totals={
            "period": "Total",
            "collections": sum(r["collections"] for r in rows),
            "weight_kg": round(sum(r["weight_kg"] for r in rows), 2),
            "co2_avoided_kg": round(sum(r["co2_avoided_kg"] for r in rows), 2),
        },
        empty="No collections in this window.",
    )


def disposition_mix(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=90)
    by_grade = {}
    for rec in _collections(env, start, end):
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
        row["share_pct"] = pct(row["weight_kg"], total_weight)
        rows.append(row)
    order = [*list(_TRIAGE_LABELS.values()), "Untriaged"]
    rows.sort(key=lambda r: order.index(r["disposition"]) if r["disposition"] in order else 99)
    return _pack(
        "Disposition Mix — collected %s to %s" % (start, end),
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
            "untriaged collections stay visible until a decision is made.",
            period_note(start, end, "date received"),
        ],
        totals={
            "disposition": "Total",
            "collections": sum(r["collections"] for r in rows),
            "weight_kg": round(total_weight, 2),
        },
        empty="No collections in this window.",
    )


def material_recovery(env, date_from=None, date_to=None, **params):
    """A05 ERP audit M18-23: the material the recyclers RECOVERED (fix.ewaste.
    material.recovery, by spec material class) with its rate and income,
    against the weight processed in the period."""
    start, end = window(env, date_from, date_to, days=90)
    batches = _mine(env, "fix.ewaste.batch")
    processed = batches.filtered(
        lambda b: b.state == "processed" and b.processed_on and start <= b.processed_on <= end
    )
    processed_kg = sum(processed.mapped("processed_weight_kg"))
    lines = (
        env["fix.ewaste.material.recovery"].sudo().search([("batch_id", "in", batches.ids)])
        if "fix.ewaste.material.recovery" in env
        else []
    )
    labels = (
        dict(env["fix.ewaste.material.recovery"]._fields["material_class"].selection)
        if lines
        else {}
    )
    rows = {}
    for line in lines:
        day = line.recorded_on or line.batch_id.processed_on
        if not (day and start <= day <= end):
            continue
        row = rows.setdefault(
            line.material_class,
            {
                "material": labels.get(line.material_class, line.material_class),
                "lines": 0,
                "recovered_kg": 0.0,
                "income": 0.0,
                "raised": 0.0,
            },
        )
        row["lines"] += 1
        row["recovered_kg"] += line.weight_kg or 0.0
        row["income"] += line.income_amount or 0.0
        if line.state == "raised":
            row["raised"] += line.income_amount or 0.0
    out = []
    for row in rows.values():
        row["recovered_kg"] = round(row["recovered_kg"], 2)
        row["income"] = round(row["income"], 2)
        row["raised"] = round(row["raised"], 2)
        row["avg_rate"] = (
            round(row["income"] / row["recovered_kg"], 2) if row["recovered_kg"] else 0.0
        )
        row["share_pct"] = pct(row["recovered_kg"], processed_kg)
        out.append(row)
    out.sort(key=lambda r: -r["recovered_kg"])
    recovered = sum(r["recovered_kg"] for r in out)
    return _pack(
        "Material Recovery — recovered %s to %s" % (start, end),
        ["material", "lines", "recovered_kg", "share_pct", "avg_rate", "income", "raised"],
        {
            "material": "Material Class",
            "lines": "Recovery Lines",
            "recovered_kg": "Recovered (kg)",
            "share_pct": "% of Processed Weight",
            "avg_rate": "Average Rate (BDT/kg)",
            "income": "Income (agreed rate)",
            "raised": "Income Raised",
        },
        out,
        [
            "Recovered material by class as recorded against the recycler's processing "
            "of each batch; the share is of the weight processed in the period "
            "(%.2f kg across %d batch(es)). Recovery rate = %.1f%%."
            % (processed_kg, len(processed), pct(recovered, processed_kg)),
            "Income raised = recovery lines whose income settlement was raised (M20).",
            period_note(start, end, "recovery recorded date (else batch processed date)"),
        ],
        totals={
            "material": "Total",
            "lines": sum(r["lines"] for r in out),
            "recovered_kg": round(recovered, 2),
            "share_pct": pct(recovered, processed_kg),
            "income": round(sum(r["income"] for r in out), 2),
            "raised": round(sum(r["raised"] for r in out), 2),
        },
        empty="No material recovery recorded in this window.",
    )


def _month_in(period, start, end):
    try:
        year, month = (int(x) for x in str(period)[:7].split("-"))
    except (TypeError, ValueError):
        return False
    first = datetime.date(year, month, 1)
    return (
        first <= end and (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) > start
    )


def compliance_pack(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=365)
    returns = _mine(env, "fix.ewaste.return").filtered(
        lambda r: _month_in(r.period, start, end) or (r.due_date and start <= r.due_date <= end)
    )
    partners = _mine(env, "fix.ewaste.partner")
    certificates = _mine(env, "fix.ewaste.certificate", [("state", "=", "issued")]).filtered(
        lambda c: c.issued_on and start <= c.issued_on <= end
    )
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
    valid_partners = len(
        partners.filtered(
            lambda p: p.state == "active" and p.approved_by_id and p.valid_to and p.valid_to >= end
        )
    )
    on_time = len(
        returns.filtered(lambda r: r.submitted_on and r.due_date and r.submitted_on <= r.due_date)
    )
    return _pack(
        "Compliance Evidence Pack — %s to %s" % (start, end),
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
            "Evidence for the period: %d statutory return(s) (%d filed on time; target "
            "100%%), %d recycler certificate(s) issued, %d approved recycler(s) with a "
            "licence in date at %s."
            % (len(returns), on_time, len(certificates), valid_partners, end),
            period_note(start, end, "return period / due date and certificate issue date"),
        ],
        empty="No statutory returns in this window.",
    )


def impact_diversion(env, date_from=None, date_to=None, **params):
    """GRI 306-4 diversion (A05 ERP audit M18-09 / XC-15): the items triaged
    in the period by triage disposition and final route; recycling under a
    certificate counts as diverted; untriaged weight is outside the rate."""
    start, end = window(env, date_from, date_to, days=365)
    cohort = _triaged_in(env, start, end)
    rows = []
    for key, label in _TRIAGE_LABELS.items():
        recs = cohort.filtered(lambda r, k=key: r.triage_grade == k)
        if not recs:
            continue
        part = _gri_fallback(recs)
        rows.append(
            {
                "disposition": label,
                "collections": len(recs),
                "weight_kg": round(part["triaged_kg"], 2),
                "diverted_kg": round(part["diverted_kg"], 2),
                "disposal_kg": round(part["directed_to_disposal_kg"], 2),
                "in_process_kg": round(part["in_process_kg"], 2),
                "co2_avoided_kg": round(_certified_co2(recs), 2),
            }
        )
    untriaged = _collections(env, start, end).filtered(lambda r: not r.triage_id)
    if untriaged:
        rows.append(
            {
                "disposition": "Untriaged (received, outside the rate)",
                "collections": len(untriaged),
                "weight_kg": round(sum(untriaged.mapped("weight_kg")), 2),
                "diverted_kg": 0.0,
                "disposal_kg": 0.0,
                "in_process_kg": 0.0,
                "co2_avoided_kg": 0.0,
            }
        )
    gri = gri_306(env, start, end)
    ops = gri.get("by_operation") or {}
    return _pack(
        "Impact & Diversion (GRI 306-4) — triaged %s to %s" % (start, end),
        [
            "disposition",
            "collections",
            "weight_kg",
            "diverted_kg",
            "disposal_kg",
            "in_process_kg",
            "co2_avoided_kg",
        ],
        {
            "disposition": "Triage Disposition",
            "collections": "Items",
            "weight_kg": "Weight (kg)",
            "diverted_kg": "Diverted from Disposal (kg)",
            "disposal_kg": "Directed to Disposal (kg)",
            "in_process_kg": "Still in Process (kg)",
            "co2_avoided_kg": "CO2e Avoided (kg, estimate)",
        },
        rows,
        [
            "KPI-083 diversion rate (GRI 306-4) = %.1f%% (target > 92%%): %.2f kg "
            "diverted of %.2f kg triaged in the period. By operation: reuse %.2f, "
            "refurbishment %.2f, parts harvest %.2f, certified recycling %.2f, donation "
            "%.2f kg; directed to disposal %.2f kg; still in process %.2f kg."
            % (
                gri["diversion_rate_pct"],
                gri["diverted_kg"],
                gri["triaged_kg"],
                ops.get("reuse", 0.0),
                ops.get("refurbish", 0.0),
                ops.get("harvest", 0.0),
                ops.get("recycle", 0.0),
                ops.get("donation", 0.0),
                gri["directed_to_disposal_kg"],
                gri["in_process_kg"],
            ),
            "Hazardous: %.2f kg diverted, %.2f kg directed to disposal."
            % (gri["hazardous_diverted_kg"], gri["hazardous_disposal_kg"]),
            "Definition (%s): %s" % (gri["method"], gri["definition"]),
            _CO2_NOTE,
            period_note(start, end, "triage decision date (untriaged: date received)"),
        ],
        totals={
            "disposition": "Total triaged",
            "collections": gri["item_count"],
            "weight_kg": round(gri["triaged_kg"], 2),
            "diverted_kg": round(gri["diverted_kg"], 2),
            "disposal_kg": round(gri["directed_to_disposal_kg"], 2),
            "in_process_kg": round(gri["in_process_kg"], 2),
            "co2_avoided_kg": round(sum(r["co2_avoided_kg"] for r in rows), 2),
        },
        empty="No items triaged or received in this window.",
    )


def esg_report(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=365)
    metrics = _mine(
        env, "fix.esg.metric", [("computed", "=", True)], order="period desc, metric_type"
    ).filtered(lambda m: _month_in(m.period, start, end))
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
        period_note(start, end, "metric month"),
    ]
    if typed:
        notes.append(
            "%d metric row(s) typed before the A05 audit are excluded from this report." % typed
        )
    return _pack(
        "Sustainability Reporting — computed ESG metrics %s to %s" % (start, end),
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
        empty="No computed ESG metrics in this window (Recompute, or wait for the daily job).",
    )


def _tolerance(env):
    return param_float(env, "cd_ewaste.weight_tolerance_pct", 5.0)


def zero_target_controls(env, date_from=None, date_to=None, **params):
    """Spec §15: seven M18 targets are zero or 100% - a partial score is a
    breach with a percentage attached."""
    start, end = window(env, date_from, date_to, days=90)
    batches = _mine(env, "fix.ewaste.batch")
    dispatched = batches.filtered(lambda b: b.dispatched_on and start <= b.dispatched_on <= end)
    # 1. items transferred without a destruction certificate (data-bearing)
    no_cert = [
        "%s/%s" % (b.name, c.name)
        for b in dispatched
        for c in b.collection_ids
        if (c.wipe_required or c.data_bearing) and not c.wipe_certificate_id
    ]
    # 2. transfers to a partner whose certification had lapsed at dispatch
    lapsed = [
        b.name
        for b in dispatched
        if b.partner_id
        and (
            not b.partner_id.valid_to
            or b.partner_id.valid_to < b.dispatched_on
            or b.partner_id.state not in ("active", "suspended")
            or not b.partner_id.approved_by_id
        )
    ]
    # 3. chain-of-custody gaps: received weight outside tolerance, or a batch
    #    received with no weighbridge reading
    tol = _tolerance(env)
    gaps = []
    for b in batches.filtered(lambda b: b.received_on and start <= b.received_on <= end):
        off = b.weight_kg and abs(b.received_weight_kg - b.weight_kg) / b.weight_kg * 100.0 > tol
        if not b.received_weight_kg or off:
            gaps.append(b.name)
    # 4. hazmat storage ceiling breaches (position now)
    breaches = []
    if "fix.ewaste.collection.point.limit" in env:
        points = _mine(env, "fix.ewaste.collection.point")
        limits = (
            env["fix.ewaste.collection.point.limit"].sudo().search([("point_id", "in", points.ids)])
        )
        breaches = [
            "%s/%s" % (lim.point_id.name, lim.hazard_class)
            for lim in limits
            if lim.max_kg and (lim.held_kg or 0.0) > lim.max_kg
        ]
    # 5. KPI-084 disposal certificates on file (100%): processed batches with no issued certificate
    processed = batches.filtered(
        lambda b: b.state == "processed" and b.processed_on and start <= b.processed_on <= end
    )
    uncertified = [
        b.name for b in processed if not b.certificate_ids.filtered(lambda c: c.state == "issued")
    ]
    # 6. statutory returns filed late (100% on time)
    returns = _mine(env, "fix.ewaste.return").filtered(
        lambda r: r.due_date and start <= r.due_date <= end
    )
    late = [
        r.name
        for r in returns
        if (r.submitted_on and r.submitted_on > r.due_date)
        or (not r.submitted_on and r.due_date < dhaka_today(env))
    ]
    rows = [
        control_row("Items transferred without a destruction certificate", no_cert),
        control_row("Transfers to a partner with expired certification", lapsed),
        control_row("Chain-of-custody gaps (receipt outside %g%% or unweighed)" % tol, gaps),
        control_row("Hazmat storage ceiling breaches (now)", breaches),
        control_row("Processed batches without a disposal certificate (KPI-084)", uncertified),
        control_row("Statutory returns not filed on time", late),
    ]
    return _pack(
        "M18 Zero-Target Controls — %s to %s" % (start, end),
        CONTROL_COLS,
        CONTROL_LABELS,
        rows,
        [
            "Spec §15: in a compliance module a partial score is a breach with a "
            "percentage attached. Weighbridge tolerance cd_ewaste.weight_tolerance_pct = %g%%."
            % tol,
            period_note(start, end, "dispatch, receipt, processing and due dates"),
        ],
        empty="No control data.",
    )


REPORTS = {
    "collection_volume": collection_volume,
    "disposition_mix": disposition_mix,
    "material_recovery": material_recovery,
    "compliance_pack": compliance_pack,
    "impact_diversion": impact_diversion,
    "esg_report": esg_report,
    # A05 ERP audit XC-18: spec §15 controls
    "zero_target_controls": zero_target_controls,
}


def kpis(env):
    today = dhaka_today(env)
    year_start = today - datetime.timedelta(days=364)
    collections = _collections(env)
    month_start = today.replace(day=1)
    open_states = ("collected", "triaged", "destruction", "recycled", "hazmat")
    weight_mtd = sum(
        r.weight_kg or 0.0
        for r in collections
        if in_window(r.collected_on or r.create_date or today, month_start, today)
    )
    total = sum(r.weight_kg or 0.0 for r in collections)
    gri = gri_306(env, year_start, today)
    recycled = sum(r.weight_kg or 0.0 for r in collections if r.state in ("recycled", "certified"))
    returns = _mine(env, "fix.ewaste.return", [("state", "=", "draft")])
    due = returns.filtered(
        lambda r: r.due_date and r.due_date <= today + datetime.timedelta(days=30)
    )
    certs = _mine(env, "fix.ewaste.certificate", [("state", "=", "issued")])
    co2 = round(_certified_co2(collections), 2)
    batches = _mine(env, "fix.ewaste.batch")
    processed = batches.filtered(lambda b: b.state == "processed")
    certified_batches = processed.filtered(
        lambda b: b.certificate_ids.filtered(lambda c: c.state == "issued")
    )
    items = processed.mapped("collection_ids")
    covered = items.filtered(lambda c: c.state == "certified")
    due_days = param_float(env, "cd_ewaste.certificate_due_days", 30.0)
    timely = [
        c
        for c in certs
        if c.batch_id.dispatched_on
        and c.issued_on
        and (c.issued_on - c.batch_id.dispatched_on).days <= due_days
    ]
    income_12m = 0.0
    if "fix.ewaste.material.recovery" in env:
        income_12m = sum(
            line.income_amount or 0.0
            for line in env["fix.ewaste.material.recovery"]
            .sudo()
            .search([("batch_id", "in", batches.ids), ("state", "=", "raised")])
            if (line.recorded_on or year_start) >= year_start
        )
    partners = _mine(env, "fix.ewaste.partner")
    active_partners = partners.filtered(lambda p: p.state == "active")
    certified_partners = active_partners.filtered(
        lambda p: p.approved_by_id and p.valid_to and p.valid_to >= today
    )
    controls = zero_target_controls(env, str(today - datetime.timedelta(days=89)), str(today))
    breaches = sum(r["actual"] for r in controls["rows"] if isinstance(r["actual"], int))
    return {
        "open_collections": len(collections.filtered(lambda r: r.state in open_states)),
        "weight_mtd": round(weight_mtd, 2),
        "diverted_kg": round(gri["diverted_kg"], 2),
        "co2_saved_kg": co2,
        "certificates_issued": len(certs),
        "returns_due_30d": len(due),
        # the module home's tiles (static/src/a05/m18.js)
        "total_intake_kg": round(total, 2),
        "recycled_kg": round(recycled, 2),
        "certs_issued": len(certs),
        # KPI-083, GRI 306-4 (M18-09): items triaged in the last 12 months
        "diversion_rate": gri["diversion_rate_pct"],
        "storage_overdue": len(collections.filtered(lambda r: r.storage_overdue)),
        # KPI-084 and the spec §15 measures (XC-18)
        "certificates_on_file_pct": pct(len(certified_batches), len(processed))
        if processed
        else None,
        "certificate_reconciliation_pct": pct(len(covered), len(items)) if items else None,
        "certificates_in_window_pct": pct(len(timely), len(certs)) if certs else None,
        "recovery_income_12m": round(income_12m, 2),
        "partners_certified": len(certified_partners),
        "partners_active": len(active_partners),
        "zero_target_breaches_90d": breaches,
    }
