# A12 · M30 Platform Administration — surfaces, packs and KPIs over branches,
# entities, config parameters, feature flags, zones, calendars, country packs
# and announcements.
import datetime

SURFACES = {
    "fix.branch": {"order": "name", "limit": 300, "actions": set()},
    "fix.entity": {"order": "legal_name", "limit": 100, "actions": set()},
    "fix.zone": {"order": "name", "limit": 100, "actions": set()},
    "fix.working.calendar": {"order": "name", "limit": 100, "actions": set()},
    "fix.notification.config": {"order": "id", "limit": 100, "actions": set()},
    "fix.feature.flag": {"order": "key", "limit": 300, "actions": set()},
    "ir.config_parameter": {"order": "key", "limit": 500, "actions": set()},
    "ir.cron": {"order": "name", "limit": 300, "actions": set()},
    "fix.platform.environment": {"order": "kind, name", "limit": 100, "actions": set()},
    "fix.platform.release": {
        "order": "planned_on desc, id desc",
        "limit": 200,
        "actions": {"action_release"},
    },
    "fix.platform.announcement": {
        "order": "publish_on desc, id desc",
        "limit": 200,
        "actions": {"action_publish", "action_retire"},
    },
    # DOFA authority ladders as governed data. Putting one in force IS the
    # ruling, so the action is exposed here rather than buried in the ORM.
    "fix.dofa.ladder": {
        "order": "target_model, basis",
        "limit": 200,
        "actions": {"action_put_in_force"},
    },
    "fix.dofa.threshold": {
        "order": "ladder_id, upper_bound",
        "limit": 300,
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


def branch_registry(env, date_from=None, date_to=None, **params):
    branches = env["fix.branch"].sudo().search([])
    rows = [
        {
            "branch": b.name,
            "code": getattr(b, "code", None) or "—",
            "entity": b.entity_id.legal_name if b.entity_id else "—",
            "zone": b.zone_id.name if getattr(b, "zone_id", False) else "—",
            "active": "Yes" if getattr(b, "active", True) else "No",
        }
        for b in branches
    ]
    return _pack(
        "Branch Registry — %d branch(es)" % len(rows),
        ["branch", "code", "entity", "zone", "active"],
        {
            "branch": "Branch",
            "code": "Code",
            "entity": "Entity",
            "zone": "Zone",
            "active": "Active",
        },
        rows,
        ["The branch master every picker reads (M15/M45/M47)."],
        empty="No branches defined.",
    )


def flag_rollout(env, date_from=None, date_to=None, **params):
    flags = env["fix.feature.flag"].sudo().search([])
    rows = [
        {
            "key": f.key,
            "description": f.name,
            "enabled": "Yes" if f.enabled else "No",
            "scope": dict(f._fields["scope"].selection).get(f.scope, f.scope) if f.scope else "—",
            "default_on": "Yes" if f.default_for_new else "No",
        }
        for f in flags
    ]
    on = len([r for r in rows if r["enabled"] == "Yes"])
    return _pack(
        "Feature Flag Rollout — %d of %d enabled" % (on, len(rows)),
        ["key", "description", "enabled", "scope", "default_on"],
        {
            "key": "Flag Key",
            "description": "Description",
            "enabled": "Enabled",
            "scope": "Scope",
            "default_on": "Default for New",
        },
        rows,
        ["Flag keys gate feature availability; scope decides who evaluates them."],
        empty="No feature flags defined.",
    )


def config_drift(env, date_from=None, date_to=None, **params):
    """Config parameter inventory grouped by prefix."""
    params_all = env["ir.config_parameter"].sudo().search([])
    groups = {}
    for p in params_all:
        prefix = (p.key or "").split(".")[0] or "other"
        groups[prefix] = groups.get(prefix, 0) + 1
    rows = [{"prefix": k, "parameters": v} for k, v in sorted(groups.items())]
    return _pack(
        "Config Parameter Inventory — %d parameter(s)" % len(params_all),
        ["prefix", "parameters"],
        {"prefix": "Prefix", "parameters": "Parameters"},
        rows,
        [
            "Grouped by first key segment (cd_ap_ext, cd_billing_engine, ...). Values are "
            "deliberately NOT shown — parameters carry credentials-adjacent config."
        ],
        empty="No config parameters.",
    )


def calendar_coverage(env, date_from=None, date_to=None, **params):
    calendars = env["fix.working.calendar"].sudo().search([])
    rows = [
        {
            "calendar": c.name,
            "lines": len(c.line_ids) if getattr(c, "line_ids", False) else 0,
            "holidays": len(c.holiday_ids) if getattr(c, "holiday_ids", False) else 0,
            "active": "Yes" if getattr(c, "active", True) else "No",
        }
        for c in calendars
    ]
    return _pack(
        "Working Calendar Coverage",
        ["calendar", "lines", "holidays", "active"],
        {
            "calendar": "Calendar",
            "lines": "Working Lines",
            "holidays": "Holidays",
            "active": "Active",
        },
        rows,
        ["Calendars drive attendance, SLA and payroll windows."],
        empty="No working calendars defined.",
    )


def branch_provisioning(env, date_from=None, date_to=None, **params):
    """Branch provisioning: how long each branch has existed, measured from its
    creation record. The <1 day target is compared against the recorded age."""
    branches = env["fix.branch"].sudo().search([])
    now = datetime.datetime.now()
    rows = []
    for b in branches:
        age_days = None
        if b.create_date:
            age_days = round((now - b.create_date).total_seconds() / 86400.0, 2)
        rows.append(
            {
                "branch": b.name,
                "code": b.code or "-",
                "entity": b.entity_id.legal_name if b.entity_id else "-",
                "created": b.create_date.strftime("%d %b %Y %H:%M") if b.create_date else "-",
                "age_days": age_days if age_days is not None else "-",
                "active": "Yes" if b.active else "No",
            }
        )
    return _pack(
        "Branch Provisioning (<1d) - %d branch(es)" % len(rows),
        ["branch", "code", "entity", "created", "age_days", "active"],
        {
            "branch": "Branch",
            "code": "Code",
            "entity": "Entity",
            "created": "Created",
            "age_days": "Age (days)",
            "active": "Active",
        },
        rows,
        [
            "Age is measured from the branch record's creation timestamp; a branch created "
            "inside 24h is inside the provisioning target. The target applies to new "
            "branches - older rows show their true age, not a pass."
        ],
        empty="No branches.",
    )


def platform_health(env, date_from=None, date_to=None, **params):
    """Scheduled jobs and data loads that actually ran: cron inventory plus the
    load-run outcome counts. No synthetic uptime figure is produced."""
    crons = env["ir.cron"].sudo().search([])
    runs = env["fix.data.run"].sudo().search([])
    failures = runs.filtered(lambda r: r.state == "failed")
    rows = [
        {
            "signal": "Scheduled jobs (total)",
            "value": len(crons),
            "detail": "%d active" % len(crons.filtered(lambda c: c.active)),
        },
        {
            "signal": "Scheduled jobs (inactive)",
            "value": len(crons.filtered(lambda c: not c.active)),
            "detail": "paused or archived",
        },
        {
            "signal": "Data loads recorded",
            "value": len(runs),
            "detail": "%d failed" % len(failures),
        },
        {
            "signal": "Data loads failed",
            "value": len(failures),
            "detail": ", ".join(sorted(set(failures.mapped("failure_reason")))[:3]) or "-",
        },
    ]
    return _pack(
        "Platform Health Console - measured job and load state",
        ["signal", "value", "detail"],
        {"signal": "Signal", "value": "Count", "detail": "Detail"},
        rows,
        [
            "Everything here is a row in the database (ir.cron, fix.data.run). There is no "
            "synthetic uptime percentage: a real uptime figure needs the monitoring feed."
        ],
        empty="No platform signals.",
    )


def job_success_rate(env, date_from=None, date_to=None, **params):
    """Scheduled-job success: each cron's own last-call state, and the data loads
    that ran in the window. Success rate = succeeded / finished loads; an
    untriggered job has no rate and is listed as such."""
    import datetime as _dt

    crons = env["ir.cron"].sudo().search([])
    runs = env["fix.data.run"].sudo().search([])
    finished = runs.filtered(lambda r: r.state in ("succeeded", "failed"))
    ok = runs.filtered(lambda r: r.state == "succeeded")
    rows = []
    for cron in crons:
        rows.append(
            {
                "job": cron.name,
                "kind": "Scheduled job",
                "state": "Active" if cron.active else "Inactive",
                "last_run": str(cron.lastcall or "-")[:19],
                "next_run": str(cron.nextcall or "-")[:19],
                "failures": 0,
            }
        )
    for run in runs.sorted(lambda r: (r.started_at or _dt.datetime.min), reverse=True)[:50]:
        rows.append(
            {
                "job": run.pipeline_id.code if run.pipeline_id else run.name,
                "kind": "Data load (%s)" % run.stage,
                "state": dict(run._fields["state"].selection).get(run.state, run.state),
                "last_run": str(run.started_at or "-")[:19],
                "next_run": "-",
                "failures": 1 if run.state == "failed" else 0,
            }
        )
    rate = round(100.0 * len(ok) / len(finished), 1) if finished else None
    return {
        "title": "Job Success Rate - %s%s (%d load(s) finished)"
        % (
            "n/a" if rate is None else ("%.1f%%" % rate),
            "" if rate is not None else "",
            len(finished),
        ),
        "cols": ["job", "kind", "state", "last_run", "next_run", "failures"],
        "labels": {
            "job": "Job / Load",
            "kind": "Kind",
            "state": "State",
            "last_run": "Last Run",
            "next_run": "Next Run",
            "failures": "Failed",
        },
        "rows": rows,
        "notes": [
            "Success rate is measured on finished data loads; a scheduled job that has "
            "never run shows its cron state with no rate rather than an assumed success."
        ],
        "empty": "No scheduled jobs or data loads recorded.",
    }


def open_dofa_rulings(env, date_from=None, date_to=None, **params):
    """Every approval ladder with an unresolved basis, and what is at stake.

    These are DECISIONS, not defects. The code implements the specification's
    prose and says so; the DOFA authority matrix says something different.
    While the ladders were Python lists the conflict was visible only to an
    engineer reading the model, and resolving it needed a release. It is now
    configuration — and this report is how the people who hold the authority
    find out they are holding it.
    """
    Ladder = env["fix.dofa.ladder"].sudo()
    rows = []
    for conflict in Ladder.conflicts():
        target = conflict["target_model"]
        for ladder in Ladder.search([("target_model", "=", target)]):
            bands = ladder.threshold_ids.sorted("upper_bound")
            rows.append(
                {
                    "target_model": target,
                    "ladder": ladder.name,
                    "basis": dict(ladder._fields["basis"].selection).get(
                        ladder.basis, ladder.basis
                    ),
                    "in_force": "YES" if ladder.in_force else "",
                    "is_today": "YES" if ladder.matches_implementation else "",
                    "bands": " · ".join(
                        "%s→%s"
                        % (
                            "∞" if band.upper_bound >= 1e9 else ("%g" % band.upper_bound),
                            band.tier.replace("tier_", "T"),
                        )
                        for band in bands
                    ),
                    "ruled_by": ladder.ruled_by.name or "",
                    "authority": ladder.ruling_reference or "",
                }
            )
    rows.sort(key=lambda r: (r["target_model"], r["basis"]))
    unresolved = sorted(
        {
            r["target_model"]
            for r in rows
            if not any(x["in_force"] for x in rows if x["target_model"] == r["target_model"])
        }
    )
    return _pack(
        "Open DOFA Rulings (approval ladders awaiting a decision)",
        [
            "target_model",
            "ladder",
            "basis",
            "is_today",
            "in_force",
            "bands",
            "ruled_by",
            "authority",
        ],
        [
            "Model",
            "Ladder",
            "Basis",
            "What The Code Does Today",
            "In Force",
            "Bands (bound→tier)",
            "Ruled By",
            "Authority",
        ],
        rows,
        notes=[
            "A row with no 'In Force' anywhere for its model means NOTHING has "
            "been ruled: the model keeps its own coded default, and behaviour "
            "is unchanged.",
            "'What The Code Does Today' marks the basis the coded default "
            "already implements. It is a fact about the code, not a ruling - "
            "so for each model one option is 'keep what we do' and the other "
            "changes the bands. The choice is not symmetrical.",
            "Putting a ladder in force requires a stated authority — the "
            "minute, memo or approval. A change to who may approve what, with "
            "nothing recorded about who authorised it, is not an improvement "
            "on a hard-coded list.",
            "Unresolved today: %s." % (", ".join(unresolved) or "none"),
            "These are business decisions. The engineering blocker (the "
            "ladders were Python lists, so a ruling needed a code change and a "
            "release) has been removed; the ruling itself has not been taken "
            "and must not be assumed.",
        ],
        empty="No approval ladders are configured, so every model uses its own " "coded default.",
    )


REPORTS = {
    "job_success_rate": job_success_rate,
    "branch_registry": branch_registry,
    "flag_rollout": flag_rollout,
    "config_drift": config_drift,
    "calendar_coverage": calendar_coverage,
}

REPORTS["branch_provisioning"] = branch_provisioning
REPORTS["platform_health"] = platform_health
REPORTS["open_dofa_rulings"] = open_dofa_rulings


def kpis(env):
    branches = env["fix.branch"].sudo().search([])
    flags = env["fix.feature.flag"].sudo().search([])
    announcements = env["fix.platform.announcement"].sudo().search([("state", "=", "published")])
    today = datetime.date.today()
    return {
        "branches": len(branches),
        "branches_active": len(branches.filtered(lambda b: b.active)),
        "flags_on": len(flags.filtered(lambda f: f.enabled)),
        "flags_total": len(flags),
        "announcements_live": len(
            announcements.filtered(lambda a: not a.expires_on or a.expires_on >= today)
        ),
    }
