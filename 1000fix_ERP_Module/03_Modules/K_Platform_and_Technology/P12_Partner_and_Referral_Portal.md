---
id: FIX-ERP2-P12
portal_id: P12
portal_code: PRP
portal_name: Partner & Referral Portal
type: External Web Portal (channel and referral partners)
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Digital Channels Squad
priority: P2
wave: W7
---

# P12 — Partner & Referral Portal
### Portal Suite · Code `PRP` · ★ New in v2.1

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P12 |
| **Portal code** | `PRP` |
| **Type** | External web portal for channel, referral and reseller partners |
| **Status** | ★ New in v2.1 — the Partner Alliance Program had no system in v1.0 |
| **Priority** | **P2** |
| **Delivery wave** | **W7** (Months 27–30) |
| **Users** | Alliance partners, referral partners, corporate resellers |
| **Volume** | **100–500 partner organisations**; target > 200 active referral partners by end of W8 |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Digital Channels Squad |
| **Technology** | Next.js 15 (React 19), shared design system |
| **Custom development** | `CD-213` |
| **Requirement range** | FR-POR-335 … FR-POR-358 |
| **Requirement count** | **24** *(measured — supersedes the 2 allocation in `05-01` §4)* |
| **Effort estimate** | **14 person-weeks** |
| **Backing modules** | M07, M10, M11, M12, M14, M20, M24, M33, M35, M38, M40, M53 |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M65 Localisation |

---

## 2. Purpose

P12 is **the surface for people who bring 1000FiX business without performing it**. It serves
three related but distinct relationships that share one need — attribution and payment:

| Partner type | What they do | What they need |
|---|---|---|
| **Referral partner** | Introduces customers | A trackable link or code, and commission when it converts |
| **Alliance partner** | Extends member or customer benefits to their own base | A benefit schedule, co-marketing material, and performance visibility |
| **Corporate reseller** | Sells refurbished stock and services onward | Stock allocation, pricing, ordering, fulfilment and settlement |

The Company already runs a **Partner Alliance Program** and a **Privileged Program** for
business partners, and P01 generates referral links for retail customers. What has never
existed is a system: attribution is manual, commission is calculated by hand, and a partner
cannot see whether the lead they sent converted.

P12 holds no authoritative state. The lead belongs to M07, the commission to M53, the stock
allocation to M14 and M15. What P12 owns is **the partner's view of what they have contributed
and what they are owed**.

### Why It Exists

**Referral is the cheapest acquisition channel and it is currently unmeasured.** `04-00`
targets **referral-attributed new customers above 12%** and **200 active referral partners**.
Neither is achievable without trackable attribution, and attribution done by hand does not
scale past a dozen partners.

**Commission accuracy is the entire trust proposition.** `04-00` sets **partner commission
accuracy at 100%** — the only portal KPI in the suite set at exactly 100% for a financial
measure. A partner paid late or short does not send the next lead, and the relationship costs
more to repair than it earned.

**Alliance partners extend reach without cost.** A corporate alliance offering 1000FiX benefits
to its own members reaches an audience the Company would otherwise pay to acquire. That
programme needs a benefit schedule the partner can see and material they can use.

**Refurbished resale needs a channel.** M14 produces refurbished devices, and retail alone
cannot absorb the volume. Corporate resellers are the channel, and they need allocation,
pricing, ordering and settlement — which is a different relationship from a referral partner
and is why this portal serves three types rather than one.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Company Profile §Partner Alliance Program | "Privileged program for business partners; special corporate rates; collaborative service agreements" — the programme this portal systematises |
| Company Profile §Privileged Program | Member benefits and priority access — extended to alliance partners' bases |
| ERP BRD BR-CRM-010 | "Promotional campaign management with coupon/voucher generation and tracking" — the mechanism behind referral codes |
| ERP BRD BR-CRM-006 | Privilege Program tiers with enrolment, upgrade, benefit application and renewal |
| ERP BRD BR-FIN-013 | Complete, immutable audit trail — commission calculation must be traceable |
| Scope Charter §6.2 | **Refurbishment & resale margin: BDT 65 lac/year** (M14) — the reseller channel contributes to it |
| Scope Charter §6.2 | **Customer retention: BDT 78 lac/year** (M07 + M10 + M27) — referral supports acquisition and retention |
| `04-00` §P12 | Capability set across seven areas and four KPIs, adopted verbatim |
| `04-00` §3 PS-01…PS-12 | Twelve cross-portal standards, all binding |
| `05-04` §1 R38 | External Party covering the referral partner sub-class; MFA required for financial actions |
| `05-04` §2 | P12 access held by R23 Marketing Manager and R38 only |
| `M40` (Category C) | Partner, Channel, Alliance & Franchise — the module behind this portal |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Partner application, document submission, agreement execution and approval tracking |
| 2 | Partner type declaration — referral, alliance, reseller — and the surfaces each receives |
| 3 | Profile and contact maintenance |
| 4 | Referral link and code generation, sharing and management |
| 5 | Direct lead submission with customer consent captured |
| 6 | Lead status tracking through to conversion |
| 7 | Attribution visibility: which lead became which customer and which revenue |
| 8 | Benefit schedule: what the partner's members or customers receive |
| 9 | Commission: earned by referral, statements, payout schedule and history |
| 10 | Co-marketing: approved material access, co-branded campaign request, campaign performance |
| 11 | Reseller: refurbished stock allocation, pricing, ordering, fulfilment tracking and settlement |
| 12 | Performance: leads submitted, conversion rate, revenue attributed, ranking |
| 13 | Bengali and English throughout |
| 14 | Instrumentation of partner adoption, referral volume and conversion |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Marketplace sellers who perform service work** | **P07** | A seller delivers a job; a partner introduces one. Different verification, different standards, different payment basis |
| **Suppliers who sell to 1000FiX** | **P05** | Direction of value is opposite |
| **Corporate clients who buy service for themselves** | **P04** | A reseller sells onward; a corporate client consumes |
| **Brand partners** | **P08** | An OEM relationship is warranty and consignment, not referral |
| **Individual retail customers who refer friends** | **P01** (FR-POR-036) | Retail referral is a loyalty feature in P01; P12 is for organisations with an agreement |
| **Partner programme design, tiers, commission rates and approval** | **M40** Partner, Channel, Alliance & Franchise | P12 presents; M40 governs |
| **Lead qualification, opportunity management and conversion** | **M07** CRM | A partner submits a lead; 1000FiX works it |
| **Commission calculation, settlement and payout execution** | **M53** Revenue, Commission & Settlement | P12 shows the wallet; M53 computes and pays |
| **Campaign design, content and execution** | **M35** Marketing & Campaigns | P12 distributes approved material; M35 creates it |
| **Loyalty tier rules, points and voucher validity** | **M10** Loyalty | P12 shows the benefit schedule; M10 owns the arithmetic |
| **Refurbished stock grading, pricing and availability** | **M14 / M15 / M11** | P12 shows allocation; the stock and price are elsewhere |
| **Order fulfilment and delivery** | **M38 / M03** | P12 shows tracking |
| **Customer identity and personal data beyond the submitted lead** | **M33** | **A partner sees the leads they submitted, never the Company's customer base** |
| **Identity, session policy and MFA** | **M29** | **PS-01**; MFA required for financial actions |

### 3.3 Shared Concepts

| Concept | P12's Role | Owning Module |
|---|---|---|
| The partner's view of contribution and entitlement | **Owns** — the defining concern of this portal | P12 |
| Partner record, tier, agreement | Submits and displays | M40 |
| Referral link and code | Generates within M40's scheme | M40 / M10 |
| Lead | Submits; tracks status | M07 |
| Attribution | Displays; M07 and M53 determine it | M07 / M53 |
| Commission and payout | Displays; requests payout | M53 |
| Benefit schedule | Displays | M10 / M40 |
| Co-marketing material | Distributes; requests co-branding | M35 |
| Refurbished stock allocation | Displays; places orders | M14 / M15 / M38 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Partner Relationship Management practice (Magentrix, Channeltivity, ZINFI, Mindmatrix)** | A branded partner portal with self-service access, **deal registration with conflict detection**, training and certification, content management with role-based access, co-branding tools, MDF and incentive management, analytics dashboards and bi-directional CRM integration | **Deal registration with conflict detection is the single most influential external reference for P12.** A partner who submits a lead needs protection from the Company's own sales team pursuing the same account, and without that protection partners stop submitting. This is the mechanism that makes a referral programme credible | Full MDF (market development fund) administration. It is a mature-channel capability and disproportionate for 100–500 partners at this stage; the co-marketing request path is the lighter equivalent |
| **Deal registration practice** | A partner formally submits an opportunity; the vendor reviews and approves, giving protection from channel conflict and often preferential commission for that account | **The registration → review → protection sequence**, with a stated protection period. A lead submitted and neither approved nor rejected is the most common cause of partner attrition | Automatic approval; a registration that is never reviewed is worse than a rejection |
| **Referral and commission tracking practice** | Referral capture, referral-fee monitoring and commission calculation on defined performance | **Attribution visible to the partner at every stage**, from link click through lead, opportunity, conversion and revenue. A partner who cannot see why they were paid a given amount assumes they were underpaid | Multi-tier or sub-affiliate commission structures |
| **Co-branding and channel marketing (TCMA)** | Co-branded content partners customise while brand standards are maintained; email templates, social assets and landing pages carrying both brands | **Approved material with a co-branding request path**, so partners get usable assets without the brand losing control of how it is presented | Full through-channel marketing automation |
| **Channel analytics practice** | Partner-sourced pipeline, deal registration conversion rate, partner engagement score and training completion | **Partner-facing performance including ranking**, which is what converts a passive partner into an active one | Partner scoring used punitively; the relationship is voluntary and low-cost to exit |
| **Reseller and allocation practice** | Stock allocation, agreed pricing, order placement, fulfilment tracking and settlement | **Allocation as a visible entitlement**, so a reseller knows what they may sell before they sell it — which is the alternative to overselling refurbished stock that does not exist | Full distributor management; the reseller channel here is a resale outlet, not a distribution tier |

**Design position.** Four deliberate differences from the benchmark.

First, **attribution is transparent at every stage.** A partner sees the click, the lead, its
status, the conversion and the commission — decomposed, not as a total. `04-00` sets commission
accuracy at 100%, and accuracy that cannot be inspected is indistinguishable from inaccuracy in
the partner's judgement.

Second, **deal registration protects the partner, with a stated clock.** A submitted lead is
reviewed within a defined period and either protected or declined with a reason. Silence is not
an outcome. This is what distinguishes a referral programme from a suggestion box.

Third, **three partner types, one portal, distinct surfaces.** A referral partner never sees
stock allocation; a reseller never sees a benefit schedule they cannot extend. Building three
portals for 100–500 organisations would not be justified; presenting all three surfaces to
everyone would confuse all of them.

Fourth, **the partner never sees the customer base.** They see the leads they submitted and the
customers those became, at the level of detail the customer consented to. A referral programme
is not a route to the Company's customer data, and the consent captured at lead submission is
what makes the introduction lawful.

---

## 5. Capability Areas & Functions

### 5.1 Onboarding & Profile

| FR ID | Feature | Function — "The portal shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-335 | Partner application | Allow an organisation to apply, declare its partner type — referral, alliance or reseller — and submit the documents that type requires | **P0** | L5 |
| FR-POR-336 | Approval tracking | Show the applicant where their application stands, what remains outstanding and the expected decision time | **P0** | L5 |
| FR-POR-337 | Agreement execution | Present the partner agreement in Bengali and English, capture digital execution, and retain the executed version with its reference | **P0** | L5 |
| FR-POR-338 | Type-scoped surfaces | Present only the surfaces the partner's declared type entitles them to | **P0** | L5 |
| FR-POR-339 | Profile and users | Maintain the organisation's profile, contacts and portal users, managed by the partner's own administrator | P1 | L5 |
| FR-POR-340 | Transaction gate | Prevent a partner from generating referral links, submitting leads or placing orders until documents are verified, the agreement is executed and approval is granted | **P0** | L5 |

### 5.2 Referral & Lead Submission

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-341 | Referral link and code | Generate trackable referral links and codes within the scheme M40 defines, per campaign or per channel, and allow the partner to manage and retire them | **P0** | L5 |
| FR-POR-342 | Sharing | Provide ready-to-share formats — link, QR code, short code and message templates in Bengali and English | P1 | L5 |
| FR-POR-343 | **Direct lead submission** | Accept a lead submitted directly with the prospective customer's details, requirement and **the customer's consent to be contacted**, recorded with a timestamp | **P0** | L5 |
| FR-POR-344 | **Deal registration and protection** | Register a submitted lead against an account, review it within a stated period, and either **protect it for a defined term** or decline with a reason — never leave it unanswered | **P0** | L5 |
| FR-POR-345 | Conflict detection | Detect at submission whether the account is already an active customer or an open opportunity, and inform the partner of the outcome before they invest effort | **P0** | L5 |
| FR-POR-346 | Lead status tracking | Show every submitted lead's status through qualification, opportunity, conversion or loss, with the reason where lost | **P0** | L5 |

### 5.3 Attribution, Commission & Payout

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-347 | **Attribution trail** | Show, for every conversion, the chain from click or code through lead, opportunity and conversion to the revenue attributed — decomposed, not as a total | **P0** | L5 |
| FR-POR-348 | Commission calculation visibility | Show the commission basis, rate, qualifying revenue and calculated amount per conversion, with the rule version that governed it | **P0** | L5 |
| FR-POR-349 | Statements | Provide period statements of commission earned, adjusted, paid and outstanding, suitable for the partner's own accounting | **P0** | L5 |
| FR-POR-350 | Payout schedule and history | Show the payout schedule, any hold and its reason, payout history and remittance references | **P0** | L5 |
| FR-POR-351 | Payout request and bank details | Allow a payout request and bank detail maintenance, both MFA-gated, with a bank change held for out-of-band verification | **P0** | L5 |
| FR-POR-352 | Adjustment transparency | Where a commission is adjusted or reversed — cancelled order, refund, clawback — show the reason and the originating transaction | **P0** | L5 |

### 5.4 Benefits, Co-Marketing & Reseller

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-353 | Benefit schedule | Present the benefit schedule available to the partner's members or customers — service discounts, priority access, privilege enrolment — with the terms and validity | **P0** | L5 |
| FR-POR-354 | Benefit redemption visibility | Show how many of the partner's members have enrolled and redeemed, without exposing individual member identity beyond what consent permits | P1 | L5 |
| FR-POR-355 | Co-marketing material | Provide approved marketing material — assets, templates, product information — with usage terms, in Bengali and English | P1 | L5 |
| FR-POR-356 | Co-branded campaign request | Allow a partner to request a co-branded campaign, track its approval and production, and view its performance against agreed measures | P2 | L5 |
| FR-POR-357 | **Reseller allocation and ordering** | For resellers: present the allocation of refurbished stock available to them with agreed pricing, place orders against it, track fulfilment, and view settlement | P2 | L5 |
| FR-POR-358 | **Performance and ranking** | Present leads submitted, conversion rate, revenue attributed, commission earned and the partner's ranking within their tier, with the underlying records | P1 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No authoritative state** | P12 persists no business object (`04-00` §1) |
| T-02 | **Partner isolation** | Every query is scoped to the authenticated partner organisation. A partner never sees another partner's leads, commission, ranking detail or allocation |
| T-03 | **Customer-base isolation** | A partner sees **only the leads they submitted and the customers those became**, at the consented level of detail. There is no path from P12 to the Company's wider customer base |
| T-04 | **Attribution integrity** | Attribution is computed by M07 and M53 and displayed with its full chain. A commission figure without a traceable chain is not displayed |
| T-05 | **Consent capture** | A directly submitted lead records the prospective customer's consent to be contacted, with timestamp, source and wording version, retained under M24 policy |
| T-06 | **Deal registration clock** | The review period is a stored, alertable deadline; an unreviewed registration escalates rather than expiring silently |
| T-07 | **Conflict detection at submission** | The account-conflict check runs synchronously and returns a result before the partner invests effort |
| T-08 | **Commission rule versioning** | Every commission records the rule version that governed it; a rate change never retroactively alters a calculated commission |
| T-09 | **MFA on financial actions** | MFA required for payout request, bank detail change and reseller order placement (`05-04` §1) |
| T-10 | **Bank change control** | A payout bank change requires MFA, is held for out-of-band verification, and excludes the partner from the next payout run |
| T-11 | **Type-scoped surfaces** | Surface visibility derives from the partner's declared and approved type, enforced server-side |
| T-12 | **All traffic through the gateway** | Every call routes through M28 with per-partner credentials and rate limits (**PS-02**) |
| T-13 | **No client-side business logic** | Commission, attribution, allocation and eligibility are computed by their owning module (**PS-11**) |
| T-14 | **Referral link integrity** | Links and codes are unforgeable, attributable, revocable, and expire per the scheme; a retired code attributes nothing |
| T-15 | **Bengali and English** | Complete in both, including shareable message templates (**PS-03**) |
| T-16 | **Accessibility and responsiveness** | WCAG 2.1 AA; usable from 320 px upward — many partners will use a phone (**PS-04, PS-05**) |
| T-17 | **Design system** | Shared component library with P01, P04, P07, P08 and P10 (**PS-06**) |
| T-18 | **Graceful degradation** | Where a backing module is unavailable, the capability is disabled with an explanation and a named contact (**PS-09**) |
| T-19 | **Instrumentation** | Partner adoption, referral volume, conversion and payout accuracy instrumented to M25 (**PS-10**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Actor

| Actor | Today | With P12 |
|---|---|---|
| **Referral partner** | Sends a name by phone and hopes to be paid | Shares a trackable link, watches the lead convert, sees the commission calculated |
| **Alliance partner** | Extends a benefit they cannot describe precisely | Presents a documented benefit schedule and sees uptake among their members |
| **Corporate reseller** | Asks what refurbished stock is available | Sees their allocation, prices it, orders it and tracks settlement |
| **Partner's finance contact** | Queries a commission figure they cannot check | Sees the attribution chain behind every taka |
| **1000FiX sales manager** | Cannot tell whether a lead is partner-sourced | Sees attribution, and channel conflict is detected before it becomes a dispute |
| **Marketing manager** | Cannot measure referral as a channel | Sees referral volume, conversion and cost per acquisition against other channels |
| **Finance** | Calculates partner commission by hand | Commission computed by M53, published with its basis, paid on schedule |
| **Retail operations (M14)** | Refurbished stock competes for retail attention alone | Has a reseller channel with visible allocation |
| **CCO** | Runs a Partner Alliance Program with no instrumentation | Sees partner-sourced pipeline, conversion and revenue by partner and tier |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Referral-attributed acquisition** | Trackable links, direct lead submission, deal protection and visible commission | `04-00` target: **> 12% of new customers referral-attributed**, and **> 200 active referral partners**. Referral is materially the cheapest acquisition channel available |
| **Customer acquisition cost** | Partner-sourced customers acquired at commission cost rather than campaign cost | Contributes to the **BDT 78 lac/year** retention and acquisition benefit attributed to M07 + M10 + M27 |
| **Refurbished resale volume** | A reseller channel with visible allocation, pricing and settlement | Supports the **BDT 65 lac/year** refurbishment and resale margin attributed to M14, by giving output a route beyond retail |
| **Alliance reach** | Benefits extended through partners' own member bases | Reaches audiences the Company would otherwise pay to acquire |
| **Commission accuracy** | Computed by M53, published with its basis | `04-00` target: **100% commission accuracy**. Every inaccuracy costs a partner relationship worth more than the error |
| **Channel conflict avoidance** | Conflict detected at submission; deal registration protects the partner | Prevents the disputes that end partner programmes, and prevents the Company paying commission twice on one account |
| **Marketing attribution** | Referral measurable alongside every other channel | Makes channel mix a decision rather than an assumption |
| **Administrative labour** | Manual attribution and hand-calculated commission eliminated | Contributes to the **BDT 62 lac/year** administrative saving |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The Partner Alliance Program becomes real** | An existing programme with no system is a page on a website. P12 makes it a measurable business relationship |
| **Trust through transparency** | A partner who can inspect the attribution chain behind their commission does not need to trust — they can verify |
| **Consent captured at introduction** | A lead submitted with recorded consent is a lawful introduction; one submitted without is a data-protection exposure the Company would carry |
| **Customer base protected** | Partners see their own leads, never the customer base. This holds a boundary that commercial pressure will test |
| **Channel discipline** | Deal registration with conflict detection prevents the internal sales conflicts that quietly kill partner programmes |
| **Brand consistency** | Approved co-marketing material with usage terms means the brand appears consistently across partners |
| **Expansion readiness** | Partner-sourced reach is the lowest-capital route into a new city or segment |

---

## 8. Journeys & State Models

### 8.1 The Referral Journey — attribution end to end

```
   PARTNER GENERATES a link or code (scheme defined by M40)
        │
   ┌────▼───────────────────────────────────────┐
   │  SHARED — link · QR · short code · template │
   └────┬───────────────────────────────────────┘
        │
   ┌────▼──────────────────┬─────────────────────────────────┐
   │  CUSTOMER CLICKS      │  OR  PARTNER SUBMITS A LEAD     │
   │  → books in P01       │      DIRECTLY (consent captured)│
   └────┬──────────────────┴──────────────┬──────────────────┘
        │                                 │
        │                       ┌─────────▼─────────────────┐
        │                       │  CONFLICT CHECK           │
        │                       │  already a customer?      │
        │                       │  open opportunity?        │
        │                       └─────────┬─────────────────┘
        │                                 │ clear
        │                       ┌─────────▼─────────────────┐
        │                       │  DEAL REGISTRATION        │
        │                       │  reviewed within a stated │
        │                       │  period → PROTECTED for a │
        │                       │  defined term, or DECLINED│
        │                       │  with a reason            │
        │                       │  ✖ silence is not an      │
        │                       │    outcome (T-06)         │
        │                       └─────────┬─────────────────┘
        │                                 │
   ┌────▼─────────────────────────────────▼──────┐
   │  LEAD IN M07 — attributed to the partner     │
   └────┬─────────────────────────────────────────┘
        │
   ┌────▼──────────────┬──────────────────────────┐
   │  QUALIFIED        │  LOST (reason shown       │
   │  → OPPORTUNITY    │   to the partner)         │
   └────┬──────────────┴──────────────────────────┘
        │ converted
   ┌────▼─────────────────────────────────────────┐
   │  CUSTOMER · REVENUE RECOGNISED                │
   └────┬─────────────────────────────────────────┘
        │
   ┌────▼─────────────────────────────────────────┐
   │  COMMISSION CALCULATED (M53)                  │
   │   basis · rate · qualifying revenue ·         │
   │   RULE VERSION · amount                       │
   └────┬─────────────────────────────────────────┘
        │
   ┌────▼─────────────────────────────────────────┐
   │  PUBLISHED TO THE PARTNER WITH THE FULL CHAIN │
   │  click → lead → opportunity → conversion →    │
   │  revenue → commission                          │
   └────┬─────────────────────────────────────────┘
        │ payout schedule
   ┌────▼──────────────┐        ┌───────────────────────────┐
   │  PAID             │◄───────┤ ADJUSTED / CLAWED BACK    │
   │  remittance ref   │        │ reason + originating txn  │
   └───────────────────┘        │ shown (FR-POR-352)        │
                                └───────────────────────────┘
```

### 8.2 Partner Lifecycle

```
   APPLIED ──documents + type declared──► UNDER REVIEW
                                              │
                            ┌─────────────────┴────────┐
                      approved                    declined
                            │                          ▼
                      ┌─────▼──────┐              DECLINED
                      │ AGREEMENT  │
                      │ EXECUTED   │
                      └─────┬──────┘
                            │  ◄── TRANSACTION GATE (FR-POR-340)
                      ┌─────▼──────┐
                      │   ACTIVE   │◄─────────────┐
                      └──┬──────┬──┘              │ re-engaged
                         │      │ no activity for │
                         │      │ the configured  │
                         │      │ period          │
                         │  ┌───▼──────────┐      │
                         │  │  DORMANT     │──────┘
                         │  └───┬──────────┘
                         │      │ agreement lapsed or terminated
                         │  ┌───▼──────────┐
                         └─►│ OFFBOARDED   │──► final settlement after
                            └──────────────┘    the attribution window
```

| Transition | Guard | Actor |
|---|---|---|
| Applied → Under review | Documents complete for the declared type | System |
| Under review → Active | M40 approval **and** agreement executed | R23 / CCO |
| Active → Dormant | No referral, lead or order for the configured period | System, automatic |
| Dormant → Active | Any qualifying activity | System |
| Active / Dormant → Offboarded | Agreement lapsed or terminated | CCO |
| Offboarded → final settlement | Attribution window elapsed and commissions settled | M53 |

> **The attribution window matters at offboarding.** A lead submitted before offboarding that
> converts afterwards still earns commission within the protection term. Settling too early is a
> dispute; settling too late is a liability carried indefinitely. The window is defined in the
> agreement and enforced by M53.

---

## 9. Portal Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P12-01 | A partner may access only their own records — leads, commission, allocation, ranking detail | **H** | CTO |
| PRU-P12-02 | **A partner sees only the leads they submitted and the customers those became; there is no path to the Company's wider customer base** | **H** | CTO / Legal |
| PRU-P12-03 | P12 persists no authoritative business state (`04-00` §1) | **H** | CTO |
| PRU-P12-04 | A partner cannot generate links, submit leads or place orders until verified, agreement-executed and approved | **H** | Chief Commercial Officer |
| PRU-P12-05 | A directly submitted lead records the prospective customer's consent to be contacted, with timestamp and wording version | **H** | Legal |
| PRU-P12-06 | A deal registration is reviewed within the stated period and either protected or declined with a reason; it never expires unanswered | **H** | Chief Commercial Officer |
| PRU-P12-07 | Conflict detection runs at submission and its result is shown to the partner before they invest effort | **H** | Chief Commercial Officer |
| PRU-P12-08 | Every commission records the rule version that governed it; a rate change never retroactively alters a calculated commission | **H** | CFO |
| PRU-P12-09 | Every commission is displayed with its full attribution chain; a figure without a traceable chain is not displayed | **H** | CFO |
| PRU-P12-10 | A commission adjustment or clawback shows its reason and the originating transaction | **H** | CFO |
| PRU-P12-11 | MFA is required for payout request, bank detail change and reseller order placement | **H** | CFO |
| PRU-P12-12 | A payout bank change is held for out-of-band verification and excludes the partner from the next payout run | **H** | CFO |
| PRU-P12-13 | A partner sees only the surfaces their approved type entitles them to | **H** | Chief Commercial Officer |
| PRU-P12-14 | A retired referral code attributes nothing from the moment of retirement | **H** | Chief Commercial Officer |
| PRU-P12-15 | Benefit redemption is reported in aggregate; individual member identity is not exposed beyond consent | **H** | Legal |
| PRU-P12-16 | Co-marketing material carries usage terms, and co-branded output requires approval before publication | **H** | Marketing Manager |
| PRU-P12-17 | Reseller allocation is an entitlement ceiling; an order beyond allocation is refused, not queued | **H** | Retail Operations Head |
| PRU-P12-18 | Commission, attribution, allocation and eligibility are computed by their owning module (**PS-11**) | **H** | CTO |
| PRU-P12-19 | Every screen and shareable template exists in Bengali and English (**PS-03**) | **H** | Chief Commercial Officer |

---

## 10. Data, Caching & State Model

### 10.1 What P12 Holds

| Object | Purpose | Ownership |
|---|---|---|
| Partner portal user accounts and type scoping | Which people at a partner may do what | **P12**, identity in M29 |
| Draft lead submissions | Recovery of an interrupted submission | **P12**, transient |
| Saved views and filters | Per partner user | **P12** |
| Session and preference | Language, landing surface | M29 / P12 |

### 10.2 Never Held

| Item | Reason |
|---|---|
| **Any customer data beyond the partner's own submitted leads and their conversions** | PRU-P12-02 — the portal's defining constraint |
| Any business object — lead, commission, allocation, order | PRU-P12-03 |
| Another partner's data of any kind | PRU-P12-01 |
| Commission rates, attribution logic or allocation rules | PRU-P12-18 |
| Bank credentials beyond a submitted change awaiting verification | PRU-P12-12 |
| 1000FiX internal cost, margin or pipeline outside the partner's own leads | External party isolation (`05-04` §8) |

### 10.3 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.partner`, tier, agreement, programme terms | **M40** | Read; submit application and profile |
| `fix.lead`, `fix.opportunity`, conversion | **M07** | Submit; read status and outcome |
| `fix.deal.registration`, protection term | M40 / M07 | Submit; read decision |
| `fix.commission`, `fix.settlement`, payout | **M53** | Read; request payout |
| `fix.referral.code`, `fix.voucher` | M10 / M40 | Generate within scheme; read performance |
| `fix.loyalty.benefit` schedule | M10 | Read |
| `fix.campaign`, approved material | **M35** | Read; request co-branding |
| Refurbished stock allocation and price | **M14 / M15 / M11** | Read; place orders |
| `fix.sale.order`, fulfilment | M38 / M03 | Create; read tracking |
| `fix.party` | M33 | Partner identity; submitted lead contacts |
| `fix.document` | M24 | Upload application documents; retrieve agreements and material |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P12-01 | Application submitted | Route to M40 for review, show the applicant the outstanding items, and state the expected decision time | Application held; applicant informed |
| AUT-P12-02 | Partner approved | Release the agreement for execution, then open the transaction gate | Gate stays closed until both complete |
| AUT-P12-03 | Lead submitted directly | Run conflict detection synchronously and return the result before submission completes | Block submission rather than accept an unchecked lead |
| AUT-P12-04 | Deal registration created | Start the review clock, notify the reviewing sales manager, and escalate on expiry of the review period | **Escalate; never allow silent expiry** |
| AUT-P12-05 | Deal registration decided | Notify the partner with the outcome, the protection term where protected, and the reason where declined | Notify; decision visible in-portal |
| AUT-P12-06 | Lead status changes in M07 | Update the partner's view, including a loss reason where lost | Update on next refresh |
| AUT-P12-07 | Lead converts to a customer | Publish the conversion, trigger commission calculation in M53, and show the attribution chain | Conversion visible; commission on next cycle |
| AUT-P12-08 | Commission calculated | Publish it with basis, rate, qualifying revenue and rule version, and add it to the statement | Publish on next cycle |
| AUT-P12-09 | Commission adjusted or clawed back | Show the reason and the originating transaction, and notify the partner **before** the next payout | Notify; adjustment visible |
| AUT-P12-10 | Payout schedule due | Execute per M53 and publish the remittance reference | Retry; status visible |
| AUT-P12-11 | Bank detail change submitted | Hold for out-of-band verification, notify Finance, and exclude from the next payout run | Hold indefinitely rather than apply |
| AUT-P12-12 | Partner inactive for the configured period | Mark dormant, notify the partner and the account owner, and offer re-engagement material | Report only |
| AUT-P12-13 | Benefit schedule changes | Notify affected alliance partners with the effective date and the previous version retained | Notify; both versions retrievable |
| AUT-P12-14 | Reseller order placed beyond allocation | Refuse with the available allocation stated | Hard refusal, not a queued order |
| AUT-P12-15 | Co-branded campaign requested | Route to M35 for approval and show the partner its progress and outcome | Request held; partner informed |
| AUT-P12-16 | Partner offboarded | Close the transaction gate, retain attribution for the agreed window, and settle after it elapses | Manual settlement |

---

## 12. Module Interfaces

### 12.1 Modules P12 Consumes

| Module | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, MFA on financial actions, partner scoping | OIDC via gateway |
| M28 Integration Platform | Every call; per-partner rate limits | Gateway |
| **M40 Partner, Channel, Alliance & Franchise** | Partner record, type, tier, agreement, programme terms, referral scheme, approval | REST + events |
| **M07 CRM** | Lead creation, qualification, opportunity, conversion, loss reason, conflict detection | REST + events |
| **M53 Revenue, Commission & Settlement** | Commission calculation, statements, payout, adjustments | REST + events |
| M10 Loyalty | Benefit schedule, referral codes, voucher performance | REST |
| M35 Marketing & Campaigns | Approved material, co-branded campaign approval, campaign performance | REST |
| M14 / M15 / M11 | Refurbished stock allocation, availability and agreed pricing | REST |
| M38 / M03 | Reseller order placement and fulfilment tracking | REST |
| M33 Party Master | Partner identity; submitted lead contacts | REST |
| M24 Documents | Application documents, agreements, marketing material | REST |
| M25 BI | Partner-scoped performance analytics | Embedded, scoped |
| M65 Localisation | Bengali and English bundles | Build-time + REST |

### 12.2 What P12 Writes Back

| Target | What | Mechanism |
|---|---|---|
| M40 | Application, profile, partner user management, co-branding requests | Command |
| **M07** | **Lead submissions with recorded consent; deal registrations** | Command |
| M53 | Payout requests | Command (MFA-gated) |
| M10 | Referral code generation and retirement within the scheme | Command |
| M35 | Co-branded campaign requests | Command |
| M38 | Reseller orders against allocation | Command (MFA-gated) |
| M33 | Partner contact maintenance | Command |
| M24 | Application document uploads | Upload |
| M25 / M62 | Adoption, referral volume, conversion and payout analytics | Event stream |

### 12.3 Events P12 Consumes

| Event | Source | Effect in P12 |
|---|---|---|
| `partner.approved` / `partner.declined` | M40 | Advance or close the application |
| `deal_registration.decided` | M40 / M07 | Publish protection or decline with reason |
| `lead.status_changed` | M07 | Update the partner's lead view |
| `lead.converted` | M07 | Publish conversion; trigger the attribution view |
| `commission.calculated` | M53 | Publish with basis, rate and rule version |
| `commission.adjusted` | M53 | Publish the reason and originating transaction |
| `payout.executed` | M53 | Publish the remittance reference |
| `benefit_schedule.changed` | M10 / M40 | Notify affected alliance partners |
| `allocation.changed` | M14 / M15 | Update the reseller's available allocation |
| `campaign.approved` / `campaign.performance_published` | M35 | Update the co-marketing view |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P12-01 | bKash / Nagad / bank rails | Outbound | Commission payout execution; via M53 and M50 |
| INT-P12-02 | Email and SMS | Outbound | Partner notification; via M27 |
| INT-P12-03 | 1000FiX public web platform | Inbound | Referral link landing and attribution capture into P01's booking funnel |
| INT-P12-04 | Social sharing surfaces | Outbound | Shareable referral formats with attribution preserved |

### 12.5 API Surface Consumed

| Endpoint | Method | Purpose | Owner |
|---|---|---|---|
| `/api/v1/partners/apply` | POST | Application with type declaration and documents | M40 |
| `/api/v1/partners/me` | GET/PATCH | Profile, contacts, portal users | M40 / M33 |
| `/api/v1/partners/me/referral-codes` | GET/POST/DELETE | Generate, manage and retire codes | M10 / M40 |
| `/api/v1/leads` | POST | **Direct lead submission with consent** | M07 |
| `/api/v1/leads/conflict-check` | POST | **Synchronous conflict detection** | M07 |
| `/api/v1/deal-registrations` | POST/GET | Register; read decision and protection term | M40 / M07 |
| `/api/v1/partners/me/leads` | GET | Submitted leads with status and loss reason | M07 |
| `/api/v1/partners/me/attribution` | GET | **Full chain: click → lead → opportunity → conversion → revenue → commission** | M07 / M53 |
| `/api/v1/partners/me/commission` | GET | Commission with basis, rate and rule version | M53 |
| `/api/v1/partners/me/statements` | GET | Period statements | M53 |
| `/api/v1/partners/me/payouts` | POST/GET | Request payout; history and remittance | M53 |
| `/api/v1/partners/me/benefits` | GET | Benefit schedule and aggregate redemption | M10 |
| `/api/v1/partners/me/materials` | GET | Approved co-marketing material | M35 |
| `/api/v1/partners/me/campaigns` | POST/GET | Co-branded campaign request and performance | M35 |
| `/api/v1/partners/me/allocation` | GET | Reseller refurbished stock allocation and pricing | M14 / M11 |
| `/api/v1/partners/me/orders` | POST/GET | Reseller orders and fulfilment tracking | M38 |
| `/api/v1/partners/me/performance` | GET | Leads, conversion, revenue, ranking | M25 |

---

## 13. Roles & Permissions

**Per `05-04` §2, P12 access is held by R23 Marketing Manager and R38 External Party only.**

| Role | Access | Scope | MFA |
|---|---|---|---|
| **R38 — Referral partner** | C R | Own referral codes, leads, attribution, commission, statements, payouts | **Required for financial actions** |
| **R38 — Alliance partner** | C R | As above, plus benefit schedule, co-marketing material and campaign requests | Required for financial actions |
| **R38 — Corporate reseller** | C R U | As referral, plus allocation, ordering, fulfilment and settlement | **Required for orders and payouts** |
| Partner administrator (sub-user) | C R U | Manage the partner organisation's own portal users | Required |
| **R23 Marketing Manager** | R U A | **All partners** — programme oversight, material publication, campaign approval |

> **Internal roles governing the programme act in P03**, not P12: R23 Marketing Manager
> (programme and material), R21 Sales Manager (deal registration review), R26 Finance Manager
> (commission and payout), R25 Retail/Refurbishment Officer (reseller allocation). **No
> impersonation path into P12 exists.**

**Field-level restrictions — the defining control.** A partner sees **only the leads they
submitted and the customers those became**, at the level of detail the customer consented to.
Absent from every P12 payload: the Company's customer base, any customer not originating from
that partner, 1000FiX internal cost and margin, another partner's leads, commission, ranking
detail or allocation, and `commission_rate` for any scheme other than the partner's own
(`05-04` §5).

**Segregation of duties.** The sales manager who reviews and approves a deal registration does
not approve the commission payout arising from it — mirroring the SOD-06 pattern applied to
marketplace sellers in `05-04` §6.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Active referral partners** | Partners with qualifying activity in the period — the `04-00` > 200 KPI | M40, M25 |
| **Referral-attributed new customers** | Share of new customers originating from a partner — the `04-00` > 12% KPI | M07, M25 |
| **Commission accuracy** | Commissions recalculated on audit versus as published — the `04-00` 100% KPI | M53, CFO |
| **Partner portal adoption** | Approved partners active in the portal — the `04-00` > 75% KPI | M40, M25 |
| Onboarding funnel | Applied, documents complete, approved, agreement executed, first referral | M40 |
| Referral funnel | Code shared, click, lead, qualified, opportunity, converted — by partner and channel | M07, M35 |
| Deal registration | Registrations submitted, reviewed within the period, protected, declined | M07, M40 |
| Conflict detection outcomes | Conflicts found at submission — the measure of channel friction prevented | M07 |
| Attribution disputes | Partners querying a commission, and the outcome | M53, CCO |
| Payout timeliness | Requested to received, by partner | M53 |
| Benefit uptake | Enrolment and redemption by alliance partner, aggregated | M10 |
| Co-marketing | Material downloaded, campaigns requested, approved and performed | M35 |
| Reseller channel | Allocation offered, ordered, fulfilled, settled | M14, M38 |
| Partner dormancy | Partners becoming dormant, and re-engagement success | M40 |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W8 Target | W9 Target |
|---|---|---|---|---|
| — | **Active referral partners** | unmeasured | **> 200 by end of W8** | > 300 |
| — | **Referral-attributed new customers** | unmeasured | **> 12% of new customers** | > 16% |
| — | **Partner commission accuracy** | unmeasured | **100%** | **100%** |
| — | **Partner portal adoption** | 0% | **> 75% of approved partners** | > 85% |
| — | Partner onboarding completion rate | n/a | > 65% | > 72% |
| — | Deal registrations reviewed within the stated period | n/a | 95% | **100%** |
| — | Deal registrations left unanswered | n/a | **0** | **0** |
| — | Leads with recorded customer consent | n/a | **100%** | **100%** |
| — | Referral lead conversion rate | unmeasured | baselined | **above the non-referral baseline** |
| — | Commissions paid on the published schedule | n/a | 96% | **99.5%** |
| — | Commission disputes per 100 payments | n/a | < 4 | **< 1** |
| — | Reseller allocation converted to orders | n/a | 55% | **> 70%** |
| — | Partners becoming dormant per quarter | n/a | baselined | **falling trend** |
| — | Bengali and English completeness | n/a | **100%** | **100%** |
| — | Cross-partner or customer-base data exposures | n/a | **0** | **0** |

> **Register note.** The first four metrics are adopted verbatim from `04-00` §P12. P12 has
> **no KPI-0nn identifiers allocated**; all fifteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action.
>
> **Wave note.** P12 lands in W7 (Months 27–30), so its targets are stated at W8 and W9.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L5 | **Next.js 15 application** — onboarding, referral and lead submission, deal registration, attribution and commission, benefits, co-marketing, reseller allocation and ordering, performance | 74% |
| L4 | Shared design system; embedded partner-scoped analytics from P06 | 12% |
| L2 | OCA `portal` and `dms` for document serving and material distribution | 8% |
| L1 | Odoo `portal` authentication and document routes | 6% |

> P12 is the smallest and simplest portal in the suite, and deliberately so. It reuses the
> design system, the analytics embed and the external-party authentication pattern established
> by P04, P05, P07 and P08. Building it as a distinct product would not be justified for
> 100–500 partners.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-213** | `p12_partner_portal` — application with type declaration and transaction gate, referral link and code generation and sharing, **direct lead submission with consent capture and synchronous conflict detection**, **deal registration with a review clock and protection term**, attribution chain display, commission with basis and rule version, statements, payout with MFA and bank-change control, benefit schedule and aggregate redemption, co-marketing material and campaign request, reseller allocation and ordering, performance and ranking | Next.js 15 application | 14 PW |

> **CD register.** One ID, **CD-213**, claimed following CD-212 (P11). **CD-214 is the next
> free ID.** All CD IDs remain provisional pending the unified CD register required by audit
> finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M40 Partner, Channel, Alliance & Franchise** | The partner record, programme, tiers and referral scheme. **W7 — the binding constraint** |
| **M07 CRM** | Lead, opportunity, conversion and conflict detection. **W1 — available well ahead** |
| **M53 Revenue, Commission & Settlement** | Commission calculation and payout. **W4/W7** |
| M29 Identity & Security | Partner identity and MFA on financial actions |
| M28 Integration Platform | Gateway with per-partner credentials |
| M10 Loyalty | Referral codes and benefit schedule (W2) |
| M35 Marketing & Campaigns | Approved material and co-branded campaign approval (W5) |
| M14 / M15 / M11 | Refurbished stock allocation and pricing (W6) — **the reseller surface follows M14** |
| M38 E-Commerce | Reseller order placement and fulfilment (W7) |
| M24 Documents | Agreements and material with retention |
| M25 / M62 | Partner-scoped performance analytics (W4) |

**Phasing within the portal.** W7 ships onboarding, referral, lead submission, deal
registration, attribution, commission and payout, benefits and performance. The reseller
allocation and ordering surface ships in the same wave, dependent on M14 and M38 being live.

### 16.4 Partner Onboarding

| Stage | Scope | Wave |
|---|---|---|
| Existing alliance partners | Migrated from the current Partner Alliance Program, personally onboarded | W7, month 28 |
| Referral partner recruitment | Corporate contacts, IT resellers, property managers, service adjacencies | W7–W8 |
| Reseller channel | Selected corporate resellers for refurbished stock | W7, with M14 volume |
| Scale | Toward 200 active referral partners by end of W8 | W8 |

> **Onboarding position.** Existing Partner Alliance Program members are onboarded first and
> personally, because they already have a relationship the portal must not disrupt. Their
> historical arrangements — informal benefit promises, verbal commission understandings — must
> be captured in the agreement before the portal makes those terms explicit and enforceable.
> Discovering an undocumented promise after go-live is a partner relationship damaged by the
> system meant to strengthen it.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **A partner cannot access any customer data beyond the leads they submitted and the customers those became**, through any path including export and API | **Tenant-isolation penetration test — the portal's highest-severity control** |
| AC-02 | A partner cannot access another partner's leads, commission, ranking detail or allocation | Isolation test across three partner accounts |
| AC-03 | A partner sees only the surfaces their approved type entitles them to | Negative test across all three types |
| AC-04 | A partner cannot generate links, submit leads or place orders until verified, agreement-executed and approved | Negative test at every transactional endpoint |
| AC-05 | A directly submitted lead cannot be accepted without recorded customer consent, with timestamp and wording version | Negative test |
| AC-06 | Conflict detection runs synchronously at submission and returns its result before submission completes | Scripted conflict scenario |
| AC-07 | A deal registration is reviewed within the stated period; an unreviewed registration escalates and never expires silently | Scripted scenario with clock manipulation |
| AC-08 | Every commission displays its full attribution chain from click or lead to revenue | Attribution audit across 50 commissions |
| AC-09 | Every commission records the rule version that governed it, and a rate change does not alter a calculated commission | Scripted rate change with historical commissions |
| AC-10 | Commission recalculated on audit matches the published figure in 100% of cases | Independent recalculation of one full period |
| AC-11 | A commission adjustment or clawback displays its reason and originating transaction, and the partner is notified before the next payout | Scripted clawback scenario |
| AC-12 | MFA is enforced for payout request, bank change and reseller order placement | Authentication test per action |
| AC-13 | A payout bank change is held for out-of-band verification and excluded from the next payout run | Scripted scenario with M53 |
| AC-14 | A retired referral code attributes nothing from the moment of retirement | Negative test |
| AC-15 | A reseller order beyond allocation is refused with the available allocation stated, not queued | Negative test |
| AC-16 | Benefit redemption is reported in aggregate with no individual member identifiable | Payload inspection |
| AC-17 | No P12 payload contains 1000FiX internal cost, margin or another partner's data | Automated payload inspection across every endpoint |
| AC-18 | Every screen and shareable template renders in Bengali and English | Translation coverage report |
| AC-19 | WCAG 2.1 AA, usable from 320 px upward | Automated scan plus manual audit |
| AC-20 | Active referral partners exceed 200 and referral-attributed new customers exceed 12% | Six consecutive monthly reports |
| AC-21 | CCO, Marketing Manager, Finance Manager and three partners sign off UAT | Signed UAT record |

**Definition of done:** the twelve cross-portal standards in `04-00` §3 plus the 21 criteria
above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | How many partners exist in the current Partner Alliance Program, on what terms, and are those terms documented? Undocumented historical promises are the largest migration risk here | CCO / Marketing Manager | **W7 minus 4 months** |
| Q-02 | What commission rates apply by partner type, referral category and revenue basis, and are they published to partners? | CCO / CFO | **W7 design** |
| Q-03 | What is the deal registration review period and the protection term? | CCO / Sales Manager | **W7 design** |
| Q-04 | What is the attribution window — how long after a click or lead does a conversion still attribute? | CCO / CFO | **W7 design** |
| Q-05 | Is customer consent at lead submission legally sufficient under Bangladesh data-protection expectations, and what wording does Legal require? | Legal / CCO | **W7 minus 3 months** |
| Q-06 | How is channel conflict resolved when a partner-registered account is already being pursued by the Company's own sales team? | CCO / Sales Manager | W7 design |
| Q-07 | Is commission clawed back on refund, cancellation or non-payment, and over what period? | CFO | W7 design |
| Q-08 | Is partner commission subject to tax withholding under Bangladesh rules, and at what rate? *(Matches P07 Q-09 — one answer should serve both)* | CFO / Legal | **W7 design** |
| Q-09 | Which corporate resellers are targeted for refurbished stock, and does M14's output volume support the channel? | Retail Operations Head / CCO | W7 minus 3 months |
| Q-10 | What benefit schedule may an alliance partner extend, and who approves a variation? | CCO / Marketing Manager | W7 design |
| Q-11 | Is there overlap between marketplace sellers (P07) and partners (P12) — can one organisation be both, and how is that presented? | CCO | **W7 design** |
| Q-12 | Do partners work predominantly in Bengali or English, and does that differ by partner type? | CCO / Marketing Manager | W7 design |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §P12, §1, §3 PS-01…PS-12, §4 ·
`P01_Customer_Self_Service_Portal_and_Mobile_Application.md` §5.6 FR-POR-036 (retail referral —
the boundary with P12) ·
`P04_Corporate_B2B_Portal.md` (boundary: client versus reseller) ·
`P05_Vendor_and_Supplier_Portal.md` (boundary: supplier versus partner) ·
`P07_Marketplace_Seller_Portal_and_Application.md` (boundary: seller performs, partner
introduces; shared MFA and bank-change patterns) ·
`P03_Admin_Operations_Portal.md` (internal partner governance) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md`
§1 (R23, R38), §2, §5 (`commission_rate`), §6 SOD-06 pattern, §8 ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §6.2
(BDT 65 lac refurbishment, BDT 78 lac retention)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-CRM-006, BR-CRM-010,
BR-FIN-013 ·
`1000FiX_Services_Company_Profile.md` **§Partner Alliance Program**, §Privileged Program,
§Exchange Offer

**External benchmark**
[PRM software and partner portal features — deal registration, MDF, incentives, co-branding and analytics](https://www.magentrix.com/features/prm-partner-relationship-management) ·
[What is PRM — portals, onboarding, deal registration, incentives and analytics in one platform](https://www.magentrix.com/glossary/prm) ·
[Partner relationship management — deal registration with channel-conflict protection](https://www.channeltivity.com/partner-relationship-management/) ·
[PRM software definition and capability set](https://www.zinfi.com/glossary/what-is-prm-software/) ·
[Best PRM software 2026 — referral capture, commission tracking and co-branded content](https://www.guideflow.com/blog/best-prm-software) ·
[PRM platforms compared — partner-sourced pipeline and deal registration conversion analytics](https://xamplify.com/the-ultimate-guide-to-partner-relationship-management-prm-software-in-2026/) ·
[Partner relationship management software guide](https://www.mindmatrix.net/partner-relationship-management-software/)

---

*Portal P12 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
