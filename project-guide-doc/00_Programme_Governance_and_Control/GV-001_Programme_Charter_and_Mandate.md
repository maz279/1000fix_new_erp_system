---
id: GV-001
title: Programme Charter & Mandate
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Director
approver: Board of Directors, 1000FiX Services Limited
standards_basis: ISO 21500:2021 · ISO 21502:2020 · ISO 21503:2022 · PMBOK Guide 7th Edition · PRINCE2 7th Edition (2023)
traces_to: PGD-000 GV-001 · audit finding PGD-A1-09 · 00-04 §6 decisions D-01, D-14 · 00-02 §1
depends_on: none — this is the root authority document
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-001 — Programme Charter & Mandate
# 1000FiX ERP System & Portal Suite v2.0

### Category 00 · Code `GV` · ISO 21503:2022 · PRINCE2 7 · PMBOK 7

---

> **This is the root document of the programme.** Nothing else in the 610-file estate is binding
> until this charter is approved. Every one of those files is currently marked
> `DRAFT FOR APPROVAL`, and audit finding **`PGD-A1-09`** records that *no constituted body exists
> that can approve any of them*. This charter and `GV-002` are the only two documents in the
> register that can be approved without a prior approval. They must be first.

---

## 1. Purpose

This charter authorises the 1000FiX ERP System & Portal Suite v2.0 programme. It names the body
that owns it, the executive accountable for it, the objectives it must achieve, the boundary of
what it will and will not do, the money and time it may consume, and the conditions under which
the Board's authorisation lapses.

It exists because the programme currently has none of those things in writing. Work has been
under way since March 2026; 610 documentation files exist; three effort figures, four requirement
counts and two cost baselines are in simultaneous circulation; and no meeting of any authorising
body has been minuted. **A programme without a charter is not a programme — it is a body of work
that people are performing on the assumption that it was approved.**

### 1.1 Scope of this document

**In scope:**

| # | Covered |
|---|---|
| 1 | The mandate: what the Board authorises, and to whom |
| 2 | Programme objectives and the measures that determine success |
| 3 | The scope boundary at charter level — capability in, capability out |
| 4 | The delivery shape: nine waves, thirty-six months, and what each wave is for |
| 5 | The financial envelope, stated as a **range that is currently contested**, and the conditions on it |
| 6 | Authority, tolerance and escalation thresholds |
| 7 | Constraints and assumptions on which the authorisation rests |
| 8 | The conditions of approval — what must be true for this charter to remain valid |
| 9 | Charter closure and the circumstances that reopen it |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Terms of reference, quorum and RACI for each governance body | `GV-002` | A charter names *that* a body exists and what it may decide; the constitution of the body is a separate, longer instrument |
| The decision log and the change-control procedure | `GV-003` | A charter is a decision; the register of decisions is a live instrument with its own lifecycle |
| Work breakdown, critical path and resource-loaded schedule | `GV-004` | A charter fixes the horizon and the wave shape, not the plan |
| The risk register | `GV-005` | Charter-level risks are named here; the live instrument is `GV-005` |
| Estimation method and the resource plan | `GV-007` | The charter records the *envelope*; `GV-007` derives what the work actually costs |
| The cost baseline and drawdown schedule | `GV-008` | The charter authorises an envelope; `GV-008` baselines it to a cost breakdown structure |
| Functional and non-functional requirements | `RQ-001`, `RQ-006` | A charter states objectives, never requirements |
| Architecture and technology selection | `AR-001`, `AR-004` | Charter-level constraints only (e.g. "the portal platform cannot be replaced") |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Board of Directors** | The instrument they sign. It is the basis on which programme spend is authorised and on which the executive is held to account |
| **Chief Executive Officer** | The mandate under which they chair the ERP Steering Committee |
| **Chief Financial Officer** | The financial envelope, its contested status, and the conditions attaching to drawdown |
| **Chief Technology Officer** | The technical constraints the Board has accepted, and the tolerance within which the CTO may act without returning to the Board |
| **Programme Director** | The document they deliver against, and the authority they hold |
| **Implementation vendor** | Evidence that the buyer has an authorised programme, an approver, and a budget — the three things whose absence makes a fixed-price bid unpriceable |
| **Internal and external audit** | The top of the traceability chain: objective → requirement → design → build → test → benefit |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / concept | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 21503:2022** *Guidance on programme management* | Programme mandate, programme brief, benefits and stakeholder alignment | The mandate (§3), objectives and benefit ownership (§4), and the wave structure (§6) follow the standard's programme-level constructs rather than project-level ones | None. The 1000FiX work is a **programme** — nine waves, multiple interdependent projects, benefit realisation beyond delivery — and is chartered as one |
| **ISO 21502:2020** *Guidance on project management* | Pre-project activities; project governance; controls | Wave-level governance inherits from this standard through `GV-009` gates | Each wave is treated as a project inside the programme, not as a phase |
| **ISO 21500:2021** *Context and concepts* | Organisational context; portfolio/programme/project relationships | §5 positions the ERP within the 1000FiX digital estate | None |
| **PRINCE2 7th Edition (2023)** | Project Brief / Project Initiation Documentation; the seven principles; **tolerance** | §8 adopts PRINCE2 *management by exception*: tolerances are stated numerically per dimension, and breach forces escalation rather than judgement | PRINCE2's sustainability performance target (new in 7th edition) is adopted and mapped to `BO-14`/`M18` |
| **PMBOK Guide 7th Edition** | Project charter contents; principles; **value delivery** over output delivery | §4 states objectives as outcomes with measures and owners, not as deliverable lists | None |
| **ISO/IEC 38500:2024** *Governance of IT for the organization* | Engage stakeholders → Evaluate → Direct → Monitor | The Board's role in §8 is expressed in EDM terms; the detailed governance model is in `GV-002` | Cited here; realised in `GV-002` |

> **Citation currency.** ISO/IEC 38500 was verified at **edition 3, published February 2024** — the
> category overview and `PGD-000` cite it without an edition. That is corrected here and raised as
> finding `PGD-A2-07`. This matters because three of the estate's critical findings (`C-04`,
> `H-01`, `M-01`) were stale citations, and rule `PG-M4` exists to stop a fourth.

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Executive Summary & Expanded Scope Charter | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-02` | The decision to expand from 11 modules to 67; the fourteen revenue streams; the guiding principles; the out-of-scope list |
| Scope Expansion Delta v1→v2 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-03` | The evidence trail for every module added, and what was considered and rejected |
| Risks, Assumptions, Dependencies & Governance | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` | 36 risks, 22 assumptions, 35 dependencies, 12 constraints, the governance structure and the 15 open decisions |
| Implementation Roadmap & Phasing | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` | The nine-wave shape, the team model, the rollout approach |
| KPI, Benefits & Acceptance Criteria | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` | 18 business objectives, 95 registered KPIs, the benefit model, 70 wave-gate criteria |
| Comprehensive BRD, RFP, URD | `../../primary-doc/` | The business need, the procurement instrument, 255 user stories, the v1.0 cost-benefit analysis |
| Documentation Audit Report | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-06` | Findings `C-01`…`C-05`, `H-01`…`H-06`, `M-01`…`M-09` |
| Category H & Repository Integrity Audit | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-07` | Findings `H2-01`…`H2-14`; the 1,513 PW measurement; decision `D-14` |
| Content & Repository Integrity Audit | `../../project_content/_AUDIT/AUDIT-001` | Findings `AF-01`…`AF-18`; the 520–775 PW content variance |
| Register Integrity Audit | `../_AUDIT/PGD-AUDIT-001` | Findings `PGD-A1-01`…`PGD-A1-13`; the governance circularity `PGD-A1-09` |
| **Direct filesystem enumeration** | Whole workspace | Every count in §6.4 and §7, enumerated **2026-08-18 02:06 (+06)** — rule `PG-03` |

### 2.3 Audit findings this document closes

| Finding | Source audit | How this document closes it |
|---|---|---|
| `PGD-A1-09` | `PGD-AUDIT-001` | **Partially.** This charter, once signed, constitutes the Board's authorisation and empowers the CEO to constitute the Steering Committee under `GV-002`. It closes the *upper* half of the circularity; `GV-002` closes the lower half. Neither closes alone |
| `D-01` (open decision) | `00-04` §6 | §11 puts the scope, budget and horizon to the Board as an explicit decision with three named options |
| `D-14` (escalated) | `00-07` H2-08 | §7 presents the counted effort figure to the Board rather than absorbing it. **`GV-003` records the decision; this charter forces it to be taken** |
| `AF-09` (escalated) | `AUDIT-001` | §6.3 names content production as a chartered workstream, closing recommendation `R-07`. It was previously accountable to nobody |
| `PGD-A1-05` | `PGD-AUDIT-001` | **Partially.** §7.3 names the two unbudgeted work streams inside the envelope discussion. `GV-007` sizes them; `GV-008` absorbs them |

---

## 3. The Mandate

### 3.1 What the Board is asked to authorise

The Board of 1000FiX Services Limited is asked to authorise a programme to design, build,
implement and operate a single enterprise system of record for every revenue stream the Company
operates or has committed to operate, together with the portal and application suite through
which customers, technicians, sellers, partners and staff transact with it.

| Attribute | Value |
|---|---|
| **Programme name** | 1000FiX ERP System & Portal Suite v2.0 |
| **Programme identifier** | `FIX-ERP2` |
| **Sponsoring body** | Board of Directors, 1000FiX Services Limited |
| **Executive Sponsor** | Chief Executive Officer |
| **Senior Responsible Owner** | Chief Technology Officer |
| **Programme Director** | Appointed by the CEO on charter approval — **currently vacant** (see §11 condition `CC-02`) |
| **Delivery horizon** | 36 months from kickoff, in nine waves |
| **Benefit horizon** | 60 months; independent benefits audit at Month 42 |
| **Scope at charter** | 67 ERP modules · 12 portals and applications · 5 technology stacks |
| **Financial envelope** | **Contested — see §7.** No single figure may be quoted until `GV-008` is baselined |
| **Charter status** | `DRAFT FOR APPROVAL` |

### 3.2 What authority the charter confers

| Authority | Held by | Limit |
|---|---|---|
| To commit the Company to the programme | Board | This charter |
| To spend within the authorised envelope | CEO, on Steering Committee recommendation | Wave-gated; see §8 tolerance |
| To constitute the ERP Steering Committee and the subordinate bodies | CEO | `GV-002` |
| To appoint the Programme Director and delivery leadership | CEO | Within the approved resource plan (`GV-007`) |
| To let and administer the implementation contract | CTO with CFO countersignature | `CO-003` Statement of Work |
| To make technical decisions inside the architecture standards | CTO / Architecture Review Board | `GV-002` §decision rights |
| To stop a wave at its gate | Steering Committee | `GV-009` |
| To stop the programme | Board | §12 |

### 3.3 What authority the charter does **not** confer

Stated explicitly, because the estate's most persistent defect is work proceeding on assumed
authority:

1. **No authority to build against an unapproved requirement baseline.** The programme has 2,930+
   requirements and **zero** approved specifications. `RQ-001` must exist and be baselined before
   any build contract is let.
2. **No authority to process personal data outside a lawful basis.** The Personal Data Protection
   Act 2026 governs almost everything this system does. `SC-003` (DPIA) is a precondition of
   Wave 2, not a Wave 4 deliverable.
3. **No authority to fix the data architecture** until the legal opinion at `DEP-31` is received
   and decision `D-13` is taken. This is the most urgent open decision in the programme.
4. **No authority to create a build backlog** from the current custom-development identifiers.
   48 of them collide (`H-03`, `H2-05`); `BE-005` must exist first.
5. **No authority to quote a completion percentage, requirement count or effort figure** that has
   not been enumerated at the time of quoting, with the enumeration timestamp recorded
   (`RG-06`, `RG-07`, `PG-M11`).

---

## 4. Objectives and Success

### 4.1 Programme objectives

The programme inherits the eighteen business objectives registered in `06-02` §1. They are not
restated here — that would create a second copy that drifts, which is the defect class
`AF-02`/`AF-03` describe. The charter fixes **which of them the Board is holding the executive to**
and at what level.

| Tier | Objectives | Charter treatment |
|---|---|---|
| **Chartered — the programme fails without these** | `BO-01` service lifecycle automation · `BO-04` warranty revenue recovery · `BO-06` financial close compression · `BO-10` Bangladesh regulatory compliance · `BO-02` technician productivity | Board-level. Reported quarterly. A miss is a Board matter |
| **Committed — the business case rests on these** | `BO-03`, `BO-05`, `BO-07`, `BO-08`, `BO-11`, `BO-12`, `BO-13`, `BO-14` | Steering Committee level. A miss is a Steering Committee matter with a Board notification |
| **Directional — value expected, not underwritten** | `BO-09`, `BO-15`, `BO-16`, `BO-17`, `BO-18` | Programme level. Tracked; not a gate condition |

> **Why the tiering matters.** All eighteen objectives are currently equal, and eighteen equal
> objectives are eighteen ways to declare partial success. The five chartered objectives are the
> ones for which the Company would not have started the programme.

### 4.2 Programme success criteria

The programme is successful if, at Month 36, all ten criteria in `06-02` §5 are met. The charter
adds three conditions that `06-02` does not carry:

| # | Additional charter criterion | Measure | Why it is here |
|---|---|---|---|
| `CS-11` | **Every claimed benefit has a measured pre-implementation baseline** | `BM-002` complete before the wave that changes the measured process | Audit `RP-02`: **44 of 95 KPI baselines are absent**, which places approximately **BDT 396 lac** of the BDT 876 lac case outside what may be claimed under the programme's own rule (`06-02` §6). A benefit with no baseline is not a benefit; it is an assertion |
| `CS-12` | **No statutory obligation is discovered after go-live** | Zero regulatory findings traced to an obligation absent from `SC-008` at the relevant wave gate | The PDPA 2026 was absent from the entire specification set until August 2026 (`C-04b`). The control is a register with verification dates, not diligence |
| `CS-13` | **The system is upgradable** | An Odoo minor-version upgrade completes in a non-production environment at every wave gate, with no core modification required | `AR-007`: one `_inherit` done wrong converts the next Odoo upgrade into a rewrite. A three-year programme that cannot take an upgrade has bought a legacy system |

### 4.3 Benefit ownership

Benefit owners are named in `06-02` §3.5 and are **not** restated here. The charter adds one rule:

> **Rule `GV-001-R1` — a benefit without a named owner is not in the business case.** A benefit
> line whose owner is vacant at a wave gate is removed from the claimed case at that gate and
> reported as removed. It may be reinstated when an owner is named. This prevents the case
> degrading silently, which is how the BDT 396 lac exposure at `CS-11` arose.

---

## 5. Programme Context

### 5.1 Position in the 1000FiX digital estate

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        1000FiX DIGITAL ESTATE                                │
│                                                                              │
│  ┌────────────────────────┐          ┌──────────────────────────────┐        │
│  │  CORPORATE WEBSITE     │          │  INTEGRATED SMART PORTAL     │        │
│  │  Next.js 15 + Payload  │◄────────►│  PLATFORM  (12 portals)      │        │
│  │  Separate programme    │          │  CON-03: CANNOT BE REPLACED  │        │
│  │  ERP integrates only   │          │  ERP integrates; owns no UI  │        │
│  └───────────┬────────────┘          └───────────────┬──────────────┘        │
│              │                                       │                       │
│              │      REST · GraphQL · Webhooks · Domain events                │
│              └───────────────────┬───────────────────┘                       │
│                                  ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │        1000FiX ERP v2.0  —  SYSTEM OF RECORD                           │  │
│  │        67 modules · Odoo 19 CE + OCA + open source + custom            │  │
│  │        ◄── THIS CHARTER AUTHORISES THIS LAYER AND ITS 12 PORTALS       │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                  │                                           │
│  ┌───────────────────────────────▼────────────────────────────────────────┐  │
│  │  DATA & INTELLIGENCE PLATFORM                                          │  │
│  │  PostgreSQL 16 · TimescaleDB · ClickHouse · Metabase · MLflow          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Boundary rule, chartered.** *The ERP owns state and truth. The portals own experience and reach.*
Any business object with a lifecycle, a financial consequence or an audit obligation is mastered
in the ERP. No portal holds an authoritative copy of anything.

> This rule is stated in one sentence in `00-01` §5 and is enforced nowhere. `AR-002` must make it
> an architectural control with a compliance test (`AR-012`), because a boundary that is only a
> sentence is a boundary that will be crossed in Wave 3 by a developer meeting a deadline.

### 5.2 What the programme is replacing

48 legacy systems and manual processes are inventoried in `DM-002`. **All 48 are unprofiled**
(`AUDIT-011`). Legacy decommissioning is a chartered obligation (`RL-006`), not an aspiration: a
system that is never formally switched off keeps costing money and keeps holding personal data
that the PDPA 2026 requires to be erasable.

---

## 6. Scope

### 6.1 Capability in scope

| # | Capability | Realised by |
|---|---|---|
| 1 | Service and repair operations, field dispatch, logistics, branch front desk, workshop and depot repair | Category A — 7 modules |
| 2 | Customer engagement: CRM, loyalty, contact centre, conversational AI, party master, feedback, marketing | Category B — 7 modules |
| 3 | Commercial: contracts, warranty and claims, pricing, marketplace, quotation, catalogue, e-commerce, subscriptions, partner channel | Category C — 9 modules |
| 4 | Circular business: rental, trade-in and refurbishment, e-waste and recycling | Category D — 3 modules |
| 5 | Supply chain: inventory, procurement, warehouse, supplier performance, demand planning, import and landed cost | Category E — 6 modules |
| 6 | Assets and facilities: device registry, enterprise assets, fleet, facilities, IoT and predictive maintenance | Category F — 5 modules |
| 7 | Finance and treasury: GL, AR, AP, fixed assets, treasury, Bangladesh tax, revenue recognition, cost accounting | Category G — 8 modules |
| 8 | People: core HR, learning and certification, time and attendance, payroll, performance, talent, health and safety | Category H — 7 modules |
| 9 | Governance: quality management, documents and e-signature, GRC, knowledge management | Category I — 4 modules |
| 10 | Data and intelligence: BI, AI/ML operations, data platform, process automation | Category J — 4 modules |
| 11 | Platform: integration, identity, administration, master data, multi-entity, internal ITSM, PPM | Category K — 7 modules |
| 12 | Twelve portals and applications: customer, technician, admin, B2B, vendor, analytics, marketplace, brand partner, rider, contact centre, field auditor, referral | 12 `P*` specifications |
| 13 | Migration of the operating history from 48 legacy sources | Category `MG` |
| 14 | The content estate that makes the system operable — master data, UI copy, SOPs, legal, training, statutory templates | `project_content` — 477 files |

### 6.2 Capability out of scope

Carried from `00-02` §8 and chartered unchanged. **These ten exclusions are the Board's, and only
the Board may vary them.**

| # | Excluded | Rationale |
|---|---|---|
| `OOS-01` | Development of the corporate website and the Next.js portal *platform* | Separate programme. The ERP integrates; it does not replace (`CON-03`) |
| `OOS-02` | Manufacturing or assembly of devices | Not a 1000FiX business |
| `OOS-03` | Consumer lending / instalment underwriting | Regulated activity. Partner-provided; the ERP records the receivable only |
| `OOS-04` | Full-scope Enterprise Asset Management for client-owned plant machinery | `M17`/`M45` cover IT, mobile, appliance and rental assets only |
| `OOS-05` | A proprietary payment switch | bKash / Nagad / SSLCOMMERZ |
| `OOS-06` | Replacement of brand partners' internal warranty systems | Integration and portal only |
| `OOS-07` | Manufacture of fleet telematics hardware | Commercial GPS units + Traccar |
| `OOS-08` | Custom hardware — kiosks, scanners, RMM appliances | Standard commercial hardware |
| `OOS-09` | Recruitment marketing / applicant-tracking beyond Odoo standard | `M58` uses standard Odoo recruitment |
| `OOS-10` | Country-specific tax engines beyond Bangladesh in Waves 1–8 | `M65` provides the framework; country packs are separate projects |

### 6.3 Chartered workstreams

The programme has **five** workstreams. The fifth is new at this charter and closes recommendation
`R-07` of `AUDIT-001`.

| # | Workstream | Accountable | Why it is chartered separately |
|---|---|---|---|
| 1 | **Build** — 67 modules, 12 portals, 5 stacks | CTO | The substance of the programme |
| 2 | **Data** — migration from 48 legacy sources, master data, data governance | CFO (finance data) / CTO (platform) | 48 unprofiled sources make this the least-understood work in the programme |
| 3 | **Change and adoption** — training, communication, champion network, rollout to 51+ branches | HR Director | `RSK-008` (technician app rejection) is a Critical risk that build quality alone cannot mitigate |
| 4 | **Assurance** — audit, independent review, regulatory currency | Chair of the Audit Committee, **not** the CTO | Four audits have now been produced by the function that authored the material (`R-07`) |
| 5 | **Content** — 477 content files: master data, UI copy, SOPs, legal, training, statutory templates | Programme Content Lead | **520–775 PW of work that appears in no plan and no budget** (`AF-09`). It was accountable to nobody until this charter |

> **Workstream 5 is the largest single omission the audits found.** `06-01` does not contain the
> word "content" as a workstream and `00-04` §5 has no content seat. Chartering it does not fund
> it — that is `GV-007` and `GV-008` — but it makes the gap owned rather than invisible.

### 6.4 Scope, counted

Enumerated from the filesystem at **2026-08-18 02:06 (+06)**. Rule `PG-03`: counted, not consulted.

| Item | Counted | Source of the count |
|---|---:|---|
| Module specifications | **67** | `find 03_Modules -name 'M*.md'` |
| Portal / application specifications | **12** | `find -name 'P[0-9][0-9]_*.md'` |
| Cross-cutting specifications | 6 | `05_Cross_Cutting_Specifications/` |
| Content files | **477** | `find project_content -type f` |
| Primary documents | 4 | `primary-doc/` |
| Guiding documents registered | 140 | `PGD-000` |
| Guiding documents written | **11** *(this category)* | `find project-guide-doc -name 'GV-*.md'` |
| **Total estate, excluding this repository** | **610** | Direct enumeration |
| Distinct `FR-` identifiers in the 67 module files | **2,996** | `grep -ohE 'FR-[A-Z0-9]{3,4}-[0-9]{3}' \| sort -u \| wc -l` |
| Module build effort — sum of the `Effort estimate` row, 67 files | **1,544 PW** | Direct sum |
| Portal build effort — sum of the `Effort estimate` row, 12 files | **298 PW** | Direct sum |
| **Total specified build effort** | **1,842 PW** | 1,544 + 298 |

> **⚠ Baseline movement — third independent occurrence.** `project_content` held **468** files at
> the `PGD-000` enumeration of 01:39 and **477** at 02:06; nine files were written between 01:53
> and 02:06 while this charter was being drafted. The estate total moved 601 → 610.
>
> This is `AUDIT-016` finding `AP-17` and `PGD-AUDIT-001` finding `PGD-A1-03` occurring for a
> **third time**. Proposed rule `RG-08` — enumeration carries a timestamp, not a date — has been
> pending ratification since August 2026. **§11 condition `CC-06` ratifies it as a charter
> condition**, because the alternative is a fourth occurrence.

---

## 7. The Financial Envelope

### 7.1 Why this section does not state a number

The Board is currently holding **$455K–$780K** as the three-year total cost of ownership.

Audit `H-02` states that the implementation cost line underpinning that figure is **understated by
70–80%**. Audit `H2-08` measured the build effort at 1,513 PW against the 834 PW the figure was
modelled on. Audit `AF-08` found **three** effort figures in simultaneous circulation. Audit
`AF-09` found a further **520–775 PW** of content work in no budget at all. Audit `PGD-A1-05`
found **two more** work streams — producing 127 unwritten guiding documents, and designing
roughly 660–1,500 screens — that are not estimated and appear in no plan.

**A charter that restated $455K–$780K would be asking the Board to authorise a number its own
auditors have disowned.** A charter that invented a replacement would create a *fifth*
uncontrolled estimate, which is precisely what `PGD-A1-05` warns against.

This section therefore does two things and no more: it states the position honestly, and it makes
the resolution a condition of approval.

### 7.2 The position, stated honestly

| Basis | Effort | 3-year TCO | Status |
|---|---:|---|---|
| **Approved business case** (30 modules, March 2026) | 834 PW | **$455K – $780K** | **Disowned** by audit `H-02` |
| `02-05` revision note | ~1,302 PW | — | Superseded; retire under `AF-08` |
| `00-02` provisional restatement | ~1,302 PW | $620K – $1,050K | Marked provisional; predates the counted figure |
| `00-07` H2-08 measured (65 module files) | 1,513 PW | ~$690K – $1,150K | Escalated as `D-14`; **decision never recorded** (`AF-04`) |
| **Counted at 2026-08-18 02:06** — 67 module files | **1,544 PW** | *see `GV-008`* | This charter |
| **Counted at 2026-08-18 02:06** — 12 portal files | **+298 PW** | *see `GV-008`* | **Has never appeared in any effort figure** |
| Content estate (`AF-09`) | 520 – 775 PW | *not costed anywhere* | Escalated; not absorbed |
| 127 unwritten guiding documents (`PGD-A1-05`) | **not estimated** | — | `GV-007` |
| ~660–1,500 screens of UX design (`PGD-A1-05`) | **not estimated** | — | `GV-007` |

> **The portal finding is new at this charter.** Every effort figure the programme has ever
> published — 834, 1,302, 1,513 — was derived from **module** identity tables. The twelve portal
> specifications carry their own `Effort estimate` rows summing to **298 person-weeks** of Flutter
> and Next.js build, and no programme total has ever included them. The counted build position is
> therefore **1,842 PW**, not 1,513 — **2.2× the approved plan** before content, guiding documents
> or screen design are added at all.

### 7.3 What the Board is authorising instead of a number

| # | The Board authorises | Limit |
|---|---|---|
| 1 | **Tranche 0 — Authority and Truth.** Spend to constitute governance and produce `GV-002`, `GV-003`, `GV-007`, `GV-008`, `RR-002`, `RR-005`, `RQ-001`, `RQ-003`, `RQ-004`, `BE-005`, `BM-002` | Capped at the Tranche 0 allocation in `GV-008` §drawdown, set at **10% of the mid-point of the last approved envelope** pending re-baselining |
| 2 | **Continuation authority** for Waves 1–4 (the v1.0 committed scope) | Released wave by wave at each `GV-009` gate, against the re-baselined figure in `GV-008` |
| 3 | **No authority** for Waves 5–9 at this charter | Waves 5–9 are re-authorised at the Wave 4 gate on the evidence of Waves 1–4, per `CON-01` |

**This is a deliberate structure, not a hedge.** Waves 1–4 deliver everything the v1.0 plan
promised, on the original dates (`06-01` §1). They are independently valuable. Waves 5–9 are the
new business lines, and `RSK-005` records that they have no delivery precedent. Authorising them
now would authorise the least-understood half of the programme against the least reliable estimate.

### 7.4 Benefit position

| Item | Value | Qualification |
|---|---|---|
| Claimed annual benefit at steady state, base case | **BDT 876 lac** (~$797K) | `06-02` §3.1 |
| Benefit currently **claimable** under the programme's own baseline rule | **~BDT 480 lac** | 44 of 95 KPI baselines absent (`RP-02`); roughly BDT 396 lac has no measurable "before" |
| Cumulative benefit, Years 1–3, base case | BDT 1,000 lac (~$909K) | `06-02` §3.2 — deliberately lagged; new lines contribute nothing until they go live |

> **The benefit case is not disputed by any audit. The cost case is disputed by three.** That
> asymmetry is what makes the programme still worth doing and the charter still worth signing —
> but it also means the Board is being asked to approve a *ratio* it cannot currently compute.
> `CC-04` fixes that before the first build contract is let.

---

## 8. Authority, Tolerance and Escalation

The charter adopts PRINCE2 **management by exception**: the Board delegates authority within
stated numeric tolerances, and a forecast breach escalates automatically rather than being judged.

### 8.1 Tolerances

| Dimension | Programme tolerance (Board) | Wave tolerance (Steering Committee) | Escalates to |
|---|---|---|---|
| **Time** | +3 months on the 36-month horizon | +4 weeks per wave | > 4 weeks → Steering Committee decides descope / extend / reallocate (`06-01` §9). > 3 months cumulative → Board |
| **Cost** | +10% on the baselined envelope once `GV-008` exists | +15% per wave | Breach → Board, with the option set from §7.3 |
| **Scope** | No reduction in any **chartered** objective (§4.1 tier 1) | P2/P3 descope inside a wave at PMO + business owner | Any P0/P1 change → Steering Committee. Any chartered-objective change → Board |
| **Quality** | Zero critical or high security findings at any gate; zero ISO 9001 major non-conformances traced to systems | Per `GV-009` gate evidence standard | A failed gate is a Steering Committee decision, never a Programme Director one |
| **Risk** | No Critical risk may be accepted without Board minute | High risk acceptance at Steering Committee; Medium and below at PMO | Per `GV-005` |
| **Benefit** | A forecast shortfall > 20% against the chartered benefit case | Per-benefit variance reported monthly | Board, with the `BM-004` decision rule |

### 8.2 The five decisions the Board must take at this charter

| # | Decision | Options | Consequence of not deciding |
|---|---|---|---|
| `D-01` | Approve the expanded scope, the 36-month horizon and the tranche structure in §7.3 | Approve · Approve with conditions · Reject · Defer Waves 5–9 | The programme has no mandate; 632 files remain non-binding |
| `D-14` | Accept the counted effort position (1,842 PW build, before content and documents) or direct a descope | Fund · Phase over more waves · Descope Categories D, F, I or J · Defer Waves 8–9 | Escalated in August 2026 and **still unrecorded** (`AF-04`). Every week it stays open, work proceeds against a plan the Board has not seen |
| `D-02` | Confirm and protect business super-user availability across all waves | Confirm and instruct department heads · Fund backfill · Accept the slip | `RSK-001` is the highest-rated risk in the register. UAT capacity, not developer capacity, paces this programme (`CON-12`) |
| `D-13` | Approve the split-residency data architecture, subject to the legal opinion at `DEP-31` | Approve subject to opinion · Commission opinion first · Accept regional hosting and the regulatory exposure | **The most urgent open decision in the programme.** The entire data architecture is blocked, and retrofitting residency into a live system is the most expensive class of rework |
| `CC-02` | Appoint a Programme Director | Appoint internally · Recruit · Assign to the CTO as an additional duty | The role is vacant. `06-01` §4 loads it at 0.5 FTE in Waves 1–2, which is below the level a nine-wave programme with four open critical findings requires |

---

## 9. Constraints and Assumptions

### 9.1 Constraints the Board is accepting

Carried from `00-04` §4 and chartered. A constraint is a limit the programme may not design around.

| ID | Constraint | Consequence the Board is accepting |
|---|---|---|
| `CON-01` | Three-year budget envelope | Waves 8 and 9 are the first deferral candidates. **Note: the envelope itself is contested — §7** |
| `CON-02` | v1.0 committed scope must be delivered by Month 18 | Waves 1–4 cannot be reordered |
| `CON-03` | The Next.js 15 + Payload CMS portal platform cannot be replaced | API contract discipline is mandatory, not preferred. `AR-002` must treat this as an architectural given |
| `CON-04` | All financial transactions must comply with NBR requirements | Compliance is a P0 gate, not a feature |
| `CON-05` | Bengali is the primary language for field and customer surfaces | Translation is a definition-of-done item, not a follow-up |
| `CON-06` | bKash and Nagad must be primary payment methods | Bangladesh-specific gateway integration is mandatory |
| `CON-07` | Field applications must operate offline for 24 hours | Offline-first architecture is non-negotiable (`AR-010`) |
| `CON-08` | No go-live during Ramadan or the Eid periods | Wave dates account for the Islamic calendar |
| `CON-09` | Data must be hosted in an approved region | **Now qualified by the PDPA 2026** — see `CON-13` |
| `CON-10` | Automation must augment roles, not displace staff without approval | Change messaging and redeployment planning required |
| `CON-11` | ISO 9001:2015 certification must be maintained throughout | Process changes require QMS documentation updates in step |
| `CON-12` | Business super-user time is finite | **UAT capacity, not developer capacity, paces the programme** |
| **`CON-13`** *(new at this charter)* | **Sensitive personal data — NID, passport, TIN, biometric templates, KYC documents — must be Bangladesh-resident** under the PDPA 2026 | A split-residency architecture, not a hosting-region preference. Audit `C-05`; risk `RSK-033`; decision `D-13` |
| **`CON-14`** *(new at this charter)* | **No production personal data may be used in a non-production environment without a documented lawful basis and masking** | `QA-004`. Using real customer data in a test environment is a processing act under the PDPA 2026 |

### 9.2 Assumptions on which the authorisation rests

The 22 assumptions in `00-04` §2 are chartered by reference. The charter promotes four to
**charter-critical**, meaning the authorisation itself is invalid if they prove false:

| ID | Charter-critical assumption | If false |
|---|---|---|
| `ASM-06` | Business stakeholders commit the stated time (Executive Sponsor 4 h/month; module owners 20%; super-users 30% during UAT) | Waves slip regardless of development capacity. This is `RSK-001` and `CON-12` — the binding constraint |
| `ASM-21` | A Bangladesh-resident data store of adequate reliability and performance is procurable | The data architecture must be re-planned before Wave 1, not adjusted during it |
| `ASM-22` | PDPA enforcement timing holds at approximately **13 May 2027** | Enforcement lands inside Wave 4. Earlier activation compresses the compliance window to nothing |
| `ASM-11` | Odoo 19 remains supported through the programme | An in-programme major upgrade is a separate project and a separate authorisation |

> **`ASM-22` verification.** The Personal Data Protection Act 2026 was enacted by Parliament in
> April 2026; enforcement, complaint and penalty mechanisms are delayed approximately 18 months
> and activate around **13 May 2027**. The National Data Management Authority reports to the Prime
> Minister's Office and may issue warnings, impose administrative fines, and order suspension or
> cessation of cross-border data transfers. The Amendment Ordinance No. 23 of 2026 (5 February
> 2026) replaced criminal penalties for managing directors with monetary fines. Verified
> **2026-08-18**. Re-verification is due at every wave gate under `PG-M4` and `RR-005`.

---

## 10. Charter-Level Risks

The live instrument is `GV-005`. The charter names only the risks the **Board** carries, because
they cannot be mitigated at programme level.

| ID | Risk | Rating | Why it is a Board risk |
|---|---|:--:|---|
| `RSK-001` | Business super-user availability falls short, stalling UAT | **Critical** | Only the CEO can protect people's time against their line objectives |
| `RSK-002` | Scope creep across a 36-month horizon | **Critical** | Scope has already moved 11 → 30 → 67 with no change-control artefact. A fourth expansion cannot be distinguished from creep until `GV-006` exists |
| `RSK-008` | Technician rejection of the mobile application | **Critical** | 200–400 people in the field decide whether this programme works. No amount of build quality substitutes for their acceptance |
| `RSK-022` | Marketplace VAT and liability model incorrect | **Critical** | A principal-versus-agent error is a restatement risk, not a delivery risk |
| `RSK-023` | Marketplace quality failure damages the brand | **Critical** | The brand is the asset the marketplace monetises |
| `RSK-032` | **Non-compliance with the PDPA 2026** | **Critical** | Penalties reach BDT 25 lakh, or BDT 50 lakh for a significant data fiduciary. Enforcement lands inside Wave 4 |
| `RSK-033` | **Data residency architecture unlawful** | **Critical** | Blocks `D-13`, which blocks the data architecture, which blocks Wave 1 |
| `RSK-036` | **Cost estimate materially understated** | **Critical** | §7. The Board is holding a number three audits have qualified |

> **Eight Critical risks, not five.** `00-04` §1.5 records *"Critical 5, High 16, Medium 10"*.
> Counting the rating column across all five risk tables returns **8 Critical, 22 High, 6 Medium
> — 36 risks**. The summary predates the `1.4a` additions and was wrong on the High/Medium split
> even before them. Recorded as finding `PGD-A2-01` and corrected in `GV-005`.

---

## 11. Conditions of Approval

The Board is asked to approve this charter **subject to the following conditions**. Each has an
owner and a date. A condition not met by its date suspends the authority it qualifies — it does
not lapse quietly.

| # | Condition | Owner | By | Suspends if unmet |
|---|---|---|---|---|
| `CC-01` | The ERP Steering Committee is constituted with written terms of reference (`GV-002`) and holds its first minuted meeting | CEO | Week 2 | All approval authority. **Closes `PGD-A1-09`** |
| `CC-02` | A Programme Director is appointed | CEO | Week 2 | Tranche 0 spend |
| `CC-03` | The decision log exists and `D-01`…`D-15` are recorded, with any unreconstructable decision marked `UNRECOVERABLE` (`GV-003`) | Programme Office | Week 2 | Nothing may be cited as decided. **Closes `AF-04`** |
| `CC-04` | `GV-007` (estimation) and `GV-008` (budget baseline) are issued, absorbing build, content, guiding documents and screen design | Programme Director / CFO | Week 6 | **The implementation contract may not be let.** Closes `PGD-A1-05`, `AF-08`, `AF-09` |
| `CC-05` | The legal opinion at `DEP-31` is received and `D-13` is taken | CTO + Legal | Before Wave 1 architecture is fixed | All architecture work on the data layer |
| `CC-06` | Rule `RG-08` is ratified — every completeness figure carries an enumeration **timestamp** | PMO | Week 2 | Nothing. But a fourth occurrence of baseline movement is then a governance failure, not an accident |
| `CC-07` | `RR-002` (Identifier Convention Standard) is issued | Enterprise Architecture | Week 2 | Build backlog creation. Eight audit findings across four audits are identifier collisions |
| `CC-08` | Independent assurance is commissioned (`GV-010`), reporting to the Audit Committee and not to the CTO | CTO / Audit Committee | Week 6 | Nothing at Wave 1; **the Wave 4 gate may not be signed without it** |
| `CC-09` | `BM-002` KPI baseline measurement begins | Programme Director | Week 4 | Benefit claims for any KPI whose process changes before its baseline is taken |
| `CC-10` | `RQ-001` (SRS) exists and is baselined | Enterprise Architecture | Before the build contract | **No build contract may be let against prose.** The vendor cannot price it and QA cannot test it |

---

## 12. Charter Closure and Reopening

### 12.1 The programme closes when

| Criterion | Evidence |
|---|---|
| All nine wave gates passed | Signed gate reports (`GV-009`) |
| All P0 and P1 requirements delivered or formally superseded | `RQ-004` traceability matrix at 100% |
| All 48 legacy systems decommissioned | `RL-006` decommission register complete, with proof each is switched off |
| Documentation handed over and accepted | Document register; acceptance signature |
| Support model transitioned to steady state | `SV-005` hypercare exit; support agreement in force |
| Knowledge transferred; two-person coverage verified | Handover records |
| Benefits tracking live with named owners | `BM-004` |
| Final financial reconciliation | CFO sign-off |
| Lessons learned recorded | `BM-005`; retrospective to the Board |

**Post-implementation review at Month 42** — an independent benefits audit against this charter,
reported to the Board. Independence is defined in `GV-010` and is not satisfied by the programme
auditing itself.

### 12.2 The charter reopens when

| Trigger | Consequence |
|---|---|
| A chartered objective (§4.1 tier 1) becomes unachievable | Board reviews the mandate |
| A programme tolerance in §8.1 is forecast to breach | Board decision required before the breach, not after |
| A charter-critical assumption in §9.2 proves false | Authorisation is invalid until re-approved |
| A scope change adds or removes a module category | `GV-006` change request escalates to Board |
| The Wave 4 gate is reached | Waves 5–9 are authorised, deferred or descoped — they are **not** authorised by this charter |
| A statutory obligation is discovered that changes the compliance posture materially | `SC-008` triggers a Board notification |

---

## 13. Decisions Recorded

Local decisions of this document. Programme decisions are `D-nnn` and are allocated only by
`GV-003`; document-local decisions are prefixed with the document ID to prevent the collision the
house template invites.

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-001-D-01` | Whether to state a single financial envelope | State the approved figure · State a new figure · State the contested position and condition approval | **State the contested position** | Restating a disowned figure misleads the Board; inventing one creates a fifth uncontrolled estimate (`PGD-A1-05`) | The Board approves a *structure* and a set of conditions, not a number. `GV-008` supplies the number |
| `GV-001-D-02` | Whether to charter Waves 5–9 | Charter all nine · Charter 1–4 only · Charter 1–2 only | **Charter Waves 1–4; re-authorise 5–9 at the Wave 4 gate** | Waves 1–4 are the v1.0 committed scope, are independently valuable, and have delivery precedent. Waves 5–9 have none (`RSK-005`) | Waves 5–9 planning continues; Waves 5–9 spend does not |
| `GV-001-D-03` | Whether to tier the eighteen business objectives | Charter all 18 equally · Tier them | **Tier: 5 chartered, 8 committed, 5 directional** | Eighteen equal objectives are eighteen ways to declare partial success | The Board holds the executive to five outcomes, and knows which five |
| `GV-001-D-04` | Whether to charter content as a workstream | Leave inside build · Charter separately | **Charter separately (workstream 5)** | 520–775 PW accountable to nobody (`AF-09`, `R-07`) | Chartering does not fund it. `CC-04` funds it |
| `GV-001-D-05` | Whether to include portal effort in the stated build position | Follow precedent (module-only) · Include portals | **Include: 1,544 + 298 = 1,842 PW** | Every prior figure excluded 298 PW of specified, estimated, contracted-for work. Precedent is not a reason to repeat an omission | The counted build position rises 22% and the variance against the approved plan becomes 2.2× |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Does 1000FiX qualify as a *significant data fiduciary* under the PDPA 2026? At 250,000+ customers per month, qualification is likely | CEO + Legal | W4 − 3 months | `D-15`; Chief Data Officer appointment; the BDT 50 lakh penalty tier |
| `Q-02` | Is the Board's authority to approve this charter itself constituted, given that no ERP-specific Board sub-committee exists? | Company Secretary | Week 1 | The signature block in §15 |
| `Q-03` | Which legal entity holds the rental and refurbished-resale business? | CFO + Legal | W6 − 3 months | `D-04`; the finance design; `M13`/`M14` |
| `Q-04` | Is the "17+ brand partners" figure current? It underpins `M22`'s certification control and `KPI-264`, and audit `H2-12` records it as unverified | Service Head | W5 | The warranty benefit line — the largest single benefit at BDT 100 lac |
| `Q-05` | Who owns the 127 unwritten guiding documents as a delivery workstream? They are chartered nowhere, in no wave, with no owner | Programme Director | Week 4 | `GV-007`; `PGD-A1-05` |

> An open question with no owner and no needed-by date is not an open question — it is an
> unrecorded risk. All five are escalated to `GV-005` on issue of this charter.

---

## 15. Approval

| Role | Name | Decision | Date | Conditions attached |
|---|---|---|---|---|
| **Chair, Board of Directors** | | Approve / Approve with conditions / Reject | | |
| Chief Executive Officer *(Executive Sponsor)* | | | | |
| Chief Financial Officer | | | | |
| Chief Technology Officer *(Senior Responsible Owner)* | | | | |
| Chief Commercial Officer | | | | |
| Service Operations Director | | | | |
| HR Director | | | | |
| Quality Manager | | | | |
| Company Secretary *(attestation of authority)* | | | | |

**Conditions of approval recorded here:**

---

**Approval note.** Signature of this charter constitutes the Board's authorisation for Tranche 0
and Waves 1–4 only, subject to conditions `CC-01`…`CC-10`. It does not authorise Waves 5–9, does
not baseline a cost figure, and does not permit a build contract to be let before `CC-04` and
`CC-10` are met.

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every objective referenced traces to a registered `BO-nn` in `06-02` §1 | Cross-reference check: 18 of 18 resolve |
| `AC-02` | Every risk referenced traces to a registered `RSK-nnn` in `00-04` §1 | 8 of 8 resolve |
| `AC-03` | Every constraint referenced traces to `00-04` §4, or is declared new and numbered in sequence | `CON-01`…`CON-12` carried; `CON-13`, `CON-14` declared new |
| `AC-04` | Every count in §6.4 carries an enumeration timestamp | `2026-08-18 02:06 (+06)` recorded per row group |
| `AC-05` | Every statutory or standards citation carries `verified_on` | Front matter: `2026-08-18`; PDPA verification recorded at §9.2 |
| `AC-06` | No figure is quoted from another register without being recounted | §6.4 and §7.2 recount build effort; the 2,930 figure is reported as *disputed*, not adopted |
| `AC-07` | Every relative link resolves | `PG-M9` link check at issue |
| `AC-08` | The document states what it does **not** authorise | §3.3, five items |
| `AC-09` | Approval is conditional and every condition has an owner and a date | §11, ten conditions |

**Definition of done.** This document is complete when every acceptance criterion above is met,
its `PGD-000` status is updated with a fresh enumeration timestamp, and the Board has signed §15.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | *(none)* | This is the root authority document |
| Downstream | `GV-002` | Constitutes the bodies this charter names |
| Downstream | `GV-003` | Records `D-01`, `D-13`, `D-14` and every subsequent decision |
| Downstream | `GV-004` | Decomposes the wave shape in §7.3 into a resource-loaded schedule |
| Downstream | `GV-005` | Holds the live register of the risks named in §10 |
| Downstream | `GV-006` | Controls the scope baseline fixed in §6 |
| Downstream | `GV-007` | Sizes the effort the envelope in §7 must cover |
| Downstream | `GV-008` | Baselines the envelope §7 declines to fix |
| Downstream | `GV-009` | Realises the wave gates that release §7.3 tranches |
| Downstream | `GV-010` | Realises condition `CC-08` independent assurance |
| Downstream | `CO-003` | The Statement of Work must not exceed this charter's scope |
| Downstream | `BM-003` | The business case restates §7 in NPV/IRR terms |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-02` | Scope charter — the business decision this document authorises |
| Lateral | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01`, `06-02` | Wave shape and objectives referenced, not restated |
| Lateral | `../../project_content/00_Content_Governance_and_Standards/CG-002` | Content workstream operating model — chartered here at §6.3 |

---

## 18. References

**Within this repository**
[`PGD-000` Master Register](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`PGD-AUDIT-001`](../_AUDIT/PGD-AUDIT-001_Register_Integrity_Audit.md) ·
[Category 00 overview](_CATEGORY_OVERVIEW.md) ·
[`GV-002`](GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) ·
[`GV-003`](GV-003_Decision_Log_and_Change_Control_Procedure.md) ·
[`GV-005`](GV-005_RAID_Register.md) ·
[`GV-007`](GV-007_Estimation_Model_and_Resource_Plan.md) ·
[`GV-008`](GV-008_Programme_Budget_and_Cost_Baseline.md)

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-02`, `00-03`, `00-04`, `00-06`, `00-07` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01`, `06-02` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md`, `…_RFP.md`, `…_URD.md` ·
`../../project_content/_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md`

**External standards and sources** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| ISO 21500:2021 · ISO 21502:2020 · ISO 21503:2022 | Programme and project management constructs |
| PMBOK Guide 7th Edition (12 principles, 8 performance domains) | Charter contents; outcome-over-output framing |
| PRINCE2 7th Edition (2023) — five integrated elements; sustainability performance target | Management by exception; tolerance model |
| ISO/IEC 38500:2024 (edition 3, February 2024) — Engage → Evaluate → Direct → Monitor | Board role in §8 |
| Bangladesh Personal Data Protection Act 2026 (Law 63 of 2026); Amendment Ordinance No. 23 of 2026 | `CON-13`, `ASM-22`, `RSK-032` |
| Cyber Security Ordinance 2025 (in force; supersedes Cyber Security Act 2023, which superseded the Digital Security Act 2018) | Replaces the repealed citation found by `C-04a` |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. First charter in the programme's history. Introduces the counted 1,842 PW build position including portal effort; tiers the eighteen objectives; charters content as workstream 5; conditions approval on ten items | *pending Board* |

---

*`GV-001` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · 586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216*
*Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
