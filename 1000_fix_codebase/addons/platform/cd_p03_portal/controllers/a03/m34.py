# A03 · M34 CX, Feedback & Complaints — surfaces, report packs and KPIs over
# fix.survey / fix.complaint / fix.cx.followup / fix.cx.throttle /
# fix.cx.review (+ goodwill credit notes from M20). Every figure is measured;
# sentiment is the recorded rating, never NLP-guessed.
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    "fix.survey": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.complaint": {
        "order": "create_date desc, id desc",
        "limit": 300,
        # The workflow's own actions. With an empty set the only route to
        # 'closed' was writing the state field, skipping RCA, DOFA and CAPA.
        # A03 P2 (M34-3/M34-6): the full ISO 10002 cl. 7 lifecycle.
        "actions": {
            "action_take_ownership",
            "action_assign",
            "action_assess",
            "action_reassess",
            "action_investigate",
            "action_raise_ncr",
            "action_record_root_cause",
            "action_verify_root_cause",
            # A10 S6 (M23-12): the Quality Manager links the REAL CAPA — the
            # one raised from this complaint's own NCR. The field is guarded.
            "action_link_capa",
            "action_open_capa",
            "action_request_verification",
            # R7: the concession is decided from the M63 inbox.
            "action_request_approval",
            "action_recall_approval",
            "action_respond",
            "action_customer_accept",
            "action_customer_reject",
            "action_close",
            "action_decline",
            "action_reopen",
        },
    },
    "fix.cx.followup": {
        "order": "due_date, id",
        "limit": 300,
        "actions": {"action_close_recovered", "action_raise_complaint"},
    },
    "fix.cx.throttle": {
        "order": "partner_id",
        "limit": 300,
        "actions": set(),
    },
    "fix.cx.review": {
        "order": "reviewed_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    # NOTE (A03 audit 2026-10-31): the misplaced M42 "fix.supplier.scorecard"
    # surface was removed — supplier performance is owned by M42 (A06); serving
    # it here also collided with M42's own surface declaration.
    # --- added by the A03 gap-closure build -------------------
    # Each of these is bound by a workspace screen below; an
    # unservable surface is what test_a03_registry_coverage exists
    # to catch, and a surface no screen opens is dead weight it
    # also catches.
    "fix.survey.template": {
        "order": "name, version desc",
        "limit": 200,
        "actions": {"action_new_version", "action_publish", "action_retire"},
    },
    "fix.survey.question": {
        "order": "template_id, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.survey.answer": {
        "order": "survey_id, sequence, id",
        "limit": 300,
        "actions": set(),
    },
}

# A03 audit M34-12: 'verification' is CAPA verification, an open state; it
# was counted as closed. Declined (not upheld) complaints are finished.
CLOSED_COMPLAINT = ("closed", "rejected")


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty or "No data in this basis yet.",
    }


def _rating_of(survey):
    try:
        return int(survey.rating or 0)
    except (TypeError, ValueError):
        return 0


def _responses(env):
    return env["fix.survey"].sudo().search([("state", "=", "responded")])


def _month_key(value):
    return value.strftime("%Y-%m") if hasattr(value, "strftime") else str(value)[:7]


def survey_blueprint(env, date_from=None, date_to=None, **params):
    """The survey instrument actually implemented by fix.survey."""
    rows = [
        {
            "question": "Overall Rating (NPS-style)",
            "type": "Selection 1–5",
            "scale": "1 Very Poor … 5 Excellent",
            "field": "rating",
        },
        {
            "question": "NPS Score",
            "type": "Integer 0–10",
            "scale": "0–10 likelihood to recommend",
            "field": "nps_score",
        },
        {"question": "Free comment", "type": "Text", "scale": "Unstructured", "field": "comment"},
    ]
    return _pack(
        "Survey Designer — the live instrument",
        ["question", "type", "scale", "field"],
        {"question": "Question", "type": "Type", "scale": "Scale", "field": "Stored Field"},
        rows,
        [
            "The CX survey is a fixed three-question instrument stored on fix.survey; "
            "a drag-drop question designer is not built (no model for custom questions)."
        ],
    )


def csat_by_branch(env, date_from=None, date_to=None, **params):
    responses = _responses(env)
    by_ou = {}
    for survey in responses:
        key = survey.operating_unit_id.id if survey.operating_unit_id else 0
        row = by_ou.setdefault(
            key,
            {
                "unit": survey.operating_unit_id.name if survey.operating_unit_id else "Unassigned",
                "responses": 0,
                "positive": 0,
                "ratings": [],
            },
        )
        row["responses"] += 1
        rating = _rating_of(survey)
        if rating:
            row["ratings"].append(rating)
        if rating >= 4:
            row["positive"] += 1
    rows = []
    for row in by_ou.values():
        avg = round(sum(row["ratings"]) / len(row["ratings"]), 2) if row["ratings"] else 0.0
        rows.append(
            {
                "unit": row["unit"],
                "responses": row["responses"],
                "avg_rating": avg,
                "csat_pct": round(row["positive"] / row["responses"] * 100.0, 1)
                if row["responses"]
                else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["csat_pct"])
    totals = {
        "unit": "Total",
        "responses": sum(r["responses"] for r in rows),
        "avg_rating": round(
            sum(s["avg_rating"] * s["responses"] for s in rows)
            / max(1, sum(r["responses"] for r in rows)),
            2,
        ),
        "csat_pct": round(
            sum(1 for s in responses if _rating_of(s) >= 4) / len(responses) * 100.0, 1
        )
        if responses
        else 0.0,
    }
    return _pack(
        "CSAT by Branch & Technician",
        ["unit", "responses", "avg_rating", "csat_pct"],
        {
            "unit": "Operating Unit",
            "responses": "Responses",
            "avg_rating": "Avg Rating",
            "csat_pct": "CSAT % (4–5)",
        },
        rows,
        [
            "CSAT % = ratings 4–5 over responses. The survey stores the operating unit, not "
            "the technician — technician-level CSAT needs the field-order link (declared gap)."
        ],
        totals=totals if rows else None,
        empty="No survey responses yet.",
    )


def nps_trend(env, date_from=None, date_to=None, **params):
    """Monthly NPS from the model's OWN computed nps_score (-100/0/+100 per
    response, derived from the 1–5 rating). Aggregation is the mean of the
    per-response scores; promoters/passives/detractors are the score bands."""
    responses = _responses(env)
    buckets = {}
    for survey in responses:
        key = _month_key(survey.create_date)
        row = buckets.setdefault(
            key,
            {"month": key, "promoters": 0, "passives": 0, "detractors": 0, "n": 0, "score_sum": 0},
        )
        score = survey.nps_score or 0
        row["n"] += 1
        row["score_sum"] += score
        if score > 0:
            row["promoters"] += 1
        elif score < 0:
            row["detractors"] += 1
        else:
            row["passives"] += 1
    rows = []
    for key in sorted(buckets, reverse=True)[:6]:
        row = buckets[key]
        row["nps"] = round(row["score_sum"] / row["n"], 1)
        rows.append(
            {k: row[k] for k in ("month", "n", "promoters", "passives", "detractors", "nps")}
        )
    complaints = env["fix.complaint"].sudo().search([])
    drivers = {}
    for c in complaints:
        drivers[c.category] = drivers.get(c.category, 0) + 1
    top = sorted(drivers.items(), key=lambda kv: -kv[1])[:3]
    notes = [
        "NPS here is the mean of the model's per-response nps_score (−100 detractor, "
        "0 passive, +100 promoter) derived from the 1–5 rating; the 0–10 recommend "
        "scale is not captured by the instrument (declared gap).",
        "Drivers: top recorded complaint categories — %s."
        % (", ".join("%s (%d)" % kv for kv in top) if top else "none recorded"),
    ]
    scores = [r["nps"] * r["n"] for r in rows]
    totals = {
        "month": "Total",
        "n": sum(r["n"] for r in rows),
        "promoters": sum(r["promoters"] for r in rows),
        "passives": sum(r["passives"] for r in rows),
        "detractors": sum(r["detractors"] for r in rows),
        "nps": round(sum(scores) / sum(r["n"] for r in rows), 1) if rows else 0.0,
    }
    return _pack(
        "NPS Trend & Drivers",
        ["month", "n", "promoters", "passives", "detractors", "nps"],
        {
            "month": "Month",
            "n": "Responses",
            "promoters": "Promoters (score +100)",
            "passives": "Passives (0)",
            "detractors": "Detractors (−100)",
            "nps": "NPS (mean)",
        },
        rows,
        notes,
        totals=totals if rows else None,
        empty="No survey responses yet.",
    )


def complaint_pareto(env, date_from=None, date_to=None, **params):
    complaints = env["fix.complaint"].sudo().search([])
    counts = {}
    for c in complaints:
        counts[c.category] = counts.get(c.category, 0) + 1
    total = len(complaints)
    rows = []
    cumulative = 0
    for category, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        cumulative += count
        rows.append(
            {
                "category": category,
                "complaints": count,
                "share_pct": round(count / total * 100.0, 1) if total else 0.0,
                "cumulative_pct": round(cumulative / total * 100.0, 1) if total else 0.0,
            }
        )
    return _pack(
        "Complaint Category Pareto",
        ["category", "complaints", "share_pct", "cumulative_pct"],
        {
            "category": "Category",
            "complaints": "Complaints",
            "share_pct": "Share %",
            "cumulative_pct": "Cumulative %",
        },
        rows,
        ["Cumulative % follows the Pareto order (largest category first)."],
        totals={
            "category": "Total",
            "complaints": total,
            "share_pct": 100.0,
            "cumulative_pct": 100.0,
        }
        if rows
        else None,
        empty="No complaints recorded yet.",
    )


def closed_loop(env, date_from=None, date_to=None, **params):
    followups = env["fix.cx.followup"].sudo().search([])
    complaints = env["fix.complaint"].sudo().search([])
    closed = complaints.filtered(lambda c: c.state in CLOSED_COMPLAINT)
    recovered = followups.filtered(lambda f: f.state == "recovered")
    rows = [
        {"metric": "Follow-ups opened", "value": len(followups), "basis": "fix.cx.followup"},
        {"metric": "Recovered", "value": len(recovered), "basis": "state=recovered"},
        {
            "metric": "Still open",
            "value": len(followups.filtered(lambda f: f.state == "open")),
            "basis": "state=open",
        },
        {
            "metric": "Complaints closed",
            "value": len(closed),
            "basis": "state in closed/declined",
        },
        {
            "metric": "Complaints open",
            "value": len(complaints) - len(closed),
            "basis": "all other states",
        },
        {
            "metric": "Recovery rate",
            "value": round(len(recovered) / len(followups) * 100.0, 1) if followups else 0.0,
            "basis": "% recovered of follow-ups",
        },
    ]
    return _pack(
        "Closed-Loop Effectiveness",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        [
            "A closed loop means the detractor was contacted and the outcome recorded — "
            "not merely that a task exists."
        ],
    )


def review_sentiment(env, date_from=None, date_to=None, **params):
    reviews = env["fix.cx.review"].sudo().search([])
    by_source = {}
    for r in reviews:
        row = by_source.setdefault(
            r.source,
            {
                "source": r.source,
                "reviews": 0,
                "stars": 0,
                "positive": 0,
                "flagged": 0,
            },
        )
        row["reviews"] += 1
        row["stars"] += r.rating or 0
        if (r.rating or 0) >= 4:
            row["positive"] += 1
        if r.state == "flagged":
            row["flagged"] += 1
    rows = []
    for row in by_source.values():
        row["avg_stars"] = round(row["stars"] / row["reviews"], 2) if row["reviews"] else 0.0
        row["positive_pct"] = (
            round(row["positive"] / row["reviews"] * 100.0, 1) if row["reviews"] else 0.0
        )
        rows.append(
            {k: row[k] for k in ("source", "reviews", "avg_stars", "positive_pct", "flagged")}
        )
    rows.sort(key=lambda r: -r["reviews"])
    return _pack(
        "Review Sentiment Summary",
        ["source", "reviews", "avg_stars", "positive_pct", "flagged"],
        {
            "source": "Source",
            "reviews": "Reviews",
            "avg_stars": "Avg Stars",
            "positive_pct": "Positive % (4–5★)",
            "flagged": "Flagged",
        },
        rows,
        ["Sentiment is the recorded star rating — no NLP inference is claimed."],
        totals={
            "source": "Total",
            "reviews": sum(r["reviews"] for r in rows),
            "avg_stars": round(
                sum(r["avg_stars"] * r["reviews"] for r in rows)
                / max(1, sum(r["reviews"] for r in rows)),
                2,
            ),
            "flagged": sum(r["flagged"] for r in rows),
        }
        if rows
        else None,
        empty="No reviews captured yet.",
    )


def complaint_escalation(env, date_from=None, date_to=None, **params):
    complaints = env["fix.complaint"].sudo().search([])
    today = datetime.date.today()
    rows = []
    for c in complaints.filtered(lambda x: x.state not in CLOSED_COMPLAINT):
        age = (today - c.create_date.date()).days if c.create_date else 0
        rows.append(
            {
                "complaint": c.name,
                "customer": c.customer_id.name,
                "category": c.category,
                "severity": c.severity,
                "state": c.state,
                "age_days": age,
            }
        )
    rows.sort(key=lambda r: -r["age_days"])
    return _pack(
        "Severity & Escalation — open complaints by age",
        ["complaint", "customer", "category", "severity", "state", "age_days"],
        {
            "complaint": "Complaint",
            "customer": "Customer",
            "category": "Category",
            "severity": "Severity",
            "state": "State",
            "age_days": "Age (days)",
        },
        rows,
        [
            "Open = not closed or declined. Age is calendar days since creation; "
            "escalation follows severity, with age as the tie-breaker."
        ],
        empty="No open complaints — the queue is clear.",
    )


def goodwill_authority(env, date_from=None, date_to=None, **params):
    try:
        notes = env["fix.credit.note"].sudo().search([("reason_code", "=", "goodwill")])
    except Exception:
        notes = env["fix.credit.note"].browse()
    rows = []
    for n in notes:
        rows.append(
            {
                "note": n.invoice_id.name or "AR/%s" % n.invoice_id.id,
                "customer": n.invoice_id.customer_id.name,
                "amount": round(n.amount, 2),
                "state": n.state,
                "issued_at": n.issued_at.strftime("%Y-%m-%d") if n.issued_at else "—",
            }
        )
    total = round(sum(n.amount for n in notes.filtered(lambda x: x.state == "issued")), 2)
    return _pack(
        "Goodwill Authority — issued goodwill credits (M20 credit notes)",
        ["note", "customer", "amount", "state", "issued_at"],
        {
            "note": "Invoice",
            "customer": "Customer",
            "amount": "Credit Amount",
            "state": "State",
            "issued_at": "Issued",
        },
        rows,
        [
            "A goodwill credit is a real AR credit note with reason 'goodwill'; the "
            "authority threshold and GL posting live in M20."
        ],
        totals={"note": "Total issued", "amount": total} if rows else None,
        empty="No goodwill credits issued yet.",
    )


def journey_measurement(env, date_from=None, date_to=None, **params):
    orders = env["fix.service.order"].sudo()
    surveys = env["fix.survey"].sudo().search([])
    complaints = env["fix.complaint"].sudo().search([])
    buckets = {}
    for order in orders:
        key = _month_key(order.create_date)
        buckets.setdefault(
            key, {"month": key, "orders": 0, "surveys": 0, "responses": 0, "complaints": 0}
        )["orders"] += 1
    for survey in surveys:
        key = _month_key(survey.create_date)
        row = buckets.setdefault(
            key, {"month": key, "orders": 0, "surveys": 0, "responses": 0, "complaints": 0}
        )
        row["surveys"] += 1
        if survey.state == "responded":
            row["responses"] += 1
    for complaint in complaints:
        key = _month_key(complaint.create_date)
        row = buckets.setdefault(
            key, {"month": key, "orders": 0, "surveys": 0, "responses": 0, "complaints": 0}
        )
        row["complaints"] += 1
    rows = []
    for key in sorted(buckets, reverse=True)[:6]:
        row = buckets[key]
        row["response_pct"] = (
            round(row["responses"] / row["surveys"] * 100.0, 1) if row["surveys"] else 0.0
        )
        row["complaint_rate"] = (
            round(row["complaints"] / row["orders"] * 100.0, 1) if row["orders"] else 0.0
        )
        rows.append(row)
    return _pack(
        "Journey Measurement: Orders to Surveys to Responses to Complaints",
        ["month", "orders", "surveys", "responses", "response_pct", "complaints", "complaint_rate"],
        {
            "month": "Month",
            "orders": "Orders",
            "surveys": "Surveys Sent",
            "responses": "Responses",
            "response_pct": "Response %",
            "complaints": "Complaints",
            "complaint_rate": "Complaint Rate %",
        },
        rows,
        [
            "Counts are grouped by each record's creation month; response % is "
            "responses over surveys, complaint rate complaints over orders."
        ],
        empty="No journey records yet.",
    )


def voc_analytics(env, date_from=None, date_to=None, **params):
    responses = _responses(env)
    ratings = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    for s in responses:
        key = str(_rating_of(s))
        if key in ratings:
            ratings[key] += 1
    scores = [s.nps_score or 0 for s in responses]
    rows = [
        {"metric": "Responses", "value": len(responses), "basis": "fix.survey responded"},
        {
            "metric": "Avg rating",
            "value": round(sum(_rating_of(s) for s in responses) / len(responses), 2)
            if responses
            else 0.0,
            "basis": "1–5 rating",
        },
        {
            "metric": "NPS (mean of per-response scores)",
            "value": round(sum(scores) / len(scores), 1) if scores else 0.0,
            "basis": "model nps_score (−100/0/+100)",
        },
    ]
    for star in ("5", "4", "3", "2", "1"):
        rows.append(
            {
                "metric": "%s-star responses" % star,
                "value": ratings[star],
                "basis": "rating distribution",
            }
        )
    recent = responses.filtered(lambda s: (s.comment or "").strip())[:5]
    notes = ["Latest free-text comments (verbatim):"]
    for s in recent:
        notes.append("“%s” — %s" % (s.comment.strip()[:160], s.customer_id.name or "anonymous"))
    return _pack(
        "VoC Analytics — ratings, NPS and verbatim comments",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        notes,
        empty="No survey responses yet.",
    )


def experience_by_branch(env, date_from=None, date_to=None, **params):
    pack = csat_by_branch(env)
    sent = env["fix.survey"].sudo().search([])
    by_ou_sent = {}
    for s in sent:
        key = s.operating_unit_id.name if s.operating_unit_id else "Unassigned"
        by_ou_sent[key] = by_ou_sent.get(key, 0) + 1
    rows = []
    for row in pack["rows"]:
        total_sent = by_ou_sent.get(row["unit"], 0)
        rows.append(
            {
                "unit": row["unit"],
                "sent": total_sent,
                "responses": row["responses"],
                "response_pct": round(row["responses"] / total_sent * 100.0, 1)
                if total_sent
                else 0.0,
                "csat_pct": row["csat_pct"],
            }
        )
    return _pack(
        "Experience by Branch — response rate and CSAT per operating unit",
        ["unit", "sent", "responses", "response_pct", "csat_pct"],
        {
            "unit": "Operating Unit",
            "sent": "Surveys",
            "responses": "Responses",
            "response_pct": "Response %",
            "csat_pct": "CSAT %",
        },
        rows,
        [
            "Technician-level experience needs the field-order technician link; the "
            "survey records the operating unit only (declared gap)."
        ],
        empty="No surveys yet.",
    )


REPORTS = {
    "survey_blueprint": survey_blueprint,
    "csat_by_branch": csat_by_branch,
    "nps_trend": nps_trend,
    "complaint_pareto": complaint_pareto,
    "closed_loop": closed_loop,
    "review_sentiment": review_sentiment,
    "complaint_escalation": complaint_escalation,
    "goodwill_authority": goodwill_authority,
    "journey_measurement": journey_measurement,
    "voc_analytics": voc_analytics,
    "experience_by_branch": experience_by_branch,
}


def _complaint_sla_met(env):
    """Share of complaints whose resolution clock succeeded, or None.

    Counts only FINISHED resolution instances. A complaint still inside its
    window has neither met nor missed its promise, and folding it into either
    bucket would move the number every hour for no reason. None -- not 0% --
    when no clock has finished.
    """
    Instance = env.get("fix.sla.kpi.instance")
    if Instance is None:
        return None
    finished = Instance.sudo().search(
        [
            ("res_model", "=", "fix.complaint"),
            ("kpi_code", "=", "resolution"),
            ("state", "in", ("succeeded", "breached")),
        ]
    )
    if not finished:
        return None
    met = len(finished.filtered(lambda i: i.state == "succeeded"))
    return round(met / len(finished) * 100.0, 1)


def kpis(env):
    responses = _responses(env)
    all_surveys = env["fix.survey"].sudo().search([])
    scores = [s.nps_score or 0 for s in responses]
    complaints = env["fix.complaint"].sudo().search([])
    open_complaints = len(complaints.filtered(lambda c: c.state not in CLOSED_COMPLAINT))
    followups = env["fix.cx.followup"].sudo().search([("state", "in", ("open", "contacted"))])
    return {
        "csat": round(len([s for s in responses if _rating_of(s) >= 4]) / len(responses) * 100.0, 1)
        if responses
        else None,
        "nps": round(sum(scores) / len(scores), 1) if scores else None,
        "open_complaints": open_complaints,
        # Closed: complaints now bind to the S9 instance engine per
        # severity, so "met" is measured from real clocks rather than implied.
        "complaint_sla_met": _complaint_sla_met(env),
        "detractor_followups": len(followups),
        "survey_response": round(len(responses) / len(all_surveys) * 100.0, 1)
        if all_surveys
        else None,
    }


class P03CxApi(http.Controller):
    @http.route("/p03/cx/kpis", type="jsonrpc", auth="user", readonly=True)
    def cx_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M34": kpis(request.env)}
