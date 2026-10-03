---
id: TS-010
title: UAT Script Pack — People and Workforce Roles
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HR with QA Lead
author: QA Lead with HR Manager, payroll, L&D and HSE
reviewers: [HR Manager, CFO delegate, HR Officer representatives, Quality Manager, L&D Lead, HSE Lead, Localisation Lead]
approver: HR Manager with QA Lead
content_class: E
purpose: >
  The acceptance scripts executed by HR, payroll, learning and safety, including the parallel-run
  comparison that must be passed before the first live payroll. Payroll is the one process on this
  programme with no tolerance and no recovery: a wrong net pay is an employment-law matter under the
  Bangladesh Labour Act, a wrong statutory deduction misstates an employee's tax position for the
  year, and neither can be corrected by a later run without the employee already having been paid
  the wrong amount. Correctness is proven against two parallel cycles, not asserted from a
  calculation.
traces_to: [M21, M22, M55, M56, M57, M58, M59, M23, M19, 05-04, 05-04 §7, 05-04 §9, 05-05, 05-06 §6.2, 06-01 §6, 06-02 §4, MD-008, MD-009, MD-010, MD-011, MD-042, MD-043, SP-021, SP-022, SP-023, SP-030, TR-015, TR-016, DT-041, DT-042, DT-043, UI-030, UI-031, BN-015, TS-001, TS-002, TS-005, TS-006, TS-009, TS-017, TS-018, DM-009]
priority: P1
wave: W5
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §10 BRU-HRM-01…07 and BRU-LMS-01…02, §12.4 AUT-041…AUT-052
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §6.2 NFR-083 Bangladesh Labour Act compliance in HR and payroll; §6.1 statutory table — Bangladesh Labour Act 2006 as amended, in force, verified 2026-08-12
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md §6 Parallel Running — payroll runs in parallel for 2 pay cycles with "zero tolerance for pay errors"
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 5 G5-01 first payroll run processed, validated and paid with zero errors, G5-02 BEFTN file accepted by the bank without rework, G5-03 zero uncertified technicians assignable to brand warranty work, G5-07 attendance capture ≥ 98%; §2.8 KPI-059…068
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# UAT Script Pack — People and Workforce Roles

| Item | Value |
|---|---|
| Test level | **UAT** — method in [`TS-006`](TS-006_UAT_Script_Pack_Service_Operations_Roles.md) §2.1 and §3.2 |
| Roles executing | `R30` `R31` `R32` — **3 roles, 6–12 people**, plus `R03` jointly on payroll approval |
| Modules covered | `M21` `M22` `M55` `M56` `M57` `M58` `M59`, with `M23` and `M19` as touchpoints |
| Portals covered | `P03` HR Console (`UI-030`), Quality Console (`UI-031`), `P06`; `P02` and `P11` as employee surfaces |
| Environment | `UAT` — frozen for the cycle; **plus two live parallel payroll cycles** (§2.1 `UA-32`) |
| Test data set | `TS-002` — employee set with a full attendance period, an unapproved-overtime case, and one certification expiring inside the window |
| Wave | W5 · `G5` at Month 22 |

> **Template conformance.** As `TS-006`: `TPL_Test_Script.md` at pack level, all six sections
> retained in order with pack-level interpretation.

> **Method by reference.** `UA-01`…`UA-18` (`TS-006` §2.1), `UA-19`–`UA-20` (`TS-007` §2.1),
> `UA-27`–`UA-31` (`TS-009` §2.1, applied to payroll's statutory outputs). This pack adds
> `UA-32`…`UA-35` (§2.1).

---

## 1. Traceability

### 1.1 Why payroll is tested differently from everything else

Every other process on this programme can be tested, found wrong, fixed and re-tested. Payroll
cannot, for three reasons that are structural rather than technical:

| Reason | Consequence for the test method |
|---|---|
| **The output is money already paid.** A wrong net pay is not a defect record; it is a shortfall or an overpayment in a named person's bank account | Correctness must be established **before** the run, by comparison against an independently produced result — `UA-32` |
| **Year-to-date figures cannot be recomputed after the fact.** `DM-009` states it plainly: migrating YTD payroll wrongly misstates every employee's tax position | The migrated YTD position is verified as a **precondition**, not as an outcome |
| **It is statutory.** `NFR-083` binds HR and payroll to the Bangladesh Labour Act 2006 as amended | `TS-009`'s statutory rules `UA-27`…`UA-31` apply here in full, with HR in the finance function's place |

`06-01` §6 already sets the mechanism: **payroll runs in parallel for two pay cycles, with "zero
tolerance for pay errors"**. `UA-32` turns that from a rollout instruction into a test obligation
with a numeric exit.

### 1.2 Traceability obligation

Per `TS-006` §1.2, `TS-007` `UA-20` and `TS-009` §1.2, with:

| Field | Source |
|---|---|
| **Payroll element** | `MD-043` payroll element and statutory deduction register — the element under test, by identifier |
| **Statutory instrument** | Bangladesh Labour Act 2006 as amended; NBR income-tax rules; with verification dates (`UA-29`) |
| **Parallel-run reference** | The independently produced figure the script compares against (`UA-32`) |

### 1.3 Role coverage

| Role | Headcount | Scripts | `P0` | Language | Scope | SOP | Course pack |
|---|---:|---:|---:|---|---|---|---|
| `R30` HR Manager | 1–2 | **16** | 9 | English | all employees | `SP-021`, `SP-022`, `SP-023` | `TR-015` |
| `R31` HR Officer | 3–6 | 12 | 5 | English | assigned scope | `SP-021`, `SP-022`, `SP-023` | `TR-015` |
| `R32` Quality Manager — learning, certification and safety | 2–4 | 8 | 4 | English | all branches | `SP-029`, `SP-030` | `TR-016` |
| **Total** | **6–12** | **36** | **18** | | | | |

> **Two audiences in this pack execute nothing and are affected by everything.** Payslips reach
> **800+ employees** and mandatory-training restrictions reach **200–400 technicians**. Neither is a
> `05-04` role for these modules, and the employee-facing verification is therefore built into
> `UAT-R30-011` and `UAT-R32-004` rather than left to a role that does not exist in the matrix.
> Recorded as `O-05`.

> **There is no HSE or L&D role in `05-04`.** The register's Category 13 row for this file names
> *"HR, payroll, learning and safety roles"*. `05-04` §1 has 38 roles and none of them is an HSE
> Lead or an L&D administrator; the closest holder of both duties is `R32` Quality Manager, who is
> assigned the learning and safety blocks here. **This is a role-register gap, not an authoring
> choice** — `O-04`.

---

## 2. Preconditions

### 2.1 Additional rules for payroll and workforce scripts

| # | Rule |
|---|---|
| **UA-32** | **Payroll correctness is proven by parallel run, not by calculation.** Two full cycles are computed in both the legacy process and the new system, and every employee's gross, each element, each statutory deduction and net pay are compared line by line. **A difference is a defect until it is explained, in writing, by HR and Finance jointly** |
| **UA-33** | **Every payroll variance is explained, not netted.** Two differences that cancel at the total are two defects, not zero. `UA-30` control totals do not substitute for line-level comparison here |
| **UA-34** | Every script touching a person's own record verifies **who else can see it** — `05-04` §5 restricts `salary`, `allowances`, `deductions`, `nid_number` and `bank_account`, and `BRU-HRM-07` prohibits peer and below-HR-Manager visibility |
| **UA-35** | Every competency or certification script verifies the **downstream restriction**, not just the record: an expired certification must be shown to have removed the technician from the dispatch pool (`AUT-042`), and overdue mandatory training to have restricted the work type (`BRU-LMS-01`) |

### 2.2 Additional preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | `TS-006` preconditions 1–4, 7, 9; `TS-005` SIT exit for the `H` block on the same release | Exit records |
| 2 | `MD-008` positions and `MD-009` roles loaded, so a joiner inherits a role from a position profile | `AUT-047` |
| 3 | `MD-010` competency taxonomy and `MD-011` certification register loaded, **with one certification expiring inside the cycle** | `UA-35` |
| 4 | `MD-042` shift and roster patterns; `MD-041` holiday calendar including moon-dependent dates | `05-06` §9 |
| 5 | `MD-043` payroll elements and statutory deductions configured and **signed off by HR and Finance** | `UA-32` |
| 6 | **Migrated YTD payroll position loaded and verified** | `DM-009` — **unwritten**, `O-02` |
| 7 | **Legacy payroll output for two full cycles available for line-by-line comparison** | `UA-32`; `06-01` §6 — **no owner allocated**, `O-01` |
| 8 | BEFTN file format confirmed against the bank's current specification | `G5-02` |
| 9 | Two distinct accounts for `SOD-03` (process payroll / approve payroll) | `TS-002` `O-04` |
| 10 | A biometric attendance device, and its template treated as residency-classified | `05-06` §6.4; `NFR-086` |
| 11 | Employee self-service accessible to a test employee who is not an HR role | `KPI-065`; `UA-34` |

---

## 3. Scripts

### 3.1 Block A — `R30` HR Manager · 16 scripts

`SP-021`, `SP-022`, `SP-023` · `TR-015` · all employees

| Script | The job | Rules and instrument | Pri |
|---|---|---|:--:|
| `UAT-R30-001` | **Run the parallel comparison for cycle 1: every employee's gross, every element, every statutory deduction, every net pay, line by line** | `UA-32` `UA-33`; `06-01` §6 | **P0** |
| `UAT-R30-002` | **Run the parallel comparison for cycle 2 and confirm zero unexplained differences** | `UA-32`; `G5-01` | **P0** |
| `UAT-R30-003` | **Try to finalise payroll with attendance for the period unverified or unlocked, and be refused** | `BRU-HRM-05`(H) `AUT-045` | **P0** |
| `UAT-R30-004` | **Confirm unapproved overtime did not count, and approved overtime did, with the approval traceable** | `BRU-HRM-02`(H) | **P0** |
| `UAT-R30-005` | **Approve payroll jointly with the CFO, and be refused approving it alone** | `BRU-HRM-06`(H) `SOD-03` | **P0** |
| `UAT-R30-006` | **Try to process and then approve the same payroll run, and be refused** | `SOD-03`; `UA-26` | **P0** |
| `UAT-R30-007` | Generate the BEFTN file and confirm the bank accepts it without rework | `AUT-046`; `G5-02` | **P0** |
| `UAT-R30-008` | Confirm the payroll journal posted to the expected accounts and ties to the disbursement | `SL-17` `SL-18`; `TS-009` | **P0** |
| `UAT-R30-009` | Confirm every statutory deduction is at the correct rate for the period, against the instrument | `NFR-083`; `UA-27` `UA-29`; `MD-043` | **P0** |
| `UAT-R30-010` | Measure the payroll processing time and corrections per run | `KPI-059` < 4 h, `KPI-060` < 0.3%; `UA-19` | P1 |
| `UAT-R30-011` | **Inspect a rendered payslip as an employee receives it, in Bengali, and confirm every element is legible and correct** | `DT-041`; `BN-015`; `UA-28`; `O-05` | **P0** |
| `UAT-R30-012` | Take a joiner from `employee.joined` through identity, role from position profile, portal access and assigned training | `AUT-047`; `05-04` §9 | P1 |
| `UAT-R30-013` | Take a leaver through revocation **within one hour**, device deregistration and delegated-authority reassignment | `BRU-SEC-06`(H) `AUT-048`; `SL-24` | P1 |
| `UAT-R30-014` | Approve leave, and be warned where coverage would fall below the configured minimum | `BRU-HRM-04`(A) | P1 |
| `UAT-R30-015` | Confirm incentive calculated only after the minimum monthly job threshold, from `M02`-measured jobs | `BRU-HRM-03`(C); `UA-19` | P1 |
| `UAT-R30-016` | Issue an HR letter from the template set and confirm it renders correctly | `DT-042` | P2 |

### 3.2 Block B — `R31` HR Officer · 12 scripts

`SP-021`, `SP-022`, `SP-023` · `TR-015` · assigned scope only

| Script | The job | Rules and instrument | Pri |
|---|---|---|:--:|
| `UAT-R31-001` | Capture and verify attendance for a period including a shift pattern, a holiday and a moon-dependent date | `MD-041`, `MD-042`; `G5-07` ≥ 98% | **P0** |
| `UAT-R31-002` | Resolve an attendance exception and confirm it flows to payroll | `AUT-045`; `KPI-061` | **P0** |
| `UAT-R31-003` | Capture biometric attendance and confirm the template is stored in the Bangladesh-resident store | `NFR-086`, `NFR-099`; `TS-017` | **P0** |
| `UAT-R31-004` | **Try to see an employee outside your assigned scope, and be refused** | `05-04` §3.4 `(scope)` | **P0** |
| `UAT-R31-005` | **Try to see `salary`, `allowances` or `bank_account` for an employee, and be refused where the grant does not extend** | `05-04` §5; `BRU-HRM-07`(H); `UA-34` | **P0** |
| `UAT-R31-006` | Onboard a new employee end to end, including mandatory training assignment | `AUT-047`; `SP-023` | P1 |
| `UAT-R31-007` | Record a transfer and confirm old permissions revoked and new granted on the effective date, **with no accumulation** | `05-04` §9 Modify | P1 |
| `UAT-R31-008` | Handle a leave balance carried from the migrated position | `DM-009`; `O-02` | P1 |
| `UAT-R31-009` | Support an employee using self-service, and confirm they can see their own payslip and nobody else's | `KPI-065`; `BRU-HRM-07`(H); `UA-34` | P1 |
| `UAT-R31-010` | Roster a shift that would breach working-time limits and confirm approved overtime is required first | `BRU-FSM-10`(H) | P1 |
| `UAT-R31-011` | Record a recruitment pipeline stage and an offer | `M58`; `SP-023` | P2 |
| `UAT-R31-012` | Issue a salary certificate and confirm it is not a payslip | `DT-041` | P2 |

### 3.3 Block C — `R32` Quality Manager — learning, certification and safety · 8 scripts

`SP-029`, `SP-030` · `TR-016` · all branches · **see `O-04` on the missing HSE and L&D roles**

| Script | The job | Rules and instrument | Pri |
|---|---|---|:--:|
| `UAT-R32-001` | **Confirm an expired certification removed the technician from that brand's warranty dispatch pool** | `BRU-HRM-01`(H) `AUT-042`; `UA-35`; `G5-03` zero | **P0** |
| `UAT-R32-002` | Confirm expiry notices fired at −90/−60/−30/−15 days to technician, manager and HR, and re-certification was scheduled | `AUT-041`; `KPI-062` 100% | **P0** |
| `UAT-R32-003` | **Confirm overdue mandatory training restricted the affected work types, and that completion lifted the restriction** | `BRU-LMS-01`(H); `UA-35`; `KPI-064` | **P0** |
| `UAT-R32-004` | **Confirm a technician can see their own certification status and assigned learning in `P02`, in Bengali** | `P02` Personal; `UI-012`; `O-05` | **P0** |
| `UAT-R32-005` | Confirm a marketplace engineer cannot be activated in a category without passing its qualification | `BRU-LMS-02`(H); `TS-007` | P1 |
| `UAT-R32-006` | Take a safety incident reported from `P02` through non-conformance, containment and CAPA | `BRU-QMS-02`(H) `AUT-049`; `SP-030`; `NFR-083` | P1 |
| `UAT-R32-007` | Confirm a CAPA cannot close without effectiveness verification, and that failed verification reopened it | `BRU-QMS-03`(H) `AUT-050`; `KPI-066` | P1 |
| `UAT-R32-008` | Run an internal quality audit entirely in the system and confirm `G5-04` | `SP-029`; `DT-043`; `G5-04` | P1 |

**Pack total: 36 scripts · 18 at `P0` · 14 at `P1` · 4 at `P2`.**

### 3.4 Negative and edge cases

| # | Condition | Expected system behaviour |
|---|---|---|
| N-01 | Attendance corrected after the period is locked | Requires a documented reopening; never a silent edit (`BRU-HRM-05`) |
| N-02 | Employee joins and leaves within one payroll period | Pro-rated correctly, both events reflected, statutory deductions correct |
| N-03 | Two payroll runs initiated for the same period | Second blocked; no duplicate disbursement |
| N-04 | BEFTN file rejected by the bank | Rejection surfaced with the reason; **no partial disbursement** (`NFR-029`) |
| N-05 | Statutory rate changes mid-year | Rate at the period applies; YTD position not retrospectively restated without a decision (`CG-006` §5) |
| N-06 | Line manager attempts to view a report's payslip | Refused — `BRU-HRM-07` prohibits visibility below HR Manager (`UA-34`) |
| N-07 | Certification expires overnight while a job is already assigned | Assigned job handled per the exception path; **new assignments blocked** (`AUT-042`) |
| N-08 | Biometric template requested for export | Blocked; residency-classified and `NFR-099`-restricted (`TS-017`) |
| N-09 | Employee record deleted | Soft deletion only; payroll history retained per `NFR-088` (`DI-08`) |
| N-10 | Overtime approved after the period is locked | Queued to the next period, not back-dated into a finalised run |

### 3.5 Bilingual check

**English-only pack (`CG-010` §3.2).** The three executing roles are 6–12 head-office people working
in English. **The artefacts they produce are read by 800+ employees in Bengali**, so three
assertions are inside the pack rather than deferred:

| Element | EN correct | BN correct | Truncation |
|---|:--:|:--:|:--:|
| **Payslip as the employee receives it** (`DT-041`, `BN-015`) — `UAT-R30-011` | ● | ● | **● — a truncated deduction line is a Labour Act exposure** |
| Certification and assigned-training screens in `P02` (`UI-012`) — `UAT-R32-004` | ● | ● | ● on a 5-inch device |
| Safety incident reporting path from `P02` (`SP-030`) | ● | ● | ● |

> **Why the pack is English-only while `TS-009` is bilingual.** `CG-010` §3.3 asks who reads the
> artefact to do their job. `TS-009` has 51+ Bengali-first cashiers *executing*; this pack has none —
> the Bengali readers are the *subjects* of the scripts, not the executors. `CG-010` §3.2 allocates
> 7 bilingual `TS` files and this is not one of them; the three assertions above are how the
> obligation is discharged without a second language edition.

---

## 4. Exit Criteria

`TS-006` §4 applies. Additional:

| Criterion | Threshold |
|---|---|
| `P0` scripts passed | **100% — no tolerance** |
| `P1` scripts passed | ≥ 98% |
| **Parallel-run cycles completed and compared line by line** | **2 of 2** (`UA-32`; `06-01` §6) |
| **Unexplained payroll differences** | **Zero.** Offsetting differences count individually (`UA-33`) |
| **`G5-01` first live payroll run** | **Processed, validated and paid with zero errors** |
| **`G5-02` BEFTN file** | **Accepted by the bank without rework** |
| **`G5-03` uncertified technicians assignable to brand warranty work** | **Zero** |
| `G5-07` attendance capture completeness | ≥ 98% |
| Downstream-restriction verifications | 100% of certification and training scripts (`UA-35`) |
| Field-level visibility refusals | 100% (`UA-34`) |
| SoD refusal (`SOD-03`) | Blocked with two distinct users |
| Payslip verified in Bengali on the rendered artefact | 100% |
| Open Critical or High defects | **Zero. High defects are not deferrable in the payroll blocks** — §5 |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Payroll defects follow `TS-009`'s non-deferral rule.** Two automatic escalations:

| Trigger | Escalation |
|---|---|
| Any defect where a payroll figure — gross, element, deduction or net — is wrong | **Critical** to HR Manager and CFO; **not deferrable**. `NFR-083` makes it statutory and `KPI-060` targets under 0.3% corrections, so the first wrong figure is the finding |
| Any defect where an employee's restricted data is visible to someone not entitled to it | **Critical** to Chief Data Officer and HR Manager. `05-04` §5 and `BRU-HRM-07` are `P0`, and under the Personal Data Protection Act 2026 payroll data is personal data with a rights regime attached |

---

## 6. Sign-off

| Role | Super-user name | Release | Pack version | Date | Signature |
|---|---|---|---|---|---|
| `R30` HR Manager | | | | | |
| `R31` HR Officer | | | | | |
| `R32` Quality Manager | | | | | |
| **Parallel-run acceptance** — HR Manager **and** CFO jointly | | | | | |
| **Pack acceptance** — HR Manager | | | | | |

> **The joint parallel-run signature is the gate.** `UA-32` requires HR and Finance to explain every
> difference in writing; the signature is the record that they did, and `G5-01` cannot be claimed
> without it.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The parallel-run comparison has no owner and no reference source.** `06-01` §6 requires two payroll cycles in parallel with zero tolerance, and `UA-32` requires a line-by-line comparison against an independently produced result. **Nothing specifies who produces the legacy result, in what format, or who signs the reconciliation.** Without it, `G5-01` is a statement that the new system agreed with itself | HR Manager with CFO | **W5 — two cycles before the first live run** |
| **O-02** | **`DM-009` HR and payroll mapping workbook is unwritten** (Category 12 unstarted). Precondition 6 — a verified migrated YTD position — cannot be met, and `DM-009`'s own register entry states that YTD figures cannot be recomputed after the fact. This is the single least recoverable migration on the programme | Data Migration Lead with HR | **W5 — but the decision is needed at W1, because YTD accumulates from cutover** |
| **O-03** | **Payroll and payslip content is statutory and has no external verification.** `TS-009` `O-01` records the same block for Mushak; here the instrument is the Bangladesh Labour Act 2006 as amended and the NBR income-tax rules, and `UA-27` requires HR to state the expected result from the instrument, not from the configuration. `DT-041` is `AUDIT-007`-blocked on the same gate | HR Manager with Legal Counsel and an external adviser | **W5 — before the first parallel cycle** |
| **O-04** | **There is no HSE role and no L&D role in `05-04`.** The register names *"HR, payroll, learning and safety roles"* for this file; the matrix has 38 roles and none of them is an HSE Lead or an L&D administrator, so the learning and safety blocks are assigned to `R32` Quality Manager by inference. `AUDIT-009` already recorded three roles unregistered in `MD-009`; **this is the same register gap surfacing in the test pack** | Enterprise Architecture with HR Manager | **W5 — register correction** |
| **O-05** | **The two largest affected populations execute nothing.** 800+ employees receive payslips and 200–400 technicians are subject to training restrictions, and neither is a `05-04` role for these modules. `UAT-R30-011` and `UAT-R32-004` verify their view by proxy; **a proxy verification of a payslip 800+ people will read is thin**, and an employee-representative execution should be considered | HR Manager with QA Lead | **W5** |
| **O-06** | **`R32` carries three unrelated duty sets in this pack** — learning, certification and safety — because no other role holds them. `05-04` §1.5 gives `R32` `CRUDA(a)` on `M23` and `R(a)` on `M22`, which means the Quality Manager can *read* learning records but not administer them. **`UAT-R32-002` and `UAT-R32-003` may not be executable by the role they are assigned to**; this must be resolved before the cycle | Quality Manager with `M29` owner | **W5 — before execution of block C** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; interpretation declared
- [x] **Method taken by reference from `TS-006`, `TS-007` and `TS-009` rather than restated (`CP-01`)**
- [x] **The three structural reasons payroll is tested differently stated, with the method consequence of each**
- [x] Four additional rules stated, led by the parallel-run obligation `UA-32`
- [x] **Offsetting variances counted individually rather than netted (`UA-33`)**
- [x] 36 scripts enumerated across 3 roles with rules, instrument and priority
- [x] Downstream restriction — not just the record — required for every certification and training script
- [x] Ten workforce edge cases stated, including joiner-and-leaver in one period and post-lock overtime
- [x] English-only status justified against `CG-010` §3.3, with three bilingual assertions retained inside the pack
- [x] Truncated payslip deduction line classified as a Labour Act exposure
- [x] Non-deferral rule inherited from `TS-009` for payroll defects, with the reason stated
- [x] Joint HR and CFO parallel-run signature made the gate for `G5-01`
- [x] All internal links resolve
- [x] Six open items recorded, including two role-register gaps found while assigning executors
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 36 per-step grids — outstanding**
- [ ] **`O-01` parallel-run reference source unowned — outstanding; `G5-01` unevidenceable without it**
- [ ] **`O-02` `DM-009` unwritten — outstanding; the YTD decision is needed at W1, not W5**
- [ ] **`O-06` `R32` may lack the permission to execute block C — outstanding**
- [ ] Named approvers recorded — **pending HR Manager and QA Lead; external adviser not appointed**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
