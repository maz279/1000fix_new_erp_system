---
id: RR-003
title: Document Standards and Template Library
category: 99 — Reference, Registers & Glossary
code: RR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture
approver: Chief Technology Officer
standards_basis: ISO/IEC/IEEE 15289:2019 · ISO 10007:2017 §5 · ISO 9001:2015 §7.5 · ISO/IEC/IEEE 12207:2017 §6.3.6 · ISO/IEC/IEEE 29148:2018 §9 · ISO/IEC/IEEE 42010:2022 · IEEE 1016-2009 · ISO/IEC/IEEE 29119-3:2021
traces_to: PGD-000 §0.3 test (c) · PGD-000 §0.5 "Until RR-003 publishes the per-document-type section sets… no ◐ may be promoted to ✅" · GV-011 §4, §5 · RR-002 RR-002-D-06 · _templates/TPL_Guiding_Document.md · PGD-A2-03 · PGD-A2-17
depends_on: PGD-000 · GV-011 · RR-002
verified_on: 2026-08-19
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
enumeration_timestamp: 2026-08-19 03:00 (+06)
rule_prefix: DSL — verified to return zero occurrences in identifier form across all 787 markdown files of the workspace before allocation, at 2026-08-19 03:00 (+06). Candidates DTL and DCS were also free; DTL was rejected as visually close to DT- (content estate document templates, 2,887 occurrences)
---

# RR-003 — Document Standards and Template Library
# 1000FiX ERP System & Portal Suite v2.0

### Category 99 · Code `RR` · ISO/IEC/IEEE 15289:2019 · ISO 10007:2017 · ISO 9001:2015 §7.5

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Registered in `PGD-000` as `RR-003`, status ⬜, `P1`, needed by `W1`.
> 2. **`PG-03` / `RG-06` Count, do not consult.** §8's conformance figures were measured across
>    every guiding document on disk at **2026-08-19 03:00 (+06)**; the commands are in §8.1.
> 3. **`PG-06` Cite standards.** ISO/IEC/IEEE 15289:2019 governs information-item content;
>    departures in §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-19`.

---

## 1. Purpose

`PGD-000` §0.3 defines a ✅ status with four tests, and test **(c)** reads: *"it covers ≥90% of the
section set its governing standard requires, counted section by section."* §0.5 then states the
consequence plainly:

> *"Until `RR-003` publishes the per-document-type section sets that the ✅ test (c) measures
> against, no ◐ may be promoted to ✅."*

**This document publishes those section sets.** §5 is the instrument: for each of eleven document
classes it states the sections the governing standard requires, which are mandatory, which are
conditional, and how the ≥90% is arithmetically computed. Until §5 existed, test (c) was an
assertion with no denominator — which is the same defect the estate found in its coverage
percentages (`TS-01`) and its identifier registers (`RR-002` `IDC-F-03`), one level up.

It also does the ordinary work of a template library: the house structure, the front-matter
schema, the review and approval workflow, and the status model — and it **measures how well the
125 documents already written conform**, which is the honest way to publish a standard against
work that already exists.

> **The order matters and is deliberate.** This document does not impose a new structure on 130
> written documents. It **derives** the house structure from what those documents already do
> (§8.2 measures 130 of 130 conformance on six of nine frame sections), ratifies it, and names the
> small number of divergences. A standard written in ignorance of the estate would produce 130
> non-conformances on day one and be ignored by day two.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **The per-document-type section sets** that `PGD-000` §0.3 test (c) measures against — §5 |
| 2 | The **universal frame**: nine sections every guiding document carries regardless of class — §4 |
| 3 | The **front-matter schema** — nineteen keys, normative, with types and validation — §6 |
| 4 | The **template library** — which template governs which class, and where it lives — §7 |
| 5 | **Measured conformance** of the 130 documents on disk, per section, per class — §8 |
| 6 | The **review and approval workflow** for a guiding document — §9 |
| 7 | The **status model**, reconciled with `PGD-000` §0.3 and `GV-011` §5.1 — §10 |
| 8 | The **retirement of the `FIX-ERP2-*` front-matter identifier space**, delegated here by `RR-002` `RR-002-D-06` — §6.4 |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| File naming, storage, retention, supersession, version control | `GV-011` §4.2, §9, §10 | `GV-011` is the configuration-management plan. This document governs what is *inside* a document; `GV-011` governs the file and its lifecycle |
| Identifier form and allocation | `RR-002` | A front-matter `id:` **value** is an identifier question. Its presence as a **key** is a template question and is here |
| Content-estate templates (12 `TPL_*` files) | `CG-005`, `project_content/_templates/` | A different estate with its own governing standard and its own approval body. Registered in §7.3, governed there |
| Module and portal specification structure (the 19-section template) | `1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` | Already exists, already enforced by a documentation gate, and covers 79 files. Registered in §7.3 as class `SPEC`; this document does not restate it |
| Approval **authority** — who may sign what | `GV-002` RACI, `GV-011` §5.4 | This document states the *workflow*; the authority matrix is governance's |
| Writing quality, tone and house style | `CG-004` (content), and convention here | Deliberately not codified: the estate's prose standard is high and emerged without a style guide. §9.4 records the one convention worth stating |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Anyone authoring a guiding document** | §4, §5, §6, §7 — the structure, the front matter, the template |
| **Anyone assessing a ✅ status** | §5 — the section-set denominator and the ≥90% arithmetic. **This is the primary use** |
| Category auditors | §5 and §8 — the conformance instrument, and the baseline to measure drift against |
| PMO | §9's workflow; §10's status model |
| Implementation vendor | §5, to know what a deliverable document must contain before it is accepted |
| Enterprise Architecture | §8's divergence list — six items, each with an owner |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC/IEEE 15289:2019** *Content of life-cycle information items* | §7 (generic information item content), §10 (specific information items) | **The governing standard.** §4's universal frame implements 15289 §7's generic content elements — identification, scope, context, status, ownership, references, revision. §5's per-class sets adopt 15289 §10's named information items where one exists for the class | 15289 names ~60 information items across ISO/IEC/IEEE 12207 and 15288 processes. This estate has eleven classes covering 140 documents. §5.2 maps each class to its 15289 item where one exists and states "no 15289 item" where none does. Declared |
| **ISO 10007:2017** | §5.2 Configuration identification, §5.5 Configuration status accounting | The front-matter schema (§6) is the configuration-identification record; §10's status model is status accounting | `GV-011` owns the CM plan; this document supplies the document-level instrument. No departure |
| **ISO 9001:2015 §7.5** *Documented information* | §7.5.2 creating and updating; §7.5.3 control | §9's review workflow and §6's mandatory `owner`/`approver` keys discharge §7.5.2's identification, format and approval requirements | ⚠ **ISO 9001:2026 publishes 16 September 2026** and revises §7.5. See `RR-005`; this document's §2.1 is registered there for re-verification at the first gate after publication |
| **ISO/IEC/IEEE 12207:2017** | §6.3.6 Information management process | Class definitions in §3 follow 12207's information-item categories | None |
| **ISO/IEC/IEEE 29148:2018** §9 | §9.5 SyRS, §9.6 SRS clause lists | Class `REQ`'s section set in §5.3 is 29148 §9.6.1–9.6.20, verbatim | **§9.6 is the SRS; §9.5 is the SyRS.** The template previously cited §9.5 for the SRS; corrected 2026-08-18 as finding `RQA-01`. Carried here so the correction is not lost |
| **ISO/IEC/IEEE 42010:2022** | §5 architecture description content | Class `ARCH`'s section set in §5.4 | None |
| **IEEE 1016-2009** | §4 design viewpoints | Class `DESIGN`'s section set in §5.5 | None |
| **ISO/IEC/IEEE 29119-3:2021** | §7 test documentation | Class `TEST`'s section set in §5.6 | None |

> **Why 15289 and not "a template".** The estate already has a template — `_templates/TPL_Guiding_Document.md`,
> written 2026-08-18, and 130 documents conform to it well (§8). What it does not have is a
> statement of *what content a document of a given kind must contain to be complete*, which is a
> different question and exactly what 15289 exists to answer. Test (c) asks the 15289 question, and
> a template alone cannot answer it.

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Master register | `../PGD-000_Master_Register_of_Project_Guiding_Documents.md` §0.3, §0.5 | Test (c) and the ◐→✅ promotion bar this document unblocks |
| House template | `../_templates/TPL_Guiding_Document.md` | The nine-section frame and the eighteen-key front matter. **The empirical basis of §4 and §6** |
| Documentation control | `../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md` §4, §5 | Naming, three status models reconciled, version numbering, approval authority by class, the `FIX-ERP2-*` finding |
| Identifier standard | `./RR-002_Identifier_Convention_Standard.md` | `IDC-08` `rule_prefix:`; `RR-002-D-06` delegating `FIX-ERP2-*` retirement here |
| Glossary | `./RR-001_Glossary_and_Acronym_Register.md` | The vocabulary section headings must use |
| The 130 guiding documents | `../[0-9][0-9]_*/[A-Z][A-Z]-[0-9][0-9][0-9]_*.md` | **The measured corpus.** §8's conformance figures are counted from them, not asserted |
| Module template | `../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` | The 19-section specification template governing 79 module and portal files — class `SPEC` |
| Content templates | `../../project_content/_templates/` | Twelve `TPL_*` content templates — registered in §7.3, governed by `CG-005` |
| Content front matter | `../../project_content/_templates/TPL_Content_File_Front_Matter.md` | The content estate's front-matter schema, for the §6.5 comparison |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `PGD-000` §0.3 test (c) had no denominator | `PGD-000` §0.5 | §5 publishes eleven section sets with a stated arithmetic. **The ◐→✅ bar is now measurable** |
| `PGD-A2-03` | `PGD-AUDIT-002` | §6.2 makes `rule_prefix:` a schema key and §4's frame carries `DL-06`'s decision-identifier rule into the template |
| `PGD-A2-17` / `RR-002` `RR-002-D-06` | `PGD-AUDIT-002`, `RR-002` §8.2 | §6.4 retires `FIX-ERP2-*` and states the replacement — the delegation `RR-002` made to this document |
| `RQA-01` | `PGD-AUDIT-002` | §5.3 fixes the SRS section set at 29148 **§9.6**, and §2.1 records why |
| **New — `DSL-F-01`…`DSL-F-05`** | This document | Five conformance defects measured in §8 |

---

## 3. The Document Class Model

### 3.1 Why classes

A section set cannot be universal. An SRS needs *external interfaces*, *performance* and
*verification*; a register needs *the register*, *its allocating authority* and *its currency*.
Applying one section list to both produces either a bloated SRS or an unmeasurable register — and
"unmeasurable" is precisely the state test (c) is in today.

**Eleven classes cover all 140 registered documents.** The class is declared in front matter
(§6.2, key `doc_class`) and is the lookup key into §5.

### 3.2 The classes

| Class | Meaning | Governing standard | 15289 item | Registered docs |
|---|---|---|---|---:|
| `SPEC` | A specification of what something must do or be | ISO/IEC/IEEE 15289 §10 | *(varies)* | 41 |
| `REQ` | A requirements specification | ISO/IEC/IEEE 29148:2018 §9.6 (SRS) / §9.5 (SyRS) | Requirements specification | 4 |
| `ARCH` | An architecture description | ISO/IEC/IEEE 42010:2022 | Architecture description | 6 |
| `DESIGN` | A design description | IEEE 1016-2009 | Design description | 9 |
| `TEST` | A test strategy, plan or specification | ISO/IEC/IEEE 29119-3:2021 | Test documentation | 11 |
| `PLAN` | A plan: what will be done, by whom, when | ISO/IEC/IEEE 15289 §10 (project plan family) | Project/management plan | 26 |
| `STD` | A standard or policy: a rule set others conform to | ISO 9001:2015 §7.5 | Procedure | 22 |
| `REG` | A register: an enumerated, maintained set of records | ISO 10007:2017 §5.5 | Status accounting record | 13 |
| `PROC` | A procedure or runbook: an ordered, repeatable sequence | ISO/IEC 20000-1:2018 §8 | Procedure | 4 |
| `ASSESS` | An assessment, audit or report on a measured state | ISO 19011:2018 §6.6 | Audit report | 3 |
| `MODEL` | A quantified model: inputs, calculation, outputs, sensitivity | AACE RP 17R-97 | *(no 15289 item)* | 1 |

**Total: 140.** The class of every registered document is listed in §5.13.

> **`MODEL` has no ISO/IEC/IEEE 15289 information item**, and it is stated rather than forced into
> the nearest one. `CO-005` Total Cost of Ownership and `GV-008` Programme Budget are cost models
> whose completeness test is *"is the calculation reproducible and is its estimate class
> declared"* — an AACE question, not a 15289 one. Inventing a 15289 mapping would make test (c)
> measure the wrong thing.

### 3.3 Assigning a class

| Question | If yes |
|---|---|
| Does it enumerate a maintained set of records with an allocating authority? | `REG` |
| Does it state rules that other documents or people must conform to? | `STD` |
| Does it state a measured state at a point in time? | `ASSESS` |
| Does it compute numbers from declared inputs? | `MODEL` |
| Does it state an ordered, repeatable sequence to be executed? | `PROC` |
| Does it state what will happen, by whom, and when? | `PLAN` |
| Is it a requirements / architecture / design / test artefact? | `REQ` / `ARCH` / `DESIGN` / `TEST` |
| Otherwise | `SPEC` |

**Order matters — take the first yes.** A document that both registers and standardises is a
`REG`: the register is the thing that must be complete, and the rules exist to keep it so.
`RR-002` is the worked example — it looks like a `STD` and is classed `REG`, because test (c) must
measure whether the register covers the estate, not whether the rules are eloquent.

---

## 4. The Universal Frame

Nine sections. Every guiding document carries all nine regardless of class, and they are the
sections **130 of 130 documents on disk already carry** (§8.2), so this is ratification, not
imposition.

| # | Section | Purpose | 15289 §7 element |
|---:|---|---|---|
| 1 | **Purpose** *(with §1.1 Scope, §1.2 Intended audience)* | What the document is for, what it unblocks, what it excludes and who owns each exclusion | Scope, context |
| 2 | **Basis and Inputs** *(§2.1 Standards conformance, §2.2 Source material, §2.3 Audit findings closed)* | What the document rests on, and what it discharges | References, context |
| 3…n−6 | **Body** | **Class-specific — §5** | Specific content |
| n−5 | **Decisions Recorded** | Local decisions, `<DOC-ID>-D-nn`, with options, choice, rationale and consequence | Status, rationale |
| n−4 | **Open Questions** | `<DOC-ID>-Q-nn`, each with an owner, a needed-by date and what it blocks | Status |
| n−3 | **Acceptance Criteria for This Document** | `AC-nn`, each with evidence, and a definition of done | Verification |
| n−2 | **Traceability** | Upstream / downstream / lateral links | Relationships |
| n−1 | **References** | Repository, workspace and external, with `verified_on` on regulatory citations | References |
| n | **Revision History** | Version, date, author, change, approver | Identification, status |

### 4.1 Frame rules

| # | Rule |
|---|---|
| `DSL-01` | **All nine frame sections are mandatory**, in this order, numbered with `##` and an integer |
| `DSL-02` | **Body sections are numbered 3…n−6** and are class-specific. A document may have any number of them |
| `DSL-03` | **No section number is used twice.** Two sections with the same title in one document is a defect — `DSL-F-02` measures two instances |
| `DSL-04` | **Decisions use `<DOC-ID>-D-nn`; questions use `<DOC-ID>-Q-nn`.** Never the bare forms — `RR-002` `IDC-07`, from `DL-06` |
| `DSL-05` | **An open question with no owner and no needed-by date is not an open question — it is an unrecorded risk**, and is escalated to `GV-005` |
| `DSL-06` | **Every acceptance criterion states its evidence**, and one that is not met at issue says so. A criterion claimed without evidence is the defect `PG-M2` forbids |
| `DSL-07` | **A class may declare a frame section Not Applicable**, keeping the heading and stating why in one line. §5.14 lists the three legitimate exemptions |

### 4.2 The three legitimate exemptions

Measured, not assumed. Three documents omit a frame section and each has a defensible reason:

| Document | Omits | Assessment |
|---|---|---|
| `AR-004` Architecture Decision Record Library | Decisions Recorded, Open Questions | **Legitimate.** The whole document *is* the decision register; a "Decisions Recorded" section inside it would be a decision register inside a decision register. **`DSL-07` applies — but the headings must still appear with a one-line statement.** Currently they do not: `DSL-F-03` |
| `AR-001` Software Architecture Document | Decisions Recorded | **Legitimate by delegation** — architecture decisions go to `AR-004` as ADRs, which the template itself directs. Heading required per `DSL-07` |
| `AR-007` Odoo Module Architecture Standard | Decisions Recorded | **Same delegation.** Heading required |

---

## 5. Per-Class Section Sets — The Test (c) Instrument

### 5.1 How test (c) is computed

`PGD-000` §0.3 test (c): *"covers ≥90% of the section set its governing standard requires, counted
section by section."*

```
              (mandatory sections present) + (conditional sections present)
coverage  =  ───────────────────────────────────────────────────────────────
              (mandatory sections total)   + (conditional sections applicable)

test (c) passes when coverage ≥ 0.90  AND  every mandatory section is present
```

| # | Rule |
|---|---|
| `DSL-08` | **The nine frame sections count toward the denominator**, because they are part of what completeness means |
| `DSL-09` | **A conditional section that does not apply is excluded from both numerator and denominator**, and the exclusion is stated in the document with a one-line reason. An unstated exclusion counts as absent |
| `DSL-10` | **Every mandatory section must be present**, whatever the arithmetic says. 90% of the sections with the requirements clause missing is not an SRS |
| `DSL-11` | **A section is "present" when it carries content, not a heading.** A heading followed by *"To be completed"* is absent. `TBD`, `TBC` and `TBS` are absence markers — `QA-001` `S-01` |
| `DSL-12` | **The assessment is recorded in the category audit**, with the count, not asserted in the document itself |

> **`DSL-10` is the rule that makes this instrument honest.** Without it, a document could omit its
> single most important clause and still score 92%. With it, the arithmetic is a *secondary* test
> and the mandatory list is the primary one — which is how ISO/IEC/IEEE 15289 §7 reads.

### 5.2 Class `SPEC` — Specification

15289 §10, generic specification content. **Mandatory 13 · Conditional 4.**

| # | Section | M/C | Notes |
|---|---|:--:|---|
| 1–2 | Frame §1, §2 | **M** | |
| 3 | Context and dependencies | **M** | What the specified thing sits inside |
| 4 | The specified capability, structure or behaviour | **M** | The body; may be many subsections |
| 5 | Interfaces and boundaries | **M** | |
| 6 | Constraints and assumptions | **M** | |
| 7 | Quality attributes / non-functional properties | **M** | Traced to `RQ-006` |
| 8 | Verification approach | **M** | How anyone would know it was built right |
| 9 | Operational considerations | C | Where the thing runs in production |
| 10 | Security and privacy considerations | C | Mandatory where personal data or credentials are in scope |
| 11 | Bilingual / localisation considerations | C | Mandatory where there is any human-facing surface — `CM-R6` |
| 12 | Migration and transition considerations | C | Mandatory where an existing system is replaced |
| 13–18 | Frame tail: Decisions, Open Questions, Acceptance Criteria, Traceability, References, Revision History | **M** | |

### 5.3 Class `REQ` — Requirements specification

**ISO/IEC/IEEE 29148:2018 §9.6** for an SRS; **§9.5** for a SyRS. Twenty clauses.
**Mandatory 20 · Conditional 0.**

| 29148 §9.6 clause | Section | M/C |
|---|---|:--:|
| 9.6.1–9.6.3 | Introduction: purpose, scope, product overview | **M** |
| 9.6.4 | Product perspective | **M** |
| 9.6.5 | Product functions | **M** |
| 9.6.6 | User characteristics | **M** |
| 9.6.7 | Limitations | **M** |
| 9.6.8 | Assumptions and dependencies | **M** |
| 9.6.9 | Apportioning of requirements | **M** |
| 9.6.10 | Specific requirements | **M** |
| 9.6.11 | External interfaces | **M** |
| 9.6.12 | Functions | **M** |
| 9.6.13 | Usability requirements | **M** |
| 9.6.14 | Performance requirements | **M** |
| 9.6.15 | Logical database requirements | **M** |
| 9.6.16 | Design constraints | **M** |
| 9.6.17 | Standards compliance | **M** |
| 9.6.18 | Software system attributes | **M** |
| 9.6.19 | Verification | **M** |
| 9.6.20 | Supporting information | **M** |
| + frame | Frame §1, §2 and the six-section tail | **M** |

> **All twenty are mandatory and there are no conditionals**, which makes `REQ` the strictest
> class. That is 29148's position, not a local tightening: §9.6 states the clause list as the
> content of an SRS. **A `REQ` document therefore passes test (c) only at 100%** — 19 of 20 is
> 95%, but `DSL-10` requires every mandatory section, so the arithmetic never rescues an omission.

### 5.4 Class `ARCH` — Architecture description

**ISO/IEC/IEEE 42010:2022.** **Mandatory 11 · Conditional 2.**

| # | Section | M/C |
|---|---|:--:|
| 1–2 | Frame §1, §2 | **M** |
| 3 | Stakeholders and their concerns | **M** |
| 4 | Architecture viewpoints | **M** |
| 5 | Architecture views — one per viewpoint | **M** |
| 6 | Architecture models | **M** |
| 7 | Correspondences and correspondence rules | **M** |
| 8 | Architecture rationale | **M** |
| 9 | Architecture decisions, or a reference to the decision register | **M** |
| 10 | Quality attribute scenarios | **M** |
| 11 | Known limitations and technical debt | C |
| 12 | Evaluation / fitness functions | C |
| 13–18 | Frame tail | **M** |

### 5.5 Class `DESIGN` — Design description

**IEEE 1016-2009 §4 design viewpoints.** **Mandatory 8 · Conditional 6** — a design description
selects the viewpoints its subject needs and states which it excluded, which is 1016's own model.

| # | Viewpoint / section | M/C |
|---|---|:--:|
| 1–2 | Frame §1, §2 | **M** |
| 3 | Context viewpoint | **M** |
| 4 | Composition viewpoint | **M** |
| 5 | Logical viewpoint | **M** |
| 6 | Dependency viewpoint | **M** |
| 7 | Information viewpoint | **M** |
| 8 | Interface viewpoint | **M** |
| 9 | Structure viewpoint | C |
| 10 | Interaction viewpoint | C |
| 11 | State dynamics viewpoint | C |
| 12 | Algorithm viewpoint | C |
| 13 | Resource viewpoint | C |
| 14 | Patterns use viewpoint | C |
| 15–20 | Frame tail | **M** |

> **`DSL-09` does real work here.** A design description that legitimately has no state machine
> excludes the state-dynamics viewpoint *and says so*; its denominator drops from 14 to 13 and it
> is not penalised. One that silently omits it scores 13/14 = 93% — still a pass, which is why
> `DSL-09`'s "unstated exclusion counts as absent" matters: without it, silence is cheaper than
> honesty.

### 5.6 Class `TEST` — Test documentation

**ISO/IEC/IEEE 29119-3:2021.** **Mandatory 12 · Conditional 3.** Clause set varies by whether the
document is a strategy (§7), a plan (§8) or a specification (§9); the mandatory core is common.

| # | Section | M/C |
|---|---|:--:|
| 1–2 | Frame §1, §2 | **M** |
| 3 | Test scope and items | **M** |
| 4 | Test levels and types | **M** |
| 5 | Test approach / design techniques | **M** |
| 6 | Entry and exit criteria | **M** |
| 7 | Test environment and data requirements | **M** |
| 8 | Test deliverables | **M** |
| 9 | Risks and contingencies | **M** |
| 10 | Roles, responsibilities and staffing | **M** |
| 11 | Schedule and estimates | C |
| 12 | Suspension and resumption criteria | C |
| 13 | Metrics and reporting | C |
| 14–19 | Frame tail | **M** |

### 5.7 Class `PLAN`

15289 §10 project-plan family. **Mandatory 12 · Conditional 3.**

| # | Section | M/C |
|---|---|:--:|
| 1–2 | Frame §1, §2 | **M** |
| 3 | Objectives and success criteria | **M** |
| 4 | Scope and deliverables | **M** |
| 5 | Approach / method | **M** |
| 6 | Schedule and milestones | **M** |
| 7 | Roles, responsibilities and resources | **M** |
| 8 | Dependencies and assumptions | **M** |
| 9 | Risks and mitigations | **M** |
| 10 | Measurement and reporting | **M** |
| 11 | Cost and effort | C |
| 12 | Communication | C |
| 13 | Contingency / fallback | C |
| 14–19 | Frame tail | **M** |

### 5.8 Class `STD` — Standard or policy

ISO 9001:2015 §7.5, ISO/IEC/IEEE 15289 procedure content. **Mandatory 11 · Conditional 2.**

| # | Section | M/C |
|---|---|:--:|
| 1–2 | Frame §1, §2 | **M** |
| 3 | Applicability — who and what this binds | **M** |
| 4 | The rules, each individually identified | **M** |
| 5 | Rationale for each rule, or a rationale section | **M** |
| 6 | Conformance and enforcement — how a breach is detected | **M** |
| 7 | Exceptions and waiver route | **M** |
| 8 | Transition — what happens to work that predates the standard | **M** |
| 9 | Review cadence | **M** |
| 10 | Worked example | C |
| 11 | Tooling | C |
| 12–17 | Frame tail | **M** |

> **§6 and §8 are the two most commonly missing sections in a standard**, in this estate and
> generally. A rule with no detection is advice; a standard with no transition statement makes 130
> existing documents non-conformant on the day it is issued. Both are mandatory here for that
> reason.

### 5.9 Class `REG` — Register

ISO 10007:2017 §5.5 status accounting. **Mandatory 11 · Conditional 2.**

| # | Section | M/C |
|---|---|:--:|
| 1–2 | Frame §1, §2 | **M** |
| 3 | What is registered — the population and its boundary | **M** |
| 4 | The allocating or maintaining authority | **M** |
| 5 | The record schema — the columns and their meaning | **M** |
| 6 | Enumeration method, with the command and the timestamp | **M** |
| 7 | **The register itself** | **M** |
| 8 | Completeness statement — what is registered against what exists | **M** |
| 9 | Maintenance: how an entry is added, changed, retired | **M** |
| 10 | Review cadence and trigger | **M** |
| 11 | Generated or hand-maintained, and if hand-maintained, why | C |
| 12 | Retirement rows | C |
| 13–18 | Frame tail | **M** |

> **§8 completeness is what test (c) really measures for a register.** A register that lists 95
> KPIs when 301 exist is *structurally* complete and *substantively* worthless. §8 forces the
> comparison into the document, which is how `RR-002` §5.6 came to state its five gaps.

### 5.10 Class `PROC` — Procedure or runbook

ISO/IEC 20000-1:2018 §8. **Mandatory 11 · Conditional 2.**

| # | Section | M/C |
|---|---|:--:|
| 1–2 | Frame §1, §2 | **M** |
| 3 | Trigger — when this procedure runs | **M** |
| 4 | Preconditions and prerequisites | **M** |
| 5 | Roles and authority to execute | **M** |
| 6 | The steps, numbered and individually verifiable | **M** |
| 7 | Decision points and branches | **M** |
| 8 | Verification — how the operator knows it worked | **M** |
| 9 | Rollback / abort | **M** |
| 10 | Escalation | **M** |
| 11 | Timing and expected duration | C |
| 12 | Evidence to be retained | C |
| 13–18 | Frame tail | **M** |

### 5.11 Class `ASSESS` — Assessment or audit report

ISO 19011:2018 §6.6. **Mandatory 11 · Conditional 1.**

| # | Section | M/C |
|---|---|:--:|
| 1–2 | Frame §1, §2 | **M** |
| 3 | Assessment objective, scope and criteria | **M** |
| 4 | Method, including what was and was not examined | **M** |
| 5 | Independence statement and assurance class | **M** |
| 6 | Findings, each individually identified and severity-rated | **M** |
| 7 | Severity basis — what makes a finding Critical | **M** |
| 8 | Evidence per finding | **M** |
| 9 | Recommendations with owners and dates | **M** |
| 10 | Findings closed at this issue, and by what | **M** |
| 11 | Limitations of the assessment | C |
| 12–17 | Frame tail | **M** |

> **§5 independence is mandatory and the estate currently fails it universally.** `PGD-A2-23`
> records that all 29 audit reports are class `I0` — self-assessment. The section is mandatory
> precisely so that the failure is stated in every report rather than inferred from its absence.

### 5.12 Class `MODEL` — Quantified model

AACE RP 17R-97 estimate classification. **Mandatory 11 · Conditional 2.**

| # | Section | M/C |
|---|---|:--:|
| 1–2 | Frame §1, §2 | **M** |
| 3 | What is being estimated, and what is excluded | **M** |
| 4 | Inputs, each with a source and a date | **M** |
| 5 | The calculation, reproducible | **M** |
| 6 | Assumptions, each individually identified | **M** |
| 7 | Outputs with ranges, not point values | **M** |
| 8 | **Estimate class (AACE 1–5) and the expected accuracy range** | **M** |
| 9 | Sensitivity analysis | **M** |
| 10 | Reconciliation against any prior or competing figure | **M** |
| 11 | Currency and price basis date | C |
| 12 | Scenario comparison | C |
| 13–18 | Frame tail | **M** |

### 5.13 Class assignment for all 140 registered documents

| Class | Documents |
|---|---|
| `REG` | `GV-003`, `GV-005`, `AR-004`, `AR-013`, `BE-005`, `BE-009`, `DA-009`, `SC-008`, `CO-004`, `BM-005`, `RR-002`, `RR-004`, `RR-005`, `RR-006`, `RR-001`, `AR-005`, `RQ-004` |
| `STD` | `GV-006`, `GV-011`, `RQ-005`, `RQ-010`, `AR-007`, `AR-012`, `DA-005`, `IN-005`, `SC-005`, `SC-006`, `UX-005`, `UX-007`, `BE-002`, `BE-003`, `BE-004`, `BE-006`, `BE-007`, `BE-008`, `QA-010`, `QA-011`, `PE-003`, `PE-009`, `RL-001`, `RL-005`, `RR-003` |
| `PLAN` | `GV-004`, `GV-010`, `MG-001`, `MG-004`…`MG-007`, `QA-002`, `QA-004`, `QA-006`…`QA-009`, `SC-009`, `SC-011`, `DA-008`, `CH-001`…`CH-004`, `RL-002`, `RL-004`, `RL-006`, `SV-005`, `BM-004`, `CO-006` |
| `SPEC` | `RQ-006`, `RQ-009`, `DA-001`, `DA-002`, `DA-007`, `IN-001`…`IN-004`, `IN-006`…`IN-008`, `SC-001`, `SC-004`, `SC-007`, `SC-010`, `UX-001`…`UX-004`, `UX-006`, `PE-001`, `PE-002`, `PE-005`…`PE-008`, `AR-010`, `AR-011`, `BE-001`, `MG-002`, `MG-003`, `SV-002`, `SV-004`, `CH-005` |
| `REQ` | `RQ-001`, `RQ-002`, `RQ-003`, `RQ-007` |
| `ARCH` | `AR-001`, `AR-002`, `AR-006`, `AR-008`, `AR-009`, `DA-003` |
| `DESIGN` | `AR-003`, and the per-module design descriptions it standardises |
| `TEST` | `QA-001`, `QA-003`, `QA-005`, and the eight plans above where assessed as `TEST` rather than `PLAN` |
| `PROC` | `SV-001`, `SV-003`, `SV-006`, `RL-003` |
| `ASSESS` | `CO-002`, `BM-002`, `UX-008` |
| `MODEL` | `GV-007`, `GV-008`, `CO-005`, `BM-003` |

> **⚠ This assignment is provisional for the 128 documents this session did not author.** A class
> assignment drives a test-(c) denominator, and assigning one from a filename would be exactly the
> unevidenced assertion `PG-M2` forbids. **The class is confirmed by adding `doc_class:` to each
> document's front matter, by its owner** — §6.2, and `RR-003-Q-01`. Where a document's assignment
> above is disputed by its owner, **the owner's assignment governs**; this table is a starting
> position, not a ruling.

### 5.14 Applying the instrument — a worked example

`RR-002`, class `REG`, assessed against §5.9:

| Section | Present? | Where |
|---|:--:|---|
| Frame §1 Purpose | ✔ | §1, §1.1, §1.2 |
| Frame §2 Basis and Inputs | ✔ | §2.1, §2.2, §2.3 |
| 3 What is registered | ✔ | §1.1 scope + §3 identifier model |
| 4 Allocating authority | ✔ | §5, "Authority" column on every row |
| 5 Record schema | ✔ | §5.1 |
| 6 Enumeration method | ✔ | §4.1, with commands and timestamp |
| 7 The register itself | ✔ | §5.2–§5.9 |
| 8 Completeness statement | ✔ | §4.2, §5.6, `IDC-F-01`, `IDC-F-03` |
| 9 Maintenance | ✔ | §7 |
| 10 Review cadence | ✔ | §9 thaw targets, §10 `CHK-06` |
| 11 Generated or hand-maintained (C) | ✔ | §7.4 states hand-maintained, and why |
| 12 Retirement rows (C) | ✔ | §8.4, §8.5 |
| Frame tail ×6 | ✔ | §11–§16 |

**Coverage = 19/19 = 100%; every mandatory section present. Test (c): PASS.**

Tests (a) and (b) also pass. **Test (d) fails** — no approval record, because no body can create
one (`PGD-A1-09`). `RR-002`'s ✅ is therefore *qualified*, exactly as the other 128 are.

---

## 6. The Front-Matter Schema

### 6.1 Measured position

All 130 guiding documents on disk carry an identical eighteen-key front matter — measured, not
assumed:

```bash
for f in */[A-Z][A-Z]-*.md; do
  awk 'NR==1&&/^---/{p=1;next} p&&/^---/{exit} p&&/^[a-z_]+:/{print $1}' "$f"
done | sort | uniq -c | sort -rn
```

| Key | Present in |
|---|---:|
| `id`, `title`, `category`, `code`, `project`, `version`, `date`, `status`, `classification`, `owner`, `approver`, `standards_basis`, `traces_to`, `depends_on`, `verified_on`, `priority`, `needed_by`, `register` | **130 of 130** |
| `enumeration_timestamp` | 102 |
| `enumerated_on` | 21 |
| `rule_prefix` | 10 |
| `artefacts` | 2 |
| `supersedes`, `review_cycle`, `extraction_method` | 1 each |

> ### `DSL-F-01` — one concept, two key names
>
> **`enumeration_timestamp` (102 documents) and `enumerated_on` (21 documents) are the same field
> under two names.** All 21 `enumerated_on` documents are in Categories 00 and 01 — the two
> earliest-authored categories — so this is authoring drift, not disagreement.
>
> Consequence: any query, script or audit that reads `enumeration_timestamp` **silently misses 21
> documents**, including the entire Programme Charter and Requirements Engineering sets. It is the
> `RR-002` `IDC-F-02` failure — one concept, two declarations — in the front-matter namespace
> rather than the identifier namespace.
>
> **`RR-003-D-01`: `enumeration_timestamp` is preferred**, on the counted majority and because it
> names a *moment*, which `RG-08` requires, where `enumerated_on` reads as a date. `enumerated_on`
> is deprecated and the 21 documents are corrected by their category owners.

### 6.2 The normative schema

**Nineteen keys.** Eighteen are inherited from the template and measured at 130/130; three are
added and one is deprecated.

| Key | Type | M/C | Rule |
|---|---|:--:|---|
| `id` | `<CODE>-<nnn>` | **M** | Matches `RR-002` §5.5. **Must equal the filename prefix** |
| `title` | string | **M** | Matches the `# <ID> — <Title>` line exactly |
| `category` | `<nn> — <Name>` | **M** | From `PGD-000` |
| `code` | 2 letters | **M** | The category code |
| **`doc_class`** | enum §3.2 | **M** ⊕ **new** | **The test (c) lookup key.** One of the eleven classes |
| `project` | string | **M** | `1000FiX ERP System v2.0` |
| `version` | `n.n` | **M** | `GV-011` §5.2 |
| `date` | ISO 8601 date | **M** | Issue date |
| `status` | enum §10 | **M** | |
| `classification` | enum | **M** | |
| `owner` | **role, never a person** | **M** | |
| `approver` | role | **M** | `GV-011` §5.4 |
| `standards_basis` | list | **M** | Every standard the document conforms to |
| `traces_to` | list | **M** | Requirements, modules, findings this discharges |
| `depends_on` | list | **M** | Documents that must exist first |
| `verified_on` | ISO 8601 date | **M** | **Mandatory when any statute, standard or vendor version is cited** — `PG-M4` |
| `priority` | `P0`–`P3` | **M** | One digit — `RR-002` `IDC-14` |
| `needed_by` | `W<n>` or `Now` | **M** | |
| `register` | path | **M** | Relative path to `PGD-000` |
| `enumeration_timestamp` | `YYYY-MM-DD HH:MM (+06)` | **M** if any count is quoted | A **moment**, not a date — `RG-08` |
| **`rule_prefix`** | string | **C** ⊕ **ratified** | Mandatory when the document allocates a document-local rule prefix. Must carry the collision check, the file count and the timestamp — `RR-002` `IDC-08` |
| **`supersedes`** | list | **C** ⊕ **new** | Documents this replaces. Currently used by one document; made schema |
| `artefacts` | list | C | Machine-readable artefacts the document owns (`IN-002`, `IN-003`) |
| `review_cycle` | string | C | |
| `extraction_method` | string | C | |
| ~~`enumerated_on`~~ | — | **Deprecated** | Use `enumeration_timestamp` — `RR-003-D-01` |

### 6.3 Validation

```bash
# DSL-CHK-01 — every mandatory key present in every guiding document
for f in */[A-Z][A-Z]-*.md; do
  for k in id title category code doc_class project version date status classification \
           owner approver standards_basis traces_to depends_on verified_on priority \
           needed_by register; do
    grep -q "^$k:" "$f" || echo "$f MISSING $k"
  done
done

# DSL-CHK-02 — front-matter id must equal the filename prefix
for f in */[A-Z][A-Z]-*.md; do
  fid=$(grep -m1 '^id:' "$f" | sed 's/id: *//')
  nid=$(basename "$f" | cut -d_ -f1)
  [ "$fid" = "$nid" ] || echo "$f: id=$fid filename=$nid"
done

# DSL-CHK-03 — deprecated key still in use
grep -l '^enumerated_on:' */[A-Z][A-Z]-*.md
```

### 6.4 Retiring `FIX-ERP2-*` — the delegation from `RR-002`

`RR-002` `RR-002-D-06` froze the module repository's `FIX-ERP2-*` front-matter identifier space —
six sub-forms, no allocating authority, and one duplicate (`FIX-ERP2-006` held by a live audit
report and a superseded pillar file) — and delegated its retirement here because retirement means
**replacing it with a schema**.

**The replacement.** The module repository adopts the same rule as `DSL-CHK-02`:

| # | Rule |
|---|---|
| `DSL-13` | **`id:` equals the identifier in the filename.** `M31_Workshop_and_Depot_Repair_Management.md` carries `id: M31`; `00-06_Documentation_Audit_Report.md` carries `id: 00-06` |
| `DSL-14` | **No parallel document identifier space.** A document has one identifier, and it is the one in its name. `GV-011` §4.3's three-scheme finding closes when this is applied |

**Migration.** 123 files, one line each, mechanical:

```bash
for f in $(find 1000fix_ERP_Module -name '*.md'); do
  nid=$(basename "$f" .md | sed -E 's/^(M[0-9]{2}|P[0-9]{2}|[0-9]{2}-[0-9]{2}).*/\1/')
  echo "$f -> id: $nid"      # review, then apply
done
```

| Consideration | Position |
|---|---|
| Does this break `RR-002` `IDC-04` (permanence)? | **No.** `IDC-04` protects an identifier *whose referent could change*. `FIX-ERP2-*` is being **retired**, not re-pointed, and `IDC-06` requires it to keep resolving — §8.5's mapping table in `RR-002` and the migration output above are that resolution |
| Are there citations to `FIX-ERP2-*` values? | **Counted: none outside front matter.** `GV-011` §4.3 already records that *"a reader given `FIX-ERP2-017` cannot locate the file"* — nobody cites what nobody can resolve. This is the rare case where retirement is nearly free |
| Who executes it? | **The module repository's owner**, not this document. `RR-003-Q-02` |

### 6.5 The content estate's schema

`project_content/_templates/TPL_Content_File_Front_Matter.md` defines a different schema —
`content_type`, `template`, `template_version`, `content_class`, `purpose`, `reviewers`,
`bilingual`, `bn_counterpart`, `sources` — governed by `CG-005`.

**The two schemas are deliberately not merged.** They describe different things: a content file
needs `bn_counterpart` and a `sources` block with per-source verification; a guiding document
needs `standards_basis` and `depends_on`. Four keys are common (`id`, `title`, `version`,
`status`) and carry the same meaning in both, which is the interoperability that matters.

> **One key is worth borrowing and is not.** The content schema's **`sources:` block carries a
> `verified:` date and a source class *per source*.** The guiding-document schema has a single
> document-level `verified_on`, so a document citing twelve standards verified on different dates
> can record only one. Raised as `RR-003-Q-03`; `RR-005` §4 is where the per-source dates live
> today.

---

## 7. The Template Library

### 7.1 Templates in this repository

| Template | Governs | Location | Status |
|---|---|---|---|
| `TPL_Guiding_Document.md` | All eleven classes — the universal frame | `../_templates/` | ✅ Exists, 2026-08-18 |
| `TPL_Class_REG.md` | Class `REG` body sections | `../_templates/` | ⬜ **To be written** — `RR-003-Q-04` |
| `TPL_Class_STD.md` | Class `STD` body sections | `../_templates/` | ⬜ **To be written** |
| `TPL_Class_ASSESS.md` | Category audit reports | `../_templates/` | ⬜ **To be written — highest value of the three**, see §7.2 |

### 7.2 What the existing template needs

`TPL_Guiding_Document.md` is sound and this document does not replace it. Four amendments:

| # | Amendment | Reason |
|---|---|---|
| `A-01` | Add `doc_class:` to the front-matter block | §6.2; the test (c) lookup key |
| `A-02` | Add `rule_prefix:` with the collision-check wording | `RR-002` `IDC-08`; already practised by 10 documents |
| `A-03` | Replace the §3 guidance note with a pointer to `RR-003` §5 | The template currently says *"replace this section with the structure the governing standard requires"* and lists four examples. §5 now states all eleven |
| `A-04` | Add `supersedes:` and standardise on `enumeration_timestamp:` | §6.1, `RR-003-D-01` |

> **`TPL_Class_ASSESS` is the highest-value of the three unwritten templates.** Fourteen audit
> reports exist in this repository and their structures diverge; §5.11 makes `independence
> statement` mandatory, which none currently carries as a numbered section even though
> `PGD-A2-23` established that all of them are class `I0`. A template makes the omission
> impossible rather than merely detectable.

### 7.3 Templates elsewhere in the workspace — registered, not governed

| Template | Governs | Repository | Authority |
|---|---|---|---|
| `_MODULE_TEMPLATE.md` | 67 module + 12 portal specifications, 19 sections | `1000fix_ERP_Module` | `00-01` |
| `TPL_Content_File_Front_Matter.md` | All content files | `project_content` | `CG-005` |
| `TPL_SOP.md`, `TPL_Runbook.md`, `TPL_Test_Script.md`, `TPL_Legal_Document.md`, `TPL_Knowledge_Article.md`, `TPL_Help_Article.md`, `TPL_Master_Data_Specification.md`, `TPL_Notification_Template.md`, `TPL_Document_Print_Template.md`, `TPL_Training_Course_Pack.md`, `TPL_UI_Copy_Pack.md` | Content classes | `project_content` | `CG-005` |

**Thirteen templates outside this repository, all with an allocating authority.** The estate's
template position is stronger than `PGD-000` Category 99 records — its `RR-003` row says
*"Engineering documents have none"*, which was true on 2026-08-18 01:16 and became false at 03:05
the same day when `TPL_Guiding_Document.md` was written. Corrected in §9 of the register update.

---

## 8. Measured Conformance

### 8.1 Method

```bash
# Frame-section presence across every guiding document
for s in "Purpose" "Basis" "Decisions Recorded" "Open Questions" \
         "Acceptance Criteria" "Traceability" "References" "Revision History"; do
  n=$(for f in */[A-Z][A-Z]-*.md; do
        grep -qE "^#{1,2} [0-9]+\. .*$s" "$f" || echo "$f"; done | wc -l)
  printf "%-22s missing in %s\n" "$s" "$n"
done

# Duplicate numbered section titles within one document — DSL-03
for f in */[A-Z][A-Z]-*.md; do
  d=$(grep -ohE '^#{1,2} [0-9]+\. .*' "$f" | sed -E 's/^#+ [0-9]+\. //' | sort | uniq -d)
  [ -n "$d" ] && echo "$(basename $f): $d"
done

# Section-count distribution
for f in */[A-Z][A-Z]-*.md; do grep -cE '^#{1,2} [0-9]+\.' "$f"; done | sort -n | uniq -c
```

### 8.2 Frame conformance — 130 documents, 2026-08-19 03:00 (+06)

| Frame section | Present | Missing | Assessment |
|---|---:|---:|---|
| §1 Purpose | **130** | 0 | ✔ |
| §2 Basis *(any variant)* | **125** | **5** | `DSL-F-04` |
| Decisions Recorded | **127** | **3** | 3 legitimate — §4.2 |
| Open Questions | **129** | **1** | 1 legitimate — §4.2 |
| Acceptance Criteria | **130** | 0 | ✔ |
| Traceability | **130** | 0 | ✔ — but 2 documents carry it **twice**, `DSL-F-02` |
| References | **130** | 0 | ✔ |
| Revision History | **130** | 0 | ✔ |

**Structural conventions — 130 of 130 on all four:**

| Convention | Conformance |
|---|---:|
| Numbered sections use `##`, never `#` | **130 / 130** |
| Title line is `# <ID> — <Title>` | **130 / 130** |
| Eighteen mandatory front-matter keys | **130 / 130** |
| Footer `*<ID> · Category <nn> · … · CONFIDENTIAL*` | **130 / 130** |

> **This is a genuinely strong result and should be said plainly.** A 130-document estate written
> across several authoring sessions with no enforced schema conforms on four structural conventions
> at 100% and on six of eight frame sections at 100%. The template works. §8.3's five defects are
> the exceptions, and four of them are single-digit.

### 8.3 Divergences

| # | Divergence | Count | Documents | Severity | Owner |
|---|---|---:|---|:--:|---|
| `DSL-F-01` | `enumerated_on` vs `enumeration_timestamp` — one concept, two keys; any script reading one misses 21 documents | 21 | All of Categories 00 and 01 | **Medium** | Category 00/01 owners |
| `DSL-F-02` | **Two `Traceability` sections in one document** — `DSL-03` breach; a reader following the numbering reaches the first and stops | 2 | `RQ-007`, `RQ-009` | **Medium** | `RQ` owner |
| `DSL-F-03` | Frame sections omitted **without** the `DSL-07` one-line statement — the omissions are legitimate, the silence is not | 3 | `AR-001`, `AR-004`, `AR-007` | Low | `AR` owner |
| `DSL-F-04` | No numbered `Basis` section | 5 | `DA-004`, `DA-007`, `DA-008`, `DA-009`, `SC-002` | Low | `DA`, `SC` owners |
| `DSL-F-05` | **Section count ranges from 10 to 50** with no class-based expectation, so "is this document complete?" was unanswerable before §5 | 130 | All | **High** | Closed by §5 |

> **`DSL-F-05` is the finding this document exists to close.** Ten sections and fifty sections can
> both be complete — a `PROC` runbook and a `REG` covering 1,094 identifier spaces have genuinely
> different needs. What was missing was the *class*, and therefore the denominator. §5 supplies it;
> the finding closes at issue, and §5.13's provisional class assignment is the residual work.

### 8.4 What was not measured

`DSL-11` says a section is present when it carries content, not a heading. **§8.2 measures
headings.** A full test-(c) assessment requires reading each section, which is a category audit's
job (`DSL-12`), not a grep's. §8.2 is therefore an **upper bound on conformance**, stated as such —
the same discipline `PGD-000` applies to its ✅ count being a lower bound.

---

## 9. Review and Approval Workflow

### 9.1 The workflow

| Stage | Action | Who | Exit |
|---:|---|---|---|
| 1 | **Register** the document in `PGD-000` — `PG-01` | Author + PMO | Row exists with ID, priority, needed-by |
| 2 | **Class** it — §3.3 — and record `doc_class:` | Author | Front matter |
| 3 | **Draft** against §4's frame and §5's class set | Author | Draft complete |
| 4 | **Self-assess** against §5 and record the coverage in the draft's acceptance criteria | Author | Coverage stated |
| 5 | **Technical review** — one reviewer who did not author it | Named reviewer | Comments resolved |
| 6 | **Category audit** — test (c) assessed and recorded | Auditor | `PGD-AUDIT-CAT-<nn>` |
| 7 | **Approve** | The `approver:` role | Approval record |
| 8 | **Status update** in `PGD-000` with a fresh enumeration timestamp | PMO | Register current |

> **Stages 5 and 7 do not currently happen, and saying so is the point.** `PGD-A2-23` records all
> 29 audit reports as class `I0` — self-assessment, no independent reviewer. `PGD-A1-09` records
> that no body can approve. **Stages 1, 2, 3, 4, 6 and 8 are operating; 5 and 7 are blocked on
> `GV-001` `CC-01`.** The workflow is written in full so that what is missing is visible as a gap
> rather than as an unwritten step.

### 9.2 Reviewer independence

| Class | Minimum independence | Basis |
|---|---|---|
| `ASSESS` | **`I2`** — reviewer outside the authoring function | ISO 19011:2018 §5.5.3 |
| `REQ`, `ARCH`, `DESIGN` | `I1` — reviewer who did not author | `GV-010` |
| All others | `I1` | `GV-010` |

**Current state: `I0` for all.** `GV-010` is the assurance plan and owns the remediation.

### 9.3 What triggers a re-review

| Trigger | Effect |
|---|---|
| A cited standard or statute changes status in `RR-005` | Re-verify §2.1 and the references table; update `verified_on` |
| An upstream document in `depends_on` changes materially | Re-review §2.2 and §14 |
| A category audit raises a finding against the document | Re-issue at the next version |
| A wave gate | Re-verify counts against a fresh enumeration — `DSL-15` |

### 9.4 The one style convention worth stating

| # | Rule |
|---|---|
| `DSL-16` | **A figure appears in a document with the timestamp at which it was counted, or it does not appear.** This is `RG-06`/`PG-03` applied to prose rather than tables, and it is the single convention that distinguishes this estate's documents from ordinary programme documentation. `PG-M10` extends it: a figure appearing in more than one place is regenerated in every place, or it is only correct where somebody remembered |

---

## 10. The Status Model

### 10.1 Reconciled

`GV-011` §5.1 found three status models in the estate and reconciled them. This document adopts
that reconciliation without change and states it once for authoring use:

| Status | Meaning for a document being written | `PGD-000` §0.3 equivalent |
|---|---|---|
| `DRAFT` | Being written | — |
| `DRAFT FOR APPROVAL` | Complete against §4 and §5; awaiting review and approval | ✅ *qualified* — tests (a)(b)(c) met, (d) not |
| `APPROVED` | Approval record exists | ✅ |
| `SUPERSEDED` | Replaced; retained for traceability | — |
| `WITHDRAWN` | Removed from the register by Change Request | — |

### 10.2 Why every document in this repository is `DRAFT FOR APPROVAL`

Not authoring incompleteness. **`PGD-A1-09`: no constituted body can create an approval record**,
so `APPROVED` is unreachable for every document in the estate until `GV-001` `CC-01` — the ERP
Steering Committee's first minuted meeting — completes. `PGD-000` §0.5 carries the same
qualification against all 128 ✅ statuses.

> **`RR-003` does not invent a sixth status to escape this**, for the reason `PGD-000` gives: no
> body could approve that either.

---

## 11. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RR-003-D-01` | `enumerated_on` vs `enumeration_timestamp` | (a) accept both as synonyms; (b) prefer `enumeration_timestamp`; (c) prefer `enumerated_on` | **(b)** | 102 documents against 21; and it names a *moment*, which `RG-08` requires | 21 documents corrected by their category owners; `DSL-CHK-03` detects |
| `RR-003-D-02` | How many document classes | (a) one universal set; (b) three or four broad classes; (c) eleven aligned to governing standards | **(c)** | Test (c) says *"the section set its **governing standard** requires"*. A class that does not map to a standard cannot answer it. `MODEL` is the one class with no 15289 item, and that is stated rather than forced | Eleven section sets; `doc_class:` becomes a mandatory key |
| `RR-003-D-03` | Whether frame sections count in the test (c) denominator | (a) exclude — measure only class-specific content; (b) include | **(b)** | Traceability and acceptance criteria *are* part of completeness in this estate, and excluding them would let a document with no traceability score 100% | Denominators are 17–20 rather than 8–12 |
| `RR-003-D-04` | Whether to restructure the 130 written documents to a new standard | (a) impose a new structure; (b) derive the standard from measured practice and name the divergences | **(b)** | §8.2 measures 100% conformance on four structural conventions and six of eight frame sections. A standard producing 130 non-conformances on day one would be ignored by day two | Five divergences, four of them single-digit, each with an owner |
| `RR-003-D-05` | `FIX-ERP2-*` replacement | (a) allocate a fresh parallel space with an authority; (b) `id:` equals the filename identifier | **(b)** | A second identifier for a document that already has one is the defect (`DSL-14`). `GV-011` §4.3 established that the parallel space resolves for nobody | 123 files, one line each; **execution is the module repository owner's** |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `RR-003-Q-01` | Each document's owner must confirm its `doc_class:` — §5.13 is provisional for the 128 this session did not author. **Assigning a class assigns a test-(c) denominator; asserting one from a filename is the defect `PG-M2` forbids** | Category owners | W1 | Every ◐→✅ promotion |
| `RR-003-Q-02` | Who executes the `FIX-ERP2-*` retirement across 123 module-repository files? | Module repository owner | W1 | `RR-002` `TH-07` |
| `RR-003-Q-03` | Should the guiding-document schema adopt the content estate's per-source `verified:` dates, so a document citing twelve standards can record twelve verification dates instead of one? | Enterprise Architecture | W1 | `RR-005` currency propagation |
| `RR-003-Q-04` | Are the three class templates (`REG`, `STD`, `ASSESS`) written now, or when the next document of each class is authored? `ASSESS` is needed first — fourteen audits and no template | PMO | W1 | Audit consistency |
| `RR-003-Q-05` | Does an `ASSESS` document require `I2` independence *before* its findings may close a `PGD-000` status? Today all are `I0`, so every ✅ rests on self-assessment | **CTO** | W1 | `PGD-A2-23`; the credibility of every category audit |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | A section set is published for every document class in the register | §5.2–§5.12 — 11 of 11; **met at issue** |
| `AC-02` | Every registered document is assigned a class | §5.13 — 140 of 140, **provisional**; `RR-003-Q-01` |
| `AC-03` | Test (c)'s arithmetic is stated unambiguously and is reproducible by two people independently | §5.1 formula + `DSL-08`…`DSL-12`; **met at issue** |
| `AC-04` | The instrument is demonstrated on a real document | §5.14, `RR-002` assessed at 19/19; **met at issue** |
| `AC-05` | The front-matter schema is normative, typed, and validated by a runnable check | §6.2, §6.3; **met at issue** |
| `AC-06` | Conformance of the existing estate is measured, not assumed, with the command printed | §8.1, §8.2; **met at issue** |
| `AC-07` | Every divergence has a count, named documents, a severity and an owner | §8.3 — 5 of 5; **met at issue** |
| `AC-08` | `RR-002`'s `FIX-ERP2-*` delegation is discharged with a replacement rule and a migration | §6.4; **met at issue** |
| `AC-09` | The three class templates exist | **NOT met** — `RR-003-Q-04`. The frame template exists and governs; class templates are additive |

**Definition of done.** Complete when every criterion is met, `PGD-000`'s `RR-003` row moves from
⬜ to ✅ with a fresh enumeration timestamp, and the approver signs. `AC-02` is **provisional** and
`AC-09` is **not met**; both are stated rather than claimed.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `PGD-000` §0.3, §0.5 | Defines test (c); **this document supplies its denominator and unblocks every ◐→✅ promotion** |
| Upstream | `GV-011` | Owns naming, versioning, storage, approval authority. This document owns document *content* |
| Upstream | `RR-002` | `IDC-08` `rule_prefix:`; `RR-002-D-06` delegates `FIX-ERP2-*` retirement |
| Upstream | `_templates/TPL_Guiding_Document.md` | The empirical basis of §4 and §6; four amendments in §7.2 |
| Downstream | **Every category audit** | §5 is the instrument they assess test (c) with |
| Downstream | `RR-004` | Its evidence rows carry the `verified_on` discipline §6.2 makes mandatory |
| Downstream | `RR-005` | §9.3's re-review trigger fires from its currency register |
| Downstream | `RR-006` | Front-matter keys are index dimensions; `DSL-CHK-01`…`03` become generated checks |
| Downstream | `GV-010` | §9.2's independence classes are its remediation scope |
| Lateral | `../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` | Class `SPEC` for 79 files; registered, not restated |
| Lateral | `../../project_content/_templates/` | Twelve content templates; registered in §7.3, governed by `CG-005` |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./RR-001_Glossary_and_Acronym_Register.md` · `./RR-002_Identifier_Convention_Standard.md` ·
`./RR-004_Source_Document_Index_and_Evidence_Register.md` ·
`./RR-005_Standards_and_Regulatory_Currency_Register.md` ·
`./RR-006_Master_Cross_Reference_and_Traceability_Index.md` ·
`../_templates/TPL_Guiding_Document.md` ·
`../00_Programme_Governance_and_Control/GV-010_Programme_Assurance_and_Independent_Review_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md` ·
`../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-01_Master_Index_and_Document_Map.md` ·
`../../project_content/_templates/TPL_Content_File_Front_Matter.md` and eleven sibling templates ·
`../../project_content/00_Content_Governance_and_Standards/CG-005_*.md`

**External standards**

| Standard | Title | Status | `verified_on` |
|---|---|---|---|
| ISO/IEC/IEEE 15289:2019 | Content of life-cycle information items (documentation) | Current | 2026-08-19 |
| ISO 10007:2017 | Configuration management | Current | 2026-08-19 |
| ISO 9001:2015 | Quality management systems — Requirements | **Current, replaced by ISO 9001:2026 on 16 September 2026** | 2026-08-19 |
| ISO/IEC/IEEE 12207:2017 | Software life cycle processes | Current | 2026-08-19 |
| ISO/IEC/IEEE 29148:2018 | Requirements engineering | Current | 2026-08-19 |
| ISO/IEC/IEEE 42010:2022 | Architecture description | Current | 2026-08-19 |
| IEEE 1016-2009 | Software design descriptions | Current | 2026-08-19 |
| ISO/IEC/IEEE 29119-3:2021 | Software testing — Test documentation | Current | 2026-08-19 |
| ISO 19011:2018 | Guidelines for auditing management systems | Current | 2026-08-19 |
| ISO/IEC 20000-1:2018 | Service management system requirements | Current | 2026-08-19 |

> **ISO 9001:2026 publishes in 28 days** and revises §7.5 *Documented information*, on which §2.1
> and §9 rest. Registered in `RR-005` as a dated horizon with this document named as an affected
> artefact.

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture | Initial issue. Eleven document classes and their section sets — the `PGD-000` §0.3 test (c) instrument. Nineteen-key front-matter schema. Conformance measured across 130 documents: five divergences. `FIX-ERP2-*` retirement discharged | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`RR-003` · Category 99 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
