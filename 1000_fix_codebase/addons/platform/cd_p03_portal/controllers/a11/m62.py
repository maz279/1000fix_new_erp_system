# A11 · M62 Data Platform & Governance — pipelines, runs, contracts, metrics,
# quality tests, incidents and retention cost. Packs read only measured rows.
#
# A11 audit E6 (M62-11): every pack and KPI is the CALLER's read — the user's
# own record rules apply and every source with a company is filtered by the
# caller's allowed companies. Only the explicit "BI company-wide" charter
# (m25._read) gets elevated reads.
import datetime

from .m25 import _bi_domain, _read

# A11 audit S2 (M62-13): the fields /p03/model/write accepts on each M62
# surface — exactly what the M62 workspace forms (static/src/a11/m62.js)
# offer as editable. Workflow fields (states, stamps, the success rate, the
# thresholds the engine owns) are never listed: they change only through
# their actions. The ACL still decides who may write at all: the governance
# rule book (entities, lineage, rules, contracts, metrics, retention) is the
# Data Governance Officer's; pipelines, runs and incidents stay writable for
# the operational flows and carry their own model guards.
WRITABLE = {
    "fix.data.pipeline": frozenset(
        {
            "code",
            "name",
            "source_system",
            "target_entity_id",
            "load_mode",
            "schedule",
            "freshness_sla_minutes",
            "data_source_id",
            "layer",
            "owner_id",
            "upstream_ids",
        }
    ),
    "fix.data.run": frozenset(
        {
            "pipeline_id",
            "kind",
            "stage",
            "started_at",
            "rows_read",
            "rows_written",
            "rows_rejected",
            "period_from",
            "period_to",
            "replay_of_run_id",
            "reason",
        }
    ),
    "fix.data.entity": frozenset(
        {
            "name",
            "entity_type",
            "owner_module",
            "steward_id",
            "classification",
            "retention_policy",
            "res_model",
            "warehouse_layer",
            "model_kind",
            "grain_declaration",
            "description",
        }
    ),
    "fix.data.lineage": frozenset(
        {
            "name",
            "company_id",
            "source_entity_id",
            "target_entity_id",
            "operating_unit_id",
            "lineage_order",
            "transformation",
        }
    ),
    "fix.data.contract": frozenset(
        {
            "dataset_code",
            "name",
            "entity_id",
            "producer",
            "consumers",
            "schema_version",
            "freshness_sla_minutes",
            "breaking_change_notice_days",
            "guarantees",
            "producer_signatory_id",
            "data_source_id",
        }
    ),
    "fix.metric.definition": frozenset(
        {"code", "name", "domain_area", "grain", "source_entity_id", "owner_role", "definition"}
    ),
    # A version is DRAFTED from a form (M62 capture audit 2026-11-18: with an
    # empty list no version could be drafted in the workspace, so no metric
    # could ever be published there). Its state, review and publication
    # stamps and the impact list are never on it: they come from its actions.
    "fix.metric.version": frozenset(
        {"definition_id", "definition_text", "grain", "source_entity_id", "change_reason"}
    ),
    "fix.metric.consumer": frozenset({"definition_id", "consumer", "consumer_type", "note"}),
    "fix.data.quality.rule": frozenset(
        {
            "name",
            "entity_id",
            "rule_type",
            "threshold",
            "active",
            "check_field",
            "freshness_window_hours",
            "severity",
        }
    ),
    # The threshold is NOT form-editable: the evidence row records the rule's
    # threshold at run time (the model stamps it whatever the caller sends).
    "fix.data.quality.test": frozenset({"rule_id", "checked_at", "observed_value", "note"}),
    "fix.data.incident": frozenset(
        {
            "title",
            "entity_id",
            "rule_id",
            "severity",
            "detected_at",
            "owner_id",
            "description",
            "resolution",
            "root_cause",
            "classification",
        }
    ),
    "fix.data.retention.policy": frozenset(
        {
            "entity_id",
            "tier",
            "retention_months",
            "volume_gb",
            "storage_cost_per_gb",
            "purge_rule",
            "active",
            "statutory_floor_months",
            "legal_hold",
        }
    ),
    # The request itself; its approval and expiry are the engine's.
    "fix.data.declassification.auth": frozenset(
        {"entity_id", "from_classification", "to_classification", "reason", "expires_on"}
    ),
    "fix.data.purge.evidence": frozenset(),
    # M62 capture audit 2026-11-18: the registers each page lacked.
    "fix.data.source": frozenset(
        {
            "code",
            "name",
            "source_type",
            "owner_module",
            "connection_ref",
            "business_owner_id",
            "steward_id",
            "active_from",
            "description",
        }
    ),
    "fix.data.dimension": frozenset(
        {
            "name",
            "entity_id",
            "natural_key",
            "surrogate_key_strategy",
            "scd_type",
            "tracked_attributes",
            "attributes",
            "source_master_module",
            "fact_entity_ids",
        }
    ),
    "fix.glossary.term": frozenset(
        {
            "term_en",
            "term_bn",
            "definition",
            "definition_bn",
            "owner_id",
            "synonyms",
            "metric_ids",
            "entity_ids",
        }
    ),
    # Layer by layer while open; completion is the officer's action.
    "fix.data.erasure": frozenset(
        {
            "request_id",
            "bronze_done",
            "silver_done",
            "gold_done",
            "feature_store_done",
            "extracts_done",
            "evidence_ref",
            "note",
        }
    ),
}

SURFACES = {
    "fix.data.pipeline": {
        "order": "code",
        "limit": 200,
        "actions": {"action_pause", "action_resume"},
        "writable": WRITABLE["fix.data.pipeline"],
    },
    "fix.data.run": {
        "order": "started_at desc, id desc",
        "limit": 500,
        "actions": {"action_finish", "action_fail"},
        "writable": WRITABLE["fix.data.run"],
    },
    "fix.data.entity": {
        "order": "name",
        "limit": 300,
        "actions": set(),
        "writable": WRITABLE["fix.data.entity"],
    },
    "fix.data.lineage": {
        "order": "lineage_order, id",
        "limit": 400,
        "actions": set(),
        "writable": WRITABLE["fix.data.lineage"],
    },
    "fix.data.contract": {
        "order": "dataset_code, version desc",
        "limit": 200,
        # action_activate is GONE from the surface on purpose (A11 audit G1):
        # activation runs only from an approved M63 task, never a click.
        "actions": {"action_producer_sign", "action_new_version", "action_request_approval"},
        "writable": WRITABLE["fix.data.contract"],
    },
    "fix.metric.definition": {
        "order": "code",
        "limit": 300,
        "actions": {"action_retire"},
        "writable": WRITABLE["fix.metric.definition"],
    },
    # G2: a metric publishes through its VERSION (steward review, then an
    # approved request), never a direct publish button on the definition.
    "fix.metric.version": {
        "order": "definition_id, version desc",
        "limit": 300,
        "actions": {"action_steward_review", "action_request_approval"},
        "writable": WRITABLE["fix.metric.version"],
    },
    "fix.metric.consumer": {
        "order": "definition_id, consumer",
        "limit": 400,
        "actions": set(),
        "writable": WRITABLE["fix.metric.consumer"],
    },
    "fix.data.quality.rule": {
        "order": "name",
        "limit": 400,
        "actions": {"action_measure"},
        "writable": WRITABLE["fix.data.quality.rule"],
    },
    "fix.data.quality.test": {
        "order": "checked_at desc, id desc",
        "limit": 500,
        "actions": set(),
        "writable": WRITABLE["fix.data.quality.test"],
    },
    "fix.data.incident": {
        "order": "detected_at desc, id desc",
        "limit": 300,
        "actions": {"action_fix", "action_close"},
        "writable": WRITABLE["fix.data.incident"],
    },
    "fix.data.retention.policy": {
        "order": "entity_id",
        "limit": 300,
        "actions": {"action_request_shorten", "action_purge"},
        "writable": WRITABLE["fix.data.retention.policy"],
    },
    # G6: the routed, time-limited authorisation a classification downgrade
    # needs; G5: the append-only disposition evidence.
    "fix.data.declassification.auth": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_request_approval"},
        "writable": WRITABLE["fix.data.declassification.auth"],
    },
    "fix.data.purge.evidence": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": set(),
        "writable": WRITABLE["fix.data.purge.evidence"],
    },
    # M62 capture audit 2026-11-18.
    "fix.data.source": {
        "order": "code",
        "limit": 300,
        "actions": {"action_activate", "action_retire"},
        "writable": WRITABLE["fix.data.source"],
    },
    "fix.data.dimension": {
        "order": "name",
        "limit": 300,
        "actions": set(),
        "writable": WRITABLE["fix.data.dimension"],
    },
    "fix.glossary.term": {
        "order": "term_en",
        "limit": 500,
        "actions": set(),
        "writable": WRITABLE["fix.glossary.term"],
    },
    "fix.data.erasure": {
        "order": "requested_at desc, id desc",
        "limit": 300,
        "actions": {"action_complete"},
        "writable": WRITABLE["fix.data.erasure"],
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


def quality_scorecard(env, date_from=None, date_to=None, **params):
    """Per entity: rules defined, tests run, pass rate over the latest test of
    each rule. 'Never tested' is stated as such, never counted as a pass."""
    entities = _read(env, "fix.data.entity").search(_bi_domain(env, "fix.data.entity", []))
    rules = _read(env, "fix.data.quality.rule").search(_bi_domain(env, "fix.data.quality.rule", []))
    tests = _read(env, "fix.data.quality.test").search(_bi_domain(env, "fix.data.quality.test", []))
    rows = []
    for entity in entities:
        my_rules = rules.filtered(lambda r, e=entity: r.entity_id.id == e.id)
        my_tests = tests.filtered(lambda t, ids=my_rules.ids: t.rule_id.id in ids)
        latest = []
        for rule in my_rules:
            mine = my_tests.filtered(lambda t, rid=rule.id: t.rule_id.id == rid)
            if mine:
                latest.append(
                    mine.sorted(lambda t: (t.checked_at or datetime.datetime.min, t.id))[-1]
                )
        passed = len([t for t in latest if t.passed])
        rows.append(
            {
                "entity": entity.name,
                "owner": entity.owner_module or "—",
                "classification": dict(entity._fields["classification"].selection).get(
                    entity.classification, entity.classification
                )
                if entity.classification
                else "—",
                "rules": len(my_rules),
                "tested": len(latest),
                "passed": passed,
                "pass_pct": round(100.0 * passed / len(latest), 1) if latest else None,
            }
        )
    rows.sort(key=lambda r: (r["pass_pct"] is None, r["pass_pct"] or 0.0))
    untested = len([r for r in rows if r["rules"] and not r["tested"]])
    return _pack(
        "Data Quality Scorecard — %d entit(ies), %d with untested rules" % (len(rows), untested),
        ["entity", "owner", "classification", "rules", "tested", "passed", "pass_pct"],
        {
            "entity": "Entity",
            "owner": "Owning Module",
            "classification": "Classification",
            "rules": "Rules",
            "tested": "Rules Tested",
            "passed": "Passed",
            "pass_pct": "Pass %",
        },
        rows,
        [
            "Pass rate uses the latest test per rule. An entity whose rules were never run shows "
            "no pass rate — it is not assumed green."
        ],
        empty="No data entities registered.",
    )


def freshness_sla(env, date_from=None, date_to=None, **params):
    pipelines = _read(env, "fix.data.pipeline").search(
        _bi_domain(env, "fix.data.pipeline", [("state", "=", "active")])
    )
    now = datetime.datetime.now()
    rows = []
    for p in pipelines:
        age_min = None
        if p.last_success_at:
            age_min = int((now - p.last_success_at).total_seconds() // 60)
        breach = (
            age_min is not None and p.freshness_sla_minutes and age_min > p.freshness_sla_minutes
        )
        rows.append(
            {
                "pipeline": p.code,
                "source": p.source_system,
                "mode": dict(p._fields["load_mode"].selection).get(p.load_mode),
                "schedule": dict(p._fields["schedule"].selection).get(p.schedule),
                "sla_min": p.freshness_sla_minutes,
                "age_min": age_min if age_min is not None else "never",
                "breach": "Yes" if breach else ("No" if age_min is not None else "—"),
            }
        )
    rows.sort(key=lambda r: (r["breach"] != "Yes", r["pipeline"]))
    breaches = len([r for r in rows if r["breach"] == "Yes"])
    return _pack(
        "Freshness SLA — %d active pipeline(s), %d breaching" % (len(rows), breaches),
        ["pipeline", "source", "mode", "schedule", "sla_min", "age_min", "breach"],
        {
            "pipeline": "Pipeline",
            "source": "Source",
            "mode": "Load Mode",
            "schedule": "Schedule",
            "sla_min": "SLO (min)",
            "age_min": "Age (min)",
            "breach": "Breaching",
        },
        rows,
        [
            "Age is measured from the last successful run to now; 'never' means the pipeline has "
            "not completed once, which is itself a finding."
        ],
        empty="No active pipelines.",
    )


def lineage_coverage(env, date_from=None, date_to=None, **params):
    entities = _read(env, "fix.data.entity").search(_bi_domain(env, "fix.data.entity", []))
    lineage = _read(env, "fix.data.lineage").search(_bi_domain(env, "fix.data.lineage", []))
    covered = len(
        set(lineage.mapped("source_entity_id").ids) | set(lineage.mapped("target_entity_id").ids)
    )
    rows = []
    for entity in entities:
        incoming = lineage.filtered(lambda ln, e=entity: ln.target_entity_id.id == e.id)
        outgoing = lineage.filtered(lambda ln, e=entity: ln.source_entity_id.id == e.id)
        rows.append(
            {
                "entity": entity.name,
                "owner": entity.owner_module or "—",
                "upstream": len(incoming),
                "downstream": len(outgoing),
                "documented": "Yes" if (incoming or outgoing) else "No",
            }
        )
    rows.sort(key=lambda r: (r["documented"] == "Yes", r["entity"]))
    return _pack(
        "Lineage Coverage — %d of %d entit(ies) have documented lineage" % (covered, len(entities)),
        ["entity", "owner", "upstream", "downstream", "documented"],
        {
            "entity": "Entity",
            "owner": "Owning Module",
            "upstream": "Upstream Links",
            "downstream": "Downstream Links",
            "documented": "Documented",
        },
        rows,
        [
            "Coverage counts entities that appear as a source or target of at least one lineage edge. "
            "An entity with no edge is a lineage gap, listed rather than omitted."
        ],
        empty="No data entities registered.",
    )


def cost_per_domain(env, date_from=None, date_to=None, **params):
    policies = _read(env, "fix.data.retention.policy").search(
        _bi_domain(env, "fix.data.retention.policy", [("active", "=", True)])
    )
    groups = {}
    for pol in policies:
        domain = pol.entity_id.owner_module or "unassigned"
        g = groups.setdefault(domain, {"entities": 0, "volume": 0.0, "cost": 0.0, "hot": 0})
        g["entities"] += 1
        g["volume"] += pol.volume_gb or 0.0
        g["cost"] += pol.monthly_cost or 0.0
        if pol.tier == "hot":
            g["hot"] += 1
    rows = [
        {
            "domain": k,
            "entities": v["entities"],
            "hot": v["hot"],
            "volume_gb": round(v["volume"], 2),
            "monthly_cost": round(v["cost"], 2),
            "annual_cost": round(v["cost"] * 12.0, 2),
        }
        for k, v in sorted(groups.items(), key=lambda kv: -kv[1]["cost"])
    ]
    total = round(sum(r["monthly_cost"] for r in rows), 2)
    return _pack(
        "Cost per Domain — BDT %.2f per month across %d domain(s)" % (total, len(rows)),
        ["domain", "entities", "hot", "volume_gb", "monthly_cost", "annual_cost"],
        {
            "domain": "Domain",
            "entities": "Entities",
            "hot": "Hot Tier",
            "volume_gb": "Volume (GB)",
            "monthly_cost": "Monthly (BDT)",
            "annual_cost": "Annual (BDT)",
        },
        rows,
        [
            "Cost = current volume x the policy's storage rate. It is a measured projection from the "
            "declared volume, not a cloud bill."
        ],
        totals={
            "domain": "Total",
            "monthly_cost": total,
            "annual_cost": round(total * 12.0, 2),
            "volume_gb": round(sum(r["volume_gb"] for r in rows), 2),
        },
        empty="No retention policies.",
    )


REPORTS = {
    "quality_scorecard": quality_scorecard,
    "freshness_sla": freshness_sla,
    "lineage_coverage": lineage_coverage,
    "cost_per_domain": cost_per_domain,
}


def kpis(env):
    pipelines = _read(env, "fix.data.pipeline").search(
        _bi_domain(env, "fix.data.pipeline", [("state", "=", "active")])
    )
    runs = _read(env, "fix.data.run").search(_bi_domain(env, "fix.data.run", []))
    tests = _read(env, "fix.data.quality.test").search(_bi_domain(env, "fix.data.quality.test", []))
    incidents = _read(env, "fix.data.incident").search(_bi_domain(env, "fix.data.incident", []))
    contracts = _read(env, "fix.data.contract").search(
        _bi_domain(env, "fix.data.contract", [("state", "=", "active")])
    )
    metrics = _read(env, "fix.metric.definition").search(
        _bi_domain(env, "fix.metric.definition", [("state", "=", "published")])
    )
    return {
        "pipelines_active": len(pipelines),
        "runs_24h": len(
            runs.filtered(
                lambda r: r.started_at
                and r.started_at >= datetime.datetime.now() - datetime.timedelta(hours=24)
            )
        ),
        "runs_failed": len(runs.filtered(lambda r: r.state == "failed")),
        "quality_tests": len(tests),
        "quality_failures": len(tests.filtered(lambda t: not t.passed)),
        "incidents_open": len(incidents.filtered(lambda i: i.state == "open")),
        "contracts_active": len(contracts),
        "metrics_published": len(metrics),
    }
