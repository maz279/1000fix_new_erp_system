---
id: FIX-ERP2-P05
portal_id: P05
portal_code: VSP
portal_name: Vendor & Supplier Portal
type: External Web Portal (multi-party-class)
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Procurement Manager
system_owner: Digital Channels Squad
priority: P1
wave: W3
---

# P05 — Vendor & Supplier Portal
### Portal Suite · Code `VSP` · Existing (expanded in v2.1)

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P05 |
| **Portal code** | `VSP` |
| **Type** | External web portal serving **four distinct external party classes** |
| **Status** | Existing (expanded in v2.1 — logistics partners, recycling partners, calibration providers and facility vendors added to the original parts-vendor scope) |
| **Priority** | **P1** |
| **Delivery wave** | **W3** (Months 9–13) |
| **Users** | Parts vendors, courier and logistics partners, sub-contractors, recycling partners, calibration providers, facility vendors |
| **Volume** | **200–500 organisations** |
| **Business owner** | Procurement Manager |
| **System owner** | Digital Channels Squad |
| **Technology** | Odoo Portal foundation + Next.js 15 surfaces for the richer flows |
| **Custom development** | `CD-205` |
| **Requirement range** | FR-POR-145 … FR-POR-170 |
| **Requirement count** | **26** *(measured — supersedes the 9 allocation in `05-01` §4)* |
| **Effort estimate** | **18 person-weeks** |
| **Backing modules** | M03, M15, M16, M18, M20, M23, M33, M42, M44, M45, M47, M52 |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M65 Localisation |

---

## 2. Purpose

P05 is **the surface through which everyone who supplies the Company transacts with it**. It
replaces the email thread, the phone call and the paper invoice that currently constitute
1000FiX's supply-side interface.

Its defining characteristic is that it serves **four unrelated party classes** with genuinely
different workflows under one authentication and governance model:

| Class | What they do here | Owning modules |
|---|---|---|
| **Parts vendors and suppliers** | Quote, receive POs, ship, invoice, handle returns | M16, M15, M42, M52 |
| **Logistics and courier partners** | Receive consignment bookings, update status, upload proof of delivery, claim settlement | M03 |
| **Recycling partners** | Receive e-waste batches, upload disposal certificates, report material recovery | M18 |
| **Service providers** | Calibration laboratories, facility vendors and sub-contractors receiving and completing assigned work | M45, M47, M42 |

P05 holds no authoritative state. The purchase order belongs to M16, the invoice to M52, the
consignment to M03, the disposal certificate to M18. What P05 owns is **the supplier's view of
their relationship with 1000FiX** and the self-service that removes 1000FiX staff from the
middle of it.

### Why It Exists

**Supplier administration is absorbing procurement capacity.** With 4–8 procurement officers
against 200–500 supplying organisations, every PO acknowledgement, delivery date query, invoice
status enquiry and payment chase is a phone call or an email. `04-00` targets a **60% reduction
in vendor phone and email queries** — that is procurement capacity returned to sourcing.

**Three-way matching fails on data the vendor holds.** BR-SCM-005 requires PO + GRN + invoice
matching. Matching fails most often because the vendor's invoice references the wrong PO, omits
a line, or arrives weeks after delivery. A portal that validates the invoice against the PO
**at submission** converts a downstream exception into an upstream correction.

**Four new supply relationships have no interface at all.** The v2.1 scope adds logistics
partners (M03), recycling partners (M18), calibration laboratories (M45) and facility vendors
(M47). Each would otherwise be managed by email. Recycling in particular carries a legal
obligation: disposal certificates are the Company's evidence of lawful e-waste handling.

**Vendor performance cannot be improved if the vendor cannot see it.** M42 scores suppliers on
delivery, quality and responsiveness. A scorecard that exists only inside 1000FiX changes
nothing; published to the vendor with the detail behind it, it becomes a conversation.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §4.1 Portal 5 | "Vendor & Partner Portal — 100-500 vendors/brand partners — PO management, warranty claims, invoice submission" |
| ERP BRD BR-SCM-001 | Vendor master with classification: OEM, authorised distributor, local supplier |
| ERP BRD BR-SCM-002 | Purchase requisition with approval workflow |
| ERP BRD BR-SCM-004 | "Record goods receipt with quality inspection before stocking" — the inspection outcome the vendor must see |
| ERP BRD BR-SCM-005 | "Perform 3-way matching: PO + GRN + Vendor Invoice" |
| ERP BRD BR-SCM-006 | "Manage return-to-vendor (RTV) for defective or incorrect parts" |
| ERP BRD BR-SCM-007 | "Track vendor performance: on-time delivery rate, quality rejection rate, lead time" |
| ERP BRD BR-FIN-010 | "Process vendor invoices with 3-way matching (PO + GRN + Invoice)" |
| `04-00` §P05 | Capability set across nine areas including logistics and recycling partners, and four KPIs, adopted verbatim |
| `04-00` §3 PS-01…PS-12 | Twelve cross-portal standards, all binding |
| `05-04` §1 R38 | External Party covering vendor, courier, recycling partner and external auditor sub-classes; MFA required for financial actions |
| `05-04` §8 | External party access rules — own records only |
| `M45` §12.2, INT-EAM-01 | Calibration providers receive jobs and upload certificates through P05 |
| `M47` §12.2, INT-FAC-04 | Facility vendors receive work orders and upload completion evidence through P05 |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Supplier self-registration, document submission and approval tracking |
| 2 | Profile, catalogue, capability, certification and banking detail maintenance |
| 3 | RFQ receipt and quotation submission with price, lead time and validity |
| 4 | Purchase order receipt, acknowledgement, query and delivery-date confirmation |
| 5 | Advance shipping notice submission |
| 6 | Expected receipts view, receipt confirmation and inspection outcome visibility |
| 7 | Rejection response and corrective action submission |
| 8 | Invoice submission against a purchase order, with validation at the point of submission |
| 9 | Three-way match status, payment schedule and remittance advice |
| 10 | Return-to-vendor notification, credit note issue and return tracking |
| 11 | Vendor scorecard with the detail behind each measure |
| 12 | **Logistics partner surface**: consignment booking receipt, status update, proof-of-delivery upload, settlement claim |
| 13 | **Recycling partner surface**: batch transfer receipt, disposal certificate upload, material recovery reporting |
| 14 | **Service provider surface**: assigned job receipt, acceptance, completion evidence, certificate upload |
| 15 | Document repository: agreements, certifications, insurance, compliance documents with expiry tracking |
| 16 | Communication thread with the responsible 1000FiX officer, per transaction |
| 17 | Bengali and English throughout |
| 18 | Instrumentation of adoption and query deflection |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Brand partner warranty claims and consignment** | **P08** Brand Partner Portal | A brand partner is a customer of the Company's service and a supplier of parts; the relationship is materially different and gets its own portal |
| **Marketplace sellers** | **P07** | A marketplace seller sells to 1000FiX's customers, not to 1000FiX |
| **Referral and alliance partners** | **P12** | A referral partner introduces business; they supply nothing |
| **Supplier qualification decision, contract negotiation and scorecard weighting** | **M42** Supplier Relationship | P05 presents the score; M42 computes it and owns the relationship |
| **Requisition, sourcing strategy, PO creation and approval** | **M16** Procurement | P05 receives a PO; it is never created here |
| **Goods receipt, quality inspection decision and stock posting** | **M15** Inventory | P05 shows the outcome; the decision is made by 1000FiX staff in P03 |
| **Three-way match logic and exception resolution** | **M16 / M52** | P05 validates at submission and shows status; the match runs in the ERP |
| **Payment execution, banking and remittance** | **M52 / M50** | P05 shows the schedule and advice; payment is executed by Finance |
| **Landed cost, customs and import documentation** | **M44** Import & Trade Compliance | P05 may collect a document; the calculation is M44's |
| **Consignment routing, manifest construction and courier selection** | **M03** Logistics | P05 receives a booking; M03 decides who gets it |
| **E-waste batch construction and recycler compliance assessment** | **M18** E-Waste | P05 receives a batch and collects the certificate |
| **Calibration profile, interval and the fitness decision** | **M45** Enterprise Assets | P05 receives a calibration job and collects the certificate; fitness is M45's decision |
| **Facility work order triage, SLA and vendor assignment** | **M47** Facility | P05 receives an assigned work order |
| **Identity, session policy and MFA enforcement** | **M29** | **PS-01**; MFA required for financial actions per `05-04` §1 |

### 3.3 Shared Concepts

| Concept | P05's Role | Owning Module |
|---|---|---|
| The supplier's view of their relationship | **Owns** — the defining concern of this portal | P05 |
| Supplier record, qualification and scorecard | Displays; submits profile changes | M42 |
| RFQ and quotation | Receives; submits | M16 |
| Purchase order | Receives; acknowledges | M16 |
| Goods receipt and inspection outcome | Displays | M15 |
| Vendor invoice | Submits with validation; displays match and payment status | M52 |
| Return to vendor and credit note | Receives; issues credit | M15 / M52 |
| Consignment | Receives booking; updates status; uploads POD | M03 |
| E-waste batch and disposal certificate | Receives; uploads certificate | M18 |
| Calibration job and certificate | Receives; uploads certificate | M45 |
| Facility work order | Receives; submits completion evidence | M47 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Ariba Supplier Management** | Supplier self-registration, company detail maintenance and **compliance document submission through a self-service portal**; electronic invoicing with payment-status monitoring; **scorecards accessible to both buyer and supplier**; structured reporting oriented to compliance and audit readiness | **Published scorecards, visible to the supplier, are the single most influential external reference for P05.** A performance measure the supplier cannot see cannot change their behaviour. Also adopted: supplier-maintained profile and compliance documents with expiry tracking, which removes an entire category of procurement admin | Ariba's supplier network model and its network fees. 1000FiX has 200–500 suppliers in one country, not a global network |
| **Coupa Supplier Portal** | Supplier updates on PO receipt and invoice submission; **invoice submissions with missing information are automatically warned or blocked, with an alert to complete the missing areas** | **Validation at submission rather than rejection after the fact, adopted exactly.** This is the mechanism that converts three-way-match failure from a downstream exception consuming procurement and finance time into an upstream correction the supplier makes in thirty seconds | Coupa's full source-to-pay footprint |
| **Supplier portal practice (Highradius, TechnologyMatch surveys)** | ERP and procurement integration, automated compliance and document management, supplier self-service, performance analytics, automated approval workflows | The pattern in full, sized to a single-country supply base | Supplier-risk scoring from external data feeds; disproportionate here |
| **Courier and logistics partner portals** | Booking receipt, status update, electronic proof-of-delivery upload, settlement claim submission | **The logistics partner surface as a first-class class**, because M03's reverse-logistics model depends on custody evidence that the courier holds | Full courier TMS capability; 1000FiX assigns, the partner executes |
| **Recycling and waste-management partner practice** | Batch transfer receipt, disposal certification, material recovery reporting for regulatory evidence | **Disposal certificate collection as a compliance obligation, not a convenience.** The certificate is the Company's legal evidence of lawful e-waste handling under Bangladesh e-waste rules | Full material-flow accounting; M18 owns that |
| **Calibration laboratory practice (ISO/IEC 17025)** | Job receipt, certificate issue with traceability and accreditation reference | **Certificate upload with accreditation reference captured as structured data**, so M45 can flag a non-accredited certificate automatically rather than a person noticing | Direct laboratory system integration; the market is fragmented and file exchange is sufficient |

**Design position.** Four deliberate differences from the benchmark.

First, **one portal, four party classes, one governance model.** The alternative — four
separate partner portals — quadruples the authentication, permission and support burden for a
combined audience of 200–500 organisations. P05 presents each class only the surfaces it needs,
under one identity model and one set of external-party access rules.

Second, **validation happens at submission.** A vendor invoice missing a PO reference, a line
that does not match, or a quantity beyond what was received is rejected **in the portal, with
the reason**, before it enters the ERP. This is more work than accepting everything and letting
the match fail, and it is the single largest efficiency in the portal.

Third, **the scorecard is published with its evidence.** Not a grade — the delivery dates, the
rejection reasons, the response times behind it. A supplier disputing a score they can see the
basis of is a productive conversation; a supplier disputing a number they cannot decompose is
an argument.

Fourth, **compliance documents expire in the portal, not in a drawer.** Trade licences,
insurance certificates, ISO/IEC 17025 accreditations and environmental clearances carry expiry
dates. P05 tracks them, alerts the supplier before expiry, and — where the document is a
precondition of transacting — blocks new work until it is renewed.

---

## 5. Capability Areas & Functions

### 5.1 Onboarding & Profile

| FR ID | Feature | Function — "The portal shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-145 | Self-registration | Allow a prospective supplier to register, declare their party class and category, submit required documents, and track approval to a decision | **P0** | L5 |
| FR-POR-146 | Document submission and expiry | Accept trade licence, TIN/BIN, bank details, insurance, ISO/IEC 17025 accreditation and environmental clearance as structured records with expiry dates, alerting the supplier before expiry | **P0** | L5 |
| FR-POR-147 | Transaction precondition | Prevent a supplier from receiving new work where a document that is a precondition of their class has expired, stating precisely what is required | **P0** | L5 |
| FR-POR-148 | Profile maintenance | Allow the supplier to maintain contacts, addresses, capabilities, service categories, catalogue and banking details, with changes above a threshold routed to M42 for approval | **P0** | L5 |
| FR-POR-149 | Agreement | Present the supplier agreement, capture digital acceptance, and retain the executed version | P1 | L5 |

### 5.2 Sourcing & Orders

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-150 | RFQ receipt and response | Present RFQs matching the supplier's categories, and accept a quotation with unit price, lead time, minimum order quantity, validity and any attachment | **P0** | L5 |
| FR-POR-151 | Quotation history | Show the supplier every quotation submitted and its outcome — awarded, not awarded, expired — so response effort is visibly worthwhile | P1 | L5 |
| FR-POR-152 | Purchase order receipt | Present every purchase order with lines, quantities, prices, delivery location and required date, downloadable as a document | **P0** | L5 |
| FR-POR-153 | Acknowledgement and query | Require acknowledgement of each PO, permit a query or a proposed date change against a line, and route it to the procurement officer | **P0** | L5 |
| FR-POR-154 | Advance shipping notice | Accept an ASN with despatch date, quantities, batch or serial detail and carrier reference, ahead of physical arrival | P1 | L5 |

### 5.3 Receipt, Quality & Returns

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-155 | Expected receipts | Show what 1000FiX expects to receive from this supplier and when, so a missed delivery is visible to both parties simultaneously | P1 | L5 |
| FR-POR-156 | Receipt and inspection outcome | Show the goods receipt and the quality inspection result per line — accepted, rejected, partially accepted — with the rejection reason and evidence (BR-SCM-004) | **P0** | L5 |
| FR-POR-157 | Rejection response | Allow the supplier to respond to a rejection with an explanation, a corrective action, or a replacement commitment, tracked to closure | P1 | L5 |
| FR-POR-158 | Return to vendor | Notify the supplier of an RTV with the RMA reference, quantities and reason, and track it to credit or replacement (BR-SCM-006) | **P0** | L5 |
| FR-POR-159 | Credit note issue | Allow the supplier to issue a credit note against an RTV or a disputed invoice line, validated against the originating document | P1 | L5 |

### 5.4 Invoicing & Payment

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-160 | **Invoice submission with validation** | Accept an invoice submitted against a specific purchase order, and **validate at submission** — PO exists, lines match, quantities do not exceed receipted quantities, prices match agreed terms, tax is correctly stated — rejecting with a precise reason rather than accepting into an exception queue | **P0** | L5 |
| FR-POR-161 | Match status | Show the three-way match state per invoice — matched, blocked with the reason, awaiting receipt — so the supplier can act before chasing (BR-SCM-005, BR-FIN-010) | **P0** | L5 |
| FR-POR-162 | Payment schedule | Show the expected payment date per approved invoice, derived from the agreed terms, and the remittance advice once paid | **P0** | L5 |
| FR-POR-163 | Statement | Present an account statement of invoices submitted, approved, paid and outstanding, with ageing | P1 | L5 |

### 5.5 Partner Class Surfaces

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-164 | **Logistics partner** | Present assigned consignment bookings with pickup and delivery detail, accept status updates and exception reasons, accept proof-of-delivery upload with signature, photograph and timestamp, and accept a settlement claim against completed consignments | **P0** | L5 |
| FR-POR-165 | **Recycling partner** | Present transferred e-waste batches with item detail, accept a disposal certificate as a structured record with issuing authority and date, and accept material recovery reporting by material class (M18) | P1 | L5 |
| FR-POR-166 | **Calibration provider** | Present assigned calibration jobs with the instrument, its profile and required traceability, and accept the certificate with certificate number, accreditation reference, standard used and as-found/as-left results (M45 INT-EAM-01) | P1 | L5 |
| FR-POR-167 | **Facility and service vendor** | Present assigned facility work orders with site, category, SLA and access instructions, accept acceptance and attendance confirmation, and accept completion evidence for branch verification (M47 INT-FAC-04) | P2 | L5 |

### 5.6 Performance & Communication

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-168 | **Published scorecard** | Present the supplier's own scorecard — on-time delivery, quality rejection rate, lead-time adherence, responsiveness, price competitiveness — **with the transactions behind each measure**, not a grade alone (BR-SCM-007) | **P0** | L5 |
| FR-POR-169 | Performance consequence | State plainly what a score below threshold means — reduced allocation, review, suspension — and what recovery requires | P1 | L5 |
| FR-POR-170 | Communication and documents | Provide a per-transaction message thread with the responsible 1000FiX officer, and a document repository of agreements, certificates and correspondence | P1 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No authoritative state** | P05 persists no business object (`04-00` §1) |
| T-02 | **Party isolation** | Every query is scoped to the authenticated supplier organisation at the record layer. A supplier cannot see another supplier's price, order, score or document under any path |
| T-03 | **Class-scoped surfaces** | A supplier sees only the surfaces of their declared party class; a courier partner never sees an RFQ, a parts vendor never sees an e-waste batch |
| T-04 | **Submission-time validation** | Invoice, quotation, ASN and certificate submissions are validated synchronously against the owning module and rejected with a specific, actionable reason. **No submission is accepted into an exception queue that the supplier cannot see** |
| T-05 | **Document integrity** | Uploaded certificates and evidence are stored through M24 as PDF/A with a content hash; a substituted document is detectable |
| T-06 | **Structured certificate capture** | Disposal and calibration certificates capture their key fields as structured data — certificate number, issuing body, accreditation reference, dates — not merely as an attached file |
| T-07 | **MFA on financial actions** | MFA is required for invoice submission, credit note issue, banking detail change and settlement claim, per `05-04` §1 |
| T-08 | **Banking change control** | A change to banking details requires MFA, is held for out-of-band verification by Finance, and is never applied to a pending payment run |
| T-09 | **All traffic through the gateway** | Every call routes through M28 with per-supplier credentials and rate limits (**PS-02**) |
| T-10 | **No client-side business logic** | Match status, score and payment date come from their owning module (**PS-11**) |
| T-11 | **Low-bandwidth operation** | Suppliers include small local vendors on poor connectivity; core flows work at 3G and under 400 KB first load |
| T-12 | **Bengali and English** | Complete in both, with Bengali default for local suppliers (**PS-03**) |
| T-13 | **Accessibility and responsiveness** | WCAG 2.1 AA; usable from 320 px upward — many suppliers will use a phone (**PS-04, PS-05**) |
| T-14 | **Mobile capture for partner classes** | Logistics POD and facility completion evidence capture work on a phone camera with GPS and timestamp |
| T-15 | **Graceful degradation** | Where a backing module is unavailable, the capability is disabled with an explanation and the responsible officer's contact (**PS-09**) |
| T-16 | **Instrumentation** | Adoption, submission validation outcomes and query deflection instrumented to M25 (**PS-10**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Actor

| Actor | Today | With P05 |
|---|---|---|
| **Parts vendor** | Receives a PO by email, invoices on their own template, phones to ask about payment | Receives, acknowledges, ships, invoices with validation, and sees the payment date |
| **Small local supplier** | Learns of a rejection weeks later | Sees the inspection outcome and the reason the same day, on a phone |
| **Courier partner** | Sends POD photographs by WhatsApp | Uploads POD against the consignment with signature, photograph and timestamp |
| **Recycling partner** | Emails a scanned certificate | Uploads it as a structured record against the batch |
| **Calibration laboratory** | Sends a PDF certificate to whoever ordered the work | Uploads it against the instrument with accreditation and as-found results captured |
| **Facility vendor** | Attends when convenient; performance is anecdotal | Receives the work order with an SLA and submits completion evidence |
| **Procurement officer** | Fields PO, delivery and payment queries all day | Handles exceptions; the routine is self-served |
| **Finance officer** | Chases invoices that will not match | Receives invoices already validated against the PO and receipt |
| **Quality manager** | Chases suppliers on rejections by email | Sees rejection responses and corrective actions tracked to closure |
| **Warehouse** | Surprised by deliveries | Sees advance shipping notices before arrival |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Procurement capacity released** | PO acknowledgement, status, delivery and payment queries self-served | `04-00` target: **vendor phone and email queries −60%**. With 4–8 procurement officers against 200–500 suppliers this is the portal's largest single benefit |
| **Three-way match exception reduction** | Invoices validated against PO and receipt **at submission** | Every prevented exception is procurement and finance time not spent, and a payment not delayed. Supports BR-SCM-005 and BR-FIN-010 |
| **Administrative labour savings** | Structured submission replaces email, attachments and re-keying across four party classes | Contributes to the **BDT 62 lac/year** cross-module administrative saving in Scope Charter §6.2 |
| **Inventory cost reduction** | Better RFQ response rates and comparable quotations improve sourcing outcomes | Supports the **BDT 34 lac/year** inventory benefit attributed to M15 + M26 |
| **Supplier performance improvement** | Published scorecards with evidence change vendor behaviour | Supports on-time delivery and quality rejection targets in M42 |
| **Payment discipline** | Suppliers see the payment date; Finance is not chased and can plan | Supports the **BDT 26 lac/year** cash-flow benefit attributed to M19 + M20 |
| **RTV credit recovery** | Returns notified in-portal with credit issue tracked to closure | Supports M15's target of 95% of RTV credit value recovered |
| **E-waste compliance evidence** | Disposal certificates collected as structured records rather than emailed PDFs | Protects the Company's legal position on lawful e-waste handling |
| **Calibration turnaround** | Jobs assigned and certificates returned in-portal with accreditation captured | Supports M45's Wave 5 calibration compliance gate |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Supplier relationship professionalism** | A portal changes how a supplier perceives the Company, and it matters in negotiation |
| **Auditable supply chain** | Every order, receipt, rejection, invoice and payment is evidenced in one place for internal and external audit |
| **Compliance document currency** | Trade licences, insurance and accreditations tracked to expiry rather than discovered lapsed |
| **Anti-fraud control** | Banking-change control with MFA and out-of-band verification addresses the most common supplier-payment fraud vector |
| **Small-supplier inclusion** | Bengali-first, phone-usable, low-bandwidth operation means local suppliers are not excluded by the technology |
| **Segregation of duties** | SOD-01 and SOD-02 in `05-04` §6 are supported because supplier-submitted data enters through a controlled surface rather than by email to an individual |
| **Expansion readiness** | A new supplier class is a surface configuration, not a new portal |

---

## 8. User Journeys & State Models

### 8.1 Invoice Submission — validation at the door

```
   SUPPLIER SUBMITS INVOICE against a PO
        │
   ┌────▼──────────────────────────────────────────────┐
   │  SYNCHRONOUS VALIDATION (M16 + M15 + M52)         │
   │   ▸ PO exists and is open?                        │
   │   ▸ lines match PO lines?                          │
   │   ▸ quantity ≤ receipted quantity?                 │
   │   ▸ price matches agreed terms?                    │
   │   ▸ tax correctly stated (VAT/Mushak)?             │
   │   ▸ no duplicate invoice number for this supplier? │
   └────┬─────────────────────────────┬────────────────┘
        │ all pass                    │ any fail
        │                       ┌─────▼──────────────────────┐
        │                       │  REJECTED AT SUBMISSION    │
        │                       │  precise reason per line   │
        │                       │  supplier corrects now     │
        │                       └────────────────────────────┘
   ┌────▼──────────────┐
   │  ACCEPTED         │──► enters M52 for three-way match
   └────┬──────────────┘
        │
   ┌────▼──────────────┬─────────────────────┐
   │  MATCHED          │  BLOCKED            │
   │  → payment date   │  → reason visible   │
   │     shown         │     to the supplier │
   └────┬──────────────┴──────────┬──────────┘
        │                         │ supplier resolves
   ┌────▼──────────────┐          │
   │  PAID → remittance│◄─────────┘
   │  advice available │
   └───────────────────┘
```

> **The design point.** Every benchmark portal accepts the invoice and lets the match fail
> downstream. Rejecting at the door — with a reason the supplier can act on immediately — is
> what turns a two-week exception cycle into a two-minute correction.

### 8.2 Supplier Lifecycle

```
   REGISTERED ──documents submitted──► UNDER REVIEW ──approved──► ACTIVE
        │                                    │                      │
        │                                    │ rejected             │ score below
        │                                    ▼                      │ threshold
        │                              DECLINED                     ▼
        │                                                   ┌───────────────┐
        │                                                   │ UNDER REVIEW  │
        │  document expired (precondition)                  │ (performance) │
        └──────────────────────────────────────────────────►└───┬───────┬───┘
                                                                │       │
                                              recovered ────────┘       │ not recovered
                                                                        ▼
                                                                  ┌──────────┐
                                                                  │SUSPENDED │
                                                                  └────┬─────┘
                                                                       │
                                                                  ┌────▼─────┐
                                                                  │ OFFBOARDED│
                                                                  └──────────┘
```

| Transition | Guard | Owner |
|---|---|---|
| Registered → Under review | Required documents complete for the declared class | System |
| Under review → Active | M42 qualification approved; agreement executed | Procurement Manager |
| Active → Under review (performance) | Scorecard below threshold for the configured period | M42, automatic |
| Active → blocked for new work | A precondition document expired | System, automatic |
| Under review → Suspended | Performance not recovered within the review period | Procurement Manager |
| Suspended → Offboarded | Decision taken; open transactions settled | Procurement Manager + CFO |

---

## 9. Portal Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P05-01 | A supplier may access only their own records, under every path including export and API | **H** | CTO |
| PRU-P05-02 | A supplier sees only the surfaces of their declared party class | **H** | Procurement Manager |
| PRU-P05-03 | P05 persists no authoritative business state (`04-00` §1) | **H** | CTO |
| PRU-P05-04 | An invoice failing submission validation is rejected with a specific reason and never enters an exception queue invisible to the supplier | **H** | CFO |
| PRU-P05-05 | A supplier cannot invoice for a quantity exceeding what was receipted | **H** | CFO |
| PRU-P05-06 | A duplicate invoice number from the same supplier is rejected | **H** | CFO |
| PRU-P05-07 | MFA is required for invoice submission, credit note issue, banking change and settlement claim (`05-04` §1) | **H** | CFO |
| PRU-P05-08 | A banking detail change is held for out-of-band verification by Finance and never applied to a pending payment run | **H** | CFO |
| PRU-P05-09 | A supplier whose precondition document has expired cannot receive new work | **H** | Procurement Manager |
| PRU-P05-10 | The scorecard is published to the supplier with the transactions behind each measure, not as a grade alone | **C** | Procurement Manager |
| PRU-P05-11 | A supplier never sees another supplier's price, quotation, score or allocation | **H** | Procurement Manager |
| PRU-P05-12 | A purchase order is never created, amended or approved in P05 | **H** | Procurement Manager |
| PRU-P05-13 | A goods receipt or inspection decision is never made in P05 | **H** | Warehouse Manager |
| PRU-P05-14 | Uploaded certificates are stored as PDF/A with a content hash, and key fields captured as structured data | **H** | Quality Manager |
| PRU-P05-15 | A calibration certificate from a non-accredited provider is flagged to M45 at submission | **H** | Quality Manager |
| PRU-P05-16 | A disposal certificate is a required, structured record before an e-waste batch is closed | **H** | Quality Manager |
| PRU-P05-17 | Core flows operate under 400 KB first load and function on a 3G connection | **C** | Digital Channels Squad |
| PRU-P05-18 | Every screen is complete in Bengali and English, with Bengali default for local suppliers (**PS-03**) | **H** | Procurement Manager |

---

## 10. Data, Caching & State Model

### 10.1 What P05 Holds

| Object | Purpose | Ownership |
|---|---|---|
| Supplier portal user accounts and class scoping | Which people at a supplier may do what | **P05**, identity in M29 |
| Draft submissions | Recovery of an interrupted quotation or invoice | **P05**, transient |
| Saved views | Per supplier user | **P05** |
| Session and preference | Language, landing surface | M29 / P05 |

### 10.2 Never Held

| Item | Reason |
|---|---|
| Any business object — PO, receipt, invoice, consignment, batch | PRU-P05-03 |
| Another supplier's data of any kind | PRU-P05-01, PRU-P05-11 |
| 1000FiX internal cost, margin, stock position or customer data | External party isolation (`05-04` §8) |
| Match logic, scoring weights or payment-term calculation | PRU-P05-... (**PS-11**) |
| Banking credentials beyond the submitted change awaiting verification | PRU-P05-08 |

### 10.3 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party` (supplier), qualification, scorecard | M33 / **M42** | Read; submit profile changes |
| `fix.rfq`, `fix.quotation` | M16 | Read RFQ; submit quotation |
| `fix.purchase.order` | M16 | Read; acknowledge and query |
| `fix.goods.receipt`, inspection outcome | M15 | Read |
| `fix.stock.rtv` | M15 | Read; respond, issue credit |
| `fix.vendor.invoice`, match state, payment schedule | **M52** | Submit with validation; read status |
| `fix.consignment`, custody event, POD | **M03** | Read booking; submit status and POD |
| `fix.ewaste.batch`, `fix.disposal.certificate` | **M18** | Read batch; submit certificate |
| `fix.calibration.record` | **M45** | Read job; submit certificate |
| `fix.facility.work.order` | **M47** | Read; accept and submit completion |
| `fix.document`, retention policy | M24 | Upload and retrieve |
| `fix.import.consignment` | M44 | Read where the supplier is the shipper |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P05-01 | RFQ issued by M16 to a supplier's category | Notify the supplier and present the RFQ with its response deadline | Notify by email; RFQ remains visible |
| AUT-P05-02 | Purchase order issued | Notify the supplier and require acknowledgement within the configured window; escalate to the procurement officer if unacknowledged | Escalate; PO remains open |
| AUT-P05-03 | Invoice submitted | Validate synchronously against PO, receipt and terms; accept or reject with a per-line reason | Reject rather than accept an unvalidated invoice |
| AUT-P05-04 | Three-way match blocked | Show the supplier the blocking reason and what is required to resolve it | Status visible; officer notified |
| AUT-P05-05 | Invoice approved for payment | Publish the expected payment date derived from agreed terms | Status visible |
| AUT-P05-06 | Payment executed | Publish the remittance advice against the invoices settled | Retry; advice retrievable |
| AUT-P05-07 | Goods receipt inspection completed | Publish the outcome per line with rejection reason and evidence, and notify the supplier | Publish on next refresh |
| AUT-P05-08 | RTV raised | Notify the supplier with the RMA reference, quantities and reason, and open the credit tracking | Notify by email; RTV remains open |
| AUT-P05-09 | Compliance document approaching expiry | Alert the supplier at 60, 30 and 7 days; on expiry, block new work for that class | Alert only until expiry, then hard block |
| AUT-P05-10 | Consignment booked to a logistics partner | Notify and present the booking with pickup, delivery and SLA | Notify by phone fallback via M03 |
| AUT-P05-11 | E-waste batch transferred | Present the batch and require a disposal certificate within the regulatory window; escalate on lapse | Escalate to Quality Manager |
| AUT-P05-12 | Calibration job assigned | Present the instrument, profile and required traceability; require the certificate on completion | Escalate to Quality Manager |
| AUT-P05-13 | Facility work order assigned | Notify with site, SLA and access instructions; escalate if unaccepted within the emergency window | Escalate per M47 AUT-FAC-08 |
| AUT-P05-14 | Scorecard period closes | Publish the updated scorecard with underlying transactions; where below threshold, state the consequence and the recovery required | Publish; notify the procurement officer |
| AUT-P05-15 | Banking detail change submitted | Hold pending out-of-band verification, notify Finance, and exclude from any pending payment run | Hold indefinitely rather than apply |

---

## 12. Module Interfaces

### 12.1 Modules P05 Consumes

| Module | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, MFA on financial actions, supplier scoping | OIDC via gateway |
| M28 Integration Platform | Every call; per-supplier rate limits | Gateway |
| M33 Party Master | Supplier identity and contacts | REST |
| M42 Supplier Relationship | Qualification state, scorecard, agreement terms | REST |
| M16 Procurement | RFQ, purchase order, acknowledgement, ASN | REST + events |
| M15 Inventory | Goods receipt, inspection outcome, RTV | REST + events |
| M52 Accounts Payable | Invoice validation, match state, payment schedule, remittance | REST |
| M03 Logistics | Consignment bookings and status | REST + events |
| M18 E-Waste | Batch transfers and certificate requirements | REST |
| M45 Enterprise Assets | Calibration job assignment and profile | REST |
| M47 Facility | Facility work order assignment and SLA | REST |
| M44 Import & Trade Compliance | Shipping documentation requirements | REST |
| M24 Documents | Document storage, hashing, retention | REST |
| M65 Localisation | Bengali and English bundles | Build-time + REST |

### 12.2 What P05 Writes Back

| Target | What | Mechanism |
|---|---|---|
| M16 | Quotation submission, PO acknowledgement, date-change query, ASN | Command |
| M52 | **Validated invoice submission**, credit note issue | Command |
| M15 | Rejection response and corrective action | Command |
| M03 | Consignment status update, exception, **proof of delivery**, settlement claim | Command |
| M18 | **Disposal certificate** with structured fields, material recovery report | Command |
| M45 | **Calibration certificate** with accreditation reference and as-found/as-left results | Command |
| M47 | Work order acceptance, attendance, completion evidence | Command |
| M42 | Profile and capability changes; scorecard responses | Command |
| M33 | Contact and address maintenance | Command |
| M29 | Supplier user management within the organisation | Command |
| M25 / M62 | Adoption, validation-outcome and deflection analytics | Event stream |

### 12.3 Events P05 Consumes

| Event | Source | Effect in P05 |
|---|---|---|
| `rfq.issued` | M16 | Present the RFQ; notify |
| `purchase_order.issued` | M16 | Present the PO; require acknowledgement |
| `stock.received` / `stock.inspection_completed` | M15 | Publish the receipt and inspection outcome |
| `stock.rtv_raised` | M15 | Notify and open credit tracking |
| `invoice.matched` / `invoice.blocked` | M52 | Update match status with reason |
| `payment.executed` | M52 | Publish remittance advice |
| `consignment.booked` | M03 | Present the booking to the logistics partner |
| `ewaste.batch_transferred` | M18 | Present the batch; require the certificate |
| `equipment.calibration_due` | M45 | Present the calibration job |
| `facility.work_order_raised` | M47 | Present the assigned work order |
| `supplier.scorecard_published` | M42 | Publish the scorecard with detail |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P05-01 | Supplier ERP or accounting systems | Inbound | Invoice and ASN submission by file for higher-volume suppliers; portal entry otherwise |
| INT-P05-02 | Email and SMS | Outbound | Notification where a supplier has not adopted the portal; via M27 |
| INT-P05-03 | Bank remittance files | Outbound | Remittance advice generated by M52 and published here |
| INT-P05-04 | Courier partner tracking systems | Bidirectional | Status exchange for partners with their own systems; via M03 and M28 |

### 12.5 API Surface Consumed

| Endpoint | Method | Purpose | Owner |
|---|---|---|---|
| `/api/v1/suppliers/me` | GET/PATCH | Profile, documents, banking, capabilities | M42 / M33 |
| `/api/v1/rfqs` | GET | RFQs for this supplier's categories | M16 |
| `/api/v1/quotations` | POST | Submit a quotation | M16 |
| `/api/v1/purchase-orders` | GET/PATCH | Receive, acknowledge, query | M16 |
| `/api/v1/asn` | POST | Advance shipping notice | M16 |
| `/api/v1/receipts` | GET | Goods receipt and inspection outcome | M15 |
| `/api/v1/rtv` | GET/POST | RTV notification and response | M15 |
| `/api/v1/invoices/validate` | POST | **Synchronous submission validation** | M52 |
| `/api/v1/invoices` | POST/GET | Submit; match status; payment schedule | M52 |
| `/api/v1/consignments` | GET/PATCH | Booking, status, POD upload | M03 |
| `/api/v1/ewaste/batches/{id}/certificate` | POST | Disposal certificate with structured fields | M18 |
| `/api/v1/equipment/{id}/calibration` | POST | Calibration certificate with readings | M45 |
| `/api/v1/facility/work-orders/{id}` | GET/PATCH | Accept, attend, complete with evidence | M47 |
| `/api/v1/suppliers/me/scorecard` | GET | Scorecard with underlying transactions | M42 |

---

## 13. Roles & Permissions

**R38 External Party** is the only role class with P05 access (`05-04` §2), scoped by declared
party class:

| Party class | Surfaces | MFA |
|---|---|---|
| **Parts vendor / supplier** | Onboarding, RFQ, PO, ASN, receipts, RTV, invoicing, scorecard | **Required for financial actions** |
| **Logistics / courier partner** | Onboarding, consignment bookings, status, POD, settlement claims, scorecard | Required for settlement claims |
| **Recycling partner** | Onboarding, batch transfers, disposal certificates, material recovery | Required for financial actions |
| **Calibration provider** | Onboarding, calibration jobs, certificate upload | Required for financial actions |
| **Facility / service vendor** | Onboarding, work orders, completion evidence, invoicing, scorecard | Required for financial actions |

Within a supplier organisation, P05 supports named users with sub-scoping — an operations
contact who acknowledges POs and a finance contact who invoices need not be the same person.

> **Internal roles with P05 visibility (via P03, not by logging into P05):** R15 Logistics
> Coordinator, R17 Inventory Manager, R19 Procurement Officer, R26 Finance Manager, R27 Finance
> Officer, per `05-04` §2. They act in P03 under their own identity; **no impersonation path
> into P05 exists.**

**Field-level restrictions.** A supplier sees their own prices and their own scorecard only.
1000FiX internal cost, margin, stock position, customer identity and any other supplier's data
are absent from every P05 payload. `vendor_price` for other vendors is never exposed.

**Segregation of duties.** P05 supports **SOD-01** (create vendor + approve vendor invoice) and
**SOD-02** (raise PO + receive goods + approve invoice) by ensuring supplier-originated data
enters through a controlled, attributed surface rather than by email to an individual officer.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Adoption by class** | Active supplier organisations per class against total onboarded; suppliers never logging in | M42, M25 |
| **PO acknowledgement rate** | Acknowledged in-portal versus by email or phone | M25 — the `04-00` KPI |
| **Invoice submission rate** | Submitted in-portal versus by email or paper | M25 — the `04-00` KPI |
| **Submission validation outcomes** | Rejections at submission by reason — the direct measure of prevented exceptions | M52, M16, M25 |
| **Query deflection** | Vendor phone and email contacts before and after adoption, per supplier | M25 — the `04-00` KPI |
| **RFQ response rate** | RFQs issued versus quotations received, by category and supplier | M16, M25 |
| Match performance | Invoices matched first time versus blocked, by supplier and reason | M52 |
| Document currency | Suppliers with expiring or expired precondition documents | M42, Quality |
| Partner-class performance | POD completeness, certificate turnaround, facility SLA attainment | M03, M18, M45, M47 |
| Scorecard engagement | Suppliers viewing their scorecard; correlation with subsequent performance | M42 |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W5 Target | W8 Target |
|---|---|---|---|---|
| — | **POs acknowledged through the portal** | 0% | 75% | **> 90%** |
| — | **Invoices submitted through the portal** | 0% | 70% | **> 85%** |
| — | **Vendor phone/email queries** | baseline | −40% | **−60%** |
| — | **RFQ response rate** | unmeasured | 60% | **> 75%** |
| — | Invoices passing submission validation first time | n/a | 80% | **> 93%** |
| — | Three-way match exceptions per 100 invoices | unmeasured | −50% | **−80%** |
| — | Supplier organisations active in the portal | 0% | 70% | **> 88%** |
| — | Proof-of-delivery uploaded in-portal by logistics partners | 0% | 90% | **100%** |
| — | Disposal certificates received within the regulatory window | unmeasured | 95% | **100%** |
| — | Calibration certificates uploaded with accreditation captured | 0% | 95% | **100%** |
| — | Suppliers with expired precondition documents transacting | unknown | **0** | **0** |
| — | Banking-change fraud incidents | unknown | **0** | **0** |
| — | Bengali and English completeness | n/a | **100%** | **100%** |
| — | Cross-supplier data exposures | n/a | **0** | **0** |

> **Register note.** The first four metrics are adopted verbatim from `04-00` §P05. P05 has
> **no KPI-0nn identifiers allocated**; all thirteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `portal` — external party authentication, document access, basic record views | 16% |
| L2 | OCA `portal`, `purchase-workflow` and `dms` portal extensions | 14% |
| L5 | **Next.js 15 surfaces** for the richer flows: invoice validation, POD capture, certificate submission, scorecard | 70% |

> P05 uses the Odoo portal foundation for authentication and document serving, and custom
> surfaces for the flows where submission-time validation and mobile evidence capture matter.
> This hybrid is deliberate: a full custom build for 200–500 users would not be justified, and a
> pure Odoo portal cannot deliver the validation-at-the-door behaviour that produces the
> benefit.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-205** | `p05_supplier_portal` — onboarding with document expiry control, RFQ and quotation, PO acknowledgement and ASN, receipt and inspection visibility, RTV and credit, **invoice submission with synchronous validation**, payment schedule and remittance, the four partner-class surfaces (logistics POD, recycling certificate, calibration certificate, facility completion), published scorecard, banking-change control | Next.js 15 + Odoo portal extension | 18 PW |

> **CD register.** One ID, **CD-205**, claimed following CD-204 (P04). All CD IDs remain
> provisional pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M29 Identity & Security | External party authentication and MFA on financial actions |
| M28 Integration Platform | Gateway with per-supplier credentials |
| M33 Party Master | Supplier identity |
| **M16 Procurement** | RFQ, PO and receipt — the portal's core (W3) |
| **M15 Inventory** | Goods receipt, inspection and RTV (W2) |
| **M52 Accounts Payable** | Invoice validation, match and payment (W3) |
| M42 Supplier Relationship | Qualification and scorecard (W4) — **the scorecard surface follows in W4** |
| M03 Logistics | Consignment bookings (W3) |
| M18 E-Waste | Recycling partner surface (W8) — added when M18 lands |
| M45 Enterprise Assets | Calibration provider surface (W5) — added when M45 lands |
| M47 Facility | Facility vendor surface (W7) — added when M47 lands |

**Phasing within the portal.** W3 ships onboarding, RFQ, PO, receipts, RTV, invoicing and the
logistics partner surface. W4 adds the published scorecard. W5 adds the calibration provider
surface. W7 adds facility vendors. W8 adds recycling partners.

### 16.4 Onboarding & Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing vendor master records | 200–500 organisations | M33 / M42, then portal invitation | W3 |
| Vendor compliance documents | Held in procurement files | `fix.document` with expiry captured | W3, verified against the original |
| Open purchase orders at cutover | Current only | M16, published to the portal | W3 |
| Open RTVs and pending credits | Current only | M15 | W3 |
| Courier partner arrangements | Held by logistics | M03, then portal invitation | W3 |

> **Onboarding position.** Suppliers are onboarded **in value order, with the top 20 by spend
> onboarded first and personally.** A portal with 15% supplier adoption produces no query
> deflection at all — the officer still handles email for the other 85% *and* checks the portal.
> Adoption is therefore driven, not offered: after the configured transition period, PO
> acknowledgement and invoice submission are portal-only for onboarded suppliers, and that date
> is communicated at onboarding.
>
> Compliance documents are loaded **with the expiry date verified against the original
> document**, not transcribed from a spreadsheet. A document loaded without a verified expiry is
> loaded as expired, which blocks new work until it is produced — the same position taken by
> M46 for vehicle documents and M47 for site licences.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A supplier cannot access another supplier's records — price, order, score, document — through any path | Tenant-isolation penetration test |
| AC-02 | A supplier sees only the surfaces of their declared party class | Negative test across all five classes |
| AC-03 | An invoice failing any validation rule is rejected at submission with a specific, per-line reason | Rule-by-rule negative test across all six validation rules |
| AC-04 | An invoice for a quantity exceeding the receipted quantity cannot be submitted | Negative test |
| AC-05 | A duplicate invoice number from the same supplier is rejected | Negative test |
| AC-06 | MFA is enforced for invoice submission, credit note issue, banking change and settlement claim | Authentication test per action |
| AC-07 | A banking detail change is held for out-of-band verification and excluded from any pending payment run | Scripted scenario with M52 |
| AC-08 | A supplier whose precondition document has expired cannot receive new work | Negative test per party class |
| AC-09 | The scorecard shows the underlying transactions behind each measure, not a grade alone | Scorecard review with three suppliers |
| AC-10 | A logistics partner can upload proof of delivery with signature, photograph and timestamp on a phone | Field test with two courier partners |
| AC-11 | A disposal certificate is captured as a structured record with issuing authority and date, and an e-waste batch cannot close without it | Scripted scenario with M18 |
| AC-12 | A calibration certificate captures certificate number, accreditation reference, standard used and as-found/as-left results, and a non-accredited certificate is flagged to M45 | Scripted scenario with M45 |
| AC-13 | No P05 payload contains 1000FiX internal cost, margin, stock position or customer data | Automated payload inspection across every endpoint |
| AC-14 | Core flows load under 400 KB and function on a throttled 3G connection | Performance test |
| AC-15 | Every screen renders in Bengali and English, with Bengali default for local suppliers | Translation coverage report |
| AC-16 | WCAG 2.1 AA, usable from 320 px upward | Automated scan plus manual audit |
| AC-17 | PO acknowledgement exceeds 90% and invoice submission exceeds 85% through the portal | Six consecutive monthly reports |
| AC-18 | Vendor phone and email queries fall by 60% against the pre-portal baseline | Contact-volume comparison over six months |
| AC-19 | Procurement Manager, Finance Manager and three suppliers sign off UAT | Signed UAT record |

**Definition of done:** the twelve cross-portal standards in `04-00` §3 plus the 19 criteria
above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | How many supplying organisations exist by class, and what is the spend concentration? This determines the onboarding sequence | Procurement Manager | **W3 minus 3 months** |
| Q-02 | Is portal-only PO acknowledgement and invoice submission mandated after a transition period, and what is that date? Without a mandate, adoption stalls and no benefit is realised | Procurement Manager / CFO | **W3 design** |
| Q-03 | What are the exact invoice validation rules — particularly tolerance on price and quantity variance? | CFO / Procurement Manager | W3 design |
| Q-04 | What is the out-of-band verification procedure for a banking-detail change, and who performs it? | CFO | **W3 design** |
| Q-05 | Which compliance documents are preconditions of transacting, per party class? | Procurement Manager / Legal / Quality Manager | W3 design |
| Q-06 | Do any suppliers have systems capable of file-based invoice and ASN submission, and in what format? | CTO / Procurement Manager | W3 build |
| Q-07 | Are payment terms disclosed in the portal as a date, or as terms only? Disclosing a date creates an expectation Finance must meet | CFO | W3 design |
| Q-08 | What scorecard weighting is published, and is the threshold consequence contractual? | Procurement Manager / Legal | W4 design |
| Q-09 | Do courier partners use their own systems, requiring integration rather than portal entry? | Logistics Manager / CTO | W3 design |
| Q-10 | What is the regulatory window for a disposal certificate after e-waste transfer under Bangladesh e-waste rules? | Quality Manager / Legal | W8 design |
| Q-11 | Are sub-contractors performing customer-facing service in P05 scope, or are they marketplace sellers in P07? | CCO / Procurement Manager | **W3 design** |
| Q-12 | Do suppliers work in Bengali or English predominantly, and does that differ by class? | Procurement Manager | W3 design |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §P05, §1, §3 PS-01…PS-12, §4 ·
`P03_Admin_Operations_Portal.md` · `P07_Marketplace_Seller_Portal_and_Application.md` ·
`P08_Brand_Partner_Portal.md` · `P09_Logistics_and_Rider_Application.md` ·
`03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md`
§5.8, §12.2 (P05 consumer of RTV status) ·
`03_Modules/F_Asset_Equipment_and_Facilities/M45_Enterprise_Asset_and_Test_Equipment.md`
§12.4 INT-EAM-01, §13 (calibration provider access) ·
`03_Modules/F_Asset_Equipment_and_Facilities/M47_Facility_Branch_Infrastructure_and_Workplace.md`
§12.4 INT-FAC-04, §13 (facility vendor access) ·
`03_Modules/A_Service_Delivery_and_Operations/M03_Service_Logistics_and_Reverse_Logistics.md` ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md`
§1 (R38), §2, §5, §6 SOD-01 and SOD-02, §8

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.1 Portal 5, BR-SCM-001,
BR-SCM-002, BR-SCM-004, BR-SCM-005, BR-SCM-006, BR-SCM-007, BR-FIN-010 ·
`1000FiX_Services_Company_Profile.md` §Authorized Service Partnerships

**External benchmark**
[SAP Ariba supplier portal — self-service registration, compliance documents, electronic invoicing and shared scorecards](https://2isolutionsus.com/blog/a-complete-guide-to-sap-supplier-portal:-features,-benefits,-and-best-practices) ·
[Coupa Supplier Portal — invoice submissions with missing information warned or blocked at submission](https://www.stampli.com/blog/ap-automation/coupa-vs-ariba/) ·
[Coupa supplier information, risk and performance management](https://coupa.com/products/supplier-information-management) ·
[Ariba versus Coupa procurement — RFQ, PO, invoice and scorecard capability](https://www.procuredesk.com/ariba-vs-coupa-procurement/) ·
[Best supplier portal software — self-service, compliance, scorecards and ERP integration](https://technologymatch.com/blog/best-supplier-portal-software-for-it-leaders) ·
[Supplier management software capabilities](https://www.highradius.com/resources/Blog/best-supplier-management-tools/) ·
[Electronic proof of delivery practice](https://locus.sh/blogs/electronic-proof-of-delivery/) ·
[ISO/IEC 17025 accreditation and metrological traceability](https://cloudlims.com/what-is-iso-iec-17025-accreditation-key-benefits-the-role-of-an-iso-iec-17025-lims-solution/)

---

*Portal P05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
