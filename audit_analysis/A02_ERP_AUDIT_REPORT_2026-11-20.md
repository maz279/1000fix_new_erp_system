# A02 Service Operations — ERP audit and remediation (19–20 Nov 2026)

Scope: M01 Service Orders, M02 Field Service, M03 Logistics, M04 Front Desk, M05 MSP, M06 Data Services,
M31 Workshop, and their links to finance (M19 GL, M20 AR, M50 treasury, M51 VAT), M09 warranty,
M15 stock, M33 credit, M39 subscriptions, M38 storefront, M63 approvals.
Branch `fix/a02-erp-audit` (worktree `1000 fix/a02erp-wt`), base e6d7a9b1.

## How it was checked
- Five read-only audits (one per module group, one cross-cutting: accounting, approvals, events,
  reports, role centres) against the M0x specs; every finding then re-checked against the code by
  the stream that fixed it.
- Executable evidence on a **copy of fix_real** (real 376-account chart, 73 branches / 58 OUs):
  an order-to-cash probe, field-cash, M06 billing and COD probes (rolled back).
- 3,178 screen field references (columns, form fields, grids, domains) of the 7 A02 modules
  validated on the ORM: **0 dropped**. 278 screen buttons validated against the served
  whitelists and the model methods: **0 dead**.
- Each fix has an ORM test; each stream ran a mutation check (defect re-introduced → test red):
  lead 10/10, M01 22/23, M02 18/18, M03/M31 32/32, M04 24/24, M05/M06 35/37 (all findings covered).

## What was wrong — the headline defects (all fixed)
1. **Money never reached the books (P0).** Counter settlements, walk-in diagnostic fees and M02 field
   cash went into the drawer and nowhere else: no AR receipt, no GL. The order's invoice then
   stayed open on AR for customers who had paid, and the M50 deposit credited branch cash that was
   never debited. Now every verified payment is a confirmed M20 receipt (Dr drawer / channel
   clearing, Cr customer AR); the tax invoice is raised at delivery and applies the receipts.
   Live on the fix_real copy: cash job Dr 100108 1,150 → invoice paid, customer AR 0; bKash job
   Dr 100111, drawer untouched.
2. **Invoices could not post at 57 of 73 real branches (P0).** The GL dimension took the company's
   first OU; every real branch has its own. Fixed in the M19 dimension fallback.
3. **M06 data recovery was never billed (P0)**: no invoice, no payment gate on hand-over. Now a
   relay consumer raises the M20 invoice (recovery + donor fee, M51 VAT) and hand-over needs it paid,
   a Finance Manager credit approval or a lab-manager waiver.
4. **MSP SLA credits could be switched off (P0)** by an engineer (onboarding trick; unguarded SLA
   terms; approved credits recomputed from the live contract). Terms are now guarded and amended by
   a credit approver; credits snapshot target and base.
5. **Rider COD shortages were never cleared and damage claims had no aggregate cap (P0).**
   Recovery now posts against the rider; claims are capped at the insured value less other claims.
6. **Goodwill/rework approved at BDT 0 waived any later price; estimate `version` could be
   rewritten to re-price an order (P0).** Waivers are pinned to the approved amount; versions are
   guarded and superseded.
7. Over-settlement, refunds of unverified TrxID claims, deadlocked price rises (no top-up),
   unreachable B2B credit release, OEM remittances never booked on AR: all fixed.
8. Operational controls: geofence bypass, stale van on reassignment, typed hub scans, editable
   dispatch evidence, a device on two live legs, returns closed without arrival, unfitted parts
   and typed labour in job cost, QC passed with failed tests, one failed QC blocking Ready forever,
   SLA business hours in UTC, late SLA marked success, passcodes in plain text, BER by one person,
   work orders surviving cancellation, re-quote approval bypass, BRU-DTS-10 bypass, purged case
   closing with media in the lab, unauthenticated seal-break witness, and more (see the ledger).
9. Reports and KPIs: company fences and Dhaka-day boundaries on every A02 pack and role-centre cue;
   wrong measures fixed (uncollected devices, revenue = invoiced ex-VAT, first-time fix, on-time
   delivery, burn-in, recovery success, SLA credit KPI).
10. Documents: counter-sale receipt (A4 + 80 mm, statutory Mushak 6.3 no.), wipe certificate, field
    service report, waybill / delivery note, workshop job card: new, printable from their screens.

Full per-finding status: `A02_ERP_AUDIT_LEDGER_2026-11-19.md` (≈105 findings).

## Owner decisions — status 20 Nov 2026 (final)
All fifteen are decided and applied.
- O1 damage-claim account = 500033 Courier Expense (fix_real); O2 invoice numbering reset to 1
  (fix_real, 0 invoices); O3 warranty exclusion ON; O4 loyalty priority = urgent; O7 fenceless arrivals
  record GPS (strict by parameter); O9 own-fleet SLA = 24 h (both DBs); O13 M06 quotes VAT-exclusive;
  O14 MSP uplift billed through M39 (1008eeee); O15 five fix_real users hold Finance Manager.
- Code (2ed13e31): O5 workshop and field repair technicians read a captured passcode (counter clerks
  still cannot; purged at hand-over); O6 90 days' repair warranty on every category; O8 routes start at
  the default depot Shewrapara HQ 23.7905, 90.3735 (`cd_field_service.default_depot`).
- Data (both DBs unless stated): O10 rider-shortage payroll account 2001821 Payable-Salary Expense on fix_real,
  230000 Salary Payable on fix_dev (both checked 20 Nov: credit side 100203 / 128100); O11 labour rate BDT 500/h on all 3
  workshops; O12 terms acceptance on Extended Warranty and AMC / Maintenance Contract Charge.
- Workshops draw parts from Warranty HO/Stock (fix_real, WARRANTY-HO) and from HO-WTY, fix_dev's
  head-office warranty store (all 3 workshops on each).
- Chattogram Central Depot: benches BENCH-CTG-L1-01, BENCH-CTG-L1-02 (L1) and BENCH-CTG-L2-01 (L2).
- The finance bridge is installed on fix_dev (owner approved).

## End-to-end walk on a fix_real copy (20 Nov, 18/18 OK)
Evidence: `evidence_a02_erp/a02_e2e_walk_odoo_shell.py.txt` (script) and
`evidence_a02_erp/a02_e2e_walk_fix_real_copy_2026-11-20.txt` (output). Staff steps only, real chart.
1. Walk-in counter repair: cash diagnostic advance → estimate 3,450 → due 3,150 → counter cash →
   INV/2026/00001 paid, AR 0; revenue 3,000 and VAT 450 posted; the deposit leaves the drawer net 0.
2. Depot repair: part issued from stock (60.01), **bench QC carries the order to Ready** (defect found by
   the walk and fixed in 9822e75e — before it, a passed bench QC left the order in qc_pending) → bKash
   posts to 100111 → invoice paid → 90-day warranty.
3. On-site repair: dispatch, GPS arrival recorded, cash 1,725 accepted by a separate cashier as a
   receipt Dr 100108.

## Field dispatch on fix_real (20 Nov, proven on a fix_real copy, 6/6)
A walk with the real users found that **only `admin` could dispatch a branch field job**: the two
Field Service Managers are head office, and the dispatcher `shariful.islam` held only Main Operating
Unit, so the OU record rule hid every branch's field orders from him (53 service branches each own an
OU). Owner decision: the head-office desk dispatches for every branch, so `shariful.islam` now holds
all 58 operating units on fix_real (applied 20 Nov).
Walk (`evidence_a02_erp/a02_dispatch_walk_*`), Motijheel Service Center order, real users, 0
certifications on the DB: an uncertified technician is refused by the M22 gate -> the dispatcher
requests a per-order waiver -> it reaches the Certification Override Approver's M63 inbox, not the
requester's -> approved -> the dispatcher dispatches from the screen (dispatch decision) -> the
branch technician accepts, travels, arrives on GPS, works and completes.

## Full regression, 21 Nov 2026 (shared HEAD 54c6f289)
Every A02 module and its finance / people / fleet neighbours, plus the 13 A02 portal suites, on a
fresh template at HEAD: **3,684 passed, 0 failed**, 83 skipped (82 by design: A02 screen models with
no workflow-controlled fields have nothing for the guard checks to attack; 1 environmental: the local
residency service returns synthetic ID numbers). Modules: cd_service_order, cd_warranty_claims,
cd_front_desk, cd_front_desk_finance, cd_msp_contract, cd_workshop, cd_field_service,
cd_device_registry, cd_consignment, cd_data_case, cd_billing_engine, cd_gl_ext, cd_tax_engine_bd,
cd_cash_position, cd_settlement_ext, cd_subscription, cd_quotation, cd_competency,
cd_vehicle_dispatch, cd_asset_workorder_spine. cd_cash_position passes on an up-to-date DB (the setup
error another session saw came from a shared test DB behind HEAD, not from the code).
Two earlier runs were cut short by shared-Postgres crashes on 20 Nov (10:43 and 13:00 UTC, under
concurrent drops and test load from several sessions). After each recovery both ports served and
all 132 A02 screens read on fix_real and fix_dev with 0 errors and 0 dropped columns.

## A02 pass 2 (21-22 Nov): integrated, reviewed, deployed
A second, independent A02 audit (owner decisions D1-D26 in `A02_ERP_PASS2_DECISIONS_2026-11-20.md`)
left six builder branches unmerged when its session ended. They were integrated (fix/a02r2-integration),
then an independent review (A03 session) found 8 blockers; all were fixed with tests that fail without
the fix, re-checked by the reviewer, and the follow-up findings closed:
- D1 gate (an unpaid Ready order shipped with COD 0), COD self-verifying from its own door receipt, the
  COD receipt over-booking a part-paid order, an own-rider COD leg never settled after a part payment,
  field over-collection, unverified part payments, the D20 permanent block.
- MSP: resolving a paused alert raised AccessError; a crafted report period; D10 coverage; the
  business-hours SLA clock; every M05 KPI request crashed.
- M06/M31: client-settable context keys switching off the custody two-person rule, the purge binding,
  the read log and the BER cancel; M18 destruction losing its two-person rule; the wipe-certificate
  binding (strict again, with consumers raising their own requests); operator scope rules that never
  restricted; finance actions taken as sudo.
- A04 and pass 2 had each built the M09 claim write-off (D24): merged into one routine.
- Owner decisions 21 Nov: MSP uplifts prorated one per effective date; M06 data and media go only to
  verified contacts; workshops draw chargeable parts from Non-Warranty HO/Stock and warranty parts from
  Warranty HO/Stock (applied in the A06 wave); VAT tax point at delivery, one Mushak 6.3 per basket
  item, parts consumption stays in suspense 110999 until cut-over (as built).
- Deployed 21 Nov (restart 15:24 local): 33 modules on fix_real and fix_dev, 132/132 A02 screens on
  both ports, 68/68 A02 reports, no log errors (A03 read-only check). Walks on a copy of the deployed
  fix_real: full repair journey 18/18 (part issued from the workshop store at cost), declined-repair fee
  9/9, field dispatch with a certification waiver 6/6 (`evidence_a02_erp/a02r2_*`).
- Regression after the A07 landing, fresh template, whole cd_p03_portal suite included: 12,313 passed,
  0 failed (the defects the A04/A06/A07 regressions found - the field-cash shortage booking without the
  finance bridge, the M05 report route, the M03 duplicate field - fixed). Follow-ups landed at 5469c0e3
  and deploy in the A06 wave.
- Skips explained: guarded-field checks on models with no guarded fields (by design); optional modules
  not installed on the test DB; data-dependent checks with no rows of that kind (A03 contact-centre
  gap-closure); the local residency service returning synthetic IDs.
- After the A06 wave (restart 22 Nov), live check: 132/132 A02 screens on 8069 and 8090, 0 errors,
  0 dropped columns. Walks re-run on a fresh copy of the deployed fix_real, now with real-time stock GL:
  repair journey 18/18 (part issued from Warranty HO at stock cost), declined fee 9/9, field dispatch
  6/6 (`evidence_a02_erp/a02_*_fix_real_after_a06_deploy_2026-11-22.txt`).
- M06 hand-over bypass (found in the A03 re-check): a recipient mobile verified only after the case
  opened passed the "verified contacts only" rule. Fixed in 4e735862: such a mobile is refused unless a
  data steward vouches for it (vouch recorded with who and when on the contact point).

## A03 review P1/P2 findings, re-checked one by one (22 Nov, tip d233cb24)
The review's serious (P1) and lower (P2) findings had been reported on the stream branches and never
re-checked on the merged code. Each was traced to its fix and test, or fixed now:

| Finding | Status |
|---|---|
| s3 COD receipt for source 'cod'; rider COD never remitted; field over-collection; M02-08 OR-ed rule; part payments | Fixed aa78fbb9 + e016c78b (N1-N5), tests in test_a02r2_release / test_a02r2_field |
| s4 D10 all-or-nothing; business-hours SLA wall-clock | Fixed e4e95620 |
| s5 P03 scoping/read log; finance sudo; consumer binding; D16 blank media | Fixed 86586402 + c1283042 |
| s5 legacy quotes | No live impact (0 rows on both DBs) |
| s4 batched uplifts from the earliest date | Fixed b56a34cc (owner decision: one proration per date) |
| s4 fee change to 0 | By design: flagged to finance, the price change cannot end the subscription (M39 decides); test_a_fee_falling_to_zero_is_flagged_not_a_silent_cancel |
| s4 late go-live, UTC date, late renewal, seed, legacy uplift events, reclassify approver, period labels | Fixed e4e95620 |
| s3 loaner legs; seal/weight locked | Fixed c1283042 / aa78fbb9 |
| **s3 D21/D22 charges never billed** | **Fixed now**: the wasted-visit fee (CHG-CALLOUT, unless waived) and the pick-and-drop tariff charge (CHG-TRANSPORT) are extra charges of the order; M51 adds their VAT to the amount due (counter, field and COD collect them) and they are billed on the delivery tax invoice to revenue. A delivery leg is priced before its COD is derived, so the rider collects its own charge. |
| **s3 courier booking COD goes stale** | **Fixed now**: a leg whose live courier booking carries a different COD does not leave ("cancel the booking and book again") |
| s5 m31_order_delivered context; self-made manager; protocol lock; hand-off withdrawal; bench ESD default | Fixed 86586402 (context key gone) |
| s5 D17 KPI counted held cases | Fixed: purge_overdue excludes cases on hold |
| s5 handover_recipient_id routable | Fixed 8ba8900d + 4e735862 (verified contacts only, steward vouch) |
| s6 AUT-018 cursor | Fixed 218c6af1, its 4 tests pass |

Proven on a fresh copy of fix_real upgraded to the shared tip (tariff BDT 120 and fee BDT 300 set on
the copy only): a pick-up leg is priced at confirm, the counter collects 1,288.00 (1,000 + 120, VAT
15%), the delivery invoice bills labour 1,150.00 + CHG-TRANSPORT 138.00, paid, revenue -1,120 / VAT
-168; a courier booking made before a part payment holds the leg ("collects BDT 2300.00 but the leg
collects BDT 1938.00 now"), the re-booking carries 1,938.00 including the leg's own charge; a failed
visit (customer absent) adds 345.00, the technician collects 2,070.00 on the second visit and the
field-delivered invoice bills CHG-CALLOUT 345.00. Charges walk 6/6; repair journey 18/18, declined
fee 9/9, dispatch 6/6 on the same copy (`evidence_a02_erp/a02_*_fix_real_copy_shared_tip_2026-11-22.txt`).
A03's re-check found one edge (a BDT 0 estimate skipped the charges in the amount due while the
invoice billed them): a free repair now owes its charges unless the order is zero-charge.

The tariff table and the wasted-visit fee are still at their D22/D21 defaults (empty / BDT 0), so no
charge arises until the business sets them.

## Still the business's to supply
- **Technician certifications** (HR records them in M22, owner 20 Nov). Until a technician holds one,
  the waiver above is the path, and it works end to end today.
- fix_dev holds **no stock at all** (0 on-hand rows), so no part can be issued there from any store;
  the workshop store link (HO-WTY) is in place for when stock is loaded. fix_real's workshop store
  holds 53,148 units and the part issue was walked there (scenario 2).

## Owner decisions (original list)
| # | Decision | Effect until decided |
|---|---|---|
| O1 | Damage-claim expense account: `cd_settlement_ext.account_code.damage_claim_expense` names 645000, which is not in the fix_real chart | payouts clear to 100102 Bank Suspense |
| O2 | Reset `fix.ar.invoice` numbering to 1 before go-live (sequence at 5, 0 invoices: 1-4 burnt by rehearsals) | first statutory invoice would be INV/2026/00005 |
| O3 | Warranty exclusions: liquid damage / physical-category faults void warranty zero-charge (`cd_service_order.warranty_excludes_customer_damage`, default ON) | ON |
| O4 | Loyalty priority level for Gold/Diamond (`cd_service_order.loyalty_priority`, default urgent); flag tiers in M10 | no tier flagged on fix_real: no effect |
| O5 | Device passcode reader roles (QC inspector, supervisor, admin) | as built |
| O6 | Repair warranty days per device category (spec Q-03) | order's own warranty days |
| O7 | Geofences: fix_real has 0 fences in 8 zones | every arrival needs a dispatcher waiver |
| O8 | Route depot coordinates | route optimisation refused |
| O9 | `cd_consignment.own_fleet_sla_hours` | own-fleet legs not judged on-time |
| O10 | `cd_cash_position.account_code.rider_shortage_payroll`; note rider_shortage and cheque_returned both point at 100203 | payroll recovery refused |
| O11 | Workshop `labour_rate_per_hour` | labour = supervisor-recorded figure |
| O12 | Products needing counter terms acceptance (`fd_counter_terms_required`) | none flagged |
| O13 | M06 pricing: quotes billed VAT-exclusive (M51 adds VAT); evaluation / destruction fees have no price field; non-NDNF unrecoverable billed full quote — confirm | as stated |
| O14 | M39 to bill `msp.device_uplift` | uplift event published, not billed |
| O15 | Who holds `account.group_account_manager` (credit release on orders and data cases) | nobody can release on credit |

## Closed in the last round (20 Nov, after the owner decisions)
- **Declined repair charged its diagnostic fee** (FR-SRM-029, SP-013 step 19). Cancelling with
  `customer_declined` / `estimate_declined` now raises a Mushak 6.3 invoice for the fee taken at intake
  (one Diagnostic / Inspection line, charge code CHG-DIAG, VAT backed out of the price the customer
  paid) and pays it from the intake's advance receipt. Before, the fee sat as the customer's credit:
  no revenue, no VAT, and auto-match could offer it to their next invoice. A refusal (credit hold, no
  charge code) never undoes the cancel; finance retries with **Invoice Diagnostic Fee** on the order.
  Other cancel reasons (duplicate, unreachable...) leave the fee as the customer's credit to move or
  refund. Tests: `cd_front_desk_finance/tests/test_a02_declined_repair_fee.py`.
  Live since 16:21 on 8069/8090 (afa7b1ca). Walked on a fix_real copy, 9/9
  (`evidence_a02_erp/a02_decline_walk_*`): cash fee 300 Dr 100108 -> estimate 8,050 declined ->
  INV/2026/00001 paid, 260.87 + VAT 39.13, Mushak 2026-000003; receipt unapplied 0, customer AR 0.
  Regression of every suite on the invoice path (billing, front desk, service order, settlement,
  quotation, asset spine, A02/M01 portal): ~1,440 tests, 0 failures.
- A refunded counter settlement no longer stays "unapplied": the refund is an M20 `fix.ar.refund`
  against the receipt, which takes it off the receipt (`test_a02_p1p2_cd_settlement_ext.py`,
  `test_a02_erp_review_money.py` assert unapplied 0). The earlier note here was out of date.
- Dispatch tests in cd_competency (M22) and cd_vehicle_dispatch (M46) still called the removed
  workspace `action_dispatch`; the workspace dispatches by saving a `fix.dispatch.decision`, which runs
  `action_dispatch` and so both gates. The tests now dispatch that way and still prove the gates refuse.
- fix_dev: workshops draw from `HO-WTY` (its head-office warranty store, the equivalent of fix_real's
  Warranty HO/Stock) and rider payroll recovery posts to `230000 Salary Payable` (fix_real 2001821).

## Operating notes (by design, not defects)
- Technician certifications are HR's data (owner, 20 Nov: HR records them in M22). Until a
  technician holds one, a field dispatch needs an approved per-order certification waiver
  (BRU-LMS-01); fix_real has none recorded yet.
- A declined repair's device goes back through the normal return / hand-over; only the fee is billed.
