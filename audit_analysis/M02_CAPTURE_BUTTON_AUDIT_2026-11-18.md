# M02 Field Service & Dispatch: data-capture button audit, second pass

**Date:** 18 Nov 2026 · **Branch:** `fix/m02-capture-buttons-2` (worktree `m02cap-wt`, from `bd3f4796`) · **Status:** built and tested on a private copy of fix_test; committed, landed (929f9e18) and **live on fix_real and fix_dev** (see §7); not pushed

## 1. The question

The M02 workspace has 12 sub-module pages. The user saw pages that still have no relevant button to record data. The first pass (13 Nov, `M02_CAPTURE_BUTTON_AUDIT_2026-11-13.md`) wired 8 pages. It left 4 pages with nothing to press on purpose:

- **7 Offline Sync**, **8 GPS & ETA** and **9 Field Evidence**: the records are written by the technician app.
- **11 On-Site Payment**: only list buttons, on another screen.

Page 1 offered only "new field order", not an assignment.

Since then the estate standard moved on: M01 and M51 (17 and 18 Nov) gave every page a capture of its own record. A workflow step became a form that first picks the record. This pass checks each page against the spec again.

## 2. What the spec says

Source: `1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md` (§5 features, §8 lifecycle, §9 business rules, §10 entities, §11 automations).

The streams the technician app writes are evidence and stay untypeable: GPS pings, the offline command journal, the panic alert and the customer's sign-off. But the spec names a **person-entered record** on each of the four pages, plus one on page 1:

| Page | What a person records | Spec | Class |
|---|---|---|---|
| 1 Candidate Scoring & Assignment | The dispatch decision. When the dispatcher overrides the engine's recommendation, a reason code | FR-FSM-046/047, BRU-FSM-03/04; entity `fix.assignment.score` (selected, override_reason) | **H** |
| 6 Technician Mobile App | Device enrolment, and revocation on loss or exit | FR-FSM-064, T-11 | — |
| 7 Offline Sync & Conflict Resolution | A supervisor's review of a flagged conflict | AUT-FSM-06, FR-FSM-027 | — |
| 8 GPS Tracking & ETA | A break or end of duty, during which location capture is suspended | FR-FSM-036, BRU-FSM-05 | **H** |
| 9 Field Evidence Capture | A failed visit (customer absent, no access, cannot complete) with geotagged evidence | FR-FSM-037/038/072, BRU-FSM-09; entity `fix.visit.exception` | **H** |
| 11 On-Site Payment | The technician's daily field cash reconciliation against jobs and hand-overs | FR-FSM-056, BRU-FSM-07; entity `fix.field.session` (cash_collected) | **H** |

## 3. What the code had (HEAD `bd3f4796`)

| # | Page | Before | Defect |
|---|---|---|---|
| 1 | Candidate Scoring | Chip *Field Work Order*; `create: false` | Nothing records an assignment. `action_dispatch` sent **any** technician and kept no trace of the engine's first choice. BRU-FSM-04 (H) was not enforced anywhere, and no record could hold an override reason. |
| 6 | Technician App | Work order only | No device register. A lost or stolen phone kept syncing (T-11). |
| 7 | Offline Sync | Nothing | The journal lists rejected and conflicted replays, but nobody can record the review AUT-FSM-06 asks for. |
| 8 | GPS & ETA | Nothing | `record_ping` stored every position, on a break or off duty alike. BRU-FSM-05 (H) was not enforced, and there was nothing to pause tracking with. |
| 9 | Field Evidence | Nothing | The order has no failed-visit state or record. A technician at a locked door could only phone the dispatcher. Decline works only before travel, and cancel is dispatcher-only. BRU-FSM-09 (H) was not met. |
| 11 | On-Site Payment | List buttons only | "Daily Cash Reconciliation" read the **branch** cash shifts (M50/M04). No technician's day was ever reconciled (BRU-FSM-07, H). |

Pages 2–5, 10 and 12 were correct and are unchanged.

## 4. What was built

`cd_field_service` 19.0.2.1.0, `models/fix_field_capture.py` (imported last; it extends the field order, ledger and location models):

| Record | Page | Rules enforced by the model |
|---|---|---|
| `fix.dispatch.decision` | 1 | Dispatcher only. On save it ranks candidates with the suggestion engine and stores the first choice, scores, rank and explanation. **Sending a lower-ranked technician needs an override reason; "other" needs notes.** Then it dispatches through `action_dispatch` (availability, M22 certification and M46 fleet gates). It cannot be edited. Event `assignment.overridden`. |
| `fix.technician.device` | 6, 7 | Dispatcher enrols and revokes. One live enrolment per device ID. Owner, ID and status change only by revoking. **The offline sync refuses a revoked device, or one enrolled to another technician** (`device_refused`). Event `technician_device.revoked`. |
| `fix.offline.conflict.review` | 7 | Only for a rejected or conflicted journal entry, once per entry. **Not by the technician who sent the command.** The journal entry is untouched. The journal list gains a Review column. |
| `fix.tracking.pause` | 8 | By the technician or a dispatcher. Starts now or later (it never hides the past), lasts at most 14 h, no overlaps, ended with End Pause. **No ping is stored while it runs** (`record_ping` and the telemetry API answer `tracking_paused`). |
| `fix.field.visit.exception` | 9 | By the **assigned technician** only, while en route, arrived or in progress. **Needs a photo and a real position within 1 km of the order's site.** Refused if a collection was taken. The order returns to `pending_dispatch` with the technician cleared. It cannot be edited. Event `visit.failed`. |
| `fix.field.cash.recon` | 11 | One per technician per day, never a future day. Figures come from the day's completed cash jobs (collected, handed to a branch shift, still held), never typed. **A variance needs an explanation.** Confirmed by a dispatcher or finance manager **who is neither the technician nor the submitter.** |

Workspace (`cd_p03_portal`):

- `static/src/a02/m02.js`: pages 1/7/8/9/11 get "+ New" for their record and page 6 a chip. There are 6 new lists and 6 new forms, and the module forms list grows from 11 to 17 entries.
- The dispatch board's **Dispatch** now saves a `fix.dispatch.decision`. It asks for the override reason when the picked technician scores below the top one. `action_dispatch` is **removed from the workspace whitelist**, so no screen dispatches without a decision.
- `controllers/a02/m02.py` SURFACES gain 6 models, and `writable.py` is regenerated. Isolation rules are regenerated for cd_field_service only; drift in 7 other modules was reverted. The event registry grows to 546.

The streams stay untypeable: offline journal, GPS pings, panic log and field-order evidence keep `create: false`.

## 5. Verification

All runs used a private copy of fix_test (`fix_test_m02`), with 37 lagging modules upgraded first so it matches HEAD.

| Check | Result |
|---|---|
| Workspace guard `cd_p03_portal/tests/test_m02_capture_buttons.py` | **35/35 pass.** Against HEAD's three front-end files it fails **13**, one per defect in §3. |
| Live tests `cd_field_service/tests/test_m02_capture_live.py` (14 tests, real non-admin technician and dispatcher users) | **14/14 pass, 0 skipped.** |
| Mutation check: each of 22 rules removed in turn | **22/22 red**: every rule is caught by a live test. Files restored byte for byte. |
| Regression: all cd_field_service + cd_p03_portal tests + event registry guards | **5,465 passed, 307 skipped.** 3 failures were mine (a test that dispatched through the now-unlisted action, and two mocked sync tests without the device model); those tests now state the new contract and pass. The **14 other failures fail identically on an untouched HEAD checkout**: M50 chips, 5 A10 guarded-field messages, M01 pick, the roster-gate message, M60 row form, M30 page, and 4 event-registry guards about peers' unregistered events. None involves M02's new events. |
| In the browser, private server on 8086 (worktree code, `fix_test_m02`) | All 12 sub-module pages show a **+ New** for their own record and list their capture chips. A Tracking Pause was saved through the in-workspace form: a start in the past was refused with the rule's message, a valid one saved, an unchanged re-save was accepted, and the Tracking Pauses list showed the row with **End Pause**. The new list chips at first showed raw ids; titles were added and re-checked. |

## 6. Not done / needs a decision

1. **Unknown devices still sync.** The device register is empty, so refusing every unenrolled phone would lock all technicians out. Only revoked phones, and phones enrolled to someone else, are refused. Once every technician's phone is enrolled, the owner can decide to refuse unknown devices too.
2. **Direct `action_dispatch` calls** (Python, tests, other modules: 102 test call sites) are not forced through a decision. The workspace, the only human dispatch surface, is.
3. AUT-FSM-10 (block the next shift until field cash is reconciled) and AUT-FSM-13 (alert after 26 h without sync) are automations, not captures. Not built.
4. BRU-FSM-14 (location-history access logged, named roles only): field-service users can still read all pings. Not in this pass's scope.
5. fix_real has 0 field orders, so these registers start empty there.

## 7. Deploy record

- **Landed** on `fix/a03-live-data-and-pending-work` at 13:27 UTC, 18 Nov (CAS fast-forward to `929f9e18`). Not pushed.
- **Went live with the M04 session's deploy**, which ran after this landing:
  - It upgraded both databases at 13:31–13:33 UTC, taking cd_field_service to 19.0.2.1.0.
  - It restarted both servers at 13:34 UTC: 8069 (fix_real) is PID 81648 and 8090 (fix_dev) is PID 63616.
  - Its backups are `fix_real_pre_m04_capture_gaps_2026-11-18.dump` and `fix_dev_pre_m04_capture_gaps_2026-11-18.dump` in `_migration/backups`.
  - The user approved deploying M02 to both databases. Because that deploy had already carried it, no second restart was needed.
- **Checked read-only on both databases:**
  - The version-gap check is empty.
  - The 6 models are registered, with 13 access rules, 12 isolation rules and 5 sequences.
  - Both servers hand out bundle `ca49a48`, which holds all six new M02 forms.
  - `/web/login` returns 200 on both.
  - The pages were not walked in the live workspace: the browser pane is not signed in to fix_real, and no credentials were entered. The page walk was done on the private test server (§5).
- **Data:** fix_real has 0 field orders, so all six registers start empty.

