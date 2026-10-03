---
id: TS-018
title: Defect Taxonomy, Triage and Sign-off Forms
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead with Programme
author: QA Lead with Programme Manager and Quality Manager
reviewers: [CTO, Programme Manager, Quality Manager, Solution Architect, CFO delegate, Support Lead, Business Owners Forum representative]
approver: Programme Manager with CTO
content_class: E
purpose: >
  The severity and priority definitions, the triage rules, the deferral criteria and the acceptance
  sign-off forms for all nine wave gates. Go-live decisions are taken against an open-defect profile,
  and without agreed severity definitions those decisions are arguments: the developer's Medium is
  the branch manager's Critical, the deferral that looked reasonable in a triage meeting is the
  reason a gate is contested six weeks later, and a gate signed without a form is a gate nobody can
  evidence was signed.
traces_to: [06-02, 06-02 §4, 05-05, 05-06 §11, 05-06 §12, M23, M60, M66, CG-004, CG-013, SP-005, SP-031, OP-002, DM-013, TS-001, TS-002, TS-003, TS-004, TS-005, TS-006, TS-007, TS-008, TS-009, TS-010, TS-011, TS-012, TS-013, TS-014, TS-015, TS-016, TS-017, RF-006]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Wave Gate Acceptance Criteria — nine gates, 70 named criteria counted by enumeration 2026-08-19, "each gate is a formal Go/No-Go; all criteria must be met; partial passes are recorded as conditional with a dated remediation plan"; Gate 1 G1-09 zero critical or high security findings
    verified: 2026-08-19
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md §237 — "defect" is reserved for a software or product defect, bound to M23 and TS-018; "bug" is permitted in engineering content only
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M23_Quality_Management_System.md §5 FR-QMS-023 classification and severity derived from category, severity and ISO clause; §9 BRU-QMS-02 root cause and CAPA required before closure, BRU-QMS-09 recurrence escalates severity; the fix.nonconformance model
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md §12 AUT-ITS-02 — an M30 alert, M28 integration failure or M29 security event creates an incident automatically with source, configuration item and severity, de-duplicated against open incidents
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# Defect Taxonomy, Triage and Sign-off Forms

| Item | Value |
|---|---|
| Test level | **All** — every pack in Category 13 raises defects under this file |
| Role executing | QA Lead triages; the Programme Manager and CTO sign gates |
| Modules covered | All |
| Portals covered | All |
| Environment | All, including production for smoke findings (`TS-013`) |
| Wave | W1 · **before the first defect is raised** |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All six
> sections retained in order. §4 is subdivided by artefact — taxonomy, triage, deferral, forms — which
> is the addition and is justified: nine gate forms and a severity scale do not belong in one section.

---

## 1. Purpose

`06-02` §4 states the rule that makes this file necessary: *"Each gate is a formal Go/No-Go. **All
criteria must be met**; partial passes are recorded as conditional with a dated remediation plan."*

**"All criteria must be met" is only enforceable if everyone means the same thing by "met".** And the
gates themselves already depend on a severity scale that does not exist anywhere in the repository:
`G1-09` requires *"zero critical or high security findings"*, and no document defines Critical or
High. That is the specific gap this file fills.

Three failures follow from its absence:

| Absent | Consequence |
|---|---|
| Agreed severity definitions | `G1-09` is unenforceable. Two people can read the same defect list and reach opposite Go/No-Go conclusions, and the louder one wins |
| Deferral criteria | Every deferral is negotiated individually under schedule pressure, and the accumulated deferrals are invisible at the gate that matters |
| Sign-off forms | A gate is claimed in a slide rather than recorded on an artefact, and `06-02`'s "conditional with a dated remediation plan" has nowhere to live |

---

## 2. Scope

**In scope.** Severity and priority definitions; the distinction between defect, non-conformance and
incident; triage rules, cadence and membership; the routing rules the packs invoke; deferral criteria
and the deferral register; the nine gate acceptance forms; the conditional-pass mechanism; and
defect metrics.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Non-conformance and CAPA workflow | `M23` — §4.2 states the boundary |
| IT incident management and its own severity scale | `M66`, `SP-031`, `OP-002` |
| Defect-tracking tooling | `06-04` (planned, absent) |
| Migration reconciliation acceptance | `DM-013`; this file supplies only its sign-off form |
| Risk register | `00-04`; a chronic defect pattern **escalates to** it, §4.6 |
| Decisions taken while triaging | `RF-006` decision log — **unwritten**, `O-03` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **QA Lead** | Triage, severity assignment, the deferral register |
| **Test analysts and business executors** | Knowing what severity to propose and what a comment on a pass becomes |
| **Module business owners** | Understanding what a deferral commits them to |
| **Programme Manager and CTO** | The gate forms and the conditional-pass mechanism |
| **Quality Manager** | The `M23` boundary and the ISO evidence chain |
| **Support Lead** | The `M66` boundary at go-live and during hypercare |
| **Steering Committee** | Reading an open-defect profile and knowing what it means |

---

## 4. Content

### 4.1 Severity — what is broken

**Severity is a property of the defect. Priority is a decision about when to fix it.** Conflating
them is the commonest failure in defect management, and it is why the two scales below are separate
and assigned by different people.

| Severity | Definition | Examples from Category 13 |
|---|---|---|
| **`S1` Critical** | The business cannot operate, money or data is wrong, a statutory output is non-compliant, or a party can reach data they must not | Stock moves without a valuation effect (`TS-004`); a Mushak field wrong (`TS-009`); offline data loss (`TS-015`); a denied portal cell that opens through the API (`TS-017`); a payroll net-pay error (`TS-010`) |
| **`S2` High** | A core task cannot be completed, or completed only by a workaround that will not survive volume; a control does not operate | A hard rule not enforced at the model layer; a first-time user cannot complete a `P0` customer task (`TS-011`); an audit-trail gap (`TS-017`); a commercial number configured wrongly (`TS-007`) |
| **`S3` Medium** | The task can be completed with a known workaround; a non-core function is broken; a WCAG criterion fails without blocking the task | A bulk action failing on one column; an incorrect label; a report figure right and slow |
| **`S4` Low** | Cosmetic, or an inconvenience with no operational consequence | Alignment, a wrong tooltip, an inconsistent capital letter |

**Severity is proposed by the finder and confirmed in triage. It is never lowered to make a gate.**
That is rule `DF-04`.

#### Automatic `S1`, regardless of the finder's proposal

The packs declare these and this file consolidates them, so the list has one home:

| Trigger | Source |
|---|---|
| A posting that does not reconcile to its source, or a control total that does not tie | `TS-004` §5 |
| Any Mushak, VAT, register or return defect, or a reused statutory sequence | `TS-009` §5 |
| Stock moving without a valuation effect; custody transferring with one party recorded | `TS-008` §5 |
| Any offline data loss or double-application; sync reported complete while queued | `TS-015` §5 |
| Any wrong payroll figure | `TS-010` §5 |
| Any party reaching data outside their scope, by any route | `TS-011` §5, `TS-017` §5 |
| Any residency-classified field written or transferred outside its permitted store | `TS-005` §5, `TS-017` §5 |
| A denial that holds in the UI and not through the API | `TS-017` §5 |
| A target met by degrading another | `TS-014` §5 |
| An assisted user cannot complete a portal's primary task | `TS-016` §5 |

### 4.2 The three-record boundary

`CG-004` reserves **defect** for a software or product defect and binds the term to `M23` and this
file. `TS-001` §4.10 states the boundary; this is the operational mapping.

| | **Defect** (`TS-018`) | **Non-conformance** (`M23`) | **Incident** (`M66`) |
|---|---|---|---|
| Is | The system does not do what a requirement says | A process or output departed from a specified requirement | A live service is degraded or unavailable now |
| Severity basis | **Requirement-driven** | **ISO-clause-driven** | **Impact-driven** |
| Scale | `S1`–`S4`, §4.1 | `M23` classification and severity (`FR-QMS-023`) | `M66` incident severity |
| Closure needs | Fix verified by re-execution | **Root cause and CAPA** (`BRU-QMS-02`), then effectiveness verification (`BRU-QMS-03`) | Service restored, then a problem record |
| Owner | Module business owner with engineering | Process owner | `R33` with Support Lead |

**Three overlaps, handled explicitly:**

| Situation | Records raised |
|---|---|
| A defect is found in production | **Incident** *and* **defect**, linked. The incident closes on restoration; the defect closes on a verified fix |
| A defect's root cause is a process failure — an untested configuration change, a skipped review | **Defect** *and* **non-conformance** (`BRU-QMS-02`), linked |
| A defect recurs after being fixed | Defect reopened at **one severity higher** (§4.3 `TR-07`), *and* a non-conformance, because the regression derivation failed (`TS-013` `RS-03`) |

**The records are linked, never merged.** Three severity scales exist because three different
questions are being answered, and forcing one scale across all three produces a scale that fits
none.

### 4.3 Priority and triage

**Priority is when it gets fixed**, decided by the business owner with QA, not by the finder.

| Priority | Meaning | Target |
|---|---|---|
| **`P1` Immediate** | Fix now; blocks a test cycle or a wave gate | Same day for `S1`; 3 working days for `S2` |
| **`P2` Current cycle** | Fix inside the current sprint or test cycle | Before the cycle closes |
| **`P3` Next wave** | Scheduled, tracked, and reported at each gate until fixed | Named wave |
| **`P4` Backlog** | Accepted and unscheduled; **reviewed quarterly and either scheduled or withdrawn** | Reviewed, never silently retained |

#### Triage rules

| # | Rule |
|---|---|
| **TR-01** | Triage runs **daily during a test cycle** and weekly otherwise. `S1` defects are triaged on discovery, not at the next meeting |
| **TR-02** | Triage membership: **QA Lead, the affected module business owner, an engineering representative, and the Solution Architect for any cross-module defect**. A triage without the business owner assigns priority without the person who carries the consequence |
| **TR-03** | Every defect leaves triage with a severity, a priority, an owner and a target. **"Under investigation" is not an outcome**; if the cause is unknown, the outcome is an investigation task with an owner and a date |
| **TR-04** | **A defect from a UAT executor's business judgement is a requirement defect**, routed to the module business owner, not a test error (`TS-006` `UA-06`) |
| **TR-05** | **A boundary defect is routed to both sides** — the emitting and consuming module — plus the Solution Architect. A seam defect with one owner is the kind that stays open (`TS-003` §5) |
| **TR-06** | **A defect that reveals a wrong or missing requirement is escalated, not fixed.** It goes to the requirement owner and, where statutory or legal, into `CG-013` escalation |
| **TR-07** | **A recurring defect is reopened one severity higher** and raises a non-conformance. `TS-013` `RS-03` promotes its case to the permanent regression core |
| **TR-08** | **A defect found in a shadow process — a spreadsheet or an out-of-system workaround — is a scope gap, not a defect** (`TS-012` `EE-05`), routed to the Programme Manager. Logging it as a defect hides it inside a defect count |
| **TR-09** | **Severity is never adjusted to affect a gate outcome** (`DF-04`). Where severity is genuinely contested, the disagreement is recorded and escalated per `CG-002` §7 |
| **TR-10** | Every triage decision that sets a precedent is logged in `RF-006` (`CG-008` DoD) — **`O-03`** |

### 4.4 Deferral

A deferral is a decision to go live with a known defect. It is available, and it is expensive to
misuse, so the criteria are explicit.

| # | Rule |
|---|---|
| **DF-01** | A deferral is a **recorded decision** with a named decision-maker, a severity, a business justification, a workaround, an affected-population estimate and a target wave (`TX-16`) |
| **DF-02** | **`S1` is never deferrable.** No exceptions, no approver |
| **DF-03** | **`S2` is deferrable only by the accountable business owner *and* the Programme Manager jointly**, and only with a stated workaround that the affected role has been shown |
| **DF-04** | **Severity is not adjusted to enable a deferral** (`TR-09`) |
| **DF-05** | **Four packs override `DF-03` and permit no `S2` deferral at all**, each for a stated reason: `TS-009` statutory output, `TS-010` payroll, `TS-011` external scope, `TS-017` access and privacy. In those four, a High defect is a No-Go |
| **DF-06** | Every deferral is **re-presented at every subsequent gate** until closed. A deferral is not a disposal |
| **DF-07** | **The deferral register is read aloud at the gate.** A count is not a profile; the gate needs to hear what is being accepted |
| **DF-08** | **A deferral affecting a Bengali-reading or field population requires that population's representative to be present** at the decision. `TS-006` and `TS-015` cover 526–1,022 and 275–635 people respectively who do not attend triage |

#### The deferral register

| Field | Content |
|---|---|
| Defect ID and severity | |
| Wave deferred at, and every gate since (`DF-06`) | |
| Business justification | |
| Workaround, and who has been shown it | |
| Affected roles and headcount | |
| Decision-makers, named | |
| Target wave for closure | |
| **Status at the current gate** | Open · closed · re-deferred **with a reason** |

### 4.5 The gate acceptance forms

One form per gate, `G1`–`G9`, against the criteria in `06-02` §4. **The form is the record**; a gate
claimed without one is unevidenced.

#### Standard form

```
GATE ACCEPTANCE — G<n> <name>            Month <n> · Wave W<n>
Release: <identifier>          Date: <YYYY-MM-DD>          Form version: <n>

1  CRITERIA
   | # | Criterion (06-02 §4, verbatim) | Evidence reference | Met / Not met / Conditional |

2  TEST COVERAGE
   | Level | Pack | Executed / planned | Passed / executed | Denominator stated |
   (TS-001 §4.9 measures; every percentage carries its basis — TS-001 §4.4)

3  OPEN DEFECT PROFILE
   | Severity | Open | Deferred at this gate | Deferred from earlier gates |
   S1 must read 0 / 0 / 0.

4  DEFERRAL REGISTER
   Read aloud (DF-07). Every entry, with its affected population.

5  NON-FUNCTIONAL POSITION
   | NFR | Target | Measured at 1.5× peak | Met |   (TS-014)

6  STATUTORY POSITION
   | Instrument | Verified by | Date | Position |   (TS-009, TS-010, TS-017 Block G)

7  BILINGUAL POSITION
   Translation coverage %, in-context sign-off status (BN-018), open truncation defects.

8  ACCESSIBILITY POSITION
   Per-criterion conformance per portal (TS-016 AX-03), open S1/S2.

9  CONDITIONAL ITEMS
   | Item | Owner | Remediation | Date |   (06-02 §4 requires the plan to be dated)

10 DECISION
   GO / CONDITIONAL GO / NO-GO
   Programme Manager: ______  CTO: ______  Business owner(s): ______
   Steering Committee noted: ______
```

#### Per-gate additions

| Gate | Criteria | Additional required signatory and section |
|:--:|---:|---|
| **`G1`** Foundation, M4 | 12 | **Migration reconciliation signed** (`G1-05`, `DM-013` form §4.7); security position with `G1-09` zero `S1`/`S2`; UAT signatures from **named** super-users (`G1-11`) |
| **`G2`** Field Operations, M8 | 10 | **Field-test evidence** (`TS-015`): location, network, device per run; inventory accuracy verified by count (`G2-06`) |
| **`G3`** Money & Movement, M13 | 9 | **CFO signature and external tax-adviser confirmation** (`G3-04`); trial-balance tie (`G3-08`) |
| **`G4`** Agreements & Contact, M18 | 10 | **`G4-10` — every v1.0 BRD requirement demonstrated as delivered or formally superseded**, as a traceability report, not an assertion |
| **`G5`** People, Quality & MSP, M22 | 7 | **Joint HR and CFO parallel-run signature** (`TS-010` §6) |
| **`G6`** New Asset Businesses, M26 | 6 | Zero units released without a destruction certificate, as a **count** (`G6-02`) |
| **`G7`** Marketplace, M30 | 6 | External VAT advice on marketplace treatment (`G7-05`); payout accuracy at 100% with zero variance (`G7-02`) |
| **`G8`** Intelligence & Sustainability, M34 | 5 | Automation coverage measured, not modelled (`G8-03`) |
| **`G9`** Expansion Readiness, M36 | 5 | **Full-scale load test at 1.5× projected peak** (`G9-03`, `TS-014`); documentation handover accepted |

#### The conditional-pass mechanism

`06-02` §4 permits a partial pass *"recorded as conditional with a dated remediation plan"*. Four
rules govern it:

| # | Rule |
|---|---|
| **CP-G1** | A conditional pass names **which criteria are not met**, not "minor items outstanding" |
| **CP-G2** | Every conditional item has an owner and a **date**, and the date is before the next gate |
| **CP-G3** | **A conditional item unclosed at the next gate makes that gate conditional too**, and the chain is shown. Two consecutive conditional gates on the same item escalate to the Steering Committee |
| **CP-G4** | **No gate is conditional on an `S1` defect, a statutory position, or an access or residency finding.** Those are No-Go items, and `DF-02`/`DF-05` already say so |

### 4.6 Defect metrics

| Measure | Definition | Reported |
|---|---|---|
| Open profile by severity | Count, at the gate | Every gate |
| **Defect density by module** | Defects ÷ requirements delivered, with the denominator stated (`TS-001` §4.4) | Per wave |
| Escape rate | Defects found in production ÷ total found | Per wave — **the single most diagnostic measure of the test approach** |
| Recurrence rate | Reopened after a verified fix (`TR-07`) | Per wave; target zero |
| Requirement-defect rate | `TR-04`/`TR-06` defects ÷ total | Per wave — a rising rate points at analysis, not at build |
| Scope gaps (`TR-08`) | Count, and the processes they were found in | Per wave; feeds `06-02` §5 criterion 1 |
| Mean age of open `S2` | Days | Weekly |
| Deferral count and cumulative age | From the register | Every gate (`DF-06`) |
| **Chronic pattern** | The same defect category recurring across three waves | **Escalates to the risk register `00-04`**, not to the defect log |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `06-02` §4 | The 70 criteria the forms are built from — counted 2026-08-19 |
| `TS-001` | Levels, coverage measures, and the denominator rule every form's §2 uses |
| `TS-003`–`TS-017` | Every pack raises defects under §4.1 and invokes a routing rule from §4.3 |
| `M23` | The non-conformance boundary and the CAPA path |
| `M66`, `OP-002`, `SP-031` | The incident boundary at go-live and in hypercare |
| `DM-013` | The migration reconciliation form referenced by the `G1` addition |
| `CG-004` | The reserved meaning of "defect" |
| `CG-013` | The legal and statutory escalation path `TR-06` invokes |
| `RF-006` | Where precedent-setting triage decisions are logged — **unwritten** |
| `00-04` | The risk register a chronic pattern escalates into |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | At every gate, before the form is issued |
| Trigger for out-of-cycle review | A contested severity that escalates to Steering; a gate criterion added or removed in `06-02`; a new pack in Category 13; a change to the `M23` or `M66` severity scales |
| Owner | QA Lead with Programme Manager |
| Change control | Severity definitions and deferral rules require Programme Manager and CTO approval — a change to `DF-02` or `CP-G4` changes what "Go" means |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`06-02` `G1-09` already requires "zero critical or high security findings" and no severity definition existed until this file.** Any severity judgement made before `W1` — in `SIT`, in early UAT, in a security scan — was made against no scale. **This file is `P1`/W1 and it should arguably be `P0`**, because every other Category 13 pack depends on it to express an exit criterion | Programme Content Lead with QA Lead | **W1 — priority review** |
| **O-02** | **No defect-tracking tool is specified.** `TR-01`'s daily triage, the deferral register, `DF-06` re-presentation across gates, and every §4.6 metric are tool functions. `TS-001` `O-01` (`06-04` absent) and `TS-013` `O-02` both bite here; **a deferral register in a spreadsheet is itself the shadow artefact `TS-012` `EE-05` fails a scenario for** | CTO with QA Lead | **W1 — before the first defect is raised** |
| **O-03** | **`RF-006` decision log is unwritten** (Category 99 unstarted) and `TR-10` requires precedent-setting triage decisions to be logged there. This is the same exposure audit `AUDIT-001` `AF-04` recorded for the module repository's missing `00-05` decision log — **and the Master Index created `RF-006` specifically so content would not repeat it** | Programme Content Lead | **W1** |
| **O-04** | **`DF-08` requires a field or Bengali-reading population representative at any deferral affecting them, and no such representative role exists.** 526–1,022 people in `TS-006`'s scope and 275–635 in `TS-015`'s do not attend triage. `06-01` §4 provides branch champions at 4 hours a week during rollout — **whether a champion can hold this role is undecided** | Programme Manager with Operations Director | **W1** |
| **O-05** | **`G4-10` requires every v1.0 BRD requirement demonstrated as delivered or formally superseded, and that is a traceability query with no register to run it against.** `RF-003` is unwritten (`TS-001` `O-02`) and the requirement denominator is contested (`TS-001` `O-04`). **The most demanding single criterion in `06-02` §4 has no mechanism** | Enterprise Architecture with QA Lead | **W4 — but the register must exist from W1** |
| **O-06** | **The `M23` and `M66` severity scales have not been read across against §4.1.** §4.2 states that three scales are correct because three questions are asked, **and the mapping between them has not been agreed with the Quality Manager or the Support Lead.** An `S1` defect that becomes an `M66` incident needs an agreed incident severity, or the escalation path breaks at go-live | QA Lead with Quality Manager and Support Lead | **W1 — before the first production release** |
| **O-07** | **`06-02` §4 gate criteria are stated as pass/fail and several are unmeasurable as written.** `G3-04` requires NBR acceptance, which occurs after go-live (`TS-009` `O-02`); `G2-04` requires travel time reduced by ≥ 15% against a baseline `06-02` §6 says must be signed off before the wave — and is not. **The forms will expose these one gate at a time unless they are reviewed together first** | Programme Manager with CTO | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision justified
- [x] **`G1-09`'s dependence on an undefined severity scale identified as the specific gap this file fills**
- [x] Severity and priority separated, defined, and assigned by different people
- [x] The ten automatic-`S1` triggers consolidated from the packs that declare them, so the list has one home
- [x] **The three-record boundary stated with all three overlaps handled, and the reason three scales are correct**
- [x] Ten triage rules stated, including the requirement-defect, boundary and scope-gap routings the packs invoke
- [x] Eight deferral rules stated, with `S1` non-deferrable and the four packs that permit no `S2` deferral named
- [x] Deferral register fields specified, including affected population and re-presentation across gates
- [x] A standard gate form with ten sections, and per-gate additions for all nine gates against `06-02` §4
- [x] **The conditional-pass mechanism given four rules, including the chain rule that prevents a conditional item being carried indefinitely**
- [x] Nine defect metrics defined, with escape rate identified as the most diagnostic
- [x] Chronic patterns routed to the risk register rather than the defect log
- [x] All internal links resolve
- [x] Seven open items recorded, including two criteria in `06-02` §4 that are unmeasurable as written
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The nine gate forms instantiated as usable artefacts — outstanding; this file specifies them**
- [ ] **`O-02` no defect-tracking tool — outstanding; blocks triage, the register and every metric**
- [ ] **`O-03` `RF-006` unwritten — outstanding; `TR-10` undischargeable**
- [ ] **`O-06` `M23`/`M66` severity read-across not agreed — outstanding; breaks at the first production release**
- [ ] Named approvers recorded — **pending Programme Manager and CTO**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
