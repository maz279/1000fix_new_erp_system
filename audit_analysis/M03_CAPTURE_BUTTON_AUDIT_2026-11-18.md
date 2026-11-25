# M03 Service Logistics: data-capture button audit (second pass)

**Date:** 18 Nov 2026 · **Branch:** `fix/m03-capture-pass2` (worktree `m03cap2-wt`, from 8ed0dc47) · **Status:** DEPLOYED on fix_real and fix_dev, 18 Nov 2026 (commit e4648971, not pushed)

## 1. The question

The M03 workspace has 12 sub-module pages. The user observed that not every page has a relevant data-capture button.

M03 had a first capture pass on 13 Nov (`all_working_folder/working/M03_Submodule_Capture_Audit_2026-11-13.md`). It took the module from 2 of 12 pages with a button to 11 of 12. This pass checks two things: whether each button is still the **relevant** capture for its page, and whether it still works after five days of engine changes across the estate.

## 2. Sources

- The module spec, `1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M03_Service_Logistics_and_Reverse_Logistics.md`: §3 scope, §5 FR-LOG, §9 rules, §10 entities.
- Owner decisions in `OWNER_DECISIONS_fix_real_2026-11-11.md` §I:
  - **I2:** the tariff is on hold.
  - **I4:** leg, item and POD records, rider shifts, route manifests, recycling, invoicing and the courier API are "none for now".
- The code: `cd_consignment`, and `cd_p03_portal/static/src/a02/m03.js`.

## 3. What the pages had (HEAD 8ed0dc47)

I measured this two ways:
- the engine's own `fregCreate`;
- a headless walk of all 12 pages on fix_dev (8090), which clicked every button and chip. Nothing was saved.

Every button opened its form, with no error dialog and no JS error.

| # | Page | Button | Relevant? |
|---|---|---|---|
| 1 | Consignment Creation & Manifest | + Consignment | yes |
| 2 | Multi-Leg Journey Planning | + Consignment | **No.** See D1 to D3. |
| 3 | Chain-of-Custody Scanning | + Record a Hub Intake Scan | yes |
| 4 | POD with OTP Verification | + Record Recipient & Signed Waybill | yes |
| 5 | Sealing & Tamper Evidence | + Seal a Consignment for Dispatch | yes |
| 6 | Rider Assignment & Shifts | + Assign Rider & Vehicle (+ Rider Certification chip) | yes. Shifts are I4. |
| 7 | Route Manifest & Load Planning | + Assign Rider & Vehicle | Acceptable. The stored route manifest is I4. |
| 8 | Rider App Offline Sync | none ("No data-entry form") | correct: the rider app writes these records |
| 9 | Courier Partner Integration | + New Courier Booking (+ POD, Partner chips) | yes |
| 10 | COD Collection & Handover | + New Rider COD Settlement (M50 form) | yes |
| 11 | Loss / Damage Claims | + New Damage Claim | yes |
| 12 | Distance & Zone Charging | + New Courier Partner (tariff tab) | Acceptable. The zone tariff is I2. |

## 4. Defects found

| # | Defect | Effect |
|---|---|---|
| D1 | **The hand-over chose the leg type from the service type alone** (`action_create_consignment`). A collection or mail-in order always got a pickup. | Once the pickup had arrived, a second press raised **another pickup**: a rider sent for a device already in the shop. The **delivery back to the customer could not be raised at all.** That breaks FR-LOG-002 (customer → branch → … → customer). |
| D2 | **Page 2 offered the same blank consignment as page 1.** | Nothing on "Multi-Leg Journey Planning" planned the next leg of a journey. |
| D3 | **The "Multi-Leg Journeys" screen listed custody scans.** | Those are page 3's records, and Chain-of-Custody already lists them. A journey is the legs of one order. |
| D4 | **The consignment form was titled "Consignment (5 types)".** | The model has 4 types: pickup, delivery, branch transfer, return to vendor. |

## 5. What was changed

- **D1:** `cd_consignment/models/fix_consignment_ext.py`, new `fix.service.order._fix_next_leg_type()`:
  - Collection and mail-in orders get a pickup until a pickup leg is **delivered**.
  - A returned pickup (a failed collection) does not count as arrived.
  - After that, the next leg is the **delivery back**. It is raised only once the order is `ready`. Before that, the hand-over refuses with a message that names the leg which arrived.
  - A ready order with no pickup (dropped off, but delivered back) gets the delivery.
  - Other service types are unchanged: a delivery leg.
  - The existing "no second live leg of the same kind" check still applies.
- **D2:** a new form, `M03-form-next-leg` ("+ Plan the Next Leg of a Journey"):
  - Step 1 picks an open collection or mail-in order, or any order that is ready.
  - Save runs the order's own `action_create_consignment`, already whitelisted for M01.
  - Chips on page 2: *Next Journey Leg* and *Consignment* (for legs with no order: branch transfers, returns to vendor).
- **D3:** `M03-journeys` now lists `fix.consignment` legs that have a service order, with the order first.
- **D4:** the title, chip and module form list now read "Consignment".
- **Comment only:** the M01 "Hand to Logistics" button comment now describes the new rule.

No model fields, data files or access rules changed, so deploying needs no module upgrade. It needs only a web-server restart, because the Python method is new.

## 6. Evidence

| Check | Result |
|---|---|
| `cd_p03_portal/tests/test_m03_submodule_capture.py` (updated: page 2 expectation, plus 4 new tests) and `cd_consignment/tests/test_consignment_ext.py` (4 new hand-over tests) | **42/42** on `fix_test_m03c` (fix_test clone, all 36 lagging modules upgraded: drift none) |
| Mutation check (7 defects re-introduced one at a time) | **7/7 killed**, including the original D1 bug |
| Regression: all `cd_consignment` tests, the M03 page guards and the estate page guards | 899 passed, 132 skipped, 30 xfail. 3 failed, 1 setup error. See the list below. |
| UI walk of all 12 pages on a private server (8094) | Page 2 shows "+ Plan the Next Leg of a Journey". All other pages are as in §3. No error dialog and no JS error. |
| UI drive with a seeded, booked-in collection order | The order is listed in step 1. **Raise the Next Leg** created pickup CSG/2026/00734 to the order's branch. A second press showed the server refusal, and no duplicate leg was created. **Multi-Leg Journeys** lists the leg. |

What the 3 failures and the 1 setup error were:
- **M03 bidirectional guard.** Its pick-domain parse could not handle the `'|'` operator. Fixed in the test; it now passes.
- **Setup error.** A `digest_digest` lock caused by my private server's cron on the same database. The test passes on re-run.
- **Two pre-existing failures, not M03:** M19/M30 declared-module rows, and the M50 statement-line `pick`. The same two failed in the 17 Nov M01 audit.

## 7. Left open

- The **owner-declined spec features (I4):**
  - item manifest lines (FR-LOG-003);
  - rider shifts, and so COD per shift (BRU-LOG-06) and the "Rider Shifts Open" KPI;
  - a stored route manifest and load limits (FR-LOG-014/029);
  - leg and POD records, recycling, invoicing, the courier API.

  Pages 6, 7 and 12 therefore capture the nearest real record.
- **The tariff (I2)** is on hold: internal riders are still charged BDT 80 + 40/kg.
- **On fix_real there are 0 consignments.** The next-leg form's pick list will be empty until real collection orders exist.

## 8. Deployment

**DEPLOYED 18 Nov 2026, about 21:23 local, on user approval ("Commit and deploy").**

1. **Commit.**
   - e4648971 on `fix/a03-live-data-and-pending-work`, rebased onto the M67 tip eb67dfc4. The M03 suites were re-run green on the rebased code.
   - Landed with a compare-and-swap ref update. The shared checkout was clean and was synced with `read-tree -m -u`. Not pushed.
   - Pre-commit hooks passed. `ruff-format` re-wrapped long lines in the three test files.
2. **Backups**, in `all_working_folder/1000fix-2/_migration/backups/`:
   - `fix_real_pre_m03_capture2_2026-11-18.dump` (51.5 MB);
   - `fix_dev_pre_m03_capture2_2026-11-18.dump` (47.3 MB).
3. **No module upgrade.** No field, data file or access rule changed. The version-gap check over every `cd_` module was clean on both databases before the restart.
4. **Restart**, of the web-server processes only (the supervisors relaunched them):
   - 8069 (fix_real): PID 48332 → 72076;
   - 8090 (fix_dev): PID 71496 → 45636.

   Both registries loaded with 0 errors, and both login pages return 200.
5. **Verification.**
   - Both servers serve the new `M03-form-next-leg` and the journeys-as-legs screen, and no longer the "(5 types)" title.
   - A headless walk of all 12 pages on live fix_dev opened all 27 buttons and chips, with no error dialog and no JS error. Page 2 shows **+ Plan the Next Leg of a Journey**, which opens its order-pick step.
   - Nothing was saved on either database.
