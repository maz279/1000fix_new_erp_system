---
id: GV-011
title: Documentation Control & Configuration Management Plan
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Management Office — Configuration Librarian
approver: ERP Steering Committee
standards_basis: ISO 10007:2017 (all five processes) · ISO 9001:2015 §7.5 documented information · ISO/IEC/IEEE 12207:2017 §6.3.5 configuration management · ISO 21502:2020 §7.10 · PRINCE2 7th Edition (2023) digital and data management
traces_to: PGD-000 GV-011 · findings AF-01, AF-02, AF-03, AF-11, AF-12, AF-13, AF-18, H-06, C-03, H-03, H2-04, H2-05, PGD-A1-01, PGD-A1-11 · CG-005, CG-006
depends_on: GV-001, GV-002, GV-003
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-011 — Documentation Control & Configuration Management Plan
# 1000FiX ERP System & Portal Suite v2.0

### Category 00 · Code `GV` · ISO 10007:2017 · ISO 9001:2015 §7.5 · ISO/IEC/IEEE 12207:2017

---

> **610 documentation files. Zero under version control.**
>
> The workspace is not a git repository. There is no history, no diff, no attribution, no branch,
> no rollback and no merge. Every one of the 69 findings raised by the four repository audits was
> found by reading files, because there was no other way to find anything.
>
> **This is the root cause beneath a large share of the estate's defect population**, and it has
> never been raised as a finding by any audit — because an audit that reads files cannot see the
> absence of the thing that would have let it read changes.

---

## 1. Purpose

This plan establishes configuration management across the four repositories: what is under
control, how items are identified, how they are versioned and approved, how changes are recorded,
how the true state is reported, and how it is audited.

It exists because the estate has excellent *document* discipline and no *configuration* discipline.
Files are well written, consistently templated and carefully cross-referenced. They are also
unversioned, un-attributed, un-diffable, and described by three incompatible identifier schemes,
three incompatible status models and two incompatible priority scales.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The configuration management plan itself — ISO 10007 process 1 |
| 2 | **Configuration identification**: what is a configuration item, and how it is named |
| 3 | Identifier schemes across the four repositories, and their reconciliation |
| 4 | The status model, the version model and the approval authority per document class |
| 5 | **Change control** — by reference to `GV-003` |
| 6 | **Configuration status accounting**: the counted state of the estate |
| 7 | **Configuration audit**: functional and physical |
| 8 | Version control — the absence of it, and the remediation |
| 9 | Storage, naming, supersession and retention |
| 10 | Cross-repository precedence and link integrity |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The change **procedure** | `GV-003` §6 | ISO 10007 process 3. One procedure, referenced not duplicated |
| The identifier **convention standard** | `RR-002` | ⛔ **Does not exist.** This plan states the interim position and defers the standard. `R-01` and `R-08` both make `RR-002` urgent |
| Content lifecycle, versioning and pinning | `CG-005`, `CG-006` | Workstream 5 has already solved this well for content. **This plan adopts their model rather than competing with it** |
| Source code configuration management | `BE-003`, `BE-004` | Code CM and document CM share tooling but not scope |
| Environment and infrastructure configuration | `PE-009` | |
| Records retention as a statutory obligation | `LG-009`, `DA-006` | This plan covers retention of *programme* artefacts |

### 1.2 Intended audience

| Audience | What they use this plan for |
|---|---|
| **Configuration Librarian (PMO)** | The operating procedure. This plan's owner |
| **Every document author** | The naming, versioning, status and approval rules that apply to what they write |
| **Steering Committee** | The true state of the estate, reported rather than asserted |
| **Auditors** | The configuration audit method, and the baseline against which they audit |
| **Implementation vendor** | Which version of which document is contractually current |
| **Quality Manager** | ISO 9001:2015 §7.5 conformance evidence |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Process / clause | How this plan conforms | Departure |
|---|---|---|---|
| **ISO 10007:2017** | **All five processes**: (1) CM planning · (2) configuration identification · (3) change control · (4) configuration status accounting · (5) configuration audit | §3 planning · §4 identification · §6 change control *(by reference)* · §7 status accounting · §8 audit | ISO 10007 addresses product configuration. Applied here to the documentation estate, which the standard's scope explicitly permits — *"products, systems or services requiring configuration control"* |
| **ISO 9001:2015** §7.5 | Documented information: identification and description, format, review and approval, control of changes, version management, retention and disposition | §4 identification · §5 status, version and approval · §9 retention | **Mandatory** — the Company is certified and `CON-11` requires it maintained |
| **ISO/IEC/IEEE 12207:2017** §6.3.5 | Software configuration management process | §8 configuration audit; §10 version control | Applied to documents ahead of code, because documents exist and code does not |
| **ISO 21502:2020** §7.10 | Information and documentation management | §9 storage and retention | None |
| **PRINCE2 7th Edition (2023)** | Digital and data management; configuration item records; product status account | §7 status accounting is the *product status account* | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Content ID and Naming Convention | `../../project_content/00_Content_Governance_and_Standards/CG-005` | Content ID format, category codes, reserved prefixes, retirement log, folder naming, enforcement. **A working model, adopted here** |
| Content Lifecycle and Versioning Policy | `../../project_content/00_Content_Governance_and_Standards/CG-006` | Eight states, MAJOR/MINOR versioning with the "could a reader now act incorrectly?" test, release pinning, statutory pinning, freeze windows, archiving |
| Review, Approval and Sign-off Workflow | `../../project_content/00_Content_Governance_and_Standards/CG-007` | Six approval gates by content class |
| Folder Structure & Repository Map | `../FOLDER_STRUCTURE.md` | `PG-01`…`PG-08` principles, `PG-M1`…`PG-M11` maintenance rules, the five-point issue checklist |
| Master Index §3 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-01` | Fifteen identifier prefixes and the module short-code table |
| Content & Repository Integrity Audit | `../../project_content/_AUDIT/AUDIT-001` | `AF-01`, `AF-02`, `AF-03`, `AF-11`, `AF-12`, `AF-13`, `AF-16`, `AF-18` |
| **Direct filesystem enumeration** | Whole workspace | Every figure in §7, enumerated **2026-08-18 02:06 (+06)** |

### 2.3 Audit findings this document closes or addresses

| Finding | Source | Disposition |
|---|---|---|
| `AF-02`, `AF-03`, `AF-16` | `AUDIT-001` | §7 makes configuration status **accounted** rather than asserted. `RG-07` is adopted as `CM-09` |
| `AF-11` | `AUDIT-001` | §4.5 records the two priority scales and rules which applies where |
| `AF-12` | `AUDIT-001` | §9.2 naming rules; the offending folder is referred, not fixed (outside `PG-M8` authority) |
| `AF-13`, `AF-18` | `AUDIT-001` | §8.2 physical configuration audit compares declared names to disk. Both were found this way |
| `H-06`, `PGD-A1-11` | `00-06`, `PGD-AUDIT-001` | §8.3 link integrity is a standing configuration audit check, per `PG-M9` |
| `C-03`, `H-03`, `H2-04`, `H2-05`, `PGD-A1-01` | Four audits | §4.4 states the interim identifier position and defers to `RR-002`. **This plan does not solve identifier collisions; it makes them countable** |
| `AF-01` | `AUDIT-001` | §8.2 records it as an open physical-configuration nonconformity |
| **New — `PGD-A2-15`** | this document | **The workspace is not under version control.** §10 |
| **New — `PGD-A2-16`** | this document | **Fourteen active files carry navigation footers pointing at an abandoned filename scheme. 0 of 14 targets resolve.** §8.3 |
| **New — `PGD-A2-17`** | this document | **Three incompatible identifier schemes describe the same documents**, and the front-matter `id` space encodes the abandoned scheme. §4.3 |

---

## 3. Configuration Management Planning

### 3.1 What is under configuration management

| Class | Contents | Repository | Control level |
|:--:|---|---|---|
| **CI-A** | Programme governance artefacts: charter, governance, decisions, plan, RAID, scope, estimation, budget, gates, assurance, this plan | `project-guide-doc/00_*` | **Full** — versioned, approved, baselined, audited |
| **CI-B** | Engineering definition: SRS, SAD, SDD, schema, contracts, threat model, DPIA, test strategy, migration strategy, IaC, CI/CD | `project-guide-doc/01_*`…`15_*` | **Full** |
| **CI-C** | Module and portal specifications | `1000fix_ERP_Module/03_Modules`, `04_Portals*` | **Full** |
| **CI-D** | Cross-cutting specifications and registers | `1000fix_ERP_Module/02_*`, `05_*`, `06_*` | **Full** |
| **CI-E** | Content artefacts | `project_content/**` | **Full**, under `CG-005`/`CG-006` |
| **CI-F** | Primary documents: BRD, RFP, URD, Technology Stack | `primary-doc/` | **Full** — they are the top of the traceability chain |
| **CI-G** | Audit reports | `_AUDIT/` in each repository | **Full** — evidence, retained under `GA-08` |
| **CI-H** | Superseded artefacts | `_Superseded/`, `_ARCHIVE/` | **Retained, not maintained.** Never deleted (`LC-07`) |
| **CI-I** | Supporting artefacts: OpenAPI, DDL, IaC, diagram sources | `<ID>_artefacts/` subfolders | **Full** — **none exists yet; the estate contains zero non-markdown files** |
| **CI-J** | Gate evidence packs | `_AUDIT/` or a gate folder | **Full** — `GV-009` `GA-08` |

### 3.2 Roles

| Role | Accountability |
|---|---|
| **Configuration Librarian** *(PMO)* | Owns this plan; maintains the item register; performs status accounting; runs configuration audits. **The role is named in `GV-002` §4.6 and is currently vacant** — `GV-003` `Q-03` |
| Document owner | The accuracy and currency of their document |
| Approver | Per class, §5.4 |
| Programme Content Lead | `CI-E` under `CG-005`/`CG-006`, reporting configuration status to the Librarian |
| Enterprise Architecture | `RR-002` identifier standard; `RR-006` cross-reference index |

### 3.3 Principles adopted

Inherited from `FOLDER_STRUCTURE.md` §2 and `CG-005` §2, consolidated so that one set governs all
four repositories.

| Rule | Provision | Source |
|---|---|---|
| `CM-01` | **Register-first.** No artefact is authored before its register entry exists | `PG-01`, `RG-01` |
| `CM-02` | **One artefact, one purpose, one owner** | `PG-02` |
| `CM-03` | **Count, do not consult.** Every completeness figure is enumerated at the time of writing | `PG-03`, `RG-06` |
| `CM-04` | **Every folder has an overview.** No folder ships empty | `PG-04` |
| `CM-05` | **Identifiers are permanent.** A withdrawn artefact's ID is retired, never reissued | `PG-05`, `RG-02` |
| `CM-06` | **Standards are cited with an edition and a verification date** | `PG-06`, `PG-M4` |
| `CM-07` | **Status is evidence-based**, set by inspecting the filesystem | `PG-07` |
| `CM-08` | **No spaces or ampersands** in any folder or file name | `PG-08`, `AF-12` |
| `CM-09` | **Completeness figures are generated, not written**, and carry an enumeration **timestamp** | `RG-07`, `RG-08`, `PG-M11` |
| `CM-10` | **Links are verified before issue** | `PG-M9` |
| `CM-11` | **Roll-ups are regenerated from their rows before issue** | `PG-M10` |
| `CM-12` *(new)* | **Every artefact is under version control.** §10 | — |

---

## 4. Configuration Identification

### 4.1 The item register

Every configuration item carries: identifier · title · class · owner · approver · version · status ·
location · baseline · supersedes / superseded-by · last enumeration timestamp.

**The register does not exist as a single artefact.** It is currently distributed across `02-02`
(modules), `1000FiX_ERP_Content_Master_Index` (content), `PGD-000` (guiding documents) and nothing
at all (primary documents, audits). §7.4 records this as the principal status-accounting gap.

### 4.2 Naming

| Repository | Convention | Example |
|---|---|---|
| `project-guide-doc/` | `<CODE>-<nnn>_<Descriptive_Name>.md` | `GV-011_Documentation_Control_and_Configuration_Management_Plan.md` |
| `1000fix_ERP_Module/` | `<nn>-<nn>_<Name>.md` · `M<nn>_<Name>.md` · `P<nn>_<Name>.md` | `06-01_Implementation_Roadmap_and_Phasing.md` |
| `project_content/` | `<CODE>-<nnn>_<Name>.md` per `CG-005` §4 | `CG-006_Content_Lifecycle_and_Versioning_Policy.md` |
| `primary-doc/` | `1000FiX_ERP_<Document>.md` | `1000FiX_ERP_System_Comprehensive_BRD.md` |

| Reserved prefix | Meaning |
|---|---|
| `_` | Non-content: template, category overview, audit folder |
| `TPL_` | Authoring template |
| `SUPERSEDED_` | Retained for traceability; not authoritative |
| `DRAFT_` | Work in progress; not approved |
| `PGD-` | Guiding-document repository-level artefact |

### 4.3 Three identifier schemes for the same documents — `PGD-A2-17`

Enumerated 2026-08-18 02:06:

| Scheme | Where it lives | Example for one document |
|---|---|---|
| **File name** | The filesystem | `06-01_Implementation_Roadmap_and_Phasing.md` |
| **Front-matter `id`** | Inside the file | `FIX-ERP2-017` |
| **Footer navigation** | The footer of every active file | `17_Implementation_Roadmap_and_Phasing.md` |

The front-matter `id` space runs `FIX-ERP2-000` … `FIX-ERP2-022` — **sequential document numbers
from an abandoned `NN_Name.md` scheme**, not from the current `NN-NN` file names. `00-07` breaks
even that convention, using the path-based `FIX-ERP2-00-07`.

**Consequence.** A reader given "`FIX-ERP2-017`" cannot locate the file without a lookup table that
does not exist. A reader following a footer cannot resolve it at all — §8.3. And `RR-002`, the
document that would adjudicate all of this, is ⛔.

### 4.4 The interim identifier position

`RR-002` is the highest-leverage missing document in the estate: **five audits have found
identifier failures**, and `R-01` and `R-08` both make it the first thing to write. Until it
exists:

| Space | Allocating authority | Known state | Interim rule |
|---|---|---|---|
| `M<nn>`, `P<nn>` | `02-02` | Stable | `02-02` allocates |
| `FR-<MOD>-nnn` | `05-01` | ◐ **Denominator disputed** — 2,352 / 2,930 / 2,996 | No new allocation until `RQ-004` |
| `KPI-nnn` | `06-02` | ⛔ **22 collide across up to 9 modules each** | **No new allocation** until reconciled |
| `CD-nnn` | `02-05` → `BE-005` | ⛔ **48–70 collide** | **No build ticket may cite a `CD-` identifier** |
| `R01`–`R46` | `05-04` | ⛔ `R39`–`R46` unregistered; `R60` duplicates `R32` | Freeze; `SC-004` resolves |
| `SOD-01`–`SOD-30` | `05-04` | ⛔ 18 of 30 unregistered | Freeze |
| `NFR-nnn` | `05-06` | ⚠ `NFR-090/091/092` each used for two requirements | Freeze |
| `D-nnn` | **`GV-003`** ✅ | Clean, 24 allocated | Operating |
| `CR-nnn` | **`GV-003`** ✅ | Clean, 0 allocated | Operating |
| `RSK-`, `ASM-`, `ISS-`, `DEP-` | **`GV-005`** ✅ | Clean | Operating |
| `SB-n` | **`GV-006`** ✅ | Clean, 3 allocated | Operating |
| `<CODE>-<nnn>` guiding documents | **`PGD-000`** ✅ | Clean, 140 registered | Operating |
| Content `<CODE>-<nnn>` | `CG-005` ✅ | Clean; one registered collision (`DM`) documented | Operating |

> **Seven of fourteen identifier spaces are frozen or disputed.** The five that are clean are the
> five with a single named allocating authority and a register that is the authority. That is not a
> coincidence; it is the finding.

### 4.5 The two priority scales — `AF-11`

| Scale | Used by | Meaning of `P1` |
|---|---|---|
| **`P0`–`P3`** | ERP module estate; ERP content estate; **this repository** | `P1` = must-have, one level below blocking |
| `P1`–`P4` | Corporate website content set (a different programme) | `P1` = launch blocker |

> **Ruling `CM-13`.** Every artefact in the four ERP repositories uses **`P0`–`P3`**. The website
> scale is out of scope for this programme and is not reconciled — `AF-11` records that
> re-prioritising 431 complete website files would deliver no benefit. **Any document citing a
> priority across the programme boundary must name the scale.**

---

## 5. Status, Version and Approval

### 5.1 Three status models — reconciled

| Model | Values | Used by |
|---|---|---|
| **Binary** | `DRAFT FOR APPROVAL` · `ACTIVE` · `ISSUED` | Module estate, primary documents |
| **Lifecycle** *(`CG-006`)* | `Planned` · `Reserved` · `Draft` · `Review` · `Approved` · `Published` · `Superseded` · `Withdrawn` | Content estate |
| **Coverage** *(`PGD-000` §0.3)* | ✅ · ◐ · ⬜ · ⛔ · ⚠ · ➖ | Guiding-document register |

> **These are not competing — they answer different questions**, and stating that resolves what
> looks like an inconsistency:
>
> | Model | Question |
> |---|---|
> | Lifecycle | *Where is this file in its own production process?* |
> | Coverage | *Does a controlled artefact discharging this purpose exist?* |
> | Binary | *Has this been approved?* — a degenerate lifecycle |
>
> **Ruling `CM-14`.** The **`CG-006` lifecycle model is adopted programme-wide** as the per-file
> status. The `PGD-000` coverage model is retained as a **register-level** status and is explicitly
> **not** a file status. The binary model is retired: `DRAFT FOR APPROVAL` maps to `Draft`, `ACTIVE`
> and `ISSUED` map to `Published`.

### 5.2 Version numbering

Adopted unchanged from `CG-006` §2 — it is a good model and duplicating it with variations would
be the `AF-02` failure.

```
MAJOR . MINOR
```

| Part | Increment when | Effect |
|---|---|---|
| **MAJOR** | The meaning changes: a rule, a term, a statutory position, scope, or the structure | Re-review and re-approval. Every citing artefact reviewed |
| **MINOR** | The meaning does not change: typo, formatting, broken link, added example | Approver informed, not re-consulted |

**The MAJOR test** (`CG-006` §2.1): *if a reader who acted correctly on the previous version could
now act incorrectly, it is MAJOR.* **When in doubt, it is MAJOR.**

### 5.3 Pinning

`CG-006` §3 requires content that describes the system to carry a `pinned_to:` key naming the
surface, release, wave and verification date; and §4 requires statutory content to be pinned to its
instrument.

> **Ruling `CM-15`.** Pinning is extended to **`CI-B` engineering definition artefacts**. An SDD,
> an OpenAPI contract, a runbook or a schema specification describes a specific build; without a
> pin it silently describes a system that no longer exists. `AR-003`, `IN-002`, `DA-001`, `PE-004`
> and `SV-003` all require pins.

### 5.4 Approval authority by class

| Class | Approver | Basis |
|---|---|---|
| `CI-A` governance | **ERP Steering Committee**; Board for `GV-001` and `GV-008` | `GV-002` §5.2 rows 1, 7, 10 |
| `CI-B` engineering definition | **Architecture Review Board**, Steering Committee to baseline | `GV-002` §5.2 rows 10, 12 |
| `CI-C` module and portal specifications | Named business owner + ARB | `GV-002` §5.2 row 12 |
| `CI-D` cross-cutting | ARB | |
| `CI-E` content | Per content class A–E, `CG-002` §5 | CFO/Legal for statutory; Content Council for C, D, E |
| `CI-F` primary documents | Board | They are the commercial and business baseline |
| `CI-G` audits | **Audit Committee** | `GV-002` §5.2 row 29 |

> **Rule `CM-16` — an author may not approve their own artefact.** `CO-04` in `CG-002`; and the
> reason `GV-010` §3.2 exists.

---

## 6. Change Control

ISO 10007 process 3 is discharged by **`GV-003` §6** and is not restated. Two configuration-specific
additions:

| Rule | Provision |
|---|---|
| `CM-17` | A change to a **baselined** configuration item increments its version and updates the item register in the **same** change |
| `CM-18` | The **impact list** (`GV-003` §6.5) is produced from `RR-006`. **Until `RR-006` exists, impact lists are produced by search and are incomplete by construction** — `AF-14` is what that looks like after the fact |

---

## 7. Configuration Status Accounting

ISO 10007 process 4. The status account is the record of *what actually exists*, as opposed to what
the registers say exists — which is the distinction three audits were written about.

### 7.1 The estate, counted

Enumerated **2026-08-18 02:06 (+06)**. Rule `CM-03`, `CM-09`.

| Repository | Files | Under version control | Item register |
|---|---:|:--:|---|
| `primary-doc/` | 4 | ❌ | **None** |
| `old-primary-doc/` | 6 | ❌ | None |
| `1000fix_ERP_Module/` | 123 | ❌ | `02-02` (modules/portals only) |
| `project_content/` | **477** | ❌ | `1000FiX_ERP_Content_Master_Index` |
| `project-guide-doc/` | **34** | ❌ | `PGD-000` |
| **Total** | **644** | **0** | 3 partial |

### 7.2 Baseline movement — the third occurrence

| Enumeration | `project_content` | Estate excl. guide-doc |
|---|---:|---:|
| 2026-08-18 **01:16** | 462 | 595 |
| 2026-08-18 **01:39** | 468 | 601 |
| 2026-08-18 **02:06** | **477** | **610** |

Nine files were written between **01:53 and 02:06** while Category 00 was being authored:
`MM-005` … `MM-008` and `RF-003` … `RF-007`.

> **This is `AUDIT-016` `AP-17` and `PGD-A1-03` occurring a third time.** Proposed rule `RG-08` —
> enumeration carries a **timestamp**, not a date — has been pending ratification since August
> 2026. `CM-09` adopts it here; `GV-001` `CC-06` and `D-023` ratify it programme-wide.
>
> **A three-times-recurring defect is a control failure, not an authoring failure** — `GV-010`
> `AS-11`.

### 7.3 Guiding-document status account

| Status | Before | Category 00 change | **After** | Note |
|:--:|---:|---:|---:|---|
| ✅ Exists as a controlled artefact | 2 | **+11** | **13** | 2 outside this repository (`CO-001` RFP, `BM-001` `06-02`) + 11 Category 00 documents issued at this date |
| ◐ Partial | 60 | **−6** | **54** | `GV-001`, `GV-002`, `GV-004`, `GV-005`, `GV-009`, `GV-011` were ◐. No remaining ◐ may become ✅ until `RR-003` publishes the section sets (`PGD-A1-08`) |
| ⬜ Missing | 21 | **−2** | **19** | `GV-006`, `GV-010` were ⬜ |
| ⛔ Missing — blocking | 57 | **−3** | **54** | `GV-003`, `GV-007`, `GV-008` were ⛔ |
| **Total** | **140** | **0** | **140** | 13 + 54 + 19 + 54 = 140 ✓ |

**Verification** regenerated from the eleven `PGD-000` Category 00 rows per `CM-11`: the eleven
comprised 6 ◐, 2 ⬜ and 3 ⛔, which is the split `PGD-000` §0.5 records for category 00.

> **Recorded, not smoothed over.** The first draft of this table moved all eleven out of ⛔ (57 → 46)
> and left ◐ and ⬜ unchanged — treating "was blocking" as if it meant "was ⛔". The total still
> summed to 140, which is why the error survived the first check. Caught by regenerating from the
> source rows rather than reconciling the total. Logged as `PGD-A2-24`; it is the second instance in
> this category of a correct total concealing wrong components (`PGD-A2-13` was the first).

> **A note on ✅.** `PGD-000` §0.3 requires four things for ✅, the fourth being *"a named owner and
> an approval record."* These eleven documents have named owners and **no approval record**, because
> no constituted body can approve anything (`PGD-A1-09`). Under a strict reading, no document in the
> estate can be ✅ until `GV-001` `CC-01` completes. Raised as `PGD-A2-25`.

### 7.4 The status-accounting gaps

| Gap | Consequence |
|---|---|
| **No single configuration item register** | Status must be assembled from three partial registers plus the filesystem |
| **`primary-doc/` has no register at all** | 1.26 MB at the top of the traceability chain, uncontrolled, never audited (`GV-010` §8.1) |
| **No version history anywhere** | "What changed, when, by whom" is unanswerable for all 644 files |
| **`RR-006` cross-reference index absent** | Impact analysis is manual and incomplete |
| **Front-matter schemas differ across repositories** | Machine-readable status accounting is impossible |

---

## 8. Configuration Audit

ISO 10007 process 5. Two audits, run at every wave gate under `PG-M7`.

### 8.1 Functional configuration audit

*Does the artefact do what its register row says it does?*

| # | Check | Method |
|---|---|---|
| 1 | Every registered artefact exists at its stated path | `test -f` per row |
| 2 | Every artefact on disk has a register row | Filesystem enumeration vs register — **this is the check that would have caught `C-02`, `H2-01` and `AF-03`** |
| 3 | Front matter is complete per the schema | Field presence check |
| 4 | Status in front matter matches status in the register | Two-way diff |
| 5 | Every completeness figure carries an enumeration timestamp | `CM-09` |
| 6 | Every statutory or standards citation carries `verified_on` | `CM-06` |

### 8.2 Physical configuration audit

*Is the artefact where and what it is declared to be?*

| # | Check | Current result |
|---|---|---|
| 1 | Declared file names match disk | ⚠ `AF-13`, `AF-18` — **found this way**; fixed |
| 2 | Declared folder placement matches disk | ❌ **`AF-01` OPEN** — 12 portal specifications, 771 KB, in `03_Modules/K_…/` instead of `04_Portals_and_Applications/` |
| 3 | Folder names conform to `CM-08` | ❌ **`AF-12` OPEN** — one folder with a space and an ampersand |
| 4 | No empty folders | ⚠ 4 empty directories; 1 unowned (`audit_analysis/`) |
| 5 | Superseded artefacts carry a `SUPERSEDED_` prefix and a supersession note | ⚠ `L-03` — five superseded files lack the note |

### 8.3 Link integrity audit — `PGD-A2-16`

`PG-M9` requires every relative link to resolve before issue. Applying it to the module estate at
2026-08-18 02:06 produced a defect no audit has previously reported.

**Fourteen active files carry a `Next document:` or `Return to` footer. Every one of them points at
a filename from the abandoned `NN_Name.md` scheme. Zero of fourteen resolve.**

| File | Footer points at | Resolves? |
|---|---|:--:|
| `00-02` | `02_Scope_Expansion_Delta_v1_to_v2.md` | ❌ |
| `00-03` | `03_ERP_Module_Architecture_and_System_Map.md` | ❌ |
| `00-04` | `00_MASTER_INDEX_and_Document_Map.md` | ❌ |
| `02-01` | `04_Module_Catalog_Master_Register.md` | ❌ |
| `02-05` | `20_Risks_Assumptions_Dependencies_and_Governance.md` | ❌ |
| `04-00` | `11_Feature_and_Function_Register.md` | ❌ |
| `05-01` | `12_Data_Model_and_Entity_Catalog.md` | ❌ |
| `05-02` | `13_Integration_and_API_Catalog.md` | ❌ |
| `05-03` | `14_Role_Permission_and_Access_Matrix.md` | ❌ |
| `05-04` | `15_Business_Rules_and_Automation_Catalog.md` | ❌ |
| `05-05` | `16_NonFunctional_Requirements_and_Architecture_Standards.md` | ❌ |
| `05-06` | `17_Implementation_Roadmap_and_Phasing.md` | ❌ |
| `06-01` | `18_KPI_Benefits_and_Acceptance_Criteria.md` | ❌ |
| `06-02` | `19_Technology_Stack_and_Build_vs_Buy_Decisions.md` | ❌ |
| **Total** | | **0 of 14** |

*(Five further instances exist in `99_Reference/_Superseded/`, which are legitimately historical and
are excluded.)*

> **Why no audit found this.** Every audit checked links of the form `](path)`. These are inline
> code spans in a footer — they look like prose, not navigation. `H-06` found five broken links in
> the README by checking markdown link syntax; this is the same defect class, three times larger,
> in a form the check did not cover.
>
> Three of them also mis-spell the target's own name — `Catalog` for `Catalogue`, and
> `..._and_Architecture_Standards` for `..._and_Standards` — so they would not resolve even under
> the old scheme. **Remediation: the footers are a legacy of the abandoned scheme and should be
> rewritten to the current file names, or removed.** ~30 minutes.

### 8.4 Nonconformity register

| # | Nonconformity | Class | Severity | Owner | Status |
|---|---|:--:|:--:|---|---|
| `NC-01` | 12 portal specifications misfiled (`AF-01`) | Physical | **Critical** | CTO | **Open** — needs `PG-M8` approval |
| `NC-02` | 14 unresolvable navigation footers (`PGD-A2-16`) | Link | High | Enterprise Architecture | **Open — new** |
| `NC-03` | Three identifier schemes for the same documents (`PGD-A2-17`) | Identification | High | Enterprise Architecture | **Open — new**; `RR-002` |
| `NC-04` | 644 files, zero under version control (`PGD-A2-15`) | Planning | **Critical** | CTO | **Open — new** |
| `NC-05` | Seven of fourteen identifier spaces frozen or disputed | Identification | **Critical** | Enterprise Architecture | Open; `RR-002`, `BE-005` |
| `NC-06` | Folder name with space and ampersand (`AF-12`) | Naming | Low | Content Lead | Open — referred |
| `NC-07` | Five superseded files lack a supersession note (`L-03`) | Identification | Low | Enterprise Architecture | Open |
| `NC-08` | `primary-doc/` has no item register and has never been audited | Accounting | High | PMO | **Open — new** |
| `NC-09` | `audit_analysis/` unowned in the workspace root | Physical | Low | PMO | Open — referred |
| `NC-10` | Baseline movement during authoring, third occurrence | Accounting | High | PMO | Open; `D-023` |

**Ten nonconformities — 3 Critical, 4 High, 3 Low.** Counted from the rows above per `CM-11`.

---

## 9. Storage, Retention and Supersession

### 9.1 Storage

| Rule | Provision |
|---|---|
| `CM-19` | Artefacts live in the repository their class assigns (§3.1). Cross-repository copies are forbidden — a copy is a divergence with a delay fuse |
| `CM-20` | Supporting artefacts sit in a subfolder sharing the document's ID stem: `IN-002_artefacts/openapi-service-order-v1.yaml` |
| `CM-21` | Superseded artefacts move to `_ARCHIVE/` or `_Superseded/` with a `SUPERSEDED_` prefix and a header note naming the replacement (`LC-07`) |
| `CM-22` | **Nothing is deleted.** Retirement is a status change plus a move |

### 9.2 Naming enforcement

| Rule | Provision |
|---|---|
| `CM-08` | No spaces, no ampersands, in any folder or file name |
| `CM-23` | Descriptive parts use `Title_Case_With_Underscores` |
| `CM-24` | A file name is never changed without changing every citation in the same change. `AF-13` and `AF-18` were resolved by correcting the *map* rather than the file, which was the right call because the file name was cited |

### 9.3 Retention

| Class | Retention | Basis |
|---|---|---|
| `CI-A` governance, `CI-G` audits | Programme life + **5 years minimum** | PDPA 2026 records-retention minimum; ISO 9001 evidence |
| `CI-B`, `CI-C`, `CI-D` | Programme life + system life | They describe an operating system |
| `CI-E` content | Per `CG-006` §4.3 |  |
| `CI-F` primary documents | Permanent | Commercial and contractual baseline |
| `CI-J` gate evidence | Programme life + 5 years | `GV-009` `GA-08` |

### 9.4 Cross-repository precedence

> Carried from `FOLDER_STRUCTURE.md` §9 and made a configuration rule.
>
> Where a `PGD` document and a module specification disagree on **what the system does**, the
> module specification wins. Where they disagree on **how it is built, delivered or governed**, the
> `PGD` document wins.
>
> **Extension `CM-25`.** Where they disagree on a **counted figure**, the more recent enumeration
> wins, and the older figure is corrected at source rather than left in place. Leaving both is how
> the estate acquired three effort figures and four requirement counts.

---

## 10. Version Control — `PGD-A2-15`

### 10.1 The finding

**The workspace is not a version-controlled repository.** Verified directly: no `.git` directory
exists at any level of `F:\sofrware_project_5\1000 fix\`.

| What is unavailable | Consequence |
|---|---|
| History | *"What did this document say last week?"* is unanswerable for 644 files |
| Attribution | *"Who changed this, and why?"* is unanswerable |
| Diff | Every audit had to read whole files. `AF-02` — a 48-point contradiction between two documents — required a human to notice it |
| Branch and merge | Concurrent authoring produces the baseline movement in §7.2, three times over |
| Rollback | A bad edit is permanent |
| Tags | There is no way to say "the version the vendor quoted against" |
| Automated checks | `PG-M9` link verification, `PG-M10` roll-up regeneration and `CM-09` timestamping are all **manual**, and all three have failed at least once |

> **This is the root cause beneath a large share of the estate's defect population.** Of the five
> recurring defect classes in `GV-010` §6.4, **four would be caught by a pre-commit hook**:
> stale roll-ups, registers denying work that exists, baseline movement during authoring, and
> broken links. Not prevented by care — *caught mechanically*, which is what `PGD-A1-13` concluded
> the controls must be.

### 10.2 Remediation

| # | Action | Owner | By |
|---|---|---|---|
| 1 | Initialise a git repository at the workspace root; commit the current state as the baseline | CTO | **Week 1** |
| 2 | Tag the baseline `estate-2026-08-18` so every audit finding to date has a fixed reference | PMO | Week 1 |
| 3 | Adopt a branch model for document authoring — `BE-003` defines it for code; extend it | Enterprise Architecture | Week 2 |
| 4 | Implement pre-commit checks: link resolution (`CM-10`), front-matter schema, enumeration timestamp presence (`CM-09`) | Platform Engineering | Week 4 |
| 5 | Implement a CI check that regenerates every roll-up table and fails on mismatch (`CM-11`) | Platform Engineering | Week 6 |
| 6 | Generate the consolidated item register from front matter | Configuration Librarian | Week 6 |

> **Step 4 alone would have prevented `H-06`, `PGD-A1-11` and `PGD-A2-16` — 20 broken references
> across three repositories.** Step 5 would have prevented `PGD-A1-02`, `PGD-A1-07`, `PGD-A1-13`,
> `AF-02`, `AF-16`, `H2-01` and the `00-04` §1.5 error corrected in `GV-005` — **seven arithmetic
> findings, two of them critical.**

### 10.3 What version control does not fix

Stated so it is not oversold: it will not fix identifier collisions (`RR-002`), a missing decision
log (`GV-003`), an unvalidated capacity plan (`GV-004`) or an absent design specification. It fixes
*integrity of the record*, which is a precondition for the rest, not a substitute for it.

---

## 11. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-011-D-01` | Whether to define a new lifecycle model | Define new · Adopt `CG-006` | **Adopt `CG-006`** | It is a good model already in force over 477 files. A second model would be the `AF-02` failure | `CM-14`; the binary model is retired |
| `GV-011-D-02` | Whether to reconcile the three status models | Force one · Explain the three · Adopt one for files, one for the register | **Adopt one for files, retain one for the register** | They answer different questions. Forcing one would lose the coverage semantics `PGD-000` needs | `CM-14` |
| `GV-011-D-03` | Whether to solve identifier collisions here | Solve · State the interim and defer to `RR-002` | **Defer, with an interim freeze** | `RR-002` is the allocating authority. Solving it here would create a second authority | §4.4; seven spaces frozen |
| `GV-011-D-04` | Whether to raise version control as a finding | Out of scope · Raise it | **Raise it** | It is the root cause beneath four of the five recurring defect classes, and no audit has raised it | `PGD-A2-15`; `NC-04`; §10 |
| `GV-011-D-05` | Whether to check footer navigation | Check markdown links only, as prior audits did · Check all references | **Check all references** | Prior audits checked `](path)` syntax and found 5 broken links. Checking inline code spans found 14 more | `PGD-A2-16`; `NC-02` |
| `GV-011-D-06` | Whether to extend pinning to engineering artefacts | Content only · Extend | **Extend (`CM-15`)** | An SDD or an OpenAPI contract without a pin silently describes a system that no longer exists — the same failure `CG-006` §3 was written to prevent for content | `AR-003`, `IN-002`, `DA-001`, `PE-004`, `SV-003` carry pins |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Who is the Configuration Librarian? The role is named in `GV-002` §4.6 and is vacant | Programme Director | **Week 2** | This entire plan |
| `Q-02` | Is there an approved hosting location for a git remote, given `CON-13` data residency? The estate is `CONFIDENTIAL` | CTO | Week 2 | §10.2 step 1 |
| `Q-03` | Should `primary-doc/` come under this plan, or does it belong to a commercial baseline outside the programme? | CFO + CTO | Week 4 | `NC-08` |
| `Q-04` | Do the 5 superseded pillar files still have citations pointing at them? If so they cannot be archived | Enterprise Architecture | Week 4 | `NC-07` |
| `Q-05` | Should the front-matter `id` space (`FIX-ERP2-nnn`) be retired or re-mapped? Retiring breaks nothing visible; re-mapping breaks `RG-02` | Enterprise Architecture | Week 4 | `NC-03`; `RR-002` |
| `Q-06` | Who fixes the 14 navigation footers, given `PG-M8` reserves structural change to the CTO? Footers are content, not structure — but the ruling is not written | Enterprise Architecture | Week 2 | `NC-02` |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | All five ISO 10007 processes are addressed | §3, §4, §6, §7, §8 |
| `AC-02` | Configuration item classes are defined with a control level | §3.1 — ten classes |
| `AC-03` | Every identifier space has a named allocating authority and a stated state | §4.4 — fourteen spaces |
| `AC-04` | The three status models are reconciled with a ruling | §5.1; `CM-14` |
| `AC-05` | The status account is counted, not asserted, with a timestamp | §7.1, §7.3 — 2026-08-18 02:06 (+06) |
| `AC-06` | Both configuration audits are defined and the current result is stated | §8.1, §8.2 |
| `AC-07` | Link integrity is verified, not assumed | §8.3 — 0 of 14 resolve |
| `AC-08` | Nonconformities are registered with severity and owner | §8.4 — 10 |
| `AC-09` | The absence of version control is stated as a finding with remediation | §10; `PGD-A2-15` |
| `AC-10` | The plan adopts existing good practice rather than competing with it | `GV-011-D-01`; `CG-005`, `CG-006`, `CG-007` adopted |

**Definition of done.** Complete when every criterion is met, a Configuration Librarian is
appointed, the workspace is under version control with pre-commit checks operating, the ten
nonconformities in §8.4 are closed or accepted, `RR-002` has unfrozen the seven identifier spaces,
and `PGD-000` records `GV-011` as ✅ with a fresh enumeration timestamp.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-002`](GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) §4.6 | Constitutes the Configuration Librarian |
| Upstream | [`GV-003`](GV-003_Decision_Log_and_Change_Control_Procedure.md) §6 | ISO 10007 process 3, referenced not duplicated |
| Downstream | `RR-002` | The identifier convention standard this plan defers to |
| Downstream | `RR-003` | Document standards and template library; the section sets `PGD-A1-08` needs |
| Downstream | `RR-006` | Cross-reference index; makes impact lists complete (`CM-18`) |
| Downstream | `BE-003`, `BE-004` | Git workflow and repository structure; §10.2 steps 3–5 |
| Downstream | [`GV-009`](GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) `SG-8` | Configuration control is a standing gate criterion |
| Downstream | [`GV-010`](GV-010_Programme_Assurance_and_Independent_Review_Plan.md) §4.1 A6 | Configuration audit is an assurance type |
| Lateral | `../../project_content/00_Content_Governance_and_Standards/CG-005`, `CG-006`, `CG-007` | **Adopted**, not superseded |
| Lateral | `../FOLDER_STRUCTURE.md` | `PG-01`…`PG-08`, `PG-M1`…`PG-M11`, consolidated at §3.3 |

---

## 15. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`FOLDER_STRUCTURE.md`](../FOLDER_STRUCTURE.md) ·
[`PGD-AUDIT-001`](../_AUDIT/PGD-AUDIT-001_Register_Integrity_Audit.md) ·
[`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) ·
[`_templates/TPL_Guiding_Document.md`](../_templates/TPL_Guiding_Document.md)

**Workspace**
`../../project_content/00_Content_Governance_and_Standards/CG-005`, `CG-006`, `CG-007` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-01` §3 ·
`../../project_content/_AUDIT/AUDIT-001` — `AF-01`, `AF-02`, `AF-03`, `AF-11`, `AF-12`, `AF-13`, `AF-16`, `AF-18`

**External standards** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| ISO 10007:2017 — CM planning, configuration identification, change control, status accounting, configuration audit; supports ISO 9001:2015 §8.5.2 identification and traceability | §3–§8 |
| ISO 9001:2015 §7.5 — documented information: identification, format, review and approval, change control, version management, retention | §4, §5, §9 |
| ISO/IEC/IEEE 12207:2017 §6.3.5 — software configuration management | §8, §10 |
| ISO 21502:2020 §7.10 — information and documentation management | §9 |
| PRINCE2 7th Edition (2023) — digital and data management; configuration item records; product status account | §7 |
| Bangladesh PDPA 2026 — records retention minimum 5 years | §9.3 |

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Programme Management Office | Initial issue. Establishes all five ISO 10007 processes across four repositories. Adopts `CG-006` lifecycle and versioning programme-wide (`CM-14`). Reconciles three status models and records two priority scales. Freezes seven of fourteen identifier spaces pending `RR-002`. Raises three new findings: **`PGD-A2-15`** — 644 files, zero under version control; **`PGD-A2-16`** — 14 navigation footers, 0 of 14 resolve; **`PGD-A2-17`** — three identifier schemes for the same documents. Registers 10 nonconformities | *pending Steering Committee* |

---

*`GV-011` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
