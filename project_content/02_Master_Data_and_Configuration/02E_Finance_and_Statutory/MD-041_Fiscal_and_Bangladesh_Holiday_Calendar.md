---
id: MD-041
title: Fiscal and Bangladesh Holiday Calendar
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance with HR
author: Finance with HR and Operations
reviewers: [HR, Operations, Service Operations, Localisation Lead]
approver: Chief Financial Officer
content_class: C
purpose: >
  Fiscal periods, Bangladesh public and religious holidays, branch-specific closures and working
  calendars. SLA clocks, payroll, attendance, dispatch capacity and financial close all read the
  calendar; a missing holiday means SLA breaches recorded against a day nobody worked.
traces_to: [M19, M55, M56, MD-028, MD-003, MD-042, 05-06 §9]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-041_Fiscal_and_Bangladesh_Holiday_Calendar_BN.md
data_file: MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.csv
effective_dated: yes
sources:
  - source: Government of Bangladesh gazette holiday notification, published annually
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 — Gregorian calendar with Bangladesh public holidays including moon-dependent dates; fiscal year July–June
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-041 — Fiscal and Bangladesh Holiday Calendar

> ⚠ **Moon-dependent holidays cannot be published a year ahead.** Eid dates and several other
> observances are confirmed only days beforehand by moon sighting.
>
> **Consequence:** the calendar carries a `date_confirmed` flag. Provisional dates are used for
> planning; SLA and payroll calculations re-evaluate when the date is confirmed. A system that
> assumes a fixed date will misreport SLA on the most operationally disrupted days of the year.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Finance & statutory |
| Owning module | `M19` |
| Data steward | Finance systems analyst |
| Golden source | Government gazette holiday notification, issued annually |
| Refresh cadence | **Annually, on gazette publication**; branch closures as they arise |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `calendar_code` | char(8) | ✔ | `CAL-nnn` | — | Business calendar identity |
| `calendar_name` | text(80) | ✔ |  | — | 24×7, business hours, extended |
| `entity_code` | fk | ✔ | → `MD-002` | — |  |
| `branch_code` | fk |  | → `MD-003`; null = all | — | Branch-specific closures |
| `working_days` | multi-enum | ✔ | SUN…SAT | — | Bangladesh week is Sun–Thu for many offices |
| `day_start` | time | ✔ |  | — | Asia/Dhaka |
| `day_end` | time | ✔ |  | — |  |
| `break_start` | time |  |  | — | Prayer break where observed |
| `break_end` | time |  |  | — |  |

### 2.1 Holiday sub-register — `MD-041_Holidays.csv`

| Column | Type | Req | Note |
|---|---|:--:|---|
| `holiday_date` | date | ✔ | |
| `holiday_name_en` | text(120) | ✔ | |
| `holiday_name_bn` | text(120) | ✔ | **Bengali required** |
| `holiday_type` | enum | ✔ | public / religious / optional / branch_closure |
| `is_moon_dependent` | bool | ✔ | **Eid and related observances** |
| `date_confirmed` | bool | ✔ | FALSE while provisional |
| `confirmed_on` | date | | When the gazette confirmed it |
| `applies_to_branches` | multi-fk | | Null = all |
| `sla_clock_stops` | bool | ✔ | Whether SLA pauses |
| `payroll_treatment` | enum | ✔ | paid / unpaid / overtime_rate |

### 2.2 Fiscal period sub-register

`period_code` · `entity_code` · `fiscal_year` · `period_no` · `start_date` · `end_date` ·
`status` (open / closing / closed / locked) · `closed_on` · `closed_by`

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `calendar_code` + `branch_code` |
| Surrogate key | `calendar_code` |
| Code format | `CAL-nnn` |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| CAL-01 | Fiscal year must run 1 July to 30 June (`05-06` §9) | **H** | `ERR-CAL-001` |
| CAL-02 | Fiscal periods must be contiguous with no gaps or overlaps | **H** | `ERR-CAL-002` |
| CAL-03 | A posting to a `closed` or `locked` period is rejected | **H** | `ERR-CAL-003` |
| CAL-04 | `holiday_name_bn` is mandatory | **H** | `ERR-CAL-004` |
| CAL-05 | A moon-dependent holiday with `date_confirmed` FALSE is provisional; SLA and payroll re-evaluate on confirmation | **C** | `—` |
| CAL-06 | Reopening a closed period requires CFO approval and is logged | **A** | `ERR-CAL-006` |
| CAL-07 | A calendar year with fewer than the gazetted public holiday count warns | **S** | `WRN-CAL-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-002` Legal entity | Before |
| `MD-003` Branches | Before |

| Depended on by |
|---|
| `MD-028` SLA clocks · `M55` attendance · `M56` payroll · `M19` close · dispatch capacity · booking availability |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Government gazette holiday notification |
| Who supplies it | Finance with HR |
| Collection method | Transcribed from the gazette; moon-dependent dates loaded provisional and confirmed on announcement |
| Known quality issues | Provisional Eid dates shift by one to two days most years; systems that hard-code them misreport |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 4–8 calendars; ~25 holidays a year; 12 fiscal periods a year | Low |
| SIT / UAT | Two full years including a moon-dependent shift scenario | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Finance systems analyst |
| Who may deactivate | CFO |
| Approval required | CFO; HR for payroll treatment |
| Effective dating | **Yes** — holidays are dated and confirmed |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
holiday_date,holiday_name_en,holiday_name_bn,holiday_type,is_moon_dependent,date_confirmed,sla_clock_stops,payroll_treatment
2027-02-21,International Mother Language Day,আন্তর্জাতিক মাতৃভাষা দিবস,public,FALSE,TRUE,TRUE,paid
2027-03-26,Independence Day,স্বাধীনতা দিবস,public,FALSE,TRUE,TRUE,paid
2027-03-20,Eid-ul-Fitr (provisional),ঈদুল ফিতর (সম্ভাব্য),religious,TRUE,FALSE,TRUE,paid
2026-12-16,Victory Day,বিজয় দিবস,public,FALSE,TRUE,TRUE,paid
```

---

## 10. Migration notes

Not migrated — loaded from the gazette.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | SLA business calendars |
| [`../02F_Workforce_and_Asset/MD-042_Shift_Roster_and_Working_Pattern_Master.md`](../02F_Workforce_and_Asset/MD-042_Shift_Roster_and_Working_Pattern_Master.md) | Rostering |
| `M56` Payroll, Benefits and Statutory Compliance | Holiday pay treatment |

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
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
