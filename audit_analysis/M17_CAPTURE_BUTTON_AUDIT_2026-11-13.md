# M17 Device & Asset Registry: data-capture button audit

**Date:** 13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** live on 8069 (fix_real upgraded), committed 472ee6c6, not pushed

## 1. The question

The M17 workspace has 11 sub-module pages (Function Register, 96 functions). Not every page showed a button to record data. Which pages should have one, and what should it open?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M17_Device_and_Customer_Asset_Registry.md`: FR-AST-001…052, BRU-AST-01…23, T-01…16, AUT-AST-01…18, roles §13
- `all_working_folder/working/A07_evidence/module_findings/M17.md`: the A07 workflow audit, which found no bulk load (BRU-AST-18) and forgeable service history (M17-7)

| # | Sub-module | Spec | What a person records |
|---|---|---|---|
| 1 | Identity & Resolution | FR-001…010 | the asset and its identifiers; provisional identity |
| 2 | Configuration & Components | FR-011…016 | installed components; the part-compatibility matrix |
| 3 | Ownership & Custody | FR-017…023, BRU-06/08/09 | **custody events** (rider, front desk), **ownership transfers** with evidence, **lost/stolen reports** |
| 4 | Service History | FR-024…026, T-05/T-06, AUT-05, BRU-07 | nothing. The timeline is a projection of orders and events and is never typed. |
| 5 | Parts Genealogy | FR-027/028/031 | the fitted or removed component and its disposition |
| 6 | Repeat-Fault Detection | FR-029/030, BRU-13 (computed) | nothing: it is detected from the history |
| 7 | Warranty Projection | FR-032…037 | the device warranty with proof |
| 8 | Corporate Estates | FR-038…043 | the estate, and **placing a device in it** ("each asset placed at exactly one node") |
| 9 | Bulk Registration | **FR-039 (P0)**, BRU-18, T-10, AUT-11 | **an estate file**: validated row by row, rejects reported per line, committed as a set |
| 10 | Condition & EOL Routing | FR-044…049 | condition grade; PM plan; end-of-life decision (asset list actions) |
| 11 | Data Quality | FR-006/007/050/051 | identity-resolution candidate; stewardship (alerts) |

## 3. What the code had (before)

This was evaluated with the workspace engine's own `fregCreate` / `fregPanels` (run by node) over the real registry fragments, the same way the browser computes the page.

| # | Page | Button before | Defect |
|---|---|---|---|
| 1 | Identity & Resolution | + New Asset, chip "Asset (6 identifiers)" | The chip said 6 identifiers; the form has 5. Identifier History & NEIR (where a Branch Manager records NEIR results) was on **no page**. |
| 2 | Configuration & Components | + New Installed Component | The compatibility list was on the page, but its form had no chip. |
| 3 | Ownership & Custody | **nothing** | No "+ New". The only chip, "Ownership Transfer", opened a **read-only** history form. No custody event, no transfer and no lost/stolen report could be recorded from the page. Lost/Stolen Holds was on no page. |
| 4 | Service History | nothing | Correct (projected), but the list did not say where its rows come from. |
| 5 | Parts Genealogy | + New Installed Component | No chip. The component form went back to a report, not its list. |
| 6 | Repeat-Fault Detection | nothing | Correct (computed); no "where rows come from" text. |
| 7 | Warranty Projection | + New Device Warranty | Correct. |
| 8 | Corporate Estates | + New Estate, chip "Estate Assignment" | "Estate Assignment" opened the **estate master**. A device could not be placed in an estate from the page. |
| 9 | Bulk Registration | + New Asset (one device) | **No bulk load existed anywhere in the code.** The page showed a readiness report and a single-asset button. The module description admitted "no bulk load yet". |
| 10 | Condition & EOL Routing | + New Condition Grading | The PM plan list was on the page, but its form had no chip. The asset list, which holds the end-of-life actions, was not on the page. |
| 11 | Data Quality | + New Identity Resolution | Merge Lineage & Reversal and the M17 Alerts list were on **no page**. |

Totals: 3 pages could capture nothing they should (3, 8 placement, 9). 4 pages hid forms that already existed (2, 5, 10, 11). 4 working screens were on no page.

## 4. What was changed

### 4.1 Workspace (`cd_p03_portal/static/src/a07/m17.js`)

| # | Page | Now offers |
|---|---|---|
| 1 | Identity & Resolution | + New Asset; chip "Asset (5 identifiers)"; Identifier History & NEIR added to the page |
| 2 | Configuration & Components | + New Installed Component; chips Installed Component, **Part Compatibility** |
| 3 | Ownership & Custody | **+ New Custody Event**; chips **Ownership Transfer** (pick the device, then a governed transfer with reason and evidence upload), Custody Event, **Report Lost / Stolen** (pick, then the flag); Lost/Stolen Holds added |
| 4 | Service History | no button (correct); the list explains that history is written by orders and registry events |
| 5 | Parts Genealogy | + New Installed Component; chip Installed Component |
| 6 | Repeat-Fault Detection | no button (correct); same explanation |
| 7 | Warranty Projection | unchanged |
| 8 | Corporate Estates | + New Estate; chips **Corporate Estate** (the master) and **Estate Assignment** (pick a device, choose the estate; the server refuses a device the client does not own); Asset Register added |
| 9 | Bulk Registration | **+ New Bulk Estate Upload**; Bulk Registrations list (Validate Again, Commit as a Set) and Bulk Registration Lines (the per-line reject report); the readiness report is kept as "Bulk Readiness" |
| 10 | Condition & EOL Routing | + New Condition Grading; chips Condition Grading, **PM Plan**; Asset Register added (lifecycle and scrap actions) |
| 11 | Data Quality | + New Identity Resolution; chip Identity Resolution; Merge Lineage and Alerts added |

Every system-written list now says where its rows come from: history, ownership, holds, merges, identifier history, bulk lines and alerts.

### 4.2 The bulk loader (new): `cd_device_registry/models/fix_device_bulk.py`

`fix.device.bulk.load` + `fix.device.bulk.line`. ACLs, company record rules and the `DBULK/%(year)s/` sequence were added.

- **Upload:** a CSV or Excel file against a corporate estate. The header names Model (catalogue name or model code) and Serial and/or IMEI 1. IMEI 2, MAC, Legacy Reference and Purchase Date are optional. Excel's numeric IMEIs are read back whole.
- **Validation** runs at upload and again with "Validate Again". Each row is checked against:
  - the M37 catalogue: unknown or ambiguous models are rejected (BRU-AST-12);
  - the other rows of the same file: a duplicate serial or IMEI is rejected, even with a case or spacing variant;
  - the registry: a device already registered to the client joins the estate; one registered to someone else is rejected ("ownership transfer first");
  - the rules a single registration meets: every new row is really registered inside a savepoint that is always rolled back, so the reject report names exactly what the commit would refuse. Nothing is registered and no event is published by a validation.
- **Commit as a Set** (Device Registry Agent): every row is registered or placed, or none is (BRU-AST-18). A row that started to fail after validation refuses the whole batch and names the row. A committed load cannot be edited or deleted, and its state is guarded.
- Devices are registered to the estate's client, in the estate, at the chosen branch.

**Decision taken without the owner:** the spec gives bulk load to R22 Account Manager, a role that does not exist in the estate. The commit is gated on the existing Device Registry Agent role, the closest registry role.

### 4.3 Other code

- `fix_device.py` `action_transfer_ownership` also accepts `evidence_file` / `evidence_filename`, filed on the device exactly as the asset form's upload is. This lets the Ownership Transfer form upload and transfer in one step.
- `controllers/a07/m17.py`: surfaces for the two new models (actions `action_validate`, `action_commit`).
- `controllers/a07/writable.py`: regenerated with `form_fields.py --a07`. The only content change is the two new models; other entries were re-sorted.
- `cd_device_registry/tests/test_a07_m17_operability.py` test_15 was already stale at HEAD: it expected the chip to open the Asset Register. It now asserts that the chip runs the governed transfer.

## 5. Tests

| File | What it proves |
|---|---|
| `cd_p03_portal/tests/test_m17_submodule_capture.py` | The engine's own page logic over the real registry: all 11 pages classified; every capture page offers a working form, and the 2 system pages offer none; no orphan screen; system lists explain themselves; the specific chips of pages 2, 3, 8, 9 and 10 |
| `cd_device_registry/tests/test_m17_capture_live.py` | Through the workspace endpoints as NON-ADMIN users: a file with 6 kinds of bad row is rejected line by line, and its validation registers and publishes nothing; a clean file commits only for the agent; devices land with the client, the estate and the purchase date; the commit is all or nothing; Excel IMEIs stay whole; a missing Model column is refused; a replaced file re-validates; the state is not typeable; the transfer form uploads evidence and transfers; the lost form flags; estate placement refuses a device the client does not own |

## 6. Not built (spec gaps that need a model or an owner decision, not a button)

- FR-AST-012 actual configuration history, FR-AST-014 asset relationships, FR-AST-015 accessory register (only custody reconciliation flags exist), FR-AST-021 location history, FR-AST-022 population classification.
- FR-AST-038 estate **nodes** (site → department → user as records with dated placements). Today an estate is one record with site and department text.
- FR-AST-040 estate reconciliation (gap, stray and movement lists), FR-AST-041 corporate-portal estate self-service.
- FR-AST-008 QR asset labels.
- R22 Account Manager role (see §4.2).

## 7. Results and deployment

**Test runs (13 Nov 2026):**
- **Portal guards (file-only):** 643 passed, 0 failed. This covers `test_m17_submodule_capture.py`, the 67-module page standard, the A07 write whitelist and the A07 form engine.
- **Live endpoints:** 96 passed, 0 failed, on a private copy of `fix_test` (`fix_test_m17cap`, upgraded with `-u cd_device_registry`). This covers `test_m17_capture_live.py` (12 new), `test_a07_m17_operability.py`, `test_a07_p1_controls.py` and `test_device_registry.py`.
- **A defect the live tests caught:** the loader's row method was first named `_register`, which is a reserved Odoo model attribute (a boolean). Every valid row was rejected with "'bool' object is not callable". It was renamed to `_register_row`.

**Live on 8069 (fix_real), browser sweep under `?debug=assets`:**

| # | Button | Chips |
|---|---|---|
| 1 | + Asset | Asset (5 identifiers) |
| 2 | + New Installed Component | Installed Component, Part Compatibility |
| 3 | + New Custody Event | Ownership Transfer, Custody Event, Report Lost / Stolen |
| 4, 6 | no button | "No data-entry form: these records are not typed in here." |
| 5 | + New Installed Component | Installed Component |
| 7 | + New Device Warranty | Device Warranty |
| 8 | + New Corporate Estate (after the retitle) | Corporate Estate, Estate Assignment |
| 9 | + New Bulk Estate Upload | Bulk Estate Upload |
| 10 | + New Condition Grading | Condition Grading, PM Plan |
| 11 | + New Identity Resolution | Identity Resolution |

The Ownership Transfer chip opened its step 1 (pick the device) correctly.

**Not yet live: needs `-u cd_device_registry` on fix_real and a restart of 8069/8089 (owner's approval).** 8069 was restarted at 01:41 after the new model file existed, but the module was not upgraded. The bulk tables and access rights therefore do not exist on fix_real, and page 9's lists answer "You are not allowed to access fix.device.bulk.load" until the upgrade runs.

**Blockers found on the way (not M17):**
- At 02:00 another session upgraded `cryptography` to 50.0.2 in the shared `.venv`. Odoo pins 42.0.8 with pyOpenSSL 24.1.0, so **any Odoo process now fails at import** (`module 'lib' has no attribute 'GEN_EMAIL'`). A restart of 8069 would leave it down. The tests here ran with a private overlay of 42.0.8 (`PYTHONPATH`); the shared venv was not touched.
- From about 00:57 to 01:26, Postgres was in crash recovery: a 22-minute fsync of the data directory, then 10 s of WAL redo. The cause is not in its log.
- A peer's pre-commit stash hid this work for 70 s (02:04:15 to 02:05:25). Nothing was lost.

**Update 02:06:** the venv is back on `cryptography` 42.0.8 (restored by another session), so this blocker is gone.

**Deploy rehearsal on a copy of fix_real (02:25–02:40), dropped afterwards:**
- **Upgrade.** `-u cd_device_registry` exited 0 with no ERROR or CRITICAL lines. It created both tables, 3 access rules and the DBULK sequence.
- **Setup.** A private server ran on port 8099 against the copy. A catalogue device model had to be seeded first, because fix_real has none.
- **Bad file.** An estate was created for a real client, and a 5-row file was uploaded. Bulk Registration Lines in the workspace showed 2 rows "Will Be Registered" and 3 "Rejected": unknown model, "Serial Number rh-sn-0001 is also on row 2", and "IMEI must be exactly 15 digits".
- **Corrected file.** Re-uploading a corrected file re-validated it clean: 3 new rows, 0 rejected.
- **Commit.** "Commit as a Set" was pressed in the workspace. The database showed the load committed, and 3 devices registered to the client, in the estate, with the purchase date. The list moved the load to "Committed".
- **Generic engine issue, not M17.** An already-open record tab kept showing "Validated" after the action and Refresh. The list showed the truth.

**Live deployment (user approved, 13 Nov ~02:50):**
- **Backup.** `_migration/backups/fix_real_pre_m17_bulk_2026-11-13.dump` (47.9 MB).
- **Upgrade.** `-u cd_device_registry` on fix_real exited 0 with no ERROR or CRITICAL lines. The tables, the 3 access rules and the sequence exist, and the module is `installed`.
- **No restart was needed.** 8069 and 8089 had been restarted by another session at 02:49:56, after this code was on disk. They picked up the schema through registry signalling: `/p03/model/records` for both bulk models answers on 8069 and 8089 (0 rows) instead of "not allowed".
- **Browser check on 8069.** Bulk Registration loads with "No records yet.", and + New Bulk Estate Upload opens the form.
- **Fix after deploy.** That check found the engine's default file picker accepts only `.pdf,.jpg,.jpeg,.png,.doc,.docx`, which hides an estate file. The form now sets `accept: '.csv,.xlsx'`, and a guard test was added. It was verified from disk under `?debug=assets`. **Verified live 03:10:** after the coordinated restart (8069 back at 03:09:14), the production bundle `477d90e` (not debug) renders the Bulk Estate Upload file input with `accept=".csv,.xlsx"`, and the bulk surface answers.

**Data note:** fix_real holds 0 devices, 0 estates and **0 catalogue device models** (M37). Until device models are loaded, every bulk-upload row will be rejected as "not in the device catalogue", correctly.

**Committed** as 472ee6c6 on fix/a03-live-data-and-pending-work (13 files, all hooks passed); not pushed.
