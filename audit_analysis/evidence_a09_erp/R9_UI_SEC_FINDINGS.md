# A09 ERP Audit — R9 (Workspace, Security & Reporting) — 2026-11-22

Scope: P03 surfaces, KPIs, reports, exports, navigation fidelity and security for all seven A09
modules (M21, M22, M55–M59). Worktree `a09erp-wt` @ `6f0d6a54`. Probes on `fix_real_a09`
(read-only, every script ends `env.cr.rollback()`); probe outputs in
`C:\Users\DELL\AppData\Local\Temp\a09erp\R9\out\` (probe1–4.json), scripts in `...\R9\probes\`,
logs in `...\R9\logs\`. No code, git or database state was changed. The private HTTP server on
8791 was NOT restarted this session (remaining checks were done through the ORM); it is not
running.

Code roots (all paths relative to `...\a09erp-wt\1000_fix_codebase`):
fragments `addons/platform/cd_p03_portal/static/src/a09/m*.js`; controllers
`addons/platform/cd_p03_portal/controllers/a09/m*.py`, `writable.py`, `__init__.py`; engine
`addons/platform/cd_p03_portal/static/src/p03_workspace.js` (+ `.xml`), `controllers/p03_generic_api.py`,
`controllers/form_fields.py`; registry `contracts/nav/registry.json`.

---

## 1. Findings

Severity: P0 money/legal/security broken; P1 core flow broken or bypassable; P2 rule/calc/report
wrong; P3 polish.

| id | severity | module/model | finding | evidence | proposed fix | files a fixer would touch |
|---|---|---|---|---|---|---|
| UI-F1 | P2 | M56 `fix.payroll.gratuity.accrual` | Nav screen **M56-gratuity ("Gratuity & Encashment") is wired to the `pf_gratuity` pack** (PF contributions per payslip); the real `gratuity_provision` pack (FR-PAY-022 monthly register) is reachable only via the report chip `M56-rpt-gratuity`. The Gratuity screen shows PF rows under a gratuity title. | `static/src/a09/m56.js:115` vs `controllers/a09/m56.py:343-498` (two distinct packs); probe2 rows (both packs serve) | Point `M56-gratuity` at `gratuity_provision`; keep `pf_gratuity` on M56-pf / its chip | m56.js |
| UI-F2 | P2 | M55 `fix.leave.request` + engine | **Fiscal window fed to a calendar-year pack**: `reportTarget` sends every period-enabled table_report `date_from/date_to = gl.stmtFrom/stmtTo`, initialised by `_glFyWindow()` to the BD fiscal July–June window (today 2026-07-01→2027-06-30). `leave_balances` takes `as_of = date_to` and `year = as_of.year` → the Balances screen labels "Annual Taken **2027**", counts leave starting in calendar 2027 and computes unused balances **as at a future date** (2027-06-30). | engine `static/src/p03_workspace.js:1108-1114, 1252-1258, 1280-1282`; `controllers/a09/m55.py:374-399` (verified from source; no leave rows on the snapshot to diff) | Clamp `as_of` to today in `leave_balances` and derive the year from today (or a pack-declared basis); decide once whether HR packs get the fiscal or calendar window and encode it on the screen config | controllers/a09/m55.py; p03_workspace.js (screen config `period:` semantics) |
| UI-F3 | P2 | M22/M56/M57/M58/M59 packs | **24 of 44 report packs ignore the period the screen offers** (M22 all 6; M56 salary_register, payroll_cost_allocation, tax_deduction_summary, pf_gratuity; M57 all 5; M58 all except day_one_readiness; M59 all 5). The date pickers change nothing; exports carry the same unfiltered rows. | controllers source: m22.py:137-459, m56.py:202-380, m57.py:143-332, m58.py:156-380, m59.py:157-390 (no date_from/date_to in any search); probe2 `period_probe`: identical titles/rows for Jan-2026 params | Apply `date_from/date_to` filters on the natural date field of each pack (issued_on, period_start, awarded_on, hired_on, accident_date…) | controllers/a09/{m22,m56,m57,m58,m59}.py |
| UI-F4 | P2 | M57 `fix.performance.review` | The review screen offers **"Recall Calibration" with no "Request Calibration"**: `action_request_calibration` is whitelisted (m57.py SURFACES) and implemented (`cd_performance/models/fix_performance_ops.py:424`) but appears on **no** P03 screen, so a calibration request can never be raised from the workspace — a dead-end control. | `static/src/a09/m57.js:77-84` (button list: recall, no request); `controllers/a09/m57.py:22-33`; action_audit.py output | Add `{ m: 'action_request_calibration', l: 'Request Calibration', states: [...] }` to the M57-reviews actions | m57.js |
| UI-F5 | P2 | M21 ESS/MSS | **M21-ess ("ESS / MSS", registry type d = dashboard) renders the `probation_conversion` pack** titled "ESS / MSS — Probation Conversions Due". The M21 spec (§5 area 9) promises an employee/manager **self-service hub**; its records (leave request, master change, notice acks, rights requests) sit scattered on other screens, and the dashboard is one narrow list. | `static/src/a09/m21.js:201`; spec `1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M21_...md` §5 row 9 | Build the ESS/MSS dashboard (my leave/balances, my changes, my documents, team actions for managers) or retitle the screen to its real content | m21.js (+ new pack in controllers/a09/m21.py) |
| UI-F6 | P3 | registry ↔ fragments | **Navigation fidelity drift**: registry.json (canonical nav universe) is stale vs the fragments — 108 nav screens exist only in fragments (M21 17, M22 12, M55 15, M56 21, M57 11, M58 16, M59 16); module `bn` titles differ on 5 modules (M55–M59); 8 screen titles differ (M57-kpis/reviews/calibration/schemes/calc/comp; M59-jsa/ppe); 25 screens' type chip `t` differs; registry form "Interview Evaluation" has no chip (fragment renamed it "Interview Round"). `freg.src`/`freg.sub` match on all 7 modules; all 80 registry screens exist in fragments with correct groups. | inventory.py output (`out/inventory.json`); registry generator `tooling/generators/generate-nav-registry.py` not re-run | Re-run the registry generator from the current fragments (or add the drift check to CI) so registry == nav universe again | contracts/nav/registry.json (generated) |
| UI-F7 | P3 | i18n bn_BD | **Bengali UI shows English on A09 forms**: bn_BD PO files are 100% translated (1489/1489 entries, POT fully covered), but the form engine serves the fragment's English label first (`spec.label or m["string"]`, p03_generic_api.py:1131) and the client dictionary `P03_BN` covers none of them — 2073/2224 field labels, 379 section titles and 103 report/KPI labels have no Bengali rendering. Nav screen titles are bilingual (fragment `bn`). | `static/src/p03_i18n.js` (1501 entries, 0 A09 form labels); probes/bn_dict_coverage.py; po_coverage.py | Either declare `bn` on fragment fields/sections (like tabs already do) or make `_form_field_meta` prefer the translated model string when lang=bn_BD and no explicit bn label exists | p03_generic_api.py `_form_field_meta`; fragments m21–m59.js |
| UI-F8 | P3 | M22/M55/M56/M57/M59 packs+KPIs | **Server-timezone date bugs**: controllers use `datetime.date.today()` / naive `datetime.now()` (m22.py:133, m55.py:148/242/302/374/433, m56.py:540, m57.py:349, m59.py:208/244-248) instead of the caller's Dhaka day (m21.py does it right with `fields.Date.context_today`); with server TZ=UTC every "today/MTD/YTD" edge is 6 h off each evening. m55 `attendance_summary`/KPIs compare **UTC-stored datetimes with local wall-clock strings** (m55.py:151-153, 434-438), so the attendance day window is shifted 6 h. [STATIC — 0 attendance rows on the snapshot to demonstrate live] | controller sources cited | Use `fields.Date.context_today(env.user)`/`_datetime_to_utc` boundaries as m21.py and identity_access_log do | controllers/a09/{m22,m55,m56,m57,m59}.py |
| UI-F9 | P3 | M55 KPIs | `holidays` is served but shown on no tile (dead payload, m55.py:444-463 vs fragment KPI list); `roster_coverage` = share of today's slots **not on leave** (m55.py:456-460) while the roster_vs_actual report computes real punch coverage — the tile overstates coverage. | m55.py kpis; frag_static.txt KPI table | Show `holidays` or drop it; define roster_coverage against punches (or rename) | m55.py; m55.js |
| UI-F10 | P3 | M21 `fix.hr.identity.access.log` | **display_name never resolves**: the model has no `name`/`_rec_name` (`cd_hr_core/models/fix_hr_identity_residency.py:625-631`), so all 5321 rows render "fix.hr.identity.access.log,<id>" wherever display_name is used (write responses, lookups). The report pack formats fields directly and is clean. | probe1.json `display_name_failures: {fix.hr.identity.access.log: [200,200]}` | Add `_rec_name` (e.g. a computed `display_name` from user/field/read_at) | cd_hr_core/models/fix_hr_identity_residency.py |
| UI-F11 | P3 | M56/M57/M22 KPI semantics | KPI labels promise more than the metric: M56 `tax_deduction_summary` title hardcodes "AY 2026-27" regardless of period (m56.py:320); M57 `reviews_on_track` = % **closed** (m57.py:358), `calibration_sessions` counts calibrated **reviews** not sessions (m57.py:361), `incentive_accuracy` = % runs approved (m57.py:365); M56 `run_duration` serves a payslip count (label "Payslips"); M22 `training_hours` divides OJT hours by a 'tech'-in-position-name heuristic with `or 1` (m22.py:498-504), inconsistent with M21's fixed dispatch-group technician count. | controller sources; frag_static.txt | Relabel or recompute each to what it measures | controllers/a09/{m56,m57,m22}.py + fragments |
| UI-F12 | P3 | M21 identity log pack | The Identity Read Log pack silently **caps at 2000 rows** (m21.py:655, `limit=2000`; 5321 exist) and titles itself "2000 reads" as if that were the total — the report standard's "N of TOTAL" honesty rule is not applied to pack row caps. | probe2: rows=2000 with 5321 in table | Title "first 2000 of 5321" or paginate | controllers/a09/m21.py |
| SEC-F1 | P2 | `/p03/model/action` (all A09) | **Action whitelist vs UI drift**: `fix.performance.review.action_request_calibration` and `fix.hse.incident.action_notify_dife` are whitelisted on surfaces where **no screen offers them** — the API accepts calls the UI never makes (wider than designed). The endpoint enforces only the SURFACES set, never the fragment `states:` precondition; state gating rests entirely on each model method (NOT CHECKED end-to-end this round — the control suite run by the lead asserts workflow-field guarding on writes). | action_audit.py output; p03_generic_api.py:1571-1605 | Trim the two dead whitelist entries; add server-side state precondition checks to the actions that rely on UI-only `states:` | controllers/a09/{m57,m59}.py |
| SEC-F2 | — (verified good) | all A09 | **No security hole found at master level** (measured, fix_real_a09, fresh-env personas): ACLs cover 194/194 A09-area models (the 8 without a row are abstract/tableless mixins); no `base.group_user` write/create/unlink on payslip, candidate, band, succession or health models (26 base-writable models are all self-service-by-design with record rules); company rules exist on every `company_id` model except `fix.hse.incident.child` (child of incident, isolated via parent); identity values (NID/TIN/passport/bank) are field-group protected — a plain employee's `fields_get`/`read` of `nid_number` raises AccessError; 13 personas × 154 models: payroll models refused for non-payroll, candidates refused outside talent, bands refused outside HR/performance, health refused outside occupational health; A09 surfaces all read as the caller (`rules: True`, a09/__init__.py:29). | probe1.json, probe3.json | — | — |
| SEC-F3 | P3 | `fix.compensation.band`, `fix.hse.permit`; SoD | `fix.compensation.band` is readable by `hr.group_hr_user` (any line manager reads salary bands — cd_performance/security/ir.model.access.csv); `fix.hse.permit` grants create to `base.group_user` (any employee can raise a work permit). 16 of 32 A09 groups hold exactly **one** user (SoD fragility). | probe1 acl_detail + group_holders | Owner decision: restrict band read to Compensation/HR; confirm permit self-service intent; appoint second holders | cd_performance/security/ir.model.access.csv; cd_hse/security/ir.model.access.csv |
| SEC-F4 | P3 | `/p03/model/write` child grids | Child-grid writes check only that the **parent's one2many field** is in the parent whitelist (p03_generic_api.py:1393-1398); the child row's field values face only the child model's own readonly/guarded locks — a per-child-field whitelist does not exist. Guarded child fields are protected solely by `fix.guarded.mixin` (covered by the control suite run by the lead); a targeted forgery probe was NOT CHECKED this round (no server). | p03_generic_api.py:1393-1398, 1451-1457 | Add the child-grid fields to the generated whitelist (form_fields.py already parses grids) and filter row_vals against them | controllers/form_fields.py, p03_generic_api.py |

Items explicitly **NOT CHECKED** this round (machine economy): HTTP-level session/login checks and
the sweep tools on port 8791 (server not restarted); action state-precondition forgery at HTTP
level; guard-token forgery; XLSX/PDF letterhead bytes of every export (the builders
`report_bytes`/`report_delivery` are shared with the estate standard and were read, not
exercised); existing test suites (run by the lead).

---

## 2. Inventory table — registry vs fragment vs controller (per module)

Registry A09 totals confirmed: **80 screens / 35 reports / 28 forms / 42 KPIs**
(`counts` cross-check by module: 6 KPIs each). Fragment "nav" = MODULE.groups; "defs" = SCREENS
export; ctrl = controllers/a09.

| module | registry screens | fragment nav screens | registry reports | fragment REPORT_ROUTES / controller packs | registry forms | fragment chips | registry KPIs | fragment tiles / controller keys | match verdict |
|---|---|---|---|---|---|---|---|---|---|
| M21 | 12 | 29 (+17 extra, 2 extra groups) | 5 | 8 / 8 | 4 | 22 | 6 | 8 / 8 | all 12 registry screens present, titles en+bn equal, groups equal, freg 70/70 equal; extras = drift (UI-F6) |
| M22 | 11 | 23 (+12) | 4 | 6 / 6 | 3 | 15 | 6 | 6 / 6 | registry ⊆ fragment; en/bn equal; freg 52/52 |
| M55 | 13 | 28 (+15) | 4 | 6 / 6 | 3 | 16 | 6 | 8 / 9 (`holidays` unserved to UI) | titles equal; module bn differs (UI-F6); freg 74/74 |
| M56 | 12 | 33 (+21) | 4 | 7 / 7 | 3 | 18 | 6 | 6 / 6 | titles equal; module bn differs; freg 82/82 |
| M57 | 10 | 21 (+11) | 4 | 5 / 5 | 3 | 13 | 6 | 6 / 6 | **6 screen titles differ** (UI-F6); module bn differs; freg 58/58 |
| M58 | 10 | 26 (+16) | 4 | 7 / 7 | 3 | 13 (registry "Interview Evaluation" → renamed "Interview Round") | 6 | 6 / 6 | title drift + form rename (UI-F6); freg 50/50 |
| M59 | 12 | 28 (+16) | 4 | 5 / 5 | 3 | 15 | 6 | 6 / 6 | **2 screen titles differ**; module bn differs; freg 60/60 |

- Every registry screen id exists in the fragment nav AND has a SCREENS definition (no nav screen
  without a def; no missing screens).
- Every fragment report chip routes to a controller pack; every registry report name has a route.
- `contracts/nav/registry.json` generator (`tooling/generators/generate-nav-registry.py`) exists;
  idempotence NOT CHECKED (registry is provably stale vs fragments — regenerating would change it).
- Breadcrumb: `openScreen` titles a non-nav screen from its data-screen config, not the first
  screen (D14 fix verified in engine, p03_workspace.js:5364-5372).
- `writable.py` regeneration is a **no-op** (render == checked-in file, byte-identical); 157/157
  A09 surfaces whitelisted; 25 surfaces empty-by-design (read-only screens, e.g. `fix.payslip`
  with `create:false`).
- Multi-tab rule: **0 violations** (every model_form with ≥15 fields has tabs; tab strip is ARIA
  `role="tablist"/tab/tabpanel` with `aria-selected`, roving `tabindex`, bn labels —
  p03_workspace.xml:3668-3690).
- Cols: **0 dropped columns and 0 unknown form fields** across all A09 screens
  (probe1 `screens_with_dropped_cols_or_fields = {}`).
- Actions: every fragment list action is in SURFACES; 2 dead whitelist entries (SEC-F1).

## 3. KPI reconciliation table (47 served keys; registry promises 42)

Method: served values from the controllers' `kpis(env)` as an all-groups user (probe2) vs my own
independent ORM formulas (probe4) on fix_real_a09. Snapshot is master-data-only (see §6), so most
figures are 0 — formulas still reconciled on the non-zero ones.

| module.key | label (tile) | served | independent | verdict |
|---|---|---|---|---|
| M21.headcount | Headcount | 504 | 504 | MATCH |
| M21.attrition_ytd | Attrition YTD % | 0.0 | 0.0 | MATCH (0 exits) |
| M21.technicians | Technicians | 141 | 141 (dispatch group) | MATCH |
| M21.open_positions | Open Positions | 0 | 0 | MATCH — but 61 positions carry no sanctioned headcount (readiness) |
| M21.probation_ending_30d | Probation Ending (30d) | 0 | 0 | MATCH (0 probation contracts) |
| M21.service_books_complete | Service Books | 0 | 0 | MATCH (1 document, unverified) |
| M21.privacy_notice_pending | Privacy Notice Pending | 504 | 504 employees unacknowledged | MATCH (withheld for callers without read) |
| M21.probation_unreviewed_30d | Probation Unreviewed (30d) | 0 | 0 | MATCH |
| M22.certified_technicians | Certified Technicians | 0 | 0 | MATCH (0 certs) |
| M22.expiring_30d | Expiring (30d) | 0 | 0 | MATCH |
| M22.expired_working | Expired Working | 0 | 0 | MATCH |
| M22.training_hours | OJT Hours /tech | 0.0 | 0 total OJT hours | MATCH — denominator heuristic flagged (UI-F11) |
| M22.brand_certifications | Brand Certifications | 0 | 0 | MATCH |
| M22.assessment_pass_rate | Assessment Pass Rate % | 0.0 | 0.0 | MATCH |
| M55.attendance_today | Attendance Today | 0 | 0 (UTC and Dhaka day) | MATCH — boundary bug [STATIC] (UI-F8) |
| M55.exceptions_pending | Exceptions Pending | 0 | 0 | MATCH |
| M55.overtime_preapproved | OT Requests Approved (month) | 0 | 0 | MATCH |
| M55.roster_coverage | Roster Coverage % | 0.0 | 0.0 | MATCH — semantics flagged (UI-F9) |
| M55.leave_pending | Leave Pending | 0 | 0 | MATCH |
| M55.geofence_clockins | Geofence Clock-Ins | 0 | 0 | MATCH |
| M55.rosters_awaiting | Rosters Awaiting Publication | 0 | 0 | MATCH |
| M55.adjustments_open | Adjustments Awaiting Approval | 0 | 0 | MATCH |
| (M55.holidays — served, no tile) | — | 12 | 12 | dead payload (UI-F9) |
| M56.payroll_cycle | Payroll Cycle | — | no periods | MATCH (honest —) |
| M56.gross_payroll | Gross Payroll ৳ | 0 | 0 | MATCH (0 slips) |
| M56.run_duration | Payslips | 0 | 0 | MATCH (label/UI-F11) |
| M56.corrections | Corrections | 0 | 0 | MATCH |
| M56.tax_withheld_mtd | Tax Withheld MTD ৳ | 0 | 0 | MATCH |
| M56.festival_bonus_accrued | Bonus Accrued ৳ | 0 | 0 | MATCH |
| M57.reviews_on_track | Reviews On Track % | 0.0 | 0.0 | MATCH (semantics UI-F11) |
| M57.incentive_pool_mtd | Incentive Pool MTD ৳ | 0 | 0 | MATCH |
| M57.goal_coverage | Goal Coverage % | 0.0 | 0/504 | MATCH — denominator includes all 504 active (leaver-free snapshot) |
| M57.calibration_sessions | Calibration Sessions | 0 | 0 (0 sessions, 0 calibrated reviews) | MATCH (semantics UI-F11) |
| M57.pips_active | PIPs Active | 0 | 0 | MATCH |
| M57.incentive_accuracy | Incentive Accuracy % | 0.0 | 0/0 runs | MATCH |
| M58.open_requisitions | Open Requisitions | 0 | 0 | MATCH |
| M58.time_to_fill | Time-to-Fill (days) | null → "—" | null | MATCH (honest no-activity state) |
| M58.pipeline | Pipeline | 0 | 0 | MATCH |
| M58.offer_accept_rate | Offer Accept Rate % | 0.0 | 0.0 | MATCH |
| M58.referral_share | Referral Share % | 0.0 | 0/0 | MATCH |
| M58.first90_retention | First-90 Retention % | 0.0 | 0.0 | MATCH |
| M59.recordable_incidents_ytd | Recordable Incidents YTD | 0 | 0 | MATCH |
| M59.lost_time_injuries | Lost-Time Injuries | 0 | 0 | MATCH (severity proxy) |
| M59.near_miss_mtd | Near-Miss MTD | 0 | 0 | MATCH |
| M59.statutory_clock | Statutory Clock | 0 | 0 | MATCH (count of un-notified registers) |
| M59.ppe_compliance | PPE Stock Compliance % | 0.0 | 0.0 (0 items) | MATCH |
| M59.drills_completed | Drills Completed | 0 | 0 | MATCH |

KPI engine honesty verified: four tile states (live / noactivity / unserved / nosource) with
captions; null renders "—" (p03_workspace.js:877-929). No KPI exception is swallowed to "—" by
the controller (only AccessError withholds a whole module's figures, by design, a09/__init__.py:41-43).

## 4. Report reconciliation table (44 served packs; registry promises 35)

All 44 packs served without error as the all-groups user (probe2). "Date filter" = does the pack
use the period the screen passes (UI-F3 class).

| pack | rows | verdict |
|---|---|---|
| M21:headcount_movement | 22 (branch rows; totals reconcile to 504) | OK; period respected |
| M21:attrition_analysis | 0 | OK; period respected |
| M21:probation_conversion | 205 — all "probationary employees with NO probation contract" | OK; honest note; readiness flag |
| M21:establishment_register | 61 | OK |
| M21:org_distribution | 140 | OK |
| M21:form6a_register | 504 | OK; HR-gated (NID column) |
| M21:identity_access_log | 2000 (of 5321) | UI-F12 cap |
| M21:data_cleanup | 0 | OK |
| M22:role_gap_analysis | 0 | OK; **no date filter** |
| M22:certification_coverage | 0 | OK; **no date filter** |
| M22:expiry_forecast | 0 | fixed 180d horizon by design |
| M22:training_effectiveness | 0 | **no date filter** |
| M22:skill_gap_heatmap | 4 | OK |
| M22:audit_evidence | 0 | **no date filter** |
| M55:attendance_summary | 0 | OK; UTC-window bug [STATIC] (UI-F8) |
| M55:overtime_analysis | 0 | derives from attendance_summary |
| M55:leave_utilisation | 0 | OK; period respected |
| M55:leave_balances | 504 | **UI-F2** fiscal-window year bug |
| M55:roster_vs_actual | 0 | OK |
| M55:coverage_gaps | 0 | OK |
| M56:my_payslips | 0 (probe admin has none) | OK; own-only window |
| M56:salary_register | 0 | **ignores date params** (UI-F3) |
| M56:payroll_cost_allocation | 0 | **ignores date params** |
| M56:tax_deduction_summary | 0 | **ignores date params** + hardcoded "AY 2026-27" |
| M56:pf_gratuity | 0 | **ignores date params**; mis-wired to M56-gratuity (UI-F1) |
| M56:payroll_variance | 0 (empty-pack columns kept) | OK |
| M56:gratuity_provision | 0 | OK; only reachable via chip (UI-F1) |
| M57:rating_distribution | 0 | **no date filter** |
| M57:incentive_payout | 0 | **no date filter**; band_base group-gated correctly |
| M57:technician_scorecards | 0 | **no date filter** |
| M57:calibration_summary | 0 | **no date filter** |
| M57:pip_outcomes | 0 | **no date filter** |
| M58:funnel_conversion | 6 stage rows (0 candidates) | OK; title honest; **no date filter** |
| M58:time_to_fill | 0 | **no date filter** |
| M58:source_effectiveness | 0 | **no date filter** |
| M58:first90_retention | 0 | **no date filter** |
| M58:practical_results | 0 | **no date filter** |
| M58:cost_per_hire | 0 | **no date filter** |
| M58:day_one_readiness | 0 | OK (open plans only) |
| M59:incident_statistics | 0 | **no date filter** |
| M59:leading_indicators | 5 | fixed MTD basis by design |
| M59:statutory_compliance | 0 | OK; BLA s.80 clock columns present |
| M59:ppe_compliance | 0 | OK |
| M59:drill_coverage | 0 | **no date filter** |

Exports: the download/email standard is one action bar bound to `reportTarget` — the SAME pack
function and params as the screen (p03_generic_api.py:600-699, 816-931; p03_workspace.js:1095-1130),
CSV/XLSX/PDF(+inline print)/e-mail with letterhead via shared `report_bytes`/`report_delivery`,
every export logged (`fix.bi.export.log`). Letterhead bytes NOT CHECKED this round. Statutory
documents from A09 screens: Form 6(a) register pack (M21-rpt-form6a), Form 6/Form 7/ID card/PSR
actions on M21-directory (SURFACES-verified), payslip bn + tax certificate + salary register via
M56 surfaces/packs, Form 28/overtime register export via `fix.attendance.lock`
(`action_export_form10_overtime_register`), service certificate via `fix.hr.exit`
(`action_issue_service_certificate`) — all whitelisted and model-backed [STATIC].

## 5. Access matrix (personas × model families, fresh envs on fix_real_a09)

read = rows visible / rows existing (master data only — nearly all families are empty);
W = write on a visible record obtained, U = unlink obtained. "refused" = AccessError.

| persona (only group + base internal) | employee master | contracts/transfers/exits | documents/dependants | disciplinary/abandonment | attendance/rosters/OT | leave | payslip/periods/structures | BEFTN/MFS/nominee | bonus/WPPF | performance/PIP/feedback | incentive runs/lines | bands/proposals/succession | candidates/offers/checks | onboarding | certs/training/OJT | HSE incidents/register/PPE | health/fitness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| plain employee | 5 visible (directory rule); NID/TIN/passport/bank read **refused** (field groups) | refused | refused | refused | refused (own-only by rule) | 6/6 types read, own-only writes | **refused** | **refused** | **refused** | refused (own-only by rule) | scheme read only | **refused** | **refused** | refused | refused | refused | **refused** |
| line manager (hr.group_hr_user) | directory + reports' data by rule | refused | 1/1 read | refused | refused | 6/6 | refused | refused | refused | refused | 2/2 read | **4/4 bands read** (SEC-F3) | refused | refused | refused | refused | refused |
| HR Officer (cd_hr_core) | as designed | as designed | 1/1 **W** | as designed | refused | 6/6 **W** | refused | refused | refused | refused | 2/2 | 4/4 | refused | refused | refused | refused | refused |
| HR Manager (hr.group_hr_manager) | full | full | 1/1 **W+U** | full | full | 6/6 W | refused | refused | refused | full | 2/2 | 4/4 | refused | full | full | full | refused |
| Payroll Officer | own-scoped | own-scoped | 1/1 read | refused | refused | 6/6 | **allowed** (ACL payroll) | **allowed** | **allowed** | refused | 1/2 | **refused** | refused | refused | refused | refused | refused |
| Payroll Manager | as officer + manage | as officer | 1/1 read | refused | refused | 6/6 | **allowed** | **allowed** | **allowed** | refused | 1/2 | **refused** | refused | refused | refused | refused | refused |
| Attendance Supervisor | refused | refused | refused | refused | **allowed** | 6/6 | refused | refused | refused | refused | 1/2 | refused | refused | refused | refused | refused | refused |
| Training (cd_competency) | refused | refused | refused | refused | refused | 6/6 | refused | refused | refused | refused | 1/2 | refused | refused | refused | **allowed** | refused | refused |
| Recruiter (cd_talent.group_talent) | refused | refused | refused | refused | refused | 6/6 | refused | refused | refused | refused | 1/2 | refused | **allowed** | **allowed** | refused | refused | refused |
| HSE Officer | refused | refused | refused | refused | refused | 6/6 | refused | refused | refused | refused | 1/2 | refused | refused | refused | refused | **allowed** | refused |
| Occupational Health | refused | refused | refused | refused | refused | 6/6 | refused | refused | refused | refused | 1/2 | refused | refused | refused | refused | refused | **allowed** |
| Finance (cd_hr_core.group_hr_finance) | refused | refused | refused | refused | refused | 6/6 | refused | refused | refused | refused | 1/2 | refused | refused | refused | refused | refused | refused |

Verdict: **no hole** — every sensitive family is refused exactly where the ACL/rule design says
so; the only widenings are the two P3 observations in SEC-F3. hr.employee itself is core-owned;
its extension fields' ACL (`cd_employee_core`) grants base read only, and identity fields are
group-gated (measured). Portal/share users: `_require_internal` guards every /p03 endpoint
(p03_generic_api.py:398 etc.) [STATIC].

## 6. Measured facts on fix_real_a09 (L)

- **hr.employee = 504, leavers (left_date set) = 0.** hr.version = 504.
- Transactional A09 data is **empty**: employment contracts 0, payslips 0, payroll periods 0,
  attendance records 0, leave requests 0, candidates 0, incidents 0, certifications 0,
  performance reviews 0, requisitions 0. Master data present: 61 positions, 21 departments,
  61 jobs, 6 leave types, 12 holidays, 5 shift templates, 3 learning paths, 4 competencies,
  4 compensation bands, 1 incentive scheme (+1 version), 1 statutory pack, 3 working-time rules,
  1 onboarding template (6 lines), 1 hr.document, 7 asset categories, 73 branches.
- **205 employees are recorded `employment_type=probationary` with 0 probation contracts** —
  the Probation Conversion report is 205 "cannot track" rows; probation KPIs read 0.
- **privacy_notice_pending = 504** (no live acknowledgement of the employment privacy notice).
- Positions carry no usable sanctioned headcount (open_positions KPI = 0 with 61 positions).
- **fix.hr.identity.access.log = 5321 reads** (identity values ARE being read and logged);
  display_name unresolved on all rows (UI-F10).
- Group holders (active internal users): every A09 group has ≥1 holder; **exactly 1 holder on 16
  of 32** groups (incl. group_hr_executive, group_hr_legal_counsel, group_clearance_it/assets,
  group_compensation, group_incentive_approver, group_scheme_cfo/hr_director, group_training_
  budget_approver, group_attendance_lock_manager, group_certification_verifier, group_injury_
  compensation_approver, group_occupational_health, all four cd_talent approver groups);
  hr_officer 5, hr_manager 5, attendance_supervisor 24, hse_officer 5, statutory_notifier 5,
  payroll officer/manager/release 3/3/3, training 7, talent 5.

## 7. Owner decisions (with recommendation)

1. **Regenerate `contracts/nav/registry.json` from the fragments** (108 screens, 5 bn titles, 8
   screen titles, 25 type chips, 1 form name drifted). Recommend: regenerate now and add a
   registry-vs-fragment equality check to CI (UI-F6).
2. **Period semantics for HR packs**: decide fiscal vs calendar window per pack; today every
   period-enabled screen sends the fiscal July–June window and `leave_balances` computes
   calendar-2027 (UI-F2). Recommend: calendar-year basis for leave/HSE/training packs; fiscal
   for payroll packs; declare it on the screen config.
3. **M56-gratuity wiring** (UI-F1): point the nav screen at `gratuity_provision`. Trivial fix.
4. **M21 ESS/MSS hub** (UI-F5): build the self-service dashboard the spec promises, or retitle
   the screen. Recommend building it — ESS adoption is KPI-213.
5. **Bengali form labels** (UI-F7): choose fragment-declared `bn` labels vs translated model
   strings. Recommend: prefer the bn_BD model string in bn mode unless the fragment declares bn.
6. **Two dead action whitelist entries** (SEC-F1) and the missing "Request Calibration" button
   (UI-F4): trim/extend respectively.
7. **SoD single holders** on 16 groups (§6): appoint second holders before the first real
   payroll run (approvals will queue on one person).
8. **Band readability by line managers / permit create by anyone** (SEC-F3): confirm or restrict.

Adviser questions: none new (statutory figures were R9-out of scope this round; the 30 Oct
statutory findings belong to the payroll auditor).

## 8. Tests

Existing A09 portal suites (`test_a09_control_suite.py`, `test_a09_write_whitelist.py`,
`test_a09_p0_people_controls.py`, `test_a09_m21_report_labels.py`,
`test_m2[12]_capture_*.py`, `test_m5[5-9]_capture_buttons.py`) — **run by the lead** (this
auditor did not restart pytest per the lead's instruction); counts not re-measured here. My own
equivalent static checks (writable regeneration, action wiring, tab rule, cols existence)
reproduced the suites' invariants and found them holding, except the two dead whitelist entries
above which the suites do not test.

## 9. Environment confirmation

- Private Odoo HTTP server on 8791: **not restarted** after the cut-off; **not running**
  (verified by the lead before resume; nothing listening). Nothing to stop.
- All fix_real_a09 probes ended with `env.cr.rollback()`; no writes persisted (the two probe
  users created inside transactions were rolled back).
- No files under any checkout were modified; all outputs live in
  `C:\Users\DELL\AppData\Local\Temp\a09erp\R9\`.
