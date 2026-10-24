# D-039: M26 Machine Learning Platform Deployment & Measured GPU Hardware Sizing (P09-M06 / R07-M04)

**Status:** APPROVED  
**Date:** 2026-10-18  
**Deciders:** Architecture Review Board (ARB), Chief Architect (`CA`), Lead Data Scientist, Head of Infrastructure  
**Governing Documents:** AR-011, TSS §20.2 W6, CD-M26-01, R07-M04-T02, R07-M04-T03  
**Cross-References:**  
- Latency Benchmark Evidence: [`../../services/conversational-ai/evidence/gpu-vs-cpu-latency-report.json`](../../services/conversational-ai/evidence/gpu-vs-cpu-latency-report.json)  
- Asset & ML Compose Definition: [`../../infra/compose/docker-compose.asset-ml.yml`](../../infra/compose/docker-compose.asset-ml.yml)  
- Inference Gateway Source: [`../../services/ml-gateway/src/ml_gateway.py`](../../services/ml-gateway/src/ml_gateway.py)  

---

## 1. Context & Business Drivers

The Wave 6 architecture introduces enterprise machine learning automation across two mission-critical domains:
1. **Operational Predictive Intelligence:**
   - **M26 Dispatch Scoring (`P09-M06-T05`):** Replacing static heuristic weights with learned coefficients trained on historical service outcomes (technician first-time-fix rate, SLA adherence, travel distance, current queue depth, brand certifications).
   - **M26 Demand Forecasting (`P09-M06-T06`):** Multi-horizon time-series forecasting of spare parts consumption and workshop capacity across regional hubs.
2. **Conversational Customer Engagement (`M32`):**
   - Natural language intent understanding across Hotline 16743 IVR, WhatsApp Business, Web Chat, and mobile apps in Bengali and English.

Milestone `R07-M04-T02` requires formalizing the deployment topology for **MLflow** and **Ollama**, and ratifying the empirical **Measured GPU Decision** prior to capital expenditure.

---

## 2. ML Platform Architecture & Container Services

In adherence to the **Single Inference Gateway Pattern (AR-011)**, individual microservices do not expose fragmented, unmonitored model endpoints. All inference traffic routes through `services/ml-gateway`.

```
                    ┌────────────────────────┐
                    │ ERP Services & Portals │
                    └───────────┬────────────┘
                                │ HTTP / JSON-RPC
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ M26 ML Inference Gateway (services/ml-gateway)                 │
│                                                                │
│  ┌──────────────────────────┐    ┌──────────────────────────┐  │
│  │ Dispatch Scoring Engine  │    │ Demand Forecast Engine   │  │
│  │ (Learned Weights)        │    │ (Exponential Smoothing)  │  │
│  └─────────────┬────────────┘    └─────────────┬────────────┘  │
│                │                               │               │
│                ▼                               ▼               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Model Governance: Drift Detection (15%) + Retraining Log │  │
│  └─────────────────────────────┬────────────────────────────┘  │
└────────────────────────────────┼───────────────────────────────┘
                                 │
           ┌─────────────────────┴─────────────────────┐
           ▼                                           ▼
┌───────────────────────────┐             ┌───────────────────────────┐
│ MLflow Model Registry     │             │ Ollama Sovereign LLM      │
│ (Port 5000)               │             │ (Port 11434)              │
│ - Version & Lineage Track │             │ - qwen2.5:3b (Q4_K_M)     │
│ - Stage Transitions       │             │ - On-Prem Sovereign NLU   │
│ - Automated Rollback      │             │ - Zero Cloud Data Leakage │
└───────────────────────────┘             └───────────────────────────┘
```

### 2.1. MLflow Model Registry
- **Pinned Digest:** `ghcr.io/mlflow/mlflow@sha256:65aa7a75fe37554bd7dd9e539b58e1ec130dac99f27fef9756df316a272dfee2`
- **Host / Port:** `0.0.0.0:5000`
- **Capabilities:**
  - Semantic versioning of all operational models (`v1.0.0`, `v1.1.0`).
  - Feature schema tracking (`DispatchFeatures`).
  - Lineage tracking connecting training datasets, hyperparameter configurations, and evaluation metrics (FTF accuracy, MAE, RMSE).
  - Model lifecycle stages: `Staging` -> `Production` -> `Archived`.
  - Instant zero-downtime rollback capability.

### 2.2. Ollama Sovereign LLM Runtime
- **Pinned Digest:** `ollama/ollama@sha256:926d40fd6eeeebd346b5c358a63de2a10ec995371cd93dd22f1843200694b1a6`
- **Host / Port:** `127.0.0.1:11434`
- **Storage Volume:** `ollama-models:/root/.ollama`
- **Baseline Model:** `qwen2.5:3b-instruct` (Q4_K_M 4-bit quantization, 1.9 GB footprint).

---

## 3. The Measured GPU Decision: Empirical Sizing Evidence

Prior to committing infrastructure budget to high-cost GPU server instances, empirical load testing was conducted across CPU and GPU hardware tiers (`services/conversational-ai/evidence/gpu-vs-cpu-latency-report.json`).

### Empirical Benchmark Results:

| Hardware Tier | Specifications | Cost / Hour | TTFT (ms) | Gen Rate (TPS) | Turn Latency (ms) | P95 Latency (ms) | SLA Compliance |
|---|---|---|---|---|---|---|---|
| **Tier 1: Standard CPU** | 8 vCPUs (Intel Xeon / AMD EPYC), 32GB RAM | **$0.38** | 285.0 | 18.5 | **1,360.0** | 1,540.0 | **Text Chat SLA (< 2.0s): PASS**<br>Voice IVR SLA (< 400ms): FAIL |
| **Tier 2: Optimized GPU** | 1x NVIDIA T4 (16GB VRAM), 4 vCPUs, 16GB RAM | **$0.95** | 42.0 | 76.0 | **305.0** | 340.0 | **Text Chat SLA: PASS**<br>**Voice IVR SLA (< 400ms): PASS** |
| **Tier 3: High-End GPU** | 1x NVIDIA A10G (24GB VRAM), 8 vCPUs, 32GB RAM | **$1.45** | 28.0 | 115.0 | **195.0** | 225.0 | Over-provisioned for current stage |

### Architectural Decision:
1. **Immediate Phase (Text & Omnichannel): Deploy CPU-Only Instances.**
   - All WhatsApp Business, Web Chat, Customer Portal, and mobile app interactions operate under an asynchronous human conversational tempo where turn latency under 1.5 seconds is perceived as near-instantaneous.
   - 8 vCPUs deliver 1.36s average latency (< 2.0s SLA) at **$0.38/hr**, saving 60% operating expenditure compared to GPU nodes ($2,700 annual savings per instance).
2. **Voice Scaling Trigger (Hotline 16743 IVR): Provision NVIDIA T4 GPU.**
   - When interactive voice turn-taking goes live and concurrent telephony calls exceed 15 channels, deploy NVIDIA T4 GPU instances to maintain conversational IVR pacing (< 400ms).

---

## 4. Model Governance, Drift Detection & Rollback Protocol

1. **Drift Detection Threshold (`detect_drift`):**
   - Inference gateway monitors incoming actual outcomes against model predictions.
   - If relative prediction deviation exceeds **15%** (`|actual - predicted| / actual > 0.15`), drift is flagged.
2. **Automated Retraining Trigger:**
   - Gateway records drift events, logs the trigger reason, executes scheduled batch weight optimization against recent operational history, and increments model version in `MODEL_REGISTRY`.
3. **Rollback Protocol:**
   - In the event of an anomalous model version release, `rollback_model(model_name, target_version)` re-activates the previous stable version in the registry within sub-second latency.

---

## 5. Decision & Ratification

- **Option Selected:** Two-Phase Measured Deployment (CPU baseline for text; GPU scaling trigger for voice IVR) + Single ML Gateway with MLflow and Ollama.
- **Vote:** Unanimous approval by Architecture Review Board.
- **Status:** **APPROVED & IN USE**.
