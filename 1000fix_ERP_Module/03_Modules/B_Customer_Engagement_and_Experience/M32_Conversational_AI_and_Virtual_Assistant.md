---
id: FIX-ERP2-M32
module_id: M32
module_code: CAI
module_name: Conversational AI & Virtual Assistant
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

# M32 — Conversational AI & Virtual Assistant
### Category B · Code `CAI` · ★ New module in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M32 |
| **Module code** | `CAI` |
| **Category** | B — Customer Engagement & Experience |
| **Status** | ★ **New** — split from M27 after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | W4 (Months 14–18) |
| **Business owner** | Customer Service Manager |
| **System owner** | Platform Squad |
| **Delivery layers** | L4 (Ollama, vector store) + L5 (custom) |
| **Custom modules** | `cd_assistant`, `cd_intent`, `cd_grounding`, `cd_guardrail`, `cd_assistant_actions` |
| **Requirement range** | FR-CAI-001 … FR-CAI-038 |
| **Requirement count** | 38 |
| **Effort estimate** | 18 person-weeks |
| **Depends on** | M27 Contact Centre · M26 AI/ML Services · M61 Knowledge · M33 Party Master · M29 Identity |
| **Depended on by** | M27, M07, M34, M01, M38, M25 |

---

## 2. Purpose

M32 is the **Bengali-first assistant** that handles the first line of every customer
conversation: answering questions, checking status, booking service, and knowing precisely
when to stop and hand over to a person.

It is not a chatbot in the 2020 sense. It grounds every answer in the Company's own data and
knowledge base, performs authenticated actions on the customer's behalf, and operates inside
hard guard rails that prevent it from doing the two things that would destroy trust: quoting a
price it invented, and refusing to escalate when it should.

### Why It Exists

The Company handles 250,000+ customer interactions a month. A large proportion are simple,
repetitive and answerable from data the ERP already holds: *where is my device, when will the
technician arrive, what does this repair cost, is my warranty valid, how do I book*.

Answering those with human agents at that volume is neither affordable nor fast. Answering
them with a scripted menu bot in a country where the customer's first language is Bengali and
their message may mix Bengali script, transliterated Bengali and English in one sentence is a
poor experience that customers abandon.

M32 exists to absorb that volume properly — and, critically, **to know its limits**.

### Why It Is Separate from M27

The Category B overview states the reason plainly: **their failure modes, release cadence and
governance differ**. M27 fails when a customer cannot reach a human. M32 fails when it gives a
confident wrong answer. A telephony configuration change must not require an AI model release,
and a model update must not risk the hotline.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Service App SOW §Customer Support | "In-app chat with customer service… **chatbot configuration**… at the end of the chat, the customer will be able to rate the conversation" |
| Business Plan §24/7 Technical Support | "Comprehensive knowledge base and self-service resources… FAQ articles, troubleshooting guides, video tutorials and user manuals, providing customers with self-help options and answers to common queries. This empowers our customers to find solutions independently and reduces their dependence on our support team for routine issues." |
| ERP BRD INT-22, CSP-013 | AI chatbot with Bengali NLP; live chat with AI and human escalation |
| ERP Technology Stack §6.10 | Divergence from Rasa to an LLM approach: "Rasa OSS has entered maintenance mode… LLM approach provides superior Bengali language understanding… tool-use capability allows the LLM to directly interact with the Odoo API… self-hosted via Ollama, no per-query API costs, data remains on-premises" |
| Portal roadmap IMPL-23, IMPL-43 | Chatbot at 70% resolution, then hybrid at 90% resolution |
| **Personal Data Protection Act 2026** *(verified 2026-08-12)* | Processing personal data in conversation requires a lawful basis; automated processing must be disclosed |
| **Category J AI governance** | Ten non-negotiable AI rules including human confirmation for material decisions, guard rails, explainability, override capture, fallback, and prohibition on training with recovered customer data |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Intent recognition across Bengali, English and mixed-script input |
| 2 | Entity extraction — order number, serial, device, date, branch, amount |
| 3 | Dialogue management: multi-turn context, clarification, disambiguation |
| 4 | Retrieval-augmented grounding against Company knowledge and live ERP data |
| 5 | Authenticated actions performed on the customer's behalf |
| 6 | Guard rails: scope, price, policy, PII, safety, and prohibited topics |
| 7 | Confidence assessment and handoff decision |
| 8 | Handoff package construction for the human agent |
| 9 | Agent assistance: summaries, suggested replies, next-best-action |
| 10 | Conversation analytics: intent distribution, containment, deflection |
| 11 | Assistant configuration: intents, flows, responses, escalation thresholds |
| 12 | Continuous improvement loop from unresolved and mis-handled conversations |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Channels, queues, routing, agent desktop, telephony** | **M27** | M32 answers; M27 carries the conversation |
| **Message delivery, consent and DND enforcement** | **M27** | The delivery layer is the only enforceable control point |
| **Model training, registry, serving infrastructure, evaluation** | **M26** | M32 is a consumer of models, not a model factory |
| **AI governance policy and model cards** | **M26** | One governance regime for every model in the estate |
| Knowledge article authoring and maintenance | **M61** | M32 retrieves; M61 owns the content and its accuracy |
| Party identity, consent record | **M33** | Master data |
| Price calculation | **M11** | M32 may **quote** a price only by calling M11; it never computes one |
| Service order state and lifecycle | **M01** | M32 creates and reads through the API |
| Satisfaction measurement | **M34** | M32 triggers the rating; M34 owns the metric |
| Internal employee assistant | **M66** | Different audience, different data scope |
| Marketplace seller assistant | **M12** | Different party class and permission model |

### 3.3 Shared Concepts

| Concept | M32's Role | Owning Module |
|---|---|---|
| Conversation | Participates in | M27 |
| Intent | **Owns detection**; M27 uses it for routing | M32 |
| Model | Consumes | M26 |
| Knowledge article | Retrieves and cites | M61 |
| Guard rail | **Owns the assistant's rails**; M26 owns platform-wide AI policy | M32 / M26 |
| Handoff | **Owns the decision**; M27 owns the destination | M32 / M27 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Enterprise conversational AI practice (2026)** | LLM paired with **RAG grounding** and **agentic workflows that complete tasks, not just reply**; production chatbots integrate with CRM | **Grounding plus action** as the core design. An assistant that cannot check a real order status is a menu with extra steps | Fully autonomous agents acting without confirmation on material outcomes |
| **AI guardrails platforms** | Application-layer controls before and after inference: input validation, output filtering for PII and policy violations, hallucination prevention through RAG, compliance enforcement through access controls and audit trails | **The full guardrail stack**, implemented as a distinct layer rather than prompt instructions | Guardrails expressed only in the system prompt — they are trivially bypassed |
| **Handoff practice** | The AI-to-human handoff **carries the highest operational risk**; escalation should trigger on **emotional signals** (frustration, distress), **operational signals** (SLA timers approaching breach) and **technical signals** (guardrail violations, low-confidence responses) | **All three signal categories** as explicit, separately-tunable handoff triggers | Confidence-only escalation, which misses the angry customer the model understood perfectly |
| **Hallucination mitigation** | Grounding responses through RAG with **confidence-based escalation thresholds routing uncertain interactions to human agents** | Confidence thresholds calibrated per intent class, not one global number | — |
| **Bangla NLP practice** | Vendors should confirm they have shipped Bangla or bilingual agents; language handling differs materially from English-only builds | **Bengali is the design language, not a translation layer**; evaluation set is Bengali-first | Building in English and translating |
| **Ollama + open-weight models** | Self-hosted inference, no per-query cost, data stays on-premises | Self-hosting — required because conversations contain personal data under the PDPA | Third-party API inference on customer conversation data |

**Design position.** Five deliberate differences.

First, **the assistant never states a price it computed itself**. Every price comes from a
call to M11. If M11 cannot price it, the assistant says so and offers a human. Invented prices
are the single fastest way to destroy commercial trust and create disputes the Company must
honour.

Second, **guard rails are a code layer, not prompt text**. Input validation, output filtering
and policy enforcement sit outside the model. A model instructed not to discuss competitors
will discuss competitors; a filter that blocks it will not.

Third, **handoff triggers on three independent signal families** — emotional, operational and
technical — each separately tunable. The most damaging failure in deployed assistants is not
a wrong answer; it is refusing to escalate a distressed customer.

Fourth, **Bengali-first with mixed-script tolerance**. Real customer messages combine Bengali
script, romanised Bengali and English in one sentence. The evaluation set is built from actual
1000FiX conversations, not translated English test cases.

Fifth, **actions require authentication and, above a threshold, confirmation**. The assistant
may check status freely. It may book a service after identity verification. It may not
authorise a repair above the approval threshold, cancel a contract, or issue a refund — those
route to a human every time.

---

## 5. Functional Areas & Features

### 5.1 Language Understanding

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAI-001 | **Bengali-first understanding** | Understand customer input in Bengali script, romanised Bengali, English and mixed-script sentences within a single message | **P1** | L4 |
| FR-CAI-002 | Intent classification | Classify input into a maintained intent taxonomy covering status, booking, pricing, warranty, complaint, product, location, payment and account intents | P1 | L5 |
| FR-CAI-003 | Entity extraction | Extract order numbers, device serials, IMEI, brand, model, dates, times, branch names, amounts and addresses, tolerant of Bengali numerals and local formats | P1 | L5 |
| FR-CAI-004 | Sentiment and emotion detection | Detect frustration, distress, urgency and satisfaction as a handoff signal and as a data point for M34 | P1 | L4 |
| FR-CAI-005 | Ambiguity handling | Ask a clarifying question rather than guessing when intent confidence is split | P1 | L5 |
| FR-CAI-006 | Multi-intent handling | Recognise more than one intent in a message and address them in sequence | P2 | L5 |
| FR-CAI-007 | Voice input | Accept Bengali speech input where the channel supports it, via speech-to-text from M26 | P3 | L4 |
| FR-CAI-008 | Out-of-scope detection | Recognise input outside the assistant's domain and route it rather than attempting an answer | **P1** | L5 |

### 5.2 Dialogue & Context

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAI-009 | Multi-turn context | Maintain context across turns within a conversation, including entities established earlier | P1 | L5 |
| FR-CAI-010 | Conversation memory | Recall the customer's recent orders, devices and prior conversations to avoid asking what the system already knows | P1 | L5 |
| FR-CAI-011 | Topic switching | Handle a mid-conversation topic change without losing the original thread | P2 | L5 |
| FR-CAI-012 | Conversation repair | Recover gracefully when the customer indicates the assistant misunderstood | P1 | L5 |
| FR-CAI-013 | Proactive prompts | Offer the likely next action based on the customer's open items — for example, offering status when the customer has an in-progress repair | P2 | L5 |
| FR-CAI-014 | Session continuity | Resume a conversation across a channel switch or a session gap, within a defined window | P2 | L5 |

### 5.3 Grounding & Knowledge

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAI-015 | **Retrieval-augmented grounding** | Ground every substantive answer in retrieved content from M61 knowledge or live ERP data; never answer a factual question from model parameters alone | **P0** | L5 |
| FR-CAI-016 | **Citation** | Attach the source of each grounded statement, visible to the agent on handoff and available for audit | **P1** | L5 |
| FR-CAI-017 | Live data retrieval | Retrieve current service order status, technician ETA, warranty validity, contract entitlement, invoice balance and branch details through the module APIs | **P1** | L5 |
| FR-CAI-018 | Knowledge freshness | Reflect knowledge article changes from M61 within a defined interval; never serve retired content | P1 | L5 |
| FR-CAI-019 | **No-answer behaviour** | State plainly that it does not know and offer a human, rather than generating a plausible answer | **P0** | L5 |
| FR-CAI-020 | Bilingual response | Respond in the customer's language, matching their script choice, with correct Bengali typography | **P1** | L5 |

### 5.4 Actions

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAI-021 | Identity verification | Verify the customer's identity through an authenticated session or a one-time code before performing any action or disclosing personal data | **P0** | L5 |
| FR-CAI-022 | Status enquiry | Answer service order, consignment, warranty claim and invoice status without action authority | P1 | L5 |
| FR-CAI-023 | Service booking | Create a service order, capture the complaint, offer available slots and confirm the booking | P1 | L5 |
| FR-CAI-024 | Rescheduling | Reschedule an appointment or a collection within policy | P1 | L5 |
| FR-CAI-025 | **Price quotation** | Quote a price **only** by calling M11; never compute, estimate or approximate one | **P0** | L5 |
| FR-CAI-026 | Warranty check | Check warranty validity by serial and purchase date, and explain the outcome | P1 | L5 |
| FR-CAI-027 | Payment link | Issue a payment link for an outstanding invoice through M20 | P2 | L5 |
| FR-CAI-028 | Complaint capture | Capture a complaint and raise it to M34, with acknowledgement to the customer | P1 | L5 |
| FR-CAI-029 | **Action authority limits** | Perform only actions within its defined authority; route contract cancellation, refunds, goodwill credit and repair approval above the threshold to a human, always | **P0** | L5 |
| FR-CAI-030 | Action confirmation | Restate the action and obtain explicit confirmation before executing anything that creates a commitment | **P1** | L5 |

### 5.5 Guard Rails & Safety

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAI-031 | **Input validation** | Screen input for prompt injection, jailbreak patterns and malicious content before inference | **P0** | L5 |
| FR-CAI-032 | **Output filtering** | Screen output for personal data leakage, policy violations, competitor commentary, medical or legal advice, and unauthorised commitments | **P0** | L5 |
| FR-CAI-033 | **Scope enforcement** | Refuse politely and route anything outside the defined domain | **P0** | L5 |
| FR-CAI-034 | **Safety escalation** | Detect distress, threat, safety risk or vulnerability indicators and escalate immediately to a human with priority | **P0** | L5 |
| FR-CAI-035 | **Audit trail** | Log every turn with input, retrieved context, model version, output, guard rails fired, confidence and action taken | **P0** | L5 |

### 5.6 Handoff & Agent Assistance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAI-036 | **Handoff decision** | Escalate on **emotional signals** (frustration, distress), **operational signals** (SLA risk, repeat contact, high-value customer) and **technical signals** (low confidence, guardrail fired, out of scope, action beyond authority) — each independently tunable | **P0** | L5 |
| FR-CAI-037 | Handoff package | Pass to M27 the full transcript, detected intent, extracted entities, actions taken, sources cited, sentiment and the explicit handoff reason | **P1** | L5 |
| FR-CAI-038 | Agent assistance | Supply the human agent with a conversation summary, suggested replies and next-best-action, always editable and never auto-sent | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Self-hosted inference** | Inference runs on Company infrastructure. Customer conversation content does not leave it — a PDPA requirement, not a preference |
| T-02 | **Guard rails outside the model** | Input and output filters are deterministic code executing before and after inference. They cannot be overridden by conversational input |
| T-03 | **Grounding enforcement** | A response to a factual question is emitted only when accompanied by at least one retrieved source; ungrounded factual output is blocked, not corrected |
| T-04 | **Price call, never price generation** | Any numeric price in output must trace to an M11 response within the turn. Output containing an unmatched currency amount is blocked |
| T-05 | **Confidence calibration per intent** | Thresholds are set per intent class from a labelled evaluation set, not by a single global number |
| T-06 | **Bengali evaluation set** | The regression set is built from real 1000FiX conversations in Bengali, romanised Bengali and mixed script, and is versioned with the model |
| T-07 | **Deterministic action execution** | Actions execute through the same authenticated APIs a human uses, with the assistant as an identified actor in the audit trail |
| T-08 | **Latency budget** | First token within 1.5 s; complete response within 4 s for a grounded answer; a timeout hands off rather than waits |
| T-09 | **Graceful degradation** | If inference or retrieval is unavailable, the assistant hands off to a human rather than degrading to ungrounded generation |
| T-10 | **Model versioning** | Every conversation records the model and prompt version used, so a regression can be traced to a release |
| T-11 | **Shadow evaluation** | A candidate model runs alongside production on live traffic without responding, and is promoted only on measured improvement |
| T-12 | **Prompt injection resistance** | Retrieved content is treated as untrusted data, never as instruction |
| T-13 | **Conversation data handling** | Transcripts used for improvement are anonymised; **recovered customer data from M06 is never used for training** (BRU-AIM-03) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M32 |
|---|---|---|
| **Customer** | Waits in a queue to ask a question the system could answer instantly | Gets an answer in seconds, in Bengali, at any hour, and reaches a human when it matters |
| **Contact centre agent** | Answers the same simple question hundreds of times a day | Handles the conversations that need judgement, with a summary already written |
| **Customer Service Manager** | Adds headcount as volume grows | Absorbs volume growth without proportional hiring |
| **Marketing** | Cannot support a campaign spike | Campaign response is absorbed by the assistant |
| **Branch staff** | Interrupted by status calls | Fewer interruptions; more counter throughput |
| **Knowledge owner (M61)** | Writes articles nobody reads | Sees which articles the assistant retrieves and which questions have no article |
| **CTO** | — | Has a measurable containment rate and a clear improvement loop |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **First-contact resolution without a human** | Grounded answers plus authenticated actions on the highest-volume intents | **> 55% AI containment** of first contacts |
| **24/7 coverage at no marginal cost** | Self-hosted assistant available continuously | Delivers the business plan's round-the-clock commitment for routine enquiries without night staffing |
| **Contact centre capacity** | Every contained conversation is an agent conversation not needed | At 55% containment, the equivalent of a materially larger agent team without hiring |
| **Zero per-query inference cost** | Self-hosted rather than API-metered | Avoids a variable cost that scales with success |
| **Faster answers** | Seconds rather than queue time | Direct contributor to satisfaction and to the **CSAT 4.7/5** target |
| **Knowledge gap discovery** | Unresolved intents show precisely what the knowledge base lacks | Makes M61 investment targeted rather than speculative |
| **Bengali service quality** | First-language service for the majority of customers | Meaningful differentiation in the Bangladeshi market |
| **Campaign elasticity** | Response spikes absorbed without pre-staffing | Enables M35 to campaign more aggressively |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Bengali-first as a stated commitment** | Most conversational AI in this market is English-first with Bengali bolted on; doing it properly is a visible differentiator |
| **Demonstrable AI governance** | Guard rails, citations, audit trail and human oversight are what make AI defensible to a corporate client or a regulator |
| **The assistant's failures are visible** | Containment, handoff reasons and unresolved intents are measured, so the capability improves rather than stagnating |
| **Agents move up the value chain** | Removing repetitive work is what makes contact centre work sustainable and reduces attrition |
| **A path to internal assistance** | The same platform, differently scoped, serves M66 internal IT support later |
| **Data stays home** | Self-hosting is a genuine assurance to corporate clients who ask where their conversations go |

---

## 8. Lifecycle & State Models

### 8.1 Assistant Turn

```
   CUSTOMER INPUT
        |
   +----v-------------------+     malicious / injection detected
   | INPUT VALIDATION       |--------------------------> BLOCKED (logged, generic response)
   +----+-------------------+
        |
   +----v-------------------+
   | INTENT + ENTITIES      |
   | + SENTIMENT            |
   +----+-------------------+
        |
   +----v-------------------+     out of scope
   | SCOPE CHECK            |--------------------------> HANDOFF (routed politely)
   +----+-------------------+
        |
   +----v-------------------+     identity required, not verified
   | AUTHORISATION CHECK    |--------------------------> VERIFY IDENTITY --> retry
   +----+-------------------+
        |
   +----v-------------------+
   | RETRIEVAL              |  knowledge (M61) + live ERP data
   +----+-------------------+
        |
   +----v-------------------+     no sources retrieved
   | GROUNDING CHECK        |--------------------------> "I don't know" + HANDOFF
   +----+-------------------+
        |
   +----v-------------------+
   | INFERENCE              |  self-hosted, model + prompt version recorded
   +----+-------------------+
        |
   +----v-------------------+     PII leak / policy breach / unmatched price
   | OUTPUT FILTER          |--------------------------> BLOCKED --> HANDOFF
   +----+-------------------+
        |
   +----v-------------------+     below threshold for this intent class
   | CONFIDENCE CHECK       |--------------------------> HANDOFF
   +----+-------------------+
        |
   +----v-------------------+
   | ACTION (if any)        |  within authority; confirmed if it creates a commitment
   +----+-------------------+
        |
   +----v-------------------+
   | RESPOND + LOG          |  turn, sources, model version, guard rails, confidence
   +------------------------+
```

### 8.2 Handoff Decision

```
                        HANDOFF TRIGGERS
                        (any one is sufficient)

   EMOTIONAL                 OPERATIONAL              TECHNICAL
   ---------                 -----------              ---------
   frustration detected      SLA at risk              confidence below threshold
   distress or vulnerability repeat contact           guard rail fired
   explicit request          high-value customer      out of scope
   for a human               contract entitlement     action beyond authority
   abusive or unsafe         complaint intent         retrieval returned nothing
   content                                            inference unavailable

                                |
                    +-----------v-----------+
                    |  HANDOFF PACKAGE      |
                    |  transcript           |
                    |  intent + entities    |
                    |  actions taken        |
                    |  sources cited        |
                    |  sentiment            |
                    |  handoff reason       |
                    +-----------+-----------+
                                |
                                v
                    M27 HUMAN QUEUE (priority set by trigger)
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-CAI-01 | **A factual answer must be grounded in a retrieved source; ungrounded factual output is blocked** | **H** | CTO |
| BRU-CAI-02 | **The assistant never states a price it did not obtain from M11** | **H** | CCO |
| BRU-CAI-03 | **The assistant never discloses personal data before identity verification** | **H** | CDO |
| BRU-CAI-04 | The assistant may not cancel a contract, issue a refund, grant goodwill credit, or approve a repair above the threshold | **H** | CCO |
| BRU-CAI-05 | An action creating a commitment requires explicit customer confirmation | **H** | CCO |
| BRU-CAI-06 | **Detected distress, threat or vulnerability escalates immediately with priority** | **H** | Customer Service Manager |
| BRU-CAI-07 | **An explicit request for a human is honoured immediately, without persuasion or deflection** | **H** | Customer Service Manager |
| BRU-CAI-08 | Guard rails execute outside the model and cannot be altered by conversational input | **H** | CTO |
| BRU-CAI-09 | Retrieved content is data, never instruction | **H** | CTO |
| BRU-CAI-10 | Every turn is logged with input, sources, model version, guard rails fired, confidence and action | **H** | CTO |
| BRU-CAI-11 | If inference or retrieval is unavailable, the assistant hands off rather than generating ungrounded output | **H** | CTO |
| BRU-CAI-12 | **Recovered customer data from M06 is never used as training or retrieval data** | **H** | CDO |
| BRU-CAI-13 | The customer is told they are speaking to an automated assistant | **H** | CDO / Legal |
| BRU-CAI-14 | A model is promoted to production only after passing the Bengali evaluation set and shadow evaluation | **H** | CTO |
| BRU-CAI-15 | Transcripts used for improvement are anonymised before use | **H** | CDO |

*Classification: **H** hard block · **A** approved override · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.assistant.session` | `fix_assistant_session` | One assistant engagement | conversation_id, party_id, channel, started_at, ended_at, outcome, contained, handoff_reason, model_version |
| `fix.assistant.turn` | `fix_assistant_turn` | One exchange | session_id, sequence, input_text, detected_language, intent, intent_confidence, entities_json, sentiment, retrieved_sources, output_text, guardrails_fired, action_taken, latency_ms |
| `fix.intent.taxonomy` | `fix_intent_taxonomy` | Maintained intent set | code, name, description, category, authority_level, confidence_threshold, example_utterances, active |
| `fix.entity.definition` | `fix_entity_definition` | Extractable entities | code, type, extraction_rules, validation, examples |
| `fix.grounding.source` | `fix_grounding_source` | What was retrieved | turn_id, source_type, source_id, snippet_ref, relevance_score, used_in_response |
| `fix.guardrail.rule` | `fix_guardrail_rule` | Guard rail definition | code, stage (input/output), rule_type, pattern_or_classifier, action, severity, active |
| `fix.guardrail.event` | `fix_guardrail_event` | Guard rail firing | turn_id, rule_code, matched_content_ref, action_taken, occurred_at |
| `fix.assistant.action` | `fix_assistant_action` | Action performed | turn_id, action_type, target_module, target_ref, parameters_json, confirmed_by_customer, executed_at, outcome |
| `fix.handoff.record` | `fix_handoff_record` | Escalation to human | session_id, trigger_category, trigger_detail, package_ref, queue_id, handed_off_at |
| `fix.assistant.config` | `fix_assistant_config` | Behaviour configuration | version, prompt_template, intent_thresholds_json, authority_matrix_json, published_at, published_by |
| `fix.evaluation.set` | `fix_evaluation_set` | Bengali regression corpus | version, case_count, language_mix, created_at |
| `fix.evaluation.result` | `fix_evaluation_result` | Model performance | model_version, evaluation_set_version, intent_accuracy, grounding_rate, guardrail_precision, run_at |
| `fix.unresolved.intent` | `fix_unresolved_intent` | Improvement queue | session_id, input_text, best_guess_intent, confidence, reviewed, disposition, knowledge_gap_ref |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.conversation`, `fix.conversation.message` | M27 | Participates; reads history |
| `fix.knowledge.article` | M61 | Retrieved and cited |
| `fix.party` | M33 | Identity and context after verification |
| `fix.consent.record` | M33 | Lawful basis for processing conversation content |
| `fix.service.order` | M01 | Status enquiry and creation |
| `fix.warranty.register` | M09 | Warranty validity check |
| `fix.price.book` | M11 | **Price retrieval — the only source of a quoted price** |
| `fix.model` | M26 | Model serving and version |
| `fix.complaint` | M34 | Complaint raised from conversation |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-CAI-01 | Customer message received on an AI-enabled channel | Run the full turn pipeline: validate, classify, authorise, retrieve, infer, filter, respond | Hand off to human |
| AUT-CAI-02 | Confidence below the intent threshold | Hand off with the low-confidence reason | — |
| AUT-CAI-03 | Guard rail fires | Block the output, log, hand off where the rail requires it | — |
| AUT-CAI-04 | **Distress, threat or vulnerability detected** | **Escalate immediately with priority; notify the supervisor** | **Escalate through all available paths** |
| AUT-CAI-05 | Customer requests a human | Hand off immediately without persuasion | — |
| AUT-CAI-06 | Retrieval returns no relevant source | Respond that it does not know; offer a human; log as a knowledge gap | — |
| AUT-CAI-07 | Action requested beyond authority | Explain the limit and hand off | — |
| AUT-CAI-08 | Session ends without resolution | Log to the unresolved queue for review | — |
| AUT-CAI-09 | Knowledge article updated in M61 | Re-index within the freshness interval | Alert on index staleness |
| AUT-CAI-10 | Weekly | Review unresolved intents; produce the knowledge gap report for M61 | — |
| AUT-CAI-11 | Candidate model available from M26 | Run the Bengali evaluation set; run shadow evaluation on live traffic | Block promotion on failure |
| AUT-CAI-12 | Handoff occurs | Construct and attach the handoff package to the M27 conversation | Hand off with transcript only; alert |
| AUT-CAI-13 | Inference latency exceeds budget | Abandon inference and hand off | — |

---

## 12. Interfaces

### 12.1 Upstream — M32 Consumes

| Source | What | Mechanism |
|---|---|---|
| M27 Contact Centre | Customer message, channel context, conversation history | Synchronous call |
| M26 AI/ML Services | Model serving, embeddings, speech-to-text, sentiment | REST with timeout |
| M61 Knowledge | Knowledge articles for retrieval and citation | Vector index + REST |
| M33 Party Master | Party identity after verification; consent status | REST |
| M01 Service Order | Order status, slot availability | REST |
| M09 Warranty | Warranty validity by serial | REST |
| **M11 Pricing** | **Price — the only permitted source of a quoted amount** | **REST, synchronous** |
| M03 Logistics | Consignment status | REST |
| M20 Receivable | Invoice balance, payment link | REST |
| M08 Contract | Entitlement context | REST |

### 12.2 Downstream — M32 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M27 Contact Centre** | **Response, intent, confidence, handoff decision and package, agent summary and suggestions** | **Synchronous response** |
| M01 Service Order | Service orders created by the assistant | Command |
| M34 Customer Experience | Complaints raised; sentiment signal | Event |
| M07 CRM | Leads identified in conversation | Event |
| M61 Knowledge | Knowledge gap report from unresolved intents | Event + report |
| M26 AI/ML | Evaluation results, override and correction signals | Warehouse extract |
| M25 Business Intelligence | Containment, intent distribution, handoff reasons, latency | Warehouse extract |
| M60 GRC | Guard rail events, audit trail | Event |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `assistant.session_started` | session, party, channel, model version | M25 |
| `assistant.intent_detected` | session, intent, confidence, entities | M27, M25 |
| `assistant.action_executed` | session, action, target, confirmed | Target module, M60 |
| `assistant.contained` | session, intent, turns, duration | M25, M34 |
| **`assistant.handoff`** | **session, trigger category, reason, package** | **M27** |
| **`guardrail.fired`** | **turn, rule, severity, action** | **M60, M26** |
| `assistant.knowledge_gap` | intent, input, frequency | M61 |
| `assistant.unresolved` | session, best-guess intent, transcript | M61, M26 |
| `sentiment.detected` | session, party, sentiment, intensity | M34 |
| `model.evaluation_completed` | model version, scores, pass or fail | M26, CTO |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/assistant/turn` | POST | Process one customer turn and return a response or handoff | **M27** |
| `/api/v1/assistant/summary/{conversation}` | GET | Conversation summary for the agent | M27, P10 |
| `/api/v1/assistant/suggest/{conversation}` | GET | Suggested replies and next-best-action | M27, P10 |
| `/api/v1/assistant/config` | GET / PUT | Intent taxonomy, thresholds, authority matrix | P03 |
| `/api/v1/assistant/evaluate` | POST | Run the evaluation set against a candidate model | M26, CI |
| `/api/v1/assistant/unresolved` | GET | Improvement queue | P03, M61 |
| `/api/v1/assistant/analytics` | GET | Containment, intents, handoff reasons | P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| Customer Service Manager | C R U D A | Intent taxonomy, thresholds, authority matrix, unresolved queue |
| R35 Contact Centre Supervisor | R U | Unresolved queue, handoff analysis |
| R34 Contact Centre Agent | R | Assistant summary and suggestions on handed-off conversations |
| R02 Chief Technology Officer | R U A | Guard rails, model promotion, configuration versions |
| **R40 Chief Data Officer** | R A | Guard rail events, audit trail, anonymisation of training data |
| R32 Quality Manager / ISO Coordinator | R | Assistant conversation quality and complaint linkage |
| Knowledge owner (M61) | R | Knowledge gap report and retrieval analytics |
| R36 Customer | — | Interacts with the assistant; no configuration access |

**Field-level restrictions.** Conversation content is accessible to supervisors and the CDO
only. The training corpus is anonymised before any access.

**Segregation of duties.** The person who authors a guard rail cannot be the sole approver of
its removal (SOD-20).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Containment dashboard | Customer Service Manager, CTO | Daily | Sessions, contained, handed off, by intent and channel |
| **Handoff reason analysis** | **Customer Service Manager** | **Weekly** | Handoffs by trigger category — emotional, operational, technical — with trend |
| Intent distribution | Customer Service Manager, M61 owner | Weekly | Volume by intent; emerging intents not in the taxonomy |
| **Knowledge gap report** | **M61 owner, Customer Service Manager** | **Weekly** | Questions with no retrievable answer, ranked by frequency |
| **Guard rail firing report** | **CTO, CDO, GRC** | **Weekly** | Rails fired by type; false-positive review; attempted injections |
| Grounding rate | CTO | Weekly | Proportion of factual answers with a cited source — target 100% |
| Model performance | CTO, M26 | Per release | Bengali evaluation scores, shadow comparison, regression check |
| Latency | CTO | Daily | First token and full response times against budget |
| Customer satisfaction — AI vs human | Customer Service Manager, M34 | Monthly | Rating comparison by intent class |
| Action audit | GRC, CDO | Monthly | Actions performed by the assistant, confirmations, outcomes |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-174 | **AI first-contact resolution (containment)** | 0% | 42% | **> 55%** |
| KPI-175 | Bengali intent accuracy | n/a | 84% | **> 88%** |
| KPI-176 | **Grounding rate on factual answers** | n/a | **100%** | **100%** |
| KPI-177 | **Prices quoted without an M11 call** | n/a | **0** | **0** |
| KPI-178 | Handoff on explicit customer request — honoured immediately | n/a | **100%** | **100%** |
| KPI-179 | Distress escalation latency | n/a | < 10 s | **< 5 s** |
| KPI-180 | First-token latency (p95) | n/a | < 2 s | **< 1.5 s** |
| KPI-181 | Full response latency (p95) | n/a | < 5 s | **< 4 s** |
| KPI-182 | Customer satisfaction — AI-handled conversations | n/a | > 3.9/5 | **> 4.2/5** |
| KPI-183 | Successful prompt injections | n/a | **0** | **0** |
| KPI-184 | Knowledge gaps closed within 30 days of identification | n/a | 60% | **> 80%** |
| KPI-185 | Sessions with complete audit record | n/a | **100%** | **100%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L4 | Ollama self-hosted inference; vector store; embedding model | 30% |
| L5 | `cd_assistant`, `cd_intent`, `cd_grounding`, `cd_guardrail`, `cd_assistant_actions` | 70% |

### 16.2 Custom Development

> CD identifiers are **provisional** pending the unified register in `02-05` (audit H-03).

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-053 | `cd_assistant` — session, turn pipeline, dialogue management, context | Service | 5 PW |
| CD-054 | `cd_intent` — taxonomy, classification, entity extraction, Bengali handling | Service | 4 PW |
| CD-055 | **`cd_grounding`** — retrieval, citation, freshness, no-answer behaviour | Service | **4 PW** |
| CD-056 | **`cd_guardrail`** — input validation, output filtering, scope, safety, audit | Service | **3 PW** |
| CD-057 | `cd_assistant_actions` — authenticated action execution and authority matrix | Service | 2 PW |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M32 is scheduled in **W4** (P1) but declares a dependency on 2 module(s) that land later: **M26** (W6); **M61** (W6). One of three things must be true before the W4 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W4 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M32 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W4 plan for M32 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| **M27 Contact Centre** | **Blocking** — the assistant has no channel without it |
| **M61 Knowledge** | **Blocking** — grounding requires content to retrieve. An assistant without a knowledge base can only answer from live ERP data |
| M26 AI/ML Services | Model serving, embeddings, sentiment |
| M33 Party Master | Identity verification and consent |
| M01, M09, M11, M20 | The APIs the assistant calls for status, warranty, price and payment |
| **Bengali evaluation set built** | **Blocking for go-live** — a model cannot be promoted without it |

> **Dependency warning.** M61 Knowledge is scheduled for **Wave 6**, but M32 is scheduled for
> **Wave 4**. An assistant deployed without a knowledge base can answer status and
> transactional questions from live ERP data, but cannot answer "how do I", "why is my device
> doing this" or "what does this mean" — which are a large share of real enquiries. Either
> **M61 core content moves to W4**, or **M32 launches with a reduced intent scope** limited to
> transactional enquiries. This is a **wave-plan decision** for `06-01`.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing FAQ content on the website | Unknown | M61, then indexed | W4 |
| Historical chat transcripts, if any exist | To be profiled | Evaluation set and intent taxonomy | W4 |
| Intent taxonomy | **Authored, not migrated** — built from contact reason analysis in M27 | `fix.intent.taxonomy` | W4 |

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **No factual answer is emitted without a cited source** | **Negative test; grounding rate report at 100%** |
| AC-02 | **No price appears in output that did not come from an M11 call** | **Negative test; output filter verification** |
| AC-03 | **Personal data is not disclosed before identity verification** | **Negative test across all intents** |
| AC-04 | An explicit request for a human is honoured on the same turn | Test across all channels |
| AC-05 | **Detected distress escalates within 5 seconds with priority** | **Timed test with a scripted distress corpus** |
| AC-06 | Guard rails cannot be bypassed by conversational input | **Red-team test with 200 injection and jailbreak attempts** |
| AC-07 | Retrieved content cannot act as instruction | Injection test with poisoned knowledge content |
| AC-08 | The assistant handles Bengali script, romanised Bengali, English and mixed-script input | Bengali evaluation set at ≥ 88% intent accuracy |
| AC-09 | Actions beyond authority are refused and handed off | Negative test for cancellation, refund, goodwill and high-value approval |
| AC-10 | An action creating a commitment is confirmed before execution | Test across booking, rescheduling and payment |
| AC-11 | Inference or retrieval unavailability results in handoff, never ungrounded generation | Fault-injection test |
| AC-12 | Every turn is logged with input, sources, model version, rails and confidence | Audit record review |
| AC-13 | The handoff package reaches the agent complete | End-to-end test with M27 |
| AC-14 | The customer is told they are speaking to an automated assistant | Conversation opening review |
| AC-15 | Inference runs on Company infrastructure; no conversation content leaves it | Network and data-flow audit |
| AC-16 | Customer Service Manager, CTO and Chief Data Officer sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Does M61 core knowledge content move to Wave 4, or does M32 launch with transactional intents only?** | CTO / PMO | **Before W4 build** |
| Q-02 | Which open-weight model is selected, and what inference hardware is required? | CTO | W4 minus 3 months |
| Q-03 | What is the authority matrix — precisely which actions may the assistant perform unaided? | CCO / Customer Service Manager | **W4 build** |
| Q-04 | Are historical chat transcripts available to build the evaluation set and intent taxonomy? If not, the taxonomy is built from M27 contact reason analysis, which requires M27 to have run for a period. | Customer Service Manager | **W4 minus 4 months** |
| Q-05 | Does the assistant operate on WhatsApp, and does that require a separate Meta approval? | Customer Service Manager / Legal | W4 design |
| Q-06 | What is the disclosure wording that tells the customer they are speaking to an assistant, in Bengali and English? | Legal / CDO | W4 build |
| Q-07 | Is voice input in scope, or text only at launch? | Customer Service Manager | W4 design |
| Q-08 | Who owns the intent taxonomy on an ongoing basis — this is a continuing editorial role, not a one-off build task | Customer Service Manager | W4 minus 2 months |

**Q-04 is the practical constraint.** Without real Bengali conversation data, the evaluation
set will be synthetic, and a model that passes a synthetic set will fail on real customers.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §4 (M27/M32 boundary) ·
`M27_Omnichannel_Contact_Centre_and_Communications.md` ·
`03_Modules/J_Data_Analytics_and_Intelligence/_CATEGORY_OVERVIEW.md` §7 (AI governance — ten
non-negotiable rules), §6 (model portfolio) ·
`03_Modules/I_Governance_Risk_Quality_and_Knowledge/_CATEGORY_OVERVIEW.md` §4 (M61 knowledge) ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3

**Workspace evidence**
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Customer Support (chatbot
configuration) · `1000fix_business/Business planning for 1000 fix.docx` §24/7 Technical
Support (knowledge base and self-service) ·
`ERP system for 1000 fix/1000FiX_ERP_Technology_Stack_Specification.md` §6.10 (Rasa to LLM
divergence, self-hosting rationale) ·
`Intergrated_web_portal/.../IMPL-23_AI_Chatbot_Implementation_Guide_Rasa_3.6.md`,
`IMPL-43_Enhanced_AI_Chatbot_90_Resolution_GPT4_Hybrid.md`

**External benchmark and regulation** *(verified 2026-08-12)*
Enterprise conversational AI practice — production systems pair an LLM with **RAG grounding
and agentic workflows that complete tasks**, integrated with the CRM ·
AI guardrails practice — application-layer controls before and after inference covering input
validation, output filtering for PII and policy violations, hallucination prevention through
RAG, and compliance enforcement through access controls and audit trails ·
Handoff practice — the AI-to-human handoff carries the highest operational risk; escalation
should trigger on **emotional**, **operational** and **technical** signal categories ·
Hallucination mitigation — grounding with **confidence-based escalation thresholds routing
uncertain interactions to human agents** · Bangla NLP practice — language handling differs
materially from English-only builds · Ollama self-hosted inference ·
**Bangladesh Personal Data Protection Act 2026** — lawful basis and disclosure for automated
processing of personal data in conversation

---

*Module M32 · Category B · 1000FiX ERP System v2.0 · CONFIDENTIAL*
