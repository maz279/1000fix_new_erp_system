---
id: FIX-ERP2-009
title: Pillar E — Intelligence & Platform Modules (M25–M30)
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Pillar E — Intelligence & Platform
# Modules M25–M30: Features & Functions

**Pillar owner:** Chief Technology Officer
**Data domain:** Insight, automation, connectivity, identity, tenancy
**Modules:** M25 BID · M26 AIM · M27 CCE · M28 IPF · M29 SEC · M30 ADM

---

# M25 — Business Intelligence & Data Platform (BID)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M25 / `BID` |
| **Status** | Expanded |
| **Priority** | P1 |
| **Wave** | W4 (core) → W8 (warehouse) |
| **Delivery layers** | L4 (Metabase, Grafana, ClickHouse) + L2 (OCA mis-builder) + L5 (CD-110…112) |
| **Requirements** | FR-BID-001 … FR-BID-045 |
| **Effort** | 30 person-weeks |

## 1. Purpose

M25 moves operational data out of the transactional system, models it once, and serves it to
every role that needs it — from a technician looking at their own scorecard on a phone, to the
CEO comparing 51+ branches, to a corporate client reading an SLA report.

The v1.0 plan delivered dashboards. v2.0 delivers a **data platform**: a warehouse, a semantic
layer, governed self-service, and the feature store that M26 depends on.

## 2. Functional Areas & Features

### 2.1 Data Pipeline & Warehouse

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-BID-001 | Operational reporting replica | Serve routine reporting from a read replica so the transactional system is never impacted | P1 |
| FR-BID-002 | Warehouse ingestion | Load data from PostgreSQL, TimescaleDB and event streams into an analytical warehouse on a defined schedule | P2 |
| FR-BID-003 | Dimensional model | Model conformed dimensions (date, customer, asset, employee, branch, business line, part, vendor, seller) and fact tables | P2 |
| FR-BID-004 | Slowly changing dimensions | Preserve history of customer, asset, employee and price changes | P2 |
| FR-BID-005 | Incremental & CDC loading | Load incrementally by change data capture to keep the warehouse near-real-time | P2 |
| FR-BID-006 | Time-series store | Store GPS, telemetry and metric data in a purpose-built time-series store with retention and downsampling | P2 |
| FR-BID-007 | Data quality monitoring | Test freshness, completeness, uniqueness and referential integrity on every load, and alert on failure | P2 |
| FR-BID-008 | Data lineage | Record lineage from source column to dashboard field | P3 |

### 2.2 Semantic Layer & Governance

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-BID-009 | Metric definitions | Define every business metric once, centrally, with formula, grain, filters and owner | P1 |
| FR-BID-010 | Certified datasets | Publish curated, certified datasets that business users can safely query | P2 |
| FR-BID-011 | Row-level security | Apply the same data-isolation tiers in analytics as in the ERP — branch, zone, own-record, customer-scoped | P0 |
| FR-BID-012 | Metric change control | Version metric definitions and communicate changes, so numbers do not silently move | P2 |
| FR-BID-013 | Data dictionary | Publish a searchable dictionary of tables, fields and metrics with business definitions | P2 |

### 2.3 Dashboards & Reporting

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-BID-014 | Executive dashboard | Revenue, margin, volume, CSAT, utilisation and cash across the group, by business line, refreshed frequently | P1 |
| FR-BID-015 | Branch performance dashboard | Compare all 51+ branches on volume, TAT, SLA, revenue, cost, margin, utilisation and CSAT, with league tables | P1 |
| FR-BID-016 | Technician scorecard | Jobs, first-time fix, CSAT, rework, utilisation, travel and earnings per technician | P1 |
| FR-BID-017 | Operational live board | Real-time open jobs, technicians on the map, SLA countdowns and queue health | P1 |
| FR-BID-018 | Self-service exploration | Let authorised users build their own analyses on certified datasets without SQL | P1 |
| FR-BID-019 | Financial dashboards | Revenue by stream, P&L by dimension, AR ageing, cash position, budget variance | P1 |
| FR-BID-020 | Inventory dashboards | Stock value, coverage, turns, dead stock, stockouts, network availability | P1 |
| FR-BID-021 | Warranty & claims dashboards | Claim pipeline, ageing, approval rate, revenue at risk, brand scorecards | P1 |
| FR-BID-022 | Contract & subscription dashboards | Base, renewals, churn, entitlement consumption, contract margin | P1 |
| FR-BID-023 | Marketplace dashboards | GMV, take rate, seller performance, dispute rate, ad revenue | P2 |
| FR-BID-024 | Managed-services dashboards | Estate health, alert volume, SLA attainment, patch compliance per client | P2 |
| FR-BID-025 | Quality dashboards | NCRs, CAPA status, complaint trends, audit findings, rework analysis | P1 |
| FR-BID-026 | Customer-facing analytics | Embed scoped dashboards in the customer and B2B portals (their data only) | P2 |
| FR-BID-027 | Mobile dashboards | Deliver key dashboards in a mobile-optimised form for managers and technicians | P1 |

### 2.4 Distribution & Alerting

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-BID-028 | Scheduled distribution | Schedule reports for email or portal delivery by role, with parameters | P1 |
| FR-BID-029 | Export | Export to PDF, Excel and CSV with formatting and full audit of exports | P1 |
| FR-BID-030 | Threshold alerts | Alert when a metric crosses a threshold or deviates from expectation | P1 |
| FR-BID-031 | Anomaly detection | Detect statistical anomalies in key metrics and alert with context | P3 |
| FR-BID-032 | Report subscriptions | Let users subscribe to reports and manage their own subscriptions | P2 |

*(FR-BID-033 … FR-BID-045 cover the feature store for M26, embedded analytics APIs,
warehouse cost management and BI adoption analytics — catalogued in Doc 11.)*

## 3. Key Entities

`fix.metric.definition` · `fix.dataset` · `fix.dashboard` · `fix.report.definition` ·
`fix.report.schedule` · `fix.data.quality.test` · `fix.data.lineage` · `fix.feature.store` ·
warehouse dimension and fact tables (see Doc 12 §9)

## 4. KPIs

| KPI | Target |
|---|---|
| Executive dashboard load time | < 5 seconds |
| Standard report generation | < 30 seconds |
| Data freshness (operational dashboards) | < 15 minutes |
| Data freshness (warehouse) | < 60 minutes |
| Data quality test pass rate | > 99% |
| Manager weekly dashboard usage | > 90% |
| Manual spreadsheet reports remaining | Zero by W8 |

---

# M26 — AI/ML Services (AIM)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M26 / `AIM` |
| **Status** | ★ New in v2.0 |
| **Priority** | P2 |
| **Wave** | W6 → W8 |
| **Delivery layers** | L4 (model serving, MLflow) + L5 (CD-113…118) |
| **Requirements** | FR-AIM-001 … FR-AIM-038 |
| **Effort** | 40 person-weeks |

## 1. Purpose

M26 is **not** a product. It is a set of callable services that make other modules better, each
with a defined input, output, owner, accuracy target and fallback behaviour. Every model must
be explainable enough that a human can overrule it, and every module that consumes a model
must work correctly when the model is unavailable.

**Evidence:** Portal roadmap IMPL-34 (ML service architecture), IMPL-40 (predictive
maintenance), IMPL-41 (demand forecasting), IMPL-42 (quality monitoring), IMPL-44 (enhanced
dispatch); Service App SOW §AI-Powered Predictive Maintenance.

## 2. The Model Portfolio

| Model | Consumed By | Input | Output | Target |
|---|---|---|---|---|
| **Dispatch assignment scoring** | M02 | Job, technician pool, context | Ranked technicians with confidence | 70%+ auto-assign, ≥ 90% dispatcher agreement |
| **Duration prediction** | M02, M01 | Device, fault, technician, history | Predicted repair minutes | MAE < 20% |
| **Travel time prediction** | M02, M03 | Origin, destination, time, day | Predicted minutes | MAE < 15% |
| **Parts demand forecast** | M15, M16 | History, seasonality, installed base | Demand by part, location, period | MAPE < 22% |
| **Service demand forecast** | M02, M21 | History, seasonality, campaigns, weather | Job volume by zone and day | MAPE < 18% |
| **Predictive failure** | M17, M08 | Telemetry, age, service history, model | Failure probability and window | Precision > 70% |
| **Fault classification** | M01, M27 | Complaint text (Bengali/English), device | Likely fault codes, ranked | Top-3 accuracy > 80% |
| **Price elasticity / win probability** | M11 | Quote context, customer, competition | Win probability by price point | AUC > 0.75 |
| **Churn risk** | M07, M08, M10 | Recency, frequency, value, satisfaction | Churn probability | AUC > 0.72 |
| **Quality risk scoring** | M23 | Job attributes, technician, history | Probability of rework/complaint | Precision > 60% at top decile |
| **Fraud & anomaly detection** | M12, M19, M20 | Transaction and behaviour patterns | Anomaly score with reasons | Recall > 80% at 5% false positive |
| **Trade-in valuation** | M14 | Model, age, condition, market signals | Indicative price range | Within 10% of assessed value 75% of the time |
| **Bengali NLP (intent, entity, sentiment)** | M27, M07 | Bengali/English/mixed text or speech | Intent, entities, sentiment | Intent accuracy > 88% |
| **Document extraction (OCR/IE)** | M16, M24, M09 | Scanned invoices, warranty documents | Structured fields | Field accuracy > 92% |

## 3. Functional Areas & Features

### 3.1 ML Platform

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-AIM-001 | Feature store | Maintain versioned, reusable features with consistent definitions for training and serving | P2 |
| FR-AIM-002 | Training pipelines | Run reproducible, scheduled training with data versioning and experiment tracking | P2 |
| FR-AIM-003 | Model registry | Register models with version, metrics, lineage, approval status and owner | P2 |
| FR-AIM-004 | Model serving | Serve models over a low-latency API with autoscaling and health checks | P2 |
| FR-AIM-005 | Batch scoring | Score in batch for forecasts, risk scores and recommendations | P2 |
| FR-AIM-006 | Model monitoring | Monitor prediction distribution, feature drift, latency and accuracy against outcomes | P2 |
| FR-AIM-007 | Retraining triggers | Retrain automatically on drift, on schedule or on accuracy degradation | P2 |
| FR-AIM-008 | A/B and shadow testing | Test a candidate model in shadow or against a holdout before promoting it | P2 |

### 3.2 Governance & Safety

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-AIM-009 | Human-in-the-loop | Require human confirmation for any decision with material customer or financial impact | P0 |
| FR-AIM-010 | Explainability | Provide the reasons behind every material prediction in language the user understands | P0 |
| FR-AIM-011 | Override & feedback | Let a human override any recommendation, capture the reason, and feed it back into training | P0 |
| FR-AIM-012 | Guard rails | Enforce hard business limits that no model may cross (price floors/ceilings, certification requirements, safety rules) | P0 |
| FR-AIM-013 | Graceful degradation | Ensure every consuming module has a defined, tested fallback when the model is unavailable | P0 |
| FR-AIM-014 | Bias & fairness testing | Test models affecting people (dispatch, incentives, seller ranking) for systematic bias and document the results | P1 |
| FR-AIM-015 | Model documentation | Maintain a model card per production model — purpose, data, limits, metrics, owner, review date | P1 |
| FR-AIM-016 | Decision audit | Log every model-influenced decision with inputs, output, version and whether a human overrode it | P0 |
| FR-AIM-017 | Data protection in ML | Exclude sensitive personal data from features unless justified; never train on recovered customer data (M06) | P0 |

### 3.3 Generative AI Services

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-AIM-018 | Self-hosted LLM inference | Serve a Bengali-capable open-weight model on Company infrastructure so customer data does not leave | P2 |
| FR-AIM-019 | Retrieval-augmented generation | Ground responses in the Company's own knowledge base, manuals and policies with citations | P2 |
| FR-AIM-020 | Tool use | Let the assistant call ERP APIs to check status, create bookings and look up entitlements, within permission scope | P2 |
| FR-AIM-021 | Summarisation | Summarise long service histories, call transcripts and complaint threads for agents | P3 |
| FR-AIM-022 | Draft generation | Draft service report narratives, customer replies and knowledge articles for human review | P3 |
| FR-AIM-023 | Prompt and output safety | Filter prompts and outputs; never expose one customer's data to another; refuse out-of-scope requests | P0 |
| FR-AIM-024 | Cost and latency control | Cap inference cost and latency per request with fallbacks to lighter models | P2 |

*(FR-AIM-025 … FR-AIM-038 cover per-model implementation detail, evaluation harnesses,
labelled-data collection and the ML operations runbook — catalogued in Doc 11.)*

## 4. Key Entities

`fix.ml.feature` · `fix.ml.feature.set` · `fix.ml.model` · `fix.ml.model.version` ·
`fix.ml.prediction.log` · `fix.ml.override` · `fix.ml.drift.metric` · `fix.ml.experiment` ·
`fix.model.card` · `fix.llm.session` · `fix.llm.citation`

## 5. KPIs

| KPI | Target |
|---|---|
| Automatic dispatch assignment rate | > 70% |
| Dispatcher agreement with recommendation | > 90% |
| Parts forecast accuracy (MAPE) | < 22% |
| Predictive-failure precision | > 70% |
| Models with a current model card | 100% |
| Model-influenced decisions logged | 100% |
| Incidents caused by unavailable models | Zero |

---

# M27 — Conversational AI & Omnichannel Contact Centre (CCE)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M27 / `CCE` |
| **Status** | ★ New in v2.0 |
| **Priority** | P1 |
| **Wave** | W4 |
| **Delivery layers** | L4 (Novu, chat infrastructure) + L5 (CD-119…124) + L6 (telephony) |
| **Requirements** | FR-CCE-001 … FR-CCE-047 |
| **Effort** | 34 person-weeks |

## 1. Purpose

Hotline **16743** takes calls from 250,000+ customers a month. WhatsApp, chat, email and social
messaging add more. Today none of this is inside the system of record — so the Company cannot
see the full customer conversation, cannot measure the 24/7 support it sells, and cannot
automate the routine half of it.

M27 brings every inbound and outbound conversation into one place, with AI handling first
line and humans handling what matters.

**Evidence:** Business Plan §24/7 Technical Support (phone, email, live chat, remote
assistance, knowledge base, escalation, quality monitoring); Service App SOW §In-app chat,
§Chatbot configuration, §Direct calling to call centre, §"at the end of the chat the customer
can rate the conversation and the entire conversation will be mailed to the customer's inbox",
§Attachment option in chat, §"from the chat window, the agent can move instantly to any other
relevant window".

## 2. Functional Areas & Features

### 2.1 Omnichannel Inbox

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CCE-001 | Unified conversation object | Represent every interaction — call, chat, WhatsApp, email, SMS, social, in-app — as one conversation linked to the customer | P1 |
| FR-CCE-002 | Channel connectors | Connect voice (IVR/PBX), WhatsApp Business, web chat, in-app chat, email, SMS and social messaging | P1 |
| FR-CCE-003 | Unified agent inbox | Give agents a single queue across all channels with priority, SLA and context | P1 |
| FR-CCE-004 | Conversation threading | Thread related interactions across channels and time into one customer narrative | P1 |
| FR-CCE-005 | Attachments | Send and receive images, documents and short videos on any channel that supports them | P1 |
| FR-CCE-006 | Conversation transcript delivery | Email the full transcript to the customer's inbox at the end of a chat | P1 |
| FR-CCE-007 | Conversation rating | Ask the customer to rate the conversation at close and record it against the agent | P1 |

### 2.2 Voice & Telephony

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CCE-008 | Inbound call handling | Receive calls on 16743 with IVR, language selection (Bengali/English) and menu routing | P1 |
| FR-CCE-009 | Screen pop | Identify the caller by number and open their Customer 360 automatically | P1 |
| FR-CCE-010 | Skill-based routing | Route calls by language, service category, customer tier and agent skill | P1 |
| FR-CCE-011 | Queue management | Manage queues with position announcement, estimated wait, callback offer and overflow | P1 |
| FR-CCE-012 | Call recording | Record calls with consent notice, store securely with retention and restricted access | P1 |
| FR-CCE-013 | Outbound campaigns | Run outbound calling for renewals, collections and follow-ups with call outcomes recorded | P2 |
| FR-CCE-014 | Click-to-call | Let agents and technicians place calls from within the ERP with automatic logging | P1 |
| FR-CCE-015 | Call transcription | Transcribe Bengali and English calls for search, quality review and analytics | P3 |
| FR-CCE-016 | 24/7 coverage | Support follow-the-clock staffing, after-hours routing and emergency escalation | P1 |

### 2.3 AI Assistant

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CCE-017 | Bengali-first assistant | Understand and respond in Bengali, English and mixed Banglish, in text and (later) voice | P1 |
| FR-CCE-018 | Intent handling | Handle the high-volume intents: book a service, check status, get a price, find a branch, check warranty, request a callback, log a complaint, renew a contract | P1 |
| FR-CCE-019 | Authenticated actions | After verifying identity, let the assistant perform real actions through ERP APIs within permission scope | P1 |
| FR-CCE-020 | Knowledge grounding | Answer from the Company's knowledge base with citations; never invent policy or price | P0 |
| FR-CCE-021 | Confidence-based handoff | Hand off to a human when confidence is low, sentiment is negative, the request is out of scope, or the customer asks | P0 |
| FR-CCE-022 | Context transfer on handoff | Give the receiving agent the full conversation, the assistant's understanding and the actions already taken | P1 |
| FR-CCE-023 | Assistant guard rails | Never quote a price outside the price book, never promise a date outside capacity, never disclose another customer's data | P0 |
| FR-CCE-024 | Continuous improvement | Review unhandled and mis-handled intents weekly and expand coverage | P2 |
| FR-CCE-025 | Agent assist | Suggest replies, knowledge articles and next actions to human agents in real time | P2 |

### 2.4 Agent Workspace & Productivity

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CCE-026 | Agent console | Provide one workspace with conversation, customer context, knowledge, actions and disposition | P1 |
| FR-CCE-027 | Contextual navigation | Let the agent jump directly from the conversation to the relevant ERP screen and back without losing context | P1 |
| FR-CCE-028 | Canned responses | Maintain approved response templates in Bengali and English with variable substitution | P1 |
| FR-CCE-029 | Disposition & wrap-up | Require structured disposition coding at close, feeding analytics and quality | P1 |
| FR-CCE-030 | Internal collaboration | Consult a colleague or supervisor within the conversation without transferring the customer | P2 |
| FR-CCE-031 | Remote-session launch | Launch an M05 remote support session from within the conversation | P1 |
| FR-CCE-032 | Agent status & availability | Manage agent presence, breaks and capacity across channels | P1 |

### 2.5 Quality & Workforce Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CCE-033 | Quality monitoring | Sample and score conversations against a quality form with agent feedback | P2 |
| FR-CCE-034 | Coaching | Record coaching sessions and track improvement | P2 |
| FR-CCE-035 | Forecasting & scheduling | Forecast contact volume and schedule agents to meet service level | P2 |
| FR-CCE-036 | Real-time supervision | Show live queues, service level, agent status and allow barge-in on calls | P2 |
| FR-CCE-037 | Contact centre analytics | Report volume, handling time, first-contact resolution, abandonment, service level and CSAT by channel | P1 |

### 2.6 Proactive & Outbound Communication

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CCE-038 | Notification orchestration | Deliver every system notification across channels with per-customer preference and language | P0 |
| FR-CCE-039 | Template management | Maintain approved templates per event, channel and language, with WhatsApp template approval tracking | P0 |
| FR-CCE-040 | Delivery tracking | Track sent, delivered, read and failed for every message, with retry and channel fallback | P1 |
| FR-CCE-041 | Quiet hours | Suppress non-urgent messages between 22:00 and 07:00 with emergency override | P1 |
| FR-CCE-042 | Preference centre | Let customers manage which notifications they receive on which channel | P1 |
| FR-CCE-043 | In-app inbox | Maintain a persistent in-app inbox of all notifications — order updates, review requests, SMS/email copies, profile changes — read-only in phase one, replyable later | P1 |

*(FR-CCE-044 … FR-CCE-047 cover video support calls, social listening, and contact-centre
integration with M23 complaint handling — catalogued in Doc 11.)*

## 3. Key Entities

`fix.conversation` · `fix.conversation.message` · `fix.channel.connector` · `fix.call.record` ·
`fix.ivr.flow` · `fix.agent.session` · `fix.agent.queue` · `fix.disposition.code` ·
`fix.canned.response` · `fix.assistant.session` · `fix.assistant.intent` ·
`fix.notification.template` · `fix.notification.log` · `fix.notification.preference` ·
`fix.inbox.item` · `fix.quality.evaluation`

## 4. KPIs

| KPI | Baseline | Target |
|---|---|---|
| Conversations captured in system | ~0% | 100% |
| AI first-contact resolution | 0% | > 55% |
| Average speed to answer (voice) | unmeasured | < 30 seconds |
| Abandonment rate | unmeasured | < 6% |
| First-contact resolution (overall) | unmeasured | > 78% |
| Conversation CSAT | unmeasured | > 4.5/5 |
| Notification delivery success | unmeasured | > 98% |
| Status-check calls to the hotline | high | −60% (deflected to self-service) |

---

# M28 — Integration, API & Event Platform (IPF)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M28 / `IPF` |
| **Status** | Expanded |
| **Priority** | P0 |
| **Wave** | W1 |
| **Delivery layers** | L4 (Kong, n8n, message bus) + L5 (CD-125…129) |
| **Requirements** | FR-IPF-001 … FR-IPF-058 |
| **Effort** | 31 person-weeks |

## 1. Purpose

Twelve portals, 30 modules, 47 external integrations and a Next.js platform that must not be
replaced. M28 is the connective tissue and the reason the whole estate does not become a mesh
of point-to-point couplings.

## 2. Functional Areas & Features

### 2.1 API Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-IPF-001 | API gateway | Terminate, authenticate, authorise, rate-limit, route and observe every API call through one gateway | P0 |
| FR-IPF-002 | API versioning | Version every API; support at least two concurrent versions with a published deprecation policy | P0 |
| FR-IPF-003 | OpenAPI specifications | Publish an OpenAPI 3.1 specification for every API, generated from code and validated in CI | P0 |
| FR-IPF-004 | Developer portal | Provide a portal with documentation, try-it consoles, credentials and change logs for internal and partner developers | P1 |
| FR-IPF-005 | API key & token management | Issue, rotate and revoke credentials per consumer with scoped permissions | P0 |
| FR-IPF-006 | Rate limiting & quotas | Apply per-consumer rate limits and quotas with clear error semantics | P0 |
| FR-IPF-007 | Request/response validation | Validate against the schema at the gateway and reject malformed traffic | P1 |
| FR-IPF-008 | GraphQL federation | Provide a federated GraphQL layer for portal consumers that need composed data | P2 |
| FR-IPF-009 | Backend-for-frontend | Provide purpose-built aggregation endpoints per portal to keep clients thin | P1 |

### 2.2 Event Platform

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-IPF-010 | Transactional outbox | Guarantee that every event is published exactly once with its transaction | P0 |
| FR-IPF-011 | Event bus | Distribute events to subscribers with ordering guarantees per aggregate | P0 |
| FR-IPF-012 | Event catalogue | Maintain a versioned catalogue of every event with schema, producer, consumers and examples | P0 |
| FR-IPF-013 | Schema registry | Enforce schema compatibility; block breaking changes without a version bump | P1 |
| FR-IPF-014 | Idempotent consumption | Provide the framework that guarantees consumers process each event once | P0 |
| FR-IPF-015 | Dead-letter handling | Capture, alert on and allow replay of failed event processing | P0 |
| FR-IPF-016 | Event replay | Replay events to rebuild a projection or recover a consumer | P1 |
| FR-IPF-017 | Event audit | Retain an immutable event log for audit and forensic reconstruction | P1 |

### 2.3 Integration Connectors

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-IPF-018 | Connector framework | Provide a common framework for building external connectors — auth, retry, backoff, circuit breaking, logging | P0 |
| FR-IPF-019 | Credential vault | Store third-party credentials encrypted with rotation and access audit | P0 |
| FR-IPF-020 | Workflow automation engine | Provide a low-code workflow engine for cross-system orchestration and notification routing | P0 |
| FR-IPF-021 | Webhook receiver | Receive third-party webhooks with signature verification, replay protection and idempotency | P0 |
| FR-IPF-022 | Webhook publisher | Publish outbound webhooks to partners with retry, signing and delivery tracking | P1 |
| FR-IPF-023 | File exchange | Handle scheduled file exchange over SFTP with validation, archiving and error handling | P1 |
| FR-IPF-024 | Batch job framework | Run scheduled batch jobs with monitoring, alerting, restart and idempotency | P0 |

### 2.4 Data Synchronisation

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-IPF-025 | Next.js platform sync | Maintain bidirectional synchronisation with the portal platform for customers, orders, availability, invoices and status | P0 |
| FR-IPF-026 | Conflict resolution | Define and enforce which system wins for each field, with reconciliation reporting | P0 |
| FR-IPF-027 | Offline sync protocol | Provide the sync protocol used by all offline-capable applications, with an append-only journal and deterministic resolution | P0 |
| FR-IPF-028 | Master data distribution | Distribute master data (catalogue, prices, branches, brands) to consuming systems with versioning | P1 |
| FR-IPF-029 | Reconciliation reporting | Report and alert on data divergence between systems on a schedule | P1 |

### 2.5 Observability of Integrations

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-IPF-030 | Distributed tracing | Trace a request end to end across gateway, ERP, services and external calls with a correlation ID | P1 |
| FR-IPF-031 | Integration dashboard | Show the health, throughput, latency and error rate of every integration | P1 |
| FR-IPF-032 | Failure alerting | Alert the right team on integration failure with actionable context | P0 |
| FR-IPF-033 | Retry and compensation | Retry transient failures with backoff; run compensating actions for unrecoverable ones | P0 |
| FR-IPF-034 | Third-party status awareness | Detect third-party outages and degrade gracefully with user-visible messaging | P1 |

*(FR-IPF-035 … FR-IPF-058 cover the full external integration catalogue implementation,
sandbox environments, partner onboarding and API analytics — catalogued in Docs 11 and 13.)*

## 3. Key Entities

`fix.api.consumer` · `fix.api.credential` · `fix.api.usage.log` · `fix.domain.event` ·
`fix.event.schema` · `fix.event.subscription` · `fix.event.delivery` · `fix.dead.letter` ·
`fix.integration.config` · `fix.integration.credential` · `fix.webhook.endpoint` ·
`fix.webhook.delivery` · `fix.sync.state` · `fix.sync.conflict` · `fix.batch.job.run`

## 4. KPIs

| KPI | Target |
|---|---|
| API availability | > 99.95% |
| API p95 latency | < 400 ms |
| Event delivery success | > 99.9% |
| Events in dead-letter unresolved > 1 hour | Zero |
| Integration failures undetected > 5 minutes | Zero |
| APIs with current OpenAPI spec | 100% |
| Data divergence incidents (ERP vs portal) | Zero |

---

# M29 — Identity, Security, Access & Audit (SEC)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M29 / `SEC` |
| **Status** | Expanded |
| **Priority** | P0 |
| **Wave** | W1 |
| **Delivery layers** | L4 (Keycloak, secrets management, SIEM) + L2 (OCA audit) + L5 (CD-130…132) |
| **Requirements** | FR-SEC-001 … FR-SEC-044 |
| **Effort** | 23 person-weeks |

## 1. Purpose

M29 answers two questions for the whole estate: **who is this, and what may they do?** — and
records the answer to a third: **what actually happened?**

With 38 roles, 12 portals, external sellers, corporate clients with their own SSO, and
recovered customer data in the building, identity and audit are not optional infrastructure.

## 2. Functional Areas & Features

### 2.1 Identity & Authentication

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SEC-001 | Central identity provider | Operate a single identity provider for all systems and portals | P0 |
| FR-SEC-002 | Single sign-on | Provide SSO across ERP, portals, BI, monitoring and supporting systems via OIDC/SAML | P0 |
| FR-SEC-003 | Multi-factor authentication | Require MFA for admin, finance, HR and any role with elevated access; offer it to all users | P0 |
| FR-SEC-004 | Password policy | Enforce length, complexity, history, expiry and breach-list checking | P0 |
| FR-SEC-005 | Passwordless & biometric | Support device biometrics and passkeys on mobile applications | P2 |
| FR-SEC-006 | Social & phone login | Support phone-OTP and social login for customer accounts | P1 |
| FR-SEC-007 | Corporate SSO federation | Federate with corporate clients' identity providers so their staff use their own credentials | P2 |
| FR-SEC-008 | Session management | Enforce timeouts, concurrent-session limits, device registration and forced logout | P0 |
| FR-SEC-009 | Step-up authentication | Require re-authentication for sensitive actions (payouts, payroll, data-case access, mass updates) | P0 |
| FR-SEC-010 | Service identities | Issue and rotate machine identities for services and integrations | P0 |

### 2.2 Authorisation

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SEC-011 | Role-based access control | Define 38 roles with permission sets mapped to modules, objects and operations | P0 |
| FR-SEC-012 | Field-level permissions | Restrict visibility and editability at field level (cost, margin, salary, NID, recovered data) | P0 |
| FR-SEC-013 | Record-level rules | Enforce the six data-isolation tiers (global, entity, branch, zone, own-record, restricted) | P0 |
| FR-SEC-014 | Attribute-based rules | Support context-based access decisions (time, location, device, business line) | P2 |
| FR-SEC-015 | Delegation | Allow temporary delegation of authority with expiry and full audit | P1 |
| FR-SEC-016 | Segregation of duties | Define and enforce incompatible duty combinations, with reporting on violations | P1 |
| FR-SEC-017 | Just-in-time elevation | Grant temporary elevated access with approval, time limit and session recording | P2 |
| FR-SEC-018 | Access request & approval | Provide a self-service access request workflow with the correct approvers | P1 |
| FR-SEC-019 | Access certification | Run periodic access reviews where managers confirm or revoke their team's access | P1 |

### 2.3 Data Protection

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SEC-020 | Encryption at rest | Encrypt the database, file storage and backups with managed key rotation | P0 |
| FR-SEC-021 | Encryption in transit | Enforce TLS 1.2+ everywhere, including internal service traffic | P0 |
| FR-SEC-022 | Field-level encryption | Encrypt the most sensitive fields (NID, bank details, recovered-data indexes) with separate keys | P0 |
| FR-SEC-023 | Key management | Manage keys in a dedicated key store with rotation, escrow and access audit | P0 |
| FR-SEC-024 | Data masking | Mask personal data in non-production environments and in screens where full values are not needed | P0 |
| FR-SEC-025 | Data-subject rights | Support access, correction, portability and erasure requests within legal constraints | P1 |
| FR-SEC-026 | Data residency | Enforce where each data class may be stored and processed | P1 |
| FR-SEC-027 | Malware scanning | Scan every uploaded file before it is stored or served | P0 |
| FR-SEC-028 | Secrets management | Store application secrets in a vault; never in code, config files or environment dumps | P0 |

### 2.4 Audit & Monitoring

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SEC-029 | Immutable audit trail | Record who did what, when, from where, with before and after values, in an append-only store | P0 |
| FR-SEC-030 | Audit coverage | Audit all financial, personal, contractual and configuration changes without exception | P0 |
| FR-SEC-031 | Access logging | Log every access to restricted data (payroll, NID, recovered data, call recordings) | P0 |
| FR-SEC-032 | Security monitoring | Detect and alert on brute force, privilege escalation, anomalous data access and mass export | P1 |
| FR-SEC-033 | Audit search & reporting | Search and report the audit trail for investigations and audits, without allowing modification | P0 |
| FR-SEC-034 | Retention of audit data | Retain audit records for five years, tamper-evident | P0 |

### 2.5 Security Operations

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SEC-035 | Vulnerability management | Scan dependencies, containers and infrastructure; track remediation to closure | P1 |
| FR-SEC-036 | Penetration testing | Commission annual penetration tests and track findings | P1 |
| FR-SEC-037 | Incident response | Operate a defined incident-response process with severity classification and breach-notification assessment | P1 |
| FR-SEC-038 | Backup & recovery assurance | Verify backups by periodic restore testing | P0 |
| FR-SEC-039 | Network security | Enforce WAF, DDoS protection, private networking and minimal exposed surface | P0 |
| FR-SEC-040 | Endpoint & workstation policy | Define and enforce security requirements for staff devices accessing the system | P2 |

*(FR-SEC-041 … FR-SEC-044 cover security awareness training linkage to M22, third-party
security assessment and the security metrics dashboard — catalogued in Doc 11.)*

## 3. Key Entities

`fix.identity` · `fix.role` · `fix.permission.set` · `fix.record.rule` ·
`fix.field.permission` · `fix.delegation` · `fix.sod.rule` · `fix.access.request` ·
`fix.access.certification` · `fix.audit.entry` · `fix.data.access.log` ·
`fix.security.event` · `fix.encryption.key.ref` · `fix.vulnerability`

## 4. KPIs

| KPI | Target |
|---|---|
| MFA coverage on privileged accounts | 100% |
| Orphaned accounts after leaver | Zero beyond 24 hours |
| Access certification completion | 100% per cycle |
| Critical vulnerabilities open > 7 days | Zero |
| Audit coverage of financial transactions | 100% |
| Security incidents with data loss | Zero |
| Backup restore tests passed | 100% |

---

# M30 — Platform Administration, Multi-Entity & Multi-Country (ADM)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M30 / `ADM` |
| **Status** | ★ New in v2.0 |
| **Priority** | P2 |
| **Wave** | W9 |
| **Delivery layers** | L1 (Odoo multi-company) + L5 (CD-133…138) |
| **Requirements** | FR-ADM-001 … FR-ADM-035 |
| **Effort** | 26 person-weeks |

## 1. Purpose

M30 is how the platform is configured and how it grows. It holds the organisational
structure, the master-data governance, the feature flags, the locale packs and the country
packs that let 1000FiX operate a second entity or a second country without a rebuild.

**Evidence:** Portal roadmap IMPL-57 Multi-Country Expansion Framework, IMPL-51 Multi-Region
Database Architecture; Service App SOW references to international customers and service
providers; BRD BO-09 growth objective.

## 2. Functional Areas & Features

### 2.1 Organisation Configuration

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ADM-001 | Legal entity management | Define legal entities with registration, tax identity, currency, fiscal calendar and reporting requirements | P2 |
| FR-ADM-002 | Branch & operating unit | Define branches with address, geography, service capabilities, operating hours, manager and cost centre | P0 |
| FR-ADM-003 | Zone & territory | Define dispatch zones, service territories and their branch relationships | P1 |
| FR-ADM-004 | Cost centre & business line | Define the reporting dimensions used across finance and analytics | P1 |
| FR-ADM-005 | Calendar management | Define working calendars, shifts, holidays and service windows per entity and branch | P1 |
| FR-ADM-006 | Organisation change | Open, close, merge and relocate branches with data-continuity handling | P2 |

### 2.2 Master Data Governance

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ADM-007 | Master data ownership | Define the owner and change process for each master data domain | P1 |
| FR-ADM-008 | Master data workflows | Route master-data changes (parts, prices, brands, service catalogue) through review and approval | P1 |
| FR-ADM-009 | Data quality rules | Define and enforce validation and completeness rules on master data | P1 |
| FR-ADM-010 | Bulk maintenance | Support controlled bulk creation and update with preview, validation and rollback | P1 |
| FR-ADM-011 | Master data audit | Track every master-data change with before/after values and approver | P0 |
| FR-ADM-012 | Reference data distribution | Publish reference data to all consuming systems with versioning | P1 |

### 2.3 Configuration Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ADM-013 | Business rule configuration | Configure thresholds, tolerances, SLAs, sequences and approval matrices without code | P0 |
| FR-ADM-014 | Feature flags | Enable and disable features per entity, branch, role or user cohort, with staged rollout | P1 |
| FR-ADM-015 | Configuration versioning | Version configuration changes with author, reason, effective date and rollback | P1 |
| FR-ADM-016 | Environment promotion | Promote configuration from staging to production with a controlled, auditable process | P1 |
| FR-ADM-017 | Configuration documentation | Auto-document current configuration for audit and handover | P2 |

### 2.4 Localisation & Country Packs

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ADM-018 | Language management | Manage translations for all user-facing strings with completeness reporting per language | P0 |
| FR-ADM-019 | Bengali-first defaults | Default field-facing and customer-facing surfaces to Bengali with per-user override | P0 |
| FR-ADM-020 | Locale formatting | Apply locale-correct date, time, number, currency and address formats — including the Bangladeshi lakh/crore convention | P0 |
| FR-ADM-021 | Country pack structure | Package country-specific tax rules, statutory reports, payroll rules, address structure, holidays and payment methods as an installable unit | P2 |
| FR-ADM-022 | Bangladesh country pack | Deliver Bangladesh as the reference implementation of the country pack | P0 |
| FR-ADM-023 | Currency & FX | Manage currencies, rate sources and rate history per entity | P1 |
| FR-ADM-024 | Regulatory variation | Isolate regulatory behaviour so a new country does not require changes to core modules | P2 |

### 2.5 Tenancy & Expansion Readiness

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ADM-025 | Entity isolation | Guarantee data isolation between legal entities with explicit, audited sharing | P2 |
| FR-ADM-026 | Cross-entity reporting | Consolidate reporting across entities with currency translation | P2 |
| FR-ADM-027 | Entity onboarding runbook | Provide a repeatable process to stand up a new entity or country | P2 |
| FR-ADM-028 | Regional deployment | Support deployment in an additional region for latency or residency, with defined replication | P3 |

### 2.6 Platform Operations

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ADM-029 | User administration | Create, modify, suspend and delete users with role assignment, integrated with M29 and HR joiner/leaver events | P0 |
| FR-ADM-030 | System health console | Show platform health, job queues, integration status and error rates in one place | P1 |
| FR-ADM-031 | Scheduled job management | View, monitor, pause, resume and rerun scheduled jobs | P1 |
| FR-ADM-032 | Announcements | Publish system announcements and maintenance notices to users by role and portal | P2 |
| FR-ADM-033 | Data archival | Archive aged transactional data to keep the operational database performant, with retrieval | P2 |
| FR-ADM-034 | Sandbox management | Provide and refresh non-production environments with masked data | P1 |
| FR-ADM-035 | Licence & subscription register | Track third-party subscriptions, licences, renewals and costs | P2 |

## 3. Key Entities

`fix.entity` · `fix.branch` · `fix.zone` · `fix.cost.center` · `fix.business.line` ·
`fix.working.calendar` · `fix.master.data.domain` · `fix.mdm.change.request` ·
`fix.config.parameter` · `fix.config.version` · `fix.feature.flag` · `fix.locale.pack` ·
`fix.country.pack` · `fix.translation.entry` · `fix.system.announcement` ·
`fix.scheduled.job` · `fix.archive.policy`

## 4. KPIs

| KPI | Target |
|---|---|
| Bengali translation completeness | 100% of user-facing strings |
| Configuration changes made without code | > 95% |
| Master data change approval compliance | 100% |
| Time to stand up a new branch | < 1 day |
| Time to stand up a new legal entity | < 10 days |
| Time to stand up a new country pack | < 12 weeks |
| Unplanned configuration rollbacks | < 2 per quarter |

---

*Next document: `10_Portal_and_Application_Suite_Specification.md`*
