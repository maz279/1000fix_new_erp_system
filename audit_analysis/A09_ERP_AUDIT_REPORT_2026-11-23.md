# A09 People & Workforce — ERP audit and fix program (report, 23 Nov 2026)

Company: 1000 FiX Services Ltd (after-sales repair, Bangladesh; BDT; Dhaka business day).
Scope: the seven A09 modules — **M21** Core HR & Employee Lifecycle, **M22** Learning, Competency
& Certification, **M55** Time, Attendance & Scheduling, **M56** Payroll, Benefits & Statutory,
**M57** Performance, Incentives & Compensation, **M58** Talent Acquisition & Onboarding, **M59**
Health, Safety & Wellbeing — with every link into and out of the other areas (M01/M02/M31 service,
M15/M16 supply chain, M17/M45–M48 assets, M19–M54 finance, M23/M24/M60 governance, M27 contact
centre, M29 identity, M30 branches, M63 approvals).
Code audited at `6f0d6a54`; production measured on `fix_real_a09`, a snapshot of the live database
taken 22 Nov 2026 18:40 (350 users, 504 employees, 155 modules).

## 1. How it was done (and what the evidence standard is)

- **Nine read-only auditors** (one per module, one for cross-area flows, one for the workspace,
  KPIs, reports and security), each with its own copy of the test database, executable probes on
  the production snapshot (every probe ended in a rollback), and a findings file with `file:line`
  plus probe output for every claim. Brief: `audit_analysis/A09_ERP_AUDITOR_BRIEF.md`.
- **The lead's own checks**, independent of the auditors: all **80 registry screens** and the seven
  module homes opened and read in the **in-app browser on production** (`fix_real@8069`); every
  high-severity claim re-tested with a separate probe; the statutory figures checked against the
  Labour Act 2006, the Labour Rules 2015 (gazette text) and official summaries, and the income-tax
  tables against the professional tax service.
- **Corrections the lead made to auditor claims** (an audit is only as good as its re-verification):
  - M56-F9 ("a plain employee can read a colleague's payslip") is **not a defect**. It reproduced
    only because the auditor's probe read the record from the ORM cache after the superuser had
    created it in the same transaction. With a cleared cache — how every real request starts — the
    field read, `read()`, `search` and `read_group` all raise AccessError.
  - X-F1 ("all 504 joiner events failed on the bus") is a **rollout item, not a bug**: the November
    employee load deliberately suppressed provisioning ("IdP deferred to user-rollout wave").
  - One auditor's claim that the 2026 Act moved termination notice to 12 weeks is **not supported**
    by any source found; the 120-day notice for monthly-rated permanent workers stands.
- Evidence archive: `audit_analysis/evidence_a09_erp/` — nine findings files, the in-app-browser
  walk (`IAB_WALK_2026-11-22.md`) and its captures, the decisions document, and the builder brief.

## 2. Result of the audit

**190 findings — P0 3 · P1 36 · P2 100 · P3 51** (one P1 disproved afterwards, one P0 re-classified
as a rollout item; the figures are the auditors' rows as recorded).

| module | findings | P0 | P1 | P2 | P3 |
|---|---|---|---|---|---|
| M21 Core HR | 31 | 0 | 4 | 16 | 11 |
| M22 Learning | 15 | 0 | 5 | 7 | 3 |
| M55 Attendance | 23 | 0 | 5 | 11 | 7 |
| M56 Payroll | 27 | 1 | 11 | 11 | 4 |
| M57 Performance | 28 | 1 | 2 | 19 | 6 |
| M58 Talent | 20 | 0 | 4 | 10 | 6 |
| M59 HSE | 14 | 0 | 1 | 11 | 2 |
| Cross-area flows | 17 | 1 | 4 | 9 | 3 |
| Workspace / KPIs / reports / security | 15 | 0 | 0 | 6 | 9 |
| **total** | **190** | **3** | **36** | **100** | **51** |

### 2.1 What the audit found working (measured, not assumed)

It is as important to say what holds, because these are the parts a fix must not break:

- **Security at master level: no hole found.** All 194 A09-area models are ACL-covered (the 8 without
  a row are tableless mixins); no model grants `base.group_user` write on payslips, candidates,
  compensation bands, succession or health records; every company-scoped model has a company rule;
  national ID / eIN / passport / bank fields are behind field groups. Thirteen personas × 154 models,
  each in a fresh environment, were refused exactly as designed (payroll for payroll roles,
  candidates for recruitment, health records for Occupational Health).
- **The payroll money path runs end to end** (synthetic staff, rolled back): trial run → attendance
  lock → calculate → pre-validate → routed approval with preparer ≠ approver and the approved digest
  pinned → release by a third role → 128-byte BEFTN file whose control total equals the approved net
  → settlement with bank evidence → publication → **a balanced journal on the real chart**
  (Dr salary 280,000 + 137,000, Dr employer PF 28,000; Cr net payable 327,125, Cr tax 61,875,
  Cr PF payable 56,000; debits = credits = 445,000) → M51 salary-tax intake → M50 payment execution.
- **Guard rails hold under attack**: direct writes to state, net, bank details, settlement amounts
  or certification state were refused; self-approval refused; a closed period refused posting even
  as superuser; identity reads logged append-only and readable only by the HR Manager.
- **Event wiring**: all 21 in-Odoo people-event consumers exist and are callable; every A09 cron
  method has an `ir.cron` record and runs as Asia/Dhaka; the 1-minute relay is healthy.
- **Workspace figures are honest**: all 47 served KPI values were recomputed independently from the
  ORM and matched; every report pack served without error and with honest empty states; no raw enum
  keys, `false`, `null` or `model,id` text on any of the 80 screens.

### 2.2 The worst defects (the ones that matter to the business)

Money
1. **Nobody can be paid.** Production holds 504 employees and **no employment contracts**, no bank
   account or routing for anyone, no TIN on anyone, no joining date on anyone. Payroll has nothing
   to compute from; annual leave accrues zero days for all 504.
2. **Incentives approved after their month's payroll were never paid** — the next run did not pick
   them up, and nothing warned.
3. **A raise effective mid-month was paid for the whole month at the old rate** — no arrears.
4. **Holiday and rest-day work was recorded but never paid**; approved unpaid leave did not reduce
   pay at all.
5. **Income tax used the pre-enactment draft thresholds** (৳375k/400k/475k/500k) instead of the
   enacted ৳400k/450k/525k/550k — over-withholding from every employee.
6. **Recoveries were unbounded**: with the cap at 0, a whole debt could be taken from one month's pay.
7. **Payroll officers could not post to the ledger** (posting needed accounting rights only the
   administrator held), so runs stranded after payment with no journal entry.
8. **Overpayment/PF/allowance defects** found by the October audit were verified fixed (allowances
   reach gross; the overtime divisor is 208; the statutory exemption is the ITA 2023 one).

Statutory
9. **Statutory forms were mislabelled**: "Form 6 Appointment Letter" (Form 6 is the identity card;
   the letter is unnumbered, r.19(4)); "Form 6(a) Register" was really the Form 8 workers' register
   and carried a national-ID column no prescribed form has.
10. **Two accident filings had no record at all** (the instant notice to the six authorities and the
    final report Form 27(A)), and the notice forms were mapped to the wrong Rules.
11. **The 2026 Labour (Amendment) Act figures were not applied** (maternity 120 days, 13 festival
    holidays, 1-year death-benefit service).
12. **No safety committee or fire drill is recorded** although the Act requires a committee in every
    establishment with 50+ workers.

Flow
13. **A hire dead-ended at onboarding completion** — the employee had no code, and nothing minted one.
14. **The Recruiter could not even read an offer** (no ACL row).
15. **Candidate national ID sat in clear** in the candidate table for the whole pipeline, and
    candidate erasure was switched off (retention 0), against the Personal Data Protection Act 2026.
16. **A leaver kept their open jobs, van and stock custody** — no consumer reassigns or blocks them,
    and the exit gate checked only IT assets and the toolkit.
17. **An un-tiered certification satisfied any repair tier**, and the workshop gate failed open.
18. **16 of 32 A09 role groups have exactly one holder (the administrator)**, and no HR money
    decision has an authority tier: a payroll release, bonus or settlement is approved at any amount.

*(The full register is the nine findings files; each row carries severity, evidence and a proposed fix.)*

### 2.3 Nine further defects the closing test runs found (fixed in this round)

Driving the regression suites green on the integrated database exposed nine code defects the
auditors' probe pass had not reached (each is now fixed and covered by the run that caught it):
1. **The monthly competence-coverage cron crashed** — `fix.certification._cron_competency_coverage`
   accumulated `fix.competency` records into a `fix.certification` recordset (`todo |= comp`), so
   `TypeError: inconsistent models` aborted the SPOF alert on every monthly run (M22 AUT-LMS-13).
   The accumulator is the competency model now.
2. **The payroll callout helper crashed** — `fix.oncall.callout._fix_payroll_verified_callout_hours`
   used `timedelta` without importing it, so verified callout hours could not reach pay (M55-F3).
3. **The employee master read "joining" for the whole workforce** — `employment_status` derived from
   the legacy `joined_date`, while the M21 master form (and the leave, exit and payroll flows) write
   `joining_date`; on production **0 of 504 employees** hold either date, so every master, KPI and
   dispatch list said "joining" and a suspended worker could never show "suspended" (M21-F13).
   The master's own Date of Joining now drives the base status, before the suspension/notice overlay.
4. **The technician KPI counted dispatchers and the Administrator** — both `m21._technicians` and
   `m22._technicians` used the group's *implied* users (`all_user_ids`), which includes every Field
   Service Manager and `base.user_admin`; the M02 dispatch pool uses the group's own members. The
   KPIs and the OJT-per-technician denominator now use the M02 rule (measured: the pool drops from
   1 phantom "technician" to 0 on an estate with no technician).
5. **The dispatch-gate readiness pack listed no device type at all** — `m22.gate_readiness` read the
   selection off `fix.device.device_type`, a *related* selection whose `_description_selection` is
   empty, so the owner-facing "Dispatch Gate Readiness" pack always reported "No device types
   defined" (M22-F2). It reads the source field on `fix.device.model` now.
6. **The instant-notice recipient model had no uniqueness constraint** — the new
   `fix.hse.notice.recipient` declared its `unique(register_id, authority)` through the legacy
   `_sql_constraints` list, which Odoo 19 only warns about and ignores, so the same authority could
   be recorded twice on one accident (M59-F2). It is a `models.Constraint` now, and the upgrade
   creates it (verified on the test database).

7. **The incentive approval gate never ran** — `fix.incentive.run.action_request_approval` set
   `voiding = bool(self.mapped("void_pending"))`: a one-item list of `False` is truthy, so the
   dispute-window and unapplied-adjustment gates were skipped on EVERY request (M57 BRU-PIC-12 /
   M57-F20). `any(...)` now.
8. **A scorecard with no facts crashed instead of scoring 0** — `composite_score` validated
   `0 <= v <= 1` over components that are `None` when their fact source is empty, so the
   renormalisation fix itself raised `TypeError` and a no-facts publish died (M57-F4/F7).
9. **The Department of Labour notice had no capture path** — the incident close gate requires
   `dol_notified` (BLA s.80(1) as replaced by the 2026 Act s.22) but nothing ever set it: every
   reportable accident was permanently unclosable. `action_notify_dol` (guarded, Statutory
   Notification Authority, reference required) records it, and the register form exposes it.

Two further observations, not fixed here: `cd_contact_centre` still declares two constraints through
`_sql_constraints` (outside A09; the same Odoo-19 no-op), and `hr.employee` carries both
`spouse_complete_name` (standard) and `spouse_name` (M21) with the same label — cosmetic duplication
to decide in the M21 UI round.

## 3. What was fixed in code (this round)

**79 distinct finding ids** are addressed in the wave-1 code changes (the code cites each id at the
fix); that change set is **9,388 changed lines across 89 code, test and contract files** in eight
modules plus the payroll engine, landed as nine per-module commits. **Wave 2 adds thirteen
findings** in seven commits (`9958ea23`, `3dd52a3e`, `9528d49f`, `3668cfa3`, `224f8178`, `1da3102b`,
`8a0bc096`): M21 UI-F12; M56-F19; M57-F2 and M57-F14; M58-F4, F12, F13, F15, F17, F18, F20;
M59-F10 and F11. Both waves were integrated on `fix_test_a09_int`, where the upgrade of every
changed module loads with no error, and closed with the module test runs recorded in §4.

**Correction to the first issue of this report.** The first issue credited four mechanisms that were
not in the code (builder summaries had been read as evidence). What is true:

- *M57 "HR Officer access per the spec"* — there was no HR Officer ACL row at all (M57-F14). Wave 2
  adds the five rows (`cd_performance/security/ir.model.access.csv`; test
  `test_a09_m57_officer_access.py`: the officer sets the cycle and goals up, unlink stays refused).
- *M57 "above-band exception via CFO"* — no such mechanism exists. M57-F18 is an owner decision
  (D27, §5) and is **open**.
- *M59 "inspection→CAPA→reopen loops"* — there was no CAPA reopen and no inspection→CAPA link. Wave
  2 builds the reopen (with the finding on the history) and the daily overdue reminder (M59-F10;
  test `test_a09_hse_r2.py`). Inspection scheduling and the inspection→CAPA/incident link remain
  open (§5).
- *M59 "fitness events published"* — no fitness event exists. What the audit actually asked for is
  built in wave 2: the dispatch now reads the published fitness status and refuses an Unfit
  technician (M59-F11; `cd_field_service`, test `test_a09_m59_fitness_gate.py`).
- *M58 "retention fail-closed"* — the retention period is an owner figure (M58-F3, §5); the code
  does not refuse capture. What is built is the residency store (M58-F4) and the erasure path.
- *M58 "hire cancel"* — not built; the hire reversal (M58-F5) is open (§5).

Highlights by module (each item is in the code; the module's test run is in §4):

- **M56 Payroll** — a Payroll Manager holding no accounting group can post (authorisation first,
  then the elevated posting funnel; the operator is still recorded); provident fund is taken only
  from registered members (empty register = nobody pays, not everybody 10/10); the A07 recovery API
  exists with a company cap and a per-source idempotency; the variance crash on a NULL-employee slip
  is guarded; approved incentive lines are carried into the next payroll; each contract version is
  paid for the days it was in force; unpaid leave and approved holiday/rest-day/callout hours reach
  pay; the statutory pack now carries real, effective-dated figures (enacted 2026-27 tables loaded
  **as proposed, awaiting sign-off** — today's table stays in force until approved); the investment
  rebate, resignation/gratuity bands, overtime base and proportional-bonus rule are pack options;
  the Bengali payslip itemises allowances, recovery, arrears and YTD and masks the account; the
  Gratuity screen shows gratuity (it showed the PF report); M56 reports honour their date range and
  Dhaka dates; gratuity refuses loudly when its accounts are unconfigured instead of writing rows
  with no journal; published payslips are archived as employee documents; a payroll **readiness
  preflight** names every missing contract, bank, tax profile and account role before a run.
- **M21 Core HR** — employee code minted from a company sequence (continuing the real `CS-####`
  series at 4892) so a hire completes; the duplicate unguarded Keycloak field gone; the statutory
  export gated to HR; the workers' register is the Form 8 shape without the NID column; a true
  Form 6(A) issue register and a correctly-titled appointment letter with the r.19(4) particulars;
  joiner events only for an employee M29 can key on; mover events for real moves only (department
  noise removed, position/branch/OU/role still announced); Form 7 clock on confirmation; identity
  log display names and an honest row count; M21 reports honour their period and Dhaka dates.
- **M55 / leave** — Balances no longer labels a future year (the lead's own find) and is batched;
  all M55 packs honour the period; day counting and Dhaka dates fixed; payroll-bound helpers for
  holiday, rest-day, callout and unpaid-leave figures; weekly payable-overtime ceiling; device
  health and exception-ageing crons; festival-typed holidays; duplicate field removed; ordinary
  exception detection (missing punch, late, early).
- **M57 Performance** — scorecards stop treating "no data" as "worst" (renormalised over the
  components that have facts) and every weighting can reach the top band; rework attribution;
  Dhaka month boundary; PIP/discipline eligibility; one adjustment can no longer block a month;
  scheme versions cannot overlap or be back-dated and their terms freeze at signature; the second
  signature is refused when the only CFO holders are the HR Director holders (wave-2 test
  `test_a09_m57_round2.py::test_the_request_refuses_when_every_cfo_is_also_the_hr_director`);
  clawbacks ride the run's approval statement and notify the employee; review-cycle dead ends
  closed; calibration can adjust; a run can be voided before payment; the six M57 tiles point at
  the lists their titles name, the missing "Request Calibration" button added, packs honour their
  period. **Wave 2**: the HR Officer's set-up access (M57-F14) — five ACL rows plus the set-up
  guards widened (create/change/open a cycle, start a review, start a PIP, request/change feedback);
  the decisions (close a cycle or a PIP, award, approve) stay where they were. **Open**: above-band
  exception (D27), and the privacy split of ratings from payroll readers (M57-F15, §5).
- **M59 HSE** — notice forms and citations corrected against the gazette (Form 27 / 27(A) / 27(B) /
  28 / 29; the register's basis is s.80(2), not s.90); the **instant notice** recorded per named
  authority and the **final report Form 27(A)** and occupational-disease notice Form 29 modelled
  with their clocks and close gates (the missing recipient model completed by the lead — its
  company isolation rule was missing until the wave-2 regeneration); the DIFE clock covers
  fatal/serious/minor/dangerous/first-aid with the 20-day escalation; the statutory compensation
  floor is computed (`fix_hse.py`, the BLA ss.150-152 block) and an award below it needs a recorded
  reason; the half-yearly return dates; committee representation checked (both sides required);
  reports and packs on Dhaka dates. **Wave 2**: CAPA reopen when a verification finds the action
  ineffective, and the daily overdue reminder (M59-F10); the dispatch fitness gate (M59-F11, in
  `cd_field_service`). **Open**: inspection scheduling and the inspection→CAPA/incident link
  (M59-F9), drill scheduling (M59-F7), PPE as stock (M59-F8) — §5.
- **M22 Learning** — an un-tiered certificate no longer satisfies a tiered job; the workshop gate
  has a switch (the flip is an owner decision); the certification check refuses before the
  assignment is written; training sessions mark availability; the effectiveness and coverage crons;
  KPI formulas fixed (brands, real technician population, configured lead time, passed assessments
  only); the catalogue skill gate covers `service` items; superuser overrides are logged; Dhaka
  dates; packs honour their period.
- **M58 Talent** — the recruiter can read and draft offers (lead-completed ACL); **wave 2**: the
  candidate's government identifiers live in the Bangladesh-resident store (M58-F4): keyed hashes
  shared with M21, pointers, the last four digits, a logged read path, the hire copies and releases,
  the 19.0.0.6.0 post-migrate moves the clear columns and a daily cron retries a row the store could
  not take (`test_m58_identity_residency.py`); the duplicate check reads the hash, never a value;
  the hiring manager and the requisition's approver can no longer approve their own requisition or
  sit on its panels (M58-F12); the KPIs say "unknown" where nothing was measured and the funnel
  share is over every candidate (M58-F13); an offer carries its acceptance deadline and an undated
  offer cannot be issued (M58-F15); a Hiring Manager reaches the first-90 reviews of their own
  requisitions (ACL row + record rule, M58-F17); "Separated" stays "Separated" on the employee
  (M58-F18); the minimum hiring age is checked when the offer is drafted (M58-F20); the appointment
  letter is corrected. **Open**: retention period and talent-pool period (M58-F3, owner), the hire
  reversal (M58-F5), the domain events (M58-F6) — §5.

Also in wave 2: **M56-F19** — the payslip's operating-unit rule filtered a column nothing sets, so
it always passed; two explicit rules now state the real scope (payroll runs the whole company;
anyone else sees their cost units), and the isolation generator skips the model (`--check` clean).
**Isolation regeneration** — `generate-isolation-rules.py --check` reported drift in eleven modules
(models added in recent rounds never got their company rule, including M58's candidate child
registers and `fix.hse.notice.recipient`); regenerated, 68 modules / 890 company rules / 453
operating-unit rules, no drift. **M21 UI-F12** — the identity read log pack stops at its cap and
says "first N of TOTAL" with the number left out (it used to title itself "2000 reads" as though
that were the whole log).

**The owner's four decisions, taken 2026-11-23 and built the same day** (`10561b43`, `9a2dccda`,
`1eba329d`; register D27, D28, D29 and M58-F15):
- **M58-F3 — candidate retention: 180 days, 365 with talent-pool consent.** The parameters are set
  (`cd_talent.candidate_retention_days = 180`, `cd_talent.talent_pool_retention_days = 365`, new) and
  `action_reject` reads them, so a candidate's talent-pool consent now has an effect (it had none).
  The 19.0.0.7.0 migration moves a database still carrying the old 0; a value the business set
  itself is never touched.
- **M58-F15 — offer validity: 14 days.** `cd_talent.offer_validity_days = 14`: a new offer defaults to
  a two-week acceptance window; an undated offer still cannot be issued.
- **M57-F15 / D28 — payroll reads the incentive money, not the ratings.** The "reads all" helper no
  longer includes the payroll groups for scorecards, goals, reviews, PIPs and feedback; payroll keeps
  the money records (lines, adjustments, clawbacks, disputes, recognition awards).
- **M57-F18 / D27 — the CFO-tier above-band exception.** A new `fix.band.exception` (employee, grade,
  monthly gross allowed up to, reason, optional contract/proposal link) is approved by the CFO tier
  from the M63 inbox; the band check then lets that contract or proposal inside the figure pass,
  while the band itself is unchanged. Its list and two-tab form are in the workspace (the sweep
  found the new screen clean).

What is still open (the builders were interrupted mid-stream twice by a shared usage cap; the
remaining items are listed in §5): the Talent hire reversal and domain events, the payroll arrears
for a raise activated after the month was paid, HSE inspection scheduling/CAPA link, the M55
cost/liability packs and Form 10 document, and the bilingual letterheaded PDF documents.

## 4. Deployment state

**Wave 1 — deployed and verified on both servers, 2026-11-23.**
- Backups before each upgrade: `fix_dev_pre_a09_erp_20261123_0834.dump` (71,151,381 B) and
  `fix_real_pre_a09_erp_20261123_0834.dump` (74,455,875 B); again at 09:43 for the hotfix
  (`fix_dev_pre_a09_20261123_0943.dump`, 71,588,751 B; `fix_real_pre_a09_20261123_0943.dump`,
  74,895,229 B).
- Upgrades: fix_dev 08:34, fix_real 09:43 — exit 0 with 0 errors in the upgrade logs (the single
  `Unexpected indentation` line is the estate's known asset-template warning). Both listeners were
  restarted through their watchdogs (8069 serves fix_real, 8090 serves fix_dev) and the regenerated
  asset bundles purged.
- Production data untouched: 504 employees, 0 employment contracts, 112 / 11 / 2 years of service,
  0 payslips; the employee-code sequence at 4892; the 2026-Act figures switch **absent** (they move
  only when approved); statutory packs baseline + drafts.
- The post-hotfix read-only sweep (46 report packs, 169 list screens, 145 form schemas and 7 module
  homes per server) found **0 issues and no console error** on either server, and confirmed the
  deployed fixes (M55 balances read "as at 2026-11-23 / Annual Taken 2026"; M22 gate readiness
  lists all 10 device types; M21 technicians 140 = the SQL count of the group's own members).
  Evidence: `scratch/rebuild/evidence/A09-deploy/live_check_after_hotfix.log`.

The production-data changes that need your approval are **not applied**: the 2026-Act figures move
only when you approve (one switch), and the enacted tax tables are proposed packs awaiting sign-off.

**Wave 2 — deployed and verified on both servers, 2026-11-23 16:55.**
- Backups before the upgrade: `fix_dev_pre_a09_20261123_1655.dump` (71,470,854 B) and
  `fix_real_pre_a09_20261123_1655.dump` (74,820,358 B).
- Upgraded on each database, fix_dev then fix_real: the seven A09 modules plus every module whose
  generated isolation rules changed (cd_competency, cd_field_service, cd_msp_contract,
  cd_service_order, cd_warranty_claims, cd_workshop, cd_contract_core, cd_quotation, cd_ewaste,
  cd_inventory, cd_gl_ext, cd_rbac_ext, cd_p03_portal) — 18 modules, **exit 0 with 0 errors** in
  both upgrade logs. Both listeners restarted (8090 at 17:06:45, 8069 at 17:07:18); assets purged
  (0 on dev, 3 on real); the 2026-Act switch **absent** on both.
- **An outage, and how it ended:** a concurrent session's deploy killed both listeners at ~17:08
  (the documented hazard of a shared checkout). The watchdogs restored them without intervention —
  8069 at 17:09:43, 8090 at 17:11:00 — 2–4 minutes down. No data was touched; the sweep below ran
  after both were back.
- The read-only sweep on the deployed code: **46 report packs, 169 list screens, 145 form schemas
  and 7 module homes per server — 0 issues, 0 console errors on both.** The Talent KPI tiles now
  read "—" where nothing was measured (fix_real: time-to-fill, offer accept rate, referral share,
  first-90 retention; fix_dev: time-to-fill, first-90 retention) instead of 0.0.
  Evidence: `scratch/rebuild/evidence/A09-deploy/live_check_wave2.log`, `results-fix_dev.json`,
  `results-fix_real.json`.
- Called directly on the deployed code (read-only), the identity read log pack on **fix_real** now
  titles itself **"Identity Read Log — first 2000 of 5321 reads"** and serves 2,000 rows: the period
  holds 5,321 reads and the pack says so, where it used to say "2000 reads" as though that were the
  whole log (fix_dev reads "20 reads", under the cap).
- Production data unchanged by the upgrade: 504 employees, **0 candidates, 0 offers, 0 payslips**.

**The owner's four decisions — deployed 2026-11-23 19:41.** Backups
`fix_dev_pre_a09_20261123_1941.dump` (71,542,271 B) and `fix_real_pre_a09_20261123_1941.dump`
(74,870,107 B); cd_talent, cd_performance, cd_gl_ext and cd_p03_portal upgraded on each database
(**exit 0, 0 errors**); both listeners restarted and back; the 2026-Act switch still absent.
Verified by SQL on both: the three figures are set (180 / 365 / 14), the `fix_band_exception` table
and its sequence exist. The sweep after it: **46 report packs, 170 list screens, 146 form schemas and
7 module homes per server — 0 issues, 0 console errors** (the new Above-Band Exceptions list and
its two-tab form serve clean). Tests: cd_performance 134 passed (after the copy that ran before a
test-data fix was re-run clean: the band-exception and review-privacy tests 2 passed, and the
Talent retention / offer-validity / KPI tests 3 passed); cd_talent **133 passed** with the one
earlier failure traced to a missing table from a concurrent session's un-upgraded model (the dunning
handoff), clear after that module's upgrade.

**Test evidence for wave 2** (`fix_test_a09_int`, the integrated database): cd_talent **133 passed**;
cd_hse **97 passed**; cd_payroll_bd **176 passed**; cd_competency **139 passed**; cd_hr_core **327
passed, 1 skipped**; the closing run of the identity-residency suite, the performance suite (with the new officer test), the M21 control
suite and the field-service fitness gate **214 passed, 1 skipped, 0 failed**; the A09 portal guard
files **509 passed** (including the two M21 wave-2 portal tests and the estate KPI-tile contract,
which requires a ratio to be None — not 0 — while its denominator is empty, as the Talent tiles now
are); the live sweep above is the check
the suites cannot make (the served screens). The whole-estate portal suite (6,713 tests over every
area) was attempted but its process was killed mid-run twice in this shared environment (at 57 % and
26 %); the failures it had shown fell in A10/A11/A12 files another session was editing at the time,
none in an A09 file.

## 5. Open items and what happens next

Built and verified in wave 2 (§3/§4): M58-F4, F12, F13, F15, F17, F18, F20; M59-F10 and F11;
M56-F19; M57-F2 and F14; M21 UI-F12; the isolation regeneration. Built on the owner's four
decisions (same day, §3): M58-F3, the offer-validity figure, M57-F15 and M57-F18 (D27).

**Open — code we owe:**

| Finding | Pri | What is missing | Remedy |
|---|---|---|---|
| M56 / M57-F3 (arrears half) | P1 | A contract version activated *after* its month was paid creates no arrears. The in-period case is built and tested (`test_m57f3_a_raise_effective_mid_month_is_paid_for_the_days_it_ran`: 30,000×15/31 + 40,000×16/31 = 35,161.29). | On activation, if the covered month is already posted, carry the difference into the next run's slip as an arrears line. |
| M58-F5 | P2 | No hire reversal: no `action_cancel` on the plan (draft / in progress), the candidate never returns to "offered". `_fix_take_back_identity` is written and has no caller. | Guarded plan cancel: unlink the draft contract and M22 baseline, archive the employee, clear `employee_id`, reset the candidate, recall the joiner event. |
| M58-F6 | P2 | 9 of the 10 spec domain events are unpublished (`requisition.approved/blocked`, `candidate.applied`, `assessment.completed`, `offer.issued/accepted/declined`, `onboarding.started`, `readiness.incomplete`, `candidate.erased`, `probation.plan_created`); only `employee.joined` flows. | Publish through `libs/py/fix_events.publish` at the existing transitions; regenerate `contracts/events`. |
| M59-F9 | P2 | Inspections have no schedule, no overdue and no link to a CAPA/incident ("Follow-up Required" is reachable, and the checks can be corrected and re-completed). | Add `scheduled_for` + an overdue cron, and a guarded "raise incident from inspection" that opens the incident whose CAPAs the findings need. |
| M59-F7 / F8 | P2 | No drill schedule/overdue logic (s.62(8)); PPE is a counter, not M15 stock (no replenishment demand, no replacement interval). | Drill cadence by workforce size; PPE as a stock item with a reorder rule. |
| M55-F10 | P2 | Overtime analysis reports hours only (no cost, no budget); leave balances have no projection; no leave-liability pack. | Price the overtime pack through the payroll engine's own `overtime_amount` (never a parallel formula) and add unused-days × daily-rate. |
| M55-F19 | P3 | Form 10 (BLR r.102) is rows from a workspace action, not a formatted statutory document. | Render it through the report-export standard (PDF, letterhead). |
| M55-F22 | P3 | A leave spanning out of a locked month is refused outright instead of being split; the maternity "six months' service" test awaits labour counsel. | Allow the future part of the span; align the maternity test once counsel rules. |

**Owner decisions:** `audit_analysis/A09_ERP_AUDIT_DECISIONS_2026-11-23.md` (40 items, each with a
recommendation), of which the five that block go-live are D1 (contracts and master data), D2
(identity rollout), D3 (role holders), D4 (authority tiers) and D5 (provident fund).
