# A12 · M29 Identity, Access & Security — access review, privileged sessions,
# sensitive-data exposure, SoD results and authentication trends.
#
# Honest scope: reads of individual sensitive fields are not instrumented, so
# "Sensitive-Data Access" reports the CLASSIFIED EXPOSURE SURFACE (which fields
# are sensitive and which roles can reach their model) — never invented reads.
#
# A12 R4: every surface declares what /p03/model/write may set on it
# (module-level WRITABLE, merged by controllers/a12/__init__.py). Workflow
# fields (state/decision/…) change only through the surface's actions.
# A12 X5 (M29-11): `res.device.log` and `res.users` read under the CALLER's
# record rules ("rules": True) — the sudo list read used to leak every
# user's IP, location and session identifier to any internal user.
# A12 P2: KPIs and reports read as the caller (no sudo().search([])).
import datetime

from odoo.exceptions import AccessError

SURFACES = {
    # A08 S4 (FR-SEC-024): an SoD exception (mitigation) for a conflicting
    # grant. Approved by an SoD exception approver who is neither the grantee
    # nor the requester; state and decision stamps move only by its actions.
    "fix.sod.mitigation": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_approve", "action_reject", "action_revoke"},
        "writable": frozenset(
            {"control_id", "user_id", "mitigating_control", "reason", "valid_from", "valid_until"}
        ),
    },
    # personal data: record rules apply (A09 pattern) — a plain user sees
    # only their own device logs, and res.users reads respect Odoo's rules
    "res.users": {"order": "name", "limit": 400, "actions": set(), "rules": True},
    "fix.role": {"order": "code", "limit": 200, "actions": set()},
    # who was actually given what: system-written, no action, no input (E3/E5)
    "fix.role.assignment": {"order": "granted_on desc, id desc", "limit": 500, "actions": set()},
    "res.groups": {"order": "name", "limit": 300, "actions": set()},
    "fix.field.rule": {"order": "id", "limit": 400, "actions": set()},
    "fix.isolation.tier": {"order": "code", "limit": 50, "actions": set()},
    "fix.access.request": {
        "order": "requested_on desc, id desc",
        "limit": 400,
        "actions": {"action_approve", "action_reject", "action_grant"},
    },
    "fix.sod.control": {"order": "code", "limit": 300, "actions": set()},
    "fix.sod.test": {
        "order": "tested_on desc, id desc",
        "limit": 400,
        "actions": {"action_run"},
    },
    "fix.privileged.session": {
        "order": "started_at desc, id desc",
        "limit": 400,
        "actions": {"action_approve", "action_reject", "action_open", "action_close"},
    },
    "fix.sensitive.field": {"order": "model_name, field_name", "limit": 400, "actions": set()},
    "res.device.log": {
        "order": "last_activity desc, id desc",
        "limit": 400,
        "actions": set(),
        "rules": True,
    },
    "fix.jml.event": {
        "order": "effective_on desc, id desc",
        "limit": 300,
        "actions": {"action_apply", "action_cancel"},
        # New User form: the Access Approver who files a joiner picks the
        # employee by NAME without HR rights; the server offers only active
        # employees with no login yet (never the browser's filter alone)
        "picker_names": ("employee_id",),
        "pickers": {"employee_id": [("user_id", "=", False)]},
    },
    "fix.access.certification": {
        "order": "period desc, id desc",
        "limit": 400,
        "actions": {"action_certify", "action_revoke"},
    },
    "fix.access.certification.campaign": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_generate"},
    },
    "fix.encryption.key": {
        "order": "code",
        "limit": 200,
        "actions": {"action_rotate"},
    },
    "fix.security.audit": {
        "order": "occurred_at desc, id desc",
        "limit": 500,
        # R5: chain verification reads the whole chain and reports — the
        # summary is the point (raises with the verified counts).
        "actions": {"action_verify_chain"},
    },
    "fix.security.incident": {
        "order": "detected_at desc, id desc",
        "limit": 400,
        "actions": {
            "action_contain",
            "action_close",
            "action_set_severity",
            "action_confirm_severity",
            "action_reject_severity",
        },
        # E16: a reporter sees their own reports; breach text is for the officer
        "rules": True,
    },
    # M29 capture audit 2026-11-14 (spec §10.1, BRU-SEC-21): the vulnerability
    # register. A reporter and the remediation owner read their own findings, a
    # Security Officer all of them - so the list reads under the caller's rules.
    "fix.vulnerability": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_remediate", "action_verify", "action_reopen", "action_accept_risk"},
        "rules": True,
    },
    "ir.rule": {"order": "model_id, id", "limit": 400, "actions": set()},
    "ir.model.access": {"order": "model_id, id", "limit": 800, "actions": set()},
    # New User form (capture audit 2026-11-14): who has narrowed access to which
    # module. Read under the caller's rules: a person sees their own rows,
    # Access Approvers and administrators see everyone's.
    "fix.module.permission": {
        "order": "user_id, module_code",
        "limit": 2000,
        "actions": set(),
        "rules": True,
    },
}

# A12 R4: the fields a workspace form may set through /p03/model/write —
# exactly what the forms in static/src/a12/m29.js offer as editable, minus
# every workflow-controlled field (those are action-only). Read-only screens
# declare an empty tuple: nothing the workspace can type on them.
WRITABLE = {
    # M29 wiring pass (2026-11-05): the D365 User form is comprehensive —
    # identity, organisation/data scope and preferences are editable here;
    # group_ids, the password fields and company_ids are NOT (entitlement
    # changes only through approved access requests / JML; passwords through
    # the invitation flow; allowed companies is a data-scope change owned by
    # the multi-entity substrate).
    "res.users": (
        "name",
        "name_bn",
        "login",
        "email",
        "phone",
        "mobile_phone",
        "work_email",
        "image_1920",
        "active",
        "lang",
        "tz",
        "preferred_language",
        "notification_type",
        "signature",
        "comment",
        "out_of_office_from",
        "out_of_office_to",
        "out_of_office_message",
        "company_id",
        "default_operating_unit_id",
        "work_location_id",
        "work_location_type",
    ),
    "fix.role": (
        "code",
        "name",
        "name_bn",
        "keycloak_role",
        "active",
        "description",
        "company_id",
    ),
    "res.groups": (),
    "fix.role.assignment": (),
    "fix.field.rule": (
        "model_id",
        "field_id",
        "fix_model_name",
        "fix_field_name",
        "role_ids",
        "permission",
        "active",
    ),
    "fix.isolation.tier": (
        "code",
        "name",
        "description",
        "record_rule_domain",
        "requires_step_up",
        "requires_audit",
    ),
    # the decision record (state/approver/decided_on) is action-only (X1)
    "fix.access.request": (
        "request_type",
        "user_id",
        "role_id",
        "requested_on",
        "valid_until",
        "reason",
    ),
    "fix.sod.control": (
        "code",
        "name",
        "control_type",
        "role_a_id",
        "role_b_id",
        "group_a_id",
        "group_b_id",
        "conflict_action",
        "rationale",
        "active",
        "company_id",
        "operating_unit_id",
    ),
    # the decision (state, approver) is taken by the actions
    "fix.sod.mitigation": (
        "control_id",
        "user_id",
        "mitigating_control",
        "reason",
        "valid_from",
        "valid_until",
    ),
    # the measurement (result/violations/users_in_conflict) is computed
    "fix.sod.test": ("control_id",),
    # the holder is the caller; the decision, the clock and the closure are actions
    "fix.privileged.session": (
        "access_kind",
        "reason",
        "ticket_ref",
        "duration_hours",
        "actions_count",
    ),
    "fix.sensitive.field": (
        "model_name",
        "field_name",
        "sensitivity",
        "data_class",
        "masking_rule",
        "lawful_basis",
        "retention_note",
        "active",
    ),
    "res.device.log": (),
    # the access a joiner/mover grants is stated on the event (M29 capture
    # audit 2026-11-14): extra roles and the data scope; the preview is computed
    "fix.jml.event": (
        "event_type",
        "employee_id",
        "user_id",
        "role_id",
        "effective_on",
        "extra_role_ids",
        "operating_unit_ids",
        "default_operating_unit_id",
        "reason",
        "lang",
        "tz",
        "valid_until",
        "permission_line_ids",
        "permission_bulk",
    ),
    # narrowed module permissions are written by an applied event only
    "fix.module.permission": (),
    # the decision (decision/decided_on) is the reviewer's action only; only an
    # Access Approver or Access Rights admin writes this register at all (E4)
    "fix.access.certification": ("period", "user_id", "role_id", "reviewer_id", "due_on", "note"),
    "fix.access.certification.campaign": ("period", "due_on"),
    # state and the rotation dates change only through action_rotate
    "fix.encryption.key": (
        "code",
        "name",
        "purpose",
        "algorithm",
        "vault_ref",
        "rotations_per_year",
        "custodian_id",
    ),
    # system-written register: nothing may be typed
    "fix.security.audit": (),
    # severity is the two-person action; state/resolution are the lifecycle
    # severity is typed by the reporter at filing, and locked after (E15)
    "fix.security.incident": (
        "title",
        "category",
        "severity",
        "detected_at",
        "detected_by_id",
        "affected_user_id",
        "session_id",
        "description",
        "containment",
        "root_cause",
        "breach_assessment",
    ),
    # the lifecycle (state, remediation, verification, acceptance) is action-only;
    # severity is re-rated by a Security Officer only (the model refuses others)
    "fix.vulnerability": (
        "title",
        "source",
        "identifier",
        "component",
        "severity",
        "discovered_on",
        "owner_id",
        "detail",
    ),
    "ir.rule": (
        "name",
        "model_id",
        "fix_model_name",
        "domain_force",
        "perm_read",
        "perm_write",
        "perm_create",
        "perm_unlink",
    ),
    "ir.model.access": (
        "name",
        "model_id",
        "fix_model_name",
        "group_id",
        "perm_read",
        "perm_write",
        "perm_create",
        "perm_unlink",
    ),
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


def _caller_search(env, model, domain, order=None, limit=None):
    """Read as the CALLER (A12 P2): a figure a user may not read is
    withheld, never computed with sudo."""
    return env[model].search(domain, order=order, limit=limit)


def access_review(env, date_from=None, date_to=None, **params):
    """Per user: active flag, role count, group count, last login. Roles are what the
    user holds (assigned, on the employee master, or named by a group), not every role
    sharing one of their groups (E5). A colleague's access is for the people who review
    it; anyone else sees their own line (E25)."""
    Sod = env["fix.sod.control"]
    domain = [("share", "=", False)]
    if not (
        env.user.has_group("base.group_erp_manager")
        or env.user.has_group("cd_rbac_ext.group_access_approver")
    ):
        domain.append(("id", "=", env.uid))
    users = _caller_search(env, "res.users", domain)
    rows = []
    for user in users:
        codes = sorted(Sod.user_held_roles(user).mapped("code"))
        rows.append(
            {
                "login": user.login,
                "user": user.name,
                "roles": ", ".join(codes) or "—",
                "role_count": len(codes),
                "groups": len(user.sudo().group_ids),
                "last_login": user.login_date.strftime("%d %b %Y") if user.login_date else "Never",
                "active": "Yes" if user.active else "No",
            }
        )
    rows.sort(key=lambda r: (-r["role_count"], r["login"]))
    no_role = len([r for r in rows if r["role_count"] == 0])
    return _pack(
        "Access Review Pack — %d internal user(s), %d with no mapped role" % (len(rows), no_role),
        ["login", "user", "roles", "role_count", "groups", "last_login", "active"],
        {
            "login": "Login",
            "user": "User",
            "roles": "Business Roles",
            "role_count": "Roles",
            "groups": "Odoo Groups",
            "last_login": "Last Login",
            "active": "Active",
        },
        rows,
        [
            "Roles are what the user was actually given: an approved request or JML event, the "
            "employee master, or a group only one role maps to. A group several roles share names "
            "none of them. A user with groups and no role was given access outside the register: "
            "that is an access-review finding, not an error."
        ],
        empty="No internal users.",
    )


def privileged_sessions(env, date_from=None, date_to=None, **params):
    sessions = _caller_search(env, "fix.privileged.session", [])
    rows = []
    for s in sessions:
        rows.append(
            {
                "session": s.name,
                "user": s.user_id.login if s.user_id else "—",
                "kind": dict(s._fields["access_kind"].selection).get(s.access_kind),
                "reason": (s.reason or "")[:40],
                "ticket": s.ticket_ref or "—",
                "started": s.started_at.strftime("%d %b %H:%M") if s.started_at else "—",
                "minutes": s.duration_minutes if s.state == "closed" else "open",
                "state": dict(s._fields["state"].selection).get(s.state),
            }
        )
    open_count = len([r for r in rows if r["state"] == "Open"])
    return _pack(
        "Privileged Session Log — %d open of %d" % (open_count, len(rows)),
        ["session", "user", "kind", "reason", "ticket", "started", "minutes", "state"],
        {
            "session": "Session",
            "user": "User",
            "kind": "Access Kind",
            "reason": "Reason",
            "ticket": "Ticket",
            "started": "Started",
            "minutes": "Minutes",
            "state": "State",
        },
        rows,
        [
            "A privileged session is opened before sudo/admin work and closed after; duration is "
            "measured from the timestamps, not typed. Stale sessions are force-closed by the "
            "M29 timeout cron (fix_rbac_ext.privileged_session_timeout_minutes)."
        ],
        empty="No privileged sessions recorded.",
    )


def sensitive_access(env, date_from=None, date_to=None, **params):
    """Classified exposure surface: sensitive fields per class and the roles that
    can reach their model. Reads are NOT instrumented — this is exposure, stated."""
    fields_cls = _caller_search(env, "fix.sensitive.field", [("active", "=", True)])
    groups = {}
    for f in fields_cls:
        key = f.data_class
        g = groups.setdefault(key, {"fields": 0, "models": set(), "masked": 0})
        g["fields"] += 1
        g["models"].add(f.model_name)
        if f.masking_rule != "none":
            g["masked"] += 1
    labels = dict(env["fix.sensitive.field"]._fields["data_class"].selection)
    rows = []
    for key in sorted(groups):
        g = groups[key]
        rows.append(
            {
                "data_class": labels.get(key, key),
                "fields": g["fields"],
                "models": len(g["models"]),
                "masked": g["masked"],
                "unmasked": g["fields"] - g["masked"],
            }
        )
    return _pack(
        "Sensitive-Data Access — classified exposure surface (%d field(s))" % len(fields_cls),
        ["data_class", "fields", "models", "masked", "unmasked"],
        {
            "data_class": "Data Class",
            "fields": "Classified Fields",
            "models": "Models",
            "masked": "Masked",
            "unmasked": "Unmasked",
        },
        rows,
        [
            "Masking rules apply on the P03 screens (lists and forms) to callers without clearance; "
            "they do not apply to the Odoo back end, report packs or exports. Individual reads are "
            "not logged, so this pack reports the classified surface, not read counts: nothing "
            "here is estimated."
        ],
        empty="No sensitive fields classified yet.",
    )


def sod_results(env, date_from=None, date_to=None, **params):
    controls = _caller_search(env, "fix.sod.control", [("active", "=", True)])
    tests = _caller_search(env, "fix.sod.test", [])
    rows = []
    for control in controls:
        mine = tests.filtered(lambda t, c=control: t.control_id.id == c.id)
        latest = mine.sorted(lambda t: (t.tested_on or datetime.date.min, t.id), reverse=True)[:1]
        rows.append(
            {
                "code": control.code,
                "control": control.name,
                "role_a": control.pair_label,
                "role_b": dict(control._fields["control_type"].selection).get(
                    control.control_type, control.control_type
                )
                if "control_type" in control._fields
                else control.role_b_id.code,
                "action": dict(control._fields["conflict_action"].selection).get(
                    control.conflict_action, control.conflict_action
                ),
                "tests": len(mine),
                "last_tested": str(latest.tested_on) if latest else "—",
                "result": dict(latest._fields["result"].selection).get(latest.result)
                if latest and latest.result
                else "Not tested",
                "violations": latest.violations_found if latest else 0,
            }
        )
    failing = len([r for r in rows if r["result"] == "Fail"])
    return _pack(
        "SoD Test Results — %d control(s), %d failing" % (len(rows), failing),
        [
            "code",
            "control",
            "role_a",
            "role_b",
            "action",
            "tests",
            "last_tested",
            "result",
            "violations",
        ],
        {
            "code": "Code",
            "control": "Control",
            "role_a": "Conflicting pair",
            "role_b": "Pair type",
            "action": "Conflict Action",
            "tests": "Tests",
            "last_tested": "Last Tested",
            "result": "Result",
            "violations": "Conflicts",
        },
        rows,
        [
            "Each test measures users who hold BOTH roles: what was assigned, the employee master "
            "and groups that name a role. A job re-measures every control weekly; an untested "
            "control shows 'Not tested' rather than an assumed pass. A 'block' control refuses "
            "the grant unless an approved SoD exception covers it."
        ],
        empty="No active SoD controls.",
    )


def auth_trends(env, date_from=None, date_to=None, **params):
    """Login recency buckets from res.users.login_date — measured, not sampled."""
    users = _caller_search(env, "res.users", [("share", "=", False), ("active", "=", True)])
    now = datetime.datetime.now()
    buckets = [("today", 1), ("7d", 7), ("30d", 30), ("90d", 90), ("never", None)]
    rows = []
    for label, days in buckets:
        if days is None:
            count = len(users.filtered(lambda u: not u.login_date))
            name = "Never logged in"
        else:
            count = len(
                users.filtered(lambda u, d=days: u.login_date and (now - u.login_date).days <= d)
            )
            name = {
                "today": "Within 24 h",
                "7d": "1–7 days",
                "30d": "8–30 days",
                "90d": "31–90 days",
            }[label]
        rows.append({"bucket": name, "users": count})
    stale = len(users.filtered(lambda u: u.login_date and (now - u.login_date).days > 90))
    return _pack(
        "Authentication Trends — login recency (%d active internal users)" % len(users),
        ["bucket", "users"],
        {"bucket": "Last Login", "users": "Users"},
        rows,
        [
            "Buckets are cumulative from login_date. %d user(s) last logged in more than 90 days "
            "ago — the account-review trigger." % stale
        ],
        empty="No active internal users.",
    )


def sod_violations(env, date_from=None, date_to=None, **params):
    """A08 S4: who holds a conflicting pair today, mitigated or not, and the
    controls group membership cannot measure (fix.sod.control report)."""
    data = env["fix.sod.control"].fix_report_violations()
    rows = [
        {
            "control": r["control"],
            "pair": r["pair"],
            "login": r["login"],
            "mitigated": "Yes, %s until %s" % (r["exception"], r["exception_until"])
            if r["mitigated"]
            else "No",
        }
        for r in data["violations"]
    ]
    return _pack(
        "SoD Violations — %d user-pair(s), %d unmitigated, %d control(s) not measurable"
        % (len(rows), data["unmitigated"], len(data["unmeasurable"])),
        ["control", "pair", "login", "mitigated"],
        {
            "control": "Control",
            "pair": "Conflicting pair",
            "login": "User",
            "mitigated": "Mitigated",
        },
        rows,
        [
            "Existing conflicts are reported, not blocked; a new conflicting grant is refused "
            "unless an approved, unexpired SoD exception covers it."
        ],
        empty="No user holds a conflicting pair.",
    )


def vulnerability_register(env, date_from=None, date_to=None, **params):
    """Spec §14 "Vulnerability register": open findings by severity and age, the
    remediation due date, and the critical-open-past-due count (target zero,
    AC-23). Read as the caller: a reporter sees their own findings."""
    vulns = _caller_search(
        env, "fix.vulnerability", [], order="state, sla_due, id desc", limit=1000
    )
    labels = dict(env["fix.vulnerability"]._fields["state"].selection)
    rows = [
        {
            "name": v.name,
            "severity": v.severity,
            "source": v.source,
            "component": v.component,
            "discovered": v.discovered_on,
            "due": v.sla_due,
            "age": v.age_days,
            "overdue": "Yes" if v.is_overdue else "",
            "state": labels.get(v.state, v.state),
        }
        for v in vulns
    ]
    open_ = vulns.filtered(lambda v: v.state == "open")
    critical_late = open_.filtered(lambda v: v.severity == "critical" and v.is_overdue)
    return _pack(
        "Vulnerability Register - %d open, %d critical past due (target 0)"
        % (len(open_), len(critical_late)),
        ["name", "severity", "source", "component", "discovered", "due", "age", "overdue", "state"],
        {
            "name": "Reference",
            "severity": "Severity",
            "source": "Source",
            "component": "Component",
            "discovered": "Discovered",
            "due": "Remediation Due",
            "age": "Age (days)",
            "overdue": "Past Due",
            "state": "Status",
        },
        rows,
        [
            "Remediation due = discovered + the window for the severity: critical 7 days "
            "(BRU-SEC-21); high 30, medium 90 and low 180 days are working defaults the owner "
            "can change in the system settings. A critical finding open past its due date is "
            "escalated by the daily job. Closure needs a second person's verification."
        ],
        empty="No vulnerabilities recorded.",
    )


REPORTS = {
    "access_review": access_review,
    "vulnerability_register": vulnerability_register,
    "sod_violations": sod_violations,
    "privileged_sessions": privileged_sessions,
    "sensitive_access": sensitive_access,
    "sod_results": sod_results,
    "auth_trends": auth_trends,
}


def kpis(env):
    """Computed as the CALLER (A12 P2): no sudo().search([]) — a figure the
    caller may not read is withheld rather than invented."""

    def _count(model, domain):
        try:
            return env[model].search_count(domain)
        except AccessError:
            return 0

    users_active = _count("res.users", [("share", "=", False), ("active", "=", True)])
    requests = env["fix.access.request"].search([])
    sessions = env["fix.privileged.session"].search([])
    tests = env["fix.sod.test"].search([])
    vulns = env["fix.vulnerability"].search([("state", "=", "open"), ("severity", "=", "critical")])
    return {
        "users_active": users_active,
        "roles_active": _count("fix.role", [("active", "=", True)]),
        "requests_open": len(requests.filtered(lambda r: r.state in ("submitted", "approved"))),
        "sessions_open": len(sessions.filtered(lambda s: s.state == "open")),
        "sod_failures": len(tests.filtered(lambda t: t.result == "fail")),
        "sod_tests": len(tests),
        "critical_vulns_overdue": len(vulns.filtered("is_overdue")),
    }
