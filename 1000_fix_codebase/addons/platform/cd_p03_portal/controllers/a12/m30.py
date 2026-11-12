# A12 · M30 Platform Administration — surfaces, packs and KPIs over branches,
# entities, config parameters, feature flags, zones, calendars, country packs
# and announcements.
import datetime

from odoo.exceptions import AccessError, UserError

SURFACES = {
    "fix.branch": {
        "order": "name",
        "limit": 300,
        # A12 finish E20 (BRU-ADM-05): a row whose stored company was lost is still
        # shown through its entity, or nobody could ever find it to repair it.
        "company_paths": ("company_id", "entity_id.company_id"),
        "actions": {
            "action_go_live",
            "action_suspend",
            "action_request_closure",
            "action_confirm_closure",
        },
    },
    "fix.entity": {"order": "legal_name", "limit": 100, "actions": set()},
    "fix.zone": {"order": "name", "limit": 100, "actions": set()},
    "fix.working.calendar": {
        "order": "name",
        "limit": 100,
        "actions": {"action_propose_closure", "action_confirm_closure"},
    },
    "fix.working.calendar.holiday": {
        "order": "date_from desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.notification.config": {"order": "id", "limit": 100, "actions": set()},
    "fix.feature.flag": {"order": "key", "limit": 300, "actions": set()},
    "ir.config_parameter": {"order": "key", "limit": 500, "actions": set()},
    "ir.cron": {"order": "name", "limit": 300, "actions": set()},
    "fix.platform.environment": {
        "order": "kind, name",
        "limit": 100,
        "actions": {
            "action_go_live",
            "action_mark_degraded",
            "action_take_offline",
            "action_record_masking",
        },
    },
    "fix.platform.release": {
        "order": "planned_on desc, id desc",
        "limit": 200,
        "actions": {"action_start_test", "action_release", "action_rollback"},
    },
    "fix.platform.announcement": {
        "order": "publish_on desc, id desc",
        "limit": 200,
        "actions": {"action_publish", "action_retire", "action_acknowledge"},
    },
    # DOFA authority ladders as governed data. A12 finish E1: a ruling is two acts
    # by two sessions, so the workspace proposes and countersigns. action_put_in_force
    # is deliberately NOT here: for a person it is only the proposal.
    "fix.dofa.ladder": {
        "order": "target_model, basis, version",
        "limit": 200,
        "actions": {"action_propose_ruling", "action_countersign", "action_withdraw_ruling"},
    },
    "fix.dofa.threshold": {
        "order": "ladder_id, upper_bound",
        "limit": 300,
        "actions": set(),
    },
}

# A12 R4: what a workspace form may set through /p03/model/write on each M30
# surface. Everything else the form is sent is refused (or dropped on create),
# so the ruling stamp, lifecycle states and deployment config cannot be typed
# in: they change only through the whitelisted actions, which run the model's
# own checks (two-authority DOFA ruling, publish/retire, release gate).
WRITABLE = {
    # Statutory register masters (X4): Platform Admin only by ACL; the
    # entity/OU of an existing branch is additionally structural server-side.
    "fix.branch": (
        "name",
        "name_bn",
        "code",
        "entity_id",
        "operating_unit_id",
        "zone_id",
        "address_id",
        "phone",
        "email",
        "manager_id",
        "calendar_id",
    ),
    "fix.entity": (
        "code",
        "legal_name",
        "legal_name_bn",
        "company_id",
        "operating_unit_id",
        "country_id",
        "currency_id",
        "bin_number",
        "tin_number",
        "vat_statutory_day",
        "statutory_calendar_rule",
        "incorporation_date",
        "active",
    ),
    "fix.zone": ("name", "name_bn", "code", "description", "active"),
    "fix.working.calendar": ("name", "template_id", "branch_id", "timezone", "active", "line_ids"),
    "fix.working.calendar.holiday": ("calendar_id", "name", "name_bn", "date_from", "date_to"),
    "fix.notification.config": (
        "consent_class",
        "channel",
        "send_window",
        "frequency_cap",
        "combined_cap_non_transactional",
        "sms_route",
        "stale_discard_hours",
    ),
    # The kill switch (BRU-ADM-09/10) is real, admin-gated work: flag content
    # and the enabled toggle stay form-editable for Platform Admin.
    "fix.feature.flag": ("key", "name", "enabled", "scope", "branch_ids", "default_for_new"),
    # Config tampering through the workspace is an A12 finding (c01-c03,
    # M30-13): parameters and crons are deployment configuration, provisioned
    # outside the workspace. Read-only inventory screens.
    "ir.config_parameter": (),
    "ir.cron": (),
    # Environment identity is platform-admin maintenance; the lifecycle state
    # is not typeable (M30-8: born-live and DR-live by write were attacks).
    "fix.platform.environment": (
        "name",
        "kind",
        "base_url",
        "database_name",
        "release_channel",
        "data_residency",
        "owner_id",
        "notes",
    ),
    # A12 finish E7: + New could never save, because version and name were
    # required and not here. Editable until release (the model then freezes them);
    # the state moves only through the actions (model-side gate, B5).
    "fix.platform.release": (
        "version",
        "name",
        "environment_id",
        "owner_id",
        "planned_on",
        "change_summary",
        "rollback_plan",
        "itsm_change_id",
    ),
    # Announcement content is authored here; state moves only through
    # action_publish / action_retire (M30-11: born-published was an attack).
    "fix.platform.announcement": (
        "name",
        "severity",
        "audience",
        "publish_on",
        "expires_on",
        "body",
        "kind",
        "maintenance_start",
    ),
    # A draft ladder's identity, its bands (the form's child grid) and the
    # countersigning authority holder. in_force / ruled_by / ruled_at /
    # ruling_reference are the SYSTEM-set ruling stamp (X3) and are refused.
    "fix.dofa.ladder": (
        "name",
        "target_model",
        "basis",
        "countersigned_by",
        "countersigner_choice",
        "threshold_ids",
    ),
    "fix.dofa.threshold": ("ladder_id", "upper_bound", "tier", "note"),
}


def _require_admin_read(env, model, what):
    """Gate a privileged report read on the model's read ACL (M30-13).

    The cron and config-parameter tables are base.group_system only; the
    reports that inventory them used to sudo the read and hand 72 job
    schedules / 17 config-key prefixes to any internal user. Now the caller
    must be able to read the model at all — a clear refusal otherwise.
    """
    try:
        env[model].check_access("read")
    except AccessError as access_err:
        raise UserError(
            "%s inventories platform deployment configuration and is available "
            "to platform administrators only." % what
        ) from access_err


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    # The workspace reads `labels` as a {col: header} map. A positional list
    # (open_dofa_rulings passed one) left every header as its raw key on 8069.
    if isinstance(labels, list | tuple):
        labels = dict(zip(cols, labels, strict=True))
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
    # A12 R4: read as the CALLER (group_user has read on the register; no
    # sudo needed and none offered).
    branches = env["fix.branch"].search([])
    rows = [
        {
            "branch": b.name,
            "code": getattr(b, "code", None) or "—",
            "entity": b.entity_id.legal_name if b.entity_id else "—",
            "zone": b.zone_id.name if getattr(b, "zone_id", False) else "—",
            "state": dict(b._fields["state"].selection).get(b.state, b.state),
            "active": "Yes" if getattr(b, "active", True) else "No",
        }
        for b in branches
    ]
    return _pack(
        "Branch Registry — %d branch(es)" % len(rows),
        ["branch", "code", "entity", "zone", "state", "active"],
        {
            "branch": "Branch",
            "code": "Code",
            "entity": "Entity",
            "zone": "Zone",
            "state": "Status",
            "active": "Active",
        },
        rows,
        ["The branch master every picker reads (M15/M45/M47)."],
        empty="No branches defined.",
    )


def flag_rollout(env, date_from=None, date_to=None, **params):
    flags = env["fix.feature.flag"].search([])
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
        [
            "Flag keys gate feature availability; scope decides who evaluates them.",
            "Only keys the code really reads may be registered, and today that is one kill "
            "switch. New capabilities do not yet ship behind flags.",
        ],
        empty="No feature flags defined.",
    )


def config_drift(env, date_from=None, date_to=None, **params):
    """Config parameter inventory grouped by prefix."""
    _require_admin_read(env, "ir.config_parameter", "The config parameter inventory")
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
            "deliberately NOT shown — parameters carry credentials-adjacent config.",
            "This is an inventory. No config registry, approval or environment promotion "
            "exists yet, and no drift is computed (BRU-ADM-02/03 are not built).",
        ],
        empty="No config parameters.",
    )


def calendar_coverage(env, date_from=None, date_to=None, **params):
    calendars = env["fix.working.calendar"].search([])
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
    branches = env["fix.branch"].search([])
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
            "branches - older rows show their true age, not a pass.",
        ],
        empty="No branches.",
    )


def platform_health(env, date_from=None, date_to=None, **params):
    """Scheduled jobs and data loads that actually ran: cron inventory plus the
    load-run outcome counts. No synthetic uptime figure is produced."""
    _require_admin_read(env, "ir.cron", "The platform health console")
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
            "synthetic uptime percentage: a real uptime figure needs the monitoring feed.",
        ],
        empty="No platform signals.",
    )


def job_success_rate(env, date_from=None, date_to=None, **params):
    """Scheduled-job success: each cron's own last-call state, and the data loads
    that ran in the window. Success rate = succeeded / finished loads; an
    untriggered job has no rate and is listed as such."""
    import datetime as _dt

    _require_admin_read(env, "ir.cron", "The job success report")
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
                # BRU-ADM-12: ir.cron carries no failure counter. The column
                # used to say 0 for every job — a silent-failure claim. It now
                # says unknown until the monitoring feed provides the figure;
                # failed data loads below are counted from the database.
                "failures": "-",
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
            "never run shows its cron state with no rate rather than an assumed success.",
            "Scheduled-job failure counts show '-' until the monitoring feed supplies "
            "them: the job scheduler keeps no failure counter, and showing 0 would claim "
            "there were no silent failures (BRU-ADM-12).",
            "This is an inventory of Odoo's job table. No job registry with owner, expected "
            "duration or failure impact exists yet (BRU-ADM-11/12 are not built).",
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
    Ladder = env["fix.dofa.ladder"]
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
                    "status": dict(ladder._fields["ruling_state"].selection).get(
                        ladder.ruling_state, ladder.ruling_state
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
                    "countersigned_by": ladder.countersigned_by.name or "",
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
            "status",
            "in_force",
            "bands",
            "ruled_by",
            "countersigned_by",
            "authority",
        ],
        [
            "Model",
            "Ladder",
            "Basis",
            "What The Code Does Today",
            "Status",
            "In Force",
            "Bands (bound→tier)",
            "Ruled By",
            "Countersigned By",
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
            "A ruling takes two acts by two people: a Tier 4 holder proposes it, citing "
            "the minute or memo and naming a Tier 5 holder, and that Tier 5 holder "
            "countersigns from their own session by restating the authority. Only the "
            "countersignature puts the ladder in force.",
            "Unresolved today: %s." % (", ".join(unresolved) or "none"),
            "These are business decisions. The engineering blocker (the "
            "ladders were Python lists, so a ruling needed a code change and a "
            "release) has been removed; the ruling itself has not been taken "
            "and must not be assumed.",
        ],
        empty="No approval ladders are configured, so every model uses its own " "coded default.",
    )


def dofa_coverage(env, date_from=None, date_to=None, **params):
    """P1-5 / M30-3: which approval-bearing models does an authority govern?

    Computed from the live registry and the live authority sources, never typed.

    A12 finish E21: the first version said "46 of 132 governed" and that was wrong
    three ways. "Ladder" only meant the model carries the mixin, and two had a
    ruling in force; "none" hid models whose approver is a group named in code; and
    44 more models with an approve action were outside the denominator. Each is now
    its own column. This report is the WORKING LIST for the one-DoA migration (P1-5,
    decision B4): it reports the 130 or so models, and migrating them is that work.
    """
    approvable_cls = type(env["fix.approvable.mixin"])
    dofa_cls = type(env["fix.dofa.mixin"])
    m63_rows = env["fix.approval.matrix"].search([])
    m63_targets = {row.res_model for row in m63_rows if row.res_model}
    domain_rows = len(m63_rows) - len([r for r in m63_rows if r.res_model])
    in_force = {
        ladder.target_model for ladder in env["fix.dofa.ladder"].search([("in_force", "=", True)])
    }
    rows = []
    for name, cls in sorted(env.registry.models.items()):
        if getattr(cls, "_abstract", False) or getattr(cls, "_transient", False):
            continue
        approvable = issubclass(cls, approvable_cls)
        approve_action = any(
            attr.startswith("action_approve") or attr == "action_dofa_approve" for attr in dir(cls)
        )
        if not (approvable or approve_action):
            continue
        ladder = issubclass(cls, dofa_cls)
        m63 = name in m63_targets
        coded = getattr(cls, "_approval_group", None)
        if ladder and m63:
            authority = "ladder+m63"
        elif ladder:
            authority = "ladder"
        elif m63:
            authority = "m63"
        elif coded:
            authority = "coded_group"
        else:
            authority = "none"
        rows.append(
            {
                "model": name,
                "source": "routed approval" if approvable else "approve action only",
                "ladder": "yes" if ladder else "-",
                "in_force": "yes" if name in in_force else "-",
                "m63": "yes" if m63 else "-",
                "coded_group": coded or "-",
                "authority": authority,
            }
        )
    counts = {}
    for row in rows:
        counts[row["authority"]] = counts.get(row["authority"], 0) + 1
    return {
        "title": "DOFA Coverage - %d approval-bearing models: ladder-capable %d (ruling in force "
        "on %d), m63 %d, both %d, coded group %d, none %d"
        % (
            len(rows),
            counts.get("ladder", 0) + counts.get("ladder+m63", 0),
            len([r for r in rows if r["in_force"] == "yes"]),
            counts.get("m63", 0),
            counts.get("ladder+m63", 0),
            counts.get("coded_group", 0),
            counts.get("none", 0),
        ),
        "cols": ["model", "source", "ladder", "in_force", "m63", "coded_group", "authority"],
        "labels": {
            "model": "Approval-Bearing Model",
            "source": "Found By",
            "ladder": "DOFA Ladder (mixin)",
            "in_force": "Ruling In Force",
            "m63": "M63 Rule Book",
            "coded_group": "Coded Group",
            "authority": "Authority",
        },
        "rows": rows,
        "notes": [
            "Coverage is computed from the registry at report time. 'DOFA Ladder' means the "
            "model CAN read a ladder; without a ruling in force it keeps its coded default.",
            "%d approval-matrix row(s) carry no model name and apply to their whole "
            "decision domain; they are not counted as named coverage." % domain_rows,
            "This is the working list for one DoA (P1-5, business decision B4). Rows with "
            "authority 'none' and 'approve action only' are the backlog; 'ladder+m63' rows "
            "must be consolidated to ONE authority. No model is migrated by this report.",
        ],
        "empty": "No approval-bearing models are installed.",
    }


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
REPORTS["dofa_coverage"] = dofa_coverage


def kpis(env):
    # A12 R4: read as the CALLER — the register models are group_user
    # readable, so the tiles need no sudo and inherit the caller's company
    # and record-rule scoping.
    branches = env["fix.branch"].search([])
    flags = env["fix.feature.flag"].search([])
    announcements = env["fix.platform.announcement"].search([("state", "=", "published")])
    today = datetime.date.today()
    return {
        "dofa_awaiting_countersign": env["fix.dofa.ladder"].search_count(
            [("ruling_state", "=", "proposed")]
        ),
        "branches": len(branches),
        "branches_active": len(branches.filtered(lambda b: b.active)),
        "flags_on": len(flags.filtered(lambda f: f.enabled)),
        "flags_total": len(flags),
        "announcements_live": len(
            announcements.filtered(lambda a: not a.expires_on or a.expires_on >= today)
        ),
    }
