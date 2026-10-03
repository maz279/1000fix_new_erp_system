---
id: SP-021
title: SOP — Payroll Run and Statutory Filing
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HR with Finance
author: Business Process Lead with HR Operations and Financial Control
reviewers: [CFO, HR Manager, Finance Manager, Tax Lead, Legal Counsel, Internal Audit, CTO, Localisation Lead]
approver: Chief Financial Officer and HR Manager, jointly, with external verification of the statutory elements
content_class: A
purpose: >
  Payroll errors for 500+ employees are visible, urgent and legally consequential. This SOP
  governs input cut-off, validation, the three-way prepare-approve-release separation,
  disbursement, statutory deduction and filing, and exception handling. Payroll cannot be
  finalised until attendance is verified and locked, requires two approvals, and the person who
  approves the run may not release the bank file — three controls that only work if the process
  operating them is fixed.
traces_to: [M56, M55, M21, M57, M50, M19, DT-041, MD-042, MD-043, MD-041, SP-004, SP-005, SP-006, SP-020, SP-022, SP-023]
priority: P1
wave: W5
bilingual: yes
bn_counterpart: SP-021_SOP_Payroll_Run_and_Statutory_Filing_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M56_Payroll_Benefits_and_Statutory_Compliance.md — prepare, approve and release are three distinct permissions; no user may hold two for the same run (SOD-03 and SOD-29)
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §10 BRU-HRM-02, BRU-HRM-05, BRU-HRM-06, BRU-HRM-07; §12.4 AUT-045, AUT-046
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-059 payroll processing time 3 days baseline, KPI-060 payroll corrections per run
    verified: 2026-08-15
    class: P1
  - source: Bangladesh Labour Act 2006 — section 108 overtime allowance at twice the ordinary rate of basic wage and dearness allowance; wages payable before the end of the seventh day after the wage period; section references and current amendments to be confirmed by Legal Counsel against the consolidated Act
    verified: 2026-08-15
    class: P2
  - source: ISO 9001:2015 clause 7.1.2 people, and clause 5.3 assigned responsibilities and authorities
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Payroll Run and Statutory Filing

| Item | Value |
|---|---|
| SOP ID | `SP-021` |
| Process owner | Chief Financial Officer and HR Manager (R30), jointly |
| Roles performing | `R31` HR Officer (prepare) · `R30` HR Manager (approve) · CFO (approve) · `R26` Finance Manager (release) · Tax Lead |
| Systems used | `P03` HR console (`UI-030`) and Finance console (`UI-029`) · `M56` · `M55` · `M50` |
| Frequency / volume | Monthly, for 500+ employees across 51+ sites and multiple legal entities |
| ISO 9001 clause reference | 7.1.2 people · 5.3 assigned authorities · 7.5.3 documented information |

> ⚠ **Class A — statutory content.** Wage payment timing, overtime rates and statutory deductions
> carry legal consequence under Bangladesh employment and tax law. The statutory citations here
> are drawn from secondary sources and are marked **class P2**. **Legal Counsel and external
> verification are required before this file leaves `Draft`** — action O-01 in §14.

---

## 1. Purpose and Outcome

**Purpose.** To pay every employee the right amount, on time, with the correct statutory
deductions made and remitted, and with the preparation, approval and release of the payment held
by three different people.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Attendance was verified and locked before the run | `BRU-HRM-05` — hard block |
| Overtime was pre-approved before it counted | `BRU-HRM-02`, `SOD-27` |
| The run carried two approvals — HR Manager and CFO | `BRU-HRM-06` |
| The bank file was released by neither the preparer nor the approver | `SOD-03`, `SOD-29` |
| Every employee received a compliant payslip | `DT-041` |
| Statutory deductions were computed, remitted and filed on time | Filing acknowledgements |
| Payroll data was visible only to the employee and to HR/Finance | `BRU-HRM-07` |
| Corrections per run below 0.5% | `KPI-060` |

---

## 2. Scope

**Applies to:** the monthly payroll run for all employees of every legal entity in `MD-002` —
input collection, validation, calculation, approval, disbursement, payslip issue, statutory
deduction and filing, and post-run corrections.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Attendance capture, roster and exception regularisation | `SP-022` |
| Recruitment, onboarding and leaver processing | `SP-023` |
| Incentive calculation | `M57`; **`M57` calculates, only `M56` pays** (`SOD-30`) |
| Vendor and contractor payments | `SP-017` |
| Employee expense reimbursement | `SP-004` A-39/A-40 |
| Financial period close and payroll journal posting | `SP-020` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Input cut-off | The date after which no further payroll input is accepted for the run |
| Attendance lock | The point at which the attendance period is verified and frozen (`BRU-HRM-05`) |
| Prepare / approve / release | Three distinct permissions; no user holds two for one run (`SOD-03`, `SOD-29`) |
| BEFTN | The bank disbursement file format |
| Payroll element | A configured earning, deduction or employer contribution (`MD-043`) |
| Off-cycle | A payment outside the normal run — final settlement, correction, statutory requirement |
| Variance check | Comparison of the run to the prior run, employee by employee and in total |
| Statutory deduction | Income tax at source, provident fund, and any other legally required withholding |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Verified and locked attendance | `SP-022`, `M55` | **Payroll cannot be finalised until attendance is verified and locked** (`BRU-HRM-05`) |
| Approved overtime | `SP-022` | Pre-approved before it counts (`BRU-HRM-02`) |
| Approved leave | `M55` | Unpaid leave and encashment resolved |
| Joiners, leavers and changes | `SP-023`, `M21` | Effective-dated; retrospective changes approved (`SOD-26`) |
| Payroll element configuration | `MD-043` | Statutory rates current for the tax year |
| Bank details verified | `M21` | A change of employee bank details is verified independently, like a vendor change (`SOD-40` pattern) |
| Working pattern and calendar | `MD-042`, `MD-041` | Shift, overtime and holiday rules resolved |
| Incentive file | `M57` | Calculated in `M57`, imported for payment only (`SOD-30`) |

---

## 5. Procedure

### 5.1 Input and cut-off

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | R30 | Publish the payroll calendar for the year: cut-off, approval, release and pay dates | `P03` | Calendar issued |
| 2 | R31 | Collect inputs: joiners, leavers, changes, unpaid leave, deductions, one-time payments | `P03` | Input register |
| 3 | R31 | Confirm attendance is verified and locked for the period | `M55` | Attendance lock |
| 4 | R31 | Confirm every overtime hour carries a pre-approval (`BRU-HRM-02`) | `M55` | Overtime approvals |
| 5 | R31 | Import the incentive file from `M57`; **do not recalculate it in payroll** (`SOD-30`) | `M56` | Incentive import |
| 6 | R31 | Close the input cut-off. Late inputs go to the next run or to an approved off-cycle | `P03` | Cut-off applied |

### 5.2 Calculate and validate

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 7 | System | Calculate gross, deductions, employer contributions and net (`AUT-045`) | `M56` | Calculated run |
| 8 | R31 | Run the validation pack: negative net, zero net, missing bank details, duplicate accounts, employees paid twice, leavers paid, joiners unpaid | `P03` | Validation report |
| 9 | R31 | Run the **variance check** against the prior run — by employee and in total. Investigate every material change | `P03` | Variance report |
| 10 | R31 | Reconcile headcount: employees paid = active employees ± joiners and leavers | `M21` | Headcount reconciliation |
| 11 | R31 | Verify statutory deductions against the current rates in `MD-043` | `M51` | Statutory check |
| 12 | R31 | Submit for approval. **The preparer's role ends here** | `P03` | Submission |

### 5.3 Approve and release — the three-way separation

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 13 | R30 HR Manager | Review and approve — headcount, changes, exceptions, variance explanations (`BRU-HRM-06`) | `P03` | HR approval |
| 14 | CFO | Review and approve — total cost, variance, statutory position (`BRU-HRM-06`) | `P03` | Finance approval |
| 15 | **R26 Finance Manager — neither preparer nor approver** | Generate and release the BEFTN file (`AUT-046`, `SOD-03`, `SOD-29`) | `M50` | Bank file released |
| 16 | R26 | Confirm the bank's acceptance and the value released matches the approved run **exactly** | `M50` | Bank confirmation |

### 5.4 Distribute and post

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 17 | System | Distribute payslips (`DT-041`) to each employee's own record only (`BRU-HRM-07`) | `M56` | Payslip distribution |
| 18 | System | Post the payroll journal to the ledger | `M19` | Journal posting |
| 19 | R27 | Reconcile the bank debit to the payroll journal and to the released file | `M50` | Reconciliation |
| 20 | R30 | Confirm every employee was paid. **An unpaid employee is an emergency, not a next-run item** | `P03` | Payment confirmation |

### 5.5 Statutory deduction and filing

| Step | Who | Action | Governed by | Evidence produced |
|---:|---|---|---|---|
| 21 | Tax Lead | Compute the statutory withholdings for the period from the approved run | `MD-043`, `M51` | Withholding schedule |
| 22 | Tax Lead | Remit the withholdings by the statutory date | `M50` | Remittance record |
| 23 | Tax Lead | File the required statutory returns and retain the acknowledgements | `M51` | Filing acknowledgements |
| 24 | R30 | Remit and file provident fund and any other statutory contribution per its own instrument | `MD-043` | Contribution record |
| 25 | Tax Lead | Issue employee tax certificates on the statutory cycle | `DT-041` variant | Certificates issued |
| 26 | R30 | Reconcile the year-to-date position per employee before the tax-year close | `M56` | YTD reconciliation |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 3 | Attendance not verified and locked | **The run does not proceed** (`BRU-HRM-05`, hard block). Escalate to the branch managers who owe the verification | R30 → R05 |
| 4 | Overtime recorded without pre-approval | It does not enter the run (`BRU-HRM-02`). Where the work genuinely happened, retrospective approval is a documented exception reviewed by R30, not a routine | R30 |
| 6 | Input arrives after cut-off | Next run, or an approved off-cycle. **A moved cut-off is a moved deadline for everyone** | R30 |
| 8 | Validation exception found | Resolve before submission. A known exception carried into approval transfers the error to the approver | R31 |
| 9 | Variance beyond tolerance and unexplained | **Hold the run** (`SP-005` PE-E4). An unexplained payroll variance is either an error or a fraud | R30 + CFO |
| 10 | Headcount does not reconcile | Do not proceed. Someone is being paid who should not be, or not paid who should | R30 |
| 13/14 | An approver is unavailable | Delegation per `SP-004` §4.6; **the two approvals may not collapse into one** (`BRU-HRM-06`) | Per DL-03/DL-08 |
| 15 | Only the preparer or an approver is available to release | **The release waits.** `SOD-03` and `SOD-29` have no compensating control | CFO |
| 16 | Released value differs from the approved run | Stop the payment if possible; investigate immediately as a potential diversion | CFO + Internal Audit |
| 20 | An employee was not paid | Off-cycle payment the same day where possible; this is a wage-payment obligation, not an administrative correction | R30 + CFO |
| 20 | An employee was overpaid | Do not deduct unilaterally from the next run. Take legal advice on recovery — deduction from wages is legally constrained | Legal Counsel + R30 |
| 22 | Statutory remittance date at risk | Escalate immediately; late remittance carries penalty and interest | CFO |
| — | A payroll record is accessed by a peer or a line manager below HR Manager | Blocked (`BRU-HRM-07`); treated as a privacy incident | CTO + DPO |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Payroll run | Any | R30 HR Manager **+** CFO — two approvals (`BRU-HRM-06`, `SP-004` A-55) | Delegation per DL-03; never collapsed to one |
| Bank file release | Any | A third person — R26 Finance Manager (`SP-004` A-56, `SOD-03`, `SOD-29`) | CFO, if CFO was not an approver of this run |
| Off-cycle payment | ≤ BDT 100,000 | R30 + R26 | CFO |
| Off-cycle payment | > BDT 100,000 | CFO | CEO |
| Retrospective overtime approval | Any | R30, as a documented exception (`SOD-27`) | CFO |
| Retrospective effective-date change to an employee record | Any | R30, not the processor (`SOD-26`, `SP-004` A-60) | CFO |
| Salary structure for a newly created record | Any | Not the record creator (`SOD-25`, `SP-004` A-61) | CFO |
| Incentive payment outside the calculated schedule | Any | CFO (`SP-004` A-63, `SOD-30`) | CEO |
| Recovery of an overpayment from wages | Any | Legal Counsel + R30 | CFO |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Input cut-off missed by a business unit | Escalate the same day (`SP-005` PE-E3); the run date does not move for one unit | R30 → CFO | Payroll exception log |
| Variance beyond tolerance | **Run held** (`SP-005` PE-E4) until explained | R30 + CFO | Variance record |
| Employee not paid | Off-cycle the same day; apologise; record the cause | R30, CFO | Payroll incident |
| Employee overpaid | Legal advice before any recovery; record the amount and the plan | Legal, R30 | Recovery record |
| Bank rejects the file | Identify the rejected records, correct, and re-release **through the same three-way path** | R26, R30 | Rejection log |
| Bank details changed shortly before the run | Verify independently before releasing. Late bank-detail changes are a known diversion pattern | R30 + R26 | Verification record |
| Duplicate payment to one employee | Stop, recover, and investigate as a control failure | CFO, Internal Audit | Duplicate register |
| Statutory rate changed mid-year | Update `MD-043` with the effective date; recompute affected runs on advice | Tax Lead, Legal | Rate change record |
| Payroll data disclosed to an unauthorised person | **L4-direct: CTO + DPO + R30**, restricted | As stated | Privacy incident (`LG-009`) |
| Suspected payroll fraud | **L4-direct: CFO + Internal Audit**, restricted; the local manager may be the subject | As stated | Restricted record |

---

## 9. Manual Fallback

Wages must be paid whether or not a system is available. Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Payroll is calculated from the **controlled payroll workbook** held by Finance, seeded from the last completed run and adjusted for known changes |
| 2 | The three-way separation is preserved on paper: prepared by R31, approved by R30 and CFO on the printed run summary, released by R26. **This separation does not relax during an outage** |
| 3 | The bank file is prepared as a manual schedule and submitted through the bank's alternate channel with dual authorisation |
| 4 | Payslips are issued manually from the workbook, carrying the same statutory content as `DT-041` |
| 5 | Statutory computation and remittance proceed on the statutory date regardless of system availability |
| 6 | **Back-enter the full run within 5 business days**, reconciling to the amounts actually paid |
| 7 | CFO signs the manual run pack; Internal Audit reviews it |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Attendance verified and locked before finalisation | Preventive (`BRU-HRM-05`) | Per run | Hard block |
| Overtime pre-approved before it counts | Preventive (`BRU-HRM-02`) | Per record | Hard block |
| Two approvals — HR Manager and CFO | Preventive (`BRU-HRM-06`) | Per run | Hard block |
| Prepare, approve and release held by three people | Preventive (`SOD-03`, `SOD-29`) | Per run | Hard block |
| Overtime requester cannot approve | Preventive (`SOD-27`) | Per record | Hard block |
| Attendance verifier cannot regularise above threshold | Preventive (`SOD-28`) | Per period | Threshold block |
| Employee record creator cannot approve the salary structure | Preventive (`SOD-25`) | Per record | Hard block |
| Retrospective change processed and approved by different people | Preventive (`SOD-26`) | Per change | Hard block |
| `M57` calculates, only `M56` pays | Preventive (`SOD-30`) | Per run | Hard block at assignment |
| Payroll visibility limited to the employee and HR/Finance | Preventive (`BRU-HRM-07`) | Continuous | Record rules |
| Variance check against the prior run | Detective | Per run | Variance report |
| Headcount reconciliation | Detective | Per run | Reconciliation |
| Bank debit reconciled to the released file and the journal | Detective | Per run | Reconciliation |
| Statutory filing timeliness | Detective | Per period | Filing acknowledgements |
| Corrections per run | Detective | Monthly | `KPI-060` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Prepare the payroll | Approve it (`SOD-03`) | Hard block | **None. The run waits** |
| Approve the payroll | Release the bank file (`SOD-29`) | Hard block | **None. The release waits** |
| Request overtime | Approve it (`SOD-27`) | Hard block | — |
| Verify an attendance period | Regularise its exceptions above the threshold count (`SOD-28`) | Threshold block | Regularisation routes to R30 |
| Create an employee record | Approve that employee's salary structure (`SOD-25`) | Hard block | — |
| Process a retrospective effective-date change | Approve it (`SOD-26`) | Hard block | — |
| Calculate an incentive (`M57`) | Disburse it (`M56`) (`SOD-30`) | Hard block at assignment | — |

> Seven controls, two of which have **no** compensating alternative. Payroll is the process where
> the programme accepts a delay rather than a weakened control.

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-059` | Payroll processing time | 3 days | 6 h; stretch < 4 h |
| `KPI-060` | Payroll corrections per run | unmeasured | < 0.5%; stretch < 0.3% |
| `KPI-061` | Attendance capture completeness | manual | 98%; stretch 99% |
| `KPI-065` | Employee self-service adoption | 0% | 75%; stretch 85% |
| Employees unpaid on the pay date | Count per run | untracked | **Zero** |
| Statutory remittances made on time | Timeliness | untracked | 100% |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-041` Payslip and Salary Certificate | Issued at step 17 |
| `DT-042` HR Letter Template Set | Employment documentation |
| `UI-030` Workspace — HR Console Copy | The screens used |
| [`SP-022_SOP_Time_Attendance_and_Roster.md`](SP-022_SOP_Time_Attendance_and_Roster.md) | Supplies the locked attendance |
| [`SP-023_SOP_Recruitment_and_Onboarding.md`](SP-023_SOP_Recruitment_and_Onboarding.md) | Joiners, leavers and record changes |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](SP-020_SOP_Month_End_and_Year_End_Close.md) | Payroll journal and accrual |
| [`../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | `SOD-03`, `SOD-25`…`SOD-30` |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md) | Elements and statutory rates |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-042_Shift_Roster_and_Working_Pattern_Master.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-042_Shift_Roster_and_Working_Pattern_Master.md) | Working patterns and overtime rules |
| `TR-015` Course Pack — HR and Payroll | Trains this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | CFO and HR Manager (pending) — statutory elements pending external verification |

**Open items**

| # | Item | Owner | Needed by |
|---|---|---|---|
| O-01 | **Verify every employment and tax citation against the enacted instruments.** Overtime at twice the ordinary rate and the seven-day wage-payment limit are cited here from secondary commentary (class **P2**); `CG-012` requires a primary source for a Class A file. Current amendments to the Bangladesh Labour Act 2006 and the applicable income-tax withholding rules must be confirmed | Legal Counsel + Tax Lead + external verifier | **Before `Approved`** |
| O-02 | Confirm the provident fund and any other statutory contribution obligations applicable to each legal entity, and record them in `MD-043` | HR Manager + Legal Counsel | Before W5 |
| O-03 | Confirm the legal constraints on recovering an overpayment by deduction from wages | Legal Counsel | Before W5 |
| O-04 | Set the payroll variance tolerance from the `SP-002` baseline | CFO | Before W5 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] The three-way prepare/approve/release separation is stated as having **no** compensating control
- [x] Variance check and headcount reconciliation specified as run-holding gates
- [x] Overpayment recovery routed to legal advice rather than unilateral deduction
- [x] Manual fallback preserves the three-way separation and the statutory dates
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **O-01 statutory citations verified against the enacted instruments — outstanding; blocks `Approved` for this Class A file (`CG-007`, `CG-012`)**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded with external verification — **pending CFO and HR Manager**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
