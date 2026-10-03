---
id: CM-005
title: Wave Launch Communication Kit
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead
author: Change Lead with Content Design
reviewers: [Programme Manager, Operations Director, HR Director, Support Lead, Localisation Lead, Content Design Lead, Brand, Marketing Manager, Programme Content Lead]
approver: Content Design Lead
content_class: D
purpose: >
  Supplies the one reusable set of communication assets every wave launch draws from — the
  announcement, the what-changes summary, the what-to-do instruction, the where-to-get-help card,
  the manager cascade brief and the champion talking points — each with a fixed structure, a
  variable block that changes per wave, and a Bengali counterpart. Nine launches improvised
  separately produce nine different levels of quality, and the wave that gets the worst one is
  decided by how busy the Change Lead was that month.
traces_to: [06-01, 06-02, CM-001, CM-002, CM-003, CM-006, CM-007, CM-008, CM-010, CM-012, CM-018, TR-002, TR-022, TR-024, OP-001, OP-006, NT-001, CG-003, CG-010, CG-011, BN-003]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: CM-005_Wave_Launch_Communication_Kit_BN.md
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §3 — the nine waves with their delivered capability, modules, portals and geography
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §6 — rollout pattern per location, T−4 weeks to T+4 weeks
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §7 — communication approach; wave-specific briefings; materials list
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-03, PS-09 — Bengali default on customer and field surfaces; every user-visible error states what happened and what to do next, in the user's language
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §21.5 — materials required, Bengali and English; support at go-live with floor-walkers and a published escalation path
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-005 — Wave Launch Communication Kit

> **Scope note.** This file owns **the reusable assets and the rules for varying them**. It does
> not own the schedule (`CM-003`), the go-live announcement at `T−0` (`CM-006`), hypercare content
> (`CM-007`), the branch readiness confirmation (`CM-012`) or the per-role impact statement
> (`CM-018`). The kit **assembles** those; it does not duplicate them (`CP-01`, `CM-R3`).
>
> **Reuse note.** Nine waves use this kit. Everything in §4.3–§4.8 is fixed structure with a named
> variable block. **A wave that rewrites a fixed section has broken the kit, not improved it.**

---

## 1. Purpose

The register's justification is exact: *"Nine launches need one repeatable kit, not nine improvised
ones."*

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| Each wave improvises its own assets | Quality tracks the author's availability, not the wave's importance |
| No fixed structure | Staff must re-learn where to find "what do I do on Monday" every wave |
| No variable block | Copy-paste from the last wave carries the last wave's facts into this one |
| No Bengali counterpart in the kit | Translation becomes a per-wave emergency; `CG-010` `CM-R6` blocks release |
| No manager cascade brief | 51+ branch managers each invent their own briefing |
| No champion talking points | The champion network answers questions with opinions |
| Kit assets duplicating `CM-006`/`CM-007`/`CM-012` | Three versions of the support route, two of which are stale |
| No accessibility rules | Printed cards unreadable at branch light levels; `CG-011` unmet |

---

## 2. Scope

**In scope:** the six kit assets and their fixed structures; the variable block definition; the
per-wave assembly checklist; the tone and reading-level rules; the accessibility and print rules;
the Bengali production sequence; version control across nine reuses; and rules `WL-01`…`WL-17`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The story and permitted claims | [`CM-001_Programme_Narrative_and_Change_Story.md`](CM-001_Programme_Narrative_and_Change_Story.md) |
| When each asset is issued | [`CM-003_Communication_Calendar_by_Wave.md`](CM-003_Communication_Calendar_by_Wave.md) §4.3 |
| The go-live announcement itself | [`CM-006_Go_Live_Announcement_Pack.md`](CM-006_Go_Live_Announcement_Pack.md) |
| Hypercare help content | [`CM-007_Hypercare_Communication_Pack.md`](CM-007_Hypercare_Communication_Pack.md) |
| Branch readiness confirmation | [`CM-012_Branch_Readiness_Communication_Checklist.md`](CM-012_Branch_Readiness_Communication_Checklist.md) |
| Per-role impact detail | [`CM-018_Change_Impact_Statement_Template.md`](CM-018_Change_Impact_Statement_Template.md) |
| Job aids and quick-reference cards | `TR-022` Job Aid and Quick Reference Library |
| Release notes | [`OP-006`](../17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md) |
| Transactional and system notifications | Category 04 `NT` |
| Visual design, logo and layout specification | `VB-004`, `MM-010`, `MM-011` — **written 2026-08-18** (`O-05`) |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Change Lead** | Assemble a launch in days rather than weeks |
| **Content Design** | Review kit output against a fixed structure |
| **Branch managers (`S05`)** | Deliver the cascade brief without writing it |
| **Champions (`S06`)** | Answer questions with approved talking points |
| **Localisation Lead** | Translate fixed sections once and variable blocks per wave |
| **L&D** | Align the training invitation with the launch message |
| **Support Lead** | Confirm the help routes printed on the card are the routes that exist |

---

## 4. Content

### 4.1 The six assets

**`WL-01`: a launch consists of these six and no others.** An asset that is needed once is
produced once and is not added to the kit; an asset needed twice is added, versioned and
translated.

| # | Asset | Format | Audience | Issued | Language |
|:--:|---|---|---|---|---|
| **K1** | **Wave announcement** | 1 page; email, notice board, intranet | All staff in scope + `S17` | Gate−1 + 2 weeks (`CM-003` M1) | EN + BN |
| **K2** | **What changes for you** | 1 page per audience group | Each affected group | Wave start + 2 weeks (M2) | **BN-first** for S07–S10 |
| **K3** | **What to do, and when** | 1 page; checklist form | Each affected group | T−1 week (M4) | **BN-first** |
| **K4** | **Where to get help** | **Wallet card + wall poster** | Every site | T−1 week, refreshed at T−0 | **BN-first** |
| **K5** | **Manager cascade brief** | 2 pages + 6 slides | `S05` branch managers | T−3 weeks | EN + BN |
| **K6** | **Champion talking points** | 2 pages; Q&A form | `S06` champions | T−3 weeks, before K5 | **BN-first** |

> **`WL-02` — K6 precedes K5, and K5 precedes K1 reaching staff.** The champion and the manager
> are asked questions the moment the announcement lands. A network briefed *after* the
> announcement spends the first week saying *"I don't know."*

### 4.2 Fixed structure and the variable block

**`WL-03`: every asset is a fixed frame plus one named variable block.** The variable block is
the only part that changes per wave, it is completed from a single source, and it is translated
per wave.

| Asset | Fixed | Variable block `V` |
|---|---|---|
| K1 | Opening, why, what does not change, support commitment, close | `V1` — wave name, capability delivered, sites, dates, roles affected |
| K2 | "Today you… / From [date] you…" two-column frame; the four support routes | `V2` — the role's before/after rows, drawn from `CM-018` |
| K3 | Numbered checklist frame with a confirmation line | `V3` — the wave's actions, deadlines and confirmations |
| K4 | Route table: self-help, champion, service desk, escalation | `V4` — the wave's champion name, desk hours, escalation contact |
| K5 | Briefing structure, the six slides, the objection index | `V5` — this wave's three most likely objections, from `CM-011` |
| K6 | Q&A frame; "what to say when you do not know" | `V6` — this wave's top ten questions |

**`WL-04`: `V1` is completed once, from `06-01` §3, and flows into every other block.** Where a
wave's capability is described differently in two assets, the wave has two stories.

### 4.3 K1 — Wave announcement

Fixed structure. **Reading level: `CG-011`; sentence length under 20 words; no programme jargon
(`NR-11`).**

| Section | Fixed content rule | Length |
|---|---|---|
| **Headline** | *"[Wave name] starts at [sites] on [date]"* — never *"Wave 3 go-live"* | 1 line |
| **What is arriving** | Three bullets maximum, in operational terms | 40 words |
| **Who this affects** | Named roles and sites, counted | 30 words |
| **What does not change** | **Mandatory section** — `NR-05` | 40 words |
| **What happens next, for you** | Points to K3 | 25 words |
| **Where to get help** | Points to K4; names the champion | 20 words |
| **Who to ask** | One name, one route (`SK-10`) | 1 line |

> **`WL-05` — the "what does not change" section is never omitted for space.** It is the section
> that answers the question staff are actually asking, and it is the first thing an editor cuts.

### 4.4 K2 — What changes for you

**`WL-06`: K2 is generated from `CM-018` change impact statements, not authored independently.**
`CM-018` owns the per-role analysis; K2 is its communication form. Two independent descriptions of
the same role's change will diverge by the third wave.

| Frame element | Rule |
|---|---|
| Two columns | **Today** and **From [date]** — never "as-is / to-be" |
| Row count | 5–8 rows. A role with twenty changes has not been analysed, it has been listed |
| **What stops** | Explicit. The paper form, the spreadsheet, the phone call — named |
| **What starts** | Explicit, with the first action |
| **What stays the same** | At least two rows (`NR-05`) |
| Training | The course and its date (`TR-002`) |
| Access | When it is granted, and that **training precedes access** |
| Help | One route (`OP-001`) |

### 4.5 K3 — What to do, and when

A checklist, not prose. **`WL-07`: every line is an action with an owner and a date.**

| # | Line type | Example frame |
|:--:|---|---|
| 1 | Before training | *"Confirm your attendance for [date] with [name]"* |
| 2 | Before go-live | *"Bring your [device / login / staff ID] on [date]"* |
| 3 | **At the freeze** | *"Stop using [named legacy artefact] at [exact instant]"* — drawn from `DM-014` `CV-06`, `CV-10` |
| 4 | On the first day | *"Log in and complete one [transaction] with your champion"* |
| 5 | During parallel run | *"Record in both systems until [date]"* — where the wave has a parallel run |
| 6 | Confirmation | *"Reply / sign to confirm you have stopped"* — the four confirmations in `CM-003` `CA-07` |

### 4.6 K4 — Where to get help

The single most-used asset. **`WL-08`: K4 is a physical card and a wall poster, not a link.**
Branch and field staff at 51+ sites need a route that works when the system is the problem.

| Route | Content rule |
|---|---|
| **1. Self-help** | The in-product help entry point and one search term (`HC-016`) |
| **2. Your champion** | **Named person**, per site, with their availability |
| **3. Service desk** | Number and hours; **the same routes `OP-001` publishes** — not a parallel set |
| **4. Escalation** | Who to call when route 3 has not answered, and after how long |
| **Hotline** | **16743** where the audience is customer-facing |
| Format | Wallet card 85×55 mm; poster A3; **minimum 12 pt body, 4.5:1 contrast** (`CG-011`) |
| Language | **Bengali primary, English secondary, on the same card** — not two cards |

> **`WL-09` — K4 is reprinted at every wave, even when nothing on it changed.** A card showing
> the previous wave's champion is worse than no card, because it is followed.

### 4.7 K5 — Manager cascade brief

| Part | Content |
|---|---|
| The three things to say | From `CM-001` §4.1 and §4.4, in the manager's own words |
| The one thing not to say | The prohibited claims relevant to this wave (`NR-10`) |
| Six slides | Narrative · what changes · what does not · dates · training · help |
| **Objection index** | `V5` — this wave's three most likely objections, with the approved response and **the escalation route for what cannot be answered** (`CM-011`) |
| Cascade obligation | **Within five working days of the champion forum** (`SK-06` treatment) |
| Evidence | Attendance recorded; questions logged and returned to the Change Lead |

### 4.8 K6 — Champion talking points

| Part | Content |
|---|---|
| Top ten questions | `V6`, refreshed per wave from the previous wave's logged questions |
| Answer format | **Two sentences, then the route.** A champion is not expected to be a trainer (`TR-023` boundary — see `CM-008` §4.2) |
| **"What to say when you do not know"** | A scripted, honest response and the logging route. This is the most important page in the kit |
| Escalation | The single route into the change team, with a response commitment |
| **What a champion never does** | Grant access · overrule a control · promise a fix date · comment on pay, grading or headcount |

### 4.9 Production sequence and Bengali

**`WL-10`: the kit is produced in this order, and the Bengali is not the last step.**

| Step | Activity | Owner | Working days |
|:--:|---|---|---:|
| 1 | `V1` completed from `06-01` §3 and confirmed by the PMO | Change Lead | 1 |
| 2 | `V2`…`V6` drafted; `V2` pulled from `CM-018` | Change Lead | 3 |
| 3 | **Bengali commissioned on the draft** (`CA-08`) | Localisation | — |
| 4 | G1 editorial review (`CG-007` §3.1) | Content Design | 3 |
| 5 | G2 factual review — routes, dates, names verified against `OP-001` and `CM-012` | Support + Ops | 5 |
| 6 | English approved | Content Design Lead | 1 |
| 7 | **G4 in-context linguistic review** (`BN-018`) | Independent reviewer | 5 |
| 8 | Print and distribute K4 to every site | Ops | 5 |
| **Total** | | | **≈ 3 weeks** |

> **`WL-11` — the kit's lead time is three weeks and `CM-003` schedules against it.** A wave
> launch commissioned two weeks out will ship in English, and `SK-08` says that is not
> communication to a Bengali-first audience.

### 4.10 Per-wave assembly checklist

| # | Check | Source |
|:--:|---|---|
| 1 | `V1` matches `06-01` §3 for this wave | PMO |
| 2 | Sites list matches the rollout record | Operations |
| 3 | Roles list matches `05-04` and the wave's `CM-018` statements | HR + Change |
| 4 | Dates are anchored, not absolute (`CA-01`) | `CM-003` |
| 5 | **Champion named for every site in scope** | `CM-008` |
| 6 | Support routes verified against `OP-001` today | Support |
| 7 | Freeze instant present and exact where a cutover applies | `DM-014` `CV-06` |
| 8 | Training dates confirmed | `TR-002` |
| 9 | **No claim outside the permitted set for this gate** | `CM-001` §4.5, `NR-08` |
| 10 | Bengali complete and in-context signed off | `BN-018` |
| 11 | K4 printed and physically at every site | Operations |
| 12 | Previous wave's K4 withdrawn (`WL-09`) | Branch manager |

### 4.11 Audience · channel · timing · message · call-to-action

| Audience | Channel | Timing | Message (asset) | Call to action |
|---|---|---|---|---|
| `S06` champions | Champion forum | **T−3 weeks, first** | K6 talking points | Cascade; log every question you cannot answer |
| `S05` branch managers | Manager briefing | T−3 weeks | K5 cascade brief | Brief your branch within 5 working days |
| All staff in scope | Email, notice board, huddle | Gate−1 + 2 weeks | K1 announcement | Read K3; ask your champion |
| Each affected role | Huddle + handout | Wave start + 2 weeks | K2 what changes for you | Confirm training attendance |
| Each affected role | Handout | T−1 week | K3 what to do | Complete every line; confirm |
| Every site | **Printed card + poster** | T−1 week, refreshed T−0 | K4 where to get help | Keep it on you |
| `S17` wider workforce | Newsletter | Monthly | K1 summary only | None |

### 4.12 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `WL-01` | A launch consists of the six assets; additions are versioned into the kit or not used twice | **H** |
| `WL-02` | K6 precedes K5, and K5 precedes K1 reaching staff | **H** |
| `WL-03` | Every asset is a fixed frame plus one named variable block | **H** |
| `WL-04` | `V1` is completed once from `06-01` §3 and flows into every other block | **H** |
| `WL-05` | The "what does not change" section is never omitted | **H** |
| `WL-06` | K2 is generated from `CM-018`, never authored independently | **H** |
| `WL-07` | Every K3 line is an action with an owner and a date | **H** |
| `WL-08` | K4 is a physical card and poster, bilingual on one artefact | **H** |
| `WL-09` | K4 is reprinted every wave and the previous version is withdrawn | **H** |
| `WL-10` | Bengali is commissioned at draft, not after approval | **H** |
| `WL-11` | The kit's lead time is three weeks; `CM-003` schedules against it | **H** |
| `WL-12` | Support routes are verified against `OP-001` on the day of issue, not carried forward | **H** |
| `WL-13` | No claim outside the permitted set for the wave's gate (`NR-08`) | **H** |
| `WL-14` | A wave that rewrites a fixed section has broken the kit; the change is made to the kit or not at all | **H** |
| `WL-15` | Every asset reaching S07–S10 is Bengali-first (`SK-08`, `CG-010`) | **H** |
| `WL-16` | Print assets meet `CG-011` — 12 pt minimum, 4.5:1 contrast, no colour-only meaning | **H** |
| `WL-17` | Questions logged by champions are the source of the next wave's `V6` | **S** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `06-01` §3, §6, §7 | `V1`, the rollout offsets, the materials list |
| [`CM-001_Programme_Narrative_and_Change_Story.md`](CM-001_Programme_Narrative_and_Change_Story.md) | Framing, permitted claims, prohibited claims, vocabulary |
| [`CM-018_Change_Impact_Statement_Template.md`](CM-018_Change_Impact_Statement_Template.md) | K2 is its communication form (`WL-06`) |
| [`CM-008_Champion_and_Super_User_Network_Kit.md`](CM-008_Champion_and_Super_User_Network_Kit.md) | The named champion per site that K4 and K6 depend on |
| [`CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md`](CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) | `V5` objection index |
| [`CM-012_Branch_Readiness_Communication_Checklist.md`](CM-012_Branch_Readiness_Communication_Checklist.md) | Site readiness and the confirmation lines in K3 |
| [`../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) | The freeze instant and last-transaction rules in K3 |
| `TR-002`, `TR-022`, `TR-024` | Training dates, job aids, release-training standard |
| [`OP-001`](../17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) | §4.7 response commitments and §4.1 populations — the support routes printed on K4 |
| `CG-011` · `BN-003` · `BN-018` | Accessibility, terminology, in-context linguistic sign-off |

| Depended on by |
|---|
| Every wave launch W1–W9 · `CM-006` go-live pack (extends K1) · `CM-007` hypercare pack (extends K4) · `CM-010` roadshow content (extends K5) · `CM-013`, `CM-014`, `CM-015` transition packs (reuse the frame) |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **After every wave launch** — the assembly checklist failures become the next version's fixes |
| Trigger for out-of-cycle review | A support-route change · a champion model change · a `CM-018` structure change · an accessibility finding |
| Owner | Change Lead; K4 co-owned with the Support Lead |
| Change log | `RF-006`; a change to a fixed section is MAJOR and re-translates every asset (`CG-006`) |
| Enforcement | `WL-01`…`WL-17`; the twelve-point assembly checklist run and signed per wave |
| Improvement loop | **Questions champions could not answer are the measure of kit quality.** A rising count in K6 `V6` means the previous wave's K2 was inadequate, not that champions were poorly briefed |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **No wave has a champion named per site.** K4 and K6 both require it, and `CM-008` `O-01` records that the network is unfunded and unselected. Without names, K4 ships with a blank route and becomes a poster nobody uses | Change Lead with Operations Director | **W1 minus 6 weeks** |
| **`O-02`** | **`OP-001` states its commitments per severity; K4 has to state them per person.** Support business hours are **09:00–22:00 BST, seven days**, with `Sev3` at 4 working hours and `Sev4` at 1 working day. A branch agent cannot map a severity to *“when will someone answer me”*, and `WL-12` requires the routes to be verified against `OP-001` on the day of issue. The translation from severity to card-legible route does not exist | Support Lead with Change Lead | **W1 minus 4 weeks** |
| **`O-03`** | **The Bengali counterpart does not exist.** `bilingual: yes`; four of six assets are Bengali-first. `CM-R6` blocks `Approved` and `WL-15` blocks use for S07–S10 | Localisation Lead | **W1 minus 3 weeks** |
| **`O-04`** | **Print production and distribution to 51+ sites is unplanned.** K4 is a physical card and an A3 poster, reprinted nine times at up to 51 sites, with the previous version withdrawn each time. No budget, supplier or distribution route exists | Operations with Brand | **W1 minus 4 weeks** |
| **`O-05`** | **Category 19 `MM` is complete — 12 of 12** *(enumerated 2026-08-18)*. `MM-010` and `MM-011` now supply the layout authority for K1–K5. **Two gaps remain and neither is a content gap:** `MM-010` `O-02` records that no rendering engine is selected, and `MM-011` `O-03` that no asset hosting domain or permanence commitment exists. **`MM-011` `O-01` records this kit's W1 need against its own W2 registration and reports it rather than patching it**, per `AUDIT-018` R-03 | Brand with Programme Content Lead | **W1** |
| **`O-06`** | **The kit is registered `W1` but its consumers begin at `W0`.** `CM-003` §4.7 schedules the W0 manager pre-brief and the kickoff cascade, both of which need K5 and K6. This is the wave-sequencing defect `AUDIT-010` §7 and `AUDIT-014` TS-02 recorded across four categories | Programme Content Lead | **W0** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **Six assets defined once and reused across nine waves**, each with a fixed frame and one named variable block
- [x] Briefing order fixed so champions and managers are briefed before staff
- [x] K2 bound to `CM-018` rather than independently authored (`CP-01`)
- [x] K4 specified as a physical bilingual artefact with accessibility minimums and a withdrawal rule
- [x] Champion talking points include the scripted honest answer for what a champion does not know
- [x] Production sequence places Bengali commissioning at draft, with a stated three-week lead time
- [x] Twelve-point per-wave assembly checklist
- [x] Seventeen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` no champions named per site**
- [ ] **`O-02` `OP-001` severity commitments not yet translated into a card-legible route**
- [ ] **`O-03` Bengali counterpart not written; `CM-R6` blocks approval**
- [ ] **`O-04` print production and distribution to 51+ sites unplanned**
- [ ] **`O-06` registered W1, consumed at W0**
- [ ] Named approver recorded — **pending Content Design Lead**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
