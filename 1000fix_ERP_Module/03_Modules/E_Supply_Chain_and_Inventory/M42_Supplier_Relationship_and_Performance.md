---
id: FIX-ERP2-M42
module_id: M42
module_code: SRM2
module_name: Supplier Relationship & Performance
category: E — Supply Chain & Inventory
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Procurement Manager
system_owner: Supply Chain Squad
priority: P1
wave: W4
---

# M42 — Supplier Relationship & Performance
### Category E · Code `SRM2` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M42 |
| **Module code** | `SRM2` *(`SRM` is permanently allocated to M01 under rule RG-02 — see `02-02` §2)* |
| **Category** | E — Supply Chain & Inventory |
| **Status** | ★ **New** — split out of M16 after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | **W4** (Months 14–18), with a **mandatory qualification slice in W3** |
| **Business owner** | Procurement Manager |
| **System owner** | Supply Chain Squad |
| **Delivery layers** | L1 Odoo `contacts` / `purchase` vendor foundation · L2 OCA `partner-contact`, `contract` · L5 custom qualification, scorecard and risk engines |
| **Custom modules** | `cd_vendor_ext`, `cd_supplier_qualification`, `cd_supplier_scorecard`, `cd_supplier_risk` |
| **Requirement range** | FR-SRM2-001 … FR-SRM2-034 |
| **Requirement count** | **34** *(measured — supersedes the 26 estimate in `02-02`)* |
| **Effort estimate** | **16 person-weeks** *(measured — supersedes the 13 PW estimate)* |
| **Depends on** | M33 Party Master · M16 Procurement · M15 Inventory · M23 Quality · M24 Documents · M29 Identity · M28 Integration · M52 Accounts Payable |
| **Depended on by** | **M16 (hard gate)**, M15, M41, M43, M44, M03, M18, M23, M52, M25, M60 |

---

## 2. Purpose

M42 owns **the supplier as a relationship**, not as a row on a purchase order.

M16 answers "what did we buy from them last Tuesday". M42 answers the questions that decide
whether there should be a next Tuesday: *are they qualified to supply this category at all? what
did we agree, and does the price on the order match it? how have they actually performed over
the last two quarters? what would happen to us if they failed? and what are we doing about the
ones who are underperforming?*

1000FiX buys from a fragmented market. Genuine OEM parts arrive through authorised distribution
channels with long lead times and letters of credit. Compatible and aftermarket parts arrive
through local traders on informal terms. Both are necessary. Only one of them carries a
meaningful risk of counterfeit product entering the estate and destroying a brand
authorisation. Distinguishing between them — deliberately, with evidence, and before the first
order rather than after the first incident — is what this module is for.

### Why It Exists

The category overview states the rule that makes M42 structural rather than administrative:
**M16 cannot raise a purchase order to a supplier that M42 has not qualified and activated.**
That single dependency converts supplier management from a filing exercise into a control.

Three further arguments.

**Performance is currently anecdotal.** Everyone in procurement knows which supplier is
unreliable. Nobody can prove it, quantify it, or put it in front of the supplier. A scorecard
built from M16's own receipt data — promised versus actual date, quantity delivered, inspection
rejection rate, invoice accuracy — changes a negotiation from opinion to evidence.

**Concentration risk is invisible.** If 60% of a critical part category comes from one importer
with no qualified alternate, the Company has a single point of failure it has never named.

**The brand partnerships are supplier relationships too.** 1000FiX is the authorised service
partner for 17+ brands. Those brands supply consignment parts, set warranty terms and audit
their partners. They are the most commercially important supplier relationships the Company
has, and they are currently managed entirely outside any system.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-SCM-001 | "Maintain a vendor master with classification: OEM, authorized distributor, local supplier" — the segmentation model |
| ERP BRD BR-SCM-007 | "Track vendor performance: on-time delivery rate, quality rejection rate, lead time" — the scorecard core |
| ERP BRD BR-INV-010 | "Classify parts as: Genuine (OEM), Compatible, Refurbished" — part class implies supplier class |
| `_CATEGORY_OVERVIEW.md` §4 | "M16 cannot raise a purchase order to a supplier that M42 has not qualified and activated" — the defining rule of this module |
| `_CATEGORY_OVERVIEW.md` §7 | Vendor on-time delivery target > 92%, owned by M42 |
| `05-04` §6 SOD-01 | "Create vendor + approve vendor invoice" is a hard block — supplier creation is a controlled act |
| `05-04` §8 EA-06 | "A vendor sees only their own purchase orders, receipts and invoices" |
| Company Profile §Authorized Service Partnerships | 17+ brand partners — the most significant supplier class |
| Company Profile §Quality & Certification | ISO certification; ISO 9001 clause 8.4 requires control of externally provided processes, products and services, including supplier evaluation and re-evaluation |
| `M03` §3.3 | Courier partners: M03 owns the operational relationship, **M42 owns the commercial one** |

---

## 3. Scope Boundary

> **The rule:** if the artefact governs *whether and on what terms* we may trade with a party,
> it is M42. If it is *a specific trade*, it is M16.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The supplier profile as an extension of the M33 party: classification, categories, capabilities, capacity |
| 2 | Supplier segmentation — strategic, preferred, approved, transactional, restricted — and the treatment each attracts |
| 3 | Supplier registration and self-service onboarding through P05 |
| 4 | **Qualification**: category-specific questionnaires, evidence collection, scoring, approval workflow |
| 5 | Qualification validity, expiry, re-qualification and lapse handling |
| 6 | **Activation and de-activation** — the authoritative gate M16 checks before any purchase order |
| 7 | Supplier document register: trade licence, VAT/BIN registration, TIN, bank details, authorisations, certifications, insurance |
| 8 | Document expiry monitoring and automatic status consequence |
| 9 | Contracts and framework agreements: term, scope, pricing, service levels, rebates, penalties, renewal |
| 10 | Agreed price lists and commercial terms that M16 calls off against |
| 11 | Consignment agreements with brand partners, including the terms M15 enforces |
| 12 | **Performance scorecards**: on-time delivery, quality, price behaviour, responsiveness, invoice accuracy, documentation |
| 13 | Weighted scoring models configurable per category, with banding and trend |
| 14 | Performance review cycles, agendas and minuted outcomes |
| 15 | **Corrective action requests** and supplier development plans with tracked milestones |
| 16 | **Risk assessment**: financial, operational, concentration, geographic, compliance, counterfeit and continuity risk |
| 17 | Concentration and single-source dependency analysis, with alternate-source obligations |
| 18 | Business-continuity requirements per critical supplier, and their verification |
| 19 | Compliance and integrity screening: sanctions, conflict of interest, related-party detection, anti-bribery declaration |
| 20 | Brand partner relationship management as a distinct supplier class |
| 21 | **Logistics-service supplier qualification** — freight forwarders, C&F agents, cargo insurers and courier partners — on the same framework, with category-specific scorecard metrics: clearance cycle time and cost accuracy (from M44), delivery performance (from M03), and document quality |
| 22 | Category strategy: spend, market structure, sourcing approach and supplier landscape per category |
| 23 | Supplier communication, announcements and the P05 supplier experience |
| 24 | Supplier lifecycle analytics and the supplier base health view |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Requisition, RFQ, purchase order, receipt, three-way match | **M16** | The transaction; M42 sets the conditions under which it may occur |
| Sourcing event execution and award decision | **M16** | An award is a transaction outcome; M42 supplies who may be invited |
| Purchase price paid on a specific order | **M16** | M42 owns the *agreed* price; M16 owns the *paid* price and the variance between them |
| Delivery and quality **measurement** | **M16** (produces the facts) | M42 interprets, scores and acts. Procurement must not grade its own suppliers |
| The party record itself — name, address, contacts, tax identifiers | **M33** Party Master | One party, one record. M42 adds the supplier role and its attributes |
| Vendor invoice posting, payment, ageing, remittance | **M52** Accounts Payable | — |
| Withholding tax and VAT treatment of supplier payments | **M51** Tax & Regulatory Compliance | — |
| Inspection standard, sampling plan, non-conformance record | **M23** Quality | M42 consumes quality outcomes; M23 owns the quality system |
| Stock, ownership class and consignment balances | **M15** | M42 owns the consignment *agreement*; M15 owns the consignment *stock* |
| Import documentation, LC, customs, freight forwarder execution | **M44** | M42 qualifies the forwarder and the C&F agent; M44 uses them |
| Courier operational assignment, booking and tracking | **M03** Logistics | M42 owns the courier contract and scorecard; M03 runs the daily work |
| Recycling partner certification and disposal compliance | **M18** E-Waste | M42 qualifies them commercially; M18 owns environmental compliance |
| Marketplace sellers | **M12** Marketplace | A seller supplies labour to customers, not goods to 1000FiX. Different lifecycle, different economics |
| Employment agencies and staffing suppliers | **M58** Talent Acquisition (with M42 for the commercial contract) | Split by subject matter |
| Enterprise risk register and GRC framework | **M60** Governance, Risk & Compliance | M42 owns supply-side risk; M60 aggregates enterprise risk |
| Contract templates, e-signature and clause library | **M08** Contract Lifecycle Management / **M24** Documents | M42 holds supplier agreements; the CLM engine is shared |

### 3.3 Shared Concepts

| Concept | M42's Role | Owning Module |
|---|---|---|
| Party | Extends with the supplier role and its attributes | M33 |
| Supplier profile, qualification, activation | **Owns** | M42 |
| Supplier agreement / framework contract | **Owns** the supplier instance; M08 owns the contract engine | M42 / M08 |
| Agreed price list | **Owns**; M16 calls off against it | M42 |
| Consignment agreement | **Owns** the agreement; M15 owns the stock and the balance | M42 / M15 |
| Delivery and quality performance | Interprets and scores; M16 measures | M16 / M42 |
| Supplier risk | **Owns** supply-side risk; M60 aggregates | M42 / M60 |
| Courier partner | Owns the commercial relationship and scorecard; M03 owns operations | M42 / M03 |
| Brand partner | Owns the supplier-side relationship; M09 owns warranty claims, P08 the portal | M42 / M09 |
| Supplier documents | Owns the register and expiry; M24 owns storage and retention | M42 / M24 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Ariba Supplier Lifecycle and Performance (SLP)** | Registration → qualification → segmentation → performance → development, with category- and region-specific qualification questionnaires, scoring models, approval flows, and segmentation by risk and business relevance | **SLP is the primary reference for M42.** Adopted whole: the lifecycle stages; **category-scoped qualification** (a supplier may be qualified for cables and not for motherboards); questionnaire-plus-scoring-plus-approval as the qualification mechanism; and segmentation driven by *risk and business relevance* rather than by spend alone | The full modular Ariba stack (SLP + Supplier Risk + Sourcing + Contracts as separate products) and its integration cost. We implement one coherent module |
| **SAP Supplier Performance Management scorecards** | KPI-based scorecards, performance reviews, audits, corrective action plans | **Scorecard + review + corrective action as one connected loop.** A score with no review and no corrective action changes nothing; the loop is the product | The survey-based stakeholder-feedback machinery at our scale — we use it only for strategic suppliers |
| **Oracle Fusion Cloud — Supplier Management** | Supplier registration, qualification areas and questions, qualification expiry and reassessment, supplier profile change approval | **Qualification expiry with automatic status consequence** — a lapsed qualification de-activates the supplier rather than merely warning. Also adopted: **profile change approval**, so bank-detail changes cannot be made silently (a well-known fraud vector) | Oracle's supplier hierarchy depth |
| **Microsoft Dynamics 365 — Vendor collaboration** | Vendor self-service portal for onboarding, profile maintenance, order confirmation and invoicing | The **supplier does its own data entry**. A supplier maintaining its own trade licence expiry is both cheaper and more accurate than procurement chasing it. Delivered through P05 | — |
| **Coupa / Ivalua supplier risk practice** | Continuous risk monitoring across financial, operational, compliance and ESG dimensions with risk-tiered treatment | **Risk-tiered treatment**: the depth of qualification and the frequency of review are set by the supplier's risk tier, not applied uniformly. This is what makes the model affordable | Third-party risk-data subscriptions; not available or economic for the Bangladesh supplier base |
| **ISO 9001:2015 clause 8.4** | Control of externally provided processes, products and services; criteria for evaluation, selection, monitoring and re-evaluation of external providers | **The clause is implemented literally.** Qualification is *selection criteria*; the scorecard is *monitoring*; re-qualification is *re-evaluation*. 1000FiX's ISO certification is a stated competitive advantage; M42 is where that clause becomes auditable evidence | — |
| **Anti-counterfeit supply-chain practice (electronics)** | Authorised-distribution verification, source traceability, grey-market controls | **Authorisation evidence is a qualification requirement for genuine-OEM categories.** A supplier claiming to supply genuine parts must evidence its authorisation, and that evidence expires | Full component-authentication testing; disproportionate, and partly covered by M15 serial provenance |

**Design position.** Four deliberate differences.

First, **qualification is scoped to categories, and activation is binary and enforced
elsewhere**. A supplier is not "approved"; a supplier is approved *for a category*, for a
period, on evidence. M16 checks that specific fact on every purchase order. This is the
structural control, and it is the reason M42 exists as a separate module rather than as a tab
on the vendor form.

Second, **procurement does not score its own suppliers**. The facts — promised versus actual
date, rejected quantity, invoice variance — are produced by M16 and M41 as a by-product of
transactions and are not editable by procurement (BRU-PRO-17). M42 computes the score from
those facts. A buyer can argue with a score; they cannot alter the data underneath it.

Third, **brand partners are modelled as a first-class supplier class, not as an exception**.
They supply consignment stock, they set warranty terms, they audit us, and losing one is the
largest single commercial risk in the supply chain. They get the deepest qualification record,
the most complete document register, and a scorecard that runs in both directions — including
how well 1000FiX performs against *their* requirements.

Fourth, **the model is deliberately affordable for a Bangladeshi supplier base**. A local
trader supplying BDT 30,000 of consumables a quarter cannot be put through a strategic-supplier
qualification, and attempting it produces either a bottleneck or a rubber stamp. Risk-tiered
treatment means a transactional supplier passes a short identity-and-licence check and is
reviewed annually, while a critical single-source importer of genuine OEM parts carries a full
qualification, quarterly review, named alternate-source obligation and continuity plan.

---

## 5. Functional Areas & Features

### 5.1 Supplier Profile & Segmentation

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM2-001 | Supplier profile | Extend the M33 party with a supplier profile: legal identity, classification, supplied categories, capabilities, capacity, geography, currencies and incoterms | **P0** | L1/L5 |
| FR-SRM2-002 | Supplier classification | Classify every supplier as OEM, authorised distributor, local distributor, local trader, importer, service provider, courier partner, recycling partner, **freight forwarder**, **C&F (clearing and forwarding) agent**, **cargo insurer** or **brand partner** (BR-SCM-001) | **P0** | L5 |
| FR-SRM2-003 | Segmentation | Segment suppliers as strategic, preferred, approved, transactional or restricted, derived from spend, criticality and risk, and reviewed on a defined cycle | P1 | L5 |
| FR-SRM2-004 | Risk tiering | Assign a risk tier that determines qualification depth, review frequency and documentation requirements | **P0** | L5 |
| FR-SRM2-005 | Category coverage | Record which spend categories each supplier is qualified to supply, and expose that as the authoritative source for M16's approved-source list | **P0** | L5 |
| FR-SRM2-006 | Supplier 360 | Present one view per supplier: profile, qualification, agreements, prices, open orders, delivery and quality history, risk, documents, contacts and open actions | P1 | L5 |

### 5.2 Qualification, Onboarding & Activation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM2-007 | Self-service registration | Allow a prospective supplier to register through P05, submitting identity, categories, capabilities and documents | P1 | L5 |
| FR-SRM2-008 | Qualification questionnaire | Define category- and tier-specific questionnaires with mandatory evidence attachments and a configurable scoring model | **P0** | L5 |
| FR-SRM2-009 | Qualification workflow | Route a completed qualification for review and approval by category owner, Quality Manager and Procurement Manager as the tier requires | **P0** | L2/L5 |
| FR-SRM2-010 | **Activation gate** | Hold the authoritative activation status per supplier per category, and expose a synchronous decision API that M16 must call before creating any purchase order | **P0** | L5 |
| FR-SRM2-011 | Qualification validity and expiry | Set a validity period per qualification, warn ahead of expiry, and **de-activate automatically on lapse** | **P0** | L5 |
| FR-SRM2-012 | Re-qualification | Trigger re-qualification on expiry, on a material profile change, on a risk-tier change, or on sustained poor performance | P1 | L5 |
| FR-SRM2-013 | Conditional and provisional approval | Permit time-boxed provisional activation with named conditions and an automatic block at expiry | P2 | L5 |
| FR-SRM2-014 | De-activation and blocking | De-activate, suspend or permanently block a supplier with a recorded reason, immediately preventing new orders while leaving open orders visible | **P0** | L5 |
| FR-SRM2-015 | Authorisation evidence | Require, for any supplier qualified to supply genuine-OEM parts, documentary evidence of its authorisation or authorised-distribution status, with an expiry date | **P0** | L5 |

### 5.3 Documents, Compliance & Integrity

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM2-016 | Document register | Hold per supplier: trade licence, VAT/BIN registration, TIN, bank account verification, ISO and other certifications, insurance, brand authorisations, each with issue and expiry dates | **P0** | L5 |
| FR-SRM2-017 | Expiry monitoring | Warn the supplier and the category owner ahead of any document expiry, and apply the configured status consequence on lapse | **P0** | L5 |
| FR-SRM2-018 | Bank detail change control | Require documented verification and second-person approval for any change to supplier bank details, with the change and its approver retained immutably | **P0** | L5 |
| FR-SRM2-019 | Integrity screening | Screen suppliers for sanctions exposure, conflict of interest with 1000FiX employees, and related-party relationships, and require an anti-bribery declaration at qualification | P1 | L5 |
| FR-SRM2-020 | Supplier code of conduct | Record acceptance of the supplier code of conduct as a qualification condition, with version tracking | P2 | L5 |

### 5.4 Agreements, Prices & Commercial Terms

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM2-021 | Framework agreement | Hold supplier agreements with term, scope, committed volume or value, service levels, penalties, rebates, notice periods and renewal terms | **P0** | L2/L5 |
| FR-SRM2-022 | Agreed price list | Hold agreed prices per part per supplier with validity dates, minimum order quantities, lead times and volume breaks, and publish them as the authority for M16 call-off | **P0** | L5 |
| FR-SRM2-023 | Price change governance | Require a supplier price increase to be submitted, justified and approved before it takes effect, and prevent M16 from ordering at an unapproved price | **P0** | L5 |
| FR-SRM2-024 | **Consignment agreement** | Hold consignment terms per brand: parts in scope, holding locations, valuation basis, settlement trigger and cadence, return rights, reconciliation frequency and liability for loss or damage — the terms M15 enforces | **P0** | L5 |
| FR-SRM2-025 | Rebate and volume commitment tracking | Track achievement against committed volumes and calculate rebates earned, raising them for M52 | P2 | L5 |
| FR-SRM2-026 | Agreement expiry and renewal | Warn ahead of agreement expiry, drive the renewal or re-tender decision, and prevent silent lapse into uncontracted spend | P1 | L5 |

### 5.5 Performance, Review & Development

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM2-027 | **Performance scorecard** | Compute a periodic scorecard per supplier from M16 and M41 transaction facts: on-time delivery, delivery-in-full, quality rejection rate, lead-time reliability, price adherence, invoice accuracy, documentation completeness and responsiveness (BR-SCM-007) | **P0** | L5 |
| FR-SRM2-028 | Weighted scoring model | Configure metric weights per category and risk tier, produce a banded overall rating, and show the trend across periods | **P0** | L5 |
| FR-SRM2-029 | Supplier-facing scorecard | Publish each supplier's own scorecard to P05, showing the metrics, the underlying data and the trend | P1 | L5 |
| FR-SRM2-030 | Performance review cycle | Schedule reviews by segment — strategic quarterly, preferred half-yearly, approved annually — with an agenda generated from the scorecard and minuted outcomes | P1 | L5 |
| FR-SRM2-031 | Corrective action request | Raise a corrective action against a supplier with a stated issue, required action, owner and due date; track it to verified closure and escalate on overdue | **P0** | L5 |
| FR-SRM2-032 | Supplier development plan | Maintain improvement plans with milestones for strategic and critical suppliers, and measure their effect on subsequent scores | P2 | L5 |

### 5.6 Risk, Continuity & Category Strategy

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM2-033 | Risk assessment and concentration | Assess and periodically re-assess financial, operational, geographic, compliance, counterfeit and continuity risk per supplier; compute spend and supply concentration per category; flag single-source dependencies for critical parts and require a named qualified alternate or an accepted, approved exception | **P0** | L5 |
| FR-SRM2-034 | Category strategy and base analytics | Hold a category strategy per spend category — market structure, sourcing approach, target supplier count, cost drivers, risks — and report supplier base health: active count, qualification currency, segment mix, concentration, risk distribution and lapse rate | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Synchronous activation decision API** | The qualification gate consumed by M16 is a synchronous call returning an explicit allow/deny plus reason, in ≤ 150 ms at p95. It fails **closed**: an unavailable service denies the order rather than permitting it |
| T-02 | **Category-scoped decisions** | Activation is evaluated per (supplier, category, entity, date). There is no global "approved supplier" state |
| T-03 | **Immutable qualification record** | A qualification decision, its questionnaire responses, its evidence hashes, its scorer and its approver are immutable. Re-qualification creates a new version; it never edits the prior one |
| T-04 | **Scorecard reproducibility** | A published scorecard stores the source fact set, the weighting model version and the computation date. A score can be reproduced and defended in a supplier meeting months later |
| T-05 | **Source-data immutability** | Performance facts arrive from M16 and M41 as events and are never editable within M42. Corrections occur at source and re-flow |
| T-06 | **Bank-change audit chain** | Every bank-detail change retains the prior value, the requester, the verification evidence, the approver and the timestamp, and emits a security event to M29 |
| T-07 | **Document expiry scheduler** | Expiry evaluation runs daily across all suppliers and documents, is idempotent, and applies status consequences exactly once per expiry |
| T-08 | **Conflict-of-interest detection** | Supplier contact and bank details are matched against employee records from M21 to surface related-party candidates, without exposing employee personal data to procurement users |
| T-09 | **Event emission via outbox** | Qualification, activation, de-activation, agreement, scorecard and risk state changes emit through the transactional outbox (AS-08) |
| T-10 | **Supplier portal isolation** | A supplier authenticated to P05 can reach only its own records (EA-01, EA-06); scope is bound to the credential and cannot be widened by request parameters (EA-11) |
| T-11 | **Evidence integrity** | Uploaded qualification evidence is hashed at capture and stored through M24 under the supplier retention class |
| T-12 | **Multi-entity awareness** | Qualification and agreements carry `company_id`; a supplier qualified for one legal entity is not automatically qualified for another (AS-03) |
| T-13 | **Performance** | Supplier 360 loads in ≤ 2 s; scorecard computation across 500 suppliers completes in ≤ 10 min; concentration analysis across all categories in ≤ 2 min |
| T-14 | **Bengali supplier experience** | P05 registration, qualification questionnaires and scorecards are available in Bengali (AS-12) — most local suppliers will not operate in English |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M42 |
|---|---|---|
| **Procurement manager** | Knows the supplier base personally; cannot prove anything about it | A segmented, qualified, scored base; concentration and single-source risks named; review cycles that actually run |
| **Procurement officer** | Uses whichever supplier is known to have the part | Buys from a qualified list for the category, at agreed prices, with performance visible at the point of choosing |
| **Quality manager** | Sees defects but cannot attribute them systematically | Rejection rates by supplier, corrective actions tracked to closure, ISO 8.4 evidence produced as a by-product |
| **Warehouse manager** | Consignment terms exist as an understanding | Consignment agreements are recorded, and M15 enforces them |
| **CFO** | Supplier risk is a conversation, not a register | Concentration, single-source and continuity exposure quantified; bank-change fraud vector closed |
| **Supplier** | No idea how 1000FiX rates them; chases for everything | Sees their own scorecard, maintains their own documents, knows what to fix |
| **Brand partner** | Managed by relationship and email | A recorded agreement, a document register, a two-way performance view and a portal |
| **Internal audit** | Cannot test supplier selection | Complete, immutable qualification and approval trail |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Vendor on-time delivery** | Measurement, publication, review and corrective action — suppliers improve when performance is visible and consequential | **> 92%** (KPI-048); each late critical part is a delayed job and an at-risk SLA |
| **Quality rejection reduction** | Attribution to supplier, corrective action, and qualification consequence for repeat failure | Supports the **< 2%** inspection rejection target owned by M16 |
| **Price discipline** | Agreed price lists with governed increases; M16 cannot order at an unapproved price | Protects the 3–5% purchase-price improvement M16 targets from erosion between negotiations |
| **Counterfeit and brand-authorisation protection** | Authorisation evidence required and expiring for genuine-OEM categories; unqualified suppliers structurally cannot be ordered from | Protects warranty revenue across **17+ brand partnerships**. This is the highest-value risk in Category E |
| **Continuity risk reduction** | Single-source dependencies for critical parts named and given qualified alternates | Removes a class of failure that currently surfaces only when it happens |
| **Fraud loss avoidance** | SOD-01 enforced; bank-detail changes verified and dual-approved; related-party detection | Closes the two most common supplier-fraud vectors |
| **Rebate capture** | Volume commitments tracked and rebates calculated rather than forgotten | Recovers contractual value currently unclaimed |
| **Onboarding effort** | Supplier self-service registration and document maintenance through P05 | Removes a recurring administrative load and improves document currency |
| **Uncontracted spend** | Agreement expiry warnings prevent silent lapse into spot buying | Supports the contract-coverage target of 75% |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **ISO 9001 clause 8.4 conformance** | Criteria for evaluation, selection, monitoring and re-evaluation of external providers, with records. M42 produces this as evidence rather than as an audit-week exercise. 1000FiX's ISO status is a stated competitive advantage and a tender qualifier |
| **Brand audit readiness** | Brand partners audit their authorised service partners. A qualification register, a document set with live expiry status, and a two-way scorecard change the character of that audit |
| **Corporate tender qualification** | Government and corporate clients increasingly ask how a bidder controls its own supply chain. Today the honest answer is "informally" |
| **Anti-bribery posture** | Declarations, conflict-of-interest screening and an auditable selection trail in a market where informal practice is common |
| **Institutional memory** | Supplier knowledge survives the departure of the people who hold it |
| **Negotiating leverage** | Evidence changes the balance of a supplier conversation more than volume does |
| **Foundation for expansion** | A second country needs a supplier base; the qualification framework is reusable, and entity-scoped qualification supports BO-18 |

---

## 8. Lifecycle & State Models

### 8.1 Supplier Lifecycle

```
        ┌──────────────┐
        │  PROSPECT    │  registered via P05 or created internally
        └──────┬───────┘
               │ profile complete, categories declared, documents uploaded
        ┌──────▼──────────┐
        │ IN QUALIFICATION│  questionnaire issued per category and risk tier
        └──────┬───────┬──┘
        scored │       │ failed
               │       └──────────────► REJECTED (reason recorded, re-apply
               │                                    permitted after a period)
        ┌──────▼──────────┐
        │ PENDING         │  category owner · Quality Manager · Procurement Manager
        │ APPROVAL        │  as the risk tier requires
        └──────┬───────┬──┘
     approved  │       │ conditional
        ┌──────▼───┐ ┌─▼───────────────┐
        │  ACTIVE  │ │  PROVISIONAL    │ time-boxed, named conditions
        │(per      │ │  (auto-blocks   │
        │ category)│ │   at expiry)    │
        └──┬───┬───┘ └─────┬───────────┘
           │   │           │ conditions met
           │   │◄──────────┘
           │   │
           │   │ document or qualification expiry ─────────┐
           │   │ sustained poor performance ───────────────┤
           │   │ risk event ───────────────────────────────┤
           │   │                                           │
           │   │                                    ┌──────▼──────┐
           │   └───────────────────────────────────►│  SUSPENDED  │
           │                                        │ (no new POs;│
           │                                        │  open POs   │
           │                                        │  visible)   │
           │                                        └──┬───────┬──┘
           │                       remediated / re-qualified│    │ not remediated
           │◄─────────────────────────────────────────────┘    │
           │                                                    │
           │ relationship ended, or integrity failure     ┌──────▼──────┐
           └─────────────────────────────────────────────►│  BLOCKED    │
                                                          │ (permanent, │
                                                          │  CFO/CEO    │
                                                          │  authority) │
                                                          └─────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Prospect | Registration submitted with legal identity and declared categories | Supplier (P05) / Procurement Officer |
| Prospect | In qualification | Mandatory documents uploaded and readable | System |
| In qualification | Pending approval | Questionnaire complete; score computed; evidence attached | System |
| In qualification | Rejected | Mandatory criterion failed, or score below the category threshold | Procurement Manager |
| Pending approval | Active | Approved at the authority the risk tier requires; **for genuine-OEM categories, authorisation evidence present and unexpired** (BRU-SRM2-05) | Category owner + Quality Manager + Procurement Manager |
| Pending approval | Provisional | Approved with named, time-boxed conditions | Procurement Manager |
| Provisional | Active | All conditions evidenced before expiry | Procurement Manager |
| Provisional | Suspended | Conditions not met by expiry | System (automatic) |
| Active | Suspended | Qualification or mandatory document lapsed; sustained poor performance; risk event; failed corrective action | System / Procurement Manager |
| Suspended | Active | Remediation evidenced and re-qualification approved | Procurement Manager |
| Any | Blocked | Integrity failure, sanctions match, counterfeit supply, or relationship terminated | CFO or CEO |

### 8.2 Qualification & Corrective Action Cycles

```
  QUALIFICATION CYCLE                    CORRECTIVE ACTION CYCLE

  Questionnaire issued                   Scorecard band breach ·
        │                                inspection rejection ·
  Supplier responds + evidence           delivery failure · audit finding
        │                                        │
  Scored against the model               CAR raised — issue, required action,
        │                                owner, due date
  Reviewed and approved                          │
        │                                Supplier responds with root cause
  ACTIVE for a validity period           and containment
        │                                        │
  ─ 60 days ► expiry warning             Action verified by Quality Manager
  ─ 30 days ► escalation                         │
  ─  0 days ► AUTO-SUSPEND               ┌───── closed ──── verified effective
        │                                │              │
  Re-qualification ──────────────────────┘         not effective
                                                        │
                                          escalate ► review ► suspension
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-SRM2-01 | **A purchase order may only be raised to a supplier that is Active for the relevant category on the order date.** The gate is evaluated by M42 and enforced by M16 | **H** | Procurement Manager |
| BRU-SRM2-02 | The activation decision service fails closed: if it is unavailable, purchase orders are blocked, not permitted | **H** | CTO |
| BRU-SRM2-03 | Qualification is granted per category and per legal entity, never globally | **H** | Procurement Manager |
| BRU-SRM2-04 | A qualification or mandatory document that expires automatically suspends the supplier for the affected categories | **H** | Procurement Manager |
| BRU-SRM2-05 | A supplier may not be qualified to supply genuine-OEM parts without current documentary evidence of authorisation or authorised-distribution status | **H** | Quality Manager |
| BRU-SRM2-06 | The user who creates or qualifies a supplier may not approve that supplier's invoice (SOD-01) | **H** | CFO |
| BRU-SRM2-07 | A change to supplier bank details requires documented verification and second-person approval, and is retained immutably with a security event | **H** | CFO |
| BRU-SRM2-08 | Performance facts originate in M16 and M41 and are not editable within M42 | **H** | Supply Chain Director |
| BRU-SRM2-09 | A published scorecard is immutable; a correction is a re-publication with a stated reason | **H** | Procurement Manager |
| BRU-SRM2-10 | A supplier scoring in the lowest band for two consecutive periods enters mandatory corrective action; a third consecutive period triggers suspension review | **C** | Procurement Manager |
| BRU-SRM2-11 | A corrective action overdue beyond its due date escalates to the Procurement Manager, then to the Supply Chain Director | **C** | Quality Manager |
| BRU-SRM2-12 | Provisional activation is time-boxed and blocks automatically at expiry with no grace period | **H** | Procurement Manager |
| BRU-SRM2-13 | A critical part with a single qualified source requires either a named qualified alternate or a documented risk acceptance approved by the Supply Chain Director | **H** | Supply Chain Director |
| BRU-SRM2-14 | M16 may not place an order at a price above the approved price list without a price change approved in M42 | **H** | Procurement Manager |
| BRU-SRM2-15 | Consignment terms recorded in M42 are the authority for M15's consignment enforcement; M15 does not hold independent terms | **H** | Supply Chain Director |
| BRU-SRM2-16 | A supplier with a confirmed sanctions match or a confirmed counterfeit supply is blocked permanently by CFO or CEO authority, and blocking cannot be reversed below that authority | **H** | CFO |
| BRU-SRM2-17 | A related-party or conflict-of-interest match must be declared and approved before activation | **H** | CFO |
| BRU-SRM2-18 | Review cadence follows the segment: strategic quarterly, preferred half-yearly, approved annually, transactional on exception | **C** | Procurement Manager |
| BRU-SRM2-19 | An expiring framework agreement warns at 90, 60 and 30 days; expiry without renewal moves the supplier's spend to uncontracted and is reported | **C** | Procurement Manager |
| BRU-SRM2-20 | A supplier sees only its own records in P05, with no cost, margin or other party's data (EA-01, EA-02, EA-06) | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.supplier.profile` | `fix_supplier_profile` | The supplier role over an M33 party | party_id, classification, segment, risk_tier, categories, capabilities, capacity_note, currencies, incoterms, payment_terms_default, state, company_id, owner_user_id |
| `fix.supplier.category` | `fix_supplier_category` | Category-scoped standing | supplier_id, spend_category_id, qualification_id, status (active/provisional/suspended/blocked), effective_from, effective_to, conditions |
| `fix.supplier.qualification` | `fix_supplier_qualification` | An immutable qualification version | supplier_id, spend_category_id, version, questionnaire_id, responses_json, evidence_ids, score, threshold, result, scored_by, approved_by, approved_at, valid_from, valid_until |
| `fix.qualification.questionnaire` | `fix_qualification_questionnaire` | Template per category and tier | name, spend_category_id, risk_tier, sections, questions, weights, pass_threshold, mandatory_criteria, version, active |
| `fix.supplier.document` | `fix_supplier_document` | Compliance document register | supplier_id, doc_type (trade_licence/vat_bin/tin/bank_verification/iso_cert/brand_authorisation/insurance), reference, issued_on, expires_on, document_id (M24), verified_by, verified_at, status |
| `fix.supplier.bank.change` | `fix_supplier_bank_change` | Controlled bank-detail change | supplier_id, previous_value_hash, new_value_ref, requested_by, verification_evidence_ids, approved_by, approved_at, security_event_id |
| `fix.supplier.agreement` | `fix_supplier_agreement` | Framework or supply agreement | supplier_id, type (framework/supply/consignment/service/courier), reference, term_from, term_to, committed_value, committed_volume, service_levels, penalties, rebate_terms, notice_days, renewal_mode, contract_doc_id, state |
| `fix.supplier.price.list` | `fix_supplier_price_list` | Agreed prices | agreement_id, supplier_id, part_id, price, currency, uom, moq, lead_time_days, volume_breaks, valid_from, valid_to, approved_by |
| `fix.supplier.price.change` | `fix_supplier_price_change` | Governed price movement | price_list_id, part_id, old_price, proposed_price, variance_pct, justification, requested_at, decided_by, decision, effective_from |
| `fix.consignment.agreement` | `fix_consignment_agreement` | Brand consignment terms | supplier_id (brand), parts_scope, holding_location_ids, valuation_basis, settlement_trigger, settlement_cadence, return_rights, reconciliation_frequency, loss_liability, term_from, term_to |
| `fix.supplier.scorecard` | `fix_supplier_scorecard` | A published period score | supplier_id, period, model_version, metrics_json, weighted_score, band, trend, source_fact_ref, published_at, published_by |
| `fix.scorecard.model` | `fix_scorecard_model` | Weighted scoring configuration | name, spend_category_id, risk_tier, metrics, weights, band_thresholds, version, effective_from |
| `fix.supplier.review` | `fix_supplier_review` | Performance review meeting | supplier_id, period, scheduled_for, held_on, attendees, agenda_ref, scorecard_id, minutes_doc_id, outcomes, next_review_due |
| `fix.supplier.car` | `fix_supplier_car` | Corrective action request | supplier_id, source (scorecard/inspection/delivery/audit), issue, required_action, raised_by, raised_at, due_date, supplier_response, root_cause, verified_by, verified_at, effectiveness, state |
| `fix.supplier.development.plan` | `fix_supplier_development_plan` | Improvement programme | supplier_id, objectives, milestones, owner, start, target_end, progress, measured_effect |
| `fix.supplier.risk` | `fix_supplier_risk` | Risk assessment | supplier_id, assessed_at, financial, operational, geographic, compliance, counterfeit, continuity, overall_tier, mitigations, next_assessment_due, assessor_id |
| `fix.supply.concentration` | `fix_supply_concentration` | Category dependency analysis | spend_category_id, period, supplier_count, top_supplier_share, hhi, single_source_parts, critical_single_source_parts, alternate_status |
| `fix.category.strategy` | `fix_category_strategy` | Category plan | spend_category_id, market_structure, sourcing_approach, target_supplier_count, cost_drivers, risks, owner, reviewed_at |
| `fix.supplier.contact` | `fix_supplier_contact` | Role-based supplier contacts | supplier_id, party_contact_id (M33), role (commercial/logistics/quality/finance/escalation), portal_user_id, active |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party`, `fix.address`, `fix.party.role` | M33 | Read and extend |
| `fix.purchase.order`, `fix.goods.receipt`, `fix.invoice.match`, `fix.purchase.price.history`, `fix.purchase.rtv` | M16 | Read as performance facts (immutable here) |
| `fix.wh.inbound.line` (inspection outcomes, packaging quality) | M41 | Read as performance facts |
| `fix.consignment.balance`, `fix.consignment.reconciliation` | M15 | Read for brand relationship review |
| `fix.nonconformance`, `fix.checklist.template` | M23 | Read; raise supplier non-conformances |
| `fix.spend.category` | M16 | Read |
| `fix.contract` (engine, templates, e-signature) | M08 | Use |
| `fix.document` | M24 | Store agreements and evidence |
| `fix.ap.invoice`, `fix.ap.payment.run` | M52 | Read for invoice accuracy and payment behaviour |
| `fix.employee` (conflict-of-interest matching only) | M21 | Restricted match service; no personal data exposed |
| `fix.import.consignment` | M44 | Read for forwarder and C&F agent performance |
| `fix.consignment` (courier performance) | M03 | Read |
| `fix.recycling.partner` | M18 | Read for environmental compliance status |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-SRM2-01 | Supplier registers through P05 | Create the prospect, validate mandatory fields and documents, issue the questionnaire for the declared categories and risk tier | Route to the procurement officer for manual onboarding |
| AUT-SRM2-02 | Questionnaire submitted | Score against the model, check mandatory criteria, route for approval at the tier's authority | Hold and notify the category owner |
| AUT-SRM2-03 | Qualification approved | Activate the supplier for the approved categories and publish the decision to M16's gate | Retry; the gate denies until published |
| AUT-SRM2-04 | Qualification or mandatory document nears expiry (60 / 30 / 7 days) | Notify the supplier and the category owner with the specific document and date | Escalate on the second notice |
| AUT-SRM2-05 | Qualification or mandatory document lapses | **Suspend the supplier for the affected categories automatically**; notify procurement, the supplier and any open-order owners | Hard suspension; no grace |
| AUT-SRM2-06 | Provisional activation reaches expiry with conditions unmet | Suspend automatically and notify | Hard suspension |
| AUT-SRM2-07 | Period end | Compute scorecards from M16 and M41 facts, band them, publish to the supplier through P05, and notify category owners of band changes | Retain the prior scorecard and alert |
| AUT-SRM2-08 | Supplier scores in the lowest band for two consecutive periods | Raise a corrective action request automatically and schedule a review | Notify the Procurement Manager |
| AUT-SRM2-09 | Third consecutive lowest-band period | Open a suspension review and notify the Procurement Manager and Supply Chain Director | Escalate |
| AUT-SRM2-10 | Corrective action passes its due date | Escalate to the Procurement Manager, then to the Supply Chain Director | Report on the overdue register |
| AUT-SRM2-11 | Inspection rejection recorded by M41 or M16 | Attach the quality event to the supplier record and update the running rejection rate | Queue and retry |
| AUT-SRM2-12 | Delivery recorded late or short by M16 | Attach the delivery event and update on-time and in-full running rates | Queue and retry |
| AUT-SRM2-13 | Bank-detail change requested | Require verification evidence, route for second-person approval, emit a security event to M29, and notify the previously recorded contact | Hard block until approved |
| AUT-SRM2-14 | Supplier profile or contact matches an employee record | Flag a potential conflict of interest for declaration and approval before activation | Block activation |
| AUT-SRM2-15 | Framework agreement approaches expiry (90 / 60 / 30 days) | Notify the category owner and open the renewal or re-tender decision | Report as uncontracted spend risk at expiry |
| AUT-SRM2-16 | Supplier price increase submitted | Route for approval with the price history and variance; on approval, publish the new price list and notify M16 | Retain the old price; M16 blocks orders at the new price |
| AUT-SRM2-17 | Monthly | Recompute concentration and single-source exposure per category; flag critical parts without a qualified alternate | Report only |
| AUT-SRM2-18 | Review cycle due for a segment | Schedule the review, generate the agenda from the scorecard, and notify participants | Report the overdue review |
| AUT-SRM2-19 | Volume commitment achievement reaches a rebate threshold | Calculate the rebate earned and raise it to M52 | Report for manual claim |

---

## 12. Interfaces

### 12.1 Upstream — M42 Consumes

| Source | What | Mechanism |
|---|---|---|
| M33 Party Master | Supplier party identity, addresses, contacts, tax identifiers | REST |
| **M16 Procurement** | Delivery performance facts, quality rejection facts, spend, price behaviour, RTV outcomes | Events + warehouse extract |
| M41 Warehouse Management | Inspection outcomes, receipt accuracy, packaging quality | Events |
| M15 Inventory | Consignment balances and reconciliation outcomes; serial anomalies attributable to a supplier | Events |
| M23 Quality | Non-conformances and audit findings | Events |
| M52 Accounts Payable | Invoice accuracy and payment behaviour | Events |
| M44 Import | Freight forwarder and C&F agent performance | Events |
| M03 Logistics | Courier partner delivery performance | Events |
| M18 E-Waste | Recycling partner environmental compliance status | Events |
| M21 Core HR | Restricted employee-match service for conflict-of-interest detection | REST (privacy-scoped) |
| M08 / M24 | Contract engine, templates and e-signature | REST |

### 12.2 Downstream — M42 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M16 Procurement** | **The activation decision** (synchronous gate), approved categories, agreements, approved price lists, payment terms | REST (synchronous) + events |
| M15 Inventory | Consignment agreement terms that M15 enforces | REST |
| M41 Warehouse Management | Supplier packaging and labelling requirements | REST |
| M43 Demand Planning | Supplier lead times, reliability and capacity constraints as planning inputs | REST |
| M44 Import | Qualified freight forwarders, C&F agents and their terms | REST |
| M03 Logistics | Qualified courier partners and contracted rate authority | REST |
| M52 Accounts Payable | Approved payment terms, verified bank details, rebates earned | Events |
| M23 Quality | Supplier corrective actions and their verified closure | Events |
| M60 GRC | Supply-side risk register entries for enterprise aggregation | Events |
| M25 BI / M62 Data Platform | Supplier, qualification, scorecard and risk facts | Warehouse extract |
| P05 Vendor Portal | Registration, qualification, documents, agreements, scorecard, corrective actions | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `supplier.registered` | party, declared categories, classification | M16, M33 |
| `supplier.qualified` | supplier, category, score, validity, approver | M16, M23 |
| `supplier.activated` | supplier, categories, effective from, entity | **M16**, M15, M03, M44 |
| `supplier.suspended` | supplier, categories, reason, effective from | **M16**, M15, M03, M44, M52 |
| `supplier.blocked` | supplier, reason, authority | **M16**, M52, M29, M60 |
| `supplier.qualification_expiring` | supplier, category, expiry date | M16, P05 |
| `supplier.document_expired` | supplier, document type, consequence applied | M16, M52, M60 |
| `supplier.agreement_signed` | supplier, agreement, term, committed value | M16, M52, M54 |
| `supplier.agreement_expiring` | supplier, agreement, expiry, renewal decision due | M16, M54 |
| `supplier.price_list_published` | supplier, parts, prices, validity | **M16**, M43, M11 |
| `supplier.price_change_approved` | supplier, part, old price, new price, effective from | M16, M43, M11 |
| `consignment.agreement_updated` | brand, parts scope, settlement terms, reconciliation cadence | **M15**, M52 |
| `supplier.scorecard_published` | supplier, period, metrics, band, trend | M16, M23, P05 |
| `supplier.car_raised` | supplier, issue, required action, due date | M23, P05 |
| `supplier.car_closed` | supplier, CAR, effectiveness verdict | M23 |
| `supplier.risk_assessed` | supplier, dimensions, overall tier, mitigations | M60, M43 |
| `supply.concentration_alert` | category, top supplier share, critical single-source parts | M43, M16, M60 |
| `supplier.bank_details_changed` | supplier, requester, approver | M52, **M29** |
| `supplier.rebate_earned` | supplier, agreement, period, amount | M52, M19 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-SRM2-01 | P05 Vendor & Supplier Portal | Bidirectional | Registration, qualification, document maintenance, scorecard, corrective action response |
| INT-SRM2-02 | Bangladesh trade licence and VAT/BIN verification *(manual or API where available)* | Outbound | Verification of supplier registration documents at qualification |
| INT-SRM2-03 | Sanctions and denied-party screening list *(file-based)* | Inbound | Integrity screening at qualification and periodically thereafter |
| INT-SRM2-04 | Brand partner authorisation confirmation | Bidirectional | Verification that a distributor's claimed authorisation is current, where the brand offers a channel |
| INT-SRM2-05 | Supplier email | Outbound | The fallback channel for suppliers not using P05 |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| **`/api/v1/suppliers/{id}/activation`** | **GET** | **The qualification gate — allow/deny for (supplier, category, entity, date) with reason** | **M16 (mandatory)** |
| `/api/v1/suppliers` | POST | Register or create a supplier | P05, P03 |
| `/api/v1/suppliers/{id}` | GET | Supplier 360 | P03, P06 |
| `/api/v1/suppliers/{id}/qualification` | POST | Submit a qualification response with evidence | P05 |
| `/api/v1/suppliers/{id}/qualification/approve` | POST | Approve, conditionally approve or reject | P03 |
| `/api/v1/suppliers/{id}/suspend` | POST | Suspend or block with reason | P03 |
| `/api/v1/suppliers/{id}/documents` | POST | Upload or renew a compliance document | P05, P03 |
| `/api/v1/suppliers/{id}/bank-details` | POST | Request a bank-detail change (verification-gated) | P05, P03 |
| `/api/v1/suppliers/{id}/agreements` | POST | Create or renew an agreement | P03 |
| `/api/v1/suppliers/{id}/price-list` | GET | Approved prices for M16 call-off | **M16**, P03 |
| `/api/v1/suppliers/{id}/price-change` | POST | Submit a price increase for approval | P05 |
| `/api/v1/suppliers/{id}/scorecard` | GET | Published scorecard and trend | P05, P03, P06 |
| `/api/v1/suppliers/{id}/car` | POST | Raise or respond to a corrective action | P03, P05 |
| `/api/v1/suppliers/{id}/risk` | GET | Risk assessment and tier | P03, M60 |
| `/api/v1/categories/{id}/concentration` | GET | Concentration and single-source exposure | P03, M43, P06 |
| `/api/v1/consignment-agreements/{brand}` | GET | Consignment terms for enforcement | **M15** |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R19 Procurement Officer | C R U | Supplier profiles, qualifications, documents in own categories |
| R17 Inventory Manager | R | Supplier performance and lead times |
| R32 Quality Manager / ISO Coordinator | C R U A | Qualification quality criteria, inspection-driven CARs, CAR verification, authorisation evidence |
| R26 Finance Manager | R U A | Bank details, payment terms, rebates, financial risk |
| R03 Chief Financial Officer | R A | All; sole authority (with CEO) to block a supplier permanently; approves bank-detail changes above threshold |
| R05 Operations Director | R | All |
| R06 Branch Manager | R | Suppliers serving own branch |
| R15 Logistics Coordinator | R | Courier partner records |
| R33 IT / System Administrator | R U | Configuration; no qualification or approval rights |
| R38 Vendor | R U | **Own record only** — registration, qualification response, documents, own scorecard, own CAR response (P05) |

**Procurement Manager rights.** Exercised through R19 with an elevated grant covering
qualification approval, activation and suspension, segmentation, scorecard model configuration,
price-change approval and agreement execution.

**Supply Chain Director rights.** Exercised through R05 with a category-strategy grant covering
single-source risk acceptance, concentration exception approval and the second escalation tier
for corrective actions.

**Field-level restrictions.** Supplier bank details are visible only to R26, R27 and R03
(`05-04` §5, `bank_account`). Employee-match results for conflict-of-interest screening return
a boolean and a case reference only — never the employee's identity — except to R03 and R30.
Suppliers never see any 1000FiX cost, margin, internal note or any other supplier's data
(EA-02).

**Segregation of duties.**
- **SOD-01 enforced:** the user who creates or qualifies a supplier cannot approve that supplier's invoice — hard block.
- The requester of a bank-detail change cannot approve it.
- A single user cannot both raise and verify the closure of a corrective action.
- The user who scores a qualification cannot be its sole approver at strategic or critical tiers.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Supplier base health** | Procurement Manager, Supply Chain Director | Monthly | Active count by segment and class, qualification currency, expiries due, lapse rate, risk distribution |
| **Supplier scorecards** | Procurement Manager, category owners, supplier (P05) | Monthly / quarterly | On-time delivery, in-full rate, rejection rate, lead-time reliability, price adherence, invoice accuracy, band and trend |
| Vendor on-time delivery | Procurement Manager, Operations Director | Monthly | Against the > 92% target, by supplier, category and criticality |
| Quality performance by supplier | Quality Manager, Procurement Manager | Monthly | Rejection rate, defect types, RTV volume, repeat offenders |
| **Concentration and single-source risk** | Supply Chain Director, CFO | Monthly | Top-supplier share and HHI per category; critical parts without a qualified alternate; accepted exceptions |
| Supplier risk register | CFO, Supply Chain Director, M60 | Quarterly | Risk by dimension and tier, mitigations, assessments overdue |
| Qualification pipeline | Procurement Manager | Weekly | Prospects, in qualification, pending approval, ageing, rejection reasons |
| Document expiry register | Procurement Officer, Procurement Manager | Weekly | Documents expiring at 60/30/7 days; lapsed documents and their status consequence |
| Corrective action register | Quality Manager, Procurement Manager | Monthly | Open CARs, ageing, overdue, verified effectiveness rate |
| Agreement and contract coverage | Procurement Manager, CFO | Quarterly | Agreements by expiry, renewal decisions due, share of spend under agreement |
| Price governance | Procurement Manager, CFO | Monthly | Price changes requested, approved and rejected; price drift by category |
| **Brand partner relationship pack** | CCO, Warehouse Manager, Procurement Manager | Quarterly | Per brand: consignment position, warranty claim performance, parts supply reliability, open issues, audit status |
| Rebate and commitment tracking | Finance Manager, Procurement Manager | Quarterly | Volume achieved against commitment, rebate earned and claimed |
| Supplier integrity register | CFO, Internal Audit | Quarterly | Conflict-of-interest declarations, related-party matches, sanctions screening outcomes, bank-detail changes |
| Category strategy review | Supply Chain Director, CCO | Annually | Market structure, supplier landscape, sourcing approach and cost drivers per category |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W5 Target | W8 Target |
|---|---|---|---|---|
| **KPI-048** | Vendor on-time delivery *(measured by M16, **owned as a relationship outcome by M42** — see the note in `M16` §15)* | unmeasured | 88% | **> 92%** |
| — | Delivered-in-full rate | unmeasured | 90% | **96%** |
| — | Supplier quality rejection rate | unmeasured | < 4% | **< 2%** |
| — | Active suppliers with current qualification | 0% | 95% | **100%** |
| — | Purchase orders to unqualified suppliers | unknown | **0** | **0** |
| — | Critical parts with a qualified alternate source | unknown | 70% | **95%** |
| — | Suppliers with an expired mandatory document still transacting | unknown | **0** | **0** |
| — | Scorecards published on schedule | 0% | 95% | **100%** |
| — | Corrective actions closed within due date | n/a | 80% | **92%** |
| — | Corrective action effectiveness (no recurrence within two periods) | n/a | 70% | **85%** |
| — | Performance reviews held on cadence | 0% | 85% | **95%** |
| — | Supplier self-service document currency (maintained via P05) | 0% | 60% | **85%** |
| — | Spend under agreement (contract coverage) | unknown | 55% | **75%** |
| — | Unapproved price increases reaching a purchase order | unknown | **0** | **0** |
| — | Supplier lead-time reliability (actual within ± 2 days of quoted) | unmeasured | 80% | **90%** |

> **Register note.** KPI-048 is the only canonical identifier in `06-02` §2.6 touching M42, and
> it is assigned there to M16 — the conflict and its resolution are documented in `M16` §15.
> `_CATEGORY_OVERVIEW.md` §7 assigns the metric to M42. **Fourteen further metrics above are
> unregistered and require `KPI-0nn` allocation in `06-02` — an audit action.**

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `contacts` and `purchase` vendor foundation — vendor record, pricelists, payment terms | 16% |
| L2 | OCA `partner-contact` (roles, extended attributes), `contract` (agreement lifecycle), `server-tools` (audit) | 22% |
| L5 | `cd_vendor_ext`, `cd_supplier_qualification`, `cd_supplier_scorecard`, `cd_supplier_risk` | 62% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 1 of 4 identifiers below are claimed by another module: **CD-072** also claimed by M55. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-072 | `cd_vendor_ext` — supplier profile, classification, segmentation, category coverage, contacts, supplier 360, P05 surface | Odoo module | 4 PW |
| **CD-149** | `cd_supplier_qualification` — questionnaires, scoring, approval workflow, **activation gate service**, validity and expiry, document register, bank-change control, integrity screening | Odoo module + service | 6 PW |
| **CD-150** | `cd_supplier_scorecard` — fact ingestion, weighted scoring models, publication, review cycle, corrective actions, development plans | Odoo module | 4 PW |
| **CD-151** | `cd_supplier_risk` — risk assessment, concentration and single-source analysis, continuity requirements, category strategy | Odoo module | 2 PW |

> CD-072 is reallocated from M16 (where `02-05` §5.2 originally placed `cd_vendor_ext`).
> CD-149…151 are claimed from the extension block for modules M31–M67. **All CD IDs remain
> provisional** pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M42 is scheduled in **W4** (P1) but declares a dependency on 1 module(s) that land later: **M23** (W5). One of three things must be true before the W4 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W4 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M42 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W4 plan for M42 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M33 Party Master (W1) | The supplier is a party role; the party record must exist first |
| M16 Procurement (W3) | The performance facts that feed every scorecard originate in M16 |
| M23 Quality (W5) | Inspection standards and non-conformance; the CAR loop connects fully at W5, with a simplified CAR available from W4 |
| M24 Documents (W3) | Agreement and evidence storage with retention |
| M52 Accounts Payable (W3) | Invoice accuracy facts and rebate claims |
| M08 Contract Lifecycle (W4) | Shared contract engine and e-signature for framework agreements |
| M29 Identity (W1) | Supplier portal authentication and the security events for bank-detail changes |

> **The W3 qualification slice — mandatory, not optional.** M16 lands in **W3** and depends on
> M42's activation gate (BRU-PRO-02, BRU-SRM2-01), but M42 is scheduled for **W4**. A minimal
> slice of M42 must therefore ship **with M16 in W3**:
>
> | W3 slice (must ship with M16) | Deferred to W4 |
> |---|---|
> | `fix.supplier.profile` with classification and risk tier | Segmentation and supplier 360 |
> | `fix.supplier.category` with active/suspended status | Provisional activation |
> | A single simplified qualification questionnaire per risk tier | Category- and tier-specific questionnaires with scoring models |
> | `fix.supplier.document` with expiry monitoring and auto-suspension | Integrity screening, code of conduct |
> | **The activation decision API** (`/activation`) | — |
> | Approved price lists (M16 needs them to call off) | Price-change governance workflow |
> | Consignment agreements (M15 needs the terms from W2 — **see the W2 note below**) | Rebate tracking |
> | — | Scorecards, reviews, CARs, development plans, risk, concentration, category strategy |
>
> **A further W2 dependency exists.** M15 enforces consignment rules from W2 and reads the terms
> from `fix.consignment.agreement`. Either the consignment agreement entity ships as a W2 stub
> under M15's build with ownership transferring to M42 in W3, or M15's W2 consignment terms are
> configuration-held and migrated. Raised as Q-01. **Effort for the W3 slice is estimated at
> 5 of the 16 PW and must be scheduled in Wave 3, not Wave 4.**

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Existing supplier list (accounts payable records, purchase history) | 40–120 active, 200–400 historical | `fix.supplier.profile` | W3 (slice) |
| Supplier documents (trade licences, VAT registrations) | Held in files or not at all | `fix.supplier.document` | W3–W4, supplier-supplied via P05 |
| Agreed price lists | 40–120 suppliers | `fix.supplier.price.list` | W3 (slice) |
| Framework agreements and contracts | Paper or email | `fix.supplier.agreement` | W4 |
| Brand consignment agreements | 17+ brands | `fix.consignment.agreement` | **W2–W3 (see the note above)** |
| Historical delivery and quality performance | Not recorded | — | **Not migrated** — scorecards start from M16 go-live |

> **Position on scorecard history.** No performance history exists to migrate. Scorecards
> therefore begin accumulating from M16's W3 go-live, and the first meaningful bands appear one
> quarter later. Publishing a scorecard built on fewer than two periods of data would damage
> supplier trust in the mechanism at exactly the moment it needs to be established. **First
> publication is scheduled for the end of W4.**

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | M16 cannot create a purchase order for a supplier that is not Active for the order's category on the order date, via any path | Negative test on UI, API and automation |
| AC-02 | The activation decision service fails closed when unavailable | Induced-outage test showing PO creation blocked |
| AC-03 | The activation decision returns in ≤ 150 ms at p95 under production PO volume | Performance test |
| AC-04 | Qualification is granted per category; a supplier qualified for one category cannot be ordered from in another | Negative test |
| AC-05 | An expiring mandatory document suspends the supplier automatically at expiry, with no grace period | Time-shifted scripted scenario |
| AC-06 | A supplier cannot be qualified for genuine-OEM parts without current authorisation evidence | Negative test |
| AC-07 | A qualification record cannot be edited after approval; re-qualification creates a new version | Negative test plus schema review |
| AC-08 | A bank-detail change requires verification evidence and a second approver, emits a security event, and notifies the previously recorded contact | Scripted scenario with M29 log verification |
| AC-09 | SOD-01 is enforced: the creator or qualifier of a supplier cannot approve that supplier's invoice | SoD negative test |
| AC-10 | Scorecards compute from M16 and M41 facts only, and no procurement user can alter a source fact or a published score | Negative test plus write-path audit |
| AC-11 | A published scorecard is reproducible from its stored fact set and model version | Recomputation test on a three-month-old scorecard |
| AC-12 | Two consecutive lowest-band periods raise a corrective action automatically | Scripted scenario |
| AC-13 | A critical part with a single qualified source is flagged, and the flag clears only on a qualified alternate or an approved risk acceptance | Scripted scenario |
| AC-14 | M16 cannot place an order above the approved price list without an approved price change | Negative test |
| AC-15 | M15 reads consignment terms from M42 and enforces them; changing a term in M42 changes M15's enforcement | Integration test |
| AC-16 | A supplier in P05 can see only its own record, and cannot widen scope through request parameters | Penetration test against EA-01, EA-06, EA-11 |
| AC-17 | A supplier can complete registration, qualification and document renewal end to end in Bengali through P05 | Field test with five local suppliers (AS-12) |
| AC-18 | The W3 qualification slice supports M16's W3 go-live with no soft-warning fallback | W3 integration test |
| AC-19 | Procurement Manager and Quality Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 19 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Where do brand consignment agreement terms live in W2**, before M42 exists? A W2 stub owned by M15, or configuration migrated to M42 in W3? | CTO / Warehouse Manager | W2 minus 2 months |
| Q-02 | Is the W3 qualification slice approved and resourced (≈5 PW pulled forward from W4)? | Procurement Manager / CTO | W3 minus 3 months |
| Q-03 | What qualification criteria apply per risk tier, and who owns each spend category? | Procurement Manager / Quality Manager | W3 build |
| Q-04 | What is the scorecard weighting model per category, and who approves it? | Procurement Manager | W4 build |
| Q-05 | Are brand partners qualified through the same framework, or does their status as principal make qualification inappropriate? What does the relationship look like in the system? | CCO / Procurement Manager | W4 design |
| Q-06 | Will local suppliers realistically adopt P05, and what is the fallback operating model — procurement enters on their behalf? | Procurement Manager | W4 design |
| Q-07 | Which sanctions or denied-party list is used, how is it obtained, and at what frequency is it refreshed? | CFO / Legal | W4 build |
| Q-08 | Is conflict-of-interest matching against employee records permissible under the Personal Data Protection Act 2026, and what is the lawful basis? | Legal / CTO | W4 build |
| Q-09 | What is the threshold above which a bank-detail change requires CFO rather than Finance Manager approval? | CFO | W3 build |
| Q-10 | Which parts are designated critical for the purpose of the alternate-source obligation, and who maintains that designation? | Supply Chain Director / Inventory Manager | W4 build |
| Q-11 | Do freight forwarders and C&F agents go through the same qualification framework as parts suppliers, or a specialised one? M44 depends on the answer. | Procurement Manager | W5 (M44 design) |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §4 (why procurement and supplier management are separate), §6, §7 ·
`M16_Procurement_and_Strategic_Sourcing.md` §3, §9 BRU-PRO-02, §15 (the KPI-048 resolution),
§16.3 (the W3 slice) · `M15_Spare_Parts_and_Inventory_Management.md` §5.2 (consignment
enforcement) · `M44_Import_Trade_Compliance_and_Landed_Cost.md` (forwarder and C&F
qualification) · `M43_Demand_Planning_and_Replenishment.md` (lead time and reliability inputs) ·
`03_Modules/A_Service_Delivery_and_Operations/M03_Service_Logistics_and_Reverse_Logistics.md`
§3.3 (courier: operational vs commercial ownership) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category E (code note on `SRM2`) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §5, §6 SOD-01, §8 EA-01/EA-02/EA-06/EA-11 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §2.6 (KPI-048) ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P05, P08

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-SCM-001, BR-SCM-007,
BR-INV-010 · `1000FiX_Services_Company_Profile.md` §Authorized Service Partnerships (17+ brands),
§Quality & Certification (ISO)

**External benchmark**
[SAP Ariba Supplier Lifecycle and Performance](https://www.sap.com/products/spend-management/supplier-lifecycle.html) —
registration, qualification, segmentation by risk and business relevance, performance,
development · [SAP Ariba SLP qualification, scoring and approval flows](https://learning.sap.com/courses/discovering-sap-ariba-supplier-management/explaining-sap-ariba-s-supplier-lifecycle-and-performance-processes_cc7c5e73-dc08-4acc-88eb-c9d5bd4e5bf7) ·
[SAP supplier performance management scorecards](https://help.sap.com/docs/strategic-sourcing/running-supplier-performance-management-reviews/creating-and-managing-supplier-performance-management-scorecards) ·
[SAP Ariba SLP practice — qualification questionnaires, scoring models, risk segmentation](https://www.multisoftsystems.com/erp/sap-ariba-supplier-lifecycle-and-performance-training) ·
Oracle Fusion Cloud Supplier Management — qualification areas, expiry and reassessment,
supplier profile change approval · Microsoft Dynamics 365 vendor collaboration — supplier
self-service onboarding and maintenance · ISO 9001:2015 clause 8.4 — control of externally
provided processes, products and services · [Counterfeiting and grey-market risk in electronics supply chains](https://www.loftware.com/resources/white-papers/2024/counterfeiting-the-rising-threat-to-electronics-manufacturers) ·
OCA `partner-contact` and `contract` — partner roles and agreement lifecycle

---

*Module M42 · Category E · 1000FiX ERP System v2.0 · CONFIDENTIAL*
