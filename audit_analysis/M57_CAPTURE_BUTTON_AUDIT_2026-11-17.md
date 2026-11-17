# M57 Performance, Incentives & Compensation: Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M57 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M57_Performance_Incentives_and_Compensation.md`. Sections used:
  - §3: scope (13 capabilities) and boundaries (M56 pays, M21 records salary, M22 closes gaps);
  - §5: FR-PIC-001 … 042;
  - §8: the incentive period and performance review lifecycles;
  - §9: BRU-PIC-01 … 17;
  - §10.1: the 21 owned entities;
  - §11: AUT-PIC-01 … 15;
  - §13: roles and boundaries (S2 data, anonymised comparison, SOD-30).
- Code:
  - `cd_p03_portal/static/src/a09/m57.js`: the page registry (7 sub-module pages);
  - `cd_p03_portal/controllers/a09/m57.py`: surfaces, reports and KPIs;
  - `cd_performance/models/*.py`: scorecards, incentive runs and lines, schemes and versions, disputes, clawbacks, goals, reviews, PIPs, recognition, bands, succession, compensation proposals.
- Live data (fix_real, read-only count on 17 Nov):
  - one incentive scheme with one version, still **draft** ("as coded, unsourced"); 4 salary bands;
  - **no** goal, scorecard, review, PIP, recognition, incentive run, clawback, proposal or succession plan;
  - 504 active employees, 269 with a line manager; **no active employment contract**, so no compensation proposal can be raised yet;
  - every M57 role group has 2 holders; 6 users hold HR Manager.

## 1. What was there (HEAD c5feece6)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Goals & KPIs | Goal | Goal | Its "KPI Definitions" list showed **technician scorecards**, with `create: false` and no chip: **no scorecard could be started anywhere in the workspace**, and an incentive run computes only from published scorecards, so no run could ever compute from the workspace. **No KPI definition existed** (FR-PIC-006 P0, T-01): the scorecard weights and targets were code constants, with no version, effective date or approval, and nothing showed an employee their value against a target. |
| 2 | Review Cycles | 360 Review | Review | **No review cycle** (FR-PIC-016 P1): HR raised one review at a time; no population, no stage deadlines, no probation cycle (FR-PIC-017), and nothing chased an overdue stage (AUT-PIC-11). PIPs were listed with no chip. |
| 3 | Multi-Source Feedback | **360 Review** | Review | The "+ New" opened a **review** (page 2's record). **No feedback record existed** (FR-PIC-020): the page could not ask a peer, a subordinate or a cross-functional colleague anything. |
| 4 | Rating & Calibration | **none** (`create: false`) | **none** | The page **captured nothing**. **No calibration session** (FR-PIC-021 P1, BRU-PIC-13 H "calibrated across managers before finalisation"): calibration was one inbox approval per review that copied the manager's rating unchanged, so a calibrated rating could never differ from the manager's, the "Calibration Summary" movement column was always 0, and there was no before/after distribution (spec §14). |
| 5 | Incentive Design & Calculation | **none** | "Incentive Scheme" | No "+ New" (the page's model is the computed payout line). Its one chip, **"Incentive Scheme", opened an incentive *run***. The scheme and scheme-version forms were on no chip. **No incentive adjustment** (FR-PIC-033 P1, BRU-PIC-10 H): a correction, a fraud reversal (FR-PIC-034) or a discretionary award could not be recorded, approved or shown to the employee. |
| 6 | Recognition | Spot Recognition | Recognition | None. |
| 7 | Compensation Review | Compensation Band | **none** | No chip at all; succession plans were listed with no capture. **No compensation cycle** (FR-PIC-038 P1): no budget, window or guidelines, so **BRU-PIC-17 H** ("a proposal exceeding the cycle budget requires CFO approval") could not be applied. |

Guard `cd_p03_portal/tests/test_m57_capture_buttons.py` on HEAD: **18 of 37 tests fail.** The failures cover pages 1, 2, 3, 4, 5 and 7, the review offered on the feedback page, the scheme chip that opened a run, the creatable lists with no capture, the six missing registers, their security and their load order.

## 2. What was built

### Backend: `cd_performance` 19.0.0.5.0, new file `models/fix_m57_capture.py`

Every decision is taken by someone other than the person who raised it, and other than the employee it is about. Stamps, measured figures and answers are guarded fields, never typed through a form.

| Page | Record | Holds | Rules |
|---|---|---|---|
| 1 | `fix.kpi.definition` (FR-PIC-006, T-01, BRU-PIC-04) | Code, name, role profile, measure (jobs completed, first-time fix, SLA, CSAT, rework, 30-day repeat repair), the fact source, unit and direction (derived from the measure), a plain-language formula, target, threshold, version and effective window. | Prepared and submitted by an Incentive Officer or HR Manager; **approved by an HR Manager who neither prepared nor submitted it**, then frozen. A change is a new version: approving it closes the old one the day before it takes effect, and a replacement that would take effect in the past is refused (BRU-PIC-02). **A volume KPI is approved only alongside a quality KPI in force for the same role (BRU-PIC-04).** Threshold and target must agree with the direction. Every employee may read the definitions (T-08). |
| 1 | Technician scorecard (extended) | **KPI Attainment** tab: each approved field-technician KPI in force at the period end, the scorecard's value against its target and threshold, and the KPIs below threshold. | Read-only. **Pay is not changed**: the composite and the bands remain the approved scheme version's, because what is rewarded is a business decision (spec §16.3). The Technician Scorecard chip now lets an Incentive Officer start a scorecard from page 1. |
| 2 | `fix.performance.review.cycle` (FR-PIC-016/017, AUT-PIC-11) | Name, type (probation, quarterly, half-yearly, annual), period, population (named employees, else a department, else the company; a probation cycle takes the employees whose active contract's probation ends by a date), and the three stage deadlines in order. | Set up and opened by an HR Manager. **Opening raises one review per employee of the population who has a line manager**, reviewed by that manager; the others are listed as not raised. Population, period and deadlines are fixed once open. A cycle closes only when every review in it is closed. **A daily job gives whoever holds an overdue stage a to-do, and their own manager one too**, once. |
| 3 | `fix.performance.feedback` (FR-PIC-020) | Review, respondent, relationship, answer-by date; the answer (rating 1-5, comments, to-improve) or the reason for declining. | Requested by HR on a review that is not yet calibrated. **The respondent is neither the employee nor their line manager.** **Only the respondent answers or declines**, through a narrow action (no write access needed); an answer is final. **The employee never reads who said what (T-10)**: the record is visible to the respondent, the line manager and HR; the review shows the count and the average. |
| 4 | `fix.performance.calibration.session` + `.line` (FR-PIC-021, BRU-PIC-13) | Period, optional review cycle, scope, date, managers taking part, minutes; **the distribution before** (measured from the managers' ratings when the session starts) and **after** (measured from the calibrated ratings when it concludes); rating changes, each with a reason. | Opened by HR or a Performance Calibrator. Ratings change only while the session is in session, and only on a calibrated, not yet closed review. **Concluding needs every rating in scope calibrated**, is done by someone who neither gave nor received a changed rating, applies the changes to the reviews (with a note on each) and freezes the session. **While a session over a period is open, no review of that period is closed.** |
| 5 | `fix.incentive.adjustment` (FR-PIC-033/034, BRU-PIC-10/11, T-06) | Employee, period, type (correction, reversal of a fraudulent or invalid job, discretionary award), signed amount, reason, evidence, service order. | Raised by an Incentive Officer, **never for their own pay**. A reversal is negative and **names its evidence**; a discretionary award is positive. **Routed through the M63 inbox to an Incentive Approver** who neither raised it nor is its subject. **The employee is told when it is approved, before it is applied** (a to-do and a message). It becomes a **visible line** of the period's run, with its reason, when the run is computed (reset and recompute a computed run); resetting the run puts it back to approved. **An approved period is locked: an adjustment for it is refused** (T-06). **No run takes anyone's incentive below zero.** Never deleted (cancelled). Payroll (M56) pays the line with the rest of the approved run, unchanged. |
| 7 | `fix.compensation.cycle` (FR-PIC-038, BRU-PIC-17) | Name, the window raises take effect in, monthly increase budget, guideline %, guidelines; approved, pending and remaining increases measured from its proposals. | Set up, opened and closed by the Compensation Manager; budget required; one open cycle per company over any date; window and budget fixed once open; it closes only when no proposal awaits a decision. **A proposal whose raise takes effect in the window belongs to the cycle.** **A proposal that would take the approved increases over the budget is routed to the CFO, and only the CFO approves it**; without a cycle the old path applies unchanged. |

Security and data:
- ACLs: plain users read KPI definitions, their own feedback requests and their own adjustments only; HR Managers maintain cycles, feedback requests and KPI definitions; calibrators and HR run sessions; Incentive Officers raise adjustments (nobody deletes one); the Compensation Manager maintains cycles; the CFO reads cycles and may now decide an over-budget proposal (new read/write row and the proposal privacy rule names the CFO).
- Privacy rules: feedback (respondent, line manager, HR), adjustments (own and direct reports, HR and payroll).
- Company and operating-unit isolation rules from `generate-isolation-rules.py`; only the cd_performance file was kept, the generator's drift in four other modules was reverted.
- Sequences FBK/, CAL/, IAD/ and the daily chase job.
- The review and feedback models gained the activity mixin (the chase and the request to-dos need it).
- Load order: the new file extends models from every other M57 file, so it is imported last (`# ruff: noqa: I001` tuple form).

### Workspace: `m57.js`, `controllers/a09/m57.py`, `writable.py`

- Seven new lists, on their pages and in the navigation: KPI Definitions, Review Cycle Set-Up, Multi-Source Feedback, Calibration Sessions, Incentive Schemes, Incentive Adjustments, Compensation Review Cycles.
- Mislabelled lists renamed to what they show: "KPI Definitions" (scorecards) → Technician Scorecards; "Incentive Schemes" (runs) → Calculation Runs; "Calculation Runs" (lines) → Payout Lines; "Compensation Review" (bands) → Salary Bands.
- Six new tabbed forms (AGENTS.md): KPI Definition, Review Cycle, Feedback Request, Calibration Session (with a rating-change grid), Incentive Adjustment, Compensation Review Cycle. The scorecard form gained a KPI Attainment tab; the review form shows its cycle and feedback count/average; the proposal form its cycle and whether it is over budget; the payout line its adjustment.
- The "Incentive Scheme" chip now opens the scheme; the run has its own "Incentive Run" chip.
- `writable.py` regenerated with `form_fields.py --a09`; only the six new entries were added.

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Goals & KPIs | Goal | Goal, **KPI Definition**, **Technician Scorecard** |
| 2 Review Cycles | **Review Cycle** | **Review Cycle**, Review, **PIP** |
| 3 Multi-Source Feedback | **Feedback Request** (was a review) | **Feedback Request** |
| 4 Rating & Calibration | **Calibration Session** (was none) | **Calibration Session** |
| 5 Incentive Design & Calculation | **Incentive Scheme** (was none) | **Incentive Scheme** (was a run), **Scheme Version**, **Incentive Run**, **Incentive Adjustment** |
| 6 Recognition | Spot Recognition | Recognition |
| 7 Compensation Review | **Compensation Review Cycle** | **Compensation Cycle**, **Salary Band**, **Succession Plan** |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m57_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry; it also checks every list column and form field against the model, every action against the surface, the whitelist against the forms, and that no stamp or measured figure is writable. | **HEAD c5feece6: 18 of 37 fail.** After: **37/37.** |
| Estate page standard `test_estate_module_pages.py` (all 67 modules). | **605/605.** |
| Live tests `cd_performance/tests/test_m57_capture_live.py`, run as freshly created non-admin users (Incentive Officers, an Incentive Approver, two HR Managers, a Calibrator, a Compensation Manager, a CFO, a line manager, a technician, a peer, a plain user) on a private clone `fix_test_m57` (`-u all`, 166 modules, exit 0, no error). Adjustments, calibrations and proposals are decided through the real M63 inbox. | **23/23.** The first run caught four real defects, fixed before the result above: the review and feedback models had no activity mixin (the chase and the request to-do failed), the approver could not stamp an approved adjustment, and the CFO could neither see nor decide an over-budget proposal. |
| Mutation check: each rule removed in turn (KPI approver differs from preparer, no backdated replacement, approval closes the old version, volume needs quality, approved KPI frozen, direction; cycle raises only managed employees, cycle terms frozen, cycle closes only when reviews close; respondent only, respondent not the subject, answer final; all ratings calibrated first, concluder not involved, review not closed during an open session, changes only in session; approved period locked, fraud evidence, never below zero, not own pay, employee told, applied by the computation; over-budget goes to the CFO, cycle budget frozen, one open cycle). | **25 of 25 mutations turned the live tests red**; the source was restored byte for byte. |
| Regression on the same clone: every `cd_performance` and `cd_payroll_bd` test, the A09 permission matrix, talent controls, the portal's A09 control suite, P0 people controls, write whitelist, M21 report labels, estate guard, A03 registry coverage and the M57 guard. | **1,414 tests: 1,412 passed, 2 failed.** The two failures (`test_the_relay_delivers_recognition_awarded`, `test_the_relay_delivers_hse_compensation_awarded`) **fail identically with the HEAD c5feece6 code on the same database** (both run, both fail): the event-outbox relay to payroll, not touched here (the M51 audit recorded the same A09 relay class). |
| Workspace UI on a private server (port 8099) over the clone, signed in as admin. | Page 1 shows the Goal, KPI Definition and Technician Scorecard chips; a KPI definition was **saved from the tabbed form** (Draft; kind, unit, direction and fact source filled by the server). Page 3 shows "+ New Feedback Request" (was "+ New 360 Review") and opens the tabbed form. Page 4 shows "+ New Calibration Session" (was nothing). Page 5 shows "+ New Incentive Scheme" with Scheme, Scheme Version, Incentive Run and Incentive Adjustment chips (was no "+ New"). Page 7 shows "+ New Compensation Review Cycle" with Compensation Cycle, Salary Band and Succession Plan chips (was none). No server error beyond the clone's missing filestore, fixed by copying `fix_test`'s. |
| After rebasing onto the shared tip a520b717 (M51, M55, M56 and M58 had landed): `form_fields.py --a09`. | `writable.py` regenerated byte-identical to the merged file. Guards: M57 37/37, estate 605/605, M51 33/33, M55 38/38, M58 48/48. Clone re-upgraded with the peers' changed modules (`-u cd_tax_engine_bd,cd_attendance,cd_payroll_bd,cd_talent,cd_performance,cd_p03_portal`, exit 0); `cd_performance` + `cd_payroll_bd` + A09 portal suites: **723 tests, the same 2 relay failures, nothing new.** |

## 4. Not built here (owner decisions or other modules)

- **What the incentive rewards** (spec §16.3, BRU-PIC-04/05 on pay): the composite score has no volume component and no quality gate; it is the weighted FTF/SLA/CSAT/salvage/rework formula, and the only scheme version on fix_real is still draft and "as coded, unsourced". The KPI definitions now record targets and thresholds and show breaches, but they deliberately do not change pay: the components, weights, gates and caps are a COO / HR Director / CFO decision, then a new scheme version for them to approve.
- **Goal library and cascade by department** (FR-PIC-001/002), **mid-period goal revision** (FR-PIC-005), **scheme simulation** (FR-PIC-037, AUT-PIC-15), **KPI dispute on a scorecard value** (FR-PIC-014; disputes exist on the incentive line), **peer comparison** (FR-PIC-015), **development actions to M22** (FR-PIC-025, AUT-PIC-13), **internal equity analysis** (FR-PIC-039): reports or integrations, not captures.
- **Approval of automatic clawbacks** (BRU-PIC-11 "approval … before it is applied"): rework and credit clawbacks are still raised and recovered by the computation without a separate approval; a fraud or invalid-job reversal is now the approved, evidenced adjustment above. Putting the automatic ones behind an approval changes how every run recovers them: an owner decision.
- **Workshop, front-desk and contact-centre scorecards** (FR-PIC-009/010/011): KPI definitions can be held for those role profiles, but only the field-technician scorecard is computed.
- **CFO group**: the CFO is the existing "Incentive Scheme Approver: CFO" group (2 holders on fix_real), used for BRU-PIC-17 too.
- **Data**: fix_real has no active employment contract, scorecard, review or approved scheme version, so none of the new flows has anything to act on until HR takes on contracts and the owners approve a scheme. No KPI definition, cycle or budget exists yet: these are a data take-on for HR and the Compensation Manager.

## 5. State

**Deployed on fix_real (8069) and fix_dev (8090), 18 Nov 2026 ~20:28 UTC, on the user's "land and deploy".** Not pushed.

- **Landed** on `fix/a03-live-data-and-pending-work`: fix 3c4baf80, report 2019e83e, by compare-and-swap with the shared checkout synced.
  - Before landing it was rebased twice: over M58 biodata/M01 (c67680a0), then over M21 (c7f2d59b).
  - `controllers/a09/writable.py` was regenerated with `form_fields.py --a09` after each rebase, and came out byte-identical.
  - Guards on the rebased tree: M57 37/37, M21 32/32, M58 51/51, M01 27/27, estate pages 605/605.
- **Backups:** `1000 fix/backups/fix_real_pre_m57_capture_2026-11-18.dump` (header checked: dbname fix_real) and `fix_dev_pre_m57_capture_2026-11-18.dump`.
- **Upgrades**, both exit 0 with no ERROR/CRITICAL:
  - fix_real: `-u cd_performance,cd_p03_portal`, run after the M21 session's fix_real `-u cd_hr_core,cd_p03_portal` had exited.
  - fix_dev: `-u cd_performance,cd_p03_portal,cd_hr_core,cd_talent`, which also brought the M21 and M58 modules level on fix_dev.
  - The version gap against the shared checkout was 0 on both databases just before the restart.
- **One restart of each server**, coordinated with the M21 and M58 sessions:
  - 8069: PID 82916 -> 49668. 8090: PID 3304 -> 26328.
  - Both answer `/web/login` 200, with no ERROR/CRITICAL since the restart.
  - The M21 session verified its screens on the same restart.
- **Post-deploy check on both databases**, run with `odoo-bin shell`:
  - all six new models are in the registry and in `p03_generic_api.SURFACES`;
  - `_cron_chase_overdue()` runs (rolled back);
  - workspace bundle `e846a36` carries all six M57 forms and the KPI definitions screen;
  - 8069 serves that bundle with a 200.
- **Chase cron first-run failure (not a defect):** the upgrade created the cron, and the *old* server process fired it at once with `KeyError: 'fix.performance.review.cycle'`. That process's registry did not know the model yet. It happened once on each database before the restart. The next run, due 19 Nov, runs on the restarted process.
- **Known cosmetic warning:** two fields on `fix.performance.review.cycle` (`review_count`, `review_ids`) share the label "Reviews". It is harmless and left for a later pass.
- **Commercial-document change landed after the restart:** the change (29e907b8) landed at 20:30 UTC, after this restart. The servers therefore run 2019e83e, which matches both databases. The commercial-document session owns its own upgrade and restart.
