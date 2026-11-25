# A09 ERP audit — auditor brief (read all of it before starting)

You are one of nine READ-ONLY auditors of the A09 "People & Workforce" area of
1000 FiX Services Ltd's Odoo 19 ERP (after-sales repair of IT, mobile and home appliances,
Bangladesh; currency BDT; business day Asia/Dhaka UTC+6; ~79 branches; 504 employees on roll;
ISO 9001:2015 certified). The owner's goal: every A09 module must work as a top-class
HR/payroll/HSE module of an ERP — data-capture forms, functions, dashboards/KPIs, approval
flows, business flows, business rules, calculations, accounting logic, professional exports —
and every cross-relation with other modules (same area and other areas) must be correct, as in
a true ERP. Find every gap, error and mistake, with evidence. A lead session will re-verify
your findings and turn them into fixes and owner decisions.

A09 has seven modules:

| id | module | addon(s) under `addons/domain/h_people/` |
|---|---|---|
| M21 | Core HR & Employee Lifecycle | `cd_hr_core` (+ the `hr.employee` master in platform addon `cd_employee_core`) |
| M22 | Learning, Competency & Certification | `cd_competency` |
| M55 | Time, Attendance & Scheduling | `cd_attendance` (leave models live in `cd_hr_core`) |
| M56 | Payroll, Benefits & Statutory | `cd_payroll_bd` |
| M57 | Performance, Incentives & Compensation | `cd_performance` |
| M58 | Talent Acquisition & Onboarding | `cd_talent` |
| M59 | Health, Safety & Wellbeing | `cd_hse` (plus the A07-owned bridge `addons/domain/f_asset_facilities/cd_asset_finance_hse_bridge`) |

## Where

- **Worktree** (code at shared HEAD `6f0d6a54`): `C:\software_project\software_project_14\1000 fix\a09erp-wt`
  - code root `...\a09erp-wt\1000_fix_codebase` (called CODE below)
  - module specs: `...\a09erp-wt\1000fix_ERP_Module\03_Modules\H_People_and_Workforce\M*.md`
    and `_CATEGORY_OVERVIEW.md` (the people chain, who owns what, the cross-module contracts)
  - other areas' specs: `...\a09erp-wt\1000fix_ERP_Module\03_Modules\<A..K>_*\M*.md`;
    cross-cutting: `...\1000fix_ERP_Module\05_Cross_Cutting_Specifications\` (roles matrix,
    business rules catalogue, integration catalogue)
  - P03 workspace (the D365-style UI on top of Odoo): fragments
    `CODE\addons\platform\cd_p03_portal\static\src\a09\m*.js`, served surfaces
    `CODE\addons\platform\cd_p03_portal\controllers\a09\m*.py` (+ generated `writable.py` = the
    fields a form may write), engine `static\src\p03_workspace.js`, report packs and KPIs under
    `cd_p03_portal\controllers\` (grep the module id, e.g. `M56`); canonical nav universe
    `CODE\contracts\nav\registry.json` (A09: 80 screens, 35 reports, 28 forms, 42 KPIs).
  - platforms A09 leans on: `cd_employee_core`, `cd_workflow_engine`, `cd_rbac_ext`,
    `cd_event_outbox`, `cd_document_core`/`cd_doc_suite`, `cd_entity_config`, `cd_party_master`
    (identity residency), `libs\py\fix_residency`, `libs\py\fix_events`.
- **Earlier audits (read first; do not re-report what is fixed — verify the current state):**
  - 3–6 Nov workflow/approval audit and its two build rounds (P0-a, P0-b, P1, P2, P3 built,
    merged, deployed): `C:\software_project\software_project_14\all_working_folder\working\A09_Workflow_and_Approval_Report.md`
    (its §7 lists decisions still waiting for the business; its Updates list every setting that
    shipped "off" or "0"); evidence `...\working\A09_evidence\` (benchmark checklist, probes).
  - capture-button audits 13–19 Nov: `...\a09erp-wt\audit_analysis\M21_CAPTURE_BUTTON_AUDIT_PASS2_2026-11-19.md`,
    `M22_CAPTURE_BUTTON_AUDIT_PASS2_2026-11-19.md`, `M55_…_2026-11-17.md`, `M56_…_2026-11-17.md`,
    `M57_…_2026-11-17.md`, `M58_…_2026-11-17.md`, `M58_CANDIDATE_BIODATA_STANDARD_2026-11-18.md`,
    `M59_…_2026-11-18.md`, `M21_BIDIRECTIONAL_AUDIT_2026-11-13.md`.
  - The area audits you should imitate in depth: `...\a09erp-wt\audit_analysis\A07_ERP_AUDIT_REPORT_2026-11-20.md`,
    `A06_ERP_AUDIT_REPORT_2026-11-21.md`, `A04_ERP_AUDIT_REPORT_2026-11-21.md`,
    `A02_ERP_AUDIT_LEDGER_2026-11-19.md` (their P0s were money that never reached the ledger and
    controls anyone could bypass).
  - 30 Oct statutory/money audit findings that must be re-checked on today's code:
    allowances never reaching gross; the incentive top band unreachable (composite score max 0.85
    vs the 0.90 band); overtime divisor 240 instead of 208 on a basic-only base; WPPF; repealed
    ITO 1984 exemptions presented as ITA 2023; wrong accident-reporting citations.
- **Databases** (Postgres on 127.0.0.1:5433 in docker `compose-postgres-1`, user `fix`):
  - `fix_real_a09` = snapshot taken today of production `fix_real`: real chart (legacy codes
    `100001..100809`, AR control 100201, AP control 200101), real users and roles, real branches
    with their own operating units, real bank accounts, real ledger take-ons. Use it to measure
    real configuration, real data and to run money/role probes. **Read-only: every script ends
    with `env.cr.rollback()`; never `-u` it; never commit.**
  - `fix_test_a09_<your id>` = your private pytest/test database (named in your prompt). You may
    run pytest on it (each test is rolled back) and `-u` a module on it ONLY if your prompt allows.
  - `fix_real`, `fix_dev`, ports 8069/8090 and every other database: hands off.

## How to probe (PowerShell; Git-Bash breaks PYTHONPATH for odoo-bin)

```powershell
$W = "C:\software_project\software_project_14\1000 fix\a09erp-wt\1000_fix_codebase"; Set-Location $W
$env:PYTHONPATH = $W; $env:TZ = "UTC"
Get-Content <your_probe.py> | .\.venv\Scripts\python.exe vendor/odoo/odoo-bin shell -c infra/odoo-conf/local.resolved.conf -d fix_real_a09 --no-http --log-level=warn
# pytest (do NOT add another -q; pyproject already has one and a second hides the summary line):
$env:FIX_TEST_DB = "fix_test_a09_<your id>"; .\.venv\Scripts\python.exe -m pytest <path> -p no:cacheprovider > <your folder>\x.log 2>&1
# SQL (ids/counts/aggregates only):
docker exec compose-postgres-1 psql -U fix -d fix_real_a09 -Atc "select ..."
```

- Write probe scripts with the **Write tool** into your own folder
  `C:\Users\DELL\AppData\Local\Temp\a09erp\<your id>\` (a security hook on this machine rejects
  shell heredocs that write code). Write ONLY inside that folder. Keep every probe and its raw
  output there.
- Run access probes as a real **non-superuser** (`env["x"].with_user(u)`, `su=False`) with a
  **fresh env** — the superuser and a warm cache hide ACL and record-rule problems.
- **The machine is shared** (other audit sessions run their own tests here). Run at most ONE
  Odoo process of your own at a time. Before starting an Odoo shell or pytest, check
  `(Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'odoo-bin.+shell|pytest' }).Count`
  — each run shows as 2 processes; wait (sleep 30, re-check, up to 15 minutes) while it is 16 or
  more. Batch many questions into one shell script instead of many short runs (one registry load
  takes ~25 s; test suites are slow under load — run them in the background and read the log).
- Odoo 19 notes: `Environment` has no `with_context` (use `env(context={**env.context, ...})`);
  no `name_get` (use `_compute_display_name`); `models.Constraint`; views use `<list>`;
  `account.account` code is in jsonb `code_store` keyed by company id.

## Hard rules

1. **READ-ONLY on code.** Do not edit, create or delete any file under the worktree or any
   checkout. Never `git commit/stash/checkout/branch/push/worktree`. Write only inside your own
   temp folder.
2. Never touch ports 8069/8089/8090, the databases `fix_real` / `fix_dev` or other sessions'
   databases, or any process you did not start. Never `-u`/`-i` any database (except your own
   test DB when your prompt allows). Never commit a transaction.
3. **No personal data in your notes.** Do not copy NID, TIN, passport, phone, address, bank
   account numbers, medical details, or a named person's salary into FINDINGS.md or probe
   outputs. Report ids, counts and aggregates only.
4. **Evidence standard.** A finding needs file:line AND, wherever possible, executable proof
   (a probe output or a failing test against the ORM). "The source says X" alone is weak: mark
   such findings [STATIC]. Re-check any claim about live data with a direct query before citing
   it. An auditor finding that does not hold up wastes a builder's time — be sure.
5. **Ownership.** Don't report what is out of A09's ownership as an A09 defect, but DO report
   broken cross-relations, with which side is wrong (A09 ↔ M01/M02/M31 service and dispatch,
   M15 stock, M45/M46/M47/M48 assets, M19 GL, M20 AR, M50 treasury, M51 tax, M52 AP, M54 budget,
   M23 QMS, M24 documents, M27 notifications, M29 access lifecycle, M30 branch/OU, M60 risk,
   M63 approvals/DOFA, M25/M62 BI).
6. **Statutory claims.** The code and the specs cite Bangladesh Labour Act 2006, Labour Rules
   2015, Income Tax Act 2023 and later amendments. Do not trust a citation because the spec or
   the code repeats it. Check the rules that matter (pay, tax, hours, leave, notices, registers,
   compensation) against primary or authoritative sources with web research
   (bdlaws.minlaw.gov.bd, nbr.gov.bd, Big 4 / law-firm alerts). Where the law changed in 2025 or
   2026, say so with the source and date. Where you cannot confirm a figure, mark it
   "ADVISER" with your best recommendation; never present a guess as law.

## What to check for each module in your scope (do all of them)

A. **Spec coverage.** For each spec section (requirements FR-*, business rules BRU-*, automations
   AUT-*, data entities, KPIs, reports, integrations / cross-module contracts) → BUILT / PARTIAL /
   MISSING / WRONG, with file:line. Concentrate on what matters to a real business: pay,
   statutory duty, safety, approvals, data privacy, and what an auditor (ISO 9001, labour
   inspector, tax) would ask for.
B. **Data capture.** Every spec record can be created from a P03 screen with the fields that
   matter; required fields enforced; no form offers a field the model guards; picker domains
   sane; `cols` all exist on the model (the endpoint silently drops unknown columns); statutory
   registers (Form 6 worker register, Form 7 service book, Form 6(a)) and documents complete.
C. **Business flow & state machine.** Every state reachable through a real action; no dead ends;
   no transition skippable by a direct write/create; cancellation/reversal paths exist and undo
   their side effects; lifecycles join up (requisition → offer → hire → employee → contract →
   attendance → payroll → exit → settlement → access closed).
D. **Business rules & approvals.** DOFA tiers, SoD (requester ≠ approver ≠ subject; payroll
   preparer ≠ approver ≠ payer), approver groups actually held by someone on `fix_real_a09`
   (count holders per group), context-flag bypasses, sudo misuse, self-service limits.
E. **Calculations.** Gross-to-net, overtime (base and divisor, 2×), leave accrual and encashment,
   festival bonus, proration, provident fund / WPPF, gratuity, final settlement, income tax
   (slabs, minimum tax, exemptions, YTD), incentive bands and scores, compensation proposals,
   headcount and training budgets, injury compensation. Run them with real numbers and show the
   arithmetic; check rounding (BDT, 2 dp) and date boundaries.
F. **Accounting.** Every money event in your scope (salary, OT, bonus, allowances, PF employee /
   employer, WPPF, gratuity accrual, tax withheld, BEFTN/MFS payment, off-cycle, recovery,
   injury compensation, final settlement, training cost, recruitment cost) reaches the GL the
   estate's way (`fix.journal.posting.log` / `post_*_move` / `account.move` as used in the estate)
   with correct accounts ON THE REAL CHART, correct sign, branch / operating-unit / cost-centre
   dimensions, employee payable cleared, and reversal on cancel. Show the resulting journal
   lines. Money that stops at a status field with no ledger entry is P0. Also check hand-offs to
   M50 (payment execution, bank confirmation, returns) and M51 (tax return, challan).
G. **Cross-module links.** Each integration the spec names exists, fires (the event consumer has
   an `ir.cron` or is called in-process), and the consumer side does the right thing. A cron
   method with no `ir.cron` record never runs; a cron that runs as a Brussels-time user uses the
   wrong "today". Event contracts: `contracts\events` + `tooling\events\verify_event_registry.py`.
H. **Dashboards / KPIs / reports.** Formulas correct, company-scoped, record-rule-scoped, date
   range respected; no raw keys, no `false`, honest "—"; exports exist per the report-export
   standard (CSV / Excel / PDF / e-mail) and the numbers in them match the ORM.
I. **Security.** ACL rows, record rules (company isolation, own-or-direct-report, HR-only
   groups), portal access, guarded fields not writable from any form, identity values (NID, TIN,
   passport) never shown in clear, read logs.
J. **Statutory duty.** Registers, forms, notice clocks, filing calendars, retention, DIFE / NBR
   duties, minimum wage, working hours, weekly/festival holidays, maternity, accident reporting,
   safety committee, PPE.
K. **Professional documents.** Appointment letter, service book, service certificate, payslip
   (Bengali), tax certificate, salary register, bank file, statutory returns, Form 6/6(a)/28 and
   the rest: do they exist, are they complete and correct, do they render from the P03 screens,
   do they carry the company letterhead?
L. **Readiness on production data.** Measure on `fix_real_a09`: how many employees have an active
   contract, bank/routing, tax profile (TIN), branch, operating unit, cost centre, department,
   manager; how many role groups have real holders; which settings (ir.config_parameter keys the
   module reads) are at their default or off. List what must be true before the first real run.

## Output

Write your full findings to `C:\Users\DELL\AppData\Local\Temp\a09erp\<your id>\FINDINGS.md`:

1. a table per module with columns: **id** (e.g. M56-F7), **severity** (P0 money/legal/security
   broken; P1 core flow broken or bypassable; P2 rule/calc/report wrong; P3 polish),
   **category** (A–L), **finding** (one or two sentences), **evidence** (file:line + probe/test
   output path), **proposed fix** (concrete: which file/method, what to change), **files a fixer
   would touch**;
2. a **spec-coverage matrix** (A) with counts BUILT / PARTIAL / MISSING / WRONG per requirement
   family;
3. a **settings register**: every `ir.config_parameter` key the module reads, its live value on
   `fix_real_a09`, the code default, and whether the live value makes the rule operative;
4. **measured facts on fix_real_a09** (L): role holders per group, data readiness, chart accounts
   / account roles the module needs and whether they exist;
5. a **cross-area** section (links into and out of the module, which side is wrong);
6. **owner decisions** — each with your recommendation — and **adviser questions** (statutory
   figures you could not confirm).

Be exhaustive but don't pad: no style nits. Your final message (under ~900 words): counts by
severity, the P0/P1 list with one line each, the top owner decisions, and the path of
FINDINGS.md.
