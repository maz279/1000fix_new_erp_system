# M14 Trade-In & Refurbishment: data-capture button audit

**Date:** 13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** all three capture fixes LIVE on fix_real (8069/8089 restarted 03:39 Dhaka, 13 Nov); committed 5bedccca on fix/a03-live-data-and-pending-work (not pushed)

## 1. The question

The M14 workspace has 10 sub-module pages (Function Register sub-modules). Not all of them showed a relevant button to record data. Which pages should have one, what should it open, and what does the code really offer?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M14_TradeIn_Refurbishment_and_Resale.md` (FR-TRF-001 … 039, §8 state model, §9 rules, §10 entities, §13 roles and SoD)
- `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` (M14 = TRF, FR-TRF-001…039)

What each sub-module page is supposed to capture:

| # | Sub-module | What a person captures here (spec) | Right button |
|---|---|---|---|
| 1 | Intake (5 channels) | the trade-in request (FR-TRF-001) | **+ New** trade-in |
| 2 | Valuation Engine | a valuation run, and the governed reference price (FR-TRF-002/032/033) | **+ New** valuation; price-grid chip |
| 3 | Provenance Screening | the IMEI / blacklist / NEIR screen with evidence (FR-TRF-006, P0) | **+ New** screen |
| 4 | Settlement | the payout request on an accepted trade-in (FR-TRF-007) | pick the trade-in, then settle |
| 5 | Bulk Buy-Back | a corporate **lot**: client, contract, lot pricing, the client's declared asset list, per-unit reconciliation (FR-TRF-009, BRU-TRF-23, AUT-TRF-22, entity `fix.bulk.buyback`) | **+ New** lot with its declared assets |
| 6 | Destruction Gate | the M06 certificate attached to the collected unit, then the gate check (FR-TRF-011, BRU-TRF-01, P0). M14 must **never** issue the certificate: *"Anyone in M14 **and** issuing a destruction certificate"* is a forbidden combination (§13). | pick the collected unit, attach the certificate; **Data Wipe** on the list |
| 7 | Refurbishment Orders | a work order / rework step (FR-TRF-010/036) | **+ New** step on a unit in refurbishment |
| 8 | Grading & QA | the QA result and the grading certificate (FR-TRF-017/018/019) | **+ New** grade; QA chip |
| 9 | Resale | the **listing preparation**: channel, price, merchant (FR-TRF-021/022), then the unit is stocked and listed. The warranty is issued by the sale (FR-TRF-023), never typed. | pick the graded unit, prepare its listing; **Resale Ready** on the list |
| 10 | Harvesting | the harvest of a parts-only unit (FR-TRF-030) | **+ New** harvest |

## 3. What the code had (before)

Measured by running the workspace engine's own `fregCreate` / `fregPanels` in node over the real registry (`static/src/a05/m14.js`):

| # | Page | Before | Defect |
|---|---|---|---|
| 5 | Bulk Buy-Back | "+ New Trade-In Request" | **Wrong record.** The page listed every trade-in (no slice) and offered the single-unit intake. There was no lot model, no declared asset list and nothing to reconcile, so FR-TRF-009 / BRU-TRF-23 could not be done at all. |
| 6 | Destruction Gate | **nothing** (`forms: []`, `create: false`) | No way to attach the M06 certificate the gate checks. It could only be typed on the 6-tab intake dossier, and the page's list was the whole intake list with 9 buttons. |
| 9 | Resale | **nothing** (`forms: []`) | No way to prepare a listing. Channel, price and merchant sat on tab 5 of the intake dossier, and **Resale Ready** was only on the intake list. |
| 2, 3, 7, 8, 10 | Valuation, Provenance, Refurb, Grading & QA, Harvest | "+ New" worked | Each **Trade-In picker offered every trade-in**, but each model refuses all but one stage (§4). A user picked a unit and the Save failed. |

Data on fix_real (13 Nov): **0** rows in every M14 table (trade-ins, valuations, grid, provenance, refurbishment, grades, QA, harvest, warranties, graded stock, M06 certificates). So nothing could be demonstrated with live records, and the missing buttons were the only way in.

## 4. Rules in the models that the pickers ignored

| Form | The model refuses | Picker now offers |
|---|---|---|
| Automated Valuation File | apply after acceptance (`action_apply_to_tradein`) | draft / offered trade-ins |
| Provenance Screening | (any open trade-in) | not closed / rejected |
| Refurbishment Work Order | a step outside refurbishment cannot start | in refurbishment |
| QA & Battery Health | create unless the unit is in refurbishment | in refurbishment |
| Grading Certificate | create unless the unit is in refurbishment | in refurbishment |
| Harvest to Parts | harvest unless graded and grade E | graded or closed, grade E |

A picker's current value is still shown on an existing record (the server inserts it), so old records do not go blank.

## 5. What was changed

### 5.1 Front end (live on save; `static/src/a05/m14.js`)

- **Destruction Gate page:** new list **Destruction Gate** (`M14-gate`): collected and data-wiped units, with **Data Wipe (passes the gate)** and **Refurbish**. New step form **+ Attach Destruction Certificate** (`M14-form-wipe`): step 1 picks a collected unit, step 2 attaches a **verified** M06 certificate (picker filtered to `sanitization_status = verified`). The gate still re-checks verification, the log hash and the media serial. No M14 page offers to issue a certificate.
- **Resale page:** new list **Resale Preparation** (`M14-resale-prep`): graded units, with **Resale Ready (stock and list)**. New step form **+ Prepare a Resale Listing** (`M14-form-resale`): step 1 picks a graded unit that is not grade E, step 2 sets channel, price, merchant and listing date. Those freeze at Resale Ready (model rule `_FROZEN_FROM`).
- **Graded Stock** list now says where its rows come from (it cannot be typed).
- **Pickers:** the six Trade-In pickers of §4 carry their stage filter.

### 5.2 Bulk buy-back lot (needs a module upgrade and restart; built in an isolated worktree)

- New models in `cd_tradein` (`models/fix_bulk_buyback.py`):
  - `fix.bulk.buyback`: client, contract ref, account manager, lot pricing (per-unit or agreed lot price), counts (declared, reconciled, exceptions, pending), state Draft → Received → Closed.
  - `fix.bulk.buyback.asset`: declared asset (tag, serial/IMEI, make/model), its trade-in, its documented exception, and a reconciliation status.
- **Receive Lot & Open Intakes** (AUT-TRF-22) opens one draft trade-in per declared asset, linked to the registered device when the serial/IMEI matches exactly one. Each unit then goes through valuation, provenance, the M06 gate and settlement like any trade-in (per-unit certification). It can be run again for an asset declared after receipt.
- **Close Lot** (BRU-TRF-23) is refused while any declared asset has neither a live intake nor a documented exception. A rejected intake puts its asset back to "not reconciled".
- Guards: the asset→trade-in link and the state are set only by the actions; a received lot keeps its client and pricing; a closed lot and its list are frozen; an asset with an intake is not deleted and its serial no longer changes; an asset is declared once per lot.
- No column is added to `fix.tradein.request`, so an un-upgraded restart cannot break the existing M14 screens.
- Workspace: list **Corporate Bulk Buy-Back** (`M14-bulk`) and form **Corporate Bulk Buy-Back Lot** (`M14-form-bulk`) with the declared-asset grid. Sub-module 5 now captures the lot.
- Security: access for internal users (no delete of a lot), company and operating-unit record rules (generated), sequence `BBK/<year>/`.

## 6. Tests

Run in worktree `C:\software_project\software_project_14\m14wt` against a private copy of fix_test (`fix_test_m14`, `cd_tradein` upgraded with exit 0).

| Suite | Result |
|---|---|
| `cd_p03_portal/tests/test_m14_capture_buttons.py` (new, node evaluates the engine's own `fregCreate`/`fregPanels`): every page offers its form, no certificate issuing, gate/resale lists and actions, bulk lot grid, the six picker filters, the whitelists | 21 passed; **13 of them fail on the old registry** |
| `cd_tradein/tests/test_m14_capture_bulk_buyback.py` (new, non-admin users through the real `/p03/model/write` and `/p03/model/action`): lot captured with its asset grid; one intake per asset with device match by IMEI; late declaration; close refused until reconciled, exception stamp; closed / received freezes; the link is never typed (ORM, create and form grid); duplicate serial; gate attach then Data Wipe; unverified and foreign certificates refused; resale listing then Resale Ready, listing frozen after | 12 passed |
| All `cd_tradein` tests (incl. the A05 M14 control suite), `test_a05_control_suite`, `test_all_submodule_mapping`, `test_estate_module_pages` (67 modules), `test_submodule_create_button`, `test_kpi_tiles_served` | together with the above: **863 passed, 6 skipped, 0 failed** |
| ruff 0.8.4 (pre-commit pin) check + format on every changed Python file | clean |

Live check: the 8069 debug bundle (`?debug=assets`, files read from disk) contains `M14-form-wipe` and `M14-form-resale` and does not contain `M14-form-bulk`. A click-through in the browser was **not** done: the Postgres crash in §8 ended the browser session, and the workspace now asks for the fix_real sign-in.

## 7. Status and what is left

| Item | Where | Live? |
|---|---|---|
| Destruction Gate page: list + Attach Destruction Certificate | shared checkout `m14.js` | **yes** (front end only, reached on save) |
| Resale page: Resale Preparation list + Prepare a Resale Listing | shared checkout `m14.js` | **yes** |
| Stage filters on the six trade-in pickers | shared checkout `m14.js` | **yes** |
| Bulk buy-back lot (models, security, sequence, surface, writable, screens, both test files) | shared checkout | **yes**: fix_real upgraded and 8089 then 8069 restarted at 03:39 Dhaka (§7.1) |

**Why the lot is not deployed yet.** `-u cd_tradein` also upgrades the modules that depend on it: `cd_marketplace`, `cd_settlement_ext`, `cd_ml_services` and `cd_asset_workorder_spine`. Another session has unfinished, uncommitted work in `cd_marketplace` (a new `fix.seller.consequence` model). The same work currently breaks `addons/conftest.py` for every pytest run in the shared checkout (`KeyError: 'fix.seller.consequence'` in the A04 `WRITABLE`). Upgrading now would push that half-built model into fix_real. Deploy once that work is committed, or with the owner's OK.

**Deploy attempt, 13 Nov 02:00–03:00 (owner approved "deploy now", then "upgrade all six, restart").**

1. Backup taken: `all_working_folder/1000fix-2/_migration/backups/fix_real_pre_m14_bulk_2026-11-13.dump`.
2. A drift check on a fix_real copy (scratchpad `m14/schema_drift.py`, run in `odoo-bin shell`) found 12 tables and columns that five other sessions' un-upgraded code expects: `cd_rate_card`, `cd_device_registry`, `cd_msp_contract`, `cd_ap_ext` (vendor invoice and purchase advance), `cd_crm_ext`. Any restart without upgrading them breaks those screens.
3. Rehearsal on the copy, `-u cd_tradein,cd_rate_card,cd_device_registry,cd_msp_contract,cd_ap_ext,cd_crm_ext`: exit 0, no ERROR, drift 0. The cascade reached about 150 modules.
4. **Stopped before touching fix_real.** Within 30 minutes the M04 session had written new, uncommitted models into `cd_front_desk`: 4 new tables, plus new columns on `fix_service_order`, `fix_token_queue` and `fix_walkin_intake`. Restarting with the six modules would break service orders. Adding `cd_front_desk` would ship a half-written M04 into fix_real (it is inside the `cd_device_registry` cascade anyway). Neither was approved, so fix_real was not upgraded and nothing was restarted.
5. The shared checkout was put back to its consistent live state: gate and resale stay; the lot code lives only in the worktree; `a05/writable.py` was regenerated with the M13/M18 sessions' entries intact.

**Deploy recipe when cleared** (a quiet window: no session mid-edit on a model, ideally after the pending commits). Copy the worktree's changed paths into the shared checkout:

- `cd_tradein`: `models/fix_bulk_buyback.py`, `models/__init__.py`, `security/*`, `data/ir_sequence.xml`, `tests/test_m14_capture_bulk_buyback.py`
- `cd_p03_portal`: `controllers/a05/m14.py`, `controllers/a05/writable.py`, `static/src/a05/m14.js`, `tests/test_m14_capture_buttons.py`

To deploy:

1. Copy those paths with `scratchpad/m14/apply_bulk.py` for the two `cd_p03_portal` files, so other sessions' edits in those files are kept, plus a plain copy of the new files.
2. Regenerate `a05/writable.py` with `form_fields.py --a05`. Never copy that file: it would drop other sessions' entries.
3. Run the drift check on a fresh fix_real copy, and add every module it names to `-u`. Rehearse on the copy until drift is 0.
4. Back up fix_real and upgrade it.
5. Restart 8089, then 8069.
6. Confirm `/p03/model/records` serves `fix.bulk.buyback` and that no surface errors.

The lot's JS must go in at the same time as the restart: before it, its screens say "not served".

**Spec gaps found, not built (owner decision):**

- **Intake channel.** "Intake (5 channels)" has no field recording the channel a trade-in came in by: portal, app, counter, field or corporate (FR-TRF-001). `acceptance_channel` only records how the customer accepted. Adding it is a column on `fix.tradein.request` and needs the same upgrade.
- **Accessory and completeness capture** (FR-TRF-035, P3) is not modelled.
- **No sale button for a graded unit outside an order.** `fix.graded.stock.action_sell`, for an Inventory Controller walk-in sale, is offered on no workspace screen. M38 serves the model with no actions, so the counter / reseller sale and its resale warranty happen only through store or marketplace orders. I left this alone: a sale without an invoice would skip revenue posting.
- **Roles.** The lot uses the module's internal-user access like the rest of M14. The spec gives the corporate buy-back to R22 Account Manager and approval to Retail Operations; there are no such M14 groups yet.

### 7.1 Deploy, 13 Nov 03:32–03:41 Dhaka (owner rule: deploy at a quiet window, rehearsed first)

1. The lot was put into the shared checkout. The two portal files were patched in place, and `a05/writable.py` was regenerated, not copied.
2. Fresh backup: `_migration/backups/fix_real_pre_m14_bulk_2026-11-13b.dump` (47.9 MB). A fresh copy `fix_real_m14r` was made with parallel query off.
3. Drift check on the copy: another session had since deployed the estate, so only `cd_msp_contract` (3 items, last changed 03:25) was missing.
4. Rehearsal `-u cd_tradein,cd_msp_contract` on the copy: exit 0, no ERROR, drift 0. The lot registered 2 models, 2 access rights and 3 record rules. The 33 lot and capture tests pass on the real-data copy.
5. Gate check: no model, data, security, manifest or controller file changed between the start of the rehearsal and the production upgrade.
6. fix_real upgraded with the same command: exit 0, no ERROR, the lot registered.
7. 8089 restarted (pid 51620 → 67572), then 8069 (pid 40252 → 50152, started 03:39:33). Both answer `/web/login` 200.
8. Verified on fix_real:
   - The live 8069 bundle contains the lot screens.
   - A fresh shell on the same code and DB serves all 10 M14 surfaces, `fix.bulk.buyback` included, with its two actions and 10 writable fields.
   - The `BBK/` sequence exists.
9. Cleanup: rehearsal and test DBs dropped, worktree removed.

The browser click-through was not done: the 8069 browser session is signed out since the Postgres incident (§8).

Note: before this deploy, another session's upgrade of fix_real at 02:52–02:53 had picked up part of the lot. It left an empty `fix_bulk_buyback` table and its sequence while the lot code was briefly in the shared checkout. The deploy above registered them properly.

## 8. Incident during this audit

At 17:01 UTC (01:01 Dhaka), Postgres crashed and spent about 25 minutes in recovery. During that time 8069 and every other server were down.

**Cause.** Two DB restores were running at once: my clone of fix_test, and another session's restore. Their parallel foreign-key checks filled the container's 64 MB `/dev/shm` (*"could not resize shared memory segment … No space left on device"*). One backend then segfaulted, which restarted the cluster, and recovery had to fsync 178 databases (49 GB).

**What I did.** I set `max_parallel_workers_per_gather=0` only after my restore; it must be set **before** it. My clone was rebuilt with parallel query off from the start, and `/dev/shm` stayed at about 33 % use.

**Side effects to check.**

- The browser session on 8069 was logged out.
- Any session that was writing or restoring at 01:01 Dhaka may have lost uncommitted work.
