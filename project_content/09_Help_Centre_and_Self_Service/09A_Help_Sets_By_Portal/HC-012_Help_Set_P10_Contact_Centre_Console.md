---
id: HC-012
title: Help Set — P10 Contact Centre Console
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Contact Centre Operations
reviewers: [Customer Service Manager, Contact Centre Supervisor, Quality Manager, Legal Counsel, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead with Customer Service Manager
content_class: D
purpose: >
  The help set for contact centre agents covering queue, screen pop, actions, transfers, AI assist,
  wrap-up and quality. Agent help must be readable inside a live call, which constrains format more
  severely than any other desk-based set: an agent cannot read a paragraph while a customer is
  speaking, and a help centre that requires them to try will simply not be opened.
traces_to: [P10, M27, M32, M34, M61, MD-026, HC-001, HC-002, HC-003, HC-015, HC-016, UI-020, SP-005, SP-028, SP-034, KB-011, TR-017]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: HC-012_Help_Set_P10_Contact_Centre_Console_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P10 targets fewer than 3 screen switches per contact and 100% disposition-coding completeness
    verified: 2026-08-18
    class: P1
  - source: project_content/08_Training_and_Enablement/08B_Course_Packs/TR-017_Course_Pack_Contact_Centre_Agent.md §4 — three screen switches is a design target; only approved, current articles may be sent to a customer
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.2 FR-KMS-020 — contact-centre surfacing of articles and customer-safe guidance during a live conversation, with one-tap send to the customer; §9 BRU-KMS-11 separate customer approval
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P10 Contact Centre Console

| Item | Value |
|---|---|
| Portal | `P10` Contact Centre Console |
| Audience | **Contact centre agent** — audience 9 · `R34` 30–60, `R35` 4–10 |
| Article type | Help set specification — **Task, scannable in seconds** |
| Reading level target | `CG-011`; trained audience, but **read under live-call pressure** |
| Languages | Bengali primary — agents handle Bengali calls |
| Related UI copy | `UI-020` `P10` console copy pack |

> **Template conformance.** As `HC-003`, applied at set level.
>
> **`PS-25`: the format constraint here is time, not literacy.** The `HC-011` rider reads
> one-handed in the rain; the `P10` agent reads while a customer is mid-sentence. Both need one
> screen — but the agent needs it **scannable**, structured so the answer is found without reading
> the article.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and shape |
| `UI-020` | Labels quoted in steps |
| [`../HC-003_Help_Set_P01_Customer_Portal_and_App.md`](../09A_Help_Sets_By_Portal/HC-003_Help_Set_P01_Customer_Portal_and_App.md) | **What the agent may send the customer** — the customer set is the sendable corpus |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-034_Call_and_Conversation_Script_Library.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-034_Call_and_Conversation_Script_Library.md) | **The boundary — see below** |

**`PS-26`: this set is not the script library.** `SP-034` owns what an agent *says*. This set owns
what an agent *does in the console*. A help article that drifts into wording is duplicating
`SP-034` (`CP-01`), and a script that drifts into system steps is duplicating this set.

| Question | Owner |
|---|---|
| *"What do I say?"* | **`SP-034`** scripts |
| *"How do I do it in the console?"* | **`HC-012`** — this set |
| *"What can I send the customer?"* | **`HC-003`** customer set, via `FR-KMS-020` |
| *"What may I say about a known defect?"* | **`KB-011`** approved messaging (`KW-07`) |

---

## Steps — *the contact and its article inventory*

### Block A — Handling a contact *(8 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 1 | **Take the next contact** | Task | **P0** |
| 2 | **Read the screen pop** — what you already know | Concept | **P0** |
| 3 | **Verify who you are speaking to** | Task | **P0** — `BRU-CAI-03` pattern |
| 4 | Handle a contact on each channel | Task | P1 |
| 5 | Put a contact on hold | Task | P1 |
| 6 | **Transfer with context** | Task | **P0** |
| 7 | Conference in a colleague | Task | P2 |
| 8 | End and wrap up | Task | **P0** |

### Block B — The three-screen paths *(7 articles)*

**`PS-27`: one article per high-volume contact type, each showing the path in three screen
switches or fewer.** These are the articles the `P10` target actually depends on.

| # | Article | Contact type | Pri |
|---:|---|---|:--:|
| 9 | **Status enquiry in three screens** | Highest volume | **P0** |
| 10 | **Booking in three screens** | High | **P0** |
| 11 | Amend or cancel in three screens | High | **P0** |
| 12 | Payment query in three screens | High | **P0** |
| 13 | Warranty query in three screens | Medium | P1 |
| 14 | Complaint intake in three screens | Medium | **P0** |
| 15 | Technical question — find and send guidance | Medium | P1 |

### Block C — Knowledge and AI assist *(6 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 16 | **Search knowledge during a call** | Task | **P0** |
| 17 | **What you may and may not send a customer** | Concept | **P0** — `BRU-KMS-11` |
| 18 | Send an article to the customer | Task | P1 |
| 19 | **Use AI assist — and when not to trust it** | Concept | **P0** |
| 20 | **The assistant handed this contact to you** | Concept | **P0** — `FR-CAI-037` handoff package |
| 21 | Report a wrong AI answer | Task | P1 |

### Block D — Coding and quality *(5 articles)*

Disposition coding · **why 100% coding matters** · re-open or link a contact · your quality score ·
**what a monitored call is assessed on**. **2 at P0, 3 at P1.**

### Block E — Difficult contacts *(6 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 27 | **A known defect — say only the approved message** | Concept | **P0** — `KW-07` |
| 28 | An angry or distressed customer | Task | **P0** |
| 29 | **A safety-relevant contact** | Task | **P0** |
| 30 | A vulnerable customer | Task | **P0** |
| 31 | A request beyond your authority | Task | P1 |
| 32 | Escalate to a supervisor | Task | P1 |

### Block F — Supervisor *(4 articles)*

Manage the queue · monitor a call · coach against the rubric · handle an escalated contact.
**0 at P0, 3 at P1, 1 at P2.**

**Set total: 36 articles · 19 at P0 · 14 at P1 · 3 at P2.**

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Contacts handled without hunting across screens | **Screen switches per contact** | **Fewer than 3** |
| Every contact is coded | **Disposition completeness** | **100%** |
| Contacts resolved first time | `KPI-027` first-contact resolution | 70% then 78% |
| Agents trust and correctly bound AI assist | Wrong-AI-answer reports raised | **Non-zero and acted on** |

**`PS-28`: Block B carries this set.** The three-screen target is met by seven articles showing
seven paths, or it is not met at all. Everything else supports them.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Screen switches above three | The path genuinely needs more screens | **This is product feedback, not an agent failure** (`TR-017` §4) |
| Help not opened during calls | Not scannable in seconds | `PS-25` — restructure, do not shorten arbitrarily |
| Agents send internal content to customers | Article 17 unread, or the send control does not enforce it | **`BRU-KMS-11`** — fix the control, then the content |
| Wrong-AI-answer reports at zero | Agents are not reporting, not that the AI is perfect | Treat zero as a warning, as `TR-004` `AS-06` does for pass rates |
| Defect messaging varies between agents | `KB-011` approved messages absent (`KW-07`) | `TR-017` `O-01` records the same gap |

---

## Related

`UI-020` · [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-034_Call_and_Conversation_Script_Library.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-034_Call_and_Conversation_Script_Library.md) — **the wording boundary** ·
[`../../07_Knowledge_Base_and_Technical_Library/KB-011_Known_Issue_and_Workaround_Register.md`](../../07_Knowledge_Base_and_Technical_Library/KB-011_Known_Issue_and_Workaround_Register.md) — approved defect messaging ·
[`../../08_Training_and_Enablement/08B_Course_Packs/TR-017_Course_Pack_Contact_Centre_Agent.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-017_Course_Pack_Contact_Centre_Agent.md) — the training counterpart ·
[`HC-003_Help_Set_P01_Customer_Portal_and_App.md`](HC-003_Help_Set_P01_Customer_Portal_and_App.md) — the sendable corpus ·
[`../09B_Conversational_AI/HC-018_Conversational_AI_Response_and_Fallback_Copy.md`](../09B_Conversational_AI/HC-018_Conversational_AI_Response_and_Fallback_Copy.md) · [`../09B_Conversational_AI/HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md`](../09B_Conversational_AI/HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md) — Block C ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md).

---

## Feedback

Helpfulness per `CG-014`, plus **screen-switch telemetry per contact type** — the only measure that
shows whether a three-screen article describes a three-screen reality.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Articles required | **36** · written **0** |
| Effort | 36 × 2–3 h = **70–110 hours** |
| Sequencing | Block B (`PS-28`) first, then the 19 P0 before W4 |
| **Dependency** | **Block B cannot be authored before `P10` is stable** — the paths must be derived from the built console, the same constraint `TR-017` `O-05` records |
| Bengali | All 36 |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Block B three-screen paths must be derived from the built console** and cannot be written in advance (`TR-017` `O-05`). The set's most important block is also its latest | Content Design with `P10` team | **W4** |
| **O-02** | **`KB-011` approved defect messages do not exist** (`TR-017` `O-01`, `KB-011` `O-02`). Article 27 is P0 and has no content to point at | Quality Manager with Contact Centre | **W4** |
| **O-03** | **`SP-034` scripts are specified but unwritten**; the `PS-26` boundary cannot be tested until they exist | Contact Centre with Content Design | W4 |
| **O-04** | `FR-KMS-020` one-tap send and the `BRU-KMS-11` sendable-corpus control arrive with `M61` at **W6**, two waves after this set | CTO with Knowledge Manager | **W4** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] The time constraint distinguished from the literacy constraint (`PS-25`)
- [x] **Boundary with `SP-034` scripts, `HC-003` sendable corpus and `KB-011` defect messaging stated (`PS-26`)**
- [x] 36 articles enumerated; the three-screen block identified as the set's purpose (`PS-27`, `PS-28`)
- [x] Screen-switch overrun routed as product feedback, not agent failure
- [x] Zero wrong-AI-answer reports treated as a warning signal
- [x] All internal links resolve
- [x] `BRU-KMS-11` and `FR-KMS-020` cited to `M61`; `FR-CAI-037` to `M32`; `P10` targets to `04-00`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 36 articles authored — outstanding**
- [ ] **`O-02` approved defect messages — outstanding; blocks a P0 article**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Customer Service Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
