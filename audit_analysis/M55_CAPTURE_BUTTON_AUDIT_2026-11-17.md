# M55 Time, Attendance & Workforce Scheduling: Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M55 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M55_Time_Attendance_and_Workforce_Scheduling.md`:
  §3 scope (15 capabilities), §5 FR-WFM-001 … 052, §8 lifecycles (attendance record, leave request, roster), §9 BRU-WFM-01 … 15, §10.1 the 20 owned entities.
- Code:
  - `cd_p03_portal/static/src/a09/m55.js`: the page registry (9 sub-module pages, 25 screens);
  - `cd_p03_portal/controllers/a09/m55.py`: surfaces, reports and KPIs;
  - `cd_attendance/models/*.py` and `cd_hr_core` leave models.
- Live data (fix_real, read-only count on 17 Nov): 6 leave types, 12 holidays, 5 shift patterns, 3 working-time rule versions, 504 employees, 73 branches; **no** attendance record, leave request, roster slot, on-call, overtime request or lock. Two users hold an attendance role.

## 1. What was there (HEAD c5feece6)

Evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Capture (4 modes) | Attendance record | Exception Regularisation, Biometric Consent | Biometric devices listed with **no chip** although the form existed; the consent list and the device webhook log were on no page. |
| 2 | Working Time & OT | **Attendance record** (page 1's record) | Overtime Request, Night-Work Consent, Working-Time Rule | The page's own record is the **overtime pre-approval** (BRU-WFM-02, P0); its list, the night-work consents and the rule versions were on **no page**, so the chips opened forms whose records you could not see on the page. |
| 3 | Leave | Leave Request | Leave Request | **No leave type** (FR-WFM-026: annual, casual, sick, maternity… with their rules) on the M55 page; the s.117 accrual list was on no page. |
| 4 | Holidays | Holiday | **none** | No chip. |
| 5 | Shifts & Rosters | Roster slot | Roster, Shift Pattern, Roster Change Request | The roster change requests were on no page. |
| 6 | On-Call | On-Call | **none** | No chip, and **no callout record** (FR-WFM-044 "on-call rota with allowance **and callout recording**"): a callout could not be recorded or verified anywhere. |
| 7 | Availability Publication | **Roster slot** (page 5's record) | Roster Publication, Roster Change Request | The page's own act is **publishing** the roster; the publication list was on no page. **No capacity forecast** (FR-WFM-048/049, P1): capacity by branch and skill against demand could not be forecast and no gap could be alerted. |
| 8 | Verification & Lock | Attendance Lock | Exception Regularisation | The regularisation decisions and the forward adjustments to payroll were on no page. |
| 9 | Timesheets | **Attendance record** (page 1's record) | Exception Regularisation | **No timesheet line** (FR-WFM-050): time could not be allocated to a project, a contract or a cost centre. |

Nine working lists sat on no page at all: biometric consent, webhook events, regularisation decisions, overtime requests, night-work consent, working-time rule versions, forward adjustments, leave accrual, roster publications and roster change requests.

Guard `cd_p03_portal/tests/test_m55_capture_buttons.py` on HEAD: **26 of 38 tests fail.**

## 2. What was built

### Backend: `cd_attendance` 19.0.0.2.0, new file `models/fix_wfm_capture.py`

Every decision is taken by someone other than the person it is about and the person who recorded it (M63 routed approval, line manager first). Stamps and measured figures are guarded fields, never typed. A locked attendance period is closed to all three records (BRU-WFM-10).

| Page | Record | Holds | Rules |
|---|---|---|---|
| 6 | `fix.oncall.callout` (FR-WFM-044) | The on-call it came in on, called at, arrived, finished, caller or channel, work order, what was done; hours computed; reference CALL/. | Recorded only on an on-call that was **started** (active or completed), and only **inside its window**; no two callouts of one on-call overlap. Recorded by the person on call, their manager or an attendance role (a colleague cannot: the global record rule refuses it). Submit routes it to the **line manager** (attendance officers when there is none); the person on call and the recorder never verify it. Rejection needs a reason. Verified callouts are final; terms change only in draft. |
| 7 | `fix.capacity.forecast` (FR-WFM-048/049) | Branch, optional skill (M22 competency), period (≤ 93 days), forecast demand hours and its basis. **Measured** from the roster: rostered hours, hours on approved leave, available hours, people, gap and gap %; reference CAP/. | Measured, never typed. With a skill, only people holding a **valid certification** of it on the day count. Maintained and published by attendance supervisors (others read). Publishing freezes the figures, **supersedes** the previous published forecast of the same branch, skill and overlapping period, and when demand exceeds capacity posts the gap and gives **every attendance supervisor a to-do** (FR-WFM-049). |
| 9 | `fix.timesheet.line` (FR-WFM-050) | Employee, date, hours, work done; allocated to an M67 **project**, an M05 **contract**, a **work order** or a **cost centre** (at least one); the day's verified attendance shown beside it. | The lines of a day **never exceed the verified attendance** of that day (biometric/mobile rows and approved manual entries), and a day with none takes no line. With no project, contract or work order, an empty cost centre is filled with the employee's own. Recorded by the employee, their manager or an attendance role (the global record rule). The **line manager approves**; the employee never approves their own. Terms change only in draft. |

Security and data:
- ACLs: callouts and timesheet lines are self-service like overtime requests (read/write/create for internal users, narrowed by global own-and-direct-reports rules; attendance roles see all); capacity forecasts are read by everyone and maintained by supervisors. **Nobody deletes** any of the three.
- Company and operating-unit rules from `generate-isolation-rules.py` (only the cd_attendance file kept; the generator's pre-existing drift in four other modules was reverted).
- Two sequences (CALL/, CAP/).
- Manifest now declares `cd_competency`, `cd_ppm` and `cd_msp_contract` (FF-46: the new records reference skills, projects and contracts). All three are installed on fix_real, fix_dev and fix_test; none of them depends on cd_attendance, so there is no cycle.

### Workspace: `m55.js`, `controllers/a09/m55.py`, `writable.py`

| Page | "+ New" after | Chips after | Lists added to the page |
|---|---|---|---|
| 1 Capture | Attendance record | Exception Regularisation, **Biometric Device**, Biometric Consent | Biometric Consent, Device Webhook Events |
| 2 Working Time & OT | **Overtime Request** (was attendance record) | Overtime Request, Night-Work Consent, Working-Time Rule | Overtime Requests, Night-Work Consent, Working-Time Rule Versions |
| 3 Leave | Leave Request | Leave Request, **Leave Type** | Annual Leave Accrual, **Leave Types** |
| 4 Holidays | Holiday | **Holiday** | — |
| 5 Shifts & Rosters | Roster slot | Roster, Shift Pattern, Roster Change Request | Roster Change Requests |
| 6 On-Call | On-Call | **On-Call / Standby**, **On-Call Callout** | **On-Call Callouts** |
| 7 Availability Publication | **Roster Publication** (was roster slot) | Roster Publication, **Capacity Forecast**, Roster Change Request | Roster Publication Approval, **Capacity Forecast**, Roster Change Requests |
| 8 Verification & Lock | Attendance Lock | Exception Regularisation | Regularisation Decisions, Forward Adjustments |
| 9 Timesheets | **Timesheet Line** (was attendance record) | **Timesheet Line**, Exception Regularisation | **Timesheets** |

- Four new lists (callouts, capacity forecasts, timesheets, leave types) with their actions, and four new tabbed forms (callout, capacity forecast, timesheet line, and an M55 leave-type form carrying carry-forward, certificate, maternity, holiday-charging and citation fields that the M21 form did not show).
- `writable.py` regenerated with `form_fields.py --a09`; only M55 entries changed.

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m55_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. | **HEAD c5feece6: 26 of 38 fail.** After: **38/38**, with the estate page standard for all 67 modules (643 tests, 0 failures). |
| Live tests `cd_attendance/tests/test_m55_capture_live.py`, run as freshly created non-admin users (technician, colleague, line manager, attendance officer, supervisor) on a private clone `fix_test_m55` (`-u all`, exit 0). Decisions go through the real M63 inbox; one test drives the `/p03/model/write` endpoint. | **7/7.** |
| Mutation check: each rule removed in turn (callout window, started on-call, no overlap, terms frozen after draft, locked period, measured figures guarded, skill filter, leave taken out, supersede, gap alert, allocation required, attendance required, allocation ≤ attendance, recorder check, cost-centre default). | **14 of 15 mutations turned the tests red;** the source was restored byte for byte. The survivor was the timesheet "who may record" check in code, which repeated the global record rule exactly; it was removed, so the rule is the single gate (as for overtime requests), and the tests now assert the rule's own refusal. |
| Regression on the same clone: every test of `cd_attendance`, `cd_hr_core`, `cd_payroll_bd` and `cd_field_service`, plus the portal's A09 control suite, people P0 controls, A09 write whitelist, M21 report labels, estate pages, KPI tiles, tell-me registry and the M55 guard. | **1,720 tests: 6 failures, 1 skipped.** The six (leaver closes future roster, leaver access revoked, mover/role-change access review, HSE and recognition awards relayed to payroll) all wait on the event relay delivering to a consumer. **They fail identically on the unchanged code** (run on a detached c5feece6 worktree against the same database), so they are pre-existing and not caused by this change. |
| Workspace UI on a private server (port 8099) signed in to the clone. | Page 2 shows "+ New Overtime Request" with Overtime Requests, Night-Work Consent and Working-Time Rule Versions; page 6 "+ New On-Call / Standby Assignment" with the On-Call Callout chip and list; page 7 "+ New Roster Publication" with the Capacity Forecast chip and list; page 9 "+ New Timesheet Line". A timesheet line was saved from the tabbed form (row 137, Draft, cost centre CC-WORKSHOP). The server log's only error was an unrelated finance job on the clone (`fix.ar.aging.snapshot` has no `_cron_monthly_snapshot`). |
| Lint | ruff 0.8.4 (the pinned pre-commit version): format and check clean on every changed Python file. |
| Generators | `generate-isolation-rules.py`: only the cd_attendance file kept (pre-existing drift in cd_workshop, cd_inventory, cd_competency and cd_rbac_ext reverted). `form_fields.py --a09`: only M55 entries changed. |

## 4. Not built here (owner decisions or other modules)

- **Biometric enrolment / template reference** (`fix.biometric.enrolment`, T-01/T-02): consent is captured (BRU-WFM-08); the template itself is S3 residency data routed through the identity vault, not M55.
- **Exception as its own record** (`fix.attendance.exception`): exceptions are carried on the attendance record (approval state and reason) and decided through the routed regularisation, which covers FR-WFM-011…013. Bulk regularisation (FR-WFM-014, P2), exception ageing before cut-off (FR-WFM-015) and fraud signals (FR-WFM-016, P2) are follow-ups.
- **Branch-specific holiday calendars** (FR-WFM-038, P2): the calendar is per company; a branch scope changes how leave days and valuation are computed, so it needs the owner's rule on which branches differ.
- **Compensatory time off** (FR-WFM-025, P2), **roster templates** (FR-WFM-045, P2), **leave recall** (FR-WFM-036, P2).
- **Committed hours in the capacity forecast**: the spec's `committed_hours` (work already booked by M02) is not measured; the forecast compares demand with available hours. Zone (spec `zone_id`) is not modelled on branches.
- **Callout pay**: verified callout hours are recorded; how M56 pays them (rate, minimum callout) is a payroll policy decision.
- **Data**: fix_real holds no attendance, roster, on-call or leave transactions, so the new lists start empty.

## 5. State

- Fix commit **b5699893** on the working branch `fix/a03-live-data-and-pending-work`. Built in worktree `m55cap-wt`, rebased onto 42d00bb2 (M51 capture work, no overlapping files), guard, estate and A09 whitelist re-run after the rebase (645 tests, 0 failures), then landed by compare-and-swap. The shared checkout was synced and is clean. **Not pushed.**
- **Deployed on fix_real (8069) on 17 Nov 2026, together with M51** (the user chose the combined deploy, because a restart loads every committed module and M51's held change alters the cash-receipt NID check):
  1. Backup `_migration/backups/fix_real_pre_m55_capture_2026-11-17.dump` (49.9 MB, 51,203 archive entries).
  2. `-u cd_attendance,cd_tax_engine_bd,cd_billing_engine,cd_p03_portal`: exit 0, no ERROR lines. Version-gap check afterwards: 83 installed cd_ modules, 0 differ from the code.
  3. The M51, M21 and M58 sessions confirmed they were holding their own 8069 work. 8069 restarted: PID 78988 became 28840 (same supervisor 23964); 155 modules loaded, no ERROR since, login answers 200.
- Verified on fix_real:
  - the three M55 models exist with 8 access rows, 8 record rules and both sequences (CALL/, CAP/);
  - the served workspace bundle `03f2536` carries the four new forms, and pages 2, 7 and 9 point at overtime request, roster publication and timesheet line.
  - M51 side: its three new models, the `nid_cash_threshold` parameter (50,000) and its notice cron are present.
- fix_real holds no callout, forecast or timesheet rows yet (0/0/0), and no attendance or roster transactions, so the new lists start empty.
- **fix_dev (8090) updated on 18 Nov 2026** (user: "Update fix_dev too"), with the same combined M55 + M51 upgrade:
  1. Backup `fix_dev_pre_m55_capture_2026-11-17.dump` (45.4 MB, 51,016 archive entries).
  2. Upgrade exit 0, no ERROR lines; gap check: 80 installed cd_ modules, 0 differ.
  3. 8090 restarted at tip 76241745: PID 66868 became 28660 (supervisor 37700), login 200, no errors since.
  - The rebuilt workspace bundle is identical in size to fix_real's and carries the four M55 forms and the page 2/7/9 mappings.
  - The M51 objects and the NID threshold (50,000) are present.
  - The restart was done before the M58 session landed its cd_talent change, so 8090 matches 76241745 exactly; fix_dev will lag M58 until it is upgraded there.
- The private clone `fix_test_m55` and the launch entry `odoo-m55-test` (port 8099) are kept for follow-up work.
