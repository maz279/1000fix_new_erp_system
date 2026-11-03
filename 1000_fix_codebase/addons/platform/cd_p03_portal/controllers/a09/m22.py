# A09 · M22 Learning & Certification — surfaces, packs and KPIs over the
# competency framework, skill matrix, certifications, courses/enrolments,
# assessments, learning paths, OJT records and audit evidence.
import datetime

SURFACES = {
    "fix.competency": {"order": "code", "limit": 300, "actions": set()},
    "fix.certification": {
        "order": "expires_on",
        "limit": 500,
        "actions": {"action_grant", "action_mark_expired"},
    },
    "fix.training.course": {"order": "code", "limit": 200, "actions": {"action_enroll"}},
    "fix.training.enrollment": {
        "order": "id desc",
        "limit": 500,
        "actions": {"action_pass"},
    },
    "fix.competency.assessment": {
        "order": "assessed_on desc, id desc",
        "limit": 400,
        "actions": set(),
    },
    "fix.learning.path": {"order": "name", "limit": 100, "actions": set()},
    "fix.ojt.record": {"order": "date_from desc, id desc", "limit": 300, "actions": set()},
    "fix.audit.evidence": {
        "order": "collected_on desc, id desc",
        "limit": 300,
        "actions": {"action_submit", "action_accept", "action_compile_iso_dossier"},
    },
    "fix.device.category": {"order": "code", "limit": 200, "actions": set()},
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


def _today():
    return datetime.date.today()


def certification_coverage(env, date_from=None, date_to=None, **params):
    """Certification coverage by brand/competency: valid vs expired holders."""
    certs = env["fix.certification"].search([])
    today = _today()
    groups = {}
    for cert in certs:
        comp = cert.competency_id
        key = comp.name
        g = groups.setdefault(key, {"holders": set(), "valid": 0, "expired": 0, "expiring": 0})
        g["holders"].add(cert.employee_id.id)
        if cert.expires_on and cert.expires_on < today:
            g["expired"] += 1
        elif cert.expires_on and (cert.expires_on - today).days <= 30:
            g["expiring"] += 1
        else:
            g["valid"] += 1
    rows = [
        {
            "competency": k,
            "holders": len(v["holders"]),
            "valid": v["valid"],
            "expiring": v["expiring"],
            "expired": v["expired"],
        }
        for k, v in sorted(groups.items())
    ]
    return _pack(
        "Certification Coverage by Brand / Competency",
        ["competency", "holders", "valid", "expiring", "expired"],
        {
            "competency": "Competency",
            "holders": "Certified Staff",
            "valid": "Valid",
            "expiring": "Expiring 30d",
            "expired": "Expired",
        },
        rows,
        [
            "A certificate counts as expired when its expiry date has passed; expiring means "
            "inside the next 30 days."
        ],
        totals={
            "competency": "Total",
            "holders": sum(r["holders"] for r in rows),
            "valid": sum(r["valid"] for r in rows),
            "expiring": sum(r["expiring"] for r in rows),
            "expired": sum(r["expired"] for r in rows),
        },
        empty="No certifications recorded.",
    )


def expiry_forecast(env, date_from=None, date_to=None, **params):
    """Expiry forecast: certificates expiring in the next 180 days, by month."""
    certs = env["fix.certification"].search([("expires_on", "!=", False)])
    today = _today()
    horizon = today + datetime.timedelta(days=180)
    rows = []
    for cert in certs:
        if today <= cert.expires_on <= horizon:
            rows.append(
                {
                    "employee": cert.employee_id.name,
                    "competency": cert.competency_id.name,
                    "expires_on": str(cert.expires_on),
                    "days_left": (cert.expires_on - today).days,
                    "status": dict(cert._fields["status"].selection).get(cert.status, cert.status),
                }
            )
    rows.sort(key=lambda r: r["days_left"])
    return _pack(
        "Expiry Forecast — next 180 days",
        ["employee", "competency", "expires_on", "days_left", "status"],
        {
            "employee": "Employee",
            "competency": "Competency",
            "expires_on": "Expires On",
            "days_left": "Days Left",
            "status": "Status",
        },
        rows,
        [
            "Renewal action is needed before days-left reaches zero; the dispatch block uses the "
            "same expiry data."
        ],
        empty="No certifications expiring in the next 180 days.",
    )


def training_effectiveness(env, date_from=None, date_to=None, **params):
    """Training effectiveness: enrolments, completions and pass rate per course."""
    courses = env["fix.training.course"].search([])
    rows = []
    for course in courses:
        enrolments = env["fix.training.enrollment"].search([("course_id", "=", course.id)])
        completed = len(enrolments.filtered(lambda e: e.state == "completed"))
        total = len(enrolments)
        rows.append(
            {
                "course": course.name,
                "code": course.code,
                "enrolments": total,
                "completed": completed,
                "completion_pct": round(completed / total * 100.0, 1) if total else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["enrolments"])
    return _pack(
        "Training Effectiveness",
        ["course", "code", "enrolments", "completed", "completion_pct"],
        {
            "course": "Course",
            "code": "Code",
            "enrolments": "Enrolments",
            "completed": "Completed",
            "completion_pct": "Completion %",
        },
        rows,
        [
            "Completion counts enrolments in the completed state; a course with no enrolments "
            "shows zero rather than a fabricated rate."
        ],
        totals={
            "course": "Total",
            "enrolments": sum(r["enrolments"] for r in rows),
            "completed": sum(r["completed"] for r in rows),
        },
        empty="No courses recorded.",
    )


def skill_gap_heatmap(env, date_from=None, date_to=None, **params):
    """Skill-gap heatmap derived from the records that exist: valid
    certifications (L3+ evidence) and the latest assessment level per
    employee/competency. There is no separate skill-matrix model."""
    competencies = env["fix.competency"].search([])
    certs = env["fix.certification"].search([("status", "!=", "expired")])
    assessments = env["fix.competency.assessment"].search([], order="assessed_on desc")
    rows = []
    for comp in competencies:
        held = certs.filtered(lambda c, cid=comp.id: c.competency_id.id == cid)
        certified = len({c.employee_id.id for c in held})
        assessed = assessments.filtered(lambda a, cid=comp.id: a.competency_id.id == cid)
        by_level = {"l1": 0, "l2": 0, "l3": 0, "l4": 0}
        seen = set()
        for assessment in assessed:  # newest first: first row per employee wins
            if assessment.employee_id.id in seen:
                continue
            seen.add(assessment.employee_id.id)
            level = assessment.level if assessment.level in by_level else "l2"
            by_level[level] += 1
        rows.append(
            {
                "competency": comp.name,
                "code": comp.code,
                "certified": certified,
                "l1": by_level["l1"],
                "l2": by_level["l2"],
                "l3": by_level["l3"],
                "l4": by_level["l4"],
                "gap_below_l3": by_level["l1"] + by_level["l2"],
                "dispatch_required": "Yes" if comp.required_for_dispatch else "No",
            }
        )
    rows.sort(key=lambda r: -r["gap_below_l3"])
    return _pack(
        "Skill-Gap Heatmap — certified staff and assessed levels per competency",
        [
            "competency",
            "code",
            "certified",
            "l1",
            "l2",
            "l3",
            "l4",
            "gap_below_l3",
            "dispatch_required",
        ],
        {
            "competency": "Competency",
            "code": "Code",
            "certified": "Valid Certificates",
            "l1": "L1",
            "l2": "L2",
            "l3": "L3",
            "l4": "L4",
            "gap_below_l3": "Gap (below L3)",
            "dispatch_required": "Dispatch Required",
        },
        rows,
        [
            "The heatmap is built from the records that exist: valid certifications count as L3+ "
            "evidence, and the latest assessment per employee supplies the level. A competency "
            "with no assessments shows zero in the level columns (it does not invent a level)."
        ],
        totals={
            "competency": "Total",
            "certified": sum(r["certified"] for r in rows),
            "l1": sum(r["l1"] for r in rows),
            "l2": sum(r["l2"] for r in rows),
            "l3": sum(r["l3"] for r in rows),
            "l4": sum(r["l4"] for r in rows),
            "gap_below_l3": sum(r["gap_below_l3"] for r in rows),
        },
        empty="No competencies defined.",
    )


def audit_evidence_pack(env, date_from=None, date_to=None, **params):
    """Audit evidence pack: evidence records with their standard clause."""
    records = env["fix.audit.evidence"].search([])
    rows = []
    for rec in records:
        rows.append(
            {
                "reference": rec.name,
                "type": dict(rec._fields["evidence_type"].selection).get(rec.evidence_type),
                "clause": rec.standard_ref or "—",
                "collected_on": str(rec.collected_on),
                "valid_until": str(rec.valid_until or "—"),
                "state": dict(rec._fields["state"].selection).get(rec.state, rec.state),
            }
        )
    rows.sort(key=lambda r: r["collected_on"], reverse=True)
    accepted = len([r for r in rows if r["state"] == "Accepted"])
    return _pack(
        "Audit Evidence Pack — %d accepted of %d" % (accepted, len(rows)),
        ["reference", "type", "clause", "collected_on", "valid_until", "state"],
        {
            "reference": "Reference",
            "type": "Evidence Type",
            "clause": "Standard / Requirement",
            "collected_on": "Collected",
            "valid_until": "Valid Until",
            "state": "State",
        },
        rows,
        ["Evidence is accepted by the auditor role; submitted-but-not-accepted rows remain open."],
        empty="No audit evidence recorded.",
    )


REPORTS = {
    "certification_coverage": certification_coverage,
    "expiry_forecast": expiry_forecast,
    "training_effectiveness": training_effectiveness,
    "skill_gap_heatmap": skill_gap_heatmap,
    "audit_evidence": audit_evidence_pack,
}


def kpis(env):
    today = _today()
    certs = env["fix.certification"].search([])
    employees = env["hr.employee"].search([])
    certified = {c.employee_id.id for c in certs if not c.expires_on or c.expires_on >= today}
    expiring = len(
        [
            c
            for c in certs
            if c.expires_on and today <= c.expires_on <= today + datetime.timedelta(days=30)
        ]
    )
    expired_working = len(
        {c.employee_id.id for c in certs if c.expires_on and c.expires_on < today}
    )
    assessments = env["fix.competency.assessment"].search([])
    passed = len(assessments.filtered(lambda a: a.passed))
    ojt = env["fix.ojt.record"].search([])
    technicians = (
        len(
            [e for e in employees if e.position_id and "tech" in (e.position_id.name or "").lower()]
        )
        or 1
    )
    hours = sum(float(r.hours or 0.0) for r in ojt) / technicians
    brands = len({c.competency_id.id for c in certs})
    return {
        "certified_technicians": len(certified),
        "expiring_30d": expiring,
        "expired_working": expired_working,
        "training_hours": round(hours, 1),
        "brand_certifications": brands,
        "assessment_pass_rate": round(passed / len(assessments) * 100.0, 1) if assessments else 0.0,
    }
