# R2-1 (round 2, M38/M12 deferred items), 21 Nov 2026

## Fixed
- **M38-F14: checkout fee and voucher, priced on the server at placement.**
  - **Delivery fee:** `cd_storefront.delivery_fee_code.<method>` names a product priced by `price_for` plus VAT, added as a `delivery` line. A named code with no released price refuses the order; an unset param means no fee.
  - **Voucher:** `fix.promotion.storefront_voucher` runs through the M11 engine at checkout (never below the floor, consumed once) and is shared across the goods lines.
  - **Invoice:** issued at net per line plus the fee. Example: 2×2,500 − 500 + 115 = 4,615, posting Dr AR 4,615 / Cr revenue 4,013.04 / Cr VAT 601.96.
- **M38-F20:**
  - an idempotency key, unique per customer, so a replay returns the same order;
  - customer self-cancel through the round-1 refund path.
- **M38-F19 (partial):**
  - the catalogue lists only items published in M37 with a VAT class and a released price;
  - a device-compatibility filter.
- **M38-F8: per-line returns.** New model `fix.storefront.return.line`.
  - Whole units, never more than were sold, frozen once authorised.
  - Restock and credit happen per line.
  - A05's refurbished path is preserved.
- **M12-F7:** the customer's name, contact and description get field-level groups. Sellers see masked brief, initials and contact fields; the full view goes to the awarded seller only.
- **M12-F15 (partial):**
  - an award acceptance window (default 24h) with a lapse cron, and the job cannot start before acceptance;
  - a provisional standing with a job cap (default 3).

## Tests
- New: 40 functions, 43 cases, all passing.
- Mutants: 19/19 killed.
- Owned suites: 493/498 in run 2; the 4 new-test fixes then passed in run 3.

## Deploy
- Versions: cd_storefront 19.0.0.2.3, cd_storefront_finance 19.0.0.1.2, cd_marketplace 19.0.0.4.2.

## Owner
- Fee codes per shipping method, and their M11 cards.
- Which promotions are checkout vouchers.
- The award window, the probation cap and the brief length.
- How existing sellers start: the standing column defaults to provisional.

## Needs from others
- `storefront_voucher` on the M11 promotion form (lead).
- Promotions that `price_for` applies by itself do not consume their budget in the storefront.
