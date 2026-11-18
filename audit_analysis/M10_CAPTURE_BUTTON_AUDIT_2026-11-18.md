# M10 Loyalty & Rewards: data-capture audit, second pass

**Date:** 18 Nov 2026 · **Branch:** `fix/m10-capture-pass2` · **Module:** `cd_loyalty` 19.0.1.1.0 + `cd_p03_portal` (A03 / M10)

## 1. The question

The user saw M10 sub-module pages without a relevant data-capture button. The 13 Nov pass
(`M10_CAPTURE_BUTTON_AUDIT_2026-11-13.md`) gave every page a button, but only for records the
estate could already hold. It listed five spec records with **no model** at all. This pass
measures each page against the spec again and builds what was missing.

Sources: `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M10_Loyalty_Membership_and_Rewards.md`
(FR-LOY-001…044, BRU-LOY-01…15, §8 lifecycles, §10 entities, §11 automations), `contracts/nav/registry.json`.

## 2. Page by page: spec vs HEAD

| # | Page | Spec says a person records | HEAD offered | Verdict |
|---|---|---|---|---|
| 1 | Tiers & Enrolment | tier with **price and duration**; a **paid membership** Pending → Active → Expiring → Lapsed / Suspended / Cancelled (FR-001/002/003/009/010) | tier, free points account, card | **Gap**: no membership, no price, no lapse |
| 2 | Benefit Engine | benefit set **with scope**: a labour discount never reaches parts (FR-004/005, **BRU-LOY-01 H**) | programme, scheme, burn rule, point type | **Gap**: no scope; the tier carried a *Parts Discount %*, which BRU-01 forbids |
| 3 | Points Ledger | goodwill / correction adjustment under approval | Points Adjustment | OK |
| 4 | Wallet | **BDT stored value**: refunds, trade-in, prepayment, goodwill; application to invoice; payout with ID check and approval (FR-022…025, BRU-06/07/13, SOD-18) | **+ New Points Adjustment** | **Wrong record**: a points adjustment is not money |
| 5 | Vouchers & Coupons | **voucher batches** (single/bulk/personalised, issuance limit, eligibility) and **stacking rules** with a cap (FR-027…030, **BRU-LOY-09 H**) | campaign hook only | **Gap** |
| 6 | Referrals | **attribution** of a new customer to a shared code; self-referral, household and cap blocks (FR-034/036/037, **BRU-LOY-10 H**) | referral code only | **Gap** |
| 7 | Alliance Benefits | alliance cohort and members | Loyalty Affiliation | OK |
| 8 | Liability & Breakage | the **period-end run**: liability and breakage calculated, reconciled to the ledger, published to M19 (FR-040/041, **BRU-LOY-11 H**, AUT-LOY-12) | nothing ("calculated") | **Gap**: a report only, nothing to sign off or publish |

## 3. What was built

`cd_loyalty/models/fix_loyalty_capture.py` (new), 8 models, all company-isolated, ACL'd and sequenced:

| Page | Record (chip) | Rules enforced in the model |
|---|---|---|
| 1 | `fix.loyalty.membership` (**Privilege Membership**) | price/term/grace default from the tier; **active only on Confirm Payment with an M20 reference**; one open membership per member per programme (a renewal waits beside it and starts the day after expiry); terms fixed once paid; suspend/cancel need a reason; daily cron notices at 60/30/7 days, completes on renewal, **lapses after grace with benefits withdrawn on the stated date** (BRU-03); fee recognised day by day, deferred balance shown (BRU-12) |
| 1 | tier fields `membership_fee_bdt`, `membership_duration_months`, `membership_grace_days` | 0–60 months, 0–90 days grace |
| 2 | `fix.loyalty.benefit` (**Tier Benefit**) | a labour discount applies to labour only; nothing applies to parts or consumables (**BRU-01**); `discount_for()` returns 0 for any non-labour line (AC-01). Tier *Parts Discount %* above 0 is now refused |
| 4 | `fix.loyalty.wallet` + `fix.loyalty.wallet.txn` (**Wallet Transaction**) | wallet opened automatically per customer; balance only from posted transactions; credits need their source document; goodwill needs a reason; application only to a posted invoice of the same customer, up to its residual; **no overdraw (row lock)**; payout needs a **verified identity document** (BRU-13) and **DOFA approval above BDT 5,000** routed through the M63 inbox; **the approver or poster of a payout may not have created credits on the wallet (SOD-18)**; posted rows immutable; no entry type comes from points (BRU-07, AC-05) |
| 5 | `fix.loyalty.voucher.batch` (**Voucher Batch**, page + New) | personalised (one code per customer) or bulk (holder named at redemption); max 10,000 codes; eligibility (tier, channel, first purchase, minimum spend, uses per customer) **checked at redemption**; close (or expiry cron) cancels unredeemed codes and records how many (AUT-14). `fix.loyalty.voucher.partner_id` is now optional for bulk codes only |
| 5 | `fix.loyalty.stacking.rule` (**Stacking Rule**) | one rule per pair; `evaluate()` is order-independent, drops a non-combinable component, caps the total at the pair ceiling and the programme's **Max Aggregate Discount %** (BRU-09, AC-06/07), and returns the rules that fired |
| 6 | `fix.loyalty.referral.event` (**Referral Registration**) | blocked and kept with its reason: self-referral, same phone/mobile/email, same address (household), circular, already attributed (first wins), existing customer, per-referrer monthly cap (BRU-10, FR-036/037); qualifies only on a completed service within the window; rewards both sides once (idempotent receipts); window-expiry cron |
| 8 | `fix.loyalty.liability.run` (**Liability Run**, page + New) | outstanding points from the posted ledger up to period end (Dhaka day), valued and netted of breakage; movement vs the last published run; membership fees deferred; **publish refused unless balances reconcile to the ledger (AC-09), by a Finance user who did not calculate it, and with a written breakage basis when breakage > 0 (FR-041)**; published runs immutable |

Programme gains `referral_window_days`, `referral_cap_per_month`, `max_aggregate_discount_pct`
(changing the cap is a DOFA Tier 3 decision, like the other cost settings).

Events (contracts + registry, 554): `loyalty.membership_activated`, `loyalty.membership_lapsed`,
`loyalty.wallet_txn_posted`, `loyalty.voucher_batch_issued`, `loyalty.referral_blocked`,
`loyalty.liability_published` (the M19 hand-off).

### Workspace (`cd_p03_portal`)

- `static/src/a03/m10.js`: 7 new chips and forms, 7 new lists, pages 4/5/8 get a page **+ New**; the
  tier form shows its benefits and the batch form its issued codes (read-only grids); the old
  points "wallet" list is now *Points Balances* on page 3; Membership Revenue Deferral report on page 8.
- `controllers/a03/m10.py`: 8 served surfaces with their allowed actions; `membership_deferral` report.
- `controllers/a03/writable.py`: regenerated; no state, balance, figure or approval field is writable.

| # | Page | Capture now |
|---|---|---|
| 1 | Tiers & Enrolment | + New Tier · chips Tier Configuration, **Privilege Membership**, Member Enrolment, Loyalty Card |
| 2 | Benefit Engine | + Loyalty Programme · chips Loyalty Programme, **Tier Benefit**, Scheme, Redemption Rule, Point Type |
| 3 | Points Ledger | + Points Adjustment |
| 4 | Wallet | **+ New Wallet Transaction** |
| 5 | Vouchers & Coupons | **+ New Voucher Batch** · chips Voucher Batch, Voucher Campaign, **Stacking Rule** |
| 6 | Referrals | + Referral Code · chips Referral Code, **Referral Registration** |
| 7 | Alliance Benefits | + Loyalty Affiliation |
| 8 | Liability & Breakage | **+ New Liability Run** |

## 4. Evidence

- **Guard** `cd_p03_portal/tests/test_m10_capture_buttons.py`: 24/24 on the fix; **11 fail on HEAD**.
- **Live** `cd_loyalty/tests/test_m10_capture_live.py` (non-admin users, private DB `fix_test_m10c2` after `-u all`): 18/18.
- **Mutations**: see §6.
- **Gates**: A03 control suite, registry coverage, sub-module mapping, write whitelist, forms-show-children,
  report export standard, estate page standard, event registry, all `cd_loyalty` tests: 1,195 run, all pass
  except 6 in `test_a03_p2_loyalty.py` (relay earn, referral award, party merge) that **fail identically with
  HEAD code** on the same DB, so they predate this change.
- Lint: ruff 0.8.4 (the pinned version) clean.

## 5. Not built (owner decisions)

| Spec | Why not |
|---|---|
| Wallet → GL posting (FR-024), payout disbursement | needs Finance to name the wallet liability account and journal; the event `loyalty.wallet_txn_posted` carries what M20 needs |
| Payout threshold BDT 5,000 | placeholder from the DOFA ladder; BRU-13 says "a defined threshold", Q-08 (mobile-wallet payout regulation) is open |
| Liability → GL journal (M19) | published as an event; the journal needs the contract-liability account (Q-04 breakage rate is also open) |
| Membership benefits wired into pricing (AUT-LOY-02), BRU-15 accrual stop | pricing engine (M11) integration |
| Multi-use single codes, referral cap by value, wallet dormancy (FR-026, P3), fraud signals with device/IP (FR-031) | no capture source in the estate |
| Corporate / household membership (FR-011) | P2, needs the group model decision |

## 6. Mutation sweep

15 rules were each disabled in turn, and the live suite went red every time (**15/15 caught**): BRU-01 benefit scope,
BRU-01 tier parts discount, payment reference, one open membership, wallet overdraw, payout identity,
SOD-18, self-referral, household, first attribution, publish SoD, publish Finance-only, breakage basis,
stacking cap, batch limit. (The first sweep let self-referral survive: the same-phone check also blocks a
self-referral and its message said "self-referral" too. The test now asserts the exact reason.)

## 7. Live endpoint probe (private server, worktree code, `fix_test_m10c2`, port 8078)

- Every M10 screen posted to its real endpoint: **50 screens (22 lists, 18 forms, 10 reports), 0 errors,
  0 dropped columns, 0 missing form fields**.
- Through `/p03/model/write` and `/p03/model/action`, as the workspace does it:
  - A tier with Parts Discount 10 was refused (BRU-LOY-01).
  - A membership posted with `state: 'active'` saved as **Pending** at the tier price, BDT 1,500 (the typed state was dropped).
  - Confirm Payment with no reference was refused.
  - With reference PROBE-RCPT-1 the membership went Active, from 18 Nov 2026 to 17 Nov 2027, with BDT 1,495.89 deferred.
- Not clicked in the pane: the browser pane was hidden, and the Odoo web client does not mount in a hidden pane.

## 8. Deployed (19 Nov 2026)

The owner said "Yes, deploy both".

- Backups: `_migration/backups/fix_real_pre_m10_capture2_2026-11-19.dump` and `fix_dev_pre_m10_capture2_2026-11-19.dump`.
- `-u cd_loyalty,cd_p03_portal` ran with exit 0 on fix_real and fix_dev, from the main checkout at the shared tip.
- One shared restart by the M06 session at 03:17 covered M06, M07, M10 and M11: 8069 = fix_real PID 65964, 8090 = fix_dev PID 77252. Both processes started after this landing.
- Read-only check on both DBs, identical: cd_loyalty 19.0.1.1.0 installed; 8 models, 16 ACL rows, 9 isolation rules, 5 sequences, 3 crons; tier fee/term/grace columns present; voucher holder now optional.
- 8069 serves the deployed `m10.js`.
- Peer fix `7c9c62e6`: a wallet row on page 4 now opens the wallet, not a blank transaction form. `test_screens_wiring` caught it; this pass had not run that test.
- Not done: the click-through on 8069. It needs the owner's sign-in in the browser pane.

## 9. Live walk on fix_real (8069), 19 Nov 2026

Signed in as the local admin. The walk was read-only: nothing was saved on fix_real.

- **Endpoints:** every M10 screen was posted to its real endpoint: **50 screens, 0 errors, 0 dropped columns, 0 missing form fields**. Row counts match the estate: 1 programme, 1 tier, 3 schemes, 3 redemption rules, 2 point types, 2 affiliations; no members, wallets or vouchers yet.
- **Pages:** each of the 8 sub-module pages was opened in the workspace. Each shows its **+ New**:
  - Tier Configuration
  - Loyalty Programme
  - Points Adjustment
  - **Wallet Transaction**
  - **Voucher Batch**
  - Referral Code
  - Loyalty Affiliation
  - **Period-End Liability Run**
- **Forms:** each new chip was clicked and its form opened with its own tabs, a Save button and no error:
  - Privilege Membership (3 tabs)
  - Tier Benefit (2)
  - Wallet Transaction (3)
  - Voucher Batch (3)
  - Stacking Rule (1)
  - Referral Registration (2)
  - Liability Run (3)
