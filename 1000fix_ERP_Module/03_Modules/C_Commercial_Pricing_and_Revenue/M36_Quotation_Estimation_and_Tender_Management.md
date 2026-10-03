---
id: FIX-ERP2-M36
module_id: M36
module_code: QTE
module_name: Quotation, Estimation & Tender Management
category: C — Commercial, Pricing & Revenue
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Commercial Squad
priority: P1
wave: W3
---

# M36 — Quotation, Estimation & Tender Management
### Category C · Code `QTE` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M36 |
| **Module code** | `QTE` |
| **Category** | C — Commercial, Pricing & Revenue |
| **Status** | ★ New — split out of the former M11 "Sales, Quotation & Dynamic Pricing" during v2.1 re-scoping |
| **Priority** | **P1** |
| **Delivery wave** | W3 (Months 9–13) |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `sale`) + L2 (OCA `sale_order_revision`, `sale_quotation_*`, `sale_order_approval`) + L5 (custom) |
| **Custom modules** | `cd_estimate`, `cd_quotation`, `cd_approval_loop`, `cd_tender`, `cd_quote_analytics` |
| **Requirement range** | FR-QTE-001 … FR-QTE-048 |
| **Requirement count** | **48** *(measured; register estimate 32)* |
| **Effort estimate** | **22 person-weeks** *(measured; register estimate 17 PW)* |
| **Depends on** | M37 Catalogue · M11 Pricing · M33 Party Master · M17 Asset Registry · M24 Document · M29 Identity · M28 Integration |
| **Depended on by** | M01, M08, M09, M13, M14, M20, M38, M04, M05, M53, M07, M25, M39 |

---

## 2. Purpose

M36 owns the **offer**: the document that states what 1000FiX will do for a specific customer,
for a specific amount, under specific terms, valid until a specific date — and the record of
what that customer decided.

It spans the full range of offer types the business needs: a two-line counter estimate for a
cracked screen, a three-page corporate AMC proposal, and a formal competitive tender response
to a government e-GP notice. These are the same object with different rigour, not three
different systems.

It is also the **legal boundary between conversation and commitment**. Before a quotation is
accepted, everything is discussion. After acceptance, a priced scope exists that flows
unchanged into a work order, a contract or an invoice. Almost every customer dispute in a
service business originates in the gap between what was said and what was billed; M36 closes
that gap by making the accepted quotation the single source of the commercial scope.

### Why It Exists

Today an estimate is a verbal figure or a handwritten note. There is no version control, so a
revised estimate replaces the original with no trace. There is no expiry, so a three-month-old
figure is still quoted. There is no record of customer approval, so disputes are unwinnable.
There is no measurement of conversion, so nobody knows how much work is lost at the estimate
stage or why.

The v1.0 plan folded quotation into a general sales module. Benchmarking against CPQ practice
and against SAP/Oracle quotation objects showed that the quotation needs its own lifecycle,
its own versioning, its own approval loop and its own legal weight. M36 was created to hold
them.

The category KPIs are explicit: **quotation-to-order conversion > 78%**, **average quotation
turnaround < 2 hours**. Neither is measurable today.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.1 (BR-SRM-006, 011, 012) | Estimate request, customer approval loop, approval thresholds |
| ERP BRD §8.11 (BR-SLS-*) | Quotation creation, versioning, validity and conversion |
| ERP BRD §10.1 BRU-SRM-07, 08, 13 | Approval above BDT 5,000 and BDT 25,000; an expired estimate is re-issued, never extended |
| ERP URD §6, §7 (US-SRM-*, US-SLS-*) | Agent, technician and account manager estimate stories |
| `05-04` §7 Approval Authority Matrix | Estimate approval thresholds by value band |
| M01 §5.3 FR-SRM-025…030 | M01 requests an estimate from M36 and displays the returned quotation |
| Business Plan §Corporate Segment, §Government Contracts | Tender and competitive bidding as a required capability |
| Service App SOW §Estimate Approval | "The customer will approve or reject the estimate from the app; the decision will push to ERP" |
| `_CATEGORY_OVERVIEW.md` §3, §10 | The commercial chain position and the "estimates diverge from invoice" risk |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The estimate object: diagnostic-driven, technical, internal-facing build-up of what a job requires |
| 2 | The quotation object: the customer-facing, priced, versioned, legally weighted offer |
| 3 | Estimate build-up from M37 (fault → operation → rBOM → SRT) and M11 (prices) |
| 4 | Manual line entry, non-catalogue lines and free-text lines with governance |
| 5 | Quotation versioning, revision, comparison and supersession |
| 6 | Validity periods, expiry, reminder sequences and re-issue |
| 7 | Internal approval routing by value, margin, discount, terms and customer risk |
| 8 | Customer approval loop across channels: portal, app, WhatsApp, SMS link, email, counter, on-site, phone-with-recording |
| 9 | Partial acceptance, line-level accept/decline and counter-offer handling |
| 10 | E-signature capture and the evidence pack that proves acceptance |
| 11 | Declined-quotation handling: reasons, diagnostic fee, return/collection trigger, follow-up |
| 12 | Multi-option quotations ("good / better / best") and alternative-line presentation |
| 13 | Corporate and multi-site quotations with per-site and per-department breakdown |
| 14 | Bulk and estate quotations from a corporate asset upload |
| 15 | Contract and subscription proposals (handing the accepted scope to M08 / M39) |
| 16 | Renewal quotations generated from expiring contracts |
| 17 | **Tender and competitive bid management**: opportunity capture, compliance matrix, document assembly, bid bond tracking, submission record, outcome |
| 18 | Competitive-bid pricing strategy support: cost build-up, target margin, bid/no-bid decision record |
| 19 | Quotation templates, standard terms, exclusions and assumptions libraries |
| 20 | Quotation document generation in Bengali and English, branded, with itemisation control |
| 21 | Cost visibility and margin display to authorised roles at quotation time |
| 22 | Conversion tracking, win/loss reasons and quotation analytics |
| 23 | The quotation API and the events by which M01, M08, M39 and M20 consume an accepted offer |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Price calculation, discount authority, margin floors | **M11** Pricing | M36 asks for a price and displays it; it never computes one |
| Item definitions, rBOM, standard repair times, fault taxonomy | **M37** Catalogue | M36 selects from the catalogue; it does not define it |
| The service order, its lifecycle and its execution | **M01** SRM | M01 is the operational record; M36 is the commercial one |
| Diagnosis itself — the technical finding | **M01** SRM | M36 consumes the diagnostic result; it does not perform diagnosis |
| Contract terms, entitlements, amendments, renewal execution | **M08** Contract | M36 produces the offer; M08 creates the agreement |
| Recurring billing mechanics | **M39** Subscription | M36 quotes the plan; M39 bills it |
| Invoice, credit note, collection | **M20** Receivable | Only Category G creates financial documents |
| Opportunity, pipeline, forecast and account plan | **M07** CRM | The opportunity precedes and contains the quotation |
| Customer identity, credit limit and consent | **M33** Party Master | Referenced, never edited |
| Document storage, retention and e-signature infrastructure | **M24** Document | M36 uses the service; it does not build it |
| Marketplace seller bids on a job | **M12** Marketplace | A seller bid is a marketplace transaction with its own rules |
| Procurement RFQ to suppliers | **M16** Procurement | Buying, not selling |
| Rental agreement terms | **M13** Rental | M36 quotes the rental; M13 owns the hire agreement |

### 3.3 Shared Concepts

| Concept | M36's Role | Owning Module |
|---|---|---|
| Estimate | **Owner** | M36 |
| Quotation | **Owner** | M36 |
| Price | Requests and displays; stores the locked value | M11 |
| Catalogue item / operation / rBOM / SRT | Consumes | M37 |
| Diagnostic result | Consumes as estimate input | M01 |
| Service order | Referenced; created or updated on acceptance | M01 |
| Contract | Produced from an accepted proposal | M08 |
| Opportunity | Referenced as parent | M07 |
| E-signature | Requests from the platform service | M24 |
| Approval authority | Applies M11's discount bands and `05-04` §7 value bands | M11 / M29 |
| Customer decision | **Owner** of the record; M01 and M27 react to it | M36 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA Sales** — Quotation (document type QT), item categories, reference document flow | A quotation as a formal sales document with validity, reasons for rejection and document flow into the order | **Document flow** — the accepted quotation is referenced by the order and the invoice, giving end-to-end traceability from offer to cash | SAP's document-type proliferation |
| **SAP S/4HANA Service** — Service Quotation | Quotation for service items with planned parts and planned labour | The **planned-parts + planned-labour** structure, which maps exactly to rBOM + SRT | — |
| **Oracle CPQ / Oracle Quoting** | Guided selling, configuration, approval sequences, proposal generation, quote versioning | **Guided estimate build-up** from fault code, and **multi-level approval sequences** with parallel and serial steps | Oracle's product-configurator depth; our configuration lives in M37 bundles |
| **Salesforce CPQ** — Quote lines, quote templates, amendment and renewal quotes | Renewal and amendment quotes generated automatically from existing contracts | **Renewal quotation generation from expiring contracts** — the mechanism behind the AMC renewal-rate target | Salesforce-specific quote-line-group modelling |
| **Microsoft Dynamics 365 Sales** — Quote → Order → Invoice | Simple, legible progression with revision numbering | The **revision numbering** convention customers can follow (Q-00123 v3) | — |
| **IFS Cloud** — Service quotation with cost build-up | Estimate as an internal cost build-up distinct from the customer quotation | **The estimate/quotation split** — an internal technical build-up and a customer-facing offer derived from it. This is the core structural decision of M36 | IFS's project-costing depth |
| **DealHub / Conga / PandaDoc class** | Digital proposal delivery, tracking (opened/viewed), e-signature, interactive acceptance | **Tracked digital delivery with view analytics and one-tap acceptance**, adapted to WhatsApp and SMS because that is how Bangladeshi customers actually respond | Full proposal-design studios |
| **Public e-procurement practice** (Bangladesh e-GP, BPPA) | Tender notice, compliance requirements, bid security, sealed submission, evaluation, award | **Compliance matrix, bid-bond tracking, document checklist and submission record** as first-class objects, so a tender is never lost on a missing annexe | Integration into e-GP submission itself — submission remains manual on the portal; M36 records and prepares |

**Design position.** 1000FiX differs from the benchmarks in five ways.

First, **the estimate and the quotation are separate objects**. The estimate is technical and
internal — operations, parts, times, costs, risk. The quotation is commercial and external —
scope, price, terms, validity. One estimate can produce several quotations (options, revisions,
partial scopes). Benchmarks that collapse the two force technicians to think commercially and
agents to think technically; separating them lets each role work in its own language.

Second, **the approval loop is designed for a customer holding a phone, not a laptop**. The
dominant acceptance path is a WhatsApp or SMS link opening a one-screen, Bengali, tap-to-approve
view with photographs of the fault. Email-and-PDF is the exception, not the default.

Third, **partial acceptance is a first-class outcome**, not an edge case. Customers routinely
approve the screen but decline the battery. The system must produce a coherent reduced scope,
re-price it, and hand only the approved part to execution — without a new quotation cycle.

Fourth, **an expired quotation is never extended**. It is re-issued at current prices as a new
version. This is BRU-SRM-13 carried into M36, and it is the control that stops months-old
estimates being honoured at a loss.

Fifth, **tender management is included in the same module rather than bought separately**.
Corporate and government tenders are a stated growth channel; the volume does not justify a
dedicated bid-management product, but the discipline (compliance matrix, bid bond, deadline,
document checklist) is exactly the discipline that decides whether bids are won or disqualified.

---

## 5. Functional Areas & Features

### 5.1 Estimate Build-Up

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-QTE-001 | Estimate creation | Create an estimate from a service order, an opportunity, a corporate asset upload, a contract renewal, a tender, or from scratch | P0 | L5 |
| FR-QTE-002 | Diagnostic-driven pre-population | Build estimate lines automatically from the M01 diagnostic result using the M37 fault → operation → rBOM → SRT chain | P0 | L5 |
| FR-QTE-003 | Line composition | Support labour lines (operation × SRT × rate), part lines (from rBOM or manual), service lines, third-party/sub-contract lines, logistics lines, fee lines and discount lines | P0 | L5 |
| FR-QTE-004 | Non-catalogue lines | Permit a free-text or non-catalogue line with a mandatory description, cost basis and approval, and flag it for catalogue review | P1 | L5 |
| FR-QTE-005 | Cost build-up and margin | Compute cost from M15 standard cost and M56 labour cost basis, display margin per line and in total, and restrict that display to authorised roles | P0 | L5 |
| FR-QTE-006 | Parts availability signal | Show live availability, lead time and alternate options per part line from M15, and mark lines that will delay the promised date | P1 | L5 |
| FR-QTE-007 | Risk and contingency | Allow a declared contingency line or percentage with a reason, visible internally and presented as part of the total externally | P2 | L5 |
| FR-QTE-008 | Estimate templates | Maintain templates for common jobs, corporate scopes and contract proposals, with per-branch and per-segment variants | P1 | L5 |
| FR-QTE-009 | Second-opinion routing | Route a high-value or contentious estimate to a senior technician or specialist for technical review before it becomes a quotation | P2 | L5 |
| FR-QTE-010 | Estimate-to-quotation conversion | Convert an approved estimate into one or more customer quotations, choosing itemisation level and which internal detail is exposed | P0 | L5 |

### 5.2 Quotation Document & Versioning

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-QTE-011 | Quotation numbering | Issue a unique, gapless quotation number with a visible version suffix that customers can quote back | P0 | L1 |
| FR-QTE-012 | Versioning and revision | Create a new version on any change after issue, retain every prior version immutably, and mark exactly one version current | P0 | L2 |
| FR-QTE-013 | Version comparison | Present a side-by-side difference between any two versions, in customer-readable language | P1 | L5 |
| FR-QTE-014 | Validity and expiry | Set a validity period per quotation type, expire automatically, and block acceptance of an expired quotation | P0 | L5 |
| FR-QTE-015 | Re-issue on expiry | Re-issue an expired quotation as a new version at current prices; never extend the original | P0 | L5 |
| FR-QTE-016 | Multi-option quotations | Present two or three priced options (for example economy / standard / premium repair) from which the customer selects exactly one | P1 | L5 |
| FR-QTE-017 | Alternative lines | Offer alternatives within a line (genuine vs OEM vs aftermarket part) with the price and warranty consequence of each shown | P1 | L5 |
| FR-QTE-018 | Terms, assumptions and exclusions | Attach governed standard terms, assumptions and exclusions by quotation type, with controlled deviation requiring legal approval | P0 | L5 |
| FR-QTE-019 | Bilingual document generation | Generate the quotation as a branded document in Bengali or English, with configurable itemisation and an accessible mobile view | P0 | L2 |
| FR-QTE-020 | Attachment and evidence | Attach diagnostic photographs, fault reports, device condition records and reference documents to the customer-facing quotation | P0 | L5 |
| FR-QTE-021 | Corporate breakdown | Break a quotation down by site, department, cost centre and asset for corporate customers, with subtotals per dimension | P1 | L5 |
| FR-QTE-022 | Bulk estate quotation | Generate a quotation covering hundreds of assets from a corporate upload, with per-asset lines and roll-up | P1 | L5 |
| FR-QTE-023 | Contract and subscription proposal | Produce a proposal for an AMC, protection plan, managed service or subscription, carrying the scope, entitlements and term that M08/M39 will instantiate | P0 | L5 |
| FR-QTE-024 | Renewal quotation | Generate a renewal quotation automatically from an expiring contract, with the prior term's actual consumption and any escalation applied | P1 | L5 |

### 5.3 Internal Approval

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-QTE-025 | Value-band approval | Enforce the approval authority matrix by quotation value — including the > BDT 25,000 branch manager and > BDT 100,000 Operations Director thresholds | P0 | L5 |
| FR-QTE-026 | Margin and discount approval | Route for approval any quotation breaching the M11 discount band or margin floor, and block issue until decided | P0 | L5 |
| FR-QTE-027 | Terms deviation approval | Require CCO and CFO approval for any non-standard commercial term, per the approval authority matrix | P0 | L5 |
| FR-QTE-028 | Credit and risk gating | Block issue or acceptance where M33 reports the customer over their credit limit or on a hold list, unless overridden by Finance | P1 | L5 |
| FR-QTE-029 | Parallel and serial approval | Support both parallel approvals (finance and legal simultaneously) and serial chains, with a visible progress state | P1 | L5 |
| FR-QTE-030 | Approval SLA and escalation | Escalate an undecided approval after a configured interval, and report approval cycle time | P1 | L5 |
| FR-QTE-031 | Mobile approval | Allow an approver to review the full quotation and decide from a phone | P1 | L5 |
| FR-QTE-032 | Approval audit | Record every approval and rejection with actor, timestamp, reason and the exact document version approved | P0 | L5 |

### 5.4 Customer Approval Loop

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-QTE-033 | Multi-channel delivery | Deliver the quotation via customer portal, mobile app, WhatsApp, SMS link, email, printed counter copy or on-site technician device, per the customer's preference | P0 | L5 |
| FR-QTE-034 | One-screen mobile acceptance | Present a Bengali, single-screen, tap-to-approve view carrying the price, scope, photographs and terms, usable on a 3G connection | P0 | L5 |
| FR-QTE-035 | Accept / decline / part-accept | Record acceptance, decline or line-level partial acceptance, and produce a coherent, re-priced approved scope in every case | P0 | L5 |
| FR-QTE-036 | Counter-offer capture | Record a customer counter-proposal as a structured request that routes to the appropriate authority rather than a phone conversation | P2 | L5 |
| FR-QTE-037 | E-signature | Capture an electronic signature or OTP-verified acceptance through M24, and store the signed artefact immutably | P0 | L5 |
| FR-QTE-038 | Acceptance evidence pack | Assemble the accepted version, the acceptance method, timestamp, IP or device, signature and delivery proof as one retrievable evidence pack | P0 | L5 |
| FR-QTE-039 | Delivery and view tracking | Record delivery, first view and repeat views, and surface unviewed quotations for follow-up | P1 | L5 |
| FR-QTE-040 | Reminder sequence | Send reminders at configured intervals before expiry, through the customer's preferred channel, and stop on decision | P1 | L5 |
| FR-QTE-041 | Decline handling | On decline, capture a reason from a governed list, raise the diagnostic fee where applicable, and trigger the return or collection task in M01/M03 | P0 | L5 |
| FR-QTE-042 | Phone acceptance with evidence | Permit acceptance recorded by an agent on a call, requiring a recorded consent reference or an OTP sent to the customer | P1 | L5 |

### 5.5 Tender & Competitive Bid Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-QTE-043 | Tender opportunity register | Register a tender or RFP with issuer, reference, scope, submission deadline, method, contact and source (including e-GP notices) | P1 | L5 |
| FR-QTE-044 | Bid/no-bid decision | Record a structured bid/no-bid decision with scoring on fit, capacity, competition, margin and risk, and the deciding authority | P1 | L5 |
| FR-QTE-045 | Compliance matrix | Maintain a requirement-by-requirement compliance matrix with owner, response, evidence document and completion state, and block submission while any mandatory item is open | P1 | L5 |
| FR-QTE-046 | Document checklist and assembly | Track every required annexe, certificate and form, assemble the submission pack, and version it | P1 | L5 |
| FR-QTE-047 | Bid security and guarantee tracking | Record bid bonds, performance guarantees and their issuing bank, value, validity and release, with expiry alerting | P1 | L5 |
| FR-QTE-048 | Tender outcome and win/loss analysis | Record the outcome, awarded party, winning price where disclosed, and structured loss reasons, and report win rate by issuer, sector and value band | P1 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Immutable versions** | An issued quotation version is immutable. Any change produces a new version; the prior version is never mutated or deleted |
| T-02 | **Price lock integrity** | Every issued line carries an M11 price lock with its rule-set version; the total is recomputed from locked lines only, never re-resolved |
| T-03 | **Deterministic partial acceptance** | Partial acceptance recomputes the approved scope deterministically, honouring bundle integrity and dependency rules, and produces a new derived version |
| T-04 | **Idempotent acceptance** | A customer tapping "approve" twice, or a webhook redelivering, produces exactly one acceptance |
| T-05 | **Tokenised public access** | The customer-facing approval view is served by a single-use, expiring, signed token; it exposes no cost, margin, internal note or other customer's data |
| T-06 | **Offline quotation on the technician app** | A technician can build, present and capture acceptance for an on-site quotation offline, with idempotent replay on reconnection |
| T-07 | **Document generation isolation** | PDF and print generation runs asynchronously; a rendering failure never blocks issue or acceptance |
| T-08 | **Evidence immutability** | The acceptance evidence pack is written once, hashed, and stored through M24 with retention policy applied |
| T-09 | **Approval as state** | Approval is a document state that blocks issue, not a notification. The state machine, not the inbox, is authoritative |
| T-10 | **Bulk estate performance** | A 500-asset corporate quotation prices, renders and issues within 60 seconds |
| T-11 | **Event exactly-once** | `quotation.decided` is emitted through the transactional outbox exactly once, even under retry, because M01, M08 and M20 all act on it |
| T-12 | **Localisation** | Bengali is complete for the customer surface including numerals, currency and date formats; the acceptance screen is under 250 KB first load |
| T-13 | **Concurrency** | Two agents editing the same estimate produce a detectable conflict, never a silent overwrite |
| T-14 | **Retention and legal hold** | Quotations are retained per the records schedule; a quotation under dispute is placed on legal hold and excluded from purge |
| T-15 | **Performance envelope** | Estimate pre-population ≤ 1.5 s p95 · quotation issue ≤ 2 s p95 · customer acceptance screen first render ≤ 3 s on 3G |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M36 |
|---|---|---|
| **Technician** | Phones the branch with a verbal figure | Builds the estimate on the phone from the diagnosis, with parts and times pre-filled |
| **Service centre agent** | Writes a number on a job card; re-explains it three times | Issues a quotation to the customer's phone in minutes and sees when it is viewed |
| **Branch manager** | Approves by nodding | Approves in the system, on a phone, with the margin visible |
| **Account manager** | Rebuilds every corporate proposal in Word; renewal season is chaos | Uses templates; renewal quotations are generated automatically from expiring contracts |
| **Bid coordinator** | Assembles tender packs by hand and discovers a missing annexe at the deadline | Works from a compliance matrix that will not let the pack be submitted incomplete |
| **Finance officer** | Reconciles invoices to a scope nobody wrote down | Invoices against an accepted quotation; variance requires a documented reason |
| **Customer** | Is told a price, forgets it, disputes the bill | Holds a link showing exactly what they approved, when, and for how much |
| **CCO** | Has no idea how much work is lost at estimate stage | Sees conversion, turnaround and loss reasons by branch, segment and value band |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Quotation-to-order conversion** | Fast turnaround, mobile one-tap acceptance, reminders before expiry, option-based quotes | Conversion from unmeasured to **> 78%** *(category KPI)* |
| **Quotation turnaround** | Diagnostic-driven pre-population removes the blank-page estimate | Average turnaround to **< 2 hours** *(category KPI)* |
| **Dispute reduction and revenue protection** | Signed acceptance evidence pack; invoice raised against the accepted scope | Directly supports the **revenue leakage < 0.5%** target and reduces write-offs from disputed billing |
| **Margin protection at the offer stage** | Margin visible at quotation; discount and floor breaches blocked before issue rather than discovered after | Contributes to the **+4 pt gross-margin** target owned by M11 |
| **AMC / RAMC renewal uplift** | Automatic renewal quotations issued at the right lead time with consumption evidence attached | A principal mechanism behind the **BDT 72 lac/year** renewal benefit and the **60% → 88%** renewal-rate target owned by M08 |
| **Corporate and tender win rate** | Compliance matrices and document checklists prevent disqualification; win/loss analysis improves pricing strategy | Enables the corporate and government growth assumed in the business plan; baseline to be established in W3 |
| **Administrative saving** | No re-typing between estimate, quotation, order and invoice | Part of the **BDT 62 lac/year** administrative labour saving |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Legal defensibility** | A signed, versioned, timestamped acceptance is admissible evidence. Verbal agreement is not |
| **Trust and transparency** | Customers see the fault photograph, the scope and the price in one place before they commit. This is the single most visible difference from the current experience |
| **Consistency across 51+ branches** | The same fault produces the same offer wherever the customer walks in |
| **Commercial memory** | Loss reasons accumulate into evidence about why work is lost — a dataset the company has never had |
| **Professional credibility with corporates** | A structured, bilingual, itemised proposal is a precondition for competing for institutional business |
| **ISO 9001 traceability** | Contract review — establishing that requirements are defined and agreed before delivery — is a clause requirement. M36 is the evidence |
| **Model-ready data** | Conversion, price position and loss reason feed M26 win-probability and pricing-guidance models |

---

## 8. Lifecycle & State Model

M36 owns two related lifecycles: the **estimate** and the **quotation**.

### 8.1 Estimate

```
   DRAFT ──► IN BUILD ──► TECHNICAL REVIEW (optional) ──► READY
                                │                          │
                                └── returned ──────────────┘
   READY ──► CONVERTED (one or more quotations created)
   Any ──► ABANDONED (reason recorded)
```

### 8.2 Quotation

```
                 ┌─────────┐
                 │  DRAFT  │ built from an estimate or from scratch
                 └────┬────┘
                      │ submit
                 ┌────▼──────────────┐
                 │ PENDING APPROVAL  │──── rejected ──► DRAFT (reason)
                 └────┬──────────────┘
                      │ internally approved
                 ┌────▼────┐
                 │ APPROVED│ (not yet seen by the customer)
                 └────┬────┘
                      │ issue (price locked, document generated, delivered)
                 ┌────▼────┐
        ┌───────►│ ISSUED  │◄──── re-issue as a new version
        │        └────┬────┘
        │             │
        │      ┌──────┼───────────────┬────────────────┐
        │      │      │               │                │
        │      ▼      ▼               ▼                ▼
        │  ┌───────┐ ┌──────────┐ ┌──────────┐  ┌──────────┐
        │  │VIEWED │ │ ACCEPTED │ │ PARTIALLY│  │ DECLINED │
        │  └───┬───┘ └────┬─────┘ │ ACCEPTED │  └────┬─────┘
        │      │          │       └────┬─────┘       │
        │      │          │            │             │ diagnostic fee,
        │      │          │            │             │ return task
        │      │          ▼            ▼             ▼
        │      │      ┌──────────────────────┐  ┌──────────┐
        │      │      │      CONVERTED       │  │  CLOSED  │
        │      │      │ (order / contract /  │  └──────────┘
        │      │      │  subscription made)  │
        │      │      └──────────────────────┘
        │      │
        │      │ validity elapsed with no decision
        │      ▼
        │  ┌─────────┐
        └──│ EXPIRED │  never extended — re-issue only (BRU-QTE-04)
           └─────────┘

   Terminal: CANCELLED (withdrawn by 1000FiX, reason recorded) · SUPERSEDED (by a later version)
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Draft | Pending Approval | All lines priced with valid M11 locks; mandatory terms attached; customer identified | Agent, technician, account manager |
| Pending Approval | Approved | All required approvals obtained per value, margin, discount and terms bands; approver ≠ author | Band-holding roles |
| Approved | Issued | Price lock valid; document generated; delivery channel confirmed; credit gate passed | Agent, system |
| Issued | Viewed | Customer opens the tokenised view | Customer |
| Issued / Viewed | Accepted | Decision recorded with signature, OTP or recorded consent; within validity | Customer |
| Issued / Viewed | Partially Accepted | Line-level decisions recorded; residual scope re-priced and coherent | Customer |
| Issued / Viewed | Declined | Reason recorded from the governed list | Customer, agent |
| Issued / Viewed | Expired | Validity elapsed without a decision | System |
| Expired | Issued *(new version)* | Re-issued at current prices; never an extension of the original | Agent |
| Accepted / Partially Accepted | Converted | Downstream object created — service order scope, contract, subscription or sales order | System |
| Any pre-decision | Cancelled | Withdrawal reason recorded | Agent with authority |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-QTE-01 | A quotation cannot be issued unless every line carries a valid M11 price lock | **H** | CCO |
| BRU-QTE-02 | An issued quotation version is immutable; any change creates a new version | **H** | CCO |
| BRU-QTE-03 | Acceptance is impossible after expiry | **H** | CCO |
| BRU-QTE-04 | An expired quotation is re-issued at current prices, never extended *(carried from BRU-SRM-13)* | **H** | CCO |
| BRU-QTE-05 | Work above BDT 5,000 cannot begin without recorded customer approval *(BRU-SRM-07)* | **H** | Ops Director |
| BRU-QTE-06 | Quotations above BDT 25,000 require customer approval and Branch Manager approval *(BRU-SRM-08)* | **H** | Ops Director |
| BRU-QTE-07 | Quotations above BDT 100,000 require Operations Director approval *(`05-04` §7)* | **H** | Ops Director |
| BRU-QTE-08 | Non-standard commercial terms require CCO and CFO approval | **H** | CFO |
| BRU-QTE-09 | The author of a quotation cannot approve it | **H** | CCO |
| BRU-QTE-10 | The invoice raised against an accepted quotation must match its approved scope; any variance requires a documented reason and re-approval | **H** | CFO |
| BRU-QTE-11 | Partial acceptance produces a coherent scope; bundle and dependency integrity is preserved or the customer is asked to re-decide | **C** | CCO |
| BRU-QTE-12 | A declined quotation triggers the diagnostic fee where the fee policy applies, and a return or collection task | **C** | Ops Director |
| BRU-QTE-13 | Cost and margin are never exposed on any customer-facing quotation surface | **H** | CFO |
| BRU-QTE-14 | A quotation cannot be issued to a customer over their credit limit or on hold without Finance override | **H** | CFO |
| BRU-QTE-15 | A tender submission cannot be marked submitted while a mandatory compliance item or document is outstanding | **H** | CCO |
| BRU-QTE-16 | Every declined or lost quotation records a reason from the governed list | **H** | CCO |
| BRU-QTE-17 | A quotation under dispute is placed on legal hold and cannot be purged | **H** | Quality Manager |
| BRU-QTE-18 | A renewal quotation is issued no later than the contract's configured renewal lead time | **C** | CCO |

*Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.estimate` | `fix_estimate` | Internal technical build-up | name, source_type, service_order_id, opportunity_id, partner_id, asset_ids, state, total_cost, total_price, margin_pct, created_by |
| `fix.estimate.line` | `fix_estimate_line` | Estimate lines | estimate_id, line_type, item_id, operation_id, qty, uom_id, srt_minutes, unit_cost, unit_price, price_lock_id, availability_state |
| `fix.quotation` | `fix_quotation` | The customer-facing offer | name, version, estimate_id, partner_id, contact_id, currency_id, valid_until, state, total, delivery_channel, template_id, language, parent_version_id |
| `fix.quotation.line` | `fix_quotation_line` | Quotation lines | quotation_id, sequence, item_id, description_bn, description_en, qty, unit_price, price_lock_id, option_group, alternative_group, accepted |
| `fix.quotation.option` | `fix_quotation_option` | Good/better/best option sets | quotation_id, code, label_bn, label_en, total, recommended |
| `fix.quotation.term` | `fix_quotation_term` | Terms, assumptions, exclusions | quotation_id, term_type, text_bn, text_en, is_standard, deviation_approval_id |
| `fix.quotation.approval` | `fix_quotation_approval` | Internal approval steps | quotation_id, version, step, role_id, mode (serial/parallel), state, actor_id, reason, decided_at |
| `fix.quotation.delivery` | `fix_quotation_delivery` | Delivery and view tracking | quotation_id, channel, sent_at, delivered_at, first_viewed_at, view_count, token_id |
| `fix.quotation.decision` | `fix_quotation_decision` | Customer decision record | quotation_id, version, decision, decided_at, method, actor_ref, signature_id, otp_ref, ip_or_device, reason_code |
| `fix.quotation.evidence` | `fix_quotation_evidence` | Immutable acceptance pack | quotation_id, version, content_hash, document_id, sealed_at |
| `fix.quotation.template` | `fix_quotation_template` | Templates | code, quotation_type, segment_id, branch_group_id, line_defaults_json, terms_ids, language |
| `fix.decline.reason` | `fix_decline_reason` | Governed decline / loss reasons | code, description_bn, description_en, category, triggers_fee |
| `fix.tender` | `fix_tender` | Tender opportunity | reference, issuer_id, source, scope, deadline_at, method, estimated_value, bid_decision, decision_by, state |
| `fix.tender.requirement` | `fix_tender_requirement` | Compliance matrix | tender_id, clause_ref, requirement, mandatory, owner_id, response, evidence_document_id, state |
| `fix.tender.document` | `fix_tender_document` | Submission checklist | tender_id, document_type, required, document_id, state, version |
| `fix.bid.security` | `fix_bid_security` | Bid bonds and guarantees | tender_id, type, bank_id, value, currency_id, issued_at, valid_until, released_at, state |
| `fix.tender.outcome` | `fix_tender_outcome` | Outcome and loss analysis | tender_id, result, awarded_to, winning_value, our_value, loss_reason_code, notes |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.catalogue.item`, `fix.repair.operation`, `fix.repair.bom`, `fix.standard.repair.time` | M37 | Master data projection |
| `fix.price.lock`, pricing resolution and explanation | M11 | REST; lock stored by reference |
| `fix.party`, contact, credit status, segment, tier | M33 | Live read |
| `fix.asset` | M17 / M49 | Live read |
| `fix.service.order`, `fix.diagnostic.result` | M01 | Live read; writes decision events back |
| `fix.contract` (for renewal source) | M08 | Live read |
| `fix.stock.quant`, `fix.stock.valuation.event` | M15 | Live read |
| `fix.document`, e-signature service | M24 | Service call |
| `fix.opportunity` | M07 | Live read; writes outcome back |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-QTE-01 | Diagnostic result recorded in M01 | Create a draft estimate pre-populated from fault → operation → rBOM → SRT with prices from M11 | Create an empty estimate and notify the agent |
| AUT-QTE-02 | Estimate marked ready | Evaluate approval requirements by value, margin, discount and terms; route accordingly | Hold in Pending Approval and escalate |
| AUT-QTE-03 | Quotation issued | Lock prices, generate the document, deliver on the preferred channel, start the validity clock and the reminder sequence | Retry delivery on the fallback channel; alert the agent after two failures |
| AUT-QTE-04 | Quotation unviewed after 24 h | Re-send on the fallback channel and create a follow-up task | Escalate to the branch manager |
| AUT-QTE-05 | Approaching expiry (T−48 h, T−24 h) | Send reminders on the customer's preferred channel | Log; continue the sequence |
| AUT-QTE-06 | Validity elapsed | Expire the quotation, release the price locks, notify the owner, and offer one-click re-issue | — |
| AUT-QTE-07 | Customer accepts | Seal the evidence pack, emit `quotation.decided`, release the approved scope to M01/M08/M39, and notify the assignee | Retry event delivery; create a manual release task after exhaustion |
| AUT-QTE-08 | Customer partially accepts | Recompute the approved scope, re-price, produce a derived version, and release only the approved part | Route to the agent for manual confirmation |
| AUT-QTE-09 | Customer declines | Record the reason, raise the diagnostic fee where applicable, and create the return or collection task in M01/M03 | Create a manual follow-up task |
| AUT-QTE-10 | Contract approaching expiry (M08 event) | Generate a renewal quotation with prior consumption and escalation applied, and assign it to the account manager | Create a manual renewal task |
| AUT-QTE-11 | Approval SLA elapsed | Escalate to the next authority and notify both parties | Repeat escalation; log |
| AUT-QTE-12 | Non-catalogue line used | Flag the line for M37 catalogue review after issue | Log |
| AUT-QTE-13 | Tender deadline approaching (T−7 d, T−3 d, T−1 d) | Alert the bid owner with the outstanding compliance and document list | Escalate to CCO |
| AUT-QTE-14 | Bid security approaching expiry | Alert Finance to extend or recover the guarantee | Escalate to CFO |
| AUT-QTE-15 | Invoice raised in M20 differs from the accepted scope | Flag the variance, require a documented reason and re-approval before the invoice is issued | Block the invoice; escalate to Finance Manager |

---

## 12. Interfaces

### 12.1 Upstream — M36 Consumes

| Source | What | Mechanism |
|---|---|---|
| M01 SRM | Service order context, diagnostic result, fault codes, device condition and photographs | Event `service_order.diagnosed` + REST |
| M37 Catalogue | Items, operations, rBOM, SRT, fault→operation mapping, contract and protection templates | Master data projection |
| M11 Pricing | Line prices with explanation, discount evaluation, margin, price locks | REST `POST /api/v1/pricing/resolve`, `/lock` |
| M33 Party Master | Customer, contact, segment, tier, credit status, language and channel preference | Live read |
| M17 Asset Registry | Device identity, specification and history | Live read |
| M15 Inventory | Standard cost and live availability with lead time | Live read |
| M08 Contract | Expiring contracts and prior-term consumption for renewal quotations | Event `contract.renewal_due` + REST |
| M07 CRM | Opportunity context for corporate and tender quotations | Live read |
| M24 Document | Templates, generated documents, e-signature and retention | Service call |
| M10 Loyalty | Applicable member benefits (applied via M11) | Indirect, through M11 |

### 12.2 Downstream — M36 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 SRM | Approved scope, approval status and decision, releasing work to execution | Event `quotation.decided` + REST |
| M08 Contract | Accepted contract proposal — scope, entitlements, term, pricing | Event `quotation.accepted` (type = contract) |
| M39 Subscription | Accepted subscription proposal — plan, term, commitment | Event `quotation.accepted` (type = subscription) |
| M09 Warranty | Accepted protection product sale | Event `quotation.accepted` (type = protection) |
| M13 Rental · M14 Refurbishment | Accepted rental or resale offer | Event |
| M20 Receivable | The accepted commercial scope against which the invoice must reconcile | Event + REST |
| M15 Inventory | Parts demand signal on acceptance for reservation | Command via M01 |
| M11 Pricing | Quotation outcomes for win/loss and elasticity analysis | Event `quotation.decided` |
| M07 CRM | Opportunity stage and value updates | Event |
| M27 Contact Centre | Customer-facing delivery, reminder and decision events | Events |
| M25 BID · M26 AIM | Full quotation fact stream: build-up, approval, delivery, view, decision, reason | Warehouse extract |
| P01 / P04 / P02 | Customer approval surfaces and technician on-site quoting | REST via M28 |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `estimate.created` | estimate id, source, service order, total | M01, M25 |
| `estimate.ready` | estimate id, total cost, total price, margin | M11, M25 |
| `quotation.issued` | quotation id, version, customer, total, valid_until, channel | M01, M27, M25 |
| `quotation.delivered` | quotation id, channel, delivered_at | M27 |
| `quotation.viewed` | quotation id, first view, view count | M27, M25 |
| `quotation.decided` | quotation id, version, decision, approved scope, evidence ref | M01, M08, M39, M09, M20, M11, M07 |
| `quotation.accepted` | quotation id, type, approved lines, total, signature ref | M08, M39, M09, M13, M14, M20 |
| `quotation.declined` | quotation id, reason code, fee applicable | M01, M03, M27, M25 |
| `quotation.expired` | quotation id, version, elapsed value | M01, M27, M25 |
| `quotation.superseded` | old version, new version | M01, M20 |
| `tender.registered` | tender id, issuer, deadline, estimated value | M07, M25 |
| `tender.submitted` | tender id, submission pack ref, our value | M07, M25 |
| `tender.outcome_recorded` | tender id, result, loss reason | M07, M11, M25 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-QTE-01 | WhatsApp Business API | Outbound | Quotation delivery and one-tap approval link |
| INT-QTE-02 | SMS gateway | Outbound | Quotation link, OTP acceptance, reminders |
| INT-QTE-03 | Email service | Bidirectional | Quotation delivery and reply capture |
| INT-QTE-04 | E-signature provider *(via M24, L6)* | Bidirectional | Qualified electronic signature on high-value quotations |
| INT-QTE-05 | Bangladesh e-GP portal (`eprocure.gov.bd`) | Inbound, manual-assisted | Tender notice capture and submission-status recording — submission itself remains on the portal |
| INT-QTE-06 | Bank guarantee issuance | Manual/document | Bid bond and performance guarantee tracking |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/estimates` | POST | Create an estimate, optionally from a service order | M01, P02, P03 |
| `/api/v1/estimates/{id}/populate` | POST | Pre-populate from diagnosis via M37/M11 | P02, P03 |
| `/api/v1/quotations` | POST | Create a quotation from an estimate | P03, P02, P04 |
| `/api/v1/quotations/{id}` | GET | Full quotation, authorisation-scoped | All portals |
| `/api/v1/quotations/{id}/issue` | POST | Lock prices, generate and deliver | P03, P02 |
| `/api/v1/quotations/{id}/versions` | GET | Version list and comparison | P03, P04 |
| `/api/v1/quotations/{id}/approve` | POST | Internal approval decision | P03, mobile |
| `/api/v1/quotations/{id}/decision` | POST | Customer decision (accept / part-accept / decline) | P01, P04, P02, P10 |
| `/api/v1/quotations/{id}/evidence` | GET | Retrieve the sealed acceptance evidence pack | P03, dispute handling |
| `/api/v1/public/quotations/{token}` | GET | Tokenised customer view | Unauthenticated customer |
| `/api/v1/public/quotations/{token}/decision` | POST | Tokenised customer decision with OTP or signature | Unauthenticated customer |
| `/api/v1/quotations/bulk` | POST | Bulk estate quotation from an asset upload | P04 |
| `/api/v1/tenders` | GET/POST | Tender register and compliance matrix | P03 |
| `/api/v1/quotations/analytics` | GET | Conversion, turnaround and loss-reason analytics | P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R04 Chief Commercial Officer | C R U D A | All |
| R21 Sales Manager | C R U A | Assigned segment |
| R22 Account Manager (Corporate) | C R U | Assigned accounts |
| R05 Operations Director | R A | All — > BDT 100,000 authority |
| R06 Branch Manager | C R U A | Own branch — > BDT 25,000 authority |
| R08 Service Centre Agent | C R U | Own branch |
| R10 / R11 / R12 Technician | C R U | Own assigned jobs — on-site estimate and quotation |
| R09 Workshop Supervisor | C R U | Own workshop |
| R34 Contact Centre Agent | C R U | Customer-facing scope |
| R26 Finance Manager | R A | All — credit gate, terms deviation |
| R03 Chief Financial Officer | R A | All — non-standard terms |
| R27 Finance Officer | R | Billing reconciliation scope |
| R32 Quality Manager / ISO Coordinator | R | All — dispute and legal hold |
| R36 Customer | R, decide | Own quotations only |
| R37 Corporate Portal User | R, decide | Own company; within delegated authority |
| R38 External Party | – | No access |
| — Bid Coordinator *(new position under R04)* | C R U | Tender register, compliance matrix, document pack |

**Field-level restrictions.** `unit_cost`, `total_cost` and `margin` are visible only to
R01–R06, R17, R21, R22, R26 and R27 *(`05-04` §5)*. The customer-facing view and every external
API response exclude cost, margin, internal notes and supplier identity absolutely.

**Segregation of duties.** The author of a quotation cannot approve it (BRU-QTE-09). A user who
approves a quotation above their band cannot also release the resulting invoice — this
interacts with SOD-04 and is jointly enforced with M20.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Quotation conversion funnel | CCO, Sales Manager, Branch Managers | Weekly | Issued → viewed → decided → accepted → converted, by branch, segment, value band and channel |
| Quotation turnaround | Ops Director, CCO | Daily | Diagnosis-to-issue and issue-to-decision elapsed time, with outliers |
| Loss reason analysis | CCO, Sales Manager | Monthly | Decline and loss reasons ranked, by branch, segment, device category and value band |
| Open quotation pipeline | Account Managers, Branch Managers | Real time | Issued and unexpired quotations by value, age and days to expiry |
| Expiry watchlist | Agents, Branch Managers | Daily | Quotations expiring in 48 hours with no decision |
| Approval cycle time | CCO, Ops Director | Weekly | Time in each approval step by band and approver, with escalations |
| Estimate accuracy | Ops Director, Quality Manager | Monthly | Estimated vs actual cost and duration, by operation and technician |
| Quotation-to-invoice variance | CFO, Finance Manager | Monthly | Accepted scope vs invoiced value, with reasons |
| Renewal quotation performance | CCO, Account Managers | Monthly | Renewal quotations issued, accepted, lapsed and lost, by contract family |
| Tender pipeline and win rate | CCO, CEO | Monthly | Bids registered, submitted, won, lost, disqualified; win rate by issuer and value band |
| Bid security exposure | CFO | Monthly | Outstanding bid bonds and guarantees by value and expiry |
| Channel effectiveness | CCO, CTO | Monthly | Acceptance rate and time-to-decision by delivery channel |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| KPI-C36-01 | Quotation-to-order conversion | unmeasured | 72% | **> 78%** |
| KPI-C36-02 | Average quotation turnaround (diagnosis → issue) | unmeasured | < 4 h | **< 2 h** |
| KPI-C36-03 | Median time from issue to customer decision | unmeasured | < 24 h | **< 8 h** |
| KPI-C36-04 | Quotations accepted on a mobile surface | 0% | 60% | **> 80%** |
| KPI-C36-05 | Quotations with a complete acceptance evidence pack | 0% | 100% | **100%** |
| KPI-C36-06 | Quotation-to-invoice variance | unmeasured | < 5% | **< 1.5%** |
| KPI-C36-07 | Quotations expiring undecided | unmeasured | < 15% | **< 8%** |
| KPI-C36-08 | Declines with a recorded reason code | 0% | 95% | **100%** |
| KPI-C36-09 | Renewal quotations issued before the lead-time deadline | 0% | 90% | **100%** |
| KPI-C36-10 | Estimate cost accuracy (actual within ±10% of estimate) | unmeasured | 70% | **> 85%** |
| KPI-C36-11 | Tenders disqualified on completeness grounds | unmeasured | < 5% | **0%** |
| KPI-C36-12 | Approval cycle time (submitted → decided) | unmeasured | < 4 h | **< 1 h** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `sale`, `mail`, `portal` | 18% |
| L2 | OCA `sale_order_revision`, `sale_order_type`, `sale_quotation_number`, `sale_order_line_menu`, `partner_contact_*` | 20% |
| L5 | `cd_estimate`, `cd_quotation`, `cd_approval_loop`, `cd_tender`, `cd_quote_analytics` | 62% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C36-01 | `cd_estimate` — estimate object, diagnostic pre-population, cost build-up, availability signalling | Odoo module | 5 PW |
| CD-C36-02 | `cd_quotation` — versioning, options, alternatives, terms, bilingual document generation | Odoo module | 6 PW |
| CD-C36-03 | `cd_approval_loop` — internal approval routing and the multi-channel customer approval loop with evidence sealing | Odoo module + service | 5 PW |
| CD-C36-04 | Tokenised public approval surface (Bengali, 3G-optimised, one screen) | Service + front end | 2 PW |
| CD-C36-05 | `cd_tender` — tender register, compliance matrix, document pack, bid security | Odoo module | 3 PW |
| CD-C36-06 | `cd_quote_analytics` — conversion, turnaround, loss reason and variance reporting | Odoo module | 1 PW |
| | | **Total** | **22 PW** |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M37 Catalogue | No estimate can be built without operations, rBOM and standard times |
| M11 Pricing | No quotation can be issued without a price lock |
| M33 Party Master | A quotation is addressed to a party with a credit position |
| M01 SRM (core) | The dominant estimate source is a diagnosed service order |
| M24 Document | Document generation, e-signature and retention |
| M28 / M29 | Tokenised public surfaces and approval identity |
| M27 Contact Centre *(W4)* | Preferred-channel delivery is fuller once M27 lands; W3 uses direct channel adapters |

**M36 must be accepted before M08 and M39 can be accepted**, since both consume an accepted
proposal as their creation path.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Open corporate proposals (Word/Excel) | ~200 | `fix.quotation` (as issued, current version only) | W3 |
| Historical accepted AMC proposals | ~1,500 | Archive area; linked to M08 contracts, excluded from conversion KPIs | W3–W4 |
| Open tender register (spreadsheet) | ~30 | `fix.tender` with compliance matrices rebuilt manually | W3 |
| Outstanding bid bonds | ~15 | `fix.bid.security` | W3 |

Migrated quotations carry their legacy reference, are marked `migrated`, and are excluded from
conversion, turnaround and variance KPIs.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | An estimate pre-populates from a diagnosed service order with no manual line entry for a standard repair | End-to-end demonstration across five device categories |
| AC-02 | A quotation cannot be issued with any unpriced or unlocked line | Negative test via UI and API |
| AC-03 | An issued version is immutable; every change produces a new, comparable version | Mutation attempt via UI, API and ORM |
| AC-04 | A customer accepts on a phone over 3G in under 60 seconds, in Bengali, including OTP | Field test with real customers at three branches |
| AC-05 | Partial acceptance produces a coherent re-priced scope and releases only the approved work | Scripted scenario including bundle and dependency cases |
| AC-06 | The acceptance evidence pack is sealed, hashed and retrievable, and proves what was approved and when | Evidence retrieval and hash verification |
| AC-07 | An expired quotation cannot be accepted and can only be re-issued as a new version | Negative test |
| AC-08 | Approval thresholds at BDT 5,000 / 25,000 / 100,000 are enforced through every channel including API | Test matrix at each boundary |
| AC-09 | Cost and margin never appear on any customer-facing surface or external API response | Response inspection + security review |
| AC-10 | A 500-asset corporate quotation prices, renders and issues within 60 seconds | Performance test |
| AC-11 | A renewal quotation is generated automatically from an expiring contract at the configured lead time | Scripted scenario |
| AC-12 | A tender cannot be marked submitted with an outstanding mandatory compliance item or document | Negative test |
| AC-13 | An invoice differing from the accepted scope is blocked pending a documented reason and re-approval | Joint test with M20 |
| AC-14 | Named business super-users sign off UAT for all P0 and P1 requirements | Signed UAT record |
| AC-15 | Zero critical or high security findings, including on the tokenised public surface | Security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Is an OTP-confirmed tap on a WhatsApp link legally sufficient acceptance under Bangladeshi contract and evidence law, or is a qualified e-signature required above a value threshold? | Legal / CFO | W3 build |
| Q-02 | What is the standard quotation validity period per quotation type — repair, corporate, contract, tender? | CCO | W3 build |
| Q-03 | Is the diagnostic fee on a declined repair waived for Privilege members? *(carried from M01 Q-02)* | CCO | W3 build |
| Q-04 | What tolerance is permitted between the accepted quotation and the final invoice before re-approval is mandatory? | CFO | W3 build |
| Q-05 | Does 1000FiX intend to bid on e-GP tenders directly, and if so who holds the e-GP registration and digital certificate? | CEO / CCO | W3 build |
| Q-06 | Should partial acceptance be permitted on contract and subscription proposals, or only on repair quotations? | CCO | W4 (M08/M39) |
| Q-07 | Who owns the governed decline/loss reason list, and how often is it reviewed? | CCO / Quality Manager | W3 build |

---

## 19. References

**Internal**
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §3, §5, §10 ·
`M37_Product_and_Service_Catalogue_Management.md` §3, §5.3 ·
`M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md` §3, §5.3 ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` §5.3, §12 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §5, §7 ·
`05-05_Business_Rules_and_Automation_Catalogue.md` ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.1, §8.11, §10.1 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §6, §7 ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Estimate Approval ·
`1000FiX Business Plan` §Corporate Segment, §Government Contracts

**External benchmark**
SAP S/4HANA sales quotation and service quotation — document flow, planned parts and labour ·
Oracle CPQ / Oracle Quoting — guided selling, approval sequences, proposal generation ·
Salesforce CPQ — amendment and renewal quote generation ·
Microsoft Dynamics 365 Sales — quote revision and progression ·
IFS Cloud service quotation — internal cost build-up separated from the customer offer ·
Digital proposal practice (DealHub, Conga, PandaDoc) — tracked delivery, view analytics, one-tap acceptance ·
Bangladesh e-GP / BPPA public procurement guidelines — compliance, bid security, submission discipline ·
Odoo 19 `sale` and OCA `sale_order_revision` module family

---

*Module M36 · Category C · 1000FiX ERP System v2.0 · CONFIDENTIAL*
