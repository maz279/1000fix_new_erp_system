# R1 findings: M37 catalogue and M11 pricing (20 Nov 2026)

- Probes are in `%TEMP%\a04erp\R1\`: q1-q5 SQL, p1_resolution, p2_controls, p3_override_lifecycle, rounding.
- All ORM probes ran on fix_real_a04 and were rolled back. User-level checks ran as md.akram (uid 1525, Quotation User) and tanjin.rabby.
- Counts: P0 1, P1 15, P2 15, P3 2.

## Headline
fix_real has no M11 price at all:
- 0 rate cards, books, versions, promotions, discount bands, parts schemes, premiums and brand rates;
- 4 floors, all seed rows on product codes that do not exist;
- all 16,100 stocked items have `list_price` = 1.00, and the 78 services have 0.00;
- M15 holds real cost for 8,008 parts (BDT 42.8M in total; the maximum is 548,493.46).

M36 falls back to list price and M38 uses list price only. So a real order is priced at BDT 1.00, and `_fix_check_sale` passes at 1.00 and even at 0.01.

## M11
| id | sev | finding | evidence | fix |
|---|---|---|---|---|
| F1 | P0 | **Real orders are priced at the 1.00 placeholder, far below M15 cost, and nothing refuses it.** | q3, p1 (`_resolve_price` → (1.0, 'list'); 0.01 passes), p2; `fix_quote_scope.py:126-144`, `fix_storefront.py:333-353` | No released price means no price. Add a cost-margin floor in `catalogue_approval.py:111` from M15 average cost. |
| F2 | P1 | **BRU-PRC-01 is broken.** `_resolve` is called only by M36 (`fix_quote_scope.py:133`) and the contact-centre FAQ. These all type their own price: M01 estimate (`fix_estimate.py:996`), M38 (`fix_storefront.py:339`), M12 listing, M08 top-up (`fix_contract_capture.py:431`), M39 (`fix_subscription.py:112`, `fix_m39_capture.py:144`). | grep, p1 | One `price_for(product, partner, channel, qty, date, company, contract)` service. A typed price is recorded as an override with its reason. |
| F3 | P1 | **M36 passes no tier, contract, date, company or currency.** The engine gives tier 2 = 900; M36 gives 1000. | p1 | Pass the context; define where a customer's tier lives (M33). |
| F4 | P1 | **Effective dating is impossible.** The unique key (code, tier, contract) refuses next year's card, and changes overwrite `unit_price` in place. | p1 UniqueViolation; `fix_rate_card.py:56`, `fix_price_change.py:204`, `fix_m11_capture.py:972` | Key on `valid_from` with no overlaps; resolve on the document date. |
| F5 | P1 | **Books and versions price nothing:** no card links to a book or version. Approving an older-dated version supersedes the newer one. | p1, p2; `fix_pricing_ops.py:312, 326-345` | Add `version_id` to the card; never activate an older version over a newer one. |
| F6 | P1 | **Discount authority can be bypassed by typing a price.** Estimate DOFA reads only the header discount; the list floor parameter is unset; M36's off-list measure uses list 1.00, so it shows 0%; promotions are not counted in the cumulative discount. | `fix_estimate.py:119, 1028`; `fix_quote_scope.py:99-110, 311` | Per-line list price; cumulative off-list % (FR-PRC-031); floor check always on. |
| F7 | P1 | **A below-floor override acts as a standing permission.** After one approval, 600 (storefront), 650 (another user) and 600 (quotation) all pass. It has no expiry and no link to a document. | p3; `fix_pricing_ops.py:555-575` | Bind the override to the line; single use; dated. |
| F8 | P1 | **A rate can be set below its floor.** 1000 → 500 under a 950 floor is accepted, and a card can be created at 400. Only mass change checks floors. | p1; `fix_price_change.py:124-154`, `fix_rate_card.py:220` | Floor check in `_validate` and `_check_card`. |
| F9 | P1 | **There is no margin floor against cost (FR-PRC-028).** The dynamic `_floor_for` matches by code only, so it misses item-keyed floors. | p3; `fix_dynamic_pricing.py:185` | `margin_floor_pct` × M15 cost; use `_floors_for`. |
| F10 | P1 | **Nothing that sells calls promotions, dynamic rules, premiums, parts schemes or brand rates.** A 20% promotion leaves the M36 price unchanged, and M09 has no rate field. | p1, p3 | Chain them in the F2 service; M09 calls `rate_for`. |
| F11 | P1 | **The live price can be edited with no control.** `product.template.list_price` (and the charge code's `default_rate`, which writes it) has no maker-checker and no trail. | q5; `fix_commercial_line.py:90, 234` | Guard `list_price`; move charge rates to M11. |
| F12 | P1 | **Pricing roles are thinly held.** Price-Book Releaser = {admin, emdadul.haq}; Pricing Officer has no direct holders; immediate mass change = {admin, ashish, rizwan}; the matrix has no pricing_* or catalogue_* rows. | q3, q4 | Owner: appoint holders. |
| F13 | P2 | **No ir.rule on card, floor or version, and the floor has no company_id.** The resolver ignores company: a company-2 card priced a company-1 lookup. | p1 | Add company_id, rules and filters. |
| F14 | P2 | Currency is ignored in `_resolve`. | `fix_rate_card.py:181` | |
| F15 | P2 | **The VAT basis differs by channel.** Cards are exclusive; the storefront is inclusive (`fix_storefront_books.py:477-515`); M36 hard-codes vat_rate 15 (`fix_quote_ops.py:229`). | STATIC | Tax mode in the resolver; rate from fix.tax.rate. |
| F16 | P2 | **Rounding is inconsistent:** HALF_EVEN, HALF_UP and float round are all used (1.54 vs 1.55). | rounding.out | One `_money`. |
| F17 | P2 | Corridor parameters are unset (−50/+100% defaults) and the rule type does not constrain the sign. | p1, q2 | |
| F18 | P2 | **All 8 packs and the KPIs are unscoped:** they read with sudo across every company and ignore the period. `realised_vs_card` reads explanations, not sales. Margin uses `standard_price` = 0. | p2; `controllers/a04/m11.py` | |
| F19 | P2 | **Missing:** FR-PRC-012 (labour × SRT), 017, 020, 010, 032, 036/045, AUT-PRC-08..12 (no consumers), 039/040. | spec | |
| F20 | P3 | A card can be released for a nonexistent code or a Draft item. | q4 | |

## M37
| id | sev | finding | evidence | fix |
|---|---|---|---|---|
| F1 | P1 | **Every item is Active with no classification.** All 16,178 have no VAT class, revenue pattern, Bengali name or approver. The sale gate is unset, so a Draft item sells. | q2, p1 | Refuse customer channels for items with no VAT class (`fix_catalogue_item.py:469-505`); classify the items in bulk. |
| F2 | P1 | **`hs_code`/`vat_class` never reach M51.** The billing TaxLine is built without them (`fix_billing_engine.py:1759-1770`), so exempt items are taxed at 15%. | STATIC | Pass them in M20 billing. |
| F3 | P1 | rBOMs and kits never explode into estimate lines or M15/M41 demand (FR-CAT-028/041). | | Explosion plus a requisition hook. |
| F4 | P1 | **Downstream channels ignore the item lifecycle.** M01 `catalog_item_id` does no out-of-scope or discontinued check (`fix_service_order.py:433`); M12 never calls `_fix_check_sale`; M38 does not require `is_published`. | p3 | |
| F5 | P2 | Plan definitions are unused by M39, `repair_warranty_days` is unused by M01, and the M09 warranty product links `product.template`. | | |
| F6 | P2 | A discontinued item is refused even for contract-covered devices (BRU-CAT-10; `fix_catalogue_item.py:480`). | | |
| F7 | P2 | Supersession is never resolved, and catalogue events have no consumers. | | |
| F8 | P2 | **Packs are unscoped, and `item_margin` is wrong:** it reports "16178 of 16178 fully costed" at 100% margin. `new_skus_mtd` = 16,178. Exports are capped at `rows[:200]`. The `rbom_coverage` formula is wrong. | p2; `controllers/a04/m37.py` | |
| F9 | P1 | **Catalogue Officer and Publisher are held only by admin.** | q4 | Owner. |
| F10 | P2 | The charge code's `default_rate` is a price with no M11 release (BRU-CAT-01). | | |
| F11 | P2 | Compatibility is checked only on rBOM lines; FR-CAT-046, 007 and 015 are missing. | | |
| F12 | P3 | `fix.rbom.line` and `fix.charge.code` have no company rule. | | |

**P03 capture:** every M11/M37 writable field exists on its model. The only guarded create field is `fix.discount.approval.state`, and the guard refuses it.

## Cross-area
- **M01:** estimate prices are typed, line discounts escape DOFA, and intake does not check the catalogue.
- **M36:** the resolver call lacks context, falls back to list 1.00, and hard-codes VAT 15.
- **M38:** uses list price on an inclusive basis, with no `is_published` check and no promotions.
- **M12:** no sale check.
- **M09:** ignores the brand rate.
- **M39:** amounts are typed.
- **M20/M51:** `hs_code`/`vat_class` not passed.
- **M15 → M11:** cost is read nowhere.
- **M63:** no matrix rows.

## Facts on fix_real_a04
- Companies: 1, 2 (My US Company), 3 (Chicago).
- Parameters unset:
  - `cd_catalogue.sale_requires_active_item`;
  - `cd_service_order.estimate_price_floor`;
  - corridor min and max.
- Discount ladder: the spec default.
- Data:
  - 3 dynamic rules;
  - 91 charge codes, none with a rate;
  - `standard_price` empty on all 16,191 products;
  - 0 A04 documents.
- Role holders:
  - DOFA tiers T1-T5: 20 / 42 / 7 / 3 / 1;
  - Quotation Manager 47, Quotation User 220;
  - Service Commercial Approver 2.
