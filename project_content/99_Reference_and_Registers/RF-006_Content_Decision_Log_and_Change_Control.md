---
id: RF-006
title: Content Decision Log and Change Control
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead
reviewers: [CTO, CFO, Legal & Compliance, Enterprise Architecture, QA Lead, Localisation Lead, Programme Office, all Category Content Owners]
approver: Programme Content Lead
content_class: E
purpose: >
  The log of every content decision, its rationale, date, decision-maker and consequence — and
  the change-control process that governs how content changes after it is approved. Audit
  `AUDIT-001` finding `AF-04` records that `00-05_Decision_Log_and_Change_Control.md` does not
  exist in the module repository while two audits record decisions as though it does. `AUDIT-017`
  `OP-12` records the consequence on the content side: **1,324 open items across 189 files have
  nowhere to be logged**, and the absence of this file now blocks Definition of Done in five
  categories. This file closes that, and resolves the identifier collision that would otherwise
  have made a decision log ambiguous from its first entry.
traces_to: [00-05, AF-04, CG-006, CG-007, CG-013, CP-02, CP-08, CM-R4, CM-R5, 00-04, RF-001, RF-003, RF-005, RF-007, RF-011, RF-012, CG-008]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md §6 — decisions D-01…D-15, owners, need-by dates and consequences of delay
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md finding AF-04 — 00-05_Decision_Log_and_Change_Control.md does not exist while two audits record decision D-14 as though it does
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md finding OP-12 and recommendation R-05 — 94 explicit open decisions in Category 17 alone; RF-006 blocks Definition of Done in five categories
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/_CATEGORY_E_AUDIT_REPORT.md §Decisions — an independent D-01…D-05 series colliding with 00-04 §6
    verified: 2026-08-18
    class: P1
  - source: Extraction of open-item identifiers across project_content/, run 2026-08-18 — 1,230 distinct file-local O-nn across 195 files and 94 qualified OP-nnn-OI-nn in Category 17
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md — states, version numbering and release pinning; the lifecycle this file's change control operates on
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2026-11-18
---

# RF-006 — Content Decision Log and Change Control

> **Written ahead of the rest of Category 99, on `AUDIT-017` recommendation `R-05`.** Its absence
> was blocking Definition of Done in five categories. Every affected file's DoD line —
> *"Decision(s) taken while authoring logged in `RF-006`"* — is now discharge-able.

---

## 1. Purpose

`AF-04` is one of four **critical** findings in the repository audit, and the only one whose
remedy was assigned to the content set rather than to engineering:

> `00-05_Decision_Log_and_Change_Control.md` does not exist, while two audits record decisions
> (`D-14`) as though it does. **Open — must be created.**

The Master Index responded by registering `RF-006` *"specifically so that content does not repeat
the module repository's missing decision log"*. The file then went unwritten for the same reason
`00-05` did: a decision log is boring until the day someone asks why something was decided, and
by then the answer is gone.

Fourteen months of decisions have accumulated in the interval. They are not lost — they are
scattered across 195 files as file-local open items, each numbered from `O-01`, each invisible to
the others. `AUDIT-017` `OP-12` measured the cost in one category: **94 open decisions with
nowhere to be logged.** Enumeration across the whole content set on 2026-08-18 finds **1,230**.

This file does four things:

1. **Fixes the identifier collision** that would make any decision log ambiguous (§4.2).
2. **Registers the programme decisions** the content set depends on, with their real status (§4.3).
3. **Registers the content decisions** taken to date, with rationale and consequence (§4.4).
4. **Defines change control** — how an approved content file changes, and what that obliges (§4.7).

---

## 2. Scope

**In scope** — content decisions and their rationale; the programme decisions content depends on;
the consolidated open-item position; change control for content after approval; the ID retirement
log required by `CP-02` and check `B3`.

**Out of scope**

| Excluded | Owner |
|---|---|
| Programme decisions themselves — making them | `00-04` §6 owners |
| The content lifecycle states and version numbering | `CG-006` |
| Review gates and who signs what | `CG-007` |
| Escalation triggers into legal or tax | `CG-013` |
| Risk (a decision not taken is a risk; a decision taken is a decision) | `RF-011` |
| Unscheduled content demand | `RF-007` |
| Audit findings | `RF-012` |

---

## 3. Audience

| Reader | Uses this log to |
|---|---|
| **A content author** | Discharge the `CG-008` DoD line "decisions logged in `RF-006`" |
| **A reviewer at G2** | Check that a stated position rests on a logged decision, not on an author's preference |
| **The Steering Committee** | See every decision the content set is waiting on, in one table with owners and dates |
| **A successor Content Lead** | Understand why the register looks the way it does |
| **An auditor** | Trace a content position to the decision that produced it |

---

## 4. Content

### 4.1 What is a decision, and what is not

| Is a decision | Is not |
|---|---|
| A choice between two defensible options, where the alternative would have produced different content | A fact discovered by enumeration |
| A choice that binds other files | A wording preference inside one file |
| A choice a successor would otherwise re-litigate | An editorial correction |
| An interpretation of an ambiguous upstream requirement | A defect fix |

**Test.** If a competent successor would reasonably do it differently and be right to, it is a
decision. If they would simply be wrong, it is a fact and belongs in the file, not here.

---

### 4.2 The identifier ruling — `PD-`, `CD-` and the legacy `D-` space

`RF-001` finding **`GL-03`** established that `D-nn` means two different things:

| `D-01` in | Means |
|---|---|
| `00-04` §6 | *Approve the expanded scope, budget and 36-month horizon* — Board / CEO |
| `_CATEGORY_E_AUDIT_REPORT.md` §Decisions | *Ownership class is a mandatory, non-nullable dimension on every stock quant and move* — `M15` |

`D-03` is the most-cited decision in the workspace — **81 references** — and resolves to the
marketplace principal-or-agent determination in one document and to opening-balance methodology in
the other. A decision log that adopted `D-nn` would be ambiguous in its first table.

**Ruling `RF6-01`.**

| Space | Meaning | Owned by | Allocated here |
|---|---|---|:--:|
| `PD-nn` | **Programme decision** — mirrors `00-04` §6 one-for-one, `PD-01` ≡ `00-04` `D-01` | Board / CEO / CTO / CFO | ❌ Mirrored, never allocated |
| `CD-nn` | **Content decision** — binds content, taken by the content workstream | Programme Content Lead | ✅ Allocated here |
| `ED-nn` | **Category E audit decision** — the colliding series, renamed at source | CTO | ❌ Requires an edit to `_CATEGORY_E_AUDIT_REPORT.md` |
| `D-nn` | **Legacy, ambiguous.** Retained only in quotations of existing text, always with its source document named | — | ❌ Never allocated again |

> **`CD-` and `CD-nnn` are different families.** `CD-041` is a custom-development component in
> `02-02` (199 registered). `CD-04` is a content decision here. Two digits versus three, as with
> `LG-01` / `LG-001`. This is a hazard, it is disclosed, and the alternative — inventing a fourth
> prefix — was rejected because `CD` for *content decision* is what authors will write.
> **Rule: a content decision is always cited as `RF-006` `CD-nn`.**

**Ruling `RF6-02`.** `_CATEGORY_E_AUDIT_REPORT.md` renumbers its `D-01`…`D-05` to `ED-01`…`ED-05`.
Until it does, the five references in that document are the only place `D-01`…`D-05` may mean
anything other than `00-04` §6. Carried to `RF-012` as finding `RF-03`.

---

### 4.3 Programme decisions the content set depends on

Mirrored from `00-04` §6. **This file does not own them and cannot change them.** The
*"Content blocked"* column is this file's contribution and is enumerated from the category audits.

#### Primary decisions

| ID | ≡ | Decision | Owner | Needed by | Status | Content blocked |
|---|---|---|---|---|:--:|---|
| `PD-01` | `D-01` | Approve the expanded scope, budget and 36-month horizon | Board / CEO | Before kickoff | **Open** | Everything. `CG-002` ratification waits on it |
| `PD-02` | `D-02` | Confirm and protect business super-user availability across all waves | CEO + department heads | Before kickoff | **Open** | `SP-002` as-is baseline; every `TR` course validation; `TS-006`–`TS-011` UAT |
| `PD-03` | `D-03` | **Marketplace commercial model — principal vs agent, commission, settlement, liability** | CEO + CFO + Legal | W7 − 3 months | **Open** | `LG-004`, `EO-001`, `EO-002`, `EO-013`, `DT-039`, `SP-024`, `M12`, `M53`. **`P07` is `BLOCKED`** |
| `PD-04` | `D-04` | Legal-entity structure for rental and refurbished resale | CFO + Legal | W6 − 3 months | **Open** | `MD-002`, `DT-036`–`DT-038`, `LG-013`, `M13`, `M14`, `M44` landed-cost treatment |
| `PD-05` | `D-05` | Multi-country target markets and sequence | CEO | W9 − 3 months | **Open** | `MD-006`, `BN-001`, `M65`. Not yet blocking |
| `PD-13` | `D-13` | **Approve the split-residency data architecture**, subject to the `DEP-31` legal opinion | CTO + CFO + Legal | **Before W1 architecture is fixed** | **Open — most urgent in the programme** | `LG-012`, `AP-012`, `OP-012`, `NFR-086a/b/c`. **No lawful DR path exists** (`AUDIT-017` `OP-01`) |
| `PD-14` | `D-14` | Accept the restated provisional TCO of $620K–$1,050K, or descope | Board / CEO / CFO | Before next Board review | **Open** | The **520–775 PW content estimate is not in the business case** — `AF-09`. Same agenda item |
| `PD-15` | `D-15` | Confirm significant-data-fiduciary status and, if so, appoint a Chief Data Officer | CEO + Legal | W4 − 3 months | **Open** | `LG-008`–`LG-012`, `AP-012`. **No DPO and no DPIA exist** (`AUDIT-016` `AP-08`) |

#### Secondary decisions

| ID | ≡ | Decision | Owner | Needed by | Status | Content blocked |
|---|---|---|---|---|:--:|---|
| `PD-06` | `D-06` | Telephony vendor for hotline 16743 | CTO | W4 − 2 months | Open | `NT-019` IVR, `BN-017` voice pack |
| `PD-07` | `D-07` | Whether to adopt a commercial RMM agent | CTO + CFO | W5 | Open | `SP-011`, `UI-035`, `KB-007` |
| `PD-08` | `D-08` | Data residency posture for recovered customer data | CTO + Legal | W6 − 2 months | Open | `SP-012`, `LG-017`, `DT-034` |
| `PD-09` | `D-09` | Whether 1000FiX guarantees marketplace work to the customer | CEO + Legal | W7 − 3 months | Open | `LG-004`, `EO-002`, `HC-009` |
| `PD-10` | `D-10` | Seller insurance requirement and liability caps | Legal | W7 − 3 months | Open | `LG-004`, `EO-001` |
| `PD-11` | `D-11` | Technician device procurement model | Ops Director + CFO | W2 − 2 months | Open | `TR-009`, `MD-042`, `TS-015` low-end device profile |
| `PD-12` | `D-12` | Refurbished warranty terms and reserve policy | CFO + Retail Head | W6 | Open | `MD-031`, `DT-036`, `LG-013` |

#### Decisions the content set needs and `00-04` does not carry

Named by the category audits and by Category 99's own registers, owned by nobody today.
**`RF6-03`: these must be added to `00-04` §6 as `PD-16`…`PD-22`**; they are listed here so they
are not lost meanwhile.

| Proposed | Decision | Raised by | Content blocked |
|---|---|---|---|
| `PD-16` | **Is 1000FiX a regulated entity under the Hazardous Waste (E-waste) Management Rules 2021?** | `AUDIT-013` | `LG-018`, `MD-047`, `DT-035`, `SP-026`. EPR collection target reaches **50% in 2026** — `RF-008` `ST-14` |
| `PD-17` | **The limitation period** on which more than twenty `DT` retention rows depend | `AUDIT-013` | `LG-009` schedule; 20+ `DT` files |
| `PD-18` | **Webhook signature scheme** — none exists anywhere | `AUDIT-016` `AP-04` | `AP-004`, `AP-007`, `AP-008`; every W3 partner integration |
| `PD-19` | **API scope vocabulary** — every credential is currently scoped by the issuer's judgement | `AUDIT-016` `AP-05` | `AP-005`, `M29`, `PS-02` |
| `PD-20` | **`API-04` error envelope vs RFC 9457** — divergence with no ruling | `AUDIT-016` | `AP-006`, `UI-004` alignment |
| `PD-21` | **ISO 9001:2026 transition plan.** The standard publishes **16 September 2026** and replaces ISO 9001:2015, with transition to September 2029 — **inside the programme window**. It is a certification decision, not a content decision | `RF-008` `SR-03` | **38 files** citing ISO 9001:2015 clauses: `LG-022`, `DT-043`, `SP-029`, `TR-016`, `MD-046`, `KB-012`, `KB-015` and 31 further. `P11` is the application the certification body inspects |
| `PD-22` | **Adopt WCAG 2.2, or hold at WCAG 2.1 AA and record the choice.** `PS-04` and `05-06` make 2.1 AA contractual; **2.2 has been the W3C Recommendation since October 2023**. Holding is defensible if deliberate; it is not defensible by omission | `RF-008` `SR-04` | `CG-011`, `UI-010`, `TS-016`, `RP-007`, `MM-002`. `TS-016` currently tests to a superseded standard either way |

**Twenty-two decisions are open. Not one is closed.** Fifteen are registered in `00-04`; **seven
are not registered anywhere**. `PD-13` was flagged *"the most urgent open decision in the
programme"* and remains open while `W1` architecture proceeds. **`PD-21` has a fixed external
deadline the programme does not control** — 16 September 2026, four weeks after this register was
written.

---

### 4.4 Content decisions taken

`CD-` decisions are owned by the content workstream and are binding on the content set.

| ID | Decision | Rationale | Date | Taken by | Consequence | Status |
|---|---|---|---|---|---|:--:|
| `CD-01` | **The requirement denominator is 3,350** — distinct `FR-` across 67 modules and 12 portals, enumerated 2026-08-18 | Three figures were in circulation and were never three counts of the same thing: one prose estimate and two counts of different scopes. `RF-003` §4.2 | 2026-08-18 | Programme Content Lead with QA Lead | `TS-001` adopts it; `G4-10` becomes answerable; `AF-06` diagnosis closed, restatement still owed by the CTO | **Taken** |
| `CD-02` | **A `verified:` date may never be later than the day the source was read**, and a check is added to enforce it | 331 declarations across 68 files carry a future date. `CG-012` and `DoD-17` make the date the control; a future date defeats both. `RF-002` §4.7 | 2026-08-18 | Programme Content Lead | 68 files to correct; new check `A7` / rule `RG-09` | **Taken; remediation open** |
| `CD-03` | **Master Index §5 is a cross-reference, not a coverage map.** `RF-005` §4.4 is the coverage map | §5 counts portal-primary files only (109) and is read as total coverage (418 enumerated). A go-live gate cannot use it. `RF-005` §4.3 | 2026-08-18 | Programme Content Lead | §5 column renamed to "Portal-primary files"; gates cite `RF-005` | **Taken; edit open** |
| `CD-04` | **Decision identifiers split into `PD-` / `CD-` / `ED-`; `D-nn` is never allocated again** | `D-01` and `D-03` each mean two things across two documents. §4.2 | 2026-08-18 | Programme Content Lead with Enterprise Architecture | `_CATEGORY_E_AUDIT_REPORT.md` renumbers to `ED-`; all future citations qualified | **Taken; source edit open** |
| `CD-05` | **Acceptance criteria are cited as `<Mnn\|Pnn>/AC-nn`** | `AC-nn` is file-local. 1,568 criteria across 79 specifications share a two-digit space. Retrofitting after scripts exist is not feasible. `RF-003` §4.6 | 2026-08-18 | QA Lead with Programme Content Lead | `TS-001` adopts before the first script | **Taken** |
| `CD-06` | **`RF-005` is maintained by identifier, never by filesystem path** | `AUDIT-001` assessed that `RF-005` could not be maintained mechanically until `AF-01` moved the portal files. Maintaining by `Pnn` removes the dependency entirely | 2026-08-18 | Programme Content Lead | `RF-005` is maintainable today; `AF-01` remains open on its own merits | **Taken** |
| `CD-07` | **Open items are qualified with their owning file** — `<ID>-OI-nn`, as Category 17 already does | 1,230 file-local `O-nn` across 195 files cannot be consolidated, escalated or closed centrally. Category 17's `OP-nnn-OI-nn` is the only form that survives aggregation | 2026-08-18 | Programme Content Lead | New files use the qualified form; existing files migrate at their next revision | **Taken** |
| `CD-08` | **A content file's Bengali counterpart is a *deliverable*, not a status** | 266 files are registered bilingual and approximately none has a written counterpart, yet categories are reported "complete". Completeness that excludes half of a bilingual deliverable is not completeness | 2026-08-18 | Programme Content Lead with Localisation Lead | Category completion statements state English and Bengali separately | **Taken** |
| `CD-09` | **Category 99 registers state their own limitations rather than implying precision they lack** | `RF-003` cannot do L4 traceability while `05-01` is a summary. A matrix that looked complete would be more damaging than one that says what it cannot do | 2026-08-18 | Programme Content Lead | `RF-003` §4.8, `RF-004` §4.6, `RF-005` §4.6 | **Taken** |
| `CD-10` | **Content risk uses the `CR-nn` space, separate from programme `RSK-nnn`** | `00-04` owns 36 programme risks. A content risk register that extended `RSK-` would need `00-04`'s owner to allocate, which is precisely the coupling that left content risk unrepresented | 2026-08-18 | Programme Content Lead | `RF-011` allocates `CR-01`…`CR-nn` | **Taken** |
| `CD-11` | **`CG-005` must state the module-code allocation rule and reserve the space** | `FR-SRM2-` was created because `SRM` was taken; 34 requirements now carry a code that does not match the stated pattern. `RF-001` `GL-02` | 2026-08-18 | Enterprise Architecture | `CG-005` v1.1; `M42` code decision is the CTO's | **Raised** |
| `CD-12` | **The five proposed-but-unregistered IDs are held in `RF-007`, not silently added** | `TR-025`, `BN-019`, `DM-015`, `DM-016`, `SP-035` are cited as though registered. Adding them without a Steering decision would breach `CM-R1` register-first | 2026-08-18 | Programme Content Lead | Register total stays **452** until decided; `RF-007` §4.3 holds them | **Taken** |
| `CD-13` | **`RF-008` is authoritative for external-standard currency; no other file re-states a currency date** | Statutory and standards references appear in 229 distinct external source strings. Currency asserted per file goes stale per file | 2026-08-18 | Programme Content Lead with Compliance | Files cite `RF-008` `ST-nn`; `RF-008` carries the date | **Taken** |
| `CD-14` | **Category completion is reported with an enumeration instant, and an enumeration taken during authoring is declared a floor** | `MM-001` did not exist at 01:07 and existed at 01:18 on 2026-08-18; Category 19 grew from 0 to 7 files during the authoring of Category 99. Same condition as `AUDIT-016` `AP-17` | 2026-08-18 | Programme Content Lead | Proposed rule `RG-08` formalised; every Category 99 file carries its instant | **Taken** |

---

### 4.5 Decisions deliberately deferred

Recorded so a successor does not read silence as oversight.

| Item | Why deferred | Revisit at |
|---|---|---|
| Whether to split the generic template into five dedicated templates | `CG-009` §6 already observes the generic template governs 155 files (34%). Splitting now would re-template 155 written files for no reader benefit | After the first approval cycle |
| Whether `RF-003` should build the L4 reverse index against `05-01` as it stands | It would be 94% empty and read as 94% uncovered. Worse than absent | On `AF-06` closure |
| Whether to renumber the `KPI-` space | 291 in use, 95 registered. Renumbering touches `06-02`, 79 specifications and all 16 `RP` files | `AUDIT-015` `RP-01` remediation |
| Whether content should adopt the module `P0`–`P3` scale for the website set too | `AF-11` documents the hazard; merging the scales is out of scope for both programmes | Never — Master Index §11 |

---

### 4.6 The consolidated open-item position

Enumerated **2026-08-18**. Category 19 `MM` was in authoring; its figures are a floor
(`CD-14`).

| Category | Files carrying open items | Distinct open items |
|---|---:|---:|
| `CG` Governance | 0 | 0 |
| `VB` Voice & brand | 0 | 0 |
| `MD` Master data | 0 | 0 |
| `UI` UI copy | 1 | 6 |
| `NT` Notifications | 0 | 0 |
| `DT` Documents | 0 | 0 |
| `SP` Process & SOP | 10 | 32 |
| `KB` Knowledge | 16 | 104 |
| `TR` Training | 24 | 133 |
| `HC` Help centre | 20 | 103 |
| `LG` Legal | 24 | **174** |
| `BN` Localisation | 0 | 0 |
| `DM` Data migration | 13 | 90 |
| `TS` Test & acceptance | 18 | 126 |
| `RP` Reporting & KPI | 16 | 108 |
| `AP` Integration | 12 | 96 |
| `CM` Change & comms | 18 | 111 |
| `OP` Operations | 16 | **94** *(qualified `OP-nnn-OI-nn`)* |
| `EO` Ecosystem | 14 | 94 |
| `MM` Multimedia *(in authoring)* | 7 | 53 |
| `RF` Reference | 6 | 47 |
| **Total** | **195** | **1,271** |

**Two observations a reader should not miss.**

**Six categories carry zero open items — and that is not good news.** `CG`, `VB`, `MD`, `NT`, `DT`
and `BN` are 160 files, including the 48 `MD` seed datasets and the 44 `DT` statutory templates.
They were authored before the open-item convention emerged in Category 06. **Their decisions were
taken and not recorded.** That is `AF-04`'s failure mode reproduced inside the content set, and it
is why `MD` and `DT` have no answer to "why is it like this?" Carried to `RF-012` as finding
`RF-04` and to `RF-007` as backlog `BL-06` — a retrospective decision-capture pass over 160 files.

**`LG` carries 174 open items across 24 files** — seven per legal document, the highest density in
the register. That is proportionate: Category 10 is where four unmade upstream decisions land.

---

### 4.7 Change control

`CG-006` owns the lifecycle. This section owns **what a change obliges**.

#### 4.7.1 Change classes

| Class | Definition | Approval | Version | Notice |
|:--:|---|---|---|---|
| **`X1` Editorial** | Typo, formatting, link repair. No meaning changes | Author | `n.n+0.0.1` | None |
| **`X2` Substantive** | Meaning changes; no downstream file changes | Original approver | `n.n+0.1` | Consuming file owners informed |
| **`X3` Binding** | Changes a fact, rule, dataset or figure another file relies on | Original approver **plus** every consuming owner | `n+1.0` | `RF-006` entry mandatory |
| **`X4` Statutory / legal** | Changes an approved Class A or B file | Full gate re-run incl. G5/G6 | `n+1.0` | `LG-001` ledger; user notice where terms change |

#### 4.7.2 Rules

| # | Rule |
|---|---|
| `CC-01` | An `X3` or `X4` change **requires a `CD-` entry in §4.4 before the edit**, not after |
| `CC-02` | A change to a **derived figure** triggers a repository-wide sweep for every restatement of that figure. Correcting it at source is *not* the correction — `AUDIT_Checklist_Recurring` `F7` records one figure restated in **eleven further places across four files** |
| `CC-03` | A change to an **approved** file supersedes, never overwrites. The prior version moves to `_ARCHIVE/` with a `SUPERSEDED_` prefix (`CP-10`, `CM-R5`) |
| `CC-04` | An `X4` change re-opens the **Bengali counterpart**. A bilingual file is not `Approved` until both languages are signed off (`CM-R6`) |
| `CC-05` | A change to a file **pinned to a release** (`CG-006` §3) re-runs gate G3 against the build. An unpinned change to pinned content is a defect |
| `CC-06` | A **rename** changes the file name and every reference, and never the ID (`CM-R4`, `CP-02`) |
| `CC-07` | A **retirement** marks the ID `WITHDRAWN` in §4.8. IDs are never recycled (`CP-02`) |
| `CC-08` | An emergency change — statutory deadline, safety, live legal exposure — may proceed on the accountable owner's authority alone, and **must** be logged here within one working day with the authority named |

#### 4.7.3 The change record

| Field | Required |
|---|---|
| Content ID and version before / after | ✅ |
| Change class `X1`–`X4` | ✅ |
| What changed, in one sentence | ✅ |
| Why — the `CD-` or `PD-` reference | ✅ for `X3`, `X4` |
| Consuming files re-checked (`CC-02`) | ✅ for `X3`, `X4` |
| Approver and date | ✅ for `X2`–`X4` |
| Bengali counterpart re-opened | ✅ where `bilingual: yes` |
| Archive path | ✅ where the prior version was `Approved` |

#### 4.7.4 Change log

| # | Date | File | Ver | Class | Change | Decision | Approver |
|---|---|---|---|:--:|---|---|---|
| — | — | — | — | — | *No approved content file has yet changed. The log opens at the first `X2` change to an approved file.* | — | — |

---

### 4.8 ID retirement log

Required by `CP-02` and audit check `B3` — *"No reused IDs: compare against `RF-006` retirement
log"*. Check `B3` has been unanswerable in seventeen audits because this log did not exist.

| ID | Title | Retired | Reason | Archived at | Reallocated |
|---|---|---|---|---|:--:|
| — | — | — | *No content ID has been retired. All 452 registered IDs are live.* | — | **Never** |

**Standing statement for check `B3`:** as at 2026-08-18, **zero content IDs have been retired and
zero have been reused.** The check passes.

Two adjacent facts, not retirements:

- **Five IDs are proposed and unallocated** — `TR-025`, `BN-019`, `DM-015`, `DM-016`, `SP-035`.
  Held in `RF-007` §4.3 under `CD-12`. Not retirements; not yet allocations.
- **Two requirement families are orphaned** — `FR-SLS-` (30) and `FR-BFO-` (3). Those are `05-01`'s
  space, not content IDs, and belong to `AF-06`.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `00-04` §6 | Owns the programme decisions mirrored in §4.3 |
| `CG-006` | Owns the lifecycle states and version numbering §4.7 operates on |
| `CG-007` | Owns the gates an `X4` change re-runs |
| `CG-013` | Owns the escalation triggers behind `CC-08` |
| `RF-001` | Supplied the `GL-03` collision that §4.2 resolves |

| Depended on by | Why |
|---|---|
| **Every content file's Definition of Done** | *"Decision(s) taken while authoring logged in `RF-006`"* |
| Audit check `B3` | Answered from §4.8 |
| `RF-007` | Takes `CD-12` and the deferred decisions |
| `RF-011` | Takes `CD-10`; an unmade decision past its need-by date becomes a risk |
| `RF-012` | Takes findings `RF-03`, `RF-04` |
| `LG-001` | `X4` changes to binding terms record in its version-acceptance ledger |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Monthly** during authoring; **every wave boundary** thereafter |
| Trigger for out-of-cycle entry | Any `X3` or `X4` change; any programme decision taken or missed; any deferred decision reaching its revisit point |
| Entry rule | `CC-01` — the entry precedes the edit |
| Escalation | A `PD-` decision passing its need-by date is escalated to the Steering Committee **and raised as a risk in `RF-011`** the same week |
| Owner | Programme Content Lead |
| Retention | Permanent. This log is never archived, never truncated — it is the answer to "why" for the life of the system |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | Not started |
| G2 Factual | ● | Programme Office with Enterprise Architecture | Not started |
| G3–G6 | ○ | — | Not required |
| Final approver | — | Programme Content Lead | **Unappointed** |

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-006-OI-01` | **Twenty programme decisions are open and none is closed.** `PD-13` was flagged the most urgent in the programme and `W1` architecture is proceeding without it | Steering Committee | `P04`, `P07` `BLOCKED`; `M12`, `M13`, `M14`, `M53` |
| `RF-006-OI-02` | **`PD-16`–`PD-20` are not registered in `00-04`** and have no owner | CTO | E-waste status; retention limitation; webhook signatures; scope vocabulary; error envelope |
| `RF-006-OI-03` | **`RF6-02` — `_CATEGORY_E_AUDIT_REPORT.md` not yet renumbered to `ED-`** | CTO | `D-01`…`D-05` remain ambiguous |
| `RF-006-OI-04` | **160 files in six categories carry zero recorded decisions** — `MD` and `DT` decisions were taken and not logged | Category owners | Retrospective capture, `RF-007` `BL-06` |
| `RF-006-OI-05` | **`CD-02` remediation open** — 331 future-dated verifications across 68 files | Programme Content Lead | `RF-002` `O-01` |
| `RF-006-OI-06` | **`CD-03` edit open** — Master Index §5 column not yet renamed | Programme Content Lead | Continued misreading |
| `RF-006-OI-07` | **`CD-07` migration open** — 1,177 unqualified `O-nn` in existing files | Category owners | Central escalation of open items |
| `RF-006-OI-08` | **No Programme Content Lead appointed** to own this log | CEO | Every entry's accountability |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; register table and maintenance procedure added per `CG-009` §3
- [x] Identifier collision resolved **before** the first log entry (`RF6-01`, `RF6-02`)
- [x] All fifteen `00-04` programme decisions mirrored with content impact
- [x] Five unregistered decisions the content set needs identified and proposed as `PD-16`–`PD-20`
- [x] Fourteen content decisions logged with rationale, date, taker and consequence
- [x] Deferred decisions recorded so silence is not read as oversight (§4.5)
- [x] Open-item position consolidated by extraction with an enumeration instant (`CP-11`, `CD-14`)
- [x] Change control defined with classes, rules and a record schema
- [x] **ID retirement log present — audit check `B3` answerable for the first time**
- [x] Uses the qualified open-item form it mandates in `CD-07`
- [x] All internal links resolve
- [x] Bengali counterpart — n/a (`bilingual: no`, `CG-010` §3.2)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [x] **Discharges the DoD line "decisions logged in `RF-006`" for the five blocked categories**
- [ ] **Named approver recorded** — outstanding, `RF-006-OI-08`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
