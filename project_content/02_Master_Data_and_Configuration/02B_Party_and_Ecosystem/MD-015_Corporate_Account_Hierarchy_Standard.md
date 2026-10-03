---
id: MD-015
title: Corporate Account Hierarchy Standard
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Account Management
author: Account Management with Finance
reviewers: [Finance, Commercial, Enterprise Architecture, Legal]
approver: Chief Commercial Officer
content_class: C
purpose: >
  Defines group to company to division to site to department to user structures, with billing and
  approval roll-up rules. P04 commits to multi-site, multi-level approval and consolidated
  invoicing; the hierarchy rules must precede the build or every corporate onboarding invents its own.
traces_to: [P04, M07, M08, MD-013, MD-007, DT-020, EO-008]
priority: P1
wave: W4
bilingual: no
bn_counterpart: n/a
data_file: MD-015_Corporate_Account_Hierarchy_Standard.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P04 corporate B2B portal — multi-user access, multi-level approval chains, multiple sites and departments
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-015 — Corporate Account Hierarchy Standard

> A corporate client is not one party. It is a tree, and **the tree decides who may approve what
> and which invoice a job lands on**. Getting it wrong produces approval deadlocks that the
> client experiences as our failure.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Party & ecosystem |
| Owning module | `M07` |
| Data steward | Account Management analyst |
| Golden source | The executed master service agreement and the client-confirmed structure |
| Refresh cadence | On contract signature and on any client restructure |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `node_id` | uuid | ✔ |  | — |  |
| `party_id` | fk | ✔ | → `MD-013` | — | The organisation party |
| `parent_node_id` | fk |  | Self-reference; max depth 5 | — |  |
| `node_level` | enum | ✔ | group / company / division / site / department | — |  |
| `node_name` | text(160) | ✔ |  | — |  |
| `address_id` | fk |  | → `MD-007`; required at `site` | — |  |
| `is_billing_node` | bool | ✔ |  | — | Where an invoice is raised |
| `billing_cycle` | enum |  | monthly / fortnightly / per_job; required when billing | — |  |
| `cost_centre_ref` | text(60) |  | The **client's** cost centre, not ours | — | Printed on `DT-020` |
| `approval_chain_id` | fk |  | → §2.1 | — |  |
| `contract_id` | fk |  | → `M08` | — | Covering contract |
| `sla_band_code` | fk |  | → `MD-028`; inherits from parent when null | — |  |
| `active` | bool | ✔ |  | — |  |

### 2.1 Approval chain

| Level | Typical role | Set by |
|---|---|---|
| 1 | Requesting user | Client |
| 2 | Line manager | Client |
| 3 | Site or department head | Client |
| 4 | 1000FiX account manager | Us — only where the contract requires our counter-approval |

Chains are defined **per node** and inherit downward unless overridden.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `party_id` + `parent_node_id` + `node_name` |
| Surrogate key | `node_id` (uuid) |
| Code format | No code — client structures rename frequently |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| CAH-01 | Hierarchy depth may not exceed 5 and may not contain a cycle | **H** | `ERR-CAH-001` |
| CAH-02 | At least one node per client must be a billing node | **H** | `ERR-CAH-002` |
| CAH-03 | A billing node must have a billing cycle and an address | **H** | `ERR-CAH-003` |
| CAH-04 | A site node must have an address | **H** | `ERR-CAH-004` |
| CAH-05 | An approval chain must terminate — a chain with no final approver is rejected | **H** | `ERR-CAH-005` |
| CAH-06 | A node may not be archived while it has open service orders or unbilled charges | **H** | `ERR-CAH-006` |
| CAH-07 | Changing a billing node mid-cycle requires Finance approval | **A** | `ERR-CAH-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-013` Party standard | **Before** |
| `MD-007` Addresses | Before |
| `MD-028` SLA bands | Before |

| Depended on by |
|---|
| `P04` corporate portal · `M08` contracts · `DT-020` consolidated invoice · `EO-008` corporate admin setup guide |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Client-confirmed organisation structure at onboarding |
| Who supplies it | Account Manager, confirmed in writing by the client administrator |
| Collection method | Structured onboarding form; bulk site upload by CSV where the client has many sites |
| Known quality issues | Clients frequently do not know their own site list. Expect the structure to be incomplete at go-live and to grow |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 500–2,000 corporate users across 50–300 client trees | Low |
| SIT / UAT | 3 complete client trees of differing shapes | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Account Manager or the client administrator |
| Who may deactivate | Account Manager |
| Approval required | Finance for a billing-node change; the client for their own structure |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
node_id,party_id,parent_node_id,node_level,node_name,is_billing_node,billing_cycle,cost_centre_ref,sla_band_code,active
c1a1,9c4d5e20,,company,Head Office,TRUE,monthly,HO-FIN-01,SLA-P1,TRUE
c1a2,9c4d5e20,c1a1,division,Network Operations,FALSE,,NOC-002,,TRUE
c1a3,9c4d5e20,c1a2,site,Gulshan Data Centre,FALSE,,NOC-002-DC,SLA-P0,TRUE
```

---

## 10. Migration notes

Not migrated — captured at corporate onboarding (`EO-007`). Legacy corporate records hold one flat account per client.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-013_Customer_and_Party_Master_Standard.md`](MD-013_Customer_and_Party_Master_Standard.md) | The organisation party |
| `DT-020` Consolidated Corporate Invoice | Billing roll-up |
| `EO-008` Corporate Admin Setup and Delegation Guide | How clients configure this |
| `P04` Corporate B2B Portal | The consuming surface |

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
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
