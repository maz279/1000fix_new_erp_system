---
id: SP-034
title: Call and Conversation Script Library
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Contact Centre
author: Business Process Lead with Contact Centre Operations and Content Design
reviewers: [CCO, Contact Centre Supervisors, Content Design Lead, Localisation Lead, Legal Counsel, Data Protection Officer, Quality Manager]
approver: Chief Commercial Officer
content_class: C
purpose: >
  First-contact resolution is to reach 78% and average handling time is to fall 25%; scripts are
  the primary lever on both. This library holds the contact-centre scripts for enquiry, booking,
  status, complaint, retention, collection and escalation, in Bengali and English, with the
  consent, disclosure and liability wording that Legal requires and the agents cannot be expected
  to improvise on a live call.
traces_to: [M27, M32, M34, P10, P01, NT-002, NT-019, BN-017, MD-026, MD-028, SP-004, SP-005, SP-013, SP-028, SP-033]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: SP-034_Call_and_Conversation_Script_Library_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M27_Omnichannel_Contact_Centre_and_Communications.md — SOD-19/SOD-35, a supervisor cannot evaluate their own handled conversations
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-025 status enquiries deflected 60–80%, KPI-026 AI first-contact resolution, KPI-027 first-contact resolution all channels 70–78%
    verified: 2026-08-15
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md §5 — spoken Bengali has a different rhythm from written translated Bengali; a translated script sounds wrong on a call
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P10_Contact_Centre_Agent_Console.md
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.2.1 customer communication, and clause 9.1.2 customer satisfaction
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# Call and Conversation Script Library

| Item | Value |
|---|---|
| SOP ID | `SP-034` |
| Process owner | Chief Commercial Officer; executed under Contact Centre Supervisors (R35) |
| Roles performing | `R34` Contact Centre Agent (30–60) · `R35` Contact Centre Supervisor · `R08` Service Centre Agent (counter variants) · `M32` AI assistant |
| Systems used | `P10` Contact Centre Agent Console · `P03` · `M27` · `M32` |
| Frequency / volume | Continuous, across voice, chat, email, WhatsApp and social, for 250,000+ customers a month |
| ISO 9001 clause reference | **8.2.1** customer communication · 9.1.2 customer satisfaction · 7.5.3 documented information |

> **Bengali is authored, not translated.** `CG-010` §5 records that spoken Bengali has a different
> rhythm from written translated Bengali, and a translated script sounds wrong on a call. The
> Bengali scripts in this library are **written in Bengali by a Bengali speaker for speech**, then
> checked for equivalence against the English — not the other way round. This is the single most
> important production rule in this file.

---

## 1. Purpose and Outcome

**Purpose.** To give agents a reliable spine for every common conversation — what to say, in what
order, what must be said for legal or consent reasons, and where the conversation is allowed to
leave the script — so that customers get consistent, competent answers and agents are not
improvising liability.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| First-contact resolution reaches 78% | `KPI-027` |
| Average handling time falls 25% | Contact centre reporting |
| Mandatory disclosures are made on every applicable call | Quality monitoring |
| Agents do not commit to dates, prices or liabilities they cannot | Quality monitoring |
| The Bengali script sounds natural in speech | Linguistic sign-off (`BN-018`, `BN-017`) |
| Complaints arising from what an agent said fall | `SP-028` cause analysis |

---

## 2. Scope

**Applies to:** agent-led conversations on voice, chat, email, WhatsApp and social, and the
conversational flows the AI assistant uses (`M32`) — for enquiry, booking, status, estimate
approval, complaint, retention, collection, and escalation handover.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Notification and message templates sent by the system | `NT-*` category |
| IVR menu wording and voice prompts | `NT-019`, `BN-017` |
| UI copy in the console itself | `UI-020` |
| The counter greeting and intake conversation | `SP-007` §5.1, which this library supplies variants for |
| The technical diagnostic path within a call | `SP-033` remote triage trees |
| Complaint investigation and redress | `SP-028`; this library supplies the wording |
| Marketing outbound campaigns | `NT-023`, subject to consent (`NT-002`) |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Script | A structured conversation guide with mandatory, recommended and optional elements |
| Mandatory element | Wording that must be said — consent, disclosure, liability, identity verification |
| Spine | The ordered structure of the conversation, which is fixed |
| Flex | The wording within a step, which the agent may adapt to the customer |
| Deflection | Resolving without escalation or a visit — the FCR objective |
| Handover | Passing a conversation to another person or channel with context intact |
| Hold statement | What is said before placing a customer on hold, and on return |
| AI flow | The same conversation performed by `M32`, with the same mandatory elements |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Customer and order data available to the agent | `P10` | An agent asking questions the system already answers destroys AHT and trust |
| Consent and preference position | `NT-002` | What the customer has agreed to receive |
| SLA bands and current promises | `MD-028` | Agents must not quote a time the operation has not committed to |
| Price and rate card | `MD-029` | Indicative bands only; firm prices follow diagnosis (`SP-013`) |
| Remote triage trees | `SP-033` | The technical path within an enquiry |
| Reason codes | `MD-026` | Outcome coding for analysis |
| Legal wording | Legal Counsel | Liability, recording, data protection, collection |
| Bengali authoring capacity | `BN-017` | Native speech authoring, not translation |

---

## 5. Procedure

### 5.1 Rules that govern every script

| # | Rule |
|---|---|
| **SC-01** | **The spine is fixed; the wording flexes.** Agents follow the order and the mandatory elements, and speak in their own words in between |
| **SC-02** | **Mandatory elements are marked and are not optional** — call recording notice, identity verification, consent, liability limits, collection wording |
| **SC-03** | **No agent commits to a date, a price or a liability outside their authority.** The script gives them the words to say what they can and cannot do (`SP-004`) |
| **SC-04** | **Bengali is authored for speech, not translated** (`CG-010` §5). English is authored second or in parallel, never as the master for the spoken form |
| **SC-05** | **Every script ends with a coded outcome** from `MD-026`, so contact reasons are analysable |
| **SC-06** | **Every script has a "this is beyond me" exit** — the agent always has a defined way to escalate without losing face or the customer |
| **SC-07** | **AI flows carry the identical mandatory elements.** The channel does not change the legal obligation (`M32`) |
| **SC-08** | **Nothing in a script may promise what the operation has not committed to** — SLA bands come from `MD-028`, prices from `MD-029` |
| **SC-09** | **Scripts are reviewed against call recordings quarterly**, not written once and archived |
| **SC-10** | **Accessibility**: plain language, short sentences, no unexplained jargon or acronyms (`CG-011`) |

### 5.2 The library

Twenty-two scripts across seven groups. Each is authored in Bengali and English per `SC-04`.

#### Group A — Enquiry and information

| # | Script | Mandatory elements | Ends with |
|---|---|---|---|
| A1 | General service enquiry | Recording notice; identity capture per `LG-009` | Coded outcome; booking or self-service pointer |
| A2 | Price and service scope enquiry | Indicative band only; "a firm estimate follows diagnosis" | Coded outcome |
| A3 | Branch, hours and coverage enquiry | — | Coded outcome |
| A4 | Warranty and entitlement enquiry | Entitlement stated from the system, never estimated | Coded outcome |
| A5 | Contract and AMC enquiry | Scope stated from the contract, not from memory | Handover to `R22` where commercial |

#### Group B — Booking and scheduling

| # | Script | Mandatory elements | Ends with |
|---|---|---|---|
| B1 | New service booking | Recording notice; device identification; **data-backup warning**; consent for contact | Service order created (`BRU-SRM-01`) |
| B2 | Reschedule or cancel | Cancellation terms where a charge applies | Updated order |
| B3 | Pick-and-drop booking | Charge or waiver stated; access and packaging expectations | Consignment booked |
| B4 | Emergency or priority request | **No promise of a time the dispatch position does not support** | Prioritised or honestly declined |

#### Group C — Status and self-service deflection

| # | Script | Mandatory elements | Ends with |
|---|---|---|---|
| C1 | Job status enquiry | Status stated from the system; **no speculation about causes** | Status given; self-service offered (`KPI-025`) |
| C2 | Delay explanation | Honest reason; revised expectation only if the operation has confirmed it | Updated expectation; escalation if breached |
| C3 | Ready-for-collection and uncollected reminder | Collection requirements; abandonment notice at the relevant stage (`BRU-SRM-16`) | Collection arranged |
| C4 | Self-service onboarding | Portal capability; consent for digital contact | Registered in `P01` |

#### Group D — Estimate and approval

| # | Script | Mandatory elements | Ends with |
|---|---|---|---|
| D1 | Estimate explanation and approval | Itemisation; validity period; **that work does not start until approved** (`BRU-SRM-07`) | Approval, decline with a coded reason, or defer |
| D2 | Revised estimate | The **cumulative** total, not only the delta (`SP-004` A-05) | Re-approval |
| D3 | Decline handling | No pressure; alternatives offered; diagnostic fee stated | Coded decline reason (`MD-026`) |
| D4 | Beyond economic repair | Evidence-based, never at triage (`BRU-SRM-12`); options and data-handling explained | Decision recorded |

#### Group E — Complaint

| # | Script | Mandatory elements | Ends with |
|---|---|---|---|
| E1 | Complaint intake | Acknowledgement; reference given; **no admission of liability** (`LG-021`) | Complaint logged (`SP-028`) |
| E2 | Complaint update | Honest position; next contact date committed and kept | Updated record |
| E3 | Resolution and closure | Explanation of what happened; **outcome confirmed with the customer** (`BRU-QMS-04`) | Confirmed closure |
| E4 | Angry or distressed customer | De-escalation; agent's right to end an abusive call, stated to the agent not the customer | Handover or resolution |

#### Group F — Retention and commercial

| # | Script | Mandatory elements | Ends with |
|---|---|---|---|
| F1 | AMC and contract renewal | Terms from the contract; no unauthorised discount (`SP-004` A-11…A-15) | Renewal, re-scope or recorded decline |
| F2 | Win-back after a lapse | Consent position respected (`NT-002`) | Outcome coded |
| F3 | Upsell or cross-sell within an inbound call | **Offered only after the customer's reason for calling is resolved** | Outcome coded |
| F4 | Loyalty and referral explanation | Terms stated accurately; no overstatement of benefit | Outcome coded |

#### Group G — Collection and escalation

| # | Script | Mandatory elements | Ends with |
|---|---|---|---|
| G1 | Payment reminder — early stage | **Legally reviewed collection wording** (`DT-018`); no threat, no implication of consequence not authorised | Payment or arrangement |
| G2 | Overdue and final demand | Legal wording exactly as approved; **agents may not vary it** | Escalation to Finance |
| G3 | Escalation handover to a supervisor | Context transferred so the customer does not repeat themselves | Warm handover |
| G4 | Escalation handover to a branch or technician | Same; with the job context attached | Warm handover |
| G5 | Media, legal or regulator contact | **Take details; make no statement; route immediately** (`SP-005` §4.8) | Routed to CEO/CCO or Legal |

### 5.3 The shape of a script — worked structure

Every script is authored to this structure so agents can navigate any of them the same way.

| Section | Content | Notes |
|---|---|---|
| **Purpose** | One line: what this conversation must achieve | |
| **When to use** | The trigger, and the nearest alternative script | Prevents the wrong script being used |
| **Before you speak** | What to have open on screen | Directly reduces AHT |
| **Opening** | Greeting, identification, recording notice | **Mandatory elements marked** |
| **Verify** | Identity verification appropriate to what will be disclosed | `LG-009` |
| **Understand** | Open questions; listen; do not interrupt to categorise | Mirrors `SP-007` step 2 |
| **Act** | The spine — ordered steps, with system actions named | Where `SP-033` trees attach |
| **Say this / not this** | Paired examples of good and poor phrasing | The most-used part of any script |
| **Mandatory wording** | Verbatim text that must be spoken | Legal, consent, disclosure |
| **If they ask…** | The five most common follow-up questions with answers | Raises FCR directly |
| **Escalate when** | The defined exit (`SC-06`) | With the `SP-005` path |
| **Close** | Summary, next step, expectation, thanks | |
| **Code the outcome** | The `MD-026` codes valid for this script | `SC-05` |

### 5.4 Authoring and maintenance

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 1 | Content Design with a Bengali speech author | Author the Bengali for speech first (`SC-04`) | `CG-010` §5, `BN-017` |
| 2 | Content Design | Author or align the English | `CG-003` |
| 3 | Legal Counsel | Approve every mandatory element and all collection wording | `LG-021`, `DT-018` |
| 4 | DPO | Approve identity verification and disclosure wording | `LG-009` |
| 5 | R35 | Pilot with agents on live calls; revise | — |
| 6 | Localisation Lead | Linguistic sign-off in context, listening to recordings, not reading text | `BN-018` |
| 7 | R35 | Publish to `P10`; align the `M32` AI flow with identical mandatory elements (`SC-07`) | `M32` |
| 8 | R35 | Review quarterly against recordings, FCR, AHT and complaint causes (`SC-09`) | §10 |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| Opening | Customer objects to recording | Follow the approved alternative wording; do not continue a recorded call against objection | R35 |
| Verify | Identity cannot be verified | Disclose nothing beyond what is public. Offer a verified channel instead | R34 |
| Act | The customer asks for a date the operation cannot support | Say what can be committed. **"I'll try to get it done sooner" is a promise** (`SC-03`, `SC-08`) | R34 |
| Act | The customer asks for a firm price before diagnosis | Give the indicative band; explain that the firm estimate follows diagnosis | R34 |
| Act | The technical path exceeds the agent's competence | Use the `SP-033` remote triage tree; where it ends, hand over — do not guess | R34 |
| Act | The customer expresses dissatisfaction | It becomes a complaint. Log it (`SP-028` §5.1 step 1); do not decide whether it "counts" | R34 |
| Act | The customer alleges harm, injury or data loss | Do not admit liability; escalate immediately on the right `SP-005` path | R35 |
| Escalate | No supervisor is available | The agent still has a defined exit (`SC-06`) — commit to a call-back with a name and a time, and keep it | R34 |
| Collection | The customer disputes the debt | Stop collection wording; route to Finance and, where appropriate, `SP-028` | R26 |
| Collection | The agent is asked to vary the approved wording | **Refused** (`SC-02`, G2). Collections language carries legal constraint | Legal |
| Any | Media, legal or regulator on the line | Take details, make no statement, route immediately (`SP-005` §4.8, G5) | CEO/CCO or Legal |
| Any | The customer becomes abusive | The agent may end the call after the approved warning. **The agent's safety and dignity are not negotiable** | R35 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Publish a new or amended script | Any | CCO on Content Design authorship, with Legal for mandatory elements | CEO |
| Approve mandatory legal wording | Any | Legal Counsel only | CCO |
| Approve collection wording | Any | Legal Counsel with CFO (`DT-018`) | CEO |
| Vary approved collection wording on a call | **None — prohibited** (`SC-02`) | — | — |
| Discount offered on a call | ≤ 10% | Agent-level authority per `SP-004` A-11 | R35, then R06 |
| Commit an SLA or a delivery date | Only what `MD-028` and the dispatch position support (`SC-08`) | — | R35 |
| Compensation offered on a call | ≤ BDT 5,000 | R06 Branch Manager (`SP-004` A-64) — **not the agent** | R05 |
| Approve the Bengali script | Any | Localisation Lead, on listening (`BN-018`) | CCO |
| Deploy an `M32` AI flow | Any | R35 with CTO; mandatory elements identical (`SC-07`) | CCO |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Agent commits to something outside authority | Correct with the customer honestly and quickly; coach, do not conceal | R35 | Quality record |
| Mandatory element omitted on a call | Quality finding; where it is a legal or consent element, assess the exposure | R35, Legal | Quality + compliance record |
| Collection wording varied | Treated as a compliance matter, not a coaching point | Legal, CFO | Compliance record |
| Complaint arises from what an agent said | Root cause is usually the script, not the agent (`SP-028` §5.4) | R35, R32 | Script review |
| Bengali script sounds unnatural on calls | Re-author for speech; do not patch a translation (`SC-04`) | Localisation Lead | Script revision |
| AI flow omits a mandatory element | Suspend the flow until corrected. The channel does not change the obligation (`SC-07`) | CTO, Legal | Flow suspension |
| Supervisor evaluates their own handled conversations | `SOD-35` violation; evaluation reassigned | R35's manager | `SP-006` exception report |
| FCR falls or AHT rises after a script change | Revert or revise; script changes are measurable and should be measured | R35 | `KPI-027` review |
| Agent abused or threatened on a call | End the call; support the agent; record; consider a customer-conduct response | R35, R30, HSE | Incident record |
| Script unavailable in the console | Printed pack per §9 | R35, R33 | Manual record |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | The contact centre holds a **printed script pack**, current version, in both languages, at every agent position |
| 2 | **Mandatory wording is printed verbatim and read from the page** — it is exactly the part that must not be improvised |
| 3 | Outcomes are recorded on a paper contact log with the customer reference and the `MD-026` code |
| 4 | Where customer or order data is unavailable, agents commit to a call-back rather than guess a status. **A guessed status is a future complaint** |
| 5 | **Back-enter every contact within 24 hours** so that volume and outcome analysis is not distorted |
| 6 | The printed pack is reissued on every script change — the same distribution discipline as `SP-032` §9 |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Mandatory elements present in every published script | Preventive (`SC-02`) | Per publication | Publication check |
| Legal approval of mandatory and collection wording | Preventive | Per change | Legal sign-off |
| AI flows carry identical mandatory elements | Preventive (`SC-07`) | Per flow | Flow review |
| Agents cannot commit outside `SP-004` authority | Preventive (`SC-03`) | Continuous | Console constraints |
| SLA and price statements sourced from the system | Preventive (`SC-08`) | Continuous | Console data |
| Every contact coded with an `MD-026` outcome | Preventive (`SC-05`) | Per contact | Coding requirement |
| Supervisor cannot evaluate own conversations | Preventive (`SOD-35`) | Per evaluation | Hard block |
| Quality monitoring against recordings | Detective | Weekly sample per agent | Quality scores |
| Mandatory-element compliance rate | Detective | Monthly | Compliance report |
| FCR, AHT and transfer rate by script | Detective | Monthly | `KPI-027` |
| Complaint causes traced to script wording | Detective | Monthly | `SP-028` analysis |
| Quarterly script review against recordings | Detective (`SC-09`) | Quarterly | Review record |
| Bengali naturalness review by listening | Detective | Quarterly | `BN-018` record |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Handle a conversation | Perform its quality evaluation (`SOD-35`) | Hard block | Evaluation by another supervisor or by Quality |
| Author a script | Approve its legal mandatory elements | Hard block | Legal Counsel approves |
| Own the FCR/AHT target | Be sole approver of a script change that affects it | Hard block | CCO approves with Content Design and Legal |
| Take a payment on a call | Approve a refund on the same order (`SOD-04` pattern) | Hard block | Refund approval sits with Finance |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-027` | First-contact resolution, all channels | unmeasured | 70%; stretch **78%** |
| `KPI-025` | Status enquiries deflected to self-service | 0% | 60%; stretch 80% |
| `KPI-026` | AI first-contact resolution | 0% | 40%; stretch 55% |
| `KPI-020` | CSAT | 3.8/5 | 4.4/5; stretch 4.7/5 |
| Average handling time | Mean contact duration by script | unmeasured | **−25%** against the `SP-002` baseline |
| Mandatory-element compliance | Calls where every mandatory element was delivered | untracked | 100% |
| Transfer rate | Contacts transferred rather than resolved | untracked | Falling |

> The AHT target is expressed as a reduction against a baseline that does not yet exist. `SP-002`
> T2 sampling must establish it before W4, or the −25% commitment is unprovable.

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `UI-020` `P10` Contact Centre Console UI Copy Pack | The console the scripts render in |
| `NT-019` IVR and Voice Prompt Scripts · `BN-017` Bengali Voice and IVR Recording Standard | Spoken content standards this library shares |
| `NT-002` Notification Preference and Consent Copy | The consent position agents must respect |
| `DT-018` Dunning and Collection Letter Series | The legally reviewed collection ladder G1–G2 aligns with |
| `LG-021` Customer Complaint and Redress Policy · `LG-009` Data Protection and Privacy Policy | The liability and disclosure positions |
| [`SP-028_SOP_Complaint_Escalation_and_Compensation.md`](SP-028_SOP_Complaint_Escalation_and_Compensation.md) | Group E scripts serve it |
| [`SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) | The technical path inside a call |
| [`SP-013_SOP_Estimate_Approval_and_Rework_Control.md`](SP-013_SOP_Estimate_Approval_and_Rework_Control.md) | Group D scripts serve it |
| [`SP-007_SOP_Walk_In_Intake_and_Front_Desk.md`](SP-007_SOP_Walk_In_Intake_and_Front_Desk.md) | Counter variants of Groups A and B |
| [`../06A_Process_Architecture/SP-005_Escalation_Matrix.md`](../06A_Process_Architecture/SP-005_Escalation_Matrix.md) | Group G escalation destinations |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Outcome coding |
| `TR-017` Course Pack — Contact Centre Agent | Trains this library |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue — library structure, 22 scripts across seven groups, governing rules `SC-01`…`SC-10` | Chief Commercial Officer (pending) |

**Open items**

| # | Item | Owner | Needed by |
|---|---|---|---|
| O-01 | **The 22 scripts are not yet authored.** This file specifies the library, its structure and its rules; the scripts themselves are a content deliverable requiring a **Bengali speech author** (`SC-04`), which is a distinct and currently unresourced skill | Content Design + Localisation Lead; resourcing by PMO | **Before W4** |
| O-02 | Legal approval of all mandatory and collection wording | Legal Counsel with CFO | Before W4 |
| O-03 | Establish the AHT baseline through `SP-002` T2 sampling, or the −25% target is unprovable | Business Process Lead + Contact Centre | Before W4 |
| O-04 | Align the `M32` AI conversational flows to carry identical mandatory elements | CTO with R35 and Legal | Before W6 AI assistant go-live |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Bengali-authored-for-speech rule stated as the primary production rule, citing `CG-010` §5
- [x] Mandatory elements defined and their variation prohibited
- [x] Every script has a defined escalation exit (`SC-06`)
- [x] AI flows bound to the same mandatory elements as human agents
- [x] The script structure specified so all 22 are navigable the same way
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **O-01 the 22 scripts authored in Bengali and English — outstanding; this file is the specification, the scripts are the deliverable**
- [ ] O-02 Legal approval of mandatory and collection wording — **outstanding**
- [ ] O-03 AHT baseline established — **outstanding, depends on `SP-002`**
- [ ] Bengali counterpart complete and signed off by listening (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending CCO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
