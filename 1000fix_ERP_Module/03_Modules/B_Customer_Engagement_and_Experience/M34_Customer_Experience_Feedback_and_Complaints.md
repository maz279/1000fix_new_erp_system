---
id: FIX-ERP2-M34
module_id: M34
module_code: CXM
module_name: Customer Experience, Feedback & Complaints
category: B — Customer Engagement & Experience
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Customer Service Manager
system_owner: Commercial Squad
priority: P1
wave: W4
regulatory_verified: 2026-08-12
---

# M34 — Customer Experience, Feedback & Complaints
### Category B · Code `CXM` · ★ New module in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M34 |
| **Module code** | `CXM` |
| **Category** | B — Customer Engagement & Experience |
| **Status** | ★ **New** — split from M07 CRM after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | W4 (Months 14–18) |
| **Business owner** | Customer Service Manager |
| **System owner** | Commercial Squad |
| **Delivery layers** | L2 (OCA `helpdesk_mgmt_rating`, `survey`) + L5 (custom) |
| **Custom modules** | `cd_voc`, `cd_complaint`, `cd_journey`, `cd_closed_loop` |
| **Requirement range** | FR-CXM-001 … FR-CXM-042 |
| **Requirement count** | 42 |
| **Effort estimate** | 17 person-weeks |
| **Depends on** | M33 Party Master · M27 Contact Centre · M01 Service Order · M23 Quality · M29 Identity |
| **Depended on by** | M07, M08, M10, M12, M23, M25, M26, M35, M57 |

---

## 2. Purpose

M34 measures **how the customer felt about what happened**, and does something about it when
the answer is bad.

It owns satisfaction measurement — CSAT, NPS and CES — the customer-facing complaint process,
review and rating capture, journey measurement, and the **closed feedback loop** that turns a
detractor's response into a contact, a resolution and a changed outcome.

### Why It Exists

The Company's baseline CSAT is 3.8 out of 5 and the target is 4.7. That is a substantial
change, and it will not come from measuring more. It comes from **acting on what is measured**
— which requires a mechanism that routes a poor score to a person with authority to fix it,
within hours, and tracks whether they did.

Research on this is unambiguous: **organisations that close the loop see roughly a threefold
increase in promoters on the next survey**, and the three most reliable drivers of NPS are
first-contact resolution, reduced customer effort, and **closing the loop with detractors
directly**.

There is a second reason. The v1.0 plan placed complaints inside the Quality module. That
conflates two different things: the customer's experience of raising a complaint, and the
organisation's internal investigation of what went wrong. The customer needs acknowledgement,
updates and a resolution. Quality needs root cause, corrective action and effectiveness
verification. Running both from one object serves neither.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §6.3 | Baseline CSAT 3.8/5 against an industry benchmark of 4.5–4.8 |
| ERP BRD BO-05 | Improve customer satisfaction; CSAT to 4.7/5 |
| ERP BRD BR-CRM-005 | "Send automated post-service satisfaction surveys (CSAT + NPS) via SMS/WhatsApp" |
| ERP BRD BR-CRM-008 | "Complaint management with root cause classification and resolution tracking" |
| ERP BRD BR-QMS-002 | Customer complaints with root cause analysis and CAPA tracking — **the internal half, owned by M23** |
| ERP BRD §7.3 A13 | CSAT survey auto-sent after service completion |
| Service App SOW §Ratings | "Different rating parameters — overall service rating, rating on timeliness, rating on professionalism, rating on behaviour" |
| Service App SOW §Customer Support | "At the end of the chat, the customer will be able to rate the conversation" |
| Company Profile §Quality Assurance | ISO 9001:2015 commitment to customer satisfaction focus |
| **ISO 10002** *(verified 2026-08-12)* | Guidelines for complaints handling: customer-focused environment open to feedback, **prompt acknowledgement, transparent status updates**, structured root cause analysis, documented corrective actions, top-management commitment, and analysis of complaints to improve quality |
| **Closed-loop practice** *(verified 2026-08-12)* | Closing the loop produces ~3× increase in promoters on the next survey; FCR, customer effort and direct detractor follow-up are the strongest NPS drivers |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Survey design, distribution, throttling and response capture |
| 2 | CSAT, NPS and CES measurement and scoring |
| 3 | Multi-parameter service ratings — overall, timeliness, professionalism, behaviour |
| 4 | Conversation and interaction rating |
| 5 | **Closed feedback loop: detractor routing, contact, resolution, verification** |
| 6 | Customer-facing complaint intake, acknowledgement, updates and resolution |
| 7 | Complaint categorisation, severity, SLA and escalation |
| 8 | Compensation and goodwill within defined authority |
| 9 | Journey definition and measurement across touchpoints |
| 10 | Customer effort measurement at defined moments |
| 11 | Review and testimonial capture and publication consent |
| 12 | Voice-of-customer analysis: themes, drivers, verbatim analysis |
| 13 | Experience reporting by branch, technician, service type and channel |
| 14 | Experience signal supply to CRM, HR incentives, Quality and Marketing |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Internal non-conformance, root cause investigation, CAPA, effectiveness verification** | **M23** | M34 owns the customer's experience of the complaint; M23 owns the organisation's investigation of the failure |
| Survey and notification **delivery** | **M27** | M34 designs and triggers; M27 sends, applying consent and quiet hours |
| Party identity and consent | **M33** | Master data |
| Conversation history and transcripts | **M27** | M34 rates the conversation; M27 owns it |
| Service order state and SLA | **M01** | M34 measures the outcome; M01 owns the process |
| **Marketplace seller reviews and ratings** | **M12** | Reviews of a third-party seller are a marketplace trust mechanism, not 1000FiX experience measurement |
| Technician incentive calculation | **M57** | M34 supplies the CSAT input; M57 turns it into pay |
| Sentiment model training | **M26** | M34 consumes; M26 governs |
| Marketing campaign response measurement | **M35** | Campaign metrics are marketing measurement, not experience |
| MSP client satisfaction under contract | **M05** | Contractual client satisfaction reporting sits with the service |
| Employee satisfaction | **M21** | Different population, different instrument |

### 3.3 Shared Concepts

| Concept | M34's Role | Owning Module |
|---|---|---|
| Complaint | **Owns the customer-facing case** | M34 |
| Non-conformance | Raises to | M23 |
| Survey | **Owns design and analysis**; M27 delivers | M34 / M27 |
| Rating | **Owns** | M34 |
| Sentiment | Consumes from M32 and M26 | M26 |
| Customer health | Contributes satisfaction inputs | M07 |
| Review | **Owns for 1000FiX service**; M12 owns seller reviews | M34 / M12 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Voice-of-customer platforms** | The six benchmarks that matter: **NPS, CSAT, CES, response rate, coverage and closing-the-loop rate** | **All six as governed metrics** — particularly *coverage* and *closing-the-loop rate*, which most implementations omit | Enterprise VoC suite licensing |
| **Closed-loop practice** | Companies that close the loop see **~3× increase in promoters on the next survey**; the three most reliable NPS drivers are **first-contact resolution, reduced customer effort, and closing the loop with detractors directly** | **Closed loop as the module's central mechanism**, not a reporting feature | Measurement-only VoC, which changes nothing |
| **ISO 10002** | Complaints handling: customer-focused environment, **prompt acknowledgement, transparent status updates**, structured root cause analysis, documented corrective action, top-management commitment, analysis to improve quality | **The full complaints framework**, with the customer-facing half here and root cause in M23 | Treating ISO 10002 as documentation rather than process |
| **CX metric practice** | NPS for relationship, CSAT for transaction, CES for effort — each answering a different question | **All three, applied at the right moment**, rather than one metric everywhere | Single-metric simplification |
| **Odoo `survey` + OCA `helpdesk_mgmt_rating`** | Survey engine and post-ticket rating | The L2 substrate | Odoo's survey-only model — no closed loop |

**Design position.** Five deliberate differences.

First, **the closed loop is the module**. Measurement without follow-up is theatre. Every
detractor response creates a case with an owner, a clock and a verified outcome. If the loop
is not closed, the score is not counted as resolved.

Second, **the complaint is one object with two views**. The customer sees acknowledgement,
status and resolution. Quality sees root cause, corrective action and effectiveness. They are
the same incident, and neither team should have to ask the other what happened.

Third, **survey fatigue is managed as a first-class constraint**. At 250,000 monthly
interactions, surveying everyone would train customers to ignore surveys. Sampling, throttling
and per-customer frequency caps are enforced in the design, not left to campaign discipline.

Fourth, **effort is measured, not assumed**. The most reliable NPS driver after FCR is reduced
customer effort. CES is measured at the moments where effort is highest — repeat contact,
device collection, complaint resolution — rather than everywhere.

Fifth, **CSAT feeds technician pay, so its integrity is a control matter**. If satisfaction
scores influence incentives, the survey mechanism becomes a target for manipulation. Response
provenance, sampling independence and anomaly detection are built in.

---

## 5. Functional Areas & Features

### 5.1 Survey Design & Distribution

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CXM-001 | Survey design | Design surveys with question types, branching, bilingual content and mobile-first presentation | P1 | L2 |
| FR-CXM-002 | Trigger definition | Define triggers by event — service completion, device collection, conversation close, complaint resolution, contract renewal, membership anniversary | P1 | L5 |
| FR-CXM-003 | Timing control | Set the delay between the triggering event and the survey, per survey type | P1 | L5 |
| FR-CXM-004 | **Sampling** | Sample rather than census where volume warrants it, with statistically valid selection by branch, technician, service type and channel | **P1** | L5 |
| FR-CXM-005 | **Fatigue control** | Enforce a maximum survey frequency per customer per period across all survey types | **P1** | L5 |
| FR-CXM-006 | Multi-channel distribution | Distribute via SMS, WhatsApp, email, in-app and post-call IVR, through M27 with consent applied | P1 | L5 |
| FR-CXM-007 | Response capture | Capture responses with minimal friction — single-tap where possible, no login required | **P1** | L5 |
| FR-CXM-008 | Partial response | Retain and use partial responses rather than discarding them | P2 | L5 |
| FR-CXM-009 | Response provenance | Record how, when and from what device each response arrived, to support integrity checks | **P1** | L5 |
| FR-CXM-010 | Reminder | Send one reminder for unanswered surveys, within fatigue limits | P2 | L5 |

### 5.2 Measurement

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CXM-011 | **CSAT** | Measure transactional satisfaction on a defined scale, at defined moments | **P1** | L5 |
| FR-CXM-012 | **NPS** | Measure relationship likelihood-to-recommend, with promoter, passive and detractor classification | **P1** | L5 |
| FR-CXM-013 | **CES** | Measure customer effort at high-effort moments — repeat contact, collection, complaint resolution | P1 | L5 |
| FR-CXM-014 | Multi-parameter service rating | Capture overall, timeliness, professionalism and behaviour ratings separately, per the SOW | P1 | L5 |
| FR-CXM-015 | Conversation rating | Capture a rating at the close of any conversation, per the SOW | P1 | L5 |
| FR-CXM-016 | Score attribution | Attribute every score to the branch, technician, agent, service type, channel and business line involved | **P1** | L5 |
| FR-CXM-017 | **Response rate and coverage** | Measure response rate and the proportion of eligible interactions covered by a survey | **P1** | L5 |
| FR-CXM-018 | Benchmarking | Compare scores across branches, technicians, service types and periods, with statistical significance indicated | P2 | L5 |
| FR-CXM-019 | **Score integrity** | Detect anomalous response patterns indicating manipulation — clustering, timing, device reuse, unusual distributions | **P1** | L5 |

### 5.3 Closed Feedback Loop

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CXM-020 | **Detractor detection** | Identify detractor and low-CSAT responses immediately on receipt | **P0** | L5 |
| FR-CXM-021 | **Loop case creation** | Create a follow-up case automatically with an owner, a contact deadline and a resolution target | **P0** | L5 |
| FR-CXM-022 | **Contact deadline** | Require first contact with a detractor within a defined window — target 24 hours | **P1** | L5 |
| FR-CXM-023 | Resolution recording | Record what was done, what the customer said, and whether they are satisfied with the outcome | P1 | L5 |
| FR-CXM-024 | **Loop closure verification** | Close the loop only on confirmed customer acknowledgement, not on internal action alone | **P1** | L5 |
| FR-CXM-025 | Escalation | Escalate unclosed loops by age and by severity through branch manager to operations director | P1 | L5 |
| FR-CXM-026 | **Closing-the-loop rate** | Measure the proportion of detractor responses closed within target, as a governed KPI | **P1** | L5 |
| FR-CXM-027 | Promoter follow-up | Invite promoters to leave a review or a referral, subject to consent and fatigue limits | P2 | L5 |

### 5.4 Complaint Management — Customer-Facing

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CXM-028 | Multi-channel intake | Accept complaints from any channel — portal, app, contact centre, counter, assistant, survey, social, email, regulator referral | P1 | L5 |
| FR-CXM-029 | **Prompt acknowledgement** | Acknowledge every complaint immediately with a reference number and expected timescale, per ISO 10002 | **P1** | L5 |
| FR-CXM-030 | Categorisation | Categorise by type, service line, severity and impact, using a maintained taxonomy | P1 | L5 |
| FR-CXM-031 | Severity and SLA | Apply a resolution SLA by severity and customer tier, with escalation on risk | P1 | L5 |
| FR-CXM-032 | Ownership | Assign a named owner accountable for resolution and for communicating with the customer | P1 | L5 |
| FR-CXM-033 | **Transparent status updates** | Keep the customer informed at defined points, per ISO 10002, without the customer having to chase | **P1** | L5 |
| FR-CXM-034 | Investigation linkage | Raise a non-conformance to M23 and track its progress without duplicating it | **P1** | L5 |
| FR-CXM-035 | Resolution and remedy | Record the resolution, any remedy offered, and the customer's acceptance | P1 | L5 |
| FR-CXM-036 | Compensation authority | Apply a defined authority matrix for goodwill, credit, free service and refund, with approval above thresholds | P1 | L5 |
| FR-CXM-037 | Reopening | Reopen a complaint if the customer is dissatisfied with the resolution, with escalation | P1 | L5 |
| FR-CXM-038 | Regulatory and external complaints | Handle complaints escalated to a regulator, consumer body or brand partner with defined handling and reporting | P2 | L5 |

### 5.5 Journey, Reviews & Voice of Customer

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CXM-039 | Journey definition | Define customer journeys with stages and touchpoints, and measure experience at each | P2 | L5 |
| FR-CXM-040 | Review capture and publication | Capture reviews, moderate them, obtain publication consent, and publish to the website with reply capability | P2 | L5 |
| FR-CXM-041 | **Verbatim analysis** | Analyse free-text feedback in Bengali and English for themes, drivers and emerging issues, using models from M26 | P2 | L5 |
| FR-CXM-042 | Driver analysis | Identify which operational measures most strongly correlate with satisfaction, to direct improvement effort | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Fatigue enforcement at dispatch** | The frequency cap is evaluated at send time in M27, not at survey design time, so it cannot be bypassed by launching multiple surveys |
| T-02 | **Immediate detractor detection** | Response processing is event-driven; a detractor response creates a loop case within 60 seconds of receipt, not on a nightly batch |
| T-03 | **Attribution integrity** | Every score is attributed at capture from the source transaction, never inferred later |
| T-04 | **Anomaly detection on responses** | Statistical monitoring for clustering, timing patterns, device reuse and distribution shifts, given that CSAT influences pay |
| T-05 | **Frictionless response capture** | Single-tap response from SMS and WhatsApp with no authentication; tokenised links that expire |
| T-06 | **One complaint, two views** | The complaint and the M23 non-conformance are linked records, never duplicated; each side sees the other's status |
| T-07 | **Bengali verbatim processing** | Theme extraction operates on Bengali, romanised Bengali and English text |
| T-08 | **Sampling reproducibility** | Sample selection is deterministic and auditable, so a branch cannot claim it was over-sampled |
| T-09 | **Consent evaluation** | Every survey dispatch evaluates consent through M33 via M27 |
| T-10 | **Score computation transparency** | NPS, CSAT and CES calculations are documented and reproducible from raw responses |
| T-11 | **Performance envelope** | Response capture ≤ 300 ms · experience dashboard ≤ 2 s · loop case creation ≤ 60 s from response |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M34 |
|---|---|---|
| **Customer** | Complains and hears nothing; is never asked what they thought | Acknowledged immediately, updated without chasing, and contacted when they score poorly |
| **Branch manager** | Learns about dissatisfaction from a complaint that reached head office | Sees their branch's scores daily and owns the loop cases arising from them |
| **Technician** | Judged on impression | Sees their own CSAT, timeliness, professionalism and behaviour scores |
| **Customer Service Manager** | Cannot demonstrate whether service is improving | Has CSAT, NPS, CES, response rate, coverage and closing-the-loop rate |
| **Quality Manager** | Investigates complaints without knowing the customer's experience of them | Receives structured non-conformances with full customer context |
| **CCO** | Cannot tell which accounts are unhappy before they leave | Satisfaction feeds account health in M07 |
| **HR / payroll** | Cannot pay a satisfaction-linked incentive defensibly | Has attributed, integrity-checked CSAT per technician |
| **CEO** | Has an anecdotal view of customer sentiment | Has a measured, trended, decomposable view |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **CSAT improvement** | Measurement plus closed loop, targeting the strongest drivers — FCR, effort and detractor follow-up | **3.8 → 4.7 out of 5** |
| **Promoter growth** | Closing the loop produces approximately a **threefold increase in promoters** on the next survey | Direct contribution to NPS above 55 |
| **Churn reduction** | Detractors contacted and resolved within 24 hours are materially less likely to leave | Contributes to **churn 15% → 8%**, worth **BDT 78 lac/year** |
| **Complaint resolution speed** | Owned cases with SLA and escalation | **> 95% resolved within SLA** |
| **Referral and review generation** | Promoters invited to review and refer at the moment of satisfaction | Feeds the **> 12% referral-attributed acquisition** target |
| **Defensible technician incentives** | Attributed, integrity-checked CSAT | Enables performance-linked pay without dispute — a precondition for the M02 productivity gain |
| **Targeted improvement investment** | Driver analysis shows which operational measures actually move satisfaction | Prevents spending on improvements that do not matter to customers |
| **ISO 9001 evidence** | Clause 9.1.2 requires monitoring customer perception | Direct evidence for surveillance audit |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The customer is heard** | An acknowledged complaint with visible progress is a materially different experience from silence, even before it is resolved |
| **Dissatisfaction becomes visible early** | Today the Company learns about problems when customers leave; measurement moves that forward by months |
| **Improvement becomes evidence-based** | Driver analysis replaces opinion about what customers care about |
| **Fairness in performance management** | Technicians judged on attributed scores rather than on who complained loudest |
| **ISO 10002 alignment** | The complaints framework is a recognised standard, useful in corporate tenders |
| **A conscience for the operation** | A visible detractor queue creates organisational pressure that process metrics alone do not |

---

## 8. Lifecycle & State Models

### 8.1 Survey Response and Closed Loop

```
   TRIGGER EVENT (service completed, device collected, conversation closed, complaint resolved)
        |
   +----v---------------+     fatigue cap reached, or not sampled, or no consent
   | ELIGIBILITY CHECK  |------------------------------------> NOT SURVEYED (logged)
   +----+---------------+
        |
   +----v---------------+
   | SURVEY SENT        |  via M27, consent and quiet hours applied
   +----+---------------+
        |
        +-------------------------------+
        |                               |
   +----v---------+              +------v-------+
   | RESPONDED    |              | NO RESPONSE  |--> ONE REMINDER --> CLOSED UNANSWERED
   +----+---------+              +--------------+
        |
   +----v---------------+
   | SCORED + ATTRIBUTED|  branch, technician, agent, service type, channel
   +----+---------------+
        |
        +------------------+------------------+
        |                  |                  |
   PROMOTER           PASSIVE            DETRACTOR / LOW CSAT
        |                  |                  |
   +----v----------+       |         +--------v-----------+
   | REVIEW /      |       |         | LOOP CASE CREATED  |  owner + 24h contact target
   | REFERRAL      |       |         +--------+-----------+
   | INVITE        |       |                  |
   +---------------+       |         +--------v-----------+
                           |         | CONTACTED          |
                           |         +--------+-----------+
                           |                  |
                           |         +--------v-----------+
                           |         | ACTION TAKEN       |--> non-conformance to M23
                           |         +--------+-----------+     if a process failure
                           |                  |
                           |         +--------v-----------+
                           |         | CUSTOMER CONFIRMS  |  <- loop closes only here
                           |         +--------+-----------+
                           |                  |
                           |         +--------v-----------+
                           +-------->|   LOOP CLOSED      |
                                     +--------------------+

   ESCALATED -- loop not closed within target; branch manager, then operations director
```

### 8.2 Complaint — Customer-Facing View

```
   +-------------+
   |  RECEIVED   |  any channel
   +------+------+
          | immediate acknowledgement with reference and timescale (ISO 10002)
   +------v---------+
   | ACKNOWLEDGED   |
   +------+---------+
          | categorised, severity set, SLA applied, owner assigned
   +------v---------+
   | UNDER REVIEW   |<-----------------------------+
   +------+---------+                              |
          |                                        |
          | investigation raised to M23 where a process failure is indicated
          |                                        |
   +------v---------+                              |
   | ACTION TAKEN   |                              |
   +------+---------+                              |
          |                                        |
   +------v---------+                              |
   | RESOLVED       |  remedy offered and recorded |
   +------+---------+                              |
          |                                        |
   +------v---------+   customer dissatisfied      |
   | CUSTOMER       |------------------------------+  REOPENED (escalated)
   | CONFIRMS       |
   +------+---------+
          |
   +------v---------+
   |    CLOSED      |
   +----------------+

   ESCALATED EXTERNAL -- regulator, consumer body or brand partner involved
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-CXM-01 | **Every complaint is acknowledged immediately with a reference and an expected timescale** | **H** | Customer Service Manager |
| BRU-CXM-02 | Every complaint has a named owner at all times | **H** | Customer Service Manager |
| BRU-CXM-03 | **A detractor or low-CSAT response creates a loop case automatically; it cannot be dismissed without contact** | **H** | Customer Service Manager |
| BRU-CXM-04 | **A loop case closes only on confirmed customer acknowledgement, never on internal action alone** | **H** | Customer Service Manager |
| BRU-CXM-05 | First contact with a detractor occurs within the defined window; breach escalates automatically | **H** | Ops Director |
| BRU-CXM-06 | A complaint indicating a process failure raises a non-conformance to M23 | **H** | Quality Manager |
| BRU-CXM-07 | The customer is informed of progress at defined points without having to chase | **H** | Customer Service Manager |
| BRU-CXM-08 | Compensation above the defined authority requires approval; every remedy is recorded | **A** | CCO |
| BRU-CXM-09 | **Survey frequency per customer is capped across all survey types; the cap is enforced at dispatch** | **H** | Customer Service Manager |
| BRU-CXM-10 | Every score is attributed at capture to the branch, technician, agent, service type and channel | **H** | Customer Service Manager |
| BRU-CXM-11 | **Scores used in incentive calculation are subject to anomaly detection; suspected manipulation is investigated before payment** | **H** | HR Director / CCO |
| BRU-CXM-12 | A reopened complaint escalates one level automatically | **C** | Customer Service Manager |
| BRU-CXM-13 | Reviews are published only with the customer's explicit consent | **H** | CDO |
| BRU-CXM-14 | Survey dispatch evaluates consent through M33 | **H** | CDO |
| BRU-CXM-15 | Response provenance is recorded for every response | **H** | Customer Service Manager |

*Classification: **H** hard block · **A** approved override · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.survey.definition` | `fix_survey_definition` | Survey design | code, name, type (CSAT/NPS/CES), questions_json, language_variants, active, version |
| `fix.survey.trigger` | `fix_survey_trigger` | When to survey | survey_id, trigger_event, delay_minutes, sampling_rate, eligibility_criteria |
| `fix.survey.dispatch` | `fix_survey_dispatch` | A survey sent | survey_id, party_id, trigger_ref, channel, sent_at, token, expires_at, reminded_at, state |
| `fix.survey.response` | `fix_survey_response` | A response received | dispatch_id, party_id, responded_at, answers_json, score, score_type, partial, provenance_json |
| `fix.score.attribution` | `fix_score_attribution` | Who and what the score relates to | response_id, branch_id, technician_id, agent_id, service_type, business_line, channel, source_ref |
| `fix.loop.case` | `fix_loop_case` | Closed-loop follow-up | response_id, party_id, severity, owner_id, created_at, contact_due, contacted_at, action_taken, customer_confirmed_at, state, escalation_level |
| `fix.complaint` | `fix_complaint` | Customer-facing complaint | reference, party_id, source_channel, category, sub_category, severity, description, owner_id, received_at, acknowledged_at, sla_due, resolved_at, closed_at, state, nonconformance_ref |
| `fix.complaint.update` | `fix_complaint_update` | Status communication | complaint_id, update_type, content, sent_at, channel |
| `fix.complaint.remedy` | `fix_complaint_remedy` | What was offered | complaint_id, remedy_type, value, approved_by, accepted_by_customer, accepted_at |
| `fix.complaint.taxonomy` | `fix_complaint_taxonomy` | Category structure | code, parent_code, name_en, name_bn, default_severity, default_owner_role |
| `fix.rating` | `fix_rating` | Multi-parameter rating | source_type, source_id, party_id, overall, timeliness, professionalism, behaviour, comment, captured_at |
| `fix.review` | `fix_review` | Published review | party_id, source_ref, rating, text, moderated_by, publication_consent, published_at, reply_text |
| `fix.journey.definition` | `fix_journey_definition` | Journey model | code, name, stages_json, touchpoints_json |
| `fix.journey.measurement` | `fix_journey_measurement` | Experience by stage | journey_id, party_id, stage, touchpoint, score, effort, measured_at |
| `fix.voc.theme` | `fix_voc_theme` | Extracted theme | period, theme, frequency, sentiment, sample_verbatims, driver_correlation |
| `fix.response.anomaly` | `fix_response_anomaly` | Integrity flag | detection_type, scope, evidence_json, detected_at, investigated_by, outcome |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party`, `fix.consent.record` | M33 | Identity and consent for survey dispatch |
| `fix.service.order`, `fix.work.order` | M01, M02 | Trigger source and attribution |
| `fix.conversation` | M27 | Conversation rating and complaint source |
| `fix.nonconformance`, `fix.capa` | M23 | Linked investigation |
| `fix.employee` | M21 | Technician and agent attribution |
| `fix.contract` | M08 | Tier and entitlement for complaint SLA |
| `fix.model` | M26 | Sentiment and theme extraction |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-CXM-01 | Trigger event occurs | Check eligibility, sampling and fatigue cap; dispatch the survey through M27 after the configured delay | Log as not surveyed with reason |
| AUT-CXM-02 | Survey unanswered after the reminder window | Send one reminder within fatigue limits; then close unanswered | — |
| AUT-CXM-03 | **Response received with a detractor or low CSAT score** | **Create a loop case within 60 seconds, assign the owner, set the 24-hour contact target, notify** | **Escalate immediately — an unrouted detractor is the failure this module exists to prevent** |
| AUT-CXM-04 | Loop case contact target passes without contact | Escalate to the branch manager; then to the operations director | Repeat and escalate |
| AUT-CXM-05 | Complaint received | Acknowledge immediately with reference and timescale; categorise; set SLA; assign owner | Manual acknowledgement task; alert |
| AUT-CXM-06 | Complaint SLA at 50% / 75% / 90% | Escalate progressively | Repeat and escalate |
| AUT-CXM-07 | Complaint categorised as a process failure | Raise a non-conformance in M23 with full customer context; link the records | Manual non-conformance task |
| AUT-CXM-08 | Complaint status changes | Update the customer through M27 at the defined points | Retry; alert owner |
| AUT-CXM-09 | Complaint resolved | Request customer confirmation; on dissatisfaction, reopen and escalate | — |
| AUT-CXM-10 | Promoter response received | Invite a review or referral, subject to consent and fatigue | — |
| AUT-CXM-11 | Response anomaly detected | Flag the scope, suspend affected scores from incentive calculation, notify HR and CCO | Escalate |
| AUT-CXM-12 | Period end | Compute CSAT, NPS, CES, response rate, coverage and closing-the-loop rate; publish to M25 | Alert on calculation failure |
| AUT-CXM-13 | Score published | Supply technician CSAT to M57 for incentive calculation, excluding flagged responses | Hold incentive input; alert |
| AUT-CXM-14 | Verbatim received | Extract theme and sentiment using M26; add to the VoC corpus | Queue for batch processing |

---

## 12. Interfaces

### 12.1 Upstream — M34 Consumes

| Source | What | Mechanism |
|---|---|---|
| M01 Service Order | Service completion, collection, rework — survey triggers and attribution | Event |
| M02 Field Service | Visit completion, technician attribution | Event |
| M27 Contact Centre | Conversation close, conversation rating, complaints raised in conversation | Event |
| M32 Conversational AI | Complaints and sentiment detected by the assistant | Event |
| M33 Party Master | Party identity, consent, tier | REST |
| M03 Logistics | Delivery completion — survey trigger | Event |
| M23 Quality | Non-conformance status for linked complaints | Event |
| M08 Contract | Customer tier for complaint SLA | REST |
| M26 AI/ML | Sentiment and theme extraction models | REST |
| M12 Marketplace | Marketplace job completion — separate survey path, seller-attributed | Event |

### 12.2 Downstream — M34 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M23 Quality** | **Non-conformances raised from complaints, with customer context** | **Command** |
| **M27 Contact Centre** | Survey dispatch requests; complaint acknowledgements and status updates | Command |
| **M57 Performance** | **Technician and agent CSAT for incentive calculation, anomaly-filtered** | Event + warehouse |
| M07 CRM | Satisfaction and complaint signals for account health | Event |
| M10 Loyalty | Promoter identification for referral invitation | Event |
| M35 Marketing | Promoter and detractor segments; review content | Event |
| M25 Business Intelligence | All experience facts | Warehouse extract |
| M26 AI/ML | Labelled satisfaction data for churn and quality-risk models | Warehouse extract |
| M12 Marketplace | 1000FiX-side experience context where a marketplace job is involved | REST |
| P01 Customer Portal | Complaint status, survey response, review submission | REST |
| P04 Corporate Portal | Account-level satisfaction and complaint summary | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `survey.dispatched` | survey, party, channel, trigger | M25 |
| `survey.responded` | response, score, type, attribution | M07, M25, M57 |
| **`detractor.detected`** | **response, party, score, attribution** | **Loop owner, M07, management** |
| `loop_case.created` | case, party, owner, contact due | M27 |
| `loop_case.closed` | case, action, customer confirmation, duration | M25, M23 |
| `loop_case.escalated` | case, level, reason | Management |
| `complaint.received` | complaint, party, category, severity, source | M23, M27, M07 |
| `complaint.acknowledged` | complaint, reference, timescale | M27 |
| `complaint.resolved` | complaint, remedy, duration, SLA outcome | M23, M07, M25 |
| `complaint.reopened` | complaint, reason, escalation | Management |
| `rating.captured` | source, party, parameters, comment | M57, M25 |
| `review.published` | party, rating, text | M35, website |
| `response.anomaly_detected` | scope, evidence | HR, CCO, M60 |
| `experience.period_scored` | period, CSAT, NPS, CES, response rate, coverage, loop closure rate | M25, M07 |
| `complaint.quality_classified` | complaint id, customer, related service order, quality failure class, severity, evidence refs | M23, M57, M60, M26 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/survey/respond/{token}` | POST | Frictionless response capture, unauthenticated | Customer, SMS, WhatsApp |
| `/api/v1/survey/definitions` | GET / POST | Survey design | P03 |
| `/api/v1/experience/scores` | GET | CSAT, NPS, CES with attribution filters | P03, P06, P04 |
| `/api/v1/loop-cases` | GET | Loop case queue | P03 |
| `/api/v1/loop-cases/{id}/contact` | POST | Record contact | P03, P10 |
| `/api/v1/loop-cases/{id}/close` | POST | Close with customer confirmation | P03, P10 |
| `/api/v1/complaints` | POST / GET | Raise and list complaints | P01, P03, P04, P10, M32 |
| `/api/v1/complaints/{id}` | GET / PATCH | Complaint detail and update | P01, P03, P04 |
| `/api/v1/complaints/{id}/remedy` | POST | Record a remedy | P03 |
| `/api/v1/ratings` | POST | Capture a rating | P01, P02, P10 |
| `/api/v1/reviews` | GET / POST | Review submission and publication | P01, website |
| `/api/v1/voc/themes` | GET | Theme and driver analysis | P03, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| Customer Service Manager | C R U D A | All surveys, complaints, loop cases, taxonomy |
| R35 Contact Centre Supervisor | C R U | Complaints and loop cases in own scope |
| R34 Contact Centre Agent | C R U | Raise complaints; contact loop cases assigned to them |
| R06 Branch Manager | R U A | Own branch scores, loop cases and complaints; compensation within limit |
| R05 Operations Director | R U A | All — escalation authority |
| R32 Quality Manager / ISO Coordinator | R U | Complaints linked to non-conformances; theme and driver analysis |
| R04 Chief Commercial Officer | R A | Scores, account-level satisfaction, compensation above branch limit |
| R30 HR Manager | R | Technician and agent scores for incentive purposes only |
| R10–R12 Technician | R | **Own scores only** |
| R36 Customer | C R | Own complaints, own survey responses, own reviews |
| R37 Corporate Portal User | R | Own company's complaints and satisfaction summary |
| R01 Chief Executive Officer | R | All experience measures |

**Field-level restrictions.** Individual verbatim comments naming a staff member are visible
to the Customer Service Manager, Branch Manager and HR Director only. Technicians see their
own aggregate scores, not individual attributed comments about them, unless released through
the coaching process.

**Segregation of duties.** The person whose score is under anomaly investigation cannot
participate in that investigation (SOD-21). Compensation approval is separated from complaint
ownership above the branch threshold (SOD-22).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Experience dashboard | Customer Service Manager, CEO | Daily | CSAT, NPS, CES, response rate, coverage, loop closure rate, trend |
| **Detractor queue** | **Branch managers, Ops Director** | **Real time** | Open loop cases by age against the contact target |
| **Closing-the-loop performance** | **Customer Service Manager, CEO** | **Weekly** | Loop cases created, contacted within target, closed, escalated |
| Branch comparison | Ops Director, CEO | Weekly | All 51+ branches on CSAT, NPS, complaint rate, loop closure |
| Technician scorecard | Ops Director, HR | Weekly | CSAT, timeliness, professionalism, behaviour per technician, with volume for significance |
| Complaint register | Customer Service Manager, Quality | Daily | Open complaints by category, severity, age, SLA status, owner |
| Complaint theme analysis | Quality Manager, Ops Director | Monthly | Categories by volume and trend; linkage to non-conformances |
| **Driver analysis** | **CEO, Ops Director** | **Quarterly** | Which operational measures correlate most strongly with satisfaction |
| Verbatim themes | Customer Service Manager, Marketing | Monthly | Emerging themes from free-text, Bengali and English |
| Journey experience | CCO, Ops Director | Quarterly | Score and effort by journey stage; friction points identified |
| Response integrity | HR Director, CCO | Monthly | Anomalies detected, scope, outcome |
| Review performance | Marketing Head | Monthly | Reviews captured, published, average rating, response rate |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-186 | **CSAT** | 3.8 / 5 | 4.3 | **4.7** |
| KPI-187 | **NPS** | unmeasured | 40 | **> 55** |
| KPI-188 | CES (lower is better) | unmeasured | baselined | **−25%** |
| KPI-189 | Survey response rate | n/a | 22% | **> 30%** |
| KPI-190 | **Survey coverage of eligible interactions** | 0% | 65% | **> 80%** |
| KPI-191 | **Closing-the-loop rate** | n/a | 80% | **> 92%** |
| KPI-192 | **Detractor contacted within 24 hours** | n/a | 85% | **> 95%** |
| KPI-193 | Complaint acknowledgement — immediate | unmeasured | **100%** | **100%** |
| KPI-194 | Complaint resolution within SLA | unmeasured | 88% | **> 95%** |
| KPI-195 | Complaint reopen rate | unmeasured | < 12% | **< 6%** |
| KPI-196 | Complaints escalated externally | unmeasured | < 1% | **< 0.3%** |
| KPI-197 | Promoter-to-review conversion | n/a | 12% | **> 20%** |
| KPI-198 | Response anomalies confirmed | n/a | < 1% | **< 0.3%** |
| KPI-199 | Survey fatigue breaches | n/a | **0** | **0** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L2 | OCA `survey`, `helpdesk_mgmt_rating`, `mgmtsystem_claim` | 18% |
| L5 | `cd_voc`, `cd_complaint`, `cd_journey`, `cd_closed_loop` | 82% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 3 of 4 identifiers below are claimed by another module: **CD-059** also claimed by M13; **CD-060** also claimed by M13; **CD-061** also claimed by M13. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-058 | `cd_voc` — survey triggers, sampling, fatigue, scoring, attribution, integrity | Odoo module | 6 PW |
| CD-059 | **`cd_closed_loop`** — detractor detection, loop case, contact tracking, closure verification, escalation | Odoo module | **4 PW** |
| CD-060 | `cd_complaint` — customer-facing complaint case, acknowledgement, updates, remedy, M23 linkage | Odoo module | 5 PW |
| CD-061 | `cd_journey` — journey definition, measurement, driver and verbatim analysis | Odoo module + service | 2 PW |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M34 is scheduled in **W4** (P1) but declares a dependency on 1 module(s) that land later: **M23** (W5). One of three things must be true before the W4 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W4 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M34 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W4 plan for M34 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| **M27 Contact Centre** | **Blocking** — surveys, acknowledgements and updates are all delivered through it |
| **M33 Party Master** | **Blocking** — consent evaluation and party attribution |
| M01, M02 | Trigger events and attribution source |
| M23 Quality | Non-conformance linkage — may be stubbed in W4 and completed in W5 |
| M26 AI/ML | Sentiment and theme extraction — verbatim analysis may lag to W6 |
| M57 Performance | CSAT consumed for incentives from W5 |

> **Sequencing note.** M34 can begin measuring in W4 but its full value depends on M23
> (non-conformance linkage, W5) and M57 (incentive linkage, W5). The **closed loop is the part
> that must work from day one** — measurement without it changes nothing.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing complaint records, if any | To be profiled | `fix.complaint` (open only) | W4 |
| Historical satisfaction data | **None exists** in structured form | — | — |
| Complaint taxonomy | **Authored, not migrated** — built with Quality from known failure categories | `fix.complaint.taxonomy` | W4 |

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **A detractor response creates a loop case within 60 seconds** | **Timed test, 50 responses** |
| AC-02 | **A loop case cannot be closed without recorded customer confirmation** | **Negative test** |
| AC-03 | A loop case not contacted within the target escalates automatically | Timed test |
| AC-04 | Every complaint is acknowledged immediately with a reference and timescale | Test across all intake channels |
| AC-05 | Complaint status updates reach the customer at the defined points without the customer chasing | End-to-end test |
| AC-06 | A complaint indicating process failure raises a linked non-conformance in M23 without duplication | Integration test |
| AC-07 | **The survey fatigue cap is enforced at dispatch and cannot be bypassed by launching a second survey** | **Negative test** |
| AC-08 | Every score is attributed to branch, technician, agent, service type and channel at capture | Data completeness check on 500 responses |
| AC-09 | Survey response requires no login and completes in a single tap where the question allows | Usability test on SMS and WhatsApp |
| AC-10 | Response anomaly detection identifies seeded manipulation patterns | Red-team test with three manipulation scenarios |
| AC-11 | Scores flagged as anomalous are excluded from incentive calculation until investigated | Integration test with M57 |
| AC-12 | CSAT, NPS, CES, response rate, coverage and loop closure rate compute correctly and reproducibly | Calculation audit against raw responses |
| AC-13 | Surveys are dispatched only with valid consent | Negative test |
| AC-14 | Verbatim theme extraction works on Bengali, romanised Bengali and English | Language test set |
| AC-15 | Customer Service Manager and Quality Manager sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **What is the detractor contact window — 24 hours, or shorter for high-value customers?** | Customer Service Manager | W4 build |
| Q-02 | **Who owns loop cases — the branch manager, the contact centre, or the technician's supervisor?** This determines whether the loop actually closes. | Ops Director / Customer Service Manager | **W4 minus 2 months** |
| Q-03 | What is the survey fatigue cap — one per customer per month, per quarter? | Customer Service Manager | W4 build |
| Q-04 | Is CSAT sampled or census? At 250,000 monthly interactions, census will exhaust customer goodwill. | Customer Service Manager | **W4 build** |
| Q-05 | What weight does CSAT carry in technician incentive, and what is the minimum response count for statistical validity? | HR Director / Ops Director | **W5 (M57)** |
| Q-06 | What is the compensation authority matrix by role and value? | CCO / CFO | W4 build |
| Q-07 | Will reviews be published on the corporate website, and who moderates them? | Marketing Head | W4 design |
| Q-08 | Is there an existing complaint log, and does it contain open cases that must be migrated? | Customer Service Manager | W4 minus 2 months |

**Q-02 is the one that determines whether this module works.** A loop case with no clear owner
is a loop that does not close.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §5 (M34/M23 boundary) · `M27_Omnichannel_Contact_Centre_and_Communications.md` ·
`M33_Customer_and_Party_Master_Management.md` · `M07_CRM_Sales_Pipeline_and_Account_Management.md` ·
`03_Modules/I_Governance_Risk_Quality_and_Knowledge/_CATEGORY_OVERVIEW.md` §3 (M23 boundary),
§6 (ISO 9001 clause mapping) ·
`03_Modules/H_People_and_Workforce/_CATEGORY_OVERVIEW.md` (M57 incentive linkage)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §6.3, BO-05, BR-CRM-005,
BR-CRM-008, BR-QMS-002, §7.3 A13 ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Ratings (four rating
parameters), §Customer Support (conversation rating) ·
`1000FiX_Services_Company_Profile.md` §Quality Assurance

**External benchmark and standards** *(verified 2026-08-12)*
**ISO 10002** *Quality management — Customer satisfaction — Guidelines for complaints handling
in organizations* — customer-focused environment open to feedback, prompt acknowledgement,
transparent status updates, structured root cause analysis, documented corrective actions,
top-management commitment, and analysis of complaints to improve quality ·
**Closed-loop practice** — companies that close the loop see approximately a threefold increase
in promoters on the next survey; the three most reliable NPS drivers are first-contact
resolution, reduced customer effort at every touchpoint, and closing the feedback loop with
detractors directly · **Voice-of-customer benchmarks** — NPS, CSAT, CES, response rate,
coverage and closing-the-loop rate as the six measures that matter ·
CX metric practice — NPS for relationship, CSAT for transaction, CES for effort ·
Odoo `survey` and OCA `helpdesk_mgmt_rating`

---

*Module M34 · Category B · 1000FiX ERP System v2.0 · CONFIDENTIAL*
