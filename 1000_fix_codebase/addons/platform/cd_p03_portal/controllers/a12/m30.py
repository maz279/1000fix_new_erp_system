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
    # M30 capture audit (2026-11-14): the operational registers of spec §10.1.
    # Each is Platform Admin only by ACL; the models enforce the second person.
    "fix.scheduled.job": {"order": "name", "limit": 300, "actions": set()},
    "fix.config.parameter": {"order": "key", "limit": 300, "actions": set()},
    "fix.config.change": {
        "order": "id desc",
        "limit": 300,
        "actions": {
            "action_apply",
            "action_apply_emergency",
            "action_regularise",
            "action_reject",
            "action_rollback",
        },
    },
    "fix.backup.verification": {
        "order": "restore_tested_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.dr.drill": {
        "order": "drill_date desc, id desc",
        "limit": 100,
        "actions": {"action_sign_off"},
    },
    # M30 capture audit, second pass (2026-11-19): the records the spec gives
    # the six pages that still had nowhere to go (models/fix_platform_ops4.py).
    "fix.branch.capability": {"order": "branch_id, service_kind", "limit": 500, "actions": set()},
    "fix.org.change": {
        "order": "effective_from desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_reject"},
    },
    "fix.change.freeze": {"order": "date_from desc", "limit": 100, "actions": {"action_lift"}},
    "fix.component.licence": {"order": "component, version", "limit": 500, "actions": set()},
    "fix.maintenance.window": {
        "order": "scheduled_from desc",
        "limit": 200,
        "actions": {
            "action_raise_announcement",
            "action_start",
            "action_complete",
            "action_cancel",
        },
    },
    "fix.runbook": {"order": "scope, code", "limit": 300, "actions": {"action_mark_reviewed"}},
    "fix.platform.alert": {"order": "severity, code", "limit": 300, "actions": set()},
    "fix.capacity.metric": {"order": "measured_on desc, resource", "limit": 300, "actions": set()},
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
    "fix.feature.flag": (
        "key",
        "name",
        "enabled",
        "scope",
        "branch_ids",
        "default_for_new",
        "owning_module",
        "planned_removal_date",
    ),
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
        "name_bn",
        "body_bn",
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
    # M30 capture audit (2026-11-14). The run state of a job is read from its
    # scheduled action; a change's state, previous value and stamps move only
    # through apply / reject / roll back; a drill's sign-off only through its action.
    "fix.scheduled.job": (
        "name",
        "cron_id",
        "owning_module",
        "owner_id",
        "expected_duration_min",
        "sla_minutes",
        "concurrent_safe",
        "failure_impact",
        "failure_note",
        "runbook_ref",
        "runbook_id",
        "active",
    ),
    # Registering a key is a system-administrator decision (model-side check).
    "fix.config.parameter": (
        "key",
        "description",
        "value_type",
        "min_value",
        "max_value",
        "allowed_values",
        "default_value",
        "owning_module",
        "business_impact",
        "active",
    ),
    "fix.config.change": ("parameter_id", "new_value", "reason", "change_reference", "emergency"),
    "fix.backup.verification": (
        "backup_ref",
        "backup_type",
        "source_environment_id",
        "restored_into_id",
        "taken_at",
        "restore_tested_at",
        "restore_duration_min",
        "result",
        "evidence",
        "note",
    ),
    "fix.dr.drill": (
        "drill_date",
        "scenario",
        "scope",
        "environment_id",
        "rpo_achieved_min",
        "rto_achieved_min",
        "issues_found",
        "actions",
    ),
    # Second pass (2026-11-19). States, stamps, the announcement link and the
    # actual times move only through the actions.
    "fix.branch.capability": (
        "branch_id",
        "service_kind",
        "device_category",
        "max_repair_level",
        "effective_from",
        "note",
        "active",
    ),
    "fix.org.change": (
        "branch_id",
        "change_type",
        "new_name",
        "new_name_bn",
        "new_zone_id",
        "new_address_id",
        "effective_from",
        "reason",
    ),
    "fix.change.freeze": ("name", "date_from", "date_to", "scope", "reason"),
    "fix.component.licence": (
        "component",
        "version",
        "licence",
        "licence_class",
        "obligation_summary",
        "compliance_note",
        "owner_id",
        "reviewed_on",
        "next_review_due",
        "active",
    ),
    "fix.maintenance.window": (
        "scheduled_from",
        "scheduled_to",
        "scope",
        "impact",
        "environment_id",
        "outcome_note",
    ),
    "fix.runbook": (
        "code",
        "name",
        "scope",
        "reference",
        "document_url",
        "steps",
        "owner_id",
        "last_reviewed_on",
        "review_months",
        "active",
    ),
    "fix.platform.alert": (
        "code",
        "name",
        "source",
        "severity",
        "threshold_expression",
        "routing",
        "runbook_id",
        "active",
    ),
    "fix.capacity.metric": (
        "resource",
        "dimension",
        "measured_on",
        "current_value",
        "capacity_value",
        "growth_rate_pct",
        "scaling_action",
        "review_note",
    ),
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
    rows += _registry_signals(env, crons)
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


def _registry_signals(env, crons):
    """M30 capture audit (2026-11-14): what the job, change and continuity
    registers measure. Read as the caller; a register the caller cannot read
    is left out rather than refused, so the console still renders."""
    rows = []

    def _readable(model):
        # absent until cd_entity_config is upgraded; unreadable for non-admins
        return model in env and env[model].has_access("read")

    if _readable("fix.scheduled.job"):
        jobs = env["fix.scheduled.job"].search([])
        registered = set(jobs.mapped("cron_id").ids)
        active = crons.filtered("active")
        missed = jobs.filtered(lambda j: j.run_state == "missed")
        rows += [
            {
                "signal": "Active jobs with no registration (BRU-ADM-11)",
                "value": len([c for c in active if c.id not in registered]),
                "detail": "%d of %d active jobs registered"
                % (len([c for c in active if c.id in registered]), len(active)),
            },
            {
                "signal": "Registered jobs that missed a run (T-09)",
                "value": len(missed),
                "detail": ", ".join(missed.mapped("name")[:3]) or "-",
            },
        ]
    if _readable("fix.config.change"):
        Change = env["fix.config.change"]
        rows.append(
            {
                "signal": "Configuration changes awaiting a second person",
                "value": Change.search_count([("state", "=", "proposed")]),
                "detail": "%d applied, %d rolled back"
                % (
                    Change.search_count([("state", "=", "applied")]),
                    Change.search_count([("state", "=", "rolled_back")]),
                ),
            }
        )
    if _readable("fix.backup.verification"):
        Test = env["fix.backup.verification"]
        passed = Test.search([("result", "=", "pass")], limit=1)
        age = (datetime.datetime.now() - passed.restore_tested_at).days if passed else None
        rows.append(
            {
                "signal": "Days since the last passed restore test (weekly, NFR-052)",
                "value": age if age is not None else "never",
                "detail": passed.name if passed else "no restore test on record",
            }
        )
    if _readable("fix.dr.drill"):
        Drill = env["fix.dr.drill"]
        since = datetime.date.today() - datetime.timedelta(days=365)
        drills = Drill.search([("state", "=", "signed_off"), ("drill_date", ">=", since)])
        rows.append(
            {
                "signal": "DR drills signed off in 12 months (2 required, NFR-051)",
                "value": len(drills),
                "detail": "%d met both RPO and RTO"
                % len(drills.filtered(lambda d: d.rpo_met and d.rto_met)),
            }
        )
    return rows + _operations_signals(env, _readable)


def _operations_signals(env, _readable):
    """Second pass (2026-11-19): freezes, emergency changes, maintenance,
    runbooks and capacity. Same rule: read as the caller, skip what it cannot read."""
    rows = []
    now = datetime.datetime.now()
    if _readable("fix.change.freeze"):
        freeze = env["fix.change.freeze"].search(
            [("date_from", "<=", now), ("date_to", ">", now)], limit=1
        )
        rows.append(
            {
                "signal": "Change freeze in force (BRU-ADM-22)",
                "value": "yes" if freeze else "no",
                "detail": "%s until %s" % (freeze.name, freeze.date_to) if freeze else "-",
            }
        )
    if _readable("fix.config.change") and "emergency" in env["fix.config.change"]._fields:
        open_emergencies = env["fix.config.change"].search(
            [("emergency", "=", True), ("state", "=", "applied"), ("regularised_on", "=", False)]
        )
        rows.append(
            {
                "signal": "Emergency changes awaiting their change record (24 h, BRU-ADM-04)",
                "value": len(open_emergencies),
                "detail": ", ".join(open_emergencies.mapped("name")[:3]) or "-",
            }
        )
    if _readable("fix.maintenance.window"):
        Window = env["fix.maintenance.window"]
        month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        windows = Window.search([("state", "!=", "cancelled"), ("scheduled_from", ">=", month)])
        windows = windows.filtered(lambda w: w.scheduled_from.month == now.month)
        rows.append(
            {
                "signal": "Planned maintenance this month, minutes (cap %d, BRU-ADM-19)"
                % Window._monthly_cap(),
                "value": sum(windows.mapped("planned_minutes")),
                "detail": "%d window(s), %d overran"
                % (len(windows), len(windows.filtered("overran"))),
            }
        )
    if _readable("fix.runbook"):
        books = env["fix.runbook"].search([])
        rows.append(
            {
                "signal": "Runbooks past their review date (NFR-091)",
                "value": len(books.filtered("review_overdue")),
                "detail": "%d runbook(s) on record" % len(books),
            }
        )
    if _readable("fix.platform.alert"):
        rows.append(
            {
                "signal": "Active alerts (each with a runbook, BRU-ADM-14)",
                "value": env["fix.platform.alert"].search_count([("active", "=", True)]),
                "detail": "-",
            }
        )
    if _readable("fix.capacity.metric"):
        latest = {}
        for metric in env["fix.capacity.metric"].search([], order="measured_on desc, id desc"):
            latest.setdefault((metric.resource, metric.dimension), metric)
        low = [m for m in latest.values() if m.headroom_pct < 20]
        rows.append(
            {
                "signal": "Resources under 20% headroom at their last review (OPS-08)",
                "value": len(low),
                "detail": ", ".join(m.resource for m in low[:3]) or "%d reviewed" % len(latest),
            }
        )
    return rows


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
        **_admin_kpis(env),
    }


def _admin_kpis(env):
    """Platform Admin tiles (M30 capture audit): empty for a caller who cannot
    read the registers, so the other tiles still load."""
    out = {}
    if "fix.config.change" in env and env["fix.config.change"].has_access("read"):
        out["config_changes_pending"] = env["fix.config.change"].search_count(
            [("state", "=", "proposed")]
        )
    if "fix.scheduled.job" in env and env["fix.scheduled.job"].has_access("read"):
        out["jobs_missed"] = len(
            env["fix.scheduled.job"].search([]).filtered(lambda j: j.run_state == "missed")
        )
    change = env.get("fix.config.change")
    if change is not None and change.has_access("read") and "emergency" in change._fields:
        out["emergency_open"] = change.search_count(
            [("emergency", "=", True), ("state", "=", "applied"), ("regularised_on", "=", False)]
        )
    if "fix.maintenance.window" in env and env["fix.maintenance.window"].has_access("read"):
        out["maintenance_upcoming"] = env["fix.maintenance.window"].search_count(
            [("state", "=", "planned"), ("scheduled_from", ">=", datetime.datetime.now())]
        )
    return out
