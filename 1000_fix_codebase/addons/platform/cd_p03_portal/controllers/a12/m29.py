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
    # personal data: record rules apply (A09 pattern) — a plain user sees
    # only their own device logs, and res.users reads respect Odoo's rules
    "res.users": {"order": "name", "limit": 400, "actions": set(), "rules": True},
    "fix.role": {"order": "code", "limit": 200, "actions": set()},
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
        "actions": {"action_close"},
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
    },
    "fix.access.certification": {
        "order": "period desc, id desc",
        "limit": 400,
        "actions": {"action_certify", "action_revoke"},
    },
    "fix.encryption.key": {
        "order": "code",
        "limit": 200,
        "actions": {"action_rotate"},
    },
    "fix.security.audit": {"order": "occurred_at desc, id desc", "limit": 500, "actions": set()},
    "fix.security.incident": {
        "order": "detected_at desc, id desc",
        "limit": 400,
        "actions": {"action_contain", "action_close", "action_set_severity"},
    },
    "ir.rule": {"order": "model_id, id", "limit": 400, "actions": set()},
    "ir.model.access": {"order": "model_id, id", "limit": 800, "actions": set()},
}

# A12 R4: the fields a workspace form may set through /p03/model/write —
# exactly what the forms in static/src/a12/m29.js offer as editable, minus
# every workflow-controlled field (those are action-only). Read-only screens
# declare an empty tuple: nothing the workspace can type on them.
WRITABLE = {
    "res.users": ("name", "login", "email", "phone", "active"),
    "fix.role": ("code", "name", "name_bn", "group_id", "keycloak_role", "active", "description"),
    "res.groups": (),
    "fix.field.rule": ("model_id", "field_id", "permission", "active"),
    "fix.isolation.tier": (
        "code",
        "name",
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
        "role_a_id",
        "role_b_id",
        "conflict_action",
        "rationale",
        "active",
    ),
    # the measurement (result/violations/users_in_conflict) is computed
    "fix.sod.test": ("control_id", "tested_on", "tested_by_id", "users_checked"),
    # closure stamps the end; duration is measured
    "fix.privileged.session": (
        "user_id",
        "access_kind",
        "reason",
        "ticket_ref",
        "started_at",
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
    "fix.jml.event": ("event_type", "employee_id", "user_id", "role_id", "effective_on"),
    # the decision (decision/decided_on) is the reviewer's action only
    "fix.access.certification": ("period", "user_id", "role_id", "reviewer_id", "note"),
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
    "fix.security.incident": (
        "title",
        "category",
        "detected_at",
        "detected_by_id",
        "affected_user_id",
        "session_id",
        "description",
        "containment",
        "root_cause",
        "breach_assessment",
    ),
    "ir.rule": (
        "name",
        "model_id",
        "domain_force",
        "perm_read",
        "perm_write",
        "perm_create",
        "perm_unlink",
    ),
    "ir.model.access": (
        "name",
        "model_id",
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
    """Per user: active flag, role count, group count, last login."""
    users = _caller_search(env, "res.users", [("share", "=", False)])
    roles = _caller_search(env, "fix.role", [])
    group_to_roles = {}
    for role in roles:
        for group in role.group_id | role.group_ids:
            group_to_roles.setdefault(group.id, []).append(role)
    rows = []
    for user in users:
        user_roles = [r.code for g in user.group_ids for r in group_to_roles.get(g.id, [])]
        rows.append(
            {
                "login": user.login,
                "user": user.name,
                "roles": ", ".join(sorted(set(user_roles))) or "—",
                "role_count": len(set(user_roles)),
                "groups": len(user.group_ids),
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
            "Roles are the business roles (fix.role) mapped to the user's Odoo groups; a user with "
            "no mapped role is an access-review finding, not an error."
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
            "Scope note: field-level reads are not instrumented in this build. This pack reports "
            "the classified surface (which fields are sensitive and whether a masking rule is set), "
            "not read counts — nothing here is estimated."
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
                "role_a": control.role_a_id.code,
                "role_b": control.role_b_id.code,
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
            "role_a": "Role A",
            "role_b": "Role B",
            "action": "Conflict Action",
            "tests": "Tests",
            "last_tested": "Last Tested",
            "result": "Result",
            "violations": "Conflicts",
        },
        rows,
        [
            "Each test measures users who actually hold BOTH roles' Odoo groups; an untested "
            "control shows 'Not tested' rather than an assumed pass. Grants are blocked at "
            "the gate for every 'block' control."
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


REPORTS = {
    "access_review": access_review,
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
    return {
        "users_active": users_active,
        "roles_active": _count("fix.role", [("active", "=", True)]),
        "requests_open": len(requests.filtered(lambda r: r.state in ("submitted", "approved"))),
        "sessions_open": len(sessions.filtered(lambda s: s.state == "open")),
        "sod_failures": len(tests.filtered(lambda t: t.result == "fail")),
        "sod_tests": len(tests),
    }
