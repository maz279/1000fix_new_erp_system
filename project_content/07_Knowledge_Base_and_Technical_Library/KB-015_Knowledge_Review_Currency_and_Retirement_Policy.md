---
id: KB-015
title: Knowledge Review, Currency and Retirement Policy
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Knowledge Manager
author: Knowledge Manager with Quality Management
reviewers: [Quality Manager, Technical Director, HSE Lead, CTO, BI Lead, Programme Content Lead]
approver: Quality Manager
content_class: E
purpose: >
  The review intervals, staleness thresholds, suspension mechanism and retirement rules that keep
  the technical library current. Stale repair guidance is worse than none — it is confidently wrong,
  it is what a junior technician will follow without question, and it is what the AI assistant will
  cite. This policy is the direct control against the category risk M61 records as "the knowledge
  base becomes stale and distrusted".
traces_to: [M61, M32, M23, M22, P02, P10, P01, KB-001, KB-002, KB-003, KB-008, KB-009, KB-010, KB-011, KB-012, KB-013, KB-014, KB-016, CG-006, RF-006]
priority: P2
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.4 FR-KMS-031 article health and staleness, FR-KMS-032 mandatory review cycle with escalation and visible overdue marking, FR-KMS-033 coverage and gap analysis
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §9 BRU-KMS-05 superseded or retired content removed from offline sets and the M32 corpus; BRU-KMS-06 an article overdue for review is visibly marked wherever it appears including offline; BRU-KMS-07 every published article carries a review cycle and an owner at all times; BRU-KMS-18 an article flagged for low usefulness is revised or retired within the declared period
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §6 T-03 staleness is visible offline; §10 fix.knowledge.health entity; §11 AUT-KMS-06/07/08/17; §15 KPI-C61-03 usefulness rating, KPI-C61-04 articles overdue for review under 3%, KPI-C61-08 stale articles served offline zero
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/_CATEGORY_OVERVIEW.md §10 — two named category risks, the second being that the knowledge base becomes stale and distrusted
    verified: 2026-08-16
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md — programme-wide states Draft to Superseded, version numbering and pinning content to releases
    verified: 2026-08-16
    class: P1
supersedes: none
review_due: 2027-02-16
---

# KB-015 — Knowledge Review, Currency and Retirement Policy

> **`M61`'s category overview names two risks. The first is that expertise leaves with the people
> who hold it — that is what the whole module exists to solve. The second is that the knowledge
> base becomes stale and distrusted.** This file is the control against the second, and the second
> is the one that kills knowledge programmes after they have already succeeded.

---

## 1. Purpose

A technical library fails twice. The first failure is being empty, and every other file in this
category addresses it. The second failure is subtler and arrives later: the library is full, and
nobody believes it.

That happens through a specific mechanism, and the mechanism is worth naming precisely because the
remedy follows from it:

| Stage | What happens |
|---|---|
| 1 | An article is written and is correct |
| 2 | The procedure, the part, the model generation or the tool changes |
| 3 | The article does not change — nobody owns it, or the owner has moved on |
| 4 | A technician follows it and it does not work |
| 5 | **The technician stops trusting the library — not that article, the library** |
| 6 | Usage falls, feedback stops, coverage measures still look fine, and the failure is invisible in every report |

**Stage 5 is the whole problem.** Trust in a reference source is not article-by-article; it is
global. Three bad experiences are enough for a technician to stop opening the app, and once they
have stopped, no amount of new content reaches them.

**The consequence of absence (`CP-03`).** Without this policy: articles have no owner after
publication, no review date, and no staleness signal. `M61` `BRU-KMS-06` requires overdue articles
to be visibly marked wherever they appear including offline, and `BRU-KMS-05` requires superseded
content to be purged from offline sets and the `M32` corpus — **neither rule can be operated
without the intervals, thresholds and states defined here.** And `M32` will cite whatever is in the
corpus, confidently, with a citation, to a customer.

---

## 2. Scope

**In scope:** review intervals by article type; ownership after publication; the health score and
its components; staleness detection and its visible marking; the **suspension** mechanism;
retirement and archival; corpus and offline-pack removal; the escalation ladder for overdue
reviews; and the currency rules for the non-article registers in this category.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Programme-wide content states, versioning and release pinning | [`../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) — **this file specialises `CG-006` for knowledge content; it does not replace it** |
| Article structure and authoring | [`KB-002_Article_Template_and_Authoring_Standard.md`](KB-002_Article_Template_and_Authoring_Standard.md) |
| Tagging, findability and the corpus boundary definition | [`KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](KB-001_Knowledge_Architecture_and_Tagging_Standard.md) §4.8 |
| Offline pack composition | [`KB-016_Technician_Field_Reference_Card_Set.md`](KB-016_Technician_Field_Reference_Card_Set.md) |
| Manual and diagram licence review | [`KB-003_Repair_Manual_Index_and_Source_Register.md`](KB-003_Repair_Manual_Index_and_Source_Register.md) `LB-12` |
| Bulletin-driven content change | [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) `BL-09` — **this file supplies the suspension mechanism `BL-09` uses** |
| The content decision log | `RF-006` |
| Quality management review and CAPA | `M23` · `SP-029` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Knowledge Manager** | Own the policy; run the review programme; report currency |
| **Technical Library Owner** | Operate it daily — chase reviews, suspend, retire |
| **Article owners (R09, R10, R12, R13)** | Understand what they took on when their name went on an article |
| **Quality Manager** | Approve retirements; audit currency; own the category risk |
| **HSE Lead** | Enforce the shorter cycle on safety content |
| **CTO / platform** | Build the health computation, the visible marking and the purge propagation |
| **BI Lead** | Compute health inputs and report currency |

---

## 4. Content

### 4.1 The two questions this policy answers

| Question | Answered by |
|---|---|
| **Is this article still right?** | Review — a human decision at an interval (§4.3) |
| **Is this article still working?** | Health — a computed signal from behaviour (§4.5) |

They are different and both are needed. An article can be technically correct and useless because
nobody can find it. An article can be heavily used and wrong. **Review without health misses the
second; health without review misses the first.**

### 4.2 Ownership after publication — `KR-01`

**`BRU-KMS-07` requires every published article to carry a review cycle and an owner at all times.**
Not an author — an *owner*, which is a continuing obligation.

| Rule | Detail |
|---|---|
| **`KR-01`** | An article cannot be `Published` without a named owner and a review cycle |
| **`KR-02`** | Ownership is **a role's obligation, transferred on role change**, not a personal favour. When a specialist leaves, their articles transfer before their last day — this is a leaver-checklist item, not a discovery made six months later |
| **`KR-03`** | An article whose owner has left and is untransferred is flagged **`orphaned`** within 7 days and reassigned by the Technical Library Owner. It is not left published and unowned |
| **`KR-04`** | The owner is accountable for review; **the reviewer at each cycle may not be the owner alone where the article is safety-, warranty- or brand-gated** (`BRU-KMS-02`, `BRU-KMS-03` apply to revisions as to originals) |

> **`KR-02` and `KR-03` exist because of `M61`'s founding argument.** The module was created
> because senior technicians retire with undocumented expertise. It would be a poor outcome if the
> documented expertise also became unowned the moment they left.

### 4.3 Review intervals

Set by article type, consistent with `KB-001` §4.2. **`KR-05`: the interval is a maximum, not a
target.**

| Article type | Interval | Why |
|---|:--:|---|
| `safety_note` | **6 months** | Consumed under pressure by someone who cannot verify it; the statutory ground moves |
| `known_issue` | **6 months** | Permanent-fix status changes; issues resolve or escalate |
| `reference_card` | **6 months** | Offline, abbreviated, and trusted absolutely — abbreviation removes the context that would reveal an error |
| `fault_fix` | 12 months | Tied to model generations and parts |
| `procedure` | 12 months | Tied to models, parts and tools |
| `faq` · `how_to` | 12 months | Tied to the UI and the service offer |
| `technique` | 24 months | Fundamentals move slowly |
| `tool_guide` | 24 months | Instrument-bound; **but immediate review on any calibration or equipment change** (`KB-012`) |

**Shortening triggers — `KR-06`.** The interval shortens automatically when any of these occur, and
the review is due immediately rather than at the next cycle:

| Trigger | Source |
|---|---|
| A brand bulletin affects the content | `KB-010` `BL-09` |
| A recall touches the model | `KB-010` §6.6 |
| A safety incident or near miss involves the procedure | `SP-030` · `M59` |
| A `KB-013` hazard control changes | `SD-08` |
| A part is superseded or withdrawn | `KB-009` §6.5 |
| A fault-code mapping is superseded | `KB-008` `FC-12` |
| The procedure's norm changes materially | `KB-014` `RT-24` |
| A statutory or regulatory change | `CG-013` |
| Repeated "did not resolve" feedback | §4.5 · `M61` AUT-KMS-17 |
| A model generation enters or leaves service | `MD-021` |

### 4.4 States

Specialising `CG-006` for knowledge content. `M61` §8.1 defines the article lifecycle; this table
states what each state means for **currency** specifically.

| State | In offline packs | In `M32` corpus | Visible marking | Who moves it |
|---|:--:|:--:|---|---|
| `Published` | ✔ | ✔ | None | — |
| **`Review due`** | ✔ | ✔ | **"Review due" shown to every reader, including offline** | System at interval |
| **`Overdue`** | ✔ | **✖ after the grace period** | **"Overdue — verify before relying on this"** | System |
| **`Suspended`** | **✖** | **✖** | **"Withdrawn pending revision — do not follow"** | Knowledge Manager or HSE |
| `Revision` | ✔ (prior version) | ✔ (prior version) | "Revision in progress" | Owner |
| `Superseded` | **✖ — purged** | **✖ — purged** | Points to the successor | System on publication of the successor |
| `Retired` | **✖ — purged** | **✖ — purged** | Archive-only, searchable with a retired marker | Quality Manager |
| `Orphaned` | ✔ | ✔ | Internal flag only | System (`KR-03`) |

**`KR-07`: the grace period between `Review due` and corpus removal is 30 days for 12- and
24-month-cycle content, and 7 days for 6-month-cycle content.** `KB-001` §4.8 refers to this grace
period; this is where it is set. After it expires the article leaves the `M32` corpus but **stays
in the offline pack with its overdue marking** — because a technician in the field with a marked
overdue article is better off than a technician with nothing, whereas an AI citing an overdue
article to a customer is not.

> **That asymmetry is the single most considered decision in this file.** A human reader can
> discount a warning label. A generated answer cannot convey one credibly, and the citation makes
> it *more* authoritative, not less.

### 4.5 Health

`M61` FR-KMS-031 requires health to be computed from review date, usage trend, resolution rate and
rating. `fix.knowledge.health` is the entity.

| Component | Signal | Interpretation |
|---|---|---|
| **Resolution rate** | "Did this resolve it?" answered at the point of use | **The primary measure.** `M61` §2: the quality measure is usefulness — does it resolve the fault |
| Rating | 1–5 at the point of use | `KPI-C61-03`: > 4.0/5 at W9 |
| Usage trend | Opens over time, relative to job volume on the same fault | Falling usage against steady volume means it is being avoided |
| Days since review | Against the interval | |
| Feedback comments | Free text | The only component that says *why* |
| Rework linkage | Rework on jobs where the article was consulted | The hardest signal to gather and the most damning |

**`KR-08`: an article receiving repeated "did not resolve" is flagged for urgent revision
immediately and its ranking reduced** (`M61` AUT-KMS-17). It is not held for the review cycle.

**`KR-09`: a flagged article is revised or retired within 60 days; it is not left published**
(`BRU-KMS-18`). "Under review" is not a resting state.

**`KR-10` — the counting rule that keeps health honest.** Health is computed on **articles that had
the opportunity to be used**. An article for a model with no jobs in the period is not unhealthy;
it is unexercised, and it is reported separately. Mixing the two produces a health report that
punishes correct coverage of low-volume models — which is exactly the coverage hardest to justify
and easiest to lose.

### 4.6 Suspension — the mechanism `KB-010` `BL-09` depends on

**`KR-11`: suspension is a first-class action, not a failure of the revision process.**

| Aspect | Rule |
|---|---|
| When | Guidance is known or strongly suspected to be wrong or unsafe, and a correct version cannot be published immediately |
| Who | Knowledge Manager, Quality Manager, **or HSE Lead unilaterally for any safety content** |
| Effect | Removed from offline packs and the `M32` corpus; visible in search with **"Withdrawn pending revision — do not follow"**; the content itself remains readable to the owner and reviewers |
| Speed | **Same day for S1/S2 bulletin-driven and all safety-driven suspensions** (`BL-09`) |
| Communication | Affected technicians notified, not left to discover it |
| Duration | **Maximum 90 days**, after which it is revised or retired — `KR-12`. A permanently suspended article is a decision nobody made |
| Reversal | Only by publishing a revision, never by simply un-suspending |

> **Why suspension matters more than it looks.** The alternative, when a bulletin invalidates a
> procedure on a Thursday afternoon, is to leave known-wrong guidance published while a revision is
> drafted — because withdrawing it feels like admitting a gap. Suspension makes the honest action
> the easy one.

### 4.7 Retirement

| Trigger | Evidence required |
|---|---|
| Model out of service across the population we serve | `MD-021` `active = False` and no installed base |
| Procedure superseded by a fundamentally different one | The successor `KNW-` code |
| Brand guidance withdrawn | `KB-010` `BUL-` reference |
| Duplicate of a better article | The retained article, and a merge record |
| Content moved to another owner category — a record, a course, a policy | The destination |
| Consistently unhealthy after revision | Health record and the revision attempt |

| Rule | Detail |
|---|---|
| **`KR-13`** | Retirement requires the **Quality Manager** with a recorded reason (`M61` §8.1 transition guard) |
| **`KR-14`** | Retired articles are **archived, never deleted** (`CP-10`); they remain searchable with a retired marker so that a technician who remembers one finds it *and sees that it is retired* |
| **`KR-15`** | Retirement purges the article from every offline pack and the `M32` corpus (`BRU-KMS-05`); **purge failure is alerted, not logged quietly** (`M61` AUT-KMS-06) |
| **`KR-16`** | The contributor's original capture text is retained on retirement (`AU-02`) — the person's contribution is not erased because the guidance aged |
| **`KR-17`** | A retirement that leaves a coverage gap creates a gap record (`M61` FR-KMS-033), so the library does not quietly shrink |

### 4.8 Escalation ladder for overdue reviews

`M61` FR-KMS-032 requires escalation on a declared ladder.

| Stage | Timing | Action |
|---|---|---|
| 1 | Interval − 30 days | Owner notified of the upcoming review |
| 2 | Interval reached | State → `Review due`; **visible marking begins** (`BRU-KMS-06`) |
| 3 | +7 or +30 days (`KR-07`) | State → `Overdue`; **removed from the `M32` corpus**; owner's line manager notified |
| 4 | +60 days | Technical Library Owner reassigns the review; Quality Manager informed |
| 5 | +90 days | **Suspended or retired** — it is not left overdue indefinitely |
| — | Any stage, safety content | **HSE Lead may suspend at any point without waiting for the ladder** |

**`KR-18`: the ladder escalates to the owner's line manager, not to the owner repeatedly.** An
owner who has not reviewed in 60 days is usually over-committed rather than negligent, and the
remedy is capacity, not another reminder.

### 4.9 Currency of the non-article registers

This category contains six registers that are not articles. Their currency rules:

| Register | Cycle | Specific trigger |
|---|:--:|---|
| [`KB-003`](KB-003_Repair_Manual_Index_and_Source_Register.md) library entries | **Annual licence review** (`LB-12`) | Brand agreement change; manual revision |
| [`KB-008`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) mappings | 12 months | Bulletin supersession (`FC-12`); `MD-024` change (`FC-09`) |
| [`KB-009`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) notes | 12 months; **6 months for `hazard_class` ≠ `none`** | Claim rejection (`PC-12`); part supersession |
| [`KB-010`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) bulletins | Not reviewed — **closed or open** | Closure requires evidence (`BL-03`) |
| [`KB-011`](KB-011_Known_Issue_and_Workaround_Register.md) issues | **6 months** | Permanent-fix status change; brand confirmation |
| [`KB-014`](KB-014_Repair_Time_Standards_and_Labour_Norms.md) norms | Annual `measured`; **6-monthly `estimate`/`derived`** | `RES-06` warning rate; procedure change (`RT-24`) |

**`KR-19`: a register entry that is overdue is marked to its reader in the same way an article is.**
A stale substitution note or fault-code mapping misleads exactly as effectively as a stale
procedure, and the reader has no way to tell without the marking.

### 4.10 What is measured

| Measure | Definition | Target | Source |
|---|---|---|---|
| **Articles overdue for review** | Overdue ÷ published | **< 10% W7, < 3% W9** | `KPI-C61-04` |
| **Stale articles served offline** | Superseded or retired content present in any pack | **Zero** | `KPI-C61-08` |
| Usefulness rating | Mean rating | > 3.6 W7, **> 4.0 W9** | `KPI-C61-03` |
| Resolution rate | "Did this resolve it?" yes ÷ answered | Rising | `M61` |
| Orphaned articles | Owner departed, untransferred | **Zero beyond 7 days** (`KR-03`) | This file |
| Suspensions open beyond 90 days | | **Zero** (`KR-12`) | This file |
| Flagged articles unresolved beyond 60 days | | **Zero** (`KR-09`) | `BRU-KMS-18` |
| Purge failures | Retirement or supersession not propagated | **Zero, alerted** (`KR-15`) | `M61` AUT-KMS-06 |
| Registers overdue | Non-article entries past their cycle | < 5% | `KR-19` |
| **Unexercised articles** | No opportunity to be used in the period | Reported, **not counted as unhealthy** (`KR-10`) | This file |

### 4.11 The measure this policy is ultimately judged on

Everything in §4.10 is a process measure. **The outcome measure is whether technicians open the
library at all.**

`M61` `KPI-C61-10` targets **jobs where knowledge was consulted** rising to over 65% by W9. If
currency is failing, that number falls before any of the process measures move — because a
technician who has been burned stops opening the app long before the overdue percentage looks bad.

**`KR-20`: a sustained fall in consultation rate triggers a currency investigation, regardless of
what the process measures say.** It is the only measure in this file that reflects trust, and trust
is the thing that is actually being protected.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) | The programme-wide lifecycle this file specialises |
| [`KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](KB-001_Knowledge_Architecture_and_Tagging_Standard.md) | Article types (§4.3 intervals) and the corpus boundary (§4.4) |
| [`KB-002_Article_Template_and_Authoring_Standard.md`](KB-002_Article_Template_and_Authoring_Standard.md) | Revision follows the same review gates as authoring (`KR-04`) |
| [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) | `BL-09` consumes the §4.6 suspension mechanism |
| [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | `SD-10` 6-monthly cycle; `SD-08` change distribution |
| [`KB-016_Technician_Field_Reference_Card_Set.md`](KB-016_Technician_Field_Reference_Card_Set.md) | Purge propagation into the offline pack |
| `M61` §5.4, §6 T-03, §8.1, §9, §10, §11, §15 | The implementing module |
| `M22` Learning, Competency and Certification | Reviewer competence at each cycle |
| `RF-006` Content Decision Log | Retirement and suspension decisions logged |
| `M23` · `SP-029` | Currency failures that cause a service failure become non-conformances |

| Depended on by |
|---|
| Every `KB` article and register · `M32` corpus admission (`KB-001` §4.8) · `P02` offline pack integrity · `HC-*` customer derivatives · `TR-*` courses built from articles |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Annual**, and after the first full review cycle completes — the first cycle will show which intervals are wrong |
| Trigger for out-of-cycle review | `KPI-C61-04` or `KPI-C61-08` missed for two consecutive quarters · a service failure traced to stale guidance · consultation rate falling (`KR-20`) · a regulatory change affecting `KB-013` |
| Owner | Knowledge Manager |
| Change log | `RF-006` |
| Enforcement | Computed states and visible marking (`M61` AUT-KMS-06/07/08/17); the §4.8 ladder; the §4.10 measures |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The review-cycle lengths are proposed here, not ratified.** `M61` Q-06 asks whether the cycle is 6, 12 or 24 months and whether it varies by type. §4.3 answers it — but the answer needs the Quality Manager's decision, not inheritance from a content file | Quality Manager | **W6 build — the system implements what is decided** |
| **O-02** | **`KR-07`'s asymmetry — overdue content stays in the offline pack but leaves the `M32` corpus — needs CTO confirmation that the platform can express the two differently.** If purge is all-or-nothing, the choice becomes leaving stale content in the AI corpus or leaving technicians with nothing offline, and both are bad | CTO with Knowledge Manager | **Before `M61` build** |
| **O-03** | **Review capacity is unquantified.** At 150–250 articles with a mix of 6-, 12- and 24-month cycles, the steady-state review load is roughly 150–300 reviews a year, drawn from the same 15–30 R12 specialists who author them and do the hardest repairs. **No capacity model exists** | Quality Manager with Technical Director | **W5 — before the first cycle falls due** |
| **O-04** | `KR-02` requires article ownership transfer on leaving. **Whether the HR leaver checklist (`SP-023`, `M21`) includes it is unconfirmed**; if it does not, `KR-03` orphan detection is the only safety net and it operates after the fact | HR Manager with Knowledge Manager | W5 |
| **O-05** | The rework-linkage health component (§4.5) requires jobs to record which articles were consulted **and** the rework outcome. `M61` T-12 requires attribution to state its method and make no unsupported causal claim; the method is undefined. Same root as `M61` Q-08 | BI Lead with CTO | W6 |
| **O-06** | `KR-19` requires overdue **register entries** to be marked to the reader. Registers are not articles and may not carry the same marking mechanism; six registers are affected | CTO with Knowledge Manager | W6 |
| **O-07** | **The policy is deliverable now; the system that enforces it lands at W6 with `M61`, and `KB` content is needed from W2.** For four waves, currency is a manual discipline with no computed states, no visible marking and no automatic purge. `KB-001` `O-05` records the same interval risk | Quality Manager with Operations Director | **W2 — an interim manual register of review dates is needed** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present, §7 added per category convention
- [x] The failure mechanism named stage by stage, so the controls follow from it rather than being asserted
- [x] Review and health separated as two distinct questions (§4.1)
- [x] Ownership defined as a continuing role obligation with transfer and orphan rules (`KR-01`…`KR-04`)
- [x] Intervals set by article type, with automatic shortening triggers enumerated
- [x] States mapped to offline-pack and `M32`-corpus presence, with visible marking per state
- [x] **The grace-period asymmetry between human readers and the AI corpus stated and justified (`KR-07`)**
- [x] Suspension defined as a first-class action with a 90-day maximum (`KR-11`, `KR-12`)
- [x] Retirement requires Quality Manager approval, archives rather than deletes, and creates a gap record
- [x] Escalation ladder escalates to the line manager rather than repeating reminders (`KR-18`)
- [x] Currency rules given for the six non-article registers (§4.9)
- [x] Health counting excludes unexercised articles so low-volume coverage is not punished (`KR-10`)
- [x] The outcome measure — consultation rate — identified as the real test (`KR-20`)
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9; `KPI-C61-*` cited to `M61` §15, **not** to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` intervals ratified by the Quality Manager — outstanding**
- [ ] **`O-02` platform confirmation of the pack/corpus asymmetry — outstanding**
- [ ] **`O-03` review capacity model — outstanding; the policy is unenforceable without it**
- [ ] **`O-07` interim manual currency register for W2–W6 — outstanding**
- [ ] Named approver recorded — **pending Quality Manager**
- [x] English-only, per `CG-010` §3.2 — governance content, head-office audience

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
