# A11 · M26 AI/ML Services — the surfaces the generic workspace endpoints may
# serve (SURFACES), the Model Accuracy & Retraining Log (REPORTS) and the
# module KPI payload (/p03/ml/kpis). Every number is a measured read of the
# real fix.ml.model / fix.ml.inference.run / fix.predictive.maintenance
# tables — accuracy columns stay honestly labelled until ground-truth
# capture exists.
import datetime
import logging
import re

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

# A Bengali grapheme anywhere in a fault-code row (E5: the 'Bengali
# classification: Live' claim is measured against this, not asserted).
_BENGALI_RE = re.compile(r"[ঀ-৿]")

SURFACES = {
    "fix.ml.model": {
        "order": "code",
        "limit": 50,
        "actions": set(),
    },
    "fix.ml.inference.run": {
        "order": "ran_at desc, id desc",
        "limit": 200,
        "actions": {"action_execute"},
        # G7/R01: a portal write may capture the HUMAN half of a run only —
        # the engine's half (state, output, latency, suggestion) is not
        # writable from any surface.
        "writable": {"final_value", "override_reason"},
    },
    "fix.predictive.maintenance": {
        "order": "write_date desc, id desc",
        "limit": 100,
        "actions": {"action_create_preventive_wo"},
        # E6/X03: the prediction list is read AS THE CALLER — OU record rules
        # apply, so operating unit B's predictions never leak onto unit A's
        # screen through this endpoint (the sudo read kept only the company
        # filter, which is not the caller's scope).
        "caller_scoped": True,
    },
    "fix.ml.model.version": {
        "order": "model_id, version desc",
        "limit": 200,
        # G7: state moves only through these actions (deploy lands via the
        # M63 inbox apply, never as a surface action).
        "actions": {"action_evaluate", "action_request_promotion", "action_retire"},
    },
    "fix.ml.evaluation.gate": {
        "order": "checked_at desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.ml.guardrail": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
}


def model_accuracy_retraining(env, **params):
    """The Model Accuracy & Retraining Log — per model: measured run counts,
    latency, last run. Honest scope note: accuracy needs ground-truth capture
    (dispatch suggestion adoption tracking) that lands with the M02
    iteration; nothing here is estimated."""
    runs = _runs(env)
    models = _models(env)
    week_ago = fields_datetime_now() - datetime.timedelta(days=7)
    rows = []
    for model in models:
        all_runs = runs.search([("model_id", "=", model.id)])
        week_runs = all_runs.filtered(lambda r, wa=week_ago: r.ran_at and r.ran_at >= wa)
        latencies = [r.latency_ms for r in all_runs if r.latency_ms]
        rows.append(
            {
                "code": model.code,
                "model": model.name,
                "implementation": model.implementation,
                "status": model.status,
                "runs_total": model.run_count,
                "runs_7d": len(week_runs),
                "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else None,
                "last_run": model.last_run_at.strftime("%d %b %H:%M") if model.last_run_at else "—",
            }
        )
    return {
        "title": "Model Accuracy & Retraining Log — measured runs (accuracy awaits ground-truth capture)",
        "cols": [
            "code",
            "model",
            "implementation",
            "status",
            "runs_total",
            "runs_7d",
            "avg_latency_ms",
            "last_run",
        ],
        "labels": {
            "code": "Code",
            "model": "Model",
            "implementation": "Implementation",
            "status": "Status",
            "runs_total": "Runs (total)",
            "runs_7d": "Runs (7d)",
            "avg_latency_ms": "Avg latency (ms)",
            "last_run": "Last run",
        },
        "rows": rows,
        "notes": [
            "Every engine here is deterministic and explainable; accuracy columns are added when "
            "suggestion-adoption ground truth is captured (M02 iteration).",
        ],
    }


def fields_datetime_now():
    from odoo import fields

    return fields.Datetime.now()


def _models(env):
    """E6: the registry is read AS THE CALLER — record rules hold the company
    scope; no sudo anywhere in the reads behind a KPI."""
    return env["fix.ml.model"].search([])


def _runs(env):
    return env["fix.ml.inference.run"]


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty or "No data in this basis yet.",
    }


def model_performance_pack(env, date_from=None, date_to=None, **params):
    """Per model: measured run volume, success rate, latency, last run."""
    runs = _runs(env)
    rows = []
    for model in _models(env):
        model_runs = runs.search([("model_id", "=", model.id)])
        computed = model_runs.filtered(lambda r: r.state == "computed")
        failed = model_runs.filtered(lambda r: r.state == "failed")
        lat = [r.latency_ms for r in computed if r.latency_ms]
        rows.append(
            {
                "code": model.code,
                "model": model.name,
                "implementation": model.implementation,
                "status": model.status,
                "runs": len(model_runs),
                "failed": len(failed),
                "success_pct": round(len(computed) / len(model_runs) * 100.0, 1)
                if model_runs
                else None,
                "avg_latency": round(sum(lat) / len(lat), 1) if lat else None,
                "last_run": model.last_run_at.strftime("%Y-%m-%d %H:%M")
                if model.last_run_at
                else "—",
            }
        )
    totals = {
        "code": "Total",
        "runs": sum(r["runs"] for r in rows),
        "failed": sum(r["failed"] for r in rows),
        "success_pct": round(
            sum(1 for r in rows if r["success_pct"] is not None)
            and (
                sum(r["success_pct"] or 0 for r in rows)
                / max(1, len([r for r in rows if r["success_pct"] is not None]))
            ),
            1,
        )
        if rows
        else None,
    }
    return _pack(
        "Model Performance Pack — measured runs, success and latency",
        [
            "code",
            "model",
            "implementation",
            "status",
            "runs",
            "failed",
            "success_pct",
            "avg_latency",
            "last_run",
        ],
        {
            "code": "Code",
            "model": "Model",
            "implementation": "Implementation",
            "status": "Status",
            "runs": "Runs",
            "failed": "Failed",
            "success_pct": "Success %",
            "avg_latency": "Avg Latency (ms)",
            "last_run": "Last Run",
        },
        rows,
        [
            "Success % = computed runs / all runs; latency is measured per run. "
            "Accuracy/F1 need suggestion-adoption ground truth and are never estimated here."
        ],
        totals=totals if rows else None,
    )


def override_analysis(env, date_from=None, date_to=None, **params):
    """Human-in-the-loop overrides: runs where the operator's final decision
    differs from the engine suggestion."""
    runs = _runs(env).search([("suggested_value", "!=", False)])
    by_model = {}
    for r in runs:
        row = by_model.setdefault(
            r.model_code or "?",
            {"code": r.model_code or "?", "decisions": 0, "overrides": 0, "reasons": set()},
        )
        row["decisions"] += 1
        if r.overridden:
            row["overrides"] += 1
            if r.override_reason:
                row["reasons"].add(r.override_reason)
    rows = []
    for row in by_model.values():
        rows.append(
            {
                "code": row["code"],
                "decisions": row["decisions"],
                "overrides": row["overrides"],
                "override_pct": round(row["overrides"] / row["decisions"] * 100.0, 1)
                if row["decisions"]
                else 0.0,
                "reasons": "; ".join(sorted(row["reasons"])) or "—",
            }
        )
    rows.sort(key=lambda r: -r["override_pct"])
    totals = {
        "code": "Total",
        "decisions": sum(r["decisions"] for r in rows),
        "overrides": sum(r["overrides"] for r in rows),
        "override_pct": round(
            sum(r["overrides"] for r in rows) / sum(r["decisions"] for r in rows) * 100.0, 1
        )
        if sum(r["decisions"] for r in rows)
        else 0.0,
    }
    return _pack(
        "Override Analysis — human decisions against engine suggestions",
        ["code", "decisions", "overrides", "override_pct", "reasons"],
        {
            "code": "Model",
            "decisions": "Decisions Recorded",
            "overrides": "Overridden",
            "override_pct": "Override %",
            "reasons": "Recorded Reasons",
        },
        rows,
        [
            "Ground truth is the operator's final decision captured on the run. "
            "A model with 0 recorded decisions has no override evidence yet."
        ],
        totals=totals if rows else None,
        empty="No human decisions captured yet — set Final Human Decision on an inference run.",
    )


def drift_report(env, date_from=None, date_to=None, **params):
    versions = env["fix.ml.model.version"].search([("drift_score", ">", 0.0)])
    rows = []
    for v in versions:
        rows.append(
            {
                "model": v.model_id.code,
                "version": v.version,
                "state": v.state,
                "drift_score": round(v.drift_score, 3),
                "band": "alert" if v.drift_score >= 0.2 else "watch",
                "deployed_at": v.deployed_at.strftime("%Y-%m-%d") if v.deployed_at else "—",
            }
        )
    rows.sort(key=lambda r: -r["drift_score"])
    return _pack(
        "Drift Report — observed drift per model version",
        ["model", "version", "state", "drift_score", "band", "deployed_at"],
        {
            "model": "Model",
            "version": "Version",
            "state": "State",
            "drift_score": "Drift Score",
            "band": "Band (≥0.2 = alert)",
            "deployed_at": "Deployed",
        },
        rows,
        [
            "Drift scores are keyed in from the monitoring run; no score is invented. "
            "Alert band is ≥ 0.2."
        ],
        empty="No drift observations recorded yet — key the monitoring score on a version.",
    )


def fairness_summary(env, date_from=None, date_to=None, **params):
    versions = env["fix.ml.model.version"].search([])
    counts = {"untested": 0, "passed": 0, "failed": 0}
    rows = []
    for v in versions:
        counts[v.bias_status] = counts.get(v.bias_status, 0) + 1
        failed_gates = v.gate_ids.filtered(lambda g: g.result == "failed")
        rows.append(
            {
                "model": v.model_id.code,
                "version": v.version,
                "bias": v.bias_status,
                "failed_gates": len(failed_gates),
                "state": v.state,
            }
        )
    totals = {
        "model": "Total",
        "bias": "%s passed / %s failed / %s untested"
        % (counts["passed"], counts["failed"], counts["untested"]),
        "failed_gates": sum(r["failed_gates"] for r in rows),
    }
    return _pack(
        "Fairness Summary — bias status and failed gates per version",
        ["model", "version", "bias", "failed_gates", "state"],
        {
            "model": "Model",
            "version": "Version",
            "bias": "Bias Test",
            "failed_gates": "Failed Gates",
            "state": "State",
        },
        rows,
        [
            "Bias status is recorded by the reviewer; 'untested' is shown as such, "
            "never silently treated as passed."
        ],
        totals=totals if rows else None,
        empty="No model versions registered yet.",
    )


def production_monitoring(env, date_from=None, date_to=None, **params):
    runs = _runs(env)
    week_ago = fields_datetime_now() - datetime.timedelta(days=7)
    week_runs = runs.search([("ran_at", ">=", week_ago)])
    rows = []
    for model in _models(env):
        mine = week_runs.filtered(lambda r, mid=model.id: r.model_id.id == mid)
        if not mine:
            continue
        lat = sorted(r.latency_ms for r in mine if r.latency_ms)
        p95 = lat[max(0, int(len(lat) * 0.95) - 1)] if lat else None
        failed = mine.filtered(lambda r: r.state == "failed")
        rows.append(
            {
                "code": model.code,
                "runs": len(mine),
                "failed": len(failed),
                "avg_latency": round(sum(lat) / len(lat), 1) if lat else None,
                "p95_latency": p95,
                "last_error": (failed[:1].error_note or "—") if failed else "—",
            }
        )
    return _pack(
        "Production Monitoring — last 7 days per model",
        ["code", "runs", "failed", "avg_latency", "p95_latency", "last_error"],
        {
            "code": "Model",
            "runs": "Runs (7d)",
            "failed": "Failed",
            "avg_latency": "Avg Latency (ms)",
            "p95_latency": "p95 Latency (ms)",
            "last_error": "Last Error",
        },
        rows,
        [
            "Latency is measured per run; p95 is the nearest-rank value of the "
            "window's successful runs."
        ],
        empty="No inference runs in the last 7 days.",
    )


def fallback_status(env, date_from=None, date_to=None, **params):
    runs = _runs(env)
    guardrails = env["fix.ml.guardrail"].search([("active", "=", True)])
    rows = []
    for model in _models(env):
        fallbacks = guardrails.filtered(
            lambda g, mid=model.id: g.model_id.id == mid and g.action == "fallback"
        )
        last_failed = runs.search(
            [("model_id", "=", model.id), ("state", "=", "failed")],
            order="ran_at desc",
            limit=1,
        )
        rows.append(
            {
                "code": model.code,
                "status": model.status,
                "fallback_rules": len(fallbacks),
                "last_failure": last_failed.ran_at.strftime("%Y-%m-%d %H:%M")
                if last_failed
                else "—",
                "last_error": (last_failed.error_note or "—") if last_failed else "—",
                "guardrail_rules": "; ".join(fallbacks.mapped("rule")) or "—",
            }
        )
    return _pack(
        "Inference Fallback — what happens when a model cannot answer",
        ["code", "status", "fallback_rules", "last_failure", "last_error", "guardrail_rules"],
        {
            "code": "Model",
            "status": "Status",
            "fallback_rules": "Fallback Rules",
            "last_failure": "Last Failure",
            "last_error": "Last Error",
            "guardrail_rules": "Fallback Conditions",
        },
        rows,
        [
            "A model with zero fallback rules has no deterministic path when it "
            "fails — configure one on the guard-rail screen."
        ],
    )


def genai_catalog(env, date_from=None, date_to=None, **params):
    """Self-hosted GenAI + RAG: honest capability status. No LLM endpoint is
    provisioned in this estate; the catalog says so instead of faking runs."""
    rows = [
        {
            "capability": "Self-hosted LLM inference",
            "status": "Porting phase",
            "detail": "No model endpoint provisioned — no generation is simulated.",
        },
        {
            "capability": "RAG over knowledge base (M61)",
            "status": "Porting phase",
            "detail": "Requires the vector index + LLM endpoint; neither exists yet.",
        },
    ]
    for model in _models(env).filtered(lambda m: m.kind in ("fault_classifier", "bi_aggregator")):
        rows.append(
            {
                "capability": model.name,
                "status": "Live (deterministic)",
                "detail": "Owning module %s — %s"
                % (model.owning_module or "n/a", model.implementation),
            }
        )
    return _pack(
        "Generative AI & RAG — capability status",
        ["capability", "status", "detail"],
        {"capability": "Capability", "status": "Status", "detail": "Detail"},
        rows,
        [
            "The platform's AI is deterministic and explainable. Generative "
            "features are listed with their true status — nothing is simulated."
        ],
    )


def bengali_nlp_catalog(env, date_from=None, date_to=None, **params):
    """Bengali NLP / OCR surfaces, measured (E5): the classifier runs a real
    token match, and the taxonomy's Bengali coverage is COUNTED per code —
    the old 'Live' claim was asserted; this row now carries its evidence."""
    runs = _runs(env)
    fault_models = _models(env).filtered(lambda m: m.kind == "fault_classifier")
    bengali_runs = runs.search([("model_id", "in", fault_models.ids)])
    codes = env["fix.fault.code"].search([("active", "=", True)])
    with_bn = [
        c.code for c in codes if _BENGALI_RE.search("%s %s" % (c.name or "", c.description or ""))
    ]
    coverage = "%d of %d active fault codes carry Bengali text" % (len(with_bn), len(codes))
    rows = [
        {
            "surface": "Bengali fault-text classification",
            "status": "Partial (token match; %s)" % coverage,
            "evidence": "The engine tokenises Bengali and English alike, but a "
            "match needs Bengali text in the taxonomy row. %d recorded "
            "inference run(s); engines: %s"
            % (
                len(bengali_runs),
                ", ".join(fault_models.mapped("code")) or "—",
            ),
        },
        {
            "surface": "Handwriting / document OCR",
            "status": "Not implemented",
            "evidence": "No OCR engine is provisioned; nothing is faked.",
        },
        {
            "surface": "Bengali speech / transliteration",
            "status": "Not implemented",
            "evidence": "No speech model in the estate.",
        },
    ]
    return _pack(
        "OCR & Bengali NLP — what actually runs",
        ["surface", "status", "evidence"],
        {"surface": "Surface", "status": "Status", "evidence": "Evidence"},
        rows,
        [
            "Bengali coverage above is counted live from fix.fault.code, not "
            "asserted. OCR and speech are declared gaps, not silent no-ops."
        ],
    )


REPORTS = {
    "model_accuracy_retraining": model_accuracy_retraining,
    "model_performance_pack": model_performance_pack,
    "override_analysis": override_analysis,
    "drift_report": drift_report,
    "fairness_summary": fairness_summary,
    "production_monitoring": production_monitoring,
    "fallback_status": fallback_status,
    "genai_catalog": genai_catalog,
    "bengali_nlp_catalog": bengali_nlp_catalog,
}


def _ml_kpis(env):
    """E6: every KPI is read AS THE CALLER under the caller's record rules
    (the sudo reads leaked every company's runs into the strip)."""
    runs = env["fix.ml.inference.run"]
    models = env["fix.ml.model"]
    week_ago = fields_datetime_now() - datetime.timedelta(days=7)
    week_runs = runs.search([("ran_at", ">=", week_ago)])
    latencies = [r.latency_ms for r in week_runs if r.latency_ms]
    alerts = env["fix.predictive.maintenance"].search_count(
        [("prediction", "=", "failure_predicted")]
    )
    decided = runs.search([("suggested_value", "!=", False)])
    overridden = decided.filtered(lambda r: r.overridden)
    try:
        drift_alerts = env["fix.ml.model.version"].search_count([("drift_score", ">=", 0.2)])
    except Exception:
        drift_alerts = None
    return {
        # registry KPI strip (M26 spec)
        "auto_assign_rate": None,  # needs dispatch-adoption ground truth
        "demand_mape": None,  # needs M15 consumption history + actuals
        "fault_f1": None,  # needs labelled fault ground truth
        "churn_auc": None,  # no churn model exists
        "override_rate": round(len(overridden) / len(decided) * 100.0, 1) if decided else None,
        "drift_alerts": drift_alerts,
        # measured extras
        "models_live": models.search_count([("status", "=", "production")]),
        "models_planned": models.search_count([("status", "=", "planned")]),
        "runs_7d": len(week_runs),
        "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else None,
        "predictive_alerts": alerts,
    }


class P03MlApi(http.Controller):
    """M26 live endpoints for the workspace shell."""

    @http.route("/p03/ml/kpis", type="jsonrpc", auth="user", readonly=True)
    def ml_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M26": _ml_kpis(request.env)}
