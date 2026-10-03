---
id: FIX-ERP2-M07
module_id: M07
module_code: CRM
module_name: CRM, Sales Pipeline & Account Management
category: B — Customer Engagement & Experience
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Commercial Squad
priority: P1
wave: W1
regulatory_verified: 2026-08-12
---

# M07 — CRM, Sales Pipeline & Account Management
### Category B · Code `CRM` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M07 |
| **Module code** | `CRM` |
| **Category** | B — Customer Engagement & Experience |
| **Status** | Existing (re-scoped — party master moved to M33, experience to M34) |
| **Priority** | **P1** |
| **Delivery wave** | W1 (Months 1–4) |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `crm`, `sale`, `calendar`) + L2 (OCA `crm_*`) + L5 (custom) |
| **Custom modules** | `cd_account_mgmt`, `cd_qbr`, `cd_sales_forecast` |
| **Requirement range** | FR-CRM-001 … FR-CRM-046 |
| **Requirement count** | 46 |
| **Effort estimate** | 22 person-weeks |
| **Depends on** | M33 Party Master · M37 Catalogue · M11 Pricing · M36 Quotation · M29 Identity |
| **Depended on by** | M08 Contract · M12 Marketplace · M35 Marketing · M40 Partner · M25 BI · M05 Managed Services |

---

## 2. Purpose

M07 is where 1000FiX **pursues revenue deliberately** rather than waiting for the phone to
ring.

It owns leads, opportunities, account plans, dedicated account managers and the quarterly
business review — the machinery by which a repair company with 250,000 monthly transactions
turns a fraction of them into contracted, recurring, managed relationships.

### Why It Exists

Today the Company has no pipeline. Corporate deals are pursued from memory and spreadsheets;
AMC renewals are chased when someone remembers; the 60% renewal rate is a symptom of that.
There is no forward view of contracted revenue, no measure of win rate, and no way to tell
whether a corporate account is growing or quietly leaving.

The v2.0 expansion makes this worse before it makes it better. Nine new revenue streams —
managed services, rental, refurbishment, marketplace, data services — are all **sold**, not
walked in. Without a pipeline, the Company will build the capability to deliver them and have
no mechanism to fill it.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.4 (BR-CRM-001…010) | Customer segmentation, corporate account management with multiple contacts and locations, campaign management |
| ERP BRD BO-08 | AMC renewal rate 60% → 85%; AMC customer base 2× |
| ERP BRD §12 Process 4 | AMC contract lifecycle: "Sales identifies lead → creates proposal → customer signs" |
| ERP BRD UC-007 | AMC renewal: account manager assigned a renewal task, contacts customer, creates renewal quotation |
| ERP URD Persona 6 | Sales & Marketing Director — pipeline visibility, AMC renewals |
| Portal roadmap IMPL-47 | **Dedicated Account Management System** — eligibility criteria for a dedicated account manager, auto-assignment algorithm, **quarterly business review automation with data extraction and PDF report generation** |
| Business Plan §Managed Service Contracts | Six contract families that must be sold, not walked in |
| Business Plan §IT Strategy Consulting | Consultative selling requiring account plans and roadmaps |
| Company Profile §Corporate Services | Bulk service agreements and enterprise support packages |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Lead capture, qualification, scoring and routing |
| 2 | Opportunity management through defined stages |
| 3 | Sales pipeline, forecasting and win/loss analysis |
| 4 | Account management: assignment, plans, objectives, stakeholder mapping |
| 5 | Dedicated account manager eligibility and auto-assignment |
| 6 | Quarterly business review scheduling, generation and action tracking |
| 7 | Activity management: calls, meetings, visits, tasks, follow-ups |
| 8 | Renewal pipeline for contracts, memberships and warranty products |
| 9 | Cross-sell and upsell opportunity identification |
| 10 | Sales team structure, territories and quota |
| 11 | Competitor and win/loss intelligence |
| 12 | Sales performance measurement and commission basis |
| 13 | Customer health signals feeding retention action |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Party identity, hierarchy, addresses, consent, credit limit** | **M33** | Master data governance; M07 raises a change request, never edits identity |
| Price calculation and price books | **M11** | Pricing is a commercial policy decision, not a sales activity |
| Quotation document, versions, approval, bidding | **M36** | A quotation is a legal instrument with its own lifecycle |
| Contract terms, entitlements, renewal execution | **M08** | M07 identifies and pursues the renewal; M08 executes it |
| Satisfaction scores, complaints, NPS | **M34** | Experience measurement is a distinct discipline |
| Campaign design and execution | **M35** | M07 consumes campaign-sourced leads; it does not run campaigns |
| Loyalty tiers, points, referral mechanics | **M10** | Membership mechanics |
| Conversation history and channels | **M27** | M07 reads conversations; it does not own them |
| Marketplace seller relationships | **M12** | Different party class, different commercial model |
| Brand partner and alliance relationships | **M40** | Channel management is a separate relationship type |
| Sales commission calculation and payment | **M53** | M07 supplies the attribution; M53 calculates and pays |
| MSP service delivery and SLA reporting | **M05** | M07 sells it; M05 delivers it |
| Project delivery for won engagements | **M67** | A won deal becomes a project |

### 3.3 Shared Concepts

| Concept | M07's Role | Owning Module |
|---|---|---|
| Party | References; requests master-data changes | M33 |
| Opportunity | **Owns** | M07 |
| Account plan | **Owns** | M07 |
| Quotation | Requests and tracks | M36 |
| Contract | Triggers creation on win | M08 |
| Renewal | Owns the pipeline; M08 owns execution | M07 / M08 |
| Customer health score | Consumes from M34 and M26; acts on it | M34 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Microsoft Dynamics 365 Sales** | Lead → opportunity → quote → order; AI lead scoring; relationship analytics | Lead-to-opportunity conversion model; scoring as an advisory signal | Platform-specific relationship analytics |
| **Salesforce Sales Cloud** | Account planning, opportunity teams, forecasting categories | Forecast categories (commit / best case / pipeline) and opportunity teams for multi-person pursuits | Full CPQ — that is M36 |
| **Oracle Sales Cloud** | Territory management, quota, sales performance | Territory and quota model | Full incentive compensation — that is M53 |
| **SAP Sales** | Sales area structure, activity management | Activity model | SAP's sales area complexity |
| **Odoo 19 CRM** | AI-powered lead scoring, natural-language search, activity scheduling, pipeline Kanban | The L1 substrate — pipeline, activities, stages | Odoo's default single-pipeline assumption |
| **PSA account management practice** | Dedicated account manager, quarterly business review, service-report-driven renewal conversation | **The QBR as an automated, data-driven deliverable** rather than a manually assembled slide deck | Consulting-firm engagement models |

**Design position.** Four deliberate differences.

First, **the QBR is generated, not written**. The portal roadmap already specifies QBR
automation with data extraction and PDF generation. An account manager who spends two days
assembling a quarterly review will not do it for thirty accounts. One that is assembled from
live service, SLA, spend and satisfaction data in minutes will be done for all of them — and
it is the single most effective renewal instrument available.

Second, **renewal is a pipeline, not a reminder**. The v1.0 design treated renewal as an
alert 60 days before expiry. At a 60% renewal rate the problem is not that nobody remembers;
it is that nobody owns it as a pursuit with a forecast, a value and a probability.

Third, **the pipeline covers nine revenue streams, not one**. Managed services, rental,
refurbishment and data services each have different sales cycles, different qualification
criteria and different stage definitions. M07 supports multiple pipelines with distinct
stage models rather than forcing one process on all of them.

Fourth, **M07 never touches master data**. Every benchmark CRM lets a salesperson edit the
customer's legal name and tax identifier. That is precisely how customer data quality dies.

---

## 5. Functional Areas & Features

### 5.1 Lead Management

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CRM-001 | Lead capture | Capture leads from the website, campaigns, referrals, the AI assistant, the contact centre, walk-in, events, marketplace enquiries and partner introductions, with source attribution | P1 | L1 |
| FR-CRM-002 | Lead qualification | Qualify against defined criteria — need, authority, budget, timing — recording the assessment | P1 | L1 |
| FR-CRM-003 | Lead scoring | Score leads on fit and engagement, using rules and, where available, the model from M26 as an advisory input | P2 | L5 |
| FR-CRM-004 | Lead routing | Route qualified leads to the right owner by product line, geography, account ownership and value, with round-robin and load balancing | P1 | L5 |
| FR-CRM-005 | Lead response SLA | Apply and measure a first-response SLA per lead source, with escalation on breach | P1 | L5 |
| FR-CRM-006 | Lead-to-party resolution | Match a lead against the party master before conversion; convert to an existing party where one exists rather than creating a duplicate | **P1** | L5 |
| FR-CRM-007 | Lead conversion | Convert a qualified lead into an opportunity, preserving the source attribution | P1 | L1 |
| FR-CRM-008 | Lead nurture handoff | Return unqualified but viable leads to M35 for nurture rather than discarding them | P2 | L5 |
| FR-CRM-009 | Duplicate lead detection | Detect duplicate leads for the same party and requirement, merging the interest rather than creating parallel pursuits | P2 | L5 |

### 5.2 Opportunity & Pipeline

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CRM-010 | Multi-pipeline support | Support distinct pipelines with their own stage models per revenue stream — managed services, AMC, corporate repair, rental, refurbishment sales, data services | **P1** | L5 |
| FR-CRM-011 | Opportunity management | Manage opportunities with value, expected close date, probability, products, competitor and decision criteria | P1 | L1 |
| FR-CRM-012 | Stage gating | Define entry and exit criteria per stage and prevent advancement without them | P1 | L5 |
| FR-CRM-013 | Opportunity team | Assign multiple contributors with roles — owner, technical, commercial, executive sponsor | P2 | L5 |
| FR-CRM-014 | Quotation linkage | Request a quotation from M36 and track its status and outcome against the opportunity | P1 | L5 |
| FR-CRM-015 | Win / loss recording | Record the outcome with a structured reason, competitor and price position | P1 | L5 |
| FR-CRM-016 | Contract handoff | On win, trigger contract creation in M08 carrying the agreed scope, terms and pricing | **P1** | L5 |
| FR-CRM-017 | Pipeline visualisation | Present the pipeline as Kanban, list, funnel and forecast views with drill-down | P1 | L1 |
| FR-CRM-018 | Pipeline hygiene | Flag stale opportunities, unrealistic close dates and stages without activity | P2 | L5 |

### 5.3 Forecasting & Sales Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CRM-019 | Forecast categories | Classify opportunities as Commit, Best Case, Pipeline or Omitted, independently of stage probability | P1 | L5 |
| FR-CRM-020 | Forecast roll-up | Roll forecasts up the sales hierarchy with manager judgement adjustment recorded separately from the raw figure | P1 | L5 |
| FR-CRM-021 | Forecast accuracy tracking | Compare forecast to actual by period, owner and pipeline, and report the variance | P2 | L5 |
| FR-CRM-022 | Territory management | Define territories by geography, industry, account size and product, with assignment rules | P2 | L5 |
| FR-CRM-023 | Quota management | Set quotas by period, owner and product line; track attainment | P2 | L5 |
| FR-CRM-024 | Sales activity metrics | Measure activity volume, conversion by stage, cycle time and win rate by owner and pipeline | P1 | L5 |
| FR-CRM-025 | Commission attribution | Record the attribution basis for each won deal and publish it to M53 for calculation | P2 | L5 |

### 5.4 Account Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CRM-026 | Account assignment | Assign an owner to every corporate, dealer and government account, with coverage rules for unassigned accounts | P1 | L5 |
| FR-CRM-027 | **Dedicated account manager eligibility** | Evaluate accounts against eligibility criteria — annual spend, contract value, asset estate size, strategic flag — and assign a dedicated manager automatically | **P1** | L5 |
| FR-CRM-028 | Account plan | Maintain an account plan with objectives, whitespace analysis, stakeholder map, risks and planned actions | P1 | L5 |
| FR-CRM-029 | Stakeholder mapping | Map decision makers, influencers, users and blockers within a corporate account, with relationship strength | P2 | L5 |
| FR-CRM-030 | Whitespace analysis | Identify products and services the account does not buy but is a candidate for, using its asset estate and peer comparison | P2 | L5 |
| FR-CRM-031 | Account health | Consume satisfaction, SLA attainment, complaint and spend trend signals and present a composite account health indicator | P1 | L5 |
| FR-CRM-032 | At-risk account workflow | Trigger a defined retention play when account health deteriorates | P2 | L5 |

### 5.5 Quarterly Business Review

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CRM-033 | **QBR scheduling** | Schedule QBRs automatically per the account's service tier, with reminders to both parties | **P1** | L5 |
| FR-CRM-034 | **QBR data assembly** | Assemble the review pack automatically: services delivered, SLA attainment, incident and complaint summary, spend, asset estate changes, entitlement consumption, satisfaction scores, and recommendations | **P1** | L5 |
| FR-CRM-035 | **QBR document generation** | Generate a branded, bilingual review document in PDF for the client, and publish it to the corporate portal | **P1** | L5 |
| FR-CRM-036 | QBR meeting record | Record attendees, discussion, decisions and agreed actions with owners and dates | P1 | L5 |
| FR-CRM-037 | QBR action tracking | Track agreed actions to completion and report them at the next review | P1 | L5 |
| FR-CRM-038 | QBR-driven opportunity | Convert recommendations accepted at a review directly into opportunities | P2 | L5 |

### 5.6 Renewals & Retention

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CRM-039 | **Renewal pipeline** | Maintain renewals as a forward pipeline with value, probability, owner and forecast — not as a reminder list | **P1** | L5 |
| FR-CRM-040 | Renewal triggers | Create renewal opportunities automatically at the configured lead time before contract, membership or warranty-product expiry | P1 | L5 |
| FR-CRM-041 | Renewal risk scoring | Score renewal risk from utilisation, satisfaction, SLA attainment, incident volume and engagement | P2 | L5 |
| FR-CRM-042 | Renewal play | Apply a defined renewal approach by risk band — automatic, light touch, or executive engagement | P2 | L5 |
| FR-CRM-043 | Win-back pipeline | Track lapsed contracts and customers as a distinct pipeline with its own plays | P2 | L5 |
| FR-CRM-044 | Cross-sell and upsell identification | Surface qualified expansion opportunities from asset estate, service history and peer comparison | P2 | L5 |

### 5.7 Activities & Collaboration

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CRM-045 | Activity management | Log calls, meetings, site visits, emails and tasks against leads, opportunities and accounts, with reminders and mobile capture | P1 | L1 |
| FR-CRM-046 | Sales collateral access | Provide access to current proposals, case studies, service descriptions and pricing guidance from M61 | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Master-data read-only discipline** | M07 has no write path to party identity attributes. Attempts to change them raise a change request to M33 rather than updating locally |
| T-02 | **Pipeline configurability** | Stage models, entry and exit criteria, and probability defaults are configuration, not code; adding a pipeline for a new revenue stream requires no release |
| T-03 | **QBR generation pipeline** | Data assembly runs as a scheduled job against the warehouse read model, not against transactional tables; a QBR for a 400-asset account completes in under 60 seconds |
| T-04 | **Document generation** | Bilingual PDF rendering with correct Bengali typography, branded template, and deterministic output for the same input |
| T-05 | **Forecast snapshot immutability** | Each period's forecast is snapshotted and never retroactively edited, so forecast accuracy is measurable |
| T-06 | **Health score composition** | Account health is computed from source-owned signals via event projection; M07 never recomputes another module's metric |
| T-07 | **Lead deduplication at capture** | Lead capture calls the M33 party match service before creating a lead, preventing pipeline pollution |
| T-08 | **Consent-aware outreach** | Any outbound activity generated from M07 evaluates consent through M33 before dispatch via M27 |
| T-09 | **Territory evaluation** | Territory assignment is evaluated on account attribute change, not by nightly full recomputation |
| T-10 | **Performance envelope** | Pipeline view ≤ 1.5 s for 2,000 open opportunities · account plan load ≤ 2 s · QBR generation ≤ 60 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M07 |
|---|---|---|
| **Sales / account manager** | Works from memory and a personal spreadsheet; renewals discovered late | Owns a pipeline with forecast, activities and renewal risk visible daily |
| **Chief Commercial Officer** | Has no forward view of revenue | Sees pipeline by stream, forecast against quota, win rate and cycle time |
| **Corporate client** | Hears from 1000FiX when something breaks or a renewal is due | Receives a quarterly review with evidence of what was delivered and what to do next |
| **Service Operations Director** | Learns about a large new contract when the work arrives | Sees the pipeline and can plan capacity against it |
| **Finance** | Cannot forecast contracted revenue | Sees weighted pipeline feeding the revenue forecast in M54 |
| **Corporate Services Head** | Sells managed services with no pursuit process | Runs an MSP pipeline with defined stages and qualification |
| **CEO** | Growth is a hope | Growth has a measurable funnel with conversion rates at each stage |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **AMC/RAMC renewal uplift** | Renewal as an owned pipeline with risk scoring and defined plays, supported by QBR evidence | **60% → 88% renewal**, contributing **BDT 72 lac/year** |
| **Contract base growth** | Systematic pursuit rather than inbound-only | **2.5× contract base** over 24 months |
| **Managed services pipeline** | The MSP line cannot reach BDT 95 lac/year without a sales motion | Precondition for **BDT 95 lac/year** (M05) |
| **Cross-sell into the installed base** | Whitespace analysis against the asset estate held in M17 | New revenue from existing customers at materially lower acquisition cost |
| **Reduced churn** | Account health signals and at-risk plays act before the customer leaves | Contributes to **churn 15% → 8%** |
| **Forecast reliability** | Snapshotted forecasts with measured accuracy | Enables capacity and cash planning in M54 |
| **Account manager productivity** | QBR assembly from days to minutes | One manager covers 30 accounts properly rather than 10 |
| **Higher-value corporate relationships** | Group hierarchy from M33 plus whitespace makes the true opportunity visible | Larger deals from the same accounts |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Commercial discipline becomes visible** | The Company can see, for the first time, whether growth is being pursued or waited for |
| **Institutional memory of relationships** | An account plan survives the account manager's departure — today the relationship leaves with the person |
| **Evidence-based renewal conversations** | The QBR changes the renewal from a price negotiation into a value review |
| **Capacity planning becomes possible** | Operations can staff against a pipeline instead of reacting to signed contracts |
| **Sales becomes coachable** | Stage conversion and cycle time by person makes management developmental rather than anecdotal |
| **A foundation for expansion** | Entering a new country requires a repeatable sales process, not a set of personal relationships |

---

## 8. Lifecycle & State Models

### 8.1 Lead

```
   CAPTURED --> QUALIFYING --> QUALIFIED --> CONVERTED (to opportunity)
       |            |              |
       |            |              +--> RECYCLED (to M35 nurture)
       |            |
       |            +--> DISQUALIFIED (reason recorded)
       |
       +--> DUPLICATE (merged into an existing lead or opportunity)
```

### 8.2 Opportunity — Managed Services Pipeline (illustrative)

```
   +-------------+
   | DISCOVERY   |  need established, stakeholders identified
   +------+------+
          | entry criteria: budget indication, decision timeline
   +------v-------------+
   | ESTATE ASSESSMENT  |  asset discovery, current-state review
   +------+-------------+
          |
   +------v-------------+
   | SOLUTION DESIGN    |  service scope, SLA tier, coverage window
   +------+-------------+
          | quotation requested from M36
   +------v-------------+
   | PROPOSAL           |
   +------+-------------+
          |
   +------v-------------+
   | NEGOTIATION        |  commercial and contractual terms
   +------+-------------+
          |
   +------v----+        +----------+
   |    WON    |        |   LOST   |  structured reason + competitor
   +------+----+        +----------+
          |
          v
   CONTRACT CREATED IN M08 --> ONBOARDING PROJECT IN M67 --> DELIVERY IN M05

   Each revenue stream has its own stage model. Stages are configuration.
```

### 8.3 Renewal

```
   +------------------+
   | RENEWAL CREATED  |  auto-generated at lead time before expiry
   +--------+---------+
            | risk scored: utilisation, satisfaction, SLA, incidents, engagement
   +--------v---------+
   |   RISK BANDED    |
   +--+-----+------+--+
      |     |      |
   LOW   MEDIUM   HIGH
      |     |      |
      v     v      v
   AUTO  LIGHT  EXECUTIVE      <- renewal play selected
   RENEW TOUCH  ENGAGEMENT
      |     |      |
      +-----+------+
            |
   +--------v---------+       +------------------+
   |    RENEWED       |       |     LAPSED       |--> WIN-BACK PIPELINE
   +------------------+       +------------------+
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-CRM-01 | **M07 may not create or amend party identity attributes; it raises a change request to M33** | **H** | CTO |
| BRU-CRM-02 | A lead must be matched against the party master before conversion; conversion may not create a duplicate party | **H** | Data Steward |
| BRU-CRM-03 | An opportunity cannot advance a stage without its declared entry criteria being met | **H** | CCO |
| BRU-CRM-04 | An opportunity cannot be marked Won without a linked accepted quotation from M36 | **H** | CCO |
| BRU-CRM-05 | Every Lost outcome requires a structured reason code | **H** | CCO |
| BRU-CRM-06 | A forecast snapshot, once taken for a period, cannot be edited | **H** | CFO |
| BRU-CRM-07 | Manager forecast adjustment is recorded separately from the raw roll-up and is attributable | **H** | CFO |
| BRU-CRM-08 | Every corporate, dealer and government account has a named owner at all times | **H** | CCO |
| BRU-CRM-09 | Dedicated account manager assignment follows the published eligibility criteria; exceptions require CCO approval | **A** | CCO |
| BRU-CRM-10 | A QBR is scheduled for every account above the eligibility threshold, at the contracted cadence | **H** | CCO |
| BRU-CRM-11 | **Any outbound activity generated from M07 evaluates consent in M33 before dispatch** | **H** | CDO |
| BRU-CRM-12 | A renewal opportunity is created automatically at the configured lead time; it may be closed but not deleted | **H** | CCO |
| BRU-CRM-13 | Commission attribution is recorded at the point of win and is not retrospectively altered without CFO approval | **H** | CFO |
| BRU-CRM-14 | An opportunity value above the delegated threshold requires management review before proposal | **H** | CCO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.lead` | `fix_lead` | Unqualified interest | source, source_detail, party_id, contact_name, requirement, score, state, owner_id, first_response_at |
| `fix.opportunity` | `fix_opportunity` | A pursued deal | party_id, pipeline_id, stage_id, value, currency, probability, forecast_category, expected_close, owner_id, competitor, state |
| `fix.pipeline` | `fix_pipeline` | Stage model per revenue stream | code, name, revenue_stream, stages_json, default_probabilities |
| `fix.opportunity.stage.log` | `fix_opportunity_stage_log` | Stage history | opportunity_id, stage, entered_at, exited_at, duration_days, actor |
| `fix.opportunity.team` | `fix_opportunity_team` | Pursuit contributors | opportunity_id, party_id, role |
| `fix.win.loss` | `fix_win_loss` | Outcome analysis | opportunity_id, outcome, reason_code, competitor, price_position, notes |
| `fix.account.assignment` | `fix_account_assignment` | Ownership | party_id, owner_id, assignment_type, dedicated, effective_from, effective_to |
| `fix.account.plan` | `fix_account_plan` | Strategic plan | party_id, period, objectives, whitespace_json, risks, actions, reviewed_at |
| `fix.stakeholder.map` | `fix_stakeholder_map` | Decision landscape | party_id, contact_id, role_type, influence, disposition, relationship_strength |
| `fix.account.health` | `fix_account_health` | Composite indicator | party_id, satisfaction, sla_attainment, complaint_rate, spend_trend, engagement, composite, evaluated_at |
| `fix.qbr` | `fix_qbr` | Quarterly business review | party_id, period, scheduled_for, held_on, document_id, attendees, state |
| `fix.qbr.action` | `fix_qbr_action` | Agreed action | qbr_id, description, owner_party, owner_internal, due_date, state |
| `fix.renewal` | `fix_renewal` | Renewal pursuit | source_type, source_id, party_id, value, expiry_date, risk_band, play, owner_id, state |
| `fix.forecast.snapshot` | `fix_forecast_snapshot` | Immutable period forecast | period, owner_id, pipeline_id, commit, best_case, pipeline_value, manager_adjustment, taken_at |
| `fix.territory` | `fix_territory` | Coverage definition | code, criteria_json, owner_id, effective_from |
| `fix.quota` | `fix_quota` | Target | owner_id, period, pipeline_id, target_value |
| `fix.sales.activity` | `fix_sales_activity` | Interaction record | subject_type, subject_id, activity_type, occurred_at, owner_id, outcome, next_action |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party`, `fix.party.hierarchy` | M33 | Read; change request only |
| `fix.consent.record` | M33 | Evaluate before outreach |
| `fix.quotation` | M36 | Request; read status |
| `fix.contract`, `fix.entitlement` | M08 | Trigger creation; read for renewal |
| `fix.asset`, `fix.asset.estate` | M17 / M49 | Read for whitespace analysis |
| `fix.survey.response`, `fix.complaint` | M34 | Read for account health |
| `fix.contract.sla` | M08 | Read for account health and QBR |
| `fix.conversation` | M27 | Read for engagement signal |
| `fix.catalogue.item` | M37 | Read for opportunity products |
| `fix.knowledge.article` | M61 | Read for sales collateral |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-CRM-01 | Lead captured | Match against the party master, score, route to owner, start the response SLA clock | Route to a default queue; alert CCO |
| AUT-CRM-02 | Lead response SLA at 75% | Escalate to the owner's manager | Repeat and escalate |
| AUT-CRM-03 | Opportunity marked Won | Create the contract in M08, create the onboarding project in M67 where applicable, publish commission attribution to M53 | Create a manual handoff task |
| AUT-CRM-04 | Opportunity stale beyond threshold | Flag for pipeline hygiene review; notify the owner then the manager | — |
| AUT-CRM-05 | Contract, membership or warranty product approaching expiry | Create a renewal opportunity at the configured lead time, score risk, assign the play | Create a manual renewal task |
| AUT-CRM-06 | Account crosses the dedicated-manager eligibility threshold | Assign a dedicated account manager per the algorithm; notify both parties | Queue for CCO assignment |
| AUT-CRM-07 | **QBR due** | Assemble the data pack, generate the bilingual document, publish to the corporate portal, notify the client and the account manager | Alert the account manager to assemble manually |
| AUT-CRM-08 | QBR action overdue | Notify the owner; escalate to the account manager then the CCO | — |
| AUT-CRM-09 | Account health deteriorates below threshold | Trigger the at-risk retention play; notify the account manager and the CCO | — |
| AUT-CRM-10 | Period end | Take the forecast snapshot; lock it; compute prior-period accuracy | Alert CFO |
| AUT-CRM-11 | Asset estate change detected in M17 | Re-evaluate whitespace; surface new cross-sell candidates | — |
| AUT-CRM-12 | Contract lapses without renewal | Move to the win-back pipeline with a defined re-engagement schedule | — |

---

## 12. Interfaces

### 12.1 Upstream — M07 Consumes

| Source | What | Mechanism |
|---|---|---|
| M33 Party Master | Party identity, hierarchy, contacts, consent, credit standing | REST + event |
| M35 Marketing | Campaign-sourced and nurtured leads | Event |
| M27 Contact Centre | Leads raised during conversations; engagement signal | Event |
| M32 Conversational AI | Leads captured by the assistant | Event |
| M12 Marketplace | Enquiries that warrant a direct 1000FiX pursuit | Event |
| M40 Partner | Partner-introduced leads | Event |
| M17 Asset Registry | Asset estate for whitespace and QBR | REST |
| M08 Contract | Contract terms, expiry dates, entitlement consumption | REST + event |
| M05 Managed Services | SLA attainment, incident volume, service reports for QBR | REST |
| M34 Customer Experience | Satisfaction scores and complaint history for account health | Event projection |
| M36 Quotation | Quotation status and acceptance | Event |
| M11 Pricing | Price guidance for opportunity valuation | REST |
| M26 AI/ML | Lead score and churn-risk model outputs | REST with fallback |

### 12.2 Downstream — M07 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M08 Contract | Won opportunity triggering contract creation | Command |
| M36 Quotation | Quotation requests with scope and context | Command |
| M53 Settlement | Commission attribution on won deals | Event |
| M54 FP&A | Weighted pipeline for revenue forecasting | Warehouse extract |
| M67 Project Management | Onboarding project trigger for won engagements | Command |
| M35 Marketing | Recycled leads for nurture; account context for targeting | Event |
| M27 Contact Centre | Outbound activity requests | Command |
| M24 Documents | QBR documents for retention | Command |
| M25 Business Intelligence | Pipeline, forecast, win/loss and activity facts | Warehouse extract |
| P04 Corporate Portal | QBR documents, account plan summary, service review actions | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `lead.captured` | lead, source, party match result | M35, M25 |
| `lead.qualified` | lead, score, assessment | M25 |
| `lead.converted` | lead, opportunity, party | M35, M25 |
| `opportunity.created` | opportunity, party, pipeline, value | M25, M54 |
| `opportunity.stage_changed` | opportunity, from stage, to stage | M25 |
| `opportunity.won` | opportunity, value, products, terms, attribution | **M08, M53, M67, M54** |
| `opportunity.lost` | opportunity, reason, competitor, price position | M11, M25 |
| `account.assigned` | party, owner, dedicated flag | M27, P04 |
| `account_plan.updated` | party, period, objectives | M25 |
| `account.health_changed` | party, composite, drivers | M34, M22, CCO |
| `qbr.generated` | party, period, document reference | P04, M24 |
| `qbr.action_created` | party, action, owner, due date | M27 |
| `renewal.created` | source, party, value, expiry, risk band | M08, M54 |
| `renewal.lost` | source, party, reason | M34, M35 |
| `forecast.snapshot_taken` | period, owner, commit, best case, pipeline | M54 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/leads` | POST / GET | Capture and list leads | P01, P03, M27, M32, M35 |
| `/api/v1/leads/{id}/convert` | POST | Convert to opportunity | P03 |
| `/api/v1/opportunities` | POST / GET | Manage opportunities | P03 |
| `/api/v1/opportunities/{id}/stage` | POST | Advance stage with criteria check | P03 |
| `/api/v1/opportunities/{id}/close` | POST | Record win or loss | P03 |
| `/api/v1/pipeline` | GET | Pipeline views and filters | P03, P06 |
| `/api/v1/forecast/{period}` | GET / POST | Forecast view and snapshot | P03, P06 |
| `/api/v1/accounts/{party}/plan` | GET / PUT | Account plan | P03 |
| `/api/v1/accounts/{party}/health` | GET | Account health composite | P03, P04 |
| `/api/v1/qbr/{party}/{period}` | GET / POST | QBR pack and record | P03, P04 |
| `/api/v1/renewals` | GET | Renewal pipeline | P03, P06 |
| `/api/v1/activities` | POST / GET | Activity logging | P03, mobile |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R04 Chief Commercial Officer | C R U D A | All pipelines and accounts |
| R22 Account Manager (Corporate) | C R U | Own accounts and opportunities |
| R21 Sales Manager | C R U | Own leads and opportunities |
| Corporate Services Head | C R U | MSP pipeline |
| R05 Operations Director | R | Pipeline visibility for capacity planning |
| R26 Finance Manager | R | Forecast, value, commission attribution |
| R06 Branch Manager | R U | Opportunities in own branch's territory |
| R34 Contact Centre Agent | C | Lead creation only |
| R32 Quality Manager / ISO Coordinator | R | Win/loss reasons relating to service quality |
| R37 Corporate Portal User | R | Own company's QBR documents and actions only |
| R01 Chief Executive Officer | R | All — pipeline and forecast |

**Field-level restrictions.** Opportunity margin and cost assumptions are visible to R21,
R22, R26 and R01 only. Competitor intelligence is restricted to R21, R22 and R23.

**Segregation of duties.** The person who records a win cannot approve their own commission
attribution change (SOD-16).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Pipeline board | Sales team, CCO | Real time | Opportunities by stage, value, age, owner; stale flags |
| Forecast | CCO, CFO, CEO | Weekly | Commit, best case, pipeline by owner and stream; adjustment trail |
| Forecast accuracy | CFO | Monthly | Prior-period forecast against actual by owner |
| Win/loss analysis | CCO, CTO, Quality | Monthly | Reasons, competitors, price position, patterns by product and segment |
| Conversion funnel | CCO | Monthly | Lead → qualified → opportunity → won, with stage conversion and cycle time |
| **Renewal pipeline** | **CCO, CFO** | **Weekly** | Renewals by month, value, risk band, play, owner |
| Account health board | CCO, account managers | Weekly | Accounts by health band; deteriorating accounts with drivers |
| **QBR compliance** | **CCO** | **Monthly** | QBRs due, held, overdue; action closure rate |
| Whitespace report | CCO, account managers | Quarterly | Products not held by account, ranked by fit and value |
| Activity report | Sales managers | Weekly | Activity volume and mix by owner; correlation with conversion |
| Territory coverage | CCO | Quarterly | Accounts covered, unassigned accounts, load by owner |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| KPI-134 | AMC / RAMC renewal rate | 60% | 78% | **88%** |
| KPI-135 | Contract base growth | baseline | 1.6× | **2.5×** |
| KPI-136 | Lead first-response within SLA | unmeasured | 88% | **> 95%** |
| KPI-137 | Lead-to-opportunity conversion | unmeasured | 28% | **> 35%** |
| KPI-138 | Opportunity win rate | unmeasured | 30% | **> 38%** |
| KPI-139 | Average sales cycle time | unmeasured | baselined | **−20%** |
| KPI-140 | Forecast accuracy (within ±10%) | n/a | 70% | **> 85%** |
| KPI-141 | **QBRs held on schedule** | 0% | 85% | **> 95%** |
| KPI-142 | QBR actions closed by next review | n/a | 75% | **> 88%** |
| KPI-143 | Corporate accounts with a current account plan | 0% | 80% | **100%** |
| KPI-144 | Accounts with a named owner | unmeasured | **100%** | **100%** |
| KPI-145 | Customer churn (contracted accounts) | ~15% | 11% | **< 8%** |
| KPI-146 | Cross-sell revenue from installed base | unmeasured | baselined | **+25%** |
| KPI-147 | Stale opportunities in pipeline | n/a | < 15% | **< 8%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `crm`, `sale`, `calendar`, `mail` | 38% |
| L2 | OCA `crm_*` (stage, lead source, phonecall, territory) | 12% |
| L5 | `cd_account_mgmt`, `cd_qbr`, `cd_sales_forecast` | 50% |

### 16.2 Custom Development

> CD identifiers are **provisional** pending the unified register in `02-05` (audit H-03).

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-040 | `cd_account_mgmt` — assignment, eligibility, account plan, stakeholder map, health | Odoo module | 7 PW |
| CD-041 | **`cd_qbr`** — scheduling, data assembly, bilingual document generation, action tracking | Odoo module + service | **6 PW** |
| CD-042 | `cd_sales_forecast` — forecast categories, snapshots, accuracy, renewal pipeline | Odoo module | 5 PW |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M07 is scheduled in **W1** (P1) but declares a dependency on 2 module(s) that land later: **M11** (W3); **M36** (W3). One of three things must be true before the W1 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W1 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M07 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W1 plan for M07 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| **M33 Party Master** | **Blocking** — an opportunity requires a governed party; lead matching depends on it |
| M37 Catalogue | Opportunity products must exist |
| M29 Identity | Ownership, territory scoping and field-level restrictions |
| M36 Quotation | Win requires an accepted quotation — may be stubbed in W1, enforced from W3 |
| M08 Contract | Win triggers contract creation — may be stubbed in W1, enforced from W4 |
| M05 / M34 | QBR data assembly requires SLA and satisfaction data — QBR generation is therefore **W4**, not W1 |

**Note on phasing.** M07 core (leads, opportunities, pipeline, accounts) delivers in W1. The
**QBR capability delivers in W4**, once M05 SLA data and M34 satisfaction data exist to
populate it. Generating a QBR from an empty data set would discredit the instrument.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Corporate account lists held by account managers | ~2,000 | `fix.account.assignment` | W1 |
| Active AMC/RAMC contracts requiring renewal tracking | 5,000+ | `fix.renewal` | W1 |
| Known opportunities in progress | Unknown, likely < 200 | `fix.opportunity` | W1 |
| Historical win/loss data | **Not migrated** — none exists in structured form | — | — |

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A lead cannot be converted without a party match check | Negative test |
| AC-02 | **M07 cannot write to any party identity attribute, including via API** | **Negative test through UI and API** |
| AC-03 | An opportunity cannot advance without stage entry criteria met | Negative test |
| AC-04 | A won opportunity creates the contract in M08 with correct scope and terms | End-to-end demonstration |
| AC-05 | Distinct pipelines operate for at least three revenue streams with different stage models | Configuration demonstration |
| AC-06 | Forecast snapshots are immutable once taken | Negative test |
| AC-07 | Renewal opportunities generate automatically at the configured lead time for contracts, memberships and warranty products | Scripted test across all three sources |
| AC-08 | **A QBR generates automatically with live service, SLA, spend and satisfaction data in under 60 seconds** | **Timed test on a 400-asset account** |
| AC-09 | The QBR document renders correctly in Bengali and English with correct branding | Visual review by CCO |
| AC-10 | Dedicated account manager assignment follows the eligibility algorithm | Test across threshold boundaries |
| AC-11 | **Outbound activity from M07 is blocked where consent is absent** | **Negative test** |
| AC-12 | Pipeline view loads in ≤ 1.5 s with 2,000 open opportunities | Load test |
| AC-13 | Every corporate, dealer and government account has a named owner at go-live | Data completeness report |
| AC-14 | CCO and two account managers sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What are the dedicated account manager eligibility criteria — annual spend, contract value, asset count, or a composite? | CCO | W1 build |
| Q-02 | How many distinct pipelines are needed at launch, and what are their stage models? | CCO | W1 design |
| Q-03 | What is the QBR cadence by account tier — quarterly for all, or monthly for the top tier? | CCO | W4 build |
| Q-04 | Does the Company have a sales team today, or must the role be created? This determines whether M07 is a system change or an organisational one. | CEO / CCO | **W1 minus 2 months** |
| Q-05 | Is sales commission in scope for W1, or deferred to M53 in W4? | CFO | W1 build |
| Q-06 | What renewal lead time applies to each contract family — 90, 60 or 30 days? | CCO | W1 build |
| Q-07 | Who owns the marketplace-sourced lead — the seller or 1000FiX? This affects channel conflict. | CCO / CEO | W7 (M12) |

**Q-04 is the material one.** M07 assumes a sales function exists. If it does not, the module
will be deployed to an organisation with nobody to use it.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3 (M33/M07 boundary) ·
`M33_Customer_and_Party_Master_Management.md` ·
`M34_Customer_Experience_Feedback_and_Complaints.md` ·
`M35_Marketing_Campaigns_and_Demand_Generation.md` ·
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §3 (the commercial chain) ·
`03_Modules/A_Service_Delivery_and_Operations/M05_Remote_Support_and_Managed_Services.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.4, BO-08, §12 Process 4,
UC-007 · `1000FiX_ERP_System_Comprehensive_URD.md` Persona 6 ·
`Intergrated_web_portal/.../IMPL-47_Dedicated_Account_Management_System_Guide.md` — eligibility
criteria, auto-assignment algorithm, QBR automation architecture, data extraction service, PDF
generation · `1000fix_business/Business planning for 1000 fix.docx` §Managed Service Contracts,
§IT Strategy Consulting · `1000FiX_Services_Company_Profile.md` §Corporate Services

**External benchmark**
Microsoft Dynamics 365 Sales — lead-to-opportunity model and AI lead scoring ·
Salesforce Sales Cloud — forecast categories and opportunity teams ·
Oracle Sales Cloud — territory and quota management ·
Odoo 19 CRM — AI-powered lead scoring, natural-language search, activity scheduling ·
Professional services account management practice — dedicated account manager and
data-driven quarterly business review

---

*Module M07 · Category B · 1000FiX ERP System v2.0 · CONFIDENTIAL*
