---
id: FIX-ERP2-M10
module_id: M10
module_code: LOY
module_name: Loyalty, Membership & Rewards
category: B — Customer Engagement & Experience
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Marketing Head
system_owner: Commercial Squad
priority: P1
wave: W2
regulatory_verified: 2026-08-12
---

# M10 — Loyalty, Membership & Rewards
### Category B · Code `LOY` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M10 |
| **Module code** | `LOY` |
| **Category** | B — Customer Engagement & Experience |
| **Status** | Existing (re-scoped — campaigns moved to M35, partner relationships to M40) |
| **Priority** | **P1** |
| **Delivery wave** | W2 (Months 5–8) |
| **Business owner** | Marketing Head |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `sale`, `product`) + L5 (custom) |
| **Custom modules** | `cd_loyalty`, `cd_wallet`, `cd_voucher`, `cd_referral` |
| **Requirement range** | FR-LOY-001 … FR-LOY-044 |
| **Requirement count** | 44 |
| **Effort estimate** | 18 person-weeks |
| **Depends on** | M33 Party Master · M37 Catalogue · M11 Pricing · M20 Receivable · M29 Identity |
| **Depended on by** | M01, M04, M11, M35, M36, M38, M40, M53, M20, M25 |

---

## 2. Purpose

M10 owns everything that changes **what a customer pays, or why they come back**: the
Privilege programme, credit points, the customer wallet, vouchers, and the referral mechanics
that turn satisfied customers into an acquisition channel.

It is a small module with disproportionate financial consequence, because points and
memberships are **liabilities** — promises to deliver value in the future — and most
organisations that run them do not account for them properly until an auditor asks.

### Why It Exists

The Company already runs a Privilege programme with Silver, Gold and Diamond tiers offering
50% off service charges. It is administered manually. There is no ledger of what has been
promised, no measure of what has been redeemed, no provision for what remains outstanding, and
no way to tell whether the programme makes or loses money.

The Service App SOW adds credit points for new-customer registration and a referral programme.
Both create further liability. Running them on spreadsheets across 51+ branches would produce
inconsistent benefit application at the counter and an unquantified balance-sheet exposure.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Company Profile §Privileged Program | "Special offers for members — 50% off on all service charges (promotional) — priority service access" |
| Company Profile §Partner Alliance Program | Privileged programme extended to business partners |
| ERP BRD §8.4 (BR-CRM-006) | "Manage Privilege Program tiers: enrolment, upgrade rules, benefit application, renewal" |
| ERP BRD BRU-CWM-06 | **"Privilege Program discounts apply only to labour charges and not to parts, consumables, or transportation charges"** |
| ERP BRD BRU-SRM-10 | Gold and Diamond members receive priority-1 SLA automatically |
| ERP BRD UC-010 | Privilege enrolment: tier selection, invoice, activation, automatic 50% labour discount, renewal reminder at 30 days |
| Service App SOW §Credit points | "For new customers, there will be some credit points so that customers can get some discounts during their next purchase by using those available points" |
| Service App SOW §Referral program | Referral programme as a named campaign mechanic |
| Service App SOW §Campaigns | "Earning double points, partnered campaigns with various brands, special day campaigns" |
| Portal roadmap IMPL-39 | Referral Partner Program — tracking, attribution, reward |
| **IFRS 15** *(verified 2026-08-12)* | Loyalty points are a **material right** and a separate performance obligation; transaction price is allocated to them at relative standalone selling price; the resulting liability is a **contract liability**; **breakage** is estimated and recognised as the likelihood of redemption becomes remote |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Privilege programme: tier definition, enrolment, benefits, upgrade, renewal, lapse |
| 2 | Benefit application engine — what a member gets, and precisely what it applies to |
| 3 | Points: earning rules, ledger, redemption, expiry, adjustment |
| 4 | Customer wallet: stored value, credits, refunds, payout rules |
| 5 | Vouchers and coupons: generation, eligibility, stacking, redemption, fraud control |
| 6 | Referral mechanics: codes, attribution, reward to both parties |
| 7 | Alliance member benefit extension (mechanics only; M40 owns the relationship) |
| 8 | **Loyalty liability calculation and breakage estimation for IFRS 15** |
| 9 | Member self-service dashboard content |
| 10 | Programme profitability analysis |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Party identity, consent, segments | **M33** | Master data governance |
| Campaign design, audience, journey, channel execution | **M35** | M10 supplies the offer mechanics; M35 decides who gets them and when |
| Price calculation and price books | **M11** | M10 supplies a benefit; M11 applies it within the pricing engine |
| Invoice creation and discount posting | **M20** | Only Category G creates financial documents |
| **Journal entries for loyalty liability** | **M19** | M10 calculates the liability; M19 posts it |
| Partner, alliance and franchise relationships | **M40** | M10 runs the mechanics; M40 owns the counterparty relationship |
| Referral commission payment to partners | **M53** | M10 attributes; M53 pays |
| Notification delivery | **M27** | M10 raises events; M27 sends |
| Marketplace seller ratings and incentives | **M12** | Different party class and commercial model |
| Warranty extension and protection products | **M09** | These are insurance-like products, not loyalty benefits |
| Contract-based discounts (AMC, MSP) | **M08** | Contractual entitlement, not membership benefit |

### 3.3 Shared Concepts

| Concept | M10's Role | Owning Module |
|---|---|---|
| Party | References | M33 |
| Benefit | **Owns the definition**; M11 applies it | M10 |
| Discount | Supplies the rule | M10 / M11 |
| Points liability | **Calculates** | M10 / M19 (posts) |
| Voucher | **Owns** | M10 |
| Referral | **Owns the mechanics** | M10 / M40 (partner relationship) |
| Campaign | Supplies mechanics to | M35 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Enterprise loyalty platforms** | Tier engines, points ledgers, wallet, voucher generation, redemption controls, fraud detection | Ledger-first design: points are an account, not a counter | Per-transaction SaaS pricing at 250,000 monthly interactions |
| **IFRS 15 loyalty accounting practice** | Points as a **material right** and separate performance obligation; transaction price allocated at relative standalone selling price; liability presented as a **contract liability**; **breakage** estimated and released as redemption becomes remote | **The complete accounting treatment.** This is the part most implementations omit and the part an auditor will test | Deferring the question until year-end |
| **Retail tier programmes** | Qualification by spend or frequency, tier progression and demotion, benefit sets per tier | Tier model with explicit progression and lapse rules | Points-only tiering — 1000FiX Privilege is a **purchased** membership, not an earned tier |
| **Odoo `loyalty` / `sale_loyalty`** | Loyalty cards, coupon programmes, promotion rules | Coupon and promotion primitives as the L1 substrate | Odoo's retail-cart assumptions |
| **Referral programme practice** | Unique code per referrer, attribution window, dual-sided reward, fraud controls | Dual-sided reward with an attribution window and self-referral prevention | — |

**Design position.** Four deliberate differences.

First, **the loyalty liability is calculated from day one, not retrofitted**. Points issued
without a corresponding liability calculation are an unrecorded obligation. M10 computes the
liability and the estimated breakage every period and publishes both to M19. This is the single
most consequential design decision in the module.

Second, **1000FiX Privilege is a purchased membership, not an earned tier**. The Company sells
Silver, Gold and Diamond. That makes it closer to a subscription than a conventional loyalty
tier, and it means enrolment revenue is recognised over the membership period while the benefit
is consumed unevenly — a second accounting consequence.

Third, **benefit scope is enforced, not advisory**. The existing rule that Privilege discounts
apply to labour only, never to parts, consumables or transport, is a hard constraint in the
benefit engine. Discount leakage on parts is invisible and expensive.

Fourth, **points and wallet are separate ledgers**. Points are an earned promotional currency
with expiry; wallet is stored value arising from refunds, trade-in proceeds and prepayment.
Conflating them creates a refund path for promotional currency, which is how loyalty
programmes get defrauded.

---

## 5. Functional Areas & Features

### 5.1 Privilege Programme & Membership

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOY-001 | Tier definition | Define membership tiers with price, duration, benefit set, eligibility rules and terms, versioned with effective dates | P1 | L5 |
| FR-LOY-002 | Enrolment | Enrol a member through the portal, app, counter, contact centre or agent, collect payment through M20, and activate on confirmation | P1 | L5 |
| FR-LOY-003 | Membership lifecycle | Manage Pending · Active · Expiring · Lapsed · Cancelled · Suspended with defined transitions and effective dating | P1 | L5 |
| FR-LOY-004 | Benefit set | Define the benefits attached to each tier — labour discount, priority SLA, free logistics, extended repair warranty, dedicated line, free annual health check | P1 | L5 |
| FR-LOY-005 | **Benefit scope enforcement** | Enforce precisely what each benefit applies to; the labour discount must never reach parts, consumables or transport | **P0** | L5 |
| FR-LOY-006 | Automatic benefit application | Apply eligible benefits automatically at quotation and invoicing, without agent intervention, and show the member the value applied | P1 | L5 |
| FR-LOY-007 | Tier upgrade | Upgrade mid-term with pro-rated pricing and immediate benefit effect | P2 | L5 |
| FR-LOY-008 | Tier downgrade and renewal | Handle downgrade at renewal and renewal at the prevailing price, with notice | P2 | L5 |
| FR-LOY-009 | Renewal and lapse | Notify at 60, 30 and 7 days before expiry; define a grace period; lapse with benefit withdrawal on a stated date | P1 | L5 |
| FR-LOY-010 | Membership suspension | Suspend benefits for non-payment or conduct, with reinstatement rules | P2 | L5 |
| FR-LOY-011 | Corporate and household membership | Support a membership covering multiple named individuals or a household group | P2 | L5 |
| FR-LOY-012 | Member dashboard content | Serve the member their tier, benefits, value realised to date, remaining entitlements, expiry and history | P1 | L5 |
| FR-LOY-013 | Benefit utilisation tracking | Track which benefits each member has used and how much value they have received | P1 | L5 |

### 5.2 Points

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOY-014 | Earning rules | Define earning rules by action — registration, first booking, spend value, review submitted, referral converted, survey completed, campaign multiplier — with effective dates and caps | P1 | L5 |
| FR-LOY-015 | Points ledger | Maintain an append-only ledger of earn, burn, expiry, adjustment and transfer, with a running balance and full provenance for every entry | **P1** | L5 |
| FR-LOY-016 | Redemption | Redeem points against service charges, parts, accessories or membership fees, subject to configurable minimum, maximum and category rules | P1 | L5 |
| FR-LOY-017 | Redemption valuation | Define and version the points-to-currency conversion rate used at redemption | P1 | L5 |
| FR-LOY-018 | Expiry | Expire points on a defined schedule with advance notification at 60 and 30 days | P2 | L5 |
| FR-LOY-019 | Manual adjustment | Permit goodwill adjustment under approval, with reason code and full audit | P1 | L5 |
| FR-LOY-020 | Points on reversal | Reverse earned points automatically when the originating transaction is cancelled, refunded or charged back | **P1** | L5 |
| FR-LOY-021 | Points statement | Provide the member a statement of earnings, redemptions and expiries for any period | P2 | L5 |

### 5.3 Wallet & Stored Value

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOY-022 | Customer wallet | Maintain a stored-value balance per party arising from refunds, trade-in proceeds, prepayment and goodwill credit | P2 | L5 |
| FR-LOY-023 | Wallet ledger | Maintain an append-only wallet ledger distinct from the points ledger, denominated in currency | P2 | L5 |
| FR-LOY-024 | Wallet application | Apply wallet balance to an invoice at the customer's election, in full or in part | P2 | L5 |
| FR-LOY-025 | Wallet payout | Permit withdrawal of wallet balance to a bank account or mobile wallet under defined conditions and approval | P2 | L5 |
| FR-LOY-026 | Wallet expiry and dormancy | Apply dormancy rules to wallet balances per policy and applicable law | P3 | L5 |

### 5.4 Vouchers, Coupons & Offers

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOY-027 | Voucher generation | Generate single-use, multi-use, personalised and bulk voucher codes with value or percentage, validity window and issuance limit | P1 | L5 |
| FR-LOY-028 | Eligibility engine | Restrict redemption by party segment, service type, product category, channel, branch, minimum value, first-purchase-only and membership tier | P1 | L5 |
| FR-LOY-029 | Stacking rules | Control which benefits, vouchers and promotions may combine, in what order they apply, and what the maximum aggregate discount is | **P1** | L5 |
| FR-LOY-030 | Redemption tracking | Track issuance, redemption, expiry and financial cost per voucher batch and per campaign | P1 | L5 |
| FR-LOY-031 | Fraud controls | Detect and block abusive patterns — velocity, device fingerprint, self-referral, code sharing beyond policy — and quarantine suspect redemptions | P2 | L5 |
| FR-LOY-032 | Voucher reconciliation | Reconcile redeemed voucher value to the discount posted in M20 | P1 | L5 |

### 5.5 Referral

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOY-033 | Referral code issuance | Issue a unique, shareable referral code or link per party, with QR and deep-link support | P1 | L5 |
| FR-LOY-034 | Attribution | Attribute a new customer to a referrer within a defined attribution window, resolving conflicts by a stated rule | P1 | L5 |
| FR-LOY-035 | Dual-sided reward | Reward both referrer and referee on the defined qualifying event — typically the referee's first completed paid service | P1 | L5 |
| FR-LOY-036 | Self-referral prevention | Block self-referral and household circularity by device, contact point and address matching | **P1** | L5 |
| FR-LOY-037 | Referral caps | Apply per-referrer caps by period and by value | P2 | L5 |
| FR-LOY-038 | Referral performance | Report referrals issued, clicked, converted and rewarded, with cost per acquisition | P1 | L5 |
| FR-LOY-039 | Alliance member benefit | Extend a defined benefit set to members of an alliance partner organisation, verified against a membership list or code | P2 | L5 |

### 5.6 Loyalty Accounting & Programme Economics

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOY-040 | **Liability calculation** | Calculate the outstanding points liability each period at the current redemption valuation, and publish it to M19 as a contract liability | **P0** | L5 |
| FR-LOY-041 | **Breakage estimation** | Estimate the proportion of issued points that will never be redeemed, using historical redemption behaviour, and recognise it as the likelihood of redemption becomes remote | **P0** | L5 |
| FR-LOY-042 | **Membership revenue deferral** | Recognise membership fee revenue over the membership period rather than at the point of sale, and publish the deferral schedule to M53 | **P0** | L5 |
| FR-LOY-043 | Programme profitability | Report programme cost — discounts given, points redeemed, vouchers, referral rewards — against attributable incremental revenue | P1 | L5 |
| FR-LOY-044 | Member value analysis | Compare spend, frequency, retention and margin of members against a matched non-member cohort | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Append-only ledgers** | Points and wallet ledgers are insert-only. A correction is a compensating entry with a reason, never an update or delete |
| T-02 | **Separate currencies** | Points and wallet are distinct ledgers with distinct units; no code path converts points to withdrawable cash |
| T-03 | **Balance derivation** | A balance is always derived from the ledger, never stored as an authoritative figure that can drift |
| T-04 | **Idempotent earning** | Earning is keyed to the originating transaction; a retried event never double-credits |
| T-05 | **Atomic redemption** | Redemption reserves, applies and commits atomically with the invoice; a failed invoice releases the reservation |
| T-06 | **Benefit evaluation API** | A single synchronous call returns all applicable benefits for a party and a proposed transaction, in under 150 ms, consumed by M11 |
| T-07 | **Stacking determinism** | Given the same inputs, the stacking engine produces the same outcome every time, and records which rules fired |
| T-08 | **Fraud signal capture** | Device fingerprint, IP, velocity and relationship signals are captured at redemption for pattern detection |
| T-09 | **Liability recalculation** | The liability calculation runs as a scheduled period-end job against the full ledger and is reproducible from source |
| T-10 | **Concurrency safety** | Two simultaneous redemptions against the same balance cannot overdraw it |
| T-11 | **Consent-aware notification** | Every member notification evaluates consent in M33 before dispatch through M27 |
| T-12 | **Performance envelope** | Benefit evaluation ≤ 150 ms · balance query ≤ 100 ms · voucher validation ≤ 200 ms |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M10 |
|---|---|---|
| **Member** | Has a card and hopes the branch honours it | Sees tier, benefits, value received, points and expiry in the app; benefits apply automatically |
| **Counter agent** | Applies the discount manually and may apply it to the wrong lines | Discount computed and scoped automatically; agent cannot mis-apply it |
| **Marketing Head** | Cannot tell whether the programme works | Sees enrolment, retention, redemption, cost and incremental revenue |
| **CFO** | Carries an unrecorded and unquantified liability | Sees the points liability and estimated breakage every period, posted to the ledger |
| **Branch manager** | Cannot sell membership consistently | Membership is a counter product with a defined pitch and instant activation |
| **Auditor** | Would find loyalty obligations undocumented | Finds a ledger, a liability calculation and a breakage methodology |
| **Referrer** | Refers informally with no reward | Has a code, sees conversions, receives a reward automatically |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Privilege base growth** | Consistent counter and digital sales with instant activation | **3× membership base** over 24 months |
| **Membership renewal** | Notification sequence, value-realised visibility, grace period | **> 80% renewal** |
| **Repeat purchase uplift** | Members return more often; points create a reason to come back | **+25% repeat rate versus non-members** |
| **Referral-sourced acquisition** | Dual-sided reward with attribution | **> 12% of new customers** referral-attributed, at materially lower acquisition cost |
| **Discount leakage prevention** | Benefit scope enforced at the pricing engine rather than at the agent's discretion | Every 1% of misapplied discount on parts across the base is direct margin |
| **Recurring membership revenue** | Membership fees recognised over the period | Predictable revenue independent of repair volume |
| **Audit and provision integrity** | Liability and breakage calculated and posted | Removes an unquantified balance-sheet exposure |
| **Campaign effectiveness** | M35 draws on real mechanics rather than ad-hoc discounts | Direct contribution to the **> 4:1 campaign ROI** target |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **A promise the Company can keep consistently** | A benefit honoured at one branch and refused at another damages trust more than having no programme |
| **Financial honesty about promotional obligations** | Recognising the liability is the difference between a marketing scheme and a managed programme |
| **Fraud resistance** | Points and vouchers are attractive targets; ledger discipline and fraud signals make abuse detectable |
| **A retention instrument the Company controls** | Unlike price, loyalty benefits can be adjusted without a market-wide signal |
| **Advocacy becomes measurable** | Referral converts goodwill into a countable, rewardable channel |
| **Foundation for partner alliances** | Extending benefits to alliance members requires mechanics that already work |

---

## 8. Lifecycle & State Models

### 8.1 Membership

```
   +-----------+
   |  PENDING  |  enrolled, payment not yet confirmed
   +-----+-----+
         | payment confirmed (M20)
   +-----v-----+
   |  ACTIVE   |<-------------------------+
   +--+--+--+--+                          |
      |  |  |                             | reinstated / renewed
      |  |  +--> SUSPENDED ---------------+  (non-payment or conduct)
      |  |
      |  +-----> EXPIRING ----------------+  (within notice window: 60 / 30 / 7 days)
      |                |
      |                | grace period elapses
      |          +-----v-----+
      |          |  LAPSED   |--> WIN-BACK (M35 campaign, consent permitting)
      |          +-----------+
      |
      +--------> CANCELLED  (customer request; refund per policy)

   Benefits are withdrawn on the stated effective date, never retroactively.
```

### 8.2 Points Ledger Entry

```
   EARNED ----> AVAILABLE ----> RESERVED ----> REDEEMED
      |              |              |
      |              |              +--> RELEASED (invoice failed or cancelled)
      |              |
      |              +--> EXPIRED (schedule, after 60 and 30 day notice)
      |
      +--> REVERSED (originating transaction cancelled, refunded or charged back)

   ADJUSTED (+/-) -- goodwill or correction, approval required, reason mandatory
```

### 8.3 Referral

```
   CODE ISSUED --> SHARED --> CLICKED --> REGISTERED --> QUALIFYING EVENT --> REWARDED
                                             |                 |
                                             |                 +--> NOT QUALIFIED
                                             |                      (window expired,
                                             |                       or no paid service)
                                             +--> BLOCKED
                                                  (self-referral, household circularity,
                                                   cap exceeded, fraud signal)
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-LOY-01 | **Privilege discounts apply to labour charges only, never to parts, consumables or transport** | **H** | CFO |
| BRU-LOY-02 | Benefits apply automatically where the member is eligible; an agent cannot decline to apply them | **H** | CCO |
| BRU-LOY-03 | Benefits are withdrawn on the stated lapse date, never retroactively | **H** | CCO |
| BRU-LOY-04 | Points ledgers are append-only; corrections are compensating entries with a reason | **H** | CFO |
| BRU-LOY-05 | Points earned on a transaction are reversed automatically if that transaction is cancelled, refunded or charged back | **H** | CFO |
| BRU-LOY-06 | A points balance cannot be overdrawn under any concurrency condition | **H** | CTO |
| BRU-LOY-07 | **Points may not be converted to withdrawable cash under any circumstance** | **H** | CFO |
| BRU-LOY-08 | Manual points adjustment requires approval above a defined threshold and always carries a reason code | **A** | Marketing Head |
| BRU-LOY-09 | Maximum aggregate discount from all stacked benefits, vouchers and promotions is capped at a configured percentage | **H** | CFO |
| BRU-LOY-10 | Self-referral and household circular referral are blocked | **H** | Marketing Head |
| BRU-LOY-11 | **Points liability and estimated breakage are calculated every period and published to M19** | **H** | CFO |
| BRU-LOY-12 | **Membership fee revenue is recognised over the membership period, not at the point of sale** | **H** | CFO |
| BRU-LOY-13 | Wallet payout requires identity verification and approval above a defined threshold | **H** | CFO |
| BRU-LOY-14 | Every member notification evaluates consent in M33 before dispatch | **H** | CDO |
| BRU-LOY-15 | A suspended or lapsed member accrues no new points and receives no benefits | **C** | CCO |

*Classification: **H** hard block · **A** approved override · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.loyalty.tier` | `fix_loyalty_tier` | Tier definition | code, name, price, duration_months, benefit_set_id, eligibility, version, effective_from |
| `fix.membership` | `fix_membership` | A member's enrolment | party_id, tier_id, state, started_at, expires_at, grace_until, price_paid, renewal_of, channel |
| `fix.benefit.definition` | `fix_benefit_definition` | What a benefit is | code, benefit_type, value, applies_to_scope, exclusions, priority, stackable |
| `fix.benefit.utilisation` | `fix_benefit_utilisation` | Value received | membership_id, benefit_code, transaction_ref, value_applied, occurred_at |
| `fix.points.ledger` | `fix_points_ledger` | Append-only points entries | party_id, entry_type, points, balance_after, source_type, source_id, rule_id, expires_at, occurred_at, reason |
| `fix.points.rule` | `fix_points_rule` | Earning rule | code, trigger_event, calculation, cap_per_period, multiplier, effective_from, effective_to |
| `fix.points.valuation` | `fix_points_valuation` | Redemption rate | points_per_currency_unit, effective_from, approved_by |
| `fix.wallet` | `fix_wallet` | Stored value account | party_id, currency, status |
| `fix.wallet.transaction` | `fix_wallet_transaction` | Append-only wallet entries | wallet_id, entry_type, amount, balance_after, source_type, source_id, occurred_at |
| `fix.voucher.batch` | `fix_voucher_batch` | Issuance batch | code_prefix, quantity, value_type, value, validity_from, validity_to, eligibility_json, campaign_ref |
| `fix.voucher` | `fix_voucher` | Individual code | batch_id, code, party_id, state, issued_at, redeemed_at, redeemed_against |
| `fix.stacking.rule` | `fix_stacking_rule` | Combination control | benefit_a, benefit_b, allowed, sequence, max_aggregate_pct |
| `fix.referral.code` | `fix_referral_code` | Referrer's code | party_id, code, issued_at, active, cap_period, cap_value |
| `fix.referral.event` | `fix_referral_event` | Attribution and reward | referral_code_id, referee_party_id, clicked_at, registered_at, qualified_at, reward_referrer, reward_referee, state, block_reason |
| `fix.alliance.benefit` | `fix_alliance_benefit` | Partner member benefit | partner_party_id, benefit_set_id, verification_method, effective_from |
| `fix.loyalty.liability` | `fix_loyalty_liability` | Period-end calculation | period, points_outstanding, valuation, gross_liability, breakage_rate, breakage_amount, net_liability, calculated_at, published_to_gl |
| `fix.fraud.signal` | `fix_fraud_signal` | Redemption risk | party_id, event_type, device_fingerprint, ip, velocity_score, decision, occurred_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party` | M33 | Read; membership attaches to it |
| `fix.consent.record` | M33 | Evaluate before notification |
| `fix.segment.membership` | M33 | Read for voucher eligibility |
| `fix.catalogue.item` | M37 | Read for redemption category rules |
| `fix.price.book` | M11 | Benefit supplied into pricing |
| `account.move`, `account.payment` | M20 | Membership fee, discount posting, wallet application |
| `fix.campaign` | M35 | Voucher batches issued under a campaign |
| `fix.partner.profile` | M40 | Alliance relationship |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-LOY-01 | Membership payment confirmed | Activate membership, publish benefits, notify the member, schedule renewal reminders | Queue for manual activation; alert |
| AUT-LOY-02 | Quotation or invoice prepared | Evaluate benefits and return them to M11 with scope and stacking applied | Proceed without benefit; flag for review |
| AUT-LOY-03 | Qualifying transaction completed | Award points per the active rules, idempotently keyed to the transaction | Retry; alert on repeated failure |
| AUT-LOY-04 | Transaction cancelled, refunded or charged back | Reverse the associated points automatically | Escalate to Finance |
| AUT-LOY-05 | Membership 60 / 30 / 7 days from expiry | Notify the member with value realised to date and a renewal path, subject to consent | — |
| AUT-LOY-06 | Grace period elapses | Lapse the membership, withdraw benefits from the stated date, notify | — |
| AUT-LOY-07 | Points 60 / 30 days from expiry | Notify the member of expiring points, subject to consent | — |
| AUT-LOY-08 | Points expiry date reached | Expire the points with a ledger entry | — |
| AUT-LOY-09 | Referral registration detected | Attribute to the referrer, run self-referral and cap checks, hold pending the qualifying event | Block and queue for review on fraud signal |
| AUT-LOY-10 | Referral qualifying event occurs | Award both rewards, notify both parties, record cost | Escalate to Marketing |
| AUT-LOY-11 | Fraud signal above threshold | Quarantine the redemption, notify Marketing, require manual release | — |
| AUT-LOY-12 | **Period end** | **Calculate points liability and breakage; publish to M19; produce the supporting schedule** | **Escalate to CFO — an unpublished liability is a reporting failure** |
| AUT-LOY-13 | Period end | Publish the membership revenue deferral schedule to M53 | Escalate to CFO |
| AUT-LOY-14 | Voucher batch expires | Close the batch, report unredeemed value, release any associated provision | — |

---

## 12. Interfaces

### 12.1 Upstream — M10 Consumes

| Source | What | Mechanism |
|---|---|---|
| M33 Party Master | Party identity, segment membership, consent | REST + event |
| M20 Receivable | Membership payment confirmation; transaction completion; refunds and chargebacks | Event |
| M01 Service Order | Completed service triggering points and benefit utilisation | Event |
| M38 E-Commerce | Online purchase triggering points | Event |
| M04 Front Desk | Counter membership sale and voucher redemption | Command |
| M35 Marketing | Campaign-driven voucher batch requests and multiplier periods | Command |
| M40 Partner | Alliance partner relationships and member verification lists | REST |
| M37 Catalogue | Redemption-eligible categories | Master data |

### 12.2 Downstream — M10 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M11 Pricing** | **Applicable benefits, scope and stacking outcome for a proposed transaction** | **REST, synchronous** |
| M36 Quotation | Benefit value shown on the quotation | REST |
| M20 Receivable | Discount lines, points redemption value, wallet application, membership fee | Command + event |
| **M19 General Ledger** | **Points liability and breakage for posting** | **Event, period-end** |
| M53 Revenue | Membership revenue deferral schedule; referral reward cost | Event |
| M01, M04 | Member tier for priority SLA and counter display | REST |
| M35 Marketing | Voucher performance, referral performance, member segments | Event + warehouse |
| M27 Contact Centre | Member notifications | Event |
| M25 Business Intelligence | Programme facts: enrolment, redemption, cost, incremental revenue | Warehouse extract |
| P01 Customer Portal | Member dashboard, points statement, referral code, vouchers | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `membership.activated` | party, tier, benefits, expiry | M11, M01, M27, P01 |
| `membership.expiring` | party, tier, days remaining, value realised | M27, M35 |
| `membership.lapsed` | party, tier, lapse date | M11, M35, M27 |
| `membership.upgraded` | party, from tier, to tier, pro-rata | M11, M20 |
| `benefit.applied` | party, benefit, transaction, value | M20, M25 |
| `points.earned` | party, points, rule, source transaction | P01, M25 |
| `points.redeemed` | party, points, value, invoice | M20, M25 |
| `points.expired` | party, points, batch | M25 |
| `points.reversed` | party, points, reason, source | M19, M25 |
| `voucher.issued` | batch, code, party, campaign | M35 |
| `voucher.redeemed` | code, party, value, transaction | M20, M35 |
| `referral.attributed` | referrer, referee, code | M07, M35 |
| `referral.rewarded` | referrer, referee, rewards, cost | M53, M27 |
| **`loyalty.liability_calculated`** | **period, gross, breakage, net** | **M19, M54** |
| `membership.deferral_schedule` | period, recognised, deferred | M53, M19 |
| `fraud.signal_raised` | party, event, score, decision | M60 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| **`/api/v1/loyalty/benefits/evaluate`** | **POST** | **Return applicable benefits and scope for a proposed transaction** | **M11, M36** |
| `/api/v1/loyalty/membership/{party}` | GET | Membership state and benefits | P01, P03, M01 |
| `/api/v1/loyalty/enrol` | POST | Enrol a member | P01, P03, P04 |
| `/api/v1/loyalty/points/{party}` | GET | Balance and statement | P01, P03 |
| `/api/v1/loyalty/points/redeem` | POST | Reserve and redeem points | P01, P03, M20 |
| `/api/v1/loyalty/wallet/{party}` | GET | Wallet balance and ledger | P01, P03 |
| `/api/v1/loyalty/vouchers/validate` | POST | Validate a code against eligibility | P01, P03, P38 |
| `/api/v1/loyalty/vouchers/redeem` | POST | Redeem a voucher | M20 |
| `/api/v1/loyalty/referral/{party}` | GET | Referral code and performance | P01 |
| `/api/v1/loyalty/liability/{period}` | GET | Liability and breakage schedule | M19, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R23 Marketing Manager | C R U D A | Programme design, rules, vouchers, campaigns mechanics |
| R04 Chief Commercial Officer | R U A | Tier pricing and benefit sets |
| R26 Finance Manager | R A | Liability, breakage, valuation, wallet payout approval |
| R08 Service Centre Agent | C R | Enrol members, apply vouchers; no adjustment authority |
| R29 Cashier / Counter Finance | C R | Membership sale and payment at the counter |
| R34 Contact Centre Agent | C R | Enrol, explain benefits, issue goodwill within limit |
| R06 Branch Manager | R U | Own branch enrolment and adjustments within limit |
| R32 Quality Manager / ISO Coordinator | R | Fraud signals and complaint linkage |
| R36 Customer | R | Own membership, points, wallet, vouchers, referral |
| R01 Chief Executive Officer | R | Programme economics |

**Field-level restrictions.** Programme cost, breakage rate and liability figures are visible
to R24, R26, R21 and R01 only. Fraud signal detail is restricted to R24, R32 and R49.

**Segregation of duties.** The person who approves a points adjustment cannot be the person
who requested it (SOD-17). Wallet payout approval is separated from wallet credit creation
(SOD-18).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Programme dashboard | Marketing Head, CCO | Daily | Active members by tier, enrolments, lapses, renewals due |
| Membership funnel | Marketing Head | Weekly | Offered, enrolled, activated, renewed, lapsed by channel and branch |
| Benefit utilisation | Marketing Head, CFO | Monthly | Value given by benefit type, tier and branch |
| **Discount leakage report** | **CFO** | **Weekly** | Discounts applied outside permitted scope — target zero |
| Points ledger summary | CFO | Monthly | Issued, redeemed, expired, adjusted, outstanding |
| **Liability and breakage schedule** | **CFO, auditor** | **Period end** | Outstanding points, valuation, gross liability, breakage rate and basis, net liability |
| Redemption behaviour | Marketing Head | Monthly | Redemption rate, time to redemption, category mix — feeds breakage estimation |
| Voucher performance | Marketing Head | Per campaign | Issued, redeemed, cost, attributed revenue, ROI |
| Referral performance | Marketing Head, CCO | Monthly | Codes issued, conversions, cost per acquisition, top referrers |
| Fraud and abuse | Marketing Head, GRC | Monthly | Quarantined redemptions, patterns, losses prevented |
| Member versus non-member | CCO, CEO | Quarterly | Spend, frequency, retention and margin against a matched cohort |
| Programme profitability | CFO, CEO | Quarterly | Total cost against attributable incremental revenue |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| KPI-148 | Privilege membership base | baseline | 1.8× | **3×** |
| KPI-149 | Membership renewal rate | unmeasured | 70% | **> 80%** |
| KPI-150 | Repeat purchase rate — members vs non-members | unmeasured | +15% | **+25%** |
| KPI-151 | **Discount applied outside permitted scope** | unknown | **0** | **0** |
| KPI-152 | Points redemption rate | n/a | 30–50% | **35–55%** (healthy band) |
| KPI-153 | **Liability published to the ledger each period** | n/a | **100%** | **100%** |
| KPI-154 | Breakage estimate variance against actual | n/a | within 15% | **within 8%** |
| KPI-155 | Referral-attributed new customers | 0% | 7% | **> 12%** |
| KPI-156 | Referral cost per acquisition vs paid channels | n/a | −30% | **−45%** |
| KPI-157 | Fraudulent redemptions detected before payout | n/a | > 85% | **> 95%** |
| KPI-158 | Benefit evaluation response time (p95) | n/a | < 200 ms | **< 150 ms** |
| KPI-159 | Member satisfaction vs non-member | unmeasured | +0.2 | **+0.4** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `sale`, `product`, `account` primitives | 16% |
| L2 | OCA `sale_loyalty` / coupon extensions where suitable | 8% |
| L5 | `cd_loyalty`, `cd_wallet`, `cd_voucher`, `cd_referral` | 76% |

### 16.2 Custom Development

> CD identifiers are **provisional** pending the unified register in `02-05` (audit H-03).

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-043 | `cd_loyalty` — tiers, membership lifecycle, benefit engine, scope enforcement, points ledger | Odoo module | 7 PW |
| CD-044 | `cd_wallet` — stored value ledger, application, payout | Odoo module | 3 PW |
| CD-045 | `cd_voucher` — generation, eligibility, stacking, fraud controls | Odoo module | 4 PW |
| CD-046 | `cd_referral` — codes, attribution, dual reward, circularity prevention | Odoo module | 2 PW |
| CD-047 | **Liability and breakage calculation service** | Service | **2 PW** |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M10 is scheduled in **W2** (P1) but declares a dependency on 2 module(s) that land later: **M11** (W3); **M20** (W3). One of three things must be true before the W2 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W2 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M10 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W2 plan for M10 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| **M33 Party Master** | **Blocking** — membership and points attach to a governed party |
| **M11 Pricing** | **Blocking** — benefits are meaningless unless the pricing engine applies them |
| M20 Receivable | Membership fee collection and discount posting |
| M37 Catalogue | Redemption category rules require the catalogue |
| M19 General Ledger | Liability posting — may lag to W3 with the liability accrued and published from W2 |
| M27 Contact Centre | Member notification — may be stubbed in W2 |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing Privilege members | To be profiled — held manually | `fix.membership` | W2 |
| Historical points balances | **None exist** — no ledger has been kept | — | — |
| Outstanding promotional commitments | To be profiled | `fix.voucher` or goodwill points | W2 |

> **Migration warning.** Existing Privilege members must be migrated with their **actual
> remaining term**, not a reset term. Resetting expiry dates on migration would either give
> away value or curtail a paid entitlement — both create disputes at the counter in Wave 2.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **A Privilege discount cannot be applied to parts, consumables or transport, including via API** | **Negative test through UI, counter and API** |
| AC-02 | Benefits apply automatically at quotation and invoice without agent action | End-to-end demonstration across all three channels |
| AC-03 | A points balance cannot be overdrawn under concurrent redemption | Concurrency test |
| AC-04 | Points earned on a cancelled or refunded transaction reverse automatically | Scripted test for cancellation, refund and chargeback |
| AC-05 | **No code path converts points to withdrawable cash** | **Code review and negative test** |
| AC-06 | Stacking produces a deterministic outcome and records which rules fired | Test matrix of 20 benefit and voucher combinations |
| AC-07 | Aggregate discount cap is enforced across all stacked benefits | Negative test |
| AC-08 | Self-referral and household circular referral are blocked | Negative test |
| AC-09 | **The period-end liability and breakage calculation runs, reconciles to the ledger, and publishes to M19** | **Two consecutive period-end cycles with CFO sign-off** |
| AC-10 | The breakage methodology is documented and reproducible from source data | Methodology document reviewed by CFO and external auditor |
| AC-11 | **Membership revenue is deferred over the membership period, not recognised on sale** | **Accounting test with CFO sign-off** |
| AC-12 | Migrated members retain their actual remaining term and tier | Migration reconciliation report |
| AC-13 | Benefit evaluation responds in ≤ 150 ms p95 | Load test |
| AC-14 | Every member notification evaluates consent before dispatch | Negative test |
| AC-15 | Marketing Head and CFO sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Is the 50% labour discount permanent or promotional?** The Company profile describes it as promotional. This determines the liability model. | CCO / CFO | **W2 minus 2 months** |
| Q-02 | What is the points-to-currency valuation, and who may change it? | CFO / Marketing Head | W2 build |
| Q-03 | What is the points expiry period — 12, 18 or 24 months? | Marketing Head | W2 build |
| Q-04 | What breakage rate should be assumed at launch, absent historical redemption data? | CFO / external auditor | **W2 build** |
| Q-05 | Is the customer wallet in scope for W2, or deferred until trade-in (M14, W6) creates the need? | CFO | W2 design |
| Q-06 | What is the referral reward structure and the per-referrer cap? | Marketing Head | W2 build |
| Q-07 | How many existing Privilege members are there, and where is that list held? | Marketing Head | **W2 minus 2 months** |
| Q-08 | Does wallet payout to a mobile wallet raise any regulatory requirement in Bangladesh? | CFO / Legal | W2 design |

**Q-04 is the material accounting question.** Without historical redemption data, the launch
breakage assumption is a judgement that will be tested at the first audit. It should be set
with the external auditor, not internally.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §5 (boundary map) · `M33_Customer_and_Party_Master_Management.md` ·
`M35_Marketing_Campaigns_and_Demand_Generation.md` ·
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §3 (the commercial chain) ·
`03_Modules/G_Finance_and_Treasury/_CATEGORY_OVERVIEW.md` (liability posting)

**Workspace evidence**
`1000FiX_Services_Company_Profile.md` §Privileged Program, §Partner Alliance Program ·
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-CRM-006, BRU-CWM-06,
BRU-SRM-10, UC-010 · `1000fix_business/SOW for 1000FiX Service App Development.docx`
§Credit points, §Referral program, §Campaigns ·
`Intergrated_web_portal/.../IMPL-39_Referral_Partner_Program.md`

**External benchmark and standards** *(verified 2026-08-12)*
**IFRS 15** — customer loyalty programmes as a material right and separate performance
obligation; allocation of transaction price at relative standalone selling price; contract
liability presentation; breakage estimated and recognised as redemption becomes remote ·
Enterprise loyalty platform practice — tier engines, points ledgers, wallet, voucher
eligibility and stacking, redemption fraud controls · Referral programme practice — unique
code, attribution window, dual-sided reward, self-referral prevention ·
Odoo `sale_loyalty` and coupon primitives

---

*Module M10 · Category B · 1000FiX ERP System v2.0 · CONFIDENTIAL*
