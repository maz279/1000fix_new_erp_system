# R3 findings: M09 warranty/claims and M39 subscriptions (20 Nov 2026)

Measured on fix_real_a04, a copy of fix_real with every probe rolled back. Probe scripts and outputs are in `%TEMP%\a04erp\R3\` (p01-p09).
fix_real_a04 has 0 subscriptions, claims, devices, orders and warranties, so every flow was built inside a rolled-back transaction on the real chart, users and parameters.

Counts: P0 7, P1 13, P2 15, P3 2.
The 10 `fix.subscription` A08 hand-off gaps were re-run as real users (p07), and all 10 now hold.

## P0
- **M39-F1: revenue is recognised twice.**
  - Issuing a cycle invoice creates a deferral schedule (`fix_invoice_deferral.py:31-77`).
  - "Generate Revenue Schedule" creates a second schedule over the whole contract value (`fix_subscription.py:556-611`).
  - Both post Dr 200401 / Cr 400100. In November 3,000 ex-VAT was billed and 5,868.13 recognised (p02 §A).
- **M39-F2: cancelling through a lifecycle request stops nothing.**
  - The obligation schedule keeps posting: 10,780.22 in the 90 days after cancelling.
  - There is no refund, credit, final bill or early-termination charge (p02 §E).
  - Code: `fix_m39_capture.py:1902`, `fix_subscription.py:799`.
- **M39-F3: a refund leaves revenue overstated.**
  - The credit note debits 200401, but `_stop_recognition` never stops the invoice deferral schedule.
  - Result: 3,000 recognised for 1,000 earned, and 200401 left with a 2,000 debit (p06).
- **M39-F4: autopay success never reaches M20.**
  - Nothing consumes `subscription.autopay_succeeded`, so the invoice residual stays 3,450 and no receipt is created (p03).
  - Latent until a gateway is live.
- **M09-F1: an OEM claim receivable cannot be raised on fix_real.**
  - The consumer looks for a `res.partner` whose `ref` equals the brand code; 0 of 161 brands match.
  - `fix.brand` has no partner field (p05).
- **M09-F2: protection plans never touch the ledger.**
  - Premium, deferral, reserve, cash settlement, excess and the cancellation refund (4,504.11) post no GL entry and create no AR document (p05).
  - The warranty provision accounts 200002, 200005 and 500229 are unused.
- **M09-F3: an approved write-off posts nothing.**
  - The claim becomes `written_off`, but the OEM invoice stays issued with residual 300.
  - No GL entry is made, and nothing consumes the write-off event.

## P1
- **M39-F5: the billing roll ignores the contract term.**
  - It uses fixed 30-day cycles and ignores the contract end date.
  - A 12-month term produced 13 charges (13,000 on a 12,000 contract) and billed past the end (p02 §B).
- **M39-F6:** a subscription with no contract value or end date bills into 200401 and never recognises it. Its schedule is born `held`.
- **M39-F7:** an approved price change applies at once whatever its effective date: a change dated 75 days ahead computed 0 proration (p02 §D).
- **M39-F8:** schedule-billed subscriptions ignore price changes, because `amount_planned` is frozen when the schedule is generated (p02 §C).
- **M39-F9: BRU-SUB-17 (reviewed dry run before commit) is bypassable.** Measured as amber (p03/p07):
  - `action_generate_charge` billed a cycle directly;
  - `next_invoice_date` could be moved a year ahead;
  - `grace_period_days` could be set to 999;
  - a 1.00 charge with no invoice marked the cycle billed.
  - The fields are writable through `a08/m53.py` writable.
- **M39-F10:** the M39 roles are unstaffed. Subscription Officer = admin only; Accountant = amber only.
- **M39-F11:** M08 contract activation creates no subscription, the quotation consumer creates one with no contract, and asset attach/detach is not prorated.
- **M09-F4: the claim value comes from the customer estimate, not the M11 brand rate.**
  - The estimate includes VAT: 2,300 vs 3,000 at the Apple L1 rate.
  - The rate API `rate_for` / `reimbursement_for` has no caller.
- **M09-F5:** a second claim on the same order is accepted, and there is no way to cancel a claim.
- **M09-F6:** two claims approved before settlement overrun the aggregate limit (15,000 paid on a 10,000 limit), and the reserve top-up covers only one.
- **M09-F7:** an appeal after a partial approval leaves the old OEM invoice on AR (1,500 left after the brand rejected).
- **M09-F8: no real person can run M09's maker-checker steps.**
  - Clerk and officer are held only by admin; Warranty Officer has 0 holders.
  - So voids and warranty verification cannot happen, and a new warranty stays `pending` and is refused at intake.

## P2
- **M39-F12:** the dry run counts only base and recurring lines (3,000 vs 8,700 committed).
- **M39-F13: KPIs and packs are unscoped and wrong.**
  - Reads are sudo with no company scope.
  - The date range is ignored.
  - `churn_logo` is an all-time ratio.
  - The cohort is not normalised.
  - There is no MRR waterfall, and NRR is None.
  - MRR includes `hold` subscriptions.
  - The dunning pack sums the recurring amount, not the overdue balance.
- **M39-F14:** a refund assumes the cycle started at `next_invoice_date` − 30.
- **M39-F15:** billing stops at `past_due`, and reinstatement back-bills the suspended months (BRU-SUB-12).
- **M39-F16:** a price increase needs no customer notice (BRU-SUB-07).
- **M39-F17:** no consumers exist for usage_reported or for suspension/cancel/pause.
- **M39-F18:** MSP uplift is refused when the device count changes again before relay, and reductions never lower the bill.
- **M09-F9:** the OEM invoice credits 400100, not 400110 "In Warranty Claim Income". VAT is hard-coded 0 on a VAT-inclusive amount (an M51/owner decision).
- **M09-F10:** there is no LAPSED state or escalation, and a claim submitted 20 days late is accepted.
- **M09-F11:** `claims_under_72h` counts unsubmitted claims as on time.
- **M09-F12:** leakage excludes approved-but-unpaid claims; ageing has no buckets; there is no chase cron (AUT-WTY-10).
- **M09-F13:** brand rule flags are not enforced, and "parts issued" evidence is matched by name.
- **M09-F14:** unallocated remittance cash is never booked, and remittance lines stay editable after matching.
- **M09-F15:** protection claims have no value-band DOFA, per-claim or count limits or depreciation, and their terms stay writable after activation.
- **M09-F16:** missing features: consignment parts, brand performance, fault codes, outbound submission, sealed evidence pack, campaigns, coverage precedence.
- **M09-F17:** `warranty_requires_verified` is off.

## P3
- **M39-F19:** consolidated B2B invoicing publishes a fabricated Mushak number.
- **M09-F18:** a 0.00 VAT line is posted, and the loss ratio uses written premium.

## Measured as correct
- **M39:**
  - VAT is 15% exclusive. The issue posts Dr 100201 3,450 / Cr 200401 3,000 / Cr 200902 450.
  - Upgrade proration: (4,500 − 3,000) × 20/30 = 1,000.
  - Calendar first period: 1,700.
  - Refund maths and tiered usage (1,400) are right.
  - A duplicate usage key is refused.
- **M09:**
  - The evidence pack is enforced.
  - The waiting period auto-rejects.
  - A fraud score of 50 or more blocks approval.
  - Excess must be collected before settlement.
  - Decisions are routed through M63.
  - A remittance creates an M20 receipt and allocates it.
  - A short payment is flagged.

## Facts on fix_real_a04
- Role holders:
  - claims clerk and claims officer: admin only;
  - Warranty Officer: 0;
  - Subscription Officer: admin;
  - account_user: 1;
  - account_manager: 4.
- Account roles:
  - ar 100201;
  - deferred_revenue 200401;
  - revenue 400100;
  - vat_output 200902;
  - writeoff 510008;
  - claim_recovery 400111 (courier damage).
- Accounts that exist but are unused: 400110, 200002, 200005, 500229.
- Parameters:
  - `cd_subscription.auto_billing` is unset (off);
  - `cd_service_order.warranty_requires_verified` is unset (off).
- Event consumers present: `quotation.accepted`, `msp.device_uplift`, `warranty_claim.decided`, `bulletin.distributed`.
