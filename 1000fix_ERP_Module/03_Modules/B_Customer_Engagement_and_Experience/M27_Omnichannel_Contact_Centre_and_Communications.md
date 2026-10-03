---
id: FIX-ERP2-M27
module_id: M27
module_code: CCE
module_name: Omnichannel Contact Centre & Communications
category: B — Customer Engagement & Experience
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Customer Service Manager
system_owner: Platform Squad
priority: P1
wave: W4
regulatory_verified: 2026-08-12
---

# M27 — Omnichannel Contact Centre & Communications
### Category B · Code `CCE` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M27 |
| **Module code** | `CCE` |
| **Category** | B — Customer Engagement & Experience |
| **Status** | Existing (re-scoped — conversational AI split to M32) |
| **Priority** | **P1** |
| **Delivery wave** | W4 (Months 14–18) |
| **Business owner** | Customer Service Manager |
| **System owner** | Platform Squad |
| **Delivery layers** | L4 (Novu, telephony) + L5 (custom) + L6 (cloud telephony / CPaaS) |
| **Custom modules** | `cd_conversation`, `cd_routing`, `cd_agent_desktop`, `cd_notification`, `cd_quality_monitor` |
| **Requirement range** | FR-CCE-001 … FR-CCE-058 |
| **Requirement count** | 58 |
| **Effort estimate** | 32 person-weeks |
| **Depends on** | M33 Party Master · M29 Identity · M28 Integration · M01 Service Order · M32 Conversational AI |
| **Depended on by** | **Every module that notifies a customer** — M01, M02, M03, M04, M05, M06, M08, M09, M10, M13, M14, M20, M34, M35, M53 |

---

## 2. Purpose

M27 owns **every conversation the Company has with anyone**, and **every message it sends**.

Two responsibilities live here that are often separated and should not be. The first is the
contact centre: hotline 16743, chat, WhatsApp, email and social, with queues, routing, agents
and quality monitoring. The second is **notification delivery**: the several million
transactional messages a year that every other module wants to send.

They belong together because they share the same three things: the customer's channel
preference, the customer's consent, and the customer's conversation history. A status SMS and
a support call are the same conversation from the customer's point of view, and the system
should treat them that way.

### Why It Exists

The hotline (16743) is the Company's most visible customer touchpoint and is entirely outside
the system of record. Nothing said on it is captured. A customer who calls three times about
one repair speaks to three agents who each start from nothing.

Meanwhile the v1.0 BRD estimates that customers call the hotline repeatedly simply to ask for
status, because there is no proactive notification. The contact centre is absorbing demand
created by the absence of communication.

The business plan also commits to **24/7 technical support** with defined escalation
procedures and quality monitoring. None of that is measurable today.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.4 (BR-CRM-004) | "Record and display communication history for each customer across all channels" |
| ERP BRD §6.2 Process 10 | Current state: status given verbally when the customer calls; no proactive notification; call centre overwhelmed |
| ERP BRD §7.3 Automation scenarios A4, A9, A13 | Customer notification at each milestone; renewal notification; CSAT survey — all delivered through this module |
| ERP BRD §14.2 (INT-05, INT-06, INT-08, INT-13) | SMS gateway, WhatsApp Business API, Firebase push, email service |
| ERP URD §14 | Notification channels, event-triggered notifications for customer, technician and manager, notification preferences, SMS template standards |
| Business Plan §24/7 Technical Support | Round-the-clock support, escalation procedures, remote assistance, knowledge base, **quality monitoring of support** |
| Service App SOW §Customer Support | "In-app chat with customer service… direct calling (in-app) to the call center… at the end of the chat, the customer will be able to rate the conversation and the entire conversation will be mailed to the customer's inbox… attachment option in chat… from the chat window, the chatting agent can move instantly to any other relevant window" |
| Service App SOW §Inbox | "Inbox will contain all push notifications, order update notifications, review request notifications, all SMS/email notifications, and any profile change notifications" |
| **BTRC regulation** *(verified 2026-08-12)* | **Do Not Disturb (DND) service** for promotional messages; **prohibition on sending SMS from midnight to dawn**; SMS masking and non-masking rules |
| **Personal Data Protection Act 2026** *(verified 2026-08-12)* | Consent required for processing; call recording is processing of personal data requiring a lawful basis and notice |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Voice: inbound and outbound telephony, IVR, call recording, hold, transfer, conference |
| 2 | Digital channels: web chat, in-app chat, WhatsApp, email, SMS inbound, social messaging |
| 3 | Unified conversation object spanning all channels |
| 4 | Queue management, skills-based routing and priority |
| 5 | Agent desktop with screen pop and cross-module navigation |
| 6 | Agent state, availability and wrap-up |
| 7 | Workforce management: forecasting, scheduling, adherence |
| 8 | Quality monitoring: recording, evaluation, calibration, coaching |
| 9 | **Notification delivery for the entire ERP** — templates, channels, language, timing |
| 10 | **Consent and DND enforcement at the point of send** |
| 11 | Customer inbox — a durable record of everything sent |
| 12 | Delivery tracking, retry, failover and dead-letter handling |
| 13 | Conversation transcript, attachment and rating capture |
| 14 | Contact centre performance measurement |
| 15 | Outbound campaigns execution (M35 designs; M27 delivers) |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Intent understanding, dialogue management, AI responses** | **M32** | Different failure mode, different governance, different release cadence |
| Party identity, contact points, **consent record** | **M33** | M27 enforces consent; M33 owns it |
| Campaign design, audience selection, journey logic | **M35** | M35 decides who and when; M27 delivers |
| Satisfaction scores, NPS, complaint case management | **M34** | M27 captures the rating; M34 owns the measurement and the complaint |
| Service order state and content | **M01** | M27 displays and creates; M01 owns |
| MSP client ticketing and contractual SLA | **M05** | Different SLA regime and audience |
| Knowledge article authoring | **M61** | M27 surfaces knowledge; M61 owns it |
| Agent employment, payroll, rostering source data | **M21** / **M55** | M27 schedules within the roster; HR owns the roster |
| Remote desktop session control | **M05** | M27 launches it; M05 owns it |
| Model training, serving and evaluation | **M26** | M32 consumes; M26 governs |

### 3.3 Shared Concepts

| Concept | M27's Role | Owning Module |
|---|---|---|
| Conversation | **Owns** | M27 |
| Notification | **Owns delivery** | M27 |
| Consent | **Enforces at send** | M33 |
| Template | **Owns** | M27 |
| Intent and AI reply | Hosts the channel; M32 produces the reply | M32 |
| Satisfaction rating | Captures | M34 |
| Complaint | Raises | M34 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **CCaaS platforms (Genesys, NICE, Five9, Nextiva, Avaya)** | Cloud voice plus digital channels in one interface; **omnichannel routing unifying every interaction into a single data thread so history and intent follow the customer across channel switches**; workforce management; quality management | **The single conversation thread across channels** — this is the defining design idea | Full CCaaS suite licensing at 30–50 agents; the ERP is the system of record, not the CCaaS |
| **Dynamics 365 Contact Center** | Agent desktop embedded in the CRM with screen pop and contextual actions | Agent desktop embedded in the ERP rather than a separate application | Platform-specific desktop framework |
| **CCaaS agent assistance (2026)** | Conversation summaries, suggested replies, next-best actions, real-time translation, AI form filling | Summaries and suggested replies **sourced from M32**, so the AI layer is replaceable | Vendor-locked AI assistance |
| **Novu** | Multi-channel notification infrastructure with templates, preferences, digest and delivery tracking | The notification substrate at zero licence cost | — |
| **WhatsApp Business Platform** | Template messages, session windows, opt-in requirements | Template governance and session-window discipline | — |
| **Bangladesh SMS practice** | **BTRC DND registry; midnight-to-dawn prohibition; masked and non-masked sender identity** | **All three as hard delivery-layer rules** | — |

**Design position.** Five deliberate differences.

First, **notification delivery is part of the contact centre, not a separate utility**. When a
customer replies to a status SMS, that reply must land in the same conversation the agent sees.
Splitting delivery from conversation guarantees it will not.

Second, **consent and DND are enforced in the delivery layer**. Not in campaign design, not in
the calling module. The last component before the message leaves is the only place enforcement
cannot be bypassed. Every module raises an intent to notify; M27 decides whether it may be sent.

Third, **the midnight-to-dawn rule is absolute for promotional traffic**. BTRC prohibits
promotional SMS overnight. M27 holds non-urgent messages in a quiet-hours queue and releases
them at the permitted hour. Transactional messages with genuine urgency are separately
classified and exempt by policy, with the classification auditable.

Fourth, **the customer inbox is durable**. The SOW specifies an inbox containing everything
sent. That is not a UI feature; it means every notification is a persisted, addressable object
with a delivery state — which is also what makes delivery measurable.

Fifth, **AI is a service the channel calls, not a property of the channel**. M27 hosts the
conversation; M32 answers. A telephony change must never require an AI release.

---

## 5. Functional Areas & Features

### 5.1 Voice Channel

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CCE-001 | Inbound voice | Receive calls to hotline 16743 and branch numbers, with number identification and party resolution before answer | P1 | L6 |
| FR-CCE-002 | IVR | Present a bilingual menu, capture intent, offer self-service, and route to the correct queue | P1 | L6 |
| FR-CCE-003 | Callback | Offer a callback in place of queueing, and honour it within the promised window | P2 | L5 |
| FR-CCE-004 | Outbound voice | Place outbound calls from the agent desktop with logging and consent evaluation | P1 | L6 |
| FR-CCE-005 | Call control | Hold, transfer (warm and cold), conference, mute and disconnect with full event logging | P1 | L6 |
| FR-CCE-006 | **Call recording** | Record calls where policy requires, **announce recording to the caller**, store under retention rules, and restrict access | **P0** | L6 |
| FR-CCE-007 | Voicemail | Capture voicemail out of hours, transcribe where possible, and queue it as a conversation | P2 | L5 |
| FR-CCE-008 | Emergency and after-hours routing | Route out-of-hours calls to the on-call rota per the 24/7 support model | P1 | L5 |

### 5.2 Digital Channels

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CCE-009 | Web and in-app chat | Provide chat on the website, customer app and corporate portal, with queueing and agent assignment | P1 | L5 |
| FR-CCE-010 | WhatsApp | Send and receive on WhatsApp Business, respecting template rules, opt-in and the 24-hour session window | P1 | L3 |
| FR-CCE-011 | Email | Receive to shared mailboxes, parse and thread, and send with tracking | P1 | L1 |
| FR-CCE-012 | Inbound SMS | Receive replies to outbound SMS and thread them to the originating conversation | P1 | L5 |
| FR-CCE-013 | Social messaging | Receive and respond on Facebook Messenger and other approved social channels | P2 | L5 |
| FR-CCE-014 | Chat attachments | Accept and send attachments in chat, malware-scanned, with size and type controls | P1 | L5 |
| FR-CCE-015 | Chat transcript to customer | Email the full transcript to the customer at conversation close, per the SOW | P1 | L5 |
| FR-CCE-016 | Channel switching | Continue one conversation across a channel switch without losing history or context | **P1** | L5 |

### 5.3 Conversation & Routing

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CCE-017 | Unified conversation | Represent every interaction, on any channel, as a conversation linked to a party and, where relevant, a service order, contract or ticket | **P1** | L5 |
| FR-CCE-018 | Conversation threading | Thread related interactions into one conversation using party, reference and time proximity | P1 | L5 |
| FR-CCE-019 | Queue management | Define queues by channel, service, language, tier and business line, with configurable overflow | P1 | L5 |
| FR-CCE-020 | Skills-based routing | Route to agents by skill, language, product knowledge, tier authorisation and current load | P1 | L5 |
| FR-CCE-021 | Priority routing | Prioritise by customer tier, contract SLA, emergency flag and repeat contact | P1 | L5 |
| FR-CCE-022 | Concurrency control | Limit concurrent digital conversations per agent by channel | P1 | L5 |
| FR-CCE-023 | Transfer and escalation | Transfer between agents, queues and to supervisors, carrying full context | P1 | L5 |
| FR-CCE-024 | **AI handoff** | Accept a conversation handed off from M32 with the full transcript, detected intent, and reason for handoff | **P1** | L5 |
| FR-CCE-025 | Conversation SLA | Apply response and resolution targets per channel and priority, with escalation on risk | P1 | L5 |

### 5.4 Agent Desktop

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CCE-026 | Screen pop | Present the resolved party, their open items and recent history before the agent answers | **P1** | L5 |
| FR-CCE-027 | Unified workspace | Handle voice and digital from one interface with a single conversation view | P1 | L5 |
| FR-CCE-028 | Cross-module navigation | Move directly from the conversation to the service order, contract, invoice, asset or ticket, per the SOW | P1 | L5 |
| FR-CCE-029 | In-conversation actions | Create a service order, reschedule, take payment, issue a voucher, launch a remote session, without leaving the conversation | P1 | L5 |
| FR-CCE-030 | Knowledge surfacing | Surface relevant knowledge articles from M61 based on detected intent | P2 | L5 |
| FR-CCE-031 | Suggested replies and summary | Present AI-generated suggestions and a conversation summary sourced from M32, always editable by the agent | P2 | L5 |
| FR-CCE-032 | Agent state | Manage available, busy, wrap-up, break and offline states with reason codes | P1 | L5 |
| FR-CCE-033 | Wrap-up and disposition | Capture a structured disposition and notes before the agent returns to available | P1 | L5 |
| FR-CCE-034 | Agent-side translation | Offer Bengali–English translation assistance in digital channels | P3 | L5 |

### 5.5 Notification Delivery — the ERP-wide Service

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CCE-035 | Notification intent API | Accept a notification intent from any module, stating party, event, purpose and urgency — never a channel or a rendered message | **P1** | L5 |
| FR-CCE-036 | Template management | Maintain versioned templates per event, channel and language, with approval before publication | P1 | L5 |
| FR-CCE-037 | Channel selection | Select the channel from the party's preference, the message urgency, channel availability and cost | P1 | L5 |
| FR-CCE-038 | **Consent enforcement** | Evaluate consent in M33 for the stated purpose and channel; suppress and log where absent | **P0** | L5 |
| FR-CCE-039 | **DND enforcement** | Suppress promotional traffic to numbers registered on the BTRC Do Not Disturb service | **P0** | L5 |
| FR-CCE-040 | **Quiet-hours enforcement** | Hold promotional messages during the prohibited overnight window and release at the permitted hour | **P0** | L5 |
| FR-CCE-041 | Urgency classification | Classify every notification as transactional-urgent, transactional-routine or promotional, with the classification auditable and challengeable | **P1** | L5 |
| FR-CCE-042 | Delivery tracking | Track queued, sent, delivered, read, failed and bounced per message, per channel | P1 | L5 |
| FR-CCE-043 | Retry and failover | Retry per channel policy and fail over to an alternative channel where the message is urgent and consent permits | P1 | L5 |
| FR-CCE-044 | Digest and throttling | Bundle non-urgent notifications and throttle per-party volume to prevent fatigue | P2 | L5 |
| FR-CCE-045 | **Customer inbox** | Persist every notification to a durable customer inbox visible in the portal and app, per the SOW | **P1** | L5 |
| FR-CCE-046 | Preference centre | Let the customer set channel preference per notification category, within mandatory transactional minimums | P1 | L5 |
| FR-CCE-047 | Bulk send execution | Execute campaign sends designed in M35, applying all suppression rules per recipient | P1 | L5 |
| FR-CCE-048 | Sender identity | Manage masked and non-masked sender identities per message class and regulatory requirement | P1 | L5 |
| FR-CCE-049 | Cost tracking | Record delivery cost per message and report cost by module, event and channel | P2 | L5 |

### 5.6 Workforce & Quality Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CCE-050 | Volume forecasting | Forecast contact volume by channel, interval and skill from history and known drivers | P2 | L5 |
| FR-CCE-051 | Scheduling | Produce agent schedules against the forecast, within rosters supplied by M55 | P2 | L5 |
| FR-CCE-052 | Adherence | Measure schedule adherence and occupancy | P2 | L5 |
| FR-CCE-053 | Real-time operations board | Show live queue depth, wait times, agent states, service level and abandonment | P1 | L5 |
| FR-CCE-054 | Quality evaluation | Evaluate recorded interactions against a scorecard, with sampling rules | P2 | L5 |
| FR-CCE-055 | Calibration | Run calibration sessions so evaluators score consistently | P3 | L5 |
| FR-CCE-056 | Coaching | Record coaching from evaluations and track improvement | P3 | L5 |
| FR-CCE-057 | Agent performance | Report handled volume, handle time, first-contact resolution, satisfaction and quality score per agent | P1 | L5 |
| FR-CCE-058 | Contact reason analysis | Report contact reasons by volume and trend, identifying demand that should be designed out | **P1** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Delivery-layer enforcement** | Consent, DND and quiet-hours checks execute in the final send path. No module can bypass them by calling a provider directly — provider credentials are held only by M27 |
| T-02 | **Fail-closed suppression** | If the consent service is unavailable, promotional sends **stop**; transactional-urgent sends proceed under a documented exception with an audit record |
| T-03 | **Intent-not-message API** | Callers submit an event and a purpose. M27 selects channel, template, language and timing. Callers cannot pass a rendered message body |
| T-04 | **Idempotent delivery** | Each notification intent carries a key; a retried intent produces one message |
| T-05 | **Quiet-hours queue** | Held messages are queued with a release time, survive restart, and release in order |
| T-06 | **Conversation continuity** | Channel switch preserves the conversation identifier; history is assembled from a single event stream, not per-channel silos |
| T-07 | **Recording storage and access** | Recordings are encrypted at rest, access-logged, retained per schedule, and excluded from analytics extracts |
| T-08 | **Screen-pop latency** | Party resolution and context assembly complete before the agent answers — under 1.5 seconds from call arrival |
| T-09 | **AI service boundary** | M32 is called over a versioned interface with a strict timeout; on failure the conversation continues without AI assistance rather than failing |
| T-10 | **Provider abstraction** | SMS, WhatsApp, email, push and voice providers sit behind an adapter so a provider can be replaced without touching calling modules |
| T-11 | **Bengali rendering across channels** | Bengali renders correctly in SMS (character-set and segment counting), WhatsApp, email and push, with segment cost calculated correctly |
| T-12 | **Throughput** | Sustain 50,000 notifications per hour with delivery-state tracking |
| T-13 | **Performance envelope** | Notification intent accepted ≤ 200 ms · screen pop ≤ 1.5 s · agent desktop load ≤ 2 s · conversation history ≤ 1 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M27 |
|---|---|---|
| **Customer** | Calls three times to ask for status; explains themselves each time | Receives updates unprompted; when they do call, the agent already knows |
| **Contact centre agent** | Answers blind; writes on paper; cannot act without leaving the call | Screen pop with full context; creates orders, takes payment and reschedules in-conversation |
| **Customer Service Manager** | Cannot see volume, wait, resolution or quality | Live board and daily reporting on every measure |
| **Every other module owner** | Builds its own notification code and hopes about consent | Raises an intent; M27 handles channel, language, timing, consent and delivery |
| **Marketing** | Sends and hopes | Sends through a layer that enforces suppression and reports delivery |
| **Compliance officer** | Cannot evidence that a customer's opt-out was honoured | Every suppression is logged with the reason |
| **CFO** | Cannot see communication spend | Cost by module, event and channel |
| **Branch staff** | Field status calls that should never reach them | Status demand is absorbed by notification and self-service |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Hotline demand reduction** | Proactive milestone notification plus tracking link removes the reason for status calls | **60–80% deflection of status enquiries**, releasing contact-centre capacity without hiring |
| **First-contact resolution** | Screen pop, full history and in-conversation actions | **> 78% FCR**, reducing repeat contact volume |
| **Notification reliability** | One delivery layer with tracking, retry and failover | **> 98% delivery success**; today it is unmeasured |
| **Regulatory exposure avoided** | Consent, DND and quiet-hours enforced in the delivery path | Avoids PDPA exposure to **BDT 25 lakh** and BTRC compliance action |
| **Communication cost control** | Channel selection by cost, digest bundling, throttling, and cost reporting | Typically **20–30%** reduction in messaging spend once visible |
| **Conversation history as an asset** | Every interaction captured against the party | Enables M34 experience measurement and M26 intent models |
| **24/7 commitment made real** | Out-of-hours routing and on-call rota | Converts a marketing claim into a measurable service |
| **Contact reason analysis** | Volume by reason shows which demand is avoidable | Drives design-out of failure demand — the highest-return use of contact centre data |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The hotline joins the system of record** | 16743 is the Company's most visible touchpoint and is currently invisible to the business |
| **Consent becomes demonstrable in practice** | A policy that is not enforced in the send path is not a control |
| **Agents stop being blamed for the system** | Most poor service in a contact centre is caused by the agent not having information, not by the agent |
| **Failure demand becomes visible** | Knowing that 30% of calls are "where is my device" is what justifies fixing the underlying process |
| **Quality becomes coachable** | Recording and evaluation turn management from impression to evidence |
| **A platform for the AI assistant** | M32 has no value without a channel layer to operate in and a human to hand off to |

---

## 8. Lifecycle & State Models

### 8.1 Conversation

```
   +-----------+
   | INITIATED |  inbound on any channel, or outbound initiated
   +-----+-----+
         | party resolved (M33)
   +-----v-----+
   |  QUEUED   |  skills, priority, tier, SLA applied
   +-----+-----+
         |
   +-----v----------+        +------------------+
   | AI HANDLING    |------->|  AI RESOLVED     |  (M32, no human involved)
   | (M32)          |        +------------------+
   +-----+----------+
         | handoff: low confidence, emotion, SLA risk, guardrail, customer request
   +-----v-----+
   | ASSIGNED  |
   +-----+-----+
         |
   +-----v-----+       +-------------+
   |  ACTIVE   |<----->| TRANSFERRED |  context carried
   +-----+-----+       +-------------+
         |
   +-----v-----+
   |  WRAP-UP  |  disposition and notes captured
   +-----+-----+
         |
   +-----v-----+
   | RESOLVED  |  transcript sent to customer; rating requested (M34)
   +-----+-----+
         |
   +-----v-----+
   |  CLOSED   |
   +-----------+

   REOPENED -- customer replies within the reopen window; same conversation continues
   ABANDONED -- customer left the queue before assignment
```

### 8.2 Notification

```
   INTENT RAISED (by any module: party + event + purpose + urgency)
        |
   +----v-----------------+
   | CLASSIFIED           |  transactional-urgent / transactional-routine / promotional
   +----+-----------------+
        |
   +----v-----------------+       consent absent
   | CONSENT EVALUATED    |------------------------> SUPPRESSED (logged with reason)
   | (M33, fails closed)  |
   +----+-----------------+
        |
   +----v-----------------+       number on BTRC DND, promotional
   | DND EVALUATED        |------------------------> SUPPRESSED (logged)
   +----+-----------------+
        |
   +----v-----------------+       promotional, within prohibited overnight window
   | QUIET HOURS CHECKED  |------------------------> HELD --> released at permitted hour
   +----+-----------------+
        |
   +----v-----------------+
   | CHANNEL SELECTED     |  preference, urgency, availability, cost
   +----+-----------------+
        |
   +----v-----------------+
   | RENDERED             |  template version, language, personalisation
   +----+-----------------+
        |
   +----v-----+     +----------+     +-----------+
   |  QUEUED  |---->|   SENT   |---->| DELIVERED |----> READ (where supported)
   +----------+     +-----+----+     +-----------+
                          |
                          +--> FAILED --> RETRY --> FAILOVER CHANNEL --> DEAD LETTER
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-CCE-01 | **No message is sent without a consent evaluation for its purpose and channel** | **H** | CDO |
| BRU-CCE-02 | **Promotional messages are never sent to a number on the BTRC Do Not Disturb registry** | **H** | Marketing Head |
| BRU-CCE-03 | **Promotional messages are not sent during the prohibited overnight window; they are held and released** | **H** | Marketing Head |
| BRU-CCE-04 | Every notification carries an urgency classification; misclassifying promotional traffic as transactional is a disciplinary matter | **H** | CDO |
| BRU-CCE-05 | If the consent service is unavailable, promotional sending stops; transactional-urgent proceeds under a logged exception | **H** | CTO |
| BRU-CCE-06 | **Call recording is announced to the caller before recording begins** | **H** | CDO / Legal |
| BRU-CCE-07 | Recording access is restricted to named roles and every access is logged | **H** | CDO |
| BRU-CCE-08 | Calling modules submit an intent, never a rendered message or a channel | **H** | CTO |
| BRU-CCE-09 | Provider credentials are held only by M27; no other module may call a provider directly | **H** | CTO |
| BRU-CCE-10 | Every conversation is linked to a resolved party before assignment, or flagged as unidentified | **H** | Customer Service Manager |
| BRU-CCE-11 | A conversation cannot close without a disposition | **H** | Customer Service Manager |
| BRU-CCE-12 | A transcript is sent to the customer on close of a digital conversation | **H** | Customer Service Manager |
| BRU-CCE-13 | Mandatory transactional notifications cannot be disabled in the preference centre | **H** | CCO |
| BRU-CCE-14 | An AI handoff carries the full transcript and the handoff reason | **H** | Customer Service Manager |
| BRU-CCE-15 | Per-party notification volume is throttled to a configured maximum per period | **C** | Marketing Head |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.conversation` | `fix_conversation` | The unified interaction | party_id, primary_channel, state, initiated_at, resolved_at, queue_id, agent_id, subject_type, subject_id, disposition, ai_handled, handoff_reason |
| `fix.conversation.message` | `fix_conversation_message` | One message or turn | conversation_id, direction, channel, sender_type, body, attachments, occurred_at, provider_ref |
| `fix.conversation.event` | `fix_conversation_event` | State and control events | conversation_id, event_type, actor, occurred_at, detail |
| `fix.queue` | `fix_queue` | Routing target | code, channels, skills_required, language, priority_rules, sla_policy_id, overflow_queue_id |
| `fix.routing.rule` | `fix_routing_rule` | Assignment logic | queue_id, criteria_json, agent_skill_match, priority_weight, active |
| `fix.agent.profile` | `fix_agent_profile` | Contact centre view of an employee | employee_id, skills, languages, channels, max_concurrent, tier_authorisation |
| `fix.agent.state.log` | `fix_agent_state_log` | Availability history | agent_id, state, reason, started_at, ended_at |
| `fix.call.recording` | `fix_call_recording` | Recording metadata | conversation_id, storage_ref, duration, announced, retention_until, access_log_ref |
| `fix.notification.intent` | `fix_notification_intent` | The request to notify | source_module, event_code, party_id, purpose, urgency_class, payload_json, idempotency_key, raised_at |
| `fix.notification` | `fix_notification` | A rendered, addressed message | intent_id, channel, template_version_id, language, address, state, queued_at, sent_at, delivered_at, read_at, failure_reason, cost |
| `fix.notification.template` | `fix_notification_template` | Versioned template | event_code, channel, language, body, variables, version, approved_by, published_at |
| `fix.notification.suppression` | `fix_notification_suppression` | Why a send did not happen | intent_id, reason, evaluated_at, evidence_ref |
| `fix.dnd.registry` | `fix_dnd_registry` | BTRC DND state | msisdn, dnd_status, source, checked_at |
| `fix.quiet.hours.queue` | `fix_quiet_hours_queue` | Held promotional messages | notification_id, held_at, release_at, released_at |
| `fix.customer.inbox` | `fix_customer_inbox` | Durable customer-facing record | party_id, notification_id, category, read_at, archived |
| `fix.channel.preference` | `fix_channel_preference` | Per-category preference | party_id, category, preferred_channel, opted_out |
| `fix.contact.forecast` | `fix_contact_forecast` | Volume forecast | channel, interval, forecast_volume, actual_volume, skill |
| `fix.agent.schedule` | `fix_agent_schedule` | Planned coverage | agent_id, interval, activity, adherence_actual |
| `fix.quality.evaluation` | `fix_quality_evaluation` | Scored interaction | conversation_id, evaluator_id, scorecard_id, scores_json, total, coaching_notes |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party`, `fix.contact.point` | M33 | Resolve caller; address selection |
| **`fix.consent.record`** | **M33** | **Evaluated before every send — fails closed** |
| `fix.service.order` | M01 | Screen pop context; in-conversation creation |
| `fix.contract`, `fix.entitlement` | M08 | Priority and entitlement context |
| `fix.membership` | M10 | Tier for priority routing |
| `fix.knowledge.article` | M61 | Surfaced to the agent |
| `fix.employee`, `fix.roster` | M21 / M55 | Agent identity and roster |
| `fix.complaint` | M34 | Raised from a conversation |
| `fix.msp.ticket` | M05 | Client conversations linked to tickets |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-CCE-01 | Inbound contact on any channel | Resolve the party, assemble context, create or thread the conversation, route to queue | Route to a general queue flagged unidentified |
| AUT-CCE-02 | Conversation queued | Apply priority from tier, contract SLA, emergency flag and repeat-contact signal | Default priority |
| AUT-CCE-03 | Agent becomes available | Assign the highest-priority waiting conversation matching their skills | Supervisor assigns manually |
| AUT-CCE-04 | Conversation SLA at risk | Alert the supervisor; escalate priority | Repeat and escalate |
| AUT-CCE-05 | **Notification intent received** | **Classify urgency, evaluate consent, evaluate DND, apply quiet hours, select channel, render, queue** | **Suppress and log; never send on uncertainty for promotional traffic** |
| AUT-CCE-06 | Send fails | Retry per channel policy; fail over where urgent and consent permits; dead-letter after exhaustion | Alert on dead-letter accumulation |
| AUT-CCE-07 | Quiet-hours release time reached | Release held promotional messages in order | Alert if the queue exceeds threshold |
| AUT-CCE-08 | Digital conversation resolved | Send the transcript to the customer; request a rating through M34 | Retry once |
| AUT-CCE-09 | AI confidence low, or emotion or guardrail signal | Hand off to a human queue with the full transcript and reason | Escalate to supervisor if no agent available |
| AUT-CCE-10 | Customer replies to an outbound message | Thread into the originating conversation and route | Create a new conversation flagged for linking |
| AUT-CCE-11 | Out-of-hours contact | Route per the on-call rota; take voicemail where unattended | Voicemail with next-business-day commitment |
| AUT-CCE-12 | DND registry refresh | Update DND status for the customer base on the published cadence | Alert on staleness beyond threshold |
| AUT-CCE-13 | Notification volume to a party exceeds the throttle | Digest or defer non-urgent messages | — |
| AUT-CCE-14 | Quality sampling schedule | Select interactions for evaluation per the sampling rules and assign to evaluators | — |

---

## 12. Interfaces

### 12.1 Upstream — M27 Consumes

| Source | What | Mechanism |
|---|---|---|
| **All modules** | **Notification intents** | **REST / event** |
| M33 Party Master | Party resolution, contact points, **consent**, channel preference | REST, synchronous |
| M32 Conversational AI | AI replies, intent, confidence, handoff decision, summaries, suggested replies | REST with timeout |
| M01 Service Order | Screen-pop context; milestone events | REST + event |
| M08, M10 | Entitlement and tier for priority routing | REST |
| M35 Marketing | Campaign send instructions with audience | Command |
| M61 Knowledge | Articles surfaced by intent | REST |
| M55 Workforce | Agent rosters and availability | Event projection |
| M05 Managed Services | Client ticket context for MSP conversations | REST |

### 12.2 Downstream — M27 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M33 Party Master | Verified contact points captured during conversation | Command |
| M01 Service Order | Service orders created in-conversation | Command |
| M34 Customer Experience | Conversation ratings, transcripts, complaint triggers | Event |
| M07 CRM | Leads raised during conversation; engagement signal | Event |
| M32 Conversational AI | Conversation transcripts for model improvement | Warehouse extract |
| M25 Business Intelligence | Volume, handling, resolution, delivery and cost facts | Warehouse extract |
| M26 AI/ML | Transcript corpus for intent and sentiment models | Warehouse extract |
| M60 GRC | Suppression log, recording access log, consent enforcement evidence | Event |
| M53 / M54 | Communication cost by module and channel | Warehouse extract |
| P01, P04 | Customer inbox, chat, transcript, preference centre | REST |
| P10 Contact Centre Console | Agent desktop | REST + WebSocket |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `conversation.initiated` | conversation, party, channel, subject | M34, M25 |
| `conversation.assigned` | conversation, agent, queue, wait time | M25 |
| `conversation.resolved` | conversation, disposition, duration, FCR flag | M34, M25 |
| `conversation.rated` | conversation, rating, comment | **M34** |
| `conversation.ai_handoff` | conversation, reason, confidence, transcript | M32, M25 |
| `notification.sent` | notification, party, channel, event, cost | M25 |
| `notification.delivered` / `.failed` | notification, state, reason | M25, source module |
| **`notification.suppressed`** | **intent, reason (consent / DND / quiet hours), party** | **M60, M35, M25** |
| `contact_point.verified` | party, channel, value | M33 |
| `complaint.raised_from_conversation` | conversation, party, category | M34 |
| `lead.raised_from_conversation` | conversation, party, requirement | M07 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| **`/api/v1/notify`** | **POST** | **Raise a notification intent — party, event, purpose, urgency** | **All modules** |
| `/api/v1/notify/{id}/status` | GET | Delivery state | Source modules |
| `/api/v1/notify/bulk` | POST | Campaign send with per-recipient suppression | M35 |
| `/api/v1/conversations` | GET / POST | List and create conversations | P10, P01 |
| `/api/v1/conversations/{id}` | GET | Full conversation with history | P10, P03 |
| `/api/v1/conversations/{id}/message` | POST | Send a message on a channel | P10, P01 |
| `/api/v1/conversations/{id}/transfer` | POST | Transfer with context | P10 |
| `/api/v1/conversations/{id}/disposition` | POST | Wrap-up and close | P10 |
| `/api/v1/agent/state` | POST | Set agent availability | P10 |
| `/api/v1/queues/live` | GET | Real-time operations board | P10, P03 |
| `/api/v1/inbox/{party}` | GET | Customer inbox | P01, P04 |
| `/api/v1/preferences/{party}` | GET / PUT | Channel preference centre | P01 |
| `/hooks/v1/channel/{provider}` | POST | Inbound webhook from a channel provider | External |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R34 Contact Centre Agent | C R U | Own assigned conversations |
| R35 Contact Centre Supervisor | C R U D A | All conversations in own queues; transfer, barge, evaluate |
| Customer Service Manager | C R U D A | All conversations, templates, queues, routing |
| R23 Marketing Manager | R U | Campaign templates and send performance |
| R08 Service Centre Agent | R | Conversations for own branch's customers |
| R22 Account Manager (Corporate) | R | Conversations for own accounts |
| R13 Remote Support Engineer | C R U | MSP client conversations |
| R32 Quality Manager / ISO Coordinator | R U | Evaluations and calibration |
| **R40 Chief Data Officer** | R A | Suppression log, recording access, consent enforcement evidence |
| R36 Customer | R | Own inbox, own transcripts, own preferences |
| R33 IT / System Administrator | — | **No access to conversation content**; provider configuration only |

**Field-level restrictions.** Call recordings require explicit grant; every access is logged.
Conversation content is excluded from analytics extracts except as an anonymised corpus for
M26 under a documented basis.

**Segregation of duties.** A supervisor cannot evaluate their own handled conversations
(SOD-19).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Live operations board | Supervisors, Customer Service Manager | Real time | Queue depth, longest wait, agents by state, service level, abandonment |
| Daily contact summary | Customer Service Manager | Daily | Volume by channel, handled, abandoned, FCR, average handle time |
| **Contact reason analysis** | **Customer Service Manager, Ops Director** | **Weekly** | Volume by reason; failure demand identified for design-out |
| Agent performance | Supervisors, HR | Weekly | Volume, handle time, FCR, satisfaction, quality score, adherence |
| **Notification delivery** | **CTO, all module owners** | **Daily** | Sent, delivered, failed, suppressed by module, event and channel |
| **Suppression report** | **CDO, Marketing Head** | **Weekly** | Suppressions by reason — consent, DND, quiet hours — with trend |
| Communication cost | CFO, CTO | Monthly | Cost by module, event, channel and campaign |
| Channel mix | Customer Service Manager | Monthly | Volume shift between channels; self-service deflection |
| Quality scorecard | Quality Manager, supervisors | Monthly | Evaluation scores, calibration variance, coaching completion |
| Forecast accuracy | Customer Service Manager | Weekly | Forecast against actual volume by interval |
| 24/7 coverage | Customer Service Manager | Monthly | Out-of-hours volume, response, on-call utilisation |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-160 | Conversations captured in the system | ~0% | 95% | **100%** |
| KPI-161 | First-contact resolution (all channels) | unmeasured | 70% | **> 78%** |
| KPI-162 | Notification delivery success | unmeasured | 96% | **> 98%** |
| KPI-163 | Status enquiries deflected | 0% | 60% | **> 80%** |
| KPI-164 | Average speed of answer — voice | unmeasured | < 45 s | **< 30 s** |
| KPI-165 | Abandonment rate | unmeasured | < 8% | **< 5%** |
| KPI-166 | Average handle time | unmeasured | baselined | **−15%** |
| KPI-167 | **Messages sent without consent evaluation** | unknown | **0** | **0** |
| KPI-168 | **Promotional messages sent in the prohibited window** | unknown | **0** | **0** |
| KPI-169 | **Promotional messages sent to DND-registered numbers** | unknown | **0** | **0** |
| KPI-170 | Screen-pop success rate (party resolved before answer) | 0% | 88% | **> 95%** |
| KPI-171 | Communication cost per contact | unmeasured | baselined | **−20%** |
| KPI-172 | Conversation rating | unmeasured | > 4.0/5 | **> 4.4/5** |
| KPI-173 | Notification dead-letter rate | n/a | < 0.5% | **< 0.1%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `mail` for email substrate | 6% |
| L2 | OCA `mail_*` extensions | 4% |
| L4 | **Novu** notification infrastructure; Firebase push | 18% |
| L5 | `cd_conversation`, `cd_routing`, `cd_agent_desktop`, `cd_notification`, `cd_quality_monitor` | 62% |
| **L6** | **Cloud telephony / CPaaS for hotline 16743 interconnect** *(decision D-04)* | 10% |

### 16.2 Custom Development

> CD identifiers are **provisional** pending the unified register in `02-05` (audit H-03).

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-048 | `cd_conversation` — unified conversation, threading, channel adapters | Odoo module + service | 8 PW |
| CD-049 | `cd_routing` — queues, skills, priority, concurrency, SLA | Odoo module | 5 PW |
| CD-050 | `cd_agent_desktop` — screen pop, unified workspace, in-conversation actions | Frontend + module | 7 PW |
| CD-051 | **`cd_notification`** — intent API, classification, **consent/DND/quiet-hours enforcement**, templates, delivery tracking, inbox | Service + module | **9 PW** |
| CD-052 | `cd_quality_monitor` — recording linkage, evaluation, calibration, coaching | Odoo module | 3 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M33 Party Master** | **Blocking** — consent enforcement and party resolution both depend on it |
| M29 Identity | Agent authentication, recording access control |
| M28 Integration | Provider adapters and event transport |
| M01 Service Order | Screen-pop context and milestone events |
| M32 Conversational AI | AI-first handling — **may be deferred**; M27 operates human-only if M32 slips |
| **Telephony provider contracted** | **Blocking for voice** *(decision D-04)* — digital channels can proceed without it |
| **DND data access arrangement** | **Blocking for promotional SMS** — how the Company obtains DND status must be resolved |

> **Phasing note.** The **notification delivery service (CD-051) should be delivered early —
> in Wave 1 or 2, not Wave 4**. Every module from W1 onward needs to notify customers, and
> each will otherwise build its own send path, which is precisely the fragmentation the
> programme exists to remove. This is a **recommended change to the wave plan** in `06-01`.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing SMS templates | Unknown | `fix.notification.template` | W1 (with CD-051) |
| Historical conversations | **None exist** in structured form | — | — |
| Agent roster and skills | 30–50 agents | `fix.agent.profile` | W4 |
| DND status for the customer base | 250,000+ numbers | `fix.dnd.registry` | W4, then refreshed |

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **No message can be sent by any module without passing through M27's consent evaluation** | **Code review, negative test, provider credential audit** |
| AC-02 | **Promotional messages to DND-registered numbers are suppressed and logged** | **Negative test with a seeded DND number** |
| AC-03 | **Promotional messages raised during the prohibited window are held and released at the permitted hour** | **Timed test across the boundary** |
| AC-04 | If the consent service is unavailable, promotional sending stops | Fault-injection test |
| AC-05 | A conversation continues across a channel switch with full history | End-to-end test: chat to voice to WhatsApp |
| AC-06 | Screen pop presents the resolved party and context within 1.5 seconds of call arrival | Timed test, 50 calls |
| AC-07 | An agent can create a service order, take payment and reschedule without leaving the conversation | Demonstration |
| AC-08 | AI handoff carries the full transcript and the handoff reason | Test with M32 |
| AC-09 | Call recording is announced before recording begins | Audio verification |
| AC-10 | Recording access is restricted and every access is logged | Access audit |
| AC-11 | Digital conversation close sends the transcript to the customer | End-to-end test |
| AC-12 | Delivery state is tracked to delivered or failed for every message | Reconciliation over 10,000 messages |
| AC-13 | The system sustains 50,000 notifications per hour with state tracking | Load test |
| AC-14 | Bengali renders correctly across SMS, WhatsApp, email and push, with correct SMS segment costing | Rendering and cost test |
| AC-15 | The customer inbox contains every notification sent, in the portal and app | Reconciliation test |
| AC-16 | Customer Service Manager and Chief Data Officer sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Which telephony provider will carry hotline 16743, and what is the interconnect arrangement?** *(decision D-04)* | CTO / Customer Service Manager | **W4 minus 4 months** |
| Q-02 | **How does the Company obtain and refresh BTRC DND status for its customer base?** Is there an operator-provided feed, or must it rely on suppression at the aggregator? | CTO / Legal | **W4 minus 3 months** |
| Q-03 | What exactly is the prohibited overnight window, and does it differ by operator? | Legal / Marketing Head | W4 build |
| Q-04 | Is call recording mandatory for all calls, sampled, or by consent? What is the retention period? | Legal / CDO | **W4 build** |
| Q-05 | **Should the notification service (CD-051) move from W4 to W1?** Every module from W1 needs it. | CTO / PMO | **Before W1 build starts** |
| Q-06 | How many contact centre agents exist today, and is the 24/7 model staffed or on-call? | Customer Service Manager / HR | W4 minus 3 months |
| Q-07 | Which social channels are in scope — Messenger only, or also Instagram and IMO? | Marketing Head | W4 design |
| Q-08 | What is the mandatory transactional minimum that a customer cannot opt out of? | Legal / CCO | W4 build |

**Q-05 is a sequencing decision, not a design question**, and it should be taken before Wave 1
build begins.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §4 (M27/M32 boundary), §5 · `M32_Conversational_AI_and_Virtual_Assistant.md` ·
`M33_Customer_and_Party_Master_Management.md` · `M34_Customer_Experience_Feedback_and_Complaints.md` ·
`M35_Marketing_Campaigns_and_Demand_Generation.md` ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` *(see Q-05)*

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-CRM-004, §6.2 Process 10,
§7.3, §14.2 · `1000FiX_ERP_System_Comprehensive_URD.md` §14 ·
`1000fix_business/Business planning for 1000 fix.docx` §24/7 Technical Support ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Customer Support, §Inbox

**External benchmark and regulation** *(verified 2026-08-12)*
CCaaS practice — cloud voice and digital in a single AI-driven interface; **omnichannel routing
unifying every interaction into one data thread so history and intent follow the customer
across channel switches**; agent assistance through summaries, suggested replies and
next-best actions · Novu multi-channel notification infrastructure ·
WhatsApp Business Platform template and session-window rules ·
**BTRC Do Not Disturb service** for promotional messages; **prohibition on promotional SMS
from midnight to dawn**; masked and non-masked sender identity rules ·
**Bangladesh Personal Data Protection Act 2026** — lawful basis and notice for call recording
and for processing conversation data

---

*Module M27 · Category B · 1000FiX ERP System v2.0 · CONFIDENTIAL*
