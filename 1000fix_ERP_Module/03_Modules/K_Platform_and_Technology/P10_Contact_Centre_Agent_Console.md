---
id: FIX-ERP2-P10
portal_id: P10
portal_code: CCC
portal_name: Contact Centre Agent Console
type: Internal Web Application (omnichannel agent desktop)
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Customer Service Manager
system_owner: Digital Channels Squad
priority: P1
wave: W4
---

# P10 — Contact Centre Agent Console
### Portal Suite · Code `CCC` · ★ New in v2.1

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P10 |
| **Portal code** | `CCC` |
| **Type** | Internal web application — omnichannel agent desktop with embedded telephony |
| **Status** | ★ New in v2.1 — v1.0 had no agent surface; agents worked the admin portal with a separate phone |
| **Priority** | **P1** |
| **Delivery wave** | **W4** (Months 14–18) |
| **Users** | Contact centre agents, team leaders, quality analysts |
| **Volume** | **30–80 users** — 30–60 agents, 4–10 supervisors, quality analysts |
| **Business owner** | Customer Service Manager |
| **System owner** | Digital Channels Squad |
| **Technology** | Next.js 15 (React 19) with embedded CTI softphone · shared design system |
| **Custom development** | `CD-211` |
| **Requirement range** | FR-POR-283 … FR-POR-310 |
| **Requirement count** | **28** *(measured — supersedes the 6 allocation in `05-01` §4)* |
| **Effort estimate** | **22 person-weeks** |
| **Backing modules** | M01, M05, M07, M08, M09, M11, M17, M20, M23, M27, M32, M33, M34, M61 |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M65 Localisation |

---

## 2. Purpose

P10 is **the surface behind hotline 16743**. It is where 30–60 agents handle every voice call,
chat, WhatsApp message, email and SMS the Company receives, and where the customer experience
is decided in the moments when something has gone wrong.

Its design problem is stated precisely by its own KPI in `04-00`: **agent screen switches per
contact under 3**. An agent who must open four systems to answer one question is an agent whose
handling time is consumed by navigation rather than by the customer. Every capability in P10
exists to keep the agent in one place while the conversation is live.

P10 holds no authoritative state. The service order belongs to M01, the customer to M33, the
conversation to M27. What P10 owns is **the agent's working context** — the unified queue, the
screen pop, the ability to act without leaving, and the wrap-up that makes the contact
measurable.

### Why It Exists

**The contact centre absorbs the work every other channel does not complete.** P01 deflects
status enquiries; what remains reaches P10, and it is by definition the harder half. An agent
handling an escalation needs the whole picture immediately.

**Omnichannel is fragmented without a console.** The Company receives contacts by voice
(16743), WhatsApp, chat, email and SMS. Without a unified queue each channel is a separate
inbox with separate staffing and separate history, and a customer who chats then calls is
treated as two strangers.

**First-contact resolution is the economics.** `04-00` targets FCR above 78% and AHT down 25%.
Both are achieved by the same mechanism: the agent can see everything and do everything in one
place. A contact that must be escalated or called back costs several times the one resolved
live.

**Quality management has no surface.** Call recording, quality scoring, coaching and agent
feedback are how a contact centre improves. Without them, 30–60 agents perform at whatever level
they arrived at.

**The AI assistant needs a human fallback.** M32 handles routine enquiries in Bengali in P01.
Every escalation from it lands here with the conversation intact — or it lands here with the
customer repeating themselves, which is worse than no assistant at all.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-SRM-001 | Service orders created by phone — "manual entry by agent" — the console's core action |
| ERP BRD BR-CRM-001 | Unified customer record with device registry, service history, contracts, invoices and communication history — **the screen pop** |
| ERP BRD BR-CRM-004 | "Record and display communication history for each customer across all channels" |
| ERP BRD BR-CRM-008 | Complaint management with root cause classification and resolution tracking |
| ERP BRD BR-SRM-009 | Automated notifications at each milestone — reducing the calls that reach the agent |
| ERP BRD §4.1 Integrations | WhatsApp Business API, SMS gateway, AI chatbot (Rasa Bengali NLP) — the channels the console unifies |
| ERP BRD OOS-10 | "Business process outsourcing or call center platform" excluded — **P10 is the agent surface onto a CPaaS, not a contact-centre platform** |
| `04-00` §P10 | Capability set across ten areas and five KPIs, adopted verbatim |
| `04-00` §3 PS-01…PS-12 | Twelve cross-portal standards, all binding |
| `02-05` §5 L6 | Cloud telephony / CPaaS approved as an L6 commercial component — "carrier interconnect in Bangladesh requires a licensed provider" |
| `05-04` §1 | R34 Contact Centre Agent (30–60, P10 only), R35 Supervisor (4–10, P10 and P06) |
| `05-04` §5 | `call_recording_url` restricted to R35, R32 and R02 |
| Company Profile §Contact Information | Hotline 16743, phone, email and WhatsApp — the channels in scope |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The unified queue across voice, chat, WhatsApp, email, SMS and social |
| 2 | Agent presence, capacity and channel-mix management |
| 3 | Embedded softphone: answer, hold, transfer, conference, consult, mute, disposition |
| 4 | Automatic screen pop of the Customer 360 on identification |
| 5 | Cross-channel conversation history in one timeline |
| 6 | Contextual panel: open jobs, contracts, entitlements, invoices, dues, devices |
| 7 | Canned responses and knowledge search in Bengali and English |
| 8 | In-conversation action: create a service order, reschedule, quote, take payment, renew, raise a complaint |
| 9 | Navigation into P03 and back with the conversation intact |
| 10 | Remote support session launch with consent capture |
| 11 | AI assist: suggested responses, next-best-action, article recommendation, live transcription |
| 12 | Structured wrap-up: disposition coding, notes, follow-up task creation |
| 13 | Quality: recording playback, scoring forms, coaching notes, agent feedback |
| 14 | Supervision: live queue and agent status, service-level monitoring, barge-in and whisper |
| 15 | Bengali and English throughout, with Bengali default for agents |
| 16 | Instrumentation of AHT, FCR, screen switches and disposition completeness |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **The telephony platform, IVR, ACD, carrier interconnect and recording storage** | **L6 CPaaS** via **M27** | `02-05` §5 approves cloud telephony as a commercial component because carrier interconnect in Bangladesh requires a licensed provider. **P10 is the agent surface, not the platform** — and BRD OOS-10 excludes building one |
| **Routing rules, queue configuration, skills-based distribution** | **M27** Omnichannel Contact Centre & Communications | P10 presents the queue M27 routes |
| **Message templates, channel selection and delivery** | **M27** | P10 sends through M27; it owns no channel |
| **The AI assistant's model, intents and Bengali NLP** | **M32** Conversational AI | P10 embeds assist; M32 owns behaviour |
| **The customer-facing chat and assistant** | **P01** | P10 is the agent end of a conversation the customer holds in P01 |
| **Service order lifecycle, SLA and state machine** | **M01** | The agent creates and updates; M01 governs |
| **Customer and party master, deduplication and merge** | **M33** | The agent identifies; M33 resolves |
| **Device identity and history** | **M17** | Displayed, not owned |
| **Price, estimate, entitlement and contract terms** | **M11 / M08 / M36** | The agent quotes what the system returns |
| **Payment processing** | **M20** | The agent initiates; M20 processes |
| **Complaint classification, root cause and CAPA** | **M34 / M23** | The agent raises; the quality process runs elsewhere |
| **Workforce management, rostering and forecasting** | **M55** | P10 shows presence; M55 schedules |
| **Deep back-office work** | **P03** | Anything beyond the conversation is done in P03; P10 links there and back |
| **Identity, session policy and MFA** | **M29** | **PS-01** |

### 3.3 Shared Concepts

| Concept | P10's Role | Owning Module |
|---|---|---|
| The agent's working context | **Owns** — the defining concern of this console | P10 |
| Unified queue presentation | **Owns** the surface; M27 routes | P10 / M27 |
| Softphone control | Embeds the CPaaS SDK; M27 owns the platform | P10 / M27 / L6 |
| Conversation and its history | Presents; M27 owns the record | M27 |
| Customer 360 | Composes the view | M33, M17, M01, M08, M20 |
| Service order | Creates and updates in-conversation | M01 |
| Knowledge article | Searches and inserts | M61 |
| AI assist | Embeds | M32 |
| Disposition code | Captures; M27 owns the taxonomy | P10 / M27 |
| Quality score | Captures on the form; M23 owns the framework | P10 / M23 |
| Recording | Plays back; the CPaaS stores | M27 / L6 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Unified agent desktop practice (NovelVox, TTEC, Genesys, Amazon Connect)** | A **single pane** presenting interactions, customer context, knowledge, scripts and tools; embedded CTI softphone; 360° customer profile; knowledge search; dynamic scripting; AI agent assist with real-time transcription, suggestions and summarisation. Eliminating toggling between screens and systems delivers faster service and improves FCR | **The single-pane principle is the single most influential external reference for P10**, and it is expressed as a measurable target: **under 3 screen switches per contact**. Every design decision is tested against it. Also adopted: embedded CTI rather than a separate phone application, which is what makes screen pop possible at all | Building a contact-centre platform. BRD OOS-10 excludes it and `02-05` §5 approves a CPaaS. P10 is the desktop only |
| **CTI screen-pop practice** | Click-to-call and screen pop presenting customer history instantly on identification, reducing AHT and improving first-call resolution | **Screen pop on identification, with a fallback that does not stall the agent.** In Bangladesh a caller's number may not match a stored contact; the console must present a fast search rather than a blank screen when identification fails | Screen pop that blocks the answer until resolved |
| **Omnichannel queue practice** | One queue across voice, email, chat, SMS and social with priority and SLA visible; full interaction history in one unified timeline; smart routing with hold, transfer and mute controls | **One queue, one history, one agent.** A customer who chatted yesterday and calls today meets an agent who can see both, which is the difference between a service organisation and a set of channels | Social-media channel management as a marketing function; that is M35 |
| **Agent assist practice** | Suggested responses, next-best-action and article recommendation while the conversation is live; post-call summarisation | **Assist as suggestion, never as automation.** The agent decides; the assistant proposes. Also adopted: automatic summarisation into the wrap-up note, which is where handling time is genuinely recovered | Automated response sending without agent confirmation |
| **Quality management practice** | Recording playback, scoring forms, calibration, coaching notes and agent feedback loops | **Scoring with a coaching route and visible feedback to the agent.** A quality programme agents cannot see is a surveillance programme, and it produces defensive behaviour rather than improvement | Speech analytics on 100% of calls at this scale |
| **1000FiX-specific: Bengali-first agent work** | — | **Canned responses, knowledge and transcription in Bengali.** Agents handle Bengali conversations; an English-only knowledge base and English-only canned responses force translation on the fly, which is the largest hidden contributor to handling time in this operation | — |

**Design position.** Five deliberate differences from the benchmark.

First, **P10 is a desktop, not a platform.** The telephony, IVR, routing and recording sit with
a licensed CPaaS provider (L6) behind M27. This is a firm boundary: BRD OOS-10 excludes building
a contact-centre platform, and carrier interconnect in Bangladesh requires a licence the Company
does not hold. P10 embeds the provider's SDK and owns nothing below it.

Second, **screen switches are the governing metric.** Under 3 per contact. Where a capability
would require a fourth switch, it is either brought into the console or explicitly accepted as a
P03 hand-off with the conversation preserved. This single number drives the scope decisions.

Third, **the agent can act, not just look.** Create a service order, reschedule, quote, take
payment, renew a contract, raise a complaint — all without leaving the conversation. A console
that only displays forces every action into P03 and defeats its own purpose.

Fourth, **assist suggests; the agent decides.** No automated action is taken on a live
conversation without agent confirmation. The Bengali NLP is good but not infallible, and a
customer receiving an incorrect automated commitment is a worse outcome than a slower reply.

Fifth, **quality is visible to the agent.** Scores, the recordings behind them and the coaching
notes are shown to the agent whose work they describe. `04-00` targets agent satisfaction with
tooling above 4.2/5, and a quality system experienced as surveillance does not reach it.

---

## 5. Capability Areas & Functions

### 5.1 Queue, Presence & Telephony

| FR ID | Feature | Function — "The console shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-283 | Unified queue | Present one queue across voice, chat, WhatsApp, email, SMS and social, with channel, priority, SLA remaining and wait time visible on every item | **P0** | L5 |
| FR-POR-284 | Presence and capacity | Allow the agent to set presence and channel mix, and enforce the concurrency limits M27 defines per channel | **P0** | L5 |
| FR-POR-285 | Embedded softphone | Provide answer, hold, transfer, conference, consult, mute and hang-up within the console, through the CPaaS SDK, with no separate phone application | **P0** | L5/L6 |
| FR-POR-286 | Click to call | Initiate an outbound call from any customer or job record in the console, logged against the conversation | **P0** | L5 |
| FR-POR-287 | Transfer with context | Transfer or conference an interaction with the customer context, conversation history and notes carried to the receiving agent | **P0** | L5 |
| FR-POR-288 | Callback | Schedule a callback with a reason and an owner, and present it in the queue at the scheduled time | P1 | L5 |

### 5.2 Context: The Screen Pop

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-289 | **Screen pop** | Present the Customer 360 automatically on caller or contact identification, before the agent speaks (BR-CRM-001) | **P0** | L5 |
| FR-POR-290 | Identification fallback | Where identification fails, present a fast multi-field search — phone, name, device serial, job number — without blocking the answer | **P0** | L5 |
| FR-POR-291 | Cross-channel history | Present every prior interaction across all channels in one chronological timeline, with the content accessible (BR-CRM-004) | **P0** | L5 |
| FR-POR-292 | Contextual panel | Present open jobs with status and SLA, registered devices with warranty state, active contracts and entitlement, outstanding invoices and dues, and loyalty status — without navigating away | **P0** | L5 |
| FR-POR-293 | Device and job context | Open any device's history or job detail in a side panel, returning to the conversation without losing state | **P0** | L5 |
| FR-POR-294 | Identity verification | Present the verification steps required before a sensitive action, and record that verification was performed | **P0** | L5 |

### 5.3 Handling & Action

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-295 | Canned responses | Provide approved canned responses in **Bengali and English**, searchable, insertable and personalised with record fields | **P0** | L5 |
| FR-POR-296 | Knowledge search | Search the M61 knowledge base from within the conversation and insert an article link or extract | **P0** | L5 |
| FR-POR-297 | Attachments | Send and receive attachments on any channel that supports them, stored through M24 against the conversation | P1 | L5 |
| FR-POR-298 | **Create a service order** | Create a service order from within the conversation, with the customer, device and fault pre-filled from context (BR-SRM-001) | **P0** | L5 |
| FR-POR-299 | Reschedule and amend | Reschedule, amend or cancel an existing job within policy, without leaving the conversation | **P0** | L5 |
| FR-POR-300 | Quote and estimate | Present an indicative price or an existing estimate, and capture the customer's decision where they are entitled to give it | P1 | L5 |
| FR-POR-301 | Take payment | Initiate a payment on the call through M20, and confirm receipt to the customer before ending | P1 | L5 |
| FR-POR-302 | Contract renewal | Present a renewal quotation and capture acceptance within the conversation | P2 | L5 |
| FR-POR-303 | Raise a complaint | Raise a complaint with structured classification, routed to M34, with the reference given to the customer before the contact ends | **P0** | L5 |
| FR-POR-304 | Remote support launch | Launch a remote assistance session through M05 with the customer's consent captured and recorded | P2 | L5 |
| FR-POR-305 | Navigate to P03 and back | Open any P03 record in a linked context and return with the conversation, notes and timer intact | **P0** | L5 |

### 5.4 AI Assist & Wrap-Up

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-306 | AI assist | Present suggested responses, next-best-action and recommended articles while the conversation is live, from M32 — **as suggestions requiring agent confirmation, never as automatic action** | P1 | L5 |
| FR-POR-307 | Live transcription and summary | Transcribe voice conversations in Bengali and English where the provider supports it, and propose a wrap-up summary the agent edits and confirms | P2 | L5/L6 |
| FR-POR-308 | **Wrap-up** | Require structured disposition coding, a note and any follow-up task before the interaction closes, within the after-contact-work allowance | **P0** | L5 |

### 5.5 Quality & Supervision

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-309 | Quality management | Provide recording playback, scoring against a form, calibration across scorers, coaching notes, and **visibility of scores and coaching to the agent whose work is scored** | P1 | L5 |
| FR-POR-310 | Supervision | Present the supervisor a live view of queue state, agent status and service level, with barge-in and whisper on live calls, and the ability to reassign or escalate an interaction | **P0** | L5/L6 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No authoritative state** | P10 persists no business object; the conversation record belongs to M27 (`04-00` §1) |
| T-02 | **Not a telephony platform** | Telephony, IVR, ACD, routing and recording storage sit with the L6 CPaaS behind M27. P10 embeds an SDK and owns nothing below it (BRD OOS-10) |
| T-03 | **Screen-switch budget** | Under 3 screen switches per contact, measured in production. A capability requiring a fourth is redesigned or explicitly accepted as a P03 hand-off |
| T-04 | **Screen-pop latency** | The Customer 360 renders within 2 seconds of identification, and never blocks answering the interaction |
| T-05 | **Context preservation** | Navigating to P03 and back preserves the conversation, the notes, the timer and the wrap-up state without loss |
| T-06 | **Concurrency control** | Channel concurrency limits are enforced from M27's configuration, not implemented in the console |
| T-07 | **Recording access control** | `call_recording_url` is accessible only to R35, R32 and R02 (`05-04` §5); an agent cannot retrieve a recording, including their own, except within a scoring session shared with them |
| T-08 | **Consent capture** | Remote support consent and any recording notification are captured with a timestamp and retained per M24 policy |
| T-09 | **Assist is advisory** | No AI suggestion is sent or acted on without explicit agent confirmation; every accepted suggestion is logged as accepted |
| T-10 | **All traffic through the gateway** | Every ERP call routes through M28 (**PS-02**); CPaaS traffic is mediated by M27 |
| T-11 | **No client-side business logic** | Price, entitlement, SLA and eligibility come from their owning module (**PS-11**) |
| T-12 | **Bengali and English** | Complete interface, canned responses, knowledge and error messages in both; Bengali default for agent roles (**PS-03**) |
| T-13 | **Performance under load** | The console remains responsive with 80 concurrent agents and a full queue; queue updates arrive within 2 seconds |
| T-14 | **Resilience** | A CPaaS outage degrades P10 to non-voice channels with a clear indication, rather than making the console unusable (**PS-09**) |
| T-15 | **Session and MFA** | Session, idle timeout and MFA are M29 policy; R35 supervisors require MFA (**PS-12**) |
| T-16 | **Accessibility** | WCAG 2.1 AA with full keyboard operation — an agent on a call cannot reach for a mouse (**PS-04**) |
| T-17 | **Instrumentation** | AHT, FCR, screen switches, disposition completeness and assist acceptance instrumented to M25 (**PS-10**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Actor

| Actor | Today | With P10 |
|---|---|---|
| **Contact centre agent** | Answers on a desk phone, opens three systems, asks the customer to repeat everything | Answers in the console with the customer's whole picture already on screen |
| **Customer calling** | Explains who they are, what device, what happened, again | Is recognised, and the agent already knows |
| **Customer who chatted yesterday** | Starts over | Meets an agent who can see the chat |
| **Team leader** | Learns of a queue problem when complaints arrive | Sees live queue, agent status and service level, and intervenes |
| **Quality analyst** | Samples calls manually with no structured form | Scores against a form with playback, calibration and coaching |
| **Agent being coached** | Receives feedback with no evidence | Sees the score, the recording and the note |
| **Customer service manager** | Manages by anecdote and monthly summary | Manages AHT, FCR and disposition data continuously |
| **Escalated customer** | Repeats the whole history to the supervisor | Is transferred with context carried |
| **Field and branch teams** | Receive vague phone-created jobs | Receive structured jobs created with device and fault context |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Average handling time** | Screen pop, single pane, in-conversation action, assist and summarisation | `04-00` target: **AHT −25%**. Across 30–60 agents this is the equivalent of 8–15 agents of capacity released without hiring |
| **First-contact resolution** | The agent can see and do everything in one place | `04-00` target: **FCR > 78%**. Every unresolved contact generates a callback, a complaint or a repeat call |
| **Customer retention** | Recognition, continuity across channels, and resolution on first contact | Contributes to the **BDT 78 lac/year** retention benefit attributed to M07 + M10 + M27 |
| **Intake quality** | Phone-created jobs carry device identity and structured fault, like a P01 booking | Improves dispatch and first-time fix, supporting the **BDT 130 lac/year** productivity benefit |
| **Revenue capture on the call** | Payment taken, contract renewed, protection product sold while the customer is engaged | Supports AMC/RAMC uplift (**BDT 72 lac**) and cash-flow improvement (**BDT 26 lac**) |
| **Administrative labour** | Structured wrap-up replaces free-text notes and post-call re-keying | Contributes to the **BDT 62 lac/year** administrative saving |
| **Complaint capture quality** | Structured classification at the point of contact | Feeds M34 and M23 with data that supports genuine root-cause work |
| **Agent retention** | Better tooling reduces frustration in a role with high turnover | `04-00` target: **agent satisfaction with tooling > 4.2/5**. Turnover in this role is expensive and largely tooling-driven |
| **AI assistant value realised** | M32 escalations arrive with the conversation intact | Makes the Bengali assistant an asset rather than a step customers learn to bypass |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The hotline becomes a system, not a set of habits** | 16743 is a public commitment; a console makes its performance measurable and improvable |
| **Bengali as the working language of service** | Canned responses, knowledge and transcription in Bengali remove the hidden translation load agents carry today |
| **Coaching culture rather than monitoring culture** | Scores and recordings visible to the agent turns quality into development |
| **Customer memory** | A customer who is recognised across channels experiences an organisation rather than a switchboard |
| **Evidence in dispute** | Recordings, consents and dispositions provide a defensible record of what was said and agreed |
| **Data quality at the point of contact** | Structured disposition and complaint coding at source is the only place this data can be captured accurately |
| **Scalability** | Adding agents is a licence and a training exercise, not an operational redesign |

---

## 8. Journeys & State Models

### 8.1 The Contact — measured in screen switches

```
   INTERACTION ARRIVES (voice · chat · WhatsApp · email · SMS · social)
        │  routed by M27 · CPaaS delivers to the agent's console
   ┌────▼──────────────────────────────────────────────────┐
   │  SCREEN POP — Customer 360, within 2 seconds           │
   │   identity · devices · open jobs · contracts ·         │
   │   entitlement · invoices and dues · loyalty ·          │
   │   cross-channel history                                │
   │                                                        │
   │   identification failed? → fast multi-field search;    │
   │   the agent still answers immediately                  │
   └────┬──────────────────────────────────────────────────┘
        │            SCREEN SWITCH BUDGET: < 3 per contact
   ┌────▼──────────────────────────────────────────────────┐
   │  HANDLE — in the console, without leaving:             │
   │   ▸ knowledge search · canned response (Bengali)       │
   │   ▸ create service order · reschedule · quote          │
   │   ▸ take payment · renew contract · raise complaint    │
   │   ▸ launch remote session (consent captured)           │
   │   ▸ AI assist SUGGESTS; the agent decides              │
   │                                                        │
   │   deep back-office work → P03 in linked context →      │
   │   return with conversation, notes and timer intact     │
   └────┬──────────────────────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────────────────────┐
   │  WRAP-UP (within the after-contact-work allowance)     │
   │   ✓ structured disposition code (mandatory)            │
   │   ✓ note — AI-proposed summary, agent-edited           │
   │   ✓ follow-up task where required                      │
   └────┬──────────────────────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────────────────────┐
   │  CLOSED → conversation written to M27 → available on   │
   │  the customer's timeline in P01 and to the next agent  │
   └───────────────────────────────────────────────────────┘
```

| Stage | Target | Why it is measured |
|---|---|---|
| Screen pop | ≤ 2 s, never blocking | The agent must not be reading while the customer is speaking |
| Handle | < 3 screen switches | The `04-00` KPI; navigation is the largest avoidable component of AHT |
| Resolution | FCR > 78% | An unresolved contact costs several times a resolved one |
| Wrap-up | 100% disposition coded | An uncoded contact is invisible to every improvement effort |

### 8.2 Escalation and Transfer — context must travel

```
   AGENT holds an interaction they cannot resolve
        │
   ┌────▼──────────────────┬──────────────────┬─────────────────┐
   │  CONSULT              │  TRANSFER        │  ESCALATE       │
   │  (agent stays on)     │  (agent leaves)  │  (to supervisor)│
   └────┬──────────────────┴────────┬─────────┴────────┬────────┘
        │                           │                  │
        └───────────────────────────┴──────────────────┘
                         │
   ┌─────────────────────▼──────────────────────────────┐
   │  CONTEXT TRAVELS WITH THE INTERACTION:              │
   │   ▸ Customer 360 state                              │
   │   ▸ full conversation content so far                │
   │   ▸ the agent's notes and what has been tried       │
   │   ▸ any action already taken                        │
   │                                                     │
   │  ✖ The customer NEVER repeats what they have said   │
   └─────────────────────────────────────────────────────┘
```

> **The rule.** A transfer that requires the customer to start again is a failed transfer, and it
> is instrumented as such. This is the single most common contact-centre failure and it is
> entirely preventable in a unified console.

---

## 9. Portal Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P10-01 | P10 is an agent desktop; it implements no telephony platform, routing engine or recording store (BRD OOS-10) | **H** | CTO |
| PRU-P10-02 | P10 persists no authoritative business state; the conversation record belongs to M27 | **H** | CTO |
| PRU-P10-03 | Screen pop never blocks answering; where identification fails, the agent answers and searches | **H** | Customer Service Manager |
| PRU-P10-04 | A transfer, consult or escalation carries the full context; the customer never repeats what they have said | **H** | Customer Service Manager |
| PRU-P10-05 | Every interaction requires a structured disposition code before it closes | **H** | Customer Service Manager |
| PRU-P10-06 | An AI suggestion is never sent or acted on without explicit agent confirmation | **H** | Customer Service Manager |
| PRU-P10-07 | `call_recording_url` is accessible only to R35, R32 and R02; an agent cannot retrieve a recording outside a scoring session shared with them (`05-04` §5) | **H** | CTO |
| PRU-P10-08 | Quality scores and coaching notes are visible to the agent whose work they describe | **C** | Customer Service Manager |
| PRU-P10-09 | Remote support consent is captured with a timestamp before any session is launched | **H** | Legal |
| PRU-P10-10 | Identity verification is performed and recorded before any sensitive action on a customer's account | **H** | CTO |
| PRU-P10-11 | An agent may act only within their role's authority; approvals above it route through P03 | **H** | Customer Service Manager |
| PRU-P10-12 | No price, entitlement, SLA or eligibility value is computed in the console (**PS-11**) | **H** | CTO |
| PRU-P10-13 | Every screen, canned response, knowledge extract and error exists in Bengali; Bengali is the default for agent roles | **H** | Customer Service Manager |
| PRU-P10-14 | A CPaaS outage degrades P10 to non-voice channels with a clear indication; the console remains usable (**PS-09**) | **H** | CTO |
| PRU-P10-15 | Channel concurrency limits are enforced from M27's configuration, not the console | **C** | Customer Service Manager |
| PRU-P10-16 | Barge-in and whisper are available to supervisors only, and every use is logged | **H** | Customer Service Manager |
| PRU-P10-17 | Screen switches per contact are instrumented; a capability that pushes a contact past three is redesigned or explicitly accepted | **C** | Customer Service Manager |

---

## 10. Data, Caching & State Model

### 10.1 What P10 Holds

| Object | Purpose | Ownership |
|---|---|---|
| Console layout and panel configuration | Which panels an agent sees, in what arrangement | **P10** |
| Agent personal preferences | Panel order, canned-response favourites, shortcut map | **P10** |
| **In-flight interaction context** | The live conversation's assembled state, notes and timer — held until wrap-up completes | **P10**, transient |
| Draft wrap-up | Recovery if the console is closed mid-wrap-up | **P10**, transient |
| Quality scoring drafts | Scorer's in-progress form | **P10**, transient |

### 10.2 Never Held

| Item | Reason |
|---|---|
| The conversation record | M27 owns it |
| Call recordings | The CPaaS stores them; P10 streams under access control |
| Any business object — customer, job, invoice, contract | `04-00` §1 |
| Routing rules or queue configuration | M27 owns them |
| Pricing, entitlement or eligibility logic | PRU-P10-12 |
| Another agent's interactions or scores | Role scoping |

### 10.3 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.conversation`, interaction, channel history | **M27** | Read; write messages and disposition |
| `fix.party`, contacts, preferences, consent | M33 | Read; update within authority |
| `fix.asset`, device history, warranty | M17 | Read |
| `fix.service.order` | M01 | Create; update within policy |
| `fix.estimate` | M01 / M36 | Read; capture decision |
| `fix.contract`, entitlement | M08 | Read; initiate renewal |
| `fix.invoice`, dues, payment | M20 | Read; initiate payment |
| `fix.loyalty.balance` | M10 | Read |
| `fix.complaint` | M34 | Create |
| `fix.knowledge.article` | M61 | Search; insert |
| `fix.qc.record` / quality form | M23 | Capture scores |
| `fix.monitored.asset`, remote session | M05 | Launch |
| Call recording | L6 CPaaS via M27 | Stream, access-controlled |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P10-01 | Interaction routed to an agent | Identify the contact and pop the Customer 360 within 2 seconds | Present the search panel; **never block the answer** |
| AUT-P10-02 | Identification ambiguous — several matching parties | Present ranked candidates for the agent to confirm, with enough detail to distinguish them | Present search |
| AUT-P10-03 | Interaction accepted | Start the handling timer and begin assembling context in the background | Timer starts regardless |
| AUT-P10-04 | Agent requests a transfer, consult or escalation | Package and carry the full context — 360 state, conversation, notes, actions taken | Block the transfer rather than send it context-less |
| AUT-P10-05 | Conversation content available | Provide M32 suggestions, next-best-action and article recommendations continuously as advisory only | Assist unavailable; console fully usable |
| AUT-P10-06 | Interaction ends | Enter wrap-up, propose an AI summary for editing, and require a disposition code before close | Interaction stays in wrap-up; agent unavailable until complete |
| AUT-P10-07 | Wrap-up exceeds the after-contact-work allowance | Notify the agent, then the supervisor | Notify only |
| AUT-P10-08 | Follow-up task created at wrap-up | Route to the owning module and surface it on the agent's or the branch's queue | Task created; routing retried |
| AUT-P10-09 | Complaint raised | Create it in M34, generate the reference, and present it to the agent to give the customer **before the contact ends** | Block close pending the reference |
| AUT-P10-10 | Sensitive action attempted without recorded verification | Block and prompt for identity verification | Hard block |
| AUT-P10-11 | Queue service level breached | Alert the supervisor with the queue, the wait time and the available agents | Alert only |
| AUT-P10-12 | CPaaS unavailable | Mark voice unavailable with a clear indication, keep non-voice channels working, and alert M30 and the supervisor | Fail visible; console remains usable |
| AUT-P10-13 | Quality score completed | Publish it and the coaching note to the scored agent, and add it to their trend | Score recorded; publication retried |
| AUT-P10-14 | Screen switches on a contact exceed three | Record it against the interaction type for design review | Record only |

---

## 12. Module Interfaces

### 12.1 Modules P10 Consumes

| Module | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, session, MFA for supervisors | OIDC via gateway |
| M28 Integration Platform | Every ERP call | Gateway |
| **M27 Contact Centre & Communications** | **The queue, routing, conversation record, channel delivery, disposition taxonomy, CPaaS mediation** | REST + WebSocket |
| M33 Party Master | Customer identity, contacts, preferences, consent | REST |
| M17 Asset Registry | Devices, history, warranty state | REST |
| M01 Service Order | Job creation, status, reschedule, estimate | REST |
| M08 Contracts | Contract, entitlement, renewal quotation | REST |
| M20 Receivable | Invoices, dues, payment initiation | REST |
| M11 Pricing | Indicative price and quotation values | REST |
| M09 Warranty | Warranty status and claim state | REST |
| M10 Loyalty | Tier, points, vouchers | REST |
| M34 Customer Experience | Complaint creation and classification | REST |
| M61 Knowledge | Article search and extract | REST |
| **M32 Conversational AI** | Suggested responses, next-best-action, transcription, summary | Embedded SDK |
| M05 Managed Services | Remote session launch | REST |
| M23 Quality | Quality scoring forms and framework | REST |
| M55 Workforce | Roster and adherence context | REST |
| **L6 CPaaS** *(via M27)* | Softphone SDK, call control, recording stream, barge-in and whisper | Embedded SDK |

### 12.2 What P10 Writes Back

| Target | What | Mechanism |
|---|---|---|
| M27 | Messages sent, disposition codes, notes, interaction outcomes | Command |
| M01 | Service orders created; reschedules and amendments | Command |
| M33 | Contact and preference updates; consent capture | Command |
| M20 | Payment initiation | Command |
| M08 | Contract renewal acceptance | Command |
| M34 | Complaints with structured classification | Command |
| M23 | Quality scores and coaching notes | Command |
| M05 | Remote session initiation with consent reference | Command |
| M24 | Attachments and consent records | Upload |
| M25 / M62 | AHT, FCR, screen switches, disposition completeness, assist acceptance | Event stream |

### 12.3 Events P10 Consumes

| Event | Source | Effect in P10 |
|---|---|---|
| `interaction.routed` | M27 | Deliver to the agent; trigger screen pop |
| `interaction.transferred` | M27 | Receive with the carried context |
| `queue.sla_breached` | M27 | Alert the supervisor view |
| `service_order.status_changed` | M01 | Refresh the contextual panel |
| `payment.received` | M20 | Confirm to the agent during the call |
| `assist.suggestion_available` | M32 | Present as advisory |
| `cpaas.degraded` | M27 / L6 | Mark voice unavailable; keep other channels |
| `complaint.reference_issued` | M34 | Present the reference to give the customer |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P10-01 | **L6 cloud telephony / CPaaS** | Bidirectional | Softphone, call control, IVR hand-off, recording, barge-in and whisper on hotline 16743. **Licensed provider — `02-05` §5** |
| INT-P10-02 | WhatsApp Business API | Bidirectional | WhatsApp conversations in the unified queue; via M27 |
| INT-P10-03 | SMS gateway (Bangladesh) | Bidirectional | SMS conversations and notifications; via M27 |
| INT-P10-04 | Email | Bidirectional | Email interactions in the queue; via M27 |
| INT-P10-05 | Social channels | Bidirectional | Social messages in the queue; via M27 |
| INT-P10-06 | Rasa 3.6 Bengali NLP / M32 | Bidirectional | Assistant escalation with conversation intact; assist suggestions |
| INT-P10-07 | Agent headsets and telephony peripherals | Local | Voice hardware |

### 12.5 API Surface Consumed

| Endpoint | Method | Purpose | Owner |
|---|---|---|---|
| `/api/v1/contact/queue` | GET/WS | Unified queue with priority and SLA | M27 |
| `/api/v1/contact/interactions/{id}` | GET/PATCH | Interaction state, content, transfer | M27 |
| `/api/v1/contact/presence` | POST | Agent presence and channel mix | M27 |
| `/api/v1/contact/disposition` | POST | Structured wrap-up | M27 |
| `/api/v1/customer-360/{partyId}` | GET | **The screen-pop payload — one call, one round trip** | Composed via M28 |
| `/api/v1/parties/search` | GET | Multi-field identification fallback | M33 |
| `/api/v1/service-orders` | POST | Create from the conversation | M01 |
| `/api/v1/service-orders/{id}/reschedule` | POST | Reschedule within policy | M01 |
| `/api/v1/payments/initiate` | POST | Take payment on the call | M20 |
| `/api/v1/contracts/{id}/renew` | POST | Renewal acceptance | M08 |
| `/api/v1/complaints` | POST | Raise with classification; return the reference | M34 |
| `/api/v1/knowledge/search` | GET | In-conversation knowledge search | M61 |
| `/api/v1/assist/suggestions` | WS | Live suggestions and next-best-action | M32 |
| `/api/v1/quality/scores` | POST/GET | Scoring, coaching, agent visibility | M23 |
| `/api/v1/contact/recordings/{id}` | GET | Access-controlled recording stream | M27 / L6 |

> **`customer-360` is a composed endpoint, deliberately.** The screen pop must be one round
> trip, not eleven. M28 composes it from M33, M17, M01, M08, M20, M09, M10 and M27 behind a
> single gateway call with a 2-second budget.

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R34 Contact Centre Agent** | C R U | **Customer-facing scope** — queue, interactions, Customer 360, in-conversation actions within authority. **P10 only**; no P03 access |
| **R35 Contact Centre Supervisor** | C R U A | **Own team and queues** — all agent capability plus live supervision, barge-in, whisper, reassignment, quality scoring. Also holds P03 and P06 |
| R32 Quality Manager / ISO Coordinator | R U | Quality scoring, calibration, recording playback across teams |
| R13 Remote Support Engineer | C R U | Assigned clients — the console for remote support conversations (per `05-04` §2) |
| R02 Chief Technology Officer | R | Recording access for audit purposes only |

> **Per `05-04` §2, P10 access is held by R13, R34, R35 and R32.** No external party has any
> access. **No impersonation of a customer exists**; an agent acting for a customer does so
> under their own identity and the audit trail says so.

**Field-level restrictions.** `call_recording_url` is visible to **R35, R32 and R02 only**
(`05-04` §5). An agent cannot retrieve a recording, including their own, except within a scoring
session a supervisor has shared with them. `unit_cost` and `margin` are not visible to R34 or
R35. `nid_number` and `bank_account` are not exposed in the console. `internal_note` is visible
to internal roles and never read aloud as customer-facing content by design of the panel.

**Authority.** An agent acts within their role's authority — discount ≤ 10% per `05-04` §7,
reschedule within policy, payment initiation, complaint raising. Anything above routes to a
supervisor or into P03 for an authorised role. The console shows the limit before the action,
not after it fails.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Average handling time** | Talk, hold, wrap-up and total, by channel, contact reason and agent — the `04-00` −25% KPI | M27, M25 |
| **First-contact resolution** | Contacts resolved without callback, transfer or repeat within the window — the `04-00` > 78% KPI | M27, M25 |
| **Screen switches per contact** | Navigations away from the console per interaction — the `04-00` < 3 KPI | M25 — **the design-governing metric** |
| **Disposition completeness** | Interactions closed with a structured code — the `04-00` 100% KPI | M27 |
| **Agent satisfaction with tooling** | Periodic survey — the `04-00` > 4.2/5 KPI | HR, Customer Service Manager |
| Screen-pop performance | Identification success rate, pop latency, fallback search usage | M25, M33 |
| Contact reason distribution | What customers actually contact about, by channel — the input to deflection design in P01 | M25, CCO |
| Transfer quality | Transfers with context carried; customer-repeat incidents | M27 |
| Assist effectiveness | Suggestions offered, accepted, edited, ignored — suggestions routinely ignored are removed | M32, M25 |
| Knowledge usage | Articles searched, inserted, and searches returning nothing | M61 |
| In-conversation actions | Orders created, payments taken, renewals accepted, complaints raised | M01, M20, M08, M34 |
| Quality | Scores by dimension, calibration variance between scorers, coaching completion | M23 |
| Queue health | Service level, abandonment, wait time, occupancy by channel and interval | M27, M55 |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| — | **Average handling time** | baseline established at W4 | −15% | **−25% vs baseline** |
| — | **First-contact resolution** | unmeasured | 70% | **> 78%** |
| — | **Agent screen switches per contact** | unmeasured | < 4 | **< 3** |
| — | **Disposition coding completeness** | ~0% | 95% | **100%** |
| — | **Agent satisfaction with tooling** | unmeasured | > 3.9/5 | **> 4.2/5** |
| — | Screen-pop success rate on identification | n/a | 82% | **> 92%** |
| — | Screen-pop latency (p95) | n/a | ≤ 2.5 s | **≤ 2 s** |
| — | Transfers requiring the customer to repeat | unmeasured | < 8% | **< 2%** |
| — | Contacts resolved without opening P03 | n/a | 65% | **> 80%** |
| — | Complaints issued a reference before the contact ends | unmeasured | 95% | **100%** |
| — | AI assist suggestions accepted | n/a | 30% | **> 45%** |
| — | Bengali canned-response coverage | n/a | **100%** | **100%** |
| — | Quality scores published to the scored agent | 0% | **100%** | **100%** |
| — | Recording access outside permitted roles | n/a | **0** | **0** |
| **KPI-004** *(supported)* | First-time fix rate — via better phone intake | 72% | 82% | **88%** |

> **Register note.** The first five metrics are adopted verbatim from `04-00` §P10. P10 has
> **no KPI-0nn identifiers allocated**; all fourteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action.
>
> **Baseline note.** The AHT −25% target is against a baseline that does not yet exist.
> Establishing it in Wave 4, before the console changes behaviour, is a deliverable — a
> reduction target without a measured baseline is not a commitment.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L5 | **Next.js 15 console** — unified queue, screen pop, contextual panels, in-conversation actions, wrap-up, quality and supervision | 68% |
| L6 | **CPaaS softphone SDK** — call control, recording, barge-in and whisper (licensed provider, `02-05` §5) | 14% |
| L5 | Composed `customer-360` endpoint and context-preserving P03 linkage | 10% |
| L4 | Shared design system; M32 assist SDK embed | 8% |

> **Boundary position.** P10 is one of only two portals with an L6 component, and the dependency
> is unavoidable: carrier interconnect in Bangladesh requires a licensed provider. The console
> is built so the CPaaS is replaceable — call control is abstracted behind an interface, and a
> provider change is an adapter, not a rebuild.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-211** | `p10_agent_console` — unified queue and presence, embedded softphone integration, **screen pop with composed Customer 360 and identification fallback**, contextual panels, canned responses and knowledge in Bengali, in-conversation actions (order, reschedule, quote, payment, renewal, complaint), context-preserving P03 linkage, AI assist embed, structured wrap-up with AI summary, quality scoring with agent visibility, supervisor live view with barge-in and whisper | Next.js 15 application | 22 PW |

> **CD register.** One ID, **CD-211**, claimed following CD-210 (P09). All CD IDs remain
> provisional pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M27 Contact Centre & Communications** | The queue, routing, conversation record and channel delivery. **W4 — P10 and M27 are delivered together** |
| **L6 CPaaS provider** | Contracted, integrated and tested. **Procurement must complete before build starts** |
| M29 Identity & Security | Agent identity, supervisor MFA, recording access control |
| M28 Integration Platform | The composed `customer-360` endpoint is a gateway capability |
| M33 Party Master | Identification and the 360 view (W1) |
| M17 Asset Registry | Devices and history in the 360 (W2) |
| M01 Service Order | In-conversation order creation (W1–W2) |
| M20 Receivable | Payment on the call (W3) |
| M08 Contracts | Entitlement and renewal (W4) |
| M34 Customer Experience | Complaint raising (W4) |
| M61 Knowledge | Knowledge search (W6) — **console ships with canned responses; knowledge search follows** |
| **M32 Conversational AI** | Assist and escalation with context (W4) |
| M23 Quality | Scoring framework (W5) — **quality module follows in W5** |

**Phasing within the portal.** W4 ships the queue, softphone, screen pop, contextual panels,
in-conversation actions and wrap-up. W5 adds quality scoring and supervision depth. W6 adds
knowledge search and transcription.

### 16.4 Adoption

| Activity | Scope | Wave |
|---|---|---|
| AHT and FCR baseline measurement | Before the console changes behaviour | **W4, first** |
| Agent training | All agents, in Bengali, on real contacts | W4 |
| Supervisor and quality-analyst training | Scoring, calibration, coaching | W5 |
| Calibration sessions | Scorers aligned before scores are used for coaching | W5 |
| Deflection loop | Contact-reason data fed back to P01 to remove the reasons | W5 onward |

> **Adoption position.** Establishing the AHT and FCR baseline **before** the console is
> deployed is the first deliverable, not an afterthought. Every other target in this
> specification is expressed against it, and it cannot be reconstructed later.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The Customer 360 pops within 2 seconds of identification and never blocks answering | Timed test across 200 inbound contacts |
| AC-02 | Where identification fails, the agent answers immediately and reaches the customer by multi-field search in under 15 seconds | Scripted unidentified-caller scenario |
| AC-03 | Screen switches per contact fall below 3 for the top ten contact reasons | Production instrumentation over 30 days |
| AC-04 | An agent can create a service order, reschedule, take payment, renew a contract and raise a complaint without leaving the conversation | Task-completion test per action |
| AC-05 | A transfer, consult or escalation carries the full context, and the customer does not repeat what they have said | Scripted transfer scenarios with observation |
| AC-06 | Navigating to P03 and back preserves the conversation, notes, timer and wrap-up state | State-preservation test |
| AC-07 | An interaction cannot close without a structured disposition code | Negative test |
| AC-08 | A complaint reference is generated and presented before the contact ends | Scripted complaint scenario |
| AC-09 | No AI suggestion is sent or acted on without explicit agent confirmation | Negative test on the assist path |
| AC-10 | `call_recording_url` is inaccessible to R34 and to any role outside R35, R32 and R02 | Access-control negative test |
| AC-11 | Remote support consent is captured with a timestamp before any session launches | Scripted scenario with M05 |
| AC-12 | A sensitive action is blocked until identity verification is recorded | Negative test |
| AC-13 | An agent cannot exceed their authority; the limit is shown before the action | Negative test at each authority boundary in `05-04` §7 |
| AC-14 | With the CPaaS unavailable, voice is marked unavailable and non-voice channels continue working | Chaos test on the CPaaS integration |
| AC-15 | The console remains responsive with 80 concurrent agents and a full queue, with queue updates within 2 seconds | Load test |
| AC-16 | Every screen, canned response and error renders in Bengali, and Bengali is the default for agents | Translation coverage report |
| AC-17 | The console is fully operable by keyboard | Keyboard-only task completion test |
| AC-18 | Quality scores and coaching notes are published to the scored agent | Scoring workflow test |
| AC-19 | Barge-in and whisper are available to supervisors only and every use is logged | Access test and log review |
| AC-20 | The AHT and FCR baseline is measured and signed off before the console is deployed | Signed baseline record |
| AC-21 | AHT falls 25% and FCR exceeds 78% against that baseline | Six consecutive monthly reports |
| AC-22 | Customer Service Manager, one supervisor and agent representatives sign off UAT, conducted in Bengali on real contacts | Signed UAT record |

**Definition of done:** the twelve cross-portal standards in `04-00` §3 plus the 22 criteria
above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Which CPaaS provider is contracted, on what terms, and does their SDK support embedded softphone, barge-in, whisper and recording streaming?** The console cannot be built against an unknown platform | CTO / Customer Service Manager / CFO | **W4 minus 6 months** |
| Q-02 | What is the current AHT and FCR baseline? Without measurement before deployment, the −25% target is unverifiable | Customer Service Manager | **W4, before deployment** |
| Q-03 | What is the disposition code taxonomy, and who owns it? A taxonomy designed badly produces 100% coding compliance and no usable data | Customer Service Manager / M27 owner | **W4 design** |
| Q-04 | Is call recording consent required by Bangladesh law for inbound calls, and what announcement is mandated? | Legal | **W4 design** |
| Q-05 | What identity verification is required before which sensitive actions? | Legal / CCO / CTO | W4 design |
| Q-06 | What channel concurrency does an agent handle — one voice, or voice plus two chats? This drives staffing and console design | Customer Service Manager | W4 design |
| Q-07 | Does the M32 Bengali NLP support live transcription at usable accuracy, or is transcription deferred? | CTO / Customer Service Manager | W6 scoping |
| Q-08 | What is the after-contact-work allowance, and is it enforced or advisory? | Customer Service Manager | W4 design |
| Q-09 | Who owns Bengali canned-response content, and how is it kept current? *(Related to P01 Q-11 — the same content function should serve both)* | Customer Service Manager / Marketing Head | **W4 minus 3 months** |
| Q-10 | Are quality scores an input to agent incentives, or to coaching only? *(The same question as P02 Q-... and M46 Q-12 — the Company should answer it once)* | HR Director / Customer Service Manager | **W4 design** |
| Q-11 | Do remote support engineers (R13) need the full console, or a reduced surface? | Corporate Services Head / CTO | W4 design |
| Q-12 | How does the console handle a customer who reaches an agent while an M32 assistant session is open in P01 — is the assistant suspended, and does its transcript transfer? | Customer Service Manager / CTO | W4 design |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §P10, §1, §3 PS-01…PS-12, §4 ·
`P01_Customer_Self_Service_Portal_and_Mobile_Application.md` (the customer end of the same
conversations; deflection target) ·
`P03_Admin_Operations_Portal.md` (**context-preserving hand-off destination**) ·
`P06_Analytics_and_Executive_Dashboard.md` (supervisor analytics) ·
`03_Modules/B_Customer_Engagement_and_Experience/M27_Omnichannel_Contact_Centre_and_Communications.md` ·
`03_Modules/B_Customer_Engagement_and_Experience/M33_Customer_and_Party_Master_Management.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` ·
`03_Modules/F_Asset_Equipment_and_Facilities/M17_Device_and_Customer_Asset_Registry.md` (360 device context) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §5, §10 ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5 (**L6 cloud telephony / CPaaS**) ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md`
§1 (R34, R35), §2, §5 (**`call_recording_url`**), §7 (agent authority limits)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.1 (integrations:
WhatsApp Business API, SMS gateway, Rasa Bengali NLP), **§4.2 OOS-10** (contact-centre platform
excluded), BR-SRM-001, BR-SRM-009, BR-CRM-001, BR-CRM-004, BR-CRM-008 ·
`1000FiX_Services_Company_Profile.md` §Contact Information (hotline 16743, WhatsApp)

**External benchmark**
[Unified agent desktop — single pane with interactions, context, knowledge, scripts, embedded CTI and AI assist](https://www.novelvox.com/unified-agent-desktops/) ·
[Genesys agent desktop capabilities](https://www.novelvox.com/unified-agent-desktops/genesys-agent-desktop/) ·
[Agent desktop for Amazon Connect](https://www.ttecdigital.com/solutions/agent-desktop-for-amazon-connect) ·
[Genesys CTI integration — click-to-call and screen pop reducing AHT and improving FCR](https://www.3clogic.com/products/genesys-call-center-cti-integration) ·
[Contact centre technology stack reference 2026](https://medium.com/@voiso/contact-center-technology-stack-e2825b906db3) ·
[Zendesk and Amazon Connect CTI integration patterns](https://www.novelvox.com/integrations/amazon-connect-zendesk-cti/) ·
[Enterprise UI design principles](https://hashbyt.com/blog/enterprise-ui-design)

---

*Portal P10 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
