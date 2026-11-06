# A12 · M29 Identity, Access & Security — access review, privileged sessions,
# sensitive-data exposure, SoD results and authentication trends.
#
# Honest scope: reads of individual sensitive fields are not instrumented, so
# "Sensitive-Data Access" reports the CLASSIFIED EXPOSURE SURFACE (which fields
# are sensitive and which roles can reach their model) — never invented reads.
import datetime

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
    "res.users": {"order": "name", "limit": 400, "actions": set()},
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
    "res.device.log": {"order": "last_activity desc, id desc", "limit": 400, "actions": set()},
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
    "fix.encryption.key": {"order": "code", "limit": 200, "actions": set()},
    "fix.security.audit": {"order": "occurred_at desc, id desc", "limit": 500, "actions": set()},
    "fix.security.incident": {
        "order": "detected_at desc, id desc",
        "limit": 400,
        "actions": {"action_contain", "action_close"},
    },
    "ir.rule": {"order": "model_id, id", "limit": 400, "actions": set()},
    "ir.model.access": {"order": "model_id, id", "limit": 800, "actions": set()},
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


def access_review(env, date_from=None, date_to=None, **params):
    """Per user: active flag, role count, group count, last login."""
    users = env["res.users"].sudo().search([("share", "=", False)])
    Role = env["fix.role"].sudo()
    roles = Role.search([])
    group_to_role = {r.group_id.id: r for r in roles if r.group_id}
    rows = []
    for user in users:
        user_roles = [group_to_role[g.id].code for g in user.group_ids if g.id in group_to_role]
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
    sessions = env["fix.privileged.session"].sudo().search([])
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
            "measured from the timestamps, not typed."
        ],
        empty="No privileged sessions recorded.",
    )


def sensitive_access(env, date_from=None, date_to=None, **params):
    """Classified exposure surface: sensitive fields per class and the roles that
    can reach their model. Reads are NOT instrumented — this is exposure, stated."""
    fields_cls = env["fix.sensitive.field"].sudo().search([("active", "=", True)])
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
    controls = env["fix.sod.control"].sudo().search([("active", "=", True)])
    tests = env["fix.sod.test"].sudo().search([])
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
            "Each test measures users who actually hold BOTH roles' Odoo groups; an untested "
            "control shows 'Not tested' rather than an assumed pass."
        ],
        empty="No active SoD controls.",
    )


def auth_trends(env, date_from=None, date_to=None, **params):
    """Login recency buckets from res.users.login_date — measured, not sampled."""
    users = env["res.users"].sudo().search([("share", "=", False), ("active", "=", True)])
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


REPORTS = {
    "access_review": access_review,
    "sod_violations": sod_violations,
    "privileged_sessions": privileged_sessions,
    "sensitive_access": sensitive_access,
    "sod_results": sod_results,
    "auth_trends": auth_trends,
}


def kpis(env):
    users = env["res.users"].sudo().search([("share", "=", False), ("active", "=", True)])
    roles = env["fix.role"].sudo().search([("active", "=", True)])
    requests = env["fix.access.request"].sudo().search([])
    sessions = env["fix.privileged.session"].sudo().search([])
    tests = env["fix.sod.test"].sudo().search([])
    return {
        "users_active": len(users),
        "roles_active": len(roles),
        "requests_open": len(requests.filtered(lambda r: r.state in ("submitted", "approved"))),
        "sessions_open": len(sessions.filtered(lambda s: s.state == "open")),
        "sod_failures": len(tests.filtered(lambda t: t.result == "fail")),
        "sod_tests": len(tests),
    }
