# Comprehensive Audit Report: Delivery Waves 1–9, Milestones, WBS Granularity & Timelines

**Target Document**: `roadmap/IR-002_Final_Production_Implementation_Roadmap.md` (4,360 lines)  
**Auditor**: Explorer 2 (Delivery Waves, Milestones & Timelines Auditor)  
**Working Directory**: `.agents/teamwork/explorer_waves_1`  
**Date**: 2026-09-29 / 2026-09-30  
**Status**: COMPLETE — AUDIT FINDINGS & SURGICAL REMEDIATIONS ISSUED

---

## 1. Executive Summary

A comprehensive, multi-dimensional forensic audit was conducted on `IR-002_Final_Production_Implementation_Roadmap.md`. The document represents an extensive and well-structured implementation execution guide covering 12 Phases, 120 Milestones, 1,200 unique Tasks, 9 Delivery Waves, 80 Sprints, and 156.5 Weeks across 67 Odoo modules and 13 application/portal surfaces.

However, the audit identified **7 major categories of critical discrepancies, logical paradoxes, broken markdown tables, and corrupted text replacement artifacts** that undermine its production readiness:

1. **Document Identity & Metadata Discrepancy**: The file is named `IR-002_Final_Production_Implementation_Roadmap.md`, yet the frontmatter (`id: IR-001`), main title (line 30), and 23 cross-references cite `IR-001`.
2. **Missing Master Schedule Milestones (`MS-01`, `MS-02`)**: The document defines milestones `MS-03` through `MS-12` matching `GV-004` §6.1, but completely omits `MS-01` (`DEP-31` legal opinion & `D-013` residency decision, Month -1) and `MS-02` (Programme kickoff & team mobilization, Month 0) from the Phase 1 and Phase 2 charters.
3. **Deadlock Circular Dependency in WBS**: An explicit 2-node circular dependency exists between `P03-M05-T08` (Party Master dedup) and `P03-M07-T07` (MDM golden-record rules), where each task mutually requires the other as a prerequisite.
4. **Nine (9) Forward Dependency Violations**: Nine tasks in earlier milestones list prerequisites on later milestones within the same phase (e.g., `P03-M02-T08` in Milestone 2 depending on `P03-M08-T04` in Milestone 8; `P04-M06-T04` in Milestone 6 depending on `P04-M07-T02` in Milestone 7; `P05-M03-T04` in Milestone 3 depending on `P05-M04-T03` in Milestone 4).
5. **Architectural Replacement & Licensing Text Corruptions**: A previous automated search-and-replace (`update_roadmap.py`) corrupted technical narratives:
   - Falsely asserts that `github.com/ceph/ceph` was archived in April 2026 and commercialized into "AIStor", when in reality `minio/minio` was archived, driving the adoption of Ceph RADOS Gateway (RGW).
   - Inverted open-source licensing attributes under `D-030` by claiming Apache Airflow is licensed under "Sustainable Use License (fair-code)" (n8n's license), Apache Kafka is licensed under "BSL" (Redpanda's license), and Apache Superset is "AGPL-3" (Metabase's license), when all three are permissive Apache-2.0.
   - States that "PostgreSQL 17 reaches end of life on 9 November 2028" (which is PG 16's EOL date) and was released in 2023, conflating PG 16 and PG 17 lifecycle data.
   - Generates duplicate naming such as `Apache Kafka/Kafka`.
6. **Point of Sale (POS) Architectural Mapping Clarification**: While all 67 modules (`M01`–`M67`) and 13 portals are scheduled, "Point of Sale" is not an Odoo retail POS module in this architecture; walk-in service desk and OTC operations are fulfilled by `M04` Branch & Front-Desk Operations, `P03` Admin Portal, `M20` Accounts Receivable, and `M51` Mushak 6.3 VAT. The roadmap must explicitly document this architectural decision.
7. **Broken Markdown Table Syntax**: Literal pipe characters `\|` inside table cells at lines 587, 956, 987, and 1011 cause column misalignment (splitting rows into 4, 8, or 10 columns instead of 3 or 7), failing strict GFM/CommonMark parsers.

---

## 2. Delivery Waves 1–9 Structure & Milestone Sequencing Audit

### 2.1 Wave-to-Phase Mapping Integrity
The roadmap maps the 9 Delivery Waves across 12 sequential Phases:
- **Phase 1** = Wave 0a: Programme Mobilisation & Blocking-Decision Closure (Months -3 to -1, Gate `G0a`)
- **Phase 2** = Wave 0b: Engineering Foundation — Environment, Monorepo, Pipeline (Months -1 to 0, Gate `G0b`)
- **Phase 3** = Wave 1a: Platform Bootstrap & Shared Kernel (Months 1–2, Sprints 1–5, Gate `G1a`)
- **Phase 4** = Wave 1b: Service Core, Front Desk & Admin Portal `P03` (Months 3–4, Sprints 6–9, Gate `G1`, Milestone `MS-03`)
- **Phase 5** = Wave 2: Field Operations, Offline Engine & Inventory (Months 5–8, Sprints 10–18, Gate `G2`, Milestone `MS-04`)
- **Phase 6** = Wave 3: Money, Movement & Documents (Months 9–13, Sprints 19–29, Gate `G3`, Milestone `MS-05`)
- **Phase 7** = Wave 4: Agreements, Billing, Contact Centre & Analytics (Months 14–18, Sprints 30–40, Gate `G4`, Milestone `MS-06`)
- **Phase 8** = Wave 5: People, Payroll, Quality & Managed Services (Months 19–22, Sprints 41–49, Gate `G5`, Milestone `MS-07`)
- **Phase 9** = Wave 6: New Asset Businesses, Event Bus & AI/ML (Months 23–26, Sprints 50–58, Gate `G6`, Milestone `MS-08`)
- **Phase 10** = Wave 7: Marketplace, Settlement & Partner Channel (Months 27–30, Sprints 59–67, Gate `G7`, Milestone `MS-09`)
- **Phase 11** = Wave 8: Intelligence, Warehouse, IoT & ESG (Months 31–34, Sprints 68–76, Gate `G8`, Milestone `MS-10`)
- **Phase 12** = Wave 9: Expansion, Decommissioning & Programme Closure (Months 35–36, Sprints 77–80, Gate `G9`, Milestones `MS-11`, `MS-12`)

### 2.2 Missing Programme Milestones (`MS-01` and `MS-02`)
- **Observation**:
  `GV-004` (Integrated Programme Plan & Master Schedule) §6.1 defines the formal programme milestone register from `MS-01` to `MS-12`:
  - `MS-01`: `DEP-31` legal opinion received; `D-013` residency decision taken (Month -1, pre-requisite to persistent build).
  - `MS-02`: Programme kickoff; team mobilised; engineering foundation established (Month 0).
  - `MS-03` through `MS-12`: Go-live gates for Waves 1 through 9.
  In `IR-002`, Phase 4 explicitly states `Milestone MS-03` (line 1609), Phase 5 states `Milestone MS-04` (line 1819), ..., Phase 12 states `Milestones MS-11, MS-12` (line 3242).
  However, **`MS-01` and `MS-02` are missing from the headers and charter exit blocks of Phase 1 and Phase 2**.
- **Impact**: Breaks traceability to `GV-004` §6.1 and creates an apparent numbering gap where the milestone sequence starts at `MS-03`.
- **Surgical Remediation**:
  - Update Phase 1 header (line 702):
    `### Wave 0a · Months −3 to −1 · 10–14 weeks · Gate G0a · Milestone MS-01`
  - Update Phase 1 Charter Exit row (line 713):
    `| **Exit criteria** | G0a — §1.10. Milestone MS-01 (DEP-31 legal opinion received & D-013 taken) |`
  - Update Phase 2 header (line 918):
    `### Wave 0b · Months −1 to 0 · 4–6 weeks · Gate G0b · Milestone MS-02`
  - Update Phase 2 Charter Exit row (after line 925):
    `| **Exit criteria** | G0b — §2.10. Milestone MS-02 (Programme kickoff & engineering foundation verified) |`

---

## 3. Task Dependency Graph Audit: Deadlocks & Forward Sequencing

A full dependency graph of all 1,200 tasks was compiled and analyzed.

### 3.1 Direct Circular Dependency (Deadlock)
- **Observation**:
  - Task `P03-M05-T08` (line 1504):  
    *Task*: "Build the deduplication and golden-record rule set, consuming M64-core's governance"  
    *Dep*: `T02, P03-M07-T07`
  - Task `P03-M07-T07` (line 1541):  
    *Task*: "Implement the golden-record rules for the party kernel that M33's dedup engine consumes"  
    *Dep*: `T01, P03-M05-T08`
- **Logic Chain**:
  `P03-M05-T08` cannot be started until `P03-M07-T07` produces the golden-record rules. Concurrently, `P03-M07-T07` declares that it cannot start until `P03-M05-T08` is complete. Neither task can ever start without violating the dependency contract.
- **Surgical Remediation**:
  The core MDM golden-record rules are defined by `M64-core` (`P03-M07-T07`) and consumed by the party kernel (`M33`).
  Remove the circular dependency by modifying `P03-M07-T07`'s `Dep` column to: `T01` (or `T01, P03-M05-T02` for party model availability), removing `P03-M05-T08` from its prerequisites.

### 3.2 Forward Dependency Violations (Sequencing Flaws)
Nine tasks declare dependencies on downstream tasks within the same phase:

| # | Caller Task | Caller Milestone | Target Task | Target Milestone | Description & Discrepancy | Surgical Remediation |
|---|---|---|---|---|---|---|
| 1 | `P03-M02-T08` (line 1447) | `P03-M02` (M29 IAM) | `P03-M08-T04` (line 1557) | `P03-M08` (M21 Employee) | Access lifecycle provisioning depends on `M21-core` leaver events, which are built 6 milestones later. | Change `Dep` in `P03-M02-T08` to `T01` (define the event contract interface); verify actual wiring in `P03-M08-T05`. |
| 2 | `P03-M05-T05` (line 1501) | `P03-M05` (M33 Party) | `P03-M09-T03` (line 1572) | `P03-M09` (Residency Z4) | Identity document routing through residency service depends on residency service built in Milestone 9. | Stub the residency client interface in `P03-M05-T05` (`Dep: T02`), and complete end-to-end integration test in `P03-M09-T08`. |
| 3 | `P03-M05-T08` (line 1504) | `P03-M05` (M33 Party) | `P03-M07-T07` (line 1541) | `P03-M07` (M64 MDM) | Consuming golden-record rules depends on rules built in Milestone 7. | In `P03-M05-T08`, build generic dedup framework (`Dep: T02`); bind `M64` rules in `P03-M07-T07`. |
| 4 | `P03-M06-T09` (line 1524) | `P03-M06` (M37 Catalog) | `P03-M07-T01` (line 1535) | `P03-M07` (M64 MDM) | Joint increment for `M37 <-> M64` depends on `M64-core` build in Milestone 7. | Co-design hook in Milestone 6 defines contract (`Dep: T01`), full joint verification occurs in `P03-M07-T01`. |
| 5 | `P03-M08-T09` (line 1562) | `P03-M08` (M21 Employee) | `P03-M09-T03` (line 1572) | `P03-M09` (Residency Z4) | Employee NID/TIN routing to Z4 depends on residency service built in Milestone 9. | Change `Dep` to `T02`; verify complete routing in `P03-M09-T03`/`T08`. |
| 6 | `P04-M06-T04` (line 1731) | `P04-M06` (P03 Admin Portal) | `P04-M07-T02` (line 1749) | `P04-M07` (Design System) | Admin portal token consumption depends on DTCG JSON token source built in Milestone 7. | Sequence `P04-M07` (Design System Foundation) before portal assembly, or stub base tokens in `P04-M06-T04` with final compile in `P04-M07-T07`. |
| 7 | `P05-M03-T04` (line 1886) | `P05-M03` (M02 Field Service) | `P05-M04-T03` (line 1902) | `P05-M04` (Geospatial) | Route orchestrator service depends on OSRM/VROOM deployment in Milestone 4. | Milestone `P05-M04` (Geospatial deployment) must precede `P05-M03-T04`, or change `Dep` to `T01` (contract design) and wire in `P05-M04-T08`. |
| 8 | `P09-M04-T03` (line 2724) | `P09-M04` (M14 Trade-In) | `P09-M05-T02` (line 2740) | `P09-M05` (M06 Data Services) | Secure data wipe step depends on wipe service built in Milestone 5. | Define data-wipe API interface in `P09-M04-T03` (`Dep: T02`), bind to `M06` implementation in `P09-M05-T02`. |
| 9 | `P09-M06-T07` (line 2764) | `P09-M06` (M26 AI/ML) | `P09-M08-T07` (line 2798) | `P09-M08` (M61 Knowledge) | AI assistant intent expansion depends on `M61` knowledge base built in Milestone 8. | Change `Dep` in `P09-M06-T07` to `T04` (offline model capability); link knowledge store in `P09-M08-T07` or `P11-M04`. |

---

## 4. WBS Granularity & Completeness Across Core Modules

The original request mandates verifying that all core modules have complete task breakdowns, deliverables, and acceptance criteria.

### 4.1 Domain Coverage Matrix

| Core Domain | Relevant Delivery Units | Roadmap Phase(s) | Milestone Breakdown | Verification & Task Granularity | Status |
|---|---|:--:|---|---|:--:|
| **Sales** | `M07` CRM & Pipeline<br>`M36` Quotation & Proposal<br>`M38` E-Commerce<br>`M11` Pricing & Dynamic Rates<br>`M39` Subscription Billing | 4, 6, 7, 10 | `P04-M04` (W1 slice)<br>`P06-M06` (Pricing & Quote)<br>`P07-M03` (Subscription)<br>`P10-M03` (E-Commerce)<br>`P10-M05` (Dynamic pricing) | 21 dedicated tasks. Full coverage of lead capture, quotation approval workflows, rate cards, and digital storefront. | **COMPLETE** |
| **Repair & Service Management** | `M01` Service Request & Order<br>`M04` Branch / Front Desk<br>`M31` Workshop Repair<br>`M17` Device Registry<br>`M05` Remote MSP Support | 4, 5, 8 | `P04-M01` (Device Reg core)<br>`P04-M02` (Branch Front-Desk)<br>`P04-M03` (Service Order core)<br>`P05-M02` (Workshop Repair)<br>`P05-M08` (Order completion)<br>`P08-M07` (Remote Support) | 40 dedicated tasks. Detailed state transitions, diagnostic trees, bench repair, QC checklists, and custody transfer. | **COMPLETE** |
| **Inventory & Warehouse** | `M15` Spare Parts & Inventory<br>`M41` Warehouse Management<br>`M03` Logistics & Fleet<br>`M16` Procurement<br>`M43` Demand Planning<br>`M44` Import / Landed Cost | 5, 6, 9 | `P05-M01` (Spare Parts)<br>`P06-M07` (Logistics, Whse, Proc)<br>`P09-M07` (Demand, Landed Cost) | 23 dedicated tasks. Bin/rack tracking, replenishment min/max, pick/pack/ship, landed cost valuation, and supplier POs. | **COMPLETE** |
| **Financial Accounting** | `M19` General Ledger<br>`M20` Accounts Receivable<br>`M52` Accounts Payable<br>`M50` Treasury & Cash<br>`M51` Bangladesh VAT / Mushak<br>`M53` Settlement & Commission<br>`M54` Cost Accounting & FP&A | 6, 7, 9, 10 | `P06-M01` (GL)<br>`P06-M02` (Mushak 6.3 core)<br>`P06-M03` (AR & Invoicing)<br>`P06-M04` (AP & Treasury)<br>`P07-M04` (NBR e-VAT)<br>`P09-M07` (FP&A)<br>`P10-M02` (Seller Settlement) | 49 dedicated tasks. Double-entry validation, bank reconciliation, automated withholding tax, Mushak 6.3/9.1 compliance, multi-party seller payout. | **COMPLETE** |
| **Warranty** | `M09` Warranty, Claims & Protection<br>`M08` Contract Lifecycle & SLA | 7 | `P07-M01` (Contracts & SLAs)<br>`P07-M02` (Warranty & Claims) | 10 dedicated tasks. OEM warranty validation, extended warranty policies, claim approval matrices, and reimbursement reconciliation. | **COMPLETE** |
| **Mobile Field Service** | `M02` Field Dispatch<br>`P02` Tech Mobile App (Flutter)<br>`P09` Rider Mobile App<br>`P11` Field Auditor App | 5, 6, 8 | `P05-M03` (Field Dispatch)<br>`P05-M04` (Geospatial/OSRM)<br>`P05-M05` (Offline Engine)<br>`P05-M06` (Technician App)<br>`P06-M09` (Rider App)<br>`P08-M09` (Auditor App) | 27 dedicated tasks. Offline SQLite sync, delta conflicts, background geolocation, turn-by-turn routing, parts consumption, digital signatures. | **COMPLETE** |
| **Customer Portal** | `P01` Customer Portal (Next.js)<br>`APP-04` Customer Mobile App<br>`P03` Operations Portal | 4, 5, 9 | `P04-M06` (Admin Portal)<br>`P05-M07` (Customer Web Portal)<br>`P09-M09` (Customer Mobile App) | 14 dedicated tasks. Booking wizard, repair tracking, online payment gateway (bKash/Nagad/SSLCommerz), push notifications. | **COMPLETE** |
| **Point of Sale (POS)** | `M04` Branch Operations<br>`P03` Front-Desk Console<br>`M20` Cash Desk / AR<br>`M51` Mushak 6.3 Receipt | 4, 6 | `P04-M02` (Walk-In intake)<br>`P04-M06` (Front desk UI)<br>`P06-M02` (Mushak invoice)<br>`P06-M03` (Cash collection) | Architecture uses `M04` + `P03` + `M20` + `M51` instead of standalone retail POS. | **CLARIFIED** |
| **Analytics & BI** | `M25` Business Intelligence<br>`M62` Data Lakehouse<br>`P06` Executive Dashboards<br>`M26` AI/ML Services | 7, 9, 11 | `P07-M07` (BI & Superset)<br>`P07-M09` (Portal P06)<br>`P09-M06` (MLflow & AI)<br>`P11-M01` (ClickHouse)<br>`P11-M02` (Warehouse DataGov)<br>`P11-M04` (Speech/NLP) | 24 dedicated tasks. dbt transformations, ClickHouse analytics cluster, Apache Superset semantic models, predictive maintenance, automated telemetry. | **COMPLETE** |

### 4.2 Point of Sale (POS) Architecture Clarification
- **Finding**: The audit cross-referenced the workspace repository (`primary-doc/`, `project-guide-doc/`, and Odoo standard architecture) for "Point of Sale" / "POS".
- In retail ERP implementations, Odoo provides a native `point_of_sale` module designed for barcode supermarkets and restaurants. However, 1000FiX ERP v2.0 is an enterprise service and repair organization across 51+ branches.
- Physical counter intake, diagnosis, estimate presentation, customer approval, over-the-counter repair handover, and cash payment collection are designed through:
  1. `M04` Branch & Front-Desk Operations (`P04-M02`)
  2. `P03` Admin & Branch Operations Portal (`P04-M06`)
  3. `M01` Service Request & Order Management (`P04-M03`)
  4. `M20` Accounts Receivable, Invoicing & Collections (`P06-M03`)
  5. `M51-core` VAT Determination & Mushak 6.3 Invoice Generation (`P06-M02`)
- **Recommendation**: Add a brief clarification callout in Section 0.4.2 (under Tier T2/T3) noting that walk-in branch retail and POS functions are fully satisfied by `M04`/`P03`/`M20`/`M51` rather than standalone retail POS.

---

## 5. Sizing, Estimation, Timeline Realism & Staffing Ramp Audit

### 5.1 Effort and Timeline Mathematical Model
- **Estate Totals**:
  - Total Phases: **12**
  - Total Milestones: **120**
  - Total Tasks: **1,200**
  - Total Sprints: **80** (2-week cadence)
  - Total Calendar Duration: **36 Months** (156.5 Weeks)
  - Wave Build Demand Total: **1,842 Person-Weeks (PW)**
- **Reconciliation of Totals**:
  - Phase 3 (W1a): ~120 PW (8.7 weeks, Sprints 1–5)
  - Phase 4 (W1b): ~119 PW (8.7 weeks, Sprints 6–9) — Wave 1 total = 239 PW
  - Phase 5 (W2): 240 PW (17.4 weeks, Sprints 10–18)
  - Phase 6 (W3): 281 PW (21.7 weeks, Sprints 19–29)
  - Phase 7 (W4): 353 PW (21.7 weeks, Sprints 30–40) — **Heaviest wave**
  - Phase 8 (W5): 247 PW (17.4 weeks, Sprints 41–49)
  - Phase 9 (W6): 235 PW (17.4 weeks, Sprints 50–58)
  - Phase 10 (W7): 185 PW (17.4 weeks, Sprints 59–67)
  - Phase 11 (W8): 39 PW (17.4 weeks, Sprints 68–76)
  - Phase 12 (W9): 23 PW (8.7 weeks, Sprints 77–80)
  - Total: $120 + 119 + 240 + 281 + 353 + 247 + 235 + 185 + 39 + 23 = \mathbf{1,842\text{ PW}}$.
  - Total weeks: $8.7 + 8.7 + 17.4 + 21.7 + 21.7 + 17.4 + 17.4 + 17.4 + 17.4 + 8.7 = \mathbf{156.5\text{ Weeks}}$ ($= 3.0\text{ years} = 36\text{ months}$).
  - Total sprints: $5 + 4 + 9 + 11 + 11 + 9 + 9 + 9 + 9 + 4 = \mathbf{80\text{ Sprints}}$.
  - The internal arithmetic of the schedule is mathematically consistent across all tables.

### 5.2 Capacity Inversion Risk (Staffing Ramp vs. Demand Curve)
- **Observation**:
  `GV-004` §5.2 models the developer staffing ramp as 3 build FTE in Wave 1, gradually ramping up to 12 FTE in Wave 6.
  This creates an **inverted capacity curve**:
  - Wave 1 demand is 239 PW against ~40.7 effective PW capacity (**5.87× deficit**).
  - Wave 4 demand is 353 PW against ~169 effective PW capacity (**2.09× deficit**).
  - Wave 8 demand drops to 39 PW against ~136 effective PW capacity (**0.29× - massive 97 PW surplus**).
- **Assessment**:
  The document openly discloses this inherited defect in Section 0.4.1 and Section 0.10.1. However, to ensure operational realism, the roadmap should explicitly reference the recommended mitigation from `GV-004` §5.3 (Option A):
  *Staff augmentation via external Odoo/Next.js implementation partner to front-load 6–8 build FTE in Waves 1–3, tapering off in Waves 7–9*, smoothing velocity to a sustainable ~25–30 PW per sprint.

### 5.3 Appendix D.0 Reconciliation Discrepancy
- In Appendix D (lines 3684–3752), the per-module requirements sum to 2,536 and 1,333 PW.
- However, measured category totals in `02-02` §3 are 2,930 requirements and 1,544 PW (shortfall of -394 requirements and -211 PW across categories C, E, F, G, I, and J).
- The roadmap documents this in Appendix D.0 and Appendix G (`IRA-03`), noting that categories C, E, F, G, I, and J carried initial estimates that grew during formal specification due to statutory and integration complexity.
- **Remediation**: Add a warning note in the table header of Appendix D referencing Section D.0 so developers do not treat the unadjusted per-module numbers as definitive sprint capacity baselines.

---

## 6. Technical Stack, Licensing & Replacement Artifact Corruptions

During the forensic review of technology baseline definitions, four major corruptions resulting from automated text replacement scripts were discovered.

### 6.1 Ceph Object Storage vs. MinIO Archival Narrative Corruption
- **Lines Affected**: 371, 458, 475, 478, 1102, 4108, 4156, 4321
- **Verbatim Error (Lines 458–461)**:
  `**ceph/ceph was archived on 25 April 2026.** Its README reads "THIS REPOSITORY IS NO LONGER MAINTAINED." The community edition is source-only with no pre-compiled binaries; the administrative web console was removed from the community edition in March 2025; and the vendor directs users to AIStor Free (standalone only) or AIStor Enterprise (distributed, commercial).`
- **Verbatim Error (Line 1102)**:
  `Do not pin Ceph Object Storage: minio/minio was archived 25 April 2026 (thus replaced by ceph/ceph) and ships no community binaries. The local image must match whatever D-028 selects, or local diverges from prod on day one`
- **Root Cause & Forensic Truth**:
  The upstream repository that was archived on 25 April 2026 was **`minio/minio`** (MinIO Inc.), which removed its console and directed users to commercial AIStor.
  This archival invalidated MinIO for 1000FiX ERP, forcing Decision `D-028`. **Ceph Object Storage (Ceph RADOS Gateway / RGW)** was selected as the robust, open-source, LGPL-2.1/Apache-2.0 replacement!
  A naive string replacement replaced `minio/minio` with `ceph/ceph`, creating the absurd claim that Ceph was archived and that developers must not pin Ceph!
- **Surgical Remediation**:
  - Restore the historical fact in §0.7.3 `D-028` (lines 456–480):
    Explain that **MinIO (`minio/minio`) was archived on 25 April 2026**, invalidating MinIO and creating blocker `B-19`.
  - State clearly that `D-028` evaluates replacements (Garage, Ceph RGW, SeaweedFS, RustFS) and selects **Ceph RADOS Gateway (RGW)** as the production baseline.
  - In `P02-M05-T02` (line 1102), replace *"Do not pin Ceph Object Storage: minio/minio was archived..."* with:  
    `Pin the Ceph RADOS Gateway (RGW) container image selected by D-028 (replacing archived MinIO). The local image must match whatever D-028 selects, so local matches prod on day one.`
  - In Appendix I (lines 4156, 4321), correctly cite MinIO's archival and Ceph RGW's adoption.

### 6.2 License Attribution Inversion in Section 0.7.3 (`D-030`)
- **Lines Affected**: 503–509, 1223, 4207
- **Verbatim Errors (Lines 503–508)**:
  - Line 505: `| Ceph Object Storage | AGPL-3 | W1 | No — and it is archived anyway (D-028) | Superseded |`
  - Line 506: `| Apache Superset | AGPL-3 | W4 | Needs a written opinion... embedded in P06 |`
  - Line 507: `| Apache Airflow | Sustainable Use License (fair-code) | W1 | No, today. Internal business purposes... |`
  - Line 508: `| Apache Kafka | BSL | W6 | No, today... Apache Kafka is Apache-2.0 with no such restriction and is already the declared alternative |`
- **Root Cause & Forensic Truth**:
  The original stack contained four restricted-license tools: MinIO (AGPL-3), Metabase OSS (AGPL-3), n8n (fair-code Sustainable Use License), and Redpanda (BSL).
  Decision `D-030` and the architectural updates **replaced all four** with fully permissive open-source alternatives:
  - MinIO -> **Ceph Object Storage** (LGPL-2.1 / Apache-2.0)
  - Metabase OSS -> **Apache Superset** (Apache-2.0)
  - n8n -> **Apache Airflow** (Apache-2.0)
  - Redpanda -> **Apache Kafka** (Apache-2.0)
  When `update_roadmap.py` replaced the names, it left the old licenses and warning notes in place! Line 508 literally says Component is "Apache Kafka", License is "BSL", and then notes that "Apache Kafka is Apache-2.0 with no such restriction"!
- **Surgical Remediation**:
  Revise the table and narrative in §0.7.3 `D-030` and Appendix I.2 `IRB-06` to state:
  - The architectural baseline eliminated restricted licenses (AGPL, BSL, Fair-Code) by standardizing on **Ceph (LGPL/Apache-2.0)**, **Apache Superset (Apache-2.0)**, **Apache Airflow (Apache-2.0)**, and **Apache Kafka (Apache-2.0)**.
  - The restricted-license gate in `P02-M08-T04` ensures no transitive or future dependencies reintroduce AGPL-3 network copyleft or non-compete fair-code licenses.

### 6.3 PostgreSQL 16 vs. 17 Lifecycle Mismatch
- **Lines Affected**: 481–496
- **Verbatim Error (Lines 483–489)**:
  `PostgreSQL 17 reaches end of life on 9 November 2028. PostgreSQL supports a major version for five years; 16 was released 14 September 2023. On a Q4-2026 kickoff, 9 Nov 2028 is roughly month 25 — inside Wave 6... which is PostgreSQL 17's date, not 16's.`
- **Root Cause**:
  `update_roadmap.py` replaced `PostgreSQL 16` with `PostgreSQL 17` indiscriminately, resulting in the contradictory claim that PostgreSQL 17 reaches EOL in November 2028 and was released in September 2023.
- **Surgical Remediation**:
  State clearly in §0.7.3 `D-029`:
  - PostgreSQL 16 was released 14 September 2023 and reaches EOL on **9 November 2028**.
  - **PostgreSQL 17 was released on 26 September 2024 and reaches EOL on 8 November 2029.**
  - Baseline is established on **PostgreSQL 17** (digest-pinned container `postgres:17.0`), providing full support through Month 36 (Q4 2029) and clearing the implementation roadmap.

### 6.4 Duplicated Terminology "Apache Kafka/Kafka"
- **Lines Affected**: 1461, 2665
- **Observation**:
  - Line 1461: `migration path to Apache Kafka/Kafka at W6 designed but not built`
  - Line 2665: `## P09-M01 — Event bus migration to Apache Kafka/Kafka`
- **Surgical Remediation**:
  Replace `Apache Kafka/Kafka` with `Apache Kafka`.

### 6.5 Document Identifier & Title Mismatch (`IR-001` vs `IR-002`)
- **Lines Affected**: 2, 30, 299, 300, 312, 381, 4002
- **Observation**:
  - Frontmatter line 2: `id: IR-001`
  - Line 30: `# IR-001 — Implementation Roadmap & Full-Stack Developer Execution Guide`
  - Filename: `IR-002_Final_Production_Implementation_Roadmap.md`
- **Surgical Remediation**:
  Update line 2 to `id: IR-002` and line 30 to `# IR-002 — Implementation Roadmap & Full-Stack Developer Execution Guide`. Update internal self-references to `IR-002`.

---

## 7. Markdown Table Formatting Integrity

An automated syntax scan across all 187 tables in `IR-002` verified that while table headers and row counts are largely sound, **four specific table rows contain unescaped or improperly escaped pipe characters `\|` that break table structure in CommonMark / GitHub Flavored Markdown (GFM)**:

1. **Line 587 (`EP-01`)**:
   `| EP-01 | Branch model: main <- release/* <- develop <- feature/* \| fix/*; hotfix/* from main | BE-003 §4 |`
   - *Problem*: The `\|` divides cell 2 into two cells, expanding the row from 3 columns to 4 columns.
   - *Remediation*: Replace `\|` with `&#124;`.

2. **Line 956 (`P02-M01-T10`)**:
   `| P02-M01-T10 | Verify no host PostgreSQL, Redis or Ceph Object Storage is running — **nothing but Odoo and the language toolchains lives on the host** | BE-001 DE-01 | Clean port map | ss -ltnp \| grep -E ':(5432\|6379\|9000)' returns nothing. A host PostgreSQL causes port is already allocated and silent version drift | DE | T06 |`
   - *Problem*: Contains 3 pipe characters inside the verification command, expanding the row from 7 columns to 10 columns.
   - *Remediation*: Encode all 3 pipes as `&#124;`: `ss -ltnp &#124; grep -E ':(5432&#124;6379&#124;9000)'`.

3. **Line 987 (`P02-M02-T01`)**:
   `| P02-M02-T01 | Install **uv** — the Python toolchain manager | BE-001 §4 | uv on PATH | curl -LsSf https://astral.sh/uv/install.sh \| sh · pinned by .python-version and uv.lock | DE | — |`
   - *Problem*: `\| sh` creates an 8th column in a 7-column table, shifting `DE` into the `Dep` column.
   - *Remediation*: Replace `\|` with `&#124;`.

4. **Line 1011 (`P02-M03-T06`)**:
   `| P02-M03-T06 | Establish the branch model: main <- release/* <- develop <- feature/* \| fix/*; hotfix/* from main | BE-003 §4.2 | Branch model documented and enforced | EP-01 | EL | T05 |`
   - *Problem*: `\| fix/*` creates an 8th column, shifting `EL` and `T05`.
   - *Remediation*: Replace `\|` with `&#124;`.

---

## 8. Prioritized Surgical Remediation Action Plan

To bring `IR-002_Final_Production_Implementation_Roadmap.md` to absolute perfection, the following modifications should be implemented by the editor agent:

### Priority 1: Structural & Markdown Integrity
1. **Fix Table Row Splitting**:
   - Line 587: Replace `feature/* \| fix/*` with `feature/* &#124; fix/*`.
   - Line 956: Replace `ss -ltnp \| grep -E ':(5432\|6379\|9000)'` with `ss -ltnp &#124; grep -E ':(5432&#124;6379&#124;9000)'`.
   - Line 987: Replace `install.sh \| sh` with `install.sh &#124; sh`.
   - Line 1011: Replace `feature/* \| fix/*` with `feature/* &#124; fix/*`.

2. **Synchronize Document Metadata**:
   - Line 2: Set `id: IR-002`.
   - Line 30: Set `# IR-002 — Implementation Roadmap & Full-Stack Developer Execution Guide`.
   - Update lines 299, 300, 312, 381, 4002 from `IR-001` to `IR-002`.

### Priority 2: WBS Dependency Graph Corrections
3. **Break Circular Deadlock**:
   - Line 1541 (`P03-M07-T07`): Change `Dep` from `T01, P03-M05-T08` to `T01`.

4. **Resolve Forward Dependencies**:
   - Line 1447 (`P03-M02-T08`): Change `Dep` from `P03-M08-T04` to `T01`.
   - Line 1501 (`P03-M05-T05`): Change `Dep` from `T02, P03-M09-T03` to `T02`.
   - Line 1504 (`P03-M05-T08`): Change `Dep` from `T02, P03-M07-T07` to `T02`.
   - Line 1524 (`P03-M06-T09`): Change `Dep` from `P03-M07-T01` to `T01`.
   - Line 1562 (`P03-M08-T09`): Change `Dep` from `T02, P03-M09-T03` to `T02`.
   - Line 1731 (`P04-M06-T04`): Change `Dep` from `T02, P04-M07-T02` to `T02`.
   - Line 1886 (`P05-M03-T04`): Change `Dep` from `T03, P05-M04-T03` to `T03`.
   - Line 2724 (`P09-M04-T03`): Change `Dep` from `T02, P09-M05-T02` to `T02`.
   - Line 2764 (`P09-M06-T07`): Change `Dep` from `T04, P09-M08-T07` to `T04`.

### Priority 3: Milestone Sequencing & Technical Accuracy
5. **Restore Master Milestones `MS-01` & `MS-02`**:
   - Line 702: Add `· Milestone MS-01` to Phase 1 header.
   - Line 713: Reference `Milestone MS-01 (DEP-31 legal opinion received & D-013 taken)` in Phase 1 exit.
   - Line 918: Add `· Milestone MS-02` to Phase 2 header.
   - Line 925: Reference `Milestone MS-02 (Programme kickoff & engineering foundation)` in Phase 2 exit.

6. **Correct Ceph & MinIO Archival Narrative**:
   - Lines 371, 458, 475, 478, 1102, 4108, 4156, 4321: Clarify that **MinIO (`minio/minio`) was archived on 25 April 2026**, driving the adoption of **Ceph Object Storage (RADOS Gateway / RGW)**. Remove claims that Ceph itself was archived.

7. **Correct Open-Source License Designations (`D-030`)**:
   - Lines 503–509, 1223, 4207: State that adopting Ceph (LGPL/Apache-2.0), Apache Superset (Apache-2.0), Apache Airflow (Apache-2.0), and Apache Kafka (Apache-2.0) successfully resolved the restricted-license risks of MinIO, Metabase, n8n, and Redpanda. Remove claims that Airflow has a fair-code license, Kafka has BSL, or Superset has AGPL-3.

8. **Correct PostgreSQL 17 Lifecycle Text**:
   - Lines 483–490: State that PostgreSQL 17 was released on 26 September 2024 and reaches EOL on 8 November 2029 (clearing the 36-month programme), while PG 16 reaches EOL on 9 November 2028.

9. **Remove Redundant Kafka String**:
   - Lines 1461, 2665: Change `Apache Kafka/Kafka` to `Apache Kafka`.

10. **Add POS Architectural Callout**:
    - Section 0.4.2: Insert an architectural note confirming that walk-in retail service desk and POS cash desk functions are fulfilled by `M04` Branch Operations, `P03` Admin Portal, `M20` Accounts Receivable, and `M51` Mushak 6.3 VAT.
