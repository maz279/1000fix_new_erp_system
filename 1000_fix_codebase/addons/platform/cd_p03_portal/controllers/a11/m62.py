# A11 · M62 Data Platform & Governance — pipelines, runs, contracts, metrics,
# quality tests, incidents and retention cost. Packs read only measured rows.
import datetime

SURFACES = {
    "fix.data.pipeline": {
        "order": "code",
        "limit": 200,
        "actions": {"action_pause", "action_resume"},
    },
    "fix.data.run": {
        "order": "started_at desc, id desc",
        "limit": 500,
        "actions": {"action_finish", "action_fail"},
    },
    "fix.data.entity": {"order": "name", "limit": 300, "actions": set()},
    "fix.data.lineage": {"order": "lineage_order, id", "limit": 400, "actions": set()},
    "fix.data.contract": {
        "order": "dataset_code",
        "limit": 200,
        "actions": {"action_activate"},
    },
    "fix.metric.definition": {
        "order": "code",
        "limit": 300,
        "actions": {"action_publish"},
    },
    "fix.data.quality.rule": {"order": "name", "limit": 400, "actions": set()},
    "fix.data.quality.test": {"order": "checked_at desc, id desc", "limit": 500, "actions": set()},
    "fix.data.incident": {
        "order": "detected_at desc, id desc",
        "limit": 300,
        "actions": {"action_fix", "action_close"},
    },
    "fix.data.retention.policy": {"order": "entity_id", "limit": 300, "actions": set()},
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
    entities = env["fix.data.entity"].sudo().search([])
    rules = env["fix.data.quality.rule"].sudo().search([])
    tests = env["fix.data.quality.test"].sudo().search([])
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
    pipelines = env["fix.data.pipeline"].sudo().search([("state", "=", "active")])
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
    entities = env["fix.data.entity"].sudo().search([])
    lineage = env["fix.data.lineage"].sudo().search([])
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
    policies = env["fix.data.retention.policy"].sudo().search([("active", "=", True)])
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
    pipelines = env["fix.data.pipeline"].sudo().search([("state", "=", "active")])
    runs = env["fix.data.run"].sudo().search([])
    tests = env["fix.data.quality.test"].sudo().search([])
    incidents = env["fix.data.incident"].sudo().search([])
    contracts = env["fix.data.contract"].sudo().search([("state", "=", "active")])
    metrics = env["fix.metric.definition"].sudo().search([("state", "=", "published")])
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
