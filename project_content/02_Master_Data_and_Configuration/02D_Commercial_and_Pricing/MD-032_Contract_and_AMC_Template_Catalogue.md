---
id: MD-032
title: Contract and AMC Template Catalogue
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Account Management
author: Account Management with Legal
reviewers: [Legal & Compliance, Finance, Service Operations, Commercial, Localisation Lead]
approver: Legal Counsel
content_class: B
purpose: >
  AMC, RAMC and MSP contract templates with entitlement structures, visit schedules, coverage
  matrices and renewal terms. Contract-type orders are blocked unless the device is on an active
  contract covered-asset list (BRU-SRM-03).
traces_to: [M08, 05-05 BRU-SRM-03, MD-028, MD-031, MD-033, DT-030, LG-015, VB-010]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: MD-032_Contract_and_AMC_Template_Catalogue_BN.md
data_file: MD-032_Contract_and_AMC_Template_Catalogue.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-03
    verified: 2026-08-15
    class: P1
  - source: 1000_fix_corporate_website project_content B2B-020 AMC Package Comparison — Basic / Standard / Premium / Enterprise tiering in market
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-032 — Contract and AMC Template Catalogue

> ⚠ **Class B — legal.** A template is a contract. Its entitlement structure is what the customer
> has bought and what we owe. `DT-030` renders it; `LG-015` governs its master terms.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Commercial & pricing |
| Owning module | `M08` |
| Data steward | Contract analyst |
| Golden source | Legal-approved contract templates |
| Refresh cadence | Annual; on any template change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | B — Legal / contractual |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `template_code` | char(9) | ✔ | `CTP-nnnnn`, permanent | — |  |
| `contract_class` | enum | ✔ | amc / ramc / msp / enterprise | — |  |
| `tier` | enum | ✔ | From the `VB-010` ladders | — | Basic/Standard/Premium/Enterprise or Essential/Plus/Premium |
| `name_en` | text(120) | ✔ | Registered name (`VB-010`) | — |  |
| `name_bn` | text(120) | ✔ |  | **✔** |  |
| `segment_code` | fk | ✔ | → `MD-014` | — |  |
| `duration_months` | int | ✔ |  | — |  |
| `preventive_visits_per_year` | int | ✔ |  | — |  |
| `reactive_calls_included` | int |  | Null = unlimited within fair use | — | "Unlimited" is a `CG-013` T-A12 claim — never used loosely |
| `sla_band_code` | fk | ✔ | → `MD-028` | — |  |
| `covers` | multi-enum | ✔ | parts / labour / consumables / on_site / pickup / remote / replacement | — |  |
| `excluded_items` | text(600) | ✔ | Must match `LG-015` | — |  |
| `warranty_type_code` | fk |  | → `MD-031` | — | Bundled warranty |
| `max_covered_assets` | int |  |  | — |  |
| `renewal_type` | enum | ✔ | manual / auto_with_notice / auto | — |  |
| `notice_period_days` | int | ✔ |  | — |  |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `contract_class` + `tier` |
| Surrogate key | `template_code` |
| Code format | `CTP-nnnnn` |
| Reuse policy | Never reused; executed contracts reference the template version |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| CTP-01 | A contract-type service order requires the device on an active covered-asset list (`BRU-SRM-03`) | **H** | `ERR-CTP-001` |
| CTP-02 | `excluded_items` must match `LG-015`; a divergence blocks activation | **H** | `ERR-CTP-002` |
| CTP-03 | Entitlement consumption may not exceed `reactive_calls_included` without an approved variation | **H** | `ERR-CTP-003` |
| CTP-04 | `auto` renewal without notice is prohibited — consumer contracts require notice | **H** | `ERR-CTP-004` |
| CTP-05 | Changing terms on a template with executed contracts is prohibited — issue a new version | **H** | `ERR-CTP-005` |
| CTP-06 | A template with no preventive visits and no reactive calls warns — it covers nothing | **S** | `WRN-CTP-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-014` Segments | Before |
| `MD-028` SLA bands | **Before** |
| `MD-031` Warranty types | Before |

| Depended on by |
|---|
| `M08` contracts · `DT-030` agreement templates · `LG-015` master terms · `P04` entitlement display · `MD-033` subscriptions |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Legal-approved contract templates and the in-market AMC package set |
| Who supplies it | Account Management with Legal |
| Collection method | Template review clause by clause; entitlements reconciled with what is actually delivered |
| Known quality issues | In-market AMC tiers (Basic/Standard/Premium/Enterprise) exist in marketing content; the entitlement detail behind them is not consistently documented |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 20–40 templates | Low |
| SIT / UAT | 12 across all classes and tiers | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Contract analyst |
| Who may deactivate | Legal Counsel |
| Approval required | **Legal Counsel**; CCO for commercial terms |
| Effective dating | **Yes** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
template_code,contract_class,tier,name_en,name_bn,segment_code,duration_months,preventive_visits_per_year,reactive_calls_included,sla_band_code,renewal_type,notice_period_days,effective_from,active
CTP-00101,amc,Premium,AMC Premium,এএমসি প্রিমিয়াম,SEG-SME,12,4,24,SLA-P2,auto_with_notice,30,2026-07-01,TRUE
CTP-00201,ramc,Plus,RAMC Plus,রেমক প্লাস,SEG-B2C,12,2,6,SLA-P3,manual,15,2026-07-01,TRUE
```

---

## 10. Migration notes

`DM-010`. Open contracts migrate against **the template version they were signed under**, which must be reconstructed from the executed document.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| `LG-015` AMC/SLA Master Terms and Service Credit Rules | **Governs the terms** |
| `DT-030` Contract and AMC Agreement Template Set | Rendering |
| `VB-010` Product, Plan and Programme Naming Standard | Tier ladders |
| `M08` Contract Lifecycle Management | The implementing module |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Legal Counsel (pending) |

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
- [ ] G5 legal review — **outstanding, unwaivable (`WV-02`)**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
