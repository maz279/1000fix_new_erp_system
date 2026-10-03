---
id: FIX-ERP2-M33
module_id: M33
module_code: CPM
module_name: Customer & Party Master Management
category: B — Customer Engagement & Experience
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Commercial Squad
priority: P0
wave: W1
regulatory_verified: 2026-08-12
---

# M33 — Customer & Party Master Management
### Category B · Code `CPM` · ★ New module in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M33 |
| **Module code** | `CPM` |
| **Category** | B — Customer Engagement & Experience |
| **Status** | ★ **New** — split from M07 CRM after enterprise benchmarking |
| **Priority** | **P0** — cannot be descoped; every other module depends on it |
| **Delivery wave** | W1 (Months 1–4) |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `contacts`, `res.partner`) + L5 (custom) |
| **Custom modules** | `cd_party_master`, `cd_party_hierarchy`, `cd_consent`, `cd_bd_address`, `cd_identity_doc` |
| **Requirement range** | FR-CPM-001 … FR-CPM-052 |
| **Requirement count** | 52 |
| **Effort estimate** | 24 person-weeks |
| **Depends on** | M29 Identity & Security · M28 Integration · M30 Platform Admin · M64 Master Data Management |
| **Depended on by** | **Every module in the system** — M01, M04, M07, M08, M09, M10, M12, M13, M14, M20, M27, M32, M34, M35, M38, M40, M53 |

---

## 2. Purpose

M33 answers one question, authoritatively, for every other module in the ERP:
**who is this party?**

It holds the identity, hierarchy, addresses, verification documents, consent and credit
standing of every customer, corporate group, household, dealer, government body, marketplace
seller and brand partner the Company deals with. Nothing else in the system holds a competing
copy.

### Why It Exists

The v1.0 plan buried customer master data inside the CRM module. Every enterprise ERP
separates the two, because they answer to different masters: master data answers to
**governance and data quality**; CRM answers to **commercial pursuit**. Merging them means a
salesperson chasing a deal can silently change a customer's legal name, tax identifier or
credit limit — and that the data quality of the entire enterprise depends on the discipline
of the sales team.

There is a second, sharper reason. The **Bangladesh Personal Data Protection Act 2026**
requires consent that is clear, explicit, specific and freely given; a transparency notice
before or during processing; data-subject rights including rectification within 30 days; and
restriction on cross-border transfer of sensitive personal data such as NID, passport and TIN.
Those obligations attach to the **party record**. They cannot be discharged if the party
record is scattered across seven modules.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.4 (BR-CRM-001…010) | Unified customer record, device registry link, segmentation, duplicate detection and merge, corporate accounts with multiple contacts and locations |
| ERP BRD BRU-PRT-01, BRU-PRT-03 | A customer sees only their own records; a corporate user sees only their company's |
| ERP BRD BRU-FIN-02 | NID capture required for cash above the statutory threshold |
| Service App SOW §Customer creation and categorisation | "We have different types of customers — end users, dealers, government, corporate… the dealer/government/corporate customer creation process will be started with a user, to be approved by his line manager, later our admin approval. Under a single dealer/government/corporate account, there can be multiple users." |
| Service App SOW §Location registration | "During profile creation, a customer can register his location through GPS. A single customer can save multiple locations with different tags e.g. home, office, factory." |
| Service App SOW §Pricing by customer | "Our admin shall be able to define different pricing models for each customer" — requires a governed customer identity to attach pricing to |
| Service App SOW §Verification | "During profile creation, there will be mobile number and email address verification options" |
| **Personal Data Protection Act 2026 (Law 63 of 2026)** *(verified 2026-08-12)* | Consent standard, transparency notice, data-subject rights, sensitive personal data definition including NID/passport/TIN, cross-border transfer restriction, five-year processing records, Chief Data Officer, National Data Management Authority |
| Company Profile §Customer Portal | Existing account and registration behaviour to be migrated |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The party record — one per legal or natural person the Company deals with |
| 2 | Party roles: a single party may be customer, seller, employee, partner and referrer at once |
| 3 | Party classification: individual, household, dealer, corporate, government, seller, brand partner |
| 4 | Account hierarchy: group → company → division → site → contact |
| 5 | Multiple tagged addresses with saved GPS coordinates |
| 6 | Bangladesh administrative address structure |
| 7 | Identity documents: NID, passport, trade licence, BIN, TIN — captured, validated, residency-controlled |
| 8 | Contact verification by OTP on mobile and email |
| 9 | Multi-tier registration approval for dealer, corporate and government accounts |
| 10 | Duplicate detection, supervised merge and survivorship |
| 11 | Golden-record construction and data quality scoring |
| 12 | **Consent capture, versioning, withdrawal and enforcement source of truth** |
| 13 | **Transparency notice versioning and presentation record** |
| 14 | **Data-subject rights: access, portability, rectification, erasure, withdrawal** |
| 15 | Segment definition (the definitional layer; M35 consumes it) |
| 16 | Credit profile: limit, terms, hold status |
| 17 | Party status lifecycle: active, dormant, blocked, credit hold, blacklisted |
| 18 | Party 360 read model serving every portal and module |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Leads, opportunities, pipeline, account plans | **M07** | Commercial pursuit, not identity |
| Loyalty tier, points balance, wallet | **M10** | Membership state changes constantly; identity does not |
| Conversation history and transcripts | **M27** | Conversations are events, not attributes |
| Satisfaction scores and complaint history | **M34** | Experience measurement is its own domain |
| Campaign membership and journey state | **M35** | Marketing state is transient |
| Devices and assets owned by the party | **M17** | Assets outlive customer relationships |
| Contracts and entitlements | **M08** | Agreements are commercial objects |
| Invoices, payments and balance | **M20** | Financial position is a ledger question |
| Credit limit **enforcement** at order time | **M20** | M33 holds the limit; M20 enforces it |
| Marketplace seller onboarding, KYC verification workflow, seller agreement | **M12** | M12 runs the process; M33 holds the resulting party record |
| Employee master record | **M21** | An employee is a party, but employment is an HR domain |
| Master data governance rules and stewardship workflow engine | **M64** | M64 governs; M33 is governed |
| Breach notification to the regulator | **M60** | M33 detects and reports; GRC notifies |
| Encryption keys and residency enforcement mechanism | **M29** | M33 classifies fields; M29 enforces |

### 3.3 Shared Concepts

| Concept | M33's Role | Owning Module |
|---|---|---|
| Party | **Owns** | M33 |
| Consent | **Owns the record**; M27 and M35 enforce at the point of send | M33 |
| Segment | Owns the definition | M33 (definition) / M35 (campaign use) |
| Credit limit | Owns the value | M33 (value) / M20 (enforcement) |
| Address | Owns | M33 |
| Identity document | Owns; residency-classified | M33 / M29 (enforcement) |
| Corporate approval chain | Owns the chain definition | M33 / M63 (executes the workflow) |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Business Partner** | One party object with multiple roles — customer, vendor, employee — sharing a single identity | **The multi-role party model.** A marketplace seller who is also a customer is one party with two roles, not two records | SAP's BP role configuration depth |
| **Oracle Trading Community Architecture** | Party, party site, relationship, contact point; customer merge with activity transfer | **The party/site/relationship separation**; merge that transfers all prior activity to the surviving record | Full TCA relationship taxonomy |
| **Oracle Customer Hub / Customer Data Management** | Data steward merge with a published survivor and victim record; matching engine; exception routing | **Steward-supervised merge with survivor/victim semantics and downstream merge notification** | Automated unsupervised merge — too risky at 250,000+ customers |
| **Master data management practice** | Golden record built by consolidating and validating across sources; per-attribute survivorship rules with authoritative source, quality threshold and update frequency; workflow routing exceptions to stewards | **Per-attribute survivorship with a named authoritative source and a quality threshold** — this is the core of the M33 design | Full MDM hub product — the ERP is the hub |
| **Microsoft Dataverse Account/Contact** | Account hierarchy, contact roles | Hierarchy model | Platform-specific conventions |
| **Odoo `res.partner`** | Single partner model with company/individual, child contacts, addresses | The L1 substrate — extended, not replaced | Odoo's flat address model, which cannot express Bangladesh administrative structure |

**Design position.** Four deliberate differences from the benchmarks.

First, **consent is a first-class object of the party master, not a marketing attribute**.
Under the PDPA 2026 the lawful basis for processing attaches to the person, is versioned
against a specific transparency notice, and must be withdrawable through a simplified
procedure. Storing it in the marketing platform — the common industry pattern — makes it
unenforceable at the point where processing actually happens.

Second, **residency classification is carried at field level**. NID, passport and TIN are
Sensitive Personally Identifiable Data under the PDPA and are written to a Bangladesh-resident
store; the rest of the party record may be held regionally. No benchmark system does this
because none of them was designed for this jurisdiction.

Third, **merge is always supervised**. Automated merge is standard practice at scale, and it
is how customer databases quietly lose data. At 250,000+ customers a month with phone numbers
shared between family members and shops, automated merge would destroy history.

Fourth, **the multi-tier corporate approval chain is modelled, not assumed**. The Service App
SOW specifies user → client line manager → 1000FiX administrator. Most systems assume one
approval step.

---

## 5. Functional Areas & Features

### 5.1 Party Identity & Classification

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CPM-001 | Unified party record | Maintain exactly one record per legal or natural person, holding identity, contacts, addresses, documents, consent, credit standing and status | **P0** | L1 |
| FR-CPM-002 | Multi-role party | Allow one party to hold several roles simultaneously — customer, marketplace seller, referral partner, employee, vendor, brand partner — without duplicating the identity | **P0** | L5 |
| FR-CPM-003 | Party classification | Classify as Individual · Household · Dealer · Corporate · Government · Marketplace Seller · Brand Partner, each with class-specific mandatory fields and validation | **P0** | L5 |
| FR-CPM-004 | Party numbering | Assign a permanent, non-reusable party identifier independent of any external reference | **P0** | L1 |
| FR-CPM-005 | Party status lifecycle | Manage Active · Dormant · Blocked · Credit Hold · Blacklisted with reasons, effective dates and controlled reactivation | P1 | L5 |
| FR-CPM-006 | Party relationships | Record relationships between parties — employer, guardian, referrer, group member, authorised representative | P2 | L5 |
| FR-CPM-007 | Household grouping | Group individuals at a shared address into a household for RAMC and appliance service, with a nominated primary contact | P2 | L5 |
| FR-CPM-045 | Party search | Search across every identifier — name, phone, email, NID, party number, device serial — with Bengali and English matching, returning in under 400 ms | **P0** | L5 |
| FR-CPM-046 | Party 360 read model | Serve a denormalised party view assembled from every owning module, loading in under 2 seconds | **P0** | L5 |

### 5.2 Account Hierarchy & Corporate Structure

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CPM-008 | Account hierarchy | Model group → company → division → site → contact, with unlimited depth and roll-up reporting at every level | P1 | L5 |
| FR-CPM-009 | Corporate contact roles | Define contact roles within a corporate account — authorised requester, approver, billing contact, technical contact, administrator — each with defined permissions | P1 | L5 |
| FR-CPM-010 | **Multi-tier registration approval** | Route dealer, corporate and government user registration through the client's own line manager and then a 1000FiX administrator, per the Service App SOW | **P1** | L5 |
| FR-CPM-011 | Delegated administration | Allow a corporate administrator to add, suspend and remove their own users within limits set by 1000FiX | P1 | L5 |
| FR-CPM-012 | Hierarchy change control | Require approval for hierarchy changes affecting contracted entities, with effective dating | P2 | L5 |
| FR-CPM-013 | Government entity handling | Apply the specific identification, approval and billing requirements of government customers | P2 | L5 |

### 5.3 Addresses & Geography

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CPM-014 | Multiple tagged addresses | Store unlimited addresses per party with user-defined tags — home, office, factory, branch, site — and a nominated default per purpose | **P0** | L5 |
| FR-CPM-015 | Bangladesh address structure | Enforce Division → District → Upazila/Thana → Union/Ward → postcode with cascading selection and validation | **P0** | L5 |
| FR-CPM-016 | GPS capture | Record and store GPS coordinates against an address, captured from the mobile app or a map picker | P1 | L5 |
| FR-CPM-017 | Address verification | Learn verified coordinates from successful service delivery and prefer them over geocoder output on repeat visits | P2 | L5 |
| FR-CPM-018 | Service zone derivation | Derive the dispatch zone and serving branch automatically from the address | P1 | L5 |
| FR-CPM-019 | International addresses | Support non-Bangladesh addresses for cross-border customers and sellers, with country-appropriate structure | P3 | L5 |

### 5.4 Identity, Verification & Documents

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CPM-020 | Identity document capture | Capture NID (10 and 17 digit), passport, birth registration, trade licence, BIN and TIN as applicable to the party class, with format validation | **P0** | L5 |
| FR-CPM-021 | **Residency-classified storage** | Write NID, passport and TIN to the **Bangladesh-resident store**; never replicate them to a regional store, cache, log or export *(NFR-086, NFR-099)* | **P0** | L5 |
| FR-CPM-022 | Contact verification | Verify mobile number and email by one-time code at registration and on any change, recording the verification event | **P0** | L5 |
| FR-CPM-023 | Document expiry tracking | Track expiry of trade licences and other time-limited documents, alerting before lapse | P2 | L5 |
| FR-CPM-024 | Document storage | Store document images in M24 with residency and access controls; never in the party record itself | P1 | L5 |
| FR-CPM-025 | Sanctions and blocklist screening | Screen parties against internal blocklists and, where applicable, external lists, before activation | P3 | L5 |

### 5.5 Data Quality, Duplicates & Golden Record

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CPM-026 | Duplicate detection at entry | Detect probable duplicates on phone, email, NID, name-plus-address and device serial **before** a record is saved, and present them to the user | **P0** | L5 |
| FR-CPM-027 | Duplicate detection batch | Run scheduled duplicate detection across the whole base with a configurable match threshold, queueing candidates for stewardship | P1 | L5 |
| FR-CPM-028 | **Supervised merge** | Merge duplicates only under data-steward review, nominating a survivor and a victim record, transferring **all** prior activity to the survivor | **P0** | L5 |
| FR-CPM-029 | Merge notification | Publish a merge event carrying survivor and victim identifiers so every downstream module re-points its references | **P0** | L5 |
| FR-CPM-030 | Merge reversal | Reverse a merge within a defined window, restoring both records and their activity | P2 | L5 |
| FR-CPM-031 | **Per-attribute survivorship** | Define, for each attribute, its authoritative source, survivorship rule, quality threshold and update frequency; apply them when constructing the golden record | P1 | L5 |
| FR-CPM-032 | Data quality scoring | Score each party record for completeness, validity and recency, exposing the score to stewards and to reporting | P1 | L5 |
| FR-CPM-033 | Stewardship queue | Route quality exceptions, unresolved duplicates and validation failures to a named data steward with ageing and escalation | P1 | L5 |
| FR-CPM-034 | Enrichment on interaction | Prompt for missing mandatory attributes at natural points of contact rather than in a bulk cleanup exercise | P2 | L5 |

### 5.6 Consent, Privacy & Data-Subject Rights *(PDPA 2026)*

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CPM-035 | **Consent record** | Record consent per processing purpose per channel, capturing the timestamp, the capture channel, the operator, the notice version presented, and the exact wording accepted | **P0** | L5 |
| FR-CPM-036 | **Consent standard** | Enforce that consent is clear, explicit, specific and freely given; apply a heightened *specific consent* standard for sensitive personal data unless a documented legitimate ground applies | **P0** | L5 |
| FR-CPM-037 | **Transparency notice** | Maintain versioned transparency notices in Bengali and English stating data categories, purposes, risks, retention periods, third-party transfers and the withdrawal procedure; record which version was presented at each capture | **P0** | L5 |
| FR-CPM-038 | **Consent withdrawal** | Provide a simplified withdrawal procedure through the portal, the app, the contact centre and the counter, taking effect immediately across all channels | **P0** | L5 |
| FR-CPM-039 | **Consent enforcement source** | Serve consent state to M27 and M35 as the single authority; suppression is evaluated at the point of send, never at the point of campaign design | **P0** | L5 |
| FR-CPM-040 | **Right of access and portability** | Produce a complete, machine-readable extract of a party's personal data on request, within the statutory period | **P0** | L5 |
| FR-CPM-041 | **Right of rectification** | Correct inaccurate data on request and **notify the party of the correction within 30 days** | **P0** | L5 |
| FR-CPM-042 | **Right of erasure** | Erase personal data when the purpose ceases, consent is withdrawn, processing was unlawful or the law requires it — subject to statutory retention overrides, which must be stated to the party | **P0** | L5 |
| FR-CPM-043 | **Rights request workflow** | Manage every data-subject request as a tracked case with identity verification, statutory clock, decision record and evidence of fulfilment | **P0** | L5 |
| FR-CPM-044 | **Processing record** | Maintain the record of processing activities for a minimum of five years, exportable for the National Data Management Authority | **P0** | L5 |
| FR-CPM-052 | **Children and vulnerable parties** | Flag parties recorded as minors or as requiring assisted consent, and apply the heightened handling rules | P2 | L5 |

### 5.7 Commercial Attributes & Segmentation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CPM-047 | Credit profile | Hold credit limit, payment terms and credit-hold status per party, with approval-controlled change and full history | P1 | L5 |
| FR-CPM-048 | Price list assignment | Assign a customer-specific or segment-specific price book, consumed by M11 | P1 | L5 |
| FR-CPM-049 | Segment definition | Define dynamic segments from any combination of party attributes, behaviour and value, evaluated on a schedule and on change | P1 | L5 |
| FR-CPM-050 | Segment membership publication | Publish segment membership as an event so M35, M10 and M25 consume it rather than recomputing it | P1 | L5 |
| FR-CPM-051 | Party audit trail | Record every change to every party attribute with before value, after value, actor, timestamp and reason where required | **P0** | L1 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Split-residency write path** | Residency-classified fields are written through a dedicated adapter to the Bangladesh-resident store; the regional record holds only a reference key. The classification is enforced at write time by the platform, not by developer convention |
| T-02 | **No sensitive data in caches or logs** | NID, passport and TIN are excluded from application logs, error traces, search indexes, analytics extracts and non-production environments by a deny-by-default field policy |
| T-03 | **Deterministic and probabilistic matching** | Duplicate detection combines deterministic keys (NID, verified phone) with probabilistic matching on name, address and device, with a tunable threshold and an explainable score |
| T-04 | **Bengali-aware matching** | Name matching handles Bengali and transliterated Latin script, common spelling variants and honorifics |
| T-05 | **Merge as a first-class transaction** | A merge is atomic: survivor updated, victim tombstoned, all foreign keys re-pointed, merge event published, reversible within the window |
| T-06 | **Tombstone resolution** | Any reference to a merged-away party identifier resolves transparently to the survivor, permanently |
| T-07 | **Party 360 read model** | Assembled asynchronously from owning-module events into a denormalised projection; never assembled by fan-out queries at request time |
| T-08 | **Consent evaluation API** | A single synchronous endpoint answers "may I contact this party on this channel for this purpose right now", in under 100 ms, and fails **closed** |
| T-09 | **Immutable consent history** | Consent records are append-only; a withdrawal is a new record, never an update or delete |
| T-10 | **Field-level audit** | Every attribute change is audited with before and after values, retained five years to satisfy the PDPA processing-record obligation |
| T-11 | **Idempotent party creation** | Concurrent registration from two channels for the same person produces one party, resolved by verified phone as the natural key |
| T-12 | **Segment evaluation at scale** | Segment membership is computed incrementally on change, not by full-base recomputation, at 250,000+ parties |
| T-13 | **Performance envelope** | Party search ≤ 400 ms p95 · Party 360 load ≤ 2 s · consent evaluation ≤ 100 ms · duplicate check at entry ≤ 600 ms |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M33 |
|---|---|---|
| **Service centre agent** | Types the customer afresh, or finds three versions of them | Finds the customer in one search; sees everything; duplicates are blocked at entry |
| **Contact centre agent** | Asks the customer to explain who they are and what has happened | Screen shows the verified party with full context before the call is answered |
| **Corporate client administrator** | Registers users by email, waits for someone to act | Self-registers users through the approval chain; sees status |
| **Account manager** | Cannot see the whole group's relationship — each site looks like a separate customer | Sees the group, its companies, sites and contacts, with roll-up spend and service history |
| **Marketing** | Sends to a list assembled from an export, with no reliable consent state | Sends to a governed segment, with suppression enforced at delivery |
| **Data steward** *(new role)* | Does not exist | Owns a stewardship queue of duplicates and quality exceptions with measurable outcomes |
| **Compliance officer** | Cannot evidence lawful basis for any processing | Can produce, for any customer, what was consented to, when, on what notice version, and through which channel |
| **Finance** | Cannot reliably identify one customer's total exposure across sites | Credit standing held once, at the right level of the hierarchy |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Duplicate elimination** | Entry-time blocking plus supervised merge | Duplicate rate to **< 1%**. Every duplicate today is a fragmented service history, a mis-sent notification and a missed upsell |
| **Enables customer-specific pricing** | The SOW's per-customer pricing model requires a governed identity to attach a price book to | Precondition for **M11 dynamic pricing margin uplift of 3–6%** |
| **Enables loyalty and retention** | A loyalty programme on a fragmented customer base rewards the wrong people and misses the right ones | Precondition for **BDT 78 lac/year** retention benefit |
| **Corporate account growth** | Group hierarchy makes the true size of a corporate relationship visible for the first time | Supports the **2.5× contract base growth** target |
| **Faster corporate onboarding** | Structured multi-tier approval replaces email chains | Registration cycle from days to **< 24 hours** |
| **PDPA penalty avoidance** | Consent, notices, rights and processing records built in rather than retrofitted | Avoids exposure of up to **BDT 25 lakh** per rights violation and **BDT 50 lakh** as a significant data fiduciary |
| **Marketing efficiency** | Governed segments replace exported lists | Direct contribution to the **> 4:1 campaign ROI** target |
| **Reduced service time** | Search-first intake depends entirely on the party record being findable | Enables the **< 3 minute** counter intake constraint |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **One version of the customer** | This is the single most-cited failure of the current estate. Every module downstream inherits M33's quality — or its absence |
| **Lawful basis becomes demonstrable** | Under the PDPA the burden is on the controller to show consent was validly obtained. Only a versioned consent record against a versioned notice discharges it |
| **Data stewardship becomes a role** | Creating a named owner for customer data quality is an organisational change as much as a system one, and it is what makes quality durable |
| **Foundation for expansion** | A second country entity needs a party model that already carries jurisdiction, locale and residency dimensions |
| **Trust with corporate clients** | Enterprise buyers ask how customer data is governed. This is a tender question, and today there is no answer |
| **Protection for staff** | Field-level audit protects staff from unfounded allegations of data misuse as much as it deters actual misuse |

---

## 8. Lifecycle & State Models

### 8.1 Party Lifecycle

```
   +-----------+
   |   DRAFT   |  created, not yet verified
   +-----+-----+
         | contact verification (OTP)
   +-----v-----------+
   | PENDING         |  dealer / corporate / government only:
   | APPROVAL        |  client line manager -> 1000FiX administrator
   +-----+-----------+
         | approved
   +-----v-----+
   |  ACTIVE   |<-------------------------+
   +--+--+--+--+                          |
      |  |  |                             |
      |  |  +--> CREDIT HOLD -------------+  (cleared by Finance)
      |  |
      |  +-----> DORMANT ----------------+   (re-engagement)
      |          no activity > threshold  |
      |                                   |
      +--------> BLOCKED -----------------+   (cleared by CCO)
                 conduct / fraud / dispute
                        |
                        v
                   BLACKLISTED  (terminal; reinstatement requires CEO)

   MERGED  -- terminal for the victim record; all references resolve to the survivor
   ERASED  -- personal data removed under PDPA right of erasure; a tombstone and the
              statutory processing record remain
```

### 8.2 Consent Lifecycle

```
   NOTICE VERSION PUBLISHED (v.n, Bengali + English)
              |
              v
   PRESENTED ---> ACCEPTED ------> ACTIVE ------> WITHDRAWN
       |              |               |               |
       |              |               |               +--> suppression effective
       |              |               |                    immediately, all channels
       |              |               +--> SUPERSEDED (new notice version presented
       |              |                    and re-accepted)
       |              +--> DECLINED --> no lawful basis for that purpose
       |
       +--> ABANDONED (presented, not acted on)

   RULE: consent records are append-only. A withdrawal never edits the original.
```

### 8.3 Duplicate Resolution

```
   DETECTED (entry-time or batch)
        |
   +----v---------+   below threshold
   |   SCORED     |--------------------> DISMISSED (recorded, not re-raised)
   +----+---------+
        | above threshold
   +----v---------+
   | STEWARD      |
   | QUEUE        |
   +----+---------+
        |
   +----v---------+       +-------------+
   |  REVIEWED    |------>| NOT A DUP   |  linked as "known similar"
   +----+---------+       +-------------+
        | confirmed
   +----v---------+
   | SURVIVOR     |  per-attribute survivorship applied
   | SELECTED     |
   +----+---------+
        |
   +----v---------+
   |   MERGED     |  activity transferred, event published, reversible for N days
   +--------------+
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-CPM-01 | A party record cannot be activated without at least one verified contact point | **H** | CCO |
| BRU-CPM-02 | Dealer, corporate and government parties cannot transact until both the client line manager and a 1000FiX administrator have approved | **H** | CCO |
| BRU-CPM-03 | A party record cannot be saved where a duplicate above the match threshold exists and has not been dismissed with a reason | **H** | Data Steward |
| BRU-CPM-04 | A merge may only be executed by a data steward; automated merge is prohibited | **H** | CCO |
| BRU-CPM-05 | All activity of a merged party transfers to the survivor; nothing is deleted | **H** | CTO |
| BRU-CPM-06 | **NID, passport and TIN are written only to the Bangladesh-resident store and never replicated regionally** | **H** | CTO |
| BRU-CPM-07 | **Personal data may not be processed for a purpose without a recorded, current consent or a documented legitimate ground** | **H** | CDO |
| BRU-CPM-08 | **Consent is invalid unless the transparency notice version presented is recorded with it** | **H** | CDO |
| BRU-CPM-09 | **Consent withdrawal takes effect immediately across every channel and every module** | **H** | CDO |
| BRU-CPM-10 | **A rectification must be notified to the data subject within 30 days** | **H** | CDO |
| BRU-CPM-11 | **Erasure is honoured except where a statutory retention obligation overrides it; the override and its basis must be stated to the data subject** | **H** | CDO / Legal |
| BRU-CPM-12 | Credit limit changes require Finance Manager approval and are fully audited | **H** | CFO |
| BRU-CPM-13 | A blacklisted party cannot be reactivated below CEO authority | **H** | CEO |
| BRU-CPM-14 | Only M33 may create or amend party identity attributes; other modules raise a change request | **H** | CTO |
| BRU-CPM-15 | Processing records are retained a minimum of five years, independently of party erasure | **H** | CDO |
| BRU-CPM-16 | A party marked as a minor requires assisted consent and heightened handling | **H** | CDO / Legal |

*Classification: **H** hard block · **A** approved override · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.party` | `fix_party` | The master record | party_number, party_class, legal_name, display_name, name_bn, status, primary_contact_id, entity_id, created_at |
| `fix.party.role` | `fix_party_role` | Roles a party holds | party_id, role_type, active_from, active_to, reference_id |
| `fix.party.hierarchy` | `fix_party_hierarchy` | Group structure | parent_party_id, child_party_id, relation_type, effective_from, effective_to |
| `fix.party.relationship` | `fix_party_relationship` | Party-to-party links | party_a, party_b, relation_type, verified |
| `fix.address` | `fix_address` | Tagged addresses | party_id, tag, division_id, district_id, upazila_id, union_ward, postcode, line1, line2, latitude, longitude, verified, is_default_for |
| `fix.bd.geography` | `fix_bd_geography` | Administrative reference | level, code, name_en, name_bn, parent_code |
| `fix.contact.point` | `fix_contact_point` | Phone, email, messaging handles | party_id, type, value, verified_at, verification_method, is_primary |
| `fix.identity.document` | `fix_identity_document` **(resident store)** | NID, passport, TIN, licence | party_id, doc_type, doc_number, issued_date, expiry_date, verified_by, verified_at |
| `fix.consent.record` | `fix_consent_record` | Append-only consent | party_id, purpose, channel, state, notice_version_id, captured_at, captured_via, captured_by, wording_hash |
| `fix.transparency.notice` | `fix_transparency_notice` | Versioned notice text | version, purpose_set, text_en, text_bn, published_at, retired_at |
| `fix.rights.request` | `fix_rights_request` | Data-subject request case | party_id, request_type, received_at, identity_verified, statutory_due, decision, fulfilled_at, evidence_ref |
| `fix.processing.record` | `fix_processing_record` | PDPA record of processing | party_id, purpose, lawful_basis, categories, recipients, retention, occurred_at |
| `fix.party.duplicate` | `fix_party_duplicate` | Detection candidate | party_a, party_b, score, factors_json, state, reviewed_by, decision |
| `fix.party.merge` | `fix_party_merge` | Merge audit | survivor_id, victim_id, executed_by, executed_at, attribute_decisions_json, reversible_until |
| `fix.survivorship.rule` | `fix_survivorship_rule` | Per-attribute rule | attribute, authoritative_source, rule, quality_threshold, update_frequency |
| `fix.party.quality` | `fix_party_quality` | Quality score | party_id, completeness, validity, recency, composite, evaluated_at |
| `fix.credit.profile` | `fix_credit_profile` | Commercial standing | party_id, credit_limit, currency, payment_terms, hold_status, approved_by, effective_from |
| `fix.segment` | `fix_segment` | Segment definition | code, name, criteria_json, evaluation_mode, owner_id, active |
| `fix.segment.membership` | `fix_segment_membership` | Current membership | segment_id, party_id, entered_at, exited_at |
| `fix.party.audit` | `fix_party_audit` | Field-level change log | party_id, attribute, old_value, new_value, actor_id, occurred_at, reason |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.document` | M24 | Identity document images stored under residency control |
| `fix.membership` | M10 | Read for tier display in Party 360 |
| `fix.contract` | M08 | Read for entitlement display |
| `fix.asset` | M17 / M49 | Read for device list |
| `fix.conversation` | M27 | Read for interaction history |
| `fix.survey.response` | M34 | Read for satisfaction display |
| `account.move` | M20 | Read for balance display |
| `fix.seller` | M12 | Seller role detail |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-CPM-01 | Party created from any channel | Run duplicate detection, request contact verification, present the current transparency notice, record consent | Block activation; route to steward queue |
| AUT-CPM-02 | Contact verification code requested | Issue a time-limited single-use code through M27; record the attempt | Retry with rate limiting; alert on abuse pattern |
| AUT-CPM-03 | Corporate registration submitted | Route to the client line manager, then to a 1000FiX administrator, with reminders and escalation at 24 and 48 hours | Escalate to CCO |
| AUT-CPM-04 | Duplicate score above threshold | Queue for stewardship with ageing; block the save at entry | — |
| AUT-CPM-05 | Merge executed | Re-point all references, publish the merge event, notify affected modules, set the reversal window | Roll back the transaction entirely |
| AUT-CPM-06 | **Consent withdrawn** | Propagate immediately to M27 and M35 suppression; confirm to the party; record in the processing record | **Escalate immediately — a failed suppression is a regulatory incident** |
| AUT-CPM-07 | **New transparency notice published** | Mark existing consents as superseded for the affected purposes; prompt re-acceptance at next interaction | Alert CDO |
| AUT-CPM-08 | **Rights request received** | Verify identity, start the statutory clock, assemble the response, route for decision | Escalate on clock risk at 50% and 75% |
| AUT-CPM-09 | Party inactive beyond threshold | Set Dormant; notify the account owner; trigger re-engagement in M35 subject to consent | — |
| AUT-CPM-10 | Data quality score below threshold | Queue for enrichment; prompt at the next customer interaction | — |
| AUT-CPM-11 | Document expiring within 30 days | Notify the party and the account owner | — |
| AUT-CPM-12 | Segment criteria met or lost | Publish membership change event | Retry; alert on repeated failure |
| AUT-CPM-13 | Credit limit exceeded on an order | Notify Finance; place the order on credit hold in M20 | — |

---

## 12. Interfaces

### 12.1 Upstream — M33 Consumes

| Source | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, field-level residency enforcement, encryption, audit substrate | Service |
| M64 Master Data Management | Stewardship workflow, data quality rules, reference data governance | Service |
| M28 Integration | Event publication, API gateway, external verification connectors | Service |
| M30 Platform Admin | Entity, branch, zone and locale configuration | Master data |
| M24 Documents | Identity document storage under residency control | Service |
| M12 Marketplace | Seller KYC verification outcome | Event |
| M21 Core HR | Employee-party linkage | Event |
| M63 Process Automation | Approval chain execution | Service |

### 12.2 Downstream — M33 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **Every module** | Party identity, addresses, classification, status | REST + event projection |
| M01, M04 | Customer lookup and inline creation at intake | REST |
| M07 | Party context for leads, opportunities and account plans | REST + event |
| M08, M20 | Party for contracts, invoicing and credit | REST |
| M10 | Party for membership and points | REST |
| **M27, M35** | **Consent state — the authority for suppression** | **REST, fails closed** |
| M11 | Customer-specific price book assignment | REST |
| M34 | Party for satisfaction and complaint attribution | REST |
| M53 | Party for settlement and payout | REST |
| M60 | Processing records, rights requests, consent evidence | REST |
| M25 | Party dimension for the warehouse | Warehouse extract |
| P01, P04, P07, P12 | Party self-service profile management | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `party.created` | party id, class, entity, source channel | All |
| `party.activated` | party id, approval chain evidence | M07, M10, M20 |
| `party.updated` | party id, changed attributes | All subscribers |
| `party.status_changed` | party id, old status, new status, reason | M20, M07, M12 |
| `party.merged` | survivor id, victim id, attribute decisions | **All — mandatory re-point** |
| `party.merge_reversed` | survivor id, restored id | All |
| `address.added` / `address.verified` | party id, address, coordinates, zone | M01, M02, M03 |
| `contact_point.verified` | party id, type, value | M27, M35 |
| **`consent.captured`** | party, purpose, channel, notice version | M27, M35, M60 |
| **`consent.withdrawn`** | party, purpose, channel, effective immediately | **M27, M35 — mandatory suppression** |
| `notice.published` | version, purposes affected | M27, M35, all capture points |
| `rights_request.received` | party, request type, statutory due date | M60, M24 |
| `rights_request.fulfilled` | party, request type, evidence | M60 |
| `segment.membership_changed` | segment, party, entered or exited | M35, M10, M25 |
| `credit_profile.changed` | party, limit, terms, hold status | M20, M07 |
| `party.quality_flagged` | party, score, deficiencies | M64 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/parties` | POST | Create a party with duplicate check | P01, P03, P04, M01, M04 |
| `/api/v1/parties/{id}` | GET / PATCH | Read and amend the party record | All |
| `/api/v1/parties/search` | GET | Multi-identifier search, Bengali-aware | P03, P10, M01, M04 |
| `/api/v1/parties/{id}/360` | GET | Assembled party view | P03, P10, P04 |
| `/api/v1/parties/{id}/addresses` | GET / POST | Address management | P01, P03, M02 |
| `/api/v1/parties/{id}/verify` | POST | Contact verification | P01, P03 |
| `/api/v1/parties/duplicates` | GET | Stewardship queue | P03 |
| `/api/v1/parties/merge` | POST | Execute a supervised merge | P03, steward only |
| **`/api/v1/consent/evaluate`** | **GET** | **May we contact this party, on this channel, for this purpose, now — fails closed** | **M27, M35** |
| `/api/v1/consent` | POST | Record consent with notice version | P01, P03, P10, M04 |
| `/api/v1/consent/withdraw` | POST | Withdraw consent | P01, P03, P10 |
| `/api/v1/rights-requests` | POST / GET | Raise and track a data-subject request | P01, P03, M60 |
| `/api/v1/parties/{id}/export` | POST | Right of access and portability extract | P01, M60 |
| `/api/v1/segments/{id}/members` | GET | Segment membership | M35, M25 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R04 Chief Commercial Officer | R U A | All parties |
| **R39 Data Steward** *(new role)* | C R U D A | All parties — merge, quality, stewardship queue |
| R08 Service Centre Agent | C R U | Create and amend at intake; no merge; no credit change |
| R34 Contact Centre Agent | C R U | Create and amend during a conversation; no merge |
| R22 Account Manager (Corporate) | R U | Own accounts — commercial attributes only |
| R26 Finance Manager | R U A | Credit profile — approval authority |
| R06 Branch Manager | R U | Own branch's parties |
| **R40 Chief Data Officer** *(new role, PDPA)* | R U A | Consent, notices, rights requests, processing records |
| R32 Quality Manager / ISO Coordinator | R | Quality scores and stewardship outcomes |
| R33 IT / System Administrator | — | **No access to identity documents**; platform administration only |
| R36 Customer | R U | Own record only — self-service profile, consent, rights requests |
| R37 Corporate Portal User | R U | Own company's parties within delegated authority |

**Field-level restrictions.** NID, passport and TIN are **write-then-restricted**: capturable
by R08, R34 and R29, readable only by R26, R27, R06 and R40, with every read logged. Credit
limit is visible to R21, R22, R26, R27 and R06 only.

**Segregation of duties.** The steward who executes a merge cannot be the person who created
either record within the preceding 24 hours (SOD-15). Credit limit approval cannot be
performed by the person who requested it (SOD-04).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Data quality dashboard | Data Steward, CCO | Daily | Completeness, validity, recency by party class; trend; worst-scoring segments |
| Stewardship queue | Data Steward | Real time | Open duplicates, quality exceptions, ageing, throughput per steward |
| Duplicate rate | CCO, CTO | Weekly | Detected, merged, dismissed; duplicate rate against the < 1% target |
| Merge audit | CTO, GRC | Monthly | Every merge with survivor, victim, executor and attribute decisions |
| **Consent coverage** | **CDO, CCO** | **Weekly** | Parties with valid current consent by purpose and channel; gaps by capture point |
| **Rights request register** | **CDO, GRC** | **Monthly** | Requests by type, statutory clock performance, decisions, overdue |
| **Notice version adoption** | **CDO** | **On publication** | Parties still on a superseded notice version |
| Corporate hierarchy report | CCO, Account Managers | Monthly | Group structures, roll-up spend, unmapped sites |
| Registration funnel | CCO | Weekly | Registrations by class and channel; approval cycle time; abandonment |
| Party growth and status | CCO, CEO | Monthly | New, active, dormant, blocked by class and geography |
| Segment population | CCO, Marketing | Weekly | Segment sizes and movement |
| Address quality | Ops Director | Monthly | Addresses with verified coordinates; failed geocodes by area |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| KPI-120 | Customer record completeness | unmeasured | 85% | **> 92%** |
| KPI-121 | Duplicate customer rate | unmeasured | < 3% | **< 1%** |
| KPI-122 | Party 360 load time | — | < 3 s | **< 2 s** |
| KPI-123 | Corporate registration approval cycle | manual, days | < 48 h | **< 24 h** |
| KPI-124 | Party search response time (p95) | — | < 600 ms | **< 400 ms** |
| KPI-125 | Contact points verified | unmeasured | 88% | **> 95%** |
| KPI-126 | **Parties with valid current consent** | n/a | 90% | **> 98%** |
| KPI-127 | **Consent evaluation availability** | n/a | **100%** | **100%** |
| KPI-128 | **Rights requests fulfilled within the statutory period** | n/a | **100%** | **100%** |
| KPI-129 | **Rectifications notified within 30 days** | n/a | **100%** | **100%** |
| KPI-130 | Stewardship queue ageing beyond 5 days | n/a | < 10% | **< 3%** |
| KPI-131 | Addresses with verified GPS coordinates | 0% | 55% | **> 80%** |
| KPI-132 | **NID or TIN found outside the resident store** | n/a | **0** | **0** |
| KPI-133 | Merges reversed (indicator of merge quality) | n/a | < 3% | **< 1%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `contacts`, `res.partner`, `base` | 22% |
| L2 | OCA `partner_*` extensions (firstname, contact type, address hierarchy) | 8% |
| L5 | `cd_party_master`, `cd_party_hierarchy`, `cd_consent`, `cd_bd_address`, `cd_identity_doc` | 70% |

### 16.2 Custom Development

> CD identifiers are **provisional** pending the unified register in `02-05` (audit H-03).

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-035 | `cd_party_master` — party, roles, status, search, 360 read model | Odoo module + service | 8 PW |
| CD-036 | `cd_party_hierarchy` — group structure, corporate contacts, approval chain | Odoo module | 4 PW |
| CD-037 | **`cd_consent`** — consent record, notice versioning, evaluation API, rights requests, processing record | Odoo module + service | **7 PW** |
| CD-038 | `cd_bd_address` — administrative hierarchy, GPS, zone derivation | Odoo module | 3 PW |
| CD-039 | `cd_identity_doc` — residency-controlled document capture and access | Odoo module + resident adapter | 2 PW |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M33 is scheduled in **W1** (P0) but declares a dependency on 1 module(s) that land later: **M64** (W2). One of three things must be true before the W1 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W1 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M33 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W1 plan for M33 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M29 Identity & Security | Field-level residency enforcement and audit are the substrate |
| **Bangladesh-resident store operational** | **Blocking** — NID cannot be captured without it *(DEP-31, decision D-13)* |
| **Transparency notice text approved in Bengali and English** | **Blocking** — consent captured without a valid notice is not valid consent *(DEP-34)* |
| M28 Integration | The consent evaluation API is consumed synchronously by other modules |
| M64 Master Data Management | Stewardship workflow — may be stubbed in W1, completed in W2 |
| M30 Platform Admin | Entity and geography configuration |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing customer records (spreadsheets) | 100,000+ | `fix.party` | W1 |
| Existing customer portal accounts | Unknown, to be profiled | `fix.party`, `fix.contact.point` | W1 |
| Corporate account lists held by account managers | ~2,000 | `fix.party`, `fix.party.hierarchy` | W1 |
| Address data | 100,000+ | `fix.address` | W1 |

**Migration is the largest risk in this module.** Three rules apply.

1. **Profile before load.** Duplicate rate, completeness and validity are measured on the
   source data before any load, and the results reported to the CCO.
2. **No consent is inferred.** Historical customers are migrated **without** consent records.
   Consent is captured at their next interaction against the current notice. Assuming
   consent from prior dealings is not a lawful basis under the PDPA.
3. **Sensitive fields last.** NID and TIN are migrated only after the resident store is live
   and verified.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A duplicate above threshold cannot be saved from any channel, including the API | Negative test across all creation paths |
| AC-02 | A supervised merge transfers all activity and every downstream reference resolves to the survivor | Trace test on 20 merges across 10 modules |
| AC-03 | A merge is reversible within the window with full restoration | Scripted reversal test |
| AC-04 | Corporate registration completes the two-tier approval chain and blocks transaction until approved | Negative and positive test |
| AC-05 | **NID, passport and TIN are absent from every regional store, cache, log, search index and analytics extract** | **Data-flow audit and log review** |
| AC-06 | **Consent cannot be recorded without a notice version reference** | **Negative test** |
| AC-07 | **Consent withdrawal suppresses all channels within 60 seconds, verified end to end** | **Timed test through M27 and M35** |
| AC-08 | **The consent evaluation API fails closed when unavailable — the caller blocks rather than sends** | **Fault-injection test** |
| AC-09 | **A rights request produces a complete, machine-readable export within the statutory period** | **Scripted request, output review** |
| AC-10 | **A rectification generates a notification to the data subject within 30 days** | **Scripted test** |
| AC-11 | Party search returns in ≤ 400 ms p95 across 250,000 parties, including Bengali names | Load test |
| AC-12 | Party 360 loads in ≤ 2 s with full context | Load test |
| AC-13 | Migration reconciles: source count, loaded count, rejected count and duplicate count all accounted for | Migration reconciliation report signed by CCO |
| AC-14 | No migrated party carries an inferred consent record | Data audit |
| AC-15 | Every party attribute change is audited with before and after values | Audit log review |
| AC-16 | CCO, Data Steward and Chief Data Officer sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Who is appointed Data Steward, and does the role sit in Commercial, Operations or IT?** This role does not exist today. | CCO | **W1 minus 2 months** |
| Q-02 | **Has the significant data fiduciary assessment been done, and is a Chief Data Officer being appointed?** *(D-15)* | CEO / Legal | W1 minus 2 months |
| Q-03 | What is the duplicate match threshold, and who may change it? | CCO / Data Steward | W1 build |
| Q-04 | Is the merge reversal window 7, 14 or 30 days? | CTO | W1 build |
| Q-05 | For historical customers, at what interaction is consent captured — first contact, first transaction, or a proactive campaign? | CDO / CCO | **W1 build** |
| Q-06 | Does the Company hold any customer personal data today for which no lawful basis can be established? | CDO / Legal | **Immediately** |
| Q-07 | What is the dormancy threshold — 12, 18 or 24 months without activity? | CCO | W1 build |
| Q-08 | Are household groupings needed at launch, or deferred with RAMC? | CCO | W1 design |

**Q-06 is not a design question.** It is a live exposure that should be assessed independently
of this programme.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3 (M33/M07 boundary), §6 (customer data ownership rule) ·
`M07_CRM_Sales_Pipeline_and_Account_Management.md` ·
`M27_Omnichannel_Contact_Centre_and_Communications.md` ·
`M35_Marketing_Campaigns_and_Demand_Generation.md` ·
`00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` (findings C-04, C-05) ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3–6.4 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §6

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.4, BRU-PRT-01/03,
BRU-FIN-02 · `1000fix_business/SOW for 1000FiX Service App Development.docx` §Customer
creation and categorisation, §Location registration, §Pricing by customer, §Verification ·
`1000FiX_Services_Company_Profile.md` §Customer Portal

**External benchmark and regulation** *(verified 2026-08-12)*
SAP Business Partner — single party with multiple roles · Oracle Trading Community
Architecture — party, site, relationship, customer merge with activity transfer ·
Oracle Customer Hub — data-steward merge publishing survivor and victim records ·
Master data management practice — golden record construction, per-attribute survivorship with
authoritative source and quality threshold, steward exception routing ·
**Bangladesh Personal Data Protection Act 2026 (Law 63 of 2026)** — consent standard,
transparency notice, access, portability, rectification within 30 days, erasure, withdrawal,
sensitive personal data including NID, passport and TIN, cross-border transfer restriction,
five-year processing records, Chief Data Officer, National Data Management Authority,
penalties to BDT 25 lakh and BDT 50 lakh

---

*Module M33 · Category B · 1000FiX ERP System v2.0 · CONFIDENTIAL*
