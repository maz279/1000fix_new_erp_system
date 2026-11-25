# M37 Product & Service Catalogue: data-capture button audit

**Date:** 13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** live on 8069/8089 since the 18:35–18:36 restart (user approved); production bundle `ecfd8eb`; nothing committed

## 1. The question

The M37 workspace has 13 sub-module pages (Function Register, 120 functions). Not all of them showed a button that captures the right record. Which pages should have one, and what should it open?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M37_Product_and_Service_Catalogue_Management.md` (FR-CAT-001…046, BRU-CAT-01…16, lifecycle §8, entities §10)
- `contracts/nav/registry.json`

| # | Sub-module | Spec | What a person records |
|---|---|---|---|
| 1 | Unified Item Master | FR-001…012 | a catalogue item of any of the nine types |
| 2 | Typed Taxonomy | FR-004 | a category node |
| 3 | Service Definition | FR-013…020 | a service (scope, duration, warranty, SLA) |
| 4 | rBOM & SRT | FR-022/023 | the standard parts of a service (rBOM line) |
| 5 | Repair Operations | FR-021/023/027 | a coded repair operation with its standard repair time |
| 6 | Kits & Bundles | FR-041 | a kit and its components |
| 7 | Product Hierarchy & Variants | FR-004/006 | a hierarchy node |
| 8 | Brand-Model-Device Master | FR-032 | a brand and its device models |
| 9 | Fault Taxonomy | FR-042 | a fault code |
| 10 | Part Identity | FR-029…035 | a spare part (MPN, supersession, grade) |
| 11 | Contract & Protection Templates | FR-036…040 | contract template, protection plan, rental SKU (refurb grades are a fixed A–D set) |
| 12 | Tax & Rev-Rec Classification | FR-043 | the tax and revenue class of an item |
| 13 | Lifecycle & Governance | FR-044/045 | nothing new: submit, approve, publish, restrict, discontinue an existing item |

## 3. What the code had (before)

The engine's own `fregCreate` / `fregPanels` were run over the real registry, and every page was clicked on 8069.

| # | Page | Capture before | Defect |
|---|---|---|---|
| 1 | Unified Item Master | + Catalogue Item | Correct |
| 2 | Typed Taxonomy | **nothing** | No category form at all |
| 3 | Service Definition | + New Service Definition | The list showed **all 16,178 items**, every one a part, accessory or finished good on fix_real. Its own list refused + New, and the form opened with no item type set. |
| 4 | rBOM & SRT | **chip only** | The rBOM list was `create: false` although its form works |
| 5 | Repair Operations | + New rBOM Line | **Wrong record.** A repair operation is the labour item with its standard time, not a BOM line. |
| 6 | Kits & Bundles | + New Service Kit | No chip on the page |
| 7 | Product Hierarchy | **nothing** | — |
| 8 | Brand-Model-Device | + New Brand | No chip on the page |
| 9 | Fault Taxonomy | **chip only** | List `create: false` though the form and the ACL allow it |
| 10 | Part Identity | **chip only (rBOM Line)** | **Wrong record.** The page listed rBOM lines (0 rows); the **13,345 real parts** were not on it. |
| 11 | Contract & Protection | + New Contract Template | The Protection Plan list also showed all 16,178 items, and its form opened with no type. Rental SKUs and refurb grades sat on **no page**. The refurb-grade list offered a + New that **no role may save**: the ACL is read-only. |
| 12 | Tax & Rev-Rec | **nothing** | — |
| 13 | Lifecycle & Governance | nothing | Correct: the lifecycle moves through the item lists' actions |

## 4. What was changed

All changes are JS registry plus one regenerated whitelist entry. No model or schema change was needed.

| # | Page | Capture now |
|---|---|---|
| 1 | Unified Item Master | unchanged |
| 2 | Typed Taxonomy | **Catalogue Category** chip (new `M37-form-category` on product.category). Only product managers may save a node, so it is a chip, not a + New. |
| 3 | Service Definition | **+ New Service Definition**. The list is filtered to service and inspection items; a new definition starts as type Service. |
| 4 | rBOM & SRT | **+ New rBOM Line** (list opened for create; empty-state text) |
| 5 | Repair Operations | page reads **Repair Operations** (new list: labour-only items with SRT, lifecycle actions). **+ New Service Definition** opens with type **Labour Only** (verified on 8069); rBOM Line chip. |
| 6 | Kits & Bundles | + New Service Kit, plus the **Service Kit** chip |
| 7 | Product Hierarchy | **Catalogue Category** chip |
| 8 | Brand-Model-Device | + New Brand & Authorisation (device models are entered on its lines), plus the chip |
| 9 | Fault Taxonomy | **+ New Fault Code** |
| 10 | Part Identity | page reads the **13,345 spare parts**, with successor and end-of-support columns and Submit / Discontinue-Supersede actions. **+ New Catalogue Item** starts as type Spare Part. |
| 11 | Contract & Protection | + New Contract Template; chips Contract Template, Protection Product Template, **Rental SKU**. The Protection Plan list is filtered to protection items, and its form starts as Protection Plan. Rental SKU and Refurb Grade lists are on the page; refurb grades are read-only, with a note. |
| 12 | Tax & Rev-Rec | **VAT Treatment** chip: M51's own tariff-code → treatment form (`M51-form-treatment`), which M51 owns and approves |
| 13 | Lifecycle & Governance | unchanged (workflow actions) |

### Files

- `addons/platform/cd_p03_portal/static/src/a04/m37.js`
- `addons/platform/cd_p03_portal/controllers/a04/writable.py`: regenerated; the only M37 change is `product.category: {name, parent_id}`. The file also holds a peer's uncommitted M11 lines, which are not part of this change.
- `addons/platform/cd_p03_portal/tests/test_m37_capture_buttons.py`: **new guard**, 32 tests; **19 fail on HEAD**

## 5. Verification

- **Guard:** 32/32. With estate standard, registry coverage, mapping and the create-button rules, **701 passed**. The 1 failure is the M01 estimate test, which needs the DB and failed before this change too. A04 whitelist: 2/2.
- **Disk code under `?debug=assets`:**
  - A probe of every page grid, list, form and report, plus M51's form, made **50 calls with 0 errors and 0 dropped columns**.
  - Part Identity now returns 13,345 rows (it returned 0 before).
  - Service and protection lists are correctly empty: fix_real has no service or protection items yet.
- **Click sweep of all 13 pages:** each shows the capture in section 4. The Repair Operations form opens with Item Type = Labour Only and no error.
- **After the 18:35 restart:**
  - the production bundle `ecfd8eb` contains the change;
  - a combined M34 + M37 probe made **77 calls with 0 errors**;
  - a product.category write is accepted by the whitelist (it answers "Record not found" for a dummy id, not "not editable").

Not exercised: saving a record on fix_real. **No user holds the Catalogue Officer role** on fix_real, so creating catalogue items, rBOM lines, kits and rental SKUs is refused for everyone but the superuser until that role is granted. That is an owner decision.

## 6. Gaps the spec asks for and the estate does not have

| Spec | Missing |
|---|---|
| FR-043, BRU-CAT-02 | **No tax class, HS code or revenue-recognition class on the catalogue item.** The item form's "Statutory HS Code & VAT" tab is empty. M51's tariff master exists but nothing links an item to it. |
| FR-021/023/024, BRU-CAT-11 | Repair operations, effective-dated SRT register and governed re-baselining (a labour item holds one SRT number) |
| FR-022, BRU-CAT-07 | rBOM per operation per model with criticality and alternates. Today it is one flat list per item. |
| FR-030/033 | Part cross-references / alternates and the model-compatibility matrix |
| FR-031 | Supersession as its own record (now: successor staged on Discontinue) |
| FR-034/035 | Provenance grade (genuine / OEM / aftermarket) and hazardous classification |
| FR-005/006 | Attribute sets and variants in the workspace |
| FR-042 | Fault tree with root cause and brand claim-code mapping (flat fault codes now) |
| FR-038 | Subscription plan definitions |
| — | MPN and legacy part number live on product.template and are not editable from the M37 forms |
| Owner | Grant the Catalogue Officer / Publisher roles (0 holders on fix_real) |
