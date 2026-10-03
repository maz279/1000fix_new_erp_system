---
id: MD-005
title: Dispatch Zone and Territory Master
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations
author: Field Operations with Dispatch
reviewers: [Commercial, Logistics, Finance, Enterprise Architecture]
approver: Operations Director
content_class: C
purpose: >
  Defines dispatch zones with coverage polygons, travel-time bands and branch/technician assignment.
  M02 dispatch, on-site charging, pick-and-drop eligibility and the SLA promise all derive from
  zone; without it every booking must be routed by hand.
traces_to: [M02, M03, MD-003, MD-006, MD-028, MD-029, P09]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-005_Dispatch_Zone_and_Territory_Master.geojson
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P09 logistics and rider application
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-005 — Dispatch Zone and Territory Master

> **A zone is a commercial promise, not a map convenience.** Drawing a zone boundary decides
> whether a customer is offered on-site service, what they are charged for it, and what SLA we
> commit to. It is approved by Operations **and** Commercial.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Organisation & network |
| Owning module | `M02` |
| Data steward | Dispatch Manager |
| Golden source | Operations coverage decision, drawn on a map and approved |
| Refresh cadence | Quarterly review; immediately on a coverage or branch change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `zone_code` | char(6) | ✔ | `ZN-nnn`, unique, permanent | — | |
| `zone_name` | text(120) | ✔ | | — | |
| `zone_type` | enum | ✔ | metro / urban / semi_urban / rural / not_covered | — | Drives charging band |
| `primary_branch_code` | fk | ✔ | → `MD-003` | — | Default fulfilling branch |
| `fallback_branch_code` | fk | | → `MD-003` | — | On capacity overflow |
| `division_code` | fk | ✔ | → `MD-006` | — | |
| `boundary` | geojson | ✔ | Valid closed polygon, WGS84 | — | Held in the `.geojson` companion |
| `travel_time_band` | enum | ✔ | under_30 / 30_60 / 60_120 / over_120 (minutes) | — | Feeds slot availability |
| `onsite_available` | bool | ✔ | | — | |
| `pickdrop_available` | bool | ✔ | | — | |
| `pickdrop_free` | bool | ✔ | | — | Free inside Dhaka metro; charged outside |
| `onsite_surcharge_band` | fk | | → `MD-029` | — | Zone surcharge |
| `sla_band_code` | fk | ✔ | → `MD-028` | — | Response and resolution targets |
| `rider_capacity_daily` | int | | | — | |
| `effective_from` / `effective_to` | date | ✔ / | | — | Effective-dated |
| `active` | bool | ✔ | | — | |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | Boundary geometry — zones may not overlap |
| Surrogate key | `zone_code` |
| Code format | `ZN-nnn` |
| Reuse policy | Never reused; historical dispatch records reference it |

> **Odoo binding.** Custom `fix.zone` (`05-02`).

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| ZON-01 | Zone polygons may not overlap. An address must resolve to exactly one zone | **H** | `ERR-ZON-001` |
| ZON-02 | `boundary` must be a valid closed WGS84 polygon within Bangladesh bounds | **H** | `ERR-ZON-002` |
| ZON-03 | `onsite_available` TRUE requires an `sla_band_code` and a travel-time band | **H** | `ERR-ZON-003` |
| ZON-04 | `pickdrop_free` FALSE requires an `onsite_surcharge_band` | **H** | `ERR-ZON-004` |
| ZON-05 | `primary_branch_code` must have the `on_site_dispatch` capability in `MD-003` | **H** | `ERR-ZON-005` |
| ZON-06 | A zone may not be archived while it has open jobs | **H** | `ERR-ZON-006` |
| ZON-07 | Changing a boundary mid-wave requires Operations **and** Commercial approval | **A** | `ERR-ZON-007` |
| ZON-08 | An address falling in no zone warns and routes to manual triage | **S** | `WRN-ZON-008` |
| ZON-09 | `zone_type = not_covered` computes `onsite_available = FALSE` | **C** | — |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `MD-006` Geographic hierarchy | n : 1 | Before |
| `MD-003` Branch master | n : 1 | Before, or bind after |
| `MD-028` SLA definitions | n : 1 | Before or same load |
| `MD-029` Rate cards | n : 1 | Before or same load |

| Depended on by |
|---|
| Every service order with an on-site or pick-and-drop mode · technician assignment · `P09` rider manifests · slot availability |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Drawn by Operations on a map, reviewed against actual travel times |
| Who supplies it | Dispatch Manager per region, approved by Operations Director |
| Collection method | Mapping workshop; travel-time bands validated against historical job data where available |
| Known quality issues | Legacy coverage is described in prose — "Dhaka metro and surrounding areas" — which cannot be evaluated by a system |
| Cleansing rules | Every polygon validated for closure, self-intersection and overlap before load |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 60–150 zones | With coverage expansion |
| SIT / UAT | 12 — covering all four zone types and an uncovered area | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Dispatch Manager |
| Who may deactivate | Operations Director |
| Approval required | Operations Director **and** Chief Commercial Officer for boundary or charging change |
| Effective dating | **Yes** — boundary and charging changes are effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change; the dataset's own audit trail for row change |

---

## 9. Sample rows

```csv
zone_code,zone_name,zone_type,primary_branch_code,division_code,travel_time_band,onsite_available,pickdrop_available,pickdrop_free,sla_band_code,effective_from,active
ZN-001,Dhaka Metro North,metro,BR-0001,DHA,under_30,TRUE,TRUE,TRUE,SLA-P1,2026-07-01,TRUE
ZN-020,Chattogram City,metro,BR-0002,CTG,30_60,TRUE,TRUE,TRUE,SLA-P2,2026-07-01,TRUE
ZN-088,Sunamganj Rural,rural,BR-0042,SYL,over_120,FALSE,TRUE,FALSE,SLA-P4,2026-07-01,TRUE
```

---

## 10. Migration notes

Not migrated — authored. No legacy equivalent exists in structured form.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-003_Branch_and_Service_Centre_Master.md`](MD-003_Branch_and_Service_Centre_Master.md) | Fulfilling branches |
| [`MD-006_Bangladesh_Geographic_Hierarchy.md`](MD-006_Bangladesh_Geographic_Hierarchy.md) | Geographic parents |
| `MD-028` Priority, Severity and SLA Definition Register | SLA bands |
| `MD-029` Price List and Rate Card Seed | Zone surcharges |
| `M02` Field Service and Dispatch Management | The implementing module |

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
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
