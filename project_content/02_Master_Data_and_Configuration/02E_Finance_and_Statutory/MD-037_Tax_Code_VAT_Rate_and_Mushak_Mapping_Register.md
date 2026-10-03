---
id: MD-037
title: Tax Code, VAT Rate and Mushak Mapping Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Tax with Finance
author: Tax with Finance and the external adviser
reviewers: [External tax adviser, Finance, Legal & Compliance, Commercial, Localisation Lead]
approver: Chief Financial Officer
content_class: A
purpose: >
  VAT rates by supply type, VDS rates, exemptions, supplementary duty and AIT where applicable, and
  the mapping of each to Mushak 6.1, 6.2, 6.3, 6.6 and 9.1 output. NBR-compliant Mushak generation
  is mandatory for a VAT-registered business; the ERP must derive the correct form and rate per
  transaction automatically.
traces_to: [M51, M19, M20, M52, MD-002, MD-019, MD-035, DT-010, DT-011, DT-012, DT-013, DT-014]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register_BN.md
data_file: MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.csv
effective_dated: yes
sources:
  - source: The Value Added Tax and Supplementary Duty Act 2012 and its schedules, as amended — **to be verified against the enacted text at gate G6**
    verified: 2026-08-15
    class: P1
  - source: Standard VAT rate 15%; reduced rates including 1.5%, 2%, 2.4%, 4.5%, 5%, 7.5% and 10% apply to specified goods and services under the Third Schedule
    verified: 2026-08-15
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-100 — Mushak 9.1 filed by the 15th of the following month through the NBR VAT Online portal
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-037 — Tax Code, VAT Rate and Mushak Mapping Register

> ⚠ **Class A — statutory. The highest-consequence dataset in this category.**
>
> A wrong rate here produces a **non-compliant invoice on every transaction it touches**, and
> Mushak records must be preserved for at least five years. Gate **G6** external verification is
> mandatory and unwaivable (`WV-02`).
>
> **Rates below are indicative and must not be relied upon until G6 verification is recorded.**
> The standard rate is 15%; reduced rates exist for specified supplies. The applicable rate for
> each of our supply types is a determination for the tax adviser, not for this document.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Finance & statutory |
| Owning module | `M51` |
| Data steward | Tax analyst |
| Golden source | The enacted VAT and Supplementary Duty Act, its schedules and current SROs |
| Refresh cadence | **Annual at the Finance Act, and immediately on any SRO** |
| Environments | Dev · SIT · UAT · Prod |
| Content class | A — Statutory |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `tax_code` | char(10) | ✔ | `TAX-nnnnn`, permanent | — |  |
| `tax_name_en` | text(120) | ✔ |  | — |  |
| `tax_name_bn` | text(120) | ✔ |  | **✔** | Printed on Mushak output |
| `tax_type` | enum | ✔ | vat_output / vat_input / vds / supplementary_duty / ait / exempt / zero_rated | — |  |
| `rate_pct` | decimal(6,3) | ✔ |  | — | **Verified at G6** |
| `supply_type` | text(120) | ✔ | The supply this applies to | — |  |
| `sro_reference` | text(60) |  | The SRO or schedule granting a reduced rate | — | **Evidence for a non-standard rate** |
| `mushak_form` | multi-enum | ✔ | 6.1 / 6.2 / 6.3 / 6.6 / 9.1 | — | **Which forms this feeds** |
| `mushak_line_ref` | text(40) |  | The line on the form | — |  |
| `gl_account_code` | fk | ✔ | → `MD-035` | — | Posting target |
| `is_reclaimable` | bool | ✔ |  | — | Input VAT recoverable |
| `applies_to_item_categories` | multi-fk |  | → `MD-019` | — |  |
| `effective_from` | date | ✔ |  | — | **Fiscal-year pinned** |
| `effective_to` | date |  |  | — |  |
| `verified_by` | text(120) | ✔ | External adviser name | — | **G6 evidence** |
| `verified_on` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `tax_type` + `supply_type` + `effective_from` |
| Surrogate key | `tax_code` |
| Code format | `TAX-nnnnn` |
| Reuse policy | **Never reused.** A retired rate must remain resolvable for the retention period of every invoice that used it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| TAX-01 | Every sellable item must resolve to exactly one output tax code at the transaction date | **H** | `ERR-TAX-001` |
| TAX-02 | A non-standard rate requires an `sro_reference` | **H** | `ERR-TAX-002` |
| TAX-03 | A tax code may not be activated without `verified_by` and `verified_on` (G6) | **H** | `ERR-TAX-003` |
| TAX-04 | A transaction is taxed at the rate effective on its **tax point**, not the current rate | **H** | `ERR-TAX-004` |
| TAX-05 | Every VAT code must map to at least one Mushak form | **H** | `ERR-TAX-005` |
| TAX-06 | A VDS code requires the deducting entity to have `is_vds_authority` TRUE in `MD-002` | **H** | `ERR-TAX-006` |
| TAX-07 | Changing a rate on a code with posted transactions is prohibited — supersede it | **H** | `ERR-TAX-007` |
| TAX-08 | A code unverified for more than 12 months blocks new transactions (`CG-006` §4.2) | **H** | `ERR-TAX-008` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-002` Legal entity | **Before** |
| `MD-035` Chart of accounts | **Before** |
| `MD-019` Catalogue | Before or bind after |

| Depended on by |
|---|
| `MD-019` item tax classes · `MD-016` vendor VDS · `DT-010`…`DT-014` Mushak output · `M20` invoicing · `M52` payables · `RP-009` statutory reports |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | The enacted VAT and Supplementary Duty Act, its schedules and current SROs |
| Who supplies it | Tax Manager with the external adviser |
| Collection method | **Read the enacted instrument and the applicable SROs.** Press reporting and secondary summaries are not sources (`CG-012` EV-02, precedent `00-07` H2-13) |
| Known quality issues | ⚠ Reduced-rate applicability to our specific supply types has not been determined. Several service categories may attract rates other than 15% |
| Cleansing rules | `DM-011`. Legacy tax codes are **not** migrated — the register is authored from the instrument |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 40–120 codes across all types and fiscal years | Low |
| SIT / UAT | All active codes — Mushak output is tested exhaustively (`TS-009`) | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Tax analyst |
| Who may deactivate | CFO |
| Approval required | **CFO with external adviser verification** — unwaivable |
| Effective dating | **Yes — fiscal-year pinned** (`CG-006` §4.1) |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
tax_code,tax_name_en,tax_name_bn,tax_type,rate_pct,supply_type,sro_reference,mushak_form,gl_account_code,is_reclaimable,effective_from,verified_by,verified_on,active
TAX-STD15,VAT standard rate,ভ্যাট স্ট্যান্ডার্ড হার,vat_output,15.000,General goods and services,,6.2;6.3;9.1,2-30-10-010,FALSE,2026-07-01,<adviser pending G6>,,FALSE
TAX-IN15,Input VAT standard,ইনপুট ভ্যাট স্ট্যান্ডার্ড,vat_input,15.000,General purchases,,6.1;9.1,1-40-10-010,TRUE,2026-07-01,<adviser pending G6>,,FALSE
TAX-VDS,VAT deducted at source,উৎসে ভ্যাট কর্তন,vds,,Services from specified suppliers,,6.6;9.1,2-30-20-010,FALSE,2026-07-01,<adviser pending G6>,,FALSE
```

---

## 10. Migration notes

Not migrated — authored from the instrument. **All sample rows load `active = FALSE` until G6 verification is recorded.**

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-035_Chart_of_Accounts_Bangladesh.md`](MD-035_Chart_of_Accounts_Bangladesh.md) | Posting targets |
| `DT-010` Tax Invoice Mushak 6.3 | The primary statutory output |
| `DT-014` VAT Return Pack Mushak 9.1 | The filing this feeds |
| `TS-009` UAT Script Pack — Finance Roles | Where Mushak correctness is verified by Finance |
| `M51` Tax and Regulatory Compliance (Bangladesh) | The implementing module |

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
