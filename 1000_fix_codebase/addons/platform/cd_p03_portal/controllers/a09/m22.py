# A09 · M22 Learning & Certification — surfaces, packs and KPIs over the
# competency framework, skill matrix, certifications, courses/enrolments,
# assessments, learning paths, OJT records and audit evidence.
#
# A09 R2 fixes (M22-F9, UI-F3, UI-F8, UI-F11): every pack honours the period
# the screen offers on its own business date field (an as-at snapshot says so
# and never takes a future date); the KPI formulas measure what their labels
# promise (brands, the real technician population, the configured lead time);
# "today" is the caller's Dhaka business day, never the server clock.
import datetime

from odoo import fields

SURFACES = {
    "fix.competency": {"order": "code", "limit": 300, "actions": set()},
    "fix.certification.waiver": {"order": "id desc", "limit": 300, "actions": {"action_cancel"}},
    "fix.certification": {
        "order": "expires_on",
        "limit": 500,
        # The grant is a routed request; the verifier decides it in the
        # approval inbox (M63). Suspend blocks dispatch at once.
        "actions": {
            "action_grant",
            "action_recall_approval",
            "action_renew",
            "action_suspend",
            "action_reinstate",
            "action_revoke",
            "action_mark_expired",
        },
    },
    "fix.training.course": {"order": "code", "limit": 200, "actions": {"action_enroll"}},
    "fix.training.enrollment": {
        "order": "id desc",
        "limit": 500,
        "pickers": {"session_id": [("state", "in", ("planned", "scheduled"))]},
        "actions": {
            "action_pass",
            "action_fail",
            "action_mark_attended",
            "action_mark_absent",
            # FR-LMS-021 (capture pass 2): cancellation and substitution
            "action_withdraw",
            "action_substitute",
        },
    },
    # FR-LMS-020/021/023: the scheduled delivery of a course (M22 capture
    # audit 2026-11-13: "Schedule & Attendance" had no session to capture).
    "fix.training.session": {
        "order": "date_start desc, id desc",
        "limit": 300,
        "actions": {"action_schedule", "action_mark_held", "action_cancel"},
    },
    # BRU-LMS-09: the attempt that reaches the limit is escalated; a
    # Training Manager grants the retake.
    "fix.competency.assessment": {
        "order": "assessed_on desc, id desc",
        "limit": 400,
        "actions": {"action_grant_retake"},
    },
    # BRU-LMS-10: the yearly budget, and the routed over-budget request.
    "fix.training.budget": {"order": "year desc, company_id", "limit": 50, "actions": set()},
    "fix.training.budget.exception": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_request_approval", "action_recall_approval", "action_cancel"},
    },
    # FR-LMS-002 / 005 (capture pass 2): a path is the role requirement; its
    # gaps raise training needs
    "fix.learning.path": {"order": "name", "limit": 100, "actions": {"action_raise_gap_needs"}},
    "fix.role.competency": {"order": "path_id, competency_id", "limit": 500, "actions": set()},
    # FR-LMS-031 / 032: the need register and the plan that consolidates it
    "fix.training.need": {
        "order": "raised_on desc, id desc",
        "limit": 500,
        "pickers": {"plan_id": [("state", "=", "draft")]},
        "actions": {"action_enrol", "action_cancel"},
    },
    "fix.training.plan": {
        "order": "year desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve", "action_return", "action_cancel"},
    },
    # FR-LMS-036: the trainee's own feedback on a training they attended
    "fix.training.feedback": {
        "order": "submitted_on desc, id desc",
        "limit": 500,
        "pickers": {"enrollment_id": [("state", "!=", "withdrawn")]},
        "actions": set(),
    },
    # FR-LMS-028: the mentoring and its interactions
    "fix.mentoring": {
        "order": "date_start desc, id desc",
        "limit": 300,
        "actions": {"action_start", "action_close", "action_cancel"},
    },
    "fix.mentoring.interaction": {
        "order": "date desc, id desc",
        "limit": 500,
        "pickers": {"mentoring_id": [("state", "=", "active")]},
        "actions": set(),
    },
    # FR-LMS-035 / BRU-LMS-15: before / after on the measure the training targeted
    "fix.training.effectiveness": {
        "order": "id desc",
        "limit": 300,
        "pickers": {"session_id": [("state", "=", "done")]},
        "actions": {"action_evaluate"},
    },
    "fix.ojt.record": {
        "order": "date_from desc, id desc",
        "limit": 300,
        "actions": {"action_sign_off"},
    },
    "fix.audit.evidence": {
        "order": "collected_on desc, id desc",
        "limit": 300,
        "actions": {
            "action_submit",
            "action_accept",
            "action_reject",
            "action_compile_iso_dossier",
        },
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


def _today(env):
    """UI-F8: the caller's business day (Asia/Dhaka when they set no tz) —
    the same rule m21.py uses; datetime.date.today() ran 6 h behind each
    Dhaka evening."""
    return fields.Date.context_today(env.user.with_context(tz=env.user.tz or "Asia/Dhaka"))


def _lead_days(env):
    """M22-F9: the configured alert lead time (cd_competency.expiry_lead_days,
    default 30) — the coverage report hardcoded 30."""
    raw = env["ir.config_parameter"].sudo().get_param("cd_competency.expiry_lead_days", "30")
    try:
        return max(int(raw), 0)
    except (TypeError, ValueError):
        return 30


def _as_of(date_to, env):
    """An as-at snapshot date: the period end, never a future day."""
    today = _today(env)
    return min(date_to, today) if date_to else today


def _period(date_from, date_to, env):
    """(from, to) for a flow pack: the offered period, 'to' never future for
    historical facts."""
    today = _today(env)
    start = date_from or datetime.date(1900, 1, 1)
    end = min(date_to, today) if date_to else today
    return start, end


def _technicians(env):
    """M22-F9 / UI-F11: the estate's technician population — the same rule the
    M02 dispatch suggestion uses (the Field Service / Technician group's OWN
    members, not the dispatchers/managers the group is implied into and not the
    Administrator), not a 'tech'-in-position-name guess with a silent `or 1`
    denominator."""
    group = env.ref("cd_field_service.group_fix_field_service_user", raise_if_not_found=False)
    if not group:
        return env["hr.employee"]
    users = group.sudo().user_ids.filtered(lambda u: u.active and not u.share)
    return env["hr.employee"].search([]).filtered(lambda e: e.user_id and e.user_id in users)


def certification_coverage(env, date_from=None, date_to=None, **params):
    """Certification coverage by brand/competency: valid vs expired holders.
    UI-F3: an AS-AT snapshot — certificates issued up to the period end (a
    future date is never taken), status judged at that same day. M22-F9:
    'expiring' uses the configured alert lead time, not a hardcoded 30 days."""
    as_of = _as_of(date_to, env)
    certs = env["fix.certification"].search([("issued_on", "<=", as_of)])
    lead = _lead_days(env)
    groups = {}
    for cert in certs:
        if cert.state not in ("valid", "lapsed"):
            continue  # drafts, suspensions and revocations are not coverage
        comp = cert.competency_id
        key = comp.name
        g = groups.setdefault(key, {"holders": set(), "valid": 0, "expired": 0, "expiring": 0})
        g["holders"].add(cert.employee_id.id)
        if cert.state == "lapsed" or (cert.expires_on and cert.expires_on < as_of):
            g["expired"] += 1
        elif cert.expires_on and (cert.expires_on - as_of).days <= lead:
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
        "Certification Coverage by Brand / Competency — as at %s" % as_of,
        ["competency", "holders", "valid", "expiring", "expired"],
        {
            "competency": "Competency",
            "holders": "Certified Staff",
            "valid": "Valid",
            "expiring": "Expiring %dd" % lead,
            "expired": "Expired",
        },
        rows,
        [
            "Granted certificates issued up to the as-at date, status judged at that day. A "
            "certificate counts as expired when it lapsed or its expiry date has passed; "
            "expiring means inside the configured alert lead time "
            "(cd_competency.expiry_lead_days)."
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
    """Expiry forecast: certificates expiring in the offered window (default:
    the next 180 days from today). UI-F3: a forecast, so a future period end
    is legitimate — the pack's business date is expires_on."""
    certs = env["fix.certification"].search([("expires_on", "!=", False), ("state", "=", "valid")])
    today = _today(env)
    start = date_from or today
    end = date_to or today + datetime.timedelta(days=180)
    rows = []
    for cert in certs:
        if start <= cert.expires_on <= end:
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
        "Expiry Forecast — %s to %s" % (start, end),
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
    """Training effectiveness: enrolments, completions and pass rate per
    course. UI-F3: with a period offered, an enrolment counts when its
    session ran in the window (no session: when it was completed in it)."""
    start, end = _period(date_from, date_to, env)

    def _in_period(enrolment):
        if date_from is None and date_to is None:
            return True  # no period offered: the course's whole history
        if enrolment.session_id and enrolment.session_id.date_start:
            day = fields.Date.to_date(enrolment.session_id.date_start)
        elif enrolment.completed_on:
            day = enrolment.completed_on
        else:
            return False
        return start <= day <= end

    courses = env["fix.training.course"].search([])
    rows = []
    for course in courses:
        enrolments = (
            env["fix.training.enrollment"]
            .search([("course_id", "=", course.id), ("state", "!=", "withdrawn")])
            .filtered(_in_period)
        )
        # FR-LMS-035: the evaluated before / after on the targeted measure
        evals = (
            env["fix.training.effectiveness"]
            .search([("course_id", "=", course.id), ("state", "=", "evaluated")])
            .filtered(
                lambda e: (date_from is None and date_to is None)
                or (
                    e.session_id.date_start
                    and start <= fields.Date.to_date(e.session_id.date_start) <= end
                )
            )
        )
        # A09 M22-28: the model's completion state is 'passed' ('completed'
        # never existed, so the KPI was always 0 %).
        completed = len(enrolments.filtered(lambda e: e.state == "passed"))
        total = len(enrolments)
        rows.append(
            {
                "course": course.name,
                "code": course.code,
                "enrolments": total,
                "completed": completed,
                "completion_pct": round(completed / total * 100.0, 1) if total else 0.0,
                "evaluated": len(evals),
                "improved": len(evals.filtered(lambda e: e.result == "improved")),
            }
        )
    rows.sort(key=lambda r: -r["enrolments"])
    return _pack(
        "Training Effectiveness",
        ["course", "code", "enrolments", "completed", "completion_pct", "evaluated", "improved"],
        {
            "course": "Course",
            "code": "Code",
            "enrolments": "Enrolments",
            "completed": "Completed",
            "completion_pct": "Completion %",
            "evaluated": "Evaluations",
            "improved": "Measure Improved",
        },
        rows,
        [
            "Completion counts enrolments in the passed state (withdrawn seats excluded); a "
            "course with no enrolments shows zero rather than a fabricated rate.",
            "With a period offered, an enrolment counts when its session ran in the window "
            "(no session: when it was completed in it); %s to %s." % (start, end),
            "Evaluations are effectiveness records (before / after on the operational measure "
            "the training targeted, FR-LMS-035) evaluated with a conclusion.",
        ],
        totals={
            "course": "Total",
            "enrolments": sum(r["enrolments"] for r in rows),
            "completed": sum(r["completed"] for r in rows),
            "evaluated": sum(r["evaluated"] for r in rows),
            "improved": sum(r["improved"] for r in rows),
        },
        empty="No courses recorded.",
    )


def skill_gap_heatmap(env, date_from=None, date_to=None, **params):
    """Skill-gap heatmap derived from the records that exist: valid
    certifications (L3+ evidence) and the latest PASSED assessment level per
    employee/competency (M22-F9: a failed attempt never showed a held level —
    the gap analysis requires a passed assessment, and so does the heatmap).
    UI-F3: with a period offered, only assessments assessed in it count.
    There is no separate skill-matrix model."""
    competencies = env["fix.competency"].search([])
    # A09 M22-09: only a granted certificate inside its dates counts; the
    # status is judged against today on every read.
    certs = env["fix.certification"].search([("state", "=", "valid"), ("status", "!=", "expired")])
    domain = [("passed", "=", True)]
    if date_from or date_to:
        start, end = _period(date_from, date_to, env)
        domain += [("assessed_on", ">=", start), ("assessed_on", "<=", end)]
    assessments = env["fix.competency.assessment"].search(domain, order="assessed_on desc")
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
            "evidence, and the latest PASSED assessment per employee supplies the level (a "
            "failed attempt holds no level — as the gap analysis). A competency with no "
            "assessments shows zero in the level columns (it does not invent a level)."
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
    """Audit evidence pack: evidence records with their standard clause.
    UI-F3: the pack's business date is collected_on; evidence is a fact of
    the past, so a future period end is never taken."""
    start, end = _period(date_from, date_to, env)
    domain = []
    if date_from or date_to:
        domain += [("collected_on", ">=", start), ("collected_on", "<=", end)]
    records = env["fix.audit.evidence"].search(domain)
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
        [
            "Evidence is accepted by a verifier other than its submitter, with the file "
            "attached; submitted-but-not-accepted rows remain open."
        ],
        empty="No audit evidence recorded.",
    )


def role_gap_analysis(env, date_from=None, date_to=None, **params):
    """FR-LMS-005: each employee in a role's positions against each competency
    requirement of that role in force; one row per requirement not met. Read
    as the caller, so assessment results stay S2 (BRU-LMS-12).
    UI-F3: an AS-AT snapshot — requirements in force at the period end (never
    a future day) are the ones measured."""
    as_of = _as_of(date_to, env)
    levels = {"l1": "L1", "l2": "L2", "l3": "L3", "l4": "L4"}
    rows = []
    for gap in env["fix.learning.path"].search([])._fix_gap_rows():
        req, emp = gap["requirement"], gap["employee"]
        if req.effective_from and req.effective_from > as_of:
            continue  # not yet in force on the as-at day
        rows.append(
            {
                "employee": emp.name,
                "position": emp.position_id.display_name or "",
                "role": gap["path"].target_role or gap["path"].name,
                "competency": req.competency_id.name,
                "required": levels[req.min_level],
                "held": levels.get(gap["held"], "None"),
                "gap": gap["gap"],
                "mandatory": "Yes" if req.mandatory else "No",
                "need": "Open" if gap["open_need"] else "None",
            }
        )
    rows.sort(key=lambda r: (r["mandatory"] != "Yes", -r["gap"], r["employee"]))
    return _pack(
        "Role Gap Analysis — requirements in force as at %s" % as_of,
        [
            "employee",
            "position",
            "role",
            "competency",
            "required",
            "held",
            "gap",
            "mandatory",
            "need",
        ],
        {
            "employee": "Employee",
            "position": "Position",
            "role": "Role / Path",
            "competency": "Competency",
            "required": "Required",
            "held": "Held",
            "gap": "Gap (levels)",
            "mandatory": "Mandatory",
            "need": "Training Need",
        },
        rows,
        [
            "Held = the latest passed assessment by an independent assessor; a granted "
            "certification in date counts as L3. A learning path measures the employees in "
            "its Applies-to-Positions against its competency requirements in force on the "
            "as-at day (a future period end is never taken).",
            "Raise Training Needs from Gaps on the Learning Paths list opens a need for "
            "every gap that has none.",
        ],
        totals={"employee": "Total gaps: %d" % len(rows)},
        empty="No gaps: every measured employee meets the requirements, or no learning path "
        "names its positions and requirements yet.",
    )


def gate_readiness(env, date_from=None, date_to=None, **params):
    """M22-F2 readiness: the dispatch gate is only as good as its config.
    One row per fix.device device type: is any dispatch-gating competency
    scoped to it, and does that competency carry a repair tier (M22-F3: a
    tier-less gating competency lets an un-tiered certification satisfy no
    tiered job — every tiered gate refuses until it is tiered)? An as-at
    snapshot (the competency register in force now)."""
    today = _today(env)
    gating = env["fix.competency"].search([("required_for_dispatch", "=", True)])
    # fix.device.device_type is a RELATED selection: its own `selection` is
    # empty, so _description_selection on it returns [] and the pack listed no
    # device type at all. Read the source field on fix.device.model instead.
    # Odoo's Environment has no .get(): the membership lookup is the one that
    # works (ruff SIM401's env.get() suggestion would AttributeError).
    has_device = "fix.device" in env
    device_model = env["fix.device"] if has_device else None
    field = device_model._fields.get("device_type") if device_model else None
    selection = field._description_selection(env) if field else []
    if not selection and "fix.device.model" in env:
        field = env["fix.device.model"]._fields.get("device_type")
        selection = field._description_selection(env) if field else []
    rows = []
    for key, label in selection:
        comps = gating.filtered(
            lambda c, k=key: (c.device_type and k in [t.strip() for t in c.device_type.split(",")])
            or (c.device_category_id and c.device_category_id.code == k)
        )
        unscoped_tier = comps.filtered(lambda c: not c.repair_tier)
        rows.append(
            {
                "device_type": "%s (%s)" % (key, label) if label else key,
                "gating_competencies": len(comps),
                "without_tier": len(unscoped_tier),
                "state": (
                    "Gated"
                    if comps and not unscoped_tier
                    else (
                        "Gated, tier missing"
                        if comps
                        else "UNGATED (fail-closed on M02" ", fail-open on M31 until the switch)"
                    )
                ),
            }
        )
    return _pack(
        "Dispatch Gate Readiness — as at %s" % today,
        ["device_type", "gating_competencies", "without_tier", "state"],
        {
            "device_type": "Device Type",
            "gating_competencies": "Gating Competencies",
            "without_tier": "Without Repair Tier",
            "state": "Gate State",
        },
        rows,
        [
            "M22-F2/F3: a device type with no dispatch-gating competency is refused by the "
            "M02 work-order gate (fail-closed) but PASSES the M31 bench gate while "
            "cd_competency.workshop_gate_fail_closed is off (the COO ruling is open). A "
            "gating competency with no repair tier lets no tiered job pass (M22-F3)."
        ],
        totals={
            "device_type": "Total ungated",
            "gating_competencies": sum(r["gating_competencies"] for r in rows),
            "without_tier": sum(r["without_tier"] for r in rows),
            "state": "%d of %d"
            % (sum(1 for r in rows if r["state"].startswith("UNGATED")), len(rows)),
        },
        empty="No device types defined.",
    )


REPORTS = {
    "role_gap_analysis": role_gap_analysis,
    "certification_coverage": certification_coverage,
    "expiry_forecast": expiry_forecast,
    "training_effectiveness": training_effectiveness,
    "skill_gap_heatmap": skill_gap_heatmap,
    "audit_evidence": audit_evidence_pack,
    "gate_readiness": gate_readiness,
}


def kpis(env):
    today = _today(env)
    certs = env["fix.certification"].search([("state", "in", ("valid", "lapsed"))])
    certified = {
        c.employee_id.id
        for c in certs
        if c.state == "valid" and (not c.expires_on or c.expires_on >= today)
    }
    expiring = len(
        [
            c
            for c in certs
            if c.expires_on and today <= c.expires_on <= today + datetime.timedelta(days=30)
        ]
    )
    expired_working = len(
        {
            c.employee_id.id
            for c in certs
            if c.state == "lapsed" or (c.expires_on and c.expires_on < today)
        }
    )
    assessments = env["fix.competency.assessment"].search([])
    passed = len(assessments.filtered(lambda a: a.passed))
    ojt = env["fix.ojt.record"].search([])
    # M22-F9 / UI-F11: the denominator is the estate's technician population
    # (the M02 dispatch pool, as the M21 'Technicians' KPI), not a
    # 'tech'-in-position-name guess; with no technicians the honest answer is
    # 0, not a division by a silent 1.
    technicians = len(_technicians(env))
    hours = sum(float(r.hours or 0.0) for r in ojt) / technicians if technicians else 0.0
    # M22-F9: 'Brand Certifications' counted distinct competencies; it counts
    # the DISTINCT BRANDS the held certifications name (cert brand, else the
    # competency's OEM scope).
    brands = len({b.id for b in (c.brand_id or c.competency_id.brand_id for c in certs) if b})
    return {
        "certified_technicians": len(certified),
        "expiring_30d": expiring,
        "expired_working": expired_working,
        "training_hours": round(hours, 1),
        "brand_certifications": brands,
        "assessment_pass_rate": round(passed / len(assessments) * 100.0, 1) if assessments else 0.0,
    }
