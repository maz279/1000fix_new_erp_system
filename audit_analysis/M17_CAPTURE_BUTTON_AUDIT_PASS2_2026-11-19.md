# M17 Device & Asset Registry: capture audit, pass 2

**Date:** 19 Nov 2026 · **Estate:** fix_real on 8069, fix_dev on 8090 · **Status:** LIVE on 8069 and 8090 (landed 4d8e44cf, pushed)

## 1. The question

The user again saw M17 sub-module pages without a relevant data-capture button. The 13 Nov pass (`M17_CAPTURE_BUTTON_AUDIT_2026-11-13.md`) gave every page that should capture a "+ New" or a chip. This pass asks a stricter question: does each page capture **the record the spec places on it**, or only some record?

## 2. Method

1. Read the spec, `1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M17_Device_and_Customer_Asset_Registry.md`: FR-AST-001…052 (§5), BRU-AST-01…23 (§9) and the owned entities (§10.1).
2. Mapped each FR to its Function Register page (the `freg.sub` mapping in `m17.js`).
3. For each page, listed what the workspace could capture (its "+ New" and chips, evaluated with the engine's own `fregCreate` / `fregPanels`) and what the models in `cd_device_registry` could hold.
4. A page fails when the spec names a record a person records there and no form, or no model, exists for it.

## 3. Findings

| # | Page | Spec record a person records there | Before (19 Nov) | Verdict |
|---|---|---|---|---|
| 1 | Identity & Resolution | FR-AST-008 QR asset tag, re-label keeps the old tag, technician and date (P1). FR-AST-002 any number of typed identifiers: brand service tag, customer asset number, part number (P0). FR-AST-010 the same identifier on two assets is quarantined (P1) | Asset form with 5 fixed identifier fields. No label model. The identifier register held only serial, IMEI 1 and IMEI 2 | **Gap**: no label, no further identifier |
| 2 | Configuration & Components | FR-AST-015 accessory register, a checklist reconciled at return (**P0**, gate of BRU-AST-08). FR-AST-012 actual configuration with history (P1) | Component and compatibility forms. The release gate was a tick box, "Accessories Reconciled", with nothing to reconcile against | **Gap**: P0 register missing |
| 3 | Ownership & Custody | FR-AST-022 exactly one population per asset (**P0**). BRU-AST-10 a population change is reason-coded. BRU-AST-11 rental or refurbishment stock becomes customer-owned only with an ownership transfer | Custody, transfer and lost/stolen forms. No population field anywhere on the device | **Gap**: P0 field and transaction missing |
| 4 | Service History | nothing (projected) | no button | correct |
| 5 | Parts Genealogy | the fitted component | Installed Component | correct |
| 6 | Repeat-Fault Detection | nothing (computed) | no button | correct |
| 7 | Warranty Projection | BRU-AST-16 (**H**): warranty dates recorded with their derivation basis; a defaulted date is flagged and cannot alone support a claim | Device Warranty form with no basis. A date defaulted from manufacture could be verified as fully as one from a receipt | **Gap**: hard rule unenforceable |
| 8 | Corporate Estates | FR-AST-038 customer → site → department → assigned user, each asset at exactly one node, moves recorded with effective dates (**P0**) | One estate record with free-text site and department. "Estate Assignment" wrote the device's estate field with no node, date or reason, and kept no history | **Gap**: P0 structure missing |
| 9 | Bulk Registration | the estate file | Bulk Estate Upload | correct |
| 10 | Condition & EOL Routing | FR-AST-048 end-of-life decision: route to M14, M18 or return to the customer, with decision, approver and basis. BRU-AST-19 (**H**) needs the customer's instruction | Condition and PM forms. End of life was a lifecycle button on the asset list, with no route, no approver of the route, and no hand-on to M14 or M18 | **Gap**: no decision record |
| 11 | Data Quality | FR-AST-051 stewardship worklist: provisional identities, duplicates, conflicts and low-quality records, assigned by branch, with ageing and escalation. BRU-AST-22: an ageing provisional identity escalates | Identity Resolution (duplicates only) and the alerts list | **Gap**: no worklist |

In total, 7 of 11 pages could not capture a record the spec places on them. Three of those records are P0 (accessories, population, estate structure) and two are hard rules (BRU-AST-16, BRU-AST-19).

## 4. What was built

### 4.1 Models: `cd_device_registry` 19.0.1.2.0, `models/fix_device_capture.py` (imported last)

| Page | Model / change | Rules enforced on the server |
|---|---|---|
| 1 | `fix.device.label` (`FXT-` codes) and `fix.device.asset_tag` | A device that already carries a label takes a new one only with a reason. The old label becomes Replaced and its identifier row is superseded, not deleted. The tag code finds the device like a serial does. A label cannot be dated in the future, edited or deleted |
| 1 | `fix.device.identifier` types: asset tag, brand service tag, customer asset number, part number; `fix.device.action_add_identifier` | The value is normalised for case and spacing. The same value twice on one device is refused. The same value of the same type on another active device is recorded, and both devices get a high-severity "identifier conflict" issue on the worklist (BRU-AST-05, FR-AST-010) |
| 2 | `fix.device.accessory` (held, returned, missing at return) | **BRU-AST-08:** "Issued to Customer" is refused while any accessory of the device is still held. Missing at return needs a reason. What was received is never rewritten. Its state is guarded |
| 2 | `fix.device.configuration` | A new value of an attribute closes the current one on the same date. A backdated value is refused. Rows are permanent. Installed options may run in parallel |
| 3 | `fix.device.population` (guarded, default customer-owned) and `fix.device.population.change` | Only the Device Registry Agent changes a population, with a reason code. **BRU-AST-11:** from rental pool or refurbishment stock to customer-owned needs an ownership transfer of this device. The transfer may not predate the last change, and it supports one change only |
| 7 | `fix.warranty.derivation_basis` and `basis_flag` | **BRU-AST-16:** verification is refused while the basis is "default from date of manufacture". The verification blocker says so. The form requires a basis |
| 8 | `fix.device.estate.node` (site / department / user) and `fix.device.estate.placement`; `fix.device.estate_node_id` (guarded) | The hierarchy is enforced: a site has no parent, a department sits in a site, and a user sits in a department or site and names a contact of the client. A placement needs the client's own device, and a node when the estate is organised. Each move closes the previous placement on the same date and is never backdated before it. An estate set or cleared on the asset (form, bulk load, transfer out) is written to the same placement history |
| 10 | `fix.device.eol.decision` (draft → requested → approved / rejected) | **BRU-AST-19:** a customer-owned device needs the customer's instruction, and it must match the route. One open decision per device. Approval needs a Branch Manager who neither raised nor requested it. On approval the device becomes obsolete and the decision is recorded on it. A disposal route moves the device to e-waste pending (M18). Refurbishment moves it to refurbishment stock, or to trade-in intake when customer-owned (M14). Both go through a reason-coded population change |
| 11 | `fix.device.quality.issue` and the daily cron `cron_steward_sweep` | Worked by the assignee or a Branch Manager. Resolving needs a resolution, and a provisional-identity issue cannot resolve while the device is still provisional. **BRU-AST-22:** the sweep lists provisional devices older than 7 days (once) and escalates issues open more than 14 days. Both thresholds are parameters |

Satellite record rules follow the device's company and operating unit; estate nodes follow the estate's company. Six sequences. No new bus events: outcomes go to the device's chatter and history.

### 4.2 Workspace: `cd_p03_portal/static/src/a07/m17.js`

| # | Page now offers |
|---|---|
| 1 | + Asset; chips **Asset Label**, **Add Identifier** (pick the device, type and value); list Asset Labels |
| 2 | + Installed Component; chips Part Compatibility, **Accessory Received**, **Configuration Record**; lists Accessory Register (Handed Back / Missing at Return), Actual Configuration |
| 3 | + Custody Event; chips Ownership Transfer, Report Lost / Stolen, **Population Change**; list Population Changes |
| 7 | the Device Warranty form asks "Dates Derived From"; the list shows the basis |
| 8 | + Corporate Estate; chips **Estate Node**, **Estate Assignment** (now a dated placement at a node, replacing the device-pick form); lists Estate Sites/Departments/Users, Estate Placements & Moves |
| 10 | chips Condition Grading, PM Plan, **End-of-Life Decision**; list End-of-Life Decisions (Request / Approve / Reject) |
| 11 | chips Identity Resolution, **Stewardship Issue**; list Stewardship Worklist (Start Work / Resolve) |

The asset register shows the asset tag and population; the asset form shows the tag, the estate node and the population (read-only).

Controllers: 8 surfaces in `controllers/a07/m17.py` and the `action_add_identifier` action. The `a07/writable.py` and `a02/writable.py` files were regenerated with `form_fields.py`; the only content changes are the new models and `fix.warranty.derivation_basis`.

## 5. Tests

| File | What it proves |
|---|---|
| `cd_p03_portal/tests/test_m17_capture_pass2.py` | Using the engine's own page logic: each of pages 1, 2, 3, 7, 8, 10 and 11 offers a form for every record the spec places there; the new lists are on their pages; the old device-pick placement form is gone; every new model is served, whitelisted and has its list actions allowed |
| `cd_device_registry/tests/test_m17_capture_pass2_live.py` | Through the workspace endpoints as non-admin users: label issue, re-label and tag search; identifier conflict; the accessory release gate; configuration history; population with BRU-AST-11; defaulted warranty basis refused; the estate node tree; placement moves and history; end-of-life with instruction and SoD; worklist SoD; sweep idempotence and escalation; no new form omits a required field |
| `cd_p03_portal/tests/test_m17_submodule_capture.py` | Updated: Estate Assignment now opens the placement record |

## 6. Not built (needs an owner decision or another module)

- FR-AST-014 asset relationships (parent/child, accessory-of) and FR-AST-021 location history at van or site granularity. Custody events carry no location yet.
- FR-AST-040 estate reconciliation (gap, stray and movement lists) and FR-AST-041 corporate-portal self-service.
- Printing the QR label. The code is issued and searchable; the print template is not built.
- Thresholds that need owner confirmation: provisional ageing at 7 days and escalation at 14 days (`cd_device_registry.steward_*_days`).
- BRU-AST-19 approver: the spec names the Workshop Supervisor, a role the registry does not have, so the Device Registry Branch Manager decides.

## 7. Results and deployment

**Tests (19 Nov 2026), on a private copy of the test template (`fix_test_m17c2`, upgraded with `-u cd_device_registry,cd_p03_portal`, exit 0):**
- **Regression: 833 passed, 0 failed.** This covers the whole `cd_device_registry` suite (A02/A07 controls, operability, the 13 Nov capture tests and the new live tests), the M17 page guards, the A07 form engine and write whitelist, the 67-module page standard and the picker standard.
- **Pass 2 alone: 53 passed** (17 live, 36 static including the 13 Nov page guard).
- **Mutations: 22 of 23 red.** Each server rule, and three page mappings, was broken in turn. The survivor drops the Device Registry Agent check on a population change; the access rights still refuse a clerk, so it is an equivalent mutant. The first run had two more survivors (a blank "missing" reason; a user node without a contact). The tests were strengthened and both now go red.
- **Defects the live tests caught:**
  - A transfer recorded in the same transaction as a population change read as "earlier", because a Python clock was compared with a transaction timestamp. The check now compares transaction timestamps.
  - Configuration rows displayed as `model,id`; they now show "device · attribute: value".

**Live walk on a private server (port 8097, the branch's code, headless Chromium):** all 11 pages render. Each page shows its "+ New", every chip opens its form with inputs, and the console logged 0 errors. Through the same endpoints the forms use, an accessory, a configuration, an identifier, a stewardship issue and an end-of-life decision were saved, and all 8 new models are served.

**Test-template note:** every peer template (`fix_test_m1xc2`) lacks some foreign keys and carries orphans: 3 part-compatibility rows on a deleted model, and 11 columns referencing a deleted entity. They were repaired in the private copy only. `fix_dev` has the same 3 orphan part-compatibility rows, but its foreign key exists, so an upgrade there is not blocked. Clean-up is for the owner.

**Landed and pushed:** 4d8e44cf on fix/a03-live-data-and-pending-work (`422b005b..4d8e44cf`), and branch `fix/m17-capture-pass2`.

**Deployed 19 Nov (the user approved "deploy all 7 together"):**
- The upgrade was combined with the other modules waiting on both databases: cd_hr_core (M21), cd_marketplace (M12), cd_tradein (M14), cd_inventory (M15), cd_requisition (M16), cd_billing_engine, cd_ewaste and cd_rental_asset, plus cd_p03_portal.
- The M21 session ran it as one combined `-u` per database, with backups first, then a single restart at 08:06.
- 8069 = PID 81988 (fix_real) and 8090 = PID 21792 (fix_dev). No module was behind on either database before the restart.

**Read-only verification on both databases:**
- `cd_device_registry` 19.0.1.2.0.
- 8 tables, 10 access rights and 8 record rules, 6 sequences, and the stewardship sweep active.
- `population`, `estate_node_id` and `asset_tag` on the device; `derivation_basis` on the warranty.
- Each database's newest web bundle carries the new forms.

**Live walk on 8069 (fix_real), headless and read-only:**
- All 11 pages render. Each page offers the "+ New" and chips listed in §4.2, and every chip opens its form with inputs.
- All 8 new models are served. They hold 0 records: fix_real has no devices yet.
- 0 console errors.
- Nothing was written to fix_real.
