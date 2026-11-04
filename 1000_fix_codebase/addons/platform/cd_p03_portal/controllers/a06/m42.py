# A06 · M42 Supplier Relationship & Performance — surfaces, packs and KPIs over
# the supplier register, documents, qualification/activation, scorecards, CARs,
# reviews, risk and compliance screening.
import datetime

# A06 workflow audit (2026-11-03) M42-9/M42-10: the supplier surface had no
# action at all (status was changed by typing it). Every lifecycle step is an
# action here; the forms no longer offer status, state or scores.
SURFACES = {
    # A06 S7 (M42-3): a bank-detail change is a proposal a second person
    # confirms; the supplier stays payment-blocked until then.
    "fix.supplier.bank.change": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_propose", "action_confirm", "action_reject"},
    },
    "fix.supplier": {
        "order": "name",
        "limit": 300,
        "actions": {
            "action_suspend",
            "action_block",
            "action_request_reinstatement",
            "action_approve_reinstatement",
        },
    },
    "fix.supplier.document": {
        "order": "valid_to desc, id desc",
        "limit": 400,
        "actions": {"action_verify"},
    },
    "fix.supplier.qualification": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_start", "action_approve", "action_reject"},
    },
    "fix.supplier.activation": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_activate"},
    },
    "fix.supplier.requalification": {
        "order": "due_on desc, id desc",
        "limit": 300,
        "actions": {"action_complete"},
    },
    "fix.supplier.performance": {
        "order": "period desc, id desc",
        "limit": 300,
        "actions": {"action_compute", "action_publish"},
    },
    "fix.supplier.car": {
        "order": "due_date desc, id desc",
        "limit": 300,
        "actions": {"action_action", "action_close"},
    },
    "fix.supplier.review": {
        "order": "review_date desc, id desc",
        "limit": 200,
        "actions": {"action_complete"},
    },
    "fix.supplier.risk": {
        "order": "assessed_on desc, id desc",
        "limit": 300,
        "actions": {"action_mitigate"},
    },
    "fix.supplier.screening": {
        "order": "screened_on desc, id desc",
        "limit": 300,
        "actions": {"action_clear", "action_flag", "action_clear_hit"},
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


def _mine(env, model, domain=None):
    """The caller's records (their rights), limited to their companies."""
    return env[model].search([("company_id", "in", env.companies.ids), *list(domain or [])])


def _of_my_suppliers(env, model, domain=None, order=None):
    return env[model].search(
        [("supplier_id.company_id", "in", env.companies.ids), *list(domain or [])],
        order=order,
    )


def _suppliers(env):
    return _mine(env, "fix.supplier")


def scorecard_league(env, date_from=None, date_to=None, **params):
    cards = _of_my_suppliers(
        env, "fix.supplier.performance", [("state", "=", "published")], "period desc, id desc"
    )
    latest = {}
    for card in cards:
        latest.setdefault(card.supplier_id.id, card)
    rows = []
    for card in latest.values():
        rows.append(
            {
                "supplier": card.supplier_id.name,
                "segment": dict(card.supplier_id._fields["segment"].selection).get(
                    card.supplier_id.segment
                ),
                "period": card.period,
                "quality": round(card.quality_score, 1),
                "delivery": round(card.delivery_score, 1),
                "cost": round(card.cost_score, 1),
                "responsiveness": round(card.responsiveness_score, 1),
                "total": round(card.total_score, 1),
                "grade": card.grade.upper() if card.grade else "—",
            }
        )
    rows.sort(key=lambda r: -r["total"])
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return _pack(
        "Supplier Scorecard League — latest published scorecard per supplier",
        [
            "rank",
            "supplier",
            "segment",
            "period",
            "quality",
            "delivery",
            "cost",
            "responsiveness",
            "total",
            "grade",
        ],
        {
            "rank": "#",
            "supplier": "Supplier",
            "segment": "Segment",
            "period": "Period",
            "quality": "Quality",
            "delivery": "Delivery",
            "cost": "Cost",
            "responsiveness": "Responsiveness",
            "total": "Total",
            "grade": "Grade",
        },
        rows,
        [
            "Total = quality 35% + delivery 30% + cost 20% + responsiveness 15%; "
            "the grade band is A ≥85, B ≥70, C ≥55, D below."
        ],
        empty="No published scorecards yet.",
    )


def car_closure(env, date_from=None, date_to=None, **params):
    cars = _of_my_suppliers(env, "fix.supplier.car")
    rows = []
    for car in cars:
        days = "—"
        if car.closed_on and car.raised_on:
            days = (car.closed_on - car.raised_on).days
        rows.append(
            {
                "car": car.name,
                "supplier": car.supplier_id.name,
                "severity": dict(car._fields["severity"].selection).get(car.severity),
                "raised": str(car.raised_on),
                "due": str(car.due_date),
                "closed": str(car.closed_on) if car.closed_on else "—",
                "closure_days": days,
                "overdue": car.is_overdue,
                "state": dict(car._fields["state"].selection).get(car.state),
            }
        )
    rows.sort(key=lambda r: (not r["overdue"], str(r["car"])), reverse=True)
    closed = len([r for r in rows if r["state"] == "Closed"])
    return _pack(
        "CAR Closure Performance — corrective actions by severity",
        [
            "car",
            "supplier",
            "severity",
            "raised",
            "due",
            "closed",
            "closure_days",
            "overdue",
            "state",
        ],
        {
            "car": "CAR",
            "supplier": "Supplier",
            "severity": "Severity",
            "raised": "Raised",
            "due": "Due",
            "closed": "Closed",
            "closure_days": "Closure Days",
            "overdue": "Overdue",
            "state": "State",
        },
        rows,
        ["%d of %d CARs closed; closure days = closed − raised." % (closed, len(rows))],
        empty="No corrective actions raised.",
    )


def risk_heat(env, date_from=None, date_to=None, **params):
    risks = _of_my_suppliers(env, "fix.supplier.risk")
    buckets = {}
    for risk in risks:
        key = (risk.likelihood, risk.impact, risk.band)
        row = buckets.setdefault(
            key,
            {
                "likelihood": risk.likelihood,
                "impact": risk.impact,
                "band": dict(risk._fields["band"].selection).get(risk.band),
                "risks": 0,
                "suppliers": set(),
            },
        )
        row["risks"] += 1
        row["suppliers"].add(risk.supplier_id.id)
    rows = []
    for row in buckets.values():
        row["suppliers"] = len(row["suppliers"])
        rows.append(row)
    rows.sort(key=lambda r: (-r["likelihood"], -r["impact"]))
    return _pack(
        "Risk Heat Map — likelihood × impact",
        ["likelihood", "impact", "band", "risks", "suppliers"],
        {
            "likelihood": "Likelihood",
            "impact": "Impact",
            "band": "Band",
            "risks": "Risks",
            "suppliers": "Suppliers",
        },
        rows,
        ["Score = likelihood × impact; critical ≥20, high ≥12, medium ≥6, low below."],
        totals={"band": "Total", "risks": sum(r["risks"] for r in rows)},
        empty="No supplier risk assessments yet.",
    )


def contract_coverage(env, date_from=None, date_to=None, **params):
    suppliers = _suppliers(env)
    active = suppliers.filtered(lambda s: s.status == "active")
    docs = _of_my_suppliers(
        env, "fix.supplier.document", [("doc_type", "=", "contract"), ("is_valid", "=", True)]
    )
    covered = set(docs.mapped("supplier_id").ids)
    rows = []
    for supplier in active:
        rows.append(
            {
                "supplier": supplier.name,
                "segment": dict(supplier._fields["segment"].selection).get(supplier.segment),
                "contract": "yes" if supplier.id in covered else "no",
                "status": dict(supplier._fields["status"].selection).get(supplier.status),
            }
        )
    rows.sort(key=lambda r: (r["contract"] == "yes", r["supplier"]))
    gaps = len([r for r in rows if r["contract"] == "no"])
    return _pack(
        "Contract Coverage — active suppliers with a valid contract document",
        ["supplier", "segment", "contract", "status"],
        {"supplier": "Supplier", "segment": "Segment", "contract": "Contract", "status": "Status"},
        rows,
        [
            "Coverage %d/%d active suppliers; %d gap(s). A contract counts only when "
            "the document is valid today." % (len(covered), len(active), gaps)
        ],
        empty="No active suppliers yet.",
    )


def compliance_log(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _of_my_suppliers(env, "fix.supplier.screening"):
        rows.append(
            {
                "screening": rec.name,
                "supplier": rec.supplier_id.name,
                "type": dict(rec._fields["screening_type"].selection).get(rec.screening_type),
                "result": dict(rec._fields["result"].selection).get(rec.result),
                "screened_on": str(rec.screened_on),
                "reference": rec.reference or "—",
                "state": dict(rec._fields["state"].selection).get(rec.state),
                "notes": rec.notes or "",
            }
        )
    rows.sort(key=lambda r: r["screened_on"], reverse=True)
    return _pack(
        "Compliance Screening Log — sanctions / COI / ABAC / PEP",
        ["screening", "supplier", "type", "result", "screened_on", "reference", "state", "notes"],
        {
            "screening": "Screening",
            "supplier": "Supplier",
            "type": "Type",
            "result": "Result",
            "screened_on": "Screened",
            "reference": "Reference",
            "state": "State",
            "notes": "Notes",
        },
        rows,
        [
            "A hit is never rewritten: it stays in the log, and only a Supplier Approver's "
            "clearance (with the reason) marks it cleared."
        ],
        empty="No compliance screenings recorded yet.",
    )


REPORTS = {
    "scorecard_league": scorecard_league,
    "car_closure": car_closure,
    "risk_heat": risk_heat,
    "contract_coverage": contract_coverage,
    "compliance_log": compliance_log,
}


def kpis(env):
    suppliers = _suppliers(env)
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=90)
    docs = _of_my_suppliers(env, "fix.supplier.document")
    expiring = docs.filtered(lambda d: d.valid_to and today <= d.valid_to <= horizon)
    cars = _of_my_suppliers(env, "fix.supplier.car")
    risks = _of_my_suppliers(env, "fix.supplier.risk")
    quals = _of_my_suppliers(env, "fix.supplier.qualification")
    screenings = _of_my_suppliers(env, "fix.supplier.screening")
    return {
        "active_suppliers": len(suppliers.filtered(lambda s: s.status == "active")),
        "qualified_pending": len(quals.filtered(lambda q: q.state in ("draft", "in_review"))),
        "docs_expiring_90d": len(expiring),
        "cars_open": len(cars.filtered(lambda c: c.state != "closed")),
        "risk_high": len(
            risks.filtered(lambda r: r.band in ("high", "critical") and r.state == "open")
        ),
        "screening_flags": len(screenings.filtered(lambda s: s.state == "flagged")),
    }
