---
id: HC-014
title: Help Set — P12 Partner and Referral Portal
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Partner and Channel Management
reviewers: [Chief Commercial Officer, Finance Manager, Legal Counsel, Marketing Manager, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead with Chief Commercial Officer
content_class: D
purpose: >
  The self-service help set for referral and channel partners covering onboarding, referral links,
  lead tracking, earnings, co-marketing and reseller allocation. Partner adoption is targeted above
  75% of approved partners, and self-service is the only scalable support model — there is no
  partner-support team, and there will not be one.
traces_to: [P12, M40, M53, M35, M61, MD-026, HC-001, HC-002, HC-016, UI-022, LG-007, TR-018]
priority: P3
wave: W7
bilingual: yes
bn_counterpart: HC-014_Help_Set_P12_Partner_and_Referral_Portal_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P12 partner and referral portal; partner adoption target above 75% of approved partners; partner commission accuracy target 100% and disputes start with wording
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md — partner, channel, alliance and franchise management
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P12 Partner and Referral Portal

| Item | Value |
|---|---|
| Portal | `P12` Partner & Referral |
| Audience | **Referral / channel partner** — audience 11 · population varies |
| Article type | Help set specification — Task and Concept |
| Reading level target | `CG-011`; small-business and individual partners |
| Languages | **Bengali primary** |
| Related UI copy | `UI-022` `P12` copy pack |

> **Template conformance.** As `HC-003`, applied at set level.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and shape |
| `UI-022` | Labels quoted in steps |
| `LG-007` referral and alliance partner agreement | **Every commission article links here** (`IA-14`) |

**`PS-31`: there is no partner-support function, and this set is the support model.** `UI-022`'s
own justification states that partner commission accuracy is targeted at 100% and *"disputes start
with wording"*. A partner who cannot understand how their commission was calculated will dispute
it, and there is nobody staffed to answer.

---

## Steps — *the partner's lifecycle*

### Block A — Becoming a partner *(6 articles)*

Apply to become a partner · **the agreement — what you are agreeing to** · your approval status ·
partner types and what each can do · add people from your organisation · your details and payment
information. **2 at P0, 3 at P1, 1 at P2.**

### Block B — Referring *(6 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 7 | **Get your referral link or code** | Task | **P0** |
| 8 | **How a referral is attributed to you** | Concept | **P0** |
| 9 | Refer a customer | Task | **P0** |
| 10 | Track your referrals | Task | **P0** |
| 11 | **Why a referral was not attributed** | Troubleshooting | **P0** |
| 12 | Referral status meanings | Concept | P1 |

### Block C — Earnings *(6 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 13 | **How your commission is calculated** | Concept | **P0** |
| 14 | **When you get paid** | Concept | **P0** |
| 15 | Your statement | Task | P1 |
| 16 | **Your commission looks wrong** | Troubleshooting | **P0** |
| 17 | Deductions, clawbacks and reversals | Concept | P1 |
| 18 | Tax on your earnings | Concept | P2 |

### Block D — Reselling and co-marketing *(5 articles)*

Reseller allocation and pricing · place a reseller order · co-marketing materials and what you may
use · **brand and naming rules** · request marketing support. **1 at P0, 3 at P1, 1 at P2.**

**Set total: 23 articles · 10 at P0 · 9 at P1 · 4 at P2.**

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Approved partners actually use the portal | **Partner adoption** | **> 75% of approved partners** |
| Attribution is understood before it is disputed | Attribution queries | Falling |
| Commission is understood | **Commission disputes** | Approaching zero; accuracy target 100% |
| Partners self-serve | Support contacts per partner | **Near zero — there is no support team** |

**`PS-32`: articles 8, 11, 13 and 16 carry this set.** Attribution and commission are the only two
things a referral partner cares about, and both generate disputes that nobody is staffed to handle.
Four articles, written precisely, are the entire partner-support model.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Adoption below 75% | Partners never onboarded into the portal, or found it unnecessary | Check the onboarding path (Category 18 `EO`) before the content |
| Attribution disputes | Article 8 vague, or the attribution rule itself is ambiguous | **Verify the rule in `M40` before rewriting the article** |
| Commission disputes | Article 13 does not match the actual calculation | Same as `HC-009` `O-04` — help clearer than the calculation creates disputes |
| Partners email the account manager | The set is not discoverable, or is not in their language | `HS-29` |

---

## Related

`UI-022` · [`../../08_Training_and_Enablement/08B_Course_Packs/TR-018_Course_Pack_Account_and_Contract_Manager.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-018_Course_Pack_Account_and_Contract_Manager.md) — the nearest internal counterpart ·
`LG-007` referral and alliance partner agreement · [`HC-009_Help_Set_P07_Marketplace_Seller_Portal.md`](HC-009_Help_Set_P07_Marketplace_Seller_Portal.md) — the same earnings-trust pattern ·
Category 18 `EO` — partner onboarding (**boundary, `HC-001` `O-06`**).

---

## Feedback

Helpfulness per `CG-014`, plus **dispute-origin analysis** on Blocks B and C, as `HC-006` does for
invoices.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Articles required | **23** · written **0** |
| Effort | 23 × 2–3 h = **45–70 hours** |
| Sequencing | Articles 8, 11, 13, 16 (`PS-32`), then 10 P0 before W7 |
| Bengali | All 23, authored in Bengali |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`LG-007` partner agreement is unwritten** (Category 10 unstarted); Blocks A and C link to it | Legal Counsel | **W7** |
| **O-02** | **The attribution rule (article 8) and the commission calculation (article 13) must be verified against `M40` and `M53` before authoring.** Help that is clearer than the rule creates the disputes it exists to prevent | Commercial with Finance | **W7** |
| **O-03** | **Category 18 `EO` partner onboarding is unstarted** and the boundary is undefined (`HC-001` `O-06`) | Programme Content Lead | W7 |
| **O-04** | Co-marketing and brand-use rules (Block D) depend on `VB-010` product and programme naming, which exists, and on brand-use permissions, which do not | Brand with Commercial | W7 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] The absence of a partner-support function stated as the design constraint (`PS-31`)
- [x] 23 articles enumerated with type and priority
- [x] The four articles constituting the support model identified (`PS-32`)
- [x] Commission linked to the agreement, never restated (`IA-14`, `IA-15`)
- [x] All internal links resolve
- [x] `P12` targets cited to `04-00`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 23 articles authored — outstanding**
- [ ] **`O-02` attribution and commission rules verified — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and CCO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
