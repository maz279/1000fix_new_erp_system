---
id: HC-017
title: Conversational AI Intent and Utterance Library
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design with AI
author: Content Design with AI Engineering and Localisation
reviewers: [CTO, AI Lead, Customer Service Manager, Legal Counsel, Localisation Lead, BI Lead, Programme Content Lead]
approver: Content Design Lead with CTO
content_class: D
purpose: >
  The intent taxonomy, training utterances in Bengali and English, entity slots and disambiguation
  prompts that M32 is trained and evaluated against. An assistant with ad-hoc intents cannot be
  regression-tested: there is no set to test against, so every model change is a leap of faith and
  every reported failure is unreproducible.
traces_to: [M32, M26, M27, M61, P01, P10, MD-021, MD-024, MD-026, HC-001, HC-002, HC-015, HC-018, HC-019, BN-003, BN-016, LG-008, CG-010, CG-012]
priority: P2
wave: W6
bilingual: yes
bn_counterpart: HC-017_Conversational_AI_Intent_and_Utterance_Library_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32 §5.1 FR-CAI-001 Bengali-first understanding across Bengali script, romanised Bengali, English and mixed-script within a single message; FR-CAI-002 intent classification against a maintained taxonomy; FR-CAI-003 entity extraction tolerant of Bengali numerals and local formats; FR-CAI-005 ambiguity handling; FR-CAI-008 out-of-scope detection
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32 §9 BRU-CAI-14 — a model is promoted to production only after passing the Bengali evaluation set and shadow evaluation; BRU-CAI-15 transcripts used for improvement are anonymised before use
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md — chatbot utterances: users type what they actually say; translated utterances train the model on Bengali nobody uses
    verified: 2026-08-18
    class: P1
  - source: Personal Data Protection Ordinance 2025 (Bangladesh), issued 6 November 2025 and finalised as the Personal Data Protection Act, 2026 (Law 63 of 2026) — applies to entities processing personal data within Bangladesh; explicit consent for collection; data-subject rights; enforcement mechanisms expected from around 13 May 2027
    verified: 2026-08-18
    class: P1
    note: Applicability to the mining of customer utterances for model training must be confirmed by Legal — see Open Item O-02
supersedes: none
review_due: 2027-02-18
---

# HC-017 — Conversational AI Intent and Utterance Library

> **This is the file that makes `M32` testable.** `BRU-CAI-14` prohibits promoting a model to
> production until it passes the Bengali evaluation set. That evaluation set is built from this
> library, and without it the rule cannot be enforced — a model would be promoted on the strength
> of a demonstration.

---

## 1. Purpose

`M32` `FR-CAI-002` requires intent classification against **a maintained intent taxonomy**. The
word that carries the requirement is *maintained*.

| Without a governed library | Consequence |
|---|---|
| Intents added ad hoc during build | No two evaluations measure the same thing |
| Utterances written by the build team | The model learns the vocabulary of people who built it, not of people who use it |
| **Bengali utterances translated from English** | `CG-010` states it precisely: *"translated utterances train the model on Bengali nobody uses"* |
| No evaluation set | `BRU-CAI-14` unenforceable; regression invisible |
| No disambiguation design | `FR-CAI-005` requires a clarifying question rather than a guess — but which question? |

**Consequence of absence (`CP-03`).** `M32` cannot be evaluated, cannot be regression-tested, and
cannot be improved deliberately. Every release is a hope, and every failure report is
unreproducible.

---

## 2. Scope

**In scope:** the intent taxonomy and its structure; the intent schema (§4.2, required by `CG-009`
§3); utterance collection, authoring and coverage; entity slots and their master-data binding;
disambiguation prompts; out-of-scope and negative examples; the evaluation set; and rules
`IL-01`…`IL-20`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| What the assistant **says** in reply | [`HC-018_Conversational_AI_Response_and_Fallback_Copy.md`](HC-018_Conversational_AI_Response_and_Fallback_Copy.md) |
| Disclosure, refusal, guardrail and handover wording | [`HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md`](HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md) |
| The grounding corpus | [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) §4.8 · `KB-001` §4.8 |
| Model architecture, training, serving, guard-rail implementation | `M32`, `M26` |
| FAQ content | [`../HC-015_FAQ_Bank_by_Audience.md`](../HC-015_FAQ_Bank_by_Audience.md) — **the same source data, a different artefact (§4.4)** |
| Bengali terminology base | `BN-003`, `BN-016` |
| Agent-facing conversation scripts | `SP-034` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **AI Engineering** | Train, evaluate and regression-test `M32` |
| **Content Design** | Own the taxonomy and author disambiguation prompts |
| **Localisation Lead** | Ensure Bengali utterances are collected, not translated |
| **Customer Service Manager** | Confirm the intents match what customers actually contact about |
| **BI Lead** | Supply utterance volume and coverage data |
| **Legal Counsel** | Confirm the basis for using customer utterances (§7 `O-02`) |

---

## 4. Content

### 4.1 Intent taxonomy

`M32` `FR-CAI-002` names nine domains. The taxonomy is two levels: **domain → intent**.

| Domain | Intents | Example intent |
|---|---:|---|
| **Status** | 8 | `status.repair_progress` · `status.collection_eta` |
| **Booking** | 9 | `booking.create` · `booking.reschedule` · `booking.cancel` |
| **Pricing** | 5 | `pricing.estimate_query` · `pricing.what_will_it_cost` |
| **Warranty** | 6 | `warranty.check_cover` · `warranty.claim_status` |
| **Complaint** | 5 | `complaint.raise` · `complaint.chase` |
| **Product** | 6 | `product.availability` · `product.compatibility` |
| **Location** | 4 | `location.nearest_centre` · `location.opening_hours` |
| **Payment** | 7 | `payment.make` · `payment.failed` · `payment.invoice_request` |
| **Account** | 6 | `account.update_details` · `account.data_request` |
| **Meta** | 5 | `meta.human_handover` · `meta.what_can_you_do` · `meta.out_of_scope` |
| | **~61 intents** | |

**`IL-01`: the taxonomy is two levels deep and no deeper.** A third level is a slot value, not an
intent.
**`IL-02`: an intent is added only with a named owner, a definition, and at least the minimum
utterance count in §4.3.** Ad-hoc intents are the failure this file exists to prevent.
**`IL-03`: `meta.human_handover` is never merged into another intent.** `BRU-CAI-07` requires an
explicit request for a human to be honoured immediately, without persuasion — which requires the
intent to be recognised in its own right.

### 4.2 Intent schema

*Required by `CG-009` §3, which allocates template 1 to `HC-017`–`HC-019` **"with an intent-schema
section"**.*

| Field | Type | Req | Note |
|---|---|:--:|---|
| `intent_id` | `domain.name` | ✔ | Permanent; never renamed, never reused |
| `display_name_en` / `_bn` | text | ✔ | For evaluation reporting and agent handoff |
| `definition` | text | ✔ | **What the user wants**, in one sentence |
| `boundary_note` | text | ✔ | **What this intent is not** — the adjacent intent it is confused with |
| `owner` | function | ✔ | `IL-02` |
| `utterances_bn` / `_en` | list | ✔ | Minimums in §4.3 |
| `entity_slots` | list | ✔ / — | §4.5 |
| `required_slots` | list | — | Slots without which the intent cannot be actioned |
| `disambiguation_prompt_bn` / `_en` | text | conditional | Required where the intent is confusable (§4.6) |
| `negative_examples` | list | ✔ | Utterances that must **not** classify here (§4.7) |
| `action_authority` | enum | ✔ | none / read / act — bound to `FR-CAI-029` limits |
| `handoff_triggers` | list | ✔ | Conditions routing to a human (`HC-019`) |
| `grounding_source` | enum | ✔ | `HC-*` / `KB-*` / live ERP data / **none — cannot be answered** |
| `evaluation_set_member` | bool | ✔ | §4.8 |
| `status` | enum | ✔ | draft / active / deprecated |

### 4.3 Utterance collection

**`IL-04`: Bengali utterances are collected from real users, never translated from English.**
`CG-010` states the reason without hedging: *"users type what they actually say; translated
utterances train the model on Bengali nobody uses."*

| Source | Weight | Note |
|---|---|---|
| **Anonymised contact transcripts and chat logs** (`M27`) | Primary | `BRU-CAI-15` anonymisation; PDPA question `O-02` |
| **Help-centre search terms**, especially search-to-nothing | Primary | Already in the user's words |
| Live assistant logs, once running | Primary from W7 | The best source, and unavailable at launch |
| Frontline staff transcription of what customers say | Secondary | Useful, biased to the memorable |
| **Authored by a Bengali-native speaker in the domain** | Secondary | Permitted; **must be marked `authored`, not passed as observed** |
| Machine translation from English | **Prohibited** | `IL-04` |

| Minimum utterances per intent | Bengali | English | Note |
|---|---:|---:|---|
| At launch | **25** | 15 | Below this the intent is not activated |
| Target at steady state | 60+ | 30+ | |
| **Mixed-script and romanised Bengali** | **≥ 30% of the Bengali set** | — | `FR-CAI-001` requires all three forms |

**`IL-05`: romanised and mixed-script Bengali are not edge cases.** `FR-CAI-001` requires
understanding of Bengali script, romanised Bengali, English and mixed-script **within a single
message**. A library with only clean Bengali-script utterances trains a model that fails on the way
most people actually type.

### 4.4 Relationship to `HC-015`

The FAQ bank and this library **draw on the same source data and are not the same artefact**.

| | `HC-015` FAQ bank | `HC-017` utterance library |
|---|---|---|
| Unit | A question **and its answer** | A phrasing, with no answer |
| Purpose | Read by a human | **Classified by a model** |
| Volume per topic | One item, merged (`FQ-11`) | **Many phrasings, deliberately unmerged** |
| Curation | Best phrasing wins | **All phrasings retained, including bad ones** |

**`IL-06`: an utterance is never "improved".** Misspellings, fragments, mixed script and rudeness
are the data. Cleaning them produces a model that only understands people who type carefully.

### 4.5 Entity slots

`FR-CAI-003` requires extraction tolerant of Bengali numerals and local formats.

| Slot | Bound to | Format tolerance required |
|---|---|---|
| `order_number` | `M01` | With and without prefix, spaced, Bengali numerals |
| `serial` / `imei` | `MD-021` | 15-digit IMEI; spaced and hyphenated forms |
| `brand`, `model` | `MD-017`, `MD-021` | Aliases and market names (`MD-021` `model_aliases`) |
| `device_type` | `MD-021` | Colloquial Bengali terms — *"ফ্রিজ"*, *"এসি"* |
| `symptom` | `MD-024` `is_customer_selectable` | **Free phrasing → `SYM-` code** |
| `date`, `time` | — | Relative (*"tomorrow"*, *"আগামীকাল"*), Bengali numerals, local formats |
| `branch` | `MD-003` | Colloquial place names and misspellings |
| `amount` | — | Bengali numerals, *"taka"*, *"৳"*, lakh/crore forms |
| `address` | `MD-006`, `MD-007` | **Informal Bangladeshi addresses** — `MD-007` exists because they are the norm |

**`IL-07`: every slot binds to a master-data register; no slot resolves to free text alone**
(`KA-02` pattern).

### 4.6 Disambiguation

`FR-CAI-005` requires a clarifying question rather than a guess when intent confidence is split.

| # | Rule | Class |
|---|---|:--:|
| **IL-08** | Every confusable intent pair declares the boundary in `boundary_note` and carries a disambiguation prompt | **H** |
| **IL-09** | A disambiguation prompt offers **at most three** options plus "something else" | **H** |
| **IL-10** | The prompt is a question a person would ask, not a menu | **H** |
| **IL-11** | **One clarification per turn, maximum two per conversation.** A third means handoff (`HC-019`) | **H** |
| **IL-12** | Disambiguation is never used to avoid a handoff the user asked for (`BRU-CAI-07`) | **H** |

**Confusable pairs requiring explicit boundaries** — the ones observed in every service assistant:
`status.repair_progress` vs `status.collection_eta` · `booking.create` vs `booking.reschedule` ·
`pricing.what_will_it_cost` vs `pricing.estimate_query` · `warranty.check_cover` vs
`warranty.claim_status` · `complaint.raise` vs `complaint.chase` · **`payment.failed` vs
`payment.make`** — the last of these matters most, because guessing wrong takes money twice or not
at all.

### 4.7 Negative examples and out of scope

`FR-CAI-008` requires out-of-scope input to be recognised and routed rather than answered.

**`IL-13`: every intent carries negative examples** — utterances that must not classify to it.
**`IL-14`: the library maintains an explicit out-of-scope set**, including: medical, legal and
financial advice · competitor comparisons · employment enquiries · anything about a person rather
than a device or an order · prompt-injection and jailbreak patterns (`FR-CAI-031`) · abusive input.

**`IL-15`: out-of-scope utterances are collected and maintained like any other set.** An assistant
that has never seen an out-of-scope example will attempt to answer one.

### 4.8 The evaluation set

`BRU-CAI-14` prohibits promoting a model to production until it passes **the Bengali evaluation
set**. This library builds it.

| Property | Rule |
|---|---|
| Composition | **Held out** — evaluation utterances are never in the training set (`IL-16`) |
| Size | ≥ 20 utterances per active intent, ≥ 40% Bengali script, ≥ 30% romanised or mixed |
| Content | Includes negative examples, out-of-scope, and the confusable pairs in §4.6 |
| **Bengali** | **The evaluation set is majority Bengali.** An English-majority set cannot discharge `BRU-CAI-14` |
| Refresh | Quarterly, from new observed utterances |
| Ownership | Content Design owns the set; AI Engineering runs it; **neither may change it alone** (`IL-17`) |
| Regression | Every model change runs the full set; results retained per model version |

**`IL-18`: the evaluation set is versioned and its results are retained per model version.** A model
promoted on an unrecorded evaluation cannot be shown to have passed anything.

### 4.9 Governing rules

`IL-01`…`IL-18` above, plus:

| # | Rule | Class |
|---|---|:--:|
| **IL-19** | An intent whose `grounding_source` is `none` **cannot be activated** — it would produce ungrounded output, which `BRU-CAI-01` blocks | **H** |
| **IL-20** | Utterances are **anonymised before entering the library**, and no utterance retains anything traceable to an individual (`BRU-CAI-15`) | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M32` §5.1, §5.3, §9 | The requirements this library serves |
| [`../HC-015_FAQ_Bank_by_Audience.md`](../HC-015_FAQ_Bank_by_Audience.md) | Shared source data, distinct artefact (§4.4) |
| [`HC-018_Conversational_AI_Response_and_Fallback_Copy.md`](HC-018_Conversational_AI_Response_and_Fallback_Copy.md) · [`HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md`](HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md) | What happens after classification |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) · [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Slot binding |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-007_Address_Format_and_Validation_Standard.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-007_Address_Format_and_Validation_Standard.md) | Informal-address tolerance |
| `BN-003`, `BN-016` | Bengali terminology and technician-facing Bengali |
| `M27` | Transcript and disposition source |

| Depended on by |
|---|
| `M32` training and evaluation · `HC-018` response mapping · `HC-019` handoff triggers · `M26` model operations |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Quarterly** — utterance refresh and evaluation-set rebuild |
| Trigger for out-of-cycle review | A new service or portal · an intent's accuracy falling · a novel out-of-scope pattern · a `MD-024`/`MD-021` change |
| Owner | Content Design owns the taxonomy and utterances; AI Engineering owns the model |
| Change log | `RF-006` |
| Enforcement | `IL-01`…`IL-20`; `BRU-CAI-14` promotion gate |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The library is empty and its primary source does not exist.** ~61 intents × 25 Bengali + 15 English utterances is **~2,450 utterances minimum**, all of which must be observed rather than invented — and `M27` transcript volume does not exist until go-live | Content Design with AI Lead | **W6; collection must begin at W2** |
| **O-02** | **Mining customer utterances for model training is a personal-data processing activity.** Bangladesh's Personal Data Protection Act 2026 requires explicit consent for collection and establishes data-subject rights, with enforcement expected from around May 2027 — **before `M32` reaches steady state**. `BRU-CAI-15` requires anonymisation; whether anonymised utterance mining sits within the consent basis is unconfirmed. The same question `HC-015` `O-02` raises | **Legal Counsel** with CDO | **W2 — `CG-013` escalation; collection cannot lawfully begin without it** |
| **O-03** | **Bengali utterance collection cannot begin at W6.** To have 25 observed Bengali utterances per intent at W6, collection must be running from W2 — four waves earlier than the file's registered wave. Raised as audit finding **HC-04** | Content Design with Contact Centre | **W2** |
| **O-04** | `MD-024` customer-selectable symptoms and `MD-021` model aliases are unpopulated (`AUDIT-008` KB-11); the `symptom` and `model` slots cannot resolve | MDM | W6 |
| **O-05** | **Who owns the evaluation set jointly** (`IL-17`) is undecided; `M26` model operations and Content Design both have a claim, and `BRU-CAI-14` depends on neither being able to move it alone | CTO with Content Design Lead | W6 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` **with the intent-schema section `CG-009` §3 requires** (§4.2)
- [x] Taxonomy bounded to two levels with a named owner per intent
- [x] **Bengali utterances required to be collected, never translated (`IL-04`), per `CG-010`**
- [x] Romanised and mixed-script Bengali required as a minimum proportion, per `FR-CAI-001`
- [x] Utterances explicitly not cleaned or improved (`IL-06`)
- [x] Slots bound to master-data registers, including informal addresses
- [x] Disambiguation bounded, and prohibited from evading a requested handoff (`IL-12`, `BRU-CAI-07`)
- [x] Negative and out-of-scope sets required and maintained
- [x] **Evaluation set defined as held-out, majority-Bengali, versioned, and jointly owned — making `BRU-CAI-14` enforceable**
- [x] Intents without a grounding source barred from activation (`IL-19`, `BRU-CAI-01`)
- [x] All internal links resolve
- [x] `BRU-CAI-*` and `FR-CAI-*` cited to **`M32`**, not to `05-05` — they do not appear in the cross-cutting register
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-02` PDPA basis for utterance mining — outstanding; collection cannot lawfully begin without it**
- [ ] **`O-03` collection must start at W2, not W6 — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and CTO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
