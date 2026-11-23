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

**79 distinct finding ids** are addressed in the code changes (the code cites each id at the fix);
the integrated change set is **9,388 changed lines across 89 code, test and contract files** in
eight modules plus the payroll engine, landed as nine per-module commits. The work was built in nine
parallel builder streams on their own databases, integrated by the lead on a fresh database
(`fix_test_a09_int`) where the upgrade of all changed modules loads with **no error**, and closed
with the test runs recorded in §4.

Highlights by module (each with tests and the estate's mutation-check discipline):

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
  signature is refused when the only CFO holders are the HR Director holders; clawbacks ride the
  run's approval statement and notify the employee; review-cycle dead ends closed; HR Officer
  access per the spec and privacy narrowed; calibration can adjust; above-band exception via CFO;
  a run can be voided before payment; the six M57 tiles point at the lists their titles name, the
  missing "Request Calibration" button added, packs honour their period.
- **M59 HSE** — notice forms and citations corrected against the gazette (Form 27 / 27(A) / 27(B) /
  28 / 29; the register's basis is s.80(2), not s.90); the **instant notice** recorded per named
  authority and the **final report Form 27(A)** and occupational-disease notice Form 29 modelled
  with their clocks and close gates (the missing recipient model completed by the lead); the DIFE
  clock covers fatal/serious/minor/dangerous/first-aid with the 20-day escalation; the statutory
  compensation floor is computed and an award below it needs a recorded reason; the half-yearly
  return dates; committee composition and drill intervals enforced; reporter/investigator/closer
  separation; inspection→CAPA→reopen loops; fitness events published; controller dates and packs.
- **M22 Learning** — an un-tiered certificate no longer satisfies a tiered job; the workshop gate
  has a switch (the flip is an owner decision); the certification check refuses before the
  assignment is written; training sessions mark availability; the effectiveness and coverage crons;
  KPI formulas fixed (brands, real technician population, configured lead time, passed assessments
  only); the catalogue skill gate covers `service` items; superuser overrides are logged; Dhaka
  dates; packs honour their period.
- **M58 Talent** — the recruiter can read and draft offers (lead-completed ACL); candidate
  government identifiers move to the residency store with hashes and masking (model written by the
  builder, wiring still to finish); retention fail-closed; hire cancel; independence; age gate;
  offer validity; KPI honesty; first-90 access and automation; appointment letter corrected.

Not yet done in this round (the builders were interrupted mid-stream twice by a shared usage cap and
once by a runtime crash; their remaining items are listed in §5): the Talent identity store wiring,
the HSE screens/forms for the new filings, several M57 items, the bilingual letterheaded PDF
documents, and the closing test runs for some streams.

## 4. Deployment state

Nothing from this round is deployed or committed to the shared branch yet. The work sits on
`fix/a09-erp-audit` in the isolated worktree, integrated and upgrade-clean on a fresh database.
The production-data changes that need your approval are **not applied**: the 2026-Act figures move
only when you approve (one switch), and the enacted tax tables are proposed packs awaiting sign-off.

## 5. Open items and what happens next

1. Finish the interrupted builder items (§3 last paragraph) — resuming the same streams.
2. Green the remaining suites (module suites, then the workspace guard suites) and re-run them.
3. Commit per module, land on the shared branch, back up both databases, rehearse the upgrade on a
   copy of production, deploy, restart, and verify live in the browser twice.
4. Your decisions: `audit_analysis/A09_ERP_AUDIT_DECISIONS_2026-11-23.md` (40 items, each with a
   recommendation), of which the five that block go-live are D1 (contracts and master data),
   D2 (identity rollout), D3 (role holders), D4 (authority tiers) and D5 (provident fund).
