---
id: FIX-ERP2-M48
module_id: M48
module_code: IOT
module_name: IoT Telemetry & Predictive Maintenance
category: F — Asset, Equipment & Facilities
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Data & Intelligence Squad
priority: P2
wave: W8
---

# M48 — IoT Telemetry & Predictive Maintenance
### Category F · Code `IOT` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M48 |
| **Module code** | `IOT` |
| **Category** | F — Asset, Equipment & Facilities |
| **Status** | ★ New in v2.1 — created from the telemetry, health-scoring and prediction scope removed from M17, and **reverses exclusion OOS-6 in the v1.0 BRD** ("AI-powered predictive maintenance engine — future Phase 7+ initiative") |
| **Priority** | **P2** |
| **Delivery wave** | W8 (Months 31–34) |
| **Business owner** | Chief Technology Officer |
| **System owner** | Data & Intelligence Squad |
| **Delivery layers** | L4 telemetry collector, MQTT broker and TimescaleDB · L5 custom stream registry, rule engine, health scoring and prescriptive routing |
| **Custom modules** | `cd_telemetry`, `cd_asset_health`, `cd_stream_registry`, `cd_alert_rules`, `cd_predictive_action` |
| **Requirement range** | FR-IOT-001 … FR-IOT-046 |
| **Requirement count** | **46** *(measured — supersedes the 28 estimate in `02-02`)* |
| **Effort estimate** | **26 person-weeks** *(measured — supersedes the 18 PW estimate)* |
| **Depends on** | **M62 Data Platform** · M17 Asset Registry · M26 AI/ML Services · M28 Integration · M29 Identity · M30 Platform Admin · M33 Party Master · M08 Contracts |
| **Depended on by** | M17, M45, M46, M47, M05, M13, M01, M02, M08, M23, M25, M26, M34 |

---

## 2. Purpose

M48 is **the platform that listens to machines**. It receives measurements from connected
assets — a customer's server reporting disk health, a rental laptop reporting battery cycles, a
branch generator reporting run hours and fuel level, a van reporting engine data, a monitored
endpoint on an MSP contract reporting temperature — stores them at a volume no transactional
database should carry, and converts them into three things the business can act on: **an
alert**, **a health score**, and **a predicted failure with a recommended intervention**.

It exists as a separate module for one reason, stated plainly in
`_CATEGORY_OVERVIEW.md` §4: telemetry is a fundamentally different data problem from a
registry. A registry holds thousands of rows per asset over its lifetime. Telemetry produces
millions of points per asset per year. Putting the second inside the first forces a
transactional system to carry a data-engineering workload, and the transactional system loses.

M48 is also the module that changes what 1000FiX sells. Every service the Company performs
today begins with something being broken. A platform that can say *this drive will fail within
30 days* converts a repair business into a maintenance business — and a maintenance business
schedules its own work.

### Why It Exists

Four capabilities depend on it, and none can be delivered anywhere else.

**Predictive maintenance was promised and then deferred.** The v1.0 BRD listed it as
out of scope (OOS-6, "future Phase 7+"), while the portal roadmap carried a Predictive
Maintenance Agent (IMPL-40) and the SOW referenced AI-powered predictive maintenance. The
capability was committed in one document and excluded in another. M48 resolves that by owning
it explicitly, late, and with the data platform it actually requires.

**Managed services need a monitoring platform.** M05 sells remote monitoring and managed
services to corporate clients. M05 declares telemetry ingestion for non-MSP assets out of scope
to M48 and states plainly that it shares the time-series platform. Two teams building two
time-series stacks is the failure this module prevents.

**Four asset populations already emit data.** Customer devices under MSP contract (M05), rental
assets (M13), Company vehicles through telematics (M46) and branch infrastructure such as
generators and UPS (M47) all produce signals today or will within the programme. Each would
otherwise build its own pipe.

**The transactional database must be protected.** `_CATEGORY_OVERVIEW.md` §9 names telemetry
volume overwhelming PostgreSQL as a **high-impact, platform-wide risk**. The mitigation is
architectural and must be enforced from the first point ingested: a time-series store with
compression and retention from day one, never in PostgreSQL transactional tables.

M48 is P2 and lands in Wave 8 — the last of Category F — because it needs the M62 data
platform, accumulated service history to train against, and enough connected assets to be worth
the build.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §4.2 OOS-6 | "AI-powered predictive maintenance engine — future Phase 7+ initiative" — **the exclusion this module reverses** |
| Scope Expansion Delta §M17 | "SOW §IoT Integration (phase 2); Portal roadmap IMPL-40 Predictive Maintenance Agent" — the commitment that conflicted with OOS-6 |
| Scope Expansion Delta §M26 | IMPL-40 Predictive Maintenance is listed against M26 AI/ML — M26 builds the model, M48 applies it |
| ERP BRD BR-CWM-002 | "Automatically generate scheduled maintenance work orders from active AMC/RAMC contracts" — condition-based triggering is the natural extension |
| ERP BRD BR-SRM-003 | Service order types include Preventive Maintenance — the order type a prediction produces |
| ERP BRD BR-BI-004 | "Service analytics: TAT, most common faults, parts consumption, rework" — fault patterns are the training signal |
| ERP BRD BR-BI-005 | Inventory analytics — predicted failures drive parts positioning |
| `_CATEGORY_OVERVIEW.md` §4 | Why IoT is its own module: rows versus points, PostgreSQL versus TimescaleDB hypertable, look up one asset versus aggregate across a fleet |
| `_CATEGORY_OVERVIEW.md` §5 | Telemetry ingestion and retention is M48, not M17; the failure prediction model is built by M26 and applied by M48 |
| `_CATEGORY_OVERVIEW.md` §7 | Telemetry ingestion reliability > 99.5%; predicted failures confirmed (precision) > 70%; proactive interventions > 500 per year |
| `_CATEGORY_OVERVIEW.md` §9 | Two risks owned here: telemetry volume overwhelming the transactional database; telemetry collected without customer consent |
| `M05` §3.2, §16.3 | M05 declares telemetry ingestion for non-MSP assets out of scope to M48, and notes the shared time-series platform |
| `M13` §3.2, §6 T-11 | M13 consumes derived telemetry signals; ISO 15143-3 (AEMP 2.0) interface shape |
| `02-05` §4 | TimescaleDB 2.x approved (Apache-2.0 features only) for M02, M05 and M17 time series; telemetry collector as a Go/Python standalone service; TD-13 decision recorded |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M48 sits between M62 (the data platform), M26 (the
> models) and five asset-owning modules. The boundary that matters most is the one that keeps
> telemetry out of PostgreSQL. Both sides of every boundary agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The stream registry: every telemetry source, bound to an asset identity that already exists |
| 2 | Device and gateway onboarding, provisioning, credentialing and decommissioning |
| 3 | **Protocol adapters**: MQTT (including Sparkplug B), OPC UA, HTTPS/REST, file batch, SNMP and agent push |
| 4 | Signal model: signal definition, unit of measure, expected range, sampling rate and quality flags |
| 5 | Unit normalisation and value validation at the edge of ingestion |
| 6 | **High-throughput ingestion into a time-series store**, with back-pressure and buffering |
| 7 | **Hypertable storage, compression, continuous aggregates and retention policy** — the volume control |
| 8 | Downsampling tiers and the rules governing what survives at each tier |
| 9 | Late, duplicate and out-of-order data handling |
| 10 | Edge and gateway buffering for intermittent connectivity |
| 11 | **Threshold and rule-based alerting** evaluated on the stream, with hysteresis and suppression |
| 12 | Alert lifecycle: raise, deduplicate, correlate, acknowledge, escalate, resolve, suppress |
| 13 | **Asset health scoring**: a composite index per asset from signals, faults and service history |
| 14 | **Failure prediction application**: scoring assets against models built by M26, with a confidence and a horizon |
| 15 | Remaining-useful-life estimation where the model and the signal support it |
| 16 | **Prescriptive routing**: converting a prediction into a proposed intervention with the parts and skills it needs |
| 17 | Prediction outcome tracking: was the predicted failure confirmed, and was the intervention effective |
| 18 | **Consent and privacy control**: what may be collected from a customer asset, disclosed and revocable |
| 19 | Telemetry access control, including customer visibility of their own asset data |
| 20 | Pipeline observability: ingestion reliability, device liveness, gap detection and lag monitoring |
| 21 | Telemetry analytics: fleet-level aggregation, cohort comparison and failure-pattern discovery |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Asset identity, ownership, custody and service history** | **M17** Device & Customer Asset Registry | A stream must bind to an asset that already exists. M48 never creates an asset identity |
| **Company tool and test equipment identity, calibration and custody** | **M45** Enterprise Asset & Test Equipment | M48 returns a condition signal for connected equipment; M45 decides what to do about it |
| **Vehicle identity, documents, servicing and cost** | **M46** Fleet & Vehicle Management | M48 ingests the telematics feed; M46 owns the vehicle and the telematics device as an asset |
| **The live technician position stream and dispatch use of it** | **M02** Field Service & Dispatch | M02 owns the dispatch consumption of position; M48 owns the ingestion pipe where the two share a feed |
| **Building-service asset register and facility maintenance** | **M47** Facility & Workplace | M48 measures the generator; M47 owns it and raises the work |
| **Model training, feature engineering, evaluation and MLOps** | **M26** AI/ML Services & Model Operations | **M26 builds; M48 applies.** This division is stated in `_CATEGORY_OVERVIEW.md` §5 and is not negotiable |
| **The data warehouse, lakehouse, ETL, data catalogue and governance** | **M62** Data Platform, Warehouse & Governance | M48 owns the operational time-series store; M62 owns the analytical platform and the long-term archive |
| **Business intelligence dashboards and report distribution** | **M25** Business Intelligence & Reporting | M48 exposes telemetry as a source; M25 presents it alongside everything else |
| **Managed-service contract, monitoring overlay, RMM agent and MSP ticketing** | **M05** Remote Support & Managed Services | M05 owns the client-facing service; M48 owns the platform beneath it |
| **Service order, work order and preventive maintenance execution** | **M01 / M31 / M02** | M48 proposes work; M01 creates and runs it |
| **Contract-driven maintenance entitlement and schedules** | **M08** Contract Lifecycle | Whether a customer is entitled to a proactive intervention is a contract question |
| **Plan-driven maintenance schedules for customer assets** | **M17** | M17 owns the plan; M48 supplies the condition trigger |
| **Spare parts availability and reservation for a predicted failure** | **M15** Inventory | M48 names the part likely to be needed; M15 answers whether it exists |
| **Customer notification and communication** | **M27** Contact Centre & Communications | M48 raises the event; M27 chooses the channel and the words |
| **Alert routing to on-call rotas and incident management for 1000FiX's own IT** | **M66** Internal IT Service Management | M66 monitors the ERP; M48 monitors assets |
| **Personal data, consent capture and preference management** | **M33 / M07** | Consent to collect from a device is recorded here; consent as a party attribute lives with the party |
| **Telemetry-derived billing, such as usage-based rental charges** | **M13 / M20** | M48 supplies the metered quantity; billing is a revenue function |

### 3.3 Shared Concepts

| Concept | M48's Role | Owning Module |
|---|---|---|
| Telemetry stream and point | **Owns** — the defining concept of this module | M48 |
| Time-series store (TimescaleDB hypertables) | **Owns** the operational store; M62 owns the analytical archive | M48 / M62 |
| Asset | References; every stream binds to one | M17 |
| Telematics device on a vehicle | Ingests from; M46 owns the device as an asset | M48 / M46 |
| Monitored endpoint on an MSP contract | Ingests from; M05 owns the monitoring overlay and the client relationship | M48 / M05 |
| Building-service asset | Ingests from; M47 owns the asset | M48 / M47 |
| Failure prediction model | **Applies**; M26 builds, trains, evaluates and versions it | M26 |
| Asset health index | **Owns** the computation; M17 displays it | M48 / M17 |
| Alert | **Owns** raise, correlate and lifecycle; M27 delivers, M01 acts | M48 |
| Proposed intervention | **Owns** the proposal; M01 owns the resulting work | M48 / M01 |
| Consent to collect | **Owns** the per-asset collection consent; M33 owns party consent | M48 / M33 |
| Metered usage quantity | Supplies; M13 and M20 bill it | M48 / M13 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Asset Performance Management with embedded Cumulocity IoT** | Connectivity to any IoT data source — smart equipment and sensors, edge devices, data historians and lakes, and **file-based integration** as an efficient channel; sensor signals such as vibration, temperature and pressure ingested, evaluated against rules **or** machine-learning models, and turned into insights or alerts; condition monitoring plus a predictive engine including remaining-useful-life estimation | **Three things adopted directly.** (a) **Rules and models side by side, not sequentially** — a threshold rule is often better than a model and always cheaper, so the platform must run both from day one. (b) **File-based ingestion as a first-class channel**, because most of what 1000FiX can collect in Bangladesh in the near term arrives as a periodic export, not a live stream. (c) The **condition monitoring → health → prediction → action** progression as the module's spine | SAP's BTP-hosted architecture and the digital-twin visualisation layer. Neither is affordable nor necessary at this scale |
| **IBM Maximo Application Suite — Monitor / Predict** | Asset condition monitoring with anomaly detection on sensor data, and predictive models scoring asset failure risk against the maintenance work-order system | The **closed loop**: a prediction that does not create actionable work is a dashboard, not a capability. Every prediction in M48 must terminate in a proposed intervention with an owner, or be explicitly suppressed | Its industrial-asset orientation and model catalogue |
| **MQTT Sparkplug B** | A standardised payload and topic structure over MQTT for industrial telemetry, with birth/death certificates, state awareness and efficient binary encoding; used where an edge gateway collects from mixed sources and publishes once for parallel consumers | **Sparkplug B as the preferred wire format where a gateway exists**, because state awareness (knowing a device is alive versus silent) is exactly the distinction that makes gap detection possible. A silent device and a device reporting zero must never look the same | Mandating Sparkplug B. Most sources 1000FiX will connect are plain MQTT, HTTPS or file, and requiring a gateway everywhere would stop the module before it started |
| **OPC UA and OPC UA PubSub over MQTT** | Semantic interoperability for machine-to-machine communication; OPC UA where meaning matters, MQTT where bandwidth efficiency matters, and OPC UA PubSub over MQTT where both do | OPC UA supported as an adapter for equipment that speaks it — principally building services and specialist bench equipment | Building an OPC UA information model. 1000FiX's assets are IT devices, vehicles and building plant, not a process plant with an address space |
| **TimescaleDB production practice** | Hypertables with automatic chunk partitioning absorbing very high insert rates where a plain PostgreSQL table degrades at scale; **columnar compression reducing historical storage by up to ~95%**, transparent to SQL; **continuous aggregates for downsampling**, which survive after the underlying raw data is dropped; and hierarchical aggregate tiers — raw → minute → hour → day — with retention policies dropping the lower tiers as data ages | **The entire storage strategy, adopted as specified.** Hypertables, compression after a defined age, hierarchical continuous aggregates, and retention that drops raw data while preserving aggregates. This is the direct implementation of the `_CATEGORY_OVERVIEW.md` §9 risk mitigation, and it is why the answer to "what happens in year three" is known before the first point is ingested. It also keeps the operational skill set identical to the rest of the platform — the same PostgreSQL engine, the same backups, the same people (TD-13) | TimescaleDB TSL-licensed advanced features. `02-05` §4 restricts us to Apache-2.0 features, and the storage strategy above is achievable within them |
| **ISO 13374 — condition monitoring and diagnostics data processing** | A layered framework for processing, communicating and presenting machine condition-monitoring information: data acquisition → data manipulation → state detection → health assessment → prognostic assessment → advisory generation | **The six-layer framework as the module's internal architecture.** It maps almost exactly onto §5's functional areas, and adopting a published framework rather than inventing one means the boundary between M48 and M26 falls in a defensible place: M48 owns acquisition through health assessment and advisory generation; M26 owns the prognostic model itself | Formal conformance claims |
| **ISO 17359 — condition monitoring general procedures** | General procedures for setting up a condition-monitoring programme: criticality assessment first, then selection of measurement parameters, alarm criteria, and a defined response to each alarm | **Criticality-first programme design.** Assets are selected for monitoring because their failure matters, not because they happen to emit data. This is the discipline that stops an IoT programme becoming a data-collection hobby | Vibration-analysis-specific methodology |
| **ISO 15143-3 (AEMP 2.0)** | A vendor-neutral interface exposing asset identity, location, cumulative operating hours, idle time and utilisation across mixed-brand telematics | **The canonical field set for vehicle and equipment telemetry**, held identical to M13 §6 T-11 and M46 §6 T-03, so that all three modules speak one shape | — |
| **Open-source stack (Eclipse Mosquitto / EMQX, Telegraf, Grafana, Prometheus)** | Broker, collector, visualisation and metrics, all Apache/EPL-licensed | The L4 substrate: an MQTT broker, a Go/Python collector already scheduled in `02-05` §5.3, and Grafana for engineering-facing stream inspection | Grafana as the business-facing analytics surface; that is M25's role, and two BI surfaces is one too many |

**Design position.** Five deliberate differences from the benchmark.

First, **retention policy is designed before ingestion begins, not after storage becomes a
problem.** Every telemetry programme that fails does so by succeeding at collection. M48's
storage tiers, compression age and retention horizons are configuration that exists on day one,
are set per signal class, and are enforced automatically. There is no path in which raw data
accumulates indefinitely because nobody decided.

Second, **rules before models, always.** A threshold with hysteresis on a disk SMART attribute
catches most of what matters, costs nothing to run, and can be explained to a customer. The
platform ships with rule-based alerting complete, and models are added where rules demonstrably
cannot do the job. Presenting an unexplainable model output to a corporate client who is being
asked to authorise a proactive intervention is the fastest way to lose the argument.

Third, **precision is preferred over recall, and the target says so.** The Category F target is
predicted failures confirmed above 70% — a *precision* target. A predictive maintenance system
that cries wolf is switched off by the technicians it was built for within two months. It is
better to miss failures than to burn credibility, particularly in the first year when the
capability is establishing whether it can be trusted.

Fourth, **consent is a hard gate on collection, not a policy statement.** Customer devices are
customer property. M48 collects only agreed signals, from assets whose owner has consented, and
honours revocation by stopping collection and applying the agreed treatment to data already
held. `_CATEGORY_OVERVIEW.md` §9 records this as a high-impact legal risk, and the control is
implemented at the ingestion gate — a stream without valid consent does not ingest, rather than
ingesting and being filtered later.

Fifth, **the module's success measure is interventions, not insights.** The target of 500
proactive interventions per year is deliberately an *action* count. A health dashboard nobody
acts on has cost the programme 26 person-weeks and returned nothing.

---

## 5. Functional Areas & Features

### 5.1 Stream Registry, Onboarding & Consent

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IOT-001 | Stream registry | Maintain one record per telemetry stream, bound to exactly one asset identity in M17, M45, M46 or M47, and reject any stream that cannot be bound | **P0** | L5 |
| FR-IOT-002 | Device and gateway registry | Register physical devices and gateways with identifier, type, firmware, connectivity, owning party and the streams they publish | **P0** | L5 |
| FR-IOT-003 | Provisioning and credentials | Provision a device or gateway with unique credentials, rotate them on a schedule, and revoke them on decommission | **P0** | L5 |
| FR-IOT-004 | Signal definition | Define each signal with a code, unit of measure, data type, expected range, sampling interval, criticality and retention class | **P0** | L5 |
| FR-IOT-005 | **Collection consent** | Record, per asset and per signal group, the owner's consent to collect, the disclosure given, the agreed purpose and the expiry, and **refuse ingestion for any stream without valid consent** | **P0** | L5 |
| FR-IOT-006 | Consent revocation | Honour a revocation by stopping collection immediately and applying the agreed treatment — retain, anonymise or delete — to data already held, with an evidence record | **P0** | L5 |
| FR-IOT-007 | Criticality-driven selection | Support a documented criticality assessment determining which assets are monitored and which signals are collected, so that monitoring scope is a decision rather than an accident (ISO 17359) | P1 | L5 |
| FR-IOT-008 | Decommissioning | Decommission a stream or device cleanly: stop ingestion, close open alerts, mark the historical series terminated, and retain or purge per policy | P1 | L5 |

### 5.2 Ingestion & Protocol Adapters

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IOT-009 | MQTT ingestion | Ingest over MQTT with per-device authentication and topic authorisation, supporting plain MQTT payloads and **Sparkplug B** where a gateway is present | **P0** | L4 |
| FR-IOT-010 | Device liveness | Use Sparkplug birth and death certificates, or a configurable heartbeat, to distinguish a silent device from a device reporting a zero value | **P0** | L4/L5 |
| FR-IOT-011 | HTTPS ingestion | Accept authenticated HTTPS/REST batch and single-point submissions for agents and integrations that cannot use MQTT | **P0** | L4 |
| FR-IOT-012 | File batch ingestion | Accept periodic file exports — CSV, JSON, provider-specific — validate them against the signal model, and ingest them as a first-class channel with the same quality treatment as a live stream | **P0** | L4/L5 |
| FR-IOT-013 | OPC UA adapter | Ingest from equipment exposing an OPC UA server, with configurable node-to-signal mapping | P2 | L4 |
| FR-IOT-014 | SNMP and agent adapters | Ingest from SNMP-capable network and print devices and from the M05 RMM collector, normalising to the same signal model | P1 | L4 |
| FR-IOT-015 | Telematics adapter | Ingest vehicle telematics conforming to the ISO 15143-3 (AEMP 2.0) field set, so a change of provider is configuration rather than redesign | **P0** | L4 |
| FR-IOT-016 | Validation and normalisation | Validate every point against its signal definition — type, range, timestamp plausibility — convert to the canonical unit, and attach a quality flag rather than discarding a suspect value silently | **P0** | L5 |
| FR-IOT-017 | Late and out-of-order data | Accept points arriving late or out of order within a configurable window, place them correctly in the series, and recompute affected aggregates | **P0** | L4 |
| FR-IOT-018 | Duplicate suppression | Deduplicate on device, signal and timestamp, so that a gateway replay after reconnection does not distort a series | **P0** | L4 |
| FR-IOT-019 | Edge buffering | Support gateway-side buffering during connectivity loss and ordered replay on reconnection, with a defined buffer horizon | **P0** | L4 |
| FR-IOT-020 | Back-pressure | Apply back-pressure and queue-based buffering under ingestion surge, shedding only the lowest-criticality signal classes and recording what was shed | **P0** | L4 |

### 5.3 Time-Series Storage & Lifecycle

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IOT-021 | **Hypertable storage** | Store all telemetry in TimescaleDB hypertables with time-based chunk partitioning, and **never in a transactional PostgreSQL table** | **P0** | L4 |
| FR-IOT-022 | **Compression policy** | Apply columnar compression automatically to chunks beyond a configurable age, per signal class, with query behaviour unchanged | **P0** | L4 |
| FR-IOT-023 | **Continuous aggregates** | Maintain hierarchical continuous aggregates — raw → minute → hour → day — refreshed on a policy, and used transparently by queries at the appropriate resolution | **P0** | L4 |
| FR-IOT-024 | **Retention policy** | Drop raw data beyond its retention horizon per signal class while **preserving the aggregates derived from it**, so that long-term trend survives the deletion of detail | **P0** | L4 |
| FR-IOT-025 | Retention governance | Define retention, compression and aggregation per signal class as configuration, require approval to change it, and report projected storage against the configured policy | **P0** | L5 |
| FR-IOT-026 | Archive to the data platform | Publish aggregates and selected raw series to M62 for long-term analytical retention and model training, without M62 becoming the operational store | P1 | L5 |
| FR-IOT-027 | Query interface | Expose time-series query by asset, signal, window and aggregation, returning at the resolution requested and meeting the latency budget in §6 | **P0** | L4/L5 |
| FR-IOT-028 | Gap detection | Detect and record gaps in an expected series, distinguishing device silence, connectivity loss and platform failure | **P0** | L5 |

### 5.4 Alerting & Rules

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IOT-029 | Rule definition | Define alert rules against signals — absolute threshold, rate of change, sustained condition, comparison to a baseline, and composite conditions across signals — without writing code | **P0** | L5 |
| FR-IOT-030 | Stream evaluation | Evaluate rules continuously against incoming data with a defined evaluation latency, not on a batch schedule | **P0** | L4/L5 |
| FR-IOT-031 | Hysteresis and dwell | Support hysteresis bands and minimum dwell times so that a value oscillating around a threshold produces one alert, not fifty | **P0** | L5 |
| FR-IOT-032 | Alert lifecycle | Manage alerts through raised → acknowledged → in progress → resolved → closed, with suppression and maintenance windows | **P0** | L5 |
| FR-IOT-033 | Deduplication and correlation | Deduplicate repeated alerts on the same asset and signal, and correlate related alerts across signals or across assets at a site into a single actionable event | **P0** | L5 |
| FR-IOT-034 | Escalation | Escalate an unacknowledged alert by severity through a configurable ladder, routing through M27 for customer-facing notification and to the owning module for internal action | **P0** | L5 |
| FR-IOT-035 | Alert-to-action | Route an alert to the module that owns the asset — M17 for a customer device, M45 for equipment, M46 for a vehicle, M47 for building services, M05 for an MSP endpoint — and never act on the asset directly | **P0** | L5 |
| FR-IOT-036 | Rule performance | Report per-rule alert volume, acknowledgement rate, false-positive rate and time to resolution, and flag rules whose output is being routinely ignored | P1 | L5 |

### 5.5 Health Scoring, Prediction & Prescriptive Action

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IOT-037 | **Asset health index** | Compute a composite health index per monitored asset from current signal state, trend, alert history, fault history from M17 and age, with the contributing factors exposed alongside the score | **P0** | L5 |
| FR-IOT-038 | Health banding and trend | Band the index into actionable states — healthy, watch, degraded, critical — and report the trajectory, not only the current value | **P0** | L5 |
| FR-IOT-039 | **Prediction application** | Score monitored assets against failure-prediction models published by M26, returning a predicted failure mode, a probability, a horizon and the model version used | **P0** | L5 |
| FR-IOT-040 | Model governance at the point of use | Refuse to apply a model that is unpublished, expired or below its evaluation threshold, and record the model version on every prediction so any output can be reproduced | **P0** | L5 |
| FR-IOT-041 | Remaining useful life | Where the model and signal support it, estimate remaining useful life with a confidence interval, and present the interval rather than a single number | P2 | L5 |
| FR-IOT-042 | **Prescriptive intervention** | Convert a prediction into a proposed intervention naming the recommended action, the parts likely required (checked for availability with M15), the skill required (M22) and the entitlement position (M08), and route it to M01 for scheduling | **P0** | L5 |
| FR-IOT-043 | Entitlement and consent check | Verify, before proposing a customer-facing intervention, that the customer is entitled under contract or has agreed to proactive service, and route a commercial opportunity to M07 where they are not | **P0** | L5 |
| FR-IOT-044 | **Outcome tracking** | Record, for every prediction, whether the predicted failure occurred, whether an intervention was performed, and whether it prevented the failure — feeding precision measurement and M26 retraining | **P0** | L5 |
| FR-IOT-045 | Fleet and cohort analytics | Aggregate telemetry across an asset cohort — model, brand, customer, branch, age band — to surface systemic failure patterns and support brand-facing reliability reporting | P1 | L5 |
| FR-IOT-046 | Pipeline observability | Monitor and report ingestion reliability, points ingested, devices reporting, gaps, evaluation lag, storage growth and compression ratio, with alerting on the platform itself | **P0** | L4/L5 |

> **Cross-cutting.** Model training, feature engineering and evaluation are **M26's**; M48
> consumes a published, versioned model artefact. Customer-facing presentation of telemetry and
> health is delivered through P01 and P04 surfaces specified by M05 and M17; M48 supplies the
> data and the access control.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Telemetry never enters a transactional table** | No telemetry point is written to any `fix_*` PostgreSQL transactional table under any circumstance. Enforced by schema separation and asserted in CI. This is the direct mitigation of the platform-wide risk in `_CATEGORY_OVERVIEW.md` §9 |
| T-02 | **Ingestion throughput** | Sustain 20,000 points per second at steady state with headroom to 60,000 in burst, on the 8 vCPU / 32 GB / 4 TB TimescaleDB node specified in `02-05` §6 |
| T-03 | **Ingestion reliability** | ≥ 99.5% of points published by a healthy device are durably stored, measured end to end by sequence-gap analysis, not by collector logs |
| T-04 | **Storage tiering** | Raw retained 30–90 days by signal class; minute aggregates 13 months; hour aggregates 3 years; day aggregates indefinitely. Compression applied beyond 7 days. Projected steady-state footprint is computed at design and monitored against actual |
| T-05 | **Aggregate survival** | Continuous aggregates persist after the underlying raw chunks are dropped by the retention policy; refresh policies are ordered so no aggregate is ever computed from data already deleted |
| T-06 | **Query latency** | A single asset's 24-hour series returns in ≤ 300 ms at p95; a 12-month daily aggregate across a 500-asset cohort in ≤ 2 s |
| T-07 | **Idempotent ingestion** | Every point carries device, signal and timestamp forming a natural idempotency key; replay after reconnection is a no-op, not a duplicate |
| T-08 | **Ordered replay** | Gateway buffers replay in timestamp order; the collector places late points correctly and triggers aggregate recomputation for the affected window |
| T-09 | **Back-pressure without silent loss** | Under surge, the collector applies back-pressure and buffers; where shedding is unavoidable it sheds only the lowest-criticality classes and **records exactly what was shed**, because unrecorded loss is indistinguishable from a healthy asset |
| T-10 | **Alert evaluation latency** | A critical-class rule is evaluated within 10 seconds of the point arriving; a standard-class rule within 60 seconds |
| T-11 | **Consent enforced at ingestion** | The consent check is performed at the ingestion gate. A stream without valid consent is rejected at the broker, not filtered downstream. There is no path by which unconsented data is written and later removed |
| T-12 | **Model application isolation** | Model scoring runs through the M26 inference gateway with a defined timeout and a fallback; a model failure degrades M48 to rule-based alerting rather than stopping the pipeline |
| T-13 | **Prediction reproducibility** | Every prediction stores its model version, input feature window and score, so any output can be reproduced and explained months later — including to a customer who was charged for a proactive intervention |
| T-14 | **Multi-entity and tenant isolation** | Every stream carries `company_id`, `operating_unit_id` and owning party; a customer accesses only their own assets' telemetry, enforced at the query layer (AS-03, AS-14) |
| T-15 | **Field-level protection** | Telemetry that could reveal personal behaviour — location traces, usage patterns on a personal device — is treated as personal data under AS-14, with field-level encryption and restricted access |
| T-16 | **Licence compliance** | Only Apache-2.0-licensed TimescaleDB features are used, per `02-05` §4. No TSL-licensed capability is a dependency |
| T-17 | **Scale envelope** | Year one: 2,000–5,000 monitored assets, ~15,000 streams, ~1.5 billion raw points per year before downsampling. Year three: 15,000 assets, ~60,000 streams. The storage model is sized for year three at design |
| T-18 | **Pipeline observability** | Ingestion, evaluation and storage metrics are exported to the OpenTelemetry/Prometheus stack (`02-05` §4), with the platform's own alerting distinct from asset alerting |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M48 |
|---|---|---|
| **Corporate client's IT manager** | Calls when a server fails, and loses a day | Is told the drive will fail, and schedules the replacement for a Saturday |
| **MSP engineer (M05)** | Monitors what the RMM agent happens to show, per client, per tool | Works one alert queue across every monitored estate, correlated and deduplicated |
| **Technician** | Attends a failure, diagnoses on site, orders a part, returns | Attends a predicted failure with the right part already on the van |
| **Dispatcher** | Fills the day with reactive work and emergencies | Has a stream of schedulable proactive work to fill low-demand periods |
| **Account manager** | Sells reactive repair, and renews on relationship | Shows a client their estate's health, and sells a maintenance outcome |
| **Branch manager** | Discovers the generator has failed when the power goes | Sees the generator degrading and has it serviced before load shedding |
| **Logistics Manager** | Services vehicles on a fixed schedule regardless of condition | Services on condition, and catches a failing vehicle before it strands a technician |
| **Quality Manager** | Investigates recurring model failures anecdotally | Queries a cohort across the installed base and produces a brand-facing reliability report |
| **CTO** | Holds a predictive-maintenance commitment with no platform | Owns one telemetry platform serving five asset populations, with a measured precision figure |

### 7.2 Quantified Business Benefit

M48 is a **capability-creating module** with both protective and revenue-enabling value. It
carries no line of its own in the Scope Charter §6.2 register.

| Benefit | Mechanism | Value |
|---|---|---|
| **Proactive interventions created** | Predictions and threshold alerts converted into scheduled work | **> 500 proactive interventions per year** (`_CATEGORY_OVERVIEW.md` §7). This is the module's primary output measure — work created, not insights displayed |
| **Managed services differentiation** | M05 sells a monitored, predictive service rather than a reactive one, at a materially different price point | Underpins the **BDT 95 lac/year** managed-services contribution attributed to M05 in §6.2. M05 is deliverable without M48 but is commercially weaker |
| **AMC/RAMC renewal and upsell** | Estate health reporting gives the account manager evidence at renewal, and predicted failures justify a higher service tier | Supports the **BDT 72 lac/year** AMC/RAMC uplift attributed to M08 |
| **Rental fleet protection** | Condition monitoring on rental assets catches degradation before a customer experiences it | Supports the **BDT 48 lac/year** rental margin attributed to M13, by protecting utilisation and reducing mid-hire failure |
| **Schedulable demand** | Proactive work is schedulable work; it fills troughs and smooths technician utilisation | Contributes to technician productivity (KPI-011) by converting emergency work into planned work |
| **First-time fix on proactive work** | A predicted failure names the likely part, checked against M15 before the visit | Supports KPI-004 first-time fix at 88%; proactive visits should materially exceed the reactive average |
| **Fleet running cost** | Condition-based servicing replacing fixed-interval servicing on vehicles | Supports M46's cost-per-kilometre −12% target |
| **Branch continuity** | Generator, UPS and HVAC degradation caught before failure | Supports M47's infrastructure availability target and protects branch operating hours |
| **Brand reliability reporting** | Cohort failure analysis across the installed base of a brand's models | A genuinely differentiating asset in a brand partnership conversation; no competitor in this market can produce it |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The transactional platform is protected** | The most important institutional benefit is negative: because M48 exists, telemetry never degrades the system every branch depends on. This risk is named at category level as high-impact and platform-wide |
| **One platform, not five** | M05, M13, M46, M47 and M17 would each otherwise build a time-series capability. One platform with one operational skill set is the difference between a maintainable estate and five orphaned pipelines |
| **Privacy discipline as a stated position** | Collecting only agreed signals, disclosing collection and honouring revocation is a position the Company can state publicly. It is also the practical defence of the "your device and data are secure" claim on which the ISMS rests |
| **Explainable automation** | Rules before models, and every prediction reproducible from a stored model version and feature window, means a customer challenged decision can be answered. Unexplainable automation is unusable in a B2B service relationship |
| **Foundation for a service model change** | The strategic value is that a company whose work begins when something breaks becomes a company whose work is scheduled before it breaks. Every other benefit follows from that |
| **Data asset for the future** | Years of condition and failure data across a large multi-brand installed base is an asset no competitor in Bangladesh will hold, and it compounds |
| **Expansion readiness** | The platform is asset-population-agnostic; a new country or a new asset class is an adapter and a signal model, not a new system |

---

## 8. Lifecycle & State Models

### 8.1 The ISO 13374 Processing Chain

M48's internal architecture follows the published condition-monitoring framework, which also
defines where M48 ends and M26 begins.

```
   ┌─────────────────────┐
   │ 1. DATA ACQUISITION │  MQTT · Sparkplug B · HTTPS · file · OPC UA · SNMP · telematics
   └──────────┬──────────┘  consent gate ▸ authentication ▸ ingestion
              │
   ┌──────────▼──────────┐
   │ 2. DATA MANIPULATION│  validation ▸ unit normalisation ▸ quality flags ▸ dedup ▸
   └──────────┬──────────┘  late/out-of-order placement ▸ hypertable write ▸ aggregates
              │
   ┌──────────▼──────────┐
   │ 3. STATE DETECTION  │  rule evaluation ▸ threshold · rate · sustained · composite
   └──────────┬──────────┘  hysteresis ▸ dedup ▸ correlation ▸ ALERT
              │
   ┌──────────▼──────────┐
   │ 4. HEALTH ASSESSMENT│  composite health index ▸ banding ▸ trend
   └──────────┬──────────┘  (signals + alerts + M17 fault history + age)
              │
   ┌──────────▼──────────┐
   │ 5. PROGNOSTIC       │  ◄── MODEL FROM M26 (built, trained, evaluated, versioned there)
   │    ASSESSMENT       │  predicted failure mode ▸ probability ▸ horizon ▸ RUL
   └──────────┬──────────┘  M48 APPLIES ONLY
              │
   ┌──────────▼──────────┐
   │ 6. ADVISORY         │  proposed intervention ▸ parts (M15) ▸ skill (M22) ▸
   │    GENERATION       │  entitlement (M08) ▸ consent ▸ route to M01
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │    OUTCOME LOOP     │  did it fail? was it prevented? → precision measure → M26 retrain
   └─────────────────────┘
```

### 8.2 Stream Lifecycle

```
   ┌────────────┐  asset identified (M17/M45/M46/M47), consent recorded
   │ REGISTERED │
   └─────┬──────┘
         │ device provisioned, credentials issued, signal model bound
   ┌─────▼──────┐
   │ PROVISIONED│
   └─────┬──────┘
         │ first valid point received
   ┌─────▼──────┐        no point within the expected interval
   │  ACTIVE    ├──────────────────────────────► SILENT ──► gap recorded,
   └──┬───┬─────┘                                  │        liveness alert
      │   │  ◄─────────────────────────────────────┘  point received
      │   │
      │   │ consent revoked
      │   └────────────────────────► SUSPENDED ──► ingestion refused,
      │                                 │           agreed data treatment applied
      │                                 │  consent restored
      │   ◄─────────────────────────────┘
      │ asset retired, device removed, or contract ended
   ┌──▼──────────┐
   │ DECOMMISSIONED│  ingestion stopped, alerts closed, series terminated,
   └─────────────┘   history retained or purged per policy
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Registered | Asset exists in M17/M45/M46/M47 **and** collection consent is valid | CTO / MSP engineer / Logistics Manager |
| Registered | Provisioned | Credentials issued, signal model bound, criticality assessed | IT Administrator |
| Provisioned | Active | First valid point received and validated | System |
| Active | Silent | No point within the expected interval, or a Sparkplug death certificate received | System, automatic |
| Silent | Active | Valid point received; the gap is recorded permanently | System |
| Active / Silent | Suspended | Consent revoked, contract ended, or a platform decision | System / account manager |
| Suspended | Active | Consent restored and re-recorded | Account manager |
| Any | Decommissioned | Asset retired, device removed, or monitoring ceased | CTO / account manager |

### 8.3 Alert & Prediction Lifecycle

| Stage | Rule | Owner |
|---|---|---|
| Raised | A rule fires with hysteresis and dwell satisfied | System |
| Deduplicated | An identical open alert on the same asset and signal exists | System |
| Correlated | Related alerts across signals or across assets at a site are grouped into one actionable event | System |
| Routed | Sent to the module owning the asset — never acted on directly by M48 | System |
| Acknowledged | A named owner accepts it within the severity SLA | Owning role |
| Escalated | Not acknowledged within the SLA; escalates by severity ladder | System |
| Suppressed | Within a maintenance window, or an explicitly suppressed rule with a reason and an expiry | Named approver |
| Resolved | Underlying condition cleared, or intervention completed | Owning role |
| **Outcome recorded** | For predictions: failure occurred / did not occur; intervention performed / not; failure prevented / not | System + owning role |

> **Precision is measured from the outcome record, not from the alert count.** An alert that is
> never acknowledged is counted as a failure of the rule, not of the person.

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-IOT-01 | **No telemetry point is ever written to a transactional PostgreSQL table**; all telemetry resides in the time-series store | **H** | CTO |
| BRU-IOT-02 | Every telemetry stream binds to exactly one existing asset identity; a stream that cannot be bound is refused | **H** | CTO |
| BRU-IOT-03 | **Telemetry is collected from a customer-owned asset only with recorded, disclosed, purpose-limited consent**; a stream without valid consent is refused at ingestion | **H** | Chief Commercial Officer |
| BRU-IOT-04 | Consent revocation stops collection immediately and applies the agreed treatment to data already held, with an evidence record | **H** | Chief Commercial Officer |
| BRU-IOT-05 | Only signals disclosed in the consent may be collected; collecting an undisclosed signal is a data-protection incident | **H** | CTO |
| BRU-IOT-06 | Retention, compression and aggregation policy is defined per signal class before ingestion begins, and a change requires CTO approval | **H** | CTO |
| BRU-IOT-07 | Raw data may be dropped by retention policy only where the aggregates derived from it are already computed and preserved | **H** | CTO |
| BRU-IOT-08 | Data shed under back-pressure is recorded; silent loss is never permitted | **H** | CTO |
| BRU-IOT-09 | A silent device and a device reporting zero are never treated as equivalent | **H** | CTO |
| BRU-IOT-10 | A model that is unpublished, expired or below its evaluation threshold is not applied | **H** | CTO |
| BRU-IOT-11 | Every prediction records the model version, feature window and score, and is reproducible | **H** | CTO |
| BRU-IOT-12 | M48 never creates, modifies or acts on an asset; it routes to the module that owns it | **H** | CTO |
| BRU-IOT-13 | A customer-facing proactive intervention is proposed only where the customer is entitled under contract or has agreed to proactive service; otherwise it routes to M07 as an opportunity | **H** | Chief Commercial Officer |
| BRU-IOT-14 | Every prediction has a recorded outcome — confirmed, not confirmed, or prevented by intervention | **H** | CTO |
| BRU-IOT-15 | A rule whose alerts are routinely unacknowledged is flagged for review and may be suspended by the CTO with a reason | **A** | CTO |
| BRU-IOT-16 | Alert suppression requires a named approver, a reason and an expiry; indefinite suppression is not permitted | **A** | CTO |
| BRU-IOT-17 | A customer may access telemetry and health data for their own assets only | **H** | CTO |
| BRU-IOT-18 | Telemetry capable of revealing personal behaviour is treated as personal data under AS-14 | **H** | CTO |
| BRU-IOT-19 | Only Apache-2.0-licensed time-series features are used; no TSL-licensed capability may become a dependency | **H** | CTO |
| BRU-IOT-20 | Monitoring scope follows a documented criticality assessment; assets are monitored because failure matters, not because data is available | **C** | CTO |
| BRU-IOT-21 | Model failure degrades M48 to rule-based alerting; it never stops ingestion | **C** | CTO |
| BRU-IOT-22 | Prediction precision below the published threshold for two consecutive months suspends customer-facing use of that model pending M26 review | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table / Store | Purpose | Key Attributes |
|---|---|---|---|
| `fix.telemetry.stream` | `fix_telemetry_stream` (PostgreSQL) | Stream registry | stream_uid, asset_id, asset_module (M17/M45/M46/M47), device_id, signal_set_id, owning_party_id, consent_id, criticality, expected_interval, state, registered_at, last_point_at, company_id, operating_unit_id |
| `fix.telemetry.device` | `fix_telemetry_device` | Physical device or gateway | device_identifier, device_type, provider_party_id, firmware, protocol, connectivity, credential_ref, credential_rotated_at, fitted_asset_id, health_state, last_seen_at, state |
| `fix.telemetry.signal` | `fix_telemetry_signal` | Signal definition | signal_code, name, data_type, canonical_unit, expected_min, expected_max, sampling_interval, criticality_class, retention_class, aggregation_functions |
| **`fix.telemetry.point`** | **`fix_telemetry_point` (TimescaleDB hypertable)** | **The measurement — the only high-volume object in the system** | time, stream_id, signal_id, value_numeric, value_text, quality_flag, ingested_at, source_channel *(hypertable, chunked by time, compressed beyond policy age)* |
| `fix.telemetry.aggregate.*` | TimescaleDB continuous aggregates | Downsampled tiers | minute / hour / day materialised views per signal class, surviving raw-data retention |
| `fix.telemetry.consent` | `fix_telemetry_consent` | Collection consent per asset | asset_id, owning_party_id, signal_groups_permitted, purpose, disclosure_document_id, granted_at, granted_by, expires_at, revoked_at, revocation_treatment, evidence_ref |
| `fix.telemetry.gap` | `fix_telemetry_gap` | A recorded absence | stream_id, gap_from, gap_to, cause (device_silent/connectivity/platform/shed), points_expected, detected_at, resolved_at |
| `fix.telemetry.shed` | `fix_telemetry_shed` | What back-pressure discarded | occurred_from, occurred_to, signal_classes_shed, streams_affected, points_estimated, trigger_metric, authorised_by_policy |
| `fix.alert.rule` | `fix_alert_rule` | An evaluable rule | name, scope (signal/asset/category/cohort), condition_type, expression, threshold, hysteresis_band, dwell_seconds, severity, evaluation_class, routing_target_module, enabled, suspended_reason, created_by |
| `fix.alert` | `fix_alert` | A raised alert | rule_id, stream_id, asset_id, raised_at, severity, trigger_value, state, deduplicated_into_id, correlation_group_id, routed_to_module, acknowledged_by, acknowledged_at, escalation_level, suppressed_until, suppressed_by, resolved_at, resolution_code |
| `fix.alert.correlation` | `fix_alert_correlation` | A grouped actionable event | group_uid, member_alert_ids, correlation_basis (asset/site/signal/cohort), opened_at, closed_at, summary |
| `fix.asset.health` | `fix_asset_health` | Composite health index | asset_id, computed_at, index_value, band (healthy/watch/degraded/critical), trend, contributing_factors_json, signal_component, alert_component, fault_history_component, age_component, previous_index |
| `fix.failure.prediction` | `fix_failure_prediction` | A prediction, reproducible | asset_id, model_id (M26), model_version, predicted_at, failure_mode, probability, horizon_days, rul_estimate, rul_confidence_interval, feature_window_from, feature_window_to, input_snapshot_ref, state |
| `fix.prediction.outcome` | `fix_prediction_outcome` | Did it happen | prediction_id, outcome (confirmed/not_confirmed/prevented/expired), observed_at, related_service_order_id, intervention_performed, evidence_ref, contributes_to_precision |
| `fix.proposed.intervention` | `fix_proposed_intervention` | The advisory | prediction_id or alert_id, asset_id, recommended_action, parts_required (M15 refs), parts_available, skill_required (M22), entitlement_state (M08), consent_state, commercial_route (contract/opportunity), proposed_at, routed_to_m01_at, service_order_id, state, declined_reason |
| `fix.monitoring.scope` | `fix_monitoring_scope` | Criticality assessment | asset_id or asset_category, criticality_rating, failure_consequence, signals_selected, selection_rationale, assessed_by, assessed_on, review_due |
| `fix.telemetry.retention.policy` | `fix_telemetry_retention_policy` | Storage governance | signal_class, raw_retention_days, compression_after_days, minute_aggregate_days, hour_aggregate_days, day_aggregate_days, approved_by, effective_from, projected_storage_gb |
| `fix.pipeline.metric` | `fix_pipeline_metric` | Platform observability | period, points_ingested, points_rejected, devices_expected, devices_reporting, ingestion_reliability, evaluation_lag_p95, storage_gb, compression_ratio, gaps_open |

> **Volume note.** Of the eighteen entities above, exactly one — `fix.telemetry.point` — is
> high-volume, and it is the only one stored as a hypertable. Every other object is ordinary
> transactional data at ordinary volume. This separation is the module's central design fact.

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.asset`, `fix.asset.fault` | **M17** / **M49** | Read for binding, fault history and health input; publish health index back |
| `fix.tool.register` | **M45** | Read for binding; publish condition signal back |
| `fix.vehicle`, `fix.telematics.device` | **M46** | Read for binding; publish condition signal and derived aggregates back |
| `fix.site.infrastructure` | **M47** | Read for binding; publish condition signal back |
| `fix.monitored.asset`, RMM collector feed | **M05** | Read the monitoring overlay; ingest the agent feed |
| Model artefact, version, evaluation metrics, inference gateway | **M26** | Read and invoke; never train |
| Warehouse, lakehouse, archive, data catalogue | **M62** | Publish aggregates and selected raw series |
| `fix.contract`, `fix.entitlement` | M08 | Read before proposing a customer-facing intervention |
| `fix.stock.quant` | M15 | Read part availability for a proposed intervention |
| `fix.competency` | M22 | Read the skill required for a proposed intervention |
| `fix.party`, consent as a party attribute | M33 | Read |
| `fix.service.order` | M01 | Create a proposed intervention; read the outcome |
| Notification channel and template | M27 | Invoke for customer-facing alerting |
| `fix.rental.asset` | M13 | Read for binding; supply metered usage |
| `fix.branch`, `fix.entity` | M30 | Read |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-IOT-01 | A device connects and publishes | Authenticate, authorise the topic, verify consent, validate against the signal model, normalise units and write to the hypertable | Reject with a logged reason; **never write unconsented or unvalidatable data** |
| AUT-IOT-02 | Consent revoked | Suspend the stream immediately, refuse further ingestion, and apply the agreed treatment — retain, anonymise or delete — to data already held | Suspend first, then escalate the treatment as a manual task if automated treatment fails |
| AUT-IOT-03 | No point received within the expected interval, or a death certificate received | Mark the stream silent, open a gap record with a cause, and raise a liveness alert to the owning module | Alert only |
| AUT-IOT-04 | Chunk age exceeds the compression threshold | Compress the chunk per the signal-class policy | Retry; alert on repeated failure and report projected storage impact |
| AUT-IOT-05 | Aggregate refresh policy due | Refresh continuous aggregates in tier order, oldest tier first | Retry; block the retention job until aggregates are current |
| AUT-IOT-06 | Raw data exceeds its retention horizon | Verify the derived aggregates exist and are current, then drop the raw chunks | **Block the drop** if aggregates are not current |
| AUT-IOT-07 | Late or out-of-order points arrive within the window | Place them in the series and recompute the affected aggregate windows | Record and alert if outside the window |
| AUT-IOT-08 | Ingestion rate exceeds the sustainable threshold | Apply back-pressure, buffer, and shed only the lowest-criticality classes, recording exactly what was shed | Alert the CTO; never shed silently |
| AUT-IOT-09 | A point satisfies a rule with hysteresis and dwell met | Raise an alert, deduplicate against open alerts, correlate into a group where related, and route to the owning module | Raise uncorrelated and alert on the correlation failure |
| AUT-IOT-10 | An alert is unacknowledged beyond its severity SLA | Escalate by ladder; for customer-facing alerts route notification through M27 | Escalate continuously |
| AUT-IOT-11 | Nightly, per monitored asset | Recompute the health index from signals, alerts, M17 fault history and age; publish the index and band to M17 | Retain the previous index and alert |
| AUT-IOT-12 | Health band worsens, or the scoring schedule falls due | Invoke the M26 inference gateway to score the asset against the applicable published model | Fall back to rule-based alerting; record that the model was unavailable |
| AUT-IOT-13 | A prediction exceeds the action threshold | Generate a proposed intervention: recommended action, parts checked with M15, skill from M22, entitlement from M08, consent verified | Raise the prediction without an intervention and flag it for review |
| AUT-IOT-14 | Proposed intervention with a valid entitlement | Route to M01 as a preventive-maintenance service order with the prediction attached as evidence | Queue and retry; escalate to the account manager |
| AUT-IOT-15 | Proposed intervention with no entitlement | Route to M07 as a commercial opportunity rather than creating unbilled work | Report only |
| AUT-IOT-16 | The prediction horizon elapses, or the asset fails | Record the outcome — confirmed, not confirmed, prevented — and update the precision measure | Mark the outcome unknown and flag it; unknown outcomes are excluded from precision, not counted as successes |
| AUT-IOT-17 | Monthly | Compute precision and recall per model, publish to M26, and **suspend customer-facing use of any model below the published precision threshold for two consecutive months** | Suspend by default on computation failure |
| AUT-IOT-18 | Monthly | Compute rule performance — volume, acknowledgement rate, false-positive rate — and flag rules routinely ignored | Report only |
| AUT-IOT-19 | Continuous | Export pipeline metrics to the observability stack; alert on ingestion reliability below 99.5%, evaluation lag above budget, or storage growth beyond projection | Alert on the platform's own health channel |
| AUT-IOT-20 | Scheduled | Publish aggregates and selected raw series to M62 for long-term retention and model training | Retry; alert on repeated failure |
| AUT-IOT-21 | Device credential rotation due | Issue new credentials, confirm adoption, and revoke the old set | Alert; never revoke before adoption is confirmed |

---

## 12. Interfaces

### 12.1 Upstream — M48 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M62 Data Platform** | The platform foundation, long-term archive and model training datasets | Platform dependency + extract |
| **M26 AI/ML Services** | Published, versioned failure-prediction models and the inference gateway | REST (inference gateway) |
| M17 Asset Registry | Asset identity for stream binding; fault history as a health input | REST + events |
| M45 Enterprise Assets | Equipment identity for connected instruments and branch equipment | REST |
| M46 Fleet | Vehicle and telematics device identity; the telematics feed context | REST + events |
| M47 Facility | Building-service asset identity — generator, UPS, HVAC | REST |
| M05 Managed Services | Monitored-asset overlay and the RMM collector feed | Events + feed |
| M13 Rental | Rental asset identity and hire period context | REST |
| M08 Contracts | Entitlement position before proposing an intervention | REST |
| M15 Inventory | Part availability for a proposed intervention | REST |
| M22 Competency | Skill required for a proposed intervention | REST |
| M33 Party Master | Owning party identity and party-level consent context | REST |
| M28 Integration Platform | Event outbox, external feed onboarding, API gateway | Platform |
| M29 Identity & Security | Device credentialing, tenant isolation, field-level encryption policy | Platform |
| External devices, gateways and provider platforms | The telemetry itself | MQTT · Sparkplug B · HTTPS · file · OPC UA · SNMP |

### 12.2 Downstream — M48 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M17 Asset Registry | **Asset health index and open failure predictions** for display on the asset | Events + REST |
| M45 Enterprise Assets | Condition signal for connected equipment, as a PM trigger | Events |
| M46 Fleet | Vehicle condition signal, derived distance and idle aggregates, failure prediction | Events + REST |
| M47 Facility | Building-service condition signal, as a PM trigger and an outage predictor | Events |
| M05 Managed Services | The monitoring platform: streams, alerts, health and predictions for client estates | REST + events |
| M13 Rental | Condition signal and metered usage for rental assets | Events + REST |
| M01 Service Order | **Proposed interventions as preventive-maintenance orders with prediction evidence** | Command + events |
| M02 Field Service | Prediction context and recommended parts for a scheduled proactive visit | REST |
| M07 CRM | Commercial opportunities where a predicted need is outside entitlement | Events |
| M08 Contracts | Condition-based trigger for contract PM schedules | Events |
| M23 Quality | Systemic failure patterns across a cohort; telemetry evidence for quality investigations | Events + REST |
| M26 AI/ML | Prediction outcomes and labelled failure data for retraining | Warehouse extract |
| M27 Communications | Customer-facing alert and proactive-service notification triggers | Events |
| M62 Data Platform | Aggregates and selected raw series for long-term analytical retention | Extract |
| M25 BI | Telemetry, health and prediction facts as a reporting source | Warehouse extract |
| M60 GRC | Consent register, data-protection posture, platform risk indicators | REST |
| P01 Customer Portal | The customer's own asset health and telemetry, within consent | REST |
| P04 Corporate Portal | Estate health, alerts and proactive-service schedule | REST |
| P03 Admin Portal | Stream registry, rules, alerts, predictions, pipeline health | REST |
| P08 Brand Partner Portal | Cohort reliability statistics for the brand's own models, without customer identity | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `telemetry.stream_registered` | stream, asset, device, signals, consent reference | M17, M05, M60 |
| `telemetry.stream_silent` | stream, asset, last point, gap cause | **M46, M47, M05**, M17 |
| `telemetry.stream_suspended` | stream, reason, consent state | M05, M07, M60 |
| `telemetry.consent_revoked` | asset, party, treatment applied, evidence | **M60**, M33, M05 |
| `telemetry.data_shed` | window, signal classes, streams affected, estimated points | M60, M25 |
| `telemetry.gap_detected` | stream, window, cause | M46, M47, M05 |
| `asset.alert_raised` | asset, rule, severity, trigger value, correlation group | **M17, M45, M46, M47, M05**, M27 |
| `asset.alert_escalated` | alert, level, owner, elapsed | M27, M05 |
| `asset.alert_resolved` | alert, resolution, elapsed | M25, M23 |
| `asset.health_updated` | asset, index, band, trend, contributing factors | **M17**, M13, M05, M08 |
| `asset.health_degraded` | asset, from band, to band, drivers | M17, M07, M08, M27 |
| `asset.failure_predicted` | asset, failure mode, probability, horizon, model version | **M01, M02, M15, M08**, M05 |
| `asset.rul_estimated` | asset, remaining useful life, confidence interval | M13, M49, M46 |
| `intervention.proposed` | asset, action, parts, skill, entitlement, commercial route | **M01, M07**, M15, M22 |
| `intervention.outcome_recorded` | prediction, outcome, intervention performed, prevented | **M26**, M25, M23 |
| `telemetry.model_suspended` | model, version, precision, period | **M26**, M05, M07 |
| `telemetry.pipeline_degraded` | metric, value, threshold, affected streams | M66, M60 |
| `asset.cohort_pattern_detected` | cohort, failure mode, incidence, population | M23, M37, P08 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-IOT-01 | MQTT broker (Eclipse Mosquitto / EMQX) | Bidirectional | Device connectivity, topic authorisation, Sparkplug B state management |
| INT-IOT-02 | Vehicle telematics provider platform | Inbound | Position, distance, engine hours, idle and harsh events for M46, on the ISO 15143-3 field set |
| INT-IOT-03 | RMM agents and endpoint monitoring (M05 collector) | Inbound | Endpoint health, disk SMART, temperature, resource utilisation for monitored client estates |
| INT-IOT-04 | SNMP-capable network devices, printers and UPS units | Inbound | Device health polling at branches and client sites |
| INT-IOT-05 | Building-management and generator controllers | Inbound | Run hours, fuel level, load, temperature for M47, over OPC UA, Modbus/TCP gateway or file |
| INT-IOT-06 | Brand and manufacturer device-health APIs, where exposed | Inbound | Manufacturer-reported device health for warranty-relevant models |
| INT-IOT-07 | OpenTelemetry / Prometheus / Grafana | Outbound | Pipeline observability and engineering-facing stream inspection |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/telemetry/ingest` | POST | Authenticated single-point or batch HTTPS ingestion (idempotent) | Devices, agents, integrations |
| `/api/v1/telemetry/ingest/file` | POST | File batch submission with validation report | Providers, M05, M46 |
| `/api/v1/telemetry/streams` | GET/POST | Stream registry and registration | P03, M05, M46, M47 |
| `/api/v1/telemetry/streams/{id}/consent` | GET/POST/DELETE | Record, inspect and revoke collection consent | P03, P04, M07 |
| `/api/v1/telemetry/devices` | GET/POST | Device and gateway registry, provisioning, credential rotation | P03, M46 |
| `/api/v1/telemetry/query` | GET | Time-series query by asset, signal, window and aggregation | M25, P03, P04, M05 |
| `/api/v1/telemetry/gaps` | GET | Gap and liveness report by stream, asset or site | P03, M46, M47 |
| `/api/v1/alerts/rules` | GET/POST/PATCH | Define, enable, suspend and inspect rules | P03 |
| `/api/v1/alerts` | GET | Alert queue with correlation grouping | P03, M05, P04 |
| `/api/v1/alerts/{id}/acknowledge` | POST | Acknowledge an alert | P03, P02, M05 |
| `/api/v1/alerts/{id}/suppress` | POST | Suppress with reason and expiry | P03 |
| `/api/v1/assets/{id}/health` | GET | **Current health index, band, trend and contributing factors** | **M17**, P01, P04, M05 |
| `/api/v1/assets/{id}/predictions` | GET | Open predictions with model version, probability and horizon | M01, M02, P04 |
| `/api/v1/predictions/{id}/outcome` | POST | Record the outcome of a prediction | M01, P03 |
| `/api/v1/interventions/proposed` | GET | Proposed interventions awaiting routing or decision | M01, M07, P03 |
| `/api/v1/telemetry/cohorts/{id}/analysis` | GET | Cohort failure-pattern analysis | M23, P08, M37 |
| `/api/v1/telemetry/pipeline/health` | GET | Ingestion reliability, lag, storage and compression metrics | P03, P06, M66 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R02 Chief Technology Officer | C R U D A | **All — owns the module, retention policy, rule governance and model suspension** |
| R33 IT / System Administrator | C R U | Stream and device registry, provisioning, credential rotation, pipeline operations |
| R13 Remote Support Engineer | R U | Assigned client estates — alert queue, acknowledgement, health and predictions (via M05) |
| R05 Operations Director | R A | All — proactive intervention volume and scheduling impact |
| R32 Quality Manager / ISO Coordinator | R | Cohort failure patterns, telemetry evidence for quality investigations |
| R15 Logistics Coordinator | R | Vehicle telemetry and condition signals for the fleet |
| Branch Operations Lead | R | Building-service telemetry and condition signals for sites |
| R09 Workshop Supervisor / R10–R12 Technician | R | Predictions and health for assets on their assigned work only |
| R22 Account Manager (Corporate) | R U | Assigned accounts — estate health, consent management, proactive-service conversation |
| R04 Chief Commercial Officer | R A | **Consent policy, disclosure wording and the commercial route for unentitled interventions** |
| R26 Finance Manager | R | Intervention volume and its revenue and cost consequence |
| R38 Brand Partner (P08) | R | Cohort reliability statistics for the brand's own models; **never customer identity, never individual asset data** |
| R37 Corporate Portal User (P04) | R | Own company's estate health, alerts and proactive schedule, within consent |
| R36 Customer (P01) | R | **Own assets only** — health summary and the telemetry disclosed in their consent |

**Field-level restrictions.** `model_confidence`, `model_features` and `input_snapshot_ref` are
visible only to R02, R33 and model owners, per `05-04` §5. Raw telemetry from a customer asset
is visible to the owning customer and to internal roles with a service reason; it is never
visible to another customer, to a brand partner at individual-asset granularity, or to any
marketplace party. Location traces and usage patterns capable of revealing personal behaviour
are field-encrypted under AS-14 and restricted to the assigned service role.

**Segregation of duties.**
- The person who defines an alert rule may not be the sole approver of its indefinite
  suppression.
- The person who records a prediction outcome may not be the person whose intervention is being
  evaluated by it, where the outcome affects an incentive.
- Consent policy (R04) is separated from technical collection configuration (R02, R33), so that
  no single role can both widen what is collected and authorise it.
- Model publication (M26) is separated from model application (M48), so that a model cannot be
  self-approved into customer-facing use.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Pipeline health** | CTO, IT Administrator | Real time | Points ingested, devices expected versus reporting, ingestion reliability against the 99.5% target, evaluation lag, storage growth, compression ratio, open gaps |
| **Alert queue** | Remote Support Engineers, IT Administrator, branch and fleet owners | Real time | Open alerts by severity, asset, correlation group and age; acknowledgement SLA status |
| **Asset health estate view** | Account Manager, corporate client (P04), MSP team | Daily | Health band distribution across an estate, degraded and critical assets, trend |
| **Prediction precision** | CTO, Operations Director, CCO | Monthly | Predictions made, confirmed, not confirmed, prevented; precision per model against the > 70% target |
| **Proactive intervention register** | Operations Director, CCO, CFO | Monthly | Interventions proposed, accepted, scheduled, completed, declined — against the > 500 per year target |
| Intervention effectiveness | Operations Director, Quality Manager | Quarterly | Did the intervention prevent the failure; first-time fix on proactive versus reactive work |
| Rule performance | CTO, IT Administrator | Monthly | Volume, acknowledgement rate, false-positive rate and time to resolve per rule; rules routinely ignored |
| **Consent register** | CCO, CTO, GRC | Monthly | Assets with consent, signals permitted, expiries, revocations and the treatment applied |
| Stream liveness and gaps | IT Administrator, fleet and facility owners | Daily | Silent streams by cause, gap duration, devices requiring attention |
| Cohort reliability analysis | Quality Manager, brand partner (P08), CCO | Quarterly | Failure mode incidence by model, brand, age band and usage cohort, with population size |
| Vehicle condition summary | Logistics Manager | Weekly | Vehicles with degrading condition signals, predicted service need |
| Building-service condition | Branch Operations Lead, Operations Director | Weekly | Generator, UPS and HVAC condition by site, predicted intervention need |
| Rental fleet condition | Rental operations, CFO | Monthly | Health and metered usage across the rental pool, mid-hire failure risk |
| Storage and retention compliance | CTO, CFO | Monthly | Actual versus projected storage, retention policy adherence, compression effectiveness |
| Data-shed register | CTO, GRC | On occurrence | Every back-pressure shedding event, what was shed and why |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W8 Target | W9 Target |
|---|---|---|---|---|
| — | **Telemetry ingestion reliability** | n/a | **> 99.5%** | **> 99.7%** |
| — | **Predicted failures confirmed (precision)** | n/a | **> 70%** | **> 78%** |
| — | **Proactive interventions from prediction** | 0 | **> 500 per year** *(annualised run rate)* | **> 800 per year** |
| — | Monitored assets under active telemetry | 0 | 2,000 | **5,000** |
| — | Streams silent beyond 24 hours | n/a | < 3% | **< 1%** |
| — | Alert acknowledgement within severity SLA | n/a | 88% | **95%** |
| — | False-positive rate on critical-severity alerts | n/a | < 20% | **< 10%** |
| — | Proposed interventions accepted and scheduled | n/a | 60% | **75%** |
| — | Predicted failures prevented by intervention | n/a | 55% | **70%** |
| — | First-time fix on proactive visits | n/a | 92% | **96%** |
| — | Assets with valid, current collection consent | n/a | **100%** | **100%** |
| — | Unconsented data ingestion incidents | n/a | **0** | **0** |
| — | Telemetry stored outside the time-series store | n/a | **0** | **0** |
| — | Storage within the configured retention projection | n/a | ±15% | **±10%** |
| — | Predictions with a recorded outcome | n/a | 90% | **98%** |
| **KPI-004** *(supported)* | First-time fix rate | 72% | 86% | **88%** |

> **Register note.** The first three metrics are adopted verbatim from
> `_CATEGORY_OVERVIEW.md` §7 (ingestion reliability > 99.5%, precision > 70%, proactive
> interventions > 500 per year). M48 has **no KPI-0nn identifiers allocated** in the programme
> KPI register; all fifteen unnumbered metrics require allocation in `06-02` (not yet issued).
> Recorded as an audit action.
>
> **On precision versus recall.** Precision is the published target; recall is deliberately not
> one in the first year. A false alarm costs a technician visit and, more expensively, the
> credibility of the whole capability. A missed failure costs a reactive repair the Company
> would have performed anyway. The asymmetry is real and the targets reflect it.
>
> **Wave note.** M48 lands in W8 (Months 31–34), so the W9 column represents the position at
> programme close, with roughly six months of operation.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L4 | **TimescaleDB 2.x** (Apache-2.0 features only) — hypertables, compression, continuous aggregates, retention policies; **MQTT broker** (Eclipse Mosquitto / EMQX); **telemetry collector** (Go/Python, already scheduled in `02-05` §5.3); Grafana for engineering-facing stream inspection; OpenTelemetry/Prometheus for pipeline metrics | 36% |
| L5 | `cd_stream_registry`, `cd_telemetry`, `cd_alert_rules`, `cd_asset_health`, `cd_predictive_action` | 64% |

> M48 has **no L1 or L2 component**. There is no Odoo or OCA module for time-series telemetry,
> and there should not be — this is precisely the kind of workload the layered delivery model
> (`02-01` §5) directs to L4 standalone open-source systems. The stack is entirely
> Apache-2.0/EPL licensed and adds **zero licence cost**, consistent with the programme's $0
> software-licence position. The operational skill set is the same PostgreSQL engine the rest of
> the platform runs, which is the explicit reason TimescaleDB was chosen over InfluxDB (TD-13).

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 5 of 5 identifiers below are claimed by another module: **CD-078** also claimed by M56; **CD-079** also claimed by M56; **CD-171** also claimed by M50; **CD-172** also claimed by M50; **CD-173** also claimed by M51. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-171** | `cd_stream_registry` — stream and device registry, signal model, provisioning and credential rotation, **collection consent and revocation treatment**, criticality assessment, decommissioning | Odoo module + service | 5 PW |
| CD-078 | `cd_telemetry` — protocol adapters (MQTT/Sparkplug B, HTTPS, file, OPC UA, SNMP, telematics), validation and normalisation, dedup and late-data handling, edge buffering and back-pressure, **hypertable storage with compression, continuous aggregates and retention**, query interface, gap detection | Standalone collector service + Odoo module | 8 PW |
| **CD-172** | `cd_alert_rules` — rule definition, stream evaluation, hysteresis and dwell, alert lifecycle, deduplication and correlation, escalation, routing to owning modules, rule performance | Odoo module + evaluation service | 5 PW |
| CD-079 | `cd_asset_health` — composite health index, banding and trend, contributing-factor exposure, publication to M17 | Odoo module | 3 PW |
| **CD-173** | `cd_predictive_action` — model application through the M26 gateway, model governance at the point of use, RUL, **prescriptive intervention with parts, skill, entitlement and consent checks**, routing to M01, outcome tracking and precision measurement, cohort analytics | Odoo module + service | 5 PW |

> **CD register reallocation.** `02-05` §5.2 allocated **CD-078 `cd_telemetry` and CD-079
> `cd_asset_health` to M17**. Under the v2.1 re-scope both **move to M48**, retaining their IDs.
> Three new IDs, **CD-171…173**, are claimed from the extension block reserved for modules
> M31–M67, following CD-167…170 claimed by M47. **All CD IDs remain provisional** pending the
> unified CD register required by audit finding M-01 in `02-05`.
>
> **Category F CD block — complete.** CD-075…077 + CD-157…158 M17 · CD-159…162 M45 ·
> CD-163…166 M46 · CD-167…170 M47 · **CD-078…079 + CD-171…173 M48**.
> Category F therefore consumes CD-157…173 from the extension block; **CD-174 is the next
> free ID** for any category specified after this one.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M62 Data Platform** | The hard dependency. M48 needs the data platform for long-term archive, model training datasets and the analytical layer. `_CATEGORY_OVERVIEW.md` §8 states plainly that M48 is late *because* it needs M62 |
| **M26 AI/ML Services** | M48 applies models; M26 builds them. Without M26 the module delivers rules, health scoring and alerting but no prediction |
| M17 Asset Registry | Every stream binds to an asset. Two years of accumulated fault history is also the training signal |
| M28 Integration Platform | External feed onboarding, API gateway, event outbox |
| M29 Identity & Security | Device credentialing, tenant isolation, field-level encryption |
| M05 Managed Services | The largest source of monitored assets, and the module most dependent on the platform. **If M05 in Wave 5 requires a time-series capability before M48 exists, the storage layer is built once, by M48's design, and operated early** — this is recorded in `M05` §16.3 |
| M46 Fleet, M47 Facility | Telemetry sources; both live before M48 and both operate with reduced direct feeds until it arrives |
| M08 Contracts, M15 Inventory, M22 Competency | Required for the prescriptive intervention to name entitlement, parts and skill |

> **Sequencing warning.** M05 (Wave 5) needs telemetry three waves before M48 (Wave 8). The
> resolution is **not** to let M05 build a second time-series stack: the storage layer, schema
> and retention policy specified here are built at M05's time under M48's design authority, and
> M48 in Wave 8 adds the registry, rule engine, health scoring and prediction on top of a store
> that already exists. This is the single most important delivery decision in Category F and it
> must be taken explicitly at Wave 5 planning, not discovered at Wave 8.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| M05 monitoring data collected from Wave 5 | Depends on the client estate onboarded | `fix.telemetry.point` (already in the store, re-registered) | W8, re-registration only |
| Telematics history held by the provider | 12–24 months where the provider retains it | `fix.telemetry.point` (aggregates only) | W8, best-effort |
| Historical fault and failure records | From M17, 24–36 months | Model training set in M62 | W8, for M26 |
| Building-service run-hour logs | Manual logs at branches | `fix.telemetry.point` (day aggregates) | W8, best-effort |

> **Migration position.** M48 has the lightest migration burden in Category F, and deliberately
> so: **telemetry history is not migrated, it is accumulated.** The only genuine migration is
> the historical *fault and failure* record from M17, which is not telemetry at all — it is the
> label set M26 needs to train against. This is why M48 is scheduled last: the module's raw
> material is produced by the two years of operation that precede it.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | No telemetry point exists in any transactional PostgreSQL table in production | Schema assertion, full-database scan and a CI check that fails the build on violation |
| AC-02 | Ingestion sustains 20,000 points per second at steady state and 60,000 in burst on the specified node | Load test at the `02-05` §6 hardware specification |
| AC-03 | Ingestion reliability measured end to end by sequence-gap analysis exceeds 99.5% over a 30-day window | 30-day production measurement |
| AC-04 | A stream without valid consent is refused at ingestion, and no unconsented point is written | Negative test across MQTT, HTTPS and file channels |
| AC-05 | Consent revocation stops collection within 60 seconds and applies the agreed treatment to held data, with an evidence record | Scripted revocation scenario with data verification |
| AC-06 | Raw data is dropped by retention policy only after its derived aggregates are computed and preserved | Scripted retention run with aggregate verification before and after |
| AC-07 | Compression achieves the projected ratio and query results are byte-identical on compressed and uncompressed chunks | Comparative query test across the compression boundary |
| AC-08 | A 24-hour single-asset series returns in ≤ 300 ms at p95, and a 12-month daily aggregate across 500 assets in ≤ 2 s | Performance test at year-three data volume |
| AC-09 | A gateway replay after reconnection produces no duplicate points and places late data correctly, with aggregates recomputed | Scripted disconnection and replay test |
| AC-10 | A silent device is distinguishable from a device reporting zero, in every adapter | Adapter-by-adapter test including Sparkplug death certificates |
| AC-11 | Back-pressure sheds only the lowest-criticality classes and records exactly what was shed | Surge test with shed-record verification |
| AC-12 | A critical-class rule evaluates within 10 seconds of point arrival at full ingestion load | Latency test under load |
| AC-13 | A value oscillating around a threshold produces one alert, not many | Hysteresis and dwell test |
| AC-14 | Related alerts across signals and across assets at a site correlate into a single actionable event | Scripted multi-signal failure scenario |
| AC-15 | An alert routes to the module owning the asset, and M48 performs no action on the asset itself | Routing test across M17, M45, M46, M47 and M05 |
| AC-16 | An unpublished, expired or below-threshold model is not applied | Negative test against the M26 gateway |
| AC-17 | Every prediction is reproducible from its stored model version and feature window | Reproduction test on predictions three months old |
| AC-18 | A model failure degrades the platform to rule-based alerting without stopping ingestion | Induced-failure test |
| AC-19 | A proposed intervention names the parts, checks availability with M15, names the skill, verifies entitlement with M08 and confirms consent before routing to M01 | End-to-end scripted scenario |
| AC-20 | An intervention proposed for an unentitled customer routes to M07 as an opportunity and creates no unbilled work | Negative test |
| AC-21 | Every prediction reaches a recorded outcome, and unknown outcomes are excluded from precision rather than counted as successes | Precision computation review |
| AC-22 | Prediction precision exceeds 70%, and a model below threshold for two consecutive months is suspended from customer-facing use automatically | Six months of precision reports plus a scripted suspension test |
| AC-23 | Proactive interventions reach an annualised run rate above 500 | Six months of the intervention register |
| AC-24 | A customer can access telemetry only for their own assets, verified across P01, P04 and P08 | Tenant-isolation penetration test |
| AC-25 | A brand partner sees cohort statistics only, with no customer identity and no individual asset data | Payload inspection across every P08 endpoint |
| AC-26 | Only Apache-2.0-licensed time-series features are in use | Licence audit of the deployed configuration |
| AC-27 | CTO and Chief Commercial Officer sign off UAT, the CCO specifically on the consent model | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 27 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Is the shared time-series store built at Wave 5 under M48's design authority to serve M05, rather than M05 building its own?** This is the single most consequential decision in Category F | CTO / Data & Intelligence Squad | **W5 planning** |
| Q-02 | Which asset populations are in scope for Wave 8 — MSP endpoints, vehicles, building services, rental assets, customer devices — and in what order? | CTO / Operations Director | W8 minus 6 months |
| Q-03 | What is the criticality assessment that determines which assets are monitored, and who signs it? Monitoring everything that emits data is the failure mode to avoid | CTO / Quality Manager | W8 design |
| Q-04 | What is the consent model for customer-owned assets — a clause in the AMC/MSP contract, a separate consent, or an opt-in in P01? What wording does Legal require? | CCO / Legal | **W8 minus 6 months** |
| Q-05 | On revocation, is held telemetry retained, anonymised or deleted? The three have materially different engineering and contractual consequences | CCO / Legal / CTO | W8 design |
| Q-06 | What retention horizon applies per signal class, and who approves the storage cost that follows from it? | CTO / CFO | W8 design |
| Q-07 | Is a proactive intervention chargeable, included in the AMC, or a goodwill act? The commercial model determines whether interventions are accepted or declined | CCO / CFO | W8 design |
| Q-08 | What is the published precision threshold below which a model is suspended from customer-facing use, and who may reinstate it? | CTO / CCO | W8 design |
| Q-09 | Which failure modes are worth predicting first? Disk failure, battery degradation, thermal failure and generator failure are candidates; the answer depends on M17's accumulated fault history | Quality Manager / CTO | W8 design |
| Q-10 | Does the current telematics provider expose a standard interface, and can building-service controllers at branches emit anything at all without new hardware? | CTO / Logistics Manager / Branch Operations Lead | W8 minus 4 months |
| Q-11 | Is edge hardware — gateways at branches, sensors on generators — a capital requirement in the Wave 8 budget, and how large? | CTO / CFO | W8 minus 6 months |
| Q-12 | What does a brand partner receive in cohort reliability reporting, and has any brand agreed to receive it? This may be a significant commercial asset or a contractual problem, and the difference is worth establishing early | CCO / Quality Manager | W8 design |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §4 (**why IoT is its own module** — rows versus points, PostgreSQL
versus TimescaleDB, look-up versus aggregate), §5 (boundary map — telemetry is M48 not M17;
M26 builds the model, M48 applies it), §7 (category KPIs), §8 (M48 is late because it needs
M62), §9 (telemetry volume and consent risks) ·
`M17_Device_and_Customer_Asset_Registry.md` §3.2, §5 FR-AST-049, §10.2 ·
`M45_Enterprise_Asset_and_Test_Equipment.md` §3.2, §5 FR-EAM-032 ·
`M46_Fleet_and_Vehicle_Management.md` §3.2, §5 FR-FLT-035, §6 T-03 ·
`M47_Facility_Branch_Infrastructure_and_Workplace.md` §3.2, §5 FR-FAC-030 ·
`03_Modules/A_Service_Delivery_and_Operations/M05_Remote_Support_and_Managed_Services.md`
§3.2, §3.3, §16.3 (shared time-series platform) ·
`03_Modules/D_Circular_and_Asset_Based_Business/M13_Rental_and_Equipment_as_a_Service.md`
§3.2, §6 T-11 (ISO 15143-3 interface shape — held consistent here) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §5 (layered delivery — L4 for
standalone OSS), §10 (AS-01, AS-03, AS-08, AS-14) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category F ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §4 (TimescaleDB 2.x, Apache-2.0
only; TSL exclusion), §5.2 (CD-078, CD-079), §5.3 (telemetry collector, RMM collector),
§6 (TimescaleDB node sizing), TD-13 ·
`05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §M17 AST
(telemetry entities reallocated here) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §5
(`model_confidence`, `model_features`) ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §Wave 8

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.2 OOS-6 *(the exclusion
reversed)*, BR-CWM-002, BR-SRM-003, BR-BI-004, BR-BI-005 ·
`00_Governance_and_Charter/00-03_Scope_Expansion_Delta_v1_to_v2.md` §M17 (SOW IoT Integration
phase 2; portal roadmap IMPL-40 Predictive Maintenance Agent), §M26 ·
`1000FiX_Services_Company_Profile.md` §Corporate Services, §Value-Added Services

**External benchmark**
[SAP Asset Performance Management — predictive maintenance](https://www.sap.com/products/scm/apm.html) ·
[SAP APM with embedded Cumulocity IoT — connectivity to sensors, edge devices, historians and file-based sources](https://community.sap.com/t5/supply-chain-management-blog-posts-by-sap/sap-asset-performance-management-apm-embedded-iot-now-generally-available/ba-p/13937447) ·
[How SAP APM uses IoT and AI — signals evaluated against rules or ML models, condition monitoring and RUL](https://www.asug.com/insights/how-sap-asset-performance-management-uses-iot-and-ai-to-drive-business-results) ·
[SAP APM architecture overview](https://nttdata-solutions.com/ae-en/blog/sap-asset-performance-management-a-new-era-in-digital-asset-management/) ·
[MQTT Sparkplug B — standardised industrial payload, state awareness, birth/death certificates](https://www.symestic.com/en-us/what-is/mqtt-sparkplug-b) ·
[MQTT vs Sparkplug B — when each is appropriate](https://flowfuse.com/blog/2026/06/mqtt-vs-sparkplug-b/) ·
[OPC UA vs MQTT Sparkplug comparison](https://www.hivemq.com/resources/iiot-protocols-opc-ua-mqtt-sparkplug-comparison/) ·
[OPC UA and MQTT Sparkplug protocol comparison](https://www.emqx.com/en/blog/a-comparison-of-iiot-protocols-mqtt-sparkplug-vs-opc-ua) ·
[TimescaleDB hypertables, continuous aggregates and compression — production guide](https://www.jusdb.com/blog/timescaledb-hypertables-continuous-aggregates-guide) ·
[Data retention with continuous aggregates — dropping raw data while preserving aggregates](https://github.com/timescale/docs/blob/latest/use-timescale/data-retention/data-retention-with-continuous-aggregates.md) ·
[Downsampling in TimescaleDB — hierarchical aggregate tiers](https://oneuptime.com/blog/post/2026-02-02-timescaledb-downsampling/view) ·
[TimescaleDB compression for continuous aggregates](https://www.tigerdata.com/blog/increase-your-storage-savings-with-timescaledb-2-6-introducing-compression-for-continuous-aggregates) ·
[Building an industrial time-series platform with TimescaleDB](https://www.metafactor.ca/historians/how-to-build-a-powerful-industrial-time-series-data-platform-with-timescaledb/) ·
[ISO 13374-1 — condition monitoring and diagnostics of machines: data processing, communication and presentation](https://www.scribd.com/document/237936892/An-Introduction-to-ISO-Standard-Methodology-for-Condition-Monitoring) ·
[ISO 17359 — condition monitoring general procedures](https://committee.iso.org/home/tc251) ·
ISO 15143-3 (AEMP 2.0) — vendor-neutral equipment telematics interface

---

*Module M48 · Category F · 1000FiX ERP System v2.0 · CONFIDENTIAL*
