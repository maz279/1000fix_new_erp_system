---
id: FIX-ERP2-M62
module_id: M62
module_code: DAT
module_name: Data Platform, Warehouse & Governance
category: J — Data, Analytics & Intelligence
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Data Squad
priority: P1
wave: W4 / W8
---

# M62 — Data Platform, Warehouse & Governance
### Category J · Code `DAT` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M62 |
| **Module code** | `DAT` |
| **Category** | J — Data, Analytics & Intelligence |
| **Status** | ★ New in v2.1 — carved out of the v2.0 M25 scope after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | **W4** (core platform, Months 15–18) · **W8** (full warehouse, Months 31–34) |
| **Business owner** | Chief Technology Officer |
| **System owner** | Data Squad |
| **Delivery layers** | L3 (ELT and warehouse services) · L4 (ClickHouse, object storage, orchestration) · L5 (custom) |
| **Custom modules** | `cd_metric_registry`, `cd_warehouse_sync`, `cd_data_contract`, `cd_data_quality`, `cd_lineage_catalogue`, `cd_feature_store` |
| **Requirement range** | FR-DAT-001 … FR-DAT-038 |
| **Requirement count** | **38** *(register `02-02` estimated 34 — measured supersession, see §16.5)* |
| **Effort estimate** | **26 person-weeks** *(register estimated 22 — measured supersession)* |
| **Depends on** | M28 Integration & Event Platform · M29 Identity & Security · M64 Master Data Management · M30 Platform Administration · every module as a data source |
| **Depended on by** | **M25 Business Intelligence** · **M26 AI/ML Services** · M54 FP&A · M43 Demand Planning · M53 Revenue · M18 ESG · M60 GRC · all portals with analytics surfaces · M48 |

---

## 2. Purpose

M62 is the plumbing and the dictionary. It **moves data out of sixty-seven operational modules
into one analytical store, shapes it into a model people can query, and defines — once — what
every number in the business means.**

It does four things nobody sees and everybody depends on. It **ingests**: change data capture,
events, batch extracts and files, landed reliably and replayably. It **models**: raw operational
tables become conformed dimensions and fact tables at a declared grain. It **certifies**: every
metric — *gross margin*, *first-time fix rate*, *fleet utilisation* — has exactly one definition,
version-controlled, change-controlled, and served to every consumer from the same place. And it
**governs**: quality tests, lineage, ownership, row-level security, retention and cost.

The module exists so that the sentence *"the dashboard is wrong"* has a place to be
investigated, and so that two people quoting the same metric in the same meeting are quoting
the same number.

### Why It Exists

The v2.0 draft merged the data platform into business intelligence. Every serious data
organisation separates them, because they fail in different ways and are fixed by different
people. A data platform fails by producing numbers that are **wrong or late**. A BI tool fails
by producing numbers that are right but **unfindable or unreadable**. Merging them means the
first failure gets diagnosed as the second, and a data engineering problem is handed to someone
holding a chart editor.

The commercial case is blunter than that. The programme's benefit register commits to **BO-07
(real-time management visibility)** and **BO-17 (decisions made on live data, zero manual
reporting packs)**. Forty-plus module specifications now declare a warehouse extract to M25 and
M26 as their analytical outlet. Without M62 there is nothing on the other end of any of those
arrows.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Category J Overview §3 | The explicit split: M62 owns ingestion, transformation, the warehouse, the dimensional model, the semantic layer, quality tests, lineage and the feature store. **"A metric is defined once, in M62's semantic layer. M25 displays it. If two dashboards disagree, the defect is in M62, not in a chart."** |
| Category J Overview §5 | Boundary map: data ingestion and dimensional model → M62; metric definition → M62 semantic layer; quality tests and lineage → M62; row-level security in analytics → M62 enforcing M29 roles; feature store → M62 |
| Category J Overview §9 | KPIs owned here: data freshness < 15 min (operational) and < 60 min (warehouse), quality test pass rate > 99%, **metrics with a single certified definition 100%** |
| Category J Overview §11 | Risks owned here: two dashboards disagreeing; uncontrolled warehouse cost; personal data used in analytics without basis |
| Scope Charter §Benefit Register | **BO-07** real-time visibility · **BO-17** decisions on live data, manual packs to zero |
| `02-05` §Technology Stack | ClickHouse 24.x (analytical warehouse, W8) · MinIO (object storage) · PostgreSQL 16 · TimescaleDB (operational time series, owned elsewhere) · warehouse ETL service in Python / dbt |
| Written module specifications (40+) | Every one declares `M25 BI / M62 Data Platform — <domain> facts — Warehouse extract` as its analytical downstream. M62 is the counterparty to all of them |
| `05-06` NFR-086 / NFR-099 | Data residency: personal data held in Bangladesh; no replication of sensitive personal data to a foreign region |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree. Where this
> table says a capability belongs elsewhere, that module's specification must claim it.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Change-data-capture, event, batch, file and API ingestion from every operational source |
| 2 | Landing, replay and backfill of any source for any period without re-touching the source system |
| 3 | The medallion progression — raw landing, cleansed and conformed, modelled and served |
| 4 | The enterprise dimensional model: conformed dimensions, slowly-changing history, declared fact grain |
| 5 | The analytical warehouse itself, its partitioning, compression and query performance |
| 6 | **The semantic layer and the metric registry — the single certified definition of every business number** |
| 7 | Metric versioning, change control, deprecation and impact analysis |
| 8 | Data contracts between producing modules and the platform |
| 9 | Data quality tests, thresholds, severities and the quality incident lifecycle |
| 10 | Data observability across the four pillars: freshness, volume, schema and distribution |
| 11 | Column-level lineage from source field to dashboard tile |
| 12 | The data catalogue, business glossary, ownership and stewardship workflow |
| 13 | Row-level and column-level security in analytics, derived from M29 roles and ERP scoping |
| 14 | Personal-data classification, masking and exclusion from the analytical estate |
| 15 | Retention, downsampling, archival and purge across the analytical estate |
| 16 | Analytical platform cost measurement and control |
| 17 | The **feature store** — offline and online features, point-in-time correctness, training-serving consistency |
| 18 | Governed analytical access: SQL endpoints, extracts, sandboxes and the API surface |
| 19 | Environment, deployment and change management for all data transformation code |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Dashboards, reports, self-service exploration, subscriptions, alerting, embedded analytics** | **M25** Business Intelligence | M62 makes the number correct and available; M25 makes it visible and findable. Different discipline, different failure mode |
| **Model training, registry, serving, evaluation, drift monitoring, model governance** | **M26** AI/ML Services | M62 owns the feature store; M26 owns everything that consumes it. Stated in Category J overview §5 and not negotiable |
| **Message transport, connectors, API gateway, retry and delivery guarantees** | **M28** Integration & API Platform | M28 guarantees the event arrives; M62 decides what it means and where it lands |
| **Approval chains, scheduled business jobs, business-rule execution** | **M63** Process Automation | M62 schedules *data pipelines*; M63 schedules *business processes*. A pipeline run is not a business event |
| **Master data authorship, golden records, survivorship and match/merge rules** | **M64** Master Data Management | M64 decides which customer record is correct; M62 conforms whatever M64 publishes into a dimension |
| **Operational real-time stores — dispatch map, technician queue, live telemetry** | **M02**, **M04**, **M48** | Operational latency is an operational concern. M48 owns TimescaleDB; M62 owns the analytical archive of it |
| **Identity, authentication, role definition and entitlement** | **M29** Identity & Security | M62 *enforces* M29's roles in the analytical estate; it never defines one |
| **Statutory and regulatory report content** | Owning module (M51, M19, M18) | M62 supplies certified facts; the statutory form and its assertions belong to the module accountable for filing |
| **Operational transaction correction** | Owning module | A wrong number in the warehouse that came from a wrong number in the source is a source defect. M62 detects and reports; it never silently corrects |
| **Write-back into operational systems (reverse ETL)** | **M28** | Any analytical output that must reach an operational record travels as an event through M28, never as a direct warehouse write |
| **Infrastructure provisioning, backup, DR and platform monitoring** | **M30** Platform Administration | M62 declares its requirements; M30 runs the estate |
| **The enterprise risk register and compliance case management** | **M60** GRC | M62 raises data-governance events; GRC investigates |

### 3.3 Shared Concepts

| Concept | M62's Role | Owning Module |
|---|---|---|
| Metric definition | **Owns — the single certified source** | M62 (M25 renders, M54 registers its measures here) |
| Dimension (customer, product, technician, branch, part) | **Owns the conformed analytical dimension** | M64 / M33 / M37 own the operational master |
| Fact table and its grain | **Owns** | Producing module owns the transaction |
| Data contract | **Owns** | Producing module co-signs |
| Data quality test | **Owns for the analytical estate** | M64 owns master-data quality rules |
| Lineage | **Owns** | — |
| Feature (for models) | **Owns the store and point-in-time correctness** | M26 owns the model that consumes it |
| Row-level security policy | **Owns the analytical enforcement** | M29 owns the role and scope |
| Personal-data classification | Applies to the analytical estate | M29 / M33 own the classification scheme |
| Retention policy | **Owns for analytical data** | M24 owns document retention |
| Event schema | Consumes | M28 |
| Warehouse infrastructure | Specifies and operates the data plane | M30 runs the platform |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Datasphere** | Business data fabric: replication and federation from source systems, a business layer with semantic definitions preserving SAP business context, unified catalogue and governance | **The separation of a technical model from a business semantic layer**, and the idea that the semantic layer carries business meaning rather than table joins | Federation-first architecture. At 1000FiX's data volume, replicate-and-model is simpler, cheaper and faster than distributed query |
| **Oracle Fusion Analytics Warehouse** | Prebuilt pipelines, a curated dimensional warehouse, prebuilt KPIs with governed definitions, and extensibility for custom subject areas | **The prebuilt-KPI concept turned inward**: the Company ships its own curated subject areas per category, so a branch manager never writes a join | The prebuilt content itself — it models Oracle's ERP, not this one |
| **Microsoft Fabric / OneLake** | One logical lake, shortcuts instead of copies, workspace-level governance, an item-level lineage view | **One logical analytical estate with no per-team copies**, and workspace-scoped governance | Fabric's capacity model and the assumption of a hyperscaler |
| **Databricks lakehouse — medallion architecture** | Bronze (raw, immutable, replayable) → Silver (cleansed, conformed, deduplicated) → Gold (business-level aggregates and marts) | **The medallion progression verbatim.** Bronze is immutable and replayable, which is what makes a backfill a rerun rather than a crisis | Delta Lake and Spark. ClickHouse plus object storage carries this workload at a fraction of the operating cost |
| **Kimball dimensional modelling** | Conformed dimensions, declared fact grain, slowly-changing dimensions, bus matrix | **All of it, as the Gold-layer discipline.** A fact table without a declared grain is the root cause of most "the numbers disagree" incidents | Enterprise-wide bus-matrix design up front. Dimensions are conformed category by category as each is delivered |
| **Data Vault 2.0** | Hub/link/satellite modelling for auditability and source-system change absorption | The **satellite pattern for high-change reference data** only, where source-system volatility is high | Full Data Vault. It is the right answer at ten times this complexity and the wrong answer here — it would triple the model surface for a marginal audit gain |
| **dbt + MetricFlow (dbt Semantic Layer)** | Metric definitions as version-controlled YAML colocated with models; a change to a definition refreshes everywhere it is invoked; queries compiled to optimised SQL against the warehouse; consistency across every downstream tool | **The core architecture of §5.3.** Metrics as code in Git, reviewed like code, with CI. This is the single most important adopted decision in the module | The hosted dbt Cloud commercial layer. dbt Core plus a self-hosted metric service meets the requirement |
| **Data contracts practice** | A producing system declares schema, semantics, quality guarantees and change policy; breaking changes are caught at the producer, not the consumer | **A signed contract per producing module**, with schema-change detection failing the pipeline rather than corrupting the model | Contract enforcement at the operational API boundary — that is M28's concern |
| **Data observability practice** | Four pillars — freshness, volume, schema, distribution — monitored so a stale dashboard is detected before a stakeholder notices | **All four pillars as first-class monitors**, with a stated detection target ahead of the consumer | Buying a commercial observability platform. The four pillars are implementable on the existing stack |
| **OpenLineage** | An open standard for collecting and exchanging lineage metadata across orchestrators and transformation tools, enabling end-to-end traceability | **OpenLineage as the lineage event format**, emitted by the pipeline and the transformation layer, so lineage is a by-product of running rather than a document someone maintains | A separate commercial catalogue product at W4 |
| **Feast / feature-store practice** | Offline store for training, online store for serving, point-in-time correct joins to prevent label leakage, one definition serving both paths | **Point-in-time correctness as a hard property.** Training-serving skew is the most common silent cause of a model that tests well and performs badly | A managed feature platform |
| **ClickHouse** | Columnar analytical store with high compression, fast aggregation, and materialised views | **The warehouse engine.** Chosen in `02-05` and confirmed here for cost and single-node capability at this data volume | Cloud data warehouses. Recurring foreign-currency cost with no offsetting capability at this scale |

**Design position.** Six deliberate differences, most of them consequences of operating in
Bangladesh at this scale rather than of taste.

**First, the analytical estate stays in Bangladesh.** PDPA 2026 and NFR-086 / NFR-099 restrict
cross-border movement of sensitive personal data. That is not a configuration setting to be
applied later — it eliminates every cloud data warehouse from consideration and it is why the
platform is self-hosted ClickHouse and MinIO on Company infrastructure. The constraint is
recorded here because it will be re-litigated by every vendor who reads this document.

**Second, sensitive personal data is excluded from the warehouse by default, not masked in
it.** The default posture is that an S3-classified field does not enter the analytical estate at
all. Where an analysis genuinely needs it, a named, approved, time-limited inclusion is
recorded with its lawful basis. This is stricter than standard practice — most platforms ingest
everything and mask on read — and it is the correct posture for a company that also runs a
data-recovery laboratory and has already made a public "100% secure" commitment.

**Third, the semantic layer is code, and code is reviewed.** A metric definition lives in Git,
changes by pull request, carries a version, and cannot be altered from a dashboard. The
Category J overview's rule — *a metric is defined once* — is only enforceable if the definition
is somewhere a chart editor cannot reach. Consequently **`cd_metric_registry` belongs to M62,
not M25** *(see §16.5 and the Category J audit finding on this point)*.

**Fourth, Bronze is immutable and complete.** Cheap object storage makes it affordable to keep
every raw record permanently, which means every restatement is a rerun rather than a
reconstruction. Teams that "clean on ingest" to save storage discover eighteen months later
that a question they now need to answer was thrown away on the way in.

**Fifth, no reverse ETL.** A number computed in the warehouse never writes back into an
operational record directly. If an analytical output must change an operational state, it
travels as an event through M28 and is applied by the owning module under that module's own
rules. Direct warehouse write-back creates a second, unaudited path into the operating system
of the business.

**Sixth, freshness is a promise per subject area, not a platform-wide figure.** Some data —
dispatch, queue, cash position — matters in minutes. Some — margin by model, supplier
scorecards — matters daily. Publishing a single "freshness SLA" makes the platform either
wastefully expensive or quietly late. Each subject area carries its own declared freshness
target, published to consumers.

---

## 5. Functional Areas & Features

### 5.1 Ingestion & Pipeline Management

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DAT-001 | Change data capture | Capture inserts, updates and deletes from operational databases without polling or load on the transactional system, preserving change order and commit boundaries | P1 | L3 |
| FR-DAT-002 | Event stream ingestion | Consume domain events published through M28 and land them with their full envelope — event type, version, occurrence time, producer, correlation identifier | P1 | L3 |
| FR-DAT-003 | Batch and file ingestion | Ingest scheduled extracts, files and third-party feeds with checksum verification and duplicate detection | P1 | L3 |
| FR-DAT-004 | API ingestion | Pull from external APIs — market prices, exchange rates, emissions factors, weather — with rate limiting, retry and response archival | P2 | L3 |
| FR-DAT-005 | Immutable landing | Land every source record in Bronze in its original shape, immutably, with ingestion timestamp and source lineage, retained for the full analytical retention period | P1 | L3 |
| FR-DAT-006 | Replay and backfill | Rebuild any downstream layer for any period from Bronze, without re-reading the operational source and without manual intervention | P1 | L3 |
| FR-DAT-007 | Late-arriving and out-of-order data | Detect and correctly incorporate records arriving after their period has been processed, restating affected aggregates and recording the restatement | P1 | L3 |
| FR-DAT-008 | Pipeline orchestration | Schedule, sequence and monitor pipeline runs with dependency awareness, so a downstream model never runs against a failed upstream load | P1 | L3 |

### 5.2 Modelling & The Warehouse

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DAT-009 | Medallion progression | Maintain the three-layer progression — Bronze raw and immutable, Silver cleansed conformed and deduplicated, Gold modelled and business-ready — with each layer's contract declared | P1 | L3 |
| FR-DAT-010 | Conformed dimensions | Maintain enterprise conformed dimensions — party, product and service, asset, employee, branch, supplier, date, geography — used identically by every fact table | P1 | L3 |
| FR-DAT-011 | Slowly-changing history | Preserve dimension history so a transaction is always analysable against the attribute values in force when it happened, not today's | P1 | L3 |
| FR-DAT-012 | Declared fact grain | Require every fact table to declare its grain explicitly, and reject a model whose loaded rows do not match the declared grain | P1 | L3 |
| FR-DAT-013 | Subject-area marts | Publish curated subject areas per business domain — service, field, parts, finance, customer, commerce, circular, workforce — so a business user queries without writing joins | P1 | L3 |
| FR-DAT-014 | Warehouse performance | Partition, order, compress and materialise so that a standard subject-area query over 24 months returns within the published response target | P1 | L4 |
| FR-DAT-015 | Environment and change management | Maintain development, test and production data environments, with all transformation logic version-controlled and promoted through review and automated testing | P1 | L3 |

### 5.3 Semantic Layer & Metric Registry

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DAT-016 | Metric registry | Hold the definitive definition of every business metric — name, business definition, formula, grain, dimensions, filters, unit, owner, certification status — as version-controlled code | **P0** | L5 |
| FR-DAT-017 | Single-definition service | Serve every metric to every consumer — dashboards, reports, APIs, models, portals — from the one definition, so no consumer can compute its own variant | **P0** | L5 |
| FR-DAT-018 | Certification workflow | Certify a metric only after its owner, definition, test coverage and lineage are complete; display certification status wherever the metric appears | P1 | L5 |
| FR-DAT-019 | Versioning and change control | Version every definition change, require review and approval, record the reason, and notify every registered consumer before the change takes effect | **P0** | L5 |
| FR-DAT-020 | Impact analysis | Show, before a definition or model change is approved, every dashboard, report, model, API and portal surface that will be affected | P1 | L5 |
| FR-DAT-021 | Deprecation | Deprecate a metric with a stated successor, a transition window and consumer notification; block silent deletion of a metric in use | P1 | L5 |
| FR-DAT-022 | Business glossary | Maintain the business glossary — term, plain-language meaning, owner, synonyms, related metrics — in Bengali and English | P2 | L5 |

### 5.4 Data Quality & Observability

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DAT-023 | Data contracts | Maintain a contract per producing module declaring schema, semantics, quality guarantees, freshness commitment and change policy, co-signed by the producing module's owner | P1 | L5 |
| FR-DAT-024 | Quality test suite | Execute declarative tests on every load — uniqueness, referential integrity, not-null, accepted values, range, reconciliation to source control totals — with per-test severity | **P0** | L5 |
| FR-DAT-025 | Freshness monitoring | Monitor arrival latency per subject area against its declared freshness target, and alert before the consumer notices | **P0** | L5 |
| FR-DAT-026 | Volume monitoring | Monitor row-count deviation per load against expected ranges, detecting both silent truncation and unexpected duplication | P1 | L5 |
| FR-DAT-027 | Schema drift detection | Detect any source schema change and fail the affected pipeline rather than load a silently misaligned column | **P0** | L5 |
| FR-DAT-028 | Distribution monitoring | Monitor statistical distribution of key measures and dimension cardinality, alerting on material shifts that pass every structural test | P2 | L5 |
| FR-DAT-029 | Quality incident lifecycle | Raise, classify, assign, track and close data quality incidents, with consumer notification and a published status for any affected subject area | P1 | L5 |

### 5.5 Lineage, Catalogue & Stewardship

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DAT-030 | Column-level lineage | Record and expose lineage from source column through every transformation to every consuming metric, dashboard tile and model feature, emitted automatically as a by-product of execution | P1 | L5 |
| FR-DAT-031 | Data catalogue | Publish a searchable catalogue of every dataset, column, metric and subject area with description, owner, freshness, quality status, sensitivity classification and usage | P1 | L5 |
| FR-DAT-032 | Ownership and stewardship | Assign a named business owner and a named technical steward to every dataset and metric, and report any asset without both | P1 | L5 |

### 5.6 Security, Privacy, Retention & Cost

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DAT-033 | Row-level security | Enforce, in the analytical estate, the same scoping a user has in the ERP — own / branch / zone / entity / all — derived from M29 roles and applied to every query path including extracts | **P0** | L5 |
| FR-DAT-034 | Sensitivity classification & exclusion | Classify every column by sensitivity; **exclude S3-classified personal data from the analytical estate by default**, permitting inclusion only under a named, approved, time-limited authorisation recording its lawful basis | **P0** | L5 |
| FR-DAT-035 | Pseudonymisation and masking | Where an identifier is needed for joining but not for reading, carry it pseudonymised, with re-identification restricted, logged and approved | P1 | L5 |
| FR-DAT-036 | Retention, downsampling and purge | Apply declared retention per subject area, downsample high-volume series beyond their detail window, purge on schedule, and honour erasure requests propagated from M33 | **P0** | L5 |
| FR-DAT-037 | Platform cost measurement | Measure storage and compute consumption by subject area, pipeline and consumer, publish it monthly, and alert on trend breaches | P2 | L5 |

### 5.7 Feature Store & Governed Access

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DAT-038 | Feature store | Maintain offline features for training and online features for serving from one definition, guarantee **point-in-time correctness** on training joins, expose features by name and version to M26, and monitor training-serving consistency | P2 | L5 |

*(Governed analytical access — SQL endpoints, scheduled extracts, sandboxes and the API surface
— is delivered by FR-DAT-017, FR-DAT-031 and FR-DAT-033 acting together, and is specified as
the API surface in §12.5 rather than as separate requirements.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Bronze immutability** | Bronze is append-only. No process in the platform can update or delete a landed record; corrections arrive as new records with later ingestion timestamps |
| T-02 | **Idempotent loads** | Every load carries a deterministic key; a replayed batch produces an identical result, never a duplicate |
| T-03 | **Exactly-once semantics at the model layer** | Downstream models are built so that at-least-once delivery from M28 cannot produce double-counted facts |
| T-04 | **Declared-grain enforcement** | A fact model that produces rows finer or coarser than its declared grain fails its build; it does not load and warn |
| T-05 | **Metric definitions as code** | The metric registry is a version-controlled repository with pull-request review, CI validation and automated deployment. There is **no UI path to edit a definition** |
| T-06 | **Compile-once, serve-everywhere** | Metric queries compile to warehouse SQL through a single service; every consumer receives identically computed results |
| T-07 | **Automatic lineage emission** | Lineage events are emitted by the orchestrator and the transformation layer in **OpenLineage** format at run time; lineage is never hand-maintained |
| T-08 | **Fail-closed schema drift** | An unexpected source schema change stops the pipeline. The platform never guesses a column mapping |
| T-09 | **Row-level security at the engine** | Scoping is enforced in the query engine, not in the BI tool, so an extract, an API call and a dashboard all return the same permitted rows |
| T-10 | **Default-deny on sensitive columns** | S3-classified columns are excluded at ingestion by an allow-list mechanism; adding one requires a code change plus an approval record |
| T-11 | **Point-in-time correct feature joins** | Training feature retrieval reconstructs the feature values as at the label timestamp, structurally preventing label leakage |
| T-12 | **Backfill without source load** | Any restatement rebuilds from Bronze; no restatement re-queries an operational database |
| T-13 | **Freshness telemetry per subject area** | Every subject area publishes its own current freshness, visible to consumers and to M25's dashboard header |
| T-14 | **Query performance targets** | Standard subject-area query over 24 months ≤ 3 s; metric API resolution ≤ 800 ms; dashboard-backing query ≤ 2 s at the 95th percentile |
| T-15 | **Data residency** | All analytical storage and compute resides on Bangladesh-resident infrastructure; the platform has no configuration permitting replication of personal data to a foreign region |
| T-16 | **Erasure propagation** | An erasure instruction from M33 propagates through Bronze, Silver, Gold, the feature store and every extract, with completion evidence |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M62 |
|---|---|---|
| **CEO** | Asks three people for the same number and gets three answers | One certified definition; the disagreement becomes a data question with an owner |
| **CFO** | Reconciles the management pack to the ledger by hand each month | Certified facts traced to source, with lineage on demand |
| **Branch manager** | Waits days for branch performance data | Queries a curated subject area, scoped automatically to their own branch |
| **Business analyst** | Rebuilds the same joins in every new spreadsheet | Starts from a modelled subject area with conformed dimensions |
| **Data engineer** | *(role does not exist)* | Has a platform, tests, lineage and a change process instead of a folder of scripts |
| **Module owner (any)** | Publishes numbers nobody can reconcile to anyone else's | Signs a data contract; sees their own quality test results |
| **Data scientist (M26)** | Rebuilds features per model, with silent training-serving skew | Requests a named, versioned, point-in-time-correct feature |
| **Quality Manager** | Compiles ISO evidence from screenshots | Pulls a lineage-backed evidence extract for any period |
| **CTO** | Carries a data estate with no ownership, no retention and no cost visibility | Carries a governed estate with named owners, published retention and monthly cost |
| **Data subject (customer)** | Their data spreads through reports with no map | Classified, scoped, retained to policy, and erasable with evidence |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Enables real-time management visibility (BO-07)** | Certified, fresh, modelled data is the precondition for every dashboard M25 publishes | Branch performance data from **days → real time** |
| **Eliminates manual reporting packs (BO-17)** | A single certified source removes the reason each function maintains its own spreadsheet | Manual management reports **100% → zero by W8** |
| **Administrative labour recovered** | Analysts stop rebuilding extracts and reconciling versions of the same number | Contributes to the **BDT 62 lac/year** cross-module administrative saving |
| **Protects every downstream benefit** | Dynamic pricing (BDT 40 lac), demand forecasting (BDT 34 lac), technician productivity (BDT 130 lac) and churn reduction all depend on trustworthy data | M62 is the precondition for roughly **BDT 200 lac/year** of model- and analytics-dependent benefit |
| **Avoided rework** | Schema drift and quality failures caught at load rather than in a board meeting | Avoids the classic pattern where a quarter of reporting is republished |
| **Decision latency** | Decisions made on data hours old rather than weeks old, at every level | Unquantified but the single largest behavioural change in the programme |
| **Warehouse cost control** | Retention, downsampling and per-subject-area cost visibility from day one | Prevents the standard 3–5× uncontrolled growth in analytical storage cost |
| **Audit and tender evidence** | Lineage-backed extracts for ISO, regulator, brand partner and corporate client | Removes a recurring manual effort and a recurring credibility gap |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Ends the "whose number is right" argument permanently** | This is the single most corrosive failure in a growing company. One certified definition, versioned and owned, removes the argument rather than adjudicating it |
| **Makes data a company asset rather than a departmental one** | Ownership, stewardship and a catalogue turn tacit knowledge held by two people into an institutional capability |
| **Builds the discipline before the volume arrives** | Governance retrofitted after users lose trust is the expensive path. Delivering lineage and quality with the first subject area costs a fraction of adding it at W8 |
| **Privacy posture that survives inspection** | Default exclusion of sensitive personal data, enforced residency and propagated erasure are the practical substance of PDPA 2026 compliance in analytics |
| **Reproducibility** | Immutable Bronze means any historical figure can be reproduced exactly, years later — which is what makes a restatement explainable rather than embarrassing |
| **A hiring and retention advantage** | Data engineers do not stay where there is no platform. A governed estate is the difference between recruiting a discipline and recruiting a person |
| **Prevents the AI failure mode** | Category J overview §8 defers models to W6–W8 precisely because data must accumulate first. M62 is what makes that accumulated data usable rather than merely present |

---

## 8. Lifecycle & State Models

### 8.1 The Data Journey — Source to Certified Metric

```
  OPERATIONAL SOURCE (67 modules)
   │  CDC · domain events (M28) · batch · files · external APIs
   ▼
 ┌──────────────────────────────────────────────────────────┐
 │  BRONZE — landed, raw, immutable, replayable             │
 │  original shape · ingestion timestamp · source lineage   │
 │  ✖ S3-classified columns never arrive here (default deny)│
 └───────────────────────┬──────────────────────────────────┘
                         │  contract check · schema drift check (fails closed)
                         ▼
 ┌──────────────────────────────────────────────────────────┐
 │  SILVER — cleansed, conformed, deduplicated              │
 │  types normalised · keys resolved via M64 · SCD applied  │
 └───────────────────────┬──────────────────────────────────┘
                         │  quality test suite · declared-grain enforcement
                         ▼
 ┌──────────────────────────────────────────────────────────┐
 │  GOLD — dimensional model + curated subject areas        │
 │  conformed dimensions · facts at declared grain          │
 └───────────────────────┬──────────────────────────────────┘
                         │
                         ▼
 ┌──────────────────────────────────────────────────────────┐
 │  SEMANTIC LAYER — the metric registry                    │
 │  one definition · versioned · certified · owned          │
 └───┬────────────┬───────────────┬──────────────┬──────────┘
     │            │               │              │
     ▼            ▼               ▼              ▼
  M25 BI     M26 features     Module APIs     Portals
 dashboards  (feature store)  (M54, M43…)    (P01…P12)
     │            │               │              │
     └────────────┴───────────────┴──────────────┘
                  all row-level-security scoped from M29
```

### 8.2 Metric Definition Lifecycle

```
   PROPOSED ──► IN REVIEW ──► APPROVED ──► CERTIFIED ──► IN USE
      │             │ rejected      │                       │
      │             ▼               │                       │ definition change proposed
      │         REWORK              │                       ▼
      │                             │                 NEW VERSION ──► (re-enters review)
      │                             │                       │
      │                             │                       │ successor named
      │                             │                       ▼
      └────────────────────────────►└──────────────► DEPRECATED ──► RETIRED
                                                     (transition window,   (no consumers
                                                      consumers notified)   remain)
```

| From | To | Guard | Actor |
|---|---|---|---|
| Proposed | In Review | Definition, formula, grain, owner and unit all present | Metric author |
| In Review | Approved | Peer review passed; CI validation green; no conflict with an existing metric | Data steward |
| Approved | Certified | Quality tests cover the underlying model; lineage resolves end to end; business owner accepts | Business owner + CTO |
| Certified | New Version | Change proposed with reason and impact analysis | Metric author |
| New Version | Certified | Review, approval **and consumer notification before effect** | Data steward |
| Certified | Deprecated | Successor named; transition window set | Business owner |
| Deprecated | Retired | **Zero registered consumers remain** | System — cannot be forced |

### 8.3 Data Quality Incident

```
  TEST FAILS or MONITOR BREACHES
        │
        ▼
   RAISED ──► TRIAGED ──► ASSIGNED ──► IN INVESTIGATION
   (severity  (source vs   (owner:      │
    computed)  platform)    module or   │
                            platform)   │
                                        ├──► SOURCE DEFECT ──► routed to the owning
                                        │                       module; subject area
                                        │                       flagged degraded
                                        ├──► PLATFORM DEFECT ──► fixed, backfilled
                                        │                        from Bronze
                                        └──► EXPECTED CHANGE ──► contract amended,
                                                                 test updated
                                        │
                                        ▼
                                   RESOLVED ──► CLOSED
                                   (consumers notified, subject-area
                                    status restored, restatement recorded)
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-DAT-01 | **A business metric has exactly one definition, held in the metric registry. No consumer computes its own variant** | **H** | CTO |
| BRU-DAT-02 | A metric definition can be changed only through version-controlled review and approval; there is no UI edit path | **H** | CTO |
| BRU-DAT-03 | A metric definition change notifies every registered consumer before it takes effect | **H** | CTO |
| BRU-DAT-04 | A metric cannot be retired while any registered consumer remains | **H** | CTO |
| BRU-DAT-05 | A metric is displayed with its certification status wherever it appears | **H** | CTO |
| BRU-DAT-06 | Bronze is immutable; no process updates or deletes a landed record | **H** | CTO |
| BRU-DAT-07 | **An unexpected source schema change stops the pipeline; the platform never infers a mapping** | **H** | CTO |
| BRU-DAT-08 | Every fact model declares its grain, and a build producing a different grain fails | **H** | CTO |
| BRU-DAT-09 | Every dataset and every metric has a named business owner and a named technical steward | **H** | CTO |
| BRU-DAT-10 | Every producing module has a signed data contract before its data enters Silver | **H** | CTO |
| BRU-DAT-11 | **S3-classified personal data is excluded from the analytical estate by default**; inclusion requires named, approved, time-limited authorisation recording the lawful basis | **H** | CTO / CDO |
| BRU-DAT-12 | Analytical row-level security mirrors the user's ERP scope and is enforced in the query engine, not the presentation tool | **H** | CTO |
| BRU-DAT-13 | Re-identification of a pseudonymised identifier requires approval and is logged | **H** | CDO |
| BRU-DAT-14 | All analytical storage and compute is Bangladesh-resident; personal data is not replicated to a foreign region | **H** | CTO |
| BRU-DAT-15 | An erasure instruction propagates through every analytical layer, the feature store and all extracts, with completion evidence | **H** | CDO |
| BRU-DAT-16 | Retention is declared per subject area; data beyond its detail window is downsampled or purged on schedule | **C** | CTO |
| BRU-DAT-17 | **No analytical process writes directly into an operational system**; write-back travels as an event through M28 | **H** | CTO |
| BRU-DAT-18 | A wrong figure originating in a source system is reported to the owning module and never silently corrected in the platform | **H** | CTO |
| BRU-DAT-19 | Training feature retrieval is point-in-time correct; a feature value later than the label timestamp cannot be served | **H** | CTO |
| BRU-DAT-20 | A quality test failure at critical severity marks the subject area degraded and notifies its consumers | **H** | CTO |
| BRU-DAT-21 | Each subject area publishes its own freshness target and its current freshness | **C** | CTO |
| BRU-DAT-22 | All transformation logic is version-controlled and promoted through review and automated testing; no production change is made directly | **H** | CTO |
| BRU-DAT-23 | Analytical platform cost is measured by subject area and published monthly | **C** | CTO |
| BRU-DAT-24 | A restatement caused by late-arriving data is recorded, and any affected published figure is flagged as restated | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.data.source` | `fix_data_source` | A registered producing system or module | module_id, source_type (cdc / event / batch / api / file), connection_ref, owner_id, steward_id, active_from, state |
| `fix.data.contract` | `fix_data_contract` | The agreement with a producing module | data_source_id, version, schema_definition, semantics_note, quality_guarantees, freshness_commitment, change_policy, signed_by_producer, signed_by_platform, effective_from |
| `fix.pipeline` | `fix_pipeline` | A defined ingestion or transformation pipeline | name, layer (bronze / silver / gold), data_source_id, schedule, dependencies, owner_id, sla_minutes, state |
| `fix.pipeline.run` | `fix_pipeline_run` | One execution | pipeline_id, started_at, ended_at, outcome, rows_in, rows_out, bytes_processed, error_ref, replay_of_run_id, lineage_event_ref |
| `fix.dataset` | `fix_dataset` | A table or view in any layer | name, layer, subject_area_id, grain_declaration, row_count, storage_bytes, owner_id, steward_id, sensitivity_class, retention_policy_id, freshness_target_minutes, current_freshness_minutes, state |
| `fix.dataset.column` | `fix_dataset_column` | A column and its classification | dataset_id, name, data_type, description, sensitivity_class, pii_flag, masking_rule, inclusion_authorisation_ref |
| `fix.subject.area` | `fix_subject_area` | A curated business domain | name, category, description, owner_id, datasets, freshness_target_minutes, status (healthy / degraded), cost_month |
| `fix.dimension` | `fix_dimension` | A conformed dimension | name, natural_key, surrogate_key_strategy, scd_type, source_master_module, attribute_list, conformed_across |
| `fix.metric` | `fix_metric` | **The single certified definition** | code, name_en, name_bn, business_definition, formula, grain, allowed_dimensions, default_filters, unit, aggregation, owner_id, steward_id, certification_state, version, registry_commit_ref, superseded_by |
| `fix.metric.version` | `fix_metric_version` | Definition history | metric_id, version, change_reason, changed_by, approved_by, effective_from, impact_analysis_ref, consumers_notified_at |
| `fix.metric.consumer` | `fix_metric_consumer` | Who uses a metric | metric_id, consumer_type (dashboard / report / api / model / portal), consumer_ref, registered_at, last_invoked_at |
| `fix.glossary.term` | `fix_glossary_term` | Business glossary | term_en, term_bn, definition, owner_id, synonyms, related_metric_ids, related_dataset_ids |
| `fix.quality.test` | `fix_quality_test` | A declarative test | dataset_id, column_id, test_type, parameters, severity, enabled, owner_id |
| `fix.quality.result` | `fix_quality_result` | One test execution | quality_test_id, pipeline_run_id, executed_at, outcome, failing_row_count, sample_ref |
| `fix.quality.incident` | `fix_quality_incident` | The incident lifecycle | raised_at, source (test / freshness / volume / schema / distribution), severity, dataset_id, subject_area_id, classification (source / platform / expected), assigned_to, state, resolved_at, restatement_ref, consumers_notified |
| `fix.observability.metric` | `fix_observability_metric` | The four pillars over time | dataset_id, observed_at, freshness_minutes, row_count, schema_hash, distribution_summary, deviation_flags |
| `fix.lineage.edge` | `fix_lineage_edge` | Column-level lineage | from_dataset_id, from_column, to_dataset_id, to_column, transformation_ref, pipeline_run_id, openlineage_event_ref |
| `fix.rls.policy` | `fix_rls_policy` | Analytical scoping | dataset_id, scope_dimension, role_ref (M29), predicate, active_from |
| `fix.retention.policy` | `fix_retention_policy` | Retention and downsampling | subject_area_id, detail_window_days, downsample_rule, archive_after_days, purge_after_days, statutory_basis |
| `fix.erasure.request` | `fix_erasure_request` | Propagated erasure | source_request_ref (M33), party_id, requested_at, layers_processed, feature_store_processed, extracts_processed, completed_at, evidence_ref |
| `fix.feature` | `fix_feature` | A named, versioned feature | name, version, description, entity_type, computation, source_dataset_ids, offline_available_from, online_serving, owner_id, consuming_models |
| `fix.feature.value` | `fix_feature_value` | Offline and online feature values | feature_id, entity_key, event_timestamp, value, computed_at |
| `fix.platform.cost` | `fix_platform_cost` | Cost attribution | period, subject_area_id, pipeline_id, storage_bytes, compute_units, cost_amount |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| Every operational entity in the ERP | Owning module | Read via CDC, event or extract under contract |
| `fix.domain.event` | M28 | Consume domain events |
| `fix.role` / `fix.record.rule` | M29 | Derive analytical row-level security |
| `fix.mdm.merge` | M64 | Conform into dimensions |
| `fix.party` | M33 | Party dimension; erasure instruction source |
| `fix.consent.record` | M33 | Lawful basis for including a personal-data field |
| `fix.model.version` | M26 | Register feature consumption by model |
| `fix.environment` | M30 | Platform capacity and monitoring |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-DAT-01 | Scheduled or event-driven pipeline due | Execute in dependency order; a downstream model never runs on a failed upstream load | Halt the dependency chain; alert the pipeline owner |
| AUT-DAT-02 | Source schema change detected | **Stop the affected pipeline**, raise a schema-drift incident, notify the producing module owner and the subject area's consumers | Fail closed — never infer a mapping |
| AUT-DAT-03 | Quality test fails at critical severity | Mark the subject area degraded, publish the status to M25 dashboard headers, raise an incident, notify registered consumers | Escalate to the CTO if unacknowledged within the severity window |
| AUT-DAT-04 | Freshness target breached | Alert before the declared consumer-visible threshold; publish current freshness on the subject area | Escalate on repeated breach |
| AUT-DAT-05 | Row-count deviation beyond expected range | Raise a volume incident; hold publication of dependent Gold models pending triage | Publish with a degraded flag only on approved override |
| AUT-DAT-06 | Distribution shift detected on a key measure | Raise a distribution alert with the before/after summary and the affected metrics | Log for the weekly data review |
| AUT-DAT-07 | Late-arriving records for a closed period | Restate affected aggregates, record the restatement, flag any published figure that moved | Alert if the restatement exceeds the materiality threshold |
| AUT-DAT-08 | Metric definition change proposed | Run impact analysis; list every affected dashboard, report, model, API and portal; attach to the review | Block approval without impact analysis |
| AUT-DAT-09 | Metric definition change approved | Notify every registered consumer with the effective date, then deploy | Do not deploy before notification completes |
| AUT-DAT-10 | Metric retirement requested with consumers remaining | Block retirement; return the consumer list | Hard block |
| AUT-DAT-11 | Pipeline run completes | Emit OpenLineage events for every dataset and column touched | Alert — missing lineage is a governance defect |
| AUT-DAT-12 | New dataset or metric created without an owner or steward | Block certification; add to the stewardship worklist | Cannot be certified |
| AUT-DAT-13 | Erasure instruction received from M33 | Propagate through Bronze, Silver, Gold, feature store and extracts; record evidence | Escalate immediately — an incomplete erasure is a regulatory failure |
| AUT-DAT-14 | Retention window elapses for a subject area | Downsample, archive or purge per policy; record the action | Escalate; retained-beyond-policy data is a control failure |
| AUT-DAT-15 | Attempt to ingest an S3-classified column not on the authorised list | Reject at ingestion, log, alert the CDO | Fail closed |
| AUT-DAT-16 | Backfill or replay requested | Rebuild from Bronze for the stated period; recompute dependent models; record the restatement | Never re-query the operational source |
| AUT-DAT-17 | Monthly | Publish platform cost by subject area, pipeline and consumer; alert on trend breach | Log for the CTO review |
| AUT-DAT-18 | Feature requested for training | Serve point-in-time correct values as at the label timestamp | Reject a request that would leak future values |
| AUT-DAT-19 | Training-serving skew detected on a feature | Alert M26 and the feature owner with the divergence measure | Escalate — skew invalidates the model, not the feature |
| AUT-DAT-20 | Data contract breach by a producing module | Raise the incident against the producing module, notify its owner, degrade the subject area | Escalate to the category owner |

---

## 12. Interfaces

### 12.1 Upstream — M62 Consumes

| Source | What | Mechanism |
|---|---|---|
| **All 67 modules** | Operational records under a signed data contract | CDC · domain events via M28 · batch extract · file |
| M28 Integration & Event Platform | Domain event streams with envelope and schema registry | Event subscription |
| M29 Identity & Security | Roles, scopes and entitlements used to derive analytical row-level security | Service |
| M64 Master Data Management | Golden records and survivorship results, conformed into dimensions | REST + event |
| M33 Party Master | Party dimension source; consent and erasure instructions | REST + event |
| M30 Platform Administration | Infrastructure capacity, monitoring and backup services | Service |
| M48 IoT Telemetry | Aggregates and selected raw series for long-term analytical retention | Extract |
| External APIs | Market prices, exchange rates, emissions factors | REST |

### 12.2 Downstream — M62 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M25 Business Intelligence** | Curated subject areas, certified metrics via the semantic layer, freshness and quality status, row-level security enforcement | Metric API + governed SQL |
| **M26 AI/ML Services** | Point-in-time correct training features, online serving features, labelled outcome data, model evaluation datasets | Feature API + extract |
| M54 Cost Accounting & FP&A | Certified financial measures and the dimensional projection its analytics run against | Warehouse + metric API |
| M43 Demand Planning | Governed consumption history and demand-stream separation | Extract |
| M53 Revenue Recognition | Period-stamped certified ledger extract | Warehouse |
| M18 E-Waste & ESG | Certified data underlying GRI-structured metrics | Warehouse |
| M60 GRC | Data-governance events, access anomalies, retention exceptions | Events |
| M23 Quality | Quality incident data and lineage-backed audit evidence | Extract |
| All portals (P01–P12) | Scoped analytical surfaces through M25 | Via M25 |
| M28 | Analytical outputs destined for operational write-back, as events | Event |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `data.subject_area_refreshed` | subject area, freshness, run reference | M25, M26 |
| `data.subject_area_degraded` | subject area, cause, severity, affected metrics | **M25**, M26, consumers |
| `data.subject_area_restored` | subject area, incident reference, restatement | M25, M26 |
| `data.quality_incident_raised` | dataset, test, severity, classification | M23, M60, module owner |
| `data.schema_drift_detected` | source, dataset, column, change | **producing module**, M60 |
| `data.contract_breached` | producing module, contract clause, evidence | producing module, M60 |
| `metric.certified` | metric, version, owner, definition | M25, M26, M54 |
| `metric.definition_changed` | metric, old version, new version, effective date, impact list | **all registered consumers** |
| `metric.deprecated` | metric, successor, transition window | all registered consumers |
| `data.restatement_recorded` | subject area, period, cause, materiality | M25, M19, M54 |
| `data.erasure_completed` | party, layers processed, evidence | **M33**, M60 |
| `feature.published` | feature, version, entity type, availability | M26 |
| `feature.skew_detected` | feature, model, divergence measure | **M26** |
| `data.cost_published` | period, subject area, storage, compute, amount | M54, M30 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-DAT-01 | Operational PostgreSQL instances (CDC) | Inbound | Change data capture without transactional load |
| INT-DAT-02 | Object storage (MinIO) | Bidirectional | Bronze landing and long-term archive |
| INT-DAT-03 | ClickHouse analytical warehouse | Bidirectional | Silver and Gold storage and query |
| INT-DAT-04 | Git repository and CI | Bidirectional | Transformation and metric definitions as code |
| INT-DAT-05 | OpenLineage-compatible lineage store | Outbound | Lineage event emission and query |
| INT-DAT-06 | External reference feeds (FX, market price, emissions factors) | Inbound | Reference data for modelled measures |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/metrics` | GET | List certified metrics with definition, owner, unit and status | M25, M26, portals |
| `/api/v1/metrics/{code}/query` | POST | **Resolve a metric for given dimensions, filters and period — the single computation path** | M25, M54, portals, APIs |
| `/api/v1/metrics/{code}/lineage` | GET | Full lineage from source column to this metric | M25, audit |
| `/api/v1/metrics/{code}/impact` | GET | Every consumer affected by a change to this metric | Change review |
| `/api/v1/subject-areas` | GET | Subject areas with freshness, quality status and owner | M25, M26 |
| `/api/v1/datasets/{id}/quality` | GET | Test results and observability state | M25, M23 |
| `/api/v1/catalogue/search` | GET | Search datasets, columns, metrics and glossary terms | Analysts |
| `/api/v1/features/{name}/training` | POST | **Point-in-time correct feature retrieval for a label set** | M26 |
| `/api/v1/features/{name}/serve` | GET | Online feature values for inference | M26 |
| `/api/v1/extracts` | POST | Request a governed, row-level-security-scoped extract | Analysts, corporate clients |
| `/api/v1/pipelines/{id}/replay` | POST | Replay or backfill a period from Bronze | Data engineer |
| `/api/v1/governance/erasure` | POST | Propagate an erasure instruction | M33 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R02 Chief Technology Officer** | C R U D A | All — platform, metrics, contracts, cost, governance |
| Data Engineer | C R U | Pipelines, datasets, transformation code (through review); **cannot certify a metric alone** |
| Data Steward | C R U A | Metric review and approval, catalogue, glossary, stewardship worklist |
| Metric Business Owner *(by domain)* | R A | Approves the business definition and certification of metrics in their domain |
| **CDO / Data Protection Officer** | R U A | Sensitivity classification, S3 inclusion authorisation, re-identification approval, erasure evidence, residency assurance |
| Business Analyst | R | Curated subject areas and certified metrics, **row-level-security scoped**; sandbox schema for exploration |
| R32 Quality Manager / ISO Coordinator | R | Quality incidents, lineage-backed evidence extracts |
| Module Owner *(any)* | R U | Own module's data contract, own quality test results, own schema-drift incidents |
| Data Scientist *(M26)* | R | Feature store, training extracts, evaluation datasets — **scoped, and never S3 data** |
| R33 IT / System Administrator | — | Infrastructure only; **no access to analytical content** |
| R26 Finance Manager | R | Finance subject areas and platform cost |
| External Auditor | R | Time-boxed, read-only, scoped evidence extract |

**Field-level restrictions.** S3-classified columns are absent from the estate by default; where
authorised, they are visible only to the named individuals on the inclusion authorisation.
Pseudonymised identifiers cannot be re-identified without a logged, approved request. Platform
cost detail is visible to the CTO, CFO and Finance only.

**Segregation of duties.**

| Incompatible combination | Why |
|---|---|
| Metric author **and** metric certifier | A definition must be reviewed by someone who did not write it |
| Data engineer **and** sensitivity-classification approver | Convenience must not be able to reclassify personal data downward |
| Pipeline developer **and** production deployment approver | All change goes through review; nobody promotes their own code |
| Analytical access **and** infrastructure administration | The administrator runs the estate; they do not read its contents |
| Re-identification requester **and** re-identification approver | The control is the second signature |

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Platform health board | Data Squad, CTO | Real time | Pipeline runs, failures, freshness by subject area, degraded areas, incident queue |
| Freshness board | All consumers, M25 header | Real time | Current freshness against target, per subject area, published to every dashboard |
| Data quality scorecard | CTO, module owners | Daily | Test pass rate by dataset and by producing module; failing tests by severity |
| Metric certification register | CTO, business owners | Weekly | Every metric, its owner, version, certification status and consumer count |
| Uncertified metric report | CTO | Weekly | Metrics in use without certification, and datasets without an owner or steward |
| Metric change log | All consumers | On change | What changed, why, effective when, and what it affects |
| Lineage explorer | Analysts, auditors, Quality | On demand | Source column → transformation → metric → dashboard tile, both directions |
| Data contract compliance | CTO, category owners | Monthly | Breaches by producing module, schema drift incidents, freshness misses |
| Sensitivity and privacy register | CDO, GRC | Monthly | Classified columns, active inclusion authorisations, re-identification events, erasure completions |
| Retention compliance | CDO, Quality | Monthly | Subject areas past detail window, downsampling executed, purges completed, exceptions |
| Platform cost report | CTO, CFO | Monthly | Storage and compute by subject area, pipeline and consumer; trend and forecast |
| Restatement log | CFO, CTO, M25 | Per event | Late-arriving-data restatements, periods affected, materiality, figures that moved |
| Feature store health | M26, Data Squad | Weekly | Feature availability, serving latency, training-serving skew measures |
| Adoption report | CTO | Monthly | Queries by subject area and role, unused datasets, catalogue search patterns |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | Data freshness — operational subject areas | n/a | < 30 min | **< 15 min** |
| — | Data freshness — warehouse subject areas | n/a | < 120 min | **< 60 min** |
| **KPI-093** | Data quality test pass rate *(register attributes this to M25; owned here — see §15 note)* | n/a | > 97% | **> 99%** |
| — | **Metrics with a single certified definition** | 0% | 80% | **100%** |
| — | Datasets with a named owner and steward | 0% | 90% | **100%** |
| — | Producing modules with a signed data contract | 0% | 70% | **100%** |
| — | Metric definition changes deployed without consumer notification | n/a | **0** | **0** |
| — | Pipelines loading after an undetected schema change | n/a | **0** | **0** |
| — | S3-classified columns in the estate without authorisation | n/a | **0** | **0** |
| — | Erasure instructions completed with evidence | n/a | **100%** | **100%** |
| — | Column-level lineage coverage of certified metrics | 0% | 85% | **100%** |
| — | Restatements exceeding the materiality threshold | n/a | < 2/quarter | **< 1/quarter** |
| — | Standard subject-area query p95 response | n/a | < 5 s | **< 3 s** |
| — | Metric API resolution p95 | n/a | < 1.5 s | **< 800 ms** |
| — | Analytical platform cost per subject area | unmeasured | Published | **Within approved envelope** |
| — | Training-serving skew incidents | n/a | — | **0 undetected** |

> **KPI ownership note.** `06-02` §2.7 attributes **KPI-093 (data quality test pass rate)** and
> **KPI-094 (manual management reports remaining)** to **M25**. Under the v2.1 split, KPI-093 is
> instrumented and owned **here in M62** — data quality is a platform property, not a
> presentation one. KPI-094 remains with **M25**. Raised as an audit action.

**Six of these targets are zero or one hundred per cent.** Certification coverage, notification,
schema-drift blocking, unauthorised personal data and erasure completion are controls. A
partial score on any of them is a defect with a percentage attached.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L3 | ELT and transformation services — CDC, event consumers, dbt-style transformation, orchestration | 30% |
| L4 | ClickHouse warehouse, MinIO object storage, lineage store, feature store infrastructure | 22% |
| L5 | `cd_metric_registry`, `cd_warehouse_sync`, `cd_data_contract`, `cd_data_quality`, `cd_lineage_catalogue`, `cd_feature_store` | 48% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-110** | `cd_metric_registry` — metric definitions as code, certification workflow, versioning and change control, impact analysis, deprecation, glossary, metric resolution service | Service + Odoo surface | **7 PW** |
| **CD-111** | `cd_warehouse_sync` — CDC and event ingestion, Bronze landing, replay and backfill, late-arriving handling, medallion transformation framework, subject-area publication | Python / dbt service | **6 PW** |
| **CD-187** | `cd_data_contract` — contract definition and signing, schema-drift detection, contract compliance monitoring and breach routing | Service + Odoo surface | 3 PW |
| **CD-188** | `cd_data_quality` — declarative test suite, four-pillar observability, incident lifecycle, degraded-status publication, consumer notification | Service + Odoo surface | 4 PW |
| **CD-189** | `cd_lineage_catalogue` — OpenLineage emission and store, column-level lineage graph, catalogue, ownership and stewardship worklist | Service + Odoo surface | 3 PW |
| **CD-190** | `cd_feature_store` — offline and online feature definition, point-in-time correct retrieval, serving API, skew monitoring | Service | 3 PW |
| | **Total** | | **26 PW** |

> **CD reallocation.** `02-05` §5.2 allocated **CD-110 `cd_metric_registry`** and
> **CD-111 `cd_warehouse_sync`** to **M25** under the v2.0 merged scope. Both are reallocated to
> **M62** under the v2.1 split, because the metric registry *is* the semantic layer and the
> warehouse sync *is* the pipeline. **CD-112 `cd_embedded_analytics` remains with M25.**
> CD-187…190 are claimed from the extension block; Category G's block ends at **CD-186**, so
> Category J starts cleanly at **CD-187**. Raised as an audit action against `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M28 Integration & Event Platform (W1)** | Event streams and schema registry are the primary ingestion path |
| **M29 Identity & Security (W1)** | Analytical row-level security derives from M29 roles and scopes |
| M30 Platform Administration (W1) | Infrastructure, backup and monitoring for the data plane |
| M64 Master Data Management (W2) | Golden records are the source of conformed dimensions |
| M33 Party Master (W1) | Party dimension, consent and erasure instruction source |
| **M62 core must land in W4, with M25** | Forty-plus module specifications declare a warehouse extract; W4 is when the first of them go live with management reporting |
| M62 full warehouse in W8 | Full dimensional coverage, feature store at scale, and the analytical depth M26's later models require |

**Wave split.** W4 delivers ingestion, Bronze and Silver, the first Gold subject areas
(service, field, finance, customer), the metric registry, quality tests and lineage. W8 delivers
the remaining subject areas, the feature store at production scale, distribution monitoring and
full cost attribution. The metric registry is **W4, not W8** — a semantic layer added after
dashboards exist is a semantic layer nobody adopts.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing operational data at each module's cutover | Full history where the source retains it | Bronze, then modelled forward | Per module wave |
| Existing management spreadsheets | **Not migrated as data** — harvested as *requirements*: each recurring spreadsheet is decomposed into the metrics it computes, which are then defined once in the registry | Metric registry | W4 |
| Legacy report definitions | **Not migrated** — reproduced against certified metrics | — | W4 |

**Migration note.** The most valuable artefact in the current estate is not the data in the
spreadsheets; it is the **definitions buried in their formulas**. Harvesting those definitions —
and forcing the disagreements between them into the open before they are certified — is the
real migration work, and it is a business exercise, not a technical one.

### 16.5 Register Variance

| Figure | `02-02` Estimate | Measured | Variance |
|---|---:|---:|---|
| Requirements | 34 | **38** | +12% — data contracts, observability pillars and erasure propagation were not separable in the estimate |
| Effort | 22 PW | **26 PW** | +18% — concentrated in the metric registry (7 PW), which the estimate treated as part of BI |

Both figures are measured supersessions of the register estimate and require `02-02` §2
Category J to be updated. Raised as an audit action.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **A metric has exactly one definition, and no consumer can compute a variant** — two dashboards, an API call and a model feature return an identical figure for the same metric, dimensions and period | Four-way comparison test |
| AC-02 | A metric definition cannot be edited through any user interface | Negative test through UI, API and database role |
| AC-03 | A metric definition change notifies every registered consumer before it takes effect | Sequence test |
| AC-04 | A metric with registered consumers cannot be retired | Negative test |
| AC-05 | An unexpected source schema change stops the pipeline and raises an incident; no misaligned column loads | Injected schema-change test |
| AC-06 | A fact model producing rows at a grain other than declared fails its build | Negative test |
| AC-07 | Bronze cannot be updated or deleted by any process in the platform | Negative test at the storage layer |
| AC-08 | Any Gold subject area can be rebuilt for any past period from Bronze alone, without touching an operational source | Backfill test with the source disconnected |
| AC-09 | Late-arriving records restate affected aggregates, and the restatement is recorded and flagged | Injected late-arrival test |
| AC-10 | **An S3-classified column cannot enter the estate without a named, approved, time-limited authorisation** | Negative ingestion test |
| AC-11 | Analytical row-level security returns identical permitted rows through a dashboard, an extract and an API call for the same user | Three-way scoping test across four role types |
| AC-12 | Re-identification of a pseudonymised identifier requires approval and is logged | Negative test plus audit review |
| AC-13 | An erasure instruction propagates through Bronze, Silver, Gold, feature store and extracts, with completion evidence | End-to-end erasure test |
| AC-14 | Column-level lineage resolves from any certified metric back to every source column, and is emitted automatically at run time | Lineage trace on 20 metrics |
| AC-15 | Impact analysis lists every affected consumer before a definition change is approved | Change-review test |
| AC-16 | A critical quality test failure marks the subject area degraded and the status appears on consuming dashboards | End-to-end degradation test |
| AC-17 | **Training feature retrieval cannot return a value later than the label timestamp** | Point-in-time correctness test with deliberately future values |
| AC-18 | Training-serving skew on a feature is detected and reported | Injected skew test |
| AC-19 | No analytical process can write directly into an operational database | Negative test at the connection layer |
| AC-20 | Retention, downsampling and purge execute on schedule per subject area, with evidence | Scripted scenario over a compressed clock |
| AC-21 | All analytical storage and compute is Bangladesh-resident, with no configuration path to foreign replication | Configuration review and negative test |
| AC-22 | Standard subject-area query over 24 months returns within the published target at p95 | Load test |
| AC-23 | Every dataset and metric in production has a named owner and steward | Register audit |
| AC-24 | CTO and the Data Steward sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 24 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Who is the Chief Data Officer / Data Protection Officer?** PDPA 2026 requires the appointment, and this module places S3 inclusion authorisation, re-identification approval and erasure evidence on that role. It is currently unfilled | CEO / CTO | **W4 minus 3 months** |
| Q-02 | **Does the Company have data engineering capability, or must it be hired?** The programme has no data engineer role in `05-04`. A platform without an owner degrades within two quarters | CTO / HR Director | **W4 minus 4 months** |
| Q-03 | What is the analytical retention policy per subject area, and what statutory minimum applies to each? PDPA 2026 requires five-year processing records; tax requires longer for some | CDO / CFO / Legal | W4 build |
| Q-04 | What is the approved infrastructure envelope — storage and compute — and what happens when a subject area exceeds it? | CTO / CFO | W4 minus 2 months |
| Q-05 | Which subject areas genuinely need sub-15-minute freshness, and which are being asked for out of habit? Each one carries a real cost | CTO / category owners | W4 build |
| Q-06 | **Which existing management spreadsheets must be harvested for metric definitions, and who arbitrates when two of them define the same metric differently?** This is the highest-value and most politically difficult task in the module | CEO / CFO | **W4 minus 2 months** |
| Q-07 | Is CDC permitted against production databases, or must ingestion use read replicas? This determines infrastructure sizing | CTO | W4 minus 2 months |
| Q-08 | Which personal-data fields are genuinely required for analytics, and what is the lawful basis for each? The default is exclusion | CDO / Legal | W4 build |
| Q-09 | Does the Company hold, or intend to hold, ISO 27001? Analytical access control and retention are among the most-tested controls | Quality Manager / CTO | W8 |
| Q-10 | **The metric registry ownership conflict.** `M54` §3.2 places the metric registry on **M25**; Category J overview §5 and this specification place it on **M62**. `02-05` allocates `cd_metric_registry` to M25. Which is authoritative? *(This specification takes the M62 position, per the overview's explicit rule)* | CTO | **W4 minus 2 months** |
| Q-11 | Is `05-01`'s FR prefix `DAT` accepted for this module, given it was not in the 30-module allocation? | Programme Director | W4 build |
| Q-12 | Will the Bengali business glossary be maintained by the data team or by the business owners? Translation drift in metric names is a real and underestimated risk | CTO / Quality Manager | W4 build |

**Q-01 and Q-02 are not design questions.** They are staffing and accountability gaps that
determine whether this module survives its first year.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` (Category J §3 the platform/BI split, §5 boundary map, §9 KPIs, §11 risks) ·
`M25_Business_Intelligence_and_Reporting.md` (the presentation consumer) ·
`M26_AIML_Services_and_Model_Operations.md` (the feature-store consumer) ·
`M63_Process_Automation_and_Workflow_Orchestration.md` ·
`03_Modules/G_Finance_and_Treasury/M54_Cost_Accounting_Budgeting_and_FPA.md` §3.2, T-15, BRU-FPA-20
*(metric registry ownership — see §18 Q-10)* ·
`03_Modules/F_Asset_Equipment_and_Facilities/M48_IoT_Telemetry_and_Predictive_Maintenance.md`
*(operational time series versus analytical archive)* ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §Category J ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §Technology Stack, §5.2 CD allocation ·
`05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` NFR-086, NFR-099 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` (BO-07, BO-17, KPI-093, KPI-094)

**Workspace evidence**
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §Benefit Register ·
`ERP system for 1000 fix/project_implementation_doc/03_Database_Schema_Data_Model_Specification.md` ·
`ERP system for 1000 fix/project_implementation_doc/14_n8n_Workflow_Specifications.md`

**External benchmark**
**SAP Datasphere** — business data fabric with a semantic business layer preserving business
context above the technical model ·
**Oracle Fusion Analytics Warehouse** — curated dimensional warehouse with prebuilt, governed KPI
definitions and extensible subject areas ·
**Microsoft Fabric / OneLake** — one logical lake, shortcuts instead of copies, workspace
governance and item-level lineage ·
**Databricks medallion architecture** — Bronze raw and immutable, Silver cleansed and conformed,
Gold business-ready ·
**Kimball dimensional modelling** — conformed dimensions, declared fact grain, slowly-changing
dimensions ·
**Data Vault 2.0** — satellite pattern for volatile reference data ·
**dbt Semantic Layer / MetricFlow** — metric definitions as version-controlled YAML colocated
with models; a definition change refreshes everywhere it is invoked; compiled to optimised
warehouse SQL; consistency across all downstream tools ·
**Data contracts practice** — producer-declared schema, semantics, quality and change policy,
with breaking changes caught at the producer ·
**Data observability** — the four pillars: freshness, volume, schema and distribution, detected
before a stakeholder notices ·
**OpenLineage** — open standard for collecting and exchanging lineage metadata across
orchestration and transformation tools ·
**Feature store practice (Feast)** — offline and online stores from one definition, with
point-in-time correct joins preventing label leakage ·
**ClickHouse** — columnar analytical engine selected in `02-05` for cost and single-node capability

**Sources consulted**
- [dbt Semantic Layer documentation](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)
- [Atlan — dbt Semantic Layer, MetricFlow, setup and examples](https://atlan.com/dbt-semantic-layer/)
- [Top semantic layer tools 2026 — comparison](https://promethium.ai/guides/top-10-semantic-layer-tools-2026-definitive-comparison/)
- [What belongs in a modern data platform in 2026 — reference architecture](https://bigdataboutique.com/blog/modern-data-platform-2026)
- [Data quality and observability — testing, monitoring, lineage, data contracts](https://mayursurani.medium.com/data-quality-observability-testing-monitoring-lineage-data-contracts-1db08e604306)
- [The definitive guide for data observability 2026](https://www.dqlabs.ai/blog/the-definitive-guide-for-data-observability-2026/)
- [Top open-source data quality and observability tools 2026](https://www.digna.ai/top-open-source-data-quality-observability-tools-to-watch-in-2026)

---

*Module M62 · Category J · 1000FiX ERP System v2.0 · CONFIDENTIAL*
