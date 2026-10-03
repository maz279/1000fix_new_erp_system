---
id: FIX-ERP2-M09
module_id: M09
module_code: WTY
module_name: Warranty, Protection Plans & Claims
category: C — Commercial, Pricing & Revenue
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Finance Director
system_owner: Commercial Squad
priority: P0
wave: W4
---

# M09 — Warranty, Protection Plans & Claims
### Category C · Code `WTY` · Existing module, retained and expanded

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M09 |
| **Module code** | `WTY` |
| **Category** | C — Commercial, Pricing & Revenue |
| **Status** | Existing (retained) — expanded in v2.1 to cover seven protection product families and full brand recovery |
| **Priority** | **P0** — carries the single largest quantified benefit in the business case |
| **Delivery wave** | W4 (Months 14–18) |
| **Business owner** | Finance Director |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `product`, `account`) + L2 (OCA `partner_*`, `document_*`) + L5 (custom) |
| **Custom modules** | `cd_warranty_register`, `cd_protection_plan`, `cd_claim_engine`, `cd_brand_recovery`, `cd_claim_reconciliation` |
| **Requirement range** | FR-WTY-001 … FR-WTY-066 |
| **Requirement count** | **66** *(measured; register estimate 48)* |
| **Effort estimate** | **36 person-weeks** *(measured; register estimate 28 PW)* |
| **Depends on** | M37 Catalogue · M17 Asset Registry · M01 SRM · M11 Pricing · M33 Party Master · M24 Document · M28 Integration · M29 Identity |
| **Depended on by** | M01, M31, M02, M04, M20, M53, M19, M15, M23, M36, M38, M14, M25, M26, M40 · Portal **P08** |

---

## 2. Purpose

M09 owns two things that look similar and behave very differently.

**Warranty entitlement** — the answer to "is this repair free, and who pays for it?" It covers
manufacturer warranty on a customer's device, the repair warranty 1000FiX grants on its own
work, and coverage under any protection product the customer has bought.

**Claim recovery** — the money 1000FiX gets back from 17+ brand partners for warranty work it
has already performed and already paid for in labour and parts. This is not a service process;
it is a receivable process with a technical evidence burden, and it is where the company
currently loses the most money.

It also owns the **seven protection product families** that 1000FiX sells in its own right —
warranty extensions, accidental damage protection and the rest — which are a margin business
rather than a recovery business, with entirely different economics.

### Why It Exists

The current position, as documented in the BRD, is severe. Warranty claims are compiled
manually from paper, weeks after the service. Roughly **half of claims are submitted 30 to 90
days late**, by which point many brands' submission windows have closed. Estimated warranty
revenue leakage is **15–20%**. There is no evidence pack, so rejections are frequent and
un-appealable. There is no reconciliation, so nobody knows which approved claims were never
paid.

The business case attributes **BDT 100 lac/year** to warranty revenue recovery — the largest
single benefit line in the programme. M01 makes it possible by capturing evidence at the point
of service; M09 realises it.

On the protection-product side, 1000FiX sells extended warranty and damage protection with an
**attach rate that is not measured at all** and no reserve discipline. Selling a multi-year
obligation without tracking the reserve against it is how protection programmes become
liabilities.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.9 (BR-WTY-001…024) | Warranty validation, claim creation, evidence, submission, tracking, reconciliation |
| ERP BRD §10.1 BRU-SRM-02, 17 | Warranty orders require active warranty; before/after photographs mandatory and blocking |
| ERP BRD §6 Pain Points | 30–90 day submission delay; 15–20% leakage |
| ERP URD §9 (US-WTY-*) | Warranty officer and brand partner stories |
| `05-04` §6 SOD-11 | Raising a claim and approving its write-off are incompatible |
| Business Plan §Warranty Products | The seven protection product families |
| Company Profile §Brand Partnerships | 17+ authorised brand partners, each with its own claim rules and portal |
| `04-00` P08 Brand Partner Portal | Claim submission, decision, reconciliation and evidence access for brands |
| M01 §5.5, §11 AUT-SRM-07 | Evidence pack assembled at service; claim-eligible event emitted on delivery |
| `_CATEGORY_OVERVIEW.md` §7, §8 | Seven protection families; claim and leakage KPIs |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The warranty register: every warranty instance against every device, from every source |
| 2 | Manufacturer warranty capture, validation and proof-of-purchase handling |
| 3 | Repair warranty issued by 1000FiX on its own work, and its consumption by rework |
| 4 | Warranty entitlement evaluation at intake — the authoritative "who pays" verdict |
| 5 | Warranty transfer on device ownership change, and void conditions |
| 6 | The seven protection product families: sale, activation, policy issue, servicing, cancellation |
| 7 | Protection product eligibility, inspection requirements, waiting periods and exclusions |
| 8 | Protection claim handling: intake, assessment, excess/deductible, approval, fulfilment, limits |
| 9 | Claim reserve, loss-ratio tracking and protection-programme profitability |
| 10 | **Brand claim creation** from completed warranty service, with automatic evidence assembly |
| 11 | Brand-specific claim rules, formats, code mappings, submission windows and channels |
| 12 | Claim submission — portal, API, file, email — and submission-state tracking |
| 13 | Claim decisions: approval, partial approval, rejection, request for information, resubmission |
| 14 | Rejection analysis, appeal handling and root-cause feedback to service operations |
| 15 | Claim ageing, chasing and escalation to brand partners |
| 16 | **Reconciliation** of claimed, approved, paid and outstanding amounts per brand |
| 17 | Consignment and warranty-parts handling: brand-supplied parts, defective returns, part recovery |
| 18 | Recall and service-campaign execution against affected serial ranges |
| 19 | Warranty cost and recovery accounting instructions to M19/M20 |
| 20 | Brand partner performance measurement — decision time, approval rate, payment time |
| 21 | The P08 Brand Partner Portal domain logic |
| 22 | Fraud and abuse detection on both inbound protection claims and outbound brand claims |
| 23 | The warranty-check API used at intake, in the customer portal and on the storefront |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| The protection product *definition* (coverage, exclusions, term, limits) | **M37** Catalogue | A product definition is a catalogue object; the policy instance is M09's |
| Protection product *pricing* | **M11** Pricing | Price is a commercial decision |
| The sale document for a protection product | **M36** Quotation / **M38** E-Commerce | M09 receives an accepted sale and issues the policy |
| Contract entitlement (AMC, MSP, RAMC) | **M08** Contract | A contract is a different entitlement instrument with no third-party recovery |
| Service execution, diagnosis, repair, QC and evidence *capture* | **M01** / **M31** / **M02** | M09 consumes the evidence; it does not capture it |
| The device record and its ownership history | **M17** Asset Registry | Warranty attaches to a device; the device is not owned by M09 |
| Cash receipt, ledger posting and receivable ageing | **M20** / **M19** | Only Category G creates financial documents and receives cash |
| Parts stock, valuation and consignment *stock* movement | **M15** Inventory | M09 governs the warranty treatment; M15 moves the goods |
| Recurring billing of a protection subscription | **M39** Subscription | Where a plan is billed monthly, M39 bills it |
| Brand partner *relationship*, rate negotiation and commercial standing | **M40** Partner *(relationship)* / **M11** *(rates)* / **M08** *(agreement)* | M09 executes claims within an agreement it does not own |
| Quality investigation and CAPA arising from failure patterns | **M23** Quality | M09 raises the signal; M23 investigates |
| Evidence pack *assembly*, sealing, retention and controlled release | **M24** Document | M09 declares what a claim pack must contain; M24 assembles it by reference, seals it and retrieves it — one assembly mechanism serves claims, audits, disputes and regulators |
| Insurance underwriting and risk transfer | *Out of ERP scope* | If protection products are underwritten externally, the ERP records the arrangement; it does not underwrite |

### 3.3 Shared Concepts

| Concept | M09's Role | Owning Module |
|---|---|---|
| Warranty register entry | **Owner** | M09 |
| Protection policy instance | **Owner** | M09 |
| Protection product definition | Consumes | M37 |
| Brand claim | **Owner** | M09 |
| Brand reimbursement rate | Consumes for valuation | M11 |
| Evidence pack | **Owner** of the *composition* — which artefacts a claim requires, per brand rules. M01 captures the contents; M24 assembles, seals and retrieves | M01 (capture) / M09 (composition) / **M24 (assembly)** |
| Device | References | M17 |
| Repair warranty | **Owner** of the register; M01 issues at handover | M09 |
| Claim receivable | Instructs; M20 posts and collects | M20 |
| Consignment parts | Governs warranty treatment; M15 holds stock | M15 |
| Brand partner portal | **Owner** of the domain logic | M09 (P08) |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA** — Warranty Claim Processing, warranty determination on the service order | Claim creation from a service confirmation, validation against product master, serial and coverage rules, structured approval chains, automatic financial posting and credit notes | **Claim creation at the point of service confirmation** rather than as a later back-office exercise, and **entitlement validation against serial and coverage rules** | SAP's recall and vehicle-centric claim modelling |
| **SAP** — Supplier / vendor recovery | Recovering warranty cost from the supplier of a defective component | The **recovery claim created automatically at the point of approval**, with deadline tracking — the discipline the industry identifies as the most under-leveraged part of warranty operations | Full multi-tier supplier recovery; our recovery is single-tier to the brand |
| **Oracle / Dynamics 365 service warranty** | Warranty registration, entitlement check at case creation | Entitlement check as a gate, not a lookup | — |
| **IFS Cloud** — warranty verification at intake | Verifying warranty against rules at intake to prevent revenue loss | **Verification at intake, before work begins** — adopted directly, and already reflected in M01 FR-SRM-006 | — |
| **Dedicated warranty platforms** (Tavant, PCMI, OnPoint, Intellinet class) | Claim lifecycle automation, validation rules, fraud detection, supplier recovery, reserve and loss-ratio accounting, dealer/servicer portals | **Rule-based claim validation before submission**, **fraud scoring**, **reserve and loss-ratio tracking on protection products**, and a **partner portal as the primary claim channel**. Industry evidence: automated recovery moves recovery rates from under 60% to above 90% | Buying a platform — the licence cost is not justified at our claim volume, and the brand-specific rule variety is ours to model anyway |
| **Extended-warranty administration practice** (PCMI, OnPoint) | Contract writing, reserve accounting, loss ratio, claims administration, cancellation and refund handling | **Reserve per policy and loss-ratio measurement per product family** — the discipline that keeps a protection programme solvent. Industry benchmark: a well-run programme holds a **30–50% loss ratio** | Actuarial underwriting inside the ERP; if underwriting is external, M09 records the cession |
| **OEM claim-approval benchmarks** | 24-hour claim approval targets; retail-rate reimbursement pressure | **Ageing and chasing as automated processes**, and brand-partner performance measurement including decision and payment time — we measure our partners as they measure us | — |

**Design position.** 1000FiX differs from the benchmarks in six ways.

First, **the claim is created by the service process, not by the finance process**. M01 emits a
claim-eligible event on delivery of a warranty order; M09 creates the claim within minutes with
the evidence pack already assembled. The 30–90 day delay is not a staffing problem; it is an
architectural one, and this is the architectural fix. The target is **> 95% of claims submitted
within 72 hours**.

Second, **a claim cannot be submitted until it passes the brand's own rules**. Each of the 17+
brands has different mandatory fields, code schemes, photograph requirements, labour-time
allowances and submission windows. M09 validates against the specific brand's rule set before
submission, because a rejected claim resubmitted late is often a claim lost.

Third, **evidence is assembled, not gathered**. Photographs, diagnostic results, fault codes,
parts consumed, technician certification and proof of purchase are already in the system from
M01, M31, M17 and M22. The evidence pack is a projection, not a collection exercise.

Fourth, **reconciliation is a first-class process**. Claims are not "submitted and hoped for".
Submitted, approved, part-approved, rejected, paid and short-paid amounts are reconciled per
brand per period, and the difference is a receivable that ages and is chased. Warranty leakage
is as often a *collection* failure as a *submission* failure.

Fifth, **protection products carry a reserve from the day they are sold**. Selling a two-year
accidental damage plan creates a two-year obligation. M09 holds a reserve per policy, tracks
incurred claims against it, and reports the loss ratio per family, so the programme is managed
as an insurance-like business rather than as free margin.

Sixth, **fraud control runs in both directions**. Inbound: protection claims for pre-existing
damage, staged damage and multiple claims on one device. Outbound: claims for work not
performed, inflated labour and parts claimed but not fitted. Both are real risks in this market;
both are scored, sampled and audited.

---

## 5. Functional Areas & Features

### 5.1 Warranty Register & Entitlement

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WTY-001 | Unified warranty register | Maintain every warranty instance against a device from every source — manufacturer, extended, protection product, repair warranty, contract-linked, seller-provided — in one register | P0 | L5 |
| FR-WTY-002 | Manufacturer warranty capture | Record manufacturer warranty from purchase evidence, brand data feed, serial-range rules or manual entry with a declared confidence level | P0 | L5 |
| FR-WTY-003 | Proof of purchase | Capture, store and validate the purchase invoice, receipt or activation record, and flag warranty asserted without evidence | P0 | L5 |
| FR-WTY-004 | Serial and IMEI validation | Validate warranty status by serial, IMEI or asset tag against brand rules and, where available, brand APIs | P0 | L5 |
| FR-WTY-005 | Entitlement verdict at intake | Return a single authoritative verdict — covered by whom, for what, with what exclusions and what customer liability — in under 300 ms | P0 | L5 |
| FR-WTY-006 | Multi-source precedence | Resolve overlapping coverage (manufacturer + protection plan + contract + repair warranty) by a declared precedence, and state which instrument pays | P0 | L5 |
| FR-WTY-007 | Repair warranty issue | Issue the repair warranty on completion of 1000FiX work, per the M37 service default, and register it against the device | P0 | L5 |
| FR-WTY-008 | Repair warranty consumption | Recognise a return within the repair-warranty window as covered rework, at zero customer charge, linked to the original order | P0 | L5 |
| FR-WTY-009 | Warranty transfer | Transfer warranty on device ownership change where the terms permit, and refuse it where they do not | P1 | L5 |
| FR-WTY-010 | Void and exclusion conditions | Record void conditions — unauthorised repair, physical or liquid damage, tampering, seal breach — with evidence, and apply them at the entitlement verdict | P0 | L5 |
| FR-WTY-011 | Warranty expiry management | Track expiry across the estate, notify customers before expiry, and offer extension through M36/M38 | P1 | L5 |
| FR-WTY-012 | Customer-visible warranty | Present warranty status, expiry and coverage in P01 and P04, with a public serial-based check | P0 | L5 |
| FR-WTY-013 | Bulk warranty registration | Register warranty in bulk from a brand feed, a corporate asset upload or a retail sales file | P1 | L5 |
| FR-WTY-014 | Warranty history | Retain the complete warranty and claim history of a device across owners and service events | P1 | L5 |

### 5.2 Protection Products — Sale & Policy

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WTY-015 | Seven protection families | Sell and administer Standard Warranty Extension, Accidental Damage Protection, Extended Repair Coverage, Mobile Device Protection, Home Appliance Protection, Computer & Laptop Care and Customised Coverage from configuration alone | P0 | L5 |
| FR-WTY-016 | Eligibility rules | Enforce eligibility by device age, condition, value, category, prior claims and purchase recency before a plan can be sold | P0 | L5 |
| FR-WTY-017 | Pre-sale inspection | Require and record a device inspection with photographic evidence where the product demands it, and refuse activation without it | P0 | L5 |
| FR-WTY-018 | Policy issue | Issue a policy on accepted sale with a unique number, term, coverage schedule, limits, excess and exclusions, in Bengali and English | P0 | L5 |
| FR-WTY-019 | Waiting period | Apply a waiting period before cover commences, and reject claims arising within it | P0 | L5 |
| FR-WTY-020 | Coverage limits | Enforce per-claim limits, aggregate limits, claim-count limits and depreciation schedules | P0 | L5 |
| FR-WTY-021 | Excess and deductible | Compute and collect the customer excess at claim, before fulfilment | P0 | L5 |
| FR-WTY-022 | Plan cancellation and refund | Cancel a plan on request or on breach, computing a pro-rata or short-rate refund per the terms, and instruct M20 | P1 | L5 |
| FR-WTY-023 | Plan transfer | Transfer a plan with the device where the terms permit | P2 | L5 |
| FR-WTY-024 | Renewal and continuation | Offer renewal or continuation before expiry, with re-eligibility assessment | P1 | L5 |
| FR-WTY-025 | Attach-rate support at point of sale | Present eligible protection products at intake, at handover, in checkout and in the portal, with the benefit stated in plain Bengali | P1 | L5 |
| FR-WTY-026 | Underwriting arrangement record | Record any external underwriting or reinsurance arrangement, the cession basis and the retained risk | P2 | L5 |

### 5.3 Protection Claims (Inbound)

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WTY-027 | Protection claim intake | Accept a protection claim from portal, app, branch, contact centre or field, capturing incident date, cause, circumstances and evidence | P0 | L5 |
| FR-WTY-028 | Coverage assessment | Assess the claim against the policy's coverage, exclusions, waiting period, limits and remaining balance, and produce a reasoned verdict | P0 | L5 |
| FR-WTY-029 | Damage assessment | Record technical assessment of the damage, its consistency with the declared cause, and repair-versus-replace economics | P0 | L5 |
| FR-WTY-030 | Approval workflow | Route protection claims for approval by value band, with a documented decision and reason | P0 | L5 |
| FR-WTY-031 | Fulfilment routing | Fulfil an approved claim as repair (M01), replacement (M15/M14), cash settlement (M20) or refund, and track it to completion | P0 | L5 |
| FR-WTY-032 | Excess collection | Collect the excess before fulfilment begins and block fulfilment until it is received or waived with approval | P0 | L5 |
| FR-WTY-033 | Claim limits enforcement | Decrement the policy's remaining limits on settlement and refuse claims exceeding them | P0 | L5 |
| FR-WTY-034 | Claim rejection and appeal | Reject with a governed reason, notify the customer in plain language, and support a single structured appeal | P1 | L5 |
| FR-WTY-035 | Fraud scoring (inbound) | Score protection claims for fraud indicators — pre-existing damage, claim timing, repeat claims, inconsistent evidence — and route high scores for investigation | P1 | L5 |
| FR-WTY-036 | Reserve movement | Establish a reserve at policy issue, adjust it on claim notification, and release it on settlement or expiry | P1 | L5 |
| FR-WTY-037 | Loss ratio measurement | Compute the loss ratio per protection family, cohort and channel, continuously | P1 | L5 |

### 5.4 Brand Claims (Outbound Recovery)

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WTY-038 | Automatic claim creation | Create a brand claim automatically within minutes of a warranty service order being delivered, with the evidence pack already assembled | P0 | L5 |
| FR-WTY-039 | Evidence pack composition | Declare, per brand, the artefacts a claim pack must contain — before/after photographs, diagnostic result, fault codes, parts consumed with serials, labour time, technician certification, proof of purchase, customer signature — and request its assembly and sealing from M24 | P0 | L5 |
| FR-WTY-040 | Brand rule engine | Hold each brand's claim rules — mandatory fields, code scheme, photograph requirements, labour allowance, part eligibility, submission window, resubmission policy — as configuration | P0 | L5 |
| FR-WTY-041 | Pre-submission validation | Validate a claim against the specific brand's rule set and block submission until it passes, listing every failure in one view | P0 | L5 |
| FR-WTY-042 | Claim valuation | Value the claim using the M11 brand reimbursement rate card version in force on the service date, for labour and parts separately | P0 | L5 |
| FR-WTY-043 | Fault code translation | Translate 1000FiX fault codes to the brand's claim codes using the M37 brand mapping | P0 | L5 |
| FR-WTY-044 | Multi-channel submission | Submit via brand API, brand portal (assisted), structured file, or the P08 portal, and record the submission reference and timestamp | P0 | L5 |
| FR-WTY-045 | Batch submission | Batch claims per brand per cycle where the brand requires it, with per-claim outcome tracking within the batch | P1 | L5 |
| FR-WTY-046 | Submission window enforcement | Track each brand's submission deadline from the service date, escalate before it, and flag any claim at risk of lapsing | P0 | L5 |
| FR-WTY-047 | Decision capture | Record approval, partial approval, rejection or request-for-information against each claim, with the brand's reason and amount | P0 | L5 |
| FR-WTY-048 | Rejection handling | Classify rejections by reason, route correctable ones for rework and resubmission within the window, and escalate systemic causes to M23 | P0 | L5 |
| FR-WTY-049 | Appeal management | Manage appeals with additional evidence, tracked to a decision | P1 | L5 |
| FR-WTY-050 | Claim ageing and chasing | Age claims by state, chase brands automatically at defined intervals, and escalate to the account owner and CCO | P0 | L5 |
| FR-WTY-051 | Fraud control (outbound) | Detect and block claims for work not evidenced, parts claimed but not issued, duplicate serials and labour beyond standard allowance | P0 | L5 |

### 5.5 Reconciliation, Parts & Campaigns

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WTY-052 | Claim receivable | Raise the claim receivable in M20 on approval, at the approved value, referenced to the claim | P0 | L5 |
| FR-WTY-053 | Remittance matching | Match brand remittance advice to claims, identify short payments and unmatched items, and drive them to resolution | P0 | L5 |
| FR-WTY-054 | Period reconciliation | Reconcile claimed, approved, rejected, paid and outstanding amounts per brand per period, and produce a signed statement | P0 | L5 |
| FR-WTY-055 | Write-off governance | Require approval to write off an unrecoverable claim, with SOD enforcement between the claim raiser and the write-off approver | P0 | L5 |
| FR-WTY-056 | Consignment parts governance | Track brand-supplied consignment parts: receipt, consumption on claims, reporting, replenishment and liability | P1 | L5 |
| FR-WTY-057 | Defective part return | Manage the return of defective parts to the brand where required, with tracking and proof, and link it to the claim's payability | P1 | L5 |
| FR-WTY-058 | Old-part retention rules | Enforce brand-specific retention and destruction rules for replaced parts, with evidence | P1 | L5 |
| FR-WTY-059 | Recall and campaign execution | Execute a brand recall or service campaign against affected serial ranges as a batch of service orders, tracked to completion and claimed as a campaign | P1 | L5 |
| FR-WTY-060 | Campaign claim treatment | Apply campaign-specific claim rules, rates and reporting distinct from standard claims | P2 | L5 |
| FR-WTY-061 | Brand partner performance | Measure each brand on decision time, approval rate, rejection reasons, payment time and short payments, and publish it internally | P1 | L5 |
| FR-WTY-062 | Warranty cost accounting | Instruct M19/M20 on warranty cost, recovery, reserve movement and write-off, with correct account determination | P0 | L5 |
| FR-WTY-063 | P08 brand partner portal logic | Serve brand partners: claim queue, evidence access, decision actions, bulk actions, remittance upload, reconciliation and performance view | P0 | L5 |
| FR-WTY-064 | Brand data isolation | Ensure a brand partner sees only claims and service data relating to their own brand *(`05-04` EA-05)* | P0 | L5 |
| FR-WTY-065 | Failure-pattern signalling | Detect abnormal failure rates by model, part or component and raise the signal to M23 and the brand | P1 | L5 |
| FR-WTY-066 | Warranty analytics | Report leakage, submission timeliness, approval rate, recovery rate, days-to-cash and attach rate across brands, branches and products | P0 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Entitlement verdict performance** | Warranty check ≤ 300 ms p95 at intake under 250,000+ monthly interactions, served from a read model |
| T-02 | **Evidence pack as a projection** | The pack is assembled by reference from M01/M31/M17/M22 artefacts, sealed with a content hash, and never re-collected |
| T-03 | **Brand rules as data** | Every brand's rule set is configuration. Adding an 18th brand partner requires no code |
| T-04 | **Claim creation latency** | A claim exists within 5 minutes of a warranty order being delivered, driven by the outbox, not by a nightly job |
| T-05 | **Submission idempotency** | Re-submitting the same claim after a transport failure never creates a duplicate at the brand |
| T-06 | **Rate-version pinning** | A claim is valued at the brand rate-card version in force on the service date, permanently pinned |
| T-07 | **Deadline scheduler** | Submission-window deadlines are evaluated continuously, not by scanning the full claim table |
| T-08 | **Reconciliation determinism** | Remittance matching is deterministic and fully auditable; unmatched items are surfaced, never absorbed |
| T-09 | **Reserve ledger** | Protection reserve is an append-only movement ledger; the balance is derived, never edited |
| T-10 | **External portal isolation** | P08 brand access is scoped by brand at the record-rule layer; scope cannot be widened by request parameters *(`05-04` EA-11)* |
| T-11 | **Attachment handling** | Claim evidence images are compressed, malware-scanned, stored in object storage and referenced, with brand-specific format and size transformation at submission |
| T-12 | **Retry and dead-letter** | Failed brand submissions retry with backoff and land in a dead-letter queue that a human works, never silently dropped |
| T-13 | **Fraud scoring isolation** | Scores are advisory signals attached to a claim, never automatic rejections, and every score is explainable |
| T-14 | **Audit completeness** | Every claim state change, valuation, decision and write-off is audited with actor and reason, append-only |
| T-15 | **Performance envelope** | Claim creation ≤ 2 s · evidence pack assembly ≤ 5 s · brand claim queue with 5,000 open claims ≤ 2 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M09 |
|---|---|---|
| **Warranty officer** | Compiles claims manually from paper weeks later; chases brands by email; cannot say what is outstanding | Works a validated claim queue; submission is automatic; ageing and chasing are systematic |
| **Service centre agent** | Guesses whether a device is in warranty; calls someone | Gets an authoritative verdict at intake in under a second, with the customer's liability stated |
| **Technician** | Does not know that a missing photograph will cost the company the claim | Cannot close a warranty job without the evidence the claim needs — the gate is at the point of work |
| **Branch manager** | Has no visibility of claim value generated or lost by the branch | Sees claim value, rejection rate and rejection causes for the branch |
| **Finance officer** | Cannot reconcile warranty receipts to claims | Reconciles per brand per period with unmatched items surfaced |
| **Finance Director** | Estimates warranty leakage at 15–20% with no way to reduce it | Measures it, and sees it fall |
| **Brand partner** | Receives incomplete claims by email, weeks late | Receives complete, coded, evidenced claims in the P08 portal within 72 hours and decides in bulk |
| **Customer** | Argues about whether a repair is covered | Sees warranty status in the app, and the coverage decision with its reason |
| **Retail / counter staff** | Never offers a protection product | Sees eligible protection products at intake and handover with the benefit in plain Bengali |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Warranty revenue recovery** | Automatic claim creation on delivery with the evidence pack assembled; brand-rule validation before submission; systematic chasing and reconciliation | **BDT 100 lac/year** — the largest single benefit line in the programme *(business case §6.2)* |
| **Leakage reduction** | Submission within the window, first-time-right claims, and reconciliation of short payments | Warranty revenue leakage **15–20% → < 2%** *(category KPI)* |
| **Submission timeliness** | Event-driven creation replaces manual compilation | Claims submitted within 72 hours: **~50% at 30–90 days → > 95%** |
| **Claim approval rate** | Brand-specific validation and complete evidence remove the dominant rejection causes | Approval rate to **> 92%** *(P08 KPI)* |
| **Days to cash** | Ageing, chasing and reconciliation as automated processes | Service-to-reimbursement **< 45 days** *(P08 KPI)* |
| **Protection product attach rate** | Eligible products presented at every touchpoint with plain-language benefit | Attach rate from unmeasured to **> 18%** *(category KPI)* |
| **Protection programme solvency** | Reserve per policy and loss-ratio measurement per family | Keeps the loss ratio inside the industry-benchmark **30–50%** band, protecting margin on a growing obligation book |
| **Fraud avoidance** | Bidirectional scoring on inbound protection claims and outbound brand claims | Avoids both leakage and the far larger risk of losing authorised-service status |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Retention of authorised-service status** | 17+ brand authorisations are the foundation of the business. They are lost through poor claim discipline, weak evidence and quality complaints — all of which M09 addresses directly |
| **Credibility with brand partners** | A partner receiving complete, coded, timely claims through a portal treats 1000FiX differently from one receiving emailed photographs |
| **Evidence culture** | Making the evidence pack a hard gate at the point of work changes technician behaviour permanently, and the same evidence settles customer disputes |
| **Customer trust** | A clear, reasoned, fast coverage decision is the difference between a satisfied customer and a public complaint |
| **Financial integrity** | Warranty receivable becomes a real, ageing, reconciled asset instead of an optimistic estimate |
| **Consumer-protection compliance** | Protection products are consumer contracts; clear terms, honest exclusions and a documented claims process are a regulatory as well as a commercial requirement |
| **Failure intelligence** | Claim data reveals which models and components fail, feeding M23 quality, M43 demand planning and the brand's own engineering |

---

## 8. Lifecycle & State Model

M09 owns three lifecycles. The **brand claim** is shown in full because it carries the money.

### 8.1 Brand Claim

```
            ┌──────────────┐
            │   ELIGIBLE   │ warranty order delivered; claim auto-created
            └──────┬───────┘
                   │ evidence pack assembled
            ┌──────▼───────┐
            │  ASSEMBLED   │
            └──────┬───────┘
                   │ brand rule validation
        ┌──────────┴──────────┐
        │                     │ fails
   passes                ┌────▼─────────┐
        │                │  BLOCKED     │──► remediate ──┐
        │                │ (failures    │                │
        │                │  listed)     │◄───────────────┘
        │                └──────────────┘
   ┌────▼──────┐
   │ VALIDATED │
   └────┬──────┘
        │ submit (API / portal / file / batch)
   ┌────▼──────┐
   │ SUBMITTED │  submission reference and timestamp recorded
   └────┬──────┘
        │
   ┌────┴───────────┬────────────────┬──────────────────┐
   ▼                ▼                ▼                  ▼
┌─────────┐  ┌──────────────┐  ┌──────────┐   ┌──────────────────┐
│ APPROVED│  │ PART-APPROVED│  │ REJECTED │   │ INFO REQUESTED   │
└────┬────┘  └──────┬───────┘  └────┬─────┘   └────────┬─────────┘
     │              │               │                   │ respond
     │              │        ┌──────┴──────┐            │
     │              │        │  APPEALED   │◄───────────┘
     │              │        └──────┬──────┘
     │              │               │ decision
     └──────┬───────┴───────────────┘
            │ receivable raised in M20
     ┌──────▼──────┐
     │  RECEIVABLE │
     └──────┬──────┘
            │ remittance matched
     ┌──────▼──────┐        ┌────────────────┐
     │    PAID     │        │  SHORT-PAID    │──► dispute ──► resolved
     └──────┬──────┘        └────────┬───────┘
            │                        │
            └────────┬───────────────┘
                     ▼
              ┌─────────────┐
              │   CLOSED    │
              └─────────────┘

  Terminal exceptions: LAPSED (submission window missed) · WRITTEN OFF (approved
  write-off, SOD-11 enforced) · CANCELLED (service order cancelled or reclassified).
```

### 8.2 Protection Policy

```
QUOTED ──► SOLD ──► INSPECTION (if required) ──► ACTIVE (after waiting period)
   │                      │ failed
   │                      ▼
   │                  DECLINED
   │
ACTIVE ──► CLAIMED (one or many) ──► ACTIVE (limits reduced)
ACTIVE ──► EXHAUSTED (limits consumed)
ACTIVE ──► CANCELLED (refund computed) · LAPSED (non-payment) · EXPIRED (term end)
                                  └──► CLOSED (reserve released)
```

### 8.3 Warranty Register Entry

```
REGISTERED ──► ACTIVE ──► EXPIRED
                 │
                 ├──► VOIDED (void condition evidenced)
                 └──► TRANSFERRED (new owner, where terms permit)
```

### Transition Guards — Brand Claim

| From | To | Guard | Actor |
|---|---|---|---|
| — | Eligible | Warranty-type service order reaches Delivered | System (M01 event) |
| Eligible | Assembled | All mandatory evidence artefacts present and referenceable | System |
| Assembled | Validated | Brand rule set passes in full; valuation computed at the pinned rate version | System |
| Assembled | Blocked | Any brand rule fails; every failure listed with a remediation action | System |
| Blocked | Assembled | Remediation completed (evidence added, coding corrected) | Warranty Officer, branch |
| Validated | Submitted | Within the brand's submission window; transport confirmed | System / Warranty Officer |
| Submitted | Approved / Part-Approved / Rejected / Info Requested | Brand decision received via API, portal or file | Brand partner (P08) |
| Rejected | Appealed | Rejection is classified as appealable and additional evidence exists | Warranty Officer |
| Approved / Part-Approved | Receivable | Receivable raised in M20 at the approved value | System |
| Receivable | Paid / Short-Paid | Remittance matched | System |
| Short-Paid | Closed | Difference recovered, or written off with approval | Finance Manager |
| Any | Lapsed | Submission window elapsed without submission | System |
| Any | Written Off | Write-off approved; raiser ≠ approver *(SOD-11)* | Finance Manager / CFO |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-WTY-01 | A warranty-type service order can only be created if warranty is active at the service request date *(BRU-SRM-02)* | **H** | Warranty Officer |
| BRU-WTY-02 | Before and after photographs are mandatory on every warranty order; the order cannot close without them *(BRU-SRM-17)* | **H** | Warranty Officer |
| BRU-WTY-03 | A brand claim is created automatically within 5 minutes of a warranty order being delivered | **C** | Finance Director |
| BRU-WTY-04 | A claim cannot be submitted until it passes the specific brand's rule set in full | **H** | Finance Director |
| BRU-WTY-05 | A claim is valued at the brand reimbursement rate-card version in force on the service date | **C** | Finance Director |
| BRU-WTY-06 | A claim approaching its brand submission window is escalated; a lapsed claim generates a mandatory incident record | **H** | Finance Director |
| BRU-WTY-07 | Raising a claim and approving its write-off cannot be performed by the same person *(SOD-11)* | **H** | CFO |
| BRU-WTY-08 | A brand partner sees only claims and service data relating to their own brand *(EA-05)* | **H** | CTO |
| BRU-WTY-09 | A claim for work with no evidence of parts issued or labour recorded is blocked, not merely flagged | **H** | Finance Director |
| BRU-WTY-10 | Only a certified technician's work is claimable where the brand requires certification; assignment is already gated by BRU-SRM-09 | **H** | Quality Manager |
| BRU-WTY-11 | A protection product cannot be activated without the eligibility check and, where required, a recorded pre-sale inspection | **H** | CCO |
| BRU-WTY-12 | A protection claim arising within the waiting period is rejected | **H** | CCO |
| BRU-WTY-13 | The customer excess is collected before fulfilment begins, unless waived with recorded approval | **H** | Finance Manager |
| BRU-WTY-14 | Settled protection claims decrement the policy's remaining limits; claims beyond the limit are refused | **C** | CCO |
| BRU-WTY-15 | A reserve is established at policy issue and released only on settlement, expiry or cancellation | **C** | CFO |
| BRU-WTY-16 | Repair warranty applies automatically to a return within its window and is charged to no one but 1000FiX | **C** | Ops Director |
| BRU-WTY-17 | A void condition must be evidenced before it is applied to refuse coverage | **H** | Quality Manager |
| BRU-WTY-18 | Consignment parts consumed on a claim are reported to the brand in the same cycle as the claim | **C** | Inventory Manager |
| BRU-WTY-19 | Where the brand requires defective-part return, the claim is not treated as recoverable until return is evidenced | **H** | Warranty Officer |
| BRU-WTY-20 | A claim rejected for a correctable reason is remediated and resubmitted within the remaining window; systemic rejection causes are raised to M23 | **C** | Quality Manager |
| BRU-WTY-21 | A protection claim scored above the fraud threshold is investigated before settlement, never auto-rejected | **A** | Finance Director |
| BRU-WTY-22 | Warranty cost, recovery, reserve movement and write-off post to their designated accounts; no manual journal substitutes for the module's instruction | **H** | CFO |

*Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.warranty.register` | `fix_warranty_register` | Every warranty instance | asset_id, source (manufacturer/extended/protection/repair/contract/seller), brand_id, start_date, end_date, terms_ref, evidence_document_id, confidence, state |
| `fix.warranty.void` | `fix_warranty_void` | Void records | register_id, condition, evidence_ids, declared_by, declared_at, approved_by |
| `fix.warranty.transfer` | `fix_warranty_transfer` | Ownership transfers | register_id, from_party, to_party, permitted, at |
| `fix.repair.warranty` *(shared with M01)* | `fix_repair_warranty` | Warranty on our own work | order_id, asset_id, scope, start_date, end_date, claimed |
| `fix.protection.policy` | `fix_protection_policy` | Sold protection instance | number, product_id, family, party_id, asset_id, sale_doc_ref, term_start, term_end, waiting_until, excess, limits_json, remaining_limits_json, state |
| `fix.protection.inspection` | `fix_protection_inspection` | Pre-sale inspection | policy_id, inspected_at, inspector_id, condition_grade, evidence_ids, outcome |
| `fix.protection.claim` | `fix_protection_claim` | Inbound claim | number, policy_id, incident_date, cause, description, assessed_value, excess_collected, state, fraud_score, decision, reason_code, fulfilment_type, fulfilment_ref |
| `fix.protection.reserve` | `fix_protection_reserve` | Append-only reserve ledger | policy_id, movement_type (establish/adjust/release), amount, reason, at |
| `fix.brand.claim` | `fix_brand_claim` | Outbound recovery claim | number, brand_id, service_order_id, asset_id, fault_code, brand_code, labour_value, parts_value, claimed_value, approved_value, paid_value, rate_version, state, submitted_at, deadline_at, submission_ref |
| `fix.brand.claim.line` | `fix_brand_claim_line` | Claim detail | claim_id, line_type (labour/part/other), item_id, serial, qty, rate, value, brand_part_code |
| `fix.claim.evidence.pack` | `fix_claim_evidence_pack` | Sealed evidence projection | claim_id, artefact_refs_json, content_hash, sealed_at |
| `fix.brand.claim.rule` | `fix_brand_claim_rule` | Per-brand rule set | brand_id, rule_type, definition_json, mandatory, submission_window_days, channel, version, valid_from |
| `fix.brand.claim.decision` | `fix_brand_claim_decision` | Brand decisions | claim_id, decision, amount, reason_code, reason_text, decided_at, decided_by_ref |
| `fix.brand.claim.appeal` | `fix_brand_claim_appeal` | Appeals | claim_id, submitted_at, additional_evidence_ids, outcome, decided_at |
| `fix.brand.remittance` | `fix_brand_remittance` | Remittance advice | brand_id, reference, period, total_amount, received_at, document_id, state |
| `fix.brand.remittance.line` | `fix_brand_remittance_line` | Matched lines | remittance_id, claim_id, amount, matched, variance, variance_reason |
| `fix.brand.reconciliation` | `fix_brand_reconciliation` | Period reconciliation | brand_id, period, claimed, approved, rejected, paid, outstanding, written_off, state, signed_by |
| `fix.claim.writeoff` | `fix_claim_writeoff` | Write-off record | claim_id, amount, reason, requested_by, approved_by, at |
| `fix.consignment.part.record` | `fix_consignment_part_record` | Brand consignment governance | brand_id, part_item_id, received_qty, consumed_qty, claim_refs, reported_at, liability_state |
| `fix.defective.return` | `fix_defective_return` | Defective part returns | claim_id, part_item_id, serial, returned_at, consignment_ref, proof_document_id, state |
| `fix.warranty.campaign` | `fix_warranty_campaign` | Recall / service campaign | brand_id, code, description, serial_ranges_json, start_date, end_date, claim_rules_ref, state |
| `fix.brand.performance` | `fix_brand_performance` | Partner scorecard | brand_id, period, decision_days_avg, approval_rate, rejection_reasons_json, payment_days_avg, short_pay_rate |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.protection.product` (definitions) | M37 | Master data projection |
| `fix.fault.taxonomy`, `fix.fault.brand.map` | M37 | Projection for code translation |
| `fix.brand.reimbursement.rate` | M11 | REST; version pinned onto the claim |
| `fix.asset`, ownership history | M17 / M49 | Live read |
| `fix.service.order`, diagnostics, photographs, QC, handover signature | M01 | Live read; evidence by reference |
| `fix.competency` (technician) | M22 | Live read for claim eligibility |
| `fix.part.item`, serials, stock issue records | M37 | Live read; consignment governance |
| `fix.ar.invoice`, `fix.ar.credit.note`, receivable | M20 | Command; live read for settlement |
| `fix.contract` (overlapping coverage) | M08 | Live read |
| `fix.document`, retention | M24 | Service call |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-WTY-01 | Warranty-type service order delivered (M01 `service_order.delivered`) | Create the brand claim, assemble the evidence pack, value it at the pinned rate version | Create the claim in Blocked with the missing artefacts listed; alert the branch |
| AUT-WTY-02 | Evidence pack assembled | Run the brand rule set; move to Validated or Blocked with a full failure list | Retry once; escalate to the Warranty Officer |
| AUT-WTY-03 | Claim validated | Submit on the brand's channel; record the submission reference | Retry with backoff; after exhaustion, dead-letter and alert |
| AUT-WTY-04 | Claim blocked | Assign remediation to the originating branch with a deadline derived from the submission window | Escalate to the branch manager, then Operations Director |
| AUT-WTY-05 | Submission window at 50% / 75% / 90% elapsed | Escalate progressively to Warranty Officer, Finance Manager and Finance Director | Repeat; log |
| AUT-WTY-06 | Submission window elapsed | Mark Lapsed, raise a mandatory incident record with the value lost and the cause | — |
| AUT-WTY-07 | Brand decision received | Record it, raise the receivable in M20 on approval, or route rejection for classification | Queue; alert if unprocessed after 4 hours |
| AUT-WTY-08 | Rejection classified as correctable | Create a remediation task with the remaining window shown, and resubmit on completion | Escalate to the Warranty Officer |
| AUT-WTY-09 | Rejection reason recurs beyond threshold | Raise a quality signal to M23 with the affected branches, technicians and models | Log |
| AUT-WTY-10 | Claim ageing beyond the brand's expected decision time | Chase the brand automatically; escalate to the account owner and CCO on repetition | Repeat on schedule |
| AUT-WTY-11 | Remittance advice received | Match to claims, settle matched, flag short payments and unmatched items | Route the whole remittance to manual matching |
| AUT-WTY-12 | Period end per brand | Produce the reconciliation statement — claimed, approved, rejected, paid, outstanding — for sign-off | Alert Finance Manager |
| AUT-WTY-13 | Protection product sold | Issue the policy, establish the reserve, start the waiting period, and deliver the policy document in the customer's language | Create a manual policy issue task |
| AUT-WTY-14 | Protection claim raised | Assess coverage, waiting period and limits; compute the excess; score for fraud; route for approval | Route to manual assessment |
| AUT-WTY-15 | Protection claim settled | Decrement limits, release or adjust the reserve, and instruct M20 for any cash element | Flag for manual reserve adjustment |
| AUT-WTY-16 | Warranty approaching expiry | Notify the customer and present an extension offer through M36/M38 | Log; retry |
| AUT-WTY-17 | Recall campaign published by a brand | Identify affected serials in M17, generate the service-order batch in M01, and open the campaign claim set | Alert the Warranty Officer with the affected list |
| AUT-WTY-18 | Loss ratio for a protection family breaches threshold | Alert the CFO and CCO with cohort and channel analysis | Log; repeat weekly |
| AUT-WTY-19 | Consignment part consumed on a claim | Record consumption against the brand's consignment and include it in the cycle report | Flag for manual reporting |
| AUT-WTY-20 | Defective return required and not evidenced by deadline | Mark the claim non-recoverable pending return and alert the branch | Escalate to Inventory Manager |

---

## 12. Interfaces

### 12.1 Upstream — M09 Consumes

| Source | What | Mechanism |
|---|---|---|
| M01 SRM | Warranty order delivery, diagnostics, fault codes, photographs, QC result, handover signature, labour time | Event `service_order.delivered` + REST |
| M31 Workshop | Component-level repair detail and bench evidence | Event + REST |
| M17 Asset Registry | Device identity, serial, purchase date, ownership history | Live read |
| M37 Catalogue | Protection product definitions, fault taxonomy, brand claim-code mapping, part definitions | Master data projection |
| M11 Pricing | Brand reimbursement rate cards (versioned), protection product pricing | REST |
| M15 Inventory | Parts issued with serials; consignment stock position | Live read + events |
| M22 Competency | Technician certification validity for claim eligibility | Live read |
| M36 Quotation · M38 E-Commerce | Accepted protection product sales | Event `quotation.accepted`, `order.completed` |
| M08 Contract | Overlapping contract coverage for precedence resolution | REST |
| M20 Receivable | Settlement, receipt and ageing of claim receivables | Events |
| M24 Document | Policy documents, evidence storage, retention | Service call |
| Brand partners | Warranty status feeds, rate cards, claim decisions, remittance advice, recall notices | INT-WTY-01…05 |

### 12.2 Downstream — M09 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 SRM | Warranty entitlement verdict at intake; evidence requirements for warranty jobs; repair-warranty rework recognition | REST `POST /api/v1/warranty/check` |
| M20 Receivable | Claim receivables, protection settlements, refunds, write-off instructions | Command |
| M19 Financial Accounting | Warranty cost, recovery, reserve movement and write-off postings | Command |
| M53 Revenue | Protection product revenue-recognition basis (over-time obligation) | Projection |
| M15 Inventory | Consignment consumption reporting and defective-return instructions | Command |
| M23 Quality | Rejection-cause patterns, failure patterns, recall execution quality | Events |
| M14 Refurbishment | Warranty status of devices entering the refurbishment stream | REST |
| M36 / M38 | Warranty expiry and extension offers; eligibility for protection products | Events + REST |
| M40 Partner | Brand partner claim performance for relationship management | Projection |
| M25 BID · M26 AIM | Claim, leakage, failure-pattern and attach-rate fact streams | Warehouse extract |
| P01 Customer Portal | Warranty status, protection policies, claim submission and status | REST |
| P04 Corporate Portal | Estate warranty position and claim status | REST |
| **P08 Brand Partner Portal** | Claim queue, evidence, decisions, bulk actions, remittance upload, reconciliation, performance | REST — the module's principal external surface |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `warranty.registered` | asset, source, brand, start, end | M17, M01, M25 |
| `warranty.verdict_issued` | asset, order, verdict, payer, exclusions, customer liability | M01, M27 |
| `warranty.voided` | register id, condition, evidence | M17, M01, M23 |
| `warranty.expiring` | asset, register id, days remaining | M36, M38, M27 |
| `protection.policy_issued` | policy id, product, party, asset, term, limits | M20, M39, M53, M27 |
| `protection.claim_decided` | claim id, decision, amount, reason | M20, M01, M27 |
| `protection.loss_ratio_alert` | family, cohort, ratio, threshold | CFO alerting, M25 |
| `claim.created` | claim id, brand, order, value, deadline | M25, P08 |
| `claim.blocked` | claim id, failures, remediation owner | M01, M23 |
| `claim.submitted` | claim id, brand, submission ref, value | M20, M25, P08 |
| `claim.decided` | claim id, decision, approved value, reason | M20, M23, M25 |
| `claim.lapsed` | claim id, value lost, cause | M23, CFO alerting |
| `claim.paid` / `claim.short_paid` | claim id, amount, variance | M20, M19 |
| `claim.written_off` | claim id, amount, reason, approver | M19, M25 |
| `brand.reconciliation_signed` | brand, period, totals | M19, M40 |
| `warranty.failure_pattern_detected` | model, part, failure rate, sample | M23, M43, M40 |
| `recall.campaign_opened` | brand, campaign, affected serial count | M01, M17, M27 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-WTY-01 | Brand partner claim APIs (where available) | Outbound / bidirectional | Claim submission and decision retrieval |
| INT-WTY-02 | Brand partner claim portals (17+) | Assisted / file | Submission where no API exists; structured file exchange |
| INT-WTY-03 | Brand warranty status lookup services | Inbound | Serial/IMEI warranty verification |
| INT-WTY-04 | Brand remittance advice | Inbound (file / document) | Payment reconciliation |
| INT-WTY-05 | Brand recall and technical bulletins | Inbound | Campaign execution and technical notices |
| INT-WTY-06 | External underwriter *(if protection products are underwritten)* | Bidirectional | Cession, bordereau reporting and claim recovery |
| INT-WTY-07 | Payment gateways (bKash / Nagad / card) *(via M20)* | Outbound | Excess collection at claim |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/warranty/check` | POST | Authoritative entitlement verdict for an asset, date and work type | M01, P01, P04, P10 |
| `/api/v1/warranty/register` | GET/POST | Warranty register query and registration | P03, bulk loader |
| `/api/v1/warranty/public-check` | GET | Anonymous serial-based warranty status | P01, website |
| `/api/v1/protection/products/eligible` | POST | Eligible protection products for a device and customer | M36, M38, P01, P03 |
| `/api/v1/protection/policies` | GET/POST | Policy issue and query | M36, M38, P01 |
| `/api/v1/protection/claims` | GET/POST | Protection claim intake and status | P01, P03, P10 |
| `/api/v1/claims` | GET | Brand claim queue with filters | P03, P08 |
| `/api/v1/claims/{id}` | GET | Full claim with evidence pack references | P03, P08 |
| `/api/v1/claims/{id}/validate` | POST | Run the brand rule set and return failures | P03 |
| `/api/v1/claims/{id}/submit` | POST | Submit on the brand's channel | P03 |
| `/api/v1/claims/{id}/decision` | POST | Record a brand decision | P08, brand API |
| `/api/v1/claims/{id}/appeal` | POST | Raise an appeal with additional evidence | P03, P08 |
| `/api/v1/claims/bulk-decision` | POST | Bulk brand decisions | P08 |
| `/api/v1/remittances` | POST | Upload remittance advice for matching | P08, P03 |
| `/api/v1/reconciliation/{brand}/{period}` | GET | Period reconciliation statement | P03, P08 |
| `/api/v1/campaigns` | GET/POST | Recall and service campaigns | P03, P08 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R28 Warranty Claims Officer | C R U D A | All claims — the primary operator |
| R03 Chief Financial Officer | R A | All — write-off, reserve, loss ratio |
| R26 Finance Manager | R U A | All — reconciliation, write-off approval, excess waiver |
| R27 Finance Officer | R U | Assigned scope — remittance matching |
| R04 Chief Commercial Officer | R A | Protection products, attach rate, brand escalation |
| R05 Operations Director | R | All — evidence and remediation performance |
| R06 Branch Manager | R U | Own branch — claim remediation |
| R08 Service Centre Agent | C R | Own branch — warranty check, protection sale, claim intake |
| R09 Workshop Supervisor | R U | Own workshop — evidence completion |
| R10/R11/R12 Technician | R | Own jobs — warranty context and evidence requirements |
| R32 Quality Manager / ISO Coordinator | R | All — rejection causes, failure patterns, void evidence |
| R17 Inventory Manager | R U | Consignment parts and defective returns |
| R34 Contact Centre Agent | C R | Customer-facing warranty and protection claim intake |
| R36 Customer | C R | Own warranties, policies and claims |
| R37 Corporate Portal User | R | Own company's estate warranty position |
| **R38 Brand Partner** | R U A | **Own brand only** — claim queue, evidence, decisions, remittance, reconciliation *(EA-05)* |

**Field-level restrictions.** Internal cost, margin, technician identity where the brand does not
require it, and other brands' data are never visible to a brand partner. `internal_note` is never
exposed externally. Customer personal data exposed to a brand is limited to what the claim
requires.

**Segregation of duties.** **SOD-11** — raising a claim and approving its write-off are a hard
block *(`05-04` §6)*. Additionally, the technician whose work is claimed cannot approve the
claim's evidence completeness, which interacts with **SOD-07**.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Claim pipeline dashboard | Warranty Officer, Finance Manager | Real time | Claims by state and brand; blocked claims with causes; claims at submission-window risk |
| Submission timeliness | Finance Director, Ops Director | Daily | Service-to-submission elapsed time distribution; claims outside 72 hours with cause |
| Warranty leakage report | Finance Director, CFO | Monthly | Claimable value vs claimed vs approved vs paid; leakage decomposed by cause (not created, blocked, lapsed, rejected, short-paid, written off) |
| Rejection analysis | Warranty Officer, Quality Manager | Weekly | Rejection reasons ranked by count and value; by branch, technician, model and brand |
| Claim ageing and recovery | Finance Manager, CFO | Weekly | Outstanding claims by age band and brand; days-to-cash trend |
| Brand reconciliation statement | Finance Manager, brand partner | Per period per brand | Claimed, approved, rejected, paid, outstanding, written off — signed by both sides |
| Brand partner scorecard | CCO, Finance Director, M40 | Quarterly | Decision time, approval rate, payment time, short-pay rate by brand |
| Protection attach rate | CCO, Branch Managers | Weekly | Attach rate by branch, channel, agent and device category |
| Protection loss ratio | CFO, CCO | Monthly | Loss ratio by family, cohort, channel and device category, against the 30–50% band |
| Reserve position | CFO | Monthly | Reserve established, adjusted, released, outstanding; adequacy assessment |
| Fraud and anomaly report | Finance Director, Quality Manager | Monthly | High-scoring inbound and outbound claims, investigation outcomes |
| Failure-pattern report | Quality Manager, brand partners, M43 | Monthly | Failure rates by model, part and component with statistical significance |
| Campaign progress | Warranty Officer, brand partner | Per campaign | Affected units, contacted, completed, claimed, outstanding |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-C09-01 | Eligible claims submitted within 72 hours | ~50% at 30–90 days | 85% | **> 95%** |
| KPI-C09-02 | Warranty revenue leakage | 15–20% | < 6% | **< 2%** |
| KPI-C09-03 | Claim approval rate | unmeasured | 88% | **> 92%** |
| KPI-C09-04 | Days from service to reimbursement | unmeasured | < 60 | **< 45** |
| KPI-C09-05 | Claims lapsed on the submission window | unknown | < 1% | **0%** |
| KPI-C09-06 | Claims blocked at validation on first attempt | n/a | < 20% | **< 8%** |
| KPI-C09-07 | Claims submitted through P08 rather than email | 0% | 70% | **> 80%** |
| KPI-C09-08 | Warranty entitlement verdict latency p95 | n/a | ≤ 400 ms | **≤ 300 ms** |
| KPI-C09-09 | Protection product attach rate | unmeasured | 12% | **> 18%** |
| KPI-C09-10 | Protection loss ratio | unmeasured | within 30–55% | **within 30–50%** |
| KPI-C09-11 | Short payments unresolved beyond 60 days | unknown | < 5% | **< 1%** |
| KPI-C09-12 | Warranty orders closed without a complete evidence pack | unknown | 0 | **0** |
| KPI-C09-13 | Protection claims settled within 5 working days | n/a | 80% | **> 92%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `product`, `account`, `mail`, `portal` | 8% |
| L2 | OCA `document_page`, `partner_*`, `base_import_*`, `queue_job` | 14% |
| L5 | `cd_warranty_register`, `cd_protection_plan`, `cd_claim_engine`, `cd_brand_recovery`, `cd_claim_reconciliation` | 78% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C09-01 | `cd_warranty_register` — unified register, entitlement verdict engine, precedence, void, transfer | Odoo module + service | 7 PW |
| CD-C09-02 | `cd_protection_plan` — seven families, eligibility, inspection, policy issue, limits, reserve, loss ratio | Odoo module | 8 PW |
| CD-C09-03 | `cd_claim_engine` — claim creation, evidence pack assembly, brand rule engine, validation, valuation | Odoo module + service | 9 PW |
| CD-C09-04 | `cd_brand_recovery` — submission adapters, deadline scheduler, decisions, appeals, ageing and chasing | Odoo module + service | 6 PW |
| CD-C09-05 | `cd_claim_reconciliation` — remittance matching, period reconciliation, write-off governance, brand scorecard | Odoo module | 4 PW |
| CD-C09-06 | P08 Brand Partner Portal domain services and brand-scoped API | Service | 2 PW |
| | | **Total** | **36 PW** |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M01 SRM (complete) | The evidence and the claim-eligible event originate there; without M01's evidence gates M09 cannot function |
| M31 Workshop | Component-level evidence for L2/L3 repairs |
| M17 Asset Registry | Warranty attaches to a device with a serial and a purchase date |
| M37 Catalogue | Protection product definitions, fault taxonomy and brand code mapping |
| M11 Pricing | Brand reimbursement rate cards |
| M15 Inventory | Parts issue evidence and consignment governance |
| M22 Competency | Certification validity for claim eligibility |
| M20 Receivable | Claim receivables and settlement |
| M24 Document | Evidence storage and retention |
| **P08 delivered with M09** | The brand portal is M09's primary external surface and is gated with it in W4 |

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Email-based claim records | 12–24 months, volume to be profiled | `fix.brand.claim` (archive state) | W4 |
| Outstanding unpaid claims | Unknown — **profiling is a Wave 3 prerequisite** | `fix.brand.claim` (live, Receivable state) | W4 |
| Sold extended-warranty records | Unknown | `fix.protection.policy` | W4 |
| Brand rate cards and claim rules (17+) | ~400 rate lines + rule sets | `fix.brand.claim.rule` (M09), rates in M11 | W4 |
| Device warranty data from service history | 500,000+ historical records, sampled | `fix.warranty.register` (confidence = derived) | W4 |
| Consignment part balances | Per brand | `fix.consignment.part.record` | W4 |

**Migration rule.** Outstanding claims are migrated live only where the submission and approval
evidence exists; anything else migrates as archive and is written off through the governed
process, not silently absorbed. **Profiling the current outstanding claim book is a Wave 3
prerequisite** — the recoverable balance is a real asset whose size is currently unknown, and
the Wave 4 business case depends on it.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A brand claim exists, with a complete evidence pack, within 5 minutes of a warranty order being delivered | Timed end-to-end test across five brands |
| AC-02 | A claim failing any brand rule cannot be submitted, and every failure is listed in one view with a remediation action | Negative test per brand rule set |
| AC-03 | A claim is valued at the rate-card version in force on the service date, across a version boundary | Scripted scenario |
| AC-04 | A warranty order cannot close without before and after photographs, through any channel | Negative test via UI, API and technician app |
| AC-05 | The entitlement verdict returns in ≤ 300 ms p95 and correctly resolves overlapping coverage | Load test + precedence test matrix |
| AC-06 | Submission-window escalation fires at 50/75/90% and a lapsed claim raises a mandatory incident | Compressed-timeline test |
| AC-07 | All seven protection families are sold, activated, claimed and settled from configuration alone | Seven scripted end-to-end scenarios |
| AC-08 | A protection claim within the waiting period, beyond limits, or on an ineligible device is refused with a clear reason | Negative test matrix |
| AC-09 | The reserve ledger reconciles to the sum of its movements and cannot be edited directly | Reconciliation + negative test |
| AC-10 | Remittance advice matches automatically; short payments and unmatched items are surfaced, never absorbed | Reconciliation test with induced variances |
| AC-11 | A brand partner in P08 can see only their own brand's claims and data, verified by negative test | Security test per brand |
| AC-12 | Raising a claim and approving its write-off cannot be done by the same user | SOD negative test |
| AC-13 | A recall campaign generates the correct service-order batch from serial ranges and claims as a campaign | Scripted campaign |
| AC-14 | Named business super-users — including at least two brand partners — sign off UAT for all P0 and P1 requirements | Signed UAT record |
| AC-15 | Zero critical or high security findings, including on the P08 external surface | Security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What is the current outstanding, unreconciled brand claim balance? The Wave 4 benefit case depends on it and it is unknown | Finance Director | **W3 — blocking** |
| Q-02 | Which of the 17+ brand partners offer a claim API, which require portal submission, and which accept only email or file? | Finance Director / CTO | W4 build |
| Q-03 | What is each brand's submission window, and are any shorter than 72 hours? | Warranty Officer | W4 build |
| Q-04 | Are 1000FiX protection products underwritten externally, self-funded, or a mix? The reserve and regulatory treatment differ materially | CFO / CEO | **W4 — blocking for §5.2** |
| Q-05 | Do protection products constitute regulated insurance business in Bangladesh, and is an IDRA licence or an underwriting partner required? | Legal / CFO | **W4 — blocking** |
| Q-06 | What is the repair warranty period by device category and repair level? *(carried from M01 Q-03)* | Ops Director / Quality | W4 build |
| Q-07 | For marketplace-fulfilled orders, does 1000FiX's repair warranty apply or the seller's? *(carried from M01 Q-05)* | CEO / Legal | W7 (M12) |
| Q-08 | Where a device is covered by both a 1000FiX protection plan and manufacturer warranty, which pays first, and is that stated in the product terms? | CCO / Legal | W4 build |
| Q-09 | What is the company's policy on writing off small-value unrecoverable claims — a de minimis threshold, or case-by-case approval? | CFO | W4 build |

---

## 19. References

**Internal**
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §7, §8 ·
`M37_Product_and_Service_Catalogue_Management.md` §5.5, §5.6 ·
`M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md` §5.2 (brand reimbursement rate cards) ·
`M08_Contract_Lifecycle_Management.md` §3 ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` §5.5, §11 AUT-SRM-07, §12 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §6 SOD-11, §8 EA-05 ·
`05-05_Business_Rules_and_Automation_Catalogue.md` ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P08 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §6, §8.9, §10.1 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §9 ·
`1000FiX Business Plan` §Warranty Products ·
`1000FiX_Services_Company_Profile.md` §Brand Partnerships

**External benchmark**
SAP S/4HANA warranty claim processing and supplier recovery ·
IFS Cloud warranty verification at intake ·
Dedicated warranty platforms (Tavant, PCMI, OnPoint, Intellinet) — claim validation, fraud detection, supplier recovery, servicer portals ·
Extended-warranty administration practice — reserve accounting and the 30–50% loss-ratio benchmark ·
OEM claim-approval and retail-rate reimbursement benchmarks (24-hour decision targets) ·
Industry evidence that automated recovery raises recovery rates from under 60% to above 90% ·
Odoo 19 / OCA `queue_job` and document module families

---

*Module M09 · Category C · 1000FiX ERP System v2.0 · CONFIDENTIAL*
