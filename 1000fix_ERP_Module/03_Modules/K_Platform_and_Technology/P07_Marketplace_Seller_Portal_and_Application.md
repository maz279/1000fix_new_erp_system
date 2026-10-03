---
id: FIX-ERP2-P07
portal_id: P07
portal_code: MSP
portal_name: Marketplace Seller Portal & Application
type: External Web Portal + Native Application (two-sided marketplace supply side)
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Marketplace Squad
priority: P1
wave: W7
---

# P07 — Marketplace Seller Portal & Application
### Portal Suite · Code `MSP` · ★ New in v2.1

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P07 |
| **Portal code** | `MSP` |
| **Type** | External web portal + native application — the **supply side** of a two-sided marketplace |
| **Status** | ★ New in v2.1 — no equivalent existed in v1.0 |
| **Priority** | **P1** |
| **Delivery wave** | **W7** (Months 27–30) |
| **Users** | External freelance engineers and independent repair shops |
| **Volume** | **500–2,000 sellers**; target 500 approved active by end of W8 |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Marketplace Squad |
| **Technology** | Next.js 15 (web) + React Native (application) · shared design system |
| **Custom development** | `CD-207` (web), `CD-208` (application) |
| **Requirement range** | FR-POR-195 … FR-POR-228 |
| **Requirement count** | **34** *(measured — supersedes the 16 allocation in `05-01` §4)* |
| **Effort estimate** | **34 person-weeks** (22 PW web · 12 PW application) |
| **Backing modules** | M11, M12, M15, M20, M22, M23, M27, M29, M33, M34, M37, M53, M60 |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M65 Localisation |

---

## 2. Purpose

P07 is **how 1000FiX grows beyond the capacity it employs**. The marketplace model lets
external engineers and independent shops deliver work under the 1000FiX brand, and the Scope
Charter assumes marketplace external capacity delivers **≥ 25% of total job volume**. Every one
of those jobs reaches a customer through this portal.

Its defining tension is the one every marketplace faces: **the platform's brand promise is
delivered by people it does not employ.** A customer booking through P01 does not distinguish
an owned technician from a marketplace seller — nor should they. That means quality, evidence
and conduct standards on a marketplace job must be **identical to an owned job**, enforced by
the platform rather than by employment.

P07 holds no authoritative state. The listing belongs to M12, the job to M01, the wallet to
M53, the rating to M34. What P07 owns is **the seller's relationship with the platform** — how
they join, what they may do, how they are measured, and what they are paid.

### Why It Exists

**Owned capacity caps growth.** With 200–400 employed technicians, job volume is bounded by
hiring. The Scope Expansion Delta records that without a marketplace, "growth is capped at owned
technician headcount". P07 is the mechanism by which capacity becomes elastic.

**Trust must be manufactured, because it cannot be assumed.** An employed technician is
recruited, trained, certified and supervised. A marketplace seller is none of those things by
default. Everything that employment provides — identity verification, competence assurance,
conduct standards, recourse — has to be constructed in the portal: KYC/KYB at onboarding,
certification per category, evidence standards identical to owned jobs, held payouts, dispute
handling and performance-driven visibility.

**Payouts are the trust mechanism in both directions.** A seller who is not paid predictably
leaves. A platform that pays before a dispute window closes carries the loss. `04-00` requires
payouts held for a defined period and blocked while a dispute is open — the standard escrow
pattern, and the one that makes both sides safe.

**Seller retention is the economics.** `04-00` targets 65% seller retention at twelve months
and 70% monthly active among approved sellers. Acquiring a seller costs onboarding, verification
and training; a seller who leaves within a year never repays it.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Scope Expansion Delta §M12 | "Marketplace commission & settlement" and "Advertising, boost & lead placement" as new revenue capabilities |
| Scope Expansion Delta §Risks | "Marketplace without a system — cannot onboard external capacity; growth capped at owned technician headcount" |
| Scope Charter §6.2 | **Marketplace commission and advertising: BDT 84 lac/year** attributed to M12 |
| Scope Charter §Assumptions | "Marketplace external capacity delivers ≥ 25% of total job volume" |
| `04-00` §P07 | Capability set across ten areas, **four governance requirements** and five KPIs, adopted verbatim |
| `04-00` §3 PS-01…PS-12 | Twelve cross-portal standards, all binding |
| `05-04` §1 R38 | External Party covering the marketplace seller sub-class; MFA required for financial actions |
| `05-04` §6 SOD-06 | Approve marketplace seller + approve their payout — hard block |
| `05-04` §7 | Marketplace seller approval by Marketplace Operations Officer; payout standard automatic, held or disputed by Finance Manager |
| `M12` (Category C) | Marketplace and seller ecosystem — the module behind this portal |
| ERP BRD BR-QMS-005 | QC checklist enforcement on service completion — applied identically to marketplace jobs |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Seller registration as a freelance engineer or a shop, with class-appropriate verification |
| 2 | Identity and business verification: NID, trade licence, references, work samples, phone and email OTP |
| 3 | Approval tracking, digital agreement execution, registration fee payment and registration expiry |
| 4 | Profile: skills, categories, service areas, working hours, photographs, shop open/closed state |
| 5 | Listing management: service and product listings, pricing, availability, individual and bulk enable/disable |
| 6 | Seller-held stock declaration for product listings |
| 7 | Job discovery: broadcast jobs matching the seller's profile, service area and certification |
| 8 | Quotation and counter-bid submission, and job acceptance |
| 9 | Job execution to completion with evidence capture and customer sign-off |
| 10 | Customer communication on an open job, with attachment and escalation to 1000FiX |
| 11 | Wallet: balance, earnings by job, commission and fee breakdown, statements, payout history and request |
| 12 | Performance scorecard with acceptance, on-time, rating, rework and dispute measures, and stated consequences |
| 13 | Review visibility and a single response per review |
| 14 | Growth: boost and top-listing purchase, page-targeted advertising, impression and click reporting |
| 15 | Standards: required training, policy acknowledgement, per-category certification requirements |
| 16 | Dispute raising and response with evidence |
| 17 | Bengali-first interface, on a phone, at low bandwidth |
| 18 | Instrumentation of onboarding funnel, activity and retention |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **The customer side of the marketplace** | **P01** | The buyer books, tracks, pays and reviews in P01; P07 is the supply side only |
| **Seller approval decision, matching algorithm, commission rates and platform policy** | **M12** Marketplace & Seller Ecosystem | P07 submits and displays; M12 decides |
| **Job broadcast, matching and allocation logic** | **M12** with **M02** | P07 shows a seller the jobs they may bid on; it never decides who gets one |
| **Commission calculation, settlement and payout execution** | **M53** Revenue, Commission & Settlement | P07 shows the wallet; M53 computes and pays |
| **Price setting for platform services, and dynamic pricing** | **M11** Pricing | A seller sets their own listing price within platform bounds M11 defines |
| **Service order lifecycle and SLA** | **M01** | A marketplace job is a service order like any other |
| **Quality standards, QC checklists and CAPA** | **M23** Quality Management | P07 enforces the same checklist an owned job requires; M23 defines it |
| **Certification content, assessment and issuance** | **M22** Learning & Competency | P07 shows requirements and status; M22 certifies |
| **Rating, review moderation and complaint handling** | **M34** Customer Experience | P07 displays and permits one response; M34 owns moderation |
| **Dispute adjudication** | **M12** with **M34** | P07 collects evidence from the seller; 1000FiX adjudicates |
| **Parts supply to sellers** | **M15** with **M38** | A seller buying parts is a commercial transaction; P07 links to it |
| **Vendor and supplier relationships** | **P05** | A supplier sells *to* 1000FiX; a marketplace seller sells *through* it |
| **Referral and alliance partners** | **P12** | A referral partner introduces business but performs no work |
| **Identity verification data source** | **M12** with an accredited provider (L6, `02-05` §5) | P07 collects; verification is performed by an accredited service |
| **Identity, session policy, MFA** | **M29** | **PS-01**; MFA required for financial actions |

### 3.3 Shared Concepts

| Concept | P07's Role | Owning Module |
|---|---|---|
| The seller's relationship with the platform | **Owns** — the defining concern of this portal | P07 |
| Seller record, approval state, policy | Submits and displays | M12 |
| Listing | Creates and manages within M12's rules | M12 / M37 |
| Job | Discovers, bids, accepts, executes | M01 / M12 |
| Evidence and QC | Captures to the same standard as an owned job | M23 |
| Wallet, commission, payout | Displays; requests payout | M53 |
| Rating and review | Displays; one response | M34 |
| Certification | Displays status; blocks uncertified categories | M22 |
| Boost and advertising | Purchases; displays performance | M12 |
| Dispute | Raises and responds with evidence | M12 / M34 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Marketplace onboarding and KYC/KYB practice** | KYC for individuals and **KYB for incorporated providers** to satisfy payout-partner due diligence; automated document verification, sanctions and PEP screening; identity checks embedded in the signup flow so the user is not sent off-platform | **Class-differentiated verification is the single most influential external reference for P07.** A freelance engineer is verified as an individual (NID, references, work samples); a shop is verified as a business (trade licence, ownership, bank account). Applying one standard to both either over-burdens the freelancer or under-verifies the shop. Also adopted: verification **inside** the signup flow, because sending an applicant to a third-party site is where onboarding funnels collapse | Full sanctions and PEP screening at this scale and jurisdiction; the risk profile of a laptop repair engineer in Dhaka does not warrant it, and it would be verification theatre |
| **Marketplace payments practice (Sharetribe, escrow providers)** | Split payments dividing between seller and platform commission; **escrow or delayed payout holding funds until service delivery**; risk-based payouts releasing established sellers quickly and holding new sellers longer; payouts blocked while a dispute is open | **Escrow with risk-based release, adopted exactly.** A new seller's first payouts are held longer than an established seller's. This is the mechanism that makes the platform safe to open to unknown parties without making it unattractive to good ones. `04-00`'s governance requirement — payouts held for a defined period and blocked during a dispute — is this pattern | Holding a marketplace payments licence. Settlement runs through M53 and the existing payment rails |
| **Trust-and-safety practice for two-sided platforms** | Identity verification at onboarding, risk-based transaction authentication, real-time monitoring for unusual activity, performance thresholds with automatic consequence | **Performance-driven visibility with automatic consequence.** `04-00` requires that falling below threshold *reduces visibility automatically, then suspends*. A graduated, automatic consequence is both fairer and more effective than a human deciding case by case, and it scales to 2,000 sellers | Behavioural surveillance beyond job-related activity |
| **Gig platform seller apps (Pathao, Uber, Swiggy partner apps)** *(the local benchmark that matters)* | Bengali-first, phone-only, low-bandwidth; earnings visible per job in real time; acceptance rate and rating as the governing metrics; instant job broadcast with a short accept window | **The interaction vocabulary Bangladeshi gig workers already have.** Earnings per job visible immediately, a scorecard they recognise, and a phone-only experience. A seller who has driven for Pathao should find P07 familiar within minutes. No international benchmark supplies this | Aggressive acceptance-rate penalties. A repair job is not a ride; a seller declining a job outside their competence should not be punished for it |
| **Field-service quality practice** | Evidence capture, QC checklists and customer sign-off as conditions of job completion | **Identical standards for marketplace and owned jobs**, which `04-00` states as a governance requirement. A customer cannot tell the difference, so the evidence must not differ either | A separate, lighter standard for marketplace work — which is how marketplaces destroy the brand that made them viable |
| **Seller growth and advertising practice** | Paid placement, boost, and page-targeted advertising with impression and click reporting | **Boost and advertising as a seller-funded growth product**, contributing to the BDT 84 lac marketplace revenue line | Auction-based ad bidding; disproportionate complexity for the scale |

**Design position.** Five deliberate differences from the benchmark.

First, **quality standards do not differ from owned work.** This is stated as a governance
requirement in `04-00` and it is the most important design decision in the portal. The same QC
checklist, the same forced evidence capture, the same customer sign-off. A marketplace job that
is easier to complete than an owned job is a marketplace job that damages the brand which makes
the marketplace worth joining.

Second, **verification is class-differentiated and completed in-flow.** A freelance engineer and
a shop face different checks appropriate to what they are. Both complete verification without
leaving P07, because `04-00` targets 60% onboarding completion from started registrations and
every off-platform redirect costs a material share of that.

Third, **consequence is automatic and graduated.** Below threshold, visibility reduces
automatically; further below, listings suspend. The seller sees the threshold, their position
against it, and what recovery requires — before the consequence, not after. Automatic and
transparent beats discretionary and opaque at 2,000 sellers.

Fourth, **payouts are risk-based, and the rule is published.** A new seller's hold period is
longer and they are told so at onboarding. A seller who discovers an unannounced hold assumes
they are being cheated; a seller who was told the rule and can see their progression toward the
shorter period is being managed.

Fifth, **the portal is a phone product first.** A freelance engineer in Bangladesh runs their
working life on a phone. The web surface exists for listing management and statements; the
application is where jobs are discovered, accepted and executed. The design centre is a
mid-range Android device on a mobile data connection.

---

## 5. Capability Areas & Functions

### 5.1 Registration, Verification & Onboarding

| FR ID | Feature | Function — "The portal shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-195 | Class selection | Allow an applicant to register as a **freelance engineer** or a **shop**, and apply the verification set appropriate to that class | **P0** | L5 |
| FR-POR-196 | Contact verification | Verify phone and email by OTP before any document is collected | **P0** | L5 |
| FR-POR-197 | Individual verification (KYC) | Collect and verify NID, photograph, address, references and work-sample images for a freelance engineer, through an accredited verification service without leaving the portal | **P0** | L5/L6 |
| FR-POR-198 | Business verification (KYB) | Collect and verify trade licence, TIN/BIN, ownership, premises evidence and bank account for a shop | **P0** | L5/L6 |
| FR-POR-199 | Approval tracking | Show the applicant exactly where their application stands, what remains outstanding, and the expected decision time | **P0** | L5 |
| FR-POR-200 | Digital agreement | Present the seller agreement in Bengali and English, capture digital execution, and retain the executed version with its version reference | **P0** | L5 |
| FR-POR-201 | Registration fee | Collect any registration fee through the standard payment rails, with a receipt | P2 | L5 |
| FR-POR-202 | Registration validity | Show registration expiry and required renewal, and prevent transacting past expiry | P1 | L5 |
| FR-POR-203 | **Transaction gate** | Prevent a seller from transacting until documents are verified, the agreement is executed and admin approval is granted (`04-00` governance requirement 1) | **P0** | L5 |

### 5.2 Profile & Listings

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-204 | Profile | Maintain skills, service categories, service areas, working hours, photographs and biography, with category claims limited by held certifications | **P0** | L5 |
| FR-POR-205 | Availability state | Set an open/closed or available/unavailable state that immediately affects job broadcast eligibility | **P0** | L5 |
| FR-POR-206 | Service listings | Create and manage service listings with description, price within platform bounds, duration and coverage area | **P0** | L5 |
| FR-POR-207 | Product listings | Create and manage product listings against the seller's own declared stock, with price and availability | P2 | L5 |
| FR-POR-208 | Bulk listing management | Enable, disable and price-adjust listings in bulk, and disable an individual listing without deleting it | P1 | L5 |
| FR-POR-209 | Own stock declaration | Declare and maintain the seller's own parts stock backing product listings, distinct from any 1000FiX inventory | P2 | L5 |

### 5.3 Work: Discovery, Bidding & Execution

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-210 | Job broadcast | Present broadcast jobs matching the seller's categories, certifications, service area and availability, with a stated response window | **P0** | L5 |
| FR-POR-211 | Quotation and counter-bid | Submit a quotation against a broadcast job, and counter-bid where the model permits, with price, timing and any condition | **P0** | L5 |
| FR-POR-212 | Acceptance | Accept an awarded job, with the full job context — customer, device, fault, address, entitlement — released on acceptance | **P0** | L5 |
| FR-POR-213 | Job execution | Execute the job to completion: arrival, diagnosis, fault coding, time, parts used and outcome | **P0** | L5 |
| FR-POR-214 | **Evidence to owned-job standard** | Require the same forced photographic evidence, before and after, geo-stamped and time-stamped, that an owned job requires (`04-00` governance requirement 2) | **P0** | L5 |
| FR-POR-215 | **QC and sign-off to owned-job standard** | Enforce the same QC checklist and capture the same customer e-signature that an owned job requires before completion (BR-QMS-005) | **P0** | L5 |
| FR-POR-216 | Certification gate | Prevent a seller accepting or completing work in a category for which they hold no current certification | **P0** | L5 |
| FR-POR-217 | Customer communication | Provide an in-job message thread with the customer, with attachments, and an escalation route to 1000FiX that both parties can invoke | **P0** | L5 |
| FR-POR-218 | Offline tolerance | Allow job execution and evidence capture to continue through connectivity loss, queueing for sync, using the P02 journal pattern | P1 | L5 |

### 5.4 Earnings, Payouts & Performance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-219 | Wallet | Present the seller's balance — available, held, in dispute — with every movement traceable to a job | **P0** | L5 |
| FR-POR-220 | Earnings breakdown | Show, per job, gross value, platform commission, any fee, tax withheld and net earning, with the calculation basis stated | **P0** | L5 |
| FR-POR-221 | **Payout hold and release** | Apply the payout hold period per the seller's risk tier, show the release date per job, and **block release entirely while a dispute is open** (`04-00` governance requirement 3) | **P0** | L5 |
| FR-POR-222 | Risk tier transparency | Show the seller their current payout tier, the hold period it carries, and what progression to a shorter hold requires | P1 | L5 |
| FR-POR-223 | Payout request and history | Request a payout of available balance, and show the schedule, history and remittance reference | **P0** | L5 |
| FR-POR-224 | Statements | Provide period statements suitable for the seller's own tax and accounting purposes | P1 | L5 |
| FR-POR-225 | **Performance scorecard** | Present acceptance rate, on-time rate, rating breakdown, rework rate and dispute rate, with the jobs behind each measure, and **state plainly the consequence of falling below threshold** (`04-00` governance requirement 4) | **P0** | L5 |
| FR-POR-226 | Graduated consequence | Reduce listing visibility automatically below the first threshold, and suspend listings below the second, notifying the seller before each takes effect with the recovery required | **P0** | L5 |

### 5.5 Reviews, Growth, Standards & Disputes

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-227 | Reviews | Show customer reviews with ratings, and permit exactly one public response per review | P1 | L5 |
| FR-POR-228 | Growth, standards and disputes | Purchase boost or top-listing placement for a period and page-targeted advertising with impression and click reporting; access required training, acknowledge policy updates and see per-category certification requirements; and raise or respond to a dispute with evidence, tracked to adjudication | P1 | L5 |

> **Cross-cutting.** Training content and certification assessment are M22's; P07 surfaces the
> requirement, launches the training and displays the outcome. Advertising placement and pricing
> are M12's; P07 is the purchase and reporting surface.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No authoritative state** | P07 persists no business object (`04-00` §1) |
| T-02 | **Seller isolation** | Every query is scoped to the authenticated seller. A seller never sees another seller's jobs, earnings, listings, rating detail or bids |
| T-03 | **Bid confidentiality** | A seller cannot see another seller's quotation on a broadcast job, before or after award |
| T-04 | **Transaction gate enforced server-side** | The verification, agreement and approval gate is evaluated on every transactional action, not merely at first login |
| T-05 | **Verification in-flow** | Identity and business verification complete inside P07 through an embedded accredited service; no redirect off-platform |
| T-06 | **Evidence parity** | The evidence, QC and sign-off requirements applied to a marketplace job are the **same configuration objects** M23 applies to owned jobs — not a parallel, lighter set |
| T-07 | **Payout hold enforcement** | Hold period and dispute block are evaluated by M53 at release; P07 displays but never computes or overrides a release date |
| T-08 | **MFA on financial actions** | MFA required for payout request, bank detail change and advertising purchase (`05-04` §1) |
| T-09 | **Bank change control** | A change to payout bank details requires MFA, is held for out-of-band verification, and excludes the seller from the next payout run |
| T-10 | **Offline job execution** | Execution and evidence capture tolerate connectivity loss using the P02 append-only journal pattern with idempotent replay (AS-13) |
| T-11 | **Device envelope** | The application runs acceptably on a mid-range Android device; the web surface operates at 3G with a bounded first-load payload (**PS-07**) |
| T-12 | **All traffic through the gateway** | Every call routes through M28 with per-seller credentials and rate limits (**PS-02**) |
| T-13 | **No client-side business logic** | Commission, hold period, threshold and eligibility are computed by their owning module (**PS-11**) |
| T-14 | **Bengali-first** | Bengali is the default; every string including every error exists in Bengali before release (**PS-03**) |
| T-15 | **Accessibility and responsiveness** | WCAG 2.1 AA; usable from 320 px upward (**PS-04, PS-05**) |
| T-16 | **Design system** | Shared component library with P01, P04, P08, P10 and P12 (**PS-06**) |
| T-17 | **Customer data minimisation** | A seller receives the customer's contact and address on acceptance and retains access only for the job's duration plus a bounded window; the customer's wider history is never exposed |
| T-18 | **Graceful degradation** | Where a backing module is unavailable, the capability is disabled with an explanation and a route to marketplace operations (**PS-09**) |
| T-19 | **Instrumentation** | Onboarding funnel, activity, retention and consequence events instrumented to M25 (**PS-10**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Actor

| Actor | Today | With P07 |
|---|---|---|
| **Freelance engineer** | Finds work by word of mouth; no brand, no recourse, unpredictable payment | Receives matched jobs under a known brand, with defined standards and predictable payout |
| **Independent shop** | Competes alone against a national network | Lists on the network's platform and gains demand it could not reach |
| **Customer** | Waits for owned capacity in an underserved area | Is served by a verified seller to the same standard, and cannot tell the difference |
| **Marketplace operations officer** | — (no capability exists) | Approves sellers, adjudicates disputes and manages a supply base from one console |
| **Dispatch** | Declines or delays work beyond owned capacity | Broadcasts overflow and out-of-area work to the marketplace |
| **Quality manager** | Would have no visibility of non-employed work | Sees marketplace QC compliance and rework on the same terms as owned work |
| **Finance** | — | Settles commission and payouts on a schedule with dispute holds enforced |
| **CCO** | Growth capped by hiring | Capacity elastic; geography extensible without a branch |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Marketplace commission and advertising** | Commission on marketplace jobs plus seller-funded boost and advertising | **BDT 84 lac/year** attributed to M12 in Scope Charter §6.2. P07 is the sole channel through which sellers transact, so this revenue does not exist without it |
| **Capacity elasticity** | External capacity delivering ≥ 25% of total job volume | The Scope Charter assumption. Removes hiring as the growth constraint and converts geographic expansion from a branch decision into a supply decision |
| **Geographic reach without capital** | Sellers serve areas where a branch is not justified | Extends coverage at zero fixed cost, supporting the nationwide-coverage claim |
| **Demand-peak absorption** | Overflow broadcast to the marketplace rather than declined or delayed | Protects TAT and CSAT during peaks that owned capacity cannot absorb |
| **Customer retention** | Service available when and where owned capacity is not | Contributes to the **BDT 78 lac/year** retention benefit |
| **Seller acquisition efficiency** | 60% onboarding completion and 65% twelve-month retention | Onboarding cost is real; retention is what makes it repay |
| **Brand protection** | Identical quality, evidence and conduct standards on marketplace work | Protects the brand that makes the marketplace attractive — the benefit that is only visible when it is absent |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Livelihood creation** | Verified, branded, predictably-paid work for independent engineers and small shops is a genuine social contribution and a defensible CSR position |
| **Sector formalisation** | Verification, standards, certification and evidence bring informal repair work into a documented framework |
| **Skills development** | Required training and per-category certification raise capability across a supply base wider than the Company employs |
| **Quality reputation as a moat** | A marketplace that enforces owned-job standards is materially harder to replicate than one that does not |
| **Fair and transparent governance** | Published thresholds, automatic graduated consequence, and payout rules stated at onboarding produce a supply base that trusts the platform |
| **Dispute recourse for both sides** | A structured dispute process with evidence protects the seller as much as the customer |
| **Expansion readiness** | A verified seller network is the fastest route into a new city or a new country |

---

## 8. Journeys & State Models

### 8.1 Seller Lifecycle

```
   APPLIED ──phone/email OTP──► VERIFYING
                                    │  KYC (engineer) or KYB (shop), in-flow
                          ┌─────────┴─────────┐
                    verified                  failed / incomplete
                          │                        │
                   ┌──────▼───────┐          ┌─────▼──────┐
                   │ AWAITING     │          │  LAPSED    │ (recoverable)
                   │ APPROVAL     │          └────────────┘
                   └──────┬───────┘
              approved    │    rejected
              ┌───────────┴──────────┐
              │                      ▼
        ┌─────▼──────┐          DECLINED
        │  AGREEMENT │
        │  EXECUTED  │
        └─────┬──────┘
              │  ◄── TRANSACTION GATE: verified + agreement + approval
        ┌─────▼──────┐
        │   ACTIVE   │◄──────────────┐
        └──┬──────┬──┘               │ recovered
           │      │ below threshold 1│
           │      ▼                  │
           │  ┌───────────────────┐  │
           │  │ REDUCED VISIBILITY│──┘
           │  └────────┬──────────┘
           │           │ below threshold 2
           │      ┌────▼──────┐
           │      │ SUSPENDED │──► listings offline, open jobs completed,
           │      └────┬──────┘    payouts held pending resolution
           │           │
           │      ┌────▼──────┐
           └─────►│ OFFBOARDED│──► final settlement after dispute window
                  └───────────┘
```

| Transition | Guard | Actor |
|---|---|---|
| Applied → Verifying | Phone and email OTP confirmed | System |
| Verifying → Awaiting approval | Class-appropriate verification passed | Accredited service |
| Awaiting approval → Active | Marketplace Operations Officer approves **and** agreement executed | R24 |
| Active → Reduced visibility | Scorecard below threshold 1 for the configured period | **System, automatic** |
| Reduced visibility → Suspended | Scorecard below threshold 2, or a serious conduct finding | **System, automatic** / R24 |
| Any → Suspended | Registration or required certification expired | System, automatic |
| Suspended → Active | Recovery conditions met and re-approved | R24 |
| Suspended → Offboarded | Not recovered, or agreement terminated | R24 + Finance |
| Offboarded → final settlement | All disputes closed and hold periods elapsed | M53 |

### 8.2 Job & Payout Flow — where escrow sits

```
   BROADCAST (M12 matches to eligible, certified, available sellers)
        │
   ┌────▼──────────┐   sellers quote / counter-bid
   │  BIDDING      │   ✖ no seller sees another's bid
   └────┬──────────┘
        │ awarded
   ┌────▼──────────┐
   │  ACCEPTED     │   full job context released to the winning seller only
   └────┬──────────┘
        │
   ┌────▼───────────────────────────────────────┐
   │  EXECUTION — identical standard to owned:  │
   │   ✓ forced before/after evidence            │
   │   ✓ QC checklist                            │
   │   ✓ customer e-signature                    │
   │   ✓ certification held for the category     │
   └────┬───────────────────────────────────────┘
        │ completed
   ┌────▼──────────┐
   │  CUSTOMER PAYS │  (P01 · M20)
   └────┬──────────┘
        │
   ┌────▼─────────────────────────────────────────┐
   │  SETTLEMENT (M53)                             │
   │   gross − commission − fees − tax = net       │
   └────┬─────────────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────────────┐
   │  WALLET: HELD                                  │
   │   ▸ hold period by seller risk tier            │
   │   ▸ release date shown per job                 │
   │   ▸ ✖ BLOCKED ENTIRELY while a dispute is open │
   └────┬──────────────────────────────────────────┘
        │ hold elapsed, no dispute
   ┌────▼──────────┐
   │  AVAILABLE    │──► payout requested → paid → remittance reference
   └───────────────┘
```

| Risk tier | Typical hold | Progression |
|---|---|---|
| New seller | Longest | Job count and clean record over time |
| Established | Shorter | Sustained scorecard above threshold |
| Trusted | Shortest | Long tenure, high rating, no upheld disputes |

> The tier, its hold period and the progression rule are **published to the seller at
> onboarding** (FR-POR-222). A hold a seller was not told about reads as theft.

---

## 9. Portal Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P07-01 | A seller cannot transact until documents are verified, the agreement is executed and admin approval is granted (`04-00` gov. req. 1) | **H** | Chief Commercial Officer |
| PRU-P07-02 | Quality, evidence and sign-off standards on a marketplace job are **identical to an owned job**, enforced by the same configuration objects (`04-00` gov. req. 2) | **H** | Quality Manager |
| PRU-P07-03 | Payouts are held for the defined period and **blocked entirely while a dispute is open** (`04-00` gov. req. 3) | **H** | CFO |
| PRU-P07-04 | Falling below the performance threshold reduces visibility automatically, then suspends (`04-00` gov. req. 4) | **C** | Chief Commercial Officer |
| PRU-P07-05 | A seller may access only their own records — jobs, earnings, listings, ratings | **H** | CTO |
| PRU-P07-06 | A seller never sees another seller's bid, before or after award | **H** | Chief Commercial Officer |
| PRU-P07-07 | A seller cannot accept or complete work in a category for which they hold no current certification | **H** | Quality Manager |
| PRU-P07-08 | Customer contact and address are released on acceptance and retained only for the job plus a bounded window; wider customer history is never exposed | **H** | CTO |
| PRU-P07-09 | MFA is required for payout request, bank detail change and advertising purchase | **H** | CFO |
| PRU-P07-10 | A payout bank change is held for out-of-band verification and excludes the seller from the next payout run | **H** | CFO |
| PRU-P07-11 | The payout hold period, risk tier and progression rule are published to the seller at onboarding | **H** | Chief Commercial Officer |
| PRU-P07-12 | The performance threshold and its consequence are shown to the seller before the consequence takes effect | **H** | Chief Commercial Officer |
| PRU-P07-13 | Commission, hold period and threshold are computed by their owning module, never client-side (**PS-11**) | **H** | CTO |
| PRU-P07-14 | A seller may respond publicly to a review exactly once | **C** | Customer Service Manager |
| PRU-P07-15 | A listing price stays within the platform bounds M11 defines | **H** | Chief Commercial Officer |
| PRU-P07-16 | Registration or certification expiry suspends the seller automatically | **H** | Quality Manager |
| PRU-P07-17 | Bengali is the default language; every string including every error exists in Bengali before release | **H** | Chief Commercial Officer |
| PRU-P07-18 | Verification completes inside the portal; no applicant is redirected off-platform | **C** | Chief Commercial Officer |
| PRU-P07-19 | **SOD-06 supported:** the officer who approves a seller does not approve that seller's payout (`05-04` §6) | **H** | CFO |

---

## 10. Data, Caching & State Model

### 10.1 What P07 Holds

| Object | Purpose | Ownership |
|---|---|---|
| Seller portal session and preference | Language, landing surface, availability toggle state | M29 / P07 |
| Draft listings and draft bids | Recovery of interrupted authoring | **P07**, transient |
| **Offline job journal** | Durability of execution and evidence during connectivity loss — the P02 pattern | **P07**, until synced |
| Media queue | Evidence pending upload | **P07**, bounded |
| Saved views | Per seller | **P07** |

### 10.2 Never Held

| Item | Reason |
|---|---|
| Any business object — listing, job, wallet, rating | PRU-P07-... (`04-00` §1) |
| Another seller's data of any kind | PRU-P07-05, PRU-P07-06 |
| Customer history beyond the accepted job | PRU-P07-08 |
| Commission rates, hold rules or threshold logic | PRU-P07-13 |
| Payment or bank credentials | Payout is a settlement instruction via M53 |
| 1000FiX internal cost, margin or inventory position | External party isolation (`05-04` §8) |

### 10.3 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.marketplace.seller`, approval state, policy | **M12** | Read; submit registration and profile |
| `fix.mp.listing` | **M12** | Create and manage within bounds |
| `fix.mp.job`, broadcast and award | **M12** / M01 | Read; bid; accept; execute |
| `fix.service.order` | M01 | Execute and complete |
| `fix.qc.record`, checklist definition | **M23** | Submit — same objects as an owned job |
| `fix.competency`, certification | **M22** | Read; launch training |
| `fix.commission`, `fix.settlement`, wallet, payout | **M53** | Read; request payout |
| `fix.review`, rating | **M34** | Read; respond once |
| `fix.dispute` | M12 / M34 | Raise; respond with evidence |
| `fix.advertising`, boost placement | **M12** | Purchase; read performance |
| `fix.document` | M24 | Upload verification documents and evidence |
| `fix.party` | M33 | Seller identity |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P07-01 | Registration started but not completed | Prompt the applicant once per stage with what remains, and retain the partial application for the configured period | Prompt only; application retained |
| AUT-P07-02 | Verification returns a result | Advance or fail the application, state the reason, and where recoverable state precisely what is needed | Application held; applicant informed |
| AUT-P07-03 | Seller approved | Release the agreement for execution, then open the transaction gate | Gate stays closed until both complete |
| AUT-P07-04 | Job broadcast matching a seller's profile | Push the job with its response window; expire the opportunity on window close | Job appears on next sync |
| AUT-P07-05 | Job awarded | Release the full job context to the winning seller only, and notify unsuccessful bidders without disclosing the winning bid | Award notification retried |
| AUT-P07-06 | Job completion attempted | Evaluate the completion gate — evidence, QC, signature, certification — and list precisely what is missing | Job stays open; nothing silently accepted |
| AUT-P07-07 | Job completed and customer paid | Settle through M53, credit the wallet as **held**, and show the release date | Settlement queued; wallet shows pending |
| AUT-P07-08 | Dispute opened on a job | **Block the payout entirely** for that job, notify the seller, and open the evidence window | Hard block |
| AUT-P07-09 | Dispute resolved | Release or adjust the held amount per the adjudication, with the outcome and reasoning shown to the seller | Manual release by Finance |
| AUT-P07-10 | Hold period elapses with no dispute | Move the amount to available and notify the seller | Retry; balance visible either way |
| AUT-P07-11 | Payout requested | Verify MFA, check no dispute is open, and execute on the settlement schedule | Request held with the reason shown |
| AUT-P07-12 | Scorecard crosses threshold 1 | Notify the seller **before** reducing visibility, with the measure, the gap and the recovery required | Notify then apply; never apply silently |
| AUT-P07-13 | Scorecard crosses threshold 2 | Notify, then suspend listings; allow open jobs to complete | Notify then apply |
| AUT-P07-14 | Certification or registration approaching expiry | Alert at 60, 30 and 7 days; suspend the affected categories on expiry | Alert then suspend |
| AUT-P07-15 | Policy or standard updated | Require acknowledgement before the next job acceptance | Block acceptance pending acknowledgement |
| AUT-P07-16 | Bank detail change submitted | Hold for out-of-band verification and exclude from the next payout run | Hold indefinitely rather than apply |
| AUT-P07-17 | Boost or advertising period ends | Report impressions, clicks and attributed jobs, and offer renewal | Report only |

---

## 12. Module Interfaces

### 12.1 Modules P07 Consumes

| Module | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, MFA on financial actions, seller scoping | OIDC via gateway |
| M28 Integration Platform | Every call; per-seller rate limits | Gateway |
| **M12 Marketplace & Seller Ecosystem** | Seller record, approval, listings, matching, broadcast, advertising, dispute | REST + events |
| M01 Service Order | Job context, execution, completion | REST + events |
| **M53 Revenue, Commission & Settlement** | Commission, wallet, hold, payout, statements | REST + events |
| M23 Quality | **The same QC checklist definitions applied to owned jobs** | REST |
| M22 Competency | Certification status, requirements, training launch | REST |
| M34 Customer Experience | Ratings, reviews, complaints | REST |
| M11 Pricing | Platform price bounds for listings | REST |
| M37 Catalogue | Service and product definitions for listings | REST |
| M15 / M38 | Parts purchase route for sellers | REST |
| M33 Party Master | Seller party identity | REST |
| M24 Documents | Verification documents and job evidence | REST |
| M27 Communications | Notification, in-job messaging, escalation | REST + WebSocket |
| M60 GRC | Policy versions requiring acknowledgement | REST |
| M65 Localisation | Bengali and English bundles | Build-time + REST |
| Accredited verification service (L6) | KYC/KYB identity verification | Embedded SDK via M12 |

### 12.2 What P07 Writes Back

| Target | What | Mechanism |
|---|---|---|
| M12 | Registration, profile, listings, bids, acceptance, advertising purchase, dispute | Command |
| M01 | Job execution events, diagnosis, parts, completion | Command / journal |
| M23 | QC results, test results, evidence | Command / journal |
| M53 | Payout requests | Command (MFA-gated) |
| M34 | Review responses | Command |
| M24 | Verification documents and job evidence media | Resumable upload |
| M22 | Training completion and acknowledgement | Command |
| M33 | Party profile updates | Command |
| M25 / M62 | Onboarding funnel, activity, retention and consequence analytics | Event stream |

### 12.3 Events P07 Consumes

| Event | Source | Effect in P07 |
|---|---|---|
| `mp.seller_approved` / `mp.seller_rejected` | M12 | Advance or close the application |
| `mp.job_broadcast` | M12 | Push the opportunity with its window |
| `mp.job_awarded` / `mp.bid_unsuccessful` | M12 | Release context or notify |
| `settlement.completed` | M53 | Credit the wallet as held with a release date |
| `settlement.released` | M53 | Move to available; notify |
| `mp.dispute_opened` / `mp.dispute_resolved` | M12 | Block or release the payout; show the outcome |
| `mp.scorecard_published` | M12 | Update the scorecard; apply graduated consequence |
| `certification.expiring` / `certification.expired` | M22 | Alert; suspend affected categories |
| `review.published` | M34 | Show the review; open the single response |
| `policy.updated` | M60 | Require acknowledgement before next acceptance |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P07-01 | Accredited identity verification service (NID/KYC, L6 per `02-05` §5) | Bidirectional | In-flow individual and business verification |
| INT-P07-02 | bKash / Nagad / bank rails | Outbound | Payout execution and registration fee collection; via M53 and M50 |
| INT-P07-03 | Firebase Cloud Messaging | Inbound | Job broadcast push with a short response window |
| INT-P07-04 | Google Maps Platform | Outbound | Service area definition, job location, navigation |
| INT-P07-05 | App stores | Outbound | Seller application distribution |
| INT-P07-06 | Device camera and GPS | Local | Evidence capture with geo and time stamps |

### 12.5 API Surface Consumed

| Endpoint | Method | Purpose | Owner |
|---|---|---|---|
| `/api/v1/mp/sellers/register` | POST | Registration by class | M12 |
| `/api/v1/mp/sellers/me/verification` | POST | In-flow KYC/KYB submission | M12 |
| `/api/v1/mp/sellers/me` | GET/PATCH | Profile, categories, service areas, availability | M12 |
| `/api/v1/mp/listings` | GET/POST/PATCH | Listing management, bulk operations | M12 |
| `/api/v1/mp/jobs/broadcast` | GET | Eligible broadcast jobs | M12 |
| `/api/v1/mp/bids` | POST | Quotation and counter-bid | M12 |
| `/api/v1/mp/jobs/{id}/accept` | POST | Accept an award | M12 |
| `/api/v1/service-orders/{id}` | GET/PATCH | Job execution and completion | M01 |
| `/api/v1/qc/records` | POST | QC checklist — the owned-job objects | M23 |
| `/api/v1/documents/upload` | POST | Evidence and verification documents | M24 |
| `/api/v1/mp/wallet` | GET | Balance: available, held, in dispute | M53 |
| `/api/v1/mp/payouts` | POST/GET | Request payout; history and remittance | M53 |
| `/api/v1/mp/scorecard` | GET | Performance with underlying jobs | M12 |
| `/api/v1/mp/disputes` | POST/GET | Raise and respond with evidence | M12 |
| `/api/v1/mp/advertising` | POST/GET | Boost purchase and performance | M12 |
| `/api/v1/competency/me` | GET | Certification status and requirements | M22 |

---

## 13. Roles & Permissions

**R38 External Party — Marketplace Seller sub-class** is the only role with P07 access
(`05-04` §2).

| Seller class | Access | Scope | MFA |
|---|---|---|---|
| **Freelance engineer** | C R U | Own profile, listings, bids, jobs, wallet, scorecard, disputes | **Required for financial actions** |
| **Shop** | C R U | As above, plus own stock declaration and multiple named operators under one seller account | **Required for financial actions** |
| Shop operator (sub-user) | C R U | Job execution only; no wallet, no payout, no bank details | Inherits |

> **Internal roles governing the marketplace act in P03**, not P07: **R24 Marketplace
> Operations Officer** (seller approval, disputes, scores, payout holds — Marketplace Console),
> **R26 Finance Manager** (held and disputed payouts), **R32 Quality Manager / ISO Coordinator** (marketplace QC
> and rework). **No impersonation path into P07 exists.**

**Field-level restrictions.** A seller sees their own gross value, commission, fees and net
earning. They never see 1000FiX internal cost or margin, another seller's bid or earnings,
another seller's rating detail, or any customer data beyond the job they hold.
`seller_kyc_document` is visible to R24, R26 and R32 only (`05-04` §5).

**Segregation of duties.** **SOD-06** — approve marketplace seller + approve their payout — is a
hard block in `05-04` §6 and is enforced on the internal side in P03. P07 supports it by keeping
approval and payout as distinct, separately-attributed actions.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Onboarding funnel** | Started, phone verified, documents submitted, verified, approved, agreement executed, first job — with the drop-off step | M12, M25 — the `04-00` completion KPI |
| **Seller activity** | Monthly active among approved; jobs per active seller; time to first job | M12, M25 |
| **Retention** | Cohort retention at 3, 6 and 12 months — the `04-00` KPI | M12, M25 |
| Bid behaviour | Bids per broadcast, win rate, decline reasons, expired opportunities | M12 |
| **Quality parity** | Marketplace QC compliance, rework and rating **against owned-job baselines** — the measure that proves the standard is real | M23, M25 |
| Completion gate failures | Which gate item blocked completion, by seller and category | M23 |
| Payout experience | Time held, disputes per 100 jobs, payout request to receipt | M53 |
| Consequence events | Visibility reductions and suspensions, and recovery rate afterwards | M12 |
| Advertising | Boost purchases, impressions, clicks, attributed jobs and return | M12 |
| Support and escalation | In-job escalations to 1000FiX, by reason | M27 |
| Application performance | Crash-free rate, offline duration, sync success on the seller application | M30 |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W8 Target | W9 Target |
|---|---|---|---|---|
| — | **Approved active sellers** | 0 | **500 by end of W8** | 900 |
| — | **Seller onboarding completion rate** | n/a | **> 60% of started registrations** | > 68% |
| — | **Seller monthly active rate** | n/a | **> 70% of approved sellers** | > 75% |
| — | **Average seller rating** | n/a | **> 4.4/5** | > 4.5/5 |
| — | **Seller retention at 12 months** | n/a | baselined | **> 65%** |
| — | Marketplace share of total job volume | 0% | 18% | **≥ 25%** |
| — | Marketplace QC compliance versus owned-job baseline | n/a | **parity** | **parity** |
| — | Marketplace rework rate versus owned-job baseline | n/a | ≤ owned + 2 pts | **≤ owned** |
| — | Disputes per 100 marketplace jobs | n/a | < 4 | **< 2** |
| — | Disputes resolved within the published window | n/a | 90% | **98%** |
| — | Payouts released on the published schedule | n/a | 97% | **99.5%** |
| — | Sellers suspended for performance | n/a | baselined | **falling trend** |
| — | Sellers recovering after reduced visibility | n/a | 40% | **> 55%** |
| — | Verification completed in-flow without redirect | n/a | **100%** | **100%** |
| — | Bengali string completeness | n/a | **100%** | **100%** |
| — | Cross-seller data exposures | n/a | **0** | **0** |

> **Register note.** The first five metrics are adopted verbatim from `04-00` §P07. P07 has
> **no KPI-0nn identifiers allocated**; all sixteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action.
>
> **Wave note.** P07 lands in W7 (Months 27–30), so its targets are stated at W8 and W9.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L5 | **Next.js 15 web** — registration and verification, profile, listings, wallet, statements, scorecard, advertising, disputes | 52% |
| L5 | **React Native application** — job discovery, bidding, acceptance, execution, evidence capture, offline journal | 34% |
| L5 | Offline journal and sync — **reusing the P02 pattern and, where feasible, its implementation** | 8% |
| L4 | Shared design system; embedded verification SDK | 6% |

> **Reuse position.** The offline journal, idempotent replay and conflict handling built for P02
> in Wave 2 are reused here rather than rebuilt. P07 lands five waves later, and rebuilding that
> component would be the most expensive avoidable duplication in the portal suite.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-207** | `p07_seller_web` — registration with class-differentiated in-flow verification, agreement execution and transaction gate, profile and listings with bulk management, wallet and statements, payout request with MFA and bank-change control, performance scorecard with graduated consequence, reviews, boost and advertising, disputes, standards and training | Next.js 15 application | 22 PW |
| **CD-208** | `p07_seller_app` — job broadcast and response window, bidding, acceptance, execution to owned-job standard with forced evidence and QC, customer messaging and escalation, offline journal reusing the P02 pattern | React Native application | 12 PW |

> **CD register.** Two IDs, **CD-207…208**, claimed following CD-206 (P06). All CD IDs remain
> provisional pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M12 Marketplace & Seller Ecosystem** | The module behind the portal — seller record, matching, broadcast, advertising, dispute. **W7, the binding constraint** |
| **M53 Revenue, Commission & Settlement** | Commission, wallet, hold and payout. **W4/W7 — no marketplace without settlement** |
| M29 Identity & Security | Seller identity, MFA on financial actions |
| M28 Integration Platform | Gateway with per-seller credentials |
| M01 Service Order | A marketplace job is a service order |
| **M23 Quality** | The QC checklist objects that make the parity standard real (W5) |
| **M22 Competency** | Certification, without which the category gate cannot be enforced (W5) |
| M34 Customer Experience | Ratings, reviews and complaints (W4) |
| M11 Pricing | Platform price bounds (W3/W7) |
| M60 GRC | Policy versioning and acknowledgement (W6) |
| **P02** | The offline journal and sync engine, reused here (W2) |
| Accredited verification service | An L6 commercial component per `02-05` §5 — **contracted before build** |

### 16.4 Seller Acquisition & Rollout

| Stage | Scope | Wave |
|---|---|---|
| Pilot cohort | 30–50 sellers in Dhaka, hand-onboarded, across three service categories | W7, month 28 |
| Category expansion | Additional categories as certification content matures with M22 | W7–W8 |
| Geographic expansion | Cities where owned capacity is thin, then underserved districts | W8 |
| Scale | Toward 500 approved active by end of W8 | W8 |

> **Acquisition position.** The pilot cohort is **hand-onboarded and personally supported**,
> because the onboarding funnel cannot be optimised before it has been observed, and the first
> fifty sellers determine the reputation that drives the next five hundred. A marketplace opened
> to self-service registration before its funnel, standards and dispute process are proven
> produces a cohort of poor experiences that is very difficult to recover from.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A seller cannot transact until verified, agreement-executed and approved — tested at every transactional endpoint, not merely at login | Negative test across all transactional APIs |
| AC-02 | Verification completes inside the portal with no off-platform redirect, for both engineer and shop classes | End-to-end onboarding test per class |
| AC-03 | The QC checklist, forced evidence points and signature requirement on a marketplace job are the **same configuration objects** as an owned job | Configuration diff between owned and marketplace job types |
| AC-04 | A job cannot be completed without evidence, QC, signature and a current certification for the category | Four negative tests at the completion gate |
| AC-05 | A seller cannot accept work in an uncertified category | Negative test with M22 |
| AC-06 | A payout is blocked entirely while a dispute is open on that job | Scripted dispute scenario with M53 |
| AC-07 | The hold period, risk tier and progression rule are shown to the seller at onboarding and on every held amount | Onboarding and wallet review |
| AC-08 | MFA is enforced for payout request, bank change and advertising purchase | Authentication test per action |
| AC-09 | A bank detail change is held for out-of-band verification and excluded from the next payout run | Scripted scenario with M53 |
| AC-10 | A seller cannot see another seller's bid, earnings, jobs, listings or rating detail | Tenant-isolation penetration test |
| AC-11 | Customer contact and address are released only on acceptance and expire after the bounded window | Data-retention test |
| AC-12 | Crossing threshold 1 notifies the seller **before** visibility reduces; crossing threshold 2 notifies before suspension | Scripted scorecard scenarios |
| AC-13 | Job execution and evidence capture survive a full connectivity loss and sync without data loss | Offline test with 20 sellers |
| AC-14 | The seller application runs acceptably on a mid-range Android device and the web surface at 3G | Performance test on the target device class |
| AC-15 | Every string including every error renders in Bengali, and Bengali is the default | Translation coverage report |
| AC-16 | WCAG 2.1 AA, usable from 320 px upward | Automated scan plus manual audit |
| AC-17 | Marketplace QC compliance and rework reach parity with owned-job baselines | Six months of comparative quality reporting |
| AC-18 | Onboarding completion exceeds 60% of started registrations | Funnel report over six months |
| AC-19 | 500 approved active sellers by end of W8 | Seller register |
| AC-20 | No P07 payload contains 1000FiX internal cost, margin or another seller's data | Automated payload inspection |
| AC-21 | CCO, Marketplace Operations Officer, Quality Manager and ten pilot sellers sign off UAT, conducted in Bengali | Signed UAT record |

**Definition of done:** the four governance requirements in `04-00` §P07, the twelve
cross-portal standards in `04-00` §3, plus the 21 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Which accredited identity-verification provider is contracted, at what per-check cost, and does it support both NID (individual) and trade licence (business) verification? | CCO / CTO / CFO | **W7 minus 6 months** |
| Q-02 | What is the commission rate by category, and is it published to sellers at onboarding? | CCO / CFO | **W7 design** |
| Q-03 | What are the payout hold periods by risk tier, and what triggers progression? | CFO / CCO | **W7 design** |
| Q-04 | What are the performance thresholds for reduced visibility and suspension, and who may override a suspension? | CCO / Quality Manager | W7 design |
| Q-05 | Is a registration fee charged? A fee improves seller quality and suppresses onboarding volume; the trade-off is commercial | CCO | W7 design |
| Q-06 | Who bears the cost of a customer-side loss on a marketplace job — the seller, the platform, or shared, and under what insurance? | CFO / Legal / CCO | **W7 design** |
| Q-07 | Which service categories open first, and does certification content exist in M22 for each? | Quality Manager / HR Director | W7 minus 4 months |
| Q-08 | Do marketplace sellers buy parts from 1000FiX, and at what price relative to internal cost? | CCO / Warehouse Manager | W7 design |
| Q-09 | Is a seller's tax withholding the platform's obligation under Bangladesh rules, and at what rate? | CFO / Legal | **W7 design** |
| Q-10 | Can a shop have multiple operators under one seller account, and how is accountability attributed between them? | CCO / Legal | W7 design |
| Q-11 | What customer data may a seller retain after job completion, and for how long? | Legal / CTO | W7 design |
| Q-12 | Is the marketplace visible to customers as distinct from owned service, or presented identically? This is a brand and a legal disclosure question | CCO / Legal | **W7 design** |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §P07 (capability set, **four
governance requirements**, KPIs), §1, §3 PS-01…PS-12, §4 ·
`P01_Customer_Self_Service_Portal_and_Mobile_Application.md` (the buyer side) ·
`P02_Technician_Mobile_Application.md` (**the offline journal pattern reused here**) ·
`P03_Admin_Operations_Portal.md` (Marketplace Console — the internal governance surface) ·
`P05_Vendor_and_Supplier_Portal.md` (boundary: supplier versus seller) ·
`P12_Partner_and_Referral_Portal.md` (boundary: referrer versus seller) ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 (AS-13, AS-14) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5 (L6 identity verification for M12) ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md`
§1 (R38), §2, §5 (`seller_kyc_document`, `commission_rate`), §6 **SOD-06**, §7, §8 ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §6.2 (BDT 84 lac), §Assumptions (≥ 25% of job volume) ·
`00_Governance_and_Charter/00-03_Scope_Expansion_Delta_v1_to_v2.md` §M12

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-QMS-005 (QC enforcement,
applied identically to marketplace work) ·
`1000FiX_Services_Company_Profile.md` §Partner Alliance Program

**External benchmark**
[Marketplace seller onboarding with KYB — verifying the entity and its owners before enabling settlement](https://didit.me/blog/marketplace-seller-kyb-onboarding-id/) ·
[KYC for the gig economy and online marketplaces](https://idenfy.com/blog/kyc-for-gig-and-online-marketplaces/) ·
[Know your seller — why marketplaces verify identities](https://www.middesk.com/blog/know-your-seller) ·
[Marketplace payments complete guide — split payments, escrow and delayed payouts](https://www.sharetribe.com/academy/marketplace-payments/) ·
[Securing marketplace payments — risk-based payouts releasing established sellers faster](https://www.journeyh.io/blog/how-secure-payments-on-marketplaces) ·
[Embedded escrow for marketplaces](https://paykeeper.com/marketplaces/) ·
[Marketplace payments compliance lessons](https://www.liquidtrust.io/blog/five-lessons-marketplace-compliance) ·
[Choosing a marketplace payment gateway](https://www.journeyh.io/blog/marketplace-payment-101-choosing-the-best-gateway-for-your-business)

---

*Portal P07 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
