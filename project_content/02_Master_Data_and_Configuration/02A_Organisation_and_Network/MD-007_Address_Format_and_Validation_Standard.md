---
id: MD-007
title: Address Format and Validation Standard
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: MDM Lead
author: MDM with Field Operations
reviewers: [Operations, Logistics, Localisation Lead, Content Design]
approver: MDM Lead
content_class: C
purpose: >
  Defines how a Bangladeshi address is composed, captured, validated and stored, including GPS
  capture and informal-address handling. Field service fails on bad addresses more often than on
  bad diagnosis; validation rules must exist before any address UI is built.
traces_to: [M02, M33, MD-006, UI-004, BN-007, P01, P09]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-007_Address_Format_and_Validation_Standard.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §2 shared kernel — fix.address with Bangladesh hierarchy and GPS
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 localisation standards
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-007 — Address Format and Validation Standard

> **Bangladeshi addresses are frequently informal.** "Beside Rahim Store, 3rd lane, Shewrapara"
> is a real address that a rider can find and a validator cannot parse. The standard must accept
> it while still capturing enough structure to route, charge and report.
>
> The answer is **structured hierarchy plus free text plus GPS**, not free text alone.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Organisation & network |
| Owning module | `M33` |
| Data steward | MDM analyst |
| Golden source | This standard |
| Refresh cadence | Annual |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `address_id` | uuid | ✔ | | — | |
| `party_id` | fk | | → `MD-013` | — | Null for branch addresses |
| `address_label` | text(40) | ✔ | Home / Office / Site / Other, or user-supplied | — | Customer-tagged (`P01`) |
| `division_code` | fk | ✔ | → `MD-006` | — | |
| `district_code` | fk | ✔ | → `MD-006` | — | |
| `upazila_code` | fk | ✔ | → `MD-006` | — | |
| `union_ward_code` | fk | | → `MD-006` | — | |
| `postcode` | char(4) | | 4 digits | — | |
| `area_name` | text(120) | ✔ | | — | Locality — Shewrapara, Agrabad |
| `road_or_block` | text(120) | | | — | |
| `house_or_holding` | text(60) | | | — | |
| `floor_flat` | text(40) | | | — | |
| `landmark` | text(200) | | | — | **Load-bearing in Bangladesh** |
| `free_text_bn` | text(400) | | | — | As the customer wrote it |
| `latitude` / `longitude` | decimal(9,6) | | Bangladesh bounds | — | |
| `gps_accuracy_m` | int | | | — | Captured accuracy |
| `gps_captured_at` | timestamp | | | — | |
| `gps_source` | enum | | device / map_pin / geocode / rider_confirmed | — | Confidence signal |
| `zone_code` | fk | ✔ | → `MD-005`, **computed** from geometry | — | |
| `is_verified` | bool | ✔ | Set TRUE only by a completed delivery | — | |
| `active` | bool | ✔ | | — | |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | None — addresses are not deduplicated on text |
| Surrogate key | `address_id` (uuid) |
| Reuse policy | Addresses are never merged automatically; a rider-confirmed address is authoritative over a geocoded one |

### 3.1 Minimum viable address by use

| Use | Minimum required |
|---|---|
| Walk-in customer | District only |
| On-site service | Division, district, upazila, area, plus GPS **or** a landmark |
| Pick & drop | As on-site, plus a contact phone |
| Statutory document | Full structured address; no free-text-only |
| Corporate site | Full structured address plus site name |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| ADR-01 | `upazila_code` must belong to `district_code`, which must belong to `division_code` | **H** | `ERR-ADR-001` |
| ADR-02 | On-site service requires either GPS or a landmark | **H** | `ERR-ADR-002` |
| ADR-03 | GPS must fall within Bangladesh bounds (20.5–26.7 N, 88.0–92.7 E) | **H** | `ERR-ADR-003` |
| ADR-04 | A statutory document may not use a free-text-only address | **H** | `ERR-ADR-004` |
| ADR-05 | `zone_code` is computed from GPS; where GPS is absent it is derived from upazila and flagged low-confidence | **C** | — |
| ADR-06 | `gps_accuracy_m` above 100 warns — the pin is probably a district centroid | **S** | `WRN-ADR-006` |
| ADR-07 | An address with no GPS after two completed visits warns for rider capture | **S** | `WRN-ADR-007` |
| ADR-08 | Overriding a computed `zone_code` requires Dispatch approval | **A** | `ERR-ADR-008` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-006` Geographic hierarchy | **Before** |
| `MD-005` Dispatch zones | Before — needed to compute `zone_code` |

| Depended on by |
|---|
| `MD-013` party records · every service order · `P09` rider manifests · `DT-002` intake receipt · `DT-027` delivery challan |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Customer entry (`P01`), agent entry (`P03`), rider confirmation (`P09`) |
| Who supplies it | The customer, then corrected by the rider on first successful delivery |
| Collection method | Structured form with map pin; free text retained verbatim |
| Known quality issues | Legacy addresses are single free-text fields with no hierarchy and no GPS. Roughly none will parse automatically |
| Cleansing rules | `DM-011`. Legacy free text is retained in `free_text_bn` and structured fields are populated where derivable; **unparseable addresses are loaded as free text plus district, not discarded** |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 300,000+ at go-live, growing with 250,000+ customers a month | High |
| SIT / UAT | 500, including deliberately informal and unparseable examples (`TS-002`) | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Any authenticated user for their own address; agents for customers |
| Who may deactivate | MDM analyst |
| Approval required | None for routine capture; Dispatch for a zone override |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
address_id,address_label,division_code,district_code,upazila_code,postcode,area_name,road_or_block,house_or_holding,landmark,latitude,longitude,gps_source,zone_code,is_verified
a1b2c3d4,Home,DHA,DHA-01,DHA-01-09,1216,Shewrapara,Begum Rokeya Sarani,586/1,Beside Rahim Store,23.7901,90.3702,rider_confirmed,ZN-001,TRUE
e5f6a7b8,Office,CTG,CTG-01,CTG-01-02,4100,Agrabad,Sk Mujib Road,Plot 42,Opposite Agrabad Hotel,22.3305,91.8112,map_pin,ZN-020,FALSE
```

---

## 10. Migration notes

`DM-004` party migration. Expect the majority of legacy addresses to require manual or rider-assisted enrichment over the first two waves. **Do not block migration on address quality** — load with free text and district, enrich in life.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-006_Bangladesh_Geographic_Hierarchy.md`](MD-006_Bangladesh_Geographic_Hierarchy.md) | The hierarchy addresses resolve to |
| [`MD-005_Dispatch_Zone_and_Territory_Master.md`](MD-005_Dispatch_Zone_and_Territory_Master.md) | Computed zone |
| `BN-007` Date, Time, Number, Currency and Address Formats | Bengali address presentation |
| `UI-004` Validation and Error Message Library | The messages above |

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
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
