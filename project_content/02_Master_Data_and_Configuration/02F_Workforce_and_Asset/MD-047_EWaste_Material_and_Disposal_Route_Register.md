---
id: MD-047
title: E-Waste Material and Disposal Route Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Sustainability
author: Sustainability with Legal and Operations
reviewers: [Legal & Compliance, Operations, Finance, HSE, Localisation Lead]
approver: Operations Director
content_class: C
purpose: >
  Material categories, hazard class, approved disposal partners, recovery rates and certificate
  requirements. M18 must issue defensible disposal certificates and report material recovery to
  regulators and to corporate clients for their own ESG reporting.
traces_to: [M18, MD-013, MD-021, DT-035, LG-018, SP-026, EO-007]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: MD-047_EWaste_Material_and_Disposal_Route_Register_BN.md
data_file: MD-047_EWaste_Material_and_Disposal_Route_Register.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M18_EWaste_Recycling_and_Circular_Economy.md
    verified: 2026-08-15
    class: P1
  - source: Environmental and e-waste rules applicable in Bangladesh — **to be verified with Legal**
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# MD-047 — E-Waste Material and Disposal Route Register

> Environmental claims are increasingly regulated. An unsubstantiated recovery rate on a
> certificate given to a corporate client is a greenwashing exposure as well as a compliance one
> (`CG-013` T-A16).

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce & asset |
| Owning module | `M18` |
| Data steward | Sustainability analyst |
| Golden source | Disposal partner agreements and regulatory authorisations |
| Refresh cadence | Annual; on any partner or regulation change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `material_code` | char(8) | ✔ | `EWM-nnn`, permanent | — |  |
| `material_name_en` | text(120) | ✔ |  | — |  |
| `material_name_bn` | text(120) | ✔ |  | **✔** | On the disposal certificate |
| `material_category` | enum | ✔ | ferrous / non_ferrous / precious / plastic / glass / battery / pcb / crt / refrigerant / mixed | — |  |
| `hazard_class` | enum | ✔ | none / lithium / lead / mercury / cadmium / refrigerant / other_hazardous | — |  |
| `source_device_families` | multi-fk |  | → `MD-021` | — |  |
| `disposal_route` | enum | ✔ | recycle / recover / refurbish_input / licensed_disposal / return_to_producer | — |  |
| `partner_party_id` | fk |  | → `MD-013` recycling partner role | — |  |
| `partner_licence_ref` | text(60) | ✔ | **Regulatory authorisation** | — | Evidence in `M24` |
| `partner_licence_expiry` | date | ✔ |  | — |  |
| `typical_recovery_pct` | decimal(5,2) |  | **Substantiated, not estimated** | — | Reported to clients |
| `certificate_required` | bool | ✔ |  | — | → `DT-035` |
| `requires_manifest` | bool | ✔ |  | — | Hazardous transport |
| `unit_value_bdt` | decimal(14,2) |  | Material recovery value | — |  |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `material_name_en` + `material_category` |
| Surrogate key | `material_code` |
| Code format | `EWM-nnn` |
| Reuse policy | Never reused; disposal certificates reference it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| EWM-01 | A batch may not be transferred to a partner whose licence has expired | **H** | `ERR-EWM-001` |
| EWM-02 | A hazardous material requires a manifest and a certificate | **H** | `ERR-EWM-002` |
| EWM-03 | `typical_recovery_pct` may only be published where substantiated by partner reporting | **H** | `ERR-EWM-003` |
| EWM-04 | `material_name_bn` is mandatory | **H** | `ERR-EWM-004` |
| EWM-05 | Changing a disposal route requires Legal review — it is a regulatory position | **A** | `ERR-EWM-005` |
| EWM-06 | A material with no partner warns — it cannot be disposed of compliantly | **S** | `WRN-EWM-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-013` Party standard | Before — partners |
| `MD-021` Device families | Before |

| Depended on by |
|---|
| `M18` e-waste · `DT-035` disposal certificate · `LG-018` environmental statements · `SP-026` disposal SOP · `EO-007` corporate onboarding |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Disposal partner agreements and their regulatory authorisations |
| Who supplies it | Sustainability with Legal |
| Collection method | Agreement and licence review; recovery rates taken from partner reporting, not estimated |
| Known quality issues | ⚠ The applicable environmental rules have not been fully determined with Legal. Recovery rates published in marketing content are unsubstantiated |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 30–80 materials | Low |
| SIT / UAT | 20 across all hazard classes | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Sustainability analyst |
| Who may deactivate | Operations Director |
| Approval required | Operations Director; **Legal for any route or published claim** |
| Effective dating | **Yes** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
material_code,material_name_en,material_name_bn,material_category,hazard_class,disposal_route,partner_licence_ref,partner_licence_expiry,typical_recovery_pct,certificate_required,requires_manifest,effective_from,active
EWM-001,Lithium-ion battery pack,লিথিয়াম-আয়ন ব্যাটারি প্যাক,battery,lithium,licensed_disposal,LIC-ENV-0012,2027-06-30,,TRUE,TRUE,2026-07-01,TRUE
EWM-010,Printed circuit board assembly,প্রিন্টেড সার্কিট বোর্ড,pcb,lead,recover,LIC-ENV-0031,2027-12-31,,TRUE,TRUE,2026-07-01,TRUE
EWM-020,Ferrous metal casing,লৌহজাত ধাতব কেসিং,ferrous,none,recycle,LIC-ENV-0031,2027-12-31,,FALSE,FALSE,2026-07-01,TRUE
```

---

## 10. Migration notes

Not migrated — authored. Recovery percentages load empty until partner reporting substantiates them.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| `DT-035` E-Waste Disposal and Material Recovery Certificate | The output |
| `LG-018` E-Waste, EPR and Environmental Compliance Statements | Regulatory position |
| `SP-026` SOP E-Waste Collection and Disposal | The process |
| `M18` E-Waste, Recycling and Circular Economy | The implementing module |

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
