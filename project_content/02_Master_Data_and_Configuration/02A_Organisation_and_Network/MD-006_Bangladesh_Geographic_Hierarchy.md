---
id: MD-006
title: Bangladesh Geographic Hierarchy
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: MDM Lead
author: MDM with Localisation
reviewers: [Operations, Finance, Localisation Lead, Marketing, Enterprise Architecture]
approver: MDM Lead
content_class: C
purpose: >
  The canonical geography of Bangladesh: 8 divisions, 64 districts, upazilas and thanas, unions and
  wards, with postcodes and bilingual names. Addresses, coverage, tax jurisdiction, reporting and
  the public locator all need one geography, or they silently disagree.
traces_to: [M65, 05-02, MD-003, MD-005, MD-007, MD-013, RP-011]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-006_Bangladesh_Geographic_Hierarchy_BN.md
data_file: MD-006_Bangladesh_Geographic_Hierarchy.csv
effective_dated: no
sources:
  - source: Bangladesh administrative geography — 8 divisions and 64 districts are stable and authoritative; upazila counts vary by source and changed during 2026
    verified: 2026-08-15
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 localisation standards
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-006 — Bangladesh Geographic Hierarchy

> **8 divisions and 64 districts are stable.** Below that, the count moves: published sources
> give upazila totals between 495 and 548, and further upazilas were created during 2026.
>
> **Consequence for this dataset:** divisions and districts are loaded as fact; upazila and below
> are loaded with a `source_version` and re-verified annually. A dataset that pretends the lower
> levels are stable will silently drift out of date.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Organisation & network |
| Owning module | `M65` |
| Data steward | MDM analyst |
| Golden source | Bangladesh Bureau of Statistics / Local Government Division published administrative lists |
| Refresh cadence | Annual, and on any gazetted administrative change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `geo_code` | text(12) | ✔ | Unique, permanent | — | |
| `parent_geo_code` | fk | | Self-reference | — | |
| `geo_level` | enum | ✔ | division / district / upazila / thana / union / ward / city_corporation / municipality | — | |
| `name_en` | text(120) | ✔ | | — | |
| `name_bn` | text(120) | ✔ | | **✔** | |
| `alt_names_en` | text(300) | | Semicolon-separated | — | Chittagong/Chattogram, Jessore/Jashore, Comilla/Cumilla |
| `postcode` | char(4) | | 4-digit, at the level that carries one | — | |
| `bbs_code` | text(12) | | Official statistical code where published | — | Traceability to the source |
| `is_metropolitan` | bool | ✔ | | — | |
| `source_version` | text(20) | ✔ | e.g. `2026-05` | — | **Which published list this row came from** |
| `active` | bool | ✔ | | — | |

### 2.1 The eight divisions — loaded as fact

| `geo_code` | English | Bengali |
|---|---|---|
| `DHA` | Dhaka | ঢাকা |
| `CTG` | Chattogram | চট্টগ্রাম |
| `RAJ` | Rajshahi | রাজশাহী |
| `KHU` | Khulna | খুলনা |
| `BAR` | Barishal | বরিশাল |
| `SYL` | Sylhet | সিলেট |
| `RAN` | Rangpur | রংপুর |
| `MYM` | Mymensingh | ময়মনসিংহ |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `parent_geo_code` + `name_en` |
| Surrogate key | `geo_code` — three-letter for divisions, hierarchical below |
| Code format | Division `AAA`; district `AAA-NN`; upazila `AAA-NN-NN` |
| Reuse policy | Never reused. A merged or renamed unit is archived and a new code issued |

> **Renames are not updates.** Chittagong → Chattogram was a rename; Jessore → Jashore likewise.
> Both spellings must resolve in search, which is why `alt_names_en` exists.

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| GEO-01 | `name_bn` is mandatory at every level | **H** | `ERR-GEO-001` |
| GEO-02 | Every non-division row must have a valid `parent_geo_code` | **H** | `ERR-GEO-002` |
| GEO-03 | Exactly 8 rows at `geo_level = division` | **H** | `ERR-GEO-003` |
| GEO-04 | Exactly 64 rows at `geo_level = district` | **H** | `ERR-GEO-004` |
| GEO-05 | `source_version` mandatory at upazila level and below | **H** | `ERR-GEO-005` |
| GEO-06 | Postcode, where present, must be 4 digits | **H** | `ERR-GEO-006` |
| GEO-07 | A geography may not be archived while an address, branch or zone references it | **H** | `ERR-GEO-007` |
| GEO-08 | A row whose `source_version` is more than 12 months old warns (`CG-012` §5.1) | **S** | `WRN-GEO-008` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| Nothing | **This is one of the first datasets loaded** |

| Depended on by |
|---|
| `MD-003` branches · `MD-005` zones · `MD-007` addresses · `MD-013` party addresses · every customer and site address · `RP-011` branch league table geography |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Published administrative lists — Bangladesh Bureau of Statistics and the Local Government Division |
| Who supplies it | MDM analyst, from the published source |
| Collection method | Transcribed from the published list with `source_version` recorded per row |
| Known quality issues | **Upazila counts differ between published sources**; five new upazilas were created in May 2026. Bengali names vary in transliteration between sources |
| Cleansing rules | Divisions and districts double-keyed. Bengali names confirmed by the Localisation Lead, not accepted from an English source's transliteration |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | ~5,200 — 8 divisions, 64 districts, ~500 upazilas/thanas, ~4,550 unions/wards | Low; gazetted changes only |
| SIT / UAT | Full division and district set plus upazilas for the branch network | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | MDM analyst, from a published source only |
| Who may deactivate | MDM Lead, on gazetted change |
| Approval required | MDM Lead; Localisation Lead for any Bengali name |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change; the dataset's own audit trail for row change |

---

## 9. Sample rows

```csv
geo_code,parent_geo_code,geo_level,name_en,name_bn,alt_names_en,postcode,is_metropolitan,source_version,active
DHA,,division,Dhaka,ঢাকা,,,TRUE,2026-05,TRUE
CTG,,division,Chattogram,চট্টগ্রাম,Chittagong,,TRUE,2026-05,TRUE
CTG-01,CTG,district,Chattogram,চট্টগ্রাম,Chittagong,4000,TRUE,2026-05,TRUE
KHU-05,KHU,district,Jashore,যশোর,Jessore,7400,FALSE,2026-05,TRUE
DHA-01-05,DHA-01,upazila,Savar,সাভার,,1340,FALSE,2026-05,TRUE
```

---

## 10. Migration notes

Not migrated — loaded from the published source. Legacy address free-text is **mapped to** this hierarchy during `DM-004` party migration, not the reverse.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-007_Address_Format_and_Validation_Standard.md`](MD-007_Address_Format_and_Validation_Standard.md) | How addresses use this hierarchy |
| [`MD-003_Branch_and_Service_Centre_Master.md`](MD-003_Branch_and_Service_Centre_Master.md) | Branch geography |
| `MD-005` Dispatch Zone and Territory Master | Zone geography |
| `BN-004` Do-Not-Translate and Transliteration Register | Place-name transliteration |
| `05-06` §9 | Localisation standards |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | MDM Lead (pending) |

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
