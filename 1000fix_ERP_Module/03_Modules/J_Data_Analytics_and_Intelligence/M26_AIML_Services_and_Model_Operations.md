---
id: FIX-ERP2-M26
module_id: M26
module_code: AIM
module_name: AI/ML Services & Model Operations
category: J — Data, Analytics & Intelligence
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Data Squad
priority: P2
wave: W6–W8
---

# M26 — AI/ML Services & Model Operations
### Category J · Code `AIM` · Existing (re-scoped in v2.1)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M26 |
| **Module code** | `AIM` |
| **Category** | J — Data, Analytics & Intelligence |
| **Status** | Existing (retained from v1.0, **re-scoped in v2.1** — the feature store moved to M62; governance obligations added) |
| **Priority** | **P2** commercially · **P0** for the AI governance controls |
| **Delivery wave** | **W6** (dispatch, forecasting, NLP) · **W8** (predictive, pricing, generative at scale) |
| **Business owner** | Chief Technology Officer |
| **System owner** | Data Squad |
| **Delivery layers** | L3 (inference gateway and model services) · L4 (MLflow, Ollama, GPU compute) · L5 (custom) |
| **Custom modules** | `cd_ml_gateway`, `cd_dispatch_ml`, `cd_forecast`, `cd_predictive`, `cd_pricing_ml`, `cd_llm_bridge`, `cd_model_governance`, `cd_model_monitoring` |
| **Requirement range** | FR-AIM-001 … FR-AIM-042 |
| **Requirement count** | **42** *(the `05-01` allocation is 38; four IDs claimed from the reserved growth block 039–055 — see §16.5)* |
| **Effort estimate** | **34 person-weeks** *(register estimated 30)* |
| **Depends on** | **M62 Data Platform (feature store — hard dependency)** · M29 Identity & Security · M28 Integration Platform · M30 Platform Administration · M06 Data Services *(training-data prohibition)* · every consuming module for outcome labels |
| **Depended on by** | M02 Field Service · M31 Workshop · M03 Logistics · M43 Demand Planning · M48 IoT · M11 Pricing · M07 CRM · M34 Experience · M23 Quality · M12 Marketplace · M14 Trade-In · M32 Conversational AI · M52 Payable · M24 Documents · M09 Warranty · M53 Revenue · M55 Workforce |

---

## 2. Purpose

M26 owns **every model in the Company and everything that happens to it after someone has an
idea for it**: the data it trains on, the code that trains it, the registry it is versioned in,
the gateway it is served through, the monitoring that detects when it stops working, the
explanation that accompanies its output, the guard rails it cannot cross, the human who can
override it, and the model card that says what it is for.

It is deliberately **not** a collection of clever features scattered across modules. Fourteen
named models serve seventeen consuming modules through **one gateway with one fallback
contract**. That centralisation is the design: a model embedded inside the module that uses it
is a model nobody monitors, nobody governs, nobody can explain, and nobody notices has quietly
degraded.

The module also carries the Company's **generative AI capability** — self-hosted, grounded in
the Company's own knowledge, and never sending customer data outside Company infrastructure.

### Why It Exists

Three of the programme's largest benefit lines are model-dependent: technician productivity
(**BDT 130 lac/year**, via dispatch scoring and duration prediction), inventory cost reduction
(**BDT 34 lac/year**, via demand forecasting), and dynamic pricing margin uplift (**BDT 40 lac/
year**, via elasticity and win-probability modelling). Churn reduction and marketplace integrity
add more. Roughly **a quarter of the total benefit case runs through this module.**

But the reason it is governed as tightly as it is has nothing to do with benefit. A model that
assigns work affects a technician's earnings. A model that ranks sellers affects a small
business's income. A model that scores a trade-in decides what a customer is paid. These are
decisions about people, made at scale, by a system that cannot be asked to justify itself unless
it was built to. The governance regime in §9 exists so that it can be.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Category J Overview §5 | Boundary map: model training, registry, serving and monitoring → **M26**; feature store → **M62**; generative inference and grounding → **M26** (M32 consumes for conversation); model-influenced decisions → M26 logs, the consuming module acts |
| **Category J Overview §6** | **The model portfolio — fourteen named models, each with a named consumer, an accuracy target and a defined fallback. "A model without all three is not deployed."** Reproduced in full in §5.3–§5.6 |
| **Category J Overview §7** | **Ten non-negotiable AI governance rules**, including three named business rules (BRU-AIM-01, -02, -03). Reproduced verbatim as §9 |
| Category J Overview §8 | Why AI comes late: models require accumulated data. Dispatch needs 12 months of M02; demand needs 18–24 months of M15; predictive needs M48 live from W8. The exception is Bengali NLP, which uses pre-trained models and can land in W4 |
| Category J Overview §9 | KPIs owned here: automatic dispatch assignment > 70%, dispatcher agreement > 90%, **models with a current model card 100%**, **model-influenced decisions logged 100%**, **incidents caused by unavailable models zero** |
| Category J Overview §11 | Risks owned here: models built before sufficient data; an unexplainable decision affecting a person's pay or a seller's income |
| Scope Charter §Benefit Register | Technician productivity **BDT 130 lac** (M02 + M26) · inventory cost **BDT 34 lac** (M15 + M26) · dynamic pricing **BDT 40 lac** (M11 + M26) · churn (M07 + M26) |
| `06-02` | **KPI-013** automatic assignment rate 0% → 70% · **KPI-023** customer churn ~15% → < 8% |
| M06 §9 BRU-DTS-14 | *"Recovered customer data is never used as training data for any model"* — the reciprocal of BRU-AIM-03 |
| `02-05` §Technology Stack | MLflow 2.x (model registry and tracking, W6) · Ollama 0.5+ (self-hosted LLM inference, W6) · ML inference gateway (Python/FastAPI, single entry point with fallback) |
| Seventeen written module specifications | Each declares the model it consumes, the mechanism (*REST with timeout and fallback*) and the training data it supplies back |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The model portfolio and its governance — what models exist, why, and who owns each |
| 2 | Training pipelines, experiment tracking and reproducible training runs |
| 3 | The model registry: versions, lineage, evaluation metrics, promotion and demotion |
| 4 | Model evaluation, offline validation gates and acceptance against a stated target |
| 5 | Deployment patterns: shadow, canary, champion–challenger, automated rollback |
| 6 | The inference gateway — a single entry point to every model, with a fallback contract |
| 7 | Production monitoring: performance, data drift, concept drift, latency, availability |
| 8 | Retraining triggers, scheduled and drift-driven |
| 9 | Explainability for every material prediction |
| 10 | Business guard rails that a model output cannot cross |
| 11 | Human-in-the-loop confirmation, override capture and override feedback into training |
| 12 | Bias and fairness testing for models affecting people, and its documentation |
| 13 | Model cards and the AI risk register |
| 14 | Complete decision logging: inputs, output, model version, explanation, override status |
| 15 | Generative AI: self-hosted inference, retrieval-augmented grounding, prompt and output guard rails |
| 16 | Bengali and English natural-language capability — intent, entity, sentiment, summarisation |
| 17 | Document extraction (OCR / information extraction) as a model service |
| 18 | The fallback contract with every consuming module, and its testing |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **The feature store, feature definitions and point-in-time correctness** | **M62** Data Platform | Category J overview §5. M62 owns the store; M26 consumes it. Separating them is what prevents training-serving skew being invisible to the party who caused it |
| **The warehouse, dimensional model, semantic layer and data quality** | **M62** | M26 is a consumer of governed data, not a data platform |
| **Dashboards, reports and the presentation of predictions** | **M25** Business Intelligence | M25 may display a prediction with its explanation; it never produces one |
| **The business decision itself, and acting on it** | **Consuming module** | Category J overview §5: *"M26 logs; consuming module acts."* M26 never writes an assignment, a price, a payment or an order |
| **Conversational experience, dialogue management and channel handling** | **M32** Conversational AI | M32 consumes model services; M26 governs the models. M32 is not a model factory |
| **Notification and message delivery** | **M27** | — |
| **Approval chains and process orchestration around a model-influenced decision** | **M63** Process Automation | M26 returns a score and an explanation; M63 routes the confirmation |
| **Identity, authentication and role definition** | **M29** | — |
| **Message transport, connectors and API gateway** | **M28** | M26 exposes services through the platform's gateway |
| **GPU and compute infrastructure operation** | **M30** Platform Administration | M26 declares requirements; M30 runs the estate |
| **Certified data destruction and data-recovery case content** | **M06** | M26 has no access to it, by rule (BRU-AIM-03) |
| **Enterprise risk register and incident investigation** | **M60** GRC | M26 maintains the AI risk register and raises events; GRC owns the enterprise view |
| **Business-rule configuration (thresholds, tolerances)** | **M63** / **M64** | A guard rail's *value* is business configuration; M26 owns its *enforcement* |

### 3.3 Shared Concepts

| Concept | M26's Role | Owning Module |
|---|---|---|
| Feature | Consumes by name and version | **M62** |
| Training dataset | Assembles from M62 extracts | M62 |
| Model | **Owns — definition, version, registry, serving, monitoring** | M26 |
| Prediction | **Owns the output and its explanation** | Consuming module acts on it |
| Model-influenced decision log | **Owns** | Consuming module owns the decision record |
| Guard rail | **Owns enforcement** | Owning module owns the value (price floor, certification requirement, safety rule) |
| Override | **Owns capture and feedback loop** | Consuming module captures the human action |
| Fallback | **Owns the contract**; consumer implements and tests it | Both |
| Model card | **Owns** | M24 retains |
| Generative inference | **Owns** | M32 consumes for conversation |
| Knowledge grounding corpus | Consumes for retrieval | **M61** Knowledge Management |
| Bias test result | **Owns** | M60 GRC reviews |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **MLflow** *(selected in `02-05`)* | Experiment tracking, model registry as the single source of truth, versioned artefacts, stage transitions, evaluation metrics attached to versions | **The registry as the single source of truth**, with production metrics, drift outputs and explainability traces mapped to registry state, so an alert carries the context of which version regressed. **Automated demotion is implemented, not only automated promotion** — a pipeline that can promote but not demote is a one-way door into production incidents | The hosted platform tier |
| **MLOps deployment practice** | Gated offline validation → shadow deployment → canary rollout → online experiment → champion–challenger with automated rollback | **The full ladder**, with shadow as the mandatory first production stage. A model that has never seen production traffic has not been tested | Continuous automated retraining into production without a gate. At this data volume and governance posture, promotion is a decision, not a cron job |
| **Drift detection practice** | PSI and Kolmogorov–Smirnov tests across features, SHAP-based feature monitoring, a common trigger being PSI > 0.2 on a key feature coinciding with a material evaluation drop; daily checks for revenue-critical models, weekly otherwise | **Exactly this**: PSI and KS on every served feature, SHAP attribution monitoring, the combined PSI-plus-evaluation-drop retraining trigger, and a per-model check cadence set by business criticality | Drift alerting without an evaluation signal. Feature drift alone produces alert fatigue and unnecessary retraining |
| **ISO/IEC 42001:2023 — AI Management System** | The first certifiable AI management standard: Plan-Do-Check-Act on the Annex SL structure, ongoing AI risk and impact assessment across the lifecycle, model cards, audit logs, decision records, and written justification of both included and excluded controls | **The management-system spine of this module.** 1000FiX already holds **ISO 9001:2015**, and Annex SL harmonisation means the AIMS extends the existing system rather than duplicating it. Model cards, the AI risk register and the decision log are its artefacts | Certification at W6. Adopted as the design target and a W8+ business decision, not a launch prerequisite |
| **EU AI Act** | Risk tiering; for high-risk systems a documented risk-management system, data governance, technical documentation, automatic logging, human oversight, accuracy/robustness/cybersecurity, and registration. Transparency obligations under Article 50 require AI-generated content to be machine-detectable from 2 August 2026. High-risk obligations for employment and related domains were **deferred to 2 December 2027 by the AI Omnibus agreement** | **The structure, not the jurisdiction.** 1000FiX is a Bangladeshi company and is not placing systems on the EU market, so the Act does not bind it. It is nonetheless the most developed template available, and two of the Company's models — **dispatch assignment** and **incentive-affecting scoring** — fall squarely in what the Act treats as employment-related high-risk. Those models are built to that standard because it is the right standard, and because brand partners may eventually require it. **AI-generated customer-facing content is labelled as such** | Registration, conformity assessment and CE-style declarations. Those are jurisdictional obligations with no Bangladeshi counterpart |
| **NIST AI Risk Management Framework** | Govern, Map, Measure, Manage — a voluntary, outcome-based risk framework | **The Map–Measure–Manage cycle** as the shape of the AI risk register | Its US federal framing |
| **Model card practice (Google / industry)** | Purpose, training data, intended use, out-of-scope use, performance by segment, limitations, ethical considerations, owner, review date | **Model card mandatory for every production model**, refreshed on every version, with a review date. Overview §7 rule 8 | — |
| **Retrieval-augmented generation practice (2026)** | Grounding output in retrievable, current, verifiable evidence to reduce hallucination; hybrid and agentic retrieval; self-reflective and corrective patterns that re-query when evidence is weak; governance with access control and metadata so only authorised content reaches the model. **40–60% of RAG implementations fail before production, typically on retrieval quality and governance gaps** | **Grounding is mandatory** — no generative answer is served without cited sources from the Company's own corpus. **Retrieval quality is measured and gated separately from generation quality**, because that is where the failures actually are. **Access control is applied at retrieval**, so the assistant cannot surface a document the asker could not open | Agentic multi-hop retrieval at W6. It is the right 2027 answer; at W6 it multiplies failure modes for marginal gain |
| **Self-hosted LLM inference (Ollama)** *(selected in `02-05`)* | Local model serving with no external data egress | **The whole point.** Overview §7 rule 10: LLM inference is self-hosted and customer data does not leave Company infrastructure. This also satisfies PDPA 2026 residency | Commercial API inference for anything touching customer data |
| **Prompt-injection and output-guard practice** | Treating retrieved content and user input as untrusted; output filtering; refusing to act on instructions embedded in data | **Retrieved documents are data, never instructions**, and generative output cannot trigger an action — it can only propose one to a human | — |

**Design position.** Six deliberate differences, and they are the reason this module is
governed more tightly than its commercial priority (P2) would suggest.

**First, every model has a named consumer, a stated target and a tested fallback — or it is not
deployed.** This is the overview's rule and it is enforced as a registry constraint, not a
review checklist. The consequence is unusual and intentional: **the Company must be able to
operate fully with every model switched off.** Overview §9 sets *incidents caused by unavailable
models* to **zero**, which is only achievable if the fallback is a real, tested, exercised path
rather than a paragraph.

**Second, M26 never acts.** It returns a score, an explanation and a confidence. The consuming
module decides. This looks like a technicality and is the single most important architectural
choice in the module: it means every model-influenced decision has a module that owns it, an
audit trail in that module's own records, and a human who can be identified. A model that writes
directly into an operational record is a decision with no owner.

**Third, explanation is not optional and not technical.** Overview §7 rule 3 requires an
explanation *a user can understand*. A SHAP vector is not that. Every material prediction carries
a short, plain-language reason — *"assigned because: nearest available technician, holds the
required certification, 92% first-time-fix on this fault type"* — in Bengali and English. If the
model cannot produce a comprehensible reason, it does not serve that decision.

**Fourth, models that affect people are treated as the highest-risk class in the estate.**
Dispatch assignment affects technician earnings. Seller ranking affects a small business's
income. Incentive-related scoring affects pay. These carry mandatory bias testing across
protected and operationally-sensitive segments, documented results, published explanation, and
an always-available human override — regardless of what any regulator currently requires of a
Bangladeshi company.

**Fifth, deferral is a design decision, not a delay.** Overview §8 states the data prerequisites
for each model. Building before the data exists produces *confident nonsense*, and a single
visibly wrong early model destroys trust in the whole capability for years. The registry
enforces this: a model cannot be promoted to production without its data-sufficiency gate
passing.

**Sixth, generative AI is grounded, self-hosted, read-only and labelled.** It answers from the
Company's own knowledge base with citations, it runs on Company infrastructure, it cannot
execute an action, and customer-facing generated content is identified as AI-generated. Given
that the Company also operates a data-recovery laboratory under M06, the prohibition on
recovered customer data as training data (BRU-AIM-03) is absolute and structurally enforced —
M26 has no credential path to that environment at all.

---

## 5. Functional Areas & Features

### 5.1 Model Lifecycle & Registry

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AIM-001 | Model portfolio register | Maintain every model in the estate with its purpose, named consumer, accuracy target, defined fallback, risk class, owner and review date | **P0** | L5 |
| FR-AIM-002 | Training pipeline | Execute reproducible training runs against M62 features, recording code version, data snapshot, feature versions, hyperparameters and environment | P2 | L3 |
| FR-AIM-003 | Experiment tracking | Record every training run, its parameters and its evaluation results, so a result can be reproduced and compared | P2 | L4 |
| FR-AIM-004 | Model registry | Version every model artefact with its lineage, evaluation metrics, stage and approval history, as the single source of truth for what is serving | **P0** | L4 |
| FR-AIM-005 | Offline validation gate | Block promotion of a version that does not meet its stated accuracy target on a held-out set, and record the gate result | **P0** | L5 |
| FR-AIM-006 | Data-sufficiency gate | Block promotion where the training data does not meet the model's declared minimum history and volume prerequisites | **P0** | L5 |
| FR-AIM-007 | Deployment patterns | Support shadow, canary, champion–challenger and full deployment, with traffic proportion controlled per model | P2 | L3 |
| FR-AIM-008 | Automated rollback and demotion | Demote a version automatically on breach of its production performance floor, and restore the prior champion | **P0** | L5 |
| FR-AIM-009 | Retraining triggers | Retrain on schedule, and on drift — a material population-stability shift on a key feature coinciding with an evaluation drop | P2 | L5 |
| FR-AIM-010 | Model retirement | Retire a model with consumer notification, fallback confirmation and archival of its card and decision log | P2 | L5 |

### 5.2 Serving, Fallback & Guard Rails

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AIM-011 | Inference gateway | Serve every model through one entry point with authentication, request logging, timeout and per-consumer rate limiting | **P0** | L3 |
| FR-AIM-012 | **Fallback contract** | Return the model's declared fallback whenever it is unavailable, times out or returns low confidence, and mark the response as a fallback so the consumer can record it | **P0** | L3 |
| FR-AIM-013 | Fallback testing | Test every consumer's fallback path on a defined cycle by deliberately disabling the model, and record the result | **P0** | L5 |
| FR-AIM-014 | **Business guard rails** | Reject or clamp any model output that would cross a business guard rail — price floor or ceiling, certification requirement, safety rule, entitlement limit — and log the intervention | **P0** | L3 |
| FR-AIM-015 | Confidence and abstention | Return a calibrated confidence with every prediction, and abstain rather than guess below the model's declared threshold | P2 | L3 |
| FR-AIM-016 | Batch scoring | Score in batch for forecasting and portfolio-level models, with the same logging and guard rails as online serving | P2 | L3 |
| FR-AIM-017 | Serving performance | Meet the published latency target per model class, so no consumer's user experience depends on model speed | P2 | L3 |

### 5.3 Operational Models — Service, Field & Logistics

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AIM-018 | **Dispatch assignment scoring** | Score candidate technicians for a job. **Consumer M02. Target: 70% auto-assign, ≥ 90% dispatcher agreement. Fallback: rule-based scoring** | P2 | L5 |
| FR-AIM-019 | **Repair duration prediction** | Predict job duration. **Consumers M02, M31. Target: MAE < 20%. Fallback: standard time from the M37 catalogue** | P2 | L5 |
| FR-AIM-020 | **Travel time prediction** | Predict travel time between locations. **Consumers M02, M03. Target: MAE < 15%. Fallback: OSRM static estimate** | P2 | L5 |
| FR-AIM-021 | **Fault classification from complaint text** | Classify the likely fault from free-text complaint, in Bengali and English. **Consumers M01, M32. Target: top-3 accuracy > 80%. Fallback: manual selection** | P2 | L5 |
| FR-AIM-022 | **Quality risk scoring** | Score jobs at risk of quality failure. **Consumer M23. Target: precision > 60% at the top decile. Fallback: sampling plan** | P3 | L5 |
| FR-AIM-023 | **Service demand forecast** | Forecast service demand by period, location and type. **Consumers M55, M02. Target: MAPE < 18%. Fallback: prior-period actuals** | P2 | L5 |

### 5.4 Supply Chain, Asset & Commercial Models

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AIM-024 | **Parts demand forecast** | Forecast part consumption by location and period. **Consumer M43. Target: MAPE < 22%. Fallback: moving average** | P2 | L5 |
| FR-AIM-025 | **Predictive failure** | Predict component or asset failure from telemetry and history. **Consumers M48, M08. Target: precision > 70%. Fallback: calendar-based maintenance** | P3 | L5 |
| FR-AIM-026 | **Price elasticity and win probability** | Estimate quotation win probability and price sensitivity. **Consumer M11. Target: AUC > 0.75. Fallback: static price book** | P3 | L5 |
| FR-AIM-027 | **Trade-in valuation** | Value a used device from model, age, condition and market reference. **Consumer M14. Target: within 10% of assessed value, 75% of the time. Fallback: depreciation table** | P3 | L5 |
| FR-AIM-028 | **Fraud and anomaly detection** | Detect anomalous transactions, claims and settlement patterns. **Consumers M12, M19, M53. Target: recall > 80% at 5% false-positive rate. Fallback: manual review thresholds** | P2 | L5 |

### 5.5 Customer Models

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AIM-029 | **Churn risk** | Score customer churn risk across the lifecycle. **Consumers M07, M34. Target: AUC > 0.72. Fallback: recency-frequency-value rules** | P3 | L5 |
| FR-AIM-030 | **Bengali NLP — intent, entity, sentiment** | Extract intent, entities and sentiment from Bengali and English text and speech. **Consumers M32, M34. Target: intent accuracy > 88%. Fallback: menu-driven flow** | P2 | L5 |
| FR-AIM-031 | Propensity and next-best-offer | Score propensity and recommend the next best offer, **advisory only** — consuming modules function without it | P3 | L5 |

### 5.6 Document & Generative Services

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AIM-032 | **Document extraction (OCR / IE)** | Extract structured fields from documents in Bengali and English. **Consumers M52, M24, M09. Target: field accuracy > 92%. Fallback: manual keying** | P2 | L5 |
| FR-AIM-033 | Self-hosted generative inference | Serve generative models **on Company infrastructure**, with no customer data leaving it, under the same gateway, logging and guard rails as every other model | **P0** | L4 |
| FR-AIM-034 | Retrieval-augmented grounding | Ground every generative answer in retrievable content from the Company's own corpus (M61 knowledge base, M24 documents), returning citations with the answer | **P0** | L5 |
| FR-AIM-035 | Retrieval quality measurement | Measure and gate retrieval quality separately from generation quality, and refuse to answer where retrieved evidence is insufficient | P2 | L5 |
| FR-AIM-036 | Access-controlled retrieval | Apply the asker's own entitlements at retrieval, so a generated answer can never surface content the asker could not open directly | **P0** | L5 |
| FR-AIM-037 | Generative guard rails | Treat retrieved content and user input as untrusted data, never as instructions; filter output; **prevent generative output from triggering any action — it may only propose one to a human** | **P0** | L5 |
| FR-AIM-038 | AI-generated content labelling | Label customer-facing AI-generated content as AI-generated | P2 | L5 |

### 5.7 Governance, Explainability & Assurance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AIM-039 | **Model cards** | Maintain a current card per production model — purpose, training data, intended and out-of-scope use, performance by segment, limitations, owner, review date — refreshed on every version | **P0** | L5 |
| FR-AIM-040 | **Explainability** | Return, with every material prediction, a plain-language explanation a user can understand, in Bengali and English, alongside the technical attribution | **P0** | L5 |
| FR-AIM-041 | **Decision logging** | Log every model-influenced decision with inputs, output, confidence, model version, explanation, guard-rail interventions and override status, retained and queryable | **P0** | L5 |
| FR-AIM-042 | **Bias and fairness testing** | Test every model affecting people — dispatch, incentives, seller ranking — across defined segments before promotion and on a recurring cycle, and document the results | **P0** | L5 |

*(Production monitoring — performance, data drift, concept drift, latency, availability — and
override capture and feedback are delivered through FR-AIM-008, FR-AIM-009 and FR-AIM-041
together with the automations in §11, and are specified as technical functions in §6.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Single gateway, no direct model access** | No consuming module can reach a model except through the inference gateway. There is no second path, and therefore no unlogged prediction |
| T-02 | **Fail-safe, not fail-closed** | Unlike the M06 destruction gate, model unavailability must **never** block a business process. The gateway returns the declared fallback and marks the response as such |
| T-03 | **Guard rails enforced at the gateway** | Guard rails are applied to the model's output before it reaches the consumer, so an ungoverned model cannot bypass them by being called differently |
| T-04 | **Registry is the source of truth for what is serving** | The gateway resolves the serving version from the registry; a model artefact cannot be deployed outside it |
| T-05 | **Automated demotion** | Production performance breaches trigger automatic demotion and restoration of the prior champion, without human initiation |
| T-06 | **Drift detection** | Population stability index and Kolmogorov–Smirnov tests on every served feature, plus attribution-shift monitoring; retraining triggers on **PSI breach coinciding with an evaluation drop**, not on drift alone |
| T-07 | **Check cadence by criticality** | Revenue- and people-affecting models are drift-checked daily; others weekly. Cadence is a registry property, not a convention |
| T-08 | **Point-in-time correct training** | All training features are retrieved from M62's feature store with point-in-time correctness; M26 cannot construct a training set by direct warehouse query |
| T-09 | **Training-serving consistency** | The features served at inference are the same definitions and versions used in training; a mismatch raises a skew alert from M62 and blocks promotion |
| T-10 | **Reproducible training** | Any training run can be reproduced exactly from its recorded code version, data snapshot, feature versions, hyperparameters and environment |
| T-11 | **Immutable decision log** | The decision log is append-only, retained for the model's risk-class retention period, and queryable by decision, subject, model and version |
| T-12 | **Explanation generation** | Plain-language explanation is generated from the technical attribution at inference time and stored with the decision, not reconstructed later |
| T-13 | **No egress for generative inference** | Generative models run on Company infrastructure; the module has no configured path to an external inference provider for any request containing customer data |
| T-14 | **Retrieval entitlement enforcement** | Retrieval applies the asker's M29 entitlements before ranking, so unauthorised content cannot enter the generation context |
| T-15 | **Untrusted-content handling** | Retrieved documents and user input are treated as data; instructions embedded in them are not executed |
| T-16 | **No action from generation** | The generative surface has no write capability into any operational system; it can only produce a proposal for a human |
| T-17 | **M06 isolation** | M26 holds no credential, network path or data grant to the M06 data-recovery environment. BRU-AIM-03 is enforced structurally, not procedurally |
| T-18 | **Performance** | Online inference p95 ≤ 300 ms; dispatch scoring ≤ 500 ms end to end including guard rails; generative first token ≤ 2 s; batch scoring within its declared window |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M26 |
|---|---|---|
| **Dispatcher** | Assigns from memory of who is good and who is free | Receives a ranked recommendation with a plain reason; agrees or overrides, and the override trains the model |
| **Technician** | Given work with no visible logic; suspects favouritism | Sees why they were assigned; the basis is published, tested for bias, and appealable |
| **Field supervisor** | Estimates job duration by feel; schedules pessimistically | Works from predicted durations with measured error, so the day is planned rather than padded |
| **Inventory Manager** | Orders on moving average and instinct | Receives a forecast with a stated accuracy, and knows when it is being overridden |
| **Pricing Manager** | Prices from a static book | Sees win probability and elasticity, within guard rails that cannot be crossed |
| **Assessment officer (M14)** | Values a trade-in by market feel | Starts from a modelled valuation and decides — **the model advises, the officer decides** |
| **Contact-centre agent** | Reads and classifies every Bengali message manually | Intent and sentiment extracted; routing suggested; the agent confirms |
| **Accounts Payable clerk** | Keys every vendor invoice | Fields extracted with measured accuracy; the clerk verifies exceptions |
| **Quality Manager** | Samples at random | Samples where risk is scored highest, and can evidence why |
| **CTO** | Would carry models nobody monitors | Carries a registry, cards, drift monitoring, bias tests and a decision log |
| **Customer** | Subject to automated decisions with no visibility | Decisions are explained, human-confirmable and overridable |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Technician productivity** | Dispatch scoring plus duration and travel prediction lifting jobs per technician per day from 4–5 to 8–9 | **BDT 130 lac/year** (M02 + M26) |
| **Automatic assignment (KPI-013)** | Assignment made without a dispatcher touching it, at ≥ 90% dispatcher agreement | **0% → 70%** |
| **Inventory cost reduction** | Parts demand forecasting driving replenishment parameters in M43 | **BDT 34 lac/year** (M15 + M26) |
| **Dynamic pricing margin uplift** | Win probability and elasticity within guard rails | **BDT 40 lac/year** (M11 + M26) |
| **Churn reduction (KPI-023)** | Churn risk scoring feeding retention action in M07 and M34 | Churn **~15% → < 8%** |
| **Fraud and leakage prevention** | Anomaly detection across marketplace, ledger and settlement | Protects marketplace commission (BDT 84 lac) and warranty recovery (BDT 100 lac) lines |
| **Document processing effort** | OCR and extraction at > 92% field accuracy across payables, warranty and documents | Direct contribution to the **BDT 62 lac/year** administrative saving |
| **Bengali self-service** | Intent and sentiment enabling containment in M32 before an agent is involved | Underpins contact-centre cost per contact |
| **Trade-in offer quality** | Modelled valuation with a margin guardrail reduces both overpayment and lost deals | Protects the **BDT 65 lac/year** refurbishment margin |
| **Combined model-dependent benefit** | — | Roughly **BDT 200+ lac/year of the BDT 876 lac case runs through this module** |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Fairness that can be demonstrated, not asserted** | When a technician asks why they got the difficult job, there is an answer, it is recorded, and it has been tested for bias. This is the difference between measurement being accepted and being resented |
| **Institutional knowledge captured** | The best dispatcher's judgement, encoded, tested and improved, stops being a single point of failure who might resign |
| **Trust preserved by deferral** | Waiting until the data exists means the first model people see actually works. One visibly stupid early prediction costs years of adoption |
| **ISO 42001 readiness** | Model cards, an AI risk register, decision logs and documented control justification are the substance of an AIMS, extending the existing ISO 9001 system rather than duplicating it |
| **Regulatory anticipation** | Bangladesh has no AI statute today. PDPA 2026 already touches automated processing, and the international direction is clear. Building to a recognised standard now is cheaper than retrofitting to one later |
| **Customer data never leaves** | Self-hosted inference means the Company can truthfully say no customer information is sent to a third-party AI service — a claim very few local competitors can make |
| **The M06 firewall** | A company that recovers customers' data and also builds models must be able to prove the two never meet. Structural isolation, not policy, is what makes that provable |
| **A capability rather than a project** | A registry, a gateway, monitoring and a governance regime mean the fifteenth model costs a fraction of the first |

---

## 8. Lifecycle & State Models

### 8.1 Model Lifecycle

```
   PROPOSED
   (named consumer · stated target · defined fallback — all three, or it stops here)
      │
      ▼
   DATA SUFFICIENCY GATE ──── fail ──► DEFERRED  (overview §8: stated prerequisite,
      │ pass                            revisit    revisit date, not cancelled)
      ▼
   IN TRAINING  ◄──── retrain (schedule · PSI breach + evaluation drop · override volume)
      │
      ▼
   OFFLINE VALIDATION ──── below target ──► REJECTED
      │ meets target
      ▼
   BIAS & FAIRNESS TESTING  (mandatory where the model affects people)
      │ documented
      ▼
   MODEL CARD COMPLETE ──── incomplete ──► BLOCKED
      │
      ▼
   SHADOW  (production traffic, output logged, not served to the consumer)
      │  performance holds
      ▼
   CANARY  (small traffic proportion, guard rails active, fallback exercised)
      │  performance holds
      ▼
   CHAMPION  ◄──────── promotion ──────── CHALLENGER
      │                                    (runs in shadow against the champion;
      │                                     promoted only after beating it on the
      │                                     declared metric for the declared period)
      │
      │ production performance floor breached
      ▼
   AUTO-DEMOTED ──► prior champion restored ──► investigation
      │
      │ superseded, or consumer retired
      ▼
   RETIRED  (consumers notified · fallback confirmed as the standing path ·
             card and decision log archived)
```

| From | To | Guard | Actor |
|---|---|---|---|
| Proposed | Data Sufficiency Gate | **Named consumer, accuracy target and fallback all declared** | Model owner |
| Data Sufficiency Gate | In Training | Declared minimum history and volume met | System |
| Data Sufficiency Gate | Deferred | Prerequisite not met; revisit date set | System |
| Offline Validation | Bias Testing | Meets the stated target on a held-out set | System |
| Bias Testing | Model Card | Results documented — **mandatory for people-affecting models** | Model owner + CTO |
| Model Card | Shadow | Card complete: purpose, data, limits, metrics, owner, review date | Data Steward |
| Shadow | Canary | Shadow performance holds for the declared period; **consumer's fallback tested** | Model owner |
| Canary | Champion | Canary performance holds; guard-rail interventions within tolerance | CTO |
| Champion | Auto-Demoted | Production performance floor breached | **System — no human initiation** |
| Any | Retired | Consumers notified; fallback confirmed as the standing path | CTO |

### 8.2 An Inference, End to End

```
  CONSUMING MODULE (e.g. M02 dispatch)
        │  request + context
        ▼
  ┌──────────────────────────────────────────────────────────┐
  │  INFERENCE GATEWAY                                        │
  │  authenticate · rate limit · start decision log           │
  └────────┬─────────────────────────────────────────────────┘
           │  features by name+version
           ▼
      M62 FEATURE STORE (online)  ──unavailable──┐
           │                                      │
           ▼                                      │
      MODEL (registry-resolved version)           │
           │  score + confidence + attribution    │
           ▼                                      │
  ┌──────────────────────────────────────────┐    │
  │  GUARD RAILS                              │    │
  │  price floor/ceiling · certification      │    │
  │  requirement · safety rule · entitlement  │    │
  │  → clamp or reject, and log the           │    │
  │    intervention                           │    │
  └────────┬─────────────────────────────────┘    │
           │                                       │
           ▼                                       ▼
  ┌──────────────────────────────────────────────────────────┐
  │  low confidence / timeout / unavailable / guard-rail      │
  │  rejection  ──►  DECLARED FALLBACK, marked as fallback    │
  └────────┬─────────────────────────────────────────────────┘
           ▼
  EXPLANATION generated (plain language, bn + en)
           │
           ▼
  DECISION LOG written (inputs · output · confidence · model version ·
                        explanation · guard-rail interventions · fallback flag)
           │
           ▼
  CONSUMING MODULE ACTS
           │
           ├── material customer or financial impact ──► HUMAN CONFIRMATION (BRU-AIM-01)
           │
           └── human overrides ──► override + reason captured ──► fed back to training
```

### 8.3 Drift & Retraining

```
   DAILY (revenue/people-affecting) or WEEKLY (others)
        │
        ▼
   FEATURE DRIFT (PSI, KS)          EVALUATION SIGNAL (labelled outcomes)
        │                                     │
        └──────────────┬──────────────────────┘
                       ▼
        ┌──────────────────────────────────────┐
        │ PSI breach AND evaluation drop       │──► RETRAIN TRIGGERED
        │ PSI breach only                      │──► WATCH  (alert, no retrain)
        │ evaluation drop only                 │──► INVESTIGATE (label or process change?)
        │ neither                              │──► no action
        └──────────────────────────────────────┘
                       │
                       ▼
        performance floor breached at any point ──► AUTO-DEMOTE
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

**The first ten rules are Category J Overview §7 — the non-negotiable AI governance regime —
reproduced here as enforceable rules.**

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| **BRU-AIM-01** | **Any decision with material customer or financial impact requires human confirmation** | **H** | CTO |
| **BRU-AIM-02** | **No model output may cross a business guard rail — price floor or ceiling, certification requirement, safety rule** | **H** | CTO |
| BRU-AIM-03 | **Recovered customer data (M06) is never used as training data for any model** | **H** | CTO / CDO |
| BRU-AIM-04 | Every material prediction carries an explanation a user can understand | **H** | CTO |
| BRU-AIM-05 | Every human override is captured with a reason and fed back into training | **H** | CTO |
| BRU-AIM-06 | Every consuming module has a **tested** fallback for model unavailability | **H** | CTO + consuming module owner |
| BRU-AIM-07 | Models affecting people — dispatch, incentives, seller ranking — are tested for bias and the results documented | **H** | CTO |
| BRU-AIM-08 | Every production model has a current model card: purpose, data, limits, metrics, owner, review date | **H** | CTO |
| BRU-AIM-09 | Every model-influenced decision is logged with inputs, output, model version and override status | **H** | CTO |
| BRU-AIM-10 | LLM inference is self-hosted; customer data does not leave Company infrastructure | **H** | CTO |
| BRU-AIM-11 | **A model without a named consumer, an accuracy target and a defined fallback is not deployed** | **H** | CTO |
| BRU-AIM-12 | A model cannot be promoted where its declared data-sufficiency prerequisite is unmet | **H** | CTO |
| BRU-AIM-13 | A model cannot be promoted without meeting its stated target on a held-out set | **H** | CTO |
| BRU-AIM-14 | **Model unavailability never blocks a business process; the gateway returns the fallback** | **H** | CTO |
| BRU-AIM-15 | No consuming module may reach a model except through the inference gateway | **H** | CTO |
| BRU-AIM-16 | **M26 never writes to an operational record; it returns a score and an explanation, and the consuming module acts** | **H** | CTO |
| BRU-AIM-17 | Training features are retrieved from M62's feature store with point-in-time correctness; direct warehouse construction of training sets is not permitted | **H** | CTO |
| BRU-AIM-18 | A training-serving skew alert from M62 blocks promotion | **H** | CTO |
| BRU-AIM-19 | Production performance breach triggers automatic demotion and restoration of the prior champion | **C** | CTO |
| BRU-AIM-20 | A challenger is promoted only after beating the champion on the declared metric for the declared period | **C** | CTO |
| BRU-AIM-21 | Every generative answer is grounded in retrievable Company content and returns its citations | **H** | CTO |
| BRU-AIM-22 | Retrieval applies the asker's own entitlements; a generated answer cannot surface content the asker could not open | **H** | CTO |
| BRU-AIM-23 | Retrieved content and user input are data, never instructions; generative output cannot trigger an action | **H** | CTO |
| BRU-AIM-24 | Customer-facing AI-generated content is labelled as AI-generated | **H** | CTO |
| BRU-AIM-25 | A model below its declared confidence threshold abstains rather than guessing | **C** | CTO |
| BRU-AIM-26 | Model cards, bias test results and the AI risk register are reviewed at least annually and on every material version change | **S** | CTO / Quality Manager |
| BRU-AIM-27 | Decision logs are immutable and retained for the model's risk-class retention period | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.model` | `fix_model` | A model in the portfolio | code, name, purpose, model_class, **consumer_modules**, **accuracy_target**, **fallback_definition**, risk_class (people_affecting / financial / operational / advisory), owner_id, review_date, drift_check_cadence, confidence_threshold, state |
| `fix.model.version` | `fix_model_version` | One version | model_id, version, training_run_id, artefact_ref (MLflow), evaluation_metrics, stage (shadow / canary / champion / challenger / demoted / retired), promoted_by, promoted_at, demoted_at, demotion_reason |
| `fix.training.run` | `fix_training_run` | A reproducible training execution | model_id, code_version, data_snapshot_ref, feature_versions, hyperparameters, environment_ref, started_at, ended_at, metrics, outcome |
| `fix.data.sufficiency.gate` | `fix_data_sufficiency_gate` | The overview §8 prerequisite | model_id, required_history_months, required_volume, source_modules, evaluated_at, result, deferred_until |
| `fix.model.card` | `fix_model_card` | The governance artefact | model_version_id, purpose, training_data_description, intended_use, out_of_scope_use, performance_by_segment, limitations, ethical_considerations, owner_id, review_date, document_id (M24), current |
| `fix.bias.test` | `fix_bias_test` | Fairness evidence | model_version_id, segments_tested, metric_by_segment, disparity_measures, assessment, documented_by, tested_at, next_due |
| `fix.guard.rail` | `fix_guard_rail` | A limit a model output cannot cross | model_id, rail_type (price_floor / price_ceiling / certification / safety / entitlement), parameter_source_module, condition, action (clamp / reject), owner_id |
| `fix.guard.rail.intervention` | `fix_guard_rail_intervention` | When a rail fired | decision_log_id, guard_rail_id, model_output, action_taken, final_output, occurred_at |
| `fix.inference.request` | `fix_inference_request` | Gateway telemetry | model_id, model_version, consumer_module, requested_at, latency_ms, outcome (served / fallback / abstained / rejected), confidence |
| `fix.decision.log` | `fix_decision_log` | **The audit record of every model-influenced decision** | model_id, model_version, consumer_module, decision_ref, subject_ref, inputs_snapshot, output, confidence, explanation_text_en, explanation_text_bn, attribution, guard_rail_interventions, fallback_used, human_confirmed_by, override_flag, override_reason, occurred_at, immutable |
| `fix.override` | `fix_override` | Human correction, fed back to training | decision_log_id, overridden_by, original_output, human_output, reason_code, reason_text, occurred_at, used_in_training_run_id |
| `fix.drift.observation` | `fix_drift_observation` | Drift monitoring | model_id, feature_name, observed_at, psi, ks_statistic, attribution_shift, threshold, breached |
| `fix.model.performance` | `fix_model_performance` | Production performance over time | model_id, model_version, period, metric_name, value, target, floor, breach_flag, labelled_sample_size |
| `fix.fallback.test` | `fix_fallback_test` | Evidence the fallback works | model_id, consumer_module, tested_at, method (disabled / simulated), consumer_behaviour, outcome, incidents_raised |
| `fix.generative.session` | `fix_generative_session` | A grounded generative interaction | requester_id, entitlements_applied, query, retrieved_document_refs, retrieval_score, answer, citations, refused_flag, refusal_reason, labelled_as_ai, occurred_at |
| `fix.retrieval.corpus` | `fix_retrieval_corpus` | Grounding sources and their index state | source_module (M61 / M24), document_ref, indexed_at, entitlement_tags, embedding_version, active |
| `fix.ai.risk` | `fix_ai_risk` | The AI risk register | model_id, risk_description, category, likelihood, impact, treatment, control_ref, owner_id, review_date, status |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.feature` / `fix.feature.value` | **M62** | **Point-in-time correct training retrieval and online serving — the only feature path** |
| `fix.dataset` / `fix.metric` | M62 | Evaluation datasets and outcome labels |
| `fix.role` / `fix.record.rule` | M29 | Gateway authentication and retrieval entitlement |
| `fix.knowledge.article` | M61 | Generative grounding corpus |
| `fix.document` | M24 | Grounding corpus; model card retention |
| `fix.margin.floor` / `fix.rate.card` | M11 | Guard-rail parameter source |
| `fix.competency` | M22 | Guard-rail parameter source (technician competency) |
| Consuming modules' decision records | Consuming module | Correlated by decision reference; **M26 never writes them** |
| `fix.data.case` | **M06** | **No access — structurally prohibited (BRU-AIM-03, T-17)** |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-AIM-01 | Model proposed | Verify a named consumer, accuracy target and fallback are all declared; evaluate the data-sufficiency gate | **Block** — a model missing any of the three does not proceed |
| AUT-AIM-02 | Data-sufficiency gate fails | Defer with a stated prerequisite and revisit date; notify the model owner and the consuming module | Record as deferred, not rejected |
| AUT-AIM-03 | Training run completes | Record metrics; evaluate against target; run bias testing where the model affects people | Block promotion on a missing bias test |
| AUT-AIM-04 | Version meets target and bias testing is documented | Require a complete model card, then deploy to shadow | Block promotion without a current card |
| AUT-AIM-05 | Shadow period completes with performance held | **Test the consumer's fallback path**, then promote to canary | Block canary until the fallback is proven |
| AUT-AIM-06 | Canary period completes within tolerance | Promote to champion; notify consumers; archive the prior champion | Hold at canary; alert the model owner |
| AUT-AIM-07 | Production performance floor breached | **Demote automatically; restore the prior champion; raise an investigation; notify consumers** | Escalate to the CTO immediately |
| AUT-AIM-08 | Drift check due (daily or weekly by criticality) | Compute PSI and KS per feature and attribution shift; classify against the evaluation signal | Alert on check failure — an unchecked model is an unmonitored model |
| AUT-AIM-09 | PSI breach **and** evaluation drop | Trigger retraining; notify the model owner | Escalate if retraining fails twice |
| AUT-AIM-10 | PSI breach without evaluation drop | Raise a watch alert; do not retrain | Log to the model health board |
| AUT-AIM-11 | M62 publishes `feature.skew_detected` | Block promotion of any pending version using that feature; alert the model owner and the feature owner | Hard block |
| AUT-AIM-12 | Model unavailable, times out, or returns below its confidence threshold | Return the declared fallback marked as fallback; record it | **Never block the consumer** |
| AUT-AIM-13 | Model output would cross a guard rail | Clamp or reject per the rail's action; log the intervention with both values | Return the fallback if rejection leaves no valid output |
| AUT-AIM-14 | Any prediction served | Write the decision log with inputs, output, confidence, version, explanation and interventions | **Block the response if logging fails** — an unlogged prediction violates BRU-AIM-09 |
| AUT-AIM-15 | Human overrides a prediction | Capture the override, its reason and the human's output; queue it for the next training cycle | Alert if override rate exceeds the model's tolerance |
| AUT-AIM-16 | Override rate exceeds tolerance | Raise a model health investigation — sustained disagreement means the model is wrong, not the humans | Escalate to the CTO |
| AUT-AIM-17 | Fallback test cycle due | Disable the model for the consumer under controlled conditions; verify the consumer operates; record the result | Escalate — an untested fallback is an unproven fallback |
| AUT-AIM-18 | Model card review date reached | Notify the owner; mark the card as due; block the next promotion until refreshed | Escalate at 30 days overdue |
| AUT-AIM-19 | Bias test cycle due for a people-affecting model | Execute, document and notify; block the next promotion until complete | Escalate to the CTO and Quality Manager |
| AUT-AIM-20 | Generative query received | Apply the asker's entitlements at retrieval; measure retrieval quality; refuse where evidence is insufficient | Refuse with an explanation rather than answer ungrounded |
| AUT-AIM-21 | Generative answer produced | Attach citations; label as AI-generated where customer-facing; log the session | Block the response without citations |
| AUT-AIM-22 | Model retirement requested | Notify consumers; confirm the fallback becomes the standing path; archive card and decision log | Block retirement without consumer confirmation |
| AUT-AIM-23 | New knowledge article or document published in M61 / M24 | Re-index into the retrieval corpus with its entitlement tags | Alert — a stale corpus produces confidently outdated answers |

---

## 12. Interfaces

### 12.1 Upstream — M26 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M62 Data Platform** | **Point-in-time correct training features, online serving features, evaluation datasets, outcome labels, skew alerts** | **Feature API + extract + events** |
| M29 Identity & Security | Gateway authentication, consumer identity, retrieval entitlements | Service |
| M28 Integration Platform | Event transport and API gateway exposure | Service |
| M30 Platform Administration | GPU and compute capacity, model serving infrastructure | Service |
| M61 Knowledge Management | Grounding corpus — technical articles, procedures, guides | REST + event |
| M24 Documents | Grounding corpus; model card retention | REST + command |
| M11 Pricing | Price floor and ceiling values for guard rails | REST |
| M22 Learning & Certification | Technician certification state for dispatch guard rails | REST |
| **All consuming modules** | Outcome labels, override events, actual results for evaluation | Events + warehouse extract |
| **M06 Data Services** | **No interface. Structurally isolated (BRU-AIM-03)** | **None** |

### 12.2 Downstream — M26 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M02 Field Service | Assignment score, duration prediction, travel prediction | **REST with timeout and fallback** |
| M31 Workshop | Duration prediction, quality risk | REST with fallback |
| M03 Logistics | Travel time prediction | REST with fallback |
| M43 Demand Planning | Parts demand forecast | Batch + REST |
| M55 Workforce / M02 | Service demand forecast | Batch |
| M48 IoT / M08 Contracts | Predictive failure scores | REST with fallback |
| M11 Pricing | Win probability, elasticity — **within guard rails** | REST with fallback |
| M14 Trade-In | Valuation, condition scoring from photographs | REST with fallback |
| M12 Marketplace / M19 / M53 | Fraud, collusion, anomaly and leakage scores | REST + batch |
| M07 CRM / M34 Experience | Churn risk, propensity, sentiment, theme extraction | REST with fallback |
| M32 Conversational AI | Intent, entity, sentiment, speech-to-text, **grounded generative inference** | REST with timeout |
| M01 Service Order | Fault classification from complaint text | REST with fallback |
| M23 Quality | Quality risk scoring | REST + batch |
| M52 Payable / M24 / M09 | Document extraction | REST with fallback |
| M25 Business Intelligence | Predictions with explanations and model versions, **for display only** | REST |
| M60 GRC | AI risk register, bias test results, governance events | Events + extract |
| M62 | Feature consumption registration and evaluation feedback | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `model.promoted` | model, version, stage, target achieved | consuming modules, M25, M60 |
| `model.demoted` | model, version, reason, restored champion | **consuming modules**, M60, CTO |
| `model.retired` | model, consumers, standing fallback | consuming modules |
| `model.deferred` | model, unmet prerequisite, revisit date | consuming modules, programme |
| `model.card_due` | model, version, owner, days overdue | owner, Quality |
| `model.bias_test_completed` | model, segments, disparity measures, assessment | **M60**, Quality |
| `model.drift_detected` | model, feature, PSI, evaluation signal, classification | model owner, M62 |
| `model.retraining_triggered` | model, trigger, drift and evaluation evidence | model owner |
| `model.performance_breach` | model, version, metric, value, floor | **CTO**, consuming modules |
| `model.fallback_served` | model, consumer, reason, count | consuming module, M25 |
| `model.fallback_tested` | model, consumer, method, outcome | consuming module, M60 |
| `model.guard_rail_fired` | model, rail, output, action, final value | **M60**, owning module |
| `model.override_recorded` | model, decision, human output, reason | model owner, M62 |
| `model.override_rate_exceeded` | model, rate, tolerance, period | **CTO** |
| `generative.answer_refused` | session, reason (insufficient evidence / entitlement) | M32, M61 |
| `ai.risk_raised` | model, risk, likelihood, impact, treatment | **M60** |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-AIM-01 | MLflow | Bidirectional | Experiment tracking, model registry, artefact storage, stage transitions |
| INT-AIM-02 | Ollama (self-hosted LLM inference) | Bidirectional | Generative inference **on Company infrastructure only** |
| INT-AIM-03 | Vector index for retrieval | Bidirectional | Embedding storage and entitlement-filtered retrieval |
| INT-AIM-04 | OSRM (via M02 / M03) | Inbound | Static travel estimate as the travel-model fallback |
| INT-AIM-05 | OCR engine | Bidirectional | Bengali and English document extraction |
| INT-AIM-06 | Pre-trained Bengali language models | Inbound | Base models for intent, entity and sentiment, fine-tuned locally |
| — | **Commercial LLM APIs** | **None** | **Explicitly excluded for any request containing customer data (BRU-AIM-10)** |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/ml/predict/{model}` | POST | **The single inference path** — score, confidence, explanation, guard-rail result, fallback flag | All consuming modules |
| `/api/v1/ml/batch/{model}` | POST | Batch scoring with the same logging and guard rails | M43, M23, M12 |
| `/api/v1/ml/models` | GET | Portfolio with purpose, consumer, target, fallback, state, card status | M25, M60, audit |
| `/api/v1/ml/models/{code}/card` | GET | Current model card | M25, M60, auditor |
| `/api/v1/ml/models/{code}/health` | GET | Performance, drift, override rate, fallback rate | M25, model owner |
| `/api/v1/ml/decisions/{ref}` | GET | The decision log entry for a specific decision — inputs, output, version, explanation, override | Consuming module, auditor, subject |
| `/api/v1/ml/overrides` | POST | Record a human override with its reason | Consuming modules |
| `/api/v1/ml/generate` | POST | Grounded generative answer with citations, entitlement-filtered | M32, M61, internal surfaces |
| `/api/v1/ml/models/{code}/fallback-test` | POST | Execute a controlled fallback test | Data Squad |
| `/api/v1/ml/risk-register` | GET | AI risk register | M60, CTO |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R02 Chief Technology Officer** | C R U D A | All — portfolio, promotion, demotion, guard rails, risk register |
| Data Scientist | C R U | Training, experiments, evaluation, model cards; **cannot promote to champion alone** |
| ML Engineer | C R U | Gateway, serving, monitoring, deployment pipelines |
| Model Owner *(per model, from the consuming function)* | R U A | Accepts the target, the fallback and the card for their model; reviews override rate |
| Data Steward | R A | Model card completeness, bias test presence, registry hygiene |
| **CDO / Data Protection Officer** | R A | Training-data provenance, BRU-AIM-03 assurance, PDPA automated-processing position |
| R32 Quality Manager / ISO Coordinator | R A | Bias test results, model cards, AI risk register, ISO 42001 evidence |
| Consuming module owner | R | Own model's health, fallback test results, override rate, decision logs for own decisions |
| R05 Operations Director | R A | Dispatch model — accepts the target and the override-rate tolerance |
| Dispatcher / supervisor / agent | R | Prediction and its explanation for the decision in front of them; **always able to override** |
| R38 External Auditor | R | Model cards, bias tests, decision-log samples, risk register — time-boxed |
| Any decision subject *(technician, seller, customer)* | R | **The explanation for a decision about them** |

**Field-level restrictions.** Raw model artefacts, hyperparameters and training snapshots are
visible to the Data Squad only. Decision-log inputs are visible to the consuming module's
authorised roles, the subject of the decision, and audit. No role can read M06 case content
through any M26 surface, because no such path exists.

**Segregation of duties.**

| Incompatible combination | Why |
|---|---|
| Data scientist who trained the model **and** sole promoter to champion | Promotion is an independent decision |
| Model owner **and** bias test reviewer | The fairness check must be external to the model's beneficiary |
| Guard-rail parameter owner **and** guard-rail enforcement administrator | The business sets the limit; the platform enforces it |
| Anyone with M06 case access **and** M26 training-data access | Structural enforcement of BRU-AIM-03 |
| Override tolerance setter **and** override rate reviewer | Tolerances must not be widened to hide disagreement |

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Model portfolio board | CTO, Data Squad | Real time | Every model, stage, version, health, card status, owner, review date |
| Model health dashboard | Model owners, CTO | Daily | Performance against target and floor, drift, latency, availability, fallback rate, override rate |
| **Governance conformance report** | CTO, Quality Manager, GRC | Weekly | **Models with a current card (target 100%)**, bias tests current, decision logging completeness, fallback tests current |
| Drift report | Data Squad, model owners | Daily / weekly by criticality | PSI and KS by feature, attribution shift, evaluation signal, classification and action taken |
| Override analysis | Model owners, CTO | Weekly | Override rate and reasons by model, user and segment — the earliest signal that a model is wrong |
| **Fallback readiness report** | CTO, consuming module owners | Monthly | Every consumer's fallback, when it was last tested, and the outcome. **Incidents caused by unavailable models — target zero** |
| Guard-rail intervention report | CTO, owning modules, GRC | Weekly | Which rails fired, how often, on which models — frequent firing means the model is misaligned with policy |
| Dispatch model performance | Operations Director, CTO | Daily | **Auto-assign rate (target > 70%)**, **dispatcher agreement (target > 90%)**, by branch and zone |
| Forecast accuracy | Inventory Manager, Demand Planner | Monthly | MAPE against target by part class and location; forecast-versus-actual |
| **Bias and fairness report** | CTO, Quality Manager, HR Director | Quarterly | Performance disparity by segment for people-affecting models, with assessment and action |
| Decision log audit extract | Auditor, GRC, Legal | On demand | Complete, immutable decision records for a period, model or subject |
| Generative service report | CTO, M32 owner, M61 owner | Weekly | Retrieval quality, refusal rate and reasons, citation coverage, corpus freshness |
| AI risk register | CTO, GRC, Quality Manager | Quarterly | Risks by model, likelihood, impact, treatment, control, review status |
| Benefit attribution | CFO, CTO | Quarterly | Measured contribution of each model to its benefit line, against the case |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| **KPI-013** | Automatic dispatch assignment rate | 0% | 40% | **> 70%** |
| — | Dispatcher agreement with recommendation | n/a | 85% | **> 90%** |
| — | **Models with a current model card** | n/a | **100%** | **100%** |
| — | **Model-influenced decisions logged** | n/a | **100%** | **100%** |
| — | **Incidents caused by unavailable models** | n/a | **0** | **0** |
| — | Consumers with a tested fallback | n/a | **100%** | **100%** |
| — | People-affecting models with current bias testing | n/a | **100%** | **100%** |
| — | Models promoted without meeting their stated target | n/a | **0** | **0** |
| — | Models deployed without a named consumer, target and fallback | n/a | **0** | **0** |
| — | Predictions served without an explanation | n/a | **0** | **0** |
| — | Repair duration prediction MAE | unmeasured | < 25% | **< 20%** |
| — | Travel time prediction MAE | unmeasured | < 20% | **< 15%** |
| — | Parts demand forecast MAPE | unmeasured | < 28% | **< 22%** |
| — | Service demand forecast MAPE | unmeasured | < 24% | **< 18%** |
| — | Fault classification top-3 accuracy | unmeasured | > 75% | **> 80%** |
| — | Bengali intent accuracy | unmeasured | > 85% | **> 88%** |
| — | Document extraction field accuracy | unmeasured | > 88% | **> 92%** |
| — | Predictive failure precision | n/a | — | **> 70%** |
| — | Win probability AUC | n/a | — | **> 0.75** |
| **KPI-023** | Churn risk AUC *(contributing to churn < 8%)* | n/a | — | **> 0.72** |
| — | Fraud detection recall at 5% FPR | n/a | > 70% | **> 80%** |
| — | Trade-in valuation within 10% of assessed | n/a | 65% | **75%** |
| — | Generative answers served without citations | n/a | **0** | **0** |
| — | Online inference p95 latency | n/a | < 500 ms | **< 300 ms** |

**Nine of these targets are zero or one hundred per cent.** Cards, logging, explanations,
fallbacks, bias tests and promotion gates are controls. The accuracy targets are performance;
the controls are not.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L3 | Inference gateway, model services, batch scoring, guard-rail enforcement | 24% |
| L4 | MLflow registry, Ollama inference, vector index, GPU compute, OCR engine | 18% |
| L5 | `cd_ml_gateway`, `cd_dispatch_ml`, `cd_forecast`, `cd_predictive`, `cd_pricing_ml`, `cd_llm_bridge`, `cd_model_governance`, `cd_model_monitoring` | 58% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort | Wave |
|---|---|---|---|:--:|
| **CD-113** | `cd_ml_gateway` — single inference entry point, authentication, timeout, **fallback contract**, guard-rail enforcement, confidence and abstention, decision logging, explanation generation | Python / FastAPI service | 5 PW | W6 |
| **CD-114** | `cd_dispatch_ml` — assignment scoring, duration prediction, travel prediction, override capture and feedback | Service + model pipelines | 4 PW | W6 |
| **CD-115** | `cd_forecast` — parts demand, service demand, batch scoring, accuracy measurement *(consumed by M43; not counted in M43's effort)* | Service + model pipelines | 5 PW | W6 |
| **CD-116** | `cd_predictive` — predictive failure, quality risk, fraud and anomaly detection | Service + model pipelines | 4 PW | W8 |
| **CD-117** | `cd_pricing_ml` — win probability, elasticity, trade-in valuation, with pricing guard rails | Service + model pipelines | 4 PW | W8 |
| **CD-118** | `cd_llm_bridge` — self-hosted generative inference, retrieval-augmented grounding, entitlement-filtered retrieval, citation, refusal, generative guard rails, AI labelling | Service | 5 PW | W6 / W8 |
| **CD-194** | `cd_model_governance` — portfolio register, model cards, bias testing, AI risk register, data-sufficiency gates, promotion and demotion workflow, fallback test register | Odoo module + service | 4 PW | W6 |
| **CD-195** | `cd_model_monitoring` — drift detection (PSI, KS, attribution), performance tracking, retraining triggers, automated demotion, override-rate analysis | Service | 3 PW | W6 |
| | **Total** | | **34 PW** | |

> **CD allocation.** CD-113…118 are retained from `02-05` §5.2. **CD-194…195 are claimed from
> the Category J extension block** (CD-187 onward, following Category G's block ending at
> CD-186). Raised as an audit action against `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M62 Data Platform (W4, feature store W4 core / W8 scale)** | **Hard dependency.** Training features, serving features and point-in-time correctness. No feature store, no models |
| M29 Identity & Security (W1) | Gateway authentication and retrieval entitlement |
| M28 Integration Platform (W1) | Event transport and gateway exposure |
| M30 Platform Administration (W1) | GPU and inference infrastructure |
| **12 months of M02 data** | Dispatch scoring, duration and travel models — available W6 |
| **18–24 months of M15 data** | Parts demand forecast — available W6–W8 |
| **M48 live (W8)** | Predictive failure requires telemetry plus failure events |
| **M36 data from W3** | Price elasticity usable by W7 |
| **M34 data from W4** | Churn requires the full lifecycle including satisfaction — W8 |
| M61 Knowledge Management (W6) | Generative grounding corpus |
| M32 Conversational AI (W4) | Bengali NLP consumer — the one capability that can land early on pre-trained models |

**Wave split.** W6 delivers the gateway, governance, monitoring, dispatch models, forecasting
and Bengali NLP. W8 delivers predictive failure, pricing, trade-in valuation, fraud detection
and generative at scale. **The governance layer (CD-194, CD-195) lands in W6 with the first
model, not after the last one** — governance retrofitted onto a running model estate is
governance nobody trusts.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Historical operational data accumulated since W1 | 12–24 months per model per overview §8 | Training datasets via M62 feature store | W6 / W8 |
| Existing heuristics and rules (dispatch practice, standard times, depreciation tables) | All in use | **Encoded as the declared fallbacks**, not discarded | W6 |
| **Recovered customer data (M06)** | — | **Never. Structurally excluded (BRU-AIM-03)** | — |

**Migration note.** The most important artefact carried into this module is not data — it is
the **existing human heuristic**. Every fallback in §5.3–§5.6 is somebody's current method,
written down. Capturing those before building the model has two benefits: the fallback is real
on day one, and the model has a baseline it must actually beat.

### 16.5 Register Variance

| Figure | Reference | Measured | Note |
|---|---|---:|---|
| Requirements | `05-01` allocation **38** · `02-02` est. **38** | **42** | Four IDs claimed from the reserved growth block **039–055**. The additions are governance requirements (model cards, bias testing, decision logging, explainability) that the v1.0 allocation predated |
| Effort | `02-02` est. **30 PW** | **34 PW** | +13%, concentrated in `cd_model_governance` (4 PW) and `cd_model_monitoring` (3 PW) — neither existed in the v1.0 scope |

Both require `02-02` §2 Category J and `05-01` §1.3 to be updated. Raised as an audit action.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **A model without a named consumer, an accuracy target and a defined fallback cannot be deployed** | Negative test at the registry |
| AC-02 | A model cannot be promoted where its data-sufficiency prerequisite is unmet | Negative test |
| AC-03 | A model cannot be promoted without meeting its stated target on a held-out set | Negative test |
| AC-04 | A people-affecting model cannot be promoted without documented bias testing | Negative test |
| AC-05 | **A model cannot be promoted without a complete, current model card** | Negative test |
| AC-06 | **Model unavailability never blocks a business process** — with every model disabled, all seventeen consuming modules operate on their fallbacks | **Full fallback exercise across the estate** |
| AC-07 | A fallback response is marked as a fallback and recorded as such by the consumer | Integration test |
| AC-08 | **Every prediction is logged with inputs, output, confidence, model version, explanation and override status; a prediction cannot be served if logging fails** | Fault-injection test |
| AC-09 | **Every material prediction carries a plain-language explanation in Bengali and English** | Sample review across all model classes |
| AC-10 | A model output that would cross a guard rail is clamped or rejected, and the intervention is logged with both values | Boundary test per rail type |
| AC-11 | **A decision with material customer or financial impact cannot complete without human confirmation** | Negative test in the consuming module |
| AC-12 | A human override is captured with a reason and appears in the next training cycle | End-to-end test |
| AC-13 | **M26 cannot write to any operational record** | Negative test at the connection layer |
| AC-14 | No consuming module can reach a model except through the gateway | Network and code audit |
| AC-15 | Production performance breach triggers automatic demotion and restores the prior champion without human initiation | Injected-degradation test |
| AC-16 | Drift detection computes PSI and KS per feature, and retraining triggers only on PSI breach coinciding with an evaluation drop | Scripted drift scenario, both single-signal and combined |
| AC-17 | A training-serving skew alert from M62 blocks promotion | Negative test |
| AC-18 | Training features are retrieved point-in-time correct; a training set cannot be built by direct warehouse query | Code audit and negative test |
| AC-19 | A training run can be reproduced exactly from its recorded snapshot | Reproducibility test |
| AC-20 | **M26 has no credential, network path or data grant to the M06 environment** | Security review and negative test |
| AC-21 | **Generative inference runs on Company infrastructure; no request containing customer data reaches an external provider** | Network egress test |
| AC-22 | Every generative answer carries citations, and an answer is refused where retrieved evidence is insufficient | Grounding test with a deliberately unanswerable query |
| AC-23 | Retrieval applies the asker's entitlements — a generated answer cannot surface content the asker could not open | Negative test across four role types |
| AC-24 | Instructions embedded in retrieved content or user input are not executed | Prompt-injection test suite |
| AC-25 | Generative output cannot trigger any action in any operational system | Negative test |
| AC-26 | Customer-facing AI-generated content is labelled as such | Conformance review |
| AC-27 | A decision subject can obtain the explanation for a decision about them | Access test |
| AC-28 | CTO, Quality Manager and Operations Director sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 28 criteria above.

**AC-06 is the module's defining test.** If the Company cannot run with every model switched
off, the models are not decision support — they are an undeclared dependency.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Does the Company have, or intend to hire, data science capability?** `05-04` contains no data scientist or ML engineer role. Fourteen models cannot be built, monitored and governed without one | CTO / HR Director | **W6 minus 6 months** |
| Q-02 | **What GPU capacity is approved for self-hosted generative inference?** BRU-AIM-10 makes self-hosting non-negotiable, which makes this a hardware decision, not a preference | CTO / CFO | **W6 minus 4 months** |
| Q-03 | **Will the dispatch model influence technician incentives or appraisal?** If yes, it is a people-affecting model of the highest sensitivity and HR, the workforce and possibly legal review must be involved before W6 | HR Director / Operations Director | **W6 minus 3 months** |
| Q-04 | Which segments are tested for bias — branch, zone, tenure, gender, employment type? The segments must be agreed before the first test, not chosen after seeing results | HR Director / CTO / Quality Manager | W6 build |
| Q-05 | What does **PDPA 2026** require regarding automated decision-making affecting individuals — notice, explanation, objection, human review? This module implements all four voluntarily; the legal minimum should be confirmed | Legal / CDO | **W6 minus 3 months** |
| Q-06 | What is the override-rate tolerance per model, and what happens when it is exceeded — retrain, demote, or withdraw? | Model owners / CTO | W6 build |
| Q-07 | Which decisions count as "material customer or financial impact" under BRU-AIM-01? The rule is only enforceable once the threshold is defined per consuming module | CTO / category owners | **W6 build** |
| Q-08 | Does the Company intend to pursue **ISO/IEC 42001**? The design supports it; the commitment is a business decision with a real cost | CEO / Quality Manager | W8 |
| Q-09 | Which pre-trained Bengali models are licensed for commercial use, and does fine-tuning on Company data create any licence obligation? | CTO / Legal | **W4** (M32 dependency) |
| Q-10 | Is 12 months of M02 data actually sufficient for dispatch scoring given branch heterogeneity, or is the prerequisite larger than overview §8 assumes? | Data Squad | W6 minus 2 months |
| Q-11 | Who is the model owner for each of the fourteen models? The register requires a named person from the consuming function, not from the Data Squad | Category owners | W6 build |
| Q-12 | What is the decision-log retention period per risk class, and does it conflict with PDPA erasure obligations for personal inputs? | CDO / Legal | W6 build |
| Q-13 | If the Company later sells software or services into the EU, do the AI Act's high-risk obligations attach to the dispatch model? The design anticipates it; the commercial intent is unknown | CEO / Legal | W8 |

**Q-01, Q-02, Q-03 and Q-05 are not design questions.** They are capability, capital, industrial-
relations and legal questions that determine whether this module can be delivered as specified.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` (Category J **§6 the model portfolio**, **§7 the ten AI governance rules**,
§5 boundary map, §8 why AI comes late, §9 KPIs, §11 risks) ·
`M62_Data_Platform_Warehouse_and_Governance.md` (**the feature store — hard dependency**) ·
`M25_Business_Intelligence_and_Reporting.md` (prediction display) ·
`M63_Process_Automation_and_Workflow_Orchestration.md` (human confirmation routing) ·
`03_Modules/A_Service_Delivery_and_Operations/M06_Data_Services_and_Secure_Data_Handling.md`
§9 BRU-DTS-14 *(the reciprocal training-data prohibition)* ·
`03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md`
*(the largest model consumer)* ·
`03_Modules/E_Supply_Chain_and_Inventory/M43_Demand_Planning_and_Replenishment.md`
*(consumes CD-115 `cd_forecast`)* ·
`03_Modules/F_Asset_Equipment_and_Facilities/M48_IoT_Telemetry_and_Predictive_Maintenance.md`
*(M26 builds, M48 applies)* ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` (MLflow, Ollama, ML inference gateway) ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` (BO-02, KPI-013, KPI-023)

**Workspace evidence**
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §Benefit Register
(technician productivity BDT 130 lac · inventory BDT 34 lac · dynamic pricing BDT 40 lac)

**External benchmark**
**MLflow** — experiment tracking and a model registry as the single source of truth, with
production metrics, drift outputs and explainability traces mapped to registry state; automated
demotion as well as promotion ·
**MLOps deployment practice** — gated offline validation, shadow deployment, canary rollout,
champion–challenger with automated rollback ·
**Drift detection practice** — PSI and Kolmogorov–Smirnov tests, SHAP-based feature monitoring,
the PSI > 0.2 plus evaluation-drop retraining trigger, daily checks for revenue-critical models ·
**ISO/IEC 42001:2023** — the first certifiable AI management system standard; Plan-Do-Check-Act
on Annex SL, lifecycle AI risk and impact assessment, model cards, audit logs, decision records,
and written justification of included and excluded controls; integrates with existing ISO 9001 ·
**EU AI Act** — high-risk obligations (risk management, data governance, technical documentation,
automatic logging, human oversight, accuracy and robustness); Article 50 transparency requiring
AI-generated content to be machine-detectable from 2 August 2026; employment-related high-risk
obligations deferred to 2 December 2027 under the AI Omnibus agreement. **Adopted as a design
template; not jurisdictionally binding on a Bangladeshi company** ·
**NIST AI Risk Management Framework** — Govern, Map, Measure, Manage ·
**Model card practice** — purpose, data, intended and out-of-scope use, performance by segment,
limitations, owner, review date ·
**Retrieval-augmented generation practice (2026)** — grounding in verifiable evidence, hybrid and
corrective retrieval, governance and access control at retrieval; 40–60% of RAG implementations
fail before production, chiefly on retrieval quality and governance gaps ·
**Self-hosted inference (Ollama)** — local serving with no external data egress ·
**Prompt-injection defence practice** — retrieved content and user input treated as untrusted data,
never as instructions

**Sources consulted**
- [MLflow — automating AI model registry updates](https://mlflow.org/articles/automating-ai-model-registry-updates/)
- [Model drift vs data drift — detection and mitigation (2026)](https://futureagi.com/blog/model-vs-data-drift-how-to-identify-and-handle-it/)
- [Model drift detection tutorial — monitoring ML models in production (2026)](https://mlopslab.org/model-drift-detection-tutorial-how-to-monitor-ml-models-in-production-2026/)
- [Deployment and evaluation strategies in MLOps](https://medium.com/@fraidoonomarzai99/deployment-evaluation-strategies-in-mlops-c208585aa3bd)
- [ISO/IEC 42001:2023 — AI management systems](https://www.iso.org/standard/42001)
- [ISO 42001 — a complete guide to AI management systems (2026)](https://www.openlayer.com/blog/iso-42001-ai-management-systems-guide)
- [Integrating ISO 42001 with ISO 27001 and ISO 9001](https://www.isms.online/frameworks/iso-42001/integration-of-iso-42001-into-existing-isms-qms/)
- [EU AI Act — obligations for high-risk AI systems](https://www.aoshearman.com/en/insights/ao-shearman-on-tech/zooming-in-on-ai-10-eu-ai-act-what-are-the-obligations-for-high-risk-ai-systems)
- [EU AI Act — Article 50 transparency rules](https://artificialintelligenceact.eu/transparency-rules-article-50/)
- [Digital AI Omnibus — proposed deferral of high-risk AI obligations](https://knowledge.dlapiper.com/dlapiperknowledge/globalemploymentlatestdevelopments/2026/The-Digital-AI-Omnibus-Proposed-deferral-of-high-risk-AI-obligations-under-the-AI-Act)
- [Retrieval-augmented generation in 2026 — enterprise RAG](https://ecanarys.com/retrieval-augmented-generation-in-2026)
- [The 2026 RAG performance landscape](https://www.flotorch.ai/blogs/the-2026-rag-performance-landscape-what-every-enterprise-leader-needs-to-know)

---

*Module M26 · Category J · 1000FiX ERP System v2.0 · CONFIDENTIAL*
