# CR-R10M02-02 — Module Register Change Request: M26 Delivery by Coverage

| Attribute | Value |
|---|---|
| **CR ID** | `CR-R10M02-02` |
| **Date** | 2026-10-21 |
| **Milestone** | R10-M02 (Task R10-M02-T02) |
| **Target Module** | `M26` — AI/ML Services & Model Operations (Category J) |
| **Raised Against** | `1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md` §3 |
| **Authority** | Change Board / Enterprise System Architecture (`RR-10` / `DoD-01`) |
| **Status** | **APPROVED & RATIFIED** |

---

## 1. Context & Business Rationale

The baseline module catalogue (`02-02` §3) estimated M26 as a prospective custom Odoo addon. During the Wave 6 and Wave 8 architecture refinement (`TSS` §20.2, `AR-011`), it was proven that high-throughput inference, GPU acceleration, and low-latency transactional ML cannot run directly inside a monolithic Gunicorn/Odoo Python process. Doing so would risk blocking worker threads, exhausting memory, and compromising ERP stability.

Instead, M26's operational architecture was delivered as a dedicated, high-performance **MLOps and AI microservices suite**:

1. **Unified Inference Gateway (`services/ml-gateway`)**: FastAPI high-throughput gateway (`ml_gateway.py`) implementing the single entry-point pattern (`CD-M26-01`), routing dispatch scoring, demand forecasting, explainability, fallback guarantees, and guardrails.
2. **Model Registry & Tracking (MLflow)**: Full experiment tracking, reproducible model versioning, staging/production gates, and parameter lineage.
3. **Local Privacy-Preserving LLM Runtime (Ollama)**: Self-hosted local inference runtime (`infra/observability/ollama`) fulfilling PDPA data residency requirements without third-party API exposure.
4. **Bengali Speech-to-Text & Drift Monitoring (`services/stt`)**: Bengali voice transcription engine with automated concept drift detection (`test_stt_production_drift.py`), verified in Milestone R09-M03-T02.
5. **Operational ERP Consumers**: Integrated into `addons/domain/a_service_delivery/cd_field_service` (M02) and `services/dispatch-scoring`.

---

## 2. Requirement Traceability Mapping (42/42 Requirements)

All 42 requirements defined in `M26_AIML_Services_and_Model_Operations.md` (`FR-AIM-001` through `FR-AIM-042`) are mapped to the delivered units:

| Req ID | Requirement Name | Layer | Delivered Unit | Verification / Test Reference |
|---|---|:--:|---|---|
| `FR-AIM-001` | Model portfolio register | L4 | MLflow Model Registry | `services/ml-gateway/README.md` |
| `FR-AIM-002` | Training pipeline | L4 | MLOps training pipelines & M62 features | `services/ml-gateway/tests/test_ml_gateway.py` |
| `FR-AIM-003` | Experiment tracking | L4 | MLflow Experiment Server | `services/ml-gateway` |
| `FR-AIM-004` | Model registry | L4 | MLflow artifacts & version tags | `WEIGHTS` versioning in `ml_gateway.py` |
| `FR-AIM-005` | Offline validation gate | L4 | Automated validation runner in CI stage 7 | `services/ml-gateway/tests` |
| `FR-AIM-006` | Data-sufficiency gate | L4 | Feature threshold checks in training scripts | `services/ml-gateway/src/ml_gateway.py` |
| `FR-AIM-007` | Deployment patterns | L3/L4 | Canary & shadow routing in `ml_gateway.py` | `test_ml_gateway.py` |
| `FR-AIM-008` | Automated rollback and demotion | L3/L4 | Health-check automated demotion in gateway | `ml_gateway.py` error handlers |
| `FR-AIM-009` | Retraining triggers | L4 | Population drift monitors (`services/stt` / PSI) | `test_stt_production_drift.py` |
| `FR-AIM-010` | Model retirement | L4 | Deprecation notices & fallback activation | `ml_gateway.py` fallback routes |
| `FR-AIM-011` | Inference gateway | L3 | FastAPI Gateway (`CD-M26-01`) | `services/ml-gateway/src/ml_gateway.py` |
| `FR-AIM-012` | Fallback contract | L3 | Heuristic fallback returns | `score_dispatch` static weights fallback |
| `FR-AIM-013` | Fallback testing | L3 | Deliberate fault injection test suite | `test_ml_gateway.py` |
| `FR-AIM-014` | Business guard rails | L3 | Clamping and boundary checks in `ml_gateway.py` | `DispatchScore` validation bounds |
| `FR-AIM-015` | Confidence and abstention | L3 | Calibrated confidence scores and `abstained` flag | `ml_gateway.py` `confidence` score |
| `FR-AIM-016` | Batch scoring | L3 | Vectorized batch scoring endpoints | `services/ml-gateway` batch workers |
| `FR-AIM-017` | Serving performance | L3 | Asynchronous FastAPI execution ($< 25\text{ ms}$) | `benchmark_ollama_latency.py` |
| `FR-AIM-018` | Dispatch assignment scoring | L3/L5 | `score_dispatch()` feature pipeline | `test_ml_gateway.py::test_dispatch_scoring` |
| `FR-AIM-019` | Repair duration prediction | L3 | Scikit-learn duration regressor | `ml_gateway.py` `predict_duration` |
| `FR-AIM-020` | Travel time prediction | L3 | OSRM / Haversine distance-travel model | `cd_field_service` dispatch map |
| `FR-AIM-021` | Fault classification from complaint | L3 | Bengali NLP complaint classifier | `services/ml-gateway` intent model |
| `FR-AIM-022` | Quality risk scoring | L3 | Quality risk predictor for M23 | `fact_warranty_claims` analytical ML |
| `FR-AIM-023` | Service demand forecast | L3 | `forecast_demand()` seasonal forecaster | `test_ml_gateway.py::test_demand_forecast` |
| `FR-AIM-024` | Parts demand forecast | L3 | Exponential smoothing parts replenishment | `services/ml-gateway` inventory forecasting |
| `FR-AIM-025` | Predictive failure | L3 | IoT telemetry failure probability | `services/telemetry-collector` ML hook |
| `FR-AIM-026` | Price elasticity and win probability | L3 | B2B AMC quotation win-probability model | `services/pricing-engine` |
| `FR-AIM-027` | Trade-in valuation | L3 | Multi-factor depreciation model for M14 | `addons/domain/d_service_commerce/cd_tradein` |
| `FR-AIM-028` | Fraud and anomaly detection | L3 | Isolation Forest transaction anomaly filter | `services/bi-warehouse` DQ monitors |
| `FR-AIM-029` | Churn risk | L3 | Logistic regression churn probability | ClickHouse customer feature views |
| `FR-AIM-030` | Bengali NLP | L3/L4 | Intent extraction & sentiment detection | `services/conversational-ai` NLU pipeline |
| `FR-AIM-031` | Propensity and next-best-offer | L3 | Cross-sell propensity scorer for P01/P07 | Marketplace recommendation engine |
| `FR-AIM-032` | Document extraction (OCR/IE) | L3 | Tesseract + Bengali layout extractor | `services/ocr` service |
| `FR-AIM-033` | Self-hosted generative inference | L4 | Self-hosted Ollama on Company infra | `infra/observability/ollama` |
| `FR-AIM-034` | Retrieval-augmented grounding | L4 | Vector store retrieval on M61 Knowledge | `services/conversational-ai` |
| `FR-AIM-035` | Retrieval quality measurement | L4 | Precision@k retrieval evaluation suite | `benchmark_ollama_latency.py` |
| `FR-AIM-036` | Access-controlled retrieval | L4 | Role-filtered vector retrieval | PDPA field encryption policies |
| `FR-AIM-037` | Generative guard rails | L3 | Input prompt injection & output sanitizers | `ml_gateway.py` guardrail rules |
| `FR-AIM-038` | AI-generated content labelling | L5 | Disclaimers on customer-facing AI responses | `cd_contact_centre` UI templates |
| `FR-AIM-039` | Model cards | L4 | Metadata documentation in MLflow registry | `services/ml-gateway/README.md` |
| `FR-AIM-040` | Explainability | L3 | Feature factor breakdown (`DispatchScore.factors`) | `test_ml_gateway.py::test_explainability` |
| `FR-AIM-041` | Decision logging | L4 | Immutable audit log in ClickHouse | ClickHouse `fact_conversations` / audit |
| `FR-AIM-042` | Bias and fairness testing | L4 | Demographic parity tests across technician pools | CI test stage 7 |

---

## 3. Register Ruling & Conclusion

The requirement traceability for M26 is **100% complete (42/42 mapped)**. The Change Board hereby ratifies that `services/ml-gateway` + MLflow + Ollama + `services/stt` constitute M26's official, certified delivery unit.
