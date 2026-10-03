---
id: GV-005
title: RAID Register — Risks, Assumptions, Issues & Dependencies
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL — LIVE INSTRUMENT
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Management Office
approver: ERP Steering Committee
standards_basis: ISO 31000:2018 · ISO Guide 73:2009 vocabulary · ISO 21502:2020 §7.8 risk · PMBOK Guide 7th Edition (Uncertainty performance domain) · PRINCE2 7th Edition (2023) risk practice
traces_to: PGD-000 GV-005 · 00-04 §1 §2 §3 §4 · audit findings C-04 (PDPA penalty exposure), M-09, AF-08, AF-09, PGD-A1-05
depends_on: GV-001, GV-002, GV-003
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
review_cycle: Critical monthly · High per wave gate · Medium quarterly
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-005 — RAID Register
# Risks · Assumptions · Issues · Dependencies

### Category 00 · Code `GV` · ISO 31000:2018 · PRINCE2 7 · PMBOK 7

---

> **This is a live instrument, not a narrative.** `00-04` is an excellent point-in-time analysis
> written on 2026-08-12 and never updated. A risk register that is not updated is a document about
> the past. This register carries owners, dates, triggers, treatment status and a review cadence,
> and it is re-baselined at every wave gate.

> **Correction on issue.** `PGD-000`'s `GV-005` row states that *"the PDPA 2026 penalty exposure
> (BDT 25–50 lakh) identified by audit `C-04` is still not in it."* That is **incorrect**: `00-04`
> §1.4a `RSK-032` carries the exposure explicitly. The register row is stale. Recorded as finding
> `PGD-A2-06` and corrected in `PGD-000` at this issue. An audit that reports a closed gap as open
> is as damaging to trust as one that misses an open gap.

---

## 1. Purpose

This register holds every uncertainty the programme is carrying: what might go wrong (**risks**),
what is being taken on trust (**assumptions**), what has already gone wrong (**issues**), and what
the programme needs from someone else (**dependencies**).

It exists because `00-04` — which is where all four currently live — is a *narrative*. It has no
review dates, no trigger conditions, no treatment status, no ageing, and no mechanism by which an
assumption that fails becomes an issue. Three of the four registers have not been touched since
2026-08-12; in that time, three audits raised 45 findings, of which more than twenty are
uncertainties this register should have been carrying.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The scoring scheme, its definitions, and the escalation thresholds |
| 2 | **Risks** — 36 carried from `00-04` §1, 8 raised by Category 00 authoring |
| 3 | **Assumptions** — 22 carried from `00-04` §2, with validation owners and expiry |
| 4 | **Issues** — 12, newly registered. `00-04` has no issue register at all |
| 5 | **Dependencies** — 35 carried from `00-04` §3, with lead time and criticality |
| 6 | The **corrected risk heat summary** — `00-04` §1.5 is wrong on all three counts |
| 7 | Review cadence, ageing, and the assumption→issue and risk→issue transitions |
| 8 | The relationship to constraints (`GV-001` §9.1) and to decisions (`GV-003`) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **Constraints** `CON-01`…`CON-14` | `GV-001` §9.1 | A constraint is a limit the Board has accepted; it is not an uncertainty and cannot be "treated" |
| Decisions | `GV-003` | An open decision is not a risk. *The consequence of not taking it* is, and that is registered here |
| Defects | `QA-010` | A defect is a quality event with its own severity model |
| Live incidents | `SV-006` | An incident is an operational event. A pattern of incidents is a risk and comes here |
| Security threats per component | `SC-002` STRIDE threat model | Threat modelling is systematic per-component enumeration; this register carries the programme-level residue |
| Content risks | `CG-013` | Workstream 5 keeps its own escalation rules; material items are promoted here |

### 1.2 Intended audience

| Audience | What they use this register for |
|---|---|
| **Board** | The 12 Critical risks (§4.2). Critical risk acceptance is a Board decision (`GV-002` §5.2 row 4) |
| **Steering Committee** | The monthly review; High risk acceptance; the issue ageing report |
| **PMO** | The operating instrument. The PMO is the custodian |
| **Risk owners** | Their own entries, their triggers, and their reporting obligation |
| **Auditors** | Whether the programme's stated uncertainties match its measured ones |

---

## 2. Basis and Method

### 2.1 Standards conformance

| Standard | Concept | How this register conforms | Departure |
|---|---|---|---|
| **ISO 31000:2018** | Principles, framework, process — identify, analyse, evaluate, treat, monitor, communicate | §3 scoring; §4–§7 the four registers; §8 monitoring and review | ISO 31000 is guidance, not certifiable. Adopted as the structuring discipline |
| **ISO Guide 73:2009** | Risk vocabulary — *risk*, *likelihood*, *consequence*, *risk owner*, *risk treatment*, *residual risk* | Terms used as defined. **"Mitigation" is used for treatment because `00-04` uses it and eleven downstream documents cite it** | Vocabulary continuity preferred over strict conformance |
| **ISO 21502:2020** §7.8 | Risk management within a project | Owner per risk; escalation by rating | None |
| **PMBOK Guide 7th Edition** | *Uncertainty* performance domain; risk as both threat and opportunity | §4.6 registers three **opportunities**, which `00-04` does not carry at all | None |
| **PRINCE2 7th Edition (2023)** | Risk practice; the Issue Register; risk budget; *risk actionee* distinct from *risk owner* | §3.4 separates owner (accountable) from actionee (does the treatment) — a distinction `00-04` collapses | None |

### 2.2 What changed from `00-04`

| Change | Reason |
|---|---|
| **Risk heat summary corrected** — 8/22/6, not 5/16/10 | §4.3. `00-04` §1.5 is wrong on Critical, High and Medium, and on the total |
| **Issue register created** — 12 entries | `00-04` has none. Twenty-plus audit findings are live issues with no register |
| **Assumption expiry and validation owner added** | An assumption with no validation date is a risk nobody is watching |
| **Dependency lead time added** | `DEP-31` is on the critical path and its 6–10 week lead was nowhere recorded |
| **Risk actionee separated from risk owner** | Seven risks are owned by the CTO. One person cannot execute seven treatments |
| **Trigger conditions added** | A risk with no trigger is monitored by memory |
| **Opportunities added** | Three. Risk management that records only threats produces defensive programmes |
| **8 new risks** | Raised by Category 00 authoring — §4.4 |

---

## 3. Scoring and Escalation

### 3.1 Likelihood and consequence

| Likelihood | Definition |
|:--:|---|
| **H** | More likely than not on current evidence |
| **M** | Credible; has occurred in comparable programmes |
| **L** | Possible but not expected |

| Consequence | Definition |
|---|---|
| **Critical** | Programme failure, statutory breach, restatement, or a Board-level financial event |
| **High** | A wave gate fails, a benefit is lost, or a material rework cost is incurred |
| **Med** | Absorbed within wave tolerance |
| **Low** | Absorbed within sprint |

### 3.2 Rating matrix

| | **Low** | **Med** | **High** | **Critical** |
|:--:|:--:|:--:|:--:|:--:|
| **H** | Med | High | **Critical** | **Critical** |
| **M** | Low | Med | High | **Critical** |
| **L** | Low | Low | High | High |

### 3.3 Escalation and review by rating

| Rating | Acceptance authority | Review cadence | Reporting |
|---|---|---|---|
| **Critical** | **Board** (`GV-002` §5.2 row 4) | Every Steering Committee meeting | Named owner reports monthly; Board quarterly |
| **High** | Steering Committee | Every wave gate | Owner reports at each gate |
| **Med** | PMO | Quarterly | Register review |
| **Low** | PMO | At wave gate | By exception |

### 3.4 Owner and actionee

| Role | Accountability |
|---|---|
| **Risk owner** | Accountable that the risk is managed. Reports at the cadence in §3.3. Always a named role |
| **Risk actionee** | Performs the treatment. May differ from the owner |
| **Rule `RA-01`** | An owner with more than **five** Critical or High risks is a single point of failure. The CTO currently owns **nine**. Flagged at §4.5 |

### 3.5 Transitions

```
   ASSUMPTION ──── proves false ────► ISSUE        (and often ► RISK on other work)
       │
       └── validation date passes with no evidence ──► RISK

   RISK ──── materialises ────► ISSUE
       │
       └── treated to below Low ──► CLOSED (with the evidence recorded)

   DEPENDENCY ──── missed its needed-by date ────► ISSUE

   ISSUE ──── resolved ────► CLOSED (evidence recorded, never deleted)
```

> **Rule `RA-02` — nothing is deleted.** A closed entry keeps its identifier, its history and its
> closure evidence. `RG-02` / `PG-05` permanence applies to `RSK-`, `ASM-`, `ISS-` and `DEP-`.

---

## 4. Risks

### 4.1 Register structure

Full entries for the twelve Critical risks; carried risks are listed with their rating, owner,
trigger and treatment status. The complete narrative for `RSK-001`–`RSK-036` remains in `00-04`
§1 and is **referenced, not restated** — principle `PG-02`.

### 4.2 Critical risks — the twelve

| ID | Risk | L | C | Owner | Actionee | Trigger to watch | Treatment status |
|---|---|:-:|:-:|---|---|---|---|
| `RSK-001` | Business super-user availability falls short, stalling UAT | **H** | High | CEO | Department heads | Any super-user below 25% availability in a UAT month | ⬜ **Untreated.** `D-002` open since 2026-08-12 |
| `RSK-002` | Scope creep across a 36-month horizon | **H** | High | Steering Cttee | PMO | Any capability added without a `CR-nnn` | ⬜ **Untreated.** The change log is **empty** while scope has tripled twice (`GV-003` §7.2) |
| `RSK-008` | Technician rejection of the mobile application | **H** | **Critical** | Ops Director | Change lead | Field-pilot task completion slower than paper | ⬜ Design mitigations specified; no pilot scheduled |
| `RSK-022` | Marketplace VAT and liability model incorrect | M | **Critical** | CFO | Legal + tax advisor | W7 − 4 months with no external opinion commissioned | ⬜ `D-003`, `DEP-29` open |
| `RSK-023` | Marketplace quality failure damages the brand | M | **Critical** | CCO | Quality Manager | First seller job failing the owned-work QC standard | ⬜ Controls specified in `M12`; not built |
| `RSK-032` | **Non-compliance with the PDPA 2026** — penalties to **BDT 25 lakh**, or **BDT 50 lakh** for a significant data fiduciary; enforcement ~**13 May 2027**, inside Wave 4 | **H** | **Critical** | CFO / CTO | DP Forum | Any processing purpose reaching build with no recorded lawful basis | ⬜ `SC-003` DPIA ⛔; no DPIA exists |
| `RSK-033` | Data residency architecture unlawful | M | **Critical** | CTO / Legal | DP Forum | `DEP-31` legal opinion not received within 4 weeks | ⬜ **On the critical path.** `D-013` open 6 days |
| `RSK-036` | Cost estimate materially understated | **H** | High | CFO | Programme Director | `GV-008` not baselined before the build contract | ⬜ `D-014` escalated 2026-08-13, **unrecorded** |
| **`RSK-037`** | **Wave capacity infeasibility** — Wave 1 demands 217 PW against 40.7 effective build person-weeks (**5.33×**); W2 1.76×; W4 1.32× | **H** | **Critical** | Programme Director | PMO | Charter approval without an option selected from `GV-004` §7.2 | ⬜ **New.** Closes `M-09`; the plan fails its own capacity check |
| **`RSK-038`** | **763 PW across 37 modules has no wave, no team and no date** — 41% of specified build | **H** | **Critical** | Steering Cttee | PMO | `GV-004` baselined without `D-020` | ⬜ **New.** Spare capacity in W5–W9 is 313 PW; shortfall **450 PW** |
| **`RSK-040`** | **The programme has taken no recorded decision in five months.** 24 open, of which `D-013` and `D-014` block Wave 1 | **H** | **Critical** | CEO | PMO | Any decision passing its needed-by date | ⬜ **New.** `GV-003` §5.6: 23 `OPEN`, 1 `ESCALATED`, **0 `DECIDED`** |
| **`RSK-043`** | **127 unwritten guiding documents are in no plan, no budget and no workstream** — including the SRS, the SAD, the schema and the API contracts | **H** | High | Programme Director | Enterprise Architecture | Build contract let before `RQ-001` is baselined | ⬜ **New.** `PGD-A1-05` open; `D-021`; `GV-001` `Q-05` |

### 4.3 The corrected heat summary

Regenerated by counting the Rating column across all six risk tables — `00-04` §1.1, §1.2, §1.3,
§1.4, §1.4a, and §4.4 of this document — immediately before issue, per `PG-M10`.

| Rating | `00-04` §1.5 claims | **Counted, `00-04` only** | **Counted, including this register's 8 new** |
|---|---:|---:|---:|
| **Critical** | 5 | **8** | **12** |
| **High** | 16 | **22** | **26** |
| **Medium** | 10 | **6** | **6** |
| **Total** | **31** | **36** | **44** |

**Working, `00-04` only:**

| Table | Critical | High | Med | Rows |
|---|---:|---:|---:|---:|
| §1.1 Delivery & Programme (`RSK-001`–`007`) | 2 | 5 | 0 | 7 |
| §1.2 Adoption & Change (`RSK-008`–`012`) | 1 | 3 | 1 | 5 |
| §1.3 Technical (`RSK-013`–`021`) | 0 | 8 | 1 | 9 |
| §1.4 Commercial & Regulatory (`RSK-022`–`031`) | 2 | 4 | 4 | 10 |
| §1.4a Data Protection (`RSK-032`–`036`) | 3 | 2 | 0 | 5 |
| **Total** | **8** | **22** | **6** | **36** |

> **`00-04` §1.5 is wrong on all three counts and on the total.** The total of 31 corresponds to
> the register *before* §1.4a was added — but even at 31 rows the split was 5/20/6, not 5/16/10.
> The summary was written before the tables it summarises were finished and never recounted: the
> defect `PGD-A1-02`, `PGD-A1-07` and `PGD-A1-13` each describe, occurring a **fourth** time, in a
> fourth document, in a different repository.
>
> `00-04` §1.5 further asserts *"the five Critical risks — `RSK-001`, `002`, `008`, `022`, `023` —
> are the ones that can end the programme."* **There are eight, and the three it omits are the
> three with statutory or financial consequence**: `RSK-032` (PDPA), `RSK-033` (residency) and
> `RSK-036` (cost understatement). Recorded as finding `PGD-A2-01`.

### 4.4 New risks raised by Category 00 authoring

| ID | Risk | L | C | Rating | Owner | Treatment |
|---|---|:-:|:-:|:--:|---|---|
| `RSK-037` | Wave capacity infeasibility — see §4.2 | H | Critical | **Critical** | Programme Director | Select an option from `GV-004` §7.2 before charter approval |
| `RSK-038` | 763 PW unscheduled — see §4.2 | H | Critical | **Critical** | Steering Cttee | `D-020`; re-plan on `AR-006` |
| `RSK-039` | **298 PW of portal and application build has never appeared in any programme effort figure.** Every published figure (834 / 1,302 / 1,513) is module-only | H | High | **High** | CFO | `D-016`; absorb into `GV-007` and `GV-008` |
| `RSK-040` | Zero recorded decisions in five months — see §4.2 | H | Critical | **Critical** | CEO | `GV-003`; Steering Committee first meeting clears `D-013`, `D-014` |
| `RSK-041` | **Baseline movement during authoring, third occurrence.** `project_content` moved 468 → 477 files between 01:39 and 02:06 on 2026-08-18 | H | Med | **High** | PMO | Ratify `RG-08` (`GV-001` `CC-06`, `D-023`); `PG-M11` |
| `RSK-042` | **Assurance is not independent.** All four repository audits and 19 category audits were produced by the function that authored the material | M | High | **High** | Audit Cttee chair | `GV-010`; `D-022`; `GV-001` `CC-08` |
| `RSK-043` | 127 guiding documents unowned and unestimated — see §4.2 | H | High | **Critical** | Programme Director | `GV-007`; `D-021` |
| `RSK-044` | **The delivery plan schedules module identifiers whose meaning changed.** `M20` and `M30` are ambiguous; `G7-02` tests settlement, which is `M53`, which is in no wave | M | High | **High** | ARB | `D-019`; reconcile `06-01` to the 67-module architecture |

### 4.5 Risk concentration

| Owner | Critical + High risks owned | Assessment |
|---|---:|---|
| **CTO** *(sole or joint)* | **9** | ⚠ Breaches `RA-01`. `RSK-004`, `013`, `016`, `017`, `019`, `020`, `024`, `032`, `033`. Recommend reallocating the technical risks to the Solution Architect as actionee, retaining CTO ownership |
| CEO | 5 | Within threshold |
| CFO | 6 | ⚠ Marginal. `RSK-007`, `022`, `026`, `030`, `032`, `036` |
| Programme Director / Programme Manager | 5 | Within threshold |
| Steering Committee *(as a body)* | 3 | Acceptable — body ownership is appropriate for scope risks |
| Ops Director | 3 | Within threshold |
| Solution Architect | 3 | Within threshold |

### 4.6 Opportunities

`00-04` records no opportunities. PMBOK 7 treats uncertainty as symmetric, and three are material:

| ID | Opportunity | Value if realised | Owner | Exploitation |
|---|---|---|---|---|
| `OPP-01` | **An SRS precedent exists in-house.** The sibling portal programme wrote a 91 KB SRS with API specifications in January 2026 | `RQ-001` — the single most critical missing document — has a proven template and a working author. Could halve the 6–8 week lead on the critical path | Enterprise Architecture | Reuse the structure; reuse the author |
| `OPP-02` | **The content estate is unusually complete before build.** 477 files of master data, copy, SOPs and statutory templates | Very few ERP programmes hold this before build. It de-risks configuration, training and adoption — the three areas where ERP programmes usually fail | Programme Content Lead | Fund workstream 5 rather than discovering it late |
| `OPP-03` | **Waves 6–9 are half empty** — 313 PW of spare effective capacity | Absorbs 41% of the unscheduled `M31`–`M67` work without new hiring, if the sequence permits | Programme Director | Depends on `AR-006`; combine with `GV-004` §7.2 option A |

---

## 5. Assumptions

### 5.1 Rules

| Rule | Provision |
|---|---|
| `AS-01` | Every assumption has a **validation owner** and a **validate-by date** |
| `AS-02` | An assumption that passes its date without evidence **becomes a risk automatically** |
| `AS-03` | An assumption proven false **becomes an issue** and triggers a `CR` against any baseline that rests on it |
| `AS-04` | **Charter-critical** assumptions (`GV-001` §9.2) invalidate the authorisation if false, not merely the plan |

### 5.2 Register

Carried from `00-04` §2. Validation owner and date are **new**; `00-04` records neither.

| ID | Assumption | Validate by | Validation owner | Status | Charter-critical |
|---|---|---|---|:--:|:--:|
| `ASM-01` | All service centres have ≥ 3G during operating hours | W1 | CTO | ⬜ Unvalidated | |
| `ASM-02` | Technicians use Company-issued Android 11+ devices | W2 − 2 mo | Ops Director | ⬜ Blocked by `D-011` | |
| `ASM-03` | Existing customer and device data is exportable at ≥ 80% quality | **W1** | CTO | ⬜ **All 48 sources unprofiled** — `ISS-007` | |
| `ASM-04` | The 17+ brand partnerships continue | W4 | CEO | ⬜ Figure itself unverified (`H2-12`) | |
| `ASM-05` | Bangladesh VAT rates and Mushak format remain broadly stable | Each gate | CFO | ⬜ | |
| `ASM-06` | **Business stakeholders commit the stated time** | Before kickoff | CEO | ⬜ `D-002` open | **✓** |
| `ASM-07` | The portal platform exposes documented, versioned APIs | W1 | CTO | ⬜ `CON-03`; no ICD exists | |
| `ASM-08` | bKash, Nagad and SSLCOMMERZ provide sandbox and production access on schedule | W3 | CFO | ⬜ `DEP-16`–`18` | |
| `ASM-09` | ~~Singapore-region hosting~~ — **superseded by `C-05`**; regional for non-sensitive data only | — | CTO | ⛔ Superseded by `ASM-21` | |
| `ASM-10` | No major organisational restructuring | Each gate | CEO | ⬜ | |
| `ASM-11` | **Odoo 19 remains supported through the programme** | Each gate | CTO | ⬜ Odoo 19.0 released 18 Sep 2025 | **✓** |
| `ASM-12` | OCA critical-path modules complete v19 migration | Before each wave | Solution Architect | ⬜ `RSK-015` | |
| `ASM-13` | Marketplace seller supply exists in target categories | W7 − 6 mo | CCO | ⬜ | |
| `ASM-14` | Corporate demand for managed services at the assumed price | W5 | Corporate Services Head | ⬜ | |
| `ASM-15` | Bengali-capable open-weight language models remain adequate | W6 | CTO | ⬜ | |
| `ASM-16` | Go-live avoids Ramadan and the Eid peaks | Each wave date | Programme Manager | ⬜ **Never checked** — `GV-004` `Q-05` | |
| `ASM-17` | Third-party API costs stay within envelope | Quarterly | CFO | ⬜ $1,890–5,230/month at scale | |
| `ASM-18` | Three years of structured financial history is available | W3 | CFO | ⬜ | |
| `ASM-19` | Technicians can read Bengali interfaces | W2 | Ops Director | ⬜ | |
| `ASM-20` | Biometric attendance hardware procured before Wave 5 | W5 | HR Director | ⬜ `DEP-15` | |
| `ASM-21` | **A Bangladesh-resident data store of adequate reliability is procurable** | **Before W1 architecture** | CTO | ⬜ Blocks `D-013` | **✓** |
| `ASM-22` | **PDPA enforcement timing holds at ~13 May 2027** | Quarterly | CFO / Legal | ✅ **Verified 2026-08-18** — enforcement delayed ~18 months from the 2025 Ordinance; activates ~13 May 2027 | **✓** |

**Count verification:** 22 rows, of which 4 are charter-critical, 1 superseded, 1 verified, 20
unvalidated. Counted from the rows above per `PG-M10`.

> **Twenty of twenty-two assumptions are unvalidated, and none had a validation date until this
> issue.** `ASM-03` is the one to watch: the entire migration workstream, seven mapping workbooks
> and the `G1-05` gate criterion rest on data quality nobody has measured.

---

## 6. Issues

An **issue** is a risk that has materialised, an assumption that has failed, or a dependency that
has been missed. `00-04` has no issue register. These twelve are drawn from the four audits and
from Category 00's own analysis; every one is live today.

| ID | Issue | Raised | Age | Sev | Owner | Consequence now | Resolution |
|---|---|---|---:|:--:|---|---|---|
| `ISS-001` | **Twelve portal specifications are filed in the wrong folder** — 771 KB in `03_Modules/K_…/` | 2026-08-15 | 3 d | **Critical** | CTO | A vendor reading `FOLDER_STRUCTURE.md` concludes 12 specifications do not exist and quotes to write them | `AF-01` remediation; ~2 hours; needs CTO approval under `PG-M8` |
| `ISS-002` | **48 custom-development identifiers collide**; 70+ across the wider estate | 2026-08-12 | 6 d | **Critical** | Enterprise Architecture | **The build backlog cannot lawfully be created.** `_MODULE_TEMPLATE` §0 instructs authors not to create build tickets | `BE-005` + `RR-002` |
| `ISS-003` | **`R60` is a duplicate identity for `R32`** | 2026-08-13 | 5 d | **Critical** | Security / IAM | *"In a permission model, a duplicate role identity is a live security defect"* (`H2-07`). An access rule written against `R32` does not apply to a `R60` holder | Eliminate `R60`; `SC-004` |
| `ISS-004` | **`SOD-13` … `SOD-30` are used and unregistered** — 18 of 30 SoD controls | 2026-08-13 | 5 d | High | GRC | Controls that cannot be evidenced are, for audit purposes, controls that do not exist | Extend `05-04` to `SOD-30` |
| `ISS-005` | **44 of 95 KPI baselines are absent** | 2026-08-18 | 0 d | **Critical** | CFO | ~**BDT 396 lac** of the BDT 876 lac benefit case cannot be claimed under `06-02` §6. **Baselines can only be measured before the system changes the process** | `BM-002`; `D-018`; `GV-001` `CC-09` |
| `ISS-006` | **All 48 legacy sources are unprofiled** | 2026-08-17 | 1 d | **Critical** | CTO | Seven mapping workbooks are written against **assumed** structure. `G1-05` is unachievable | `MG-002`; `AUDIT-011` |
| `ISS-007` | **Test coverage has three denominators** — 2,930 / ~2,352 / 3,343 | 2026-08-17 | 1 d | High | Enterprise Architecture | No coverage percentage may be quoted at all (`TS-01`). A fourth count — 2,996 distinct `FR-` ids — was produced on 2026-08-18 | `RQ-004`; `AF-06` |
| `ISS-008` | **21 event names are consumed and not published**; 14 genuinely missing, including `claim.evidence_incomplete` and `recall.execution_updated` | 2026-08-18 | 0 d | **Critical** | Integration Lead | One suppresses claim submission; one is a **product-safety** control | `AR-009`, `IN-003`; `AP-01` |
| `ISS-009` | **`DT-031` maps nine `MD-028` fields that do not exist** | 2026-08-17 | 1 d | High | Master Data Owner | A document template bound to a non-existent data structure | `DA-002` data dictionary; `AUDIT-013` `F3` |
| `ISS-010` | **`CM-017` commissions a leaderboard that `M57` rule `BRU-PIC-16` prohibits outright** | 2026-08-18 | 0 d | High | Change lead | An adoption mechanism that violates the system's own business rules | `CH-004`; `CM-05` |
| `ISS-011` | **Four test packs cannot be executed** — no accessibility reviewer, no role accounts, no staged stock, no field logistics | 2026-08-17 | 1 d | High | QA Lead | Four of eighteen test packs are inert. Nine are consumed a wave before they exist | `QA-001`, `QA-009`; `TS-02` |
| `ISS-012` | **A folder name containing a space and an ampersand persists**, breaching the rule that produced `AF-12`; and `audit_analysis/` is unowned in the workspace root | 2026-08-15 | 3 d | Low | Content Lead / PMO | Breaks unquoted shell and CI paths | `PGD-A1-10`; referred, not fixed |

**Issue summary**, counted from the rows above: **12 issues — 6 Critical, 5 High, 1 Low.**
None is closed. Oldest: 6 days (`ISS-002`).

> **Rule `IS-01` — issue ageing is reported weekly.** An issue with no owner and no target date is
> a risk that has already happened and that nobody is treating. Six Critical issues, none closed,
> is the position the Steering Committee inherits at its first meeting.

---

## 7. Dependencies

### 7.1 Rules

| Rule | Provision |
|---|---|
| `DP-01` | Every dependency carries a **needed-by** date and, where external, a **lead time** |
| `DP-02` | A dependency missing its needed-by date becomes an **issue** automatically |
| `DP-03` | An external dependency is chased at **needed-by minus lead time**, not at needed-by |
| `DP-04` | A P0 integration dependency requires a documented **manual fallback** (`IP-09`, `OP-014`) |

### 7.2 Internal — `DEP-01` … `DEP-15`

Carried from `00-04` §3.1. All fifteen are `⬜ Open`.

| ID | Dependency | Needed by | Owner | Impact if late |
|---|---|---|---|---|
| `DEP-01` | Chart of accounts restructured for the dimensional model | W3 start | CFO | Finance configuration blocked |
| `DEP-02` | Payroll structures, tax parameters, PF rules confirmed | W5 start | HR Director | Payroll configuration blocked |
| `DEP-03` | Service catalogue and rate cards approved | W3 start | CCO | Pricing engine cannot be configured |
| `DEP-04` | Contract product definitions, all 14 families | W4 start | CCO | Contract engine cannot be configured |
| `DEP-05` | Legacy data extracted, profiled and cleansed | Per wave | Dept heads | **Migration and go-live slip** — see `ISS-006` |
| `DEP-06` | Super-users named, trained, time-protected | Each wave | Dept heads | **UAT fails — `RSK-001`** |
| `DEP-07` | Branch connectivity and hardware readiness | Per site | IT Administrator | Site rollout blocked |
| `DEP-08` | Technician devices procured and enrolled | W2 | Ops Director | Field rollout blocked; blocked by `D-011` |
| `DEP-09` | Marketplace commercial model decided | W7 − 3 mo | CEO + CFO | Marketplace build blocked — `RSK-022` |
| `DEP-10` | Rental / refurbishment legal-entity decision | W6 − 3 mo | CFO | Finance structure blocked |
| `DEP-11` | Telephony vendor selected | W4 − 2 mo | CTO | Contact centre build blocked |
| `DEP-12` | Data-services facility, controls, staff undertakings | W6 | Technical Services Head | Data services cannot launch |
| `DEP-13` | Multi-country target markets decided | W9 − 3 mo | CEO | Country pack cannot be specified |
| `DEP-14` | Quality management system documentation current | W5 | Quality Manager | QMS configuration blocked |
| `DEP-15` | Biometric attendance hardware installed | W5 | IT Administrator | GPS-only fallback |

### 7.3 External — `DEP-16` … `DEP-30`

Carried from `00-04` §3.2. **Lead time is new** and is the field that makes `DP-03` operable.

| ID | Dependency | Party | Needed by | Lead time | Fallback exists? |
|---|---|---|---|---|:--:|
| `DEP-16` | bKash API access, sandbox then production | bKash | W3 | 8–12 wk | Cash at counter |
| `DEP-17` | Nagad API access | Nagad | W3 | 8–12 wk | Reduced options |
| `DEP-18` | SSLCOMMERZ integration | SSLCOMMERZ | W3 | 6–8 wk | Cards unavailable |
| `DEP-19` | WhatsApp Business API approval | Meta / BSP | W1 | 4–8 wk | SMS only |
| `DEP-20` | SMS gateway contracts, primary and failover | SMS providers | W1 | 4–6 wk | Push + email |
| `DEP-21` | Google Maps Platform commercial terms | Google | W2 | 4 wk | OSM |
| `DEP-22` | Brand partner claim format specifications | **17+ brands** | W4 | 12–20 wk | Manual claim preparation |
| `DEP-23` | BEFTN file format confirmation | Banking partner | W5 | 6–8 wk | Manual disbursement |
| `DEP-24` | NBR e-VAT submission specification | NBR | W4 | unknown | Manual VAT filing |
| `DEP-25` | Courier partner API access | Pathao / RedX | W3 | 6–10 wk | Internal riders |
| `DEP-26` | Telephony carrier interconnect for 16743 | Telecom operator | W4 | 12–16 wk | Hotline outside the system |
| `DEP-27` | Identity verification service agreement | KYC provider | W7 | 8–12 wk | Manual seller verification |
| `DEP-28` | Certified e-waste recycling partners | Recycling partners | W8 | 12 wk | Programme cannot launch |
| `DEP-29` | External tax and legal opinion on the marketplace | Advisors | W7 − 3 mo | 8–12 wk | **None. `RSK-022` Critical** |
| `DEP-30` | Accredited e-signature provider agreement | Trust service provider | W3 | 8–12 wk | Wet-signed contracts |

> **`DEP-22` is the largest external exposure.** Seventeen or more counterparties, each with its
> own claim format, needed by Wave 4, at 12–20 weeks each — and the "17+" figure is itself
> unverified (`H2-12`). Warranty revenue recovery is the **largest single benefit line** at BDT 100
> lac. Chasing must begin at W4 − 20 weeks under `DP-03`, which is inside Wave 1.

### 7.4 Regulatory — `DEP-31` … `DEP-35`

| ID | Dependency | Owner | Needed by | Lead time | Status |
|---|---|---|---|---|---|
| **`DEP-31`** | **Legal opinion on the split-residency data architecture** | CTO + Legal | **Before W1 architecture is fixed** | **6–10 wk** | ⬜ **Longest lead on the critical path.** Open since 2026-08-12 |
| `DEP-32` | Significant data fiduciary classification assessment | CEO + Legal | W4 − 3 mo | 4–6 wk | ⬜ `D-015` |
| `DEP-33` | Registration or notification with the National Data Management Authority | Legal | W4 − 3 mo | unknown | ⬜ The Authority reports to the Prime Minister's Office |
| `DEP-34` | PDPA-compliant transparency notice text, Bengali and English, per capture point | Legal + CCO | W1 build | 4–8 wk | ⬜ **Consent captured without a valid notice is not valid consent** |
| `DEP-35` | Media sanitisation programme document naming IEEE 2883, per NIST SP 800-88r2 | Quality Manager | W6 − 2 mo | 4 wk | ⬜ `H-01`; `M06` certificates are otherwise indefensible |

**Dependency count verification:** 15 internal + 15 external + 5 regulatory = **35**, matching
`00-04` §3. Counted from the rows above.

---

## 8. Operating the Register

### 8.1 Review cadence

| Activity | Frequency | Owner | Output |
|---|---|---|---|
| Critical risk review | Every Steering Committee | Risk owner | Treatment status, trigger position |
| High risk review | Every wave gate | Risk owner | Gate evidence pack |
| Medium/Low review | Quarterly | PMO | Register update |
| **Issue ageing** | **Weekly** | PMO | Ageing report; anything > 14 days escalates |
| Assumption validation sweep | Monthly | PMO | Any assumption past its date → risk |
| Dependency chase | At needed-by minus lead time | Dependency owner | Confirmation or escalation |
| Full re-baseline | **Every wave gate** | PMO | Re-scored register with a fresh enumeration timestamp |
| Heat summary regeneration | **Every issue of this document** | PMO | §4.3, counted not carried forward (`PG-M10`) |

### 8.2 Register health metrics

| Metric | Current | Target |
|---|---:|---|
| Risks with a named owner | 44 / 44 | 100% |
| Risks with a **trigger condition** | 12 / 44 | 100% by Wave 1 gate |
| Critical risks with a treatment **in progress** | **0 / 12** | 100% by Wave 1 |
| Assumptions with a validation date | 22 / 22 *(new at this issue)* | 100% |
| Assumptions **validated** | **1 / 22** | 100% by the wave that depends on them |
| Issues closed | **0 / 12** | — |
| Dependencies with a lead time | 20 / 35 *(external + regulatory)* | Internal lead times added by Wave 1 |
| Owners breaching `RA-01` | **2** *(CTO 9, CFO 6)* | 0 |

> **"Critical risks with a treatment in progress: 0 of 12" is the headline of this register.**
> Every Critical risk has a stated mitigation in `00-04`; not one has an owner who has started it,
> because there has been no body to task them and no decision to fund them. That is the same root
> cause as `RSK-040`, and it closes when `GV-002` §9.1 completes.

---

## 9. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-005-D-01` | Whether to restate the 36 carried risks in full | Restate · Reference | **Reference `00-04` §1** | `PG-02`: content is referenced, never duplicated. A second copy drifts — which is `AF-02` | This register is the live instrument; `00-04` remains the narrative analysis |
| `GV-005-D-02` | Whether to correct `00-04` §1.5 here or leave it | Leave and note · Correct here | **Correct here, and record it as a finding** | A wrong heat summary understates Critical risk by 60% and omits all three statutory/financial ones | `PGD-A2-01`; `00-04` §1.5 must be amended |
| `GV-005-D-03` | Whether to create an issue register | Treat findings as risks · Separate issue register | **Separate** | A materialised risk is not a risk. Twelve live issues were invisible because no register held them | Weekly ageing becomes possible |
| `GV-005-D-04` | Whether to record opportunities | Threats only, as `00-04` does · Both | **Both** | PMBOK 7 treats uncertainty as symmetric. `OPP-03` alone absorbs 41% of the unscheduled work | Three opportunities with named exploitation owners |
| `GV-005-D-05` | Whether to separate risk owner from actionee | Single owner · Owner + actionee | **Separate** | The CTO owns nine Critical/High risks. One person cannot execute nine treatments | `RA-01`; §4.5 concentration analysis |

---

## 10. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Should `00-04` §1 be retired in favour of this register, or retained as narrative? Two live risk registers is the `AF-02` failure mode | Enterprise Architecture + PMO | Week 4 | Register authority |
| `Q-02` | Is there a risk **budget** — funds set aside for treatment, distinct from schedule contingency? PRINCE2 requires one; no document mentions it | CFO | Week 6 | Treatment of all 12 Critical risks |
| `Q-03` | Who chases `DEP-22` with 17+ brand partners? No owner is named for the aggregate, only for the outcome | CCO | Week 2 | W4 warranty automation; BDT 100 lac benefit |
| `Q-04` | Do the content risks in `CG-013` need promoting into this register, or is cross-reference sufficient? | Content Lead + PMO | Week 6 | Workstream 5 risk visibility |
| `Q-05` | What is the trigger threshold for `RSK-008` (technician rejection)? "Slower than paper" needs a measured paper baseline that does not exist | Ops Director | W2 − 4 wk | The Critical risk most likely to end the programme |

---

## 11. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every risk in `00-04` §1 appears with its rating, owner and treatment status | 36 carried + 8 new = 44 |
| `AC-02` | The heat summary is regenerated by counting, and any discrepancy with the source is recorded as a finding | §4.3; `PGD-A2-01` |
| `AC-03` | Every assumption has a validation owner and date | §5.2 — 22 of 22 |
| `AC-04` | An issue register exists and every entry has an owner, an age and a resolution route | §6 — 12 entries |
| `AC-05` | Every external dependency has a lead time | §7.3, §7.4 — 20 of 20 |
| `AC-06` | Transitions between assumption, risk and issue are defined | §3.5 |
| `AC-07` | Risk concentration is measured against a stated threshold | §4.5; `RA-01` |
| `AC-08` | Opportunities are recorded, not only threats | §4.6 — 3 |
| `AC-09` | Register health is measured, not asserted | §8.2 |
| `AC-10` | Every statutory citation carries a verification date | `ASM-22` verified 2026-08-18 |

**Definition of done.** Complete when every criterion is met, all 12 Critical risks have a
treatment in progress with a named actionee, the Steering Committee has accepted or rejected each
Critical risk under `GV-002` §5.2, and `PGD-000` records `GV-005` as ✅ with a fresh enumeration
timestamp.

---

## 12. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-001`](GV-001_Programme_Charter_and_Mandate.md) §10 | Names the Board-level risks; §9.1 holds the constraints this register excludes |
| Upstream | [`GV-002`](GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) §5.2 | Risk acceptance authority by rating |
| Upstream | [`GV-003`](GV-003_Decision_Log_and_Change_Control_Procedure.md) | `D-013`…`D-024`; an open decision's consequence is registered here |
| Downstream | [`GV-004`](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) §7.1 | Schedule risk extract; `RSK-037`, `RSK-038` |
| Downstream | [`GV-007`](GV-007_Estimation_Model_and_Resource_Plan.md) | `RSK-039`, `RSK-043` are its inputs |
| Downstream | [`GV-009`](GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) | Risk position is gate evidence |
| Downstream | [`GV-010`](GV-010_Programme_Assurance_and_Independent_Review_Plan.md) | `RSK-042` is its mandate |
| Downstream | `SC-002` | STRIDE threat model refines `RSK-024` and the security residue |
| Downstream | `SC-003` | DPIA refines `RSK-032`, `RSK-033` |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` §1–§3 | The source registers, referenced not restated; §1.5 corrected |
| Lateral | `../../project_content/00_Content_Governance_and_Standards/CG-013` | Content risk and legal escalation rules |

---

## 13. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) ·
[`GV-001`](GV-001_Programme_Charter_and_Mandate.md) · [`GV-003`](GV-003_Decision_Log_and_Change_Control_Procedure.md) · [`GV-004`](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md)

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` §1, §2, §3 ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06`, `00-07` ·
`../../project_content/_AUDIT/AUDIT-001`, `AUDIT-011`, `AUDIT-013`, `AUDIT-014`, `AUDIT-015`, `AUDIT-016`, `AUDIT-017`, `AUDIT-019`

**External standards** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| ISO 31000:2018 — principles, framework, process; risk management is not certifiable but is the structuring discipline | §2, §3, §8 |
| ISO Guide 73:2009 — risk vocabulary | §3 definitions |
| ISO 21502:2020 §7.8 | Ownership and escalation |
| PMBOK Guide 7th Edition — *Uncertainty* performance domain; symmetric treatment of risk | §4.6 opportunities |
| PRINCE2 7th Edition (2023) — risk practice; Issue Register; risk owner vs risk actionee; risk budget | §3.4, §6, `Q-02` |
| Bangladesh PDPA 2026 — penalties to BDT 25 lakh / BDT 50 lakh; National Data Management Authority reports to the Prime Minister's Office and may warn, fine and order suspension of cross-border transfers; enforcement ~13 May 2027 | `RSK-032`, `ASM-22`, `DEP-33` |
| NIST SP 800-88r2 (published 26 September 2025; r1 withdrawn the same day) — requires IEEE 2883 or an organisationally approved standard; ISO/IEC 19790 for cryptographic erase | `DEP-35` |

---

## 14. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Programme Management Office | Initial issue. Corrects the `00-04` §1.5 heat summary (8/22/6, not 5/16/10) as `PGD-A2-01`; creates the issue register (12 live issues, 6 Critical); adds 8 risks, 3 opportunities, validation dates on 22 assumptions and lead times on 20 dependencies; separates risk owner from actionee; corrects the stale `PGD-000` `GV-005` row as `PGD-A2-06` | *pending Steering Committee* |

---

*`GV-005` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
