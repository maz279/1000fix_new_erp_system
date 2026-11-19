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

## Owner decisions (mechanism built, fail-closed; the figure or choice is the business's)
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

## Known limits (stated, not hidden)
- A refunded counter settlement leaves its M20 receipt "unapplied" in the AR sub-ledger (the GL is
  right: the refund debits the customer's credit); finance clears it from the unapplied queue.
- A diagnostic fee on a declined repair stays as the customer's credit; it is invoiced or refunded
  by finance from the unapplied-cash queue (no automatic fee invoice).
- Pre-existing failures outside A02 seen during the runs (cd_competency / cd_vehicle_dispatch
  calling a removed P03 dispatch path; `test_a04_register_reconciliation`; `test_m04_submodule_capture`)
  are listed in the stream reports and were not changed.
