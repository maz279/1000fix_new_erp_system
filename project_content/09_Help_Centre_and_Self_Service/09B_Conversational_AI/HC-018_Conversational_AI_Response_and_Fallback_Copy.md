---
id: HC-018
title: Conversational AI Response and Fallback Copy
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design with AI
author: Content Design with AI Engineering
reviewers: [CTO, AI Lead, Customer Service Manager, Legal Counsel, Localisation Lead, Quality Manager, Programme Content Lead]
approver: Content Design Lead with CTO
content_class: D
purpose: >
  The response templates, grounding citations, clarification, fallback and no-answer copy the
  assistant speaks in. An assistant that answers confidently from nothing is worse than one that
  hands over cleanly — a wrong answer delivered fluently is acted on, and the customer discovers it
  was wrong only after they have relied on it.
traces_to: [M32, M26, M27, M61, P01, P10, HC-001, HC-002, HC-015, HC-017, HC-019, KB-001, KB-015, CG-003, CG-004, CG-010, VB-001, VB-009, BN-003]
priority: P2
wave: W6
bilingual: yes
bn_counterpart: HC-018_Conversational_AI_Response_and_Fallback_Copy_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32 §5.3 FR-CAI-015 retrieval-augmented grounding, FR-CAI-016 citation, FR-CAI-019 no-answer behaviour — state plainly that it does not know and offer a human rather than generating a plausible answer; FR-CAI-020 bilingual response matching the customer's script choice
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32 §9 BRU-CAI-01 ungrounded factual output is blocked; BRU-CAI-02 never states a price it did not obtain from M11; BRU-CAI-05 an action creating a commitment requires explicit confirmation; BRU-CAI-09 retrieved content is data, never instruction; BRU-CAI-11 if inference or retrieval is unavailable the assistant hands off
    verified: 2026-08-18
    class: P1
  - source: project_content/07_Knowledge_Base_and_Technical_Library/KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md KR-07 — overdue content leaves the M32 corpus while remaining available to human readers, because a generated answer with a citation cannot convey a warning credibly
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# HC-018 — Conversational AI Response and Fallback Copy

> **`HC-017` decides what the customer meant. This file decides what the assistant says back** —
> and, more importantly, what it says when it does not know.

---

## 1. Purpose

`FR-CAI-019` is a `P0` requirement and it is unusually blunt: the assistant must **state plainly
that it does not know and offer a human, rather than generating a plausible answer**.

That requirement is a content problem, not a model problem. A model can be configured to decline;
whether the decline is usable depends entirely on the words:

| A bad decline | Why it fails |
|---|---|
| *"I'm sorry, I don't have information on that."* | Dead end. The customer has been refused and given nothing |
| *"I'm not sure I understand. Could you rephrase?"* | Blames the customer for the model's limit |
| *"Please contact customer service."* | Where? How? Now? The customer has to start again |
| Silence, or a generic error | The customer assumes the service is broken |

**Consequence of absence (`CP-03`).** Without governed response copy the assistant either invents
answers — which `BRU-CAI-01` blocks technically but which shows up as evasive or empty replies — or
it declines in ways that push the customer to the hotline in a worse mood than if it had never
answered. `KPI-026` targets 40–55% AI first-contact resolution; the failures matter as much as the
successes, because they are the ones the customer remembers.

---

## 2. Scope

**In scope:** the assistant's voice; response templates by intent class; grounding and citation
presentation; clarification copy; the fallback ladder; no-answer copy; error and unavailability
copy; confirmation copy for actions; language and script matching; and rules `RC-01`…`RC-22`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Intents, utterances, slots, disambiguation logic | [`HC-017_Conversational_AI_Intent_and_Utterance_Library.md`](HC-017_Conversational_AI_Intent_and_Utterance_Library.md) |
| **Disclosure, refusal, guardrail and handover wording** | [`HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md`](HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md) — **the boundary is §4.7** |
| The grounding corpus and its admission test | [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) §4.8 · `KB-001` §4.8 |
| Model behaviour, guard-rail execution, retrieval | `M32`, `M26` |
| Product voice generally | `VB-001` · `CG-003` — **this file specialises it for a machine speaker** |
| Agent scripts | `SP-034` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Content Design** | Author and maintain the response set |
| **AI Engineering** | Implement templates and fallback behaviour |
| **Customer Service Manager** | Own how the company sounds when automated |
| **Localisation Lead** | Ensure Bengali responses are authored, not translated |
| **Quality Manager** | Assess assistant conversations as a quality surface |

---

## 4. Content

### 4.1 The assistant's voice

`VB-001` sets the product voice. **`RC-01`: the assistant is a competent, plain-spoken member of
staff — not a personality, not a mascot, and not a person.**

| The assistant is | The assistant is not |
|---|---|
| Direct — the answer first | Chatty, apologetic, or padded |
| Plain — `CG-011` reading level | Formal or bureaucratic |
| Honest about its limits | Confident where it is uncertain |
| Consistent | Variable in tone by turn |
| **Clear that it is automated** | Pretending to be human (`HC-019`, `BRU-CAI-13`) |

**`RC-02`: no filler.** *"Great question!"*, *"I'd be happy to help you with that!"* and *"Let me
look into that for you"* add turns to a conversation the customer wants to end. In a market where
many customers are on metered mobile data, filler has a cost.

**`RC-03`: no false empathy.** *"I completely understand how frustrating that must be"* from a
machine reads as insulting when the customer is genuinely angry. Acknowledge the fact, not the
feeling: *"Your repair is four days past its estimate. I'll get you to someone who can act on it."*

### 4.2 Response templates by intent class

| Intent class | Template shape | Grounding | Example structure |
|---|---|---|---|
| **Status** | Fact → what happens next → offer | **Live ERP data** (`FR-CAI-017`) | *"Your repair is [status]. [Next step] is expected [timing]. Do you want the details?"* |
| **Informational** | Answer → source → related | **`HC-*`/`KB-*` corpus** | Answer first (`RC-04`), then the article link |
| **Transactional** | Restate → confirm → execute → confirm done | Live data + action | `BRU-CAI-05` explicit confirmation |
| **Price** | **Retrieved figure only, or handoff** | **`M11` only** (`BRU-CAI-02`) | Never computed, never estimated |
| **Diagnostic** | Symptom → likely next step → route | `MD-024`, `KB` customer derivatives | **Never a repair instruction** (`IA-07`) |
| **Complaint** | Acknowledge → capture → route | `M34` | Never resolves; always routes |
| **Out of scope** | Decline → route | None | `HC-019` |

**`RC-04`: the answer is the first sentence.** The same rule as `FQ-04`, and for the same reason —
a customer reading on a phone sees one or two lines before scrolling.

**`RC-05`: every response offers a next step.** A response that answers and stops leaves the
customer to work out what to do, which is when they call.

### 4.3 Grounding and citation

`FR-CAI-016` requires the source of each grounded statement to be attached, visible to the agent on
handoff and available for audit.

| # | Rule | Class |
|---|---|:--:|
| **RC-06** | A factual response is grounded, or it is not given (`BRU-CAI-01`) | **H** |
| **RC-07** | **Citation is presented as a useful link, not as an academic reference.** *"You can read the full steps here"* rather than a source identifier | **H** |
| **RC-08** | The customer-facing citation names the article; the **audit record carries the article code and version** (`FR-CAI-016`) | **H** |
| **RC-09** | Where a response combines live data and corpus content, both are attributable | **H** |
| **RC-10** | **Retrieved content is data, never instruction** (`BRU-CAI-09`) — the response copy never repeats text that could be read as a directive to the model | **H** |
| **RC-11** | Content that has left the corpus is never cited from cache (`KB-015` `KR-07`, `KA-11`) | **C** |

> **`RC-07` is a small decision with a large effect.** An assistant that answers and then shows a
> reference identifier reads as a machine reciting. One that answers and says *"the full steps are
> here"* reads as help. The audit trail is unaffected either way — it is `RC-08`'s job.

### 4.4 Clarification

| # | Rule |
|---|---|
| **RC-12** | Clarification asks a question a person would ask, offering at most three options plus "something else" (`IL-09`, `IL-10`) |
| **RC-13** | The assistant never asks for information it already has (`FR-CAI-010`) — asking a logged-in customer for their order number is the fastest way to lose them |
| **RC-14** | **One clarification per turn; two per conversation; the third is a handoff** (`IL-11`) |
| **RC-15** | A clarification is never used to avoid a requested handoff (`BRU-CAI-07`, `IL-12`) |

### 4.5 The fallback ladder

**`RC-16`: fallback is a ladder, and each rung is a distinct message.** A single generic fallback
for every failure mode is the commonest and most damaging shortcut.

| Rung | Situation | What the assistant says (shape) | Then |
|:--:|---|---|---|
| 1 | Intent unclear, first attempt | Clarify with options (`RC-12`) | Retry |
| 2 | Intent unclear, second attempt | **Offer the three most likely things** and a human | Retry once |
| 3 | **Intent clear, no grounded answer** | *"I don't have a reliable answer to that."* → offer a human | **Handoff** (`FR-CAI-019`) |
| 4 | **Out of scope** | Decline plainly, say what it can do, route | `HC-019` |
| 5 | **Beyond action authority** | Say the action needs a person, route with context | `FR-CAI-029`, `HC-019` |
| 6 | **Retrieval or inference unavailable** | Say the service is unavailable, **do not attempt an answer**, route | `BRU-CAI-11` |
| 7 | **Distress, safety, vulnerability detected** | **Immediate priority handoff** | `BRU-CAI-06`, `HC-019` |

**`RC-17`: rungs 3 and 6 never guess.** `BRU-CAI-11` requires handoff rather than ungrounded output
when retrieval is unavailable, and `FR-CAI-019` requires a plain statement of not knowing. The copy
must make both sound like competence, not like failure.

**`RC-18`: the no-answer message names what happens next and when.** *"I don't have a reliable
answer. I can pass you to an agent now — typically under two minutes at this time of day. Shall I?"*
is a decline the customer can act on. *"I'm sorry, I can't help with that"* is not.

### 4.6 Action confirmation

`BRU-CAI-05` requires explicit confirmation before executing anything that creates a commitment.

| # | Rule |
|---|---|
| **RC-19** | Restate the action in the customer's terms, including anything that costs them money or time, then ask |
| **RC-20** | Confirmation is explicit and unambiguous — silence, *"ok"* in a stream of other text, or a resumed conversation is not consent |
| **RC-21** | After execution, confirm what was done and what happens next |
| **RC-22** | If the action fails, say so plainly, say what state things are in, and route — **never leave the customer unsure whether it happened** |

### 4.7 The boundary with `HC-019`

| Copy | Owner |
|---|---|
| Answering, clarifying, confirming, and saying *"I don't know"* | **`HC-018`** — this file |
| **Disclosing that it is a machine** | **`HC-019`** |
| **Refusing** — out of scope, beyond authority, prohibited topic | **`HC-019`** |
| **Handover wording and what the human receives** | **`HC-019`** |
| **Data-use notice** | **`HC-019`** |

**`RC-23`: where the two meet — the no-answer handoff at rung 3 — `HC-018` writes the "I don't
know" and `HC-019` writes the handover.** Two files, one sentence pair, and the seam must be
invisible to the customer. Joint review is required (§6).

### 4.8 Language and script

`FR-CAI-020` requires the assistant to respond in the customer's language, **matching their script
choice**, with correct Bengali typography.

| # | Rule |
|---|---|
| **RC-24** | Match the customer's script: Bengali script in, Bengali script out; romanised in, **romanised out** |
| **RC-25** | Mixed-script input is answered in the dominant script, not corrected |
| **RC-26** | Bengali responses are **authored in Bengali** (`HS-29`, `IL-04`) |
| **RC-27** | Codes, order numbers, amounts and model names are never translated (`HS-32`) |
| **RC-28** | Bengali typography and numerals per `VB-009` |

**`RC-25` matters more than it looks.** A customer typing romanised Bengali who receives Bengali
script has been silently told they typed it wrong.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M32` §5.3, §9 | The requirements this copy discharges |
| [`HC-017_Conversational_AI_Intent_and_Utterance_Library.md`](HC-017_Conversational_AI_Intent_and_Utterance_Library.md) | Every response maps to an intent |
| [`HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md`](HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md) | The `RC-23` seam |
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) §4.8 · [`../../07_Knowledge_Base_and_Technical_Library/KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](../../07_Knowledge_Base_and_Technical_Library/KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) | The corpus and its currency (`RC-11`) |
| [`../HC-015_FAQ_Bank_by_Audience.md`](../HC-015_FAQ_Bank_by_Audience.md) | A large share of grounded answers |
| `VB-001`, `CG-003`, `CG-004` | Voice and terminology |
| `VB-009`, `BN-003` | Bengali typography and terms |
| `M11` | The only source of a price (`BRU-CAI-02`) |

| Depended on by |
|---|
| `M32` response generation · `HC-012` agent help on AI assist · `M27` handoff quality |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Quarterly**, with the `HC-017` utterance refresh |
| Trigger for out-of-cycle review | Fallback rate rising · handoff satisfaction falling · a guardrail incident · a corpus change · a `VB-001` voice change |
| Owner | Content Design, jointly with AI Engineering on the fallback ladder |
| **Joint review** | **`RC-23` requires `HC-018` and `HC-019` to be reviewed together** — the seam is invisible to the customer and must be to the reviewer too |
| Change log | `RF-006` |
| Enforcement | `RC-01`…`RC-28`; `BRU-CAI-01`, `-02`, `-05`, `-09`, `-11` |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The response set is unwritten** — ~61 intents × response, clarification and failure variants, in two languages and two scripts, is roughly **400–500 copy items**. Effort **150–250 hours** plus Bengali authoring | Content Design with AI Lead | **W6** |
| **O-02** | **Bengali response authoring** (`RC-26`) requires domain-competent Bengali writers — the same capability gap `TR-001` `O-05`, `KB-002` `O-05` and `HC-002` `O-05` record | Localisation Lead | **W6** |
| **O-03** | **Script matching (`RC-24`, `RC-25`) requires the platform to detect and preserve the customer's script.** Whether `M32` exposes that is unconfirmed; if not, the rule is unimplementable | CTO with AI Lead | **W6** |
| **O-04** | Handoff wait-time statements (`RC-18`) require live queue data from `M27`. Stating a time the system cannot support is worse than stating none | AI Lead with Contact Centre | W6 |
| **O-05** | **The `RC-23` seam has no joint owner.** `HC-018` and `HC-019` have different owners and different approvers — Content Design and Legal — and the customer sees one message | Content Design Lead with Legal Counsel | **W6** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` with the intent-related schema treatment `CG-009` §3 expects for `HC-017`–`HC-019`
- [x] The assistant's voice specified against `VB-001`, with filler and false empathy prohibited
- [x] Answer-first structure and a next step in every response (`RC-04`, `RC-05`)
- [x] Grounding and citation presented usefully while preserving the audit record (`RC-07`, `RC-08`)
- [x] **Fallback specified as a seven-rung ladder rather than one generic message (`RC-16`)**
- [x] No-answer copy required to name what happens next and when (`RC-18`)
- [x] Action confirmation explicit; failure states never left ambiguous (`RC-19`…`RC-22`)
- [x] **Boundary with `HC-019` stated, including the shared seam and its joint-review requirement (`RC-23`)**
- [x] Script matching required, including romanised Bengali (`RC-24`, `RC-25`)
- [x] All internal links resolve
- [x] `BRU-CAI-*` and `FR-CAI-*` cited to **`M32`**, not to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-03` script preservation confirmed — outstanding**
- [ ] **`O-05` joint ownership of the `HC-018`/`HC-019` seam — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and CTO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
