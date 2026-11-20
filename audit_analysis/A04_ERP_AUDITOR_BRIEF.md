# A04 ERP audit — auditor brief (read fully before starting)

You are one of five READ-ONLY auditors of the A04 "Commercial, Pricing & Revenue" area of
1000 FiX Services Ltd's Odoo 19 ERP (after-sales repair, Bangladesh; currency BDT, VAT 15%,
business day Asia/Dhaka UTC+6). The owner's goal: every A04 module must work as a top-class
ERP — data-capture forms, functions, dashboards/KPIs, approval flows, business flows, business
rules, calculations, accounting logic, professional exports — and every cross-relation with
other modules (same area and other areas) must be correct. Find every gap, error and mistake,
with evidence. A lead session will turn your findings into fixes.

## Where
- Worktree (code at origin HEAD d0589b7b): `C:\software_project\software_project_14\1000 fix\a04erp-wt`
  - code root `...\a04erp-wt\1000_fix_codebase` (call it CODE)
  - module specs: `...\a04erp-wt\1000fix_ERP_Module\03_Modules\C_Commercial_Pricing_and_Revenue\M*.md`
    and `_CATEGORY_OVERVIEW.md` (the commercial chain, who owns what)
  - other areas' specs: `...\1000fix_ERP_Module\03_Modules\<A..K>_*\M*.md`
  - P03 workspace screens: `CODE\addons\platform\cd_p03_portal\static\src\a04\m*.js`,
    served surfaces `CODE\addons\platform\cd_p03_portal\controllers\a04\m*.py` (+ `writable.py`
    whitelist of form-editable fields), engine `static/src/p03_workspace.js`, report packs and
    KPIs under `cd_p03_portal/controllers/` (grep the module id, e.g. `M36`).
  - addons: M08 cd_contract_core, M09 cd_warranty_claims, M11 cd_rate_card + cd_dynamic_pricing,
    M12 cd_marketplace, M36 cd_quotation, M37 cd_catalogue, M38 cd_storefront (+ cd_storefront_finance),
    M39 cd_subscription, M40 cd_partner. Bridges into finance live in g_finance addons
    (cd_billing_engine, cd_ar*, cd_gl_ext, ...): grep for the A04 model names.
  - Earlier A04 audit (3-5 Nov, approval/workflow controls, mostly fixed since):
    `C:\software_project\software_project_14\working\A04_Workflow_and_Approval_Report.md`.
    The A02 ERP audit you should imitate in depth: `...\a04erp-wt\audit_analysis\A02_ERP_AUDIT_REPORT_2026-11-20.md`
    and `A02_ERP_AUDIT_LEDGER_2026-11-19.md` (its P0s were money that never reached the ledger).
- Databases (Postgres on 127.0.0.1:5433 in docker `compose-postgres-1`):
  - `fix_real_a04` = copy of production fix_real (real 376-account legacy chart: AR control 100201,
    AP control 200101; 73 branches each with its own operating unit; real users/roles; few
    transactions). Use it to measure real configuration and to run money probes.
  - `fix_test_a04erp` = clean test template upgraded to HEAD (pytest uses it).
  - Both may still be building when you start. Before your first probe check
    `docker exec compose-postgres-1 sh -c 'psql -U "$POSTGRES_USER" -d fix_real_a04 -Atc "select count(*) from res_users"'`
    answers a number, and for fix_test_a04erp that `ir_module_module` has no row in state 'to upgrade'.
    Meanwhile read specs and code.

## How to probe (PowerShell; Git-Bash breaks PYTHONPATH for odoo-bin)
```
$W = "C:\software_project\software_project_14\1000 fix\a04erp-wt\1000_fix_codebase"; Set-Location $W
$env:PYTHONPATH = $W; $env:TZ = "UTC"
Get-Content <your_probe.py> | .\.venv\Scripts\python.exe vendor/odoo/odoo-bin shell -c infra/odoo-conf/local.resolved.conf -d fix_real_a04 --no-http --log-level=warn
```
Every probe script MUST end with `env.cr.rollback()` and must never commit. Run probes as a real
non-superuser where access matters (`env(user=<uid>)` with su=False, e.g. `env['x'].with_user(u)`),
because the superuser bypasses the guards you are testing. Put your scripts and outputs ONLY in your
own folder: `C:\Users\DELL\AppData\Local\Temp\a04erp\<your id>\`. For a SQL count use the docker psql
line above. pytest is also allowed: `$env:FIX_TEST_DB="fix_test_a04erp"; .\.venv\Scripts\python.exe -m pytest <path> -p no:cacheprovider -q > <your folder>\x.log 2>&1`
(never pipe pytest into head).

## Hard rules
1. READ-ONLY on code: do not edit, create or delete any file under the worktree or any checkout.
   Never git commit/stash/checkout/branch/push. Write only inside your own temp folder.
2. Never touch ports 8069/8089/8090, the databases fix_real / fix_dev, or any process you did not start.
   Never `-u`/`-i` any database. Never commit a transaction.
3. Evidence standard: a finding needs file:line AND, wherever possible, executable proof (a probe
   output or a failing test against the ORM). "The source says X" alone is weak; mark such
   findings [STATIC]. Re-check any claim about live data with a direct query before citing it.
   A sudo read can prefetch into the cache and hide an ACL problem: prove access findings with
   a fresh env as the real user.
4. Don't report what is out of A04's ownership as an A04 defect, but DO report broken
   cross-relations (A04 <-> M01 orders, M15 stock, M16/M19 procurement/AP, M20 AR, M33 party/credit,
   M50 GL, M51 tax, M27 notifications, M63 approvals/DOFA, M05 MSP, M41 demand, etc.) with which side
   is wrong.

## What to check for each module in your scope (do all of them)
A. Spec coverage: for each spec section (requirements FR-*, business rules BRU-*, automations AUT-*,
   data entities, KPIs, reports, integrations/cross-module contracts) -> BUILT / PARTIAL / MISSING /
   WRONG, with file:line. Concentrate on what matters to a real business: money, approvals,
   statutory, customer-facing correctness.
B. Data capture: every spec record can be created from a P03 screen with the fields that matter;
   required fields enforced; no form offers a field the model guards; picker domains sane;
   `cols` all exist on the model (the endpoint silently drops unknown columns).
C. Business flow & state machine: every state reachable through a real action; no dead ends;
   no transition skippable by a direct write/create; cancellation/reversal paths exist and undo
   their side effects.
D. Business rules & approvals: DOFA tiers, SoD (requester != approver), approver groups actually
   held by someone on fix_real_a04 (count holders), context-flag bypasses, sudo misuse,
   portal/share users unable to set commercial fields.
E. Calculations: prices, discounts, VAT (15% / inclusive vs exclusive), rounding (BDT, 2 dp),
   proration, commission, MRR/ARR, claim recovery amounts, tender scoring. Run them with real numbers.
F. Accounting: every money event in your scope (invoice, receipt, refund, credit note, commission,
   payout, claim recovery, deferred revenue, COGS, write-off) reaches M20/M19 sub-ledgers and the GL
   (fix.gl / account.move as used in this estate) with correct accounts ON THE fix_real CHART,
   correct sign, branch/OU dimension, tax line, and reversal on cancel. Run an end-to-end money
   probe on fix_real_a04 (rolled back) and show the resulting journal lines. Money that stops at a
   status field with no ledger entry is P0.
G. Cross-module links: each integration the spec names exists, fires (event consumer has an ir.cron
   or is called), and the consumer side does the right thing. A cron method with no ir.cron record
   never runs.
H. Dashboards/KPIs/reports: formulas correct, company-scoped (`company_id in env.companies.ids`),
   date-range respected, no cross-company leakage; exports exist per the report-export standard
   (CSV/Excel/PDF/Email) and the numbers in them match the ORM.
I. Security: ACL rows, record rules (company isolation), portal access.

## Output
Write your full findings to `C:\Users\DELL\AppData\Local\Temp\a04erp\<your id>\FINDINGS.md`:
a table per module with columns: id (e.g. M36-F7), severity (P0 money/legal/security broken,
P1 core flow broken or bypassable, P2 rule/calc/report wrong, P3 polish), category (A-I),
finding (one or two sentences), evidence (file:line + probe/test output path), proposed fix
(concrete: which file/method, what to change), files a fixer would touch. Then a "cross-area"
section, and a "measured facts on fix_real_a04" section (role holders, config params, account
codes that exist/do not exist). Be exhaustive but don't pad: no style nits.
Your final message (under ~900 words): counts by severity, the P0/P1 list with one line each,
and the path of FINDINGS.md.
