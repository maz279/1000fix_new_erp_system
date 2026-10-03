---
id: RL-003
title: Go-Live Readiness Assessment and Gate Criteria
category: 12 — Release, Deployment & Transition
code: RL
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Management Office
approver: Programme Director, endorsed by the ERP Steering Committee
standards_basis: >
  ISO 21502:2020 §6.4 gates and decision points, applied below the programme gate ·
  UK IPA / OGC Gateway Review practice — Gate 4 "Readiness for Service" ·
  PRINCE2 7th Edition (2023) stage boundary and end-stage assessment ·
  ISO 9001:2015 §8.6 release of products and services ·
  GV-009 §4 evidence classes E1…E8, inherited unchanged
traces_to: >
  PGD-000 RL-003 row (⛔) · _CATEGORY_OVERVIEW seven readiness dimensions ·
  GV-009 §3.3 six dimensions, §4 evidence classes, §5 assessors, §6 gate process, §9.1 SG-1…SG-11 ·
  DM-014 C2 and C7 · CM-012 RB-01…RB-12 · OP-002 §4.7 · 06-02 §4 (70 gate criteria) ·
  QA-001, QA-006, QA-007, QA-008, QA-009, QA-010, QA-011 (all cite RL-003 as consumer) ·
  MG-004, MG-006 · BE-003 §9 step 6 (mis-citation, corrected in RL-001 §9.4)
depends_on: >
  GV-009 (issued) · QA-001…QA-011 (issued) · MG-004, MG-006 (issued) · RL-001, RL-002 (issued) ·
  SC-003, SC-009 (issued) · UX-005 (issued) · SV-001, SV-002, SV-003 (ISSUED 2026-08-19) ·
  PE-002, PE-007 (ISSUED 2026-08-19) · CH-002, CH-004, CH-005 (ISSUED 2026-08-19) ·
  SV-004, SV-005 (ISSUED 2026-08-19) · SV-006 (ABSENT ◐) · CO-003 Statement of Work (ABSENT ⛔)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-18 23:27 (+06)
rule_prefix: GLR — verified unused across all 777 markdown files of the workspace, re-verified at audit 2026-08-19 02:10 (+06)
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RL-003 — Go-Live Readiness Assessment and Gate Criteria

### Category 12 · Code `RL` · Rule space `GLR` · ISO 21502:2020 §6.4 · IPA Gateway 4 · `GV-009` evidence model

---

> **`PGD-000` records this document as ⛔ with the note:** *"`06-02` §4 lists wave-gate criteria. It
> does not define readiness **assessment** — who checks, against what evidence, with what authority
> to stop a go-live."*
>
> **That note was written before `GV-009` existed, and `GV-009` has since discharged most of it.**
> `GV-009` §4 defines eight evidence classes, §5 names an assessor per dimension with an
> independence requirement, and §6.3 defines the consequence of a failed gate. A document that
> restated any of that would be a duplicate.
>
> §2.4 states what is actually left, and this document does only that.

---

## 1. Purpose

A **wave gate** is a programme decision taken nine times by the Steering Committee about scope,
funding and benefits. A **go-live** is an operational event that happens many more than nine times,
at named sites, on named dates, and its question is narrower and more urgent: *can these people, at
these places, run the business on this system from tomorrow morning?*

This document supplies the **instrument that answers that question**: seven dimensions, a named
assessor per dimension holding a veto, an evidence requirement per dimension, a scoring rule that
refuses to average, a re-assessment rule for when a date slips, and a form.

Its output is not a decision. It is the **evidence on which two existing decisions are taken** —
`DM-014` `C7` and the `GV-009` wave gate.

### 1.1 The thing this document deliberately does not do

> **`GLR-01`. This document does not create a new go/no-go decision.** The programme already has
> four, and a fifth would be the defect, not the fix.

| # | Existing decision | Taken by | When | About |
|:--:|---|---|---|---|
| 1 | **`C2` — branch readiness** (`CM-012`, `DM-014`) | Change Lead + Branch Operations Lead | T−3 days | Whether **a site** cuts over |
| 2 | **`C7` — cutover go/no-go** (`DM-014` `CV-14`) | **CTO with the Programme Director**, non-delegable | End of `P2` | Whether **the data load stands and the business starts** |
| 3 | **The wave gate** (`GV-009` §3.2) | **ERP Steering Committee** | At the milestone | Whether the **next wave** is scoped and funded |
| 4 | **The rollback decision** (`OP-002` §4.7) | Varies by trigger; PM + CFO, PM + Ops Director, CFO, or CTO | During hypercare | Whether to **go back** |

> **The `_CATEGORY_OVERVIEW` proposed that this document give *"seven assessors a documented
> veto"*.** It is adopted — but the veto lands **into `C7`**, not into a new decision of this
> document's own. A veto that stops a go-live is `C7` saying no. A veto that stops a wave is the
> Steering Committee saying no. This document determines what those two bodies are told.

### 1.2 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **seventh dimension** `GV-009` does not have, and why it is needed (§3) |
| 2 | The **assessor and veto model** — who holds each dimension's veto and what it stops (§4) |
| 3 | The **evidence requirement per dimension**, in `GV-009`'s `E1`…`E8` classes (§5) |
| 4 | **Scoring** — RAG per dimension, and the rule that readiness is never averaged (§6) |
| 5 | The **assessment timeline**, reconciled across `GV-009`, `CM-012` and `DM-014` (§7) |
| 6 | The **readiness assessment form** (§8) |
| 7 | **Re-assessment when the date slips** (§9) |
| 8 | **Conditional readiness** — what may carry an open item and what may not (§10) |
| 9 | The **assessor roles that do not exist**, and the interim position (§11) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The 70 wave-gate criteria `G1-01`…`G9-05` | `06-02` §4 | Authoritative; `GV-009` §3.1 already ruled them so |
| Evidence classes `E1`…`E8` and rules `GA-01`…`GA-12` | `GV-009` §4 | **Inherited unchanged.** §5 uses them; it does not redefine them |
| Standing criteria `SG-1`…`SG-11` | `GV-009` §9.1 | Consumed as dimension inputs; not restated |
| The gate process, report, outcomes and signature | `GV-009` §6 | Programme-level; this document feeds it |
| Branch-level readiness domains `D1`…`D8` | `CM-012` §4.1 | **Adopted by citation.** §4.7 states the relationship |
| Defect thresholds | `QA-010` §5 | An input to dimension `RD-1`, not restated |
| Cutover checkpoints `C1`…`C9` and triggers `T1`…`T7` | `DM-014` | This document's output is an input to `C7` |
| The deployment checklist | `RL-002` §8 | Evidence for dimension `RD-2` |
| Whether to roll back after go-live | `OP-002` §4.7 | A different decision at a different time |

### 1.3 Intended audience

| Audience | What they use this document for |
|---|---|
| Programme Management Office | The whole document. The PMO runs the assessment |
| The seven dimension assessors | §4 (their veto), §5 (their evidence), §8 (the form they sign) |
| CTO and Programme Director | §6 and §8 — what they are handed before taking `C7` |
| Steering Committee | §6.4 — how a readiness position is reported into a gate without being confused with one |
| Change Lead and Branch Operations Lead | §4.7 — how `C2` site readiness rolls into `RD-5` |
| Business owners | §5.1 — what "functionally ready" is evidenced by, so it is not argued at T−1 |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 21502:2020** | §6.4 gates and decision points | §7's timeline places a decision point below the programme gate, with defined entry evidence and a defined output | **Departure:** ISO 21502 addresses gates at project and programme level. This instrument sits *below* the lowest gate it describes, because a nine-gate programme rolling out to 51+ sites has more go-live events than gates |
| **IPA / OGC Gateway** | **Gate 4 — Readiness for Service** | The seven dimensions are a Gateway 4 review reduced to an operable form: is the solution ready, is the business ready, is the service ready, is the contract ready | Gateway 4 is a peer review by external reviewers. §11 records that the programme has no independent reviewer before Gate 4 (`GV-009` `GA-09`), so the cross-assessment rule substitutes |
| **PRINCE2 7 (2023)** | Stage boundary; end-stage assessment | §9's re-assessment rule and §10's conditional model follow the exception-and-tolerance pattern | None |
| **ISO 9001:2015** | §8.6 — release only when planned arrangements are satisfactorily completed | §6.2's non-averaging rule is §8.6 stated numerically: *satisfactorily completed* is per arrangement, not on aggregate | None |
| **`GV-009` §4** | Evidence classes `E1`…`E8`; rules `GA-01`…`GA-12` | **Inherited unchanged and applied at release level**, exactly as `GV-009`'s own traceability table anticipates | None. This is the interface `GV-009` declared |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `GV-009` §3.3 | Six readiness dimensions with assessors — the base this document extends |
| `GV-009` §4.1, §4.2, §4.3 | Eight evidence classes; class-by-criterion-type; `GA-01`…`GA-08` |
| `GV-009` §5.3 | Four assessor roles that do not exist — Security Lead, Service Manager, accessibility reviewer, Data Protection Forum |
| `GV-009` §9.1 | Eleven standing criteria `SG-1`…`SG-11` |
| `GV-009` §9.2 | Seven entry criteria `EN-01`…`EN-07`, checked at T−6 weeks |
| `_CATEGORY_OVERVIEW` | The seven-dimension table and the claim that *"none of those seven assessors is currently named anywhere"* |
| `CM-012` §4.1, §4.2, §4.5, §4.7 | Eight branch readiness domains; who confirms what; the not-ready route; `RB-11` re-confirmation tiers |
| `DM-014` §4.6 | `C1`…`C9`; `CV-14`'s non-delegable `C7` |
| `QA-009`, `QA-011`, `QA-006`, `QA-007`, `QA-008`, `QA-010` | Each names `RL-003` as the consumer of its evidence |
| `MG-004` | Reconciliation governance: Preparer / Reviewer / Approver, attribute sampling, the evidence pack |
| `RL-002` §8 | The 58-item go-live checklist, five items of which cannot be evidenced today |
| `06-02` §4 | The 70 gate criteria, counted 12+10+9+10+7+6+6+5+5 |

### 2.3 Register gaps and audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `RL-003` ⛔ | `PGD-000` | The residual gap after `GV-009` is defined in §2.4 and filled by §3–§11 |
| *"None of those seven assessors is currently named anywhere"* | `_CATEGORY_OVERVIEW` | §4.2 names all seven and states the veto each holds. §11 records that four of the seven roles are unfilled |
| The register row for `RL-003` is stale | This document, §2.4 | The row's justification was written before `GV-009` issued and is now partly discharged. Recorded as `RLA-02` |
| `GV-009` has six dimensions; the category overview has seven | This document, §3.2 | Reconciled: the seventh is **Commercial**, and §3.3 states why `GV-009` could not have had it |
| `QA-008` accessibility cannot be gated | `GV-009` §5.3 | §11.2 states the position rather than assigning a veto to a vacant role |

### 2.4 What `GV-009` left, stated precisely

This is the most important table in the document, because everything after it is scoped by it.

| Question | Answered by `GV-009`? | Residual gap this document fills |
|---|:--:|---|
| What evidence class does a criterion need? | **Yes** — §4.2 | None. Inherited |
| Who assesses each dimension at a **wave gate**? | **Yes** — §5.1 | None at gate level |
| What happens when a gate fails? | **Yes** — §6.3 | None |
| What are the standing criteria? | **Yes** — §9.1 | None |
| **How many dimensions are there?** | Six | **Seven.** Commercial readiness is absent (§3) |
| **Who assesses readiness at a *go-live*, which is not a gate?** | No | §4 — a go-live is a different event from a gate, and happens more often |
| **What does an assessor's negative opinion actually stop?** | No — §5.1 gives opinions, not vetoes | §4.3 — the veto model, and what each veto stops |
| **How is a readiness position expressed?** | No | §6 — RAG per dimension, never averaged, never scored out of ten |
| **What happens when the go-live date slips?** | No | §9 — three re-assessment tiers, adopted from `CM-012` `RB-11` |
| **What may carry an open item and what may not?** | Partly — §6.3's conditional pass is gate-level | §10 — four dimensions that cannot carry one at a go-live |
| **What is the instrument?** | No | §8 — the form |

> **`GLR-02`. Where this document and `GV-009` appear to disagree, `GV-009` governs the wave gate
> and this document governs the go-live.** They are different events. `GV-009` is not amended by
> anything here.

### 2.5 The rule space

Rules carry the prefix **`GLR`**, verified at **zero** occurrences across all 754 markdown files of
the workspace before allocation. `GV-009` §9.1 already records why this matters: its own first draft
used `SC-G*`, collided with the Security category code, and was corrected before issue.

---

## 3. Seven Dimensions

### 3.1 The six inherited

Adopted from `GV-009` §3.3 unchanged in meaning, renumbered `RD-n` (Readiness Dimension) so that a
reader can never confuse a go-live dimension with a gate dimension in a conversation where both are
on the table.

| # | Dimension | The question | `GV-009` equivalent |
|:--:|---|---|:--:|
| **`RD-1`** | **Functional** | Does it do what the requirements said, for the scope going live? | D1 |
| **`RD-2`** | **Technical** | Is it deployed, performing, and recoverable? | D2 |
| **`RD-3`** | **Data** | Is the data migrated, reconciled and signed for? | D3 |
| **`RD-4`** | **Security & privacy** | Is it safe, and is it lawful? | D4 |
| **`RD-5`** | **Operational** | Can it be run, supported and recovered from tomorrow morning? | D5 |
| **`RD-6`** | **People** | Are the users trained, accessed and supported? | D6 |

### 3.2 The seventh

| # | Dimension | The question |
|:--:|---|---|
| **`RD-7`** | **Commercial** | Has the delivered scope been formally accepted, and is the programme contractually entitled to operate it? |

### 3.3 Why `GV-009` could not have had it, and why this document must

`GV-009` §3.3 adds four dimensions to `06-02`'s functional-and-technical criteria and stops at six.
It is not an omission on `GV-009`'s part: its authority is the Steering Committee's Go/No-Go on
**scope and funding**, and commercial acceptance is an input to that decision rather than a
dimension of it.

At a **go-live**, commercial readiness is different and it is operational:

| Commercial question | Consequence if unanswered at go-live |
|---|---|
| Has the vendor's delivered scope been accepted against a schedule? | The programme operates a system it has not accepted, and the acceptance milestone quietly passes by use |
| Are the licences for the live user population in place? | A licence shortfall discovered in production is a compliance event, not a procurement task (`CO-004` ◐) |
| Are third-party service contracts live for the go-live date — gateways, telematics, SMS, hosting? | A live payment gateway with an unsigned contract is an operating risk with no counterparty obligation |
| Is support commercially in force from the go-live instant, not from the contract's convenience? | `SV-005` hypercare exit hands to a support model that must already be contracted |
| Do the SLAs the business is about to promise customers match those the vendor has promised the business? | The company assumes a liability gap it has never measured |

> **`GLR-03`. `RD-7` exists because a go-live creates contractual exposure on the day it happens,
> and no other dimension owns that.** `CO-003` (Statement of Work & Deliverable Acceptance Schedule)
> is ⛔; §11.1 records what that means for `RD-7`'s assessability at W1.

### 3.4 Dimension scope: what each covers at a go-live but not at a gate

| Dimension | Gate-level (`GV-009`) | **Go-live-level (this document)** |
|---|---|---|
| `RD-1` Functional | The wave's requirements demonstrated | **These sites' transactions demonstrated in `prod`**, with this site's data |
| `RD-2` Technical | Architecture, performance, upgradability | **This deployment** verified; rollback rehearsed and in-window |
| `RD-3` Data | Migration reconciled, quality stated | **This site's** reconciliation signed by its own domain owner |
| `RD-4` Security | Findings closed, DPIA current | Access provisioned to the **right roles at these sites**, and no more |
| `RD-5` Operational | Runbooks exist and are rehearsed | **On-call is staffed for tonight**, floor-walkers are rostered, fallback is on site |
| `RD-6` People | Training ≥ 95%, adoption absorbed | **These named people** have completed, passed, and logged in once |
| `RD-7` Commercial | *(not assessed)* | Acceptance, licences, third-party contracts, support in force |

---

## 4. Assessors and Vetoes

### 4.1 What a veto is

> **`GLR-04`. A veto is a named person's recorded statement that their dimension is not ready, and
> its effect is that `C7` may not be taken as a go.** It is not advice, it is not a risk, and it is
> not overridden by seniority. It is discharged only by the evidence its holder named, or by the
> Steering Committee accepting the exposure in a minuted decision recorded in `GV-003` as a `D-nnn`.

### 4.2 The seven assessors

| Dim | Assessor | Deputy | Independence requirement | Veto stops |
|:--:|---|---|---|---|
| `RD-1` | **Named business owner** for the wave's primary module | The module's lead super-user | Must not report to the Programme Director (`GV-009` §5.1) | `C7`, and the affected sites |
| `RD-2` | **Platform Lead** | Solution Architect | **Must not have built the component being assessed** | `C7` |
| `RD-3` | **Financial Controller** (financial data) **with the Data Migration Lead** (all other data) | None for financial data — `CFO sign-off is non-delegable` | The Data Migration Lead may not sign for data they loaded (`MG-004` Preparer/Reviewer/Approver separation) | `C7`; financial data alone stops it |
| `RD-4` | **Security Lead**, with the **DPO** for privacy | CTO for security only, never for privacy | Penetration and vulnerability findings require `E6` — a reviewer independent of the builder | `C7` |
| `RD-5` | **Service Manager** | Support Lead | **Must be the person who will run it**, not the person who built it | `C7` |
| `RD-6` | **Change Lead**, with the **HR Director** for statutory training | Branch Operations Lead | — | The affected sites, not necessarily `C7` (§4.6) |
| `RD-7` | **PMO**, with **Legal Counsel** for contractual questions | Programme Director | Must not be the person negotiating the acceptance | `C7` |

### 4.3 What each veto actually stops

> **`GLR-05`. Not every veto stops everything.** A dimension that fails at one site and passes at
> forty stops that site; a dimension that fails at the platform level stops the go-live.

| Veto scope | Dimensions | Rule |
|---|---|---|
| **Programme-wide** — stops `C7` outright | `RD-2`, `RD-4`, `RD-7` | These are properties of the platform, the law and the contract. They do not vary by site |
| **Site-scoped** — stops the named sites; the rest may proceed as a **partial go** (`CM-006` `GO-13`) | `RD-5`, `RD-6` | Staffing, training and support are site properties. `CM-012` `RB-08` already provides the route |
| **Scope-scoped** — stops the affected functional scope; other scope may proceed behind toggles (`RMP-02`) | `RD-1` | A single module unready does not stop a wave that delivers eleven |
| **Mixed** | `RD-3` | **Financial data is programme-wide** (`T2`, `T6` are absolute). Non-financial data is site-scoped |

### 4.4 The rule that makes a veto real

| # | Rule |
|---|---|
| **`GLR-06`** | An assessor **may not be asked to reconsider** by anyone in their reporting line. A veto is discharged by evidence or by a Steering Committee acceptance, and by nothing in between |
| **`GLR-07`** | An assessor who has not been given the evidence their dimension requires **records `RED` by default**, not `AMBER`. Absence of evidence is not partial evidence — `GA-06`: *"zero findings from a test that did not run is not zero findings"* |
| **`GLR-08`** | An assessor's opinion is recorded **before** the `C7` bridge convenes, not during it. `MG-006` §10.1 establishes how a checkpoint is taken; a readiness opinion formed in the room, at 04:00, under the eyes of the people whose work it judges, is not an assessment |
| **`GLR-09`** | **A veto exercised is a normal outcome and is never treated as a failure of the person exercising it.** `CM-012` `RB-10` states the same rule for branch managers and states the reason: *"the moment the first branch to say so is treated as a problem, every subsequent branch says it is ready"* |

### 4.5 Cross-assessment before Gate 4

`GV-009` `GA-09` provides independence from **Gate 4** onward, and the **cross-assessment rule**
before it: *no person assesses a criterion for a component they built or managed.*

> **`GLR-10`.** The same rule binds every readiness assessment, at every go-live, from W1. It is the
> only independence control available before Gate 4 and it is therefore not waivable at a go-live
> under time pressure.

### 4.6 Why `RD-6` does not usually stop `C7`

`RD-6` failing means people at some sites are not trained, not accessed, or not supported. `CM-012`
`RB-08` already routes that: the site does not cut over and joins the next window. Stopping a
programme-wide `C7` because eleven of fifty sites are not trained would delay the forty who are.

> **`GLR-11`.** `RD-6` escalates to a programme-wide veto in exactly one case: **when the untrained
> population includes a role whose absence makes the system unoperable anywhere** — a statutory
> approver, the only trained payroll operator, the sole certified technician for a brand's warranty
> work. `RL-004` §8 identifies those roles per wave; the escalation is not a judgement made on the
> night.

### 4.7 The relationship with `CM-012`'s eight branch domains

`CM-012` §4.1 defines eight site readiness domains `D1`…`D8` with their own confirmers and the `C2`
checkpoint. **They are adopted whole and are not restated.** The mapping into this document's
dimensions:

| `CM-012` domain | Rolls into | Note |
|---|:--:|---|
| `D1` Connectivity | `RD-5` | Non-negotiable at `CM-012` `RB-09`; carries through |
| `D2` Hardware | `RD-5` | May carry a dated open item |
| `D3` Access | `RD-4` **and** `RD-6` | Access *provisioning* is security; access *held by the right trained person* is people |
| `D4` Training | `RD-6` | Completion and assessment, never attendance (`RB-03`) |
| `D5` Champion | `RD-6` | Champion **and deputy** |
| `D6` Data | `RD-3` | Non-negotiable at `RB-09` |
| `D7` Physical count readiness | `RD-3` | W2 and W5 principally |
| `D8` Cash and finance | `RD-3` | Non-negotiable at `RB-09` |

| # | Rule |
|---|---|
| **`GLR-12`** | **`C2` is an input to this assessment, not a duplicate of it.** A site that failed `C2` is excluded from the go-live scope before the assessment runs; the assessment then reports on the sites that remain |
| **`GLR-13`** | The count of sites in scope is **counted, never estimated** (`CM-012` `CP-11`), and it is stated on the form. A readiness assessment that cannot say how many sites it covers is not an assessment |

---

## 5. Evidence per Dimension

Evidence classes are `GV-009` §4.1's `E1`…`E8`, used unchanged. `GA-02` (right environment), `GA-03`
(dated in window), `GA-04` (a percentage carries its denominator), `GA-05` (a sample carries its
size and method), `GA-06` (negative evidence is evidence) and `GA-07` (progressive assembly) all
apply without modification.

### 5.1 `RD-1` Functional

| # | Evidence required | Class | Source | Owner |
|---|---|:--:|---|---|
| `F-1` | UAT executed and signed by named business super-users for the scope going live | **`E4`** | `QA-009` wave acceptance record | QA Lead |
| `F-2` | Requirements-to-test coverage report for the wave's scope, **with its denominator stated** | **`E2`** | `QA-011` | Head of Quality Engineering |
| `F-3` | Defect position against every `QA-010` threshold `DMG-T1`…`DMG-T9` | **`E2`** | Defect register | Head of Quality Engineering |
| `F-4` | The wave's `06-02` criteria demonstrated end to end in `prod` at a pilot site | **`E1`** | Witnessed demonstration | Business owner |
| `F-5` | Where a criterion is a human-performance target, a timed observation with **sample size, method and distribution** | **`E3`** | `06-02` `G1-03` pattern | Business owner |

> **`GLR-14`** — `F-2` may not be quoted without its denominator. `AUDIT-014` `TS-01` recorded that
> coverage in this estate has had **five superseded denominators**; `QA-011` fixed one — **3,389** —
> with provenance and a reproduction command. The number on this form is that one or it is not
> accepted.

### 5.2 `RD-2` Technical

| # | Evidence required | Class | Source | Owner |
|---|---|:--:|---|---|
| `T-1` | `RL-002` §8 go-live checklist complete and signed, all applicable scopes | **`E4`** | Deployment record | Platform Lead |
| `T-2` | Wave release deployed to `prod` at or before `RMP-25`'s T−15 working days, and verified at +48 h | **`E2`** | Deployment record + verification report | Platform Lead |
| `T-3` | Performance results within `NFR` thresholds for the delivered scope | **`E5`** | `QA-006` report | Platform Engineering |
| `T-4` | Rollback **rehearsed**, with a measured duration that fits the remaining window | **`E1`** | `DoD-16` rehearsal record | Platform Lead |
| `T-5` | Environments exist **and are provisioned** at the class the criteria require | **`E2`** | `PE-002` §4.2 — twelve specified, **none provisioned**; see §11.4 | Platform Lead |
| `T-6` | Backup taken and **restore tested** in the wave's scope | **`E5`** | `SG-6`; `PE-007` (issued 2026-08-19; **restore not yet tested**) | Platform Lead |

### 5.3 `RD-3` Data

| # | Evidence required | Class | Source | Owner |
|---|---|:--:|---|---|
| `D-1` | Every applicable `DM-013` reconciliation signed by its **domain owner**, per `MG-004`'s Preparer/Reviewer/Approver separation | **`E7`** + **`E4`** | `MG-004` evidence pack | Financial Controller / Data Migration Lead |
| `D-2` | Control totals derived from the source **by a different code path** and frozen | **`E7`** | `MG-004` | Data Migration Lead |
| `D-3` | Attribute-sampling result with sample size and confidence stated; **payroll YTD at 100%** | **`E2`** | `MG-004` | Financial Controller |
| `D-4` | Mushak 6.3 sequence position assertable | **`E4`** | `FO-12`; `DM-014` `T6` | Financial Controller |
| `D-5` | Physical count complete at every site in scope, or the declared number of exceptions is within tolerance | **`E7`** | `DM-014` `T7` | Warehouse Manager |
| `D-6` | Lawful basis recorded for every personal-data set loaded | **`E4`** | `MG-001` `MST-21`; `SC-003` | DPO |

### 5.4 `RD-4` Security & privacy

| # | Evidence required | Class | Source | Owner |
|---|---|:--:|---|---|
| `S-1` | Zero **open** critical or high security findings in the wave's scope | **`E5`** + **`E6`** | `SG-1`; `QA-007`; `SC-009` remediation | Security Lead |
| `S-2` | DPIA updated; lawful basis recorded for every new processing purpose | **`E4`** | `SG-2`; `SC-003` | DPO |
| `S-3` | No unmasked production personal data in any non-production environment | **`E2`** | `SG-3`; `CON-14`; `QA-004` | Security Lead |
| `S-4` | Access provisioned to the right roles at the sites in scope, and to no others | **`E2`** | `SC-004`; `CM-012` `D3` | Security Lead |
| `S-5` | Residency-classified fields written only to their permitted store | **`E2`** | `SC-007`; `MTS-E2` | Security Lead |
| `S-6` | Regulatory citations re-verified; `RR-005` currency register updated | **`E4`** | `SG-10`; `PG-M4` | Legal Counsel |

### 5.5 `RD-5` Operational

| # | Evidence required | Class | Source | Owner |
|---|---|:--:|---|---|
| `O-1` | Runbooks exist, are current, and have been **rehearsed** — not merely written | **`E1`** + **`E4`** | `SG-4`; `SV-003` (issued 2026-08-19); `OP-007`…`OP-011` | Service Manager |
| `O-2` | On-call rota staffed and **paging tested end to end** | **`E1`** | `SG-5`; `SV-004` (issued 2026-08-19; **no rota, no paging platform, no test**) | Service Manager |
| `O-3` | Hypercare staffing confirmed: floor-walkers rostered at the `OP-002` §4.4 ratios | **`E4`** | `OP-002`; `SV-005` (issued 2026-08-19) | Support Lead |
| `O-4` | Manual fallback procedures current and physically present at each site | **`E1`** | `OP-014`; `MG-007` §8 | Operations Director |
| `O-5` | Connectivity tested at the busiest hour at every site in scope | **`E3`** | `CM-012` `RB-02` | IT Administrator |
| `O-6` | Support macros, canned responses and known-issue log current | **`E2`** | `OP-003`; `OP-002` §4.6 | Support Lead |

### 5.6 `RD-6` People

| # | Evidence required | Class | Source | Owner |
|---|---|:--:|---|---|
| `P-1` | Training **completed and passed** per named person for every role in scope — never attendance | **`E2`** | `SG-7`; `CM-012` `RB-03`; `M22` records | HR Director / L&D |
| `P-2` | Access granted only after training (`TR-002`), evidenced per person | **`E2`** | `CM-012` `D3` | IT Administrator |
| `P-3` | Champion **and deputy** confirmed, trained and published at every site in scope | **`E4`** | `CM-012` `D5`; `NW-16` | Change Lead |
| `P-4` | Every role identified in `RL-004` §8 as go-live-critical is covered by at least two trained people | **`E2`** | `GLR-11` | Change Lead |
| `P-5` | Bengali-language materials issued for every affected role | **`E4`** | `TR-002`; `CM-R6` | L&D |

### 5.7 `RD-7` Commercial

| # | Evidence required | Class | Source | Owner |
|---|---|:--:|---|---|
| `C-1` | Delivered scope formally accepted against a deliverable acceptance schedule | **`E4`** | `CO-003` — **⛔** | PMO |
| `C-2` | Licences in place for the live user population at go-live volumes | **`E2`** | `CO-004` ◐; `BE-007` SBOM | PMO |
| `C-3` | Third-party service contracts in force for the go-live date — gateways, SMS, telematics, hosting | **`E8`** | Contract register | Legal Counsel |
| `C-4` | Support arrangements contractually in force from the go-live instant | **`E4`** | `CO-003` ⛔; `SV-002` ⬜ | PMO |
| `C-5` | Customer-facing SLA commitments reconciled against supplier-side commitments | **`E4`** | `LG-015`; `SV-002` ⬜ | Legal Counsel |

**Thirty-nine evidence items across seven dimensions.** Counted at 2026-08-18 23:27 (+06):
`RD-1` 5 · `RD-2` 6 · `RD-3` 6 · `RD-4` 6 · `RD-5` 6 · `RD-6` 5 · `RD-7` 5.

---

## 6. Scoring

### 6.1 RAG per dimension

| Status | Definition |
|---|---|
| **GREEN** | Every evidence item for the dimension exists, is dated in window, is attributable and is reproducible (`GA-01`) |
| **AMBER** | Every item exists **except** one or more with a **dated remediation plan and a named owner**, none of which is on §10's non-negotiable list |
| **RED** | Any evidence item is absent, or is present and fails, or falls on §10's non-negotiable list |

### 6.2 Readiness is never averaged

> **`GLR-15`. There is no overall readiness score, no percentage and no traffic light for the
> assessment as a whole.** The output is **seven statuses**, reported as seven.

The reason is arithmetic and it is the estate's own recurring defect. `PGD-A2-24` and `QAA-12`
record the same failure twice: *a correct total concealing a wrong component*. Six GREENs and one
RED average to something reassuring; what it conceals is that the system is unlawful, or has no
on-call, or has not been paid for.

> **`GLR-16`** — a report that presents readiness as a single figure is rejected by the PMO and
> returned. `CM-012` `EP-06` sets the same rule for the branch dashboard: report **the worst site,
> not the average**.

### 6.3 What each combination means at `C7`

| Position | Meaning | `C7` |
|---|---|---|
| Seven GREEN | Ready | **May be taken as a go** |
| Any AMBER, no RED | Ready with dated remediation | **May be taken as a go**, and every AMBER item is carried into hypercare with an owner and a date |
| **Any RED on `RD-2`, `RD-4` or `RD-7`** | Programme-wide veto | **`C7` may not be a go** |
| **RED on `RD-3` financial data** | Programme-wide veto | **`C7` may not be a go** (`DM-014` `T2`, `T6`) |
| RED on `RD-1`, or `RD-3` non-financial, or `RD-5`, or `RD-6` | Scope- or site-scoped veto | **Partial go** (`CM-006` `GO-13`), with the vetoed scope or sites excluded and named |

### 6.4 Reporting into the wave gate

> **`GLR-17`.** The readiness position is reported into the `GV-009` gate report as an **input to
> dimension opinions**, in §6.2 section 2, and never as a substitute for them. A gate assessor forms
> their own opinion; this document tells them what the go-live evidence showed. The two are
> different judgements about different questions and are recorded separately.

---

## 7. The Assessment Timeline

### 7.1 Three timelines already exist and they are not aligned

| Source | Anchor | Points |
|---|---|---|
| `GV-009` §6.1 | The **gate** | T−6 wk entry criteria · T−4 UAT opens · T−3 security · T−2 pack review · T−1 dry run · T−3 d report · T−0 gate |
| `CM-012` §4.3 | The **site cutover** | T−6 wk champion · T−4 readiness notice · T−3 data review · T−2 count rehearsal · T−1 confirmation · T−3 d `C2` result |
| `DM-014` §4.1 | The **freeze instant** | `P0` T−21 d · `P1` T−3 d · `P2` freeze · `P3` parallel · `P4` withdrawal |

They use the same notation against three different zero points. A person reading "T−3" cannot tell
which.

### 7.2 The reconciliation

> **`GLR-18`. In this category, unqualified `T` means the *freeze instant* defined by `DM-014`
> `CV-06`.** Gate-relative times are written `G−n`; site-relative times are written `S−n`. This is
> stated once and applied everywhere in Category 12.

| When | Activity | Owner | Feeds |
|---|---|---|---|
| **`G−6 wk`** | `GV-009` `EN-01`…`EN-07` entry criteria checked; **evidence pack opened** | PMO | All dimensions |
| **`T−25 wd`** | Wave code freeze (`RMP-26`) | Release Manager | `RD-2` |
| **`T−15 wd`** | Wave release deployed to `prod` (`RMP-25`) | Platform Lead | `RD-2` `T-2` |
| **`T−13 wd`** | Deployment verification closes at +48 h | Support Lead | `RD-2` `T-2` |
| **`S−4 wk`** | Site readiness notice; connectivity tested at the busiest hour | IT Administrator | `RD-5` `O-5` |
| **`T−21 d`** | `P0` rehearsal begins | Data Migration Lead | `RD-2` `T-4`, `RD-3` |
| **`S−3 wk`** | Site data review request issued | Data Migration | `RD-3` `D-1` |
| **`G−2 wk`** | Evidence pack reviewed by the PMO; gaps become remediation items | PMO | All |
| **`T−10 wd`** | **First readiness assessment.** All seven assessors record a provisional status | PMO | The form |
| **`S−1 wk`** | Site readiness confirmation returned; `C2` form submitted | Branch managers | `RD-3`, `RD-5`, `RD-6` |
| **`T−3 d`** | **`C2` decided.** Sites excluded from scope are named | Change Lead + Branch Ops Lead | `GLR-12` |
| **`T−2 d`** | **Final readiness assessment.** Seven statuses recorded and signed | PMO | `C7` |
| **`T−2 d`** | `CM-006` `G4` contact-centre brief released, carrying **both** branches (`GO-02`) | Contact Centre Manager | — |
| **`T−0`** | Freeze instant; `P2` begins | Data Migration Lead | — |
| **End `P2`** | **`C7`** taken by the CTO with the Programme Director, holding the readiness form | CTO + PD | The go decision |
| **`G−3 d`** | Gate report circulated, carrying the readiness position (`GLR-17`) | PMO | `GV-009` |

| # | Rule |
|---|---|
| **`GLR-19`** | The assessment is run **twice**: provisionally at `T−10 wd` and finally at `T−2 d`. One assessment is a snapshot; two make the trend visible, and a dimension that moved from GREEN to AMBER in eight working days is more informative than either reading alone |
| **`GLR-20`** | The final assessment is at **`T−2 d`, before `P1`'s freeze approach**, not during `P2`. `GA-11`'s principle applies: *"a gate that discovers at T−0 that its evidence cannot be produced has already failed"* |

---

## 8. The Readiness Assessment Form

```
GO-LIVE READINESS ASSESSMENT                                    Wave: ____
Freeze instant (Asia/Dhaka, CV-06): ____-__-__ __:__            Assessment: ☐ provisional (T−10 wd)  ☐ final (T−2 d)
Sites in scope: ____  (counted, not estimated — GLR-13)         Sites excluded at C2: ____
Scope going live: ______________________________________        Wave release tag: v_._._-w_

DIMENSION STATUS — recorded independently, never averaged (GLR-15)

  RD-1 Functional        ☐ GREEN ☐ AMBER ☐ RED    Assessor: ______________ Date: ______
       F-1 UAT signed ☐   F-2 coverage + denominator ☐   F-3 DMG-T1…T9 ☐   F-4 prod demo ☐   F-5 timed obs ☐
  RD-2 Technical         ☐ GREEN ☐ AMBER ☐ RED    Assessor: ______________ Date: ______
       T-1 checklist ☐   T-2 deployed T−15 wd + verified ☐   T-3 perf ☐   T-4 rollback rehearsed ☐
       T-5 environments ☐   T-6 restore tested ☐
  RD-3 Data              ☐ GREEN ☐ AMBER ☐ RED    Assessor: ______________ Date: ______
       D-1 reconciliations signed ☐   D-2 control totals ☐   D-3 sampling ☐   D-4 Mushak sequence ☐
       D-5 counts ☐   D-6 lawful basis ☐          Financial data specifically: ☐ GREEN ☐ AMBER ☐ RED
  RD-4 Security/privacy  ☐ GREEN ☐ AMBER ☐ RED    Assessor: ______________ Date: ______
       S-1 zero crit/high ☐  S-2 DPIA ☐  S-3 no prod PII off-prod ☐  S-4 access ☐  S-5 residency ☐  S-6 citations ☐
  RD-5 Operational       ☐ GREEN ☐ AMBER ☐ RED    Assessor: ______________ Date: ______
       O-1 runbooks rehearsed ☐  O-2 paging tested ☐  O-3 floor-walkers ☐  O-4 fallback on site ☐
       O-5 connectivity ☐  O-6 macros + known issues ☐
  RD-6 People            ☐ GREEN ☐ AMBER ☐ RED    Assessor: ______________ Date: ______
       P-1 trained + passed ☐  P-2 access after training ☐  P-3 champion + deputy ☐
       P-4 critical roles ×2 ☐  P-5 Bengali materials ☐
  RD-7 Commercial        ☐ GREEN ☐ AMBER ☐ RED    Assessor: ______________ Date: ______
       C-1 acceptance ☐  C-2 licences ☐  C-3 third-party contracts ☐  C-4 support in force ☐  C-5 SLA reconciled ☐

VETOES EXERCISED
  Dimension: ____  Scope: ☐ programme-wide  ☐ sites: __________  ☐ functional scope: __________
  Held by: ______________  Discharged by (evidence, or GV-003 D-nnn): ______________________

AMBER ITEMS CARRIED (each requires a dated plan and a named owner — GLR-21)
  Item ____  Owner ______________  Date ______      Item ____  Owner ______________  Date ______

UNEVIDENCEABLE ITEMS (dependency is ABSENT — recorded, not ticked; GA-06)
  ______________________________________________________________________

SIGNATURES — seven assessors sign their own dimension only
  RD-1 ____________  RD-2 ____________  RD-3 ____________  RD-4 ____________
  RD-5 ____________  RD-6 ____________  RD-7 ____________
  PMO — completeness of the pack, not the opinions .......... ______________  Date ______

HANDED TO C7:  ☐ Yes, at ____:____   Received by CTO ______________ / Programme Director ______________
```

> **`GLR-21`** — every AMBER carries a dated plan and a named owner on the form itself. An AMBER
> with neither is a RED that has been written down optimistically.

> **`GLR-22`** — the PMO signs for the **completeness of the pack**, never for the opinions in it.
> This mirrors `GV-009` §6.4, where the Programme Director signs for evidence completeness and the
> CEO signs the decision.

---

## 9. Re-assessment When the Date Slips

Adopting `CM-012` `RB-11`'s tiers, because the underlying fact is the same: *readiness expires*.

| Slip | Re-assessment required |
|---|---|
| **≤ 5 working days** | `RD-4` `S-4` (access) re-checked. All other statuses stand |
| **6–20 working days** | **`RD-2`, `RD-3`, `RD-5` and `RD-6` fully re-assessed.** `RD-1`, `RD-4` and `RD-7` stand unless their evidence has aged past `GA-03`'s window |
| **> 20 working days** | **Full re-assessment, all seven dimensions.** Staff have changed, stock has moved, training has decayed, and evidence has aged out of the gate window |
| **Any slip** | Every site in scope is told the new date **and** the re-confirmation requirement in the same message (`CM-012` `RB-11`) |

| # | Rule |
|---|---|
| **`GLR-23`** | A GREEN older than `GA-03`'s six-week evidence window is **not a GREEN**. It is an unassessed dimension, and `GLR-07` makes an unassessed dimension RED |
| **`GLR-24`** | A slip **never** reduces the assessment. The temptation on a re-planned go-live is to carry the previous form forward with a new date on it; `GLR-23` is the control against exactly that |

---

## 10. Conditional Readiness

`GV-009` §6.3 provides a **conditional pass** at gate level. At go-live level the equivalent is
AMBER, and four dimensions' items cannot take it.

### 10.1 What may never be AMBER

| # | Item | Dimension | Why |
|:--:|---|:--:|---|
| 1 | Open `S1` defect, or any open defect on an `RC-A` population | `RD-1` | `QA-010` `DMG-T1`/`DMG-T2` — not acceptable by **any** body |
| 2 | Rollback not rehearsed, or its measured duration exceeds the remaining window | `RD-2` | `DM-014` `T4`; continuing means continuing with no way back |
| 3 | A financial reconciliation unsigned by its domain owner | `RD-3` | `DM-014` `T5`; the accountable person does not accept the data |
| 4 | Mushak 6.3 sequence position unassertable | `RD-3` | `DM-014` `T6`; uncorrectable statutory exposure |
| 5 | Open critical or high security finding in scope | `RD-4` | `SG-1`; P0 at every gate |
| 6 | Personal data loaded with no recorded lawful basis | `RD-4` | `MG-001` `MST-21`; PDPA 2026 enforcement lands **inside Wave 4** |
| 7 | Production personal data unmasked in a non-production environment | `RD-4` | `SG-3`; `CON-14` |
| 8 | No on-call cover for the go-live night and the following 48 hours | `RD-5` | An incident with nobody to page is an outage of unbounded length |
| 9 | Manual fallback procedures absent from a site in scope | `RD-5` | `P2` has no system of record (`CV-02`); paper is the only path |
| 10 | Connectivity unconfirmed at a site in scope | `RD-5` | `CM-012` `RB-09`; a site with no connectivity cannot transact |

> **`GLR-25`. Ten items. Any one of them is RED, and RED on `RD-2`, `RD-4` or financial `RD-3` stops
> `C7`.** They are not "high-priority AMBERs" and there is no route by which they become AMBER
> through negotiation.

### 10.2 What AMBER is legitimately for

| Example | Dimension | Why AMBER is right |
|---|:--:|---|
| Two of forty sites lack a second label printer | `RD-5` | `CM-012` `D2` may carry a dated open item |
| A `S3` defect with a documented workaround | `RD-1` | `DMG-T6` sets no cap on `S3` |
| A runbook updated but not yet rehearsed for a low-frequency procedure | `RD-5` | `SG-4` requires rehearsal; a dated plan is a legitimate remediation |
| Refresher training outstanding for a role not transacting in week 1 | `RD-6` | Sequenced, not absent |
| A third-party contract signed but the countersignature outstanding | `RD-7` | `E8` obtainable within days |

---

## 11. The Roles That Do Not Exist

`GV-009` §5.3 records four assessor roles as unfilled. This document adds three more requirements
and must state the same thing about them.

### 11.1 Position by dimension

| Dim | Assessor required | Exists in `06-01` §4 team model? | Consequence |
|:--:|---|:--:|---|
| `RD-1` | Named business owner | **Yes** — module business owners at 20% | Assessable |
| `RD-2` | Platform Lead | **Yes** — DevOps/Platform Engineer from W1 | Assessable, but `T-5` and `T-6` remain unevidenceable — **not for want of a document** (`PE-002` and `PE-007` issued 2026-08-19) but for want of a provisioned environment and a tested restore. §11.4 |
| `RD-3` | Financial Controller + Data Migration Lead | Financial Controller **not named**; Data Migration Lead implied by the migration workstream | Partly assessable |
| `RD-4` | **Security Lead** + DPO | **No.** `GV-009` §5.3: not in `06-01` §4 at any wave; 12–20 week hire lead. Data Protection Forum constituted by `GV-002` §4.8, **not yet convened** | **`RD-4` has no assessor.** `S-1` and `S-2` cannot be signed |
| `RD-5` | **Service Manager** | **No.** `GV-009` §5.3; `AUDIT-017`: *"operational content and no operational capability"* | **`RD-5` has no assessor.** `SV-001`…`SV-005` were all issued 2026-08-19 and **none of it is running** — `O-2` remains unevidenceable, now for want of a paging platform rather than a paging design |
| `RD-6` | Change Lead + HR Director | **Yes** — Change & Training Lead from W1 at 0.5 FTE | Assessable |
| `RD-7` | **PMO + Legal Counsel** | PMO implied; **Legal Counsel not in the team model** | Partly assessable; `C-1` unevidenceable (`CO-003` ⛔) |

> **`GLR-26`. Three of seven dimensions have no appointed assessor at the time of issue, and a
> fourth has no legal counsel.** Under `GLR-07` an unassessed dimension is RED, and under §6.3 a RED
> on `RD-4` stops `C7`. **Read literally, this document makes Wave 1 unable to go live.**
>
> That reading is correct and is not softened. The three appointments — Security Lead, Service
> Manager, Financial Controller — plus Legal Counsel access are **the cheapest items on the Wave 1
> critical path**, and the alternative to naming the consequence is a Wave 1 go-live where nobody
> was accountable for security, operations or acceptance. Raised as `Q-01` and escalated to
> `GV-005` as a **Critical** dependency.

### 11.2 Accessibility has no assessor and no dimension

`GV-009` §5.3 records the accessibility reviewer as *"explicitly absent — `TS-016` cannot be
executed"*, and concludes that `QA-008` accessibility conformance cannot be gated.

> **`GLR-27`.** Accessibility is **not** given its own readiness dimension here, and this is
> deliberate. Creating an eighth dimension with no assessor would produce a permanent RED that would
> be routinely waived, and a routinely waived veto teaches every other assessor that vetoes are
> negotiable. Instead, `UX-005` conformance and `QA-008`'s Accessibility Conformance Report sit
> inside `RD-1` `F-2`'s coverage evidence, where their absence is visible as a coverage gap with a
> stated denominator. When an accessibility reviewer is appointed, `RD-1` gains an evidence item
> `F-6`; it does not gain a dimension. Recorded so the omission is a decision, not a gap.

### 11.4 A document is not a capability

> **⚠ Added at audit, 2026-08-19 02:10 (+06) — finding `RLA-17`.** Between this document's drafting
> and its issue, **Category 10 (`PE-001`…`PE-009`), three of Category 11 (`SV-001`…`SV-003`) and all
> five of Category 13 (`CH-001`…`CH-005`) were authored** by concurrent sessions. Several evidence
> items in §5 were written against those documents' absence and had to be corrected.
>
> **The corrections did not change a single status**, and that is the point worth recording.

| Evidence item | v1.0 said | Now | Assessable? |
|---|---|---|:--:|
| `T-5` environments | `PE-002` ⛔ | `PE-002` issued; **0 of 12 provisioned** | **No** |
| `T-6` restore tested | `PE-007` ⛔ | `PE-007` issued; **no restore performed** | **No** |
| `O-1` runbooks rehearsed | `SV-003` ◐ | `SV-003` issued; **no rehearsal performed** | **No** |
| `O-2` paging tested | `SV-004` ⛔ | `SV-004` **issued**; no paging platform, no test | **No** |
| `P-1` training completed | `CH-002` ◐ | `CH-002` issued; **no cohort trained** | **No** |
| `C-1` acceptance | `CO-003` ⛔ | `CO-003` still ⛔ | **No** |

> **`GLR-31`. An evidence item is discharged by the evidence, never by the issue of the document
> that specifies it.** `PGD-000` §0.3 already draws this line — its ✅ test requires *"a named file
> exists"*, which is an assertion about a specification and not about a running system. This
> document assesses **capability**, and six of the items above moved from *"the document does not
> exist"* to *"the document exists and the thing does not."* The second is a better position and it
> is not a different status.

---

### 11.3 The interim position

| # | Rule |
|---|---|
| **`GLR-28`** | Until a Security Lead is appointed, `RD-4` is assessed by the **CTO** for `S-1`, `S-3`, `S-4`, `S-5` and by **Legal Counsel** for `S-2` and `S-6`. The CTO may not assess a component the CTO's own team built (`GLR-10`), which in practice means an external reviewer is required for `S-1`'s `E6` |
| **`GLR-29`** | Until a Service Manager is appointed, `RD-5` is assessed by the **Operations Director**, who will operate the business on it. This is a worse assessor than a Service Manager and a much better one than nobody |
| **`GLR-30`** | Every interim assessment records **"interim, pending appointment"** on the form. An interim signature that reads like a permanent one removes the pressure that closes `Q-01` |

---

## 12. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| `GLR-01` | This document creates no new go/no-go decision; four already exist | 1.1 |
| `GLR-02` | `GV-009` governs the wave gate; this document governs the go-live | 2.4 |
| `GLR-03` | `RD-7` Commercial exists because a go-live creates contractual exposure on the day | 3.3 |
| `GLR-04` | A veto is a recorded statement that stops `C7` being taken as a go | 4.1 |
| `GLR-05` | Vetoes are programme-wide, site-scoped or scope-scoped; not all stop everything | 4.3 |
| `GLR-06` | An assessor may not be asked to reconsider by their reporting line | 4.4 |
| `GLR-07` | An assessor without evidence records RED, not AMBER | 4.4 |
| `GLR-08` | Opinions are recorded before the `C7` bridge convenes | 4.4 |
| `GLR-09` | A veto exercised is a normal outcome, never a performance matter | 4.4 |
| `GLR-10` | Cross-assessment binds every readiness assessment from W1 | 4.5 |
| `GLR-11` | `RD-6` escalates programme-wide only for a role that makes the system unoperable anywhere | 4.6 |
| `GLR-12` | `C2` is an input to this assessment, not a duplicate of it | 4.7 |
| `GLR-13` | Sites in scope are counted, never estimated, and stated on the form | 4.7 |
| `GLR-14` | A coverage figure without its denominator is not accepted | 5.1 |
| `GLR-15` | Readiness is never averaged; the output is seven statuses | 6.2 |
| `GLR-16` | A single-figure readiness report is returned by the PMO | 6.2 |
| `GLR-17` | The readiness position is an input to gate opinions, never a substitute | 6.4 |
| `GLR-18` | Unqualified `T` means the freeze instant; `G−n` and `S−n` for gate and site | 7.2 |
| `GLR-19` | The assessment runs twice — provisional and final | 7.2 |
| `GLR-20` | The final assessment is at `T−2 d`, before `P1` | 7.2 |
| `GLR-21` | Every AMBER carries a dated plan and a named owner on the form | 8 |
| `GLR-22` | The PMO signs for pack completeness, never for the opinions | 8 |
| `GLR-23` | A GREEN older than the `GA-03` window is not a GREEN | 9 |
| `GLR-24` | A slip never reduces the assessment | 9 |
| `GLR-25` | Ten items may never be AMBER | 10.1 |
| `GLR-26` | Three of seven dimensions have no appointed assessor; read literally, W1 cannot go live | 11.1 |
| `GLR-27` | Accessibility is an `RD-1` evidence item, not an eighth dimension | 11.2 |
| `GLR-28` | Interim `RD-4`: CTO plus Legal Counsel, with an external `E6` reviewer | 11.3 |
| `GLR-29` | Interim `RD-5`: the Operations Director | 11.3 |
| `GLR-30` | Every interim assessment is marked "interim, pending appointment" | 11.3 |
| **`GLR-31`** | **An evidence item is discharged by the evidence, never by the issue of the specifying document** | 11.4 |

**Thirty-one rules.** `GLR-01`…`GLR-31`; `GLR-31` added at the audit. Counted from this table at 2026-08-19 02:10 (+06).

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **When are the Security Lead, Service Manager and Financial Controller appointed?** `GV-009` §5.3 gives a 12–20 week lead for the first | Programme Director | **W1 minus 5 months** | `GLR-26`; `RD-4` and `RD-5` are RED until then |
| `Q-02` | Who provides the `E6` independent reviewer for `S-1` before Gate 4? | CTO with the Audit Committee | **W1** | `GLR-28` |
| `Q-03` | Does `CO-003` issue in time for `RD-7` `C-1` to be evidenceable at W1? | PMO | **W1 minus 2 months** | `RD-7` |
| `Q-04` | Is Legal Counsel a programme role or an external retainer, and what is its response time? | Programme Director | W1 | `RD-7` `C-3`, `C-5`; `S-6` |
| `Q-05` | Does `GV-009` accept `GLR-17`'s reporting relationship, or does it want the readiness form as a gate annex? | PMO | W1 | Gate report structure |
| `Q-06` | Which body accepts a Steering Committee exposure decision when the Steering Committee has not been constituted (`GV-001` `CC-01`)? | Programme Director | **Now** | `GLR-04`'s discharge route |
| `Q-07` | When an accessibility reviewer is appointed, does `F-6` become `RD-1` evidence or trigger a dimension review? | Head of Quality Engineering | W2 | `GLR-27` |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RL-003-D-01` | Whether to create a go-live go/no-go decision of this document's own | (a) A fifth decision point · (b) An instrument feeding `C7` and the gate | **(b)** | Four decisions already exist. A fifth would compete with `C7`, which `CV-14` makes non-delegable and holds by two named people | The document's output is evidence, not a decision. Its power is the veto in §4 |
| `RL-003-D-02` | Six dimensions or seven | (a) Mirror `GV-009`'s six · (b) Add Commercial | **(b)** | A go-live creates contractual exposure on the day and no other dimension owns it. `GV-009` correctly does not, because its authority is scope and funding | `RD-7` is unassessable at W1 while `CO-003` is ⛔ (`Q-03`) |
| `RL-003-D-03` | Whether to publish an overall readiness score | (a) A weighted percentage · (b) Seven statuses, never averaged | **(b)** | `PGD-A2-24` and `QAA-12` are the same defect recorded twice: a correct total concealing a wrong component | Reports are longer and harder to summarise. That is the intent |
| `RL-003-D-04` | Whether to give accessibility its own dimension | (a) Eighth dimension · (b) Evidence item inside `RD-1` | **(b)** | An eighth dimension with no assessor is a permanent RED that gets waived, and a routinely waived veto teaches that vetoes are negotiable | Accessibility visibility depends on `QA-011` coverage reporting rather than on a veto |
| `RL-003-D-05` | Whether to soften `GLR-26` | (a) Provide a waiver route so W1 can proceed · (b) State the consequence plainly and provide named interims | **(b)** | A waiver route written at issue is a waiver route that will be used at W1 | §11.3's interims are worse assessors than the real roles and are declared as such |
| `RL-003-D-06` | Time notation | (a) Leave `T−n` ambiguous across three anchors · (b) `T` = freeze instant, `G−n` gate, `S−n` site | **(b)** | Three timelines currently use `T−3` to mean three different moments | Category 12 documents all adopt `GLR-18` |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The residual gap after `GV-009` is stated before anything is written | §2.4 — eleven questions, five with residual gaps |
| `AC-02` | Nothing `GV-009` owns is restated | §5 preamble; `E1`…`E8` and `GA-01`…`GA-12` used, not redefined |
| `AC-03` | Seven dimensions exist, and the seventh is justified rather than asserted | §3.2, §3.3, `GLR-03` |
| `AC-04` | Every dimension has a named assessor and a stated veto scope | §4.2, §4.3 — seven rows |
| `AC-05` | Every dimension has enumerated evidence in `GV-009` classes | §5 — 39 items counted |
| `AC-06` | The scoring rule refuses to average, with the reason recorded | `GLR-15`, `GLR-16`, `RL-003-D-03` |
| `AC-07` | The three conflicting `T−n` timelines are reconciled | `GLR-18`, §7.2 |
| `AC-08` | An instrument exists that a person can actually fill in | §8 |
| `AC-09` | Re-assessment on slip is defined in tiers | §9 |
| `AC-10` | Items that may never be conditional are enumerated | §10.1 — ten items |
| `AC-11` | Every unfilled assessor role is named with its consequence | §11.1, `GLR-26` |
| `AC-12` | No rule identifier collides with any existing identifier | §2.5 — `GLR` verified at zero across 754 files |

**Definition of done.** As `RL-001` §16, and subject to the same `PGD-A2-25` qualification.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `GV-009` | Evidence classes, standing criteria and gate process inherited; §2.4 states the boundary |
| Upstream | `06-02` §4 | The 70 gate criteria, authoritative and unrestated |
| Upstream | `CM-012` | Eight branch domains, `C2`, and the `RB-11` re-confirmation tiers |
| Upstream | `DM-014` | `C7` is the decision this document's output feeds; `T1`…`T7` inform §10.1 |
| Upstream | `QA-006`…`QA-011` | Each names `RL-003` as its evidence consumer; §5.1 discharges that |
| Upstream | `MG-004` | Reconciliation governance becomes `RD-3` evidence |
| Upstream | `RL-002` §8 | The go-live checklist is `RD-2` `T-1` |
| Downstream | **`RL-004`** | §8's go-live-critical roles feed `GLR-11`; per-site assessment runs per tranche |
| Downstream | **`RL-005`** | Readiness position versus actual outcome is a PIR input |
| Downstream | `GV-009` | `GLR-17` reports the position into the gate report §6.2 section 2 |
| Upstream | `SV-001`, `SV-003` (issued 2026-08-19) | Specify the service model and runbooks `RD-5` assesses |
| Downstream | `SV-004`, `SV-005` (issued 2026-08-19) | Must be **implemented** before `O-2` and `O-3` have evidence. The **Service Manager role**, not the document, is what `RD-5` still lacks |
| Downstream | `CO-003` ⛔ | Must exist before `RD-7` `C-1` is evidenceable |
| Upstream | `CH-002`, `CH-004`, `CH-005` (issued 2026-08-19) | `RD-6` evidence `P-1`, `P-3`, `P-4`; §11.4 records that issue ≠ evidence |
| Lateral | `BE-003` §9 step 6 | Mis-cites `RL-003` for emergency change; corrected in `RL-001` §9.4, finding `RLA-01` |

---

## 17. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`RL-001`](RL-001_Release_Management_and_Versioning_Policy.md) ·
[`RL-002`](RL-002_Deployment_Plan_and_Go_Live_Checklist.md) ·
[`RL-004`](RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) ·
[`RL-005`](RL-005_Post_Implementation_Review_Standard.md) ·
[`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md`](../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) ·
[`../08_Quality_Engineering_and_Test/QA-009_UAT_Plan_and_Business_Sign_off_Protocol.md`](../08_Quality_Engineering_and_Test/QA-009_UAT_Plan_and_Business_Sign_off_Protocol.md) ·
[`../08_Quality_Engineering_and_Test/QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md`](../08_Quality_Engineering_and_Test/QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md) ·
[`../09_Data_Migration_and_Cutover/MG-004_Reconciliation_and_Validation_Plan.md`](../09_Data_Migration_and_Cutover/MG-004_Reconciliation_and_Validation_Plan.md) ·
[`../05_Security_Privacy_and_Compliance/SC-009_Vulnerability_Management_and_Penetration_Test_Plan.md`](../05_Security_Privacy_and_Compliance/SC-009_Vulnerability_Management_and_Penetration_Test_Plan.md)

**Workspace**
`../../project_content/16_Change_Management_and_Comms/CM-012_Branch_Readiness_Communication_Checklist.md` ·
`../../project_content/16_Change_Management_and_Comms/CM-006_Go_Live_Announcement_Pack.md` ·
`../../project_content/12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §4 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §4, §6

**External standards** *(verified 2026-08-19)*

| Source | Edition | Used for |
|---|---|---|
| ISO 21502:2020 | Current | §2.1; gates and decision points |
| UK IPA / OGC Gateway Review | **Gate 4 — Readiness for Service** | The seven-dimension shape |
| PRINCE2 | **7th Edition (2023)** | §9, §10 — exception and tolerance |
| ISO 9001:2015 | §8.6 | `GLR-15`'s non-averaging rule |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.1 | 2026-08-19 | Programme Management Office | **Audit corrections, `PGD-AUDIT-CAT-12`.** `RLA-17` — six evidence items were written against documents that were authored concurrently and issued the same day. All six corrected; **none changed status**, because each was blocked by a missing *capability* rather than a missing document. §11.4 and `GLR-31` added to make that distinction a rule rather than a footnote | *Pending — `GV-001` `CC-01`* |
| 1.0 | 2026-08-19 | Programme Management Office | Initial issue. Thirty `GLR` rules; seven dimensions; 39 evidence items; ten never-AMBER items; one form. States the residual gap after `GV-009` before writing anything, and restates nothing `GV-009` owns. Adds the seventh dimension — **Commercial** — with its justification. Refuses an averaged readiness score. Reconciles three conflicting `T−n` timelines. **Records that three of seven dimensions have no appointed assessor, and that read literally this makes Wave 1 unable to go live** | *Pending — `GV-001` `CC-01`* |

---

*`RL-003` · Category 12 · Rule space `GLR` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
