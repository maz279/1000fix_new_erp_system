---
id: MD-043
title: Payroll Element and Statutory Deduction Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HR with Finance
author: HR and Finance with the external adviser
reviewers: [External tax adviser, Finance, Legal & Compliance, Audit, Localisation Lead]
approver: Chief Financial Officer
content_class: A
purpose: >
  Earnings, deductions, allowances, incentive elements, tax slabs, provident fund and statutory
  contributions. Payroll cannot be run or filed without the element structure, and technician
  incentive schemes depend on it.
traces_to: [M56, M57, M19, MD-008, MD-012, MD-035, MD-042, DT-041]
priority: P0
wave: W5
bilingual: yes
bn_counterpart: MD-043_Payroll_Element_and_Statutory_Deduction_Register_BN.md
data_file: MD-043_Payroll_Element_and_Statutory_Deduction_Register.csv
effective_dated: yes
sources:
  - source: The enacted Income Tax Act and the applicable Finance Act — **to be verified at gate G6**
    verified: 2026-08-15
    class: P1
  - source: Bangladesh labour legislation on provident fund, gratuity and statutory contributions — **to be verified at gate G6**
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M56_Payroll_Benefits_and_Statutory_Compliance.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-043 — Payroll Element and Statutory Deduction Register

> ⚠ **Class A — statutory.** Gate **G6** external verification is mandatory and unwaivable.
>
> Payroll errors for 500+ employees are visible, urgent and legally consequential. Tax slabs and
> statutory contribution rates **must be verified against the enacted instrument**, never against
> a summary or a prior year's configuration (`CG-012` EV-02; precedent `00-07` H2-13).

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce & asset |
| Owning module | `M56` |
| Data steward | Payroll analyst |
| Golden source | The enacted Income Tax Act and labour legislation, verified by the adviser |
| Refresh cadence | **Annually at the Finance Act**; immediately on any statutory change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | A — Statutory |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `element_code` | char(9) | ✔ | `PAY-nnnnn`, permanent | — |  |
| `element_name_en` | text(120) | ✔ |  | — |  |
| `element_name_bn` | text(120) | ✔ |  | **✔** | **Printed on the payslip** (`DT-041`) |
| `element_type` | enum | ✔ | earning / deduction / employer_contribution / statutory_deduction / reimbursement | — |  |
| `calculation_basis` | enum | ✔ | fixed / percentage_of / formula / slab / attendance_based / performance_based | — |  |
| `basis_element_code` | fk |  | Self-reference; for percentage_of | — |  |
| `formula` | text(500) |  | Machine-evaluable | — |  |
| `is_taxable` | bool | ✔ |  | — |  |
| `is_pf_applicable` | bool | ✔ |  | — | Counts toward provident fund base |
| `is_gratuity_applicable` | bool | ✔ |  | — |  |
| `gl_account_code` | fk | ✔ | → `MD-035` | — |  |
| `statutory_reference` | text(120) |  | The provision requiring it | — | **G6 evidence** |
| `proration_on_partial_month` | bool | ✔ |  | — |  |
| `display_order` | int | ✔ | Payslip order | — |  |
| `effective_from` | date | ✔ |  | — | **Fiscal-year pinned** |
| `verified_by` | text(120) | ✔ |  | — | **G6** |
| `verified_on` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

### 2.1 Tax slab sub-register — `MD-043_Tax_Slabs.csv`

`slab_code` · `fiscal_year` · `taxpayer_category` · `lower_bdt` · `upper_bdt` · `rate_pct` ·
`statutory_reference` · `verified_by` · `verified_on` · `active`

> Slabs, thresholds and categories are **determinations for the adviser**, not for this document.
> They load `active = FALSE` until G6 verification is recorded.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `element_name_en` + `effective_from` |
| Surrogate key | `element_code` |
| Code format | `PAY-nnnnn` |
| Reuse policy | **Never reused.** Payslips are retained per `LG-009` and must remain interpretable |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| PAY-01 | An element may not be activated without `verified_by` and `verified_on` (G6) | **H** | `ERR-PAY-101` |
| PAY-02 | A statutory deduction requires a `statutory_reference` | **H** | `ERR-PAY-102` |
| PAY-03 | Payroll is calculated on the element version effective in the pay period | **H** | `ERR-PAY-103` |
| PAY-04 | `element_name_bn` is mandatory — the payslip is bilingual | **H** | `ERR-PAY-104` |
| PAY-05 | Changing an element after a payroll run in that period is prohibited | **H** | `ERR-PAY-105` |
| PAY-06 | A percentage element must reference a valid basis element | **H** | `ERR-PAY-106` |
| PAY-07 | An element unverified for more than 12 months blocks payroll (`CG-006` §4.2) | **H** | `ERR-PAY-107` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-035` Chart of accounts | **Before** |
| `MD-008` Positions | Before |
| `MD-042` Shifts | Before for attendance-based |

| Depended on by |
|---|
| `M56` payroll · `M57` incentives · `DT-041` payslip · `DM-009` YTD migration · statutory filings |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | The enacted Income Tax Act, Finance Act and labour legislation |
| Who supplies it | Payroll analyst with the external adviser |
| Collection method | **Read the enacted instrument.** Verified at G6 before activation |
| Known quality issues | ⚠ Slab rates, PF rates and gratuity basis are not determined in this document. Prior-year configuration must not be carried forward without re-verification |
| Cleansing rules | `DM-011`. **YTD figures cannot be recomputed** — they migrate as-is and must reconcile (`DM-013`) |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 80–200 elements plus slab sets per fiscal year | Low |
| SIT / UAT | All elements — payroll is tested against a parallel run | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Payroll analyst |
| Who may deactivate | CFO |
| Approval required | **CFO with adviser verification** — unwaivable |
| Effective dating | **Yes — fiscal-year pinned** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
element_code,element_name_en,element_name_bn,element_type,calculation_basis,is_taxable,is_pf_applicable,gl_account_code,statutory_reference,display_order,effective_from,verified_by,verified_on,active
PAY-00101,Basic salary,মূল বেতন,earning,fixed,TRUE,TRUE,6-10-10-010,,10,2026-07-01,<adviser pending G6>,,FALSE
PAY-00120,House rent allowance,বাড়ি ভাড়া ভাতা,earning,percentage_of,TRUE,FALSE,6-10-10-020,<provision pending G6>,20,2026-07-01,<adviser pending G6>,,FALSE
PAY-00310,Provident fund - employee,ভবিষ্য তহবিল - কর্মচারী,statutory_deduction,percentage_of,FALSE,FALSE,2-20-10-010,<provision pending G6>,60,2026-07-01,<adviser pending G6>,,FALSE
```

---

## 10. Migration notes

`DM-009`. **All rows load `active = FALSE` until G6 verification.** YTD balances migrate and must reconcile exactly before the first live run.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| `DT-041` Payslip and Salary Certificate | Where elements are printed |
| [`../02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.md`](../02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.md) | Posting targets |
| `SP-021` SOP Payroll Run and Statutory Filing | The process |
| `M56` Payroll, Benefits and Statutory Compliance | The implementing module |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`
- [x] Record structure names column, type, required flag, constraint and Bengali requirement
- [x] Keys, code format and reuse prohibition stated
- [x] Every validation rule carries a class and an error message ID
- [x] Load dependencies stated and reconciled with `MD-048`
- [x] Golden source and acquisition method named
- [x] Volumes stated per environment
- [x] Sample rows included and parse as CSV
- [x] Archive rule states records are archived, never deleted (`05-02` DM-06)
- [x] All internal links resolve
- [ ] Bengali name columns populated and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] G6 statutory verification against the enacted instrument — **outstanding, unwaivable (`WV-02`)**
- [ ] `statutory_pin` fiscal year confirmed (`CG-006` §4.1)
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
