---
id: MD-028
title: Priority, Severity and SLA Definition Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Service Operations with Legal
author: Service Operations with Legal and Finance
reviewers: [Legal & Compliance, Finance, Commercial, Account Management, Localisation Lead]
approver: Operations Director
content_class: C
purpose: >
  Priority and severity scales, response and resolution targets by contract class, business-hour
  calendars and pause rules. SLA is a contractual and financial obligation carrying service credits;
  it cannot be configured from prose scattered across module files.
traces_to: [M08, M05, MD-014, MD-020, MD-041, LG-015, DT-031, NT-020]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-028_Priority_Severity_and_SLA_Definition_Register_BN.md
data_file: MD-028_Priority_Severity_and_SLA_Definition_Register.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M08_Contract_Lifecycle_Management.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P04 — real-time SLA status, breach history, service credits earned
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-028 — Priority, Severity and SLA Definition Register

> ⚠ **This register carries financial liability.** Service credits are a contractual remedy paid
> in money. The definitions here must reconcile **exactly** with `LG-015` master terms and
> `DT-031` the SLA schedule annex. A divergence between the three is a dispute waiting to happen.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Catalogue & technical |
| Owning module | `M08` |
| Data steward | Service Operations analyst |
| Golden source | Executed contracts and the approved service catalogue |
| Refresh cadence | Per wave; on any contract template change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `sla_band_code` | char(8) | ✔ | `SLA-Pn`, permanent | — |  |
| `band_name_en` | text(80) | ✔ |  | — |  |
| `band_name_bn` | text(80) | ✔ |  | **✔** | Shown in `P01` and `P04` |
| `priority_level` | enum | ✔ | P0 / P1 / P2 / P3 / P4 | — | Business urgency |
| `severity_scale` | enum | ✔ | critical / high / medium / low | — | Impact, distinct from priority |
| `response_target_min` | int | ✔ | Minutes to first meaningful response | — |  |
| `resolution_target_min` | int | ✔ | Minutes to resolution | — |  |
| `business_calendar_code` | fk | ✔ | → `MD-041` | — | **Which clock runs** |
| `clock_runs` | enum | ✔ | 24x7 / business_hours / extended_hours | — |  |
| `pause_conditions` | multi-enum | ✔ | awaiting_customer / awaiting_part / awaiting_brand / customer_unavailable | — | **When the clock stops** |
| `service_credit_applies` | bool | ✔ |  | — |  |
| `credit_calculation` | text(300) |  | Required when credits apply | — | Must match `LG-015` verbatim |
| `credit_cap_pct` | decimal(5,2) |  |  | — | Cap as a % of the period charge |
| `escalation_at_pct` | int | ✔ | e.g. 75 — warn at 75% of target | — | Feeds `NT-020` |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `sla_band_code` |
| Surrogate key | `sla_band_code` |
| Code format | `SLA-Pn` |
| Reuse policy | Never reused; contracts reference the band by name |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| SLA-01 | `resolution_target_min` must exceed `response_target_min` | **H** | `ERR-SLA-001` |
| SLA-02 | `service_credit_applies` TRUE requires a `credit_calculation` and a cap | **H** | `ERR-SLA-002` |
| SLA-03 | `credit_calculation` must match the wording in `LG-015`; a divergence blocks activation | **H** | `ERR-SLA-003` |
| SLA-04 | Pause conditions must be evidenced — a paused clock without a recorded trigger resumes | **H** | `ERR-SLA-004` |
| SLA-05 | `band_name_bn` is mandatory | **H** | `ERR-SLA-005` |
| SLA-06 | Changing a target on a band referenced by an active contract requires Legal and CCO approval | **A** | `ERR-SLA-006` |
| SLA-07 | A band with a resolution target shorter than the average actual for that work type warns | **S** | `WRN-SLA-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-041` Business calendars | **Before** |
| `MD-014` Segments | Before |
| `MD-020` Delivery modes | Before |

| Depended on by |
|---|
| `M08` contracts · `M05` managed services · `MD-005` zones · `DT-031` SLA annex · `LG-015` master terms · `NT-020` breach notifications · `P04` SLA display |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Executed contracts and the approved service catalogue |
| Who supplies it | Operations Director with Legal |
| Collection method | Contract review; targets validated against actual performance before commitment |
| Known quality issues | ⚠ Existing SLA commitments are stated in prose across contracts and marketing content, and have not been reconciled. **Some may already be unachievable** |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 10–20 bands | Low |
| SIT / UAT | All bands — SLA calculation is tested exhaustively | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Service Operations analyst |
| Who may deactivate | Operations Director |
| Approval required | **Legal and CCO** for any band on an active contract |
| Effective dating | **Yes** — a job is judged by the band version in force at its creation |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
sla_band_code,band_name_en,band_name_bn,priority_level,severity_scale,response_target_min,resolution_target_min,business_calendar_code,clock_runs,pause_conditions,service_credit_applies,credit_cap_pct,escalation_at_pct,effective_from,active
SLA-P0,Critical Enterprise,ক্রিটিক্যাল এন্টারপ্রাইজ,P0,critical,30,240,CAL-24X7,24x7,awaiting_customer;awaiting_part,TRUE,10.00,75,2026-07-01,TRUE
SLA-P2,Standard Corporate,স্ট্যান্ডার্ড কর্পোরেট,P2,medium,240,2880,CAL-BUS,business_hours,awaiting_customer;awaiting_part;awaiting_brand,TRUE,5.00,75,2026-07-01,TRUE
SLA-P3,Standard Consumer,স্ট্যান্ডার্ড কনজিউমার,P3,medium,480,4320,CAL-BUS,business_hours,awaiting_customer;awaiting_part,FALSE,,80,2026-07-01,TRUE
```

---

## 10. Migration notes

Not migrated — authored from contracts. Open contracts must be mapped to a band at cutover (`DM-010`).

---

## 11. Related documents

| Document | Relationship |
|---|---|
| `LG-015` AMC/SLA Master Terms and Service Credit Rules | **Must reconcile exactly** |
| `DT-031` SLA Schedule and Service Credit Annex | **Must reconcile exactly** |
| [`../02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`](../02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md) | Business-hour clocks |
| `NT-020` Escalation and SLA Breach Notification Library | Breach messaging |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Operations Director (pending) |

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
