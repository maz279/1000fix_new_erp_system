---
id: MD-042
title: Shift, Roster and Working Pattern Master
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HR with Operations
author: HR with Field Operations
reviewers: [Operations, Payroll, Legal, Dispatch]
approver: HR Director
content_class: C
purpose: >
  Shift definitions, roster patterns, overtime rules, geofence parameters and break policy. M55
  scheduling and technician clock-in with geofence on P02 both consume it, and overtime
  miscalculation is a labour-law exposure as well as a payroll error.
traces_to: [M55, M56, M02, P02, MD-008, MD-041, MD-043, SP-022]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
data_file: MD-042_Shift_Roster_and_Working_Pattern_Master.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M55_Time_Attendance_and_Workforce_Scheduling.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P02 — shift clock-in/out with geofence
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-042 — Shift, Roster and Working Pattern Master

> Geofence parameters are the most disputed data in this register. Too tight and technicians
> cannot clock in from a customer site; too loose and attendance means nothing.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce & asset |
| Owning module | `M55` |
| Data steward | HR systems analyst |
| Golden source | HR-approved shift patterns, compliant with labour law |
| Refresh cadence | Per wave; on any pattern change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `shift_code` | char(8) | ✔ | `SHF-nnn`, permanent | — |  |
| `shift_name` | text(80) | ✔ |  | — |  |
| `entity_code` | fk | ✔ | → `MD-002` | — |  |
| `applies_to_positions` | multi-fk |  | → `MD-008` | — | Null = all |
| `start_time` | time | ✔ |  | — | Asia/Dhaka |
| `end_time` | time | ✔ | Crosses midnight where later than start | — |  |
| `break_minutes` | int | ✔ |  | — |  |
| `working_days` | multi-enum | ✔ | SUN…SAT | — |  |
| `calendar_code` | fk | ✔ | → `MD-041` | — | Holiday treatment |
| `grace_in_minutes` | int | ✔ | Late tolerance | — |  |
| `grace_out_minutes` | int | ✔ |  | — |  |
| `geofence_radius_m` | int | ✔ | **Clock-in tolerance** | — | `P02` geofence |
| `geofence_anchor` | enum | ✔ | branch / job_site / either | — | Where the fence centres |
| `overtime_threshold_min` | int | ✔ | Daily | — |  |
| `overtime_rate_element` | fk |  | → `MD-043` | — | Payroll element for OT |
| `night_shift_allowance_element` | fk |  | → `MD-043` | — |  |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `entity_code` + `shift_name` |
| Surrogate key | `shift_code` |
| Code format | `SHF-nnn` |
| Reuse policy | Never reused; attendance history references it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| SHF-01 | Clock-in outside the geofence is recorded as an exception requiring supervisor approval | **A** | `ERR-SHF-001` |
| SHF-02 | Overtime beyond the statutory limit requires HR approval | **A** | `ERR-SHF-002` |
| SHF-03 | A shift must reference a calendar for holiday treatment | **H** | `ERR-SHF-003` |
| SHF-04 | Break minutes may not exceed the shift duration | **H** | `ERR-SHF-004` |
| SHF-05 | Changing a pattern retrospectively over a processed payroll period is prohibited | **H** | `ERR-SHF-005` |
| SHF-06 | `geofence_radius_m` below 100 warns — GPS accuracy on mid-range devices rarely beats it | **S** | `WRN-SHF-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-008` Positions | Before |
| `MD-041` Calendars | **Before** |
| `MD-043` Payroll elements | Before or bind after |

| Depended on by |
|---|
| `M55` scheduling · `M56` payroll · `P02` clock-in · `SP-022` attendance SOP · dispatch capacity |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | HR-approved shift patterns |
| Who supplies it | HR Director with Field Operations |
| Collection method | Workshop; geofence radii validated by field test on the `P02` baseline device |
| Known quality issues | Current shifts are informal and vary by branch; overtime is calculated manually |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 20–50 patterns | Low |
| SIT / UAT | 12 including a night shift and a geofence-exception scenario | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | HR systems analyst |
| Who may deactivate | HR Director |
| Approval required | HR Director; **Legal for any change touching statutory overtime** |
| Effective dating | **Yes** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
shift_code,shift_name,entity_code,start_time,end_time,break_minutes,working_days,calendar_code,grace_in_minutes,geofence_radius_m,geofence_anchor,overtime_threshold_min,effective_from,active
SHF-001,Branch day shift,EN-01,09:00,18:00,60,SAT;SUN;MON;TUE;WED;THU,CAL-BUS,15,150,branch,480,2026-07-01,TRUE
SHF-010,Field technician day,EN-01,08:30,17:30,60,SAT;SUN;MON;TUE;WED;THU,CAL-BUS,20,300,either,480,2026-07-01,TRUE
```

---

## 10. Migration notes

`DM-009`. Attendance history is not migrated beyond the current payroll period.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-043_Payroll_Element_and_Statutory_Deduction_Register.md`](MD-043_Payroll_Element_and_Statutory_Deduction_Register.md) | Overtime elements |
| [`../02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`](../02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md) | Holiday treatment |
| `SP-022` SOP Time, Attendance and Roster | The process |
| `M55` Time, Attendance and Workforce Scheduling | The implementing module |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | HR Director (pending) |

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
