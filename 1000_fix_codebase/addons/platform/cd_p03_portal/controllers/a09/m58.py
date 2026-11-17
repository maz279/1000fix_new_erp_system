# A09 · M58 Talent Acquisition — surfaces, packs and KPIs over requisitions,
# candidates, interviews, practical assessments, checks, offers and first-90
# reviews.

# A09 workflow audit (M58-F1..F5): "Approve Requisition", "Mark Clear" and
# "Issue Offer" were the maker's own buttons. Approvals are now requested here
# and decided from the M63 inbox by someone else; the apply methods
# (action_approve, action_clear, action_issue) are not offered on the screens.
from odoo import fields

SURFACES = {
    "fix.job.requisition": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_request_approval", "action_recall_approval", "action_close"},
    },
    "fix.candidate": {
        "order": "id desc",
        "limit": 500,
        "actions": {
            "action_screen",
            "action_interview",
            "action_offer",
            "action_reject",
            "action_hire",
        },
    },
    "fix.talent.interview": {
        "order": "scheduled_on desc, id desc",
        "limit": 400,
        "actions": {
            "action_add_panelist",
            "action_remove_panelist",
            "action_done",
            "action_cancel",
        },
    },
    "fix.talent.assessment": {"order": "assessed_on desc, id desc", "limit": 400, "actions": set()},
    "fix.talent.check": {
        "order": "id desc",
        "limit": 400,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_mark_failed",
            "action_mark_discrepancy",
        },
    },
    "fix.talent.offer": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_accept",
            "action_decline",
        },
    },
    "fix.onboarding.plan": {
        "order": "joined_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_start",
            "action_complete",
            "action_acknowledge_appointment",
            "action_attest_signed_appointment",
        },
    },
    "fix.talent.first90": {"order": "check_date desc, id desc", "limit": 300, "actions": set()},
    # Round 2 (BRU-TAO-07): a panelist's own evaluation, private until the
    # whole panel has submitted (record rules).
    "fix.talent.evaluation": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_submit"},
    },
    # Round 2 (BRU-TAO-01): the approved headcount budget, decided by the CFO tier.
    "fix.headcount.budget": {
        "order": "year desc, id desc",
        "limit": 300,
        "actions": {"action_request_approval", "action_recall_approval", "action_close"},
    },
    # Round 2 (FR-TAO-027): onboarding tasks with owners, due dates and evidence.
    "fix.onboarding.task": {
        "order": "due_date, id",
        "limit": 500,
        "actions": {"action_done", "action_cancel"},
    },
    # Capture audit 2026-11-17: the records the M58 pages cover.
    "fix.job.profile": {"order": "name", "limit": 300, "actions": set()},
    "fix.job.posting": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_publish", "action_close"},
    },
    "fix.talent.referral": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_approve_reward", "action_decline_reward"},
    },
    "fix.recruitment.channel": {"order": "name", "limit": 200, "actions": set()},
    "fix.recruitment.cost": {"order": "incurred_on desc, id desc", "limit": 400, "actions": set()},
    # candidate biodata standard (18 Nov 2026): the evidence a candidate gives,
    # decided by a Background Verifier who did not key or upload it
    "fix.candidate.document": {
        "order": "candidate_id desc, id",
        "limit": 500,
        "actions": {"action_verify", "action_flag_discrepancy"},
    },
    "fix.candidate.education": {
        "order": "candidate_id desc, id",
        "limit": 500,
        "actions": {"action_verify", "action_flag_discrepancy"},
    },
    "fix.candidate.experience": {
        "order": "candidate_id desc, id",
        "limit": 500,
        "actions": {"action_verify", "action_flag_discrepancy"},
    },
    "fix.candidate.training": {
        "order": "candidate_id desc, id",
        "limit": 500,
        "actions": {"action_verify", "action_flag_discrepancy"},
    },
    "fix.preboarding.document": {
        "order": "plan_id, id",
        "limit": 500,
        "actions": {"action_verify", "action_reject"},
    },
    "fix.onboarding.induction": {
        "order": "scheduled_at, id",
        "limit": 400,
        "actions": {"action_mark_attended", "action_mark_missed", "action_cancel"},
    },
    "fix.onboarding.template": {"order": "name", "limit": 100, "actions": set()},
    "fix.onboarding.template.line": {
        "order": "template_id, sequence, id",
        "limit": 400,
        "actions": set(),
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


def funnel_conversion(env, date_from=None, date_to=None, **params):
    """Funnel & conversion: candidates by pipeline stage."""
    candidates = env["fix.candidate"].search([])
    stages = [
        ("applied", "Applied"),
        ("screening", "Screening"),
        ("interview", "Interview"),
        ("offered", "Offered"),
        ("hired", "Hired"),
        ("rejected", "Rejected"),
    ]
    counts = {k: len(candidates.filtered(lambda c, kk=k: c.state == kk)) for k, _ in stages}
    base = counts["applied"] or len(candidates) or 1
    rows = [
        {"stage": label, "candidates": counts[key], "share": round(counts[key] / base * 100.0, 1)}
        for key, label in stages
    ]
    return _pack(
        "Funnel & Conversion — %d candidates" % len(candidates),
        ["stage", "candidates", "share"],
        {"stage": "Stage", "candidates": "Candidates", "share": "% of Applied"},
        rows,
        [
            "Shares are over the applied pool; a stage further down with more people than a "
            "stage above it means candidates skipped a step (shown as measured)."
        ],
        totals={"stage": "Total", "candidates": len(candidates)},
        empty="No candidates recorded.",
    )


def time_to_fill(env, date_from=None, date_to=None, **params):
    """Time to fill by requisition, from opened to first hire."""
    reqs = env["fix.job.requisition"].search([])
    candidates = env["fix.candidate"].search([("state", "=", "hired")])
    rows = []
    for req in reqs:
        hired = candidates.filtered(lambda c, r=req.id: c.requisition_id.id == r)
        opened = req.create_date.date() if req.create_date else None
        # the hire is stamped when it happens (hired_on), not when the
        # candidate was keyed in
        first_hire = (
            min((c.hired_on or c.create_date for c in hired), default=None) if hired else None
        )
        days = (first_hire.date() - opened).days if (opened and first_hire) else None
        rows.append(
            {
                "requisition": req.name,
                "openings": req.openings,
                "hired": len(hired),
                "state": dict(req._fields["state"].selection).get(req.state, req.state),
                "days_to_fill": days if days is not None else "Not filled",
            }
        )
    rows.sort(key=lambda r: (r["days_to_fill"] == "Not filled", r["days_to_fill"]))
    return _pack(
        "Time-to-Fill by Role",
        ["requisition", "openings", "hired", "state", "days_to_fill"],
        {
            "requisition": "Requisition",
            "openings": "Openings",
            "hired": "Hired",
            "state": "State",
            "days_to_fill": "Days to Fill",
        },
        rows,
        [
            "Days to fill is from the requisition's creation to the first hired candidate; "
            "unfilled requisitions say so instead of showing a number."
        ],
        empty="No requisitions recorded.",
    )


def source_effectiveness(env, date_from=None, date_to=None, **params):
    """Source effectiveness: applications and hires by the candidate's channel."""
    candidates = env["fix.candidate"].search([])
    labels = dict(env["fix.candidate"]._fields["source"].selection)
    groups = {}
    for cand in candidates:
        key = labels.get(cand.source, "Not recorded")
        g = groups.setdefault(key, {"applied": 0, "hired": 0})
        g["applied"] += 1
        if cand.state == "hired":
            g["hired"] += 1
    rows = [
        {
            "source": k,
            "applied": v["applied"],
            "hired": v["hired"],
            "conversion": round(v["hired"] / v["applied"] * 100.0, 1) if v["applied"] else 0.0,
        }
        for k, v in sorted(groups.items())
    ]
    return _pack(
        "Source Effectiveness",
        ["source", "applied", "hired", "conversion"],
        {"source": "Source", "applied": "Applied", "hired": "Hired", "conversion": "Hire Rate %"},
        rows,
        ["Grouped by the channel recorded on each candidate."],
        totals={
            "source": "Total",
            "applied": sum(r["applied"] for r in rows),
            "hired": sum(r["hired"] for r in rows),
        },
        empty="No candidates recorded.",
    )


def first90_retention(env, date_from=None, date_to=None, **params):
    """First-90 retention: reviews and whether the hire is on track."""
    reviews = env["fix.talent.first90"].search([])
    rows = []
    for rev in reviews:
        rows.append(
            {
                "employee": rev.employee_id.name,
                "milestone": dict(rev._fields["milestone"].selection).get(rev.milestone),
                "check_date": str(rev.check_date),
                "rating": rev.rating or 0.0,
                "on_track": "Yes" if rev.on_track else "No",
            }
        )
    rows.sort(key=lambda r: r["check_date"], reverse=True)
    on_track = len([r for r in rows if r["on_track"] == "Yes"])
    return _pack(
        "First-90 Retention — %d of %d on track" % (on_track, len(rows)),
        ["employee", "milestone", "check_date", "rating", "on_track"],
        {
            "employee": "Employee",
            "milestone": "Milestone",
            "check_date": "Check Date",
            "rating": "Rating",
            "on_track": "On Track",
        },
        rows,
        [
            "A hire with no review recorded is not counted as retained or lost — only recorded "
            "reviews appear."
        ],
        empty="No first-90 reviews recorded.",
    )


def practical_results(env, date_from=None, date_to=None, **params):
    """Practical assessment results per candidate."""
    assessments = env["fix.talent.assessment"].search([])
    rows = []
    for a in assessments:
        rows.append(
            {
                "candidate": a.candidate_id.name,
                "competency": a.competency_code or "—",
                "assessed_on": str(a.assessed_on),
                "score": round(a.score or 0.0, 1),
                "passed": "Yes" if a.passed else "No",
                "assessor": a.assessor_id.name if a.assessor_id else "—",
            }
        )
    rows.sort(key=lambda r: -r["score"])
    passed = len([r for r in rows if r["passed"] == "Yes"])
    return _pack(
        "Practical Assessment Results — %d of %d passed" % (passed, len(rows)),
        ["candidate", "competency", "assessed_on", "score", "passed", "assessor"],
        {
            "candidate": "Candidate",
            "competency": "Competency",
            "assessed_on": "Assessed",
            "score": "Score %",
            "passed": "Passed",
            "assessor": "Assessor",
        },
        rows,
        [
            "Score is the recorded 0–100 percentage; passed means the score reached the "
            "requisition's approved pass mark."
        ],
        empty="No practical assessments recorded.",
    )


def cost_per_hire(env, date_from=None, date_to=None, **params):
    """Recruitment cost per hire, by requisition (FR-TAO-034)."""
    costs = env["fix.recruitment.cost"].search([])
    hired = env["fix.candidate"].search([("state", "=", "hired")])
    by_req = {}
    for cost in costs:
        row = by_req.setdefault(cost.requisition_id.id, {"req": cost.requisition_id, "cost": 0.0})
        row["cost"] += cost.amount or 0.0
    rows = []
    for row in by_req.values():
        hires = len(hired.filtered(lambda c, r=row["req"].id: c.requisition_id.id == r))
        rows.append(
            {
                "requisition": row["req"].name,
                "cost": round(row["cost"], 2),
                "hires": hires,
                "cost_per_hire": round(row["cost"] / hires, 2) if hires else "No hire yet",
            }
        )
    rows.sort(key=lambda r: -r["cost"])
    total = round(sum(r["cost"] for r in rows), 2)
    total_hires = sum(r["hires"] for r in rows)
    return _pack(
        "Cost per Hire",
        ["requisition", "cost", "hires", "cost_per_hire"],
        {
            "requisition": "Requisition",
            "cost": "Recruitment Cost",
            "hires": "Hires",
            "cost_per_hire": "Cost per Hire",
        },
        rows,
        [
            "Costs are those recorded against each requisition (advertising, agency fees, "
            "checks, travel); a requisition with no hire yet shows its cost without a rate."
        ],
        totals={
            "requisition": "Total",
            "cost": total,
            "hires": total_hires,
            "cost_per_hire": round(total / total_hires, 2) if total_hires else "",
        },
        empty="No recruitment cost recorded.",
    )


def day_one_readiness(env, date_from=None, date_to=None, **params):
    """Onboarding plans not yet complete, with what is still missing (FR-TAO-033)."""
    plans = env["fix.onboarding.plan"].search([("state", "in", ("draft", "in_progress"))])
    today = fields.Date.context_today(env.user)
    rows = []
    for plan in plans:
        problems = plan.sudo()._fix_completion_problems()
        rows.append(
            {
                "plan": plan.name,
                "joining": str(plan.joined_date),
                "days_to_start": (plan.joined_date - today).days if plan.joined_date else "",
                "outstanding": len(problems),
                "missing": "; ".join(problems) or "Ready",
            }
        )
    rows.sort(key=lambda r: r["days_to_start"] if r["days_to_start"] != "" else 9999)
    ready = len([r for r in rows if not r["outstanding"]])
    return _pack(
        "Day-One Readiness - %d of %d ready" % (ready, len(rows)),
        ["plan", "joining", "days_to_start", "outstanding", "missing"],
        {
            "plan": "Onboarding Plan",
            "joining": "Joining Date",
            "days_to_start": "Days to Start",
            "outstanding": "Items Outstanding",
            "missing": "What Is Missing",
        },
        rows,
        [
            "Every open onboarding plan, nearest start date first. What is missing is the "
            "same list that stops the onboarding from completing."
        ],
        empty="No onboarding plan is open.",
    )


REPORTS = {
    "cost_per_hire": cost_per_hire,
    "day_one_readiness": day_one_readiness,
    "funnel_conversion": funnel_conversion,
    "time_to_fill": time_to_fill,
    "source_effectiveness": source_effectiveness,
    "first90_retention": first90_retention,
    "practical_results": practical_results,
}


def kpis(env):
    reqs = env["fix.job.requisition"].search([])
    candidates = env["fix.candidate"].search([])
    # Offers are HR-manager data: a recruiter sees the pipeline KPIs without
    # them instead of losing every KPI to an AccessError.
    can_offers = env["fix.talent.offer"].has_access("read")
    offers = env["fix.talent.offer"].search([]) if can_offers else env["fix.talent.offer"]
    hired = candidates.filtered(lambda c: c.state == "hired")
    accepted = offers.filtered(lambda o: o.state == "accepted")
    issued = offers.filtered(lambda o: o.state in ("issued", "accepted", "declined"))
    reviews = env["fix.talent.first90"].search([])
    on_track = len(reviews.filtered(lambda r: r.on_track))
    # Real time-to-fill: average days from requisition creation to its first hire.
    fill_days = []
    for req in reqs:
        req_hired = hired.filtered(lambda c, r=req.id: c.requisition_id.id == r)
        if req_hired and req.create_date:
            first = min(c.hired_on or c.create_date for c in req_hired)
            fill_days.append((first.date() - req.create_date.date()).days)
    return {
        "open_requisitions": len(reqs.filtered(lambda r: r.state == "open")),
        "time_to_fill": round(sum(fill_days) / len(fill_days), 1) if fill_days else None,
        "pipeline": len(
            candidates.filtered(lambda c: c.state in ("applied", "screening", "interview"))
        ),
        "offer_accept_rate": (round(len(accepted) / len(issued) * 100.0, 1) if issued else 0.0)
        if can_offers
        else None,
        "referral_share": round(
            len(candidates.filtered(lambda c: c.source == "referral")) / len(candidates) * 100.0,
            1,
        )
        if candidates
        else 0.0,
        "first90_retention": round(on_track / len(reviews) * 100.0, 1) if reviews else 0.0,
    }
