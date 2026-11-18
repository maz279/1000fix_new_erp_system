# M67 Projects & Portfolio: sub-module capture audit

**Date:** 18 Nov 2026 · **Area:** A12 · **Base:** `bd3f4796` · **Branch:** `fix/m67-capture-buttons`
**Spec:** `1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M67_Project_Program_and_Portfolio_Management.md`
**Workspace fragment:** `cd_p03_portal/static/src/a12/m67.js` · **Controller:** `cd_p03_portal/controllers/a12/m67.py`
**Backend:** `cd_ppm` (new `models/fix_ppm_capture.py`)

The user saw M67 sub-module pages without a relevant data-capture button. That was right. Two pages
had no form chip at all, and five records the specification makes M67 own did not exist anywhere in
the code, so no page could capture them.

## 1. Method

1. **Spec.** Each of the 6 Function Register sub-modules was mapped to the FR-PPM requirements (§5),
   the business rules (§9) and the owned entities (§10.1).
2. **Code, as the browser evaluates it.** Node ran the workspace engine's own `fregCreate` and
   `fregPanels` over the real registry fragments. This gave each page's "+ New", its form chips and
   the lists it shows.
3. **Data on fix_real (8069).** Read-only counts: 0 projects, 2 templates, and 0 milestones, tasks,
   gates, billing lines and risks. Nothing live is affected by the closure rules below.
4. **Build and proof.** Built in a worktree and tested on a private database (`fix_test_m67c`).

## 2. What the pages offered at HEAD

| # | Page | "+ New" | Chips | Defect |
|---|---|---|---|---|
| 1 | Portfolio | Project | Project | Correct |
| 2 | Project Setup | Project Template | Project | No chip for the page's own record, the template |
| 3 | Delivery | Task | Task, Milestone | **No deliverable register** (FR-PPM-004 **P0**): nothing recorded what a milestone hands over or who accepted it. The Resource Utilisation report sat on no page |
| 4 | Governance | Stage Gate Review | Stage Gate Review | **No scope change control** (FR-PPM-013 **P0**, BRU-PPM-06 **H**): a change could not be priced or decided |
| 5 | Financials | Milestone Billing | **none** | **No budget by cost category** (FR-PPM-024 **P0**) |
| 6 | "Audit" | Risk / Issue | **none** | The page holds the risk and issue register, not an audit. **No lessons learned** (FR-PPM-032 **P0**, BRU-PPM-14 **H**) and **no benefit realisation** (FR-PPM-032 **P0**, BRU-PPM-15 **H**). The Benefits Realisation report printed "not recorded" on every row because nothing could record a benefit, and it sat on no page |

The guard test written for this audit (`test_m67_capture_buttons.py`) fails **13 of its 22 checks
on HEAD**, on pages 2 to 6.

## 3. What was built

### Workspace (`m67.js`)

| # | Page | "+ New" | Chips now | New lists and reports |
|---|---|---|---|---|
| 1 | Portfolio | Project | Project | — |
| 2 | Project Setup | Project Template | **Project Template**, Project | — |
| 3 | Delivery | Task | Task, Milestone, **Deliverable** | Deliverables list; Resource Utilisation report placed |
| 4 | Governance | Stage Gate Review | Stage Gate Review, **Scope Change** | Scope Changes list |
| 5 | Financials | Milestone Billing | **Milestone Billing**, **Budget Line** | Budget by Category list |
| 6 | **Risks, Issues & Closure** (was "Audit") | Risk / Issue | **Risk / Issue**, **Lesson Learned**, **Benefit Measurement** | Lessons Learned and Benefit Realisation lists; Benefits Realisation report placed |

- The module's form chips grew from 4 to 12, and every chip sits on a page.
- A new "Closure" navigation group holds the lessons, benefits and the benefits report.
- Two new KPI tiles: **Scope Changes Pending** and **Deliverables Awaiting Acceptance**.

### Backend (`cd_ppm` 19.0.0.2.0, `models/fix_ppm_capture.py`, imported last)

- **`fix.project.deliverable`** (FR-PPM-004, §8.2):
  - records acceptance criteria, the evidence required, the reviewer and the attached evidence;
  - submission needs the evidence and a reviewer who is not the submitter;
  - the reviewer, or a sponsor, accepts it or sends it back with a reason;
  - once submitted, what the reviewer judges cannot change;
  - **a milestone with deliverables completes only when they are all accepted** (BRU-PPM-11).
- **`fix.project.change`** (FR-PPM-013, BRU-PPM-06):
  - each change is priced for cost, schedule and resources;
  - a sponsor who neither raised it nor manages the project approves or rejects it, and a rejection states why;
  - once submitted it cannot be rewritten;
  - on approval the schedule impact moves the planned end;
  - on a running project an approved cost increase becomes the **Requested Budget**, which re-baselines the project only through the DOFA approval the project already routes (BRU-PPM-05/07). The change never edits the budget itself;
  - a change still waiting for a decision blocks closure.
- **`fix.project.budget.line`** (FR-PPM-024):
  - one line per cost category (labour, parts, subcontract, travel, equipment, overhead);
  - the lines never exceed the project budget;
  - they freeze when the project is activated and its budget baselined;
  - Budget vs Actual now shows the category split and the unallocated rest.
- **`fix.project.lesson`** (FR-PPM-032, BRU-PPM-14):
  - "Pass to Quality (M23)" publishes `project.lesson_recorded`;
  - once passed, a lesson is evidence and cannot be edited or deleted;
  - **a project closes only with at least one lesson passed to Quality.**
- **`fix.project.benefit`** (FR-PPM-032, BRU-PPM-15):
  - records the business-case target, its unit and the measurement method;
  - only for internal initiatives;
  - a sponsor who does not deliver the initiative records the measurement, with evidence;
  - once measured, the target is fixed;
  - **an internal initiative closes only with a benefit measured**;
  - the Benefits Realisation report now shows each benefit as "measured of target" and the realised %.
- **Security.**
  - Access rows for all five models: internal users read only; project managers and sponsors as each workflow needs.
  - Company isolation rules regenerated by `generate-isolation-rules.py`.
  - The A12 write whitelist names exactly the typed fields. State, decision and stamp fields are never writable.
- **Event contracts.** `project.change_approved` and `project.lesson_recorded` added to `contracts/events`.
- **Existing tests.** The four closure tests in `test_a12f_m67_finish.py` and `test_ppm_orm.py` now record the lesson, and the benefit for an internal project, that the new rules require.

## 4. Proof

| Check | Result |
|---|---|
| Guard `test_m67_capture_buttons.py` (engine-evaluated pages, served models and actions, write whitelist, stamps never typed, prompt kwargs, ACL and rules, load order, KPIs, closure hook) | **22/22** on the branch; **13/22 fail on HEAD** |
| Live `test_m67_capture_live.py` (non-admin project managers, sponsors and a plain reviewer, through the P03 controller the screen calls) | **16/16** |
| Endpoint probe as a non-admin project manager and sponsor | 12 lists, 12 forms, 10 reports: **0 errors** |
| Mutation check (one control removed at a time) | **18/18** turn the live tests red. Four survived the first run, because another check masked them; the tests were strengthened until each control is caught on its own |
| cd_ppm suite (all M67 tests) | 7 failures, **identical on untouched HEAD** with the same failure points: the M60 enterprise-register relay (F5 tests, the full walk), the seed's dead hand-off and the progress consumer. None involves the new records |
| Portal static checks (estate page standard, A12 write whitelist, A12 DOFA coverage, sub-module create button) | pass, except one pre-existing failure that names M19 and M30 pages, not M67 |
| Lint | ruff check and format clean |
| Browser click-through | **Not done.** The browser pane was hidden, so the web client never mounted. The pages were evaluated with the engine's own functions instead (guard above) |

The live tests found two defects the static checks could not:

- **The reference was a guarded field, so the create that filled it from the sequence was refused.** It is now stamped by the server after the create.
- **The closure check ran before the Finance confirmation.** A project with unconfirmed billing then reported a missing lesson instead of the billing problem. The check now runs last, just before the project closes.

The A12 seed (`db/seeds/a12_finish_m67.py`) closes its walk project. It now records and passes a lesson first, as the new rule requires.

## 5. Not built (gaps for the owner)

| Item | Why it is not built here |
|---|---|
| **Role-based resource demand, named assignment and conflict detection** (FR-PPM-017..020 P0, BRU-PPM-08..10) | Needs availability from the M55 roster, dispatch commitments from M02 and certificates from M22. M67 must hold no calendar of its own (T-04). This is an integration build across three modules, not a capture button. Tasks still name their assignee. |
| **Timesheets** (FR-PPM-021) | Effort is captured with the task's Log Hours action. Per-day entries reconciled with M55 attendance (BRU-PPM-21) need the same M55 integration. |
| **Programme grouping** (FR-PPM-006, P1) | P1. No programme model. |
| **Phases, work packages and the cost by source reference** (FR-PPM-003/025, BRU-PPM-12) | Cost is measured from project-tagged ledger postings and task hours. It is never typed, which BRU-PPM-12 requires. Work-package cost collection is a costing redesign. |
| **Quality (M23) consuming `project.lesson_recorded`** | The event is published and in the contract registry. No M23 consumer exists yet: M23 (`cd_qms_process`) owns that. |
| **Project types** | The spec names five types. The model has three (internal, client, infrastructure), and the form label still says "Project (6 types)". This is an owner decision on the type list, not a capture gap. |

## 6. Deployment

Not deployed yet. fix_real has no projects, so the new closure rules change nothing live. Deploying needs `-u cd_ppm,cd_p03_portal` on fix_real and one 8069 restart, because the controller serves new models.
