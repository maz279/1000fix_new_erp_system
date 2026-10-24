# ml-gateway — the ML inference gateway (P09-M06, CD-M26-01)

One gateway for all ML models, not per-model endpoints. Routes inference
requests to the appropriate model backend.

**Status (honest):** NO trained model is deployed and NO MLflow server is
running. What serves today is the explainable heuristic below, and every
response is labelled `model_backend: "heuristic-v1"` so it can never be
mistaken for a trained model. Registry cards carry EMPTY `metrics` and `None`
lineage until a real backend reports measured numbers.

## Models

### Dispatch scoring (P09-M06-T05)
Replaces the heuristic scoring in `services/dispatch-scoring`. Learns from
three years of dispatch outcomes. The W6 baseline uses explainable weighted
factors (certification 3.0, first-time-fix 2.5, SLA hit 1.5, workload
penalty −0.3/job); MLflow-tracked retraining replaces these with learned
coefficients as data accumulates.

```python
from ml_gateway import DispatchFeatures, score_dispatch
score = score_dispatch(DispatchFeatures(
    technician_id="T001", historical_ftf=0.85, historical_sla=0.92,
    certification_active=True, workload_today=3))
# score.score, score.factors (explainable)
```

### Demand forecast (P09-M06-T06)
Feeds M43 demand planning. Exponential smoothing baseline with confidence
degradation over forecast horizon; upgrades to ARIMA/Prophet via MLflow.

```python
from ml_gateway import forecast_demand
forecasts = forecast_demand([("2026-01", 100), ("2026-02", 110)], periods_ahead=3)
```

## Model governance (P09-M06-T09)
- `MODEL_REGISTRY`: version, stage, training metadata per model - `metrics`
  stay empty until measured; nothing is invented
- `trigger_retraining()` records a registry event (`status: "recorded"`) - no
  training pipeline exists, so no post-retraining accuracy is fabricated
- `detect_drift()`: triggers retraining when |actual - predicted| / actual > 15%
- Every score is explainable (the factors dict shows each contribution)

## Infrastructure
- MLflow (model registry): `docker compose --profile asset-ml up`
- Ollama (LLM inference): same profile; GPU only if measured latency requires
- Tests: `python -m pytest services/ml-gateway/tests`

## HTTP API (src/main.py, stdlib http.server)

```
GET  /health          liveness + model_backend label + trained_model_deployed=false
POST /v1/dispatch     {"candidates": [DispatchFeatures...]} -> ranked scores
POST /v1/forecast     {"history": [["2026-01", 100], ...], "periods_ahead": 3}
GET  /v1/models/<name> registry card
```

Run locally: `FIX_ENV=local python services/ml-gateway/src/main.py`
(port 8090, override with `ML_GATEWAY_PORT`).
