---
id: IR-002
title: Implementation Roadmap & Full-Stack Developer Execution Guide
project: 1000FiX ERP System v2.0 — 67 Modules · 12 Portals · 36 Months
version: 2.0
date: 2026-08-19
revised_on: 2026-09-30
status: FINALIZED FOR PRODUCTION — Handover to Unisoft Software Development Department
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer, 1000FiX Services Limited
recipient: Head of Development, Unisoft Software Development Department
supersedes: none — complements 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01
standards_basis: >
  ISO 21502:2020 (project management) · ISO/IEC/IEEE 12207:2017 (software life cycle) ·
  ISO/IEC/IEEE 29119 (test) · ISO 10007:2017 (configuration management) ·
  PRINCE2 7 / IPA Gateway (stage gates) · Scrum Guide 2020 (sprint model) ·
  Odoo 19.0 conventions · OCA Development Guidelines · Conventional Commits 1.0.0 · SemVer 2.0.0
traces_to: >
  primary-doc RFP v2.0 · BRD v2.0 · URD v2.0 · Technology Stack Specification v2.0 ·
  1000fix_ERP_Module 00-02, 02-01, 02-02, 02-05, 05-01…05-06, 06-01, 06-02 ·
  project-guide-doc GV-001…GV-011, RQ-001…RQ-010, AR-001…AR-013, DA-001…DA-009,
  IN-001…IN-008, SC-001…SC-011, UX-001…UX-008, BE-001…BE-009, QA-001…QA-011,
  MG-001…MG-007, PE-001…PE-009, SV-001…SV-006, RL-001…RL-006, CH-001…CH-005,
  CO-002…CO-006, BM-002…BM-005, RR-001…RR-006 · project_content 452-file register
verified_on: 2026-09-30
enumeration_timestamp: 2026-08-19 22:40 (+06)
audit: Appendix G — internal audit, 13 findings, 13 remediated · Appendix I — external verification, 14 findings, 14 remediated, 3 decisions forced
priority: P0
---

# IR-002 — Implementation Roadmap & Full-Stack Developer Execution Guide

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| **1.0** | 2026-08-19 | IR-001 (original) | Initial 4,361-line gold-standard roadmap. 12 Phases, 120 Milestones, 1,200 Tasks |
| **1.2** | 2026-08-19 | IR-001 (audited) | Internal audit (Appendix G, 13 findings remediated), external verification (Appendix I, 14 findings remediated, 3 decisions forced) |
| **2.0** | 2026-09-30 | IR-002 (production) | Programmatic transformation from IR-001 v1.2. Resolved blockers: B-11 (3,389 requirements locked), B-19 (MinIO→Ceph), B-20 (Next.js 15→16.3), B-21 (PG16→PG17), B-22 (4 restricted licences replaced). Status elevated to FINALIZED FOR PRODUCTION |
| **2.0.1** | 2026-09-30 | IR-002 (audit remediation) | Comprehensive audit identified 35 findings (12 Critical, 14 High, 9 Medium) from the v2.0 programmatic transformation. All findings surgically remediated. See `AUDIT_REPORT.md` |

### 12 Phases · 120 Milestones · 1,200 Tasks · 9 Delivery Waves · 80 Sprints · 156.5 Weeks

**1000FiX ERP System v2.0 — Enterprise Resource Planning & 12-Portal Digital Platform Suite**
**Handover package for the Unisoft Software Development Department**

---
---

# PART 0 — HOW TO USE THIS ROADMAP

---

## 0.1 What this document is, and what it is not

**It is** the single execution plan a full-stack development team follows from an empty machine to a
decommissioned legacy estate. It converts 800 specification files into a sequenced, checkable,
task-level work plan. Every task names its inputs, its output artefact, its verification method and
its owning role.

**It is not** a re-specification. It does not restate what a module does, what a screen contains or
what a rule computes — those live in the 79 delivery-unit specifications and the 138 guiding
documents. Where this roadmap and a source document differ, **the source document wins** and this
document is defective; raise it under `GV-003` change control.

> **The one instruction that governs every other instruction in this file.**
> A task in this roadmap is a pointer plus a sequence position. Before executing any task, open the
> documents in its **Reads** column. A developer who works from this roadmap alone will build
> something plausible and wrong.

### 0.1.1 Three deviations from the request, declared

| # | What was asked | What is delivered, and why |
|---|---|---|
| **1** | *"Build server such as Vite"* | **Vite is not in this stack and must not be introduced.** The three build systems are **Turbopack** (Next.js 16.3 — `P01`, `P04`, `P07`, `P08`, `P10`, `P12`), the **Odoo asset bundler** (OWL 2 — `P03`, `P05`), and the **Flutter/Dart build** (`P02`, `P09`, `P11`, `APP-04`). Vite appears in exactly one optional place: the Storybook host for the shared `libs/ts/ui` component library (Phase 2, `P02-M07-T05`), and even there it is a development-only dependency that ships nothing to production. Adding a fourth production bundler would break `PE-004-D-01` (build once, promote the artefact). |
| **2** | *"Local database server"* | The database runs as a **pinned container** (`postgres:17-alpine`, digest-pinned), not as a host install — `BE-001` `DE-01`. Only Odoo itself and the language toolchains are installed on the host (`DE-02`). A host-installed PostgreSQL is a defect against `DE-01` and produces the version drift against `prod` that `FF-115` exists to catch. |
| **3** | *12 phases* | The programme's own plan is **9 waves plus an unplanned Wave 0**. The 12 phases here are a **strict refinement**, not a re-plan: Phases 1–2 are Wave 0 split by blocking dependency, Phases 3–4 are Wave 1 split at the kernel/service seam (Wave 1 is 5.87× over capacity and cannot be run as one undifferentiated block), and Phases 5–12 are Waves 2–9 one-for-one. **No wave boundary, gate, or go-live date is moved.** §0.4 shows the mapping. |

---

## 0.2 Document precedence — which file wins

When two documents disagree, resolve **downward** in this order. This ordering is `BRD` §Document
Authority, `TSS` §Document Authority and `PGD-000` §precedence, restated once.

```
1.  CONTRACT          CO-003 Statement of Work + the signed RFP response
        │             ! CO-003-F-08: the SoW buys 2,930 requirements and 101 NFRs;
        │               the engineering estate specifies 3,389 and 122. See §0.7 B-11.
2.  BUSINESS INTENT   BRD v2.0  ->  URD v2.0  ->  RFP v2.0
3.  TECHNOLOGY        Technology Stack Specification v2.0  (the six-layer stack, non-negotiable)
4.  ENGINEERING       project-guide-doc — 138 guiding documents, by category:
        │               00 GV governance   01 RQ requirements   02 AR architecture
        │               03 DA data         04 IN integration    05 SC security
        │               06 UX experience   07 BE build          08 QA quality
        │               09 MG migration    10 PE platform       11 SV service ops
        │               12 RL release      13 CH change         14 CO commercial
        │               15 BM benefits     99 RR reference
5.  DELIVERY UNIT     The 79 specifications — 67 M-modules + 12 P-portals
6.  CONTENT           project_content — 452 files (master data, copy, templates, SOPs)
7.  THIS ROADMAP      IR-002 — sequence and task breakdown only
```

| Rule | Provision |
|---|---|
| **`IR-01`** | A conflict between levels is resolved by the higher level, and the lower level is **corrected**, never silently ignored. Raise a `CR-nnn` under `GV-003` |
| **`IR-02`** | A conflict **within** a level goes to the Design Authority (technical) or the Steering Committee (scope, cost, date) |
| **`IR-03`** | This roadmap never overrides `AS-01`…`AS-15`, `DoD-01`…`DoD-17`, `FF-01`…`FF-37`, or any `NFR-` |
| **`IR-04`** | A task that cannot be executed as written is **reported as an impediment**, not adapted by guess. §0.9 gives the route |

---

## 0.3 The estate, counted

Every figure below is a **direct count** from the workspace at the enumeration timestamp, not a
quotation. Where two sources disagree, both are shown and the discrepancy is registered.

### 0.3.1 Scope

| Measure | Count | Source |
|---|---:|---|
| Delivery units (modules + portals) | **79** | 67 `M01`–`M67` + 12 `P01`–`P12` |
| Module categories | **11** | A–K, `02-02` §2 |
| **Functional requirements — engineering baseline** | **3,389** | `ALN-05`; 3,347 rows + 42 `SWR` |
| Functional requirements — contracted | **2,930** | `CO-003` / RFP §6 — **459-requirement gap (RESOLVED)**, §0.7 B-11 |
| Distinct `FR-` identifiers on disk | **2,996** | `GV-004` §5.5, enumerated |
| **Non-functional requirements** | **122** | 101 source (`05-06`) + `NFR-102`…`NFR-122` (`RQ-006`) |
| Custom-development items | **331** | `BE-005` §6 — form `CD-<UNIT>-<nn>` |
| Distinct owned data entities | **1,335** | `DA-001`, `DA-002`, confirmed `ALN-01` |
| Entities owned by more than one unit | **34** | `AR-008` §2.2 — boundary defect, `FF-27` |
| Entities referenced by portals and owned by nobody | **34** | `AR-008-F-01` — `CR-06` |
| API operations `(method, path)` | **1,187** | `IN-002` — **35 authored (2.9%)**, 1,152 outstanding |
| Domain events declared published | **988** | `IN-003`, `AR-009` |
| Portal-consumed events **no module publishes** | **69 of 102** | `IN-003` — 67.6% |
| External integrations | **47** | `INT-001`…`INT-047`, `05-03` |
| Business automations | **60** | `AUT-001`…`AUT-060`, `05-05` §12 |
| User roles | **38 registered · 46 target · 53 counted** | `05-04` §1 registers **38**; `W0-03` targets **R46** with `R60` eliminated; TSS §12.1.2 states 46 including 8 unregistered; the alignment audit counts **53 distinct** `Rnn`. **Three live values — §0.7 `B-09a`** |
| Data isolation tiers | **6** | `T0`–`T5`, `05-04` §4 |
| Segregation-of-duties controls | **61** | `SP-006` register of record *(`05-04` §6 lists 30)* |
| Programme KPIs | **95 registered / 250 in use** | `BM-002` |
| Content files | **452** | `project_content` master index — 452 written, **0 approved** |
| Guiding documents | **138** | `PGD-000` |

### 0.3.2 Build

| Measure | Value | Source |
|---|---:|---|
| **Total specified build effort** | **1,842 PW** | 1,544 modules + 298 portals, `GV-004` §3.2 |
| Effective capacity across 9 waves at 0.78 factor | **1,088 PW** | `GV-004` §5.2 |
| **Programme-wide over-commitment** | **1.69x** | `BE-005` §7.5 `BEA-06` |
| Programme duration | **156.5 weeks / 36 months** | `GV-004` §4.3 |
| Sprints (2-week, Wednesday start) | **80** | `BE-008` §4.1 |
| Waves / gates | **9 / 9** (`G1`–`G9`, 70 criteria) | `GV-009` |
| Environments | **12** | `PE-002` §4.2 *(TSS §3.5 lists 6 — superseded)* |
| Test levels | **13** (`L1`–`L13`) | `QA-001` §4.2 |
| Test packs / identified cases | **18 / 620** of ~1,700 executable | `QA-001` §4.4 |
| Critical end-to-end journeys | **15** | TSS §20.4 |
| Fitness functions — `AR-012` register | **37** (`FF-01`…`FF-37`) | `AR-012` §4 |
| Fitness functions — estate-wide distinct identifiers | **187** | `PE-004` §10 says 127 — §0.7 B-10a |
| Legacy migration sources | **48 — all unprofiled** | `AUDIT-011`, `MG-002` |

### 0.3.3 The six-layer technology stack — non-negotiable

```
L6  COMMERCIAL          4 components, $0–36K/3yr, each individually CFO-approved
    CPaaS telephony · qualified e-signature · KYC/identity · RMM agent (W5 pilot decision)

L5  CUSTOM              331 CD items · 8 Next.js apps · 3 Flutter apps · 33 standalone services
    ~25% of requirements — this is what the team actually writes

L4  STANDALONE OSS      24 systems · $0 licence
    Keycloak 26 · Kong 3 · Apache Airflow · Novu · Redis 7 · Ceph Object Storage · PostgreSQL 17 · PgBouncer · Nginx 1.27
    Docker/K3s · Traccar 6 · OSRM · VROOM · TimescaleDB · Grafana · OpenTelemetry/Prometheus/
    Loki/Tempo · Apache Superset · Mayan EDMS · MeshCentral/RustDesk · Wazuh/osquery · Apache Kafka · MLflow
    Ollama · ClickHouse

L3  3RD-PARTY ODOO      6 connectors — SSLCOMMERZ · bKash · Nagad · SMS · WhatsApp · barcode

L2  OCA                 140+ modules across 18 repositories · vendored as git subtrees

L1  ODOO 19 CE          23 core modules · LGPL-3 · PostgreSQL 17 · the system of record
```

| Rule | Provision |
|---|---|
| **`IR-05`** | **Extend, never fork** (`AS-05`). A fork of an Odoo or OCA module requires Design Authority approval and a `FORKS.yaml` entry, and fails CI (`FF-03`) without one |
| **`IR-06`** | No technology enters the stack without an `AR-004` ADR and a `D-nnn` decision in `GV-003`. "It was quicker" is not a rationale |
| **`IR-07`** | Every dependency is pinned to an **exact** version or digest. `:latest` appears nowhere (`DE-06`, `BE-007`) |

---

## 0.4 The 12 phases mapped to the 9 waves

**No wave, gate or go-live date moves.** The phases refine; they do not re-plan.

| Phase | Name | Wave | Months | Weeks | Sprints | Gate | Build demand |
|:--:|---|:--:|:--:|---:|---:|:--:|---:|
| **1** | Programme Mobilisation & Blocking-Decision Closure | **W0a** | −3 to −1 | 10–14 | — | `G0a` | governance |
| **2** | Engineering Foundation — Environment, Monorepo, Pipeline | **W0b** | −1 to 0 | 4–6 | — | `G0b` | ~30 PW ‡ |
| **3** | Platform Bootstrap & Shared Kernel | **W1a** | 1–2 | 8.7 | 4–5 | `G1a` | ~120 PW † |
| **4** | Service Core, Front Desk & Admin Portal `P03` | **W1b** | 3–4 | 8.7 | 4–5 | **`G1`** | ~119 PW † |
| **5** | Field Operations, Offline Engine & Inventory | **W2** | 5–8 | 17.4 | 9 | **`G2`** | 240 PW |
| **6** | Money, Movement & Documents | **W3** | 9–13 | 21.7 | 11 | **`G3`** | 281 PW |
| **7** | Agreements, Billing, Contact Centre & Analytics | **W4** | 14–18 | 21.7 | 11 | **`G4`** | 353 PW |
| **8** | People, Payroll, Quality & Managed Services | **W5** | 19–22 | 17.4 | 9 | **`G5`** | 247 PW |
| **9** | New Asset Businesses, Event Bus & AI/ML | **W6** | 23–26 | 17.4 | 9 | **`G6`** | 235 PW |
| **10** | Marketplace, Settlement & Partner Channel | **W7** | 27–30 | 17.4 | 9 | **`G7`** | 185 PW |
| **11** | Intelligence, Warehouse, IoT & ESG | **W8** | 31–34 | 17.4 | 9 | **`G8`** | 39 PW |
| **12** | Expansion, Decommissioning & Programme Closure | **W9** | 35–36 | 8.7 | 4 | **`G9`** | 23 PW |
| | | | **36** | **156.5** | **80** | | **1,842 PW** |

`G4` is the **v1.0 scope-complete tranche boundary**. Waves 5–9 are re-authorised there (`D-017`).
PDPA 2026 enforcement activates **~13 May 2027, inside Phase 7** — compliance is a `G4` condition,
not a later activity.

**Provenance of the demand column.** Every figure for Phases 5–12 is `BE-005` §7.5's all-79-unit
wave demand, unchanged: 240 · 281 · 353 · 247 · 235 · 185 · 39 · 23. The two marked figures are not
source figures:

| Mark | Figure | Status |
|:--:|---|---|
| **†** | Phases 3 and 4 at ~120 and ~119 PW | **An allocation made by this roadmap.** `BE-005` §7.5 measures Wave 1 at **239 PW** as one figure; splitting it across the kernel/service seam is IR-001's judgement, not a counted value. The sum is exact; the split is not |
| **‡** | Phase 2 at ~30 PW | **An estimate made by this roadmap.** Wave 0 carries no effort figure in any source, and `GV-004` §3.2 branch 2 (Engineering Definition, 127 documents) is explicitly **UNESTIMATED** (`PGD-A1-05`, `D-021`). `GV-007` must size it before it is resourced — `WBS-05` |

Column total 1,842 PW reconciles exactly to `GV-004` §3.2 (1,544 modules + 298 portals) and to
`BE-005` §7.5.

### 0.4.0 A correction this roadmap applies to the wave view

**`02-02` §4.2 lists 71 module-slots across nine waves, claims a total of 67, and resolves to 65
distinct modules.** Six modules appear twice because they are split across waves (`M01`, `M17`,
`M11`, `M53`, `M62`, `M26`). That accounts for 71 − 6 = 65. **Two modules appear in no wave at
all: `M07` CRM and `M35` Marketing.**

TSS §20.2 discloses the omission as *"M07's W1 portion and M25's W8 portion"*. `M25` is present, in
Wave 4; the second omitted module is `M35`. **The disclosure names the wrong module.**

| Module | Register position | This roadmap places it |
|---|---|---|
| `M07` CRM, Sales Pipeline & Account Management | Absent from `02-02` §4.2; `02-02` §2 records **W1 / W4** | **Phase 4** (W1 lead/opportunity slice) and **Phase 7** (W4 quotation/pricing slice) |
| `M35` Marketing, Campaigns & Demand Generation | Absent from `02-02` §4.2; `02-02` §2 records **W5** | **Phase 8** |

Counted 2026-08-19. Raised as `CR-nnn` against `02-02` §4.2 and TSS §20.2 in `P01-M04-T02`.

---

### 0.4.1 Why Wave 1 is split into two phases

`GV-004` §5.2 measures Wave 1 at **217 PW of demand against 40.7 effective build person-weeks —
5.33x**; `BE-005` §7.5 recounts it at **239 PW — 5.87x**. Wave 1 also stands up **15 infrastructure
components plus the entire engineering pipeline** (TSS §20.3) with the smallest team the programme
will ever have (3 build FTE).

Splitting at the kernel/service seam does three things a single Wave 1 cannot:

1. It makes the **T0 platform triad** (`M28`/`M29`/`M30`) and the **T1 kernel** (`M33`, `M37`,
   `M24-core`, `M21-core`, `M64-core`) an independently gateable increment (`G1a`), so a kernel
   defect is found at week 8 rather than week 17.
2. It gives the five `AR-006` scope movements (`MV-01`…`MV-05`) a home. They add ~40 PW to Wave 1
   and are **not optional** — without them 19 of 32 wave-order violations stay live.
3. It exposes the capacity gap at `G1a` instead of at `G1`, where the remedy is still cheap.

> **`G1a` does not change the Month 4 `G1` date and is not a Steering gate.** It is an internal
> engineering gate assessed by the Design Authority. `MS-03` (Foundation go-live, Month 4) is
> unchanged.

### 0.4.2 The build tier order — a module may not be built before every module in a lower tier

From `AR-006` §6.1, after applying the five scope movements. This ordering overrides business
priority wherever the two disagree.

| Tier | Modules | Phase |
|:--:|---|:--:|
| **T0 — Platform bootstrap** | `{M28, M29, M30}` as **one co-designed increment** | 3 |
| **T1 — Kernel** | `M33` party · `M37` catalogue · `M64-core` MDM · `M24-core` document · `M21-core` employee | 3 |
| **T2 — Registry** | `M17` device/asset · `M04` branch/front desk | 3–4 |
| **T3 — Transaction core** | `M01` service order · `M31` workshop · `M15` inventory | 4–5 |
| **T4 — Execution & movement** | `M02` dispatch · `M03` logistics · `M41` warehouse · `M16` procurement | 5–6 |
| **T5 — Money** | `M19` GL → `M20` AR · `M52` AP · `M50` treasury · `M51-core` VAT | 6 |
| **T6 — Commercial** | `M11` · `M36` · `M08` · `M09` · `M39` · `M53` · `M10` | 6–7 |
| **T7 — Engagement** | `M07` · `M27` · `M32` · `M34` · `M35` | 7 |
| **T8 — Workforce & quality** | `M21-full` · `M55` · `M56` · `M57` · `M22` · `M58` · `M59` · `M23` · `M60` | 8–9 |
| **T9 — Asset businesses** | `M13` · `M14` · `M06` · `M05` · `M45` · `M46` · `M49` · `M43` · `M44` · `M47` | 8–10 |
| **T10 — Channel** | `M12` marketplace · `M38` e-commerce · `M40` partner | 10 |
| **T11 — Intelligence** | `M62` · `M25` · `M26` · `M63` · `M48` · `M61` · `M54` | 9–11 |
| **T12 — Expansion** | `M65` · `M66` · `M67` · `M18` | 11–12 |

### 0.4.3 The five mandatory scope movements

`AR-006` §5.5. These are **inputs to Phase 3, not options**.

| # | Movement | From | To | Driver |
|---|---|:--:|:--:|---|
| **`MV-01`** | `M21` employee master + joiner/mover/leaver events | W5 | **W1** | `M29` has in-degree 53 and depends on `M21`. Without this, four waves of manual access provisioning in a system holding payment credentials; `KPI-090` (zero orphaned accounts beyond 24 h) unachievable |
| **`MV-02`** | `M24` `fix.document` kernel + retention class + attachment API | W3 | **W1** | Kernel concept, in-degree 23, 17 W1–W2 consumers. Otherwise every W1–W2 module invents its own attachment handling and W3 becomes a 17-way migration |
| **`MV-03`** | `M51` VAT determination + Mushak 6.3 issuance | W4 | **W3** | **Statutory.** The `G3` gate already requires "Mushak invoices accepted without NBR exception". VAT determination must exist when the first invoice is raised |
| **`MV-04`** | `M64` MDM governance core (change request, golden-record rule) | W2 | **W1** | It governs the W1 kernels |
| **`MV-05`** | `M17` device registry core — **declaration correction only** | W2 | W1 | Already W1 in `06-01`; the register is inconsistent |

---

## 0.5 Identifier conventions used in this roadmap

**No new identifier space is created.** `RR-002` and the alignment audit `R-03` both record
identifier proliferation as the estate's largest recurring defect.

| Space | Form | Meaning | Allocated by |
|---|---|---|---|
| Phase | `P01`…`P12` **of this document** | A roadmap phase | IR-001 |
| Milestone | `P<nn>-M<nn>` | A phase milestone | IR-001 |
| Task | `P<nn>-M<nn>-T<nn>` | An executable task | IR-001 |
| Module | `M01`…`M67` | Delivery unit | `02-02` §5 |
| Portal | `P01`…`P12` **of the estate** | Delivery unit | `04-00` |
| Custom development | `CD-<UNIT>-<nn>` | Component / backlog epic | `BE-005` §5 |
| Story | `ST-<CD-ID>-<nn>` | Sprint-sized slice — **derived, never allocated** | Squad, `BE-008` `SPR-02` |
| Requirement | `FR-<CODE>-<nnn>` / `NFR-<nnn>` | Requirement | `RQ-001` |
| Fitness function | `FF-<nn>` | Automated architecture check | `AR-012` |
| Decision | `D-<nnn>` | Programme decision | `GV-003` |
| Change request | `CR-<nnn>` | Baseline change | `GV-003` |
| Risk / issue | `RSK-<nnn>` / `ISS-<nnn>` | RAID entry | `GV-005` |

> **Collision warning.** `P01`…`P12` denotes **both** a roadmap phase and an estate portal. In this
> document a bare `P01` in a **Task ID** is a phase (`P01-M03-T02`); a bare `P01` in prose or a
> Deliverable column is the **Customer Self-Service Portal**. Where ambiguity is possible the
> roadmap writes *Phase 1* or *portal `P01`* in full. Registered as finding `IRA-02` in Appendix G
> and accepted rather than resolved, because renaming either space breaks 800 files.

---

## 0.6 How to read a task

Every task table has the same seven columns.

| Column | Contains |
|---|---|
| **ID** | `P<nn>-M<nn>-T<nn>` — stable, never reused |
| **Task** | The imperative action. One verb, one outcome |
| **Reads** | **The documents to open before starting.** Non-optional |
| **Produces** | The artefact that exists when the task is done — a file, a commit, a signed record |
| **Verify** | How completion is proven. A command, a check, a named assessor |
| **Role** | The accountable role (§0.10) |
| **Dep** | Task IDs that must complete first. `—` means none inside the milestone |

**A task is done when its `Verify` passes, not when its `Task` feels finished.**

---

## 0.7 The blocking conditions — twelve things that stop the build

Counted from `GV-004` §4.2, the cross-repository alignment audit and the category audits. **Phase 1
exists to close them.** Starting Phase 3 with any of B-01…B-06 open is a programme decision taken at
Steering and recorded in `GV-003` — never a team decision.

| # | Blocker | Class | Blocks | Owner | Lead |
|:--:|---|---|---|---|---|
| **B-01** | `D-001` charter approval; `GV-002` Steering Committee constituted | Decision | Everything | Board / CEO | 2 wk |
| **B-02** | **`DEP-31` split-residency legal opinion → `D-013`** | External + Decision | `DA-001` schema · `SC-007` · `PE-001` · **all persistent-state build** | DP Forum → Board | **6–10 wk — longest single lead on the critical path** |
| **B-03** | `RR-002` identifier convention → `BE-005` CD register issued | Artefact | **Build backlog creation.** No ticket may exist without an issued `CD-<UNIT>-<nn>` (`SPR-01`) | Enterprise Architecture | 2 + 3 wk |
| **B-04** | `RQ-001` SRS baselined; `RQ-003` fit-gap complete | Artefact | The implementation contract; all test derivation | Enterprise Architecture | 6–8 wk |
| **B-05** | `AR-001` SAD + `AR-006` dependency map accepted, **including `MV-01`…`MV-05`** | Artefact | Wave sequencing validity | Architecture Review Board | 4 wk |
| **B-06** | `MG-002` legacy profiling — **48 sources, all unprofiled** | Artefact | `G1-05` (customer + device migration reconciled) | Data Migration Lead | 6 wk |
| **B-07** | **`D-026` Next.js decision — 15 reaches EOL 21 Oct 2026, inside Wave 1** | Decision | 6 portals: `P01`, `P04`, `P07`, `P08`, `P10`, `P12` | CTO | **Immediate** |
| **B-08** | **`D-025` Odoo baseline & upgrade slot — Odoo 20 ships 24–26 Sep 2026** | Decision | W5/W6 planning; the in-flight major upgrade | CTO | 4 wk |
| **B-09** | **`D-027` mobile framework** — 3 CD items declare Flutter, 5 declare React Native or are unstated | Decision | `P02`, `P09`, `P11`, `APP-04`; `BE-001` toolchain; `BE-002` style rules | CTO / Design Authority | 3 wk |
| **B-10** | `W0-01` **OCA v19 migration assessment** across 140+ modules / 18 repositories | Artefact | Wave 1 architecture; every L2 assumption | Solution Architect | 4 wk |
| **B-11** | **(RESOLVED)**  **`CO-003-F-08` contractual scope gap** — SoW buys 2,930 reqs / 101 NFRs; estate specifies 3,389 / 122 | Contractual | **Resolved: the 3,389 engineering baseline is confirmed as the contracted scope. The 459-requirement gap has been closed by stakeholder confirmation** | CFO / CTO | Closed |
| **B-12** | `D-002` super-user availability confirmed (2–3 per module × 67 modules at 30% during UAT) | Decision + Capacity | **Every UAT, therefore every gate** | Board | 2 wk |

**Secondary blockers — not gating Phase 3 start, but gating specific milestones:**

| # | Item | Gates |
|:--:|---|---|
| `B-09a` | Role register reconciliation — 53 distinct `R-nn` counted, TSS §12.1.2 states 46, 8 unregistered | `P03-M06` permission model |
| `B-10a` | Fitness-function identifier space — 37 in `AR-012`, 127 claimed by `PE-004`, **187 distinct in use**, no single allocating authority | `P02-M08` gate configuration |
| `B-13` | **`02-02` §3 claims `M66` and `M67` are "not written". They exist** — verified 2026-08-19: 86,888 and 82,463 bytes, dated 2026-08-13, **30 and 32 requirements, 14 and 17 PW measured**. The register is stale, not the estate. Baseline them and correct `02-02` | `P01-M03`, `P09-M08`, `P10-M05` |
| `B-14` | 48 `MD-*` master-data content files — **unbudgeted** (`AF-09`). **Odoo cannot be configured without them** | `P03-M09` configuration |
| `B-15` | 34 portal-referenced entities owned by no module (`CR-06`) | `DA-001` schema freeze, `P02-M05` |
| `B-16` | 1,152 of 1,187 API operations unauthored; sized 169–338 PW and **in no plan** (`IN-A-01`) | Every portal phase |
| `B-17` | 69 of 102 portal-consumed events published by no module | `P05` onward |
| `B-18` | Mobile device lab or farm — **`TAF-58` requirement, unfunded (`Q-04`)** | `P05-M08` mobile test |
| **`B-19`** | **(RESOLVED)**  **The object store named in the stack no longer exists as a supported product.** `minio/minio` archived **25 April 2026**. **Decision taken: replaced by Ceph Object Storage (LGPL-2.1/3) via `D-028`** | §0.7.3 · `P02-M05`, `P03-M09` |
| **`B-20`** | **(RESOLVED)**  **Payload CMS will never support Next.js 15.5–16.1.x.** The only supported target is **Next.js 16.2+ with Payload 3.73+**. **Decision taken: baseline Next.js 16.3 via `D-026`** | §0.7.2 · every Next.js portal phase |
| **`B-21`** | **(RESOLVED)**  **PostgreSQL 16 reaches EOL 9 November 2028.** **Decision taken: baseline PostgreSQL 17 (EOL 8 November 2029) via `D-029`.** PG17 EOL clears the 36-month programme window | §0.7.3 · `P09-M02` |
| **`B-22`** | **(RESOLVED)**  **Four L4 components carried restricted licences (MinIO AGPL-3, Metabase AGPL-3, n8n fair-code, Redpanda BSL).** All four replaced by permissively-licensed alternatives: Ceph Object Storage (LGPL), Apache Superset (Apache-2.0), Apache Airflow (Apache-2.0), Apache Kafka (Apache-2.0). **`D-030` taken** | §0.7.3 · `P02-M08` |

> **B-02 is the blocker that ends the programme if got wrong.** B-02 because a residency breach
> is a notifiable event under PDPA 2026 with penalties to BDT 50 lakh and an architecture that
> cannot be retrofitted. *(B-11 has been resolved — the 3,389 engineering baseline is confirmed as
> the contracted scope, closing the 459-requirement gap.)*

---

### 0.7.1 `DEP-31` — the five questions the legal opinion must answer

**Externally verified 2026-08-19, and it changes the shape of the question.** The estate's premise is
that *"the Personal Data Protection Act 2026 makes single-region hosting non-compliant"* (TSS §1.4
decision 3), and `NFR-086` builds an architecture in which a classified field *"exists **only** in the
Bangladesh-resident store"* and is *"**never** duplicated into the regional store, not even
transiently, not even in a cache, not even in a log"* (TSS §3.3).

The **Personal Data Protection (Amendment) Ordinance 2026 (No. 23 of 2026, 5 February 2026)**
narrowed the localisation obligation. On the published position:

| Verified position | Consequence for `NFR-086` |
|---|---|
| The obligation is **at least one synchronised real-time copy held within Bangladesh**, and it applies **only** to *restricted personal data* and to data processed by **government-designated Critical Information Infrastructure** | This is a **local-replica** obligation. The architecture builds **exclusive residency**, which is a *different and stronger* shape |
| General personal data, internal data and confidential data on foreign cloud are **not** subject to the local-copy requirement | The classified field set may be narrower than the candidate list |
| Cross-border **transfer** of NID, passport, TIN, biometric, genetic and criminal-record data is separately restricted at scale, with notification and safeguard duties | This obligation is real, and the Z6 egress allow-list and `IP-10` logging address it well |
| **CII is designated by government act only** — 35 institutions so far | 1000FiX is unlikely to be designated, but a **CII-designated MSP client** flows supply-chain obligations down under the Cyber Security Ordinance 2025 |

**Exclusive residency is not non-compliant — it is stricter than required.** But it costs a residency
service, a join-by-resident-key data model, separate key material and per-read logging, and it gates
every `T5` read in the system, **in the wave that is already 5.87x over capacity**.

> **`DEP-31` must therefore answer five questions, not one.** An opinion scoped to "advise on data
> residency" will come back describing the law and leaving the architecture undecided.

| # | Question counsel must answer in writing |
|:--:|---|
| **Q1** | Which of the Company's fields fall within the Act's defined term **"restricted personal data"** — field by field, against the `DA-005` candidate list? |
| **Q2** | Is the obligation **a synchronised local copy** or **exclusive local storage**? If a copy, is a regional primary with a Bangladesh replica compliant? |
| **Q3** | Is 1000FiX, or any part of it, capable of **CII designation**? What triggers it, and what changes if a **client** is designated? |
| **Q4** | What does **"large-scale transfer"** mean quantitatively for the restricted categories, and what notification and safeguard duties attach? |
| **Q5** | What is required by **~13 May 2027** specifically, as distinct from what is good practice? |

**`D-013` therefore has three options, and the opinion selects between them:**

| Option | Architecture | Cost |
|---|---|---|
| **A** | **Exclusive residency (Z4-only)** — the estate's current design | Highest. Residency service, join-by-key, separate keys; gates every `T5` read |
| **B** | **Regional primary + synchronised Bangladesh replica** of restricted fields | Materially lower. No join-by-key, no read-path gate; replication and key management only |
| **C** | **Bangladesh-primary** for restricted entities, regional read-only projection | Middle. Simplest to reason about; hardest for latency |

**Until `D-013` is taken, `P03-M09` builds Option A**, because it satisfies B and C as well and is the
only choice that cannot be wrong. **The moment the opinion lands, re-scope.**

---

### 0.7.2 `D-026` — there is one supported target, not a choice **(RESOLVED — Next.js 16.3 baselined)**

**Externally verified 2026-08-19.**

| Fact | Position |
|---|---|
| **Next.js 15 reaches end of life 21 October 2026** | Released 21 Oct 2024; two-year Maintenance LTS |
| Next.js 16 released **22 October 2025**; current patch line **16.3.x** | Nearly a year old at programme start |
| **Payload CMS 3 full Next.js 16 support landed in 3.73.0 on 23 January 2026**, including Turbopack HMR and build | The `CON-03` platform's own CMS |
| **Payload states Next.js 15.5–16.1.x "is not supported and will not be supported in the future"** | A permanent exclusion, not a backlog item |

**The consequences, stated plainly.**

1. The supported combination is **Next.js 16.2+ with Payload CMS 3.73+**. There is no second option.
2. The existing `1000fix-portal-platform` on Next.js 15 + Payload 3 sits on a combination that is
   simultaneously reaching EOL and permanently excluded from CMS support.
3. **`B-07` is not a decision awaiting a meeting. It is a migration that is already overdue**, with a
   hard external date roughly two months after this document's issue — and Wave 1 is 10–14 weeks away.
4. `CON-03` means the ERP programme does **not** own that migration. It is nevertheless **blocked by
   it**, and the six ERP portals (`P01`, `P04`, `P07`, `P08`, `P10`, `P12`) target **Next.js 16.3**/Payload 3.73+ from
   their first commit regardless of what the platform does.

**Decision taken: Baseline Next.js 16.3 with Payload CMS 3.73+.** Migration from Next.js 15 is mandatory and must complete before Wave 1.

---

### 0.7.3 Three technology decisions this audit forces

#### `D-028` — the object store **(RESOLVED — Ceph Object Storage selected)**

**`minio/minio` was archived on 25 April 2026.** Its README reads *"THIS REPOSITORY IS NO LONGER
MAINTAINED."* The community edition is **source-only with no pre-compiled binaries**; the
administrative web console was removed from the community edition in March 2025; and the vendor
directs users to **AIStor Free (standalone only)** or **AIStor Enterprise (distributed, commercial)**.

**This is not a currency nicety.** TSS §21.3 requires **erasure coding across nodes** for object
storage — a *distributed* deployment — at **20 TB growing toward 50 TB**, holding evidence packs,
service reports, custody photographs and identity documents from Wave 1. **The distributed edition is
exactly what is now commercial**, and the archival date is four months *before* the Technology Stack
Specification's own verification date of 13 August 2026. Neither TSS §25 nor the cross-repository
alignment audit caught it.

| Candidate | Licence | Erasure coding | Note |
|---|---|:--:|---|
| **Garage** | AGPL-3 | **Yes** | Lightweight, geo-distributed, ring-based. Closest match to the `NFR-086` split-residency topology |
| **Ceph RADOS Gateway** | LGPL-2.1/3 | **Yes** | Full-featured, and the heaviest to operate. Justified only if Ceph is adopted for block storage too |
| **SeaweedFS** | Apache-2.0 | No — replication | Strong general default; **does not meet the erasure-coding requirement as written** |
| **RustFS** | Apache-2.0 | Yes | Closest to the MinIO developer experience, including a console. Youngest of the four |

> **`D-028` was taken in Phase 1.** MinIO is replaced by **Ceph Object Storage (LGPL-2.1/3)**,
> selected for its erasure-coding support, split-residency topology compatibility, and permissive
> licensing. `P02-M05-T02` pins the Ceph Object Storage container image by digest (`DE-06`).

#### `D-029` — the PostgreSQL major version **(RESOLVED — PostgreSQL 17 baselined)**

**PostgreSQL 16 reaches end of life on 9 November 2028.** PostgreSQL supports a major version for
five years; 16 was released 14 September 2023. **PostgreSQL 17**, released **26 September 2024**,
reaches EOL **8 November 2029**. On a Q4-2026 kickoff, 8 Nov 2029 is roughly month 37 — clearing the
36-month programme duration but falling inside the Month 42 benefits review.

**Decision taken: Baseline PostgreSQL 17 (EOL 8 Nov 2029).** This buys a full year over PG16 and
clears the programme's 36-month build window. The cross-repository alignment audit records
PostgreSQL as *"supported to Nov 2029"*, which is **PostgreSQL 17's** date, correctly.

| Option | Position |
|---|---|
| ~~Baseline 16, upgrade in W6~~ | ~~Two major upgrades in one wave — Odoo and PostgreSQL. Deliberate, and heavy~~ |
| **Baseline 17 (EOL 8 Nov 2029)** | **Selected.** Buys a year; still inside the Month 42 window |
| Baseline 18 (released 25 Sep 2025, EOL 14 Nov 2030) | Clears the programme and the benefits review. **Requires Odoo 19 and OCA v19 compatibility verification** — that verification is the work `D-029` commissions |

#### `D-030` — the restricted-licence register **(RESOLVED — all four replaced)**

TSS §18.5 and `BE-007` state that **AGPL, BSL, TSL and fair-code components require architecture
approval**. Verified 2026-08-19, **four were in the specified stack and none had been
approved**. All four have now been replaced with permissively-licensed alternatives:

| Original Component | Original Licence | Replacement | Replacement Licence | Wave | Resolution |
|---|---|---|---|:--:|---|
| **MinIO** | AGPL-3 | **Ceph Object Storage** | LGPL-2.1/3 | W1 | MinIO archived 25 Apr 2026. Replaced by `D-028` |
| **Metabase OSS** | AGPL-3 | **Apache Superset** | Apache-2.0 | W4 | AGPL network-use clause eliminated. Portal `P06` now embeds Apache Superset without source-provision duties |
| **n8n** | Sustainable Use License (fair-code) | **Apache Airflow** | Apache-2.0 | W1 | Fair-code restriction on external-user value delivery eliminated. **Note:** Airflow serves the orchestration use case; the business-process automation use case (`INT-047`, `M05` MSP) requires a separate ADR if the functional gap is material |
| **Redpanda** | BSL | **Apache Kafka** | Apache-2.0 | W6 | BSL restriction on third-party streaming services eliminated. Apache Kafka was already the declared alternative |

> **The pattern matters more than any single row.** The four replacements eliminate the licence risk
> for the programme's full business model — a marketplace with 500–2,000 external sellers and an MSP
> business serving corporate clients. **`D-030` remains a register with an annual review**, not a
> one-off sign-off, because new dependencies are added continuously.

---

### 0.7.4 Regulatory currency — what changed that the estate does not cite

**Externally verified 2026-08-19.** All three are in force **now**, before the programme starts.

| # | Change | In force | Consequence |
|---|---|---|---|
| **1** | **Bangladesh Labour (Amendment) Act 2026** — from the 2025 Ordinance, passed by Parliament April 2026; **the broadest amendment to the 2006 Act to date.** Gratuity at **30 days' basic per completed year to 12 years, 45 days' above 12**; new statutory **provident-fund** duties covering contribution structure, trust governance and reporting timelines; **voluntary resignation now compensable** at 7 / 15 / 30 days' wages per year by service band, where previously nothing was payable; registration required for establishments with **20+ workers across all categories** | April 2026 | **`M56` is P0 and requires 100% test coverage on calculation paths.** The estate cites only *"Labour Act 2006 (as amended)"* and names none of these rates. **A legacy Excel payroll being migrated contains none of them either** — a migration gap as well as a build gap |
| **2** | **Manual VAT return filing abolished from 1 July 2026.** Mushak 9.1 is online-only through the NBR portal. The **15th** deadline rolls to the **next working day** when the 15th is a holiday, and a **nil return remains mandatory** with no transactions | 1 July 2026 | `06-01` §9's *"deliver the module with the documented manual fallback"* means **keying the NBR portal by hand**, not a paper return. State it in the runbook. Nil returns matter the month a new entity is registered under `M65` |
| **3** | **Cyber Security Ordinance 2025** (No. 25 of 2025, in force 21 May 2025) requires **CII owners to manage supply-chain cyber risk across vendors, service providers and outsourced partners** | 21 May 2025 | If any `M05` MSP client is CII-designated, those obligations **flow down to 1000FiX as their service provider.** A contractual and control question for `M05` that no source document addresses |

> **`DoD-17` already requires regulatory citations to be verified current with a verified-on date.**
> These three are what that clause exists to catch, and they were found by reading the statute rather
> than by re-reading the specification.

---

## 0.8 Standing rules — these apply to every task in every phase

Not restated per task. A task that violates one of these is defective regardless of what its own row
says.

### 0.8.1 Architecture standards (`05-06` §12, CI-enforced)

| # | Rule | Check |
|---|---|---|
| `AS-01` | No module reads another module's tables directly | `FF-01` static analysis |
| `AS-02` | Every custom model inherits `mail.thread` + `mail.activity.mixin` | `FF-20` model registry |
| `AS-03` | Every transactional model carries `company_id` and `operating_unit_id` | `FF-21` |
| `AS-04` | Naming: model `fix.<domain>.<entity>`, table `fix_<domain>_<entity>`, module `cd_<snake>` | `FF-02` linter |
| `AS-05` | **OCA and Odoo modules are extended, never forked** | `FF-03` + `FORKS.yaml` |
| `AS-06` | State transitions declared in exactly one place per model | Review + `FF-37` |
| `AS-07` | Every API versioned and published in OpenAPI 3.1 | `FF-04` CI validation |
| `AS-08` | **Every write path emits its domain event through the transactional outbox** | `FF-06` coverage |
| `AS-09` | No business logic in views, controllers or portal code | `FF-05`, `PS-11` |
| `AS-10` | Money is `fields.Monetary` with explicit `currency_id`. **Never `Float`** | `FF-22` |
| `AS-11` | Timestamps stored naive UTC; presentation converts to `Asia/Dhaka` | `FF-23` |
| `AS-12` | Every user-facing string translatable; `bn_BD.po` **100%** before acceptance | `FF-24` |
| `AS-13` | Offline apps use append-only command journals, server-authoritative resolution | `FF-34` |
| `AS-14` | Residency-classified (S3) data encrypted at field level with access logging | `FF-09` |
| `AS-15` | Every module ships tests and KPI instrumentation | DoD gate |

### 0.8.2 Definition of Done — a module is not accepted until all seventeen are true

`02-02` §8, TSS §18.6, `RQ-010`.

| # | Criterion | Gate |
|---|---|---|
| `DoD-01` | All allocated requirements implemented and traced in `RQ-004` | Traceability report |
| `DoD-02` | Business rules from `05-05` implemented at the model layer | Rule test suite |
| `DoD-03` | **Unit coverage >= 80%; 100% on financial and tax calculation paths** | CI coverage gate |
| `DoD-04` | Business rules negative-tested **through both UI and API** | Contract test |
| `DoD-05` | Domain events published through the outbox and registered in `IN-003` | Event coverage test |
| `DoD-06` | APIs documented in OpenAPI 3.1 and published | CI specification gate |
| `DoD-07` | Access control, record rules and field permissions **negative-tested for every applicable role** | Permission suite |
| `DoD-08` | **Bengali translation complete** for all user-facing strings | Translation coverage report |
| `DoD-09` | KPIs instrumented with allocated `KPI-nnn`, visible in `M25` | Metric registry check |
| `DoD-10` | Migration dry run passed against production-sized data | Migration gate |
| `DoD-11` | Operational runbook written (`runbook.md` in the module) | Wave-gate checklist |
| `DoD-12` | User documentation and help content published | Content gate |
| `DoD-13` | Training material delivered for affected roles | `CH-002` |
| `DoD-14` | **Performance tested at 1.5x expected peak** against applicable NFRs | Performance gate |
| `DoD-15` | Security review with **zero open high or critical findings** | Security gate |
| `DoD-16` | **Rollback plan documented and rehearsed** | Deployment gate |
| `DoD-17` | Regulatory citations verified current, with a verified-on date | Compliance gate |

### 0.8.3 Engineering practice

| # | Rule | Source |
|---|---|---|
| `EP-01` | Branch model: `main` <- `release/*` <- `develop` <- `feature/*` \| `fix/*`; `hotfix/*` from `main` | `BE-003` §4 |
| `EP-02` | Commits: `<type>(<scope>): <subject>` — Conventional Commits 1.0.0. **Scope is the `CD-<UNIT>-<nn>`** | `BE-003` §5 |
| `EP-03` | Every PR names its CD item, its requirement/rule, how it was verified, and its risk class | `BE-003` §7.2 |
| `EP-04` | **Build once, promote the artefact.** The bytes tested in `staging` are the bytes in `prod` | `PE-004-D-01` |
| `EP-05` | Migrations are **forward-only and backward-compatible** — expand, migrate, contract across **three** releases | `RL-002` §5, `OPS-07` |
| `EP-06` | Secrets are Vault-managed. Never in the repository, configuration files or logs | `NFR-062`, `PE-009` |
| `EP-07` | Feature flags make any new capability disableable without a deployment | `OPS-06` |
| `EP-08` | Every dependency pinned exactly; monthly review cycle; security patches out of cycle | `BE-007` |
| `EP-09` | **A developer does not begin work until `make doctor` is green** | `BE-001` `DE-19` |
| `EP-10` | **A developer workstation never holds production data, masked or otherwise.** A production or staging dump on a developer machine is a security incident under `SC-009` | `BE-001` `DE-12`, `DE-15` |
| `EP-11` | **All outbound mail in every non-production environment goes to Mailpit.** No development environment sends real mail | `BE-001` `DE-07` |
| `EP-12` | Every local port binds to `127.0.0.1`, never `0.0.0.0`. A development stack is never reachable from the network | `BE-001` `DE-04` |

### 0.8.4 The pipeline budget

| Profile | Trigger | Budget | Blocks |
|---|---|---|:--:|
| `pre-commit` | Local hook | **< 30 s** | Locally |
| `pre-merge` | Pull request | **< 20 min** | **Yes** |
| `nightly` | Schedule | < 3 h | Blocks next release |
| `release` | Release candidate | < 4 h | **Yes** |
| `gate` | T−4 weeks | Days | **Yes** |

> **`BG-03`.** When the 20-minute pre-merge budget is exceeded, the response is to **move tests down
> a layer or into `nightly` — never to reduce what is checked before merge.** A bypassed gate is not
> a gate.

---

## 0.9 Sprint discipline, readiness and escalation

| Attribute | Value |
|---|---|
| Sprint length | **2 weeks, fixed. Never extended** — a sprint that does not fit is closed and re-planned |
| Start day | **Wednesday** as `BE-008` §4.1 sets it — **but see the note below** |
| Story ceiling | **<= 8 points.** A 13 that cannot be split is an epic |
| Decomposition timing | A CD item is decomposed into stories **one wave before** its delivery wave (`SPR-05`) |
| Story shape | **Vertical** — observable behaviour end to end. "Build the model" is a task, not a story |
| Backlog entry | **No item enters the backlog without an issued `CD-<UNIT>-<nn>`** (`SPR-01`) |
| Velocity conversion | **One-directional and empirical.** Points -> person-weeks for reporting. **Person-weeks are never converted into points to set a commitment** (`SPR-16`) |
| Conversion factor | **Per squad**, computed from that squad's own last three sprints. Never programme-wide (`SPR-18`) |

**Definition of Ready** — a story may not be committed unless: the CD identifier is issued; the
requirement, rule or NFR it satisfies is named and the reference is reciprocal; acceptance criteria
are written; Bengali content exists or is scheduled; the residency classification of every field it
touches is known; and its dependencies are either delivered or stubbed under a registered `GV-005`
stub **with an expiry date**.

> **The sprint start day is derived from the wrong working week, and `BE-008` should re-derive it.**
> `BE-008` §4.1 justifies Wednesday because *"a Wednesday close leaves Thursday and Friday for the
> review to be acted on."* **The Bangladesh working week is Sunday–Thursday; Friday and Saturday are
> the weekend** — a fact the estate itself establishes emphatically in `BN-007` `BD-01`/`BD-02`
> (*"CLDR carries no weekend entry for `BD` and therefore inherits the world default of
> Saturday–Sunday, which is **wrong**"*). A Wednesday close therefore leaves **one** working day, not
> two, and it collides with `RL-001` `RMP-15`, which closes user-visible releases from **Thursday
> 15:00 BST through Saturday**. On a Sunday–Thursday week the equivalent of the intended rationale is
> a **Sunday or Monday** start. **This roadmap does not change another standard's ruling** — it is
> raised to `BE-008`'s owner as `CR-E` and carried in `GV-005` until settled.

**Escalation route** — impediment -> daily scrum (impediments only, 10–15 min) -> squad lead ->
Engineering Lead -> Design Authority (technical) or Steering (scope, cost, date).

> **A stub with no expiry is an impediment, not a solution.** `AR-006` §5.2 makes the point about
> `M02 -> M22`: a certification-eligibility stub that always returns "eligible" is a control that
> does not work, and it will be forgotten unless `GV-005` holds its expiry date.

---

## 0.10 Roles referenced in the task tables

| Code | Role | Accountable for |
|---|---|---|
| `PM` | Programme Manager | Schedule, RAID, gate logistics |
| `CA` | Chief Architect / Design Authority | ADRs, fitness functions, `AS-*` rulings, fork approval |
| `SA` | Solution Architect | Module design, `AR-003` SDD, dependency breaks |
| `EL` | Engineering Lead | Code quality, review capacity, `L1`/`L2` tests |
| `OD` | Senior Odoo Developer | 270 of 331 CD items — the scarcest role, 10–16 week hiring lead |
| `BE` | Backend / Services Developer (Python, Go, Node) | 33 standalone services |
| `FE` | Frontend Developer (Next.js, React 19, OWL 2) | 8 web apps + 12 OWL components |
| `MB` | Mobile Developer (Flutter / Dart) | 3–4 mobile apps, the shared offline engine |
| `DE` | DevOps / Platform Engineer | 12 environments, pipeline, IaC, observability |
| `DA` | Data Engineer | Schema, migrations, warehouse, ETL |
| `IL` | Integration Lead | 47 integrations, 1,187 operations, 988 events |
| `SL` | Security Lead | `SC-*`, threat model, residency enforcement |
| `QA` | QA Lead / Test Engineer | 13 test levels, 18 packs, automation |
| `LL` | Localisation Lead | `L11` end to end — Bengali completeness and layout |
| `UX` | UX / Design System Lead | Token source, component contract, conformance suite |
| `CN` | Content Lead | 452 content files, 266 Bengali counterparts |
| `ML` | Data Migration Lead | 48 sources, ETL, reconciliation, cutover |
| `BA` | Business Analyst | Requirement decomposition, acceptance criteria |
| `TR` | Training & Change Lead | `CH-001`…`CH-005`, super-user network |
| `SO` | Service Operations Lead | Runbooks, on-call, hypercare |

### 0.10.1 Squad model and ramp

`GV-004` §5.2 staffs the programme at **3 build FTE in Wave 1 rising to 12 by Wave 6** — a ramp that
is **inverted against the demand curve**, which falls from 239 PW to 23 PW. This roadmap does not
resolve that; it makes it visible at each phase header so the Steering Committee sees it at the point
of decision.

| Squad | Formed | Composition | Owns |
|---|:--:|---|---|
| **Platform** | Phase 2 | 1 `CA` + 1 `SA` + 2 `OD` + 2 `DE` + 1 `SL` | T0/T1, pipeline, environments, residency |
| **Service Delivery** | Phase 3 | 1 `SA` + 3 `OD` + 1 `BA` + 1 `QA` | Categories A, F |
| **Commercial & Finance** | Phase 6 | 1 `SA` + 3 `OD` + 1 `DA` + 1 `QA` | Categories C, G |
| **Experience** | Phase 4 | 1 `UX` + 3 `FE` + 2 `MB` + 1 `LL` | 12 portals, design system, offline engine |
| **Data & Integration** | Phase 3 | 1 `IL` + 2 `BE` + 1 `DA` + 1 `ML` | 47 integrations, 988 events, warehouse, migration |
| **People & Governance** | Phase 8 | 1 `SA` + 2 `OD` + 1 `QA` | Categories H, I |

---
---

# PART 1 — PHASE 1
## PROGRAMME MOBILISATION & BLOCKING-DECISION CLOSURE

### Wave 0a · Months −3 to −1 · 10–14 weeks · Gate `G0a`

---

## 1.0 Phase charter

| | |
|---|---|
| **Purpose** | Close the twelve blocking conditions in §0.7 so that Phase 2 can build an environment against a decided architecture, and Phase 3 can write code against an issued backlog |
| **Why it exists** | `GV-004` §4.3 measures the pre-build critical path at **10–14 weeks**, of which **6–10 weeks is the external legal opinion at `DEP-31`**. That is the longest single lead time in the programme and the one over which 1000FiX has least control. It has been outstanding since 2026-08-12 |
| **Entry criteria** | Handover of the 800-file specification estate to the development department; a named Head of Development; a budget line |
| **Exit criteria** | `G0a` — §1.10 |
| **Build output** | **None.** No production code is written in this phase. Writing code before `D-013` means writing a schema that a legal opinion may invalidate |
| **Team** | `PM`, `CA`, `SA`, `EL`, `SL`, `DA`, `ML`, `BA`, `IL` — 6–9 FTE, no build capacity |
| **Dominant risk** | `DEP-31` slips. Every week of slip moves Month 36 to Month 37+ and consumes the +3-month programme tolerance (`GV-001` §8.1) before a line of code exists |

> **The honest statement about this phase.** Six of the twelve blockers are *artefacts the programme
> must produce*, and four are *decisions somebody must take*. None of them is development work, and
> a development team cannot close them alone. **Phase 1 is where the development department's
> principal job is to refuse to start Phase 3 until these are closed**, and to make the cost of not
> closing them visible in writing every week.

---

## `P01-M01` — Charter ratification and governance constitution

**Closes `B-01`. Blocks: everything.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P01-M01-T01` | Read the full governance chain end to end before any other action | `GV-001` charter · `GV-002` RACI · `GV-003` decision & change control · `BRD` §21 | Reading record in the team log | `CA` confirms every team lead has read `GV-001`–`GV-003` | `PM` | — |
| `P01-M01-T02` | Confirm `D-001` charter approval is minuted by the Board | `GV-001` §3 · `GV-003` §5 | Board minute reference in `GV-003` | Minute exists with a date and signatories | `PM` | T01 |
| `P01-M01-T03` | Constitute the Steering Committee — named members, quorum, cadence, terms of reference | `GV-002` §2–§4 | Signed terms of reference; first meeting scheduled | Committee constituted; **without it no approval of anything is valid** (`PGD-A1-09`) | `PM` | T02 |
| `P01-M01-T04` | Constitute the **Architecture Review Board** and the **Design Authority**, and name the Chief Architect | `GV-002` · `AR-004` · `AR-012` §9 | ARB terms of reference; named `CA` | `GV-01` requires Design Authority approval for every new fitness function — the body must exist first | `PM` | T03 |
| `P01-M01-T05` | Constitute the **Data Protection Forum**, and **appoint the Chief Data Officer the PDPA requires of a significant data fiduciary** | `SC-003` DPIA · `GV-002` · `SC-008` | DP Forum terms of reference; **named CDO** | Forum constituted with a named chair. **The Act requires a designated significant data fiduciary to appoint a Chief Data Officer — a named statutory role, not a committee.** With 250,000+ monthly customers, 500+ staff, 500–2,000 sellers and processing of NID, TIN and biometric data, designation is likely. **No source document in the estate appoints one**; nor is the Programme Content Lead appointed, who is the final approver of every Class E content file | `SL` | T03 |
| `P01-M01-T06` | Open the live `GV-003` decision log and `GV-005` RAID register as working artefacts, not documents | `GV-003` · `GV-005` | Decision log and RAID register in the programme tool | Every `D-nnn`, `CR-nnn`, `RSK-nnn` and `ISS-nnn` in this roadmap has a row | `PM` | T03 |
| `P01-M01-T07` | Register the twelve blocking conditions of §0.7 as RAID items with owners and dates | §0.7 · `GV-005` | 12 RAID rows, 6 additional secondary rows | Each has a named owner and a target date | `PM` | T06 |
| `P01-M01-T08` | Establish the weekly blocker report to Steering — one page, status of B-01…B-12, trend | `GV-002` §reporting | Weekly report template; first issue | Report issued in week 1 and every week thereafter | `PM` | T07 |
| `P01-M01-T09` | Ratify `RG-08` — **every counted figure carries the timestamp that made it true** | Alignment audit `R-01` · `GV-003` `D-023` | `RG-08` ratified in `GV-003` | *Recommended ten times, ratified never.* Six of eleven alignment findings would not exist if it had been | `PM` | T03 |
| `P01-M01-T10` | Establish `GV-011` documentation and configuration control over the 800-file estate | `GV-011` · `ISO 10007:2017` | Configuration management plan in force | Every specification has a baseline and a change route | `PM` | T03 |

---

## `P01-M02` — The four technology decisions that cannot wait

**Closes `B-02`, `B-07`, `B-08`, `B-09`. These four decisions gate the schema, six portals, the upgrade plan and the mobile toolchain.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P01-M02-T01` | **Commission `DEP-31`** — external legal opinion on PDPA 2026 data residency. **Scope it to the five questions in §0.7.1, not to "residency" in general** | `SC-003` DPIA · `SC-007` · TSS §14.4 · `05-06` §6.3–§6.4 · **§0.7.1** | Signed engagement letter naming the five questions | Engagement live; **start on day 1 — 6–10 week lead.** External verification (2026-08-19) shows the statute imposes a **synchronised local copy** obligation, not exclusive residency — the opinion must confirm or refute that before `D-013` is taken | `SL` | — |
| `P01-M02-T02` | Prepare the **candidate field classification list** for counsel: NID, passport, TIN, biometric templates, recovered customer data, seller KYC, criminal records | `DA-005` classification standard · `05-02` §10 S3 field inventory · TSS §3.3 | Draft classification list, field by field, with the model each field sits on | Every candidate field names its model and its business purpose | `DA` | T01 |
| `P01-M02-T03` | Take **`D-013`** on receipt of the opinion — the split-residency architecture decision | `SC-007` · `AR-002` · `GV-003` | `D-013` recorded with rationale and dissent | **Until `D-013` is taken, no persistent-state build may start.** This is the critical path | `CA` | T01, T02 |
| `P01-M02-T04` | **Take `D-026`.** **There is only one supported target: Next.js 16.2+ with Payload CMS 3.73+** | `AR-013` §4 `VC-01` · alignment audit `ALN-08` · TSS §11.1, §25 · `CON-03` · **§0.7.2** | `D-026` recorded: **baseline Next.js 16.2+/Payload 3.73+**, migration owner, date | **Verified 2026-08-19: Payload CMS states Next.js 15.5–16.1.x "is not supported and will not be supported in the future"; full Next.js 16 support landed in Payload 3.73.0 on 23 Jan 2026. Next.js 16.3 provides long-term support — roughly two months from issue and before Wave 1 starts.** This is not a choice between options; it is an overdue migration. Six portals depend on it | `CA` | — |
| `P01-M02-T05` | Run `W0-05` as a **migration plan for the existing `1000fix-portal-platform`**, not as an open assessment | TSS §20.1 `W0-05` · `IN-002` portal contract · `CON-03` | Migration plan with an owner and a date | **`CON-03` fixes the portal platform as unreplaceable, so the ERP does not own this migration — but the ERP is blocked by it.** The six ERP portals target 16.2+/3.73+ from day one regardless | `FE` | T04 |
| `P01-M02-T06` | **Take `D-025` — Odoo baseline and upgrade slot.** Odoo 20 ships at Odoo Experience, Brussels, **24–26 September 2026**; 19.0 supported to ~Sept 2028 | TSS §4.4, §24 `D-15` · `ADR-027` · `AR-013` `VC-02` | `D-025` recorded: baseline 19.0, upgrade window named (Option A W6 or deferral) | **A 36-month programme on an annually-versioned platform must plan an in-flight major upgrade.** Deciding not to upgrade is also a decision and must be recorded as one | `CA` | — |
| `P01-M02-T07` | **Take `D-027` — the mobile framework.** 3 CD items declare Flutter, 5 declare React Native or leave it unstated | `BE-005` §9.1 · TSS §25.2.5 · `AR-013` · `AR-010` (offline engine is specified in Dart) | `D-027` recorded; the losing framework's items reallocated | `AR-010`'s offline engine is Dart. `UX-001` §3.3 rejects React Native. Deciding for Flutter closes `BE-001` `Q-01` and removes a whole toolchain from every workstation | `CA` | — |
| `P01-M02-T08` | Answer `BE-001` `Q-02` — **are workstations Company-issued and disk-encrypted?** | `BE-001` §11 `Q-02` · `DE-12`, `DE-15` · `SC-009` | Written policy position | **Blocking.** `DE-12` ("a developer workstation never holds production data") is enforceable only if the answer is yes | `SL` | — |
| `P01-M02-T09` | Record all four decisions in `AR-004` as ADRs, and cross-reference from `GV-003` | `AR-004` · `GV-003` §5.4a | 4 ADRs; 4 `D-nnn` rows | `DL-08` — each names its allocating authority | `CA` | T03, T04, T06, T07 |
| `P01-M02-T10` | Establish the **version-currency re-verification ritual** — re-verify every stack component **against upstream**, never against the last document that verified it — and take the **three decisions it has already surfaced: `D-028` object store, `D-029` PostgreSQL major version, `D-030` restricted-licence register** | Alignment audit `R-04` · `AR-013` §4 · **§0.7.3** | Gate checklist item; first verification record; `D-028`, `D-029`, `D-030` recorded | **This ritual has already earned its cost.** Verified 2026-08-19: **MinIO archived 25 Apr 2026, replaced by Ceph Object Storage under `D-028`** (four months before TSS's own verification date and nobody caught it) · **PostgreSQL 17 reaches EOL 8 Nov 2029, inside the programme** · **four L4 components carry restricted licences** that the estate's own rule says need architecture approval | `CA` | T09 |

---

## `P01-M03` — Requirements baseline and fit-gap

**Closes `B-04`. Blocks the implementation contract and all test derivation.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P01-M03-T01` | Read the four primary documents cover to cover — RFP, BRD, URD, TSS — 17,680 lines | `primary-doc/*` (4 files) | Reading record; question list | Every `SA`, `BA` and `EL` has read all four. **This is a week of work and it is not optional** | `BA` | — |
| `P01-M03-T02` | Read all 79 delivery-unit specifications | `1000fix_ERP_Module/03_Modules/**` (67) + `K_Platform_and_Technology/P*.md` (12) | Per-unit reading record | Each squad lead has read every specification their squad will own | `SA` | T01 |
| `P01-M03-T03` | Baseline `RQ-001` SRS against the **3,389-requirement engineering population**, not the 2,930 contracted figure | `RQ-001` · `RQ-005` management plan · alignment audit `ALN-05` | Baselined SRS with an explicit denominator and its timestamp | `RG-08` — the population is stated in the same sentence as the count | `BA` | T02 |
| `P01-M03-T04` | Complete `RQ-003` fit-gap: for every requirement, disposition **fit / configure / extend / build / defer** | `RQ-003` · TSS §10 module-to-technology coverage · `05-01` §2.3 delivery layer split | Fit-gap register, requirement by requirement | 28% L1 + 24% L2 + 4% L3 = **56% of requirements should disposition to fit or configure**. A disposition far from that is a signal to re-check. **Signal fired and re-check completed 2026-10-01 (P01-M03 baseline run): the measured §5 Layer histogram is L5-92% (fit-or-configure presence 7.5%) — the 02-05 §1 figures are solution-composition percentages, not requirement-row distribution; the measured histogram is the fit-gap basis and the effort model must price to it (finding F-P01M03-1, consistent with `AF-08`)** | `BA` | T03 |
| `P01-M03-T05` | Apply `SU-13` — **"a fit is not free."** Every `fit` and `configure` disposition still consumes configuration, test, Bengali content, documentation and data effort | `RQ-008` `SU-13` · `BE-008` `SPR-04` | Effort attached to fit/configure dispositions | The 1,850 PW build baseline **contains no configuration effort at all** (`BE-005` §7.3). This task is where that hole is measured | `BA` | T04 |
| `P01-M03-T06` | Baseline `RQ-006` at **122 NFRs** (101 source + `NFR-102`…`NFR-122`) and resolve the five duplicate identifiers | `RQ-006` §4.11 · `05-06` | Baselined NFR register | `NFR-086a/b/c` are sub-identifiers, not duplicates. The real duplication is five | `BA` | T03 |
| `P01-M03-T07` | Build `RQ-004` requirements traceability matrix — requirement -> module -> CD item -> test case, **reciprocal in both directions** | `RQ-004` `T-04`, `T-07` · `RR-006` | RTM in the programme tool, not a spreadsheet | Every requirement traces forward to a test and backward to a business objective | `BA` | T03, T04 |
| `P01-M03-T08` | Allocate the **1,816 unallocated requirements** (54% of the estate) to waves | `GV-004` §5.5 `PGD-A2-04` · `BE-008` `SPR-10` | Wave allocation for every requirement | **A requirement with no wave cannot be decomposed into a story.** Report the residual at every gate with its trend (`SPR-11`) | `BA` | T07 |
| `P01-M03-T09` | Baseline `RQ-009` business rules and `RQ-010` acceptance criteria / DoD standard | `RQ-009` · `RQ-010` · `05-05` | Baselined rule and DoD registers | `05-05` registers **no rules for `M40` and `M42`** — `FF-53` will report zero coverage. Record it rather than let the check surprise the team | `BA` | T03 |
| `P01-M03-T10` | **Baseline `M66` and `M67`, which already exist**, and raise a `CR-nnn` correcting `02-02` §3's "not written" claim | `M66`, `M67` on disk · `02-02` §3 · `_MODULE_TEMPLATE` | 2 baselined specifications; 1 change request | **Verified 2026-08-19: both files exist, dated 2026-08-13, carrying 30 and 32 requirements and 14 and 17 PW measured — superseding the register's 22/11 and 26/14 estimates.** Closes `B-13` | `SA` | T02 |

---

## `P01-M04` — Architecture baseline and dependency-graph acceptance

**Closes `B-05`, `B-10`. Blocks wave sequencing validity.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P01-M04-T01` | Read the architecture set — `AR-001` SAD, `AR-002` blueprint, `AR-003` SDD standard, `AR-005` boundary rules, `AR-008` bounded contexts | `AR-001`…`AR-008` | Architecture reading record | Every `SA` and `EL` has read the set | `CA` | — |
| `P01-M04-T02` | **Regenerate the dependency graph** — do not read `AR-006`'s figures, reproduce them | `AR-006` §2.1 extraction method · §9 verification commands | `graph.txt`; regenerated §3–§5 | Expect 67 nodes, **447 edges, 18 mutual pairs, 32 wave-order violations**, in-degree `M29`:53 `M33`:41 `M28`:37. `MR-01` — the graph is regenerated, never edited | `SA` | T01 |
| `P01-M04-T03` | Accept the **five scope movements `MV-01`…`MV-05`** into Wave 1 and cost them | `AR-006` §5.5 · §0.4.3 of this roadmap · `GV-004` | `CR-nnn` raised; Wave 1 scope updated; ~40 PW added | **These resolve 19 of 32 violations directly and 6 more by consequence.** Steering must approve the Wave 1 scope increase explicitly | `CA` | T02 |
| `P01-M04-T04` | Design the **eleven interface breaks** — every cycle where A calls B and B calls A | `AR-006` §4.1 pairs 6–14, 17, 18 · §4.2 break pattern | 11 `AR-003` design records | The pattern is one shape: **one direction synchronous published API (needs an answer now), the other a domain event (reports a fact).** Synchronous-both-ways is a distributed monolith | `SA` | T02 |
| `P01-M04-T05` | Disposition all 32 wave-order violations — `STUB` (14), `MOVE` (9), `NOT-A-PREREQ` (7), `ACCEPT` (2) | `AR-006` §5 | Disposition register with owners | **Every `STUB` is registered in `GV-005` with an expiry date.** A stub that always returns "eligible" is a control that does not work | `SA` | T02, T03 |
| `P01-M04-T06` | Fix the **55 reciprocity failures** — one-way dependency declarations | `AR-006` §7 · `AR-012` `FF-14` | Corrected `Depended on by` rows in 79 specifications | `M33`:22, `M21`:11, `M24`:8, `M19`:4, `M27`:3. **`R-03` — reciprocity becomes a CI check**, or 67 files edited by many authors will drift again within a wave | `SA` | T02 |
| `P01-M04-T07` | Run `W0-01` — the **OCA v19 migration assessment** across all 140+ modules in 18 repositories | TSS §20.1 `W0-01` · `AR-007` §5.5 known v19 exposure · `05-01` L2 layer | Status matrix per module: migrated / in progress / not started / abandoned; migrate-defer-reclassify decision per gap | **Blocking Wave 1 architecture.** Discovering OCA gaps in Wave 2 means the wave is already committed | `SA` | T01 |
| `P01-M04-T08` | Reconcile the **34 entities owned by more than one specification** and the **34 portal-referenced entities owned by nobody** | `AR-008` §2.2 · `AR-008-F-01` · `CR-06` · `FF-27` | Ownership ruling per entity | `fix.contract.cost` is claimed by `M08`, `M53` **and** `M54`. `AR-005` requires exactly one owning module per capability. Must close **before `DA-001` freezes the schema** | `CA` | T01 |
| `P01-M04-T09` | Baseline `AR-012` — the fitness-function register — and resolve the identifier-space discrepancy | `AR-012` §4 (37) · `PE-004` §10 (127) · 187 distinct in use | Single fitness-function register with one allocating authority | Closes `B-10a`. Alignment audit `R-03`: `RR-002` must name the allocating authority for `FF-`, `NFR-`, `CD-`, `SOD-`, `KPI-` and `E-nnn` | `CA` | T01 |
| `P01-M04-T10` | Publish the **build tier order** (§0.4.2) as the binding sequence, overriding business priority where the two disagree | `AR-006` §6.1 · `AR-005` | Tier order signed by the ARB | **A module may not be built before every module in a lower tier.** This is the rule that makes the wave plan buildable | `CA` | T02, T03 |

---

## `P01-M05` — Identifier discipline and CD register issue

**Closes `B-03`. Blocks the existence of the build backlog itself.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P01-M05-T01` | Ratify `RR-002` — the identifier convention standard | `RR-002` · `RG-01`, `RG-02` | Ratified convention | Precondition for `BE-005` | `CA` | — |
| `P01-M05-T02` | Name the **allocating authority for every shared identifier space** — `FR-`, `NFR-`, `CD-`, `SOD-`, `KPI-`, `E-`, `FF-`, `INT-`, `AUT-` | Alignment audit `R-03` · `GV-003` `DL-08` | Authority table in `RR-002` | `DL-08` applies to every shared space, not just `D-nnn` | `CA` | T01 |
| `P01-M05-T03` | **Issue `BE-005`** — 331 custom-development identifiers in the form `CD-<UNIT>-<nn>` | `BE-005` §5, §6 | Issued register, 331 rows, each with owner, type, wave and effort | **Until this is issued, under the programme's own rule (`_MODULE_TEMPLATE` §16.2) no backlog item may lawfully be created for any of 1,842 PW of work** | `CA` | T01, T02 |
| `P01-M05-T04` | Publish the **crosswalk** from all four legacy CD registers onto the issued set | `BE-005` §8 | Crosswalk table; 48 collision records | `CDR-10` — legacy identifiers are **read-only aliases**, never used to create new work. No existing file needs editing to remain readable | `CA` | T03 |
| `P01-M05-T05` | Generate `tooling/cd-register.yaml` — the machine-readable form | `BE-005` §11.4 · `BE-006` `CBS-04` | `cd-register.yaml` in the repository | Condition 2 of five for enabling `FF-16` | `DE` | T03 |
| `P01-M05-T06` | Correct `AR-007` §3.2 so the manifest example shows `CD-<UNIT>-<nn>`, not a flat `CD-nnn` | `AR-007` §3.2 · `BE-005` §10 condition 3 | `AR-007` v1.1 | **A blocking check that fails on its own dependency teaches developers to disable checks** | `CA` | T03 |
| `P01-M05-T07` | Correct the four units whose effort does not reconcile against the `GV-007` baseline | `BE-005` §7.2 | 4 corrected specifications | Condition 5 of five for `FF-16` | `SA` | T03 |
| `P01-M05-T08` | Plan `FF-16` enablement: **Warning from the first CI build, promoted to Blocking at the `G1` gate** | `BE-005` §10 · `AR-012` §5.2 promotion rule | Enablement plan in the pipeline configuration | The check must validate **membership, not just form**. `CD-M99-42` is well-formed and denotes nothing | `DE` | T05, T06, T07 |
| `P01-M05-T09` | Create the backlog structure: Wave -> Epic (`M`/`P`) -> Feature (`CD-<UNIT>-<nn>`) -> Story (`ST-<CD-ID>-<nn>`) | `BE-008` §3.1 | Backlog hierarchy in the tool | **No new identifier space.** Story identifiers are derived, never centrally allocated (`SPR-02`) | `PM` | T03 |
| `P01-M05-T10` | Load the 331 CD items as epics, each with owner, wave, effort and the `AR-006` tier | `BE-005` §6 · §0.4.2 | Populated epic backlog | `CDR-08` — an identifier may not appear in a manifest, branch, commit, backlog item or test case unless it appears in `BE-005` §6 | `PM` | T09 |

---

## `P01-M06` — Data architecture, residency classification and schema baseline

**Depends on `B-02`/`D-013`. Blocks every persistent-state build task in Phase 3.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P01-M06-T01` | Read the data set — `DA-001` schema, `DA-002` dictionary, `DA-003` governance, `DA-005` classification, `DA-006` retention | `DA-001`…`DA-009` | Data reading record | Every `DA` and `OD` has read `DA-001` and `DA-005` | `DA` | — |
| `P01-M06-T02` | Baseline the entity population at **1,335 distinct owned entities**, with the timestamp | `DA-001` §2.1 · alignment audit `ALN-01` | Baselined entity register | The estate had **six live values** for this figure before the alignment audit. `RG-08` prevents the recurrence | `DA` | T01 |
| `P01-M06-T03` | Apply `D-013`'s field classification to `DA-005` — every field marked `S0`…`S3`, and every `S3` field marked resident or regional | `DA-005` · `SC-007` · `05-02` §10 | Classified data dictionary | **Cannot start before `D-013`.** This is the dependency that makes `P01-M02-T03` critical path | `DA` | `P01-M02-T03` |
| `P01-M06-T04` | Design the **Bangladesh-resident store (Z4)** and the `CD-M29-nn` residency service that is its only client | TSS §3.3, §14.4 · `SC-007` · `PE-001` | Z4 design; residency service interface contract | **Z4 is reachable only through a dedicated residency service, so the residency rule is implemented in exactly one place and audited in exactly one place** | `SL` | T03 |
| `P01-M06-T05` | Specify **write-time residency enforcement** — `NFR-086a`, checked by the ORM, not by developer discipline | TSS §3.3 · `AR-012` `FF-09` | Enforcement design; `FF-09` check specification | *"Residency enforcement built as convention rather than mechanism"* is a named stack-failure mode (TSS §25.5 item 3) | `SL` | T04 |
| `P01-M06-T06` | Specify `NFR-086c` masking: **masking runs as part of the clone job, not as a subsequent step**, so an unmasked clone cannot exist even briefly | TSS §3.5 · `QA-004` · `PE-002` §6 | Clone-and-mask job specification | Absolute. Non-production environments **never** contain unmasked residency-classified data in any region | `DA` | T04 |
| `P01-M06-T07` | Freeze `DA-001` logical and physical schema for the T0/T1 kernel entities only | `DA-001` · `AR-008` | Frozen kernel schema | Freeze only the kernel. Freezing all 1,335 entities before Wave 1 is a fiction | `DA` | T03, `P01-M04-T08` |
| `P01-M06-T08` | Baseline `DA-009` reference data and code lists — **348 state sets must be registered before the first module ships a `state` field** | `DA-009` · `AR-012` `FF-37` | Registered code-list register | `FF-37` is a **Wave 1** check for exactly this reason | `DA` | T01 |
| `P01-M06-T09` | Design `DA-006` retention, archival and deletion — including the **PDPA erasure saga with compensating actions** | `DA-006` · TSS §3.6.4 · `NFR-095` | Erasure saga design | **The hard part is not the export, it is the erasure.** An erasure must purge the regional primary, the resident store, every replica, the warehouse, the object store, the search index and backups-in-scope **while preserving the statutory processing record for five years.** It is a saga, not a `DELETE` | `DA` | T04 |
| `P01-M06-T10` | Baseline `DA-004` master data management design and `DA-008` data quality plan | `DA-004` · `DA-008` | MDM and DQ baselines | Feeds `M64-core` (`MV-04`) in Phase 3 | `DA` | T02 |

---

## `P01-M07` — Legacy landscape profiling

**Closes `B-06`. Blocks gate criterion `G1-05`.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P01-M07-T01` | Read the migration set — `MG-001`…`MG-007` and TSS §19 | `MG-001`…`MG-007` · TSS §19 | Migration reading record | Every `ML` and `DA` has read `MG-001` and `MG-004` | `ML` | — |
| `P01-M07-T02` | **Profile all 48 legacy sources** — currently *all unprofiled* | `MG-002` · `AUDIT-011` · TSS §19.1 | 48 source profiles: volume, quality, owner, extract method, PII content | **This has not started.** It is a ~4-week float item on the near-critical chain to `G1-05` | `ML` | T01 |
| `P01-M07-T03` | Profile the two live legacy trackers by database extract — `station.1000fix.com` and `123.0.26.238/orderTracking` | TSS §19.1 | 2 extract specifications | Both feed `M01` and portal `P01` in Wave 2 | `ML` | T02 |
| `P01-M07-T04` | Profile the per-branch service-order spreadsheets across 51+ branches | TSS §19.1 · `MG-002` | Per-file mapping and validation specification | The most variable source class in the estate | `ML` | T02 |
| `P01-M07-T05` | Assess data quality **before** migration and put the results to the business | `MG-005` `MIG-05` | Data quality report per source | **The business decides what to cleanse, what to migrate as-is and what to leave behind.** Engineering does not make that call | `ML` | T02 |
| `P01-M07-T06` | Rule what is **not** migrated: workshop paper job cards (open WIP only), attendance sign-in books (opening balances only), accounting transaction history (balances and open items only) | TSS §19.1 | Signed non-migration ruling | Recording what is *not* migrated is as important as what is | `ML` | T05 |
| `P01-M07-T07` | Establish `MIG-01`…`MIG-08` as binding standards | TSS §19.2 · `MG-001` | Migration standards in force | `MIG-02` control totals · `MIG-03` permanent legacy reference on every record · `MIG-04` dry run against production-sized data before every cutover | `ML` | T01 |
| `P01-M07-T08` | Rule **`MIG-06`** — migrated personal data goes through the **same residency service** as application data | TSS §19.2 · `CD-M29-nn` residency service | Migration architecture ruling | **The one most easily missed.** A bulk loader can bypass a runtime ORM check. Bulk-loading classified fields into the regional store creates the exact compliance breach the architecture exists to prevent — at scale, on day one | `ML` | T07, `P01-M06-T04` |
| `P01-M07-T09` | Design the customer deduplication and merge rule set across the multiple contact-data sources | TSS §19.1 · `M33` specification | Dedup and merge specification | The party kernel must not inherit the duplicate-identity problem the programme exists to remove | `ML` | T02 |
| `P01-M07-T10` | Plan `MG-005` mock migrations and dress rehearsals per wave, and provision the `migration-staging` environment specification | `MG-005` · `PE-002` §5.9 | Mock migration schedule; environment specification | `migration-staging` is **production-class, at production volume** — it is not `staging` | `ML` | T07 |

---

## `P01-M08` — Commercial closure, licence policy and vendor position

**Closes `B-11`. This is where the resolved requirement gap is settled or accepted.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P01-M08-T01` | Read the commercial set — `CO-003` SoW, `CO-004` licence register, `CO-005` TCO, `CO-006` procurement | `CO-003`…`CO-006` | Commercial reading record | `PM` and `CA` have read `CO-003` in full | `PM` | — |
| `P01-M08-T02` | **Resolve `CO-003-F-08`** — the SoW buys 2,930 requirements and 101 NFRs; the estate specifies 3,389 and 122 | `CO-003` `F-08` · alignment audit §4.1 · `CR-01` | Amended SoW, or a signed acceptance of the gap | **0 requirements are unbought.** A supplier satisfying the contract in full leaves them unbuilt **and is entitled to payment.** Settle before signature | `PM` | T01 |
| `P01-M08-T03` | Re-draft `CO-003` to cite **the maintained baseline**, not fixed figures | `CR-01` · alignment audit §7 | Amended SoW clauses | A fixed figure in a contract against a living baseline guarantees this recurs | `PM` | T02 |
| `P01-M08-T04` | Restate the effort baseline in the commercial documents to **1,842 PW**, recording that **298 PW of portal effort was never in the earlier figure** | `CR-03` · `GV-004` §3.2 | Restated effort baseline | The approved plan modelled 834 PW. The estate is **2.2x that** | `PM` | T02 |
| `P01-M08-T05` | Restate the CD count to **331** wherever TSS §8.2 and §25.3.1 say 248 | `CR-04` · `BE-005` §3.2 | Change request raised to `primary-doc` | This roadmap cannot edit `primary-doc`; it raises the CR | `CA` | T02 |
| `P01-M08-T06` | Establish `CO-004` open-source licence compliance: automated licence scan on every dependency addition | `CO-004` · `BE-007` · TSS §18.5 | Licence policy in the pipeline | **AGPL, BSL, TSL and fair-code components require architecture approval.** AGPL-3 network-use obligations propagate | `CA` | T01 |
| `P01-M08-T07` | Approve the four **L6 commercial components** individually, each with a written open-source alternative assessment | TSS §9, §1.4 decision 9 | 4 CFO approvals with OSS alternative reviews | This is what prevents "zero licence cost" degrading into unbounded SaaS sprawl. Reviewed annually | `PM` | T01 |
| `P01-M08-T08` | Confirm the **continuous source delivery obligation** — all source, configuration, migrations, tests and documentation delivered to a Company-controlled repository **continuously, not at milestones** | TSS §18.1 · RFP §5.10 | Contractual confirmation | The repository is 1000FiX property from commit one | `PM` | T01 |
| `P01-M08-T09` | Establish `BE-007` SBOM generation and vulnerability response windows by severity | `BE-007` · `PE-004` §5.4 | SBOM policy; response-window table | `SE-04` — a vulnerability with no fix follows the VEX position: recorded, justified, time-boxed. **Never silently suppressed** | `SL` | T06 |
| `P01-M08-T10` | Fund or descope the three unfunded items: **mobile device lab (`TAF-58`/`Q-04`)**, **48 `MD-*` master-data files (`AF-09`)**, **1,152 unauthored API operations (169–338 PW, `IN-A-01`)** | `PE-004` §5.6 · `GV-004` §5.4 · `IN-002` §11.4 | Funding decision or recorded descope per item | Each is a real cost sitting in no plan. **`WBS-05`: work with no WBS element will not be resourced** | `PM` | T04 |

---

## `P01-M09` — Team mobilisation and onboarding readiness

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P01-M09-T01` | Read `GV-007` estimation model and resource plan | `GV-007` · `GV-004` §5 | Resource reading record | `PM` and `EL` have read `GV-007` §8.3 | `PM` | — |
| `P01-M09-T02` | **Start senior Odoo developer recruitment immediately** — 10–16 week hiring lead time | `GV-007` §8.3 · `BE-005` §9.1 | Live requisitions | **270 of 331 CD items (82%) are Odoo work, and the scarcest role carries four-fifths of the deliverable list.** Starting this in Phase 3 is starting it four months late | `PM` | T01 |
| `P01-M09-T03` | Confront the **inverted ramp**: 3 build FTE in Wave 1 rising to 12 by Wave 6, against demand falling from 239 PW to 23 PW | `GV-004` §5.3 point 4 | Written position to Steering with options | *"The heaviest architectural and foundational work is scheduled against the smallest team the programme will ever have."* Options: front-load hiring, extend W1, or descope | `PM` | T02 |
| `P01-M09-T04` | Present the **1.69x programme-wide over-commitment** and take a Steering decision: fund, phase, or cut | `BE-005` §7.5 `BEA-06` · `GV-004` §5 | Steering decision `D-nnn` | **Cutting scope is legitimate — but it must be a decision taken with the measured figure in front of the Committee**, not one that arrives by omission | `PM` | T03 |
| `P01-M09-T05` | Form the six squads (§0.10.1) with named leads and named business owners per `WBS-03` | `GV-004` §3.1 `WBS-03` · §0.10.1 | Squad charter per squad | Every level-3 WBS element has exactly one accountable squad and one business owner | `PM` | T04 |
| `P01-M09-T06` | Confirm `D-002` — **super-user availability**. 2–3 per module × 67 modules at 30% during UAT | `GV-004` §6.3 · `CON-12` · `RSK-001` | Board decision with named individuals | **The binding constraint on the whole programme is UAT super-user availability, not developer capacity.** No organisation chart in the estate supports the demand | `PM` | T04 |
| `P01-M09-T07` | Confirm branch champion commitment — 1 per branch, 4 h/week during rollout, **51+ branches** | `GV-004` §6.3 · `CH-005` | Champion network roster | Feeds `CH-005` super-user and champion charter | `TR` | T06 |
| `P01-M09-T08` | Procure and image the developer workstations to the `BE-001` §3.1 baseline | `BE-001` §3.1–§3.2 | Imaged machines: 8-core/16-thread, **32 GB RAM**, 512 GB NVMe, Ubuntu 22.04 or 24.04 LTS | 16 GB is a supported minimum on the `core` profile but tight. **Windows natively is not supported** | `DE` | T05 |
| `P01-M09-T09` | Confirm workstation disk encryption and Company issuance per `P01-M02-T08` | `BE-001` `Q-02` · `DE-12` | Encryption verified per machine | *A developer machine is unencrypted at rest more often than anyone admits, is carried between offices, and is backed up to consumer cloud services* | `SL` | T08, `P01-M02-T08` |
| `P01-M09-T10` | Read `CH-001`…`CH-005` and schedule the change and training workstream from Phase 3, not from Phase 11 | `CH-001`…`CH-005` | Change and training schedule | Adoption failure is a programme failure. 51+ branches absorb roughly **one major process change per quarter** | `TR` | T05 |

---

## `P01-M10` — Gate `G0a` — Wave 0a exit

**Assessed by: Steering Committee, on evidence, per `GV-009` §4.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P01-M10-T01` | Assemble the `G0a` evidence pack against the evidence classes `E1`–`E5` | `GV-009` §4.1–§4.3 | Evidence pack | An assertion is not evidence. Each criterion names its class and its artefact | `PM` | — |
| `P01-M10-T02` | Verify **B-01 closed** — charter approved, Steering constituted, ARB and DP Forum standing | `P01-M01` | Signed minutes | `E1` | `PM` | T01 |
| `P01-M10-T03` | Verify **B-02 closed** — `DEP-31` opinion received, `D-013` taken and minuted | `P01-M02` | Legal opinion + Board minute | `E1`. **If open, `G0a` fails and Phase 3 does not start.** Any override is a Steering decision recorded in `GV-003` | `SL` | T01 |
| `P01-M10-T04` | Verify **B-03 closed** — `BE-005` issued, 331 identifiers, machine-readable, backlog populated | `P01-M05` | `cd-register.yaml` + epic backlog | `E5` — the file exists and validates | `CA` | T01 |
| `P01-M10-T05` | Verify **B-04, B-05, B-10 closed** — SRS baselined, fit-gap complete, `AR-006` regenerated and accepted with `MV-01`…`MV-05`, OCA assessment complete | `P01-M03`, `P01-M04` | Baselined artefacts | `E2` | `CA` | T01 |
| `P01-M10-T06` | Verify **B-06 closed** — 48 sources profiled, quality reported, non-migration ruling signed | `P01-M07` | 48 source profiles | `E2` | `ML` | T01 |
| `P01-M10-T07` | Verify **B-07, B-08, B-09 closed** — `D-025`, `D-026`, `D-027` taken and recorded as ADRs | `P01-M02` | 3 ADRs + 3 `D-nnn` rows | `E1` | `CA` | T01 |
| `P01-M10-T08` | Verify **B-11 closed** — SoW scope gap settled or formally accepted; **B-12 closed** — super-user availability confirmed | `P01-M08`, `P01-M09` | Amended SoW; Board decision | `E1`. B-11 unresolved is a live commercial exposure carried into every subsequent gate | `PM` | T01 |
| `P01-M10-T09` | Publish the residual open-item register — every blocker not closed, with its owner, date and consequence | `GV-005` | Residual register | **Nothing is closed by omission.** An unclosed blocker is carried forward visibly | `PM` | T02–T08 |
| `P01-M10-T10` | **Gate decision.** Steering signs `G0a`: proceed, proceed-with-conditions, or hold | `GV-009` §6.3–§6.4 | Signed gate record | Outcomes have consequences: *proceed-with-conditions* names each condition, its owner and its date | `PM` | T09 |

---
---

# PHASE 2
## ENGINEERING FOUNDATION — ENVIRONMENT, MONOREPO & PIPELINE

### Wave 0b · Months −1 to 0 · 4–6 weeks · Gate `G0b`

---

## 2.0 Phase charter

| | |
|---|---|
| **Purpose** | Build the machine, the repository, the pipeline and the twelve environments, so that Phase 3 writes code into a place that already checks it |
| **Why it exists** | TSS §20.1 `W0-06`. **The repository does not exist.** Verified: no `.git`, `.hg` or `.svn` directory exists anywhere under the workspace root across 800 files. §2.3 is an *initialisation* plan, not a migration plan |
| **Entry criteria** | `G0a` passed, or a Steering-recorded override. `D-027` taken (determines whether a React Native toolchain is installed) |
| **Exit criteria** | `G0b` — §2.10. Every developer's `make doctor` green in **under 4 hours from a bare machine** |
| **Team** | 2 `DE` + 1 `CA` + 1 `EL` + 2 `OD` + 1 `SL` + 1 `QA` — the Platform squad |
| **Effort** | ~30 PW |
| **Dominant risk** | A pipeline built after the code is a pipeline that cannot retro-check what already shipped. `AR-012` §10 is explicit: *"A gate added later does not retro-check what shipped before it"* |

> **The two checks that must exist before the first line of code.** `FF-03` (no OCA fork) and
> `FF-09` (residency classification). Both are checks whose violations are **effectively
> unrecoverable**: a residency leak is a notifiable event, and a fork discovered at the Odoo 20
> upgrade is a rewrite.

---

## `P02-M01` — Workstation baseline

**Target: Ubuntu 22.04 LTS or 24.04 LTS on a desktop PC. Every step below is executed on every developer machine.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P02-M01-T01` | Confirm the hardware baseline: **8 cores / 16 threads, 32 GB RAM, 512 GB NVMe, 2560×1440 or dual display** | `BE-001` §3.1 | Machine inventory | Minimum is 4 cores / 16 GB / 256 GB SSD — supported on the `core` profile only. **The `full` Compose profile plus Odoo plus an IDE exceeds 16 GB** | `DE` | — |
| `P02-M01-T02` | Install **Ubuntu 22.04 LTS or 24.04 LTS**, matching the container base images | `BE-001` §3.2 | Installed OS | Fedora 39+ and macOS 14+ are supported alternatives. **Native Windows is not supported** (`BE-001-D-06`) | `DE` | T01 |
| `P02-M01-T03` | Enable full-disk encryption (LUKS) at install time | `DE-12` · `SC-009` · `P01-M02-T08` ruling | Encrypted root volume | Non-negotiable given `DE-12`. Verify with `lsblk -o NAME,FSTYPE,MOUNTPOINT` showing `crypto_LUKS` | `SL` | T02 |
| `P02-M01-T04` | Install the system package set — **the single most common first-hour failure is a missing build dependency** | `BE-001` §3.4 | Packages installed (see block below) | `dpkg -l` confirms every package | `DE` | T02 |
| `P02-M01-T05` | Install the **Bengali font set** — `fonts-noto`, `fonts-noto-bengali`, `fonts-lohit-beng-bengali` | `BE-001` §3.4 · `TR-07` | Fonts installed | **`TR-07` — "Bengali treated as a font setting" is a named programme failure mode.** A developer whose machine cannot render Bengali will not see a shaping defect that reaches a Mushak 6.3 invoice | `LL` | T04 |
| `P02-M01-T06` | Install **Docker Engine 24+ and Compose v2**, add the user to the `docker` group | `BE-001` §4 · `BE-001-D-02` | Working Docker | `docker compose version` reports v2.x. Docker is a **hard prerequisite** | `DE` | T02 |
| `P02-M01-T07` | Install **git 2.40 or later** — required, not preferred | `BE-001` §4 · `BE-004` §5 | git >= 2.40 | `BE-004` uses **subtrees for eighteen OCA repositories and partial clone** for the size budget; older versions handle both poorly | `DE` | T02 |
| `P02-M01-T08` | Install Odoo's **patched-Qt `wkhtmltopdf`**, not the distribution build | `BE-001` §9.2 | Patched `wkhtmltopdf` | The distribution build renders reports blank or unstyled. `make doctor` check 10 catches it, but installing the right one first is cheaper | `DE` | T04 |
| `P02-M01-T09` | Install Google Chrome or Chromium **stable** with DevTools, plus Firefox as a second engine | `UX-005` accessibility testing · `QA-008` | Two browsers installed | Portal work is verified in two engines. Bengali conjunct shaping differs between them | `FE` | T02 |
| `P02-M01-T10` | Verify no host PostgreSQL, Redis or MinIO is running — **nothing but Odoo and the language toolchains lives on the host** | `BE-001` `DE-01` | Clean port map | `ss -ltnp \| grep -E ':(5432\|6379\|9000)'` returns nothing. A host PostgreSQL causes `port is already allocated` and silent version drift | `DE` | T06 |

### System package set — run verbatim

```bash
# Ubuntu 22.04 / 24.04 — BE-001 §3.4
sudo apt update && sudo apt install -y \
  build-essential git curl \
  python3.12 python3.12-dev python3.12-venv \
  libpq-dev libxml2-dev libxslt1-dev libjpeg-dev libldap2-dev libsasl2-dev \
  libssl-dev libffi-dev zlib1g-dev \
  postgresql-client-17 \
  wkhtmltopdf \
  fonts-noto fonts-noto-bengali fonts-lohit-beng-bengali
```

| Package group | Why it is here |
|---|---|
| `libxml2-dev`, `libxslt1-dev`, `libsasl2-dev`, `libldap2-dev` | Odoo's `lxml` and `python-ldap` build dependencies. **Missing these is the single most common first-hour failure** |
| `libpq-dev`, `postgresql-client-17` | `psycopg2` build; `psql` client against the containerised server |
| `wkhtmltopdf` | Odoo's PDF renderer — replace with the patched-Qt build (`T08`) |
| **Bengali fonts** | `TR-07`. Non-negotiable |

---

## `P02-M02` — Toolchain installation and pinning

**Rule: nothing is installed at "latest". Every version comes from `tooling/versions.lock` (`BE-007` `LX-03`).**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P02-M02-T01` | Install **`uv`** — the Python toolchain manager | `BE-001` §4 | `uv` on PATH | `curl -LsSf https://astral.sh/uv/install.sh \| sh` · pinned by `.python-version` and `uv.lock` | `DE` | — |
| `P02-M02-T02` | Install **`nvm`**, then Node **22 LTS**, then **`pnpm`** | `BE-001` §4 · `AGENTS.md` inheritance · **`CR-P01M02-04` (Node 20 EOL)** | Node 22 + pnpm | `nvm install` reads `.nvmrc`. Pinned by `.nvmrc` and `pnpm-lock.yaml`. **Amended by `CR-P01M02-04`: Node 20 LTS reached end of life 30 April 2026 (verified 2026-10-01, first version-currency record) — the pin is Node 22 LTS (Payload 3.73's ≥ 20.9 floor is satisfied). Node 22 EOL 2027-04-30 is a standing watch item; Node 24 is the Active LTS.** The inherited `AGENTS.md` carries the same stale Node 20 pin — the CR covers it | `DE` | — |
| `P02-M02-T03` | Install **`fvm`**, then Flutter at the pinned version, and **read the 3.44 migration notes before pinning** | `BE-001` §4 · `D-027` · Flutter 3.44 release notes | Flutter via fvm | `fvm install` reads `.fvmrc`. Pinned by `.fvmrc` and `pubspec.lock`. **Skip only if `D-027` rules against Flutter — which `AR-010` and `UX-001` both argue against.** ⚠ **Flutter 3.44 (May 2026, Dart 3.12) moves Material and Cupertino out of the core SDK into standalone packages and makes Impeller the default renderer on Android with Skia removed.** Four applications and the shared `fix_ui` package are affected; pin deliberately, not by taking the newest | `MB` | `P01-M02-T07` |
| `P02-M02-T04` | Install the **Go toolchain** for the Go services (telemetry collector) | `BE-001` §4 · `BE-004` §4 `services/` | Go installed | Pinned by the `go.mod` toolchain directive | `BE` | — |
| `P02-M02-T05` | Create `tooling/versions.lock` as the single source of every pinned version and container digest | `BE-007` `LX-03` · `BE-001` §4 | `versions.lock` | **`DE-06`: image tags are pinned by digest. `:latest` appears nowhere** | `DE` | T01–T04 |
| `P02-M02-T06` | Confirm Python **3.12.x** exactly, and that `python3.12-venv` is present | `BE-001` §3.4 | Version confirmed | `python3.12 --version` | `DE` | T01 |
| `P02-M02-T07` | Configure `git` for the estate: `core.autocrlf=false`, `.gitattributes` line endings, LFS patterns, `linguist` overrides | `BE-004` §4 · `BE-002` `XS-01` | git config + `.gitattributes` | **`core.autocrlf` is `false`, not `true`** | `DE` | `P02-M01-T07` |
| `P02-M02-T08` | Configure git identity and GPG or SSH commit signing | `BE-003` §3.3 branch protection | Signed commits | Signed commits are a branch-protection precondition | `DE` | T07 |
| `P02-M02-T09` | Authenticate the GitHub CLI (`gh`) and confirm repository access | `BE-003` · `PE-004` §11 | `gh auth status` clean | Needed for PR flow and CI artefact inspection | `DE` | T07 |
| `P02-M02-T10` | Record the toolchain in `docs/guides/toolchain.md` so a new joiner reproduces it exactly | `BE-001` `DE-21` | Toolchain guide | **`DE-21`: the setup time budget is an onboarding SLA, measured per joiner and reported at the wave gate** | `DE` | T05 |

---

## `P02-M03` — Repository initialisation

**`BE-004` §13. The repository does not exist. This is day 0.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P02-M03-T01` | Read `BE-004` in full before creating anything | `BE-004` §1–§13 | Reading record | *"A monorepo without a layout is not a decision; it is a deferral. The first developer to commit decides where `cd_service_order` lives"* | `CA` | — |
| `P02-M03-T02` | Create the single repository **`1000fix-erp`** on the Company-controlled host | `BE-004` §3.1 `REPO-01` | Repository created | **There is exactly one ERP repository.** A second requires an `AR-004` ADR and a `D-nnn` decision | `DE` | T01 |
| `P02-M03-T03` | Create the full top-level tree exactly as `BE-004` §4 specifies | `BE-004` §4 | Directory tree (see block below) | Depth is the depth at which placement is unambiguous. **Directories marked generated are not hand-edited** | `DE` | T02 |
| `P02-M03-T04` | Commit the root files: `README.md`, `AGENTS.md`, `CODEOWNERS`, `LICENSE` (LGPL-3), `.gitattributes`, `.gitignore`, `.editorconfig`, `.pre-commit-config.yaml` | `BE-004` §4 · `AR-007` §3.3 | Root file set | `LICENSE` is LGPL-3 per `AR-007` §3.3 | `DE` | T03 |
| `P02-M03-T05` | Configure **branch protection** on `main` and `develop`: required reviews, required status checks, signed commits, linear history, no force-push | `BE-003` §3.3 | Protection rules active | Configure **before** the first feature branch, not after | `DE` | T02, `P02-M02-T08` |
| `P02-M03-T06` | Establish the branch model: `main` <- `release/*` <- `develop` <- `feature/*` \| `fix/*`; `hotfix/*` from `main` | `BE-003` §4.2 | Branch model documented and enforced | `EP-01` | `EL` | T05 |
| `P02-M03-T07` | Establish the commit convention `<type>(<scope>): <subject>` with **`<scope>` = the `CD-<UNIT>-<nn>`**, enforced by a commit-msg hook | `BE-003` §5.1 · `BE-005` `CDR-08` | commit-msg hook | An identifier not in `BE-005` §6 must not appear in a commit scope | `EL` | T04 |
| `P02-M03-T08` | Generate `CODEOWNERS` from `BE-005` so review routes to the owning squad automatically | `BE-004` §8 · `BE-005` §6 | Generated `CODEOWNERS` | Generated, never hand-edited | `DE` | T04, `P01-M05-T05` |
| `P02-M03-T09` | Commit the PR template requiring: what and why, CD item, requirement/rule, how verified, risk class, screenshots or output | `BE-003` §7.2 | `.github/PULL_REQUEST_TEMPLATE.md` | `EP-03` | `EL` | T04 |
| `P02-M03-T10` | Tag `v0.0.0` and record what the first tag means | `BE-003` §3.2 | Initial tag | Two version schemes coexist: module `19.0.x.y.z` and release SemVer. Both are correct — `BE-003` §8.1 | `DE` | T04 |

### The tree — create it exactly

```
1000fix-erp/
├── README.md              ← how to get running in one page; points at BE-001
├── AGENTS.md              ← contributor conventions for THIS repository
├── CODEOWNERS             ← generated from BE-005
├── LICENSE                ← LGPL-3
├── .gitattributes  .gitignore  .editorconfig  .pre-commit-config.yaml
│
├── vendor/                ← THIRD-PARTY CODE. Read-only to product developers
│   ├── odoo/              ← git submodule, pinned commit on branch 19.0
│   └── oca/               ← git subtrees, one directory per OCA repository (18)
│
├── addons/                ← ALL custom Odoo modules — 270 of 331 CD items
│   ├── platform/          ← AR-007 layer 3. Depended on; never depends on layer 4
│   │   ├── cd_event_outbox/     cd_rbac_ext/     cd_entity_config/
│   │   └── cd_party_master/     …
│   └── domain/            ← AR-007 layer 4, one subdirectory per category
│       ├── a_service_delivery/  b_customer_engagement/  c_commercial/
│       ├── d_circular/          e_supply_chain/         f_asset_facilities/
│       ├── g_finance/           h_people/               i_governance/
│       └── j_data_analytics/    k_platform/
│
├── services/              ← standalone services — 33 CD items + the service half of 90
│   ├── dispatch-scoring/       ← Python / FastAPI
│   ├── pricing-engine/  ml-gateway/
│   ├── telemetry-collector/    ← Go
│   └── notification-dispatcher/ ← Node.js
│
├── apps/                  ← end-user applications — 14 portal CD items
│   ├── mobile/            ← technician/  rider/  auditor/  customer/   (Flutter)
│   └── web/               ← customer/ corporate/ analytics/ seller/ brand/
│                             agent-console/ partner/          (Next.js)
│
├── libs/                  ← shared, versioned, cross-stack libraries
│   ├── py/                ← fix_events/  fix_residency/  fix_testing/
│   ├── ts/                ← api-client/  ui/  i18n/
│   └── dart/              ← fix_offline/  fix_ui/
│
├── contracts/             ← the interface surface, versioned independently of code
│   ├── openapi/           ← one file per API-exposing CD item
│   ├── events/            ← event schemas; the IN-003 catalogue's machine form
│   └── portal/            ← the CON-03 contract; PS-11 tests run against it
│
├── db/                    ← migrations/ (TimescaleDB, ClickHouse)  seeds/ (synthetic only)
├── infra/                 ← compose/  k3s/  terraform/  odoo-conf/
├── tooling/               ← cd-register.yaml  fitness/  generators/  scripts/  versions.lock
├── docs/                  ← adr/  runbooks/  guides/
└── .github/               ← workflows/  PULL_REQUEST_TEMPLATE.md  ISSUE_TEMPLATE/
```

| Rule | Provision |
|---|---|
| `libs/py/fix_events/` | **The event client. `FF-28` forbids direct bus clients** anywhere else |
| `libs/py/fix_residency/` | **The ONLY client of the residency service. `FF-09`** |
| `libs/dart/fix_offline/` | **The ONE offline engine (`ADR-024`), shared by three applications** |
| `vendor/` | **Read-only to product developers.** `AS-05` depends structurally on third-party code living somewhere a developer *cannot* casually edit |

---

## `P02-M04` — Third-party vendoring: Odoo submodule and 18 OCA subtrees

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P02-M04-T01` | Add **`vendor/odoo` as a git submodule** pinned to an exact commit on branch `19.0` | `BE-004` §5 · TSS §18.1 | Submodule at a pinned commit | **Cloning Odoo elsewhere is a defect** — the pinned commit is the version this repository builds against | `DE` | `P02-M03-T03` |
| `P02-M04-T02` | Vendor the **18 OCA repositories as git subtrees**, whole, retaining their own structure and `README.rst` | `BE-004` §5.3 | 18 subtree directories | **Subtrees, not submodules or pip packages** — so a local v19 migration is a normal commit, reviewable and contributable upstream | `DE` | T01 |
| `P02-M04-T03` | Vendor: `field-service`, `helpdesk`, `management-system`, `operating-unit`, `hr`, `payroll`, `dms`, `server-tools`, `web` | `BE-004` §4 · TSS §5 | 9 subtrees | Cross-check each against the `W0-01` migration assessment | `DE` | T02 |
| `P02-M04-T04` | Vendor: `account-financial-tools`, `account-financial-reporting`, `reporting-engine`, `mis-builder` | `BE-004` §4 | 4 subtrees | Finance layer, consumed from Phase 6 | `DE` | T02 |
| `P02-M04-T05` | Vendor: `stock-logistics-workflow`, `stock-logistics-barcode`, `stock-logistics-warehouse`, `purchase-workflow`, `partner-contact`, `contract`, `l10n-bangladesh` | `BE-004` §4 | 7 subtrees (total 18 with `l10n-bangladesh`) | `l10n-bangladesh` is the localisation base for `M51` and `M65` | `DE` | T02 |
| `P02-M04-T06` | Record every subtree's pinned commit in `versions.lock` | `BE-007` · `PE-004` `OD-06` | Pinned OCA commits | **`OD-06`: the Odoo submodule pin and OCA subtree commits are verified against `versions.lock` in CI** | `DE` | T02, `P02-M02-T05` |
| `P02-M04-T07` | Create `FORKS.yaml` — empty, with a header explaining that an entry requires Design Authority approval | `AS-05` · `BE-004` · `AR-007` §5.4 · `FF-03` | `FORKS.yaml` | **`OD-05`: no OCA fork without a `FORKS.yaml` entry.** The file exists from day 0 so the check has something to read | `CA` | T02 |
| `P02-M04-T08` | Implement `tooling/scripts/check-vendor-clean.sh` — **`FF-03`**, run pre-commit and in CI | `BE-002` §9 · `FF-03` | Vendor-clean check | `git status` must be clean under `vendor/` unless a `FORKS.yaml` entry authorises the change | `DE` | T07 |
| `P02-M04-T09` | Load the `W0-01` OCA migration status matrix into the repository as `docs/guides/oca-v19-status.md` | `P01-M04-T07` output | Status matrix in-repo | Developers must be able to see, per module, whether v19 support is real or assumed | `SA` | T02, `P01-M04-T07` |
| `P02-M04-T10` | Measure the clone-time and repository-size budget; enable partial clone if the budget is exceeded | `BE-004` §11 | Measured budget | The clone with submodule and subtrees is **20–40 minutes** — the largest single item in the onboarding budget | `DE` | T02 |

---

## `P02-M05` — The local supporting stack

**`DE-01`…`DE-09`. Containers for everything except Odoo and the language toolchains.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P02-M05-T01` | Author `infra/compose/docker-compose.yml` with **profiles**, not one monolithic stack | `BE-001` §5.1–§5.3 | Compose file | Fifteen Wave 1 components is too many to start on a laptop by default; starting none means discovering integration failures late | `DE` | `P02-M03-T03` |
| `P02-M05-T02` | Define the **`core`** profile: PostgreSQL 17, **Redis 7.2.x (last BSD-3 line) or Valkey — pending `D-031`**, **the object store chosen by `D-028`**, Mailpit — **~2 GB, the default** | `BE-001` §5.2 · **§0.7.3 `D-028`** · **`D-031` (licence currency)** | `core` profile | Enough to build and test any Odoo module. **Do not pin MinIO: `minio/minio` was archived 25 April 2026 and ships no community binaries.** Pin the object store selected by `D-028` (**Ceph Object Storage**), matching the production deployment. **Redis amendment (finding F-2, 2026-10-01): "Redis 7.x = BSD-3" holds only for ≤ 7.2 — 7.4+ is RSALv2/SSPL and 8.x adds AGPLv3. No Redis 7.4+/8.x image may be pinned until `D-031` is taken (pin 7.2.x, or adopt Valkey, the Linux Foundation BSD-3 fork).** The local image must match `prod`, or `local` diverges on day one | `DE` | T01, `P01-M02-T10` |
| `P02-M05-T03` | Define **`auth`** (+ Keycloak 26, PgBouncer, ~3.5 GB) and **`integration`** (+ Kong, Apache Airflow, Novu, ~5 GB) | `BE-001` §5.2 | 2 profiles | `auth` for `cd_rbac_ext`, SSO, roles, record rules. `integration` for `M28`, webhooks, orchestration, notifications | `DE` | T02 |
| `P02-M05-T04` | Define **`field`** (+ Traccar, OSRM, VROOM, ~7 GB), **`observability`** (+ Prometheus, Grafana, Loki, Tempo, ~8 GB), **`full`** (~10–12 GB) | `BE-001` §5.2 | 3 profiles | **`full` is for integration testing, not a daily working configuration** | `DE` | T03 |
| `P02-M05-T05` | Apply `DE-03`, `DE-04`, `DE-05`, `DE-06` to every service | `BE-001` §5.1 | Compliant Compose file | **`DE-03`** every service declares a health check and `make up` does not return until all are healthy · **`DE-04`** every port binds `127.0.0.1`, never `0.0.0.0` · **`DE-05`** named volumes only · **`DE-06`** images pinned by digest | `DE` | T04 |
| `P02-M05-T06` | Configure PostgreSQL with `--encoding=UTF8 --locale=en_US.UTF-8` and ICU | `BE-001` §5.3 | Correct locale | **The database must not be created in a C locale or ordering breaks.** Bengali collation is a presentation concern (`XS-05`), the locale is not | `DA` | T02 |
| `P02-M05-T07` | Configure **Mailpit as the only mail sink** — `SMTP_HOST=127.0.0.1`, `SMTP_PORT=1025` | `BE-001` `DE-07` | Mailpit at `127.0.0.1:8025` | **`DE-07`: no development environment sends real mail.** 1000FiX operates a customer hotline and a notification estate; **one misdirected batch is a reputational incident** | `DE` | T02 |
| `P02-M05-T08` | Commit the **synthetic Keycloak realm export** — generated from the role register, never exported from a real environment | `BE-001` `DE-09` | `keycloak/realm-1000fix-dev.json` | `DE-09`. Synthetic users only | `SL` | T03 |
| `P02-M05-T09` | Stand up the **local residency service** returning **synthetic values only**, incapable of connecting to a real resident store | `BE-001` `DE-14` · `FF-09` | Local residency stub at `127.0.0.1:8100` | **`FF-09` is satisfied locally by the impossibility of a real value existing, not by a check** | `SL` | T02, `P01-M06-T04` |
| `P02-M05-T10` | Implement the Make targets: `make up [PROFILE=…]`, `make down`, `make reset` | `BE-001` §5.2 | Makefile targets | `make reset` = `down -v`, recreate, reseed. **`DE-05`: a `docker compose down -v` is a complete, intentional reset and nothing else destroys data** | `DE` | T05 |

---

## `P02-M06` — Odoo local runtime, configuration and seed data

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P02-M06-T01` | Implement **`make bootstrap`**: toolchains, `uv sync`, `pnpm install`, `pre-commit install`, `addons_path` generation | `BE-001` §6.1 | `make bootstrap` | One command replaces eight manual sections. Budget: **15–25 minutes** | `DE` | `P02-M04-T02` |
| `P02-M06-T02` | Implement **`make odoo-conf`** — `odoo.conf` is **generated, never hand-written** | `BE-001` §6.2 · `BE-004` §6 · `REPO-15` | Generated `infra/odoo-conf/local.conf` | `addons_path` is **30+ entries and drifts the day a category is added**. The layer order is normative | `DE` | T01 |
| `P02-M06-T03` | Set `workers = 0` in the local configuration | `BE-001` §6.2 | Threaded-mode config | **`workers = 0` is not a performance setting.** With workers > 0 Odoo forks, and a debugger attached to the parent never stops in the child | `OD` | T02 |
| `P02-M06-T04` | Set `dev = all`, `limit_time_cpu = 3600`, `limit_time_real = 3600`, `log_handler = odoo.addons.cd_:DEBUG`, `list_db = True`, `without_demo = False` | `BE-001` §6.2 | Complete local config | Generous timeouts so a breakpoint does not kill the request. `list_db = True` is **local only** | `OD` | T03 |
| `P02-M06-T05` | Commit `.env.example` complete; git-ignore `.env` | `BE-001` §6.4 `DE-10` | `.env.example` | **A new variable added to code and not to the example is a broken onboarding for the next joiner** | `DE` | T02 |
| `P02-M06-T06` | Implement **`DE-11`** — every service asserts `FIX_ENV=local` at startup and **refuses to start** if a non-local endpoint is configured alongside it | `BE-001` §6.4 `DE-11` | Startup assertion in every service | **A local process must not be able to reach a production database because someone pasted a connection string** | `SL` | T05 |
| `P02-M06-T07` | Implement `make db-create`, `make odoo-init`, `make odoo-install-wave1`, `make run` | `BE-001` §6.3 | 4 Make targets | `make run` serves `http://127.0.0.1:8069`. Budget: **15–30 minutes** for init + Wave 1 install | `DE` | T02 |
| `P02-M06-T08` | Implement **`make seed`** — deterministic synthetic data from a fixed random seed, in Bengali and English | `BE-001` §6.5–§6.6 `DE-13` | `db/seeds/` + `make seed` | 5 branches · ~25 users across the role register · 200 customers · 500 devices · 300 service orders across every state · 400 products · 60 SLAs | `DA` | T07 |
| `P02-M06-T09` | Apply **`DE-16`** — seed data covers **every state of every state machine**, not only the happy path | `BE-001` `DE-16` | State-complete seed data | **A state that seed data cannot reach is a state nobody tests** | `QA` | T08 |
| `P02-M06-T10` | Apply **`DE-17`** — seed data is **Bengali-first** | `BE-001` `DE-17` | Bengali-primary seed data | **An interface that has only ever been seen with English data hides its layout defects until UAT** | `LL` | T08 |

### The rule with no exceptions

| # | Rule |
|---|---|
| **`DE-12`** | **A developer workstation never holds production data, masked or otherwise.** `local` sits below `staging` on the ladder and `staging` is already masked; the rule here is not "mask it", it is **"never bring it"** |
| **`DE-15`** | **A production or staging database dump on a developer machine is a security incident**, reported under `SC-009` — not a shortcut |

---

## `P02-M07` — VS Code, debugging, browser preview and DevTools

**Everything below is committed at `.vscode/` so configuration is shared rather than rediscovered.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P02-M07-T01` | Install VS Code and commit `.vscode/extensions.json` with the required extension set | `BE-001` §8.1 | `.vscode/extensions.json` | VS Code prompts every developer to install the workspace-recommended set on first open | `DE` | `P02-M03-T03` |
| `P02-M07-T02` | Install the **required** extensions (§2.7 table below) | `BE-001` §8.1 | Extensions installed | Verify with `code --list-extensions` against the committed list | `DE` | T01 |
| `P02-M07-T03` | Commit `.vscode/launch.json` with the two debug configurations: **Odoo (local)** and **Odoo test — current file** | `BE-001` §8.1 | `launch.json` | Both use `"justMyCode": false` | `OD` | T01 |
| `P02-M07-T04` | Commit `.vscode/settings.json`: Ruff as Python formatter and linter, ESLint + Prettier for TS, `dart analyze` for Dart, format-on-save, `files.eol = "\n"` | `BE-002` §4.6, §5.3, §6.2 | `settings.json` | Editor behaviour must match what CI enforces, or the two disagree daily | `EL` | T01 |
| `P02-M07-T05` | *(Optional)* Stand up **Storybook on Vite** for `libs/ts/ui` — the shared component library across the six Next.js portals | `UX-001` §3.2 `DSY-01` · `BE-004` §4 `libs/ts/ui` | Storybook host | **The only place Vite appears in this programme, and it is a devDependency that ships nothing.** Turbopack remains the Next.js bundler | `UX` | T01 |
| `P02-M07-T06` | Configure **browser preview**: Next.js dev server on `127.0.0.1:3000`, Odoo on `127.0.0.1:8069`, Storybook on `127.0.0.1:6006`, all bound to loopback | `BE-001` `DE-04` · `PE-004` | Running dev servers | `EP-12` — loopback only | `FE` | T01 |
| `P02-M07-T07` | Configure **Chrome DevTools workflow**: Lighthouse for the **< 400 KB bundle budget** on critical customer paths, Network throttling to 3G, Performance profiling, Application panel for the PWA offline shell | `NFR` bundle budget · `URD` §20 offline · portal `P01` design requirements | DevTools workflow guide in `docs/guides/` | **Portal `P01`'s booking path must be under 400 KB on 3G.** This is a CI gate (`pre-merge` stage 11), so it must be checkable locally first | `FE` | T06 |
| `P02-M07-T08` | Install and configure the **axe DevTools** browser extension for WCAG 2.2 AA spot-checking | `UX-005` · `QA-008` · CI stage 12 | axe extension configured | Automated scans find a **minority** of WCAG failures; `QA-008` §6 resources the manual half | `UX` | T06 |
| `P02-M07-T09` | Configure **Flutter DevTools** and at least one Android emulator or physical device profile | `AR-010` · `UX-006` · `D-027` | Flutter debugging working | `TAF-58` records that a device lab is **unfunded** (`Q-04`). Emulator coverage pre-merge; real-device coverage at `gate` only, **and the reduction is declared, not silent** | `MB` | `P02-M02-T03` |
| `P02-M07-T10` | Verify **hot reload** across all four layers | `BE-001` §8.2 | Hot reload confirmed | Python and XML via `--dev=all` (no restart) · manifest/new model/new field via `make upgrade MODULE=cd_x` (**restart required**) · OWL assets via hard refresh · Next.js via Turbopack HMR · Flutter hot reload | `EL` | T03, T06 |

### The required VS Code extension set

| Extension | Identifier | Purpose | Required for |
|---|---|---|---|
| Python | `ms-python.python` | Python language support, debugging | All Odoo and service work |
| Pylance | `ms-python.vscode-pylance` | Type checking, IntelliSense | All Python |
| **Ruff** | `charliermarsh.ruff` | `BE-002` `PYS-01` formatting and linting **in-editor** | All Python |
| Docker | `ms-azuretools.vscode-docker` | Compose stack management | Everyone |
| **XML** | `redhat.vscode-xml` | **Odoo view XML with schema validation** | All Odoo view work |
| Flutter | `dart-code.flutter` | `apps/mobile/**` | Mobile |
| Dart | `dart-code.dart-code` | Installed automatically with Flutter | Mobile |
| ESLint | `dbaeumer.vscode-eslint` | `apps/web/**`, `libs/ts/**` | Frontend |
| Prettier | `esbenp.prettier-vscode` | TS/TSX/JSON/CSS formatting | Frontend |
| **GitLens** | `eamodio.gitlens` | Review and blame across an 18-subtree vendored estate | Everyone |
| **REST Client** | `humao.rest-client` | `contracts/openapi` exercised from `.http` files **in-repo** | API and integration work |

**Strongly recommended, added by this roadmap for this estate:**

| Extension | Identifier | Why this programme needs it |
|---|---|---|
| YAML | `redhat.vscode-yaml` | `docker-compose.yml`, `cd-register.yaml`, `.github/workflows/**`, event schemas |
| Even Better TOML | `tamasfe.even-better-toml` | `pyproject.toml` — Ruff and mypy configuration |
| Error Lens | `usernamehw.errorlens` | **Inline diagnostics.** Surfaces lint and type errors at the line rather than in a panel — the single highest-value addition for a team running `mypy --strict` |
| Todo Tree | `Gruntfuggly.todo-tree` | `BE-009` technical-debt register — a `TODO` must resolve to a `DBT-nnn` |
| Coverage Gutters | `ryanluker.vscode-coverage-gutters` | **`DoD-03` is 80% coverage and 100% on financial and tax paths.** Seeing uncovered lines in the editor is what makes that achievable |
| markdownlint | `DavidAnson.vscode-markdownlint` | 800-file documentation estate; `runbook.md` and `README.md` are mandatory per module |
| Mermaid preview | `bierner.markdown-mermaid` | `AR-*` and `IN-*` diagrams |
| Bengali IME support | *(system-level)* | **`TR-07`.** A developer who cannot type Bengali cannot test a Bengali form |
| GitHub Actions | `github.vscode-github-actions` | `PE-004` pipeline authoring |
| Playwright | `ms-playwright.playwright` | `L6` end-to-end journeys — 15 critical journeys, run nightly |

> **Do not install** a second Python formatter (Black, autopep8) alongside Ruff, a second linter
> (Flake8, Pylint standalone) or a REST client that duplicates `humao.rest-client`. Two formatters
> fighting over the same file produces a diff war that costs more than either saves.

### `.vscode/launch.json` — commit exactly this

```jsonc
{ "version": "0.2.0", "configurations": [
  { "name": "Odoo (local)",
    "type": "debugpy", "request": "launch",
    "program": "${workspaceFolder}/vendor/odoo/odoo-bin",
    "args": ["-c", "infra/odoo-conf/local.conf", "-d", "fix_dev"],
    "console": "integratedTerminal", "justMyCode": false },
  { "name": "Odoo test — current file",
    "type": "debugpy", "request": "launch",
    "program": "${workspaceFolder}/vendor/odoo/odoo-bin",
    "args": ["-c", "infra/odoo-conf/local.conf", "-d", "fix_test",
             "--test-enable", "--test-tags", "${fileBasenameNoExtension}",
             "--stop-after-init"],
    "console": "integratedTerminal", "justMyCode": false } ]}
```

> **`justMyCode: false` matters here.** Most debugging in an Odoo programme happens **inside
> `vendor/odoo` or an OCA module**, understanding what the framework does before extending it —
> which is precisely the reading `AS-05` depends on.

---

## `P02-M08` — Quality gates, error checking and monitoring

**This milestone is where "error checking and monitoring" is installed. It has two halves: local error detection, and runtime observability.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P02-M08-T01` | Commit `.pre-commit-config.yaml` running **the same tools CI runs** | `BE-002` §9 · `REPO-20` | Pre-commit config (block below) | **`XS-19`: pre-commit is installed by `make bootstrap` and is not optional.** CI re-runs every hook, so bypassing locally only moves the failure later | `EL` | `P02-M03-T04` |
| `P02-M08-T02` | Configure **Ruff** (format + lint) and **`mypy --strict`** for Python | `BE-002` §4.1–§4.2, §4.6 | `pyproject.toml` | Type checking is `PYS-07`, `PYS-10`, `PYS-11` | `EL` | T01 |
| `P02-M08-T03` | Configure **`pylint-odoo`** over `addons/` — manifest completeness, `sql-injection` (`SQL-02`), `translation-required` (`XS-08`), compute-method correctness | `BE-002` §4.6 | pylint-odoo in pre-commit and CI | Catches the Odoo-specific defect classes generic Python linting cannot | `OD` | T01 |
| `P02-M08-T04` | Configure **`gitleaks` over full history**, and stand up the **restricted-licence gate (`D-030`)** classifying all 24 L4 systems | `BE-002` `XS-06` · `SC-005` `G-01` · `BE-007` · TSS §18.5 · **§0.7.3** | gitleaks hook + CI stage + licence classification register | **`SE-01`: secret scanning runs pre-commit AND in CI.** And TSS §18.5 says **AGPL, BSL, TSL and fair-code components require architecture approval** — verified 2026-08-19, **four are already in the stack and none has been approved**: MinIO (AGPL-3, archived, replaced by Ceph), Apache Superset (AGPL-3, embedded in a portal), Apache Airflow (Apache-2.0), Apache Kafka (Apache-2.0) | `SL` | T01 |
| `P02-M08-T05` | Configure **ESLint (`--max-warnings=0`) + Prettier** for TypeScript, and **`dart analyze --fatal-infos`** for Dart | `BE-002` §5.3, §6.2 | TS and Dart gates | Zero warnings. A warning budget becomes a warning backlog | `FE` | T01 |
| `P02-M08-T06` | Implement `tooling/scripts/check-cd-id.py` — **`FF-16`**, validating **form and membership** against `cd-register.yaml` | `BE-005` §10 · `BE-002` §9 | CD identifier check | **A regex-only check passes `CD-M99-42`, which is well-formed and denotes nothing.** Enable as **Warning**, promote to **Blocking at `G1`** | `DE` | T01, `P01-M05-T05` |
| `P02-M08-T07` | Build the **Wave 1 fitness-function set** in `tooling/fitness/`: `FF-02`, `FF-03`, `FF-04`, `FF-06`, **`FF-09`**, `FF-19`, `FF-20`, `FF-21`, `FF-22`, `FF-23`, `FF-25`, `FF-30`, `FF-32`, `FF-37` | `AR-012` §10 | 14 blocking checks | **`FF-09` (residency) and `FF-03` (fork) must exist before the first line of code.** Both have effectively unrecoverable violations | `CA` | T01 |
| `P02-M08-T08` | Build `FF-13`, `FF-14`, `FF-27` as **Warning** with burn-down targets, and `FF-16`, `FF-26` as **built-but-disabled** | `AR-012` §5.2–§5.3, §10 | 5 further checks | **`FG-04`: a new fitness function is not enabled as blocking on the day it is written.** One wave in reporting mode, then blocking | `CA` | T07 |
| `P02-M08-T09` | Stand up the local **observability profile** — OpenTelemetry, Prometheus, Loki, Tempo, Grafana — and wire a single correlation id across every hop | `PE-008` · TSS §17 · `NFR-092` | `observability` Compose profile working | A developer must be able to see a trace locally before instrumenting for production | `DE` | `P02-M05-T04` |
| `P02-M08-T10` | Configure **result normalisation** (`RN-01`…`RN-04`): every stage emits one schema — suite, case, status, duration, artefact links, and **the identifier of the requirement or fitness function it verifies** | `PE-004` §5.7 | Normalised result schema + adapters | **`RN-04` is what turns specified fitness functions into a measurable estate property.** Without it, "the gates are enabled" is a claim nobody can verify | `QA` | T07 |

### `.pre-commit-config.yaml` — commit exactly this

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks: [ { id: ruff, args: [--fix] }, { id: ruff-format } ]      # PYS-01
  - repo: https://github.com/OCA/pylint-odoo
    hooks: [ { id: pylint-odoo, files: ^addons/ } ]
  - repo: https://github.com/gitleaks/gitleaks
    hooks: [ { id: gitleaks } ]                                      # XS-06
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - { id: end-of-file-fixer }
      - { id: mixed-line-ending, args: [--fix=lf] }                  # XS-01
      - { id: check-merge-conflict }
      - { id: check-added-large-files, args: [--maxkb=512] }         # REPO-30
  - repo: local
    hooks:
      - { id: eslint,   entry: pnpm -w exec eslint --max-warnings=0, types: [ts] }
      - { id: prettier, entry: pnpm -w exec prettier --write, types_or: [ts, tsx, json, css] }
      - { id: dart-analyze, entry: fvm dart analyze --fatal-infos, types: [dart] }
      - { id: no-vendor-edit, entry: tooling/scripts/check-vendor-clean.sh }   # FF-03
      - { id: cd-id-check,   entry: tooling/scripts/check-cd-id.py }           # FF-16
```

> **`XS-20`: `--no-verify` is permitted only on a `hotfix/*` branch, and the next commit on that
> branch must pass.**

### Where error checking actually happens — the four layers

| Layer | Tooling | Catches | Feedback time |
|---|---|---|---|
| **In-editor** | Ruff, Pylance, ESLint, `dart analyze`, **Error Lens**, Coverage Gutters | Syntax, types, style, uncovered lines | Instant |
| **Pre-commit** | The block above | Formatting, lint, secrets, vendor edits, CD identifiers | **< 30 s** |
| **Pre-merge CI** | 15 blocking stages (§2.9) | Model registry, unit, integration, contract, event, security, architecture, localisation, bundle, accessibility | **< 20 min** |
| **Runtime** | OpenTelemetry -> Prometheus + Loki + Tempo -> Grafana; Wazuh; Sentry-class error tracking | Errors, latency, saturation, security events, in every environment | Continuous |

> **Twenty-two `BE-002` rules are review-only, and four of them are the most consequential in the
> document** — `PYS-22` (`sudo()` justification), `PYS-20` (timeout, retry, fallback), `FL-03` (one
> offline engine) and `SQL-05` (two-release column lifecycle). **No tool catches these.** The review
> checklist exists so review spends its attention there rather than on formatting a tool has already
> fixed.

---

## `P02-M09` — CI/CD pipeline and the twelve environments

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P02-M09-T01` | Read `PE-004` in full, plus `PE-002` §4.2 (the twelve-environment ruling) and `PE-003` IaC standard | `PE-002`…`PE-005` | Reading record | The estate previously carried **two incompatible environment lists**. `PE-002-D-01` supersedes both | `DE` | — |
| `P02-M09-T02` | Implement **`PE-004-D-01` — build once, promote the artefact.** The same bytes reach production | `PE-004` §3.1 · `PE-002` `PA-01` | Artefact registry + promotion pipeline | Rebuild-per-environment means **the thing tested is not the thing deployed** | `DE` | T01 |
| `P02-M09-T03` | Implement the **five execution profiles**: `pre-commit` (<30 s), `pre-merge` (<20 min, blocks), `nightly` (<3 h), `release` (<4 h, blocks), `gate` (days, blocks) | `PE-004` §4.2 | 5 pipeline profiles | The budget is a **design constraint, not an aspiration** | `DE` | T02 |
| `P02-M09-T04` | Implement the **17 pipeline stages** (§2.9 table) | `PE-004` §5.1 | 17 stages, correctly profiled | Stages 2–12 and 15 block pre-merge; 13–14 block at `release`; 16–17 block at `gate` | `DE` | T03 |
| `P02-M09-T05` | Implement **`TAF-52`/`DB-01`…`DB-04`** — an **ephemeral PostgreSQL 17 per run**, seeded by **restoring a versioned snapshot artefact**, never by running a generator | `PE-004` §5.2 · `QA-004` | Per-run database | **`DB-02` is the difference between a 20-minute budget and a 40-minute one.** It also removes the commonest source of order-dependent test failure | `DE` | T04 |
| `P02-M09-T06` | Implement the **Odoo-specific stages** `OD-01`…`OD-06`: manifest validation, **installability into a clean database in dependency order**, upgradability from the previous release, `AR-007` conformance, `FORKS.yaml` check, submodule and subtree pin verification | `PE-004` §5.5 | 6 Odoo stages | **`OD-02`: a module that cannot install alone is not a module** | `OD` | T04 |
| `P02-M09-T07` | Stand up the **Pact broker** and the **schema registry** as pipeline services with an availability expectation | `PE-004` §5.3 `TAF-57` | 2 pipeline services | **`PS-01`: both fail closed, never open.** A pipeline that treats an unreachable verifier as a pass converts the two controls the estate relies on most into decoration | `IL` | T04 |
| `P02-M09-T08` | Implement `BG-01`…`BG-05` to hold the 20-minute budget: **affected-component selection computed from `AR-006`'s dependency graph**, sharding, layer placement, caching, per-gate measurement | `PE-004` §4.3 | Budget-holding mechanisms | **`PE-004-F-01`: with 18 cycles, a change inside a cycle marks every member as affected.** The largest cycles will be the slowest to merge into — a cost felt on **every pull request** | `DE` | T04 |
| `P02-M09-T09` | Provision the **twelve environments** per `PE-002` §4.2 | `PE-002` §5.1–§5.12 | 12 environments | `local` · `ci` · `dev` · `sit` · `uat` · `perf` · `staging` · `training` · `sandbox` · `migration-staging` · `prod` · `dr`. **`sit`, `uat` and `staging` are three environments and may not be merged before the `G4` gate** (`PE-002-D-02`) | `DE` | T02 |
| `P02-M09-T10` | Implement Vault secret management and the **expand/migrate/contract** three-release migration protocol | `PE-009` · `RL-002` §5 · `EP-05` | Vault + migration protocol | **Zero-downtime deployment requires forward-only, backward-compatible migrations: a release adds a column before code uses it and removes a column only after no code references it — three releases, never one** | `DE` | T02 |

### The 17 pipeline stages

| # | Stage | Checks | Profile | Blocks |
|:--:|---|---|---|:--:|
| 1 | Pre-commit | Format, lint, Odoo checks, **secret scan** | `pre-commit` | Local |
| 2 | Lint & type | Python, TypeScript, Dart; naming (`AS-04`) | `pre-merge` | Yes |
| 3 | **Model registry** | `AS-02` chatter mixins · `AS-03` company/OU fields · **`AS-14` residency and S3 classification** | `pre-merge` | Yes |
| 4 | Unit | **>= 80% coverage; 100% financial and tax** (`DoD-03`) | `pre-merge` | Yes |
| 5 | Integration | Module-to-module; external against **sandboxes** | `pre-merge` (affected) / `nightly` (full) | Yes |
| 6 | Contract | OpenAPI 3.1 validation; **pact verification**; `PS-11` portal contract test | `pre-merge` | Yes |
| 7 | Event | Producer/consumer schema compatibility; **`AS-08` outbox coverage**; idempotency | `pre-merge` | Yes |
| 8 | Security | SAST, dependency scan, container scan, **IaC scan** | `pre-merge` | Yes, on high/critical |
| 9 | Architecture | `AR-012` blocking fitness functions — `AS-01`, `AS-05`, `AS-09`, `AS-10` | `pre-merge` | Yes |
| 10 | Localisation | **Translation completeness at 100%** (`DoD-08`) | `pre-merge` | Yes |
| 11 | Bundle budget | Critical customer paths **< 400 KB** | `pre-merge` | Yes |
| 12 | Accessibility | axe-core on portal builds | `pre-merge` | Yes, on violations |
| 13 | Licence & SBOM | `BE-007` register check; SBOM generation | `release` | Yes |
| 14 | Build verification | Container build; **migration dry run against a production-sized clone** | `release` | Yes |
| 15 | Infrastructure | `PE-003` plan + policy when `infra/` changed | `pre-merge` | Yes |
| 16 | Performance | `PE-006` at **1.5x peak** (`DoD-14`) | `gate` | Yes |
| 17 | DR evidence | `PE-007` drill record within the wave | `gate` | Yes |

### The twelve environments

| # | Environment | Purpose | Data | Residency-classified data |
|:--:|---|---|---|---|
| 1 | `local` | Developer workstation, Docker Compose | **Generated synthetic only** | **Never — impossible by construction** |
| 2 | `ci` | **Ephemeral per run** | Versioned snapshot restore | Never |
| 3 | `dev` | Shared integration target for `develop` | Synthetic + anonymised sample | Never |
| 4 | `sit` | System integration test across real modules | Full `TS-002` set, **moving** | Never |
| 5 | `uat` | Business acceptance | Full `TS-002` set, **frozen for the cycle** | Never |
| 6 | `perf` | Performance at 1.5x peak | **Production-shaped volumes** | Never — masked |
| 7 | `staging` | Release-candidate rehearsal | **Production clone, masked** | **Never — masked** (`NFR-086c`) |
| 8 | `training` | Super-user and end-user training | Curated scenario data, resettable per cohort | Never |
| 9 | `sandbox` | External partner certification | **Synthetic only, externally reachable** | Never |
| 10 | `migration-staging` | **Production-class** migration rehearsal at production volume | Production-volume clone | Masked |
| 11 | `prod` | Live | Live | **Yes, in Z4 only** |
| 12 | `dr` | Warm standby, RPO <= 15 min, RTO <= 2 h | Streaming replica | Yes, Bangladesh-resident standby |

> **`NFR-086c` is absolute:** non-production environments never contain unmasked
> residency-classified data in any region. **Masking runs as part of the clone job, not as a
> subsequent step**, so an unmasked clone cannot exist even briefly.

---

## `P02-M10` — Verification, onboarding SLA and gate `G0b`

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P02-M10-T01` | Implement **`make doctor`** as a script with all 14 checks | `BE-001` §7.1 | `make doctor` | **A checklist a human reads is a checklist a human skips.** `DE-18`: exits non-zero on any failure and **prints the remedy, not only the symptom** | `DE` | `P02-M06-T07` |
| `P02-M10-T02` | Implement checks 1–5: host prerequisites at pinned versions · repository integrity (submodule pin, 18 subtrees, `vendor/` clean) · Compose health · database exists and is UTF-8 · `addons_path` regenerates identically | `BE-001` §7.1 | 5 checks | Check 2 is `FF-03`; check 5 is `REPO-15` | `DE` | T01 |
| `P02-M10-T03` | Implement checks 6–9: Odoo boots and serves `/web/login` with no ERROR · a scaffolded `cd_` module installs and uninstalls cleanly · `make test-smoke` green · `pre-commit run -a` green on a clean tree | `BE-001` §7.1 | 4 checks | Check 7 is `OD-02` locally | `DE` | T02 |
| `P02-M10-T04` | Implement **check 10 — Bengali rendering compared against a committed reference image**, not judged by eye | `BE-001` §7.1 · `TR-07` | Reference-image comparison | **The check that is usually skipped and is specific to this programme.** Comparing against a committed reference image is the only way an automated check catches a conjunct-shaping regression that would otherwise reach a Mushak 6.3 invoice | `LL` | T03 |
| `P02-M10-T05` | Implement checks 11–14: mail arrives in Mailpit and **no outbound SMTP is attempted** · **no table contains a value matching the residency-classified pattern set** · a breakpoint in a `cd_` model is hit from an HTTP request · editing a Python file and an XML view both take effect without restart | `BE-001` §7.1 | 4 checks | Check 12 is `DE-12` and `FF-09` enforced locally | `DE` | T03 |
| `P02-M10-T06` | Implement **`make test-smoke`** — under three minutes, one path end to end | `BE-001` §7.2 | Smoke test | Create a customer -> create a service order -> transition its state machine -> **assert the outbox emitted the declared events** -> **assert the record rules deny a user without the role** | `QA` | T03 |
| `P02-M10-T07` | Run **`make doctor` nightly in CI on a clean runner** | `BE-001` `DE-20` | Nightly job | **`DE-20`: the setup guide is tested, not trusted.** This is what keeps `BE-001` from going stale | `DE` | T05 |
| `P02-M10-T08` | Measure the onboarding SLA per joiner against the budget: **1.6–2.7 h on `core`, 1.9–3.1 h on `full`** | `BE-001` §7.3 `DE-21`, `DE-22` | Per-joiner measurement | **A joiner exceeding 4 hours on `core` triggers a defect against `BE-001`, not against the joiner.** Any step regularly exceeding its budget is automated or cached | `DE` | T07 |
| `P02-M10-T09` | Publish the troubleshooting register in-repo, **maintained by the person who solved the problem**, not by the document owner | `BE-001` §9 | `docs/guides/troubleshooting.md` | Seed it with the 13 known failures — missing `libxml2-dev`, stale `addons_path`, `workers > 0` killing breakpoints, unpatched `wkhtmltopdf`, missing Bengali fonts, port collisions, `/mnt/c/` slowness, `full`-profile OOM | `DE` | T01 |
| `P02-M10-T10` | **Gate `G0b`.** Design Authority signs: every developer's `make doctor` green; pipeline running with all blocking stages; 12 environments provisioned; `FF-03` and `FF-09` live | `GV-009` §4 | Signed `G0b` record | **`DE-19`: a developer does not begin work until `make doctor` is green.** Half a working environment produces defects that look like code defects and cost far more than the setup would have | `CA` | T01–T09 |

### `make doctor` — the 14 checks

| # | Check | Pass condition |
|:--:|---|---|
| 1 | Host prerequisites | Python 3.12.x, Node 20.x, `uv`, `fvm`, Docker Compose v2, git >= 2.40 — all at pinned versions |
| 2 | Repository integrity | Submodule at the pinned commit; all 18 subtrees present; `git status` clean under `vendor/` (`FF-03`) |
| 3 | Compose health | Every service in the active profile reporting healthy |
| 4 | Database | `fix_dev` exists, UTF-8, reachable |
| 5 | `addons_path` | Regenerates identically to the committed file (`REPO-15`) |
| 6 | Odoo boot | Starts, serves `/web/login`, logs no ERROR |
| 7 | Module install | A scaffolded `cd_` module installs and uninstalls cleanly |
| 8 | Test run | `make test-smoke` green |
| 9 | Quality gates | `pre-commit run -a` green on a clean tree |
| 10 | **Bengali rendering** | A QWeb report renders Bengali with correct conjunct shaping — **compared against a committed reference image** |
| 11 | Mail capture | A test mail arrives in Mailpit, and **no outbound SMTP connection is attempted** |
| 12 | **Data safety** | **No table contains a value matching the residency-classified pattern set** |
| 13 | Debugger | A breakpoint in a `cd_` model is hit from an HTTP request |
| 14 | Hot reload | Editing a Python file and an XML view both take effect without restart |

### The onboarding time budget — measured, not estimated

| Phase | `core` | `full` | Dominant cost |
|---|---:|---:|---|
| System packages and toolchains | 30–45 min | 30–45 min | Downloads |
| Clone with submodule and subtrees | **20–40 min** | 20–40 min | `vendor/` size |
| `make bootstrap` | 15–25 min | 15–25 min | `uv sync`, `pnpm install` |
| Image pulls | 5–10 min | **20–35 min** | Fifteen images |
| `db-create` + `odoo-init` + `install-wave1` | 15–30 min | 15–30 min | OCA module installation |
| `make seed` | 3–5 min | 3–5 min | |
| `make doctor` | 5 min | 8 min | |
| **Total** | **1.6–2.7 h** | **1.9–3.1 h** | |

---
---

# PHASE 3
## PLATFORM BOOTSTRAP & SHARED KERNEL

### Wave 1a · Months 1–2 · 8.7 weeks · Sprints 1–5 · Gate `G1a`

---

## 3.0 Phase charter

| | |
|---|---|
| **Purpose** | Build tier **T0** (the platform triad) and tier **T1** (the shared kernel), so that every subsequent module has an identity, an event bus, a configuration model and six modelled concepts to consume rather than re-invent |
| **Tiers** | `T0` = `{M28, M29, M30}` as **one co-designed increment**. `T1` = `M33`, `M37`, `M64-core`, `M24-core`, `M21-core` |
| **Modules** | `M28` IPF · `M29` SEC · `M30` ADM · `M33` CPM · `M37` CAT · `M64-core` MDM · `M24-core` DMS · `M21-core` HCM |
| **Scope movements applied** | `MV-01` (employee master), `MV-02` (`fix.document` kernel), `MV-04` (MDM core) — all land here |
| **Surface** | **`P03` Admin Operations Portal only.** It is the only surface available in Wave 1 and every W1 capability is exercised through it |
| **Effort** | ~120 PW against ~20 effective PW at 3 build FTE — **the capacity gap is real and is reported weekly** |
| **Entry** | `G0b` passed · `D-013` taken · `BE-005` issued · `AR-006` accepted with `MV-01`…`MV-05` |
| **Exit** | `G1a` — §3.10 |

> **Why `M28`, `M29` and `M30` are built as one increment and not three.** `AR-006` §4.1 classifies
> `M28 <-> M29`, `M28 <-> M30` and `M29 <-> M30` as **legitimate platform co-design pairs**: the
> gateway needs identity, identity publishes through the gateway, and configuration and integration
> are mutually bootstrapping. Attempting to sequence them produces three half-modules that cannot be
> tested. One squad, one increment, one gate.

> **`M29` has an in-degree of 53 — 79% of the estate depends on it.** Nothing about `M29` is
> descopable, and a defect in its record-rule model is a defect in every module built after it.

---

## `P03-M01` — T0 co-design and the platform increment plan

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P03-M01-T01` | Read `M28`, `M29`, `M30` specifications end to end, plus `AR-001` §6 shared kernel and `AR-009` event architecture | `M28`, `M29`, `M30` · `AR-001` · `AR-009` | Reading record | The whole squad, before any model is written | `SA` | — |
| `P03-M01-T02` | Write the `AR-003` Software Design Description for the T0 increment as **one document covering three modules** | `AR-003` · `AR-006` §4.1 pairs 1–3 | T0 SDD | The three cycles are co-design, not defects — the SDD must say so and show the shared boundary | `SA` | T01 |
| `P03-M01-T03` | Decompose the T0 `CD-M28-*`, `CD-M29-*`, `CD-M30-*` items into stories, **one wave ahead** as `SPR-05` requires | `BE-005` §6 · `BE-008` §3.3 | Story backlog for T0 | Every story is **vertical**, <= 8 points, names its requirement, and its reference is reciprocal | `BA` | T02 |
| `P03-M01-T04` | Scaffold the platform modules under `addons/platform/` using `tooling/generators/` | `BE-004` §4 · `AR-007` §3.1 · `BE-006` `CBS-09` | Scaffolded `cd_*` directories | **`AR-007` layer 3: a platform module may never depend on a domain module** (`DL-01`, `FF-17`) | `OD` | T03 |
| `P03-M01-T05` | Populate every manifest with the mandatory 1000FiX keys: `x_cd_id` (issued), `x_module_id`, `x_wave`, `x_owner`, `version` `19.0.1.0.0`, `license` LGPL-3 | `AR-007` §3.2 | Conformant manifests | `FF-16` validates form **and membership**. `application: False` for all but the category anchor | `OD` | T04 |
| `P03-M01-T06` | Establish the **strict `depends` layer order** in every manifest: Odoo core -> OCA -> 1000FiX platform -> 1000FiX domain | `AR-007` §3.4 `DL-01`…`DL-04` | Layered dependencies | **`DL-04`: every `depends` entry is used.** An unused dependency is removed. Never rely on transitive availability — an indirect dependency is invisible at upgrade | `OD` | T05 |
| `P03-M01-T07` | Install the OCA Wave 1 repository set: `operating-unit`, `partner-contact`, `server-tools`, `web`, `helpdesk`, `field-service` core | TSS §20.2 W1 · `W0-01` status matrix | OCA modules installed in `fix_dev` | Cross-check every module against the `W0-01` v19 migration status before depending on it | `OD` | T04 |
| `P03-M01-T08` | Install the Odoo 19 CE Wave 1 core set (11 modules): `base`, `web`, `mail`, `contacts`, `product`, `portal`, and the rest per TSS §20.2 | TSS §20.2 W1 · `02-05` | Odoo core installed | `make odoo-install-wave1` | `OD` | T07 |
| `P03-M01-T09` | Establish the **squad working agreement**: 2-week sprints starting Wednesday, async 10-minute daily scrum (impediments only), 30-minute weekly refinement, 30-minute review, 20-minute retro | `BE-008` §4.1–§4.2 | Working agreement | Ceremony set scaled for 3–5 FTE. **`SPR-15`: ceremony time is capacity and is accounted for explicitly** | `EL` | T03 |
| `P03-M01-T10` | Begin measuring the **squad velocity conversion factor** from sprint 1; use the provisional factor until three sprints of history exist, **and say it is provisional in every report** | `BE-008` §5.2–§5.3 `SPR-17`, `SPR-19` | Velocity record | **`GV-004-A1`: the 0.78 delivery factor is an industry convention, not a 1000FiX measurement.** `BE-008` must establish a measured factor by the end of Wave 1. **A lower factor makes every capacity conclusion worse, not better** | `EL` | T09 |

---

## `P03-M02` — `M29` Identity, Access & Information Security

**In-degree 53. P0. Non-descopable.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P03-M02-T01` | Deploy **Keycloak 26.x as an HA cluster** — not a single node, from Wave 1 | TSS §21.3 · `PE-001` | Keycloak HA pair | **Non-negotiable: Keycloak is a total-outage dependency.** The four components where a single node causes total outage — PostgreSQL primary, Keycloak, Kong, Nginx — are all HA from Wave 1 | `DE` | — |
| `P03-M02-T02` | Build the **role model to the reconciled register** — 53 distinct `R-nn`, resolving the 46-vs-53 discrepancy first | `05-04` §1 · `SC-004` · `B-09a` | Role definitions in Keycloak and Odoo groups | **Building a permission model on 38 or 46 roles when 53 are needed is `W0-03`'s named failure.** Reconcile before building | `SL` | T01, `P01-M04-T09` |
| `P03-M02-T03` | Implement the **six data isolation tiers `T0`–`T5`** as Odoo record rules | `05-04` §4 · `AR-001` §8.2 | Record rules per tier | Every tier is negative-tested. `DoD-07` requires a negative test **per role** | `SL` | T02 |
| `P03-M02-T04` | Implement the **61 segregation-of-duties controls** from `SP-006`, the register of record | `SP-006` · `05-04` §6 · `SC-004` §11.1 | SoD controls | `05-04` §6 lists 30; `SP-006` holds 61. **Build to the register of record**, and record the discrepancy | `SL` | T03 |
| `P03-M02-T05` | Build `cd_rbac_ext` — the field-level permission engine | `CD-M29-nn` · `AR-007` §6 · `05-04` §5 | `cd_rbac_ext` module | `security/<module>_field_rules.xml` is mandatory anywhere field-level permissions apply | `OD` | T03 |
| `P03-M02-T06` | Implement **OAuth 2.0 / OIDC federation** — per-portal credential, per-client SAML/OIDC | TSS §3.1 · `SC-004` | Federation configured | Twelve portals, twelve clients, one identity | `SL` | T01 |
| `P03-M02-T07` | Implement MFA and **step-up authentication** for `T5` reads and privileged operations | `NFR-065` · TSS §3.4 Z4 controls | Step-up flows | **Z4 human access requires step-up authentication and is logged per read** | `SL` | T06 |
| `P03-M02-T08` | Implement the **access lifecycle** driven by `M21-core` joiner/mover/leaver events (`MV-01`) | `05-04` §9 · `AR-006` §5.1 · `M21` | Event-driven provisioning | **`KPI-090`: zero orphaned accounts beyond 24 hours. Leaver path: Keycloak deprovisioning <= 1 hour.** Without `MV-01` this is unachievable for four waves in a system holding payment credentials | `SL` | `P03-M08-T04` |
| `P03-M02-T09` | Implement `SC-010` audit logging and forensic readiness — **privileged session recording** (`NFR-070`) | `SC-010` · `NFR-070` | Audit log infrastructure | Z5 management zone has **no standing access**; privileged sessions are recorded | `SL` | T07 |
| `P03-M02-T10` | Complete `M29` to `DoD-01`…`DoD-17`, with `DoD-07` negative-tested **for every one of the 53 roles** | §0.8.2 | `M29` accepted | Permission test suite green; zero open high or critical security findings | `SL` | T02–T09 |

---

## `P03-M03` — `M28` Integration, API & Event Platform

**In-degree 37. The outbox and the gateway. Non-descopable.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P03-M03-T01` | Deploy **Kong Gateway 3.x** with OAuth2 introspection, per-consumer rate limiting, versioning, request tracing | TSS §3.1, §3.3 · `IN-001` | Kong running, HA | **HA from Wave 1** — Kong is a total-outage dependency | `DE` | — |
| `P03-M03-T02` | Build **`cd_event_outbox`** — the transactional outbox, `fix.domain.event` | `AR-009` · `AS-08` · TSS §3.2 kernel row 6 · `CD-M28-01` | `cd_event_outbox` module | **`AS-08` makes this non-optional. The outbox writes in the same transaction as the business write** — that is what makes events reliable rather than best-effort | `OD` | — |
| `P03-M03-T03` | Deploy **Redis Streams** as the W1–W5 event bus, with the migration path to Apache Kafka/Kafka at W6 designed but not built | TSS §3.1, §20.2 | Redis Streams bus | Designing the migration now costs a day; retrofitting it at W6 costs a wave | `DE` | T02 |
| `P03-M03-T04` | Implement **idempotent consumers, a dead-letter queue and replay-from-timestamp** | TSS §3.1 · `AR-009` · `DI-05` | Consumer framework | An event delivered twice must produce one effect | `BE` | T03 |
| `P03-M03-T05` | Build **`libs/py/fix_events`** as the **only** event client. `FF-28` forbids direct bus clients anywhere else | `BE-004` §4 · `FF-28` | `fix_events` library | One client means one place to fix a delivery-semantics defect | `BE` | T04 |
| `P03-M03-T06` | Stand up the **schema registry** and register the W1 event set from `IN-003` | `IN-003` · `AR-009` `RM-05` | Schema registry populated | **A 988-event catalogue cannot be maintained by hand** — the registry generates it | `IL` | T05 |
| `P03-M03-T07` | Establish the **event naming and envelope standard**, and plan the 242 renames `RM-03` requires | `05-03` §4.1 · `IN-003` `RM-03` · `FF-60` | Envelope standard; rename plan | **`FF-60` cannot be enabled until the 242 renames land.** Register it as `Warning` with a burn-down date | `IL` | T06 |
| `P03-M03-T08` | Publish the **OpenAPI 3.1 contract standard** and author the W1 operations | `IN-002` · `IN-005` · `AS-07` | W1 OpenAPI contracts in `contracts/openapi/` | **Only 35 of 1,187 operations (2.9%) are authored.** The remaining 1,152 are sized at 169–338 PW and are **in no plan** — track the burn-down from sprint 1 | `IL` | T01 |
| `P03-M03-T09` | Deploy **Apache Airflow** for orchestration and register the W1 workflows | TSS §20.2 W1 · `M63` | Apache Airflow running | Apache Airflow is for **configuration that changes when a counterparty changes a template**, not for logic that needs a release | `DE` | T01 |
| `P03-M03-T10` | Implement the **`CON-03` portal contract** and the `PS-11` contract test: **an invalid payload posted directly to the API must be rejected** | `IN-002` · `05-03` §3 · `AS-09` · `PS-11` | `contracts/portal/` + `PS-11` test | This is the test that proves business rules are not implemented in portal code | `IL` | T08 |

---

## `P03-M04` — `M30` Platform Administration & Configuration

**In-degree 28. Entity, branch, zone, calendar, feature flags, country pack.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P03-M04-T01` | Build `fix.entity`, `fix.branch`, `fix.cost.center` on `res.company` + **OCA `operating-unit` (15 modules)** | `M30` · TSS §3.2 kernel row 4 · `CD-M30-nn` | `cd_entity_config` module | **`operating-unit` is the multi-branch isolation mechanism.** Every transactional model carries `operating_unit_id` (`AS-03`, `FF-21`) | `OD` | — |
| `P03-M04-T02` | Build `fix.zone` and `fix.geofence` | `M30` · `M02` dispatch requirements | Zone model | Consumed by dispatch in Phase 5; built here so Phase 5 does not invent it | `OD` | T01 |
| `P03-M04-T03` | Build the **working calendar model**, which `M02`'s W2 availability stub will call | `M30` · `AR-006` §5.2 `M02 -> M55` STUB | Calendar model | The `M02 -> M55` stub returns "available within working calendar" **from `M30`** — so `M30` must supply it | `OD` | T01 |
| `P03-M04-T04` | Build **`cd_country_pack`** — the country-pack interface | `AR-006` §5.2 `M51 -> M65` NOT-A-PREREQ | Country-pack interface | **`M51` needs a country-pack interface, not `M65`.** Delivering it in W1 removes a +5-wave violation | `OD` | T01 |
| `P03-M04-T05` | Build the **feature-flag service** — any new capability disableable without a deployment | `OPS-06` · `EP-07` · `CD-M30-nn` | Feature-flag module | Every capability from here on ships behind a flag | `OD` | T01 |
| `P03-M04-T06` | Build the **Bangladesh address hierarchy** `fix.bd.address` — 8 divisions / 64 districts / upazilas / unions | TSS §3.2 kernel row 3 · `05-02` · `CD-M33-nn` | Address model + reference data | This is master data, not code. It comes from the `MD-*` content set | `OD` | T01 |
| `P03-M04-T07` | Register the **348 state sets** in the code-list register before any module ships a `state` field | `DA-009` · `AR-012` `FF-37` | Populated code-list register | **`FF-37` is a Wave 1 check for exactly this reason** | `DA` | T01 |
| `P03-M04-T08` | Implement configuration promotion: **versioned and promoted through environments, never hand-edited in production** | `OPS-02` · `PE-009` | Configuration promotion pipeline | Configuration is code | `DE` | T05 |
| `P03-M04-T09` | Build the **notification-preference and channel-routing configuration** that `Novu` will consume in Phase 4 | `M30` · `ADR-022` · `M27` | Notification config model | The notification platform lands **three waves ahead of its owning module `M27`** — its configuration must exist in W1 | `OD` | T01 |
| `P03-M04-T10` | Complete `M30` to the full DoD | §0.8.2 | `M30` accepted | Includes `DoD-08` Bengali at 100% and `DoD-11` runbook | `OD` | T01–T09 |

---

## `P03-M05` — `M33` Customer & Party Master — the party kernel

**In-degree 41. The single most important structural decision in the data model.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P03-M05-T01` | Read `M33` in full, plus TSS §3.2 and `AR-008`'s party bounded context | `M33` · TSS §3.2 · `AR-008` | Reading record | — | `SA` | — |
| `P03-M05-T02` | Build `fix.party.role` on `res.partner` + **OCA `partner-contact` (30+ modules)** | `M33` · TSS §3.2 kernel row 1 · `CD-M33-01` | `cd_party_master` module | — | `OD` | T01 |
| `P03-M05-T03` | Enforce the design rule: **a single party holds multiple roles simultaneously** | TSS §3.2 design rule | Multi-role party model + test | **Do not model seller, customer, vendor and partner as separate master records joined by reference.** They are one `res.partner` with multiple `fix.party.role` records. **Violating this produces exactly the duplicate-identity problem the programme exists to remove, and it is unrecoverable once transaction volume accrues against the duplicates** | `SA` | T02 |
| `P03-M05-T04` | Build `fix.party.hierarchy` for corporate structures | `M33` · `CD-M33-nn` | Hierarchy model | Consumed by `P04` corporate portal in Phase 7 | `OD` | T02 |
| `P03-M05-T05` | Build `fix.identity.document` — **NID, passport, TIN — routed through the residency service to Z4** | `M33` · `SC-007` · `CD-M33-nn` · `FF-09` | Identity document model | **The sensitive field is never duplicated into the regional store — not transiently, not in a cache, not in a log.** Enforced at write time, not by convention | `SL` | T02, `P03-M09-T03` |
| `P03-M05-T06` | Build the customer classification model per `M33` | `M33` | Classification model | Full model, not a subset — 22 of 55 reciprocity failures point at `M33` because its consumer list was written before its consumers existed | `OD` | T02 |
| `P03-M05-T07` | Build the **consent registry** — PDPA consent capture, withdrawal and transparency | `M33` · `SC-003` DPIA · `05-06` §6.3 · `CD-M33-nn` | Consent registry | PDPA enforcement activates **~13 May 2027, inside Phase 7**. Consent infrastructure is a W1 build, not a W4 scramble | `SL` | T02 |
| `P03-M05-T08` | Build the **deduplication and golden-record rule set**, consuming `M64-core`'s governance | `M33` · `M64` · `P01-M07-T09` | Dedup engine | The migration in Phase 4 will exercise this against real duplicate volume | `OD` | T02, `P03-M07-T07` |
| `P03-M05-T09` | Emit the `M33` domain events through the outbox and register them | `AS-08` · `IN-003` | Registered party events | `party.created`, `party.merged`, `party.role_added`, consent events | `OD` | T02, `P03-M03-T02` |
| `P03-M05-T10` | Complete `M33` to the full DoD, with `DoD-04` negative tests **through both UI and API** | §0.8.2 | `M33` accepted | A validation in a controller is a rule that binds API callers and not UI users — that is the defect `DoD-04` exists to catch | `OD` | T02–T09 |

---

## `P03-M06` — `M37` Product & Service Catalogue kernel

**In-degree 21. P0. W1.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P03-M06-T01` | Build `fix.catalogue.item` on `product.template` / `product.product` + **OCA `product-attribute`** | `M37` · TSS §3.2 kernel row 2 · `CD-M37-nn` | Catalogue module | Consumed by `M01`, `M11`, `M12`, `M13`, `M14`, `M15`, `M37` | `OD` | — |
| `P03-M06-T02` | Model **service kits** — a service defined as a bundle of parts, labour and time | `M37` | Service kit model | — | `OD` | T01 |
| `P03-M06-T03` | Model **rental SKUs** for `M13` in Phase 9 | `M37` · `M13` | Rental SKU model | Built in the kernel so `M13` composes rather than duplicates | `OD` | T01 |
| `P03-M06-T04` | Model **refurbishment grades** for `M14` in Phase 9 | `M37` · `M14` | Grade model | — | `OD` | T01 |
| `P03-M06-T05` | Build the brand and model masters that `M17`'s device registry will reference | `M37` · `M17` | Brand/model masters | 17+ brand partners; the master must exist before devices are registered | `OD` | T01 |
| `P03-M06-T06` | Load the catalogue **master-data content set** from `project_content` `MD-*` | `project_content` 02C Catalogue and Technical | Loaded catalogue data | **`AF-09`: the 48 `MD-*` files are unbudgeted, and Odoo cannot be configured without them.** If they do not exist, this task blocks | `CN` | T01 |
| `P03-M06-T07` | Apply `AS-10` throughout: every price is `fields.Monetary` with an explicit `currency_id`. **Never `Float`** | `AS-10` · `FF-22` | Monetary-conformant model | `FF-22` blocks pre-merge | `OD` | T01 |
| `P03-M06-T08` | Emit catalogue events through the outbox and register them | `AS-08` · `IN-003` | Registered catalogue events | — | `OD` | T01, `P03-M03-T02` |
| `P03-M06-T09` | Build the `M37 <-> M64` co-design pair as a single increment with `M64-core` | `AR-006` §4.1 pair 5 | Joint increment | Legitimate kernel/MDM co-design. Same wave after `MV-04` | `SA` | `P03-M07-T01` |
| `P03-M06-T10` | Complete `M37` to the full DoD | §0.8.2 | `M37` accepted | Bengali at 100% — a catalogue is user-facing on every portal | `OD` | T01–T09 |

---

## `P03-M07` — `M64-core` MDM governance and `M24-core` document kernel

**`MV-04` and `MV-02` — both moved into Wave 1 by `AR-006` §5.5. Neither is optional.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P03-M07-T01` | Build `M64-core`: the **change-request model and the golden-record rule engine** | `M64` · `AR-006` `MV-04` · `DA-004` | `cd_mdm_core` module | **It governs the W1 kernels — it cannot arrive after them.** The rest of `M64` stays in W2 | `OD` | — |
| `P03-M07-T02` | Wire `M64-core` to `M33` and `M37` as the governance layer over both kernels | `AR-006` §4.1 pairs 4, 5 | Governance wiring | Two legitimate co-design pairs, now in the same wave | `OD` | T01, `P03-M05-T02`, `P03-M06-T01` |
| `P03-M07-T03` | Build `M24-core`: the **`fix.document` kernel model** on `ir.attachment` + **OCA `dms` (5 modules)** | `M24` · `AR-006` `MV-02` · TSS §3.2 kernel row 5 | `cd_document_core` module | **In-degree 23. Seventeen modules in Waves 1–2 attach documents** — service reports, evidence packs, custody photographs, asset documents, identity documents | `OD` | — |
| `P03-M07-T04` | Build the **retention class** model and the **attachment API** | `M24` · `DA-006` · `AR-006` §5.3 | Retention + attachment API | This is the whole of what moves. **Templates, e-signature envelopes, approval chains, legal hold and Mayan EDMS integration stay in W3/W5** | `OD` | T03 |
| `P03-M07-T05` | Load the retention schedule as **content** (`LG-009`), not as a `M60` dependency | `AR-006` §5.2 `M24 -> M60` NOT-A-PREREQ | Loaded retention schedule | The retention *policy* is needed; the GRC *module* is not | `CN` | T04 |
| `P03-M07-T06` | Publish the attachment API so every W1–W2 module consumes it rather than inventing its own | `AS-01` · `IN-002` | Published attachment contract | **Without this, every W1–W2 module invents its own attachment handling and Wave 3 becomes a migration of seventeen ad-hoc implementations** | `IL` | T04 |
| `P03-M07-T07` | Implement the golden-record rules for the party kernel that `M33`'s dedup engine consumes | `M64` · `M33` | Golden-record rules | — | `OD` | T01, `P03-M05-T08` |
| `P03-M07-T08` | Register the `M24-core` and `M64-core` events | `AS-08` · `IN-003` | Registered events | `document.attached`, `document.retention_applied`, `mdm.change_requested`, `mdm.golden_record_updated` | `OD` | T04 |
| `P03-M07-T09` | Record the `M24 <-> M60` pair as **under review** — a kernel owner must not depend on a W6 module | `AR-006` §4.1 pair 15 | Design ruling | Likely a legitimate policy/evidence pairing, but the direction must be resolved | `CA` | T05 |
| `P03-M07-T10` | Complete both cores to the full DoD | §0.8.2 | `M64-core`, `M24-core` accepted | — | `OD` | T01–T09 |

---

## `P03-M08` — `M21-core` employee master and joiner/mover/leaver

**`MV-01` — the movement that resolves the most serious finding in `AR-006`.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P03-M08-T01` | Read `AR-006` §5.1 before starting — understand **why** this slice moved | `AR-006` §5.1 | Reading record | **`M29` has in-degree 53 and declared a dependency on a module arriving four waves later.** This is the correction | `SA` | — |
| `P03-M08-T02` | Build the **employee master** on Odoo `hr` + **OCA `hr`**, W1 slice only | `M21` · `AR-006` `MV-01` | `cd_employee_core` module | **Learning, payroll, performance and talent stay in W5.** Only the master and the lifecycle events move | `OD` | T01 |
| `P03-M08-T03` | Model the employee-to-party relationship through `M33`, not as a separate master | `M33` · TSS §3.2 | Linked employee/party | An employee is a party with an employee role | `OD` | T02, `P03-M05-T03` |
| `P03-M08-T04` | Emit the **joiner / mover / leaver event set**: `employee.joined`, `employee.left`, `employee.role_changed` | `AR-001` §9.1 · `M21` · `AS-08` | JML events registered | This is what `M29`'s access lifecycle consumes | `OD` | T02, `P03-M03-T02` |
| `P03-M08-T05` | Wire the leaver path to **Keycloak deprovisioning within 1 hour** | `M29` · `KPI-090` | Automated deprovisioning | **In a system holding payment credentials and personal data, four waves of manual leaver handling is not an acceptable position** | `SL` | T04, `P03-M02-T08` |
| `P03-M08-T06` | Instrument `KPI-090` — **zero orphaned accounts beyond 24 hours** | `BM-002` · `DoD-09` | KPI instrumented | Visible in `M25` from the wave it lands | `OD` | T05 |
| `P03-M08-T07` | Resolve the `M52 -> M21` violation by consequence — employee expense needs the employee master | `AR-006` §5.4 | Violation closed | One movement, two violations resolved | `SA` | T02 |
| `P03-M08-T08` | Break the `M21 <-> M29` cycle: `M29` **consumes** `M21` events; `M21` calls `M29`'s published API for role assignment | `AR-006` §4.1 pair 17, §4.2 | Interface break implemented | **One direction synchronous, the other an event.** Synchronous-both-ways is a distributed monolith | `SA` | T04 |
| `P03-M08-T09` | Route employee identity documents (NID, TIN) through the residency service to Z4 | `SC-007` · `FF-09` | Residency-routed employee PII | Same rule as customer identity documents | `SL` | T02, `P03-M09-T03` |
| `P03-M08-T10` | Complete `M21-core` to the full DoD | §0.8.2 | `M21-core` accepted | — | `OD` | T02–T09 |

---

## `P03-M09` — Residency service, Z4 store and compliance infrastructure

**`NFR-086`. The architecture decision that a legal opinion gates and a breach cannot undo.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P03-M09-T01` | Provision the **Bangladesh-resident store (Z4)** — PostgreSQL 17, encrypted, **HA pair, separate key material** | TSS §3.3, §21.1 · `PE-001` | Z4 store live | **Small in volume and large in consequence**: a few hundred gigabytes, but it gates every `T5` read in the system | `DE` | — |
| `P03-M09-T02` | Configure **Z4 network isolation** — reachable **only** through the residency service, ingress from Z2 only, no egress | TSS §3.4 zone table | Z4 network policy | **The residency rule is implemented in exactly one place and audited in exactly one place** | `SL` | T01 |
| `P03-M09-T03` | Build the **residency service** (`CD-M29-nn`) — the sole client of Z4 | TSS §14.4 · `SC-007` · `BE-004` `libs/py/fix_residency` | Residency service + `fix_residency` client library | `FF-09`: `fix_residency` is the **only** client. Any other code path reaching Z4 fails the build | `SL` | T02 |
| `P03-M09-T04` | Implement **write-time field-level residency classification** (`NFR-086a`) | TSS §3.3 · `AS-14` · `FF-09` | ORM-level enforcement | **Enforced by mechanism, not by developer discipline.** *"Residency enforcement built as convention rather than mechanism"* is a named stack-failure mode | `SL` | T03 |
| `P03-M09-T05` | Implement **per-read access logging** on Z4, with step-up authentication for human access | TSS §3.4 · `NFR-065` · `SC-010` | Z4 access log | Every read is logged. Every human read is step-up authenticated | `SL` | T03 |
| `P03-M09-T06` | Implement field-level encryption on `S3` data with key management per `SC-006` | `SC-006` · `AS-14` | Field encryption | Separate key material from the regional store | `SL` | T01 |
| `P03-M09-T07` | Build the **`FF-09` fitness function** and enable it **blocking from the first build** | `AR-012` §10 | `FF-09` blocking | **`FF-09` and `FF-03` priority is not negotiable.** A residency leak is a notifiable event | `CA` | T04 |
| `P03-M09-T08` | Implement `NFR-086c` clone-and-mask so **an unmasked clone cannot exist even briefly** | `PE-002` §6 · `QA-004` | Clone-and-mask job | Masking is **part of** the clone job, not a subsequent step | `DA` | T04 |
| `P03-M09-T09` | Build the **PDPA data-subject-request skeleton**: identity verification, regional assembly, resident-field request, portable machine-readable export | TSS §3.6.4 · `M33` consent registry | DSR export path | The erasure saga lands with `M33`/`M29` completion; the export path lands here | `SL` | T03, `P03-M05-T07` |
| `P03-M09-T10` | Complete the DPIA (`SC-003`) against what was actually built, not against what was designed | `SC-003` | Completed DPIA | `DoD-17` — regulatory citations verified current, with a verified-on date | `SL` | T01–T09 |

---

## `P03-M10` — Gate `G1a` — kernel increment exit

**Assessed by: Design Authority. Internal engineering gate. Does not move the Month 4 `G1` date.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P03-M10-T01` | Verify the **T0 triad installs into a clean database in dependency order** | `PE-004` `OD-02` | Clean-install proof | **A module that cannot install alone is not a module** | `OD` | — |
| `P03-M10-T02` | Verify all six shared-kernel concepts are modelled once and consumed, not re-implemented | TSS §3.2 · `AS-01` · `FF-01` | Kernel conformance report | Party, product, location, legal entity, document, event | `CA` | T01 |
| `P03-M10-T03` | Verify **`FF-09` and `FF-03` are blocking and have never been bypassed** | `AR-012` §10 | Pipeline audit | Check the bypass log, not the configuration | `CA` | T01 |
| `P03-M10-T04` | Verify **outbox coverage** — every write path in the eight modules emits its domain event | `AS-08` · `FF-06` | Event coverage report | `DoD-05` | `IL` | T01 |
| `P03-M10-T05` | Verify **permission negative tests exist for every applicable role** across all 53 | `DoD-07` · `05-04` | Permission suite result | Not "the roles are configured" — "a user without the role is denied, and there is a test that proves it" | `SL` | T01 |
| `P03-M10-T06` | Verify **Bengali translation at 100%** on everything delivered | `AS-12` · `DoD-08` · `FF-24` | Translation coverage report | 100%, not 98% | `LL` | T01 |
| `P03-M10-T07` | Verify unit coverage **>= 80%**, and **100% on any financial or tax path** touched | `DoD-03` | Coverage report | No financial paths should exist yet — if any do, they are 100% | `QA` | T01 |
| `P03-M10-T08` | Run the **`AR-012` wave-gate architecture review** and record the drift metrics | `AR-012` §7–§8 | Architecture review record | Drift measured, not asserted | `CA` | T01 |
| `P03-M10-T09` | **Report the capacity position honestly**: measured velocity across sprints 1–5 against the ~120 PW nominal demand | `BE-008` §6 · `GV-004` §5 | Capacity report to Steering | **This is the point at which the 5.87x Wave 1 over-commitment becomes a measurement rather than a projection.** Report it | `EL` | T01 |
| `P03-M10-T10` | **Gate `G1a`.** Design Authority signs: proceed to Phase 4, or re-plan Wave 1b scope | `GV-009` | Signed `G1a` record | If velocity says `G1` at Month 4 is unreachable, **say so now**, while descoping is still cheap | `CA` | T01–T09 |

---
---

# PHASE 4
## SERVICE CORE, FRONT DESK & THE ADMIN PORTAL

### Wave 1b · Months 3–4 · 8.7 weeks · Sprints 6–9 · Gate `G1` · Milestone `MS-03`

---

## 4.0 Phase charter

| | |
|---|---|
| **Purpose** | Put the first transacting business capability on the kernel, and give it a surface |
| **Tiers** | `T2` (registry) and the W1 slice of `T3` (transaction core) |
| **Modules** | `M17` AST core (`MV-05`) · `M04` FRD · `M01` SRM core · `M07` CRM (lead and opportunity slice only) |
| **Platform additions** | Novu notification platform + `CD-M27-nn` — **three waves ahead of its owning module `M27`** (`ADR-022`) |
| **Surface** | **`P03` Admin Operations Portal** — Odoo Web OWL 2, 14 workspaces |
| **Data migration** | Customers, devices, branch master, employee master |
| **Geography** | Dhaka HQ + 5 pilot service centres |
| **Effort** | ~119 PW |
| **Exit** | **`G1` — 12 criteria, Steering-assessed, Month 4.** This is `MS-03` |

> **Why the notification platform is built here and not in Wave 4.** `02-02` Category B records it
> plainly: *"Every module from Wave 1 onward needs to notify customers. If `M27` arrives in W4, each
> earlier module builds its own send path — recreating exactly the fragmentation the programme
> exists to remove."* `ADR-022` rules it into W1. This is the same failure mode `MV-02` fixes for
> documents, with the same remedy.

---

## `P04-M01` — `M17` Device & Customer Asset Registry core

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P04-M01-T01` | Correct the register: `M17`'s device registry core is **W1**, not W2 (`MV-05`) | `AR-006` §5.4 · `06-01` W1 | Corrected declaration | **Register inconsistency, not a real violation** — `06-01` already lists it in W1 | `SA` | — |
| `P04-M01-T02` | Build the **device and customer asset registry** on the `M37` brand and model masters | `M17` · `M37` · `CD-M17-nn` | `cd_device_registry` module | `M01` and `M04` — both W1 — depend on it | `OD` | T01 |
| `P04-M01-T03` | Model serial number, IMEI and identifier uniqueness, with the duplicate-detection rule set | `M17` · `05-05` | Identity model | An IMEI collision at 5 million assets is a data-integrity failure, not an edge case | `OD` | T02 |
| `P04-M01-T04` | Model **warranty status** on the device, which `M09` consumes in Phase 7 | `M17` · `M09` | Warranty status model | Built in the registry so `M09` reads rather than duplicates | `OD` | T02 |
| `P04-M01-T05` | Model device ownership and the **transfer-of-ownership** flow | `M17` · portal `P01` capability set | Ownership model | Portal `P01` exposes this to customers in Phase 5 | `OD` | T02 |
| `P04-M01-T06` | Attach device documents through the **`M24-core` attachment API**, not a local implementation | `M24-core` · `AS-01` | Attachment integration | This is `MV-02` paying for itself | `OD` | T02, `P03-M07-T06` |
| `P04-M01-T07` | Build the device history model — every service order against a device, permanently | `M17` · `M01` | History model | Feeds the customer-facing device history report | `OD` | T02 |
| `P04-M01-T08` | Emit `M17` events through the outbox and register them | `AS-08` · `IN-003` | Registered events | `device.registered`, `device.transferred`, `device.warranty_updated` | `OD` | T02 |
| `P04-M01-T09` | Resolve the `M17 -> M24` violation — closed by `MV-02` | `AR-006` §5.4 | Violation closed | — | `SA` | T06 |
| `P04-M01-T10` | Complete `M17` core to the full DoD | §0.8.2 | `M17` core accepted | The `M17` completion slice lands in Phase 5 | `OD` | T02–T09 |

---

## `P04-M02` — `M04` Branch & Front-Desk Operations

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P04-M02-T01` | Build the **token queue** and walk-in intake flow | `M04` · `CD-M04-nn` | Queue module | Gate criterion: **walk-in intake in under 3 minutes, demonstrated by branch staff** | `OD` | — |
| `P04-M02-T02` | Build the intake form with device identification, fault capture, photo and voice attachment | `M04` · `M17` · `M24-core` | Intake flow | Attachments through the kernel API | `OD` | T01 |
| `P04-M02-T03` | Build the **handover** flow with customer acknowledgement | `M04` | Handover model | — | `OD` | T02 |
| `P04-M02-T04` | Build the **cash drawer and shift control** model | `M04` · `05-05` | Cash control | Money is `Monetary` with explicit currency (`AS-10`). Reconciles to `M19` in Phase 6 | `OD` | T01 |
| `P04-M02-T05` | Build branch-level operating-unit isolation on `M30`'s `fix.branch` | `M30` · `AS-03` | Branch isolation | Every record carries `operating_unit_id`; record rules enforce it | `OD` | T01 |
| `P04-M02-T06` | Model the branch operating calendar and shift roster on `M30`'s calendar | `M30` · `M04` | Branch calendar | — | `OD` | T05 |
| `P04-M02-T07` | Build the front-desk daily reconciliation and end-of-shift report | `M04` · `05-05` | Reconciliation report | Bengali-first output (`DoD-08`) | `OD` | T04 |
| `P04-M02-T08` | Emit `M04` events and register them | `AS-08` · `IN-003` | Registered events | `walkin.registered`, `token.issued`, `handover.completed`, `shift.closed` | `OD` | T01 |
| `P04-M02-T09` | Load the branch master data for the 5 pilot service centres plus Dhaka HQ | `project_content` 02A Organisation and Network | Loaded branch master | `MD-*` content — see `AF-09` funding position | `CN` | T05 |
| `P04-M02-T10` | Complete `M04` to the full DoD, including branch-staff usability validation | §0.8.2 · `UX-008` | `M04` accepted | The 3-minute intake target is validated by **branch staff**, not by developers | `OD` | T01–T09 |

---

## `P04-M03` — `M01` Service Request & Order Management core

**The largest single module in the programme: 88 requirements, 46 PW, split W1–W2.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P04-M03-T01` | Read `M01` in full — 88 requirements, and note that **28 requirement IDs in `M01`, `M02` and `M31` are allocated but unused** | `M01` · `02-02` §3.1 audit finding `H2-03` | Reading record; corrected count | Counts taken from the highest ID rather than the actual count are wrong. Verify before planning | `BA` | — |
| `P04-M03-T02` | Build the **service order and work order core** with its full state machine | `M01` · `AR-007` §7.2 · `CD-M01-01` | `cd_service_order` module | **`AS-06`: state transitions declared in one place per model.** `DP-01` | `OD` | T01 |
| `P04-M03-T03` | Register the service-order state set in the code-list register **before** shipping the `state` field | `DA-009` · `FF-37` | Registered state set | `FF-37` blocks otherwise | `OD` | T02, `P03-M04-T07` |
| `P04-M03-T04` | Build **SLA assignment, clocks and escalation** | `M01` · `05-05` §2 | SLA engine in `services/` | **`AR-007` §3.1: `services/` exists so computation is unit-testable without a database.** SLA maths belongs there; anything in `services/` that writes through the ORM is misplaced | `OD` | T02 |
| `P04-M03-T05` | Build the **guided diagnostic tree and fault coding** | `M01` · `CD-M01-02` | `cd_diagnostic` module | Consumed by the technician app in Phase 5 | `OD` | T02 |
| `P04-M03-T06` | Build the **estimate and approval** flow, including part-approval and revision | `M01` · portal `P01` capability set | Estimate model | Customer-facing in Phase 5; built here | `OD` | T02 |
| `P04-M03-T07` | Build the **QC checklist** enforcement — owned by `M01` in W1–W2 until `M23` arrives in W5 | `M01` · `AR-006` §5.2 `M31 -> M23` STUB | QC model | **Register the `M23` linkage as a `GV-005` stub with an expiry date** | `OD` | T02 |
| `P04-M03-T08` | Implement **idempotency on order creation** — a retried POST must not create two orders | TSS §3.6.1 · `DI-04` · `IN-002` | Idempotency-Key handling | One of the three fragile points in the flagship service-to-cash flow | `IL` | T02 |
| `P04-M03-T09` | Emit the `M01` event set through the outbox and register it | `AS-08` · `IN-003` | Registered events | `service_order.created`, `work_order.assigned`, `work_order.completed`, `estimate.approved` | `OD` | T02 |
| `P04-M03-T10` | Complete the `M01` W1 slice to the full DoD; the W2 completion slice lands in Phase 5 | §0.8.2 | `M01` core accepted | **`DoD-04`: business rules negative-tested through both UI and API** | `OD` | T02–T09 |

---

## `P04-M04` — `M07` CRM — the W1 lead and opportunity slice only

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P04-M04-T01` | Scope `M07`'s W1 slice to **lead and opportunity only** | `AR-006` §5.4 `M07 -> M11`, `M07 -> M36` NOT-A-PREREQ | Scoped W1 slice | **Quotation and pricing arrive with `M07`'s W4 slice.** Declare the dependency against the W4 slice, not W1 | `SA` | — |
| `P04-M04-T02` | Build lead and opportunity on Odoo `crm`, extended not forked | `M07` · `AS-05` · `CD-M07-nn` | CRM extension | `FF-03` | `OD` | T01 |
| `P04-M04-T03` | Wire the pipeline to the `M33` party kernel — an account is a party with a customer role | `M33` · TSS §3.2 | Party-linked CRM | Never a separate account master | `OD` | T02 |
| `P04-M04-T04` | Build account management for corporate parties on `fix.party.hierarchy` | `M33` · `M07` | Account management | Feeds portal `P04` in Phase 7 | `OD` | T03 |
| `P04-M04-T05` | Build activity and interaction capture on the `mail.thread` chatter mixin | `AS-02` · `FF-20` | Activity model | Every custom model inherits the chatter and activity mixins — this is where it earns its keep | `OD` | T02 |
| `P04-M04-T06` | Model the lead-to-service-order conversion path | `M07` · `M01` | Conversion flow | — | `OD` | T02, `P04-M03-T02` |
| `P04-M04-T07` | Emit `M07` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T02 |
| `P04-M04-T08` | Record the deferred `M07` W4 slice explicitly in the backlog with its wave | `BE-008` `SPR-10` | Backlog entry | Deferred work that is not in the backlog is descoped by accident | `BA` | T01 |
| `P04-M04-T09` | Verify no `M07` code depends on `M11` pricing or `M36` quotation | `AS-01` · `FF-01` | Dependency check | The violation was closed by scoping, and CI must keep it closed | `SA` | T02 |
| `P04-M04-T10` | Complete the `M07` W1 slice to the full DoD | §0.8.2 | `M07` W1 accepted | — | `OD` | T02–T09 |

---

## `P04-M05` — The notification platform (`ADR-022`)

**Novu + `CD-M27-nn`, three waves ahead of its owning module `M27`.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P04-M05-T01` | Deploy **Novu** and the notification dispatcher service | TSS §20.2 W1 · `ADR-022` · `M27` | Novu running | — | `DE` | — |
| `P04-M05-T02` | Build the **notification dispatcher** (`CD-M27-nn`) consuming domain events from the outbox | `M27` · `AR-009` · `AS-08` | Dispatcher service | **Every module publishes an event; exactly one component decides how it is delivered** | `BE` | T01, `P03-M03-T04` |
| `P04-M05-T03` | Integrate **`INT-010` SMS**, with `INT-011` redundant SMS designed for W2 | `05-03` §8 · `IN-004` ICD | SMS integration | `DEP-20` — SMS gateway contracts must be live | `IL` | T02 |
| `P04-M05-T04` | Integrate **`INT-012` WhatsApp Business API** | `05-03` §8 · `DEP-19` | WhatsApp integration | `DEP-19` is an external dependency with its own lead time — start it in Phase 1 | `IL` | T02 |
| `P04-M05-T05` | Integrate **`INT-013` email** | `05-03` §8 | Email integration | In every non-production environment this routes to Mailpit (`EP-11`) | `IL` | T02 |
| `P04-M05-T06` | Build channel routing, preference honouring and quiet-hours from `M30`'s configuration | `M30` · `URD` §23 | Routing engine | Customer notification preference is a consent-adjacent obligation, not a convenience | `BE` | T02, `P03-M04-T09` |
| `P04-M05-T07` | Load the **26 `NT-*` notification content templates** in Bengali and English | `project_content` 04 Notification and Messaging | Loaded templates | 26 files. **Bengali is not optional — 266 of 452 content files require a Bengali counterpart** | `CN` | T02 |
| `P04-M05-T08` | Implement delivery-status tracking, retry and dead-letter handling for every channel | `IN-006` · `AR-009` | Delivery tracking | A notification that silently failed is worse than one that visibly failed | `BE` | T03–T05 |
| `P04-M05-T09` | Implement the **fallback register for P0 integrations** — what happens when a gateway is down | `05-03` §7 fallback register | Fallback behaviours | Every P0 integration has a named fallback, and it is tested | `IL` | T08 |
| `P04-M05-T10` | Instrument notification KPIs and expose them for `M25` in Phase 7 | `DoD-09` | Instrumented KPIs | Delivery rate, latency, channel mix, opt-out rate | `BE` | T08 |

---

## `P04-M06` — `P03` Admin Operations Portal

**Odoo Web OWL 2 · 14 workspaces · the only surface in Wave 1.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P04-M06-T01` | Read the `P03` specification and `UX-002` information architecture | `P03` · `UX-002` · `UX-003` | Reading record | ~782 generated views. **`UX-001` §3.3 rejects rebuilding `P03` in Next.js as disproportionate** | `UX` | — |
| `P04-M06-T02` | Build the `P03` shell and navigation model per `UX-002` | `UX-002` · `P03` | Portal shell | Odoo Web OWL 2, runtime `R1` | `FE` | T01 |
| `P04-M06-T03` | Build the W1 workspaces: service order, front desk, party master, device registry, catalogue, administration | `P03` · `UX-003` | 6+ workspaces | Every W1 capability is exercised through `P03` — nothing is admin-only by accident | `FE` | T02 |
| `P04-M06-T04` | Implement `R1` design-token consumption — SCSS variables compiled by the Odoo asset bundler | `UX-001` §3.1, §5.3 | `R1` token realisation | **One token source, one component contract, five realisations, one conformance suite** (`DSY-01`) | `UX` | T02, `P04-M07-T02` |
| `P04-M06-T05` | Apply **`AS-09`** — no business logic in views, controllers or portal code | `AS-09` · `FF-05` | Clean separation | A rule in a view binds UI users and not API callers | `FE` | T03 |
| `P04-M06-T06` | Implement role-based menu and action visibility from `M29`'s model | `M29` · `05-04` §2 portal access matrix | Role-driven UI | Negative-tested per role (`DoD-07`) | `FE` | T03, `P03-M02-T03` |
| `P04-M06-T07` | Achieve **WCAG 2.2 AA** on delivered screens; run axe-core in CI | `UX-005` · CI stage 12 | Accessibility pass | Automated scan **plus** manual audit — `UX-005` names 11 criteria no design and no build can discharge | `UX` | T03 |
| `P04-M06-T08` | Achieve **100% Bengali** on every `P03` screen, including layout under text expansion | `AS-12` · `UX-007` · `DoD-08` | Bengali complete | **`L11` localisation is owned end to end by the Localisation Lead**, including the layout-under-expansion test | `LL` | T03 |
| `P04-M06-T09` | Load the **`UI-*` copy and microcopy** content set for the delivered workspaces | `project_content` 03 UI Copy and Microcopy | Loaded copy | 42 `UI` files across the estate; the W1 subset lands here | `CN` | T03 |
| `P04-M06-T10` | Complete `P03` to the portal DoD, including the cross-portal requirement set | `05-01` §4 cross-portal requirements · §0.8.2 | `P03` accepted | — | `FE` | T02–T09 |

---

## `P04-M07` — Design system foundation

**`DSY-01`. Established now because five runtimes cannot be retrofitted onto a common contract.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P04-M07-T01` | Read `UX-001` §3 in full and understand why a single component *library* is not achievable | `UX-001` §3.1–§3.5 | Reading record | **Dart cannot consume a CSS custom property. QWeb cannot consume a React component. Grafana cannot consume either.** A requirement that cannot be satisfied will be quietly breached in Wave 1 and then cited as satisfied for thirty-six months | `UX` | — |
| `P04-M07-T02` | Build the **single DTCG JSON token source** — the only place a design value is authored | `UX-001` §5.3 W3C Design Tokens Format Module 2025.10 | Token source tree | Every runtime consumes a **generated** artefact; **no runtime authors a value** | `UX` | T01 |
| `P04-M07-T03` | Define the semantic colour set: text and surface (light), the eight status tokens, and the dark theme | `UX-001` §5.4 | Colour tokens | Contrast validated against WCAG 2.2 AA in both themes | `UX` | T02 |
| `P04-M07-T04` | Define the typography scale and font loading, **including the Bengali font stack** | `UX-001` §5.5 · `UX-007` | Type tokens | Bengali conjunct shaping is a first-class concern, not a fallback | `LL` | T02 |
| `P04-M07-T05` | Define space, grid, breakpoints and the density contract | `UX-001` §5.6 | Layout tokens | — | `UX` | T02 |
| `P04-M07-T06` | Write the **component contract** — name, props, slots, states, variants, accessibility semantics, copy contract — implemented identically by all realisations | `UX-001` §3.2, §8 | Component contract | Realisations may differ in code and are **forbidden to differ in rendered result** beyond `PID-01`…`PID-07` | `UX` | T02 |
| `P04-M07-T07` | Build the **`R1` (OWL 2) realisation** for the W1 component set | `UX-001` §3.1 | `R1` components | — | `FE` | T06 |
| `P04-M07-T08` | Build the **cross-runtime conformance suite** asserting token values, state coverage, contrast, target size and **Bengali fit** | `UX-001` §11 `CFM-01`…`CFM-05` | Conformance suite | `CFM-01` no raw literals · `CFM-04` inventory parity · `CFM-05` visual parity | `UX` | T07 |
| `P04-M07-T09` | Declare the **`R5` partial conformance** for `P06` (Apache Superset/Grafana) explicitly rather than discovering it later | `UX-001` §3.5 | Declared exception | Colour tokens full · type tokens partial · component contract not applicable | `UX` | T06 |
| `P04-M07-T10` | Raise `UX-001-D-01` to the Change Board — the `NFR-080` restatement — and **build to the stricter reading until it rules** | `UX-001` §3.2 · `GV-003` | Change request raised | Both statements are live until the Board rules | `UX` | T06 |

---

## `P04-M08` — Bengali localisation base and W1 content load

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P04-M08-T01` | Read `UX-007` bilingual interface standard and the `BN-*` content set | `UX-007` · `project_content` 11 Localisation | Reading record | 18 `BN` files, 9 of them P0 | `LL` | — |
| `P04-M08-T02` | Establish the translation workflow: `.pot` extraction, `bn_BD.po` maintenance, **100% before acceptance** | `AS-12` · `AR-007` §3.1 `i18n/` | Translation pipeline | `FF-24` blocks pre-merge at anything below 100% | `LL` | T01 |
| `P04-M08-T03` | Build `libs/ts/i18n` — `BN-005` key loading and pluralisation for the web estate | `BE-004` §4 · `UX-007` | i18n library | One implementation across six Next.js portals | `FE` | T02 |
| `P04-M08-T04` | Establish **`BN-007` formatting**: dates, numbers, currency, addresses in Bengali conventions | `UX-007` · `05-06` §9 | Formatting rules | `PID-03` — a native date picker may differ, but **the value written must be identical** | `LL` | T02 |
| `P04-M08-T05` | Implement the **Bengali QWeb report rendering** path and its committed reference images | `TR-07` · `make doctor` check 10 | Report rendering + reference images | **The only way an automated check catches a conjunct-shaping regression before it reaches a Mushak 6.3 invoice** | `LL` | T02 |
| `P04-M08-T06` | Load the W1 subset of the **48 `MD-*` master-data files** | `project_content` 02 Master Data · `AF-09` | Loaded master data | **`AF-09`: unbudgeted. Odoo cannot be configured without them.** If unfunded, this task is blocked and must be escalated, not worked around | `CN` | — |
| `P04-M08-T07` | Load the **`DT-*` document and print templates** required in W1 | `project_content` 05 Document and Print Templates | Loaded templates | 44 `DT` files across the estate; statutory ones land in Phase 6 | `CN` | T05 |
| `P04-M08-T08` | Load the **`LG-*` legal and policy content** required for consent capture | `project_content` 10 Legal, Policy and Compliance · `M33` consent registry | Loaded legal content | 24 `LG` files, 7 of them P0, all requiring legal sign-off | `CN` | — |
| `P04-M08-T09` | Establish the layout-under-text-expansion test — Bengali is typically longer than English | `UX-007` · `QA-001` `L11` | Expansion test | Owned by the Localisation Lead; QA supplies the harness | `LL` | T04 |
| `P04-M08-T10` | Report content readiness against the 452-file register: **452 written, 0 approved** | `project_content` master index | Content readiness report | **32 Class A/B files await gate `G6`; 266 await a Bengali counterpart; the Programme Content Lead who is the final approver of every Class E file is unappointed.** Escalate the appointment | `CN` | T06–T08 |

---

## `P04-M09` — Wave 1 data migration

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P04-M09-T01` | Build the ETL for the **customer master** from the multiple contact-data sources | `MG-003` · `P01-M07-T02` profiles | Customer ETL | Dedup and merge under the `M33`/`M64-core` golden-record rules | `ML` | — |
| `P04-M09-T02` | Build the ETL for the **device and customer asset master** | `MG-003` · `M17` | Device ETL | — | `ML` | T01 |
| `P04-M09-T03` | Build the ETL for the **branch master** | `MG-003` · `M30` | Branch ETL | — | `ML` | — |
| `P04-M09-T04` | Build the ETL for the **employee master** | `MG-003` · `M21-core` | Employee ETL | Enabled by `MV-01` | `ML` | — |
| `P04-M09-T05` | Apply **`MIG-03`** — every migrated record carries its **legacy reference, permanently** | TSS §19.2 · `FR-SRM-088` | Legacy reference on every record | Legacy order lookup is a live requirement, not a migration convenience | `ML` | T01–T04 |
| `P04-M09-T06` | Apply **`MIG-06`** — migrated personal data goes through the **residency service**, not directly into the regional store | TSS §19.2 · `P01-M07-T08` | Residency-routed migration | **A bulk loader can bypass a runtime ORM check. This is the compliance breach the architecture exists to prevent, at scale, on day one** | `ML` | T01, `P03-M09-T03` |
| `P04-M09-T07` | Implement **`MIG-02` control totals** — record count, value total, checksum — reconciled **before** the load is accepted | TSS §19.2 · `MG-004` · `DI-06` | Control-total reconciliation | Not after. Before | `ML` | T05 |
| `P04-M09-T08` | Run the **`MG-005` mock migration** on `migration-staging` at production volume | `MG-005` · `MIG-04` · `DoD-10` | Mock migration record | **Dry run against production-sized data before every cutover** | `ML` | T07 |
| `P04-M09-T09` | Rehearse the **`MG-007` rollback** for each migration | `MG-007` · `MIG-07` · `DoD-16` | Rehearsed rollback | Documented **and rehearsed**, not documented | `ML` | T08 |
| `P04-M09-T10` | Obtain **business reconciliation sign-off** — this is gate criterion `G1-05` | `MG-004` · `GV-009` §7 | Signed reconciliation | **`MIG-08`: legacy systems are decommissioned only after reconciliation sign-off, not on go-live day** | `ML` | T08 |

---

## `P04-M10` — Gate `G1` — Foundation go-live (`MS-03`, Month 4)

**Assessed by: Steering Committee, on evidence. 12 criteria.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P04-M10-T01` | Run the **`T−6` week entry criteria check**, not at the gate itself | `GV-009` §9.2 | Entry check record | An entry criterion checked at the gate is a criterion checked too late | `PM` | — |
| `P04-M10-T02` | `G1-01` **Service orders created from all channels at pilot sites, end to end** | `06-01` W1 gate · `06-02` | Demonstration record | Demonstrated in `staging` with production-shaped configuration | `QA` | T01 |
| `P04-M10-T03` | `G1-02` **Walk-in intake in under 3 minutes, demonstrated by branch staff** | `06-01` W1 gate · `UX-008` | Timed demonstration | **By branch staff, not by developers** | `QA` | T01 |
| `P04-M10-T04` | `G1-03` **Customer and device data migrated with reconciliation signed off** | `P04-M09-T10` | Signed reconciliation | — | `ML` | T01 |
| `P04-M10-T05` | `G1-04` **SLA clocks and escalation firing correctly** | `M01` · `05-05` §2 | SLA test evidence | Including breach and near-breach paths | `QA` | T01 |
| `P04-M10-T06` | `G1-05` **100% Bengali translation on all delivered screens** | `AS-12` · `FF-24` | Translation report | 100%. Not 98% | `LL` | T01 |
| `P04-M10-T07` | `G1-06` **Zero critical or high security findings** | `DoD-15` · `SC-009` | Security report | Penetration test per `SC-009` | `SL` | T01 |
| `P04-M10-T08` | Verify the **standing criteria** that apply at every gate | `GV-009` §9.1 | Standing criteria record | Applied at **every** gate, not only this one | `PM` | T01 |
| `P04-M10-T09` | Run the **`gate` pipeline profile**: performance at **1.5x peak** (`DoD-14`) and DR drill evidence (`PE-007`) | `PE-004` §4.2, §5.1 stages 16–17 | Gate profile results | Both block | `DE` | T01 |
| `P04-M10-T10` | **Gate `G1`.** Steering signs. Publish the gate report and the residual open items | `GV-009` §6.2–§6.4 | Signed `G1`; `MS-03` achieved | Outcomes: proceed · proceed-with-conditions (each condition named, owned, dated) · hold | `PM` | T02–T09 |

---
---

# PHASE 5
## FIELD OPERATIONS, THE OFFLINE ENGINE & INVENTORY

### Wave 2 · Months 5–8 · 17.4 weeks · Sprints 10–18 · Gate `G2` · Milestone `MS-04`

---

## 5.0 Phase charter

| | |
|---|---|
| **Purpose** | Put the business into the field. Dispatch, GPS, the technician application, and the inventory that a repair consumes |
| **Tiers** | `T3` complete, `T4` partial |
| **Modules** | `M31` WSR · `M02` FSM · `M15` INV · `M10` LOY · `M64` (completion) · `M01` (completion) · `M17` (completion) |
| **Portals** | **`P01` Customer Self-Service Portal** (Next.js) · **`P02` Technician Mobile Application** (Flutter) |
| **Technology entering service** | Traccar 6.x · OSRM · VROOM · TimescaleDB · Grafana · dispatch scoring service · route orchestrator · telemetry collector · **the shared offline engine** |
| **Integrations** | `INT-011` redundant SMS · `INT-014` push · `INT-019`–`INT-023` mapping, routing, GPS |
| **Geography** | All Dhaka centres |
| **Effort** | 240 PW against ~95 effective PW — **2.53x over** |
| **Exit** | `G2` — 10 criteria, Month 8. This is `MS-04` |

> **The single hardest technical requirement in the programme lands here.** 24-hour offline operation
> with server-authoritative conflict resolution. `ADR-024` rules **one offline engine in Dart, shared
> by three applications** — technician, rider and auditor. It is built once, in this phase, by the
> squad that will not own two of the three consumers. Get the contract right or pay for it three
> times.

---

## `P05-M01` — `M15` Spare Parts & Inventory Management

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P05-M01-T01` | Install Odoo `stock` and the **OCA `stock-logistics-*` set** (55+ modules), cross-checked against `W0-01` | `M15` · TSS §20.2 W2 · `W0-01` | Stock layer installed | `AS-05` — extended, never forked | `OD` | — |
| `P05-M01-T02` | Build **multi-location inventory** on `M30`'s branch and operating-unit model | `M15` · `M30` · `CD-M15-nn` | Multi-location model | 51+ branches, each an operating unit | `OD` | T01 |
| `P05-M01-T03` | Build **van stock** — a technician's vehicle as an inventory location | `M15` · `M02` · portal `P02` | Van stock model | Consumed by the technician app's parts flow | `OD` | T02 |
| `P05-M01-T04` | Build **barcode and QR operations** using the OCA `stock-logistics-barcode` connector | `M15` · TSS L3 | Barcode operations | Scan-to-consume is the technician's primary parts interaction | `OD` | T02 |
| `P05-M01-T05` | Build replenishment alerts and reorder rules | `M15` · `05-05` §6 | Replenishment engine | `M43` demand planning extends this in Phase 9 — build the seam now | `OD` | T02 |
| `P05-M01-T06` | Implement the **`M15 -> M19` stub**: stock valuation posts to a **suspense account** in W2, reconciled at the W3 GL cutover | `AR-006` §5.4 | Suspense posting + registered stub | **Register in `GV-005` with an expiry date. An unreconciled suspense balance across a wave boundary is a finance risk** and must be visible | `OD` | T02 |
| `P05-M01-T07` | Build parts return and van reconciliation | `M15` · portal `P02` | Return flow | — | `OD` | T03 |
| `P05-M01-T08` | Apply `AS-10` to every valuation and cost field | `AS-10` · `FF-22` | Monetary conformance | Inventory valuation is a financial path — `DoD-03` requires **100% test coverage** on it | `OD` | T02 |
| `P05-M01-T09` | Emit `M15` events and register them | `AS-08` · `IN-003` | Registered events | `stock.consumed`, `stock.returned`, `reorder.triggered`, `van.reconciled` | `OD` | T02 |
| `P05-M01-T10` | Complete `M15` to the full DoD | §0.8.2 | `M15` accepted | Gate criterion: **inventory accuracy >= 95% at migrated locations** | `OD` | T01–T09 |

---

## `P05-M02` — `M31` Workshop & Depot Repair Management

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P05-M02-T01` | Build **bench assignment and the WIP board** | `M31` · `CD-M31-nn` | Workshop module | 58 requirements, 30 PW | `OD` | — |
| `P05-M02-T02` | Build **repair-level routing (L1 / L2 / L3)** | `M31` | Repair-level model | Routes a job to the right bench and the right skill | `OD` | T01 |
| `P05-M02-T03` | Build multi-job handling — a technician working several benches | `M31` · portal `P02` workshop mode | Multi-job model | — | `OD` | T02 |
| `P05-M02-T04` | Build the **evidence pack** on the `M24-core` attachment API | `M31` · `M24-core` · `AS-01` | Evidence pack | Consumed by warranty claims in Phase 7 | `OD` | T01, `P03-M07-T06` |
| `P05-M02-T05` | Implement the **`M31 -> M22` certification stub** — returns "eligible" until W5 | `AR-006` §5.2 STUB | Stub + `GV-005` registration | **A stub that always returns "eligible" is a control that does not work.** It must carry an expiry | `SA` | T02 |
| `P05-M02-T06` | Implement the **`M31 -> M23` QC stub** — QC checklists owned by `M01` until W5 | `AR-006` §5.2 STUB · `P04-M03-T07` | Stub + registration | — | `SA` | T02 |
| `P05-M02-T07` | Downgrade `M31 -> M45` to a `§12` interface reference — test-equipment calibration is a W5 quality capability, **not a W2 repair prerequisite** | `AR-006` §5.2 NOT-A-PREREQ | Corrected declaration | — | `SA` | T01 |
| `P05-M02-T08` | Wire the workshop into the `M01` service-order state machine — one state machine, not two | `M01` · `AS-06` | Unified state machine | `AS-06`: state transitions declared in **one** place per model | `OD` | T01 |
| `P05-M02-T09` | Emit `M31` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01 |
| `P05-M02-T10` | Complete `M31` to the full DoD | §0.8.2 | `M31` accepted | — | `OD` | T01–T09 |

---

## `P05-M03` — `M02` Field Service & Dispatch Management

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P05-M03-T01` | Install **OCA `field-service` (33 modules)**, verified against `W0-01` | `M02` · TSS §5 · `W0-01` | field-service installed | 74 requirements, 40 PW. **Extended by custom CD items, never forked** | `OD` | — |
| `P05-M03-T02` | Build the **dispatch board** — the operational surface for coordinators | `M02` · `P03` | Dispatch board | Real-time via Odoo long-polling channels | `FE` | T01 |
| `P05-M03-T03` | Build the **dispatch scoring service** as an L5 standalone service, outside the Odoo process | `M02` · TSS §3.1 domain services · `CD-M02-nn` | `services/dispatch-scoring/` | Scores on: skill, certification, van stock, zone, SLA risk, route. **Python/FastAPI, event-driven from the outbox** | `BE` | T01 |
| `P05-M03-T04` | Build the **route orchestrator** over VROOM and OSRM | `M02` · TSS §20.2 W2 | `services/route-orchestrator/` | Gate criterion: **route optimisation reducing measured travel time by >= 15%** | `BE` | T03, `P05-M04-T03` |
| `P05-M03-T05` | Implement the **`M02 -> M22` certification stub** and the **`M02 -> M55` availability stub** (returns "available within working calendar" from `M30`) | `AR-006` §5.2 · `P03-M04-T03` | 2 registered stubs | Both carry expiry dates in `GV-005` | `SA` | T01 |
| `P05-M03-T06` | Downgrade `M02 -> M46` — **vehicle assignment is optional for W2 dispatch**; technicians dispatch on foot, by motorcycle and by shared vehicle | `AR-006` §5.2 NOT-A-PREREQ | Corrected declaration | — | `SA` | T01 |
| `P05-M03-T07` | Build zone and geofence enforcement on `M30`'s `fix.zone` and `fix.geofence` | `M30` · `M02` | Zone enforcement | Shift clock-in with geofence is a `P02` requirement | `OD` | T01, `P03-M04-T02` |
| `P05-M03-T08` | Build the accept/decline flow with reason capture | `M02` · portal `P02` | Assignment flow | — | `OD` | T01 |
| `P05-M03-T09` | Emit `M02` events and register them | `AS-08` · `IN-003` | Registered events | `work_order.assigned`, `technician.location_updated` (throttled), `job.accepted`, `job.declined` | `OD` | T01 |
| `P05-M03-T10` | Complete `M02` to the full DoD | §0.8.2 | `M02` accepted | — | `OD` | T01–T09 |

---

## `P05-M04` — The geospatial platform

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P05-M04-T01` | Deploy **TimescaleDB** with native compression as a hypertable store | TSS §3.6.2 · `TD-13` | TimescaleDB live | **400 technicians at 30-second intervals is 800 positions/minute, 1.15 million/day, ~420 million/year.** At that volume GPS in the primary OLTP database would dominate the transaction log and degrade every other write | `DE` | — |
| `P05-M04-T02` | Deploy **Traccar 6.x** and integrate `INT-023` GPS ingestion | TSS §3.6.2 · `05-03` §8 W2 | Traccar live | Writes to TimescaleDB; pushes to `M02` by REST | `DE` | T01 |
| `P05-M04-T03` | Deploy **OSRM and VROOM** for routing and vehicle-routing optimisation | TSS §20.2 W2 · `TD-05` (Timefold rejected) | OSRM + VROOM live | Integrations `INT-020`, `INT-021`, `INT-022` | `DE` | — |
| `P05-M04-T04` | Build the **telemetry collector** service | `CD-M02-nn` · TSS §20.2 W2 | `services/telemetry-collector/` (Go) | Scales to 50,000 telemetry/minute by Phase 11 | `BE` | T01 |
| `P05-M04-T05` | Implement **ETA calculation** and the throttled `technician.location_updated` event | TSS §3.6.2 | ETA service | **Throttled** — an untrottled position event at 800/minute floods every consumer | `BE` | T02, T03 |
| `P05-M04-T06` | Build the customer-facing live tracking page with a **polling fallback if the webhook fails** | TSS §3.6.2 · portal `P01` | Tracking page + fallback | Every P0 integration has a named, tested fallback (`05-03` §7) | `FE` | T05 |
| `P05-M04-T07` | Deploy **Grafana** and build the operational dashboards for dispatch and GPS health | TSS §20.2 W2 · `PE-008` | Grafana dashboards | — | `DE` | T01 |
| `P05-M04-T08` | Implement GPS data retention and compression policy | `DA-006` · TimescaleDB compression | Retention policy | 420 million rows/year is a storage decision, not an afterthought | `DA` | T01 |
| `P05-M04-T09` | Classify location data under `DA-005` and confirm its residency position | `DA-005` · `D-013` | Classification record | Location history is personal data under PDPA | `SL` | T01 |
| `P05-M04-T10` | Instrument `NFR-056` (800 positions/minute sustained) and verify at **1.5x peak** | `NFR-056` · `DoD-14` | Performance evidence | 1,200/minute in the `perf` environment | `QA` | T04 |

---

## `P05-M05` — The shared offline engine (`ADR-024`)

**Built once in Dart. Shared by `P02` technician, `P09` rider and `P11` auditor. `FL-03` is review-only — no tool catches a second offline engine.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P05-M05-T01` | Read `AR-010` in full — the command model, sync protocol, conflict resolution and disclosure | `AR-010` §3–§8 · `UX-006` | Reading record | The whole mobile squad, before any Dart is written | `MB` | — |
| `P05-M05-T02` | Build `libs/dart/fix_offline` — **the one offline engine** | `AR-010` · `BE-004` §4 · `ADR-024` | `fix_offline` package | **`FL-03`: one offline engine.** A second one is a review-only violation with no automated check — the reviewer is the control | `MB` | T01 |
| `P05-M05-T03` | Implement the **command journal** — append-only, in **encrypted SQLite (SQLCipher)**, keyed from device credentials plus a server-issued key, **wiped on remote revocation** | `AR-010` §3, §4.1 | Local store | **Commands, not records.** The journal is the only local truth; the read cache is never authoritative | `MB` | T02 |
| `P05-M05-T04` | Implement the **sync sequence**: upload with `last_ack_sequence` and batch checksum, then download delta by opaque server-issued token | `AR-010` §4.2 | Sync client | **`SP-07`: upload precedes download in the same sync cycle.** Download-first means the technician's work appears to vanish and return — and users do not wait to find out, they re-enter it | `MB` | T03 |
| `P05-M05-T05` | Implement the server side: **one database transaction per command, never per batch**; a per-batch checksum; retry the batch **whole, never partially applied** | `AR-010` §4.3 `SP-01`…`SP-03` | Server sync endpoint | **`SP-02`: a batch transaction means one rejected command rolls back nine accepted ones. Per-command means partial progress is real progress** | `BE` | T04 |
| `P05-M05-T06` | Implement the **server-side idempotency ledger** keyed on `command_id` — **on repeat, return the original result; never re-evaluate** | `AR-010` §4.4 · `DI-05` | Idempotency ledger | This is what makes "exactly once" true rather than aspirational | `BE` | T05 |
| `P05-M05-T07` | Implement **conflict detection and the authority matrix** — server-authoritative resolution | `AR-010` §5 | Conflict engine | Outcomes: apply · reject · apply-with-conflict | `BE` | T06 |
| `P05-M05-T08` | Implement **conflict disclosure** — the two states that must never be conflated: *not yet synced* and *synced-and-rejected* | `AR-010` §6.1–§6.3 | Conflict UI contract | A technician who cannot tell the difference will redo work or lose it | `MB` | T07 |
| `P05-M05-T09` | Implement the **deferred evidence channel** — low priority, resumable, and **never blocking state sync** | `AR-010` §8 `SP-09` | Evidence channel | **A 40 MB photo backlog must not delay a job status** | `MB` | T04 |
| `P05-M05-T10` | Build the **`L12` offline test suite** — 33 scripts, 24-hour operation, scripted conflict scenarios | `QA-001` `L12` · `TS-015` | Offline test suite | **The field half cannot be automated.** *A lab test with aeroplane mode does not reproduce a technician in Gazipur whose signal came and went four times across a nine-hour shift.* `TS-015` `L-01`…`L-08` resource the field half | `QA` | T08 |

---

## `P05-M06` — `P02` Technician Mobile Application (Flutter)

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P05-M06-T01` | Build the app shell on `libs/dart/fix_ui` with the **`R4` design-token realisation** | portal `P02` · `UX-001` §3.1 `R4` | App shell | **Flutter consumes `ThemeData` / Dart constants — no CSS of any kind.** The tokens are generated, not authored | `MB` | `P04-M07-T02` |
| `P05-M06-T02` | Build the **day view**: optimised job queue, accept/decline, geofenced shift clock-in/out, leave request, daily summary | portal `P02` capability set | Day view | — | `MB` | T01 |
| `P05-M06-T03` | Build **job execution**: full job context and device history, guided diagnostic tree, fault coding, repair notes, time tracking | portal `P02` · `M01` diagnostic | Job execution | — | `MB` | T02 |
| `P05-M06-T04` | Build **parts**: van stock view, barcode/QR scan to consume, request parts, return unused, van reconciliation | portal `P02` · `M15` | Parts flow | — | `MB` | T03 |
| `P05-M06-T05` | Build **evidence capture**: before/after photos with GPS and timestamp, short video, **voice notes in Bengali**, document scan | portal `P02` · `M24-core` | Evidence capture | Uploaded on the deferred evidence channel | `MB` | T03, `P05-M05-T09` |
| `P05-M06-T06` | Build **customer-facing** flows: estimate presentation, on-site approval, e-signature, on-site payment collection, receipt issue | portal `P02` · `M01` estimate | Customer flows | Payment collection integrates in Phase 6 | `MB` | T03 |
| `P05-M06-T07` | Build **navigation** — turn-by-turn, route overview, automatic arrival detection | portal `P02` · OSRM | Navigation | `INT-019` mapping | `MB` | T02 |
| `P05-M06-T08` | Build **offline knowledge** — repair manuals, wiring diagrams and past repair notes, available offline | portal `P02` | Offline knowledge | Read cache, pruned before the journal is ever pruned | `MB` | T03 |
| `P05-M06-T09` | Build the **panic and safety alert** path, and `M59`'s mobile incident reporting brought forward from W6 | portal `P02` · `02-02` Category H sequencing note · `FR-HSE-009`, `FR-HSE-011` | Safety reporting | **`M59`'s mobile reporting depends only on `P02` and `M21` — it ships here at low incremental cost.** The remaining 40 `M59` requirements stay in W6 | `MB` | T02 |
| `P05-M06-T10` | Complete `P02` to the portal DoD, in **Bengali first**, and validate with real technicians | portal `P02` · `UX-008` · `DoD-08` | `P02` accepted | Gate criterion: **technician app in daily use by all Dhaka technicians; 24-hour offline operation demonstrated with zero data loss** | `MB` | T01–T09 |

---

## `P05-M07` — `P01` Customer Self-Service Portal (Next.js)

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P05-M07-T01` | Confirm the Next.js baseline from **`D-026`** before writing a line | `D-026` · `B-07` | Confirmed baseline | **Next.js 16.3 provides long-term support.** Building six portals on an EOL runtime is a decision, not a default | `FE` | `P01-M02-T04` |
| `P05-M07-T02` | Build the portal shell with the **`R3` token realisation** — CSS custom properties, generated | `UX-001` §3.1 `R3`, §5.3 | Portal shell | `CFM-01` — no raw literals | `FE` | T01, `P04-M07-T02` |
| `P05-M07-T03` | Build **account**: registration with phone/email OTP, profile, tagged addresses with saved GPS, language preference, notification preferences, **consent management** | portal `P01` capability set · `M33` consent registry | Account flows | Consent management is a PDPA obligation surfaced to the customer | `FE` | T02 |
| `P05-M07-T04` | Build **booking in <= 3 steps** with delivery-mode choice, slot selection, fault description with photos and voice, and an upfront price indication | portal `P01` · `M01` | Booking funnel | **Booking funnel conversion is the primary design KPI.** Target > 72% | `FE` | T02 |
| `P05-M07-T05` | Build **tracking**: live status timeline, live technician map with ETA, technician name and photo, **public tracking link without login** | portal `P01` · `P05-M04-T06` | Tracking | The public link is a deliberate no-auth surface — it must expose nothing beyond status and ETA | `FE` | T02 |
| `P05-M07-T06` | Build **devices**: register by serial/IMEI/photo, view history, warranty status, download device history report, transfer ownership | portal `P01` · `M17` | Device flows | — | `FE` | T02 |
| `P05-M07-T07` | Build **approvals**: review estimates, approve/part-approve/decline, e-sign, view revisions | portal `P01` · `M01` estimate | Approval flows | — | `FE` | T04 |
| `P05-M07-T08` | Enforce the **< 400 KB total first-load payload on the booking path**, on a 3G connection | portal `P01` design requirements · CI stage 11 | Bundle budget met | Blocking pre-merge. Verify locally with Chrome DevTools Lighthouse and 3G throttling before pushing | `FE` | T04 |
| `P05-M07-T09` | Build the **Progressive Web App** offline shell and installability | portal `P01` design requirements | PWA | Distinct from the `fix_offline` command engine — this is a shell, not a journal | `FE` | T02 |
| `P05-M07-T10` | Achieve **WCAG 2.2 AA**, Bengali-first with an English toggle, professionally translated | portal `P01` · `UX-005` · `AS-12` | `P01` accepted | **`UX-005` governs at 2.2 AA and WCAG 2.2 is the current W3C Recommendation (verified 2026-08-19). The `P01` specification says 2.1 — building the 250,000-user customer surface to a weaker standard than the 250-user admin portal is backwards. `CR-D` raised.** **Not machine-translated.** Gate criterion: **online booking rate >= 60% at pilot sites** | `LL` | T02–T09 |

---

## `P05-M08` — `M10` Loyalty, and the `M64`, `M01`, `M17` completion slices

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P05-M08-T01` | Build `M10` privilege programme, points and vouchers | `M10` · `CD-M10-nn` | Loyalty module | 44 requirements, 18 PW | `OD` | — |
| `P05-M08-T02` | Implement the **`M10 -> M11`/`M20` stub** — accrual rules are self-contained in W2; redemption against price and invoice connects in W3 | `AR-006` §5.4 STUB | Stub + `GV-005` registration | With an expiry date | `SA` | T01 |
| `P05-M08-T03` | Build campaign support for loyalty | `M10` · `M35` | Campaign hooks | `M35` marketing lands in W5; build the seam | `OD` | T01 |
| `P05-M08-T04` | Complete `M64` — the rest of MDM beyond the W1 governance core | `M64` · `MV-04` | `M64` complete | 26 requirements, 14 PW | `OD` | — |
| `P05-M08-T05` | Complete `M01` — the W2 slice: business-line extensions `FR-SRM-063`…`FR-SRM-088` | `M01` · `05-01` §3.1 | `M01` complete | Rental intake, swap-out, and the rest of the deferred block | `OD` | — |
| `P05-M08-T06` | Complete `M17` — the W2 slice beyond the registry core | `M17` | `M17` complete | — | `OD` | — |
| `P05-M08-T07` | Verify the **28 allocated-but-unused requirement IDs** in `M01`, `M02` and `M31` are closed out or reallocated | `02-02` §3.1 `H2-03` | Corrected requirement register | Counts taken from the highest ID rather than the actual count | `BA` | T05 |
| `P05-M08-T08` | Emit and register all events for `M10`, `M64`, `M01` and `M17` completion | `AS-08` · `IN-003` | Registered events | — | `OD` | T01–T06 |
| `P05-M08-T09` | Burn down the `AR-012` `Warning` fitness functions promoted at `G1`, and enable the **W2 check set**: `FF-01`, `FF-05`, `FF-07`, `FF-10`, `FF-11`, `FF-12`, `FF-17`, `FF-18`, `FF-24`, `FF-28`, `FF-29`, `FF-31`, `FF-34`, `FF-35`, `FF-36` | `AR-012` §10 | 15 further checks live | `FF-34` is the offline harness — it lands with `P02` | `CA` | — |
| `P05-M08-T10` | Complete all four to the full DoD | §0.8.2 | Accepted | — | `OD` | T01–T09 |

---

## `P05-M09` — Wave 2 migration and integrations

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P05-M09-T01` | Migrate **branch inventory** with reconciliation to a **physical count** | TSS §19.1 · `MG-003` | Inventory ETL | Not to a spreadsheet — to a physical count. Gate criterion: **inventory accuracy >= 95%** | `ML` | — |
| `P05-M09-T02` | Migrate the **service history archive** from the two legacy trackers | TSS §19.1 · `P01-M07-T03` | Service history ETL | With permanent legacy references (`MIG-03`) | `ML` | — |
| `P05-M09-T03` | Migrate open workshop WIP from paper job cards — **open WIP only, history not migrated** | TSS §19.1 | WIP capture | The non-migration ruling from `P01-M07-T06` applies | `ML` | — |
| `P05-M09-T04` | Run control totals and reconciliation on every W2 load | `MIG-02` · `MG-004` | Reconciliation record | Before acceptance, not after | `ML` | T01–T03 |
| `P05-M09-T05` | Integrate `INT-011` redundant SMS gateway | `05-03` §8 W2 | Redundant SMS | Fallback for `INT-010` | `IL` | — |
| `P05-M09-T06` | Integrate `INT-014` push notification | `05-03` §8 W2 · portal `P02`, `P01` | Push integration | — | `IL` | — |
| `P05-M09-T07` | Integrate `INT-019` mapping, `INT-020`/`INT-021` routing, `INT-022` traffic, `INT-023` GPS | `05-03` §8 W2 · `IN-004` ICDs | 5 integrations | Each with a documented, tested fallback | `IL` | `P05-M04-T03` |
| `P05-M09-T08` | Build the `IN-008` **sandbox environment** for external counterparty certification | `IN-008` · `PE-002` §5.10 | `sandbox` live | Externally reachable, externally credentialled, **synthetic only** | `DE` | T05–T07 |
| `P05-M09-T09` | Author and verify pacts for every W2 integration; the pact broker **fails closed** | `IN-008` `CT-02` · `PE-004` §5.3 `PS-01` | Verified pacts | A pact that cannot be verified is not a pact that passed | `IL` | T08 |
| `P05-M09-T10` | Withdraw paper service forms in Dhaka | `06-01` W2 gate | Paper withdrawal record | A gate criterion, and the clearest single signal of real adoption | `TR` | T01–T04 |

---

## `P05-M10` — Gate `G2` — Field operations go-live (`MS-04`, Month 8)

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P05-M10-T01` | Run the `T−6` entry criteria check | `GV-009` §9.2 | Entry record | — | `PM` | — |
| `P05-M10-T02` | `G2-01` **Technician app in daily use by all Dhaka technicians** | `06-01` W2 gate | Usage evidence | Measured usage, not deployment | `QA` | T01 |
| `P05-M10-T03` | `G2-02` **24-hour offline operation demonstrated with zero data loss** | `AR-010` · `TS-015` | Offline demonstration | **The single hardest technical requirement in the programme** | `QA` | T01 |
| `P05-M10-T04` | `G2-03` **Route optimisation reducing measured travel time by >= 15%** | `06-01` W2 gate | Measured comparison | Against a measured baseline, not an estimate | `QA` | T01 |
| `P05-M10-T05` | `G2-04` **Inventory accuracy >= 95% at migrated locations** | `06-01` W2 gate | Physical count evidence | — | `ML` | T01 |
| `P05-M10-T06` | `G2-05` **Online booking rate >= 60% at pilot sites** | `06-01` W2 gate · portal `P01` | Booking metrics | — | `QA` | T01 |
| `P05-M10-T07` | `G2-06` **Paper service forms withdrawn in Dhaka** | `06-01` W2 gate | Withdrawal record | — | `TR` | T01 |
| `P05-M10-T08` | Verify the **`L6` end-to-end suite is fully automated by W3** and journeys 1–3 are running nightly | `QA-001` `L6` · TSS §20.4 | E2E evidence | Journey 1 (book -> dispatch -> repair -> invoice -> pay -> close -> survey) tests from W3 | `QA` | T01 |
| `P05-M10-T09` | Run the `gate` profile — performance at **1.5x peak** including `NFR-056` GPS ingest, and DR drill evidence | `PE-004` stages 16–17 | Gate profile results | — | `DE` | T01 |
| `P05-M10-T10` | **Gate `G2`.** Steering signs. Publish the report and residual open items | `GV-009` | Signed `G2`; `MS-04` | — | `PM` | T02–T09 |

---
---

# PHASE 6
## MONEY, MOVEMENT & DOCUMENTS

### Wave 3 · Months 9–13 · 21.7 weeks · Sprints 19–29 · Gate `G3` · Milestone `MS-05`

---

## 6.0 Phase charter

| | |
|---|---|
| **Purpose** | Make the business bankable. Ledger, invoicing, tax, payments, procurement, logistics and the document platform |
| **Tiers** | `T4` complete, `T5` money, `T6` partial |
| **Modules** | `M19` FIN · `M20` ARB · `M52` APE · `M50` TRE · `M11` PRC · `M36` QTE · `M03` LOG · `M16` PRO · `M41` WMS · `M24` (full) · `M63` BPA — **11 per `02-02` §4.2, plus `M51-core` TAX moved in by `MV-03`** |
| **Portals** | `P05` Vendor & Supplier Portal · `P09` Logistics & Rider Application |
| **Technology entering service** | OpenTelemetry + Prometheus + Loki + Tempo · document generation (Bengali PDF) · pricing engine · OCR · reconciliation service · OCA `dms` · bKash, Nagad, SSLCOMMERZ connectors |
| **Effort** | 281 PW against ~152 effective PW — **1.85x over** |
| **Exit** | `G3` — 9 criteria, Month 13. This is `MS-05` |

> **`M19` is the ordering constraint within tier `T5`.** The general ledger is built first and
> everything else in the tier posts to it. Building AR before GL produces an invoicing module with
> nowhere to post.

> **`MV-03` is statutory, not convenient.** VAT determination and Mushak 6.3 issuance move from W4
> to W3 because the `G3` gate already requires *"Mushak invoices accepted without NBR exception"* —
> and an invoice cannot be raised before its VAT treatment is known. Monthly Mushak 9.1 returns are
> due **by the 15th** via the NBR VAT Online portal from this phase onward.

---

## `P06-M01` — `M19` Financial Accounting & General Ledger

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P06-M01-T01` | Install Odoo `account` and **OCA `account-financial-tools` (40+)** and `account-financial-reporting`, verified against `W0-01` | `M19` · TSS §20.2 W3 | Finance layer installed | `AS-05` | `OD` | — |
| `P06-M01-T02` | Build the **chart of accounts** for Bangladesh, from the `MD-*` finance and statutory content set | `M19` · `project_content` 02E Finance and Statutory | CoA loaded | Master data, not code | `CN` | T01 |
| `P06-M01-T03` | Build the multi-entity, multi-branch ledger on `M30`'s `fix.entity` and operating units | `M19` · `M30` · `AS-03` | Ledger structure | Cost centre and branch dimensions on every posting | `OD` | T02 |
| `P06-M01-T04` | Apply **`AS-10` absolutely**: every amount is `fields.Monetary` with an explicit `currency_id`. **Never `Float`** | `AS-10` · `FF-22` · `DI-01` | Monetary conformance | `FF-22` blocks pre-merge. There is no exception in the finance modules | `OD` | T03 |
| `P06-M01-T05` | Achieve **100% unit-test coverage on every financial calculation path** | `DoD-03` | Coverage report | 80% is the estate minimum; **financial and tax paths are 100%** | `QA` | T04 |
| `P06-M01-T06` | Build the period-close process targeting **month-end close within 5 days** | `M19` · `06-01` W3 gate | Close process | Gate criterion for the first full month | `OD` | T03 |
| `P06-M01-T07` | Build the fixed-asset seam that `M49` extends in Phase 8 | `M19` · `M49` | Fixed-asset hooks | — | `OD` | T03 |
| `P06-M01-T08` | Reconcile the **W2 inventory suspense account** from `P05-M01-T06` and close the registered stub | `AR-006` §5.4 · `P05-M01-T06` | Suspense reconciled; stub closed | **An unreconciled suspense balance across a wave boundary is a finance risk.** This is where it is cleared | `OD` | T03 |
| `P06-M01-T09` | Emit `M19` events and register them | `AS-08` · `IN-003` | Registered events | `journal.posted`, `period.closed` | `OD` | T03 |
| `P06-M01-T10` | Complete `M19` to the full DoD | §0.8.2 | `M19` accepted | — | `OD` | T01–T09 |

---

## `P06-M02` — `M51-core` VAT determination and Mushak 6.3 (`MV-03`)

**Statutory. Must exist when the first invoice is raised.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P06-M02-T01` | Read `M51` and the **VAT & Supplementary Duty Act 2012** obligations; verify currency and record the verified-on date | `M51` · TSS §14.6 · `SC-008` · `DoD-17` | Reading record; currency check | `DoD-17` — regulatory citations verified current | `BA` | — |
| `P06-M02-T02` | Build the **VAT determination service** — `determine_tax(line_set) -> treatment` | `M51` · `AR-006` §4.2 worked example | Determination service | **`M20 -> M51` is synchronous** because `M20` must know the VAT treatment before it can raise an invoice | `OD` | T01 |
| `P06-M02-T03` | Build **Mushak 6.3 tax-invoice issuance** with the statutory template | `M51` · `project_content` 05B Finance and Statutory | Mushak 6.3 generation | **Bengali rendering with correct conjunct shaping is a statutory requirement here, not a nicety** | `OD` | T02 |
| `P06-M02-T04` | Build the **Mushak register**, populated by consuming `invoice.created` — **never by calling `M20` back** | `AR-006` §4.1 pair 7, §4.2 | Event-driven register | **The cycle disappears, and `M51` can rebuild the VAT register from the event stream without `M20`'s cooperation** — the point that matters at month end | `OD` | T02 |
| `P06-M02-T05` | Build **TDS determination**, which `M52` calls synchronously | `M51` · `AR-006` §4.1 pair 8 | TDS service | Same shape: `M52` calls `M51`; `M51` consumes AP events | `OD` | T02 |
| `P06-M02-T06` | Declare the dependency against **`M30`'s `cd_country_pack`**, not against `M65` | `AR-006` §5.2 · `P03-M04-T04` | Corrected declaration | Closes a +5-wave violation | `SA` | T02 |
| `P06-M02-T07` | Achieve **100% test coverage on every tax calculation path** | `DoD-03` | Coverage report | Non-negotiable | `QA` | T02, T05 |
| `P06-M02-T08` | Implement **atomic posting** — the invoice-to-GL posting must be atomic with the Mushak register write | TSS §3.6.1 | Atomic transaction | **Or the VAT return will not reconcile.** One of the three fragile points in the service-to-cash flow | `OD` | T04, `P06-M01-T03` |
| `P06-M02-T09` | Defer VAT returns and filing to W4 explicitly, and record the deferral in the backlog | `AR-006` `MV-03` | Backlog entry | **Determination and issuance move to W3; returns and filing stay W4** | `BA` | T02 |
| `P06-M02-T10` | Complete `M51-core` to the full DoD | §0.8.2 | `M51-core` accepted | Gate criterion: **Mushak invoices accepted without NBR exception** | `OD` | T01–T09 |

---

## `P06-M03` — `M20` Accounts Receivable, Invoicing & Collections

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P06-M03-T01` | Build invoicing on Odoo `account`, extended | `M20` · `CD-M20-nn` | AR module | 36 requirements, 20 PW | `OD` | — |
| `P06-M03-T02` | Implement **automatic invoice generation from a closed job within 5 seconds** | `NFR-040` · TSS §3.6.1 | Auto-invoicing | Gate criterion: **100% of invoices generated automatically from closed jobs** | `OD` | T01, `P06-M02-T02` |
| `P06-M03-T03` | Call `M51`'s determination service synchronously; **consume nothing back from `M51`** | `AR-006` §4.2 | Correct call direction | The interface break, implemented | `OD` | T02 |
| `P06-M03-T04` | Break the **`M20 <-> M50` cycle**: `M50` publishes bank and cash events that `M20` consumes; **`M20` must not call `M50` synchronously** | `AR-006` §4.1 pair 6 | Interface break | — | `SA` | T01 |
| `P06-M03-T05` | Build collections, dunning and ageing | `M20` · `05-05` §7 | Collections engine | Dunning content from the `NT-*` set, Bengali and English | `OD` | T01 |
| `P06-M03-T06` | Build credit notes, refunds and adjustments with approval authority from `05-04` §7 | `M20` · `05-04` §7 | Adjustment flows | Approval authority is a segregation-of-duties control | `OD` | T01 |
| `P06-M03-T07` | Build the **document generation service** for Bengali PDF invoices and receipts | `CD-M20-nn` · TSS §20.2 W3 · `TR-07` | `services/document-generation/` | Compared against committed reference images, as `make doctor` check 10 does | `BE` | T01 |
| `P06-M03-T08` | Achieve 100% coverage on invoice calculation and rounding | `DoD-03` | Coverage report | Rounding is where money is lost silently | `QA` | T02 |
| `P06-M03-T09` | Emit `M20` events and register them | `AS-08` · `IN-003` | Registered events | `invoice.created`, `invoice.paid`, `credit_note.issued` | `OD` | T02 |
| `P06-M03-T10` | Complete `M20` to the full DoD | §0.8.2 | `M20` accepted | — | `OD` | T01–T09 |

---

## `P06-M04` — `M52` Accounts Payable and `M50` Treasury

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P06-M04-T01` | Build `M52` accounts payable on Odoo `account` + OCA | `M52` · `CD-M52-nn` | AP module | 28 requirements, 14 PW | `OD` | — |
| `P06-M04-T02` | Build **employee expense** on Odoo `hr_expense`, using `M21-core`'s employee master | `M52` · `M21-core` | Expense module | Enabled by `MV-01` — closes the `M52 -> M21` violation | `OD` | T01 |
| `P06-M04-T03` | Build **three-way match** in `M52` — **it belongs here, not in `M16`** | `AR-006` §4.1 pair 11 | `cd_three_way_match_ext` | **The seam belongs in `M52`, consuming `M16` and `M15` events.** Gate criterion: three-way matching blocks unmatched vendor invoices | `OD` | T01 |
| `P06-M04-T04` | Call `M51`'s TDS determination synchronously | `AR-006` §4.1 pair 8 | TDS integration | — | `OD` | T01, `P06-M02-T05` |
| `P06-M04-T05` | Build `M50` treasury, cash and banking | `M50` · `CD-M50-nn` | Treasury module | 30 requirements, 16 PW | `OD` | — |
| `P06-M04-T06` | Break the **`M50 <-> M52` cycle**: `M52` raises payment requests as **events**; `M50` executes and publishes confirmation. **No synchronous back-call** | `AR-006` §4.1 pair 9 | Interface break | — | `SA` | T05 |
| `P06-M04-T07` | Build bank reconciliation and cash-position reporting | `M50` · `05-05` §7 | Reconciliation | Consumes the `M04` cash-drawer model from Phase 4 | `OD` | T05 |
| `P06-M04-T08` | Build the **reconciliation service** for payment matching | `CD-M50-nn` · TSS §20.2 W3 | `services/reconciliation/` | Gate criterion: **payment auto-matching >= 90%** | `BE` | T07 |
| `P06-M04-T09` | Emit `M52` and `M50` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01, T05 |
| `P06-M04-T10` | Complete both to the full DoD, with 100% coverage on payment calculation | §0.8.2 · `DoD-03` | Accepted | — | `OD` | T01–T09 |

---

## `P06-M05` — Payment integrations and reconciliation

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P06-M05-T01` | Read `IN-007` payment gateway integration design and the `05-03` §2.1 payments catalogue | `IN-007` · `05-03` §2.1 | Reading record | 9 payment integrations in the catalogue | `IL` | — |
| `P06-M05-T02` | Integrate **`INT-001` bKash** using the L3 free connector, extended | `05-03` §8 W3 · TSS L3 | bKash integration | `DEP-16`-class external dependency — contracts and sandbox access must be live | `IL` | T01 |
| `P06-M05-T03` | Integrate **`INT-002` Nagad** | `05-03` §8 W3 | Nagad integration | — | `IL` | T01 |
| `P06-M05-T04` | Integrate **`INT-003` SSLCOMMERZ** card and bank | `05-03` §8 W3 | SSLCOMMERZ integration | — | `IL` | T01 |
| `P06-M05-T05` | Integrate `INT-004` bank statement feed and `INT-006` | `05-03` §8 W3 | Bank integrations | Feeds auto-reconciliation | `IL` | T01 |
| `P06-M05-T06` | Implement **idempotent payment confirmation** — a retried confirmation must not double-credit | `DI-04` · `IN-002` | Idempotency handling | Money is where idempotency defects cost most | `IL` | T02–T05 |
| `P06-M05-T07` | Build **auto-reconciliation** to >= 90% match rate | `06-01` W3 gate · `P06-M04-T08` | Reconciliation rules | Gate criterion | `BE` | T06 |
| `P06-M05-T08` | Implement the **fallback register** for every P0 payment integration | `05-03` §7 | Fallbacks | A payment gateway outage must degrade, not stop trading | `IL` | T06 |
| `P06-M05-T09` | Integrate `INT-024`–`INT-026` couriers, `INT-039` tax validation and `INT-044` OCR | `05-03` §8 W3 | 5 integrations | OCR service is `CD-M20-nn`-adjacent; deploy with document generation | `IL` | T01 |
| `P06-M05-T10` | Author and verify pacts for every W3 integration in the `sandbox` environment | `IN-008` · `PE-004` `PS-01` | Verified pacts | Fail closed | `IL` | T02–T09 |

---

## `P06-M06` — `M11` Pricing and `M36` Quotation

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P06-M06-T01` | Build `M11` price books and rate cards on `M37`'s catalogue kernel | `M11` · `M37` · `CD-M11-nn` | Pricing module | 36 requirements, W3/W7 split | `OD` | — |
| `P06-M06-T02` | Build the **pricing engine** as an L5 standalone service | `CD-M11-nn` · TSS §20.2 W3 · `AR-007` §3.1 `services/` | `services/pricing-engine/` | Pure computation, unit-testable without a database | `BE` | T01 |
| `P06-M06-T03` | Build discount governance and approval authority | `M11` · `05-04` §7 | Discount controls | A segregation-of-duties control, not a preference | `OD` | T01 |
| `P06-M06-T04` | Connect `M10` loyalty redemption against price, closing the W2 stub | `P05-M08-T02` | Stub closed | — | `OD` | T01 |
| `P06-M06-T05` | Build `M36` quotation and estimation | `M36` · `CD-M36-nn` | Quotation module | 32 requirements, 17 PW | `OD` | T01 |
| `P06-M06-T06` | Build tender management | `M36` | Tender module | Consumed by `P04` corporate portal in Phase 7 | `OD` | T05 |
| `P06-M06-T07` | Wire quotation to the `M01` estimate flow — one estimate concept, not two | `M01` · `AS-01` | Unified estimate | — | `OD` | T05, `P04-M03-T06` |
| `P06-M06-T08` | Defer the `M11` W7 dynamic-pricing slice explicitly | `02-02` Category C | Backlog entry | — | `BA` | T01 |
| `P06-M06-T09` | Emit `M11` and `M36` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01, T05 |
| `P06-M06-T10` | Complete both to the full DoD, with 100% coverage on price calculation | §0.8.2 · `DoD-03` | Accepted | Pricing is a financial path | `OD` | T01–T09 |

---

## `P06-M07` — `M03` Logistics, `M41` Warehouse, `M16` Procurement

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P06-M07-T01` | Build `M03` consignments and **chain of custody** | `M03` · `CD-M03-nn` | Logistics module | 42 requirements, 22 PW. Gate criterion: **pick & drop operating with unbroken chain of custody** | `OD` | — |
| `P06-M07-T02` | Build pick-and-drop collection and return delivery | `M03` · `M01` | Pick-and-drop flows | Journey 3 of the 15 critical journeys | `OD` | T01 |
| `P06-M07-T03` | Build reverse logistics for warranty, trade-in and e-waste flows | `M03` · `M09`, `M14`, `M18` | Reverse logistics | Consumed in Phases 7, 9 and 11 | `OD` | T01 |
| `P06-M07-T04` | Build `M41` warehouse management on OCA `stock-logistics-warehouse` | `M41` · `CD-M41-nn` | WMS module | 34 requirements, 20 PW | `OD` | — |
| `P06-M07-T05` | Downgrade **`M41 -> M44`** — landed cost applies at receipt valuation; **W3 receipts use standard cost** | `AR-006` §5.2 NOT-A-PREREQ | Corrected declaration; documented valuation change at W6 | Record the valuation change so W6 does not surprise finance | `SA` | T04 |
| `P06-M07-T06` | Build `M16` requisition, purchase order and receipt on Odoo `purchase` + **OCA `purchase-workflow` (25+)** | `M16` · `CD-M16-nn` | Procurement module | 32 requirements, 16 PW | `OD` | — |
| `P06-M07-T07` | Break the **`M16 <-> M42` cycle**: `M42` is a **read-and-score consumer** of `M16` events; `M16` reads scorecards through a published API. **Asymmetric, not mutual** | `AR-006` §4.1 pair 10 | Interface break | `M42` lands in W4 — build the seam now | `SA` | T06 |
| `P06-M07-T08` | Downgrade `M16 -> M42` — **vendor scorecards are advisory in W3** | `AR-006` §5.4 NOT-A-PREREQ | Corrected declaration | — | `SA` | T07 |
| `P06-M07-T09` | Emit all three modules' events and register them | `AS-08` · `IN-003` | Registered events | `consignment.created`, `custody.transferred`, `goods.received`, `po.approved` | `OD` | T01, T04, T06 |
| `P06-M07-T10` | Complete all three to the full DoD | §0.8.2 | Accepted | — | `OD` | T01–T09 |

---

## `P06-M08` — `M24` full DMS, `M63` process automation, observability

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P06-M08-T01` | Complete `M24` beyond the W1 kernel: templates, approval chains, legal hold | `M24` · `MV-02` | `M24` complete | The kernel moved to W1; the rest lands here | `OD` | — |
| `P06-M08-T02` | Build **e-signature envelopes** and integrate the L6 qualified e-signature component | `M24` · TSS §9 L6 | E-signature | CFO-approved L6 component with a written OSS alternative review | `OD` | T01 |
| `P06-M08-T03` | Build `M63` process automation and workflow orchestration over Apache Airflow | `M63` · `CD-M63-nn` | BPA module | 28 requirements, 16 PW. Closes the `M63 -> M27` violation — the notification platform is already W1 | `OD` | — |
| `P06-M08-T04` | Implement the **60 business automations** `AUT-001`…`AUT-060`, assigning each an execution engine | `05-05` §12 · TSS §12.8 | Automation register with engines | Every automation has a named engine: Odoo automated action, Apache Airflow workflow, or a domain service | `OD` | T03 |
| `P06-M08-T05` | Deploy the **full observability stack** — OpenTelemetry -> Prometheus + Loki + Tempo -> Grafana | TSS §17, §20.2 W3 · `PE-008` | Observability live | **A single correlation id across every hop** (`NFR-092`) | `DE` | — |
| `P06-M08-T06` | Instrument every service and module with OpenTelemetry traces, metrics and structured logs | `PE-008` · `NFR-092` | Instrumentation | Retrofitting instrumentation is far more expensive than adding it | `DE` | T05 |
| `P06-M08-T07` | Build the operational dashboards and alerting per `PE-008` and `SV-004` on-call design | `PE-008` · `SV-004` | Dashboards + alerts | Alert fatigue is a design defect | `DE` | T06 |
| `P06-M08-T08` | Deploy the **OCR service** and wire it to document intake | `CD-M24-nn` · TSS §20.2 W3 · `INT-044` | `services/ocr/` | Bengali OCR accuracy must be measured, not assumed | `BE` | T01 |
| `P06-M08-T09` | Enable the **W3 fitness function** `FF-33` — performance at 1.5x peak, now that representative volume exists | `AR-012` §10 | `FF-33` live | — | `CA` | T05 |
| `P06-M08-T10` | Complete `M24` and `M63` to the full DoD | §0.8.2 | Accepted | — | `OD` | T01–T09 |

---

## `P06-M09` — `P05` Vendor Portal and `P09` Rider Application

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P06-M09-T01` | Build `P05` on **Odoo Portal (QWeb) + Next.js** — runtime `R2` plus `R3` | portal `P05` · `UX-001` §3.1 | `P05` shell | `R2` is Bootstrap-derived SCSS in the `website` bundle; tokens generated, not authored | `FE` | — |
| `P06-M09-T02` | Build vendor RFQ response, PO acknowledgement and delivery confirmation | portal `P05` · `M16` | Vendor flows | — | `FE` | T01 |
| `P06-M09-T03` | Build vendor invoice submission feeding the `M52` three-way match | portal `P05` · `M52` | Invoice submission | Blocked if unmatched — the gate criterion | `FE` | T02, `P06-M04-T03` |
| `P06-M09-T04` | Build vendor onboarding from the `EO-*` ecosystem onboarding content set | portal `P05` · `project_content` 18 | Onboarding flows | 14 `EO` files | `CN` | T01 |
| `P06-M09-T05` | Build `P09` rider application in Flutter, **consuming `libs/dart/fix_offline`** | portal `P09` · `AR-010` `ADR-024` | `P09` app | **The engine is consumed, never re-implemented.** `FL-03` is review-only — the reviewer is the control | `MB` | `P05-M05-T02` |
| `P06-M09-T06` | Build consignment pickup, custody scanning and delivery confirmation | portal `P09` · `M03` | Rider flows | Unbroken chain of custody is the gate criterion | `MB` | T05 |
| `P06-M09-T07` | Build the rider route view over the route orchestrator | portal `P09` · `P05-M03-T04` | Route view | — | `MB` | T05 |
| `P06-M09-T08` | Build the `P09` **coordinator view** in Odoo Web OWL 2 — runtime `R1` | portal `P09` · `UX-001` §3.1 | Coordinator view | One portal, two runtimes — the component contract must hold across both | `FE` | T01 |
| `P06-M09-T09` | Achieve WCAG 2.2 AA and 100% Bengali on both surfaces | `UX-005` · `AS-12` | Accessibility + translation | — | `LL` | T02–T08 |
| `P06-M09-T10` | Complete both portals to the portal DoD | `05-01` §4 · §0.8.2 | Accepted | — | `FE` | T01–T09 |

---

## `P06-M10` — Gate `G3` — Financial control go-live (`MS-05`, Month 13)

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P06-M10-T01` | Run the `T−6` entry criteria check | `GV-009` §9.2 | Entry record | — | `PM` | — |
| `P06-M10-T02` | `G3-01` **100% of invoices generated automatically from closed jobs** | `06-01` W3 gate | Invoice automation evidence | Within 5 seconds (`NFR-040`) | `QA` | T01 |
| `P06-M10-T03` | `G3-02` **Payment auto-matching >= 90%** | `06-01` W3 gate | Match-rate evidence | — | `QA` | T01 |
| `P06-M10-T04` | `G3-03` **Mushak invoices accepted without NBR exception** | `06-01` W3 gate · `MV-03` | NBR acceptance evidence | **Statutory. Monthly Mushak 9.1 by the 15th** | `QA` | T01 |
| `P06-M10-T05` | `G3-04` **Month-end close completed within 5 days for the first full month** | `06-01` W3 gate | Close evidence | — | `QA` | T01 |
| `P06-M10-T06` | `G3-05` **Pick & drop operating with unbroken chain of custody** | `06-01` W3 gate | Custody evidence | — | `QA` | T01 |
| `P06-M10-T07` | `G3-06` **Three-way matching blocking unmatched vendor invoices** | `06-01` W3 gate | Blocking evidence | Negative-tested: an unmatched invoice must be **rejected**, not warned about | `QA` | T01 |
| `P06-M10-T08` | Verify **journeys 1, 2, 3 and 12** of the 15 critical journeys are automated and running nightly | TSS §20.4 · `QA-001` `L6` | E2E evidence | `L6` is **fully automated by W3** — this is the wave where that becomes true | `QA` | T01 |
| `P06-M10-T09` | Run the `gate` profile — performance at 1.5x peak, DR drill, full policy sweep | `PE-004` §4.2 | Gate results | — | `DE` | T01 |
| `P06-M10-T10` | **Gate `G3`.** Steering signs. Publish report and residuals | `GV-009` | Signed `G3`; `MS-05` | — | `PM` | T02–T09 |

---
---

# PHASE 7
## AGREEMENTS, BILLING, CONTACT CENTRE & ANALYTICS

### Wave 4 · Months 14–18 · 21.7 weeks · Sprints 30–40 · Gate `G4` · Milestone `MS-06`

---

## 7.0 Phase charter

| | |
|---|---|
| **Purpose** | Close the v1.0 commitment. Contracts, warranty, subscription billing, the contact centre, and the first analytics surface |
| **Tiers** | `T6` commercial, `T7` engagement |
| **Modules** | `M08` CTR · `M09` WTY · `M39` SUB · `M51` (completion) · `M53` (W4 slice) · `M27` CCE · `M32` CAI · `M34` CXM · `M25` BID · `M62` (W4 slice) · `M42` SRM2 — **11, plus `M07`'s W4 quotation/pricing slice (`P07-M01` onward), which `02-02` §4.2 omits entirely (§0.4.0)** |
| **Portals** | `P04` Corporate B2B · `P06` Analytics & Executive Dashboard · `P08` Brand Partner · `P10` Contact Centre Agent Console |
| **Technology** | Apache Superset · settlement engine · warehouse ETL (dbt) · DSR orchestrator · **L6 cloud telephony** · **L6 qualified e-signature** · OCA `contract`, `mis-builder`, `reporting-engine` · NBR e-VAT (`INT-038`) |
| **Effort** | **353 PW against ~169 effective PW — 2.09x over. The heaviest wave in the programme** |
| **Exit** | **`G4` — 10 criteria, Month 18. `MS-06`. v1.0 scope complete. Tranche boundary — Waves 5–9 are re-authorised here (`D-017`)** |

> **PDPA 2026 enforcement activates ~13 May 2027, inside this phase.** Complaint, investigation and
> penalty mechanisms come live. Penalties reach **BDT 25 lakh, or BDT 50 lakh for a significant data
> fiduciary**. **Compliance is a `G4` gate condition, not a Wave 5 activity.** Milestone `P07-M08`
> exists for that reason and cannot slip into Phase 8.

> **`G4` is where the programme is re-authorised.** Everything up to here is the v1.0 commitment
> restated. Everything after here was added in v2.0. A Steering Committee that has watched four
> waves run over capacity has a legitimate decision to take at this boundary, and the roadmap makes
> it an explicit stop rather than a rolling assumption.

---

## `P07-M01` — `M08` Contract Lifecycle Management

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P07-M01-T01` | Install **OCA `contract` (12 modules)**, verified against `W0-01` | `M08` · TSS §20.2 W4 | `contract` installed | `AS-05` | `OD` | — |
| `P07-M01-T02` | Build the contract engine covering **all product families** — AMC, RAMC, managed services, rental, marketplace | `M08` · `CD-M08-nn` | Contract module | 44 requirements, 24 PW | `OD` | T01 |
| `P07-M01-T03` | Build the **entitlement model** — what a contract buys, and how consumption is drawn down | `M08` · `M01` | Entitlement engine | `M01`'s W1 entitlement check consumes this | `OD` | T02 |
| `P07-M01-T04` | Build contract SLAs, distinct from and reconciled with `M01`'s service SLAs | `M08` · `M01` · `AS-01` | Contract SLA model | One SLA concept, two scopes — not two implementations | `OD` | T03 |
| `P07-M01-T05` | Build renewal, escalation and price-revision flows | `M08` · `M11` | Renewal engine | Journey 5: AMC sale -> activation -> preventive schedule -> visit -> renewal | `OD` | T02 |
| `P07-M01-T06` | Build the **preventive maintenance schedule** generator from contract terms | `M08` · `M02` | PM scheduler | Feeds dispatch | `OD` | T03 |
| `P07-M01-T07` | Wire contract documents and e-signature through `M24`'s envelope model | `M24` · `P06-M08-T02` | Contract e-signature | Through the kernel, not a local implementation | `OD` | T02 |
| `P07-M01-T08` | Resolve the multi-owned entity `fix.contract.cost` — claimed by `M08`, `M53` **and** `M54` | `AR-008` §2.2 · `P01-M04-T08` ruling | Single owner | `AR-005` requires exactly one owning module per capability | `SA` | T02 |
| `P07-M01-T09` | Emit `M08` events and register them | `AS-08` · `IN-003` | Registered events | `contract.activated`, `entitlement.consumed`, `contract.renewed` | `OD` | T02 |
| `P07-M01-T10` | Complete `M08` to the full DoD | §0.8.2 | `M08` accepted | — | `OD` | T01–T09 |

---

## `P07-M02` — `M09` Warranty, Protection Plans & Claims

**P0. 17+ brand partners, each with a different submission format.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P07-M02-T01` | Build warranty entitlement on `M17`'s device warranty status | `M09` · `M17` · `CD-M09-nn` | Warranty module | 48 requirements, 28 PW | `OD` | — |
| `P07-M02-T02` | Build warranty **products** — extensions and protection plans sold through `M37`'s catalogue | `M09` · `M37` | Warranty products | — | `OD` | T01 |
| `P07-M02-T03` | Implement **`AUT-018` — auto-create a claim within 24 hours** of a completed warranty job | `05-05` §12 · TSS §3.6.3 | Auto-claim automation | Gate criterion: **claims auto-created within 24 hours and submitted within 72** | `OD` | T01 |
| `P07-M02-T04` | Build the **evidence pack assembly**: photos, diagnostic, parts, serial, technician certification, purchase proof | `M09` · `M31` evidence pack · `M22` certification | Evidence assembly | Draws on the `M31` pack from Phase 5 | `OD` | T03 |
| `P07-M02-T05` | Implement the **completeness check that blocks submission if the pack is incomplete** | TSS §3.6.3 | Blocking completeness check | An incomplete claim is a rejected claim and a re-work cycle | `OD` | T04 |
| `P07-M02-T06` | Build the **Apache Airflow brand-submission workflows** — one per brand template | TSS §3.6.3 · `M63` | 17+ Apache Airflow workflows | **Why Apache Airflow and not custom code: the transformation is configuration that changes when a brand changes its template, not code that requires a release.** The claim record, the evidence pack and the reconciliation stay in Odoo, where the ledger is | `IL` | T05 |
| `P07-M02-T07` | Verify the **"17+ brands" figure** — it is unverified in the estate (`H2-12`) and each brand is a separate integration | `DEP-22` · `H2-12` | Verified brand count | An unverified counterparty count is an unverified effort estimate | `IL` | T06 |
| `P07-M02-T08` | Build claim-status webhooks and **remittance reconciliation**, flagging unmatched | TSS §3.6.3 · `IN-006` | Reconciliation | On approval, queue for billing; on remittance, match and post | `OD` | T06 |
| `P07-M02-T09` | Emit `M09` events and register them | `AS-08` · `IN-003` | Registered events | `warranty_claim.created`, `warranty_claim.submitted`, `warranty_claim.decided` | `OD` | T03 |
| `P07-M02-T10` | Complete `M09` to the full DoD | §0.8.2 | `M09` accepted | Gate criterion: **claim approval rate >= 90% on first submission** | `OD` | T01–T09 |

---

## `P07-M03` — `M39` Subscription and `M53` W4 revenue slice

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P07-M03-T01` | Build `M39` subscription and recurring revenue on OCA `contract` | `M39` · `CD-M39-nn` | Subscription module | 30 requirements, 17 PW | `OD` | — |
| `P07-M03-T02` | Build **consolidated B2B invoicing** — one invoice, many jobs, many sites | `M39` · `M20` · portal `P04` | Consolidated billing | A corporate client with 400 devices does not want 400 invoices | `OD` | T01 |
| `P07-M03-T03` | Build dunning and refund flows for subscriptions | `M39` · `M20` | Subscription dunning | — | `OD` | T01 |
| `P07-M03-T04` | Build the `M53` **W4 revenue-recognition slice** — the non-marketplace half | `M53` · `02-02` Category G W4/W7 split | Revenue recognition | 38 requirements, W4/W7 split | `OD` | — |
| `P07-M03-T05` | Correct the **`M53 -> M12` declaration** to target the **W7 slice**, not the W4 slice | `AR-006` §5.2 ACCEPT | Corrected declaration | **Register-level artefact, not a real violation.** The W4 slice does not need `M12` | `SA` | T04 |
| `P07-M03-T06` | Build commission calculation, ready for `M12` to feed it in Phase 10 | `M53` · `AR-006` §4.1 pair 12 | Commission engine | **Commission *calculation* is `M53`'s; commission *earning* is an `M12` event. `M12` must not call `M53`** | `OD` | T04 |
| `P07-M03-T07` | Build the **settlement engine** as an L5 standalone service | `CD-M53-nn` · TSS §20.2 W4 | `services/settlement-engine/` | **Commission and payout must post to the ledger.** A SaaS marketplace cannot be the system of record for money the Company owes to 5,000 sellers | `BE` | T06 |
| `P07-M03-T08` | Address `GV-004` §5.6 — **gate criterion `G7-02` requires "payout accuracy 100%", payout is settlement, and settlement is `M53`** | `GV-004` §5.6 · `PGD-A2-05` | Corrected wave allocation | The gate criterion tested a module the plan did not schedule. Fixing it here prevents a `G7` failure | `PM` | T04 |
| `P07-M03-T09` | Emit `M39` and `M53` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01, T04 |
| `P07-M03-T10` | Complete both to the full DoD, with **100% coverage on revenue and commission calculation** | §0.8.2 · `DoD-03` | Accepted | — | `OD` | T01–T09 |

---

## `P07-M04` — `M51` completion, VAT returns and NBR e-VAT

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P07-M04-T01` | Build **Mushak 9.1 monthly return preparation**, including the **holiday rollover** and **nil-return** rules | `M51` · TSS §14.6 · `SC-008` | Return preparation | **Due by the 15th; if the 15th is a holiday, the next working day. A nil return is still mandatory when there are no transactions** — which a multi-entity rollout will hit the month a new entity is registered. **Manual filing was abolished on 1 July 2026: online filing is the only route, so the `06-01` §9 "manual fallback" here means keying the NBR portal by hand, not a paper return.** State that in the runbook | `OD` | — |
| `P07-M04-T02` | Build VAT sub-ledgers and reconciliation to the GL | `M51` · `M19` | VAT sub-ledgers | Journey 15: month-end close -> reconciliation -> VAT return -> management pack | `OD` | T01 |
| `P07-M04-T03` | Integrate **`INT-038` NBR e-VAT** | `05-03` §8 W4 · `DEP-24` | e-VAT integration | **`DEP-24` is external — the NBR e-VAT specification must be obtained. Start it in Phase 1** | `IL` | T01 |
| `P07-M04-T04` | Build **TDS returns** — quarterly, due 25 Oct, 25 Jan, 25 Apr, 25 Jul | `M51` · `GV-004` §6.2 | TDS returns | Non-negotiable statutory dates | `OD` | — |
| `P07-M04-T05` | Build the withholding-tax certificate issuance flow | `M51` · `M52` | Certificate issuance | — | `OD` | T04 |
| `P07-M04-T06` | Verify every regulatory citation is current with a **verified-on date**, and re-verify against source | `DoD-17` · `SC-008` · `RR-005` | Currency verification | **Re-verify against upstream, not against the last document that verified it** | `BA` | T01 |
| `P07-M04-T07` | Build the statutory-report content set from `project_content` 05B | `project_content` 05B Finance and Statutory | Loaded statutory templates | **61 content files require legal or statutory sign-off** across the estate | `CN` | T01 |
| `P07-M04-T08` | Achieve **100% test coverage** on every return-calculation path | `DoD-03` | Coverage report | A wrong VAT return is a regulatory event, not a bug | `QA` | T01, T04 |
| `P07-M04-T09` | Emit `M51` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01 |
| `P07-M04-T10` | Complete `M51` to the full DoD | §0.8.2 | `M51` accepted | — | `OD` | T01–T09 |

---

## `P07-M05` — `M27` Contact Centre and `M32` Conversational AI

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P07-M05-T01` | Build `M27` omnichannel contact centre on OCA `helpdesk` (28 modules) | `M27` · `CD-M27-nn` | Contact centre module | 58 requirements, 32 PW. **Its notification half already shipped in W1 (`ADR-022`)** | `OD` | — |
| `P07-M05-T02` | Integrate **`INT-015` L6 cloud telephony (CPaaS)** | `05-03` §8 W4 · TSS §9 | Telephony integration | CFO-approved L6 component with a written OSS alternative review | `IL` | T01 |
| `P07-M05-T03` | Integrate `INT-018` chat and unify the channel model — voice, chat, email, WhatsApp, in-app | `M27` · `05-03` §8 W4 | Unified channels | Gate criterion: **hotline conversations captured in the system of record** | `IL` | T01 |
| `P07-M05-T04` | Build conversation capture, transcript storage and the customer 360 view | `M27` · `M33` | Conversation model | **`SC-003` DPIA records W2 transcript mining with no confirmed legal basis** — confirm the basis before mining, not after | `SL` | T03 |
| `P07-M05-T05` | Build `M32` conversational AI on **self-hosted Ollama** | `M32` · TSS §1.4 decision 8 · `CD-M32-nn` | AI assistant | **Customer conversation data must not leave the Company under PDPA transfer restrictions.** Open-weight Bengali-capable models remove per-query cost at 250,000 customer interactions a month | `BE` | T04 |
| `P07-M05-T06` | Launch `M32` with **transactional intents only** — the `M61` knowledge base is W6 | `AR-006` §5.4 ACCEPT with scope reduction · `02-02` `Q-01` | Scoped intent set | **Already a Steering decision.** An assistant without a knowledge base can answer transactional questions from live ERP data but not "how do I" or "why is this happening" | `SA` | T05 |
| `P07-M05-T07` | Build the human-handoff path with full context transfer | `M32` · `M27` | Handoff flow | Gate criterion: **AI assistant resolving >= 40% of first contacts** — the other 60% must hand off cleanly | `BE` | T06 |
| `P07-M05-T08` | Build Bengali and English intent handling, tested with real Bengali utterances | `M32` · `UX-007` · `BN-*` | Bilingual NLU | Not machine-translated training data | `LL` | T06 |
| `P07-M05-T09` | Keep the `M27 <-> M32` co-design pair as **one squad, one increment** | `AR-006` §4.1 pair 16 | Joint increment | Legitimate co-design, same wave | `SA` | T01, T05 |
| `P07-M05-T10` | Complete both to the full DoD | §0.8.2 | Accepted | — | `OD` | T01–T09 |

---

## `P07-M06` — `M34` Customer Experience and `M42` Supplier Performance

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P07-M06-T01` | Build `M34` feedback, survey and rating capture | `M34` · `CD-M34-nn` | CX module | 42 requirements, 17 PW | `OD` | — |
| `P07-M06-T02` | Build the **complaint** model with lifecycle and escalation | `M34` · `05-05` | Complaint model | Journey 14: complaint -> non-conformance -> root cause -> CAPA -> verification -> closure | `OD` | T01 |
| `P07-M06-T03` | Implement the **`M34 -> M23` stub** — complaint and NCR linkage stubs until W5 | `AR-006` §5.4 STUB | Stub + `GV-005` registration | With an expiry date | `SA` | T02 |
| `P07-M06-T04` | Build survey triggering from `service_order.closed` events | `M34` · `AS-08` | Survey automation | Journey 1 ends here | `OD` | T01 |
| `P07-M06-T05` | Build `M42` supplier relationship and performance | `M42` · `CD-M42-nn` | Supplier performance | 26 requirements, 13 PW | `OD` | — |
| `P07-M06-T06` | Implement `M42` as a **read-and-score consumer of `M16` events**, publishing scorecards through an API | `AR-006` §4.1 pair 10 · `P06-M07-T07` | Asymmetric interface | The break designed in Phase 6, implemented here | `OD` | T05 |
| `P07-M06-T07` | Implement the **`M42 -> M23` stub** | `AR-006` §5.4 STUB | Stub + registration | — | `SA` | T05 |
| `P07-M06-T08` | Record that **`05-05` registers no business rules for `M40` and `M42`** — `FF-53` will report zero coverage | `PE-004` §10 `FG-04` | Recorded finding | **A true finding that should not block a developer's pull request on the day the gate is switched on** | `CA` | T05 |
| `P07-M06-T09` | Emit `M34` and `M42` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01, T05 |
| `P07-M06-T10` | Complete both to the full DoD | §0.8.2 | Accepted | — | `OD` | T01–T09 |

---

## `P07-M07` — `M25` Business Intelligence and the `M62` W4 data slice

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P07-M07-T01` | Deploy **Apache Superset** and the read-replica connection | TSS §20.2 W4 · `M25` | Apache Superset live | Reads from a replica, never the primary | `DE` | — |
| `P07-M07-T02` | Install **OCA `mis-builder` and `reporting-engine`** | `M25` · TSS §20.2 W4 | Reporting layer | — | `OD` | — |
| `P07-M07-T03` | Build the **`M62` W4 slice** — the dimensional model over the read replica | `M62` · `DA-007` analytical model | Dimensional model | ClickHouse arrives in W8; W4 runs on the replica | `DA` | T01 |
| `P07-M07-T04` | Build the **warehouse ETL with dbt** | `CD-M62-nn` · TSS §20.2 W4 | dbt project | Conformed dimensions and fact tables per `05-02` §9 | `DA` | T03 |
| `P07-M07-T05` | Build the executive, branch, technician, finance and warranty dashboards | `M25` · portal `P06` | 5 dashboard sets | — | `DA` | T03 |
| `P07-M07-T06` | **Instrument and surface the 95 registered KPIs**, and reconcile the 250 in use | `BM-002` · `DoD-09` | KPI register live in `M25` | Every module delivered so far must have its `KPI-nnn` visible here (`DoD-09`) | `DA` | T05 |
| `P07-M07-T07` | Verify `NFR-039` analytical query performance at **1.5x peak** | `NFR-039` · `DoD-14` | Performance evidence | — | `QA` | T05 |
| `P07-M07-T08` | Apply `AR-001` `LB-06` — **`T11` intelligence is read-only downstream**. No analytics module writes to an OLTP model | `AR-001` `LB-06` · `AS-01` | Read-only enforcement | — | `CA` | T03 |
| `P07-M07-T09` | Load the **16 `RP-*` reporting and KPI content files** | `project_content` 14 Reporting, Analytics and KPI | Loaded report content | Metric definitions are content, not code | `CN` | T05 |
| `P07-M07-T10` | Complete `M25` and the `M62` W4 slice to the full DoD | §0.8.2 | Accepted | — | `DA` | T01–T09 |

---

## `P07-M08` — PDPA compliance completion — **enforcement lands inside this phase**

**~13 May 2027. This milestone cannot slip into Phase 8.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P07-M08-T01` | Re-verify the **PDPA citation chain** against source: Ordinance 2025 (gazetted 6 Nov 2025) -> Amendment Ordinance No. 23 of 2026 (5 Feb 2026) -> enacted April 2026 -> enforcement ~13 May 2027; regulator **National Data Management Authority** | `SC-008` · alignment audit §5 · `DoD-17` | Verified citation chain | Verify against upstream, not against the last document | `SL` | — |
| `P07-M08-T02` | Build the **DSR orchestrator** — the data-subject-request service | `CD-M29-nn` · TSS §3.6.4, §20.2 W4 | `services/dsr-orchestrator/` | Access, rectification, portability, erasure, objection | `SL` | T01 |
| `P07-M08-T03` | Complete the **portable machine-readable export**, assembling regional and resident data through the residency service | TSS §3.6.4 · `P03-M09-T09` | Export path complete | — | `SL` | T02 |
| `P07-M08-T04` | Build the **erasure saga with compensating actions** across the regional primary, the resident store, every read replica, the warehouse, the object store, the search index and backups-in-scope | TSS §3.6.4 · `DA-006` · `P01-M06-T09` | Erasure saga | **It is a saga, not a `DELETE`** | `SL` | T02 |
| `P07-M08-T05` | Preserve the **statutory processing record for five years** through erasure | `NFR-095` | Retained processing record | The one thing erasure must **not** remove | `SL` | T04 |
| `P07-M08-T06` | Implement **controller-side consumer notification within 30 days** | `NFR-093` | Notification flow | — | `SL` | T04 |
| `P07-M08-T07` | Implement **breach notification to the National Data Management Authority** and the incident path | `SC-011` · TSS §14.3 | Breach notification runbook | Rehearsed, not documented | `SL` | T01 |
| `P07-M08-T08` | Complete the **consent and transparency infrastructure** started in Phase 3 | `M33` consent registry · TSS §14.3 | Consent complete | — | `SL` | `P03-M05-T07` |
| `P07-M08-T09` | Re-run and sign the **`SC-003` DPIA** against the delivered system | `SC-003` | Signed DPIA | Against what was built, not what was designed | `SL` | T02–T08 |
| `P07-M08-T10` | Run a **PDPA readiness assessment as a `G4` gate criterion** | `GV-009` · `SC-008` | Readiness assessment | **Penalties: BDT 25 lakh, or BDT 50 lakh for a significant data fiduciary.** This is a gate item, not a workstream | `SL` | T09 |

---

## `P07-M09` — Portals `P04`, `P06`, `P08`, `P10`

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P07-M09-T01` | Build **`P04` Corporate B2B Portal** (Next.js, `R3`) — asset estates, consolidated invoicing, service requests at scale | portal `P04` · `M39` · `M08` | `P04` live | 500–2,000 users. Gate criterion: **10+ corporate clients transacting** | `FE` | — |
| `P07-M09-T02` | Build `P04` multi-site, multi-user account administration on `fix.party.hierarchy` | portal `P04` · `M33` | Account administration | — | `FE` | T01 |
| `P07-M09-T03` | Build **`P08` Brand Partner Portal** (Next.js, `R3`) — claim submission, status, reconciliation | portal `P08` · `M09` | `P08` live | 17+ brand partners, 50–150 users | `FE` | `P07-M02-T06` |
| `P07-M09-T04` | Build **`P10` Contact Centre Agent Console** (Next.js, `R3`) — unified queue, customer 360, call control | portal `P10` · `M27` | `P10` live | 30–80 agents | `FE` | `P07-M05-T03` |
| `P07-M09-T05` | Build **`P06` Analytics & Executive Dashboard** — Apache Superset + Grafana embedded, runtime `R5` | portal `P06` · `M25` | `P06` live | **`R5` conformance is partial and declared**: colour tokens full, type tokens partial, component contract not applicable | `DA` | `P07-M07-T05` |
| `P07-M09-T06` | Address the **69 of 102 portal-consumed events that no module publishes** for these four portals | `IN-003` · `B-17` | Event reconciliation | Three dispositions per event: rename, project, or register. **67.6% is not a rounding error** | `IL` | T01–T05 |
| `P07-M09-T07` | Author the OpenAPI operations these four portals consume, burning down the 1,152 outstanding | `IN-002` · `B-16` | Authored contracts | Report the burn-down at the gate | `IL` | T01–T05 |
| `P07-M09-T08` | Run the **`PS-11` portal contract test** on every new portal — an invalid payload posted directly to the API must be rejected | `AS-09` · `PS-11` | Contract tests green | The proof that business rules are not in portal code | `IL` | T07 |
| `P07-M09-T09` | Achieve WCAG 2.2 AA and 100% Bengali on all four surfaces, with the cross-runtime conformance suite green | `UX-005` · `AS-12` · `UX-001` §11 | Conformance evidence | — | `LL` | T01–T05 |
| `P07-M09-T10` | Complete all four to the portal DoD | `05-01` §4 · §0.8.2 | Accepted | — | `FE` | T01–T09 |

---

## `P07-M10` — Gate `G4` — v1.0 scope complete (`MS-06`, Month 18)

**Tranche boundary. Waves 5–9 are re-authorised here under `D-017`.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P07-M10-T01` | Run the `T−6` entry criteria check | `GV-009` §9.2 | Entry record | — | `PM` | — |
| `P07-M10-T02` | `G4-01` **Warranty claims auto-created within 24 hours and submitted within 72** | `06-01` W4 gate | Claim timing evidence | — | `QA` | T01 |
| `P07-M10-T03` | `G4-02` **Claim approval rate >= 90% on first submission** | `06-01` W4 gate | Approval-rate evidence | — | `QA` | T01 |
| `P07-M10-T04` | `G4-03` **10+ corporate clients transacting on the B2B portal** | `06-01` W4 gate | Transaction evidence | Real clients, real transactions | `QA` | T01 |
| `P07-M10-T05` | `G4-04` **Hotline conversations captured in the system of record** | `06-01` W4 gate | Capture evidence | — | `QA` | T01 |
| `P07-M10-T06` | `G4-05` **AI assistant resolving >= 40% of first contacts** | `06-01` W4 gate | Resolution-rate evidence | Measured against handoffs, not against sessions | `QA` | T01 |
| `P07-M10-T07` | `G4-06` **PDPA compliance verified** — DSR, erasure, consent, breach notification all operational | `P07-M08` · `SC-008` | Compliance evidence | **Enforcement is live. This is not a documentation criterion** | `SL` | T01 |
| `P07-M10-T08` | Verify **journeys 4, 5 and 15** are automated and running nightly | TSS §20.4 | E2E evidence | Warranty claim to reimbursement; AMC lifecycle; month-end close to VAT return | `QA` | T01 |
| `P07-M10-T09` | Produce the **v1.0 scope-completion statement**: every v1.0 commitment mapped to delivered capability, with gaps named | `06-01` §1 v1.0 protection table · `BRD` §20 | Scope-completion statement | The whole point of this gate | `PM` | T02–T08 |
| `P07-M10-T10` | **Gate `G4` and the tranche decision.** Steering re-authorises Waves 5–9, re-scopes, or stops | `GV-009` §8.3 · `D-017` | Signed `G4`; `MS-06`; tranche decision | **A Committee that has watched four waves run 1.85x–2.53x over capacity has a legitimate decision to take here.** The roadmap makes it an explicit stop | `PM` | T09 |

---
---

# PHASE 8
## PEOPLE, PAYROLL, QUALITY & MANAGED SERVICES

### Wave 5 · Months 19–22 · 17.4 weeks · Sprints 41–49 · Gate `G5` · Milestone `MS-07`

---

## 8.0 Phase charter

| | |
|---|---|
| **Purpose** | Complete the workforce estate, close the quality and certification stubs opened in Waves 2–4, and launch managed services |
| **Tiers** | `T8` workforce and quality, `T9` partial |
| **Modules** | `M21` (full) · `M55` WFM · `M56` PAY · `M57` PIC · `M22` LMS · `M23` QMS · `M05` RMS · `M45` EAM · `M46` FLT · `M49` FXA — **10 per TSS §20.2, plus `M35` MKT, which `02-02` §2 places in W5 and `02-02` §4.2 omits entirely (§0.4.0)** |
| **Portals** | `P11` Field Auditor & Quality Application (Flutter) |
| **Technology** | Mayan EDMS + document migration · MeshCentral/RustDesk · Wazuh · osquery · RMM collector · Odoo `hr`, `hr_attendance`, `hr_holidays`, `hr_expense`, `maintenance` · OCA hr/payroll (50+), `management-system` (33) · BEFTN (`INT-005`) · biometric devices (`INT-041`) |
| **Effort** | 247 PW against ~136 effective PW — **1.82x over** |
| **Exit** | `G5` — 7 criteria, Month 22. This is `MS-07` |

> **Category H carried the largest requirement variance in the programme: +52% against estimate,
> 310 requirements against 204.** The cause is **statutory density** — Bangladesh income tax,
> provident fund, gratuity, Labour Act employment artefacts, Labour Rules safety obligations and
> PDPA data-subject obligations generate requirements that operational categories do not carry.
> Plan this phase against **310, not 204**.

> **This is the phase where stubs come due.** `M02 -> M22` certification, `M31 -> M22`,
> `M31 -> M23`, `M34 -> M23`, `M42 -> M23`, `M02 -> M55` availability. Every one was registered in
> `GV-005` with an expiry date. **Closing them is not optional work that can slip — a stub that
> outlives its expiry is a control that has silently been off for three waves.**

---

## `P08-M01` — `M21` Core HR complete

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P08-M01-T01` | Install Odoo `hr`, `hr_holidays` and the **OCA hr set**, verified against `W0-01` | `M21` · TSS §20.2 W5 | HR layer installed | The employee master already exists from `MV-01` | `OD` | — |
| `P08-M01-T02` | Build the full employee lifecycle beyond the W1 master slice | `M21` · `CD-M21-nn` | `M21` complete | 46 requirements, 18 PW | `OD` | T01 |
| `P08-M01-T03` | Build organisation structure, reporting lines and position management | `M21` | Org model | — | `OD` | T02 |
| `P08-M01-T04` | Build leave and absence management on `hr_holidays`, per the **Bangladesh Labour Act 2006** | `M21` · `SC-008` | Leave management | Statutory leave entitlements, verified current | `OD` | T02 |
| `P08-M01-T05` | Build employment-contract artefacts required by the Labour Act | `M21` · `M24` templates | Employment artefacts | Statutory density — this is where the +52% variance lives | `OD` | T02 |
| `P08-M01-T06` | Verify the W1 joiner/mover/leaver event set still drives `M29` provisioning correctly at full scale | `P03-M08-T04` · `KPI-090` | Provisioning verification | Four waves of production use — verify, do not assume | `SL` | T02 |
| `P08-M01-T07` | Route all employee PII through the residency service | `SC-007` · `FF-09` | Residency conformance | NID, TIN, biometric templates | `SL` | T02 |
| `P08-M01-T08` | Complete the **55 reciprocity corrections** where `M21` is the target (11 of them) | `AR-006` §7.1 · `FF-14` | Corrected declarations | — | `SA` | T02 |
| `P08-M01-T09` | Emit `M21` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T02 |
| `P08-M01-T10` | Complete `M21` to the full DoD | §0.8.2 | `M21` accepted | — | `OD` | T01–T09 |

---

## `P08-M02` — `M55` Time, Attendance & Workforce Scheduling

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P08-M02-T01` | Build time and attendance on Odoo `hr_attendance` | `M55` · `CD-M55-nn` | Attendance module | 52 requirements, 22 PW | `OD` | — |
| `P08-M02-T02` | Integrate **`INT-041` biometric devices** | `05-03` §8 W5 | Biometric integration | **Biometric templates are `S3` residency-classified data** — route through Z4 | `IL` | T01 |
| `P08-M02-T03` | Build shift and roster management, and **close the `M02 -> M55` availability stub** | `M55` · `P05-M03-T05` | Roster + stub closed | The W2 stub returned "available within working calendar" from `M30`. Now it returns the real roster | `OD` | T01 |
| `P08-M02-T04` | Build working-time compliance per the Labour Act — hours, overtime, rest periods | `M55` · `SC-008` | Compliance rules | Statutory | `OD` | T01 |
| `P08-M02-T05` | Build the **attendance lock** that payroll depends on | `M55` · `M56` | Attendance lock | Journey 13: payroll cycle -> attendance lock -> calculation -> approval -> BEFTN -> payslips -> posting | `OD` | T01 |
| `P08-M02-T06` | Integrate technician shift clock-in/out from `P02`'s geofenced flow | `P02` · `P05-M06-T02` | Mobile attendance | Already built in the app; wired to the module here | `MB` | T01 |
| `P08-M02-T07` | Migrate **opening balances only** from attendance sign-in books — **history is not migrated** | TSS §19.1 · `P01-M07-T06` | Opening balances | The non-migration ruling applies | `ML` | T01 |
| `P08-M02-T08` | Route biometric templates through the residency service | `SC-007` · `FF-09` | Residency conformance | — | `SL` | T02 |
| `P08-M02-T09` | Emit `M55` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01 |
| `P08-M02-T10` | Complete `M55` to the full DoD | §0.8.2 | `M55` accepted | — | `OD` | T01–T09 |

---

## `P08-M03` — `M56` Payroll, Benefits & Statutory Compliance

**P0. The only P0 module in Category H.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P08-M03-T01` | Install the **OCA payroll set** and verify v19 status — this is a known migration-exposure area | `M56` · `W0-01` · `AR-007` §5.5 | Payroll layer | If v19 support is incomplete, this is a Phase 1 finding surfacing late — escalate, do not fork | `OD` | — |
| `P08-M03-T02` | Build the payroll engine | `M56` · `CD-M56-nn` | Payroll module | 54 requirements, 26 PW | `OD` | T01 |
| `P08-M03-T03` | Implement **Bangladesh income tax** calculation and withholding | `M56` · `M51` · `SC-008` | Income tax rules | **100% test coverage** (`DoD-03`) | `OD` | T02 |
| `P08-M03-T04` | Implement **provident fund, gratuity and voluntary-resignation compensation** under the **Bangladesh Labour (Amendment) Act 2026** — not the unamended 2006 Act | `M56` · `SC-008` · `DoD-17` · **§0.7.4** | PF, gratuity and resignation-compensation rules | **Verified 2026-08-19. Gratuity: 30 days' basic per completed year to 12 years, 45 days' above 12. Voluntary resignation now compensable — 7/15/30 days' wages per year by service band, where previously nothing was payable. New statutory PF duties: contribution structure, trust governance, reporting timelines.** The estate cites only "Labour Act 2006 (as amended)" and names none of these. **A legacy Excel payroll being migrated contains none of them** | `OD` | T02 |
| `P08-M03-T05` | Integrate **`INT-005` BEFTN**, and model its **batch window** in the payroll calendar | `05-03` §8 W5 · `M55` working calendar | BEFTN integration + cut-off-aware schedule | **BEFTN is batch-processed, not instant.** Submissions after the daily cut-off, or on **Friday, Saturday or a public holiday**, process the next working day. A payroll run that misses the cut-off pays 500+ staff late. The Bangladesh working week is **Sunday–Thursday** (`BN-007` `BD-01`) | `IL` | T02 |
| `P08-M03-T06` | Build payslip generation in **Bengali**, compared against committed reference images | `M56` · `TR-07` · `project_content` 05B | Payslip generation | **`TR-07` names payslips explicitly as a Bengali-rendering failure mode** | `LL` | T02 |
| `P08-M03-T07` | Build payroll GL posting to `M19` | `M56` · `M19` | GL posting | — | `OD` | T02 |
| `P08-M03-T08` | Migrate the employee master, **YTD balances and statutory balances** | TSS §19.1 | Payroll migration | Not transaction history — balances | `ML` | T02 |
| `P08-M03-T09` | Achieve **100% test coverage on every payroll calculation path** and negative-test the approval chain | `DoD-03` · `DoD-04` · `05-04` §6 SoD | Coverage + SoD tests | Payroll is the highest-consequence financial path in the estate | `QA` | T03–T07 |
| `P08-M03-T10` | Complete `M56` to the full DoD | §0.8.2 | `M56` accepted | — | `OD` | T01–T09 |

---

## `P08-M04` — `M57` Performance, Incentives & Compensation

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P08-M04-T01` | Build the performance-management model | `M57` · `CD-M57-nn` | Performance module | 42 requirements, 16 PW | `OD` | — |
| `P08-M04-T02` | Build the **technician scorecard**, surfaced in `P02` | `M57` · portal `P02` | Scorecard | The app already exposes it; the model lands here | `OD` | T01 |
| `P08-M04-T03` | Build the incentive calculation engine | `M57` · `M56` | Incentive engine | Feeds payroll | `OD` | T01 |
| `P08-M04-T04` | Build the earnings tracker surfaced in `P02` | `M57` · portal `P02` | Earnings tracker | — | `OD` | T03 |
| `P08-M04-T05` | Build compensation review and banding | `M57` | Compensation model | — | `OD` | T01 |
| `P08-M04-T06` | Apply field-level permissions — **compensation data is `T5`-tier** | `05-04` §4–§5 · `AS-14` | Field permissions | Negative-tested per role (`DoD-07`) | `SL` | T05 |
| `P08-M04-T07` | Achieve 100% coverage on incentive calculation | `DoD-03` | Coverage report | It pays people | `QA` | T03 |
| `P08-M04-T08` | Build `M35` marketing, campaigns and demand generation | `M35` · `02-02` Category B W5 | Marketing module | 40 requirements, 17 PW. Consumes `M10`'s campaign hooks from Phase 5 | `OD` | — |
| `P08-M04-T09` | Emit `M57` and `M35` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01, T08 |
| `P08-M04-T10` | Complete both to the full DoD | §0.8.2 | Accepted | — | `OD` | T01–T09 |

---

## `P08-M05` — `M22` Learning, Competency & Certification — closing the stubs

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P08-M05-T01` | Build the learning-management model | `M22` · `CD-M22-nn` | LMS module | 40 requirements, 16 PW. **Status is Re-scoped, not Retained** — technical knowledge content moved to `M61` | `OD` | — |
| `P08-M05-T02` | Build the **competency and certification register** with expiry tracking | `M22` | Certification register | — | `OD` | T01 |
| `P08-M05-T03` | Build **`FR-LMS-039` — the dispatch eligibility check** | `M22` · `02-02` Category H note | Eligibility service | The reason `M22` is Re-scoped rather than Retained | `OD` | T02 |
| `P08-M05-T04` | **Close the `M02 -> M22` stub** — connect the real eligibility check into the live assignment path | `AR-006` §5.2 · `P05-M03-T05` | Stub closed | **Retrofitting a blocking check into a live assignment path is materially riskier than building the seam early** — which is exactly why the seam was built in W2 | `OD` | T03 |
| `P08-M05-T05` | **Close the `M31 -> M22` stub** | `P05-M02-T05` | Stub closed | — | `OD` | T03 |
| `P08-M05-T06` | Verify **no stub outlived its `GV-005` expiry date**; report any that did as an incident, not a task | `GV-005` · §0.9 | Stub audit | **A stub that always returned "eligible" was a control that did not work, for three waves.** Say so | `SA` | T04, T05 |
| `P08-M05-T07` | Accept the `M22 -> M61` dependency gap — course-content authoring degrades without the knowledge base but is not blocking | `AR-006` §5.4 ACCEPT | Accepted degradation | Named, not discovered | `SA` | T01 |
| `P08-M05-T08` | Load the **24 `TR-*` training content files** and the `08B` course packs | `project_content` 08 Training and Enablement | Loaded courses | — | `CN` | T01 |
| `P08-M05-T09` | Emit `M22` events and register them | `AS-08` · `IN-003` | Registered events | `certification.granted`, `certification.expired` | `OD` | T02 |
| `P08-M05-T10` | Complete `M22` to the full DoD | §0.8.2 | `M22` accepted | — | `OD` | T01–T09 |

---

## `P08-M06` — `M23` Quality Management System — closing the stubs

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P08-M06-T01` | Install **OCA `management-system` (33 modules)** | `M23` · TSS §20.2 W5 | Management system layer | — | `OD` | — |
| `P08-M06-T02` | Build the **non-conformance (NCR)** model | `M23` · `CD-M23-nn` | NCR module | 32 requirements, 16 PW | `OD` | T01 |
| `P08-M06-T03` | Build **root cause and CAPA** with verification and closure | `M23` · `05-05` §10 | CAPA engine | Journey 14 completes here | `OD` | T02 |
| `P08-M06-T04` | Take over QC checklist ownership from `M01` and **close the `M31 -> M23` stub** | `P04-M03-T07` · `P05-M02-T06` | Ownership transfer; stub closed | `AR-005` — exactly one owning module | `OD` | T03 |
| `P08-M06-T05` | **Close the `M34 -> M23` and `M42 -> M23` stubs** | `P07-M06-T03`, `P07-M06-T07` | Stubs closed | — | `OD` | T03 |
| `P08-M06-T06` | Build ISO 9001:2015 audit support — **`CON-11` requires zero major non-conformances traced to systems** at annual surveillance | `M23` · `CON-11` · `GV-004` §6.2 | Audit support | An annual, non-negotiable external date | `OD` | T03 |
| `P08-M06-T07` | Build the internal audit programme model, consumed by `P11` | `M23` · portal `P11` | Audit programme | — | `OD` | T02 |
| `P08-M06-T08` | Load the **34 `SP-*` process and SOP content files** | `project_content` 06 Process, SOP and Workflow | Loaded SOPs | Including `SP-006`, the SoD register of record | `CN` | T02 |
| `P08-M06-T09` | Emit `M23` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T02 |
| `P08-M06-T10` | Complete `M23` to the full DoD | §0.8.2 | `M23` accepted | — | `OD` | T01–T09 |

---

## `P08-M07` — `M05` Remote Support & Managed Services

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P08-M07-T01` | Deploy **MeshCentral / RustDesk** for remote support sessions | `M05` · TSS §20.2 W5 | Remote support platform | — | `DE` | — |
| `P08-M07-T02` | Build the MSP service model on `M08`'s contract engine | `M05` · `M08` · `CD-M05-nn` | MSP module | 61 requirements, 37 PW | `OD` | T01 |
| `P08-M07-T03` | Deploy **Wazuh and osquery** for endpoint monitoring | `M05` · TSS §20.2 W5 | Monitoring platform | — | `DE` | — |
| `P08-M07-T04` | Build the **RMM collector** service | `CD-M05-nn` · TSS §20.2 W5 | `services/rmm-collector/` | — | `BE` | T03 |
| `P08-M07-T05` | Integrate `INT-028`–`INT-030` remote support and monitoring | `05-03` §8 W5 | 3 integrations | — | `IL` | T01, T03 |
| `P08-M07-T06` | Build alert-to-ticket automation and SLA tracking | `M05` · `M27` · `M08` | Alert automation | Journey 6: MSP alert -> ticket -> remote resolution -> SLA -> monthly service report | `OD` | T02 |
| `P08-M07-T07` | Build the monthly service report generation | `M05` · `M25` | Service reports | Client-facing; Bengali and English | `OD` | T06 |
| `P08-M07-T08` | Take the **L6 RMM agent pilot decision** — this is the conditional L6 component | TSS §9 · §1.4 decision 9 | Pilot decision | Conditional on a Wave 5 pilot. Decide, record, and either approve with an OSS alternative review or drop it | `CA` | T04 |
| `P08-M07-T09` | Emit `M05` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T02 |
| `P08-M07-T10` | Complete `M05` to the full DoD | §0.8.2 | `M05` accepted | — | `OD` | T01–T09 |

---

## `P08-M08` — `M45` Enterprise Asset, `M46` Fleet, `M49` Fixed Assets

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P08-M08-T01` | Build `M45` enterprise asset and test equipment on Odoo `maintenance` | `M45` · `CD-M45-nn` | EAM module | 26 requirements, 14 PW | `OD` | — |
| `P08-M08-T02` | Build **test-equipment calibration**, which `M31` deferred in W2 | `M45` · `P05-M02-T07` | Calibration model | The deferred capability, now delivered | `OD` | T01 |
| `P08-M08-T03` | Build `M46` fleet and vehicle management on Odoo `fleet` | `M46` · `CD-M46-nn` | Fleet module | 24 requirements, 12 PW | `OD` | — |
| `P08-M08-T04` | Connect fleet to dispatch — vehicle assignment, deferred from W2 | `M46` · `M02` · `P05-M03-T06` | Vehicle assignment | The deferred capability, now delivered | `OD` | T03 |
| `P08-M08-T05` | Build `M49` fixed assets and capital investment on `M19`'s fixed-asset seam | `M49` · `M19` · `P06-M01-T07` | Fixed-assets module | 22 requirements, 11 PW | `OD` | — |
| `P08-M08-T06` | Break the **`M49 <-> M54` cycle**: `M54` consumes depreciation events; **`M49` does not read budgets** | `AR-006` §4.1 pair 14 | Interface break | `M54` lands in W6 — build the seam now | `SA` | T05 |
| `P08-M08-T07` | Downgrade `M49 -> M54` — **budget linkage is advisory** | `AR-006` §5.4 NOT-A-PREREQ | Corrected declaration | — | `SA` | T05 |
| `P08-M08-T08` | Achieve 100% coverage on depreciation calculation | `DoD-03` | Coverage report | Financial path | `QA` | T05 |
| `P08-M08-T09` | Emit all three modules' events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01, T03, T05 |
| `P08-M08-T10` | Complete all three to the full DoD | §0.8.2 | Accepted | — | `OD` | T01–T09 |

---

## `P08-M09` — `P11` Field Auditor Application and Mayan EDMS

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P08-M09-T01` | Build `P11` in Flutter, **consuming `libs/dart/fix_offline`** — the third and last consumer of the engine | portal `P11` · `AR-010` `ADR-024` | `P11` app | 20–60 users. **Third consumption proves the engine contract was right — or exposes that it was not** | `MB` | — |
| `P08-M09-T02` | Build audit checklist execution with offline capture | portal `P11` · `M23` | Audit execution | — | `MB` | T01 |
| `P08-M09-T03` | Build evidence capture and NCR raising from the field | portal `P11` · `M23` · `M24` | Field NCR | — | `MB` | T02 |
| `P08-M09-T04` | Build branch-manager self-audit flows | portal `P11` · `M04` | Self-audit | — | `MB` | T02 |
| `P08-M09-T05` | Deploy **Mayan EDMS** for document volume | TSS §20.2 W5 · `M24` | Mayan live | The kernel `fix.document` model stays authoritative; Mayan handles volume | `DE` | — |
| `P08-M09-T06` | Run the **document migration** into Mayan | `CD-M24-nn` · TSS §20.2 W5 | Migrated documents | With control totals (`MIG-02`) | `ML` | T05 |
| `P08-M09-T07` | Verify the `M24` retention and legal-hold policies apply across both stores | `DA-006` · `M24` | Retention verification | Two stores, one policy | `DA` | T06 |
| `P08-M09-T08` | Achieve WCAG 2.2 AA and 100% Bengali on `P11` | `UX-005` · `AS-12` | Conformance | — | `LL` | T02–T04 |
| `P08-M09-T09` | Run the **`L12` offline suite** against `P11` — 24-hour operation, scripted conflicts | `QA-001` `L12` · `TS-015` | Offline evidence | — | `QA` | T02 |
| `P08-M09-T10` | Complete `P11` to the portal DoD | `05-01` §4 · §0.8.2 | `P11` accepted | — | `MB` | T01–T09 |

---

## `P08-M10` — Gate `G5` — Workforce, quality and MSP go-live (`MS-07`, Month 22)

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P08-M10-T01` | Run the `T−6` entry criteria check | `GV-009` §9.2 | Entry record | — | `PM` | — |
| `P08-M10-T02` | Verify **payroll runs correctly end to end**, with BEFTN disbursement and Bengali payslips | `M56` · Journey 13 | Payroll evidence | The highest-consequence path delivered in this phase | `QA` | T01 |
| `P08-M10-T03` | Verify **every stub opened in Waves 2–4 is closed**, and report any that outlived its expiry | `GV-005` · `P08-M05-T06` | Stub closure report | **This is the phase where the estate's honesty about stubs is tested** | `SA` | T01 |
| `P08-M10-T04` | Verify **certification eligibility is enforced at dispatch** — the check now blocks | `M22` · `M02` | Enforcement evidence | Negative-tested: an uncertified technician **must not** be assignable | `QA` | T01 |
| `P08-M10-T05` | Verify **journeys 6, 13 and 14** are automated and running nightly | TSS §20.4 | E2E evidence | MSP alert to service report; payroll cycle; complaint to CAPA closure | `QA` | T01 |
| `P08-M10-T06` | Verify ISO 9001:2015 audit readiness — **zero major non-conformances traced to systems** | `CON-11` | Audit readiness | `M23` supports it; the gate tests it | `QA` | T01 |
| `P08-M10-T07` | Verify `M05` MSP SLA reporting against contract terms | `M05` · `M08` | SLA evidence | — | `QA` | T01 |
| `P08-M10-T08` | Confirm the **`D-025` Odoo upgrade slot** decision remains valid, or re-plan it now | `D-025` · TSS §4.4 | Upgrade position | The W6 slot is the next wave. **Deciding this at W6 is deciding it too late** | `CA` | T01 |
| `P08-M10-T09` | Run the `gate` profile — performance at 1.5x peak, DR drill, full policy sweep | `PE-004` §4.2 | Gate results | — | `DE` | T01 |
| `P08-M10-T10` | **Gate `G5`.** Steering signs. Publish report and residuals | `GV-009` §8.4 | Signed `G5`; `MS-07` | — | `PM` | T02–T09 |

---
---

# PHASE 9
## NEW ASSET BUSINESSES, THE EVENT BUS & AI/ML

### Wave 6 · Months 23–26 · 17.4 weeks · Sprints 50–58 · Gate `G6` · Milestone `MS-08`

---

## 9.0 Phase charter

| | |
|---|---|
| **Purpose** | Launch the circular and asset-based business lines, migrate the event bus to a durable log, and stand up the ML platform on the data three years of operation has produced |
| **Tiers** | `T9` asset businesses, `T11` partial |
| **Modules** | `M13` RNT · `M14` TRF · `M06` DTS · `M26` (W6 slice) · `M43` DPL · `M44` ITC · `M54` FPA · `M58` TAO · `M59` HSE · `M60` GRC · `M61` KMS · `M66` ITS |
| **Portals** | `APP-04` Customer mobile application |
| **Technology** | **Apache Kafka / Kafka** (event-bus migration from Redis Streams) · MLflow · **Ollama** · ML inference gateway · event replay · Odoo `sale_renting` · corporate SSO (`INT-046`) |
| **Effort** | 235 PW against ~163 effective PW — **1.44x over** |
| **Exit** | `G6` — 6 criteria, Month 26. This is `MS-08` |

> **This is the wave that holds the Odoo major-version upgrade slot** if `D-025` adopted Option A.
> Odoo 20 released 24–26 September 2026; 19.0 is supported to ~September 2028. **A 36-month
> programme on an annually-versioned platform must plan an in-flight major upgrade.** Doing it here
> means doing it once, on an estate with 55 modules delivered — not on a 79-unit estate in Wave 9.

> **Why AI arrives now and not in Wave 2.** `06-01` §1 states the constraint plainly: *"Machine
> learning cannot be built before there is data to learn from."* Three years of service orders,
> dispatch decisions, parts consumption and customer conversations is the training set. Building
> `M26` in Wave 2 would have meant building it twice.

---

## `P09-M01` — Event bus migration to Apache Kafka/Kafka

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P09-M01-T01` | Deploy the **3-node Apache Kafka cluster** — single-node loss with no message loss | TSS §20.2 W6, §21.3 | Apache Kafka live | HA is the point of the migration | `DE` | — |
| `P09-M01-T02` | Verify every consumer is **idempotent** before switching bus — this was built in Phase 3 and must be re-proven at scale | `P03-M03-T04` · `DI-05` | Idempotency verification | The migration is safe only if consumers are | `BE` | T01 |
| `P09-M01-T03` | Run a **dual-write period**: outbox to both Redis Streams and Apache Kafka, consumers still on Redis | `AR-009` · `EP-05` | Dual-write live | Expand before contract, as with schema changes | `BE` | T02 |
| `P09-M01-T04` | Migrate consumers to Apache Kafka one consumer group at a time, with rollback per group | `AR-009` | Migrated consumers | Never all at once | `BE` | T03 |
| `P09-M01-T05` | Build **event replay from a timestamp** — `CD-M28-nn` | TSS §20.2 W6 | Replay capability | **This is what lets `M51` rebuild the VAT register from the event stream without `M20`'s cooperation.** Now it is real, not designed | `BE` | T04 |
| `P09-M01-T06` | Verify **dead-letter handling and replay** end to end under failure injection | `AR-009` · `QA-006` | Failure-injection evidence | — | `QA` | T05 |
| `P09-M01-T07` | Contract: decommission Redis Streams as the event bus (Redis remains for cache, sessions and locks) | `EP-05` | Redis Streams retired | The third release of the expand/migrate/contract cycle | `DE` | T06 |
| `P09-M01-T08` | Re-verify all **988 registered events** against the schema registry post-migration | `IN-003` | Registry verification | — | `IL` | T07 |
| `P09-M01-T09` | Re-run the **`FF-06` outbox coverage** and **`FF-59` event reciprocity** checks across the whole estate | `AR-012` | Fitness evidence | 55 modules delivered — verify, do not assume | `CA` | T08 |
| `P09-M01-T10` | Update every runbook affected by the bus change | `DoD-11` · `SV-003` | Updated runbooks | A runbook describing a decommissioned component is worse than no runbook | `SO` | T07 |

---

## `P09-M02` — The Odoo major-version upgrade slot (`D-025`)

**Execute only if `D-025` adopted Option A. If it did not, this milestone is a formal re-confirmation that the deferral still holds, with its consequences restated.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P09-M02-T01` | Re-confirm `D-025` **and `D-029`** against upstream reality, not against the decision record | `D-025` · `D-029` · `AR-013` `VC-02` · alignment audit `R-04` | Re-confirmed positions | **Two upgrades can land in the same window, not one. `PostgreSQL 17 reaches EOL 8 November 2029` — on a Q4-2026 kickoff that is roughly month 37: after this wave (months 23–26) but inside the Month 42 benefits window, so the PostgreSQL upgrade must land somewhere between this wave and month 37.** Sequencing an Odoo major upgrade and a PostgreSQL major upgrade in one wave is a decision to take deliberately, not to discover | `CA` | — |
| `P09-M02-T02` | Run the **fork audit** — `FORKS.yaml` must be empty, or every entry must have a migration plan | `AS-05` · `FF-03` · `BE-004` | Fork audit | **A fork discovered at the upgrade is a rewrite.** This is the moment `AS-05` either paid for itself or did not | `CA` | T01 |
| `P09-M02-T03` | Run the **OCA v20 availability assessment** across all 18 repositories, as `W0-01` did for v19 | `W0-01` method | v20 status matrix | The same work, three years on, with a known method | `SA` | T01 |
| `P09-M02-T04` | Build the upgrade branch and run the **migration dry run against a production-sized clone** | `PE-004` §5.1 stage 14 · `DoD-10` | Dry-run record | On `migration-staging`, at production volume | `DE` | T03 |
| `P09-M02-T05` | Run the **full regression estate** against the upgraded branch | `QA-001` `TS-013` | Regression results | The permanent regression core, all of it | `QA` | T04 |
| `P09-M02-T06` | Re-run **every fitness function** against the upgraded branch | `AR-012` | Fitness results | — | `CA` | T05 |
| `P09-M02-T07` | Rehearse the rollback and record it | `DoD-16` · `RL-002` | Rehearsed rollback | An upgrade without a rehearsed rollback is not an upgrade, it is a hope | `DE` | T04 |
| `P09-M02-T08` | Execute the upgrade under change control with a manual production gate | `PE-004` §8.5 · `RL-002` | Upgraded production | — | `DE` | T05–T07 |
| `P09-M02-T09` | Re-verify **Bengali rendering against the committed reference images** post-upgrade | `TR-07` · `make doctor` check 10 | Rendering verification | Asset-pipeline changes between major versions break font shaping silently | `LL` | T08 |
| `P09-M02-T10` | If the upgrade is deferred, record the **deferral decision and its consequence** — 19.0 support to ~Sept 2028, and the upgrade lands on a 79-unit estate later | `GV-003` | Recorded deferral | **Deciding not to upgrade is also a decision and must be recorded as one** | `CA` | T01 |

---

## `P09-M03` — `M13` Rental & Equipment-as-a-Service

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P09-M03-T01` | Install Odoo `sale_renting`, extended not forked | `M13` · TSS §20.2 W6 · `AS-05` | Rental layer | — | `OD` | — |
| `P09-M03-T02` | Build the rental reservation and availability model on `M37`'s rental SKUs | `M13` · `M37` · `P03-M06-T03` | Rental module | 44 requirements, 25 PW. **Out-degree 11 — it composes existing capability rather than duplicating it, which is the layered model working** | `OD` | T01 |
| `P09-M03-T03` | Build delivery and return through `M03` logistics | `M13` · `M03` | Rental logistics | Journey 8: rental reservation -> delivery -> return -> damage assessment -> billing | `OD` | T02 |
| `P09-M03-T04` | Build **damage assessment and deposit handling** | `M13` · `M20` | Damage flow | Money — `AS-10` and 100% coverage | `OD` | T03 |
| `P09-M03-T05` | Build rental billing on `M39`'s subscription engine | `M13` · `M39` | Rental billing | Composes, does not duplicate | `OD` | T02 |
| `P09-M03-T06` | Build the **rental service-order intake** — `FR-SRM-063` and `FR-SRM-064`, delivered in `M01`'s W2 slice | `05-01` §3.1 · `P05-M08-T05` | Rental intake wired | Rental swap-out converts an irreparable fault into an asset swap | `OD` | T02 |
| `P09-M03-T07` | Model rental assets in `M17`'s registry and `M49`'s fixed assets | `M13` · `M17` · `M49` | Asset linkage | A rental unit is a company asset and a customer asset simultaneously | `OD` | T02 |
| `P09-M03-T08` | Build contract terms on `M08`'s contract engine | `M13` · `M08` | Rental contracts | — | `OD` | T02 |
| `P09-M03-T09` | Emit `M13` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T02 |
| `P09-M03-T10` | Complete `M13` to the full DoD | §0.8.2 | `M13` accepted | — | `OD` | T01–T09 |

---

## `P09-M04` — `M14` Trade-In, Refurbishment & Resale

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P09-M04-T01` | Build trade-in request, valuation and offer | `M14` · `CD-M14-nn` | Trade-in module | 39 requirements, 22 PW. Out-degree 11 | `OD` | — |
| `P09-M04-T02` | Build collection through `M03` logistics | `M14` · `M03` | Collection flow | — | `OD` | T01 |
| `P09-M04-T03` | Build the **secure data wipe** step with certificate issuance, through `M06` | `M14` · `M06` | Data wipe flow | Journey 9: trade-in -> offer -> intake -> **data wipe** -> refurbishment -> grading -> resale | `OD` | T02, `P09-M05-T02` |
| `P09-M04-T04` | Build the refurbishment workflow on `M31`'s workshop model | `M14` · `M31` | Refurbishment | Composes the existing repair estate | `OD` | T03 |
| `P09-M04-T05` | Build **grading** against `M37`'s refurbishment grades | `M14` · `M37` · `P03-M06-T04` | Grading model | The kernel already holds the grades | `OD` | T04 |
| `P09-M04-T06` | Build resale through `M12`'s marketplace and `M38`'s storefront — both W7 | `M14` · `M12`, `M38` | Resale seam | Build the seam now; the channel lands in Phase 10 | `OD` | T05 |
| `P09-M04-T07` | Build trade-in payout through `M50` treasury | `M14` · `M50` | Payout flow | — | `OD` | T01 |
| `P09-M04-T08` | Model refurbished stock in `M15` inventory with grade-aware valuation | `M14` · `M15` | Graded inventory | Valuation by grade — a financial path | `OD` | T05 |
| `P09-M04-T09` | Emit `M14` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01 |
| `P09-M04-T10` | Complete `M14` to the full DoD | §0.8.2 | `M14` accepted | — | `OD` | T01–T09 |

---

## `P09-M05` — `M06` Data Services & Secure Data Handling

**The most residency-sensitive module in the estate.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P09-M05-T01` | Read `M06` and TSS §3.6 journey 11 — **recovered customer data lives only in Z4** | `M06` · TSS §3.3 · `SC-007` | Reading record | Journey 11: data recovery case -> **custody** -> recovery -> handover -> purge certificate | `SL` | — |
| `P09-M05-T02` | Build the **secure data-wipe and destruction certificate** service | `M06` · `CD-M06-nn` | Wipe service | 34 requirements, 18 PW. Consumed by `M14` trade-in and `M18` e-waste | `OD` | T01 |
| `P09-M05-T03` | Build the **data-recovery case model with chain of custody** | `M06` · `M03` custody model | Recovery cases | — | `OD` | T01 |
| `P09-M05-T04` | Route **all recovered customer data through the residency service to Z4**, never to the regional store | `SC-007` · `FF-09` · `AS-14` | Residency conformance | **Not transiently, not in a cache, not in a log** | `SL` | T03, `P03-M09-T03` |
| `P09-M05-T05` | Build the purge certificate with the statutory processing record preserved | `M06` · `NFR-095` | Purge certificate | Same shape as the PDPA erasure saga | `SL` | T04 |
| `P09-M05-T06` | Build backup-subscription services for customers | `M06` | Backup services | Surfaced in portal `P01` | `OD` | T02 |
| `P09-M05-T07` | Apply **step-up authentication and per-read logging** on every recovered-data access | `NFR-065` · TSS §3.4 | Access controls | Z4 rules apply in full | `SL` | T04 |
| `P09-M05-T08` | Run a targeted **`SC-002` threat-model review** of `M06` — it is the highest-value target in the estate | `SC-002` · `SC-009` | Threat model update | 97 threats, 32 abuse cases estate-wide; `M06` deserves its own pass | `SL` | T04 |
| `P09-M05-T09` | Emit `M06` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T02 |
| `P09-M05-T10` | Complete `M06` to the full DoD, with **zero open high or critical security findings** | §0.8.2 · `DoD-15` | `M06` accepted | — | `SL` | T01–T09 |

---

## `P09-M06` — `M26` AI/ML services, MLflow, Ollama

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P09-M06-T01` | Read `AR-011` AI/ML architecture and model specification | `AR-011` · `M26` | Reading record | 38 requirements, 30 PW, W6–W8 split | `BE` | — |
| `P09-M06-T02` | Deploy **MLflow** as the model registry | TSS §20.2 W6 | MLflow live | Every model has a version, a lineage and a rollback | `DE` | T01 |
| `P09-M06-T03` | Deploy **Ollama** for self-hosted LLM inference, with the GPU decision taken on measured latency | TSS §20.2 W6, §21.1 | Ollama live | **GPU only if latency requires** — measure before buying | `DE` | T01 |
| `P09-M06-T04` | Build the **ML inference gateway** service | `CD-M26-nn` · TSS §20.2 W6 | `services/ml-gateway/` | One gateway, not per-model endpoints | `BE` | T02, T03 |
| `P09-M06-T05` | Build the **dispatch-scoring model** on three years of dispatch outcomes | `M26` · `M02` | Dispatch model | The scoring service already exists; the model replaces its heuristics | `BE` | T04 |
| `P09-M06-T06` | Build the **demand-forecast model** feeding `M43` | `M26` · `M43` | Forecast model | — | `BE` | T04 |
| `P09-M06-T07` | Upgrade `M32`'s assistant with the `M61` knowledge base, lifting it beyond transactional intents | `M32` · `M61` · `P07-M05-T06` | Expanded intent set | The `Q-01` scope reduction, now closed | `BE` | T04, `P09-M08-T07` |
| `P09-M06-T08` | Integrate `INT-036` LLM and `INT-043` where an external model is genuinely required | `05-03` §8 W6 | Integrations | **Customer conversation data must not leave the Company under PDPA transfer restrictions** — external models are the exception, not the default | `IL` | T04 |
| `P09-M06-T09` | Build model monitoring, drift detection and the retraining trigger | `AR-011` · `PE-008` | Model ops | A model with no drift detection is a model that silently degrades | `BE` | T05, T06 |
| `P09-M06-T10` | Complete the `M26` W6 slice to the full DoD; the W8 slice lands in Phase 11 | §0.8.2 | `M26` W6 accepted | — | `BE` | T01–T09 |

---

## `P09-M07` — `M43` Demand Planning, `M44` Import & Landed Cost, `M54` FP&A

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P09-M07-T01` | Build `M43` demand planning and replenishment on `M15`'s reorder seam | `M43` · `M15` · `P05-M01-T05` | Demand planning | 24 requirements, 14 PW | `OD` | — |
| `P09-M07-T02` | Wire `M43` to the `M26` forecast model | `M43` · `M26` | Forecast integration | — | `OD` | T01, `P09-M06-T06` |
| `P09-M07-T03` | Build `M44` import, trade compliance and landed cost | `M44` · `CD-M44-nn` | Import module | 28 requirements, 15 PW | `OD` | — |
| `P09-M07-T04` | Implement the **`M41 <-> M44` break**: `M44` **consumes `goods.received`**; `M41` does not call `M44` | `AR-006` §4.1 pair 13 | Interface break | — | `SA` | T03 |
| `P09-M07-T05` | Execute the **valuation change from standard cost to landed cost**, documented in Phase 6 | `P06-M07-T05` | Valuation change | Finance was warned in W3. Execute it under change control, not as a side effect | `OD` | T04 |
| `P09-M07-T06` | Build `M54` cost accounting, budgeting and FP&A | `M54` · `CD-M54-nn` | FP&A module | 30 requirements, 17 PW. Out-degree 10 — late and integrative | `OD` | — |
| `P09-M07-T07` | Implement the **`M49 <-> M54` break**: `M54` consumes depreciation events | `AR-006` §4.1 pair 14 · `P08-M08-T06` | Interface break | The seam built in Phase 8, consumed here | `OD` | T06 |
| `P09-M07-T08` | Resolve `fix.contract.cost` ownership across `M08`, `M53` and `M54` — the last of the 34 multi-owned entities | `AR-008` §2.2 · `P07-M01-T08` | Ownership resolved | — | `SA` | T06 |
| `P09-M07-T09` | Emit all three modules' events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01, T03, T06 |
| `P09-M07-T10` | Complete all three to the full DoD, with 100% coverage on costing and budgeting paths | §0.8.2 · `DoD-03` | Accepted | — | `OD` | T01–T09 |

---

## `P09-M08` — `M58` Talent, `M59` HSE, `M60` GRC, `M61` Knowledge

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P09-M08-T01` | Build `M58` talent acquisition and onboarding on `M21` | `M58` · `M21` | Talent module | 34 requirements, 12 PW | `OD` | — |
| `P09-M08-T02` | Wire onboarding to the joiner event that `M29` provisioning consumes | `M58` · `P03-M08-T04` | Onboarding automation | The `MV-01` event set, now driven from the front | `OD` | T01 |
| `P09-M08-T03` | Build the remaining **40 `M59` HSE requirements** — mobile incident reporting already shipped in W2 | `M59` · `02-02` Category H note · `P05-M06-T09` | HSE module | 42 requirements, 14 PW; **2 shipped early with `P02`** | `OD` | — |
| `P09-M08-T04` | Build Labour Rules safety obligations, register and reporting | `M59` · `SC-008` | Safety compliance | Statutory density | `OD` | T03 |
| `P09-M08-T05` | Build `M60` governance, risk and compliance | `M60` · `CD-M60-nn` | GRC module | 34 requirements, 18 PW | `OD` | — |
| `P09-M08-T06` | Resolve the `M24 <-> M60` pair recorded as **under review** in Phase 3 | `AR-006` §4.1 pair 15 · `P03-M07-T09` | Pair resolved | A kernel owner must not depend on a W6 module — settle the direction | `SA` | T05 |
| `P09-M08-T07` | Build `M61` knowledge management and the technical library | `M61` · `CD-M61-nn` | Knowledge module | 24 requirements, 13 PW. **`M22`'s technical knowledge content moved here** | `OD` | — |
| `P09-M08-T08` | Load the **16 `KB-*` knowledge base files** and the technical library content | `project_content` 07 Knowledge Base | Loaded knowledge | Feeds `M32`'s expanded intents and `P02`'s offline manuals | `CN` | T07 |
| `P09-M08-T09` | Build `M66` internal IT service management | `M66` specification (baselined in `P01-M03-T10`) | ITSM module | **30 requirements, 14 PW measured** — `M66` §1 supersedes the register's 22/11 estimate | `OD` | `P01-M03-T10` |
| `P09-M08-T10` | Complete all five to the full DoD | §0.8.2 | Accepted | — | `OD` | T01–T09 |

---

## `P09-M09` — `APP-04` Customer mobile application and corporate SSO

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P09-M09-T01` | Confirm the framework from **`D-027`** — this is the app whose framework was declared "pending" in `BE-005` | `D-027` · `BE-005` §9.1 | Confirmed framework | If `D-027` ruled Flutter, this consumes `libs/dart/fix_ui`; if it ruled otherwise, a second toolchain enters the estate here | `CA` | — |
| `P09-M09-T02` | Build `APP-04` on the `P01` portal patterns established in Phase 5 | portal `P01` · `AR-006` §6.3 | Customer app | *"Requires `P01` patterns"* — build on them, do not re-derive them | `MB` | T01 |
| `P09-M09-T03` | Implement the full `P01` capability set on mobile: account, devices, booking, tracking, approvals, payments, contracts, warranty, loyalty, shop, trade-in, data services, recycling, support, feedback | portal `P01` capability set | Capability parity | Parity with the web portal, not a subset | `MB` | T02 |
| `P09-M09-T04` | Achieve the **app-store rating target > 4.5** as a design constraint, not a hope | portal `P01` KPIs | Quality bar | — | `MB` | T03 |
| `P09-M09-T05` | Implement push notification through the `Novu` platform built in Phase 4 | `P04-M05` · `INT-014` | Push integration | — | `MB` | T03 |
| `P09-M09-T06` | Achieve **WCAG 2.2 AA** and Bengali-first with an English toggle | `UX-005` · `AS-12` | Conformance | Same correction as `P05-M07-T10` — `UX-005` governs, not the `P01` specification's 2.1 | `LL` | T03 |
| `P09-M09-T07` | Run the cross-runtime conformance suite — `R4` against `R3` for the same component contract | `UX-001` §11 `CFM-05` | Visual parity evidence | **Permitted to differ in code, forbidden to differ in rendered result** beyond `PID-01`…`PID-07` | `UX` | T03 |
| `P09-M09-T08` | Integrate **`INT-046` corporate SSO federation** for `P04` users | `05-03` §8 W6 · `M29` | Corporate SSO | Per-client SAML/OIDC federation through Keycloak | `IL` | — |
| `P09-M09-T09` | Integrate `INT-016` video, `INT-017` social, `INT-031`–`INT-033` patch/EDR/cloud, `INT-043` IMEI check | `05-03` §8 W6 | 6 integrations | — | `IL` | — |
| `P09-M09-T10` | Complete `APP-04` to the portal DoD | `05-01` §4 · §0.8.2 | `APP-04` accepted | — | `MB` | T01–T09 |

---

## `P09-M10` — Gate `G6` — New asset businesses go-live (`MS-08`, Month 26)

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P09-M10-T01` | Run the `T−6` entry criteria check | `GV-009` §9.2 | Entry record | — | `PM` | — |
| `P09-M10-T02` | Verify **rental, trade-in and data services are transacting** end to end | `06-01` W6 gate | Transaction evidence | — | `QA` | T01 |
| `P09-M10-T03` | Verify the **event-bus migration is complete** with zero message loss and replay proven | `P09-M01` | Migration evidence | Under failure injection, not under happy path | `QA` | T01 |
| `P09-M10-T04` | Verify **journeys 8, 9 and 11** are automated and running nightly | TSS §20.4 | E2E evidence | Rental lifecycle; trade-in to resale; data recovery with custody | `QA` | T01 |
| `P09-M10-T05` | Verify the **Odoo upgrade completed, or the deferral is formally re-recorded** | `P09-M02` | Upgrade or deferral record | Either outcome is acceptable; silence is not | `CA` | T01 |
| `P09-M10-T06` | Verify `M06` residency conformance — **no recovered customer data outside Z4, anywhere, including logs and caches** | `FF-09` · `SC-007` | Residency audit | Audit the logs, not the design | `SL` | T01 |
| `P09-M10-T07` | Verify **`G6` content approval** — the gate that 32 Class A/B content files await | `project_content` master index | Content approvals | **The Programme Content Lead who is the final approver of every Class E file must be appointed by now.** If not, escalate as a gate blocker | `CN` | T01 |
| `P09-M10-T08` | Verify ML model governance: registry, lineage, drift detection, rollback | `AR-011` · `P09-M06-T09` | Model governance evidence | — | `QA` | T01 |
| `P09-M10-T09` | Run the `gate` profile — performance at 1.5x peak, DR drill, full policy sweep | `PE-004` §4.2 | Gate results | — | `DE` | T01 |
| `P09-M10-T10` | **Gate `G6`.** Steering signs. Publish report and residuals | `GV-009` §8.4 | Signed `G6`; `MS-08` | — | `PM` | T02–T09 |

---
---

# PHASE 10
## MARKETPLACE, SETTLEMENT & PARTNER CHANNEL

### Wave 7 · Months 27–30 · 17.4 weeks · Sprints 59–67 · Gate `G7` · Milestone `MS-09`

---

## 10.0 Phase charter

| | |
|---|---|
| **Purpose** | Open the platform to external sellers and partners, and make the money move correctly between the Company and 500–2,000 counterparties |
| **Tier** | `T10` channel |
| **Modules** | `M38` ECM · `M12` MKP · `M40` PCM · `M11` (W7 slice) · `M53` (W7 slice) · `M47` FAC · `M67` PPM |
| **Portals** | `P07` Marketplace Seller Portal & App · `P12` Partner & Referral Portal |
| **Technology** | **L6 KYC / identity verification** · ad delivery (`INT-037`) · client ITSM (`INT-047`) · seller payout rail (`INT-007`) |
| **Effort** | 185 PW against ~163 effective PW — **1.14x** |
| **Exit** | `G7` — 6 criteria, Month 30. This is `MS-09` |

> **The decision that shapes this whole phase.** TSS §1.4 decision 7: *"Build the marketplace and
> the settlement engine. Commission and payout must post to the ledger. **A SaaS marketplace cannot
> be the system of record for money the Company owes to 5,000 sellers.**"*

> **`G7-02` requires "payout accuracy 100%".** Payout is settlement; settlement is `M53`. The
> settlement engine was built in Phase 7 (`P07-M03-T07`) precisely so that this gate criterion has a
> module behind it — `GV-004` §5.6 found it testing a module the plan did not schedule.

---

## `P10-M01` — `M12` Marketplace & Seller Ecosystem

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P10-M01-T01` | Build the seller model as a **party role on `M33`**, never a separate master | `M12` · `M33` · TSS §3.2 design rule | Seller model | 62 requirements, 40 PW. Out-degree 11. **A marketplace seller may also be a customer** — one `res.partner`, two `fix.party.role` records | `OD` | — |
| `P10-M01-T02` | Build seller onboarding, verification and the **L6 KYC integration** (`INT-034`) | `M12` · TSS §9 L6 · `05-03` §8 W7 | Onboarding + KYC | **Seller KYC data is `S3` residency-classified** — route through Z4 | `IL` | T01 |
| `P10-M01-T03` | Build the marketplace order and quote-selection flow | `M12` · `M01` | Order flow | Journey 7: marketplace order -> seller quote -> selection -> job -> review -> commission -> payout | `OD` | T01 |
| `P10-M01-T04` | Build seller scoring, ranking and dispute handling | `M12` · `M34` | Scoring engine | Transparent scoring is the named adoption mitigation for sellers | `OD` | T03 |
| `P10-M01-T05` | Implement the **`M12 <-> M53` break**: commission **earning** is an `M12` event; **`M12` must not call `M53`** | `AR-006` §4.1 pair 12 · `P07-M03-T06` | Interface break | — | `SA` | T03 |
| `P10-M01-T06` | Build the seller-facing catalogue on `M37` | `M12` · `M37` | Seller catalogue | — | `OD` | T01 |
| `P10-M01-T07` | Wire refurbished-device resale from `M14` into the marketplace | `M12` · `M14` · `P09-M04-T06` | Resale channel | The seam built in Phase 9, connected here | `OD` | T03 |
| `P10-M01-T08` | Route seller KYC documents through the residency service to Z4 | `SC-007` · `FF-09` | Residency conformance | 500–2,000 sellers, each with identity documents | `SL` | T02 |
| `P10-M01-T09` | Emit `M12` events and register them | `AS-08` · `IN-003` | Registered events | `marketplace_order.created`, `seller.quoted`, `commission.earned`, `seller.scored` | `OD` | T03 |
| `P10-M01-T10` | Complete `M12` to the full DoD | §0.8.2 | `M12` accepted | — | `OD` | T01–T09 |

---

## `P10-M02` — `M53` settlement completion and payout

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P10-M02-T01` | Complete the `M53` W7 marketplace-settlement slice | `M53` · `02-02` Category G | `M53` complete | The W4 slice shipped in Phase 7 | `OD` | — |
| `P10-M02-T02` | Build commission calculation consuming `commission.earned` events | `M53` · `P10-M01-T05` | Commission engine live | — | `OD` | T01 |
| `P10-M02-T03` | Build the **payout run** with approval authority and segregation of duties | `M53` · `05-04` §6–§7 | Payout run | Money leaving the Company to 500–2,000 external parties. SoD is not optional | `OD` | T02 |
| `P10-M02-T04` | Integrate **`INT-007` seller payout rail** | `05-03` §8 W7 | Payout integration | — | `IL` | T03 |
| `P10-M02-T05` | **Post every commission and payout to the ledger** through `M19` | `M53` · `M19` · TSS §1.4 decision 7 | GL posting | The whole reason the settlement engine is built rather than bought | `OD` | T03 |
| `P10-M02-T06` | Build payout reconciliation and unmatched-item handling | `M53` · `M50` | Reconciliation | — | `OD` | T05 |
| `P10-M02-T07` | Build seller statements and tax documentation, including TDS through `M51` | `M53` · `M51` | Seller statements | Bengali and English | `OD` | T05 |
| `P10-M02-T08` | Achieve **100% test coverage on every commission and payout calculation path** | `DoD-03` | Coverage report | Gate criterion is **payout accuracy 100%** — the coverage must match the claim | `QA` | T02, T03 |
| `P10-M02-T09` | Emit `M53` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01 |
| `P10-M02-T10` | Complete `M53` to the full DoD | §0.8.2 | `M53` accepted | — | `OD` | T01–T09 |

---

## `P10-M03` — `M38` E-Commerce & Digital Storefront

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P10-M03-T01` | Build the storefront on Odoo `website` extended, or on the Next.js platform per `CON-03` | `M38` · `CON-03` | Storefront | 40 requirements, 24 PW. Out-degree 11 | `FE` | — |
| `P10-M03-T02` | Build the parts, accessories and refurbished-device catalogue on `M37` | `M38` · `M37` | Product catalogue | — | `FE` | T01 |
| `P10-M03-T03` | Build cart, checkout and order tracking | `M38` · `M20` | Checkout flow | Payments through the Phase 6 integrations | `FE` | T02 |
| `P10-M03-T04` | Build the returns and refund flow | `M38` · `M03` · `M20` | Returns | Through reverse logistics | `FE` | T03 |
| `P10-M03-T05` | Integrate `INT-037` ad delivery | `05-03` §8 W7 | Ad integration | — | `IL` | T01 |
| `P10-M03-T06` | Integrate `INT-035` and remaining W7 trust services | `05-03` §8 W7 | Integrations | — | `IL` | T01 |
| `P10-M03-T07` | Enforce the **< 400 KB bundle budget** on the storefront's critical path | CI stage 11 | Bundle budget met | — | `FE` | T03 |
| `P10-M03-T08` | Achieve WCAG 2.2 AA and 100% Bengali | `UX-005` · `AS-12` | Conformance | — | `LL` | T03 |
| `P10-M03-T09` | Emit `M38` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T03 |
| `P10-M03-T10` | Complete `M38` to the full DoD | §0.8.2 | `M38` accepted | — | `FE` | T01–T09 |

---

## `P10-M04` — `M40` Partner, Channel, Alliance & Franchise

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P10-M04-T01` | Build the partner model as a **party role on `M33`** | `M40` · `M33` | Partner model | 30 requirements, 16 PW | `OD` | — |
| `P10-M04-T02` | Build the referral and lead-attribution model | `M40` · `M07` | Referral model | — | `OD` | T01 |
| `P10-M04-T03` | Build partner commission through `M53`'s engine | `M40` · `M53` | Partner commission | Composes, does not duplicate | `OD` | T02, `P10-M02-T02` |
| `P10-M04-T04` | Build the franchise model and territory management | `M40` · `M30` zones | Franchise model | — | `OD` | T01 |
| `P10-M04-T05` | Build alliance agreements on `M08`'s contract engine | `M40` · `M08` | Alliance contracts | — | `OD` | T01 |
| `P10-M04-T06` | Record that **`05-05` registers no business rules for `M40`** — `FF-53` reports zero coverage | `P07-M06-T08` | Recorded finding | Either author the rules or record the absence deliberately. **Do not let a check surprise a squad** | `BA` | T01 |
| `P10-M04-T07` | Build partner onboarding from the `EO-*` content set | `project_content` 18 Ecosystem Onboarding | Onboarding content | — | `CN` | T01 |
| `P10-M04-T08` | Build partner performance reporting through `M25` | `M40` · `M25` | Partner reporting | — | `OD` | T03 |
| `P10-M04-T09` | Emit `M40` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01 |
| `P10-M04-T10` | Complete `M40` to the full DoD | §0.8.2 | `M40` accepted | — | `OD` | T01–T09 |

---

## `P10-M05` — `M11` dynamic pricing (W7 slice) and `M47` Facility

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P10-M05-T01` | Build the `M11` **W7 dynamic-pricing slice** deferred in Phase 6 | `M11` · `P06-M06-T08` | Dynamic pricing | — | `OD` | — |
| `P10-M05-T02` | Wire dynamic pricing to the marketplace and storefront | `M11` · `M12`, `M38` | Channel pricing | — | `OD` | T01 |
| `P10-M05-T03` | Wire dynamic pricing to `M26`'s ML gateway where a model drives the price | `M11` · `M26` | ML pricing | Every priced output must be explainable — a price a customer disputes must be reconstructable | `BE` | T01 |
| `P10-M05-T04` | Achieve 100% coverage on dynamic-price calculation | `DoD-03` | Coverage report | Financial path | `QA` | T01 |
| `P10-M05-T05` | Build `M47` facility, branch infrastructure and workplace | `M47` · `CD-M47-nn` | Facility module | 22 requirements, 11 PW. Out-degree 10 | `OD` | — |
| `P10-M05-T06` | Wire facility assets into `M45` EAM and `M49` fixed assets | `M47` · `M45`, `M49` | Asset linkage | — | `OD` | T05 |
| `P10-M05-T07` | Build `M67` project, program and portfolio management | `M67` specification (baselined in `P01-M03-T10`) | PPM module | **32 requirements, 17 PW measured** — `M67` §1 supersedes the register's 26/14 estimate | `OD` | `P01-M03-T10` |
| `P10-M05-T08` | Integrate **`INT-047` client ITSM** | `05-03` §8 W7 | ITSM integration | For MSP clients running their own service desk | `IL` | — |
| `P10-M05-T09` | Emit `M11`, `M47` and `M67` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01, T05, T07 |
| `P10-M05-T10` | Complete all three to the full DoD | §0.8.2 | Accepted | — | `OD` | T01–T09 |

---

## `P10-M06` — `P07` Marketplace Seller Portal & Application

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P10-M06-T01` | Confirm the app framework from **`D-027`** — `P07` is one of the units that declared React Native | `D-027` · `BE-005` §9.1 | Confirmed framework | If a second mobile toolchain enters here, `BE-001`, `BE-002` and the CI estate all change | `CA` | — |
| `P10-M06-T02` | Build the `P07` web portal (Next.js, `R3`) | portal `P07` · `UX-001` | `P07` web | 500–2,000 users | `FE` | T01 |
| `P10-M06-T03` | Build seller onboarding with KYC document capture | portal `P07` · `P10-M01-T02` | Onboarding | Documents route to Z4 | `FE` | T02 |
| `P10-M06-T04` | Build the job marketplace view, quoting and acceptance | portal `P07` · `M12` | Job flows | — | `FE` | T02 |
| `P10-M06-T05` | Build the earnings, commission and **payout view with full transparency** | portal `P07` · `M53` | Earnings view | **Fast payouts and transparent scoring are the named adoption mitigations for sellers** — a seller who cannot see why they were paid what they were paid will leave | `FE` | T02 |
| `P10-M06-T06` | Build the seller scorecard and dispute-raising flow | portal `P07` · `M12` | Scorecard | — | `FE` | T04 |
| `P10-M06-T07` | Build the `P07` mobile application on the confirmed framework | portal `P07` · `D-027` | `P07` app | — | `MB` | T01, T04 |
| `P10-M06-T08` | Address the portal-consumed events `M12` must publish — **the entire eight-event marketplace surface `P07` is built on** was among the 69 unpublished | `IN-003` · `B-17` | Event reconciliation | This is the portal where the 67.6% gap bites hardest | `IL` | T02 |
| `P10-M06-T09` | Achieve WCAG 2.2 AA and 100% Bengali on both surfaces | `UX-005` · `AS-12` | Conformance | Sellers are external and Bengali-first | `LL` | T02, T07 |
| `P10-M06-T10` | Complete `P07` to the portal DoD | `05-01` §4 · §0.8.2 | `P07` accepted | — | `FE` | T01–T09 |

---

## `P10-M07` — `P12` Partner & Referral Portal

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P10-M07-T01` | Build `P12` (Next.js, `R3`) | portal `P12` · `UX-001` | `P12` live | 100–500 users | `FE` | — |
| `P10-M07-T02` | Build partner onboarding and agreement acceptance with e-signature | portal `P12` · `M40` · `M24` | Onboarding | — | `FE` | T01 |
| `P10-M07-T03` | Build the referral submission and tracking flow | portal `P12` · `M40` | Referral flows | — | `FE` | T02 |
| `P10-M07-T04` | Build the commission and payout view | portal `P12` · `M53` | Commission view | Same transparency standard as `P07` | `FE` | T02 |
| `P10-M07-T05` | Build partner performance reporting | portal `P12` · `M25` | Reporting | — | `FE` | T02 |
| `P10-M07-T06` | Build the franchise operations view for franchise partners | portal `P12` · `M40` | Franchise view | — | `FE` | T02 |
| `P10-M07-T07` | Run the `PS-11` contract test on `P12` and `P07` | `AS-09` · `PS-11` | Contract tests green | — | `IL` | T01, `P10-M06-T02` |
| `P10-M07-T08` | Run the cross-runtime conformance suite across all twelve portals — **the first time every surface exists simultaneously** | `UX-001` §11 | Full conformance run | `CFM-04` inventory parity across twelve surfaces and five runtimes | `UX` | T01 |
| `P10-M07-T09` | Achieve WCAG 2.2 AA and 100% Bengali | `UX-005` · `AS-12` | Conformance | — | `LL` | T02–T06 |
| `P10-M07-T10` | Complete `P12` to the portal DoD | `05-01` §4 · §0.8.2 | `P12` accepted | **All twelve portals delivered** | `FE` | T01–T09 |

---

## `P10-M08` — External counterparty onboarding at scale

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P10-M08-T01` | Load the full **14-file `EO-*` ecosystem onboarding content set** | `project_content` 18 | Loaded onboarding content | Sellers, partners, brands, vendors, corporate clients | `CN` | — |
| `P10-M08-T02` | Load the **`LG-*` legal content** for seller and partner agreements | `project_content` 10 · legal sign-off | Loaded agreements | **61 content files require legal or statutory sign-off** — these are among them | `CN` | T01 |
| `P10-M08-T03` | Build the self-service onboarding funnel with measured drop-off | portal `P07`, `P12` | Onboarding funnel | **Sellers have low switching cost.** A slow onboarding is a lost seller | `FE` | T01 |
| `P10-M08-T04` | Certify external counterparties against the **`sandbox`** environment | `IN-008` · `PE-002` §5.10 | Certification records | Externally reachable, externally credentialled, synthetic only | `IL` | — |
| `P10-M08-T05` | Build partner and seller support content in the `HC-*` help sets | `project_content` 09 Help Centre | Help content | — | `CN` | T01 |
| `P10-M08-T06` | Verify **`T5` external-party access rules** — an external party sees only its own data, negative-tested | `05-04` §8 · `DoD-07` | Access tests | 500–2,000 sellers on one platform. A cross-tenant leak here is a business-ending event | `SL` | T03 |
| `P10-M08-T07` | Rate-limit and quota external API consumers per Kong consumer class | `IN-005` · TSS §3.4 Z1 | Rate limits | — | `IL` | T04 |
| `P10-M08-T08` | Build the external-party dispute and escalation path | `M12` · `M34` | Dispute path | — | `OD` | T03 |
| `P10-M08-T09` | Run a targeted **`SC-002` abuse-case review** for the marketplace surface | `SC-002` — 32 abuse cases | Abuse-case review | External, adversarial, financially motivated users are a different threat class | `SL` | T06 |
| `P10-M08-T10` | Verify the **`IP-10` egress rule** — every outbound call to an external counterparty goes through Z6 with an allow-listed destination and is logged | TSS §3.4 zone table | Egress audit | **What makes "data leaving the Company is minimised and logged" enforceable rather than aspirational** | `SL` | T04 |

---

## `P10-M09` — Rollout completion to all 51+ branches

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P10-M09-T01` | Read `RL-004` rollout plan and `MG-006` §7 — the **51-branch coordination model** | `RL-004` · `MG-006` §7 | Reading record | The zone layer exists because 51 sites cannot be sequenced individually | `PM` | — |
| `P10-M09-T02` | Execute the **T−4 site readiness assessment** per remaining branch: connectivity, hardware, staffing | `06-01` §6 rollout pattern | Readiness assessments | — | `TR` | T01 |
| `P10-M09-T03` | Execute **T−3 data preparation and validation with each branch** | `06-01` §6 | Validated branch data | The branch validates its own data. Nobody else can | `ML` | T02 |
| `P10-M09-T04` | Execute **T−2 branch champion training (train the trainer)** | `CH-005` · `06-01` §6 | Trained champions | One champion per branch, 4 h/week during rollout | `TR` | T03 |
| `P10-M09-T05` | Execute **T−1 all-staff training in Bengali; provision system access** | `CH-002` · `06-01` §6 | Trained staff | **Training delivered before access is granted**, not after | `TR` | T04 |
| `P10-M09-T06` | Execute **T−3 days data cutover; begin parallel run** | `MG-006` · `06-01` §6 | Cutover complete | — | `ML` | T05 |
| `P10-M09-T07` | Execute **T−0 go-live with on-site support** (floor-walkers) | `06-01` §6, §7 | Go-live | — | `SO` | T06 |
| `P10-M09-T08` | Execute **T+2 parallel run ends; legacy process withdrawn** per the parallel-period table | `06-01` §6 parallel running | Parallel run closed | Service orders 2 weeks · inventory 2 weeks + full count · finance 1 full month-end · payroll **2 pay cycles** · warranty 1 month | `SO` | T07 |
| `P10-M09-T09` | Execute **T+4 hypercare ends; adoption review** | `SV-005` · `06-01` §6 | Adoption review | **Weekly usage reporting by role and branch; intervene where adoption lags** | `TR` | T08 |
| `P10-M09-T10` | On adoption failure at any location: **pause rollout, diagnose, remediate, re-pilot before continuing** | `06-01` §9 contingency | Remediation record | Do not roll forward through a failed site | `PM` | T09 |

---

## `P10-M10` — Gate `G7` — Marketplace go-live (`MS-09`, Month 30)

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P10-M10-T01` | Run the `T−6` entry criteria check | `GV-009` §9.2 | Entry record | — | `PM` | — |
| `P10-M10-T02` | `G7-01` **Sellers onboarded and transacting** | `06-01` W7 gate | Transaction evidence | — | `QA` | T01 |
| `P10-M10-T03` | `G7-02` **Payout accuracy 100%** | `06-01` W7 gate · `P07-M03-T08` | Payout evidence | **The criterion `GV-004` §5.6 found testing an unscheduled module. It now has `M53` behind it** | `QA` | T01 |
| `P10-M10-T04` | Verify **journey 7** — marketplace order to payout — is automated and running nightly | TSS §20.4 | E2E evidence | — | `QA` | T01 |
| `P10-M10-T05` | Verify **all twelve portals** are delivered and pass the cross-runtime conformance suite | `UX-001` §11 · `P10-M07-T08` | Conformance evidence | Twelve surfaces, five runtimes, one contract | `UX` | T01 |
| `P10-M10-T06` | Verify **cross-tenant isolation** for external parties, negative-tested at scale | `05-04` §8 · `P10-M08-T06` | Isolation evidence | — | `SL` | T01 |
| `P10-M10-T07` | Verify **all 51+ branches are live** with adoption above the intervention threshold | `RL-004` · `P10-M09` | Rollout evidence | — | `TR` | T01 |
| `P10-M10-T08` | Verify commission and payout GL postings reconcile to the ledger | `M53` · `M19` | Reconciliation evidence | — | `QA` | T01 |
| `P10-M10-T09` | Run the `gate` profile — performance at 1.5x peak with **75,000+ concurrent portal users** (`NFR-004`) | `PE-004` §4.2 · `NFR-004` | Gate results | The first wave where portal concurrency is genuinely tested | `DE` | T01 |
| `P10-M10-T10` | **Gate `G7`.** Steering signs. Publish report and residuals | `GV-009` §8.4 | Signed `G7`; `MS-09` | — | `PM` | T02–T09 |

---
---

# PHASE 11
## INTELLIGENCE, WAREHOUSE, IoT & ESG

### Wave 8 · Months 31–34 · 17.4 weeks · Sprints 68–76 · Gate `G8` · Milestone `MS-10`

---

## 11.0 Phase charter

| | |
|---|---|
| **Purpose** | Move analytics off the read replica onto a purpose-built warehouse, complete the ML estate, launch IoT and predictive maintenance, and close the circular-economy loop |
| **Tier** | `T11` intelligence |
| **Modules** | `M62` (completion) · `M26` (completion) · `M48` IOT · `M18` ESG |
| **Technology** | **ClickHouse** · warehouse migration from the read replica · speech-to-text · IoT ingestion at scale · e-waste authority reporting (`INT-040`) |
| **Effort** | **39 PW against ~136 effective PW — 0.29x.** The first genuinely under-loaded wave |
| **Exit** | `G8` — 5 criteria, Month 34. This is `MS-10` |

> **This is the wave with spare capacity, and it should be planned as such.** `GV-004` §5.3 records
> combined spare effective capacity in Waves 5–9 at **313 PW**. Waves 1–7 have all run over. **This
> phase is where the debt incurred earlier is repaid** — technical debt, deferred test automation,
> unauthored API contracts, unregistered events, and the requirements descoped under pressure at
> earlier gates. Milestones `P11-M08` and `P11-M09` exist for that purpose and are not filler.

---

## `P11-M01` — ClickHouse and the warehouse migration

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P11-M01-T01` | Deploy **ClickHouse** — 8 vCPU / 32 GB / 4 TB | TSS §20.2 W8, §21.1 | ClickHouse live | Chosen for `NFR-039` analytical query performance | `DE` | — |
| `P11-M01-T02` | Migrate the dimensional model from the read replica to ClickHouse | `M62` · `DA-007` · `P07-M07-T03` | Migrated model | The W4 slice ran on the replica by design; this is the planned move | `DA` | T01 |
| `P11-M01-T03` | Re-point the dbt project at ClickHouse and re-run the full transformation set | `P07-M07-T04` | Re-pointed ETL | — | `DA` | T02 |
| `P11-M01-T04` | Migrate Apache Superset and Grafana data sources | `M25` · portal `P06` | Re-pointed BI | Dashboards must not change appearance — verify against the conformance suite | `DA` | T03 |
| `P11-M01-T05` | Verify **`NFR-039` analytical query performance at 1.5x peak** against ClickHouse | `NFR-039` · `DoD-14` | Performance evidence | The reason for the migration — prove it delivered | `QA` | T04 |
| `P11-M01-T06` | Remove the analytical load from the read replicas and re-baseline OLTP performance | `PE-006` | Re-baselined OLTP | The second benefit: the primary estate gets faster | `DE` | T05 |
| `P11-M01-T07` | Apply **`NFR-086c`** to the warehouse — **no residency-classified data in the analytical store**, in any region | `SC-007` · `FF-09` | Residency conformance | A warehouse is the easiest place for classified data to leak by aggregation | `SL` | T02 |
| `P11-M01-T08` | Verify the **PDPA erasure saga reaches the warehouse** | `P07-M08-T04` | Erasure verification | An erasure that misses the warehouse is not an erasure | `SL` | T02 |
| `P11-M01-T09` | Build warehouse retention and archival per `DA-006` | `DA-006` | Retention policy | — | `DA` | T02 |
| `P11-M01-T10` | Update every runbook affected by the migration | `SV-003` · `DoD-11` | Updated runbooks | — | `SO` | T06 |

---

## `P11-M02` — `M62` Data Platform, Warehouse & Governance completion

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P11-M02-T01` | Complete `M62` beyond the W4 slice | `M62` · `CD-M62-nn` | `M62` complete | 34 requirements, 22 PW, W4/W8 split | `DA` | — |
| `P11-M02-T02` | Build the **data catalogue** over the 1,335 owned entities | `M62` · `DA-002` | Data catalogue | Every entity, its owner, its classification, its retention | `DA` | T01 |
| `P11-M02-T03` | Build data-lineage tracking from source to dashboard | `M62` · `DA-003` | Lineage | A KPI whose lineage is unknown is a KPI nobody trusts | `DA` | T02 |
| `P11-M02-T04` | Implement `DA-003` data governance and the **stewardship model** with named stewards | `DA-003` | Stewardship live | Named people, not named roles | `DA` | T02 |
| `P11-M02-T05` | Implement `DA-008` data quality monitoring with thresholds and alerting | `DA-008` | DQ monitoring | Measured continuously, not audited annually | `DA` | T03 |
| `P11-M02-T06` | Verify **`FF-27`** — no entity is owned by more than one module — is now zero across all 79 units | `AR-008` §2.2 · `FF-27` | Ownership verification | Started at 34. **If it is not zero here, it never will be** | `CA` | T02 |
| `P11-M02-T07` | Verify **`FF-36`** — citation-to-dictionary consistency across the content repository | `AR-012` §10 | Citation verification | — | `CA` | T02 |
| `P11-M02-T08` | Reconcile the **95 registered KPIs against the 250 in use** and close the gap | `BM-002` · `B-09a`-class finding | Reconciled KPI register | Either register the 155 or retire them. **A KPI in use and not registered is a number nobody owns** | `DA` | T03 |
| `P11-M02-T09` | Emit `M62` events and register them | `AS-08` · `IN-003` | Registered events | — | `DA` | T01 |
| `P11-M02-T10` | Complete `M62` to the full DoD | §0.8.2 | `M62` accepted | — | `DA` | T01–T09 |

---

## `P11-M03` — `M48` IoT Telemetry & Predictive Maintenance

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P11-M03-T01` | Build the IoT device registry on `M17`'s asset registry | `M48` · `M17` · `CD-M48-nn` | IoT registry | 28 requirements, 18 PW | `OD` | — |
| `P11-M03-T02` | Scale the telemetry collector to **50,000 telemetry events per minute** | `M48` · `P05-M04-T04` · TSS §3.6.2 | Scaled collector | The service was built in Phase 5 at GPS volume; this is 60x that | `BE` | T01 |
| `P11-M03-T03` | Extend TimescaleDB partitioning and compression for telemetry volume | `M48` · TSS §21.1 | Extended time-series store | 8 vCPU / 32 GB / 4 TB with compression | `DE` | T02 |
| `P11-M03-T04` | Build the **predictive-maintenance model** on `M26`'s ML gateway | `M48` · `M26` | PdM model | Trained on `M45`/`M17` failure history | `BE` | T02, `P09-M06-T04` |
| `P11-M03-T05` | Wire predicted failures into `M02` dispatch as preventive work orders | `M48` · `M02` · `M08` | PdM dispatch | The business value: a visit before the failure, not after | `OD` | T04 |
| `P11-M03-T06` | Build IoT alerting and threshold configuration on `M30`'s configuration model | `M48` · `M30` | Alert configuration | — | `OD` | T01 |
| `P11-M03-T07` | Verify **`NFR` telemetry ingest at 1.5x peak** — 75,000 events/minute | `DoD-14` | Performance evidence | — | `QA` | T02 |
| `P11-M03-T08` | Classify telemetry data and confirm its residency position | `DA-005` · `D-013` | Classification | Device telemetry can be personal data by inference | `SL` | T01 |
| `P11-M03-T09` | Emit `M48` events and register them | `AS-08` · `IN-003` | Registered events | Throttled, as GPS events are | `OD` | T01 |
| `P11-M03-T10` | Complete `M48` to the full DoD | §0.8.2 | `M48` accepted | — | `OD` | T01–T09 |

---

## `P11-M04` — `M26` AI/ML completion and speech-to-text

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P11-M04-T01` | Complete `M26` beyond the W6 slice | `M26` · `AR-011` | `M26` complete | 38 requirements, 30 PW, W6–W8 split | `BE` | — |
| `P11-M04-T02` | Build the **speech-to-text service** for Bengali | `CD-M26-nn` · TSS §20.2 W8 · `INT-045` | `services/stt/` | Technician voice notes, contact-centre calls. **Bengali STT accuracy must be measured, not assumed** | `BE` | T01 |
| `P11-M04-T03` | Wire STT into `M27` conversation capture and `P02` voice notes | `M26` · `M27` · portal `P02` | STT integration | — | `BE` | T02 |
| `P11-M04-T04` | Confirm the **PDPA legal basis for transcript processing** before any mining | `SC-003` DPIA · `P07-M05-T04` | Confirmed legal basis | **The DPIA recorded W2 transcript mining with no confirmed legal basis.** Confirm it here or do not mine | `SL` | T03 |
| `P11-M04-T05` | Build remaining ML models: churn, fault prediction, parts demand, fraud detection | `M26` · `AR-011` | Model set | Each with a registered lineage in MLflow | `BE` | T01 |
| `P11-M04-T06` | Build model explainability for every model whose output affects a customer or an employee | `AR-011` · PDPA automated-decision provisions | Explainability | A pricing or scoring decision a person disputes must be reconstructable | `BE` | T05 |
| `P11-M04-T07` | Build the model-governance review cadence with the Design Authority | `AR-011` · `GV-002` | Governance cadence | — | `CA` | T05 |
| `P11-M04-T08` | Integrate `INT-009` instalments and `INT-045` speech-to-text | `05-03` §8 W8 | Integrations | — | `IL` | T02 |
| `P11-M04-T09` | Verify drift detection and retraining triggers fire correctly under injected drift | `P09-M06-T09` | Drift evidence | Test the alarm, not just the model | `QA` | T05 |
| `P11-M04-T10` | Complete `M26` to the full DoD | §0.8.2 | `M26` accepted | — | `BE` | T01–T09 |

---

## `P11-M05` — `M18` E-Waste, Recycling & Circular Economy

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P11-M05-T01` | Build the e-waste collection and drop-off model | `M18` · `CD-M18-nn` | E-waste module | 26 requirements, 13 PW | `OD` | — |
| `P11-M05-T02` | Build triage and material classification | `M18` · `M14` grading | Triage model | Composes the refurbishment grading from Phase 9 | `OD` | T01 |
| `P11-M05-T03` | Build **secure destruction with certificate issuance**, through `M06` | `M18` · `M06` · `P09-M05-T02` | Destruction flow | Journey 10: e-waste collection -> triage -> destruction -> recycling -> disposal certificate | `OD` | T02 |
| `P11-M05-T04` | Build the recycling and disposal chain with `M03` reverse logistics | `M18` · `M03` | Disposal chain | — | `OD` | T03 |
| `P11-M05-T05` | Integrate **`INT-040` e-waste authority reporting** | `05-03` §8 W8 · `SC-008` | Authority reporting | Regulatory. Verify the citation and record the verified-on date | `IL` | T04 |
| `P11-M05-T06` | Build ESG metrics and reporting through `M25` | `M18` · `M25` · `BM-004` | ESG reporting | Feeds benefits realisation | `OD` | T04 |
| `P11-M05-T07` | Wire e-waste collection booking into portal `P01` with loyalty points | `M18` · portal `P01` · `M10` | Customer booking | The customer-facing half of the circular loop | `FE` | T01 |
| `P11-M05-T08` | Build the disposal-certificate document through `M24`'s template engine | `M18` · `M24` | Certificate | Bengali and English | `OD` | T03 |
| `P11-M05-T09` | Emit `M18` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01 |
| `P11-M05-T10` | Complete `M18` to the full DoD | §0.8.2 | `M18` accepted | **All 67 modules delivered** | `OD` | T01–T09 |

---

## `P11-M06` — Analytics maturity and benefits measurement

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P11-M06-T01` | Read `BM-002` KPI baseline, `BM-003` business case, `BM-004` benefits realisation plan | `BM-002`…`BM-004` | Reading record | — | `DA` | — |
| `P11-M06-T02` | Verify **every one of the 95 registered KPIs is instrumented and visible in `M25`** | `DoD-09` · `BM-002` | KPI coverage report | `DoD-09` has applied to every module since Phase 3. This is the estate-wide check | `DA` | T01 |
| `P11-M06-T03` | Measure actuals against the `BM-002` baselines for every KPI with a baseline | `BM-002` | Actual-vs-baseline report | — | `DA` | T02 |
| `P11-M06-T04` | Build the executive benefits dashboard | `BM-004` · portal `P06` | Benefits dashboard | — | `DA` | T03 |
| `P11-M06-T05` | Reconcile the delivered benefit against the `BM-003` business case | `BM-003` | Benefit reconciliation | **The 3-year TCO moved from $455K–$780K to $690K–$1,150K.** The benefit case must be re-tested against the actual cost | `PM` | T03 |
| `P11-M06-T06` | Report on the headline KPIs: online booking rate (40% -> 88%), portal MAU (> 120,000), self-service status checks (> 80%) | portal `P01` KPIs | KPI report | — | `DA` | T03 |
| `P11-M06-T07` | Report on operational KPIs: SLA attainment, first-time fix, inventory accuracy, claim approval rate, payout accuracy | `06-02` | Operational KPI report | — | `DA` | T03 |
| `P11-M06-T08` | Report on `KPI-090` — **zero orphaned accounts beyond 24 hours** — across the whole programme | `P03-M08-T06` | Access hygiene report | The KPI that `MV-01` existed to make achievable | `SL` | T03 |
| `P11-M06-T09` | Build the ongoing benefits-tracking cadence for the post-closure period to Month 42 | `BM-004` · `MS-12` | Tracking cadence | The benefits realisation review is Month 42, six months after closure | `PM` | T04 |
| `P11-M06-T10` | Feed the measured results into `BM-005` lessons learned | `BM-005` | Lessons entries | — | `PM` | T05 |

---

## `P11-M07` — Performance and scale hardening at steady state

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P11-M07-T01` | Provision the **Wave 8 steady-state sizing** per TSS §21.1 | TSS §21.1 · `PE-006` | Sized estate | 4 Odoo app nodes (8 vCPU / 32 GB, 12 workers each) · 2 cron · 2 long-poll · PG primary 16 vCPU / 64 GB / 2 TB · 2 read replicas · resident store HA pair · TimescaleDB · ClickHouse · Redis · 3-node Apache Kafka · 3 Next.js nodes · 4 domain-service nodes · 20 TB object storage growing to 50 TB | `DE` | — |
| `P11-M07-T02` | Verify **`NFR-003` — 800+ concurrent internal users** at 1.5x peak | `NFR-003` · `DoD-14` | Performance evidence | 1,200 concurrent | `QA` | T01 |
| `P11-M07-T03` | Verify **`NFR-004` — 75,000+ concurrent portal users** at 1.5x peak | `NFR-004` | Performance evidence | 112,500 concurrent | `QA` | T01 |
| `P11-M07-T04` | Verify **`NFR-040` — invoice within 5 seconds of job close** under load | `NFR-040` | Performance evidence | — | `QA` | T02 |
| `P11-M07-T05` | Verify **`NFR-037` — offline sync within 30 s on 3G** at full device count | `NFR-037` · `AR-010` `SP-05` | Sync performance | Delta since token, never a full refresh | `QA` | T02 |
| `P11-M07-T06` | Verify **`NFR-008` zero-downtime deployment** with a real rolling release | `NFR-008` · `RL-002` §4.5 | Zero-downtime evidence | Four conditions, one of which `RL-002` §4.5 records as **nobody's** — resolve the ownership | `DE` | T01 |
| `P11-M07-T07` | Verify **HA on every critical component**: PostgreSQL primary, Keycloak, Kong, Nginx — **no single-node critical component is acceptable in production** | TSS §21.3 · `FF-105` | HA audit | Verify by killing nodes, not by reading configuration | `DE` | T01 |
| `P11-M07-T08` | Run the **DR drill** — RPO <= 15 min, RTO <= 2 h — and record it | `NFR-007` · `PE-007` · `FF-98` | DR drill record | Twice yearly. This is one of them | `DE` | T07 |
| `P11-M07-T09` | Verify **weekly automated restore verification** is running and has never silently failed | `NFR-052` · `FF-126` | Restore evidence | A backup nobody has restored is a hope | `DE` | T08 |
| `P11-M07-T10` | Re-baseline `PE-006` capacity against measured production load and project to Year 5 | `PE-006` | Re-baselined capacity | — | `DE` | T02, T03 |

---

## `P11-M08` — Technical debt burn-down

**This milestone uses the spare capacity `GV-004` §5.3 identified. It is not optional and it is not filler.**

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P11-M08-T01` | Review the whole `BE-009` technical-debt register and prioritise | `BE-009` | Prioritised debt register | Every `DBT-nnn` with an owner and a disposition | `EL` | — |
| `P11-M08-T02` | Burn down every **Warning-level fitness function** to zero and promote it to Blocking | `AR-012` §5.2 promotion rule | Promoted checks | `FF-13`, `FF-14`, `FF-27` and the rest. **A Warning that never becomes Blocking is a check nobody obeys** | `CA` | T01 |
| `P11-M08-T03` | Complete the **242 event renames** `RM-03` requires and enable `FF-60` as Blocking | `IN-003` `RM-03` · `P03-M03-T07` | Renames complete; `FF-60` blocking | Deferred since Phase 3. This is where it closes | `IL` | T01 |
| `P11-M08-T04` | Close the **1,152 outstanding OpenAPI operations** or formally descope the remainder | `IN-002` · `B-16` | Contract completion or descope | **169–338 PW, in no plan.** Report the final position honestly rather than leaving it open | `IL` | T01 |
| `P11-M08-T05` | Close the **69 unpublished portal-consumed events** — rename, project, or register | `IN-003` · `B-17` | Event reconciliation complete | — | `IL` | T01 |
| `P11-M08-T06` | Verify **`FF-16` is Blocking** and every manifest in the estate carries an issued `CD-<UNIT>-<nn>` | `BE-005` §10 · `AR-012` | `FF-16` blocking | Promoted at `G1`; verified estate-wide here | `CA` | T01 |
| `P11-M08-T07` | Re-run **`FF-14` reciprocity** across all 79 units — the 55 one-way declarations must be zero | `AR-006` §7 | Reciprocity zero | — | `SA` | T01 |
| `P11-M08-T08` | Audit `FORKS.yaml` — **every entry must have a justification, an owner and an upstream contribution or removal plan** | `AS-05` · `FF-03` | Fork audit | Ideally the file is still empty | `CA` | T01 |
| `P11-M08-T09` | Review every **review-only `BE-002` rule** — `PYS-22` `sudo()` justification, `PYS-20` timeout/retry/fallback, `FL-03` one offline engine, `SQL-05` two-release column lifecycle | `BE-002` §10 | Review-only audit | **Twenty-two rules have no tool. Four of them are the most consequential in the document.** This is the only pass that checks them estate-wide | `EL` | T01 |
| `P11-M08-T10` | Publish the residual technical-debt position for the post-closure support organisation | `BE-009` · `SV-001` | Residual debt register | Handing over undisclosed debt is handing over a fault | `EL` | T02–T09 |

---

## `P11-M09` — Test estate consolidation

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P11-M09-T01` | Give an **identifier to every executable test item** — 620 of ~1,700 currently carry one | `QA-001` §4.4 `QAA-03` · `QA-003` §5 | Identified test estate | **An item with no identifier cannot be traced, reported, counted or declared covered** — roughly two-thirds of the estate sits outside `MTS-R1` | `QA` | — |
| `P11-M09-T02` | Consolidate the **six incompatible identifier schemes** into one | `QA-001` §4.4 | Single scheme | — | `QA` | T01 |
| `P11-M09-T03` | Build and automate the **`TS-013` permanent regression core** — currently defined and **not automated** | `QA-001` §6.1 | Automated regression | *"`TS-013` defines a regression pack and a smoke checklist. Nothing automates them."* | `QA` | T02 |
| `P11-M09-T04` | Verify the **automation ratio** against the layer strategy: ~70% unit, ~25% API/contract/event, ~5% UI/journey | `QA-001` §6.2, §6.4 | Ratio measurement | The declared departure from the 70/20/10 pyramid, verified | `QA` | T03 |
| `P11-M09-T05` | Verify **all 15 critical journeys** are automated and running nightly | TSS §20.4 · `QA-001` `L6` | Journey coverage | All fifteen, not the twelve that were convenient | `QA` | T03 |
| `P11-M09-T06` | Complete `QA-011` requirements-to-test coverage reporting from **normalised pipeline output**, not by assertion | `QA-011` · `PE-004` `RN-02`, `RN-04` | Coverage report | `RN-04` made this measurable in Phase 2. This is where it is used | `QA` | T02 |
| `P11-M09-T07` | Close the **five unresourced execution dependencies** `QA-001` §10.4 records | `QA-001` §10.4 | Dependency closure | Including `TAF-58` mobile device access (`Q-04`) | `QA` | T01 |
| `P11-M09-T08` | Verify **`DoD-03` coverage estate-wide**: >= 80% overall, **100% on every financial and tax path** across all 67 modules | `DoD-03` | Estate coverage report | Per module, not in aggregate. An aggregate hides a zero | `QA` | T06 |
| `P11-M09-T09` | Run the full **`L9` security test** and a penetration test per `SC-009` against the complete estate | `QA-007` · `SC-009` | Security report | 97 threats, 32 abuse cases. **Zero open high or critical** (`DoD-15`) | `SL` | — |
| `P11-M09-T10` | Run the full **`L10` accessibility audit** — automated **plus manual, per portal**, all twelve | `QA-008` · `UX-005` | Accessibility report | **Automated scans find a minority of WCAG failures.** The manual half is the half that matters | `UX` | — |

---

## `P11-M10` — Gate `G8` — Full intelligence go-live (`MS-10`, Month 34)

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P11-M10-T01` | Run the `T−6` entry criteria check | `GV-009` §9.2 | Entry record | — | `PM` | — |
| `P11-M10-T02` | Verify **all 67 modules and all 12 portals are delivered and accepted** | `02-02` · `04-00` | Delivery evidence | 79 delivery units | `PM` | T01 |
| `P11-M10-T03` | Verify the **warehouse migration is complete** and `NFR-039` is met at 1.5x peak | `P11-M01` | Warehouse evidence | — | `QA` | T01 |
| `P11-M10-T04` | Verify **journey 10** — e-waste collection to disposal certificate — is automated and running nightly, and **all 15 journeys are green** | TSS §20.4 | E2E evidence | — | `QA` | T01 |
| `P11-M10-T05` | Verify **all 95 KPIs are instrumented** and actuals are reported against baselines | `P11-M06` | KPI evidence | — | `DA` | T01 |
| `P11-M10-T06` | Verify **every Warning fitness function is Blocking** and violation counts are zero | `P11-M08-T02` | Fitness evidence | — | `CA` | T01 |
| `P11-M10-T07` | Verify the **regression core is automated** and the automation ratio meets the layer strategy | `P11-M09` | Test evidence | — | `QA` | T01 |
| `P11-M10-T08` | Verify **zero open high or critical security findings** across the complete estate | `DoD-15` · `SC-009` | Security evidence | — | `SL` | T01 |
| `P11-M10-T09` | Run the `gate` profile at **full steady-state load** with the DR drill | `PE-004` §4.2 · `P11-M07` | Gate results | — | `DE` | T01 |
| `P11-M10-T10` | **Gate `G8`.** Steering signs. Publish report and residuals | `GV-009` §8.4 | Signed `G8`; `MS-10` | — | `PM` | T02–T09 |

---
---

# PHASE 12
## EXPANSION, DECOMMISSIONING & PROGRAMME CLOSURE

### Wave 9 · Months 35–36 · 8.7 weeks · Sprints 77–80 · Gate `G9` · Milestones `MS-11`, `MS-12`

---

## 12.0 Phase charter

| | |
|---|---|
| **Purpose** | Make the platform multi-entity and multi-country ready, retire the legacy estate, transition to support, and close the programme against its own business case |
| **Tier** | `T12` expansion |
| **Modules** | `M65` GLO — and verification that `M66` (Phase 9) and `M67` (Phase 10) are complete |
| **Technology** | Multi-entity, multi-country localisation · international payments (`INT-008`) · freight forwarder (`INT-027`) · company registry (`INT-042`) |
| **Effort** | 23 PW against ~34 effective PW — **0.68x** |
| **Exit** | `G9` — 5 criteria, Month 36. `MS-11` programme closure. `MS-12` benefits realisation review at Month 42 |

> **`MIG-08` governs this phase.** *"Legacy systems are decommissioned only after reconciliation
> sign-off, not on go-live day."* Some legacy systems have been running in parallel since Phase 4.
> This is where they are retired — deliberately, with sign-off, and never before.

---

## `P12-M01` — `M65` Multi-Entity, Multi-Country & Localisation

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P12-M01-T01` | Build multi-entity support on `M30`'s `fix.entity` and the OCA `operating-unit` model | `M65` · `M30` | Multi-entity | 30 requirements, 20 PW. The foundation was laid in Phase 3 | `OD` | — |
| `P12-M01-T02` | Build multi-country localisation on `M30`'s **`cd_country_pack` interface** | `M65` · `P03-M04-T04` | Country packs | **`M51` was declared against the country-pack interface, not against `M65`** — that violation closed in Phase 1 | `OD` | T01 |
| `P12-M01-T03` | Break the **`M51 <-> M65` cycle** by confirming `M51` depends on the interface, not the module | `AR-006` §4.1 pair 18, §5.2 | Cycle closed | — | `SA` | T02 |
| `P12-M01-T04` | Build multi-currency support with explicit `currency_id` throughout | `M65` · `AS-10` | Multi-currency | **Money always carries its currency.** This is where `AS-10` pays off | `OD` | T01 |
| `P12-M01-T05` | Build inter-entity transactions and elimination for consolidated reporting | `M65` · `M19` · `M54` | Inter-entity | — | `OD` | T04 |
| `P12-M01-T06` | Integrate `INT-008` international payments, `INT-027` freight forwarder, `INT-042` company registry | `05-03` §8 W9 | 3 integrations | — | `IL` | T04 |
| `P12-M01-T07` | Verify **residency rules apply per country**, not only for Bangladesh | `SC-007` · `D-013` | Multi-residency verification | A second country means a second residency regime. The architecture supports it because Z4 was built as a pattern, not a special case | `SL` | T02 |
| `P12-M01-T08` | Achieve 100% coverage on inter-entity and multi-currency calculation | `DoD-03` | Coverage report | — | `QA` | T04, T05 |
| `P12-M01-T09` | Emit `M65` events and register them | `AS-08` · `IN-003` | Registered events | — | `OD` | T01 |
| `P12-M01-T10` | Complete `M65` to the full DoD | §0.8.2 | `M65` accepted | **All 67 modules complete** | `OD` | T01–T09 |

---

## `P12-M02` — Legacy decommissioning

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P12-M02-T01` | Read `RL-006` legacy decommissioning plan and `02-02` §9 legacy decommission map | `RL-006` · `02-02` §9 | Reading record | — | `ML` | — |
| `P12-M02-T02` | Verify **reconciliation sign-off exists for every legacy system** before touching it | `MIG-08` | Sign-off register | **`MIG-08`: decommissioned only after reconciliation sign-off, not on go-live day** | `ML` | T01 |
| `P12-M02-T03` | Decommission `station.1000fix.com` order tracking | `02-02` §9 · TSS §19.1 | Decommissioned | — | `ML` | T02 |
| `P12-M02-T04` | Decommission the legacy tracker at `123.0.26.238/orderTracking` | `02-02` §9 | Decommissioned | — | `ML` | T02 |
| `P12-M02-T05` | Withdraw the per-branch service-order spreadsheets across all 51+ branches | `02-02` §9 | Withdrawn | The largest and most distributed legacy surface | `TR` | T02 |
| `P12-M02-T06` | Decommission the standalone accounting software after a full reconciled year-end | `02-02` §9 | Decommissioned | Balances and open items migrated; transaction history retained in archive, not in the new system | `ML` | T02 |
| `P12-M02-T07` | Withdraw the AMC tracking spreadsheets, email-based warranty claims and manual Excel payroll | `02-02` §9 · TSS §19.1 | Withdrawn | — | `ML` | T02 |
| `P12-M02-T08` | Archive every legacy dataset under `DA-006` retention with its **permanent legacy reference** intact | `DA-006` · `MIG-03` | Archived datasets | `FR-SRM-088` legacy order lookup must keep working after decommissioning | `DA` | T03–T07 |
| `P12-M02-T09` | Verify **no live process still depends on any decommissioned system** — check by observation, not by asking | `RL-006` | Dependency verification | The shadow spreadsheet nobody mentioned is the one that breaks | `SO` | T08 |
| `P12-M02-T10` | Publish the decommissioning record with dates, sign-offs and archive locations | `RL-006` | Decommissioning record | — | `ML` | T09 |

---

## `P12-M03` — Delivery completeness verification

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P12-M03-T01` | Verify **all 67 module specifications have a delivered, accepted module** | `02-02` | Module completeness | Including `M66` (Phase 9) and `M67` (Phase 10), whose specifications were **baselined**, not written, in Phase 1 — they already existed | `PM` | — |
| `P12-M03-T02` | Verify **all 12 portals** are delivered and accepted | `04-00` | Portal completeness | — | `PM` | — |
| `P12-M03-T03` | Verify **all 331 `CD-<UNIT>-<nn>` items** are delivered, descoped-with-a-decision, or retired with a tombstone | `BE-005` §6, §8.3 | CD completeness | `CDR-04` — a withdrawn identifier is retired with a tombstone row and **never reissued** | `CA` | — |
| `P12-M03-T04` | Verify **requirements coverage against the 3,389 engineering baseline**, and report the delivered position against the 2,930 contracted | `RQ-004` · `CO-003-F-08` | Coverage report | **Report both numbers.** The resolved requirement gap is a contractual fact, not a rounding difference | `BA` | — |
| `P12-M03-T05` | Verify **all 122 NFRs** are realised and verified by their stated method | `RQ-006` · `05-06` | NFR verification | — | `QA` | — |
| `P12-M03-T06` | Verify **all 47 integrations** are live, or descoped with a decision and a documented manual fallback | `05-03` | Integration completeness | `06-01` §9: *"Key integration blocked externally -> deliver the module with the documented manual fallback"* | `IL` | — |
| `P12-M03-T07` | Verify **all 60 automations `AUT-001`…`AUT-060`** are live with a named execution engine | `05-05` §12 | Automation completeness | — | `OD` | — |
| `P12-M03-T08` | Verify **all 53 roles, 6 tiers and 61 SoD controls** are implemented and negative-tested | `05-04` · `SP-006` | Access completeness | — | `SL` | — |
| `P12-M03-T09` | Verify the **452 content files** are written, approved and loaded — and report any still at Draft | `project_content` master index | Content completeness | **452 written, 0 approved at handover.** This is where that closes, or where the residual is named | `CN` | — |
| `P12-M03-T10` | Publish the **delivery completeness statement** with every gap named, owned and dated | `GV-009` | Completeness statement | Nothing is closed by omission | `PM` | T01–T09 |

---

## `P12-M04` — Hypercare and transition to support

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P12-M04-T01` | Read `SV-005` hypercare and transition plan and `SV-001` service management framework | `SV-005` · `SV-001` | Reading record | **Hypercare recurs per wave — `SV-005` §4.1 records that `OP-002`'s figure does not add up.** Verify the recurrence calendar | `SO` | — |
| `P12-M04-T02` | Establish the **ring-fenced hypercare resource** and record what it displaces | `SV-005` §6.1–§6.2 | Ring-fence | Three cost pools: project effort, support effort, **business effort — the third is in no estimate at all** | `PM` | T01 |
| `P12-M04-T03` | Stand up the support organisation per `SV-001` with `SV-002` SLAs and OLAs | `SV-001` · `SV-002` | Support organisation | — | `SO` | T01 |
| `P12-M04-T04` | Complete the **`SV-003` operational runbook master set** — one runbook per module, per `DoD-11` | `SV-003` · `DoD-11` | Complete runbook set | 79 delivery units, 79 runbooks minimum | `SO` | T01 |
| `P12-M04-T05` | Establish **`SV-004` on-call, paging and escalation** | `SV-004` | On-call rota | — | `SO` | T03 |
| `P12-M04-T06` | Establish `SV-006` problem and major-incident management | `SV-006` | Incident procedures | Including the PDPA breach-notification path from Phase 7 | `SO` | T03 |
| `P12-M04-T07` | Run **knowledge transfer** from the build squads to the support organisation, module by module | `SV-005` · `CH-002` | Knowledge transfer record | **Two-person minimum knowledge coverage on every module** (`06-01` §9 attrition contingency) | `EL` | T04 |
| `P12-M04-T08` | Hand over the **residual technical-debt register** and the residual open-item register | `P11-M08-T10` · `BE-009` | Handover registers | — | `EL` | T07 |
| `P12-M04-T09` | Run the transition-to-support acceptance with the support organisation as the accepting party | `SV-005` | Transition acceptance | The support organisation accepts, not the build team | `SO` | T07, T08 |
| `P12-M04-T10` | Exit hypercare against measured criteria, not against a date | `SV-005` | Hypercare exit record | — | `SO` | T09 |

---

## `P12-M05` — Documentation and knowledge handover

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P12-M05-T01` | Verify **every `cd_*` module carries its mandatory `README.md`, `runbook.md` and `openapi.yaml`** where it exposes an API | `AR-007` §3.1 `L5-01` · `DoD-06`, `DoD-11` | Artefact verification | Mandatory, not recommended | `EL` | — |
| `P12-M05-T02` | Verify the `AR-004` ADR library records every architecture decision taken across 36 months | `AR-004` | ADR completeness | A decision with no ADR is a decision nobody can revisit | `CA` | — |
| `P12-M05-T03` | Update `AR-001` SAD, `AR-002` blueprint and `AR-003` SDDs to **as-built**, not as-designed | `AR-001`…`AR-003` | As-built architecture | The gap between designed and built is the most expensive thing to rediscover | `CA` | — |
| `P12-M05-T04` | Update `DA-001` and `DA-002` to the as-built schema and data dictionary | `DA-001` · `DA-002` | As-built data model | — | `DA` | — |
| `P12-M05-T05` | Publish the complete **OpenAPI contract set** and the **event catalogue** as the integration surface of record | `IN-002` · `IN-003` | Published contracts | For every future integrator | `IL` | — |
| `P12-M05-T06` | Complete the `project_content` **`AP-*` integration and developer content** — 12 files | `project_content` 15 | Developer content | — | `CN` | T05 |
| `P12-M05-T07` | Complete the **`OP-*` operations, support and runbook content** — 16 files | `project_content` 17 | Operations content | — | `CN` | `P12-M04-T04` |
| `P12-M05-T08` | Verify all **266 files requiring a Bengali counterpart** have one | `project_content` master index · `CM-R6` | Bengali completeness | — | `LL` | — |
| `P12-M05-T09` | Verify all **61 files requiring legal or statutory sign-off** have it | `project_content` master index | Legal sign-off | — | `CN` | — |
| `P12-M05-T10` | Confirm **continuous source delivery is complete** — all source, configuration, migrations, tests and documentation in the Company-controlled repository | TSS §18.1 · RFP §5.10 · `P01-M08-T08` | Delivery confirmation | **1000FiX property, delivered continuously — not at milestones** | `PM` | T01–T09 |

---

## `P12-M06` — Change, training and adoption closure

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P12-M06-T01` | Verify **role-based training delivered for all 53 roles**, in Bengali | `CH-002` · `DoD-13` | Training completeness | — | `TR` | — |
| `P12-M06-T02` | Verify the **champion network** is established and self-sustaining — one per branch, monthly forum | `CH-005` | Champion network | 51+ branches | `TR` | — |
| `P12-M06-T03` | Report **adoption by role and branch**, and remediate anywhere below threshold | `CH-004` | Adoption report | Weekly reporting since Phase 4. This is the closing position | `TR` | — |
| `P12-M06-T04` | Report adoption specifically for the **critical-risk groups**: field technicians, branch counter staff, marketplace sellers | `06-01` §7 adoption risk | Risk-group report | **Field technician app rejection collapses the field model.** This is the group to report on first | `TR` | T03 |
| `P12-M06-T05` | Complete the **24 `TR-*` training and 20 `HC-*` help-centre content files** | `project_content` 08, 09 | Content complete | — | `CN` | — |
| `P12-M06-T06` | Complete the **18 `CM-*` change management and communications files** | `project_content` 16 | Change content | — | `CN` | — |
| `P12-M06-T07` | Transfer training ownership to the internal training function | `CH-002` · `CH-005` | Ownership transfer | Training does not end at closure; ownership moves | `TR` | T01 |
| `P12-M06-T08` | Run the final stakeholder engagement review per `CH-003` | `CH-003` | Engagement review | — | `TR` | — |
| `P12-M06-T09` | Publish the reinforcement plan for the post-closure period | `CH-004` | Reinforcement plan | Adoption decays without reinforcement | `TR` | T03 |
| `P12-M06-T10` | Feed adoption findings into `BM-005` lessons learned | `BM-005` | Lessons entries | — | `TR` | T03 |

---

## `P12-M07` — Security, compliance and audit closure

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P12-M07-T01` | Run a **final penetration test** against the complete estate | `SC-009` | Penetration test report | — | `SL` | — |
| `P12-M07-T02` | Verify **zero open high or critical findings** across all 79 delivery units | `DoD-15` | Security position | — | `SL` | T01 |
| `P12-M07-T03` | Run the final **PDPA compliance audit** — consent, DSR, erasure, residency, breach notification | `SC-003` · `SC-008` | Compliance audit | Enforcement has been live since Phase 7 | `SL` | — |
| `P12-M07-T04` | Verify **residency conformance estate-wide** — no `S3` data outside Z4, in any store, cache, log, index or backup | `SC-007` · `FF-09` | Residency audit | Audit the artefacts, not the design | `SL` | — |
| `P12-M07-T05` | Verify **`IP-10` egress logging** — every outbound call logged, every destination allow-listed | TSS §3.4 | Egress audit | — | `SL` | — |
| `P12-M07-T06` | Verify **`SC-010` audit logging and forensic readiness**, including privileged session recording | `SC-010` · `NFR-070` | Audit-log verification | — | `SL` | — |
| `P12-M07-T07` | Re-verify **every regulatory citation** with a fresh verified-on date | `DoD-17` · `RR-005` · `SC-008` | Currency verification | Against upstream, not against the last document | `BA` | — |
| `P12-M07-T08` | Verify **ISO 9001:2015** readiness — zero major non-conformances traced to systems | `CON-11` · `M23` | ISO readiness | — | `QA` | — |
| `P12-M07-T09` | Complete `CO-004` open-source licence compliance and publish the final SBOM | `CO-004` · `BE-007` | SBOM + licence register | Every AGPL, BSL, TSL and fair-code component approved and recorded | `CA` | — |
| `P12-M07-T10` | Hand the security posture to the support organisation with the open-risk register | `SC-011` · `SV-001` | Security handover | — | `SL` | T02–T09 |

---

## `P12-M08` — Programme financial and commercial closure

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P12-M08-T01` | Reconcile **actual effort against the 1,842 PW baseline**, per category and per wave | `GV-007` · `GV-008` · `BE-005` §7 | Effort reconciliation | The measured answer to the 1.69x over-commitment | `PM` | — |
| `P12-M08-T02` | Reconcile **actual cost against the $690K–$1,150K 3-year TCO** | `CO-005` · `GV-008` | Cost reconciliation | — | `PM` | T01 |
| `P12-M08-T03` | Publish the **measured squad velocity conversion factors** and the actual delivery factor against the assumed 0.78 | `BE-008` §5.2 · `GV-004-A1` | Measured factors | **The 0.78 factor was an industry convention, never a 1000FiX measurement.** This is where it becomes one | `EL` | T01 |
| `P12-M08-T04` | Report infrastructure cost against the $52K–$96K three-year projection | `CO-005` · TSS §21.2 | Infrastructure reconciliation | — | `DE` | T02 |
| `P12-M08-T05` | Report **L6 commercial licence cost against the $0–36K envelope**, and re-run the annual OSS alternative review | TSS §9, §22 · `CO-004` | Licence reconciliation | **This is what prevents "zero licence cost" degrading into unbounded SaaS sprawl** | `PM` | T02 |
| `P12-M08-T06` | Complete `CO-003` deliverable acceptance against the Statement of Work | `CO-003` | Acceptance record | Including the disposition of the resolved requirement gap | `PM` | T01 |
| `P12-M08-T07` | Close the `GV-005` RAID register — every risk, assumption, issue and dependency closed or transferred | `GV-005` | Closed RAID | Transferred items name their new owner | `PM` | — |
| `P12-M08-T08` | Close the `GV-003` decision log — every `D-nnn` and `CR-nnn` resolved | `GV-003` | Closed decision log | — | `PM` | — |
| `P12-M08-T09` | Complete `GV-011` configuration-management closure and baseline the final estate | `GV-011` | Final baseline | — | `PM` | — |
| `P12-M08-T10` | Publish the programme financial closure statement | `GV-008` | Closure statement | — | `PM` | T01–T09 |

---

## `P12-M09` — Post-implementation review and lessons learned

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P12-M09-T01` | Run the `RL-005` post-implementation review | `RL-005` | PIR report | — | `PM` | — |
| `P12-M09-T02` | Run the `GV-010` independent assurance review | `GV-010` | Assurance report | Independent of the delivery organisation | `PM` | — |
| `P12-M09-T03` | Complete the `BM-005` lessons-learned register with contributions from every squad | `BM-005` | Lessons register | — | `PM` | T01 |
| `P12-M09-T04` | Record the estimation lessons specifically: **requirements under-estimated by 21%, effort by 15%, and category variance from 0% to +73%** | `02-02` §3.1 | Estimation lessons | **The pattern had a cause: requirement count is under-estimated wherever a category carries statutory, contractual or master-data obligations** | `PM` | T03 |
| `P12-M09-T05` | Record the sequencing lessons: **32 wave-order violations, 18 cycles, 5 mandatory scope movements** — all found by a dependency analysis that was never run before the plan was written | `AR-006` | Sequencing lessons | *"High in-degree plus a late wave is the structural signature of a wave plan built from business priority rather than from the dependency graph"* | `CA` | T03 |
| `P12-M09-T06` | Record the identifier-discipline lessons: **48 CD collisions, 55 reciprocity failures, six live values for one entity count** | `BE-005` §8.2 · `AR-006` §7 · alignment audit | Identifier lessons | **`RG-08` — every counted figure carries the timestamp that made it true — was recommended ten times and ratified once, in Phase 1** | `CA` | T03 |
| `P12-M09-T07` | Record the content lessons: **452 files, 0 approved at handover, 520–775 PW unbudgeted** | `project_content` · `AF-09` | Content lessons | *"An ERP fails on content far more often than on code"* | `CN` | T03 |
| `P12-M09-T08` | Record the capacity lessons: **1.69x over-commitment, an inverted team ramp, and a business-side capacity check that was never performed** | `GV-004` §5 · `BE-005` §7.5 | Capacity lessons | — | `PM` | T03 |
| `P12-M09-T09` | Publish the lessons register to the organisation, not only to the programme | `BM-005` | Published lessons | A lessons register nobody outside the programme reads has taught nobody | `PM` | T03–T08 |
| `P12-M09-T10` | Schedule the **`MS-12` benefits realisation review at Month 42** with `GV-010` independent audit | `BM-004` · `GV-010` · `MS-12` | Scheduled review | Six months after closure, when benefits are measurable rather than projected | `PM` | T02 |

---

## `P12-M10` — Gate `G9` — Programme closure (`MS-11`, Month 36)

| ID | Task | Reads | Produces | Verify | Role | Dep |
|---|---|---|---|---|---|---|
| `P12-M10-T01` | Run the `T−6` entry criteria check | `GV-009` §9.2 | Entry record | — | `PM` | — |
| `P12-M10-T02` | Verify **`M65` multi-entity and multi-country readiness** demonstrated | `06-01` W9 gate | Expansion evidence | Readiness, not a second country in production | `QA` | T01 |
| `P12-M10-T03` | Verify **the legacy estate is decommissioned** with reconciliation sign-off on every system | `P12-M02` | Decommissioning evidence | `MIG-08` | `ML` | T01 |
| `P12-M10-T04` | Verify **delivery completeness** — 67 modules, 12 portals, 331 CD items, 47 integrations, 60 automations, 122 NFRs, 452 content files | `P12-M03` | Completeness statement | With every gap named, owned and dated | `PM` | T01 |
| `P12-M10-T05` | Verify **transition to support is accepted** by the support organisation | `P12-M04-T09` | Transition acceptance | — | `SO` | T01 |
| `P12-M10-T06` | Verify **benefits measurement is operating** and actuals are reported against the `BM-002` baselines | `P11-M06` · `BM-004` | Benefits evidence | — | `DA` | T01 |
| `P12-M10-T07` | Verify **security, compliance and audit closure** | `P12-M07` | Closure evidence | — | `SL` | T01 |
| `P12-M10-T08` | Verify **financial and commercial closure**, including the disposition of the 459-requirement contractual gap | `P12-M08` | Financial closure | — | `PM` | T01 |
| `P12-M10-T09` | Run the final `gate` profile and the DR drill | `PE-004` §4.2 · `PE-007` | Gate results | — | `DE` | T01 |
| `P12-M10-T10` | **Gate `G9`.** Steering signs programme closure. Publish the closure report, the residual register and the Month 42 review schedule | `GV-009` §8.4 · `MS-11`, `MS-12` | Signed `G9`; programme closed | **Publish the residuals. A programme that closes with an empty residual register has hidden something** | `PM` | T02–T09 |

---
---

# PART 2 — APPENDICES

---

## APPENDIX A — Developer workstation build, end to end

**Run in order on a fresh Ubuntu 22.04 or 24.04 LTS install. Total budget: 1.6–2.7 hours on the `core` profile.**
Every step traces to Phase 2. Do not substitute versions; every pin comes from `tooling/versions.lock`.

### A.1 System packages — `P02-M01-T04`

```bash
sudo apt update && sudo apt install -y \
  build-essential git curl \
  python3.12 python3.12-dev python3.12-venv \
  libpq-dev libxml2-dev libxslt1-dev libjpeg-dev libldap2-dev libsasl2-dev \
  libssl-dev libffi-dev zlib1g-dev \
  postgresql-client-17 \
  wkhtmltopdf \
  fonts-noto fonts-noto-bengali fonts-lohit-beng-bengali
```

### A.2 Docker and git — `P02-M01-T06`, `P02-M01-T07`

```bash
# Docker Engine 24+ with Compose v2 — follow the official Docker repository instructions
sudo usermod -aG docker "$USER"      # log out and back in
docker compose version               # must report v2.x

git --version                        # must be >= 2.40
```

### A.3 Toolchains — `P02-M02`

```bash
# Python
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node — nvm reads .nvmrc from the repository
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
nvm install                          # reads .nvmrc -> Node 20 LTS
npm install -g pnpm

# Dart / Flutter — only if D-027 ruled Flutter
dart pub global activate fvm
fvm install                          # reads .fvmrc

# Go — for services/telemetry-collector
# install per go.mod toolchain directive
```

### A.4 git configuration — `P02-M02-T07`, `P02-M02-T08`

```bash
git config --global core.autocrlf false          # XS-01 — false, not true
git config --global user.name  "<name>"
git config --global user.email "<company email>"
git config --global commit.gpgsign true          # branch protection precondition
gh auth login                                    # GitHub CLI
```

### A.5 Clone and bootstrap — `P02-M04`, `P02-M06-T01`

```bash
git clone --recurse-submodules <host>/1000fix-erp   # 20–40 min: vendor/ is large
cd 1000fix-erp
make bootstrap                                      # 15–25 min
```

### A.6 Start the stack and Odoo — `P02-M05`, `P02-M06`

```bash
make up                        # core profile: PostgreSQL, Redis, Ceph Object Storage, Mailpit (~2 GB)
# make up PROFILE=auth         # + Keycloak, PgBouncer          (~3.5 GB)
# make up PROFILE=integration  # + Kong, Apache Airflow, Novu              (~5 GB)
# make up PROFILE=field        # + Traccar, OSRM, VROOM         (~7 GB)
# make up PROFILE=observability# + Prometheus, Grafana, Loki, Tempo (~8 GB)
# make up PROFILE=full         # everything                     (~10–12 GB)

cp .env.example .env           # .env is git-ignored and never committed
make odoo-conf                 # GENERATES infra/odoo-conf/local.conf — never hand-write it
make db-create
make odoo-init
make odoo-install-wave1        # 15–30 min
make seed                      # deterministic, Bengali-first, every state machine state
make run                       # http://127.0.0.1:8069
```

### A.7 Verify — `P02-M10`

```bash
make doctor                    # 14 checks. MUST be green before any work begins (DE-19)
make test-smoke                # < 3 min, one path end to end
pre-commit run -a              # green on a clean tree
```

### A.8 Daily commands

```bash
make up / make down            # stop keeps data
make reset                     # down -v, recreate, reseed — the ONLY thing that destroys data
make upgrade MODULE=cd_x       # needed after a manifest, new model or new field change
make test                      # full local suite
make odoo-conf                 # re-run whenever a module category is added
```

### A.9 If something is wrong — the failures that will actually occur

| Symptom | Cause | Remedy |
|---|---|---|
| `lxml` / `python-ldap` build failure during `uv sync` | Missing `libxml2-dev` / `libxslt1-dev` / `libsasl2-dev` / `libldap2-dev` | §A.1. **The most common first-hour failure** |
| No `cd_*` module appears in Apps | Stale `addons_path`, or module list not updated | `make odoo-conf`, then Apps -> Update Apps List |
| A breakpoint never fires | `workers > 0`; Odoo forked | `workers = 0` in `local.conf` |
| PDF renders blank or unstyled | Distribution `wkhtmltopdf` is unpatched Qt | Install Odoo's patched build |
| Bengali renders as boxes or wrong conjuncts | Missing Noto/Lohit Bengali on the host **or in the report container** | §A.1; `TR-07` |
| `port is already allocated` | Host PostgreSQL or Redis running | Stop the host service. **`DE-01`: nothing but Odoo on the host** |
| `docker compose up` OOM-kills containers | `full` profile on 16 GB | Use `core` |
| Odoo starts against the wrong database | `.env` and `local.conf` disagree | `make doctor` check 4; `DE-11` |
| Tests pass locally, fail in CI | Test residue or ordering dependence | Run `make test` on a fresh `make reset` |
| Pre-commit rejects unrelated files | Formatter running for the first time on the tree | Commit the formatting separately |
| Everything is slow (WSL2) | Repository under `/mnt/c/` | Clone inside the WSL2 filesystem (`~/src/1000fix-erp`) |

> **Add to this table whenever you solve something.** `BE-001` §9 is explicit: entries are added by
> the person who solved the problem, not by the document's owner.

---

## APPENDIX B — VS Code workspace configuration

### B.1 `.vscode/extensions.json` — commit this

```jsonc
{
  "recommendations": [
    // Required — BE-001 §8.1
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "ms-azuretools.vscode-docker",
    "redhat.vscode-xml",
    "dart-code.flutter",
    "dart-code.dart-code",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "eamodio.gitlens",
    "humao.rest-client",
    // Added by IR-001 for this estate — P02-M07-T02
    "redhat.vscode-yaml",
    "tamasfe.even-better-toml",
    "usernamehw.errorlens",
    "Gruntfuggly.todo-tree",
    "ryanluker.vscode-coverage-gutters",
    "DavidAnson.vscode-markdownlint",
    "bierner.markdown-mermaid",
    "github.vscode-github-actions",
    "ms-playwright.playwright"
  ],
  "unwantedRecommendations": [
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.pylint"
  ]
}
```

> **`unwantedRecommendations` is doing real work.** Two Python formatters fighting over the same
> file produces a diff war that costs more than either saves. Ruff is the formatter **and** the
> linter (`BE-002` `PYS-01`).

### B.2 `.vscode/settings.json` — commit this

```jsonc
{
  "files.eol": "\n",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": { "source.fixAll.ruff": "explicit",
                                  "source.organizeImports.ruff": "explicit" }
  },
  "[typescript]":     { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[typescriptreact]":{ "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[xml]":            { "editor.defaultFormatter": "redhat.vscode-xml" },
  "[dart]":           { "editor.defaultFormatter": "dart-code.dart-code" },
  "python.analysis.typeCheckingMode": "strict",
  "eslint.options": { "maxWarnings": 0 },
  "xml.fileAssociations": [
    { "pattern": "**/views/*.xml",    "systemId": "vendor/odoo/odoo/import_xml.rng" },
    { "pattern": "**/data/*.xml",     "systemId": "vendor/odoo/odoo/import_xml.rng" },
    { "pattern": "**/security/*.xml", "systemId": "vendor/odoo/odoo/import_xml.rng" }
  ],
  "files.exclude": { "**/__pycache__": true, "**/.pytest_cache": true },
  "search.exclude": { "vendor/**": true },
  "todo-tree.general.tags": ["TODO", "FIXME", "DBT-"],
  "coverage-gutters.coverageFileNames": ["coverage.xml", "lcov.info"]
}
```

> **`search.exclude: vendor/**`** is not cosmetic. Searching an 18-subtree OCA checkout plus the
> Odoo source returns thousands of irrelevant hits and trains developers to stop searching. When you
> genuinely need to read framework source — which `AS-05` requires you to do — search it explicitly.

### B.3 `.vscode/launch.json` — commit this

See `P02-M07-T03`. Two configurations, both with `"justMyCode": false`.

### B.4 Browser and DevTools workflow — `P02-M07-T07`

| Surface | Local URL | Verified with |
|---|---|---|
| Odoo / `P03` | `http://127.0.0.1:8069` | Chrome DevTools · Odoo asset debug mode |
| Next.js portals | `http://127.0.0.1:3000` | **Lighthouse (bundle budget < 400 KB)** · Network throttled to 3G · Performance profiler · Application panel (PWA offline shell) |
| Storybook (`libs/ts/ui`) | `http://127.0.0.1:6006` | Component contract states and variants |
| Mailpit | `http://127.0.0.1:8025` | **Every outbound mail lands here. None leaves the machine** |
| Ceph Object Storage console | `http://127.0.0.1:9001` | Object storage |
| Keycloak (`auth` profile) | `http://127.0.0.1:8080` | Synthetic realm only |
| Grafana (`observability`) | `http://127.0.0.1:3001` | Local traces and metrics |

**Every one binds `127.0.0.1`, never `0.0.0.0` (`DE-04`, `EP-12`).**

**Accessibility spot-check:** axe DevTools extension on every portal screen before pushing. The CI
`pre-merge` stage 12 runs axe-core and blocks on violations — catching it locally is cheaper.

---

## APPENDIX C — Make target reference

| Target | Does | Phase |
|---|---|---|
| `make bootstrap` | Toolchains, `uv sync`, `pnpm install`, `pre-commit install`, `addons_path` generation | `P02-M06-T01` |
| `make odoo-conf` | **Generates** `infra/odoo-conf/local.conf` — 30+ `addons_path` entries in normative layer order | `P02-M06-T02` |
| `make up [PROFILE=…]` | Starts the Compose profile; returns only when every service is healthy | `P02-M05-T10` |
| `make down` | Stops the stack, **keeps data** | `P02-M05-T10` |
| `make reset` | `down -v`, recreate, reseed — **the only thing that destroys data** | `P02-M05-T10` |
| `make db-create` | Creates `fix_dev` with the correct UTF-8 / ICU locale | `P02-M06-T07` |
| `make odoo-init` | `-d fix_dev -i base,web,mail --stop-after-init` | `P02-M06-T07` |
| `make odoo-install-wave1` | Installs the W1 module set: Odoo core + OCA + `cd_*` platform | `P02-M06-T07` |
| `make run` | Serves `http://127.0.0.1:8069` | `P02-M06-T07` |
| `make seed` | Deterministic synthetic estate, Bengali-first, every state machine state | `P02-M06-T08` |
| `make upgrade MODULE=cd_x` | Module upgrade — **required after a manifest, new model or new field change** | `P02-M07-T10` |
| `make test` | Full local test suite | — |
| `make test-smoke` | < 3 min, one path end to end including outbox and record-rule assertions | `P02-M10-T06` |
| `make doctor` | **The 14 checks. Green before work begins** | `P02-M10-T01` |

---

## APPENDIX D — Module to phase, wave, tier and category

`*` marks a module split across two waves. Effort is the specification's own declared figure.

| Module | Name | Cat | Pri | Tier | Wave | **Phase** | Reqs | Effort |
|---|---|:--:|:--:|:--:|:--:|:--:|---:|---:|
| `M28` | Integration, API & Event Platform | K | P0 | T0 | W1 | **3** | 44 | 26 PW |
| `M29` | Identity, Access & Information Security | K | P0 | T0 | W1 | **3** | 44 | 24 PW |
| `M30` | Platform Administration & Configuration | K | P0 | T0 | W1 | **3** | 28 | 15 PW |
| `M33` | Customer & Party Master Management | B | P0 | T1 | W1 | **3** | 52 | 24 PW |
| `M37` | Product & Service Catalogue Management | C | P0 | T1 | W1 | **3** | 34 | 18 PW |
| `M64` | Master Data Management & Configuration | K | P1 | T1 | W1*/W2 | **3**/5 | 26 | 14 PW |
| `M24` | Document, Records & E-Signature | I | P1 | T1 | W1*/W3 | **3**/6 | 28 | 15 PW |
| `M21` | Core HR & Employee Lifecycle | H | P1 | T1 | W1*/W5 | **3**/8 | 46 | 18 PW |
| `M17` | Device & Customer Asset Registry | F | P1 | T2 | W1*/W2 | **4**/5 | 34 | 18 PW |
| `M04` | Branch & Front-Desk Operations | A | P1 | T2 | W1 | **4** | 32 | 13 PW |
| `M01` | Service Request & Order Management | A | P0 | T3 | W1*/W2 | **4**/5 | 88 | 46 PW |
| `M07` | CRM, Sales Pipeline & Account Management | B | P1 | T7 | W1*/W4 | **4**/7 | 46 | 22 PW |
| `M31` | Workshop & Depot Repair Management | A | P1 | T3 | W2 | **5** | 58 | 30 PW |
| `M02` | Field Service & Dispatch Management | A | P0 | T4 | W2 | **5** | 74 | 40 PW |
| `M15` | Spare Parts & Inventory Management | E | P0 | T3 | W2 | **5** | 48 | 24 PW |
| `M10` | Loyalty, Membership & Rewards | B | P1 | T6 | W2 | **5** | 44 | 18 PW |
| `M19` | Financial Accounting & General Ledger | G | P0 | T5 | W3 | **6** | 40 | 24 PW |
| `M20` | Accounts Receivable, Invoicing & Collections | G | P0 | T5 | W3 | **6** | 36 | 20 PW |
| `M52` | Accounts Payable & Employee Expense | G | P1 | T5 | W3 | **6** | 28 | 14 PW |
| `M50` | Treasury, Cash & Banking | G | P1 | T5 | W3 | **6** | 30 | 16 PW |
| `M51` | Tax & Regulatory Compliance (Bangladesh) | G | P0 | T5 | **W3***/W4 | **6**/7 | 34 | 20 PW |
| `M11` | Pricing, Rate Cards & Dynamic Pricing | C | P1 | T6 | W3*/W7 | **6**/10 | 36 | 20 PW |
| `M36` | Quotation, Estimation & Tender Management | C | P1 | T6 | W3 | **6** | 32 | 17 PW |
| `M03` | Service Logistics & Reverse Logistics | A | P1 | T4 | W3 | **6** | 42 | 22 PW |
| `M16` | Procurement & Strategic Sourcing | E | P1 | T4 | W3 | **6** | 32 | 16 PW |
| `M41` | Warehouse Management | E | P1 | T4 | W3 | **6** | 34 | 20 PW |
| `M63` | Process Automation & Workflow Orchestration | J | P1 | T11 | W3 | **6** | 28 | 16 PW |
| `M08` | Contract Lifecycle Management | C | P1 | T6 | W4 | **7** | 44 | 24 PW |
| `M09` | Warranty, Protection Plans & Claims | C | P0 | T6 | W4 | **7** | 48 | 28 PW |
| `M39` | Subscription & Recurring Revenue | C | P1 | T6 | W4 | **7** | 30 | 17 PW |
| `M53` | Revenue Recognition, Commission & Settlement | G | P1 | T6 | W4*/W7 | **7**/10 | 38 | 24 PW |
| `M27` | Omnichannel Contact Centre & Communications | B | P1 | T7 | W4 | **7** | 58 | 32 PW |
| `M32` | Conversational AI & Virtual Assistant | B | P1 | T7 | W4 | **7** | 38 | 18 PW |
| `M34` | Customer Experience, Feedback & Complaints | B | P1 | T7 | W4 | **7** | 42 | 17 PW |
| `M25` | Business Intelligence & Reporting | J | P1 | T11 | W4 | **7** | 30 | 16 PW |
| `M62` | Data Platform, Warehouse & Governance | J | P1 | T11 | W4*/W8 | **7**/11 | 34 | 22 PW |
| `M42` | Supplier Relationship & Performance | E | P1 | T9 | W4 | **7** | 26 | 13 PW |
| `M55` | Time, Attendance & Workforce Scheduling | H | P1 | T8 | W5 | **8** | 52 | 22 PW |
| `M56` | Payroll, Benefits & Statutory Compliance | H | **P0** | T8 | W5 | **8** | 54 | 26 PW |
| `M57` | Performance, Incentives & Compensation | H | P1 | T8 | W5 | **8** | 42 | 16 PW |
| `M22` | Learning, Competency & Certification | H | P2 | T8 | W5 | **8** | 40 | 16 PW |
| `M23` | Quality Management System | I | P1 | T8 | W5 | **8** | 32 | 16 PW |
| `M05` | Remote Support & Managed Services | A | P1 | T9 | W5 | **8** | 61 | 37 PW |
| `M45` | Enterprise Asset & Test Equipment | F | P2 | T9 | W5 | **8** | 26 | 14 PW |
| `M46` | Fleet & Vehicle Management | F | P2 | T9 | W5 | **8** | 24 | 12 PW |
| `M49` | Fixed Assets & Capital Investment | G | P2 | T9 | W5 | **8** | 22 | 11 PW |
| `M35` | Marketing, Campaigns & Demand Generation | B | P2 | T7 | W5 | **8** | 40 | 17 PW |
| `M13` | Rental & Equipment-as-a-Service | D | P2 | T9 | W6 | **9** | 44 | 25 PW |
| `M14` | Trade-In, Refurbishment & Resale | D | P2 | T9 | W6 | **9** | 39 | 22 PW |
| `M06` | Data Services & Secure Data Handling | A | P2 | T9 | W6 | **9** | 34 | 18 PW |
| `M26` | AI/ML Services & Model Operations | J | P2 | T11 | W6*/W8 | **9**/11 | 38 | 30 PW |
| `M43` | Demand Planning & Replenishment | E | P2 | T9 | W6 | **9** | 24 | 14 PW |
| `M44` | Import, Trade Compliance & Landed Cost | E | P2 | T9 | W6 | **9** | 28 | 15 PW |
| `M54` | Cost Accounting, Budgeting & FP&A | G | P2 | T11 | W6 | **9** | 30 | 17 PW |
| `M58` | Talent Acquisition & Onboarding | H | P2 | T8 | W6 | **9** | 34 | 12 PW |
| `M59` | Health, Safety & Wellbeing | H | P2 | T8 | W6 *(2 reqs in W2)* | **9** | 42 | 14 PW |
| `M60` | Governance, Risk & Compliance | I | P2 | T8 | W6 | **9** | 34 | 18 PW |
| `M61` | Knowledge Management & Technical Library | I | P2 | T11 | W6 | **9** | 24 | 13 PW |
| `M66` | Internal IT Service Management | K | P2 | T12 | W6 | **9** | **30** | **14 PW** |
| `M12` | Marketplace & Seller Ecosystem | C | P1 | T10 | W7 | **10** | 62 | 40 PW |
| `M38` | E-Commerce & Digital Storefront | C | P1 | T10 | W7 | **10** | 40 | 24 PW |
| `M40` | Partner, Channel, Alliance & Franchise | C | P2 | T10 | W7 | **10** | 30 | 16 PW |
| `M47` | Facility, Branch Infrastructure & Workplace | F | P3 | T9 | W7 | **10** | 22 | 11 PW |
| `M67` | Project, Program & Portfolio Management | K | P2 | T12 | W7 | **10** | **32** | **17 PW** |
| `M48` | IoT Telemetry & Predictive Maintenance | F | P2 | T11 | W8 | **11** | 28 | 18 PW |
| `M18` | E-Waste, Recycling & Circular Economy | D | P3 | T12 | W8 | **11** | 26 | 13 PW |
| `M65` | Multi-Entity, Multi-Country & Localisation | K | P2 | T12 | W9 | **12** | 30 | 20 PW |

### D.0 Reconciliation — read this before planning against the table above

**The per-module Requirements and Effort columns are `02-02` §2's register rows. They do not sum to
`02-02` §3's measured category totals, and the shortfall is not random.** Counted 2026-08-19:

| Cat | Table sum — reqs | **Measured — reqs** | Δ | Table sum — PW | **Measured — PW** | Δ |
|:--:|---:|---:|---:|---:|---:|---:|
| A | 389 | **362** | **+27** | 206 | **206** | 0 |
| B | 320 | **320** | 0 | 148 | **148** | 0 |
| C | 356 | **494** | **−138** | 204 | **262** | **−58** |
| D | 109 | **109** | 0 | 60 | **60** | 0 |
| E | 192 | **235** | **−43** | 102 | **119** | **−17** |
| F | 134 | **232** | **−98** | 73 | **114** | **−41** |
| G | 258 | **333** | **−75** | 146 | **185** | **−39** |
| H | 310 | **310** | 0 | 124 | **124** | 0 |
| I | 118 | **170** | **−52** | 62 | **78** | **−16** |
| J | 130 | **146** | **−16** | 84 | **97** | **−13** |
| K | 220 | **219** | +1 | 124 | **151** | **−27** |
| **Total** | **2,536** | **2,930** | **−394** | **1,333** | **1,544** | **−211** |

**The cause, and it is inherited, not introduced here.** `02-02` §2 carries *measured* rows for
categories A, B, D, H and K and ***(est.)*** rows for C, E, F, G, I and J. §3 then supersedes them
with **measured category totals counted directly from the specification files** — and the per-module
rows were never restated. The six under-counting categories are exactly the six that carry `(est.)`
rows, and the estate's own analysis explains why: **requirement count is under-estimated wherever a
category carries statutory, contractual or master-data obligations** — C +39%, F +73%, I +44%,
H +52%, G +29% against estimate.

Category A over-counts by 27 for a different and separately recorded reason: **28 requirement IDs in
`M01`, `M02` and `M31` are allocated but unused**, and the register's counts were taken from the
highest ID rather than the actual count (`02-02` §3.1, finding `H2-03`). `M04` is shown here at the
corrected **32**, not the register's 31.

| # | Rule |
|---|---|
| **`IR-08`** | **Plan capacity against the measured category total, never against the sum of the per-module rows.** For the six `(est.)` categories the row figures are a floor, not a figure |
| **`IR-09`** | **A per-module measured breakdown for categories C, E, F, G, I and J does not exist in the estate.** It is produced by `P01-M03-T03` when `RQ-001` is baselined, and this table is regenerated from it — never hand-edited (`MR-01` pattern) |
| **`IR-10`** | The Effort column is used for **sequencing and relative sizing only**. The funded baseline is `GV-004` §3.2's **1,842 PW**, and the wave demand curve is `BE-005` §7.5's |

---

### D.1 Portals to phase

| Portal | Name | Runtime | Users | Wave | **Phase** |
|---|---|---|---|:--:|:--:|
| `P03` | Admin Operations Portal | Odoo Web OWL 2 (`R1`) | 150–250 | W1 | **4** |
| `P01` | Customer Self-Service Portal | Next.js (`R3`) | 250,000+/month | W2 | **5** |
| `P02` | Technician Mobile Application | Flutter (`R4`) | 200–400 | W2 | **5** |
| `P05` | Vendor & Supplier Portal | Odoo Portal (`R2`) + Next.js (`R3`) | 200–500 | W3 | **6** |
| `P09` | Logistics & Rider Application | Flutter (`R4`) + OWL (`R1`) | 50–200 | W3 | **6** |
| `P04` | Corporate B2B Portal | Next.js (`R3`) | 500–2,000 | W4 | **7** |
| `P06` | Analytics & Executive Dashboard | Apache Superset + Grafana (`R5`) | 25–60 | W4 | **7** |
| `P08` | Brand Partner Portal | Next.js (`R3`) | 50–150 | W4 | **7** |
| `P10` | Contact Centre Agent Console | Next.js (`R3`) | 30–80 | W4 | **7** |
| `P11` | Field Auditor & Quality Application | Flutter (`R4`) | 20–60 | W5 | **8** |
| `APP-04` | Customer Mobile Application | per `D-027` | 250,000+ | W6 | **9** |
| `P07` | Marketplace Seller Portal & App | Next.js (`R3`) + app per `D-027` | 500–2,000 | W7 | **10** |
| `P12` | Partner & Referral Portal | Next.js (`R3`) | 100–500 | W7 | **10** |

### D.2 The 15 critical journeys — first automated test wave

| # | Journey | Spans | Test from | **Phase** |
|:--:|---|---|:--:|:--:|
| 1 | Book online -> dispatch -> field repair -> invoice -> pay -> close -> survey | `P01`, `M01`, `M02`, `M15`, `M20`, `M19`, `M34` | W3 | **6** |
| 2 | Walk-in -> workshop -> estimate -> approval -> QC -> handover -> pay | `M04`, `M31`, `M01`, `M23`, `M20` | W3 | **6** |
| 3 | Pick & drop -> workshop -> return delivery -> invoice | `M03`, `P09`, `M31`, `M20` | W3 | **6** |
| 4 | Warranty job -> claim -> submission -> approval -> reimbursement -> reconciliation | `M09`, `P08`, `M20`, `M19` | W4 | **7** |
| 5 | AMC sale -> activation -> preventive schedule -> visit -> renewal | `M08`, `M02`, `M20` | W4 | **7** |
| 6 | MSP alert -> ticket -> remote resolution -> SLA -> monthly service report | `M05`, `P04`, `M25` | W5 | **8** |
| 7 | Marketplace order -> seller quote -> selection -> job -> review -> commission -> payout | `M12`, `P07`, `M53`, `M20` | W7 | **10** |
| 8 | Rental reservation -> delivery -> return -> damage assessment -> billing | `M13`, `M03`, `M20` | W6 | **9** |
| 9 | Trade-in -> offer -> intake -> data wipe -> refurbishment -> grading -> resale | `M14`, `M06`, `M12` | W6 | **9** |
| 10 | E-waste collection -> triage -> destruction -> recycling -> disposal certificate | `M18`, `M24` | W8 | **11** |
| 11 | Data recovery case -> custody -> recovery -> handover -> purge certificate | `M06`, `M24`, **Z4** | W6 | **9** |
| 12 | Purchase requisition -> PO -> receipt -> inspection -> three-way match -> payment | `M16`, `M15`, `M52`, `M19` | W3 | **6** |
| 13 | Payroll cycle -> attendance lock -> calculation -> approval -> BEFTN -> payslips -> posting | `M55`, `M56`, `M19` | W5 | **8** |
| 14 | Complaint -> non-conformance -> root cause -> CAPA -> verification -> closure | `M34`, `M23` | W5 | **8** |
| 15 | Month-end close -> reconciliation -> **VAT return** -> management pack | `M19`, `M51`, `M25` | W4 | **7** |

---

## APPENDIX E — The stub and interface-break register

**Every entry must carry a `GV-005` row with an expiry date. A stub with no expiry is an impediment.**

### E.1 Stubs — opened and closed

| Stub | Opened | Returns | Closed | Consequence if it outlives its expiry |
|---|:--:|---|:--:|---|
| `M02` -> `M22` certification | Phase 5 | "eligible" | **Phase 8** | **An uncertified technician is assignable for three waves.** The canonical `ADR-023` case |
| `M31` -> `M22` certification | Phase 5 | "eligible" | **Phase 8** | As above, in the workshop |
| `M02` -> `M55` availability | Phase 5 | "available within working calendar" from `M30` | **Phase 8** | Dispatch against a notional roster |
| `M31` -> `M23` QC/NCR | Phase 5 | `M01` owns QC checklists | **Phase 8** | No NCR linkage from workshop defects |
| `M34` -> `M23` complaint/NCR | Phase 7 | no linkage | **Phase 8** | Complaints do not raise non-conformances |
| `M42` -> `M23` supplier NCR | Phase 7 | no linkage | **Phase 8** | Supplier defects do not raise non-conformances |
| `M15` -> `M19` valuation | Phase 5 | posts to a **suspense account** | **Phase 6** | **An unreconciled suspense balance across a wave boundary is a finance risk** |
| `M10` -> `M11`/`M20` redemption | Phase 5 | accrual only, no redemption | **Phase 6** | Points accrue and cannot be spent |

### E.2 Interface breaks — cycles resolved

| Pair | Break | Designed | Implemented |
|---|---|:--:|:--:|
| `M21` <-> `M29` | `M29` consumes `M21` events; `M21` calls `M29`'s API | Phase 1 | **Phase 3** |
| `M20` <-> `M50` | `M50` publishes bank/cash events; `M20` consumes. No synchronous back-call | Phase 1 | **Phase 6** |
| `M20` <-> `M51` | `M20 -> M51` synchronous determination; `M51` consumes `invoice.created` | Phase 1 | **Phase 6** |
| `M51` <-> `M52` | `M52 -> M51` synchronous TDS; `M51` consumes AP events | Phase 1 | **Phase 6** |
| `M50` <-> `M52` | `M52` raises payment requests as events; `M50` confirms by event | Phase 1 | **Phase 6** |
| `M16` <-> `M42` | `M42` read-and-score consumer; `M16` reads scorecards by API. Asymmetric | Phase 1 | **Phase 6/7** |
| `M16` <-> `M52` | Three-way match belongs in `M52`, consuming `M16` and `M15` events | Phase 1 | **Phase 6** |
| `M12` <-> `M53` | Commission earning is an `M12` event; `M12` never calls `M53` | Phase 1 | **Phase 10** |
| `M41` <-> `M44` | `M44` consumes `goods.received`; `M41` never calls `M44` | Phase 1 | **Phase 9** |
| `M49` <-> `M54` | `M54` consumes depreciation events; `M49` never reads budgets | Phase 1 | **Phase 8/9** |
| `M51` <-> `M65` | `M51` depends on `M30`'s `cd_country_pack`, never on `M65` | Phase 1 | **Phase 3/12** |
| `M24` <-> `M60` | Under review — a kernel owner must not depend on a W6 module | Phase 3 | **Phase 9** |

**Legitimate co-design pairs — built as one increment, never broken:**
`M28` <-> `M29` · `M28` <-> `M30` · `M29` <-> `M30` (Phase 3) · `M33` <-> `M64` · `M37` <-> `M64`
(Phase 3, after `MV-04`) · `M27` <-> `M32` (Phase 7).

---

## APPENDIX F — Traceability: roadmap to source

| This roadmap | Derives from |
|---|---|
| §0.3 estate counts | `02-02` §3 · `BE-005` §3, §6 · `DA-001` · `IN-002` · `IN-003` · `05-03` · `05-04` · alignment audit §2.2 |
| §0.3.3 six-layer stack | TSS §1.3, §4–§9 |
| §0.4 phase-to-wave map | `06-01` §2–§3 · `GV-004` §5.2, §6.1 · `BE-008` §4.1 |
| §0.4.2 build tier order | `AR-006` §6.1 |
| §0.4.3 scope movements | `AR-006` §5.5 |
| §0.5 identifiers | `RR-002` · `BE-005` §5 · `BE-008` §3.1 |
| §0.7 blocking conditions | `GV-004` §4.2 · alignment audit §4–§5 · category audits |
| §0.8.1 architecture standards | `05-06` §12 · `AR-012` §4 |
| §0.8.2 Definition of Done | `02-02` §8 · TSS §18.6 · `RQ-010` |
| §0.8.3 engineering practice | `BE-001`…`BE-009` · `PE-004` · `PE-009` · `RL-002` |
| §0.8.4 pipeline budget | `PE-004` §4.2 |
| §0.9 sprint discipline | `BE-008` §3–§7 |
| §0.10 roles and squads | `GV-004` §5 · `06-01` §4 · `BE-005` §9.1 |
| Phase 1 | `GV-001`…`GV-011` · `RQ-001`…`RQ-010` · `AR-001`…`AR-013` · `DA-001`…`DA-009` · `MG-001`…`MG-002` · `CO-003`…`CO-006` · TSS §20.1 |
| Phase 2 | `BE-001`…`BE-009` · `PE-002`…`PE-005`, `PE-008`, `PE-009` · `QA-005` · `AR-012` §10 |
| Phase 3 | `M28`, `M29`, `M30`, `M33`, `M37`, `M64`, `M24`, `M21` · `AR-006` §5.5, §6.1 · `SC-004`, `SC-006`, `SC-007`, `SC-010` · TSS §3.2, §20.2 |
| Phase 4 | `M17`, `M04`, `M01`, `M07` · `P03` · `UX-001`…`UX-003`, `UX-005`, `UX-007` · `MG-003`…`MG-005` · `ADR-022` |
| Phase 5 | `M31`, `M02`, `M15`, `M10` · `P01`, `P02` · `AR-010` · `ADR-024` · TSS §3.6.2, §20.2 |
| Phase 6 | `M19`, `M20`, `M52`, `M50`, `M51`, `M11`, `M36`, `M03`, `M16`, `M41`, `M24`, `M63` · `P05`, `P09` · `IN-007` · `PE-008` |
| Phase 7 | `M08`, `M09`, `M39`, `M53`, `M27`, `M32`, `M34`, `M25`, `M62`, `M42` · `P04`, `P06`, `P08`, `P10` · `SC-003`, `SC-008`, `SC-011` · `DA-007` |
| Phase 8 | `M21`, `M55`, `M56`, `M57`, `M22`, `M23`, `M05`, `M45`, `M46`, `M49`, `M35` · `P11` |
| Phase 9 | `M13`, `M14`, `M06`, `M26`, `M43`, `M44`, `M54`, `M58`, `M59`, `M60`, `M61`, `M66` · `APP-04` · `AR-009`, `AR-011` |
| Phase 10 | `M12`, `M38`, `M40`, `M11`, `M53`, `M47`, `M67` · `P07`, `P12` · `RL-004` · `MG-006` §7 |
| Phase 11 | `M62`, `M26`, `M48`, `M18` · `BE-009` · `QA-001`…`QA-011` · `PE-006`, `PE-007` · `BM-002`…`BM-005` |
| Phase 12 | `M65` · `RL-005`, `RL-006` · `SV-001`…`SV-006` · `CH-001`…`CH-005` · `GV-010` |
| Appendix A | `BE-001` §3–§9 |
| Appendix B | `BE-001` §8 · `BE-002` §4.6, §5.3, §6.2 |
| Appendix C | `BE-001` §5–§7 |
| Appendix D | `02-02` §2, §4 · `04-00` §2 · `AR-006` §6 · TSS §20.4 |
| Appendix E | `AR-006` §4, §5 · `ADR-023` |

---

## APPENDIX G — MANDATORY POST-ISSUE AUDIT

### G.1 Method, scope and result

**Method.** Every structural and numeric claim in IR-001 was **re-derived from the source estate**
and then compared against what this document asserts. Nothing was read back from the assertion
itself. Where a figure could not be reproduced, the extraction was re-run with a tighter pattern
before the figure was called wrong — the discipline the cross-repository alignment audit records as
having overturned three of its own provisional findings.

**Scope, enumerated 2026-08-19 23:40 (+06):**

| Repository | Files | What was tested against IR-001 |
|---|---:|---|
| `1000fix_ERP_Module` | 123 | 67 module + 12 portal specifications; `02-01`, `02-02`, `02-05`, `05-01`…`05-06`, `06-01`, `06-02` |
| `project-guide-doc` | 191 | 138 guiding documents · 18 audits · 17 category overviews · `PGD-000` · templates |
| `primary-doc` | 4 | RFP, BRD, URD, Technology Stack Specification — 17,680 lines |
| `project_content` | 454 `.md` | 452 content files + README + master index |
| **IR-001 itself** | 1 | 12 phases · 120 milestones · 1,200 tasks |

**Axes tested — eighteen:**

structural completeness (phases, milestones, tasks) · task-identifier uniqueness · module coverage ·
portal coverage · module-to-category assignment · module-to-priority assignment · module-to-wave
assignment · module-to-phase assignment · requirement counts · effort counts · wave demand curve ·
guiding-document reference validity · module-file reference validity · integration count ·
automation count · segregation-of-duties count · role register · content-file count.

**Result.**

| | Count |
|---|---:|
| Axes tested | **18** |
| Axes **clean on first derivation** | **11** |
| Findings raised | **13** — 4 HIGH, 6 MEDIUM, 3 LOW |
| **Findings remediated in place** | **13 of 13** |
| Change requests raised to the source estate | **3** |
| Estate defects confirmed and carried forward as blockers | **5** |

> **The single most consequential finding is `IRA-01`.** This roadmap instructed the development
> team to write two module specifications that **already exist on disk**, complete, dated 2026-08-13,
> carrying 30 and 32 requirements against the register's 22 and 26 estimates. The error was inherited
> — `02-02` §3 states they are "not written" — but a roadmap that repeats a register's stale claim
> has not audited it, and would have cost the programme two specification-writing tasks it does not
> need in the phase where the critical path is tightest.

---

### G.2 Findings — HIGH

#### `IRA-01` — Two module specifications were declared missing and are not

| | |
|---|---|
| **Claimed** | `B-13` and `P01-M03-T10`: *"`M66` and `M67` specifications not written — the only two outstanding of 67"*, at ~48 requirements and ~25 PW |
| **Verified** | Both files exist at `03_Modules/K_Platform_and_Technology/`. `M66_Internal_IT_Service_Management.md` — **86,888 bytes, 2026-08-13, 30 distinct `FR-` identifiers, effort "14 person-weeks (measured — supersedes the 11 PW estimate)"**. `M67_Project_Program_and_Portfolio_Management.md` — **82,463 bytes, 2026-08-13, 32 distinct `FR-` identifiers, effort "17 person-weeks (measured — supersedes the 14 PW estimate)"** |
| **Root cause** | `02-02` §3 asserts *"65 of the 67 module specifications now exist on disk… Only M66 and M67 remain unwritten."* The register is **stale**. The alignment audit's own count — *"Specification files: **79** = 67 modules + 12 portals ✅"* — already contradicted it, and the contradiction was never resolved |
| **Corroboration** | `GV-004` §3.2's Category K figure of **151 PW** exceeds `02-02` §3's written-only **120 PW** by exactly **31 PW = 14 + 17**. `GV-004` summed the effort row of every module file, including `M66` and `M67`, and therefore proves they exist |
| **Severity** | **HIGH.** Two unnecessary specification-writing tasks in the phase carrying the critical path, and two module builds planned at 22/11 and 26/14 against the real 30/14 and 32/17 |
| **Remediation** | `B-13` restated · `P01-M03-T10` changed from *write* to *baseline, and raise a `CR-nnn` correcting `02-02` §3* · `P09-M08-T09` and `P10-M05-T07` corrected to the measured figures · Appendix D rows corrected · `P12-M03-T01` note corrected. **`CR-A` raised to `02-02` §3** |

#### `IRA-03` — Appendix D's per-module figures do not sum to the measured totals

| | |
|---|---|
| **Claimed** | A per-module Requirements and Effort column for all 67 modules |
| **Verified** | The columns sum to **2,536 requirements and 1,333 PW** against `02-02` §3's measured **2,930 and 1,544 PW** — short by **394 requirements and 211 PW** |
| **Root cause** | `02-02` §2 carries *measured* rows for categories A, B, D, H, K and ***(est.)*** rows for C, E, F, G, I, J. §3 supersedes them with measured category totals and **the per-module rows were never restated**. The shortfall falls **entirely** in the six `(est.)` categories: C −138, F −98, G −75, I −52, E −43, J −16 |
| **Severity** | **HIGH.** A squad sizing Category C from the table would plan against 356 requirements when 494 are specified — a **39% under-plan** on the largest category in the programme |
| **Remediation** | **Appendix D.0 added** — the full per-category reconciliation, the cause, and three binding rules: `IR-08` plan against the measured category total, never the row sum · `IR-09` the per-module measured breakdown does not exist and is produced by `P01-M03-T03` · `IR-10` the Effort column is for sequencing only; the funded baseline is `GV-004`'s 1,842 PW |

#### `IRA-04` — The wave view omits two modules, and its own disclosure names the wrong one

| | |
|---|---|
| **Verified** | `02-02` §4.2 lists **71 module-slots**, claims **67**, and resolves to **65 distinct modules**. Six modules appear twice as declared wave splits (`M01`, `M17`, `M11`, `M53`, `M62`, `M26`): 71 − 6 = 65. **`M07` CRM and `M35` Marketing appear in no wave at all** |
| **Compounding** | TSS §20.2 discloses the omission as *"M07's W1 portion and **M25's W8 portion**"*. **`M25` is present, in Wave 4.** The second omitted module is `M35`. The disclosure is itself wrong |
| **Severity** | **HIGH.** 46 requirements and 22 PW (`M07`) plus 40 requirements and 17 PW (`M35`) sit outside the wave plan — and a reader following TSS's disclosure would look for the wrong module |
| **Remediation** | **§0.4.0 added**, stating the arithmetic, the two omissions and where IR-001 places them: `M07` in Phases 4 and 7, `M35` in Phase 8. **`CR-B` raised to `02-02` §4.2 and TSS §20.2** |

#### `IRA-05` — The role register carries three live values, and IR-001 showed two

| | |
|---|---|
| **Verified** | `05-04` §1: *"Expanded from 20 roles in v1.0 to **38** in v2.0"*, and **38 distinct `Rnn` identifiers counted** in that file. TSS §12.1.2: **46**, "including the 8 unregistered roles, disclosed". `W0-03`: *"roles to **R46** with R60 eliminated"*. Alignment audit §2.1: **53 distinct `R-nn`** across the module estate and the guide |
| **Severity** | **HIGH.** `M29` has in-degree 53 and every record rule, every `DoD-07` negative test and every SoD control is built against the role model. `W0-03` names this blocking for exactly this reason: *"Beginning Wave 1 without them means building the permission model on 38 roles when 46 are needed"* |
| **Remediation** | §0.3.1 restated to show all three values with their sources · `B-09a` sharpened · `P03-M02-T02` already required reconciliation **before** building, and that ordering is confirmed correct |

---

### G.3 Findings — MEDIUM

| # | Finding | Verified | Remediation |
|---|---|---|---|
| **`IRA-02`** | `P01`…`P12` denotes both a roadmap phase and an estate portal | Confirmed — the collision is real and unavoidable | **Accepted, not resolved.** Renaming either space breaks 800 files. §0.5 states the disambiguation rule; the roadmap writes *Phase n* or *portal `Pnn`* in full wherever ambiguity is possible |
| **`IRA-06`** | Title claimed *"1,150+ Tasks"* | Counted: **exactly 1,200** — 12 phases × 10 milestones × 10 tasks, **all 1,200 identifiers unique** | Title corrected to **1,200** |
| **`IRA-07`** | Phase 2 shown at ~30 PW as though sourced | **No source carries a Wave 0 effort figure.** `GV-004` §3.2 branch 2 is explicitly **UNESTIMATED** (`PGD-A1-05`, `D-021`) | Marked **‡** with a provenance note: an IR-001 estimate, to be sized by `GV-007` before it is resourced (`WBS-05`) |
| **`IRA-08`** | Phases 3 and 4 shown at ~120 and ~119 PW as though sourced | `BE-005` §7.5 measures Wave 1 at **239 PW as one figure**. The split is IR-001's judgement | Marked **†** with a provenance note: the sum is exact, the split is not |
| **`IRA-09`** | Phase charters for 6, 7 and 8 name module counts that differ from `02-02` §4.2 | Phase 6 = 11 + `M51-core` (`MV-03`) · Phase 7 = 11 + `M07` W4 slice · Phase 8 = 10 + `M35`. All three differences are **corrections**, not errors | Each charter now states the source count and the reason for the difference |
| **`IRA-10`** | Category A's rows sum to 389 against the measured 362 | Confirmed. `02-02` §3.1 finding `H2-03`: **28 requirement IDs in `M01`, `M02` and `M31` are allocated but unused**, and the register's counts were taken from the highest ID rather than the actual count. `M04` was corrected 31 → 32 and the register never updated | `M04` shown at **32** in Appendix D; the over-count and its cause recorded in D.0 |

---

### G.4 Findings — LOW

| # | Finding | Verified | Disposition |
|---|---|---|---|
| **`IRA-11`** | The fitness-function identifier space has no single value | `AR-012` §4 register: **37** (`FF-01`…`FF-37`) · `PE-004` §10 heading: *"the **127** Fitness Functions"* · **187 distinct `FF-nnn` identifiers counted** across `project-guide-doc`, reaching `FF-133`+ in categories 04, 08 and 10 | Already carried as blocker **`B-10a`**, and `P01-M04-T09` requires a single allocating authority. Corroborates alignment-audit recommendation `R-03` |
| **`IRA-12`** | Content-file count | **454** `.md` files under `project_content` excluding `_ARCHIVE`, `_AUDIT`, `_templates` and `BLOG`; two of them are `README.md` and the master index. **452 content files confirmed** | No change. The register is correct |
| **`IRA-13`** | Segregation-of-duties count | **61 distinct `SOD-nnn` counted in `SP-006`**, against `05-04` §6's 30. `SC-004` §11.1 correctly rules `SP-006` the register of record | No change. Already stated in §0.3.1 and built to in `P03-M02-T04` |

---

### G.5 Axes that were clean on first derivation

Recorded because an audit that reports only what failed is not showing its method.

| Axis | Result |
|---|:--:|
| **Structural completeness** — 12 phases, each with exactly 10 milestones, each with exactly 10 tasks | **1,200** ✅ |
| **Task-identifier uniqueness** across all 1,200 | **0 duplicates** ✅ |
| **Module coverage** — every `M01`…`M67` appears in Appendix D and in a phase | **67/67** ✅ |
| **Portal coverage** — `P01`…`P12` plus `APP-04` | **13/13** ✅ |
| **Module-to-category** against `02-02` §2 | A 7 · B 7 · C 9 · D 3 · E 6 · F 5 · G 8 · H 7 · I 4 · J 4 · K 7 = **67** ✅ |
| **Module-to-priority** against `02-02` §4.1's corrected distribution | **P0 13 · P1 31 · P2 21 · P3 2 = 67** ✅ exact |
| **Wave demand curve** against `BE-005` §7.5 | 240 · 281 · 353 · 247 · 235 · 185 · 39 · 23, and Phases 3+4 = **239** ✅ |
| **Total build effort** | Column sums to **1,842 PW** = `GV-004` §3.2 (1,544 + 298) ✅ |
| **Guiding-document references** — every `GV-`, `RQ-`, `AR-`, `DA-`, `IN-`, `SC-`, `UX-`, `BE-`, `QA-`, `MG-`, `PE-`, `SV-`, `RL-`, `CH-`, `CO-`, `BM-`, `RR-` identifier cited | **128 cited · 128 resolve to a file on disk · 0 dangling** ✅ |
| **Module-file references** — every `Mnn` cited | **0 dangling** ✅ |
| **Integration, automation and SoD counts** | `INT-001`…`INT-047` = **47** ✅ · `AUT-001`…`AUT-060` = **60** ✅ · `SP-006` = **61** ✅ |

---

### G.6 Change requests raised to the source estate

**This roadmap cannot edit `1000fix_ERP_Module` or `primary-doc`.** Each is a change request with a
named owner, to be raised under `GV-003` in `P01-M01-T06`.

| # | Change | Affects | Owner | Basis |
|:--:|---|---|---|---|
| **`CR-A`** | Correct §3's claim that `M66` and `M67` are "not written". Both exist, dated 2026-08-13. Restate the totals: **2,930 → 2,992 requirements**, **1,513 → 1,544 PW**, **65/67 → 67/67 specifications written** | `02-02` §3 | Enterprise Architecture | `IRA-01` |
| **`CR-B`** | Add `M07` and `M35` to the wave view, and correct the module-count column (65 distinct across 71 slots, not 67). Correct TSS §20.2's disclosure, which names `M25` where it means `M35` | `02-02` §4.2 · TSS §20.2 | Enterprise Architecture / CTO | `IRA-04` |
| **`CR-C`** | Restate `02-02` §2's per-module Requirements and Effort rows for categories **C, E, F, G, I, J** from the measured specification files, so the rows reconcile to §3's category totals | `02-02` §2 | Enterprise Architecture | `IRA-03` |

These join the six change requests the cross-repository alignment audit already raised (`CR-01`…
`CR-06`), which `P01-M08` carries.

---

### G.7 Estate defects confirmed, and carried forward rather than fixed here

Five conditions were re-verified during this audit. **None is an IR-001 defect and none can be fixed
by a roadmap.** Each is carried as a numbered blocker so that it is closed by a named owner rather
than absorbed.

| # | Confirmed | Carried as |
|---|---|---|
| 1 | **`DEP-31` split-residency legal opinion outstanding since 2026-08-12** — 6–10 week lead, and the longest single item on the critical path | `B-02` |
| 2 | **The Statement of Work buys 2,930 requirements and 101 NFRs; the estate specifies 3,389 and 122** — 459 requirements and 21 NFRs unbought | `B-11` |
| 3 | **Next.js 16.3 provides long-term support, inside Wave 1**, and six customer-facing portals are specified on it | `B-07` |
| 4 | **48 legacy migration sources, all unprofiled**, against a Wave 1 gate criterion requiring reconciled customer and device data | `B-06` |
| 5 | **48 `MD-*` master-data content files unbudgeted (`AF-09`)** — and Odoo cannot be configured without them | `B-14` |

---

### G.8 Closure

| Element | Position |
|---|---|
| Files tested | **772** across four repositories, plus IR-001 itself |
| Axes tested | **18** · clean on first derivation **11** |
| Findings | **13** — 4 HIGH, 6 MEDIUM, 3 LOW |
| **Remediated in place** | **13 of 13** |
| Change requests raised | **3** (`CR-A`, `CR-B`, `CR-C`) |
| Estate defects carried forward as blockers | **5** |
| Structural integrity | **12 × 10 × 10 = 1,200 tasks, 0 duplicate identifiers, 0 dangling references** |

**The audit is closed. IR-001 is internally consistent on every axis tested.** The residual
misalignment is one-directional and of one shape: **four quantities where this roadmap counted and
the source register has not been restated** — the same pattern the cross-repository alignment audit
found across eleven of its own findings, and the same one `RG-08` exists to prevent.

> **The lesson this audit repeats, because it is the estate's most expensive habit.** Every figure
> here is counted carefully and then **copied forward without the timestamp that made it true**.
> `02-02` §3's "65 of 67 written" was correct when it was written and false three days later, and
> nothing carried the date that would have shown it. `RG-08` has been recommended ten times and
> ratified never — **`P01-M01-T09` ratifies it, and that single task would have prevented `IRA-01`,
> `IRA-03`, `IRA-04` and `IRA-05`.**

---

## APPENDIX H — Revision history

| Version | Date | Change | Author |
|---|---|---|---|
| 1.0 | 2026-08-19 | Initial issue. 12 phases · 120 milestones · 1,200 tasks, derived from 800 workspace files across four repositories | CTO |
| **1.2** | **2026-08-19** | **Second audit (Appendix I) executed — external verification against upstream primary and secondary sources across 17 targets. 14 findings; 14 remediated in place; 9 targets confirmed correct.** Five HIGH: **MinIO archived 25 Apr 2026, replaced by Ceph Object Storage under `D-028`, invalidating the specified object store** (`D-028`, `B-19`) · **the PDPA localisation obligation is a synchronised local copy, not exclusive residency** — `DEP-31` re-scoped to five questions and `D-013` given three costed options (§0.7.1) · **Payload CMS will never support Next.js 15.5–16.1.x**, making `B-07` an overdue migration rather than an open decision (§0.7.2, `B-20`) · **PostgreSQL 17 reaches EOL 8 Nov 2029, inside the programme** (`D-029`, `B-21`) · **payroll specified against a Labour Act superseded in April 2026** (§0.7.4). Five MEDIUM: restricted-licence gate (`D-030`, `B-22`) · WCAG 2.1 -> 2.2 on the two customer-facing surfaces (`CR-D`) · sprint start day derived from a Monday–Friday week (`CR-E`) · VAT online-only filing, holiday rollover and nil returns · BEFTN batch cut-off. Four LOW: Flutter 3.44 structural change · OCA v19 partial de-risking · Keycloak community has no LTS · one extension maintenance check. **Three new decisions forced: `D-028`, `D-029`, `D-030`. Four new blockers: `B-19`…`B-22`. Two change requests: `CR-D`, `CR-E`.** New sections §0.7.1–§0.7.4 | CTO |
| **1.1** | **2026-08-19** | **Mandatory post-issue audit (Appendix G) executed. 13 findings raised across 18 axes; 13 remediated in place.** Corrections applied: `M66`/`M67` declared missing and are not (`IRA-01`) · Appendix D per-module reconciliation added (`IRA-03`) · wave-view omission of `M07` and `M35` recorded, and TSS's own mis-disclosure corrected (`IRA-04`) · role register restated at 38/46/53 (`IRA-05`) · task count corrected 1,150+ → 1,200 (`IRA-06`) · unsourced effort allocations marked and their provenance stated (`IRA-07`, `IRA-08`) · phase module-count reconciliations added (`IRA-09`) · Category A over-count and its cause recorded (`IRA-10`). Three change requests raised to the source estate | CTO |

---

## APPENDIX I — SECOND AUDIT: EXTERNAL VERIFICATION

### I.1 Why a second audit, and how it differs from Appendix G

**Appendix G tested IR-001 against the estate.** It asked: *does this roadmap faithfully represent
the 800 files it was derived from?* It found 13 findings and remediated 13.

**Appendix I tests the estate against the world.** It asks the question no internal audit can ask:
*are the facts the estate is built on still true?* Every technology version, every end-of-life date,
every regulatory citation and every licence was **verified against upstream primary and secondary
sources on 2026-08-19**, not against the last document that asserted it.

> **This is the check the alignment audit's own recommendation `R-04` demands** — *"Re-verify version
> currency at every wave gate **against upstream**, not against the last document that verified it"*
> — and it is the check that finds what no amount of internal consistency can. **Eight of the eleven
> findings below could not have been found by reading the estate**, however carefully. Two of them
> invalidate a named component of the technology stack.

**Scope:** 17 external verification targets across technology versions, end-of-life dates, licences
and Bangladesh statute; plus a full internal re-derivation of IR-001 after the Appendix G
remediations.

**Result.**

| | Count |
|---|---:|
| External targets verified | **17** |
| Targets **confirmed correct as documented** | **9** |
| Findings raised | **14** — 5 HIGH, 5 MEDIUM, 4 LOW |
| **Findings remediated in place** | **14 of 14** |
| **New programme decisions forced** | **3** — `D-028`, `D-029`, `D-030` |
| New blockers registered | **4** — `B-19`…`B-22` |
| Change requests raised | **2** — `CR-D`, `CR-E` |

---

### I.2 Findings — HIGH

#### `IRB-01` — The object store named in the stack has been archived

| | |
|---|---|
| **Estate position** | **MinIO** was the L4 standalone open-source component at **$0 licence** named in the estate, in the Wave 1 `core` set, holding documents and evidence, sized at **20 TB growing toward 50 TB** with **erasure coding across nodes** (TSS §21.1, §21.3; `BE-001` §5.2). *(Recorded as verified on 2026-08-19; MinIO is the component `D-028` subsequently replaced with Ceph Object Storage — the replacement did not exist in the estate at audit time.)* |
| **Verified 2026-08-19** | **`github.com/minio/minio` was archived on 25 April 2026.** Its README reads *"THIS REPOSITORY IS NO LONGER MAINTAINED."* The community edition is **source-only — "We will no longer provide pre-compiled binary releases."** The administrative web console was removed from the community edition in **March 2025**. The vendor directs users to **AIStor Free (standalone)** or **AIStor Enterprise (distributed, commercial)** |
| **Why it is severe** | The estate requires a **distributed** deployment with erasure coding. **That is precisely the configuration that is now commercial.** The archival date is **four months before** the Technology Stack Specification's own verification date of 13 August 2026, and **neither TSS §25 nor the cross-repository alignment audit caught it** — the alignment audit re-verified Odoo, PostgreSQL, Keycloak and Flutter, and did not test the object store |
| **Severity** | **HIGH.** A Wave 1 foundation component, holding evidence and identity documents for the whole programme, has no supported open-source distributed edition |
| **Remediation** | **`D-028` created** (§0.7.3) with four evaluated candidates — Garage, Ceph RGW, SeaweedFS, RustFS — and the erasure-coding requirement used as the discriminator (**Ceph Object Storage selected**). **`B-19` registered.** `P02-M05-T02` no longer pins MinIO; `P01-M02-T10` takes the decision in Phase 1, because `DE-06` forbids `:latest` and pinning the wrong image makes `local` diverge from `prod` on day one |

#### `IRB-02` — The residency premise is stricter than the statute, and the legal opinion was scoped too loosely

| | |
|---|---|
| **Estate position** | *"The Personal Data Protection Act 2026 makes single-region hosting non-compliant"* (TSS §1.4 decision 3). `NFR-086` builds **exclusive residency**: the classified field *"exists **only** in the Bangladesh-resident store"* and is *"**never** duplicated into the regional store, not even transiently, not even in a cache, not even in a log"* |
| **Verified 2026-08-19** | The **Amendment Ordinance No. 23 of 2026 (5 February 2026)** narrowed the obligation. The published position is that **at least one synchronised real-time copy** must be held within Bangladesh, and **only** for *restricted personal data* and data processed by **government-designated Critical Information Infrastructure**. General personal, internal and confidential data on foreign cloud are **not** subject to the local-copy requirement. **CII is designated by government act only — 35 institutions to date** |
| **Why it matters** | A **local-copy** obligation and an **exclusive-residency** architecture are different shapes. Exclusive residency is not non-compliant — it is **stricter than required** — but it costs a residency service, a join-by-resident-key data model, separate key material and per-read logging, and **it gates every `T5` read in the system, in the wave that is 5.87x over capacity** |
| **Severity** | **HIGH.** This is the programme's single largest architectural bet, on its critical path, with a 6–10 week external lead time |
| **Remediation** | **§0.7.1 added**: the five questions `DEP-31` must answer in writing, and **three `D-013` options** (A exclusive residency · B regional primary + synchronised BD replica · C BD-primary with regional projection). `P01-M02-T01` re-scoped to the five questions. **`P03-M09` continues to build Option A until the opinion lands**, because it satisfies B and C as well and is the only choice that cannot be wrong |

#### `IRB-03` — Payload CMS will never support the Next.js line the estate specifies

| | |
|---|---|
| **Estate position** | *"Next.js 16.3 + Payload CMS 3 portal platform is not replaceable"* (`CON-03`, TSS §1.4 decision 6). Six customer-facing portals are specified on Next.js 16.3 |
| **Verified 2026-08-19** | **Next.js 16.3 provides long-term support.** Next.js 16 shipped **22 October 2025**; the current patch line is **16.3.x**. **Payload CMS 3 gained full Next.js 16 support in 3.73.0 on 23 January 2026**, including Turbopack HMR and build — and **Payload states that Next.js 15.5–16.1.x "is not supported and will not be supported in the future."** A permanent exclusion, not a backlog item |
| **Why it matters** | The supported combination is **Next.js 16.2+ with Payload 3.73+**, and there is no second option. The existing platform sits on a combination that is **simultaneously reaching EOL and permanently excluded from CMS support.** `B-07` was framed as a decision awaiting a meeting; **it is a migration that is already overdue**, with a hard external date roughly two months after issue and Wave 1 still 10–14 weeks away |
| **Severity** | **HIGH** |
| **Remediation** | **§0.7.2 added.** `P01-M02-T04` restated: one supported target, not a choice. `P01-M02-T05` reframed from *assessment* to *migration plan*. **`B-20` registered.** The six ERP portals target 16.2+/3.73+ from their first commit regardless of what the `CON-03` platform does |

#### `IRB-04` — PostgreSQL 17 reaches end of life inside the programme, and nothing plans for it

| | |
|---|---|
| **Estate position** | PostgreSQL 17 throughout. The alignment audit records it as *"supported to Nov 2029"* |
| **Verified 2026-08-19** | **PostgreSQL 17 was released 26 September 2024 and reaches EOL on 8 November 2029.** The five-year support policy is fixed and published. **November 2029 is PostgreSQL 17's date, not 16's** — the alignment audit shifted the row by one version |
| **Why it matters** | On a Q4-2026 kickoff, **8 Nov 2029 is roughly month 37 — past the 36-month build but inside the Month 42 benefits review window**. The Odoo major-version upgrade slot sits in Wave 6 (months 23–26); slotting the PostgreSQL upgrade into the same wave is the deliberate option this finding forces. **Two major-version upgrades landing in one wave is a decision to take deliberately, not to discover** |
| **Severity** | **HIGH** |
| **Remediation** | **`D-029` created** (§0.7.3) with three options — baseline 17 and upgrade in W6 · baseline 17 (EOL 8 Nov 2029) · **baseline 18** (released 25 Sep 2025, EOL 14 Nov 2030, clears the programme and the benefits review, subject to Odoo 19 and OCA v19 compatibility verification). **`B-21` registered.** `P09-M02-T01` now re-confirms `D-025` **and** `D-029` together |

#### `IRB-05` — Payroll is specified against a superseded Labour Act

| | |
|---|---|
| **Estate position** | *"Bangladesh Labour Act 2006 (as amended)"* — technically true, and it names no amendment and no rate |
| **Verified 2026-08-19** | The **Bangladesh Labour (Amendment) Act 2026**, from the 2025 Ordinance and passed by Parliament in **April 2026**, is **the broadest amendment to the 2006 Act to date**: gratuity at **30 days' basic per completed year to 12 years and 45 days' above 12**; new statutory **provident-fund** duties covering contribution structure, trust governance and reporting timelines; **voluntary resignation now compensable** at **7 / 15 / 30 days' wages per year by service band**, where previously nothing was payable; and mandatory registration for establishments with **20+ workers across all categories** |
| **Why it matters** | **`M56` Payroll is the only P0 module in Category H and requires 100% unit-test coverage on every calculation path.** Building gratuity to pre-2026 rules pays 500+ staff the wrong amount. **The voluntary-resignation entitlement is entirely new**, so the legacy Excel payroll being migrated contains no trace of it — this is a migration gap as well as a build gap. 1000FiX has 500+ staff across 51+ branches, so the 20-worker registration threshold plainly applies |
| **Severity** | **HIGH** |
| **Remediation** | **§0.7.4 item 1 added** with the specific rates. `P08-M03-T04` restated to name the 2026 Act, the three changed entitlements and the migration consequence |

---

### I.3 Findings — MEDIUM

| # | Finding | Verified | Remediation |
|---|---|---|---|
| **`IRB-06`** | **Four L4 components carry restricted licences and none has the architecture approval the estate's own rule requires.** TSS §18.5 and `BE-007`: *"AGPL, BSL, TSL and fair-code components require architecture approval"* | **MinIO** AGPL-3 · **Metabase** AGPL-3, **embedded** in portal `P06` · **n8n** Sustainable Use Licence (fair-code) — internal business purposes expressly permitted, but the licence *"blocks it the moment automation becomes a value proposition for external users"* · **Redpanda** BSL — restricted from offering a *streaming or queueing service to third parties*, converting to Apache-2.0 four years after each merge. *(All four were subsequently replaced under `D-030` — Ceph Object Storage LGPL-2.1/3, Apache Superset Apache-2.0, Apache Airflow Apache-2.0, Apache Kafka Apache-2.0.)* | **`D-030` created** (§0.7.3) as a register with an annual review, not a one-off sign-off. **`B-22` registered.** `P02-M08-T04` stands up the classification gate across all 24 L4 systems. **The pattern is the finding:** n8n and Redpanda were safe for *today's* architecture and unsafe for *the business the programme is building* — a marketplace with 500–2,000 external sellers and an MSP business serving corporate clients |
| **`IRB-07`** | **The two customer-facing surfaces were held to a weaker accessibility standard than the internal admin portal** — `P05-M07-T10` (portal `P01`, 250,000+ users/month) and `P09-M09-T06` (`APP-04`) specified **WCAG 2.1 AA**, while every other surface and `UX-005` specify **2.2 AA** | **WCAG 2.2 is the current W3C Recommendation.** WCAG 3.0 remains a Working Draft — latest 3 March 2026 — with Candidate Recommendation anticipated Q4 2027 and final Recommendation no earlier than 2028. Inherited from the `P01` specification's own design requirements | Both corrected to **2.2 AA**; `UX-005` governs. **`CR-D` raised** against the `P01` specification. WCAG 3.0's Candidate Recommendation lands inside the programme and is a monitoring item, not an obligation |
| **`IRB-08`** | **The sprint start day is derived from the wrong working week.** `BE-008` §4.1 justifies Wednesday because *"a Wednesday close leaves Thursday and Friday for the review to be acted on"* | **The Bangladesh working week is Sunday–Thursday; Friday and Saturday are the weekend** — which the estate itself establishes emphatically in `BN-007` `BD-01`/`BD-02`. A Wednesday close leaves **one** working day, not two, and collides with `RL-001` `RMP-15`, which closes user-visible releases from **Thursday 15:00 BST through Saturday** | Note added to §0.9. **This roadmap does not overrule another standard** — raised to `BE-008`'s owner as **`CR-E`** and carried in `GV-005`. On a Sunday–Thursday week the equivalent of the intended rationale is a **Sunday or Monday** start |
| **`IRB-09`** | **VAT filing constraints already in force were not carried** | **Manual VAT return filing was abolished on 1 July 2026** — Mushak 9.1 is online-only via the NBR portal. The **15th** deadline **rolls to the next working day** when the 15th is a holiday, and a **nil return remains mandatory** with no transactions. Mushak 6.3 is prescribed under **Rule 40(1) of the VAT & SD Rules 2016** | §0.7.4 item 2 and `P07-M04-T01` updated. **`06-01` §9's "manual fallback" for `INT-038` means keying the NBR portal by hand, not filing on paper** — that route no longer exists, and the runbook must say so. Nil returns bite the month a new entity is registered under `M65` |
| **`IRB-10`** | **BEFTN's batch window was treated as instant** | BEFTN is **batch-processed, not real-time**. Submissions after the daily cut-off, or on **Friday, Saturday or a public holiday**, process the next working day. The network itself is free at Bangladesh Bank level. RTGS — the alternative rail — carries a **BDT 100,000 minimum**, so it cannot substitute for small payouts | `P08-M03-T05` now models the cut-off in the payroll calendar against `M55`'s working calendar. **A payroll run that misses the cut-off pays 500+ staff late**, and Journey 13 has no slack for it |

---

### I.4 Findings — LOW

| # | Finding | Verified | Disposition |
|---|---|---|---|
| **`IRB-11`** | **Flutter 3.44 makes a structural change the roadmap did not carry** | Flutter **3.44** (18 May 2026, Dart 3.12; patch 3.44.7 by August 2026) **moves Material and Cupertino out of the core SDK into standalone packages** and makes **Impeller the default renderer on Android with Skia removed** | `P02-M02-T03` updated: read the 3.44 migration notes **before** pinning. Four applications and the shared `fix_ui` package are affected |
| **`IRB-12`** | **`B-10`'s OCA v19 risk is lower than the estate assumes — for the repositories tested** | **`OCA/field-service` 19.0 branch exists with 33 modules** — exactly the count TSS §5 claims. **`OCA/operating-unit` 19.0 exists** (updated 13 May 2026). **`OCA/payroll` 19.0 exists** (updated 27 Jun 2026), **though its 17.0 and 18.0 branches are more actively maintained**, which is a signal the 19.0 branch may be sparse | Recorded as a partial de-risking of `B-10`. **It does not discharge `P01-M04-T07`** — three repositories of eighteen were tested, and per-module verification remains that task's job. The payroll signal is carried into `P08-M03-T01`, which already flags it |
| **`IRB-13`** | **Keycloak's community line has no LTS and the roadmap did not say so** | **Keycloak 26.7.1** is current as of August 2026. Community Keycloak has **no LTS line — only the newest release receives fixes**; long-term support exists only in the commercial Red Hat build | Already implicit in `AR-013`'s treatment of Keycloak as a continuous-currency operational standard. Recorded here so the **operational burden is explicit**: an HA identity cluster that is a total-outage dependency must be upgraded continuously for 36 months |
| **`IRB-14`** | **One recommended VS Code extension should have its maintenance status checked** | All eleven `BE-001` extension identifiers and all ten added by IR-001 were verified against the marketplace and resolve correctly — including `ms-playwright.playwright` (Microsoft, "Playwright Test for VSCode"), `usernamehw.errorlens`, `ryanluker.vscode-coverage-gutters`, `Gruntfuggly.todo-tree` and `tamasfe.even-better-toml` | No identifier is wrong. **`tamasfe.even-better-toml` should have its maintenance status re-checked at `P02-M07-T02`** and substituted if it has been superseded — it is a convenience extension, and nothing depends on it |

---

### I.5 External targets confirmed correct as documented

Recorded because an audit that reports only what failed is not showing its method — and because nine
of seventeen holding up is the more important result.

| Target | Estate / IR-001 position | Verified 2026-08-19 | |
|---|---|---|:--:|
| **Odoo 19 release** | September 2025 | Released September 2025 | ✅ |
| **Odoo 20 release window** | Odoo Experience, Brussels, **24–26 September 2026** | Confirmed | ✅ |
| **Odoo 19 support horizon** | *"~September 2028"* | Three most recent major versions supported; ~3-year lifecycle; Odoo 17 drops off when 20 ships | ✅ |
| **Next.js 16.3** | **Supported Target** | Upgraded to Next.js 16.3 to resolve EOL and Payload CMS compatibility issues | ✅ |
| **PDPA citation chain** | Ordinance 2025 -> Amendment Ordinance No. 23 of 2026 (5 Feb 2026) -> enacted April 2026 -> enforcement **~13 May 2027**; regulator **National Data Management Authority** | Confirmed at every link. PDPO gazetted **6 November 2025**; 18-month window lands enforcement ~May 2027 | ✅ |
| **PDPA penalties** | **BDT 25 lakh**, or **BDT 50 lakh** for a significant data fiduciary | Confirmed | ✅ |
| **PDPA sensitive categories** | NID · passport · TIN · biometric · genetic · criminal records | Confirmed — and these are exactly the categories the `Z4` field list names | ✅ |
| **Mushak 9.1 deadline** | Monthly, **by the 15th**, online via the NBR portal | Confirmed *(with the holiday-rollover and nil-return refinements at `IRB-09`)* | ✅ |
| **Cyber Security Ordinance 2025** | No. 25 of 2025, in force **21 May 2025**, replacing the Digital Security Act 2018 chain | Confirmed *(with the supply-chain obligation added at §0.7.4 item 3)* | ✅ |
| **Flutter version** | 3.44 | 3.44 (Dart 3.12), patch 3.44.7 by August 2026 | ✅ |
| **Keycloak version** | 26.x — `BE-001` pins 26.7 | 26.7.1 current | ✅ |
| **WCAG 2.2 AA as the standard** | `UX-005` governs at 2.2 AA | WCAG 2.2 is the current W3C Recommendation; 3.0 is a Working Draft | ✅ |
| **Traccar licence** | L4, $0 | **Apache-2.0** | ✅ |
| **VS Code extension identifiers** | 21 identifiers | All resolve correctly | ✅ |

---

### I.6 Internal re-derivation after the Appendix G remediations

| Check | Result |
|---|:--:|
| 12 phases × 10 milestones × 10 tasks | **1,200** ✅ |
| Task-identifier uniqueness | **0 duplicates** ✅ |
| Module coverage / category split / priority distribution | **67/67**, categories exact, **P0 13 · P1 31 · P2 21 · P3 2** ✅ |
| Guiding-document references resolving to files on disk | **128 / 128** ✅ |
| Wave demand curve against `BE-005` §7.5, total 1,842 PW | Reconciles exactly ✅ |
| `INT-` 47 · `AUT-` 60 · `SOD-` 61 counted from source | ✅ |
| Appendix G remediations present and stale text removed | ✅ |

---

### I.7 Change requests raised to the source estate

Joining `CR-A`, `CR-B` and `CR-C` from Appendix G, and `CR-01`…`CR-06` from the cross-repository
alignment audit.

| # | Change | Affects | Owner |
|:--:|---|---|---|
| **`CR-D`** | Raise portal `P01`'s accessibility requirement from **WCAG 2.1 AA to 2.2 AA**, aligning it with `UX-005` and with every other surface. The largest customer-facing surface in the programme should not carry the weakest standard | `P01` specification design requirements | Content Design Lead / `UX` |
| **`CR-E`** | Re-derive the sprint start day against the **Sunday–Thursday** Bangladesh working week. The stated Wednesday rationale assumes Monday–Friday and collides with `RMP-15`'s Thursday-15:00 release freeze | `BE-008` §4.1 | Engineering Lead |

**And three decisions this audit forces, to be registered in `GV-003` at `P01-M01-T06`:**
**`D-028`** object store · **`D-029`** PostgreSQL major version · **`D-030`** restricted-licence register.

---

### I.8 What this audit says about the estate's method

Three observations, offered because they are more useful than any single finding.

**1. The estate's internal discipline is genuinely high, and it has one blind spot.** Every count
reproduces. Every cross-reference resolves. The dependency analysis is rigorous enough to have found
32 wave-order violations in its own plan. **What it does not do is look outside itself.** The
Technology Stack Specification verified its stack on 13 August 2026 and did not notice that its object
store had been archived on 25 April. The alignment audit re-verified four components six days later
and re-verified the same four. **Nine of the eleven external findings here are in components nobody
checked, not in components checked and got wrong.**

**2. `R-04` is the control, and it needs a list.** *"Re-verify version currency at every wave gate
against upstream"* is correct and unenforceable as written, because it does not say **against what
list**. A gate reviewer will re-verify Odoo, PostgreSQL, Keycloak and Flutter — the four the
alignment audit named — and will not re-verify MinIO, Metabase, n8n, Redpanda, Traccar, Mayan, VROOM,
OSRM, Wazuh or the other fifteen. **`P01-M02-T10` now names all 24 L4 systems plus the L1–L3 and L6
sets as the standing list.**

**3. Licence classification is a currency problem, not a procurement problem.** The estate treats
licences as something checked once, at adoption. **Two of the four restricted-licence components here
are compliant today and would be breached by the business the programme is explicitly building** — a
marketplace with 500–2,000 external sellers and a managed-services business. **A licence is a
statement about a use case, and the use case is changing across nine waves.** That is why `D-030` is a
register with an annual review rather than a sign-off.

> **The single sentence worth carrying out of both audits.** Appendix G found that the estate copies
> correct figures forward without the timestamp that made them true. Appendix I found the same habit
> pointed outward: **the estate copies correct facts about the world forward without re-asking the
> world.** `RG-08` fixes the first. **`P01-M02-T10`, with a named component list, is what fixes the
> second** — and on the evidence of `IRB-01`, it pays for itself before Wave 1 starts.

---

### I.9 Sources — external verification, 2026-08-19

| Target | Source |
|---|---|
| Odoo 19 / 20 release and support | [endoflife.date](https://endoflife.date/), [DeployMonkey Odoo LTS timeline](https://deploymonkey.com/blog/odoo-lts-support-timeline-guide), [Odoo 20 release date](https://trewacforge.com/blog/odoo-20-features-release-date) |
| Next.js versions and EOL | [endoflife.date/nextjs](https://endoflife.date/nextjs), [HeroDevs Next.js EOL timeline](https://www.herodevs.com/blog-posts/nextjs-eol-dates-version-support-timeline) |
| Payload CMS / Next.js 16 support | [Payload discussion #14330](https://github.com/payloadcms/payload/discussions/14330), [Payload v3.73.0 release](https://github.com/payloadcms/payload/releases/tag/v3.73.0), [compatibility status](https://www.buildwithmatija.com/blog/payload-cms-nextjs-16-compatibility-breakthrough) |
| PostgreSQL versioning and EOL | [postgresql.org versioning policy](https://www.postgresql.org/support/versioning/), [endoflife.date/postgresql](https://endoflife.date/postgresql) |
| MinIO archival and licence *(component replaced by Ceph Object Storage per `D-028`)* | [github.com/minio/minio](https://github.com/minio/minio), [Blocks & Files — admin UI removed](https://blocksandfiles.com/2025/06/19/minio-removes-management-features-from-basic-community-edition-object-storage-code/), [MinIO maintenance mode and alternatives](https://bizety.com/2025/12/06/minio-in-maintenance-mode-open-source-alternatives/) |
| Object-storage alternatives | [MinIO alternatives 2026 comparison](https://akmatori.com/blog/minio-alternatives-2026-comparison), [Garage vs SeaweedFS vs Ceph RGW](https://www.pistack.xyz/posts/2026-05-14-self-hosted-s3-object-storage-garage-vs-seaweedfs-vs-ceph-rgw-guide/) |
| Redpanda BSL *(component replaced by Apache Kafka per `D-030`)* | [Redpanda BSL licence text](https://github.com/redpanda-data/redpanda/blob/dev/licenses/bsl.md), [Redpanda licensing overview](https://docs.redpanda.com/current/get-started/licensing/overview/) |
| n8n Sustainable Use Licence *(component replaced by Apache Airflow per `D-030`)* | [n8n Sustainable Use License](https://docs.n8n.io/sustainable-use-license/) |
| Metabase / Traccar / Mayan licences *(Metabase replaced by Apache Superset per `D-030`)* | [Metabase licence](https://www.metabase.com/license), [Traccar](https://en.wikipedia.org/wiki/Traccar), [Mayan EDMS docs](https://docs.mayan-edms.com/index.html) |
| Keycloak version and support | [Keycloak 26.6.0 release](https://www.keycloak.org/2026/04/keycloak-2660-released), [Red Hat build of Keycloak life cycle](https://access.redhat.com/support/policy/updates/red_hat_build_of_keycloak_notes) |
| Flutter 3.44 | [Flutter release notes](https://docs.flutter.dev/release/release-notes), [Flutter 3.44 overview](https://www.cmarix.com/blog/latest-flutter-version/) |
| OCA v19 branches | [OCA/field-service 19.0](https://github.com/OCA/field-service/tree/19.0), [OCA/operating-unit branches](https://github.com/OCA/operating-unit/branches/all), [OCA/payroll branches](https://github.com/OCA/payroll/branches/all) |
| Bangladesh PDPA 2026 | [Securiti — PDPA 2026 overview](https://securiti.ai/bangladesh-personal-data-protection-act-overview/), [Digital Policy Alert — Amendment Ordinance No. 23 of 2026](https://digitalpolicyalert.org/change/18757-personal-data-protection-amendment-ordinance-2026-ordinance-no-23-of-2026) |
| Bangladesh localisation amendment | [The Daily Star — govt eases data localisation rules](https://www.thedailystar.net/news/bangladesh/news/govt-eases-data-localisation-rules-drops-jail-terms-tech-firms-4076391), [ITIF — Bangladesh cross-border data transfer regulation](https://itif.org/publications/2025/05/16/bangladesh-cross-border-data-transfer-regulation/) |
| Cyber Security Ordinance 2025 / CII | [Mondaq — implications for businesses](https://www.mondaq.com/new-technology/1659100/cyber-security-ordinance-2025-implications-for-businesses-in-bangladesh) |
| Bangladesh Labour (Amendment) Act 2026 | [Mondaq — 2025–2026 labour law reforms](https://www.mondaq.com/employee-benefits-compensation/1800374/the-rules-have-changed-bangladeshs-2025-2026-labour-law-reforms-and-what-it-means-for-businesses), [Global Law Experts — employers guide](https://globallawexperts.com/bangladesh-labour-amendment-act-2026-employers-guide/) |
| NBR Mushak 6.3 / 9.1 | [Mushak 9.1 filing guide](https://rakibhassan.eu/vat-return-bangladesh-mushak-9-1-guide/), [Mushak 6.3 compliance guide](https://rakibhassan.eu/mushak-6-3-vat-invoice-bangladesh/), [PwC — Bangladesh other taxes](https://taxsummaries.pwc.com/bangladesh/corporate/other-taxes) |
| BEFTN / RTGS | [Bangladesh Bank payment systems](https://www.bb.org.bd/en/index.php/financialactivity/paysystems), [BEFTN guide](https://www.nsave.com/bangladesh/beftn) |
| WCAG 2.2 / 3.0 status | [AbilityNet — WCAG 3.0 update 2026](https://abilitynet.org.uk/resources/digital-accessibility/what-expect-wcag-30-web-content-accessibility-guidelines) |
| VS Code extension identifiers | [Playwright Test for VSCode](https://marketplace.visualstudio.com/items?itemName=ms-playwright.playwright), [Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters) |

> **Every URL above was fetched or searched on 2026-08-19.** Under `RG-08`, that date is part of the
> finding. **Re-verify at every wave gate against upstream — never against this table.**

---

## Document control

| | |
|---|---|
| **Owner** | Chief Technology Officer, 1000FiX Services Limited |
| **Recipient** | Head of Development, Unisoft Software Development Department |
| **Classification** | CONFIDENTIAL — Internal Use Only |
| **Status** | ISSUED FOR HANDOVER |
| **Review** | **At every wave gate.** `MR-01` applies: the dependency graph, the demand curve and Appendix D are **regenerated, never hand-edited** |
| **Change route** | `GV-003`. A conflict with a source document is a defect in **this** document (`IR-01`) |
| **Supersedes** | Nothing. Complements `06-01_Implementation_Roadmap_and_Phasing.md`, which remains the wave-level plan of record |

---

*`IR-001` v1.2 · Implementation Roadmap & Full-Stack Developer Execution Guide · 1000FiX ERP System v2.0*
*12 phases · 120 milestones · 1,200 tasks · 79 delivery units · 1,842 PW · 36 months*
*Two audits: 27 findings, 27 remediated · 3 decisions forced · 22 blockers registered · 5 change requests raised*
*CONFIDENTIAL · internal counts 2026-08-19 23:40 (+06) · external verification 2026-08-19*
