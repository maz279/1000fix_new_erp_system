---
id: FIX-ERP2-M25
module_id: M25
module_code: BID
module_name: Business Intelligence & Reporting
category: J — Data, Analytics & Intelligence
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Data Squad
priority: P1
wave: W4
---

# M25 — Business Intelligence & Reporting
### Category J · Code `BID` · Existing (re-scoped in v2.1)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M25 |
| **Module code** | `BID` |
| **Category** | J — Data, Analytics & Intelligence |
| **Status** | Existing (retained from v1.0, **re-scoped in v2.1** — the data platform was carved out to M62) |
| **Priority** | **P1** |
| **Delivery wave** | W4 (Months 15–18) |
| **Business owner** | Chief Technology Officer *(content ownership sits with each functional head)* |
| **System owner** | Data Squad |
| **Delivery layers** | L2 (OCA reporting engine) · L4 (Metabase, Grafana) · L5 (custom) |
| **Custom modules** | `cd_embedded_analytics`, `cd_report_distribution`, `cd_alert_engine`, `cd_statutory_report` |
| **Requirement range** | FR-BID-001 … FR-BID-034 |
| **Requirement count** | **34** *(within the `05-01` allocation of 45; register `02-02` estimated 30 — see §16.5)* |
| **Effort estimate** | **18 person-weeks** *(register estimated 16)* |
| **Depends on** | **M62 Data Platform (hard dependency)** · M29 Identity & Security · M27 Contact Centre (delivery channels) · M24 Documents · M63 Process Automation (scheduling) |
| **Depended on by** | Every module as a reporting consumer · all portals P01–P12 · M60 GRC · M23 Quality · executive and branch management |

---

## 2. Purpose

M25 is **where the business looks**. It takes the certified numbers M62 produces and makes them
visible, findable, readable and actionable — as dashboards for a role, as scheduled reports in
an inbox, as an alert when something moves, as a chart embedded inside the screen where someone
is already working, and as a self-service surface for the analyst who has a question nobody
anticipated.

Its job is narrow and it matters enormously: **remove every reason a manager would open a
spreadsheet instead.** A dashboard that is slower than the spreadsheet, harder to find than the
spreadsheet, or missing the one column the spreadsheet had, loses — and when it loses, the
Company goes back to running on numbers nobody can reconcile.

M25 does not decide what a number means. That is M62's semantic layer. M25 decides **who sees
it, where, when, next to what, and what they can do about it.**

### Why It Exists

The programme's benefit register carries two objectives that live or die here: **BO-07 —
give management real-time visibility**, moving branch performance data from *days* to *real
time*; and **BO-17 — make decisions on live data**, taking manual reporting packs from *100% to
zero*.

Neither is a technology problem. The Company already has data. What it lacks is a place where
the same number appears the same way for everyone, fast enough to be used in the meeting it was
prepared for. The Category J risk register names the failure mode precisely: *management reverts
to spreadsheets*, and when that happens the visibility benefit never lands regardless of what
was built.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Category J Overview §3 | M25 owns dashboards, reports, self-service exploration, subscriptions, alerting and embedded analytics. Fails when "numbers are right but nobody can find or read them". Consumers: *every role, every portal* |
| Category J Overview §5 | Boundary map: dashboards, reports, exploration and distribution → M25; **metric definition → M62 (M25 renders it)**; operational real-time boards → the owning module |
| Category J Overview §9 | KPIs owned here: executive dashboard load < 5 s, standard report generation < 20 s, manager weekly usage > 90%, **manual spreadsheet packs zero by W8** |
| Category J Overview §11 | The named risk: *management reverts to spreadsheets*. Mitigation is retiring the source data for manual packs, making dashboards materially better, and requiring decisions to cite the dashboard |
| Scope Charter §Benefit Register | **BO-07** real-time visibility (CEO, days → real time) · **BO-17** decisions on live data (CTO, manual packs → zero) |
| `06-02` §2.7 | **KPI-094** manual management reports remaining → **zero** |
| `02-05` §Technology Stack | Metabase 0.52+ (BI and dashboards, W4) · Grafana 11.x (operational monitoring, W2) · OCA `reporting-engine` and `mis-builder` |
| Written module specifications (40+) | Every one names M25 as its reporting outlet; §14 of each specifies the reports M25 must be able to deliver |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Role-based dashboards for every management and operational role in the Company |
| 2 | Executive, branch, functional and personal dashboard tiers |
| 3 | Standard report library — the canonical, named reports each module's §14 requires |
| 4 | Pixel-controlled operational and statutory report rendering, in Bengali and English |
| 5 | Governed self-service exploration for analysts, against certified metrics only |
| 6 | Scheduled distribution — subscriptions, bursting by scope, and delivery to email, portal and messaging |
| 7 | Threshold, trend and anomaly alerting with routing and acknowledgement |
| 8 | Embedded analytics inside ERP screens and inside the customer, corporate and partner portals |
| 9 | Mobile-readable dashboards for field and branch management |
| 10 | Drill-down, drill-through and cross-filter navigation from summary to transaction |
| 11 | Export and offline distribution with the scoping intact |
| 12 | Data-freshness and certification indicators displayed on every surface |
| 13 | Dashboard and report lifecycle: request, build, certify, publish, review, retire |
| 14 | Usage analytics — who uses what, how often, and which surfaces are dead |
| 15 | The spreadsheet-retirement programme and its tracking |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Metric definition — the formula, grain and meaning of every number** | **M62** semantic layer | Category J overview §3: *"a metric is defined once, in M62's semantic layer. M25 displays it. If two dashboards disagree, the defect is in M62, not in a chart."* A metric editable from a chart is a metric with no single definition |
| **Ingestion, transformation, the warehouse and the dimensional model** | **M62** | Different discipline, different failure mode |
| **Data quality tests, freshness monitoring, lineage and the catalogue** | **M62** | M25 *displays* quality and freshness status; it does not compute or own it |
| **Row-level security enforcement** | **M62** (deriving from **M29**) | Scoping is enforced in the query engine so an extract, an API call and a dashboard return identically permitted rows. A BI tool enforcing its own security creates a second, divergent model |
| **The feature store and anything a model consumes** | **M62** / **M26** | — |
| **Model training, serving, explanation and monitoring** | **M26** | M25 may display a prediction; it never produces one |
| **Operational real-time boards — dispatch map, technician queue, branch queue, counter board** | **M02**, **M04**, **M31** | These are operating surfaces with sub-second expectations and write-back actions. They are part of doing the work, not part of reporting on it |
| **Infrastructure and platform monitoring dashboards** | **M30** / **M28** *(Grafana)* | Grafana serves technical observability; Metabase serves business analytics. The audiences never overlap |
| **Statutory return content, assertions and filing** | **M51**, **M19**, **M18**, **M21** | M25 renders the artefact; the module accountable for filing owns what it says |
| **Document storage, versioning and retention** | **M24** | A generated report filed as a record is retained by M24 |
| **Notification transport — email, SMS, WhatsApp, push** | **M27** | M25 decides what to send and to whom; M27 delivers it |
| **Schedule execution as a business process** | **M63** | M63 runs the scheduler; M25 declares the schedule |
| **KPI target setting and performance management** | Owning function / **M57** | M25 shows performance against target; it does not set targets or drive appraisal |

### 3.3 Shared Concepts

| Concept | M25's Role | Owning Module |
|---|---|---|
| Metric | **Renders — never defines** | M62 |
| Dashboard | **Owns** | M25 |
| Standard report | **Owns the artefact**; content owner is the functional head | M25 |
| Data freshness and quality status | Displays | M62 |
| Row-level scope | Applies M62's enforcement | M62 / M29 |
| Subscription and distribution | **Owns** | M27 delivers |
| Alert | **Owns definition and routing** | M27 delivers; M63 may act on it |
| Embedded chart | **Owns** | Host module owns the screen |
| Prediction displayed on a dashboard | Displays with its explanation | M26 |
| Statutory report layout | **Owns the rendering** | Filing module owns the content |
| Report as a retained record | Produces | M24 retains |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Oracle Transactional Business Intelligence (OTBI)** | Analytics over the operational model with the ERP's own security model applied automatically, plus prebuilt subject areas per business function | **Security inheritance as a non-negotiable**: a user's analytical scope is their ERP scope, computed once, never re-declared in the BI tool | OTBI's real-time query against the transactional system. It protects the operational database at 1000FiX's transaction volume to read from the warehouse instead |
| **SAP Analytics Cloud** | Stories, planning and analytics on one surface, with a live connection to a governed semantic model | **Story-style narrative dashboards** for the executive tier — a dashboard that explains rather than merely displays | The integrated planning layer. Planning belongs to M54 (FP&A) and M43 (demand) |
| **Microsoft Power BI** | Certified and promoted datasets, workspace governance, subscriptions, alerts, mobile layouts, embedded analytics with row-level security | **The certification badge pattern**: certified content visually distinguished from personal exploration, everywhere it appears | The self-service-first culture. Uncontrolled dataset proliferation is precisely the failure mode M62 exists to prevent |
| **Metabase 0.52+** *(selected in `02-05`)* | Question and dashboard authoring, SQL and no-code query building, subscriptions and alerts, signed embedding, sandboxing by attribute, verified items | **The delivery platform.** Verified-item marking, attribute-based sandboxing, signed embedding and subscriptions cover most of §5.1, §5.5 and §5.6 | Metabase as the metric definition store. Metabase questions can each define their own logic — which is exactly the divergence M62 prevents. Metabase queries the semantic layer, not raw tables |
| **Grafana** *(already deployed W2)* | Time-series operational monitoring and alerting | **Kept for technical observability only**, with an explicit boundary so the Company does not end up with two BI tools by accident | Grafana as a business BI surface |
| **OCA `reporting-engine` / `mis-builder`** | Odoo-native report rendering and MIS report builder over the accounting model | **Pixel-controlled statutory and operational document rendering**, where a specific legal layout is required | MIS-builder as the management reporting layer — it reads the operational model, not the certified warehouse |
| **Enterprise "single source of truth" practice** | Certified content, deprecation of shadow reporting, adoption measured rather than assumed | **The spreadsheet-retirement programme as an explicit, tracked deliverable** with a named owner per pack, rather than a hope | — |
| **Report bursting practice** | One report definition rendered per recipient scope and delivered individually | **Bursting by branch, zone, entity and account**, so 51 branch managers receive one report definition scoped 51 ways | — |
| **Data storytelling practice** | Annotation, target lines, variance framing and plain-language summary alongside the chart | **Annotation and plain-language summary on executive surfaces**, in Bengali and English | Automated narrative generation at W4 — deferred to the M26 generative capability in W8 |

**Design position.** Five deliberate differences, all of them consequences of *who actually
uses this* — branch managers on mid-range Android phones over mobile data, not analysts on
desktops.

**First, the dashboard must beat the spreadsheet on the spreadsheet's own terms.** The Category
J risk register names reversion to spreadsheets as a High risk, and mitigation is not
exhortation. It is three concrete things this module commits to: the dashboard is **faster**
(executive load under five seconds), it is **more complete** (it has the column the spreadsheet
had, because the spreadsheet was harvested during M62 migration), and the **source data for the
manual pack is retired** so the old path stops being available. A fourth, cultural measure sits
outside the system: decisions cite the dashboard.

**Second, mobile is the primary design target for operational roles.** A branch manager will not
open a laptop to check yesterday's queue time. Operational and branch dashboards are designed
mobile-first, tested on mid-range Android over a constrained connection, and hold a small number
of large, legible figures rather than a dense desktop grid.

**Third, every surface displays freshness and certification.** A number without a timestamp
invites the question *"is this current?"*, and one unanswered instance of that question sends a
manager back to the spreadsheet permanently. Every dashboard header carries the subject area's
current freshness from M62, and every metric carries its certification status. A degraded
subject area says so, visibly, rather than silently showing stale figures.

**Fourth, self-service is governed, not free.** Analysts explore against certified metrics and
conformed dimensions. They can build any question they like from those components; they cannot
redefine what *gross margin* means, and they cannot publish an uncertified answer to a
management audience. This is deliberately more restrictive than the Power BI norm, because the
whole point of M62 is undone the moment a chart can hold its own arithmetic.

**Fifth, Bengali is a first-class rendering requirement, not a translation afterthought.**
Statutory documents, branch-facing reports and portal-embedded analytics render correctly in
Bengali script including numerals, in generated PDFs, on mobile, and in exports. Bengali
rendering failures in generated PDFs are a well-known and recurring defect class, and they are
treated here as an acceptance criterion rather than a styling preference.

---

## 5. Functional Areas & Features

### 5.1 Dashboards

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BID-001 | Role-based dashboard assignment | Present each user, on login, the dashboard set defined for their role, scoped automatically to their ERP scope with no user configuration | P1 | L5 |
| FR-BID-002 | Executive dashboard tier | Provide CEO, CFO, COO and category-owner dashboards covering the programme's benefit objectives, with target lines and variance framing | P1 | L5 |
| FR-BID-003 | Branch and functional dashboards | Provide branch-manager, workshop, field, warehouse, contact-centre, finance and HR dashboards, each showing that function's own KPIs against target | P1 | L5 |
| FR-BID-004 | Personal performance view | Show an individual — technician, agent, seller — their own measured performance, scoped to themselves | P2 | L5 |
| FR-BID-005 | Mobile-first operational layouts | Render operational and branch dashboards legibly on a mid-range Android device over a constrained connection | P1 | L5 |
| FR-BID-006 | Drill navigation | Drill down through dimensions, drill through to the underlying transaction list, and cross-filter across tiles, preserving the user's scope at every step | P1 | L5 |
| FR-BID-007 | Freshness and certification indicators | Display, on every surface, the subject area's current data freshness and each metric's certification status, and visibly mark a degraded subject area | **P0** | L5 |
| FR-BID-008 | Comparison and target framing | Present every KPI against its target, its prior period and its trend, rather than as a bare number | P1 | L5 |
| FR-BID-009 | Annotation and commentary | Allow a named owner to annotate a figure or period with an explanation visible to that dashboard's audience | P2 | L5 |
| FR-BID-010 | Executive performance | Load an executive dashboard within the published response target on a standard connection | P1 | L5 |

### 5.2 Standard Reports & Statutory Rendering

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BID-011 | Standard report library | Maintain the canonical, named report set required by each module's §14, each with an owner, a definition and a certification status | P1 | L5 |
| FR-BID-012 | Report generation performance | Generate a standard report within the published response target | P1 | L5 |
| FR-BID-013 | Pixel-controlled rendering | Render reports requiring an exact layout — statutory forms, certificates, manifests, invoices, evidence packs — to a controlled specification | P1 | L2 |
| FR-BID-014 | **Bengali and English rendering** | Render all report and dashboard content correctly in Bengali script including numerals, in screen, PDF, print and export, without glyph or ligature failure | **P0** | L5 |
| FR-BID-015 | Report parameterisation | Parameterise reports by period, scope, entity, branch and dimension, with the user's permitted scope enforced | P1 | L5 |
| FR-BID-016 | Report as a record | File a generated report as a retained record in M24 where it constitutes evidence | P2 | L5 |
| FR-BID-017 | Report versioning and reproducibility | Record the metric versions and data as-of time used, so a report can be reproduced identically later, and mark any report affected by a subsequent restatement | P1 | L5 |

### 5.3 Governed Self-Service

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BID-018 | Governed exploration | Let an analyst compose any question from certified metrics and conformed dimensions, without the ability to redefine a metric | P1 | L5 |
| FR-BID-019 | Personal and shared workspaces | Separate personal exploration from published content, so an unfinished answer cannot be mistaken for a certified one | P1 | L5 |
| FR-BID-020 | Publication and certification workflow | Require review and certification before any content reaches a management audience, with the certification visible on the artefact | P1 | L5 |
| FR-BID-021 | SQL access for advanced users | Provide a governed SQL surface against curated subject areas, with row-level security enforced by M62 and every query logged | P2 | L5 |
| FR-BID-022 | Content lifecycle | Manage dashboards and reports through request, build, certify, publish, periodic review and retirement, retiring unused content | P2 | L5 |

### 5.4 Distribution & Alerting

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BID-023 | Subscriptions | Let a user subscribe to a dashboard or report on a schedule, delivered through M27 to their preferred channel | P1 | L5 |
| FR-BID-024 | Bursting by scope | Render one report definition once per recipient scope — branch, zone, entity, account, technician — and deliver each individually | P1 | L5 |
| FR-BID-025 | Threshold and trend alerts | Raise an alert when a metric crosses a threshold, deviates from trend, or fails to arrive, routed to a named role with acknowledgement | P1 | L5 |
| FR-BID-026 | Alert suppression and escalation | Suppress duplicate alerts, escalate unacknowledged alerts, and report alert volume so the system is not tuned into being ignored | P1 | L5 |
| FR-BID-027 | Export with scope intact | Export to spreadsheet, CSV and PDF with the user's scope applied and the export logged | P1 | L5 |
| FR-BID-028 | Offline and low-bandwidth delivery | Deliver a scheduled summary through a low-bandwidth channel where a branch has poor connectivity | P2 | L5 |

### 5.5 Embedded & Portal Analytics

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BID-029 | Embedded analytics in ERP screens | Embed the relevant chart inside the operational screen where the decision is made, scoped to the record in context | P1 | L5 |
| FR-BID-030 | Customer portal analytics | Present a customer their own service history, spend and asset analytics through P01, scoped to themselves | P2 | L5 |
| FR-BID-031 | Corporate portal analytics | Present a corporate client their fleet, contract, disposal and spend analytics through P04, scoped to their organisation | P2 | L5 |
| FR-BID-032 | Partner and seller analytics | Present marketplace sellers, resellers and channel partners their own performance through P05 / P07 | P2 | L5 |

### 5.6 Adoption & Retirement

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BID-033 | Usage analytics | Measure who views what, how often, from which device, and report unused and duplicated content | P1 | L5 |
| FR-BID-034 | **Spreadsheet-retirement register** | Maintain the register of every manual management pack, its owner, its replacement dashboard, its retirement date and its status, and report progress to zero | P1 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No metric arithmetic in the presentation layer** | Every figure resolves through M62's metric API. A dashboard tile cannot contain its own aggregation logic for a certified metric |
| T-02 | **Security inheritance** | The user's analytical scope is resolved from M29 through M62 at query time. M25 holds no independent security model and cannot widen a scope |
| T-03 | **Consistent scoping across surfaces** | A dashboard, an export, a subscription and an embedded chart return identically permitted rows for the same user |
| T-04 | **Freshness propagation** | Subject-area freshness and degraded status from M62 render in the surface header within one refresh cycle |
| T-05 | **Reproducibility stamping** | Every generated report records the metric versions and the data as-of time used, enabling identical regeneration |
| T-06 | **Restatement flagging** | When M62 publishes a restatement, every previously generated report covering the affected period is flagged |
| T-07 | **Bengali text rendering** | Bengali script, conjuncts and numerals render correctly in HTML, generated PDF/A, print and spreadsheet export, verified by an automated rendering test suite |
| T-08 | **Signed embedding** | Embedded analytics use signed, short-lived, scope-bound tokens; an embed URL cannot be replayed by another user |
| T-09 | **Query result caching with correct invalidation** | Results are cached for performance and invalidated on subject-area refresh, never served stale past the declared freshness |
| T-10 | **Bursting isolation** | A burst run renders each recipient's scope independently; a failure for one recipient never leaks another's data or halts the run |
| T-11 | **Export logging** | Every export records user, content, scope, row count and time, retained for audit |
| T-12 | **Performance targets** | Executive dashboard load ≤ 5 s; standard report generation ≤ 20 s; drill-through ≤ 3 s; embedded chart ≤ 2 s; all at p95 |
| T-13 | **Mobile rendering budget** | Operational dashboards render within the target on a mid-range Android device over a 3G-class connection |
| T-14 | **Alert idempotency** | A repeated threshold breach within the suppression window produces one alert, not a stream |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M25 |
|---|---|---|
| **CEO** | Receives a monthly pack assembled over several days, already out of date on arrival | Opens a dashboard; sees the Company as of this morning, against target |
| **CFO** | Reconciles a management pack to the ledger by hand | Certified financial measures, drillable to transaction, with restatements flagged |
| **Branch manager** | Waits for head office to send branch numbers | Sees their own branch on a phone, scoped automatically, every morning |
| **Operations Director** | Compares branches using inconsistent local spreadsheets | Compares 51 branches on one definition of every measure |
| **Workshop / field supervisor** | Judges throughput by feel | Sees cycle time, first-time fix and utilisation against target daily |
| **Business analyst** | Rebuilds the same extract for every question | Explores certified metrics; publishes only after certification |
| **Functional head** | Owns a report nobody trusts | Owns a certified report with a definition anyone can inspect |
| **Contact-centre supervisor** | Reacts when a queue is already bad | Receives an alert on the threshold, with acknowledgement tracked |
| **Corporate client** | Requests a service summary by email | Self-serves their own analytics in the corporate portal |
| **Marketplace seller** | Cannot see how they are performing | Sees their own ranking inputs and performance |
| **CTO** | Cannot say whether reporting is used | Usage analytics per surface, and a tracked retirement register |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Real-time management visibility (BO-07)** | Role-based dashboards on certified data, scoped automatically | Branch performance data **days → real time** |
| **Manual reporting packs eliminated (BO-17 / KPI-094)** | Replacement dashboards plus retirement of the source data behind each pack | Manual management reports **100% → zero by W8** |
| **Administrative labour recovered** | Report assembly, reconciliation and distribution stop being manual work across every function | Material contribution to the **BDT 62 lac/year** cross-module administrative saving |
| **Decision latency** | A decision that waited for month-end can be taken on the day the data moves | The largest behavioural benefit in the programme, and the hardest to price |
| **Benefit realisation made visible** | Every BO objective and canonical KPI has a dashboard showing progress against target | Protects the **BDT 876 lac/year** benefit case by making shortfalls visible early enough to act on |
| **Branch performance convergence** | Comparable, published branch metrics create a management conversation that could not previously happen | Underpins productivity and quality targets across M02, M04, M31 |
| **Alerting instead of inspection** | Thresholds surface exceptions rather than requiring managers to hunt for them | Recovers supervisory time across 51+ branches |
| **Portal analytics as a commercial feature** | Corporate clients and partners self-serve their own performance | Reduces account-management effort; a differentiator in corporate tenders |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Ends parallel truth** | When everyone reads the same number from the same place, meetings are about what to do rather than whose figure is right |
| **Makes performance discussable** | Published, comparable metrics change management from anecdote to evidence — the precondition for every operational improvement in the programme |
| **Transparency downward, not only upward** | A technician seeing their own measured performance is treated as a professional rather than merely measured. This materially affects whether measurement is accepted |
| **Bengali-first accessibility** | Reporting that renders correctly in Bengali is usable by the whole workforce, not only its English-reading managers |
| **Institutional memory of decisions** | Annotated figures record *why* a number moved, which is the context that otherwise leaves with the person |
| **Audit and tender readiness** | Reproducible, certification-stamped reports satisfy ISO, regulator, brand-partner and corporate-client scrutiny without a scramble |
| **Adoption is measured, so failure is visible** | Usage analytics mean a dashboard nobody opens is a known problem rather than a quiet one |

---

## 8. Lifecycle & State Models

### 8.1 Analytical Content Lifecycle

```
   REQUESTED ──► IN BUILD ──► IN REVIEW ──► CERTIFIED ──► PUBLISHED
   (business      (built on     (definition   (owner and    (visible to
    owner names   certified      and scope     content       its audience,
    the decision  metrics only)  verified)     accepted)     badge shown)
    it supports)                                                  │
                                                                  │ periodic review
                                                                  ▼
                                                          ┌───────────────┐
                                                          │  UNDER REVIEW │
                                                          └───┬───────┬───┘
                                            still used ◄──────┘       └──────► unused or
                                                │                              superseded
                                                ▼                                  │
                                            PUBLISHED                              ▼
                                                                            DEPRECATED
                                                                                   │ notice period
                                                                                   ▼
                                                                             RETIRED
```

| From | To | Guard | Actor |
|---|---|---|---|
| Requested | In Build | Named business owner and the decision it supports are stated | Functional head |
| In Build | In Review | Uses only certified M62 metrics; scope behaviour tested | Analyst |
| In Review | Certified | Definition, scope, performance and Bengali rendering all verified | Data Steward |
| Certified | Published | Business owner accepts content and audience | Business owner |
| Published | Under Review | Review cycle due, or usage falls below threshold | System |
| Under Review | Deprecated | Unused, superseded, or owner withdraws | Business owner |
| Deprecated | Retired | Notice period elapsed; no active subscriptions remain | System |

### 8.2 Spreadsheet Retirement — The Programme That Decides Whether M25 Succeeded

```
   REGISTERED ──► REPLACEMENT BUILT ──► PARALLEL RUN ──► REPLACEMENT
   (pack named,     (dashboard or        (both produced,   ACCEPTED
    owner named,     report certified)    figures            │
    metrics                               reconciled)        │
    harvested                                 │              │
    into M62)                                 │ discrepancy  │
        │                                     ▼              │
        │                              INVESTIGATED ─────────┘
        │                              (defect is in M62,
        │                               or the pack was wrong)
        ▼                                                    │
   ┌─────────────────────────────────────────────────────────▼──────────┐
   │  SOURCE DATA RETIRED — the manual path is no longer available      │
   └────────────────────────────────┬───────────────────────────────────┘
                                    ▼
                              PACK RETIRED  (counts toward KPI-094 → zero)
```

**The parallel-run step is where most of the value is realised.** Reconciling a manual pack to
the certified dashboard surfaces every place the business has been quietly computing something
differently — and each of those discrepancies is resolved *once*, in M62, rather than
perpetually.

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-BID-01 | **A certified metric is resolved through M62's semantic layer; no dashboard, report or export computes its own version** | **H** | CTO |
| BRU-BID-02 | Analytical scope is inherited from the user's ERP scope; M25 cannot widen it | **H** | CTO |
| BRU-BID-03 | A dashboard, export, subscription and embedded chart return identically permitted rows for the same user | **H** | CTO |
| BRU-BID-04 | Every published surface displays the subject area's freshness and each metric's certification status | **H** | CTO |
| BRU-BID-05 | A degraded subject area is visibly marked on every surface that uses it | **H** | CTO |
| BRU-BID-06 | Content reaching a management audience must be certified; personal exploration cannot be published directly | **H** | Data Steward |
| BRU-BID-07 | Every published dashboard and report has a named business owner | **H** | CTO |
| BRU-BID-08 | Every generated report records the metric versions and data as-of time used | **H** | CTO |
| BRU-BID-09 | A report covering a period subsequently restated is flagged as affected | **H** | CTO |
| BRU-BID-10 | Bengali rendering is verified before certification; a rendering failure blocks publication | **H** | Quality Manager |
| BRU-BID-11 | Every export is logged with user, content, scope and row count | **H** | CTO |
| BRU-BID-12 | An embedded analytics token is short-lived, scope-bound and non-replayable | **H** | CTO |
| BRU-BID-13 | Alert thresholds are owned by the receiving role, and alert volume is reported so tuning is deliberate | **C** | Functional head |
| BRU-BID-14 | An unacknowledged alert escalates to the next level within the defined window | **C** | Functional head |
| BRU-BID-15 | Content unused for two consecutive review cycles enters deprecation | **C** | Data Steward |
| BRU-BID-16 | A manual management pack cannot be retired until its replacement has completed a reconciled parallel run | **H** | CFO / CTO |
| BRU-BID-17 | Once a replacement is accepted, the source data behind the manual pack is retired | **A** | CFO / CTO |
| BRU-BID-18 | Portal-embedded analytics expose only the viewing party's own data | **H** | CTO |
| BRU-BID-19 | A prediction displayed on any surface is shown with its explanation and its model version | **H** | CTO |
| BRU-BID-20 | Operational real-time boards are not built in M25; a request for one is routed to the owning module | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.dashboard` | `fix_dashboard` | A published analytical surface | name_en, name_bn, tier (executive / functional / branch / personal / portal), audience_roles, business_owner_id, subject_area_ids, metric_codes, certification_state, review_cycle, last_reviewed, state |
| `fix.dashboard.tile` | `fix_dashboard_tile` | One visual element | dashboard_id, sequence, tile_type, metric_code, dimensions, filters, target_reference, comparison_basis, drill_target |
| `fix.report.definition` | `fix_report_definition` | A standard report | code, name_en, name_bn, owning_module, business_owner_id, parameters, layout_type (analytical / pixel_controlled), output_formats, retention_to_m24, certification_state |
| `fix.report.run` | `fix_report_run` | One generation | report_definition_id, parameters, requested_by, scope_applied, generated_at, data_as_of, metric_versions_used, duration_ms, output_document_id, restatement_flag |
| `fix.exploration` | `fix_exploration` | A saved analyst question | name, author_id, workspace (personal / shared), metric_codes, dimensions, filters, certification_state, published_to |
| `fix.subscription` | `fix_subscription` | A scheduled delivery | subscriber_id, content_type (dashboard / report), content_ref, schedule, channel, format, scope_basis, burst_dimension, active |
| `fix.burst.run` | `fix_burst_run` | One bursting execution | subscription_id, executed_at, recipient_count, succeeded, failed, failure_details |
| `fix.alert.definition` | `fix_alert_definition` | An alerting rule | metric_code, condition_type (threshold / trend / absence), parameters, evaluation_schedule, owning_role, routing, suppression_window, escalation_after, active |
| `fix.alert.instance` | `fix_alert_instance` | One raised alert | alert_definition_id, raised_at, observed_value, scope, routed_to, acknowledged_by, acknowledged_at, escalated_at, closed_at |
| `fix.embedded.surface` | `fix_embedded_surface` | An embedded chart placement | host_module, host_screen, context_binding, metric_codes, audience_roles, token_ttl_seconds |
| `fix.content.usage` | `fix_content_usage` | Adoption measurement | content_type, content_ref, user_id, role, device_class, viewed_at, duration_seconds, drill_actions |
| `fix.export.log` | `fix_export_log` | Export audit | user_id, content_ref, format, scope_applied, row_count, exported_at, ip |
| `fix.manual.pack` | `fix_manual_pack` | **The spreadsheet-retirement register** | pack_name, function, current_owner_id, frequency, effort_hours_per_cycle, metrics_harvested, replacement_content_ref, parallel_run_status, reconciliation_result, source_data_retired_at, retired_at, state |
| `fix.annotation` | `fix_annotation` | Explanatory commentary | content_ref, metric_code, period, author_id, text_en, text_bn, visible_to_roles, created_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.metric` | **M62** | **Resolve every figure — the only computation path** |
| `fix.subject.area` | M62 | Freshness, quality status, degraded flag |
| `fix.dataset` / `fix.dimension` | M62 | Conformed dimensions for exploration |
| `fix.rls.policy` | M62 | Scope enforcement at query time |
| `fix.role` / `fix.record.rule` | M29 | Audience and scope resolution |
| `fix.document` | M24 | Reports retained as records |
| `fix.notification` | M27 | Subscription and alert delivery |
| `fix.scheduled.job` | M30 / M63 | Schedule execution |
| `fix.inference.request` | M26 | Predictions displayed with explanation and model version |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-BID-01 | User logs in | Present the dashboard set for their role, scoped to their ERP scope | Present a safe default; never a wider scope |
| AUT-BID-02 | Subject area refreshed in M62 | Invalidate affected caches; update freshness indicators on all surfaces | Serve cached with a stale marker; never silently stale |
| AUT-BID-03 | M62 publishes `data.subject_area_degraded` | Mark every affected dashboard, report and embedded surface as degraded; notify subscribers of affected scheduled content | Escalate — a silently degraded dashboard is the trust failure this module exists to prevent |
| AUT-BID-04 | M62 publishes `metric.definition_changed` | Notify owners of every affected dashboard and report; annotate affected surfaces with the change and its effective date | Block the change from taking effect until notification completes |
| AUT-BID-05 | M62 publishes `data.restatement_recorded` | Flag every previously generated report covering the affected period; notify its recipients | Escalate to the CFO where materiality is exceeded |
| AUT-BID-06 | Subscription schedule due | Render, burst by scope, and deliver through M27 | Retry, then notify the subscriber of the failure with the reason |
| AUT-BID-07 | Alert condition evaluates true | Raise the alert, route to the owning role, start the acknowledgement clock, apply suppression | Escalate on delivery failure |
| AUT-BID-08 | Alert unacknowledged past window | Escalate to the next level and record the escalation | Escalate again at the second threshold |
| AUT-BID-09 | Report generated for retention | File in M24 with its metadata and reproducibility stamp | Retry; alert the report owner |
| AUT-BID-10 | Content review cycle due | Present usage statistics to the business owner and request retain-or-retire | Auto-deprecate after two unanswered cycles |
| AUT-BID-11 | Content usage falls below threshold | Flag for review with usage evidence | Log to the adoption report |
| AUT-BID-12 | Manual pack replacement certified | Open the parallel run, schedule reconciliation, notify the pack owner | Cannot proceed to retirement without reconciliation |
| AUT-BID-13 | Parallel-run reconciliation shows a discrepancy | Raise a data investigation against **M62**, not against the dashboard | Hold the retirement |
| AUT-BID-14 | Monthly | Publish the retirement register progress toward zero, and the adoption report | Escalate to the CTO on stalled retirement |
| AUT-BID-15 | Export executed | Log user, content, scope and row count | Block export if logging is unavailable |
| AUT-BID-16 | Embedded surface requested | Issue a short-lived, scope-bound signed token | Deny; never fall back to an unscoped view |
| AUT-BID-17 | Bengali rendering test fails on a certification candidate | Block certification with the failing element identified | Hard block |

---

## 12. Interfaces

### 12.1 Upstream — M25 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M62 Data Platform** | **Certified metrics via the semantic layer; curated subject areas; conformed dimensions; freshness, quality and degraded status; row-level security enforcement; restatement and definition-change events** | **Metric API + governed SQL + events** |
| M29 Identity & Security | Roles, scopes, authentication and audience resolution | Service |
| M26 AI/ML Services | Predictions with their explanations and model versions, for display only | REST |
| M27 Contact Centre & Communications | Delivery channels for subscriptions and alerts | Command |
| M63 Process Automation | Schedule execution for subscriptions, bursts and alert evaluation | Service |
| M24 Documents | Retention of generated reports as records | Command |
| All modules | Report requirements declared in each specification's §14 | Design input |

### 12.2 Downstream — M25 Provides

| Consumer | What | Mechanism |
|---|---|---|
| Every internal role | Role-based dashboards, standard reports, exploration, subscriptions, alerts | Web + mobile |
| All ERP modules | Embedded analytics inside operational screens, bound to the record in context | Signed embed |
| P01 Customer Portal | Customer's own service, spend and asset analytics | Signed embed + REST |
| P04 Corporate Portal | Corporate client's fleet, contract, disposal and spend analytics | Signed embed + REST |
| P05 / P07 Partner and Seller portals | Partner and seller performance analytics | Signed embed |
| P06 Management Portal | Executive and functional dashboards | Web + mobile |
| M60 GRC | Control dashboards, exception reporting, export audit | Dashboards + events |
| M23 Quality | Certified evidence reports for ISO and audit | Report + M24 |
| M24 Documents | Generated reports as retained records | Command |
| **M62** | **Metric consumer registration — so impact analysis knows what a definition change affects** | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `bi.content_certified` | content, type, owner, metrics used | M62 (consumer registration), M60 |
| `bi.content_published` | content, audience, owner | M27, audience roles |
| `bi.content_deprecated` | content, reason, successor, notice period | subscribers |
| `bi.alert_raised` | metric, condition, observed value, scope, routed to | **M27**, M63, owning role |
| `bi.alert_escalated` | alert, escalation level, elapsed time | M27, management |
| `bi.report_generated` | report, parameters, data as-of, metric versions, document reference | M24 |
| `bi.report_restatement_flagged` | report, period, restatement reference | recipients, M19 |
| `bi.export_logged` | user, content, scope, row count | M60, M29 |
| `bi.manual_pack_retired` | pack, function, replacement, effort released | **M60**, CFO, programme |
| `bi.adoption_reported` | period, usage by surface and role, unused content | CTO, M62 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-BID-01 | Metabase | Bidirectional | Dashboard authoring, subscriptions, alerts, sandboxing, signed embedding |
| INT-BID-02 | Grafana | — | **Boundary only** — technical observability remains with M30 / M28; no business content |
| INT-BID-03 | Document generation service | Outbound | Pixel-controlled PDF/A rendering with Bengali script support |
| INT-BID-04 | Spreadsheet export libraries | Outbound | Scoped, logged exports with Bengali rendering |
| INT-BID-05 | M27 delivery channels (email, SMS, WhatsApp, push) | Outbound | Subscription and alert delivery |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/bi/dashboards` | GET | Dashboards available to the caller, scoped | Web, mobile, P06 |
| `/api/v1/bi/dashboards/{id}` | GET | Dashboard definition and resolved tile data | Web, mobile |
| `/api/v1/bi/reports` | GET | Standard report catalogue with owners and certification | All roles |
| `/api/v1/bi/reports/{code}/run` | POST | Generate a report with parameters, scope enforced | All roles, M63 |
| `/api/v1/bi/explore` | POST | Compose a question from certified metrics and dimensions | Analysts |
| `/api/v1/bi/subscriptions` | GET / POST / DELETE | Manage subscriptions | All roles |
| `/api/v1/bi/alerts` | GET / POST | Manage alert definitions | Functional heads |
| `/api/v1/bi/alerts/{id}/acknowledge` | POST | Acknowledge an alert | Owning role |
| `/api/v1/bi/embed/token` | POST | Issue a short-lived, scope-bound embed token | Host modules, portals |
| `/api/v1/bi/usage` | GET | Adoption analytics by surface and role | CTO |
| `/api/v1/bi/manual-packs` | GET | Retirement register and progress | CTO, CFO |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R02 Chief Technology Officer** | C R U D A | All content, certification, adoption, retirement register |
| Data Steward | C R U A | Certification, content lifecycle, deprecation |
| Business Analyst | C R U | Personal exploration; build candidates for certification; governed SQL |
| Functional Head *(each)* | R U A | Owns and accepts content for their function; owns alert thresholds |
| R01 Chief Executive Officer / R05 Operations Director / R26 Finance Manager | R | Executive tier, all scopes |
| Branch Manager | R | Own branch dashboards and reports |
| R09 Service Supervisor / R35 Contact Centre Supervisor | R | Own team's operational dashboards and alerts |
| R10–R12 Technicians | R | **Own personal performance only** |
| R32 Quality Manager / ISO Coordinator | R | Certified evidence reports, control dashboards |
| R33 IT / System Administrator | — | Platform operation only; **no access to business content** |
| R36 Customer | R | **Own data only**, through P01 |
| R37 Corporate Portal User | R | Own organisation only, through P04 |
| R38 External Party (seller, partner, auditor) | R | Own records only; auditors time-boxed and scoped |

**Field-level restrictions.** Cost, margin and individual compensation measures are visible only
to the roles entitled to them in `05-04`; a dashboard cannot expose a measure the user could not
see in the ERP. Personal performance is visible to the individual and their line management,
never laterally.

**Segregation of duties.**

| Incompatible combination | Why |
|---|---|
| Content author **and** certifier | Certification is an independent check, not a self-declaration |
| Alert threshold owner **and** alert suppression administrator | Thresholds must not be quietly tuned into silence by the person they alert |
| Manual pack owner **and** sole approver of its retirement | Retirement requires the CFO or CTO, because pack owners have an incentive to keep them |
| Platform administration **and** business content access | The administrator operates the tool; they do not read the business |

---

## 14. Reports & Analytics

*(This module's own instrumentation — the reports M25 runs about itself.)*

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Executive scorecard | CEO, board | Daily | Every BO objective and canonical KPI against target, with trend and variance framing |
| Category owner dashboards | Category owners (A–K) | Daily | That category's KPIs, exceptions and benefit progress |
| Branch league table | COO, branch managers | Daily | Comparable branch performance on one definition of every measure |
| Benefit realisation tracker | CEO, CFO, Programme Director | Monthly | Actual against the BDT 876 lac benefit case, by benefit line and owning module |
| Adoption report | CTO | Monthly | Views by surface, role and device; unused and duplicated content; **manager weekly usage against the >90% target** |
| **Spreadsheet-retirement register** | CEO, CFO, CTO | Monthly | Every manual pack, owner, replacement, parallel-run status, retirement date, **progress to zero** |
| Alert effectiveness | Functional heads, CTO | Monthly | Alert volume, acknowledgement rate, escalations, suppression — detecting alert fatigue before it sets in |
| Content certification register | Data Steward, CTO | Weekly | Every dashboard and report, owner, certification status, review date |
| Performance report | CTO | Weekly | Dashboard load, report generation and drill times against target, at p95, by surface and device class |
| Export audit | GRC, CTO | Monthly | Who exported what, at what scope and volume — the main data-leakage vector in any BI estate |
| Degraded-surface log | CTO, M62 | Per event | Which surfaces were marked degraded, for how long, and why |
| Bengali rendering conformance | Quality Manager | Per release | Automated rendering test results across surfaces, formats and devices |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | Executive dashboard load time (p95) | n/a | < 8 s | **< 5 s** |
| — | Standard report generation (p95) | manual, days | < 30 s | **< 20 s** |
| — | Manager weekly dashboard usage | 0% | 70% | **> 90%** |
| **KPI-094** | **Manual management reports remaining** | 100% | < 40% | **Zero** |
| — | Manual pack effort released (hours per month) | 0 | 50% of baseline | **100% of baseline** |
| — | Dashboards displaying freshness and certification status | n/a | **100%** | **100%** |
| — | Published content without a named business owner | n/a | **0** | **0** |
| — | Uncertified content reaching a management audience | n/a | **0** | **0** |
| — | Scope divergence between dashboard, export and embed | n/a | **0** | **0** |
| — | Bengali rendering failures in certified content | n/a | **0** | **0** |
| — | Reports reproducible from their stamp | n/a | **100%** | **100%** |
| — | Alert acknowledgement rate within window | n/a | 80% | **> 90%** |
| — | Content unused for two review cycles still published | n/a | < 15% | **< 5%** |
| — | Portal analytics adoption (corporate clients using P04 analytics) | 0% | 30% | **> 60%** |

> **KPI ownership note.** `06-02` §2.7 attributes **KPI-093 (data quality test pass rate)** to
> M25. Under the v2.1 split it is instrumented and owned by **M62** — data quality is a platform
> property. **KPI-094 remains here.** Raised as an audit action.

**Six of these targets are zero or one hundred per cent**, and one of them — manual reports to
zero — is the single clearest test of whether this module succeeded. Everything else can score
well while the business quietly carries on using spreadsheets.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L4 | Metabase — authoring, dashboards, subscriptions, alerts, sandboxing, signed embedding | 34% |
| L2 | OCA `reporting-engine` / `mis-builder` — pixel-controlled and Odoo-native rendering | 10% |
| L5 | `cd_embedded_analytics`, `cd_report_distribution`, `cd_alert_engine`, `cd_statutory_report` | 56% |

Metabase carries a large share of the authoring and delivery surface. What it does not carry is
everything that makes the estate governed: certification lifecycle, freshness and degraded-status
propagation, reproducibility stamping, bursting by ERP scope, Bengali pixel rendering, the
retirement register, and the hard rule that no tile computes its own metric.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-112** | `cd_embedded_analytics` — signed scope-bound embedding, in-screen and portal placement, context binding, freshness and certification badges | Odoo module + service | 5 PW |
| **CD-191** | `cd_report_distribution` — subscriptions, bursting by ERP scope, delivery orchestration through M27, retention filing to M24, reproducibility stamping and restatement flagging | Service + Odoo surface | 5 PW |
| **CD-192** | `cd_alert_engine` — threshold, trend and absence conditions, routing, acknowledgement, suppression, escalation, effectiveness reporting | Service + Odoo surface | 4 PW |
| **CD-193** | `cd_statutory_report` — pixel-controlled rendering with **Bengali script and numerals**, content lifecycle and certification workflow, retirement register | Odoo module + service | 4 PW |
| | **Total** | | **18 PW** |

> **CD reallocation.** `02-05` §5.2 allocated **CD-110 `cd_metric_registry`** and **CD-111
> `cd_warehouse_sync`** to M25 under the v2.0 merged scope. Both move to **M62** under the v2.1
> split — the metric registry is the semantic layer and the warehouse sync is the pipeline.
> **CD-112 `cd_embedded_analytics` stays here.** CD-191…193 are claimed from the Category J
> extension block beginning at CD-187. Raised as an audit action against `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M62 Data Platform core (W4, same wave)** | **Hard dependency.** Without certified metrics there is nothing to render. M62 must land at or before M25 within W4 |
| M29 Identity & Security (W1) | Roles, scopes and audience resolution |
| M27 Contact Centre & Communications (W4) | Subscription and alert delivery channels |
| M63 Process Automation (W3) | Schedule execution for subscriptions, bursts and alert evaluation |
| M24 Documents (W3) | Retention of generated reports as records |
| Preceding operational modules | A dashboard needs the module's data to exist. Content is delivered category by category as each goes live |

**Delivery shape.** M25 is not a single W4 release. The platform, governance and the first
executive and finance surfaces land in W4; each subsequent wave adds that wave's dashboards and
reports as its modules go live. The **retirement register runs continuously from W4 to W8**, and
KPI-094 reaching zero is a W8 commitment, not a W4 one.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing management spreadsheets and packs | Every recurring pack | `fix.manual.pack` register entries; their **metric definitions harvested into M62** | W4 |
| Existing Odoo/legacy report definitions | All in active use | Rebuilt against certified metrics — not migrated | W4 onward |
| Historical report outputs | **Not migrated** — they are unreproducible, being built on definitions that were never recorded | Retained as documents only where statutorily required | — |

**Migration note.** There is no data to migrate into M25; the migration is **organisational**.
The deliverable is a complete register of every manual pack in the Company, with an owner, the
effort it consumes, and the metrics buried in it — which becomes M62's definition backlog and
this module's retirement plan. Compiling that register honestly is the hardest part of the
module and should start well before W4.

### 16.5 Register Variance

| Figure | Reference | Measured | Note |
|---|---|---:|---|
| Requirements | `02-02` est. **30** · `05-01` allocation **45** | **34** | Within the `05-01` allocation of FR-BID-001…045. IDs **035–045 are released back** to the reserved block, reflecting the v2.1 carve-out of the data platform to M62 |
| Effort | `02-02` est. **16 PW** | **18 PW** | +12%, concentrated in Bengali pixel rendering and bursting by ERP scope |

Both require `02-02` §2 Category J to be updated. Raised as an audit action.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **No dashboard tile, report or export computes a certified metric itself** — every figure resolves through M62's metric API | Code and configuration audit plus negative test |
| AC-02 | Two dashboards, a report, an export and an embedded chart return an identical figure for the same metric, scope and period | Five-way comparison test |
| AC-03 | A user's analytical scope equals their ERP scope, on every surface, and cannot be widened in M25 | Scoping test across four role types and four surface types |
| AC-04 | Every published surface displays the subject area's freshness and each metric's certification status | Visual conformance audit |
| AC-05 | A degraded subject area is visibly marked on every consuming surface within one refresh cycle | End-to-end degradation test |
| AC-06 | A metric definition change notifies the owner of every affected dashboard and report before taking effect | Sequence test |
| AC-07 | A restatement flags every previously generated report covering the affected period | Injected restatement test |
| AC-08 | A generated report can be reproduced identically from its stamp months later | Reproducibility test |
| AC-09 | **Bengali script, conjuncts and numerals render correctly on screen, in generated PDF, in print and in spreadsheet export** | Automated rendering suite across all formats and two device classes |
| AC-10 | Uncertified personal exploration cannot be published to a management audience | Negative test |
| AC-11 | An executive dashboard loads within target at p95 on a standard connection | Load test |
| AC-12 | An operational dashboard renders legibly and within target on a mid-range Android device over a 3G-class connection | Device test |
| AC-13 | A standard report generates within target at p95 | Load test |
| AC-14 | A bursted report renders per recipient scope with no cross-recipient data leakage, and one recipient's failure does not halt the run | Burst test with 51 branch scopes and an injected failure |
| AC-15 | An embed token is short-lived, scope-bound and cannot be replayed by another user | Security test |
| AC-16 | Portal analytics expose only the viewing party's own data | Negative test on P01, P04, P05 |
| AC-17 | Every export is logged with user, content, scope and row count | Audit log review |
| AC-18 | An unacknowledged alert escalates within the defined window | Timed scenario |
| AC-19 | A manual pack cannot be retired without a reconciled parallel run | Negative test |
| AC-20 | A parallel-run discrepancy raises an investigation against M62, not against the dashboard | Process test |
| AC-21 | A displayed prediction carries its explanation and model version | Integration test with M26 |
| AC-22 | Content unused for two review cycles enters deprecation automatically | Scripted scenario over a compressed clock |
| AC-23 | CTO, CFO and two functional heads sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 23 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **What is the complete inventory of manual management packs in the Company today — how many, owned by whom, consuming how many hours?** KPI-094 cannot be measured against an unknown denominator, and this is the module's headline commitment | CFO / CTO | **W4 minus 3 months** |
| Q-02 | **Who arbitrates when a manual pack's figure disagrees with the certified metric during parallel run?** The answer is usually that the pack was wrong, which is politically difficult and needs an owner before the first reconciliation | CEO / CFO | **W4 minus 2 months** |
| Q-03 | Which packs are retired by *removing the source data*, and who authorises that? Mitigation of the reversion risk depends on it | CFO / CTO | W4 build |
| Q-04 | What is the standard connection and device profile for branch management? The mobile performance target is meaningless without it | CTO / COO | W4 build |
| Q-05 | Is Metabase's AGPL-3 licence acceptable for embedded delivery into customer- and partner-facing portals, given the network-service disclosure obligation? `02-05` records deployment unmodified — does embedding change the analysis? | CTO / Legal | **W4 minus 2 months** |
| Q-06 | Which dashboards must be available in Bengali at W4, and who owns the translation of metric names? Translation drift in metric names is a real risk | COO / Quality Manager | W4 build |
| Q-07 | Do branch managers have devices and connectivity capable of the mobile experience, and if not, what is the low-bandwidth fallback? | COO / CTO | W4 minus 2 months |
| Q-08 | What are the alert thresholds for each functional area at launch, and who tunes them thereafter? Badly-set thresholds at go-live produce alert fatigue that is very hard to recover from | Functional heads | W4 build |
| Q-09 | Will individual performance dashboards be used in appraisal? If so, M57 and HR must be involved before launch, and the measurement will be contested | HR Director / COO | **W4 minus 2 months** |
| Q-10 | Which corporate clients want portal analytics, and what will they be permitted to see? | Account Management | W6 |
| Q-11 | Is the **KPI-093 / KPI-094 ownership split** (093 → M62, 094 → M25) accepted? | CTO | W4 build |
| Q-12 | Does the metric registry sit in M62 or M25? `M54` §3.2 and `02-05` say M25; the Category J overview and this specification say **M62** | CTO | **W4 minus 2 months** |

**Q-01 and Q-02 are not design questions.** They determine whether this module's headline
benefit is achievable, and both are organisational rather than technical.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` (Category J §3 the platform/BI split, §5 boundary map, §9 KPIs, §11 the
reversion-to-spreadsheets risk) ·
`M62_Data_Platform_Warehouse_and_Governance.md` (**the hard dependency** — metrics, subject areas,
freshness, scope enforcement) ·
`M26_AIML_Services_and_Model_Operations.md` (predictions displayed here) ·
`M63_Process_Automation_and_Workflow_Orchestration.md` (schedule execution) ·
`03_Modules/G_Finance_and_Treasury/M54_Cost_Accounting_Budgeting_and_FPA.md` §3.2
*(metric registry ownership — see §18 Q-12)* ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` (Metabase, Grafana, OCA reporting
engine, licence compliance notes) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` (BO-07, BO-17,
KPI-093, KPI-094) ·
§14 of every written module specification — the report requirements this module must satisfy

**Workspace evidence**
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §Benefit Register ·
`ERP system for 1000 fix/project_implementation_doc/08_UI_UX_Design_System_Wireframes.md`

**External benchmark**
**Oracle Transactional Business Intelligence (OTBI)** — analytics inheriting the ERP's own
security model, with prebuilt functional subject areas ·
**SAP Analytics Cloud** — narrative stories over a governed semantic model ·
**Microsoft Power BI** — certified and promoted datasets, workspace governance, subscriptions,
alerts, mobile layouts, embedded analytics with row-level security ·
**Metabase 0.52+** — dashboards, questions, subscriptions, alerts, verified items, attribute-based
sandboxing, signed embedding *(selected in `02-05`)* ·
**Grafana** — technical observability, retained for that purpose only ·
**OCA `reporting-engine` / `mis-builder`** — Odoo-native and pixel-controlled rendering ·
Report bursting practice — one definition rendered per recipient scope ·
Enterprise single-source-of-truth practice — certified content, tracked deprecation of shadow
reporting, adoption measured rather than assumed ·
Data storytelling practice — annotation, target lines and plain-language framing alongside the chart

**Sources consulted**
- [Metabase — product documentation and embedding](https://www.metabase.com/docs/latest/)
- [Oracle Transactional Business Intelligence overview](https://docs.oracle.com/en/cloud/saas/otbi/index.html)
- [Microsoft Power BI — endorsement and certification of content](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-endorse-content)
- [dbt Semantic Layer — consistent metrics across downstream tools](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)
- [What belongs in a modern data platform in 2026](https://bigdataboutique.com/blog/modern-data-platform-2026)

---

*Module M25 · Category J · 1000FiX ERP System v2.0 · CONFIDENTIAL*
