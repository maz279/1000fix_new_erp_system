---
id: MD-002
title: Legal Entity and Company Master
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Finance with Legal
reviewers: [Legal & Compliance, Tax, Enterprise Architecture, MDM Lead]
approver: Chief Financial Officer
content_class: C
purpose: >
  Defines every legal entity in the group with its statutory identity, fiscal calendar and
  functional currency. Multi-entity operation (M65) and every statutory document derive from it;
  no invoice, filing or posting can be produced without a correctly registered entity.
traces_to: [M65, M51, M19, MD-035, MD-040, DT-010]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-002_Legal_Entity_and_Company_Master.csv
effective_dated: no
sources:
  - source: Company registration and BIN/TIN certificates held in `M24`
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M65_Multi_Entity_Multi_Country_and_Localisation.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-002 — Legal Entity and Company Master

> Small dataset, maximum consequence. Every Mushak 6.3 challan, every filing and every ledger
> posting carries the entity identity from this table. A wrong BIN is an invalid invoice.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Organisation & network |
| Owning module | `M65` |
| Data steward | Finance systems analyst |
| Golden source | Registrar of Joint Stock Companies certificate + NBR BIN/TIN certificates |
| Refresh cadence | On incorporation, restructuring or statutory identifier change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `entity_code` | char(4) | ✔ | `EN-nn`, unique, permanent | — | Internal entity code |
| `legal_name` | text(200) | ✔ | Exactly as registered | — | Registered legal name |
| `trading_name` | text(200) | | | — | Name used commercially |
| `entity_type` | enum | ✔ | private_limited / public_limited / branch | — | |
| `registration_no` | text(50) | ✔ | RJSC number | — | |
| `bin` | text(20) | ✔ | 13-digit NBR Business Identification Number | — | **Printed on every Mushak** |
| `tin` | text(20) | ✔ | 12-digit Taxpayer Identification Number | — | Classified S3 (`05-02` §10) |
| `vat_circle` | text(60) | ✔ | NBR VAT circle | — | Determines filing office |
| `vat_division` | text(60) | ✔ | NBR VAT division | — | |
| `vat_commissionerate` | text(60) | ✔ | | — | |
| `registered_address_id` | fk | ✔ | → `MD-007` address | — | Statutory address |
| `functional_currency` | char(3) | ✔ | ISO 4217; `BDT` for all current entities | — | |
| `fiscal_year_start` | date | ✔ | 1 July (`05-06` §9) | — | |
| `fiscal_year_end` | date | ✔ | 30 June | — | |
| `incorporation_date` | date | ✔ | | — | |
| `chart_of_accounts_id` | fk | ✔ | → `MD-035` | — | |
| `is_vat_registered` | bool | ✔ | | — | Drives Mushak obligation |
| `is_vds_authority` | bool | ✔ | | — | Whether the entity must deduct VAT at source |
| `active` | bool | ✔ | Default TRUE | — | Archive flag (`DM-06`) |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `bin` — one BIN, one entity |
| Surrogate key | `entity_code` |
| Code format | `EN-nn`, zero-padded, sequential |
| Reuse policy | **Never reused.** A dissolved entity keeps its code permanently (`GR-04`) |

> **Odoo binding.** Extends `res.company`; `05-02` names the entity as `fix.entity`.

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| ENT-01 | `bin` must be 13 digits and unique across active and archived entities | **H** | `ERR-ENT-001` |
| ENT-02 | `tin` must be 12 digits | **H** | `ERR-ENT-002` |
| ENT-03 | A VAT-registered entity must have `vat_circle`, `vat_division` and `vat_commissionerate` | **H** | `ERR-ENT-003` |
| ENT-04 | Fiscal year must be 1 July – 30 June | **H** | `ERR-ENT-004` |
| ENT-05 | An entity may not be archived while it has open financial periods | **H** | `ERR-ENT-005` |
| ENT-06 | Changing a `bin` requires CFO approval and a recorded reason | **A** | `ERR-ENT-006` |
| ENT-07 | `functional_currency` other than BDT warns — no such entity exists today | **S** | `WRN-ENT-007` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `MD-007` Address format | 1 : 1 | Standard must exist first |
| `MD-035` Chart of accounts | 1 : 1 | May load after, then bind |
| `MD-041` Fiscal calendar | 1 : n | After |

| Depended on by |
|---|
| `MD-003` branches · `MD-008` org structure · `MD-036` dimensions · `MD-037` tax codes · `MD-040` sequences · every transactional table via `company_id` (`05-02` DM-03) |

**This is the first dataset loaded.**

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | RJSC incorporation certificate; NBR BIN and TIN certificates |
| Who supplies it | Company Secretary and Finance |
| Collection method | Certificate transcription, double-keyed and verified against the certificate image |
| Known quality issues | VAT circle/division/commissionerate are frequently recorded inconsistently in legacy records |
| Cleansing rules | `DM-011`; BIN and TIN verified digit-by-digit against the certificate, not against a spreadsheet |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 1–3 today | Grows only on incorporation or acquisition |
| SIT / UAT | 2 minimum — one to prove multi-entity separation | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Company Secretary, on incorporation |
| Who may deactivate | CFO, on dissolution, and only with all periods closed |
| Approval required | CFO for any change; Legal for a legal-name change |
| Effective dating | Statutory identifier changes are effective-dated; the prior value is retained for filings already made |
| Archive rule | Archived, never deleted (`05-02` DM-06) |

---

## 9. Sample rows

```csv
entity_code,legal_name,trading_name,entity_type,bin,tin,vat_circle,functional_currency,fiscal_year_start,fiscal_year_end,is_vat_registered,is_vds_authority,active
EN-01,1000FiX Services Limited,1000FiX,private_limited,0000000000000,000000000000,<circle>,BDT,2026-07-01,2027-06-30,TRUE,TRUE,TRUE
```

---

## 10. Migration notes

Migrated from the finance system's company record. **Do not migrate — re-key from the
certificates.** Legacy company records commonly carry a transposed BIN that has never mattered
because no system validated it. See `DM-008`.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-003_Branch_and_Service_Centre_Master.md`](MD-003_Branch_and_Service_Centre_Master.md) | Branches belong to an entity |
| [`MD-007_Address_Format_and_Validation_Standard.md`](MD-007_Address_Format_and_Validation_Standard.md) | Registered address format |
| `MD-035` Chart of Accounts | Bound per entity |
| `MD-037` Tax Code, VAT Rate and Mushak Mapping | Uses the entity BIN |
| `DT-010` Tax Invoice Mushak 6.3 | Prints the entity identity |
| `M65` Multi-Entity, Multi-Country and Localisation | The implementing module |

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
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
