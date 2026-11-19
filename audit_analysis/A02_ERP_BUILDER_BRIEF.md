# A02 ERP audit — builder brief (read fully before touching code)

You are one of four builder streams fixing defects found by the A02 ERP audit of
1000 FiX Services Ltd's Odoo 19 estate (after-sales repair, Bangladesh). The
lead integrates, commits and deploys. Ledger of all findings:
`audit_analysis/A02_ERP_AUDIT_LEDGER_2026-11-19.md`.

## Where
- Worktree (shared by all streams + the lead): `C:\software_project\software_project_14\1000 fix\a02erp-wt`
  - code root `...\a02erp-wt\1000_fix_codebase` (call it CODE)
  - specs `...\a02erp-wt\1000fix_ERP_Module\03_Modules\A_Service_Delivery_and_Operations\M0x_*.md`
- Your own database (a copy of production fix_real: real 376-account chart, AR control 100201,
  73 branches each with its own operating unit, 0 transactions): named in your prompt.
  It may still be restoring when you start: before your first upgrade, check
  `docker exec compose-postgres-1 sh -c 'psql -U "$POSTGRES_USER" -d <DB> -Atc "select count(*) from fix_service_order"'`
  answers a number (not an error).

## Hard rules
1. Edit ONLY the files your prompt says you own. Another stream or the lead owns everything else. If a fix
   needs a change elsewhere, do not make it: write it under "Needs from others" in your report.
2. Never `git commit`, `git stash`, `git checkout`, branch or push. The lead commits.
3. Never touch ports 8069/8089/8090 or the databases fix_real / fix_dev, and never stop any process you did
   not start. Never run -u on a DB other than yours.
4. Don't fabricate business data (statutory rates, account codes that do not exist in the chart, approver
   appointments). If a fix needs a business figure, build the mechanism fail-closed and list it as OWNER.
5. Every fix ships with an executable test against the ORM (pytest `odoo_env` fixture, rolled back), never a
   source-text assertion. Then a mutation check: re-introduce each defect and confirm a test goes red.
6. Write files with LF endings. A test file you write must be written with the Write tool (heredocs mangle "\n").
7. A new model / field / P03 surface: bump that module's `__manifest__` version (patch digit), add ACL rows,
   and if a P03 form writes it, add the field to the module's block in
   `addons/platform/cd_p03_portal/controllers/a02/writable.py` (only your module's block). Any guarded field
   must stay OUT of writable.py. A model that guards fields inherits `fix.guarded.mixin` and writes via
   `self._guarded().write(...)`; a guarded field must be in `_fix_guarded_fields()`.
8. A model's own write() refusal must let guarded fields reach the mixin (`test_a02_control_suite` expects
   "changes only through its workflow").
9. Dates: the business day is Asia/Dhaka (UTC+6). Use `fields.Date.context_today` / a Dhaka conversion,
   never `date.today()` or naive UTC midnights, in anything business-dated.
10. P03 reports/KPIs read with sudo: always add `("company_id", "in", env.companies.ids)` (where the model
    has company_id) and respect date_from/date_to.

## How to run things (PowerShell; Git-Bash breaks PYTHONPATH for odoo-bin)
```
$W = "C:\software_project\software_project_14\1000 fix\a02erp-wt\1000_fix_codebase"; Set-Location $W; $env:PYTHONPATH = $W
# upgrade your modules on YOUR db (after code changes that add fields/models/data):
.\.venv\Scripts\python.exe vendor/odoo/odoo-bin -c infra/odoo-conf/local.resolved.conf -d <DB> -u <mod1>,<mod2> --stop-after-init --no-http --log-level=warn
# tests (rolled back per test):
$env:FIX_TEST_DB = "<DB>"; .\.venv\Scripts\python.exe -m pytest <paths> -p no:cacheprovider -q --junitxml=<scratch>\junit.xml > <scratch>\pytest.log 2>&1
```
Never pipe pytest into `head` (SIGPIPE kills it). Long suites: run in background and read the log.
Fixture traps: a fixture that creates a `fix.entity` for the company must reuse the company's existing entity
(`fix_entity_company_unique`). `res.partner` has no `mobile` field. Tests that read config params must set the
params they depend on (the DB is a production copy with real settings).

## Report back (final message, under ~1,200 words)
Per finding id: FIXED (what, file:line, test name) / OWNER (what decision) / NOT-A-DEFECT (evidence) /
DEFERRED (why). Test counts (your new tests, mutation results, the existing suites of your modules
before vs after). List every file you changed. "Needs from others". Manifest versions bumped.
