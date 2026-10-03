---
id: HC-019
title: AI Guardrail, Disclosure and Handover Copy
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal with Content Design
author: Legal Counsel with Content Design and AI Engineering
reviewers: [Chief Data Officer, CTO, AI Lead, Customer Service Manager, Chief Commercial Officer, Localisation Lead, Programme Content Lead]
approver: Legal Counsel with Chief Data Officer
content_class: B
purpose: >
  The AI disclosure statements, refusal copy, out-of-scope handling, human-handover wording and
  data-use notice. Customers must know they are talking to a machine, and the assistant must not
  commit the company to prices, promises or legal positions it has no authority to make — a
  commitment made by an automated agent is still a commitment, and the customer is entitled to
  rely on it.
traces_to: [M32, M26, M27, M34, M29, P01, P10, HC-001, HC-015, HC-017, HC-018, LG-008, LG-002, LG-011, CG-010, CG-013, BN-003]
priority: P1
wave: W6
bilingual: yes
bn_counterpart: HC-019_AI_Guardrail_Disclosure_and_Handover_Copy_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32 §9 BRU-CAI-13 the customer is told they are speaking to an automated assistant; BRU-CAI-02 never states a price it did not obtain from M11; BRU-CAI-03 never discloses personal data before identity verification; BRU-CAI-04 may not cancel a contract, issue a refund, grant goodwill credit or approve a repair above threshold; BRU-CAI-06 detected distress, threat or vulnerability escalates immediately with priority; BRU-CAI-07 an explicit request for a human is honoured immediately, without persuasion or deflection
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32 §5.5 FR-CAI-031…035 guard rails executed outside the model; §5.6 FR-CAI-036 handoff decision on emotional, operational and technical signals; FR-CAI-037 handoff package
    verified: 2026-08-18
    class: P1
  - source: Personal Data Protection Ordinance 2025 (Bangladesh), issued 6 November 2025 and finalised as the Personal Data Protection Act, 2026 (Law 63 of 2026) — applies to all entities processing personal data within Bangladesh and to entities abroad handling Bangladeshi citizens' data; requires explicit consent for collection; establishes data-subject rights and a national data authority; enforcement mechanisms expected to activate around 13 May 2027
    verified: 2026-08-18
    class: P1
    note: Binding law in the company's own jurisdiction. Legal Counsel must confirm the consent basis and the data-subject-rights expression before this file is Approved — Open Item O-01
  - source: EU AI Act Article 50 transparency obligations, applicable from 2 August 2026 — providers must ensure a reasonably informed person understands they are interacting with an AI system unless obvious from context; Commission guidance indicates that placing the disclosure in terms and conditions is not sufficient
    verified: 2026-08-18
    class: P2
    note: Cited as an international reference standard for what adequate disclosure looks like. Applicability to a Bangladesh-domiciled service is NOT established and is not asserted — see §4.2 and Open Item O-02
supersedes: none
review_due: 2027-02-18
---

# HC-019 — AI Guardrail, Disclosure and Handover Copy

> **Content class `B` — legal and contractual.** This is the only class-`B` file in Category 09 and
> the only one approved by Legal Counsel. `CG-002` §4 defines the class by consequence: an
> unenforceable term, a liability exposure, a contractual dispute. Every statement in this file is
> written to be read back to the company by someone who relied on it.

---

## 1. Purpose

Two obligations meet here, and they are different in kind.

**The first is honesty about what the customer is talking to.** `BRU-CAI-13` requires the customer
to be told they are speaking to an automated assistant. That is a hard rule in `M32` §9, and it
exists because a customer who believes they are speaking to a person calibrates their trust
accordingly.

**The second is containment of what the assistant can commit the company to.** `BRU-CAI-02` blocks
any price the assistant did not obtain from `M11`. `BRU-CAI-04` bars it from cancelling a contract,
issuing a refund, granting goodwill credit or approving a repair above threshold. These are hard
rules because **a commitment made by an automated agent acting for the company is still a
commitment**, and the customer is entitled to rely on it. The guardrails are technical; the wording
that keeps the assistant inside them is content, and it is this file.

**Consequence of absence (`CP-03`).** An assistant that does not disclose, refuses opaquely, or
hands over without context — and, worse, one whose refusal copy is vague enough that a customer
reasonably infers a commitment was made. `CG-013` escalates content carrying legal consequence to
Legal, and this file is that escalation made permanent.

---

## 2. Scope

**In scope:** disclosure statements and their placement; the data-use notice; refusal copy by
refusal class; out-of-scope handling; commitment-boundary language; handover copy and the handover
package's customer-facing side; safety, distress and vulnerability escalation copy; identity and
personal-data copy; and rules `GD-01`…`GD-24`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Answering, clarifying, confirming, "I don't know" | [`HC-018_Conversational_AI_Response_and_Fallback_Copy.md`](HC-018_Conversational_AI_Response_and_Fallback_Copy.md) — **the seam is `RC-23`** |
| Intents, utterances, out-of-scope **detection** | [`HC-017_Conversational_AI_Intent_and_Utterance_Library.md`](HC-017_Conversational_AI_Intent_and_Utterance_Library.md) `IL-14` — detection there, wording here |
| Guard-rail **implementation** | `M32` §5.5 · `FR-CAI-031`…`035` |
| The privacy notice itself | `LG-008` — **this file links to it and never restates it** (`IA-14`) |
| Portal terms | `LG-002` |
| Complaint handling process | `SP-028` · `M34` |
| Contact-centre agent handling of a handed-over contact | [`../09A_Help_Sets_By_Portal/HC-012_Help_Set_P10_Contact_Centre_Console.md`](../09A_Help_Sets_By_Portal/HC-012_Help_Set_P10_Contact_Centre_Console.md) Block C |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Legal Counsel** | Own the disclosure and commitment position; approve |
| **Chief Data Officer** | Own the data-use notice and the PDPA position |
| **Content Design** | Author within the legal boundary |
| **AI Engineering** | Bind guardrail triggers to the correct copy |
| **Customer Service Manager** | Own what the customer experiences at handover |
| **Localisation Lead** | Ensure Bengali disclosure is legally adequate, not merely translated |

---

## 4. Content

### 4.1 Disclosure

**`GD-01`: the customer is told they are speaking to an automated assistant, before the first
substantive exchange** (`BRU-CAI-13`).

| Requirement | Rule |
|---|---|
| **When** | At the start of every conversation, and on resumption after a session gap |
| **Where** | **In the conversation itself.** `GD-02`: disclosure placed only in terms and conditions does not satisfy the obligation |
| **How** | Plain, short, in the customer's language and script (`RC-24`) |
| **Persistence** | A persistent visual indicator for the duration of the conversation, in addition to the opening statement |
| **On handover** | The customer is told **explicitly** when they move from machine to human, and when they move back |
| **If asked** | *"Are you a person?"* is answered directly and immediately — `GD-03`, and it is never deflected |

**`GD-03`: the assistant never claims or implies it is human**, does not use a human name, and does
not describe itself as having feelings, opinions or personal experience.

> **On the standard applied — stated precisely under `CG-012`.**
> The binding requirement is `BRU-CAI-13`, an internal hard rule. In addition, **EU AI Act Article
> 50**, applicable from 2 August 2026, requires providers of AI systems intended to interact
> directly with people to ensure a reasonably informed person understands they are interacting with
> an AI system, and Commission guidance indicates that placing the disclosure in terms and
> conditions is not sufficient. **That instrument is cited here as an international reference for
> what adequate disclosure looks like. Its applicability to a Bangladesh-domiciled service business
> is not established and is not asserted.** `GD-02` adopts its substance because it is the better
> practice, not because the company has determined it is bound. Legal Counsel to confirm — `O-02`.

### 4.2 The data-use notice

**Bangladesh has binding data protection law.** The Personal Data Protection Ordinance 2025, issued
6 November 2025 and finalised as the Personal Data Protection Act, 2026, applies to entities
processing personal data within Bangladesh, requires explicit consent for collection, establishes
data-subject rights and a national data authority, with enforcement mechanisms expected from around
May 2027 — **before `M32` reaches steady state**.

| # | Rule | Class |
|---|---|:--:|
| **GD-04** | The customer is told, at the start, **what the conversation is used for** — resolving their enquiry, and improvement of the service — in one sentence, linking to `LG-008` for the full notice | **H** |
| **GD-05** | The notice **links to** `LG-008` and never restates it (`IA-14`) | **H** |
| **GD-06** | **Transcripts used for improvement are anonymised before use** (`BRU-CAI-15`), and the notice says so | **H** |
| **GD-07** | **Recovered customer data from `M06` is never used as training or retrieval data** (`BRU-CAI-12`) — and is never referenced in a conversation | **H** |
| **GD-08** | The assistant can tell a customer **how to exercise their data rights**, and routes the request rather than handling it (`account.data_request` intent) | **H** |
| **GD-09** | Personal data is never disclosed before identity verification (`BRU-CAI-03`), and the verification request explains why it is being asked | **H** |

**`GD-10`: the data-use notice is written by Legal, not adapted by Content Design.** Content Design
may propose plain-language phrasing; the legal content is Legal's, and the approved wording is used
verbatim.

### 4.3 Refusal copy by class

**`GD-11`: every refusal names a reason class and offers a route.** A refusal without a route is an
abandonment.

| Class | Trigger | What the assistant conveys | Route |
|---|---|---|---|
| **Out of scope** | `FR-CAI-008`, `IL-14` | This is not something it can help with; what it *can* do | Human, or none if genuinely unrelated |
| **Beyond authority** | `BRU-CAI-04`, `FR-CAI-029` | **A person needs to do this** — not that it is impossible | **Human, with context** |
| **Price not retrievable** | `BRU-CAI-02` | It cannot give a price for this; a person can | Human |
| **Identity not verified** | `BRU-CAI-03` | It cannot share that until it knows who it is speaking to; how to verify | Verification, then retry |
| **Prohibited topic** | `FR-CAI-032` — medical, legal, financial advice, competitor commentary | It does not advise on that | Human where appropriate |
| **Abusive or injection input** | `FR-CAI-031` | Brief, neutral, non-escalating | Human on repetition |
| **Retrieval or inference unavailable** | `BRU-CAI-11` | The service is unavailable; **no attempt at an answer** | Human |

**`GD-12`: "beyond authority" is never worded as "I can't do that".** The customer hears *refused*.
The correct sense is *this needs a person*, which is a routing statement, not a denial.

**`GD-13`: refusal copy is neutral and does not moralise**, including on abusive input. A machine
lecturing a frustrated customer escalates a contact that a neutral handover would have resolved.

### 4.4 The commitment boundary

This is the section the class-`B` designation exists for.

| # | Rule | Class |
|---|---|:--:|
| **GD-14** | The assistant **never states a price it did not obtain from `M11`** — not an estimate, not a range, not a "typically" (`BRU-CAI-02`) | **H** |
| **GD-15** | The assistant **never states or implies an SLA, a guarantee, a warranty position or a legal entitlement.** It links to the governing `LG-*` artefact | **H** |
| **GD-16** | The assistant **never commits to a date, a time or an outcome** it has not retrieved from live data, and states retrieved timings as expectation, not promise (`HS-13`) | **H** |
| **GD-17** | The assistant **never cancels a contract, issues a refund, grants goodwill credit or approves a repair above threshold** (`BRU-CAI-04`) | **H** |
| **GD-18** | Where an action creates a commitment, the assistant restates it and obtains explicit confirmation (`BRU-CAI-05`, `RC-19`…`RC-21`) | **H** |
| **GD-19** | **Hedging language is prohibited where it could be read as a commitment.** *"It should be ready by Tuesday"* is a commitment in the customer's ear. Either state retrieved data or say a person will confirm | **H** |
| **GD-20** | Every conversation turn is logged with input, retrieved sources, model version, guardrails fired, confidence and action (`BRU-CAI-10`) — **the record that resolves a disputed commitment** | **C** |

> **`GD-19` is the rule most likely to be eroded in drafting**, because hedged language sounds
> helpful and reads as harmless. It is not harmless: a customer who arranges their day around
> *"should be ready by Tuesday"* and finds it is not has been given a commitment by the company,
> however it was phrased.

### 4.5 Handover

`FR-CAI-036` triggers handoff on emotional, operational and technical signals, each independently
tunable. `FR-CAI-037` passes the human the full transcript, intent, entities, actions, sources,
sentiment and the handoff reason.

| # | Rule | Class |
|---|---|:--:|
| **GD-21** | **An explicit request for a human is honoured immediately, without persuasion or deflection** (`BRU-CAI-07`). No "let me try once more" | **H** |
| **GD-22** | The customer is told a handover is happening, what the person will already know, and — where the system can support it — how long it will take (`RC-18`, `O-05`) | **H** |
| **GD-23** | **The customer never repeats themselves after a handover.** If the agent has to ask again, the handover package failed (`FR-CAI-037`) | **H** |
| **GD-24** | Where no human is available, the assistant says so honestly, captures the enquiry, and commits to a callback **only if the system can honour it** | **H** |

### 4.6 Safety, distress and vulnerability

**`GD-25`: detected distress, threat, safety risk or vulnerability escalates immediately with
priority** (`BRU-CAI-06`, `FR-CAI-034`). The copy at this moment is the most consequential in the
category.

| Situation | What the assistant does | What it must never do |
|---|---|---|
| Customer describes a device that is hot, smoking, swollen or burning | **Safety statement first** — stop using it, isolate it — then immediate priority handoff | Ask diagnostic questions first |
| Customer expresses distress or is in crisis | Acknowledge briefly, hand over immediately with priority | Attempt to help; offer resources it is not qualified to offer |
| Customer indicates vulnerability | Hand over with the signal passed | Continue automated handling |
| Threat to a person | Immediate escalation per `SP-030` and `M34` | Respond conversationally |

**`GD-26`: safety copy is approved by HSE as well as Legal**, and is never abbreviated for
conversational tone. The `KB-013` hazard position governs what is said about a device (`IA-07`).

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M32` §5.5, §5.6, §9 | Every rule in this file discharges an `M32` requirement or hard rule |
| [`HC-018_Conversational_AI_Response_and_Fallback_Copy.md`](HC-018_Conversational_AI_Response_and_Fallback_Copy.md) | The `RC-23` seam; joint review required |
| [`HC-017_Conversational_AI_Intent_and_Utterance_Library.md`](HC-017_Conversational_AI_Intent_and_Utterance_Library.md) | Out-of-scope and handover intents |
| `LG-008` privacy notice · `LG-002` portal terms · `LG-011` cookie and tracking policy | Linked, never restated |
| [`../../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](../../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | The safety position behind `GD-26` and `IA-07` |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md) · [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Escalation routes |
| `M11` | The only lawful source of a price in a conversation |
| `M27`, `M34` | Handover destination and complaint capture |

| Depended on by |
|---|
| `M32` guardrail copy binding · `HC-012` Block C agent help · `HC-018` fallback rungs 4–7 · `M27` handover experience |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **6-monthly** — the shortest in this category, matching `KB-013`'s safety cycle |
| Trigger for out-of-cycle review | **Any regulatory change affecting disclosure or data protection** · a guardrail incident · a disputed commitment · a distress-handling failure · an `M32` authority change |
| Owner | Legal Counsel owns the legal content; Content Design owns the phrasing within it |
| **Joint review** | With `HC-018` (`RC-23`) and with HSE for `GD-26` |
| Approval | **Legal Counsel with Chief Data Officer** — class `B` (`CG-002` §4, `CG-007`) |
| Change log | `RF-006` |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The Personal Data Protection Act 2026 position is not confirmed.** The law is binding in the company's own jurisdiction, requires explicit consent, establishes data-subject rights, and enforcement is expected from around May 2027. **§4.2's notice, `GD-06` anonymisation and `GD-08` rights routing all rest on a consent basis Legal has not confirmed.** The same question `HC-015` `O-02` and `HC-017` `O-02` raise from the content side | **Legal Counsel with CDO** | **W2 — `CG-013` trigger; it gates `HC-015` and `HC-017` collection, not just this file** |
| **O-02** | **Whether EU AI Act Article 50 applies to this service is not established**, and §4.1 does not assert that it does. `GD-02` adopts its substance as better practice. Legal to confirm whether any extraterritorial obligation arises | Legal Counsel | W6 |
| **O-03** | **`LG-008` privacy notice, `LG-002` portal terms and `LG-011` cookie policy are unwritten** (Category 10 unstarted). `GD-05` requires linking to a notice that does not exist | Legal Counsel | **W6 — blocking `Approved` status** |
| **O-04** | **The `RC-23` seam between `HC-018` and `HC-019` has no joint owner**, and the two files have different approvers — Content Design Lead and Legal Counsel. `HC-018` `O-05` records it from the other side | Content Design Lead with Legal Counsel | **W6** |
| **O-05** | `GD-22` and `GD-24` reference wait times and callbacks. **Stating a time the system cannot honour is precisely the commitment `GD-19` prohibits** — the capability must be confirmed before the copy is written | AI Lead with Contact Centre | W6 |
| **O-06** | **Bengali disclosure must be legally adequate, not merely translated.** A disclosure that is clear in English and ambiguous in Bengali fails for the majority of customers. Legal review of the Bengali is required, and the reviewer must be able to assess Bengali | Legal Counsel with Localisation Lead | **W6** |
| **O-07** | `GD-25` distress and vulnerability detection depends on `FR-CAI-004` sentiment detection operating reliably in Bengali. **A miss here is the most serious failure mode in the category** | AI Lead with Customer Service Manager | **W6** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` per `CG-009` §3 for `HC-017`–`HC-019`
- [x] Content class `B` with Legal Counsel and CDO as approvers (`CG-002` §4, `CG-007`)
- [x] **Disclosure required in the conversation, not in terms and conditions (`GD-02`)**
- [x] **The EU AI Act cited as a reference standard with its applicability explicitly not asserted** (`CG-012`)
- [x] **Bangladesh's Personal Data Protection Act identified as binding law in the company's own jurisdiction, with the open question stated rather than assumed resolved**
- [x] Refusal copy classified, each with a route (`GD-11`); "beyond authority" distinguished from refusal (`GD-12`)
- [x] **Commitment boundary stated as hard rules, including the hedging prohibition (`GD-19`)**
- [x] Handover requires no repetition by the customer (`GD-23`)
- [x] Safety, distress and vulnerability copy specified, with HSE approval required (`GD-26`)
- [x] Privacy notice linked, never restated (`GD-05`, `IA-14`)
- [x] All internal links resolve
- [x] `BRU-CAI-*` and `FR-CAI-*` cited to **`M32`**, not to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` PDPA consent basis confirmed — outstanding; gates `HC-015` and `HC-017` as well as this file**
- [ ] **`O-03` `LG-008` privacy notice — outstanding; blocks `Approved`**
- [ ] **`O-06` Bengali disclosure legally reviewed — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] **Named approvers recorded — pending Legal Counsel and Chief Data Officer (required for class `B`, `CM-R7`)**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
