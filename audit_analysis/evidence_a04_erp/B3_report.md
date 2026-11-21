# B3 report: M09 warranty/protection and M39 subscriptions (21 Nov 2026)

Test DB: fix_test_a04b3.

## P0 (all FIXED)
- **M39-F1: one recognition basis per subscription.**
  - `_fix_recognition_basis()` returns contract, invoice or none.
  - The contract basis creates no invoice deferral.
  - The invoice basis refuses a contract schedule (`_fix_refuse_second_basis`).
- **M39-F2: cancelling settles the money.**
  - `action_cancel` calls `_fix_settle_cancellation`, which issues refund credit notes for billed cycles past the cancellation.
  - It issues a final bill for service delivered but unbilled.
  - On the contract basis it settles the remaining liability.
  - Every schedule stops (`_fix_stop_at`). The lifecycle cancel uses `effective_date`.
- **M39-F3 / F14: refunds are measured on the actual billed cycle.**
  - The deferral stops, and any non-refunded part is recognised.
  - Account 200401 nets to 0.
- **M39-F4: autopay success becomes an M20 receipt.**
  - Consumer `consume_autopay_succeeded` creates a confirmed receipt and allocates it.
  - A UNIQUE `receipt_id` keeps it to one receipt per attempt.
- **M09-F1 / X4: brands have a billing partner.**
  - New field `fix.brand.partner_id`. `billing_partner()` reads it first, with the ref fallback kept.
  - The consumer refuses until a partner is linked.
  - `action_create_billing_partner` is for system administrators only and is never automatic.
  - OWNER: create the 161 brand partners.
- **M09-F2: protection plans reach the ledger.**
  - Code: `cd_billing_engine/models/fix_a04_warranty_subscription_billing.py`.
  - Activation raises a premium invoice. VAT is per M51; `cd_warranty_claims.protection_premium_vat=exempt` is OWNER.
  - The premium is deferred over the term.
  - The reserve posts Dr `warranty_cost` / Cr `warranty_provision`, and release reverses it.
  - Cash settlement goes through an M50 instruction; cancellation raises a credit note.
  - OWNER account roles: `warranty_provision` defaults to 200002 (alternative 200005); `warranty_cost` defaults to 500229.
  - DEFERRED: an M20 document for the excess.
- **M09-F3: an approved write-off posts.** It raises a `fix.ar.writeoff` on the OEM invoice, using the loss allowance first, then bad debt. It is refused until the invoice is issued, and SoD checks run first.

## P1
- **M39-F5:** FIXED. Calendar cycles aligned to the anniversary, clipped and prorated at the contract end.
- **M39-F6:** FIXED. An invoice deferral counts as its own basis.
- **M39-F7:** FIXED. Prorations apply on their effective date through the cron `ir_cron_subscription_proration_due`.
- **M39-F8:** FIXED. Periods carry a `fraction` and are priced on the billing day.
- **M39-F9:** FIXED.
  - `action_generate_charge` needs the reviewed run's token, and a charge cannot be created directly.
  - The cron prepares a dry run.
  - The term fields are locked after creation.
- **M39-F11:** DEFERRED, OWNER/B2 decision. The M08 walker already bills contracts, so creating a subscription on `contract.activated` would double-bill.
- **M09-F4:** FIXED.
  - Claims are valued by `reimbursement_for`, ex-VAT, with `repair_level`, `rate_id`, `valuation_basis` and `parts_value`.
  - With no rate, it falls back to the estimate ex-VAT, flagged.
  - OWNER: `cd_warranty_claims.require_brand_rate`.
- **M09-F5:** FIXED. One live claim per order; a new `cancelled` state and `action_cancel`.
- **M09-F6:** FIXED. Approved claims count against the aggregate limit, which is re-checked at settle, and the reserve top-up covers all of them.
- **M09-F7:** FIXED. An appeal books only the delta: it drops a draft, credits an issued invoice, or raises a supplementary invoice.

## P2/P3
- **FIXED:**
  - M39-F12: the dry run now matches the commit.
  - M39-F13: KPIs read through `scoped()`, with monthly churn, a normalised cohort, a waterfall and NRR; MRR excludes holds; dunning shows the overdue balance.
  - M39-F15: billing continues while past due, and reinstatement skips the held months.
  - M39-F18: uplift deltas bill, and reductions lower the bill.
  - M39-F19: no fake Mushak number.
  - M09-F9: income goes to 400110 through the `warranty_claim_income` role. The VAT mode is OWNER/M51 (`cd_billing_engine.warranty_claim_vat_mode`).
  - M09-F10: a lapsed state, set by cron, and `action_extend_deadline`.
  - M09-F11/F12: KPIs corrected, with ageing buckets.
  - M09-F14: the unallocated remittance becomes a receipt, and matched lines are locked.
  - M09-F15 (part): terms are frozen after activation.
  - M09-F18: loss ratio uses earned premium.
- **Brand authorisation:** checked on submit behind `cd_warranty_claims.require_brand_authorisation`, default off (OWNER).
- **DEFERRED:** M39-F16, M39-F17, the M09-F12 chase cron, M09-F13, M09-F16, and the rest of M09-F15 (the limits need business figures).
- **OWNER:** M39-F10, M09-F8, M09-F17.

## Tests
- **New:** 43, all passing.
- **Mutants:** 14 of 14 killed.
- **Existing suites:** first run 434/448. The 14 failures were tests that encoded the old defects, plus 3 real bugs that B3 fixed. Re-run: 187/188.
- **Still to confirm:** the last test (`test_proration_credit_is_approved_under_dofa_and_applied`) was updated, and its re-run was waiting for a slot.
- **Not run:** the cd_settlement_ext A08 tests.

## Versions and deploy
- Versions: cd_subscription 19.0.1.4.2, cd_warranty_claims 19.0.2.3.1, cd_billing_engine 19.0.2.7.1 (shared with B2).
- Deploy: `-u cd_warranty_claims,cd_billing_engine,cd_subscription`.

## Needs from the lead
- `a08/m53.py`: remove `action_generate_charge` and the 3 term fields from writable, and the Generate Charge button in `m53.js`.
- `cd_settlement_ext/tests/test_a08_m53_controls.py` lines 811/830/847 call `action_generate_charge` as a user.
- The M39-F11 decision.
