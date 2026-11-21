# A06 Supply Chain — ERP audit and remediation (20–21 Nov 2026)

Branch `fix/a06-erp-audit`; ledger `A06_ERP_AUDIT_LEDGER_2026-11-20.md`; builder brief `A06_ERP_BUILDER_BRIEF.md`.

Scope: M15 Spare Parts & Inventory, M41 Warehouse, M16 Procurement, M42 Supplier Relationship,
M43 Demand Planning, M44 Import & Landed Cost, and their hand-offs to finance (M19 GL, M52 AP,
M50 treasury, M51 VAT), A02 service jobs (M01/M02/M31 part issue), M14 refurbishment, M37
catalogue, M38 storefront, M63 approvals and the A07 asset registers.
(cd_consignment is M03 / A02 and was audited by the A02 session; only the M15 hand-off is here.)
Branch `fix/a06-erp-audit` (worktree `1000 fix/a06erp-wt`), base d0589b7b.

## How it was checked
- Five read-only audits (M15, M41, M16+M42, M43+M44, and one cross-cutting audit of money-to-ledger
  and cross-area hand-offs) against the six specs, with SELECT-only SQL on a copy of fix_real.
  ≈200 findings (6 P0), each with file:line evidence; the lead re-checked the P0s in the code.
- Eight owner decisions (D1-D8, below), all taken as recommended.
- Five builder streams, each in its own worktree with its own test DB and fix_real copy; every fix
  has an ORM test; each stream ran a mutation check (defect re-introduced -> a test goes red):
  LEDGER 20/20, M15 29/29, M41 33/33, M43/M44 7/7, P2P 48/48, integration 3/3.
- Integration on `fix/a06-erp-audit`: the streams merged, cross-stream defects fixed (below), then
  an end-to-end probe on a fix_real copy and a chunked regression.

## What was wrong — headline defects (fixed)
1. **Stock never reached the general ledger (P0).** Every movement only wrote a row to a holding
   account (110999) for a month-end journal someone would type; fix_real's BDT 165.26M of stock
   showed 0 in the GL. Now (D1) every receipt, issue to a job, return, transfer between branches,
   count difference, write-off, RTV and price variance posts its own balanced journal at the moment
   it happens, on the legacy chart (D2): stock by brand (Samsung 100506, Xiaomi 100508, Huawei
   100509, Whirlpool 100511, others 100502), received-not-billed 100503, parts cost 600002,
   count/write-off 500905, price variance 600007 — each line at the stock's own branch OU.
   Take-on (D4) proven on the fix_real copy: 28 entries (one per OU), BDT 165,260,650.54; the new
   Stock-to-GL Tie-out report shows subledger = GL to the paisa.
2. **A purchase order's goods could be received twice (P0)**: a manual M15 receipt against a PO was
   invisible to M16, so the M16 receipt took the goods in again. Receipts against a PO now come only
   through M16's goods receipt.
3. **USD vendor bills were booked as taka (P0)**: USD 100 posted BDT 100; approval bands, TDS and
   VDS were computed on the USD figure. (P2P stream: full FX, D5.)
4. **The warehouse could ship stock with no document behind it (P0)**: a wave line or cross-dock of
   manual/job/refurb demand wrote the stock off as a "shipment". Nothing leaves the warehouse now
   without an M15 transfer, RTV or job issue.
5. **Received-not-billed never cleared**: local receipts credited nothing, the bill debited
   GRNI for everything (services included). Now the receipt credits 100503 and the bill clears it
   at the received value, price difference to 600007, rate difference to 500030.
6. **Imports**: an LC payment and the supplier's bill could both be paid (D6: the LC payment now
   settles the bill, or is an advance on 10255 that the bill applies); variance account 610000 did
   not exist (now 600007); customs was credited with the computed, not the assessed, figure; duty was
   spread by value instead of each line's own HS duty; CIF/CFR assessable value left out freight
   and insurance; serialised imported parts could never be received.
7. **Replenishment ordered twice** (M43 plan and M15 sweep both raised requisitions) and bought
   from suppliers what a van or branch should get from the warehouse (D7: one engine; vans and
   branches by transfer). Safety stock now includes lead-time variability.
8. **Controls**: quarantine release by anyone (now Quality Manager / Inventory Controller); returns
   of parts from closed, invoiced jobs; warranty jobs drawing non-warranty stock (D3); counts
   double-counting movements made between count and approval; count losses breaking reservations
   and stopping the expiry job; van reconciliation by total pieces only; transfers across companies;
   operators arming automatic wave release, re-pointing bins to other ledger locations, editing
   handling-equipment requirements; put-away override bypass; sealed-bid / screening / requester
   segregation gaps; payments to sanctioned suppliers; non-PO bills buying stock parts.
9. **Data**: 4,863 stock buckets (BDT 38.4M) stamped with the main OU instead of their branch's,
   hiding stock from branch users (repaired by migration); the receiving branch could not see a
   transfer addressed to it.
10. **Reports and KPIs**: date ranges and Dhaka dates on every A06 report; ageing that works without
    lots; stock-out KPI on real minimums (14,011 of 16,178 parts "out" was the default min 5);
    honest pick accuracy; seven new M41 reports including slot-vs-ledger reconciliation; new M15
    registers; WAPE/bias/fill rate in M43.

## Integration (lead) — cross-stream defects found only after merging
- Imports posted their own journals to the retired 110999: now each part's brand stock account at
  the receiving/holding branch, with M15's rows linked to the import's entry (never posted twice);
  a later serial receipt links to the import's goods entry. Probe: 0 import lines on 110999.
- Two transfer posting paths (LEDGER hook and M15 rows): one path in a real-time company.
- Two uncosted-issue controls (X19): one control — a controller's approval of the issue or an
  approved release, either honoured by the other check.
- Import entries dated in UTC, stock entries in Dhaka: a receipt between 00:00 and 06:00 Dhaka would
  have split across two periods. Import entries now take the Dhaka business date.
- Stock-to-GL tie-out flagged a 2-paisa unit-cost rounding as a break: GL vs subledger stays exact;
  subledger vs qty x unit cost now has a provable rounding bound (tested both ways).
- The item master and its standard-cost action move from M41 to M15 (no cost in M41).
- Tests that encoded replaced behaviour updated (A02 d11 return-after-delivery, A36 van custodian).


## Verification (21 Nov 2026, merged branch incl. A02 pass 2, A04 and A07)
- Full chunked regression on a test-template copy upgraded with the 54 changed modules: inventory 590/0,
  imports 241/0, demand planning 150/0, GL 341/0, AP 235/0, requisition + supplier portal 394/0,
  A06 workspace screens 916/0, A07 money and fixed-asset suites 216/0. A02 links 757/762: the five
  failures are an A02 pass-2 field-cash defect (a cd_front_desk method needs a `reference` that the
  new cd_field_service caller does not pass, harmless where cd_front_desk_finance is installed, i.e.
  fix_real and fix_dev), reported to and fixed by the A02 session.
- On a fix_real copy: ledger, counter/storefront parts-cost and M44 suites 53/53; import probe: 0 import
  lines on 110999, receipt and landed-cost rows linked to the import's own entries, GL = stock subledger
  to the paisa after take-on + a USD LC import.
- Deploy rehearsal on a fresh fix_real copy: -u 0 errors (200 s); data script idempotent; take-on 12,776
  rows, BDT 165,260,650.54; tie-out subledger = on-hand = GL; 658 suppliers reset; D8 limits set.

## Cross-area defects found during integration (fixed)
- A07 rent / garage / fit-out bills were refused by the new non-PO supplier rule (P09): a bill backed
  line by line by an approved A07 source document needs no M42 register entry (audit O6).
- GR/IR had lost its "invoiced, not received" side in the P2P rewrite: restored on the posted basis.
- M16 goods that are not spare parts left GRNI debited by the bill and never credited: accrued at receipt.
- Cost-document bills compared against base BDT instead of the company currency.
- M43 converted to base BDT instead of the company currency.
- AP users could not open a bill (no read on its LC advance take-backs).
- Foreign import supplier bills withheld TDS/VDS already collected at customs.

## Owner decisions (20 Nov 2026, all the recommended option)
D1 real-time stock posting; D2 legacy account map; D3 brand warranty parts company-owned, warranty
jobs from warranty stores; D4 stock take-on, zero-cost lines to Finance; D5 full FX; D6 LC settles
the bill, accounts 10255/100812/100302/500030/600007, BDT 10 customs tolerance; D7 one replenishment
engine, vans/branches by transfer; D8 limits (count 2%, van 1%, transfer > BDT 50,000, write-off >
BDT 5,000, AP match +2%/+BDT 500, 3 quotes > BDT 50,000, emergency BDT 25,000).
21 Nov: 658 cut-over suppliers reset to prospect; forecast window 12 months / minimum history 6;
Redmi valued with Xiaomi (100508); 100510 cooler parts left unmapped. A02 (relayed): each workshop has
a non-warranty and a warranty store (fix_real W0003 / WARRANTY-HO, fix_dev HO-NWT / HO-WTY).

## Still open (needs a business figure or decision)
- 4,685 stock lines (fix_real) carry zero cost: Finance prices them (Finance tool built).
- Graded (refurbished) stock accounts `cd_inventory.account_code.graded_stock/graded_intake`.
- LCA coverage: top-up or replacement LCAs.
- 0 Procurement Managers are appointed; the 658 prospect suppliers are onboarded in waves (documents,
  screening, qualification with approved categories) before POs can be sent to them.
- W0001: lay out zones/bins, then load opening slots (tool built).
- Deferred features (listed in the ledger): Croston/seasonal forecasting, portal RFQ bidding,
  multi-line requisitions with UoM, automatic put-away, per-category scorecard weights.

## Deploy record
(to be completed at deploy)
