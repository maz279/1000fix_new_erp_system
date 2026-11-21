# B1 report: M11 pricing and M37 catalogue (21 Nov 2026)

## Price service
File: `cd_rate_card/models/fix_price_service.py`.

`fix.rate.card.price_for(...)`:
- returns `price`, which is None when no price is released; it never falls back to list_price;
- precedence: contract card, then customer card, then tier card (`res.partner.fix_price_tier`, set by a Pricing Officer), then the standard card, then a parts scheme on M15 cost;
- after the card, adds premiums, applies the best promotion and, on customer channels, the dynamic rule. Both are capped at the floor;
- effective on the document date, filtered by company and currency;
- VAT-exclusive, with the rate taken from M51.

`check_sale_price(...)`:
- floor = max(the M11 floors, M15 cost × (1 + `cd_rate_card.margin_floor_pct`));
- below the floor, a sale is refused unless an approved, single-use `fix.price.override` is bound to that line;
- customer channels refuse a line when the price is None.

Also exposed: `rate_for` / `reimbursement_for` (M09), and `_fix_check_sale` on product.product and fix.catalogue.item.

## Findings
- **M11-F1:** FIXED. M36 no longer falls back to list price. An M01 typed price is checked against the M15 cost floor.
- **M11-F2/F3:** FIXED.
  - The M36 resolver now gets the full context, and `_check_sellable` passes line and partner.
  - Estimate lines get a stored `unit_price` default from `price_for`, plus `card_price`, `price_source` and `price_override_reason`.
  - A typed price that differs from the card needs a reason.
  - The line total is still qty × unit_price.
- **M11-F4:** FIXED. Cards are keyed by (company, code, tier, contract, partner, valid_from) and checked for overlaps. Price changes and mass changes create dated versions.
- **M11-F5:** FIXED. Cards carry `version_id`. An older version never displaces a newer one.
- **M11-F6:** FIXED. The DOFA amount is the cumulative discount off released prices, and the floor check is always on.
- **M11-F7:** FIXED. New model `fix.price.override`: bound to one line, its DOFA tier set by how far below the floor, routed through M63, single use, with a use-by date and an expiry cron.
- **M11-F8:** FIXED. The floor is enforced in `_check_card` and in the price-change `_validate`.
- **M11-F9:** FIXED. The cost margin floor; the dynamic rule uses `_floor_info`.
- **M11-F10:** FIXED. Promotions, dynamic rules, premiums, schemes and brand rates are all chained into `price_for`.
- **M11-F11:** FIXED. `list_price` writes need the Pricing Officer, even under sudo, and leave a trail.
- **M11-F12:** OWNER. The Pricing Officer and Releaser roles are held by the same people: admin and emdadul.haq.
- **M11-F13:** FIXED. company_id and rules added; the resolver filters by company.
- **M11-F14:** FIXED. Currency.
- **M11-F15:** PARTIAL. The service is VAT-exclusive. M36's hard-coded 15 (B2) and M38's inclusive basis (B4) remain.
- **M11-F16:** FIXED. One half-up `money` helper.
- **M11-F17:** FIXED. The rule type constrains the sign. The corridor values are OWNER (defaults −50/+100).
- **M11-F18:** FIXED. Packs and KPIs read through `scoped()`. "Realised vs card" reads sold lines. Margin uses M15 cost.
- **M11-F19:** DEFERRED. New spec features: FR-PRC-012/017/020/010/032/036/045 and AUT-PRC-08..12.
- **M11-F20:** FIXED. Release refuses an unknown code or a non-Active item.
- **M37-F1:** FIXED. Customer channels refuse items with no VAT class; storefront and web require the item to be published.
- **M37-F3:** FIXED (mechanism). `_fix_explode` (rBOM and kit, depth-bounded), `_fix_part_demand`, and `fix.estimate.action_explode_catalogue_item`.
- **M37-F4:** FIXED. A service-order lifecycle constraint, plus `_fix_check_sale`.
- **M37-F5:** DEFERRED. The consumers belong to M39, M01 and M09.
- **M37-F6:** FIXED. A discontinued item is still allowed on contract channels.
- **M37-F7:** PARTIAL. `_fix_live_successor` exists; the event consumers are deferred.
- **M37-F8:** FIXED. Reports corrected; the 200-row export cap removed.
- **M37-F9:** OWNER. Catalogue Officer and Publisher: admin only.
- **M37-F10:** FIXED. `default_rate` is now reference only.
- **M37-F11:** PARTIAL. Explosion refuses a part that does not fit.
- **M37-F12:** FIXED. company_id on rBOM line and charge code.

## Tests
- New tests: 47/47 pass (37 in cd_rate_card, 10 in cd_catalogue).
- Its own suites: 253/253 after one test was rewritten.
- Targeted M01/M36 suites: 202 pass, 6 fail. All 6 are intended behaviour changes in files B1 does not own (next section).
- Mutants: 15 of 16 killed. The one that survived ("F7 `_use_for` removed") is covered by a second layer, `_bound_to`; the stronger mutant was never run.

## Needs from others
- **B2:**
  - three `test_a04_m36_controls` tests: the monkeypatch must accept `**kw`, and there is no list fallback any more;
  - `test_award_is_a_committee_decision`: 700000 vs 608695.65, which is the tender VAT basis;
  - `fix_quote_ops.py:229` hard-codes VAT 15.
- **Lead:**
  - cd_service_order tests `test_a02_authz_accuracy_m01::test_list_price_floor_applies_to_a_labour_line_with_a_product` and `test_a02_p0_m01::test_price_below_list_needs_the_discount_route` expect the old list-price floor;
  - bump cd_service_order's manifest;
  - `price_override_reason` on the M01 estimate-line P03 form.
- **B4:** use `price_for` and `_fix_check_sale(line=)`, on the inclusive-to-exclusive basis.
- **B3:** use `reimbursement_for`.
- **M41/M15:** consume `_fix_part_demand`.

## Manifests and deploy
- Manifests: cd_rate_card 19.0.1.2.1, cd_catalogue 19.0.1.4.1, cd_dynamic_pricing 19.0.0.1.1.
- `-u` on deploy: cd_catalogue, cd_service_order, cd_rate_card, cd_dynamic_pricing, cd_p03_portal.
