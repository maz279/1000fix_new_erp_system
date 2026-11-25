# M54 Costing, Budget & FP&A: Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M54 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M54_Cost_Accounting_Budgeting_and_FPA.md`. Sections used:
  - §3: scope (24 capabilities);
  - §5: FR-FPA-001 … 040;
  - §8: the period cost cycle, the budget cycle (target → preparation → submission → approval → revision) and the allocation cycle lifecycle;
  - §9: BRU-FPA-01 … 25;
  - §10.1: the 31 owned entities;
  - §11: AUT-FPA-01 … 20;
  - §13: roles and segregation of duties;
  - §18: open questions Q-01 … Q-14.
- Research: `audit_analysis/A08_FINANCE_TARGET_SPEC.md` (M54 build list).
- Code:
  - `cd_p03_portal/static/src/a08/m54.js`: the page registry (8 sub-module pages);
  - `cd_p03_portal/controllers/a08/m54.py`: surfaces, reports and KPIs;
  - `cd_fpa/models/*.py`: budgets, versions, cost pools and elements, allocation cycles, board packs and the reporting engine.
- Live data (fix_real, read-only count on 17 Nov):
  - 14 business lines, 1 cost pool with 3 cost elements;
  - **no** budget version, budget, budget line, allocation cycle, board pack or scenario driver;
  - no service order or work order, so the job-costing and loaded-cost reports are empty;
  - 5 users hold Accounting Administrator and 1 holds Accountant, so every two-person step below can be staffed.

## 1. What was there (HEAD 94bf9e99)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Cost Model | Cost Pool | Allocation Rule (the pool) | The page lists **cost elements** with no chip, although the form existed. **No cost centre** (FR-FPA-001 P0): the cost centre was free text on budget lines and journal dimensions, with no owner, parent, branch or allocation behaviour, so no variance could be put to an accountable owner (BRU-FPA-12). |
| 2 | Allocation Cycles | Allocation Cycle | Allocation Cycle | None for capture. (Control gaps in §4.) |
| 3 | Job & Contract Costing | **none** | **none** | The page **captured nothing**. **No planned activity rate** (FR-FPA-012/013 P0, BRU-FPA-16 H "approved by the CFO and applied consistently"): job costing applied each technician's *actual* rate over whatever window the report was asked for, so the same hour cost differently on different days and nobody approved the rate. |
| 4 | Business-Line Profitability | Business Line | **none** | The Business Line chip existed but was not on the page; no way to explain a business-line variance. |
| 5 | Branch & Channel Profitability | **none** | **none** | The page **captured nothing**. Branch managers own their branch's variance explanation (spec §13), and there was no record for it. |
| 6 | Budgeting | Budget | Budget Version | **No top-down target** (FR-FPA-029 P0, spec §8.2 "Target set by CFO/CEO"): a budget could be submitted with nothing to be read against. |
| 7 | Variance & Forecast | **Budget** | Scenario | The "+ New" opened a **budget** (page 6's record). **No variance explanation** (FR-FPA-037 P0, BRU-FPA-12 H, AUT-FPA-07/08): the variance report could not be acted on, and the "100% explained within 3 working days" target (AC-20) could not be measured. A forecast version could only be started from the budget workflow, not from this page. |
| 8 | Board Pack | Board Pack | Board Pack | None. |

Guard `cd_p03_portal/tests/test_m54_capture_buttons.py` on HEAD: **16 of 29 tests fail.** The failures cover pages 1, 3, 4, 5, 6 and 7, the Budget offered on the variance page, the creatable lists with no capture, the missing records, and their security.

## 2. What was built

### Backend: `cd_fpa` 19.0.0.4.0, new file `models/fix_fpa_capture.py`

Every decision is taken by someone other than the person who raised it. Stamps and measured figures are guarded fields, never typed.

| Page | Record | Holds | Rules |
|---|---|---|---|
| 1 | `fix.cost.centre` (FR-FPA-001) | Code (the one written on budget lines and journal dimensions), name and Bengali name, parent, branch, **owner**, allocation behaviour (absorbing / allocating / both), active window. | Maintained by Accounting Administrators; accountants read. No cycles in the hierarchy. Never deleted (deactivated). The owner is who explains the centre's variances. |
| 3 | `fix.activity.rate` (FR-FPA-012/013, BRU-FPA-16) | Activity (technician hour, workshop hour, delivery, contact), branch or all branches, planned rate, **composition** (required), effective window, and the actual loaded rate measured over a comparison window (payroll + loaded overhead ÷ productive hours) beside it. | Prepared and submitted by finance; **approved by an Accounting Administrator who neither prepared nor submitted it**, then frozen. A change is a new rate: approving it closes the old one the day before it takes effect, so a past job is still explained by the rate then in force; a replacement that would take effect in the past is refused. Rejection needs a reason. |
| 3 | Job costing (engine) | — | Labour on a job is now work-order hours × **the approved planned rate** in force for the order's branch on the day the work finished (the branch's own rate wins over the all-branch rate). Where no rate is approved, the technician's actual loaded rate is used as before. The job-costing report shows which rate was used. |
| 6 | `fix.budget.target` (FR-FPA-029, AUT-FPA-13) | Budget or forecast version, scope (company, branch, business line, cost centre), measure (revenue, cost, margin), target amount, guidance. Plan, plan − target and departure % are read live from the version's lines. | Set and issued by an Accounting Administrator, only while the version is draft or submitted. Issued targets are frozen; one issued target per scope and measure; withdrawal needs a reason. **Submitting a version posts its departures from every issued target** on the version. |
| 4, 5, 7 | `fix.variance.explanation` (FR-FPA-037, BRU-FPA-10/12, AUT-FPA-07/08) | What the variance is of (a budget line, a branch, or a business line) and the period; **budget, actual, variance and variance % measured** from the approved budget and the posted ledger when it is raised; threshold; accountable owner; due date (3 Bangladesh working days); root cause, explanation and action committed. | Measured only against an **approved** version. The scope and period are fixed once measured; figures are never typed (Re-measure while open picks up late postings). The owner defaults to the cost-centre owner, else the version's preparer; only an Accounting Administrator reassigns it. **Only the owner writes and submits** the explanation. **An Accounting Administrator who is neither the owner nor the submitter accepts it or returns it with a reason.** Accepted explanations are final and never deleted. One explanation per scope and period. **A daily job raises one for every approved line whose variance last month passed the threshold** (default BDT 50,000 and 10%, until the CFO sets `cd_fpa.variance_threshold_amount` / `_pct`), with a to-do for the owner; another gives overdue ones a to-do. |

Security and data:
- ACLs: the read-only finance group reads; accountants prepare rates and raise explanations; administrators maintain cost centres and targets and take every decision; nobody deletes a cost centre or an explanation, and a rate or target only while draft. Every model has its own administrator row.
- Company and operating-unit isolation rules from `generate-isolation-rules.py`. Only the cd_fpa file was kept; the generator's pre-existing drift in four other modules was reverted.
- Three sequences (ACR/, BTG/, VEX/) and two daily jobs.
- Load order: the new file extends `fix.budget.version` and `fix.fpa.engine`, so it is imported last (`# ruff: noqa: I001`).

### Workspace: `m54.js`, `controllers/a08/m54.py`, `writable.py`

- Seven new lists, on their pages and in the navigation: Cost Centres, Planned Activity Rates, Top-Down Targets, Variance Explanations, Branch Variance Explanations, Business-Line Variance Explanations, Forecast Versions.
- Seven new forms. Planned Activity Rate, the three Variance Explanation forms and Forecast Version are tabbed (AGENTS.md). The branch and business-line forms preset their scope.
- `writable.py` was regenerated with `form_fields.py --a08`; only the M54 entries changed. The variance forms are written out literally, because the generator reads the declarations as text (a JS helper hid their fields from it in the first draft).

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Cost Model | Cost Pool | Allocation Rule, **Cost Element**, **Cost Centre** |
| 2 Allocation Cycles | Allocation Cycle | Allocation Cycle |
| 3 Job & Contract Costing | **Planned Activity Rate** | **Planned Activity Rate** |
| 4 Business-Line Profitability | Business Line | **Business Line**, **Business-Line Variance Explanation** |
| 5 Branch & Channel Profitability | **Branch Variance Explanation** | **Branch Variance Explanation** |
| 6 Budgeting | Budget | Budget Version, **Budget Target** |
| 7 Variance & Forecast | **Variance Explanation** (was Budget) | **Variance Explanation**, **Forecast Version**, Scenario |
| 8 Board Pack | Board Pack | Board Pack |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m54_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. | **HEAD 94bf9e99: 16 of 29 fail.** After: **29/29.** |
| Live tests `cd_fpa/tests/test_m54_capture_live.py`, run as non-admin finance users (two accountants, two Accounting Administrators holding the CFO tier, a plain user) on a private clone `fix_test_m54` (`-u all`, exit 0). Budget versions are approved through the real M63 inbox. | **14/14.** |
| Job costing with an approved rate (`test_a08_m54_reports.py`, new test): the branch rate wins over the all-branch rate and is applied to the work-order hours. | Green. |
| Mutation check: each rule removed in turn (rate approver differs from preparer and submitter; approved rate frozen; no replacement in the past; approval closes the old rate; issued target frozen; one issued target per scope; measured figures never typed; only the owner writes and submits; reviewer differs from owner and submitter; only an administrator reassigns; scope and period fixed; approved version only; monthly job threshold; job costing applies the approved rate). | **15 of 15 mutations turned the tests red;** the source was restored byte for byte. |
| Regression on the same clone: every `cd_fpa` test plus the portal's M54 registry, reports and capture guards, the estate page guard, the A08 write whitelist and control suite, KPI tiles, the A03/A04 registry and child-form guards and M49. | **1,242 tests: 0 failures, 0 errors.** 35 skipped, all "model carries no workflow-controlled fields" in the control suite (not applicable). Final run after formatting: 55/55. |
| Workspace endpoints and UI on a private server (port 8086), signed in to the clone. | All 5 new or extended lists serve every column (none silently dropped). Page 3 shows "+ New Planned Activity Rate"; a rate was saved from the tabbed form (Draft; the server first refused it without an effective date). Page 5 shows "+ New Branch Variance Explanation" and opens the tabbed form with the scope preset to Branch. Page 7 shows "+ New Variance Explanation" with the Variance Explanation, Forecast Version and Scenario chips. |
| `generate-isolation-rules.py`, `form_fields.py --a08` | Only the cd_fpa / M54 entries changed. |

## 4. Not built here (owner decisions or other modules)

- **Allocation cycle versioning and CFO approval** (BRU-FPA-05, spec §8.3, "the author of a cycle cannot approve it"): the pool is the allocation rule and is maintained by any Accounting Administrator with no approval; fixed shares are manual drivers without the approval BRU-FPA-06 asks for. The allocation *run* already separates compute and post. Adding an approval to the pool changes how every existing pool is used, so it is an owner decision (Q-01 — the allocation policy itself is undecided).
- **Standard costs** (FR-FPA-016 P1, BRU-FPA-24): spec Q-12 asks the owner whether standard costing is wanted at all.
- **Inter-branch transfer pricing** (FR-FPA-010 P2): spec Q-10. Inter-company transfer-pricing rates already exist in `cd_multi_entity`.
- **Contract costing and the negative-margin register** (FR-FPA-014/015 P0, AUT-FPA-06): these are reports over M08 contracts and M53 recognised revenue, not captures; there is no contract-cost report yet. A follow-up, not a capture button.
- **Budget commitments and availability** (FR-FPA-032/033, AUT-FPA-15/16): computed from approved POs and capex requests; nothing for a person to capture.
- **Initiative benefit tracking** (FR-FPA-040 P2).
- **Absorption reconciliation** (FR-FPA-013 second half): with planned rates now approved and applied, the under/over-absorption report (planned applied vs actual loaded cost) can be built from the two figures the rate form already shows.
- **CFO group**: there is no CFO group in Odoo (R-03 is a role record), so an Accounting Administrator other than the preparer approves rates and issues targets until the owner maps R-03 to a group.
- **Variance threshold** (spec Q-05): defaults to BDT 50,000 and 10% until the CFO sets the two parameters.
- **Data**: fix_real holds no budget version, so no variance can be measured and the monthly job raises nothing until a budget is approved. No cost centre, rate or target exists yet: these are a data take-on for the finance team.

## 5. State

- Built and tested in worktree `m54cap-wt` on branch `fix/m54-capture-buttons`, from the working branch tip 94bf9e99.
- Fix commit 675f071c is on the working branch `fix/a03-live-data-and-pending-work`, moved by compare-and-swap from 94bf9e99. **Not pushed.**
- **Deployed on fix_real (8069) and fix_dev (8090) on 17 Nov 2026**, on the user's approval. It went out inside the M49 session's combined deploy (the user chose to include M54 there rather than run two restarts), so this session did not upgrade or restart anything itself:
  1. Backups `fix_real_pre_m49_gaps_2026-11-17.dump` and `fix_dev_pre_m49_gaps_2026-11-17.dump`.
  2. `-u cd_fixed_asset_ext,cd_fpa,cd_p03_portal` on each database; cd_fpa is 19.0.0.4.0 on both, and no cd_ module lags its code.
  3. Restarts: 8069 PID 52108 became 78988 (13:42 UTC), 8090 PID 45588 became 66868 (13:46 UTC).
- Verified by this session on 8069 after the restart:
  - the new process logged 155 modules loaded and no ERROR line; login answers 200;
  - the four models, their 12 access rows, the three sequences (ACR/, BTG/, VEX/) and both daily jobs exist in fix_real;
  - the served bundle 02b1916 (the same on 8090) carries all seven new M54 forms;
  - the M49 session read all four new models through `/p03/model/records` on both servers (0 rows each).
- Between the upgrade and the restart, the old 8069 process ran the two new M54 jobs once at 12:53 UTC and logged them as failed (it did not yet know the new models). The restarted process runs them normally.
- fix_real holds no budget version, cost centre, rate or target yet, so the lists are empty and the monthly job raises nothing until a budget is approved.
