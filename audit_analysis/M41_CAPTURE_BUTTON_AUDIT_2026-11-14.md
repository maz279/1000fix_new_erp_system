# M41 Warehouse Management — Sub-Module Capture Audit (2026-11-14)

**Trigger.** The user observed that not every M41 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M41_Warehouse_Management.md`. Sections used: §5 FR-WMS-001…041, §6 T-04/T-15, §9 BRU-WMS-01…18, §10.1 owned entities, §11 AUT-WMS.
- Code:
  - `cd_p03_portal/static/src/a06/m41.js` (the page registry);
  - `controllers/a06/m41.py` (surfaces);
  - `cd_inventory/models/fix_wms_ops.py` (the floor models);
  - `cd_wms_structure` (warehouse, zone and bin).

## 1. What was there (HEAD 54dd2ae3)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| # | Page | "+ New" | Form chips | Defect |
|---|---|---|---|---|
| 1 | Physical Structure | Bin | Bin | No zone or warehouse capture. The zone list was on no page. |
| 2 | Slotting | Slot | — | No chip. No pick-face minimum anywhere. |
| 3 | Inbound & Put-Away | Put-Away | Dock Appointment | The scan-receiving list (a goods receipt with its inspection gate) had no capture. |
| 4 | Wave Planning | Wave | Wave Template | There was no wave-template list. |
| 5 | **Picking** | **none** | **none** | The mapping said `create: false`. The pick-line list, the only place a pick is scanned, was on no page. A bin holding less than the ledger could not be reported short (FR-WMS-024). |
| 6 | Packing & Staging | Carton | Packing Station | No staging capture. There was no packing-station list. |
| 7 | **Replenishment** | **none** | **none** | The page listed the spare-part master. No bin-to-bin move existed, and a "replenish" task completed **without moving anything** (FR-WMS-028/029/030). |
| 8 | **RF Execution** | **none** | **none** | There was no one-step task claim, no scan-completion form, and no RF device register (FR-WMS-036/038, T-04, T-15). |
| 9 | **Labour & Analytics** | **none** | **none** | There was no operative profile and no handling-equipment record, so BRU-WMS-18 could not even be stated. Floor counts had no chip. |

In summary:
- 4 of the 9 pages captured nothing.
- 4 more pages offered only part of what they list.
- Four §10.1 floor records had no model at all: `fix.wh.replenishment`, `fix.wh.operative`, `fix.wh.equipment` and `fix.wh.device`.

## 2. What was built

### Backend — `cd_inventory` 19.0.1.3.0

**New file `models/fix_wms_ops_floor.py`.** Its name sorts after `fix_wms_ops`, so ruff's import order keeps the load order correct.

- **`fix.wms.move`: internal move and replenishment** (FR-WMS-028/029/030)
  - It is a bin-to-bin move inside one warehouse, so the M15 location total never changes (BRU-WMS-01). A test asserts this.
  - Creating a move raises its task in the queue (FR-WMS-035).
  - It is confirmed by scanning the from-bin, the to-bin and the item (BRU-WMS-05).
  - Only free stock moves. Stock allocated to a wave does not move.
  - A move is refused when the target bin:
    - is blocked (BRU-WMS-12);
    - is in a quarantine or inspection zone;
    - is not hazardous-class and the part is hazardous (BRU-WMS-11);
    - holds a different ownership class (BRU-WMS-03);
    - would exceed its capacity (BRU-WMS-09).
  - A move between warehouses is refused; that is an M15 transfer.
  - A done or cancelled move is final.
- **Slot pick-face minimum.** New fields `min_qty` / `max_qty` and the action **Raise Replenishment**.
  - The move comes from the bulk slot with the most free stock, in the same warehouse and of a compatible ownership class.
  - Only one replenishment per pick face may be open at a time.
  - **AUT-WMS-11:** a pick that takes a pick face below its minimum raises the replenishment automatically.
- **Short pick** (`action_scan_short_pick`, FR-WMS-024 / BRU-WMS-07):
  - the operative scans the bin and gives the quantity actually there;
  - that quantity is picked and the line goes short;
  - an immediate count-back task is raised;
  - the ledger is corrected only by the approved M15 count;
  - an empty bin needs no item scan.
- **Task claim** (`action_claim`, FR-WMS-036, T-04):
  - the row is locked with `FOR UPDATE NOWAIT`, so two devices can never claim the same task;
  - only an open task can be claimed.
- **Equipment rule** (BRU-WMS-18): the task field `equipment_required` is checked on assign and on claim against the operative's profile.
- **`fix.wms.operative`, `fix.wms.equipment` and `fix.wms.device`** (FR-WMS-039, T-15):
  - only a Warehouse Supervisor, an Inventory Controller or the IT administrator writes them;
  - a device is deactivated with a reason, and a different administrator reactivates it.
- Supporting changes:
  - ACLs: nobody deletes, and a plain employee reads only;
  - company isolation rules;
  - the `MOVE/%(year)s/` sequence.

### Workspace — `a06/m41.js`, `controllers/a06/m41.py`, `writable.py` (regenerated)

| # | Page | "+ New" | Form chips |
|---|---|---|---|
| 1 | Physical Structure | Bin | Bin · Warehouse Zone · Warehouse |
| 2 | Slotting | Slot | Slot Assignment (with the pick-face minimum) |
| 3 | Inbound & Put-Away | Directed Put-Away | Put-Away · Dock Appointment · Goods Receipt (scan receiving) |
| 4 | Wave Planning | Pick Wave | Pick Wave · Wave Template |
| 5 | Picking | **Scan a Pick** | Scan a Pick · Report a Short Pick |
| 6 | Packing & Staging | Carton | Carton · Staging Record · Packing Station |
| 7 | Replenishment | **New Internal Move / Replenishment** | Internal Move · Confirm a Move by Scan |
| 8 | RF Execution | **Complete a Task by Scan** | Complete by Scan · Claim a Task · Warehouse Task · RF Device |
| 9 | Labour & Analytics | **New Operative Profile** | Operative Profile · Handling Equipment · Floor Count |

New lists:
- Wave Templates, Packing Stations, Internal Moves & Replenishment, RF Devices, Operative Profiles and Handling Equipment, all with navigation labels;
- Zones and Pick Lines are now placed on pages.

The pick-style forms (Scan a Pick, Short Pick, Confirm Move, Complete Task, Claim) run the workflow method with the scans as inputs. No form writes a quantity, a state or scan evidence.

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m41_capture_buttons.py` (37 tests, engine evaluated in node) | **37 pass**. On HEAD 54dd2ae3: **26/36 fail**, every page flagged. |
| Live ORM `cd_inventory/tests/test_m41_capture_live.py` (16 tests, non-admin roles) | **16/16 pass** on a private clone `fix_test_m41` |
| Estate page standard + A06 write whitelist | pass |
| Server probe on a private server (port 8079): every M41 list, form, pick list and report endpoint | **56 calls, 0 errors**, no missing form field, no dropped column |
| Click sweep under `?debug=assets` | Each of the 9 pages shows its own "+" button. RF Execution was screenshotted with 4 capture forms. |
| Write path through `/p03/model/write` | Created warehouse → zone → bin → equipment → device → operative (with equipment). A forged `state` on a device was dropped. Deactivating without a reason was refused. A non-surfaced method was refused. |
| Defect caught by the live tests | The operative's same-warehouse check merged two recordsets of different models (a TypeError). Fixed. |
| Defect caught in the browser | The new lists showed raw ids ("M41-devices") because they were in no navigation group. Fixed, and guarded by a new test. |

## 4. Open — owner or spec gaps (not built)

- **No WMS data on fix_real.** There are no warehouse bins or slots, so pages show empty lists until the bin master is authored (spec §16.4).
- The **RF handheld app itself** (CD-144) and offline replay (T-06/T-07) are a mobile build. The workspace forms are the desk equivalent.
- Not built:
  - bin coordinates and pick-path sequencing (T-09, FR-WMS-022);
  - cross-dock (FR-WMS-016);
  - handling-unit nesting (T-11);
  - dock **slots** as master data;
  - labour time standards (FR-WMS-040).
- The spec's inspection-execution entity (sample size, evidence per line) is covered only by the M15 receipt's inspection gate. M23 owns the plan.
- Who holds the Warehouse Supervisor grant on fix_real decides who can create profiles, equipment and devices (spec §13: R17 with a supervisor grant).

## 5. Deploy to fix_real (user-approved, 14 Nov 2026 23:45 machine time)

- Commit `1015b9e8` landed on `fix/a03-live-data-and-pending-work` by `git update-ref` from the old tip `54dd2ae3`. It is unpushed.
- Backup: `_migration/backups/fix_real_pre_m41_capture_2026-11-14.dump` (48.8 MB).
- Upgrade: `-u cd_inventory,cd_p03_portal` on fix_real.
  - 155 modules loaded with 0 errors.
  - cd_inventory is at 19.0.1.3.0.
  - The tables `fix_wms_move/device/operative/equipment` and the task columns `move_id` and `equipment_required` exist.
- Restart: 8069 was relaunched with its own launcher at 23:47. `/web/login` returns 200.
- The production bundle `web.assets_web` `801fe70` contains the new screens (`M41-form-scan-pick`, `M41-devices`, `action_claim`).
- Read-only probe:
  - It ran as fix_real's one non-admin Warehouse Supervisor and was rolled back.
  - It covered all 22 models the M41 screens use, with 0 errors.
- fix_real holds 261 warehouses and 0 zones, bins, slots or tasks. The bin master is still to be authored (§16.4), so the new pages open on empty lists.
- Supervisor and operator grants have 1 holder each. They decide who can create operative profiles, equipment and RF devices.
