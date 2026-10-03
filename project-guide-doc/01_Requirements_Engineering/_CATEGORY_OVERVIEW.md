---
id: PGD-CAT-01
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
owner: Lead Business Analyst / Requirements Manager
last_enumerated: 2026-08-18 03:05 (+06)
audit: ../_AUDIT/PGD-AUDIT-004_Category_01_Requirements_Engineering_Audit.md
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# Category 01 — Requirements Engineering (`RQ`)

**10 of 10 documents authored · 34 audit findings · 12 closed, 22 open**

## Purpose

A BRD states what the **business** wants. A URD states what **users** want. Neither is buildable.
This category converts business and user intent into **testable, traceable, unambiguous statements
a developer can implement and a tester can verify** — and maintains the thread from objective to
requirement to design to test to acceptance.

## Documents

All ten issued 2026-08-18. Status is a **qualified ✅**: tests (a), (b) and (c) of `PGD-000` §0.3
are met and verified; test (d)'s approval record does not exist and cannot until `GV-002`
constitutes a body that can create one (`PGD-A1-09`).

| ID | Document | Status | Pri | Needed by |
|---|---|:--:|:--:|:--:|
| [`RQ-001`](RQ-001_Software_Requirements_Specification.md) | **Software Requirements Specification (SRS)** — ISO/IEC/IEEE 29148:2018 **§9.6** | ✅ † | **P0** | **Now** |
| [`RQ-002`](RQ-002_System_Requirements_Specification.md) | System Requirements Specification (SyRS) — §9.5 | ✅ † | P1 | W1 |
| [`RQ-003`](RQ-003_Fit_Gap_Analysis_and_Functional_Design_Specification.md) | **Fit-Gap Analysis & Functional Design Specification** | ✅ † | **P0** | **Now** |
| [`RQ-004`](RQ-004_Requirements_Traceability_Matrix.md) | Requirements Traceability Matrix (RTM) | ✅ † | **P0** | W1 |
| [`RQ-005`](RQ-005_Requirements_Management_Plan.md) | Requirements Management Plan | ✅ † | P1 | W1 |
| [`RQ-006`](RQ-006_Non_Functional_Requirements_Specification.md) | Non-Functional Requirements Specification — ISO/IEC 25010:**2023** | ✅ † | P0 | W1 |
| [`RQ-007`](RQ-007_Business_Process_Model_Repository.md) | Business Process Model Repository (BPMN 2.0) | ✅ † | P1 | W1 |
| [`RQ-008`](RQ-008_Use_Case_and_User_Story_Specification.md) | Use Case & User Story Specification with Acceptance Criteria | ✅ † | P1 | W1 |
| [`RQ-009`](RQ-009_Business_Rules_Specification.md) | Business Rules Specification | ✅ † | P0 | W1 |
| [`RQ-010`](RQ-010_Acceptance_Criteria_and_Definition_of_Done_Standard.md) | Acceptance Criteria & Definition of Done Standard | ✅ † | P1 | W1 |

## What the category established

Counted from the filesystem at **2026-08-18 03:05 (+06)**, per `PG-03` and `PG-M11`.

| # | Established | Where |
|---|---|---|
| 1 | **One requirement denominator: 3,347 adopted + 42 specified = 3,389**, with the counting rule and a reproduction command. Closes audit `TS-01` | `RQ-001` §3.10.5 |
| 2 | The **requirement construct**, 13 mandatory attributes, the nine individual and five set characteristics, and 12 automated conformance checks | `RQ-001` §3.10.2–§3.10.10 |
| 3 | **42 programme-level requirements** `SWR-001`–`SWR-042` that no module owned — including the ten PDPA obligations reallocated out of the NFR space | `RQ-001` §3.12 |
| 4 | **71 system requirements** `SYR-001`–`SYR-071` above the software boundary, including the unsatisfiable-but-stated lawful DR obligation | `RQ-002` §4 |
| 5 | The **fit-gap disposition taxonomy** with an evidence standard, and the honest starting position: **3,389 `undetermined`** | `RQ-003` §3, §5.5 |
| 6 | **17 trace link types, 12 reciprocal**, and ten coverage measures with formulas | `RQ-004` §3.2, §5.2 |
| 7 | **Allocation authority named for 17 identifier spaces**, with a mandatory four-repository sweep before any new space | `RQ-005` §7 |
| 8 | The NFR set **re-based onto ISO/IEC 25010:2023** — 119 requirements across nine characteristics, five duplicate identifiers resolved, **Safety populated for the first time** | `RQ-006` §4 |
| 9 | A **30-model process inventory** with trigger-based selection, conforming to `SP-003` rather than restating it | `RQ-007` §4 |
| 10 | Given/When/Then, an 11-item **Definition of Ready**, and story-point sizing — none of which existed | `RQ-008` §4 |
| 11 | The **business rule reconciliation** of two disjoint populations (140 catalogue vs 1,330 estate) and the `H`-classification decision test | `RQ-009` §4, §6 |
| 12 | **Eight evidence types** and a Definition of Done at four levels | `RQ-010` §3, §4 |

## The five findings that matter most

From [`PGD-AUDIT-004`](../_AUDIT/PGD-AUDIT-004_Category_01_Requirements_Engineering_Audit.md) —
5 critical, 13 high, 12 medium, 4 low.

| ID | Finding | Why it matters |
|---|---|---|
| `RQA-02` | **Zero of 3,347 requirement rows contains the word `shall`** | No row is a requirement in the sense a contract, a test or the standard uses |
| `RQA-14` | **The layer coverage percentages carrying the cost model sum to 1,180** — the superseded 30-module baseline | The 834 PW and $455K–780K figures descend from a requirement population the programme no longer has |
| `RQA-15` | **The `Layer` column marks 92% of rows `L5` custom; the stack summary claims 25%** | A 3.7× contradiction on the single number the budget rests on |
| `RQA-08` | **`FR-ECM-` resolves to M12 via the register and M38 via the estate** | Every citation of an `FR-ECM` identifier is ambiguous |
| `RQA-27` | **`BRU-ECM-01`…`-10` denote two rules each**, including the seller-verification hard block | A control on 500–2,000 external parties resolves two ways |

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `00_Governance` | `GV-002` must constitute the body that can approve; `GV-003` records requirement decisions; `GV-006` baselines scope; `GV-007` sizes what `RQ-003` measures |
| Upstream | `99_Reference` | `RR-002` must ratify the `SWR`, `SYR`, `FG` and `BPM` reservations and rule on the `RQ-nn`/`RQ-nnn` and `PGD-AUDIT-002` collisions |
| Downstream | `02_Architecture` | `AR-001` derives from the requirement set and `RQ-006`; `AR-003` from `RQ-003`'s gaps |
| Downstream | `03_Data`, `04_Integration` | `DA-001`/`DA-002` and `IN-002`/`IN-003` close trace links `T-10` and `T-06` |
| Downstream | `05_Security` | `SC-002` is a prerequisite for `NFR-113`; `SC-004` must register `R39`–`R50` and `SOD-13`–`SOD-30` |
| Downstream | `07_Build` | `BE-005` is the sole `CD` allocation authority; `BE-008` consumes the sizing unit |
| Downstream | `08_Quality` | Every test case derives from `RQ-001` §3.19; coverage from `RQ-004` §5 |
| Downstream | `14_Commercial` | `CO-003` accepts against the `RQ-001` baseline and the `RQ-010` standard |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Implementation vendor, developers, QA, business owners |
| Change frequency | **High until baseline, then controlled** — `RQ-005` §6 |
| Standards basis | ISO/IEC/IEEE 29148:2018 · **ISO/IEC 25010:2023** · ISO/IEC/IEEE 12207:2017 Annex H · OMG BPMN 2.0 · OMG SBVR · OMG DMN 1.4 · ISO 9001:2015 §4.4, §8.6 · BABOK v3 |

## Existing material these documents build on

`1000fix_ERP_Module/03_Modules/` — 67 modules and 12 portals, §5 and §9 ·
`05_Cross_Cutting_Specifications/05-01`, `05-05`, `05-06` ·
`primary-doc/…BRD.md` §3, §8, §10, §13 · `…URD.md` §6–17 · `…RFP.md` §5–10 ·
`project_content/06_Process_SOP_and_Workflow/` — `SP-001`…`SP-034`

> **Correction carried from `RQA-24`.** The figure *"255 user stories"* used in earlier issues of
> this overview and in `PGD-000` counts acceptance-criteria markers. **Counting story headers
> returns 245.**

---

*Category 01 · `RQ` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
