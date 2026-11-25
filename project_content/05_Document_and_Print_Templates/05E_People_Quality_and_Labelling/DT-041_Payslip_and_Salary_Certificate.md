---
id: DT-041
title: Payslip and Salary Certificate
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Human Resources with Finance
author: Human Resources with Finance, Legal & Compliance and Content Design
reviewers: [Legal Counsel, External tax adviser, Finance, Payroll, Internal Audit, Localisation Lead]
approver: Chief Financial Officer with HR Director
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  The payslip layout with earnings, deductions, employer contributions and year-to-date figures,
  plus the salary certificate format. Payslips are a statutory entitlement for 500+ employees and
  the most scrutinised document HR issues — every employee reads their own payslip more carefully
  than any other document the company produces.
traces_to: [M56, M21, M55, M57, DT-001, DT-042, MD-002, MD-009, MD-012, MD-036, MD-040, MD-042, MD-043, LG-009, BRU-HRM-05, BRU-HRM-06, BRU-HRM-07, BRU-HRM-02]
priority: P1
wave: W5
bilingual: yes
bn_counterpart: DT-041_Payslip_and_Salary_Certificate_BN.md
sources:
  - source: Bangladesh Labour Act 2006 — wage payment obligations and limits on deductions; total deductions are limited relative to wages. **The wage-record and payslip obligations must be verified against the enacted text and the Labour Rules at G6**
    verified: 2026-08-15
    class: P2
  - source: Income Tax Act 2023 — monthly deduction of tax at source from salary as advance income tax. **Rates, slabs and the evidence to be given to the employee must be verified at G6**
    verified: 2026-08-15
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-HRM-05 and BRU-HRM-06 — payroll cannot be finalised until attendance is verified and locked; payroll requires two approvals, HR Manager and CFO
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-HRM-07 — an employee's payroll record is visible to them and to HR/finance, never to peers or line managers below HR Manager
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-041 — Payslip and Salary Certificate

> ⚠ **Tier S — statutory. Gate G6 mandatory and unwaivable (`WV-02`).**
>
> **Every one of 500+ employees reads this document every month, and reads it carefully.** A
> payslip error is not a finance defect; it is an employee-relations event, and at scale it is a
> recurring one. The error rate on this document is the most visible quality signal HR produces.
>
> **`BRU-HRM-07`: a payroll record is visible to the employee and to HR/finance, and to nobody
> else — not to peers, not to line managers below HR Manager.** That is a distribution
> requirement, not a preference, and §5.1 states how it is met.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **Statutory payslip** + salary certificate |
| Owning module | `M56` Payroll, Benefits and Statutory Compliance |
| Statutory | **Yes — Tier S.** Labour Act 2006 wage records; Income Tax Act 2023 withholding evidence |
| Recipient(s) | The employee only; HR and Finance; third parties **only** on the employee's request via the salary certificate |
| Languages | **Bilingual — stacked labels.** A large share of the workforce reads Bengali |
| Output formats | **Digital-first — PDF to the employee's self-service portal**, password-protected email · A4 print on request · **PDF/A-3 archive** |
| Numbering mask | `MD-040` — `PSL-{entity}-{yy}-{seq:06d}` payslip; `SLC-{entity}-{yy}-{seq:06d}` certificate |
| Retention period | Per the Labour Act and tax obligations — **pending G6**; not less than the tax retention |
| Fiscal pin | **FY2026-27** — tax slabs and statutory rates are fiscal-year dependent |

### 1.1 Two documents, different purposes

| | Payslip | Salary certificate |
|---|---|---|
| Issued | Every pay period, automatically | On request |
| Purpose | Statutory wage record; the employee's evidence of pay and deductions | Third-party evidence of employment and income — bank, landlord, visa, loan |
| Detail | Full: every earning, deduction, employer contribution, YTD | Summary: employment, position, tenure, gross and net, as requested |
| Recipient | Employee only | Employee, who provides it onward |
| Contains bank details | No | No |
| Signed | No — system-issued | **Yes — authorised HR signatory** |

---

## 2. Statutory Requirements

> All rows **unverified pending G6**.

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Wage record showing wages payable and paid | Labour Act 2006 — **pending G6** | pending | Whole payslip |
| Itemisation of deductions | Labour Act 2006 — **pending G6** | pending | Deductions block |
| Limit on total deductions relative to wages | Labour Act 2006 — **pending G6** | pending | Validated, not printed |
| Employer identity | Labour Act 2006 — **pending G6** | pending | Header |
| Employee identity and designation | Labour Act 2006 — **pending G6** | pending | Party block |
| Wage period | Labour Act 2006 — **pending G6** | pending | Header |
| Tax deducted at source and its basis | Income Tax Act 2023 — **pending G6** | pending | Deductions and YTD |
| Employee and employer statutory-fund contributions | Applicable fund rules — **pending G6** | pending | Contributions block |

### 2.1 G6 questions

| # | Question |
|---|---|
| **PY1** | **Is a payslip in a prescribed form, and what are the mandatory contents under the Labour Act 2006 and the Labour Rules?** |
| **PY2** | What wage registers must be maintained alongside payslips, and for how long? |
| **PY3** | What is the lawful limit on total deductions, and which deductions count toward it? |
| **PY4** | What tax-deduction evidence must an employee receive, and on what cycle — monthly, annually, or on request? |
| **PY5** | Which statutory funds apply to us — provident fund, gratuity, workers' profit participation — and what must the payslip show? |
| **PY6** | Is an electronic payslip sufficient, or must a physical copy be provided? |
| **PY7** | What must a salary certificate contain, and are there restrictions on what it may state? |
| **PY8** | What are the record-retention obligations for payroll? |

---

## 3. Layout

**Primary format: PDF, A4 portrait.** Print on request.

| Zone | Content | Bilingual |
|---|---|---|
| Header | Employer, period, payslip number, **CONFIDENTIAL** marking | Title stacked |
| Party block | Employee name, ID, designation, department, location left; pay period, pay date, bank (masked) right | Labels stacked |
| Body | **Earnings** → **Deductions** → **Employer contributions** → net pay → **year-to-date** | Labels stacked |
| Totals | **Net pay**, in figures and words | Arabic numerals |
| Statutory block | Statutory deduction detail and tax basis | Parallel columns |
| Signature | None on a payslip; **authorised signatory on a salary certificate** | — |
| Footer | Payslip reference, `page n of m`, HR contact for queries | English |

| # | Rule |
|---|---|
| **L-41-a** | **Earnings, deductions and employer contributions are three separate blocks.** Netting a deduction against an earning is how an employee comes to believe they were not paid something they were |
| **L-41-b** | **Employer contributions are shown even though they are not paid to the employee.** They are part of the cost of employing that person and showing them is worth more than the space they take |
| **L-41-c** | Year-to-date figures print for gross, tax and each statutory contribution. **Employees need YTD at tax time and will otherwise ask HR** |
| **L-41-d** | Net pay prints in figures **and words**, in both languages |
| **L-41-e** | Every payslip is marked **CONFIDENTIAL** and carries the employee ID, so a misdirected payslip is recognisable |
| **L-41-f** | Bank details print masked; the full account never appears |
| **L-41-g** | Variable elements — overtime, incentive, allowance — print with the **basis**: hours, units or the rule applied. A figure with no basis produces a query |

---

## 4. Field Mapping

### 4.1 Header and employee

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Employer | নিয়োগকর্তা | `MD-002.entity_legal_name` | Text | ✔ |
| Employer address | ঠিকানা | `MD-002` | Text | ✔ |
| Payslip no. | পে-স্লিপ নং | `MD-040` sequence | Monospace | ✔ |
| Pay period | বেতন মেয়াদ | `MD-041` period | `MM/YYYY` | ✔ |
| Pay date | পরিশোধের তারিখ | `payroll.pay_date` | `DD/MM/YYYY` | ✔ |
| Employee name | কর্মীর নাম | `MD-012.employee_name` | Text | ✔ |
| **Employee ID** | কর্মী আইডি | `MD-012.employee_code` | Monospace | ✔ |
| Designation | পদবি | `MD-009.job_title` | Text | ✔ |
| Department / cost centre | বিভাগ / ব্যয় কেন্দ্র | `MD-008`, `MD-036` | Text + monospace | ✔ |
| Location / branch | কর্মস্থল | `MD-003` | Text | ✔ |
| Date of joining | যোগদানের তারিখ | `MD-012.join_date` | `DD/MM/YYYY` | ✔ |
| TIN | টিআইএন | `MD-012.tin` | Monospace | ✔ where held |
| Bank account (masked) | ব্যাংক হিসাব | `MD-038` | Last 4 | ✔ |
| Payment method | পরিশোধের পদ্ধতি | `MD-038` | Label | ✔ |
| Days / hours worked | কর্মদিবস / ঘণ্টা | `M55` attendance | Number | ✔ |
| Leave taken in period | গৃহীত ছুটি | `M21` leave | Days by type | ✔ |
| Leave balance | ছুটির ব্যালেন্স | `M21` | Days by type | ✔ |

### 4.2 Earnings, deductions and contributions

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Earning element | আয়ের উপাদান | `MD-043.element_code` + name | Code + text | ✔ per element |
| Basic | মূল বেতন | `MD-043` | BDT, 2 dp | ✔ |
| House rent allowance | বাড়ি ভাড়া ভাতা | `MD-043` | BDT, 2 dp | ✔ where applicable |
| Medical / conveyance / other allowances | চিকিৎসা / যাতায়াত / অন্যান্য ভাতা | `MD-043` | BDT, 2 dp | ✔ where applicable |
| **Overtime** | অতিরিক্ত সময় | `M55` + `MD-043` | Hours × rate = BDT | ✔ **with basis (`BRU-HRM-02`)** |
| Incentive / bonus | প্রণোদনা / বোনাস | `M57` | BDT + basis | ✔ where paid |
| Arrears | বকেয়া | `MD-043` | BDT + period explained | ✔ where any |
| **Gross earnings** | মোট আয় | Computed | BDT, 2 dp | ✔ |
| Deduction element | কর্তনের উপাদান | `MD-043.element_code` + name | Code + text | ✔ per element |
| **Tax deducted at source** | উৎসে আয়কর কর্তন | `MD-043` + tax table | BDT, 2 dp | ✔ **pending G6 PY4** |
| Provident fund — employee | ভবিষ্য তহবিল — কর্মী | `MD-043` | BDT, 2 dp | ✔ where applicable |
| Advance / loan repayment | অগ্রিম / ঋণ পরিশোধ | `MD-043` + balance | BDT + remaining | ✔ where any |
| Other authorised deduction | অন্যান্য অনুমোদিত কর্তন | `MD-043` | BDT + authority | ✔ where any |
| **Total deductions** | মোট কর্তন | Computed | BDT, 2 dp | ✔ |
| **Net pay** | নিট প্রদেয় | Computed | BDT, 2 dp, largest type | ✔ |
| Net pay in words | কথায় | Computed | Text, both languages | ✔ |
| Employer PF contribution | নিয়োগকর্তার পিএফ | `MD-043` | BDT, 2 dp | ✔ where applicable |
| Employer gratuity accrual | গ্র্যাচুইটি সঞ্চিতি | `MD-043` | BDT, 2 dp | ✔ where applicable |
| Other employer contribution | অন্যান্য নিয়োগকর্তার অবদান | `MD-043` | BDT, 2 dp | ✔ where applicable |
| **YTD gross / tax / PF** | বছরের মোট | Computed | BDT, 2 dp | ✔ |

| # | Rule |
|---|---|
| **FM-41-a** | Every element resolves to `MD-043`. **An ad-hoc pay element that exists only in a spreadsheet cannot appear on a payslip** |
| **FM-41-b** | Total deductions are validated against the lawful limit (**G6 PY3**) before the payroll can be finalised. The limit is a hard rule, not a warning |
| **FM-41-c** | Overtime requires prior approval (`BRU-HRM-02`) and prints hours × rate, not a lump sum |
| **FM-41-d** | Arrears state the period they relate to. Unexplained arrears generate the most payroll queries after tax |
| **FM-41-e** | Loan and advance deductions print the **remaining balance**, so the employee can see the end |
| **FM-41-f** | Payroll cannot finalise until attendance is verified and locked (`BRU-HRM-05`) and two approvals are recorded (`BRU-HRM-06`) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-HRM-02` | Overtime pre-approved before it counts |
| `BRU-HRM-03` | Performance incentive only after the minimum monthly job threshold |
| `BRU-HRM-05` | Attendance verified and locked before finalisation |
| `BRU-HRM-06` | Two approvals — HR Manager and CFO |
| `BRU-HRM-07` | Visibility restricted to the employee and HR/finance |
| `BRU-SEC-02` | Payroll finalisation requires step-up authentication |
| `BRU-SEC-05` | Bulk export of personal data requires approval and is logged |
| `BRU-DMS-03` | An issued payslip is not edited; a correction is a supplementary payslip |

### 5.1 Distribution and confidentiality

`BRU-HRM-07` is a distribution problem, and distribution is where payroll confidentiality
actually fails.

| # | Rule |
|---|---|
| **DS-41-a** | **Digital-first: the payslip is published to the employee's self-service portal.** No printing, no envelopes, no distribution chain |
| **DS-41-b** | Where email is used, the PDF is **password-protected** with a credential the employee already holds, never the employee ID alone |
| **DS-41-c** | **Printed payslips are never distributed via a line manager.** Where a printed copy is needed — field staff without portal access — it is collected in person on identification, or issued at the branch by HR |
| **DS-41-d** | A line manager below HR Manager cannot view a payslip in any system (`BRU-HRM-07`), and cannot be given one on paper either |
| **DS-41-e** | Access to payslip records is logged; bulk access requires approval (`BRU-SEC-05`) |
| **DS-41-f** | A misdirected payslip is a **personal-data incident** and follows the `LG-021` ISMS incident process, not an apology |

> **DS-41-c is the rule that gets tested every month.** Handing a stack of payslips to a branch
> manager to distribute is efficient, ordinary, and a breach of `BRU-HRM-07`.

### 5.2 Corrections

| # | Rule |
|---|---|
| **CR-41-a** | An issued payslip is never edited (`BRU-DMS-03`) |
| **CR-41-b** | An error is corrected by a **supplementary payslip** for the same period, referencing the original and showing only the correction, or by an adjustment in the next period clearly labelled with the period it relates to |
| **CR-41-c** | An underpayment is corrected **immediately**, not in the next cycle, where the amount is material to the employee |
| **CR-41-d** | An overpayment recovery is agreed with the employee and scheduled; it is not deducted unilaterally beyond what the Labour Act permits (**G6 PY3**) |
| **CR-41-e** | Payslip error rate and cause are reported monthly to the HR Director and CFO |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Monthly payslip** | Salaried staff, the default | The base document |
| **Field / technician payslip** | Staff with incentive and overtime | Variable elements with bases prominent (`L-41-g`) |
| **Daily-rated / contract** | Where applicable | Days worked and rate foremost |
| **Final settlement** | On exit | Notice pay, leave encashment, gratuity, clearances, full YTD; issued with the `DT-042` clearance letter |
| **Supplementary** | Correction (`CR-41-b`) | Shows the correction only, references the original |
| **Bonus / festival payment** | Off-cycle | Separate payslip with the basis stated |
| **Salary certificate** | On employee request | §1.1 summary form, signed by an authorised HR signatory |
| **Salary certificate — bank / visa** | Where a third party specifies content | Only what the employee authorises; **never** performance or disciplinary information (**G6 PY7**) |

---

## 7. Worked Example

> **Specimens follow G6 PY1 and PY5.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-041-S1` | Salaried employee, standard month | Base bilingual payslip with YTD |
| `DT-041-S2` | Technician with overtime and incentive | `L-41-g` bases printed |
| `DT-041-S3` | Employee with a loan deduction | `FM-41-e` remaining balance |
| `DT-041-S4` | Arrears for a prior period | `FM-41-d` period explanation |
| `DT-041-S5` | Final settlement on exit | Settlement variant |
| `DT-041-S6` | Salary certificate for a bank | `PY7` content restraint |

Held in `RF-009`, watermarked **SPECIMEN**, using synthetic employee data only.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Human Resources with Finance | 2026-08-15 | Draft issue |
| Reviewer — Payroll | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| Reviewer — Localisation | *pending* | | |
| **G6 — Legal Counsel and external tax adviser (PY1–PY8)** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — CFO with HR Director | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequences | `PSL-…` payslip, `SLC-…` salary certificate, separate |
| Gap policy | `no_gaps` on payslips — a wage record with unexplained gaps is a Labour Act exposure |
| Archive format | **PDF/A-3 at issue** |
| Retention | Per the Labour Act and tax obligations — **pending G6 PY8**; not less than the tax retention |
| Wage registers | Maintained alongside per **G6 PY2** |
| Re-render | **Prohibited.** Tax slabs, statutory rates and personal data change; a re-render would not match what the employee holds |
| Reprint | Watermarked **COPY**, logged; reprints are issued **to the employee only** |
| Employee access | Full payslip history available in self-service for the retention period |
| Fiscal pinning | Tax tables and statutory rates pinned to the fiscal year (`CG-006` §4.1) |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-042_HR_Letter_Template_Set.md`](DT-042_HR_Letter_Template_Set.md) | Offer, confirmation and clearance letters; final settlement pairs with it |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md) | **Every earning and deduction element** |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-042_Shift_Roster_and_Working_Pattern_Master.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-042_Shift_Roster_and_Working_Pattern_Master.md) | Working patterns behind attendance |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-012_Employee_Master_Data_Template.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-012_Employee_Master_Data_Template.md) | Employee identity fields |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md) | Pay periods and fiscal year |
| `LG-021` ISMS Policy Set | `DS-41-f` |
| `LG-009` Data Retention and Deletion Schedule | Retention |
| [`SP-021_SOP_Payroll_Run_and_Statutory_Filing.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-021_SOP_Payroll_Run_and_Statutory_Filing.md) | The run, its locks and its two approvals |
| [`NT-014_Email_Template_Library_Internal_and_HR.md`](../../04_Notification_and_Messaging/04C_Email/NT-014_Email_Template_Library_Internal_and_HR.md) | Payslip availability notification |
| `HC-015` FAQ Bank by Audience | Where employees find and understand their payslip |
| `RP-004` Dashboard Specification Pack — Operational Consoles | Error-rate reporting (`CR-41-e`) |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Payslip and salary certificate separated, three-block earnings/deductions/contributions layout, YTD requirement, six distribution rules enforcing `BRU-HRM-07`, five correction rules, eight-question G6 list | CFO with HR Director (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Payslip and salary certificate distinguished with their different purposes and recipients
- [x] Distribution rules stated, including the line-manager prohibition (`DS-41-c`)
- [x] Corrections handled by supplementary payslip, never by editing
- [x] Every element bound to `MD-043`
- [x] All internal links resolve
- [ ] **G6 PY1 — prescribed payslip contents under the Labour Act and Rules** — **outstanding, unwaivable (`WV-02`)**
- [ ] **G6 PY3 — lawful deduction limit** — **outstanding; `FM-41-b` cannot be enforced without it**
- [ ] G6 PY5 — applicable statutory funds — **outstanding; blocks `MD-043` completion**
- [ ] G6 PY7 — permissible salary-certificate contents — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Tax tables pinned to FY2026-27 and verified — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
