---
id: CO-003
title: Statement of Work & Deliverable Acceptance Schedule
category: 14 — Commercial, Vendor & Contract
code: CO
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Financial Officer, with Legal Counsel
approver: Board of Directors, on the recommendation of the ERP Steering Committee
standards_basis: >
  ISO 9001:2015 §8.4 (control of externally provided processes, products and services) —
  the clause RFP §19.3 obliges 1000FiX to maintain throughout · ISO/IEC/IEEE 12207:2017 §6.1.1
  (acquisition process) and §6.1.2 (supply process) · ISO/IEC/IEEE 15288:2023 §6.4.7
  (verification) and §6.4.9 (validation) · ISO 21502:2020 §7.14 (procurement) ·
  ISO 37500:2014 §7 (outsourcing transition and governance) · ISO 44001:2017 stages 5–7 ·
  ISO 10007:2017 (configuration management of the deliverable baseline) · WorldCC contracting
  principles · Bangladesh Contract Act 1872 · Arbitration Act 2001 (Bangladesh)
traces_to: >
  PGD-000 CO-003 · RFP §12.4 (wave gate acceptance), §12.5 (17-point Definition of Done),
  §14 (support, hypercare, warranty), §16.4 (payment structure), §16.5 (CR-01…CR-09),
  §19.1–§19.4 (contractual terms) · GV-009 §6.3 (gate outcomes) · GV-008 §5 (tranches and
  drawdown) · CO-005 §6.1, §6.2, §6.7 (tax and FX) · CO-002 §11 (the five selection risks) ·
  GV-007 §7.5 · CVA-02
depends_on: CO-002 · CO-005 · GV-008 · GV-009 · GV-003 · GV-006 · GV-011 · QA-011 · RL-002 · RL-003 · SV-002 · SC-003
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 02:36 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# CO-003 — Statement of Work & Deliverable Acceptance Schedule

### Category 14 · Code `CO` · ISO 9001:2015 §8.4 · ISO/IEC/IEEE 12207:2017 §6.1 · ISO 21502:2020 §7.14 · ISO 37500:2014 §7

---

> **Local rule prefix: `SOW-nn`.** Verified to return **zero** occurrences workspace-wide before
> allocation, at 2026-08-19 02:36 (+06), by
> `grep -rho "SOW-[0-9]\{1,3\}" --include=*.md .` across all six repositories.
>
> **⚠ The category code `CO` is already a rule prefix in three unrelated namespaces** — cost
> controls in `PE-006` §8.4, content-operating-model rules in `CG-002`, callback-ordering rules in
> `IN-006`; **108 occurrences across 30 files and 3 repositories**. No document in Category 14 uses
> `CO-nn` as a local rule prefix. Recorded as `CVA-01`.

---

## 1. Purpose

**This is the document that makes the rest of the register enforceable.**

`PGD-000` states the problem in two sentences: *"Every document in this register should appear in
the Statement of Work as a named deliverable with an acceptance test and a payment milestone.
Without that, 'done' is renegotiated per invoice, and the absent documents remain absent because
nobody is contractually obliged to produce them."*

That is the failure mode this document exists to prevent, and it is not hypothetical. Three audits
have found the same shape of defect: work that everybody assumed somebody owned, which nobody had
been instructed to do. `AF-09` found 520–775 person-weeks of content production *"accountable to
nobody"*. `PGD-A1-05` found the guiding-document estate unestimated. `CH-002` §7.1 lists nine
training resources and marks every one *"In `GV-007` §8? ✘ — Funded? ✘"*. **In each case the work
was necessary, visible and unowned.** A contract is the instrument that converts *necessary* into
*owed*.

### 1.1 The distinction that shapes this whole document

A naive Statement of Work would list the register's 140 documents as deliverables and ask the
implementation partner to produce them. **That would be wrong, expensive and slow**, because
**123 of the 140 already exist.**

**Enumerated from disk at 2026-08-19 03:02 (+06)** — re-run at audit, because the estate moved by
eight documents in the twenty-six minutes between this document's first enumeration and its audit:

| Position | Count |
|---|---:|
| Documents registered in `PGD-000` | **140** |
| Authored and present in this repository | **131** |
| Marked ✅ against material outside this repository — `CO-001` (the RFP) and `BM-001` (`06-02`) | **2** |
| **Covered** | **133** |
| **Genuinely absent** — `BM-003`, `BM-004`, `BM-005`, `RR-003`, `RR-004`, `RR-005`, `RR-006` | **7** |

**Verification** *(regenerated per `PG-M10`)*: 131 + 2 = 133 ✓ · 140 − 133 = **7** ✓.

> **`SOW-Q-11` — the count in this table is a reading, not a state.** The first enumeration at 02:36
> returned 123 authored and 15 absent; the audit re-run at 03:02 returned **131 and 7**. Eight
> documents were authored in twenty-six minutes by concurrent sessions. **Any figure in this
> document that counts the register is true at its stated timestamp and at no other moment**, and
> §5.2's per-category column carries the same caveat. `PG-03`'s *"count, do not consult"* has a
> corollary in an estate authored concurrently: **count, state when you counted, and re-count before
> you rely on it.**

**So the contractual obligation is not "write 140 documents". It is four different obligations, and
naming them correctly is the difference between a Statement of Work that works and one that buys
the wrong thing:**

| Type | Obligation | Applies to | Acceptance test |
|:--:|---|---|---|
| **A — Author** | Produce the document to the standard its category requires | The 15 absent, **and** the per-wave instances of documents that recur | Approved by the named approver in `PGD-000` |
| **F — Conform** | **Build in conformance with the document, evidenced** | Most of the 123 that exist | The fitness function, the gate evidence, or the negative test named in §6 |
| **M — Maintain** | Keep it current across nine waves under `GV-011` configuration control | Every document the build changes | Version incremented in the same change; `GV-011` `CM-17` |
| **X — Company obligation** | **1000FiX** produces, supplies or decides it, by a dated commitment **inside the contract** | Governance, requirements, benefits, commercial, and the business-side commitment | A dated dependency schedule, §8 |

> **Type X is the type most Statements of Work omit, and omitting it is how a fixed-price contract
> becomes a claim.** `GV-007` §7.5 records that the programme depends on **134–201 super-users at
> 30% during UAT**, that **not one has been named**, and that `RSK-001` is rated Critical on exactly
> this. A vendor whose contract does not name the Company's obligations will meet the first UAT
> delay with a change request, and will be right to.

### 1.2 Scope

**In scope:**

| # | Covered |
|:--:|---|
| 1 | The **deliverable architecture** — four classes, and what belongs in each (§4) |
| 2 | The **deliverable schedule** — every one of the register's 140 documents typed A/F/M/X, with counts verified (§5) |
| 3 | The **acceptance regime** — the 17-point Definition of Done as the acceptance standard, the evidence classes, timeboxes, deemed acceptance, rejection and re-submission (§6) |
| 4 | **Payment milestones** mapped to `GV-009` wave gates and `GV-008` tranches, with retention (§7) |
| 5 | The **Company's own obligations**, dated, inside the contract (§8) |
| 6 | **Remedies** — service credits, retention, performance bond, step-in, termination (§9) |
| 7 | **Commercial clauses** the RFP does not contain: tax, FX, escalation (§10) |
| 8 | **Change control** — the interface between `CR-02`/`CR-03` and `GV-003`/`GV-006` (§11) |
| 9 | **Key personnel**, substitution and the remedy for bench-and-swap (§12) |
| 10 | **Intellectual property, source delivery, escrow and exit** (§13) |
| 11 | **Data protection** — the DPA under PDPA 2026 and sub-processor control (§14) |
| 12 | Two **conflicts between the RFP and the estate's own gate handbook** that must be resolved before signature (§7.4, §7.5) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **Selection** of the counterparty | `CO-002` | This document is what the selected party signs |
| The **price** and its derivation | `CO-005` | §7 schedules payment; it does not set the amount |
| **Wave gate criteria** themselves | `GV-009` | §6 makes them contractual; it does not author them. Restating them here would create a second, divergent set — the `PGD-A2-11` defect |
| **Programme change control** | `GV-003` §6, `GV-006` | §11 is the contractual interface to them, not a replacement |
| **Licence obligations** on components | `CO-004`, `BE-007` | §13.4 makes them contractual; the register is `CO-004`'s |
| **Procurement** of goods and infrastructure | `CO-006` | A different contract type with a different acceptance model |
| The **support contract** after warranty | `SV-002` | §7.6 covers hypercare and warranty; steady-state service levels are `SV-002`'s |
| The **legal drafting** | Legal Counsel | This document specifies what the contract must achieve; it is not the contract |

### 1.3 Intended audience

| Audience | What they use this document for |
|---|---|
| **Legal Counsel** | The specification the contract is drafted against. §5, §6, §9, §10, §12, §13, §14 are drafting instructions |
| **Chief Financial Officer** | The owner. §7's payment schedule and §9's remedies are the commercial spine |
| **Programme Director / PMO** | §6's acceptance procedure is run weekly for three years |
| **ERP Steering Committee** | §7.4 and §7.5's conflicts require a decision before signature |
| **Board of Directors** | §7.1's milestone structure is how the Board's tranche authority reaches the vendor |
| **Implementation partner** | Every obligation on them, and every obligation on the Company, is here |
| Category owners and document approvers | §6.3 — they are named as acceptors and the timebox binds them |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 9001:2015** | **§8.4** — control of externally provided processes, products and services | §5's deliverable typing, §6's verification regime and §9's controls discharge §8.4.1 (criteria for evaluation and selection), §8.4.2 (type and extent of control) and §8.4.3 (information for external providers) | **None, and it is not optional.** RFP §19.3 obliges 1000FiX to maintain ISO 9001:2015 *"throughout"*. A contract that does not implement §8.4 puts the Company's own certification at risk, which is a consequence nobody has stated before |
| **ISO/IEC/IEEE 12207:2017** | §6.1.1 acquisition, §6.1.2 supply | §4's deliverable classes, §6's acceptance, §11's change control | The agreement processes assume a bespoke development. **Departure:** this is a build-and-integrate on a packaged platform, so §5's obligation types A/F/M replace a flat deliverable list |
| **ISO/IEC/IEEE 15288:2023** | §6.4.7 verification, §6.4.9 validation | §6.2's separation of *verification* (built right, against the specification) from *validation* (right thing, against the business need — `DoD-13`'s named super-user sign-off) | None. This separation is why `DoD-02` and `DoD-13` are both required and neither substitutes for the other |
| **ISO 21502:2020** | §7.14 procurement | §7's payment and §11's administration | None |
| **ISO 37500:2014** | §7 outsourcing transition and governance | §8's Company obligations, §12's key personnel, §13's exit | None |
| **ISO 44001:2017** | Stages 5–7 (value creation, staying together, exit) | §9's remedies, §11's change interface, §13.5's exit | `CO-002` §2.1 covers stages 1–4. Together the two documents cover the relationship life cycle; neither claims to alone |
| **ISO 10007:2017** | Configuration identification and control of the deliverable baseline | §5.4 — every deliverable is a configuration item under `GV-011` | Delegated to `GV-011`; not restated |
| **WorldCC contracting principles** | Balanced risk allocation; the most-negotiated-terms analysis | §9 and §10 place risk with the party that controls it | Adopted as practice |
| **Bangladesh Contract Act 1872**; **Arbitration Act 2001** | — | §9.6's dispute path; RFP §19.1(9)–(10) | Governing law and arbitration are already fixed by RFP §19.1 and are not reopened |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| RFP §12.4 | `../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` | Wave gate acceptance criteria |
| RFP §12.5 | as above | **The 17-point Definition of Done**, stated to be *"contractually binding"* |
| RFP §12.6, §12.7, §12.8 | as above | Delivery method, team model, contingency |
| RFP §14.1–§14.4 | as above | Hypercare, steady-state support, maintenance, **warranty ≥ 12 months per wave** |
| RFP §16.4, §16.5 | as above | The eleven payment milestones, retention, service credits, `CR-01`…`CR-09` |
| RFP §19.1–§19.4 | as above | IP, source delivery, data ownership, termination, DPA, step-in, escrow, governing law |
| `GV-009` §6.3, §6.4, §9.1 | `../00_Programme_Governance_and_Control/GV-009_*.md` | **PASS / CONDITIONAL PASS / FAIL** and their funding consequences; the signature set; `SG-1`…`SG-11` standing criteria |
| `GV-008` §5.1–§5.3, §8 | `../00_Programme_Governance_and_Control/GV-008_*.md` | Tranches T0/T1/T2, funding release gates, `CB-01`…`CB-10` |
| `GV-003` §6 | `../00_Programme_Governance_and_Control/GV-003_*.md` | Programme change control, into which contractual change must feed |
| `GV-006` | `../00_Programme_Governance_and_Control/GV-006_*.md` | Scope baseline control — `CR-02`'s "agreed requirement set" |
| `GV-011` §5.4, §6 | `../00_Programme_Governance_and_Control/GV-011_*.md` | Configuration classes, approval authority, `CM-16`, `CM-17` |
| `CO-005` §6.1, §6.2, §6.7, §6.8 | `./CO-005_Total_Cost_of_Ownership_Model.md` | The tax, FX and escalation positions §10 makes contractual |
| `CO-002` §11 | `./CO-002_Vendor_Evaluation_and_Selection_Report.md` | The five selection risks, each mapped here to a named clause |
| `GV-007` §7.3, §7.5 | `../00_Programme_Governance_and_Control/GV-007_*.md` | The excluded work streams and the unsized business-side draw §8 makes contractual |
| `QA-011`, `RL-002`, `RL-003`, `SV-002` | `../08_Quality_Engineering_and_Test/QA-011_*.md` · `../12_Release_Deployment_and_Transition/RL-002_*.md`, `RL-003_*.md` · `../11_Service_Operations_and_Support/SV-002_*.md` | The evidence artefacts §6 accepts against |
| `SC-003` | `../05_Security_Privacy_and_Compliance/SC-003_*.md` | The DPIA the DPA in §14 must be consistent with |

### 2.3 Findings this document raises or closes

| Finding | Severity | Statement |
|---|:--:|---|
| *"Without a Statement of Work, 'done' is renegotiated per invoice"* | — | **Closed in specification.** §5 and §6 |
| **`CVA-10`** *(raised here)* | High | **The RFP's retention provisions are internally ambiguous.** §16.4's milestone table carries a 2% line *"retention released after the 12-month warranty on the final wave"*, while its following paragraph separately retains **5% of each milestone payment**. Two retention mechanisms, one of which is also a milestone. §7.3 |
| **`CVA-11`** *(raised here)* | **High** | **The RFP and `GV-009` give opposite funding consequences for the same gate outcome.** RFP §16.4: *"No milestone payment is released against a conditionally passed gate until the dated remediation plan is complete"* — **0%**. `GV-009` §6.3: *"Funding released at 80%, balance on remediation closure"* — **80%**. §7.4 |
| **`CVA-12`** *(raised here)* | Medium | **Warranty and retention run past the contract's own horizon.** Warranty is ≥ 12 months per wave (RFP §19.2); Wave 9's gate is Month 36; its retention therefore releases at **Month 48** — a year after programme closure, in a period `CO-005` §7.2 models as run-state with no project to administer it. §7.3 |
| **`CVA-13`** *(raised here)* | Medium | **`DoD-17` requires regulatory citations to be *"verified current, with a verified-on date"*, but nothing in the RFP obliges the vendor to re-verify at each subsequent gate.** A citation verified at Wave 2 and relied on at Wave 8 is four regulatory years old. `GV-009` `SG-10` fixes this on the Company side; the contract does not. §6.5 |
| **`CVA-06`** *(carried from `CO-005`)* | **High** | **RFP §14.1 prices hypercare at four weeks per wave — 36 weeks. `SV-005` §4.1 requires 56.** The contractual scope is understated by **20 weeks, or 56%**, and respondents are pricing against the lower figure. Joins Addendum 1 with `CVA-02` |
| **`CVA-14`** *(raised here)* | Medium | **The RFP's 17-point Definition of Done applies to *modules*. Twelve portals have no Definition of Done at all.** RFP §12.5 is headed *"Module Definition of Done"*, and `D-016` establishes that the 298 PW of portal build is outside the module figure. §6.4 |

---

## 3. What This Contract Is Buying

Stated before the schedule, because a deliverable list without a shape is a list.

| # | The thing bought | Quantity | Where it is specified |
|:--:|---|---:|---|
| 1 | **Working software** — modules | 67 | `1000fix_ERP_Module/03_Modules`; RFP §6 |
| 2 | **Working software** — portals and applications | 12 | `1000fix_ERP_Module/04_Portals`; RFP §7 |
| 3 | **Requirements satisfied**, at requirement level | 2,930 | RFP §6, Appendix A |
| 4 | **External integrations** | 47 | RFP §8.2; `IN-001`…`IN-008` |
| 5 | **Non-functional requirements** met and evidenced | 101 | RFP §9 |
| 6 | **Engineering artefacts** — conformance to, and maintenance of, the register | 140 documents | `PGD-000`; §5 |
| 7 | **Evidence packs** at each wave gate | 9 gates × 6 dimensions | `GV-009` §3.3, §7, §8 |

> **`CO-003-F-08` (HIGH, raised 2026-08-19). Rows 3 and 5 buy less than the estate specifies.**
> Both quantities are the RFP's, and the RFP has not been restated since the engineering estate was
> counted. **This document inherits the gap; it does not create it** — but it is the document that
> makes it contractual.

| Row | The contract buys | The estate specifies | Gap | Counted by |
|:--:|---:|---:|---:|---|
| 3 — requirements | **2,930** (RFP §6, Appendix A) | **3,389** = 3,347 module/portal rows + 42 `SWR` | **+459 (+15.7%)** | `RQ-001` §3.10.5, `RQ-004` `CV-01`, `QA-011` |
| 5 — non-functional requirements | **101** (RFP §9) | **122** — `05-06`'s 101 plus the contiguous block `NFR-102`…`NFR-122` | **+21 (+20.8%)** | `RQ-006` §4 |

> **Verification** *(counted 2026-08-19 18:46 (+06))*: distinct `NFR-` identifiers — module estate
> and `primary-doc` **101**, `project-guide-doc` **122**, with **zero** source NFRs missing, so the
> guide extends rather than diverges ✓ · 3,389 − 2,930 = **459** ✓ · 459 ÷ 2,930 = **15.7%** ✓ ·
> 122 − 101 = **21** ✓.
>
> **Why this is HIGH and not a drafting note.** A supplier who satisfies all 2,930 and all 101 has
> **met this schedule in full** and is entitled to payment, while 459 requirements and 21 NFRs the
> engineering estate treats as in-scope remain unbuilt. `SOW-27`'s acceptance test would pass.
> The exposure runs in the Company's direction, and it is the largest single scope risk in this
> document.
>
> **Remediation — a change request to `primary-doc`, which this document cannot edit.** RFP §6
> Appendix A and §9 are restated to **3,389** and **122**, or rows 3 and 5 are re-drafted to cite
> *"the requirement baseline as maintained in `RQ-001` and `RQ-006` at contract date"* rather than a
> fixed number. **The second option is the better one**: it survives the next recount, and `RQ-005`
> already governs baseline change. Raised as `GV-005` and carried in `PGD-AUDIT-ALIGN-001` §4.1.
>
> **`CO-002` inherits the same figure** in its evaluation sizing (2,930 responses per respondent,
> §7.2 and `CO-002-D-05`'s sampling plan). That sizing is **correct for the RFP as issued** and is
> re-sized if the RFP is restated.
| 8 | **Hypercare**, after every wave go-live | 9 × 4–8 weeks | RFP §14.1; `OP-002` §4.3 |
| 9 | **Warranty**, per wave | ≥ 12 months | RFP §19.2 |
| 10 | **Knowledge transfer** sufficient to make 1000FiX self-sufficient | — | RFP §16.2.7; criterion 11 |
| 11 | **Source, configuration and IaC**, delivered continuously | Continuous | RFP §19.1(6); `MQ-08` |

> **Item 11 is the most valuable provision in the RFP and it should not be traded in negotiation.**
> *"A milestone is not complete until the corresponding code is in the Company repository"* converts
> vendor exit from a recovery project into a personnel change, and it is the practical answer to
> `CO-002` §11 risk 5's concentration exposure. `SOW-33` makes it an acceptance condition rather
> than an aspiration.

---

## 4. The Deliverable Architecture

Four classes. Each has its own acceptance test, its own evidence standard and its own place in the
payment schedule. Mixing them is how acceptance disputes start.

| Class | Contents | Acceptance standard | Payment linkage |
|:--:|---|---|---|
| **D1 — System increments** | The 67 modules and 12 portals, wave by wave | **The 17-point Definition of Done** (RFP §12.5) — every item true, per module | The wave gate milestone |
| **D2 — Engineering artefacts** | The register's 140 documents, typed A/F/M/X (§5) | Type A: approved by the `PGD-000` approver. Types F and M: the fitness function, gate evidence or negative test named in §6.3 | **Entry condition** to the gate, not a milestone of its own |
| **D3 — Gate evidence** | The `GV-009` evidence pack: six dimensions, `SG-1`…`SG-11` standing criteria, per gate | `GV-009` §4's evidence classes `E1`–`E6` | The gate outcome itself |
| **D4 — Transition and knowledge** | Training delivery, runbooks, source and IaC, escrow, exit plan, 90-day transition assistance | §13; RFP §16.2.7, §19.2 | Final milestone and retention release |

> **`SOW-01` — D2 is an entry condition to a gate, never a milestone in its own right.** Paying
> separately for documents produces documents. Making them a **precondition to the payment for
> working software** produces documents that are true, because a specification nobody built against
> fails at `DoD-02` before it fails at review.

---

## 5. The Deliverable Schedule — D2

### 5.1 The typing rule

| Type | Applied when |
|:--:|---|
| **A — Author** | The document does not exist, **or** it recurs per wave / per release / per gate and each instance is a new artefact |
| **F — Conform** | The document exists and constrains how the system is built. The deliverable is **conformance, evidenced** |
| **M — Maintain** | The document exists and the build changes it. The deliverable is currency under `GV-011` `CM-17` |
| **X — Company** | 1000FiX produces, supplies or decides it. It enters the contract as a **dated dependency** (§8), not as a vendor deliverable |

**A document may carry more than one type.** `AR-001` is F (build in conformance) **and** M (the
architecture changes across nine waves). `QA-011` is F **and** A-per-wave (a new coverage report at
each gate). The types are obligations, not categories.

### 5.2 The register, typed

Enumerated from `PGD-000`'s seventeen category tables and from disk at **2026-08-19 02:36 (+06)**.

| Cat | Code | Docs | On disk | Primary types | Notes on the typing |
|:--:|:--:|---:|---:|---|---|
| 00 | `GV` | 11 | 11 | **X** | Programme governance is the Company's. The vendor **operates within** it (RFP §19.4) and that operation is a `SOW-27` obligation, not a deliverable |
| 01 | `RQ` | 10 | 10 | **X**, with `RQ-003` **A** | The Company owns its requirements. **`RQ-003`'s fit-gap is the vendor's to produce** — it is the analysis of what Odoo 19 CE and OCA already deliver, and no one else can do it |
| 02 | `AR` | 13 | 13 | **F + M** | The ARB holds architecture authority (`GV-002` §5.2). `AR-012`'s fitness functions are the conformance evidence |
| 03 | `DA` | 9 | 9 | **F + M** | `DA-002`'s residency classification is a build constraint, not advice |
| 04 | `IN` | 8 | 8 | **F + M**, with contract tests **A-per-interface** | The ~800-pair contract-test suite is authored per interface and is the acceptance evidence for the 47 integrations |
| 05 | `SC` | 11 | 11 | **F + M**, with `SC-003`, `SC-008` **X** | The DPIA and the regulatory register are the **controller's**, and the controller is 1000FiX |
| 06 | `UX` | 8 | 8 | **F + M**, with `UX-003` **A** | **`UX-003`'s screen inventory does not exist and is the class 5 driver in `GV-007` §6.1.** Whoever produces it converts the design estimate from class 5 to class 3 |
| 07 | `BE` | 9 | 9 | **F** | Build standards bind the vendor's own engineering. `BE-005`'s CD register is **F + M** and is where `H2-05`'s 70 colliding identifiers are resolved |
| 08 | `QA` | 11 | 11 | **F**, with `QA-011` **A-per-wave** | A coverage report per gate, against `QA-011`'s single denominator of 3,389 |
| 09 | `MG` | 7 | 7 | **F + M**, with `MG-002` **A** | **`MG-002`'s legacy profiling of 48 unprofiled sources is a vendor deliverable and a `GV-008` §6.3 risk-budget call** |
| 10 | `PE` | 9 | 9 | **F + M** | `PE-003`'s IaC standard makes `PE-002` §9.3's ephemerality real, which is worth $60K–$110K (`CO-005` §5.2) |
| 11 | `SV` | 6 | **6** | **F + M** | **Complete at the audit re-run.** `SV-005` **resolved `CVA-06`**: `OP-002` §4.3's per-wave durations sum to **56 weeks**, and §5.5 derives ≈ 678 PW across three pools. `CO-005` §6.4 takes that figure |
| 12 | `RL` | 6 | 6 | **F**, with `RL-002`, `RL-003` **A-per-wave** | A deployment plan and a readiness assessment per wave — **nine instances each**, not one |
| 13 | `CH` | 5 | 5 | **X**, with `CH-002` delivery **shared** | `GV-001` §6.3 charters change and content as **Company** workstreams. RFP §16.2.7 nonetheless prices train-the-trainer and knowledge transfer to the vendor — the boundary must be drawn in the contract. `SOW-Q-02` |
| 14 | `CO` | 6 | **5** | **X** | Commercial documents are the Company's. `CO-004`'s **register** is X; the vendor's **contribution** to it (its own dependency tree, its SBOM) is `SOW-34` |
| 15 | `BM` | 5 | **1** | **X** | Benefits are the Company's to claim and to measure. **`BM-002`'s baselines must be measured before the process changes** — a `SOW-27` dependency with a hard date |
| 99 | `RR` | 6 | **2** | **X**, with `RR-002` **shared** | `RR-002` is the identifier allocation authority and was authored during the audit window. Four remain |
| | **Total** | **140** | **131** | | |

**Verification** *(regenerated from the rows per `PG-M10`, at 2026-08-19 03:02 +06)*: registered
11 + 10 + 13 + 9 + 8 + 11 + 8 + 9 + 11 + 7 + 9 + 6 + 6 + 5 + 6 + 5 + 6 = **140** ✓ · on disk
11 + 10 + 13 + 9 + 8 + 11 + 8 + 9 + 11 + 7 + 9 + 6 + 6 + 5 + 5 + 1 + 2 = **131** ✓.

### 5.3 The seven documents that are genuinely the vendor's to author

Extracted from §5.2, because a list of 140 obscures the seven that matter. **One — `SV-005` — was
discharged by the Company on 2026-08-19, during this document's audit window, leaving six.**

| # | Document | Why the vendor, and nobody else | Needed by |
|:--:|---|---|---|
| 1 | **`RQ-003`** — fit-gap analysis | Only the party with production Odoo 19 CE and OCA experience can determine what is already delivered. `GV-008` §7.3 calls it *"the largest untested cost lever in the programme"* | **Before Wave 1 scope lock** |
| 2 | **`MG-002`** — legacy source profiling | 48 unprofiled sources; `GV-007` §7.3 records migration execution as unknowable until this completes | W1 |
| 3 | **`UX-003`** — screen inventory | Converts `GV-007` §6.1's class 5 driver to a count | **Before `GV-008` is re-baselined** |
| 4 | ~~**`SV-005`** — hypercare plan~~ **— discharged 2026-08-19** | Settled `CVA-06`: **56 weeks across nine waves**, ≈ 678 PW in three pools (`SV-005` §5.5). **The residual obligation is the vendor's ring-fenced pool 1 — 288 PW — which `SOW-13` makes contractual** | Discharged |
| 5 | **`RL-002` per wave** — deployment plan | Nine instances | Each wave, T−4 weeks |
| 6 | **`RL-003` per wave** — go-live readiness assessment | Nine instances | Each wave, T−2 weeks |
| 7 | **`QA-011` per wave** — coverage report | Nine instances, against the 3,389 denominator | Each gate |

> **`SOW-02` — an "A" deliverable that is not on this list is the Company's until the contract says
> otherwise.** The default matters: a vendor asked at Month 20 to produce a document nobody assigned
> will price it as a change, and will be entitled to.

### 5.4 Configuration control of the deliverable baseline

| # | Rule |
|---|---|
| **`SOW-03`** | Every deliverable in every class is a **configuration item** under `GV-011` §5, with a class, a version and a named approver |
| **`SOW-04`** | **The vendor may not approve its own deliverable.** `GV-011` `CM-16`; and it is the reason `GV-010` §3.2 exists |
| **`SOW-05`** | A change to a **baselined** deliverable increments its version and updates the item register **in the same change** (`GV-011` `CM-17`) |
| **`SOW-06`** | The **deliverable baseline is re-stated at each wave gate** and forms part of the gate pack. A deliverable that has silently drifted is a gate finding, not a discovery at contract close |

---

## 6. Acceptance

### 6.1 The acceptance standard

RFP §12.5: *"No module is accepted at a wave gate until every item is true. **This list is
contractually binding.**"*

| # | Criterion | Evidence class (`GV-009` §4) | Verifies or validates |
|---|---|:--:|:--:|
| `DoD-01` | Registered with ID, code, category, priority, wave and owners **before** its specification was written | E2 | V |
| `DoD-02` | All P0 and P1 requirements implemented and demonstrated | **E5** + E1 | Verify |
| `DoD-03` | Unit coverage ≥ 80%; **100% on financial and tax calculations** | **E5** | Verify |
| `DoD-04` | Business rules enforced at the model layer, verified by **negative tests through both UI and API** | **E5** | Verify |
| `DoD-05` | Domain events published through the outbox and registered in the event catalogue | E5 | Verify |
| `DoD-06` | APIs documented in OpenAPI 3.1 and published | E5 | Verify |
| `DoD-07` | Access control, record rules and field permissions **negative-tested for every applicable role** | **E5** | Verify |
| `DoD-08` | **Bengali translation complete for all user-facing strings** | E2 + E5 | Verify |
| `DoD-09` | KPIs instrumented with allocated `KPI-nnn` identifiers, visible in M25 | E5 | Verify |
| `DoD-10` | Migration mapping defined and **dry-run executed** where legacy data exists | E5 | Verify |
| `DoD-11` | Operational runbook written | E2 | Verify |
| `DoD-12` | Training material in **Bengali and English** for every affected role | E2 | Verify |
| `DoD-13` | **UAT executed and signed by named business super-users** | **E4** | **Validate** |
| `DoD-14` | Performance tested against applicable NFRs | **E5** | Verify |
| `DoD-15` | Security review complete, **zero open high or critical findings** | **E5** + E6 | Verify |
| `DoD-16` | Rollback plan documented **and rehearsed** | E1 + E4 | Verify |
| `DoD-17` | **Regulatory citations verified current, with a verified-on date** | E4 | Verify |

### 6.2 Verification and validation are not the same acceptance

Per ISO/IEC/IEEE 15288 §6.4.7 and §6.4.9:

| | Verification | Validation |
|---|---|---|
| Question | *"Was it built to the specification?"* | *"Is it the thing the business needs?"* |
| Evidence | Automated, mostly — `DoD-02`…`DoD-12`, `DoD-14`…`DoD-17` | **`DoD-13` alone** — named super-user sign-off |
| Who can give it | The vendor's own pipeline, audited | **Only a named 1000FiX super-user** |
| If it is missing | The gate fails on evidence | **The gate fails on authority** — nobody is entitled to say the software does the job |

> **`DoD-13` is the single point where this entire contract depends on a Company obligation that is
> currently unresourced.** `GV-007` §7.5: 134–201 super-users required, **none named**; `RSK-001`
> Critical. **A vendor can satisfy sixteen of the seventeen Definition-of-Done items entirely on its
> own, and cannot satisfy the seventeenth at all.** §8 makes the Company's side of it contractual,
> because an unfunded obligation that gates every payment is a dispute waiting for a date.

### 6.3 The acceptance procedure

| Step | Action | Timebox | Rule |
|:--:|---|---|---|
| 1 | Vendor submits the deliverable with its **evidence pack** and a completed DoD checklist | — | `SOW-07`: a submission without evidence is not a submission and does not start the clock |
| 2 | Company acknowledges receipt | **2 working days** | |
| 3 | Company reviews and responds: **accept**, **accept with observations**, or **reject with reasons** | **10 working days** for D1 and D2; **5** for D3 | `SOW-08` |
| 4 | On rejection, the vendor re-submits addressing every stated reason | 10 working days | `SOW-09`: the Company may not introduce **new** rejection reasons at re-submission that were available at first review |
| 5 | Re-review | 5 working days | |
| 6 | Unresolved after two rejection cycles → **escalation to the Steering Committee** | 10 working days | `SOW-10` |

| # | Rule |
|---|---|
| **`SOW-08`** | **Deemed acceptance after 15 working days of Company silence** — but only where the evidence pack was complete at step 1. Deemed acceptance is a discipline on the Company, and without it a vendor's cash flow is hostage to an unstaffed review queue |
| **`SOW-09`** | **Rejection reasons are stated in full at first review.** Iterative rejection — one reason per cycle — is the most common acceptance pathology and the most damaging to a fixed-price schedule |
| **`SOW-10`** | Two failed cycles escalate. **A deliverable in its third cycle is a scope disagreement, not a quality problem**, and is resolved under §11, not under §6 |
| **`SOW-11`** | **Acceptance of a deliverable is not acceptance of the wave.** Only the `GV-009` gate accepts a wave, and only the Steering Committee signs it (`GV-009` §6.4) |
| **`SOW-12`** | `GV-008` `CB-10`: **value is earned at the gate, not at the demo.** Work demonstrated but not accepted earns nothing |

### 6.4 `CVA-14` — the twelve portals have no Definition of Done

RFP §12.5 is headed **"Module Definition of Done"** and every criterion is written for a module.
`D-016` establishes that the twelve portals carry **298 PW outside the module figure**, and criterion
3 of the evaluation weights portal and mobile capability at 10% with a sub-50 elimination floor.

**Yet there is no acceptance standard for a portal.** Several module criteria do not transfer:
`DoD-05` (domain events through the outbox) is a backend property; `DoD-09` (KPIs visible in M25)
is a module instrumentation property; `DoD-10` (migration mapping) rarely applies.

**And the criteria a portal most needs are absent:**

| # | Portal criterion the module DoD does not contain | Source |
|:--:|---|---|
| `PDoD-01` | **Accessibility conformance** verified, to the level `UX-005` sets | `UX-005` |
| `PDoD-02` | **Bengali layout verified at 15–30% string expansion**, not merely translated | `UX-007`; `CON-05` |
| `PDoD-03` | **Offline behaviour** specified, tested and conflict-resolution verified | `AR-010`; `NFR-037`, `NFR-047` |
| `PDoD-04` | **Measured performance on a low-end Android device**, not on a developer handset | RFP §17.2 criterion 3; `NFR-076` |
| `PDoD-05` | **No business logic in the portal and no portal-held authoritative state** | `AS-01`…`AS-15`; §17.5 item 4 |
| `PDoD-06` | **Every portal API call is a published contract** with a contract test | `IN-002`, `IN-003` |
| `PDoD-07` | Session, token and consent handling verified against `SC-004` | `SC-004` |

> **`SOW-13` — the twelve portals are accepted against `DoD-01`…`DoD-04`, `DoD-06`…`DoD-08`,
> `DoD-11`…`DoD-17`, plus `PDoD-01`…`PDoD-07`.** The seven additional criteria are specified here
> because no document in the estate contains them and because `RSK-008` — technician rejection of
> the mobile application, **High likelihood / Critical consequence** — is a portal risk that the
> module Definition of Done cannot detect. Referred to `UX-008` and `QA-001` for adoption.

### 6.5 `CVA-13` — `DoD-17` needs a recurrence rule

`DoD-17` requires regulatory citations to be *"verified current, with a verified-on date"*. It says
nothing about **re-verification**, so a citation verified at the Wave 2 gate in Month 8 can be relied
on at the Wave 8 gate in Month 34 with a twenty-six-month-old date.

`GV-009` `SG-10` already fixes this on the Company's side — *"regulatory citations re-verified;
`RR-005` currency register updated"*, **P0 at every gate**. The contract does not.

> **`SOW-14` — `DoD-17` is re-performed at every subsequent gate for every module already accepted,
> not only for the wave's new scope.** This is the `C-04` / `H-01` recurrence the estate has already
> suffered twice — the Digital Security Act 2018 was superseded by the Cyber Security Ordinance 2025
> while documents still cited it — and `PG-M4` exists because of it. The cost is small and recurring;
> the failure is large and discovered at audit.

---

## 7. Payment

### 7.1 The milestone schedule

RFP §16.4, mapped to `GV-009` gates and `GV-008` §5.1 tranches.

| # | Milestone | % of implementation value | Gate | Tranche | Month |
|:--:|---|---:|:--:|:--:|:--:|
| 1 | Contract signature and mobilisation | 8% | — | T0 | 0 |
| 2 | Wave 1 gate passed | 12% | `G1` | T1 | 4 |
| 3 | Wave 2 gate passed | 12% | `G2` | T1 | 8 |
| 4 | Wave 3 gate passed | 12% | `G3` | T1 | 13 |
| 5 | **Wave 4 gate passed — v1.0 scope complete** | **14%** | **`G4`** | **T1 → T2 decision** | **18** |
| 6 | Wave 5 gate passed | 12% | `G5` | T2 | 22 |
| 7 | Wave 6 gate passed | 11% | `G6` | T2 | 26 |
| 8 | Wave 7 gate passed | 9% | `G7` | T2 | 30 |
| 9 | Wave 8 gate passed | 5% | `G8` | T2 | 34 |
| 10 | Wave 9 gate passed and programme closure accepted | 3% | `G9` | T2 | 36 |
| 11 | **Retention released after the 12-month warranty on the final wave** | **2%** | — | — | **48** |
| | **Total** | **100%** | | | |

**Verification** *(regenerated per `PG-M10`)*: 8 + 12 + 12 + 12 + 14 + 12 + 11 + 9 + 5 + 3 + 2 =
**100** ✓. Milestones 1–5 (T0 + T1, to the Wave 4 gate): 8 + 12 + 12 + 12 + 14 = **58%** ✓.

> **58% of the implementation value is payable by Month 18, at which point the complete v1.0
> commitment is delivered.** That is the commercial expression of `GV-008` §9 option B and `D-017`,
> and it is a well-constructed schedule: the Company can stop at the Wave 4 gate having paid 58% for
> 100% of what it originally committed to deliver. **`SOW-15`: milestone 5's 14% — the largest
> single milestone — is not reduced in negotiation**, because it is what makes the option-B exit
> real rather than theoretical.

### 7.2 What a milestone is contingent on

| # | Condition | Rule |
|:--:|---|---|
| 1 | The `GV-009` gate outcome is **PASS** (or CONDITIONAL PASS, per §7.4 once resolved) | `SOW-16` |
| 2 | **The corresponding source, configuration and IaC are in the Company repository** — RFP §19.1(6): *"a milestone is not complete until the corresponding code is in the Company repository"* | `SOW-33` |
| 3 | All D2 deliverables that are entry conditions to that gate are accepted | `SOW-01` |
| 4 | The `GV-009` evidence pack is complete and signed per §6.4 | `SOW-17` |
| 5 | No open Critical or High **security** finding in the wave's scope (`SG-1`, `DoD-15`) | `SOW-18` |

### 7.3 `CVA-10` and `CVA-12` — retention

**The ambiguity.** RFP §16.4's table carries milestone 11 as *"Retention released after the 12-month
warranty on the final wave — **2%**"*. The paragraph immediately below states: *"**5%** of each
milestone payment is retained and released at the wave's 12-month warranty expiry, subject to no
open Critical or High defects."*

These are two different mechanisms and the contract must not carry both without reconciling them:

| Reading | Effect |
|---|---|
| **A** — the 2% is a final holdback **and** 5% is retained from each of milestones 1–10 | At peak the Company holds 5% × 98% + 2% = **6.9%** of contract value. Each wave's 5% releases at that wave's warranty expiry; the 2% releases at Month 48 |
| **B** — the 2% **is** the aggregate retention, and the 5% paragraph describes how it accrues | Arithmetically impossible: 5% of 98% is 4.9%, not 2% |

> **`SOW-19` — reading A is adopted, and the contract states it in one place.** Peak retention is
> **6.9%**, each wave's 5% releases at that wave's 12-month warranty expiry, and the final 2%
> releases at Month 48. **Reading B does not reconcile**, and leaving the ambiguity in a signed
> contract means it is resolved by whoever has more leverage at Month 40, which will not be the
> Company.

**`CVA-12` — the tail.** Wave 1's gate is Month 4, so its retention releases at Month 16; Wave 9's
gate is Month 36, so its retention releases at **Month 48**. Warranty and retention administration
therefore run **twelve months past programme closure**, into a period `CO-005` §7.2 models as
run-state with no programme to administer them.

| # | Rule |
|---|---|
| **`SOW-20`** | The **warranty and retention administration obligation survives programme closure** and is named in the closure report as an ongoing Company responsibility with an owner — the CFO — not left to lapse with the PMO |
| **`SOW-21`** | Retention releases **only** on a defect position, not on the calendar: *"no open Critical or High defects"* is tested and evidenced at release, per `SV-002`'s severity definitions |

### 7.4 `CVA-11` — the conditional-pass conflict, which must be resolved before signature

**Two documents give opposite consequences for the same gate outcome:**

| Source | Provision | Funding released on a CONDITIONAL PASS |
|---|---|---:|
| **RFP §16.4** *(contractual — issued to the market)* | *"No milestone payment is released against a conditionally passed gate until the dated remediation plan is complete"* | **0%** |
| **`GV-009` §6.3** *(the Company's own gate handbook)* | *"Next wave starts. **Funding released at 80%**, balance on remediation closure"* | **80%** |

`GV-008` §5.3 aligns with `GV-009`. `CO-002`'s respondents will have priced against the RFP.

**Why this matters more than the 80 percentage points.** `GV-009` §6.3 also rules that a conditional
pass **starts the next wave**. Under the RFP's reading, the vendor is contractually required to begin
Wave *n*+1 while unpaid for Wave *n* — for however long remediation takes. **No vendor will accept
that, and one that does has mispriced.** The likely outcome is not a dispute at Month 20; it is a
premium in the bid, or a refusal to accept a conditional pass at all — which converts every
conditional pass into a `FAIL` negotiation and destroys the middle outcome `GV-009` created
deliberately.

| Option | Assessment |
|:--:|---|
| **Adopt `GV-009`'s 80%** | **Recommended.** It preserves the middle outcome, it is what the Company's own gate handbook and budget baseline already say, and it keeps the vendor solvent through a remediation the Company has agreed is acceptable |
| Adopt the RFP's 0% | Consistent with what respondents were told, but it makes CONDITIONAL PASS commercially indistinguishable from FAIL |
| Split — 80% on P1 remediation, 0% on P0 | **`GV-009` §6.3 already forbids the case this would cover**: a conditional pass requires *all P0-classified criteria met*. There is no such thing as a conditional pass with an open P0 |

> **`SOW-22` — a CONDITIONAL PASS releases 80% of the milestone; the balance releases on remediation
> closure, evidenced.** And because respondents were told 0%, **this change must be made by
> Addendum 1 alongside `CVA-02`'s corrections**, not introduced at negotiation with the preferred
> respondent — where it would be a unilateral improvement in the winner's terms after the field had
> priced against something else. `SOW-Q-01`; escalated to `GV-003`.
>
> **`SOW-23`** — `GV-009` §6.3's other rule is carried into the contract unchanged: **a second
> consecutive conditional pass on the same criterion is a FAIL.**

### 7.5 Invoicing, currency and set-off

| # | Rule |
|---|---|
| **`SOW-24`** | Invoices are raised **against an accepted milestone**, never against elapsed time or percentage completion |
| **`SOW-25`** | Payment terms: **30 days** from a valid invoice accompanied by a valid **Mushak 6.3** where the supplier is resident (`CO-005` §6.1) |
| **`SOW-26`** | **Invoice currency is USD** (RFP §16.2). The `SOW-32` FX mechanism, if adopted, operates as a separate adjustment and does not change the invoice currency |
| **`SOW-27`** | The Company may **set off** accrued service credits and liquidated damages against the next milestone, having given 10 working days' notice |

---

## 8. The Company's Obligations

**An SoW that binds only the vendor is not a Statement of Work; it is a wish list with penalties.**
ISO 37500 §7 and ISO 44001 both require the client's obligations to be as specific as the supplier's,
and `GV-007` §7.5 makes the case empirically: the programme's stated pacing constraint is Company
capacity, and none of it is resourced.

### 8.1 The dependency schedule — `SOW-28`

Each becomes a dated schedule to the contract. **A missed Company dependency is a recorded relief
event (§8.2), not a matter for argument.**

| # | Company obligation | Source | Due | Consequence if late |
|:--:|---|---|---|---|
| 1 | **Named super-users** — 2–3 per module, 134–201 people, with time **formally protected in their objectives** | `06-01` §4; `RSK-001`; `GV-007` §7.5 | **Before Wave 1 UAT** | `DoD-13` cannot be satisfied. **This gates every milestone** |
| 2 | **Module business owners** at 20%, per wave | `06-01` §4 | Per wave, T−4 weeks | Requirements sign-off and UAT slip |
| 3 | **Branch champions**, 1 per branch, 4 h/week | `06-01` §4; `CH-005` | W1–W5 | Rollout slips; `RL-004`'s tranche schedule fails |
| 4 | **Data owners** at 20% during migration | `06-01` §4 | W1–W5 | `MG-002` profiling and `DoD-10` dry runs stall |
| 5 | **Executive sponsor** — CEO, 4 hours/month | `06-01` §4; `CH-001` §5 | Monthly | Escalations unresolved; `CH-001` §5.2's sponsorship gap |
| 6 | **`RQ-001` baselined** and `GV-006` scope control operating | `GV-008` §5.3 T0 exit | **Before Wave 1** | `CR-02`'s *"agreed requirement set"* has no referent |
| 7 | **`BM-002` KPI baselines measured** | `BM-002`; `CC-09` | **Before the process changes, per wave** | ~BDT 396 lac of benefit becomes unclaimable. **Irrecoverable once the process has changed** |
| 8 | **`D-013` residency legal opinion (`DEP-31`)** | `SC-007` `Q-01` | Before W1 architecture freeze | `Z4`'s field set is unfixed; a later change is a notifiable migration |
| 9 | **`D-014` cost/scope decision** | `GV-003`; `CO-005` §11 | **Before Stage 6**, and before signature | The vendor is building to a scope the Company may cut |
| 10 | **`D-018` RMM agent decision** | `AR-013` §5.1 | W5 pilot | `M05`'s patch orchestration is unspecified |
| 11 | **`W0-01` OCA `field-service` v19 migration assessment** | `AR-013` §5.1 — **blocking** | **W0** | Build-vs-buy decision 2 is unresolved at Wave 1 start |
| 12 | **MinIO replacement decision** (`BEA-16`) | `BE-007` §7.1 — **W0, blocking Wave 1** | **W0** | Wave 1 object storage has no supported component |
| 13 | **Environments provisioned** per `PE-002` §8.2's sequence | `PE-002`; `PE-003` | Per the provisioning sequence | The vendor cannot build; `SG-3` fails |
| 14 | **`BD-R` site selected and provisioned** | `PE-001` §3.3; `SC-007-D-01` | **W1** | Residency-classified processing cannot start |
| 15 | **Test data and anonymised fixtures** | `QA-*`; `PE-002` §6 | Per wave | `SG-3` (no unmasked production data in non-production) is P0 |
| 16 | **Content estate delivered** — the 477-file workstream `GV-001` §6.3 charters to the Company | `AF-09`; `GV-001` | Per wave | `DoD-08` and `DoD-12` cannot be satisfied — **and they are the vendor's criteria** |
| 17 | **Training facilities, devices and the `training` environment** | `CH-002` §7.1, §9; `CO-006` | Per wave | `SG-7` (training before access) fails |
| 18 | **Timely acceptance decisions** within §6.3's timeboxes | This document | Continuous | `SOW-08` deemed acceptance |

> **Item 16 is the one that will surprise people.** `DoD-08` (Bengali translation complete) and
> `DoD-12` (training material in both languages) are **vendor** acceptance criteria, but the content
> estate that feeds them is a **Company** workstream under `GV-001` §6.3 — 477 files, 520–775 PW,
> and `CH-002` §7.1 records the establishment as unfunded. **A vendor cannot be held to an
> acceptance criterion whose input the Company has not delivered**, and a contract that tries will
> lose. `SOW-Q-02` requires the boundary to be drawn explicitly, per deliverable, before signature.

### 8.2 Relief events — `SOW-29`

| # | Rule |
|---|---|
| **`SOW-29`** | A failure of a §8.1 dependency is a **recorded relief event**: the vendor notifies within 5 working days, the Company acknowledges or disputes within 5, and an acknowledged event **extends the affected milestone date without cost** |
| **`SOW-30`** | **Relief extends time, not price**, unless the delay exceeds 20 working days, at which point demobilisation and remobilisation costs are recoverable **at the rate card**, capped |
| **`SOW-31`** | **An unnotified delay is not relievable.** A vendor that absorbs a Company failure silently and raises it at contract close has waived it. This protects both parties from a claim constructed retrospectively |
| **`SOW-32`** | Relief events are reported to the Steering Committee **monthly, cumulatively**. Three relief events on the same dependency is a governance failure, not a scheduling one |

---

## 9. Remedies

Placed with the party that controls the risk, per WorldCC practice.

| # | Failure | Remedy | Rule |
|:--:|---|---|---|
| 1 | Gate FAIL | Next wave does not start; no milestone payment; Steering Committee chooses extend / descope / escalate (`GV-009` §6.3) | `SOW-33` |
| 2 | Second consecutive conditional pass on the same criterion | Treated as FAIL | `SOW-23` |
| 3 | **Defect in warranty** | Rectification at the vendor's cost; **no payment for rework caused by respondent defect** (`CR-04`) | `SOW-34` |
| 4 | **SLA breach** in the support period | **Service credits** against the following period's fees, on a scale agreed at contract (RFP §16.4) and defined against `SV-002`'s severity model | `SOW-35` |
| 5 | **Key personnel substituted without approval** | See §12 | `SOW-40` |
| 6 | **Sustained material breach** | **Step-in rights** (RFP §19.2), exercisable because source and IaC are already in the Company repository | `SOW-36` |
| 7 | Termination for cause | 90 days' transition assistance, at no additional charge | `SOW-37` |
| 8 | Termination for convenience | 90 days' transition assistance, paid at the rate card; payment for accepted work only | `SOW-38` |
| 9 | Non-performance generally | **Performance bond or bank guarantee, 10% of contract value** (`CR-07`) | `SOW-39` |

| # | Rule |
|---|---|
| **`SOW-35`** | **Service credits are a price adjustment, not a penalty, and are drafted as such.** Under Bangladesh contract law a stipulated sum that is not a genuine pre-estimate of loss is vulnerable; a credit expressed as an abatement of the fee for a service not delivered is not |
| **`SOW-36`** | **Step-in is exercisable in practice, not only in principle.** It requires: current source in the Company repository (`SOW-33`), current IaC (`PE-003`), current runbooks (`DoD-11`, rehearsed under `SG-4`), and a named internal or third-party team able to receive it. **A step-in right without those four is a clause, not a remedy** |
| **`SOW-41`** | **Liability is capped at contract value, with the customary carve-outs**: death or personal injury, fraud, breach of confidentiality, IP infringement, and **breach of the data-protection obligations in §14**. The PDPA 2026 carve-out matters — a processor breach exposes the Company as controller, and that exposure is not bounded by the contract value |

---

## 10. Commercial Clauses the RFP Does Not Contain

`CO-005` §6 quantifies three exposures that no RFP clause addresses. Each is closed by one clause,
and each clause costs nothing to include and a great deal to omit.

### 10.1 `SOW-42` — tax: no gross-up

| Element | Provision |
|---|---|
| **The clause** | *"The Contract Price is inclusive of all taxes for which the Supplier is liable. The Company shall deduct or withhold any amount required by the laws of Bangladesh and shall account for it to the National Board of Revenue, and any such deduction shall be treated as payment of the corresponding part of the Contract Price. **The Company shall not gross up.**"* |
| **Why** | Bangladesh withholding on non-resident technical and professional services is **10%** for entities (20% for individuals). Absent this clause the supplier will seek a gross-up at the first payment, costing **11.1% of the offshore portion — $83K expected** (`CO-005` §6.2) |
| **Reciprocal obligation** | The Company issues the **withholding certificate** promptly, so the supplier can claim credit in its home jurisdiction. Withholding without documentation is a real cost to the supplier and will be priced |
| **Treaty relief** | Where a double-taxation agreement applies, the Company will co-operate in obtaining the **NBR certificate** authorising payment at the reduced rate. Co-operation is an obligation; the outcome is not warranted |
| **What must not be traded** | RFP §19.1(3) already requires pre-existing frameworks to be licensed *"perpetually, irrevocably and **royalty-free**"*. Royalty-free avoids the **20%** royalty withholding class entirely. **A lower headline price in exchange for a royalty-bearing licence is a worse deal than it looks** |

### 10.2 `SOW-43` — VAT

| Element | Provision |
|---|---|
| **The clause** | Prices are exclusive of Bangladesh VAT (RFP §16.2). A **resident** supplier issues a valid **Mushak 6.3** with every invoice as a condition of payment (`SOW-25`). For a **non-resident** supplier, VAT on imported services at 15% is withheld at payment and accounted for on the Company's **Mushak 9.1** |
| **Why** | Input rebate is unavailable without a valid Mushak 6.3. **A documentation failure converts 15% of the contract into a real cost** — up to $50K (`CO-005` §6.1) |
| **The dependency nobody has stated** | `M51`, the Mushak module, is a **Wave 3** deliverable. **For the first three years of contract payments the rebate rests on a manual process the ERP does not yet support.** `SOW-Q-03` |

### 10.3 `SOW-44` — foreign exchange

| Element | Provision |
|---|---|
| **The exposure** | All pricing is in USD; all benefit is in BDT. The Company bears **100%** of the FX risk over 36 months. The model's assumed rate of 110 is **11.5% from the verified rate of 122.70** (`CO-005` §6.7) |
| **Options** | **(a)** Accept the exposure and hedge externally — a treasury decision, not a contract one · **(b)** Price a defined portion in BDT, so the supplier bears the risk on its local cost base · **(c)** A **collar**: rates fixed while USD/BDT stays within a stated band, with a defined sharing mechanism outside it |
| **Recommendation** | **(b) for the onshore portion, (a) for the offshore.** A local implementation partner under `MQ-04` has a **BDT cost base** and is the natural bearer of BDT risk on that portion; asking an offshore supplier to bear BDT risk simply buys the hedge back at a worse rate |
| **Evaluation linkage** | `CO-002` §8.2 rule 4 scores FX-sharing proposals under criterion 13 |

### 10.4 `SOW-45` — escalation

| Element | Provision |
|---|---|
| **The clause** | Rates fixed for **24 months**; thereafter capped at **Bangladesh CPI or 5% per annum, whichever is lower** (RFP §16.2.11) |
| **The context to hold in negotiation** | Bangladesh general CPI was **8.32%** in July 2026 and non-food **9.28%** (verified 2026-08-19). **The 5% cap therefore binds**, transferring 3–4 points a year of wage inflation to the supplier from Month 25 |
| **The consequence** | A rational supplier prices that into its **initial** rate. `CO-005` §6.8 carries **+7% expected** for this. **`CO-002` §8.3 test 4 exists to detect a bid that has not** — such a bid will seek recovery through change requests under `CR-03` |
| **`SOW-46`** | **The rate card is fixed for the whole term for change requests as well as for baseline work** (`CR-03`: *"change requests priced from the published rate card, never renegotiated per change"*). This is the single most effective anti-claim provision in the RFP and must survive negotiation |

---

## 11. Change Control

### 11.1 The interface

Three change mechanisms exist and they must not diverge.

| Mechanism | Owns | Rule |
|---|---|---|
| **`GV-003` §6** | Programme decisions and their change control | The programme record |
| **`GV-006`** | Scope baseline control — what `CR-02`'s *"agreed requirement set"* refers to | The scope record |
| **This contract, §11** | The **commercial** consequence of a change | The money |

| # | Rule |
|---|---|
| **`SOW-47`** | A contractual change is **first** a `GV-003` decision. **A change request priced and agreed without a `GV-003` record is not a change; it is an undocumented scope movement**, and it is the mechanism by which `H-02`'s 834 PW became 3,022 |
| **`SOW-48`** | `CR-02`: effort and cost per wave are **re-baselined at wave start** against the agreed requirement set; variance beyond **±10%** requires Steering Committee approval. **The re-baseline is against `GV-006`'s baseline, not against the vendor's estimate** |
| **`SOW-49`** | `CR-03`: change requests are priced **from the published rate card**, never renegotiated per change |
| **`SOW-50`** | `CR-04`: **no payment for rework caused by supplier defect or misunderstanding of a documented requirement.** The word *documented* is load-bearing: it is why `GV-006`'s baseline and `GV-011`'s configuration control are contractual preconditions and not merely good practice |
| **`SOW-51`** | `CR-06`: **the Company does not pay for supplier learning** of the Odoo platform or the Bengali language |
| **`SOW-52`** | **Every change request states its effect on the `CO-005` TCO**, not only on the contract price. A change that adds an L6 component or an environment changes the five-year position, and `TCO-15` requires it to be modelled before signature |

### 11.2 Descope — `SOW-53`

`CR-08` permits the Company to award the whole programme, a subset of waves, or a subset of
categories. `D-014` and `GV-008` §9 make a descope live.

| # | Rule |
|---|---|
| **`SOW-53`** | The contract is structured so that **`OPT-01`…`OPT-12` can be removed at a wave or category boundary without stranding cost**, and the removal price is fixed at contract, not negotiated at removal |
| **`SOW-54`** | `CC-05`: **each removal states the benefit forgone.** Category D alone carries BDT 125 lac of rental and refurbishment margin. A descope decision taken on cost alone is half a decision |
| **`SOW-55`** | **`OPT-05` (M66, M67) is priced but not awarded** until their specifications exist. Awarding an unspecified module at a fixed price converts the fixed price into a change request on day one |

---

## 12. Key Personnel

`CO-002` §11 risk 2 identifies bench-and-swap as a known post-award risk. RFP §15.4 `VQ-36`
requires approval for substitution but attaches no consequence, which makes it a request rather than
an obligation.

| # | Rule |
|---|---|
| **`SOW-56`** | The **named key personnel and their committed time percentages** (`VQ-23`…`VQ-36`, recorded at `CO-002` `VES-23`) form **Schedule 3** to the contract |
| **`SOW-57`** | Substitution requires **written Company approval**, and the proposed substitute must be **of equal or better calibre**, assessed by the same interview standard used at Stage 4 |
| **`SOW-40`** | **Substitution without approval is a material breach**, and attracts: (a) suspension of the next milestone payment until an approved substitute is in post; (b) a **30-working-day handover overlap at the supplier's cost**; and (c) a Steering Committee escalation |
| **`SOW-58`** | Key personnel are subject to a **minimum commitment period**: the Programme Manager, Solution Architect and Odoo Technical Lead for **the whole term**; wave-specific leads for **their wave plus the following hypercare** |
| **`SOW-59`** | **Departure through resignation is not a breach**, but it triggers the same handover overlap. The distinction matters: penalising a supplier for an employee's free choice is unenforceable and sours the relationship; requiring a handover is neither |

---

## 13. Intellectual Property, Source, Escrow and Exit

| # | Provision | Source | Rule |
|:--:|---|---|---|
| 1 | **All customisations, configurations, custom modules, services, applications, migrations, test suites, documentation and training material created for 1000FiX are owned by 1000FiX** | RFP §19.1(3) | `SOW-60` |
| 2 | Pre-existing proprietary frameworks remain the supplier's, **must be declared in the Exceptions schedule**, and are licensed **perpetually, irrevocably and royalty-free** | RFP §19.1(3) | `SOW-61` |
| 3 | **All data belongs to 1000FiX**; full export in open, documented formats **at any time, not only at termination** | RFP §19.1(5) | `SOW-62` |
| 4 | **Source, configuration and IaC delivered continuously** to a Company-controlled repository; **a milestone is not complete until the code is there** | RFP §19.1(6); `MQ-08` | **`SOW-33`** |
| 5 | **Source-code escrow for any proprietary component** | RFP §19.2 | `SOW-63` |
| 6 | Open-source obligations complied with; **OCA migrations contributed upstream**; a licence register maintained | RFP §19.1(4) | **`SOW-34`** |
| 7 | 90 days' transition assistance on termination, for cause or convenience | RFP §19.2 | `SOW-37`, `SOW-38` |

| # | Rule |
|---|---|
| **`SOW-61`** | **The Exceptions schedule is scrutinised at Stage 6, not at contract.** A supplier that reserves a framework on which the system's core depends has converted a royalty-free perpetual licence into a dependency, and the time to find that out is before the preferred respondent is named. `CO-002` §10 item 7's discipline applies |
| **`SOW-34`** | The supplier's obligation under RFP §19.1(4) is discharged **into `CO-004`'s register**, not into a document of its own. Specifically: a **CycloneDX 1.7 SBOM per artefact** (`BE-007` §8), an **SPDX 3.0.1 export on request**, and an entry in `CO-004` §5 for every gated licence it introduces |
| **`SOW-64`** | **The supplier may not introduce an AGPL, BSL, TSL or fair-code component without architecture approval** (`BE-007` `LX-02`; `AR-013` `LW-02`), and **may not modify an AGPL component at all** without a Chief Architect approval and a published-source plan (`BE-007` `LX-26`). A breach is a material breach, because it creates a **disclosure obligation on 1000FiX**, not on the supplier |
| **`SOW-63`** | **Escrow is verified, not merely lodged.** An annual escrow verification — that the deposit builds, from the deposited materials, to the running version — is a condition of the retention release. An unverified escrow deposit is a filing cabinet |
| **`SOW-65`** | The **exit plan is a deliverable at the Wave 4 gate**, not at termination. `AR-013` `L6-05` requires every L6 component to have a documented exit; the same principle applies to the supplier relationship, and the moment to write it is when relations are good |

---

## 14. Data Protection

RFP §19.2 requires *"a data processing agreement under the PDPA 2026, with sub-processor control."*
`SC-003`'s DPIA is the controller-side assessment this must be consistent with.

| # | Provision | Rule |
|:--:|---|---|
| 1 | 1000FiX is **controller**; the supplier is **processor**. Every processing operation is on documented instructions | `SOW-66` |
| 2 | **Sub-processors require prior written authorisation**, and the list is obtained at Stage 6 (`CO-002` §10 item 6), not at contract | `SOW-67` |
| 3 | **A sub-processor in a jurisdiction incompatible with `SC-007`'s residency design may not be authorised.** This is an architectural constraint, not a commercial preference | `SOW-68` |
| 4 | **No production personal data in any non-production environment** without masking and a lawful basis (`GV-009` `SG-3`, P0; `CON-14`) | `SOW-69` |
| 5 | Personal-data breach notification to the Company **within 24 hours** of the processor becoming aware — tighter than the statutory notification the Company itself owes, because the Company's clock starts when it is told | `SOW-70` |
| 6 | Assistance with **data-subject rights**: access, rectification, erasure, portability — the `D-07` demonstration scenario in operational form | `SOW-71` |
| 7 | **Deletion or return of all personal data at the end of processing**, evidenced, with the backup-retention tension in `PE-007` §4.6 addressed explicitly rather than left to conflict | `SOW-72` |
| 8 | **Audit rights**, including the right for 1000FiX and, under `PE-001` §12, a counterparty's regulator, to audit the processing | `SOW-73` |

> **`SOW-74` — the data-protection obligations sit outside the liability cap** (`SOW-41`). A
> processor breach exposes 1000FiX as controller to PDPA 2026 consequences that are not bounded by
> the contract value, and a cap that includes them transfers an unbounded risk to the party that
> does not control it.

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `SOW-Q-01` | **Is the conditional-pass funding consequence 0% (RFP §16.4) or 80% (`GV-009` §6.3)** — and will the resolution be issued by addendum so all respondents price the same term? | CFO with Steering Committee | **17 Sept 2026** | `CVA-11`; §7.4; every bid's cash-flow model |
| `SOW-Q-02` | **Where exactly does the content and training boundary fall** between the Company's chartered workstreams (`GV-001` §6.3) and RFP §16.2.7's priced scope? | Programme Director | **Before signature** | `DoD-08`, `DoD-12`; §8.1 item 16; `CH-002` |
| `SOW-Q-03` | Since **`M51` is a Wave 3 deliverable**, what manual process supports Mushak 6.3 input rebate on contract payments in Years 1–3? | CFO | **Before the first invoice** | `SOW-43`; `CO-005` §6.1 |
| `SOW-Q-04` | **Is retention 6.9% at peak (reading A)?** | CFO with Legal | Before signature | `CVA-10`; §7.3 |
| `SOW-Q-05` | Who administers **warranty and retention in Months 37–48**, after programme closure? | CFO | Before closure | `CVA-12`; `SOW-20` |
| `SOW-Q-06` | Will the Company adopt **`SOW-44` option (b)** — a BDT-priced onshore portion? | CFO with Treasury | Stage 6 | `CO-005` §6.7; `CO-002` §8.2 rule 4 |
| `SOW-Q-07` | **Are `PDoD-01`…`PDoD-07` adopted** as the portal acceptance standard, and by which document? | Chief Architect with QA Lead | **Before Wave 1** | `CVA-14`; §6.4; `UX-008`, `QA-001` |
| `SOW-Q-08` | **Will the 134–201 super-users be named and their time protected** before Wave 1 UAT? | CEO with HR Director | **Before Wave 1 UAT** | `DoD-13`, and therefore **every milestone**. `RSK-001` |
| `SOW-Q-09` | Does `CR-09` apply — **more than one supplier**? If so, who owns the integration seam between them? | Steering Committee | Stage 6 | The whole contract structure |
| `SOW-Q-10` | What is the **service-credit scale** RFP §16.4 leaves *"to be agreed at contract"*? | CFO with Service Manager | Before signature | `SOW-35`; `SV-002` |
| `SOW-Q-11` | **Which enumeration of `PGD-000` is the contractual one?** The register moved by eight documents in twenty-six minutes during this document's audit. The Statement of Work must name a **frozen enumeration by timestamp** as its Schedule 1, or the deliverable list is a moving target | **Head of Procurement with `GV-011`** | **Before signature** | §1.1, §5.2; the whole of §5 |

> All eleven are escalated to `GV-005` RAID at issue. `SOW-Q-01`, `SOW-Q-08` and `SOW-Q-02` are the
> three that can stop the programme.

---

## 16. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `CO-003-D-01` | How to express the register in the SoW | List all 140 as deliverables to be authored · **Type them A/F/M/X** | **Type them** | 123 of 140 already exist. Listing them as authorship deliverables would pay a supplier to re-author the Company's own governance and would leave the real obligation — conformance, evidenced — unstated | §5. **Seven documents are genuinely the supplier's to author**, and §5.3 names them |
| `CO-003-D-02` | Whether D2 documents are paid milestones | Pay per document · **Entry conditions to the gate** | **Entry conditions** | Paying for documents produces documents. Making them preconditions to payment for working software produces documents that are true | `SOW-01` |
| `CO-003-D-03` | The conditional-pass funding conflict | RFP's 0% · **`GV-009`'s 80%** · A split | **80%, by addendum** | 0% requires the supplier to start the next wave unpaid, which makes CONDITIONAL PASS commercially identical to FAIL and destroys the middle outcome `GV-009` created deliberately | `SOW-22`; `CVA-11`; must be issued by Addendum 1, not conceded at negotiation |
| `CO-003-D-04` | Retention reading | Reading B (2% aggregate) · **Reading A (5% per milestone + 2% final)** | **Reading A** | Reading B does not reconcile arithmetically: 5% of 98% is 4.9%, not 2% | `SOW-19`; peak retention **6.9%** |
| `CO-003-D-05` | Whether to specify a portal Definition of Done | Rely on the module DoD · **Specify `PDoD-01`…`PDoD-07`** | **Specify** | 298 PW and the programme's most dangerous adoption risk (`RSK-008`) sit behind an acceptance standard written for modules | `SOW-13`; `CVA-14`; referred to `UX-008` and `QA-001` |
| `CO-003-D-06` | Whether to include deemed acceptance | No — it lets defects through · **Yes, at 15 working days, conditional on a complete evidence pack** | **Yes, conditional** | Without it the supplier's cash flow depends on an unstaffed Company review queue, and `GV-007` §7.5 shows the queue will be unstaffed. The condition — a complete evidence pack — prevents it from becoming a loophole | `SOW-08` |
| `CO-003-D-07` | Whether to contract the Company's own obligations | Manage them internally · **Schedule them in the contract with dates** | **Schedule them** | `RSK-001` is Critical, none of the 134–201 super-users is named, and `DoD-13` gates every milestone. An unfunded obligation that gates payment is a dispute with a date | §8; `SOW-28`, `SOW-29` |
| `CO-003-D-08` | Where FX risk sits | Company bears all (status quo) · Supplier bears all · **Split by cost base** | **Split by cost base** | A local partner with a BDT cost base is the natural bearer of BDT risk on its portion; an offshore supplier asked to bear it simply sells the hedge back at a worse rate | `SOW-44` option (b) for onshore, (a) for offshore |
| `CO-003-D-09` | Liability cap treatment of data protection | Inside the cap · **Carved out** | **Carved out** | A processor breach exposes the Company as controller to consequences not bounded by contract value. A cap that includes them transfers an unbounded risk to the party that does not control it | `SOW-74` |

---

## 17. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | **Every one of the register's 140 documents is typed** A/F/M/X, and the counts are verified against a disk enumeration with a **stated timestamp**, re-run at audit | §1.1, §5.2; `enumeration_timestamp`; `SOW-Q-11` |
| `AC-02` | The documents that are **genuinely the supplier's to author** are named and dated | §5.3 — seven, of which one was discharged at audit, plus the per-wave instances |
| `AC-03` | The **17-point Definition of Done** is mapped to `GV-009` evidence classes and separated into verification and validation | §6.1, §6.2 |
| `AC-04` | A **portal acceptance standard** exists | §6.4; `PDoD-01`…`PDoD-07` |
| `AC-05` | The **acceptance procedure** has timeboxes on both parties, and deemed acceptance protects the supplier from Company delay | §6.3 |
| `AC-06` | The **eleven payment milestones** are verified to sum to 100% and mapped to gates and tranches | §7.1 |
| `AC-07` | **Every Company obligation** is scheduled with a date and a consequence | §8.1 — eighteen |
| `AC-08` | The **three commercial exposures** `CO-005` quantifies are each closed by a named clause | §10; `SOW-42`, `SOW-43`, `SOW-44`, `SOW-45` |
| `AC-09` | Every one of `CO-002` §11's **five selection risks** maps to a named clause | §12, §11.2, §8, §13 |
| `AC-10` | The **two RFP/`GV-009` conflicts** are stated, resolved with a recommendation, and routed to a decision | §7.3, §7.4; `CVA-10`, `CVA-11` |
| `AC-11` | **Step-in is shown to be exercisable**, with its four preconditions named | `SOW-36` |
| `AC-12` | The local rule prefix `SOW-nn` was **verified to zero occurrences** workspace-wide before allocation | Header note |

**Definition of done.** This document is complete when every criterion above is met, `SOW-Q-01`,
`SOW-Q-02` and `SOW-Q-04` are resolved, Legal Counsel confirms the specification is draftable under
Bangladesh law, and `PGD-000` records `CO-003` as ✅ with a fresh enumeration date.

---

## 18. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `CO-001` — the RFP | §12.4, §12.5, §14, §16.4, §16.5, §19 are the contractual terms this document specifies against |
| Upstream | `CO-002` | Supplies the counterparty and the five risks §9 and §12 mitigate |
| Upstream | `CO-005` | Supplies the price basis and the three exposures §10 closes |
| Upstream | `GV-009` | Supplies the gate outcomes §7 pays against. `CVA-11` is the conflict between it and the RFP |
| Upstream | `GV-008` | Supplies the tranche structure §7.1 maps to; `CB-09` (commitment) and `CB-10` (earned at the gate) |
| Upstream | `GV-003`, `GV-006`, `GV-011` | Change control, scope baseline and configuration control — §11's contractual interface |
| **Downstream** | **Every category in `PGD-000`** | §5 is what makes each category's documents contractually owed. **This is the document `PGD-000` names as the one that makes the register enforceable** |
| Downstream | `CO-004` | `SOW-34` and `SOW-64` discharge the supplier's licence obligations into its register |
| Downstream | `SV-002` | `SOW-35`'s service credits are defined against its severity model |
| Downstream | `SV-005` | **Settled `CVA-06` on 2026-08-19.** `SOW-13`'s acceptance and `SOW-22`'s milestone consequence now rest on its 56-week, three-pool derivation |
| Downstream | `UX-008`, `QA-001` | `PDoD-01`…`PDoD-07` referred for adoption |
| Downstream | `RL-002`, `RL-003`, `QA-011` | Named as A-per-wave deliverables — nine instances each |
| Lateral | `SC-003`, `SC-007` | §14's DPA must be consistent with the DPIA and the residency design |
| Lateral | `GV-005` | Ten open questions escalated at issue |

---

## 19. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./CO-002_Vendor_Evaluation_and_Selection_Report.md` ·
`./CO-004_Licence_and_Open_Source_Compliance_Register.md` ·
`./CO-005_Total_Cost_of_Ownership_Model.md` · `./CO-006_Procurement_and_Purchase_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-003_Decision_Log_and_Change_Control_Procedure.md` ·
`../00_Programme_Governance_and_Control/GV-006_Scope_Management_and_Baseline_Control_Procedure.md` ·
`../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-008_Programme_Budget_and_Cost_Baseline.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md` ·
`../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md` ·
`../05_Security_Privacy_and_Compliance/SC-003_Data_Protection_Impact_Assessment_PDPA_2026.md` ·
`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-007_Dependency_Licence_and_SBOM_Management_Standard.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-002_Environment_Strategy_and_Specification.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-003_Infrastructure_as_Code_Standard.md` ·
`../11_Service_Operations_and_Support/SV-002_Platform_SLA_OLA_and_Internal_Service_Catalogue.md` ·
`../12_Release_Deployment_and_Transition/RL-002_Deployment_Plan_and_Go_Live_Checklist.md` ·
`../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md` ·
`../13_Training_Change_and_Adoption/CH-002_Training_Plan_and_Delivery_Schedule.md`

**Workspace**
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` — §12, §14, §16, §19 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md` — hypercare duration and the eighteen `HX` exit criteria

**External standards** *(all verified 2026-08-19)*

| Source | Used for |
|---|---|
| **ISO 9001:2015 §8.4** — control of externally provided processes, products and services | §5's typing, §6's verification regime, §9's controls. **Obligatory**, because RFP §19.3 requires 1000FiX to maintain ISO 9001 throughout |
| **ISO/IEC/IEEE 12207:2017** §6.1.1, §6.1.2 — acquisition and supply processes | §4's deliverable classes; §11's change control |
| **ISO/IEC/IEEE 15288:2023** §6.4.7, §6.4.9 — verification and validation | §6.2's separation of `DoD-13` from the other sixteen |
| **ISO 21502:2020** §7.14 | §7, §11 |
| **ISO 37500:2014** §7 — outsourcing transition and governance | §8's Company obligations; §13's exit |
| **ISO 44001:2017** stages 5–7 | §9, §11, §13.5. *(ISO/DIS 44001 in the enquiry phase — `CO-002` `VES-Q-06`)* |
| **ISO 10007:2017** | §5.4's configuration control, delegated to `GV-011` |
| **WorldCC** contracting principles — balanced risk allocation | §9, §10 |
| **Bangladesh Contract Act 1872**; **Arbitration Act 2001** | `SOW-35`'s drafting as abatement not penalty; RFP §19.1(9)–(10)'s governing law and arbitration |
| Bangladesh withholding rates — non-resident technical/professional services 10% (entities) / 20% (individuals); royalties 20%; resident services 5%; NBR treaty certificates | `SOW-42` |
| Bangladesh VAT — imported services at 15% withheld at payment; input rebate requires a valid Mushak 6.3; Mushak 9.1 return | `SOW-43` |
| Bangladesh CPI, July 2026 — general **8.32%**, non-food **9.28%** | `SOW-45` |

> Verify every path resolves before issuing. Nine module files carried references to superseded
> filenames until the August 2026 audits corrected them.

---

## 20. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Chief Financial Officer with Legal Counsel and Enterprise Architecture | Initial issue. Types all 140 registered documents A/F/M/X against a disk enumeration of 123. Raises `CVA-10` (retention ambiguity), **`CVA-11` (the conditional-pass funding conflict — High)**, `CVA-12` (warranty tail past closure), `CVA-13` (`DoD-17` has no recurrence rule) and `CVA-14` (the twelve portals have no Definition of Done). Specifies `PDoD-01`…`PDoD-07` | Board of Directors |

---

*`CO-003` · Category 14 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
