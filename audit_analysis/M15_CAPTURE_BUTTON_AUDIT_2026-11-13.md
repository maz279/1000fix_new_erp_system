# M15 Spare Parts & Inventory: data-capture button audit

**Date:** 13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** JS-only fix on disk (no server restart needed), guard test added, nothing committed

## 1. The question

The M15 workspace has 13 sub-module pages (Function Register, 107 functions). Not all of them showed a button to record data. Which pages should have one, and what should it open?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md` (FR-INV-001…054, §10 entities, §13 roles and SoD)
- the models in `addons/domain/e_supply_chain/cd_inventory/models/` (what the server lets a person create)

The rule used (the same as the M02, M09 and M10 audits): a record a person enters gets a "+ New" or a form chip. A record that only a workflow writes, or that is calculated, gets no button, and its list says where its rows come from. Typing a ledger figure in would bypass the movement controls (FR-INV-005, FR-INV-008).

| # | Sub-module | Spec | What a person records |
|---|---|---|---|
| 1 | On-Hand & Classes | FR-INV-001, 003, 005 | nothing: the position moves only by receipts, issues, transfers, counts, quarantine, scrap and RTV |
| 2 | Location Hierarchy | FR-INV-002, 028 | **a stock location**: store, van (with its custodian technician), workbench, quarantine, scrap |
| 3 | Ownership Segregation | FR-INV-010…018 | **an ownership-class change**: named, approved, reason-coded (FR-INV-018, BRU-INV-06) |
| 4 | Reservations | FR-INV-019…021 | nothing: written by M41 wave release |
| 5 | Issue / Return / Consumption | FR-INV-022, 023 | a stock issue; a return is a list action |
| 6 | Van Stock | FR-INV-028…032 | a shift-end van reconciliation; **van par levels** (FR-INV-029) |
| 7 | Serial & Lot Trace | FR-INV-035…040 | nothing: a serial is recorded by its goods receipt and then follows the ledger |
| 8 | Valuation | FR-INV-041…046 | nothing: weighted average from the movements |
| 9 | Goods Receipt | FR-INV-005 / M16 | a goods receipt with the inspection gate |
| 10 | Counting | FR-INV-047…051 | a cycle or full count |
| 11 | Ageing & Analysis | FR-INV-045, ABC/XYZ | nothing: calculated |
| 12 | Transfers & RTV | FR-INV-052, 054 | a transfer request; a quarantine/scrap order; **a return to vendor** |
| 13 | Item Master | R4 real inventory | the 7-tab item master |

## 3. What the code had (before)

Evaluated with the workspace engine's own `fregCreate` / `fregPanels` over the real registry (the new guard test fails 10 of 21 checks on the old code).

| # | Page | Button before | Defect |
|---|---|---|---|
| 1 | On-Hand & Classes | none | Correct. |
| 2 | Location Hierarchy | **none** | No way to add a store, van or quarantine location, although M41 has the location form and a storekeeper may create one. No list of locations on the page. |
| 3 | Ownership Segregation | **none** | The class-change document (list and form) existed but **sat on no page**, so the only lawful way to change a class could not be reached from the register. |
| 4 | Reservations | none | Correct (M41 wave release reserves). |
| 5 | Issue / Return | + New Stock Issue | Correct. |
| 6 | Van Stock | + New Van Reconciliation | No chip for the reorder rule, so van par levels (FR-INV-029) could not be set from the page. The Replenishment list had a "+ New", but only one click deeper. |
| 7 | Serial & Lot Trace | **+ New Serial / Lot** | **Dead button.** Every required field of a lot (serial, part, location, quantity, status) is guarded, and no store role holds create rights. A blank lot form could never save. |
| 8 | Valuation | none | Correct, but the Valuation Suspense Integrity check sat on no page. |
| 9 | Goods Receipt | + New Goods Receipt | Correct. |
| 10 | Counting | + New Cycle Count | Correct. |
| 11 | Ageing & Analysis | none | Correct. |
| 12 | Transfers & RTV | + New Transfer Request; Scrap Order chip | **No Return to Vendor chip**, although the page is "Transfers & RTV" and the RTV form exists. |
| 13 | Item Master | + New Inventory Item Master | Correct. |

## 4. What was changed

| # | Page | Capture now |
|---|---|---|
| 2 | Location Hierarchy | **+ New Stock Location** and a **Stock Location** chip (M41's location form, the one location master); new **Stock Locations** list (Activate / Deactivate) in the Stock Ledger group |
| 3 | Ownership Segregation | **+ New Ownership-Class Change** and its chip; the class-change list (Submit / Approve & Apply / Reject) is on the page |
| 6 | Van Stock | adds a **Reorder Rule** chip next to + New Van Reconciliation |
| 7 | Serial & Lot Trace | no button; the list says serials come from posted goods receipts; the lot form opens existing records only |
| 8 | Valuation | the Valuation Suspense Integrity check is on the page |
| 12 | Transfers & RTV | adds a **Return to Vendor** chip |

No server change was needed. All four reused forms were already in the A06 write whitelist (`controllers/a06/writable.py`), and no form field was added.

### Files

- `addons/platform/cd_p03_portal/static/src/a06/m15.js`
- `addons/platform/cd_p03_portal/tests/test_m15_submodule_capture.py` (new, 21 tests; 10 fail on the old code)

### Tests run

- `test_m15_submodule_capture.py` 21/21
- `test_estate_module_pages.py` (all 67 modules) green
- `test_all_submodule_mapping.py`, `test_screens_wiring.py`, `test_submodule_create_button.py`, `test_a06_write_whitelist.py` green; the ORM-bound checks skipped because Postgres was in crash recovery at the time (see §6)

## 5. Spec gaps that need a build, not a button

These are in the spec but have no model, so no page can capture them. Each needs an owner decision:

- **Reservation as a record** (`fix.stock.reservation`, FR-INV-019…021, 027): today a reservation is a number on the on-hand row, set only by M41 wave release. There is no automatic reservation from a service-order parts requisition, no priority, no expiry, and no emergency override with a reason.
- **Per-brand consignment ledger and monthly reconciliation** (FR-INV-012, 014; `fix.consignment.balance` / `.reconciliation`).
- **Harvest and core capture** (FR-INV-053): a part recovered from a scrapped device as refurbished stock.
- **Backorder** (FR-INV-025) and **kit issue** (FR-INV-026).
- **Van-to-van transfer** with dual scan (FR-INV-033).
- **Obsolescence provision** (FR-INV-045) is reported but not raised to M19.

## 6. Live check (8069 = fix_real, `?debug=assets`, 13 Nov)

Click sweep of all 13 pages in the real workspace:

| # | Page | "+ New" | Form chips |
|---|---|---|---|
| 1 | On-Hand & Classes | none | none |
| 2 | Location Hierarchy | + New Stock Location | Stock Location |
| 3 | Ownership Segregation | + New Ownership-Class Change | Ownership-Class Change |
| 4 | Reservations | none | none |
| 5 | Issue / Return / Consumption | + New Stock Issue | Stock Issue |
| 6 | Van Stock | + New Van Reconciliation | Reorder Rule |
| 7 | Serial & Lot Trace | none | none |
| 8 | Valuation | none | none |
| 9 | Goods Receipt | + Goods Receipt | Goods Receipt (inspection gate) |
| 10 | Counting | + New Cycle Count | Cycle Count |
| 11 | Ageing & Analysis | none | none |
| 12 | Transfers & RTV | + New Transfer Request | Transfer Request, Scrap Order, Return to Vendor |
| 13 | Item Master | + New Inventory Item Master | Item Master (7 tabs) |

- Each new chip (Stock Location, Ownership-Class Change, Reorder Rule, Return to Vendor) opens its form with inputs and a Save button, and no load error.
- The server serves every new list: fix_real has 197 stock locations and 17,461 on-hand rows. It has 0 class changes, 0 reorder rules, 0 RTVs and 0 lots.
- The Serial & Lot list shows its explanation and no "+ New".
- No record was saved on fix_real: it is the real estate.

**Not yet live for normal users.** The production bundle on 8069 (`bb2bba0`) predates the edit. Odoo did not rebuild it on file change this time. Users get the change at the next 8069 restart. Until then it shows only under `?debug=assets`.

During the work, the shared Postgres container (`compose-postgres-1`) went into crash recovery at about 17:02 UTC on 12 Nov (23:02 Dhaka time). It was fsyncing the whole data directory, so every server and test lost the database for several minutes. I did not cause it and did not intervene. It recovers on its own.
