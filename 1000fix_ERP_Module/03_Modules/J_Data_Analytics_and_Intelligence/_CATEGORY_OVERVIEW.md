---
id: FIX-ERP2-CAT-J
category: J
category_name: Data, Analytics & Intelligence
module_count: 4
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category J — Data, Analytics & Intelligence

**4 modules · Category owner: Chief Technology Officer**

---

## 1. What Belongs in This Category

Turning operational data into insight, prediction and automation.

If a capability answers *"what happened, why, what will happen next, and can the system act
on it without a human"*, it belongs here.

This category consumes from every other module and writes back recommendations. It is the
layer that turns 66 modules of record-keeping into a business that gets better at itself.

---

## 2. Modules

| ID | Module | Status | Priority | Wave | One-Line Definition |
|---|---|---|:--:|:--:|---|
| **M62** | Data Platform, Warehouse & Governance ★ | New | P1 | W4 / W8 | Pipelines, warehouse, dimensional model, semantic layer, data quality, lineage and the feature store |
| **M25** | Business Intelligence & Reporting | Re-scoped | P1 | W4 | Dashboards, reports, self-service exploration, distribution, alerting and embedded analytics |
| **M26** | AI/ML Services & Model Operations | Re-scoped | P2 | W6–W8 | The model portfolio, training, serving, monitoring, governance and generative AI services |
| **M63** | Process Automation & Workflow Orchestration ★ | New | P1 | W3 | Cross-module workflow, approvals, business-rule execution, scheduled and event-driven automation |

★ = new in v2.1 after enterprise benchmarking.

---

## 3. Why the Data Platform Is Separate from BI

The v2.0 draft merged them. Every serious data organisation separates them, because they are
different disciplines with different failure modes.

| | M62 Data Platform | M25 Business Intelligence |
|---|---|---|
| **Owns** | Ingestion, transformation, the warehouse, the dimensional model, the semantic layer, data quality tests, lineage, the feature store | Dashboards, reports, self-service exploration, subscriptions, alerting, embedded analytics |
| **Skill** | Data engineering | Analytics and visualisation |
| **Fails how** | Numbers are wrong or late | Numbers are right but nobody can find or read them |
| **Analogue** | Oracle *Fusion Analytics Data Pipelines* · SAP *Datasphere* · dbt + warehouse | Oracle *OTBI* · SAP *Analytics Cloud* · Metabase |
| **Consumers** | M25, M26, external analysts | Every role, every portal |

**Rule:** a metric is defined once, in M62's semantic layer. M25 displays it. If two
dashboards disagree, the defect is in M62, not in a chart.

---

## 4. Why Automation Is Its Own Module

Workflow orchestration was buried inside the integration platform in the v2.0 draft. It is a
distinct capability with a distinct audience.

| | M28 Integration Platform (Category K) | M63 Process Automation |
|---|---|---|
| **Concern** | Moving data reliably between systems | Advancing a business process through steps and approvals |
| **Audience** | Developers and integration engineers | Business analysts and process owners |
| **Artifacts** | Connectors, event schemas, API contracts, retry policy | Approval chains, escalation rules, scheduled jobs, business-rule sets |
| **Change cadence** | On system change | On policy change — far more frequent |
| **Analogue** | MuleSoft / Kong / Kafka | SAP *Business Workflow* · Oracle *BPM* · n8n / Camunda |

**Rule:** M28 guarantees the message arrives. M63 decides what happens next and who must
approve it. A change to an approval threshold must never require an integration release.

---

## 5. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| Data ingestion, warehouse, dimensional model | **M62** | M25 |
| Metric definition (the single source of a number) | **M62** semantic layer | M25 (renders it) |
| Data quality tests and lineage | **M62** | M64 (owns master data quality rules) |
| Row-level security in analytics | **M62** enforces from **M29** roles | M25 |
| Dashboards, reports, exploration, distribution | **M25** | M62 |
| Operational real-time boards (dispatch map, queue) | Owning module (M02, M04) | M25 |
| Feature store for models | **M62** | M26 |
| Model training, registry, serving, monitoring | **M26** | M62 |
| Model-influenced decisions and their audit | **M26** logs; consuming module acts | — |
| Generative AI inference and grounding | **M26** | M32 (consumes for conversation) |
| Approval chains and escalation rules | **M63** | Every module declares its need; M63 executes |
| Scheduled and event-driven job execution | **M63** | M28 (transports the event) |
| Business-rule configuration (thresholds, tolerances) | **M63** | M64 (stores the parameter) |
| Notification delivery | **M27** (Category B) | M63 (triggers it) |

---

## 6. The Model Portfolio (M26)

Every model has a named consumer, an accuracy target and a defined fallback. A model without
all three is not deployed.

| Model | Consumed By | Target | Fallback When Unavailable |
|---|---|---|---|
| Dispatch assignment scoring | M02 | 70% auto-assign, ≥ 90% dispatcher agreement | Rule-based scoring |
| Repair duration prediction | M02, M31 | MAE < 20% | Standard time from M37 catalogue |
| Travel time prediction | M02, M03 | MAE < 15% | OSRM static estimate |
| Parts demand forecast | M43 | MAPE < 22% | Moving average |
| Service demand forecast | M55, M02 | MAPE < 18% | Prior-period actuals |
| Predictive failure | M48, M08 | Precision > 70% | Calendar-based maintenance |
| Fault classification from complaint text | M01, M32 | Top-3 accuracy > 80% | Manual selection |
| Price elasticity / win probability | M11 | AUC > 0.75 | Static price book |
| Churn risk | M07, M34 | AUC > 0.72 | Recency-frequency-value rules |
| Quality risk scoring | M23 | Precision > 60% at top decile | Sampling plan |
| Fraud and anomaly detection | M12, M19, M53 | Recall > 80% at 5% FPR | Manual review thresholds |
| Trade-in valuation | M14 | Within 10% of assessed value, 75% of the time | Depreciation table |
| Bengali NLP — intent, entity, sentiment | M32, M34 | Intent accuracy > 88% | Menu-driven flow |
| Document extraction (OCR / IE) | M52, M24, M09 | Field accuracy > 92% | Manual keying |

---

## 7. AI Governance — Non-Negotiable

| # | Rule | Enforced By |
|---|---|---|
| 1 | Any decision with material customer or financial impact requires human confirmation | M26, BRU-AIM-01 |
| 2 | No model output may cross a business guard rail (price floor/ceiling, certification requirement, safety rule) | M26, BRU-AIM-02 |
| 3 | Every material prediction carries an explanation a user can understand | M26 |
| 4 | Every human override is captured with a reason and fed back into training | M26 |
| 5 | Every consuming module has a tested fallback for model unavailability | M26 + consumer |
| 6 | Recovered customer data (M06) is never used as training data | M26, BRU-AIM-03 |
| 7 | Models affecting people — dispatch, incentives, seller ranking — are tested for bias and the results documented | M26 |
| 8 | Every production model has a current model card: purpose, data, limits, metrics, owner, review date | M26 |
| 9 | Every model-influenced decision is logged with inputs, output, model version and override status | M26 |
| 10 | LLM inference is self-hosted; customer data does not leave Company infrastructure | M26 |

---

## 8. Why AI Comes Late (Waves 6–8)

This is a deliberate sequencing decision, not a deprioritisation.

| Model | Data It Needs | Available From |
|---|---|---|
| Dispatch scoring | Assignment outcomes, travel actuals, fix rates | 12 months of M02 data → W6 |
| Demand forecast | Consumption history by part and location, seasonality | 18–24 months of M15 data → W6–W8 |
| Predictive failure | Telemetry plus failure events | M48 live from W8 |
| Price elasticity | Quotation win/loss at varied price points | M36 data from W3, usable by W7 |
| Churn | Full customer lifecycle including satisfaction | M34 data from W4 → W8 |

Building models before the data exists produces confident nonsense and destroys trust in the
whole capability. The exception is the Bengali language assistant (M32/M26 generative), which
uses pre-trained models and can land in Wave 4.

---

## 9. Category KPIs

| KPI | Baseline | Target | Owning Module |
|---|---|---|---|
| Data freshness — operational dashboards | n/a | < 15 minutes | M62 |
| Data freshness — warehouse | n/a | < 60 minutes | M62 |
| Data quality test pass rate | n/a | > 99% | M62 |
| Metrics with a single certified definition | 0% | 100% | M62 |
| Executive dashboard load time | n/a | < 5 seconds | M25 |
| Standard report generation | manual, days | < 20 seconds | M25 |
| Manager weekly dashboard usage | 0% | > 90% | M25 |
| Manual spreadsheet management reports remaining | 100% | **Zero by W8** | M25 |
| Automatic dispatch assignment rate | 0% | > 70% | M26 |
| Dispatcher agreement with recommendation | n/a | > 90% | M26 |
| Models with a current model card | n/a | **100%** | M26 |
| Model-influenced decisions logged | n/a | **100%** | M26 |
| Incidents caused by unavailable models | n/a | **Zero** | M26 |
| Approval cycle time (all approvals) | manual, days | < 4 working hours | M63 |
| Workflow changes made without a code release | 0% | > 95% | M63 |
| Overall automation of routine operational work | ~20% | **85%** | M63 |

---

## 10. Category Delivery Sequence

```
W3   M63 Process Automation ─────► approvals and workflow from the first money module
W4   M62 Data Platform (core) ──┐
     M25 Business Intelligence ─┴──► management sees live numbers
W6   M26 AI/ML (dispatch, forecasting) ──► first models on accumulated data
W8   M62 Warehouse (full) ──────┐
     M26 AI/ML (predictive, pricing, generative) ┴──► full intelligence layer
```

---

## 11. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| Two dashboards show different numbers for the same metric | High — trust in all reporting collapses | Single semantic layer; metric definitions versioned and change-controlled | M62 |
| Management reverts to spreadsheets | High — the visibility benefit never lands | Retire the source data for manual packs; make dashboards materially better; require decisions to cite the dashboard | M25 |
| Models built before sufficient data exists | High — confident nonsense destroys trust | Deliberate deferral to W6–W8 with stated data prerequisites | M26 |
| A model makes an unexplainable decision affecting a person's pay or a seller's income | High — fairness and legal exposure | Explainability mandatory; bias testing documented; human override always available | M26 |
| Automation encodes a wrong rule at scale | High — errors multiply faster than humans catch them | Rules are configuration with approval; every automation has a defined failure behaviour and an audit trail | M63 |
| Warehouse cost grows uncontrolled | Medium | Retention and downsampling policy from day one; cost monitored monthly | M62 |
| Personal data used in analytics without basis | High — legal | Row-level security mirrors ERP isolation; S3 fields excluded from the warehouse by default | M62 / M29 |

---

*Category J · 1000FiX ERP System v2.0*
