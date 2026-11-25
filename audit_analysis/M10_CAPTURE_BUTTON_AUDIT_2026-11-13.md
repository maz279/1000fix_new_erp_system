# M10 Loyalty & Rewards: data-capture button audit

**Date:** 13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** fix live on 8069 (production bundle `bb2bba0` contains it), guard test added, nothing committed

## 1. The question

The M10 workspace has 8 sub-module pages (Function Register, 63 functions). Not all of them showed a button to record data. Which pages should have one, and what should it open?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M10_Loyalty_Membership_and_Rewards.md` (FR-LOY-001…044, BRU-LOY-01…15, T-01…12)
- `contracts/nav/registry.json` (the 8 sub-modules and their function counts)

| # | Sub-module | Spec requirements | What a person records |
|---|---|---|---|
| 1 | Tiers & Enrolment | FR-001…013 | tier definitions; **member enrolment** (FR-002: portal, counter, contact centre); the member's card |
| 2 | Benefit Engine | FR-004…006, FR-014, FR-016/017 | the programme; earn rules (schemes); redemption rules; point types |
| 3 | Points Ledger | FR-015…021 | a goodwill or correction adjustment, with approval and reason (FR-019, BRU-08) |
| 4 | Wallet | FR-022…026 | nothing typed into a balance: it is derived from the ledger (T-01, T-03) |
| 5 | Vouchers & Coupons | FR-027…032 | the issuing rule (campaign + reward); vouchers are issued, not typed |
| 6 | Referrals | FR-033…038 | a referral code |
| 7 | Alliance Benefits | FR-039 | the alliance cohort and its members |
| 8 | Liability & Breakage | FR-040…044 | nothing: a period-end calculation (AUT-LOY-12) |

## 3. What the code had (before)

Evaluated with the workspace engine's own `fregCreate` / `fregPanels` over the real registry, and confirmed by clicking each page on 8069.

| # | Page | Button before | Defect |
|---|---|---|---|
| 1 | Tiers & Enrolment | + New Tier Configuration | **No way to enrol a member.** The enrolment form (`M10-form-account`) existed but had no chip. Loyalty Cards screen and form were on no page. |
| 2 | Benefit Engine | + Loyalty Programme, Scheme chip | The schemes, redemption-rule and point-type lists were on no page; no chip for a redemption rule or point type. |
| 3 | Points Ledger | + New Points Adjustment | Correct. The Redemption Rules report was on no page. |
| 4 | Wallet | **nothing** | No button, and no text saying how a balance moves. |
| 5 | Vouchers & Coupons | **no + New** (chip only) | The campaign-hook list, where a saved hook is **activated**, was on no page; the hook form returned to the voucher list. A new "Voucher Campaign" defaulted to a bonus-points reward. Fraud Controls was on no page. The empty voucher list did not say vouchers are issued by a hook. |
| 6 | Referrals | + New Referral Code | Correct. |
| 7 | Alliance Benefits | **+ New Tier Configuration** | Wrong record. The alliance cohort is `fix.loyalty.affiliation`; the affiliation list was on no page. |
| 8 | Liability & Breakage | nothing | Correct (calculated), but its wallet list offered a "+ New" that opened the enrolment form. |

Seven working screens sat on no sub-module page: schemes, redemption rules, point types, affiliations, cards, campaign hooks, fraud controls. On fix_real that hid the 3 schemes, 3 redemption rules, 2 point types and 2 affiliations that exist.

## 4. What was changed

| # | Page | Capture now |
|---|---|---|
| 1 | Tiers & Enrolment | + New Tier Configuration; chips **Member Enrolment**, **Loyalty Card**; Loyalty Cards list added |
| 2 | Benefit Engine | + Loyalty Programme; chips Loyalty Programme, Loyalty Scheme, **Redemption Rule**, **Point Type**; the three rule lists added |
| 3 | Points Ledger | unchanged, plus the Redemption Rules report |
| 4 | Wallet | **+ New Points Adjustment** (the only thing that moves a balance); ledger list added; wallet list is open-only and says how a wallet opens and moves |
| 5 | Vouchers & Coupons | **+ New Voucher Campaign**; Campaign Reward Hooks list (Activate / Complete, state-gated) and Fraud Controls added; the form returns to the hook list and defaults to a voucher reward; voucher and hook lists explain where rows come from |
| 6 | Referrals | unchanged |
| 7 | Alliance Benefits | page now reads affiliations: **+ New Loyalty Affiliation**; the tier-benefit list is read-only with a note |
| 8 | Liability & Breakage | no button (calculated); wallet list no longer offers + New |

No server change was needed: the write whitelist (`controllers/a03/writable.py`) regenerates identical, since no form field was added.

### Files

- `addons/platform/cd_p03_portal/static/src/a03/m10.js`: sub-module mappings, chips, screen flags, voucher-campaign form
- `addons/platform/cd_p03_portal/tests/test_m10_capture_buttons.py`: **new guard**, 15 tests

## 5. Verification

- **Guard:** 15/15 pass on the fix. On the pre-fix file it fails **8**.
- **Estate page standard + guard:** 620/620 pass (all 67 modules).
- **Server probe on 8069 (fix_real):** each page grid, every M10 list, all 11 forms and every report posted to its real endpoint: **42 calls, 0 errors, 0 dropped columns**.
- **Clicked in the workspace:** each page shows the button in section 4. Member Enrolment, Voucher Campaign (reward = voucher) and Loyalty Affiliation open their forms with no error. Alliance Benefits lists the 2 affiliations. Console shows only the usual service-worker notice.
- A blank ledger line on a new enrolment is dropped on save, so it does not block an enrolment.

Not exercised: saving a record on fix_real. That would create real-estate data, and it needs a real customer and, for a voucher hook, a running M35 campaign (fix_real has 0 campaigns).

## 6. Gaps the spec asks for and the estate does not have

The buttons above cover every record the estate can hold. These spec items have **no model**, so no button can capture them yet:

| Spec | Missing |
|---|---|
| FR-022…026, BRU-13 | **Stored-value (BDT) wallet**: refunds, trade-in credit, prepayment, payout. The "Wallet" page shows points wallets only. |
| FR-001, 003, 007…010, BRU-12 | **Paid membership**: price, duration, Pending / Expiring / Lapsed states, renewal notices, fee deferral. Accounts are only active / frozen / suspended / closed. |
| FR-027…029, 032 | **Voucher batches**: single, multi-use or bulk codes with an issuance limit, the eligibility engine, stacking rules and reconciliation to M20. Vouchers are issued only one per campaign responder, by a hook. |
| FR-034…037 | **Referral attribution events**: click, register, qualify, block, and per-referrer caps. Only the code exists. |
| FR-031, T-08 | **Fraud signals** (device, IP, velocity) are not stored. Fraud Controls counts three signals from existing rows. |

Building these is new commercial and finance scope and needs owner decisions, for example the payout approval threshold and the membership price. It was not done here.

## 7. Data note

Every M10 row on fix_real is synthetic audit seed, not business data:

- programme "1000 FiX Rewards (audit)" and tier Silver (27 Oct);
- `SEED-A03-*` schemes, point types and affiliations, and three redemption rules (2 Nov).

There are no members, ledger lines, vouchers or referrals. Whether to remove the seed before go-live is the owner's call.
