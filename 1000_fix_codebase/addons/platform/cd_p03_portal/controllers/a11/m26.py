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

# The specification's portfolio (FR-AIM-018..031) names 14 models. The label
# "(14 models)" is an owner decision and stays; the portfolio pack reports the
# MEASURED counts beside it (A2-F01: 7 rows existed, 9 spec models had none).
_PORTFOLIO_SPEC_MODELS = 14


def _labels(env, model_name, field_name):
    """A selection field's labels, read from the model definition itself — the
    same source /p03/model/records labels the grids with. A pack must print
    the label, never the raw enum key (D-L06: `live_engine`, `production`,
    `deployed`, `untested` were shown where the grids showed words)."""
    field = env[model_name]._fields.get(field_name)
    if field is None or field.type != "selection":
        return {}
    return dict(field._description_selection(env))


def _safe_caller_search(env, model_name, domain, order=None):
    """Read a register another area owns, AS THE CALLER, inside a savepoint:
    the screen's status must degrade to its declared static state when the
    model is absent or refuses the read, never 500 the whole pack."""
    if model_name not in env:
        return []
    try:
        with env.cr.savepoint():
            return list(env[model_name].search(domain, order=order))
    except Exception:
        _logger.warning(
            "M26: could not read %s as the caller — the catalog falls back to its static text",
            model_name,
        )
        return []

SURFACES = {
    # Capture audit 2026-11-14: every M26 form surface now declares what its
    # form may write (R3). Without it the Model Version form posted `state`
    # (a selection with a default) and the model's lifecycle guard refused
    # every create AND every edit - no version could be registered and no
    # model card written from the workspace.
    "fix.ml.model": {
        "order": "code",
        "limit": 50,
        "actions": set(),
        "writable": {
            "code",
            "name",
            "kind",
            "implementation",
            "status",
            "owning_module",
            "notes",
            "purpose",
            "consumer_modules",
            "accuracy_target",
            "fallback_definition",
            "risk_class",
            "owner_id",
            "review_date",
            "min_history_months",
            "min_volume",
        },
    },
    "fix.ml.inference.run": {
        "order": "ran_at desc, id desc",
        "limit": 200,
        "actions": {"action_execute"},
        # G7/R01: a portal write may capture the HUMAN half of a run only —
        # the engine's half (state, output, latency, suggestion) is not
        # writable from any surface. The request half (model, input, field
        # order) is human too: without it the +New run form cannot create.
        "writable": {"model_id", "input_text", "field_order_id", "final_value", "override_reason"},
    },
    "fix.predictive.maintenance": {
        "order": "write_date desc, id desc",
        "limit": 100,
        # M48 capture audit (2026-11-17) FR-IOT-044: the outcome of a prediction
        # no intervention acted on.
        "actions": {"action_create_preventive_wo", "action_record_outcome"},
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
        # state / approver / deploy date move only through the actions above;
        # the drift score follows the drift observations
        "writable": {
            "model_id",
            "version",
            "artifact_ref",
            "training_dataset",
            "training_run_id",
            "metrics_json",
            # bias_status follows the bias test (capture audit pass 2)
            "bias_notes",
            "deployment_mode",
            "model_card",
        },
    },
    "fix.ml.evaluation.gate": {
        "order": "checked_at desc, id desc",
        "limit": 200,
        "actions": set(),
        "writable": {"version_id", "gate", "result", "notes"},
    },
    "fix.ml.guardrail": {
        "order": "name",
        "limit": 200,
        "actions": set(),
        "writable": {"name", "model_id", "rule", "threshold", "action", "active", "note"},
    },
    # Deployment & Monitoring evidence (capture audit 2026-11-14)
    "fix.ml.fallback.test": {
        "order": "tested_at desc, id desc",
        "limit": 200,
        "actions": set(),
        "writable": {
            "model_id",
            "consumer_module",
            "method",
            "consumer_behaviour",
            "outcome",
            "incidents_raised",
            "tested_at",
        },
    },
    "fix.ml.drift.observation": {
        "order": "observed_at desc, id desc",
        "limit": 200,
        "actions": set(),
        "writable": {
            "version_id",
            "feature_name",
            "psi",
            "ks_statistic",
            "threshold",
            "observed_at",
            "note",
        },
    },
    # The AI risk register (Portfolio & Governance, GenAI & RAG)
    "fix.ml.ai.risk": {
        "order": "review_date, id desc",
        "limit": 200,
        "actions": set(),
        "writable": {
            "name",
            "model_id",
            "category",
            "description",
            "likelihood",
            "impact",
            "treatment",
            "control_ref",
            "owner_id",
            "review_date",
            "state",
        },
    },
    # Capture audit pass 2 (2026-11-19): the lifecycle evidence the Training
    # Pipelines, Evaluation Gates and Deployment & Monitoring pages capture.
    # Each is append-only; the stamps (trained_by, evaluated_by, documented_by,
    # recorded_by) and derived results are never writable.
    "fix.ml.training.run": {
        "order": "ended_at desc, id desc",
        "limit": 200,
        "actions": set(),
        "writable": {
            "model_id",
            "code_version",
            "data_snapshot_ref",
            "feature_versions",
            "hyperparameters",
            "environment_ref",
            "started_at",
            "ended_at",
            "outcome",
            "metrics_json",
            "failure_note",
            "m06_data_excluded",
        },
    },
    "fix.ml.data.sufficiency": {
        "order": "evaluated_at desc, id desc",
        "limit": 200,
        "actions": set(),
        "writable": {
            "model_id",
            "observed_history_months",
            "observed_volume",
            "source_modules",
            "deferred_until",
            "prerequisite_note",
            "evaluated_at",
        },
    },
    "fix.ml.bias.test": {
        "order": "tested_at desc, id desc",
        "limit": 200,
        "actions": set(),
        "writable": {
            "version_id",
            "segments_tested",
            "metric_by_segment",
            "max_disparity",
            "assessment",
            "notes",
            "tested_at",
            "next_due",
        },
    },
    "fix.ml.performance.observation": {
        "order": "period_end desc, id desc",
        "limit": 200,
        "actions": set(),
        "writable": {
            "version_id",
            "period_start",
            "period_end",
            "metric_name",
            "value",
            "target",
            "floor",
            "higher_is_better",
            "labelled_sample_size",
            "note",
        },
    },
}


def model_accuracy_retraining(env, **params):
    """The Model Accuracy & Retraining Log — per model: measured run counts,
    latency, last run. Honest scope note: accuracy needs ground-truth capture
    (dispatch suggestion adoption tracking) that lands with the M02
    iteration; nothing here is estimated."""
    runs = _runs(env)
    models = _models(env)
    outcome_labels = _labels(env, "fix.ml.training.run", "outcome")
    implementation_labels = _labels(env, "fix.ml.model", "implementation")
    status_labels = _labels(env, "fix.ml.model", "status")
    week_ago = fields_datetime_now() - datetime.timedelta(days=7)
    rows = []
    for model in models:
        all_runs = runs.search([("model_id", "=", model.id)])
        week_runs = all_runs.filtered(lambda r, wa=week_ago: r.ran_at and r.ran_at >= wa)
        latencies = [r.latency_ms for r in all_runs if r.latency_ms]
        trainings = env["fix.ml.training.run"].search(
            [("model_id", "=", model.id)], order="ended_at desc, id desc"
        )
        perf = env["fix.ml.performance.observation"].search(
            [("model_id", "=", model.id)], order="period_end desc, id desc", limit=1
        )
        rows.append(
            {
                "training_runs": len(trainings),
                "last_training": "%s (%s)"
                % (
                    trainings[0].ended_at.strftime("%d %b %Y"),
                    outcome_labels.get(trainings[0].outcome, trainings[0].outcome),
                )
                if trainings
                else "never",
                "last_performance": "%s %s (floor %s)%s"
                % (perf.metric_name, perf.value, perf.floor, " BREACH" if perf.breached else "")
                if perf
                else "not measured",
                "code": model.code,
                "model": model.name,
                "implementation": implementation_labels.get(
                    model.implementation, model.implementation
                ),
                "status": status_labels.get(model.status, model.status),
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
            "training_runs",
            "last_training",
            "last_performance",
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
            "training_runs": "Training runs",
            "last_training": "Last training",
            "last_performance": "Last production metric",
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
    implementation_labels = _labels(env, "fix.ml.model", "implementation")
    status_labels = _labels(env, "fix.ml.model", "status")
    rows = []
    computed_total = 0
    runs_total = 0
    for model in _models(env):
        model_runs = runs.search([("model_id", "=", model.id)])
        computed = model_runs.filtered(lambda r: r.state == "computed")
        failed = model_runs.filtered(lambda r: r.state == "failed")
        lat = [r.latency_ms for r in computed if r.latency_ms]
        computed_total += len(computed)
        runs_total += len(model_runs)
        rows.append(
            {
                "code": model.code,
                "model": model.name,
                "implementation": implementation_labels.get(
                    model.implementation, model.implementation
                ),
                "status": status_labels.get(model.status, model.status),
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
    # A2-F14(a): with no run anywhere the success ratio has no denominator —
    # it is None ("—"), never 0%, which would read as "every run failed".
    totals = {
        "code": "Total",
        "runs": runs_total,
        "failed": sum(r["failed"] for r in rows),
        "success_pct": round(computed_total / runs_total * 100.0, 1) if runs_total else None,
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
    """Human-in-the-loop overrides: runs on which a person RECORDED a final
    decision, and how many of those differ from the engine suggestion.

    A2-F07: the denominator is the run with a `final_value` — a suggestion
    nobody acted on is not a decision. The old basis (every run carrying a
    suggestion) reported 439 'decisions' and 0.0% override while no human had
    ever looked: a model can look never-overridden when it was never reviewed.
    With no decision recorded the ratio is None ('—'), never 0.0."""
    runs = _runs(env).search([("final_value", "!=", False)])
    decided = runs.filtered(lambda r: (r.final_value or "").strip())
    by_model = {}
    for r in decided:
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
                else None,
                "reasons": "; ".join(sorted(row["reasons"])) or "—",
            }
        )
    rows.sort(key=lambda r: -(r["override_pct"] or 0.0))
    total_decisions = sum(r["decisions"] for r in rows)
    totals = {
        "code": "Total",
        "decisions": total_decisions,
        "overrides": sum(r["overrides"] for r in rows),
        "override_pct": round(sum(r["overrides"] for r in rows) / total_decisions * 100.0, 1)
        if total_decisions
        else None,
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
            "Ground truth is the operator's final decision captured on the run; a run "
            "with no final decision is a suggestion nobody acted on and is not counted. "
            "A model with 0 recorded decisions has no override evidence yet — '—', not 0%."
        ],
        totals=totals if rows else None,
        empty="No human decisions captured yet — set Final Human Decision on an inference run.",
    )


def drift_report(env, date_from=None, date_to=None, **params):
    versions = env["fix.ml.model.version"].search([("drift_score", ">", 0.0)])
    state_labels = _labels(env, "fix.ml.model.version", "state")
    rows = []
    for v in versions:
        rows.append(
            {
                "model": v.model_id.code,
                "version": v.version,
                "state": state_labels.get(v.state, v.state),
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
    bias_labels = _labels(env, "fix.ml.model.version", "bias_status")
    state_labels = _labels(env, "fix.ml.model.version", "state")
    counts = {"untested": 0, "passed": 0, "failed": 0}
    rows = []
    for v in versions:
        counts[v.bias_status] = counts.get(v.bias_status, 0) + 1
        failed_gates = v.gate_ids.filtered(lambda g: g.result == "failed")
        rows.append(
            {
                "model": v.model_id.code,
                "version": v.version,
                "bias": bias_labels.get(v.bias_status, v.bias_status),
                "failed_gates": len(failed_gates),
                "state": state_labels.get(v.state, v.state),
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
            "Bias status follows the newest bias test, documented by someone who neither "
            "registered the version nor owns the model; 'untested' is shown as such, "
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
    status_labels = _labels(env, "fix.ml.model", "status")
    outcome_labels = _labels(env, "fix.ml.fallback.test", "outcome")
    # BRU-AIM-06: a fallback counts when it was TESTED - the newest test per model
    tests = env["fix.ml.fallback.test"].search([], order="tested_at desc, id desc")
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
        last_test = tests.filtered(lambda t, mid=model.id: t.model_id.id == mid)[:1]
        rows.append(
            {
                "code": model.code,
                "status": status_labels.get(model.status, model.status),
                "fallback": model.fallback_definition or "not declared",
                "last_test": last_test.tested_at.strftime("%Y-%m-%d") if last_test else "never",
                "test_outcome": outcome_labels.get(last_test.outcome, last_test.outcome)
                if last_test
                else "—",
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
        [
            "code",
            "status",
            "fallback",
            "last_test",
            "test_outcome",
            "fallback_rules",
            "last_failure",
            "last_error",
            "guardrail_rules",
        ],
        {
            "code": "Model",
            "status": "Status",
            "fallback": "Defined Fallback",
            "last_test": "Last Fallback Test",
            "test_outcome": "Test Outcome",
            "fallback_rules": "Fallback Rules",
            "last_failure": "Last Failure",
            "last_error": "Last Error",
            "guardrail_rules": "Fallback Conditions",
        },
        rows,
        [
            "A model with zero fallback rules has no deterministic path when it "
            "fails — configure one on the guard-rail screen.",
            "BRU-AIM-06: every consumer needs a TESTED fallback — record each test "
            "with Record Fallback Test (Deployment & Monitoring).",
        ],
    )


def genai_catalog(env, date_from=None, date_to=None, **params):
    """Self-hosted GenAI + RAG: the status is DERIVED from M32's provider
    register and its ask log (A2-F12), read as the caller in a savepoint —
    the old two static rows claimed no endpoint existed while the estate
    held an active self-hosted chat provider, and could never go stale.
    With no generation ever served, the measured count says exactly that;
    when the model is not installed, the declared static text stands."""
    rows = []
    provider_installed = "fix.assistant.llm.provider" in env
    if provider_installed:
        state_labels = _labels(env, "fix.assistant.llm.provider", "state")
        residency_labels = _labels(env, "fix.assistant.llm.provider", "residency")
        profile_labels = _labels(env, "fix.assistant.llm.provider", "latency_profile")
        providers = _safe_caller_search(env, "fix.assistant.llm.provider", [], order="sequence, id")
        asks = _safe_caller_search(env, "fix.assistant.ask", [], order="asked_at desc, id desc")
        active = [p for p in providers if p.state == "active" and p.active]
        for provider in providers:
            rows.append(
                {
                    "capability": "LLM provider — %s (%s)" % (provider.name, provider.code),
                    "status": state_labels.get(provider.state, provider.state),
                    "detail": "Residency: %s · profile: %s · model: %s · endpoint key: %s · "
                    "may receive customer context: %s"
                    % (
                        residency_labels.get(provider.residency, provider.residency),
                        profile_labels.get(provider.latency_profile, provider.latency_profile),
                        provider.model_name or "—",
                        provider.endpoint_config_key or "—",
                        "yes" if provider.may_receive_customer_context else "no",
                    ),
                }
            )
        generated = [a for a in asks if a.engine == "llm"]
        refused = [a for a in asks if a.engine == "refused"]
        grounded = [a for a in asks if a.engine == "rule_grounder"]
        rows.append(
            {
                "capability": "Generative answers served (measured)",
                "status": "%d generation(s) served" % len(generated),
                "detail": "%d ask record(s) in total — %d answered by a rule grounder, "
                "%d refused. A configured provider is not a generation: this count is "
                "the evidence." % (len(asks), len(grounded), len(refused)),
            }
        )
        rows.append(
            {
                "capability": "RAG over knowledge base (M61)",
                "status": "Not implemented",
                "detail": "No vector index exists in the estate; %d provider(s) configured "
                "(%d active). Grounding today is M32's ORM grounder."
                % (len(providers), len(active)),
            }
        )
    else:
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
    implementation_labels = _labels(env, "fix.ml.model", "implementation")
    for model in _models(env).filtered(lambda m: m.kind in ("fault_classifier", "bi_aggregator")):
        rows.append(
            {
                "capability": model.name,
                "status": "Live (deterministic)",
                "detail": "Owning module %s — %s"
                % (
                    model.owning_module or "n/a",
                    implementation_labels.get(model.implementation, model.implementation),
                ),
            }
        )
    return _pack(
        "Generative AI & RAG — capability status",
        ["capability", "status", "detail"],
        {"capability": "Capability", "status": "Status", "detail": "Detail"},
        rows,
        [
            "The platform's AI is deterministic and explainable. The provider rows and "
            "the generation count are read live from M32's register and ask log "
            "(as the caller) — nothing is simulated, and the status cannot go stale."
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
            "asserted. The measured taxonomy holds %d active fault code(s) — the "
            "catalog's old fixed-count note was stale (A2-F14c). OCR and speech "
            "are declared gaps, not silent no-ops." % len(codes),
        ],
    )


def portfolio_summary(env):
    """The Model Portfolio's honest summary line, computed from the registry
    (A2-F01/A2-F08): the '(14 models)' title is an owner decision, so the
    screen states the MEASURED counts beside the specification's number."""
    models = _models(env)
    live = models.filtered(lambda m: m.status == "production")
    planned = models.filtered(lambda m: m.status == "planned")
    return (
        "%d registered · %d live · %d planned — the specification's portfolio "
        "names %d models; the rest are not registered yet."
        % (len(models), len(live), len(planned), _PORTFOLIO_SPEC_MODELS)
    )


def model_portfolio(env, date_from=None, date_to=None, **params):
    """The Model Portfolio, computed: the honest summary line as the title and
    one row per registered model with the grids' labels."""
    models = _models(env)
    kind_labels = _labels(env, "fix.ml.model", "kind")
    implementation_labels = _labels(env, "fix.ml.model", "implementation")
    status_labels = _labels(env, "fix.ml.model", "status")
    risk_labels = _labels(env, "fix.ml.model", "risk_class")
    rows = []
    for model in models:
        rows.append(
            {
                "code": model.code,
                "model": model.name,
                "kind": kind_labels.get(model.kind, model.kind),
                "implementation": implementation_labels.get(
                    model.implementation, model.implementation
                ),
                "status": status_labels.get(model.status, model.status),
                "risk_class": risk_labels.get(model.risk_class, model.risk_class or "—"),
                "consumer": model.consumer_modules or "not declared",
                "fallback": "declared"
                if (model.fallback_definition or "").strip()
                else "not declared",
                "versions": len(model.version_ids),
                "owner": model.owner_id.name if model.owner_id else "—",
            }
        )
    return _pack(
        "Model Portfolio — " + portfolio_summary(env),
        [
            "code",
            "model",
            "kind",
            "implementation",
            "status",
            "risk_class",
            "consumer",
            "fallback",
            "versions",
            "owner",
        ],
        {
            "code": "Code",
            "model": "Model",
            "kind": "Kind",
            "implementation": "Implementation",
            "status": "Status",
            "risk_class": "Risk Class",
            "consumer": "Named Consumer(s)",
            "fallback": "Fallback",
            "versions": "Versions",
            "owner": "Model Owner",
        },
        rows,
        [
            portfolio_summary(env),
            "Of the %d rows, five dispatch_scoring/fault_classifier/predictive_maintenance/"
            "tradein_valuation/demand_forecast are among the specification's 14; lead scoring "
            "and the BI aggregator are engines the registry governs besides it." % len(rows),
            "A model without a named consumer, a stated target and a defined fallback is "
            "not deployed (BRU-AIM-11) — the fallback column shows who has declared one.",
        ],
        empty="No model is registered yet.",
    )


REPORTS = {
    "model_portfolio": model_portfolio,
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
    # A2-F07: the denominator is the HUMAN decision, not the engine's
    # suggestion — a suggestion nobody acted on must not inflate the base.
    decided = runs.search([("final_value", "!=", False)]).filtered(
        lambda r: (r.final_value or "").strip()
    )
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
