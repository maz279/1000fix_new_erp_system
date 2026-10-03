---
id: VB-010
title: Product, Plan and Programme Naming Standard
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial Lead
author: Commercial with Brand and Content Design
reviewers: [Brand, Content Design Lead, Legal & Compliance, Localisation Lead, Enterprise Architecture]
approver: Content Design Lead
content_class: D
purpose: >
  Fixes how AMC tiers, protection plans, loyalty tiers, subscription plans, campaigns and
  programmes are named and abbreviated. Product names appear simultaneously in contracts,
  invoices, portals, advertising and master data; renaming one after launch is a data-migration
  event with a legal tail, not a marketing refresh.
traces_to: [MD-019, MD-031, MD-032, MD-033, MD-034, CG-004, CG-010, LG-013, DT-030, VB-009]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: VB-010_Product_Plan_and_Programme_Naming_Standard_BN.md
sources:
  - source: 1000fix_ERP_Module/README.md — the fourteen revenue streams and their owning modules
    verified: 2026-08-15
    class: P1
  - source: 1000_fix_corporate_website project_content VP-002 RAMC, VP-003 Privileged Program, VP-001 Warranty Extension, VP-007 Points Rewards — existing consumer programme names in market
    verified: 2026-08-15
    class: P1
  - source: 1000_fix_corporate_website project_content B2B-020 AMC Package Comparison — Basic / Standard / Premium / Enterprise tiering in market
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M39_Subscription_and_Recurring_Revenue.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# VB-010 — Product, Plan and Programme Naming Standard

> **A product name is the most expensive string in the system.** It is printed on contracts
> customers have signed, invoices held for five years under VAT retention, master data rows that
> transactions reference, brand advertising already in market, and every portal.
>
> **Renaming after launch is a migration, a re-papering exercise and a customer-communication
> campaign — not a design change.** Get it right once.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | The form, structure, abbreviation, capitalisation and bilingual treatment of every commercial name |
| **What it does not govern** | Which products exist (`MD-019`, `MD-031`…`MD-034`); pricing (`MD-029`); contract terms (`DT-030`, `LG-015`); internal system terminology (`CG-004`) |
| **What breaks without it** | "RAMC Premium", "Premium RAMC", "Residential Premium" and "RAMC-P" all existing, each authoritative somewhere |

---

## 2. Scope

**In scope:** AMC and RAMC tiers, protection and warranty products, loyalty tiers, subscription
plans, service packages, campaigns, partner programmes, and the customer-facing names of
delivery modes.

**Out of scope:** legal entity names; module and portal identifiers (`CG-004` `T-12`); internal
codes (`MD-019`); brand marks (`VB-003` §8).

---

## 3. Governing rules

| # | Rule |
|---|---|
| **NM-01** | **A launched name is permanent.** Changing it requires Steering approval, a customer-communication plan, a master-data migration and a contract-variation assessment |
| **NM-02** | **One name, one product.** The same words never name two things |
| **NM-03** | **One product, one name.** No alternate marketing name alongside the system name |
| **NM-04** | Names are registered in `MD-019` **before** they appear in any content, contract or campaign — `RG-01` applied to names |
| **NM-05** | Every name has an approved **abbreviation** and an approved **Bengali form**, registered at the same time |
| **NM-06** | Names are **not translated** — they are brand assets (`BN-004`). The Bengali form is a transliteration or an approved Bengali name, decided once |
| **NM-07** | A name never encodes price, duration or coverage that can change. "AMC 12" dies the day a 15-month contract is sold |
| **NM-08** | A name never encodes a superlative or a claim (`CG-013` T-A13). "Best", "Total", "Complete", "Unlimited" are refused |
| **NM-09** | Names are checked for trade-mark conflict before approval (`CG-013` T-A19) |
| **NM-10** | Names must survive Bengali rendering, thermal print, a 14-character badge and an SMS |

---

## 4. Name structure

```
[Family]  [Tier]        [Qualifier]
 RAMC      Premium       —
 Privilege Gold          —
 FiXCare   Extended      24 months        ← qualifier is a separate field, not part of the name
```

| Part | Required | Rule |
|---|:--:|---|
| **Family** | Yes | The product line. Stable for the life of the business |
| **Tier** | Where tiers exist | From the approved tier ladders in §5 |
| **Qualifier** | No | **Never part of the name.** Duration, coverage and price are attributes in `MD-019`, displayed beside the name |

| # | Rule |
|---|---|
| **ST-01** | Maximum **three words** and **24 characters** in the full name |
| **ST-02** | Family first, tier second. Never "Premium RAMC" |
| **ST-03** | No punctuation except a hyphen inside a coined word |
| **ST-04** | No numerals in a name unless the numeral is part of the brand — "1000FiX" |
| **ST-05** | No internal codes in a customer-facing name |

---

## 5. Approved tier ladders

**Three ladders. A new product uses one of them; it does not invent a fourth.**

| Ladder | Levels | Used for | In market today |
|---|---|---|---|
| **Commercial** | Basic → Standard → Premium → Enterprise | Corporate AMC, MSP, managed services | Yes — `B2B-020` AMC package comparison |
| **Consumer** | Essential → Plus → Premium | RAMC, protection products, subscriptions | Partly |
| **Loyalty** | Silver → Gold → Diamond | Privilege membership tiers | Partly — `VP-003` Privileged Program |

| # | Rule |
|---|---|
| **TL-01** | A tier word means the same relative position in every ladder it appears in |
| **TL-02** | **"Premium" appears in two ladders and is the one collision to watch.** Commercial Premium and Consumer Premium are different products at different prices. They are always disambiguated by family: "AMC Premium", "RAMC Premium" — never "Premium" alone |
| **TL-03** | Never mix ladders within one family |
| **TL-04** | Never add a level to a ladder without Commercial and Brand approval |
| **TL-05** | Tier names are never comparative in a way that disparages a lower tier |

---

## 6. Abbreviations

Abbreviations appear where the full name does not fit — badges, thermal receipts, SMS, dense
tables, dashboards.

| # | Rule |
|---|---|
| **AB-01** | Every name has **one** approved abbreviation. Not two, not an ad-hoc shortening |
| **AB-02** | Maximum 8 characters |
| **AB-03** | Registered in `MD-019` alongside the full name |
| **AB-04** | The abbreviation is the **same in both languages** where it is an initialism |
| **AB-05** | An abbreviation is never used in a contract, an invoice, a statutory document or a legal notice — those carry the full registered name |
| **AB-06** | An abbreviation is never used on first mention in help or training |

| Full name | Abbreviation | Where the abbreviation is used |
|---|---|---|
| AMC Enterprise | AMC-ENT | Badge, dashboard, dense table |
| RAMC Premium | RAMC-PR | Badge, SMS |
| Privilege Gold | PRIV-G | Badge, loyalty card |
| FiXCare Extended | FXC-EXT | Badge, receipt |

---

## 7. Capitalisation and typography

`CG-003` §1.2 mandates sentence case. **Registered product names are proper nouns and are the
declared exception.**

| # | Rule |
|---|---|
| **CP-01** | A registered product name is capitalised as registered, wherever it appears |
| **CP-02** | The surrounding sentence remains sentence case: "Your RAMC Premium contract expires on 30 September." |
| **CP-03** | Never ALL CAPS for a product name except inside a status badge of ≤ 12 characters (`CG-003` §1.2) |
| **CP-04** | Never italicise or bold a product name for emphasis |
| **CP-05** | Trade-mark symbols appear on first use in legal and marketing content only, never in UI |
| **CP-06** | Names are never letter-spaced or condensed to fit. In Bengali this is prohibited outright (`VB-009` LH-02) |

---

## 8. Bengali treatment

| # | Rule |
|---|---|
| **BN-01** | Product names are in the **do-not-translate register** (`BN-004`). They are transliterated or given an approved Bengali name — never translated word by word |
| **BN-02** | The decision per name is made **once**, at registration, and recorded in `MD-019` and `BN-003` |
| **BN-03** | Where a name is kept in Latin script inside Bengali text, it is marked with a `lang` attribute (`VB-009` MX-04) |
| **BN-04** | Where a name is transliterated, both forms are registered and the Latin form remains valid in technical and statutory contexts |
| **BN-05** | Bengali forms are checked against the badge and SMS budgets (`VB-006` §8, `NT-004`) — Bengali SMS segments at 70 characters |
| **BN-06** | The **1000FiX wordmark is never transliterated** (`VB-009` BR-01) |

| Name | Bengali treatment | Form |
|---|---|---|
| 1000FiX | Never transliterated | 1000FiX |
| AMC / RAMC | Kept as initialisms | AMC / RAMC |
| Privilege Gold | Transliterated | প্রিভিলেজ গোল্ড |
| FiXCare | Never transliterated — coined brand term | FiXCare |
| Mushak 6.3 | Never translated — statutory | Mushak 6.3 |

> Bengali forms above are **indicative pending `BN-003`** (`CG-004` `T-07`).

---

## 9. Names in market today

Recorded so that new naming does not contradict what customers already hold. Sourced from the
website content set, verified 2026-08-15.

| Existing name | Source | Status | Action |
|---|---|---|---|
| **RAMC** — Residential Annual Maintenance Contract | `VP-002` | In market | Adopt as a family. Apply the consumer ladder |
| **AMC** — Annual Maintenance Contract | `B2B-002`, `B2B-020` | In market with Basic / Standard / Premium / Enterprise | Adopt as a family with the commercial ladder |
| **Privileged Program** — 50% off service charges | `VP-003` | In market | ⚠ **Rename to "Privilege"** — see §9.1 |
| Warranty Extension Program | `VP-001` | In market, descriptive not branded | Decide: brand it, or keep it descriptive |
| Points Rewards Program | `VP-007` | In market, descriptive | Decide: fold into Privilege, or brand separately |
| Partner Alliance Program | `VP-004`, `B2B-014` | In market | Adopt as a programme name |
| **1000FiX Station** — metro kiosk network | `WP-004` | In market | Adopt. Note it is a **channel**, not a product |
| **FiXnChill** — seasonal campaign | `PC-001` | Campaign, time-boxed | Campaigns are exempt from the permanence rule — §11 |

### 9.1 Open naming decision — "Privileged Program"

**"Privileged Program" fails `ST-01` and reads awkwardly in English.** "Privileged" describes
the member, not the programme; the natural form is "Privilege".

| Option | Consequence |
|---|---|
| **Rename to "Privilege"** — recommended | Cleaner, shorter, tiers naturally as Privilege Silver / Gold / Diamond. Requires customer communication and marketing update, but **before** the ERP makes it a master-data row |
| Keep "Privileged Program" | Locks a defective name into contracts, master data and invoices under `NM-01` |

> **This must be decided before `MD-034` Loyalty Tier Register is authored**, not after. Once the
> name is a master-data row referenced by transactions, `NM-01` applies and the change becomes a
> migration. Raised as an open decision in §13 and logged in `RF-006`.

---

## 10. Registering a name

| Step | Action | Who |
|---|---|---|
| 1 | Confirm no registered name already covers it (`NM-02`) | Commercial |
| 2 | Select the family and the ladder from §5 | Commercial |
| 3 | Draft the name to §4 structure and §3 rules | Commercial with Brand |
| 4 | Check trade-mark conflict | Legal (`CG-013` T-A19) |
| 5 | Check the claim rules — no superlative, no unlimited (`NM-08`) | Legal + Content Design |
| 6 | Decide the Bengali treatment (`BN-02`) | Localisation |
| 7 | Assign the abbreviation (`AB-01`) | Commercial |
| 8 | Test against the constraints — badge 14 chars, SMS budget, thermal print, Bengali rendering (`NM-10`) | Content Design + Localisation |
| 9 | Register in `MD-019` with the abbreviation and Bengali form | Master Data Owner |
| 10 | Register the Bengali form in `BN-003` and the Latin form in `BN-004` | Localisation |
| 11 | Log the decision in `RF-006` | Content Lead |

**Only then may the name appear in content, a contract or a campaign** (`NM-04`).

---

## 11. Campaign names

Campaigns are time-boxed and are the one exception to permanence.

| # | Rule |
|---|---|
| **CM-01** | Campaign names carry an end date at registration |
| **CM-02** | A campaign name is never reused for a product |
| **CM-03** | A campaign name never appears in a contract, an invoice or a statutory document — the underlying product name does |
| **CM-04** | A campaign name may be playful where a product name may not — "FiXnChill" is acceptable as a campaign, not as a product |
| **CM-05** | A campaign that recurs annually keeps its name; a campaign that is retired does not have it reused within three years |

---

## 12. Do and do not

| Do not | Do |
|---|---|
| AMC 12 Month Premium Package | AMC Premium — duration is an attribute |
| Premium (alone) | AMC Premium or RAMC Premium — always disambiguate |
| Total Care Unlimited | Refused — superlative and absolute claim (`NM-08`) |
| Use "PRIV-G" on a contract | Use "Privilege Gold"; abbreviations never appear on contracts |
| Invent a fourth tier ladder | Use commercial, consumer or loyalty |
| Translate "FiXCare" into Bengali | It is a brand term; keep it, mark the `lang` |
| Launch a name and register it afterwards | Register in `MD-019` first (`NM-04`) |
| Rename after launch to improve it | `NM-01` — it is a migration, not an edit |
| Let a name exceed 24 characters | Shorten the name, not the type |

---

## 13. Open decisions

| # | Decision | Owner | Needed by | Blocks |
|---|---|---|---|---|
| 1 | **Rename "Privileged Program" to "Privilege"** (§9.1) | Commercial Lead with Brand | **Before `MD-034` is authored** | `MD-034`, `UI-011`, all loyalty content |
| 2 | Is Warranty Extension branded or descriptive? | Commercial with Brand | Before `MD-031` | `MD-031`, `LG-013` |
| 3 | Does Points Rewards fold into Privilege, or stand alone? | Commercial | Before `MD-034` | `MD-034`, `M10` content |
| 4 | Consumer ladder — is it Essential / Plus / Premium, or does RAMC keep its existing tier names? | Commercial | Before `MD-032` | `MD-032`, `DT-030` |
| 5 | Bengali form per name (`BN-02`) | Localisation Lead | Before `BN-003` | All bilingual product content |

---

## 14. Dependencies

| Depends on | Why |
|---|---|
| `MD-019` Product and Service Catalogue Seed | Where names are registered |
| `MD-031`…`MD-034` | The warranty, contract, subscription and loyalty registers naming this governs |
| `BN-003`, `BN-004` | Bengali forms and do-not-translate treatment |
| `CG-004` | The system terminology names must not collide with |
| `VB-009` | Bengali rendering constraints on names |
| `LG-013`, `DT-030` | Where names carry contractual force |

---

## 15. Enforcement

| Check | Mechanism | When |
|---|---|---|
| Name registered in `MD-019` before use | Automated cross-file check | Every commit |
| Name length ≤ 24 characters | Automated | At registration |
| Abbreviation ≤ 8 characters, one per name | Automated | At registration |
| Banned superlatives in a name | Automated (`CG-013` §2.4 word list) | At registration |
| Abbreviation used in a contract or statutory document | Automated scan of `DT` and `LG` content | Every commit |
| Bengali form registered | Cross-check against `BN-003` | Every wave audit |
| Name fits a 14-character badge, or has an approved abbreviation | Manual at registration | At registration |
| No unregistered name in content | `AUDIT_Checklist_Recurring.md` §F | Every wave |

---

## 16. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave until the catalogue stabilises, then annually |
| Out-of-cycle trigger | A new product line; a trade-mark challenge; a campaign launch |
| Owner | Commercial Lead |
| Bengali counterpart | `VB-010_Product_Plan_and_Programme_Naming_Standard_BN.md` — required, not yet written |

---

## 17. Related documents

| Document | Relationship |
|---|---|
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](VB-003_Brand_Application_in_Enterprise_UI.md) | Brand marks, which names are not |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](VB-009_Bengali_Typography_and_Brand_Standard.md) | Bengali rendering of names |
| [`VB-006_Design_System_Content_Standards.md`](VB-006_Design_System_Content_Standards.md) | Badge budgets names must fit |
| [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | System terminology, distinct from product names |
| [`../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md`](../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md) | T-A13 superlatives, T-A19 trade marks |
| `MD-019` Product and Service Catalogue Seed | The register |
| `MD-034` Loyalty Tier, Point and Benefit Register | Blocked by open decision 1 |
| `BN-004` Do-Not-Translate and Transliteration Register | `BN-01` |

---

## 18. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Ten governing rules, three-part name structure, three approved tier ladders with the Premium collision rule, abbreviation policy, capitalisation exception to `CG-003`, Bengali treatment, audit of eight names in market, registration procedure, five open decisions including the Privileged Program rename | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Permanence rule stated first, with its real cost
- [x] Name structure prevents encoding duration, price or coverage
- [x] Tier ladders closed at three, with the "Premium" collision explicitly handled
- [x] Names in market audited against the standard rather than assumed compliant
- [x] The "Privileged Program" defect raised **before** it becomes a master-data row
- [x] Registration procedure enforces register-first
- [x] All internal links resolve
- [ ] Bengali counterpart written and signed off in context — **outstanding; blocks `Approved`**
- [ ] Five open decisions resolved — **outstanding; decision 1 blocks `MD-034`**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
