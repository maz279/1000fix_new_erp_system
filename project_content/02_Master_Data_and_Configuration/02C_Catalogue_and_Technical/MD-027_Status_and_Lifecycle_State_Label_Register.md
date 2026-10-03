---
id: MD-027
title: Status and Lifecycle State Label Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture
author: Enterprise Architecture with Content Design
reviewers: [Content Design Lead, Design System, Localisation Lead, all module owners]
approver: Architecture Review Board
content_class: C
purpose: >
  The canonical state name and customer-facing label for every state machine in the system, in both
  languages. 05-02 DM-10 requires one declared transition map per model; customer, technician and
  agent must see the same state named the same way, and the customer must never see an internal name.
traces_to: [05-02 DM-10, VB-008, CG-004 T-06, UI-002, BN-003]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-027_Status_and_Lifecycle_State_Label_Register_BN.md
data_file: MD-027_Status_and_Lifecycle_State_Label_Register.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 DM-10 — an explicit state selection field with the transition map declared in one place
    verified: 2026-08-15
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-008 §4 state register
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-027 — Status and Lifecycle State Label Register

> **`VB-008` decides how a state looks. This register decides what a state *is* and what it is
> called.** The two are ratified together and neither is authoritative alone.
>
> The internal name and the customer-facing label are **different fields on purpose**
> (`CG-004` `T-06`). `sla_breached` internally is "Delayed" to a customer.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Catalogue & technical |
| Owning module | `M30` |
| Data steward | Enterprise Architecture analyst |
| Golden source | Each module's declared transition map (`05-02` DM-10) |
| Refresh cadence | Per wave |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `state_id` | char(12) | ✔ | `ST-<model>-nnn`, permanent | — |  |
| `model_name` | text(60) | ✔ | The `fix.*` model owning the state machine | — | → `05-02` |
| `state_key` | text(40) | ✔ | The technical value stored | — | **Never shown to a customer** |
| `internal_label_en` | text(60) | ✔ |  | — | Shown to staff |
| `internal_label_bn` | text(60) | ✔ |  | **✔** |  |
| `customer_label_en` | text(60) |  | Null where the state is not customer-visible | — |  |
| `customer_label_bn` | text(60) |  |  | **✔** |  |
| `is_customer_visible` | bool | ✔ |  | — |  |
| `semantic_token` | fk | ✔ | → `VB-008` §3.1 — one of eight | — | Colour and glyph |
| `state_order` | int | ✔ | Display and progress order | — |  |
| `is_terminal` | bool | ✔ |  | — | No outbound transitions |
| `allowed_next_states` | multi-fk | ✔ | Self-reference | — | **The transition map** |
| `requires_reason` | bool | ✔ |  | — | → `MD-026` |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `model_name` + `state_key` |
| Surrogate key | `state_id` |
| Code format | `ST-<model>-nnn` |
| Reuse policy | Never reused; audit trails reference the key |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| STA-01 | Every `fix.*` model with a `state` field must have a complete register entry set | **H** | `ERR-STA-001` |
| STA-02 | A transition not in `allowed_next_states` is rejected | **H** | `ERR-STA-002` |
| STA-03 | `is_customer_visible` TRUE requires both customer labels | **H** | `ERR-STA-003` |
| STA-04 | **A state key may never be displayed to a customer** (`T-06`) | **H** | `ERR-STA-004` |
| STA-05 | Every state must map to one of the eight `VB-008` semantic tokens | **H** | `ERR-STA-005` |
| STA-06 | Every model must have at least one terminal state | **H** | `ERR-STA-006` |
| STA-07 | A state with no inbound transition warns — it is unreachable | **S** | `WRN-STA-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `05-02` transition maps | **Before** — extracted from them |
| `VB-008` semantic tokens | Before |

| Depended on by |
|---|
| `VB-008` · `UI-002` labels · every list, badge, timeline and report showing a state · `NT-001` event-to-notification matrix |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Each module file's §8 Lifecycle and State Model section |
| Who supplies it | Enterprise Architecture, by extraction from all 67 module files |
| Collection method | **Enumeration** (`RG-06`) — extract every declared state machine, do not rely on a summary |
| Known quality issues | Not every module file declares its transition map to the same depth; gaps must be closed with the module owner |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 600–1,200 states across all state machines | Low |
| SIT / UAT | All states for the W1 models | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Enterprise Architecture analyst |
| Who may deactivate | Architecture Review Board |
| Approval required | ARB; **Content Design for any label**, Localisation for Bengali |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
state_id,model_name,state_key,internal_label_en,internal_label_bn,customer_label_en,customer_label_bn,is_customer_visible,semantic_token,state_order,is_terminal,requires_reason,active
ST-SO-010,fix.service.order,submitted,Submitted,জমা দেওয়া হয়েছে,Booking received,বুকিং গৃহীত হয়েছে,TRUE,status-info,10,FALSE,FALSE,TRUE
ST-SO-070,fix.service.order,awaiting_parts,Awaiting parts,পার্টসের অপেক্ষায়,Waiting for a part,পার্টসের অপেক্ষায়,TRUE,status-hold,70,FALSE,TRUE,TRUE
ST-SO-140,fix.service.order,sla_breached,SLA breached,এসএলএ লঙ্ঘিত,Delayed,বিলম্বিত,TRUE,status-error,140,FALSE,TRUE,TRUE
ST-SO-160,fix.service.order,cancelled,Cancelled,বাতিল,Cancelled,বাতিল,TRUE,status-inactive,160,TRUE,TRUE,TRUE
```

---

## 10. Migration notes

Not migrated. Legacy statuses are mapped to the new state keys in `DM-006`, with the mapping retained for historical reporting continuity.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../../01_Voice_Brand_and_Design_Content/VB-008_Status_Colour_and_Label_Semantics_Register.md`](../../01_Voice_Brand_and_Design_Content/VB-008_Status_Colour_and_Label_Semantics_Register.md) | How states look |
| [`MD-026_Reason_Code_Register.md`](MD-026_Reason_Code_Register.md) | Reasons accompanying transitions |
| `CG-004` Terminology Standard | `T-06` internal versus customer-facing |
| `BN-003` Bilingual Terminology Glossary | Authoritative Bengali labels |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Architecture Review Board (pending) |

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
