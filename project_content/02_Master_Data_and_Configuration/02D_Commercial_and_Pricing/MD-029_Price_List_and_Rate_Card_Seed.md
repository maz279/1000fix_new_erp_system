---
id: MD-029
title: Price List and Rate Card Seed
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial
author: Commercial with Finance
reviewers: [Finance, Tax, Operations, Account Management, Localisation Lead]
approver: Chief Commercial Officer
content_class: C
purpose: >
  Standard, corporate, brand-warranty, marketplace and refurbished price lists; labour rates;
  call-out charges; zone surcharges. Pricing is the most-changed and most-disputed data in the
  system and must be governed, versioned and effective-dated from day one.
traces_to: [M11, M36, MD-014, MD-019, MD-005, MD-037, EO-011, DT-005]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-029_Price_List_and_Rate_Card_Seed_BN.md
data_file: MD-029_Price_List_and_Rate_Card_Seed.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-029 — Price List and Rate Card Seed

> **Effective dating is not optional here.** A job is priced by the rate card in force on the day
> it was created, not the card in force when it is invoiced. Without that, every retrospective
> price change silently reprices open work.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Commercial & pricing |
| Owning module | `M11` |
| Data steward | Pricing analyst |
| Golden source | CCO-approved price list version |
| Refresh cadence | Quarterly, and on any approved change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `price_list_code` | char(8) | ✔ | `PL-nnn`, permanent | — |  |
| `price_list_name_en` | text(120) | ✔ |  | — |  |
| `price_list_name_bn` | text(120) | ✔ |  | **✔** | Shown where the customer sees the list name |
| `list_class` | enum | ✔ | standard / corporate / brand_warranty / marketplace / refurbished / internal | — |  |
| `segment_code` | fk |  | → `MD-014` | — | Default assignment |
| `brand_code` | fk |  | → `MD-017`; required for brand_warranty | — |  |
| `currency` | char(3) | ✔ | `BDT` | — |  |
| `tax_inclusive` | bool | ✔ |  | — | **Whether the price already contains VAT** |
| `effective_from` | date | ✔ |  | — |  |
| `effective_to` | date |  | Null = current | — |  |
| `approved_by` | text(120) | ✔ | Named approver | — |  |
| `active` | bool | ✔ |  | — |  |

### 2.1 Price line — `MD-029_Price_Lines.csv`

| Column | Type | Req | Note |
|---|---|:--:|---|
| `price_list_code` | fk | ✔ | |
| `item_code` | fk | ✔ | → `MD-019` |
| `unit_price` | decimal(14,2) | ✔ | Two decimals (`05-06` §9) |
| `min_price` / `max_price` | decimal(14,2) | | Discount floor and estimate ceiling |
| `labour_rate_per_hour` | decimal(14,2) | | Services |
| `zone_surcharge_pct` | decimal(5,2) | | Applies per `MD-005` zone type |
| `effective_from` / `effective_to` | date | ✔ / | Line-level dating |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `list_class` + `segment_code` + `brand_code` |
| Surrogate key | `price_list_code` |
| Code format | `PL-nnn` |
| Reuse policy | Never reused; invoices reference the version applied |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| PRC-01 | A price line may not overlap another for the same item and list on the same date | **H** | `ERR-PRC-001` |
| PRC-02 | An order is priced by the version effective on its creation date, never the current version | **H** | `ERR-PRC-002` |
| PRC-03 | A discount below `min_price` requires approval per `MD-030` | **A** | `ERR-PRC-003` |
| PRC-04 | A brand_warranty list requires a `brand_code` and must match the agreement rate card | **H** | `ERR-PRC-004` |
| PRC-05 | `tax_inclusive` must be consistent within a list | **H** | `ERR-PRC-005` |
| PRC-06 | A sellable item with no price on any active list warns | **S** | `WRN-PRC-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-019` Catalogue | **Before** |
| `MD-014` Segments | Before |
| `MD-017` Brands | Before |
| `MD-037` Tax | Before |

| Depended on by |
|---|
| `M11` pricing engine · `M36` quotations · `DT-005` estimates · `DT-010` invoices · `MD-020` mode charges · `EO-011` rate-card communication |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Existing price sheets, brand rate cards and the CCO pricing decision |
| Who supplies it | CCO with Finance |
| Collection method | Transcription from approved price sheets, then Finance verification of tax treatment |
| Known quality issues | Legacy pricing lives in spreadsheets with no effective dating; the price applied to a historical job cannot be reconstructed |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 8–20 lists; 30,000–150,000 price lines | Continuous |
| SIT / UAT | 1,500 lines across all list classes | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Pricing analyst |
| Who may deactivate | CCO |
| Approval required | **CCO for every change**; Finance for tax-inclusive treatment |
| Effective dating | **Yes — mandatory** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
price_list_code,price_list_name_en,price_list_name_bn,list_class,segment_code,currency,tax_inclusive,effective_from,approved_by,active
PL-STD,Standard Retail,স্ট্যান্ডার্ড রিটেইল,standard,SEG-B2C,BDT,TRUE,2026-07-01,Chief Commercial Officer,TRUE
PL-ENT,Enterprise Contract,এন্টারপ্রাইজ চুক্তি,corporate,SEG-ENT,BDT,FALSE,2026-07-01,Chief Commercial Officer,TRUE
```

---

## 10. Migration notes

Not migrated as history — the current approved list is loaded with an effective date of go-live. Historical pricing is retained in the archive for reference only (`DM-001`).

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-030_Discount_Promotion_and_Voucher_Rule_Register.md`](MD-030_Discount_Promotion_and_Voucher_Rule_Register.md) | Discount floors |
| [`../02C_Catalogue_and_Technical/MD-019_Product_and_Service_Catalogue_Seed.md`](../02C_Catalogue_and_Technical/MD-019_Product_and_Service_Catalogue_Seed.md) | Priced items |
| `EO-011` Rate Card and Pricing Communication Pack | How changes are communicated |
| `M11` Pricing, Rate Cards and Dynamic Pricing | The implementing module |

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
