---
id: HC-009
title: Help Set — P07 Marketplace Seller Portal
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Marketplace Operations
reviewers: [Chief Commercial Officer, Marketplace Operations, Legal Counsel, Finance Manager, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead with Chief Commercial Officer
content_class: D
purpose: >
  The self-service help set for 500–2,000 marketplace sellers covering registration, listings,
  bidding, job execution, earnings, performance, disputes and boost. Seller onboarding completion
  is targeted above 60% of started registrations, and help is the completion lever: a registration
  abandoned at the document-upload step is a seller the marketplace never acquires.
traces_to: [P07, M12, M53, M61, MD-018, MD-026, HC-001, HC-002, HC-016, UI-017, LG-004, TR-019, SP-024]
priority: P2
wave: W7
bilingual: yes
bn_counterpart: HC-009_Help_Set_P07_Marketplace_Seller_Portal_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P07 serves 500–2,000 external sellers, many with low English literacy; onboarding completion target above 60% of started registrations
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-LMS-02 — a marketplace engineer cannot be activated in a category without passing that category's qualification
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P07 Marketplace Seller Portal

| Item | Value |
|---|---|
| Portal | `P07` Marketplace Seller |
| Audience | **Marketplace seller** — audience 6 · 500–2,000, **many with low English literacy** |
| Article type | Help set specification — Task predominates |
| Reading level target | `CG-011`; **the second-lowest in the register after `HC-003`** |
| Languages | **Bengali authored** (`HS-29`) |
| Related UI copy | `UI-017` `P07` copy pack |

> **Template conformance.** As `HC-003`, applied at set level.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and shape |
| `UI-017` | Labels quoted in steps |
| `LG-004` marketplace seller agreement and policy handbook | **Every governance article links here** (`IA-14`) |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md) | Category standards and qualification requirements |

**`PS-17`: this audience earns income from the platform, which changes what help must do.** A
customer who cannot find help is inconvenienced. A seller who cannot find help **loses money**, and
responds by phoning, by posting in informal groups, or by leaving. The tone is practical and the
money articles come first.

---

## Steps — *the seller's lifecycle*

### Block A — Becoming a seller *(9 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 1 | **Register as a seller** | Task | **P0** |
| 2 | **The documents we need and how to photograph them** | Task | **P0** — the abandonment point |
| 3 | **Which categories you can work in** | Concept | **P0** |
| 4 | **Pass a category qualification** | Task | **P0** — `BRU-LMS-02` |
| 5 | Your application status | Concept | **P0** |
| 6 | Your application was rejected | Troubleshooting | P1 |
| 7 | The seller agreement — what you are agreeing to | Concept | P1 — links `LG-004` |
| 8 | Add engineers from your team | Task | P1 |
| 9 | Your bank details and how you get paid | Task | **P0** |

### Block B — Getting work *(7 articles)*

Find available jobs · **how bidding works** · what makes a bid successful · accept a job · decline
a job without penalty · your availability · **why you are not seeing jobs**. **2 at P0, 4 at P1,
1 at P2.**

### Block C — Doing the work *(6 articles)*

Start a job · record what you did · **the evidence we require** · complete a job · the customer
is not there · escalate a problem. **2 at P0, 3 at P1, 1 at P2.**

### Block D — Money *(7 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 23 | **How your earnings are calculated** | Concept | **P0** |
| 24 | **Commission — what we take and why** | Concept | **P0** |
| 25 | **When you get paid** | Concept | **P0** |
| 26 | Track a payment | Task | P1 |
| 27 | Your payment is late or wrong | Troubleshooting | **P0** |
| 28 | Deductions and adjustments | Concept | P1 |
| 29 | Statements and tax | Concept | P2 |

### Block E — Performance and disputes *(6 articles)*

Your scorecard and how it is calculated · **why your score dropped** · a warning — what it means
and what to do · suspension · **dispute a customer complaint** · appeal a decision. **2 at P0,
3 at P1, 1 at P2.**

### Block F — Growth *(3 articles)*

Boost your listings · what boost costs and returns · grow into a new category. **0 at P0, 1 at P1,
2 at P2.**

**Set total: 38 articles · 13 at P0 · 17 at P1 · 8 at P2.**

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Registrations complete rather than abandon | **`P07` onboarding completion** | **> 60% of started registrations** |
| Sellers understand their earnings | Payment and commission query volume | Falling |
| Governance decisions are understood | Appeals against warnings and suspensions | Falling; and **better argued when they occur** |
| Marketplace operations scale | Officer time per seller | Falling — 4–10 officers against 500–2,000 sellers |

**`PS-18`: articles 2, 23, 24 and 25 carry this set.** Article 2 is where registrations die —
document upload from a phone camera is the single highest-abandonment step in any seller
onboarding. Articles 23–25 are where trust is won or lost: a seller who cannot predict their income
does not stay.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Completion below 60% | Abandonment at document upload | Article 2; and **measure the funnel step by step before rewriting anything** |
| Payment queries dominate | Articles 23–25 unclear or contradicted by the actual calculation | Verify against `M53`; the help may be right and the calculation surprising |
| Sellers organise informally to share answers | The set is not reaching them, or is not in their language | `HS-29` — authored Bengali, not translated |
| Appeals rise after a governance change | Change communicated through the portal only | Governance changes need a push, not a page |
| Sellers ask officers what an article says | Officers answering rather than pointing | Same failure `TR-023` module 7 addresses internally |

---

## Related

`UI-017` · [`../../08_Training_and_Enablement/08B_Course_Packs/TR-019_Course_Pack_Marketplace_and_Seller_Operations.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-019_Course_Pack_Marketplace_and_Seller_Operations.md) — the internal counterpart ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance.md) ·
[`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md) · `LG-004` ·
Category 18 `EO` — seller onboarding content (**`TR-019` `O-04` records that nothing yet trains the sellers themselves**).

---

## Feedback

Helpfulness per `CG-014`, plus **funnel-step abandonment** on Block A and **query volume by topic**
on Block D.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Articles required | **38** · written **0** |
| Effort | 38 × 2–3 h = **75–115 hours** |
| Sequencing | Articles 2, 23, 24, 25 (`PS-18`), then 13 P0 before W7 |
| Bengali | All 38, **authored in Bengali** — low English literacy is stated in the portal spec |
| Video | Article 2 (document photography) is the strongest video candidate in the register — `HC-020` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`LG-004` seller agreement is unwritten** (Category 10 unstarted). Blocks A and E link to it throughout; `TR-019` `O-01` records the same gap | Legal Counsel | **W7** |
| **O-02** | `MD-018` seller categories and qualification standards are unpopulated | Commercial with MDM | W7 |
| **O-03** | **Category 18 `EO` seller onboarding is unstarted**, and the boundary with this set is undefined (`HC-001` `O-06`, `TR-019` `O-04`) | Programme Content Lead | W7 |
| **O-04** | Commission and payout calculation (`M53`) must be verified before articles 23–25 are written; **help that is clearer than the calculation creates disputes** | Finance with Marketplace Operations | W7 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] The income relationship stated as the design constraint (`PS-17`)
- [x] 38 articles enumerated with type and priority
- [x] The four articles carrying completion and trust identified (`PS-18`)
- [x] Qualification block taught as a rule with a route, not an obstacle (`BRU-LMS-02`)
- [x] Legal artefacts linked, never restated (`IA-14`)
- [x] All internal links resolve
- [x] `BRU-LMS-02` cited to `05-05`; `P07` target to `04-00`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 38 articles authored — outstanding**
- [ ] **`O-01` `LG-004` — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and CCO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
