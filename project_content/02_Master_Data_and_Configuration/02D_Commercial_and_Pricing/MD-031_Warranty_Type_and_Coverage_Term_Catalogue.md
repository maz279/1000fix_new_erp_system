---
id: MD-031
title: Warranty Type and Coverage Term Catalogue
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Warranty
author: Warranty with Legal
reviewers: [Legal & Compliance, Commercial, Finance, Technical, Localisation Lead]
approver: Legal Counsel
content_class: B
purpose: >
  Manufacturer, service, extended and protection-plan warranty types with coverage, exclusions,
  duration and claim rules. Warranty eligibility is a hard rule at order creation (BRU-SRM-02);
  the rule needs a catalogue to evaluate against.
traces_to: [M09, 05-05 BRU-SRM-02, MD-017, MD-021, MD-025, LG-013, DT-032]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: MD-031_Warranty_Type_and_Coverage_Term_Catalogue_BN.md
data_file: MD-031_Warranty_Type_and_Coverage_Term_Catalogue.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-02 — a warranty-type order can only be created if the device warranty is active at the service request date
    verified: 2026-08-15
    class: P1
  - source: Executed brand authorisation agreements and the approved service terms held in `M24`
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-031 — Warranty Type and Coverage Term Catalogue

> ⚠ **Class B — legal.** Coverage and exclusions are contractual text. This catalogue and
> `LG-013` Service Terms, Warranty Terms and Exclusions must state the same thing; where they
> differ, `LG-013` governs and this catalogue is corrected.
>
> The word **insurance** is never used for any of these (`CG-013` §2.4 — regulated term).

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Commercial & pricing |
| Owning module | `M09` |
| Data steward | Warranty officer |
| Golden source | Executed brand agreements and the approved service terms |
| Refresh cadence | Annual; on any terms change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | B — Legal / contractual |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `warranty_type_code` | char(9) | ✔ | `WTY-nnnnn`, permanent | — |  |
| `warranty_class` | enum | ✔ | manufacturer / service_repair / extended_purchased / protection_plan / refurbished | — |  |
| `name_en` | text(120) | ✔ | Registered name (`VB-010`) | — |  |
| `name_bn` | text(120) | ✔ |  | **✔** | On `DT-032` certificate |
| `brand_code` | fk |  | → `MD-017`; manufacturer class | — |  |
| `device_families` | multi-fk | ✔ | → `MD-021` | — |  |
| `duration_months` | int | ✔ |  | — |  |
| `starts_from` | enum | ✔ | purchase_date / service_completion / activation | — |  |
| `covers` | multi-enum | ✔ | parts / labour / on_site / pickup / replacement | — |  |
| `exclusions` | text(1000) | ✔ | **Must match `LG-013` verbatim** | — |  |
| `claim_window_days` | int | ✔ |  | — |  |
| `transferable` | bool | ✔ |  | — | On device resale |
| `is_sellable` | bool | ✔ |  | — | Purchased products only |
| `item_code` | fk |  | → `MD-019`; required when sellable | — |  |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `warranty_class` + `brand_code` + `name_en` |
| Surrogate key | `warranty_type_code` |
| Code format | `WTY-nnnnn` |
| Reuse policy | Never reused; issued warranties reference it for their full life |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| WTY-01 | A warranty-type service order requires an active warranty at the request date (`BRU-SRM-02`) | **H** | `ERR-WTY-001` |
| WTY-02 | `exclusions` must match `LG-013`; a divergence blocks activation | **H** | `ERR-WTY-002` |
| WTY-03 | A manufacturer warranty requires a `brand_code` within its authorisation scope | **H** | `ERR-WTY-003` |
| WTY-04 | `is_sellable` TRUE requires an `item_code` and a price on an active list | **H** | `ERR-WTY-004` |
| WTY-05 | `name_bn` is mandatory | **H** | `ERR-WTY-005` |
| WTY-06 | Changing coverage or exclusions on a type with issued warranties is prohibited — issue a new type | **H** | `ERR-WTY-006` |
| WTY-07 | A repair resolution with `grants_repair_warranty` and no matching type warns | **S** | `WRN-WTY-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-017` Brands | Before |
| `MD-021` Device families | Before |
| `MD-019` Catalogue | Before for sellable types |

| Depended on by |
|---|
| `M09` warranty and claims · `DT-032` warranty certificate · `LG-013` service terms · `MD-032` contract templates |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Executed brand agreements and the approved service terms |
| Who supplies it | Warranty officer with Legal |
| Collection method | Agreement and terms review, clause by clause |
| Known quality issues | Existing warranty terms are stated in marketing content and on receipts, and have not been reconciled with brand agreements |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 60–150 types | Low |
| SIT / UAT | 30 across all classes | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Warranty officer |
| Who may deactivate | Legal Counsel |
| Approval required | **Legal Counsel**; CCO for a sellable product |
| Effective dating | **Yes** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
warranty_type_code,warranty_class,name_en,name_bn,brand_code,duration_months,starts_from,covers,claim_window_days,transferable,is_sellable,effective_from,active
WTY-00101,service_repair,30-day repair warranty,৩০ দিনের মেরামত ওয়ারেন্টি,,1,service_completion,parts;labour,30,FALSE,FALSE,2026-07-01,TRUE
WTY-00210,manufacturer,Samsung standard warranty,স্যামসাং স্ট্যান্ডার্ড ওয়ারেন্টি,BRD-005,24,purchase_date,parts;labour,30,TRUE,FALSE,2026-07-01,TRUE
WTY-00401,extended_purchased,FiXCare Extended 12 months,ফিক্সকেয়ার এক্সটেন্ডেড ১২ মাস,,12,activation,parts;labour;pickup,30,TRUE,TRUE,2026-07-01,TRUE
```

---

## 10. Migration notes

`DM-010` contracts, warranty and claims. Warranty registrations must migrate with their **original terms**, not the current version — WTY-06 exists for this reason.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| `LG-013` Service Terms, Warranty Terms and Exclusions | **Governs the exclusion text** |
| `DT-032` Warranty Certificate and Extension Document | Where terms are printed |
| [`MD-032_Contract_and_AMC_Template_Catalogue.md`](MD-032_Contract_and_AMC_Template_Catalogue.md) | Contract-bundled warranty |
| `M09` Warranty, Protection Plans and Claims | The implementing module |

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
