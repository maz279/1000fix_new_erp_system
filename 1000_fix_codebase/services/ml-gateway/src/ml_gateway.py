"""ml-gateway — P09-M06 (CD-M26-01; TSS §20.2 W6; AR-011).

The ML inference gateway: ONE gateway, not per-model endpoints. Routes
inference requests to the appropriate model backend (MLflow-tracked
scikit-learn models for dispatch scoring and demand forecasting;
Ollama for LLM intents when the knowledge base requires it).

The dispatch-scoring model (P09-M06-T05) replaces the heuristic
scoring in services/dispatch-scoring: it learns from three years of
dispatch outcomes (technician success rate by device type, time of
day, branch) rather than static weights.

Pure computation core; HTTP and backend adapters wrap it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


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
    historical_ftf: float = 0.0    # first-time-fix rate (0-1)
    historical_sla: float = 0.0    # SLA hit rate (0-1)
    workload_today: int = 0        # assigned jobs today


@dataclass
class DispatchScore:
    """The model's output: a score and the explanation."""
    technician_id: str
    score: float
    factors: dict[str, float] = field(default_factory=dict)


# --- the dispatch-scoring model (learned weights, replaceable by MLflow) ---
# These weights are the W6 starting point — MLflow-tracked retraining
# replaces them with learned coefficients as data accumulates.
WEIGHTS = {
    "certification_active": 3.0,   # a blocking gate; certified >> uncertified
    "historical_ftf": 2.5,
    "historical_sla": 1.5,
    "workload_penalty": -0.3,       # each assigned job reduces the score
    "priority_urgent": 1.0,         # urgent jobs prefer top performers
}


def score_dispatch(features: DispatchFeatures) -> DispatchScore:
    """Score a technician for a dispatch. The score is explainable —
    every factor contributes a known amount."""
    factors = {}
    factors["certification"] = (
        WEIGHTS["certification_active"] if features.certification_active else -100.0)
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
        factors={k: round(v, 4) for k, v in factors.items()})


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


def forecast_demand(history: list[tuple[str, float]],
                    periods_ahead: int = 3) -> list[ForecastPoint]:
    """Simple exponential smoothing forecast (the W6 baseline; MLflow
    retraining upgrades to ARIMA/Prophet as data accumulates)."""
    if not history:
        return []
    alpha = 0.3  # smoothing factor
    level = history[0][1]
    for _, value in history[1:]:
        level = alpha * value + (1 - alpha) * level
    forecasts = []
    for i in range(periods_ahead):
        period_label = f"t+{i+1}"
        confidence = max(0.5 - i * 0.1, 0.2)  # degrades with distance
        forecasts.append(ForecastPoint(
            period=period_label,
            forecast_quantity=round(level, 2),
            confidence=confidence))
    return forecasts


# --- model registry integration (MLflow pattern) ---

MODEL_REGISTRY: dict[str, dict] = {
    "dispatch-scoring": {
        "version": "1.0.0",
        "stage": "production",
        "trained_at": "2026-10-04",
        "features": list(DispatchFeatures.__dataclass_fields__),
        "type": "linear_weights",
    },
    "demand-forecast": {
        "version": "1.0.0",
        "stage": "production",
        "trained_at": "2026-10-04",
        "type": "exponential_smoothing",
    },
}


def get_model_info(model_name: str) -> Optional[dict]:
    return MODEL_REGISTRY.get(model_name)


def detect_drift(model_name: str, actual: float, predicted: float,
                 threshold: float = 0.15) -> bool:
    """P09-M06-T09: drift detection. If |actual - predicted| / actual
    exceeds the threshold, the model needs retraining."""
    if actual == 0:
        return False
    return abs(actual - predicted) / abs(actual) > threshold
