# M02 Field Service & Dispatch: bidirectional audit (screen ⇄ backend)

**Date:** 13 Nov 2026 · **Estate:** fix_real on 8069 · **Follows:** `M02_CAPTURE_BUTTON_AUDIT_2026-11-13.md`

## 1. Method

The audit ran in both directions and was exhaustive rather than sampled.

- **Backend dump.** A read-only Odoo shell on fix_real recorded every M02 model: each field's type, required, read-only, stored, computed, groups and selection keys. It also recorded each model's actions, guarded and form-locked fields, ACLs, record rules, crons, and who holds the Field Service groups.
- **Screen dump.** The live workspace registry was dumped: every M02 screen, column, form field, action and its state gate, report, chip, and the master forms borrowed from M15, M30 and M59.
- **Diff, screen → backend.** Every column, form field, domain value, action, state gate, status label, required flag and report resolves to something real. Every editable field is writable through the save endpoint's generated whitelist and is not guarded.
- **Diff, backend → screen.** Every required field is capturable, and every whitelisted action has a button or a stated reason not to.
- **Business rules.** The backend was read against the spec: the state model (§8), the 14 business rules BRU-FSM-01…14 (§9), the KPIs (§15) and roles (§13).
- **Proof.** The whole lifecycle was walked on a **clone of fix_real** by real people under their own permissions, followed by ORM tests.

## 2. What was already sound

The field-order backend is well built:

- every lifecycle step checks its actor: dispatcher-only steps, and steps only the assigned technician may take;
- 44 workflow fields are guarded from plain writes;
- a closed order is frozen;
- arrival has anti-spoofing and geofence checks, with a dispatcher waiver that needs a reason;
- completion needs the customer's sign-off, a photo, a work summary, and every picked part fitted or returned;
- cash settles only on hand-over to an open branch shift;
- an SLA breach escalates to dispatchers;
- the M22 certification gate covers dispatch, reassignment and start of work, with a routed waiver;
- events are published for M01's hand-back.

## 3. Discrepancies found and fixed

| # | Where | What was wrong | Fix |
|---|---|---|---|
| D1 | Work Order Record, Unassigned, Work Orders (lists) | Buttons had no state gate. Decline, Mark Arrival, Reassign, Waive Geofence and Cancel looked available in every state, and the server refused most presses. | Each button declares exactly the states its method accepts. |
| D2 | Route Optimisation | Optimise, Start and Complete were whitelisted but on no button. | Three state-gated buttons. |
| D3 | Route Plan form | No way to add stops, yet Optimise refuses a route with fewer than 2. A plan made in the workspace could never leave Draft. The read-only reference was editable on the form. | Stops (many2many), depot and notes added; the reference is now read-only (numbered on save). |
| D4 | Route model | Nothing stopped another technician's order being a stop. | Constraint: no stop is another technician's order or a cancelled one; an order not yet dispatched may be planned. |
| D5 | Work Orders | A pending slot had no way to get its technician (`action_assign`, dispatcher-only, on no button). | **Assign Technician** button + whitelist. |
| D6 | Field Work Order form | "Last Safety Heartbeat At" was editable: anyone could type a safety heartbeat. | Read-only on the form and removed from the save whitelist. |
| D7 | Zone Geofence form | It asked for "GeoJSON". Real GeoJSON fails the model's check, and a fence that can't be read refuses every arrival. It also didn't say only Platform Admin can save (A12 decision E25). | Exact formats shown; the owner of the register stated. |
| D8 | KPI "Auto-Assignment" | Computed as assigned ÷ dispatched, which is 100% by construction. No automatic dispatch exists. | KPI-013 now reports automatic ÷ dispatched = **0%** when there are dispatches. |
| D9 | Lone-Worker / Panic reports | They returned a fixed zero and said no safety store existed. | They count M59 sessions by state and the panic alerts received. |
| D10 | Suggestion engine (BRU-FSM-01) | A technician on approved leave was still offered and could be dispatched or reassigned. | Never offered; dispatch and reassign refuse with the reason. A missing roster slot lowers the score and says so. |
| D11 | Suggestion engine | Candidates came only from past orders and rosters. On fix_real (none of either) it offered **nobody**, so no first dispatch was possible. | Field Service Technician group members are candidates. |
| D12 | Dispatch board | Accept, Travel, Arrive, Work and Complete appeared for everyone. Only the assigned technician may press them, so a dispatcher was always refused. Mark Arrival sent no position, so a fenced order was always refused. | The step shows only to the assigned technician; Arrival asks for the position. |
| D13 | Lone-worker check-in (from the previous pass) | Location and Notes were added to the form but not to the save whitelist, so saving them was refused. | Whitelist regenerated. |
| D14 | M59 forms | Tab badge counts were wrong (3 vs 5; 6/3/2 vs 7/10/6). | Corrected. |

| D15 | Suggestion engine (pre-existing) | The visit day was the UTC date of the scheduled start, while leave and roster slots are local dates and the M55 check uses the user's day. A 03:00 Dhaka visit was checked against the previous day. | One helper, `_fix_day`, in the M55 frame (`context_today`). |

**One change I reverted.** I first made "a slot created with its technician" start as Assigned. Eight existing tests encode the recorded design A02 M01-P2: the slot stays pending and the state moves only through a transition. So the change was reverted, and the Assign button uses the proper transition instead.

## 4. Proof

- **Registry guard + estate page standard:** 630 tests pass. They pin every fix above, including that every list button declares its states.
- **ORM tests: 442 passed, 0 failed.**
  - Covered: the new `cd_field_service/tests/test_m02_bidirectional_audit.py`, all of `cd_field_service`, `cd_service_order` (API security, models, technician API), attendance, all of `cd_competency`, and the portal service-order API.
  - Run on a private copy of fix_test.
  - The shared fix_test carries a 53,621-event unrelayed outbox backlog that breaks every relay-driven test on any copy. It was cleared on the private copy only (`relayed_at`).
- **Committed** as `8e7d2bea` on `fix/a03-live-data-and-pending-work`, with only my hunks; the other sessions' uncommitted work in the shared engine and generated whitelist was left in place.
- **Lifecycle walk on a clone of fix_real:**
  - Dispatcher: Md Shariful Islam (R-07). Technician: Zahidul Islam Sraban (R-12).
  - 25 steps: 20 succeed and the other 5 are refusals the rules are supposed to make (see the list after this table).

  | Step | Result |
  |---|---|
  | create, submit, suggestion lists the technician | ✓ |
  | dispatch without a certification | refused (M22) ✓ |
  | certification recorded → dispatch | ✓ |
  | dispatcher presses Accept | refused ✓ |
  | technician: accept → travel → arrive → collect cash 900 → start work | ✓ |
  | complete without evidence | refused ✓ |
  | evidence → complete | ✓ (cash pending hand-over) |
  | cash hand-over | refused: no open branch shift ✓ |
  | crew slot by the dispatcher | ✓ (pending, by design) |
  | slot naming a technician by a non-dispatcher | refused ✓ |
  | route: 2 stops, optimise (4.9 km), start, complete | ✓ |
  | lone-worker session opened by the dispatcher on the order | ✓ |
  | panic alert | 6 people notified, session escalated ✓ |
  | KPIs and all 17 reports compute as the dispatcher | ✓ |

  The five expected refusals: dispatch without a certification, the dispatcher pressing Accept, completion without evidence, cash hand-over with no open shift, and a non-dispatcher naming a technician on a slot.

## 5. What blocks M02 on fix_real (data and decisions, not code)

| Blocker | Effect | Prepared |
|---|---|---|
| ~~Technician roles R-10/R-11/R-12 lack "Field Service / Technician"~~ | **Resolved 13 Nov, owner-approved:** 141 granted, 0 refused (see §6). | `sync_23_field_service_technician_roles_fix_real.py`, role map `86b08ed2`. |
| 0 certifications (4 dispatch-gating competencies exist) | The M22 gate refuses every dispatch. | HR/Training must record technicians' certifications. Meanwhile a dispatcher can request a waiver per job. |
| Certification Override Approver = admin only | Waivers can only be decided by the system admin. | Name the Operations Director (spec authority). |
| 0 devices / device models | No service order, so no field order. | M01/M17 intake data. |
| No open branch cash shift | Field cash cannot be handed over. | Normal branch operation (M04). |
| Roster not loaded | Work-order assignment needs a roster slot (M55), and suggestions can't rank by shift. | Roster is on the owner's "keep pending" list. |
| ~~Acceptance timeout off~~ | **Resolved 13 Nov, owner-approved:** set to 15 minutes. | — |

## 6. Deployment: done, live on 8069 (13 Nov, 04:00)

- **Code.**
  - `8e7d2bea` (all fixes) and `86b08ed2` (role map) are pushed to origin `fix/a03-live-data-and-pending-work`.
  - The 8069/8089 restart was run by the M05 session at 03:51, after its own `-u cd_msp_contract`. We coordinated so that no screen would read a missing column. That restart loaded the M02 server fixes.
- **Live verification after the restart:**
  - 53 calls cover every M02 list, form, report and sub-module grid, plus the borrowed M15/M30/M59 forms: 0 errors, 0 dropped columns.
  - The board sends the viewer's employee id.
  - KPIs report "nothing measured".
  - The safety reports read M59 sessions and panic alerts.
  - `action_assign` passes the surface whitelist.
  - The dispatch board renders with no error.
- **Owner-approved changes applied on fix_real.** Backup first: `_migration/backups/fix_real_pre_m02_role_grant_2026-11-13.dump`.
  - Field Service / Technician now carried by R-10/R-11/R-12, and **granted to 141 technicians, 0 SoD refusals**, through the grant service.
  - Acceptance timeout **15 minutes** (was unset); its 5-minute cron is active.

## 7. Owner decisions (13 Nov, 04:10)

- **End-to-end proof:** the lifecycle walk on the fix_real clone is accepted as the proof. No test transactions are to be created in fix_real.
- **Certifications, devices, roster:** no source data yet. The business enters them through the normal screens. The system refuses safely until then.
- **Certification waivers:** stay admin-only for now.

## 8. Business data the code is waiting for

These can only be supplied by the business. The code is ready for each and refuses safely until then (proven in the walk):

- **Technicians' certifications.** HR/Training records them; until then the M22 gate refuses dispatch. A waiver per job is possible.
- **Certification Override Approver.** Name the Operations Director; today only the admin holds it.
- **Devices.** Register them through M01/M17 intake.
- **Branch cash shifts.** Open one (M04) to receive field cash.
- **Roster.** Load it (M55), already on the owner's pending list.
