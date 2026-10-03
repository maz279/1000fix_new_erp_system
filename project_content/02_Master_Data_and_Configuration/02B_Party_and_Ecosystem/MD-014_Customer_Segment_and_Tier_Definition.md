---
id: MD-014
title: Customer Segment and Tier Definition
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial
author: Commercial with BI
reviewers: [Marketing, Finance, Service Operations, BI Lead, Localisation Lead]
approver: Chief Commercial Officer
content_class: C
purpose: >
  Defines customer segments and the rules that assign them. Pricing, SLA, campaign targeting and
  reporting all segment-key; ad-hoc segmentation makes analytics meaningless and lets two reports
  disagree about how many corporate customers exist.
traces_to: [M07, M11, M35, MD-013, MD-029, RP-001]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: MD-014_Customer_Segment_and_Tier_Definition_BN.md
data_file: MD-014_Customer_Segment_and_Tier_Definition.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M07_CRM_Sales_Pipeline_and_Account_Management.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-014 — Customer Segment and Tier Definition

> A segment is a **rule**, not a label. If a human can assign it by judgement, two humans will
> assign it differently and every segment-keyed report becomes unreliable.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Party & ecosystem |
| Owning module | `M07` |
| Data steward | Commercial analyst |
| Golden source | Commercial segmentation decision |
| Refresh cadence | Quarterly review; assignment recomputed nightly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `segment_code` | char(8) | ✔ | `SEG-nnn`, permanent | — |  |
| `segment_name_en` | text(80) | ✔ |  | — |  |
| `segment_name_bn` | text(80) | ✔ |  | **✔** | Shown in `P01` where relevant |
| `segment_class` | enum | ✔ | b2c / sme / enterprise / government / marketplace / walk_in | — |  |
| `assignment_rule` | text(500) | ✔ | Machine-evaluable expression | — | **Not prose** |
| `assignment_priority` | int | ✔ | Lower wins on conflict | — | Segments are mutually exclusive |
| `default_price_list_code` | fk | ✔ | → `MD-029` | — |  |
| `default_sla_band_code` | fk | ✔ | → `MD-028` | — |  |
| `credit_terms_days` | int | ✔ | 0 for prepay | — |  |
| `requires_contract` | bool | ✔ |  | — |  |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `segment_name_en` |
| Surrogate key | `segment_code` |
| Code format | `SEG-nnn` |
| Reuse policy | Never reused; historical analytics reference it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| SEG-01 | Segments must be mutually exclusive — every party resolves to exactly one | **H** | `ERR-SEG-001` |
| SEG-02 | `assignment_rule` must be machine-evaluable; prose is rejected | **H** | `ERR-SEG-002` |
| SEG-03 | Every segment must have a default price list and SLA band | **H** | `ERR-SEG-003` |
| SEG-04 | `credit_terms_days` above zero requires `requires_contract` | **H** | `ERR-SEG-004` |
| SEG-05 | Manual segment override requires Commercial approval and a recorded reason | **A** | `ERR-SEG-005` |
| SEG-06 | A party matching no segment falls to `SEG-B2C` and warns | **S** | `WRN-SEG-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-029` Price lists | Before |
| `MD-028` SLA bands | Before |
| `MD-013` Party standard | Before |

| Depended on by |
|---|
| `M11` pricing resolution · `M35` campaign targeting · `RP-002` report catalogue · `P01` and `P04` entitlement display |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Commercial segmentation workshop |
| Who supplies it | Chief Commercial Officer |
| Collection method | Workshop, then rule expression authored and tested against migrated data |
| Known quality issues | Legacy segmentation is a free-text field with dozens of inconsistent values |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 8–15 segments | Low |
| SIT / UAT | All segments — pricing resolution is tested exhaustively | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Commercial analyst |
| Who may deactivate | Chief Commercial Officer |
| Approval required | CCO; Finance for a credit-terms change |
| Effective dating | **Yes** — assignment rules and defaults are effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
segment_code,segment_name_en,segment_name_bn,segment_class,assignment_rule,assignment_priority,default_price_list_code,default_sla_band_code,credit_terms_days,requires_contract,effective_from,active
SEG-ENT,Enterprise,এন্টারপ্রাইজ,enterprise,"party_type='organisation' AND active_contract_value_bdt>=2000000",10,PL-ENT,SLA-P1,45,TRUE,2026-07-01,TRUE
SEG-SME,Small and Medium Business,ক্ষুদ্র ও মাঝারি ব্যবসা,sme,"party_type='organisation' AND active_contract_value_bdt<2000000",20,PL-SME,SLA-P2,30,TRUE,2026-07-01,TRUE
SEG-B2C,Individual Customer,ব্যক্তিগত গ্রাহক,b2c,"party_type='individual'",90,PL-STD,SLA-P3,0,FALSE,2026-07-01,TRUE
```

---

## 10. Migration notes

Assigned by rule at load, not migrated. Legacy free-text segment values are mapped to the new codes in `DM-004` and the mapping is retained for reconciliation.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-013_Customer_and_Party_Master_Standard.md`](MD-013_Customer_and_Party_Master_Standard.md) | Parties segmented |
| `MD-029` Price List and Rate Card Seed | Default pricing |
| `MD-028` Priority, Severity and SLA Definition Register | Default SLA |
| `RP-001` KPI Dictionary | Segment-keyed metrics |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Commercial Officer (pending) |

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
