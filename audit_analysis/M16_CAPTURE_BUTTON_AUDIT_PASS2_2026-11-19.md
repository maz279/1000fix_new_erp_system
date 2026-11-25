# M16 Procurement & Sourcing: data-capture audit, second pass

**Date:** 19 Nov 2026 · **Estate:** fix_real on 8069 (fix_dev on 8090) · **Branch:** `fix/m16-capture-pass2` · **Status:** LIVE on fix_real and fix_dev, 19 Nov 2026 (see §7)

## 1. The question

The user again saw M16 sub-module pages without a relevant data capture button. The 13 Nov pass ([M16_CAPTURE_BUTTON_AUDIT_2026-11-13.md](M16_CAPTURE_BUTTON_AUDIT_2026-11-13.md)) gave every page a button. This pass asks the harder question: does each button capture the record the spec says that function records, and does every record the spec asks a person to enter have a capture at all?

## 2. Method

1. **Spec:** `1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M16_Procurement_and_Strategic_Sourcing.md`: FR-PRO-001…038, the lifecycles (§8), rules BRU-PRO-01…20, owned entities (§10.1).
2. **Code, as the user sees it:** the engine's own `fregCreate` / `fregPanels` run in node over the real registry (`static/src/a06/m16.js`). For each page this gives the "+ New" and every chip, with the model and form each opens.
3. **Model inventory:** every field and action of `cd_requisition` (requisition, PO, receipt, RFQ, bid, award, blanket, expediting, inspection), plus the M15 RTV, the M42 price list and the M52 match records, checked against the spec's entities and rules.

## 3. Findings (HEAD fdc8fef7)

Statically, all 9 capture pages still had a button (the 13 Nov fix held). Against the spec, seven pages captured records without what the requirement is about, or lacked a record that had no model anywhere:

| # | Page | What the button captured | What the spec requires (missing) |
|---|---|---|---|
| 1, 2 | Demand Intake / Requisition | a requisition | FR-PRO-001 (P0): **where the demand comes from** (branch, M15 replenishment, M43 plan, job backorder, project, facilities, IT, marketing) and its reference. FR-PRO-002 (P0): the **budget reference**. FR-PRO-037: whether it buys stock, non-stock goods or a **service**. None existed. |
| 4 | RFQ & Bidding | RFQ, bid, award | FR-PRO-009 (P0): **no approved-source list** per part (no model). FR-PRO-011 (P0): an RFQ had **no invited suppliers and no response deadline**: it was issued to nobody, and anyone could bid. FR-PRO-012/013 (P0): a bid was a **price and a lead time only**: no warranty, MOQ, payment terms, incoterm or quotation document, so bids compared on price alone. |
| 5 | PO Lifecycle | local / import PO | FR-PRO-017 (P0): **no payment terms or incoterm** on the order, not even on an import PO. |
| 6 | Blanket Orders | blanket agreement | FR-PRO-019: an active blanket offered **no call-off**; a call-off could only be made by opening a new PO elsewhere and picking the blanket. |
| 8 | GRN & Inspection | PO goods receipt, inspection, RTV | FR-PRO-026 (P0): a receipt line recorded **no condition or discrepancy**. FR-PRO-037 / **BRU-PRO-19 (hard rule)**: **no service-entry confirmation**: a service or non-stock purchase could only be "received" as goods by a storekeeper, never confirmed by the requester. |
| 9 | 3-Way Match | vendor bill (M52 form) | FR-PRO-030 (P0): an exception is worked as a **case** with cause, owner and due date; BRU-PRO-09: **tolerance bands** set by the CFO. Both exist as M52 records (`fix.ap.match.exception`, `fix.ap.match.tolerance`) but the M16 page offered neither. |
| 3, 7, 10 | Consolidation / Expediting / Spend | | correct (10 is computed) |

## 4. What was built

### Models: `cd_requisition` 19.0.1.1.0, `models/fix_procurement_capture.py` (imported last)

| Spec | Built |
|---|---|
| FR-PRO-001/002 | `fix.requisition`: `demand_source` (required, default Branch Request), `source_ref`, `budget_ref`, `purchase_kind` (stock / non-stock / service). Submission refuses a replenishment, planned-order, job or project demand without its reference, and a project without its budget. An M43-raised requisition is tagged "M43 Planned Order". All four are fixed once converted or cancelled. |
| FR-PRO-009 | **`fix.procurement.approved.source`** (new): part, supplier, priority, agreed price, currency, MOQ, lead time, validity. A Buyer proposes it. A Procurement Approver **other than the proposer** approves it, only for a supplier active in M42 (BRU-PRO-02), and never twice for the same part and supplier. Terms are fixed once approved; withdrawing needs a reason. **It is used in two places:** RFQ "Invite Approved Sources", and the vendor of a requisition submitted without one. That vendor is filled in at **submission**, so the approver decides the requisition with its vendor known: changing the vendor after approval voids the approval. |
| FR-PRO-011/016 | `fix.procurement.rfq`: `invited_vendor_ids`, `response_deadline`. **Opening needs invitations and a deadline that has not passed.** Only an invited supplier can bid, and only before the deadline. While the RFQ is open, suppliers can be added but **never removed**, and the deadline can only be extended. Both are fixed after close. |
| FR-PRO-012/013 | `fix.procurement.bid`: `warranty_months`, `moq`, `payment_terms`, `incoterm`, `quote_file` (+ filename), computed `total_price`. All are **sealed with the price** once the RFQ closes. |
| FR-PRO-017 | `fix.purchase.order`: `payment_terms`, `incoterm`. Both are pinned with the order's other terms: a change after approval voids it, and after sending one is refused (change order). They are carried from the award's bid and onto a change order. |
| FR-PRO-026 | `fix.purchase.receipt.line`: `condition` (good / damaged / wrong item / short / excess), `discrepancy_note`. A line not in good condition cannot be posted without its note. |
| FR-PRO-037, BRU-PRO-19 | **`fix.purchase.service.entry`** (new). A goods receipt now **refuses** a service-product line, or any line of a non-stock / service requisition. Only a confirmed service entry can receive one. The entry: <ul><li>is confirmed by the **requester** of the purchase (never its buyer, SOD-02). A PO on a no-requisition exception is confirmed by a Procurement Approver;</li><li>needs evidence or a description;</li><li>is bounded by the ordered quantity;</li><li>on confirmation posts the receipt (receiver = the confirmer, no inspection), which the **three-way match reads**;</li><li>is final once confirmed.</li></ul> |

Security: ACLs; the generated company / operating-unit isolation rules; sequences APSRC / SRVE. Any employee may create and confirm a service entry (as for a requisition), but `action_confirm` refuses anyone except the requester. This is recorded as the second `EMPLOYEE_WRITABLE` exception in `test_a06_control_suite.py`.

### Workspace: `static/src/a06/m16.js`, engine, server

| Page | Now offers |
|---|---|
| 1, 2 | The requisition form is now **3 tabs** (it passed 15 fields): Request · Source & Budget · Requester & Status. The list shows the demand source and what is bought. |
| 4 | Chip **Approved Source** + new list **Approved Sources** (Approve by a second approver, Withdraw with reason). The RFQ and Consolidated RFQ forms require Invited Suppliers and Response Deadline. The RFQ list has **Invite Approved Sources**. The bid form has the five terms + quotation upload. Bid Comparison shows total, lead time, warranty, MOQ, payment terms, incoterm. |
| 5 | The local PO has payment terms + incoterm. The import PO **requires** an incoterm. |
| 6 | Blanket list: **Raise Call-Off PO** on an active agreement. It opens the PO form with the blanket and its vendor filled in. |
| 8 | Receipt grid: Condition + Discrepancy. Chip **Service Entry** + new list **Service Entries** (Confirm Delivery, Cancel). |
| 9 | Chips **Match Exception Case** and **Match Tolerance** (M52's own forms) + list **Match Exception Cases (M52)**. |

- **Engine** (`p03_workspace.js` `mlAction`): a row action that opens a form may now declare `carry: {formField: rowColumn}`. It copies more of the selected row onto the new record. It is the only engine change and is additive.
- **Server** (`controllers/a06/m16.py`): surfaces for the two new models and the RFQ invite action. `writable.py` was regenerated (`form_fields.py --a06`).

## 5. Evidence

| Check | Result |
|---|---|
| `cd_p03_portal/tests/test_m16_capture_pass2.py` (node over the registry + server maps + a model check that every form field exists and no form omits a required field) | 11/11; **9 of the 10 static tests fail on HEAD** (the 10th, "every page still captures", is a regression guard that passes on both) |
| `cd_requisition/tests/test_m16_capture_pass2.py` (ORM, non-admin users, rolled back) | 20/20 |
| Mutation check: each new guard disabled in turn (approver SoD, open-needs-invitations, bid deadline, invited-only bids, invitations never withdrawn, receipts refuse service lines, requester confirms, discrepancy note, award carries terms, source terms fixed) | **10/10 mutants turn a test red** |
| Regression, cd_requisition (whole suite) | all pass except `test_m16_R03_cfo_tier_holder_approves_via_inbox`: environmental. In this clone (and in fix_test_m15c2 / m13c2), admin holds `group_dofa_tier_4`, so the CFO tier routes to admin too. Approval routing is untouched here. Three pass-1 consolidation tests first failed because a peer added one-legal-entity-per-company (`fix_entity_company_unique`). Their fixture now reuses the company's entity, and they pass. |
| Regression, portal: A06 control suite, A06 final M16, M16 pass 1 + pass 2, doc reports | all pass after 3 fixture updates. `test_a3`: the second bidder is invited. `test_a6`: skips client-only `__` form actions. A06 control suite: the service entry is the second documented employee-writable model. |
| Regression, dependents touching PO / receipt / requisition / RFQ: cd_inventory (M15 controls, final, handoffs, M16 bridges, RTV credit), cd_import_order (M44 final, controls, proforma), cd_demand_plan (M43 final, controls), cd_vendor_portal (M42 final, controls, residency), cd_ap_ext (M16 match, ORM, supplier advance) | all pass except 2 `TestExpenseClaim` tests in `cd_ap_ext/test_ap_ext_orm.py` (expense claims, not touched here) |
| Upgrade `-u cd_requisition,cd_p03_portal` on a private clone `fix_test_m16c2` | exit 0, 151 modules, no errors |
| Headless walk on a private server (port 8196, the clone; never 8069/8090), via the workspace's own `p03:open` hook | 7 lists open with their buttons: Approved Sources (+ New, Approve, Withdraw), Service Entries (+ New, Confirm Delivery), Match Exception Cases, RFQ Events (Invite Approved Sources), Bid Comparison, Blanket (**Raise Call-Off PO**), Requisitions. 7 forms render every new field: the requisition's 3 tabs with Demand Source / Source Reference / What Is Bought / Budget Reference; the bid's five terms and quotation upload; the RFQ's Invited Suppliers and Response Deadline; the PO's payment terms and incoterm; the service entry with its evidence upload. The only browser errors were 500s on asset files missing from the clone's filestore (an artefact of cloning the DB without its files). |

Existing fixtures that opened an RFQ with no invitation were updated to invite suppliers and set a deadline. These were `test_a06_m16_controls._rfq/_bid`, `test_procurement_ops`, and `test_a06_final_m16`'s `rfq` fixture: the rule they now meet is the one this pass adds.

## 6. Not built: needs an owner decision or another module's owner

| Spec | Gap | Why not here |
|---|---|---|
| BRU-PRO-08, FR-PRO-032 | A **documented match override** approved by the Finance Manager | M52's 17 Nov audit decided "there is no override of the match": a case closes only when its cause is fixed. That conflicts with BRU-PRO-08. **The CFO must choose** before either side builds it. |
| §8.2 | RTV states RMA-requested / RMA-issued / awaiting-credit / escalated, and credit ageing (FR-PRO-034) | The RTV is M15's `fix.stock.rtv` (draft → submitted → approved → shipped → credited); M16 records its RMA ref and credit. Changing its lifecycle is M15's call. |
| FR-PRO-011 | A gate that **invitees are M42-qualified** at invitation time | The award already refuses an inactive supplier (BRU-PRO-02). Gating invitations as well would block inviting a supplier mid-qualification; owner's choice. |
| FR-PRO-005 (P2), FR-PRO-015 (P2) | Budget check against M54; reverse auction | P2 |
| §10.1 | `fix.spend.category` taxonomy with a competitive threshold per category | The threshold is one parameter today (`cd_requisition.rfq_competitive_threshold`); a taxonomy is a design decision. |

## 7. Deployment state

- **Branch** `fix/m16-capture-pass2`: `ae3ad759` (code), `d0036d88` (fixtures), plus this report.
- **Deploy needs** `-u cd_requisition,cd_p03_portal` on fix_real and fix_dev, then one restart of 8069 and 8090.
  - New models, fields, ACLs, rules and sequences need the `-u`.
  - The new server surfaces need the restart (controllers load at start).
  - The JS reaches the browser with the `-u`'s asset rebuild.
  - The M18 session has asked to run one combined `-u` / restart with its `cd_ewaste`.
- **Data effect** (read-only count, 19 Nov): fix_real holds 0 requisitions, 0 POs and 0 RFQs; fix_dev holds 0 requisitions, 1 PO and 1 draft RFQ. No service-type PO line exists on either. Existing rows take the defaults (Demand Source = Branch Request, What Is Bought = Stock). The one draft RFQ on fix_dev will need its suppliers and deadline before it opens.

### Deployed 19 Nov 2026 (owner said "Yes, deploy now")

- **Landed and pushed:** fix/a03-live-data-and-pending-work at `4e492171` (code `969bdb6f`, fixtures `b7fd9a5f`, this report), plus branch `fix/m16-capture-pass2`.
- **Backups:** `1000 fix/backups/fix_{real,dev}_pre_m16_capture2_2026-11-19.dump`.
- **Upgrade:** `-u cd_requisition,cd_p03_portal` on fix_real, then fix_dev; exit 0 on both. The other sessions deploying that morning (M13, M15, M18, M21) were told and held their own upgrades until it finished.
- **Restart:** one restart for the whole deploy wave, done by the M21 session after its combined `-u` at 08:06:51. 8069 = PID 81988 (fix_real), 8090 = PID 21792 (fix_dev), both started after this upgrade.
- **Verified live:**
  - `cd_requisition` 19.0.1.1.0 on both DBs, with the 2 new tables, 5 new columns and 4 access rules.
  - The served `web.assets_web` bundle (`17a52539…`) carries the new forms, `__call_off` and the engine `carry`.
- **Signed-in, read-only walk** (headless browser, dev login, `fixreal.localhost:8069` / `fixdev.localhost:8090`):
  - 7 lists render with their new buttons: Approved Sources, Service Entries, Match Exception Cases, Invite Approved Sources, Raise Call-Off PO.
  - 7 forms render every new field, including the requisition's 3 tabs.
  - fix_real: 0 browser errors. fix_dev: the local PO form needed a longer load wait, then showed all its fields.
  - No server-log errors involve M16 models.

