# B4 report: M38 storefront and M12 marketplace (21 Nov 2026)

Test DB: fix_test_a04erp. cd_storefront_finance was not installed on that DB, so B4 installed it there; fix_real already has it.

## Results
- **Passing:** cd_storefront, cd_storefront_finance (1 skip: single OU), cd_marketplace, and the P03 m38/m12 capture tests.
- **New tests:** about 43, including TestDeployment checks.
- **Mutants:** 14 of 14 red.
- **Still failing:** cd_settlement_ext has 25 failures (about 20 come from the new M12 rules); cd_cash_position `test_a04_c7_storefront_consumer` has 4.

## M38
- **F1:** FIXED.
  - `_sf_m11_price` prices through `price_for(channel='storefront')` and refuses a missing or ≤0 price.
  - Lines carry a price lock (`unit_price_excl`, `price_card_id`, `price_source`) and are re-priced at placement.
  - The customer price is VAT-inclusive via M51, so the invoice matches to the paisa.
  - Only priced items are listed. OWNER: until M11 prices are released, the storefront sells nothing.
- **F2:** FIXED. A paid-but-uninvoiced cancellation now:
  - captures the receipt and raises one `fix.ar.refund` on the original rail (unique per order);
  - never shows posting state "none" while money is owed;
  - is handled by consumer `consume_storefront_order_cancelled`.
- **F3:** FIXED.
  - The bridge is the single refund owner; the cd_cash_position consumer stands down.
  - One live credit note per storefront source.
- **F4:** FIXED. Whole units only.
- **F5:** FIXED.
  - New `group_fix_storefront_assisted_sales`; base users are read-only.
  - Recording terms or client approval needs a role, and the recorder must not be the clerk.
- **F6:** FIXED. M15 stock is reserved at placement, released on cancel or timeout, and consumed at dispatch.
- **F7:** FIXED. `payment_expires_at` plus a 10-minute expiry cron. OWNER: `cd_storefront.payment_timeout_minutes`, default 60.
- **F8:** DEFERRED. Per-line returns need a new return-line model and changes to A05's restock path.
- **F9:** OWNER. Roles.
- **F10:** FIXED.
  - Dispatch is refused while the invoice is owed.
  - The retry-posting and record-NID actions are whitelisted; posting_state is on the grid.
  - `stock_location_id` and `cod_customer_nid` are on the form.
- **F11:** FIXED. Exposure is read from `fix.stock.onhand` via `stock_location_ids`.
- **F12:** PARTIAL.
  - COD is refused without an active rule; OWNER to approve one.
  - Guests get one customer per phone, and guest COD is refused.
  - OTP is DEFERRED: there is no SMS service.
- **F13:** FIXED. A prepaid rail needs a live M65 gateway; web and app checkout also need the secret. OWNER: secrets.
- **F15:** DEFERRED/OWNER. There is no card-reversal rail.
- **F16/F17:** FIXED. Reports read through `scoped()`; paid-state GMV; returns from both models.
- **F18:** FIXED. The OU comes from the fulfilling store.
- **F14, F19, F20:** DEFERRED (product work).
- **F21:** OWNER (M15 cost data).

## M12
- **F1:** FIXED.
  - New `customer_receipt_id` (unique) and `customer_paid_at`, set by `action_record_customer_receipt`: an Accountant, a confirmed receipt for the full awarded amount.
  - Commission is earned only with that receipt.
  - The accrual debits the `marketplace_collections` role, falling back to 100201 AR, never 101404.
  - OWNER: confirm the account (alternative 200016).
  - Gap: the receipt stays unapplied in the sub-ledger.
- **F2:** FIXED. `action_paid` needs the M53 ledger rows paid, and is set by the discharge.
- **F3:** FIXED. Consumers for dispute_resolved and chargeback_lost: an M20 refund to the customer, and a seller forfeit or draft clawback. Nothing is auto-approved.
- **F4:** FIXED. No award without a commission scheme in force. OWNER: the scheme and D-03.
- **F5:** FIXED. The record rule covers open and quoted jobs.
- **F6:** OWNER. Roles.
- **F7:** DEFERRED. Masking.
- **F8:** FIXED. KYC needs a Z4 key or documents; no made-up token.
- **F9:** FIXED. Commission VAT via M51 (agent model), with `vat_amount` deducted from the payout. OWNER: the commission income account (today 400100).
- **F10:** FIXED. The rate pinned on the order wins.
- **F11:** FIXED. Changing categories withdraws the CFO approval.
- **F12:** FIXED. SOD-06 conflicts added.
- **F13:** FIXED. Sequences.
- **F14:** FIXED. Score bands use the 0–1 scale; fill rate formula; approved sellers only; reports scoped.
- **F16:** FIXED. The tier is restored when a dispute is resolved.
- **F15:** DEFERRED.

## Needs from others
- **cd_settlement_ext tests:** fixtures now need a seller commission scheme, a customer receipt and the M51 VAT model (see `cd_marketplace/tests/b4_helpers.py`).
- **cd_settlement_ext:** manifest bump (new field `vat_amount`).
- **cd_cash_position `test_a04_c7_storefront_consumer`:** fixture update.
- **Billing engine:** NOWAIT on the invoice sequence (B5 fixed this), and agent-collection receipt application.
- **Storefront Manager group** is `noupdate`: the implied assisted-sales group does not reach existing holders. Needs a migration or a manual change.

## Versions and deploy
- Versions: cd_storefront 19.0.0.2.1, cd_storefront_finance 19.0.0.1.1, cd_marketplace 19.0.0.4.1.
- `-u` on deploy: cd_storefront, cd_storefront_finance, cd_marketplace, cd_settlement_ext, cd_cash_position, cd_p03_portal.
