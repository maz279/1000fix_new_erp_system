# A12 · M64 Master Data Management — steward requests, DQ rules and governed
# code lists, with packs computed from the same records.
#
# A12 workflow audit (2026-11-04) R4: every surface declares what
# /p03/model/write may set (WRITABLE, merged by controllers/a12/__init__.py);
# workflow fields (state, decision…) are NEVER in it, and the reports and
# KPIs below read as the CALLER (no sudo().search([])) - the caller's ACL
# decides what they see.
import datetime

SURFACES = {
    "fix.mdm.steward": {
        "order": "created_at desc, id desc",
        "limit": 300,
        # action_approve AND the rejection both run from the M63 approver's
        # inbox (P1-2): the task carries the decision note as its comment, so
        # the record has no Reject button either. Review routes it, Apply lands it.
        "actions": {
            "action_review",
            "action_request_approval",
            "action_recall_approval",
            "action_apply",
        },
    },
    "fix.mdm.dq.rule": {"order": "code", "limit": 300, "actions": {"action_evaluate"}},
    "fix.mdm.code.list": {
        "order": "code",
        "limit": 200,
        "actions": {"action_publish", "action_retire", "action_new_version"},
    },
    "fix.mdm.code.entry": {"order": "list_id, value", "limit": 500, "actions": set()},
    "fix.mdm.duplicate": {
        "order": "score desc, id desc",
        "limit": 400,
        "actions": {
            "action_merge",
            "action_keep_separate",
            "action_false_positive",
            "action_sync_merge_state",
        },
    },
    "fix.mdm.xref": {"order": "code_list, source_value", "limit": 500, "actions": set()},
    "fix.mdm.golden.rule": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.mdm.stewardship": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_audit_data_quality"},
    },
    "fix.mdm.change.request": {
        "order": "id desc",
        "limit": 400,
        # action_approve runs from the routed approval inbox, not a button.
        "actions": {
            "action_submit",
            "action_request_approval",
            "action_recall_approval",
            "action_reject",
            "action_cancel",
            "action_apply",
        },
    },
    "fix.mdm.match.rule": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.mdm.governed.attribute": {
        "order": "model_name, category, field_name",
        "limit": 300,
        "actions": set(),
    },
}

# R4: the fields a user may legitimately type. Everything else - state,
# decision, measured scores, evaluator results, decision stamps - is set by
# the workflow actions and the server, never by the form endpoint.
WRITABLE = {
    "fix.mdm.steward": (
        "request_type",
        "res_model",
        "record_ref",
        "reason",
        "proposed_changes",
        "merge_with_ref",
        "steward_id",
    ),
    "fix.mdm.dq.rule": (
        "code",
        "name",
        "res_model",
        "field_name",
        "rule_type",
        "expression",
        "severity",
        "active",
    ),
    "fix.mdm.code.list": ("code", "name", "domain_area", "version", "effective_from"),
    "fix.mdm.code.entry": (
        "list_id",
        "value",
        "label",
        "label_bn",
        "active",
        "effective_from",
        "effective_to",
    ),
    # score is measured by the detection run (E18), never typed.
    "fix.mdm.duplicate": (
        "res_model",
        "record_a_ref",
        "record_b_ref",
        "match_factors",
        "decision_note",
    ),
    "fix.mdm.xref": (
        "code_list",
        "source_system",
        "source_value",
        "canonical_value",
        "canonical_label",
        "confidence",
        "active",
    ),
    "fix.mdm.golden.rule": (
        "sequence",
        "model_name",
        "field_name",
        "strategy",
        "priority_source_ids",
        "description",
        "active",
    ),
    "fix.mdm.stewardship": ("name", "domain", "lead_steward_id", "owner_id", "operating_unit_id"),
    "fix.mdm.change.request": (
        "title",
        "description",
        "model_name",
        "record_id",
        "proposed_changes",
        "priority",
        "review_notes",
        "operating_unit_id",
    ),
    "fix.mdm.match.rule": (
        "sequence",
        "model_name",
        "field_name",
        "match_type",
        "weight",
        "normalize",
        "description",
        "active",
    ),
    "fix.mdm.governed.attribute": (
        "model_name",
        "field_name",
        "category",
        "block_direct_edit",
        "note",
        "active",
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


def steward_backlog(env, date_from=None, date_to=None, **params):
    reqs = env["fix.mdm.steward"].search([])
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
    rules = env["fix.mdm.dq.rule"].search([])
    rows = [
        {
            "code": r.code,
            "name": r.name,
            "model": r.res_model,
            "field": r.field_name,
            "type": dict(r._fields["rule_type"].selection).get(r.rule_type),
            "severity": dict(r._fields["severity"].selection).get(r.severity),
            "active": "Yes" if r.active else "No",
            "violations": r.last_violation_count if r.last_status == "ok" else "—",
            "checked": r.last_records_checked if r.last_status == "ok" else "—",
            "last_status": dict(r._fields["last_status"].selection).get(r.last_status, "—")
            if r.last_status
            else "never run",
        }
        for r in rules
    ]
    return _pack(
        "Data Quality Rule Register",
        [
            "code",
            "name",
            "model",
            "field",
            "type",
            "severity",
            "active",
            "violations",
            "checked",
            "last_status",
        ],
        {
            "code": "Code",
            "name": "Rule",
            "model": "Master Model",
            "field": "Field",
            "type": "Rule Type",
            "severity": "Severity",
            "active": "Active",
            "violations": "Violations",
            "checked": "Records Checked",
            "last_status": "Last Run",
        },
        rows,
        [
            "Rules declare the DQ expectation per master field; the violations and record "
            "counts are MEASURED by the evaluator (action_evaluate / the daily cron), "
            "never asserted. A rule for a missing model or field runs as 'skipped'.",
        ],
        empty="No DQ rules defined.",
    )


def code_list_usage(env, date_from=None, date_to=None, **params):
    lists = env["fix.mdm.code.list"].search([])
    rows = [
        {
            "code": c.code,
            "name": c.name,
            "domain": c.domain_area or "—",
            "version": c.version or "—",
            "entries": len(c.entry_ids),
            "active_entries": len(c.entry_ids.filtered(lambda e: e.active)),
            "state": dict(c._fields["state"].selection).get(c.state, c.state),
        }
        for c in lists
    ]
    return _pack(
        "Governed Code Lists",
        ["code", "name", "domain", "version", "entries", "active_entries", "state"],
        {
            "code": "List Code",
            "name": "List",
            "domain": "Domain",
            "version": "Version",
            "entries": "Entries",
            "active_entries": "Active Entries",
            "state": "State",
        },
        rows,
        [
            "Governed code lists are the single source for pickers; values are unique "
            "inside each list (database UNIQUE). A PUBLISHED list is frozen: changes "
            "ship as a new version (P1-2).",
        ],
        empty="No code lists defined.",
    )


def golden_coverage(env, date_from=None, date_to=None, **params):
    """Golden-record coverage: which master models have active DQ rules."""
    rules = env["fix.mdm.dq.rule"].search([("active", "=", True)])
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
    rules = env["fix.mdm.dq.rule"].search([])
    requests = env["fix.mdm.steward"].search([])
    dups = env["fix.mdm.duplicate"].search([])
    xrefs = env["fix.mdm.xref"].search([])
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
    entities = env["fix.data.entity"].search([])
    lineage = env["fix.data.lineage"].search([])
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
    """Data quality per master domain: the active rules, their severity mix
    and the MEASURED outcome of the evaluator's latest run. A domain with no
    rule is listed as ungoverned rather than omitted."""
    rules = env["fix.mdm.dq.rule"].search([("active", "=", True)])
    domains = {}
    for rule in rules:
        key = (rule.res_model or "").split(".")[-1].replace("_", " ").title() or "Unassigned"
        d = domains.setdefault(
            key,
            {
                "rules": 0,
                "critical": 0,
                "major": 0,
                "minor": 0,
                "fields": set(),
                "violations": 0,
                "skipped": 0,
                "errors": 0,
                "never_run": 0,
            },
        )
        d["rules"] += 1
        d[rule.severity if rule.severity in ("critical", "major", "minor") else "major"] += 1
        d["fields"].add(rule.field_name)
        if rule.last_status == "ok":
            d["violations"] += rule.last_violation_count or 0
        elif rule.last_status == "skipped":
            d["skipped"] += 1
        elif rule.last_status == "error":
            d["errors"] += 1
        else:
            d["never_run"] += 1
    rows = [
        {
            "domain": k,
            "rules": v["rules"],
            "critical": v["critical"],
            "major": v["major"],
            "minor": v["minor"],
            "fields": len(v["fields"]),
            "violations": v["violations"],
            "skipped": v["skipped"],
            "errors": v["errors"],
            "never_run": v["never_run"],
        }
        for k, v in sorted(domains.items(), key=lambda kv: -kv[1]["rules"])
    ]
    return {
        "title": "Data Quality by Domain - %d rule(s) over %d domain(s)" % (len(rules), len(rows)),
        "cols": [
            "domain",
            "rules",
            "critical",
            "major",
            "minor",
            "fields",
            "violations",
            "skipped",
            "errors",
            "never_run",
        ],
        "labels": {
            "domain": "Master Domain",
            "rules": "DQ Rules",
            "critical": "Critical",
            "major": "Major",
            "minor": "Minor",
            "fields": "Fields Covered",
            "violations": "Measured Violations",
            "skipped": "Skipped Rules",
            "errors": "Errored Rules",
            "never_run": "Never Run",
        },
        "rows": rows,
        "notes": [
            "Violations are the evaluator's MEASURED counts from its latest run (the daily "
            "cron / action_evaluate). A master domain with no active rule is ungoverned "
            "and does not appear here - the gap is visible by absence. Skipped rules "
            "target a model or field that is not installed (e.g. a stale res.partner "
            "rule) and are reported, not silently counted clean.",
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
    reqs = env["fix.mdm.steward"].search([])
    rules = env["fix.mdm.dq.rule"].search([("active", "=", True)])
    lists = env["fix.mdm.code.list"].search([("state", "=", "published")])
    entries = env["fix.mdm.code.entry"].search([])
    change_requests = env["fix.mdm.change.request"].search([])
    candidates = env["fix.mdm.duplicate"].search([("decision", "=", "pending")])
    return {
        "steward_open": len(reqs.filtered(lambda r: r.state in ("submitted", "in_review"))),
        "steward_total": len(reqs),
        "change_requests_open": len(
            change_requests.filtered(lambda r: r.state in ("submitted", "under_review", "approved"))
        ),
        "change_requests_applied": len(
            change_requests.filtered(lambda r: r.state == "implemented")
        ),
        "duplicates_pending": len(candidates),
        "dq_rules": len(rules),
        "dq_violations_measured": sum(r.last_violation_count or 0 for r in rules),
        "dq_rules_never_run": len(rules.filtered(lambda r: not r.last_status)),
        "code_lists": len(lists),
        "code_entries": len(entries),
    }
