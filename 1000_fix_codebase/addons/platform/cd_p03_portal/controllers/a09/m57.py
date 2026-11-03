# A09 · M57 Performance & Incentives — surfaces, packs and KPIs over goals,
# scorecards, review cycles, PIPs, incentive runs/lines, recognition and
# compensation bands.
import datetime

SURFACES = {
    "fix.performance.goal": {
        "order": "period desc, employee_id",
        "limit": 400,
        "actions": {"action_activate", "action_close"},
    },
    "fix.performance.scorecard": {
        "order": "period desc, employee_id",
        "limit": 400,
        "actions": {"action_publish"},
    },
    "fix.performance.review": {
        "order": "period desc, employee_id",
        "limit": 400,
        "actions": {"action_manager_review", "action_calibrate", "action_close"},
    },
    "fix.performance.pip": {
        "order": "start_date desc, id desc",
        "limit": 200,
        "actions": {"action_start", "action_close"},
    },
    "fix.performance.recognition": {
        "order": "awarded_on desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.incentive.run": {
        "order": "period desc, id desc",
        "limit": 100,
        "actions": {"action_compute", "action_apply"},
    },
    "fix.incentive.line": {"order": "run_id desc, id desc", "limit": 500, "actions": set()},
    "fix.compensation.band": {"order": "grade", "limit": 100, "actions": set()},
    "fix.succession.plan": {"order": "position_name", "limit": 100, "actions": set()},
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
    rows = []
    for run in runs:
        lines = env["fix.incentive.line"].search([("run_id", "=", run.id)])
        rows.append(
            {
                "period": run.period,
                "band_base": round(float(run.band_base or 0.0), 2),
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
        ["The run total is the sum of its line amounts; the band base is the scheme's base value."],
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
        ["Composite score is the model's weighted calculation over FTF, SLA, CSAT and rework."],
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
    pool_mtd = sum(float(r.total or 0.0) for r in runs if r.period == month)
    closed = len(reviews.filtered(lambda r: r.state == "closed"))
    employees = env["hr.employee"].search_count([])
    goals_active = len(goals.filtered(lambda g: g.state in ("active", "achieved", "missed")))
    return {
        "reviews_on_track": round(closed / len(reviews) * 100.0, 1) if reviews else 0.0,
        "incentive_pool_mtd": round(pool_mtd, 2),
        "goal_coverage": round(goals_active / employees * 100.0, 1) if employees else 0.0,
        "calibration_sessions": len(reviews.filtered(lambda r: r.state == "calibrated")),
        "pips_active": len(pips),
        "incentive_accuracy": round(
            len(runs.filtered(lambda r: r.state in ("approved", "paid"))) / len(runs) * 100.0, 1
        )
        if runs
        else 0.0,
    }
