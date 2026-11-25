# M16 Procurement & Sourcing: sub-module capture-button audit

Date: 13 Nov 2026 · Scope: the 10 Function Register sub-module pages of M16 in the P03 workspace
· Live server: 8069 = `fix_real`

## 1. What was reported

Not every M16 sub-module page had a button to record its data.

## 2. How the audit was done

- **What M16 should do.** The module specification
  (`1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M16_Procurement_and_Strategic_Sourcing.md`):
  - §3 scope (M16 owns the requisition, PO, goods-receipt document, three-way match and the RTV raise;
    M15 owns the warehouse stock event, M52 the vendor bill);
  - §5 FR-PRO-001…038;
  - §8 lifecycles, §9 BRU-PRO-01…20, §13 roles.
- **What the code allows.** The models in `cd_requisition` (requisition, PO, RFQ, bid, award, blanket,
  expediting, inspection, PO goods receipt), `cd_inventory` (stock receipt, RTV) and `cd_ap_ext`
  (vendor bill and its match).
- **What the workspace shows.** The registry `static/src/a06/m16.js` and the server surfaces
  `controllers/a06/m16.py`.
- **What a user actually sees.** Each page was evaluated with the engine's own `fregCreate` /
  `fregPanels` code, run in node over the real registry (exactly what the browser runs).
- **How each page is classified:** a record a person enters → a "+ New" button or a form chip;
  a step on an existing record → buttons on the page's list; a computed verdict → no button.

## 3. Findings (before the fix)

| # | Page | What it showed | Verdict |
|---|---|---|---|
| 1 | Demand Intake | "+ New Purchase Requisition", chip | OK |
| 2 | Requisition & Approval | Same; approval decided in the M63 inbox | OK |
| 3 | Consolidation | **Nothing.** The page was `create: false` with no form. Its report grouped every requisition (any state) **by branch and urgency** | **Missing, and the report was the opposite of the requirement.** FR-PRO-006 consolidates the *same part* across branches into one sourcing event. No RFQ could carry more than one requisition, so consolidation was impossible anywhere |
| 4 | RFQ & Bidding | "+ New RFQ" and an RFQ chip only | **Partly missing.** No chip for the supplier bid (FR-PRO-012, P0) or the award decision (FR-PRO-014), though both forms exist |
| 5 | PO Lifecycle | "+ New Local PO"; 4 chips | OK |
| 6 | Blanket Orders | "+ New Blanket Agreement"; **no chip** (`forms: []`) | Partly missing |
| 7 | Expediting | "+ New Expediting Case"; **no chip** (`forms: []`) | Partly missing |
| 8 | GRN & Inspection | "+ New Inspection Outcome"; chips PO Goods Receipt, **GRN**, RTV Request. The RTV list had no "+ New" and no actions | **Wrong record + inconsistent.** The "GRN" chip created an M15 *warehouse* stock receipt with no purchase order, a second receiving path that bypasses the PO goods receipt and so the three-way match (FR-PRO-026, BRU-PRO-01). No chip for the inspection outcome. The RTV list refused "+ New" while its chip raised one, and credit tracking (FR-PRO-033/034) had no button on the page |
| 9 | 3-Way Match | **Nothing.** Only the computed workbench report | **Missing.** The match is computed, but its third document, the vendor's bill, had no capture on the page, and the bills with their verdict were not listed |
| 10 | Spend Analysis | No button | OK (spend and price history are computed from the orders) |

Result: 2 of 10 pages captured nothing (3, 9); 4 pages lacked a chip for their record (4, 6, 7, 8);
1 page offered a wrong-record chip (8, GRN).

## 4. What was changed

### Workspace registry: `cd_p03_portal/static/src/a06/m16.js`

| Page | Now offers |
|---|---|
| 3 Consolidation | **"+ Consolidate Requisitions into an RFQ"** (new form `M16-form-rfq-consol`): choose the part and the approved requisitions from any branch. The grid lists only approved requisitions not yet on a PO. Chip: Consolidated RFQ |
| 4 RFQ & Bidding | "+ New RFQ"; chips RFQ, **Supplier Bid**, **Award Decision**. The RFQ form shows its consolidated requisitions |
| 6 Blanket Orders | "+ New Blanket Agreement"; chip **Blanket Agreement** |
| 7 Expediting | "+ New Expediting Case"; chip **Expediting Case** |
| 8 GRN & Inspection | Chips PO Goods Receipt, **Inspection Outcome**, RTV Request; the **GRN chip is removed** (the warehouse receipt form is now read-only here, `create: false` + pick message). The RTV list has "+ New", an empty-state text, and **Submit RTV** / **Record Credit** (approval and shipping stay M15's) |
| 9 3-Way Match | **"+ New Vendor Bill"** (M52's own bill form, preset to a PO bill); new list **M16-match-queue**: the PO bills with their match verdict and its detail, read-only, opening M52's bill form |
| 10 Spend Analysis | Unchanged: no button (computed) |

### Model: `cd_requisition` (FR-PRO-006 consolidation, needs a module upgrade)

- `fix.procurement.rfq.requisition_ids` (new Many2many "Consolidated Requisitions").
  - Each must be **approved**, **not yet on a PO**, for the **RFQ's part**, and on no other live RFQ.
  - The RFQ quantity becomes their total.
  - It is fixed once bids are invited.
- `fix.procurement.award.action_create_po` converts **every** requisition of the RFQ.
  - It raises one PO with **one line per requisition**, at the awarded price, each line labelled with its branch.
  - The PO carries the first requisition as its own (BRU-PRO-01).
  - It has no single branch when the requisitions come from several branches.
- `fix.requisition.action_convert_to_po` refuses a requisition that is out to tender on an RFQ: the award raises its PO, so a direct PO would buy it twice. This also closes the same gap for the existing single-requisition RFQ.

### Server: `cd_p03_portal/controllers/a06/m16.py` and `writable.py`

- The **Cross-Branch Consolidation** report now groups approved, unconverted requisitions by part. For each part it shows:
  - the requesting branches and how many there are;
  - the requisitions, the total quantity and the estimated amount;
  - the earliest required-by date;
  - its sourcing status: Consolidate, Single branch, or Out to tender on an RFQ.
- `writable.py` was regenerated (`form_fields.py --a06`): `requisition_ids` is writable on the RFQ.

### Tests

- `cd_p03_portal/tests/test_m16_submodule_capture.py` (17 tests). It evaluates every page as the browser does: **10 fail on the old registry; all pass now**. The estate page standard (`test_estate_module_pages.py`) passes for M16.
- `cd_requisition/tests/test_procurement_ops.py`: 3 new ORM tests:
  - the consolidated quantity;
  - one PO with a line per branch, all requisitions converted;
  - the refusals: draft, wrong part, already on an RFQ, direct conversion while out to tender, change after opening.

**Results** on a private copy of `fix_test` upgraded with `-u cd_requisition`:

| Suite | Result |
|---|---|
| `test_procurement_ops.py` (with the 3 new tests) | all 11 pass |
| `test_requisition.py` | pass |
| `test_a06_final_m16.py` | 29 / 29 |
| `test_supplier_proforma_advance.py` | 20 / 20 |
| `test_a06_m16_controls.py` | 84 pass, 3 fail |

All 3 `test_a06_m16_controls.py` failures read `column fix_vendor_invoice.advance_applied does not exist`. That column is another session's uncommitted `cd_ap_ext` field, absent from the test copy; it is not from this change.

## 5. Gaps that need a build or an owner decision (not done here)

| Spec | Gap |
|---|---|
| BRU-PRO-08, FR-PRO-030 | No **documented match override**: an exception is resolved only by correcting the PO, the receipt or the bill. A Finance-Manager override record (and its approval) does not exist |
| FR-PRO-009 | No **approved-source list** per part (`fix.approved.source`) |
| FR-PRO-037, BRU-PRO-19 | No **service-entry confirmation** for non-stock purchases |
| FR-PRO-015 | No reverse auction |
| FR-PRO-005 | No budget check against M54 |
| §8.2 | The RTV has no RMA-requested / RMA-issued / awaiting-credit / escalated states (M15's lifecycle: draft → submitted → approved → shipped → credited) |

## 6. Deployment state

- **JS (all buttons, chips and lists): live on 8069 as soon as Odoo rebuilds the asset bundle** (or at once under `?debug=assets`).
- **Needs an 8069 restart with `-u cd_requisition`**:
  - the consolidation field and its award conversion;
  - the direct-conversion guard;
  - the rewritten consolidation report;
  - the writable entry.

  Until then, the consolidation form shows no requisition picker, because the server skips a field it does not know.
- **Update, 13 Nov ~02:40:**
  - `fix_real` already holds the schema. The relation table `fix_procurement_rfq_requisition_rel` and its `ir.model.fields` row exist: another session upgraded `cd_requisition` there.
  - A read-only, rolled-back run of this code against `fix_real` worked: it loaded the field, ran the consolidation report (0 rows) and read the RFQs.
  - A plain 8069 restart is therefore enough. One was scheduled by another session.
- **Committed 13 Nov as `bbd17803`** on `fix/a03-live-data-and-pending-work` (7 files; all hooks passed). Not pushed.
  - The PO vendor-picker residency filter is not in it: another session committed it earlier as `a446a239` (pushed).
    The last bullet of the `bbd17803` commit message wrongly says the commit carries it.
