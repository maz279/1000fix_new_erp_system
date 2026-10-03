---
id: FIX-ERP2-P04
portal_id: P04
portal_code: B2B
portal_name: Corporate B2B Portal
type: External Web Portal (multi-user, multi-site organisations)
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

# P04 — Corporate B2B Portal
### Portal Suite · Code `B2B` · Existing (expanded in v2.1)

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P04 |
| **Portal code** | `B2B` |
| **Type** | External web portal for multi-user, multi-site client organisations |
| **Status** | Existing (expanded in v2.1 — asset estate management, managed-services dashboard, SLA credits, compliance evidence and procurement added) |
| **Priority** | **P1** |
| **Delivery wave** | **W4** (Months 14–18) |
| **Users** | Corporate and government client staff — requesters, approvers, finance, administrators |
| **Volume** | **500–2,000 users** across contracted client organisations |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Digital Channels Squad |
| **Technology** | Next.js 15 (React 19), shared design system |
| **Custom development** | `CD-204` |
| **Requirement range** | FR-POR-113 … FR-POR-144 |
| **Requirement count** | **32** *(measured — supersedes the 16 allocation in `05-01` §4)* |
| **Effort estimate** | **26 person-weeks** |
| **Backing modules** | M01, M03, M05, M06, M07, M08, M09, M11, M17, M18, M20, M25, M27, M33, M36, M39, M48, M53, M67 |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M65 Localisation |

---

## 2. Purpose

P04 is **the surface on which the Company's largest and most demanding relationships are
run**. A corporate client with 400 devices across 12 sites does not want a booking form; they
want to see what they own, what it costs them, whether the SLA was met, and whether the invoice
is right — and they want their own people to be able to do that without emailing an account
manager.

Its defining problem is not volume. At 500–2,000 users it is the smallest external audience in
the suite. Its defining problem is **organisational complexity**: many users under one account,
with different authorities, across many sites and departments, against contracts with
entitlements and service credits, billed on a consolidated invoice that several people must
approve.

P04 holds no authoritative state. The estate belongs to M17, the contract to M08, the invoice
to M20, the SLA to M08 and M01. What P04 owns is **the client organisation's view of itself**
and the delegation model that lets their staff act within it.

### Why It Exists

**Corporate revenue depends on visibility that the Company cannot currently provide.** The BRD
commits to corporate accounts with multiple contacts, multiple locations and bulk service
capability (BR-CRM-007). Today that is an account manager, a spreadsheet and an email thread.
A client cannot see their estate, their entitlement consumption or their SLA attainment
without asking, and asking is friction that erodes renewal.

**Bulk operations are the corporate use case.** A retail chain raising 40 service requests
after a power event, an office registering 100 new machines, a bank decommissioning 300 assets
— none of these are 40, 100 or 300 individual bookings. `04-00` requires bulk service request
creation in under 5 minutes and bulk estate upload as first-class capability.

**Invoice disputes destroy corporate margin.** A consolidated monthly invoice covering many
sites, departments and assets is disputed when it cannot be decomposed. `04-00` targets
disputes below 3%, and the mechanism is an itemised breakdown the client can check themselves
before they raise a query.

**Managed services need a client-facing window.** M05 sells monitored, contracted IT services.
A managed-services client who cannot see estate health, open incidents, patch compliance and
SLA attainment is buying a promise. P04 is where that becomes evidence.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §4.1 Portal 4 | "Corporate B2B Portal — 500-2,000 corporate users — AMC management, bulk booking, consolidated invoicing, SLA monitoring" |
| ERP BRD BR-CRM-007 | "Manage corporate/B2B accounts with multiple contacts, multiple locations, and bulk service capabilities" |
| ERP BRD BR-CWM-001 | AMC contracts with covered devices, service inclusions, response SLAs, visit schedule and billing terms |
| ERP BRD BR-CWM-003 | "Track AMC contract utilization: visits used vs. included, parts consumed" |
| ERP BRD BR-CWM-011 | "Define and monitor SLAs per service type, customer tier, and contract with real-time dashboard" |
| ERP BRD BR-SRM-011 | Configurable approval workflows above a cost threshold — the client-side delegation model |
| ERP BRD BR-FIN-008 | Branch-wise and consolidated financial statements — the basis of consolidated invoicing |
| ERP BRD BR-DMS-001 | Centralised repository for compliance documents — the evidence pack |
| Scope Expansion Delta §M17 | "Corporate customer's asset listing… register all 100 devices with serial nos." — the estate requirement |
| `04-00` §P04 | Capability set across ten areas and five KPIs, adopted verbatim |
| `04-00` §3 PS-01…PS-12 | Twelve cross-portal standards, all binding |
| `05-04` §1 R37 | Corporate Portal User with sub-roles Requester, Approver, Finance and Admin; MFA mandatory for Approver and Finance |
| `05-04` §8 | External party access rules — own company only, role-scoped within it |
| `M17` §5.6 | Estate structure, bulk registration, reconciliation and self-service — the module contract behind this portal |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The corporate account surface: many users under one client organisation |
| 2 | Client-side role assignment: requester, approver, finance, administrator |
| 3 | Multi-level approval chains within the client organisation, and delegated authority limits |
| 4 | Site and department structure as the client experiences it |
| 5 | Asset estate view, search, filter and export |
| 6 | Bulk estate upload, update, assignment and retirement |
| 7 | Single and bulk service request raising, with coverage validation before submission |
| 8 | Request tracking, estimate approval within delegated authority, and history |
| 9 | Contract and entitlement visibility, consumption against entitlement, and the scheduled maintenance calendar |
| 10 | Renewal quotation, amendment request and contract document access |
| 11 | Managed-services dashboard: estate health, incidents, alerts, patch compliance |
| 12 | SLA status per request, breach history and service credits earned |
| 13 | Consolidated invoicing with itemised decomposition by site, department and asset |
| 14 | Client-side invoice approval workflow, payment, statements and dispute raising |
| 15 | Scoped analytics on the client's own estate with export |
| 16 | Procurement against agreed pricing: parts, services, rentals, trade-in and decommission projects |
| 17 | Compliance evidence: destruction certificates, disposal certificates, service evidence packs |
| 18 | Support: named account manager, priority contact, knowledge base |
| 19 | Bengali and English, per user preference |
| 20 | Instrumentation of adoption, bulk usage and dispute rate |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Individual retail customer journeys** | **P01** | A corporate user acting personally uses P01; the two audiences and the two delegation models do not mix |
| **Contract terms, entitlement rules, pricing and renewal calculation** | **M08 / M11** | P04 displays and requests; the commercial engine is elsewhere |
| **SLA definition, clock, pause rules and credit calculation** | **M08 / M01** | P04 shows attainment and credits earned; it computes neither |
| **Asset identity, resolution, ownership and estate reconciliation logic** | **M17** | P04 submits estate data; M17 resolves and reconciles it |
| **Service order lifecycle and dispatch** | **M01 / M02** | — |
| **Invoice generation, consolidation logic, tax and credit notes** | **M20 / M51** | P04 presents a rendered invoice and captures approval and dispute |
| **Managed-services monitoring, alerting and remediation** | **M05** (telemetry by **M48**) | P04 is the client window onto M05's service |
| **Data destruction execution and certification** | **M06** | P04 retrieves the certificate |
| **E-waste disposal and recycler compliance** | **M18** | P04 books and retrieves evidence |
| **Corporate rollout and decommission project delivery** | **M67** Project Management | P04 requests a project and shows its status; M67 runs it |
| **Account management, opportunity and QBR content** | **M07** | P04 exposes the client's own data; the relationship is run by a person |
| **Identity, session policy, MFA enforcement** | **M29** | **PS-01**; MFA is mandatory for Approver and Finance sub-roles per `05-04` §1 |
| **Client organisation's own IT systems and asset databases** | The client | P04 accepts an estate file or an API feed; it does not integrate into client systems |

### 3.3 Shared Concepts

| Concept | P04's Role | Owning Module |
|---|---|---|
| The client organisation's view of itself | **Owns** — the defining concern of this portal | P04 |
| Client-side delegation and approval chain | **Owns** the model; M29 enforces the resulting permission | P04 / M29 |
| Asset estate | Displays, submits, requests changes | M17 |
| Contract and entitlement | Displays, requests renewal and amendment | M08 |
| SLA and service credit | Displays | M08 / M01 |
| Service request | Creates in bulk and singly; tracks | M01 |
| Consolidated invoice | Presents, decomposes, captures approval and dispute | M20 |
| Estate health and alerts | Displays | M05 / M48 |
| Compliance certificate | Retrieves | M06 / M18 / M24 |
| Project | Requests; displays status | M67 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **B2B customer portal practice (k-ecommerce, WizCommerce, NAW)** | Repeat ordering, account-specific terms, **multi-user roles and approvals that match how customer teams actually buy**, financial transparency showing credit, outstanding balance and payment history | **Governance that mirrors the client's own organisation is the single most influential external reference for P04.** A corporate portal fails when it assumes one user per account. Requester → approver → finance, with delegated limits, is how corporate clients already work, and the portal must model it rather than flatten it | Full B2B e-commerce catalogue and quote-to-cash complexity; 1000FiX sells service, not a product line |
| **ServiceMax / Salesforce B2B service portals** | Installed base visible to the customer, entitlement validated before a request is accepted, SLA visibility per case | **Coverage validation before submission** — the client is told at the point of raising a request whether it is covered, out of scope or chargeable. This is the mechanism that prevents the two most common corporate disputes: unbilled work performed, and billed work the client believed was included | Their asset-360 depth on the client side; the client needs coverage and health, not full genealogy |
| **B2B invoice and payment portal practice (Gaviti, TransactBridge)** | Centralised invoicing, payment tracking and account management in one self-service surface; itemised history to accelerate collection and reduce disputes | **Invoice decomposition as dispute prevention.** A consolidated invoice a client can break down by site, department and asset — and reconcile against the requests they raised — is disputed far less often than one they must query to understand. This is the direct mechanism behind the < 3% dispute target | Payment-portal-only products; billing here is inseparable from service evidence |
| **SLA transparency practice** | Contractual performance metrics, response times and guarantees published to the customer, with breach history and credits | **Publishing SLA attainment and credits earned, unprompted.** A client who has to ask whether the SLA was met assumes it was not. Publishing it — including breaches and the credits they earned — converts an argument into an accounted fact | Automatic credit application without commercial review; credits are recognised by M53 and confirmed by an account manager |
| **IT managed-services client portals (RMM/PSA vendor portals)** | Estate health, incident history, patch compliance and SLA attainment as a standing client-facing dashboard | **The MSP dashboard as evidence of a service being delivered**, which is what converts a managed-services contract from a promise into a renewable product | Deep remote-control capability on the client side |
| **Government and enterprise procurement practice (Bangladesh context)** | Multi-level approval, documented delegation, auditable trail, formal dispute route | **Auditable delegation.** Government and large corporate clients require that an approval be traceable to a named individual with documented authority. The delegation model is therefore a first-class, exportable record, not a convenience feature | e-GP integration; out of scope for this programme |

**Design position.** Four deliberate differences from the benchmark.

First, **coverage is answered before the request is submitted, not after the work is done.**
The client sees, at the moment of raising, whether an asset is covered, out of scope or
chargeable and at what rate. This is more work to build than accepting everything and sorting
it out in billing, and it removes the largest single source of corporate dispute.

Second, **the delegation model belongs to the client, not to 1000FiX.** A client administrator
defines their own approval chain and limits within the bounds the contract allows. A portal
where 1000FiX must configure each client's internal hierarchy does not scale past a dozen
accounts and puts the Company in the middle of the client's internal politics.

Third, **the estate is reconciled and the client sees the reconciliation.** M17 runs a standing
comparison between the declared estate and the assets actually seen in service, producing gaps
and strays. P04 shows the client that report. Most vendors hide the divergence until renewal;
publishing it makes the true-up conversation factual and, in practice, favourable more often
than not.

Fourth, **SLA breaches are published.** Including the ones that cost the Company money. A
service relationship in which the vendor reports only its successes is not trusted, and the
credits are contractually owed regardless of whether they are surfaced.

---

## 5. Capability Areas & Functions

### 5.1 Account, Users & Delegation

| FR ID | Feature | Function — "The portal shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-113 | Corporate account | Present one account per client organisation with many users, scoped so that no user sees another organisation's data under any condition (`05-04` §8) | **P0** | L5 |
| FR-POR-114 | Client-side roles | Support the requester, approver, finance and administrator sub-roles of R37, assignable by the client's own administrator | **P0** | L5 |
| FR-POR-115 | Delegation and limits | Allow the client administrator to define approval chains and per-user authority limits within the bounds the contract permits, and hold the definition as an auditable, exportable record | **P0** | L5 |
| FR-POR-116 | Approval routing | Route a request or estimate exceeding a user's limit to their defined approver, showing the chain and the current holder to everyone involved (BR-SRM-011) | **P0** | L5 |
| FR-POR-117 | Site and department structure | Present the client's sites and departments as they experience them, aligned to the M17 estate structure, with users scoped to all or some | **P0** | L5 |
| FR-POR-118 | Step-up authentication | Enforce MFA for the approver and finance sub-roles, and step-up for invoice approval and dispute raising, per M29 policy (`05-04` §1) | **P0** | L5 |
| FR-POR-119 | User lifecycle | Allow the client administrator to invite, suspend and remove their own users, with every change logged and visible to 1000FiX | P1 | L5 |

### 5.2 Asset Estate

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-120 | Estate view | Present the full registered estate with model, serial, site, department, assigned user, warranty state, coverage and last service, searchable and filterable | **P0** | L5 |
| FR-POR-121 | Bulk upload | Accept a bulk estate file, validate every line against M17 and M37, report rejects line by line, and commit or reject as a set (M17 FR-AST-039) | **P0** | L5 |
| FR-POR-122 | Estate maintenance | Assign and reassign assets to sites, departments and users, and request additions and retirements, subject to the client's own approval chain | **P0** | L5 |
| FR-POR-123 | **Estate reconciliation** | Present M17's standing reconciliation — declared but never seen, seen but never declared, and movements — with the ability to accept or query each line (M17 FR-AST-040) | P1 | L5 |
| FR-POR-124 | Estate analytics | Report age profile, failure rate by model, cost to serve per asset, downtime and refresh candidates, exportable | P1 | L5 |
| FR-POR-125 | Estate export | Export the estate and its history within the client's own scope, in a format their asset system can consume | P1 | L5 |

### 5.3 Service Requests & SLA

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-126 | Single request | Raise a service request against a specific asset, with fault description, evidence, priority and preferred window | **P0** | L5 |
| FR-POR-127 | **Bulk request** | Raise many requests at once by file upload or multi-select from the estate, completing in under five minutes for a typical batch | **P0** | L5 |
| FR-POR-128 | **Coverage validation** | Validate every request against contract coverage **before submission**, stating clearly whether it is covered, out of scope or chargeable and at what rate | **P0** | L5 |
| FR-POR-129 | Request tracking | Track every request with status, assigned resource, SLA clock and history, filterable by site, department, asset and requester | **P0** | L5 |
| FR-POR-130 | Estimate approval | Present estimates for chargeable work and capture approval within the approver's delegated authority, escalating above it | **P0** | L5 |
| FR-POR-131 | **SLA visibility** | Show real-time SLA status per request, historical attainment by period and site, every breach with its cause, and the service credits earned (BR-CWM-011) | **P0** | L5 |
| FR-POR-132 | Scheduled maintenance | Present the contracted preventive maintenance calendar, allow a visit to be rescheduled within policy, and show completion evidence (BR-CWM-002) | P1 | L5 |

### 5.4 Contracts, Managed Services & Compliance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-133 | Contract view | Present every active contract with covered assets, inclusions, exclusions, response SLAs, term and billing basis, and the contract document (BR-CWM-001) | **P0** | L5 |
| FR-POR-134 | Entitlement consumption | Show consumption against entitlement — visits used against included, parts consumed, value drawn — with a projection to term end (BR-CWM-003) | **P0** | L5 |
| FR-POR-135 | Renewal and amendment | Present a renewal quotation ahead of expiry, and allow an amendment request — assets added, sites changed, coverage varied | P1 | L5 |
| FR-POR-136 | Managed-services dashboard | Present estate health, open incidents, alert history, patch compliance and SLA attainment for clients under an M05 contract | P1 | L5 |
| FR-POR-137 | Service reviews | Publish periodic service review packs and allow the client to schedule a review with their account manager | P2 | L5 |
| FR-POR-138 | Compliance evidence | Retrieve data destruction certificates (M06), e-waste disposal certificates (M18) and service evidence packs on demand | P1 | L5 |

### 5.5 Billing, Procurement & Support

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-139 | Consolidated invoice | Present the consolidated invoice for the billing cycle as a rendered NBR-compliant document with a summary the client can read | **P0** | L5 |
| FR-POR-140 | **Invoice decomposition** | Decompose any consolidated invoice by site, department, asset, request and line, reconcilable against the requests the client raised | **P0** | L5 |
| FR-POR-141 | Invoice approval and payment | Route the invoice through the client's own approval chain, then permit payment by their agreed method, and present statements and ageing | **P0** | L5 |
| FR-POR-142 | Dispute | Raise a dispute against an invoice or a line with a reason and evidence, track it to resolution, and show the credit note when issued | **P0** | L5 |
| FR-POR-143 | Procurement | Order parts, services and rentals against agreed contract pricing, and request trade-in and decommission projects routed to M67 | P2 | L5 |
| FR-POR-144 | Support and knowledge | Present the named account manager with priority contact routes, a scoped knowledge base, and a conversation history with 1000FiX | P1 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No authoritative state** | P04 persists no business object; every object belongs to its module (`04-00` §1) |
| T-02 | **Organisation isolation** | Every query is scoped to the authenticated user's client organisation at the record layer. **A cross-organisation data exposure is the single highest-severity failure this portal can have** and is tested as such |
| T-03 | **Delegation as data, not code** | The client's approval chain and limits are configuration held against the account, evaluated server-side, and exportable as an audit record |
| T-04 | **Bulk integrity** | A bulk estate upload or bulk request submission validates every line and commits or rejects **as a set**, with a line-level reject report. Partial commits are not permitted |
| T-05 | **Bulk performance** | A 500-line estate upload validates and reports in ≤ 60 seconds; a 50-request bulk submission completes in ≤ 5 minutes end to end including coverage validation |
| T-06 | **Coverage validation is synchronous** | Coverage is resolved against M08 and M17 before submission is accepted, never asynchronously after the fact |
| T-07 | **Invoice decomposition performance** | A consolidated invoice of 2,000 lines decomposes and filters in ≤ 3 seconds |
| T-08 | **All traffic through the gateway** | Every call routes through M28 with per-portal credentials and per-organisation rate limits (**PS-02**) |
| T-09 | **No client-side business logic** | Coverage, entitlement, price, SLA and credit values come from their owning module (**PS-11**) |
| T-10 | **MFA and step-up** | MFA mandatory for approver and finance sub-roles; step-up for invoice approval, dispute raising and delegation changes — enforced by M29 (**PS-12**) |
| T-11 | **Export governance** | Every export is scoped, logged and attributed; a client can export only their own data |
| T-12 | **Document integrity** | Invoices, certificates and evidence packs are served as rendered PDF/A with a verifiable reference, never reconstructed in the portal |
| T-13 | **Accessibility and responsiveness** | WCAG 2.1 AA; usable from 320 px upward, though the design centre is a desktop browser (**PS-04, PS-05**) |
| T-14 | **Bengali and English** | Complete in both, per user preference (**PS-03**) |
| T-15 | **Design system** | Shared component library and tokens with P01, P07, P08, P10 and P12 (**PS-06**) |
| T-16 | **Graceful degradation** | Where a backing module is unavailable, the affected capability is disabled with an explanation and a route to the account manager (**PS-09**) |
| T-17 | **Instrumentation** | Adoption, bulk usage, coverage-validation outcomes and dispute rate instrumented to M25 (**PS-10**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Actor

| Actor | Today | With P04 |
|---|---|---|
| **Client IT manager** | Emails the account manager and waits | Sees the estate, raises 40 requests in five minutes, knows what is covered before asking |
| **Client requester** | Phones the hotline like a retail customer | Raises against a specific asset within their delegated authority |
| **Client approver** | Approves by email, with no record of authority | Approves in a chain their own administrator defined, with an auditable trail |
| **Client finance** | Queries a consolidated invoice they cannot decompose | Breaks it down by site, department and asset and reconciles it themselves |
| **Client executive** | Takes the vendor's word on SLA performance | Sees attainment, breaches and credits earned, published |
| **1000FiX account manager** | Spends the week answering status and coverage questions | Spends it on renewal, expansion and service reviews |
| **1000FiX service agent** | Re-keys bulk requests from a spreadsheet | Receives structured, asset-linked, coverage-validated requests |
| **1000FiX finance** | Chases invoice queries by email | Sees disputes raised with a reason and evidence, tracked to resolution |
| **1000FiX MSP team** | Reports estate health in a monthly deck | Publishes it continuously; the deck becomes a conversation |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **AMC/RAMC renewal uplift** | Entitlement consumption, SLA attainment and estate age visible before renewal; the renewal conversation is evidenced rather than negotiated blind | Supports the **BDT 72 lac/year** AMC/RAMC uplift attributed to M08 in Scope Charter §6.2 |
| **Managed services contribution** | The client-facing window that makes an MSP contract a visible, renewable service rather than a promise | Supports the **BDT 95 lac/year** managed-services contribution attributed to M05 |
| **Customer retention — corporate** | Self-service, transparency and auditable delegation reduce the friction that erodes corporate relationships | Contributes to the **BDT 78 lac/year** retention benefit |
| **Invoice dispute reduction** | Decomposable consolidated invoices reconcilable against raised requests | `04-00` target: **disputes < 3%** of consolidated invoices. Each dispute currently costs finance and account-manager time and delays cash |
| **Revenue leakage prevention** | Coverage validated before work is authorised; out-of-scope work is priced, not absorbed | Prevents uncovered work being performed free — the most common corporate margin leak |
| **Account manager capacity** | Status, coverage and invoice queries deflected to self-service | Releases account-manager time to the 8–20 people who hold the corporate relationships |
| **Administrative labour** | Bulk requests arrive structured and asset-linked; no re-keying | Contributes to the **BDT 62 lac/year** administrative saving |
| **Cash collection** | Invoice approval routed through the client's own chain, then paid in-portal | Supports the **BDT 26 lac/year** close and cash-flow benefit |
| **Corporate segment growth** | A portal is a qualification requirement in corporate and government tenders | Enabling; a tender lost for lack of a client portal costs the whole contract |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Auditable delegation** | Government and large corporate clients require that approvals trace to named individuals with documented authority. P04 makes that exportable |
| **Published SLA performance** | Reporting breaches as well as successes is what makes the attainment figure credible when it is good |
| **Compliance evidence on demand** | Data destruction and e-waste certificates retrievable by the client is a regulatory and reputational asset for both parties |
| **Estate truth** | Publishing the reconciliation rather than hiding divergence makes the true-up conversation factual |
| **Tender credibility** | The portal is demonstrable in a bid, which changes how a corporate buyer assesses the Company |
| **Data protection posture** | Strict organisation isolation, tested as the highest-severity failure mode, is what a corporate client's own security review will probe |
| **Expansion readiness** | A multi-entity, multi-currency client structure means a regional client is a configuration case, not a rebuild |

---

## 8. User Journeys & State Models

### 8.1 The Delegated Request Journey

```
   REQUESTER (client staff)
        │ selects asset from the estate
   ┌────▼──────────────────────────────────────────┐
   │  COVERAGE VALIDATION (synchronous, M08 + M17) │
   │   ▸ covered      → no charge shown             │
   │   ▸ chargeable   → rate shown before submit    │
   │   ▸ out of scope → stated, with the reason     │
   └────┬──────────────────────────────────────────┘
        │
   ┌────▼───────────────────────┐
   │  WITHIN REQUESTER'S LIMIT? │
   └────┬──────────────────┬────┘
        │ yes              │ no
        │            ┌─────▼───────────────────────┐
        │            │  APPROVAL CHAIN             │
        │            │  (client-defined, auditable)│
        │            │  approver 1 → approver 2 →  │
        │            │  finance, per limit         │
        │            └─────┬───────────────────────┘
        │                  │ approved
   ┌────▼──────────────────▼────┐
   │  SUBMITTED → M01           │
   └────┬───────────────────────┘
        │
   ┌────▼────────────────────────────────────────┐
   │  TRACKED — status · SLA clock · assigned    │
   │  resource · estimate if chargeable          │
   └────┬────────────────────────────────────────┘
        │
   ┌────▼────────────────────────────────────────┐
   │  COMPLETED → evidence → billed on the        │
   │  consolidated invoice for the cycle          │
   └─────────────────────────────────────────────┘
```

### 8.2 Consolidated Invoice Lifecycle

```
   BILLING CYCLE CLOSES (M20)
        │
   ┌────▼──────────────────────────────────┐
   │  ISSUED — rendered PDF/A + decomposable│
   │  breakdown by site · department ·      │
   │  asset · request · line                │
   └────┬──────────────────────────────────┘
        │
   ┌────▼──────────────────────┐
   │  CLIENT APPROVAL CHAIN     │  (client-defined; step-up auth)
   └────┬──────────────────┬────┘
        │ approved         │ queried
        │            ┌─────▼──────────────────────────┐
        │            │  DISPUTED — reason + evidence  │
        │            │  line-level or whole invoice   │
        │            └─────┬──────────────────────────┘
        │                  │ resolved by 1000FiX finance
        │            ┌─────▼──────────────┬────────────┐
        │            │ upheld → credit    │ rejected → │
        │            │ note issued (M20)  │ explained  │
        │            └─────┬──────────────┴─────┬──────┘
        │                  │                    │
   ┌────▼──────────────────▼────────────────────▼──────┐
   │  PAYABLE → paid in-portal → statement updated      │
   └───────────────────────────────────────────────────┘
```

| State | Owner | P04's role |
|---|---|---|
| Issued | M20 | Present and decompose |
| In client approval | **P04** (chain) / M29 (permission) | Route and record |
| Disputed | M20 | Capture reason and evidence; track |
| Credit issued | M20 / M53 | Present the credit note |
| Paid | M20 | Initiate and confirm |

---

## 9. Portal Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P04-01 | A user may access only their own client organisation's data, under every path including direct object reference and export | **H** | CTO |
| PRU-P04-02 | P04 persists no authoritative business state (`04-00` §1) | **H** | CTO |
| PRU-P04-03 | Coverage is validated against the contract **before** a request is accepted, never after the work is performed | **H** | Chief Commercial Officer |
| PRU-P04-04 | A request or estimate above a user's delegated limit cannot be submitted or approved by that user | **H** | Chief Commercial Officer |
| PRU-P04-05 | The client's approval chain is defined by the client administrator within contract bounds, and is an auditable, exportable record | **H** | Chief Commercial Officer |
| PRU-P04-06 | MFA is mandatory for the approver and finance sub-roles; step-up is required for invoice approval, dispute raising and delegation change (`05-04` §1) | **H** | CTO |
| PRU-P04-07 | A bulk upload or bulk submission commits or rejects as a set, with a line-level report; partial commits are not permitted | **H** | CTO |
| PRU-P04-08 | Every consolidated invoice is decomposable to the request and line that generated it | **H** | CFO |
| PRU-P04-09 | SLA breaches and the credits they earned are published to the client, not withheld | **H** | Chief Commercial Officer |
| PRU-P04-10 | Estate reconciliation results are published to the client, including strays and gaps | **C** | Chief Commercial Officer |
| PRU-P04-11 | Out-of-scope work is priced and approved before performance, never absorbed silently | **H** | CFO |
| PRU-P04-12 | Internal cost, margin and internal notes are absent from every P04 payload | **H** | CFO |
| PRU-P04-13 | A client administrator manages their own users; 1000FiX never manages a client's internal hierarchy | **C** | Chief Commercial Officer |
| PRU-P04-14 | Every export is scoped to the client's own data, logged and attributed | **H** | CTO |
| PRU-P04-15 | No price, entitlement, SLA or credit value is computed client-side (**PS-11**) | **H** | CTO |
| PRU-P04-16 | Every screen is complete in Bengali and English (**PS-03**) | **H** | Chief Commercial Officer |
| PRU-P04-17 | Where a backing module is unavailable, the capability is disabled with an explanation and a route to the account manager (**PS-09**) | **H** | CTO |

---

## 10. Data, Caching & State Model

### 10.1 What P04 Holds

| Object | Purpose | Ownership |
|---|---|---|
| **Client delegation model** | Approval chains, authority limits, user-to-site scoping | **P04** — the only configuration it owns; the resulting permission is enforced by M29 |
| Client user invitations and state | Invite, suspend, remove within the organisation | **P04**, identity in M29 |
| Saved views and filters | Per user, per organisation | **P04** |
| Draft bulk uploads | Recovery of an interrupted upload | **P04**, transient |
| Session and preference | Language, default site, landing view | M29 / P04 |

### 10.2 Never Held

| Item | Reason |
|---|---|
| Any business object — estate, contract, request, invoice | PRU-P04-02 |
| Another organisation's data of any kind | PRU-P04-01 — the highest-severity failure mode |
| Internal cost, margin, internal notes | PRU-P04-12 |
| Coverage, entitlement, SLA or credit logic | PRU-P04-15 |
| Payment credentials | Payment is a gateway handoff via M20 |

### 10.3 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party` (corporate account, contacts) | M33 | Read |
| `fix.asset.estate`, `fix.asset.estate.node`, `fix.asset.estate.placement`, `fix.asset.estate.reconciliation` | **M17** | Read; submit bulk load, moves, retirements |
| `fix.asset`, `fix.asset.service.history` | M17 | Read within the client's estate |
| `fix.contract`, `fix.entitlement`, `fix.pm.schedule` | M08 | Read; request renewal and amendment |
| `fix.service.order` | M01 | Create singly and in bulk; read status |
| `fix.estimate` | M01 / M36 | Read; approve within limit |
| `fix.sla.status`, breach, credit | M01 / M08 / M53 | Read |
| `fix.invoice`, `fix.credit.note`, `fix.statement` | M20 | Read; approve, dispute, pay |
| `fix.monitored.asset`, alerts, patch state | M05 / M48 | Read |
| `fix.destruction.certificate` | M06 | Read |
| `fix.disposal.certificate` | M18 | Read |
| `fix.project` | M67 | Request; read status |
| `fix.knowledge.article` | M61 | Read, scoped |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P04-01 | Request raised above the requester's limit | Route to the defined approver, notify them, and show the chain state to the requester | Request held; escalate after the configured wait |
| AUT-P04-02 | Coverage validation returns out-of-scope or chargeable | State it before submission with the rate and the reason; require explicit acknowledgement | Block submission rather than accept an unvalidated request |
| AUT-P04-03 | SLA at risk or breached on a client request | Notify the client contact, publish the breach and compute the credit earned | Publish on next refresh; never suppress |
| AUT-P04-04 | Consolidated invoice issued | Notify the client finance contact, route into the client approval chain, and open the dispute window | Notify by email; invoice remains retrievable |
| AUT-P04-05 | Invoice dispute raised | Acknowledge with a reference and expected response, route to 1000FiX finance, and track to credit or explanation | Acknowledge; escalate the routing failure |
| AUT-P04-06 | Entitlement consumption crosses a threshold | Notify the client and the account manager with a projection to term end | Report only |
| AUT-P04-07 | Contract approaching expiry | Present the renewal quotation in-portal and notify the client and account manager at M08's horizons | In-portal only |
| AUT-P04-08 | Estate reconciliation run completes (M17 AUT-AST-12) | Publish gaps, strays and movements to the client with the ability to accept or query each line | Publish on next cycle |
| AUT-P04-09 | Bulk upload submitted | Validate every line, report rejects line by line, and commit or reject as a set | Reject whole; retain the staged file |
| AUT-P04-10 | Managed-services alert raised (M48) | Surface it on the estate health dashboard and notify per the client's preference | Dashboard only |
| AUT-P04-11 | Scheduled maintenance visit due | Notify the client contact for the site and allow rescheduling within policy | Notify; visit proceeds per contract |
| AUT-P04-12 | Compliance certificate issued (M06 or M18) | Make it retrievable and notify the requesting contact | Retrievable; notification retried |

---

## 12. Module Interfaces

### 12.1 Modules P04 Consumes

| Module | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, MFA, step-up, organisation scoping | OIDC via gateway |
| M28 Integration Platform | Every call; per-organisation rate limits | Gateway |
| M33 Party Master | Corporate account, contacts, hierarchy | REST |
| M17 Asset Registry | Estate structure, assets, history, bulk load, reconciliation | REST |
| M08 Contracts | Contract, entitlement, coverage, PM schedule, renewal quotation | REST |
| M01 Service Order | Request creation, status, estimate | REST + events |
| M36 Quotation | Renewal and amendment quotations | REST |
| M11 Pricing | Contract rate card for chargeable work and procurement | REST |
| M20 Receivable & Billing | Consolidated invoice, decomposition, statement, payment, credit note | REST |
| M53 Revenue & Settlement | Service credit recognition | REST |
| M05 Managed Services | Estate health, incidents, patch compliance, SLA | REST |
| M48 IoT & Predictive | Alerts and health index for monitored assets | REST |
| M06 Data Services | Destruction certificates and case status | REST |
| M18 E-Waste | Disposal certificates and collection booking | REST |
| M67 Project Management | Rollout and decommission project status | REST |
| M25 BI | Scoped estate analytics | Embedded |
| M27 Communications | Notification and conversation history | REST |
| M61 Knowledge | Scoped knowledge base | REST |
| M65 Localisation | Bengali and English bundles | Build-time + REST |

### 12.2 What P04 Writes Back

| Target | What | Mechanism |
|---|---|---|
| M01 | Single and bulk service requests; estimate approvals | Command |
| M17 | Bulk estate load, asset moves, addition and retirement requests, reconciliation responses | Command |
| M08 | Renewal acceptance and amendment requests | Command |
| M20 | Invoice approval, dispute with reason and evidence, payment initiation | Command |
| M67 | Project requests — rollout, decommission, trade-in | Command |
| M18 | E-waste collection bookings | Command |
| M29 | Client user invitations, suspensions and removals | Command |
| M25 / M62 | Adoption, bulk usage, coverage-validation and dispute analytics | Event stream |

### 12.3 Events P04 Consumes

| Event | Source | Effect in P04 |
|---|---|---|
| `service_order.status_changed` | M01 | Update request tracking |
| `sla.at_risk` / `sla.breached` | M01 / M08 | Update SLA view; publish breach and credit |
| `invoice.issued` | M20 | Open the approval chain and dispute window |
| `credit_note.issued` | M20 | Present against the disputed line |
| `contract.renewal_due` | M08 | Present the renewal quotation |
| `entitlement.threshold_crossed` | M08 | Notify with projection |
| `asset.estate_reconciled` | **M17** | Publish gaps, strays and movements |
| `asset.alert_raised` / `asset.health_degraded` | M48 | Update the estate health dashboard |
| `project.milestone_reached` | M67 | Update project status |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P04-01 | Client asset-management systems | Inbound | Estate file exchange at onboarding and periodic refresh; CSV/Excel by default, API by exception |
| INT-P04-02 | Corporate payment rails (bank transfer, cheque, corporate card) | Outbound | Invoice payment; via M20 and M50 |
| INT-P04-03 | Client email and calendar | Outbound | Notification and service-review scheduling; via M27 |
| INT-P04-04 | Client SSO (SAML/OIDC), where a client requires it | Inbound | Federated authentication for large clients; via M29 |

### 12.5 API Surface Consumed

| Endpoint | Method | Purpose | Owner |
|---|---|---|---|
| `/api/v1/estates/{id}` | GET | Estate structure and placements | M17 |
| `/api/v1/estates/{id}/bulk-load` | POST | Bulk estate registration, set-committed | M17 |
| `/api/v1/estates/{id}/reconciliation` | GET | Declared versus observed | M17 |
| `/api/v1/contracts` | GET | Contracts, entitlement, coverage, PM calendar | M08 |
| `/api/v1/coverage/validate` | POST | **Synchronous coverage decision before submission** | M08 |
| `/api/v1/service-orders/bulk` | POST | Bulk request submission, set-committed | M01 |
| `/api/v1/service-orders` | GET/POST | Single request; tracking | M01 |
| `/api/v1/sla/status` | GET | Real-time and historical SLA with breaches and credits | M01 / M08 |
| `/api/v1/invoices/{id}/decomposition` | GET | Itemised breakdown by site, department, asset, request | M20 |
| `/api/v1/invoices/{id}/approve` | POST | Client-chain approval | M20 |
| `/api/v1/invoices/{id}/dispute` | POST | Raise a dispute with evidence | M20 |
| `/api/v1/msp/estate-health` | GET | Estate health, incidents, patch compliance | M05 / M48 |
| `/api/v1/certificates` | GET | Destruction and disposal certificates | M06 / M18 |
| `/api/v1/projects` | GET/POST | Rollout and decommission projects | M67 |

---

## 13. Roles & Permissions

**R37 Corporate Portal User** is the only role with P04 access (`05-04` §2), with four
sub-roles:

| Sub-role | Access | Scope | MFA |
|---|---|---|---|
| **Requester** | C R | Own sites/departments — raise and track requests, view estate | Optional |
| **Approver** | R U A | Assigned scope — approve requests and estimates within delegated limits | **Mandatory** |
| **Finance** | R U A | Whole organisation — invoices, decomposition, approval, dispute, payment, statements | **Mandatory** |
| **Administrator** | C R U D A | Whole organisation — manage users, define approval chains and limits, manage estate structure | **Mandatory** |

> **Per `05-04` §8, external party access is own-records-only and role-scoped within it.** No
> 1000FiX internal role signs in to P04. An account manager viewing a client's portal
> experience does so through P03 under their own identity — never by impersonation.

**Field-level restrictions.** `unit_cost`, `margin`, `internal_note`, `vendor_price` and
`technician_incentive_detail` are absent from every P04 payload. The client sees the price they
are charged, never the cost basis. Technician identity is presented as a name and photograph
for the visit only; no employee record is exposed.

**Segregation of duties within the client organisation.** P04 enforces the chain the client
administrator defines, and additionally blocks: a user approving their own request above their
limit, and the same user both raising and approving an invoice dispute above the configured
value.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Portal adoption** | Active users per client organisation against contracted users; clients with zero activity | M25, Account Managers |
| **Bulk usage** | Share of corporate requests raised in bulk versus singly; bulk batch sizes and completion time | M25 — the `04-00` KPI |
| **Coverage validation outcomes** | Covered, chargeable and out-of-scope rates by client and asset category — a direct signal of contract fit | M25, M08, CCO |
| **Invoice disputes** | Disputes raised per consolidated invoice, by reason and line type, and resolution outcome | M25, CFO |
| SLA visibility | SLA views per client; correlation between viewing and disputing | M25 |
| Estate maintenance | Bulk uploads, moves, retirements, reconciliation lines accepted versus queried | M17, M25 |
| Entitlement consumption | Rate of draw-down against term, by client — a renewal and upsell signal | M08, M07 |
| Approval chain performance | Time in the client's own approval chain, by client and step | M25 |
| Support deflection | Portal actions versus account-manager contacts for the same client | M25, M07 |
| Estate health engagement | MSP dashboard views by client; correlation with renewal | M05, M25 |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| — | **Corporate clients actively using the portal** | 0% | 70% | **> 85% of contracted clients** |
| — | **Bulk requests submitted through the portal** | 0% | 55% | **> 70% of corporate requests** |
| — | **Bulk service request creation time** | n/a | < 8 min | **< 5 min** |
| — | **Invoice disputes** | unmeasured | < 5% | **< 3% of consolidated invoices** |
| — | **Corporate client satisfaction** | unmeasured | > 4.3/5 | **> 4.6/5** |
| — | Corporate requests raised in-portal versus by email or phone | ~0% | 65% | **> 85%** |
| — | Estates maintained by the client rather than by 1000FiX | 0% | 50% | **> 75%** |
| — | Estate reconciliation lines accepted by the client | n/a | 70% | **> 90%** |
| — | Coverage disputes after work performed | unmeasured | < 4% | **< 1%** |
| — | Consolidated invoices approved in-portal | 0% | 60% | **> 85%** |
| — | Account-manager contacts for status and coverage queries | unmeasured | −40% | **−70%** |
| — | Bengali and English completeness | n/a | **100%** | **100%** |
| — | Cross-organisation data exposures | n/a | **0** | **0** |
| **KPI-041** *(supported)* | SLA attainment on corporate contracts | unmeasured | 92% | **96%** |

> **Register note.** The first five metrics are adopted verbatim from `04-00` §P04. P04 has
> **no KPI-0nn identifiers allocated**; all thirteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L5 | **Next.js 15 application** — account and delegation, estate, requests, SLA, contracts, MSP dashboard, billing, procurement, support | 78% |
| L4 | Shared design system and component library (with P01, P07, P08, P10, P12) | 10% |
| L2 | OCA `portal` and `dms` for document serving and rendered invoice retrieval | 6% |
| L1 | Odoo `portal` authentication and document routes where reused | 6% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-204** | `p04_corporate_portal` — organisation account and client-side delegation model, estate view and bulk maintenance, coverage validation, single and bulk request, SLA and credits, contract and entitlement, MSP dashboard, consolidated invoice with decomposition and dispute, procurement, compliance evidence, scoped analytics | Next.js 15 application | 26 PW |

> **CD register.** One ID, **CD-204**, claimed following CD-203 (P03). All CD IDs remain
> provisional pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M29 Identity & Security | Organisation scoping and mandatory MFA for approver and finance sub-roles |
| M28 Integration Platform | Gateway with per-organisation rate limits |
| M33 Party Master | The corporate account and its contacts |
| **M17 Asset Registry** | **The estate is the portal's spine** — structure, bulk load and reconciliation must exist first (W2) |
| **M08 Contracts** | Coverage validation, entitlement and SLA — the commercial engine (W4) |
| M01 Service Order | Requests must land somewhere |
| M20 Receivable & Billing | Consolidated invoicing and dispute (W3) |
| M05 Managed Services | The MSP dashboard (W5) — **P04 ships in W4 without it and adds it in W5** |
| M53 Revenue & Settlement | Service credit recognition (W4) |
| M67 Project Management | Rollout and decommission projects (W7) — added when M67 lands |

**Phasing within the portal.** W4 ships account and delegation, estate, requests with coverage
validation, SLA, contracts and consolidated invoicing. W5 adds the managed-services dashboard.
W7 adds procurement and project requests.

### 16.4 Onboarding & Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Corporate client estate declarations | Held by each client, various formats | M17 estate via bulk upload | W4, per client at onboarding |
| Client contact lists | Held by account managers | M33 contacts, then P04 user invitations | W4 |
| Existing corporate contracts | Paper and PDF | M08 | W4, with M08 migration |
| Open corporate requests at cutover | Current only | M01 | W4 |

> **Onboarding position.** Client onboarding is **per client, account-manager-led, and
> sequenced by contract value.** A corporate client whose estate is loaded badly experiences the
> portal as wrong data and does not return. The estate load, the delegation model and the first
> invoice decomposition are walked through with the client's administrator before the account
> is opened to their wider user base.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A user cannot access another client organisation's data through any path, including direct object reference, export, search and API | **Tenant-isolation penetration test — the highest-severity test for this portal** |
| AC-02 | A 500-line estate upload validates, reports rejects line by line, and commits or rejects as a set within 60 seconds | Scripted bulk load with deliberate rejects |
| AC-03 | A 50-request bulk submission completes end to end, including coverage validation, in under 5 minutes | Timed test with a representative client estate |
| AC-04 | Coverage is stated before submission as covered, chargeable with a rate, or out of scope with a reason | Scripted scenarios across all three outcomes |
| AC-05 | A request or estimate above a user's delegated limit cannot be submitted or approved by that user | Negative test at every sub-role |
| AC-06 | The client's approval chain is definable by their administrator and exportable as an audit record | Scripted definition and export |
| AC-07 | MFA is enforced for approver and finance sub-roles, and step-up for invoice approval, dispute and delegation change | Authentication test per sub-role |
| AC-08 | A 2,000-line consolidated invoice decomposes and filters in under 3 seconds | Performance test |
| AC-09 | Every invoice line traces to the request that generated it, and reconciles against the client's own request history | Reconciliation test with three client datasets |
| AC-10 | SLA breaches and the credits earned are published to the client without prompting | Scripted breach scenario |
| AC-11 | Estate reconciliation results, including strays and gaps, are published and each line can be accepted or queried | Scripted reconciliation with M17 |
| AC-12 | No P04 payload contains cost, margin, internal notes or employee records | Automated payload inspection across every endpoint |
| AC-13 | Every export is scoped to the client's own data, logged and attributed | Export audit |
| AC-14 | A dispute is acknowledged with a reference and expected response time, and tracked to credit or explanation | Scripted dispute lifecycle |
| AC-15 | WCAG 2.1 AA across every journey, in Bengali and English | Automated scan plus manual audit |
| AC-16 | With a backing module unavailable, the capability is disabled with an explanation and a route to the account manager | Chaos test per backing module |
| AC-17 | Corporate portal adoption exceeds 85% of contracted clients and bulk share exceeds 70% | Six consecutive monthly reports |
| AC-18 | Three corporate clients confirm they can reconcile a consolidated invoice unaided | Signed client confirmations |
| AC-19 | CCO and three corporate client administrators sign off UAT | Signed UAT record |

**Definition of done:** the twelve cross-portal standards in `04-00` §3 plus the 19 criteria
above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | How many corporate clients are contracted, how many users each, and how many hold declared estates today? | CCO / Account Managers | **W4 minus 4 months** |
| Q-02 | What delegation limits does the contract permit a client to set, and who approves a client's chain definition? | CCO / Legal | W4 design |
| Q-03 | Are service credits automatic on breach, or subject to commercial review before publication? | CCO / CFO | **W4 design** |
| Q-04 | What consolidated invoice cycle applies per client — monthly, per site, per department? | CFO / Account Managers | W4 design |
| Q-05 | Does any client require federated SSO, and on what protocol? | CTO / Account Managers | W4 build |
| Q-06 | Do government clients have procurement or audit requirements the portal must satisfy (e-GP linkage, prescribed formats)? | CCO / Legal | W4 design |
| Q-07 | Is the estate reconciliation published automatically, or released by the account manager after review? | CCO | W4 design |
| Q-08 | What is the dispute window per invoice, and what happens to payment terms while a dispute is open? | CFO | W4 design |
| Q-09 | Can a client's own API push estate changes, or is file exchange sufficient for the programme horizon? | CTO / Account Managers | W4 scoping |
| Q-10 | Which clients are onboarded first, and who runs the walkthrough? | CCO / Account Managers | W4 minus 2 months |
| Q-11 | Is out-of-scope work ever performed on goodwill, and if so who authorises it and how is it recorded? | CCO / CFO | W4 design |
| Q-12 | Do corporate users work primarily in English rather than Bengali, and does that change the default? | CCO | W4 design |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §P04, §1, §3 PS-01…PS-12, §4 ·
`P01_Customer_Self_Service_Portal_and_Mobile_Application.md` ·
`P03_Admin_Operations_Portal.md` · `P08_Brand_Partner_Portal.md` ·
`03_Modules/F_Asset_Equipment_and_Facilities/M17_Device_and_Customer_Asset_Registry.md`
§5.6 (estate structure, bulk load, reconciliation), §12.2, §12.5 ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M05_Remote_Support_and_Managed_Services.md` ·
`03_Modules/B_Customer_Engagement_and_Experience/M33_Customer_and_Party_Master_Management.md` ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md`
§1 (R37 sub-roles and MFA), §2, §5, §8 (external party access rules)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.1 Portal 4, BR-CRM-007,
BR-CWM-001, BR-CWM-002, BR-CWM-003, BR-CWM-011, BR-SRM-011, BR-FIN-008, BR-DMS-001 ·
`00_Governance_and_Charter/00-03_Scope_Expansion_Delta_v1_to_v2.md` §M17 (corporate asset listing) ·
`1000FiX_Services_Company_Profile.md` §Corporate Services, §Additional Services

**External benchmark**
[B2B customer portal best practices — multi-user roles, approvals and account-specific terms](https://k-ecommerce.com/blog/b2b-ecommerce-customer-portal-best-practices) ·
[Complete guide to B2B customer portals — governance, role-based access and approvals](https://wizcommerce.com/blog/b2b-customer-portal/) ·
[B2B customer portals with invoice and payment history — centralised invoicing and transparency](https://www.transactbridge.com/blog/b2b-customer-portals-with-invoice-and-payment-history-features-benefits-use-cases) ·
[Best practices for self-service customer portals](https://www.naw.org/self-service-customer-portals/) ·
[B2B customer portal design and personalised trust](https://k-ecommerce.com/blog/personalized-customer-portals-trust) ·
[B2B customer payment portals 2026](https://gaviti.com/best-b2b-customer-payment-portals/) ·
[B2B customer service best practices — SLA definition and transparency](https://lform.com/blog/post/7-top-best-practices-for-b2b-customer-service/) ·
[ServiceMax entitlement engine — warranty and contract validation before work](https://www.ptc.com/en/products/servicemax/core)

---

*Portal P04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
