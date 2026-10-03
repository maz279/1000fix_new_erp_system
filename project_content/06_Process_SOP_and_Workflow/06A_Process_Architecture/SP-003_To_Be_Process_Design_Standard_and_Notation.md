---
id: SP-003
title: To-Be Process Design Standard and Notation
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Business Process Lead
author: Business Process Lead with Content Design
reviewers: [Enterprise Architecture, Quality Manager, Programme Content Lead, Content Design Lead, Training Lead]
approver: Business Process Lead
content_class: E
purpose: >
  Fixes the notation, decomposition depth, naming, swimlane conventions, RACI embedding and
  versioning for every process artefact the programme produces. Sixty-seven modules' worth of
  process design authored to different conventions by internal analysts, an implementation
  partner and branch subject-matter experts cannot be compared, reviewed, tested against or
  trained from.
traces_to: [SP-001, SP-002, SP-004, SP-005, SP-006, CG-003, CG-004, CG-005, CG-006, CG-009, 05-04, 05-05]
priority: P2
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: OMG Business Process Model and Notation (BPMN) 2.0.2 specification — element set, pool/lane semantics, gateway types
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 4.4.1 — determine processes, their sequence and interaction, criteria and methods
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §1 BR-STD-01…BR-STD-07 rule standards and H/A/S/C classification
    verified: 2026-08-15
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-009_Content_Template_Register.md §3 — SP-001…SP-006 use template 1, SP-007…SP-034 use template 6
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SP-003 — To-Be Process Design Standard and Notation

> **This file is a constraint, not a suggestion.** A process artefact that does not conform is
> rejected at review under `CG-008`, in the same way a content file that ignores its template is
> rejected. The cost of enforcing this is a few hours per author. The cost of not enforcing it is
> a process library nobody can read.

---

## 1. Purpose

Process design for this programme will be authored by at least four groups working in parallel:
the internal Business Process Lead, an implementation partner's consultants, module business
owners, and branch subject-matter experts describing their own work. Without a fixed standard
they will produce, for the same process:

- one BPMN diagram, one flowchart, one numbered list and one slide;
- four different names for the same decision point;
- swimlanes that variously mean a role, a department, a system and a branch;
- decision gateways whose branches do not exhaust the possibilities, so real cases fall through;
- RACI stated in three artefacts, in two of which it disagrees with `05-04`.

That is not a hypothetical risk for this programme. The module repository has already recorded
four identifier-collision audits caused by the same absence of an up-front convention. This file
applies the lesson to process content before the artefacts exist rather than after.

---

## 2. Scope

**In scope**

- Notation: which diagram language, which element subset, which is forbidden.
- Decomposition: how many levels, what belongs at each, when to stop.
- Naming: process, step, decision, role, system and artefact names.
- Swimlanes: what a lane means, how many are allowed, ordering.
- RACI embedding: where accountability is stated and where it must not be restated.
- Rules and controls: how a `BRU-` rule, an `SOD-` control or an approval limit appears in a process artefact.
- Versioning, review and the source-of-truth relationship between diagram and text.

**Out of scope**

| Not covered here | Owned by |
|---|---|
| The value streams themselves | `SP-001` |
| The current state | `SP-002` |
| Approval values and delegation | `SP-004` |
| Escalation destinations and timers | `SP-005` |
| Incompatible duty pairs | `SP-006` |
| Prose style, sentence case, terminology | `CG-003`, `CG-004` |
| Content IDs and file naming | `CG-005` |
| Which template each file uses | `CG-009` |

---

## 3. Audience

Every person who authors, reviews or approves a process artefact for this programme: internal
analysts, implementation-partner consultants, module business owners, branch SMEs describing
their own work, the Quality Manager maintaining the ISO 9001 process library, and the training
and test designers who consume the output.

---

## 4. Content

### 4.1 The decision that governs everything else — text is the source of truth

**Rule PD-01.** For this programme, **the SOP text is authoritative and the diagram is
derivative.** Where a diagram and its SOP disagree, the SOP governs and the diagram is corrected.

Why, stated plainly, because the opposite convention is common:

| Argument for diagram-authoritative | Why it was rejected here |
|---|---|
| Diagrams are faster to read | True, and they remain the primary reading aid. But they are not translatable into Bengali without redrawing, and 28 of 34 `SP` files are bilingual (`CG-010` §3.2) |
| Diagram tools generate executable models | 1000FiX is implementing on Odoo, not a BPM engine. No diagram in this programme executes |
| Diagrams are precise | A gateway with unlabelled branches is not precise. Text forces the author to state the condition |
| Auditors want diagrams | ISO 9001:2015 does not require diagrams at all. It requires documented information sufficient to have confidence the process is carried out as planned (clause 4.4.2) |

Consequence: a process without a diagram is acceptable. **A process without conforming text is
not.** Diagrams are produced for L1 and for any L2 with three or more parallel paths (§4.3).

### 4.2 Notation — a constrained BPMN subset

Where a diagram is drawn, it uses **BPMN 2.0** with the element subset below. BPMN was chosen
over flowchart or UML activity notation because it is the only one of the three with agreed
semantics for the two things this business actually has trouble with: **message flows to
external parties** (customer, brand, courier, seller) and **boundary events on a timer** (SLA
escalation).

**Permitted elements**

| Element | Use for | Notes |
|---|---|---|
| Pool | An organisation: 1000FiX, Customer, Brand Partner, Vendor, Courier, Marketplace Seller | External pools are drawn collapsed — we do not model another party's internals |
| Lane | A **role** from `05-04` — never a department, never a system | §4.5 |
| Task (User) | A human step | Default |
| Task (Service) | A step the system performs unattended | Must cite an `AUT-nnn` from `05-05` §12 |
| Task (Manual) | A physical step with no system record at the time | e.g. sealing a consignment |
| Sub-process (collapsed) | An L2 process referenced from an L1 diagram | Must name the SOP that expands it |
| Exclusive gateway (XOR) | A decision with exactly one outcome | Every branch labelled; branches must be exhaustive (§4.6) |
| Parallel gateway (AND) | Genuinely simultaneous paths | Rare; do not use for "either order" |
| Event: start / end | | Every end event is typed and named (§4.6) |
| Event: timer (boundary, interrupting) | SLA and expiry behaviour | Must cite the source of the duration — `MD-028`, `SP-005` or a `BRU-` rule |
| Event: message (send/receive) | Communication crossing a pool boundary | Must cite the `NT-nnn` message library entry |
| Event: error (boundary) | An exception path | Must correspond to a row in the SOP's §8 exception table |
| Data object | A document produced or consumed | Must cite a `DT-nnn` |
| Text annotation | A rule or control marker | §4.7 |

**Forbidden**

| Forbidden | Why |
|---|---|
| Inclusive gateway (OR) | Ambiguous in practice; readers and implementers disagree on its semantics. Model as explicit XOR branches |
| Complex gateway | Same reason, worse |
| Event sub-process, compensation, transaction | Not implementable in this stack; models an intention that will not exist |
| A lane that is a system | Systems are named on the task, not as a lane. A lane is who is accountable |
| An unlabelled sequence flow leaving a gateway | The most common real-world defect; makes the diagram unreviewable |
| Colour carrying meaning | Fails `CG-011` accessibility. Meaning is carried by shape, label and annotation; colour may only reinforce |
| A diagram with no matching SOP text | `PD-01` |

### 4.3 Decomposition — four levels, and when to stop

Levels are as defined in `SP-001` §4.1. This file adds the stopping rule.

| Level | Granularity | Artefact | Diagram? |
|---:|---|---|---|
| **L0** | Value stream | `SP-001` §4.3 map | One per programme |
| **L1** | Stage | `SP-001` §4.4–4.8 tables | One diagram per stream |
| **L2** | Process | An SOP in `06B` | Only where three or more parallel paths exist |
| **L3** | Activity / step | A row in that SOP's §5 step table | Never |

**Rule PD-02 — the stopping rule.** Decompose one level further only if the answer to all three
is yes:

1. Does the next level change **who** does the work, **where** it is done, or **what system** records it?
2. Would a competent new joiner get it wrong without that level of detail?
3. Is the detail **stable** — will it survive a configuration change?

If the detail is unstable (a screen layout, a menu path, a field position) it does not belong in
a process artefact at all. It belongs in the UI copy pack (`UI-023`…`UI-036`) or the training
job aid (`TR-*`), which are re-issued per release. **Process documents that describe screens
become wrong at the first release and are then distrusted entirely.**

**Rule PD-03 — step-count bound.** An L2 process with more than **20 steps** in its §5 table is
either two processes or is documenting L3 detail. Split it or raise the abstraction. An L2
process with fewer than **4 steps** is a step of something else and should not have its own SOP.

### 4.4 Naming

**Rule PD-04.** Names come from `CG-004` controlled vocabulary. A process artefact may not
introduce a business-object synonym. "Job", "ticket", "case" and "request" are not
interchangeable with `service order`.

| Artefact | Pattern | Good | Bad |
|---|---|---|---|
| Value stream | `<noun>-to-<noun>` | Request-to-cash | Customer journey |
| Stage (L1) | `<Verb> <object>` | Take custody | Custody |
| Process (L2) | `<Verb> <object>` — matches its SOP title | Issue a repair estimate | Estimation process |
| Step (L3) | `<Imperative verb> <object>` | Capture device IMEI and condition | IMEI |
| Decision | A **question with a yes/no or enumerated answer** | Is the estimate above BDT 25,000? | Value check |
| End event | `<Object> <past-participle state>` | Service order completed | End |
| Role | The exact `05-04` label, with its `Rnn` | R08 Service Centre Agent | Front desk staff |
| System | The exact `Mnn`/`Pnn` and its register title | `M15` Spare Parts and Inventory Management | Inventory system |
| Document | The exact `DT-nnn` and title | `DT-002` Service Intake Receipt | Intake form |

**Rule PD-05.** A step name never contains "and" joining two verbs. `Inspect and accept the
goods` is two steps with two different failure modes and, frequently, two different people.

### 4.5 Swimlanes

**Rule PD-06.** A lane is a **role** from `05-04`, labelled with its `Rnn` and its canonical
name. Not a department. Not a system. Not a person. Not a branch.

**Rule PD-07.** Maximum **six lanes** per diagram. A process touching more than six roles is
above L2 and belongs at L1 with collapsed sub-processes.

**Rule PD-08.** Lane order, top to bottom: **customer or external party → front-line → supervisory
→ specialist → back office → system**. Consistent ordering means a reader can find the
accountable role without reading every label.

**Rule PD-09.** Where the same person commonly holds two lanes at small sites (the C4 and C5
clusters in `SP-002` §4.3), the diagram still shows two lanes and the SOP records the
role-doubling in its §11 segregation-of-duties table with the compensating control from
`SP-006`. **The design is not degraded to match the smallest site.**

### 4.6 Decisions and end states

**Rule PD-10 — exhaustive branches.** Every gateway's branches must cover every possible answer.
The reviewer's test is: *name a real case that takes none of these branches.* If one exists, the
gateway is wrong. The most common miss in service processes is the third answer:

| Decision | Usual branches | The missing branch |
|---|---|---|
| Did the customer approve the estimate? | Yes / No | **No response by expiry** (`BRU-SRM-13` — expired estimates are re-issued, not extended) |
| Is the part in stock? | Yes / No | **In stock elsewhere in the network** (`AUT-007`) |
| Did the repair succeed? | Yes / No | **Beyond economic repair** (`BRU-SRM-12` — requires photographic evidence and a second technician) |
| Did the customer collect the device? | Yes / No | **Uncollected at 30 days → abandonment process** (`BRU-SRM-16`) |
| Was the visit completed? | Yes / No | **Customer not present / access refused** (`BRU-FSM-09` — geotagged evidence required) |

**Rule PD-11 — typed end events.** Every end event names the resulting state using the exact
label from `MD-027` Status and Lifecycle State Label Register. A process ending in "Done" is not
designed; the system has no such state.

**Rule PD-12 — the unhappy path is not optional.** Every L2 process artefact carries at least one
exception path, and it matches the SOP's §8 exception table row for row. A process with only a
happy path has not been designed, it has been imagined.

### 4.7 How rules, controls and authority appear

**Rule PD-13 — cite, never restate.** A process artefact **references** a rule by identifier and
never paraphrases it. Paraphrase creates a second version that drifts.

| Thing | How it appears in a process artefact | Never |
|---|---|---|
| Business rule | `(BRU-SRM-07)` after the step or on a text annotation | The rule's wording, retyped |
| Rule class | Take it from `05-05` — **H** blocks, **A** overridable with approval, **S** warns, **C** computed | A new class |
| Approval limit | `per SP-004 §<band>` | A currency figure typed into the diagram |
| Segregation of duties | `(SOD-nn)` in the SOP's §11 table | A description of who cannot do what |
| Escalation | `per SP-005 §<path>` | A named individual or a timer typed inline |
| SLA duration | `per MD-028 <band>` | A number of hours typed inline |
| Notification | `(NT-nnn)` | Draft message text |
| Document | `(DT-nnn)` | A screenshot of the form |
| Automation | `(AUT-nnn)` | "the system does this automatically" |

**Rule PD-14 — no new identifiers.** A process artefact may not mint a `BRU-`, `SOD-`, `KPI-`,
`Rnn`, `NFR-` or any other programme-wide identifier. If the design needs one, it is registered
in its owning register first and cited here second. This is `RG-01` (register-first) from audit
`00-07`, extended to process content. **Ignoring it is precisely how `SOD-13`…`SOD-30` came to
exist as eighteen unregistered controls** — see `SP-006` §3.

### 4.8 RACI embedding

**Rule PD-15.** Accountability is stated **once**, in the SOP's §1 header table (process owner)
and §5 step table (`Who` column), using `05-04` roles. It is not restated in a separate RACI
matrix inside the same file.

**Rule PD-16.** Exactly one Accountable per process. If two functions claim it, that is escalated
under `SP-005`, not resolved by writing both names.

**Rule PD-17.** Where an SOP's `Who` column disagrees with `05-04`, **`05-04` governs** and the
SOP is corrected — or `05-04` is formally extended first. It is never resolved silently in the
SOP, and never by inventing an unregistered role. `00-07` H2-07 and the module-set audit A3-17
record `R39`–`R50` already used but unregistered; process content must not add to that list.

### 4.9 Versioning and lifecycle

Process artefacts follow the content lifecycle in `CG-006`. Two additions specific to process:

**Rule PD-18 — pin to the release that implements it.** An SOP describes a process the system
supports. It is pinned in front matter to the wave and, once the build exists, to the release.
An unpinned SOP describing behaviour the build does not have is worse than no SOP.

**Rule PD-19 — an SOP is not `Approved` until it has been walked.** "Walked" means executed
end-to-end by someone who did not write it, against the actual configured system in UAT, with
the walk recorded. This is the process equivalent of the `TS-` test evidence and is the entry
in the SOP's §14 revision history.

| State | Meaning for an SOP |
|---|---|
| `Draft` | Authored, conforms to this standard |
| `Review` | Under review by the process owner and affected roles |
| `Approved` | Walked in UAT, signed by the process owner, conformant to `CG-008` |
| `Published` | Issued to the branches in both languages, training delivered |
| `Superseded` | Replaced; archived under `_ARCHIVE/` with a `SUPERSEDED_` prefix (`CP-10`) |

### 4.10 Review checklist for a process artefact

The reviewer answers all fifteen. Any "no" blocks approval. This checklist is referenced from the
`CG-008` Definition of Done for `SP` files.

| # | Check |
|---:|---|
| 1 | Text exists and governs; any diagram matches it (`PD-01`) |
| 2 | Only permitted BPMN elements used; no OR/complex gateway, no system lane (§4.2) |
| 3 | Decomposition stops at the right level; 4–20 steps (`PD-02`, `PD-03`) |
| 4 | All names follow `CG-004` and §4.4; no verb-and-verb steps (`PD-05`) |
| 5 | Lanes are `05-04` roles, ≤ 6, in the standard order (`PD-06`…`PD-08`) |
| 6 | Small-site role-doubling handled by compensating control, not by degrading the design (`PD-09`) |
| 7 | Every gateway branch labelled and exhaustive; the "third answer" tested (`PD-10`) |
| 8 | Every end event uses an `MD-027` state label (`PD-11`) |
| 9 | At least one exception path, matching the SOP §8 table (`PD-12`) |
| 10 | Rules and controls cited by identifier, never paraphrased (`PD-13`) |
| 11 | No new programme-wide identifier minted (`PD-14`) |
| 12 | Accountability stated once, from `05-04`; exactly one Accountable (`PD-15`, `PD-16`) |
| 13 | Any `05-04` disagreement escalated, not resolved locally (`PD-17`) |
| 14 | Pinned to a wave/release (`PD-18`) |
| 15 | Walked in UAT before `Approved` (`PD-19`) |

### 4.11 Tooling

| Item | Decision | Rationale |
|---|---|---|
| Diagram format | BPMN 2.0 XML, exported to SVG for embedding | XML is diffable in version control; SVG is accessible and scales at 1366×768 branch hardware (`VB-003`) |
| Storage | Alongside the SOP, same stem, `.bpmn` and `.svg` | Mirrors the `MD` convention of data beside specification (Master Index §3.1) |
| Bengali diagrams | **Not produced.** The SVG carries English labels; the Bengali SOP text carries the translated step names | Redrawing 28 diagrams in Bengali doubles maintenance for no comprehension gain, since the text is authoritative (`PD-01`). Confirmed with Localisation Lead |
| Accessibility | Every embedded SVG carries a text alternative that is the SOP's §5 step table | `CG-011`; a diagram is never the only carrier of information |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`SP-001_Process_Architecture_and_Value_Stream_Map.md`](SP-001_Process_Architecture_and_Value_Stream_Map.md) | Supplies the L0/L1 structure this standard decomposes |
| [`../../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | `PD-04` naming draws from it |
| [`../../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md`](../../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) | States in §4.9 |
| [`../../00_Content_Governance_and_Standards/CG-009_Content_Template_Register.md`](../../00_Content_Governance_and_Standards/CG-009_Content_Template_Register.md) | Which template each `SP` file uses |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md) | End-event labels (`PD-11`) |
| `05-04` Role matrix | Lane identity and RACI |
| `05-05` Business rules and automations | Rule identifiers, classes, `AUT-nnn` |

| Depended on by |
|---|
| All 28 SOPs in `06B` · `SP-004`, `SP-005`, `SP-006` (citation conventions) · `TS-004` process test scripts · `TR-003` training design standard · `KB-001` knowledge architecture (shares the citation convention) |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually, and at every wave boundary while `06B` is being authored |
| Trigger for out-of-cycle review | A change to `CG-004`, `CG-006` or `CG-009`; adoption of a BPM tool; a reviewer finding a defect class this standard does not catch |
| Owner | Business Process Lead |
| Enforcement | `CG-008` Definition of Done references §4.10; a non-conformant artefact does not reach `Review` |
| Change control | Adding or removing a `PD-` rule requires Business Process Lead approval and an `RF-006` entry |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3)
- [x] Every factual claim carries a source and a verification date
- [x] Notation subset stated as permitted **and** forbidden, with reasons
- [x] Decomposition stopping rule stated and bounded (`PD-02`, `PD-03`)
- [x] Citation convention forbids paraphrase and forbids minting identifiers (`PD-13`, `PD-14`)
- [x] Reviewer checklist is complete and referenced by `CG-008`
- [x] Terminology matches `CG-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Ratified by the Business Owners Forum — **pending**
- [ ] Diagram tooling procured and the BPMN subset configured as a validation profile — **pending**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
