# A09 · M57 Performance & Incentives — surfaces, packs and KPIs over goals,
# scorecards, review cycles, PIPs, incentive runs/lines, recognition and
# compensation bands.
import datetime

SURFACES = {
    "fix.performance.goal": {
        "order": "period desc, employee_id",
        "limit": 400,
        "actions": {"action_agree", "action_activate", "action_close"},
    },
    "fix.performance.scorecard": {
        "order": "period desc, employee_id",
        "limit": 400,
        "actions": {"action_compute_from_orders", "action_publish"},
    },
    "fix.performance.review": {
        "order": "period desc, employee_id",
        "limit": 400,
        # Calibration is decided from the approval inbox (M63), never here.
        # The line manager requests and recalls it and, from a closed
        # review, proposes compensation (narrow methods: no write ACL).
        "actions": {
            "action_start",
            "action_record_self_rating",
            "action_submit_self_assessment",
            "action_record_manager_rating",
            "action_manager_review",
            "action_request_calibration",
            "action_recall_calibration",
            "action_close",
            "action_propose_compensation",
        },
    },
    "fix.performance.pip": {
        "order": "start_date desc, id desc",
        "limit": 200,
        "actions": {"action_start", "action_close"},
    },
    "fix.performance.recognition": {
        "order": "awarded_on desc, id desc",
        "limit": 200,
        "actions": {
            "action_award",
            "action_request_approval",
            "action_recall_approval",
            "action_cancel",
        },
    },
    "fix.incentive.run": {
        "order": "period desc, id desc",
        "limit": 100,
        # I4: approval is routed to the Incentive Approver's inbox; payroll
        # (M56) picks the approved lines up. There is no "apply" any more.
        "actions": {
            "action_compute",
            "action_request_approval",
            "action_recall_approval",
            "action_reset_draft",
        },
    },
    # BRU-PIC-12: the employee disputes their own computed line.
    "fix.incentive.line": {
        "order": "run_id desc, id desc",
        "limit": 500,
        "actions": {"action_raise_dispute"},
    },
    # BRU-PIC-01/02: a version is approved by the HR Director then the CFO,
    # both from the approval inbox (M63).
    "fix.incentive.scheme": {"order": "code", "limit": 100, "actions": set()},
    "fix.incentive.scheme.version": {
        "order": "scheme_id, date_from desc, version_no desc",
        "limit": 200,
        "actions": {"action_request_approval", "action_recall_approval", "action_reset_draft"},
    },
    "fix.incentive.dispute": {
        "order": "raised_at desc, id desc",
        "limit": 300,
        "actions": {"action_uphold", "action_reject"},
    },
    "fix.incentive.clawback": {"order": "id desc", "limit": 300, "actions": set()},
    # BRU-PIC-17: the Compensation Manager decides from the approval inbox.
    "fix.compensation.proposal": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_calibration_review", "action_calibration_return", "action_withdraw"},
    },
    "fix.compensation.band": {"order": "grade", "limit": 100, "actions": set()},
    # M57-F18 / D27: the CFO tier approves an above-band gross from the M63
    # inbox; the workspace only raises, recalls or withdraws it.
    "fix.band.exception": {
        "order": "create_date desc",
        "limit": 300,
        "actions": {"action_request_approval", "action_recall_approval", "action_cancel"},
    },
    "fix.succession.plan": {"order": "position_name", "limit": 100, "actions": set()},
    # Capture audit 2026-11-17: the records the sub-module pages lacked.
    # FR-PIC-006 / BRU-PIC-04: versioned KPI definitions, approved by an HR
    # Manager who neither prepared nor submitted them.
    "fix.kpi.definition": {
        "order": "role_profile, code, date_from desc, version_no desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve", "action_reject", "action_retire"},
    },
    # FR-PIC-016/017: HR opens a cycle, which raises the reviews.
    "fix.performance.review.cycle": {
        "order": "self_deadline desc, id desc",
        "limit": 100,
        "actions": {"action_open", "action_close"},
    },
    # FR-PIC-020: only the respondent answers (narrow methods: no write ACL).
    "fix.performance.feedback": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_submit_feedback", "action_decline"},
    },
    # FR-PIC-021 / BRU-PIC-13.
    "fix.performance.calibration.session": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_start", "action_conclude"},
    },
    # FR-PIC-033/034 / BRU-PIC-10/11: decided from the approval inbox (M63).
    "fix.incentive.adjustment": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_request_approval", "action_recall_approval", "action_cancel"},
    },
    # FR-PIC-038 / BRU-PIC-17.
    "fix.compensation.cycle": {
        "order": "date_from desc, id desc",
        "limit": 100,
        "actions": {"action_open", "action_close"},
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


def rating_distribution(env, date_from=None, date_to=None, **params):
    """Rating distribution across review cycles (calibrated where present)."""
    reviews = env["fix.performance.review"].search([])
    groups = {}
    for rev in reviews:
        rating = rev.calibrated_rating or rev.manager_rating or 0.0
        band = (
            "5 - Outstanding"
            if rating >= 4.5
            else "4 - Exceeds"
            if rating >= 3.5
            else "3 - Meets"
            if rating >= 2.5
            else "2 - Below"
            if rating >= 1.5
            else "1 - Unsatisfactory"
            if rating
            else "Not rated"
        )
        groups[band] = groups.get(band, 0) + 1
    total = sum(groups.values()) or 1
    rows = [
        {"band": k, "reviews": v, "share": round(v / total * 100.0, 1)}
        for k, v in sorted(groups.items(), reverse=True)
    ]
    return _pack(
        "Rating Distribution — %d review records" % len(reviews),
        ["band", "reviews", "share"],
        {"band": "Rating Band", "reviews": "Reviews", "share": "% of Reviews"},
        rows,
        [
            "Uses the calibrated rating when present, else the manager rating; unrated rows are "
            "shown honestly in their own band."
        ],
        totals={"band": "Total", "reviews": sum(r["reviews"] for r in rows)},
        empty="No review records.",
    )


def incentive_payout(env, date_from=None, date_to=None, **params):
    """Incentive payout by run and scheme band."""
    runs = env["fix.incentive.run"].search([])
    # band_base is T5: shown only to the roles the field allows (A09 M57-06).
    sees_base = env.su or bool(env["fix.incentive.run"].fields_get(["band_base"]))
    rows = []
    for run in runs:
        lines = env["fix.incentive.line"].search([("run_id", "=", run.id)])
        rows.append(
            {
                "period": run.period,
                "band_base": round(float(run.band_base or 0.0), 2) if sees_base else "—",
                "lines": len(lines),
                "total": round(float(run.total or 0.0), 2),
                "state": dict(run._fields["state"].selection).get(run.state, run.state),
            }
        )
    return _pack(
        "Incentive Payout by Scheme",
        ["period", "band_base", "lines", "total", "state"],
        {
            "period": "Period",
            "band_base": "Band Base",
            "lines": "Lines",
            "total": "Total Payout",
            "state": "State",
        },
        rows,
        [
            "The run total is the sum of its line amounts; the band base is the scheme's base "
            "value (shown to the incentive roles only). Payroll pays approved runs only."
        ],
        totals={
            "period": "Total",
            "lines": sum(r["lines"] for r in rows),
            "total": round(sum(r["total"] for r in rows), 2),
        },
        empty="No incentive runs recorded.",
    )


def technician_scorecards(env, date_from=None, date_to=None, **params):
    """Technician scorecards: FTF, SLA, CSAT, rework and composite score."""
    cards = env["fix.performance.scorecard"].search([])
    rows = []
    for card in cards:
        rows.append(
            {
                "employee": card.employee_id.name,
                "period": card.period,
                "ftf": round((card.first_time_fix or 0.0) * 100, 1),
                "sla": round((card.sla_hit or 0.0) * 100, 1),
                "csat": round((card.csat or 0.0) * 100, 1),
                "rework": round((card.rework_rate or 0.0) * 100, 1),
                "score": round(card.score or 0.0, 3),
            }
        )
    rows.sort(key=lambda r: -r["score"])
    return _pack(
        "Technician Scorecards",
        ["employee", "period", "ftf", "sla", "csat", "rework", "score"],
        {
            "employee": "Employee",
            "period": "Period",
            "ftf": "First-Time Fix %",
            "sla": "SLA Hit %",
            "csat": "CSAT %",
            "rework": "Rework %",
            "score": "Composite",
        },
        rows,
        [
            "Composite score is the model's weighted calculation over FTF, SLA, CSAT and rework, "
            "computed from the technician's completed service orders (never typed)."
        ],
        totals={
            "employee": "Average",
            "score": round(sum(r["score"] for r in rows) / len(rows), 3) if rows else 0.0,
        },
        empty="No scorecards recorded.",
    )


def calibration_summary(env, date_from=None, date_to=None, **params):
    """Calibration summary: manager vs calibrated rating movement."""
    reviews = env["fix.performance.review"].search([])
    rows = []
    for rev in reviews:
        if not (rev.manager_rating or rev.calibrated_rating):
            continue
        rows.append(
            {
                "employee": rev.employee_id.name,
                "period": rev.period,
                "manager": rev.manager_rating or 0.0,
                "calibrated": rev.calibrated_rating or 0.0,
                "movement": round((rev.calibrated_rating or 0.0) - (rev.manager_rating or 0.0), 2),
                "state": dict(rev._fields["state"].selection).get(rev.state, rev.state),
            }
        )
    rows.sort(key=lambda r: -abs(r["movement"]))
    moved = len([r for r in rows if r["movement"]])
    return _pack(
        "Calibration Summary — %d of %d ratings moved" % (moved, len(rows)),
        ["employee", "period", "manager", "calibrated", "movement", "state"],
        {
            "employee": "Employee",
            "period": "Period",
            "manager": "Manager Rating",
            "calibrated": "Calibrated Rating",
            "movement": "Movement",
            "state": "State",
        },
        rows,
        ["Movement is calibrated minus manager rating; a non-zero row is a calibration change."],
        empty="No rated reviews to calibrate.",
    )


def pip_outcomes(env, date_from=None, date_to=None, **params):
    """PIP outcomes."""
    pips = env["fix.performance.pip"].search([])
    rows = []
    for pip in pips:
        rows.append(
            {
                "employee": pip.employee_id.name,
                "start": str(pip.start_date),
                "end": str(pip.end_date),
                "mentor": pip.mentor_id.name if pip.mentor_id else "—",
                "outcome": dict(pip._fields["outcome"].selection).get(pip.outcome, "Open"),
                "state": dict(pip._fields["state"].selection).get(pip.state, pip.state),
            }
        )
    rows.sort(key=lambda r: r["start"], reverse=True)
    improved = len([r for r in rows if r["outcome"] == "Improved"])
    return _pack(
        "PIP Outcomes — %d improved" % improved,
        ["employee", "start", "end", "mentor", "outcome", "state"],
        {
            "employee": "Employee",
            "start": "Start",
            "end": "End",
            "mentor": "Mentor",
            "outcome": "Outcome",
            "state": "State",
        },
        rows,
        ["An open PIP has no outcome yet; closing requires one (model gate)."],
        empty="No PIPs recorded.",
    )


REPORTS = {
    "rating_distribution": rating_distribution,
    "incentive_payout": incentive_payout,
    "technician_scorecards": technician_scorecards,
    "calibration_summary": calibration_summary,
    "pip_outcomes": pip_outcomes,
}


def kpis(env):
    reviews = env["fix.performance.review"].search([])
    goals = env["fix.performance.goal"].search([])
    pips = env["fix.performance.pip"].search([("state", "=", "active")])
    runs = env["fix.incentive.run"].search([])
    today = datetime.date.today()
    month = today.strftime("%Y-%m")
    approved = runs.filtered(lambda r: r.state == "approved")
    # One run per period and company: the pool is the approved run's total.
    pool_mtd = sum(float(r.total or 0.0) for r in approved if r.period == month)
    closed = len(reviews.filtered(lambda r: r.state == "closed"))
    employees = env["hr.employee"].search_count([])
    goals_active = len(goals.filtered(lambda g: g.state in ("active", "achieved", "missed")))
    return {
        "reviews_on_track": round(closed / len(reviews) * 100.0, 1) if reviews else 0.0,
        "incentive_pool_mtd": round(pool_mtd, 2),
        "goal_coverage": round(goals_active / employees * 100.0, 1) if employees else 0.0,
        "calibration_sessions": len(reviews.filtered(lambda r: r.state == "calibrated")),
        "pips_active": len(pips),
        # A09 M57-22: the share of runs that reached approval (the states the
        # model really has; it counted 'approved'/'paid' when neither existed).
        "incentive_accuracy": round(len(approved) / len(runs) * 100.0, 1) if runs else 0.0,
    }
