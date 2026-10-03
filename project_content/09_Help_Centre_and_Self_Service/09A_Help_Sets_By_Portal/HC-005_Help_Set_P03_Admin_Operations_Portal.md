---
id: HC-005
title: Help Set — P03 Admin Operations Portal
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Branch and Back-Office Operations
reviewers: [Operations Director, Quality Manager, Finance Manager, Inventory Manager, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead with Operations Director
content_class: D
purpose: >
  The sustaining help layer for 150–250 back-office users across fourteen P03 workspaces, bulk
  actions, exception handling and permissions. P03 targets training-time-to-competence under four
  hours; help is what carries the user from that four hours to competence across a workspace set no
  induction could cover, and it is the only W1 help set in the register.
traces_to: [P03, M01, M02, M04, M15, M19, M23, M30, M61, MD-026, HC-001, HC-002, HC-016, UI-013, UI-023, UI-036, TR-007, TR-022, SP-005]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: HC-005_Help_Set_P03_Admin_Operations_Portal_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P03 delivered as fourteen role-scoped workspaces for 150–250 back-office users on 1366×768 branch hardware; training-time-to-competence under four hours
    verified: 2026-08-18
    class: P1
  - source: project_content/08_Training_and_Enablement/08B_Course_Packs/TR-007_Course_Pack_Service_Centre_Agent.md §3.2 and §3.3 — what the four hours covers and what is deliberately deferred to help and job aids
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BR-STD-06 — overrides are permitted only where designed and are always logged with a reason
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P03 Admin Operations Portal

| Item | Value |
|---|---|
| Portal | `P03` Admin Operations — fourteen workspaces |
| Audience | **Internal operations user** — audience 3 · 150–250 |
| Article type | Help set specification — Task and Troubleshooting predominate |
| Reading level target | `CG-011`; trained audience, so operational vocabulary is permitted |
| Languages | Bengali primary for branch roles; English parallel |
| Related UI copy | `UI-013` · `UI-023`…`UI-036` workspace packs |

> **Template conformance.** As `HC-003`, applied at set level. **This is the only `W1` help set**,
> and the only one whose audience is guaranteed to have been trained (`TR-007` and siblings) —
> which changes what it must cover.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and article shape |
| `UI-013` and the fourteen workspace copy packs | Labels quoted in steps (`HS-08`) |
| [`../../08_Training_and_Enablement/08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md) | **The boundary — see below** |

**`PS-08`: this set is not the twenty most frequent tasks.** Those are `TR-022` job aids, for a
trained user at the point of work. **This set covers what training deliberately left out** —
`TR-007` §3.3 defers bulk and corporate intake, pick-and-drop booking, loyalty handling, complaint
intake beyond acknowledgement, and trade-in to weeks 2–4. Help is where those live.

| Question | Owner |
|---|---|
| *"The twenty things I do every day"* | **`TR-022`** job aid |
| *"The thing I do twice a month and have forgotten"* | **`HC-005`** — this set |
| *"Why does the system stop me here?"* | **`HC-005`** — exception and permission articles |

---

## Steps — *the workspace set and its article inventory*

### Block A — Cross-workspace *(8 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 1 | Find anything — search, filters and saved views | Task | **P0** |
| 2 | **Bulk actions — and what cannot be undone** | Task | **P0** |
| 3 | **Why the system stopped you** — reading a block | **Concept** | **P0** |
| 4 | Record an override with a reason | Task | **P0** — `BR-STD-06` |
| 5 | Your permissions and what lies outside them | Concept | P1 |
| 6 | Export and report from a workspace | Task | P1 |
| 7 | Keyboard shortcuts and working fast | Concept | P2 |
| 8 | Working on branch hardware — 1366×768 | Concept | P2 |

### Block B — Service and dispatch workspaces *(9 articles)*

Intake exceptions · unresolved device · walk-in to on-site conversion · dispatch re-routing ·
capacity exceptions · workshop hold management · QC gate refusal · rework linking · pick-and-drop
booking. **2 at P0, 5 at P1, 2 at P2.**

### Block C — Inventory, procurement and finance workspaces *(9 articles)*

Stock adjustment above threshold · inter-branch transfer · quarantine · van reconciliation
exceptions · requisition to PO · three-way match exception · invoice correction · counter cash
reconciliation · month-end tasks. **3 at P0, 4 at P1, 2 at P2.**

### Block D — Contract, warranty and quality workspaces *(7 articles)*

Contract activation and covered assets · entitlement queries · claim assembly · claim rejection
handling · NCR raising · CAPA assignment · audit finding classification. **1 at P0, 4 at P1,
2 at P2.**

### Block E — Exceptions and recovery *(7 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 34 | **A transaction failed halfway** | Troubleshooting | **P0** |
| 35 | Duplicate record — which to keep | Troubleshooting | P1 |
| 36 | Data looks wrong — who to tell | Task | P1 |
| 37 | The system is slow or unavailable | Troubleshooting | P1 |
| 38 | **Working when the system is down** | Concept | **P0** — manual fallback |
| 39 | Recovering after an outage | Task | P1 |
| 40 | Escalate a system problem usefully | Task | P1 — `SP-005` |

**Set total: 40 articles · 11 at P0 · 20 at P1 · 9 at P2.**

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Users reach competence beyond the four-hour core | Time to unaided completion of deferred tasks | Falling |
| Blocks are understood rather than worked around | **Block-workaround attempts** | Approaching zero |
| Overrides are logged with valid reasons | Override logging rate | 100% (`BR-STD-06`) |
| Help desk contacts on `P03` tasks fall | Contacts per user per wave | Falling wave on wave |

**`PS-09`: article 3 — reading a block — is the highest-value article in this set.** `TR-007` §4
records the misconception it exists to correct: *"The system won't let me, so I'll book it as
something else."* A user who understands why a control exists stops trying to defeat it.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Help contacts high on tasks that have a job aid | Users cannot tell which artefact to use | `PS-08` boundary unclear; review with L&D |
| Block-workaround attempts persist | Article 3 not reaching people, or the block message itself is opaque | Check `UI-004` message quality first |
| Same question across many branches | It is a product or process gap, not a help gap | Route as `TR-023` module 8 does |
| Articles orphaned after a release | `HS-38` review not run | `TR-024` `RL-04` |

---

## Related

`UI-013` and the fourteen workspace packs · [`../../08_Training_and_Enablement/08B_Course_Packs/TR-007_Course_Pack_Service_Centre_Agent.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-007_Course_Pack_Service_Centre_Agent.md) ·
[`../../08_Training_and_Enablement/08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md) ·
[`../../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md`](../../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) ·
[`../HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md`](../HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) · [`HC-012_Help_Set_P10_Contact_Centre_Console.md`](HC-012_Help_Set_P10_Contact_Centre_Console.md) — agents cross between consoles.

---

## Feedback

Helpfulness per `CG-014`, plus **help-desk topic correlation**: an article with high views and a
rising help-desk topic is failing, not succeeding.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Articles required | **40** · written **0** |
| Effort | 40 × 2–3 h = **80–120 hours** |
| **Sequencing** | **This is the only `W1` help set.** The 11 P0 articles are needed at W1 go-live alongside `TR-007` |
| Bengali | All 40; branch-facing articles authored in Bengali |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`W1` is the tightest deadline in this category.** `HC-001` and `HC-002` — which govern this set — are both `W2`. **The set that must ship first is governed by files that ship second.** Raised as audit finding **HC-01** | Programme Content Lead | **W1** |
| **O-02** | The `PS-08` boundary with `TR-022` needs the same joint owner `TR-022` `O-02` requests | Programme Content Lead with L&D | **W1** |
| **O-03** | `TS-002` sandbox for screenshots (`HS-19`) does not exist | Test Lead | W1 |
| **O-04** | Blocks B–D article titles are summarised rather than enumerated individually; they must be itemised before authoring begins | Content Design with workspace owners | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] **Boundary with `TR-022` stated: help covers what training deferred (`PS-08`)**
- [x] 40 articles enumerated by block with type and priority
- [x] The highest-value article identified and tied to a recorded misconception (`PS-09`)
- [x] Manual-fallback and outage-recovery articles included
- [x] All internal links resolve
- [x] `BR-STD-06` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` W1 set governed by W2 files — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
