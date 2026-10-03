---
id: MD-026
title: Reason Code Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations with Quality
author: Operations with Quality and Finance
reviewers: [Quality, Finance, HR, BI Lead, Localisation Lead]
approver: Operations Director
content_class: C
purpose: >
  Cancellation, rejection, return, exception, delay, override and refund reasons across all modules.
  Every override must record a reason (BR-STD-06); ad-hoc per-module reason lists make root-cause
  analysis impossible and let the same cause be counted under four names.
traces_to: [05-05 BR-STD-06, M30, MD-027, UI-007, RP-001, SP-028]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: MD-026_Reason_Code_Register_BN.md
data_file: MD-026_Reason_Code_Register.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §1 BR-STD-06 — overrides possible only where designed, always logged with a reason and an approver
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-026 — Reason Code Register

> **One register, all modules.** A cancellation reason in `M01`, a rejection reason in `M09` and a
> return reason in `M15` are the same kind of object. Kept separately, they cannot be analysed
> together — and the analysis is the point.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Catalogue & technical |
| Owning module | `M30` |
| Data steward | Operations analyst |
| Golden source | Cross-functional reason workshop |
| Refresh cadence | Quarterly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `reason_code` | char(10) | ✔ | `RSN-nnnnn`, permanent | — |  |
| `reason_context` | enum | ✔ | cancellation / rejection / return / exception / delay / override / refund / leave / adjustment | — |  |
| `module_scope` | multi-fk | ✔ | `Mnn` — which modules may use it | — |  |
| `description_en` | text(200) | ✔ |  | — |  |
| `description_bn` | text(200) | ✔ |  | **✔** | Shown to customers and field staff |
| `attributable_to` | enum | ✔ | customer / 1000fix / vendor / brand / logistics / external / unknown | — | **Drives root-cause reporting** |
| `requires_free_text` | bool | ✔ |  | — | Forces an explanation |
| `requires_approval` | bool | ✔ |  | — | Ties to `SP-004` |
| `is_chargeable` | bool | ✔ |  | — | Whether the customer is still charged |
| `triggers_capa` | bool | ✔ |  | — | Raises an `M23` quality record |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `reason_context` + `description_en` |
| Surrogate key | `reason_code` |
| Code format | `RSN-nnnnn` |
| Reuse policy | Never reused; trend analysis depends on stability |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| RSN-01 | Every cancellation, rejection, return and override must carry a reason code | **H** | `ERR-RSN-001` |
| RSN-02 | `requires_free_text` TRUE blocks submission without an explanation | **H** | `ERR-RSN-002` |
| RSN-03 | `requires_approval` TRUE routes to the `SP-004` approver before taking effect | **H** | `ERR-RSN-003` |
| RSN-04 | `attributable_to` may not be `unknown` on more than 5% of records in a period | **S** | `WRN-RSN-004` |
| RSN-05 | Adding a reason code requires Operations and Quality agreement | **A** | `ERR-RSN-005` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| Nothing structural | Early |

| Depended on by |
|---|
| Every module recording an exception · `UI-007` override dialogs · `RP-001` root-cause metrics · `SP-028` complaint handling |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Cross-functional workshop; seeded from legacy free-text exception notes |
| Who supplies it | Operations Director |
| Collection method | Workshop plus text analysis of legacy notes |
| Known quality issues | Legacy reasons are free text and module-specific; the same cause appears under many labels |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 150–400 codes | Low |
| SIT / UAT | 80 across all contexts | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Operations analyst |
| Who may deactivate | Operations Director |
| Approval required | Operations Director and Quality Manager |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
reason_code,reason_context,module_scope,description_en,description_bn,attributable_to,requires_free_text,requires_approval,is_chargeable,triggers_capa,active
RSN-00101,cancellation,M01;M03,Customer changed mind,গ্রাহক সিদ্ধান্ত পরিবর্তন করেছেন,customer,FALSE,FALSE,FALSE,FALSE,TRUE
RSN-00210,delay,M01;M15,Part not available in network,নেটওয়ার্কে পার্টস নেই,1000fix,TRUE,FALSE,FALSE,TRUE,TRUE
RSN-00455,override,M01,Estimate approved verbally by customer,গ্রাহক মৌখিকভাবে অনুমোদন দিয়েছেন,1000fix,TRUE,TRUE,TRUE,FALSE,TRUE
```

---

## 10. Migration notes

Not migrated — authored. Legacy free-text reasons are mapped where the top strings allow.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-027_Status_and_Lifecycle_State_Label_Register.md`](MD-027_Status_and_Lifecycle_State_Label_Register.md) | States a reason accompanies |
| `UI-007` Confirmation and Destructive Action Library | Where reasons are captured |
| `SP-028` SOP Complaint, Escalation and Compensation | Attribution feeds this |

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
