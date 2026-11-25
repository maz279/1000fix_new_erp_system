# M46 Fleet & Vehicle Management — Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M46 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M46_Fleet_and_Vehicle_Management.md`. Sections used: §3 scope, §5 FR-FLT-001…044, §8 lifecycles, §9 BRU-FLT-01…22, §10.1 owned entities (21), §13 roles and segregation of duties, §14 reports.
- Code:
  - `cd_p03_portal/static/src/a07/m46.js` (the page registry: 8 sub-module pages, 16 screens);
  - `cd_p03_portal/controllers/a07/m46.py` (surfaces, packs, KPIs);
  - `cd_vehicle_ext/models/fix_vehicle.py` and `fix_vehicle_ops.py` (the 10 M46 models).
- Live data: fix_real holds **no M46 record of any kind**: 0 vehicles, 0 vehicle models, 0 drivers, 0 documents, 0 checks, fills, services, snapshots and accidents. The Fleet Logistics Manager role has 1 holder; the Fleet Officer role has no direct holder (the Logistics Manager implies it); the Driver role has 0.

## 1. What was there (HEAD 48184ca8)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| # | Page | "+ New" | Form chips | Defect |
|---|---|---|---|---|
| 1 | Vehicle Register | Vehicle | Vehicle | **A vehicle needs a Model, and no Model or Make could be added from the page** (both lists sat on no page). fix_real has 0 models, so the first vehicle could not be registered from the sub-module. No ownership basis (FR-FLT-003 P0): a leased van was capitalised in M49 like an owned one. |
| 2 | **Statutory Documents** | Vehicle Document | **none** | The page lists off-road records with no capture. **No renewal record** (FR-FLT-013 P0, FR-FLT-014): who renews, when it was submitted, the government fee, agent fee and lapse penalty were recorded nowhere. |
| 3 | Drivers | Driver | Driver | No traffic fine against a driver (FR-FLT-043, BRU-FLT-16). |
| 4 | **Assignment & Pool** | Vehicle Booking | **none** | |
| 5 | Pre-Use & PM | Pre-Use Check | PM Service | **No defect record**: a defect existed only as an off-road record, so a deferrable defect could not be reported without stopping the vehicle (FR-FLT-025 P0). A service named no garage, work, invoice or next due (FR-FLT-026/027 P0). |
| 6 | Fuel & Odometer | Fuel Transaction | Fuel Transaction | — |
| 7 | **Telematics** | Telemetry Snapshot | **none** | **No device register** (FR-FLT-035 P0): the tracker was a free-text label on a snapshot; no identifier, SIM, data plan, firmware or fitment was held, and one device could be "on" two vans. |
| 8 | Accidents & Insurance | Accident Report | Accident Report | The Insurers list sat on no page. No traffic fine or penalty register (FR-FLT-043, BRU-FLT-16 class A). |

The new guard (`test_m46_capture_buttons.py`) run against HEAD: **19 of 38 tests fail.**

## 2. What was built

### Backend — `cd_vehicle_ext` 19.0.0.4.0, new file `models/fix_vehicle_capture.py`

| Page | Record | What it does | Controls |
|---|---|---|---|
| 2 | `fix.vehicle.document.renewal` (FR-FLT-013/014, §10.1) | One renewal of one statutory document: the person responsible, the issuing authority, initiated/submitted dates, government fee, agent fee, late penalty (with its reason), the fee receipt and the renewed certificate. | Opened by a Fleet Officer; one renewal in progress per document. Initiated → submitted → **completed only on a new certificate of the same vehicle and type, in date, with its scan in the register**. A renewal that paid a penalty is completed by an officer **other than the person responsible** (§13 SoD). Fees are frozen once completed; never deleted. The fees count in Cost per Kilometre. |
| 5 | `fix.vehicle.defect` (FR-FLT-025, BRU-FLT-04) | A defect reported by anyone, with category, description and photo, classed safety-critical or deferrable. | **Safety-critical → the vehicle goes off-road at once** (linked off-road record; dispatch refuses it). A deferrable defect leaves the vehicle on the road. A saved defect is never downgraded. Cleared by a Fleet Officer who did not raise it; a safety-critical one only on a passed pre-use check recorded after it. |
| 5 | `fix.vehicle.pm` + execution | The service names its garage, work performed, parts, invoice reference, downtime and the next due date/odometer (FR-FLT-027). | A service at a garage needs its invoice reference before Mark Done. **A next due date or odometer opens the next service** when this one is done, so the schedule continues (FR-FLT-026). Execution fields are frozen once done. The work text stays optional, because the M45/M47 work-order spine completes services that carry their work on the work order. |
| 7 | `fix.telematics.device` (FR-FLT-035/036) | The tracker as an asset: identifier (IMEI/serial), provider, SIM, data plan, firmware, the vehicle it is fitted to and when. Health (reporting / silent / never reported / not fitted) and last report come from its latest snapshot. | Registered by a Fleet Officer. The identifier is unique (case-blind). **One device per vehicle.** A fitted device moves only through Remove from Vehicle (with the reason), and the fitment history is kept in its chatter. Retire needs it removed first. |
| 7 | `fix.vehicle.telemetry` + `device_id` | A snapshot is linked to the registered device fitted to its vehicle. | A device reference that is not in the register, on a vehicle that carries a registered device, is refused. An unregistered legacy reference is still accepted. |
| 3, 8 | `fix.vehicle.penalty` (FR-FLT-043, BRU-FLT-16) | A traffic fine: authority, case/slip number, offence, amount, slip scan, payment. | Recorded by a Fleet Officer against the vehicle and **the driver on duty**: if none is named, the driver booked on the vehicle that day, else its assigned driver; with neither, it is refused. A Fleet Logistics Manager **who did not record it** decides to recover it from the driver or absorb it, with the reason. The decision emits an event for M52/M21; it is never a disciplinary input (BRU-FLT-17). Frozen once decided. |
| 1 | `fleet.vehicle` + ownership | Ownership basis (owned, leased, hired, employee-owned), contract reference, contract end and end-of-term obligation (FR-FLT-003). | A vehicle that is not owned names its contract and contract end. The basis is set and changed by a Fleet Logistics Manager. **M49 capitalises only an owned vehicle** (`cd_asset_finance_hse_bridge`). A lease bought out (basis changed to owned) capitalises at that point. |

Also:
- ACLs: nobody deletes. A plain employee only reads, except a defect, which any employee reports (spec §13, R10–R12/R16).
- Company and operating-unit record rules through the vehicle. A device in stock (no vehicle) is admitted explicitly: a null many2one path matches no `vehicle_id.company_id = False` clause. The live test caught this.
- Three sequences: VREN/, VDEF/, VPEN/.
- Cost per Kilometre gains a **Document Renewals** column. It is counted in the total and the cost/km. The pack note no longer says document fees are excluded.

### Workspace — `m46.js`, `controllers/a07/m46.py`, `writable.py`

- Four new list screens, each labelled in the navigation, with their actions served: Document Renewals, Defects, Telematics Devices, Traffic Fines & Penalties.
- Four new forms. The renewal and penalty forms are tabbed.
- The Vehicle form gains an Ownership tab. The PM Service form is now tabbed (Schedule / Execution). The Telemetry form names its registered device.
- The regenerated `writable.py` whitelists exactly the typed inputs, and no state, stamp or derived figure.
- Pickers: the renewed certificate is chosen among scanned documents; garages and telematics providers among companies.
- Every page now has its own capture and a chip for every record it lists:

| # | Page | "+ New" | Chips |
|---|---|---|---|
| 1 | Vehicle Register | Vehicle | Vehicle, **Vehicle Model, Vehicle Make** |
| 2 | Statutory Documents | Vehicle Document | **Vehicle Document, Document Renewal, Off-Road Record** |
| 3 | Drivers | Driver | Driver, **Traffic Penalty** |
| 4 | Assignment & Pool | Vehicle Booking | **Vehicle Booking** |
| 5 | Pre-Use & PM | Pre-Use Check | **Pre-Use Check, Vehicle Defect**, PM Service |
| 6 | Fuel & Odometer | Fuel Transaction | Fuel Transaction |
| 7 | Telematics | **Telematics Device** | **Telematics Device, Telemetry Snapshot** |
| 8 | Accidents & Insurance | Accident Report | Accident Report, **Traffic Penalty** (Insurers list now on the page) |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m46_capture_buttons.py` (node runs the engine's own `fregCreate`/`fregPanels` over the real registry) | **HEAD 48184ca8: 19 of 38 fail** (pages 1, 2, 3, 4, 5, 7, 8; page 7's own record; three orphan lists; the four registers; ownership, execution, device link, security, load order, M49). **After: 38/38.** |
| Live `cd_vehicle_ext/tests/test_m46_capture_live.py` (non-admin users with the real roles, rolled back) | **10/10.** Mutation check: switching off the renewal-penalty SoD, the safety-critical off-road, one-device-per-vehicle, the fine-decision SoD and the M49 ownership skip turns **5 tests red**; restored. The first run caught a real defect: a device in stock was invisible to every non-admin user (record-rule null path); fixed and asserted. |
| Regression on a freshly cloned and fully upgraded DB (`-u all`, 0 errors), with no server attached: all of `cd_vehicle_ext`, `cd_vehicle_dispatch`, `cd_asset_finance_hse_bridge` and `cd_asset_workorder_spine` tests, and every A07, estate-page, capture-button, write-whitelist, KPI and report-export portal suite | **2,161 tests, 14 failures, all environmental.** Every failure is a relay test: re-dispatch (5), spine (1), wiring round 2 (8). Each relays the oldest 5,000 unrelayed outbox events, and the `fix_test` template holds **53,624** unrelayed events from 8 to 14 Nov, so a test's own event is never reached. With that backlog marked relayed in the private clone, the three files pass **27/27**. **Baseline: the original code (HEAD 48184ca8) fails the same 14 on the project's own `fix_test`** (27 run, 14 failed, identical names), so the change adds no failure. Static estate guards: 1,750/0. |
| UI on a private server (port 8073, worktree code) | All 8 sub-module pages show the "+ New" and chips in the table above, read from the rendered page. The Telematics Device form was filled and saved through the UI ("Saved ✓"); the record is in the DB as Not Fitted. |

## 4. Not built here (owner decisions or other modules)

- **Class profile** (`fix.vehicle.class.profile`, FR-FLT-002/010): the mandatory documents are still one fleet-wide list (`cd_vehicle_ext.mandatory_document_types`), the licence class comes from the model type, and service intervals sit on each PM. A class-driven requirement set is a design change to the dispatch gate. The renewal cycles per class are still Open Question Q-02 with BRTA.
- **Automatic renewal task at 30 days** (AUT-FLT-01): a renewal needs a named responsible person, and no rule names one. The alerts still fire at 60/30/15/7/1 days.
- **Not modelled (P1/P2):**
  - stand-alone odometer reading (FR-FLT-030): readings are captured on the check, the fill, the service and the snapshot, and reconciled from those;
  - trip and usage record (FR-FLT-037);
  - tyre and battery lifecycle (FR-FLT-029);
  - pool handover condition (FR-FLT-021/022);
  - behaviour score from telematics events (FR-FLT-038): no event feed exists before M48;
  - replacement recommendation (FR-FLT-044): Retire raises the M49 disposal.
- **Owner gaps on fix_real:**
  - no M46 data at all;
  - one Fleet Logistics Manager and no direct Fleet Officer or Driver holder.

  Every new decision is two-person (renewal with a penalty, defect clearance, fine decision), so a second officer or manager is needed before those can complete.
- **Test environment:** the `fix_test` template's 53,624-event outbox backlog makes the relay tests fail on every clone. Draining it (or relaying it once in the template) is a test-estate task.

## 5. State — deployed 17 Nov 2026 (user-approved "Yes, deploy it")

- Commits 14a1e3bf (fix), b67fe42a and 4a80b3fa (report) were made on `fix/m46-capture-buttons`. All commit hooks passed.
- `fix/a03-live-data-and-pending-work` was fast-forwarded to them with a compare-and-swap `update-ref` from 48184ca8, and the shared checkout's files were synced. **Not pushed.**
- fix_real:
  - Backup: `all_working_folder/1000fix-2/_migration/backups/fix_real_pre_m46_deploy_2026-11-17.dump` (49 MB). An earlier one, `fix_real_pre_m46_capture_2026-11-17.dump`, also exists.
  - Ran `-u cd_vehicle_ext,cd_asset_finance_hse_bridge,cd_p03_portal`: exit 0, no errors. cd_vehicle_ext is now 19.0.0.4.0; the 4 new tables and the ownership column exist.
- 8069 was restarted once: the supervisor loop relaunched it in about 2 s (PID 49012). Registry: 155 modules, 0 errors, 0 "Failed to load registry".
- Verified on the deployed code:
  - all four new models exist and are served (`p03_generic_api.SURFACES`);
  - the ownership and service-execution fields exist;
  - the served bundle `web.assets_web` 88d58bb (HTTP 200) contains the four new forms, the new lists and the chips.
- **fix_dev (8090) was not upgraded.** It runs from the same checkout. Like the earlier capture deploys, it needs `-u` before its next restart, or its vehicle screens will miss the new columns.
- The 14 relay-test failures are pre-existing on `fix_test` (see §3) and are a test-estate task.
