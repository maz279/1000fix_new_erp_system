# A06 Supply Chain ERP audit - findings ledger (20 Nov 2026)

Branch `fix/a06-erp-audit` (worktree `1000 fix/a06erp-wt`), base d0589b7b.
Scope: M15 Spare Parts & Inventory, M41 Warehouse, M16 Procurement, M42 Supplier Relationship,
M43 Demand Planning, M44 Import & Landed Cost, plus their money-to-ledger and cross-area hand-offs.
(cd_consignment is M03 / A02 and was audited by the A02 session; only the M15 hand-off is here.)
Method: five read-only auditors (code trace + SELECT-only SQL on a copy of fix_real), lead spot-checks,
then builder streams with executable tests and mutation checks.

Status per id: OPEN / FIXED (test) / VERIFIED-LIVE / OWNER / NOT-A-DEFECT / DEFERRED.

## Owner decisions (20 Nov 2026, all the recommended option)
| id | decision |
|---|---|
| D1 | Inventory posts each movement to the GL as it happens (perpetual). The 110999 suspense stub is retired. |
| D2 | Account map (legacy chart): stock by brand Samsung 100506, Xiaomi 100508, Huawei 100509, Cooler parts 100510, Whirlpool 100511, others 100502; received-not-billed 100503 Stock Incoming; parts cost on jobs/sales 600002; count losses/gains and write-offs 500905; price variance 600007. |
| D3 | Brand warranty parts are company-owned stock (valued on the brand stock accounts); warranty jobs draw only from warranty stores, non-warranty jobs only from non-warranty stores. |
| D4 | Post the stock take-on (current qty x cost) Dr stock accounts / Cr 300101; give Finance the zero-cost lines (4,685); zero-cost stock cannot be counted/issued/written off without approval until priced. |
| D5 | Full FX: PO stamps its rate at approval; bids compared in BDT; bills post amount_currency with BDT; receipt-vs-bill rate difference to 500030; approval bands, TDS, VDS in BDT. |
| D6 | Imports: an LC payment settles the supplier's AP bill directly (before the bill: advance on 10255 Advance for Purchase); LC margin 100812; customs duty paid 100302 Deposits - Customs; FX 500030; duty and landed-cost variance 600007; customs-rounding tolerance BDT 10 per Bill of Entry. |
| D7 | One replenishment engine: M43 sets min/max (safety stock with lead-time variability); M15's sweep is the only document raiser and nets on-order and in-transit; vans/branches below min get a transfer from their parent warehouse; only warehouses buy. |
| D8 | Limits: count tolerance 2%, van 1%, transfer approval above BDT 50,000, write-off approval above BDT 5,000; AP match price +2% or +BDT 500, qty 0%; three quotes above BDT 50,000; emergency purchase ceiling BDT 25,000. |

Defaults taken by the lead (controls with one sensible answer; reversible settings):
quarantine release by Quality Manager or Inventory Controller; deactivated (sanctioned) suppliers are not paid;
non-PO bills cannot buy stock parts; transfers across companies are refused; W0001 stays switched on and gets an
opening-slot load with no ledger effect; RF devices must be issued to a named operative; manual/job/refurb
warehouse demand leaves only through an M15 document (transfer/consumption); posting cut-off is the Dhaka date.


---

## A06 money-to-ledger + cross-area auditor findings (20 Nov 2026) - saved by lead
P0 2, P1 9, P2 23, P3 3. Paths rel. addons.
Today: every M15 movement writes one fix.inventory.valuation.suspense row (_fix_post fix_valuation_suspense.py:270-294) on 110999, no counter-account. Only M44 import posts real-time. Period close: a person types one cutover journal; system checks it moves 110999 by net (fix_gl_ext.py:594-700).

| id | sev | finding | evidence | fix |
|---|---|---|---|---|
| X01 | P0 | no account determination: receipts, COGS/job cost, count +/-, scrap, shipments, class change, sale cost net into one suspense figure; GRNI/COGS 600002/write-off 500905/brand stock accts never derived | fix_valuation_suspense.py:44-58, 270-294; fix_gl_ext.py:640-700; cd_gl_ext test_gl_ext_orm.py:539 | posting-rule table entry_type x class -> Dr/Cr; real-time |
| X02 | P0 | fix_real on-hand BDT 165,260,650.54 owned; 0 GL on 1005xx/110999; 0 suspense rows -> GL inventory 0 | SQL | OWNER take-on Dr stock / Cr 300101 + initial rows reconciled |
| X03 | P1 | local PO receipt never credits GRNI; bill debits 100503 at bill price; PPV/FX stay in GRNI; import path does credit | fix_purchase_receipt.py:137-202; fix_stock_bridges.py:259-330; fix_ap_ext.py:986-1021; fix_import_order.py:425-436 | |
| X04 | P1 | suspense cutover no date cut-off; close refuses while any row pending -> live estate can never close | fix_gl_ext.py:556-585, 609-613 | |
| X05 | P2 | w/o PPV legs cutover check uses abs() -> wrong direction passes | fix_gl_ext.py:669-671 | |
| X06 | P2 | suspense balances shown to Finance are unsigned raw sums | p03_gl_api.py:769-775; fix_gl_ext.py:717, 560-568; fix_valuation_suspense.py:447 | |
| X07 | P2 | OU dimension lost at cutover | | |
| X08 | P1 | landed accrual 201279 never relieved; fix.import.cost no AP bill link -> C&F/freight bills expensed in AP AND capitalised | fix_import_capture.py:73-160; fix_import_ops.py:3024-3030 | |
| X09 | P1 | LC payment Dr lc_clearing, nothing credits; AP not LC aware -> supplier bill payable twice; params unset | fix_import_ops.py:968-985 | |
| X10 | P1 | import variance 610000 not in chart | fix_import_ops.py:3015-3022, 2304-2313 | |
| X11 | P1 | import w/o PO: receipt credits GRNI, bill debits expense -> GRNI never clears, double counted | fix_import_order.py:69, 425-436; fix_ap_ext.py:993 | |
| X12 | P2 | landed split stock/consumed uses pooled bucket qty | fix_import_ops.py:2995-3001 | |
| X13 | P2 | import postings fall back to company's first OU; import OU optional | fix_import_common.py:246; fix_import_order.py:66 | |
| X14 | P2 | FX diff receipt vs bill stays in GRNI | | |
| X15 | P2 | BoE import VAT/AT never reach input-VAT register; 9.1 input VAT hand typed | fix_tax_returns.py:270-285 | |
| X16 | P1 | WMS ship of van/refurb/job/manual demand writes stock off as shipment; cross-dock same (= M41 F01) | fix_wms_ops.py:1005-1060; flow:360-420; spec:1204-1225 | |
| X17 | P1 | refurb graded stock off-ledger; cd_tradein posts no GL | fix_graded_stock.py:197-215; fix_storefront_books.py _sfb_issue | |
| X18 | P2 S | harvested parts enter at typed unit_value, no relief of trade-in unit cost | fix_tradein_ops.py:1086-1140 | |
| X19 | P1 | 4,685/17,461 buckets qty at zero cost: issues zero cost, WAC averaged down, count variance on them skips DOFA | fix_inventory_approval.py:268-273; fix_inventory_ops.py:1620-1630 vs 2252-2259 | |
| X20 | P2 | transfer can cross companies, no intercompany | fix_inventory_ops.py:957-1280 | |
| X21 | P2 | 4,863 buckets (BDT 38.4M) stamped Main OU while location is branch OU; OU rule hides from branch users | fix_isolation_rules.xml:99-102 | data repair |
| X22 | P2 | M15 issue cost never reaches field/work-order job lines; stock.consumed/returned no consumer; publish failure swallowed | fix_field_order_part.py:105-107; fix_work_order_part_m15.py:148-152; fix_stock_consumption.py:523-530 | |
| X23 | P2 | workshop line "Reserved in M15" holds nothing in M15 | fix_workshop_part_line.py:341-348; fix_workshop_part_line_p1p2.py:217-223 | |
| X24 | P2 latent | workshop with Odoo location consumes via stock.move skipping M15 | fix_workshop_part_line_m15.py:192 | |
| X25 | P2 S | capex PO part into M15 stock AND CWIP | fix_stock_bridges.py:259-330; m49_capex_bill.py:34-38 | |
| X26 | P2 | AP GRNI accrual not as-at, ignores RTVs/credit notes; M16 gr_ir report different basis; neither ties to GL | fix_ap_capture.py:181-215 | |
| X27 | P2 | lost/scrapped brand consignment books no liability/claim; not linked to M09 claim; core return free text | fix_m15_capture.py:1350-1465; fix_m09_capture.py:1897 | |
| X28 | P2 | A07 device-component Stock Lot picker targets stock.lot (0 rows) not fix.stock.lot | fix_maintenance_demand.py:116-138 | |
| X29 | P2 | no A06 report applies date range; no as-at valuation; no stock-vs-GL tie-out; Suspense Integrity reads pending only | | |
| X30 | P2 | ageing serial lots only (0) | | |
| X31 | P2 | M16 spend adds currencies; match_exceptions wrong | | |
| X32 | P3 | KPIs UTC; stockout means <=min; pick accuracy is fill rate; report key typo `ageeing` | | |
| X33 | P2 | 41/54 published A06 event types no consumer; cx_feedback.consume_goods_received not registered | money/events.txt | |
| X34 | P3 | GRNI role 100503 asset treated as liability | | |
| X35 | P2 | storefront shows no availability, reserves nothing at checkout | | |
| X36 | P3 | 95 locations + all parts no OU -> suspense rows no dimension | | |
| X37 | P2 | counter/storefront revenue immediate, COGS only at cutover | | |

OWNER: 1 account map (brand stock 100502/100506/100508.., COGS 600002, write-off 500905, P&L adj); 2 take-on BDT 165.26M + cost 4,685 zero buckets; 3 import variance 600007/new 600008; 4 LC clearing + FX acct w/ AP offset; 5 GRNI liability acct; 6 suspense cut-off Dhaka date; 7 refuse intercompany transfers; 8 consignment loss who pays; 9 write-off DOFA (controller max 25k, CFO unset, write-off/transfer 0); 10 cd_ap_ext.account_code.supplier_advance unset.

Checked OK: suspense protected; RTV PPV clears to 600007; non-owned not valued; WAC consistent; M16->M15 bridge; M44 PO import no double stock; import posts fail closed; landed final balances, BoE reversal; codes exist except 610000; AP payment block + payee bank; counter sale legs + refund; A02 close gate; part->product 16,178 unique; crons; exports exist for every A06 report; KPI company scope; write-off DOFA routing.

---

## M15 auditor findings (20 Nov 2026) - saved by lead
inv/ = addons/domain/e_supply_chain/cd_inventory/models/. P0 1, P1 10, P2 18, P3 9.

| id | sev | finding | evidence |
|---|---|---|---|
| A01 | P0 | manual M15 receipt vs PO invisible to M16 -> later M16 receipt receives again: stock+value doubled, vendor bills once; manual path skips receiver role, SOD-02, 3-way qty | inv/fix_inventory_ops.py:620, 643-679; cd_requisition/models/fix_purchase_receipt.py:156; fix_requisition.py:1652-1656; inv/fix_stock_bridges.py:320-326 |
| A02 | P1 | no stock event reaches GL with its accounts; every movement = one suspense 110999 row; close only checks a hand-posted journal moves 110999 by net; stub expiry 2026-11-30 | inv/fix_valuation_suspense.py:44-58, 340-346; cd_gl_ext/models/fix_gl_ext.py:615-703 |
| A03 | P1 | local PO receipts never credit GRNI (= M16 F05) | cd_ap_ext/models/fix_ap_ext.py:988-993; cd_import_order/models/fix_import_order.py:367 |
| A04 | P1 | counts: expected snapshotted at line create, diff applied to live ledger, no freeze -> movements counted twice; no full-count lockdown FR-INV-051 | inv/fix_inventory_ops.py:1822-1835, 1790-1794, 1688-1698 |
| A05 | P1 | count loss taken from reserved stock first -> reservations orphaned; release/expiry raises; hourly expiry cron no per-record savepoint -> one bad stops sweep | inv/fix_inventory_ops.py:316-327, 357-369, 1691-1698; inv/fix_m15_capture.py:254-263, 441-451 |
| A06 | P1 | job hand-offs (work order, field order, workshop, PO receiving) pick first of a branch's stores; HO has 63 stores -> warranty job draws non-warranty or fails | fix_work_order_part_m15.py:70-81; fix_field_order_part_m15.py:63-75; fix_workshop_part_line_m15.py:31-49; inv/fix_stock_bridges.py:237-246 |
| A07 | P1 | brand-consignment consumption never settled (no ownership transfer/settlement/payable/claim FR-INV-013 AUT-INV-06); scrap consignment raises nothing | inv/fix_stock_consumption.py:484-503 |
| A08 | P1 | job bridges pass no stock class, no reservation: warranty jobs can't use consignment; job's reservation not drawn, held 72h while issue takes other stock | bridges :108-121, :100-115, :127-143 |
| A09 | P1 | action_return_part no job-state/age/role check; workspace action; return from closed invoiced order recreates stock + reverses cost | inv/fix_stock_consumption.py:538-561; m15.py:29-33 |
| A10 | P1 | quarantine release no approval (rejected/counterfeit/recalled -> usable) | inv/fix_inventory_ops.py:2230-2247 |
| A11 | P1 | van recon compares total pieces per van only; no per-part, no value; nothing corrects ledger | inv/fix_inventory_ops.py:1925-1927, 1966-1973, 2024-2026 |
| A12 | P2 | fully rejected receipt line unrecordable (accepted>0); same person receive/inspect/post | :716-735 |
| A13 | P2 | PO receipt ownership class user-chosen -> purchased goods as consignment/customer, never valued | :513-520; writable.py |
| A14 | P2 | transfers/RTVs move only owned/van stock; consignment/warranty-reserve/customer can't transfer; unused consignment can't return to brand except via quarantine | :1051, 1187, 1219, 2750-2754 |
| A15 | P2 | class change any pair; customer property -> owned (BRU-INV-04) | :3010-3012, 3054-3082 |
| A16 | P2 | transfers book no valuation row (branch value wrong); inter-company transfer not stopped (3 companies) | :1170-1279 |
| A17 | P2 | transfers/RTVs no link to M03 consignments either way | |
| A18 | P2 | ownership classes != spec six; no owner/brand field; brand statement infers from part | |
| A19 | P2 | all 17,461 fix_real rows (BDT 165.26M) owned/unrestricted incl 88 warranty stores; warranty vs non-warranty only a location field nothing enforces | |
| A20 | P2 | no immutable stock-movement ledger FR-INV-005 | |
| A21 | P2 | FIFO refused; no provisional cost flag, dead-stock provision, ABC count scheduling | |
| A22 | P2 | reports ignore date range; ageing reads lots only (0 lots) -> empty; accuracy % counts hidden blind lines exact; 6 spec registers missing | |
| A23 | P2 | Stock-Out KPI 14,011/16,178 because default min 5 + all classes/statuses; KPI-042..047 not computed | |
| A24 | P2 | Network Availability limited to user's OU by record rule | |
| A25 | P2 | reorder ignores in-transit/on-order; van below par raises PR not transfer; rejected PR leaves rule "ordered" | |
| A26 | P2 | auto reservation + job parts-wait not built; no module creates reservations/backorders | |
| A27 | P2 | 8 published stock events no consumer (stock.consumed, stock.van_variance_detected) | |
| A28 | P2 | direct M15 issue skips job-state gate A02 bridges apply | |
| A29 | P2 | graded refurbished stock outside ledger/valuation; any user creates any cost | |
| A30 | P3 | consignment brand check compares legacy brand text; 358 parts disagree | |
| A31 | P3 | count lines no class column | |
| A32 | P3 | cutover check compares absolute values (wrong-direction journal passes) | |
| A33 | P3 | event publish failures swallowed in consumption | |
| A34 | P3 | cancel transfer/RTV + mark RTV credited no role check | |
| A35 | P3 | PO currency at today's rate not receipt date | |
| A36 | P3 | storekeeper creates van naming any custodian (check on write only) | |
| A37 | P3 | report dates UTC | |
| A38 | P3 S | transfer stamped sender OU may be invisible to receiving branch | |

OWNER: 1 brand-supplied warranty parts = consignment w/ brand owner, enforce warranty vs non-warranty at issue; 2 accounts per movement (inventory 100502 or per-brand 1005xx, GRNI 100503, COGS, write-off 500905, count variance), post each movement; 3 consignment settlement = one M52 obligation per consumption; 4 WAC only, amend spec; 5 thresholds (all 0): count 2%, van 1%, transfer 50k, write-off 5k, CFO max; 6 8,170 parts / 4,685 rows zero cost -> load costs; 7 remove default min 5/max 25; 8 receiving store on PO; 9 quarantine release by QM or Inventory Controller.

Checked OK: ledger refuses negative + taking reserved (code + DB constraint), whole-piece/serial, WAC on receipt; stock/lot/suspense read-only, guarded, undeletable; transfer SoD, in-transit stays sender's, partial receipt/discrepancy correct; counts blind, counter != approver, ladder 25k->CFO; zero-cost scrap approval; RTV tied to GR+bill, RMA, draft AP credit note, 600007/110999 exist; van issue custodian-only, discrepancy holds; reservation priority; brand statement 2-person; A02 close gate counts M15 issues; M44 import journal coherent with suspense cutover; all m15.js cols exist; SURFACES; crons + inspection-rejected consumer wired.

---

## M41 auditor findings (20 Nov 2026) - saved by lead
Paths relative to cd_inventory/models/ unless prefixed. P0 1, P1 10, P2 14, P3 7. All CONFIRMED by code trace.

W0001 (on, no bins) does NOT block M15: _fix_check_bins returns when nothing binned (fix_inventory_ops.py:228-230); approved transfer/RTV only queues demand, direct dispatch cancels it (fix_wms_ops_spec_flow.py:241-254, 336-346).
Slot sum vs on-hand: slots can exceed on-hand; nothing reconciles. Breaks F02 F03 F06 F08 F09 F10 F11.

| id | sev | finding | evidence | fix |
|---|---|---|---|---|
| F01 | P0 | shipping a wave line with no M15 transfer/RTV behind it (manual/job/refurb/typed) removes stock from ledger + posts "Warehouse Shipment" suspense row; every cross-dock dispatch same; destination receives nothing; with F05 one operator end to end | fix_wms_ops.py:1024-1036; fix_wms_ops_spec.py:1219-1222; flow:372-376; nothing consumes wh.shipped | refuse ship/cross-dock without M15 document; manual demand -> M15 transfer, job -> M15 consumption |
| F02 | P1 | put-away/cross-dock accept stock still in inspection (inspection-held PO receipts posted qty_accepted=qty_received); put-away never checks units still unslotted on-hand -> slots > on-hand -> _fix_check_bins blocks every M15 issue | fix_stock_bridges.py:296-298, 319-323; fix_wms_ops.py:524-552; fix_wms_ops_spec.py:109-128, 1173-1174; fix_inventory_ops.py:238-245 | refuse while inspection pending; cap at unrestricted - binned |
| F03 | P1 | every M41 ledger call books `owned`, bins accept consignment/customer/warranty receipts, release never checks class -> picking consignment reserves/ships/values owned | fix_wms_ops.py:730,784,917,1022,1694; spec.py:1626; flow:795; fix_wms_ops.py:569-575 | slot ownership class, used everywhere |
| F04 | P1 | override bypass: create put-away with bin and no receipt line (directive skipped), then write receipt line (write re-checks only to_bin_id) -> completes override_state none | spec.py:540-541,548-550,724; writable.py:1203-1215 | re-run directive on line/part/qty change; check at completion |
| F05 | P1 | operators can create/edit wave templates incl release_rule; auto-release builds+releases under sudo (release is supervisor-only) | ACL ir.model.access.csv:55,96-97; writable.py:1295-1308; flow:131-133,147-190 | |
| F06 | P1 | operator can write warehouse stock_location_id/company/OU, bin zone_id/class, zone warehouse_id/type -> re-attributes slot stock; stock_location_id not unique | cd_wms_structure ACL; writable.py:1014-1056; fix_wms_layout.py:198-208 | |
| F07 | P1 | on-hand stock can never be slotted: legacy stock + stock arriving by M15 transfer have no receipt line -> put-away impossible; floor-count gain posts on-hand+variance to M15 (inflates); no opening load (spec 16.4) | fix_wms_ops.py:524-530,1693-1711,1733-1740; fix_inventory_ops.py:1208-1240 | opening slot load w/o ledger effect; put-away from transfer receipt |
| F08 | P1 | floor count expected qty snapshotted at create, bin not frozen -> any pick/move before counting = false variance posted to M15 | fix_wms_ops.py:1640-1644,1693-1711; spec.py:2037-2046 | |
| F09 | P1 | ordinary M15 count at a WMS location posts negative variances without _fix_check_bins / slots | fix_inventory_ops.py:1681-1713 | |
| F10 | P1 | cross-dock vs transfer/RTV demand shrinks/deletes wave line not demand -> ship refuses or demand waved forever; stock already left | spec.py:1175-1179; flow:246-263,381-386 | |
| F11 | P1 | one demand line of multi-line transfer can be cancelled; ship moves every transfer line from staged incl unpicked -> fails or takes another wave's staged stock (pooled) | spec.py:1767-1774; flow:277-283,403-407 | |
| F12 | P2 | count-back/zero-crossing create only a task, no floor count; task never completable; phantom stays allocatable | fix_wms_ops.py:846-867,1538-1544; spec.py:693-702 | |
| F13 | P2 | blind counts not blind: slot qty shown (m41.js:144); floor count expected_qty/variance no group restriction (fix_wms_ops.py:1579-1581) unlike M15 (fix_inventory_ops.py:1796-1814) | | |
| F14 | P2 | reports ignore date range (controllers/a06/m41.py:214-533); shift buckets UTC (:218-224); pick accuracy inflated (qty rewritten fix_wms_ops.py:963, spec.py:1667, flow:829); utilisation mixes unconstrained bins | | |
| F15 | P2 | missing: daily override report BRU-WMS-06, cycle times, compliance, short-pick rate, cross-dock, device health, slot-vs-ledger recon AC-01 | | |
| F16 | P2 | no OU rules; no company rule on zone/bin/wave template/packing station; claim/put-away/move/RF ignore operative warehouse profile; RF device w/o operative usable by anyone | fix_wms_ops_floor.py:495-528; flow:1146,1186-1199 | |
| F17 | P2 | substitution create under _guarded() -> RPC can set requested_by_id/state; substitute bin class/pick zone unchecked | flow:776,756-765 | |
| F18 | P2 | HU store skips class/hazard/capacity; HU never dispatched, not linked to slots | spec.py:929-965 | |
| F19 | P2 | equipment_required writable/unguarded -> clear then claim (BRU-WMS-18) | writable.py:1260-1273 | |
| F20 | P2 | put-away exceptions w/o proof loop directive to wanted bin; blocked-bin exception does not block bin | spec.py:669-715 | |
| F21 | P2 | AUT-WMS-02/03/13 not built (auto put-away on receipt/inspection pass, M03 hand-over) | | |
| F22 | P2 | manual/job/refurb demand never shipped; cross-dock doesn't update demand | flow:372-400 | |
| F23 | P2 | carton contents_qty Integer; no per-part content | fix_wms_ops.py:1254 | |
| F24 | P2 | any operator/RF exception can block a bin (spec 13: supervisor/QM) | fix_wms_ops.py:155-167 | |
| F25 | P2 | W0001 queues dead demand for every approved transfer/RTV + empty nightly productivity run | | |
| F26 | P3 | 7 wh.* events missing from contracts registry; 6 spec events never emitted | | |
| F27 | P3 | productivity cron can duplicate runs; typed tasks w/o movement counted | | |
| F28 | P3 | template cut-off uses UTC date (spec.py:1542-1547); failed auto-release only logged | | |
| F29 | P3 | RF journal caches refused outcomes forever; keys per device | | |
| F30 | P3 | task cancel no role check; put-away no cancel | | |
| F31 | P3 | approved override can land in staging/returns/dispatch zone bin | | |
| F32 | P3 | M41 surface exposes action_set_standard_cost + valuation-suspense list (spec 13 no cost in M41) | | |

OWNER: O1 manual/job/refurb leave via M15 transfer/consumption only; O2 W0001 opening positions: disable until cutover count, load opening slots w/o ledger effect; O3 auto-release armed by supervisor only; O4 WMS count tolerance 0; O5 operators report, supervisor/QM block; O6 non-owned stock in "any" bins: no; O7 RF device must be issued to a named operative; O8 W0001 keep enabled w/o layout? recommend disable.

Checked OK: release all-or-nothing; Pick All idempotent supervisor+reason; wave cancel symmetric; moves keep ledger + checks; SoD on override/return disposition/substitution/unblock; guarded fields; append-only logs; claim FOR UPDATE NOWAIT; RF runs as bearer, refuses unknown/deactivated/others' devices, idempotency key unique; all m41.js cols exist (84 blocks); JS actions in SURFACES; 3 crons active; reports caller + company; transfer hand-off keeps receiver SoD; serials checked.

---

## M16 + M42 auditor findings (20 Nov 2026) - saved by lead
Paths rel. to addons. P0 1, P1 9, P2 23, P3 12.
Live: 0 POs/reqs/bills; 658 suppliers all `qualified`, none active, 0 docs/quals/screenings -> no PO sendable today. No cd_requisition.* params set; category gate off. GRNI param = 100503 "Stock Incoming" (asset). OU 1 has 74 branch stores, no central store.

| id | sev | conf | finding | evidence | fix |
|---|---|---|---|---|---|
| F01 | P0 | C | USD vendor bill posted to GL with USD figures as BDT (no currency_id/amount_currency); approval band, TDS, VDS on USD figure; local USD POs allowed | g_finance/cd_ap_ext/models/ap_gl.py:161-181; fix_ap_ext.py:1015-1069, 883; cd_requisition/models/fix_purchase_proforma.py:700-705 | convert w/ amount_currency, band/TDS on BDT; until then refuse non-BDT bills |
| F02 | P1 | C | match never compares bill vs PO currency; P05 bills always BDT | fix_ap_ext.py:353-478; cd_vendor_portal/controllers/vendor_api.py:250-272; fix_ap_ext.py:133 | block/convert; portal takes PO currency |
| F03 | P1 | C | lowest bid ranked on raw unit_price across currencies; threshold in bid currency -> bypass rationale + 3-quote | fix_procurement_ops.py:405-409, 234-236, 476-477 | normalise to BDT / RFQ currency |
| F04 | P1 | C | agreed-price lookup filters on PO currency; no match = no check -> other currency escapes price list | cd_vendor_portal/models/fix_supplier_terms.py:815-834, 1048-1068 | any currency + convert |
| F05 | P1 | C | local GR posts no GL; bill debits GRNI 100503 (asset) for every PO product incl services; nothing credits; services never expensed; imports do Dr stock/Cr GRNI | fix_ap_ext.py:986-999; cd_inventory/models/fix_stock_bridges.py:262-332; cd_import_order/models/fix_import_order.py:425-436; fix_ap_capture.py:1434-1453 | receipt/service entry Dr inv/exp Cr GRNI (liability); bill clears GRNI, PPV |
| F06 | P1 | C | receipt location = global param or OU's first store (limit=1); PO branch_id ignored | fix_stock_bridges.py:225-251; fix_requisition.py:835 | store from branch_id; refuse ambiguous |
| F07 | P1 | S | requested_by not pinned in write(); colleague repoints requested_by then confirms service entry | fix_requisition.py:261, 346, 366-377; fix_approval_guard.py:34-41; ACL:2; fix_procurement_capture.py:718-756 | pin after submit |
| F08 | P1 | C | category gate default off; approved_category_ids P03-writable w/o approval | fix_supplier_controls.py:34, 108-129; fix_supplier.py:149-157 | gate on; categories via qualification |
| F09 | P1 | C | non_po bill = match not_required, no supplier gate, no limit (BRU-PRO-01/02) | fix_ap_ext.py:180-188, 359-362, 637-644; fix_supplier_controls.py:407-446 | whitelist expense types; active supplier |
| F10 | P1 | C | deactivated (sanctions) supplier still paid; payment checks only payment_block | fix_supplier_controls.py:438-446, 452-469; fix_supplier.py:401-406, 1871 | refuse |
| F11 | P2 | C | no route for genuine price variance after receipt (BRU-PRO-08 vs M52 BRU-APE-03) | fix_ap_capture.py:669-691; fix_requisition.py:1411-1415, 1462 | OWNER O1 |
| F12 | P2 | C | no PPV; tolerance overage debits GRNI in full | fix_ap_ext.py:1015-1019, 431-466 | PPV 600007 |
| F13 | P2 | C | GRNI rows use received not accepted qty, live PO price unconverted, ignore as_of | fix_ap_capture.py:181-220 | |
| F14 | P2 | C | portal invoice submit not idempotent; replay duplicate draft blocks genuine; dup detection exact ref only | vendor_api.py:220-287; fix_ap_ext.py:706-717, 780-785 | |
| F15 | P2 | C | portal bills use vendor invoice_date + default 30 days; PO/agreement terms unused | vendor_api.py:275; fix_ap_ext.py:138-140, 284-288; fix_procurement_capture.py:526 | |
| F16 | P2 | C | buyer ack-on-behalf sets any vendor_confirmed_date; OTD/scorecard measure against it | fix_requisition.py:1340-1384; fix_supplier.py:1353-1362; m16.py:259 | |
| F17 | P2 | C | scorecard: fixed weights, no DIFOT/lead time/invoice accuracy, no refresh on inspection, no period-end cron, no suspension review 3rd D, cost compare any currency | fix_supplier.py:1233-1238, 1319-1408, 1438-1521 | |
| F18 | P2 | C | qualification no validity; requal typed by one steward | fix_supplier.py:804-851, 1099-1156 | |
| F19 | P2 | C | brand-authorisation expiry no effect; classification changeable after activation | fix_supplier_terms.py:369-394, 57-62; fix_supplier.py:258-268, 499-515 | |
| F20 | P2 | C | screening recorded+cleared by same steward; no COI match (AUT-SRM2-14) | fix_supplier.py:1845-1860 | |
| F21 | P2 | C | SoD: qual/activation approvers not excluded from bill approval; award decider not from PO approval; receiver inspects own receipt, no Quality role | fix_supplier_controls.py:414-436; fix_requisition.py:991-994; fix_procurement_ops.py:985-990 | |
| F22 | P2 | C | sealed bid by create_uid but staff key bids -> buyer sees all; RFQ closable before deadline, no auto-close | security/fix_requisition_rules.xml:14-19; fix_procurement_ops.py:213-220 | |
| F23 | P2 | C | award ranking price only (FR-PRO-013); losers not notified (014) | fix_procurement_ops.py:404-406 | |
| F24 | P2 | C | supplier not notified on PO send/change/cancel; no po.amended | fix_requisition.py:1307-1318, 1399-1456, 1475 | |
| F25 | P2 | C | M16 reports no date filter; spend/maverick/price include drafts+superseded, double-count change orders, add currencies | controllers/a06/m16.py:157-205, 311-403, 729-769 | |
| F26 | P2 | C | "Match Exceptions" KPI counts open unreceived PO lines; KPI-049 missing; PO cycle time wrong basis | m16.py:806-819, 406-439 | |
| F27 | P2 | C | M16 blankets duplicate M42 agreements; approved-source agreed_price not used; PO price from req estimate | fix_procurement_ops.py:633-801; fix_procurement_capture.py:187-353; fix_requisition.py:794 | |
| F28 | P2 | C | requisition single product; no UoM anywhere; cost centre/budget free text, no budget check | fix_requisition.py:262-324, 1580-1613; fix_procurement_capture.py:107 | |
| F29 | P2 | C | PO stores no FX rate/date (BRU-PRO-20) | fix_requisition.py:123-129; fix_stock_bridges.py:253-260 | |
| F30 | P2 | C | base.group_user reads PO prices, approved sources, price lists | cd_requisition ACL:4-5,36; vendor_portal ACL | |
| F31 | P2 | S | ineligible input VAT stays on input-VAT acct | fix_ap_ext.py:1020-1029, 1180-1202; cd_tax_engine_bd/models/fix_tax_compliance.py:1391-1414 | |
| F32 | P2 | C | portal lacks RFQ bid, dispatch advice, scorecard, self-registration | vendor_api.py:119-287 | |
| F33 | P2 | C | missing events requisition.*, po.amended, po.overdue, invoice.matched, price_changed, emergency; no ack chase cron; price alert hard-coded 10% | m16.py:336 | |
| F34 | P3 | C | contract coverage counts suppliers not spend | m42.py | |
| F35 | P3 | C | cut-over labels 658 suppliers qualified w/o record | fix_party_import_vendor.py:68-84 | |
| F36 | P3 | C | supplier register not per company | fix_supplier.py:206, 250-255 | |
| F37 | P3 | C | emergency release no role; anyone cancels any req | fix_requisition.py:590-694 | |
| F38 | P3 | C | PO/award cancel leaves req converted | fix_requisition.py:1458-1476; fix_procurement_ops.py:564 | |
| F39 | P3 | C | blanket cap ignores currency; double counts original during change order | fix_procurement_ops.py:700-709; fix_requisition.py:1126-1138 | |
| F40 | P3 | C | consolidated PO links only first requisition | fix_procurement_ops.py:573-628; fix_purchase_receipt.py:126-135 | |
| F41 | P3 | C | same product on several PO lines: highest approved price allowed for all | fix_ap_ext.py:110-114, 459-466 | |
| F42 | P3 | C | draft PO for unqualified vendor | fix_requisition.py:1030-1037 | |
| F43 | P3 | C | bank change doesn't notify previous contact | fix_supplier_controls.py:249-341 | |
| F44 | P3 | C | risk_tier drives nothing | | |
| F45 | P3 | C | "two consecutive D" not strictly consecutive | fix_supplier.py:1494-1504 | |

OWNER: O1 versioned re-approved post-receipt price amendment, no match override; O2 liability GRNI credited at receipt/service entry, PPV 600007; O3 keep USD local POs but store rate, bill in PO currency, block USD bills until built; O4 category gate on; O5 hold payments to deactivated suppliers, suspended pay w/ warning; O6 non-PO whitelist rent/utilities/fees/courier/telecom; O7 tolerance price +2%/+BDT500, qty 0%, competitive threshold BDT 50k; O8 appoint DOFA holders + Procurement Manager (0 today); O9 activate 658 suppliers in waves; O10 VAT rate on PO lines 15%; O11 emergency ceiling 25k/48h; O12 scorecard weights per category.

Checked OK: DOFA routing w/ split sums; SoD exclusions; pinned fields void approval; sent PO locked; change order reapproved; send re-checks; GR only vs sent PO by Receiver != buyer/requester; over-receipt capped; inspection final; service entry; match payee/once/approved price/2nd person tolerance; bill SoD; payment lock; award rules; emergency; M42 activation/expiry/sanctions/bank dual control/2-person agreements/scorecards computed+CAR; portal fenced; crons/consumers wired; all m16/m42 cols exist (89 blocks, 19 freg); writable excludes state/stamps.

---

## M43 + M44 auditor findings (20 Nov 2026) - saved by lead from the auditor's report
I = addons/domain/e_supply_chain/cd_import_order/models, D = addons/domain/e_supply_chain/cd_demand_plan/models
fix_real has 0 rows in fix_import_*, fix_demand_*, fix_bank_facility: all code-trace + config SQL.
Count: P1 14 (M44 8, M43 6), P2 26, P3 9.

## M44
| id | sev | finding | evidence | fix |
|---|---|---|---|---|
| M44-01 | P1 | variance account param = 610000, not in fix_real chart -> BoE paid with accepted variance and final sheet with consumed share refused | I/fix_import_common.py:164-178; I/fix_import_ops.py:2304-2312, 3014-3021 | OWNER names account |
| M44-02 | P1 | account_code.lc_clearing + fx_difference unset on fix_real -> every LC payment refused | ops:968-969 | OWNER/config |
| M44-03 | P1 | duty variance tolerance default 0 BDT, customs rounds per levy -> nearly every BoE needs variance acceptance -> 610000 | common:26; ops:2294-2325 | tolerance + M44-01 |
| M44-04 | P1 | within tolerance the bank is credited with the COMPUTED total, not customs_assessed_total | ops:2314 | always credit assessed |
| M44-05 | P2 | accepted variance 100% to variance acct; extra CD/RD/SD never in stock cost, extra VAT/AT never in input tax | ops:2321-2325 | per-levy assessed amounts |
| M44-06 | P1 | CIF/CFR/DDP assessable value omits freight/insurance that the invoice value includes -> duty understated | fix_import_order.py:247-256 vs 714-720; ops:171-176 | cif_amount includes all freight+insurance |
| M44-07 | P2 | duty at LC commitment FX rate, not customs rate on BoE date | ops:2567 | customs FX rate on BoE |
| M44-08 | P1 | final sheet allocates total CD+RD+SD by value/qty, ignoring each line's HS duty -> per-part cost wrong | ops:2790-2801, 2992, 2837-2840 | allocate duty directly from BoE lines |
| M44-09 | P2 | only value/qty basis, one per sheet; no weight/volume/direct/per-factor (FR-ITC-035) | ops:2717-2721 | add bases |
| M44-10 | P1 | serialised imported parts never receivable: M15 needs one line per unit with serial; import receipt sends qty>1 no serial | order:382-395; cd_inventory/fix_inventory_ops.py:762-771 | mirror M16 bridge serial draft receipt |
| M44-11 | P1 | LC payment debits LC clearing; nothing credits it or settles supplier bill -> double payment risk | ops:972-984 | settle AP bill from LC payment |
| M44-12 | P2 | LC margin never posted (100812 exists), no facility reservation, bank charges not auto-captured (AUT-ITC-07) | ops:359, 626-650 | post margin; draft bank cost doc |
| M44-13 | P2 | final revaluation only at receiving location; transferred stock treated as consumed -> COGS/variance | ops:3003-3009 | revalue network-wide |
| M44-14 | P2 | no partial shipments; receipt takes full line qty not BoE declared qty | ops:1853-1896; order:382-395 | per shipment |
| M44-15 | P2 | demurrage days only, no rate/amount/accrual | ops:1738-1808 | add amounts |
| M44-16 | P2 | import.duty_paid / landed_cost.finalised / import.cleared / arrived / lc_opened have no consumers; recoverable VAT/AT/AIT never reaches M51 (AUT-ITC-18); M51 report calls paid import SD/AT a liability, ignores dates | ops:2345, 3056, 1885; data/fix_import_consumers.xml; controllers/a08/m51.py:673-700 | wire consumers |
| M44-17 | P2 | M15 never flags imported stock provisional (BRU-ITC-01/AC-08), no 30-day escalation | cd_inventory comment line 612 | flag + job |
| M44-18 | P2 | refused LC discrepancy still allows payment under the LC | fix_import_capture.py:541-553 | block |
| M44-19 | P2 S | finalisation credits 201279 for freight/insurance/bank charges but cost documents never posted/handed to M52 -> 201279 never relieved | ops:3027-3033; capture:303-328 | post or emit to M52 |
| M44-20 | P2 | missing: landed-cost estimation API FR-ITC-005, multi-PO consolidation, stage cycle/lead-time publication to M43, full LC states, FX exposure, ~9 reports | order:68-76; m44.py:739 | backlog |
| M44-21 | P2 S | GRNI credited at commitment rate, M52 debits at bill-date rate -> FX residue; TT advance imports no FX | order:423-436 | clear GRNI at commitment rate |
| M44-22 | P3 | LC state `amended` never set; action_close accepts only `opened` | ops:587, 655, 847 | |
| M44-23 | P3 | amendment raising LC value does not re-check LCA coverage | ops:814-857 | |
| M44-24 | P3 | landed-cost report omits bank charges; order list "Landed Cost" is not the sheet | m44.py:306-358; order:239 | |
| M44-25 | P3 | reports ignore date range; KPIs UTC dates | m44.py:758 | |
| M44-26 | P3 | landed sheet allows non-BDT currency at model level, posts as BDT (latent) | ops:2686, 3024 | force BDT |
| M44-27 | P3 | DDP still runs importer BoE flow; HS classification unique per product across companies | order:81-90; ops:1355 | |

## M43
| id | sev | finding | evidence | fix |
|---|---|---|---|---|
| M43-01 | P1 | SS = z*sigma_d*sqrt(L) ignores lead-time variability; sigma_L measured, unused (BRU-DPL-07) | D/fix_demand_common.py:232-234; fix_demand_ops.py:888-895; fix_demand_capture.py:632 | z*sqrt(L sd^2 + d^2 sL^2) |
| M43-02 | P1 | two replenishment engines: policy + van par published as M15 reorder rules whose sweep drafts PR at on-hand<=min ignoring on-order; plan also releases its own PR -> double ordering | ops:1147; cd_inventory/fix_reorder_rule.py:397-414, 266-330; fix_demand_plan.py:413 | one engine |
| M43-03 | P1 | van/branch par replenished by supplier PR, not transfer | capture:1264; fix_reorder_rule.py:266-330 | transfer |
| M43-04 | P1 | requisition estimate uses last PO unit_price in that PO currency (USD) as BDT -> DOFA band/budget wrong | plan:369-389, 455 | convert |
| M43-05 | P1 | on-order netted company-wide while stock/policy per location; imports without M16 PO not counted | common:197-228; plan:281 | per location; include imports |
| M43-06 | P1 | plan subtracts whole period forecast then compares to ROP that already includes LT demand -> ~1 extra period ordered every cycle | plan:282-283; ops:892-895 | inventory position vs ROP |
| M43-07 | P2 | on_hand counts quarantine/inspection/blocked | common:183-193 | stock_status filter |
| M43-08 | P2 | service levels only 90/95/98/99; else silently z=1.65 | common:24, 233 | inverse normal |
| M43-09 | P2 | moving average only; no Croston/seasonality (BRU-DPL-04) | ops:164-177, 347-401 | |
| M43-10 | P2 | exclude outlier sets month 0 but divides by full window; adjustments never reach policy sigma/mean | capture:273, 289-313; ops:396, 970 | |
| M43-11 | P2 S | history = job consumption only; no transfers out/sales/refurb/backorders | common:119-133 | |
| M43-12 | P2 | MAPE denominator = forecast when actual 0; unweighted; no bias | ops:292-295; m43.py:199-233, 343 | WAPE, bias |
| M43-13 | P2 | KPI service level averages target settings, not achieved | m43.py:672-678 | fill rate |
| M43-14 | P2 | policy pools all suppliers' lead times; per-supplier LT model unused | ops:975-991 | |
| M43-15 | P2 | budget headroom adds USD + BDT | common:384-395 | convert |
| M43-16 | P2 | new-part and EOL/LTB approvals lead nowhere | capture:821-843, 945-980 | act on approval |
| M43-17 | P2 | only one cron; AUT-DPL-01..18 not automated | data/ir_cron.xml | |
| M43-18 | P2 | rebalance benefit typed; no surplus/shortage detection | ops:1352 | |
| M43-19 | P2 | ABC/XYZ only for created segment rows; no criticality/intermittency | ops:495, 551-600 | |
| M43-20 | P2 | no guard-rail auto-apply for B/C, no investment-impact notice (BRU-DPL-20) | ops:1079-1148 | |
| M43-21 | P3 | windows/month buckets UTC | common:140, 161 | |
| M43-22 | P3 | what-if keeps recomputing after run | ops:1584 | |
| M43-23 | P3 | segment company optional; unique per product across companies | ops:465, 495 | |

## OWNER (auditor recommendations)
1 variance acct: 600007 Purchase Price Variance (or split 600007 duty / 600002 COGS consumed share)
2 LC clearing: new asset acct "LC Payments Clearing"; FX 500030 Foreign Exchange Gain/Loss; how LC payment relieves the M52 bill
3 duty tolerance ~BDT 10 per BoE
4 AT base excludes RD (ops:2581) - tax adviser
5 import VAT/AT/AIT fully recoverable (Q-07)
6 duty clearing posts Dr 200306 Accrued Customs (liability) -> move to asset 100302 Deposits-Customs; keep 100503 GRNI
7 LC margin owner/account (100812); lc_requires_facility on with no M50 facility on fix_real blocks every LC
8 cost-doc variance tolerance; CFO threshold for final landed cost
9 M43 service levels (85% needed), window 12 / min history 6
10 one replenishment engine; vans/branches by transfer

## Checked OK (summary)
M44: duty cascade per FR-ITC-033; rates frozen; VAT/AT/AIT to 200901/100047/100037; 1% landing not capitalised; allocation exhaustive; M15 revalue real (110999); receipt idempotent, no double stock; STJ/PBLM exist; guards; SoD; DOFA on LC; LC caps/coverage/IRC/permits/C&F active/insurance/docs; ACL+rules 25 models; SURFACES actions exist; cols exist; reports company-scoped; 4 crons.
M43: approver != preparer everywhere; one PR per plan (UNIQUE); M16 approval; active supplier; versioned policies; ROP/max standard; ABC/XYZ math; LTB CFO >500k; ACL+rules 15 models.
