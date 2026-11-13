# M02 Field Service & Dispatch: data-capture button audit

**Date:** 12–13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** front-end fixes live, KPI fix waits for a server restart, nothing committed

## 1. The question

The M02 workspace has 12 sub-module pages. Not all of them showed a button to record data. Which pages should have one, and what should it open?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md`
- `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`

The spec has 63 live requirements (FR-FSM-001…074, with 11 retired). They fall into three kinds of capture:

| Kind | Examples in the spec | Right button |
|---|---|---|
| A person records it in the back office | zones and geofences (FR-005), crews (FR-008), emergency insertion and reschedule (FR-010), route plans (FR-012), van counts (FR-041/056), lone-worker check-in (FR-031), field incident reporting to M59 (FR-059) | **+ New** or a form chip that opens the form |
| A workflow step on an existing record | dispatch (FR-002/003), decline with a reason (FR-018), on-site payment (FR-025), cash reconciliation (FR-056) | action buttons on a list |
| The technician app writes it | GPS pings (FR-032, T-07), the offline command journal (FR-026/027), signature and photos (FR-023/024), the panic alert (FR-031) | **no** button. Typing these in would fabricate tracking or a customer's sign-off, so the page should say where the record comes from. |

## 3. What the code had (before)

Nine of the twelve pages declared `forms: []`. Checking each page against its record and its owner showed these defects:

| # | Page | Before | Defect |
|---|---|---|---|
| 1 | Candidate Scoring & Assignment | chip *Field Exception Report* | Its list's **+ New** opened a decline-log form, and `fix.field.decline.log.create` refuses any create that does not come from **Decline**. The button could only fail on Save. |
| 2 | Dispatch Board | nothing | The *Emergency Reschedule* form existed but was on no page. |
| 4 | Territory / Zone / Geofence | + New only | No chip. A geofence needs a zone, and the zone form was not reachable from here. |
| 5 | Work-Order Lifecycle | *Crew Assignment* chip | The chip opened the **field-order** form, which has no crew field. A crew is 2+ technician work orders on one service order. |
| 6 | Technician Mobile App | + New only | No chip. |
| 9 | Field Evidence Capture | lists `fix.workshop.evidence` | **Wrong record.** That is M31's bench-repair evidence and needs a workshop job. Field evidence is the signature, photos and job sheet on the field order. |
| 10 | Van Stock | **nothing** | M15 masters `fix.stock.van.recon` with a form, but M02 had no way to it. The grid also asked for `variance`, which is restricted to approvers (blind count), so that column silently vanished. |
| 11 | On-Site Payment | **nothing** | Record Collection and Hand Over Cash existed only on a different page. |
| 12 | Field Safety | **nothing** | Both screens reported *"No safety-event store exists in the estate yet"*. That is false: `fix.hse.loneworker` (M59) exists with a form. |
| — | KPI row | — | With 0 field orders, the row showed **84.5 % auto-assignment, 91.5 % on-time, 32.7 % travel share, 100 % sync health** as "Live from Odoo". These were hard-coded fallbacks. |
| — | M59 lone-worker form | — | Its status labels used `active`, a state the model does not have (`checked_in`/`missed`), and it had no Location or Notes fields. |

## 4. What was changed

| # | Page | Capture now | How |
|---|---|---|---|
| 1 | Candidate Scoring & Assignment | Dispatch Board (assign) + *Field Work Order* chip | Dispatch Board added to the page. The exception list and form are now open-existing-only and say Decline writes them. |
| 2 | Dispatch Board | **Reschedule a Field Order** + chip | The form first asks which order (`pickRecord`), so it never creates one. |
| 3 | Route Optimisation | + New Route Plan + chip | unchanged (was correct) |
| 4 | Territory / Zone / Geofence | + New Zone Geofence, chips *Zone Geofence*, *Dispatch Zone* (M30's form) | |
| 5 | Work-Order Lifecycle | + New Field Work Order, chips *Field Work Order*, *Crew Assignment* (now the technician work-order form), *Field Exception Report* | |
| 6 | Technician Mobile App | + New Work Order + *Technician Work Order* chip; Field Order Parts screen added | |
| 7 | Offline Sync & Conflict Resolution | none (system-written) | Empty-state text says where entries come from. |
| 8 | GPS Tracking & ETA | none (telemetry) | unchanged |
| 9 | Field Evidence Capture | none (the technician app captures it) | Remapped to field orders, with columns for signature, OTP, before/after photos and job sheet. |
| 10 | Van Stock | **+ New Van Reconciliation** + chip (M15's blind-count form) | `variance` column replaced by van location |
| 11 | On-Site Payment | **Collect & Hand Over** list with **Record Collection** / **Hand Over Cash** | New screen, state-gated buttons |
| 12 | Field Safety | **+ New Lone-Worker Check-In** + chips *Lone-Worker Check-In*, *Field Incident Report* (M59's forms) | The lone-worker list reads M59's sessions on field orders, with Check Out / Escalate. The panic log reads `panic_sos` entries in the offline journal. |
| — | KPI row | nothing measured → "no activity" | `controllers/a02/m02.py` `kpis()` returns `None`, as M01 does |

Records another module owns open **that module's** form (M15 van counts, M59 lone-worker and incidents, M30 zones), as M38 already does with M11's promotion form. Nothing is duplicated.

### Files

- `addons/platform/cd_p03_portal/static/src/a02/m02.js`: sub-module mappings, forms, screens, chips
- `addons/platform/cd_p03_portal/static/src/a09/m59.js`: lone-worker form state labels and fields
- `addons/platform/cd_p03_portal/controllers/a02/m02.py`: KPI fallbacks removed
- `addons/platform/cd_p03_portal/tests/test_m02_capture_buttons.py`: **new guard**, 20 tests

## 5. Verification

- **Guard test:** 20/20 pass on the fix. Against the pre-fix files from git HEAD it fails **12**, so it catches each defect above.
- **Estate page standard + guard:** 624 pass. The one failure is M04, from another session's work in progress.
- **Server probe on 8069 (fix_real):** every M02 list, sub-module grid, form (including M15/M59/M30's), report and the reschedule picker was posted to its real endpoint: **55 calls, 0 errors**. No column was dropped after the van-stock fix.
- **Clicked in the workspace:**
  - Van Stock → + New opens M15's form inside M02.
  - Dispatch Board → Reschedule shows step 1 (pick the order) with an honest empty state.
  - Field Safety → + New check-in; its list shows Check Out / Escalate, disabled until a row is selected.
  - Collect & Hand Over shows its two buttons.
  - Field Exceptions has no + New.
  - No "Oops" and no console errors (apart from the usual service-worker notice).
- Nothing was saved on fix_real. The forms were opened, not submitted.

### Panic alert: fixed in code (second pass, 13 Nov)

`cd_field_service/controllers/offline_sync_api.py` handled the technician app's `panic_sos` command by writing a log line only, yet answered `dispatch_notified: True`. Nobody was told. It now:

- escalates the technician's open lone-worker session through M59's existing contact chain;
- schedules an urgent **"PANIC SOS: <technician>"** to-do, with the position, time and message, for:
  - every Field Service Manager (dispatcher) and HSE Officer in the technician's company;
  - the session's buddy;
  - the dispatcher who opened the session;
- attaches that to-do to the technician's active field order, or to the technician if no order is active;
- answers `dispatch_notified` truthfully, with `notified_count`. When nobody can be reached it tells the technician to call 16743.

The alert shows on the M02 **Panic Alert Log**. Tests in `cd_field_service/tests/test_offline_sync_behaviour.py` assert the dispatcher's to-do and the session escalation; the old test had asserted the false `True`. **The whole file passes, 21/21**, on a private copy of fix_test. The shared fix_test deadlocked with other sessions' runs, and the container's 64 MB `/dev/shm` filled under that load, so the copy ran with parallel query off.

## 6. Not done / needs a decision

1. **Update 13 Nov 02:14: now LIVE.** 8069/8089 were restarted at 02:10 (not by me), after the commits. `/p03/field/kpis` now returns `null` for the four unmeasured KPIs. *Original note:* **KPI and panic fixes were not live yet.** Both are Python, so they need a server restart. A plain restart of 8069 is **not safe right now**: other sessions have uncommitted model changes in about six addons, not yet upgraded into fix_real. For example, `fix.payment.method` has no table on fix_real, and cd_front_desk, cd_quotation, cd_msp_contract and others are changed. A restart would load all of that against a database without its schema. These two fixes need no module upgrade (controller code only), so they go live with the next coordinated `-u` + restart, once the peers' work is upgraded.
2. ~~Panic button notifies nobody~~: fixed in code, see above.
3. **No M02 data exists on fix_real**: 0 service orders, so 0 field orders. *+ New Field Work Order* needs a service order (M01) first, and a Dispatch Zone (8 exist).
4. Spec features with **no surface anywhere**: standby/emergency rota (FR-055), technician device enrolment and revocation (FR-064/T-11), slot capacity by skill (FR-052). These are builds, not wiring.
5. **Committed and pushed** (origin `9cedf519..eb3aae29`) (13 Nov, on `fix/a03-live-data-and-pending-work`): `378ff9d1` (panic SOS) and `eb3aae29` (M02 capture wiring, KPI fallbacks, M59 labels, guard test). Only these six files; the other sessions' uncommitted work was left untouched.
