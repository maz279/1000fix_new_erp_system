# M44 Import, Trade Compliance & Landed Cost — Sub-Module Capture Audit (2026-11-16)

**Trigger.** The user observed that not every M44 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M44_Import_Trade_Compliance_and_Landed_Cost.md`. Sections used: §3 scope, §5 FR-ITC-001…036, §6 T-01…T-11, §8.1/§8.2 lifecycles, §9 BRU-ITC-01…20, §10.1 owned entities, §13 roles.
- Code:
  - `cd_p03_portal/static/src/a06/m44.js` (the page registry: 8 sub-module pages);
  - `cd_p03_portal/controllers/a06/m44.py` (surfaces, packs, KPIs);
  - `cd_import_order/models/*.py` (21 M44 models).
- Live data: fix_real holds **no M44 record of any kind** (0 import orders, LCs, Bills of Entry, landed sheets, arrivals, C&F agents, tariff rows, HS rulings, IRCs, covers). The Import Officer and Import Approver roles have **1 holder each**.

## 1. What was there (HEAD a94fb665)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| # | Page | "+ New" | Form chips | Defect |
|---|---|---|---|---|
| 1 | Import Order Lifecycle | Import Order | Import Order | The page lists proformas, but no proforma could be captured from it. |
| 2 | LC & Payments | LC | LC Application | **LC Amendments, LC Payments and Advance Payments sat on no page.** No LC discrepancy existed (FR-ITC-016, §8.2 DISCREPANT → accepted/refused). Bank charges (FR-ITC-018, P0) could only be typed as one total on the landed sheet. |
| 3 | HS Classification | HS ruling | HS Ruling Request | **The HS Tariff Master (the rate schedule every ruling reads) sat on no page.** |
| 4 | **Eligibility & IRC** | IRC | **none** | **Restricted & Prohibited Goods and Import Permits sat on no page.** The LCA list was on the page with no capture. |
| 5 | **Shipping & Insurance** | Shipping document | **none** | **Cargo Insurance sat on no page.** No freight booking: the shipment named no forwarder, carrier or booking (FR-ITC-021 P0, BRU-ITC-12). |
| 6 | Port & Customs | Arrival | Bill of Entry | **C&F Agents sat on no page.** No customs query or examination could be recorded (FR-ITC-028 P0: assessment ⇄ query). Port, storage, handling and C&F charges (FR-ITC-030/031 P0) had no document. |
| 7 | Duty Computation | Bill of Entry | Bill of Entry | The tariff rows the cascade reads were not reachable. |
| 8 | **Landed Cost** | Landed sheet | **none** | **No cost document existed.** Freight, clearing and bank charges were typed totals with no bill behind them; `fix.import.order.action_close` said so itself: "BRU-ITC-16 has no document model". |

In summary:
- Every page had a "+ New", but **8 working lists** (with working forms) were on **no** sub-module page. Their records could not be captured from any sub-module.
- Pages 4, 5 and 8 offered no chip.
- Three §10.1 owned entities had no model: `fix.consignment.cost` (cost documents), `fix.lc.discrepancy` and the query/examination half of `fix.bill.of.entry`. The `fix.import.shipment` forwarder/booking attributes were also missing.

## 2. What was built

### Backend — `cd_import_order` 19.0.0.3.0, new file `models/fix_import_capture.py`

| Page(s) | Record | What it does | Controls |
|---|---|---|---|
| 2, 6, 8 | `fix.import.cost` | One cost document of a consignment: freight, insurance premium, C&F agency fee, port/storage/handling/examination, demurrage, inland transport, LC & bank charges, or other. It records who billed it, the bill number and date, the currency and amount, the agreed/quoted amount and the copy of the bill. | Recorded by an Import Officer or Finance user. **Reconciled by an Import Approver who did not record it**, with the copy attached. A variance from the agreed amount beyond `cd_import_order.cost_variance_tolerance_pct` (default 0%) **needs a classified cause** (BRU-ITC-16, T-11); "other" needs a note. A foreign-currency document needs its rate to BDT and the rate source (BRU-ITC-14); BDT is derived and stored. An agency fee names its C&F agent (FR-ITC-030). A bank charge's LC must be the order's. Frozen once decided. No capitalisable document after the final landed cost. |
| 8 | `fix.import.landed` + **Fill from Cost Documents** | Fills freight / insurance / clearing / bank charges from the reconciled documents. A line that no document evidences keeps its typed figure. | **Finalise is refused** while any cost document of the order is unreconciled, or when a line differs from its reconciled documents (BRU-ITC-16). The filler counts as the person who changed the amounts, so they cannot finalise. |
| — | `fix.import.order.action_close` | | Refused while a cost document is unreconciled (BRU-ITC-18). |
| 2 | `fix.import.lc.discrepancy` | A presentation defect raised by the negotiating bank: bank, reference, date, description, fee, delay. | Only on an opened or amended LC. **No LC payment is recorded while one is undecided** (§8.2). Accepted (waived) or refused by an Import Approver other than the recorder, with a reason. |
| 6 | `fix.import.customs.query` | A classification, valuation or document query, or a physical examination, on a lodged Bill of Entry. | Open → answered (response) → resolved (customs decision). An examination needs its result. **The Bill of Entry is not assessed while a query is unresolved** (FR-ITC-028, §8.1). |
| 5, 6 | `fix.import.arrival` + forwarder, carrier, booking ref, port of loading | The shipment record becomes the freight booking. | **The forwarder must be active in M42** (BRU-ITC-12). The booking is fixed once the shipment arrives. |

Also: ACLs (a plain employee only reads; nobody deletes; Finance may record cost documents), company and operating-unit rules, and three sequences (ICOST/, ILCD/, ICQ/).

### Workspace — `m44.js`, `controllers/a06/m44.py`, `writable.py`

- Three new list screens (Import Cost Documents, LC Discrepancies, Customs Queries & Examination), labelled in the navigation, with their actions served.
- Three new forms. Every form offers only typed inputs; the regenerated `writable.py` whitelists exactly those fields. The arrival form gained the booking fields and is now tabbed (Booking / Arrival & Clearance), as the >15-field rule requires.
- Every page now has its own capture and a chip for every record it lists:

| # | Page | "+ New" | Chips |
|---|---|---|---|
| 1 | Import Order Lifecycle | Import Order | Import Order, **Proforma Invoice** |
| 2 | LC & Payments | LC | LC Application, **LCA, LC Amendment, LC Discrepancy, LC Payment, Advance Payment, Import Cost Document** |
| 3 | HS Classification | HS ruling | HS Ruling Request, **Tariff Rate** |
| 4 | Eligibility & IRC | IRC | **IRC Register, Import Restriction, Import Permit, LCA** |
| 5 | Shipping & Insurance | Shipping document | **Shipping Document, Shipment Booking & Arrival, Cargo Insurance** |
| 6 | Port & Customs | Arrival | **Shipment Booking & Arrival**, Bill of Entry, **Customs Query, C&F Agent, Import Cost Document** |
| 7 | Duty Computation | Bill of Entry | Bill of Entry, **Tariff Rate** |
| 8 | Landed Cost | Landed sheet | **Landed Cost Sheet, Import Cost Document** |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m44_capture_buttons.py` (node runs the engine's own `fregCreate`/`fregPanels`) | **HEAD a94fb665: 16 of 32 fail** (all 8 pages, the orphan-list check, the three registers, the forwarder, security, load order). **After: 32/32.** |
| Live `cd_import_order/tests/test_m44_capture_live.py` (non-admin users with the real roles, rolled back) | **18/18.** Mutation check: switching off the variance classification, the landed-sheet agreement check, the discrepancy payment block and the query assessment block turns **4 tests red**; restored. |
| Regression on a fully upgraded clone (`-u all` on a fix_test copy): every A06 portal suite, the estate page standard, the write whitelist, KPI tiles, report export, and all of `cd_import_order/tests` | **1,650 tests, 1 failure.** The failure is `test_submodule_create_button` on M19/2 Journals and M30/1 Branch Master; it predates this work and touches no M44 file. |
| UI on a private server (port 8072, worktree code, upgraded clone) | All 8 pages show the "+ New" and chips in the table above. The Import Cost Document form opens with its two tabs and the eight categories. `/p03/model/records` serves `fix.import.cost`, `fix.import.lc.discrepancy`, `fix.import.customs.query` and the arrival with its forwarder fields. |

## 4. Not built here (owner decisions or other modules)

- **Cost-factor master** (`fix.cost.factor`, a data-driven allocation basis per factor) — the eight fixed categories map onto the sheet's four capitalised lines, and allocation stays by value or quantity. By weight or volume (FR-ITC-035) needs part weights/volumes that M37 does not hold yet.
- **Late cost after the final landed cost** (FR-ITC-036 revaluation on a late document): the module supports one final sheet per order, so a capitalisable document after it is refused with a pointer to Finance (M52/M19). A second revaluation round is a design change.
- **Insurance claims** (FR-ITC-024 P1) and **consolidation of several POs into one shipment** (FR-ITC-004 P1) are not modelled.
- **Owner gaps on fix_real:** one Import Officer and one Import Approver. Every new control is two-person, so the approver cannot be the person who records. No forwarder, C&F agent or insurer exists in M42 yet.

## 5. State — deployed 16 Nov 2026 (user-approved "Commit and deploy")

- Code commit **a5dab160** on `fix/a03-live-data-and-pending-work`, landed from the worktree with a compare-and-swap `update-ref`. All pre-commit hooks passed. **Not pushed.**
- fix_real:
  - Backup: `all_working_folder/1000fix-2/_migration/backups/fix_real_pre_m44_capture_2026-11-16.dump` (49 MB).
  - Ran `-u cd_import_order,cd_p03_portal`, exit 0, no errors. cd_import_order is now 19.0.0.3.0; the three new tables and the four arrival columns exist.
  - Restarted 8069 once; the supervisor loop relaunched it in about 2 s and the registry loaded cleanly (155 modules).
- Live verification:
  - Read-only probe as the real role holders. The Import Officer (admin) can create all three new records. The Import Approver (one real user) can create cost documents and decide the rest. Every new action is served.
  - The served bundle `web.assets_web` 0ea3d80 contains the new forms and actions.
  - The browser pane is not signed in to fix_real, so the pages were walked on the private server (§3), not on 8069.
