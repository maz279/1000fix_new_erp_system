# A04 Commercial, Pricing & Revenue: ERP audit and fix (20-21 Nov 2026)

**Scope.** The nine A04 modules were audited as one ERP area:
- M37 Catalogue, M11 Pricing, M36 Quotation/Tender;
- M08 Contracts, M09 Warranty/Protection, M39 Subscriptions;
- M38 Storefront, M12 Marketplace, M40 Partner/Franchise.

Each module was checked against its spec (FR / BRU / AUT), data capture, flows and states, rules and approvals, calculations, accounting on the real fix_real chart, cross-module links, KPIs, reports and exports, and security.

**Where the work is:**
- branch `fix/a04-erp-audit` (worktree `1000 fix/a04erp-wt`, base d0589b7b);
- evidence in `audit_analysis/evidence_a04_erp/`, holding the auditors' R1-R5 findings and the builders' B1-B5 reports.

## Method
1. **Audit.** Five read-only auditors measured every money flow end to end on `fix_real_a04`, a copy of production fix_real with the 376-account legacy chart and real users. Every probe was rolled back, and access was tested as real non-superusers.
2. **Fix.** Five builder streams worked with strict file ownership, each on its own test database:
   - every fix ships with an ORM test;
   - every main fix had a mutation check: the defect was put back and a test had to go red.
3. **Integrate.** The lead reconciled the cross-stream tests, upgraded every changed module on one integration DB (with the same finance bridges installed as fix_real), and ran the combined regression. Results are in "Verification".

## What was wrong (the headline)
About 185 findings. The P0s were money that never reached the ledger, or reached it wrong:
- **Every real price was a placeholder.** All 16,191 sellable items carry list_price 1.00 or 0.00, and M11 had no price at all. M36 fell back to that price and M38 sold at it: 3 chargers for BDT 3.00, and a BDT 0.00 order.
- **M39 subscriptions:**
  - revenue recognised twice: 5,868 recognised on 3,000 billed;
  - a cancellation kept recognising revenue (10,780 in 90 days);
  - a refund left revenue overstated;
  - an autopay success never became a receipt.
- **M08 contracts:**
  - suspended months were billed;
  - a termination penalty, the stub days and top-ups were never invoiced;
  - a 12-month AMC was billed as 13 thirty-day periods.
- **M36 tender:** the award billed VAT twice (115,000 billed 132,250).
- **M09 warranty:**
  - no brand could be billed for a claim (0 of 161 brands mapped to a party);
  - protection plans never touched the ledger;
  - a write-off posted nothing.
- **M38 storefront:**
  - a paid order cancelled before posting lost the money;
  - one return refunded twice;
  - 0.01 of an item could be bought.
- **M12 marketplace:** sales booked cash that was never received (the debit went to 101404, a legacy bank account).
- **M40 partners:** the franchise royalty, the initial fee and MDF claims stopped at a status field, with no invoice and no payment.
- **Reports:** 96 of 96 A04 report packs ignored the requested period, and about 60 read across companies.
- **Approvals:** most A04 approver roles have no holder apart from admin.

## What was built, per module
| Module | Findings | Fixed | Owner | Deferred | Stream report |
|---|---|---|---|---|---|
| M11 Pricing | 20 | 16 (+2 partial) | 1 | 1 | B1_report.md |
| M37 Catalogue | 12 | 8 (+2 partial) | 1 | 1 | B1_report.md |
| M36 Quotation/Tender | 17 | 15 (+F13 by the lead) | 1 | 0 | B2_report.md |
| M08 Contracts | 22 | 19 (+2 partial) | 1 | 0 | B2_report.md |
| M09 Warranty | 18 | 12 (+1 partial) | 2 | 3 | B3_report.md |
| M39 Subscriptions | 19 | 14 | 1 | 4 | B3_report.md |
| M38 Storefront | 21 | 13 (+1 partial) | 3 | 5 | B4_report.md |
| M12 Marketplace | 16 | 13 | 1 | 2 | B4_report.md |
| M40 Partner/Franchise | 30 | 24 (+2 partial) | 2 | 3 | B5_report_round1.md |

**Cross-area work:**
- the M20 GL now carries the invoice's operating unit;
- the catalogue item's HS code and VAT class reach M51;
- the invoice-number lock waits instead of failing;
- one report-scope helper, `controllers/a04/_scope.py`.

**The pieces to know:**
- **One M11 price service**, `fix.rate.card.price_for` / `check_sale_price`. Every selling channel prices through it:
  - order: contract, then customer, then tier, then standard card; then promotions and dynamic rules inside the floor;
  - effective-dated and company-scoped;
  - floor = the M11 floor or the M15 cost margin floor;
  - an override below the floor is single-use and bound to one line.
- **Money now reaches M20/M50 and the GL** for:
  - subscription cancel and refund, autopay, contract termination, top-up, retention and bonds;
  - tender VAT;
  - protection premium, reserve, settlement and refund; claim write-off; brand receivable;
  - storefront cancel-refund; the marketplace customer receipt and commission VAT;
  - franchise royalty, initial fee, MDF and rebate payouts with TDS.
- **New consumers** for events that move money: terminated, topped_up, variation_approved, quotation.declined, autopay_succeeded, order_cancelled, dispute_resolved, chargeback_lost, mdf_claim_approved, authorisation_expiring.
- **New crons:** service credits, PM dispatch, entitlement reset, proration due, storefront payment expiry, tier changes, override expiry.
- **Printouts:**
  - a contract printout with a Print button on the contracts list;
  - the quotation PDF prints its issue date and its terms and exclusions.

## Owner decisions (nothing was fabricated; every mechanism fails closed)
1. **Prices.** Release M11 rate cards. Until then:
   - the storefront sells nothing;
   - M36 refuses unpriced product lines;
   - M01 typed prices are checked against M15 cost.
2. **Role holders** (each held only by admin, or by nobody):
   - Pricing Officer and Price-Book Releaser are the same person;
   - Catalogue Officer and Publisher;
   - Tender Committee, Legal Reviewer;
   - Warranty Officer;
   - Subscription Officer;
   - every storefront role, plus the new assisted-sales role;
   - marketplace operator, compliance, arbitrator;
   - every M40 role.
3. **Account roles** (recommended codes all exist on fix_real):

   | Use | Code(s) |
   |---|---|
   | Contract revenue by family | 400107 / 400108 / 400100 |
   | Termination penalty | 400109 |
   | Retention receivable | 100031 |
   | Bond margin / deposit / charges | 100035 / 100031 / 500226 |
   | Warranty provision / cost | 200002 (or 200005) / 500229 |
   | Claim income | 400110 |
   | Franchise royalty / fee | 400109 |
   | Rebate expense | 500306 |
   | MDF expense | 500210 |
   | Marketplace collections | 100201, or 200016 |
   | Commission income | currently 400100 |
   | Bond encashment loss | 500906 vs 500226 |
   | Partner payable 32656556 | needs reconcile switched on |
4. **Business data:**
   - 161 brand billing partners;
   - a COD rule;
   - gateway secrets;
   - a seller commission scheme, plus the M51 D-03 marketplace position;
   - `labour_cost_per_hour`;
   - payment timeout;
   - the corridor limits.
5. **Tax:**
   - whether VAT applies to OEM reimbursement, the protection premium and the termination penalty;
   - switching on `warranty_requires_verified` once officers exist.
6. **Policy switches, default off:**
   - `cd_warranty_claims.require_brand_rate` and `require_brand_authorisation`;
   - `cd_catalogue.sale_requires_active_item`.

## Round 1 is LIVE (21 Nov 2026, 15:24)
- **How it went live.** The user approved "Deploy both". The A02 combined wave upgraded 33 modules on fix_real and fix_dev, all 18 A04 modules among them, then restarted 8069 and 8090 once.
- **Live check** (`verify_a04_live.py`): ALL OK on both ports.
  - Every new A04 list is served with no dropped columns.
  - The web bundle carries the new screens.
  - The logs show 0 ERROR lines since the restart.
- **Doc-suite tests.** `cd_doc_suite`'s 20 TransactionCase errors were not product errors. That test class could not run under pytest, so no suite PDF was ever rendered in CI. It now runs on the odoo_env fixture: 20/20 PDFs render and every mail template attaches its PDF. Shared branch bc204bd6.

## Round 2: the deferred items, built (21 Nov 2026)
Four more streams built what round 1 had deferred, wherever no owner data is needed. Each stream report is in `evidence_a04_erp/R2-*_report.md`.

| Stream | Built | New tests | Mutants red |
|---|---|---|---|
| R2-1 M38/M12 | M38-F14 (server-priced delivery fee and voucher), F20 (idempotent placement, customer self-cancel), F19 (published / VAT-classed catalogue, compatibility filter), F8 (per-line returns); M12-F7 (customer data masked before award), F15 (award acceptance window and lapse, seller probation cap) | 40 | 19/19 |
| R2-2 M09/M39 | M09-F13 (brand rules at submit), F12 (chase cron, ageing), F15 (plan limits, depreciation, DOFA value bands), F16 (submission record, fault-code map, brand performance pack); M39-F16 (price-increase notice), F17 (usage and service-gate consumers), F11 (one billing engine per contract); M37-F5 links | 29 | 18/18 |
| R2-3 M11/M37 | M11-F19 (labour rate × SRT, volume breaks, channel differentials, public indicative band, override log, AUT-PRC-08..12 reviews and scans); M37-F5/F7/F11 (plan hook, repair warranty from the item, live successor, impact preview, numbering, skill bands); M11-F15 (VAT by VAT class) | 26 | 18/20 (2 blocked by a second layer) |
| R2-4 M40 | F23 (deal conflicts and M07 hand-off), F26 (one MDF mechanism), F28 (alliance benefit as a member-only M11 promotion), F25 (partner TDS through M51 for rebate and MDF payouts), F14 (authorisations-expiring pack) | 17 | 21/21 |

**Still not built, with the reason:**
- Referral payout-run TDS on the M51 no-TIN default: a statutory reading for A08/M51 to confirm.
- FR-SUB-025: late usage is not re-rated into the next period.
- Promotions that `price_for` applies by itself do not consume their budget in the storefront.
- The `fix.storefront.rma` legacy model returns whole orders only.
- Consumers for `pricing.*` and `catalogue.item_activated` events: the spec puts them in M36/M38/M12/M25.

**New owner settings (all fail closed or default safe):**
- delivery fee codes; voucher flags;
- award window, probation cap, brief length;
- DOFA value bands for protection claims; chase days; notice days; suspended-service policy;
- channel spread, margin target, leakage alert;
- labour rates, skill bands, numbering masks;
- partner TDS rate code;
- confirm the Managed Services billing default (D8).

## Deferred in round 1 (see round 2 above for what was built since) beyond the audit's fix scope, listed honestly)
- M11-F19: labour rate × SRT, and AUT-PRC-08..12 consumers.
- M37-F5 / F7 / F11 rest.
- M36: none left.
- M09:
  - consignment parts, brand performance, fault codes, outbound submission and evidence pack;
  - the chase cron;
  - value-band DOFA.
- M39:
  - the price-increase notice;
  - usage and suspension consumers;
  - M39-F11, which needs an owner decision on whether M08 or M39 bills a contract.
- M38:
  - per-line returns;
  - voucher, loyalty and delivery fee;
  - guest OTP;
  - card reversal rail;
  - catalogue-driven publishing.
- M12: data masking before award; payout verification and wallet.
- M40: the M07 hand-off; one MDF mechanism; the alliance benefit link.

## Verification

**Per stream.** Every fix has an ORM test, run as real non-superusers where access matters, and a mutation check: the defect was put back and the test had to fail.

| Stream | New tests | Mutants red |
|---|---|---|
| B1 | 47 | 15 of 16 (the 16th is covered by a second guard layer) |
| B2 | 49 | 22 of 22 |
| B3 | 43 + 2 | 14 of 14 + 2 |
| B4 | ~43 + 1 | 14 of 14 + 1 |
| B5 | 26 | 21 of 21 |

**Integration DB.** `fix_test_a04b2` and `fix_test_a04erp`, with every changed module upgraded from the committed tree, plus the finance bridges `cd_front_desk_finance` and `cd_storefront_finance` that fix_real has.
- **cd_p03_portal, full suite:** 6,665 tests, 5 failures.
  - All 5 were tests that needed to follow the new rules: A12 checkout needs a released price, a gateway and a callback secret; M53 billing is run-only; the M40 draw form is pick-only.
  - All 5 are updated, and the re-run passes.
- **A04 and neighbouring module suites:** 2,866 tests. The 18 suites:
  - cd_rate_card, cd_dynamic_pricing, cd_catalogue;
  - cd_service_order, cd_quotation, cd_contract_core;
  - cd_billing_engine, cd_warranty_claims, cd_subscription;
  - cd_storefront, cd_storefront_finance, cd_marketplace;
  - cd_partner, cd_settlement_ext, cd_cash_position;
  - cd_doc_suite, cd_front_desk_finance, cd_msp_contract.
- **Result:** 2,842 passed, 2 skipped, 4 failures, 20 errors.
  - The 20 errors are `cd_doc_suite TestDocSuiteRendering` setup errors. They are identical on the base code (an Odoo TransactionCase run under pytest), so they predate this work.
  - The 4 failures are `cd_billing_engine test_m20_capture_pass2`, off by one day. The shard started at 05:55 Asia/Dhaka, inside the known 00:00-06:00 Dhaka window, and all 22 tests pass on re-run.
- **A04 code outcome: 0 failures.**

**fix_real copy (`fix_real_a04`).** The upgrade of all 18 changed modules on real data exits 0, with 0 ERROR lines. The readiness probe (`evidence_a04_erp/LEAD_readiness_fix_real_copy.md`) shows:
- BDT 1.00 is refused for a real part with an M15 cost of 2,229.24, on quotation and service;
- the storefront refuses it, because there are 0 released rate cards;
- the ageing cron captures the 31 Oct month-end;
- all 96 A04 report packs run with a period, with 0 errors;
- the owner parameters are unset, and their mechanisms fail closed.

**Not covered.**
- No browser walk of the changed screens: the P03 static guards and form/whitelist tests stand in for it.
- The base comparison was run only for failing tests.
- Nothing is deployed yet: deploying needs the user's approval and one restart coordinated with the A02, A05 and A07 sessions.

**Also fixed on the way (outside A04, found by the A07 session):** the monthly AR ageing cron on fix_real (id 193) called a method that did not exist, so it failed every month. The method is restored, with a test.
