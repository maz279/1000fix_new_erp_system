# A09 ERP Audit — R3 · M55 Time, Attendance & Scheduling (+ leave arithmetic from cd_hr_core)

Auditor: R3 · Date: 2026-11-22 · Code at shared HEAD `6f0d6a54` (worktree `a09erp-wt`)
Scope per brief: `addons/domain/h_people/cd_attendance` (all), `fix_leave_controls.py` + leave models in `cd_hr_core`, P03 surfaces `controllers/a09/m55.py` + `static/src/a09/m55.js`, cross-area consumers in `a_service_delivery` (cd_service_order technician API, cd_field_service), payroll hand-off in `cd_payroll_bd`.

Probe scripts and raw outputs: `C:\Users\DELL\AppData\Local\Temp\a09erp\R3\` (`probe1_static_real.py(.out.txt)`, `probe2_arithmetic_testdb.py(.out.txt)`, `probe3_sod_testdb.py(.out.txt)`, test logs).

Severity scale: P0 money/legal/security broken · P1 core flow broken or bypassable · P2 rule/calc/report wrong · P3 polish.

---

## 1. Findings table

| id | severity | category | finding | evidence | proposed fix | files a fixer would touch |
|---|---|---|---|---|---|---|
| M55-F1 | P1 | L | Production readiness: on `fix_real_a09` there are **0 `fix.employment.contract` rows and 0 employees with a joining date**, so `_fix_service_start()` is False for all 504 employees → annual leave accrues 0 days for everyone (s.117), maternity eligibility check can never pass ("joined on no recorded date"), payroll population excludes everyone. First real payroll/leave is blocked by master data, not by M55 logic (contract master is M21's). | `fix_leave_controls.py:646-658` (`_fix_service_start`), `fix_payroll.py` `_payroll_population`; probe1 `counts["fix.employment.contract"]=0`, `with_joining=0` | Load contracts (or at minimum joining dates) for the 504 employees before first leave request / payroll run; M21 owns the fix, M55/M56 blocked by it | `cd_hr_core` data load (M21) |
| M55-F2 | P1 | J/E | Statutory currency: Labour (Amendment) Act 2026 (passed ~2026-04-10; 93 sections amended) raised **maternity 112→120 days (60 before + 60 after)** and **festival holidays 11→13**. Live types on `fix_real_a09` are maternity 112 and festival 11, and the code floor `STATUTORY_LEAVE` says 112/11; the split check uses `entitlement_days // 2` (would become 60/60 automatically if entitlement updated). | `fix_hr_core.py:13-20`; probe1 leave_types (maternity 112, festival 11); Global Law Experts + Legal 500 alerts (2026), see §7 adviser questions | After counsel confirms the enacted text: update the two seeded leave types and `STATUTORY_LEAVE` floors (120, 13); re-run `action_validate_statutory` | `cd_hr_core/models/fix_hr_core.py`, `cd_hr_core/data/statutory_leave_data.xml`, live data |
| M55-F3 | P1 | F | Holiday/rest-day/callout work is never paid as such: `rest_day_hours` and `holiday_hours` are computed and stored, but **payroll (`cd_payroll_bd`) never reads them** — no 2-days'-wages / substitute-holiday logic for festival-holiday work (BLA s.118 as amended: two compensatory holidays with full pay + substitute), and weekly-holiday work is only paid if it happens to be covered by an approved OT request (all rest-day hours count as "recorded OT", cap 10 h). Verified on-call **callouts** (`fix.oncall.callout`, manager-verified hours) are likewise never valued — only the standby `approved_allowance` reaches payroll. No compensatory-holiday balance exists anywhere (FR-WFM-025 missing). | `fix_attendance.py:619-625` (valuation), `cd_payroll_bd/models/fix_payroll.py` grep: no `holiday_hours`/`rest_day_hours`/`callout` read; probe2 scenario K | Decide policy: (a) pay holiday work at 2× with a substitute-leave record, or (b) record compensatory holidays and block their lapse; value callouts (fee or OT); read the figures in `_slip_plan`/`PayslipInput`; add a compensatory-leave type with balance | `cd_payroll_bd/models/fix_payroll.py`, `cd_attendance/models/fix_attendance.py`, new compensatory logic |
| M55-F4 | P1 | F | Approved unpaid leave has no effect on pay: no "unpaid" leave type exists in the catalogue, and payroll deducts absence days only through the retro `fix.attendance.adjustment` path (re-opened paid periods). A month with days of unpaid absence (once such a type is added) would still pay the full month — the salary plan prorates only by join/left dates. | grep: no "unpaid" in cd_hr_core/cd_attendance; `fix_payroll.py:620-700` (`_payroll_population` proration only by contract dates), `_retro_figures` absence only via adjustments; [STATIC] | Add the unpaid/bereavement/compensatory/special types (FR-WFM-026); make `_slip_plan` subtract approved unpaid-leave days of the period from `paid_days` (or produce a deduction line) | `cd_hr_core` seeds, `cd_payroll_bd/models/fix_payroll.py` |
| M55-F5 | P1 | G | `availability.changed` (spec §12.3; AUT-WFM-09 "update availability projection within 60 s; notify dispatch") is not published and **no availability projection exists** (T-10/FR-WFM-046 "per employee per interval"): M02 discovers leave/roster state only at assignment time, and neither dispatch path checks the **shift window against the job time** (a 22:00–06:00 night slot satisfies a 14:00 work-order assignment). The two M02 dispatch paths also disagree: `fix.work.order.action_check_technician_availability` **hard-blocks** assignment with no roster slot, while `cd_field_service.fix.field.order._fix_unavailable_on` treats a missing slot as "not proof" (only approved leave rules a technician out) — a night-shift or unrostered technician can be dispatched via field orders. | `fix_attendance.py:1630-1718` vs `cd_field_service/models/fix_field_order.py:765-806`; no `/api/v1/availability` route anywhere | Publish `availability.changed` on leave approve/cancel + roster publish/change; align the two dispatch checks (field order should call the same roster/night-consent check or consume the same helper); check slot start/end against the job window; M02 side owns the field-order half | `cd_attendance/models/fix_attendance.py`, `fix_leave_controls.py`, `cd_field_service/models/fix_field_order.py` |
| M55-F6 | P2 | A/G | 9 of the 11 spec §12.3 events are not published (only `leave.approved`/`leave.cancelled` match by name): missing `attendance.recorded`, `attendance.exception_raised`, `attendance.period_locked`, `overtime.approved`, `overtime.limit_breached`, `availability.changed`, `roster.published`, `capacity.gap_detected`, `leave.balance_updated`. The 8 events the code does publish (`attendance.approved/rejected/checked_out/locked/unlocked/availability.verified` + the two leave ones) are all registered in `contracts/events`, so the registry and the code agree with each other and both disagree with the spec. Consumers M25/M27/M04/M60 get no push. | grep publish( in cd_attendance + fix_leave_controls; `contracts/events/` listing | Publish the missing events (or amend the spec — the direct reads cover M56/M02 today) | `cd_attendance/models/*.py`, `cd_hr_core/models/fix_leave_controls.py`, `contracts/events/` |
| M55-F7 | P2 | G | AUT-WFM-04 device health monitoring is not built: no cron watches `fix.biometric.device.last_sync_at`/status, so a dead terminal is silent (no alert within 1 h, no branch fallback). AUT-WFM-06 exception ageing/escalation before payroll cut-off also missing (the routing cron routes pending records but nothing ages or escalates them; AUT-WFM-13 "block lock until exceptions cleared" holds via the pending check). AUT-WFM-12 leave-lapse notifications missing. | `data/fix_a09_attendance_data.xml` (only 2 M55 crons + accrual in cd_hr_core); probe1 crons list; `fix_attendance.py:1202-1218` | Add `fix.biometric.device` health cron (1 h, alert supervisors + set status offline) and an exception-ageing escalation (3 days before cut-off) wired to the existing cron | `cd_attendance/models/fix_biometric_intake.py`, `fix_attendance.py`, data XML |
| M55-F8 | P2 | H | Report/KPI day boundary is process-local, not user-TZ: `controllers/a09/m55.py` uses `datetime.date.today()` for `attendance_today`, default report ranges and KPI periods — correct only while the Odoo process runs Asia/Dhaka; the dev/test recipe runs UTC, in which the "today" filter is wrong by 6 h (18:00–24:00 Dhaka lands on the next day). Also `attendance_summary` counts "days" as records, so a split shift shows 2 days; `overtime_analysis` totals omit the `days` column. | `controllers/a09/m55.py:146-153,432-441` [STATIC] | Use a user/server-TZ-aware today (as the ORM code does with `fields.Date.context_today`); count distinct employee-days; add the totals key | `cd_p03_portal/controllers/a09/m55.py` |
| M55-F9 | P2 | A | Exception detection is limited to working-time labels: FR-WFM-011's missing punch, late arrival, early departure, absent-without-leave and impossible-travel are not detected as exceptions (no shift-vs-actual comparison beyond the roster-vs-actual pack's "Gap" day count); FR-WFM-016 fraud signals (repeated identical timings, geofence-spoof indicators, device sharing) and the "Attendance integrity" report are missing; FR-WFM-014 bulk regularisation missing (a branch-wide device failure must be regularised record by record). | spec §5.2; `compliance_status` selection `fix_attendance.py:493-507`; no matching code (grep) | Add end-of-day exception detection (roster shift window vs punches), a periodic fraud-pattern scan + integrity pack, and a bulk regularisation action with one documented reason | `cd_attendance/models/fix_attendance*.py`, controller pack |
| M55-F10 | P2 | A | FR-WFM-024 overtime budget/cost reporting and FR-WFM-031 balance *projection* (future-dated) are missing: `overtime_analysis` reports hours only (no cost, no budget), leave balances are as-of only (projection = the `until` trick in `_fix_annual_leave_available`, not surfaced). Leave-liability report (accrued unused value feeding the M56 provision) missing. | `controllers/a09/m55.py:209-236,371-419` [STATIC] | Extend the overtime pack with `overtime_amount`-priced cost (contract basic+DA+adhoc) and add a leave-liability pack (unused days × daily rate) | `cd_p03_portal/controllers/a09/m55.py` |
| M55-F11 | P2 | E | On `fix_real_a09` the Attendance **Lock Manager group has 1 holder (admin only)** and `hr_attendance.group_hr_attendance_user` — the officer fallback that decides regularisations, overtime requests, callouts and timesheets when no line manager exists — has **0 holders**; 235 of 504 employees have no manager recorded, so their flagged clock-ins and OT requests route to nobody until the M63 escalation fires (still the same empty group). Leave's fallback group (HR Officer) is also admin-only. Attendance Supervisors (20 holders) read everything but are not in the officer approver group. | probe1 groups (lock_manager 1 = admin; hr_attendance_user 0; hr_officer 1 = admin); `with_manager=269`; `fix_attendance.py:55-56` APPROVER_GROUP | Appoint real holders (Nov report §7.1 decision); consider making the Attendance Supervisor group imply the hr_attendance officer group or adding supervisors to the routing fallback | live data (roles) / `cd_attendance/security/fix_a09_groups.xml` |
| M55-F12 | P2 | L | Data quality on `fix_real_a09`: `sex` = 'unspecified' for **all 504** employees (SQL), so the s.109 night-work control never triggers and maternity is refused for everyone ("recorded as unspecified" — on top of F1's missing service start); `overtime_eligible` defaults True for all 504 (incl. managers); holiday calendar has 12 rows for 2026 but **0 typed "festival"** (the 11 statutory festival days are not distinguishable); two demo companies (My Company (Chicago), My US Company) still carry working-time rule versions. | probe1 + SQL `select sex, count(*)` (unspecified 504); `overtime_eligible_true=504`; `holidays_by_year` festival 0 | Populate sex, review OT eligibility, type the festival rows (or seed from the s.118 list), prune demo companies | live data |
| M55-F13 | P2 | C | Weekly limit decision still open: live rule v1 = **60 h weekly** (label) with s.101 interval, s.105 spread-over and the s.102 56 h annual average all **0 = not checked** and all modes "label". What the rule does TODAY: 10 h/2 h-OT caps enforced on requests and roster; 60 h/week flagged only; no rest-interval, spread-over or annual-average check. | probe1 working_time_rules; `fix_working_time.py:36-51` DEFAULTS | Owner decision (below): set 48 h + 56 h average + s.101/s.105 figures and modes; effective-dated new version (T-07 flow exists) | live data via M55-wt-rules screen |
| M55-F14 | P2 | C | Roster publication notice (`fix_roster_notice_days`) and dispatch-published-only (`fix_roster_dispatch_published_only`) both ship off/0 on `fix_real_a09`; coverage threshold 0% (BRU-WFM-04 flag never fires); annual-leave basis 'service'. All are the §7.4 pending decisions — measured live, none has been ruled. | probe1 company_settings | Owner decisions (below) | live data |
| M55-F15 | P3 | B/D | Leave entitlement accounting is by `date_from` calendar year: a leave spanning a year boundary (Dec 28–Jan 3) charges all its days to the starting year and none to the next, so days falling in the new year consume no new-year entitlement (a small leak across years for casual/sick/paternity). | `fix_leave_controls.py:346-362,519-525` [STATIC] | Charge each day of the span to its own calendar year | `cd_hr_core/models/fix_leave_controls.py` |
| M55-F16 | P3 | B | `fix.work.order` extension in cd_attendance re-declares `operating_unit_id`, already defined by `cd_service_order/models/fix_work_order.py:66` — duplicate field declaration across areas (harmless merge, but A09 should not re-declare M02's field). | `fix_attendance.py:1628` vs `cd_service_order/models/fix_work_order.py:66` | Drop the duplicate field (rely on M02's) | `cd_attendance/models/fix_attendance.py` |
| M55-F17 | P3 | H | `leave_balances` pack iterates every visible employee computing the s.117 ledger per employee (N+1 searches over leave requests × service years) — on 504 employees this exceeds the T-12 ≤500 ms projection envelope; also no company filter (record rules only). | `controllers/a09/m55.py:371-419` [STATIC] | Batch: read all approved leaves once, group in memory | `cd_p03_portal/controllers/a09/m55.py` |
| M55-F18 | P3 | A | Spec §12.4 REST surface (`/api/v1/attendance/*`, `/api/v1/leave/*`, `/api/v1/roster/*`, `/api/v1/availability`, `/api/v1/capacity/forecast`) is not implemented as such; only `/hooks/v1/biometric/<device>` and the A02 technician API exist; P03 covers the rest through the generic model API. Functional impact low (P03 is the UI), but the M02/M27 "one call" availability contract is absent. | grep for `api/v1/` routes [STATIC] | Implement the availability endpoint or amend the contract | `cd_attendance/controllers/` |
| M55-F19 | P3 | K | Form 10 (BLR r.102) overtime register is exported as rows from a workspace action, not as a formatted statutory document (no PDF/letterhead render path for it in P03). | `fix_attendance.py:1521-1614`; m55.js action `action_export_form10_overtime_register` | Render the register through the report-export standard (pdf) | `cd_p03_portal` report pack |
| M55-F20 | P3 | D | `fix.leave.type.verified_on` still defaults to `fields.Date.today` in the base model (`fix_hr_core.py:1451`); the override in `fix_leave_controls.py:91` sets default=False for new records, but any create path that bypasses the controls class (none found today) would re-introduce the auto-verified defect. [STATIC] | `fix_hr_core.py:1451-1455` | Move the default=False into the base definition | `cd_hr_core/models/fix_hr_core.py` |
| M55-F21 | P2 | E | The default 'service' basis for the s.117 accrual over-counts days of work: it credits every calendar day of service less exactly one weekly holiday in seven (`days - days//7`) — festival holidays (11–13/yr) and paid/unpaid leave days count as "days of work performed", so an employee on leave all year still earns ~17 annual-leave days a year. The stricter 'attendance' basis exists but is off, and there is no attendance data yet anyway. | `fix_leave_controls.py:660-670` (`_fix_leave_days_worked` 'service' branch) | Either subtract leave days and festival holidays from the service basis, or switch the company to the 'attendance' basis once capture is live (decision) | `cd_hr_core/models/fix_leave_controls.py` |
| M55-F22 | P3 | C | A leave spanning out of a locked month is refused outright (e.g. Jan 28–Feb 5 once January is locked) instead of being split; and `_fix_check_maternity` reads "six months' service before confinement" as total service ≥ 6 months, not service "immediately preceding" delivery. | `fix_attendance_approval.py:555-574`; `fix_leave_controls.py:375-381` [STATIC] | Allow the future part of a span; align the maternity service test once counsel rules (§6) | `cd_attendance/models/fix_attendance_approval.py`, `cd_hr_core/models/fix_leave_controls.py` |
| M55-F23 | P2 | C | No weekly payable-OT cap: payable OT is capped per day (2 h; 10 h rest day) but nothing caps the *week* — 7 × 2 h = 14 h payable OT = 48+14 = 62 h paid, above the s.102 60 h weekly ceiling with overtime (12 h), while the weekly flag (`weekly_ot_limit_exceeded`) is label-only and unread by payroll. | `fix_attendance.py:601-626` (`_fix_value_day` daily caps only), `_compute_weekly_totals` label; probe2 scenario I | Cap payable OT per employee-week at `weekly_limit − 48` during valuation (needs the F13 ruling to be meaningful at 60) | `cd_attendance/models/fix_attendance.py` |

Historic items re-checked (3–6 Nov §7 Update 4, capture audit, 30 Oct):
- **OT divisor 240/basic-only (30 Oct)** — FIXED: `libs/py/payroll_engine/__init__.py:95-96` `OT_DIVISOR_HOURS=208`, `OT_BASE_COMPONENTS=(basic,dearness,ad_hoc)`, `overtime_amount` = base/208×2×h; M55 Form 10 and `_overtime_value` use the same kernel. Verified with numbers in probe2 scenario J.
- **Overlap/clean-up list (fix_dev)** — on `fix_real_a09` there are **0 attendance records and 0 leave requests**, so the overlapping attendance/leave pairs and September OT-without-attendance cases do not exist in production data; nothing to clean.
- **Capture-button audit M55 (17 Nov)** — 26 of 38 guard tests failed then; today `test_m55_capture_buttons.py` = **38 passed** (baseline below). Callouts, capacity forecast, timesheet, leave-type catalogue all captured.
- **`unused_leave_days` no setter (3 Nov §7)** — resolved: M56's `unused_leave_days()` delegates to M55's `_fix_unused_annual_leave_days` (s.117 ledger), used by exit settlement and payslip encashment (basic/30 × days). No typed figure remains.

---

## 2. Spec-coverage matrix (A)

| Requirement family (M55 spec) | Verdict | Notes |
|---|---|---|
| FR-WFM-001..010 capture (biometric, GPS, geofence, identity, derived, web/kiosk, manual, offline, multi-punch, source) | **PARTIAL** | Biometric webhook + replay log, technician geofenced clock-in (A02 API), manual with reason, multi-punch per-day valuation, source recorded (F5/F7 crons fine). Web/kiosk screen = P03 list (no kiosk mode); FR-WFM-005 derived-from-M02-job-events not found (attendance from job events not implemented — the technician API clock_in is the only M02 link) |
| FR-WFM-011..016 exceptions & regularisation | **PARTIAL** | detection limited to compliance_status labels (missing punch / AWOL / impossible travel not detected); routed regularisation solid; bulk (F9) and ageing (F7) missing; fraud signals missing |
| FR-WFM-017..025 working time & OT | **PARTIAL** | versioned rules T-07/T-08 excellent; s.100/108 caps enforced (probe2 A–H); pre-approval enforced; retrospective→HR; caps per day and rest day; weekly 48/60 label-only (F13); s.101/s.105/56 h average not ruled (0); OT budget (F10) and compensatory off (F3) missing |
| FR-WFM-026..036 leave | **PARTIAL** | types/entitlement/accrual/balance/overlap/certificate/holiday-exclusion/cancel built and probed; maternity statutory checks built; missing: unpaid/bereavement/compensatory/special types (F4), coverage threshold off (F14), projection UI (F10), recall-from-leave (cancel covers it), calendar screen is a list |
| FR-WFM-037..045 holidays, shifts, rosters | **BUILT (mostly)** | moon-dependent tentative flag + recompute on confirm; branch calendars via company rows (branch-specific variations not per-branch); shift templates; roster draft→publication→change control with notice setting; on-call with callouts; templates-by-season = shift templates (ok) |
| FR-WFM-046..052 availability, capacity, payroll interface | **PARTIAL** | availability = on-assignment check, not a published projection (F5/F18); skill-based availability = capacity forecast skill filter (BUILT); period verify+lock gate BUILT (payroll re-checks); post-lock forward adjustments BUILT (I8) |
| AUT-WFM-01..16 | **PARTIAL** | 01,02,03(via technician API),05,08,10(notices),11(accrual cron),13(pending check),14(lock),16(leaver consumer) built; 04,06,07(label only),09(no push),12,15(alert on publish only) missing/partial |
| Data entities §10.1 (20 owned) | **PARTIAL** | 17 of 20 exist with different names (no fix.attendance.exception, fix.time.valuation table — valuation is computed fields, no fix.availability projection table); punch events + consents + adjustments + baselines added beyond spec |
| KPIs §15 (KPI-223..234) | **PARTIAL** | 8 KPIs surfaced; no completeness %, disputes, notice-compliance, breach, manual-share, availability-accuracy, enrolment-coverage, response-time metrics |
| Reports §14 (12 packs) | **PARTIAL** | 6 packs built and ORM-consistent (F8 caveats); missing: absence analysis, statutory breaches, leave liability, on-call utilisation, roster publication compliance, integrity |
| Roles §13 | **BUILT** | groups + record rules + SoD as spec'd; SOD-27/28 enforced; holder gap F11 |
| BRU-WFM-01..15 | **BUILT except** | BRU-WFM-04 (setting 0, off), BRU-WFM-05 weekly 48 (60 live, label), BRU-WFM-12 notice 0; the rest enforced in code and tests |
| PDPA T-01/T-02 | **BUILT** | consent gate, hashed device credential, template→Z4 routing, alternative capture methods |

Counts: BUILT 4 families, PARTIAL 10, MISSING 0 families wholly (individual FRs missing listed above).

Nav/UI conformance (B/H): `contracts/nav/registry.json` carries the 13 canonical M55 screens; the fragment serves all 13 plus 13 operational screens added by the audits (webhook log, regularisation decisions, rule versions, adjustments, leave types, publication approvals, change requests, callouts, capacity, timesheets, lock, accrual, calendar), 6 report packs (spec-era 5 + Coverage Gaps) and 17 D365 multi-tab forms. All list `cols` exist on their models (verified field-by-field against the models, incl. `approved_by` on fix.attendance.record and `basis` on fix.leave.accrual); guarded/stamped fields render readonly in every form; the generic `/report/export` path serves csv/xlsx/pdf for the packs and logs downloads. Registry names and fragment ids agree.

---

## 3. Settings register (measured on `fix_real_a09`)

| key / field | live value | code default | effect today |
|---|---|---|---|
| res.company.fix_roster_notice_days | 0 | 0 | no minimum publication notice (FR-WFM-041 off) |
| res.company.fix_roster_dispatch_published_only | False | False | dispatch accepts any slot (draft counts) |
| res.company.fix_annual_leave_basis | 'service' | 'service' | s.117 counts service days less 1-in-7 (attendance basis unused — no attendance data yet) |
| res.company.fix_leave_coverage_max_pct | 0.0 | 0.0 | BRU-WFM-04 coverage check off |
| res.company.fix_leave_coverage_mode | 'flag' | 'flag' | (moot while pct=0) |
| fix.working.time.rule v1 (all 3 companies) | daily_max 10, ot_cap 2, weekly 60, min_rest 11 (label); s.101/s.105/annual-avg 0, all modes 'label' | same | caps enforced on OT requests + roster; weekly flagged at >60; no interval/spread/average checks |
| ir.config_parameter fix.attendance.max_accuracy_m | (unset) | 100.0 m | mobile clock-in accuracy limit 100 m (A02 reads it) |
| ir.config_parameter cd_performance.incentive_requires_attendance_lock | '1' | — | M57 gate reads the M55 lock (cross-area, working) |
| crons | route-pending (hourly), route-adjustments (hourly), accrue-annual-leave (daily) — all `__system__` tz Asia/Dhaka, state code | — | operative |

---

## 4. Measured facts on `fix_real_a09` (L)

- employees 504; with user 310; with manager 269; with department 504; with joining_date 0; overtime_eligible True ×504; sex = 'unspecified' ×504 (SQL).
- contracts 0; attendance records 0; leave requests 0; roster slots/publications 0; oncall 0; OT requests 0; locks 0; devices 0; consents 0; punch events 0; adjustments 0; timesheets 0; capacity forecasts 0; night consents 0; accrual rows 0; payroll periods 0.
- shift templates 5 (Morning 9–17, Day 10–18, Evening 14–22, Night 22–6, Split 9–13 [4 h]); Night covers 22:00–06:00.
- holidays: 12 rows in 2026, 1 tentative, 0 of type 'festival'.
- leave types 6 (annual 20/CF40/encash, casual 10, sick 14+cert, festival 11, maternity 112, paternity 10 policy).
- groups: attendance_supervisor 20 holders; lock_manager 1 (admin); hr_attendance officer 0; hr manager 5; hr officer (cd_hr_core) 1 (admin); payroll officer 0; payroll manager 3.
- working-time rule versions: 3 (one per company incl. 2 demo companies).
- all 504 employees have a branch; 149 sit in a branch with a dispatch zone; **0 active fix.geofence rows** → every mobile clock-in would evaluate `no_geofence` and be born pending until geofences exist (A02/M02 data).
- 0 work orders / 0 field orders on the snapshot (M02 flows not yet live in production data).

Before the first real payroll: contracts/joining dates (F1), sex + OT eligibility (F12), festival-typed holidays, roster slots for dispatchable technicians (or M02 assignments hard-block), biometric devices + consents, lock-manager and officer role holders (F11), weekly-limit/notice/coverage rulings (F13/F14).

---

## 5. Cross-area section

| link | state | which side is wrong |
|---|---|---|
| M56 payroll ← lock/OT/oncall/adjustments | working: verify+calculate re-check lock & pending; OT = sum of M55 payable OT on approved/not_required records (probe2 V: equal); oncall = approved_allowance of completed shifts in period; adjustments consumed once per slip (I8) | none (money path proven) |
| M56 payroll ← holiday/rest-day/night/unpaid | reads nothing (F3/F4) | M55 must define the categories and M56 read them — joint, M55 first |
| M02 work order ← roster/leave/night-consent | blocking check on assignment; requires a slot (any state unless published-only switch) | working as designed; but see F5 divergence |
| M02 field order ← leave/on_leave | leave blocks; missing roster slot does NOT block (score only) | M02 field-order side diverges from the work-order path (F5) |
| M02 technician API → M55 records | geofence evaluation server-side, flagged not refused; ir.config_parameter max_accuracy_m consumed | OK (A02-owned, M55-consumed) |
| M27 ← roster notices | per-employee SMS/e-mail via fix.notif.delivery with dedup key; chatter+activity fallback | OK |
| M22 ← capacity forecast skill filter | valid certification on the day | OK |
| M63 approvals | people mixin, manager-first, conflict checks; DOFA ladder absent (role group decides) | as ruled in Nov report §7 |
| M30 branches/zones | employee.branch_id.zone_id drives geofences; zone coverage of employees not yet measured (no branch data probed — with_department 504 only) | data |
| crons | 3 M55 crons + M63 engine cron exist, run as Asia/Dhaka system user | OK |
| events | 8 published and registered; 9 of the 11 spec events missing (F6) | M55 |

---

## 6. Owner decisions (recommendation) and adviser questions

1. **Weekly hours 48 vs 60** (BRU-WFM-05 vs s.102): recommend a new rule version from a future date with weekly_limit 48 (label) and annual_avg 56 h (label), s.101 interval (e.g. 5 h → 30 min… needs ruling) and s.105 spread-over 12 h, all 'label' until discipline settles. — A09 §7.4 open.
2. **Pay beyond the daily/weekly cap**: today an OT request cannot exceed 2 h/day (10 h rest day), so excess recorded hours are never payable; recommend keeping that and routing genuine exceptions as HR-approved forward adjustments — confirm.
3. **Holiday work pay** (F3): decide 2× pay + substitute day vs compensatory balance per s.118; recommend compensatory-leave type + 2× only for festival days, weekly rest day = substitute or OT at 2×.
4. **Maternity 120 / festival 13** (2026 amendment): adviser to confirm enacted figures (see questions), then update seeds (F2).
5. **Notice days / published-only dispatch / coverage threshold**: recommend notice 7 days, published-only ON once rosters exist, coverage 30% flag.
6. **Appoint Lock Manager and attendance officers** (F11) and payroll officer (M56) — roles decision.
7. **Unpaid leave policy** (F4): whether unpaid absence is deducted in-period (recommend yes, via paid_days) and the missing leave types (bereavement, compensatory, special).

Adviser questions:
- Confirm the Labour (Amendment) Act 2026 exact figures: maternity 120 days (60+60)? festival holidays 13? any change to s.100/102/108/109 figures or the OT base (basic+DA+ad-hoc)?
- Confirm the s.118 obligation for festival-holiday work (two extra compensatory holidays + substitute) and s.103 weekly-holiday compensation for commercial establishments (1½-day week; compensatory holiday with wages).
- Confirm whether s.46(1) service condition post-2018/2026 is "six months immediately preceding delivery" (code) or "9 months in the 12 preceding".

---

## 7. Arithmetic and access evidence (probe2/probe3 on `fix_test_a09_r3`, all rolled back)

Worked-time / OT valuation (`fix.attendance.record`, live ORM):
- 8 h day, no request → worked 8, recorded 0, payable 0, compliant.
- 10 h day + approved 2 h → worked 10, recorded 2, payable 2.
- 12 h day + approved 2 h → recorded 4, **payable capped at 2** (s.100/108), unapproved 2, compliance `daily_limit_exceeded` (label).
- 10 h day, no request → recorded 2, payable 0 (BRU-WFM-02 holds).
- Split shift 9–13 + 14–19 (9 h) + approved 1 h → the second row carries cum 9 → recorded 1, payable 1 (per-employee-day valuation keeps split-shift OT).
- Rest day 9–19 marked rest-day + 10 h request → worked 10, recorded 10, **payable 10** (cap = daily_max 10), rest_day_hours 10.
- Non-eligible employee (`overtime_eligible=False`): the request itself is refused ("not overtime-eligible, BLA s.2(65)/s.108"); 10 h day pays 0 OT.
- Request above cap (3 h) → refused ("at most 2 h of overtime a day").
- OT money (kernel): 26,000 basic → 2 h = **500.00** (26,000/208×2×2); with DA 4,000 → 576.92; with +ad-hoc 1,000 → 596.15; 20,000 basic, 10 h rest-day = 1,923.08. Divisor 208 and 2× confirmed live.
- Holiday work (confirmed holiday row): holiday_hours = 8 stored, payable 0 — nothing paid (F3).
- Roster: woman on a 22:00–06:00 slot without consent → refused (BLA s.109); with an active consent → created. Day+Night on one day (16 h) → refused (s.100 roster cap).
- TZ: webhook punch "2026-06-15T09:00:00+06:00" stored as 03:00 UTC (offset honoured; naive input = UTC by convention).

Leave arithmetic (live ORM):
- s.117 accrual, joiner 2024-06-01, 'service' basis: year 1 = 313 worked → 17 days; year 2 → 17; unused 34 (cap 40) — 1-day-per-18 confirmed.
- Casual 6 approved then 5 more → refused ("6 approved + 5 requested > 10 days in 2026").
- Sick without certificate → refused; holiday inside span (5-day span over 1 confirmed holiday) → days 4.
- Leave over a day with attendance → refused ("a day is either worked or on leave").
- Maternity: 112-day span (56 before / 56 from confinement) APPROVED; ≥2 surviving children → refused; short service → refused; man → refused; span split violations → refused.
- Balance survives cancel (only approved leave counts).

Payroll hand-off (money path, live ORM):
- `fix.payroll.period._payable_overtime_hours(emp)` for May-2026 = **15.0 h == sum of M55 `overtime_hours`** on approved/not_required records (equal: True).
- `_oncall_allowance` reads the **approved_allowance** (1,500 of a completed on-call), not the requested one.
- `pending_in_period` returns the flagged clock-ins (0 after decisions).
- Locked-period edit/create/unlock, payroll gate and forward-adjustment consumption are covered by the module's own tests (below) and were reviewed in code (I8 `_fix_consume` refuses non-approved, cross-employee, cross-company and non-later-period consumption).

Access/SoD as real non-superusers (fresh `Environment` per call, cold cache):
- worker writes own record's hours → allowed but record stays `pending` (re-decided);
- worker writes/creates a colleague's record → **AccessError** (own/direct-report record rule);
- worker calls approve on own pending attendance, own OT, own leave → **refused, "not awaiting your decision"** (routed to the line manager/officers);
- worker creates a lock → **AccessError** (ACL: supervisors only);
- Attendance Supervisor gives biometric consent for another employee → **AccessError** (employee's or HR's only); the employee's own Give → allowed;
- roster: planner (supervisor) submits; planner approving own submission → refused; a different supervisor approves → published;
- read scope: worker sees 1 record (own), supervisor sees all 3.

---

## 8. Test baseline (private DB fix_test_a09_r3)

- `cd_p03_portal/tests/test_m55_capture_buttons.py`: **38 passed, 0 failed, 0 skipped** (6.01 s).
- `cd_attendance` full suite (5 files, 99 tests): final counts below (run under heavy shared-machine load; two earlier partial runs reached 38 tests with 0 failures).
- SUITE RESULT: see `cd_att_final.log` tail appended below.
