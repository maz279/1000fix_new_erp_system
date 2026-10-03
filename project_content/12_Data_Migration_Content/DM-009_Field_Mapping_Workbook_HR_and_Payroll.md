---
id: DM-009
title: Field Mapping Workbook — HR and Payroll
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration with HR
author: Data Migration analysts with the HR Operations Manager
reviewers: [HR Director, CFO, Tax Manager, Legal Counsel, Chief Data Officer, Security Lead, QA Lead]
approver: HR Director with CFO
content_class: C
purpose: >
  Maps employee records, employment contracts, organisation structure, salary structures, leave
  balances, competencies and year-to-date payroll balances to the ERP people model, under the
  strictest correctness constraint in the programme. Year-to-date tax, provident-fund and gratuity
  balances cannot be recomputed after the fact: if they are wrong at cutover every subsequent
  calculation compounds the error and the year-end tax certificate is wrong for every employee.
traces_to: [M21, M56, M55, M22, M57, M58, MD-012, MD-008, MD-009, MD-010, MD-011, MD-042, MD-043, MD-035, DM-001, DM-002, DM-003, DM-004, DM-008, DM-011, DM-013]
priority: P1
wave: W5
bilingual: no
bn_counterpart: n/a
data_file: DM-009_Field_Mapping_HR_and_Payroll.xlsx
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M56 §16.4 — migration warning, the most dangerous in the programme; year-to-date balances must be exact; cutover at the start of an assessment year if at all possible; otherwise reconcile employee by employee with sign-off from both HR Director and CFO before the first live run
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M21 §16.4 — the service book should be opened with a single verified opening entry stating service from the joining date; a fabricated service history is worse than an honest opening balance in a Labour Act dispute
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M55 §16.4 and M22 §16.4 — opening leave balances agreed with each employee before cutover, not imported and announced; there is no existing skill matrix to migrate and the initial matrix must be constructed through supervisor assessment of 500+ employees
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-012_Employee_Master_Data_Template.md §2 — employee record structure with S0–S3 sensitivity per field; nid, tin, passport, biometric reference and bank details all Bangladesh-resident
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md §2 and §2.1 — element structure, is_taxable, is_pf_applicable, is_gratuity_applicable, statutory_reference, G6 verification, and the tax slab sub-register loading inactive until G6
    verified: 2026-08-18
    class: P1
  - source: Bangladesh Labour Act 2006 with the Bangladesh Labour Rules 2015 — the service book date of birth is conclusive proof of a worker's age; gratuity accrues at not less than thirty days' wages at the last drawn rate for every completed year of service
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# DM-009 — Field Mapping Workbook: HR and Payroll

> Governs `DM-009_Field_Mapping_HR_and_Payroll.xlsx`. The markdown governs; the workbook loads.
>
> **Template conformance note.** As `DM-004`: `TPL_Master_Data_Specification.md` retained in full;
> the `CG-009` source-to-target column set is inherited from `DM-004` §2.1 (`CP-01`).
>
> **Identifier note (`CG-005` §3.3).** `DM-009` is a **content** identifier; `05-02` `DM-14`
> (modelling standard — sensitive data classified S0–S3) is cited with its document prefix.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | People, payroll and statutory employment records |
| Owning module | `M21` HCM; `M56` PAY; `M55` WFM; `M22` LMS |
| Data steward | HR Operations Manager |
| Golden source | This mapping; sources `SRC-013`, `SRC-014`, `SRC-015`, `SRC-030`, `SRC-038` |
| Refresh cadence | Once at cutover; **YTD balances never re-run without dual approval** (`SQ-06`) |
| Environments | Dev · SIT · UAT · Prod — **every non-production environment masked**; `S3` fields never present unmasked in any region (`NFR-086c`) |
| Content class | C — Operational-critical *(with statutory consequence at the `M56` boundary)* |
| Effective-dated | Service, salary and leave records are effective-dated |
| **Build wave** | **W5** *(the register wave — `MS-22`)* |
| **Load wave** | **W5** — `M21`, `M55`, `M56`, `M22` §16.4 and `06-01` W5 |

**Consequence of absence (`CP-03`).** `M56` §16.4 carries the strongest warning in the module set:

> *"**Migration warning — the most dangerous in the programme.** **Year-to-date balances must be
> exact.** If year-to-date tax, PF or gratuity balances are wrong at cutover, every subsequent
> calculation compounds the error, and the year-end tax certificate will be wrong for every
> employee."*

Three things make this different from every other migration in Category 12:

| Property | Why it changes the approach |
|---|---|
| **Irreversibility** | A YTD figure cannot be recomputed from source — the source is an Excel workbook maintained monthly with manual tax (BRD §6.1) |
| **Per-person visibility** | 500+ employees each receive a payslip and a tax certificate. An error is not an aggregate variance; it is 500 individual disputes |
| **Statutory exposure** | Under the Labour Act 2006 the service book's recorded date of birth is conclusive proof of age; gratuity accrues on completed years of service. A fabricated history is a liability, not a convenience |

Additionally, `G5-01` requires the **first payroll run processed, validated and paid with zero
errors**, and `G5-02` requires the **BEFTN file accepted by the bank without rework**. Both are
gate criteria at month 22 and both depend entirely on what this workbook loads.

---

## 2. Record structure

Target structures are `MD-012` §2 (employee master) and `05-02` §6 (`M21` — 21 entities). Not
restated (`CP-01`). Mapping column set: `DM-004` §2.1.

### 2.1 The four HR origins

**`HP-01`: every people figure carries an `origin` and the confirmation it requires.**

| `origin` | Population | Confirmation required | Signed by |
|---|---|---|---|
| **`document_verified`** | Employee identity, contract, join date, NID, bank details | **Against the physical document in the personnel file** | HR Operations Manager |
| **`employee_agreed`** | **Leave balances**, outstanding advances | **Agreed with the individual employee before cutover** | The employee, and HR |
| **`reconciled_balance`** | **YTD tax, PF, gratuity** | **Reconciled employee by employee** | **HR Director and CFO, jointly** |
| **`constructed`** | Competency matrix, skill profiles | Supervisor assessment | Line supervisor with HR |

> **`HP-02`.** There is no `extracted` origin for anything an employee will see on a payslip. The
> Excel payroll workbook is an **input to** the reconciliation, not the reconciled balance —
> the same distinction `DM-008` `FO-02` makes for the trial balance, and for the same reason.

> **`HP-03` — leave balances are agreed, not announced.** `M55` §16.4: *"Opening leave balances must
> be **agreed with each employee before cutover**, not imported and announced. A disputed opening
> balance is the fastest way to lose staff confidence in the whole system."* At W5 the platform is
> being rolled out to all 51+ centres; the first thing 500+ people will check is their leave
> balance.

### 2.2 Map A — `hr.employee` core

Target columns are `MD-012` §2. Sensitivity classes are taken from that file, not re-derived.

| Source field *(typical)* | `SRC` | Target | Transform | Sens |
|---|---|---|---|:--:|
| `Emp ID` / `Staff No` | `SRC-013` | `employee_code` | **`H-01`** — legacy code retained as `legacy_record_id`; a new `EMP-nnnn` is allocated per `MD-012`. Where the legacy code is already unique, stable and understood by staff, it may be adopted — **a decision, recorded, not a default** | S0 |
| `Name` | `SRC-013`, `SRC-030` | `full_name_en` | **As on the NID** (`MD-012`), verified against the personnel file — not as typed in the spreadsheet | S1 |
| `Name (Bangla)` | `SRC-030` | `full_name_bn` | **As on the NID, Bengali script**; encoding conversion first (`DM-004` §2.5) | S1 |
| `DOB` | `SRC-030` | `date_of_birth` | **`H-02`** — `document_verified` only. Under the Labour Act 2006 the service-book date of birth is **conclusive proof of age**; a transcription error becomes a legal fact | S2 |
| `NID` | `SRC-030` | `nid_number` | **`T-08` deferred step** — resident store only (`NFR-086`, `MS-21`) | **S3** |
| `TIN` | `SRC-014` | `tin_number` | `T-08` deferred | **S3** |
| `Mobile` | `SRC-013` | `mobile` | `T-01` (`DM-004`) — this is the OTP channel | S2 |
| `Join Date` | `SRC-030` | `join_date` | `document_verified`. **Drives gratuity, service book and probation** | S0 |
| `Confirmation Date` | `SRC-030` | `confirmation_date` | `document_verified` | S0 |
| `Designation` | `SRC-013` | `position_code` → `MD-008` | `T-05`; **unmapped designations escalate, they do not default** | S0 |
| `Role` / function | `SRC-013` | `role_code` → `MD-009` | `T-05` | S0 |
| `Branch` | `SRC-013` | `branch_code` → `MD-003` | `T-05` | S0 |
| `Type` | `SRC-013` | `employment_type` | permanent / contract / temporary | S0 |
| `Bank A/C`, `Routing` | `SRC-014` | `bank_account_no`, `bank_routing_no` | **`HP-04`** — `document_verified` **and** re-verified before the first BEFTN run | **S3** |
| `PF No` | `SRC-014` | `pf_membership_no` | `document_verified` | S2 |
| Present / permanent address | `SRC-030` | `present_address_id`, `permanent_address_id` → `MD-007` | Via `DM-004` Map C | S2 |
| Emergency contact | `SRC-030` | `emergency_contact_name`, `_phone` | Required at target (`MD-012`) | S2 |
| `Blood Group` | `SRC-030` | `blood_group` | **Field-safety relevant** (`MD-012`) — carried where recorded | S2 |
| Biometric template | — | `biometric_template_ref` | **Not migrated.** `M55` templates are enrolled fresh; **templates are never exported** (`05-02` §10) | **S3** |
| *(control)* | — | `legacy_source_system`, `legacy_record_id`, `migration_batch_id` | `MS-18` | S0 |

> **`HP-04` — bank details carry the `DM-008` `FO-09` treatment.** A migrated employee bank account
> is `unverified` until confirmed against the document **and** re-verified before the first BEFTN
> file is generated. `G5-02` requires the BEFTN file accepted by the bank **without rework**; a
> rejected line is a person who is not paid.

### 2.3 Map B — the service book

`M21` §16.4 gives an unusual instruction and it is adopted verbatim:

> *"Historical service records are likely incomplete. The service book should be opened with a
> **single verified opening entry** stating service from the joining date, rather than a
> reconstructed history that cannot be evidenced. **A fabricated service history is worse than an
> honest opening balance in a Labour Act dispute.**"*

| Rule | Detail |
|---|---|
| **`HP-05`** | **One** `fix.service.book` opening entry per employee: joining date, current position, current grade, as-at date, and the statement that prior detail is not evidenced |
| Prohibited | Reconstructed promotion, transfer or grade history from spreadsheets or memory |
| Permitted | Documented events **where the document exists in the personnel file** — an appointment letter, a promotion letter — loaded individually with the document attached |
| Gratuity | Accrues from `join_date`; the opening provision is `reconciled_balance` (§2.5), not derived from a reconstructed history |

### 2.4 Map C — leave

| Source | Target | Rule |
|---|---|---|
| Leave balance spreadsheets (`SRC-015`) | `fix.leave.entitlement` opening | **`HP-03`** — `employee_agreed`. A balance the employee has not agreed does **not** load |
| Leave policy documents | `fix.leave.type` | Authored into `MD-042`/`M55` configuration, not migrated as data |
| Public holiday calendar | `fix.holiday.calendar` | From the gazette (`SRC-042`), current and next year |
| **Historical attendance** | — | **Not migrated** (`L`) — *"sign-in books are not machine-readable and not reliable"* |
| Shift patterns and rosters | — | **Authored** (`N`) — none exist in structured form |

> **`HP-06`.** Agreement must be **recorded per employee**, with a date, and retained. "HR sent the
> balances round and nobody objected" is not agreement, and it will not survive the first dispute.

### 2.5 Map D — year-to-date payroll balances

**The most constrained mapping in Category 12.**

| Balance | Target | Rule |
|---|---|---|
| YTD gross, per element | `fix.payroll.balance` | Per `MD-043` element, **element by element** — not a single gross figure |
| YTD tax deducted | `fix.payroll.balance` (tax) | **`HP-07`** — reconciled per employee to the deposited challans; a difference is resolved before load |
| YTD PF — employee and employer | `fix.pf.ledger` | Reconciled to the PF trustee's records, not only to the payroll workbook |
| Gratuity opening provision | `fix.gratuity.accrual` | Computed from `join_date` and last drawn wage per the Labour Act basis; **agreed with Finance** |
| Outstanding loans and advances | `fix.loan` | `employee_agreed` — each acknowledged in writing (`M52` applies the same rule to advances) |
| Investment declarations, current year | `fix.investment.declaration` | Current year only |
| **Historical payslips** | — | **Not migrated** (`L`); retained as `M24` documents where they exist |

> **`HP-08` — cutover at the start of an assessment year, if at all possible.** `M56` §16.4 states
> it as the preferred mitigation. Bangladesh's income-tax assessment year begins in July, and W5 is
> months 19–22 of the programme. **Whether the W5 cutover lands at an assessment-year boundary is a
> planning decision nobody has taken**, and it is the difference between loading a zero YTD position
> and reconciling 500+ mid-year balances. Recorded as `O-01`.
>
> If mid-year cutover is unavoidable: **reconcile employee by employee and obtain sign-off from both
> the HR Director and the CFO before the first live run** (`HP-01` `reconciled_balance`).

> **`HP-09` — no reload.** `DM-003` `SQ-06` makes YTD balances `never_reload`. A correction after
> the first live payroll run is an **adjustment posted through payroll**, with an audit trail — never
> a silent re-load of the opening position.

### 2.6 Map E — salary structure and payroll elements

| Source | Target | Rule |
|---|---|---|
| Salary structures (500+) | `fix.salary.structure` | Mapped to `MD-043` elements; **an element with no `MD-043` equivalent is created in `MD-043` first**, never invented inside a salary structure |
| Element amounts | Structure lines | `05-02` `DM-07` monetary with explicit `BDT` |
| Tax slabs | `MD-043` §2.1 sub-register | **Loaded `active = FALSE` until G6 verification is recorded** (`MD-043`). Migration does not activate them |
| `is_taxable`, `is_pf_applicable`, `is_gratuity_applicable` | From `MD-043` | **Never inferred from the legacy workbook's formulas** — the workbook is the thing being replaced |
| GL posting accounts | `MD-043` `gl_account_code` → `MD-035` | Requires the `DM-008` chart to be loaded first |

> **`HP-10`.** The legacy Excel payroll contains embedded formulas that encode the current
> interpretation of tax and PF rules. Those formulas are **evidence of current practice, not a
> specification**. `MD-043` carries `statutory_reference`, `verified_by` and `verified_on` as G6
> evidence precisely so that the new system's rules are traceable to law rather than to a
> spreadsheet. Copying the formula forward would import an unverified interpretation into a
> statutory calculation.

### 2.7 Map F — competency and certification

| Source | Target | Rule |
|---|---|---|
| Existing certificates, physical or scanned (`SRC-030`) | `fix.employee.certification` + `M24` document | **Only where the certificate exists.** Long lead time (`M22` §16.4) |
| Brand certification lists from principals | `fix.employee.certification` | Confirmed by the brand, per `MD-011` |
| **Supervisor knowledge** (`SRC-038`) | `fix.employee.competency` | **`constructed`** — *"the hard one"*. **500+ employees × every relevant competency**, by supervisor assessment |
| Training records where any exist | `fix.enrolment` history | Best-effort |

> **`HP-11` — the competency matrix is not a migration.** `M22` §16.4: *"There is no existing skill
> matrix to migrate. The initial matrix must be **constructed** … For 500+ employees this is a
> substantial exercise with a long lead time, and it must start well before W5."*
>
> It appears in this workbook because **`BRU-SRM-09` blocks assignment of a service order to a
> technician lacking current certification for that brand's warranty work**, and `G5-03` requires
> *zero uncertified technicians assignable to brand warranty work*. An empty competency matrix at W5
> either blocks all warranty dispatch or forces the rule to be disabled. `MD-011` exists for this;
> the data to fill it does not.

### 2.8 What is not migrated

| Not migrated | Disposition | Reason |
|---|---|---|
| Historical attendance | `L` | Sign-in books not machine-readable or reliable |
| Historical payslips | `L` | Retained as `M24` documents only |
| Historical appraisal records | `L` *(optional reference)* | Variable quality |
| Historical KPI baselines | `L` | Accumulated from live data, not migrated |
| **Historical job applications** | **`P` purge** | **Personal data with no lawful retention basis and no consent on record** (`M58` §16.4, PDPA 2026) |
| Biometric templates | `N` | Enrolled fresh; templates are never exported |
| Shift patterns and rosters | `N` | Authored; none exist in structured form |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `employee_code` (`EMP-nnnn`), permanent (`MD-012`) |
| Alternate key | NID — **`S3`, resident store only**; used for verification, never as the join key in the regional store |
| Legacy key | `legacy_source_system` + `legacy_record_id` (`MS-18`) |
| Party linkage | Every employee is also a party with the `employee` role (`MD-013` §2.1, `DM-004` `T-07`) — **one party, two roles**, never two records |
| Reuse policy | `employee_code` is never reused, including after separation (`MD-012`) |
| Leaver handling | Leavers within the retention window load with `active = FALSE` and `leave_date`; records are archived, never deleted (`05-02` `DM-06`) |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `HP-01` | Every people figure carries an `origin` and the confirmation that origin requires | **H** | `ERR-HRP-001` |
| `HP-02` | No payslip-visible figure loads with `origin = extracted` | **H** | `ERR-HRP-002` |
| `HP-03` | A leave balance loads only where the employee's agreement is recorded | **H** | `ERR-HRP-003` |
| `HP-04` | Employee bank details load `unverified` and are re-verified before the first BEFTN run | **H** | `ERR-HRP-004` |
| `HP-05` | Exactly one opening service-book entry per employee; reconstructed history is rejected | **H** | `ERR-HRP-005` |
| `HP-06` | Employee agreement is recorded individually with a date; silence is not agreement | **H** | `ERR-HRP-006` |
| `HP-07` | YTD tax reconciles per employee to deposited challans before load | **H** | `ERR-HRP-007` |
| `HP-08` | Mid-year cutover requires joint HR Director and CFO sign-off per employee cohort before the first live run | **H** | `ERR-HRP-008` |
| `HP-09` | YTD balances are `never_reload`; corrections are payroll adjustments with an audit trail | **A** | `ERR-HRP-009` |
| `HP-10` | Legacy payroll formulas are never copied into element definitions; `MD-043` `statutory_reference` governs | **H** | `ERR-HRP-010` |
| `HP-11` | A competency record is `constructed` with a named assessing supervisor and date | **H** | `ERR-HRP-011` |
| `HP-12` | `date_of_birth` and `join_date` load only from the personnel document (`document_verified`) | **H** | `ERR-HRP-012` |
| `HP-13` | `S3` fields load only to the resident store, after verification (`NFR-086`, `MS-21`) | **H** | `ERR-HRP-013` |
| `HP-14` | Non-production environments hold no unmasked employee data in any region (`NFR-086c`) | **H** | `ERR-HRP-014` |
| `HP-15` | Biometric templates are never migrated or exported | **H** | `ERR-HRP-015` |
| `HP-16` | Historical job applications are purged, not migrated (`M58`, PDPA) | **H** | `ERR-HRP-016` |
| `HP-17` | Tax slabs load `active = FALSE` until G6 verification is recorded (`MD-043`) | **H** | `ERR-HRP-017` |
| `HP-18` | A certification loads only with its evidencing certificate or the brand's confirmation | **H** | `ERR-HRP-018` |
| `HP-19` | An unmapped designation escalates; it never takes a default position code | **H** | `ERR-HRP-019` |
| `HP-20` | One party, two roles — an employee is never a second party record | **H** | `ERR-HRP-020` |
| `HP-21` | Every loaded row carries the three control values (`MS-18`) | **H** | `ERR-HRP-021` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `MD-008` positions, `MD-009` roles | N:1 | Seed tier 3, **before** |
| `MD-012` employee template | 1:1 | The target structure |
| `MD-010` competencies, `MD-011` certifications | N:1 | Seed tier 8 |
| `MD-042` shift patterns, `MD-043` payroll elements and slabs | N:1 | Seed tiers 9 and 4 |
| `MD-035` chart of accounts | N:1 | Via `DM-008` — payroll elements post to GL accounts |
| `DM-004` party | N:1 | Tier `X1` — the employee party |
| `DM-008` finance | N:1 | **Tier `X7` before `X8`** — GL accounts must exist |
| The resident store (`NFR-086`) | — | **`S3` fields cannot load until it is verified** |

| Depended on by |
|---|
| `M56` first live payroll run · `G5-01`, `G5-02`, `G5-03` · `M02` dispatch certification enforcement (`BRU-SRM-09`) · `M57` incentive calculation · `TS-010` UAT scripts |

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | `SRC-030` personnel files (paper) · `SRC-013` HR spreadsheets · `SRC-014` Excel payroll · `SRC-015` leave spreadsheets · `SRC-038` supervisor knowledge |
| Who supplies it | HR Director; CFO for the payroll reconciliation; line supervisors for competency |
| Collection method | **Document verification against the physical personnel file** · per-employee agreement · per-employee reconciliation · structured supervisor assessment |
| Known quality issues | Service history *"likely incomplete"*; payroll maintained in Excel with manual tax on a 3-day cycle; leave balances disputed in practice; **no skill matrix exists at all** |
| Cleansing rules applied | `DM-011` |
| Re-verification | Parallel payroll run before the first live run; BEFTN pre-validation with the bank |

---

## 7. Volumes

| Population | Rows | Origin | Wave |
|---|---:|---|:--:|
| Employees | **500+** | `document_verified` | W5 |
| Employment contracts | 500+ | `document_verified` | W5 |
| Organisation units and positions | 51+ branches, all departments | Seed + mapping | W5 |
| Salary structures | 500+ | `document_verified` | W5 |
| Employee bank accounts | 500+ | `document_verified` → re-verified | W5 |
| **YTD payroll balances** | **500+ × every `MD-043` element** | **`reconciled_balance`** | **W5** |
| Leave balances | 500+ | **`employee_agreed`** | W5 |
| Outstanding loans and advances | Variable | `employee_agreed` | W5 |
| Gratuity opening provisions | 500+ | `reconciled_balance` | W5 |
| Certifications | Variable, evidence-gated | `document_verified` | W5 |
| **Competency assessments** | **500+ × relevant competencies** | **`constructed`** | **W5, long lead** |

> **The two large numbers here are not row counts, they are conversation counts.** 500+ leave
> agreements and 500+ supervisor competency assessments are each a person-to-person exercise. At ten
> minutes per leave conversation that is ~85 hours; the competency matrix is materially larger. The
> `06-01` allocation of 20% of a data owner's time through W1–W5 does not obviously contain either.

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add a mapping row | Migration analyst |
| Who may set `business_confirmed` | HR Operations Manager |
| Who may set `signed_off` | **HR Director with CFO** — jointly, for anything touching YTD balances |
| Approval required | CFO and HR Director for YTD; Tax Manager with the tax consultant for slab and element treatment; Legal Counsel for anything touching `S3` fields or the purge instruction |
| Effective dating | Service, salary and leave rows are effective-dated; the mapping is not |
| Archive rule | Records archived (`active = FALSE`), never deleted (`05-02` `DM-06`); employee records retained ten years after termination (BRD §11.7) |
| Logged in | `RF-006`; per-employee reconciliation and agreement evidence retained as `M24` documents |

---

## 9. Sample rows

```csv
map_id,source_id,source_field,source_type,source_example,target_entity,target_field,transform_rule,default_value,required_at_target,sensitivity,residency_restricted,dq_rule,unmapped_disposition,owner,status
HMAP-000601,SRC-030,Date of Birth,date,MASKED,hr.employee,date_of_birth,HP-12 document_verified against the personnel file; conclusive proof of age under the Labour Act 2006,,TRUE,S2,FALSE,DQ-HR-001,,HR Operations Manager,proposed
HMAP-000606,SRC-014,YTD Tax Deducted,decimal,MASKED,fix.payroll.balance,ytd_tax,HP-07 reconciled per employee to deposited challans; a difference is resolved before load; never_reload,,TRUE,S3,FALSE,DQ-HR-006,,CFO,proposed
HMAP-000611,SRC-015,Leave Balance,decimal,12.5,fix.leave.entitlement,opening_balance,HP-03 employee_agreed; loads only where the employee's dated agreement is recorded,,TRUE,S2,FALSE,DQ-HR-011,,HR Director,proposed
HMAP-000617,SRC-014,PF Formula,text,=Basic*0.10,,,HP-10 legacy formulas are evidence of practice not specification; MD-043 statutory_reference governs,,FALSE,S1,FALSE,,carried_to_legacy_payload,Tax Manager,proposed
HMAP-000622,SRC-038,Supervisor skill note,text,"strong on split AC, not board-level",fix.employee.competency,level_id,HP-11 constructed with a named assessing supervisor and date; never inferred from job title,,FALSE,S2,FALSE,DQ-HR-022,,HR Director,proposed
HMAP-000630,SRC-023,Historical application,record,MASKED,,,HP-16 purge disposition; no lawful retention basis and no consent on record,,FALSE,S3,TRUE,,dropped_with_reason,Legal Counsel,proposed
```

---

## 10. Migration notes

**Three Gate 5 criteria depend on this workbook.**

| Gate | Criterion | Served by |
|---|---|---|
| `G5-01` | First payroll run processed, validated and paid with **zero errors** | §2.5 YTD reconciliation and §2.6 element mapping |
| `G5-02` | BEFTN file accepted by the bank **without rework** | `HP-04` bank-detail verification |
| `G5-03` | **Zero uncertified technicians assignable to brand warranty work** | §2.7 — and it is the least ready |

**The honest position on `G5-03`.** `BRU-SRM-09` is a hard rule; `MD-011` is the register it
evaluates against; `M22` states that the competency matrix does not exist and must be constructed
for 500+ employees. If the matrix is incomplete at W5, the programme faces a choice between blocking
warranty dispatch (operationally unacceptable) and disabling a hard business rule (the exact failure
`AUDIT-001` §7 catalogued as *a specification assuming content that no workstream produces*). The
resolution is a **W3-start assessment programme**, not a W5 data load.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-012_Employee_Master_Data_Template.md`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-012_Employee_Master_Data_Template.md) | The target record structure and its S0–S3 classification |
| [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md) | Elements, slabs and the G6 verification gate |
| [`../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | The register `BRU-SRM-09` evaluates against |
| [`DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md`](DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md) | GL accounts payroll elements post to; the same `unverified` bank-account treatment |
| [`DM-004_Field_Mapping_Workbook_Party_and_Customer.md`](DM-004_Field_Mapping_Workbook_Party_and_Customer.md) | The employee party and the one-party-two-roles rule |
| [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) | The per-employee reconciliation HR and Finance sign |
| `M56` §16.4 · `M21` §16.4 · `M55` §16.4 · `M22` §16.4 · `M58` §16.4 | The migration positions implemented here |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Four HR origins, single opening service-book entry, leave agreed per employee, YTD reconciled per employee with joint sign-off and `never_reload`, legacy payroll formulas excluded from element definitions, competency matrix identified as a construction programme rather than a load | HR Director (pending) |

---

## 13. Open items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **Whether the W5 cutover lands at the start of an assessment year has not been decided.** `M56` names it as the preferred mitigation for *"the most dangerous migration in the programme"*. It is a scheduling decision with a per-employee correctness consequence, and it must be taken while W5 timing is still movable | HR Director with CFO and PMO | **W3 — while W5 timing is still movable** |
| **`O-02`** | **The competency matrix construction programme is not scheduled.** 500+ employees × relevant competencies by supervisor assessment, needed complete at W5 for `G5-03` and `BRU-SRM-09`. `M22` says it *"must start well before W5"*; nothing has started | HR Director with Service Ops Director | **W3 — start** |
| **`O-03`** | **500+ individual leave-balance agreements have no process or owner.** `HP-03` blocks the load without them, and W5 rolls out to all 51+ centres simultaneously | HR Operations Manager | **W5 minus 2 months** |
| **`O-04`** | **The `MD-043` G6 verification has not been performed.** Slabs load `active = FALSE` until it is; without it there is no payroll calculation at all, only a structure | CFO with Tax Manager and the tax consultant | **W5 minus 2 months** |
| **`O-05`** | **The resident store is unproven** (`ASM-21`, decision `D-13`). NID, TIN, passport and bank details are all `S3`. If the store is unavailable at W5, employees load without statutory identifiers and payroll cannot compute tax | CTO with Legal Counsel | **W5** |
| **`O-06`** | **PF balances must reconcile to the trustee's records, not only to the payroll workbook.** Whether trustee records exist in a reconcilable form is unknown and unprofiled | CFO with HR Director | **W5 minus 3 months** |
| **`O-07`** | **The `M58` purge instruction has no execution owner.** `HP-16` requires historical job applications destroyed rather than migrated; destruction of personal data needs a recorded, evidenced act. [`LG-009`](../10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md) and [`LG-012`](../10_Legal_Policy_and_Compliance/LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) now exist at `Draft` (written 2026-08-17), but **neither names who executes a pre-migration purge or what evidence it produces** | Legal Counsel with HR Director | W6 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; mapping column set inherited from `DM-004` §2.1 (`CP-01`)
- [x] Four HR origins defined, with `extracted` prohibited for anything payslip-visible
- [x] **`M56`'s warning implemented as hard rules** — per-employee reconciliation, joint sign-off, `never_reload`
- [x] Assessment-year cutover preference raised as a scheduling decision while it is still movable
- [x] **Single opening service-book entry adopted verbatim**, with the Labour Act reasoning stated
- [x] Leave balances made `employee_agreed` with recorded, dated individual agreement
- [x] Legacy payroll formulas excluded from element definitions, with `MD-043` `statutory_reference` governing
- [x] Competency matrix identified as a construction programme and bound to `BRU-SRM-09` and `G5-03`
- [x] Biometric templates and historical applications handled as `N` and `P`, not as migrations
- [x] `S3` handling, residency deferral and non-production masking stated as hard rules
- [x] Volumes expressed in conversations as well as rows, against the `06-01` allocation
- [x] Sample rows included, masked where `S2`+, and parse as CSV
- [x] Archive rule states records are archived, never deleted (`05-02` `DM-06`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] **`O-01` assessment-year cutover undecided**
- [ ] **`O-02` competency matrix unstarted — `G5-03` is not reachable without it**
- [ ] **`O-04` `MD-043` G6 verification not performed**
- [ ] Named approver recorded — **pending HR Director with CFO**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
