---
id: FIX-ERP2-M35
module_id: M35
module_code: MKT
module_name: Marketing, Campaigns & Demand Generation
category: B — Customer Engagement & Experience
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Marketing Head
system_owner: Commercial Squad
priority: P2
wave: W5
regulatory_verified: 2026-08-12
---

# M35 — Marketing, Campaigns & Demand Generation
### Category B · Code `MKT` · ★ New module in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M35 |
| **Module code** | `MKT` |
| **Category** | B — Customer Engagement & Experience |
| **Status** | ★ **New** — split from M10 Loyalty after enterprise benchmarking |
| **Priority** | **P2** |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | Marketing Head |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `mass_mailing`, `marketing_automation`) + L5 (custom) |
| **Custom modules** | `cd_campaign`, `cd_journey_orchestration`, `cd_attribution`, `cd_content` |
| **Requirement range** | FR-MKT-001 … FR-MKT-040 |
| **Requirement count** | 40 |
| **Effort estimate** | 17 person-weeks |
| **Depends on** | M33 Party Master · M27 Contact Centre · M10 Loyalty · M07 CRM · M34 Experience |
| **Depended on by** | M07, M10, M12, M38, M40, M25 |

---

## 2. Purpose

M35 is how 1000FiX **creates demand deliberately** rather than waiting for devices to break.

It owns campaign planning and execution, audience selection, customer journey orchestration,
content and creative management, budget control, and the attribution that tells the Company
which marketing spend actually produced revenue.

### Why It Exists

The Company has a large installed base — 250,000+ customers a month, 200,000+ registered
devices, 51+ branches — and almost no systematic way to reach it. Seasonal demand for AC
servicing, monsoon appliance failures, winter geyser maintenance and the FiXnChill campaign
are all real, recurring and predictable, and all currently addressed ad hoc.

More importantly, the v2.0 expansion adds nine revenue streams that **must be marketed**.
Rental, refurbished device sales, data services and the marketplace do not generate their own
demand the way a broken laptop does. Someone has to tell customers those services exist.

### Why It Is Separate from M10

M10 owns the **mechanics** — what a voucher is worth, how points are earned, what a tier
entitles you to. M35 owns the **campaign** — who receives an offer, when, through which
channel, and whether it worked. Merging them makes every campaign change a change to the
loyalty ledger, and makes loyalty economics indistinguishable from campaign performance.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-CRM-010 | "Promotional campaign management with coupon/voucher generation and tracking" |
| ERP BRD BO-08 | Drive AMC/RAMC subscription growth; 2× customer base |
| Service App SOW §Campaigns | "Run various promotional campaigns and offers for the total app platform / specific service providers / specific product campaigns. Various campaigns may include earning double points, **partnered campaigns with various brands**, special day campaigns" |
| Service App SOW §Campaign management | "**Scheduled auto on/off the campaign**… push notification feature… different types of forms integration and reporting facility" |
| Service App SOW §Advertising | "In-app ad section on different pages / check-out page" |
| Service App SOW §Personalisation | "Offer tailored recommendations and service suggestions" |
| Company Profile §FiXnChill Campaign | "Seasonal promotional offers, special service packages, customer engagement initiatives" |
| Company Profile §Blog & Articles | Content marketing already in practice — seasonal care advice, troubleshooting guides |
| Corporate website programme | Service, city and brand landing page taxonomy already built — the demand-capture surface M35 drives traffic to |
| **BTRC regulation** *(verified 2026-08-12)* | **Do Not Disturb registry; prohibition on promotional SMS from midnight to dawn**; masking rules |
| **Personal Data Protection Act 2026** *(verified 2026-08-12)* | Marketing requires clear, explicit, specific and freely given consent; withdrawal must be simple and immediate |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Campaign planning, briefing, approval and scheduling |
| 2 | Audience selection from governed segments |
| 3 | Journey orchestration — multi-step, multi-channel, behaviour-triggered |
| 4 | Content and creative management with versioning and approval |
| 5 | Offer selection (mechanics supplied by M10) |
| 6 | Campaign scheduling with automatic activation and deactivation |
| 7 | A/B and holdout testing |
| 8 | Budget planning, commitment and spend tracking |
| 9 | **Attribution — which marketing activity produced which revenue** |
| 10 | Lead generation and handoff to M07 |
| 11 | Lead nurture for unqualified but viable leads |
| 12 | In-app and portal advertising placement management |
| 13 | Seasonal and event campaign templates |
| 14 | Brand co-marketing campaigns with partners |
| 15 | Marketing performance reporting and ROI |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Message delivery, consent enforcement, DND, quiet hours** | **M27** | The delivery layer is the only enforceable control point |
| **Consent record and segment definition** | **M33** | Master data governance |
| **Voucher, points, tier and referral mechanics** | **M10** | M35 selects an offer; M10 defines what it is worth |
| Lead qualification, opportunity, pipeline | **M07** | M35 generates; M07 pursues |
| Price and discount calculation | **M11** | Marketing does not set prices |
| Satisfaction measurement | **M34** | Campaign response is not experience measurement |
| Corporate website content and SEO | Website programme | M35 drives traffic to it; the site is a separate programme |
| Marketplace seller advertising and boost | **M12** | Seller-purchased promotion is a marketplace revenue mechanic |
| Partner and alliance relationships | **M40** | M35 runs co-marketing; M40 owns the relationship |
| Sales collateral and proposals | **M07** / **M61** | Sales enablement, not demand generation |
| Employer branding and recruitment marketing | **M58** | Different audience |

### 3.3 Shared Concepts

| Concept | M35's Role | Owning Module |
|---|---|---|
| Segment | Consumes the definition | M33 |
| Consent | Relies on; never overrides | M33 / M27 |
| Offer mechanics | Selects and uses | M10 |
| Campaign | **Owns** | M35 |
| Journey | **Owns marketing journeys**; M34 owns experience journeys | M35 / M34 |
| Lead | Generates | M07 |
| Attribution | **Owns marketing attribution**; M53 owns commission attribution | M35 / M53 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Marketing automation platforms (2026)** | Predictive segmentation, next-best-action, **autonomous journey orchestration**, multi-touch nurture that adapts to engagement, dynamic audiences updating in real time, **attribution models allocating credit across the complete customer journey** | **Journey orchestration and multi-touch attribution** as the core capabilities | Platforms with a list database behind a segmentation interface — the distinction the 2026 market draws is between genuine profile stores and list databases; ours is M33 |
| **Customer journey orchestration** | Unified touchpoints in a single orchestration layer with consistent messaging, optimised timing and centralised attribution | The orchestration-layer model, with M27 as the delivery layer beneath it | Standalone journey tools that hold their own customer profile |
| **Consent-first orchestration** | Privacy regulation makes **consent-aware suppression essential**; winning brands prioritise consent-driven data ecosystems | **Consent-first by architecture** — M35 cannot send; it can only request that M27 sends | Consent checks at campaign design time, which are bypassed by any manual send |
| **Odoo `marketing_automation` and `mass_mailing`** | Campaign workflows, mailing lists, A/B testing | The L1 substrate for campaign execution | Odoo's list-based audience model — audiences come from M33 segments |
| **Bangladesh SMS practice** | BTRC DND registry, midnight-to-dawn prohibition, masked and non-masked sender rules | Compliance delegated entirely to M27, where it is enforceable | Managing compliance in the campaign tool |

**Design position.** Five deliberate differences.

First, **M35 has no send capability at all**. It requests. M27 decides whether the message may
go, to whom, on which channel, and at what hour. This is architectural, not procedural: M35
holds no provider credentials. It is the only design in which consent, DND and quiet-hours
compliance cannot be bypassed by a marketer under deadline pressure.

Second, **audiences come from governed segments, never from exports**. A marketer cannot
upload a list. Every audience resolves to an M33 segment definition, which means every audience
is reproducible, auditable and consent-aware.

Third, **attribution is multi-touch and holdout-validated**. Last-click attribution flatters
the last channel and misleads the budget. Where volume permits, campaigns run with a holdout
group so incremental effect is measurable rather than assumed.

Fourth, **seasonality is a first-class concept**. AC servicing before summer, geyser
maintenance before winter, monsoon appliance failures, Eid periods and the FiXnChill campaign
are recurring and predictable. They are templates with a calendar, not annual improvisation.

Fifth, **campaigns must not create operational overload**. A successful AC campaign in Dhaka in
April produces demand the field organisation may not be able to serve. M35 checks planned
demand against M02 capacity before a campaign activates.

---

## 5. Functional Areas & Features

### 5.1 Campaign Management

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKT-001 | Campaign definition | Define a campaign with objective, audience, offer, channels, content, budget, schedule and success measures | P2 | L1 |
| FR-MKT-002 | Campaign brief and approval | Route campaigns for approval by value and audience size, recording the decision | P2 | L5 |
| FR-MKT-003 | **Scheduled activation** | Activate and deactivate campaigns automatically at defined times, per the Service App SOW | **P2** | L5 |
| FR-MKT-004 | Campaign types | Support acquisition, retention, win-back, cross-sell, upsell, seasonal, event, referral, brand co-marketing and reactivation campaigns | P2 | L5 |
| FR-MKT-005 | Campaign hierarchy | Group campaigns into programmes and calendars, with roll-up reporting | P3 | L5 |
| FR-MKT-006 | **Capacity check** | Check projected demand against operational capacity in M02 before activation, and warn or block where capacity is insufficient | **P2** | L5 |
| FR-MKT-007 | Campaign calendar | Present a forward calendar of planned and active campaigns, with conflict detection | P2 | L5 |
| FR-MKT-008 | Emergency stop | Halt a running campaign immediately across all channels | **P2** | L5 |

### 5.2 Audience & Segmentation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKT-009 | **Segment-based audiences** | Build audiences only from governed M33 segment definitions; **manual list upload is not permitted** | **P2** | L5 |
| FR-MKT-010 | Audience composition | Combine segments with include, exclude and intersect logic | P2 | L5 |
| FR-MKT-011 | Dynamic audiences | Re-evaluate audience membership continuously so entering and leaving customers are handled correctly mid-campaign | P2 | L5 |
| FR-MKT-012 | Audience estimation | Estimate reachable audience size **after** consent, DND and fatigue suppression, before the campaign is approved | **P2** | L5 |
| FR-MKT-013 | Suppression lists | Apply campaign-level suppression for recent recipients, active complaints, credit hold and do-not-market flags | P2 | L5 |
| FR-MKT-014 | Holdout groups | Reserve a randomised holdout from the audience to measure incremental effect | P2 | L5 |
| FR-MKT-015 | Predictive audiences | Use propensity and churn models from M26 to build audiences, as an advisory input | P3 | L5 |

### 5.3 Journey Orchestration

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKT-016 | Journey design | Design multi-step journeys with entry criteria, waits, branches, conditions and exit criteria | P2 | L1 |
| FR-MKT-017 | Behaviour triggers | Trigger journey steps on customer behaviour — service completed, quote not accepted, contract expiring, device ageing, cart abandoned, review left | P2 | L5 |
| FR-MKT-018 | Multi-channel steps | Compose a journey from steps across SMS, WhatsApp, email, push, in-app and portal | P2 | L5 |
| FR-MKT-019 | Journey exit | Exit a customer from a journey on conversion, on consent withdrawal, on complaint, or on entering a conflicting journey | **P2** | L5 |
| FR-MKT-020 | Journey conflict resolution | Prevent a customer receiving conflicting messages from concurrent journeys, with priority rules | **P2** | L5 |
| FR-MKT-021 | Nurture journeys | Nurture unqualified leads returned by M07 until they qualify or disengage | P2 | L5 |
| FR-MKT-022 | Lifecycle journeys | Run onboarding, reactivation, renewal reminder and win-back journeys triggered by lifecycle events | P2 | L5 |
| FR-MKT-023 | Journey performance | Report entry, progression, conversion and drop-off at every step | P2 | L5 |

### 5.4 Content, Offers & Creative

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKT-024 | Content library | Maintain campaign content and creative with versioning, approval and expiry | P2 | L5 |
| FR-MKT-025 | Bilingual content | Author and approve every customer-facing asset in Bengali and English | **P2** | L5 |
| FR-MKT-026 | Personalisation | Personalise content with party, device, service history and entitlement variables, with safe fallbacks | P2 | L5 |
| FR-MKT-027 | Offer selection | Select an offer from M10 mechanics — voucher batch, points multiplier, tier benefit, bundled price | P2 | L5 |
| FR-MKT-028 | Template governance | Require approval before a template is used in a live campaign, and version it | P2 | L5 |
| FR-MKT-029 | Landing page linkage | Link campaigns to corporate website landing pages with tracked parameters | P3 | L5 |
| FR-MKT-030 | **Advertising placement** | Manage in-app and portal advertising placements by page and position, per the Service App SOW | P3 | L5 |

### 5.5 Testing, Budget & Attribution

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MKT-031 | A/B testing | Test content, offer, channel and timing variants with statistically valid allocation and winner selection | P2 | L5 |
| FR-MKT-032 | Budget planning | Plan budget by campaign, programme, channel and period | P2 | L5 |
| FR-MKT-033 | Spend tracking | Track committed and actual spend, including delivery cost from M27 and offer cost from M10 | P2 | L5 |
| FR-MKT-034 | Budget control | Prevent a campaign exceeding its approved budget without re-approval | P2 | L5 |
| FR-MKT-035 | **Multi-touch attribution** | Attribute revenue across the touchpoints in a customer's journey, using a defined and documented model | **P2** | L5 |
| FR-MKT-036 | **Incremental measurement** | Measure incremental effect against the holdout group, distinguishing campaign-caused revenue from revenue that would have occurred anyway | **P2** | L5 |
| FR-MKT-037 | Campaign ROI | Report revenue attributed and incremental against total campaign cost | **P2** | L5 |
| FR-MKT-038 | Channel effectiveness | Compare channels on reach, engagement, conversion and cost per acquisition | P2 | L5 |
| FR-MKT-039 | Lead generation reporting | Report leads generated, qualified and converted by campaign and source | P2 | L5 |
| FR-MKT-040 | Marketing dashboard | Present the marketing position — active campaigns, spend against budget, leads, attributed revenue, ROI | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No send capability** | M35 holds no provider credentials and has no direct delivery path. Every message is a request to M27. This is enforced by credential ownership, not policy |
| T-02 | **No list upload** | There is no interface, API or import that accepts an arbitrary recipient list. Audiences resolve to M33 segment identifiers |
| T-03 | **Post-suppression audience estimation** | Estimated reach is computed after consent, DND, fatigue and suppression evaluation, so approvers see the real number |
| T-04 | **Journey state machine per party** | Each party's position in each journey is explicit and queryable; conflicting journeys are resolved by priority before dispatch |
| T-05 | **Deterministic holdout assignment** | Holdout allocation is deterministic from a stable hash so a customer's holdout status is consistent across campaigns in an experiment |
| T-06 | **Attribution reproducibility** | The attribution model is versioned and its output reproducible from raw touchpoint and conversion data |
| T-07 | **Emergency stop propagation** | A campaign halt reaches M27 within 60 seconds and cancels queued but unsent messages |
| T-08 | **Capacity signal consumption** | Projected demand is compared against M02 capacity through an event projection, not a live query at activation |
| T-09 | **Content approval enforcement** | An unapproved or expired template cannot be used by a live campaign, enforced at request time |
| T-10 | **Bengali content rendering** | All content is validated for correct Bengali rendering and SMS segment cost across target channels before approval |
| T-11 | **Performance envelope** | Audience estimation ≤ 10 s for 250,000 parties · journey evaluation ≤ 5 min cycle · campaign dashboard ≤ 2 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M35 |
|---|---|---|
| **Marketing Head** | Runs campaigns with no measurement of effect | Plans against a calendar, measures incremental revenue, defends the budget with evidence |
| **Customer** | Receives ad hoc promotions, sometimes irrelevant, sometimes after opting out | Receives relevant, consented, appropriately timed offers, and can opt out once and be believed |
| **CCO** | Cannot generate demand for the new revenue streams | Has a mechanism to tell 250,000 customers that rental, refurbished devices and managed services exist |
| **Branch manager** | Discovers a campaign when customers arrive | Sees the campaign calendar and can staff against it |
| **Ops Director** | Absorbs demand spikes without warning | Capacity is checked before activation; demand is planned |
| **CFO** | Marketing spend is unmeasurable | Sees spend by campaign against attributed and incremental revenue |
| **Compliance officer** | Cannot be confident marketing honours opt-outs | Marketing structurally cannot send; suppression is enforced downstream |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Campaign ROI** | Measured attribution and incremental testing directing spend to what works | **> 4 : 1** |
| **AMC and RAMC growth** | Renewal, cross-sell and seasonal campaigns against the installed base | Supports **2× contract base** and the **BDT 72 lac/year** renewal benefit |
| **New revenue stream awareness** | Rental, refurbishment, data services and marketplace have no organic demand | **Precondition** for the combined **BDT 190 lac/year** from M13, M14 and M18 |
| **Seasonal demand capture** | Templated seasonal campaigns replacing annual improvisation | Captures predictable peaks rather than reacting to them |
| **Reactivation of dormant customers** | The installed base contains a large dormant population with known devices | Lower acquisition cost than any external channel |
| **Reduced wasted spend** | Holdout measurement distinguishes caused revenue from coincidental revenue | Typically reveals that a material share of attributed revenue is not incremental |
| **Referral amplification** | Campaigns that activate referral mechanics at the right moment | Supports **> 12% referral-attributed acquisition** |
| **Advertising revenue** | In-app and portal placements sold to brand partners and marketplace sellers | Contributes to the advertising and placement revenue stream |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Marketing becomes accountable** | Attribution and holdout testing change marketing from an expense to an investment with a measurable return |
| **Compliance by architecture** | A marketing function that structurally cannot bypass consent is a materially stronger control than one that promises not to |
| **The installed base becomes an asset** | 200,000+ registered devices with known age and service history is a demand-generation asset the Company currently does not use |
| **Demand becomes plannable** | Operations can staff against a campaign calendar rather than absorb surprises |
| **Brand consistency** | Approved, versioned, bilingual content replaces improvised messaging across 51+ branches |
| **Partner co-marketing becomes possible** | Brand partners will co-fund campaigns only where effect can be measured |

---

## 8. Lifecycle & State Models

### 8.1 Campaign

```
   +----------+
   |  DRAFT   |  objective, audience, offer, content, budget, schedule
   +----+-----+
        |
   +----v-------------------+
   | AUDIENCE ESTIMATED     |  post-suppression reach shown to approver
   +----+-------------------+
        |
   +----v-------------------+     capacity insufficient
   | CAPACITY CHECKED (M02) |------------------------> BLOCKED / RESCHEDULED
   +----+-------------------+
        |
   +----v-------------------+
   | PENDING APPROVAL       |  by value and audience size
   +----+-------------------+
        |
   +----v-------------------+
   |     APPROVED           |
   +----+-------------------+
        | scheduled activation time reached
   +----v-------------------+
   |      ACTIVE            |<-----+
   +----+-------------------+      |
        |                          | resumed
        +--> PAUSED ---------------+
        |
        +--> HALTED (emergency stop; queued messages cancelled within 60 s)
        |
        | scheduled deactivation, budget exhausted, or audience complete
   +----v-------------------+
   |     COMPLETED          |
   +----+-------------------+
        | attribution window elapses
   +----v-------------------+
   |     MEASURED           |  attributed revenue, incremental effect, ROI
   +------------------------+
```

### 8.2 Party in a Journey

```
   ELIGIBLE --> ENTERED --> STEP 1 --> WAIT --> STEP 2 --> ... --> COMPLETED
                   |           |                  |
                   |           |                  +--> BRANCHED (condition met)
                   |           |
                   |           +--> SUPPRESSED at this step
                   |                (consent, DND, quiet hours, fatigue)
                   |
                   +--> EXITED
                        reasons: converted · consent withdrawn · complaint raised
                                 · entered a higher-priority journey
                                 · exit criteria met · campaign halted
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-MKT-01 | **M35 has no send capability; every message is a request to M27** | **H** | CTO |
| BRU-MKT-02 | **Audiences are built only from governed M33 segments; manual list upload is not permitted** | **H** | CDO |
| BRU-MKT-03 | Estimated reach shown to an approver is the **post-suppression** figure | **H** | Marketing Head |
| BRU-MKT-04 | A campaign above the defined value or audience threshold requires approval before activation | **H** | Marketing Head |
| BRU-MKT-05 | **A campaign projecting demand beyond operational capacity is blocked or rescheduled** | **A** | Ops Director |
| BRU-MKT-06 | A customer cannot receive messages from two conflicting journeys; priority resolves the conflict | **H** | Marketing Head |
| BRU-MKT-07 | **Consent withdrawal exits the party from every active journey immediately** | **H** | CDO |
| BRU-MKT-08 | A party with an open complaint is suppressed from promotional campaigns until it is resolved | **C** | Customer Service Manager |
| BRU-MKT-09 | An unapproved or expired content template cannot be used by a live campaign | **H** | Marketing Head |
| BRU-MKT-10 | Every customer-facing asset exists in both Bengali and English before approval | **H** | Marketing Head |
| BRU-MKT-11 | A campaign cannot exceed its approved budget without re-approval | **H** | CFO |
| BRU-MKT-12 | The attribution model is versioned; changing it does not retrospectively restate closed campaigns | **H** | CFO |
| BRU-MKT-13 | Emergency stop halts all channels and cancels queued messages | **H** | Marketing Head |
| BRU-MKT-14 | Holdout groups are excluded from the campaign entirely, including from any manual follow-up | **H** | Marketing Head |

*Classification: **H** hard block · **A** approved override · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.campaign` | `fix_campaign` | A campaign | code, name, type, objective, programme_id, audience_def_id, offer_ref, channels, budget, activate_at, deactivate_at, state, approved_by, capacity_check_result |
| `fix.campaign.programme` | `fix_campaign_programme` | Campaign grouping | code, name, period, owner_id, budget |
| `fix.audience.definition` | `fix_audience_definition` | Audience composition | campaign_id, include_segments, exclude_segments, suppression_rules, holdout_pct, estimated_reach, estimated_at |
| `fix.audience.member` | `fix_audience_member` | Resolved membership | audience_id, party_id, state, holdout, suppressed_reason, evaluated_at |
| `fix.journey` | `fix_journey` | Journey definition | code, name, entry_criteria, steps_json, exit_criteria, priority, active |
| `fix.journey.instance` | `fix_journey_instance` | A party's position | journey_id, party_id, current_step, entered_at, last_step_at, state, exit_reason |
| `fix.journey.step.log` | `fix_journey_step_log` | Step execution | instance_id, step_code, executed_at, outcome, notification_intent_ref, suppressed_reason |
| `fix.content.asset` | `fix_content_asset` | Creative and copy | code, type, channel, language, body, variables, version, approved_by, approved_at, expires_at |
| `fix.campaign.offer` | `fix_campaign_offer` | Offer used | campaign_id, offer_type, m10_reference, value, terms_ref |
| `fix.ab.test` | `fix_ab_test` | Variant test | campaign_id, variable, variants_json, allocation, winner, significance, concluded_at |
| `fix.campaign.budget` | `fix_campaign_budget` | Budget and spend | campaign_id, planned, committed, actual_delivery_cost, actual_offer_cost, currency |
| `fix.touchpoint` | `fix_touchpoint` | A marketing contact | party_id, campaign_id, journey_instance_id, channel, occurred_at, engaged, engagement_type |
| `fix.attribution.model` | `fix_attribution_model` | Versioned model | code, method, lookback_window, weighting_json, version, effective_from |
| `fix.attribution.result` | `fix_attribution_result` | Attributed revenue | campaign_id, period, model_version, attributed_revenue, incremental_revenue, holdout_baseline, cost, roi |
| `fix.ad.placement` | `fix_ad_placement` | In-app and portal advertising | placement_code, surface, page_context, position, campaign_id, advertiser_party_id, impressions, clicks, active_from, active_to |
| `fix.campaign.calendar` | `fix_campaign_calendar` | Forward schedule | period, campaign_id, conflict_flags |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| **`fix.segment`, `fix.segment.membership`** | **M33** | **The only permitted audience source** |
| `fix.consent.record` | M33 | Relied upon; enforced by M27 |
| `fix.voucher.batch`, `fix.points.rule` | M10 | Offer mechanics |
| `fix.notification.intent` | M27 | Created by M35; owned by M27 |
| `fix.lead` | M07 | Generated by M35; owned by M07 |
| `fix.survey.response` | M34 | Promoter and detractor segments |
| `fix.asset` | M17 / M49 | Device age and type for targeting |
| `fix.contract` | M08 | Expiry-driven journey triggers |
| `fix.partner.profile` | M40 | Co-marketing partner |
| `fix.model` | M26 | Propensity and churn models |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-MKT-01 | Campaign submitted for approval | Resolve the audience, estimate post-suppression reach, run the capacity check, route for approval | Hold in draft; alert |
| AUT-MKT-02 | **Scheduled activation time reached** | Activate the campaign; begin journey entry evaluation | Alert Marketing Head; do not activate silently |
| AUT-MKT-03 | Scheduled deactivation reached, or budget exhausted, or audience complete | Deactivate; stop journey entry; allow in-flight journeys to complete or exit per configuration | — |
| AUT-MKT-04 | Journey entry criteria met | Enter the party, subject to conflict priority and suppression | Log as not entered with reason |
| AUT-MKT-05 | Journey step due | Raise a notification intent to M27; record the outcome including suppression | Record suppression; continue the journey |
| AUT-MKT-06 | **Consent withdrawn (event from M33)** | **Exit the party from every active journey immediately; suppress from all campaigns** | **Escalate — a failed exit is a regulatory incident** |
| AUT-MKT-07 | Complaint raised (event from M34) | Suppress the party from promotional campaigns until resolution | — |
| AUT-MKT-08 | Conversion detected | Exit the party from the journey; record the touchpoint chain for attribution | — |
| AUT-MKT-09 | Emergency stop invoked | Halt all channels within 60 seconds; cancel queued messages in M27 | Escalate to CTO |
| AUT-MKT-10 | A/B test reaches significance | Declare the winner; optionally shift remaining allocation | Continue to the planned end |
| AUT-MKT-11 | Attribution window elapses | Run attribution, compare against the holdout baseline, compute incremental revenue and ROI | Alert on calculation failure |
| AUT-MKT-12 | Campaign spend reaches 80% / 100% of budget | Notify the owner; at 100% pause pending re-approval | — |
| AUT-MKT-13 | Seasonal campaign template date approaches | Create the campaign from the template and route it for review | — |
| AUT-MKT-14 | Content asset approaching expiry | Notify the owner; block use after expiry | — |

---

## 12. Interfaces

### 12.1 Upstream — M35 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M33 Party Master** | **Segment definitions and membership — the only audience source**; consent state; consent withdrawal events | REST + event |
| M10 Loyalty | Offer mechanics — voucher batches, points multipliers, tier benefits | REST |
| M34 Experience | Promoter and detractor segments; complaint suppression signal | Event |
| M07 CRM | Unqualified leads for nurture; account context | Event |
| M17 Asset Registry | Device age, type and warranty status for targeting | REST |
| M08 Contract | Contract expiry for renewal journeys | Event |
| M02 Field Service | **Operational capacity for the pre-activation check** | Event projection |
| M26 AI/ML | Propensity, churn and next-best-offer models | REST with fallback |
| M40 Partner | Co-marketing partner relationships | REST |
| M27 Contact Centre | Delivery outcome and suppression reasons | Event |

### 12.2 Downstream — M35 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M27 Contact Centre** | **Notification intents and bulk send instructions with audience** | **Command** |
| M07 CRM | Campaign-generated and nurtured leads with source attribution | Event |
| M10 Loyalty | Voucher batch requests; points multiplier periods | Command |
| M53 / M54 | Marketing spend and attributed revenue | Warehouse extract |
| M25 Business Intelligence | Campaign, journey, touchpoint and attribution facts | Warehouse extract |
| M12 Marketplace | Advertising placement inventory and performance | REST |
| M40 Partner | Co-marketing performance for partner reporting | Event |
| P01, P04 | In-app and portal advertising placements | REST |
| Corporate website | Tracked campaign links and landing page parameters | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `campaign.approved` | campaign, audience size, budget, schedule | M02, M25 |
| `campaign.activated` | campaign, channels, offer | M27, M10, M25 |
| `campaign.halted` | campaign, reason | M27 |
| `campaign.completed` | campaign, reach, engagement, spend | M25 |
| `journey.entered` | journey, party, entry trigger | M25 |
| `journey.exited` | journey, party, exit reason | M25 |
| `touchpoint.recorded` | party, campaign, channel, engaged | M25, attribution |
| `lead.generated` | lead, campaign, source | **M07** |
| `campaign.attributed` | campaign, attributed revenue, incremental, ROI | M54, M25 |
| `ab_test.concluded` | test, winner, significance | M25 |
| `advertising.impression_recorded` | placement, advertiser, count | M12, M53 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/campaigns` | GET / POST | Campaign management | P03 |
| `/api/v1/campaigns/{id}/estimate` | POST | Post-suppression audience estimate | P03 |
| `/api/v1/campaigns/{id}/approve` | POST | Approve for activation | P03 |
| `/api/v1/campaigns/{id}/halt` | POST | Emergency stop | P03 |
| `/api/v1/journeys` | GET / POST | Journey design | P03 |
| `/api/v1/journeys/{id}/instances` | GET | Party positions and progression | P03 |
| `/api/v1/content` | GET / POST | Content library and approval | P03 |
| `/api/v1/attribution/{campaign}` | GET | Attribution and incremental result | P03, P06 |
| `/api/v1/marketing/dashboard` | GET | Marketing position | P03, P06 |
| `/api/v1/ad-placements` | GET / POST | Advertising placement management | P03, M12 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R23 Marketing Manager | C R U D A | All campaigns, journeys, content, budget |
| R50 Marketing Executive | C R U | Campaign build and content, within approval limits |
| R04 Chief Commercial Officer | R A | Approval above the value threshold |
| R26 Finance Manager | R A | Budget approval and spend |
| R05 Operations Director | R A | **Capacity check override authority** |
| **R40 Chief Data Officer** | R A | Audience governance, suppression evidence, consent compliance |
| R22 Account Manager (Corporate) | R | Campaigns affecting own accounts |
| R06 Branch Manager | R | Campaign calendar affecting own branch |
| R32 Quality Manager / ISO Coordinator | R | Complaint-driven suppression |
| R01 Chief Executive Officer | R | Marketing performance and ROI |

**Field-level restrictions.** Individual party membership of an audience is visible to R24 and
R40 only; other roles see counts. Attribution model configuration is restricted to R24, R26
and R02.

**Segregation of duties.** The person who builds a campaign cannot approve it above the
threshold (SOD-23). Budget approval is separated from campaign ownership (SOD-24).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Marketing dashboard | Marketing Head, CCO | Daily | Active campaigns, reach, engagement, spend against budget, leads, attributed revenue |
| Campaign calendar | Marketing Head, Ops Director, branch managers | Weekly | Forward schedule with conflicts and capacity flags |
| **Campaign performance** | **Marketing Head, CFO** | **Per campaign** | Reach, engagement, conversion, attributed revenue, **incremental revenue against holdout**, cost, ROI |
| Journey performance | Marketing Head | Weekly | Entry, step progression, drop-off, conversion by journey |
| **Suppression analysis** | **Marketing Head, CDO** | **Weekly** | Audience shrinkage by suppression reason — consent, DND, fatigue, complaint |
| Channel effectiveness | Marketing Head, CFO | Monthly | Reach, engagement, conversion and cost per acquisition by channel |
| Lead generation | Marketing Head, CCO | Weekly | Leads by campaign and source; qualification and conversion rate |
| Budget position | Marketing Head, CFO | Weekly | Planned, committed and actual by campaign and programme |
| A/B test results | Marketing Head | Per test | Variant performance, significance, winner |
| Content usage | Marketing Head | Monthly | Assets used, performance by asset, expiring assets |
| Advertising performance | Marketing Head, M12 | Monthly | Impressions, clicks, revenue by placement and advertiser |
| Seasonal performance | Marketing Head, CEO | Annually | Year-on-year comparison of recurring seasonal campaigns |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-200 | **Campaign ROI** | unmeasured | 3 : 1 | **> 4 : 1** |
| KPI-201 | **Incremental revenue as a share of attributed revenue** | unmeasured | baselined | **> 55%** |
| KPI-202 | Lead generation from campaigns | unmeasured | baselined | **+40%** |
| KPI-203 | Campaign-attributed AMC/RAMC sales | unmeasured | baselined | **+35%** |
| KPI-204 | Dormant customer reactivation rate | 0% | 6% | **> 12%** |
| KPI-205 | Email and message engagement rate | unmeasured | baselined | **+25%** |
| KPI-206 | **Campaigns activated without a capacity check** | n/a | **0** | **0** |
| KPI-207 | **Messages sent to withdrawn-consent parties** | unknown | **0** | **0** |
| KPI-208 | Journey conflict incidents | n/a | **0** | **0** |
| KPI-209 | Campaign spend within approved budget | unmeasured | 95% | **100%** |
| KPI-210 | Content assets bilingual at approval | unmeasured | **100%** | **100%** |
| KPI-211 | Advertising placement revenue | 0 | baselined | Target set at launch |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `mass_mailing`, `marketing_automation`, `utm` | 28% |
| L5 | `cd_campaign`, `cd_journey_orchestration`, `cd_attribution`, `cd_content` | 72% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 4 of 4 identifiers below are claimed by another module: **CD-062** also claimed by M13; **CD-063** also claimed by M14; **CD-064** also claimed by M14; **CD-065** also claimed by M14. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-062 | `cd_campaign` — campaign, approval, scheduling, capacity check, budget, emergency stop | Odoo module | 5 PW |
| CD-063 | **`cd_journey_orchestration`** — journey design, instance state, conflict priority, exit handling | Odoo module + service | **5 PW** |
| CD-064 | **`cd_attribution`** — touchpoint capture, multi-touch model, holdout, incremental measurement | Service | **4 PW** |
| CD-065 | `cd_content` — content library, versioning, approval, bilingual validation, ad placements | Odoo module | 3 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M33 Party Master** | **Blocking** — segments are the only audience source; consent is the basis for sending |
| **M27 Contact Centre** | **Blocking** — M35 cannot send; M27 delivers everything |
| **M10 Loyalty** | **Blocking** — campaigns need offer mechanics |
| M07 CRM | Lead handoff and nurture return |
| M34 Experience | Promoter and detractor segments; complaint suppression |
| M02 Field Service | Capacity signal for the pre-activation check |
| M26 AI/ML | Propensity models — advisory only; M35 functions without them |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing campaign content and creative | Unknown | `fix.content.asset` | W5 |
| Historical campaign performance | **None exists** in structured form | — | — |
| Seasonal campaign definitions | **Authored, not migrated** — built from known seasonal patterns | `fix.campaign` templates | W5 |

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **M35 cannot send a message directly; no provider credentials exist in the module** | **Code review and credential audit** |
| AC-02 | **No interface, API or import accepts an arbitrary recipient list** | **Negative test through UI and API** |
| AC-03 | Estimated reach presented to an approver is the post-suppression figure | Verification against actual send volume on three campaigns |
| AC-04 | A campaign projecting demand beyond capacity is blocked or requires override | Scripted test with a constrained capacity signal |
| AC-05 | **Consent withdrawal exits the party from every active journey within 60 seconds** | **Timed test across three concurrent journeys** |
| AC-06 | A party cannot receive messages from two conflicting journeys | Scripted conflict test |
| AC-07 | Emergency stop halts all channels and cancels queued messages within 60 seconds | Timed test |
| AC-08 | An unapproved or expired template cannot be used by a live campaign | Negative test |
| AC-09 | Every customer-facing asset exists in Bengali and English before approval | Negative test |
| AC-10 | Holdout allocation is deterministic and holdout parties receive nothing from the campaign | Verification on a 10,000-party campaign |
| AC-11 | **Attribution output is reproducible from raw touchpoint and conversion data** | **Recalculation audit** |
| AC-12 | Incremental revenue is measured against the holdout baseline and reported separately from attributed revenue | Report review by CFO |
| AC-13 | Campaign spend cannot exceed the approved budget without re-approval | Negative test |
| AC-14 | Audience estimation completes in ≤ 10 seconds for 250,000 parties | Load test |
| AC-15 | Marketing Head, CDO and CFO sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Does a marketing function exist today with the capacity to run a campaign calendar?** As with M07, this may be an organisational change rather than a system one. | CEO / CCO | **W5 minus 3 months** |
| Q-02 | What attribution model is adopted — last touch, linear, time decay or position-based? | Marketing Head / CFO | **W5 build** |
| Q-03 | What is the attribution lookback window by campaign type? | Marketing Head | W5 build |
| Q-04 | What holdout percentage, and does it apply to all campaigns or only above a size threshold? | Marketing Head / CFO | W5 build |
| Q-05 | What is the campaign approval matrix by value and audience size? | CCO / CFO | W5 build |
| Q-06 | Who has authority to override a capacity-check block — Ops Director alone, or jointly with CCO? | Ops Director / CCO | W5 build |
| Q-07 | Is advertising placement sold to third parties at launch, or reserved for internal campaigns until M12 goes live? | CCO | W5 design |
| Q-08 | What is the fatigue cap for promotional contact, and how does it interact with M34's survey fatigue cap? | Marketing Head / Customer Service Manager | **W5 build** |

**Q-08 matters more than it appears.** Survey fatigue and promotional fatigue draw on the same
customer patience. The two caps must be designed together, not separately.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §5 (M35/M10 and M35/M27 boundaries), §6 (data ownership rule) ·
`M33_Customer_and_Party_Master_Management.md` ·
`M27_Omnichannel_Contact_Centre_and_Communications.md` ·
`M10_Loyalty_Membership_and_Rewards.md` · `M34_Customer_Experience_Feedback_and_Complaints.md` ·
`M07_CRM_Sales_Pipeline_and_Account_Management.md` ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-CRM-010, BO-08 ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Campaigns (double points,
partnered brand campaigns, special day campaigns, scheduled auto on/off), §Advertising
(in-app ad section, check-out page), §Personalisation ·
`1000FiX_Services_Company_Profile.md` §FiXnChill Campaign, §Blog & Articles ·
`1000_fix_corporate_website/` — service, city and brand landing page taxonomy

**External benchmark and regulation** *(verified 2026-08-12)*
Marketing automation practice 2026 — predictive segmentation, next-best-action, **autonomous
journey orchestration**, multi-touch nurture adapting to engagement, dynamic real-time
audiences, and **attribution models allocating credit across the complete customer journey**;
the market distinction between platforms with genuine profile stores and those with a list
database behind a segmentation interface · Customer journey orchestration — unified touchpoints
in a single orchestration layer with centralised attribution · **Consent-first orchestration** —
privacy regulation makes consent-aware suppression essential ·
**BTRC Do Not Disturb service and the prohibition on promotional SMS from midnight to dawn**
(enforced in M27) · **Bangladesh Personal Data Protection Act 2026** — clear, explicit,
specific and freely given consent for marketing, with simple immediate withdrawal ·
Odoo `marketing_automation` and `mass_mailing`

---

*Module M35 · Category B · 1000FiX ERP System v2.0 · CONFIDENTIAL*
