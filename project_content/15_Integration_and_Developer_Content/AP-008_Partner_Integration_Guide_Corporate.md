---
id: AP-008
title: Partner Integration Guide — Corporate
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
author: Platform Engineering with Account Management
reviewers: [CTO, Solution Architect, Account Management Lead, Commercial Director, Finance Manager, Security Lead, Legal Counsel, Content Design Lead]
approver: Content Design Lead with Commercial Director
content_class: D
purpose: >
  The integration guide a corporate client's IT function reads to connect their asset,
  service-management or procurement systems to 1000FiX — estate exchange, coverage validation
  before submission, bulk request submission, SLA and credit publication, consolidated invoice
  decomposition and dispute, ticket exchange with an ITSM platform, and federated sign-on. Without
  it, enterprise clients that make ticket and asset integration a condition of contract are told
  "yes, in principle" by an account manager and discover the actual boundary during
  implementation, which is where renewals are lost; and every client's estate arrives in a
  different spreadsheet with no stated contract.
traces_to: [P04, P04 FR-POR, P04 AC-01, P04 AC-02, P04 AC-03, P04 §12.4, P04 §12.5, P04 Q-05, P04 Q-09, M05, M08, M17, M01, M20, M53, M67, M06, M18, 05-03, 05-03 INT-046, 05-03 INT-047, 05-04 §8, EA-03, AP-001, AP-002, AP-004, AP-005, AP-006, AP-010, AP-011, AP-012, EO-007, EO-008, MD-015, LG-003, LG-015, HC-006, NT-010, DM-012]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P04_Corporate_B2B_Portal.md §3.2 "P04 accepts an estate file or an API feed; it does not integrate into client systems", §12.4 INT-P04-01…04, §12.5 the fifteen endpoints P04 consumes, §13 four sub-roles and field-level restrictions, §16.4 onboarding, §17 AC-01…AC-19, §18 Q-05 and Q-09
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §2.7 INT-046 corporate client SSO (SAML/OIDC per client, W6, P2) and INT-047 client ITSM ServiceNow/Jira (REST + webhook, W7, P3); §8 delivery sequence
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §8 EA-03 "corporate portal users see only their own company's data, further scoped by their role in that company"; §1.7 R37 with MFA mandatory for Approver and Finance
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 G4-05 ten or more corporate clients transacting on the B2B portal; G4-08 consolidated B2B invoicing operating correctly
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Partner Integration Guide — Corporate

| Item | Value |
|---|---|
| Audience | Corporate client IT, ITSM and procurement systems teams |
| Portal | `P04` Corporate B2B Portal · code `B2B` |
| Integration modes | 4 — file, API, ITSM exchange, federation (§4.2) |
| Endpoints available | 15 (`P04` §12.5) |
| Events available | 10 (§4.8) — **six unregistered** |
| Actions requiring a human | 4 — step-up gated (§4.7) |
| Data never disclosed | 6 categories (§4.9) |
| Onboarding steps | 8 (§4.11) |
| Wave | W4 for file and API · **W6 federation · W7 ITSM** — §4.2 and open item `O-01` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume. The **endpoint reference table**
> required by `CG-009` §3 is §4.5. The **error catalogue table** required by `CG-009` §3 is
> §4.10, referencing `AP-006` codes rather than defining new ones (`CP-01`).
>
> **Identifier scoping.** `AC-nn` in this file means a **`P04` §17 acceptance criterion**
> throughout, and nothing else. The `AC-nn` series is document-scoped, not programme-scoped —
> `M28`, `P04` and `P08` each run their own `AC-01`… sequence — so every `AC-nn` reference
> elsewhere in Category 15 carries its owning document explicitly.

---

## 1. Purpose

The register justification is a commercial fact: *"Enterprise clients increasingly require ticket
and asset integration as a condition of contract."*

`P04` §3.2 sets the boundary in one line — *"P04 accepts an estate file or an API feed; it does
not integrate into client systems."* That is a clear, defensible position and it is **not what a
client hears from an account manager**, because the account manager is answering "can you
integrate with ServiceNow?" and the honest answer has three parts: yes at W7, at P3 priority, and
in one direction more readily than the other.

This file exists so that answer is written down once, before the contract, rather than discovered
during implementation.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| The stated boundary (§4.1) | Clients expect 1000FiX to integrate *into* their systems. `P04` §3.2 says we do not, and an unwritten boundary is renegotiated on every call |
| Estate exchange contract | Every client's estate arrives in a different spreadsheet. `AC-02` requires a 500-line load to validate, report rejects line by line and commit **as a set** in 60 seconds — a contract nobody has written down for the client to build against |
| Coverage validation documentation | The client submits work that is out of scope and disputes the charge. `AC-04` requires coverage stated **before** submission; a client integration that skips the call gets the outcome the control exists to prevent |
| Bulk submission contract | A client loops the single-request endpoint 500 times, exhausts its rate limit and reports an outage |
| Invoice decomposition contract | `G4-08` consolidated invoicing; `AC-09` requires every line to trace to the request that generated it and reconcile against the client's own history. Without a documented decomposition, the client reconciles by eye and disputes what they cannot match |
| ITSM mapping | Ticket exchange is built per client, each mapping states differently, and a "resolved" in ServiceNow means something different for each |
| Federation position | `P04` Q-05 asks whether any client requires federated SSO and on what protocol. Unanswered, the first client that requires SAML gets a bespoke W4 build against a W6 integration |

---

## 2. Scope

**In scope.** The integration boundary; four integration modes with their waves; estate exchange
as a contract; coverage validation; bulk and single request submission; SLA and credit
publication; invoice decomposition, approval and dispute; ITSM ticket exchange and its state
mapping; federated sign-on; the endpoint and event reference; step-up-gated actions; the
disclosure boundary; error conditions; and the onboarding sequence.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| Client business onboarding, welcome kit, portal walkthrough | `EO-007` | For the client's **users**; this is for their **developers** |
| Client administrator configuration — users, sites, approval chains | `EO-008` | Configuration, not integration |
| Corporate account hierarchy rules | `MD-015` | Group → company → division → site → department, with billing and approval roll-up |
| Portal terms, liability, data protection | `LG-003` | Linked, never restated |
| SLA definitions, service credits, pause rules | `LG-015`, `MD-028` | This file transmits SLA data; it does not define it |
| Which fields the client receives and on what basis | `AP-012` | §4.9 states the boundary; `AP-012` is the register |
| Auth, scopes, credentials, limits | `AP-005` | Referenced, not restated |
| Error codes | `AP-006` | §4.10 indexes |
| Webhook mechanism | `AP-004` | §4.8 lists which events |
| Sandbox and promotion | `AP-010` | Onboarding step 4 |
| Migrating a client's historical data into 1000FiX | `DM-012` load templates and `M17` migration | Estate **onboarding** (§4.3) is a steady-state contract, not a migration |
| Client-side field mapping into their own systems | The client | We publish our contract; we do not map their schema — `O-05` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Corporate client IT and integration teams** | The primary audience; usually the client's internal IT or an outsourced systems integrator |
| **Client ITSM administrators** | §4.6 — the ticket exchange mapping |
| **1000FiX Account Managers (`R22`)** | The document sent with a proposal, so the technical boundary precedes the commercial commitment |
| **1000FiX Finance (`R26`, `R27`)** | §4.4 — how a client's system consumes and disputes a consolidated invoice |
| **1000FiX Platform Engineering** | Building `INT-P04-01` and `INT-047` per client |
| **Legal** | §4.9 and the `P04` `AC-01` tenant-isolation position |

---

## 4. Content

### 4.1 The boundary, stated first

> **`P04` §3.2: "P04 accepts an estate file or an API feed; it does not integrate into client
> systems."**

| 1000FiX does | 1000FiX does not |
|---|---|
| Publish documented, versioned APIs the client's systems call | Build or operate a connector inside the client's environment |
| Accept an estate file or API feed on a defined contract | Read the client's asset database directly |
| Send webhooks to a client endpoint | Poll the client's systems |
| Accept a client's ITSM tickets and return updates (`INT-047`, W7) | Install an app in the client's ServiceNow or Jira instance |
| Federate authentication to the client's IdP (`INT-046`, W6) | Hold or synchronise the client's user directory |
| Provide sandbox, credentials and support for the client's build | Write the client's integration |

**Why this boundary and not a more generous one.** Each of 500–2,000 corporate users sits inside
an unknown number of client organisations (`P04` Q-01), each with its own systems. A programme that
commits to integrating *into* client environments commits to an unbounded number of bespoke
builds, on client change calendars, with client-side support obligations. The API-and-file
boundary is what makes corporate integration deliverable at all — and it is a **commercial**
position that Account Management must hold, not only a technical one.

### 4.2 Four integration modes

| Mode | What it is | Wave | Priority | Suits |
|---|---|:--:|:--:|---|
| **C1 — File exchange** *(default)* | Estate as CSV/Excel at onboarding and on periodic refresh (`INT-P04-01`) | **W4** | Default | Every client. The only mode guaranteed available at `P04` go-live |
| **C2 — API** | The client's systems call the `P04` API surface directly | **W4** | — | Clients with an asset or service-management platform and IT capacity |
| **C3 — ITSM ticket exchange** | Bidirectional ticket exchange with ServiceNow or Jira (`INT-047`) | **W7** | **P3** | Enterprise MSP clients |
| **C4 — Federated sign-on** | SAML or OIDC federation into `M29` (`INT-046`, `INT-P04-04`) | **W6** | **P2** | Large clients with a directory and a policy against local accounts |

> **Read the wave and priority columns together, because they are the most commercially sensitive
> facts in this guide.** `P04` goes live in **W4** (Month 18). `G4-05` requires ten or more
> corporate clients transacting by that gate. **Federation arrives two waves later at W6 (Month
> 26) and ITSM exchange three waves later at W7 (Month 30), at `P3` — the lowest priority in the
> register, described as "enhancement; opportunistic".**
>
> A client whose contract makes ticket integration a condition therefore signs in W4 against a
> capability scheduled for W7 at a priority that `05-03` §2 explicitly marks deferrable. That is
> a contradiction between the register's own justification for this file — *"a condition of
> contract"* — and the priority assigned to the integration that satisfies it. Recorded as
> `O-01`, and it is a commercial exposure before it is a technical one.

### 4.3 Estate exchange

The client's estate is the foundation of everything else: coverage, SLA, billing and reporting all
resolve through it.

| # | Contract point | Detail |
|---|---|---|
| **ES-1** | **Set-committed** | A bulk load commits **as a set** or rejects as a set (`AC-02`). There is no partial estate |
| **ES-2** | **Line-by-line rejects** | Every rejected line is reported with its line number and reason. The client corrects and resubmits the whole set |
| **ES-3** | **Performance contract** | 500 lines validate, report and commit or reject **within 60 seconds** (`AC-02`) |
| **ES-4** | **Idempotent** | Resubmitting an identical set with the same `Idempotency-Key` returns the original result and creates nothing (`API-07`) |
| **ES-5** | **Structure before assets** | Sites and departments must exist before assets can be placed in them. Estate structure follows `MD-015` |
| **ES-6** | **Serial is the identity** | An asset is identified by serial. Two loads carrying the same serial are the same asset, not two |
| **ES-7** | **Reconciliation is published back** | Declared versus observed, including **strays** and **gaps**, with each line acceptable or queryable (`AC-11`, `asset.estate_reconciled`) |
| **ES-8** | **Refresh is a full set, not a delta** — unless the client uses the API mode's asset-level endpoints | A delta file with no deletion semantics silently accumulates retired assets |

**File mode (C1).** CSV or Excel to the specification issued at onboarding, exchanged through the
portal or an agreed secure route. **The file specification itself is not in this file and does not
exist yet** — `DM-012` holds the migration load templates and `M17` owns the estate model.
Recorded as `O-02`.

**API mode (C2).** `POST /api/v1/estates/{id}/bulk-load`, same semantics, plus asset-level
create, move, retire. **Whether a client's own API may *push* estate changes, rather than
1000FiX pulling or the client uploading, is `P04` Q-09 and is unresolved** — it changes whether
C2 is a client-initiated or 1000FiX-initiated integration, which is a material design difference.

### 4.4 Requests, coverage, SLA and invoicing

| Flow | Contract | Integration note |
|---|---|---|
| **Coverage validation** | `POST /api/v1/coverage/validate` returns **covered**, **chargeable with a rate**, or **out of scope with a reason** — synchronously, **before** submission (`AC-04`) | **Call it. Always.** A client integration that submits without validating gets the charge dispute the control exists to prevent. It is a read; it costs one call |
| **Single request** | `POST /api/v1/service-orders` | Standard. `AP-002` §4.5 is the worked reference |
| **Bulk request** | `POST /api/v1/service-orders/bulk`, **set-committed** | `AC-03`: 50 requests including coverage validation complete end to end in under 5 minutes. **Use this rather than looping the single endpoint** — the bulk class has its own rate limit (`AP-005` §4.7) |
| **Delegated limits** | A request or estimate above a user's delegated limit **cannot be submitted or approved by that user** (`AC-05`) | Limits are the client administrator's configuration (`EO-008`). A service credential inherits the limits of the identity it acts for; see `O-06` |
| **SLA status** | `GET /api/v1/sla/status` — real time and historical, with breaches and the credits earned | Credits are **published without prompting** (`AC-10`). A client system does not need to ask; it will receive `sla.breached` |
| **Consolidated invoice** | `GET /api/v1/invoices/{id}/decomposition` — itemised by site, department, asset and request | `AC-08`: a 2,000-line invoice decomposes and filters in under 3 seconds. `AC-09`: **every line traces to the request that generated it** |
| **Invoice approval** | `POST /api/v1/invoices/{id}/approve` — the client's own chain | **Step-up gated** (`AC-07`) |
| **Invoice dispute** | `POST /api/v1/invoices/{id}/dispute` with reason and evidence | **Step-up gated.** Acknowledged with a reference and an expected response time, tracked to credit or explanation (`AC-14`) |
| **Certificates** | `GET /api/v1/certificates` — destruction (`M06`) and disposal (`M18`) | Read-only. These are compliance evidence for the client's own auditors |
| **Projects** | `GET/POST /api/v1/projects` — rollout and decommission (`M67`, W7) | Later wave; noted so a client does not plan against it at W4 |
| **Estate health** | `GET /api/v1/msp/estate-health` — incidents, patch compliance, SLA (`M05`, `M48`, W5) | W5, one wave after portal go-live |

> **Two dependencies inside the portal's own phasing.** `P04` §16.3 ships account, estate,
> requests, SLA, contracts and consolidated invoicing at **W4**; the managed-services dashboard at
> **W5**; procurement and project requests at **W7**. A client integrating at W4 against
> `/api/v1/msp/estate-health` or `/api/v1/projects` will find them absent. This is stated because
> the endpoint list in `P04` §12.5 carries no wave column.

### 4.5 Endpoint reference

The endpoint reference table required by `CG-009` §3. Paths and owners from `P04` §12.5; scope,
step-up, mode and wave are this file's contribution.

| Endpoint | Method | Purpose | Owner | Scope *(proposed — `AP-005` `O-01`)* | Step-up | Wave |
|---|:--:|---|:--:|---|:--:|:--:|
| `/api/v1/estates/{id}` | GET | Estate structure and placements | `M17` | `estate:read:own_org` | — | W4 |
| `/api/v1/estates/{id}/bulk-load` | POST | Bulk estate registration, set-committed | `M17` | `estate:write:own_org` | — | W4 |
| `/api/v1/estates/{id}/reconciliation` | GET | Declared versus observed, with strays and gaps | `M17` | `estate:read:own_org` | — | W4 |
| `/api/v1/contracts` | GET | Contracts, entitlement, coverage, PM calendar | `M08` | `contract:read:own_org` | — | W4 |
| `/api/v1/coverage/validate` | POST | **Synchronous coverage decision before submission** | `M08` | `coverage:read:own_org` | — | W4 |
| `/api/v1/service-orders` | GET/POST | Single request; tracking | `M01` | `service_order:read` / `:write:own_org` | — | W4 |
| `/api/v1/service-orders/bulk` | POST | Bulk submission, set-committed | `M01` | `service_order:write:own_org` | — | W4 |
| `/api/v1/sla/status` | GET | Real-time and historical SLA with breaches and credits | `M01`/`M08` | `sla:read:own_org` | — | W4 |
| `/api/v1/invoices/{id}/decomposition` | GET | Itemised breakdown by site, department, asset, request | `M20` | `invoice:read:own_org` | — | W4 |
| `/api/v1/invoices/{id}/approve` | POST | Client-chain approval | `M20` | `invoice:approve:own_org` | **●** | W4 |
| `/api/v1/invoices/{id}/dispute` | POST | Raise a dispute with evidence | `M20` | `invoice:approve:own_org` | **●** | W4 |
| `/api/v1/msp/estate-health` | GET | Estate health, incidents, patch compliance | `M05`/`M48` | `estate_health:read:own_org` | — | **W5** |
| `/api/v1/certificates` | GET | Destruction and disposal certificates | `M06`/`M18` | `certificate:read:own_org` | — | W4 |
| `/api/v1/projects` | GET/POST | Rollout and decommission projects | `M67` | `project:read` / `:write:own_org` | — | **W7** |
| `/api/v1/customers/{id}/invoices` | GET | Invoice list and payment status | `M20` | `invoice:read:own_org` | — | W4 |

**`{id}` is convenience, not security.** The credential determines the organisation (`EA-03`,
`AP-005` `SC-02`). `P04` `AC-01` makes tenant isolation *"the highest-severity test for this
portal"* and names direct object reference, export, search and API as the paths tested. **A client
passing another organisation's identifier receives `403 auth.out_of_scope` on every one of them.**

### 4.6 ITSM ticket exchange — `INT-047`, W7

`05-03` §2.7 registers `INT-047` as bidirectional REST + webhook with ServiceNow or Jira, owned by
`M05`, at **W7, priority P3**.

**The mapping problem.** A client's ITSM and 1000FiX's service order are different objects with
different lifecycles. The mapping below is this file's **proposal**; none exists in the
repository, and building it per client is how each client ends up with a different definition of
"resolved".

| Client ITSM (typical) | 1000FiX | Direction | Note |
|---|---|:--:|---|
| Incident created | `POST /api/v1/service-orders` | → | Coverage validated first (§4.4) |
| Incident priority | `MD-028` priority and SLA class | → | **The client's priority scale is not ours.** Mapping is agreed per client and recorded |
| Incident assigned | `work_order.assigned` | ← | Technician name and photograph only; no employee record (`P04` §13) |
| Incident work note | Request update | ↔ | 1000FiX internal notes are **never** exchanged (`EA-02`) |
| Incident resolved | `service_order.completed` | ← | **Completed is not customer-accepted** (`AP-003` §4.7 `T-01`). A client mapping `resolved` to `completed` closes tickets before handover |
| Incident closed | `service_order.closed` | ← | The correct mapping for ticket closure |
| Incident reopened | **New** service order, linked | → | 1000FiX does not reopen a closed order (`AP-003` `EV-02`) |
| Change request | Not mapped | — | Out of scope; `M67` projects are the nearest equivalent, W7 |
| CMDB asset | Estate asset | ↔ | §4.3. **Serial is the join key**, not the client's CI identifier |
| SLA clock | `MD-028` SLA with pause rules | ← | The client's clock and ours will differ. **Ours is contractual** (`LG-015`); theirs is informational |

**Five rules for a client building C3.**

| # | Rule |
|---|---|
| **IT-1** | **The 1000FiX SLA clock is authoritative for contractual purposes.** A client dashboard showing a different figure is showing their own measurement, not the contract |
| **IT-2** | Map `closed`, not `completed`, to ticket closure |
| **IT-3** | A reopened ticket creates a **new** service order and carries the link. There is no reopen |
| **IT-4** | Internal notes are not exchanged in either direction. `internal_note` is never exposed to any external portal (`05-04` §5) |
| **IT-5** | Priority mapping is agreed once, recorded in the onboarding record, and changed by agreement — not by whoever edits the connector |

### 4.7 The four actions a machine cannot complete

`EA-09`, `AC-07`, `AP-005` §4.6.

| Action | Why gated | What an integration can do |
|---|---|---|
| Invoice approval | Financial consequence | Decompose, reconcile against the client's own request history, and present the difference to the approver |
| Invoice dispute | Financial consequence, and it stops the clock on payment terms | Assemble the evidence and pre-fill the dispute |
| Delegation change | Changes who may commit the client to spend | Prepare the change |
| Payment initiation | Financial consequence (`EA-09`) | Prepare |

**Plus a structural one.** `P04` §13: *"No 1000FiX internal role signs in to P04. An account
manager viewing a client's portal experience does so through `P03` under their own identity —
never by impersonation."* A client integration must therefore never be issued a credential that
1000FiX staff also use — and a client should not build a "1000FiX support access" account.

### 4.8 Events available to a corporate client

| Event | Source | Registered? | What it tells the client |
|---|---|:--:|---|
| `sla.breached` | `M01`/`M08` | ✔ | An SLA target was missed; credits follow (`AC-10`) |
| `asset.health_degraded` | `M48` | ✔ | A monitored asset's condition has worsened — an **indication, not a fault** (`AP-003` §4.5.6) |
| `contract.expiring` | `M08` | ✔ | Renewal horizon crossed |
| `service_order.completed` · `closed` · `cancelled` | `M01` | ✔ | Lifecycle. **Map `closed` to ticket closure** (`IT-2`) |
| *(unregistered)* `service_order.status_changed` | `M01` | ✖ | `P04` §12.3 names it; the inventory has eight specific events instead |
| *(unregistered)* `sla.at_risk` | `M01`/`M08` | ✖ | The inventory calls it `sla.warning` |
| *(unregistered)* `invoice.issued` | `M20` | ✖ | The inventory calls it `invoice.created` |
| *(unregistered)* `credit_note.issued` | `M20` | ✖ | **No credit-note event exists at all** — and credits are the SLA remedy this portal publishes |
| *(unregistered)* `contract.renewal_due` | `M08` | ✖ | The inventory calls it `contract.expiring` |
| *(unregistered)* `entitlement.threshold_crossed` | `M08` | ✖ | Distinct from `contract.entitlement_consumed` — a condition, not a delta |
| *(unregistered)* `asset.estate_reconciled` | `M17` | ✖ | **The output of `ES-7`**, with no registered event |
| *(unregistered)* `project.milestone_reached` | `M67` | ✖ | W7 |

> **Six of the ten events `P04` §12.3 consumes are not in the `05-03` §4.2 inventory**
> (`AP-003` §4.9). Four are naming divergence and are free to fix; two — `credit_note.issued` and
> `asset.estate_reconciled` — are genuinely missing, and both are outputs this guide promises the
> client. Recorded as `O-03`.

### 4.9 The disclosure boundary

`P04` §13 and `AC-12`, restated as an integration contract.

| # | Never in any `P04` payload | Basis |
|---|---|---|
| 1 | `unit_cost`, `total_cost`, `margin` | `05-04` §5, `EA-02`. **The client sees the price they are charged, never the cost basis** |
| 2 | `internal_note` | `05-04` §5 — never exposed to any external portal |
| 3 | `vendor_price` | `05-04` §5 |
| 4 | `technician_incentive_detail` | `05-04` §5 |
| 5 | Any employee record. Technician identity is a **name and photograph for the visit only** | `P04` §13 |
| 6 | Any other client organisation's data, through any path — direct object reference, export, search or API | `AC-01`, `EA-03` |

**`AC-12` requires automated payload inspection across every endpoint** to prove the first four.
That is a stronger control than a review and it is worth a client's integration team knowing it
exists, because it means the absence of those fields is enforced rather than intended.

**Every export is scoped, logged and attributed** (`AC-13`), and bulk export of personal data
requires approval and step-up (`EA-12`, `AP-005` §4.6).

### 4.10 Error conditions specific to corporate integrations

Codes are `AP-006`'s; no new codes are defined here (`CP-01`).

| Situation | Code | Remedy |
|---|---|---|
| Passing another organisation's identifier on any endpoint | `403 auth.out_of_scope` | Correct the identifier. `AC-01` is tested by penetration test; the response confirms nothing |
| Submitting a request without coverage validation, for work that is out of scope | `422 rule.not_on_contract` | Call `/coverage/validate` first (§4.4) |
| A user acting above their delegated limit | `422 rule.over_approval_limit` | `details.authorising_role`; route to the approver (`AC-05`) |
| Approving or disputing an invoice with a machine credential | `403 auth.step_up_required` | A human completes it (§4.7) |
| Estate load with one invalid line | `400 validation.failed` with `details.errors[]` per line | **The whole set is rejected** (`ES-1`). Correct and resubmit the set |
| Estate load placing an asset in a site that does not exist | `400 validation.reference_invalid` | Load structure first (`ES-5`) |
| Estate load exceeding the payload limit | `413 request.payload_too_large` | Split into sets. Each set is atomic in itself |
| Duplicate serial within one load | `409 resource.already_exists` | Serial is the identity (`ES-6`) |
| Resubmitting an identical load | `2xx` — original result returned | Not an error; `ES-4` idempotency |
| Bulk submission by looping the single endpoint | `429 ratelimit.exceeded` | Use `/service-orders/bulk` (`bulk` rate class) |
| Calling `/msp/estate-health` before W5 or `/projects` before W7 | `404 resource.not_found` | The capability has not shipped; see §4.5's wave column |
| Disputing an invoice outside the dispute window | `422 state.transition_invalid` | **The window length is not defined** — `P04` Q-08 |
| Requesting a cost or margin field | `403 data.disclosure_not_permitted` | §4.9; `AP-012` governs |

### 4.11 Onboarding — eight steps

`P04` §16.4 is emphatic that onboarding is **per client, account-manager-led, and sequenced by
contract value**, because *"a corporate client whose estate is loaded badly experiences the portal
as wrong data and does not return."* This is the technical track inside that.

| Step | What happens | Owner | Prerequisite |
|---:|---|---|---|
| 1 | Contract signed, including `LG-003` terms, the `AP-012` disclosure schedule, and **the integration modes committed with their waves** (§4.2) | Account Management + Legal | — |
| 2 | Account hierarchy configured — group, company, division, site, department (`MD-015`) | Account Management + client administrator | Step 1 |
| 3 | **Estate walked through with the client's administrator** before any bulk load, per `P04` §16.4 | Account Management | Step 2 |
| 4 | Sandbox credentials issued; the client's team works the `AP-001` golden path | Platform | Steps 1–2, `AP-010` |
| 5 | Estate load rehearsed in sandbox **including a deliberate reject**, so the client sees `ES-2` behaviour before production | Client + Platform | Step 4 |
| 6 | Coverage validation, request submission and invoice decomposition tested against the client's own contract shape | Client + Account Management | Step 5 |
| 7 | **Promotion review** — `AP-010` checklist plus the corporate-specific items below | Platform + Security | Step 6 |
| 8 | Production credentials issued; **first consolidated invoice decomposed and reconciled with the client before the portal opens to their wider user base** | Finance + Account Management | Step 7 |

**Corporate-specific promotion items, additional to `AP-010`:**

| # | Item |
|---|---|
| CP-1 | Estate loaded and **reconciled**, with strays and gaps accepted or queried (`ES-7`, `AC-11`) |
| CP-2 | Delegation chain defined by the client's administrator and **exported as an audit record** (`AC-06`) |
| CP-3 | Coverage validation demonstrated across all three outcomes — covered, chargeable, out of scope (`AC-04`) |
| CP-4 | Step-up rehearsed with a named human for each of the four gated actions |
| CP-5 | The disclosure boundary confirmed in writing, so no field on the §4.9 list is expected |
| CP-6 | Invoice decomposition reconciled against the client's own request history (`AC-09`) |
| CP-7 | Dispute lifecycle rehearsed end to end, including the acknowledgement reference (`AC-14`) |
| CP-8 | For C3: the ITSM state mapping (§4.6) agreed **in writing** and recorded, with priority mapping named |
| CP-9 | For C4: federation protocol, metadata exchange and a break-glass local account for the client administrator agreed |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `P04` | Every capability, control, endpoint and acceptance criterion originates there |
| `M17`, `M08`, `M01`, `M20`, `M05`, `M48`, `M06`, `M18`, `M67` | The modules behind the fifteen endpoints |
| `MD-015` | Corporate account hierarchy — onboarding step 2 |
| `MD-028`, `LG-015` | SLA definitions and service credits, which §4.4 transmits |
| `AP-005` | Credentials, scopes, step-up; its `O-01` blocks §4.5's scope column |
| `AP-004` | Webhook mechanism for §4.8 |
| `AP-006` | The codes §4.10 indexes |
| `AP-010` | Sandbox and the promotion gate |
| `AP-012` | The disclosure authority behind §4.9 |
| `EO-007`, `EO-008` | The business-facing onboarding this guide sits beside |
| `LG-003` | Portal terms |
| `DM-012` | Load templates — the nearest existing artefact to the estate file specification `O-02` needs |
| `06-02` `G4-05`, `G4-08` | The gate criteria this integration serves |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave from W4, and after each client onboarding |
| Trigger for out-of-cycle review | A `P04` capability landing in W5 or W7 · resolution of `P04` Q-05 or Q-09 · resolution of `AP-003` `O-06` · a client requesting a field on the §4.9 list · a disputed invoice traced to a decomposition the client could not reconcile |
| Owner | Platform Engineering Lead, with Account Management Lead accountable for §4.1's commercial boundary and Legal for §4.9 |
| Change control | Changes to §4.1 (boundary) require **Commercial Director and CTO**. Changes to §4.9 require **Legal Counsel and Security Lead** and an `AP-012` update. All need a `RF-006` entry and notice under `AP-011` |
| Version pinning | Pinned to **API version** (`CG-006` §5) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The capability the register calls "a condition of contract" is scheduled `P3` at W7.** `INT-047` client ITSM is priority `P3` — *"enhancement; opportunistic"* in `05-03` §2 — and lands at Month 30, twelve months after `P04` go-live. `INT-046` federation is `P2` at W6. **Clients sign in W4.** Either the priorities are wrong or the register justification is, and Commercial must not sell against W7 capability at W4 | Commercial Director with CTO | **W4 minus 4 months — before the first corporate contract is signed against it** |
| **O-02** | **No estate file specification exists.** C1 is the default mode for every client and the only one guaranteed at W4. `ES-1`…`ES-8` state the semantics; the columns, types, required fields, encoding and reject-report format are unwritten. `DM-012` holds migration load templates, which is a different artefact for a different purpose | `M17` owner with Data Migration Lead | **W4 minus 3 months — blocking every client onboarding** |
| **O-03** | **Six of the ten events `P04` consumes are unregistered** (`AP-003` §4.9). Four are naming divergence; **`credit_note.issued` and `asset.estate_reconciled` do not exist at all** — and both are outputs this guide promises: credits are the SLA remedy (`AC-10`) and reconciliation is `ES-7` and `AC-11` | Enterprise Architecture with `M20`, `M17` owners | **W4 minus 2 months** |
| **O-04** | **`P04` Q-09 unresolved: can a client's own API push estate changes?** It determines whether C2 is client-initiated or 1000FiX-initiated, which changes the authentication direction, the webhook direction and the client's build entirely | CTO with Account Managers | **W4 scoping** |
| **O-05** | **`P04` Q-05 unresolved: does any client require federated SSO, and on what protocol?** SAML 2.0 and OIDC are different builds. `INT-046` is W6; a W4 client requiring federation has no path | CTO with Account Managers | **W4 build** |
| **O-06** | **Delegated limits and service credentials are unreconciled.** `AC-05` blocks a user acting above their delegated limit; a machine credential is not a user and `05-04` §7's approval matrix is expressed in human roles. Whether a client's service account inherits a limit, holds its own, or cannot submit above any limit is undefined | Security Lead with `M29` owner | **W4 design** |
| **O-07** | **The invoice dispute window is undefined** (`P04` Q-08), and so is what happens to payment terms while a dispute is open. §4.10 documents an error for a condition whose boundary nobody has set | CFO | **W4 design** |
| **O-08** | **No ITSM state mapping exists** and `CP-8` requires one per client. Without a published default, each client's mapping is negotiated from zero and "resolved" means something different in each — the failure `IT-2` describes | `M05` owner with Platform Engineering Lead | W7 minus 3 months |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] **The `P04` §3.2 boundary stated first, with the does/does-not table and the reason it is drawn there**
- [x] Four integration modes with their **waves and priorities**, and the commercial contradiction stated rather than smoothed
- [x] Estate exchange specified as eight contract points, with the missing file specification recorded
- [x] Coverage validation given the emphasis its acceptance criterion carries
- [x] All fifteen endpoints tabled with scope, step-up and **wave** — the column `P04` §12.5 lacks
- [x] ITSM state mapping proposed with five rules, and the completed-versus-closed trap named
- [x] Four step-up-gated actions plus the no-impersonation structural rule
- [x] Events listed with registration status; six unregistered marked as such
- [x] Disclosure boundary stated as six absolutes, with `AC-12`'s automated enforcement noted
- [x] Corporate-specific error conditions indexed to `AP-006` codes, no new codes invented
- [x] Eight-step onboarding with nine corporate-specific promotion items
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` ITSM integration is `P3`/W7 against a W4 contractual condition — outstanding; a commercial exposure**
- [ ] **`O-02` no estate file specification — outstanding; blocks every client onboarding**
- [ ] **`O-03` `credit_note.issued` and `asset.estate_reconciled` unregistered — outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Commercial Director**
- [ ] Bengali counterpart — n/a; developer audience, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
