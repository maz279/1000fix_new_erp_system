# M31 Workshop & Depot Repair: sub-module capture audit, second pass

**Date:** 19 Nov 2026 · **Area:** A02 · **Workspace fragment:** `cd_p03_portal/static/src/a02/m31.js`
**Backend:** `cd_workshop` 19.0.2.2.0 (new `models/fix_workshop_capture2.py`), `cd_p03_portal/controllers/a02/m31.py`

The user again saw M31 sub-module pages without a relevant data-capture button. The two earlier passes
(13 Nov: every page got a button; 14 Nov: pages 3 and 7 captured the wrong record) still passed their own
guards. So this pass did not count buttons. It read each page against what the specification says a person
records there: §5 FR-WSR-001..053, §9 BRU-WSR-01..14, §10.1 owned entities, and SOP SP-010.

Judged that way, **every one of the nine pages was missing captures the spec gives it**. Of the 15 entities
§10.1 says M31 owns, only 4 existed (job, workshop, bench, test protocol/result). Three hard rules were not
enforced at all: BRU-WSR-08, BRU-WSR-12 and BRU-WSR-14. BRU-WSR-13 had no record to enforce it on.

## What each page is supposed to capture, and what it had

| # | Page | Spec | Had (14 Nov) | Missing |
|---|---|---|---|---|
| 1 | Repair Order Creation | FR-WSR-001..008 | Receive Device, Repair Order | **Incoming buffer location** (FR-WSR-005, P1; the Booked In → Queued guard is "location assigned in the incoming buffer"). |
| 2 | Workshop & Bench Master | FR-WSR-009/010, 034, 050 | Workshop, Bench | **ESD verification record** (FR-WSR-050). `action_log_daily_esd` existed on the bench and was whitelisted, but no screen offered it (it takes two readings, so a one-question list action could not carry it) and it kept no history. **Burn-in station** (FR-WSR-034, entity `fix.burnin.station`). **Buffer / staging / secure-store locations.** |
| 3 | Bench Allocation & Queue | FR-WSR-011..017, 053, BRU-WSR-13 | Bench Allocation | **Hand-over record** (FR-WSR-015, entity `fix.bench.handover`): only a free-text note that the next allocation overwrote. **Shift close** with WIP reconciliation (FR-WSR-017, SOP steps 22-23). **Overnight secure storage** (FR-WSR-053, BRU-WSR-13, hard rule). |
| 4 | Repair-Level Routing | FR-WSR-003, 020, 029 | Job Routing | **Escalation to a specialist** with reason and full context (FR-WSR-029, P1). |
| 5 | Diagnosis & Execution | FR-WSR-018..030 | Bench Diagnosis | **Teardown record** (FR-WSR-019, entity `fix.teardown.record`). **Instrument use** (FR-WSR-025, P1; FR-WSR-040, P1; BRU-WSR-09): only the one QC instrument on the job. **Knowledge promotion** to M61 (FR-WSR-028). |
| 6 | Parts Consumption & Genealogy | FR-WSR-022..024, BRU-WSR-08/12 | Part Fitment | **Consumables** (FR-WSR-024, entity `fix.consumable.usage`). BRU-WSR-08 (warranty stock only on warranty repairs) and BRU-WSR-12 (harvested parts never on warranty repairs) were **not enforced**: a part line took any source on any job. |
| 7 | Testing & Burn-In | FR-WSR-031..040, BRU-WSR-07 | Test Result, Protocol, Evidence | **Burn-in run at a station** (FR-WSR-033/034, entity `fix.burnin.session`): burn-in started from a bare button with no station, no capacity and no protocol duration (BRU-WSR-07). |
| 8 | Rework & Transfers | FR-WSR-016, 038, BRU-WSR-10/14 | Job Routing (same as page 4) | **Workshop transfer** (FR-WSR-016; BRU-WSR-14, hard rule). The page's "transfer" was Job Routing writing `workshop_id` directly: no receiving-workshop confirmation and no M03 consignment. **Internal rework record** (FR-WSR-038, entity `fix.workshop.rework`): only a counter and the last reason on the job. |
| 9 | Repair Costing | FR-WSR-026, 043, 044 | Labour & Cost (typed minutes and labour cost) | **Labour time capture** (FR-WSR-026, P1: start, pause, resume, stop; active vs waiting; SOP step 10 "as work proceeds, not retrospectively"). **Cost build-up** (FR-WSR-043, entity `fix.repair.cost.line`: labour at rate, components, consumables, equipment time, overhead) and **cost vs estimate** (FR-WSR-044). |

How the gaps were confirmed: none of the missing entities, or an equivalent, existed anywhere in `addons/`
(searched for teardown, consumable, burn-in station/session, rework, hand-over, shift close, time log, cost line,
transfer, buffer/secure location). M45's `fix.equipment.usage` exists; M31 now writes to it rather than
duplicating it. M61's `fix.knowledge.capture` exists and every internal user may create it, so page 5 opens
M61's own form.

## What was changed

### Workspace (`m31.js`): what each page captures now

| # | Page | "+ New" | Form chips (new in **bold**) | New lists on the page |
|---|---|---|---|---|
| 1 | Repair Order Creation | Receive Device into Workshop | Repair Order, **Move Device to Location** | Device Location Moves |
| 2 | Workshop & Bench Master | Workshop Facility | Bench Master, **Workshop Location**, **Burn-In Station**, **ESD Bench Check** | Workshop Locations, Burn-In Stations, Bench ESD Checks |
| 3 | Bench Allocation & Queue | Allocate a Job to a Bench | **Shift Close**, **Move Device to Location** | Bench Hand-Overs, Shift Closes (Close the Shift action), Device Location Moves |
| 4 | Repair-Level Routing | Route or Re-route a Job | **Escalation** | Escalations (Accept / Decline) |
| 5 | Diagnosis & Execution | Record Bench Diagnosis | **Teardown Record**, **Instrument Use**, **Knowledge Capture** (opens M61's form) | Teardown Records, Instruments Used |
| 6 | Parts Consumption & Genealogy | Part Fitment | **Consumable Usage** | Consumables Used |
| 7 | Testing & Burn-In | Record a Test Result | Test Protocol, Test Evidence, **Burn-In Run** ("Start Burn-In at a Station") | Burn-In Runs (Extend action) |
| 8 | Rework & Transfers | **Request a Workshop Transfer** (was Job Routing) | Job Routing | Workshop Transfers (Confirm / Record Arrival / Decline / Cancel), Internal Rework Loops |
| 9 | Repair Costing | Record Labour & Cost | **Work Clock** ("Start the Work Clock") | Time Booked (Stop/Pause action), Cost Sheets (Build Cost Sheet action), Cost Build-Up |

Other workspace changes: the Repair Order form shows High-Value Device, Current Location and "QC marked for
review"; the Workshop form has a Costing Rates tab; the Job Routing form says the workshop changes there only
before book-in.

### Backend (`cd_workshop` 19.0.2.2.0, `models/fix_workshop_capture2.py`, imported last)

- **`fix.workshop.location`** + **`fix.workshop.custody.move`** (FR-WSR-005/042/053). A booked-in job is placed
  in a location of its own workshop, within capacity. The job carries `current_location_id`. The trail is never
  edited or deleted.
- **`fix.workshop.esd.check`** (FR-WSR-050). A passing reading feeds the bench's existing ESD interlock. A failed
  reading is kept and takes the bench's ESD status down, which blocks L2/L3 repair there until a passing check.
- **`fix.workshop.bench.handover`** (FR-WSR-015). Written by every allocation that changes the bench or the
  technician. Moving a job that is already on a bench now **requires the hand-over note**.
- **`fix.workshop.shift.close`** (FR-WSR-017, BRU-WSR-13). A supervisor closes it. The count must match the
  devices held or carry its exception, and **no shift closes while a high-value device is outside the secure
  store**. High value = ticked on the job, or an approved amount at or above `cd_workshop.high_value_bdt`
  (default 25,000 BDT, the independent-QC threshold).
- **`fix.workshop.escalation`** (FR-WSR-029). Raised with a reason; the bench context is copied in. A supervisor
  who did not raise it accepts it. Acceptance applies it through the job's own routes: the level lock, the
  certification check and the bench rules. "Another workshop" becomes a workshop transfer.
- **`fix.workshop.teardown`** (FR-WSR-019). Fixed once the job passes QC; never deleted.
- **`fix.workshop.instrument.use`** (FR-WSR-025/040, BRU-WSR-09). Stamps whether the instrument's calibration was
  valid at use (M45's own fitness rules). An out-of-calibration use is **recorded, not blocked** (BRU-WSR-09 is
  class A): the job is marked `calibration_review` and its QC pass says so. Each use writes M45's usage row, so
  M45's impact assessment sees it.
- **`fix.workshop.consumable.usage`** (FR-WSR-024), costed at standard cost.
- **BRU-WSR-08 / BRU-WSR-12** on `fix.workshop.part.line`: OEM warranty stock only on a job whose order category
  is warranty; a harvested component never on one.
- **`fix.workshop.burnin.station`** + **`fix.workshop.burnin.session`** (FR-WSR-033/034, BRU-WSR-07). Starting a
  run starts the job's burn-in, within the station's capacity. Its duration is the protocol's or the L2/L3 policy
  minimum: **extended, never shortened**, and Pass Burn-In refuses a run shorter than its own duration. Once a
  workshop has a station, burn-in there starts only at a station. A workshop with no station is unchanged.
- **`fix.workshop.rework`** (FR-WSR-038, BRU-WSR-10). Written by Fail QC and Fail Burn-In, attributed to the
  repairing technician, numbered per job. Nobody edits or deletes it.
- **`fix.workshop.transfer`** (FR-WSR-016, **BRU-WSR-14**). The receiving workshop (its manager or a supervisor,
  not the requester) confirms. Confirmation raises the M03 `branch_transfer` consignment, moves the job and frees
  its bench. A job on the bench (in repair, burn-in, QC) is first put to Wait for Parts. **A booked-in job's
  workshop can no longer be changed any other way** (cd_workshop now depends on cd_consignment).
- **`fix.workshop.time.log`** (FR-WSR-026). Started now and stopped later by the technician; one running clock per
  technician; active and waiting time apart. Stopping it sets the job's actual minutes from the clock.
- **`fix.workshop.cost.line`** (FR-WSR-043/044). "Build Cost Sheet" writes labour (clocked minutes at the workshop
  rate, or the typed labour figure when no rate is set), components, consumables, instrument hours and overhead.
  The job shows the full cost, the variance against the approved amount, and a flag beyond
  `cd_workshop.cost_variance_tolerance_pct` (default 10%).
- Workshop: `labour_rate_per_hour`, `equipment_rate_per_hour`, `overhead_pct`.

All new records carry company isolation rules and workshop-role ACLs; system stamps are guarded
(`fix.guarded.mixin`).

## Evidence

- New guard `cd_workshop/tests/test_m31_capture_pass2.py`: **20/20 pass** on `fix_test_m31c2` (a clone of
  `fix_test_m30c2` with its 8-module version gap closed), all through the real `/p03/model/*` controller or
  the ORM as non-admin workshop users.
- **Mutation check: 20/20 mutants killed.** Each rule above was disabled in turn (BRU-WSR-08/12/13/14, the
  hand-over note, burn-in never shortened at start or at pass, station capacity, location workshop, the
  receiving-side and requester checks on transfers and escalations, rework written and never edited, one
  running clock, calibration review, failed ESD, shift count and supervisor); the guard went red every time.
- **Regression:** cd_workshop's whole suite plus the portal's A02 control suite, write whitelists (A02, A12),
  sub-module button and picker tests: **405 passed, 0 failed**. Before the harness fixes below, 33 of them
  failed identically on the unchanged code, because the tests read the live estate's own settings.
- **Test-harness isolation** (tests only, no product change): the A02 M31 fixture pins the QC-instrument switch off
  (the live estate has it on); the zero-charge cap test starts from no cap (live is 5,000); the M22 gate tests stop
  the database's own dispatch-gating competencies from gating (a smartphone one on the live clone); calibrations the
  M31 tests record are accepted, as M45's own tests do (`tests/_m45_decided.py`); the bridge and model fixtures
  reuse the company's legal entity.
- Test-fixture repair: `test_a02_p0_m31.py` created a second legal entity for the company, which a peer's
  new `fix_entity_company_unique` constraint refuses, so 62 M31 tests could not even set up. It now reuses the
  company's entity, and those 62 pass again.
- **Headless walk** on a private server (worktree code, port 8171): all 9 pages, their 15 chips (every one opens a
  form with inputs, including M61's Field Capture), 30 new screens, one save through `/p03/model/write`,
  **0 console errors**. Page 8's button reads "+ Request a Workshop Transfer".

## Open (owner decisions)

- **Daily ESD:** the L2/L3 interlock still reads "ESD certified" rather than "verified today"
  (`esd_compliant_today`). Enforcing the daily check would stop live L2/L3 work on benches not yet checked today.
- **Incoming buffer as a gate:** placement is recorded, but not yet required before a bench is allocated (the
  Booked In → Queued guard). Turning it on needs locations set up in every workshop first.
- **Harvesting into stock** (FR-WSR-023): a harvested part keeps its donor serial on the part line; booking it
  into M15 inventory with provenance is not built.
- **Rates:** no workshop has a labour rate yet, so cost sheets use the typed labour figure until one is set.

## Deployment (19 Nov 2026)

- Owner approved "Deploy both now". Backups: `1000 fix/backups/fix_{real,dev}_pre_m31_capture2_2026-11-19.dump`.
- M35's combined wave already carried `-u cd_workshop,cd_p03_portal` on fix_real and fix_dev, so M31 ran no
  upgrade of its own. Verified read-only on both: cd_workshop 19.0.2.2.0, 15 new tables, 3 new job columns,
  ACLs and company rules.
- M35's single restart: 8069 = PID 52556 (fix_real), 8090 = PID 80704 (fix_dev); version gap empty at 36878e82.
- **Live walk** (read-only, no saves) on **8069/fix_real and 8090/fix_dev**: all 9 pages, 15 chips, 30 screens
  served, **0 console errors** on each.
