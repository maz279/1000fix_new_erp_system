---
id: FIX-ERP2-006
title: Pillar B — Customer, Commercial & Revenue Modules (M07–M14)
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Pillar B — Customer, Commercial & Revenue
# Modules M07–M14: Features & Functions

**Pillar owner:** Chief Commercial Officer
**Data domain:** Parties, agreements, prices, orders, channels
**Modules:** M07 CRM · M08 CTR · M09 WTY · M10 LOY · M11 SLS · M12 ECM · M13 RNT · M14 TRF

---

# M07 — Customer Relationship Management & Customer 360 (CRM)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M07 / `CRM` |
| **Status** | Expanded |
| **Priority** | P0 |
| **Wave** | W1 |
| **Delivery layers** | L1 (Odoo crm, contacts) + L5 (CD-033…036) |
| **Requirements** | FR-CRM-001 … FR-CRM-055 |
| **Effort** | 25 person-weeks |

## 1. Purpose

M07 answers one question authoritatively: **who is this customer, and what is our complete
relationship with them?** Every other module depends on it. 250,000+ customers per month,
across five customer classes, with devices, contracts, entitlements, conversations, payments
and preferences unified in one record.

## 2. Scope Expansion Over v1.0

| v1.0 | v2.0 Addition |
|---|---|
| Individual and corporate | + Dealer, Government, Household group, Marketplace seller-as-customer |
| Flat customer record | Hierarchical accounts: group → company → division → site → contact |
| Single approval | Multi-tier corporate registration approval: user → client line manager → 1000FiX admin |
| One address | Multiple tagged addresses (home, office, factory) with saved GPS coordinates |
| Standard pricing | Customer-specific and segment-specific price lists (SOW: "laptop service rate for company A is 500 tk, company B 400 tk") |
| — | Consent and communication-preference management with audit |
| — | Credit limits, payment terms and credit-hold enforcement |
| — | Customer health score, churn risk and lifetime value |
| — | Household/family grouping for RAMC and appliance services |
| — | Complete conversation history from M27 across all channels |

## 3. Functional Areas & Features

### 3.1 Customer Master

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CRM-001 | Unified customer record | Maintain one record per customer with identity, contacts, addresses, devices, service history, contracts, invoices, payments, communications and documents | P0 |
| FR-CRM-002 | Customer classification | Classify as Individual · Household · Dealer · Corporate · Government · Marketplace Seller · Brand Partner, with class-specific fields and rules | P0 |
| FR-CRM-003 | Account hierarchy | Model group → company → division → site → contact relationships with roll-up reporting | P1 |
| FR-CRM-004 | Multiple tagged addresses | Store unlimited addresses with tags (home, office, factory, branch) and saved GPS coordinates from the mobile app | P1 |
| FR-CRM-005 | Bangladesh address structure | Enforce division → district → upazila → union/ward → postcode with cascading selection and map picker | P1 |
| FR-CRM-006 | Identity verification | Capture and validate NID (10/17-digit), passport, trade licence, BIN and TIN as applicable to the customer class | P0 |
| FR-CRM-007 | Duplicate detection & merge | Detect duplicates on phone, email, NID and device serial; provide a supervised merge that preserves history | P1 |
| FR-CRM-008 | Registration approval workflow | For dealer/corporate/government: route new user registration through the client's line manager and then a 1000FiX administrator | P1 |
| FR-CRM-009 | Contact verification | Verify mobile number and email by OTP at registration and on change | P0 |
| FR-CRM-010 | Customer status | Manage Active · Dormant · Blocked · Credit Hold · Blacklisted with reasons and re-activation controls | P1 |

### 3.2 Device & Asset Association

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CRM-011 | Device registry link | Link every device the customer owns, has serviced, rents or has traded in (mastered in M17) | P0 |
| FR-CRM-012 | Bulk asset registration | Allow corporate customers to register asset estates in bulk by CSV/Excel with serial, brand, model, purchase date, location and image | P1 |
| FR-CRM-013 | Device transfer | Transfer device ownership between customers with an audit trail (resale, trade-in, corporate reassignment) | P2 |

### 3.3 Segmentation, Insight & Value

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CRM-014 | Segmentation engine | Build dynamic segments from any combination of attributes, behaviour and value | P1 |
| FR-CRM-015 | Customer 360 view | Present a single screen with everything: profile, devices, open jobs, history, contracts, entitlements, dues, tier, conversations, sentiment | P0 |
| FR-CRM-016 | Lifetime value | Calculate and display revenue, margin and CLV per customer | P2 |
| FR-CRM-017 | Health score & churn risk | Compute a health score from recency, frequency, value, satisfaction and complaint signals; flag churn risk (model from M26) | P2 |
| FR-CRM-018 | Next-best-action | Suggest the next commercial action (renew, upsell, recover, retain) on the customer record | P3 |

### 3.4 Sales Pipeline & Opportunity

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CRM-019 | Lead capture | Capture leads from the website, campaigns, referrals, chatbot, walk-in and events with source attribution | P1 |
| FR-CRM-020 | Lead qualification & routing | Score and route leads to the right sales owner by product, geography and value | P1 |
| FR-CRM-021 | Opportunity management | Manage opportunities through stages with value, probability, expected close and competitor tracking | P1 |
| FR-CRM-022 | Account planning | Maintain account plans for key corporate accounts with objectives, stakeholders and actions | P2 |
| FR-CRM-023 | Activity management | Log calls, meetings, visits and follow-ups with reminders | P1 |

### 3.5 Service Experience & Voice of Customer

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CRM-024 | Communication history | Show every interaction across SMS, WhatsApp, email, chat, call and in-person, sourced from M27 | P0 |
| FR-CRM-025 | CSAT / NPS capture | Trigger and record satisfaction surveys; compute rolling scores by branch, technician and service type | P1 |
| FR-CRM-026 | Complaint intake | Log complaints with category and severity, route to M23 for CAPA, and track resolution to the customer | P0 |
| FR-CRM-027 | Sentiment analysis | Derive sentiment from conversations and reviews (model from M26) and surface it on the customer record | P3 |
| FR-CRM-028 | Consent & preferences | Record consent for marketing by channel with timestamp and source; enforce it in all outbound messaging | P0 |

### 3.6 Commercial Controls

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CRM-029 | Customer price list assignment | Assign a specific price list per customer or segment, used by M11 | P1 |
| FR-CRM-030 | Credit limit & terms | Set credit limits and payment terms; block new orders above the limit pending approval | P1 |
| FR-CRM-031 | Contract & entitlement view | Show all active contracts, entitlements and remaining balances at a glance | P1 |
| FR-CRM-032 | Account statement | Produce a customer account statement of invoices, payments, credits and balance | P1 |

*(FR-CRM-033 … FR-CRM-055 cover household grouping, corporate contact roles and approval
chains, customer portal identity linkage, data-subject requests, and CRM analytics —
catalogued in Doc 11.)*

## 4. Key Entities

`fix.party` · `fix.party.role` · `fix.party.hierarchy` · `fix.customer.profile` ·
`fix.address` · `fix.contact.verification` · `fix.identity.document` · `fix.consent.record` ·
`fix.segment` · `fix.customer.health` · `fix.lead` · `fix.opportunity` · `fix.activity` ·
`fix.complaint` · `fix.survey.response` · `fix.credit.profile`

## 5. KPIs

| KPI | Baseline | Target |
|---|---|---|
| Customer record completeness | unmeasured | > 92% of mandatory fields |
| Duplicate customer rate | unmeasured | < 1% |
| Customer 360 load time | — | < 2 seconds |
| CSAT | 3.8/5 | 4.7/5 |
| NPS | unmeasured | > 55 |
| Churn (active customers) | ~15% | < 8% |
| Corporate registration approval cycle | manual | < 24 hours |

---

# M08 — Contract Lifecycle Management (CTR)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M08 / `CTR` |
| **Status** | Expanded (split from v1.0 Contract & Warranty) |
| **Priority** | P1 |
| **Wave** | W4 |
| **Delivery layers** | L2 (OCA fieldservice_agreement, recurring) + L5 (CD-037…040) |
| **Requirements** | FR-CTR-001 … FR-CTR-052 |
| **Effort** | 28 person-weeks |

## 1. Purpose

The Company's business plan describes **at least fourteen distinct contract products** across
five AMC families, six managed-service families and five mobile/appliance service families.
A single "AMC" object cannot model them. M08 provides a general contract engine with product
templates, entitlements, service schedules, SLAs, pricing, billing terms and renewal.

## 2. Contract Product Families Supported

| Family | Products | Source |
|---|---|---|
| **Residential AMC (RAMC)** | Appliance packages (6 tiers) covering TV, fridge, AC, washing machine, oven, geyser | Business Plan §Residential AMC; Company Profile §RAMC |
| **Commercial AMC** | Office/retail/restaurant equipment: computers, printers, servers, CCTV, fire alarm | Business Plan §Commercial AMC |
| **IT Infrastructure AMC** | Servers, networking, storage, backup & recovery systems | Business Plan §IT Infrastructure AMC |
| **Healthcare Equipment AMC** | Diagnostic machines, lab equipment, patient monitoring — with calibration obligations | Business Plan §Healthcare Equipment AMC |
| **Specialty Equipment AMC** | Manufacturing, R&D, telecom equipment with bespoke plans | Business Plan §Specialty Equipment AMC |
| **Managed Services (MSP)** | Basic · Comprehensive · Security-focused · Cloud Services · DR/BC · IT Strategy Consulting | Business Plan §Managed Service Contracts |
| **Mobile & Appliance Service Contracts** | Basic Maintenance · Comprehensive Maintenance & Repair · Extended Warranty · Accidental Damage Protection · Priority Service | Business Plan §Mobile and Home Appliance Service Contracts |
| **Rental Master Agreements** | Framework agreements governing rental orders | Business Plan §Rental Services |
| **Marketplace Seller Agreements** | Terms, commission rates, service standards | SOW §external registrant agreement with digital signature |
| **Brand Partner Agreements** | Authorised service terms, claim rules, rate cards | Company Profile §17 brand partnerships |

## 3. Functional Areas & Features

### 3.1 Contract Definition

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CTR-001 | Contract product templates | Define reusable contract templates per family with default entitlements, SLAs, pricing and terms | P1 |
| FR-CTR-002 | Contract creation | Create a contract from a template, a quotation or a renewal, with customer, period, scope and commercials | P1 |
| FR-CTR-003 | Covered scope | Define coverage by device, asset class, site, seat, user or estate, with inclusion and exclusion rules | P1 |
| FR-CTR-004 | Entitlement definition | Define what is included: visit counts, incident counts, labour hours, parts allowance, response and resolution SLAs, coverage window | P1 |
| FR-CTR-005 | Exclusions | Record explicit exclusions (accidental damage, consumables, software, third-party faults) enforced at service intake | P1 |
| FR-CTR-006 | Pricing & billing terms | Set price, billing frequency (monthly, quarterly, half-yearly, annual), advance/arrears, indexation and escalation | P1 |
| FR-CTR-007 | Multi-year & auto-renew | Support multi-year terms, auto-renewal with notice periods, and price uplift at renewal | P1 |
| FR-CTR-008 | Contract documents | Attach the signed agreement, obtain e-signature, and version amendments | P1 |
| FR-CTR-009 | Approval workflow | Route contracts above thresholds or with non-standard terms for internal approval | P1 |

### 3.2 Contract Execution

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CTR-010 | Activation | Activate on signature and payment (as configured); publish entitlements to M01, M02 and M05 | P1 |
| FR-CTR-011 | Preventive-maintenance schedule | Generate the visit schedule for the contract term and create work orders automatically at the right lead time | P1 |
| FR-CTR-012 | Entitlement consumption | Decrement entitlements as services are delivered; prevent or flag over-consumption | P1 |
| FR-CTR-013 | Overage handling | Detect and price consumption beyond entitlement; bill or seek an uplift | P1 |
| FR-CTR-014 | Coverage validation at intake | Validate at service intake that the device, site and fault are within contract scope | P0 |
| FR-CTR-015 | Contract amendments | Add or remove covered assets, change entitlements or price mid-term with effective dating and pro-rated billing | P1 |
| FR-CTR-016 | Suspension & reinstatement | Suspend on non-payment or customer request; reinstate with rules on the suspended period | P1 |
| FR-CTR-017 | Termination | Terminate for cause or convenience with notice, final billing, refund calculation and asset return | P1 |

### 3.3 SLA Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CTR-018 | SLA definition | Define response, resolution and availability SLAs per contract, priority and coverage window | P1 |
| FR-CTR-019 | SLA measurement | Measure attainment per incident and per period against the contract calendar | P1 |
| FR-CTR-020 | SLA reporting | Produce contractual SLA reports for the customer at the agreed cadence | P1 |
| FR-CTR-021 | Service credits | Calculate credits on breach per the contract's credit schedule and pass to M20 | P1 |

### 3.4 Renewal & Retention

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CTR-022 | Renewal pipeline | Maintain a forward view of contracts due for renewal by month, value and risk | P1 |
| FR-CTR-023 | Renewal alerts | Notify the customer and the account owner at 90/60/30/15 days before expiry | P1 |
| FR-CTR-024 | Renewal quotation | Generate a renewal quotation with uplift and usage-based recommendations | P1 |
| FR-CTR-025 | Non-renewal handling | On expiry without renewal, cancel scheduled work, notify the customer, and revert to standard pricing | P1 |
| FR-CTR-026 | Win-back | Track lapsed contracts and run win-back campaigns through M10 | P2 |

### 3.5 Contract Profitability

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CTR-027 | Cost capture | Accumulate the actual cost of delivering the contract — labour, parts, travel, sub-contract, logistics | P2 |
| FR-CTR-028 | Profitability analysis | Report revenue vs cost vs margin per contract, product family and customer | P2 |
| FR-CTR-029 | Loss-making alerts | Alert when a contract's margin falls below threshold, with drill-down to cause | P2 |
| FR-CTR-030 | Pricing feedback | Feed actual delivery cost back into M11 pricing for future contract quotes | P3 |

*(FR-CTR-031 … FR-CTR-052 cover contract templates library, obligations tracking, calibration
schedules for healthcare AMC, contract portal self-service, and bulk contract operations —
catalogued in Doc 11.)*

## 4. Key Entities

`fix.contract` · `fix.contract.template` · `fix.contract.line` · `fix.contract.covered.asset` ·
`fix.entitlement` · `fix.entitlement.consumption` · `fix.contract.sla` · `fix.sla.measurement` ·
`fix.sla.credit` · `fix.pm.schedule` · `fix.pm.visit` · `fix.contract.amendment` ·
`fix.renewal.opportunity` · `fix.contract.cost.line`

## 5. KPIs

| KPI | Baseline | Target |
|---|---|---|
| AMC/RAMC renewal rate | 60% | 88% |
| Contract base growth | — | 2.5× in 24 months |
| Preventive visits completed on schedule | unmeasured | > 95% |
| Contracts with negative margin | unmeasured | < 3% |
| Entitlement over-consumption unbilled | unmeasured | < 2% |
| SLA attainment across contracts | unmeasured | > 97% |

---

# M09 — Warranty & Claims Management (WTY)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M09 / `WTY` |
| **Status** | Expanded (split from v1.0 Contract & Warranty) |
| **Priority** | P0 |
| **Wave** | W4 |
| **Delivery layers** | L2 (OCA fieldservice_equipment_warranty) + L4 (n8n) + L5 (CD-041…044) |
| **Requirements** | FR-WTY-001 … FR-WTY-048 |
| **Effort** | 28 person-weeks |

## 1. Purpose

Two things live here, and both are money:

1. **Inbound** — recovering revenue from 17+ brand partners for warranty work performed.
   The v1.0 BRD estimates 15–20% of warranty revenue is currently unclaimed or delayed.
2. **Outbound** — selling and honouring 1000FiX's own warranty products: seven distinct
   protection products described in the business plan.

## 2. Warranty Product Families (1000FiX-Sold)

| Product | Coverage | Source |
|---|---|---|
| Standard Warranty Extension | Extends manufacturer warranty 1+ years for defects in materials/workmanship | Business Plan |
| Accidental Damage Protection | Drops, spills, physical damage | Business Plan |
| Extended Repair Coverage | Parts and labour beyond manufacturer warranty | Business Plan |
| Mobile Device Protection | Comprehensive smartphone/tablet cover with replacement option | Business Plan |
| Home Appliance Protection | Mechanical/electrical failure cover for appliances | Business Plan |
| Computer & Laptop Care | Hardware, software and accidental damage | Business Plan |
| Customised Coverage | Bespoke device selection, duration and terms | Business Plan |

## 3. Functional Areas & Features

### 3.1 Warranty Entitlement

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-WTY-001 | Manufacturer warranty register | Record manufacturer warranty start, duration, terms and evidence per device | P0 |
| FR-WTY-002 | Automatic entitlement check | Determine warranty status at service intake from serial, purchase date and brand rules | P0 |
| FR-WTY-003 | Purchase evidence | Capture and validate invoice/receipt evidence for warranty claims | P0 |
| FR-WTY-004 | Warranty exclusions | Enforce brand-specific exclusions (physical damage, liquid, unauthorised repair, tamper) with evidence capture | P0 |
| FR-WTY-005 | Warranty void determination | Record a void determination with evidence, technician attestation and customer notification | P1 |
| FR-WTY-006 | Repair warranty | Apply and track 1000FiX's own warranty on completed repairs; auto-classify returns within the window | P0 |

### 3.2 Warranty Product Sales

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-WTY-007 | Product catalogue | Define warranty and protection products with device eligibility, term options, price and terms | P1 |
| FR-WTY-008 | Eligibility assessment | Assess a device's eligibility from age, condition report, photographs and prior history | P1 |
| FR-WTY-009 | Condition-based quotation | Produce a price quotation from the assessment, following the SOW model (customer submits images and details; back office quotes) | P1 |
| FR-WTY-010 | Enrolment & activation | Enrol, collect payment, activate cover and issue a certificate | P1 |
| FR-WTY-011 | Coverage dashboard | Give the customer a portal view of cover: start, end, claims used, remaining benefit, service history, payments | P1 |
| FR-WTY-012 | Claim against own product | Process a claim against a 1000FiX warranty product with excess, limits and replacement rules | P1 |
| FR-WTY-013 | Replacement fulfilment | Handle irreparable-device replacement with valuation, sourcing and depreciation rules | P2 |
| FR-WTY-014 | Reserve & liability | Maintain an actuarial reserve for outstanding warranty liability and report it to finance | P2 |
| FR-WTY-015 | Renewal | Notify and renew warranty products before expiry | P1 |

### 3.3 Brand Warranty Claims (Inbound Revenue)

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-WTY-016 | Automatic claim creation | Create a claim automatically within 24 hours of closing a warranty service order | P0 |
| FR-WTY-017 | Evidence pack assembly | Assemble the required evidence — serial, fault code, diagnosis, before/after photos, parts replaced, technician certification, purchase proof | P0 |
| FR-WTY-018 | Brand rule engine | Apply each brand's claim rules: eligible fault codes, labour rates, parts policy, documentation requirements, submission window | P0 |
| FR-WTY-019 | Completeness validation | Block submission of incomplete claims and tell the user exactly what is missing | P0 |
| FR-WTY-020 | Multi-format submission | Submit via brand partner portal API, structured email, or file batch, per brand | P0 |
| FR-WTY-021 | Claim lifecycle | Track Draft → Validated → Submitted → Under Review → Approved → Partially Approved → Rejected → Resubmitted → Invoiced → Paid → Closed | P0 |
| FR-WTY-022 | Response ingestion | Ingest brand responses and update claim status, approved amount and reason codes | P1 |
| FR-WTY-023 | Rejection management | Route rejections to a dispute queue with reason analysis, correction and resubmission | P0 |
| FR-WTY-024 | Duplicate prevention | Prevent duplicate claims for the same serial and fault within the brand's window | P0 |
| FR-WTY-025 | Ageing & follow-up | Age submitted claims and drive automated follow-up per each brand's stated reimbursement timeline | P0 |
| FR-WTY-026 | Payment reconciliation | Match brand remittances to claims, handle part-payments and short-payments, and post to M19 | P0 |
| FR-WTY-027 | Consignment parts reconciliation | Reconcile brand-supplied parts consumed against claims and returns | P1 |
| FR-WTY-028 | Brand scorecard | Report per brand: claim volume, approval rate, average days to payment, rejection reasons, revenue realised | P1 |

### 3.4 Warranty Analytics & Control

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-WTY-029 | Revenue-at-risk | Show warranty revenue not yet claimed, claimed but unapproved, and approved but unpaid | P0 |
| FR-WTY-030 | Leakage detection | Identify closed warranty jobs with no claim raised, and jobs claimed outside the brand window | P0 |
| FR-WTY-031 | Failure-pattern reporting | Report failure patterns by brand, model and component for brand feedback and predictive models | P2 |
| FR-WTY-032 | Claim profitability | Compare claim reimbursement against actual delivery cost per brand and repair type | P2 |

*(FR-WTY-033 … FR-WTY-048 cover brand partner portal interactions, rate card management,
audit packs for brand audits, and warranty product actuarial reporting — catalogued in Doc 11.)*

## 4. Key Entities

`fix.warranty.register` · `fix.warranty.product` · `fix.warranty.policy` ·
`fix.warranty.assessment` · `fix.warranty.claim` · `fix.claim.evidence` · `fix.claim.line` ·
`fix.brand.rule` · `fix.brand.rate.card` · `fix.claim.response` · `fix.claim.remittance` ·
`fix.warranty.reserve` · `fix.consignment.part.usage`

## 5. KPIs

| KPI | Baseline | Target |
|---|---|---|
| Claim submission within 72 hours of closure | ~50% at 30–90 days | > 95% |
| Warranty revenue leakage | 15–20% | < 2% |
| Claim approval rate (first submission) | unmeasured | > 92% |
| Average days from service to cash | 60–120 | < 45 |
| Claims with complete evidence at first submission | unmeasured | > 98% |
| Warranty product attach rate on eligible repairs | unmeasured | > 18% |

---

# M10 — Loyalty, Referral & Campaign Management (LOY)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M10 / `LOY` |
| **Status** | Expanded |
| **Priority** | P1 |
| **Wave** | W2 |
| **Delivery layers** | L5 (CD-045…047) |
| **Requirements** | FR-LOY-001 … FR-LOY-041 |
| **Effort** | 19 person-weeks |

## 1. Purpose

M10 runs everything that changes what a customer pays or why they come back: the Privilege
programme, credit points, vouchers, referral programmes, partner alliances and promotional
campaigns across all channels.

**Evidence for expansion:** Company Profile §Privileged Program, §Partner Alliance Program;
SOW §"for new customers, there will be some credit points so that customers can get discounts
during their next purchase", §Referral program, §Campaigns (double points, partnered brand
campaigns, special day campaigns), §"scheduled auto on/off the campaign";
Portal roadmap IMPL-39 Referral Partner Program.

## 2. Functional Areas & Features

### 2.1 Privilege Programme

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOY-001 | Tier definition | Define Silver / Gold / Diamond tiers with price, duration, benefits and qualification rules | P1 |
| FR-LOY-002 | Enrolment | Enrol via portal, app, counter or agent with payment and instant activation | P1 |
| FR-LOY-003 | Benefit application | Apply benefits automatically at quotation and invoicing — 50% labour discount, priority SLA, free logistics, extended repair warranty | P1 |
| FR-LOY-004 | Benefit scoping rules | Enforce that discounts apply to labour only, not parts, consumables or transport | P0 |
| FR-LOY-005 | Tier upgrade/downgrade | Upgrade mid-term with pro-rated pricing; downgrade at renewal | P2 |
| FR-LOY-006 | Membership dashboard | Show the customer their tier, benefits used, remaining services, expiry and history | P1 |
| FR-LOY-007 | Renewal | Notify and renew before expiry, with lapse handling | P1 |

### 2.2 Points & Wallet

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOY-008 | Points earning rules | Define earning rules by action: registration, first booking, spend value, review submitted, referral converted, campaign multiplier | P1 |
| FR-LOY-009 | Points ledger | Maintain an auditable ledger of earn, burn, expiry, adjustment and transfer | P1 |
| FR-LOY-010 | Redemption | Redeem points against service charges, parts, accessories or membership fees, with configurable limits | P1 |
| FR-LOY-011 | Expiry | Expire points on a schedule with advance notification | P2 |
| FR-LOY-012 | Customer wallet | Maintain a stored-value wallet for refunds, credits and pre-paid balances, with full ledger and payout rules | P2 |

### 2.3 Vouchers, Coupons & Offers

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOY-013 | Voucher generation | Generate single-use, multi-use and bulk voucher codes with value, validity and eligibility rules | P1 |
| FR-LOY-014 | Eligibility engine | Restrict by customer segment, service type, channel, branch, minimum value, first-purchase-only | P1 |
| FR-LOY-015 | Stacking rules | Control which offers can combine and in what order they apply | P1 |
| FR-LOY-016 | Redemption tracking | Track issuance, redemption, expiry and financial cost per campaign | P1 |
| FR-LOY-017 | Fraud controls | Detect and block abusive redemption patterns | P2 |

### 2.4 Referral & Partner Alliance

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOY-018 | Customer referral programme | Issue unique referral links/codes; attribute conversions; reward both referrer and referee | P1 |
| FR-LOY-019 | Partner alliance programme | Onboard alliance partners (retailers, corporates, associations) with agreed benefits for their members | P2 |
| FR-LOY-020 | Partner referral tracking | Track leads and revenue attributable to each partner | P2 |
| FR-LOY-021 | Commission on referral | Calculate referral commissions and pass to M20 for payment | P2 |
| FR-LOY-022 | Partner portal statements | Publish referral performance and commission statements to the partner portal (P12) | P2 |

### 2.5 Campaign Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOY-023 | Campaign definition | Define a campaign with audience, offer, channels, budget, creative and schedule | P1 |
| FR-LOY-024 | Scheduled activation | Automatically switch campaigns on and off at defined times | P1 |
| FR-LOY-025 | Multi-channel execution | Execute through SMS, WhatsApp, email, push, in-app inbox, portal banners and the website | P1 |
| FR-LOY-026 | Consent enforcement | Suppress any recipient without valid marketing consent for that channel | P0 |
| FR-LOY-027 | Brand co-marketing | Run partnered campaigns with brands, tracking cost share and attributed revenue | P2 |
| FR-LOY-028 | Seasonal & event campaigns | Support recurring seasonal campaigns (FiXnChill, Eid, monsoon AC service, winter geyser) with templates | P2 |
| FR-LOY-029 | Campaign analytics | Report reach, engagement, conversion, revenue, cost and ROI per campaign | P1 |
| FR-LOY-030 | A/B testing | Test offer and message variants and select the winner | P3 |

*(FR-LOY-031 … FR-LOY-041 cover in-app advertising placement, gamification, birthday/anniversary
triggers, win-back journeys and loyalty analytics — catalogued in Doc 11.)*

## 3. Key Entities

`fix.privilege.tier` · `fix.privilege.member` · `fix.benefit.rule` · `fix.points.ledger` ·
`fix.wallet` · `fix.wallet.transaction` · `fix.voucher` · `fix.voucher.redemption` ·
`fix.offer.rule` · `fix.referral.code` · `fix.referral.conversion` · `fix.alliance.partner` ·
`fix.campaign` · `fix.campaign.audience` · `fix.campaign.result`

## 4. KPIs

| KPI | Target |
|---|---|
| Privilege membership base | 3× growth in 24 months |
| Privilege renewal rate | > 80% |
| Repeat purchase rate | +25% vs non-members |
| Referral-attributed new customers | > 12% of new customers |
| Campaign ROI | > 4:1 |
| Points redemption rate | 35–55% (healthy band) |

---

# M11 — Sales, Quotation & Dynamic Pricing (SLS)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M11 / `SLS` |
| **Status** | ★ New in v2.0 |
| **Priority** | P1 |
| **Wave** | W3 (core) → W7 (dynamic pricing) |
| **Delivery layers** | L1 (Odoo sale, pricelist) + L5 (CD-048…051) |
| **Requirements** | FR-SLS-001 … FR-SLS-046 |
| **Effort** | 27 person-weeks |

## 1. Purpose

Every price in the business comes from here: service rate cards, parts pricing, contract
pricing, rental tariffs, refurbished device pricing, marketplace listing prices, and the
competitive bidding described in the Service App SOW.

**Evidence:** SOW §Quotation and Acceptance ("engineers can provide quotations… customers
can choose and accept preferred quotations… the customer can bid on an offer; the engineer
can accept or re-bid"), §"our admin shall be able to define different pricing models for
each customer", §"pre-defined rate charts (service type wise, product wise)";
Portal roadmap IMPL-63 Dynamic Pricing Engine.

## 2. Functional Areas & Features

### 2.1 Price Book Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SLS-001 | Price book structure | Maintain price books by business line, customer segment, channel, branch/zone and currency | P1 |
| FR-SLS-002 | Service rate cards | Define labour rates by service type, device category, repair level and delivery mode (walk-in, on-site, remote, pick & drop) | P1 |
| FR-SLS-003 | Parts pricing | Price parts by cost-plus, list price or fixed price, differentiated by genuine/compatible/refurbished | P1 |
| FR-SLS-004 | Customer-specific pricing | Assign a dedicated price book or discount schedule to a named customer or corporate group | P1 |
| FR-SLS-005 | Effective dating | Version price books with effective-from/to dates and scheduled activation | P1 |
| FR-SLS-006 | Price approval | Require approval to publish a price book change above a variance threshold | P1 |
| FR-SLS-007 | Currency & FX | Support multi-currency price books with FX rate sourcing for cross-border pricing | P2 |

### 2.2 Estimation & Quotation

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SLS-008 | Quotation builder | Build quotations from catalogue items, service kits, parts and labour with automatic price resolution | P1 |
| FR-SLS-009 | Service kits | Define standard repair kits (parts + labour + time) per fault code and device model | P1 |
| FR-SLS-010 | Margin visibility | Show cost, price, margin % and margin value to authorised users during quoting | P1 |
| FR-SLS-011 | Discount governance | Enforce maximum discount by role with escalation for exceptions | P1 |
| FR-SLS-012 | Quotation versions | Version quotations with a full change history and reason codes | P1 |
| FR-SLS-013 | Quotation delivery & acceptance | Deliver by SMS, WhatsApp, email and portal; capture accept, reject, or partial accept with e-signature | P1 |
| FR-SLS-014 | Validity & expiry | Apply validity periods with reminders and automatic expiry | P1 |
| FR-SLS-015 | Order customisation post-acceptance | Allow scope change after acceptance with re-quotation and re-approval | P2 |

### 2.3 Competitive Bidding (Marketplace)

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SLS-016 | Request for offer | Let a customer publish a service need, optionally with a target budget | P2 |
| FR-SLS-017 | Multi-party offers | Let 1000FiX and qualified marketplace sellers submit competing offers with price, ETA and rating visible | P2 |
| FR-SLS-018 | Customer bidding | Let the customer counter-bid; let the provider accept or re-bid, with a bounded number of rounds | P2 |
| FR-SLS-019 | Offer comparison | Present offers side by side with price, rating, distance, ETA and warranty | P2 |
| FR-SLS-020 | Variable final price | Support a documented price change after physical diagnosis, with customer re-approval | P2 |
| FR-SLS-021 | Bid integrity controls | Prevent collusion, bid sniping and fake offers; audit all bid activity | P2 |

### 2.4 Dynamic Pricing

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SLS-022 | Pricing rule engine | Define rules that adjust price by demand, capacity, time of day, urgency, seasonality, geography and customer value | P2 |
| FR-SLS-023 | Surge & off-peak pricing | Apply configurable surge for emergency/out-of-hours and discounts for off-peak slots | P2 |
| FR-SLS-024 | Guard rails | Enforce floor and ceiling prices, maximum movement per period, and exclusion of contract and warranty pricing | P0 |
| FR-SLS-025 | Model-driven recommendation | Consume price elasticity and win-probability models from M26 as recommendations, never as automatic overrides above the guard rails | P2 |
| FR-SLS-026 | Price transparency | Always show the customer the final price before commitment; never change price after acceptance without re-approval | P0 |
| FR-SLS-027 | Pricing experiments | Run controlled pricing experiments with holdout groups and measure margin and conversion | P3 |
| FR-SLS-028 | Pricing audit | Log every price decision with the rule and inputs that produced it | P0 |

*(FR-SLS-029 … FR-SLS-046 cover promotions integration, tender/RFP responses for corporate
deals, rental tariff structures, refurbished pricing by grade, and pricing analytics —
catalogued in Doc 11.)*

## 3. Key Entities

`fix.price.book` · `fix.price.rule` · `fix.rate.card` · `fix.service.kit` · `fix.quotation` ·
`fix.quotation.line` · `fix.quotation.version` · `fix.discount.policy` · `fix.offer` ·
`fix.bid` · `fix.pricing.decision.log` · `fix.price.experiment`

## 4. KPIs

| KPI | Target |
|---|---|
| Quotation-to-order conversion | > 78% |
| Average quotation turnaround | < 2 hours |
| Gross margin on paid repair | +4 percentage points vs baseline |
| Price override exceptions | < 5% of quotations |
| Dynamic pricing margin uplift | +3–6% on eligible transactions |
| Pricing errors reaching the customer | < 0.2% |

---

# M12 — E-Commerce, Parts Retail & Marketplace (ECM)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M12 / `ECM` |
| **Status** | ★ New in v2.0 |
| **Priority** | P1 |
| **Wave** | W7 |
| **Delivery layers** | L5 (CD-052…058) + L6 (KYC verification) |
| **Requirements** | FR-ECM-001 … FR-ECM-079 |
| **Effort** | 57 person-weeks — the largest single new module |

## 1. Purpose

The Service App SOW describes an **e-commerce aggregator marketplace** in which external
engineers and shops register, list services and products, bid for work, are rated, pay for
promotion and receive commission-based settlement — all under the 1000FiX brand.

This is a fundamentally different commercial model from owned service delivery, and it is
the single largest unbuilt commitment in the Company's documentation. M12 is that model.

## 2. Functional Areas & Features

### 2.1 Catalogue & Storefront

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ECM-001 | Product & service catalogue | Publish saleable products and services with descriptions, images, specifications, variants and pricing | P1 |
| FR-ECM-002 | Service type modelling | Model in-home service, service-centre service, remote service, doorstep delivery and rental as distinct purchasable types | P1 |
| FR-ECM-003 | Stock-aware ordering | Block ordering of out-of-stock items; show availability by location; sync stock with M15 and seller warehouses | P1 |
| FR-ECM-004 | Search & discovery | Full-text and faceted search with multi-tag support, auto-complete and suggestions in Bengali and English | P1 |
| FR-ECM-005 | Recommendations | Show related, frequently-bought-together and personalised recommendations | P2 |
| FR-ECM-006 | Cart & checkout | Manage cart, apply vouchers and points, calculate delivery charge, VAT and total, and check out | P1 |
| FR-ECM-007 | Guest and registered checkout | Support both, with account creation prompts | P2 |
| FR-ECM-008 | Pre-book / pre-order | Accept pre-orders with payment before product/service launch | P3 |

### 2.2 Order Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ECM-009 | Order orchestration | Split a customer order into fulfilment orders by seller, warehouse and service type; track each independently | P1 |
| FR-ECM-010 | Order status tracking | Provide unified customer-facing status across split fulfilments | P1 |
| FR-ECM-011 | Delivery charging | Calculate distance-based delivery charge — same area, within country, international | P1 |
| FR-ECM-012 | Order modification | Allow modification within a policy window with re-pricing | P2 |
| FR-ECM-013 | Cancellation & returns | Handle cancellations, returns and replacements with reason codes, approval and refund routing | P1 |
| FR-ECM-014 | Refund & reversal | Process refunds through the original payment method with gateway reversal support | P1 |
| FR-ECM-015 | Purchase history | Give the customer a complete purchase and payment history | P1 |

### 2.3 Seller Onboarding & Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ECM-016 | Seller registration | Register external engineers (freelancers) and shops with profile, skills, service areas and categories | P1 |
| FR-ECM-017 | Document verification | Collect and verify NID, trade licence, references and work samples/portfolio images | P0 |
| FR-ECM-018 | Contact verification | Verify mobile and email by OTP | P0 |
| FR-ECM-019 | Admin approval workflow | Require 1000FiX administrator approval before a seller can transact | P0 |
| FR-ECM-020 | Digital agreement | Present the seller agreement and capture a digital signature | P0 |
| FR-ECM-021 | Registration validity & fees | Apply registration expiry dates and optional chargeable registration or renewal fees | P1 |
| FR-ECM-022 | Seller tiers | Classify sellers by tier with differentiated commission, visibility and job access | P2 |
| FR-ECM-023 | Seller suspension & offboarding | Suspend or bar a seller for quality, conduct or compliance reasons, with job reassignment | P1 |
| FR-ECM-024 | Seller self-service on/off | Let a seller mark their shop open or closed and enable/disable individual listings at any time | P1 |
| FR-ECM-025 | Seller warehouse | Maintain a stock location per seller with visibility and reservation rules | P2 |

### 2.4 Marketplace Job Flow

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ECM-026 | Job broadcast | Broadcast eligible jobs to qualified sellers by category, area, rating and capacity | P1 |
| FR-ECM-027 | Seller quotation | Let sellers quote on open jobs with price, ETA and notes (via M11) | P1 |
| FR-ECM-028 | Customer selection | Let the customer choose a seller from competing offers | P1 |
| FR-ECM-029 | Job acceptance & lock | Lock the job to the selected seller with agreed terms | P1 |
| FR-ECM-030 | Seller job execution | Give sellers a job workspace: status updates, evidence upload, parts, completion and customer sign-off | P1 |
| FR-ECM-031 | Seller–customer chat | Enable chat scoped to an open job, with moderation, retention and dispute evidence | P1 |
| FR-ECM-032 | Escalation to 1000FiX | Escalate a failing marketplace job to a 1000FiX technician with commercial consequences for the seller | P1 |
| FR-ECM-033 | Quality standards | Apply the same QC evidence and warranty standards to marketplace jobs as to owned jobs | P0 |

### 2.5 Ratings, Reviews & Trust

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ECM-034 | Multi-parameter rating | Collect ratings on overall service, timeliness, professionalism, behaviour and value | P1 |
| FR-ECM-035 | Verified reviews only | Permit reviews only from customers with a completed transaction | P0 |
| FR-ECM-036 | Review moderation | Moderate reviews for abuse, personal data and defamation before publication | P1 |
| FR-ECM-037 | Seller response | Let sellers respond publicly to a review once | P2 |
| FR-ECM-038 | Rating aggregation & display | Compute and display seller ratings with recency weighting and volume thresholds | P1 |
| FR-ECM-039 | Fraud detection | Detect review manipulation, fake accounts and rating rings | P2 |
| FR-ECM-040 | Dispute resolution | Run a structured dispute process between customer and seller with 1000FiX adjudication and evidence | P1 |

### 2.6 Commission, Advertising & Monetisation

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ECM-041 | Commission schemes | Define commission by category, seller tier, order value band, and promotional overrides | P1 |
| FR-ECM-042 | Commission calculation | Calculate commission per transaction with taxes and withholding, and post to M20 | P1 |
| FR-ECM-043 | Seller wallet & payouts | Maintain a seller wallet, accrue earnings, deduct commission and fees, and run scheduled payouts | P1 |
| FR-ECM-044 | Payout controls | Apply hold periods, minimum thresholds, dispute holds and bar/unbar controls on payouts | P1 |
| FR-ECM-045 | Paid boost / top listing | Sell time-boxed placement so a seller's profile or listing ranks higher in search | P2 |
| FR-ECM-046 | Advertising placements | Sell page-targeted in-app and portal ad slots (e.g. a laptop engineer advertising only on laptop pages) and checkout-page placements | P2 |
| FR-ECM-047 | Ad delivery & billing | Serve ads, count impressions and clicks, and bill by placement, impression or click | P2 |
| FR-ECM-048 | Monetisation reporting | Report revenue by commission, advertising, boost, registration fee and delivery margin | P1 |

### 2.7 Marketplace Governance

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ECM-049 | Seller performance scorecard | Score sellers on acceptance rate, on-time rate, rework, rating, dispute rate and cancellation | P1 |
| FR-ECM-050 | Automatic consequences | Reduce visibility, restrict categories or suspend automatically when scores fall below thresholds | P2 |
| FR-ECM-051 | Marketplace policy engine | Maintain and version seller policies with acknowledgement tracking | P1 |
| FR-ECM-052 | Liability & insurance | Record seller insurance, liability caps and 1000FiX's residual obligation to the customer | P1 |
| FR-ECM-053 | Regulatory compliance | Apply VAT treatment correctly for marketplace transactions (principal vs agent) per NBR rules | P0 |

*(FR-ECM-054 … FR-ECM-079 cover the seller mobile experience, bulk listing management,
promotions for sellers, marketplace search ranking, seller analytics, and international
seller/customer handling — catalogued in Doc 11.)*

## 3. Key Entities

`fix.mp.seller` · `fix.mp.seller.document` · `fix.mp.seller.agreement` · `fix.mp.listing` ·
`fix.mp.listing.variant` · `fix.ecom.order` · `fix.ecom.order.line` · `fix.fulfilment.order` ·
`fix.mp.job` · `fix.mp.offer` · `fix.mp.chat.thread` · `fix.review` · `fix.review.moderation` ·
`fix.seller.score` · `fix.commission.scheme` · `fix.commission.entry` · `fix.seller.wallet` ·
`fix.payout.run` · `fix.ad.placement` · `fix.ad.campaign` · `fix.dispute.case` ·
`fix.mp.policy`

## 4. Critical Decisions Required Before Build (Wave 7)

| Decision | Owner | Impact |
|---|---|---|
| Principal vs agent model for VAT and liability | CFO + Legal | Determines invoicing structure, VAT treatment and consumer-protection exposure |
| Commission rates by category and tier | CCO | Determines seller economics and platform revenue |
| Settlement cycle and hold period | CFO | Working capital and seller acquisition |
| Whether 1000FiX guarantees marketplace work | CEO + Legal | Determines warranty reserve and brand risk |
| Seller insurance requirement | Legal | Onboarding friction vs risk exposure |

## 5. KPIs

| KPI | Target |
|---|---|
| Approved active sellers | 500 by end of W8 |
| Marketplace share of total job volume | > 25% |
| Seller approval cycle time | < 72 hours |
| Marketplace job completion rate | > 94% |
| Average seller rating | > 4.4/5 |
| Dispute rate | < 1.5% of marketplace jobs |
| Commission + ad revenue | BDT 84 lac/year at steady state |
| Payout accuracy | 100% |

---

# M13 — Rental & Asset-as-a-Service (RNT)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M13 / `RNT` |
| **Status** | ★ New in v2.0 |
| **Priority** | P2 |
| **Wave** | W6 |
| **Delivery layers** | L1 (Odoo rental basis) + L5 (CD-059…062) |
| **Requirements** | FR-RNT-001 … FR-RNT-044 |
| **Effort** | 25 person-weeks |

## 1. Purpose

The business plan commits to renting **eight asset categories**: laptops, cameras, projectors,
tablets, audiovisual equipment, servers, networking equipment and electronic test equipment.
Rental is an asset-intensive business with a completely different economics from repair —
utilisation, condition, deposits, damage recovery and depreciation.

## 2. Functional Areas & Features

### 2.1 Rental Asset Pool

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RNT-001 | Rental asset register | Register every rentable unit with serial, category, specification, acquisition cost, condition grade and current status | P2 |
| FR-RNT-002 | Asset status lifecycle | Track Available · Reserved · Out on Rent · In Transit · Under Service · Quarantined · Retired · Sold | P2 |
| FR-RNT-003 | Category & specification model | Model rentable categories with attributes so customers can select by specification, not just by name | P2 |
| FR-RNT-004 | Accessories & kits | Bundle accessories (chargers, cases, cables, lenses, tripods) and track each item's return | P2 |
| FR-RNT-005 | Asset depreciation link | Link each asset to its fixed-asset record and depreciation schedule in M19 | P2 |
| FR-RNT-006 | Utilisation tracking | Measure days-on-rent vs days-available per asset and per category | P2 |

### 2.2 Reservation & Agreement

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RNT-007 | Availability calendar | Show real-time availability by category and date range across branches | P2 |
| FR-RNT-008 | Reservation | Reserve by category or specific unit, with hold expiry and overbooking controls | P2 |
| FR-RNT-009 | Rental agreement | Generate the agreement with period, tariff, deposit, usage limits, liability terms and e-signature | P2 |
| FR-RNT-010 | Customer eligibility | Check identity, credit standing and rental history before approving a rental | P2 |
| FR-RNT-011 | Corporate framework rentals | Support master agreements with call-off orders for corporate customers | P2 |
| FR-RNT-012 | Long-term / EaaS | Support multi-month equipment-as-a-service arrangements including bundled maintenance | P3 |

### 2.3 Tariffs & Billing

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RNT-013 | Tariff structures | Define hourly, daily, weekly, monthly and custom-period tariffs with volume and duration discounts | P2 |
| FR-RNT-014 | Security deposit | Calculate, collect, hold, and refund or offset deposits | P2 |
| FR-RNT-015 | Usage-based charges | Charge for excess usage where metered (e.g. projector lamp hours, print counts) | P3 |
| FR-RNT-016 | Extension | Extend a rental in-flight with availability check and re-pricing | P2 |
| FR-RNT-017 | Early return | Handle early return with the agreed refund or minimum-period rules | P2 |
| FR-RNT-018 | Late return penalties | Apply overdue charges automatically with escalating notifications | P2 |
| FR-RNT-019 | Recurring invoicing | Invoice long rentals on a recurring cycle through M20 | P2 |

### 2.4 Delivery, Condition & Return

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RNT-020 | Pre-dispatch check | Complete a functional and cosmetic check with photographs before dispatch | P2 |
| FR-RNT-021 | Condition report — out | Produce a signed condition report at handover, including accessories | P2 |
| FR-RNT-022 | Delivery & collection | Create logistics consignments in M03 for delivery and collection | P2 |
| FR-RNT-023 | Condition report — in | Complete the return inspection against the outbound report, itemising differences | P2 |
| FR-RNT-024 | Damage assessment & charging | Quantify damage, price the repair, offset against deposit and invoice the balance | P2 |
| FR-RNT-025 | Loss & theft | Handle non-return with the agreed valuation, insurance claim and legal escalation | P2 |
| FR-RNT-026 | Refurbish-between-rentals | Route returned assets through cleaning, servicing and testing before returning them to the available pool | P2 |

### 2.5 Rental Support & Fleet Health

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RNT-027 | In-rental support | Provide support and swap-out for a failed rental asset within the agreed response time | P2 |
| FR-RNT-028 | Preventive maintenance | Schedule maintenance by calendar or usage for rental assets | P2 |
| FR-RNT-029 | Fleet health & retirement | Track cumulative repair cost per asset and recommend retirement or sale to M14 | P2 |

*(FR-RNT-030 … FR-RNT-044 cover rental portal self-service, insurance products, subscription
rental, and rental analytics — catalogued in Doc 11.)*

## 3. Key Entities

`fix.rental.asset` · `fix.rental.category` · `fix.rental.kit` · `fix.rental.reservation` ·
`fix.rental.agreement` · `fix.rental.line` · `fix.rental.tariff` · `fix.rental.deposit` ·
`fix.condition.report` · `fix.damage.assessment` · `fix.rental.extension` ·
`fix.asset.utilisation`

## 4. KPIs

| KPI | Target |
|---|---|
| Fleet utilisation | > 68% |
| Revenue per asset per month | Category targets set at launch |
| On-time return rate | > 90% |
| Damage recovery rate | > 85% of assessed damage |
| Asset loss rate | < 0.5% per year |
| Rental gross margin | > 55% |

---

# M14 — Trade-In, Refurbishment & Resale (TRF)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M14 / `TRF` |
| **Status** | ★ New in v2.0 |
| **Priority** | P2 |
| **Wave** | W6 |
| **Delivery layers** | L5 (CD-063…066) |
| **Requirements** | FR-TRF-001 … FR-TRF-039 |
| **Effort** | 22 person-weeks |

## 1. Purpose

The Company buys used devices, refurbishes them and resells them with warranty. The business
plan describes the full chain: refurbishment, data wiping and privacy protection, quality
assurance testing, resale and distribution, warranty and customer support, and the
environmentally-friendly rationale. The Service App SOW describes the customer-facing
trade-in quotation flow.

M14 makes this chain traceable — which matters commercially (margin per unit) and legally
(what data was on the device, and what warranty the buyer gets).

## 2. Functional Areas & Features

### 2.1 Trade-In & Acquisition

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-TRF-001 | Trade-in request | Accept a trade-in request with device details, condition self-assessment, photographs and warranty status | P2 |
| FR-TRF-002 | Automated indicative valuation | Produce an indicative price from model, age, condition and market reference data | P2 |
| FR-TRF-003 | Back-office assessment | Route to the assessment team for review, producing a firm offer (the SOW model) | P2 |
| FR-TRF-004 | Offer & acceptance | Present the offer to the customer with validity; capture acceptance | P2 |
| FR-TRF-005 | Physical intake & verification | Verify the device on receipt against the declared condition; revise or withdraw the offer with evidence if it differs | P2 |
| FR-TRF-006 | Ownership & provenance | Verify seller identity and record a provenance chain to deter handling of stolen goods; check IMEI/serial against blocklists where available | P0 |
| FR-TRF-007 | Payment to customer | Pay by mobile money, bank transfer or store credit/wallet, recorded on the customer's profile | P2 |
| FR-TRF-008 | Exchange against purchase | Offset trade-in value against the purchase of another device or service | P2 |
| FR-TRF-009 | Bulk corporate buy-back | Handle corporate fleet buy-backs with lot pricing and reconciliation against the client's asset list | P2 |

### 2.2 Refurbishment

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-TRF-010 | Refurbishment work order | Create a refurbishment work order with a standard scope by device class | P2 |
| FR-TRF-011 | Data destruction | Mandate certified data wiping via M06 before any further processing; block progression without a certificate | P0 |
| FR-TRF-012 | Diagnostics & repair | Run full diagnostics, repair faults and replace consumables, drawing parts from M15 | P2 |
| FR-TRF-013 | Cosmetic restoration | Record cleaning, panel replacement and cosmetic work | P2 |
| FR-TRF-014 | Software & firmware | Reinstall the operating system, apply firmware updates and verify licensing | P2 |
| FR-TRF-015 | Refurbishment cost tracking | Accumulate parts, labour and overhead per unit to determine landed cost | P2 |

### 2.3 Grading & Quality Assurance

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-TRF-016 | Grading standard | Maintain a published grading standard (A / B / C / Parts-only) with objective cosmetic and functional criteria | P2 |
| FR-TRF-017 | QA test protocol | Run the full test protocol — hardware components, software functionality, connectivity, battery health — and record results | P2 |
| FR-TRF-018 | Battery & consumable health | Measure and record battery health and other wear indicators, disclosed at point of sale | P2 |
| FR-TRF-019 | Grade assignment | Assign the final grade from the QA results, with supervisor override requiring justification | P2 |
| FR-TRF-020 | Rejection to recycling | Route units failing refurbishment to M18 recycling with cost write-off | P2 |

### 2.4 Resale

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-TRF-021 | Resale listing | List refurbished units for sale through the e-commerce channel (M12), retail counters and authorised resellers, with grade and disclosed condition | P2 |
| FR-TRF-022 | Grade-based pricing | Price by model, grade, specification and market reference, with ageing markdowns | P2 |
| FR-TRF-023 | Refurbished warranty | Apply the defined warranty on refurbished units and track the resulting liability | P1 |
| FR-TRF-024 | Provenance disclosure | Give the buyer a device history report: refurbishment date, work performed, grade, test results, warranty | P2 |
| FR-TRF-025 | Reseller/distribution channel | Manage sales through partner resellers with pricing, allocation and settlement | P3 |
| FR-TRF-026 | Return & post-sale support | Handle returns and warranty claims on refurbished units, feeding quality data back to grading | P2 |

### 2.5 Inventory & Profitability

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-TRF-027 | Refurb inventory | Track refurbished stock separately from new parts inventory, by grade and ageing | P2 |
| FR-TRF-028 | Unit economics | Report acquisition cost, refurbishment cost, sale price and margin per unit and per model | P2 |
| FR-TRF-029 | Ageing & markdown | Age refurbished stock and trigger markdown or channel-shift rules | P2 |
| FR-TRF-030 | Harvest for parts | Convert unsellable units into harvested parts, adding them to M15 with a refurbished classification | P2 |

*(FR-TRF-031 … FR-TRF-039 cover the trade-in mobile experience, market price feeds, donation
programmes and refurbishment analytics — catalogued in Doc 11.)*

## 3. Key Entities

`fix.tradein.request` · `fix.tradein.valuation` · `fix.tradein.offer` · `fix.provenance.record` ·
`fix.refurb.order` · `fix.refurb.cost.line` · `fix.grading.standard` · `fix.grading.result` ·
`fix.qa.test.result` · `fix.refurb.unit` · `fix.resale.listing` · `fix.refurb.warranty` ·
`fix.harvest.record`

## 4. KPIs

| KPI | Target |
|---|---|
| Trade-in offer acceptance rate | > 55% |
| Average refurbishment cycle time | < 5 days |
| Refurbishment yield (units sellable) | > 88% |
| Gross margin per refurbished unit | > 22% |
| Refurbished return rate | < 4% |
| Data destruction certificates issued | 100% of units |
| Refurbished stock ageing > 90 days | < 12% |

---

*Next document: `07_Pillar_C_Supply_Chain_and_Asset_Modules.md`*
