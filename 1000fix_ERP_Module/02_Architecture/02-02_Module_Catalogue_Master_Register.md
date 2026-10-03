---
id: FIX-ERP2-022
title: Module Catalogue — Master Register
project: 1000FiX ERP System v2.0
version: 2.1
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
supersedes: v2.0 (30-module / 5-pillar register)
audit_ref: 00-06 findings C-01, C-02, C-03, H-02, H-03, H-04
---

# Module Catalogue — Master Register
# 67 Modules · 11 Categories

> **This is the authoritative register.** Where any other document disagrees with this one on
> module identity, code, category, ownership, priority or wave, **this document wins**.
>
> **Revision 2.1 note.** This register previously described a 30-module, 5-pillar
> architecture. Audit finding **C-01** identified that the repository described two
> architectures simultaneously. This revision restates the register on the 67-module,
> 11-category architecture defined in `README.md` and `FOLDER_STRUCTURE.md`, and registers
> module **M31**, which audit finding **C-02** found had no institutional existence.

---

## 1. Register Governance

| Rule | Detail |
|---|---|
| **RG-01 Register-first** | No module specification file may be created until its entry exists here, its requirement ID range is allocated in `05-01`, and its owned entities are allocated in `05-02`. *(Adopted following audit finding C-02.)* **Extended:** register-first applies to **every programme-wide identifier space** — `KPI-`, `CD-`, `SOD-`, `R`, `RSK-`, `DEP-`, `D-`, `NFR-`. No module file may introduce an identifier in a shared space that does not already exist in its owning register. *(Extended following audit findings H2-04 … H2-07.)* |
| **RG-02 Permanent identity** | `Mnn` and the module code are permanent. A module may be renamed or re-scoped; its ID and code may not change. A retired or allocated code is never reused — where a natural code is taken, a distinct variant is assigned instead (M42 `SRM2`). *(Adopted following audit finding C-03.)* |
| **RG-03 Single owner** | Every module has exactly one business owner and one system owner. |
| **RG-04 Boundary symmetry** | If module A declares a capability out of scope and owned by module B, module B must claim it. |
| **RG-05 Provisional figures** | Requirement counts and effort estimates marked *(est.)* are extrapolations pending the module's specification file. They must not be used for contractual commitment. |
| **RG-06 Count, do not consult** | Any figure describing what the repository **contains** — specification counts, requirement totals, effort totals, completeness percentages — must be derived by **direct enumeration of the files at the time of writing**. A prior statement of the same figure, *including one in this register*, is not evidence. Every such figure carries the date it was counted. *(Adopted following audit finding H2-01, in which this register understated repository completeness by 44 module specifications and the error was then restated with greater precision.)* |

---

## 2. Register — All 67 Modules

### Category A — Service Delivery & Operations (7)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M01 | Service Request & Order Management | `SRM` | Re-scoped | P0 | W1–W2 | Service Ops Director | 88 | 46 PW | ✓ |
| M31 | Workshop & Depot Repair Management | `WSR` | ★ New | P1 | W2 | Service Ops Director | 58 | 30 PW | ✓ |
| M02 | Field Service & Dispatch Management | `FSM` | Re-scoped | P0 | W2 | Service Ops Director | 74 | 40 PW | ✓ |
| M03 | Service Logistics & Reverse Logistics | `LOG` | Retained | P1 | W3 | Logistics Manager | 42 | 22 PW | ✓ |
| M04 | Branch & Front-Desk Operations | `FRD` | Retained | P1 | W1 | Branch Operations Lead | 31 | 13 PW | ✓ |
| M05 | Remote Support & Managed Services | `RMS` | Retained | P1 | W5 | Corporate Services Head | 61 | 37 PW | ✓ |
| M06 | Data Services & Secure Data Handling | `DTS` | Retained | P2 | W6 | Technical Services Head | 34 | 18 PW | ✓ |
| | | | | | | **Category A total** | **388** | **206 PW** | **7/7** |

### Category B — Customer Engagement & Experience (7)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M33 | Customer & Party Master Management | `CPM` | ★ New | P0 | W1 | Chief Commercial Officer | 52 | 24 PW | ✓ |
| M07 | CRM, Sales Pipeline & Account Management | `CRM` | Re-scoped | P1 | W1 / W4 | Chief Commercial Officer | 46 | 22 PW | ✓ |
| M10 | Loyalty, Membership & Rewards | `LOY` | Re-scoped | P1 | W2 | Marketing Head | 44 | 18 PW | ✓ |
| M34 | Customer Experience, Feedback & Complaints | `CXM` | ★ New | P1 | W4 | Customer Service Manager | 42 | 17 PW | ✓ |
| M27 | Omnichannel Contact Centre & Communications | `CCE` | Re-scoped | P1 | W4 *(see note)* | Customer Service Manager | 58 | 32 PW | ✓ |
| M32 | Conversational AI & Virtual Assistant | `CAI` | ★ New | P1 | W4 | Customer Service Manager | 38 | 18 PW | ✓ |
| M35 | Marketing, Campaigns & Demand Generation | `MKT` | ★ New | P2 | W5 | Marketing Head | 40 | 17 PW | ✓ |
| | | | | | | **Category B total** | **320** | **148 PW** | **7/7** |

> **Category B measured — variance against estimate.** The estimate was 243 requirements and
> 133 PW. Measured: **320 requirements (+32%) and 148 PW (+11%)**. Requirement under-estimation
> is now confirmed across two categories (A: +23%, B: +32%); the **correction factor applied to
> Categories C–K is revised from 23% to 30%** (audit finding H-02).
>
> **Two sequencing issues surfaced during specification and require a wave-plan decision:**
>
> 1. **M27 notification service should move from W4 to W1 or W2.** Every module from Wave 1
>    onward needs to notify customers. If M27 arrives in W4, each earlier module builds its own
>    send path — recreating exactly the fragmentation the programme exists to remove. See
>    `M27` §16.3 and open question Q-05.
> 2. **M32 depends on M61 Knowledge, which is scheduled for W6 — two waves later.** An
>    assistant without a knowledge base can answer transactional questions from live ERP data
>    but not "how do I" or "why is this happening". Either M61 core content moves to W4, or M32
>    launches with a reduced intent scope. See `M32` §16.3 and open question Q-01.

### Category C — Commercial, Pricing & Revenue (9)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M37 | Product & Service Catalogue Management | `CAT` | ★ New | P0 | W1 | Chief Commercial Officer | 34 *(est.)* | 18 PW *(est.)* | — |
| M11 | Pricing, Rate Cards & Dynamic Pricing | `PRC` | Re-scoped | P1 | W3 / W7 | Chief Commercial Officer | 36 *(est.)* | 20 PW *(est.)* | — |
| M36 | Quotation, Estimation & Tender Management | `QTE` | ★ New | P1 | W3 | Chief Commercial Officer | 32 *(est.)* | 17 PW *(est.)* | — |
| M08 | Contract Lifecycle Management | `CTR` | Re-scoped | P1 | W4 | Chief Commercial Officer | 44 *(est.)* | 24 PW *(est.)* | — |
| M09 | Warranty, Protection Plans & Claims | `WTY` | Retained | P0 | W4 | Finance Director | 48 *(est.)* | 28 PW *(est.)* | — |
| M39 | Subscription & Recurring Revenue | `SUB` | ★ New | P1 | W4 | CFO | 30 *(est.)* | 17 PW *(est.)* | — |
| M38 | E-Commerce & Digital Storefront | `ECM` | ★ New | P1 | W7 | Chief Commercial Officer | 40 *(est.)* | 24 PW *(est.)* | — |
| M12 | Marketplace & Seller Ecosystem | `MKP` | Re-scoped | P1 | W7 | Chief Commercial Officer | 62 *(est.)* | 40 PW *(est.)* | — |
| M40 | Partner, Channel, Alliance & Franchise | `PCM` | ★ New | P2 | W7 | Chief Commercial Officer | 30 *(est.)* | 16 PW *(est.)* | — |
| | | | | | | **Category C total** | **356** | **204 PW** | **0/9** |

### Category D — Circular & Asset-Based Business (3)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M13 | Rental & Equipment-as-a-Service | `RNT` | Retained | P2 | W6 | Corporate Services Head | 44 *(est.)* | 25 PW *(est.)* | — |
| M14 | Trade-In, Refurbishment & Resale | `TRF` | Retained | P2 | W6 | Retail Operations Head | 39 *(est.)* | 22 PW *(est.)* | — |
| M18 | E-Waste, Recycling & Circular Economy | `ESG` | Retained | P3 | W8 | Quality Manager | 26 *(est.)* | 13 PW *(est.)* | — |
| | | | | | | **Category D total** | **109** | **60 PW** | **0/3** |

### Category E — Supply Chain & Inventory (6)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M15 | Spare Parts & Inventory Management | `INV` | Re-scoped | P0 | W2 | Warehouse Manager | 48 *(est.)* | 24 PW *(est.)* | — |
| M41 | Warehouse Management | `WMS` | ★ New | P1 | W3 | Warehouse Manager | 34 *(est.)* | 20 PW *(est.)* | — |
| M16 | Procurement & Strategic Sourcing | `PRO` | Re-scoped | P1 | W3 | Procurement Manager | 32 *(est.)* | 16 PW *(est.)* | — |
| M42 | Supplier Relationship & Performance | `SRM2` | ★ New | P1 | W4 | Procurement Manager | 26 *(est.)* | 13 PW *(est.)* | — |
| M43 | Demand Planning & Replenishment | `DPL` | ★ New | P2 | W6 | Warehouse Manager | 24 *(est.)* | 14 PW *(est.)* | — |
| M44 | Import, Trade Compliance & Landed Cost | `ITC` | ★ New | P2 | W6 | Procurement Manager | 28 *(est.)* | 15 PW *(est.)* | — |
| | | | | | | **Category E total** | **192** | **102 PW** | **0/6** |

> **Code note.** M42 carries `SRM2` because `SRM` is permanently allocated to M01 under
> rule RG-02. Supplier Relationship Management and Service & Repair Management collide on the
> natural abbreviation; M01 holds the original allocation.

### Category F — Asset, Equipment & Facilities (5)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M17 | Device & Customer Asset Registry | `AST` | Re-scoped | P1 | W2 | Service Ops Director | 34 *(est.)* | 18 PW *(est.)* | — |
| M45 | Enterprise Asset & Test Equipment | `EAM` | ★ New | P2 | W5 | Quality Manager | 26 *(est.)* | 14 PW *(est.)* | — |
| M46 | Fleet & Vehicle Management | `FLT` | ★ New | P2 | W5 | Logistics Manager | 24 *(est.)* | 12 PW *(est.)* | — |
| M47 | Facility, Branch Infrastructure & Workplace | `FAC` | ★ New | P3 | W7 | Branch Operations Lead | 22 *(est.)* | 11 PW *(est.)* | — |
| M48 | IoT Telemetry & Predictive Maintenance | `IOT` | ★ New | P2 | W8 | CTO | 28 *(est.)* | 18 PW *(est.)* | — |
| | | | | | | **Category F total** | **134** | **73 PW** | **0/5** |

### Category G — Finance & Treasury (8)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M19 | Financial Accounting & General Ledger | `FIN` | Re-scoped | P0 | W3 | CFO | 40 *(est.)* | 24 PW *(est.)* | — |
| M20 | Accounts Receivable, Invoicing & Collections | `ARB` | Re-scoped | P0 | W3 | CFO | 36 *(est.)* | 20 PW *(est.)* | — |
| M52 | Accounts Payable & Employee Expense | `APE` | ★ New | P1 | W3 | CFO | 28 *(est.)* | 14 PW *(est.)* | — |
| M50 | Treasury, Cash & Banking | `TRE` | ★ New | P1 | W3 | CFO | 30 *(est.)* | 16 PW *(est.)* | — |
| M51 | Tax & Regulatory Compliance (Bangladesh) | `TAX` | ★ New | P0 | W4 | CFO | 34 *(est.)* | 20 PW *(est.)* | — |
| M53 | Revenue Recognition, Commission & Settlement | `REV` | ★ New | P1 | W4 / W7 | CFO | 38 *(est.)* | 24 PW *(est.)* | — |
| M49 | Fixed Assets & Capital Investment | `FXA` | ★ New | P2 | W5 | CFO | 22 *(est.)* | 11 PW *(est.)* | — |
| M54 | Cost Accounting, Budgeting & FP&A | `FPA` | ★ New | P2 | W6 | CFO | 30 *(est.)* | 17 PW *(est.)* | — |
| | | | | | | **Category G total** | **258** | **146 PW** | **0/8** |

### Category H — People & Workforce (7)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M21 | Core HR & Employee Lifecycle | `HCM` | Re-scoped | P1 | W5 | HR Director | 46 | 18 PW | ✓ |
| M55 | Time, Attendance & Workforce Scheduling | `WFM` | ★ New | P1 | W5 | HR Director | 52 | 22 PW | ✓ |
| M56 | Payroll, Benefits & Statutory Compliance | `PAY` | ★ New | **P0** | W5 | HR Director | 54 | 26 PW | ✓ |
| M57 | Performance, Incentives & Compensation | `PIC` | ★ New | P1 | W5 | HR Director | 42 | 16 PW | ✓ |
| M22 | Learning, Competency & Certification | `LMS` | Re-scoped | P2 | W5 | HR Director | 40 | 16 PW | ✓ |
| M58 | Talent Acquisition & Onboarding | `TAO` | ★ New | P2 | W6 | HR Director | 34 | 12 PW | ✓ |
| M59 | Health, Safety & Wellbeing | `HSE` | ★ New | P2 | W6 | HR Director | 42 | 14 PW | ✓ |
| | | | | | | **Category H total** | **310** | **124 PW** | **7/7** |

> **Category H measured — variance against estimate.** The estimate was 204 requirements and
> 108 PW. Measured: **310 requirements (+52%) and 124 PW (+15%)**. This is the **largest
> requirement variance of any category specified so far** (A +23%, B +32%, H +52%).
>
> **Cause: statutory density.** Bangladesh income tax, provident fund, gratuity, Labour Act
> employment artefacts, Labour Rules safety obligations and PDPA 2026 data-subject obligations
> generate requirements that operational categories do not carry. Categories with comparable
> statutory exposure — **G (Finance & Treasury) and I (Governance, Risk, Quality)** — should be
> expected to behave the same way.
>
> **Consequence for the correction factor.** The 30% factor set after Category B under-predicts
> a statutory-dense category by a wide margin. The factor is now **differentiated**: 30% for
> operational categories, **50% for statutory-dense categories (G, I)**. See §3 below.
>
> **M22 status corrected.** Recorded as *Retained* in the v2.1 draft; it is **Re-scoped** —
> technical knowledge content moved to M61, and dispatch eligibility enforcement was added.
>
> **One sequencing issue surfaced during specification and requires a wave-plan decision:**
>
> **M59's mobile reporting should move from W6 to W3.** FR-HSE-009 (incident, near-miss and
> hazard reporting from the technician app) and FR-HSE-011 (immediate serious-incident alert)
> depend only on **P02** and **M21**, not on the rest of M59. They can ship with the technician
> app in W3 at low incremental cost. The remaining 40 requirements stay in W6. Decision for
> `06-01`. See `M59` §16.3, Q-05.
>
> **One cross-wave build constraint.** M22's eligibility check (FR-LMS-039) is consumed by M02
> at assignment. **M02 goes live in W2; M22 in W5.** The interface must be built into M02 in W2
> as a stub returning "eligible", and connected in W5. Retrofitting a blocking check into a live
> assignment path is materially riskier. See `M22` §16.3.

### Category I — Governance, Risk, Quality & Knowledge (4)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M23 | Quality Management System | `QMS` | Re-scoped | P1 | W5 | Quality Manager | 32 *(est.)* | 16 PW *(est.)* | — |
| M60 | Governance, Risk & Compliance | `GRC` | ★ New | P2 | W6 | CFO | 34 *(est.)* | 18 PW *(est.)* | — |
| M24 | Document, Records & E-Signature | `DMS` | Re-scoped | P1 | W3 | Quality Manager | 28 *(est.)* | 15 PW *(est.)* | — |
| M61 | Knowledge Management & Technical Library | `KMS` | ★ New | P2 | W6 | Quality Manager | 24 *(est.)* | 13 PW *(est.)* | — |
| | | | | | | **Category I total** | **118** | **62 PW** | **0/4** |

### Category J — Data, Analytics & Intelligence (4)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M62 | Data Platform, Warehouse & Governance | `DAT` | ★ New | P1 | W4 / W8 | CTO | 34 *(est.)* | 22 PW *(est.)* | — |
| M25 | Business Intelligence & Reporting | `BID` | Re-scoped | P1 | W4 | CTO | 30 *(est.)* | 16 PW *(est.)* | — |
| M26 | AI/ML Services & Model Operations | `AIM` | Re-scoped | P2 | W6–W8 | CTO | 38 *(est.)* | 30 PW *(est.)* | — |
| M63 | Process Automation & Workflow Orchestration | `BPA` | ★ New | P1 | W3 | CTO | 28 *(est.)* | 16 PW *(est.)* | — |
| | | | | | | **Category J total** | **130** | **84 PW** | **0/4** |

### Category K — Platform & Technology (7)

| ID | Module | Code | Status | Pri | Wave | Business Owner | Reqs | Effort | Spec |
|---|---|---|---|:--:|:--:|---|---:|---:|:--:|
| M28 | Integration, API & Event Platform | `IPF` | Re-scoped | P0 | W1 | CTO | 44 *(est.)* | 26 PW *(est.)* | — |
| M29 | Identity, Access & Information Security | `SEC` | Retained | P0 | W1 | CTO | 44 *(est.)* | 24 PW *(est.)* | — |
| M64 | Master Data Management & Configuration | `MDM` | ★ New | P1 | W2 | CTO | 26 *(est.)* | 14 PW *(est.)* | — |
| M65 | Multi-Entity, Multi-Country & Localisation | `GLO` | ★ New | P2 | W9 | CTO | 30 *(est.)* | 20 PW *(est.)* | — |
| M66 | Internal IT Service Management | `ITS` | ★ New | P2 | W6 | CTO | 22 *(est.)* | 11 PW *(est.)* | — |
| M30 | Platform Administration & Configuration | `ADM` | Re-scoped | P0 | W1 | CTO | 28 *(est.)* | 15 PW *(est.)* | — |
| M67 | Project, Program & Portfolio Management | `PPM` | ★ New | P2 | W7 | CTO | 26 *(est.)* | 14 PW *(est.)* | — |
| | | | | | | **Category K total** | **220** | **124 PW** | **0/7** |

---

## 3. Programme Totals

> **Audit finding H-02, superseded by audit finding H2-01 (2026-08-13).** The v1.0 register
> stated 1,180 requirements and 834 person-weeks for 30 modules. A later revision replaced that
> with a mix of measured and estimated figures for 67 modules. **Both are superseded.**
>
> The Category H audit established that **65 of the 67 module specifications now exist on
> disk**, not the 21 the register recorded. Every figure below is now **counted directly from
> the specification files**, not estimated. Only M66 and M67 remain unwritten.

**Measured 2026-08-13 by direct count of `03_Modules/**/M*.md`.**

| Category | Modules | Specs Written | Requirements | Effort |
|---|---:|:--:|---:|---:|
| A — Service Delivery & Operations | 7 | **7/7** | **362** | **206 PW** |
| B — Customer Engagement & Experience | 7 | **7/7** | **320** | **148 PW** |
| C — Commercial, Pricing & Revenue | 9 | **9/9** | **494** | **262 PW** |
| D — Circular & Asset-Based Business | 3 | **3/3** | **109** | **60 PW** |
| E — Supply Chain & Inventory | 6 | **6/6** | **235** | **119 PW** |
| F — Asset, Equipment & Facilities | 5 | **5/5** | **232** | **114 PW** |
| G — Finance & Treasury | 8 | **8/8** | **333** | **185 PW** |
| H — People & Workforce | 7 | **7/7** | **310** | **124 PW** |
| I — Governance, Risk, Quality & Knowledge | 4 | **4/4** | **170** | **78 PW** |
| J — Data, Analytics & Intelligence | 4 | **4/4** | **146** | **97 PW** |
| K — Platform & Technology | 7 | **5/7** ⚠ | **219** | **120 PW** |
| **Total (written)** | **67** | **65/67** | **2,930** | **1,513 PW** |
| M66 Internal IT Service Management | | ⬜ **not written** | 22 *(est.)* | 11 PW *(est.)* |
| M67 Project, Program & Portfolio Mgmt | | ⬜ **not written** | 26 *(est.)* | 14 PW *(est.)* |
| **Projected total (67 modules)** | **67** | | **~2,978** | **~1,538 PW** |

⚠ **Category K is incomplete.** M66 and M67 are registered modules with **no specification
file**. They are the only two outstanding specifications in the programme.

### 3.1 Estimate Accuracy — The Estimating Model Failed

With every category now measured, the estimate-versus-actual comparison can be closed out.

| | Estimated (v2.1 register) | Measured | Variance |
|---|---:|---:|---:|
| Requirements | ~2,429 | **2,930** | **+21%** |
| Build effort | ~1,317 PW | **1,513 PW** | **+15%** |

Category-level variance was far wider than the aggregate, in both directions:

| Category | Reqs estimated | Reqs measured | Variance |
|---|---:|---:|---:|
| C — Commercial, Pricing & Revenue | 356 | **494** | **+39%** |
| H — People & Workforce | 204 | **310** | **+52%** |
| G — Finance & Treasury | 258 | **333** | **+29%** |
| I — Governance, Risk, Quality | 118 | **170** | **+44%** |
| F — Asset, Equipment & Facilities | 134 | **232** | **+73%** |
| E — Supply Chain & Inventory | 192 | **235** | **+22%** |
| B — Customer Engagement | 243 | **320** | **+32%** |
| A — Service Delivery *(recount)* | 315 | **362** | **+15%** |
| J — Data & Analytics | 130 | **146** | **+12%** |
| D — Circular & Asset-Based | 109 | **109** | **0%** |
| K — Platform & Technology *(5 of 7)* | 220 | **219** | — |

**The pattern is consistent and it has a cause.** Requirement count is under-estimated wherever
a category carries **statutory, contractual or master-data obligations** — C (+39%), F (+73%),
I (+44%), H (+52%), G (+29%). It is estimated accurately where the category is purely
operational — D (0%), J (+12%). Effort tracks much closer than count, because statutory
requirements are numerous but individually small: most resolve to configuration in a versioned
rule pack rather than new code.

**The correction-factor mechanism is now retired.** It existed to project unwritten
specifications. With 65 of 67 written, projection is no longer needed — only M66 and M67 remain
estimated, and their combined 48 requirements cannot move the total materially.

> **Correction to Category A.** The register recorded **388** requirements for Category A. A
> direct count returns **362**. Two causes: (a) M04 was corrected from 31 to 32 requirements in
> the first audit and the register was never updated; (b) **28 requirement IDs in M01, M02 and
> M31 are allocated but unused** — the recorded counts were taken from the highest ID rather
> than the actual count. See audit finding H2-03.

### 3.2 Consequence for the Business Case

| | v1.0 plan (30 modules) | **Measured (67 modules)** | Change |
|---|---:|---:|---:|
| Requirements | 1,180 | **2,930** | **+148%** |
| Build effort | 834 PW | **1,513 PW** | **+81%** |

**The implementation cost line in `00-02` §6 and `06-02` §3.3 is materially understated.** Those
documents model $290K–$470K of implementation and custom development against 834 PW. At the
measured **1,513 PW** the same unit rates give approximately **$525K–$855K**, and the 3-year TCO
moves from **$455K–$780K** to approximately **$690K–$1,150K**.

**These figures are no longer provisional in the way earlier revisions were.** They are counted
from 65 written specifications, not projected. What remains uncertain is not the scope but the
**unit rate and the delivery model** — whether 1,513 PW is delivered by an in-house squad, a
partner, or a mix, and at what blended rate.

**This is a Steering Committee decision (D-14), not something to absorb silently.** The
programme as specified is roughly **1.8× the effort of the approved plan**. The options are to
fund it, to phase it across more waves, or to cut scope — and cutting scope is legitimate, but
it must be a decision taken with the measured figure in front of the Committee.

---

## 4. Register Views

### 4.1 By Priority

| Priority | Count | Modules |
|---|---:|---|
| **P0** | 11 | M01, M02, M09, M15, M19, M20, M28, M29, M30, M33, M37, M51, M56 *(13 — see note)* |
| **P1** | 27 | M03, M04, M05, M07, M08, M10, M11, M12, M16, M17, M23, M24, M25, M27, M31, M32, M34, M36, M38, M39, M41, M42, M46, M50, M52, M53, M55, M57, M62, M63, M64 |
| **P2** | 24 | M06, M13, M14, M18*, M21, M22, M26, M35, M40, M43, M44, M45, M48, M49, M54, M58, M59, M60, M61, M65, M66, M67 |
| **P3** | 3 | M18, M47 |

*Note: the P0 list contains 13 entries; the count column is corrected to 13. M18 is P3.*

**Corrected distribution:** P0 = 13 · P1 = 31 · P2 = 21 · P3 = 2 · **Total 67**

### 4.2 By Wave

| Wave | Months | Modules Delivered | Module Count | Effort |
|---|---|---|---:|---:|
| **W1** | 1–4 | M29, M28, M30, M33, M37, M17*, M01*, M04 | 8 | ~180 PW |
| **W2** | 5–8 | M31, M02, M15, M10, M64, M01*, M17* | 7 | ~150 PW |
| **W3** | 9–13 | M19, M20, M52, M50, M11*, M36, M03, M16, M41, M24, M63 | 11 | ~200 PW |
| **W4** | 14–18 | M08, M09, M39, M51, M53*, M27, M32, M34, M25, M62*, M42 | 11 | ~230 PW |
| **W5** | 19–22 | M21, M55, M56, M57, M22, M23, M05, M45, M46, M49 | 10 | ~190 PW |
| **W6** | 23–26 | M13, M14, M06, M26*, M43, M44, M54, M58, M59, M60, M61, M66 | 12 | ~200 PW |
| **W7** | 27–30 | M38, M12, M40, M11*, M53*, M47, M67 | 7 | ~150 PW |
| **W8** | 31–34 | M62*, M26*, M48, M18 | 4 | ~90 PW |
| **W9** | 35–36 | M65 | 1 | ~20 PW |
| | | | **67** | **~1,302 PW** |

*Modules marked with an asterisk are delivered across two waves; their effort is split.*

> **Audit finding M-09.** Wave capacity has not been validated against the restated effort.
> W4 at ~230 PW against a 17-FTE wave of ~18 weeks gives roughly 306 available person-weeks
> at 100% capacity, or ~245 at 80% — a fit, but with almost no contingency. W3 and W6 are
> similarly tight. A capacity re-plan is required before the roadmap is baselined.

### 4.3 By Business Owner

| Business Owner | Modules |
|---|---|
| Chief Technology Officer | M25, M26, M28, M29, M30, M48, M62, M63, M64, M65, M66, M67 |
| Chief Financial Officer | M19, M20, M39, M49, M50, M51, M52, M53, M54, M60 |
| Chief Commercial Officer | M07, M08, M11, M12, M33, M36, M37, M38, M40 |
| Service Operations Director | M01, M02, M17, M31 |
| HR Director | M21, M22, M55, M56, M57, M58, M59 |
| Quality Manager | M18, M23, M24, M45, M61 |
| Customer Service Manager | M27, M32, M34 |
| Corporate Services Head | M05, M13 |
| Logistics Manager | M03, M46 |
| Warehouse Manager | M15, M41, M43 |
| Procurement Manager | M16, M42, M44 |
| Marketing Head | M10, M35 |
| Branch Operations Lead | M04, M47 |
| Retail Operations Head | M14 |
| Technical Services Head | M06 |
| Finance Director | M09 |

---

## 5. Complete Module Code Register

> **Audit finding H-04.** The previous register listed 30 codes. All 67 are listed here.
> Codes are permanent under rule RG-02.

| Code | Module | Code | Module | Code | Module |
|---|---|---|---|---|---|
| `SRM` | M01 Service Request & Order | `TRF` | M14 Trade-In & Refurbishment | `WMS` | M41 Warehouse Management |
| `FSM` | M02 Field Service & Dispatch | `INV` | M15 Spare Parts & Inventory | `SRM2` | M42 Supplier Relationship |
| `LOG` | M03 Service Logistics | `PRO` | M16 Procurement & Sourcing | `DPL` | M43 Demand Planning |
| `FRD` | M04 Branch & Front-Desk | `AST` | M17 Device & Asset Registry | `ITC` | M44 Import & Landed Cost |
| `RMS` | M05 Remote & Managed Services | `ESG` | M18 E-Waste & Recycling | `EAM` | M45 Enterprise Asset & Test Eq. |
| `DTS` | M06 Data Services | `FIN` | M19 Financial Accounting & GL | `FLT` | M46 Fleet & Vehicle |
| `CRM` | M07 CRM & Account Management | `ARB` | M20 Receivable & Collections | `FAC` | M47 Facility & Workplace |
| `CTR` | M08 Contract Lifecycle | `HCM` | M21 Core HR & Lifecycle | `IOT` | M48 IoT & Predictive |
| `WTY` | M09 Warranty & Claims | `LMS` | M22 Learning & Certification | `FXA` | M49 Fixed Assets & Capital |
| `LOY` | M10 Loyalty & Rewards | `QMS` | M23 Quality Management | `TRE` | M50 Treasury, Cash & Banking |
| `PRC` | M11 Pricing & Rate Cards | `DMS` | M24 Document & Records | `TAX` | M51 Tax & Regulatory (BD) |
| `MKP` | M12 Marketplace & Sellers | `BID` | M25 Business Intelligence | `APE` | M52 Payable & Expense |
| `RNT` | M13 Rental & EaaS | `AIM` | M26 AI/ML Services | `REV` | M53 Revenue & Settlement |
| | | `CCE` | M27 Contact Centre | `FPA` | M54 Costing, Budget & FP&A |
| | | `IPF` | M28 Integration & API | `WFM` | M55 Time & Workforce |
| | | `SEC` | M29 Identity & Security | `PAY` | M56 Payroll & Statutory |
| | | `ADM` | M30 Platform Administration | `PIC` | M57 Performance & Incentives |
| | | `WSR` | M31 Workshop & Depot Repair | `TAO` | M58 Talent Acquisition |
| | | `CAI` | M32 Conversational AI | `HSE` | M59 Health & Safety |
| | | `CPM` | M33 Customer & Party Master | `GRC` | M60 Governance, Risk & Compliance |
| | | `CXM` | M34 Customer Experience | `KMS` | M61 Knowledge Management |
| | | `MKT` | M35 Marketing & Campaigns | `DAT` | M62 Data Platform & Warehouse |
| | | `QTE` | M36 Quotation & Tender | `BPA` | M63 Process Automation |
| | | `CAT` | M37 Product & Service Catalogue | `MDM` | M64 Master Data Management |
| | | `ECM` | M38 E-Commerce & Storefront | `GLO` | M65 Multi-Entity & Localisation |
| | | `SUB` | M39 Subscription & Recurring | `ITS` | M66 Internal IT Service Mgmt |
| | | `PCM` | M40 Partner & Channel | `PPM` | M67 Project & Portfolio Mgmt |

### Retired and Reallocated Codes

| Code | History |
|---|---|
| `BFO` | **Retired.** Used briefly for M04 during drafting; reverted to `FRD` under audit finding C-03. Never to be reissued. |
| `SCM` | **Retired.** Used for M16 in the 30-module register; superseded by `PRO` when procurement narrowed and supplier relationship split to M42. |
| `BIL` | **Retired.** Used for M20 in the 30-module register; superseded by `ARB` when billing mechanics split to M39 and settlement to M53. |
| `HRM` | **Retired.** Used for M21 in the 30-module register; superseded by `HCM` when time, payroll, performance and talent split out. |

---

## 6. Requirement Identifier Allocation

Every module's requirement range is reserved here and mirrored in `05-01`. Ranges are
permanent.

| Module | Prefix | Allocated | Reserved for Growth |
|---|---|---|---|
| M01 | `FR-SRM-` | 001–088 | 089–140 |
| M31 | `FR-WSR-` | 001–058 | 059–090 |
| M02 | `FR-FSM-` | 001–074 | 075–110 |
| M03 | `FR-LOG-` | 001–042 | 043–070 |
| M04 | `FR-FRD-` | 001–031 | 032–060 |
| M05 | `FR-RMS-` | 001–061 | 062–100 |
| M06 | `FR-DTS-` | 001–034 | 035–060 |

Ranges for M07–M30 and M32–M67 are allocated in `05-01` §1.3 as each category's
specifications are written, under rule RG-01.

---

## 7. Module Interaction Matrix — Category A

*(Full 67 × 67 matrix is maintained in `02-04_Module_Dependency_Map.md`. Category A is shown
here because its specifications are complete.)*

Legend: **W** writes / commands · **R** reads · **E** consumes events · **–** no coupling

| ↓ depends on → | M01 | M31 | M02 | M03 | M04 | M05 | M06 | M15 | M17 | M20 | M27 | M33 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **M01 SRM** | — | W | W | W | E | E | W | W | R | W | W | R |
| **M31 WSR** | E | — | – | W | – | – | – | W | R | – | – | – |
| **M02 FSM** | E | – | — | W | – | E | – | W | R | W | W | R |
| **M03 LOG** | E | E | E | — | E | – | R | W | W | W | W | R |
| **M04 FRD** | W | – | – | W | — | – | – | W | R | W | W | R |
| **M05 RMS** | W | – | W | – | – | — | R | – | W | W | W | R |
| **M06 DTS** | W | – | – | W | – | R | — | – | R | W | W | R |

---

## 8. Module Definition-of-Done

No module is accepted at a wave gate until every item is true.

| # | Criterion |
|---|---|
| DoD-01 | Registered here with ID, code, category, priority, wave and owners **before** its specification was written *(rule RG-01)* |
| DoD-02 | All P0 and P1 requirements implemented and demonstrated |
| DoD-03 | Unit test coverage ≥ 80%; 100% on financial and tax calculations |
| DoD-04 | Business rules enforced at the model layer, verified by negative tests through both UI and API |
| DoD-05 | Domain events published through the outbox and registered in the event catalogue |
| DoD-06 | APIs documented in OpenAPI 3.1 and published |
| DoD-07 | Access control, record rules and field permissions defined and negative-tested for every applicable role |
| DoD-08 | Bengali translation complete for all user-facing strings |
| DoD-09 | KPIs instrumented with allocated `KPI-nnn` identifiers and visible in M25 |
| DoD-10 | Data migration mapping defined and dry-run executed where legacy data exists |
| DoD-11 | Operational runbook written |
| DoD-12 | Training material produced in Bengali and English for every affected role |
| DoD-13 | UAT executed and signed by named business super-users |
| DoD-14 | Performance tested against applicable NFRs |
| DoD-15 | Security review completed with zero open high or critical findings |
| DoD-16 | Rollback plan documented and rehearsed |
| **DoD-17** | **Regulatory citations verified current, with a verified-on date** *(added following audit finding C-04)* |

---

## 9. Legacy Decommission Map

| Legacy System / Practice | Replaced By | Wave |
|---|---|---|
| Service order spreadsheets (per branch) | M01 + M04 | W2 |
| Workshop whiteboards and paper job cards | M31 | W2 |
| WhatsApp / phone dispatch | M02 + M27 | W2 |
| Paper service forms and QC checklists | M01 + M02 + M23 | W2 |
| Branch inventory spreadsheets | M15 | W2 |
| `station.1000fix.com` order tracking | P01 Customer Portal | W2 |
| Legacy tracker `123.0.26.238/orderTracking` | P01 Customer Portal | W2 |
| Phone-coordinated pick & drop | M03 | W3 |
| Standalone accounting software | M19 + M20 + M52 | W3 |
| Manual invoice preparation | M20 | W3 |
| Email-based warranty claims | M09 + P08 | W4 |
| AMC tracking spreadsheets | M08 | W4 |
| Manual payroll in Excel | M56 | W5 |
| Attendance sign-in books | M55 | W5 |
| Paper ISO records | M23 + M24 | W5 |
| Ad-hoc remote support tools | M05 | W5 |
| Data recovery job cards | M06 | W6 |
| Rental log books | M13 | W6 |
| Refurbishment tally sheets | M14 | W6 |
| Manual partner commission calculation | M53 | W7 |
| Excel management reporting packs | M25 + M62 | W8 |

---

## 10. Change History

| Version | Date | Change |
|---|---|---|
| 2.0 | 2026-08-12 | Initial register — 30 modules, 5 pillars |
| **2.1** | **2026-08-12** | **Restated on the 67-module, 11-category architecture. Registered M31 (audit C-02). Reverted M04 to code `FRD` (audit C-03). Published the complete 67-code register (audit H-04). Restated requirement and effort totals with the provisional marking and business-case consequence (audit H-02). Added rules RG-01…RG-05 and DoD-17.** |
| 2.2 | 2026-08-12 | Category H measured — seven specifications written; totals restated at 310 requirements and 124 PW |
| **2.3** | **2026-08-13** | **All figures recounted by direct enumeration (audit 2, `00-07`). Repository holds 65 of 67 module specifications, not 21 — §3 rewritten with counted figures for all eleven categories: 2,930 requirements and 1,513 PW. Category A corrected 388 → 362 (28 allocated-but-unused IDs, audit H2-03). M66 and M67 flagged as the only outstanding specifications (H2-02). Correction-factor mechanism retired. Added rule RG-06; extended RG-01 to all shared identifier spaces and RG-02 to code-variant allocation.** |

---

*Register maintained by Enterprise Architecture · 1000FiX ERP System v2.0*
