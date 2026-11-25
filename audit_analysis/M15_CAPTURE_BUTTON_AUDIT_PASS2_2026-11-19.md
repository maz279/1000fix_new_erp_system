# M15 Spare Parts & Inventory: data-capture audit, pass 2

**Date:** 19 Nov 2026 · **Branch:** `fix/m15-capture-pass2` · **Status:** landed, pushed and live on fix_real (8069) and fix_dev (8090) since 19 Nov 08:06 (see §8)

## 1. The question

The user again saw M15 sub-module pages without a relevant data-capture button. The first pass, on 13 Nov (`M15_CAPTURE_BUTTON_AUDIT_2026-11-13.md`), gave every page that needed one a "+ New" or a form chip. This pass asks a stricter question: **can each page record what the spec says a person records there?** A button that opens the wrong record does not count.

## 2. Method

1. Read the module spec, `1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md`:
   - FR-INV-001…054;
   - §8 lifecycles;
   - §9 BRU-INV-01…24;
   - §10 entities;
   - §11 AUT-INV-01…18;
   - §13 roles and segregation of duties.

   The nav registry (`contracts/nav/registry.json`) gives only the 13 page names and their function counts. The spec is the yardstick.
2. Mapped every FR to its page (§5 below), and for each one asked: is it a record a person enters, or something the system writes or calculates?
3. For each "person enters" FR, read the code to see what exists: the `cd_inventory` models, the `cd_p03_portal` workspace (`static/src/a06/m15.js`), the served surfaces (`controllers/a06/m15.py`), and the write whitelist.
4. Checked the peer modules that might already cover a gap:
   - M14 `fix.tradein.harvest` raises a draft M15 goods receipt;
   - M09 `fix.warranty.recall` is a device campaign;
   - M37 `fix.service.kit` is a catalogue kit;
   - M01, M02 and M31 part lines issue stock but never reserve it.

## 3. Findings

| # | Page | Button before | What the spec says a person records there | Verdict |
|---|---|---|---|---|
| 1 | On-Hand & Classes | none | nothing: the ledger position | correct |
| 2 | Location Hierarchy | + New Stock Location | a location | correct (see §7 for the missing fields) |
| 3 | Ownership Segregation | + New Ownership-Class Change | a class change (FR-018), **and the per-brand consignment statement reconciled to the brand's own figures (FR-012, FR-014, AUT-INV-07)** | **gap: no consignment balance or statement anywhere** |
| 4 | Reservations | **none** | **a reservation held for a job, with priority, expiry and emergency override (FR-019…021, 027; BRU-INV-17…19; AUT-INV-01 fallback "manual reservation task")** | **gap: a reservation was only a number on the on-hand row, written by M41 wave release, recording no job, no priority and no expiry** |
| 5 | Issue / Return / Consumption | + New Stock Issue | an issue (FR-022); **a backorder when the part is not at hand (FR-025, AUT-INV-02)** | **gap: no backorder. An issue also could not draw the stock reserved for its job** |
| 6 | Van Stock | + New Van Reconciliation; Reorder Rule chip | reconciliation and par levels; **van-to-van transfer (FR-033)** | **minor gap: the transfer form handles van to van, but the page offered no chip for it** |
| 7 | Serial & Lot Trace | none | serials come from receipts (correct), **but a recall: quarantine every affected unit across all locations and vans in one transaction and list the jobs already consuming it (FR-040, AUT-INV-14)** | **gap: no recall. The M09 recall never touches stock** |
| 8 | Valuation | none | nothing: calculated | correct |
| 9 | Goods Receipt | + Goods Receipt | a receipt with the inspection gate | correct. Customer-supplied parts (FR-015) are held to the customer's job through the receipt partner |
| 10 | Counting | + New Cycle Count | a count | correct |
| 11 | Ageing & Analysis | none | nothing: calculated | correct |
| 12 | Transfers & RTV | Transfer, Scrap, RTV | the same three | correct. Harvest (FR-053) now arrives as an M14 goods receipt |
| 13 | Item Master | + New Item Master | the item master | correct |

## 4. What was built

### Records (cd_inventory 19.0.1.3.0 → 19.0.1.4.0, `models/fix_m15_capture.py`, imported last)

| Page | Record | Controls |
|---|---|---|
| 4 | `fix.stock.reservation` | Reserves through the ledger's own `_fix_reserve`, so only unrestricted, unreserved stock can be held. The class rule runs at reservation as at issue (FR-INV-011, BRU-INV-01/03/04), and quarantine or scrap stock is refused (BRU-INV-08). **Priority is computed from the job** (BRU-INV-17): warranty, AMC, rework or SLA-bound work ranks above paid work, which ranks above internal demand. A higher-priority job takes stock from lower-priority holds, and their requesters are notified. **Emergency override** (BRU-INV-19) needs an Inventory Controller or Branch Manager plus a written reason, notifies the displaced requester, and is reported on the list (*Emergency Override Of*). **Expiry** (BRU-INV-18) is an hourly cron; validity comes from `cd_inventory.reservation_validity_hours` (default 72). Release is limited to the requester or a controller. A held reservation is fixed; state and audit fields are guarded. Events `stock.reserved` and `stock.reservation_released`. |
| 5 | issue `reservation_id` | An issue may name the job's reservation. The part, location, class and job must match, and the issue unreserves exactly what it takes. Another job's hold can be taken only by an override. |
| 5 | `fix.stock.backorder` | Refused when the location can supply the quantity ("reserve it instead"). The network source is computed (AUT-INV-02). **Raise Transfer** creates the transfer request. **Raise Requisition** creates the M16 requisition, but only when no location can supply the part, so a branch never buys what another holds. **Fulfil** reserves the arrived stock for the job. Cancel needs a reason. Event `stock.stockout`. |
| 7 | `fix.stock.recall` | Scope is every unit of the part, or named serials. **Execute** (Inventory Controller) releases the reservations holding the part, then quarantines every unrestricted bucket or serial at every location and van in one transaction, through `fix.stock.quarantine`. What it cannot reach (in transit, issued, in warehouse bins, held by a wave pick) goes on a **manual sweep worklist**. It lists the **jobs already consuming it** (FR-040), and a counterfeit recall quarantines as *suspect*. Event `stock.quarantined`. |
| 3 | `fix.consignment.reconciliation` + `.line` | **Compute from Ledger**, per brand part: closing consignment stock now, plus received (posted consignment receipts), consumed on warranty and damaged/written off since the period start. The opening carries from the last acknowledged statement, and a period overlapping it is refused. "Other movements" is the balancing figure. **Send to Brand**, then enter the brand's closing figure per line. **Record Brand Acknowledgement** needs an Inventory Controller who did not prepare it, the brand's statement reference, signatory and date, and an explanation for any variance. Figures come only from the ledger. Event `stock.consignment_reconciled`. |

The supporting pieces:

- sequences RSV, BKO, RCL and CSR;
- ACLs (storekeeper and controller write; plain employees read);
- company and operating-unit record rules;
- 5 event schemas in `contracts/events/`.

### Workspace (`cd_p03_portal`)

- Page 3: **Consignment Statement** chip, plus the *Brand Consignment Statements* list (Compute / Send / Acknowledge).
- Page 4: **+ New Stock Reservation** and chip, plus the *Reservations* list (Reserve / Release).
- Page 5: **Backorder** chip, plus the *Backorders (Parts Wait)* list. The Stock Issue form gains *From Reservation*.
- Page 6: **Transfer Request** chip (van to van, FR-033).
- Page 7: **+ New Stock Recall** and chip, plus the *Recalls* list. The serial list stays read-only.
- 5 served surfaces in `controllers/a06/m15.py`; `writable.py` regenerated by `form_fields.py --a06`. Only the new models changed.

## 5. Evidence

| Check | Result |
|---|---|
| `cd_inventory/tests/test_m15_capture_pass2.py` (new; non-admin users with real roles, rolled back) | **18/18** |
| `cd_p03_portal/tests/test_m15_submodule_capture.py` (updated; the engine's own `fregCreate`/`fregPanels` in node) | **27/27** |
| Mutation check: each of 22 server controls and 5 workspace wirings disabled in turn, in a throwaway worktree | **27/27 red**. The first run had one survivor: a hold could bump an *equal*-priority hold. A test for two warranty jobs competing was added, and that mutant is now red. |
| Regression: every M15 suite in `cd_inventory` (not the M41 warehouse suites, which this change does not touch), the M01/M02/M31 issue bridges, and the portal registry, whitelist and page-standard checks | **1,078 tests: 1,058 pass, 1 fail, 19 error. All 20 reproduce identically on the base commit fdc8fef7 against the same DB, so none is from this change.** `test_s0_duplicate_baseline…` fails on the clone's suspense baseline. The 19 bridge tests stop in their fixture on `fix_entity_company_unique`, because the `fix_dev` clone already has the company entity. The override changes nothing when no reservation is named. The issue path itself is covered by `test_a06_m15_controls`, which passes. |
| Live walk on a private server (port 8115, worktree code, `fix_test_m15c2`; headless Chromium) | All 13 pages. Every "+ New" and every chip opens its form: Consignment Statement (2 tabs), Stock Reservation, Backorder, Transfer Request on p6, Stock Recall. **0 load errors, 0 console errors.** |
| Endpoint round trip, as the form does it (`/p03/model/write` then `/p03/model/action`) | Saved RSV/2026/00134 and ran Reserve: state *Held*, priority *Internal*, expiry +72 h; ledger 5 on hand, 2 reserved, 3 available. A direct `state` write is refused ("changes only through its workflow action"). Over-reserving is refused with the rule's message pointing to a backorder or an override. |

The private test DB `fix_test_m15c2` was cloned from `fix_dev` and upgraded with `-u cd_inventory,cd_p03_portal`: 0 errors, 151 modules.

## 6. What was not built, and why

- **Automatic reservation when M01/M02/M31 raise a parts requisition (FR-INV-019 "automatically", AUT-INV-01).** There is no parts-requisition record in M01: a work-order part line *is* the consumption. The reservation record and `action_reserve` are the seam M01 calls once it has one. This is an M01 build.
- **Kit issue (FR-INV-026, P2) and substitution at issue (FR-INV-024, P1).** The catalogue has `fix.service.kit` but no supersession or alternate chain to validate against. Both need M37 data first.
- **Obsolescence provision raised to M19 (FR-INV-045, P2).** Ageing is reported; posting a provision is a finance decision (Q-06 provision bands are open).

## 7. Spec divergences found in passing (owner decisions, not capture gaps)

- **The ledger's six ownership classes are not the spec's six.** The code has owned / consignment / customer / van / bench / warranty. The spec has own commercial / brand consignment / customer-supplied / refurbished-harvested / rental pool / marketplace seller. "Van" and "bench" are locations in the spec, not owners. Refurbished stock is traced only by serial (the BRU-INV-03 check in the issue). Rental-pool and marketplace classes do not exist.
- **No immutable movement ledger** (`fix.stock.move`, T-03). Movements live on their documents, so the consignment statement's "other movements" is a balancing figure, not a list.
- **Location master** (FR-INV-002): there is no accountable role and no permitted ownership-class set on `fix.stock.location`.
- **`fix_dev` data integrity** (found while cloning): 162 orphan rows sit behind 13 foreign keys that `fix_dev` still declares. The largest are 106 in `account_account_res_company_rel` and 46 in `account_fiscal_position_account_tax_rel`; the others are in SLA KPI instances, device-part compatibility, intercompany rules and stock routes. A restore cannot recreate those keys. They were repaired on the private clone only.

## 8. State

**Landed and pushed** on 19 Nov: shared branch `fix/a03-live-data-and-pending-work` 565f7ee9..946c088f (fix b17cab7f, test caf0b12e, docs 946c088f). The feature branch `fix/m15-capture-pass2` is pushed as well.

**Deployed** on 19 Nov, with the owner's OK, as part of one combined deploy wave shared with M12, M14, M16, M17, M18, M20 and M21, so that 8069 and 8090 restarted only once:

- **Upgrade.** `cd_inventory` 19.0.1.3.0 → 19.0.1.4.0 reached fix_real and fix_dev through the M16 session's `-u cd_requisition,cd_p03_portal`, which cascaded into it (exit 0 on both). The M21 session then ran the remaining combined `-u` and did the single restart at 08:06:51. A final gap check found no module behind its code on either database.
- **Servers after the restart:** 8069 = PID 81988 (fix_real), 8090 = PID 21792 (fix_dev).

**Verified live, read-only, on both databases** (`scratchpad/m15_verify_live.py`, `m15_walk_ro.mjs`; nothing was written to either estate):

| Check | fix_real | fix_dev |
|---|---|---|
| `cd_inventory` installed | 19.0.1.4.0 | 19.0.1.4.0 |
| Tables for the 5 new models | all present | all present |
| ACLs / record rules | 3+2+2+2+2 / 2+2+1+1+1 | same |
| Sequences RSV, BKO, RCL, CSR | present | present |
| Parameter `reservation_validity_hours` | 72 | 72 |
| Expiry cron on the new process | ran 08:24, done, 0 errors | ran 08:27, done, 0 errors |
| Served bundle carries the 4 new forms | yes (17a52539) | yes (17a52539) |
| `/p03/model/records` serves the 4 new models | yes | yes |
| Headless walk: 13 pages, every "+ New" and chip opens its form | yes, 0 console errors | yes, 0 console errors |

**Log notes:**
- Both old processes logged `KeyError: 'fix.stock.reservation'` from the new cron. That happened between the `-u` and the restart, when the database already held the cron but the process had not loaded the model. It is gone after the restart.
- The only other ERROR line since the restart on 8069 is a `could not serialize access` on `ir_config_parameter`. Two logins collided, and Odoo retried successfully.

**Open:**
- Nobody has created a reservation, backorder, recall or statement on either estate yet; the lists are empty.
- The owner decisions in §6 and §7 are unchanged.
