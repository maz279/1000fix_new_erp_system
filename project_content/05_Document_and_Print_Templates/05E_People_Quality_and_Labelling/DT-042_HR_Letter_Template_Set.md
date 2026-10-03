---
id: DT-042
title: HR Letter Template Set
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Human Resources with Legal & Compliance
author: Human Resources with Legal & Compliance and Content Design
reviewers: [Legal Counsel, HR Director, Finance, Internal Audit, Localisation Lead]
approver: Legal Counsel with HR Director
content_class: B
purpose: >
  Offer, appointment, confirmation, transfer, promotion, warning and exit/clearance letters. HR
  letters carry employment-law consequence; improvised wording across a 500-person workforce
  creates dispute exposure one letter at a time, and the letters that matter most are written
  under time pressure by the people least equipped to draft them.
traces_to: [M21, M58, M56, M57, DT-001, DT-041, LG-013, MD-008, MD-009, MD-012, MD-040, MD-043, BRU-SEC-06, BRU-HRM-07, BRU-DMS-03]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: DT-042_HR_Letter_Template_Set_BN.md
sources:
  - source: Bangladesh Labour Act 2006 — employment classification, notice, termination and service-benefit provisions. **All must be verified against the enacted text and the Labour Rules at G6**
    verified: 2026-08-15
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SEC-06 — a leaver's access is revoked within one hour of the leaver event
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-HRM-07 — payroll and personal records visibility restricted
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-042 — HR Letter Template Set

> ⚠ **Class B — legal.** Every letter in this set is approved by Legal Counsel **as a set**. An
> HR manager may select and populate; they may not draft.
>
> **The letters that create the most exposure are written under the most pressure.** A warning
> letter drafted at the end of a difficult day, a termination letter written to hit a deadline, a
> counter-offer letter written to keep someone — these are exactly the letters that end up being
> read aloud in a dispute.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | HR correspondence template set |
| Owning module | `M21` Core HR and Employee Lifecycle, with `M58` Talent Acquisition |
| Statutory | No prescribed forms. **Legally consequential under the Labour Act 2006** |
| Recipient(s) | The employee or candidate; HR file; the manager only where the letter is copied to them |
| Languages | **Bilingual — separate versions with a precedence clause.** Employment terms must be understood by the person bound by them |
| Output formats | A4 portrait on letterhead · PDF · e-signature (`M24`) · self-service portal |
| Numbering mask | `MD-040` — `HRL-{entity}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; **employment duration plus the limitation period** |

### 1.1 The set

| # | Letter | Trigger | Signed by | Legal sensitivity |
|---:|---|---|---|:--:|
| 1 | **Offer** | Selection decision | HR Manager | High |
| 2 | **Appointment** | Offer accepted | HR Director | **Very high** — it is the contract |
| 3 | **Confirmation** | Probation completed | HR Manager | Medium |
| 4 | **Probation extension** | Probation not passed | HR Manager | High |
| 5 | **Transfer** | Location or department change | HR Manager | Medium |
| 6 | **Promotion / re-grade** | Role change upward | HR Director | Medium |
| 7 | **Salary revision** | Pay change | HR Director | Medium |
| 8 | **Show-cause notice** | Alleged misconduct | HR Manager | **Very high** |
| 9 | **Warning — verbal record / written / final** | Disciplinary outcome | HR Manager | **Very high** |
| 10 | **Suspension pending enquiry** | Serious allegation | HR Director | **Very high** |
| 11 | **Enquiry outcome** | Disciplinary process concluded | HR Director | **Very high** |
| 12 | **Resignation acceptance** | Employee resigns | HR Manager | Medium |
| 13 | **Termination / dismissal** | Employer-initiated exit | **HR Director with Legal** | **Very high** |
| 14 | **Retrenchment / redundancy** | Role removed | **HR Director with Legal** | **Very high** |
| 15 | **Experience / service certificate** | On exit or request | HR Manager | Medium |
| 16 | **Clearance and final settlement** | Exit completion | HR Manager with Finance | High |

| # | Rule |
|---|---|
| **LS-01** | Letters 8–11, 13 and 14 — the disciplinary and exit set — **require Legal review of the populated letter**, not only of the template. Facts, not wording, are what makes these letters risky |
| **LS-02** | An HR manager may issue letters 1, 3, 5, 12 and 15 from the template without further review |
| **LS-03** | No letter is issued outside this set. A situation the set does not cover goes to Legal, and if it recurs it becomes template 17 |

---

## 2. Statutory Requirements

Not prescribed forms. Five constraints, all Labour Act 2006:

| Constraint | Source | Effect |
|---|---|---|
| Employment classification and its consequences | Labour Act 2006 — **pending G6** | Permanent, probationary, temporary, casual and apprentice carry different rights |
| Notice periods | Labour Act 2006 — **pending G6** | Notice varies by classification and by who initiates |
| Disciplinary procedure | Labour Act 2006 — **pending G6** | A prescribed process may apply before dismissal for misconduct |
| Service benefits on exit | Labour Act 2006 — **pending G6** | Gratuity, leave encashment and other entitlements |
| Restrictions on terms | Labour Act 2006 — **pending G6** | Terms less favourable than statutory minimums are void |

### 2.1 G6 questions for Legal Counsel

| # | Question |
|---|---|
| **HR1** | What are the employment classifications under the Act, and what must an appointment letter state for each? |
| **HR2** | What notice periods apply, by classification and by initiating party? |
| **HR3** | **What disciplinary procedure must precede dismissal for misconduct, and what must each letter in that process contain?** |
| **HR4** | What service benefits are payable on each type of exit, and how are they calculated? |
| **HR5** | Are probation terms and extensions restricted? |
| **HR6** | What may and may not appear in an experience or service certificate? |
| **HR7** | Are restrictive covenants — non-compete, non-solicit — enforceable, and in what form? |
| **HR8** | What language obligations apply to employment documents? |

> **HR3 is the one that determines whether a dismissal stands.** A procedurally defective
> dismissal is usually reversible regardless of the underlying facts.

---

## 3. Layout

| Zone | Content | Bilingual |
|---|---|---|
| Header | Letterhead, letter reference, date, **CONFIDENTIAL** | Title stacked |
| Party block | Employee name, ID, designation, department left; issuing officer right | Labels stacked |
| Body | Subject → the decision or offer → terms → effective date → what the recipient must do | **Separate versions** per language |
| Totals | Where remuneration appears: structure by element, referencing `MD-043` | Arabic numerals |
| Statutory block | Acknowledgement and, where applicable, the right of response and its deadline | Both languages present |
| Signature | Per §1.1; employee acknowledgement where required | Labels stacked |
| Footer | Letter reference, `page n of m`, HR contact | English |

| # | Rule |
|---|---|
| **L-42-a** | Every letter states **one decision** and its effective date. A letter that promotes and transfers and revises pay in one paragraph is a letter that will be disputed in parts |
| **L-42-b** | Disciplinary letters state the **right of response and its deadline** in the statutory block. Removing it does not strengthen the letter; it invalidates the process |
| **L-42-c** | Remuneration is stated by element, referencing `MD-043`, so the appointment letter and the payslip agree |
| **L-42-d** | Acknowledgement of receipt is captured for every letter — signature, e-signature or a recorded delivery. **An unacknowledged warning letter is a warning that did not happen** |
| **L-42-e** | Bengali and English are complete separate versions with a precedence clause (**G6 HR8**) |
| **L-42-f** | Every letter is marked **CONFIDENTIAL** and addressed to the employee, not to their manager |

---

## 4. Field Mapping

### 4.1 Common fields

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Letter reference | পত্র সূত্র | `MD-040` sequence | Monospace | ✔ |
| Letter type | পত্রের ধরন | Template code | Code + name | ✔ |
| Template version | টেমপ্লেট সংস্করণ | `M21.template_version` | `v{n}.{n}` | ✔ |
| Date | তারিখ | `letter.issued_at` | `DD/MM/YYYY` | ✔ |
| Employee name | কর্মীর নাম | `MD-012.employee_name` | Text | ✔ |
| Employee ID | কর্মী আইডি | `MD-012.employee_code` | Monospace | ✔ |
| Designation | পদবি | `MD-009.job_title` | Text | ✔ |
| Department / location | বিভাগ / কর্মস্থল | `MD-008`, `MD-003` | Text | ✔ |
| Employment classification | কর্মসংস্থানের শ্রেণি | `MD-012.employment_type` | Enum per **G6 HR1** | ✔ |
| Effective date | কার্যকর তারিখ | `letter.effective_date` | `DD/MM/YYYY` | ✔ |
| Issuing officer | ইস্যুকারী কর্মকর্তা | `employee.display_name` + designation | Text | ✔ |
| Acknowledgement | স্বীকৃতি | Signature / e-signature / delivery | Reference + date | ✔ |

### 4.2 Type-specific fields

| Letter | Additional required fields |
|---|---|
| **Offer / appointment** | Position, reporting line, classification, probation period, remuneration by `MD-043` element, benefits, notice period, joining date, conditions (documents, references, medical), **restrictive covenants per G6 HR7** |
| **Confirmation** | Probation period served, confirmation date, revised terms if any |
| **Probation extension** | Reason, extended period, review criteria, review date |
| **Transfer** | From/to location and department, effective date, allowance changes, relocation support |
| **Promotion / re-grade** | New position, grade, reporting line, remuneration change by element |
| **Salary revision** | Effective date, revised structure by element, reason |
| **Show-cause** | The allegation with dates and specifics, the rule alleged breached, **response deadline**, consequence of not responding |
| **Warning** | Level (written / final), the conduct, prior warnings referenced, expected change, review period, consequence of repetition |
| **Suspension** | Grounds, effective date, pay status during suspension, expected duration, conditions |
| **Enquiry outcome** | Process followed, findings, decision, right of appeal and deadline |
| **Resignation acceptance** | Resignation date, last working day, notice position, handover requirements |
| **Termination / dismissal** | Grounds, process reference, notice or pay in lieu, last working day, settlement summary, right of appeal |
| **Retrenchment** | Grounds, selection basis, notice, statutory compensation per **G6 HR4** |
| **Experience certificate** | Dates of employment, positions held — **and nothing more unless G6 HR6 permits** |
| **Clearance and settlement** | Asset return, access revocation, dues and recoveries, final settlement figure, `DT-041` reference |

| # | Rule |
|---|---|
| **FM-42-a** | Remuneration always resolves to `MD-043` elements (`L-42-c`) |
| **FM-42-b** | Disciplinary letters state **specifics** — dates, incidents, rules — not characterisations. "Unprofessional behaviour" is not an allegation a person can answer |
| **FM-42-c** | A warning references prior warnings by reference and date, or states that there are none |
| **FM-42-d** | The experience certificate states dates and positions only, unless **G6 HR6** permits more and the employee has requested it. **Adverse comment in a service certificate is a defamation risk with no upside** |
| **FM-42-e** | The clearance letter triggers `BRU-SEC-06` access revocation within one hour of the leaver event — the letter records that it occurred |
| **FM-42-f** | Template version prints, so a letter issued years ago can be read against the terms then in force |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SEC-06` | Leaver access revoked within one hour; clearance letter records it |
| `BRU-HRM-07` | Letters are addressed to the employee; managers see only what their role requires |
| `BRU-HRM-06` | Remuneration changes flow into a payroll run requiring two approvals |
| `BRU-LMS-01` | Mandatory training status may condition a confirmation |
| `BRU-DMS-03` | An issued letter is not edited; a correction is a new letter referencing it |
| `BRU-SEC-07` | The issuing officer cannot be the subject of the letter |

### 5.1 The disciplinary sequence

| Step | Letter | Requirement |
|---|---|---|
| 1 | **Show-cause** | Specific allegation, rule cited, response deadline (**G6 HR3**) |
| 2 | *Employee response* | Recorded, whether or not it is provided |
| 3 | **Suspension** (where warranted) | Grounds and pay status stated |
| 4 | *Enquiry* | Conducted per **G6 HR3**; the employee is heard |
| 5 | **Enquiry outcome** | Findings, decision, right of appeal |
| 6 | **Warning** or **Termination** | Proportionate to the finding |

| # | Rule |
|---|---|
| **DP-42-a** | **Steps are not skipped.** A dismissal without a show-cause and an enquiry is procedurally defective whatever the conduct |
| **DP-42-b** | Every step is acknowledged or its delivery evidenced (`L-42-d`) |
| **DP-42-c** | The employee's response is on file whether or not it helps them |
| **DP-42-d** | Legal reviews the populated letter at steps 1, 5 and 6 (`LS-01`) |
| **DP-42-e** | Timelines between steps are recorded. An enquiry outcome issued months later is not an outcome of that enquiry |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard** | Each of the 16 letter types | Per §1.1 |
| **Field / technician staff** | Bengali-first workforce | Bengali version leads; plainer register (`VB-002`) |
| **Senior / management** | Director and manager appointments | Additional terms, notice, covenants per **G6 HR7** |
| **Fixed-term / project** | Contract staff | Term, renewal position and end-of-term consequences stated |
| **Apprentice / trainee** | Where the classification applies | Per **G6 HR1** classification requirements |
| **Bulk** | Organisation-wide changes | Individually addressed and acknowledged; **never a notice board** |

---

## 7. Worked Example

> **Specimens follow G6 HR1 and HR3.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-042-S1` | Appointment letter, permanent technician | Remuneration by `MD-043` element, classification terms |
| `DT-042-S2` | Show-cause with a specific allegation | `FM-42-b` specificity and response deadline |
| `DT-042-S3` | Final warning referencing two prior warnings | `FM-42-c` |
| `DT-042-S4` | Enquiry outcome with right of appeal | `DP-42-a` sequence completeness |
| `DT-042-S5` | Clearance and final settlement | `BRU-SEC-06` and `DT-041` linkage |
| `DT-042-S6` | Experience certificate | `FM-42-d` restraint |

Held in `RF-009`, watermarked **SPECIMEN**, using synthetic employee data only.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Human Resources with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — HR Director | *pending* | | |
| Reviewer — Finance (settlement letters) | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **Legal Counsel — the set approved as a set (HR1–HR8)** | *pending* | | **Required** |
| Approver — Legal Counsel with HR Director | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `HRL-{entity}-{yy}-{seq:06d}` |
| Gap policy | `gaps_recorded`; a drafted-but-not-issued letter consumes no number |
| Archive format | **PDF/A-3 at issue** |
| Retention | `LG-009`; **employment duration plus the limitation period**; disciplinary records may have a shorter active life but a longer retention — **G6** |
| Personal file | Letters are filed to the employee's record with access per `BRU-HRM-07` |
| Re-render | **Prohibited.** Terms and templates change |
| Reprint | Watermarked **COPY**, logged; issued to the employee only |
| Template versioning | Every version retained while any employee remains on terms issued under it (`FM-42-f`) |
| Acknowledgement | Retained with the letter; a letter with no acknowledgement evidence is flagged |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-041_Payslip_and_Salary_Certificate.md`](DT-041_Payslip_and_Salary_Certificate.md) | Final settlement pairs with the clearance letter; remuneration elements shared |
| [`DT-043_NCR_CAPA_and_Internal_Audit_Report_Forms.md`](DT-043_NCR_CAPA_and_Internal_Audit_Report_Forms.md) | Where a quality non-conformance involves conduct, the two processes are kept separate |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md) | Remuneration elements |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md) | Designations |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-012_Employee_Master_Data_Template.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-012_Employee_Master_Data_Template.md) | Employee identity and classification |
| `LG-020` Acceptable Use and Internal Access Policy | The policy these letters implement |
| [`SP-023_SOP_Recruitment_and_Onboarding.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-023_SOP_Recruitment_and_Onboarding.md) | The processes, including the §5.1 sequence |
| [`NT-014_Email_Template_Library_Internal_and_HR.md`](../../04_Notification_and_Messaging/04C_Email/NT-014_Email_Template_Library_Internal_and_HR.md) | Covering messages |
| `TR-015` Course Pack — HR and Payroll | Where letter selection and the disciplinary sequence are taught |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Sixteen-letter set with signatory and sensitivity per letter, Legal review of populated disciplinary letters, one-decision-per-letter rule, six-step disciplinary sequence with five rules, experience-certificate restraint | Legal Counsel with HR Director (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Sixteen letters enumerated with trigger, signatory and sensitivity
- [x] Legal review required on populated disciplinary letters, not only templates (`LS-01`)
- [x] Disciplinary sequence stated with no-skip rule (`DP-42-a`)
- [x] Acknowledgement made mandatory (`L-42-d`)
- [x] All internal links resolve
- [ ] **Legal Counsel approval of the set (HR1–HR8)** — **outstanding; blocks `Approved`**
- [ ] **G6 HR3 — the mandatory disciplinary procedure** — **outstanding; letters 8–11 cannot be finalised without it**
- [ ] G6 HR1/HR2/HR4 — classifications, notice and exit benefits — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
