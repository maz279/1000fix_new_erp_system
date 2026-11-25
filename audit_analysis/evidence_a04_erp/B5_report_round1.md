# B5 round 1 (M40 + shared M20): code written, NOT run

The run was blocked by the Postgres crash. Verified so far: py_compile, plus ruff check and format, both clean. Nothing else has been run.

## Design
- cd_partner now depends on cd_billing_engine and cd_rate_card. Neither of those reaches cd_partner, so there is no dependency cycle.
- Royalty, franchise fee and reseller draws raise draft M20 invoices inline, via `fix.ar.invoice._fix_draft_invoice_from_source`.
- MDF and rebate payouts go through M53 consumers in `cd_settlement_ext/models/fix_settlement_m53.py`, which `_inherit`s `fix.a04.finance.consumers`.

## Findings (written, untested)
- **F1/F19 royalty.**
  - The basis is the branch OU's M20 ex-VAT `taxable_amount` for the period, net of credit notes.
  - `action_raise_invoice` (finance users only) raises a royalty line and a levy line, with VAT from M51.
  - It fails closed while `cd_partner.account_code.royalty_income` is unset.
- **F2:** franchise activation raises the fee invoice. It fails closed while `cd_partner.account_code.franchise_fee_income` is unset.
- **F3 MDF claims.**
  - Approval publishes `partner.mdf_claim_approved`.
  - The M53 consumer posts Dr MDF expense / Cr payable (net) / Cr TDS, and raises a pending `fix.payment.execution`.
  - "Paid" requires the executed instruction.
- **F13 rebates:** the same pattern: accrual, TDS, an M50 instruction, and a payout that requires execution.
- **F4/F18 referrals.**
  - ACL: base 1,0,0,0; channel officer 1,1,1,0; portal read-only.
  - `fix.referral.write` freezes the attribution fields.
- **F5 commission rate.**
  - New model `fix.partner.rate.change`, approved via routed DOFA at Tier 3.
  - The default rate is now 0 and readonly.
- **F6:** the referral rate is frozen at earning. The M53 accrual uses it, and a ledger override keeps referral rows at that rate; the scheme supplies TDS only.
- **F7:** new field `referred_on`. Evidence counts only invoices inside the window: `referred_on` to `referred_on + cd_partner.lead_attribution_days` (default 90).
- **F8:** portal submissions create a consented `fix.partner.lead`. The portal never echoes `res.partner` names.
- **F9:** earning states are onboarded and probation only. Suspend, exit and dormancy remove the portal group; reinstate restores it.
- **F10:** consent fields are required on referrals.
- **F11:** onboarding needs a published programme, an active M08 contract and a completed checklist.
- **F12:** the rebate period is set, and the basis is guarded and computed from paid invoices net of credits.
- **F14 (partial).**
  - Brand authorisation warnings at T-180/90/30, with a to-do consumer.
  - New API `fix.partner.authorisation.fix_assert_brand_authorised(brand, what)`. M09/M01 do not call it yet.
- **F16 (partial).**
  - The allocation price comes from `price_for(channel='reseller')`.
  - New model `fix.reseller.draw` raises an invoice and a stock move. The stock-move path is untested.
- **F17:** duplicate checks use `child_of` on the commercial entity.
- **F20:** new field `fix.partner.brand_id`. It must agree with `fix.brand.partner_id` (B3's field).
- **F21/F22:** all 13 packs read through `_scope`. KPI fixes:
  - "Brand Partners" counts active brand partners;
  - "Partner Revenue" is referred revenue;
  - the audit calendar includes `fix.brand.audit`;
  - the health score is factor-based. Its weights and bands are OWNER.
- **F24:** new states probation, dormant, exiting and exited. An exit is refused while money is unsettled. The dormancy cron needs `cd_partner.dormancy_days` (OWNER).
- **F27:** a stored related `company_id` on 13 child models, plus company rules.
- **F29:** group names are read with sudo.
- **F30:** tier changes are staged with an effective date and applied by a cron.
- **X3:** partner events now have consumers or inline billing.
- **M08-F4 / M38-F18:** `_ar_posting_dims` now carries the OU: the branch's OU first, then the explicit argument, then the invoice's own OU.
- **M37-F2:** `_fix_item_tax_keys` passes `hs_code` to M51 and applies an exempt/zero `vat_class` only when no tariff row exists. This covers the `_fix_determined` build only.
- **X10:** the invoice-number sequence takes a waiting `FOR UPDATE` with `lock_timeout` 15s.

## OWNER
- F15: appoint holders for the partner roles.
- F25: the payable reconcile flag, and the M51 TDS register.
- F26: one MDF mechanism or two.
- Account parameters (all fail closed). Recommended codes:
  - royalty income: 400109 Other Income;
  - franchise fee: 400109;
  - rebate expense: 500306 Sales Commission;
  - MDF expense: 500210 Marketing Expense.

## DEFERRED
- F23: M07 hand-off.
- F28: alliance benefit link.

## Files
- **cd_partner:**
  - manifest 19.0.0.3.1;
  - models: `fix_partner.py`, `fix_partner_ops.py`, `fix_partner_capture.py`, NEW `fix_partner_a04erp.py`;
  - `controllers/partner_api.py`;
  - security: ACL, `fix_partner_security.xml`, NEW `fix_partner_a04erp_rules.xml`;
  - NEW `data/fix_partner_a04erp_data.xml`;
  - tests: NEW `m40_fixtures.py` and `test_a04erp_b5_m40.py`; 5 existing tests edited.
- **cd_settlement_ext:** `fix_settlement_m53.py`.
- **cd_billing_engine:** `fix_billing_engine.py`.
- **cd_p03_portal:** `controllers/a04/m40.py`, `static/src/a04/m40.js`, `writable.py`.

`-u` on deploy: cd_billing_engine, cd_rate_card, cd_partner, cd_settlement_ext, cd_p03_portal.

## Expected test breakage (old behaviour encoded)
- cd_partner: `test_comarketing_links.py`, `test_partner.py`, `test_partner_live.py`.
- cd_settlement_ext: `test_a04_c7_settlement_consumers.py`, and the `test_a08_m53_*` referral tests.

## Needs from others
- M09/M01 must call `fix_assert_brand_authorised`.
- The A02 billing owner: the service-order TaxLine build (~l.1256) still omits `hs_code`.
- B3: confirm the `fix.brand.partner_id` design.
- The Mushak 6.3 sequence also uses NOWAIT.

## Round 2 (21 Nov): VERIFIED on fix_test_a04base
- **New tests:** 26/26 pass.
- **Suites:**
  - cd_partner: 146 passed, 0 failed, 1 skipped.
  - P03 `test_m40_capture_buttons`: 57/57.
- **Mutants:** 21/21 killed, injected in memory through a pytest plugin (`%TEMP%\a04erp\B5\mut\b5_mutants.py`).
- **Fixes the test runs found:**
  - the F7 window opens at min(Dhaka day, UTC day), because M20 dates invoices in UTC;
  - Tier 3 can write `fix.partner.rate.change`;
  - the referral link code now uses `token_hex`.
- **cd_settlement_ext:** 176/203 pass, down to 27 failures from 85. None of the 27 is on a partner path:
  - 21 are marketplace (M12-F1/F4), handed to B4;
  - 3 are the M39 billing-run gate (m53_28/29/30);
  - 2 are A02 `test_a02_p1p2` refund unpacking;
  - 1 is M08 m53_13.
- **cd_billing_engine:** 3 order-dependent failures in `test_contract_revenue_recognised`. They pass when run alone, and also pass with B5's changes reverted.
- **Billing notes:**
  - M20 `invoice_date` defaults to the UTC date;
  - the service-order TaxLine build (~l.1256) omits `hs_code`;
  - the Mushak 6.3 sequence still uses NOWAIT.
