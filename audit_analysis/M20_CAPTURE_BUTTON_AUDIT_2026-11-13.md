# M20 AR, Invoicing & Collections — sub-module capture-button audit

**Date:** 13 Nov 2026 · **Scope:** the ten Function Register sub-module pages of M20 in the P03 workspace
**Spec:** `1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M20_Accounts_Receivable_Invoicing_and_Collections.md` (§5 FR-ARB-001..044, §8 lifecycles, §10 entities)
**Code:** `cd_p03_portal/static/src/a08/m20.js`, `controllers/a08/m20.py`, `controllers/a08/writable.py` (generated), `static/src/p03_workspace.xml` (3 empty-state texts), engine `fregCreate` in `p03_workspace.js`
**Guard:** `cd_p03_portal/tests/test_m20_capture_buttons.py` — 19 tests; 13 fail on HEAD, 19 pass on the fix.

## 1. How a page gets its button

A sub-module page shows "+ New …" when its mapping names a creatable form (`create: '<form>'`), or when its own record has a list that allows "+ New" and a form bound to it. A page whose lists all say `create: false` gets no button, even if the module has a form for the record. Form chips in the page's Forms panel are a second way in.

Classification used (same rule as the M02/M09/M10 audits): a record a person types → button or chip. A workflow step on an existing record → list action. A record written by the system or a computed report → no button, and the list says where its rows come from.

## 2. Findings, page by page

| # | Page | Spec (what a person captures here) | Before | After |
|---|---|---|---|---|
| 1 | Billable-Event Intake | Nothing typed: closed jobs feed the queue (FR-ARB-001/002/044). | No button (correct). **The page grid listed invoices, not the queue**: mapped to `fix.ar.invoice`, but the queue is `fix.billable.event`. | No button. The grid lists `fix.billable.event` (new read-only surface). |
| 2 | Invoice Assembly | Manual-invoice exception (FR-ARB-010); consolidated corporate invoice (FR-ARB-008, P0). | "+ New AR Invoice" + Invoice Request chip. There was no way to start a consolidated bill. | Same, plus a **Consolidated Bill** chip. |
| 3 | Mushak 6.3 Rendering | Nothing: rendered when the invoice is issued (FR-ARB-006). | No button (correct). | Unchanged. |
| 4 | Delivery Channels | Consolidated statement-based invoice for a corporate account (FR-ARB-008); statements are run on demand. | **No button, no chip.** The consolidated-bill list was `create: false` and had **no Generate/Send actions**, although its surface already allowed `action_generate`/`action_send`. | **"+ New Consolidated Bill"** (customer, operating unit, reference, period) plus list actions **Generate** (pulls the period's issued invoices) and **Mark Sent**. |
| 5 | Receipt Capture | Receipt in 8 tenders (FR-ARB-019); payment link (FR-ARB-015). | "+ New Receipt" + Receipt and Payment Link chips. | Unchanged. |
| 6 | Matching & Allocation | Allocation is done in the matching console. The person-typed record is the customer's Mushak 6.6 VDS certificate. | No button (`create: false`). VDS Certificate only as a chip. Unapplied Receipts (BRU-ARB-22) and the AR-to-GL reconciliation report sat on no page. | **"+ New VDS Certificate"**. Unapplied Receipts and the AR-to-GL reconciliation added to the page. |
| 7 | Credit Control | Credit terms and limit per customer (FR-ARB-030, P0); write-off; ECL loss rates. | **No "+ New".** A profile could only be added from a "New profile" box inside the Limits screen. ECL Loss Rates and Write-offs lists sat on no page. | **"+ New Credit Profile"**: opens M33's credit-profile form. That form is already live, with its write whitelist; the customer master surfaces the same record. Credit Profile chip added. ECL Loss Rates and Write-offs lists added to the page. |
| 8 | Dunning & Collections | **Log a dispute against an invoice (FR-ARB-036, P0).** Promise to pay (FR-ARB-035, P1). | **No button, no chip, and no screen anywhere could raise a dispute.** The engine's `arDisputeCreate` is never called from any template. Both dispute screens told users to "open one from an invoice's detail view", and that view has no such control. | **"+ New Dispute"**: invoice (issued/paid only), disputed amount, reason. Resolution stays on the five outcome buttons (BRU-ARB-17). Empty texts corrected. |
| 9 | Credit Notes & Refunds | Credit-note request (FR-ARB-038); refund (FR-ARB-040). | No button: the register list is `create: false`. Chips only. | **"+ New Credit Note / Refund"**. |
| 10 | Leakage Detection | Nothing: delivered-but-unbilled is computed (FR-ARB-043). | No button (correct). | Unchanged. |

**Result:** 7 of 10 pages now show a capture button (0 → 3 new person-typed records reachable). The other 3 are system-fed by design.

## 3. Other defects found on the way

- **`/p03/ar/consolidated/generate` can never succeed.** It creates the bill without `operating_unit_id`, which is required. It is also dead code: the engine's `arConsolidatedGenerate` is called from no template. The new form asks for the operating unit, so this endpoint is no longer needed. It was left as is.
- The bespoke Consolidated Bills screen still offers only "Mark sent". A new bill is generated from the list (page 4).

## 4. Spec gaps that need a build, not a button (no model exists)

| FR | Priority | Missing entity |
|---|---|---|
| FR-ARB-032 dunning ladders per segment | P0 | `fix.ar.dunning.policy`: the ladder is hard-coded (Reminder → Final 7d → Escalate 14d) |
| FR-ARB-043/044 delivered-but-unbilled exceptions | P0 | `fix.ar.unbilled.exception`: the page is a report, and an exception has no resolution record |
| FR-ARB-013/014 delivery record per channel | P0 | `fix.ar.invoice.delivery`: delivery is a state flag; the channels are porting phase |
| FR-ARB-035 promise to pay | P1 | `fix.ar.promise` |
| FR-ARB-034 collections worklist | P1 | `fix.ar.collection.case` |
| FR-ARB-028 deposits and retention | P1 | `fix.ar.deposit` |
| FR-ARB-007 proforma and advance invoice | P1 | no document type on `fix.ar.invoice` |
| FR-ARB-037 payment plans | P2 | `fix.ar.payment.plan`: a dunning suppression code only |

## 5. Verification and deployment state

**Live check on 8069 (fix_real), 13 Nov 01:30, under `?debug=assets`.** That mode reads the edited files from disk for one browser session. A sweep of all ten pages found:

- Seven pages show "+ AR Invoice", "+ New Consolidated Bill", "+ New Receipt", "+ New VDS Certificate", "+ New Credit Profile", "+ New Dispute" and "+ New Credit Note / Refund".
- Pages 1, 3 and 10 show no button.
- The Dispute, Consolidated Bill and Credit Profile forms open with their fields.
- Nothing was saved: fix_real holds 0 rows in every M20 model, and no test records were written there.

**Deployment: DONE, 13 Nov 02:50.**
- Another session upgraded `cd_msp_contract`, `cd_requisition`, `cd_ap_ext`, `cd_ewaste` and `cd_p03_portal` on fix_real (02:44–02:45). It then restarted 8069 and 8089 at 02:49:56. My M20 files were on disk at that point.
- A plain restart before that upgrade would have broken M05 alerts, monitored assets and purchase advances. Their committed fields had no columns on fix_real. I found this before restarting, so I neither restarted nor upgraded myself.
- The production bundle `99c8ea0` contains the change. A sweep on the normal (non-debug) workspace shows all ten pages as in §2, with no errors.
- Server proof, with nothing saved (fix_real still has 0 disputes):
  - The event queue is served.
  - A dispute save passes the whitelist and is refused by the model (invoice does not exist).
  - A consolidated-bill save passes the whitelist and stops at "Operating Unit is required".
- **Committed** `c6be632f` on `fix/a03-live-data-and-pending-work`: the five M20 files only, all pre-commit hooks green. Not pushed.

**Left open:** `fix.ewaste.licence.record` (M18, another session's work) still has no table on fix_real.
