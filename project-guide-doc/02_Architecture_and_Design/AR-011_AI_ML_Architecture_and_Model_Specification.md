---
id: AR-011
title: AI/ML Architecture & Model Specification
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: Chief Technology Officer
standards_basis: >
  ISO/IEC 23894:2023 (AI risk management) · ISO/IEC 42001:2023 (AI management systems) ·
  Model Cards (Mitchell et al.) · MLOps maturity practice · ISO/IEC/IEEE 42010:2022
traces_to: >
  PGD-000 AR-011 · M26 AIM · M32 CAI · M48 IOT · ADR-029 (self-hosted LLM) ·
  AR-001 LB-06 · risk TR-17 · NFR-099 (PDPA transfer restriction) · audit HC (critical)
depends_on: AR-001 · AR-008 · DA-007 (analytical model) · SC-003 (DPIA)
verified_on: 2026-08-18
priority: P1
needed_by: W5
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-011 — AI/ML Architecture & Model Specification

### Category 02 · Code `AR` · ISO/IEC 23894:2023 · ISO/IEC 42001:2023 · Model Cards

---

## 1. Purpose

Four capabilities in the programme depend on machine learning: **M26** (dispatch scoring, forecasting,
predictive maintenance, pricing), **M32** (Bengali conversational assistant), **M48** (IoT anomaly and
asset health) and the dispatch scoring service (CD-235). `02-05` §7 commits to **self-hosted LLM
inference for Bengali customer conversations with no evaluation criteria**, and no model in the
programme has a specification, an owner, a fallback contract or a drift definition.

This document establishes the ML architecture: the model inventory, the training/serving split, the
**fallback contract that keeps ML off the critical path**, drift monitoring, human override, and the
governance that makes an automated decision defensible when a customer or a regulator asks why it was
made.

**Written now rather than at Wave 5** because two of its constraints bind Wave 1: models must not be
trained on personal data without a lawful basis (`SC-003`), and **audit finding `HC` (critical)
records that customer-transcript mining is scheduled at W2 with no confirmed legal basis.**

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | Model inventory — what is a model, and what is a rule pretending to be one |
| 2 | The training/serving split and the inference topology |
| 3 | **The fallback contract** — `ML-01`, and why no business path may depend on model availability |
| 4 | Feature management and the training-serving skew problem |
| 5 | Drift detection, thresholds and response |
| 6 | Human override, explainability and the decision log |
| 7 | Model lifecycle — proposal, evaluation, promotion, monitoring, retirement |
| 8 | **LLM-specific architecture** — self-hosting, prompt handling, grounding, evaluation |
| 9 | Data protection: lawful basis, residency, minimisation, and the transcript-mining problem |
| 10 | Model cards and the governance record |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Warehouse and dimensional model | `DA-007`, M62 | Features are derived from it |
| The DPIA itself | `SC-003` | This document states the ML-specific inputs |
| Per-model algorithm design | `AR-003` M26/M32/M48 SDDs | Architecture vs design |
| GPU sizing and inference infrastructure | `PE-006` | This document states the driver |
| Conversational content, intents, tone | M32, `UI-*` content | |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| AI/ML engineer (joins W6) | The architecture they build into |
| Solution Architect | §4's fallback contract is a design obligation on every consuming module, from Wave 2 |
| DPO | §10 is a direct input to `SC-003` |
| CTO | §9's LLM position and its cost/quality assumption |
| Service Ops Director | §7 human override — dispatchers must be able to disagree with the model |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **ISO/IEC 23894:2023** — AI risk management | §6 drift, §7 override, §11 risk register alignment | Full AI risk assessment is `SC-003`/`GV-005`'s; this document supplies the technical risks |
| **ISO/IEC 42001:2023** — AI management systems | §8 lifecycle, §10 model cards, §7 accountability | **Departure:** no full AIMS is established. The programme has four ML capabilities, not an AI portfolio. Certification is not sought. Stated rather than implied |
| **Model Cards** (Mitchell et al., 2019) | §10 — mandatory per model | Adopted in full |
| MLOps practice | §3 training/serving split; MLflow registry | |
| ISO/IEC/IEEE 42010:2022 | Inherits `AR-001` viewpoints at ML scope | |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `../../1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M26_AIML_Services_and_Model_Operations.md` | 11 entities including `fix.ml.model`, `fix.ml.prediction.log`, `fix.ml.override`, `fix.ml.drift.metric`, `fix.model.card` |
| `../../1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32_Conversational_AI_and_Virtual_Assistant.md` | Intent scope; the M61 knowledge dependency (`Q-01`) |
| `../../1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M48_IoT_Telemetry_and_Predictive_Maintenance.md` | Telemetry-driven prediction |
| `../../primary-doc/…Technology_Stack_Specification.md` §23 `TR-17`, §24 TD-06, §25.4 `A-04` | The fallback rule, the self-hosting decision, the Bengali-quality assumption |
| `.../02-05_*.md` §7 #15 | *"Build on self-hosted LLM"* — the commitment with no evaluation criteria |
| `.../05-06_*.md` §6.3 NFR-099 | The transfer restriction that makes self-hosting a legal position |
| `AUDIT-*` finding `HC` (critical) | Customer-transcript mining at W2 with no confirmed legal basis |

### 2.3 Audit findings addressed

| Finding | How |
|---|---|
| `PGD-000` `AR-011` — *"`02-05` commits to self-hosted LLM inference with no evaluation criteria"* | §9.4 defines the evaluation gate and the consequence of failing it |
| **`HC` (critical)** — transcript mining at W2, no confirmed legal basis | §10.2 — **blocked pending `SC-003`**; a technical control is specified so the block is enforceable rather than advisory |
| `TR-17` ML model failure blocks a business path | §4 `ML-01` fallback contract, exercised in the DR drill |
| `AR-001` LB-06 — analytics writes advisory records only | §7.3 |

---

## 3. Model Inventory

### 3.1 What counts as a model

> **A model is a function whose behaviour is learned from data rather than specified.** A weighted
> scoring rule with hand-set weights is **not** a model — it is a rule, and it belongs in the pricing
> or dispatch service under normal change control.

This distinction matters because a rule dressed as a model acquires unnecessary governance, and a
model dressed as a rule escapes necessary governance.

### 3.2 The inventory

| ID | Model | Consumer | Kind | Wave | Fallback | Decision class |
|---|---|---|---|:--:|---|---|
| **ML-01** | **Dispatch assignment scoring** | M02 via CD-235 | Ranking | W6 | **Deterministic rule-based scoring** (skill, certification, van stock, zone, distance) | Advisory — dispatcher assigns |
| **ML-02** | Job duration prediction | M02 | Regression | W6 | Historical median by fault code × device category | Advisory |
| **ML-03** | Parts demand forecasting | M43, M15 | Time series | W6 | Moving average with a safety factor | Advisory — M43 sets parameters |
| **ML-04** | Predictive maintenance / asset health | M48, M17, M05 | Classification | W8 | Threshold rules on telemetry | Advisory |
| **ML-05** | Dynamic pricing recommendation | M11 | Regression + guard rails | W7 | Static rate card | Advisory — **guard rails are rules, not model output** |
| **ML-06** | Churn / customer health | M07, M34 | Classification | W8 | Recency-frequency-monetary segmentation | Advisory |
| **ML-07** | Quality-risk / rework prediction | M23, M01 | Classification | W8 | Rework rate by technician × fault code | Advisory |
| **ML-08** | **Bengali conversational assistant** | M32, M27 | LLM (open-weight, self-hosted) | W6 | **Rule-based responses; direct human routing** | Advisory — **never resolves a case autonomously** |
| **ML-09** | Document extraction (OCR post-processing) | CD-240, M24, M16 | Sequence labelling | W3 | Manual data entry | Advisory |
| **ML-10** | Bengali speech-to-text | CD-246, M27 | ASR | W8 | Manual note-taking | Advisory |

**All ten are advisory.** No model in the programme makes an autonomous decision with a financial,
contractual or safety consequence. That is a deliberate architectural position (§7.3), not an interim
state.

---

## 4. The Fallback Contract — `ML-01`

> **`ML-01`: every model has a deterministic fallback, and no business path depends on model
> availability.** Every fallback is exercised in the twice-yearly DR drill (NFR-051).

### 4.1 Why this is an architecture rule and not an operations one

A model is the least reliable component in the estate: it depends on a training pipeline, a feature
store, a serving process, GPU capacity and data quality, any of which can degrade without an outage.
If dispatch cannot assign a technician when the scoring model is unavailable, then **a model-quality
problem becomes a business-stopping incident**, and the business stops for a reason nobody on the
incident bridge can diagnose quickly.

### 4.2 The contract

| # | Rule |
|---|---|
| **FB-01** | Every model has a **named, implemented, tested deterministic fallback** — not "fall back to manual" |
| **FB-02** | The fallback is **built first**, before the model. `AR-006` sequencing: rule-based dispatch scoring ships in W2; ML-01 augments it in W6 |
| **FB-03** | Fallback activation is a **feature-flag state (CD-135)**, operable without a deployment (OPS-06) |
| **FB-04** | Fallback activation is **automatic** on inference timeout, error rate, or a drift breach (§6.3) |
| **FB-05** | Fallback activation is **visible** — to the operator in the console, and where relevant to the user |
| **FB-06** | Every fallback is exercised in the **DR drill** (`TR-17`) |
| **FB-07** | A model whose fallback has never been exercised **may not be promoted to production** |

### 4.3 The consequence for the ML gateway

**All inference passes through a single ML inference gateway (CD-245).** The gateway — not each
consumer — owns timeout, circuit breaking, fallback selection, prediction logging and metrics.

| Property | Value |
|---|---|
| Inference timeout | Per model, defaulting to **200 ms** for synchronous paths |
| Circuit breaker | Opens on error rate or latency breach; closes on a probe |
| On open | Return the fallback result, **flagged as a fallback** |
| Logging | Every prediction to `fix.ml.prediction.log` — inputs, output, model version, latency, fallback flag |
| Batch inference | Separate path; no timeout constraint |

---

## 5. Training and Serving

### 5.1 The split

```
  TRAINING (offline, W6+)                    SERVING (online)
  ┌──────────────────────────┐               ┌──────────────────────────┐
  │ ClickHouse warehouse     │               │ ML gateway (CD-245)      │
  │  + feature definitions   │               │  timeout · breaker ·     │
  │  (fix.ml.feature)        │──── model ───►│  fallback · logging      │
  │                          │    artefact   │                          │
  │ MLflow — experiments,    │               │ Model runtime            │
  │ versions, lineage        │               │ (CPU default; GPU only   │
  │                          │               │  where latency requires) │
  │ Ollama — LLM weights     │               │ Ollama — LLM inference   │
  └──────────────────────────┘               └──────────────────────────┘
         ▲                                              │
         │ features computed from the SAME definitions ─┘  (§5.2)
```

| Aspect | Position |
|---|---|
| Training data source | **The warehouse (M62/ClickHouse), never the OLTP primary.** Training queries must not touch production transaction load |
| Registry | **MLflow** — versions, experiments, lineage, artefacts (ADR-016 family, TD-16 era decisions) |
| Serving | CD-245 gateway; CPU by default. **GPU only where latency requires it**, which for the LLM it does |
| Retraining | Scheduled per model; a retrain is a **promotion candidate**, never an automatic replacement |
| Promotion | §8 — evaluation gate, shadow period, then promotion |

### 5.2 Feature management and training-serving skew

> **Training-serving skew is the defect that produces a model that scores well offline and badly in
> production, and it is invisible in every offline metric.**

| # | Rule |
|---|---|
| **FT-01** | A feature is **defined once** in `fix.ml.feature` and computed from that single definition in both training and serving |
| **FT-02** | Serving features are computed from the **same logical source** as training features |
| **FT-03** | A feature that cannot be computed at serving time within the latency budget **may not be used in training** |
| **FT-04** | **Point-in-time correctness:** a training example uses only feature values that were knowable at the prediction moment. Leakage of future information is the most common cause of an over-performing offline model |
| **FT-05** | Feature definitions are **versioned**; a feature change is a model-retraining trigger |
| **FT-06** | **No feature is derived from a residency-classified value** (`AR-001` LB-08). Where a signal is needed from such data, a derived non-identifying attribute is computed inside CD-233 and only that crosses the boundary |

> **FT-06 has a real modelling consequence and must be designed for.** A feature such as
> "customer district" is fine; "customer NID prefix" is not, even though it may be predictive. The
> residency boundary constrains the feature space, and the ML engineer must know that before building
> a pipeline, not after.

---

## 6. Drift

### 6.1 Three kinds, three responses

| Kind | Definition | Detection | Response |
|---|---|---|---|
| **Data drift** | Input distribution moves | Population stability index per feature, weekly | Investigate; retrain if sustained |
| **Concept drift** | The input→output relationship changes | Rolling performance against labelled outcomes | Retrain; if performance stays below threshold, **fall back** |
| **Performance decay** | Accuracy falls without an obvious distribution change | Rolling metric vs the promotion baseline | As concept drift |

### 6.2 Metrics per model

Every model declares, in its model card, at least: a **primary metric with a promotion threshold**, a
**degradation threshold** that triggers investigation, and a **fallback threshold** that triggers
automatic fallback.

| Model | Primary metric | Promotion | Degradation | **Fallback** |
|---|---|---|---|---|
| ML-01 dispatch | Dispatcher agreement rate | ≥ 88% *(W6 gate)* | < 85% | < 75% |
| ML-02 duration | MAE vs actual | Per gate | +25% | +50% |
| ML-03 forecast | Forecast accuracy | Per gate | −10 pp | −20 pp |
| ML-04 predictive | Precision on the pilot estate | ≥ 70% *(W8 gate)* | < 65% | < 55% |
| ML-08 assistant | Containment rate + human-rated correctness | ≥ 40% first-contact resolution *(W4 gate)* | < 35% | < 25% **or any safety breach** |

> **ML-08's fallback trigger includes "any safety breach" with no numeric threshold**, because a
> single confidently wrong answer about a data-recovery case or a warranty entitlement is a different
> class of failure from a 5% accuracy drop.

### 6.3 Drift response

| # | Rule |
|---|---|
| **DR-01** | Drift metrics are computed on a schedule and written to `fix.ml.drift.metric` |
| **DR-02** | Crossing the **degradation** threshold raises a task for the model owner |
| **DR-03** | Crossing the **fallback** threshold triggers automatic fallback (FB-04) and an alert |
| **DR-04** | Fallback is **not** automatically reverted. Restoration requires a promotion decision |
| **DR-05** | A model with no labelled outcome stream **cannot** have concept drift detected — its card must say so explicitly, and it carries a shorter review cycle |

---

## 7. Human Override and Explainability

### 7.1 Override

| # | Rule |
|---|---|
| **HO-01** | **Every model output can be overridden by an authorised human.** No exception |
| **HO-02** | Every override is recorded in `fix.ml.override` with actor, timestamp, model version, original output, chosen output and **reason** |
| **HO-03** | **Override rate is a monitored model-quality signal.** A dispatcher overriding 40% of assignments is telling you the model is wrong |
| **HO-04** | An override is **never** presented as an error by the user. It is a legitimate use of the system |
| **HO-05** | Overrides are a **training input**, subject to the same lawful-basis rules as any other data |

### 7.2 Explainability

| Consumer of the explanation | Requirement |
|---|---|
| **Operator** (dispatcher, planner) | The **top contributing factors**, in plain Bengali or English. *"Nearest qualified technician with the part in van stock"* — not a SHAP plot |
| **Affected person** (customer, technician) | Where a model output materially affects them, the **existence** of automated input is disclosed, and a human is reachable |
| **Auditor / regulator** | Model card, version, inputs, output and decision log for the specific decision — reconstructible from `fix.ml.prediction.log` |

### 7.3 The advisory-write rule

> **`AR-001` LB-06 — Category J is read-only with respect to transactional aggregates.** An ML output
> is written as an **advisory record** (`fix.ml.prediction.log`, `fix.failure.prediction`), **never as
> a state mutation.**

Concretely: the dispatch model does not set `work_order.technician_id`. It writes a scored candidate
list; **M02 assigns**, applying its own rules and its own audit trail. This is what keeps the
system's behaviour explainable after a model is retired, and it is checked by `AR-012` `FF-07`.

---

## 8. Model Lifecycle

| Stage | Gate |
|---|---|
| **1. Proposal** | A named business problem, a fallback that already works, a labelled-outcome source, and a lawful basis for the training data (§10) |
| **2. Data assessment** | Availability, quality, bias, point-in-time correctness, residency constraints (FT-06) |
| **3. Development** | Experiments tracked in MLflow; features from `fix.ml.feature` only |
| **4. Evaluation** | Offline metric vs promotion threshold; **fairness assessment where the model affects people**; latency within the serving budget |
| **5. Shadow** | Runs in production **without affecting decisions**; predictions logged and compared to human outcomes. Minimum one full business cycle |
| **6. Promotion** | Model owner + business owner sign the model card. **The fallback must have been exercised (FB-07)** |
| **7. Monitoring** | Drift, override rate, latency, fallback activations |
| **8. Retirement** | Fallback becomes primary; the card is archived, never deleted; the prediction log is retained per §10.4 |

> **Stage 5 is the one most likely to be cut under schedule pressure, and it is the one that catches
> training-serving skew.** A model that has not run in shadow has never been evaluated on production
> data.

---

## 9. LLM Architecture

### 9.1 Position (ADR-029)

**Self-hosted open-weight inference via Ollama.** Hosted LLM APIs are rejected on a legal ground, not
a cost one: they **send customer personal data offshore, breaching PDPA transfer restrictions**
(NFR-099). No commercial term makes that acceptable.

### 9.2 Topology

| Component | Role |
|---|---|
| Ollama | Model serving, in Z2 |
| CD-245 ML gateway | Single entry point; timeout, breaker, fallback, logging |
| CD-118 `cd_llm_bridge` / CD-122 `cd_assistant` | Odoo-side integration |
| M61 knowledge base | **Grounding source** for retrieval |
| `fix.llm.session`, `fix.llm.citation` | Session and provenance records |

### 9.3 Grounding and safety rules

| # | Rule |
|---|---|
| **LLM-01** | **Retrieval-grounded, not free-generating.** Answers are grounded in M61 knowledge, live ERP data or approved templates, and **cite their source** (`fix.llm.citation`) |
| **LLM-02** | **No autonomous action.** The assistant may draft, suggest and retrieve. It may not create an order, take a payment, approve an estimate or change a state |
| **LLM-03** | **No residency-classified value enters a prompt.** Checked at the gateway (`FF-09` extension) |
| **LLM-04** | Prompts and completions are logged with the session, subject to §10 retention and erasure |
| **LLM-05** | **Handoff to a human is always available and always visible** (`cd_ai_handoff`) |
| **LLM-06** | Refusal and escalation behaviour is specified for out-of-scope, ambiguous and distressed-user cases |
| **LLM-07** | Adversarial input (prompt injection through customer-supplied text) is treated as untrusted. **Retrieved content is data, never instruction** |

> **LLM-07 is the LLM-specific security control and it is easy to omit.** A customer's fault
> description is user input; if it is concatenated into a prompt that also carries system
> instructions, a crafted description can redirect the assistant. `SC-002` must include prompt
> injection as an abuse case.

### 9.4 The evaluation gate `02-05` never defined

`02-05` §7 #15 commits to a self-hosted LLM. Assumption `A-04` states the risk plainly: *"Open-weight
LLMs deliver adequate Bengali quality for the assistant's intent scope. If wrong, the assistant's
scope narrows to templated and transactional responses and the fallback becomes the primary path."*

**The gate, defined here:**

| # | Criterion | Threshold |
|---|---|---|
| **EV-01** | Bengali comprehension on a held-out set of **≥ 500 real, consented customer enquiries** across the declared intent scope | ≥ 90% correct intent identification |
| **EV-02** | Bengali generation quality, rated by **native-speaker reviewers** against a rubric | ≥ 4.0 / 5.0 mean |
| **EV-03** | **Groundedness** — every factual claim traceable to a cited source | ≥ 98% (a hallucinated warranty term is a commercial exposure) |
| **EV-04** | Refusal correctness on out-of-scope and adversarial inputs | ≥ 95% |
| **EV-05** | Latency at p95 within the conversational budget | ≤ 3 s to first token |
| **EV-06** | Inference cost per conversation at projected volume | Within the `PE-006` envelope |

**Failing EV-01, EV-02 or EV-03 narrows M32's scope to transactional intents** — the ADR-029 negative
consequence, made a decision rather than a discovery. This is also the second half of open question
`Q-01` (M32 launching before its knowledge base M61, two waves later).

---

## 10. Data Protection

### 10.1 Lawful basis — the gate before any training

| # | Rule |
|---|---|
| **DP-01** | **No model is trained on personal data without a recorded lawful basis** for that purpose (NFR-090). Training is a distinct processing purpose from service delivery, and consent for one is not consent for the other |
| **DP-02** | Training data is **minimised** — only features with a stated modelling justification (NFR-097, IP-10) |
| **DP-03** | **No residency-classified value in a training set, a feature store, a prompt or a model artefact** (FT-06, LLM-03) |
| **DP-04** | An erasure request (NFR-093) reaches **training sets, feature stores and prediction logs**. Model weights already trained cannot be unlearned; the mitigation is DP-02 minimisation and a bounded retraining cycle. **This limitation is disclosed in `SC-003`, not hidden** |
| **DP-05** | Model outputs affecting a person are within the DPIA scope |

### 10.2 The transcript-mining problem — `HC` (critical)

> Audit finding **`HC` (critical)** records that **customer-transcript mining is scheduled at Wave 2
> with no confirmed legal basis.**

**Position taken here.**

| # | Statement |
|---|---|
| 1 | Customer conversation transcripts are **personal data**, and may include **sensitive** categories where a customer discusses health, finances or identity documents |
| 2 | Mining them for model training is a **distinct processing purpose** from handling the conversation |
| 3 | **No transcript mining may begin until `SC-003` records a lawful basis for that purpose** and, if consent-based, until the consent mechanism exists in M33 |
| 4 | **The control is technical, not procedural:** the warehouse ETL (CD-243) must not load conversation content into a training-accessible dataset until a purpose flag is set by M33. **A policy statement is not a control** |
| 5 | Call **recordings** are additionally S3-classified (`05-02` §10) and access-logged |

**This is a Wave 1 blocking item for `SC-003`, not a Wave 5 concern**, because the pipeline that would
make the data available is built in Wave 4 (CD-243).

### 10.3 Fairness

| Model | Fairness concern | Assessment required |
|---|---|---|
| ML-01 dispatch | Systematic disadvantage to technicians by zone, shift or tenure — **it affects earnings** | Outcome distribution by protected and quasi-protected attributes, at promotion and quarterly |
| ML-05 pricing | Differential pricing by customer segment | **Guard rails are rules, not model output.** Assessed against a published policy |
| ML-06 churn | Service-level differentiation by predicted value | Reviewed at promotion |
| ML-07 quality risk | Technician-level risk scores affecting assignment or appraisal | **Must not feed M57 performance appraisal without an explicit decision** |

> **ML-01 is the model with the most direct human consequence in the programme.** Dispatch assignment
> determines a technician's job count, which determines their incentive earnings under M57. A scoring
> model that systematically favours some technicians is a pay-equity issue before it is a technical one.

### 10.4 Retention

| Artefact | Retention |
|---|---|
| Training sets | Per purpose; minimised; deleted when the purpose ends |
| Feature store | Rolling window per model |
| `fix.ml.prediction.log` | **2 years** — needed to defend a decision that affected someone |
| `fix.ml.override` | With the prediction log |
| Model cards | **Permanent** — archived on retirement, never deleted |
| LLM sessions | Per conversation retention (M27); subject to erasure |

---

## 11. Model Cards

**Every model in production has a card (`fix.model.card`).** No card, no promotion.

| Section | Content |
|---|---|
| Identity | Name, ID, version, owner (a role), business owner |
| Intended use | The decision it informs, and — explicitly — **what it must not be used for** |
| Inputs | Features, sources, point-in-time rules, residency exclusions |
| Training data | Period, volume, **lawful basis**, known bias, exclusions |
| Performance | Primary metric, promotion threshold, degradation and **fallback** thresholds, evaluation set |
| Fairness | Assessment performed, groups considered, findings |
| **Fallback** | The named deterministic fallback, **and the date it was last exercised** |
| Limitations | Where the model is known to be weak; the failure modes |
| Monitoring | Drift metrics, cadence, alert routing |
| Human oversight | Override mechanism, expected override rate, escalation |
| Lifecycle | Promoted, last retrained, next review, retirement trigger |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Transcript mining lawful basis** (`HC` critical). The CD-243 pipeline is built in W4 | DPO / Legal / `SC-003` | **W1** | Any conversation-derived model; the CD-243 purpose flag |
| Q-02 | Does the Bengali LLM evaluation gate (§9.4) pass? `A-04` is an assumption, not a measurement | CTO / AI-ML Engineer | **W5**, before M32's W6 build | M32 scope; `Q-01` (M32/M61 sequencing) |
| Q-03 | May ML-07 quality-risk scores feed M57 performance appraisal? | HR Director / CTO | W8 | ML-07 intended use; fairness |
| Q-04 | Who owns model governance before the AI/ML engineer joins in W6? | CTO | W1 | §8 lifecycle gates |
| Q-05 | Is GPU capacity funded for LLM inference at projected volume (EV-06)? | CFO / `PE-006` | W5 | ML-08 viability |
| Q-06 | Does an erasure request require model retraining, or is DP-02 minimisation an accepted mitigation? | DPO | W4 | `SC-003` disclosure |

---

## 13. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-A11-01 | Model autonomy | Autonomous for low-risk; **advisory only** | **Advisory only** | Every one of the ten models informs a decision with a financial, contractual or human consequence | Every consumer builds a human decision point |
| D-A11-02 | Fallback | Best-effort; **mandatory, built first, exercised** | **Mandatory (`ML-01`)** | A model-quality problem must not become a business-stopping incident | FB-02 puts rule-based dispatch in W2, before ML in W6 |
| D-A11-03 | Inference entry | Per consumer; **single gateway** | **Single gateway (CD-245)** | Timeout, breaker, fallback and logging cannot be "mostly right" per consumer | No module calls a model directly |
| D-A11-04 | LLM hosting | Hosted API; **self-hosted open-weight** | **Self-hosted (ADR-029)** | NFR-099 transfer restriction. A legal rejection, not a cost one | `A-04` Bengali-quality assumption; §9.4 gate |
| D-A11-05 | LLM generation | Free generation; **retrieval-grounded with citations** | **Grounded** | A hallucinated warranty term is a commercial exposure | M61 knowledge becomes an M32 prerequisite (`Q-01`) |
| D-A11-06 | Transcript mining | Proceed with a policy statement; **technical block until `SC-003`** | **Technical block** | `HC` is critical; a policy statement is not a control | CD-243 purpose flag is W4 scope |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every ML capability has an inventory entry with a fallback and a decision class | §3.2 — 10 models |
| AC-02 | The fallback contract is architectural and testable | §4 — FB-01…FB-07, DR drill |
| AC-03 | Training-serving skew has a named set of controls | §5.2 — FT-01…FT-06 |
| AC-04 | Drift has three kinds, per-model thresholds and an automatic response | §6 |
| AC-05 | Human override is mandatory and its rate is monitored as a quality signal | §7.1 |
| AC-06 | The LLM evaluation gate `02-05` never defined now exists | §9.4 — EV-01…EV-06 |
| AC-07 | The `HC` transcript-mining finding has a **technical** control, not a policy statement | §10.2 |
| AC-08 | Model cards are mandatory and include the last fallback exercise date | §11 |
| AC-09 | Fairness is assessed where a model affects a person's earnings or service | §10.3 |

**Definition of done.** Complete when every criterion is met, Q-01 is resolved by `SC-003`, and
`PGD-000`'s `AR-011` row is updated with a fresh enumeration timestamp.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` LB-06 | Advisory-write rule |
| Upstream | `AR-004` ADR-029 | Self-hosted LLM |
| Upstream | `AR-008` | Aggregates the advisory records attach to |
| Upstream | `DA-007` | Analytical model features derive from |
| Upstream | **`SC-003`** | DPIA — **blocking for Q-01** |
| Downstream | `AR-003` M26/M32/M48 SDDs | Implementation design |
| Downstream | `AR-012` `FF-07` | Advisory-write CI check |
| Downstream | `PE-006` | GPU and inference sizing |
| Downstream | `QA-006` | Latency testing of the inference path |
| Downstream | `SC-002` | **Prompt injection as an abuse case** (LLM-07) |
| Lateral | `../../1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M26_*`, `B_Customer_Engagement_and_Experience/M32_*`, `F_Asset_Equipment_and_Facilities/M48_*` | The modules realised |

---

## 16. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001` · `./AR-004` · `./AR-008` · `./AR-012` ·
`../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M26_*.md` ·
`.../B_Customer_Engagement_and_Experience/M32_*.md` · `.../F_Asset_Equipment_and_Facilities/M48_*.md` ·
`.../02_Architecture/02-05` §7 · `.../05_Cross_Cutting_Specifications/05-02` §10, `05-06` §6.3 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §23 `TR-17`, §24 TD-06, §25.4 `A-04`

**External standards**

| Standard | Version | Verified |
|---|---|---|
| ISO/IEC 23894 — AI risk management | 2023 | 2026-08-18 |
| ISO/IEC 42001 — AI management systems | 2023 | 2026-08-18 |
| Mitchell et al., *Model Cards for Model Reporting* | 2019 | 2026-08-18 |
| Personal Data Protection Act 2026, Bangladesh — NFR-090, NFR-093, NFR-099 | In force | 2026-08-18 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Ten-model inventory, all advisory. Defines the `ML-01` fallback contract and the LLM evaluation gate `02-05` omitted. Converts the `HC` transcript-mining finding into a technical control | *Pending — CTO* |

---

*`AR-011` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
