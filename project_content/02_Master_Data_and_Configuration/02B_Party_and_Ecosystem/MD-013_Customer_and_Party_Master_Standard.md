---
id: MD-013
title: Customer and Party Master Standard
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: MDM Lead
author: MDM with CRM and Data Migration
reviewers: [Commercial, Legal & Compliance, DPO, Data Migration Lead, Localisation Lead]
approver: Chief Commercial Officer
content_class: E
purpose: >
  The party model: individual versus organisation, the roles a party may hold, identity keys, and
  matching and merge rules. M33 owns the golden customer record; 250,000+ customers a month with
  no matching rules produces duplicate-driven failure in loyalty, warranty and collections.
traces_to: [M33, M07, 05-02, MD-006, MD-007, MD-014, DM-004, DM-011, LG-008]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-013_Customer_and_Party_Master_Standard_BN.md
data_file: MD-013_Customer_and_Party_Master_Standard.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33_Customer_and_Party_Master_Management.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §2 shared kernel — fix.party, fix.party.role, fix.party.hierarchy
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-013 — Customer and Party Master Standard

> **One party, many roles.** The same person may be a customer, an employee and a referral
> partner. Modelling them as three records is the single most damaging master-data decision
> available, and it is the default in most legacy systems.
>
> This file is a **standard**, not a dataset: it defines the model and the rules. The party
> records themselves are created by transactions and migration.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Party & ecosystem |
| Owning module | `M33` |
| Data steward | MDM Lead |
| Golden source | The ERP itself once live; before that, the CRM and service history |
| Refresh cadence | Continuous; matching rules reviewed per wave |
| Environments | Dev · SIT · UAT · Prod |
| Content class | E — Internal governance |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `party_id` | uuid | ✔ |  | — | Surrogate, permanent |
| `party_type` | enum | ✔ | individual / organisation | — | Fixed at creation; never changes |
| `display_name_en` | text(200) | ✔ |  | — |  |
| `display_name_bn` | text(200) |  |  | **✔** | Preferred for Bengali-language contact |
| `legal_name` | text(200) |  | Organisation only | — | As registered |
| `primary_mobile` | text(20) | ✔ | BD format `01[3-9]nnnnnnnn` | — | **The principal identity key** |
| `alt_mobile` | text(20) |  |  | — |  |
| `email` | text(120) |  |  | — |  |
| `nid_number` | text(20) |  | **S3** — Bangladesh-resident (`NFR-086`) | — | Individual; captured only where required |
| `bin` | text(20) |  | Organisation | — | Required for a VAT-registered buyer |
| `tin` | text(20) |  | **S3** — Bangladesh-resident | — |  |
| `primary_address_id` | fk |  | → `MD-007` | — |  |
| `segment_code` | fk | ✔ | → `MD-014` | — |  |
| `preferred_language` | enum | ✔ | bn / en; default **bn** | — | `PS-03` |
| `parent_party_id` | fk |  | Self-reference; organisation hierarchy | — | → `MD-015` |
| `match_confidence` | decimal(3,2) | ✔ | 0.00–1.00, computed | — | Duplicate risk |
| `golden_record_id` | fk |  | Self-reference | — | Set on merge; survivor points to itself |
| `consent_state` | enum | ✔ | See `LG-008` | — | Marketing consent, distinct from transactional |
| `active` | bool | ✔ |  | — |  |

### 2.1 Party roles — `fix.party.role`

A party holds one or more roles; roles are additive and time-bounded.

`customer` · `corporate_client` · `employee` · `vendor` · `seller` · `brand_partner` ·
`referral_partner` · `rider` · `courier_partner` · `recycling_partner` · `prospect`

> A party with both `employee` and `seller` roles is a segregation-of-duties question, not a
> data error. `SP-006` decides whether it is permitted.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `primary_mobile` for individuals; `bin` for VAT-registered organisations |
| Surrogate key | `party_id` (uuid) |
| Code format | No human-readable code — a customer number that encodes branch or year cannot survive a merge |
| Reuse policy | **Never reused.** A merged party is archived with `golden_record_id` pointing at the survivor |

### 3.1 Matching and merge rules

| Rule | Detail |
|---|---|
| **Deterministic match** | Same `primary_mobile` **and** same `party_type` → confidence 1.00, auto-merge candidate |
| **Strong probabilistic** | Same `nid_number`, or same `bin` → 0.95 |
| **Weak probabilistic** | Same name + same `upazila_code` + a device serial in common → 0.70, **manual review** |
| **Never auto-merge** | Confidence below 0.95, or where either party has an open financial balance |
| **Survivorship** | Most-recently-verified value wins; a rider-confirmed address beats a geocoded one; a manually verified value beats a derived one (`DM-011`) |
| **Merge is reversible for 30 days** | After that the merge is permanent and the archived record is retained for audit |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| PTY-01 | `primary_mobile` must match the Bangladesh mobile format and is mandatory | **H** | `ERR-PTY-001` |
| PTY-02 | `party_type` may never be changed after creation | **H** | `ERR-PTY-002` |
| PTY-03 | A VAT-registered organisation buyer must have a `bin` before a Mushak 6.3 can be issued | **H** | `ERR-PTY-003` |
| PTY-04 | Auto-merge is blocked below confidence 0.95 or where a financial balance is open | **H** | `ERR-PTY-004` |
| PTY-05 | S3 fields must be written to the Bangladesh-resident store (`NFR-086a`) | **H** | `ERR-PTY-005` |
| PTY-06 | Marketing contact requires `consent_state` permitting it (`LG-008`) | **H** | `ERR-PTY-006` |
| PTY-07 | Manual merge of two parties with different NIDs requires MDM Lead approval | **A** | `ERR-PTY-007` |
| PTY-08 | A party with no address after two completed services warns | **S** | `WRN-PTY-008` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-006` Geography | Before |
| `MD-007` Address standard | Before |
| `MD-014` Segment definition | Before or same load |

| Depended on by |
|---|
| `MD-015` corporate hierarchy · `MD-016` vendors · `MD-018` sellers · every service order, contract, invoice, claim and loyalty record |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Legacy CRM, service history, and the ERP itself once live |
| Who supplies it | MDM Lead; records created by transaction thereafter |
| Collection method | Migration `DM-004`, then continuous capture |
| Known quality issues | Legacy systems hold one row per **transaction**, not per party. Expect a high duplicate rate on first load — deduplication is the largest single migration task |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 300,000–1,500,000 parties at go-live depending on the history depth migrated | High |
| SIT / UAT | 2,000 including deliberate near-duplicates to exercise the matching rules (`TS-002`) | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Any authenticated channel; agents on behalf of customers |
| Who may deactivate | MDM Lead only, and never while a balance is open |
| Approval required | MDM Lead for a merge above 500 records |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
party_id,party_type,display_name_en,display_name_bn,primary_mobile,email,segment_code,preferred_language,match_confidence,consent_state,active
7f3a2b10,individual,Rahim Uddin,রহিম উদ্দিন,01712345678,rahim@example.com,SEG-B2C,bn,1.00,transactional_only,TRUE
9c4d5e20,organisation,Banglalink Digital Communications Ltd,,01911000000,it@example.com,SEG-ENT,en,1.00,marketing_opt_in,TRUE
```

---

## 10. Migration notes

`DM-004` Field Mapping Workbook — Party and Customer. **This is the highest-risk migration in the programme**: it is the most duplicated, least structured legacy data and the one users notice immediately.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-014_Customer_Segment_and_Tier_Definition.md`](MD-014_Customer_Segment_and_Tier_Definition.md) | Segmentation |
| [`MD-015_Corporate_Account_Hierarchy_Standard.md`](MD-015_Corporate_Account_Hierarchy_Standard.md) | Organisation hierarchy |
| [`../02A_Organisation_and_Network/MD-007_Address_Format_and_Validation_Standard.md`](../02A_Organisation_and_Network/MD-007_Address_Format_and_Validation_Standard.md) | Addresses |
| `DM-011` Data Quality Rules, Cleansing and Deduplication Standard | Survivorship |
| `LG-008` Privacy Notice and Consent Copy | Consent states |

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
