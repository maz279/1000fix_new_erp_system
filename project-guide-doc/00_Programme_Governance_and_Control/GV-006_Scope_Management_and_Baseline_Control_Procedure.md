---
id: GV-006
title: Scope Management & Baseline Control Procedure
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Management Office
approver: ERP Steering Committee
standards_basis: ISO 10007:2017 §5.2 configuration identification · ISO 21502:2020 §7.4 scope · PMBOK Guide 7th Edition · PRINCE2 7th Edition (2023) product-based planning
traces_to: PGD-000 GV-006 · RSK-002 (scope creep, Critical) · 00-03 scope expansion delta · GV-003 §7.2 empty change log
depends_on: GV-001, GV-002, GV-003
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-006 — Scope Management & Baseline Control Procedure
# 1000FiX ERP System & Portal Suite v2.0

### Category 00 · Code `GV` · ISO 10007:2017 · ISO 21502:2020 · PRINCE2 7

---

> **Scope has moved 11 → 30 → 67 modules and 6 → 12 portals with no change-control artefact of any
> kind.** `RSK-002` (scope creep) is rated **Critical** and its stated mitigation is *"formal change
> control"*. `GV-003` §7.2 records that the change log is **empty**.
>
> This document does two things: it establishes the procedure, and it **retrospectively baselines
> the three scope positions that already exist** — so that the fourth expansion, whenever it comes,
> can be distinguished from creep. Today it cannot be.

---

## 1. Purpose

This document defines what the programme has agreed to deliver, how that agreement is recorded as
a baseline, and how the baseline is changed.

A scope baseline is not a list. It is a **frozen, versioned, approved statement** against which
variance can be measured. The 1000FiX programme has had three scope positions and no baseline, so
its scope variance is not merely unmeasured — it is unmeasurable. That is the condition this
document ends.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The definition of a scope baseline and its components |
| 2 | **Retrospective baselining of `SB-1`, `SB-2` and `SB-3`** — the three positions the programme has occupied |
| 3 | The measured movement between them, and what it cost |
| 4 | The current baseline `SB-3` and its known gaps |
| 5 | Scope decomposition rules and the boundary between scope, requirement and design |
| 6 | The scope change procedure and its interface with `GV-003` |
| 7 | The wave-lock rule, the parking lot, and the treatment of good ideas |
| 8 | The descope hierarchy and the items that may never be descoped |
| 9 | Gold-plating control and scope-creep measurement |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The change **procedure** — raise, assess, classify, decide, apply, verify | `GV-003` §6 | One procedure for all baselines. This document defines the *scope* baseline; `GV-003` changes any baseline |
| Requirements themselves | `RQ-001` SRS | A scope item is a capability; a requirement is a testable statement about it. Conflating them is how a scope baseline becomes 2,996 rows nobody can approve |
| The schedule consequence of scope | `GV-004` | Scope and schedule are separate baselines so that a scope change is visibly a schedule change |
| The cost consequence of scope | `GV-007`, `GV-008` | Same reason |
| Module boundary adjudication — which module owns a contested capability | `AR-005` | A boundary dispute is an architecture question. **`AR-005` does not exist**; see §5.4 |
| Configuration item identification and versioning | `GV-011` | Configuration management is the wider discipline |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Steering Committee** | The baseline they approve, and the variance report they receive |
| **Board** | The measured history of scope movement — evidence for `D-014` |
| **PMO** | The operating procedure and the variance measurement |
| **Business owners** | What is in their category's scope, and how to get something added |
| **Implementation vendor** | The contractual scope. **A capability not in `SB-3` is not in the contract** |
| **Auditors** | Whether the estate's scope claims match its scope baseline |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure |
|---|---|---|---|
| **ISO 10007:2017** §5.2 | Configuration identification: selecting configuration items, establishing baselines, documenting the configuration | §3 defines the baseline components; §4 establishes three baselines with identifiers and dates | ISO 10007 addresses product configuration; scope baselines are treated as configuration baselines, which the standard's §5.2 supports |
| **ISO 21502:2020** §7.4 | Scope: definition, control, and the relationship to requirements | §5 decomposition; §6 change control | None |
| **PMBOK Guide 7th Edition** | Scope baseline = scope statement + WBS + WBS dictionary; *Delivery* performance domain | §3.2; the WBS lives in `GV-004` §3 and is referenced | None |
| **PRINCE2 7th Edition (2023)** | Product-based planning; Project Product Description; tolerance on scope | §5.2 uses module and portal specifications as product descriptions — they already serve this purpose | PRINCE2's Product Breakdown Structure is realised as the `GV-004` §3 WBS rather than duplicated |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Scope Expansion Delta v1→v2 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-03` | The line-by-line 11 → 30 delta with an evidence trail, and what was considered and rejected |
| Executive Summary & Scope Charter | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-02` | The 30 → 67 restatement; the out-of-scope list; the guiding principles |
| Module Catalogue Master Register | `../../1000fix_ERP_Module/02_Architecture/02-02` | The authoritative module register — *"where any other document disagrees… this document wins"* |
| Comprehensive RFP | `../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` | The 405-requirement register — the v1.0 contractual scope |
| Implementation Roadmap | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` | Wave allocation; contingency; what cannot be descoped |
| Documentation Audit | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-06` | `C-01` — the repository describes two architectures |
| **Direct enumeration** | Whole estate | 67 module files, 12 portal files, 2,996 distinct `FR-` identifiers, 1,842 PW — 2026-08-18 02:06 (+06) |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `RSK-002` treatment | `00-04` §1.1 | §6 supplies the "formal change control" the mitigation names; §7 supplies the measurement that makes creep detectable |
| `C-01` *(scope half)* | `00-06` | §4.4 declares `SB-3` (67 modules) authoritative and records the superseded positions with their identifiers, so that "two architectures" becomes "one baseline and two superseded baselines" |
| `GV-003` §7.2 empty change log | this category | §4 retrospectively baselines the three positions, giving the change log a starting point |
| **New — `PGD-A2-08`** | this document | `02-02` declares itself authoritative on *"module identity, ownership, priority or wave"*, and `00-06` `C-01` records that `02-02` was itself written against the superseded 30-module architecture. The authority claim and the content contradict each other. §4.4 resolves it |

---

## 3. What a Scope Baseline Is

### 3.1 Components

| Component | Content | Where it lives |
|---|---|---|
| **Scope statement** | The capability boundary: what is in, what is explicitly out, and why | `GV-001` §6.1, §6.2 |
| **Product register** | The enumerated set of modules, portals, applications and content classes | `02-02` (modules/portals) · `1000FiX_ERP_Content_Master_Index` (content) |
| **Work breakdown structure** | Deliverable decomposition to level 3 | `GV-004` §3.2 |
| **WBS dictionary** | Per element: owner, squad, effort, acceptance | Module and portal specifications §17 |
| **Exclusions** | The ten `OOS-nn` items | `GV-001` §6.2 |
| **Acceptance basis** | How completion is judged | `RQ-010`, `GV-009` |

### 3.2 Baseline rules

| Rule | Provision |
|---|---|
| `SB-01` | A baseline is **approved, dated, versioned and frozen**. An unapproved list is not a baseline |
| `SB-02` | A baseline is changed only by an approved change request (`GV-003` §6) |
| `SB-03` | Baselines are **never deleted**. A superseded baseline is retained with its identifier and its supersession record |
| `SB-04` | Variance is measured **against the current baseline**, never against the previous position |
| `SB-05` | A capability not in the current baseline is **not in the contract, not in the plan, and not in the budget** |
| `SB-06` | The baseline identifier appears in every gate report, every vendor deliverable and every contractual variation |

---

## 4. The Scope Baselines

### 4.1 Why these are being created retrospectively

The programme has occupied three distinct scope positions. None was baselined. `00-03` documents
the first transition well — with an evidence trail per module — but as a *narrative of a decision
already taken*, not as a controlled change from one baseline to another.

Retrospective baselining does not legitimise the changes. It makes them **measurable**, which is
the precondition for `RSK-002` having any treatment at all.

### 4.2 `SB-1` — v1.0 Approved Scope

| Attribute | Value |
|---|---|
| **Identifier** | `SB-1` |
| **Version** | 1.0 |
| **Approved** | March 2026 — the approval on which the programme was authorised |
| **Status** | **SUPERSEDED** by `SB-2` |
| **Scope** | 11 ERP modules · 6 portals · ~405 requirements (RFP register) · 20 custom development items · 20 user roles · 15 integrations · 5 revenue streams |
| **Delivery** | 18 months, 6 phases |
| **Effort** | Not stated |
| **Cost** | $182K – $342K, 3-year TCO |
| **Evidence** | `primary-doc/…RFP.md` §requirement register · `old-primary-doc/` v1.0 set |

### 4.3 `SB-2` — v2.0 Proposed Expanded Scope

| Attribute | Value |
|---|---|
| **Identifier** | `SB-2` |
| **Version** | 2.0 |
| **Proposed** | 2026-08-12 (`00-02`) |
| **Status** | **SUPERSEDED** by `SB-3`. **Never formally approved** — `D-001` remains `OPEN` |
| **Scope** | 30 ERP modules · 12 portals · ~1,180 requirements · ~138 CD items · 38 roles · 47 integrations · **14 revenue streams** |
| **Delivery** | 36 months, 9 waves |
| **Effort** | 834 PW |
| **Cost** | $455K – $780K, 3-year TCO |
| **Evidence** | `00-02` §2, §5 · `00-03` full delta with per-module evidence trail |
| **Rationale** | Nine revenue streams already committed on paper had no system of record. `00-02` §1: *"they are not new business ideas; they are existing commitments without a system"* |

> **`SB-2` is the position the Board still holds.** The $455K–$780K figure, the 834 PW effort and
> the 18-month v1.0 commitment date all belong to this baseline. `D-001` and `D-014` are the
> decisions that would move the Board to `SB-3`.

### 4.4 `SB-3` — v2.1 Current Scope *(authoritative)*

| Attribute | Value |
|---|---|
| **Identifier** | `SB-3` |
| **Version** | 2.1 |
| **Established** | 2026-08-13, on completion of the 67-module specification set |
| **Status** | **CURRENT — pending formal approval.** Approved by nobody; `PGD-A1-09` |
| **Scope** | **67 ERP modules** in 11 categories · **12 portals and applications** · **2,996** distinct `FR-` identifiers *(counted; denominator disputed — `AF-06`)* · 14 revenue streams · 48 legacy sources to migrate · **477 content files** |
| **Delivery** | 36 months, 9 waves — **unchanged from `SB-2`** |
| **Effort** | **1,842 PW counted** (1,544 modules + 298 portals) + 520–775 PW content + two unestimated streams |
| **Cost** | **Contested.** See `GV-008` |
| **Evidence** | Direct enumeration 2026-08-18 02:06 (+06) · `02-02` · `00-07` H2-01 |

**Known gaps in `SB-3`:**

| Gap | Consequence |
|---|---|
| **37 modules (`M31`–`M67`) have no wave** | 763 PW unscheduled — `RSK-038` |
| **1,816 requirements have no wave** | The wave plan schedules `SB-2`'s requirement set — `PGD-A2-04` |
| `02-02` declares itself authoritative but was written against `SB-2` | Resolved below |
| The content estate is in `SB-3` scope but in no wave and no budget | `AF-09` |
| The 127 unwritten guiding documents are in no baseline at all | `PGD-A1-05` |

> **Resolution of the `02-02` authority contradiction (`PGD-A2-08`).** `02-02` states: *"where any
> other document disagrees with this one on module identity, ownership, priority or wave, this
> document wins."* `00-06` `C-01` records that `02-02` was one of the documents describing the
> superseded 30-module architecture, and `00-07` H2-01 records that it was subsequently corrected
> to counted 67-module figures.
>
> **`SB-3` therefore adopts `02-02` as authoritative on module identity, ownership and priority —
> and explicitly NOT on wave.** Wave allocation is held by `GV-004`, because `02-02` inherits
> `06-01`'s allocation, which covers only `M01`–`M30` and uses identifiers whose meaning changed
> (`PGD-A2-05`, `D-019`).

### 4.5 Measured scope movement

Counted from the three baselines above, per `PG-M10`.

| Dimension | `SB-1` | `SB-2` | `SB-3` | `SB-1`→`SB-3` |
|---|---:|---:|---:|---:|
| ERP modules | 11 | 30 | **67** | **+509%** |
| Portals and applications | 6 | 12 | 12 | +100% |
| Requirements | ~405 | ~1,180 | **2,996** | **+640%** |
| Revenue streams | 5 | 14 | 14 | +180% |
| User roles | 20 | 38 | 46+ *(`R39`–`R46` unregistered)* | +130% |
| Integrations | 15 | 47 | 47+ | +213% |
| Custom development items | 20 | ~138 | **unresolved — 48 collide** | — |
| Build effort | not stated | 834 PW | **1,842 PW** | **+121% vs `SB-2`** |
| Content files | 0 | 0 | **477** | new |
| Delivery horizon | 18 months | 36 months | 36 months | +100% |
| 3-year TCO | $182K–342K | $455K–780K | **contested** | — |

> **The single most important line is the last row of effort.** `SB-3` more than doubles `SB-2`'s
> effort **while holding `SB-2`'s 36-month horizon and `SB-2`'s team model unchanged.** That is
> precisely what `GV-004` §5 measures and reports as infeasible. Scope moved; the plan did not.

### 4.6 Baseline register

| ID | Version | Established | Status | Superseded by | Approved by |
|---|---|---|---|---|---|
| `SB-1` | 1.0 | 2026-03 | Superseded | `SB-2` | Board *(the original authorisation)* |
| `SB-2` | 2.0 | 2026-08-12 | Superseded | `SB-3` | **Nobody** — `D-001` open |
| `SB-3` | 2.1 | 2026-08-13 | **Current** | — | **Nobody** — `PGD-A1-09` |

**Three baselines. One approval, and it was for the position two baselines ago.**

---

## 5. Scope Decomposition

### 5.1 The three altitudes

| Altitude | Artefact | Question it answers | Baseline |
|---|---|---|---|
| **Capability** | `GV-001` §6.1; `02-02` module register | *What business capability does the system provide?* | `SB-3` — this document |
| **Requirement** | `RQ-001` SRS; `FR-<MOD>-nnn` | *What shall the system do, testably?* | Requirements baseline — `RQ-001` |
| **Design** | `AR-003` SDD; `CD-nnn` modules | *How is it built?* | Architecture baseline — `AR-001` |

> **Rule `SD-01` — a scope change is a capability change.** Adding a requirement inside an existing
> module is a *requirements* change (`RQ-005`), not a scope change, unless it adds a capability the
> module's declared boundary excludes. Adding a module, a portal, a revenue stream or an integration
> counterparty **is** a scope change.
>
> This distinction matters because the estate has none. Scope moved from 11 to 67 modules and the
> only artefact recording it is a narrative delta.

### 5.2 Product descriptions

Every scope item has a product description. The estate already has them and they are good:

| Product class | Description artefact | Sections | Adequacy |
|---|---|---|---|
| ERP module | `M*.md` | 19-section enforced template | ✅ Strong. `00-06` §7: *"at a level a vendor could quote against"* |
| Portal / application | `P*.md` | Same template | ✅ Complete — 771 KB, 10,020 lines |
| Content file | `project_content` templates | 12 templates in `_templates/` | ✅ |
| Guiding document | `_templates/TPL_Guiding_Document.md` | 9 sections | ⚠ Exists; **127 of 140 unwritten** |
| Infrastructure component | — | — | ⛔ None. `PE-001`…`PE-009` all absent |
| Data migration object | `DM-*` workbooks | 7 field-mapping workbooks | ◐ Written against **unprofiled** sources (`ISS-006`) |

### 5.3 The scope boundary rules

| Rule | Provision | Source |
|---|---|---|
| `SD-02` | **One system of record.** Every business object with a lifecycle or financial consequence is mastered in the ERP. Portals hold no authoritative state | `00-02` §7 principle 1 |
| `SD-03` | **One module, one capability.** A capability claimed by two modules is a boundary dispute for `AR-005` | `FOLDER_STRUCTURE` §7 |
| `SD-04` | **One entity, one owner.** Every data entity is owned by exactly one module | `05-02` |
| `SD-05` | **Declared boundaries are symmetric.** If `M01` declares a boundary with `M31`, `M31` declares the same boundary | `RG-04` |
| `SD-06` | **The ten `OOS-nn` exclusions are the Board's.** Only the Board may vary them | `GV-001` §6.2 |

### 5.4 The overlap control that does not exist

`FOLDER_STRUCTURE.md` §7 names **three** controls preventing capability overlap across 67 modules.
Their status, enumerated 2026-08-18 02:06:

| Control | Artefact | Status |
|---|---|---|
| Module boundary and overlap rules register | `02-03` / `AR-005` | ⛔ **Does not exist** |
| Single-owner entity allocation | `05-02` | ◐ Exists but is **titled and scoped to 30 modules** (`AF-07`). 37 modules' entities are unassigned |
| Declared scope boundary per module | `M*.md` §scope boundary | ✅ Present in all 67 |

> **Two of the three overlap controls are not operating.** With 67 modules the probability that two
> claim the same capability approaches certainty, and the estate already shows it: `fix.van.stock`
> double-declared (`M-07`), `fix.custody.event` ambiguous (`M-08`), and 255 entity references
> naming entities their declared owner does not define. The third control — per-module declared
> boundaries — is doing all the work alone.

---

## 6. Scope Change Control

### 6.1 What constitutes a scope change

| Change | Scope change? | Authority |
|---|:--:|---|
| Add or remove a module, portal or application | **Yes** | Steering Committee; Board if a category changes |
| Add or remove a revenue stream | **Yes** | Board |
| Add an integration counterparty | **Yes** | Steering Committee |
| Move a capability between modules | **Yes** — boundary change | ARB, then Steering Committee |
| Vary an `OOS-nn` exclusion | **Yes** | **Board only** |
| Add a P0/P1 requirement inside an existing module boundary | No — requirements change | Steering Committee (`RQ-005`) |
| Add a P2/P3 requirement inside an existing module boundary | No | Change Advisory Board |
| Change wave allocation | No — schedule change | `GV-004`; Steering Committee if a gate date moves |
| Add a content file to an existing class | No | Content Council |
| Add a **content class** | **Yes** | Steering Committee |

### 6.2 Procedure

The procedure is `GV-003` §6 and is not restated. Scope changes carry three additional
requirements:

| # | Additional requirement | Why |
|---|---|---|
| `SC-01` | The impact assessment must state the effect on **effort in PW**, counted from the affected specifications — not estimated in the change request | The estate's three effort figures all arose from estimating rather than counting |
| `SC-02` | The assessment must name the **benefit added or forgone**, and `BM-004` is updated in the same change | `CC-05`. A scope change with no benefit statement is a cost with no case |
| `SC-03` | The assessment must state which **wave** absorbs the change and what that wave gives up | `GV-004` §5 shows Waves 1–4 already over capacity. "It fits" is not an answer |

### 6.3 The wave lock

| Rule | Provision |
|---|---|
| `WL-01` | **Scope is locked at wave start.** No approved change enters a wave in progress (`CC-04`, `00-04` §5.4) |
| `WL-02` | An approved change enters the **next** wave, or the parking lot |
| `WL-03` | The only exception is a change required to correct a **statutory non-compliance** or a **Sev-1 defect**, and it is authorised by the CTO with retrospective Steering review |
| `WL-04` | Wave scope at lock is recorded in the gate report as the variance denominator |

### 6.4 The parking lot

| Provision | Detail |
|---|---|
| Purpose | To hold good ideas without letting them into a wave. `00-04` §1.1 names *"a parking lot for good ideas"* as the `RSK-002` mitigation; no parking lot exists |
| Identifier | `PL-nnn`, allocated by the PMO |
| Contents | Any capability raised, assessed and not approved for the current baseline |
| Review | Every wave gate. An item unreviewed for three gates is closed with a reason |
| Rule `PL-01` | **A parking-lot item is not a commitment.** It carries no effort, no budget and no date until it becomes a change request |

### 6.5 Gold-plating control

| Rule | Provision |
|---|---|
| `GP-01` | Work delivered that is not traceable to a baselined scope item and an approved requirement is **gold plating** and is rejected at code review |
| `GP-02` | Every build ticket carries a `CD-nnn`, an `FR-` identifier and a wave. `BE-005` and `RR-002` make this enforceable; until they exist, it is a manual check |
| `GP-03` | A squad delivering unrequested capability is reported to the PMO as a scope event, not praised as initiative |

> `GP-02` cannot be enforced today: **48 `CD-` identifiers collide** (`ISS-002`) and the requirement
> denominator is disputed (`ISS-007`). Gold-plating control is therefore **advisory until `BE-005`
> and `RR-002` are issued** — stated here rather than assumed to work.

---

## 7. Measuring Scope

### 7.1 The variance report

Produced by the PMO at every wave gate and at every Steering Committee meeting.

| Metric | Definition | Denominator |
|---|---|---|
| **Scope variance** | Capabilities added or removed since baseline approval | `SB-3` |
| **Cumulative movement** | Capabilities changed across all baselines | `SB-1` |
| **Requirement variance** | `FR-` identifiers added or retired since the requirements baseline | `RQ-001` |
| **Effort variance** | PW added or removed, counted from specifications | `GV-007` |
| **Uncontrolled change** | Capabilities present in the estate but in no baseline **and** no change request | Zero is the only acceptable value |
| **Parking lot ageing** | `PL-nnn` items by age | — |

### 7.2 The current position

| Metric | Value at 2026-08-18 02:06 (+06) |
|---|---|
| Approved baseline | **`SB-1`** — 11 modules, from March 2026 |
| Current baseline | **`SB-3`** — 67 modules, approved by nobody |
| **Uncontrolled change** | **56 modules, 6 portals, ~2,591 requirements, 477 content files** |
| Change requests raised, ever | **0** |
| Parking lot | Does not exist |
| Scope variance measurable? | **No, until `SB-3` is approved** |

> **This table is the finding.** Every capability beyond the eleven modules in `SB-1` is, in
> change-control terms, uncontrolled — not because it is wrong, but because nothing has been
> approved since March 2026. `00-03` demonstrates that the 11→30 expansion was well-reasoned and
> well-evidenced. **A well-reasoned change is still an uncontrolled change if no one approved it.**
> `D-001` closes this in one decision.

### 7.3 Descope hierarchy

When scope must be reduced, this is the order. Established here because `06-01` §9 and `00-04`
§1.1 both assume a hierarchy without stating one.

| Order | Candidate | Authority | Basis |
|:--:|---|---|---|
| 1 | **P3 requirements**, any module | PMO with the business owner | Backlog by definition |
| 2 | **P2 requirements**, any module | Change Advisory Board | Deferrable one wave |
| 3 | **Waves 8 and 9** in whole | Board | `CON-01`; `06-01` §9 — the first deferral candidates |
| 4 | **Categories D, F, I or J** | Board | `RSK-036` names these four |
| 5 | **Wave 7** (marketplace) | Board | Revenue-generating; deferring it defers `BO-12` and BDT 84 lac |
| 6 | **Wave 6** (new asset businesses) | Board | Revenue-generating; BDT 143 lac across `M13`, `M14`, `M06` |

### 7.4 What may never be descoped

Carried from `06-01` §9 and made a baseline rule. **Any proposal to descope an item below requires
a Board decision and a recorded statutory or contractual justification.**

| Item | Reason |
|---|---|
| `M29` Identity, Access & Information Security | Everything depends on it |
| `M28` Integration, API & Event Platform | Everything depends on it |
| `M01` Service & `M02` Field Service | The business itself |
| `M19` Finance & Bangladesh compliance | Legal obligation — `CON-04` |
| `M09` Warranty & Claims | The largest single revenue-recovery benefit — BDT 100 lac |
| Bengali localisation | Field adoption fails without it — `CON-05` |
| Offline capability | Field operation fails without it — `CON-07` |
| Audit trail and data protection | Legal and ISO obligation — `CON-11`, PDPA 2026 |
| **Data residency compliance** *(added)* | Statutory. `CON-13`; `RSK-033`; not a design preference |
| **The DPIA and lawful basis for each processing purpose** *(added)* | Statutory. Enforcement lands inside Wave 4 |

---

## 8. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-006-D-01` | Whether to baseline retrospectively | Baseline forward only · Baseline all three positions | **All three** | Without `SB-1` and `SB-2`, the 11→67 movement is invisible and `RSK-002` has no measurement | The uncontrolled-change figure in §7.2 becomes stateable, and it is large |
| `GV-006-D-02` | Whether `02-02` remains authoritative | Fully · Not at all · Partially | **Authoritative on identity, ownership and priority; NOT on wave** | `02-02` was corrected to 67-module figures (`H2-01`) but inherits `06-01`'s 30-module wave allocation | Wave authority moves to `GV-004`; `PGD-A2-08` closed |
| `GV-006-D-03` | Where the scope/requirement boundary sits | Every requirement is scope · Only capabilities are scope | **Capabilities only** (`SD-01`) | A 2,996-row scope baseline is unapprovable. A 79-product baseline is | Requirement changes route to `RQ-005`, not here |
| `GV-006-D-04` | Whether to state that gold-plating control is inoperable | Assert the control · State the limitation | **State it** | `GP-02` depends on `BE-005` and `RR-002`, neither of which exists | The control is advisory and labelled so, rather than assumed effective |
| `GV-006-D-05` | Whether to publish the descope hierarchy before it is needed | Wait for pressure · Publish now | **Publish now** | A descope decided under budget pressure with no published hierarchy is decided by whoever argues hardest | `RSK-007` (budget pressure) has a pre-agreed treatment |

---

## 9. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Is the content estate inside the scope baseline, or a parallel programme? It is in no wave, no budget and no `02-02` row | Steering Committee | Week 4 | `SB-3` completeness; `AF-09` |
| `Q-02` | Are the 127 unwritten guiding documents a scope item or an overhead? They appear in no baseline at all | Programme Director | Week 4 | `D-021`; `GV-007` |
| `Q-03` | Does `SB-3` include the ~660–1,500 screens as products in their own right, or as attributes of the 12 portals? | ARB + UX lead | Week 6 | `UX-003`; `PGD-A1-05` |
| `Q-04` | Which body adjudicates a boundary dispute until `AR-005` exists? §5.4 shows two of three overlap controls inoperative | ARB | Week 2 | Every module boundary question |
| `Q-05` | Should the 48 legacy sources be scope items (each with a profile, extract and retirement) rather than a single migration line? | Migration lead | Week 6 | `MG-002`; `RL-006` |

---

## 10. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every scope position the programme has occupied is baselined with an identifier and a date | §4.2–§4.4; §4.6 register |
| `AC-02` | Scope movement is measured, not described | §4.5 — 11 dimensions, `SB-1`→`SB-3` |
| `AC-03` | The boundary between scope, requirement and design is defined | §5.1; `SD-01` |
| `AC-04` | A change is classified as scope or not-scope by a stated test | §6.1 |
| `AC-05` | The wave lock and its single exception are stated | §6.3 |
| `AC-06` | The parking lot exists with an identifier space and a review rule | §6.4 |
| `AC-07` | Controls that cannot currently operate are declared, not assumed | §5.4, §6.5 |
| `AC-08` | A descope hierarchy is published before it is needed | §7.3 |
| `AC-09` | The uncontrolled-change position is stated numerically | §7.2 |
| `AC-10` | Every figure is counted at the time of writing with a timestamp | §4.4, §4.5, §7.2 — 2026-08-18 02:06 (+06) |

**Definition of done.** Complete when every criterion is met, `SB-3` is approved by the Steering
Committee under `D-001`, the uncontrolled-change figure in §7.2 reaches zero, and `PGD-000` records
`GV-006` as ✅ with a fresh enumeration timestamp.

---

## 11. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-001`](GV-001_Programme_Charter_and_Mandate.md) §6 | The chartered scope statement and the ten exclusions |
| Upstream | [`GV-003`](GV-003_Decision_Log_and_Change_Control_Procedure.md) §6 | The change procedure this document uses |
| Downstream | [`GV-004`](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) | Holds wave allocation; consumes `SB-3` |
| Downstream | [`GV-007`](GV-007_Estimation_Model_and_Resource_Plan.md) · [`GV-008`](GV-008_Programme_Budget_and_Cost_Baseline.md) | Effort and cost of `SB-3` |
| Downstream | `RQ-001`, `RQ-005` | The requirements baseline beneath this scope baseline |
| Downstream | `AR-005` | Boundary adjudication — **absent**; §5.4 |
| Downstream | `CO-003` | The Statement of Work is bounded by `SB-3` |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-03` | The `SB-1`→`SB-2` delta and its evidence trail |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-02` | Authoritative on identity, ownership and priority; not on wave |

---

## 12. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) ·
[`GV-001`](GV-001_Programme_Charter_and_Mandate.md) · [`GV-003`](GV-003_Decision_Log_and_Change_Control_Procedure.md) · [`GV-004`](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md)

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-02` §5 §8, `00-03` ·
`../../1000fix_ERP_Module/02_Architecture/02-02` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` §9 ·
`../../1000fix_ERP_Module/FOLDER_STRUCTURE.md` §7 ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md`

**External standards** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| ISO 10007:2017 §5.2 configuration identification — selecting items, establishing baselines | §3, §4 |
| ISO 21502:2020 §7.4 scope | §5, §6 |
| PMBOK Guide 7th Edition — scope baseline components; *Delivery* performance domain | §3.1 |
| PRINCE2 7th Edition (2023) — product-based planning; Project Product Description | §5.2 |

---

## 13. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Programme Management Office | Initial issue. Retrospectively baselines `SB-1`, `SB-2`, `SB-3`; measures 11 dimensions of scope movement; states the uncontrolled-change position; establishes the wave lock, parking lot, descope hierarchy and gold-plating control; resolves the `02-02` authority contradiction as `PGD-A2-08`; declares two of three overlap controls inoperative | *pending Steering Committee* |

---

*`GV-006` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
