---
id: PE-008
title: Observability & Monitoring Design
category: 10 — Infrastructure, DevOps & Environments
code: PE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
approver: CTO with Head of Service and Design Authority (constituted under GV-002)
standards_basis: >
  OpenTelemetry 1.x (traces, metrics, logs) · Google SRE SLO and multi-window multi-burn-rate
  alerting · USE method (Gregg) · RED method · W3C Trace Context ·
  ISO/IEC 25010 · AR-013 LW-01 licence rules
traces_to: >
  PGD-000 PE-008 · Technology Stack §17 · 02-05 §9 · PE-001 §9.1 availability scopes ·
  PE-006 §7 triggers · PE-007 §13 · AR-009 §5.4 outbox · IN-001 §12 · RP-012 ·
  audit AP-02 (critical), OP-04 · NFR-006, NFR-045, NFR-046, NFR-048, NFR-043, NFR-092
depends_on: PE-001 · PE-002 · PE-005 · PE-006 · DA-005 · SC-007
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 01:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# PE-008 — Observability & Monitoring Design

### Category 10 · Code `PE` · OpenTelemetry · Google SRE SLO practice · W3C Trace Context

---

> **`PGD-000`'s `PE-008` row:** *"`02-05` names OpenTelemetry, Prometheus, Loki, Tempo and Grafana.
> `RP-012` defines alert thresholds for **business** anomalies. **Platform observability is
> undesigned.**"*
>
> **Three findings this document must resolve, measured 2026-08-19 01:45 (+06):**
>
> | # | Finding |
> |---|---|
> | **1** | **The estate states four different availability targets — 99.9%, 99.7%, 99.9% and 99.95% — and two of them do not state a measurement window.** `PE-001` §9.1 reconciled them by scope and flagged the gap; **this document must make them measurable or they are not SLOs** |
> | **2** | **`AP-02` (critical): `NFR-092` means *distributed tracing* in `05-06` §7 and a *PDPA transparency notice* in `05-06` §6.3.** This document's central mechanism — one correlation id across every hop — is cited by one of the two, and the identifier is genuinely ambiguous |
> | **3** | **`AR-013` `LW-01` requires every AGPL component to carry a named fallback. Grafana is `Adopt` and its fallback cell reads "— (observability is replaceable but disruptive)".** Loki, Tempo and Mimir are AGPL-3 too. **The estate's own radar is in violation for its entire observability stack** |

---

## 1. Purpose

`RP-012` defines alert thresholds for business anomalies. Technology Stack §17 draws the stack and
lists what is monitored. **Neither defines an SLO, an error budget, an alert that fires on
user-visible harm rather than on a resource number, or what happens to personal data in a log.**

This document designs platform observability: the signal model and the collection path, the SLOs
that make the estate's availability targets measurable, burn-rate alerting, the dashboard set, log
handling under `DA-005` and `NFR-086c`, retention, correlation across the estate's own boundaries,
and the alert discipline that keeps a paging system trustworthy.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The **signal model** — metrics, logs, traces, and what each is for |
| 2 | The collection path, and its **licence position** |
| 3 | **Instrumentation obligations** on every component |
| 4 | **Correlation** — one id across HTTP, events, jobs and the residency boundary |
| 5 | **SLOs** — reconciling four availability numbers into measurable objectives |
| 6 | **Error budgets and multi-window multi-burn-rate alerting** |
| 7 | Alert discipline, routing, severity and the on-call interface |
| 8 | The dashboard set, per audience |
| 9 | **Logs and personal data** — what may never be logged |
| 10 | Retention, and the `NFR-092` collision |
| 11 | **Observing the residency boundary** without breaching it |
| 12 | What is monitored per tier, and the triggers `PE-006` and `PE-007` require |
| 13 | Fitness functions `FF-165`…`FF-174` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **Business KPIs and anomaly thresholds** | **`RP-012`**, M25 | Business signals, not platform signals — §12.5 states the interface |
| Incident management, on-call rota, escalation | `SV-*`, `OP-013` | This document produces the alert; `SV-*` responds to it |
| Runbooks per alert | `OP-007`…`OP-011` | `OPS-03` requires one per alert; §8.4 enforces the link |
| Where the collectors run | **`PE-005`** | Placement |
| Capacity thresholds | **`PE-006`** §7 | This document instruments them |
| DR drill instrumentation | **`PE-007`** | Consumed |
| Security monitoring, SIEM, threat detection | `SC-009`, Wazuh | §12.4 states the interface only |
| Data classification | `DA-005` | Applied here to logs |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Platform engineers | The whole document |
| Every developer | §4's instrumentation obligations are per-component |
| **Head of Service and on-call** | §7's SLOs, §8's alerts, §9's dashboards |
| **CTO and the Steering Committee** | §7.6's error-budget policy is a delivery-governance instrument |
| DPO | §10 — logs are a processing activity |
| `RQ-006` owner | §7.2's two unmeasurable NFRs |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | Conformance | Departure and rationale |
|---|---|---|---|
| **OpenTelemetry 1.x** | Traces, metrics, logs with one SDK and one collector | §3, §4 | None |
| **W3C Trace Context** | `traceparent` / `tracestate` propagation | §5 | **Extended**: the estate also propagates its own `correlation_id` (`API-09`), and §5.2 explains why both exist |
| **Google SRE** SLO practice | SLI, SLO, error budget, **multi-window multi-burn-rate** alerting | §7, §8.2 | None |
| **USE** (Gregg) | Utilisation, saturation, errors — resources | §12.1 | None |
| **RED** | Rate, errors, duration — services | §12.1 | None |
| ISO/IEC 25010 | Reliability, performance efficiency | §7 | None |
| **`AR-013` `LW-01`** | Named fallback for AGPL/BSL components | §3.4 — **applied, and it finds a violation** | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| **Technology Stack §17** | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` | The stack diagram; **what is monitored, eight layers**; `OPS-03`, `OPS-05`; alert discipline |
| `02-05` §9 | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | The named components |
| **`PE-001` §9.1** | `./PE-001_*.md` | **The four availability targets reconciled by scope**, and `PE-001-F-04`'s window gap |
| `PE-006` §7 | `./PE-006_*.md` | Twelve scaling triggers requiring instrumentation |
| `PE-007` §13 | `./PE-007_*.md` | `FF-155` WAL lag, `FF-164` DNS TTL, drill instrumentation |
| **`AR-009`** §5.4 | `../02_Architecture_and_Design/AR-009_*.md` | **Outbox depth *and age*; age is the leading indicator** |
| `IN-001` §12 | `../04_Integration_and_API_Engineering/IN-001_*.md` | `OB-01`…`OB-07`; egress logging; `05-03` §7's integration thresholds |
| **`AUDIT-016` `AP-02`** | `../../project_content/_AUDIT/AUDIT-016_*.md` | **`NFR-090`/`-091`/`-092` mean two things each** |
| `AUDIT-017` `OP-04` | `../../project_content/_AUDIT/AUDIT-017_*.md` | Platform incident severity had three claimed owners and no owner |
| `RP-012` | `../../project_content/14_Reporting_Analytics_and_KPI/RP-012_*.md` | **Business** anomaly thresholds — the boundary |
| `DA-005` | `../03_Data_and_Information_Architecture/DA-005_*.md` | Classification and handling per state, **including in logs** |
| `SC-007` | `../05_Security_Privacy_and_Compliance/SC-007_*.md` | Residency; the quiet-copy prohibitions |
| `05-06` | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` | `NFR-006`, `-043`, `-045`, `-046`, `-048`, `-092` |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| `PGD-000` `PE-008` — platform observability undesigned | `PGD-000` | **Closed as a design** |
| **`AP-02` (critical)** — `NFR-090`/`-091`/`-092` each mean two different requirements | `AUDIT-016` | **Contributes.** §10.4 states which sense this document implements and **qualifies every citation**, per `AP-02`'s interim instruction. **Closes on renumbering by Enterprise Architecture** |
| **`PE-001-F-04`** — `NFR-046` and `NFR-048` state no measurement window | `PE-001` | **Closed by ruling** — §7.2 fixes the window per SLO; referred to `RQ-006` for the source correction |
| `OP-04` — platform incident severity had three claimed owners and no owner | `AUDIT-017` | §8.5 — one severity model, one owner |
| **`AR-013` `LW-01`** violation — Grafana `Adopt` with no named fallback | `AR-013` §6 | **§3.4 supplies the fallback**; raised as `PE-A-02` in `PE-003` and closed here |
| `OPS-03` — every alert has a runbook entry | Technology Stack §17.3 | §8.4; `FF-169` |
| `OPS-05` — every scheduled job reports success, failure and duration | Ibid. | §12.3 |
| `AR-009` §5.4 — outbox **age** is the leading indicator | `AR-009` | §12.3 |

---

## 3. The Signal Model

### 3.1 Three signals, three jobs

| Signal | Answers | Cardinality | Retention |
|---|---|---|---|
| **Metrics** | *"Is it healthy, and how much?"* | **Low** — bounded label sets | Long (§10.3) |
| **Logs** | *"What exactly happened in this case?"* | High | Short-to-medium |
| **Traces** | *"Where did this request spend its time, across which hops?"* | Very high — **sampled** | Short |

> **`PE-008-D-01`. Metrics drive alerts. Logs and traces explain them.** An alert on a log pattern is
> an alert on an unbounded, unaggregated signal; it fires late and cannot express a rate. **Every
> alert in §8 is metric-based**, and every alert links to the logs and traces that explain it.

### 3.2 The collection path

```
Odoo · Next.js · Flutter · 16 domain services · CD-233
        │  OpenTelemetry SDK — traces, metrics, logs; one correlation id
        ▼
   OpenTelemetry Collector          ← the ONLY egress point for telemetry
        │  processors: PII redaction (§10.2) · sampling (§6.3) · attribute enrichment
        │
        ├──► Metrics store   ──► alert rules, SLOs, error budgets
        ├──► Log store       ──► structured logs, personal data redacted BEFORE storage
        └──► Trace store     ──► distributed traces, sampled
                 │
                 ▼
              Dashboards ──► on-call routing (§8.3)
```

| # | Rule |
|---|---|
| **CP-01** | **Every component emits through the OpenTelemetry SDK.** No component writes to a store directly |
| **CP-02** | **The collector is the only place redaction, sampling and enrichment happen** — one place to audit (§10.2) |
| **CP-03** | The collector runs **per cluster**, including in `BD-R` — §11 |
| **CP-04** | **Collector failure must not fail the application.** Telemetry export is asynchronous and bounded; a full buffer drops telemetry, never blocks a request |
| **CP-05** | **Telemetry loss is itself monitored.** `FF-165` |

> **`CP-04` is the rule that gets omitted and causes the outage it was meant to observe.** A
> synchronous exporter with a blocking queue turns a monitoring outage into an application outage —
> and it does so under load, when telemetry volume is highest.

### 3.3 Components

`02-05` §9 and Technology Stack §17.1 name OpenTelemetry, **Prometheus, Loki, Tempo and Grafana**.

| Concern | Component | Licence |
|---|---|---|
| Instrumentation | **OpenTelemetry SDK + Collector** | Apache-2.0 |
| Metrics | **Prometheus** | Apache-2.0 |
| Logs | **Loki** | **AGPL-3** |
| Traces | **Tempo** | **AGPL-3** |
| Dashboards, alerting | **Grafana** | **AGPL-3** |
| Alert delivery | **Novu** (Technology Stack §17.1) | — |

### 3.4 The licence position — and `AR-013`'s own violation

`AR-013` `LW-01`: *"Every AGPL, BSL, TSL or fair-code component has a **named fallback** on the
radar. **A component with no fallback may not be `Adopt`.**"*

`AR-013` §6 records Grafana as **AGPL-3, `Adopt`**, with the fallback cell reading
**"— (observability is replaceable but disruptive)"**.

> **`PE-008-F-01`. That is not a named fallback, and `LW-01` says a component without one may not be
> `Adopt`. Loki and Tempo are AGPL-3 on the same terms and are not on the radar at all.** The
> estate's entire observability stack is in violation of its own licence rule.

**Closed here:**

| Component | Licence | **Named fallback** | Obligation |
|---|---|---|---|
| **Grafana** | AGPL-3 | **Perses** (CNCF, Apache-2.0) for dashboards; alerting falls back to Prometheus Alertmanager | Deployed **unmodified** (`LW-05`) |
| **Loki** | AGPL-3 | **OpenSearch** (Apache-2.0) or Elasticsearch-compatible store | Deployed unmodified |
| **Tempo** | AGPL-3 | **Jaeger** (CNCF, Apache-2.0) | Deployed unmodified |
| Prometheus | Apache-2.0 | — | Permissive |
| OpenTelemetry | Apache-2.0 | — | **The reason the fallbacks are cheap** |

> **`PE-008-D-02`. OpenTelemetry is the estate's insurance against every one of those fallbacks.**
> Because instrumentation is vendor-neutral and the collector is the only exporter, **replacing a
> backend is a collector configuration change, not a re-instrumentation of 67 modules.** This is the
> same argument `AR-009` §6.2 makes for the shared consumer library and the Redis→Redpanda migration.
>
> **`LW-05` applies**: all four AGPL components are deployed **unmodified**. A modification would
> require an ADR and a publication commitment. **Referred to `AR-013` for radar correction** —
> `PE-A-06`.

---

## 4. Instrumentation Obligations

| # | Obligation | Applies to |
|---|---|---|
| **IO-01** | Emit **RED** metrics — rate, errors, duration — with **bounded label cardinality** | Every service |
| **IO-02** | Emit **structured JSON logs to stdout/stderr** (`PE-005` `IM-09`), never to a file |
| **IO-03** | **Propagate trace context and `correlation_id`** on every outbound call, event and job (§5) |
| **IO-04** | **Never log a value classified `S3`, `personal` or `residency_restricted`** (§10.1) |
| **IO-05** | Expose **liveness and readiness** (`PE-005` §10) and emit their outcomes |
| **IO-06** | **Every scheduled job reports start, success/failure and duration** — `OPS-05`; §12.3 |
| **IO-07** | **Every event published and consumed emits a metric** carrying `event_type` and outcome (`AR-009`) |
| **IO-08** | **Every outbound external call emits a metric and an egress log entry** naming the counterparty and the field set sent (`IN-001` `OB-02`) |
| **IO-09** | Emit a **build identifier** — commit and artefact digest — as a resource attribute, so a metric is attributable to a release |
| **IO-10** | **No alert-relevant signal exists only in a log.** If it drives an alert, it is a metric (`PE-008-D-01`) |

> **`IO-01`'s cardinality constraint is a cost and a reliability control.** A metric labelled with a
> service-order id has 5 million label values a year. **Unbounded cardinality is the most common way
> a metrics store is destroyed by its own users**, and `FF-166` bounds it.

---

## 5. Correlation

### 5.1 The requirement

`API-09`: every response carries a `correlation_id`. Technology Stack §17.1: *"One correlation id
spans the whole journey — injected by Kong, propagated through Odoo, the domain services, the event
bus and back into the portal response."* `AR-009` §4: the event envelope carries `correlation_id`
**and** `causation_id`.

### 5.2 Two identifiers, deliberately

| Identifier | Standard | Scope | Purpose |
|---|---|---|---|
| **`traceparent`** | W3C Trace Context | One trace, spans and their parents | **Tooling** — the trace store reconstructs the call graph |
| **`correlation_id`** | The estate's own (`API-09`) | **The whole business journey**, potentially across days | **Humans and business flows** — a support engineer takes it from a user's error message |

> **They are not redundant.** A W3C trace ends when the request ends. **A `correlation_id` survives
> into an event, into a consumer's transaction hours later, into a batch file the next morning** —
> `AR-009`'s `causation_id` chains those hops. A trace cannot express *"the invoice raised overnight
> from the order this customer placed on Tuesday"*; a correlation id can.

### 5.3 Propagation rules

| # | Rule |
|---|---|
| **CR-01** | **Kong injects `correlation_id` at ingress** if absent, and `traceparent` per W3C |
| **CR-02** | Both propagate across **every internal HTTP call** |
| **CR-03** | Both enter the **event envelope** (`AR-009` §4) and are restored by the consumer |
| **CR-04** | Both propagate into **scheduled jobs** — a job triggered by an event carries the causing event's ids |
| **CR-05** | **Both appear in every log line** as structured fields |
| **CR-06** | Both cross the **`CD-233` residency boundary** — §11.2 |
| **CR-07** | **Both are returned to the caller** — `correlation_id` in the response body and the `X-Correlation-Id` header (`IN-002` §5.3) |
| **CR-08** | **An error body without a `correlation_id` fails `FF-167`** |

### 5.4 What correlation buys

> Technology Stack §17.1: *"A support engineer takes a correlation id from a user's error message and
> sees the entire request path."* **That is only true if `CR-04` and `CR-06` hold** — the two hops
> most often dropped. A journey that traverses a scheduled job or the residency service and loses
> correlation there is a journey that goes dark at exactly the point where diagnosis is hardest.

---

## 6. Sampling

| # | Rule |
|---|---|
| **SM-01** | **Metrics are never sampled.** They are aggregates |
| **SM-02** | **Logs are not sampled** at `WARN` and above; `INFO` and `DEBUG` may be, with the rate recorded |
| **SM-03** | **Traces are sampled**, at the collector (`CP-02`) |
| **SM-04** | **Tail-based sampling**: keep **every error trace and every slow trace**, sample the rest |
| **SM-05** | **Sample the whole trace or none of it.** Partial traces are worse than absent ones |
| **SM-06** | The sampling rate is **configuration** (`PE-009`), raisable during an incident without a deployment |
| **SM-07** | **Money paths, `Z4` access and authentication are never sampled out** — §6.1 |

### 6.1 The never-sampled set

| Path | Why |
|---|---|
| Payment initiation and confirmation (`IN-007`) | Money; and `unknown`-state resolution depends on the trace |
| **Every `CD-233` call** | `Z4` access is separately logged per read (`AR-001` §8.1) and is a regulatory record |
| Authentication and authorisation | Security investigation |
| Failed requests, any path | The reason to have traces |
| Requests exceeding their `x-endpoint-class` p99 | The reason to have traces |

---

## 7. Service Level Objectives

### 7.1 Why the estate does not have SLOs yet

`05-06` states four availability **targets**. A target is not an SLO. An SLO requires a **service
level indicator** — a precise ratio of good events to valid events — **a window**, and an **error
budget** with a stated consequence.

`PE-001` §9.1 reconciled the four by scope; `PE-001-F-04` recorded that two state no window.

### 7.2 The ruling

> **Ruling `PE-008-D-03`. Every SLO states a scope, an SLI, a window and an error budget. The two
> targets with no stated window are ruled to be 24×7, and the ruling is referred to `RQ-006` for
> correction at source.**

| SLO | Scope | SLI | Objective | **Window** | Error budget / 30 d |
|---|---|---|---|---|---|
| **`SLO-01`** | System, **business hours 09:00–22:00 BST** | Successful requests ÷ valid requests | **99.9%** (`NFR-006`) | Business hours only | ≈ **23 min** of business-hours time |
| **`SLO-02`** | System, 24×7 | As above | **99.7%** (`NFR-045`) | 24×7 | ≈ **2 h 10 m** |
| **`SLO-03`** | **Customer portal** | Successful portal requests ÷ valid | **99.9%** (`NFR-046`) | **24×7 — ruled** | ≈ **43 min** |
| **`SLO-04`** | **Payment path** | Successful payment operations ÷ valid | **99.95%** (`NFR-048`) | **24×7 — ruled** | ≈ **22 min** |
| **`SLO-05`** | Event delivery | Events consumed within 5 s ÷ published | **95%** (`NFR-043`) | 24×7 | — |
| **`SLO-06`** | ERP screen latency | Requests ≤ 2 s ÷ valid | **95%** (`NFR-001`) | Business hours | — |
| **`SLO-07`** | API latency | Requests ≤ 400 ms ÷ valid | **95%** (`NFR-002`) | 24×7 | — |
| **`SLO-08`** | **`Z4` availability** | `CD-233` successful ÷ attempted | **Stated separately** (`SC-007` §9.5) | 24×7 | §7.5 |

### 7.3 The two that are not achievable by infrastructure

| SLO | Constraint |
|---|---|
| **`SLO-04`** payment path | **`IN-007` §9.3: `INT-003` is the only card acquirer.** Infrastructure can deliver 99.95% of the platform; it cannot deliver 99.95% of a single-supplier external dependency. **The SLI must therefore exclude counterparty-attributable failures, and the exclusion must be visible on the dashboard** — otherwise a green SLO conceals an unavailable card path |
| **`SLO-08`** `Z4` | **Unbounded RTO until `PE-007` §7.5 is decided.** Reported separately, never folded into `SLO-01` or `SLO-02` |

### 7.4 What counts as a "valid event"

The definition that decides whether an SLO is honest:

| # | Rule |
|---|---|
| **VE-01** | A **valid** request is one the estate is responsible for serving. `429` rate-limited and `401` unauthenticated requests are **valid and successful** — the system worked |
| **VE-02** | A `5xx` is a **failure**. A `4xx` is **not**, except `500`-class errors misreported as `4xx` |
| **VE-03** | **`503 dependency.*` from a counterparty outage is attributed to the counterparty** and excluded from `SLO-04`'s numerator — **and shown as a separate series** (`§7.3`) |
| **VE-04** | Synthetic monitoring requests are **excluded** from SLIs and reported separately |
| **VE-05** | **Requests during a declared and announced maintenance window (`NFR-049`) are excluded** — but the window is capped at 4 h/month, so this cannot be abused |

> **`VE-03` is the rule that will be argued about.** Excluding counterparty failures makes the SLO
> measure *our* reliability, which is what an error budget should govern. **Showing them separately
> is what stops that becoming an excuse** — the customer experienced an outage either way, and
> `IN-007` §9.3's procurement question is driven by that second series.

### 7.5 `Z4`'s separate line

| # | Rule |
|---|---|
| **Z4-01** | **`SLO-08` is reported separately on every availability report** (`SC-007` §9.5) |
| **Z4-02** | It is **never folded into** `SLO-01` or `SLO-02` — a green estate SLO would conceal an unbounded `Z4` RTO |
| **Z4-03** | **`HC-01`'s monthly DR RAG report carries it** (`PE-007` §11.4) |
| **Z4-04** | Degraded operation (`SC-007` §9.2) is a **distinct state** on the dashboard, not an outage and not normal |

---

## 8. Alerting

### 8.1 The principle

> **`PE-008-D-04`. Alerts fire on user-visible harm or imminent harm, not on resource numbers.**

A CPU alert at 80% pages someone about a number. **An SLO burn-rate alert pages someone because
users are experiencing failures fast enough to exhaust the month's budget** — which is a fact about
the service, not about a machine.

Resource signals remain, as **ticket-level** signals feeding `PE-006`'s scaling triggers.

### 8.2 Multi-window, multi-burn-rate

Adopted from Google SRE practice. **Burn rate** = current error rate ÷ the SLO's tolerable error
rate. A 99.9% SLO tolerates 0.1%; erroring at 1.4% is a burn rate of 14.

| Tier | Burn rate | Long window | Short window | Budget consumed | Action |
|---|---:|---|---|---|---|
| **Fast** | **14.4×** | 1 h | 5 min | 2% | **Page** |
| **Medium** | **6×** | 6 h | 30 min | 5% | **Page** |
| **Slow** | **1×** | 3 d | 6 h | 10% | **Ticket** |

| # | Rule |
|---|---|
| **AL-01** | **Both windows must exceed the threshold** for the alert to fire — the short window resets the alert quickly and suppresses false positives |
| **AL-02** | **Only fast and medium burn page.** Slow burn is a ticket |
| **AL-03** | **Only `Sev1` pages out of hours** (Technology Stack §17.3) |
| **AL-04** | Burn-rate alerts are defined **per SLO**, not per component |

> **This replaces threshold alerting on error rate, and the difference is the point.** A fixed "error
> rate > 2%" alert fires identically whether the budget is fresh or exhausted. **A burn-rate alert
> knows how much budget remains**, so it escalates when it matters and stays quiet when a brief blip
> costs nothing.

### 8.3 Routing

| # | Rule |
|---|---|
| **RT-01** | **Alerts route to the owning role, never to a shared inbox** (Technology Stack §17.3), via Grafana → Novu |
| **RT-02** | Every alert carries: what broke, which SLO, budget remaining, **a runbook link**, and a correlation id or dashboard link |
| **RT-03** | **Severity is one model, one owner** — §8.5 |
| **RT-04** | **Alert delivery is itself monitored.** A paging system that has not delivered in a week is tested, not trusted. `FF-168` |

### 8.4 Alert discipline

| # | Rule | Source |
|---|---|---|
| **AD-01** | **Every alert has a runbook entry. Alerts without an action are removed** | `OPS-03`; `FF-169` |
| **AD-02** | **Alert volume is reviewed at every wave gate.** A persistently firing alert is a defect in the alert or the system, **never background noise** | Technology Stack §17.3 |
| **AD-03** | **An alert that has never fired is reviewed** — either it is redundant or it is not wired |
| **AD-04** | **An alert acknowledged and not acted on three times is deleted or fixed** |
| **AD-05** | **Silencing requires a reason and an expiry** — an indefinite silence is a deleted alert with an alibi |

### 8.5 Severity — closing `OP-04`

`AUDIT-017` `OP-04`: *"Platform incident severity had three claimed owners and no owner."*

> **`PE-008-D-05`. One severity model, defined here, owned by the Head of Service.**

| Severity | Definition | Pages | Example |
|---|---|:--:|---|
| **`Sev1`** | **Business-stopping** — a P0 user journey unavailable, or fast-burn on `SLO-01`/`SLO-04` | **Yes, 24×7** | Payment path down; ERP unavailable in business hours |
| **`Sev2`** | **Degraded** — a journey impaired, or medium-burn | Business hours | Portal slow; one integration failing over |
| **`Sev3`** | **Informational** — a ticket | No | Slow-burn budget consumption; capacity trigger |

| # | Rule |
|---|---|
| **SV-01** | **The model is defined once, here, and referenced by `SV-*` and `OP-*`** — not redefined |
| **SV-02** | **Business severity (`RP-012`) and platform severity are the same three levels**, so an incident does not change severity when it changes hands |
| **SV-03** | **`Z4` unavailability is `Sev1`** — it gates every `T5` read (`PE-006` §7.2) |

---

## 9. Dashboards

| Audience | Dashboard | Contents |
|---|---|---|
| **On-call** | **Service health** | The eight SLOs, **budget remaining**, active alerts, recent deploys |
| Platform | Infrastructure | `PE-006` §7's twelve triggers, `USE` per tier, cluster capacity |
| **Integration** | Integration health | 47 integrations: availability, error rate, latency, **breaker state**, queue depth, DLQ, credential expiry (`IN-001` §12, `05-03` §7) |
| Data | Data platform | Replication lag, connection saturation, **outbox depth and age**, slow queries, partition health |
| **Release** | Deployment | In-flight deploys, artefact digests per environment, **`dr` digest parity** (`PE-004` `FF-134`), rollback readiness |
| **DR** | Continuity | **WAL archive lag, restore-test results, drill status, `BKP-3` verification** (`PE-007` §13) |
| Security | Security | Failed authentications, privilege changes, **`T5` access**, anomalous export (Technology Stack §17.2) |
| **Executive** | Availability | SLOs by month, **`Z4` on its own line**, incident count, cost per transaction (`PE-006` §8.3) |

| # | Rule |
|---|---|
| **DB-01** | **Every dashboard has an audience and a question it answers.** A dashboard that answers no question is deleted |
| **DB-02** | Dashboards are **code**, versioned and deployed (`PE-003`) |
| **DB-03** | **The on-call dashboard fits one screen.** A dashboard requiring scrolling during an incident is a dashboard nobody reads during an incident |
| **DB-04** | **Every environment banner** (`PE-002` `LC-06`) appears on its dashboards too |

---

## 10. Logs, Personal Data and Retention

### 10.1 What may never be logged

`DA-005` classifies; this section applies it to logs, where the estate's most common accidental
disclosure occurs.

| # | Rule |
|---|---|
| **LG-01** | **No `residency_restricted` value ever appears in a log, in any region.** NID, passport, TIN, biometric templates, recovered data (`NFR-086c`, `AR-009` P-03) |
| **LG-02** | **No secret, token, signature, password or key** (`NFR-062`, `IN-001` `OB-07`, `IN-006` `FF-82`) |
| **LG-03** | **No card data** — `PCI-05` (`IN-007` §4.2) |
| **LG-04** | **No full personal record.** An identifier is logged; the record is not |
| **LG-05** | Free-text customer input is **not logged at `INFO`** — it may contain anything |
| **LG-06** | **Request and response bodies are not logged by default.** Where needed for diagnosis, they are redacted at the collector and time-boxed |

### 10.2 Redaction at the collector

| # | Rule |
|---|---|
| **RD-01** | **Redaction runs in the collector, before any store receives the log** (`CP-02`) |
| **RD-02** | It is **pattern-based and field-based**: known-sensitive field names are dropped; value patterns — NID, TIN, card, phone, token shapes — are masked |
| **RD-03** | **Redaction failing closed**: if the processor errors, the log is **dropped**, not forwarded |
| **RD-04** | **The redaction rule set is code**, reviewed, tested with fixtures that assert masking |
| **RD-05** | **A scanner samples the log store for unredacted patterns**; a hit is a **security incident** (`FF-170`) |

> **`RD-03` is deliberately drastic and it is correct.** A dropped log is a diagnostic loss. **A
> forwarded unredacted log is a personal-data disclosure into a system with different access
> controls, longer retention and, potentially, a different jurisdiction.**

### 10.3 Retention

| Signal | Hot | Total | Basis |
|---|---|---|---|
| Metrics — high resolution | 15 days | — | Incident diagnosis |
| Metrics — downsampled | — | **13 months** | Year-on-year comparison and capacity |
| **SLO / error-budget series** | — | **13 months** | §7's monthly reporting |
| Logs — application | 14 days | **35 days** | Aligns with `PE-007`'s backup window |
| **Logs — audit and access** | 35 days | **Per `SC-008`'s obligation period** | Statutory |
| **`Z4` per-read access log** | 35 days | **Per `SC-008`; in country** | `AR-001` §8.1; §11.3 |
| Traces | 7 days | 14 days | Volume; tail-sampled |
| **Egress logs** (`IN-001` `OB-02`) | 35 days | **Per `AP-012`** | Disclosure record |

| # | Rule |
|---|---|
| **RN-01** | **Log retention is a processing decision**, in the DPIA (`SC-003`), not a storage default |
| **RN-02** | **Erasure does not reach logs** — logs hold identifiers, not records (`LG-04`), and the identifier is the processing record `NFR-095` requires. **This is the `AR-009` §8.4 tension, resolved the same way** |
| **RN-03** | **`Z4` access logs never leave Bangladesh** — §11.3 |

### 10.4 `NFR-092` — the `AP-02` collision

**`AUDIT-016` `AP-02` (critical):** `05-06` uses `NFR-090`, `NFR-091` and `NFR-092` for **two
different requirements each**:

| ID | `05-06` §6.3 — PDPA 2026 | `05-06` §7 — Maintainability & Operability |
|---|---|---|
| **`NFR-092`** | Issue a **transparency notice** before or during processing | **Distributed tracing across all services with a single correlation id** |

> **`PE-008-F-02`. This document implements `05-06` §7's `NFR-092` — distributed tracing — and every
> citation of it here is qualified with its section**, per `AP-02`'s interim instruction: *"Until
> renumbered, every citation must name its section."*
>
> **The collision is not this document's to resolve.** `AP-02`'s remediation instruction assigns it
> to Enterprise Architecture: renumber the **PDPA** block to `NFR-102`…`NFR-104`, because *"`05-06`
> §7's `NFR-090`…`NFR-092` are older and more widely cited — including by `M28` itself — so the PDPA
> block is the one that moves."* **Recorded as still open at 2026-08-19.**

---

## 11. Observing Across the Residency Boundary

### 11.1 The problem

Observability collects data about what the system did. **`Z4` holds data whose collection is
regulated.** A telemetry pipeline that exports `Z4` traces to a regional store is a cross-border
transfer wearing an operational hat.

### 11.2 The design

| # | Rule |
|---|---|
| **RB-01** | **`BD-R` runs its own collector** (`CP-03`) and its own metric, log and trace stores |
| **RB-02** | **`Z4` logs and traces do not leave Bangladesh.** `FF-171` |
| **RB-03** | **Metrics may cross** — aggregate counters and latencies carry no personal data (`IO-01`'s cardinality bound is what guarantees this) |
| **RB-04** | **`correlation_id` and `traceparent` cross** (`CR-06`) — they are opaque identifiers, not personal data — **so a journey can be followed across the boundary without the content crossing it** |
| **RB-05** | A regional operator investigating a `Z4`-involved journey sees **the shape and timing of the `CD-233` call, and not its content** |
| **RB-06** | Where the content is needed, an **in-country operator** examines the in-country store, under `Z4` access rules |

> **`RB-04` is the design's key move.** Because the correlation id is opaque and carries no personal
> data, **it can cross the boundary that its associated content cannot** — which preserves the
> single most valuable diagnostic capability (`CR-01`…`CR-08`) without breaching `SC-007`'s quiet-copy
> prohibitions.

### 11.3 The `Z4` access log

| # | Rule |
|---|---|
| **AC-01** | **Every `Z4` read is logged** — who, when, which field, which subject, under which lawful basis (`AR-001` §8.1) |
| **AC-02** | **The log is held in country** and retained per `SC-008` |
| **AC-03** | **It is itself `T5`** — reading the access log is a privileged, logged act |
| **AC-04** | **Anomalous access patterns alert** — volume, unusual hours, unusual actor (Technology Stack §17.2) |

---

## 12. What Is Monitored

### 12.1 Method per layer

| Layer | Method | Signals |
|---|---|---|
| **Services** | **RED** | Rate, errors, duration per endpoint class (`IN-002` `x-endpoint-class`) |
| **Resources** | **USE** | Utilisation, saturation, errors per CPU, memory, disk, network, connection pool |
| **Business** | `RP-012` | Volume deviation from expected band — **not this document's** |

### 12.2 The eight layers

Technology Stack §17.2 lists them. This document adds the SLO and trigger linkage:

| Layer | Key signals | Threshold | Feeds |
|---|---|---|---|
| Business | Orders, jobs, invoices, payments, SLA breaches | Deviation from band | **`RP-012`** |
| **Integration** | Availability, error rate, latency p95, queue depth, DLQ, webhook failures, **credential expiry** | `05-03` §7; **credential expiry 30 and 7 days** | `IN-001` §12; `SLO-04` |
| Application | Request rate, errors, latency percentiles, **worker saturation**, job success | NFR targets | `SLO-01`, `SLO-06`, `SLO-07`; `PE-006` §7.2 |
| **Data** | **Replication lag**, connection saturation, slow queries, bloat, partition health | Lag > 30 s; **connections > 70%** | `PE-006` §7.2; `PE-007` `FF-155` |
| Infrastructure | CPU, memory, disk, network, container restarts | `USE` | `PE-006` |
| Security | Failed auth, privilege changes, **`T5` access**, anomalous export | Any privilege escalation; any anomalous export | `SC-009` |
| **Offline sync** | Success rate, duration, conflict rate, queue depth per device | **Any sync failure — target is zero** | `AR-010` |
| Cost | Spend vs wave budget; third-party consumption | **Monthly variance > 15%** | `PE-006` §8.4 |

### 12.3 Signals the estate has specified and never instrumented

| Signal | Requirement | Why it matters |
|---|---|---|
| **Outbox depth *and age*** | `AR-009` §5.4 | **"Age is the leading indicator; depth alone hides a stuck partition"** |
| **Scheduled job success, failure and duration** | `OPS-05` | *"A job that fails silently is a defect"* — 60 automations |
| **`CD-233` latency** | `PE-001` `Q-07` | **On the critical path of every `T5` read** |
| **WAL archive lag** | `PE-007` `FF-155` | **The RPO measurement** — `NFR-007` is measured here, not asserted |
| **Telemetry loss** | `CP-05` | The observability system's own health |
| **`dr` digest parity** | `PE-004` `FF-134` | A standby running last month's artefact |
| **Event delivery latency** | `NFR-043` | `SLO-05` |

> **`PE-008-F-03`. Seven signals are required by name in existing documents and instrumented in
> none.** They are not exotic; each is a counter or a gauge. **They are absent because nobody owned
> platform observability**, which is precisely `PGD-000`'s statement of why this document exists.

### 12.4 The security interface

| # | Position |
|---|---|
| **Wazuh** (`INT-029`) is the host and file-integrity detection layer; `SC-009` owns it |
| **This document routes security signals to the same alerting fabric**, so an on-call engineer sees one alert stream |
| **Security incident response is `SC-008`/`SV-*`'s**, not this document's |
| **Audit logs are immutable and separately retained** (§10.3) |

### 12.5 The business interface

| # | Position |
|---|---|
| **`RP-012` owns business anomaly thresholds** — order volume, payment success, SLA breach rates |
| **This document owns platform signals** and provides the fabric `RP-012`'s alerts are delivered on |
| **Severity is shared** (`SV-02`), so an incident does not change severity when it changes hands |
| A business anomaly with a platform cause is **one incident**, correlated by `correlation_id` |

---

## 13. Fitness Functions

Allocation confirmed by enumerating every `FF-nn` definition across all authored categories at
**2026-08-19 01:45 (+06)**, per `PGD-AUDIT-007` `PGD-A7-01`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-165** | **Telemetry loss is measured and within budget**; no component is silently not reporting | All | Continuous | **Alert** |
| **FF-166** | **No metric exceeds its cardinality budget** | All metrics | Continuous | **Alert** → block on repeat |
| **FF-167** | **Every error response carries a `correlation_id`**, and it propagates across HTTP, events and jobs | All | CI + runtime sample | **Fail** |
| **FF-168** | **Alert delivery is verified** end to end at least weekly | Alerting | Weekly | **Fail** |
| **FF-169** | **Every alert rule links to a runbook entry** (`OPS-03`) | All rules | CI on rule definitions | **Fail** |
| **FF-170** | **A sampling scan of the log store finds no unredacted sensitive pattern** | Log store | Daily | **Security incident** |
| **FF-171** | **No `Z4` log or trace exists in a regional store** | Both stores | Daily | **Fail** |
| **FF-172** | **Every SLO in §7.2 has a live SLI, a burn-rate alert and a budget series** | 8 SLOs | Wave gate | **Fail** |
| **FF-173** | **The seven signals in §12.3 are instrumented and reporting** | 7 | Wave gate | **Fail** |
| **FF-174** | **Every AGPL observability component is deployed unmodified** and carries a named fallback on `AR-013`'s radar | 4 components | Wave gate | **Fail** |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `PE-008-D-01` | What drives alerts | Logs · **metrics** · traces | **Metrics** | A log-pattern alert is unbounded, unaggregated, late, and cannot express a rate | `IO-10`; every §8 alert is metric-based |
| `PE-008-D-02` | Vendor neutrality | Native agents per backend · **OpenTelemetry everywhere** | **OpenTelemetry** | It makes every AGPL fallback a collector configuration change rather than re-instrumenting 67 modules | §3.4; the same argument as `AR-009` §6.2 |
| `PE-008-D-03` | SLO definition | Carry the four NFR targets · **eight SLOs with SLI, window and error budget** | **Eight SLOs** | A target without a window and an SLI is not measurable; two of the four had no window | §7.2; referred to `RQ-006`; closes `PE-001-F-04` |
| `PE-008-D-04` | Alert philosophy | Resource thresholds · **SLO burn rate**, resources as tickets | **Burn rate** | A fixed error-rate threshold fires identically whether the budget is fresh or exhausted | §8.2; three tiers |
| `PE-008-D-05` | Severity ownership | Three claimants · **one model, Head of Service** | **One model** | `OP-04` — three claimed owners and no owner | §8.5; shared with `RP-012` |
| `PE-008-D-06` | Redaction failure | Forward and flag · **drop** | **Drop** | A forwarded unredacted log is a disclosure into a system with different controls and possibly a different jurisdiction | `RD-03` |
| `PE-008-D-07` | Cross-boundary telemetry | Export `Z4` telemetry regionally · **`Z4` stores in country, ids cross, content does not** | **Ids cross** | The correlation id is opaque and carries no personal data, so diagnosis survives the boundary the content cannot cross | `RB-01`…`RB-06`; `FF-171` |
| `PE-008-D-08` | `SLO-04` counterparty failures | Include · **exclude from the numerator, show as a separate series** | **Exclude and show** | The error budget should govern *our* reliability; the separate series stops that becoming an excuse | `VE-03`; feeds `IN-007` §9.3 |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Does `RQ-006` accept the `SLO-03`/`SLO-04` window ruling**, and correct `NFR-046`/`NFR-048` at source? (`PE-001-F-04`) | `RQ-006` owner | **W1** | §7.2, `FF-172` |
| **Q-02** | **Is `AP-02` renumbering executed?** `NFR-092` means two different things and this document implements one of them | Enterprise Architecture | **W1** | §10.4, every `NFR-092` citation estate-wide |
| **Q-03** | **Does `AR-013` accept the named fallbacks** for Grafana, Loki and Tempo, and add Loki/Tempo to the radar? (`PE-008-F-01`) | Design Authority | **W1** | `LW-01` compliance, `FF-174` |
| **Q-04** | **Who owns the error-budget policy** — what happens when a budget is exhausted? §7 defines budgets; **the consequence is a delivery-governance decision** | CTO + Head of Service + `GV-009` | **W2** | §8.2's usefulness |
| **Q-05** | Is the **`CD-233` latency budget** defined? Every `T5` read traverses it (`PE-001` `Q-07`) | Chief Architect | **W1** | `SLO-08`, §12.3 |
| **Q-06** | Who operates the **in-country observability stores** (§11.2), and are they in `PE-006`'s cost model? | Platform Engineering Lead | **W1** | `BD-R` sizing |
| Q-07 | Is 13-month metric retention affordable at the estate's cardinality, or does it need further downsampling? | Platform Engineering Lead | W2 | §10.3 |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The three signals have distinct roles, and **alerts are metric-based** | §3.1, `PE-008-D-01` |
| AC-02 | The collection path has **one redaction and sampling point**, and cannot fail the application | §3.2, `CP-02`, `CP-04` |
| AC-03 | **The AGPL licence position is resolved with named fallbacks**, closing `AR-013`'s own violation | §3.4, `PE-008-F-01` |
| AC-04 | Correlation is specified across **HTTP, events, jobs and the residency boundary** | §5.3 |
| AC-05 | **Four availability targets become eight SLOs** with SLI, window and error budget | §7.2, `PE-008-D-03` |
| AC-06 | The two SLOs infrastructure cannot deliver alone are named | §7.3 |
| AC-07 | "Valid event" is defined, including the counterparty-exclusion rule and its safeguard | §7.4, `VE-03` |
| AC-08 | Alerting is **multi-window multi-burn-rate**, with only fast and medium paging | §8.2 |
| AC-09 | **One severity model with one owner**, closing `OP-04` | §8.5 |
| AC-10 | **What may never be logged** is stated, and redaction **fails closed** | §10.1, `RD-03` |
| AC-11 | **Telemetry respects the residency boundary** while preserving cross-boundary diagnosis | §11.2, `PE-008-D-07` |
| AC-12 | **The seven specified-but-uninstrumented signals are named** | §12.3, `PE-008-F-03` |

**Definition of done.** Complete when every criterion is met, **Q-01…Q-03 are answered**,
`FF-165`…`FF-174` are enabled, all eight SLOs have live SLIs and burn-rate alerts, and `PGD-000`'s
`PE-008` row carries a fresh enumeration timestamp. **`AP-02` closes only on Enterprise
Architecture's renumbering — this document qualifies its citations and cannot close it.**

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | Technology Stack §17 | The stack, the eight monitored layers, `OPS-03`, `OPS-05` |
| Upstream | **`PE-001`** §9.1 | The four availability targets, reconciled by scope; **`PE-001-F-04` closed here** |
| Upstream | **`PE-006`** §7 | Twelve scaling triggers requiring instrumentation |
| Upstream | **`PE-007`** §13 | WAL lag, restore tests, drills |
| Upstream | `AR-009` §5.4 | **Outbox depth and age** |
| Upstream | `DA-005`, `SC-007` | Classification; the residency boundary |
| Downstream | **`SV-*`** | Alerts, severity and the on-call interface |
| Downstream | `OP-007`…`OP-011` | `OPS-03`'s runbook per alert |
| Downstream | `RP-012` | Shares the fabric and the severity model |
| Downstream | `GV-009` | SLO attainment as wave-gate evidence |
| Downstream | **`AR-013`** | **`PE-A-06`** — radar correction for Grafana, Loki, Tempo |
| Downstream | `RQ-006` | `SLO-03`/`SLO-04` window correction |
| Lateral | `../../project_content/_AUDIT/AUDIT-016_*.md` `AP-02` | **The `NFR-092` collision, still open** |
| Lateral | `../../project_content/_AUDIT/AUDIT-017_*.md` `OP-04` | Severity ownership, closed by §8.5 |

---

## 18. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./PE-001_Infrastructure_and_Network_Architecture_Design.md`](./PE-001_Infrastructure_and_Network_Architecture_Design.md) ·
[`./PE-005_Containerisation_and_Orchestration_Design.md`](./PE-005_Containerisation_and_Orchestration_Design.md) ·
[`./PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md`](./PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) ·
[`./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md`](./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) ·
[`./PE-009_Configuration_and_Secrets_Management_Standard.md`](./PE-009_Configuration_and_Secrets_Management_Standard.md) ·
[`../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md`](../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md) ·
[`../02_Architecture_and_Design/AR-009_Event_Driven_Architecture_and_Messaging_Design.md`](../02_Architecture_and_Design/AR-009_Event_Driven_Architecture_and_Messaging_Design.md)

**Workspace**
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §17 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` §6.3, §7 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §7 ·
`../../project_content/_AUDIT/AUDIT-016_*.md` `AP-02` ·
`../../project_content/_AUDIT/AUDIT-017_*.md` `OP-04` ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-012_*.md`

**External sources**

| Source | What it establishes | Verified |
|---|---|---|
| **OpenTelemetry 1.x** | One SDK and collector for traces, metrics and logs; vendor-neutral export | 2026-08-19 |
| **W3C Trace Context** | `traceparent` / `tracestate` propagation | 2026-08-19 |
| **Google SRE Workbook — *Alerting on SLOs*** | Multi-window multi-burn-rate: **14.4× / 1 h page**, **6× / 6 h page**, **1× / 3 d ticket**, with short windows at 1/12 of the long | 2026-08-19 |
| Gregg — USE method; RED method | Resource and service signal models | 2026-08-19 |
| **Grafana, Loki, Tempo, Mimir licensing** | **Relicensed from Apache-2.0 to AGPLv3**; plugins and some libraries remain Apache | 2026-08-19 |
| **Perses (CNCF), Jaeger (CNCF), OpenSearch** | Apache-2.0 alternatives — **the named fallbacks** | 2026-08-19 |
| Prometheus | Apache-2.0 | 2026-08-19 |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Platform Engineering | Initial issue. **Converts four availability targets into eight SLOs** with SLI, window and error budget, ruling the two undefined windows and closing `PE-001-F-04`. Adopts **multi-window multi-burn-rate alerting** so alerts fire on user-visible harm rather than resource numbers. **Closes `OP-04`** with one severity model and one owner. **Finds and closes `AR-013`'s own `LW-01` violation** — Grafana `Adopt` with no named fallback, and Loki and Tempo absent from the radar entirely (`PE-008-F-01`). Designs telemetry across the residency boundary so **opaque identifiers cross and content does not** (`PE-008-D-07`). Names **seven signals required by existing documents and instrumented in none** (`PE-008-F-03`), and qualifies every `NFR-092` citation pending `AP-02`'s renumbering | *Pending — CTO, Head of Service; `GV-002` not constituted* |

---

*`PE-008` · Category 10 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
