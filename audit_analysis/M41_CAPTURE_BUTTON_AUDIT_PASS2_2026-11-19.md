# M41 Warehouse Management — Sub-Module Capture Audit, Pass 2 (2026-11-19)

**Trigger.** The user again saw M41 sub-module pages without a relevant data-capture button, after pass 1 (14 Nov, `M41_CAPTURE_BUTTON_AUDIT_2026-11-14.md`) had given all nine pages a "+ New".

**Method.** Pass 1 counted buttons. This pass read each page's forms against what the spec says the page records:
- §5 FR-WMS-001…041;
- §6 T-01…T-16;
- §9 BRU-WMS-01…18;
- §10.1, the 19 owned entities.

For each page the question was: can a person record here what the spec says this sub-module records?

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M41_Warehouse_Management.md`.
- Code at HEAD `e73400f6`:
  - `cd_p03_portal/static/src/a06/m41.js` (pages, lists, forms);
  - `controllers/a06/m41.py`;
  - `cd_inventory/models/fix_wms_ops.py` and `fix_wms_ops_floor.py`;
  - `cd_wms_structure/models/fix_wms_structure.py`.

## 1. What was missing (HEAD e73400f6)

| # | Page | Button existed | What the form could not hold |
|---|---|---|---|
| 1 | Physical Structure | Bin, Zone, Warehouse | **FR-WMS-003 (P0):** no per-warehouse switch for warehouse execution, so every warehouse was implicitly "on". No wave cut-offs or shift pattern (§10.1). **FR-WMS-001:** zone types lacked bulk / pick / staging / secure, and a zone could not be reserved for one ownership class (T-02). **FR-WMS-002 (P0) / T-09:** a bin had no aisle/bay/level/position, no pick-face flag, no dimensions and no weight or volume limit. **FR-WMS-034:** when a block was lifted, its reason and actor were lost. |
| 2 | Slotting | Slot | Complete (velocity, slot type, pick-face min/max from pass 1). |
| 3 | Inbound & Put-Away | Put-Away, Dock, Receipt | **FR-WMS-013 (P0):** the "directed" put-away was a bin the user typed. There was no strategy, no record of rejected bins (T-01) and no override reason or approval (FR-WMS-014, BRU-WMS-06). **FR-WMS-015:** no way to report a full bin, a blocked bin or a damaged item. **FR-WMS-008:** no dock door master and no unload clock. **FR-WMS-010 / T-11:** no handling unit (licence plate), although §3.3 says M41 *owns* it. **FR-WMS-016:** no cross-dock. **FR-WMS-017:** no return receiving with a disposition. **FR-WMS-011 (P0):** M16's inspection record was not reachable from the page. |
| 4 | Wave Planning | Wave, Template | **FR-WMS-018 (P0):** no outbound demand queue. Demand existed only as lines typed into a wave, with no source, destination, priority or cut-off. **FR-WMS-019:** templates had no purpose, release rule, priority or destination filter. **FR-WMS-021:** no cluster or pick-and-pass strategy. **FR-WMS-022:** no pick path. |
| 5 | Picking | Scan / Short Pick | **FR-WMS-024 (P0):** a short pick recorded the shortfall and the count-back but never re-sourced the shortfall from another bin. |
| 6 | Packing & Staging | Carton, Stage, Station | **FR-WMS-025:** no handling-unit chip. |
| 7 | Replenishment | Move | Complete (pass 1). |
| 8 | RF Execution | Task, Claim, Device | Tasks carried no walk order, no start time and no time standard. |
| 9 | Labour & Analytics | Operative, Equipment, Floor Count | **FR-WMS-031 (P0):** counting was one bin at a time; there was no way to count a zone, a set of bins or an ABC class. **FR-WMS-040:** no time standard and no productivity record (§10.1 `fix.wh.productivity`, AUT-WMS-15). |

## 2. What was built

M41 still never authors a stock quantity (BRU-WMS-01). Every ledger effect below goes through `fix.stock.onhand`, as the pass-1 floor records do.

### Structure — `cd_wms_structure` 19.0.1.1.0, new `models/fix_wms_layout.py`

**Warehouse (FR-WMS-003, BRU-WMS-02)**
- New fields `wms_enabled`, `wave_cutoffs` (validated HH:MM) and `shift_pattern`.
- Only a Warehouse Supervisor or the IT administrator may enable or disable execution.
- A zone cannot be created in a warehouse that is not enabled.
- Execution cannot be turned off while bins hold stock or tasks are open.
- Migration `19.0.1.1.0/post-migrate.py` enables every warehouse that already has zones, so existing layouts keep running.

**Zone**
- New zone types: bulk, pick, staging and secure.
- A zone can be reserved for one ownership class; bins in it must then match that class (T-02).
- New walk sequence.

**Bin (FR-WMS-002, T-09)**
- Coordinate fields: aisle, bay, level and position.
- Pick-face flag, length / width / height, weight limit and volume limit.
- A stored serpentine `pick_sequence`: zones in their walk order, odd aisles walked up and even aisles walked back down.

### Floor records — `cd_inventory` 19.0.1.5.0, new `models/fix_wms_ops_spec.py`

| Page | Record / control | Rules enforced |
|---|---|---|
| 1 | `fix.wms.bin.block.log` (FR-WMS-034) | Append-only. Written only by Block and Unblock, and records how long the bin was blocked. |
| 1 | Slot weight/volume constraint | BRU-WMS-09 now covers kg and m³, using the product's weight and volume, not only the unit count. |
| 3 | **Directed put-away** (FR-WMS-013/014, T-01) | Strategy sequence: fixed bin → existing stock → near the pick face → nearest empty bin → bulk. It respects capacity, weight, volume, storage class and ownership class. It stores the strategy that answered and every rejected bin with the reason. |
| 3 | **Override** (BRU-WMS-06) | Choosing a different bin needs a reason. The put-away then waits for approval by a Warehouse Supervisor who is not the overrider, and cannot be completed until then. The `wh.directive_overridden` event is published. |
| 3 | `fix.wms.putaway.exception` (FR-WMS-015/033) | Full bin or blocked bin: the put-away is re-directed to the next eligible bin, and a full bin gets a count-back task. Damaged item: recorded. |
| 3 | `fix.wms.dock.door` + appointment `door_id`, arrival / unload start / completion times (FR-WMS-008) | Door direction must match the appointment. Doors are master data, set by a supervisor or IT. |
| 3 | `fix.wms.handling.unit` + content lines (FR-WMS-010, T-11) | Licence plate `HU/`. One level of nesting only. Contents cannot exceed what the receipt accepted. Contents are final once the unit is closed. Store = scan the bin. |
| 3 | `fix.wms.crossdock` (FR-WMS-016, BRU-WMS-15) | Only from a posted receipt line, only to the demand line of a wave that is not yet released. Confirm (scan the item) moves stock unrestricted → staged and shrinks the demand. Dispatch ships it. The cross-docked quantity can no longer be put away. |
| 3 | `fix.wms.return.receipt` (FR-WMS-017) | Held in a returns-zone bin. The disposition is decided by a supervisor or inventory controller who did not receive it. Restock raises a directed put-away. Quarantine, RTV, refurbishment and scrap must name their M15 record. |
| 3 | Chip to M16's inspection form + an "Inspection Outcomes" list (FR-WMS-011) | M23/M16 own the plan; M41 executes it. |
| 4 | `fix.wms.outbound.demand` (FR-WMS-018/020) | Source, destination, priority and cut-off. "Build Wave" groups demand into one draft wave per warehouse and template. It picks from free slot stock (pick faces first, then walk order), splits across bins, and refuses when stock is short. |
| 4 | Wave template purpose, release rule, priority, warehouse, destinations (FR-WMS-019); cluster and pick-and-pass strategies (FR-WMS-021) | Demand outside a template's destinations is refused. A wave takes its strategy and cut-off from its template. |
| 4/8 | Pick walk order (FR-WMS-022) | On release, lines and tasks are numbered in bin `pick_sequence`. |
| 5 | Short-pick re-source (FR-WMS-024, AUT-WMS-09) | The shortfall becomes a new pick line from another bin with free stock, allocated in M15 and on the slot, with its own task. The short line closes at what was picked. |
| 9 | `fix.wms.count.plan` (FR-WMS-031) | Scope: bins, zone, velocity (ABC) class or the whole warehouse. Generates one blind floor count and one task per slot, skipping slots already under count. Closes only when no count is open. |
| 9 | `fix.wms.time.standard`, task `claimed_at` / `time_standard_sec` (FR-WMS-035/040) | Standards are set by a supervisor. |
| 9 | `fix.wms.productivity.run` + `fix.wms.productivity` (FR-WMS-040, AUT-WMS-15) | Measured by a supervisor, and nightly by cron, from completed tasks only. Rows are never typed. |

**Security**
- 24 ACL rows: users read only, nobody deletes (except an open unit's content line).
- Company rules for all 12 new models.
- 6 sequences and the nightly cron.

### Workspace — `a06/m41.js`, `controllers/a06/m41.py`, `writable.py` (regenerated)

**New lists, all with navigation labels**
- Bin Block History, Put-Away Exceptions, Dock Doors, Inspection Outcomes, Handling Units, Cross-Dock, Return Receiving.
- Outbound Demand Queue.
- Count Plans, Time Standards, Productivity Runs, Labour Productivity.

**Forms**
- Bin and put-away forms are now tabbed (workspace standard for forms over 15 fields).
- The warehouse, zone, dock, wave (with demand columns on its lines), template and floor-count forms carry the new fields.

**New forms**
- Report a Put-Away Exception: pick a put-away, then run the workflow method.
- Dock Door, Handling Unit (content grid), Cross-Dock, Return Receiving (tabbed), Outbound Demand, Count Plan, Time Standard.
- Productivity Run, with a read-only results grid.

**Page captures after this pass**

| # | Page | "+ New" | Capture chips |
|---|---|---|---|
| 1 | Physical Structure | Bin | Bin · Warehouse Zone · Warehouse |
| 2 | Slotting | Slot | Slot Assignment |
| 3 | Inbound & Put-Away | Directed Put-Away | Directed Put-Away · **Report a Put-Away Exception** · Dock Appointment · **Dock Door** · Goods Receipt · **Inspection Outcome (M16)** · **Handling Unit** · **Cross-Dock** · **Return Receiving** |
| 4 | Wave Planning | Pick Wave | Pick Wave · **Outbound Demand** · Wave Template |
| 5 | Picking | Scan a Pick | Scan a Pick · Report a Short Pick (now re-sources) |
| 6 | Packing & Staging | Carton | Carton · Staging Record · **Handling Unit** · Packing Station |
| 7 | Replenishment | Internal Move | Internal Move · Confirm a Move by Scan |
| 8 | RF Execution | Complete a Task by Scan | Complete · Claim · Warehouse Task · RF Device |
| 9 | Labour & Analytics | Operative Profile | Operative · Equipment · **Count Plan** · Floor Count · **Time Standard** · **Labour Productivity Run** |

### Existing tests and seeds adjusted (behaviour change, deliberate)

- **Fixtures enable warehouse execution.** Fixtures that lay zones into a warehouse now set `wms_enabled`. This touched 6 test files and both A06 seeds; `seed_a06_gap_b1` enables it as superuser, since the operator may not.
- **Put-away helper records an override.** The shared `putaway()` test helper names a bin on purpose, to exercise that bin's rule (capacity, quarantine, hazard, ownership class, blocked). It now records an override reason, and a second supervisor approves it. Before this pass, those tests typed a bin the directive would not have chosen, and nothing objected.

## 3. Evidence

All runs used the private clone `fix_test_m41c2` (a copy of fix_real), upgraded with `-u cd_wms_structure,cd_inventory,cd_p03_portal`. The upgrade logged 0 errors: the 3 "ERROR" lines it printed are RST warnings in module descriptions.

| Check | Result |
|---|---|
| Pass-2 guard `cd_p03_portal/tests/test_m41_capture_pass2.py` (pages evaluated with the engine's own `fregCreate` / `fregPanels` in node; forms, whitelist, ACLs and rules read directly) | **36/36 pass.** On HEAD `e73400f6`: **33 fail.** |
| Pass-1 guard `test_m41_capture_buttons.py` | Pass. Its probe now also accepts the M16 inspection form. |
| Live ORM `cd_inventory/tests/test_m41_capture_pass2_live.py` (19 tests, run as non-admin operator, keeper, supervisor and controller) | **19/19 pass** |
| M41 suites (A06 controls, final pass, pass-1 live, pass-2 live, WMS ops, structure) | **125 / 0** |
| Mutation check: 35 mutants, each re-introducing one defect against the live suite | **34 red.** One survivor: "door created by an operator". The ACL refuses the operator with the same message, so the code check is a second, equivalent guard. "Unlimited nesting" first survived; a test was added for it and it now goes red. |
| Regression: all of `cd_inventory` and `cd_wms_structure`, plus the A06 / M15 / M41 / estate / write-whitelist / registry tests of `cd_p03_portal` (1,831 tests) | **Final run: 1,828 pass / 3 fail, 0 errors; the 3 are environmental (below).** The first run had 12 fails. **9** came from the new directive (older tests naming bins); fixed through the helper above. **3 are environmental:** they fail identically with the HEAD code on an untouched fix_real clone (`fix_test_m41base`). `m15_83`: a real fix_real user holds the Inventory Controller role. `b18` / `b19`: a storekeeper cannot read a location under fix_real's OU rules. |
| Headless walk on private server 8191 (`walk_m41.mjs`) | **9/9 pages** open, each with its own "+ New". **All 35 capture chips** found and opening forms. **36/36 new and changed screens** render. **0 console errors.** |
| Endpoint probes `/p03/model/*` | 7 new lists read their columns. A dock door was created through `/p03/model/write`. A forged `state: waved` on a new demand was dropped (it stayed queued). A forged `override_state` was refused ("read-only … workflow action"). `action_report_exception` ran through `/p03/model/action`. A private method was refused ("Action not available for this surface"). |
| Defect the walk data exposed | A dock appointment's double-booking check compared dock *codes* across the whole company, so door D1 of one warehouse blocked D1 of another. The check is now per door. A test covers both cases. |

## 4. Open — not built, owner or other-module work

Part 2 (section 6) closed the scan log, the demand feed for transfers / van replenishment / RTV with auto-release, substitution, the slotting proposals and the RF API. Still open:

- **The RF handheld app itself** (CD-M41-04 mobile build). Its server side, `/api/v1/wh/*`, now exists.
- **Refurbishment and job issues into the demand queue.** These are M14/M31 consumptions with their own scan-to-consume flow. Routing them through a wave needs an M14/M31 hand-off design, so they are still queued from the page.
- **Cartonisation proposal** from part dimensions (FR-WMS-025): it depends on M37 recording part dimensions first. Also not built: the layout map (FR-WMS-007), task interleaving (FR-WMS-037) and congestion rebalancing (FR-WMS-041).
- **Part weight and volume** come from the purchased-as product (`product_id.weight` / `.volume`). Most spare parts on fix_real have none, so weight and volume limits only bite once M37 records them.
- **Data on fix_real:** no warehouse has execution enabled and there are 0 zones, bins, slots, doors or standards. The pages open on empty lists until the owner (a) enables the central warehouse(s), and (b) lays out zones and bins (§16.4). The upgrade migration enables only warehouses that already have zones, so none on fix_real.
- **Who can act on fix_real:** the Warehouse Supervisor and Operator grants have 1 holder each. Enabling a warehouse, setting time standards, approving overrides and measuring productivity all need a supervisor.

## 5. State

**LIVE on 8069 (fix_real) and 8090 (fix_dev), 20 Nov 2026.** The user approved the deploy.

- Rebased onto `a12f34b2` and landed as `a8480732` (code) and `db6ee05c` (report), by a compare-and-swap `update-ref` plus `read-tree -m -u`. Pushed together with the branch `fix/m41-capture-pass2`.
- Backups: `_migration/backups/fix_real_pre_m41_capture2_2026-11-20.dump` (52.9 MB) and `fix_dev_pre_m41_capture2_2026-11-20.dump` (49 MB).
- Upgrade: `-u cd_wms_structure,cd_inventory,cd_p03_portal` on both databases, 0 errors.
  - Versions: cd_wms_structure 19.0.1.1.0, cd_inventory 19.0.1.5.0.
  - 28 `fix_wms_*` tables exist.
  - Warehouses enabled by the migration: 0 on fix_real, 3 on fix_dev (the ones that already had zones).
- One restart: each server was stopped by its listening port, and its relaunch loop brought it back. New PIDs: 8069 = 9816, 8090 = 11212. `/web/login` returns 200 on both.
- Read-only walk of both estates (`walk_m41.mjs`, `READONLY=1`): 9/9 pages, every capture chip opens its form, 36/36 screens render, 0 console errors. The new lists read their columns; they are empty on both estates, which is expected.
- Private test assets: DB `fix_test_m41c2`, launch entry `odoo-m41-cap2` (port 8191) and comparison DB `fix_test_m41base`.

## 6. Part 2 (2026-11-20): the items the owner chose to build

After pass 2 went live, the owner was asked item by item about the open spec work and chose five items. All are built in `cd_inventory` 19.0.1.6.0 (`models/fix_wms_ops_spec_flow.py`, `controllers/wms_rf_api.py`).

| # | Item | What it does | Rules enforced |
|---|---|---|---|
| 1 | **Demand feed and hand-off** (FR-WMS-018/027, AUT-WMS-07) | An approved M15 transfer, van replenishment or RTV out of a warehouse that runs execution queues its lines as outbound demand by itself. The wave that picks them performs the document's **own** dispatch when it ships: a transfer moves staged → in transit (the sender keeps it, BRU-INV-16) and is marked dispatched by the shipper; an RTV posts its own ledger exit. | The wave never ships that stock a second time. A direct M15 dispatch of a waved document is refused; of a merely queued one, it takes the demand off the queue. A transfer or RTV ships whole, so a short line must be re-sourced or cancelled first. A cancelled wave puts its demand back in the queue, and a waved transfer can't be cancelled until its wave is. |
| 1 | **Auto-release** | A template with release rule "at the cut-off" builds and releases its wave once per cut-off (cron every 15 min); "immediate" releases on arrival. Demand is assigned to the warehouse's template by purpose and destination. | Demand the bins cannot cover stays queued with the reason ("Waiting Because"), never half-waved. |
| 2 | **Scan log** `fix.wms.scan.event` (§10.1 `fix.wh.task.event`) + **Attempted Violations** report (§14) | Every put-away, pick, short pick, move, cross-dock, handling-unit store and task completion records who scanned what, on which device, and whether it was accepted. | A **refused** attempt is written in its own transaction, so it survives the rollback, with the rule that refused it (BRU-WMS-03 ownership class, -05 wrong bin/item, -11 hazard, -12 blocked). The log is append-only. |
| 3 | **Substitute pick** `fix.wms.substitution` (FR-WMS-023) | A short line can be filled with a part that M37 (`fix.part.crossref`) lists as an approved alternate (one way from the asked part, or two way), from a bin that holds it free. On approval it becomes a new pick line with its own task. | Approved by a supervisor who did not request it. Never for a transfer or RTV line, which moves one named part. Never with an alternate restricted to certain device models. |
| 4 | **Slotting proposals** `fix.wms.slot.proposal` (FR-WMS-006/030, AUT-WMS-15) | Nightly, and on demand from the warehouse list ("Propose Re-slotting Now"): slot velocity is recomputed from 90 days of picks (thresholds `cd_inventory.wms_fast_picks_90d` = 20 and `_medium_` = 5). A fast mover outside a pick face gets a re-slot proposal; a part split across bins of one class gets a consolidation proposal. | A supervisor accepts (it becomes an open move with its task, confirmed by scan) or rejects. Never proposed twice; proposals are never typed. |
| 5 | **RF API** `/api/v1/wh/tasks/next`, `/claim`, `/confirm`, `/exception`, `/sync`, `/handling-units/<code>` + journal `fix.wms.rf.journal` (T-04/06/07/15) | The operative's own API key (bearer) plus the enrolled device code. Returns the current task and the next three; Bengali part names; no cost fields. | Every confirmation carries an idempotency key; a replay returns the stored outcome and never runs twice. An unknown or deactivated device, or one issued to someone else, is refused. Actions run as the operative, under the same rules as the forms. |

**Workspace:**
- Substitutions list and "Request a Substitute Part" form (page 5).
- Slotting Proposals (page 2).
- Scan Log, RF Confirmations and the Attempted Violations report (page 8).
- Demand form shows its transfer / RTV and why it waits; templates show their last auto-release.
- Form status labels cover the new states.

**Evidence** (private clone `fix_test_m41c3` of fix_real, upgraded 0 errors):
- **Guard:** the pass-2 guard now has 42 checks; 7 part-2 checks fail on the live code `d338215a` and all pass now. Pass-1 + pass-2 static: 79 pass.
- **Live ORM:** `test_m41_capture_pass2b_live.py`, 16 tests as non-admin roles, all pass. The refused scan is read back from its own committed transaction.
- **Mutation check:** 24 mutants against part 2, **23 red**. The one survivor ("an operator accepts a proposal") is refused by the ACL with the same message, so the code check is a second guard. "RF runs as superuser" survived at first, because `sudo()` keeps the user id; the test now also requires the scan to be logged under the device, and that mutant goes red.
- **Regression:** 1,888 tests. 3 environmental fails, the same as before. A form-status gap (`shipped` / `handed` labels) was found and fixed, and a seed-time serialization blip passed on re-run.
- **HTTP probe** of the RF API on private server 8193, with a test operative's API key:
  - no key → 401;
  - `next` returns the task;
  - claim and confirm succeed;
  - the same key replayed returns `replayed: true`;
  - sync replays idempotently;
  - an unknown device → forbidden.
- **Feed on real data:** approving a transfer on the clone queued its demand, and the wave was built and released from it.
- **Walk:** 9/9 pages, all chips including the substitute form, 42/42 screens, 0 console errors.
