---
id: HC-011
title: Help Set — P09 Logistics and Rider App
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Logistics Operations
reviewers: [Logistics Manager, Operations Director, HSE Lead, Finance Manager, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead with Logistics Manager
content_class: D
purpose: >
  The in-app help set for 50–150 riders and 10–25 coordinators covering manifest, scanning,
  exceptions, proof of delivery, cash and offline working. Riders need short, visual, Bengali
  guidance available without connectivity — they are alone at a door, one-handed, outdoors, often
  in rain, and every second spent looking for an answer is a second the customer is watching.
traces_to: [P09, M03, M46, M50, M59, M61, MD-005, MD-026, HC-001, HC-002, HC-004, HC-016, UI-019, KB-013, KB-016, TR-020, SP-009, SP-019, SP-030, DT-005]
priority: P2
wave: W3
bilingual: yes
bn_counterpart: HC-011_Help_Set_P09_Logistics_and_Rider_App_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P09 riders operate one-handed, outdoors, offline, in Bengali; custody-break prevention depends on unambiguous scan and handover copy
    verified: 2026-08-18
    class: P1
  - source: project_content/07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md §4.4 — damaged, defective or recalled lithium batteries are forbidden for transport by air and require controlled handling by road
    verified: 2026-08-18
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md — devices in transit are the company's highest-value uninsured exposure
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P09 Logistics and Rider App

| Item | Value |
|---|---|
| Portal | `P09` Logistics & Rider |
| Audience | **Rider / logistics** — audience 8 · `R16` 50–150 riders, `R15` 10–25 coordinators |
| Article type | Help set specification — **Task, very short** |
| Reading level target | `CG-011`; **visual-first, mixed literacy, high turnover** |
| Languages | **Bengali authored** (`HS-29`) |
| Related UI copy | `UI-019` `P09` rider app copy pack |

> **Template conformance.** As `HC-003`, applied at set level. **This set follows the `HC-004`
> offline-first pattern**, not the `HC-003` browse pattern.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and shape |
| `UI-019` | Labels quoted in steps |
| [`../../07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md`](../../07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md) | **The hazard card boundary** — the damaged-battery card is authored there, referenced here (`CP-01`) |
| [`../../08_Training_and_Enablement/08B_Course_Packs/TR-020_Course_Pack_Rider_and_Logistics.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-020_Course_Pack_Rider_and_Logistics.md) | This set is the reminder layer over that training |

**`PS-22`: the reading constraint is severer than any other set in the register.** One hand, a
phone, sunlight or rain, a customer waiting, no signal. **Maximum five steps per article, one
screen, no scrolling for the answer.** An article that does not fit is a video (`HC-020`) or it is
wrong.

---

## Steps — *the rider's run and its article inventory*

### Block A — The manifest *(5 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 1 | **Start your run** | Task | **P0** |
| 2 | Read your manifest | Task | **P0** |
| 3 | Your route and order of stops | Concept | P1 |
| 4 | A stop was added or removed | Concept | P1 |
| 5 | You cannot complete your run | Task | P1 |

### Block B — Custody *(6 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 6 | **Scan a device into your custody** | Task | **P0** |
| 7 | **Seal and pack** | Task | **P0** |
| 8 | **Hand over to the branch or the next rider** | Task | **P0** |
| 9 | The barcode will not scan | Troubleshooting | **P0** |
| 10 | The item does not match the manifest | Troubleshooting | **P0** |
| 11 | **A damaged battery consignment** | Task | **P0** — references `KB-016` |

### Block C — At the door *(6 articles)*

Collect from a customer · **capture condition before you take it** · deliver to a customer ·
**capture proof of delivery** · the customer is not there · the customer refuses. **3 at P0,
3 at P1.**

### Block D — Cash *(4 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 18 | **Take a payment at the door** | Task | **P0** |
| 19 | **Your cash limit** | Concept | **P0** |
| 20 | **Hand in your cash** | Task | **P0** |
| 21 | Your cash does not balance | Troubleshooting | **P0** |

### Block E — Offline and problems *(5 articles)*

Working with no signal · **check what has synced before you finish** · sync failed · report a
vehicle problem · **report an accident or an incident**. **3 at P0, 2 at P1.**

### Block F — Coordinator *(4 articles)*

Build a manifest · reassign a stop · manage an exception · reconcile the day's cash. **1 at P0,
3 at P1.**

**Set total: 30 articles · 18 at P0 · 12 at P1 · 0 at P2.**

> **`PS-23`: this set has the highest P0 proportion in the register — 60%.** That is not
> priority inflation. A rider at a door with no signal has no fallback: there is no colleague to
> ask, no desk to return to, and the customer is watching. Content that is not there when needed is
> content that does not exist.

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Custody is never broken | **Custody breaks** | **Zero** |
| Proof of delivery is complete first time | POD dispute rate | Falling |
| Cash reconciles | **Cash variance per rider** | Falling |
| Riders use the app rather than phoning the coordinator | Coordinator interruption volume | Falling |

**`PS-24`: articles 6, 8, 11, 18 and 20 carry this set.** Custody in, custody out, the hazard case,
and the two cash articles. Everything else is convenience; these five are exposure.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Custody breaks occur | Article 6 or 8 not reachable at the moment of scan | **In-app, at the scan step** — a help centre elsewhere has failed |
| Riders phone the coordinator | Answer not findable in one screen | `PS-22` — the article is too long |
| Cash variance persists | Article 19 or 21 unclear, or the limit itself is unrealistic | Check the limit before the content |
| Damaged battery carried incorrectly | Article 11 duplicated the `KB-016` card and they diverged | `CP-01` — author once, reference |
| Help unread in rain | Screen and format failure, not content failure | Product feedback, not a rewrite |

---

## Related

`UI-019` · [`HC-004_Help_Set_P02_Technician_App.md`](HC-004_Help_Set_P02_Technician_App.md) — the same offline-first pattern and the same boundary discipline ·
[`../../07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md`](../../07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md) · [`../../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](../../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md) §4.4 ·
[`../../08_Training_and_Enablement/08B_Course_Packs/TR-020_Course_Pack_Rider_and_Logistics.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-020_Course_Pack_Rider_and_Logistics.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) · [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md) · `DT-005`.

---

## Feedback

In-app helpfulness, capturable **offline** and replayed on sync. Reported weekly with custody, POD
and cash telemetry.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Articles required | **30** · written **0** |
| Effort | 30 × 1.5–2.5 h = **45–75 hours** — shorter articles, but **visual production adds cost** |
| Sequencing | The 5 exposure articles (`PS-24`), then 18 P0 before W3 |
| Delivery | **In-app and offline**, as `HC-004` |
| Bengali | All 30, authored in Bengali |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The damaged-battery road-transport standard does not exist** (`KB-013` `O-03`, `KB-006` `O-04`, `TR-020` `O-01`). **Article 11 is P0 and has no compliant method to describe** — the fourth file to record this gap | HSE Lead with Logistics | **W3 — blocking article 11** |
| **O-02** | **Offline help delivery inside `P09` must exist at W3**; `M61` provides the mechanism at W6, the same gap `HC-004` `O-01` records for `P02` | CTO with Content Design | **W3 — blocking the delivery model** |
| **O-03** | Bengali authoring capability (`TR-001` `O-05`) | Localisation Lead | W3 |
| **O-04** | Rider cash limits (article 19) are set by `SP-019` and are not yet defined per role | Finance with Logistics | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] The severest reading constraint in the register stated and bounded to five steps, one screen (`PS-22`)
- [x] 30 articles enumerated with type and priority
- [x] The 60% P0 proportion justified rather than left as inflation (`PS-23`)
- [x] The five exposure articles identified (`PS-24`)
- [x] Hazard card authored once in `KB-016` and referenced (`CP-01`)
- [x] All internal links resolve
- [x] `P09` constraints cited to `04-00`; `KB-013` §4.4 for the transport constraint
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 30 articles authored — outstanding**
- [ ] **`O-01` damaged-battery transport standard — outstanding; blocks a P0 article**
- [ ] **`O-02` offline delivery at W3 — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Logistics Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
