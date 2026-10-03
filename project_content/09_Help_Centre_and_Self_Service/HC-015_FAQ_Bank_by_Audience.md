---
id: HC-015
title: FAQ Bank by Audience
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design with Customer Experience
author: Content Design with Customer Experience and Contact Centre
reviewers: [Customer Service Manager, Knowledge Manager, Legal Counsel, BI Lead, AI Lead, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead with Customer Service Manager
content_class: D
purpose: >
  The curated question-and-answer sets per audience, sourced from real contact-centre and support
  volume rather than from what the business imagines customers ask. FAQs are the highest-traffic
  help asset and the primary grounding source for the AI assistant; an FAQ bank written from
  assumption trains the assistant on questions nobody asks and leaves the real ones unanswered.
traces_to: [M27, M32, M34, M61, P01, P02, P04, P05, P07, P08, P10, MD-024, MD-026, HC-001, HC-002, HC-003, HC-017, HC-018, HC-019, LG-008, KB-011, CG-014]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: HC-015_FAQ_Bank_by_Audience_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32 §5.3 FR-CAI-015 retrieval-augmented grounding — never answer a factual question from model parameters alone; FR-CAI-019 no-answer behaviour
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32 §9 BRU-CAI-01 ungrounded factual output is blocked; BRU-CAI-15 transcripts used for improvement are anonymised before use
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-025 status enquiries deflected to self-service; KPI-026 AI first-contact resolution
    verified: 2026-08-18
    class: P1
  - source: Personal Data Protection Ordinance 2025 (Bangladesh), issued 6 November 2025 and finalised as the Personal Data Protection Act, 2026 (Law 63 of 2026) — applies to entities processing personal data within Bangladesh; requires explicit consent for collection, establishes data-subject rights, and restricts sensitive and cross-border processing; enforcement mechanisms expected to activate around 13 May 2027
    verified: 2026-08-18
    class: P1
    note: Applicability to the reuse of contact transcripts as content source material must be confirmed by Legal Counsel — see Open Item O-02
supersedes: none
review_due: 2027-02-18
---

# FAQ Bank by Audience

| Item | Value |
|---|---|
| Portal | All — the bank is audience-scoped, not portal-scoped |
| Audience | **All eleven audiences** (`HC-001` §4.1), each with its own set |
| Article type | **FAQ item** — object type 4 (`HC-001` §4.2) |
| Reading level target | `CG-011`; **the answer is the first sentence** |
| Languages | **Bengali authored** for customer-, technician-, rider- and seller-facing sets |
| Related UI copy | `UI-011`, `UI-012`, `UI-014`…`UI-022` per audience |

> **Template conformance.** `TPL_Help_Article.md` applied at **bank level**, as `CG-009` §3
> requires. All sections retained in order with bank-level interpretation, consistent with
> [`09A_Help_Sets_By_Portal/HC-003_Help_Set_P01_Customer_Portal_and_App.md`](09A_Help_Sets_By_Portal/HC-003_Help_Set_P01_Customer_Portal_and_App.md).

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`HC-001_Help_Centre_Information_Architecture.md`](HC-001_Help_Centre_Information_Architecture.md) · [`HC-002_Help_Article_Template_and_Style_Rules.md`](HC-002_Help_Article_Template_and_Style_Rules.md) | Facets, audiences, style |
| **`M27` contact disposition and transcript data** | **The source.** Without it the bank is guesswork — `O-01` |
| [`09A_Help_Sets_By_Portal/HC-003_Help_Set_P01_Customer_Portal_and_App.md`](09A_Help_Sets_By_Portal/HC-003_Help_Set_P01_Customer_Portal_and_App.md) and siblings | An FAQ answers briefly and links to the article that answers fully |
| `LG-008` privacy notice | Governs the reuse of contact data as source material |

**`FQ-01`: an FAQ item is a question people actually asked, in the words they asked it.** Not a
question the business wishes they would ask, and not a heading rewritten as a question. The whole
value of the bank is that it is evidence of demand.

---

## Steps — *how the bank is built and maintained*

### Stage 1 — Source

| Source | Weight | Note |
|---|---|---|
| **`M27` contact dispositions** by volume | Primary | The single best evidence of what people ask |
| **Contact transcripts and chat logs** | Primary | **Anonymised before use** (`BRU-CAI-15`); see `FQ-08` |
| Help-centre search terms, especially search-to-nothing | High | Reveals demand the help set missed (`IA-17`) |
| `M34` complaint themes | High | A complaint is a question that was answered badly |
| Portal abandonment points | Medium | Where people give up is where they had a question |
| Frontline staff nominations | Medium | Useful, but biased toward the memorable rather than the frequent |
| Business assumption | **Excluded** | `FQ-01` |

**`FQ-02`: every item records its source and its observed volume.** An item with no evidence of
demand is a candidate for retirement at the next review.

### Stage 2 — Curate

| # | Rule | Class |
|---|---|:--:|
| **FQ-03** | The question is phrased as the asker phrases it, including common Bengali and mixed-script forms | **H** |
| **FQ-04** | **The answer's first sentence is the answer.** Context follows; qualification follows that | **H** |
| **FQ-05** | Maximum 80 words. An answer longer than that is an article, and the FAQ links to it | **S** |
| **FQ-06** | Every item links to the full article where one exists (`IA-12`) | **H** |
| **FQ-07** | No item states a price, fee, SLA or legal term (`IA-14`, `IA-15`) | **H** |
| **FQ-08** | Source transcripts are **anonymised before use** and no item contains anything traceable to an individual | **H** |
| **FQ-09** | Items about a known device defect carry **only the approved message** (`KB-011` `KW-07`) | **H** |
| **FQ-10** | Items are audience-scoped; the same question may have different answers for different audiences, and that is correct | **H** |
| **FQ-11** | Duplicate and near-duplicate questions are **merged**, with alternate phrasings retained as search aliases | **C** |
| **FQ-12** | An item that cannot be answered honestly is **not written**; the gap is reported instead | **H** |

### Stage 3 — Bank structure per audience

| Audience | Target items | Note |
|---|---:|---|
| **Customer** (`P01`) | **80–120** | The largest set; drives `KPI-025` |
| Technician (`P02`) | 30–40 | Offline-available |
| Internal operations (`P03`) | 40–60 | Overlaps `HC-005` |
| Corporate admin (`P04`) | 30–40 | Billing-weighted |
| Vendor (`P05`) | 25–35 | Payment-weighted |
| Marketplace seller (`P07`) | 30–40 | Earnings-weighted |
| Brand partner (`P08`) | 20–30 | Claims-weighted |
| Rider (`P09`) | 20–25 | Offline-available |
| Contact centre agent (`P10`) | 25–35 | **Internal FAQ — what agents ask each other** |
| Field auditor (`P11`) | 15–20 | |
| Partner (`P12`) | 20–25 | Commission-weighted |
| | **~335–470 items** | |

### Stage 4 — Review

**`FQ-13`: the bank is re-ranked quarterly against current volume.** An FAQ bank that is not
re-ranked becomes a record of what people asked in year one. Items whose volume has collapsed are
retired; new high-volume questions are added.

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| High-volume questions are answered before contact | **`KPI-025`** deflection | 60% W7, **80% W9** |
| The assistant answers from evidence of real demand | **`KPI-026`** AI first-contact resolution | 40% W7, 55% W9 |
| The bank reflects reality | Items with observed volume | **100%** (`FQ-02`) |
| Gaps are visible | Questions with volume and no item | Reported weekly — the authoring backlog |

**`FQ-14`: the customer set's top 20 items carry the deflection target.** In every self-service
programme a small number of questions account for most volume. Those twenty are written, tested and
translated first, and re-derived quarterly.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Deflection flat despite a large bank | Items written from assumption, not volume | `FQ-01` — re-derive from `M27` |
| The assistant answers oddly | It is grounded on FAQ items that are ambiguous or overlapping | `FQ-11` merge; `HC-018` grounding rules |
| Items contradict the help articles | Two answers to one question | `FQ-06` — the FAQ summarises and links; it does not answer independently |
| Bengali items unused | Translated rather than authored | `HS-29` |
| An item states a price or an SLA | `FQ-07` breached | Withdraw; the assistant may have repeated it (`BRU-CAI-02`) |
| Legal challenge over transcript reuse | `FQ-08` or the PDPA position | **Stop and escalate — `O-02`** |

---

## Related

[`HC-001_Help_Centre_Information_Architecture.md`](HC-001_Help_Centre_Information_Architecture.md) · [`HC-002_Help_Article_Template_and_Style_Rules.md`](HC-002_Help_Article_Template_and_Style_Rules.md) ·
[`09A_Help_Sets_By_Portal/HC-003_Help_Set_P01_Customer_Portal_and_App.md`](09A_Help_Sets_By_Portal/HC-003_Help_Set_P01_Customer_Portal_and_App.md) and the eleven other sets — every item links into them ·
[`09B_Conversational_AI/HC-017_Conversational_AI_Intent_and_Utterance_Library.md`](09B_Conversational_AI/HC-017_Conversational_AI_Intent_and_Utterance_Library.md) — **the same source data, a different use** ·
[`09B_Conversational_AI/HC-018_Conversational_AI_Response_and_Fallback_Copy.md`](09B_Conversational_AI/HC-018_Conversational_AI_Response_and_Fallback_Copy.md) · [`09B_Conversational_AI/HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md`](09B_Conversational_AI/HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md) ·
[`../07_Knowledge_Base_and_Technical_Library/KB-011_Known_Issue_and_Workaround_Register.md`](../07_Knowledge_Base_and_Technical_Library/KB-011_Known_Issue_and_Workaround_Register.md) — approved defect messaging · `LG-008` privacy notice.

---

## Feedback

Helpfulness per `CG-014` on every item, plus **volume tracking**: an item's traffic against the
contact volume for the same question is the measure of whether it is deflecting anything.

---

## Coverage and Authoring Plan *(addition — justified: consistent with the category convention)*

| Item | Position |
|---|---|
| Items required | **~335–470** across eleven audiences · written **0** |
| Effort | 400 items × 0.5–1 h including review = **200–400 hours**, plus Bengali authoring |
| **Sequencing** | The customer top-20 (`FQ-14`) first, then the customer set, then by audience wave |
| **Critical dependency** | **The bank cannot be derived before `M27` produces volume data.** Pre-go-live items are provisional and must be marked so, then re-derived after six months |
| Bengali | Customer, technician, rider and seller sets **authored in Bengali** |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`M27` contact volume and disposition data does not exist pre-go-live.** `FQ-01` requires items to come from real demand; the first bank must be provisional and re-derived. **The register places this file at W2, which is before the data exists.** Raised as audit finding **HC-03** | Content Design with Contact Centre | **W2 provisional; re-derive by W4** |
| **O-02** | **Reuse of contact transcripts as content source material is a personal-data processing activity.** Bangladesh's Personal Data Protection Act 2026 requires explicit consent for collection and establishes data-subject rights, with enforcement expected from around May 2027. `BRU-CAI-15` requires anonymisation; **whether anonymised transcript reuse for content authoring is within the consent basis has not been confirmed** | **Legal Counsel** with CDO | **W2 — `CG-013` escalation trigger** |
| **O-03** | **`KB-011` approved defect messages do not exist** (`TR-017` `O-01`, `HC-012` `O-02`). `FQ-09` items cannot be written | Quality Manager | W3 |
| **O-04** | The customer top-20 must be identified before authoring, and cannot be before `O-01`. **The interim source is frontline nomination, which `FQ-01` explicitly deprioritises** — the compromise must be recorded, not hidden | Content Design with Contact Centre | W2 |
| **O-05** | Bengali authoring capability (`HS-29`, `TR-001` `O-05`) | Localisation Lead | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at bank level; additions justified
- [x] **Items required to come from observed demand, with business assumption explicitly excluded (`FQ-01`, `FQ-02`)**
- [x] Answer-first structure and length bound (`FQ-04`, `FQ-05`)
- [x] Price, fee, SLA and legal terms excluded (`FQ-07`, `IA-14`, `IA-15`)
- [x] **Transcript anonymisation required, and the PDPA question raised rather than assumed (`FQ-08`, `O-02`)**
- [x] Approved-defect-message rule carried from `KB-011` (`FQ-09`)
- [x] Unanswerable questions reported as gaps rather than answered badly (`FQ-12`)
- [x] Quarterly re-ranking made a rule (`FQ-13`)
- [x] The provisional status of any pre-go-live bank stated openly
- [x] All internal links resolve
- [x] `BRU-CAI-01`/`-02`/`-15` and `FR-CAI-015`/`-019` cited to `M32`; `KW-07` to `KB-011`; `KPI-025`/`-026` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The ~400 items authored — outstanding**
- [ ] **`O-01` W2 placement before the data exists — outstanding**
- [ ] **`O-02` PDPA position on transcript reuse — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Customer Service Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
