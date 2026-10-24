---
id: GV-003
title: Decision Log & Change Control Procedure
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Management Office
approver: ERP Steering Committee
standards_basis: ISO 10007:2017 §5.3 change control · ISO 21502:2020 §7.5 change management · ISO 9001:2015 §7.5.3 · PRINCE2 7th Edition (2023) issue and change control · PMBOK Guide 7th Edition
traces_to: PGD-000 GV-003 · AUDIT-001 finding AF-04 (CRITICAL) and recommendation R-02 · 00-07 H2-08 decision D-14 · 00-04 §5.4, §6
depends_on: GV-001, GV-002
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-003 — Decision Log & Change Control Procedure
# 1000FiX ERP System & Portal Suite v2.0

### Category 00 · Code `GV` · ISO 10007:2017 · ISO 21502:2020 · PRINCE2 7

---

> **This document closes a critical audit finding.** `AUDIT-001` finding **`AF-04`** records:
> *"The decision log referenced by two audits does not exist."* Audit `00-07` escalated the
> programme's largest financial variance as **decision `D-14`** — an identifier that, until this
> document, resolved to nothing. Thirteen prior decisions were equally unlocatable.
>
> **A programme that cites decisions it cannot produce has not made them.** This is the register.

---

## 1. Purpose

This document does two related things. It is the **decision log**: the permanent, append-only
record of every programme decision, its context, its options, its rationale, its author and its
date. And it is the **change control procedure**: the method by which anything already baselined
is changed.

They are one document because they are one mechanism. A change request that is approved becomes a
decision; a decision that alters a baseline is a change. Splitting them is how programmes end up
with an approved change nobody can trace to a decision, and a decision nobody applied to a
baseline.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The `D-nnn` identifier space: its format, its allocating authority, and the rule that it is never reused |
| 2 | The decision record schema — the fields every decision must carry |
| 3 | **The reconstructed log `D-001`…`D-015`**, recovered from `00-04` §6, `00-07`, `AUDIT-001` and `PGD-AUDIT-001` |
| 4 | New decisions `D-016`…`D-024` raised by this category's authoring |
| 5 | The change control procedure: raise → assess → classify → decide → apply → verify |
| 6 | Baseline definitions and what "baselined" means for each artefact class |
| 7 | The change log and its identifier space `CR-nnn` |
| 8 | Emergency and retrospective change |
| 9 | The relationship to Architecture Decision Records (`AR-004`) and content decisions (`RF-006`) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Who is empowered to take each decision | `GV-002` §5.2 | This document records; `GV-002` empowers |
| **Architecture** decision records — context, options, consequences, status per technical decision | `AR-004` | An ADR is a design artefact with its own lifecycle and its own identifier space. This log records *that* an architecture decision was taken and points to the ADR |
| **Content** decisions | `../../project_content/99_Reference_and_Registers/RF-006` | Workstream 5 keeps its own log under `CG-006` §6, deliberately, so that content decisions do not repeat `AF-04` |
| Scope baseline definition and the scope change hierarchy | `GV-006` | `GV-006` defines what a scope baseline *is*; this document defines how any baseline is changed |
| Configuration items, versioning and supersession | `GV-011` | Configuration management is the wider discipline; change control is one of its five processes (ISO 10007 §5) |
| Defect triage and severity | `QA-010`, `SV-006` | A defect is not a change. Conflating them is how change control becomes a bug queue |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Steering Committee** | The record of what they have decided, and the queue of what they must decide |
| **PMO** | The operating procedure. The PMO is the custodian of this log |
| **Programme Director** | The change pipeline, its ageing, and the decisions blocking delivery |
| **Auditors** | The evidence trail. `AF-04` exists because this was absent |
| **Implementation vendor** | The only route by which scope changes. A change not recorded here is not a change the Company owes payment for |
| **Anyone citing "`D-14`"** | The decision itself, at last |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 10007:2017** *Guidelines for configuration management* | §5.3 **change control**; §5.4 configuration status accounting | §6 implements the change-control process: identify, evaluate, disposition, implement, verify. §7 implements status accounting — the log *is* the accounting record | ISO 10007 addresses product configuration; this document applies it to the documentation and scope baselines as well, which is the wider reading the standard permits |
| **ISO 21502:2020** §7.5 | Change control within a project | Change classification and authority thresholds in §6.3 | None |
| **ISO 9001:2015** §7.5.3 | Control of documented information; changes controlled and versions managed | Every decision alters a controlled document; §6.6 requires the affected documents to be versioned in the same change | The Company's ISO 9001 certification makes this obligatory, not optional |
| **PRINCE2 7th Edition (2023)** | Issue and change control; the *Issue Register* and *Daily Log*; change authority and change budget | §6.3 adopts a change authority with delegated limits (the CAB), and §6.7 a change budget concept applied to the wave contingency | PRINCE2 separates Issue / Request for Change / Off-Specification. Adopted, with "off-specification" mapped to the defect process in `QA-010` |
| **PMBOK Guide 7th Edition** | Integrated change control; decision-making under the *Uncertainty* performance domain | §4 decision record schema captures options and rationale, not just outcome | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Risks, Assumptions, Dependencies & Governance §6 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` | `D-01`…`D-05`, `D-13`, `D-14`, `D-15` primary decisions; `D-06`…`D-12` secondary — **the primary evidence for reconstruction** |
| Risks… §5.4 | Same | The existing change-control flow diagram and its four rules |
| Category H Audit | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-07` | H2-08 escalation of the effort variance **as `D-14`** |
| Content & Repository Integrity Audit | `../../project_content/_AUDIT/AUDIT-001` | `AF-04` (critical, open) and recommendation `R-02` |
| Register Integrity Audit | `../_AUDIT/PGD-AUDIT-001` | `PGD-A1-05`, `PGD-A1-09`; the register's own change-control clause |
| Technology Decision Log | `../../1000fix_ERP_Module/02_Architecture/02-05` §10 | `TD-01`…`TD-15` — fifteen technology decisions **already taken**, in a separate identifier space |
| Content Lifecycle and Versioning Policy | `../../project_content/00_Content_Governance_and_Standards/CG-006` §6 | The content change-control procedure and impact-list method, adopted here by analogy |
| **Technology Stack Specification** §24, §25.2 | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` | **`D-15`…`D-17`** — three technology decisions raised there and never registered here, on identifiers this log had already allocated. Re-registered as `D-025`…`D-027` (§5.4a). **Added 2026-08-19; `GV-003-F-01`** |
| Master Index §6 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-01` | The existing change-control statement and the five pre-Wave-1 decisions |

### 2.3 Audit findings this document closes

| Finding | Source | Severity | How this document closes it |
|---|---|:--:|---|
| **`AF-04`** | `AUDIT-001` | **Critical** | §5 reconstructs `D-001`…`D-015` from the primary sources, records each with its status and its evidence, and marks as `UNRECOVERABLE` anything that cannot be reconstructed. Nothing was unrecoverable |
| `R-02` | `AUDIT-001` | — | *"Create the decision log and reconstruct D-01…D-14; mark unrecoverable decisions rather than renumbering."* Done at §5 |
| `D-14` unlocatable | `00-07` H2-08 | High | `D-014` now exists, with the counted figures, the option set and the decision status |
| `GV-001` `CC-03` | `GV-001` | — | The charter condition requiring this log to exist by Week 2 |
| **Template collision** | *new* | Medium | The house template `TPL_Guiding_Document.md` §4 invites every document to number its local decisions `D-01`, colliding with the programme space. §3.4 rules the local form `<ID>-D-nn`. Raised as `PGD-A2-03` |

---

## 3. The `D-nnn` Identifier Space

### 3.1 Format and authority

```
D-nnn          programme decision, three digits, zero-padded, allocated sequentially
```

| Rule | Provision |
|---|---|
| `DL-01` | **The PMO is the sole allocating authority for `D-nnn`.** No other document, body or person may issue a `D-` identifier |
| `DL-02` | Identifiers are **permanent**. A withdrawn or superseded decision keeps its identifier and gains a status; the number is never reissued (`RG-02`, `PG-05`) |
| `DL-03` | Allocation is **sequential and contiguous**. A gap in the sequence is a defect, not a reservation |
| `DL-04` | A decision is allocated an identifier **when it is raised**, not when it is taken. This is what makes the queue visible |
| `DL-05` | **Zero-padded to three digits.** The pre-existing log used `D-01`…`D-15`; those are restated here as `D-001`…`D-015`, with the short form recorded in §5 as an alias so that citations in `00-04`, `00-07` and `AUDIT-001` continue to resolve |

> **Why `DL-05` is not renumbering.** `RG-02` forbids reusing or renumbering an allocated
> identifier. `D-01` and `D-001` are the *same* decision under two renderings, not two decisions —
> the alias column in §5 makes that explicit and machine-checkable. This is a formatting
> normalisation, and it is recorded here so that no future reader mistakes it for a reallocation.

### 3.2 Adjacent identifier spaces — what is *not* a `D-nnn`

| Space | Contains | Owner | Relationship |
|---|---|---|---|
| `TD-nn` | Technology decisions already taken — 15 of them in `02-05` §10 | Architecture Review Board | **Migrating to `AR-004` ADRs.** Until `AR-004` exists, `TD-nn` remains valid and is cross-referenced here, not absorbed |
| `ADR-nnn` | Architecture Decision Records — context, options, decision, consequences, status | `AR-004` | A significant architecture decision gets **both**: a `D-nnn` row here recording *that it was taken and by whom*, and an ADR carrying the technical reasoning |
| `RF-006` content decisions | Content decisions | Programme Content Lead | Separate log, deliberately, per `CG-006` §6 |
| `CR-nnn` | Change requests | PMO | A change request that is **approved** produces a `D-nnn`. A rejected one does not |
| `<ID>-D-nn` | Document-local decisions | The document's owner | See §3.4 |

### 3.3 Decision status values

| Status | Meaning | May be cited as decided? |
|---|---|:--:|
| `OPEN` | Raised, allocated, not yet taken | **No** |
| `IN ASSESSMENT` | Impact assessment under way | **No** |
| `ESCALATED` | Referred upward; the owning body has changed | **No** |
| `DECIDED` | Taken by the empowered body and minuted | **Yes** |
| `DEFERRED` | Consciously postponed, with a review date. **A deferral is itself a decision and is minuted** | No — but the deferral may be cited |
| `SUPERSEDED` | Replaced by a later decision, which is named | Reference only |
| `WITHDRAWN` | No longer required. The identifier is retired | No |
| `UNRECOVERABLE` | Referenced in the estate but not reconstructable from any source | **No — and this must be stated wherever it is cited** |

### 3.4 Document-local decisions

> **Rule `DL-06`.** A guiding document recording decisions local to itself uses the form
> **`<DOCUMENT-ID>-D-nn`** — for example `GV-001-D-01`. It may **not** use the bare form `D-01`.
>
> The house template `_templates/TPL_Guiding_Document.md` §4 currently shows a bare `D-01` in its
> "Decisions Recorded" table. Applied literally across 140 documents that would produce up to 140
> different decisions all called `D-01`, colliding with the programme space — precisely the defect
> class that produced `H-03` (48 colliding CD identifiers), `H2-04` (22 colliding KPI identifiers)
> and `PGD-A1-01`. The template is corrected as part of this issue; the finding is
> **`PGD-A2-03`**.

---

## 4. The Decision Record Schema

Every decision carries these fields. A decision missing any mandatory field is `OPEN`, whatever
else it says.

| Field | Mandatory | Purpose |
|---|:--:|---|
| `id` | ✓ | `D-nnn` |
| `alias` | conditional | The short form, where the decision predates `DL-05` |
| `title` | ✓ | What is being decided, in one line |
| `raised` | ✓ | Date the decision was identified as needed |
| `raised_by` | ✓ | Role |
| `owner` | ✓ | The **body** empowered to take it, per `GV-002` §5.2 |
| `needed_by` | ✓ | The point at which the *absence* of the decision starts destroying work — not when it would be convenient |
| `status` | ✓ | Per §3.3 |
| `context` | ✓ | Why the decision exists. A decision with no context cannot be re-evaluated when circumstances change |
| `options` | ✓ | **At least two.** A decision with one option is a notification |
| `decision` | on `DECIDED` | What was chosen |
| `rationale` | on `DECIDED` | Why. **This is the field that has value in three years** |
| `decided_on` / `decided_by` | on `DECIDED` | Date and the minute reference |
| `consequence` | on `DECIDED` | What becomes true, and what becomes impossible |
| `affects` | ✓ | The baselines, documents and identifiers this decision changes |
| `review_by` | on `DEFERRED` | When the deferral is revisited |
| `superseded_by` | on `SUPERSEDED` | The `D-nnn` that replaced it |
| `evidence` | ✓ | Where the record lives — minute, audit finding, source document and section |

> **Rule `DL-07` — two-day rule.** A decision taken by any body in `GV-002` §4 is written to this
> log within **two working days** of the meeting, by the body's secretary. `GV-002` §4.2 makes
> this the Steering Committee secretary's explicit duty.

---

## 5. The Decision Log

### 5.1 Reconstruction method and result

`AF-04` required reconstruction from `00-04` §6, `00-03`, `00-06` and `00-07`, with anything
unreconstructable marked `UNRECOVERABLE`.

| Step | Result |
|---|---|
| Sources searched | `00-01` §6 · `00-03` · `00-04` §6 (primary and secondary tables) · `00-06` §8 · `00-07` §7 · `02-05` §10 · `AUDIT-001` §2, §8 · `PGD-AUDIT-001` §9, §10 |
| Decisions found | **15** — `D-01`…`D-15`, all present in `00-04` §6 |
| Decisions **unrecoverable** | **0** |
| Decisions found **already taken** | **0** — every one of the fifteen is a decision *required*, not a decision *made* |
| New decisions raised by Category 00 authoring | **9** — `D-016`…`D-024` |
| **Total in the log at issue** | **24** |

> **The reconstruction's most important finding is that there was nothing to reconstruct.**
> `00-04` §6 is titled *"Decisions Required Before Wave 1"*. Every entry is a decision the
> programme knows it must take. **Not one has been taken.** The programme has been described
> throughout as having a decision log with fourteen decisions in it; what it has is a list of
> fifteen decisions it has not made. `AF-04` reported the file as missing. The more serious
> position is that the file's absence concealed a fully open decision queue, the oldest entries of
> which have been open since **2026-08-12** — and two of which (`D-013`, `D-014`) block Wave 1.

### 5.2 Log — reconstructed decisions `D-001` … `D-015`

| ID | Alias | Title | Owner *(`GV-002` §5.2)* | Raised | Needed by | Status | Blocks |
|---|---|---|---|---|---|:--:|---|
| `D-001` | `D-01` | Approve the expanded scope, budget and 36-month horizon | **Board** | 2026-08-12 | Before kickoff | **OPEN** | The programme cannot start. All 610 files remain non-binding |
| `D-002` | `D-02` | Confirm and protect business super-user availability across all waves | **Board** *(instructs)* | 2026-08-12 | Before kickoff | **OPEN** | `RSK-001`, the highest-rated risk. UAT capacity paces the programme (`CON-12`) |
| `D-003` | `D-03` | Marketplace commercial model — principal vs agent, commission, settlement, liability | **Board**, with external tax advice | 2026-08-12 | W7 − 3 months | **OPEN** | `RSK-022` (Critical); Wave 7 build |
| `D-004` | `D-04` | Legal-entity structure for rental and refurbished resale | **Board**, on CFO recommendation | 2026-08-12 | W6 − 3 months | **OPEN** | Finance design; `M13`, `M14`; `DEP-10` |
| `D-005` | `D-05` | Multi-country target markets and sequence | **Board** | 2026-08-12 | W9 − 3 months | **OPEN** | `M65` country pack specification; `DEP-13` |
| `D-006` | `D-06` | Telephony vendor for hotline 16743 | **ARB** → **CFO** *(L6)* | 2026-08-12 | W4 − 2 months | **OPEN** | `M27` contact centre build; `DEP-11`, `DEP-26` |
| `D-007` | `D-07` | Whether to adopt a commercial RMM agent at L6 | **CFO**, on ARB recommendation | 2026-08-12 | W5 | **OPEN** | `M05` managed services; `02-05` §7 records it "deferred to Wave 5" with no review mechanism |
| `D-008` | `D-08` | Data residency posture for customer data recovered under `M06` | **Data Protection Forum** | 2026-08-12 | W6 − 2 months | **OPEN** | `M06` data services launch; interacts with `D-013` |
| `D-009` | `D-09` | Whether 1000FiX guarantees marketplace work to the customer | **Board** | 2026-08-12 | W7 − 3 months | **OPEN** | `RSK-023`; marketplace liability model |
| `D-010` | `D-10` | Seller insurance requirement and liability caps | **Steering Committee**, on Legal advice | 2026-08-12 | W7 − 3 months | **OPEN** | `M12` seller onboarding; `EO-002` |
| `D-011` | `D-11` | Technician device procurement model — Company-issued vs allowance | **Steering Committee** | 2026-08-12 | W2 − 2 months | **OPEN** | `ASM-02`; `DEP-08`; Wave 2 field rollout |
| `D-012` | `D-12` | Refurbished warranty terms and reserve policy | **Steering Committee**, on CFO recommendation | 2026-08-12 | W6 | **OPEN** | `RSK-028`; `M14` |
| `D-013` | `D-13` | **Approve the split-residency data architecture** — Bangladesh-resident store for sensitive personal data, regional store for the remainder, subject to the legal opinion at `DEP-31` | **DP Forum** *(recommends)* → **Board** *(approves)* | 2026-08-12 | **Before Wave 1 architecture is fixed** | **OPEN** | **The entire data architecture.** `RSK-033`; `C-05`; `OP-01`; `SC-007`; `DA-001` |
| `D-014` | `D-14` | **Accept the restated effort and cost position, or direct a descope** | **Board** | 2026-08-13 | Before the next Board review | **ESCALATED — unrecorded for 5 days** | The budget baseline (`GV-008`); the implementation contract (`CO-003`); `H2-08`, `AF-08`, `AF-09`, `RSK-036` |
| `D-015` | `D-15` | Confirm whether the Company is a *significant data fiduciary* and, if so, appoint a Chief Data Officer | **CEO**, on Legal advice | 2026-08-12 | W4 − 3 months | **OPEN** | `RSK-034`; `DEP-32`; the BDT 50 lakh penalty tier |

### 5.3 `D-014` in full — the decision the programme has been citing

Recorded at full schema depth because two audits cite it, `AUDIT-001` established that it could
not be located, and it carries the largest financial consequence in the programme.

| Field | Value |
|---|---|
| `id` | `D-014` *(alias `D-14`)* |
| `title` | Accept the restated programme effort and cost position, or direct a descope |
| `raised` | 2026-08-13, by the Category H audit (`00-07` H2-08, remediation item 4) |
| `owner` | **Board**, on Steering Committee recommendation |
| `needed_by` | Before the next Board review — **originally "now", 5 days ago** |
| `status` | **ESCALATED**. Escalated 2026-08-13; **no record of receipt, consideration or decision exists** |
| `context` | The approved business case models 834 person-weeks across 30 modules. The architecture is now 67 modules and 12 portals. Three audits have measured or re-measured the effort and each returned a larger figure. `AUDIT-001` `AF-08` found three figures in simultaneous circulation with a 679 PW spread, escalated to a decision identifier that resolved to nothing |
| `options` | **(a)** Fund the counted position · **(b)** Phase the same scope across more waves, extending the horizon beyond 36 months · **(c)** Descope — Categories D, F, I or J are the candidates named in `RSK-036` · **(d)** Defer Waves 8 and 9, per `CON-01` and `06-01` §9 |
| `evidence` | `00-07` §4 H2-08; `AUDIT-001` §4 `AF-08`, `AF-09`; `PGD-AUDIT-001` `PGD-A1-05`; direct enumeration 2026-08-18 02:06 |
| `affects` | `GV-004` schedule · `GV-007` estimation model · `GV-008` cost baseline · `BM-003` business case · `CO-003` statement of work · `CO-005` TCO · `00-02` §6 · `06-02` §3.3 |
| `decision` | *(pending)* |

**The counted position placed before the decision-maker**, enumerated 2026-08-18 02:06 (+06):

| Component | Effort | Source | Ever presented to the Board? |
|---|---:|---|:--:|
| Approved business case | 834 PW | 30 modules, March 2026 | ✓ |
| Module build, counted from all 67 `Effort estimate` rows | **1,544 PW** | Direct sum | ✗ *(1,513 from 65 files was escalated, not decided)* |
| **Portal and application build**, counted from all 12 `Effort estimate` rows | **298 PW** | Direct sum | **✗ — never included in any effort figure** |
| **Total specified build** | **1,842 PW** | 1,544 + 298 | ✗ |
| Content estate | 520 – 775 PW | `AF-09` | ✗ — escalated, never absorbed |
| 127 unwritten guiding documents | *not estimated* | `PGD-A1-05` | ✗ |
| ~660–1,500 screens of UX design | *not estimated* | `PGD-A1-05` | ✗ |

> **The variance is no longer 1,513 against 834.** On the counted build alone it is **1,842 against
> 834 — 2.2×**. With content it is **2,362–2,617 PW, 2.8×–3.1×**. `GV-007` adds the two unestimated
> streams and `GV-008` converts the result to money. **Presenting `D-014` on the 1,513 figure would
> understate it by 22% before content is counted at all.**

### 5.4 New decisions raised by Category 00 — `D-016` … `D-024`

Raised because authoring `GV-001`…`GV-011` surfaced choices no existing document had identified.
All are allocated on the date of this issue and are `OPEN`.

| ID | Title | Owner | Needed by | Why it is a decision, not an assumption |
|---|---|---|---|---|
| `D-016` | **Whether portal and application effort is inside or outside the build baseline** | Steering Committee → Board | Before `GV-008` | 298 PW of specified work has never appeared in an effort figure. If it is *inside* the 834 PW, the module figure is overstated; if *outside*, the baseline is understated by 22%. It cannot be both, and no document says which |
| `D-017` | **Whether Waves 5–9 are authorised now or re-authorised at the Wave 4 gate** | Board | At charter approval | `GV-001-D-02` proposes the latter. It halves what the Board is being asked to authorise against the least reliable estimate, and it is a Board choice, not an authoring one |
| `D-018` | **Whether a benefit with no measured baseline may be claimed** | Board | Week 4 | `06-02` §6 states the rule; `RP-02` showed **44 of 95 baselines absent**, restated by `BM-002` §3.4 to **71 of 95**. Roughly **BDT 396 lac** of the BDT 876 lac case depends on the answer. The rule currently has no enforcer |
| `D-019` | **Which module identifiers the wave plan refers to** | ARB → Steering Committee | **Before Wave 1 planning is fixed** | `06-01` schedules `M20` meaning *Billing, Revenue Recognition & Settlement*; in the 67-module architecture `M20` is *Accounts Receivable, Invoicing & Collections* and settlement is `M53`. `M30` means *Platform Administration & Multi-Entity*; multi-country is now `M65`. **The delivery plan's module references are ambiguous.** See `GV-004` §5.3 |
| `D-020` | **Where the 37 unscheduled modules (`M31`–`M67`, 763 PW) are placed in the wave plan** | Steering Committee | Before `GV-004` is baselined | `06-01` allocates waves to `M01`–`M30` only. **49% of module effort has no wave.** `C-02` identified the register gap; the *schedule* gap has not previously been quantified |
| `D-021` | **Whether the 127 unwritten guiding documents are a funded workstream** | Board, on `GV-007` | Week 6 | `PGD-A1-05`, open. They are chartered nowhere, in no wave, with no owner (`GV-001` `Q-05`) |
| `D-022` | **Whether independent assurance is internal-but-separate, or external** | Audit Committee → Board | Week 6 | `R-07`. Internal-but-separate is cheaper and weaker; four audits by the authoring function is the alternative that has already been tried |
| `D-023` | **Whether ratifying `RG-08` (timestamped enumeration) is mandatory across all four repositories or only this one** | PMO → Steering Committee | Week 2 | Baseline movement during authoring has now occurred **three** times. `GV-001` `CC-06`. A rule that binds one repository does not prevent the other three from moving under it |
| `D-024` | **Whether `TD-01`…`TD-15` are migrated into `AR-004` ADRs or retained in `02-05`** | ARB | Before `AR-004` is issued | Fifteen technology decisions currently sit in a table with one-line reasons and no rejected-option analysis. Migration preserves rationale; retention preserves citations. Both are defensible; neither is decided |

### 5.4a Decisions raised by the Technology Stack Specification — `D-025` … `D-027`

> **`GV-003-F-01` (HIGH, raised 2026-08-19).** `primary-doc/1000FiX_ERP_Technology_Stack_Specification.md`
> §25.2 and §24 allocate **`D-15`, `D-16` and `D-17`** to three technology decisions. **§2.2 of this
> document does not list that specification as a source, and none of the three has ever been
> registered here.** Worse, all three identifiers are **already taken**: this log allocates `D-015`,
> `D-016` and `D-017` to entirely different decisions, and `DL-05` records `D-15` as an explicit
> **alias** for `D-015`.
>
> **A reader following the Technology Stack Specification's `D-15` lands on the data-fiduciary
> decision, not the Odoo upgrade slot.** This is the `H-03` / `H2-04` / `AP-02` defect class — a
> shared identifier space with no allocating authority — occurring **between two repositories**.

| Collision | Technology Stack Specification | **This log** |
|---|---|---|
| `D-15` | Odoo version baseline and upgrade slot (§4.4) | Significant data fiduciary / appoint a CDO |
| `D-16` | Next.js 15 → 16 upgrade timing (§11.1) | Portal effort inside or outside the build baseline |
| `D-17` | P07 mobile surface — PWA, Flutter or React Native (§11.9) | Waves 5–9 authorised now or re-authorised at the W4 gate |

**Re-registered here under `DL-01` (this log is the sole allocating authority for `D-nnn`).**
`D-025`…`D-027` were verified free across all four repositories at **2026-08-19 18:46 (+06)**.

| ID | Title | Owner | Needed by | Why it is a decision, and what has changed since it was raised |
|---|---|---|---|---|
| `D-025` | **Odoo version baseline and the major-version upgrade slot** *(was `D-15` in the Technology Stack Specification §4.4, §25.2.1)* | CTO → Steering Committee | **Wave 0** | Baseline is **Odoo 19.0** (released 18 Sep 2025, supported to ~Sep 2028). **Verified 2026-08-19: Odoo 20 is released at Odoo Experience, Brussels, 24–26 September 2026 — five weeks from this issue.** The specification recommends one upgrade slot between W5 and W6. A 36-month programme otherwise reaches steady state within a year of 19.0 leaving support |
| `D-026` | **Next.js 15 → 16 upgrade timing** *(was `D-16`, §11.1, §25.2.2)* | CTO | **Wave 0 — the date has moved** | **Verified 2026-08-19: Next.js 15 reaches end of life on 21 October 2026**, and 16.3 is current (released 3 Aug 2026). The specification's *"leaving the supported line during the programme"* is now precise and much nearer: **EOL falls inside Wave 1 (months 1–4)**. Six customer-facing surfaces — `P01`, `P03`, `P04`, `P06`, `P10`, `P12` — are specified on 15. Deferring means building six applications on an unsupported framework and migrating them together |
| `D-027` | **`P07` mobile surface — PWA now, Flutter later, or React Native** *(was `D-17`, §11.9, §25.2.5)* | CTO | Wave 6 | The estate must not acquire a **second mobile framework by default**. Flutter is the single framework for the other four apps (3.44 current). React Native's legacy architecture was removed at 0.83, so adopting it means adopting the New Architecture outright. The specification recommends PWA in W7 |

> **`DL-08` (new).** **The Technology Stack Specification is added to §2.2 as a decision source.** Any
> `D-nn` it or any other document outside this log allocates is **not a programme decision** until
> re-registered here. `RR-002` records `D-nnn` as belonging to this log; that rule was correct and
> was not being enforced across repository boundaries.
>
> **Change request to the source.** `primary-doc/…Technology_Stack_Specification.md` §24 and §25.2
> should cite `D-025`, `D-026`, `D-027`. Raised as `GV-005` `ISS-nnn`; this log cannot edit
> `primary-doc`.

### 5.5 Decisions taken elsewhere and cross-referenced

Recorded so the log is complete, and so that nobody concludes the programme has made **no**
decisions. These fifteen were taken; they are technology decisions in a separate space.

| Space | Count | Location | Disposition |
|---|---:|---|---|
| `TD-01` … `TD-15` | 15 | `02-05` §10 | Valid. Migration to `AR-004` is `D-024`. **Each carries a one-line reason and no rejected-option analysis** — `AR-004`'s stated purpose |

### 5.6 Log summary

Regenerated by counting the rows of §5.2, §5.4 and §5.4a immediately before issue, per rule `PG-M10`.

| Status | Count |
|---|---:|
| `OPEN` | **26** |
| `ESCALATED` | **1** *(`D-014`)* |
| `DECIDED` | **0** |
| `DEFERRED` | 0 |
| `SUPERSEDED` | 0 |
| `WITHDRAWN` | 0 |
| `UNRECOVERABLE` | 0 |
| **Total** | **27** |

> **Zero decisions taken.** Verified by counting the Status column of §5.2 (15 rows: 14 `OPEN`,
> 1 `ESCALATED`), §5.4 (9 rows, all `OPEN`) and **§5.4a (3 rows, all `OPEN`)**. 14 + 9 + 3 = 26
> `OPEN`; + 1 `ESCALATED` = **27** = the row
> count. This is the single most important number in Category 00: **a 36-month programme,
> 610 documentation files, five months of work, and not one recorded decision.**

---

## 6. Change Control Procedure

### 6.1 What is under change control

> **Rule `CC-01` — nothing is under change control until it is baselined, and everything baselined
> is under change control.**

| Baseline | Established by | Baselined when | Changed by |
|---|---|---|---|
| **Charter baseline** | `GV-001` | Board approval | Board decision only |
| **Scope baseline** | `GV-006` | Steering Committee approval of the module/portal set | `CR` → Steering Committee |
| **Requirements baseline** | `RQ-001` SRS | Steering Committee approval | `CR` → Steering Committee (P0/P1) or CAB (P2/P3) |
| **Architecture baseline** | `AR-001` SAD + `AR-004` ADRs | ARB approval | ADR supersession + `CR` where cost/schedule affected |
| **Schedule baseline** | `GV-004` | Steering Committee approval | `CR` → Steering Committee if a gate date moves; PMO within wave tolerance |
| **Cost baseline** | `GV-008` | Board approval | `CR` → Board on tolerance breach; Steering Committee within |
| **Configuration baseline** | `GV-011` | Per configuration item | Per `GV-011` §change control |
| **Content baseline** | `CG-006` | Per content file at `Approved` | `CG-006` §6, logged in `RF-006` |

### 6.2 The procedure

```
  ┌────────────┐
  │  RAISE     │  Anyone may raise. PMO allocates CR-nnn within 1 working day.
  └─────┬──────┘  A change not raised in writing does not exist.
        ▼
  ┌────────────┐  Mandatory, all six dimensions. An assessment that omits a
  │  ASSESS    │  dimension is returned, not approved:
  └─────┬──────┘  scope · cost · schedule · risk · benefit · COMPLIANCE
        ▼
  ┌────────────┐  Against §6.3. The classification determines the authority,
  │  CLASSIFY  │  and the authority may not be chosen by the raiser.
  └─────┬──────┘
        ▼
  ┌────────────┐  The empowered body decides: APPROVE · REJECT · DEFER ·
  │  DECIDE    │  APPROVE WITH CONDITIONS. Recorded as a D-nnn if approved.
  └─────┬──────┘
        ▼
  ┌────────────┐  Baseline updated · every affected document versioned in the
  │  APPLY     │  SAME change · impact list from §6.5 worked through
  └─────┬──────┘
        ▼
  ┌────────────┐  PMO verifies the baseline and the documents actually moved.
  │  VERIFY    │  An approved change that was never applied is the most common
  └────────────┘  failure mode and the hardest to detect later.
```

### 6.3 Classification and authority

| Class | Definition | Authority | SLA |
|:--:|---|---|---|
| **C1** | Changes a chartered objective, a programme tolerance, or the scope of a module category | **Board** | Next Board meeting; emergency by written procedure |
| **C2** | Affects a **P0 or P1** requirement · cross-module · any cost impact · moves a wave gate date · changes a published API contract | **Steering Committee** | Next monthly meeting |
| **C3** | **P2/P3** within a module · cross-module with no cost and no wave impact · reallocation inside a tranche | **Change Advisory Board** | Next fortnightly meeting |
| **C4** | Architecture standard, technology selection at L4/L5, module boundary | **Architecture Review Board** | Next fortnightly meeting; 48 h for a blocking decision |
| **C5** | Editorial, non-substantive, no meaning change *(`CG-006` §2.1 MINOR test)* | **Document owner**, notify PMO | 2 working days |
| **C6** | **Emergency production change** | **CTO**, retrospective Steering review | Immediate; recorded within 24 h |

> **Rule `CC-02` — the raiser does not classify.** The PMO classifies on receipt of the impact
> assessment. Self-classification is how C2 changes become C3 changes.

### 6.4 The four standing rules

Carried from `00-04` §5.4 and made enforceable:

| Rule | Provision | Enforcement |
|---|---|---|
| `CC-03` | **No change is implemented before it is approved and recorded** | A build ticket with no `CR-nnn` or `D-nnn` is rejected at code review (`BE-003`) |
| `CC-04` | **No wave absorbs a change mid-wave.** Approved changes enter the next wave | Sprint planning admits only wave-scoped items; `GV-009` gate evidence includes the change log |
| `CC-05` | **A change that removes scope must state which benefit is forgone** | The impact assessment's benefit dimension is mandatory. `BM-004` is updated in the same change |
| `CC-06` | **The change log is reviewed at every Steering Committee meeting** | Standing agenda item; ageing report |
| `CC-07` *(new)* | **A change affecting personal data processing requires a Data Protection Forum opinion before decision** | The compliance dimension of the impact assessment names the forum's opinion or states why none is required |

### 6.5 The impact list

Adopted from `CG-006` §6.2, which solved this problem for content. Before a change is approved,
the assessment must enumerate what cites the thing being changed.

| Change to | Impact list must include |
|---|---|
| A requirement | Every design element, test case, content file and KPI tracing to it (`RQ-004`, `RF-003`) |
| An identifier | Every file citing it — the estate has seven identifier spaces and no index (`RR-006`) |
| A module boundary | Both modules' specifications, `05-02` entity ownership, `05-03` interfaces, `05-05` rules |
| A schema element | `DA-001`, `DA-002`, every consuming API contract, every migration mapping in `DM-*` |
| A published API | Every registered consumer; the deprecation notice period in `IN-005` |
| A statutory position | Every content file with a `statutory pin` (`CG-006` §4); `SC-008`; `RR-005` |
| A wave allocation | `GV-004` critical path, capacity check, and every dependency in `GV-005` |

> **Until `RR-006` (Master Cross-Reference Index) exists, the impact list is produced by search
> and is therefore incomplete by construction.** That is stated here rather than assumed away.
> `AF-14` — four module files citing a path that will break — is what an incomplete impact list
> looks like after the fact.

### 6.6 Applying a change

| Step | Requirement |
|---|---|
| 1 | The baseline is updated **and its version incremented** per `GV-011` |
| 2 | **Every** document on the impact list is versioned in the **same** change. A change applied to five of seven affected documents leaves two describing a system that no longer exists |
| 3 | The `PGD-000` register row is updated where a guiding document's status changes, with a fresh enumeration **timestamp** (`PG-M11`) |
| 4 | The change is communicated to every consulted party in the impact assessment |
| 5 | The PMO **verifies** — reads the changed documents and confirms the change is present |

### 6.7 Change budget and contingency

| Provision | Value |
|---|---|
| Wave contingency | **20% on Waves 5–8** per `RSK-005`, which records that the new business lines have no delivery precedent |
| Change budget | Held by the Steering Committee within programme cost tolerance (`GV-001` §8.1: +10%) |
| Rule `CC-08` | Contingency draw requires a `CR` and is reported to the Board quarterly. **Contingency consumed without a change request is a cost overrun that has not been recognised yet** |

### 6.8 Emergency and retrospective change

| Provision | Rule |
|---|---|
| Who may authorise | CTO, or the Major Incident Manager during a declared Sev-1 |
| Bound | Only what is necessary to restore service or prevent harm |
| Recording | `CR-nnn` allocated and impact assessment completed **within 24 hours**, retrospectively |
| Review | Retrospective Steering Committee review at the next meeting; a pattern of emergency change is a `GV-005` issue |
| Prohibition | An emergency change **may not** be used to introduce scope. A scope change disguised as an emergency is a governance breach, reported to the Audit Committee |

---

## 7. The Change Log

### 7.1 `CR-nnn` identifier space

| Rule | Provision |
|---|---|
| `CL-01` | PMO is the sole allocating authority |
| `CL-02` | Allocated on **raise**, not on approval — so that rejected and withdrawn changes remain visible |
| `CL-03` | Permanent; never reissued |
| `CL-04` | An approved `CR` produces exactly one `D-nnn`, cross-referenced in both directions |

### 7.2 Change log

| CR | Title | Raised | Class | Status | Decision | Baselines affected |
|---|---|---|---|---|---|---|
| — | *No change request has been raised. Scope has moved **11 → 30 → 67 modules** and **6 → 12 portals** with **no change-control artefact of any kind**.* | — | — | — | — | — |

> **This empty table is the finding.** `RSK-002` (scope creep) is rated **Critical** and its stated
> mitigation is *"formal change control"*. The scope has tripled twice and the change log is empty.
> `GV-006` §4 retrospectively baselines the three scope positions so that the **fourth** expansion
> — whenever it comes — can be distinguished from creep. It cannot be distinguished today.

### 7.3 Change reporting

| Report | Frequency | Content |
|---|---|---|
| Change pipeline | Weekly to PMO | Raised, in assessment, awaiting decision, approved-not-applied |
| **Approved-not-applied ageing** | Weekly | The highest-risk state. An approved change nobody applied is invisible until something breaks |
| Change log review | Every Steering Committee | Standing item, `CC-06` |
| Cumulative scope movement | Per wave gate | Against the `GV-006` baseline — the measurement `RSK-002` needs and has never had |
| Contingency drawdown | Quarterly to Board | `CC-08` |

---

## 8. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-003-D-01` | Whether to combine the decision log and change control | Two documents · One | **One** | An approved change *is* a decision. Splitting them produces approved changes with no decision and decisions applied to no baseline | A longer document; one mechanism |
| `GV-003-D-02` | How to handle `D-01` vs `D-001` | Keep short form · Renumber · Normalise with an alias column | **Normalise, alias retained** | `RG-02` forbids renumbering. An alias is a rendering, not a reallocation, and every existing citation still resolves | §5.2 carries an Alias column permanently |
| `GV-003-D-03` | Whether to record the reconstructed decisions as `OPEN` or infer what was decided | Infer from later documents · Record as found | **Record as found: `OPEN`** | Inferring a decision from a document that assumed it is how `AF-04` became invisible for two audits. Not one of the fifteen has a minute | The log's headline is *zero decisions taken*, which is accurate and uncomfortable |
| `GV-003-D-04` | Whether to absorb `TD-01`…`TD-15` into this log | Absorb · Cross-reference | **Cross-reference; migration is `D-024`** | Absorbing them would reallocate identifiers cited across the estate | The log is not the only place decisions live, and §3.2 says so |
| `GV-003-D-05` | Whether to raise `D-016`…`D-024` | Note them in prose · Allocate identifiers | **Allocate** | `DL-04`: an identifier is allocated when a decision is *raised*. Nine choices surfaced by this category's authoring would otherwise be prose nobody tracks | The open queue grows from 15 to 24, which is the true position |

---

## 9. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Were any of `D-001`…`D-015` in fact taken verbally or by email between 2026-08-12 and today? | Programme Director | Week 1 | If so, they must be minuted retrospectively; if not, §5.6's "zero decided" stands |
| `Q-02` | Does the Board have a written-procedure mechanism for decisions between quarterly meetings? Six of the fifteen are Board decisions and three are needed before kickoff | Company Secretary | Week 2 | `D-001`, `D-002`, `D-013`, `D-014` |
| `Q-03` | Who is the PMO configuration librarian who will hold this log? The role is named in `GV-002` §4.6 and does not exist | Programme Director | Week 2 | `DL-01`, `DL-07` |
| `Q-04` | Should `RF-006` (content decision log) merge into this log once the Content Council is constituted? | Programme Content Lead + PMO | Week 8 | Two logs is a divergence risk; one log is a bottleneck |

---

## 10. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every decision cited anywhere in the estate resolves to a row in §5 | `D-01`…`D-15` traced to `00-04` §6; `D-14` additionally to `00-07` H2-08 |
| `AC-02` | Any decision that could not be reconstructed is marked `UNRECOVERABLE` | Zero unrecoverable; method stated at §5.1 |
| `AC-03` | The `D-nnn` space has a single named allocating authority | `DL-01` |
| `AC-04` | The template collision that would produce 140 documents each with a `D-01` is closed | `DL-06`; finding `PGD-A2-03`; template corrected |
| `AC-05` | Every decision has an owning **body**, not merely an owning role | §5.2, §5.4 — owners resolve to `GV-002` §5.2 |
| `AC-06` | The log summary is regenerated by counting rows, not carried forward | §5.6 verification note, per `PG-M10` |
| `AC-07` | Change classification determines authority, and the raiser cannot choose it | `CC-02` |
| `AC-08` | Every effort figure quoted is enumerated at the time of writing | §5.3, enumerated 2026-08-18 02:06 (+06) |
| `AC-09` | The empty change log is stated as a finding, not left as an empty table | §7.2 |

**Definition of done.** Complete when every criterion is met, the Steering Committee has adopted
the procedure at its first meeting, `D-013` and `D-014` have a recorded decision, and `PGD-000`
records `GV-003` as ✅ with a fresh enumeration timestamp.

---

## 11. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-001`](GV-001_Programme_Charter_and_Mandate.md) | Condition `CC-03` requires this log |
| Upstream | [`GV-002`](GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) | Supplies the empowered body for every decision |
| Downstream | [`GV-004`](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) | `D-019`, `D-020` block the schedule baseline |
| Downstream | [`GV-006`](GV-006_Scope_Management_and_Baseline_Control_Procedure.md) | Uses this procedure; retrospectively baselines the three scope positions |
| Downstream | [`GV-007`](GV-007_Estimation_Model_and_Resource_Plan.md) · [`GV-008`](GV-008_Programme_Budget_and_Cost_Baseline.md) | `D-014`, `D-016`, `D-021` are their inputs |
| Downstream | `AR-004` | ADRs carry the technical reasoning; this log records that the decision was taken |
| Downstream | `CO-003` | A scope change outside this procedure is not a contractual variation |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` §5.4, §6 | The procedure and the fifteen decisions this document formalises |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05` §10 | `TD-01`…`TD-15`, cross-referenced not absorbed |
| Lateral | `../../project_content/99_Reference_and_Registers/RF-006` | The content decision log — parallel, deliberately separate |

---

## 12. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) ·
[`_templates/TPL_Guiding_Document.md`](../_templates/TPL_Guiding_Document.md) *(corrected at this issue)*

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-01` §6, `00-04` §5.4 §6, `00-06` §8, `00-07` §7 ·
`../../1000fix_ERP_Module/02_Architecture/02-05` §10 ·
`../../project_content/_AUDIT/AUDIT-001` §3 `AF-04`, §8 `R-02` ·
`../../project_content/00_Content_Governance_and_Standards/CG-006` §6

**External standards** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| ISO 10007:2017 §5.3 change control, §5.4 status accounting — configuration management planning, identification, change control, status accounting, audit | §6, §7 |
| ISO 21502:2020 §7.5 | Change classification |
| ISO 9001:2015 §7.5.3 | Controlled documented information; version management |
| PRINCE2 7th Edition (2023) — issue and change control; change authority; change budget | §6.3, §6.7 |
| PMBOK Guide 7th Edition — integrated change control | §6.2 |

---

## 13. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Programme Management Office | Initial issue. **Closes critical finding `AF-04`.** Reconstructs `D-001`…`D-015` (0 unrecoverable, 0 decided); raises `D-016`…`D-024`; establishes the `D-nnn` and `CR-nnn` spaces and their allocating authority; closes the template decision-identifier collision `PGD-A2-03` | *pending Steering Committee* |

---

*`GV-003` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
