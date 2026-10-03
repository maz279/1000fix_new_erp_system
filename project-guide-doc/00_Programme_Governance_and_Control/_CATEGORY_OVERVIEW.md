---
id: PGD-CAT-00
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-18
status: COMPLETE — 11 of 11 authored, pending approval
owner: Programme Director / PMO
enumerated_on: 2026-08-18 03:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
audit: ../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md
---

# Category 00 — Programme Governance & Control (`GV`)

> **All eleven documents authored and issued 2026-08-18.** This is the first category in the
> register to be completed. Audited the same day in
> [`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) — **25 findings,
> 12 closed, 13 open**; sixteen against the existing estate, nine against this category's own
> authoring.

## Purpose

These documents decide **who may decide**, **what "done" means**, and **what the programme costs
and is worth**. Every other category in this repository inherits its authority from here.

## Documents

| ID | Document | Status | Pri | Size |
|---|---|:--:|:--:|---:|
| `GV-001` | [Programme Charter & Mandate](GV-001_Programme_Charter_and_Mandate.md) | ✅ † | P0 | 55 KB |
| `GV-002` | [Governance Framework, RACI & Terms of Reference](GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) | ✅ † | P0 | 59 KB |
| `GV-003` | [Decision Log & Change Control Procedure](GV-003_Decision_Log_and_Change_Control_Procedure.md) | ✅ † | P0 | 44 KB |
| `GV-004` | [Integrated Programme Plan & Master Schedule](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) | ✅ † | P0 | 43 KB |
| `GV-005` | [RAID Register](GV-005_RAID_Register.md) | ✅ † | P0 | 41 KB |
| `GV-006` | [Scope Management & Baseline Control Procedure](GV-006_Scope_Management_and_Baseline_Control_Procedure.md) | ✅ † | P1 | 33 KB |
| `GV-007` | [Estimation Model & Resource Plan](GV-007_Estimation_Model_and_Resource_Plan.md) | ✅ † | P0 | 44 KB |
| `GV-008` | [Programme Budget & Cost Baseline](GV-008_Programme_Budget_and_Cost_Baseline.md) | ✅ † | P0 | 37 KB |
| `GV-009` | [Wave Gate & Phase Exit Criteria Handbook](GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) | ✅ † | P1 | 44 KB |
| `GV-010` | [Programme Assurance & Independent Review Plan](GV-010_Programme_Assurance_and_Independent_Review_Plan.md) | ✅ † | P1 | 37 KB |
| `GV-011` | [Documentation Control & Configuration Management Plan](GV-011_Documentation_Control_and_Configuration_Management_Plan.md) | ✅ † | P1 | 42 KB |

† **The ✅ is qualified.** `PGD-000` §0.3 test (d) requires *"a named owner and an approval
record."* All eleven have named owners and **none has an approval record**, because no constituted
body can approve one (`PGD-A1-09`). Finding `PGD-A2-25`; closes with `GV-001` condition `CC-01`.

## What this category found

Eleven documents were written to close gaps. They also surfaced sixteen defects in the estate that
no prior audit had found. The five that change decisions:

| # | Finding | Where |
|---|---|---|
| 1 | **The wave plan is capacity-infeasible.** Wave 1 demands 217 PW against 40.7 effective build person-weeks — **5.33×**. W2 1.76×, W4 1.32×; W6–W9 half empty | `GV-004` §5 — closes `M-09` |
| 2 | **763 PW across 37 modules has no wave, no team and no date** — 41% of the specified build. Spare capacity in W5–W9 is 313 PW, leaving a 450 PW shortfall | `GV-004` §5.4 |
| 3 | **298 PW of portal build has never appeared in any effort figure.** Every published number (834 / 1,302 / 1,513) is module-only. The counted build position is **1,842 PW** | `GV-007` §4.3 |
| 4 | **`06-02` overstates three-year benefit by 2.2×–3.3×** — independently of any cost restatement. §3.2's column header contradicts its own values, and §3.4 is unsupported by either reading | `GV-008` §7.2 |
| 5 | **644 files. Zero under version control.** Four of the estate's five recurring defect classes would be caught mechanically by a pre-commit hook | `GV-011` §10 |

And the number that frames all of them:

> **`GV-003` §5.6 — twenty-four decisions open, one escalated, and *zero taken*.** Five months of
> work, 610 documentation files, and not one recorded programme decision. `D-013` and `D-014` both
> block Wave 1.

## What "done" looks like for this category

1. ~~A named sponsor has signed `GV-001`~~ → **`GV-001` is written and awaiting Board signature.**
   The five open decisions in `00-01` §6 now have an empowered body (`GV-002` §9.2).
2. ~~`GV-003` exists and decision **D-14** has a record~~ → **Done.** `D-014` is recorded in full
   at `GV-003` §5.3, with the counted figures the Board has never seen.
3. ~~The 834 vs 1,513 PW variance is resolved in `GV-007`~~ → **Sized, not resolved.** The variance
   is larger than stated: **2,537–3,931 PW against 834**. `GV-008` restates the cost baseline at
   **$1.02M–$2.61M** against the $455K–$780K the Board holds. **`D-014` remains the Board's.**
4. **Outstanding:** no document anywhere in the estate may be quoted as authoritative while marked
   `DRAFT FOR APPROVAL`. That includes these eleven. `CC-01` closes it.

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Downstream | **All** | Nothing is baselined until `GV-001` and `GV-002` are approved |
| Upstream | `14_Commercial` | `CO-005` TCO must absorb the two streams `GV-007` sized |
| Upstream | `15_Benefits` | `BM-002` KPI baselines — 44 of 95 absent; `BM-003` must resolve `PGD-A2-10` |
| Upstream | `02_Architecture` | **`AR-006` module dependency map is a hard input to `GV-004` and does not exist.** The wave sequence is unverified |
| Peer | `99_Reference` | **`RR-002` identifier standard is the control `GV-011` enforces and it does not exist.** Five audits have found identifier failures; this category committed a sixth (`PGD-A2-19`) |

## Open items this category cannot close

| # | Item | Owner | Why not closable here |
|---|---|---|---|
| 1 | `D-001`, `D-013`, `D-014` | Board | Three decisions move governance, technical and cost simultaneously |
| 2 | `PGD-A2-04`, `PGD-A2-05` | Steering Cttee / ARB | The wave plan's requirement and module allocations need decisions, not documentation |
| 3 | `PGD-A2-01`, `-02`, `-09`, `-10`, `-14`, `-16` | PMO / CFO / EA | **Referred** — corrections in `1000fix_ERP_Module`, outside this repository's authority under `PG-M8` |
| 4 | `PGD-A2-23` | Audit Cttee | This category is entirely a class I0 self-assessment. Its three quantitative conclusions should be independently re-derived |
| 5 | `PGD-A2-15` | CTO | Version control is a one-week action with programme-wide effect |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Board, CEO, CFO, CTO, Steering Committee, PMO |
| Secondary | Implementation vendor, internal and external audit |
| Change frequency | **Low** — changes only on formal decision |
| Standards basis | ISO 21500:2021 · ISO 21502:2020 · ISO 21503:2022 · ISO 10007:2017 · ISO 31000:2018 · **ISO/IEC 38500:2024 (edition 3)** · ISO 19011:2018 · ISO 9001:2015 · PMBOK Guide 7th Edition · PRINCE2 7th Edition (2023) · AACE RP 17R-97 · IIA Three Lines Model (2020) · UK IPA Gateway practice |

## Existing material built from

`1000fix_ERP_Module/00_Governance_and_Charter/00-01` … `00-04`, `00-06`, `00-07` ·
`1000fix_ERP_Module/02_Architecture/02-02`, `02-05` ·
`1000fix_ERP_Module/06_Delivery_and_Implementation/06-01`, `06-02` ·
`1000fix_ERP_Module/03_Modules/**/M*.md`, `P*.md` — 79 `Effort estimate` rows, directly summed ·
`project_content/00_Content_Governance_and_Standards/CG-002`, `CG-005`, `CG-006`, `CG-007` ·
`project_content/_AUDIT/AUDIT-001` … `AUDIT-019` · `primary-doc/` BRD, RFP, URD

---

*Category 00 · `GV` · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*11 of 11 authored 2026-08-18 · Audited `PGD-AUDIT-002` · Independence class I0*
