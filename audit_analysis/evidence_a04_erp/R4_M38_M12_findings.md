# R4 findings: M38 storefront and M12 marketplace (20 Nov 2026)

Measured on fix_real_a04 with every probe rolled back. Probes are in `%TEMP%\a04erp\R4\` (p0-p6, q1-q5).

Path prefixes:
- SF = `addons/domain/b_customer_engagement/cd_storefront`
- SFF = `.../cd_storefront_finance`
- MKP = `addons/domain/d_circular/cd_marketplace`
- P03 = `addons/platform/cd_p03_portal`
- SET = `addons/domain/g_finance/cd_settlement_ext`
- CP = `addons/domain/g_finance/cd_cash_position`

Counts: P0 5 (M38 4, M12 1), P1 15, P2 14, P3 3, plus 10 cross-area items.

## M38: measured as correct
- **bKash order:**
  - The invoice INV/2026/00001 posts Dr 100201 2,300 / Cr 400102 2,000 / Cr 200902 300 (15% inclusive), with a Mushak 6.3.
  - The capture is an M20 receipt (Dr 100111 / Cr 100201), allocated.
- **COD:** the invoice is raised at dispatch, and POD books a cod receipt Dr 100204 / Cr 100201.
- **Stock:** issued from M15 at dispatch and restocked on return.
- **Cancelling a paid order:** raises an M20 credit note, pending approval. Its GL mirror is correct.
- **The 3 Nov C1 portal fix holds,** proven with a fresh portal env:
  - no cart create;
  - no total or price write;
  - no other customer's order;
  - no direct return.

## M38
| id | sev | finding / evidence | fix |
|---|---|---|---|
| F1 | P0 | **The price comes from `product.template.list_price`, not M11.** fix_real has list_price 1.00 on 16,100 products and 0.00 on 91, with 0 rate cards and 0 pricelist items. p5: 3 chargers came to BDT 3.00, and one order to BDT 0.00. Code: `SF/models/fix_storefront.py:333-339, 349-353, 156-159`; `SF/controllers/storefront_api.py:219, 271` | Price each line through M11 for the "storefront" channel and store the price lock. Refuse a missing or ≤0 price. Show only priced items. |
| F2 | P0 | **A gateway-paid order cancelled while its posting is pending:** no receipt, invoice, credit or refund instruction; posting goes to "none". `storefront.order_cancelled` has no consumer. p6. Code: `SFF/models/fix_storefront_books.py:360-363, 377-384`; `SF/models/fix_storefront.py:900-923` | Capture the receipt, then raise an M50 refund on the original rail. Posting must never go to "none" while refund_due > 0. |
| F3 | P0 | **Double refund.** The relay consumer's M50 path (`CP/models/fix_a04_storefront_consumer.py:85-157`) and the bridge credit note (`SFF/models/fix_storefront_refund_books.py:325-358`) each raise an instruction. p2: instructions 56 and 57 at 1,150 each for one 1,150 return | Make one path the owner, and add a unique refund-per-return guard. |
| F4 | P0 | **Fractional quantity:** a Float qty (`fix_storefront.py:324, 952`; API checks only > 0 at `storefront_api.py:242-247`). Ordering 0.01 of a 1,150 item paid 11.50 | Whole units only. |
| F5 | P1 | **Any internal user can order and forge approvals.** base.group_user has cart/line create and write (SF ACL rows 2-3). `action_record_terms` and `action_record_client_approval` check no role (`SF/models/fix_storefront_capture.py:987-1027`) | Add an assisted-sales group, role checks, and a recorder ≠ clerk rule. |
| F6 | P1 | **No M15 reservation at placement** (BRU-ECM-03, FR-041): reserved 0 → 0 | Reserve at placement, consume at dispatch, release on cancel or timeout. |
| F7 | P1 | **No payment expiry or timeout cron** (AUT-ECM-08) | Add `payment_expires_at` and a cron. |
| F8 | P1 | **A return has no lines,** so the whole order is restocked: a 1,150-of-2,300 refund restocked 2 units (`fix_storefront_refund_books.py:270-323`) | Add return lines. |
| F9 | P1 | **Storefront roles are held only by admin,** so no refund approver exists | Appoint holders (owner). |
| F10 | P1 | **Fails open:** dispatch proceeds without an M20 invoice (BRU-ECM-20; `fix_storefront_books.py:36-41, 386-417`). The P03 surface lacks `action_retry_posting` and `action_record_customer_nid` (`P03/controllers/a04/m38.py:39-48`). writable.py lacks `stock_location_id` and `cod_customer_nid`. The invoice sequence `FOR UPDATE NOWAIT` fails under concurrency | Block dispatch while the invoice is owed, whitelist the action, show the posting state. |
| F11 | P1 | **The exposure policy reads stock.quant (0 rows), not M15** (`fix_storefront_capture.py:613-660`) | Use `fix.stock.onhand` (qty − reserved). |
| F12 | P1 | **COD and guest controls missing:** 0 COD rules, no OTP, and one shared guest partner (`storefront_api.py:108-133`; `fix_storefront_capture.py:481-523`) | A partner per OTP-verified phone; refuse COD with no rule. |
| F13 | P1 | **Gateways have no callback secrets** (503), and a rail with no gateway is accepted (`fix_storefront.py:183-201`) | Refuse a rail that has no gateway. |
| F14 | P2 | **No delivery fee, voucher or loyalty;** the "Checkout Promotions (from M11)" screen is unused (`m38.js:58`) | Add server-priced fee and discount lines. |
| F15 | P2 | **SSLCOMMERZ and COD refunds go by bank_transfer** (`fix_storefront_refund_books.py:370-384`; `fix_a04_storefront_consumer.py:21-32`) | Refund to the original tender. |
| F16 | P2 | **KPIs and packs are unscoped** (sudo `search([])`), the period is ignored, GMV includes unpaid and cancelled orders, and dates are UTC (`P03/controllers/a04/m38.py:133-138, 169-196, 389-419, 482-510`) | Company domain, date filter, paid states only, `context_today`. |
| F17 | P2 | **Reports read `fix.storefront.rma`,** while the API creates `fix.storefront.return` (`m38.py:301-331, 492`) | Union the two models or merge them. |
| F18 | P2 | **Storefront revenue has no OU or branch;** everything lands on [OU1] Main | Derive it from the fulfilling location or pickup branch. |
| F19 | P2 | **Spec gaps:** catalogue from M37, compatibility, protection, rental, trade-in, subscription checkout, partial fulfilment, return fraud, warranty routing, consignment typed by hand, tracking link | Product work. |
| F20 | P3 | No idempotency key on placement, and no self-cancel | Add both. |
| F21 | P3 | COGS is 0 because the M15 avg cost is 0.00 (data) | M15 take-on. |

## M12: measured as correct
- KYC works, and the CFO approval is routed through M63 to tier 4 excluding the reviewer.
- A portal seller (fresh env) is refused writes to: kyc, cfo, tier, payout_hold, rating, categories, a pre-selected quote, quote price and state, order budget, and quoting as another seller.
- Commission 4,000 × 0.10 = 400 is pinned, and `commission.earned` creates the M53 ledger row.
- A dispute sets the payout hold.

## M12
| id | sev | finding / evidence | fix |
|---|---|---|---|
| F1 | P0 | **No customer invoice or receipt in M20,** yet the M53 accrual debits gross GMV to 101404 "POS Standard Chartered (legacy)", a cash account. The payout then pays the seller from the bank: cash booked that was never received (`MKP/models/fix_marketplace.py:476-605`; `SET/models/fix_settlement_ext.py:44-47, 644-691`; param `cd_settlement_ext.account_code.clearing=101404`) | Collect through M20, accrue against the receipt clearing, refuse accrual with no receipt. |
| F2 | P1 | **`action_paid` sets "Payout Complete"** with no payout run or M50 instruction, and the ledger stays earned (`fix_marketplace.py:898-931`) | Drop it from P03; set paid from the M53 discharge. |
| F3 | P1 | **No consumer for `dispute_resolved` or `chargeback_lost`:** a 4,000 refund was ruled, the hold lifted, and commission stays earned | Add consumers: customer refund, commission forfeit, seller clawback. |
| F4 | P1 | **No seller commission scheme or D-03 position,** so commission cannot be accrued on fix_real | Configure; block awards until configured. |
| F5 | P1 | **The record rule shows only `state='open'`** (`MKP/security/fix_marketplace_security.xml:44-53`), so other sellers' boards empty after the first quote | Rule should cover open and quoted. |
| F6 | P1 | **Operator, compliance and arbitrator are admin only; the seller group has 0 holders** | Appoint holders (owner). |
| F7 | P2 | **All sellers see customer name and description before award** (BRU-MKP-04) | Mask them. |
| F8 | P1 | **KYC verified on a made-up `z4-token-<id>-<ts>`** with no document (`fix_marketplace.py:304-319`) | Require documents. |
| F9 | P1 | **Commission posts to 400100 with no output VAT** (`fix_settlement_ext.py:654-692`) | Use M51 VAT and a commission income account. |
| F10 | P2 | **The scheme rate overwrites the order's pinned rate** (`fix_settlement_ext.py:474-527`) | One source for the rate. |
| F11 | P2 | **`category_ids` writable after CFO approval** (`writable.py:606-620`) | Pin it, or require re-approval. |
| F12 | P2 | **SOD-06 missing:** the CFO approver can approve the seller's payout (`fix_settlement_ext.py:1197-1207`) | Add the conflict. |
| F13 | P2 | **No sequences,** so names are MKT/New and DSP/New | Add sequences. |
| F14 | P2 | **Score bands assume 0-100** (scores run 0-0.85); fill-rate formula wrong; unapproved sellers counted; reports unscoped and undated (`P03/controllers/a04/m12.py:205-314, 468-560, 873-894`) | Fix formulas and scope. |
| F15 | P2 | **Spec gaps:** payout verification, e-sign, probation states, award window, wallet, fees, listings on the storefront | Product work. |
| F16 | P3 | **Tier stays at_risk after escalation** (`fix_marketplace.py:1719-1737`) | Recompute on resolution. |

## Cross-area
- **X1:** M38 → M50 double refund (consumer).
- **X2:** `order_cancelled` not consumed.
- **X3:** M38 → M15: no reservation; exposure reads stock.quant.
- **X4:** M12 → M20/M53: no customer document; M53 debits a static cash account.
- **X5:** M12 → M53: dispute and chargeback events not consumed; `action_paid` not tied to a payout.
- **X6:** M53 → M51: no VAT on commission.
- **X7:** M38 → M65: a gateway "active" with no secret.
- **X8:** M38 → M11: price from list_price.
- **X9:** M38/M12 roles admin only.
- **X10:** the M20 sequence NOWAIT lock fails under concurrency.

## Facts on fix_real_a04
- **Data:** 3 companies; 0 storefront and marketplace rows.
- **Role holders:**
  - all storefront roles: admin only;
  - marketplace operator, compliance, arbitrator: admin only;
  - marketplace seller: 0;
  - DOFA tiers T1-T5: 20 / 42 / 7 / 3 / 1;
  - portal users: 8.
- **Prices:** 16,191 sale_ok templates, all with list_price ≤ 1. 0 rate cards, 0 pricelist items, 4 price floors.
- **Stock:** stock.quant has 0 rows; M15 onhand is the real stock, at unit_cost 0.00.
- **Gateways:** bKash and SSLCOMMERZ marked active in M65, with no callback secrets.
- **Commission:** platform rate 0.10; no tier rates; 1 partner scheme; no D-03 position.
- **Accounts:**
  - 400102 Parts Sales;
  - 400100 Service Sales;
  - 100201 AR;
  - 200902 VAT out;
  - 100111 MFS/card clearing;
  - 100204 COD clearing;
  - 110999 inventory valuation suspense;
  - 101404 settlement clearing (a cash account, wrong);
  - 200102 Trade Payables;
  - 200905 Tax Payable.
  - The code defaults 101000, 200200 and 210100 do not exist on this chart.
- **Event consumers:**
  - present: commission.earned, dispute_raised, cart_abandoned, refund_approved;
  - absent: order_cancelled, dispute_resolved, chargeback_lost, seller.approved.
- **Crons:** no payment-timeout cron and no payout-eligibility cron.
