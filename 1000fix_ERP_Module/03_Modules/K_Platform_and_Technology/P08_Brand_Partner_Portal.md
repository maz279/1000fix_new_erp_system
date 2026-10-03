---
id: FIX-ERP2-P08
portal_id: P08
portal_code: BPP
portal_name: Brand Partner Portal
type: External Web Portal (OEM / brand principal)
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Digital Channels Squad
priority: P1
wave: W4
---

# P08 — Brand Partner Portal
### Portal Suite · Code `BPP` · ★ New in v2.1

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P08 |
| **Portal code** | `BPP` |
| **Type** | External web portal for OEM brand principals |
| **Status** | ★ New in v2.1 — v1.0 had only a combined vendor/partner portal with no brand-specific capability |
| **Priority** | **P1** |
| **Delivery wave** | **W4** (Months 14–18) |
| **Users** | Authorised brand partner staff — warranty administrators, quality engineers, parts managers, auditors |
| **Volume** | **50–150 users** across **17+ brand partners** |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Digital Channels Squad |
| **Technology** | Next.js 15 (React 19), shared design system |
| **Custom development** | `CD-209` |
| **Requirement range** | FR-POR-229 … FR-POR-254 |
| **Requirement count** | **26** *(measured — supersedes the 7 allocation in `05-01` §4)* |
| **Effort estimate** | **18 person-weeks** |
| **Backing modules** | M09, M11, M15, M17, M22, M23, M24, M25, M33, M37, M42, M52 |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M65 Localisation |

---

## 2. Purpose

P08 is **the surface on which the Company's most valuable relationships are audited**. 1000FiX
is the authorised warranty service partner for **17+ international brands** — Dell, HP, Lenovo,
Acer, Toshiba, Sony, Samsung, Xiaomi, Huawei, Microsoft, Epson, Intel and others. That
authorisation is the single largest structural asset the business holds, and it produces the
largest single benefit line in the programme: **BDT 100 lac per year of warranty revenue
recovery**.

Its purpose is narrow and consequential: let a brand partner **decide a claim from evidence,
without asking for it.** Today a warranty claim reaches a brand by email with attachments, and
the brand's administrator requests what is missing, which takes days, and the claim ages, and
some proportion is never paid.

P08 holds no authoritative state. The claim belongs to M09, the evidence to M17 and M24, the
consignment stock to M15. What P08 owns is **the brand's view of 1000FiX as their service
partner** — and that view is, in practice, the renewal case for the authorisation.

### Why It Exists

**Warranty recovery is the programme's largest single benefit and it depends on evidence
reaching a decision-maker.** `04-00` targets claims submitted through the portal above 80%,
decision time under 10 days, approval rate above 92% and days from service to reimbursement
under 45. Each of those is a working-capital and revenue number, and each is unachievable by
email.

**Brand audits are how authorisations are lost.** A brand auditing its authorised partner will
ask for calibration records, technician certification, parts provenance and claim evidence.
Category F's M45 exists substantially to answer those questions; P08 is where the answers are
presented. A partner who can produce them on demand is in a different conversation from one who
compiles them over two weeks.

**Consignment stock is the brand's property held by 1000FiX.** M15 models brand consignment as
an ownership class that must never be consumed on paid work, reconciled monthly to the brand's
own records. That reconciliation is published here. A brand that cannot see its own stock in a
partner's custody is carrying an unmeasured risk.

**Reliability data is a genuine asset.** 1000FiX holds fault history across a large installed
base of each brand's models. Presented as cohort reliability analysis — failure mode by model,
by age band, with population size — it is information most brands cannot easily obtain in this
market, and it materially changes the partnership conversation.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §4.1 Portal 5 | The v1.0 combined vendor/partner portal included "warranty claims" — separated here into a brand-specific portal |
| ERP BRD BR-CWM-006 | "Auto-generate warranty claim records from closed warranty-type service orders" |
| ERP BRD BR-CWM-007 | "Track warranty claim lifecycle: Submitted → Under Review → Approved → Parts Shipped → Completed → Billed → Paid" |
| ERP BRD BR-CWM-008 | "Attach all required documentation to warranty claims (photos, diagnostic report, parts used)" |
| ERP BRD BR-CWM-009 | "Reconcile brand partner warranty payments against submitted claims" |
| ERP BRD BR-FIN-003 | "Generate warranty claim invoices to brand partners with all required documentation attached" |
| ERP BRD BR-BI-010 | Warranty claim analytics: claims by brand, approval rate, ageing, revenue realisation |
| ERP BRD BR-HRM-002 | Technician certifications and **brand authorisations** with expiry — surfaced to the brand |
| Scope Charter §6.2 | **Warranty revenue recovery: BDT 100 lac/year**, attributed to M09 — the benefit this portal protects |
| Company Profile §Authorized Service Partnerships | 17+ named brands for whom 1000FiX performs warranty work |
| `04-00` §P08 | Capability set across nine areas and five KPIs, adopted verbatim |
| `04-00` §3 PS-01…PS-12 | Twelve cross-portal standards, all binding |
| `05-04` §1 R38 | External Party covering the brand partner sub-class; MFA required for financial actions |
| `M15` §5.2, §12.2, §14 | Consignment ledger by brand, monthly reconciliation pack published to P08 |
| `M17` §5.5, §12.2 | Claim evidence pack assembly; installed-base and fault reporting to P08 |
| `M45` §7.2, §13 | Calibration evidence is what a brand auditor examining a rejected claim asks for |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Claim receipt with the complete evidence pack attached, per claim |
| 2 | Claim decision: approve, part-approve, reject with reason, or request more information |
| 3 | Bulk claim action across a filtered set |
| 4 | Evidence inspection: photographs, diagnostic reports, parts replaced with serials, technician certification, purchase proof |
| 5 | Claim pipeline visibility: submitted, under review, approved, paid, with ageing |
| 6 | Reconciliation: remittance advice upload and difference resolution against submitted claims |
| 7 | Consignment stock position: supplied, consumed on warranty, returned, damaged, outstanding |
| 8 | Monthly consignment reconciliation pack with acknowledgement |
| 9 | Replenishment request and defective-return notification for consignment parts |
| 10 | Rate card publication and versioning: labour rates, parts pricing, claim rules |
| 11 | Service performance on the brand's own products: volume, TAT, first-time fix, rework, CSAT |
| 12 | **Cohort reliability analysis**: failure mode incidence by model, age band and usage cohort, with population size |
| 13 | Quality concern raising, CAPA response visibility and partner audit scheduling with evidence access |
| 14 | Technician certification status for technicians authorised on the brand |
| 15 | Bulletins, technical notices and recall notifications from the brand to 1000FiX |
| 16 | Document repository: authorisation agreement, technical bulletins, rate card history |
| 17 | English-primary interface with Bengali available |
| 18 | Instrumentation of adoption, decision time and evidence completeness |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Claim creation, lifecycle, submission and reconciliation logic** | **M09** Warranty, Protection Plans & Claims | P08 presents a claim and captures a decision; M09 runs the claim |
| **Evidence assembly** | **M17** Asset Registry (§5.5 FR-AST-036) | M17 assembles the pack; P08 displays it |
| **Consignment ledger, ownership-class rules and reconciliation computation** | **M15** Inventory | P08 publishes M15's reconciliation; it computes nothing |
| **Parts vendor transactions — RFQ, PO, invoice, RTV** | **P05** Vendor & Supplier Portal | A brand supplying consignment stock does so under a consignment agreement, not a purchase order. **Where a brand also sells parts commercially, that transaction is P05** |
| **Marketplace sellers** | **P07** | — |
| **Corporate clients** | **P04** | — |
| **Rate card application, pricing and claim valuation** | **M11 / M09** | P08 receives a published rate card; the system applies it |
| **Quality event, root cause and CAPA execution** | **M23** Quality Management | P08 lets a brand raise a concern and see the CAPA response; M23 runs it |
| **Technician certification issuance and assessment** | **M22** Learning & Competency | P08 displays status; M22 certifies |
| **Calibration records and equipment fitness** | **M45** Enterprise Asset & Test Equipment | P08 surfaces calibration evidence during an audit; M45 owns it |
| **Payment execution and settlement** | **M52 / M50** | P08 accepts remittance advice; Finance reconciles and posts |
| **Customer identity and personal data** | **M33** | **A brand partner never sees a customer's identity, contact details or unrelated history** — the hardest boundary in this portal |
| **Individual asset data outside a claim** | **M17** | A brand sees its installed base as **cohort statistics**, never as an addressable list of customers' devices |
| **Identity, session policy and MFA** | **M29** | **PS-01**; MFA required for financial actions |

### 3.3 Shared Concepts

| Concept | P08's Role | Owning Module |
|---|---|---|
| The brand's view of 1000FiX as its service partner | **Owns** — the defining concern of this portal | P08 |
| Warranty claim | Presents with evidence; captures the decision | M09 |
| Claim evidence pack | Displays | M17 assembles |
| Consignment position and reconciliation | Publishes | M15 |
| Rate card | Receives and versions | M11 / M09 |
| Service performance on the brand's products | Presents, brand-scoped | M25 / M62 |
| Cohort reliability | Presents, anonymised | M17 / M23 / M25 |
| Technician certification on the brand | Displays | M22 |
| Quality concern and CAPA | Raises; displays response | M23 |
| Calibration evidence during audit | Surfaces | M45 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **OEM dealer and service-partner claim portals (automotive, equipment)** | **Guided submission with real-time validation at every step**; parts and labour line items validated against contract terms instantly; self-service portals letting partners register products, submit claims and track resolution without calling; live claim status feeds to partner dashboards | **Validation against the brand's own rules before submission is the single most influential external reference for P08.** A claim that cannot pass the brand's stated rules should never reach the brand's queue — it should be corrected while the evidence is fresh and the technician is reachable. This is the mechanism behind the 92% approval-rate target | Their dealer-network scale apparatus. 17 brands and 50–150 users does not need a dealer management system |
| **OEM warranty management practice (WarrantyHub, OnPoint, ServiceCPQ)** | Claim submission → validation → authorisation → repair → reimbursement; document analysis and fraud signals; line-item adjudication recommendations | **The claim lifecycle and line-item adjudication**, including part-approval, which is what avoids the all-or-nothing rejection that destroys a claim's value | AI fraud scoring of the Company's own claims. Building a system that treats 1000FiX's submissions as suspect is the wrong posture; the brand may apply its own scoring at its end |
| **Automotive dealer claim exception handling (DICE-style)** | A structured channel for back-and-forth on claim exceptions, replacing email threads with an assignable, tracked exchange | **Request-more-information as a first-class claim state with a clock**, rather than an email. This is where claim age accumulates, and making it a tracked state is what brings decision time under 10 days | — |
| **Consignment inventory practice** | Consignment stock physically held by the partner, owned by the principal, reconciled periodically, with ownership transferring at consumption | **Publishing the reconciliation to the brand, with acknowledgement.** M15 computes it; P08 is where the brand sees and accepts it. A consignment position the owner cannot see is a governance failure on both sides | — |
| **Brand audit practice** | Periodic partner audits examining process, competence, equipment and records | **Audit-mode evidence access**: during a scheduled audit window, the brand's auditor gets structured access to calibration records, certifications and claim evidence for the audit scope. This converts a two-week compilation exercise into a portal session | Standing unrestricted access to internal records outside an audit window |
| **Installed-base reliability reporting** | Failure mode incidence by model and age, with population size as the denominator | **Cohort reliability analysis as a partnership asset**, anonymised so no customer is identifiable. 1000FiX holds fault history most brands cannot easily obtain in this market | Any presentation that would let a brand identify or contact a customer |

**Design position.** Five deliberate differences from the benchmark.

First, **a claim reaches the brand complete or not at all.** M17 assembles the evidence pack and
M09 validates against the brand's published rules before submission. A claim that would be
rejected for missing evidence is held internally and corrected, not submitted and rejected.
This inverts the usual dynamic: the approval rate becomes a measure of the Company's discipline
rather than the brand's generosity.

Second, **no customer is identifiable to a brand, ever.** This is the hardest and most
important boundary. A brand sees a claim's device, fault, parts and evidence. It does not see
the customer's name, contact details, address, other devices or unrelated history. Cohort
analytics are aggregated with a minimum population threshold. The commercial temptation to
share more is real; the customer relationship belongs to 1000FiX, and the privacy position is
what the ISMS claim rests on.

Third, **the reconciliation is published, not requested.** Consignment position, claim
reconciliation and service performance are pushed to the brand on a cycle. A partner who
publishes their own performance — including the parts they broke and the claims they got wrong
— is in a materially stronger position at authorisation renewal than one who waits to be asked.

Fourth, **audit mode is a defined, time-boxed state.** Rather than granting standing access to
records a brand does not need day to day, an audit window opens structured access to the audit
scope, logs every access, and closes. This is both better governance and a better audit
experience.

Fifth, **the portal is designed for the brand's administrator, not for 1000FiX.** The success
measure is claims decided quickly, which means the decision surface must be fast, bulk-capable
and complete enough that the administrator never needs to email. Every request for more
information is a design failure to be instrumented and removed.

---

## 5. Capability Areas & Functions

### 5.1 Claims: Receipt, Evidence & Decision

| FR ID | Feature | Function — "The portal shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-229 | Claim queue | Present the brand's claim queue with filter by status, model, fault, value, branch and age, and a default view ordered by ageing | **P0** | L5 |
| FR-POR-230 | Claim detail with evidence | Present each claim with the complete evidence pack — device identity and serial, purchase proof, fault history, diagnostic report, before and after photographs, parts replaced with serials, labour, and the technician's certification for that brand (BR-CWM-008) | **P0** | L5 |
| FR-POR-231 | Parts provenance | Show, for every part claimed, its serial, its source, and whether it was drawn from the brand's own consignment stock or purchased | **P0** | L5 |
| FR-POR-232 | **Decision** | Capture approve, part-approve at line level, reject with a reason from the brand's own reason set, or request more information — each with a timestamp and the deciding user (BR-CWM-007) | **P0** | L5 |
| FR-POR-233 | Request more information | Treat a request for more information as a first-class claim state with a clock, an assignable owner at 1000FiX, and a tracked response — never an email | **P0** | L5 |
| FR-POR-234 | Bulk action | Approve or reject a filtered set of claims in one action, with a confirmation showing exactly what will change | P1 | L5 |
| FR-POR-235 | Claim history | Show every state change, decision, comment and information exchange on a claim, attributable and timestamped | **P0** | L5 |
| FR-POR-236 | Claim pipeline | Present submitted, under review, approved, rejected and paid volumes and values with ageing, by period and model | **P0** | L5 |

### 5.2 Reconciliation & Settlement

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-237 | Claim reconciliation | Present submitted, approved and paid claims for a period, reconcilable line by line against the brand's own records (BR-CWM-009) | **P0** | L5 |
| FR-POR-238 | Remittance advice upload | Accept a remittance advice from the brand, match it automatically against approved claims, and present unmatched lines from both sides | **P0** | L5 |
| FR-POR-239 | Difference resolution | Provide a tracked exchange to resolve reconciliation differences, with the resolution recorded against the affected claims | P1 | L5 |
| FR-POR-240 | Ageing and realisation | Show days from service to reimbursement, and claim value realised against value submitted, by period and model | P1 | L5 |

### 5.3 Consignment Parts

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-241 | Consignment position | Present the brand's parts held in 1000FiX custody: received, consumed on warranty, returned, damaged and outstanding, by part and location (M15 FR-INV-012) | **P0** | L5 |
| FR-POR-242 | **Monthly reconciliation pack** | Publish M15's monthly consignment reconciliation — opening, received, consumed, returned, closing, variance — and capture the brand's acknowledgement (M15 FR-INV-014) | **P0** | L5 |
| FR-POR-243 | Consumption detail | Decompose any consumption figure to the claims and jobs that consumed it, with serials | P1 | L5 |
| FR-POR-244 | Replenishment request | Accept a replenishment request from 1000FiX and let the brand confirm, part-confirm or decline with an expected date | P1 | L5 |
| FR-POR-245 | Defective returns | Notify the brand of defective consignment parts, and track the return to credit or replacement | P1 | L5 |

### 5.4 Rate Cards, Performance & Reliability

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-246 | Rate card publication | Allow the brand to publish and version labour rates, parts pricing and claim rules, with an effective date, and show which version governed any given claim | **P0** | L5 |
| FR-POR-247 | Claim rules | Allow the brand to state the rules a claim must satisfy — required evidence, labour time allowances, part eligibility — which 1000FiX validates against **before** submission | **P0** | L5 |
| FR-POR-248 | Service performance | Present 1000FiX's service performance on the brand's products: volume, turnaround time, first-time fix, rework rate and CSAT, by period and branch, brand-scoped | **P0** | L5 |
| FR-POR-249 | **Cohort reliability analysis** | Present failure mode incidence by model, age band and usage cohort **with the population size as denominator**, aggregated above a minimum population threshold so no individual customer or device is identifiable (M48 FR-IOT-045) | P1 | L5 |
| FR-POR-250 | Export | Export claim, reconciliation, consignment and performance data within the brand's own scope, logged | P1 | L5 |

### 5.5 Quality, Certification & Communication

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-251 | Quality concern and CAPA | Allow the brand to raise a quality concern against a claim, a model or a process, and show the M23 CAPA response and its closure | P1 | L5 |
| FR-POR-252 | **Audit mode** | Support a scheduled partner audit as a time-boxed window granting structured access to the audit scope — calibration records (M45), technician certifications (M22), claim evidence and process records — with every access logged, and closing automatically at the window's end | P1 | L5 |
| FR-POR-253 | Technician certification | Show the certification status and expiry of technicians authorised on the brand, and flag any expiring within the horizon (BR-HRM-002) | P1 | L5 |
| FR-POR-254 | Bulletins and recalls | Accept technical bulletins, service notices and **recall notifications** from the brand, route them to M23 and M17, and show 1000FiX's acknowledgement and execution status | **P0** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No authoritative state** | P08 persists no business object (`04-00` §1) |
| T-02 | **Brand isolation** | Every query is scoped to the authenticated brand. A brand never sees another brand's claims, consignment, rates, performance or reliability data |
| T-03 | **Customer anonymity** | **No customer identity, contact detail, address or unrelated device history appears in any P08 payload, under any path.** Tested as the portal's highest-severity control |
| T-04 | **Cohort minimum population** | Reliability analytics are suppressed below a configured minimum population, so a cohort cannot resolve to an individual device or customer |
| T-05 | **Evidence completeness at submission** | A claim is submitted only when M17's evidence pack is complete against the brand's published rules; incomplete claims are held internally in P03, not submitted |
| T-06 | **Rate card versioning** | Every claim records the rate card version that governed it; a rate change never retroactively alters a decided claim |
| T-07 | **Reconciliation matching** | Remittance advice matching runs server-side against approved claims, presenting unmatched lines from both sides rather than silently absorbing a difference |
| T-08 | **Audit-mode access control** | An audit window is a time-boxed grant with an explicit scope; every record access within it is logged with user, record and timestamp, and the grant expires automatically |
| T-09 | **MFA on financial actions** | MFA required for claim approval above a value threshold, bulk approval, remittance upload and rate card publication (`05-04` §1) |
| T-10 | **Bulk action safety** | A bulk decision shows exactly which claims and what total value will change, and is logged as a single attributable action |
| T-11 | **All traffic through the gateway** | Every call routes through M28 with per-brand credentials and rate limits (**PS-02**) |
| T-12 | **No client-side business logic** | Claim value, rate application and reconciliation matching are computed by their owning module (**PS-11**) |
| T-13 | **Document integrity** | Evidence documents are served as rendered PDF/A with verifiable references; remittance advices are stored with a content hash |
| T-14 | **Performance** | A claim with its full evidence pack loads in ≤ 3 seconds; a 500-claim queue filters in ≤ 2 seconds |
| T-15 | **Language** | English primary with Bengali available — the inverse of the customer-facing default, reflecting the audience (**PS-03**) |
| T-16 | **Accessibility and responsiveness** | WCAG 2.1 AA; usable from 320 px upward, design centre a desktop browser (**PS-04, PS-05**) |
| T-17 | **Design system** | Shared component library with P01, P04, P07, P10 and P12 (**PS-06**) |
| T-18 | **Graceful degradation** | Where a backing module is unavailable, the capability is disabled with an explanation and a named 1000FiX contact (**PS-09**) |
| T-19 | **Instrumentation** | Adoption, decision time, information-request rate and evidence completeness instrumented to M25 (**PS-10**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Actor

| Actor | Today | With P08 |
|---|---|---|
| **Brand warranty administrator** | Receives claims by email, requests missing evidence, waits | Opens a queue where every claim is already complete, and decides |
| **Brand quality engineer** | Has no visibility of failure patterns in this market | Sees cohort reliability by model and age band across a large installed base |
| **Brand parts manager** | Takes the partner's word on consignment consumption | Sees the position and acknowledges a monthly reconciliation |
| **Brand auditor** | Requests records and waits two weeks for a compilation | Opens an audit window and inspects calibration, certification and evidence directly |
| **1000FiX warranty claims officer** | Chases evidence, then chases decisions, by email | Submits complete claims and works only genuine exceptions |
| **1000FiX quality manager** | Learns of a brand concern through an account conversation | Receives it as a tracked concern with a CAPA response path |
| **1000FiX finance** | Reconciles remittances against a spreadsheet of claims | Uploads the advice; unmatched lines are presented from both sides |
| **1000FiX CCO** | Argues the partnership's value from assertion | Shows performance, reliability data and reconciliation discipline |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Warranty revenue recovery** | Complete claims submitted, decided faster, rejected less often, reconciled cleanly | The delivery surface for the **BDT 100 lac/year** warranty recovery attributed to M09 in Scope Charter §6.2 — **the largest single benefit line in the programme** |
| **Claim decision time** | Evidence complete on arrival; information requests as tracked states rather than emails | `04-00` target: **decision time < 10 days**. Each day removed is working capital released |
| **Claim approval rate** | Validation against the brand's published rules before submission | `04-00` target: **approval rate > 92%**. Every rejected claim is work performed and not paid for |
| **Reimbursement cycle** | Reconciliation and remittance matching in one place | `04-00` target: **days from service to reimbursement < 45**, directly improving cash conversion |
| **Claim leakage prevention** | Claims that would have been abandoned in an email thread are visible, aged and worked | Supports KPI-038 (warranty leakage < 2%) and KPI-041 (claims with complete evidence 98%) |
| **Consignment integrity** | Monthly reconciliation published and acknowledged by the brand | Protects M15's consignment control and, with it, the partnership. A consignment dispute is an authorisation risk |
| **Authorisation retention** | Audit-ready evidence, published performance and reconciliation discipline | **The dominant benefit.** A single lost brand authorisation would exceed the entire portal suite's cost. 17+ authorisations are the business's structural asset |
| **Administrative labour** | Email threads replaced by structured exchange on both sides | Contributes to the **BDT 62 lac/year** administrative saving |
| **Commercial position** | Reliability data no competitor in this market can produce | Enabling; changes the terms on which authorisation and rate cards are negotiated |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Customer privacy preserved under commercial pressure** | A brand partner is a powerful counterparty who would find customer data valuable. Holding that boundary — no identity, no contact, no addressable list — is what makes the ISMS claim credible and the customer relationship the Company's own |
| **Audit readiness as a standing state** | Calibration (M45), certification (M22) and evidence (M17) presented on demand rather than compiled on request |
| **Partnership transparency** | Publishing performance including failures is what makes the good numbers believed |
| **ISO 9001 alignment** | Traceability of parts to outcomes and instrument to measurement, presented to the party most entitled to ask |
| **Recall execution evidence** | A recall notification routed to M17 and executed across the installed base, with the execution status visible to the brand, is a safety and liability capability |
| **Market intelligence as a shared asset** | Reliability insight benefits both parties and deepens a relationship that is otherwise transactional |
| **Expansion readiness** | An eighteenth brand is an onboarding, not a build |

---

## 8. Journeys & State Models

### 8.1 The Claim Journey — where the value is won or lost

```
   SERVICE ORDER CLOSED as warranty type (M01)
        │
   ┌────▼──────────────────────────────────────┐
   │  M09 CREATES CLAIM (BR-CWM-006)           │
   └────┬──────────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────────┐
   │  M17 ASSEMBLES EVIDENCE PACK (FR-AST-036) │
   │   identity · purchase proof · fault history│
   │   diagnostics · photos · part serials ·    │
   │   technician certification                 │
   └────┬──────────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────────┐
   │  VALIDATE AGAINST THE BRAND'S PUBLISHED    │
   │  CLAIM RULES (FR-POR-247)                  │
   └────┬─────────────────────────┬────────────┘
        │ complete                │ incomplete
        │                    ┌────▼──────────────────────┐
        │                    │ HELD INTERNALLY in P03    │
        │                    │ worked by the claims       │
        │                    │ officer — NOT submitted    │
        │                    └───────────────────────────┘
   ┌────▼──────────────┐
   │  SUBMITTED → P08  │  the brand sees a complete claim
   └────┬──────────────┘
        │
   ┌────▼──────────────┐
   │  UNDER REVIEW     │  ◄─── ageing clock runs; target < 10 days
   └──┬────┬────┬───┬──┘
      │    │    │   │ more information requested
      │    │    │   └────────────► ┌─────────────────────────┐
      │    │    │                  │ INFORMATION REQUESTED   │
      │    │    │                  │ tracked state · clock ·  │
      │    │    │                  │ owner at 1000FiX         │
      │    │    │                  └──────────┬──────────────┘
      │    │    │                             │ responded
      │    │    │◄────────────────────────────┘
      │    │    │
      │    │    │ rejected (reason from the brand's set)
      │    │    └──────────► REJECTED ──► M09 works the reason;
      │    │                              resubmit if remediable
      │    │ part-approved (line level)
      │    └──────────► PART-APPROVED
      │ approved
   ┌──▼────────┐
   │ APPROVED  │
   └──┬────────┘
      │
   ┌──▼──────────────────┐
   │  BILLED (M09 → M52) │
   └──┬──────────────────┘
      │  remittance advice uploaded by the brand
   ┌──▼──────────────────┐
   │  RECONCILED → PAID  │  target: service to reimbursement < 45 days
   └─────────────────────┘
```

| State | Owner | The design intent |
|---|---|---|
| Held internally | M09 / P03 | **A claim that would be rejected never reaches the brand.** This is what produces a > 92% approval rate |
| Submitted | M09 | Complete on arrival |
| Under review | Brand (P08) | Ageing measured; the decision-time KPI runs here |
| Information requested | **Tracked state, both sides** | The single largest source of claim ageing, made visible and assignable |
| Rejected | Brand | Reason from the brand's own set, so M09 can work it |
| Approved / part-approved | Brand | Line-level part-approval avoids all-or-nothing loss |
| Reconciled | M52 with brand remittance | Unmatched lines shown from both sides |

### 8.2 Audit Mode

```
   BRAND SCHEDULES AN AUDIT (P08)
        │  scope · period · records classes
   ┌────▼───────────────────────────────────┐
   │  1000FiX ACCEPTS AND CONFIRMS WINDOW   │  Quality Manager
   └────┬───────────────────────────────────┘
        │
   ┌────▼───────────────────────────────────────────┐
   │  AUDIT WINDOW OPEN (time-boxed)                 │
   │   structured access within scope to:            │
   │    ▸ claim evidence for the audit period        │
   │    ▸ calibration records (M45)                  │
   │    ▸ technician certifications (M22)            │
   │    ▸ process and QC records (M23)               │
   │   ✖ still NO customer identity or contact data  │
   │   ▸ every access logged: user · record · time   │
   └────┬───────────────────────────────────────────┘
        │ window closes automatically
   ┌────▼───────────────────────────────────┐
   │  ACCESS REVOKED · access log available  │
   │  to both parties · findings raised as   │
   │  quality concerns → M23 CAPA            │
   └────────────────────────────────────────┘
```

> **The customer-anonymity boundary holds even in audit mode.** An auditor examining a claim
> sees the device, the fault, the parts, the technician and the evidence. They do not see who
> owns the device. If a brand requires customer contact for a safety recall, that is executed by
> 1000FiX through M27 on the brand's instruction — never by handing over a list.

---

## 9. Portal Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P08-01 | **No customer identity, contact detail, address or unrelated device history appears in any P08 payload, under any path, including audit mode** | **H** | CTO / Legal |
| PRU-P08-02 | A brand may access only its own claims, consignment, rates, performance and reliability data | **H** | CTO |
| PRU-P08-03 | Cohort reliability analytics are suppressed below the configured minimum population | **H** | CTO / Legal |
| PRU-P08-04 | A claim is submitted only when its evidence pack is complete against the brand's published rules; incomplete claims are held internally | **H** | Warranty Claims Officer |
| PRU-P08-05 | A request for more information is a tracked state with a clock and a named owner, never an email | **C** | Chief Commercial Officer |
| PRU-P08-06 | Every claim records the rate card version that governed it; a rate change never retroactively alters a decided claim | **H** | CFO |
| PRU-P08-07 | A rejection carries a reason from the brand's own published reason set | **H** | Chief Commercial Officer |
| PRU-P08-08 | Part-approval operates at line level; a claim is never all-or-nothing where lines are separable | **C** | CFO |
| PRU-P08-09 | MFA is required for claim approval above the value threshold, bulk approval, remittance upload and rate card publication | **H** | CFO |
| PRU-P08-10 | A bulk decision shows exactly which claims and what total value will change before executing, and is logged as one attributable action | **H** | CFO |
| PRU-P08-11 | The monthly consignment reconciliation is published to the brand and its acknowledgement recorded | **H** | Warehouse Manager |
| PRU-P08-12 | A reconciliation difference is presented from both sides and resolved through a tracked exchange; it is never silently absorbed | **H** | CFO |
| PRU-P08-13 | An audit window is time-boxed, scoped, fully logged, and expires automatically | **H** | Quality Manager |
| PRU-P08-14 | A recall notification is routed to M23 and M17 and its execution status is published back to the brand | **H** | Quality Manager |
| PRU-P08-15 | Claim value, rate application and reconciliation matching are computed by their owning module, never client-side (**PS-11**) | **H** | CTO |
| PRU-P08-16 | Every export is scoped to the brand's own data, logged and attributed | **H** | CTO |
| PRU-P08-17 | Where a brand also supplies parts commercially, that transaction is conducted in **P05**, not P08 | **C** | Procurement Manager |

---

## 10. Data, Caching & State Model

### 10.1 What P08 Holds

| Object | Purpose | Ownership |
|---|---|---|
| Brand portal user accounts and scoping | Which people at a brand may do what | **P08**, identity in M29 |
| **Audit window grants** | Scope, period, expiry and the access log | **P08** |
| Saved views and filters | Per brand user | **P08** |
| Draft decisions and bulk selections | Recovery of an interrupted action | **P08**, transient |
| Session and preference | Language, landing view | M29 / P08 |

### 10.2 Never Held

| Item | Reason |
|---|---|
| **Any customer identity, contact or address** | PRU-P08-01 — the portal's defining constraint |
| Any business object — claim, consignment, invoice | `04-00` §1 |
| Another brand's data of any kind | PRU-P08-02 |
| 1000FiX internal cost, margin or unrelated commercial data | External party isolation (`05-04` §8) |
| Claim valuation or reconciliation logic | PRU-P08-15 |

### 10.3 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.warranty.claim`, lifecycle, reconciliation | **M09** | Read; submit decision |
| Claim evidence pack | **M17** (§5.5 FR-AST-036) | Read |
| `fix.part.genealogy` — serials on claimed parts | M17 / M15 | Read |
| `fix.consignment.balance`, `fix.consignment.reconciliation` | **M15** | Read; acknowledge |
| `fix.stock.rtv` — defective consignment returns | M15 | Read |
| Rate card, claim rules | M11 / **M09** | Publish; version |
| Brand-scoped service performance | M25 / M62 | Read |
| Cohort reliability (anonymised, above threshold) | M17 / M23 / **M48** | Read |
| `fix.competency`, brand authorisation status | **M22** | Read |
| `fix.calibration.record` *(audit mode only)* | **M45** | Read within an open audit window |
| `fix.quality.event`, `fix.capa` | **M23** | Raise; read response |
| `fix.vendor.invoice`, remittance | M52 | Upload advice; read match |
| `fix.document` — agreements, bulletins, rate card history | M24 | Read; upload bulletins |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P08-01 | Claim validated complete against the brand's rules | Submit to the brand's queue and notify the brand's administrator | Claim held; 1000FiX notified |
| AUT-P08-02 | Claim evidence incomplete | Hold internally in P03 with the missing item named, assigned to the claims officer — **do not submit** | Hard hold |
| AUT-P08-03 | Claim unactioned beyond the ageing threshold | Notify the brand administrator, then escalate through 1000FiX's account contact | Escalate; ageing published |
| AUT-P08-04 | Brand requests more information | Open the tracked state with a clock, assign an owner at 1000FiX, and notify them | State remains open and reportable |
| AUT-P08-05 | Information supplied | Return the claim to under review, stopping the information clock | Retry notification |
| AUT-P08-06 | Claim approved, part-approved or rejected | Notify M09, record the rate card version applied, and where rejected route the reason to the claims officer | Decision recorded; notification retried |
| AUT-P08-07 | Month end | Publish M15's consignment reconciliation pack to the brand and request acknowledgement (M15 AUT-INV-07) | Escalate to the Warehouse Manager |
| AUT-P08-08 | Consignment stock consumed on a warranty job | Update the brand's position in near real time (M15 AUT-INV-06) | Update on next cycle |
| AUT-P08-09 | Remittance advice uploaded | Match against approved claims and present unmatched lines from both sides | Present unmatched; never auto-absorb |
| AUT-P08-10 | Rate card published by the brand | Version it with an effective date, notify M09 and M11, and apply it to claims from that date forward only | Publication held; both parties notified |
| AUT-P08-11 | Brand raises a quality concern | Create the quality event in M23, assign an owner and notify the Quality Manager | Escalate |
| AUT-P08-12 | Brand issues a recall notification | Route to M17 for installed-base identification and M23 for execution, and publish execution status back | Escalate immediately; recalls are never queued |
| AUT-P08-13 | Audit window scheduled and accepted | Open the time-boxed scoped grant, notify the audit contacts, and start the access log | Window stays closed pending acceptance |
| AUT-P08-14 | Audit window expires | Revoke access automatically and publish the access log to both parties | Hard revoke |
| AUT-P08-15 | A technician's brand certification approaches expiry | Notify 1000FiX and show the status to the brand | Notify only |

---

## 12. Module Interfaces

### 12.1 Modules P08 Consumes

| Module | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, MFA on financial actions, brand scoping | OIDC via gateway |
| M28 Integration Platform | Every call; per-brand rate limits | Gateway |
| **M09 Warranty & Claims** | Claim, lifecycle, valuation, reconciliation | REST + events |
| **M17 Asset Registry** | Claim evidence pack, part genealogy, installed-base cohorts | REST |
| **M15 Inventory** | Consignment position, monthly reconciliation, defective returns | REST + events |
| M11 Pricing | Rate card structure and application | REST |
| M22 Competency | Brand-specific technician certification and expiry | REST |
| M23 Quality | Quality events, CAPA responses, recall execution | REST + events |
| M45 Enterprise Assets | Calibration records — **audit mode only** | REST, scoped |
| M52 Accounts Payable | Claim billing and remittance matching | REST |
| M25 / M62 | Brand-scoped performance and cohort analytics | Embedded, scoped |
| M48 IoT & Predictive | Cohort failure-pattern analysis | REST, aggregated |
| M24 Documents | Evidence documents, agreements, bulletins, rate card history | REST |
| M33 Party Master | Brand party identity | REST |
| M65 Localisation | English and Bengali bundles | Build-time + REST |

### 12.2 What P08 Writes Back

| Target | What | Mechanism |
|---|---|---|
| M09 | Claim decisions — approve, part-approve, reject with reason, request information | Command (MFA-gated above threshold) |
| M15 | Consignment reconciliation acknowledgement; replenishment confirmation | Command |
| M11 / M09 | Rate card publication with effective date and version | Command (MFA-gated) |
| M23 | Quality concerns; recall notifications | Command |
| M17 | Recall scope for installed-base identification | Command |
| M52 | Remittance advice with matching result | Command (MFA-gated) |
| M24 | Technical bulletins and service notices | Upload |
| M25 / M62 | Adoption, decision-time and information-request analytics | Event stream |

### 12.3 Events P08 Consumes

| Event | Source | Effect in P08 |
|---|---|---|
| `claim.submitted` | M09 | Add to the brand's queue with its evidence pack |
| `claim.evidence_incomplete` | M17 / M09 | **Suppress submission**; hold internally |
| `stock.consignment_consumed` | M15 | Update the brand's consignment position |
| `stock.consignment_reconciled` | M15 | Publish the monthly pack; request acknowledgement |
| `stock.rtv_raised` (consignment) | M15 | Notify the brand of a defective return |
| `capa.closed` | M23 | Show the response against the brand's concern |
| `recall.execution_updated` | M17 / M23 | Publish execution status |
| `certification.expiring` | M22 | Show against the technician list |
| `payment.received` | M52 | Update reconciliation and realisation |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P08-01 | Brand warranty systems (Dell, HP, Lenovo, Acer and others, where an interface exists) | Bidirectional | Claim submission and decision exchange by API where the brand supports it; portal entry otherwise. **Matches M17 INT-AST-01 and M15 INT-INV-01** |
| INT-P08-02 | Brand parts-ordering portals | Outbound | Consignment replenishment where the brand mandates its own channel |
| INT-P08-03 | Email | Outbound | Notification to brand administrators; via M27 |
| INT-P08-04 | Brand SSO, where a brand requires federated access | Inbound | Federated authentication; via M29 |

### 12.5 API Surface Consumed

| Endpoint | Method | Purpose | Owner |
|---|---|---|---|
| `/api/v1/warranty/claims` | GET | Brand-scoped claim queue with filters | M09 |
| `/api/v1/warranty/claims/{id}` | GET | Claim with complete evidence pack | M09 / M17 |
| `/api/v1/warranty/claims/{id}/decision` | POST | Approve, part-approve, reject, request information | M09 |
| `/api/v1/warranty/claims/bulk-decision` | POST | Bulk decision with confirmation | M09 |
| `/api/v1/warranty/reconciliation` | GET | Period reconciliation, line by line | M09 / M52 |
| `/api/v1/warranty/remittance` | POST | Upload remittance advice; matching result | M52 |
| `/api/v1/consignment/{brand}/balance` | GET | Consignment position by part and location | **M15** |
| `/api/v1/consignment/{brand}/reconciliation` | GET/POST | Monthly pack; acknowledgement | **M15** |
| `/api/v1/brands/{id}/rate-card` | POST/GET | Publish and version rates and claim rules | M11 / M09 |
| `/api/v1/brands/{id}/performance` | GET | Brand-scoped service performance | M25 |
| `/api/v1/brands/{id}/reliability` | GET | Cohort failure analysis, above minimum population | M17 / M48 |
| `/api/v1/brands/{id}/certifications` | GET | Technicians certified on the brand | M22 |
| `/api/v1/brands/{id}/audit-window` | POST/GET | Schedule, open, access, close, log | **P08** |
| `/api/v1/quality/concerns` | POST/GET | Raise a concern; read the CAPA response | M23 |
| `/api/v1/brands/{id}/bulletins` | POST | Technical bulletin and recall notification | M24 / M23 |

---

## 13. Roles & Permissions

**R38 External Party — Brand Partner sub-class** is the only role with P08 access
(`05-04` §2).

| Brand-side role | Access | Scope | MFA |
|---|---|---|---|
| **Warranty administrator** | R U A | Own brand's claims — decide, request information, bulk action | **Required above the value threshold** |
| **Parts manager** | R U | Own brand's consignment position, reconciliation acknowledgement, replenishment | Required for acknowledgement |
| **Quality engineer** | R U | Own brand's performance, reliability cohorts, quality concerns, CAPA responses, bulletins and recalls | Optional |
| **Auditor** | R | **Audit-window scope only**, time-boxed, fully logged | **Required** |
| **Commercial / account** | R U | Rate card publication and versioning | **Required** |

> **Internal roles that see the brand relationship act in P03:** R28 Warranty Claims Officer
> (Warranty Console), R26 Finance Manager (reconciliation), R32 Quality Manager / ISO Coordinator (concerns,
> CAPA, audits), R17 Inventory Manager (consignment). Per `05-04` §2, R26 and R28 hold P08
> visibility for reconciliation purposes. **No impersonation path exists.**

**Field-level restrictions — the defining control.** Absent from every P08 payload:
**customer name, contact number, email, address, NID, any other device owned by that customer,
and any service history unrelated to the claim.** Also absent: 1000FiX internal cost, margin,
technician personal data beyond certification status, another brand's data, and any commercial
term not part of this brand's agreement.

**Segregation of duties.** A brand user who publishes a rate card may not also approve claims
valued under it above the threshold, where the brand's own governance requires separation —
configurable per brand at onboarding.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Portal claim share** | Claims submitted and decided in-portal versus by email, per brand — the `04-00` KPI | M09, M25 |
| **Decision time** | Submission to decision, per brand, per claim value band — the `04-00` KPI | M09, M25 |
| **Approval rate** | Approved, part-approved and rejected, with rejection reasons by frequency — the `04-00` KPI | M09, M25 |
| **Information requests** | Requests per 100 claims, by missing item — **each one is a design failure to be removed** | M17, M09 |
| **Reimbursement cycle** | Service date to reimbursement, per brand — the `04-00` KPI | M52, M25 |
| Evidence completeness | Claims held internally for incomplete evidence, by missing item | M17, M09 |
| Consignment reconciliation | Packs published, acknowledged, disputed; variance value | M15 |
| Reconciliation matching | Remittance lines matched automatically versus manually resolved | M52 |
| Audit activity | Windows opened, records accessed, findings raised | M23, Quality |
| Brand engagement | Logins, performance views, reliability views per brand — a partnership health signal | M25, CCO |
| Bulk action usage | Bulk decisions, claim counts and values | M09 |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| — | **Claims submitted through the portal (vs email)** | 0% | 65% | **> 80%** |
| — | **Average claim decision time** | unmeasured | < 15 days | **< 10 days** |
| — | **Claim approval rate** | unmeasured | 88% | **> 92%** |
| — | **Brand partner satisfaction** | unmeasured | > 4.2/5 | **> 4.5/5** |
| — | **Days from service to reimbursement** | unmeasured | < 60 | **< 45** |
| — | Information requests per 100 claims | unmeasured | < 12 | **< 4** |
| — | Claims held internally for incomplete evidence | unmeasured | < 8% | **< 2%** |
| — | Consignment reconciliation packs acknowledged by the brand | 0% | 80% | **> 95%** |
| — | Consignment reconciliation variance | untracked | < 1% | **0%** |
| — | Remittance lines matched automatically | 0% | 85% | **> 95%** |
| — | Brands actively using the portal | 0 | 10 of 17+ | **> 15 of 17+** |
| — | Audit windows completed in-portal rather than by compilation | 0% | 60% | **> 90%** |
| — | Customer data exposures to a brand partner | n/a | **0** | **0** |
| — | Cross-brand data exposures | n/a | **0** | **0** |
| **KPI-038** *(supported)* | Warranty leakage | unmeasured | < 4% | **< 2%** |
| **KPI-041** *(supported)* | Claims with complete evidence | unmeasured | 92% | **98%** |

> **Register note.** The first five metrics are adopted verbatim from `04-00` §P08. P08 has
> **no KPI-0nn identifiers allocated**; all fourteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action. KPI-038 and KPI-041 are owned by M09.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L5 | **Next.js 15 application** — claim queue and decision surface, evidence viewer, reconciliation, consignment, rate cards, performance and reliability, quality and audit mode | 76% |
| L4 | Shared design system; embedded scoped analytics from P06 | 12% |
| L2 | OCA `portal` and `dms` for document serving | 6% |
| L1 | Odoo `portal` authentication and document routes | 6% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-209** | `p08_brand_portal` — claim queue with evidence viewer and line-level decision, information-request tracked state, bulk action with confirmation, reconciliation and remittance matching, consignment position and monthly acknowledgement, rate card publication and versioning, brand-scoped performance and anonymised cohort reliability, quality concerns and CAPA visibility, **time-boxed audit mode with full access logging**, bulletins and recall routing | Next.js 15 application | 18 PW |

> **CD register.** One ID, **CD-209**, claimed following CD-208 (P07). All CD IDs remain
> provisional pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M09 Warranty & Claims** | The claim itself. **W4 — the binding constraint** |
| **M17 Asset Registry** | Evidence pack assembly (FR-AST-036). **W2** — without it there is nothing to show |
| **M15 Inventory** | Consignment ledger and monthly reconciliation. **W2** |
| M29 Identity & Security | Brand scoping and MFA on financial actions |
| M28 Integration Platform | Gateway with per-brand credentials |
| M11 Pricing | Rate card structure (W3) |
| M52 Accounts Payable | Claim billing and remittance (W3) |
| M23 Quality | Quality events, CAPA and recall execution (W5) — **quality and audit surfaces follow in W5** |
| M22 Competency | Brand certification status (W5) |
| M45 Enterprise Assets | Calibration records for audit mode (W5) — **audit mode completes in W5** |
| M25 / M62 | Brand-scoped analytics (W4) |
| M48 IoT | Cohort reliability enrichment (W8) — the basic cohort analysis ships from M17 fault history in W4 |

**Phasing within the portal.** W4 ships claims with evidence and decision, reconciliation,
consignment position and rate cards. W5 adds quality concerns, certification visibility and full
audit mode. W8 enriches reliability analysis with telemetry.

### 16.4 Brand Onboarding

| Stage | Scope | Wave |
|---|---|---|
| Pilot brands | 3 brands with the highest claim volume, onboarded personally | W4, month 15 |
| Rate card and rules capture | Each brand's claim rules encoded so pre-submission validation is meaningful | W4, per brand |
| Reconciliation walkthrough | First monthly consignment pack walked through with the brand's parts manager | W4–W5, per brand |
| Full network | All 17+ brands | W5–W6 |

> **Onboarding position.** The pre-submission validation (FR-POR-247) is only as good as the
> claim rules each brand supplies. Capturing those rules — required evidence, labour allowances,
> part eligibility — is **the onboarding work**, and a brand onboarded without them gets a
> portal that submits incomplete claims faster. Rules capture is therefore a gate on opening a
> brand's portal access, not a follow-up task.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **No customer identity, contact, address or unrelated device history appears in any P08 response**, including in audit mode and in every export | **Automated payload inspection across every endpoint plus a manual privacy review — the portal's highest-severity control** |
| AC-02 | A brand cannot access another brand's claims, consignment, rates, performance or reliability data | Tenant-isolation penetration test |
| AC-03 | Cohort reliability analytics are suppressed below the configured minimum population | Negative test at and below the threshold |
| AC-04 | A claim with an incomplete evidence pack is held internally and never submitted to a brand | Negative test across every missing-item case |
| AC-05 | A claim opens with its complete evidence pack in under 3 seconds; a 500-claim queue filters in under 2 seconds | Performance test at production volume |
| AC-06 | A request for more information creates a tracked state with a clock and an assigned owner, and stops the review clock | Scripted scenario |
| AC-07 | Line-level part-approval is possible and correctly valued | Scripted multi-line claim |
| AC-08 | Every claim records the rate card version that governed it, and a rate change does not alter a decided claim | Scripted rate change with historical claims |
| AC-09 | MFA is enforced for approval above threshold, bulk approval, remittance upload and rate card publication | Authentication test per action |
| AC-10 | A bulk decision shows the exact claims and total value before executing, and is logged as one attributable action | Scripted bulk decision |
| AC-11 | The monthly consignment reconciliation is published automatically and its acknowledgement recorded | Scripted month-end with M15 |
| AC-12 | Remittance advice matches automatically against approved claims, with unmatched lines shown from both sides | Scripted reconciliation with deliberate differences |
| AC-13 | An audit window opens with the agreed scope, logs every access, and revokes automatically at expiry | Scripted audit window |
| AC-14 | Calibration records and certifications are accessible in audit mode and inaccessible outside it | Negative test outside the window |
| AC-15 | A recall notification routes to M17 and M23 and its execution status is published back to the brand | Scripted recall drill |
| AC-16 | Every export is scoped to the brand's own data, logged and attributed | Export audit |
| AC-17 | Claims submitted in-portal exceed 80% and decision time falls below 10 days | Six consecutive monthly reports |
| AC-18 | Approval rate exceeds 92% and information requests fall below 4 per 100 claims | Six consecutive monthly reports |
| AC-19 | At least three brand partners confirm they can decide a claim without requesting anything further | Signed brand confirmations |
| AC-20 | CCO, Warranty Claims Officer, Quality Manager and three brand administrators sign off UAT | Signed UAT record |

**Definition of done:** the twelve cross-portal standards in `04-00` §3 plus the 20 criteria
above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Which of the 17+ brands will use a portal, and which mandate their own claim system? *(Matches M15 Q-07 and M17 Q-03 — one answer serves all three)* | CCO / Warranty Claims Officer | **W4 minus 4 months** |
| Q-02 | What claim rules does each brand apply — required evidence, labour allowances, part eligibility? Pre-submission validation is worthless without them | Warranty Claims Officer / CCO | **W4 minus 3 months, per brand** |
| Q-03 | Which brands place consignment stock, on what terms, and what reconciliation format does each require? *(Matches M15 Q-01)* | Warehouse Manager / CCO | W4 minus 3 months |
| Q-04 | Is the customer-anonymity position acceptable to every brand, and is it stated in the authorisation agreements? Some brands may expect customer contact for recalls | CCO / Legal | **W4 design** |
| Q-05 | What minimum population threshold applies to cohort reliability analytics before a cohort could resolve to an individual? | Legal / CTO | W4 design |
| Q-06 | Does any brand require federated SSO or IP restriction? | CTO / CCO | W4 build |
| Q-07 | What is the claim approval value threshold above which brand-side MFA is required, and is it per brand? | CFO / CCO | W4 design |
| Q-08 | How is a recall executed to customers — by 1000FiX on the brand's instruction, or does the brand require the customer list? The answer determines whether Q-04's position holds | CCO / Legal / Quality Manager | **W4 design** |
| Q-09 | What audit scope and window duration do brands typically require, and how often? | Quality Manager / CCO | W5 design |
| Q-10 | Is the portal English-only, or do any brand partners' local teams require Bengali? | CCO | W4 design |
| Q-11 | Where a brand both supplies parts commercially and holds consignment, how is the P05/P08 boundary explained to them so they do not have two portals for one relationship? | Procurement Manager / CCO | **W4 design** |
| Q-12 | Is reliability data shared unconditionally, or is it a negotiated element of the authorisation agreement? | CCO | W4 design |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §P08, §1, §3 PS-01…PS-12, §4 ·
`P03_Admin_Operations_Portal.md` (Warranty Console — the internal counterpart) ·
`P04_Corporate_B2B_Portal.md` · `P05_Vendor_and_Supplier_Portal.md` (boundary: commercial parts supply) ·
`P06_Analytics_and_Executive_Dashboard.md` (brand-scoped embedded analytics) ·
`03_Modules/F_Asset_Equipment_and_Facilities/M17_Device_and_Customer_Asset_Registry.md`
§5.5 FR-AST-036 (evidence pack), §12.2, §13 (brand partner sees no customer identity) ·
`03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md`
§5.2 FR-INV-012 and FR-INV-014, §12.2, §14 (brand consignment reconciliation), §12.4 INT-INV-01 ·
`03_Modules/F_Asset_Equipment_and_Facilities/M45_Enterprise_Asset_and_Test_Equipment.md`
§7.2, §13 (external auditor access), §14 (calibration certificate register) ·
`03_Modules/F_Asset_Equipment_and_Facilities/M48_IoT_Telemetry_and_Predictive_Maintenance.md`
§5.5 FR-IOT-045, §13 (brand partner cohort statistics only) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 (AS-14) ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §1 (R38), §2, §5, §8 ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §6.2 (BDT 100 lac)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.1 Portal 5, BR-CWM-006,
BR-CWM-007, BR-CWM-008, BR-CWM-009, BR-FIN-003, BR-BI-010, BR-HRM-002 ·
`1000FiX_Services_Company_Profile.md` §Authorized Service Partnerships (17+ named brands),
§Quality & Certification

**External benchmark**
[Warranty automation for equipment OEMs — guided submission portals with real-time validation and line-item validation against contract terms](https://www.servicecpq.com/warranty-automation/) ·
[OEM warranty management — self-service portals for dealer and service-partner networks](https://warrantyhub.com/manufacturer-warranty-software/) ·
[Mastering the OEM warranty claim process — submission, validation, authorisation, reimbursement](https://www.deteringconsulting.com/blog/oem-warranty-claim-process) ·
[How OEMs streamline warranty claims management](https://www.onpointwarranty.com/about-us/blog/how-can-oems-streamline-warranty-claims-management) ·
[Automotive warranty claims processing and dealer claim exception handling](https://warrantymanaged.com/automotive-warranty-claims-processing/) ·
[OEM authorised repair network — certified repair, claim processing, genuine parts and compliance documentation](https://premierss.com/articles/reverse-logistics-asset-management/oem-authorized-repair-network/) ·
[Consignment inventory accounting and segregation practice](https://www.cleverence.com/articles/for-business/consignment-inventories-4837/)

---

*Portal P08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
