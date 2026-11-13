# M13 Rental & EaaS — sub-module data-capture audit (13 Nov 2026)

**Report:** "not all the sub-modules have a relevant data capture button".
**Scope:** the 9 Function Register sub-module pages of the M13 workspace
(`cd_p03_portal/static/src/a05/m13.js`). Each page was checked against the
module specification (`1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M13_Rental_and_Equipment_as_a_Service.md`,
FR-RNT-001…044, BRU-RNT-01…22) and against the server rules in
`cd_rental_asset`.

## How it was measured

- **Page rule:** the engine's own `fregCreate` (in `p03_workspace.js`) was
  executed in node over the real registry. It returns the button each page
  shows. This is the method the M02 and M06 audits used.
- **Server:** every form a page offers was checked against the model's
  `create` and `write` guards. A button the server refuses counts as a
  defect, not as a capture.
- **Live data:** `fix_real` (the database 8069 serves) has **0 rows in every
  M13 table**, and **0 rental SKUs**. The live pages are empty whatever they
  offer.

## Findings (before)

| # | Sub-module | What the page offered | Verdict |
|---|---|---|---|
| 1 | Fleet Register | + New Fleet Serialized Asset Master; Kit as a chip | OK, but a fleet unit **requires** a rental SKU, and fix_real has none. No page offered the M37 SKU form. |
| 2 | Availability & Reservation | + New Reservation (module button) | OK |
| 3 | Agreements | + New Reservation again; the agreement chip opened a **blank** form | **Wrong capture.** The chip made a second, empty booking with no SKU or unit, instead of preparing the agreement on an existing booking. |
| 4 | Deposits & Waivers | nothing (`create: false`, no forms) | **Missing.** See also defect D1. |
| 5 | Condition & Damage | + New Condition Inspection Report | OK, but its booking picker listed every rental, and the server refuses a report outside its stage. |
| 6 | Returns & Recovery | page 5's damage form again | **Missing.** Nothing recorded the return itself, and the damage picker was also unfiltered. |
| 7 | In-Rental Support | nothing | **Missing.** The backend had no fault-report path at all (FR-RNT-027). |
| 8 | Turnaround & PM | + New Turnaround & Regrading Dossier | **Dead button.** `fix.rental.turnaround.create` refuses any typed turnaround ("opened by the rental return … not typed"). |
| 9 | Analytics | nothing | Correct: utilisation and fleet-health figures are computed. |

### Defects found on the way

- **D1 — every deposit was booked as cash.** `action_reserve` called the
  ledger's `_post` without a tender, so `method` was always `cash`. The
  tender decides the GL clearing account (`rental_gl.tender_account`) and the
  M50 refund method. So a bKash deposit was posted to the cash account and
  refunded as cash. Refunds, deductions and forfeits were also hard-coded to
  cash.
- **D2 — fields the model holds were never captured.**
  - Condition report: body condition, charge cycles, maintenance-required.
  - Turnaround: sensors, connectors, firmware, memory card, storage reset,
    functional score, battery after PM.
  - Damage: discovered-on date, repair hours.

## What was changed

### Workspace (`static/src/a05/m13.js`)

This file is served from disk, so the change is live on 8069 now.

| # | Page now offers | Chips on the page |
|---|---|---|
| 1 | + New Fleet Serialized Asset Master | Rental Kit Bundle, **Rental SKU (M37)** |
| 2 | + New Reservation | Reservation Cockpit |
| 3 | **Prepare a Rental Agreement**: pick a draft or declined agreement on a draft or reserved booking, then fill in its terms | Rental Agreement (e-sign) |
| 4 | **Take a Security Deposit**: pick a draft booking, choose the tender and enter its reference, then `action_reserve` | **Loss Waiver Request**: pick a damage line with an unrecovered loss, write the justification, then the routed M63 request |
| 5 | + New Condition Inspection Report (picker limited to rentals at an inspection stage; 3 more checks) | Damage Assessment & Recovery (picker limited to returned rentals; 2 more fields) |
| 6 | **Record a Rental Return**: pick an active rental, then `action_return` | Damage Assessment & Recovery |
| 7 | **Report a Fault on a Live Rental**: pick a delivered or active rental, then describe the fault | **Book a Return Collection (M03)** |
| 8 | **Record a Turnaround Checklist**: pick an open turnaround, then the full checklist. The list no longer offers the refused "+ New". | **Send a Unit to Preventive Maintenance** |
| 9 | (none, computed) | — |

### Server (live on 8069/8089 since the 02:10 relaunch, 13 Nov; no `-u`, no schema change)

- **`cd_rental_asset/models/fix_rental_asset.py`**
  - `action_reserve(method=None, reference=None)` takes the tender (cash,
    bKash, Nagad, card or bank) and its reference. A non-cash deposit needs a
    reference, and an unknown tender is refused. With no tender it is cash, as
    before, so the list's Reserve button is unchanged.
  - New `action_report_fault(fault)` for a delivered or active rental. It
    writes the fault to the rental's history (who reported it and when) and
    creates a to-do for the person who booked the rental. The deadline is the
    swap SLA (`cd_rental_asset.swap_sla_hours`, default 24 h). The swap itself
    is still not modelled.
  - Three non-stored input fields carry what the step forms type:
    `deposit_method`, `deposit_reference` and `fault_report`.
- **`cd_rental_asset/models/fix_rental_fleet.py`:** `_post` takes a
  reference. A refund, deduction or forfeit now follows the tender the
  deposit was collected in.
- **`controllers/a05/m13.py`:** `action_report_fault` is on the reservation
  surface.
- **`controllers/a05/writable.py`:** regenerated
  (`form_fields.py --a05`) for the D2 fields.

**Until the restart:**
- The Report a Fault step is refused ("not allowed").
- Ticking a new checklist box on an existing turnaround is refused with a
  clear "not editable on this screen".
- On a *new* condition report, the three new checks are dropped.
- Taking a deposit works, but it is posted as cash.

fix_real has no M13 rows, so nobody can reach these paths today.

### Guard test

`cd_p03_portal/tests/test_m13_submodule_capture.py`:
- The page rule is executed over the real registry, with the expected
  button for each of the 9 pages.
- Every chip resolves to a form.
- No page offers a create the server refuses.
- Every form field, picker column and filter exists, and every `saveAction`
  method is on its surface.
- Each new step's legitimate path runs as a non-admin clerk through
  `/p03/model/action` and `/p03/model/write`. It reuses the fixtures of
  `cd_rental_asset/tests/test_a05_m13_controls.py`.

## Verification (13 Nov, on `fix_test`; rollback, no data left behind)

- `test_m13_submodule_capture.py`: **22 passed**.
  - The bKash branch was confirmed live: the deposit was posted to the GL
    as bKash, and its cancellation refund was queued to M50 as bKash.
  - The waiver request was routed successfully.
- Regression: `cd_rental_asset/tests` (5 files) plus
  `test_a05_control_suite.py`. **159 passed, 6 skipped, 0 failed.** The skips
  are by design: those models carry no workflow fields.
- Estate page standard (`test_estate_module_pages.py`, all 67 modules):
  **605 passed**.
- `ruff format` and `ruff check` are clean (local 0.17.1; the pre-commit pin
  is 0.8.4).
- **Not done:** a live click-through on 8069. The browser pane needed a
  sign-in on a real-data database.
- **Incident:** while a private test database was being cloned, the shared
  Postgres container crashed. Several sessions were restoring clones at the
  same time. It ran crash recovery for about 13 minutes, then accepted
  connections again, and 8069 answered 200.

**Live check (13 Nov, 8069, read-only):**
- `/p03/model/action` on `fix.rental.reservation`:
  - `action_report_fault` gets "Record not found".
  - An unlisted method gets "Action not available for this surface".
  - So the restarted server carries the new whitelist.
- `/p03/model/form` returns the new `deposit_method` and `fault_report`
  fields, so the model change is loaded.
- Vendor bills read cleanly. The AP session upgraded `cd_ap_ext` on fix_real
  at 02:45, after the relaunch.

## Still open (not built here)

| Spec item | Gap |
|---|---|
| FR-RNT-016 extension, FR-RNT-033 variation | No extension or variation path. `date_to` is an agreement term frozen at sending, and a variation needs re-signature. |
| FR-RNT-027 swap-out | Only the fault report exists. There is no swap record, and no paired condition reports for the outgoing and incoming units. |
| FR-RNT-025 loss / non-return | No loss record, escalation stage, police report or insurance claim (`fix.rental.loss` in spec §10 does not exist). |
| FR-RNT-036 damage-waiver product | No elective waiver line on the agreement. "Waivers" today are loss write-offs only. |
| FR-RNT-021/023 photographs | `photos_ref` is a text link. There are no hashed, immutable photos (T-04) and no side-by-side outbound-vs-inbound comparison. |
| Upstream data | fix_real has 0 rental SKUs, so no fleet unit can be registered until M37 creates them (now reachable from page 1). |
