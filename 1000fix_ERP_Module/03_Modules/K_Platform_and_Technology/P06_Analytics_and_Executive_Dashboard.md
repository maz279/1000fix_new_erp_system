---
id: FIX-ERP2-P06
portal_id: P06
portal_code: AED
portal_name: Analytics & Executive Dashboard
type: Embedded Analytics Surface
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Data & Intelligence Squad
priority: P1
wave: W4
---

# P06 — Analytics & Executive Dashboard
### Portal Suite · Code `AED` · Existing (expanded in v2.1)

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P06 |
| **Portal code** | `AED` |
| **Type** | Embedded analytics surface over governed datasets |
| **Status** | Existing (expanded in v2.1 — from 6 dashboards to functional coverage of all 67 modules, plus real-time operations and mobile) |
| **Priority** | **P1** |
| **Delivery wave** | **W4** (Months 14–18) |
| **Users** | Executives, directors, branch managers, functional managers |
| **Volume** | **25–60 users** — the smallest audience, the highest decision leverage |
| **Business owner** | Chief Technology Officer |
| **System owner** | Data & Intelligence Squad |
| **Technology** | Metabase (governed self-service BI) + Grafana (real-time operations) embedded in P03 |
| **Custom development** | `CD-206` |
| **Requirement range** | FR-POR-171 … FR-POR-194 |
| **Requirement count** | **24** *(measured — supersedes the 7 allocation in `05-01` §4)* |
| **Effort estimate** | **16 person-weeks** |
| **Backing modules** | **M25 Business Intelligence** (primary) · **M62 Data Platform** (datasets) · all 67 as sources |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M62 Data Platform · M64 MDM |

---

## 2. Purpose

P06 is **where the Company decides**. It is the smallest audience in the suite — 25 to 60
people — and the only surface whose output is a decision rather than a transaction.

Its purpose is stated most sharply by its own KPI in `04-00`: *decisions made on live data
rather than compiled spreadsheets — 100% of management reviews*. That is the whole point. The
Company currently manages 51+ branches and fourteen revenue streams from spreadsheets compiled
after the fact by people who could be doing something else. P06 replaces the compilation, not
just the presentation.

P06 holds no authoritative state and — unusually — it holds no business logic either. Every
number it shows is computed by M25 against datasets governed by M62. What P06 owns is
**the presentation, the drill path and the row-level security that makes one surface safe for a
CEO and a branch manager simultaneously**.

### Why It Exists

**Management reporting is a full-time job nobody was hired to do.** `04-00` targets a 90%
reduction in manual management reporting effort. Across branch managers, functional managers
and finance, the compilation of weekly and monthly reports is a measurable and substantial cost
that produces numbers already out of date when they are read.

**Fourteen revenue streams cannot be managed on one P&L.** The v2.1 scope adds rental,
refurbishment, marketplace, managed services, data services, e-waste and parts retail. Each has
different unit economics. A group view that cannot decompose to a stream, a branch and a job is
not a management instrument.

**51+ branches need to be comparable.** BR-BI-002 requires branch performance dashboards
comparing all locations. Comparison is what turns 51 independent operations into a managed
network — and it is impossible without one definition of every metric, which is precisely what
a governed semantic layer provides and a spreadsheet does not.

**Real-time operations and periodic analysis are different problems.** A dispatch manager
watching SLA countdowns needs sub-second refresh on operational state. A CFO analysing margin
by stream needs a governed, reconciled, historically consistent dataset. Serving both from one
tool produces something that does neither well — which is why P06 deliberately uses two.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §4.1 Portal 6 | "Analytics Dashboard — 15-25 management users — executive dashboards, branch performance, trend analysis" |
| ERP BRD BR-BI-001 | "Real-time executive dashboard with configurable KPIs" |
| ERP BRD BR-BI-002 | "Branch performance dashboards comparing all 51+ locations" |
| ERP BRD BR-BI-003 | Technician performance: jobs/day, first-time fix, CSAT, rework, earnings |
| ERP BRD BR-BI-004 | Service analytics: TAT, common faults, parts consumption, rework |
| ERP BRD BR-BI-005 | Inventory analytics: turnover, dead stock, inter-branch movement, stockout frequency |
| ERP BRD BR-BI-006 | Financial analytics: revenue by service type, brand and branch; profitability; cash flow |
| ERP BRD BR-BI-007 | "Custom report builder with drag-and-drop interface" |
| ERP BRD BR-BI-008 | "Scheduled report generation and email distribution" |
| ERP BRD BR-BI-009 | Export to PDF, Excel and CSV |
| ERP BRD BR-BI-010 | Warranty claim analytics by brand, approval rate, ageing, revenue realisation |
| ERP BRD NFR-005 | "Standard reports shall generate within 30 seconds" |
| `04-00` §P06 | Capability set across eight areas and four KPIs, adopted verbatim |
| `04-00` §3 PS-01…PS-12 | Twelve cross-portal standards, all binding |
| `02-05` §4 | Metabase and Grafana in the approved open-source stack; TimescaleDB for time series |
| `05-04` §2 | 17 roles hold P06 access — all management, no operational or external role |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The executive dashboard: group performance across all revenue streams |
| 2 | Branch league tables comparing all 51+ locations on every operational and financial dimension |
| 3 | Functional dashboards for service, field, inventory, finance, HR, quality, warranty, contracts, marketplace, assets and managed services |
| 4 | Real-time operations board: open jobs, technicians on map, SLA countdowns, queue health, system health |
| 5 | Drill-through from any aggregate to the underlying records in P03 |
| 6 | Governed self-service: building analyses on certified datasets without SQL |
| 7 | Row-level and column-level security applied to every dataset and every user |
| 8 | Scheduled report generation, subscription and distribution |
| 9 | Export to PDF, Excel and CSV within the user's data scope |
| 10 | Threshold and anomaly alerting delivered to the accountable role |
| 11 | Mobile-optimised presentation of key dashboards |
| 12 | Metric definition transparency: what a number means and where it came from |
| 13 | Data freshness indication on every view |
| 14 | Embedded analytical panels inside P03 consoles and P04 client views |
| 15 | Instrumentation of usage, adoption and decision support |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Metric definition, calculation and the semantic layer** | **M25** Business Intelligence & Reporting | P06 presents a metric; M25 defines what it means. **One definition, one owner** — this is the boundary that prevents two dashboards disagreeing |
| **The data warehouse, lakehouse, ETL, modelling and data quality** | **M62** Data Platform, Warehouse & Governance | P06 queries certified datasets; it never transforms |
| **Operational lists, queues and work** | **P03** Admin Operations Portal | A console is for acting, a dashboard for deciding. P06 shows a number; P03 shows the work behind it |
| **Machine-learning models, forecasts and predictions** | **M26** AI/ML Services | P06 displays a forecast M26 produced; it never fits a model |
| **Telemetry ingestion and time-series storage** | **M48** IoT & Predictive | Grafana reads the time-series store; it does not own it |
| **Client-facing analytics** | **P04** (corporate), **P07** (seller), **P08** (brand) | Each external audience gets its own scoped surface; **no external party has P06 access** |
| **Financial statements, statutory reporting and the close** | **M19 / M51** | P06 analyses; the ledger reports |
| **Regulatory and tax submissions** | **M51** | Never from a BI tool |
| **Identity, roles and record rules** | **M29** | P06 applies row-level security derived from M29; it defines no permission |
| **Platform and infrastructure observability** | **M30** with **M28** | Grafana serves both; the platform-health estate is M30's, the business real-time board is P06's |

### 3.3 Shared Concepts

| Concept | P06's Role | Owning Module |
|---|---|---|
| Presentation, drill path and dashboard composition | **Owns** — the defining concern of this portal | P06 |
| Row-level and column-level security enforcement | **Owns** the enforcement; M29 supplies the scope | P06 / M29 |
| Metric definition and semantic layer | Consumes | **M25** |
| Certified dataset | Consumes | **M62** |
| Real-time operational state | Presents | The owning operational module |
| Forecast and prediction | Presents | M26 |
| Time-series telemetry | Presents | M48 |
| Scheduled distribution | Owns the schedule; M27 delivers | P06 / M27 |
| Alert threshold | Owns the definition on a metric; M27 delivers | P06 / M27 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Metabase** | Visual query builder with the lowest barrier to entry for non-technical users; collection-level permissions and RBAC in the community edition; embedding with SSO and row-level security | **The visual query builder as the self-service surface**, because the audience is 25–60 managers, not analysts. A tool requiring SQL produces a self-service capability nobody uses and an analytics team that becomes a bottleneck | — but see the design position below on **row-level security licensing**, which is a genuine constraint |
| **Grafana** | Battle-tested for time-series, infrastructure metrics and operational observability; organisation, folder and datasource permissions | **Grafana for the real-time operations board only** — SLA countdowns, technicians on map, queue health, system health — which is exactly what it is excellent at | **Grafana as the business BI surface.** It has no semantic layer for consistent metric definitions, does not provide governed self-service for business users, and enforces business row filtering in the backend rather than the tool. Using it for management analytics would put metric definitions in dashboard queries — the precise failure this architecture exists to prevent |
| **Apache Superset** | The most comprehensive built-in security of the open-source options: RBAC, **row-level security**, dataset-level permissions and OAuth/SAML **all in the open-source edition** | **Superset is the fallback if Metabase's row-level security licensing proves unacceptable.** This is recorded as an explicit open question (Q-02) rather than discovered during build | Superset's steeper learning curve for a 25–60 manager audience, which is why it is the fallback and not the default |
| **Embedded analytics practice** | Analytics delivered inside the operational application rather than as a separate destination; SSO, permissions and RLS carried through the embed | **Embedding into P03 consoles and P04 client views.** A manager who must leave their working surface to see a number checks it weekly; a manager who sees it in their console acts on it daily | Customer-facing embedded analytics as a product |
| **Semantic-layer practice (dbt metrics, LookML, Cube)** | One definition of every metric, versioned, tested, and consumed by every surface | **A governed semantic layer owned by M25 as the single source of metric truth**, so that "first-time fix rate" means the same thing on the executive dashboard, in a branch league table, in a technician scorecard and in a brand partner report | Buying a commercial semantic-layer product |
| **Executive dashboard practice** | Drill from group to transaction; trend and forecast alongside actual; mobile access for managers away from a desk | **Drill from group to a single job** — `04-00` requires it explicitly, and it is what makes an executive dashboard trusted rather than doubted | Dashboards that cannot be interrogated. A number a director cannot decompose is a number they will ask an analyst to check, which recreates the compilation cost |

**Design position.** Five deliberate differences from the benchmark.

First, **two tools, one boundary, no overlap.** Metabase serves governed business analytics;
Grafana serves the real-time operations board. The boundary is not negotiable, because the
common failure is a real-time tool accumulating business metrics defined in dashboard queries.
Every metric on a Metabase surface comes from M25's semantic layer; Grafana never defines a
business metric.

Second, **no metric is defined in a dashboard.** If a number is worth showing to management, it
is worth defining once, in M25, with an owner, a formula and a test. A dashboard containing its
own calculation is a defect, and P06's review process rejects it.

Third, **every view states its freshness and its definition.** A manager looking at a figure can
see when the data was last refreshed and what the metric means, without asking. This is the
cheapest possible defence against the most expensive analytics failure — a decision taken on a
number that meant something else.

Fourth, **row-level security is a design constraint, not a configuration afterthought.** A
branch manager and a CEO use the same dashboards. The branch manager sees their branch. This
must be enforced in the analytics layer, derived from M29, and it must be tested as a security
control — because a branch league table that leaks another branch's detail to the wrong manager
is both a data breach and a workforce-relations incident.

Fifth, **the audience is managers, not analysts.** Self-service means a branch manager building
a comparison without SQL, within the datasets and the security they are permitted. It does not
mean giving 60 people warehouse access. The measure of success is `04-00`'s 90% reduction in
manual reporting effort, which is achieved by managers answering their own questions — not by
an analytics team answering them faster.

---

## 5. Capability Areas & Functions

### 5.1 Executive & Branch Analytics

| FR ID | Feature | Function — "The portal shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-171 | Executive dashboard | Present group performance across all revenue streams — revenue, margin, volume, cash, CSAT, utilisation — with trend and forecast, configurable per executive (BR-BI-001) | **P0** | L4 |
| FR-POR-172 | Revenue stream decomposition | Decompose group performance to each revenue stream — service, contracts, warranty, rental, refurbishment, marketplace, managed services, data services, parts retail, e-waste — with its own unit economics | **P0** | L4 |
| FR-POR-173 | **Drill to a single job** | Drill from any aggregate figure through stream, branch, period and category to the individual transactions behind it, and hand off to P03 for the record itself | **P0** | L4/L5 |
| FR-POR-174 | Branch league table | Rank and compare all 51+ branches on every operational and financial dimension, with configurable ranking and peer grouping by branch type and size (BR-BI-002) | **P0** | L4 |
| FR-POR-175 | Branch scorecard | Present each branch manager their own branch's full scorecard with peer comparison, without exposing another branch's detail beyond the ranked measure | **P0** | L4 |
| FR-POR-176 | Trend and forecast | Present trend against prior periods and the M26 forecast where one exists, with the forecast visually distinguished from actuals and its confidence stated | P1 | L4 |

### 5.2 Functional Dashboards

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-177 | Service and field analytics | Present TAT, first-time fix, rework, SLA attainment, common faults, technician productivity and utilisation (BR-BI-003, BR-BI-004) | **P0** | L4 |
| FR-POR-178 | Inventory and supply analytics | Present turnover, dead stock, stockout frequency, inter-branch movement, van variance, supplier performance and landed cost (BR-BI-005) | **P0** | L4 |
| FR-POR-179 | Financial analytics | Present revenue and margin by service type, brand, branch and stream; cash position; receivable ageing; cost to serve (BR-BI-006) | **P0** | L4 |
| FR-POR-180 | Warranty and contract analytics | Present claims by brand, approval rate, ageing, revenue realisation, leakage, contract profitability, entitlement consumption and renewal pipeline (BR-BI-010) | **P0** | L4 |
| FR-POR-181 | People and quality analytics | Present headcount, attendance, skills coverage, certification currency, incentive distribution, NCRs, CAPAs, complaints and audit findings | P1 | L4 |
| FR-POR-182 | Asset and facility analytics | Present device registry completeness, equipment calibration compliance, fleet cost per kilometre, facility cost per site and infrastructure availability | P2 | L4 |
| FR-POR-183 | New-business analytics | Present marketplace, rental, refurbishment, managed services and e-waste performance with their own unit economics | P2 | L4 |

### 5.3 Real-Time Operations

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-184 | Live operations board | Present open jobs by state, technicians on a live map, SLA countdowns, branch queue health and platform health, refreshing continuously | **P0** | L4 |
| FR-POR-185 | Real-time boundary | Serve the real-time board from Grafana over operational and time-series sources, and **define no business metric within it** | **P0** | L4 |
| FR-POR-186 | Wallboard mode | Present a branch or operations wallboard suitable for a display screen, without interaction | P2 | L4 |

### 5.4 Self-Service, Distribution & Alerting

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-187 | Governed self-service | Allow a manager to build an analysis on certified datasets using a visual query builder, without SQL, within their row-level security scope (BR-BI-007) | **P0** | L4 |
| FR-POR-188 | Certified datasets only | Expose only datasets certified by M62, each with an owner, a definition and a freshness guarantee; raw table access is not offered to any P06 user | **P0** | L4 |
| FR-POR-189 | Metric transparency | Show, for every metric on every view, its definition, its owner and its source, on demand and without leaving the view | **P0** | L4/L5 |
| FR-POR-190 | Freshness indication | State on every view when its underlying data was last refreshed, and flag a view whose data is stale beyond its guarantee | **P0** | L4/L5 |
| FR-POR-191 | Scheduled distribution | Schedule and subscribe to reports delivered by email at a defined cadence, respecting each recipient's row-level security (BR-BI-008) | P1 | L4 |
| FR-POR-192 | Export | Export any permitted view to PDF, Excel and CSV within the user's data scope, with the export logged (BR-BI-009) | P1 | L4 |
| FR-POR-193 | Threshold and anomaly alerting | Define thresholds and anomaly conditions on a metric, and deliver an alert to the accountable role through M27 when crossed | P1 | L4/L5 |
| FR-POR-194 | Mobile and embedded | Present key dashboards optimised for a phone, and embed analytical panels inside P03 consoles and P04 client views with security carried through | P1 | L4/L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No metric defined in a dashboard** | Every business metric comes from M25's semantic layer. A dashboard containing its own calculation is rejected at review. This is the portal's central architectural control |
| T-02 | **No raw table access** | P06 exposes only M62-certified datasets. No user, at any privilege level, queries a source table directly through P06 |
| T-03 | **Row-level security** | Every dataset carries a security policy derived from M29 — branch, entity, zone, own-records — applied at query time and tested as a security control, not a configuration |
| T-04 | **Column-level security** | Restricted fields per `05-04` §5 — `salary`, `margin`, `nid_number`, `bank_account`, `commission_rate`, `model_confidence` — are excluded from datasets by role, not merely hidden in a view |
| T-05 | **Two-tool boundary** | Metabase serves governed business analytics; Grafana serves the real-time operations board. Grafana defines no business metric; Metabase serves no sub-minute refresh |
| T-06 | **Executive dashboard performance** | Executive dashboard loads in ≤ 5 seconds (`04-00` KPI); standard reports generate within 30 seconds (NFR-005) |
| T-07 | **Real-time refresh** | The operations board refreshes within 10 seconds of a state change, sourced from operational stores and TimescaleDB rather than the warehouse |
| T-08 | **Drill-through contract** | Every aggregate exposes a drill path to its constituent records, terminating in a P03 deep link with the user's permissions re-evaluated at the destination |
| T-09 | **Freshness contract** | Every certified dataset publishes a freshness guarantee; a view whose data exceeds it is flagged in the interface, not silently stale |
| T-10 | **Single sign-on** | Authentication through M29; P06 maintains no separate credential store (**PS-01**) |
| T-11 | **Query governance** | Long-running or high-cost queries are bounded, queued and attributed; no self-service query can degrade the operational estate |
| T-12 | **Warehouse isolation** | Analytical queries run against M62's warehouse, never against transactional databases, except for the explicitly scoped real-time board |
| T-13 | **Export governance** | Every export is logged with user, view, row count and timestamp; bulk export beyond a threshold requires justification |
| T-14 | **Distribution security** | A scheduled report is rendered per recipient under that recipient's row-level security, never rendered once and sent to many |
| T-15 | **Mobile presentation** | Key dashboards are legible and interactive on a phone, for managers away from a desk (**PS-05**) |
| T-16 | **Embedding security** | Panels embedded in P03 and P04 carry the host session's identity and security scope; an embed never widens access |
| T-17 | **Bengali and English** | Dashboard labels, metric names and definitions available in both (**PS-03**) |
| T-18 | **Accessibility** | WCAG 2.1 AA on dashboard surfaces, including colour-independent encoding of status (**PS-04**) |
| T-19 | **Instrumentation** | Dashboard usage, drill depth, self-service authoring and export volume instrumented to M25 (**PS-10**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With P06 |
|---|---|---|
| **CEO** | Reads a monthly deck compiled from spreadsheets | Opens the group view, decomposes to a stream, drills to a branch, asks a better question |
| **CFO** | Waits for the close to see margin | Sees margin by stream and branch continuously; the close confirms rather than reveals |
| **CCO** | Cannot compare the economics of fourteen revenue streams | Sees each stream's contribution, growth and unit economics side by side |
| **Operations Director** | Learns of an SLA problem from a complaint | Sees the live operations board and the SLA countdown before the breach |
| **Branch manager** | Compiles their own weekly numbers | Opens their scorecard with peer ranking; spends the time on the exceptions |
| **Functional manager** | Requests a report and waits days | Builds the analysis themselves on certified data |
| **Quality manager** | Analyses failure patterns anecdotally | Queries the installed base and produces a brand-facing report |
| **Analyst / MIS staff** | Compiles reports full time | Builds and certifies datasets; stops being a report-generation service |
| **Brand partner (via P08)** | Receives a manually prepared performance summary | Receives scoped analytics generated from the same certified datasets |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Manual reporting effort eliminated** | Compilation replaced by governed self-service and scheduled distribution | `04-00` target: **−90% manual management reporting effort**. Across branch managers, functional managers and MIS staff this is a substantial recurring labour recovery |
| **Decision quality and speed** | Live data at the point of decision rather than compiled data weeks later | `04-00` target: **100% of management reviews on live data**. Unquantifiable directly, and the reason the programme exists |
| **Branch performance improvement** | Comparability across 51+ branches makes underperformance visible and improvement attributable | Supports every operational KPI; a network that cannot compare its units cannot manage them |
| **Revenue stream management** | Fourteen streams with visible unit economics, so capital and attention go to what earns | Enables the management of the **BDT 876 lac** upside case in Scope Charter §6.2 rather than merely hoping for it |
| **Working capital and inventory** | Turnover, dead stock and stockout visibility drives the inventory position | Supports the **BDT 34 lac/year** inventory benefit attributed to M15 + M26 |
| **Warranty realisation** | Claim ageing, approval rate and leakage visible by brand | Supports the **BDT 100 lac/year** warranty recovery attributed to M09 |
| **Financial close** | Continuous visibility means the close confirms rather than discovers | Supports the **BDT 26 lac/year** close and cash-flow benefit, and KPI-050 |
| **Technician productivity management** | Productivity, first-time fix and rework visible per technician and branch | Supports the **BDT 130 lac/year** productivity benefit attributed to M02 + M26 |
| **Analyst capacity** | MIS staff move from compiling reports to building certified datasets | Converts a cost centre into a capability |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **One definition of every metric** | The single largest institutional benefit. When "first-time fix rate" means one thing across the executive dashboard, a branch scorecard, a technician's app and a brand partner report, arguments about numbers end and arguments about performance begin |
| **Numbers that can be interrogated** | A figure a director can decompose to a job is a figure they act on. A figure they cannot is one they ask an analyst to verify — which recreates the cost the portal exists to remove |
| **Evidence-based management culture** | Comparability and transparency change how branch performance conversations happen |
| **Data protection in analytics** | Row-level and column-level security tested as a security control means the analytics estate does not become the weak point in an otherwise well-governed system |
| **Board and investor readiness** | Group performance across fourteen streams, decomposable and reconciled to the ledger, is what external scrutiny requires |
| **Zero licence cost** | Metabase and Grafana are open source; the analytics capability adds no software licence cost, consistent with the programme's $0 core position |
| **Expansion readiness** | Entity and country dimensions on every dataset mean a second country appears as a filter, not a second analytics estate |

---

## 8. Journeys & State Models

### 8.1 The Metric Contract — how a number reaches a screen

```
   SOURCE MODULE (one of 67)
        │ transactional truth
   ┌────▼────────────────────────────────────┐
   │  M62 DATA PLATFORM                       │
   │  ETL · modelling · data quality tests    │
   │  ▸ dataset CERTIFIED with owner,         │
   │    definition and freshness guarantee    │
   └────┬────────────────────────────────────┘
        │
   ┌────▼────────────────────────────────────┐
   │  M25 SEMANTIC LAYER                      │
   │  ▸ metric defined ONCE, with owner,      │
   │    formula, grain and test               │
   │  ▸ consumed by every surface             │
   └────┬────────────────────────────────────┘
        │
   ┌────▼────────────────────────────────────┐
   │  P06 PRESENTATION                        │
   │  ▸ row-level security applied (M29)      │
   │  ▸ freshness stated                      │
   │  ▸ definition available on the view      │
   │  ▸ drill path to constituent records     │
   └────┬────────────────────────────────────┘
        │
   ┌────▼──────────┬──────────────┬──────────────────┐
   │ Executive     │ Branch       │ Embedded in P03 · │
   │ dashboard     │ scorecard    │ P04 · P07 · P08   │
   └───────────────┴──────────────┴───────────────────┘

   ✖ FORBIDDEN: a metric calculated in a dashboard query
   ✖ FORBIDDEN: a P06 user querying a raw source table
```

| Stage | Owner | What is guaranteed |
|---|---|---|
| Source | Module | Transactional correctness |
| Certified dataset | **M62** | Modelled, tested, owned, freshness-guaranteed |
| Metric definition | **M25** | One definition, one owner, versioned and tested |
| Presentation | **P06** | Correct security scope, stated freshness, available definition, working drill path |

### 8.2 Drill-Through — group to job

```
   GROUP REVENUE (executive dashboard)
        │ drill
   ┌────▼──────────────────┐
   │  BY REVENUE STREAM    │   service · contracts · warranty · rental ·
   └────┬──────────────────┘   refurb · marketplace · MSP · data · retail · e-waste
        │ drill
   ┌────▼──────────────────┐
   │  BY BRANCH            │   ranked, peer-grouped, RLS-scoped
   └────┬──────────────────┘
        │ drill
   ┌────▼──────────────────┐
   │  BY PERIOD / CATEGORY │
   └────┬──────────────────┘
        │ drill
   ┌────▼──────────────────┐
   │  TRANSACTION LIST     │   the constituent records
   └────┬──────────────────┘
        │ hand off (deep link, permissions re-evaluated)
   ┌────▼──────────────────┐
   │  P03 — THE RECORD     │   the job, the invoice, the claim
   └───────────────────────┘
```

> **The rule.** Every aggregate must be decomposable to its constituent records, and the final
> hop hands off to P03 where the user's permissions are re-evaluated at the destination. A
> dashboard figure that terminates in itself is not trusted, and a drill path that widens access
> is a security defect.

---

## 9. Portal Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P06-01 | **No business metric is defined in a dashboard**; every metric comes from M25's semantic layer | **H** | CTO |
| PRU-P06-02 | **No P06 user queries a raw source table**; only M62-certified datasets are exposed | **H** | CTO |
| PRU-P06-03 | Row-level security derived from M29 is applied to every dataset and tested as a security control | **H** | CTO |
| PRU-P06-04 | Column-level restrictions per `05-04` §5 are enforced by exclusion from the dataset, not by hiding in a view | **H** | CFO |
| PRU-P06-05 | Grafana defines no business metric; Metabase serves no sub-minute refresh | **H** | CTO |
| PRU-P06-06 | Every view states its data freshness, and a view stale beyond its guarantee is flagged | **H** | CTO |
| PRU-P06-07 | Every metric's definition, owner and source are available on the view without leaving it | **C** | CTO |
| PRU-P06-08 | Every aggregate is decomposable to its constituent records | **C** | CTO |
| PRU-P06-09 | A drill-through never widens access; permissions are re-evaluated at the destination | **H** | CTO |
| PRU-P06-10 | A scheduled report is rendered per recipient under that recipient's security scope | **H** | CTO |
| PRU-P06-11 | Every export is logged with user, view, row count and timestamp | **H** | CFO |
| PRU-P06-12 | Analytical queries run against the warehouse, never against transactional databases, except the scoped real-time board | **H** | CTO |
| PRU-P06-13 | A self-service query cannot degrade the operational estate; queries are bounded, queued and attributed | **H** | CTO |
| PRU-P06-14 | **No external party has P06 access**; external analytics are served by P04, P07 and P08 | **H** | CTO |
| PRU-P06-15 | A branch manager sees their own branch's detail and only the ranked measure for peers | **H** | Operations Director |
| PRU-P06-16 | An embedded panel carries the host session's identity and scope, and never widens access | **H** | CTO |
| PRU-P06-17 | Status and performance are encoded independently of colour alone (**PS-04**) | **C** | CTO |

---

## 10. Data, Caching & State Model

### 10.1 What P06 Holds

| Object | Purpose | Ownership |
|---|---|---|
| Dashboard and view definitions | Composition, layout, drill paths | **P06** |
| Row-level security policies | The mapping from M29 scope to dataset filter | **P06**, derived from M29 |
| Self-service saved questions and collections | User-built analyses | **P06** |
| Subscription and schedule definitions | Who receives what, when | **P06** |
| Alert threshold definitions | Metric, condition, recipient role | **P06** |
| Query result cache | Performance | **P06**, bounded and invalidated on refresh |

### 10.2 What P06 Never Holds

| Item | Reason |
|---|---|
| A business metric definition | PRU-P06-01; M25 owns it |
| A transformed or derived dataset | PRU-P06-02; M62 owns it |
| Authoritative business data of any kind | It is a presentation surface |
| A permission definition | M29 owns it; P06 applies it |
| Any external party's access | PRU-P06-14 |

### 10.3 Referenced Datasets

| Dataset domain | Certified By | Sourced From |
|---|---|---|
| Service and field performance | M62 | M01, M02, M31, M03 |
| Customer and experience | M62 | M33, M07, M34, M10 |
| Inventory and supply chain | M62 | M15, M16, M41, M42, M43, M44 |
| Financial and revenue | M62 | M19, M20, M50, M51, M52, M53, M54 |
| Contract, warranty and entitlement | M62 | M08, M09, M39 |
| People and quality | M62 | M21, M22, M23, M55, M56, M57, M59 |
| Assets, fleet and facilities | M62 | M17, M45, M46, M47 |
| New business streams | M62 | M05, M12, M13, M14, M18, M38 |
| Telemetry and prediction | M62 / **M48** | M48, M26 |
| Real-time operational state | Direct (bounded) | M01, M02, M15, M28, M30 |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P06-01 | A metric crosses a defined threshold | Deliver an alert to the accountable role through M27, with the value, the threshold and a link to the view | Alert retried; never silently dropped |
| AUT-P06-02 | An anomaly is detected against a metric's expected range | Alert the accountable role with the observed and expected values | Alert only |
| AUT-P06-03 | A subscription schedule falls due | Render the report **per recipient under their own security scope** and deliver through M27 | Retry; notify the subscription owner on repeated failure |
| AUT-P06-04 | A certified dataset's freshness exceeds its guarantee | Flag every view depending on it, and alert M62 and the dataset owner | Flag; never present stale data as current |
| AUT-P06-05 | A dataset fails its M62 quality tests | Mark dependent views as unreliable with an explanation, and alert the dataset owner | Mark; do not silently serve |
| AUT-P06-06 | A self-service query exceeds its cost or duration bound | Terminate, inform the user, and suggest a narrower scope | Terminate rather than degrade the estate |
| AUT-P06-07 | An export exceeds the configured row threshold | Require justification, log it, and notify the data owner | Block pending justification |
| AUT-P06-08 | A dashboard is submitted for publication containing an inline calculation | Reject at review with the metric that must be defined in M25 first | Publication blocked |
| AUT-P06-09 | A user's role or scope changes in M29 | Re-evaluate their row-level security on next query; no cached result crosses a scope change | Fail closed |
| AUT-P06-10 | An SLA countdown on the real-time board reaches its threshold | Surface it on the operations board and notify the accountable role | Board display only |

---

## 12. Module Interfaces

### 12.1 Modules P06 Consumes

| Module | What | Mechanism |
|---|---|---|
| **M25 Business Intelligence** | **The semantic layer — every metric definition, owner, formula and grain** | Semantic layer |
| **M62 Data Platform** | Certified datasets, freshness guarantees, quality test results, warehouse | Warehouse query |
| M29 Identity & Security | Authentication, user scope for row-level security derivation | OIDC + scope API |
| M28 Integration Platform | Gateway for embedded panels and API-served views | Gateway |
| M26 AI/ML Services | Forecasts and predictions for presentation | REST |
| M48 IoT & Predictive | Time-series data for the real-time board and asset analytics | TimescaleDB |
| M27 Communications | Alert and subscription delivery | REST |
| M64 MDM | Reference data and hierarchy definitions behind every dimension | Warehouse |
| M30 Platform Admin | Platform health for the operations board | Metrics endpoint |
| Operational modules (bounded) | Real-time state for the operations board only | Read replica |

### 12.2 What P06 Provides

| Consumer | What | Mechanism |
|---|---|---|
| Executives and directors | Group, stream, branch and functional analytics | Web |
| Branch and functional managers | Scorecards, league tables and self-service | Web |
| **P03 Admin Operations Portal** | Embedded analytical panels inside consoles | Embed |
| **P04 Corporate B2B Portal** | Scoped client estate analytics | Embed, client-scoped |
| **P07 Marketplace Seller Portal** | Seller performance analytics | Embed, seller-scoped |
| **P08 Brand Partner Portal** | Brand-scoped service performance and reliability analytics | Embed, brand-scoped |
| M27 Communications | Alert and scheduled report payloads | REST |
| M25 / M62 | Usage telemetry: which views, which drills, which self-service queries | Event stream |

### 12.3 Events P06 Consumes

| Event | Source | Effect in P06 |
|---|---|---|
| `dataset.refreshed` | M62 | Update freshness stamp; invalidate cache |
| `dataset.quality_failed` | M62 | Mark dependent views unreliable |
| `metric.definition_changed` | M25 | Version the metric; annotate affected views |
| `model.published` | M26 | Make the forecast available for presentation |
| `user.scope_changed` | M29 | Re-evaluate row-level security |
| `sla.at_risk` | M01 / M08 | Surface on the real-time operations board |
| `telemetry.pipeline_degraded` | M48 | Flag asset analytics freshness |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P06-01 | Email (via M27) | Outbound | Scheduled report distribution and alerting |
| INT-P06-02 | Display screens at branches and operations | Outbound | Wallboard mode |
| INT-P06-03 | Executive mobile devices | Outbound | Mobile dashboard access and push alerting |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/analytics/embed/{view}` | GET | Signed, scoped embed token for a panel | P03, P04, P07, P08 |
| `/api/v1/analytics/metrics/{id}/definition` | GET | Metric definition, owner and source | Any surface |
| `/api/v1/analytics/datasets` | GET | Certified datasets available to this user | Self-service |
| `/api/v1/analytics/subscriptions` | GET/POST | Manage report subscriptions | Managers |
| `/api/v1/analytics/alerts` | GET/POST | Manage metric thresholds | Managers |

---

## 13. Roles & Permissions

**17 roles hold P06 access** per `05-04` §2 — all management, no operational or external role.

| Role group | Roles | Scope |
|---|---|---|
| Executive | R01 Chief Executive Officer, R02 Chief Technology Officer, R03 Chief Financial Officer, R04 Chief Commercial Officer, R05 Operations Director | All entities, all branches, all streams |
| Branch and operations | R06 Branch Manager, R07 Dispatch Manager | **Own branch / assigned zones**, with peer ranking visible but peer detail not |
| Supply chain | R17 Inventory Manager | All locations |
| Commercial | R21 Sales Manager, R22 Account Manager (Corporate), R23 Marketing Manager, R24 Marketplace Operations Officer | Assigned segment, accounts or domain |
| Finance and governance | R26 Finance Manager, R28 Warranty Claims Officer, R32 Quality Manager / ISO Coordinator | All entities (finance), all claims, all branches (quality) |
| People | R30 HR Manager | All employees |
| Contact centre | R35 Contact Centre Supervisor | Own team and queues |

> **No external party has P06 access under any circumstance** (PRU-P06-14). Brand partners,
> corporate clients and marketplace sellers receive scoped analytics through P08, P04 and P07
> respectively, generated from the same certified datasets under their own security scope.

**Field-level restrictions.** Restricted fields are **excluded from the dataset by role**, not
hidden in a view: `salary`, `allowances` and `deductions` to R03, R26, R30 and R31;
`unit_cost`, `total_cost` and `margin` to R01–R05, R06, R17, R21, R22, R26 and R27;
`commission_rate` to R03, R04, R24 and R26; `nid_number` and `bank_account` to the named finance
and HR roles; `model_confidence` and `model_features` to R02, R33 and model owners;
`technician_incentive_detail` to R30, R31, the technician and their branch manager in summary
only.

**Row-level security.** A branch manager sees their own branch's full detail and peers' ranked
measures without peer detail. A dispatch manager sees their assigned zones. An account manager
sees their assigned accounts. This is enforced in the dataset, tested as a security control, and
re-evaluated on every scope change.

---

## 14. Analytics & Instrumentation

*(P06 instruments itself; this is the meta-layer.)*

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Weekly usage by managers** | Which of the 25–60 users open P06 weekly — the `04-00` KPI | M25, CTO |
| Dashboard usage | Views opened, time spent, dashboards never opened | M25 |
| **Drill depth** | How far users decompose an aggregate — a direct measure of whether numbers are trusted | M25 |
| Self-service authoring | Questions built, by whom, and whether they are reused or abandoned | M25 |
| Report request volume | Ad-hoc report requests to MIS before and after — the `04-00` −90% effort measure | M25, CTO |
| Performance | Dashboard load time, query duration, cache hit rate | M30 |
| Freshness breaches | Views served while flagged stale, and for how long | M62 |
| Export volume | Exports by user, view and row count | CFO |
| Alert effectiveness | Alerts raised, acknowledged, actioned, ignored — alerts routinely ignored are removed | M25 |
| Security | Row-level security evaluations, denials, scope changes applied | M29 |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| — | **Executive dashboard load** | n/a | < 7 s | **< 5 s** |
| — | **Weekly usage by managers** | 0% | 75% | **> 90%** |
| — | **Decisions made on live data rather than compiled spreadsheets** | ~0% | 80% | **100% of management reviews** |
| — | **Manual management reporting effort** | baseline | −60% | **−90%** |
| — | Standard report generation time | unmeasured | < 30 s | **< 20 s** |
| — | Real-time operations board refresh lag | n/a | < 15 s | **< 10 s** |
| — | Metrics defined in the semantic layer rather than in a dashboard | 0% | **100%** | **100%** |
| — | Views stating freshness and definition | 0% | **100%** | **100%** |
| — | Aggregates with a working drill path to records | 0% | 90% | **100%** |
| — | Self-service analyses built by managers per month | 0 | 40 | **> 100** |
| — | Ad-hoc report requests to MIS | baseline | −65% | **−90%** |
| — | Row-level security defects found in testing | n/a | **0 in production** | **0 in production** |
| — | External party access to P06 | n/a | **0** | **0** |
| **KPI-050** *(supported)* | Financial close duration | unmeasured | ≤ 5 days | **≤ 3 days** |

> **Register note.** The first four metrics are adopted verbatim from `04-00` §P06. P06 has
> **no KPI-0nn identifiers allocated**; all thirteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L4 | **Metabase** — governed business analytics, visual query builder, dashboards, subscriptions, embedding | 46% |
| L4 | **Grafana** — real-time operations board over operational and TimescaleDB sources | 18% |
| L5 | **Dashboard composition, row-level security mapping, metric-transparency and freshness surfaces, drill-through contract, embed tokens** (`CD-206`) | 30% |
| L2 | OCA `reporting-engine` and `mis-builder` for statutory and finance-formatted outputs | 6% |

> **Licence position.** Both tools are open source and add **no software licence cost**,
> consistent with the programme's $0 core position (`02-05` §1). **However** — Metabase's
> row-level security (data sandboxing), SAML SSO and audit logs are Enterprise-tier features,
> while Apache Superset provides row-level security, RBAC and SAML in its open-source edition.
> Since row-level security is a **hard requirement** (PRU-P06-03), this is a genuine decision,
> not a detail. It is raised as Q-02 and must be resolved before build.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-206** | `p06_analytics_surface` — dashboard composition and the fourteen functional dashboards, executive and branch league surfaces, row-level security mapping from M29 to dataset policies, metric-transparency and freshness surfaces, drill-through contract with P03 hand-off, subscription and alert definition, signed embed tokens for P03/P04/P07/P08, mobile and wallboard presentation | Configuration + Next.js/OWL surfaces | 16 PW |

> **CD register.** One ID, **CD-206**, claimed following CD-205 (P05). All CD IDs remain
> provisional pending the unified CD register required by audit finding M-01 in `02-05`.
>
> **Effort note.** 16 PW covers the P06 surface. The **datasets and metric definitions are
> M25's and M62's effort**, not P06's, and they are the larger share of the total analytics
> cost. A plan that budgets 16 PW and expects certified datasets for 67 modules is wrong by a
> wide margin.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M62 Data Platform** | Certified datasets are the portal's entire substrate. **W4** — this is the binding constraint |
| **M25 Business Intelligence** | The semantic layer; no metric can be presented before it is defined. **W4** |
| M29 Identity & Security | Row-level security derives from M29 scope |
| M28 Integration Platform | Embed tokens and gateway |
| M64 MDM | Dimension hierarchies behind every breakdown |
| M27 Communications | Alert and subscription delivery |
| M26 AI/ML | Forecast presentation (W6–W8) — dashboards ship without forecasts and add them |
| M48 IoT | Asset and telemetry analytics (W8) — added when M48 lands |
| The source modules | A dashboard cannot precede the module whose data it presents |

**Wave progression.** P06 grows with the estate:

| Wave | Dashboards delivered |
|---|---|
| **W4** | Executive · Branch league · Service & field · Financial · Real-time operations |
| **W5** | Inventory & supply · Warranty & contract · People & quality |
| **W6** | Forecast presentation (M26) · New-business streams |
| **W7** | Marketplace analytics |
| **W8** | Asset, fleet and facility analytics · Telemetry and prediction (M48) |

### 16.4 Adoption

| Activity | Scope | Wave |
|---|---|---|
| Executive onboarding | Individual, per executive, on their own numbers | W4 |
| Branch manager enablement | Scorecard walkthrough with peer comparison | W4–W5 |
| Self-service training | Visual query builder, certified datasets, security scope | W5 |
| Report retirement | Each legacy manual report is retired against a P06 replacement, with a named date | W4–W8 |

> **Adoption position.** The −90% manual reporting target is achieved by **retiring legacy
> reports on a named date against a named replacement**, not by hoping managers stop compiling
> them. Each existing manual report is inventoried, matched to a P06 view, and retired
> explicitly. A dashboard that exists alongside the spreadsheet it was meant to replace has
> delivered nothing and cost 16 person-weeks.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every business metric presented in P06 is defined in M25's semantic layer; no dashboard contains an inline calculation | Full audit of every published dashboard |
| AC-02 | No P06 user can query a raw source table at any privilege level | Negative test including administrator accounts |
| AC-03 | Row-level security is correctly applied for every role and scope combination, tested as a security control | **Security test matrix covering all 17 roles × scope types — the highest-severity test for this portal** |
| AC-04 | A branch manager sees their own branch's detail and only ranked measures for peers | Negative test with two branch manager accounts |
| AC-05 | Restricted fields are absent from the dataset for unauthorised roles, not merely hidden in the view | Dataset inspection per role for every field in `05-04` §5 |
| AC-06 | A scope change in M29 is reflected in the user's next query, with no cached result crossing the change | Scripted scope-change test |
| AC-07 | The executive dashboard loads in under 5 seconds at production data volume | Performance test |
| AC-08 | Standard reports generate within 30 seconds (NFR-005) | Performance test across all functional dashboards |
| AC-09 | The real-time operations board reflects a state change within 10 seconds | Latency test |
| AC-10 | Every aggregate decomposes to its constituent records and hands off to P03 with permissions re-evaluated | Drill-path audit across every dashboard |
| AC-11 | A drill-through cannot widen a user's access | Negative test at the destination |
| AC-12 | Every view states its data freshness and flags data stale beyond its guarantee | Scripted staleness test |
| AC-13 | Every metric's definition, owner and source are available on the view | Metric-transparency audit |
| AC-14 | A scheduled report is rendered per recipient under that recipient's security scope | Test with three recipients of differing scope on one subscription |
| AC-15 | A self-service query exceeding its bound is terminated without degrading the operational estate | Load test with a deliberately expensive query |
| AC-16 | Every export is logged with user, view, row count and timestamp | Export register review |
| AC-17 | Grafana contains no business metric definition and Metabase serves no sub-minute refresh | Configuration audit |
| AC-18 | No external party can reach P06 through any path | Access test from P04, P07 and P08 sessions |
| AC-19 | Embedded panels in P03, P04, P07 and P08 carry the host session's scope and never widen access | Embed security test per host |
| AC-20 | Group revenue in P06 reconciles to the general ledger for one full quarter | Finance-signed reconciliation |
| AC-21 | Every legacy manual management report has a named P06 replacement and a retirement date | Report inventory with retirement schedule |
| AC-22 | Weekly manager usage exceeds 90% and management reviews run on live data | Six consecutive monthly usage reports plus review observation |
| AC-23 | CTO, CFO and Operations Director sign off UAT | Signed UAT record |

**Definition of done:** the twelve cross-portal standards in `04-00` §3 plus the 23 criteria
above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Which legacy manual management reports exist today, who compiles them, and how long does each take? Without this inventory the −90% target cannot be measured or achieved | CTO / Operations Director | **W4 minus 4 months** |
| Q-02 | **Metabase Enterprise (for row-level security, SAML SSO and audit logs) or Apache Superset (which has all three in open source)?** Row-level security is a hard requirement, so this is a build-blocking decision with a licence-cost consequence | CTO / CFO | **W4 minus 3 months** |
| Q-03 | Who owns each metric definition in M25 — the module business owner, or a central data function? | CTO / CFO | **W4 design** |
| Q-04 | What freshness guarantee applies per dataset domain — real-time, hourly, daily? This drives M62's ETL cadence and cost | CTO / CFO | W4 design |
| Q-05 | Are branch peers named in a league table, or anonymised beyond the user's own branch? This is a workforce-relations decision with a real effect on adoption | Operations Director / HR Director | **W4 design** |
| Q-06 | Which executives require mobile access, and to which dashboards? | CEO / CTO | W4 design |
| Q-07 | What is the export row threshold above which justification is required? | CFO / CTO | W4 build |
| Q-08 | Do any brand partners or corporate clients contractually require analytics the certified datasets do not yet support? | CCO | W4 design |
| Q-09 | Is a wallboard deployment planned at branches, and who owns the display hardware? | Operations Director / Branch Operations Lead | W5 scoping |
| Q-10 | What happens to the MIS function's role as compilation is eliminated? This is a people question that determines whether the change is supported or resisted | HR Director / CTO | **W4 design** |
| Q-11 | Are dashboard labels and metric definitions required in Bengali, or is management analytics English-only? | CTO / Operations Director | W4 design |
| Q-12 | What is the retention period for query logs and export logs, given they contain business-sensitive query patterns? | CTO / Legal | W4 build |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §P06, §1, §3 PS-01…PS-12, §4 ·
`P03_Admin_Operations_Portal.md` (embedded panels, drill-through destination) ·
`P04_Corporate_B2B_Portal.md` · `P07_Marketplace_Seller_Portal_and_Application.md` ·
`P08_Brand_Partner_Portal.md` ·
`03_Modules/K_Platform_and_Technology/_CATEGORY_OVERVIEW.md` §6 (boundary map), §9 ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §5, §10 (AS-03, AS-14) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §1 ($0 licence position),
§4 (Metabase, Grafana, TimescaleDB, OpenTelemetry) ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §2 (17 roles), §5 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §Wave 4

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.1 Portal 6, BR-BI-001 …
BR-BI-010, NFR-005 ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §6.2 (benefit register)

**External benchmark**
[Metabase row and column security documentation](https://www.metabase.com/docs/latest/permissions/row-and-column-security) ·
[Grafana versus Metabase for customer-facing analytics — semantic layer and governed self-service](https://www.sumboard.io/blog/grafana-vs-metabase) ·
[Open-source BI tools compared 2026 — Superset row-level security in open source versus Metabase Enterprise tiers](https://www.basedash.com/blog/best-open-source-bi-tools-compared-2026) ·
[Open-source BI tools overview](https://www.domo.com/learn/article/open-source-bi-tools) ·
[Self-serve embedded BI and analytics tools 2026](https://embeddable.com/blog/top-self-serve-embedded-bi-analytics-tools) ·
[Metabase alternatives and governance comparison](https://dashboardfox.com/blog/metabase-alternatives/) ·
[WCAG 2.1 AA success criteria](https://www.levelaccess.com/blog/wcag-2-1-exploring-new-success-criteria/)

---

*Portal P06 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
