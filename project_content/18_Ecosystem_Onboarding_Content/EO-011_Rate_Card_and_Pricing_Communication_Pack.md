---
id: EO-011
title: Rate Card and Pricing Communication Pack
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial
author: Commercial with Finance and Content Design
reviewers: [Chief Commercial Officer, Chief Financial Officer, Legal Counsel, Procurement Manager, Marketplace Operations, Account Management, Warranty Officer, Localisation Lead, Content Design Lead]
approver: Programme Content Lead
content_class: E
purpose: >
  The standard for communicating a price, rate-card, commission or fee change to any external
  ecosystem — marketplace sellers, suppliers, brand partners and corporate clients — including who
  must be told, how much notice each is owed, which version governs a transaction already in
  flight, and what a counterparty may do about it. Four ecosystems price on four different
  mechanics running in four different directions; a change communicated on one pattern across all
  four produces four simultaneous disputes, each with a different contractual basis, in the same
  week.
traces_to: [M11, M08, M12, M40, M42, M16, M20, M53, P04, P05, P07, P08, P12, MD-029, MD-017, MD-018, MD-016, MD-032, MD-037, MD-040, FR-MKP-009, FR-MKP-068, FR-MKP-069, FR-SRM2-022, FR-SRM2-023, FR-SRM2-026, FR-PCM-003, FR-PCM-012, BRU-MKP-15, BRU-SRM2-14, BRU-SRM2-19, BRU-PCM-03, BRU-PCM-12, BRU-PCM-19, CG-006 §3.4, CG-006 §3.2, LG-003, LG-004, LG-005, LG-006, LG-007, LG-015, NT-010, NT-011, NT-012, NT-013, DT-020, DT-039, DT-040, UI-014, UI-015, UI-017, UI-018, UI-022, RF-006, EO-001, EO-003, EO-005, EO-007, EO-009, EO-010, EO-013, EO-014]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: EO-011_Rate_Card_and_Pricing_Communication_Pack_BN.md
sources:
  - source: project_content/02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md — the register holding price lists, rate cards, commission bands and fee schedules, effective-dated
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md §3.4 — master data carries effective dates rather than release pins; "a transaction is evaluated against the version effective on its own date, never against the current version"; §3.2 places EO in the not-pinned set
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M42_Supplier_Relationship_and_Performance.md §5.4 FR-SRM2-023 — a supplier price increase must be submitted, justified and approved before it takes effect, and M16 is prevented from ordering at an unapproved price; §9 BRU-SRM2-14; BRU-SRM2-19 agreement expiry warns at 90, 60 and 30 days
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md §5.1 FR-MKP-009 re-acceptance of the agreement on material change; §5.7 FR-MKP-068 commission scheme by category, tier, value band, job type and promotional period with a declared fallback, FR-MKP-069 fee definitions
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md §9 BRU-PCM-03 M40 defines programmes, M11 holds rates and M53 computes and pays; BRU-PCM-12 programme terms are versioned and a partner is bound to the version in force at their agreement date; BRU-PCM-19 alliance benefits are applied by M11 and never configured as ad-hoc discounts
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md §2 rate_card_owner enum brand / 1000fix / negotiated — who sets labour and parts rates
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Rate Card and Pricing Communication Pack

| Item | Value |
|---|---|
| Audience | **Internal** — the commercial, procurement, marketplace, account-management and warranty owners who make price changes |
| Ecosystems governed | Marketplace sellers · Suppliers · Brand partners · Corporate clients · *(franchise and channel partners, `EO-010`)* |
| Content class | **E — internal governance.** Approver: Programme Content Lead (`CG-002` §4) |
| Language | **Bilingual** — the *notices* this pack specifies reach Bengali-reading sellers and corporate users |
| Wave | W4 · Months 14–18 — **but rate cards go live at W3** (`O-01`) |
| Register of record | `MD-029` for values; **`RF-006` for the decision** |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions are applied to a change rather than to a
> counterparty: §4.3 is the **journey** a price change travels from decision to effect, §4.4 is the
> **pre-notice checklist**, and §4.7 replaces the *first-90-days* section with **the first change
> cycle**, which is the same idea measured in changes rather than in days. Declared, because this
> is the one `EO` file with no onboarded audience.

---

## 1. Purpose

The Master Index states the failure in one line: *"price changes communicated inconsistently
across four ecosystems generate simultaneous disputes."*

The reason they are simultaneous is structural. A rate-card revision in `MD-029` can touch a
seller's commission, a supplier's agreed price, a brand's reimbursement rate and a corporate
client's contracted schedule **in the same load**. Four counterparty populations then discover it
in the same week, on four different contractual bases, through four portals, in two languages.

And the four are not variations on one pattern. **They run in different directions:**

| Ecosystem | Who proposes the change | Who must approve it | Governing instrument |
|---|---|---|---|
| **Marketplace sellers** | **1000FiX** — commission and fees are ours to set (`FR-MKP-068`) | 1000FiX; the seller may accept or leave | `LG-004`; re-acceptance on material change (`FR-MKP-009`) |
| **Suppliers** | **The supplier** — they submit a proposed increase | **1000FiX**, before it takes effect; `M16` cannot order at an unapproved price (`BRU-SRM2-14`) | `LG-006`; the agreed price list (`FR-SRM2-022`) |
| **Brand partners** | **Either** — `MD-017` `rate_card_owner` is `brand`, `1000fix` or `negotiated` | Whoever the field names | The authorisation agreement; `LG-005` |
| **Corporate clients** | **1000FiX**, but only within the contract | Usually **both** — a change outside the contract is an amendment | The contract; `LG-003`, `LG-015` |

A single "price change notice" template applied to all four would be wrong three times: it would
notify a supplier of a change they were supposed to propose, notify a brand of a rate they own,
and notify a corporate client of a variation they have not agreed to.

**This pack therefore governs the communication, not the price.** `MD-029` holds values; `M11`
computes; `M53` settles; this file states **who is told, how, when, and which version governs the
transaction in flight**.

---

## 2. Scope

**In scope.** The change taxonomy and what each type triggers; the four ecosystem patterns and
their direction of travel; the change journey from decision to effect; notice periods and how each
is derived from its instrument; the pre-notice checklist; the effective-dating rule and the
in-flight transaction question; the notice content standard; the channel per ecosystem; the
counterparty's options — accept, query, dispute, exit; simultaneous-change coordination across
ecosystems; and the review of a completed change cycle.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Price, rate, commission and fee **values** | `MD-029`; brand rates `MD-017`; seller bands `MD-018`; supplier price lists `M42` |
| Pricing strategy, guard rails and dynamic pricing | `M11` |
| Commission calculation, settlement and payout | `M53`, `M52` |
| Tax treatment of a price | `MD-037`, `M51` |
| **Consumer-facing price changes** | `CM` change and communications; `NT` notification templates; `UI` in-product copy — **customers are not an ecosystem in this pack's sense** |
| The notification **templates** themselves | `NT-010` corporate, `NT-011` vendor, `NT-012` seller and partner, `NT-013` brand |
| The statements a change appears on | `DT-020`, `DT-039`, `DT-040` |
| Contract amendment mechanics | `M08`; `MD-032` |
| The decision itself, and its rationale | **`RF-006`** decision log — *unwritten*, `O-03` |
| Disputes arising from a change | **`EO-013`** |
| A counterparty leaving because of a change | **`EO-014`** |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **CCO / Commercial** | The coordination rule when a change touches more than one ecosystem |
| **Marketplace Operations** | Commission and fee changes, and the re-acceptance trigger |
| **Procurement Manager** | Inbound supplier increases, and why they are approved rather than announced |
| **Account Management** | Corporate changes that are amendments rather than notices |
| **Warranty Officer** | Brand rate changes, and who owns the card |
| **CFO / Finance** | Effective dating, in-flight transactions and the revenue consequence |
| **Legal Counsel** | Notice periods against each instrument |
| **Content Design and Localisation** | The notice content standard and its Bengali obligation |

---

## 4. Content

### 4.1 Change taxonomy

| Type | Example | Notice? | Re-acceptance? | Amendment? |
|---|---|:--:|:--:|:--:|
| **Correction** — the published value was wrong | A rate loaded with a transposed figure | **Yes, immediately** | No | No |
| **Indexation** — a pre-agreed formula applies | An annual uplift the agreement provides for | Yes, per the instrument | No | No |
| **Structural** — the shape changes | Commission moves from flat to banded (`FR-MKP-068`) | **Yes, with the longest notice** | **Usually** | Where contracted |
| **Rate** — a value changes within the existing shape | A commission percentage moves | Yes | Material changes only | Where contracted |
| **New fee** — something previously unpriced is priced | A listing fee introduced (`FR-MKP-069`) | **Yes, treated as structural** | **Yes** | Where contracted |
| **Scope** — what a price covers changes | An inclusion becomes chargeable | **Yes, treated as structural** | Usually | Usually |
| **Promotional** — time-boxed and reverting | A commission holiday for a category | Yes, **with the reversion date stated in the same notice** | No | No |

> **A promotional change with an unstated reversion date becomes a permanent change in the
> counterparty's mind, and its expiry is experienced as an increase.** `RC-07` requires the
> reversion date in the original notice.

### 4.2 The four patterns

#### Marketplace sellers — outbound, with a re-acceptance trigger

| Element | Position |
|---|---|
| What changes | Commission scheme, fees, hold and payout terms (`FR-MKP-068`, `FR-MKP-069`) |
| Direction | 1000FiX sets; the seller accepts or exits |
| Instrument | `LG-004` §4.5, §4.9, §9 change control |
| **Re-acceptance** | A **material** change requires the agreement to be re-presented and re-signed (`FR-MKP-009`). *Material* is defined in `LG-004` and **is currently pending** — `O-02` |
| Channel | `P07` in-portal, plus `NT-012`; both, never one |
| Consequence of getting it wrong | A seller who discovers a commission change on a payout statement (`DT-039`) rather than in a notice will dispute the payout, not the change — and `KPI-C12-13` targets payout disputes below 0.2% |

#### Suppliers — inbound, approved before effect

| Element | Position |
|---|---|
| What changes | The agreed price list (`FR-SRM2-022`) |
| Direction | **The supplier proposes**; 1000FiX approves or refuses |
| Instrument | `LG-006`; the framework agreement |
| Control | **`M16` cannot raise an order above the approved price** (`BRU-SRM2-14`). The control is preventive, not corrective |
| Channel | `P05` submission and decision; `NT-011` for the outcome |
| Also outbound | Agreement expiry warns at **90, 60 and 30 days** (`BRU-SRM2-19`); expiry without renewal moves spend to uncontracted and is reported |
| Consequence of getting it wrong | A supplier who believes an increase is effective invoices at it, the three-way match fails, and both the invoice-accuracy and price-adherence metrics in `EO-006` score against them for a communication failure that was ours |

#### Brand partners — ownership depends on a field

| Element | Position |
|---|---|
| What changes | Labour rates, parts pricing and claim rules |
| Direction | **Per brand.** `MD-017` `rate_card_owner` = `brand`, `1000fix` or `negotiated` |
| Instrument | The authorisation agreement; `LG-005` |
| Where `owner = brand` | We are **notified**, and the change is reflected in `MD-029` with its effective date. Our task is ingestion, not negotiation |
| Where `owner = 1000fix` or `negotiated` | Standard outbound or bilateral change |
| Consequence of getting it wrong | Claims submitted at a superseded rate are short-paid, and the shortfall surfaces at reconciliation (`EO-003` §4.5) weeks later, per claim |

#### Corporate clients — a notice or an amendment, never both

| Element | Position |
|---|---|
| What changes | Contracted service pricing, rate schedules, uplift provisions |
| Direction | 1000FiX, **within** what the contract permits |
| **The test** | Does the contract provide for this change? **Yes → notice. No → amendment** (`M08`) |
| Instrument | The contract; `LG-003`, `LG-015` |
| Channel | `P04` plus `NT-010`, **and the account manager in person for anything structural** |
| Consequence of getting it wrong | An unagreed variation appearing on a consolidated invoice (`DT-020`) is an invoice dispute, and `04-00` targets corporate invoice disputes **below 3%** |

### 4.3 The change journey

| # | Stage | Who | Output |
|---|---|---|---|
| **1** | **Decide** | The owning function; CCO or CFO per the value | The decision, **logged in `RF-006`** with rationale, options and consequence |
| **2** | **Classify** | Commercial | Type per §4.1; ecosystems touched; whether it is structural |
| **3** | **Check the instrument** | Legal Counsel | Notice period, re-acceptance and amendment requirements per ecosystem |
| **4** | **Assess reach** | Commercial with Finance | Which counterparties, how many, and what each currently pays |
| **5** | **Set the effective date** | Finance | Effective-dated in `MD-029` (`CG-006` §3.4); **never retrospective** |
| **6** | **Pre-notice check** | Owner | §4.4 checklist |
| **7** | **Notify** | Owner, per ecosystem channel | Notice content per §4.5, bilingual where required |
| **8** | **Handle responses** | Owner | Queries answered; disputes routed to `EO-013`; exits to `EO-014` |
| **9** | **Take effect** | System | `MD-029` version becomes effective; in-flight rule §4.6 applies |
| **10** | **Review** | Commercial | §4.7 |

### 4.4 The pre-notice checklist

**Any "no" stops the notice, not the change.**

| # | Check | Why |
|---|---|---|
| 1 | Is the decision logged in `RF-006` with its rationale? | A change nobody can trace the reason for cannot be defended in a dispute |
| 2 | Has the instrument been read **for each affected ecosystem**? | The notice period is a contractual quantity, not a courtesy |
| 3 | Is the effective date **in the future**, with the full notice period ahead of it? | `CG-006` §3.4 — a transaction is evaluated against the version effective on its own date |
| 4 | Does the notice state **the old value, the new value and the effective date**? | A notice stating only the new value cannot be checked by the recipient |
| 5 | Does it state **what happens to transactions already in flight**? (§4.6) | This is the first question every counterparty asks |
| 6 | Is re-acceptance required, and is the mechanism ready? (`FR-MKP-009`) | A re-acceptance requirement discovered after notice is a second notice |
| 7 | Is a Bengali version ready **for the same send**? | A Bengali notice sent later is a second, contradictory announcement |
| 8 | Have the **other three ecosystems** been checked for the same change? | §4.8 — this is the rule the whole pack exists for |
| 9 | Do the portal, the notification and the statement all show the same value on the effective date? | `UI-*`, `NT-*` and `DT-*` diverging is how a correct change becomes a dispute |
| 10 | Is there a named person to answer queries, with a response commitment? | An unanswered query becomes a dispute at no cost to the counterparty |

### 4.5 Notice content standard

Every notice, every ecosystem, carries these eight elements in this order:

| # | Element |
|---|---|
| 1 | **What is changing** — in one sentence, in plain language |
| 2 | **The old value and the new value**, side by side |
| 3 | **The effective date** |
| 4 | **What happens to work already in progress** (§4.6) |
| 5 | **Why** — briefly, and honestly. A change with no stated reason is read as opportunism |
| 6 | **What the recipient must do**, if anything — including re-acceptance |
| 7 | **Who to ask**, with a named route and a response commitment |
| 8 | **Where the governing document is** — `LG-004`, `LG-005`, `LG-006`, `LG-007`, `LG-003`, `LG-015` or the contract |

**Prohibited in a notice:** a value with no comparison; an effective date in the past; a change
described as a "clarification" when a value moves; bundling an increase with unrelated good news;
and any wording that implies acceptance by silence where the instrument does not provide for it.

### 4.6 Effective dating and the transaction in flight

`CG-006` §3.4 states the rule and this pack applies it to the four ecosystems:

> **A transaction is evaluated against the version effective on its own date, never against the
> current version.**

| Ecosystem | The transaction's "own date" is | Which means |
|---|---|---|
| **Seller** | The job's completion date | A job awarded before and completed after the effective date settles at the **new** commission — **which is the single most disputed case and must be stated in the notice** |
| **Supplier** | The **order** date | An order raised at the old approved price is delivered and invoiced at that price, whatever changed since |
| **Brand** | The **service** date | A claim submitted after a rate change is reimbursed at the rate effective when the service was performed (`EO-004` `BC-08`) |
| **Corporate** | The service or billing-period date, per the contract | Consolidated invoices spanning an effective date are itemised at both rates |

> **The seller case deserves a decision, not an inheritance.** Settling on completion date is
> defensible and is what the effective-dating rule produces by default; settling on **award** date
> is arguably fairer to a seller who bid on a known commission. `M12` does not state which, and
> **`FR-MKP-068`'s scheme model carries `valid_from` without stating what it is compared against**.
> Recorded as `O-04`.

### 4.7 The first change cycle

The `EO` first-90-days addition, measured in changes rather than days, because a communication
standard is only tested when a change happens.

| Change | What to review | What it proves |
|---|---|---|
| **First** | Did every affected counterparty receive the notice, in their language, before the effective date? | The reach assessment at stage 4 is reliable |
| **First** | How many queries arrived, and how many were about §4.5 elements 4 and 5? | Whether the in-flight rule and the reason were actually stated |
| **Second** | Did any counterparty learn of the change from a statement rather than a notice? | The gap between `NT-*` and `DT-*` |
| **Second** | Did the portal, notification and statement agree on the effective date? | Check 9 |
| **Third** | Did a change touch more than one ecosystem, and was it coordinated? | §4.8 — the pack's core rule |
| **Every** | Disputes attributable to the communication rather than to the price | The only measure that matters |

### 4.8 Coordinating a change across ecosystems

The rule that gives the pack its reason to exist.

| # | Rule |
|---|---|
| 1 | **Before any notice, establish every ecosystem the change touches.** `MD-029` is one register serving four; a change made for one may load for all |
| 2 | **Sequence by notice period, not by convenience.** The ecosystem with the longest contractual notice is notified first, so all four take effect on one date |
| 3 | **One effective date across ecosystems** wherever the instruments permit. Staggered effective dates on one underlying change produce counterparties comparing notes and finding inconsistency |
| 4 | **Where instruments force different dates, say so in each notice.** A seller who hears that suppliers got 90 days and they got 14 will assume arbitrariness unless told it is contractual |
| 5 | **Never let one ecosystem's notice be the first another hears of it.** Brands talk to suppliers; corporate clients talk to sellers; the marketplace and the vendor base overlap in small-shop Bangladesh |
| 6 | **Franchise and channel partners (`EO-010`) are a fifth ecosystem** and are bound to the programme version at their agreement date (`BRU-PCM-12`), which can make a change inapplicable to them entirely |

### 4.9 Rules

| # | Rule |
|---|---|
| **RC-01** | This pack states **no value**. `MD-029` and the instruments hold them |
| **RC-02** | Every change is classified (§4.1) before it is communicated. The classification determines the notice period, not the other way round |
| **RC-03** | The notice period is read from the **instrument**, per ecosystem, every time. It is never assumed from precedent |
| **RC-04** | **No change is ever retrospective.** An effective date in the past is a correction, and a correction is handled under §4.1 with its own immediate notice |
| **RC-05** | Every notice carries the eight §4.5 elements, in order |
| **RC-06** | Every notice states what happens to work in flight (§4.6) |
| **RC-07** | A promotional change states its **reversion date in the original notice** |
| **RC-08** | The Bengali version is sent **in the same despatch** as the English, never after (`CP-05`, `CG-010`) |
| **RC-09** | Every change decision is logged in **`RF-006`** with its rationale before notice (`CG-006`) |
| **RC-10** | Supplier increases are described as **submitted, justified and approved** — never as "notified" (`FR-SRM2-023`, `BRU-SRM2-14`) |
| **RC-11** | Alliance benefits are applied by the pricing engine and **never configured as an ad-hoc discount** (`BRU-PCM-19`); a benefit change follows this pack like any other |
| **RC-12** | Where `MD-017` `rate_card_owner` = `brand`, our process is **ingestion with an effective date**, not negotiation |
| **RC-13** | A counterparty's route to query, dispute or exit is stated in every notice (`EO-013`, `EO-014`) |
| **RC-14** | **No seller settlement, invoicing or VAT logic is built or changed before the principal/agent opinion is documented** (`BRU-MKP-15`). A commission change that alters the tax treatment is blocked by the same rule |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`MD-029`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md) | The register every change lands in, effective-dated |
| [`MD-017`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md), [`MD-018`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md), [`MD-016`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md), `MD-032` | Brand rate ownership, seller commission bands, supplier terms, contract templates |
| [`CG-006`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) §3.4 | The effective-dating rule §4.6 applies |
| `M11`, `M53`, `M20` | Pricing, settlement and invoicing that consume the change |
| `M42` `FR-SRM2-022`, `FR-SRM2-023` | The inbound supplier pattern |
| `M12` `FR-MKP-068`, `FR-MKP-069`, `FR-MKP-009` | The outbound seller pattern and the re-acceptance trigger |
| `M40` `BRU-PCM-03`, `BRU-PCM-12`, `BRU-PCM-19` | Partner programme versioning and benefit application |
| `M08` | Where a corporate change becomes an amendment |
| [`LG-003`](../10_Legal_Policy_and_Compliance/LG-003_Portal_Terms_of_Use_Corporate.md), [`LG-004`](../10_Legal_Policy_and_Compliance/LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md), [`LG-005`](../10_Legal_Policy_and_Compliance/LG-005_Brand_Partner_Portal_Terms.md), `LG-006`, `LG-007`, `LG-015` | The instruments the notice period is read from |
| [`NT-010`](../04_Notification_and_Messaging/04C_Email/NT-010_Email_Template_Library_Corporate_and_B2B.md)…[`NT-013`](../04_Notification_and_Messaging/04C_Email/NT-013_Email_Template_Library_Brand_Partner_Claims.md) | The templates this pack sets the content standard for |
| [`DT-020`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-020_Consolidated_Corporate_Invoice.md), [`DT-039`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-039_Marketplace_Seller_Payout_Statement.md), [`DT-040`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-040_Partner_Commission_Statement.md) | Where a change becomes visible if the notice failed |
| **`RF-006`** | The decision log — **unwritten** |
| [`EO-001`](EO-001_Marketplace_Seller_Onboarding_Kit.md), [`EO-003`](EO-003_Brand_Partner_Onboarding_Pack.md), [`EO-005`](EO-005_Vendor_and_Supplier_Onboarding_Pack.md), `EO-007`, `EO-009`, `EO-010` | The kits that point here for change communication |
| [`EO-013`](EO-013_Ecosystem_Dispute_Resolution_Content.md), [`EO-014`](EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | Dispute and exit routes stated in every notice |

> **Rule-citation attribution.** **BRU-MKP-\***  → `M12` §9 · **BRU-PCM-\***  → `M40` §9 · **BRU-SRM2-\***  → `M42` §9 — these are **module-scoped** rule families and **`05-05` carries none of them**. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually, and after every change that touches more than one ecosystem |
| Trigger for out-of-cycle review | A new ecosystem or portal; a change to a notice period in any instrument; a dispute traced to the communication rather than the price; the principal/agent determination landing; `RF-006` being written; a `CG-006` change to effective dating |
| Owner | Commercial, with Finance for §4.6 and Legal for §4.2 notice periods |
| Change control | A change to §4.5's eight elements or to §4.8's coordination rule requires CCO and CFO sign-off — both alter what counterparties are entitled to be told |
| Effectiveness measure | **Disputes attributable to communication rather than to price**, per change cycle; and the count of counterparties who learned of a change from a statement rather than a notice — which should be zero |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This pack is W4 and rate cards go live at W3.** `06-01` §3 Wave 3 delivers *"price books, rate cards, quotation engine, discount governance"* and the vendor portal; `MD-029` loads at W3. **The first price change is therefore possible a wave before the standard that governs how it is communicated exists**, and `EO-005` (W3) and `EO-006` (W3) both point here for change communication — **a W3 file citing a W4 file for an operative process**. `AUDIT-014` TS-02 recorded nine instances of the same defect in Category 13 and asked for the register's sequencing basis to be corrected once, register-wide | Programme Content Lead with CCO | **W3 — before the first rate card is published** |
| **O-02** | **"Material change" is undefined, and it is the trigger for seller re-acceptance.** `FR-MKP-009` requires re-acceptance on material change; `LG-004` §4.5 and §4.8 are **drafted as alternatives pending `O-01`/`O-03`** in that file. §4.2 therefore cannot say which commission changes require a signature and which require a notice — **and the difference is the difference between a 500-seller re-signature exercise and an email** | Legal Counsel with CCO | **W7 — before the first commission change** |
| **O-03** | **`RF-006` decision log is unwritten and `RC-09` requires every change decision logged there before notice.** Category 99 is unstarted. `AUDIT-014` TS-12 records `RF-006` as blocking `TS-018` `TR-10` for the same reason, and notes that **`RF-006` was created in this register specifically so content would not repeat the module repository's missing `00-05`** (`AF-04`). **This is the second category to be blocked by its absence** | Programme Content Lead | **W1** |
| **O-04** | **The seller in-flight rule is undecided.** §4.6 applies `CG-006` §3.4 by default — a job settles at the commission effective on its **completion** date — and notes that **award** date is arguably the fairer basis for a seller who bid on a known rate. `FR-MKP-068`'s scheme carries `valid_from` and states nothing about what it is compared against. **This is the most disputable single case in the pack and it is currently resolved by inheritance rather than by decision** | CFO with CCO and Marketplace Operations | **W7 — before the first commission change** |
| **O-05** | **No notice period is stated in any instrument yet.** §4.2 and `RC-03` require the period to be read from `LG-003`…`LG-007` and `LG-015`; **none of those files carries a numeric notice period for a pricing change**, and `AUDIT-013` records all 24 `LG` files as awaiting gate `G5`. The pack specifies a process whose central quantity does not yet exist in any of its five governing instruments | Legal Counsel | **W4 — before the first coordinated change** |
| **O-06** | **The four `NT` template families are English-first and this pack's notices must be bilingual in the same despatch** (`RC-08`). `CG-010` §3.2 makes **`NT-011` vendor and `NT-013` brand-partner email English-only**, which is correct for those audiences — **but a single change touching all four ecosystems then produces two bilingual notices and two English ones from one decision**, and §4.8 rule 5 warns that these populations talk to each other. The interaction has not been assessed | Localisation Lead with Content Design Lead | **W4** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the first-90-days addition replaced by a **first change cycle** and the substitution declared
- [x] Content class **E** assigned, with the reasoning: the failure mode is inconsistency and rework across ecosystems, not a user-facing or contractual failure
- [x] **The four ecosystems distinguished by the direction the change travels, which is the pack's central insight**
- [x] Seven-type change taxonomy, each mapped to notice, re-acceptance and amendment requirements
- [x] Ten-stage change journey ending in a review rather than in the effective date
- [x] Ten-point pre-notice checklist in which any "no" stops the notice
- [x] Eight-element notice content standard, plus five prohibited constructions
- [x] **Effective-dating applied per ecosystem, with the "transaction's own date" resolved differently for each**
- [x] The seller in-flight case identified as resolved by inheritance rather than decision, and raised
- [x] First-change-cycle review measured in changes, with communication-attributable disputes as the only real measure
- [x] Six cross-ecosystem coordination rules, including the fifth-ecosystem franchise case
- [x] Fourteen rules
- [x] All internal links resolve
- [x] Six open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` pack is W4, rate cards are W3, and two W3 files cite it — outstanding**
- [ ] **`O-02` "material change" undefined — outstanding; the seller re-acceptance trigger has no definition**
- [ ] **`O-03` `RF-006` unwritten — outstanding; `RC-09` undischargeable**
- [ ] **`O-04` seller in-flight rule undecided — outstanding**
- [ ] **`O-05` no notice period exists in any of the five governing instruments — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approver recorded — **pending Programme Content Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
