---
id: FIX-ERP2-M12
module_id: M12
module_code: MKP
module_name: Marketplace & Seller Ecosystem
category: C — Commercial, Pricing & Revenue
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

# M12 — Marketplace & Seller Ecosystem
### Category C · Code `MKP` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M12 |
| **Module code** | `MKP` |
| **Category** | C — Commercial, Pricing & Revenue |
| **Status** | Existing (re-scoped — own-inventory e-commerce moved to M38; the module is now purely the third-party seller ecosystem) |
| **Priority** | **P1** |
| **Delivery wave** | W7 (Months 27–30) |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Marketplace Squad |
| **Delivery layers** | L2 (OCA `partner_*`, `queue_job`) + L4 (Next.js / React Native seller app) + L5 (custom — the largest custom build in Category C) |
| **Custom modules** | `cd_seller_onboarding`, `cd_listing`, `cd_job_broadcast`, `cd_seller_performance`, `cd_dispute`, `cd_seller_settlement`, `cd_seller_ads` |
| **Requirement range** | FR-MKP-001 … FR-MKP-078 |
| **Requirement count** | **78** *(measured; register estimate 62)* |
| **Effort estimate** | **50 person-weeks** *(measured; register estimate 40 PW)* — the largest module in Category C |
| **Depends on** | M38 E-Commerce · M37 Catalogue · M11 Pricing · M33 Party Master · M01 SRM · M53 Revenue & Settlement · M20 Receivable · M51 Tax · M29 Identity · M28 Integration · M24 Document |
| **Depended on by** | M01, M03, M20, M53, M23, M34, M40, M25, M26, M15 · Portal **P07** |

---

## 2. Purpose

M12 is how 1000FiX **grows service capacity without hiring technicians**.

It is a two-sided platform on which external engineers and independent repair shops register,
are verified, list their services and parts, bid for broadcast jobs, execute work under the
1000FiX brand and quality standards, and are paid a share of the value less commission. The
business plan targets **500 approved sellers** and **25% of total job volume** delivered by
external capacity.

The module owns everything about that supply side: onboarding and KYC, listings, job broadcast
and award, seller execution oversight, ratings and reviews, performance consequences, disputes,
commission definition, payout instruction, and the paid-promotion products sellers buy to gain
visibility.

The distinction from M38 is absolute and is drawn in the category overview §4.3: on M12 **the
seller is a third party**. Inventory is seller-declared, revenue to 1000FiX is commission and
fees rather than the full sale value, liability is shared per the seller agreement, and the VAT
treatment is a formal principal-versus-agent decision with restatement risk if it is wrong.

### Why It Exists

1000FiX can serve only as many customers as it has technicians. The business plan's growth
assumptions exceed what owned headcount can deliver, particularly outside the 51+ branch
footprint. Bangladesh has a large population of independent repair engineers and small shops
with capacity, no brand, no customer acquisition channel and no payment infrastructure. The
marketplace connects the two.

It also creates two revenue streams that do not exist today: **marketplace commission and
settlement** (stream 13) and **advertising, boost and lead placement** (stream 14), together
attributed **BDT 84 lac/year** in the business case.

The risk register is equally clear about the downside. Two of the category's three Critical
risks belong to this module: getting the VAT and liability model wrong, and letting marketplace
quality failures damage a brand built on 17+ manufacturer authorisations. The module is designed
around those two risks.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Service App SOW §Marketplace | Seller registration, listings, job broadcast, bidding, ratings, disputes, commission, boost and advertising — the primary source specification |
| Service App SOW §Seller Agreement | Terms, commission and standards as a signed agreement |
| ERP BRD §8.12 (BR-ECM-*) | Marketplace transactions, seller settlement |
| ERP URD §11 (US-MKP-*) | Seller and marketplace operations stories |
| Business Plan §Marketplace | 500 sellers, 25% of job volume, commission and advertising revenue |
| Executive Summary §3 streams 13–14 | Marketplace commission and advertising as committed revenue streams |
| `04-00` P07 Marketplace Seller Portal | The complete seller-facing capability set and governance requirements |
| `05-04` §6 SOD-06, §8 EA-04 | Seller approval and payout cannot be the same person; seller data access limits |
| `_CATEGORY_OVERVIEW.md` §4.3, §10 (RSK-022) | The E-Commerce/Marketplace boundary and the two Critical risks |
| NBR guidance on e-commerce VAT | 5% VAT applies to the commission or service charge of online platforms, not to the goods value where the platform acts as agent — the basis of the principal/agent decision |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Seller registration for two seller types: freelance engineer and shop/business |
| 2 | KYC and verification: NID, trade licence, TIN/BIN, references, work samples, address, bank account |
| 3 | Seller agreement issue, digital signature, versioning and re-acceptance on change |
| 4 | Seller categories, skills, service areas, working hours and capacity declaration |
| 5 | Seller approval workflow, provisional status, probation and graduation |
| 6 | Seller tiers and the benefits, obligations and commission rates attached to each |
| 7 | Listings: service listings and product listings, with seller-declared price and availability |
| 8 | Listing moderation, prohibited-item control and content standards |
| 9 | Seller-declared stock and its clear separation from 1000FiX-owned inventory |
| 10 | **Job broadcast**: publishing an eligible job to matching sellers |
| 11 | **Bidding and award**: seller quotations, counter-bids, customer or system award, award rules |
| 12 | Direct booking of a seller by a customer where the model permits |
| 13 | Seller job execution oversight: acceptance, evidence, checklists, completion, customer sign-off |
| 14 | Quality standards parity: marketplace jobs meet the same evidence and QC standards as owned work |
| 15 | Ratings and reviews, two-sided where applicable, with moderation and seller response |
| 16 | Seller performance scoring, thresholds, automatic visibility reduction, suspension and removal |
| 17 | Disputes: customer↔seller, seller↔1000FiX; evidence, mediation, decision, remedy |
| 18 | Commission scheme definition by category, tier, value band and promotion |
| 19 | Fee definition: listing fees, registration fees, payment-processing pass-through, cancellation fees |
| 20 | Seller wallet, earnings statement, payout eligibility, hold periods and payout instruction |
| 21 | **Paid promotion**: boost, top-listing placement and page-targeted advertising as purchasable products |
| 22 | Seller training, standards acknowledgement and certification requirements per category |
| 23 | Seller communication: broadcast notices, policy updates, in-job messaging with the customer |
| 24 | Marketplace trust and safety: fraud detection, collusion detection, off-platform-transaction detection |
| 25 | Marketplace analytics: supply, demand, liquidity, match rate, fill rate, seller cohort economics |
| 26 | The P07 Marketplace Seller Portal and App domain logic |
| 27 | The **principal-versus-agent determination record** and its consequences for revenue and VAT treatment |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| 1000FiX's own storefront, cart, checkout and payment orchestration | **M38** E-Commerce | One commerce core; M12 supplies third-party supply into it |
| Item definitions and category taxonomy | **M37** Catalogue | Seller listings reference the taxonomy; they do not define it |
| 1000FiX's own prices | **M11** Pricing | A seller sets their own listing price; M11 prices only 1000FiX's fees and commissions |
| Commission *calculation and payout execution* | **M53** Revenue & Settlement | M12 defines the scheme; M53 computes and pays *(category boundary map)* |
| Invoice, credit note, receipt, receivable and payable posting | **M20** / **M52** | Only Category G creates financial documents |
| VAT rates and NBR filing | **M51** Tax | M12 records the principal/agent determination; M51 applies it |
| The service order lifecycle | **M01** SRM | A marketplace job is a service order with an external executing party |
| Physical logistics | **M03** Logistics | Where 1000FiX logistics is used at all |
| Brand partner, alliance, referral and franchise relationships | **M40** Partner | A marketplace seller is not a channel partner |
| Supplier and procurement relationships | **M16** / **M42** | Buy-side |
| Technician competency for *owned* staff | **M22** Competency | Seller certification is governed here; employee competency is HR |
| Quality investigation and CAPA | **M23** Quality | M12 raises quality events; M23 investigates |
| Customer identity and consent | **M33** Party Master | Sellers are parties in M33; their marketplace attributes are M12's |
| Payment gateway contracts and settlement banking | **M50** Treasury | M12 instructs; treasury executes |

### 3.3 Shared Concepts

| Concept | M12's Role | Owning Module |
|---|---|---|
| Seller | **Owner** of the marketplace profile; M33 owns the party record | M12 (profile) / M33 (party) |
| Listing | **Owner** | M12 |
| Job broadcast, bid, award | **Owner** | M12 |
| Marketplace job | Creates; M01 owns the service order | M12 → M01 |
| Commission scheme | **Owner** of the definition; M53 computes | M12 (scheme) / M53 (calculation) |
| Seller wallet and payout | **Owner** of eligibility and instruction; M53/M52 execute | M12 (instruction) / M53 (execution) |
| Rating and review | **Owner** for sellers; M34 owns 1000FiX service feedback | M12 |
| Dispute | **Owner** for marketplace disputes; M34 owns complaints about 1000FiX | M12 |
| Seller agreement | References; M08 holds the agreement instance | M08 (agreement) / M12 (conduct) |
| Storefront and checkout | Consumes M38's commerce core | M38 |
| Principal/agent determination | **Owner** of the record; M51 applies the tax consequence | M12 (record) / M51 (tax) |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Service marketplaces** (Urban Company, TaskRabbit, Thumbtack class) | Supply verification, job broadcast and matching, seller scoring with automatic consequence, two-sided ratings, take-rate economics | **Job broadcast with skill-, area- and rating-based matching**, and **automatic consequence on performance thresholds** rather than discretionary intervention — the mechanism that keeps quality from drifting as supply scales | Their pure-gig model; 1000FiX carries brand liability that a neutral platform does not |
| **Product marketplaces** (Amazon, Daraz, Flipkart) | Seller onboarding and KYC, listing moderation, prohibited items, buyer protection, dispute resolution, payout hold periods, seller advertising | **Payout hold periods with dispute-driven blocking**, **listing moderation with prohibited-item control**, and **seller advertising as a distinct revenue product** | Their scale-oriented arbitration machinery; a mediation queue with clear rules is proportionate here |
| **Stripe Connect / marketplace payment platforms** | Connected-account onboarding, hosted KYC, escrow-style balance, platform fee capture, payout scheduling, dispute routing with fund recovery | **The escrow-and-hold model**: funds held for a configurable period, released on completion and dispute expiry, recoverable on chargeback. Also **KYC as a gating precondition to transacting** | Adopting a single foreign PSP wholesale — Bangladeshi payout runs through bKash, Nagad and local banking, so the escrow and payout logic must be ours |
| **Odoo / OCA marketplace and commission modules** | `sale_commission` family — commission by pricelist, product, category, with rules and fallbacks | The **commission-rule model** (by category, product and tier with a fallback percentage) as the L2 base for scheme definition | Treating commission calculation as a sales-commission problem; M53 computes marketplace settlement, which is a different money flow |
| **Gig-platform trust and safety practice** | Identity verification, background checks, off-platform-transaction detection, collusion detection, review-manipulation detection | **Off-platform leakage detection and collusion signals** — in a market where cash-in-hand is the norm, disintermediation is the single largest commercial threat to a marketplace | Aggressive surveillance approaches incompatible with PDPA 2026 and with treating sellers as partners |
| **Bangladesh e-commerce VAT practice (NBR)** | 5% VAT on the commission or service charge of online platforms; platform obligations where goods are supplied without VAT paid at source | **The principal/agent determination as a formal, documented, externally-advised decision** taken before build, with the revenue and VAT treatment derived from it — recorded as risk RSK-022 | Deferring the decision to implementation, which is precisely how restatement risk materialises |

**Design position.** 1000FiX differs from every consumer marketplace benchmark in five ways, and
each difference exists because this marketplace carries a brand that manufacturers audit.

First, **quality standards are identical to owned work, not lighter**. A marketplace job requires
the same evidence pack, the same before/after photographs, the same QC checkpoints and the same
customer sign-off as a job done by a 1000FiX technician *(P07 governance requirement)*. This is
non-negotiable: the category risk register rates marketplace quality failure as Critical because
it endangers the 17+ authorisations the core business depends on.

Second, **1000FiX is an accountable intermediary, not a neutral notice board**. When a
marketplace job fails, the customer's counterparty is 1000FiX in their perception whatever the
agreement says. The dispute process is therefore designed for 1000FiX to remedy first and
recover from the seller second — a stance most platforms avoid and this one cannot.

Third, **the principal/agent decision is a gate, not a detail**. No build starts on settlement,
invoicing or VAT until an external tax and legal opinion is documented. The risk register
requires this three months before build; this specification treats it as a blocking prerequisite.

Fourth, **disintermediation is designed against, not ignored**. Sellers meeting customers
through the platform and then transacting in cash is the dominant failure mode of service
marketplaces in cash economies. The counter-measures are structural — value delivered through
the platform (warranty, dispute protection, guaranteed payment, lead flow, ratings that
compound) — supported by detection, not by surveillance alone.

Fifth, **the seller experience is built for a smartphone and low literacy in English**. Sellers
are independent engineers, not e-commerce merchants. Registration, bidding, evidence capture and
earnings must work in Bengali on a mid-range Android phone, offline-tolerant, with the same
rigour applied to the technician app.

---

## 5. Functional Areas & Features

### 5.1 Seller Onboarding & Verification

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKP-001 | Two seller types | Support registration as an individual freelance engineer or as a shop/business, with different document and verification requirements | P0 | L5 |
| FR-MKP-002 | Registration flow | Provide a staged, resumable, Bengali registration flow on web and mobile, with progress preserved across sessions | P0 | L5 |
| FR-MKP-003 | Identity verification | Capture and verify NID, photograph, phone OTP and email; verify trade licence, TIN and BIN for businesses | P0 | L5 |
| FR-MKP-004 | Document management | Collect, store, expiry-track and re-request KYC documents through M24, at restricted access tier T5 | P0 | L5 |
| FR-MKP-005 | References and work samples | Capture references and work-sample images, and record their verification outcome | P1 | L5 |
| FR-MKP-006 | Bank and payout details | Capture and verify the payout destination (bank account, bKash, Nagad) with a penny-verification or equivalent check | P0 | L5 |
| FR-MKP-007 | Skills, categories and areas | Declare service categories, skills, device brands, service areas, working hours and daily capacity | P0 | L5 |
| FR-MKP-008 | Certification requirements | Enforce category-specific certification requirements, and block listing in a category until they are met | P0 | L5 |
| FR-MKP-009 | Seller agreement | Present the current agreement version, capture digital signature through M24, and require re-acceptance on material change | P0 | L5 |
| FR-MKP-010 | Registration fee | Collect a registration or annual fee where the model requires it, through M38 checkout | P2 | L5 |
| FR-MKP-011 | Approval workflow | Route the completed application for review and approval, with provisional, approved, probation and rejected outcomes and recorded reasons | P0 | L5 |
| FR-MKP-012 | Onboarding training | Require completion of platform standards training and acknowledgement before first job award | P1 | L5 |
| FR-MKP-013 | Seller tiers | Define tiers with entry criteria, commission rates, visibility weighting, payout frequency and obligations, with automatic movement between them | P1 | L5 |
| FR-MKP-014 | Registration expiry and renewal | Track registration and document expiry, notify in advance, and suspend transacting on lapse | P1 | L5 |
| FR-MKP-015 | Seller profile | Maintain the public seller profile — name, photograph, categories, areas, rating, completed jobs, response time — with moderation | P0 | L5 |
| FR-MKP-016 | Shop open/closed and availability | Let a seller set availability, holiday mode and capacity, and reflect it in matching | P1 | L5 |

### 5.2 Listings & Catalogue Participation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKP-017 | Service listings | Create service listings against the M37 category taxonomy with seller-declared price, scope, duration and area | P0 | L5 |
| FR-MKP-018 | Product listings | Create product listings for seller-owned parts and accessories with declared stock, condition and warranty | P1 | L5 |
| FR-MKP-019 | Seller-declared stock | Track seller-declared stock separately from 1000FiX inventory, with no commingling in M15 | P0 | L5 |
| FR-MKP-020 | Listing moderation | Moderate listings against content standards before publication, with automated screening and human review of exceptions | P0 | L5 |
| FR-MKP-021 | Prohibited items and categories | Maintain and enforce a prohibited list — counterfeit parts, restricted goods, categories requiring authorisation the seller lacks | P0 | L5 |
| FR-MKP-022 | Bulk listing management | Create, update and enable/disable listings in bulk, with per-row validation | P1 | L5 |
| FR-MKP-023 | Listing quality scoring | Score listings for completeness and quality, and weight visibility accordingly | P2 | L5 |
| FR-MKP-024 | Price sanity control | Flag listing prices materially outside the category norm for review, without setting the seller's price | P1 | L5 |
| FR-MKP-025 | Listing lifecycle | Enforce draft → in review → active → paused → withdrawn, with reasons and history | P0 | L5 |
| FR-MKP-026 | Storefront presentation | Present marketplace listings within the M38 storefront with unambiguous seller attribution and the applicable protections | P0 | L5 |

### 5.3 Job Broadcast, Bidding & Award

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKP-027 | Job eligibility | Determine which service orders may be offered to the marketplace, by category, value, brand authorisation, warranty status, customer consent and geography | P0 | L5 |
| FR-MKP-028 | Job broadcast | Publish an eligible job to matching sellers by skill, category, area, availability, rating and tier, with a declared broadcast window | P0 | L5 |
| FR-MKP-029 | Broadcast fairness | Apply declared, auditable fairness rules to broadcast ordering so visibility is not arbitrary, and record the ranking basis | P1 | L5 |
| FR-MKP-030 | Seller quotation and bid | Allow a seller to quote a price, ETA and scope against a broadcast job, and to revise it within the window | P0 | L5 |
| FR-MKP-031 | Counter-bid | Support a customer or 1000FiX counter-offer and a seller response | P2 | L5 |
| FR-MKP-032 | Award | Award the job by customer choice, automatic rule (best score) or operator decision, with the basis recorded | P0 | L5 |
| FR-MKP-033 | Award acceptance and expiry | Require seller acceptance within a window; on lapse, re-award automatically to the next candidate | P0 | L5 |
| FR-MKP-034 | Direct booking | Allow a customer to book a specific seller directly from a listing or profile where the model permits | P1 | L5 |
| FR-MKP-035 | Job reassignment | Reassign an accepted job on seller failure, with consequence applied to the seller and continuity for the customer | P0 | L5 |
| FR-MKP-036 | Capacity and concurrency limits | Limit concurrent awarded jobs per seller by tier and demonstrated capacity | P1 | L5 |
| FR-MKP-037 | Customer consent to marketplace fulfilment | Obtain and record explicit customer consent that a job will be performed by an external seller, with the implications stated | P0 | L5 |
| FR-MKP-038 | Data minimisation on award | Release the customer's name, contact and address to the seller only on award, and revoke access a defined period after completion *(EA-04)* | P0 | L5 |

### 5.4 Execution, Quality & Evidence

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKP-039 | Seller job execution | Provide the seller a job workspace with context, checklist, evidence capture, time recording and completion, in Bengali and offline-tolerant | P0 | L5 |
| FR-MKP-040 | Evidence parity | Require the same before/after photographs, diagnostic record and QC checklist as an owned job; block completion without them | P0 | L5 |
| FR-MKP-041 | Customer sign-off | Capture customer verification, signature or OTP at completion, with the same evidence standard as owned work | P0 | L5 |
| FR-MKP-042 | Parts provenance declaration | Require the seller to declare parts used, their provenance grade and any warranty, and surface it to the customer | P0 | L5 |
| FR-MKP-043 | 1000FiX parts supply option | Allow a seller to purchase parts from 1000FiX for a job, settled against their earnings | P2 | L5 |
| FR-MKP-044 | Escalation to 1000FiX | Let a seller or customer escalate a live job to 1000FiX operations, with takeover if required | P0 | L5 |
| FR-MKP-045 | Marketplace job warranty | Apply the declared warranty on marketplace work, state clearly who honours it, and route claims accordingly | P0 | L5 |
| FR-MKP-046 | In-job messaging | Provide moderated in-job messaging between seller and customer, retained as evidence, with contact-detail masking | P1 | L5 |
| FR-MKP-047 | Rework on marketplace jobs | Detect and route rework on marketplace work, applying seller consequence and preserving customer continuity | P1 | L5 |
| FR-MKP-048 | Field audit of sellers | Support M23/P11 audit of marketplace sellers against platform standards, with findings feeding the seller score | P1 | L5 |

### 5.5 Ratings, Performance & Consequence

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKP-049 | Customer ratings and reviews | Collect multi-parameter ratings and written reviews after completion, with verified-job attribution | P0 | L5 |
| FR-MKP-050 | Review moderation and response | Moderate reviews against policy and allow the seller one response per review | P1 | L5 |
| FR-MKP-051 | Review-manipulation detection | Detect rating manipulation — self-reviews, coordinated patterns, incentivised reviews — and act | P2 | L5 |
| FR-MKP-052 | Seller scorecard | Compute a composite score from acceptance rate, on-time rate, completion rate, rating, rework rate, dispute rate and evidence compliance | P0 | L5 |
| FR-MKP-053 | Automatic consequence ladder | Apply declared consequences automatically as the score crosses thresholds: reduced visibility, category restriction, suspension, removal | P0 | L5 |
| FR-MKP-054 | Probation and remediation | Place a seller on probation with a remediation plan, required training and a review date | P1 | L5 |
| FR-MKP-055 | Appeal against consequence | Allow a seller to appeal a consequence with evidence, decided by an operator who did not impose it | P1 | L5 |
| FR-MKP-056 | Seller-visible performance | Show the seller their own score, its components, their standing and the consequence of falling further | P0 | L5 |
| FR-MKP-057 | Recognition | Recognise high performers with visibility weighting, badges and tier advancement | P2 | L5 |

### 5.6 Disputes & Trust and Safety

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKP-058 | Dispute intake | Accept disputes from customer or seller with category, evidence and desired remedy | P0 | L5 |
| FR-MKP-059 | Dispute workflow | Manage a dispute through triage, evidence exchange, mediation, decision and remedy, with SLA at each stage | P0 | L5 |
| FR-MKP-060 | Payout hold on dispute | Block the payout of disputed value while a dispute is open | P0 | L5 |
| FR-MKP-061 | Remedy execution | Execute the decided remedy — rework, refund, partial refund, replacement, goodwill — instructing M20 and M01 as required | P0 | L5 |
| FR-MKP-062 | 1000FiX-first remediation | Where the customer's experience requires it, remedy at 1000FiX cost immediately and recover from the seller separately | P0 | L5 |
| FR-MKP-063 | Seller recovery | Recover the cost of a remedy from seller earnings or security deposit within declared limits, with notice and appeal | P1 | L5 |
| FR-MKP-064 | Off-platform transaction detection | Detect signals of disintermediation — contact exchange, cancellation patterns, repeat customer–seller pairs with no platform transaction — and act on policy | P1 | L5 |
| FR-MKP-065 | Collusion and fraud detection | Detect collusion between sellers, fake jobs, and payment fraud patterns, and route for investigation | P1 | L5 |
| FR-MKP-066 | Counterfeit-part control | Act on counterfeit or non-genuine part reports, with immediate listing suspension and investigation | P0 | L5 |
| FR-MKP-067 | Seller offboarding | Offboard a seller with settlement of outstanding earnings, retention of records, revocation of access and customer continuity for open jobs | P0 | L5 |

### 5.7 Commission, Settlement & Monetisation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKP-068 | Commission scheme definition | Define commission by category, seller tier, value band, job type and promotional period, with a declared fallback | P0 | L5 |
| FR-MKP-069 | Fee definition | Define listing fees, registration fees, cancellation fees and payment-processing pass-through | P1 | L5 |
| FR-MKP-070 | Seller wallet | Maintain a seller ledger of earnings, commission, fees, adjustments, recoveries and payouts, as an append-only record | P0 | L5 |
| FR-MKP-071 | Hold period and payout eligibility | Hold funds for the declared period after completion, release on expiry of the dispute window, and block on open dispute | P0 | L5 |
| FR-MKP-072 | Payout instruction | Instruct M53/M52 to pay eligible balances on the tier's payout schedule, to the verified destination | P0 | L5 |
| FR-MKP-073 | Seller statements | Produce a per-period statement showing every job, its value, commission, fees, adjustments and net, downloadable and in Bengali | P0 | L5 |
| FR-MKP-074 | Tax treatment on seller earnings | Apply the declared withholding and VAT treatment on seller earnings per the principal/agent determination, with M51 | P0 | L5 |
| FR-MKP-075 | Boost and top-listing | Sell time-boxed visibility boost and top-listing placement, priced by M11, purchased through M38 checkout | P1 | L5 |
| FR-MKP-076 | Advertising placements | Sell page- and category-targeted advertising with impression and click reporting | P2 | L5 |
| FR-MKP-077 | Promotion effect transparency | Mark promoted placements clearly to customers and never let a boost override a quality-based restriction | P0 | L5 |
| FR-MKP-078 | Marketplace analytics | Report supply and demand by category and area, liquidity, match rate, fill rate, take rate, seller cohort retention and unit economics | P0 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Two-sided identity isolation** | Seller identity and customer identity are separate principals under M29; a seller may also be a customer without any data crossing between the roles |
| T-02 | **Time-boxed data grants** | Customer contact data is granted to a seller on award and revoked automatically after the declared post-completion period, enforced at the record-rule layer *(EA-04)* |
| T-03 | **Broadcast fan-out at scale** | A job broadcast to 500 sellers delivers within 10 seconds, through push, SMS and in-app, with per-seller delivery tracking |
| T-04 | **Deterministic ranking** | Broadcast and search ranking is computed from declared, auditable factors; every ranking decision is reconstructible for a fairness audit |
| T-05 | **Wallet as an append-only ledger** | Seller balance is derived from movements; it is never edited. Every movement carries its source document |
| T-06 | **Payout idempotency** | A payout instruction is idempotent by (seller, period, batch); no double payment is possible under retry |
| T-07 | **Dispute-driven fund blocking** | Opening a dispute atomically blocks the disputed amount; closing it releases or recovers atomically |
| T-08 | **Offline-tolerant seller app** | Job acceptance, evidence capture and completion work offline with idempotent replay, to the same standard as P02 |
| T-09 | **KYC data at tier T5** | KYC documents are restricted-tier data: named allow-list access, step-up authentication, every access logged *(`05-04` §4)* |
| T-10 | **Contact masking** | In-job messaging masks phone numbers and detects contact-detail exchange without storing message content beyond the retention policy |
| T-11 | **Listing moderation pipeline** | Automated screening runs before publication; only exceptions reach humans; the queue never blocks compliant listings |
| T-12 | **Revenue treatment flag** | Every marketplace transaction carries an explicit principal/agent flag derived from the documented determination, and it drives both revenue recognition and VAT |
| T-13 | **Seller data portability and erasure** | A seller can obtain their data and request erasure within PDPA 2026 obligations, subject to statutory retention on transactions |
| T-14 | **Rate limiting and abuse control** | Registration, listing and bidding endpoints are rate-limited per identity and device to resist automated abuse |
| T-15 | **Performance envelope** | Broadcast delivery ≤ 10 s to 500 sellers · listing search ≤ 300 ms p95 · seller dashboard ≤ 1.5 s on 3G · payout batch of 2,000 sellers ≤ 15 min |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M12 |
|---|---|---|
| **1000FiX (as a business)** | Capacity is capped at owned technician headcount | Capacity extends to 500 external sellers without payroll, in areas with no branch |
| **Marketplace Operations Officer** | Role does not exist | Runs onboarding, moderation, disputes and seller performance from one console |
| **Customer** | Waits for a 1000FiX technician, or goes to an unvetted local shop with no recourse | Chooses a verified seller with a rating, a warranty and a dispute path |
| **External engineer** | Works cash-in-hand with no lead flow, no brand and no payment guarantee | Receives jobs, is paid reliably, builds a rating that compounds, and gains the 1000FiX association |
| **Dispatch manager** | Declines or delays jobs outside coverage | Broadcasts overflow and out-of-area jobs to the marketplace |
| **Quality manager** | Has no visibility of work done under the brand by outsiders | Sees marketplace evidence, QC and audit findings on the same standard as owned work |
| **Finance officer** | — | Settles seller payouts from a ledger with hold periods and dispute blocks, not from a spreadsheet |
| **CCO** | Growth requires hiring | Growth has a second lever: supply-side acquisition |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Marketplace commission and advertising** | Take rate on marketplace jobs plus boost, top-listing and advertising products | **BDT 84 lac/year** *(business case §6.2, revenue streams 13 and 14)* |
| **Capacity extension without payroll** | 25% of job volume delivered by external sellers | Removes the headcount ceiling on growth; **500 approved sellers** and **> 25% of job volume** *(category KPIs)* |
| **Geographic reach beyond 51+ branches** | Sellers operate where 1000FiX has no branch | Serves demand that is currently declined, and tests markets before capital is committed to a branch |
| **Overflow absorption** | Peak and out-of-area demand is broadcast rather than refused | Improves SLA attainment on owned work by removing overload, supporting the M01 **96% SLA** target |
| **Parts sales to sellers** | Sellers buying genuine parts from 1000FiX for their jobs | An additional channel for revenue stream 5, settled against earnings |
| **Customer retention** | A customer whose job cannot be served by 1000FiX is retained on the platform rather than lost to an independent shop | Contributes to the **BDT 78 lac/year** retention benefit |
| **Demand and supply intelligence** | Bid data reveals true market price and capacity by category and area | Improves M11 pricing and M43 capacity planning with data no internal source can produce |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Formalising an informal sector** | Verified identity, documented standards, recorded work and traceable payment bring independent engineers into a formal economy — with genuine social value and a real regulatory story |
| **Brand extension without capital** | Every marketplace job extends brand presence at negligible marginal cost |
| **Quality leverage across the industry** | Requiring platform standards of 500 external engineers raises the standard of repair work far beyond 1000FiX's own staff |
| **A recruitment pipeline** | High-performing sellers are pre-verified, pre-rated candidates for employment |
| **Resilience** | External capacity absorbs shocks — seasonal peaks, staff shortages, disruption — that owned capacity cannot |
| **Strategic optionality** | A functioning two-sided platform is a materially different asset from a service company, with different valuation and expansion characteristics |

> **Counterweight, stated honestly.** These benefits are conditional on the two Critical risks
> being controlled. A marketplace that damages the brand or produces a tax restatement destroys
> more value than it creates. The controls in §5.4, §5.6 and §9 are not optional hardening; they
> are the conditions under which the module should be built at all.

---

## 8. Lifecycle & State Model

M12 owns four lifecycles. **Seller** and **marketplace job** are shown in full.

### 8.1 Seller

```
   ┌───────────┐
   │ REGISTERED│ account created, application incomplete
   └─────┬─────┘
         │ documents and profile submitted
   ┌─────▼──────────┐
   │ PENDING REVIEW │──── rejected ──► REJECTED (reason; reapplication window)
   └─────┬──────────┘
         │ KYC verified, agreement signed, training complete
   ┌─────▼──────────┐
   │  PROVISIONAL   │ limited job value, closer monitoring
   └─────┬──────────┘
         │ probation criteria met (jobs, rating, evidence compliance)
   ┌─────▼──────────┐
   │    APPROVED    │◄──────── reinstated
   └─────┬──────────┘
         │
   ┌─────┼───────────────┬──────────────────┐
   ▼     ▼               ▼                  ▼
┌──────────┐   ┌──────────────┐   ┌────────────────┐
│ RESTRICTED│  │  PROBATION   │   │   SUSPENDED    │
│(category │   │ (remediation │   │ (transacting   │
│ or value │   │  plan)       │   │  blocked)      │
│ limits)  │   └──────┬───────┘   └───────┬────────┘
└────┬─────┘          │                   │
     └────────────────┴───────────────────┤
                                          │ terminal breach / voluntary exit
                                    ┌─────▼──────┐
                                    │ OFFBOARDING│ open jobs transitioned,
                                    └─────┬──────┘ earnings settled
                                          ▼
                                    ┌────────────┐
                                    │  REMOVED   │ records retained per policy
                                    └────────────┘

  Cross-cutting: EXPIRED (document or registration lapse) blocks transacting
  until remediated, without changing the underlying standing.
```

### 8.2 Marketplace Job

```
  ELIGIBLE ──► BROADCAST ──► BIDDING ──┬── no bids ──► RE-BROADCAST / WITHDRAWN
                                       │
                                       └── bids received ──► AWARDED
  AWARDED ──┬── not accepted in window ──► RE-AWARDED (next candidate)
            └── accepted ──► IN PROGRESS ──► EVIDENCE COMPLETE ──► CUSTOMER SIGN-OFF
  CUSTOMER SIGN-OFF ──► COMPLETED ──► HOLD PERIOD ──► SETTLED
  Any post-award ──► ESCALATED (1000FiX takeover) · DISPUTED (payout blocked)
                   · CANCELLED (reason and consequence recorded)
```

### 8.3 Dispute

```
RAISED ──► TRIAGED ──► EVIDENCE EXCHANGE ──► MEDIATION ──► DECIDED ──► REMEDY EXECUTED ──► CLOSED
   └──► WITHDRAWN                                   └──► APPEALED ──► FINAL DECISION
```

### 8.4 Listing

```
DRAFT ──► IN MODERATION ──┬── rejected ──► DRAFT (reason)
                          └── approved ──► ACTIVE ──► PAUSED ──► ACTIVE
                                              └──► WITHDRAWN (seller or platform)
```

### Transition Guards — Seller

| From | To | Guard | Actor |
|---|---|---|---|
| Registered | Pending Review | All mandatory documents and profile fields submitted | Seller |
| Pending Review | Provisional | KYC verified; payout destination verified; agreement signed; training complete | Marketplace Operations |
| Provisional | Approved | Minimum completed jobs, minimum rating, full evidence compliance, no upheld disputes | System |
| Approved | Restricted | Score below the category threshold, or a category certification lapsed | System |
| Approved / Restricted | Probation | Score below threshold with a remediation plan issued | Marketplace Operations |
| Any | Suspended | Terminal-severity breach, upheld serious dispute, or counterfeit-part finding | Marketplace Operations + CCO |
| Suspended / Probation | Approved | Remediation verified; appeal upheld | Operator ≠ the one who imposed it |
| Any | Offboarding | Terminal breach, or voluntary exit | Seller / Marketplace Operations |
| Offboarding | Removed | Open jobs transitioned; earnings settled; disputes closed; access revoked | System |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-MKP-01 | A seller cannot transact until KYC is verified, the agreement is signed and approval is granted *(P07 governance)* | **H** | CCO |
| BRU-MKP-02 | Quality and evidence standards for marketplace jobs are identical to owned jobs; a job cannot complete without them | **H** | Quality Manager |
| BRU-MKP-03 | Approving a seller and approving their payout cannot be done by the same person *(SOD-06)* | **H** | CFO |
| BRU-MKP-04 | Customer contact data is released only on award and revoked a defined period after completion *(EA-04)* | **H** | CTO |
| BRU-MKP-05 | Payouts are held for the declared period and blocked entirely while a dispute is open *(P07 governance)* | **H** | CFO |
| BRU-MKP-06 | Falling below the performance threshold reduces visibility automatically, then suspends *(P07 governance)* | **C** | CCO |
| BRU-MKP-07 | The customer must explicitly consent to marketplace fulfilment, with the implications stated, before a job is broadcast | **H** | CCO |
| BRU-MKP-08 | A job requiring brand authorisation the seller does not hold is never broadcast to that seller | **H** | Quality Manager |
| BRU-MKP-09 | Warranty work under a brand authorisation is never broadcast to the marketplace | **H** | Warranty Officer |
| BRU-MKP-10 | Seller-declared stock is never commingled with 1000FiX inventory in M15 | **H** | Inventory Manager |
| BRU-MKP-11 | A counterfeit-part finding suspends the listing immediately and the seller pending investigation | **H** | Quality Manager |
| BRU-MKP-12 | Paid promotion never overrides a quality-based restriction or suppression | **H** | CCO |
| BRU-MKP-13 | Promoted placements are clearly marked as promoted to the customer | **H** | CCO |
| BRU-MKP-14 | Every marketplace transaction carries an explicit principal/agent flag derived from the documented determination | **H** | CFO |
| BRU-MKP-15 | No settlement, invoicing or VAT logic is built before the external tax and legal opinion is documented *(RSK-022)* | **H** | CFO |
| BRU-MKP-16 | The seller wallet is an append-only ledger; balances are derived and never edited | **H** | CTO |
| BRU-MKP-17 | Recovery from seller earnings requires notice, a declared limit and a right of appeal | **H** | CCO |
| BRU-MKP-18 | An appeal is decided by an operator other than the one who imposed the consequence | **H** | CCO |
| BRU-MKP-19 | KYC documents are tier T5 data: allow-list access, step-up authentication, every access logged | **H** | CTO |
| BRU-MKP-20 | Where the customer experience requires it, 1000FiX remedies first and recovers from the seller separately | **C** | CCO |
| BRU-MKP-21 | A seller's registration or document lapse blocks transacting immediately | **C** | Marketplace Operations |
| BRU-MKP-22 | Broadcast ranking is computed from declared factors and every ranking decision is reconstructible | **H** | CCO |

*Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.seller` | `fix_seller` | Marketplace seller profile | partner_id, seller_type, code, state, tier_id, categories, areas, rating, completed_jobs, score, registered_at, expires_at, agreement_version |
| `fix.seller.kyc` | `fix_seller_kyc` | KYC records (T5) | seller_id, document_type, document_ref, number_masked, verified, verified_by, verified_at, expires_at, document_id |
| `fix.seller.payout.method` | `fix_seller_payout_method` | Verified payout destination | seller_id, method (bank/bKash/Nagad), account_masked, verified, verified_at |
| `fix.seller.capability` | `fix_seller_capability` | Skills and certification | seller_id, category_id, skill_id, certification_id, valid_until, verified |
| `fix.seller.availability` | `fix_seller_availability` | Working hours and capacity | seller_id, calendar_json, daily_capacity, holiday_mode, areas |
| `fix.seller.tier` | `fix_seller_tier` | Tier definitions | code, entry_criteria_json, commission_override_json, visibility_weight, payout_frequency, obligations_json |
| `fix.listing` | `fix_listing` | Service and product listings | seller_id, listing_type, category_id, item_ref, title_bn, title_en, description, price, availability, area_scope, state, quality_score |
| `fix.listing.moderation` | `fix_listing_moderation` | Moderation record | listing_id, screening_result, reviewer_id, decision, reason, at |
| `fix.seller.stock` | `fix_seller_stock` | Seller-declared stock | listing_id, declared_qty, condition, warranty_days, updated_at |
| `fix.job.broadcast` | `fix_job_broadcast` | Broadcast record | service_order_id, eligibility_basis, broadcast_at, window_minutes, candidate_ids, ranking_basis_json, state |
| `fix.job.bid` | `fix_job_bid` | Seller bids | broadcast_id, seller_id, price, eta, scope_note, state, submitted_at, revised_at |
| `fix.job.award` | `fix_job_award` | Award record | broadcast_id, bid_id, seller_id, awarded_by, basis, accepted_at, expires_at, reassigned_from |
| `fix.marketplace.job` | `fix_marketplace_job` | The marketplace transaction | service_order_id, seller_id, award_id, gross_value, commission, fees, net_to_seller, principal_agent_flag, state, completed_at, hold_until |
| `fix.seller.evidence` | `fix_seller_evidence` | Evidence compliance | job_id, artefact_type, artefact_ref, captured_at, compliant |
| `fix.seller.review` | `fix_seller_review` | Ratings and reviews | job_id, seller_id, partner_id, ratings_json, text, media_ids, moderation_state, seller_response, response_at |
| `fix.seller.score` | `fix_seller_score` | Composite performance | seller_id, period, acceptance_rate, ontime_rate, completion_rate, avg_rating, rework_rate, dispute_rate, evidence_compliance, composite, band |
| `fix.seller.consequence` | `fix_seller_consequence` | Applied consequences | seller_id, type, trigger, effective_from, effective_to, imposed_by, appeal_id, state |
| `fix.marketplace.dispute` | `fix_marketplace_dispute` | Disputes | job_id, raised_by, category, description, evidence_ids, state, sla_due, decision, remedy_type, remedy_value, decided_by, closed_at |
| `fix.commission.scheme` | `fix_commission_scheme` | Commission definitions | category_id, tier_id, value_band, job_type, rate_pct, min_fee, max_fee, promo_period, fallback, valid_from |
| `fix.marketplace.fee` | `fix_marketplace_fee` | Fee definitions | fee_type, scope_json, value, basis, valid_from |
| `fix.seller.wallet.movement` | `fix_seller_wallet_movement` | Append-only ledger | seller_id, movement_type (earning/commission/fee/adjustment/recovery/payout), amount, source_doc_ref, hold_until, at |
| `fix.seller.payout` | `fix_seller_payout` | Payout instruction | seller_id, period, gross, deductions, net, destination_ref, batch_id, idempotency_key, state, executed_at |
| `fix.seller.statement` | `fix_seller_statement` | Period statement | seller_id, period, lines_json, opening, closing, document_id |
| `fix.seller.promotion` | `fix_seller_promotion` | Boost and advertising | seller_id, promo_type, scope_json, start_at, end_at, price_paid, impressions, clicks, state |
| `fix.trust.signal` | `fix_trust_signal` | Fraud and leakage signals | subject_type, subject_id, signal_type, score, evidence_json, state, investigated_by, outcome |
| `fix.principal.agent.determination` | `fix_principal_agent_determination` | The formal record | scope (category/transaction_type), determination, basis, external_opinion_ref, effective_from, approved_by |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.party` (seller as a party) | M33 | Live read; M12 owns the marketplace profile |
| Category taxonomy, item definitions | M37 | Master data projection |
| Commission and fee *prices* | M11 | REST |
| Storefront, cart, checkout, payment | M38 | Commerce API |
| `fix.service.order` | M01 | Command + events |
| Settlement execution and payout | M53 / M52 | Command |
| Invoice, credit note, refund | M20 | Command |
| Tax treatment | M51 | REST |
| Seller agreement instance | M08 | Live read |
| Quality checklists, audit findings | M23 | Projection + events |
| Document storage and e-signature | M24 | Service call |
| Fraud and ranking models | M26 | Model output API |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-MKP-01 | Registration submitted | Run automated document checks, create the review task, notify the applicant of the expected decision time | Queue for manual review; notify the applicant |
| AUT-MKP-02 | KYC document approaching expiry | Notify the seller at 30, 14 and 7 days; block transacting on lapse | Escalate to Marketplace Operations |
| AUT-MKP-03 | Seller approved | Provision portal access, issue the agreement, assign onboarding training, set provisional limits | Create a manual provisioning task |
| AUT-MKP-04 | Eligible job created and customer consent recorded | Compute the candidate set, rank by declared factors, broadcast within the window, record the ranking basis | Retry; fall back to operator-assisted assignment |
| AUT-MKP-05 | Broadcast window closes with no bid | Re-broadcast with widened criteria, then escalate to operations for owned fulfilment | Escalate to dispatch |
| AUT-MKP-06 | Job awarded | Grant time-boxed customer data access, notify the seller, start the acceptance timer | Revoke and re-award; alert operations |
| AUT-MKP-07 | Award not accepted within the window | Re-award to the next candidate and record a non-acceptance against the seller's score | Escalate to operations |
| AUT-MKP-08 | Job completed with customer sign-off | Compute commission and fees, credit the wallet with the hold period, revoke customer data access at the declared interval | Hold the wallet movement; alert finance |
| AUT-MKP-09 | Evidence incomplete at completion attempt | Block completion and list the missing artefacts to the seller | — |
| AUT-MKP-10 | Hold period elapses with no dispute | Make the amount payout-eligible | Log; retry |
| AUT-MKP-11 | Dispute raised | Block the disputed amount atomically, triage, start the SLA clock, notify both parties | Escalate to the dispute officer |
| AUT-MKP-12 | Dispute decided | Execute the remedy, instruct M20/M01, release or recover the held amount, update the seller score | Escalate to Finance Manager |
| AUT-MKP-13 | Score crosses a consequence threshold | Apply the declared consequence automatically, notify the seller with the reason and the appeal route | Log; alert operations |
| AUT-MKP-14 | Payout schedule reached | Assemble eligible balances, deduct recoveries, produce statements, instruct M53/M52 idempotently | Hold the batch; alert finance; never partially pay |
| AUT-MKP-15 | Off-platform or collusion signal exceeds threshold | Create a trust-and-safety investigation with the evidence attached | Log; escalate on repetition |
| AUT-MKP-16 | Counterfeit-part report received | Suspend the listing immediately, notify the seller and Quality, and open an investigation | — |
| AUT-MKP-17 | Boost or advertising purchased | Activate the placement for the paid period and start impression/click accounting | Refund through M20; alert |
| AUT-MKP-18 | Seller offboarding initiated | Transition open jobs, settle earnings, close disputes, revoke access, retain records per policy | Escalate to operations; never strand a customer's open job |
| AUT-MKP-19 | Review submitted | Screen for policy breach and manipulation signals, publish or hold, notify the seller of their response right | Hold for moderation |
| AUT-MKP-20 | Rework detected on a marketplace job | Route the remedy, apply seller consequence, preserve customer continuity | Escalate to operations |

---

## 12. Interfaces

### 12.1 Upstream — M12 Consumes

| Source | What | Mechanism |
|---|---|---|
| M38 E-Commerce | Storefront, cart, checkout, payment orchestration for marketplace transactions and seller purchases | Commerce API |
| M37 Catalogue | Category taxonomy, item definitions, permitted listing scope | Master data projection |
| M11 Pricing | Commission rates, fee schedule, boost and advertising prices | REST |
| M33 Party Master | Seller and customer party records, consent | Live read |
| M01 SRM | Eligible service orders, job context, execution status, rework detection | Events + commands |
| M08 Contract | Seller agreement instance and standing | Live read |
| M23 Quality | Checklist templates, audit findings on sellers | Projection + events |
| M24 Document | KYC documents, agreements, e-signature, retention | Service call |
| M51 Tax | Tax treatment rules under the principal/agent determination | REST |
| M20 Receivable | Payment receipt and refund outcomes | Events |
| M26 AI/ML | Ranking, fraud, collusion and leakage models | Model output API |
| M22 Competency | Certification definitions used for seller category gating | Projection |

### 12.2 Downstream — M12 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 SRM | Marketplace jobs as service orders with an external executing party; award, completion and escalation events | Command + events |
| M53 Revenue & Settlement | Commission scheme, computed job economics, payout instructions | Command + projection |
| M52 Payable | Payout execution instructions | Command |
| M20 Receivable | Customer-side documents, refunds and remedies | Command |
| M51 Tax | Principal/agent flag per transaction | Projection |
| M23 Quality | Marketplace quality events, evidence compliance, rework, counterfeit findings | Events |
| M34 Customer Experience | Marketplace-originated satisfaction and complaint signals | Events |
| M15 Inventory | Parts sold to sellers for marketplace jobs | Command |
| M03 Logistics | Consignments where 1000FiX logistics serves a marketplace job | Command |
| M40 Partner | Distinction and cross-reference where a seller is also a channel partner | Projection |
| M35 Marketing | Seller acquisition funnel and supply-gap signals | Events |
| M25 BID · M26 AIM | Full marketplace fact stream: supply, demand, bids, awards, outcomes, disputes, economics | Warehouse extract |
| **P07 Seller Portal & App** | The complete seller experience | REST — the module's principal external surface |
| P01 Customer Portal | Marketplace listings, seller profiles, ratings, dispute raising | Via M38 commerce API |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `seller.registered` | seller id, type, categories, areas | M33, M25 |
| `seller.approved` | seller id, tier, categories, limits | M08, M29, M25 |
| `seller.suspended` / `seller.reinstated` | seller id, reason, effective, open job count | M01, M38, M53 |
| `seller.offboarded` | seller id, settlement ref, records retained | M53, M33, M29 |
| `listing.published` / `listing.withdrawn` | listing id, seller, category, reason | M38, M25 |
| `mp_job.broadcast` | service order, candidate count, window, ranking basis | M01, M25 |
| `mp_job.awarded` | service order, seller, price, ETA, data grant expiry | **M01**, M03, M27 |
| `mp_job.completed` | job id, seller, gross, commission, net, hold_until | M53, M20, M34 |
| `mp_job.escalated` | job id, reason, takeover required | M01, M27 |
| `dispute.raised` | dispute id, job, party, category, amount blocked | M53, M34, M27 |
| `dispute.decided` | dispute id, decision, remedy, recovery | M20, M01, M53 |
| `seller.score_changed` | seller id, composite, band, consequence applied | M53, M38, M25 |
| `seller.consequence_applied` | seller id, type, trigger, appeal route | M27, M25 |
| `payout.instructed` | seller id, period, net, batch, idempotency key | M53, M52 |
| `trust.signal_raised` | subject, signal type, score | M23, investigations |
| `promotion.activated` | seller id, promo type, period, price | M20, M53, M25 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-MKP-01 | NID verification service | Outbound | Seller identity verification |
| INT-MKP-02 | Trade licence / RJSC / BIN validation | Outbound | Business seller verification |
| INT-MKP-03 | bKash / Nagad disbursement | Outbound | Seller payouts *(via M52/M50)* |
| INT-MKP-04 | Bank disbursement / EFT | Outbound | Seller payouts to bank accounts |
| INT-MKP-05 | Payment gateways *(via M38)* | Inbound | Customer payment on marketplace transactions |
| INT-MKP-06 | SMS / push / WhatsApp | Outbound | Job broadcast delivery and seller notifications |
| INT-MKP-07 | Background-check provider *(optional)* | Outbound | Enhanced verification for high-trust categories |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/sellers/register` | POST | Staged seller registration | P07 |
| `/api/v1/sellers/{id}` | GET/PATCH | Seller profile and standing | P07, P03 |
| `/api/v1/sellers/{id}/kyc` | POST | KYC document submission (T5) | P07 |
| `/api/v1/sellers/{id}/approve` | POST | Approval decision | P03 |
| `/api/v1/listings` | GET/POST/PATCH | Listing management | P07, P03 |
| `/api/v1/listings/bulk` | POST | Bulk listing operations | P07 |
| `/api/v1/broadcasts` | GET | Jobs broadcast to this seller | P07 |
| `/api/v1/broadcasts/{id}/bid` | POST | Submit or revise a bid | P07 |
| `/api/v1/awards/{id}/accept` | POST | Accept an awarded job | P07 |
| `/api/v1/mp-jobs/{id}` | GET | Job workspace with context and checklist | P07 |
| `/api/v1/mp-jobs/{id}/evidence` | POST | Evidence capture (offline-replayable) | P07 |
| `/api/v1/mp-jobs/{id}/complete` | POST | Completion with customer sign-off | P07 |
| `/api/v1/mp-jobs/{id}/escalate` | POST | Escalate to 1000FiX | P07, P01 |
| `/api/v1/disputes` | GET/POST | Raise and manage disputes | P07, P01, P03 |
| `/api/v1/sellers/{id}/wallet` | GET | Wallet, movements and hold status | P07 |
| `/api/v1/sellers/{id}/statements` | GET | Period statements | P07 |
| `/api/v1/sellers/{id}/score` | GET | Scorecard with components and consequences | P07 |
| `/api/v1/promotions` | GET/POST | Buy and manage boost and advertising | P07 |
| `/api/v1/marketplace/analytics` | GET | Supply, demand, liquidity and economics | P03, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R24 Marketplace Operations Officer | C R U D A | Marketplace domain — onboarding, moderation, disputes, performance |
| R04 Chief Commercial Officer | C R U D A | All — suspension, policy, commission schemes |
| R03 Chief Financial Officer | R A | All — payouts, recovery limits, principal/agent determination |
| R26 Finance Manager | R U A | Payout batches, held payouts, recovery approval |
| R27 Finance Officer | R U | Payout processing and reconciliation |
| R32 Quality Manager / ISO Coordinator | R U A | Evidence compliance, counterfeit findings, seller audits |
| R05 Operations Director | R A | Job eligibility policy, escalations, takeovers |
| R07 Dispatch Manager | R U | Broadcast oversight and fallback to owned fulfilment |
| R23 Marketing Manager | R U | Seller acquisition campaigns, promotion products |
| R34 Contact Centre Agent | R U | Customer-side marketplace support and dispute intake |
| R33 IT / System Administrator | R U | Configuration, integrations, rate limits |
| R36 Customer | R, rate, dispute | Own marketplace jobs and reviews |
| **R38 Marketplace Seller** | C R U | **Own records only** — profile, listings, bids, awarded jobs, wallet, statements, disputes *(EA-04)* |
| — Dispute Officer *(new position under R24)* | C R U A | Disputes; cannot decide an appeal against their own decision |

**Field-level restrictions.** `seller_kyc_document` is restricted to R24, R26 and R32
*(`05-04` §5)* at tier T5 with logged access. `commission_rate` is restricted to R03, R04, R24
and R26. A seller never sees another seller's data, 1000FiX cost or margin, or any customer data
beyond an awarded job within its grant window.

**Segregation of duties.** **SOD-06** — approving a seller and approving their payout is a hard
block *(`05-04` §6)*. Additionally, an appeal must be decided by an operator other than the one
who imposed the consequence (BRU-MKP-18), and dispute decision is separated from payout release.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Marketplace console | Marketplace Operations | Real time | Pending approvals, moderation queue, open disputes, jobs at risk, held payouts |
| Supply and demand map | CCO, Ops Director | Weekly | Seller density and demand by category and area; unserved demand and supply gaps |
| Liquidity and fill rate | CCO | Weekly | Broadcast-to-bid, bid-to-award and award-to-completion rates by category and area |
| Seller cohort economics | CCO, CFO | Monthly | Acquisition cost, activation, retention, jobs and take rate by seller cohort |
| Seller performance league | Marketplace Operations, CCO | Weekly | Scores, bands, consequences applied, appeals |
| Quality parity report | Quality Manager, CCO | Weekly | Evidence compliance, QC pass rate, rework and CSAT — marketplace vs owned work, side by side |
| Dispute analysis | CCO, Quality Manager, CFO | Weekly | Dispute rate by category and seller, decision mix, remedy cost, recovery rate, SLA attainment |
| Take rate and commission | CFO, CCO | Monthly | Gross marketplace value, commission, fees, promotion revenue, net contribution |
| Payout and wallet position | CFO, Finance Manager | Weekly | Held, eligible, paid and recovered balances; ageing of held funds |
| Trust and safety report | CCO, Quality Manager | Monthly | Off-platform signals, collusion, review manipulation, counterfeit findings and outcomes |
| Promotion performance | CCO, Marketing | Monthly | Boost and advertising revenue, impressions, clicks, seller ROI |
| Principal/agent compliance | CFO, auditor | Quarterly | Transactions by treatment, VAT position, determination currency |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W8 Target | W9 Target |
|---|---|---|---|---|
| KPI-C12-01 | Approved active sellers | 0 | 300 | **500** |
| KPI-C12-02 | Marketplace share of total job volume | 0% | 15% | **> 25%** |
| KPI-C12-03 | Marketplace dispute rate | n/a | < 2.5% | **< 1.5%** |
| KPI-C12-04 | Seller onboarding completion rate | n/a | 50% | **> 60%** |
| KPI-C12-05 | Seller monthly active rate | n/a | 60% | **> 70%** |
| KPI-C12-06 | Average seller rating | n/a | 4.2 | **> 4.4** |
| KPI-C12-07 | Seller retention at 12 months | n/a | n/a | **> 65%** |
| KPI-C12-08 | Broadcast-to-award fill rate | n/a | 70% | **> 85%** |
| KPI-C12-09 | Evidence compliance on marketplace jobs | n/a | 97% | **100%** |
| KPI-C12-10 | Marketplace CSAT vs owned-work CSAT gap | n/a | ≤ 0.4 | **≤ 0.15** |
| KPI-C12-11 | Rework rate on marketplace jobs | n/a | < 6% | **< 3%** |
| KPI-C12-12 | Payouts executed on schedule | n/a | 98% | **100%** |
| KPI-C12-13 | Payout disputes or errors | n/a | < 1% | **< 0.2%** |
| KPI-C12-14 | Detected off-platform leakage rate | n/a | measured | **< 3%** |
| KPI-C12-15 | Counterfeit-part findings per 1,000 jobs | n/a | < 3 | **< 1** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L2 | OCA `partner_*`, `queue_job`, `sale_commission` family (scheme modelling), `document_*` | 12% |
| L4 | P07 Next.js seller portal and React Native seller app | 24% |
| L5 | `cd_seller_onboarding`, `cd_listing`, `cd_job_broadcast`, `cd_seller_performance`, `cd_dispute`, `cd_seller_settlement`, `cd_seller_ads` | 64% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C12-01 | `cd_seller_onboarding` — registration, KYC at T5, verification, agreement, tiers, approval workflow | Odoo module + service | 8 PW |
| CD-C12-02 | `cd_listing` — service and product listings, moderation pipeline, prohibited items, seller stock | Odoo module | 7 PW |
| CD-C12-03 | `cd_job_broadcast` — eligibility, matching, ranking, broadcast fan-out, bidding, award, reassignment, data-grant control | Odoo module + service | 10 PW |
| CD-C12-04 | `cd_seller_performance` — evidence parity, scorecard, consequence ladder, probation, appeals, reviews | Odoo module | 7 PW |
| CD-C12-05 | `cd_dispute` — dispute workflow, mediation, remedy execution, recovery, fund blocking | Odoo module | 6 PW |
| CD-C12-06 | `cd_seller_settlement` — commission schemes, wallet ledger, hold periods, payout instruction, statements | Odoo module + service | 7 PW |
| CD-C12-07 | `cd_seller_ads` — boost, top-listing, advertising placements and reporting | Odoo module | 3 PW |
| CD-C12-08 | Trust and safety — off-platform, collusion and manipulation detection with investigation workflow | Service | 2 PW |
| | | **Total** | **50 PW** |

> **Scale note.** At 50 PW this is the largest module in Category C and the second largest in the
> programme after M01. It is also the module with the highest proportion of custom code (64%),
> because no open-source component models a service marketplace with brand-liability controls.
> Wave 7 capacity must be validated against this figure before the roadmap is baselined
> *(cross-reference audit finding M-09)*.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **External tax and legal opinion on principal/agent** | **Blocking.** Required three months before build per RSK-022. No settlement or VAT logic may be built without it |
| M38 E-Commerce | M12 extends M38's storefront, cart and checkout; building M12 first would duplicate the commerce core |
| M01 SRM (complete) | A marketplace job is a service order with an external party |
| M37 Catalogue · M11 Pricing | Taxonomy and fee pricing |
| M53 Revenue & Settlement *(W4/W7)* | Settlement execution and payout |
| M20 Receivable · M51 Tax · M52 Payable | Financial documents, VAT and disbursement |
| M23 Quality | Evidence standards and audit |
| M24 Document · M29 Identity | KYC storage, e-signature, seller identity |
| P07 delivered with M12 | The seller portal and app are the module's only meaningful surface |

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Existing informal sub-contractor list | ~50–150 | `fix.seller` (Registered state — full onboarding still required) | W7 |
| Historical sub-contract job records | To be profiled | Warehouse only, for baseline | W7 |

**Migration rule.** No existing sub-contractor is migrated as an Approved seller. Every seller
completes KYC, agreement signature and training through the platform. This is deliberately
slower than migrating a list, and it is the only way the verification chain is defensible to a
brand partner or a regulator.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A documented external tax and legal opinion on principal/agent exists, is recorded in the determination register, and drives the transaction flag | Opinion document + determination record + transaction inspection |
| AC-02 | A seller cannot bid, be awarded or be paid until KYC is verified, the agreement is signed and approval is granted | Negative test at each stage via UI and API |
| AC-03 | A marketplace job cannot complete without the same evidence pack, QC checklist and customer sign-off as an owned job | Negative test; side-by-side comparison with an owned job |
| AC-04 | Customer contact data is released only on award and is provably inaccessible after the revocation interval | Access test before award, during, and after revocation |
| AC-05 | A job broadcast to 500 sellers delivers within 10 seconds with per-seller delivery tracking | Load test |
| AC-06 | Broadcast ranking is reconstructible for any past broadcast from the recorded basis | Fairness audit on historical broadcasts |
| AC-07 | Warranty work under a brand authorisation is never broadcast to the marketplace, by any route | Negative test across job types |
| AC-08 | Opening a dispute atomically blocks the disputed amount; closing it releases or recovers atomically | Concurrency test |
| AC-09 | The seller wallet balance always equals the sum of its movements, and no route permits a direct balance edit | Reconciliation + negative test via UI, API and ORM |
| AC-10 | A payout batch of 2,000 sellers executes idempotently with no double payment under induced failure | Chaos test |
| AC-11 | Score thresholds apply consequences automatically, and an appeal is decided by a different operator | Scripted scenario + SOD test |
| AC-12 | Approving a seller and approving their payout cannot be performed by the same user | SOD-06 negative test |
| AC-13 | A seller completes registration, bidding, evidence capture and completion entirely in Bengali on a mid-range Android device, including offline | Field test with ten real sellers |
| AC-14 | Marketplace CSAT, evidence compliance and rework are reported side by side with owned work and meet the parity targets | Parity report at the Wave 8 gate |
| AC-15 | Zero critical or high security findings, with particular attention to T5 KYC data and the seller data-grant boundary | Security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Is 1000FiX principal or agent for marketplace transactions, per category? The VAT, revenue and liability treatment all follow, and RSK-022 rates getting this wrong as Critical | CFO / CEO / external counsel | **W6 — blocking, three months before build** |
| Q-02 | Who bears warranty liability on marketplace work — 1000FiX or the seller? *(carried from M01 Q-05)* | CEO / Legal | **W7 — blocking** |
| Q-03 | Is a security deposit required from sellers, and what recovery limits apply against earnings? | CFO / CCO | W7 build |
| Q-04 | What is the payout hold period, and does it differ by seller tier and job value? | CFO | W7 build |
| Q-05 | What commission rate structure is commercially viable given that independent engineers currently keep 100% of cash work? | CCO / CEO | **W6 — the module's viability depends on it** |
| Q-06 | Are background checks beyond NID required for sellers entering customers' homes, and is 1000FiX liable if one is not done? | Legal / CCO | **W7 — blocking** |
| Q-07 | Does PDPA 2026 permit the customer-data grant model described in §5.3, and for how long may a seller retain contact details? | Legal / CTO | W7 build |
| Q-08 | Do brand partners accept that 1000FiX operates a marketplace at all, and are there authorisation terms restricting it? | CCO / Finance Director | **W6 — blocking** |
| Q-09 | What is the policy consequence when off-platform transaction is detected — warning, penalty, or removal? | CCO | W7 build |
| Q-10 | Is Wave 7 capacity sufficient for a 50 PW module alongside M38 and M40? | CTO / Programme Manager | W6 planning |

---

## 19. References

**Internal**
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §4.3, §5, §8, §10 (RSK-022) ·
`M38_ECommerce_and_Digital_Storefront.md` §3, §12 ·
`M37_Product_and_Service_Catalogue_Management.md` §3 ·
`M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md` §5.2 (marketplace fee schedule) ·
`M08_Contract_Lifecycle_Management.md` §5.1 (seller agreement family) ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` §5.8 FR-SRM-068, §12 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §4 (T5), §5, §6 SOD-06, §8 EA-04 ·
`05-05_Business_Rules_and_Automation_Catalogue.md` ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P07 ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §3 streams 13–14 ·
`00-04_Risks_Assumptions_Dependencies_and_Governance.md` RSK-022 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Marketplace, §Seller Agreement — the primary source ·
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.12 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §11 ·
`1000FiX Business Plan` §Marketplace

**External benchmark**
Service marketplace practice (Urban Company, TaskRabbit, Thumbtack) — verification, broadcast matching, automatic performance consequence ·
Product marketplace practice (Amazon, Daraz) — listing moderation, buyer protection, payout holds, seller advertising ·
Marketplace payment platforms (Stripe Connect class) — hosted KYC, escrow-style holds, platform fee capture, dispute fund recovery ·
Gig-platform trust and safety — off-platform leakage, collusion and review-manipulation detection ·
NBR guidance on e-commerce VAT — 5% VAT on platform commission and service charges; the principal-versus-agent question ·
Odoo / OCA `sale_commission` module family — commission rule modelling

---

*Module M12 · Category C · 1000FiX ERP System v2.0 · CONFIDENTIAL*
