---
id: PGD-README
title: Project Guiding Document Repository
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-18
status: ACTIVE
last_enumerated: 2026-08-18 03:05 (+06)
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer, 1000FiX Services Limited
---

# 1000FiX ERP System v2.0
# Project Guiding Document Repository

**140 registered documents · 17 categories · 130 written and reflected in the register ·
133 on disk · 7 still missing, 3 of them blocking**

> **⚠ Counts regenerated at 2026-08-19 03:02 (+06), and the estate is still moving faster than the
> register.** **133 registered documents exist** — 131 in this repository plus `CO-001` and
> `BM-001`, which carry ✅ from outside it. The register reflects **130**, because `BM-002`,
> `RR-001` and `RR-002` were written by other sessions whose rows are not yet updated — and no
> session may set ✅ for work it has not assessed against `PGD-000` §0.3's four tests.
>
> **This repository moved by eight documents in the twenty-six minutes** between `CO-003`'s first
> enumeration and its audit re-run (`CVA-27`). Every count on this page is a reading at its stated
> timestamp and at no other moment.
>
> | Category | On disk | Register row current? |
> |---|---:|---|
> | 00–10 Governance → Infrastructure | 11 · 10 · 13 · 9 · 8 · 11 · 8 · 9 · 11 · 7 · 9 | ✔ |
> | **11 Service Operations & Support** | **6** | ✔ **AUTHORED 2026-08-19** |
> | 12 Release · 13 Training | 6 · 5 | ✔ |
> | 14 Commercial · 99 Reference | 4 · 1 | ✘ **rows not yet updated** |
>
> This is at least the **tenth** recorded instance of the baseline moving during authoring —
> **twenty-three files appeared in sixty-three minutes** while Category 11 was being written, which
> made **nine** absence assertions inside it false before it was finished; all nine are corrected
> and recorded in [`PGD-AUDIT-CAT-11`](_AUDIT/PGD-AUDIT-CAT-11_Category_11_Service_Operations_and_Support_Audit.md) `SVA-16`
> rather than silently fixed. **`RR-002` was issued during that window** and its `IDC-13` closes the
> identifier-race half of the problem. **The staleness half is untouched**: `RG-08` — timestamped
> enumeration — has now been recommended **nine** times and never ratified, and `PG-M12` (version
> control) is still not in place across 644+ files.

> **Category 00 — Programme Governance & Control — is complete.** Eleven documents
> (`GV-001` … `GV-011`) were authored and issued **2026-08-18** and audited the same day in
> [`PGD-AUDIT-002`](_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md): **27 findings,
> 13 closed, 14 open**. It is the first category in the register to be finished.

---

## What this repository is

The 1000FiX programme holds **621 documentation files** across four repositories *(enumerated 2026-08-18 03:05 +06; the estate is being actively authored — recount before quoting)*. They answer
*why* the system is needed, *what* it must do, *who* uses it and *what content* must be written
to operate it.

**They do not answer how it is engineered.**

This repository holds the register of every document that does — the Software Requirements
Specification, the Software Architecture Document, the design descriptions, the database schema,
the API contracts, the threat model, the DPIA, the test strategy, the migration strategy, the
CI/CD design, the runbooks and the registers that hold it all together.

---

## Start here

> **Read the audit before you rely on this register.** Thirteen findings were raised against it —
> two critical — of which **eleven are closed and two remain open**. Both open findings need a
> decision from outside this repository.
>
> Three of the closed findings were committed *by the register itself*: two identifier collisions,
> by the document that names identifier collisions as the estate's largest defect class, and one
> arithmetic error in the audit's own findings count — the same error it had just raised against
> the register. Those are recorded rather than smoothed over, and each produced a mechanical
> control (`PG-M9`, `PG-M10`, `PG-M11`) rather than a resolution to be more careful.

| I want to… | Go to |
|---|---|
| **See the complete register — 140 documents** | [PGD-000 Master Register](PGD-000_Master_Register_of_Project_Guiding_Documents.md) |
| **See what is known to be wrong with it** | [PGD-AUDIT-001 Register Integrity Audit](_AUDIT/PGD-AUDIT-001_Register_Integrity_Audit.md) — 13 findings, **2 open** · [PGD-AUDIT-002 Category 00 Governance Audit](_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) — 27 findings, **14 open** |
| **Read the completed category** | [00_Programme_Governance_and_Control](00_Programme_Governance_and_Control/) — `GV-001` … `GV-011`, all eleven written |
| **Understand the single biggest gap** | [PGD-000 §0.2](PGD-000_Master_Register_of_Project_Guiding_Documents.md) |
| **See what to write first** | [PGD-000 §2.1](PGD-000_Master_Register_of_Project_Guiding_Documents.md) — the critical path |
| **See the order to write things in** | [PGD-000 §2.2](PGD-000_Master_Register_of_Project_Guiding_Documents.md) — tranches T0–T8 |
| **See what is already strong** | [PGD-000 §2.3](PGD-000_Master_Register_of_Project_Guiding_Documents.md) |
| Understand the folder layout and naming rules | [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) |
| Write a guiding document | [_templates/TPL_Guiding_Document.md](_templates/TPL_Guiding_Document.md) |
| Understand one category in depth | Open its folder → `_CATEGORY_OVERVIEW.md` |

---

## The position, in one table

Enumerated from the filesystem at **2026-08-18 03:05 (+06)**. These are counted figures, not
projections — rule `PG-03`.

| Status | Count | Δ | Meaning |
|:--:|---:|:--:|---|
| ✅ | **36** | +34 | Exists as a controlled artefact — the RFP, the KPI & Benefits document (qualified by `H-02`), **the eleven Category 00 governance documents**, **the ten Category 01 requirements documents** and **the thirteen Category 02 architecture documents**. Every one of these ✅ is qualified by `PGD-A2-25` and `RQA-34`'s sibling note: none has an approval record, because no body can approve one |
| ◐ | **46** | −14 | Material exists inside documents written for another purpose. Read as *"absent, with useful source material"* — `PGD-A1-08` |
| ⬜ | **14** | −7 | Does not exist |
| ⛔ | **44** | −13 | Does not exist, **and a Wave 1 activity, statutory obligation or go-live gate already depends on it** |
| | **140** | | 36 + 46 + 14 + 44 = 140 ✓ |

**The programme has 3,347 requirement rows** *(counted 2026-08-18 03:04 +06; `RQ-001` §3.10.5 fixes this as the single denominator, closing audit `TS-01`)* **— and, of them, zero are well-formed requirement statements** *(`RQA-02`: no row contains the word `shall`)*.

**And, as of `GV-003`: twenty-four decisions open, one escalated, and _zero taken_ in five months.**

---

## The seventeen categories

| Folder | Code | Docs | ⛔ | What it answers |
|---|:--:|---:|---:|---|
> **⚠ This README lags `PGD-000`. Treat the register as the authority.**
>
> Re-enumerated **2026-08-19 09:40 (+06)**: `project-guide-doc/` holds **136 files**, the workspace
> holds **757**, and **`PGD-000` §0.5 records 88 of 140 documents authored**. Figures elsewhere in
> this README — *"36 ✅"*, *"51 on disk"*, *"621 documentation files"* — were correct when written
> and are now several authoring sessions stale.
>
> Only the **Category 09** row below was updated at this issue. The other rows are **left untouched
> deliberately**: asserting a status for work this session did not author and has not assessed
> against `PGD-000` §0.3's four tests is precisely the unevidenced status change `PG-M2`, `PG-07`
> and `PGD-A1-08` forbid — the same restraint `BEA-21` recorded for Categories 04–06.
>
> Recorded as `MGA-15` in
> [`PGD-AUDIT-CAT-09`](_AUDIT/PGD-AUDIT-CAT-09_Category_09_Data_Migration_and_Cutover_Audit.md).
> The durable fix is `RG-08` (timestamped enumeration) and `RR-006` (cross-reference index), both
> unwritten.

| [00_Programme_Governance_and_Control](00_Programme_Governance_and_Control/) ✅ **complete** | `GV` | 11 | **0** | Who decides, what "done" means, what it costs |
| **[01_Requirements_Engineering](01_Requirements_Engineering/)** ✅ **complete** | `RQ` | 10 | **0** | **AUTHORED 2026-08-18** — what exactly shall the system do, testably |
| **[02_Architecture_and_Design](02_Architecture_and_Design/)** | `AR` | 13 | **0** ✅ | **AUTHORED 2026-08-18** — how it is structured so it works and stays changeable |
| **[03_Data_and_Information_Architecture](03_Data_and_Information_Architecture/)** | `DA` | 9 | **0** ✅ | **AUTHORED 2026-08-18** — what the data is, who owns it, how it is protected |
| [04_Integration_and_API_Engineering](04_Integration_and_API_Engineering/) | `IN` | 8 | **0** ✅ | What are the contracts between systems |
| [05_Security_Privacy_and_Compliance](05_Security_Privacy_and_Compliance/) | `SC` | 11 | **0** ✅ | Is it safe, and is it lawful |
| **[06_Experience_and_Interface_Design](06_Experience_and_Interface_Design/)** ✅ **complete** | `UX` | 8 | **0** ✅ | **AUTHORED 2026-08-18** — what the user actually sees and does. **1,404 screens counted**, 130 of them bespoke |
| [07_Build_Engineering_and_Development_Standards](07_Build_Engineering_and_Development_Standards/) | `BE` | 9 | **0** ✅ | How do developers work, consistently |
| **[08_Quality_Engineering_and_Test](08_Quality_Engineering_and_Test/)** ✅ **complete** | `QA` | 11 | **0** ✅ | **AUTHORED 2026-08-18** — how do we know it works, and how much of it is actually proven |
| **[09_Data_Migration_and_Cutover](09_Data_Migration_and_Cutover/)** ✅ **complete** | `MG` | 7 | **0** ✅ | **AUTHORED 2026-08-18** — how does the old data become the new data, safely. **357 KB, 257 rules**; closes `AUDIT-011`'s CRITICAL finding. Audited [`PGD-AUDIT-CAT-09`](_AUDIT/PGD-AUDIT-CAT-09_Category_09_Data_Migration_and_Cutover_Audit.md) |
| [10_Infrastructure_DevOps_and_Environments](10_Infrastructure_DevOps_and_Environments/) | `PE` | 9 | **0** ✅ | What does it run on, and how is it deployed |
| **[11_Service_Operations_and_Support](11_Service_Operations_and_Support/)** ✅ **complete** | `SV` | 6 | **0** ✅ | **AUTHORED 2026-08-19** — how is it kept alive. **490 KB, 221 rules**; discharges `AUDIT-017`'s *"operational content and no operational capability"* at the specification layer **and quantifies it**: planned maintenance alone breaches the 24×7 availability target (240 min against a 131.5 min budget), the on-call rota needs **eleven** people not ten, hypercare is **≈ 678 PW ≈ 45% of the build estimate** in no estimate, and **two `P0` services have no runbook**. Audited [`PGD-AUDIT-CAT-11`](_AUDIT/PGD-AUDIT-CAT-11_Category_11_Service_Operations_and_Support_Audit.md) |
| **[12_Release_Deployment_and_Transition](12_Release_Deployment_and_Transition/)** ✅ **complete** | `RL` | 6 | **0** ✅ | **AUTHORED 2026-08-19** — how does it go live, nine times |
| **[13_Training_Change_and_Adoption](13_Training_Change_and_Adoption/)** ✅ **complete** | `CH` | 5 | **0** ✅ | **AUTHORED 2026-08-19** — how do people actually use it. **3,829 lines, 128 rules**; the estate's first counted training model (**12,306–21,759 learner-hours**, **380–525 trainer-days**, **2.8–3.5 trainer FTE against 0 established**) and first counted business-side commitment (**1,190–1,622 PW**). Audited [`PGD-AUDIT-CAT-13`](_AUDIT/PGD-AUDIT-CAT-13_Category_13_Training_Change_and_Adoption_Audit.md) |
| **[14_Commercial_Vendor_and_Contract](14_Commercial_Vendor_and_Contract/)** ✅ **complete** | `CO` | 6 | **0** ✅ | **AUTHORED 2026-08-19** — what is bought, from whom, for how much. **4,850 lines, 230 rules across six prefixes, 22 findings.** The estate's first **five-year** TCO (**Tier 1 $1,912K–$5,367K**, a steady-state run rate of **$337K/yr** nobody had computed) and its first **tax, FX and escalation** lines. **`CVA-02` is Critical and expires 17 September 2026**: the live RFP publishes an envelope and an effort basis that `GV-007` and `GV-008` superseded days after issue. Audited [`PGD-AUDIT-CAT-14`](_AUDIT/PGD-AUDIT-CAT-14_Category_14_Commercial_Vendor_and_Contract_Audit.md) |
| [15_Benefits_Measurement_and_Assurance](15_Benefits_Measurement_and_Assurance/) | `BM` | 5 | **3** | Did it deliver what it promised |
| [99_Reference_Registers_and_Glossary](99_Reference_Registers_and_Glossary/) | `RR` | 6 | **4** | What does this term / identifier / citation mean |
| | | **140** | **7** | |

---

## The ten documents to write first

From [PGD-000 §2.1](PGD-000_Master_Register_of_Project_Guiding_Documents.md) and §2.2 tranches
T0–T1. Each unblocks a class of work rather than a single task.

| # | ID | Document | Unblocks |
|---:|---|---|---|
| 1 | `RR-002` | Identifier Convention Standard | Prevents recurrence of 8 existing findings — and **3** committed by this register, the third being `PGD-A2-19` |
| 2 | ~~`GV-003`~~ | ~~Decision Log & Change Control~~ | ✅ **Written 2026-08-18.** `D-014` is recorded at last — and the log shows **24 decisions open and 0 taken** |
| 3 | `RQ-001` | **Software Requirements Specification** | Vendor pricing, test derivation, acceptance |
| 4 | `RQ-003` | Fit-Gap Analysis & FDS | The entire cost model — what Odoo already does |
| 5 | `BE-005` | Custom Development Master Register | **The build backlog cannot lawfully be created without it** |
| 6 | `AR-001` | **Software Architecture Document** | Every build decision across 80 deliverables |
| 7 | `SC-003` | DPIA (PDPA 2026) | Lawful basis for W2 processing; enforcement lands in Wave 4 |
| 8 | `SC-007` | Data Residency Design | Closes two critical findings, one of them a live DR illegality |
| 9 | `MG-001` | Data Migration Strategy | Closes the `AUDIT-011` critical finding |
| 10 | `BM-002` | KPI Baseline Measurement | ~BDT 396 lac of benefit becomes unclaimable once go-live changes the baseline |

**`BM-002` is time-critical in a way the others are not.** Baselines can only be measured before
the system changes the operating environment. Every week of delay permanently forecloses part of
the benefit case.

---

## What is already strong

This repository names gaps, so it is worth being explicit about what it is *not* criticising.

| Asset | Assessment |
|---|---|
| **67 module specifications** | Written to a consistent, enforced 19-section template with declared scope boundaries. Better than most enterprise programmes achieve |
| **12 portal specifications** | Complete — 771 KB, 10,020 lines |
| **468 content files** | Master data, UI copy, SOPs, legal, training, migration mappings. Very few ERP programmes write this at all, and almost none write it *before* build |
| **The audit culture** | Three repository audits and nineteen category audits, self-critical to the point of recording *"1 critical, against the auditor's own authoring"*. **This repository exists because that culture surfaced the gaps** |
| **Bangladesh regulatory grounding** | Mushak 6.1/6.2/6.3/6.6/9.1, BEFTN, NBR VAT Online, PDPA 2026, Cyber Security Ordinance 2025 — corrected under audit and specific |
| **Bilingual discipline** | A Bengali counterpart requirement enforced as an approval gate (`CM-R6`), not an afterthought |
| **An SRS precedent** | The sibling portal programme wrote a full 91 KB SRS with API specifications in January 2026. The capability exists in-house; it was never applied to the ERP |

**The programme has done the hardest documentation work and not started the most standard
documentation work.** That is an unusual and recoverable position — specification depth cannot be
bought, but an SRS, a SAD and a schema can be produced quickly *because the requirements already
exist to derive them from*.

**The risk is not that these 138 documents are hard. It is that 601 files read as readiness, and
Wave 1 starts without them.**

---

## Relationship to the other repositories

| Repository | Files | Answers |
|---|---:|---|
| `../primary-doc/` | 4 | **Why** — BRD, RFP, URD, Technology Stack Specification |
| `../1000fix_ERP_Module/` | 123 | **What** — 67 modules, 12 portals, 6 cross-cutting specifications |
| `../project_content/` | **477** | **What must be written** — master data, copy, SOPs, legal, training, migration, tests |
| `../old-primary-doc/` | 6 | **History** — v1.0 baseline, Odoo 19 CE strategy, and the March 2026 missing-documents checklist |
| **`project-guide-doc/`** | **34** | **How it is engineered, delivered and governed** |
| **Workspace total** | **644** | **Of which 0 are under version control** — finding `PGD-A2-15` |

A `PGD` document **references** the other three; it never restates them. Where a `PGD` document and
a module specification disagree on *what the system does*, the module specification wins. Where they
disagree on *how it is built*, the `PGD` document wins.

---

## Status

| Item | State |
|---|---|
| Register | **Issued 2026-08-18, v1.1 — DRAFT FOR APPROVAL** |
| Folder structure | **Created** — 17 category folders, each with an overview |
| Authoring template | **Created and corrected** — `_templates/TPL_Guiding_Document.md`, decision-identifier collision closed (`PGD-A2-03`) |
| Mandatory audits | **`PGD-AUDIT-001` v1.1** — 13 findings, 11 closed, 2 open · **`PGD-AUDIT-002`** — 26 findings, 13 closed, 13 open · **`PGD-AUDIT-003`** · **`PGD-AUDIT-004`** — 34 findings, 13 closed, 21 open |
| Documents authored | **51 on disk** — Cat 00 (11), 01 (10), 02 (13), **03 (9)**, 04 (3), 05 (2), 06 (2), 07 (1) · **the register reflects 45**; Categories 04–07 are mid-authoring and their rows are not yet updated |
| Audit identifier space | **Clean** — `001`–`004`. A duplicate `PGD-AUDIT-002` was observed at 03:05 and resolved at ~03:10 (`RQA-34`, closed). `RR-002` is asked to re-base the sequential space to a category-keyed form, since sequential allocation is unsafe under concurrent authoring |
| Effort to produce them | ✅ **Sized** — `GV-007` §5.2: **264–528 PW**, estimate class 3. Closes `PGD-A1-05` work stream 1 |
| Screen-design effort (~660–1,500 screens) | ✅ **Sized** — `GV-007` §6.3: **95–325 PW**, estimate class 5. Closes `PGD-A1-05` work stream 2 |
| Programme effort, all four streams | **2,537–3,931 PW, expected 3,022** against 834 approved — **3.0×–4.7×** (`GV-007` §7) |
| Programme cost, restated | **$1.02M–$2.61M, expected $1.63M** against $455K–$780K held — **2.2×–3.3×** (`GV-008` §4.4) |
| Approval body | **Still does not exist** — finding `PGD-A1-09`, **OPEN**. `GV-001` and `GV-002` are now *written*; they must now be *approved* |
| Version control | **None. 644 files, zero versioned** — finding `PGD-A2-15`, **OPEN**, Critical |
| Independent assurance | **None. 29 audit reports, all class I0** — finding `PGD-A2-23`, **OPEN** |

**Nothing in this repository is authorised until the ERP Steering Committee is constituted
(`GV-002` §9.1) and approves the Programme Charter (`GV-001`).** That now includes the eleven
Category 00 documents themselves — see `PGD-A2-25`.

### The three decisions that unblock the most

| Decision | Subject | Owner | Blocks |
|---|---|---|---|
| `D-001` | Approve the scope, budget and horizon | Board | Everything. 610 files remain non-binding |
| `D-013` | Approve the split-residency data architecture | Board, on DP Forum recommendation | The entire data architecture. Longest lead on the critical path |
| `D-014` | Accept the restated effort and cost, or direct a descope | Board | The budget baseline and the implementation contract |

---

*1000FiX Services Limited · ERP Programme · Enterprise Architecture*
*586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh*
*Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
