# M09 Warranty & Claims — sub-module capture-button audit

Date: 13 Nov 2026 · Scope: the 12 Function Register sub-module pages of M09 in the P03 workspace
· Live server checked: 8069 = `fix_real`

## 1. What was reported

Not every M09 sub-module page had a button to record its data.

## 2. How the audit was done

- **What M09 should do.** The module specification (`1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M09_Warranty_Protection_Plans_and_Claims.md`):
  - §5 FR-WTY-001…066;
  - §8 lifecycles;
  - §9 business rules, in particular BRU-WTY-16: the repair warranty is charged to 1000FiX only.
- **What the code allows.** The models in `cd_warranty_claims` and `cd_device_registry`:
  - who may create each record (`create()` guards, ir.model.access);
  - which workflow methods exist.
- **What the workspace shows.** The registry (`static/src/a04/m09.js`) and the server whitelist (`controllers/a04/m09.py`).
- **What a user actually sees.** Each page was evaluated with the engine's own `fregCreate` / `fregPanels` code, run in node over the real registry, which is exactly what the browser runs.
- **How each page is classified:**
  - a record a person enters → a "+ New" button or a form chip;
  - a step on an existing record → buttons on the page's list;
  - a computed verdict or score → no button.

## 3. Findings (before the fix)

| # | Page | What it showed | Verdict |
|---|---|---|---|
| 1 | Warranty Register | "+ New Warranty Register Entry"; no chips. "Transfer & Void Rules" was on no page at all | Partly OK. The transfer form was unreachable from the sub-module pages |
| 2 | Manufacturer Validation | No button. Request Verification is on the register list | OK (a workflow step) |
| 3 | Repair Warranty | **"+ New Brand Claim"** and a "Brand Claim" chip. Its report re-listed the brand claims | **Wrong record.** 1000FiX's own repair warranty is never claimed from a brand (BRU-WTY-16). A comeback is opened on the delivered order (`action_reopen_comeback`) |
| 4 | Entitlement Evaluation | No button | OK (the verdict is computed at intake) |
| 5 | Protection Products | **Nothing.** The list was marked `create:false` and the page named no form | **Missing.** `fix.warranty.product` is created by a Warranty Officer, and a form exists (`M09-form-wproduct`). That form's Back also pointed at the wrong list |
| 6 | Claim Assessment | No button; actions on Brand Claims | OK |
| 7 | Evidence Assembly | **Nothing.** The list was `create:false`, no form, and the Assemble Evidence button was not on the page | **Missing.** A clerk may add an evidence item while the claim is draft or ready (the model locks the pack after submission), and an upload form exists (`M09-form-wevidence`) |
| 8 | Brand Submission | "+ New Brand Claim" | OK |
| 9 | Decisions & Appeals | "+ New Claim Appeal", but the Claim Appeals list itself had no "+ New" | Inconsistent (fixed) |
| 10 | Reconciliation | Listed **M53's IAS 37 provisions** (a computed reserve) and no button | **Missing, and serious:** see the note below |
| 11 | Recalls | Recall Campaign chip only. The list was `create:false`, so there was no "+ New" | **Missing.** A clerk enters a planned campaign; the model allows it |
| 12 | Fraud Detection | No button | OK (signals are computed) |

Also found:

- **The "Protection Policy" chip opened the wrong record.** It opened the warranty *provision* policy (cost ratio, lookback months), which is accounting configuration. In this estate the cover sold to a customer is a warranty register row of type "Extended/1000FiX".

**Note on Reconciliation (#10):** recording the brand's money has no button anywhere.
- The model methods exist: `action_record_remittance(amount, bank_ref)` for a Claim Decision Officer, and `action_record_remittance_advice` for a clerk.
- Neither appears in any workspace screen, and neither is on the server's action whitelist.
- So an approved claim could never become *remitted*, and therefore never *closed*, from the workspace. FR-WTY-053 (remittance matching) was unreachable.

Result: 5 of 12 pages had no capture at all (5, 7, 10, 11, plus the unreachable transfer form). 2 pages captured the wrong record (3, and the Protection Policy chip).

## 4. What was changed

**`static/src/a04/m09.js`** (live on 8069 under `?debug=assets` straight away):

| Page | Now offers |
|---|---|
| 1 Warranty Register | "+ New Warranty Register Entry"; chips Warranty Register Entry and Warranty Transfer; the Transfer & Void Rules list is on the page |
| 3 Repair Warranty | Its records are now service orders with a repair warranty. Two new lists:<br>• **Repair Warranty Comebacks**: delivered and closed orders, with *Open Comeback (repair warranty)*;<br>• **Open Rework Orders**, with *Request Zero-Charge Rework*.<br>No brand-claim button |
| 4 Entitlement Evaluation | No button (unchanged). It now also lists Manufacturer Validation |
| 5 Protection Products | **"+ New Protection Product"**; chips Protection Product and Protection Policy (now the extended-cover registration). Back on the product form fixed |
| 7 Evidence Assembly | **"+ New Warranty Claim Evidence"** (upload form); chip Claim Evidence Item; Brand Claims list on the page (Assemble Evidence) |
| 9 Decisions & Appeals | The Claim Appeals list now has "+ New"; Brand Claims list on the page |
| 10 Reconciliation | Its records are approved / remitted claims. A new **Remittance Matching** list has three buttons:<br>• *Record Bank Receipt* (asks for the amount and the bank reference);<br>• *Note Brand Remittance Advice*;<br>• *Close Claim*.<br>Also: a Provision Policy chip; the provisions list says it is computed in M53 |
| 11 Recalls | **"+ New Recall Campaign"** |

- **Protection Policy chip** → the warranty register form (extended cover).
- **New Provision Policy chip** → the provision policy form, now titled "Warranty Provision Policy".

**`controllers/a04/m09.py`** (Python: goes live at the next 8069 restart):
- `action_record_remittance` and `action_record_remittance_advice` are added to the `fix.warranty.claim` whitelist. Each method still checks its own role and the claim's state.
- The "Repair Warranty & Rework" report now lists orders carrying a repair warranty, with:
  - the warranty end date and the days left;
  - any comeback order.

  It used to list brand claims.

**Server-side proof:** two tests in `cd_warranty_claims/tests/test_a04_m09_controls.py`. They call `/p03/model/action` exactly as the workspace does, through the merged whitelist:
- `test_the_remittance_matching_page_settles_an_approved_claim`:
  - a clerk notes the brand's advice, and the claim stays part-approved;
  - a clerk's bank receipt is refused by the method's role check, not by the whitelist;
  - an officer's receipt moves the claim to *remitted*.
- `test_the_repair_warranty_page_and_report_read_service_orders`:
  - Open Comeback creates the linked rework order;
  - the report lists the order with its comeback and 30 days left;
  - the report shows no brand claim.

**Guard:** `tests/test_m09_capture_buttons.py`, 24 tests.
- On the old code: 12 fail.
- On the new code: 24 pass.

## 5. Evidence

| Check | Result |
|---|---|
| Guard test on HEAD (old registry and controller) | 12 failed, 12 passed |
| Guard test on the fix | 24 passed |
| Estate and registry suites (`test_estate_module_pages`, `test_submodule_create_button`, `test_a04_submodule_mapping`, `test_all_submodule_mapping`, `test_a04_write_whitelist`, `test_a04_forms_show_their_children`, `test_a04_registry_coverage`, plus the guard) | **686 passed, 0 failed** (an M11 failure in one earlier run came from a peer session's half-saved `m11.js` and cleared on rerun) |
| Server path on a private copy of `fix_test` (`test_a04_m09_controls.py`, run with this checkout's controller) | **23 passed**, including the remittance and repair-warranty endpoint tests |
| `node --check m09.js`; `py_compile` and `ruff check` on `m09.py` | clean |
| 8069 serves the edited registry from disk | `/cd_p03_portal/static/src/a04/m09.js` → 200, contains `M09-remit`, `action_reopen_comeback`, `M09:Provision Policy` |
| fix_real M09 data (read-only count) | 0 warranties, 0 claims, 0 evidence, 0 products, 0 recalls, 0 appeals, 0 transfers, 0 service orders |

**Live run on a throwaway server.**
- Setup:
  - Odoo on port 8111 against a private copy of `fix_test` (seeded with one part-approved claim and one delivered order carrying a repair warranty), serving this checkout's Python and JS;
  - signed in as a generated test user;
  - 8069 was not touched.
- **Sub-module sweep, "+ New" per page.**
  - Present on six pages, exactly as designed: 1 Warranty Register Entry · 5 Protection Product · 7 Warranty Claim Evidence · 8 Brand Claim · 9 Claim Appeal · 11 Recall Campaign.
  - None on 2, 3, 4, 6, 10, 12.
- **Every page lists its screens and chips, and shows its live rows.** Examples: Reconciliation shows Remittance Matching, Brand Reconciliation, Reserves, Policy Lifecycle and the Provision Policy chip; Repair Warranty shows SO005101.
- **Record Bank Receipt** pressed on the Remittance Matching row (1500, BANK-LIVE-1): claim CLM/2026/00142 went from part-approved to **remitted**, with the receipt and reference stored and the test user recorded as the person who entered it.
- **Open Comeback** chosen on the Repair Warranty Comebacks row: rework order SO005103 was created, linked to SO005101, in category rework.
- **Repair Warranty & Rework report** (served by `/p03/model/report`): SO005101, warranty until 2026-12-12, 29 days left, comeback SO005103; no brand claim in it.
- **+ New Recall Campaign**: the form opened and saved as Planned.
- **Defect found and fixed during the run.** A list action that asks several questions prefixed each prompt with the row's `name`. A claim has no `name`, so the prompt read "undefined — Amount received…".
  - The fix is in `p03_workspace.js`: fall back to the row's first column, then `#id`.
  - Re-checked live: the prompt now reads "CLM/2026/00142 — Amount the brand advises it paid (BDT)".

**On the real 8069 (fix_real), read-only, with the user signed in.**
- 8069 restarted at 01:41, after the M09 edits (01:04 on disk), so it already runs them. No further restart was made.
- **Whitelist:** `/p03/model/action` with an empty id list accepts `action_record_remittance` and `action_record_remittance_advice` (they reach "Record not found"). An unlisted method is still refused ("Action not available for this surface").
- **Report:** `warranty_repairs` returns the new columns (order, device, until, days left, comeback) and the new empty text.
- **Bundle users load** (`/web/assets/658eef3/web.assets_web.min.js`): contains `M09-remit`, `action_reopen_comeback` and `M09:Provision Policy`.
- **Sub-module sweep:** "+ New" on pages 1, 5, 7, 8, 9 and 11 only, identical to the throwaway run.
- **The prompt-label fix** in `p03_workspace.js` reached users without a restart: 8069 rebuilt its bundle as `7889fb2`, which contains it.
- **Committed** as `1abde660` on `fix/a03-live-data-and-pending-work` (5 files; all pre-commit hooks passed; not pushed).

**Incident during verification:**
- At 01:01 local time (17:01 UTC), Postgres crashed: its 64 MB shared-memory area (`/dev/shm`) filled during a database restore's foreign-key check, then a server process hit a segmentation fault.
- Postgres stayed in recovery for about 17 minutes. Every server, 8069 included, was cut off from the database during that time.
- fix_real and the test copy both came back intact.
- My copy had parallel queries turned off and had finished restoring before the crash, so the restore that filled the memory was most likely another session's.
- The standing fix is to give the container a larger `shm_size` in the compose file.

**Not verified:**
- A click-through in the signed-in workspace. The browser pane is not signed in, and I do not type passwords into the fix_real database.
- The list buttons (Record Bank Receipt, Open Comeback) on fix_real itself. fix_real has no claim or order row to press them on. Their server path is proven on the test copy.

## 6. Still open (needs a build or an owner decision, not a button)

- **Brand claim rules (FR-WTY-040).**
  - The screen "Brand Rules & Formats" lists warranty products.
  - Per-brand rules (mandatory fields, photo requirements, submission window) are not configurable: the evidence requirement list is fixed in code.
  - This needs a model (spec: `fix.brand.claim.rule`).
- **Protection policy instance (FR-WTY-018 to 026).**
  - There is no sold-policy record with limits, excess, waiting period and reserve.
  - The extended cover is a warranty register row.
- **Inbound protection claims (FR-WTY-027 to 037), write-off (FR-WTY-055), defective-part return (FR-WTY-057).** Not built.
- Nothing M09-specific is waiting on a restart: the registry, controller and prompt fix are all live on 8069.
