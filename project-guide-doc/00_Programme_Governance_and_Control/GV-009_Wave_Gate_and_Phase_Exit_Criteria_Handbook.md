---
id: GV-009
title: Wave Gate & Phase Exit Criteria Handbook
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Management Office
approver: ERP Steering Committee
standards_basis: ISO 21502:2020 §6.4 gates and decision points · PRINCE2 7th Edition (2023) stage boundaries and end-stage assessment · PMBOK Guide 7th Edition (Measurement, Delivery) · UK IPA / OGC Gateway Review practice · ISO 9001:2015 §8.6 release of products
traces_to: PGD-000 GV-009 · 06-02 §4 (70 gate criteria, no evidence standard) · 06-01 §3 (46 gate criteria, competing set)
depends_on: GV-001, GV-002, GV-004
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-009 — Wave Gate & Phase Exit Criteria Handbook
# 1000FiX ERP System & Portal Suite v2.0

### Category 00 · Code `GV` · ISO 21502:2020 · PRINCE2 7 · IPA Gateway practice

---

> **`PGD-000` records the gap this document fills:** *"`06-02` §4 lists gate criteria but not the
> **evidence standard**, the **assessor**, or the **consequence of a failed gate**."*
>
> A criterion without an evidence standard is a criterion that will be argued about at the gate, by
> people under schedule pressure, with the next wave's funding waiting. This handbook decides those
> arguments in advance.

---

## 1. Purpose

This handbook defines what a wave gate is, who assesses it, what evidence each criterion requires,
what the possible outcomes are, and what happens after each of them.

The programme already has good gate *criteria*. It has two sets of them — 70 in `06-02` §4 and 46
in `06-01` §3 — with no declared precedence, no evidence standard, no named assessor and no defined
consequence of failure. This document resolves all four.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The purpose and authority of a wave gate |
| 2 | **Reconciliation of the two competing criteria sets** |
| 3 | The six readiness dimensions every gate assesses |
| 4 | **The evidence standard** — eight evidence classes, and which criterion types require which |
| 5 | The assessor per dimension, and the independence rules |
| 6 | The gate process: T−6 weeks to T+2 weeks |
| 7 | Gate outcomes: Pass, Conditional Pass, Fail — and the consequence of each |
| 8 | The nine gates, with evidence class and assessor per criterion |
| 9 | **Standing criteria** added at every gate — security, data protection, documentation, operational readiness |
| 10 | Conflicts between gate criteria and the KPI register |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The wave dates | `GV-004` §6.1 | A gate is a decision point; the schedule places it |
| Funding release | `GV-008` §5.3 | The gate result triggers release; it does not decide the amount |
| Test strategy, levels, entry/exit per test level | `QA-001` | A **test** exit criterion is not a **gate** criterion. The gate consumes test evidence |
| Defect severity and the defect thresholds that block a gate | `QA-010` | **⛔ Does not exist.** See §9.3 |
| Go-live readiness at branch level | `RL-003`, `RL-004` | A wave gate is programme-level; site readiness is release-level |
| UAT scripting and participant selection | `QA-009` | The gate consumes the UAT sign-off record |

### 1.2 Intended audience

| Audience | What they use this handbook for |
|---|---|
| **Steering Committee** | The instrument by which they take a Go/No-Go decision, and the evidence they are entitled to demand |
| **Programme Director / PMO** | The gate process and the evidence pack contents |
| **Squad leads** | What they must produce, and by when — the pack is assembled over six weeks, not in one |
| **QA Lead, Security Lead, Solution Architect** | Their assessment responsibilities |
| **Business owners** | What they are signing when they sign a UAT record |
| **Audit Committee** | The gates from Wave 4 at which independent assurance is required |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | How this handbook conforms | Departure |
|---|---|---|---|
| **ISO 21502:2020** §6.4 | Gates and decision points; pre-defined criteria; a decision to proceed, stop or revise | §6 outcomes; §5 assessors | None |
| **PRINCE2 7th Edition (2023)** | Stage boundaries; End Stage Assessment; the Project Board decides continuation; management by exception | Each wave is a stage; the Steering Committee performs the End Stage Assessment | PRINCE2's Exception Plan is realised as the Conditional Pass remediation plan in §6.3 |
| **UK IPA / OGC Gateway Review** | Independent review by a panel at prescribed points across a six-gate lifecycle (0–5); a delivery-confidence assessment | §5.2 introduces independent review from Gate 4, mapped from Gateway practice | Adapted: 1000FiX has nine delivery waves, not six lifecycle gates. Independence is provided by `GV-010`, not by a central authority |
| **PMBOK Guide 7th Edition** | *Measurement* and *Delivery* performance domains; acceptance criteria and definition of done | §4 evidence classes; §9.1 standing criteria | None |
| **ISO 9001:2015** §8.6 | Release of products and services: planned arrangements completed, with evidence of conformity and traceability to the authorising person | §6.4 requires a named signatory per criterion. **This is a certification requirement, not a preference** | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| KPI, Benefits & Acceptance Criteria §4 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` | **70 gate criteria across nine gates** — the primary set |
| Implementation Roadmap §3 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` | **46 gate criteria** stated per wave — the competing set |
| KPI Register §2 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` | 95 registered KPIs with W4 and W8 targets — against which §9.4 tests the gate criteria |
| Delivery Method | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` §5 | *"Wave gate — formal Go/No-Go with the Steering Committee against published criteria"* |
| Contingency | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` §9 | *"Business UAT capacity unavailable → wave gate slips; development does not run ahead into unaccepted work"* |
| Category 13 TS Audit | `../../project_content/_AUDIT/AUDIT-014` | `TS-01`, `TS-02` — four test packs cannot be executed; nine are consumed a wave before they exist |
| Governance Framework | [`GV-002`](GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) §5.2 row 6 | Wave Go/No-Go is a Steering Committee decision |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `GV-009` register row | `PGD-000` | §4 evidence standard · §5 assessors · §6.3 consequence of failure |
| `TS-02` *(gate half)* | `AUDIT-014` | §9.3 makes "the test pack exists and is executable" a **standing entry criterion**, so a pack that cannot be run is caught at T−6 weeks, not at the gate |
| **New — `PGD-A2-11`** | this document | **Two gate criteria sets exist** — 70 in `06-02` §4 and 46 in `06-01` §3 — with no declared precedence. §3.1 resolves it |
| **New — `PGD-A2-12`** | this document | **Gate criterion `G1-03` requires a standard the KPI register does not expect until Wave 8.** §9.4 |

---

## 3. What a Wave Gate Is

### 3.1 Resolving the two criteria sets — `PGD-A2-11`

| Set | Location | Criteria | Nature |
|---|---|---:|---|
| **Primary** | `06-02` §4, tables `G1-01` … `G9-05` | **70** | Identified, numbered, with an evidence column at `G1` |
| **Secondary** | `06-01` §3, "Gate criteria" bullets per wave | **46** | Unnumbered prose bullets inside the wave descriptions |

**Counted from the source tables at 2026-08-18 02:06:** `06-02` — 12 + 10 + 9 + 10 + 7 + 6 + 6 + 5 +
5 = **70**. `06-01` — 6 + 6 + 6 + 6 + 5 + 5 + 5 + 4 + 3 = **46**.

> **Ruling.** `06-02` §4 is the **authoritative** gate criteria set. `06-01` §3's bullets are a
> *narrative summary* of it and carry no independent authority. Where they differ, `06-02` wins.
>
> This matters because the two sets are not identical: `06-02` `G1` includes UAT sign-off,
> runbook delivery, audit-trail completeness, SSO operation and performance testing; `06-01`'s
> Wave 1 bullets include none of those five. **A team preparing for the gate from `06-01` would
> arrive missing five of twelve criteria.** `06-01` §3 must carry a pointer to `06-02` §4.

### 3.2 Authority and purpose

| Attribute | Provision |
|---|---|
| **Decision** | Go / No-Go on releasing the next wave and its funding |
| **Authority** | **ERP Steering Committee** (`GV-002` §5.2 row 6) |
| **Independent input** | Audit Committee, from **Gate 4** onward (`GV-001` `CC-08`) |
| **Cannot be taken by** | The Programme Director, the CTO, or any squad. A gate assessed by the people who built the work is not a gate |
| **Frequency** | Nine gates, `G1` … `G9`, at the milestones in `GV-004` §6.1 |
| **Effect of a pass** | The next wave's scope is locked (`GV-006` §6.3), its funding is released (`GV-008` §5.3), and the delivered wave's benefits become claimable |
| **Effect of a fail** | §6.3 |

### 3.3 The six readiness dimensions

Every gate assesses six dimensions. `06-02`'s criteria are functional and technical almost
exclusively; four dimensions are added here because a wave that is functionally complete and
operationally unsupportable has not finished.

| # | Dimension | Question | Assessor |
|:--:|---|---|---|
| **D1** | **Functional** | Does it do what the requirements said? | Named business owner + QA Lead |
| **D2** | **Technical** | Is it built to the architecture, performant, and upgradable? | Solution Architect |
| **D3** | **Data** | Is the data migrated, reconciled and of stated quality? | Data owner + CFO for financial data |
| **D4** | **Security & privacy** | Is it safe, and is it lawful? | Security Lead + Data Protection Forum |
| **D5** | **Operational** | Can it be run, supported and recovered? | Service Manager |
| **D6** | **People** | Are users trained, and is the change absorbed? | Change lead + HR Director |

> **Dimensions D4, D5 and D6 have no criteria in `06-02` beyond `G1-09` (zero critical/high
> security findings).** §9.1 adds standing criteria for all three at every gate. Without them a
> wave can pass with no runbook, no on-call rota, no DPIA and no trained users — which is the
> position `AUDIT-017` described as *"operational content and no operational capability."*

---

## 4. The Evidence Standard

### 4.1 Evidence classes

> **Rule `GA-01` — a criterion is met when its evidence exists, is dated, is attributable and is
> reproducible.** An assertion by the delivery team is not evidence.

| Class | Evidence type | Must record | Reproducible by |
|:--:|---|---|---|
| **E1** | **Witnessed demonstration** | Script, date, witnesses by name and role, environment, result per step | Re-running the script |
| **E2** | **System-generated report** | Query or report definition, execution timestamp, environment, row counts | Re-executing the query |
| **E3** | **Timed observation** | Sample size, sampling method, observer, individual times, distribution — **not just a mean** | Repeating the observation |
| **E4** | **Signed record** | Named signatory, role, date, the statement being signed | — |
| **E5** | **Test report** | Tool and version, scope, environment, pass/fail per case, defects raised, coverage | Re-running the suite |
| **E6** | **Independent review opinion** | Reviewer, **independence statement**, method, scope, findings, opinion | — |
| **E7** | **Reconciliation** | Control totals both sides, variance, tolerance, explanation of every item outside tolerance, sign-off | Re-running the reconciliation |
| **E8** | **Third-party confirmation** | Counterparty, contact, reference, date, the statement confirmed | Contacting the counterparty |

### 4.2 Evidence class by criterion type

| Criterion phrased as… | Required class | Why |
|---|:--:|---|
| "X operates / is demonstrated end to end" | **E1** | Behaviour must be seen, not reported |
| "X% / ≤ N / ≥ N" against a system-measurable quantity | **E2** | A percentage with no query behind it is an opinion |
| "in under N minutes/seconds by staff" | **E3** | A human-performance target needs a sample and a distribution |
| "signed off / accepted by" | **E4** | Named accountability |
| "zero critical or high findings" | **E5 + E6** | A test report **and** a reviewer independent of the builder |
| "migrated and reconciled" | **E7** | Control totals, not a row count |
| "accepted by NBR / the bank / the brand" | **E8** | Only the counterparty can confirm acceptance |
| "documentation delivered" | **E4 + E2** | A register listing the artefacts, and a signature accepting them |

### 4.3 Evidence rules

| Rule | Provision |
|---|---|
| `GA-02` | **Evidence is produced in the environment the criterion names.** Evidence from `dev` does not discharge a production criterion |
| `GA-03` | **Evidence is dated within the gate window** — T−6 weeks to T−0. Evidence older than the window is re-taken |
| `GA-04` | **A percentage carries its denominator.** Audit `TS-01` records that coverage has three denominators, so no coverage percentage may be quoted without stating which |
| `GA-05` | **A sample carries its size and method.** `G1-03` requires 20 samples; the method is stated in `06-02` and must be repeated |
| `GA-06` | **Negative evidence is evidence.** "Zero defects found" requires the test scope; zero findings from a test that did not run is not zero findings |
| `GA-07` | The evidence pack is **assembled progressively** from T−6 weeks and reviewed at T−2. A pack assembled in the final week is a pack nobody has checked |
| `GA-08` | Evidence is retained for the programme's life plus the statutory retention period (minimum 5 years under the PDPA 2026) and is a configuration item under `GV-011` |

---

## 5. Assessment

### 5.1 Who assesses what

| Dimension | Assessor | Independence requirement |
|---|---|---|
| D1 Functional | Named business owner, supported by QA Lead | The business owner must not report to the Programme Director |
| D2 Technical | Solution Architect | **Must not have built the component being assessed** |
| D3 Data | Data owner; CFO for financial data | CFO sign-off on financial migration is non-delegable |
| D4 Security & privacy | Security Lead + Data Protection Forum | Penetration and vulnerability findings require **E6** — a reviewer independent of the builder |
| D5 Operational | Service Manager | Must be the person who will run it, not the person who built it |
| D6 People | Change lead + HR Director | — |
| **Overall gate opinion** | **Programme Director**, presenting to the Steering Committee | The Programme Director presents; **the Steering Committee decides** |

### 5.2 The independence problem this handbook inherits

`AUDIT-019` recorded a critical finding *"against the auditor's own authoring"*; `PGD-AUDIT-001`
§12 declares itself *"Not independent"*. Four repository audits and nineteen category audits have
been produced by the function that authored the material.

> **Rule `GA-09`.** From **Gate 4**, at least one dimension per gate is assessed by a reviewer
> independent of the delivery organisation, and the Audit Committee confirms that reviewer's
> independence (`GV-002` §5.2 row 30). Before Gate 4, independence is provided by the
> **cross-assessment rule**: no person assesses a criterion for a component they built or managed.

### 5.3 Roles that do not exist yet

Stated because a handbook that assigns work to vacant roles is not operable:

| Assessor role | Status | Consequence |
|---|---|---|
| Solution Architect | Loaded at 1.0 FTE from W1 in `06-01` §4 | Assumed available |
| Security Lead | **Not in `06-01` §4 at any wave** | `G1-09` (zero critical/high security findings) has **no assessor**. `GV-007` §8.3 lists it as a hire with a 12–20 week lead |
| Service Manager | Not in `06-01` §4 | D5 has no assessor. `AUDIT-017`: *"operational content and no operational capability"* |
| **Accessibility reviewer** | **Explicitly absent** — `TS-016` cannot be executed | `QA-008` accessibility conformance cannot be gated |
| Data Protection Forum | Constituted by `GV-002` §4.8; not yet convened | D4 privacy has no assessor until Week 3 |

---

## 6. The Gate Process

### 6.1 Timeline

```
T−6 wk   Gate notice issued. Evidence pack opened. Entry criteria checked (§9.3).
         Any criterion whose evidence cannot be produced is raised NOW, not at T−0.
T−4 wk   UAT window opens. Super-users released per DEP-06.
T−3 wk   Security and privacy assessment. Independent review commissioned (Gate 4+).
T−2 wk   Evidence pack review by the PMO. Gaps become remediation items with owners.
T−1 wk   Dry-run assessment. Each dimension assessor issues a provisional opinion.
T−3 d    Gate report circulated to the Steering Committee — RULE GA-10: 3 working days minimum.
T−0      GATE. Steering Committee decides: PASS · CONDITIONAL PASS · FAIL.
T+2 d    Decision written to GV-003 with a D-nnn identifier.
T+2 wk   Hypercare begins (4 weeks per 06-01 §5). Benefits become claimable.
```

### 6.2 The gate report

| Section | Content |
|---|---|
| 1 | Criterion-by-criterion result: **Met · Not met · Met with deviation**, with the evidence reference |
| 2 | Dimension opinions from all six assessors |
| 3 | Open defects by severity, against the `QA-010` thresholds — **⛔ `QA-010` does not exist; see §9.3** |
| 4 | Open audit findings and their ageing |
| 5 | Risk position: any Critical risk that materialised in the wave |
| 6 | Scope variance against the locked wave scope (`GV-006` §6.3) |
| 7 | Cost and earned value: CPI, SPI, EAC (`GV-008` §8.2) |
| 8 | Benefit position: which KPIs moved, against which baselines |
| 9 | Programme Director's recommendation |
| 10 | *(Gate 4 onward)* Independent assurance opinion |

### 6.3 Outcomes and consequences

| Outcome | Definition | Consequence |
|---|---|---|
| **PASS** | **All** criteria met, with evidence | Next wave scope locked and funded. Benefits claimable. Hypercare begins |
| **CONDITIONAL PASS** | All **P0-classified** criteria met; one or more others met with a **dated remediation plan and a named owner** | Next wave starts. **Funding released at 80%**, balance on remediation closure. Remediation items are tracked as `ISS-nnn` in `GV-005` with weekly ageing. **A second consecutive conditional pass on the same criterion is a FAIL** |
| **FAIL** | Any P0 criterion not met, or a conditional pass with no credible remediation plan | **Next wave does not start.** The Steering Committee chooses: extend the wave · descope and re-gate · escalate to the Board. Development **does not run ahead into unaccepted work** (`06-01` §9) |

> **Which criteria are P0?** `06-02` does not classify them. This handbook classifies as **P0**:
> every criterion in dimension **D4** (security and privacy), every criterion containing the word
> *zero*, every statutory criterion, and every criterion the wave's successors technically depend
> on. All others are P1. The classification is shown per gate in §7 and §8.

### 6.4 Signature

Per ISO 9001:2015 §8.6, release requires traceability to the authorising person.

| Signature | Signs for |
|---|---|
| Six dimension assessors | Their dimension's opinion |
| Programme Director | The completeness of the evidence pack |
| **CEO, as Steering Committee chair** | The Go/No-Go decision |
| Audit Committee chair *(Gate 4+)* | That independent assurance was obtained and its findings considered |

---

## 7. Gate 1 — Foundation, Month 4

The gate closest in time, stated in full so the standard is unambiguous.

| # | Criterion (`06-02` §4) | Dim | Evidence | Assessor | P |
|---|---|:--:|:--:|---|:--:|
| `G1-01` | Service orders created from all live channels at pilot sites | D1 | **E1** + **E2** transaction log | Business owner (M01) | P1 |
| `G1-02` | Full service order lifecycle operating end to end | D1 | **E1** | Business owner (M01) | **P0** — successors depend on it |
| `G1-03` | Walk-in intake completed **in under 3 minutes** by branch staff | D1 | **E3**, 20 samples, distribution stated | Business owner (M04) | P1 — **see §9.4** |
| `G1-04` | SLA clocks and escalations firing correctly | D1 | **E5** | QA Lead | **P0** |
| `G1-05` | Customer and device data migrated and reconciled | D3 | **E7** control totals + **E4** signed reconciliation | Data owner | **P0** — **at risk: all 48 sources unprofiled (`ISS-006`)** |
| `G1-06` | Single sign-on and role framework operating for all delivered roles | D4 | **E5** security test report | Security Lead | **P0** |
| `G1-07` | Audit trail complete for all delivered objects | D4 | **E2** sample extract + **E5** | Security Lead | **P0** — ISO 9001 and PDPA evidence |
| `G1-08` | 100% Bengali translation on delivered screens | D1 | **E2** translation coverage report | Localisation Lead | **P0** — `CON-05` |
| `G1-09` | **Zero critical or high security findings** | D4 | **E5** + **E6** independent review | Security Lead + independent reviewer | **P0** — **no Security Lead is staffed (§5.3)** |
| `G1-10` | Performance targets met for delivered screens | D2 | **E5** load test report | Solution Architect | P1 |
| `G1-11` | UAT signed off by named super-users | D1 | **E4** signed UAT record | Business owner | **P0** — **no super-user has been named (`GV-007` §7.5)** |
| `G1-12` | Runbooks and training materials delivered | D5, D6 | **E4** + **E2** document register | Service Manager + Change lead | P1 |
| **+ standing criteria** | §9.1 — 10 additional | D4, D5, D6 | Per §9.1 | Per §9.1 | mixed |

**Gate 1 readiness assessment, at 2026-08-18 02:06:**

| Criterion | Blocker | Source |
|---|---|---|
| `G1-05` | All 48 legacy sources unprofiled; `MG-002` ⛔ | `ISS-006`, `AUDIT-011` |
| `G1-06`, `G1-09` | No Security Lead staffed; `SC-001`–`SC-004` all ⛔ | §5.3; `GV-007` §8.3 |
| `G1-11` | No super-user named; `D-002` open | `GV-007` §7.5 |
| `G1-08` | 48 `MD-*` master data files and the Bengali bundles are unbudgeted | `AF-09` |
| `G1-12` | `OP-007`…`OP-011` runbooks written against infrastructure that is not designed | `SV-003` |

> **Five of twelve Gate 1 criteria have a named blocker today, and four of those five are P0.**
> Wave 1 ends at Month 4. Every blocker above is a Tranche 0 item in `GV-008` §5.1.

---

## 8. Gates 2 – 9

Criteria are `06-02` §4's, with evidence class, assessor and priority assigned.

### 8.1 Gate 2 — Field Operations, Month 8

| # | Criterion | Dim | Evidence | Assessor | P |
|---|---|:--:|:--:|---|:--:|
| `G2-01` | Technician app in daily use by 100% of Dhaka technicians | D6 | **E2** usage report | Change lead | **P0** — `RSK-008` |
| `G2-02` | 24-hour offline operation with **zero** data loss | D2 | **E5** scripted conflict test | Solution Architect | **P0** — `CON-07` |
| `G2-03` | Sync completing within 30 s on 3G after 24 h offline | D2 | **E3** + **E5** | Solution Architect | P1 |
| `G2-04` | Route optimisation reducing measured travel time ≥ 15% | D1 | **E2**, baseline stated | Business owner (M02) | P1 |
| `G2-05` | GPS tracking and customer tracking page live | D1 | **E1** | Business owner (M02) | P1 |
| `G2-06` | Inventory accuracy ≥ 95% at migrated locations, verified by count | D3 | **E7** physical count reconciliation | Data owner | **P0** |
| `G2-07` | Van stock reconciling daily, variance < 2% | D3 | **E7** | Inventory Manager | P1 |
| `G2-08` | Online booking rate ≥ 60% at pilot sites | D1 | **E2** | Business owner (P01) | P1 |
| `G2-09` | Paper service forms withdrawn in Dhaka | D6 | **E4** + **E1** | Change lead | P1 |
| `G2-10` | Privilege benefits applying automatically and correctly | D1 | **E5** | Business owner (M10) | P1 |

### 8.2 Gate 3 — Money & Movement, Month 13

| # | Criterion | Dim | Evidence | Assessor | P |
|---|---|:--:|:--:|---|:--:|
| `G3-01` | 100% of invoices generated automatically from closed jobs | D1 | **E2** | CFO | **P0** |
| `G3-02` | Payment auto-matching ≥ 90% | D1 | **E2** | CFO | P1 |
| `G3-03` | bKash, Nagad and card payments live and reconciling | D1 | **E1** + **E7** | CFO | **P0** |
| `G3-04` | Mushak invoices accepted with **zero** NBR exceptions | D1 | **E8** NBR confirmation | CFO | **P0** — statutory; `CON-04` |
| `G3-05` | First full month-end closed within 5 days | D1 | **E4** + **E2** | CFO | **P0** |
| `G3-06` | Three-way matching blocking unmatched vendor invoices | D1 | **E5** | Business owner (M16) | P1 |
| `G3-07` | Pick & drop with unbroken chain of custody, **zero** exceptions | D1 | **E2** | Business owner (M03) | **P0** |
| `G3-08` | Financial history migrated and reconciled to the trial balance | D3 | **E7** + **E4** CFO sign-off | **CFO — non-delegable** | **P0** |
| `G3-09` | Branch cash reconciling daily across all live branches | D3 | **E7** | CFO | P1 |

### 8.3 Gate 4 — Agreements & Contact, Month 18 · **v1.0 scope complete**

The tranche boundary. Waves 5–9 are re-authorised here (`D-017`, `GV-008` §5.3).

| # | Criterion | Dim | Evidence | Assessor | P |
|---|---|:--:|:--:|---|:--:|
| `G4-01` | Warranty claims auto-created within 24 h and submitted within 72 h | D1 | **E2** | Finance Director | **P0** — largest benefit line |
| `G4-02` | First-submission approval rate ≥ 90% | D1 | **E2** + **E8** brand confirmation | Finance Director | P1 |
| `G4-03` | Contract engine operating all live product families | D1 | **E1** | Business owner (M08) | P1 |
| `G4-04` | Preventive maintenance work generating automatically on schedule | D1 | **E2** | Business owner (M08) | P1 |
| `G4-05` | 10+ corporate clients transacting on the B2B portal | D1 | **E2** | CCO | P1 |
| `G4-06` | Hotline conversations captured in the system of record | D1 | **E2** | Business owner (M27) | P1 |
| `G4-07` | AI assistant resolving ≥ 40% of first contacts | D1 | **E2** | Business owner (M27) | P1 |
| `G4-08` | Consolidated B2B invoicing operating correctly | D1 | **E5** | CFO | P1 |
| `G4-09` | Executive and branch dashboards in weekly management use | D6 | **E2** | CTO | P1 |
| `G4-10` | **Every v1.0 BRD requirement demonstrated as delivered or formally superseded** | D1 | **E2** traceability report from `RQ-004` + **E4** | Business owner + Audit Cttee | **P0** — **`RQ-004` ⛔; this criterion is currently unmeasurable** |
| **+ `G4-11`** *(new)* | **PDPA 2026 compliance demonstrated: DPIA complete, lawful basis recorded per purpose, breach notification procedure tested** | D4 | **E4** + **E6** | Data Protection Forum + independent reviewer | **P0** — **enforcement activates ~13 May 2027, inside this wave** |
| **+ `G4-12`** *(new)* | **Independent assurance opinion obtained** | — | **E6** | Audit Committee | **P0** — `GV-001` `CC-08` |

### 8.4 Gates 5 – 9

| Gate | # | Criterion | Dim | Evidence | Assessor | P |
|:--:|---|---|:--:|:--:|---|:--:|
| **G5** | `G5-01` | First payroll run processed, validated and paid with **zero** errors | D1 | **E7** + **E4** | HR Director + CFO | **P0** |
| | `G5-02` | BEFTN file accepted by the bank without rework | D1 | **E8** | CFO | **P0** |
| | `G5-03` | **Zero** uncertified technicians assignable to brand warranty work | D1 | **E5** | Quality Manager | **P0** |
| | `G5-04` | ISO 9001 internal audit executed entirely in the system | D1 | **E1** + **E4** | Quality Manager | **P0** — `CON-11` |
| | `G5-05` | First MSP clients live with monitored estates and SLA reporting | D1 | **E1** | Corporate Services Head | P1 |
| | `G5-06` | All 51+ service centres operating on the platform | D6 | **E2** | Change lead | P1 |
| | `G5-07` | Attendance capture ≥ 98% complete across all branches | D1 | **E2** | HR Director | P1 |
| **G6** | `G6-01` | Rental transacting with full condition, deposit and damage control | D1 | **E1** | Corporate Services Head | P1 |
| | `G6-02` | **Zero** refurbished units released without a data destruction certificate | D1 | **E2** | Quality Manager | **P0** — `H-01`, NIST SP 800-88r2 |
| | `G6-03` | Data-services chain of custody with **zero** exceptions | D4 | **E2** | Security Lead | **P0** |
| | `G6-04` | Automatic dispatch assignment ≥ 50% with ≥ 88% dispatcher agreement | D1 | **E2** | Ops Director | P1 |
| | `G6-05` | Parts demand forecast accuracy within target | D1 | **E2** | Inventory Manager | P1 |
| | `G6-06` | Customer native mobile apps published and adopted | D6 | **E2** | Change lead | P1 |
| **G7** | `G7-01` | 200+ approved sellers transacting | D1 | **E2** | CCO | P1 |
| | `G7-02` | Payout accuracy 100% with **zero** unexplained variance | D1 | **E7** | CFO | **P0** — **`M53` settlement is in no wave (`GV-004` §5.6)** |
| | `G7-03` | Marketplace jobs meeting the same quality and evidence standards as owned jobs | D1 | **E2** + **E5** | Quality Manager | **P0** — `RSK-023` |
| | `G7-04` | Dispute rate below target, all disputes resolved within SLA | D1 | **E2** | CCO | P1 |
| | `G7-05` | VAT treatment validated by external tax advice | D4 | **E6** | CFO | **P0** — `RSK-022`, `DEP-29` |
| | `G7-06` | Dynamic pricing within guard rails with a complete decision audit | D1 | **E2** | CCO | P1 |
| **G8** | `G8-01` | All management reporting served from the warehouse; **zero** manual packs | D1 | **E2** | CTO | P1 |
| | `G8-02` | Predictive maintenance precision ≥ 70% on the pilot estate | D1 | **E2** | CTO | P1 |
| | `G8-03` | Overall automation of routine operational work ≥ 85% | D1 | **E2**, denominator stated | Ops Director | P1 |
| | `G8-04` | E-waste chain fully certified with **zero** uncertified disposals | D1 | **E8** + **E2** | Quality Manager | **P0** — regulatory |
| | `G8-05` | Every production model has a current model card and drift monitoring | D2 | **E2** | Solution Architect | P1 |
| **G9** | `G9-01` | A test entity in a second country stood up in ≤ 12 weeks using configuration only | D2 | **E1** + **E3** | Solution Architect | P1 |
| | `G9-02` | Consolidated multi-entity reporting validated | D1 | **E7** | CFO | P1 |
| | `G9-03` | Full-scale load test passed at 1.5× projected peak | D2 | **E5** | Solution Architect | **P0** |
| | `G9-04` | All programme documentation handed over and accepted | D5 | **E4** + **E2** | Service Manager | **P0** |
| | `G9-05` | Support model transitioned to steady state | D5 | **E4** | Service Manager | **P0** |

---

## 9. Standing Criteria, Entry Criteria and Conflicts

### 9.1 Standing criteria — applied at **every** gate

**Eleven** criteria that `06-02` does not carry. They cover dimensions D4, D5 and D6, which
`06-02` addresses only at `G1-09`.

> **Identifier note.** These carry the prefix `SG-` (Standing Gate criterion), **not** `SC-`.
> `SC` is the category code for Security, Privacy & Compliance in `PGD-000`, and `SOD-`/`SC-`
> confusion is the exact defect class behind `PGD-A1-01` and `PGD-A1-06`. The first draft of this
> handbook used `SC-G*` and was corrected before issue.

| # | Standing criterion | Dim | Evidence | P |
|---|---|:--:|:--:|:--:|
| `SG-1` | Zero **open** critical or high security findings from the wave's scope | D4 | **E5** + **E6** | **P0** |
| `SG-2` | Every new processing purpose has a recorded lawful basis; DPIA updated | D4 | **E4** | **P0** from W2 |
| `SG-3` | No production personal data in a non-production environment without masking and a lawful basis | D4 | **E2** | **P0** — `CON-14` |
| `SG-4` | Runbooks exist, are current, and have been **rehearsed** — not merely written | D5 | **E1** + **E4** | **P0** |
| `SG-5` | On-call rota staffed and paging tested end to end | D5 | **E1** | **P0** — `OP-06`: *"no paging platform at all"* |
| `SG-6` | Backup taken and **restore tested** in the wave's scope | D5 | **E5** | **P0** — `KPI-091` |
| `SG-7` | Training delivered before access granted; completion ≥ 95% | D6 | **E2** | P1 |
| `SG-8` | Every delivered artefact is under configuration control with a version and an approver | D5 | **E2** | P1 — `GV-011` |
| `SG-9` | Open audit findings from prior gates are closed, or re-accepted with a dated plan | — | **E4** | **P0** |
| `SG-10` | Regulatory citations re-verified; `RR-005` currency register updated | D4 | **E4** | **P0** — `PG-M4`; closes `C-04`/`H-01` recurrence |
| `SG-11` | **Every numeric gate criterion reconciles to its registered KPI's target for that wave, or states explicitly why it is more demanding** | D1 | **E2** | P1 — §9.4; `PGD-A2-12` |

### 9.2 Entry criteria — checked at **T−6 weeks**, not at the gate

> **Rule `GA-11` — a gate that discovers at T−0 that its evidence cannot be produced has already
> failed.** These are checked six weeks out, when there is still time.

| # | Entry criterion | Why |
|---|---|---|
| `EN-01` | Every gate criterion has a named evidence owner | Otherwise the pack has gaps nobody owns |
| `EN-02` | Every assessor role in §5.1 is filled | §5.3 lists four that are not |
| `EN-03` | **Every test pack the gate depends on exists and is executable** | `TS-02`: nine test files are consumed a wave before they exist; four cannot be executed at all |
| `EN-04` | Super-users are named and released for the UAT window | `DEP-06`; `RSK-001` |
| `EN-05` | The wave's scope was locked at wave start and the locked scope is on record | `GV-006` §6.3; it is the variance denominator |
| `EN-06` | Environments exist at the class the criteria require | `GA-02`; `PE-002` ⛔ — the `dr` environment is *"named in the architecture and sized nowhere"* |
| `EN-07` | Independent reviewer engaged *(Gate 4+)* | `GA-09` |

### 9.3 The threshold that does not exist

`QA-010` (Defect Management & Quality Gate Standard) is ◐ in `PGD-000`: `TS-018` defines a defect
taxonomy and forms, but *"the gate — how many open Sev-2s block go-live — is undefined."*

> **Interim rule `GA-12`, applying until `QA-010` is issued:** a gate may not be passed with **any
> open Sev-1**, or with **more than five open Sev-2 defects** in the wave's scope, or with any open
> Sev-2 that affects a P0 criterion. This is a placeholder set by this handbook because a gate with
> no defect threshold has no floor at all. **`QA-010` supersedes it and should not simply adopt
> it** — the numbers here are conventional, not derived.

### 9.4 A gate criterion that contradicts the KPI register — `PGD-A2-12`

| Source | Statement |
|---|---|
| `06-02` §4 `G1-03` | *"Walk-in intake completed in **under 3 minutes** by branch staff"* — **Gate 1, Month 4** |
| `06-01` §3 Wave 1 | *"Walk-in intake in under 3 minutes, demonstrated by branch staff"* |
| `06-02` §2.1 `KPI-010` | Walk-in intake time — baseline **~10 min** · **W4 target < 4 min** · **W8 target < 3 min** |

> **The Wave 1 gate requires a performance standard the KPI register does not expect until Wave 8**
> — Month 34, thirty months later — and which exceeds the register's own Wave 4 target.
>
> One of the two is wrong. Either `G1-03` should read *"under 4 minutes"*, aligning Gate 1 with the
> nearest KPI milestone, or `KPI-010`'s trajectory is too conservative. **This handbook does not
> resolve it**, because the resolution is a business owner's call about what is achievable at
> Month 4 with newly trained counter staff. It is raised as `PGD-A2-12` and routed to the `M04`
> business owner via `GV-005`.
>
> **The general control** is `SG-11`, added here: *every numeric gate criterion must reconcile to
> a registered KPI's target for that wave, or state explicitly why it is more demanding.* Applying
> that control across all 70 criteria is a Wave 1 task for the PMO.

---

## 10. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-009-D-01` | Which criteria set is authoritative | `06-01` · `06-02` · Merge | **`06-02` §4** | It is identified, numbered and carries an evidence column. `06-01`'s bullets are narrative | `PGD-A2-11` closed; `06-01` §3 must point at `06-02` §4 |
| `GV-009-D-02` | Whether to add criteria `06-02` does not have | Assess only what exists · Add standing criteria | **Add 10 standing criteria** | `06-02` covers D1 and D2 well and D4/D5/D6 barely. A wave can currently pass with no rehearsed runbook, no paging and no DPIA | Gate scope grows by 10 per gate; `AUDIT-017`'s finding gets a control |
| `GV-009-D-03` | Whether to set a defect threshold before `QA-010` | Wait · Set an interim | **Set an interim (`GA-12`)** | A gate with no defect floor has no floor | An explicitly conventional number, flagged for supersession |
| `GV-009-D-04` | How to handle the `G1-03` conflict | Silently align to 4 min · Silently keep 3 min · Raise it | **Raise it; do not resolve it** | The resolution is a business judgement about achievability, not a documentation fix | `PGD-A2-12`; control `SG-11` |
| `GV-009-D-05` | Whether Conditional Pass releases full funding | Full · Partial | **80%, balance on remediation closure** | A conditional pass with full funding is a pass. The 20% is the only mechanism that makes remediation happen | `GV-008` §5.3 |
| `GV-009-D-06` | When independent assurance becomes mandatory | Every gate · From Gate 4 · Never | **From Gate 4** | Gate 4 is the tranche boundary and the v1.0 completion point; it is where the Board re-authorises. Every gate would be disproportionate before then | `GA-09`; `G4-12`; `GV-001` `CC-08` |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Is `G1-03`'s 3 minutes or `KPI-010`'s 4 minutes correct for Month 4? | Business owner (M04) | W1 − 6 wk | `PGD-A2-12`; Gate 1 |
| `Q-02` | Who is the Security Lead who assesses `G1-06`, `G1-09` and `SG-1`? The role is in no wave of `06-01` §4 | CTO | **Week 4** | Four P0 criteria at Gate 1 |
| `Q-03` | Who is the Service Manager who assesses dimension D5? | CTO | Week 6 | `SG-4`–`SG-6`; `G9-04`, `G9-05` |
| `Q-04` | Can `G4-10` be assessed at all without `RQ-004`? It requires a traceability report from a matrix that does not exist | Enterprise Architecture | W4 − 6 mo | The v1.0 completion criterion, and the tranche boundary |
| `Q-05` | Does `G7-02` (payout accuracy) test `M53`, which `GV-004` §5.6 shows is in no wave? | ARB | Before W7 planning | `D-019`, `D-020` |
| `Q-06` | Do the remaining 69 numeric criteria reconcile to their KPI targets? `SG-11` requires the check; only `G1-03` has been tested | PMO | W1 | The credibility of every numeric gate criterion |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every gate criterion has an evidence class | §7, §8 — 70 of 70 |
| `AC-02` | Every gate criterion has a named assessor role | §7, §8 |
| `AC-03` | Every gate criterion is classified P0 or P1 | §6.3 rule; §7, §8 |
| `AC-04` | The evidence standard is defined, with reproducibility per class | §4.1 — eight classes |
| `AC-05` | The consequence of each outcome is stated | §6.3 |
| `AC-06` | Entry criteria are checked before the gate window closes | §9.2 — seven, at T−6 weeks |
| `AC-07` | Assessor roles that do not exist are named | §5.3 — four |
| `AC-08` | The two competing criteria sets are reconciled with a ruling | §3.1; `PGD-A2-11` |
| `AC-09` | Conflicts between gate criteria and the KPI register are surfaced | §9.4; `PGD-A2-12`; control `SG-11` |
| `AC-10` | Gate 1 readiness is assessed against today's position | §7 readiness table — five blockers |

**Definition of done.** Complete when every criterion is met, `06-01` §3 carries a pointer to
`06-02` §4, the four vacant assessor roles are filled, `QA-010` supersedes `GA-12`, `SG-11` has
been applied to all 70 criteria, and `PGD-000` records `GV-009` as ✅ with a fresh enumeration
timestamp.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-001`](GV-001_Programme_Charter_and_Mandate.md) §8 | Tolerance; the tranche boundary at Gate 4 |
| Upstream | [`GV-002`](GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) §5.2 | Wave Go/No-Go authority |
| Upstream | [`GV-004`](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) §6.1 | Places the nine gates in time |
| Downstream | [`GV-008`](GV-008_Programme_Budget_and_Cost_Baseline.md) §5.3 | Gate result releases funding |
| Downstream | [`GV-005`](GV-005_RAID_Register.md) | Conditional-pass remediation items become `ISS-nnn` |
| Downstream | `QA-001`, `QA-009`, `QA-010` | Supply test, UAT and defect evidence; `QA-010` supersedes `GA-12` |
| Downstream | `RL-003` | Go-live readiness assessment inherits this evidence model at release level |
| Downstream | `BM-004` | Benefits become claimable on a gate pass |
| Downstream | `GV-011` | Gate evidence packs are configuration items (`GA-08`) |
| Lateral | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` §4 | The authoritative criteria set |
| Lateral | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` §3, §5, §9 | The narrative set, subordinated here |

---

## 14. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) ·
[`GV-004`](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) · [`GV-008`](GV-008_Programme_Budget_and_Cost_Baseline.md)

**Workspace**
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` §2, §4 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` §3, §5, §9 ·
`../../project_content/_AUDIT/AUDIT-014` `TS-01`, `TS-02`, `AUDIT-017` `OP-04`, `OP-06`

**External standards** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| ISO 21502:2020 §6.4 — gates and decision points | §3, §6 |
| PRINCE2 7th Edition (2023) — stage boundaries; End Stage Assessment; Exception Plan | §6 |
| PMBOK Guide 7th Edition — *Measurement* and *Delivery* performance domains | §4 |
| UK IPA / OGC Gateway Review — independent panel review at prescribed points; delivery confidence | §5.2, `GA-09` |
| ISO 9001:2015 §8.6 — release of products; traceability to the authorising person | §6.4 |
| Bangladesh PDPA 2026 — enforcement ~13 May 2027, inside Wave 4 | `G4-11`, `SG-2` |
| NIST SP 800-88r2 / IEEE 2883 | `G6-02` |

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Programme Management Office | Initial issue. Establishes eight evidence classes, six readiness dimensions, named assessors, three gate outcomes with defined consequences, seven entry criteria and eleven standing criteria. Rules `06-02` §4 authoritative over `06-01` §3 (`PGD-A2-11`). Raises `PGD-A2-12`: `G1-03` demands at Month 4 a standard `KPI-010` does not target until Month 34. Assesses Gate 1 as having five blockers today, four of them P0 | *pending Steering Committee* |

---

*`GV-009` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
