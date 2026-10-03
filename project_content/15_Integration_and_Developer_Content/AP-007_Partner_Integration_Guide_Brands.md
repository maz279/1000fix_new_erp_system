---
id: AP-007
title: Partner Integration Guide — Brands
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
author: Platform Engineering with Commercial and Warranty
reviewers: [CTO, Solution Architect, Commercial Director, Warranty Claims Manager, Inventory Manager, Quality Manager, Security Lead, Legal Counsel, Content Design Lead]
approver: Content Design Lead with Commercial Director
content_class: D
purpose: >
  The integration guide a brand partner's development team reads to connect their warranty system
  to 1000FiX — what can be exchanged by API and what cannot, the claim, consignment, rate-card and
  bulletin flows, the data they receive and the data they will never receive, and the onboarding
  sequence from agreement to production. `P08` exists to move 17+ brands off email; a brand
  partner with their own warranty system will only move if the integration path is documented
  before the commercial conversation, and every brand that stays on email keeps a manual claims
  process the company has costed out of its business case.
traces_to: [P08, P08 FR-POR-229, P08 FR-POR-246, P08 FR-POR-252, P08 FR-POR-254, P08 T-03, P08 §12.4, P08 §12.5, M09, M15, M17, M22, M23, M11, M24, M48, M52, 05-03, 05-03 IP-04, 05-03 IP-10, 05-04 §8, EA-05, AP-001, AP-002, AP-004, AP-005, AP-006, AP-010, AP-011, AP-012, EO-003, EO-004, MD-017, LG-005, DT-033, HC-010, NT-013]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P08_Brand_Partner_Portal.md §5 capability areas FR-POR-229…FR-POR-254, §6 T-01…T-19, §12.4 external integrations INT-P08-01…04, §12.5 the fifteen API endpoints P08 consumes, §13 brand-side roles and the field-level restrictions, §16.4 brand onboarding
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §8 EA-01…EA-12, in particular EA-05 "a brand partner sees only claims and service data relating to their own brand"
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 G4-01 claims auto-created within 24 h and submitted within 72 h; G4-02 first-submission approval rate ≥ 90%
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-07_Category_H_Audit_and_Repository_Integrity_Report.md H2-12 — the "17+ brands" figure recorded as unverified while an M22 control depends on it; carried into project_content MD-017
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Partner Integration Guide — Brands

| Item | Value |
|---|---|
| Audience | Brand partner integration and warranty-systems teams |
| Portal | `P08` Brand Partner Portal · code `BPP` |
| Integration modes | 3 — portal only, API, hybrid (§4.2) |
| Endpoints available | 15 (`P08` §12.5) |
| Events available | 9 (§4.8) |
| Actions requiring a human | 5 — step-up gated (§4.7) |
| Data never disclosed | 8 categories (§4.9) |
| Onboarding steps | 9 (§4.11) |
| Wave | W4 — aligned with `P08` and `EO-003` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume. The **endpoint reference table**
> required by `CG-009` §3 is §4.5. The **error catalogue table** required by `CG-009` §3 is
> §4.10 — the brand-specific error conditions, referencing `AP-006` codes rather than defining
> new ones (`CP-01`).

---

## 1. Purpose

`P08`'s register justification is blunt: *"Brand partners have their own warranty systems; the
integration guide determines whether they use `P08` or email."*

The commercial position behind that sentence is worth stating, because it is what makes this a
`P2` file that behaves like a `P1` one. `P08` §12.4 `INT-P08-01` describes claim exchange with
brand warranty systems *"by API where the brand supports it; portal entry otherwise"*. `G4-01`
requires claims auto-created within 24 hours and submitted within 72; `G4-02` requires a
first-submission approval rate of 90%. Both targets are achievable through the portal by a human,
and both are **easier** through an API — but only if the brand's own team can see, before the
commercial conversation, exactly what integrating costs them.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| A published integration path | Every brand conversation starts with "can we integrate?" answered by a meeting. Seventeen-plus brands, seventeen-plus meetings, and the answer differs by whoever attends |
| The step-up constraint (§4.7) | A brand builds an end-to-end automated claim decision flow and discovers at acceptance that approval above the value threshold requires a human in the portal. The rework lands on the brand, and the relationship pays for it |
| The disclosure boundary (§4.9) | A brand asks for customer contact details to "verify the claim". Without a written, pre-agreed boundary that conversation is had per brand, per request, by whoever is on the call |
| The rate-card versioning contract | A brand publishes a rate change and expects it to apply to claims already decided. `T-06` says it does not. Undocumented, this becomes a reconciliation dispute |
| The consignment reconciliation contract | The monthly pack is published and unacknowledged; stock variance accumulates and surfaces at year end as a commercial argument |
| An onboarding sequence | Each brand is onboarded differently, and the first one sets an accidental precedent for the other sixteen |

---

## 2. Scope

**In scope.** The three integration modes and how to choose; what a brand may exchange by API;
the claim, consignment, rate-card, quality and bulletin flows as integration contracts; the
endpoint and event reference; the human-required actions; the disclosure boundary; audit-window
mechanics; error conditions; and the nine-step onboarding sequence.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| The brand's business onboarding, portal walkthrough, contacts | `EO-003` Brand Partner Onboarding Pack | This file is for the brand's **developers**; `EO-003` is for their warranty administrators |
| Claim rules, required evidence, rejection reasons | `EO-004` | The **content** of a good claim; this file carries how it is transmitted |
| Portal terms, liability, data-protection clauses | `LG-005` Brand Partner Portal Terms | Linked, never restated (`CP-01`) |
| Which fields the brand receives and the lawful basis | `AP-012` | §4.9 states the boundary; `AP-012` is the register and the authority |
| Authentication, scopes, credentials, limits | `AP-005` | Referenced throughout; not restated |
| Error codes | `AP-006` | §4.10 indexes brand-specific conditions to existing codes |
| Webhook signature, retry, idempotency | `AP-004` | §4.8 lists which events; `AP-004` gives the mechanism |
| Sandbox access and test data | `AP-010` | Step 4 of onboarding |
| Claim document format (the printed claim) | `DT-033` | A document, not an interface |
| Brand-facing help and notifications | `HC-010`, `NT-013` | Different audience — the warranty administrator, not the developer |
| The brand master register | `MD-017` | Which brands exist, their authorisation scope and claim rules |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Brand warranty-systems developers** | The primary audience. Typically working in the brand's regional or global IT function, not in Bangladesh |
| **Brand integration architects** | Deciding whether to integrate at all, and at what depth (§4.2) |
| **1000FiX Commercial and Account teams** | The document they send with a brand agreement, so the technical answer precedes the commercial one |
| **1000FiX Warranty Claims Officer (`R28`)** | Understanding what an integrated brand does automatically and what still needs a human |
| **1000FiX Platform Engineering** | Building and supporting `INT-P08-01` per brand |
| **Legal** | The disclosure boundary at §4.9 is a contractual position as much as a technical one |

---

## 4. Content

### 4.1 What the relationship actually is

Stated first because integration decisions follow from it and because it is frequently
misunderstood in both directions.

| | 1000FiX | The brand |
|---|---|---|
| Performs the repair | ● | |
| Owns the customer relationship | ● | |
| Holds the device and the evidence | ● | |
| Owns the warranty obligation | | ● |
| Decides the claim | | ● |
| Sets the rate card and the claim rules | | ● |
| Reimburses | | ● |
| Owns consignment stock held at 1000FiX | | ● |
| Holds custody of that stock | ● | |

**Consequences that surprise people.** The brand is the **decider and the payer**, not the
operator — so the API is shaped around *the brand receiving work and returning decisions*, not
around the brand instructing 1000FiX. And 1000FiX holds the customer relationship — so
`P08` `T-03` makes customer anonymity the portal's **highest-severity control**, and no
integration depth changes it.

### 4.2 Three integration modes

| Mode | What it means | Suits a brand that | Effort on the brand |
|---|---|---|---|
| **M1 — Portal only** | Brand staff work in `P08`. No integration | Has fewer than ~50 claims a month with 1000FiX, or no regional IT capacity | None |
| **M2 — Hybrid** *(recommended default)* | Claims and reconciliation flow by API; **decisions above the threshold, rate-card publication and remittance upload stay in the portal** | Has a warranty system and wants claim data in it, but cannot justify a full build | Low — read endpoints and webhooks only |
| **M3 — Full API** | Everything the API permits, including decisions below the step-up threshold | Has a mature regional warranty platform and material volume | Moderate |

> **M2 is the recommended default and the reason is §4.7, not caution.** Five actions require a
> human step-up and cannot be automated at all. A brand that builds M3 still needs a human for
> those five, so M3's incremental benefit over M2 is automated decisions **below** the value
> threshold — real, but smaller than it first appears. Stating this before a brand estimates
> their build is the single most useful thing this guide does.

**No mode is exclusive.** A brand may run M2 for claims and M1 for quality concerns. Modes are
per capability, not per brand, and the onboarding record (§4.11 step 2) captures which.

### 4.3 The claim flow as an integration contract

```
  1000FiX side                                          Brand side
  ────────────                                          ──────────
  Warranty-classified job (M01/M09)
        │  claim auto-created within 24 h  (G4-01)
        ▼
  warranty_claim.created  ── internal only ──✗  NOT visible to the brand
        │
        │  evidence pack assembled (M17): device identity and serial,
        │  purchase proof, fault history, diagnostic report,
        │  before/after photographs, parts with serials, labour,
        │  technician certification for this brand  (FR-POR-230)
        │
        │  validated against the brand's own published claim rules (FR-POR-247)
        │      ✖ incomplete ──► held internally in P03, NOT submitted  (T-05)
        ▼
  warranty_claim.submitted  ── within 72 h  (G4-01) ──────►  GET /warranty/claims
        │                                                     webhook: claim submitted
        │                                              ┌──────────────────────────┐
        │                                              │ approve / part-approve / │
        │                                              │ reject with reason /     │
        │                                              │ request information      │
        │                                              └────────────┬─────────────┘
        │                                                           │ POST …/decision
        ▼                                                           │  (step-up above threshold)
  warranty_claim.decided  ◄──────────────────────────────────────────┘
        │
        ▼
  Reimbursement expected ──► remittance advice uploaded by the brand
        │                     matched line by line against approved claims (FR-POR-238)
        ▼
  Reconciliation — unmatched lines presented from BOTH sides (T-07)
```

**Six contract points a brand's developer must know.**

| # | Point | Why it matters |
|---|---|---|
| **CL-1** | A claim becomes visible to the brand at **submission**, not creation | `warranty_claim.created` is internal (`AP-003` §4.5.8). A brand polling for created claims sees nothing |
| **CL-2** | Submission requires a **complete** evidence pack against the brand's own published rules | `T-05`. Incomplete claims are held in `P03` and never reach the brand — which is why `G4-02`'s 90% first-submission approval target is achievable at all |
| **CL-3** | **Part-approval is a first-class outcome**, at line level | A decision payload with a single boolean cannot express it. This is the most common integration modelling error |
| **CL-4** | **Request-more-information is a claim state with a clock and an owner**, not a comment | `FR-POR-233` — *"never an email"*. An integration that models it as a note loses the clock |
| **CL-5** | A decision is **attributable** — timestamp and deciding user, on the brand's side | `FR-POR-232`. A service-account decision must still carry a named human in `details`, or the audit trail names a robot |
| **CL-6** | The **rate card version that governed the claim is recorded**, and a later rate change never alters a decided claim | `T-06`. Reconciliation disputes come from brands assuming the opposite |

### 4.4 Consignment, rate cards, quality and bulletins

| Flow | Contract | Integration note |
|---|---|---|
| **Consignment position** | The brand's parts in 1000FiX custody: received, consumed on warranty, returned, damaged, outstanding — by part and location (`FR-POR-241`) | Read-only by API. Any figure decomposes to the claims and jobs that consumed it (`FR-POR-243`) |
| **Monthly reconciliation pack** | Opening, received, consumed, returned, closing, variance — published monthly, **acknowledgement captured** (`FR-POR-242`) | Acknowledgement is a **write** and is step-up gated. An integration can fetch the pack and prepare the response; a human confirms it |
| **Replenishment** | 1000FiX requests; the brand confirms, part-confirms or declines with an expected date (`FR-POR-244`) | Fully automatable — no step-up |
| **Defective returns** | 1000FiX notifies; the return is tracked to credit or replacement (`FR-POR-245`) | Fully automatable |
| **Rate card publication** | The brand publishes and versions labour rates, parts pricing and claim rules with an **effective date** (`FR-POR-246`) | **Step-up gated.** Publication is a commercial act with financial consequence |
| **Claim rules** | The brand states required evidence, labour-time allowances and part eligibility; 1000FiX validates **before** submission (`FR-POR-247`) | Published with the rate card. **The highest-leverage thing a brand can automate** — better rules mean fewer rejections, which is `G4-02` |
| **Service performance** | Volume, turnaround, first-time fix, rework rate, CSAT — brand-scoped (`FR-POR-248`) | Read-only. Aggregated; no individual job or customer resolvable |
| **Cohort reliability** | Failure-mode incidence by model, age band and usage cohort, **with population as denominator**, suppressed below a minimum population (`FR-POR-249`, `T-04`) | Read-only, and the suppression is not negotiable — it is what stops a cohort resolving to one customer |
| **Quality concern and CAPA** | The brand raises a concern; `M23`'s CAPA response and closure are shown (`FR-POR-251`) | Automatable both directions |
| **Bulletins and recalls** | The brand submits technical bulletins, service notices and **recall notifications**; 1000FiX acknowledges and reports execution status (`FR-POR-254`) | Automatable. **The safety-critical flow** — and see `O-04`, because `recall.execution_updated` is not a registered event |
| **Audit mode** | A scheduled, time-boxed window granting structured access to calibration records, technician certifications, claim evidence and process records, every access logged, closing automatically (`FR-POR-252`, `T-08`) | §4.6 |

### 4.5 Endpoint reference

The endpoint reference table required by `CG-009` §3. Paths and owners from `P08` §12.5; the scope,
step-up and mode columns are this file's contribution.

| Endpoint | Method | Purpose | Owner | Scope *(proposed — `AP-005` `O-01`)* | Step-up | Mode |
|---|:--:|---|:--:|---|:--:|:--:|
| `/api/v1/warranty/claims` | GET | Brand-scoped claim queue with filters | `M09` | `warranty_claim:read:own_brand` | — | M2 |
| `/api/v1/warranty/claims/{id}` | GET | Claim with the complete evidence pack | `M09`/`M17` | `warranty_claim:read:own_brand` | — | M2 |
| `/api/v1/warranty/claims/{id}/decision` | POST | Approve, part-approve, reject, request information | `M09` | `warranty_claim:approve:own_brand` | **● above threshold** | M3 |
| `/api/v1/warranty/claims/bulk-decision` | POST | Bulk decision with confirmation | `M09` | `warranty_claim:approve:own_brand` | **● always** | M3 |
| `/api/v1/warranty/reconciliation` | GET | Period reconciliation, line by line | `M09`/`M52` | `warranty_claim:read:own_brand` | — | M2 |
| `/api/v1/warranty/remittance` | POST | Upload remittance advice; receive the matching result | `M52` | `remittance:write:own_brand` | **●** | M3 |
| `/api/v1/consignment/{brand}/balance` | GET | Consignment position by part and location | `M15` | `consignment:read:own_brand` | — | M2 |
| `/api/v1/consignment/{brand}/reconciliation` | GET/POST | Monthly pack; acknowledgement | `M15` | `consignment:read` / `:write:own_brand` | **● on POST** | M2/M3 |
| `/api/v1/brands/{id}/rate-card` | POST/GET | Publish and version rates and claim rules | `M11`/`M09` | `rate_card:read` / `:write:own_brand` | **● on POST** | M3 |
| `/api/v1/brands/{id}/performance` | GET | Brand-scoped service performance | `M25` | `performance:read:own_brand` | — | M2 |
| `/api/v1/brands/{id}/reliability` | GET | Cohort failure analysis above minimum population | `M17`/`M48` | `reliability:read:own_brand` | — | M2 |
| `/api/v1/brands/{id}/certifications` | GET | Technicians certified on this brand | `M22` | `certification:read:own_brand` | — | M2 |
| `/api/v1/brands/{id}/audit-window` | POST/GET | Schedule, open, access, close, log | `P08` | `audit_window:write:own_brand` | **●** | M3 |
| `/api/v1/quality/concerns` | POST/GET | Raise a concern; read the CAPA response | `M23` | `quality_concern:write:own_brand` | — | M2/M3 |
| `/api/v1/brands/{id}/bulletins` | POST | Technical bulletin and recall notification | `M24`/`M23` | `bulletin:write:own_brand` | — | M3 |

**Every path is brand-scoped, and two are scoped twice.** `{brand}` and `{id}` in the paths above
are convenience, not security: the credential already determines the brand (`EA-05`, `EA-11`,
`AP-005` `SC-02`). **A brand passing another brand's identifier receives `403 auth.out_of_scope`,
never that brand's data and never a `404` that would confirm the brand exists.**

### 4.6 Audit mode

`FR-POR-252` and `T-08`. Brand partner audits are a contractual reality; this is how they work
without becoming a standing access grant.

| # | Property |
|---|---|
| **AU-1** | An audit window is **scheduled**, with a start, an end and an explicit scope |
| **AU-2** | The scope may include calibration records (`M45`), technician certifications (`M22`), claim evidence and process records — **nothing else** |
| **AU-3** | Access requires the auditor sub-role and **MFA** (`P08` §13) |
| **AU-4** | **Every record access inside the window is logged** with user, record and timestamp |
| **AU-5** | The window **closes automatically** at its end. There is no manual extension inside the window; a new window is scheduled |
| **AU-6** | Audit mode does **not** widen the disclosure boundary at §4.9. An auditor sees more *records*, never more *fields* |
| **AU-7** | Audit access is API-available, so a brand's audit tooling can pull evidence rather than screen-scrape — but the window still governs |

### 4.7 The five actions a machine cannot complete

`EA-09` requires MFA for any external action with financial consequence; `P08` `T-09` names the
gated actions. **A server-to-server credential cannot satisfy a step-up challenge** (`AP-005`
§4.6). Therefore:

| Action | Why gated | What an integration **can** do |
|---|---|---|
| Claim approval above the value threshold | Financial consequence | Prepare and queue the decision; a human confirms in `P08` |
| Bulk claim decision | Aggregated financial consequence, and `T-10` requires the total value to be shown | Compute the set and pre-select it |
| Remittance advice upload | Financial reconciliation | Prepare the file; a human uploads |
| Rate card publication | Commercial and financial consequence, versioned | Prepare the version and its effective date |
| Consignment reconciliation acknowledgement | Confirms a stock position with financial effect | Fetch, verify against the brand's own records, present the difference |

> **Read the right-hand column before estimating an M3 build.** In every case the integration does
> the work and a human does the confirmation, which is a materially cheaper build than full
> automation — and the only one the auth model permits. **How the step-up requirement is signalled
> to a machine caller is undefined** (`AP-005` `O-07`); until it is, an integration will meet it as
> an unexplained `403`.

### 4.8 Events available to a brand

Subject to the three filters in `AP-004` §4.8 — platform events never, scope-filtered, and
payload-filtered per `AP-012`.

| Event | Source | What it tells the brand |
|---|---|---|
| `warranty_claim.submitted` | `M09` | A new claim is in the queue with its evidence pack |
| `warranty_claim.decided` | `M09` | A decision was recorded — including one made in the portal by the brand's own staff, which is how an M2 brand keeps its system in step |
| `capa.closed` | `M23` | The response to a quality concern is complete and verified |
| `certification.expiring` | `M22` | A technician certified on this brand is approaching expiry |
| `certification.expired` | `M22` | **A hard dispatch block is now in force** for that technician on this brand |
| `asset.status_changed` | `M17` | Where the asset is one this brand has an interest in |
| `part.consumed` | `M15` | Where the part came from this brand's consignment stock |
| *(unregistered)* `stock.consignment_consumed` | `M15` | `P08` §12.3 names it; **not in the `05-03` §4.2 inventory** — `AP-003` §4.9 |
| *(unregistered)* `stock.consignment_reconciled` · `stock.rtv_raised` · `claim.evidence_incomplete` · `recall.execution_updated` | `M15`/`M09`/`M23` | Four further events `P08` consumes that are **not registered** — `AP-003` `O-06` |

> **Five of the nine events a brand integration needs are unregistered.** That is not a
> presentational problem: `claim.evidence_incomplete` **suppresses submission**, and
> `recall.execution_updated` carries product-safety status. Recorded as `O-04`.

### 4.9 The disclosure boundary

`P08` `T-03` makes this the portal's highest-severity control and tests it as such. It is
restated here as an integration contract because a brand's developer will otherwise design
around fields that are never coming.

**Never present in any `P08` payload, by any path, in any mode:**

| # | Never disclosed | Basis |
|---|---|---|
| 1 | Customer name, contact number, email or address | `P08` `T-03`, `EA-02` |
| 2 | Customer NID or any government identifier | `T-03`, `NFR-086`, `NFR-099` |
| 3 | Any **other device** owned by that customer | `T-03` |
| 4 | Any service history **unrelated to the claim** | `T-03`, `EA-05` |
| 5 | 1000FiX internal cost or margin | `EA-02`, `05-04` §5 |
| 6 | Technician personal data beyond certification status | `05-04` §5, `T-03` |
| 7 | **Another brand's data**, in any aggregate that could isolate it | `EA-05` |
| 8 | Any commercial term not part of this brand's own agreement | `EA-02` |

**What the brand does receive** is the evidence needed to decide a claim: device identity and
serial, purchase proof, fault and diagnostic detail, photographs, parts with serials and
provenance, labour, and the technician's certification for that brand (`FR-POR-230`). That set is
sufficient to decide, which is the whole `IP-10` minimisation test.

**Cohort suppression is part of this boundary, not a separate control.** Reliability analytics are
suppressed below a configured minimum population (`T-04`) so that a cohort cannot resolve to an
individual device or customer. A brand asking for a lower threshold is asking to defeat control 1
by arithmetic, and the answer is no.

**`AP-012` is the authority.** This section states the boundary; the field-by-field register and
the lawful basis for each disclosure are `AP-012`'s, and the brand's own extract from it is
published in `AP-001` section 9.

### 4.10 Error conditions specific to brand integrations

Codes are `AP-006`'s; this indexes the ones a brand will actually meet. No new codes are defined
here (`CP-01`, `AP-006` `CG-03`).

| Situation | Code | Remedy |
|---|---|---|
| Requesting another brand's claim, or passing another brand's `{id}` | `403 auth.out_of_scope` | Correct the identifier. The response will not confirm whether the claim exists |
| Deciding above the value threshold with a machine credential | `403 auth.step_up_required` | A human confirms in `P08` (§4.7) |
| Publishing a rate card with a machine credential | `403 auth.step_up_required` | As above |
| Deciding a claim already decided | `422 state.already_in_target` | Treat as success; an earlier call succeeded and its response was lost |
| Deciding a claim in `information_requested` | `422 state.transition_invalid` | `details.allowed_transitions` |
| Requesting cohort reliability below the minimum population | `422 export.result_too_large` **or** an empty cohort with a suppression note | Widen the cohort. Suppression is not negotiable (`T-04`) |
| Requesting a field on the §4.9 list | `403 data.disclosure_not_permitted` | Not resolvable by the brand; `AP-012` governs |
| Accessing audit-scope records outside a window | `403 auth.out_of_scope` | Schedule a window (§4.6) |
| Uploading a remittance advice that matches nothing | `2xx` with unmatched lines from **both** sides | Not an error. `T-07` presents the difference rather than absorbing it |
| Rate card with an effective date in the past | `400 validation.date_range_invalid` | A rate change never retroactively alters a decided claim (`T-06`) |
| Bulk decision exceeding the payload limit | `413 request.payload_too_large` | Split the set, or use filters to narrow it |
| Exceeding the rate limit | `429 ratelimit.exceeded` | `partner-standard` class proposed (`AP-005` §4.7) — honour `Retry-After` |

### 4.11 Onboarding — nine steps

`P08` §16.4 sequences brand onboarding commercially. This is the technical track that runs
alongside it.

| Step | What happens | Owner | Prerequisite |
|---:|---|---|---|
| 1 | Brand agreement signed, including the `LG-005` portal terms and the `AP-012` disclosure schedule | Commercial + Legal | — |
| 2 | **Integration mode chosen per capability** (§4.2) and recorded | Commercial + Platform | Step 1 |
| 3 | Brand registered in `MD-017` with its authorisation scope, claim rules and contacts | Commercial | Step 1 |
| 4 | **Sandbox credentials issued**; brand's team works the `AP-001` golden path | Platform | Steps 2–3, and `AP-010` |
| 5 | Brand publishes its **claim rules and rate card** in sandbox and verifies the pre-submission validation behaves as they expect | Brand + Warranty | Step 4 |
| 6 | Brand builds and tests: claim read, decision write, webhook receipt with signature verification | Brand | Step 5 |
| 7 | **Promotion review** — the `AP-010` production checklist, plus the brand-specific items below | Platform + Security | Step 6 |
| 8 | Production credentials issued; first claims flow with a parallel manual check for the first cycle | Platform + Warranty | Step 7 |
| 9 | First **monthly reconciliation** completed and acknowledged end to end | Finance + Brand | Step 8 |

**Brand-specific promotion items, additional to `AP-010`:**

| # | Item |
|---|---|
| BP-1 | The brand's claim rules are published and current in `M09`, and pre-submission validation has been demonstrated to reject an incomplete pack |
| BP-2 | The brand's rate card is published with an effective date, and the version-governs-the-claim behaviour has been demonstrated |
| BP-3 | Webhook signature verification demonstrated **including a deliberate failure** (`AP-004` §4.11) |
| BP-4 | Step-up path rehearsed with a named human on the brand side for each of the five gated actions |
| BP-5 | The disclosure boundary confirmed in writing by the brand, so no field on the §4.9 list is expected |
| BP-6 | Escalation contacts exchanged both ways, with a named human — not a shared mailbox (`AP-004` `CO-10`) |
| BP-7 | Reconciliation responsibility agreed: who reconciles what, on what cadence, and what happens to an unresolved difference |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `P08` | The portal this guide integrates with. Every capability, control and endpoint originates there |
| `M09`, `M15`, `M17`, `M11`, `M22`, `M23`, `M24`, `M52` | The modules behind the fifteen endpoints |
| `AP-005` | Credentials, scopes, step-up. §4.7 is meaningless without it, and its `O-01` blocks §4.5's scope column |
| `AP-004` | Webhook mechanism for §4.8 |
| `AP-006` | The codes §4.10 indexes |
| `AP-010` | Sandbox for onboarding step 4 and the promotion gate at step 7 |
| `AP-012` | The disclosure authority behind §4.9 |
| `AP-011` | Notice for any change to these contracts |
| `EO-003`, `EO-004` | The business-facing onboarding and claim-rules content this guide sits beside |
| `MD-017` | The brand register — onboarding step 3 |
| `LG-005` | Portal terms, referenced at step 1 |
| `DT-033` | The claim document format |
| `06-02` `G4-01`, `G4-02` | The gate criteria this integration exists to meet |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave from W4, and after each brand onboarding |
| Trigger for out-of-cycle review | A new `P08` capability · a change to the step-up gating · resolution of `AP-003` `O-06` (the five unregistered events) · a brand requesting a field on the §4.9 list · a reconciliation dispute traced to this guide |
| Owner | Platform Engineering Lead, with Commercial Director accountable for §4.2's commercial framing and Legal for §4.9 |
| Change control | Changes to §4.9 (disclosure) require **Legal Counsel and Security Lead** approval and an `AP-012` update. Changes to §4.7 (step-up) require CTO and Security Lead. Both need a `RF-006` entry and notice under `AP-011` — brands build against these |
| Version pinning | Pinned to **API version** (`CG-006` §5) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **No brand has been surveyed for API capability.** `INT-P08-01` reads *"where an interface exists"* and `MD-017` is the register that would record it. **The number of brands able to integrate at all is unknown**, so the effort behind §4.2 modes and the value of `P08`'s API surface are both unestimated | Commercial Director with Platform Engineering Lead | **W4 minus 4 months** |
| **O-02** | **The "17+ brands" figure remains unverified.** Audit `00-07` H2-12 recorded it as unverified while an `M22` control depends on it, and `MD-017` is where it is meant to be closed. Every effort and adoption figure in this guide's scope rests on it | Commercial Director | W4 |
| **O-03** | **The claim value threshold for step-up is not stated anywhere.** `P08` `T-09` requires MFA "above a value threshold"; no figure exists in `P08`, `05-04` §7 or `MD-028`. **A brand cannot design its decision flow without it**, and it is the boundary between M2 and M3 | Commercial Director with CFO | **W4 design** |
| **O-04** | **Five of the nine events a brand integration needs are unregistered** — `stock.consignment_consumed`, `stock.consignment_reconciled`, `stock.rtv_raised`, `claim.evidence_incomplete`, `recall.execution_updated` (`AP-003` §4.9). Two carry control and safety consequence | Enterprise Architecture with `M15`, `M09`, `M23` owners | **W4 minus 2 months** |
| **O-05** | **Brand SSO protocol undecided.** `INT-P08-04` supports federated access "where a brand requires it"; no protocol is named and no brand has been asked. `INT-046` corporate SSO is scheduled W6, two waves after `P08` | CTO with Commercial | W4 build |
| **O-06** | **No per-brand rate limit exists.** `AP-005` `O-03`; the `partner-standard` class in §4.10 is a proposal. A brand running a nightly bulk pull of a month's claims will discover its limit in production | Platform Engineering Lead | W4 |
| **O-07** | **Reconciliation responsibility is unassigned.** `BP-7` requires it to be agreed per brand; no default exists, and `T-07` deliberately presents unmatched lines from both sides without assigning who resolves them. An unowned difference becomes a year-end commercial dispute | Finance Manager with Commercial Director | W4 |
| **O-08** | **Audit-mode API access has no negative test owner.** `AU-4` logs every access and `AU-5` closes automatically; `TS-017` does not cover time-boxed grant expiry, and an audit window that fails to close is a standing access grant to a third party | QA Lead with Security Lead | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] The commercial relationship stated before the technical contract, because the technical shape follows from it
- [x] **Three integration modes with a recommended default and the reason the recommendation is not caution**
- [x] Claim flow drawn as a two-sided contract with six named contract points
- [x] All fifteen `P08` endpoints tabled with scope, step-up and mode
- [x] **The five actions a machine credential can never complete, with what an integration can do instead**
- [x] Events listed, with the five unregistered ones marked as unregistered rather than promised
- [x] **Disclosure boundary stated as eight absolutes, with cohort suppression identified as part of it**
- [x] Brand-specific error conditions indexed to `AP-006` codes, with no new codes invented (`CP-01`)
- [x] Nine-step onboarding with seven brand-specific promotion items
- [x] Audit mode specified with automatic closure and the fields-versus-records distinction
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` no brand surveyed for API capability — outstanding; the audience size is unknown**
- [ ] **`O-03` step-up value threshold unstated — outstanding; blocks every brand's decision-flow design**
- [ ] **`O-04` five required events unregistered — outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Commercial Director**
- [ ] Bengali counterpart — n/a; developer audience, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
