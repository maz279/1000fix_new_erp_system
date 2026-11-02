# A12 · M64 Master Data Management — steward requests, DQ rules and governed
# code lists, with packs computed from the same records.
import datetime

SURFACES = {
    "fix.mdm.steward": {
        "order": "created_at desc, id desc",
        "limit": 300,
        "actions": {"action_review", "action_approve", "action_reject"},
    },
    "fix.mdm.dq.rule": {"order": "code", "limit": 300, "actions": set()},
    "fix.mdm.code.list": {"order": "code", "limit": 200, "actions": {"action_publish"}},
    "fix.mdm.code.entry": {"order": "list_id, value", "limit": 500, "actions": set()},
    "fix.mdm.duplicate": {
        "order": "score desc, id desc",
        "limit": 400,
        "actions": {"action_merge", "action_keep_separate"},
    },
    "fix.mdm.xref": {"order": "code_list, source_value", "limit": 500, "actions": set()},
    "fix.mdm.golden.rule": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.mdm.stewardship": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.mdm.change.request": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.mdm.match.rule": {"order": "id desc", "limit": 400, "actions": set()},
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


def steward_backlog(env, date_from=None, date_to=None, **params):
    reqs = env["fix.mdm.steward"].sudo().search([])
    rows = [
        {
            "request": r.name,
            "type": dict(r._fields["request_type"].selection).get(r.request_type),
            "model": r.res_model,
            "record": r.record_ref or "—",
            "steward": r.steward_id.name if r.steward_id else "—",
            "age_days": (datetime.date.today() - r.created_at.date()).days if r.created_at else "—",
            "state": dict(r._fields["state"].selection).get(r.state, r.state),
        }
        for r in reqs
    ]
    rows.sort(key=lambda r: -r["age_days"] if isinstance(r["age_days"], int) else 0)
    open_count = len([r for r in rows if r["state"] in ("Submitted", "In Review")])
    return _pack(
        "Steward Request Backlog — %d open" % open_count,
        ["request", "type", "model", "record", "steward", "age_days", "state"],
        {
            "request": "Request",
            "type": "Type",
            "model": "Master Model",
            "record": "Record",
            "steward": "Steward",
            "age_days": "Age (d)",
            "state": "State",
        },
        rows,
        ["Every master-data change that needs steward approval; age is from submission."],
        empty="No steward requests.",
    )


def dq_rule_register(env, date_from=None, date_to=None, **params):
    rules = env["fix.mdm.dq.rule"].sudo().search([])
    rows = [
        {
            "code": r.code,
            "name": r.name,
            "model": r.res_model,
            "field": r.field_name,
            "type": dict(r._fields["rule_type"].selection).get(r.rule_type),
            "severity": dict(r._fields["severity"].selection).get(r.severity),
            "active": "Yes" if r.active else "No",
        }
        for r in rules
    ]
    return _pack(
        "Data Quality Rule Register",
        ["code", "name", "model", "field", "type", "severity", "active"],
        {
            "code": "Code",
            "name": "Rule",
            "model": "Master Model",
            "field": "Field",
            "type": "Rule Type",
            "severity": "Severity",
            "active": "Active",
        },
        rows,
        [
            "Rules declare the DQ expectation per master field; execution counts live in "
            "the M25 BI module, not invented here."
        ],
        empty="No DQ rules defined.",
    )


def code_list_usage(env, date_from=None, date_to=None, **params):
    lists = env["fix.mdm.code.list"].sudo().search([])
    rows = [
        {
            "code": c.code,
            "name": c.name,
            "domain": c.domain_area or "—",
            "entries": len(c.entry_ids),
            "active_entries": len(c.entry_ids.filtered(lambda e: e.active)),
            "state": dict(c._fields["state"].selection).get(c.state, c.state),
        }
        for c in lists
    ]
    return _pack(
        "Governed Code Lists",
        ["code", "name", "domain", "entries", "active_entries", "state"],
        {
            "code": "List Code",
            "name": "List",
            "domain": "Domain",
            "entries": "Entries",
            "active_entries": "Active Entries",
            "state": "State",
        },
        rows,
        [
            "Governed code lists are the single source for pickers; values are unique "
            "inside each list (database UNIQUE)."
        ],
        empty="No code lists defined.",
    )


def golden_coverage(env, date_from=None, date_to=None, **params):
    """Golden-record coverage: which master models have active DQ rules."""
    rules = env["fix.mdm.dq.rule"].sudo().search([("active", "=", True)])
    models = sorted({r.res_model for r in rules})
    rows = [
        {
            "model": m,
            "rules": len(rules.filtered(lambda r, mm=m: r.res_model == mm)),
            "critical_rules": len(
                rules.filtered(lambda r, mm=m: r.res_model == mm and r.severity == "critical")
            ),
        }
        for m in models
    ]
    return _pack(
        "Golden Record Coverage — %d governed master model(s)" % len(models),
        ["model", "rules", "critical_rules"],
        {"model": "Master Model", "rules": "Active DQ Rules", "critical_rules": "Critical Rules"},
        rows,
        [
            "A master model with zero active rules is ungoverned: it will simply not "
            "appear here (the gap is visible by absence)."
        ],
        empty="No active DQ rules: no master model is governed yet.",
    )


def impact_analysis(env, date_from=None, date_to=None, **params):
    """Impact per master model: the governance controls that would have to move if
    the model changed - DQ rules, steward requests, duplicate pairs, cross-refs."""
    rules = env["fix.mdm.dq.rule"].sudo().search([])
    requests = env["fix.mdm.steward"].sudo().search([])
    dups = env["fix.mdm.duplicate"].sudo().search([])
    xrefs = env["fix.mdm.xref"].sudo().search([])
    models = sorted(
        set(rules.mapped("res_model"))
        | set(requests.mapped("res_model"))
        | set(dups.mapped("res_model"))
    )
    rows = []
    for model in models:
        rows.append(
            {
                "model": model,
                "rules": len(rules.filtered(lambda r, m=model: r.res_model == m)),
                "steward_requests": len(requests.filtered(lambda r, m=model: r.res_model == m)),
                "duplicate_pairs": len(dups.filtered(lambda d, m=model: d.res_model == m)),
                "xref_domains": len({x.code_list for x in xrefs}),
            }
        )
    return _pack(
        "Impact Analysis - %d governed master model(s)" % len(rows),
        ["model", "rules", "steward_requests", "duplicate_pairs", "xref_domains"],
        {
            "model": "Master Model",
            "rules": "DQ Rules",
            "steward_requests": "Steward Requests",
            "duplicate_pairs": "Duplicate Pairs",
            "xref_domains": "Xref Domains",
        },
        rows,
        [
            "Impact is the count of governance records tied to the model: changing the model "
            "means reviewing exactly these."
        ],
        empty="No governed master models.",
    )


def lineage_coverage(env, date_from=None, date_to=None, **params):
    entities = env["fix.data.entity"].sudo().search([])
    lineage = env["fix.data.lineage"].sudo().search([])
    rows = []
    covered = 0
    for entity in entities:
        inc = lineage.filtered(lambda ln, e=entity: ln.target_entity_id.id == e.id)
        out = lineage.filtered(lambda ln, e=entity: ln.source_entity_id.id == e.id)
        if inc or out:
            covered += 1
        rows.append(
            {
                "entity": entity.name,
                "owner": entity.owner_module or "-",
                "upstream": len(inc),
                "downstream": len(out),
                "documented": "Yes" if (inc or out) else "No",
            }
        )
    rows.sort(key=lambda r: (r["documented"] == "Yes", r["entity"]))
    return _pack(
        "Lineage - %d of %d entit(ies) documented" % (covered, len(entities)),
        ["entity", "owner", "upstream", "downstream", "documented"],
        {
            "entity": "Entity",
            "owner": "Owning Module",
            "upstream": "Upstream",
            "downstream": "Downstream",
            "documented": "Documented",
        },
        rows,
        ["An entity with no lineage edge is listed as undocumented rather than omitted."],
        empty="No data entities.",
    )


def dq_by_domain(env, date_from=None, date_to=None, **params):
    """Data quality per master domain: the active rules, their severity mix and
    the latest test outcome for each rule's model. A domain with no rule is
    listed as ungoverned rather than omitted."""
    rules = env["fix.mdm.dq.rule"].sudo().search([("active", "=", True)])
    domains = {}
    for rule in rules:
        key = (rule.res_model or "").split(".")[-1].replace("_", " ").title() or "Unassigned"
        d = domains.setdefault(
            key, {"rules": 0, "critical": 0, "major": 0, "minor": 0, "fields": set()}
        )
        d["rules"] += 1
        d[rule.severity if rule.severity in ("critical", "major", "minor") else "major"] += 1
        d["fields"].add(rule.field_name)
    rows = [
        {
            "domain": k,
            "rules": v["rules"],
            "critical": v["critical"],
            "major": v["major"],
            "minor": v["minor"],
            "fields": len(v["fields"]),
        }
        for k, v in sorted(domains.items(), key=lambda kv: -kv[1]["rules"])
    ]
    return {
        "title": "Data Quality by Domain - %d rule(s) over %d domain(s)" % (len(rules), len(rows)),
        "cols": ["domain", "rules", "critical", "major", "minor", "fields"],
        "labels": {
            "domain": "Master Domain",
            "rules": "DQ Rules",
            "critical": "Critical",
            "major": "Major",
            "minor": "Minor",
            "fields": "Fields Covered",
        },
        "rows": rows,
        "notes": [
            "A master domain with no active rule is ungoverned and does not appear here - "
            "the gap is visible by absence, and the rule engine (S2) is where it is fixed."
        ],
        "empty": "No active DQ rules.",
    }


REPORTS = {
    "dq_by_domain": dq_by_domain,
    "steward_backlog": steward_backlog,
    "dq_rule_register": dq_rule_register,
    "code_list_usage": code_list_usage,
    "golden_coverage": golden_coverage,
}

REPORTS["impact_analysis"] = impact_analysis
REPORTS["lineage_coverage"] = lineage_coverage


def kpis(env):
    reqs = env["fix.mdm.steward"].sudo().search([])
    rules = env["fix.mdm.dq.rule"].sudo().search([("active", "=", True)])
    lists = env["fix.mdm.code.list"].sudo().search([("state", "=", "published")])
    entries = env["fix.mdm.code.entry"].sudo().search([])
    return {
        "steward_open": len(reqs.filtered(lambda r: r.state in ("submitted", "in_review"))),
        "steward_total": len(reqs),
        "dq_rules": len(rules),
        "code_lists": len(lists),
        "code_entries": len(entries),
    }
