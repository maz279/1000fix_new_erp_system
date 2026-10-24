"""ml-gateway — P09-M06 (CD-M26-01; TSS §20.2 W6; AR-011).

The ML inference gateway: ONE gateway, not per-model endpoints. Routes
inference requests to the appropriate model backend (MLflow-tracked
scikit-learn models for dispatch scoring and demand forecasting; Ollama for
LLM intents when the knowledge base requires it).

HONESTY CONTRACT (GV-009): today there is NO trained model and NO MLflow
server. What exists is an explainable heuristic scorer (labelled
``model_backend: heuristic-v1``) whose weights are written down below - not
learned. The registry therefore carries NO accuracy metrics, NO mlflow run
ids and NO s3 training datasets: those would be invented. When a real backend
is trained and registered, its measured metrics replace the empty ``metrics``
dicts here.

The dispatch-scoring model (P09-M06-T05) will replace the heuristic scoring
in services/dispatch-scoring by learning from three years of dispatch
outcomes (technician success rate by device type, time of day, branch).

Pure computation core; HTTP (src/main.py) and backend adapters wrap it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Every inference response carries this label so no consumer can mistake the
# heuristic for a trained model.
MODEL_BACKEND_LABEL = "heuristic-v1"


@dataclass
class DispatchFeatures:
    """The dispatch model's feature vector — learned from history."""

    technician_id: str
    device_type: str = ""
    brand: str = ""
    branch: str = ""
    hour_of_day: int = 12
    priority: str = "normal"
    certification_active: bool = True
    historical_ftf: float = 0.0  # first-time-fix rate (0-1)
    historical_sla: float = 0.0  # SLA hit rate (0-1)
    workload_today: int = 0  # assigned jobs today


@dataclass
class DispatchScore:
    """The model's output: a score and the explanation."""

    technician_id: str
    score: float
    factors: dict[str, float] = field(default_factory=dict)
    model_backend: str = MODEL_BACKEND_LABEL


# --- the dispatch-scoring heuristic (hand-set weights, NOT learned) ---
# These weights are the W6 starting point — MLflow-tracked retraining
# replaces them with learned coefficients as data accumulates. They are
# deliberately visible here: nothing about them is "trained" or "measured".
WEIGHTS = {
    "certification_active": 3.0,  # a blocking gate; certified >> uncertified
    "historical_ftf": 2.5,
    "historical_sla": 1.5,
    "workload_penalty": -0.3,  # each assigned job reduces the score
    "priority_urgent": 1.0,  # urgent jobs prefer top performers
}


def score_dispatch(features: DispatchFeatures) -> DispatchScore:
    """Score a technician for a dispatch using the labelled heuristic. The
    score is explainable — every factor contributes a known amount."""
    factors = {}
    factors["certification"] = (
        WEIGHTS["certification_active"] if features.certification_active else -100.0
    )
    factors["first_time_fix"] = features.historical_ftf * WEIGHTS["historical_ftf"]
    factors["sla_hit"] = features.historical_sla * WEIGHTS["historical_sla"]
    factors["workload"] = features.workload_today * WEIGHTS["workload_penalty"]
    if features.priority == "urgent":
        factors["urgency"] = WEIGHTS["priority_urgent"]
    else:
        factors["urgency"] = 0.0
    score = sum(factors.values())
    return DispatchScore(
        technician_id=features.technician_id,
        score=round(score, 4),
        factors={k: round(v, 4) for k, v in factors.items()},
        model_backend=MODEL_BACKEND_LABEL,
    )


def rank_technicians(features_list: list[DispatchFeatures]) -> list[DispatchScore]:
    """Rank technicians for a dispatch: highest score first; uncertified
    technicians are ALWAYS at the bottom (the blocking gate)."""
    scores = [score_dispatch(f) for f in features_list]
    return sorted(scores, key=lambda s: s.score, reverse=True)


# --- the demand-forecast model (P09-M06-T06) ---


@dataclass
class ForecastPoint:
    period: str
    forecast_quantity: float
    confidence: float  # 0-1
    model_backend: str = MODEL_BACKEND_LABEL


def forecast_demand(
    history: list[tuple[str, float]], periods_ahead: int = 3
) -> list[ForecastPoint]:
    """Simple exponential smoothing forecast (the W6 baseline heuristic;
    MLflow retraining upgrades to ARIMA/Prophet as data accumulates)."""
    if not history:
        return []
    alpha = 0.3  # smoothing factor
    level = history[0][1]
    for _, value in history[1:]:
        level = alpha * value + (1 - alpha) * level
    forecasts = []
    for i in range(periods_ahead):
        period_label = f"t+{i + 1}"
        confidence = max(0.5 - i * 0.1, 0.2)  # degrades with distance
        forecasts.append(
            ForecastPoint(
                period=period_label,
                forecast_quantity=round(level, 2),
                confidence=confidence,
                model_backend=MODEL_BACKEND_LABEL,
            )
        )
    return forecasts


# --- model registry (MLflow pattern) ---
#
# Every card is HONEST: ``metrics`` is empty until a trained backend reports
# measured numbers, and ``lineage`` contains no invented mlflow run ids or s3
# datasets (the previous registry fabricated accuracy metrics, mlflow_run_id
# strings and s3:// training datasets that never existed).

MODEL_REGISTRY: dict[str, dict] = {
    "dispatch-scoring": {
        "version": "1.0.0",
        "stage": "heuristic",  # not "production": no trained model exists
        "model_backend": MODEL_BACKEND_LABEL,
        "trained_at": None,  # never trained
        "features": list(DispatchFeatures.__dataclass_fields__),
        "type": "linear_weights_hand_set",
        "metrics": {},  # UNMEASURED: no evaluation has been run
        "history": [],
        "lineage": {
            "training_dataset": None,  # no dataset exists yet
            "feature_pipeline": None,
            "mlflow_run_id": None,  # no MLflow server is deployed
        },
    },
    "demand-forecast": {
        "version": "1.0.0",
        "stage": "heuristic",
        "model_backend": MODEL_BACKEND_LABEL,
        "trained_at": None,
        "type": "exponential_smoothing",
        "metrics": {},  # UNMEASURED
        "history": [],
        "lineage": {
            "training_dataset": None,
            "feature_pipeline": None,
            "mlflow_run_id": None,
        },
    },
    "bengali-stt": {
        "version": "0.0.0",
        "stage": "not-deployed",  # no STT backend is configured (see services/stt)
        "model_backend": None,
        "trained_at": None,
        "type": "external-backend-required",
        "metrics": {},  # UNMEASURED: no production WER has ever been measured
        "history": [],
        "lineage": {
            "training_dataset": None,
            "feature_pipeline": None,
            "mlflow_run_id": None,
        },
    },
}

RETRAINING_LOG: list[dict] = []


def get_model_info(model_name: str) -> dict | None:
    return MODEL_REGISTRY.get(model_name)


def detect_drift(model_name: str, actual: float, predicted: float, threshold: float = 0.15) -> bool:
    """P09-M06-T09: drift detection. If |actual - predicted| / actual
    exceeds the threshold, the model needs retraining."""
    if actual == 0:
        return False
    return abs(actual - predicted) / abs(actual) > threshold


def trigger_retraining(
    model_name: str, trigger_reason: str, sample_history: list | None = None
) -> dict:
    """R07-M04-T03: retraining trigger upon drift or schedule.

    This is a REGISTRY BOOKKEEPING event only: no training job exists to run,
    so the event is recorded with status "recorded" and NO new metrics are
    invented (the previous implementation fabricated post-retraining accuracy
    numbers). The archived version keeps its own (possibly empty) metrics.
    """
    model = MODEL_REGISTRY.get(model_name)
    if not model:
        raise ValueError(f"Unknown model: {model_name}")

    old_version = model["version"]
    parts = old_version.split(".")
    new_version = f"{parts[0]}.{int(parts[1]) + 1}.0"

    # Archive current version into history
    archived_entry = {
        "version": old_version,
        "stage": "archived",
        "prior_stage": model["stage"],  # restored verbatim on rollback
        "trained_at": model["trained_at"],
        "metrics": dict(model.get("metrics", {})),
    }
    model.setdefault("history", []).append(archived_entry)

    # Update model to new version. Metrics stay UNMEASURED - retraining
    # without a real training pipeline cannot produce accuracy numbers.
    from datetime import date

    model["version"] = new_version
    model["stage"] = model["stage"] if model["stage"] == "not-deployed" else "retrain-requested"
    model["trained_at"] = None
    model["metrics"] = {}

    event = {
        "model_name": model_name,
        "from_version": old_version,
        "to_version": new_version,
        "reason": trigger_reason,
        "triggered_at": date.today().isoformat(),
        "status": "recorded",  # bookkeeping only - no training pipeline ran
        "note": "no training backend is deployed; metrics remain unmeasured",
    }
    RETRAINING_LOG.append(event)
    return event


def get_model_lineage(model_name: str) -> dict:
    """R07-M04-T02: Retrieve full lineage and version history for governance."""
    model = MODEL_REGISTRY.get(model_name)
    if not model:
        raise ValueError(f"Unknown model: {model_name}")
    return {
        "model_name": model_name,
        "active_version": model["version"],
        "stage": model["stage"],
        "model_backend": model.get("model_backend"),
        "lineage": model.get("lineage", {}),
        "metrics": model.get("metrics", {}),
        "history": model.get("history", []),
        "retraining_events": [r for r in RETRAINING_LOG if r.get("model_name") == model_name],
    }


def rollback_model(model_name: str, target_version: str) -> dict:
    """R07-M04-T02: Instant rollback to a previous version in the registry."""
    model = MODEL_REGISTRY.get(model_name)
    if not model:
        raise ValueError(f"Unknown model: {model_name}")

    # Search history for target version
    found = None
    for entry in model.get("history", []):
        if entry["version"] == target_version:
            found = entry
            break

    if not found:
        raise ValueError(f"Version {target_version} not found in model history.")

    current_version = model["version"]
    model["version"] = target_version
    model["stage"] = found.get("prior_stage", "archived")
    model["trained_at"] = found["trained_at"]
    model["metrics"] = dict(found["metrics"])

    return {
        "model_name": model_name,
        "rolled_back_from": current_version,
        "active_version": target_version,
        "status": "rolled_back",
    }
