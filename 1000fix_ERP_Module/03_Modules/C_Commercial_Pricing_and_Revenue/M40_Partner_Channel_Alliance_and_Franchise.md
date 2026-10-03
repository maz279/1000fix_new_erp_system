---
id: FIX-ERP2-M40
module_id: M40
module_code: PCM
module_name: Partner, Channel, Alliance & Franchise
category: C — Commercial, Pricing & Revenue
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Commercial Squad
priority: P2
wave: W7
---

# M40 — Partner, Channel, Alliance & Franchise
### Category C · Code `PCM` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M40 |
| **Module code** | `PCM` |
| **Category** | C — Commercial, Pricing & Revenue |
| **Status** | ★ New — created in v2.1 after benchmarking identified that no module owned non-seller external commercial relationships |
| **Priority** | **P2** |
| **Delivery wave** | W7 (Months 27–30) |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Commercial Squad |
| **Delivery layers** | L2 (OCA `partner_*`, `crm_*`, `agreement`) + L4 (P12 partner portal) + L5 (custom) |
| **Custom modules** | `cd_partner_program`, `cd_referral`, `cd_deal_registration`, `cd_partner_performance`, `cd_franchise` |
| **Requirement range** | FR-PCM-001 … FR-PCM-042 |
| **Requirement count** | **42** *(measured; register estimate 30)* |
| **Effort estimate** | **20 person-weeks** *(measured; register estimate 16 PW)* |
| **Depends on** | M33 Party Master · M08 Contract · M11 Pricing · M07 CRM · M53 Revenue & Settlement · M24 Document · M29 Identity · M28 Integration |
| **Depended on by** | M07, M09, M10, M14, M20, M53, M35, M25, M12, M23 · Portal **P12** |

---

## 2. Purpose

M40 owns every **external commercial relationship that is not a customer, not a supplier and not
a marketplace seller**.

That is a larger and more valuable set than it first appears:

- The **17+ brand partners** whose authorisations are the foundation of the entire business
- **Alliance partners** — insurers, telecom operators, banks, corporate benefit schemes,
  retailers — who bring volume through their own customer bases
- **Referral partners** who send individual leads for a commission
- **Resellers and corporate resellers** who buy refurbished stock or services to sell on
- **Franchise branches**, where the business plan's expansion depends on a model that is not
  owned-branch

Each of these is a relationship with a lifecycle: recruit, qualify, agree, enable, transact,
measure, reward, renew or exit. Today none of them has a system. Brand partner relationships live
in the Finance Director's inbox; referrals are informal; franchise is a plan on paper.

M40 does not own the *agreement* (M08) or the *money* (M53). It owns the **relationship, the
programme, the enablement and the performance** — and the P12 portal through which partners
transact.

### Why It Exists

Two pressures created this module.

First, **brand partner relationships are managed nowhere**. M09 processes their claims; M11
holds their rates; M08 will hold their agreements. But nobody owns the relationship: who the
contacts are, when the authorisation expires, what audits are due, how 1000FiX is performing
against their expectations, and which brands are at risk. Losing an authorisation is an
existential event for a business built on being an authorised service centre, and it happens
through neglect, not through a decision.

Second, the business plan commits to **referral and alliance channels** and to **franchise
expansion**, and the portal suite already specifies P12 with a target of **200 active referral
partners** contributing **12% of new customers**. Neither can operate without a system for deal
registration, attribution and commission.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Company Profile §Brand Partnerships | 17+ authorised brand partners with authorisation terms and audit rights |
| Business Plan §Expansion Strategy, §Franchise | Franchise branches as an expansion route distinct from owned branches |
| Business Plan §Alliance & Referral | Corporate benefit schemes, insurer and telecom partnerships as demand channels |
| `04-00` P12 Partner & Referral Portal | Onboarding, referral links, lead submission, benefits, earnings, co-marketing, reseller allocation, performance — with KPIs of > 200 active partners and > 12% referral-attributed new customers |
| `05-04` §1.7 R38 | External party class including brand partner, referral partner and recycling partner |
| `_CATEGORY_OVERVIEW.md` §2, §5 | Registers M40 and assigns it brand partner, alliance and franchise relationships, explicitly *not* M12 or M42 |
| `02-02` §2 Category C | Registers M40 as ★ new, P2, W7, CCO-owned |
| M09 §5.5 FR-WTY-061 | Brand partner performance measurement, consumed by M40 for relationship management |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The partner master: partner types, programmes, tiers, standing and lifecycle |
| 2 | Partner recruitment, application, qualification and approval |
| 3 | Partner onboarding: documents, agreement execution (via M08), enablement, portal provisioning |
| 4 | **Brand partner relationship management**: contacts, authorisation scope, expiry, audit calendar, escalation path, relationship health |
| 5 | Authorisation and certification tracking per brand, including the technicians authorised on each |
| 6 | **Alliance partner management**: scheme definition, member eligibility, benefit schedule, volume commitments |
| 7 | **Referral partner management**: referral links and codes, lead submission, attribution, conversion tracking |
| 8 | **Deal registration**: registering an opportunity to a partner, conflict detection, protection period, approval |
| 9 | **Reseller management**: allocation of refurbished stock and services, reseller pricing, order fulfilment |
| 10 | **Franchise management**: franchisee lifecycle, territory, fees and royalties, brand standards, compliance audits |
| 11 | Partner commercial terms: commission schemes, rebates, discounts, MDF and co-op funds *(rates held in M11, computed by M53)* |
| 12 | Partner enablement: training, certification, collateral, product updates, policy acknowledgement |
| 13 | Co-marketing: approved materials, co-branded campaign requests, MDF claims and approval |
| 14 | Partner performance: attributed revenue, conversion, quality, compliance, ranking and tier movement |
| 15 | Partner communication: bulletins, notices, mandatory acknowledgements |
| 16 | Partner health and risk: relationship health scoring, at-risk detection, renewal and exit management |
| 17 | Channel conflict management between partners, marketplace sellers and direct sales |
| 18 | The P12 Partner & Referral Portal domain logic |
| 19 | Partner analytics: channel contribution, partner cohort economics, programme ROI |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Marketplace sellers — onboarding, listings, jobs, ratings, disputes, payouts | **M12** Marketplace | A seller supplies capacity on a platform; a partner brings demand or represents the brand. Different lifecycle, different economics *(category boundary map)* |
| Suppliers and vendor commercial relationships | **M42** Supplier Relationship (Category E) | Buy-side relationships |
| The legal agreement instance, its terms, obligations and renewal | **M08** Contract | M40 manages the relationship; M08 holds the agreement |
| Commission and rebate **calculation and payout execution** | **M53** Revenue & Settlement | M40 defines the programme; M53 computes and pays |
| Commission **rates** | **M11** Pricing | Rates are commercial pricing decisions |
| Warranty claim processing with brand partners | **M09** Warranty | M09 runs claims; M40 runs the relationship they occur within |
| Brand reimbursement rate cards | **M11** Pricing | Held with all other rates |
| Party identity, contacts, addresses, banking | **M33** Party Master | Referenced, never mastered |
| Opportunity and pipeline management | **M07** CRM | A registered deal becomes an M07 opportunity |
| Loyalty and customer referral by *customers* | **M10** Loyalty | Customer-to-customer referral is a loyalty mechanic |
| Campaign execution and marketing automation | **M35** Marketing | M40 approves and funds co-marketing; M35 executes |
| Employee franchise-branch staff, payroll and HR | **M21** / **M56** | Franchise staff are the franchisee's employees |
| Franchise branch operations, service delivery and inventory | **M04** / **M01** / **M15** | A franchise branch operates the same operational modules as an owned branch |
| Invoice, receivable and payable posting | **M20** / **M52** | Only Category G creates financial documents |

### 3.3 Shared Concepts

| Concept | M40's Role | Owning Module |
|---|---|---|
| Partner | **Owner** of the programme profile; M33 owns the party | M40 (profile) / M33 (party) |
| Partner agreement | References; M08 holds the instance | M08 |
| Brand authorisation | **Owner** of scope, expiry and audit tracking | M40 |
| Brand claim performance | Consumes M09's scorecard for relationship management | M09 |
| Commission scheme | **Owner** of the programme design; M11 holds rates, M53 computes | M40 / M11 / M53 |
| Referral lead | **Owner** until conversion; M07 owns the opportunity | M40 → M07 |
| Deal registration | **Owner** | M40 |
| MDF / co-op fund | **Owner** of allocation and claim approval; M52 pays | M40 |
| Franchise territory and standards | **Owner** | M40 |
| Reseller stock allocation | **Owner** of the allocation; M14/M15 hold the goods | M40 |
| Channel conflict | **Owner** of the rules | M40 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **PRM platforms** (ZINFI, Impartner, Channeltivity, Mindmatrix, xAmplify class) | The six defining functions: recruitment, onboarding, deal registration, incentives and MDF, co-marketing, performance analytics; plus a secure partner portal with role-based access and partner training | **All six functions**, and specifically **deal registration with approval and conflict detection**, **MDF management with claim approval**, and **certification-gated programme tiers**. These are mature, well-understood patterns and there is no reason to invent alternatives | Through-channel marketing automation (TCMA) at full depth — M35 covers campaign execution; and AI partner-engagement scoring, which needs data we will not have for two years |
| **Salesforce PRM / Oracle Partner Management** | Partner accounts, partner users, deal registration, lead distribution, partner scorecards, tiering | The **partner-user model layered on the party master** — a partner is an account with scoped users, not a separate identity domain | Their CRM-platform coupling |
| **SAP / IFS channel management** | Channel partner agreements, rebates, authorisation tracking | **Authorisation scope and expiry tracking as first-class objects**, which is exactly what brand partner management needs | Full rebate settlement — M53 owns it |
| **Franchise management systems** (FranConnect class) | Franchisee lifecycle, territory, royalty and fee collection, brand standards audits, field visit reports, performance benchmarking | **Territory definition, royalty schedules, brand-standards audit and franchisee benchmarking** — adopted wholesale, because franchise is a distinct discipline and the business plan commits to it | A separate franchise product; the volume does not justify it and the operational modules are shared with owned branches |
| **Insurance and telco alliance practice** | Scheme-based benefit entitlement for a partner's member base, volume commitments, co-branded servicing | **Scheme-based member eligibility** — an insurer's policyholders or a telco's subscribers receive defined benefits without each being a contracted customer | — |
| **Odoo 19 + OCA** — `partner_*`, `crm_lead`, `agreement`, `commission` families | Partner records, lead source attribution, agreement records, commission rules | The **party and agreement base** and lead-source attribution as the L2 foundation | Odoo's assumption that a partner is simply a contact with a tag; programme, tier, authorisation and territory need real structure |

**Design position.** 1000FiX differs from the PRM benchmark in four ways.

First, **the highest-value partner relationship is inbound, not outbound**. Standard PRM assumes
partners sell *your* product. Here, the most important partners — the 17+ brands — *authorise*
1000FiX to service theirs. The relationship runs the other way: 1000FiX is the partner being
measured. M40 therefore models **relationship health from both directions**, including how the
brand rates 1000FiX, and treats **authorisation expiry as a critical-path event** with the same
seriousness a sales organisation gives to a renewal.

Second, **one module holds five relationship types that PRM products usually split**. Brand,
alliance, referral, reseller and franchise share a common spine — programme, tier, agreement,
enablement, performance, portal — with typed extensions for what differs. This is the same
pattern M37 uses for catalogue items, and it exists for the same reason: the business will add
relationship types faster than a release cycle.

Third, **channel conflict is a designed control, not an afterthought**. With direct sales, a
marketplace, referral partners, resellers and franchise branches all touching the same market,
conflict is certain. Deal registration with a protection period, territory rules for franchise,
and explicit precedence between channels are built in from the start.

Fourth, **franchise is treated as a relationship, not a branch type**. A franchise branch uses
the same M01, M04 and M15 as an owned branch — that is the point of a single ERP. What differs is
the *relationship*: territory, fees, royalties, standards, audits and exit. Putting franchise
economics into the branch modules would corrupt them; putting it here keeps operations uniform.

---

## 5. Functional Areas & Features

### 5.1 Partner Master, Programme & Lifecycle

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PCM-001 | Partner master | Maintain a partner record for each external commercial relationship, typed as brand, alliance, referral, reseller or franchise, layered on the M33 party | P0 | L5 |
| FR-PCM-002 | Typed extensions | Hold type-specific attributes in typed extensions so a new relationship type is configuration, not code | P0 | L5 |
| FR-PCM-003 | Programme definition | Define partner programmes with entry criteria, tiers, benefits, obligations, commercial terms and exit conditions | P0 | L5 |
| FR-PCM-004 | Tiering | Assign and move partners between tiers automatically on declared criteria, with notice and effective dating | P1 | L5 |
| FR-PCM-005 | Recruitment and application | Accept partner applications through P12 or by referral, with a staged, resumable, bilingual flow | P1 | L5 |
| FR-PCM-006 | Qualification and approval | Qualify applicants against programme criteria and route for approval, with recorded reasons | P1 | L5 |
| FR-PCM-007 | Onboarding checklist | Drive onboarding through a programme-specific checklist — documents, agreement, training, portal access, banking, tax registration | P1 | L5 |
| FR-PCM-008 | Agreement linkage | Request and link the partner agreement in M08, and block transacting until it is executed | P0 | L5 |
| FR-PCM-009 | Partner contacts and roles | Maintain named contacts with roles — commercial, technical, finance, escalation — and their portal scope | P0 | L5 |
| FR-PCM-010 | Partner standing | Maintain standing (active, probation, suspended, dormant, exiting, exited) with the consequences of each | P0 | L5 |
| FR-PCM-011 | Renewal and exit | Manage relationship renewal at the M08 lead time, and manage exit with obligation settlement and access revocation | P1 | L5 |
| FR-PCM-012 | Partner hierarchy | Model partner groups, parent–subsidiary relationships and multi-entity partners | P2 | L5 |

### 5.2 Brand Partner Relationship

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PCM-013 | Authorisation register | Record each brand authorisation: scope by product category and repair level, territory, effective and expiry dates, conditions and the authorising document | P0 | L5 |
| FR-PCM-014 | Authorisation expiry management | Alert at declared intervals before expiry, drive the renewal process, and escalate as the date approaches | P0 | L5 |
| FR-PCM-015 | Authorised technician register | Track which technicians are certified on which brand, sourced from M22, and report coverage and gaps against authorisation conditions | P0 | L5 |
| FR-PCM-016 | Brand audit calendar | Schedule and track brand partner audits, their scope, findings, responses and closure, integrating with M23 | P1 | L5 |
| FR-PCM-017 | Brand obligation tracking | Track obligations under the authorisation — tooling, training, facility standards, reporting, stock holding — with evidence and due dates | P1 | L5 |
| FR-PCM-018 | Relationship health score | Compute a health score per brand from claim performance (M09), quality (M23), audit findings, obligation compliance, volume trend and contact engagement | P1 | L5 |
| FR-PCM-019 | At-risk detection and escalation | Detect deteriorating brand relationships and escalate to the CCO and CEO with the contributing factors | P1 | L5 |
| FR-PCM-020 | Brand engagement log | Record meetings, bulletins, technical notices, escalations and commitments made in both directions | P2 | L5 |
| FR-PCM-021 | Brand performance exchange | Present 1000FiX's performance on the brand (from M09/M23) and record the brand's own assessment | P1 | L5 |

### 5.3 Referral, Alliance & Deal Registration

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PCM-022 | Referral links and codes | Generate unique, trackable referral links and codes per partner and per campaign | P0 | L5 |
| FR-PCM-023 | Lead submission | Accept leads submitted directly through P12 with customer consent captured, and by link attribution | P0 | L5 |
| FR-PCM-024 | Attribution model | Attribute a converted customer or job to a partner under a declared attribution model with a defined attribution window | P0 | L5 |
| FR-PCM-025 | Lead-to-opportunity handoff | Create the M07 opportunity from a qualified partner lead, preserving attribution through to revenue | P1 | L5 |
| FR-PCM-026 | Lead status visibility | Show the partner the status of every lead they submitted, from receipt to conversion or loss, with reasons | P1 | L5 |
| FR-PCM-027 | Deal registration | Allow a partner to register an opportunity, detect conflicts with existing pipeline and other partners, and approve or refuse with a reason | P1 | L5 |
| FR-PCM-028 | Deal protection period | Grant a time-boxed protection period on an approved registration, with declared renewal and lapse rules | P1 | L5 |
| FR-PCM-029 | Channel conflict rules | Apply declared precedence between direct sales, partners, resellers, franchise territories and the marketplace, and surface conflicts for decision | P1 | L5 |
| FR-PCM-030 | Alliance scheme definition | Define an alliance scheme: the partner's member base, eligibility rules, benefit schedule, volume commitments and validation method | P1 | L5 |
| FR-PCM-031 | Member eligibility validation | Validate at service intake whether a customer qualifies under an alliance scheme, and apply the benefit through M11 | P1 | L5 |
| FR-PCM-032 | Volume commitment tracking | Track a partner's actual volume against any committed volume, and report shortfall and over-performance | P2 | L5 |

### 5.4 Reseller, Franchise & Co-Marketing

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PCM-033 | Reseller allocation | Allocate refurbished stock and service capacity to resellers, with visibility of their allocation and its status | P2 | L5 |
| FR-PCM-034 | Reseller ordering and settlement | Let a reseller order against allocation and agreed pricing through P12, settling per the programme terms | P2 | L5 |
| FR-PCM-035 | Franchise territory | Define franchise territories with exclusivity rules, and detect and prevent cross-territory conflict | P2 | L5 |
| FR-PCM-036 | Franchise fees and royalties | Define initial fees, ongoing royalties and marketing levies, computing the amounts due and instructing M20/M53 | P2 | L5 |
| FR-PCM-037 | Franchise brand standards | Maintain the brand-standards manual, track franchisee acknowledgement, and schedule standards audits through M23/P11 | P2 | L5 |
| FR-PCM-038 | Franchise performance benchmarking | Benchmark franchise branches against owned branches and each other on operational and financial measures | P2 | L5 |
| FR-PCM-039 | MDF and co-op funds | Allocate marketing development funds, accept claims with evidence, approve or refuse, and instruct payment | P2 | L5 |
| FR-PCM-040 | Co-marketing materials and requests | Publish approved marketing materials, accept co-branded campaign requests, route for approval and hand execution to M35 | P2 | L5 |
| FR-PCM-041 | Partner enablement and certification | Assign training, track completion and certification, and gate programme benefits on it | P1 | L5 |
| FR-PCM-042 | Partner analytics | Report attributed revenue, conversion, partner cohort economics, programme ROI and channel contribution | P0 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Typed partner model** | One partner spine with typed extensions; a new relationship type is configuration, verified by an acceptance test that instantiates all five types |
| T-02 | **Attribution durability** | Attribution is written at lead creation and carried immutably through opportunity, quotation, order and revenue, so commission is never recomputed from inference |
| T-03 | **Attribution window enforcement** | The attribution window is evaluated deterministically at conversion; a lead outside its window attributes to no partner rather than to the wrong one |
| T-04 | **Deal-registration conflict detection** | Conflict detection runs against open pipeline, other registrations and territory rules at submission, in under 2 seconds |
| T-05 | **Authorisation expiry scheduler** | Expiry and obligation dates are evaluated continuously; no brand authorisation can lapse without escalation having fired |
| T-06 | **Partner data isolation** | A partner sees only their own records; scope cannot be widened by request parameters *(EA-01, EA-11)* |
| T-07 | **Referral link integrity** | Referral links and codes are signed, revocable and non-guessable, with abuse rate-limiting |
| T-08 | **Health score explainability** | Every relationship health score decomposes into its named contributing factors with their weights |
| T-09 | **MDF fund ledger** | Fund allocation, claims and payments are an append-only ledger; balance is derived |
| T-10 | **Programme versioning** | Programme terms are versioned and effective-dated; a partner is bound to the version in force at their agreement date |
| T-11 | **Portal provisioning lifecycle** | P12 access is provisioned on approval and revoked automatically on exit, expiry or suspension, within one hour |
| T-12 | **Consent on partner-submitted leads** | A partner-submitted lead cannot be created without recorded customer consent, satisfying PDPA 2026 |
| T-13 | **Franchise data segregation** | A franchisee sees only their own territory's operational data, enforced at the record-rule layer alongside the standard branch tier |
| T-14 | **Audit completeness** | Every programme change, tier movement, registration decision, fund claim and standing change is audited with actor and reason |
| T-15 | **Performance envelope** | Partner dashboard ≤ 1.5 s p95 · attribution resolution ≤ 200 ms · conflict detection ≤ 2 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M40 |
|---|---|---|
| **Finance Director** | Manages 17+ brand relationships from an inbox; discovers an expiring authorisation late | Sees every authorisation, its expiry, its obligations and the relationship health score on one board |
| **CCO** | Has no channel other than direct and, from W7, the marketplace | Has a partner channel with measurable contribution and programme ROI |
| **Account manager** | Loses deals to a partner-introduced conflict nobody detected | Sees registered deals and territory rules before working an opportunity |
| **Quality manager** | Learns of a brand audit when the auditor arrives | Works a scheduled audit calendar with obligations tracked to evidence |
| **Marketing head** | Cannot run partner co-marketing because there is no fund or approval mechanism | Allocates MDF, approves claims and measures campaign return |
| **Referral partner** | Sends a customer and hopes to be paid | Submits a lead, tracks it to conversion and sees the commission accrue |
| **Alliance partner (insurer, telco)** | Cannot offer their members a defined 1000FiX benefit | Has a scheme with eligibility validation at intake and reporting |
| **Franchisee** | Model does not exist | Operates on the same ERP as an owned branch, with territory, royalties and standards managed |
| **CEO** | Cannot see channel mix or partner contribution | Sees contribution by channel and the risk position on brand authorisations |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Referral-attributed customer acquisition** | Trackable referral links, lead submission, attribution and commission | **> 200 active referral partners** and **> 12% of new customers referral-attributed** *(P12 KPIs)*; category target **> 200 active referral / alliance partners** |
| **Protection of brand authorisations** | Authorisation expiry management, obligation tracking, audit calendar and relationship health scoring | Protects the revenue of streams 1 and 4 in their entirety. Warranty service and warranty products depend on authorisations; losing one is not a margin event but a revenue-line event |
| **Alliance channel volume** | Scheme-based benefits for insurer, telco and corporate member bases, validated at intake | New demand at low acquisition cost; contributes to the **BDT 78 lac/year** retention and acquisition benefit |
| **Franchise expansion without capital** | A managed franchise model with territory, royalties and standards | Enables geographic expansion beyond what owned-branch capital allows; the business plan's expansion assumption depends on it |
| **Reseller channel for refurbished stock** | Allocation and reseller ordering | Adds a wholesale channel alongside M38 retail, supporting the **BDT 65 lac/year** refurbishment margin |
| **Channel conflict cost avoidance** | Deal registration, protection periods and precedence rules | Avoids the margin destruction and relationship damage of two channels competing on the same customer |
| **Partner commission accuracy** | Programme terms and attribution feeding M53 computation | **100% partner commission accuracy** *(P12 KPI)*; removes the manual commission calculation retired in W7 |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Institutional ownership of the brand relationships** | The 17+ authorisations stop depending on one executive's personal relationships and become a managed corporate asset with succession |
| **Early warning on existential risk** | A deteriorating brand relationship is visible months before an authorisation is withdrawn, when it can still be repaired |
| **Credibility with institutional partners** | Insurers, banks and telcos require a partner that can report accurately and honour a scheme mechanically. A portal and a scheme engine are entry requirements |
| **Scalable expansion model** | Franchise standards and audits make expansion repeatable rather than dependent on the founder's attention |
| **Ecosystem trust** | Partners paid accurately and on time, with visible attribution, refer more. Partners paid late or wrongly stop |
| **Governance and anti-conflict discipline** | Documented deal registration and territory rules prevent the internal disputes that poison channel programmes |
| **Data on channel economics** | The company learns which channels actually produce profitable customers — a question it currently cannot answer |

---

## 8. Lifecycle & State Model

M40 owns the **partner relationship** lifecycle, plus the **deal registration** and **MDF claim**
lifecycles.

### 8.1 Partner Relationship

```
   ┌────────────┐
   │  PROSPECT  │ identified or self-applied
   └─────┬──────┘
         │ application complete
   ┌─────▼──────────┐
   │  QUALIFYING    │──── not qualified ──► DECLINED (reason)
   └─────┬──────────┘
         │ meets programme criteria
   ┌─────▼──────────┐
   │   APPROVED     │ agreement requested in M08
   └─────┬──────────┘
         │ agreement executed; onboarding checklist complete
   ┌─────▼──────────┐
   │  ONBOARDING    │
   └─────┬──────────┘
         │ enablement and portal provisioning complete
   ┌─────▼──────────┐
   │    ACTIVE      │◄──────── reinstated
   └─────┬──────────┘
         │
   ┌─────┼──────────────┬────────────────┬─────────────────┐
   ▼     ▼              ▼                ▼                 ▼
┌──────────┐  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐
│ TIER     │  │  PROBATION  │  │   DORMANT    │  │   SUSPENDED    │
│ CHANGED  │  │ (remediation│  │ (no activity │  │ (breach or     │
│ (same    │  │  plan)      │  │  in window)  │  │  expiry lapse) │
│  state)  │  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘
└──────────┘         │                │                   │
                     └────────────────┴───────────────────┤
                                                          │
                                              ┌───────────▼──────┐
                                              │     EXITING      │
                                              │ obligations      │
                                              │ settled, access  │
                                              │ revoked          │
                                              └───────────┬──────┘
                                                          ▼
                                                  ┌───────────────┐
                                                  │    EXITED     │
                                                  └───────────────┘

  Brand partners carry an additional cross-cutting flag: AUTHORISATION AT RISK,
  which escalates independently of standing and never resolves silently.
```

### 8.2 Deal Registration

```
SUBMITTED ──► CONFLICT CHECK ──┬── conflict found ──► REVIEW ──┬── approved ──► PROTECTED
                               │                                └── refused ──► DECLINED (reason)
                               └── no conflict ──► PROTECTED
PROTECTED ──► CONVERTED (opportunity won, commission accrues)
           ──► EXPIRED (protection period lapsed)
           ──► WITHDRAWN (by the partner)
```

### 8.3 MDF Claim

```
FUND ALLOCATED ──► CLAIM SUBMITTED ──► EVIDENCE REVIEW ──┬── approved ──► PAYMENT INSTRUCTED ──► PAID
                                                          └── refused ──► CLOSED (reason, appeal right)
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Prospect | Qualifying | Application complete with mandatory documents | Partner / Partner Manager |
| Qualifying | Approved | Programme criteria met; approver holds the authority | CCO or delegate |
| Approved | Onboarding | Agreement executed in M08 | System (M08 event) |
| Onboarding | Active | Checklist complete: training, certification, banking, tax registration, portal provisioned | System |
| Active | Tier changed | Tier criteria met or lost; notice period observed | System |
| Active | Probation | Performance or compliance below threshold; remediation plan issued | Partner Manager |
| Active / Probation | Suspended | Material breach, agreement lapse, or authorisation expiry | CCO |
| Active | Dormant | No qualifying activity within the declared window | System |
| Any | Exiting | Agreement terminated, non-renewed, or voluntary exit | CCO / Partner |
| Exiting | Exited | Obligations settled; outstanding commission paid; access revoked; records retained | System |
| Submitted | Protected | Conflict check passed, or conflict reviewed and approved | System / Partner Manager |
| Protected | Converted | Linked opportunity won within the protection period | System |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-PCM-01 | A partner cannot transact until the M08 agreement is executed and onboarding is complete | **H** | CCO |
| BRU-PCM-02 | A marketplace seller is not a partner and is never managed here; M12 owns sellers | **H** | CCO |
| BRU-PCM-03 | M40 defines partner commercial programmes; M11 holds rates and M53 computes and pays | **H** | CFO |
| BRU-PCM-04 | Attribution is written at lead creation and is immutable through to revenue | **H** | CTO |
| BRU-PCM-05 | A lead converting outside its attribution window attributes to no partner | **C** | CCO |
| BRU-PCM-06 | A partner-submitted lead requires recorded customer consent before the record is created | **H** | Legal / CTO |
| BRU-PCM-07 | A brand authorisation may never lapse without escalation having fired at the declared intervals | **H** | Finance Director |
| BRU-PCM-08 | Work requiring a brand authorisation cannot be performed once that authorisation has lapsed | **H** | Quality Manager |
| BRU-PCM-09 | A deal registration is granted a protection period only after conflict check; conflicts are decided, never auto-approved | **H** | CCO |
| BRU-PCM-10 | Channel precedence rules are declared and applied consistently; ad-hoc exceptions require CCO approval | **H** | CCO |
| BRU-PCM-11 | MDF claims require evidence and approval by someone other than the allocator | **H** | CFO |
| BRU-PCM-12 | Programme terms are versioned; a partner is bound to the version in force at their agreement date | **H** | CCO |
| BRU-PCM-13 | Portal access is revoked within one hour of exit, suspension or agreement expiry | **H** | CTO |
| BRU-PCM-14 | A partner sees only their own records; never another partner's, and never 1000FiX cost or margin *(EA-01, EA-02)* | **H** | CTO |
| BRU-PCM-15 | Outstanding partner commission is settled before a relationship reaches Exited | **H** | CFO |
| BRU-PCM-16 | A franchise territory is exclusive as declared; cross-territory activity requires documented agreement | **H** | CCO |
| BRU-PCM-17 | Franchise royalties are computed from ERP-recorded revenue, not from franchisee self-declaration | **C** | CFO |
| BRU-PCM-18 | A relationship health score must decompose into its named contributing factors | **H** | CCO |
| BRU-PCM-19 | Alliance scheme benefits are applied by M11 and never configured as ad-hoc discounts | **H** | CCO |
| BRU-PCM-20 | A brand partner's own assessment of 1000FiX is recorded verbatim and is not editable by the account owner | **H** | Finance Director |

*Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.partner.profile` | `fix_partner_profile` | The partner spine | partner_id, partner_type, code, programme_id, tier_id, state, agreement_id, onboarded_at, owner_id, health_score |
| `fix.partner.programme` | `fix_partner_programme` | Programme definition | code, partner_type, version, entry_criteria_json, benefits_json, obligations_json, commercial_terms_ref, exit_conditions, valid_from |
| `fix.partner.tier` | `fix_partner_tier` | Tiers within a programme | programme_id, code, criteria_json, benefits_json, commission_ref, notice_days |
| `fix.partner.contact.role` | `fix_partner_contact_role` | Named contacts | partner_id, contact_id, role, portal_scope, primary |
| `fix.partner.onboarding` | `fix_partner_onboarding` | Onboarding checklist | partner_id, step, required, state, evidence_document_id, completed_at |
| `fix.brand.authorisation` | `fix_brand_authorisation` | Brand authorisation register | partner_id, brand_id, scope_categories, repair_levels, territory, effective_from, expires_at, conditions_json, document_id, state |
| `fix.brand.obligation` | `fix_brand_obligation` | Obligations under authorisation | authorisation_id, obligation_type, description, due_date, recurrence, owner_id, evidence_document_id, state |
| `fix.brand.audit` | `fix_brand_audit` | Brand audit calendar | partner_id, scheduled_at, scope, conducted_at, findings_ref, response_ref, closed_at, m23_ref |
| `fix.partner.health` | `fix_partner_health` | Health scoring | partner_id, period, factors_json, weights_json, score, band, trend, at_risk |
| `fix.partner.engagement` | `fix_partner_engagement` | Engagement log | partner_id, type, at, participants, summary, commitments_json, document_ids |
| `fix.referral.link` | `fix_referral_link` | Referral links and codes | partner_id, campaign_ref, code, signed_url, uses, valid_from, valid_to, state |
| `fix.partner.lead` | `fix_partner_lead` | Submitted and attributed leads | partner_id, link_id, customer_ref, consent_ref, submitted_at, state, opportunity_id, converted_at, loss_reason |
| `fix.attribution` | `fix_attribution` | Immutable attribution record | subject_type, subject_id, partner_id, model, window_days, established_at, source_ref |
| `fix.deal.registration` | `fix_deal_registration` | Deal registration | partner_id, customer_ref, description, estimated_value, submitted_at, conflict_result_json, state, protected_until, decided_by, opportunity_id |
| `fix.channel.conflict.rule` | `fix_channel_conflict_rule` | Precedence rules | scope_json, channel_precedence, territory_rule, override_role_id, valid_from |
| `fix.alliance.scheme` | `fix_alliance_scheme` | Alliance schemes | partner_id, code, member_definition_json, eligibility_method, benefit_ref, volume_commitment, valid_from, valid_to |
| `fix.alliance.eligibility.check` | `fix_alliance_eligibility_check` | Validation log | scheme_id, customer_ref, checked_at, result, evidence_ref |
| `fix.reseller.allocation` | `fix_reseller_allocation` | Reseller stock/service allocation | partner_id, item_ref, qty, period, consumed_qty, pricing_ref, state |
| `fix.franchise` | `fix_franchise` | Franchise extension | partner_id, territory_id, branch_ids, initial_fee, royalty_scheme_ref, marketing_levy, opened_at, standards_version |
| `fix.franchise.territory` | `fix_franchise_territory` | Territory definition | code, geography_json, exclusivity, partner_id, valid_from, valid_to |
| `fix.franchise.royalty` | `fix_franchise_royalty` | Computed royalties | franchise_id, period, revenue_basis, rate, amount, state, invoice_ref |
| `fix.mdf.fund` | `fix_mdf_fund` | Fund allocation ledger | partner_id, period, allocated, claimed, approved, paid, balance |
| `fix.mdf.claim` | `fix_mdf_claim` | MDF claims | fund_id, partner_id, campaign_ref, amount, evidence_document_ids, state, approved_by, payment_ref |
| `fix.partner.enablement` | `fix_partner_enablement` | Training and certification | partner_id, course_ref, required, completed_at, certification_ref, expires_at |
| `fix.partner.communication` | `fix_partner_communication` | Bulletins and acknowledgements | partner_ids, type, title, content_ref, sent_at, ack_required, ack_records_json |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.party`, contacts, banking, tax registration | M33 | Live read |
| `fix.contract` (partner agreement instance) | M08 | Live read + creation request |
| Commission and rebate rates | M11 | REST |
| Commission calculation and payout | M53 | Command + projection |
| `fix.opportunity`, pipeline | M07 | Live read + creation |
| Brand claim performance scorecard | M09 | Projection |
| Quality findings and audits | M23 | Projection + events |
| Technician brand certification | M22 | Projection |
| Refurbished stock available for allocation | M14 / M15 | Live read |
| Franchise branch operational and financial data | M04, M01, M19 | Projection |
| Campaign execution | M35 | Command |
| Document storage and e-signature | M24 | Service call |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-PCM-01 | Partner application submitted | Run qualification checks against programme criteria and create the review task | Queue for manual qualification |
| AUT-PCM-02 | Partner agreement executed in M08 | Advance to Onboarding, generate the checklist, assign enablement | Create a manual onboarding task |
| AUT-PCM-03 | Onboarding checklist complete | Activate the partner, provision P12 access with the correct scope, issue welcome communication | Alert the Partner Manager; never activate with an incomplete checklist |
| AUT-PCM-04 | Brand authorisation approaching expiry (T−180, T−90, T−30 days) | Escalate progressively to Finance Director, CCO and CEO with the obligation and audit status attached | Repeat escalation; a lapse without escalation is a defect |
| AUT-PCM-05 | Brand authorisation lapsed | Block work requiring that authorisation, notify operations and the branches affected, raise a priority incident | — |
| AUT-PCM-06 | Brand obligation due | Notify the obligation owner; escalate on the due date; block audit readiness sign-off on lapse | Escalate to Quality Manager |
| AUT-PCM-07 | Monthly health scoring cycle | Recompute health from M09 claims, M23 quality, audits, obligations, volume and engagement; publish with factor decomposition | Retry; alert on failure |
| AUT-PCM-08 | Health score enters the at-risk band | Escalate to CCO and CEO with the contributing factors and a recommended action | Repeat weekly until resolved |
| AUT-PCM-09 | Referral link used | Record the touch, establish attribution within the window, and show the partner the activity | Log; reconcile nightly |
| AUT-PCM-10 | Partner lead submitted | Validate consent, create the lead, notify sales, and confirm receipt to the partner | Reject without consent; explain to the partner |
| AUT-PCM-11 | Attributed opportunity won | Carry attribution to the revenue record and notify M53 to accrue commission | Flag for manual attribution review |
| AUT-PCM-12 | Deal registration submitted | Run conflict detection against pipeline, other registrations and territories; approve or route for review | Route to review; never auto-approve a conflict |
| AUT-PCM-13 | Deal protection period approaching expiry | Notify the partner and the account owner; lapse on expiry | Log |
| AUT-PCM-14 | Alliance member eligibility checked at intake | Validate against the scheme and return the benefit for M11 to apply | Return not-eligible with a reason; never guess |
| AUT-PCM-15 | Franchise period close | Compute royalties and levies from ERP-recorded revenue and instruct M20 to invoice | Hold; alert Finance |
| AUT-PCM-16 | MDF claim submitted | Validate against fund balance and evidence requirements, and route for approval by someone other than the allocator | Route to manual review |
| AUT-PCM-17 | Partner inactive beyond the declared window | Set Dormant, notify the partner and the owner, and start the re-engagement or exit process | Log |
| AUT-PCM-18 | Partner exit initiated | Settle outstanding commission, close open registrations, revoke portal access within one hour, retain records | Escalate to CCO; never revoke before settlement is instructed |
| AUT-PCM-19 | Tier criteria met or lost | Move tier with the declared notice, apply new benefits and commission from the effective date | Alert the Partner Manager |
| AUT-PCM-20 | Mandatory communication issued | Track acknowledgement, escalate non-acknowledgement, and restrict benefits where the programme requires it | Repeat; escalate |

---

## 12. Interfaces

### 12.1 Upstream — M40 Consumes

| Source | What | Mechanism |
|---|---|---|
| M33 Party Master | Party records, contacts, banking, tax registration, consent | Live read |
| M08 Contract | Partner agreement execution, terms, renewal and termination events | Events + REST |
| M11 Pricing | Commission rates, partner pricing, alliance benefit values | REST |
| M07 CRM | Pipeline and opportunity status for attribution and conflict detection | Live read + events |
| M09 Warranty | Brand claim performance scorecard (decision time, approval rate, payment time) | Projection |
| M23 Quality | Quality findings, audit outcomes, brand-standards audit results | Projection + events |
| M22 Competency | Technician brand certification status and expiry | Projection |
| M14 / M15 | Refurbished stock available for reseller allocation | Live read |
| M19 / M04 | Franchise branch revenue for royalty computation | Projection |
| M53 Revenue & Settlement | Commission computation and payout status | Projection |
| M24 Document | Agreements, authorisations, evidence, e-signature | Service call |

### 12.2 Downstream — M40 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M07 CRM | Partner-sourced leads and opportunities with attribution; deal registrations and protection periods | Command + events |
| M53 Revenue & Settlement | Programme terms, attribution and accrual instructions for commission and royalty | Projection + command |
| M20 Receivable | Franchise fee, royalty and levy invoicing instructions | Command |
| M52 Payable | MDF claim payment instructions | Command |
| M11 Pricing | Alliance scheme benefits to apply and partner pricing scope | Projection |
| M09 Warranty | Brand authorisation scope and validity governing claimable work | Projection |
| M01 / M02 / M31 | Authorisation status gating brand-authorised work | Projection |
| M23 Quality | Brand and franchise audit schedules and obligations | Command + projection |
| M35 Marketing | Approved co-marketing campaign requests and partner audiences | Command |
| M12 Marketplace | Cross-reference where a party is both a seller and a partner, keeping the two roles distinct | Projection |
| M10 Loyalty | Alliance member benefit definitions where they interact with membership | Projection |
| M25 BID · M26 AIM | Partner, channel, attribution and programme fact streams | Warehouse extract |
| **P12 Partner & Referral Portal** | The complete partner experience | REST — the module's principal external surface |
| **P08 Brand Partner Portal** | Relationship, authorisation and obligation context alongside M09's claim surface | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `partner.approved` | partner id, type, programme, tier | M08, M29, M25 |
| `partner.activated` | partner id, portal scope, commercial terms | M11, M53, M35 |
| `partner.tier_changed` | partner id, old tier, new tier, effective | M11, M53 |
| `partner.suspended` / `partner.exited` | partner id, reason, settlement status | M29, M53, M07 |
| `authorisation.expiring` | brand, authorisation, days remaining, obligations outstanding | M09, M01, M23, executive alerting |
| `authorisation.lapsed` | brand, scope affected, branches affected | **M01, M02, M31, M09** — work gating |
| `partner.health_at_risk` | partner id, score, factors, recommended action | Executive alerting, M25 |
| `referral.lead_submitted` | partner id, lead ref, consent ref | M07, M33 |
| `attribution.established` | subject, partner, model, window | M53, M07, M25 |
| `deal.registered` | registration id, partner, customer, value, protected_until | M07, M25 |
| `deal.conflict_detected` | registration id, conflicting party, basis | M07, CCO alerting |
| `alliance.benefit_applicable` | scheme, customer, benefit ref | M11, M01 |
| `franchise.royalty_computed` | franchise, period, basis, amount | M20, M53 |
| `mdf.claim_approved` | claim id, partner, amount | M52, M35 |
| `partner.communication_unacknowledged` | partner id, communication, days overdue | CCO alerting |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-PCM-01 | Brand partner systems and portals | Bidirectional | Authorisation notices, bulletins, audit scheduling *(alongside M09's claim integrations)* |
| INT-PCM-02 | Alliance partner member systems (insurer, telco, bank) | Inbound / API | Member eligibility validation |
| INT-PCM-03 | E-signature *(via M24)* | Bidirectional | Partner agreement execution |
| INT-PCM-04 | Disbursement for MDF and commission *(via M52/M50)* | Outbound | Partner payments |
| INT-PCM-05 | Business registration verification (RJSC / BIN) | Outbound | Partner and franchisee verification |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/partners` | GET/POST | Partner register and application | P12, P03 |
| `/api/v1/partners/{id}` | GET/PATCH | Partner profile, standing and programme | P12, P03 |
| `/api/v1/partners/{id}/onboarding` | GET/POST | Onboarding checklist progress | P12, P03 |
| `/api/v1/authorisations` | GET/POST | Brand authorisation register | P03, P08 |
| `/api/v1/authorisations/check` | POST | Is this work covered by a valid authorisation? | M01, M02, M31, M09 |
| `/api/v1/partners/{id}/health` | GET | Health score with factor decomposition | P03, P06 |
| `/api/v1/referral/links` | GET/POST | Referral link and code management | P12 |
| `/api/v1/referral/leads` | GET/POST | Lead submission and status | P12 |
| `/api/v1/deals/register` | POST | Register a deal with conflict detection | P12 |
| `/api/v1/deals/{id}` | GET | Registration status and protection period | P12, P03 |
| `/api/v1/alliance/eligibility` | POST | Validate a customer against an alliance scheme | M01, M11, P03 |
| `/api/v1/partners/{id}/earnings` | GET | Attributed revenue, commission accrued and paid | P12 |
| `/api/v1/mdf/claims` | GET/POST | MDF claim submission and status | P12, P03 |
| `/api/v1/franchise/{id}/royalty` | GET | Computed royalties by period | P03, P12 |
| `/api/v1/partners/analytics` | GET | Channel contribution and programme ROI | P03, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R04 Chief Commercial Officer | C R U D A | All — programmes, tiers, suspension, conflict overrides |
| R28 Warranty Claims Officer *(Finance Director's delegate)* | R U | Brand authorisations and obligations |
| R03 Chief Financial Officer | R A | Commercial terms, MDF approval, franchise royalties |
| R26 Finance Manager | R U A | MDF claims, commission settlement, royalty invoicing |
| R21 Sales Manager | C R U | Referral and alliance partners in the assigned segment; deal registration decisions |
| R22 Account Manager (Corporate) | R U | Assigned partners |
| R23 Marketing Manager | C R U | Co-marketing, MDF allocation, partner campaigns |
| R32 Quality Manager / ISO Coordinator | R U | Brand and franchise audits, obligations, standards |
| R05 Operations Director | R | Authorisation status affecting delivery |
| R06 Branch Manager | R | Franchise branch context where applicable |
| R24 Marketplace Operations Officer | R | Cross-reference where a party is both seller and partner |
| R33 IT / System Administrator | R U | Portal provisioning and integrations |
| **R38 External Party — Brand Partner** | R U | Own brand: authorisation, obligations, audits, performance *(EA-05)* |
| **R38 External Party — Referral / Alliance Partner** | C R U | Own records: links, leads, registrations, earnings, materials *(EA-01)* |
| **R38 External Party — Reseller** | C R U | Own allocation, orders and settlement |
| **R38 External Party — Franchisee** | R U | Own territory: performance, royalties, standards, audits |
| — Partner Manager *(new position under R04)* | C R U | All partner records; cannot approve their own MDF allocation |

**Field-level restrictions.** `commission_rate` is restricted to R03, R04, R24 and R26
*(`05-04` §5)*. No partner sees another partner's data, 1000FiX cost or margin, or internal notes
*(EA-01, EA-02)*. Franchise branch data visible to a franchisee is scoped to their own territory
in addition to the standard branch tier.

**Segregation of duties.** SOD-18 *(to be registered in `05-04` §6)*: allocating MDF and
approving a claim against it cannot be the same person. A deal-registration conflict cannot be
decided by the account manager who owns the conflicting opportunity.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Brand relationship board | CEO, CCO, Finance Director | Weekly | Every brand: authorisation status and expiry, obligations outstanding, audit position, claim performance, health score and trend |
| Authorisation expiry watchlist | Finance Director, CCO, Ops Director | Weekly | Authorisations expiring within 180 days with renewal status and blocking issues |
| Partner health and at-risk register | CEO, CCO | Monthly | Partners in the at-risk band with contributing factors and actions |
| Channel contribution | CEO, CCO, CFO | Monthly | Revenue and margin by channel — direct, referral, alliance, reseller, franchise, marketplace |
| Referral performance | CCO, Marketing | Weekly | Leads submitted, qualified, converted, and revenue attributed, by partner and campaign |
| Partner cohort economics | CCO, CFO | Quarterly | Acquisition cost, activation, productivity and retention by partner cohort; programme ROI |
| Deal registration and conflict log | CCO, Sales Manager | Weekly | Registrations by state, protection periods expiring, conflicts and their decisions |
| Alliance scheme performance | CCO, Account Managers | Monthly | Eligibility checks, benefits applied, volume against commitment, scheme profitability |
| Franchise performance benchmark | CEO, CCO, Ops Director | Monthly | Franchise branches against owned branches and each other on volume, TAT, CSAT, quality and financials |
| Franchise royalty and compliance | CFO, CCO | Monthly | Royalties computed, invoiced and collected; standards-audit status |
| MDF fund position | Marketing Head, CFO | Monthly | Allocated, claimed, approved, paid and remaining, with campaign outcomes |
| Partner enablement status | CCO, Quality Manager | Monthly | Training and certification completion; unacknowledged mandatory communications |
| Partner commission accuracy | CFO, CCO | Monthly | Commission computed vs paid vs disputed; error rate against the 100% accuracy target |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W8 Target | W9 Target |
|---|---|---|---|---|
| KPI-C40-01 | Active referral / alliance partners | 0 | 120 | **> 200** |
| KPI-C40-02 | Referral-attributed new customers | 0% | 8% | **> 12%** |
| KPI-C40-03 | Partner portal adoption among approved partners | 0% | 60% | **> 75%** |
| KPI-C40-04 | Partner commission accuracy | unmeasured | 99% | **100%** |
| KPI-C40-05 | Brand authorisations lapsed without escalation | unknown | 0 | **0** |
| KPI-C40-06 | Brand authorisations renewed before expiry | unmeasured | 95% | **100%** |
| KPI-C40-07 | Brand obligations completed by due date | unmeasured | 90% | **> 98%** |
| KPI-C40-08 | Brand partner satisfaction | unmeasured | 4.2 | **> 4.5** |
| KPI-C40-09 | Partners in the at-risk health band | unknown | < 20% | **< 10%** |
| KPI-C40-10 | Deal registrations decided within SLA | n/a | 90% | **> 98%** |
| KPI-C40-11 | Channel conflicts escalated to the CCO | n/a | measured | **declining trend** |
| KPI-C40-12 | Partner onboarding cycle time | n/a | < 21 days | **< 10 days** |
| KPI-C40-13 | MDF claims decided within SLA | n/a | 90% | **> 95%** |
| KPI-C40-14 | Franchise branches meeting brand standards at audit | n/a | 90% | **> 95%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L2 | OCA `partner_*`, `agreement`, `crm_lead_*`, `commission` family, `document_*` | 22% |
| L4 | P12 Next.js partner portal *(shared components with P07/P08)* | 20% |
| L5 | `cd_partner_program`, `cd_referral`, `cd_deal_registration`, `cd_partner_performance`, `cd_franchise` | 58% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C40-01 | `cd_partner_program` — partner spine, typed extensions, programmes, tiers, onboarding, standing, exit | Odoo module | 5 PW |
| CD-C40-02 | Brand authorisation register, expiry scheduler, obligation and audit tracking, work gating | Odoo module | 4 PW |
| CD-C40-03 | `cd_referral` — links, codes, lead submission with consent, attribution model and window | Odoo module | 3 PW |
| CD-C40-04 | `cd_deal_registration` — registration, conflict detection, protection periods, channel precedence | Odoo module | 3 PW |
| CD-C40-05 | `cd_partner_performance` — health scoring with factor decomposition, enablement, communications, analytics | Odoo module | 2 PW |
| CD-C40-06 | `cd_franchise` — territory, fees, royalties, standards, benchmarking; plus MDF fund ledger and claims | Odoo module | 2 PW |
| CD-C40-07 | P12 portal domain services and partner-scoped API | Service | 1 PW |
| | | **Total** | **20 PW** |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M33 Party Master | A partner is a party before it is a partner |
| M08 Contract | The agreement gates activation; partner agreement families live there |
| M11 Pricing | Commission rates and alliance benefit values |
| M07 CRM | Attribution and conflict detection run against pipeline |
| M53 Revenue & Settlement | Commission and royalty computation and payout |
| M09 Warranty *(W4)* | Brand claim performance feeds relationship health |
| M23 Quality *(W5)* | Audit findings feed health and franchise standards |
| P12 delivered with M40 | The portal is the module's principal surface |

> **Sequencing concern, stated plainly.** M40 is scheduled P2 in W7, yet its brand-authorisation
> capability protects revenue streams 1 and 4 from the programme's first day. The authorisation
> register, expiry scheduler and obligation tracking (CD-C40-02, 4 PW) are **candidates for
> earlier delivery in W4 alongside M09**, leaving the referral, franchise and MDF capability in
> W7. This is a recommendation for the programme board, not a unilateral re-plan; the register
> in `02-02` remains authoritative until it decides.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Brand authorisation documents and terms | 17+ | `fix.brand.authorisation` + `fix.brand.obligation` | W4 *(if advanced)* / W7 |
| Brand partner contacts | ~60–100 | `fix.partner.contact.role` (party in M33) | W4 / W7 |
| Informal referral arrangements | To be profiled | `fix.partner.profile` (Prospect state — full onboarding required) | W7 |
| Existing alliance or corporate benefit schemes | To be profiled | `fix.alliance.scheme` | W7 |
| Manual partner commission records | 12 months | Warehouse only, for baseline | W7 |

**Migration rule.** Brand authorisations are migrated with the source document attached and the
expiry date verified against that document, not against a spreadsheet. Any authorisation whose
current validity cannot be evidenced is migrated flagged and escalated immediately — an
unevidenced authorisation is a live operational risk, not a data-quality issue.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | All five partner types instantiate from configuration with no code change | Five scripted instantiations |
| AC-02 | A partner cannot transact until the M08 agreement is executed and onboarding is complete | Negative test via UI, portal and API |
| AC-03 | Brand authorisation expiry escalates at every declared interval, and no authorisation can lapse silently | Compressed-timeline test across all 17+ authorisations |
| AC-04 | Work requiring a lapsed authorisation is blocked in M01, M02, M31 and M09 | Negative test per module |
| AC-05 | Attribution written at lead creation survives unchanged through opportunity, quotation, order and revenue | End-to-end traceability test |
| AC-06 | A lead converting outside its attribution window attributes to no partner | Boundary test |
| AC-07 | A partner-submitted lead cannot be created without recorded customer consent | Negative test |
| AC-08 | Deal-registration conflict detection completes in under 2 seconds and never auto-approves a conflict | Performance + negative test |
| AC-09 | A partner sees only their own records, verified by negative test per partner type | Security test |
| AC-10 | Portal access is revoked within one hour of exit, suspension or agreement expiry | Timed test |
| AC-11 | Relationship health scores decompose into named factors with weights, and reproduce from source data | Reconciliation test |
| AC-12 | Franchise royalties compute from ERP-recorded revenue and reconcile to the invoice raised | Joint test with M19/M20 |
| AC-13 | MDF allocation and claim approval cannot be performed by the same user | SOD negative test |
| AC-14 | Named business super-users — including at least two brand partners and two referral partners — sign off UAT for all P0 and P1 requirements | Signed UAT record |
| AC-15 | Zero critical or high security findings on the P12 external surface | Security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Should the brand-authorisation register be advanced to W4 alongside M09, given that it protects revenue streams 1 and 4 from day one? | CTO / CCO / Programme Board | **W3 — roadmap decision** |
| Q-02 | Should brand-partner authorisation agreements live in M08 with the relationship in M40, as this design assumes? *(carried from M08 Q-07)* | CCO | W4 |
| Q-03 | What is the referral commission model — fixed fee, percentage, or tiered by value — and is it viable against the marketplace take rate? | CCO / CFO | W7 build |
| Q-04 | What is the attribution window and model — first touch, last touch, or partner-declared with validation? | CCO | W7 build |
| Q-05 | Is franchise expansion an approved strategy with a defined model, or an aspiration in the business plan? The 2 PW franchise build should not proceed on an aspiration | CEO | **W6 — blocking for §5.4** |
| Q-06 | Do alliance partners (insurers, telcos) require API-based member eligibility validation, and will they expose one? | CCO / CTO | W7 build |
| Q-07 | What channel precedence applies when a referral partner introduces a customer already in the direct pipeline? | CCO | W7 build |
| Q-08 | Is there an MDF budget at all, or is co-marketing partner-funded? The module supports both; the programme design must choose | CCO / Marketing Head | W7 build |
| Q-09 | Where a marketplace seller is also a referral partner, are both roles permitted simultaneously, and how is conflict of interest managed? | CCO | W7 build |

---

## 19. References

**Internal**
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §2, §5, §8 ·
`M12_Marketplace_and_Seller_Ecosystem.md` §3 (the seller/partner boundary) ·
`M09_Warranty_Protection_Plans_and_Claims.md` §5.5 FR-WTY-061, §12 ·
`M08_Contract_Lifecycle_Management.md` §5.1, §18 Q-07 ·
`M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md` §3 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §1.7, §5, §8 EA-01, EA-02, EA-05 ·
`05-05_Business_Rules_and_Automation_Catalogue.md` ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P08, P12 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`1000FiX_Services_Company_Profile.md` §Brand Partnerships ·
`1000FiX Business Plan` §Expansion Strategy, §Franchise, §Alliance & Referral ·
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.11 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §7

**External benchmark**
PRM platform practice (ZINFI, Impartner, Channeltivity, Mindmatrix, xAmplify) — recruitment, onboarding, deal registration, MDF, co-marketing, partner analytics, certification-gated tiers ·
Salesforce PRM / Oracle Partner Management — partner accounts, scoped partner users, deal registration, scorecards ·
SAP / IFS channel management — authorisation and agreement tracking ·
Franchise management practice (FranConnect class) — territory, royalties, brand standards audits, franchisee benchmarking ·
Insurance and telecommunications alliance practice — scheme-based member benefit entitlement ·
Odoo 19 / OCA `partner_*`, `agreement` and `commission` module families

---

*Module M40 · Category C · 1000FiX ERP System v2.0 · CONFIDENTIAL*
