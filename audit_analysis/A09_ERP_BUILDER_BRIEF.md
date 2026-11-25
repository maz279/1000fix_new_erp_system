# A09 ERP audit: builder brief (read all of it before touching code)

You are one builder stream fixing defects found by the A09 ERP audit of the People & Workforce
area (M21 Core HR, M22 Learning, M55 Attendance, M56 Payroll, M57 Performance, M58 Talent, M59 HSE)
of 1000 FiX Services Ltd's Odoo 19 estate. 1000 FiX does after-sales repair in Bangladesh, in BDT;
the business day is Asia/Dhaka (UTC+6); the weekend is Friday–Saturday; about 504 employees.
The lead integrates, commits and deploys. Nothing you do reaches a live database.

## Where
- **Worktree.** All streams and the lead share one worktree:
  `C:\software_project\software_project_14\1000 fix\a09erp-wt`.
  - Code root: `...\a09erp-wt\1000_fix_codebase` (called CODE below).
  - Specs: `...\a09erp-wt\1000fix_ERP_Module\03_Modules\H_People_and_Workforce\M*.md`.
- **Your test database** is named in your prompt. It is a clean copy at HEAD. pytest uses it through
  `FIX_TEST_DB`; you may `-u` YOUR modules on it. Never touch any other database.
- **fix_real reference.** `fix_real_a09` is a snapshot of production fix_real (real chart with
  legacy codes, real users, real branches). READ-ONLY probes only (end every script with
  `env.cr.rollback()`); never `-u` it, never commit to it.
- **Findings.** The auditors' findings are in `...\a09erp-wt\audit_analysis\evidence_a09_erp\`
  (`R1_M21_FINDINGS.md`, `R2_M22_FINDINGS.md`, `R4_M56_FINDINGS.md`, `R6_M58_FINDINGS.md`,
  `R9_UI_SEC_FINDINGS.md`, `R8_X_FINDINGS.md`, and the others as they land). Your prompt lists
  your finding ids. Read the full rows for your ids only, and **re-verify each one in code before
  you fix it** — auditors are sometimes wrong. A finding that does not hold up is NOT-A-DEFECT
  with evidence; do not "fix" it.

## Hard rules
1. **Edit only the files your prompt says you own.** Another stream or the lead owns everything
   else. If a fix needs a change elsewhere, do not make it: write it under "Needs from others".
2. **Never run** `git commit`, `git stash`, `git checkout`, branch or push. The lead commits.
   (`git status` needs `--ignore-submodules` in this worktree.)
3. **Leave alone** ports 8069/8090, the databases fix_real / fix_dev and other sessions' databases,
   and any process you did not start.
4. **Do not invent business data**: statutory rates, account codes that are not on the chart,
   approver appointments, retention periods, thresholds. If a fix needs a business figure, build
   the mechanism fail-closed and list the figure as OWNER with your recommended value. The one
   exception is where your prompt hands you a sourced statutory figure explicitly.
   - An account choice becomes an `ir.config_parameter` account role or a company account field
     whose default is an account that EXISTS on the fix_real chart with the right type.
5. **Tests.** Every fix ships with an executable test against the ORM (pytest `odoo_env` fixture,
   rolled back), never a source-text assertion.
   - Run access tests as a real non-superuser (`.with_user(user)`) with the cache cleared
     (`env.invalidate_all()`) and a fresh env: a superuser read prefetched into the cache hides
     ACL problems.
   - Then do a mutation check: re-introduce each defect and confirm a test goes red; build each
     test so only the new rule can refuse it.
6. **File format.** LF endings. Write files with the Write tool (shell heredocs that write code
   are blocked on this machine by a security hook).
7. **New model, field or P03 surface.** Bump the module's `__manifest__` version (patch digit)
   ONLY if your prompt makes you the owner of that manifest; add ACL rows; add a company-isolation
   `ir.rule` if it has company_id; declare P03 surfaces in `controllers/a09/m<NN>.py` with
   whitelisted actions only; a typed form field goes in the form's `fields` in
   `static/src/a09/m<NN>.js`. Do NOT regenerate `controllers/a09/writable.py` yourself (shared
   file): list the form fields you added or removed in your report; the lead regenerates it.
   A GUARDED field is never editable on a form (`readonly: true`).
8. **Guarded models.** A model that guards fields inherits `fix.guarded.mixin`, writes through
   `self._guarded().write(...)` and lists the field in `_fix_guarded_fields()`.
   `super(..., self._guarded()).create()` RETURNS records carrying the guard token — return
   `self.browse(records.ids)`.
9. **Business dates.** Use `fields.Date.context_today` / a Dhaka conversion, never `date.today()`
   or naive UTC midnights.
10. **Money reaches the ledger the estate's way**: `post_with_dimensions` /
    `fix.journal.posting.log` in `g_finance/cd_gl_ext`, with the operating-unit / branch /
    cost-centre dimensions, the real chart's accounts, and a reversal on cancel. Follow an
    existing working pattern; do not invent a parallel ledger. Show the journal lines in a test.
11. **Events.** An event someone must act on needs a consumer row (`fix.event.consumer`) or an
    in-process call; a cron method with no `ir.cron` record never runs. Write a `TestDeployment`
    test asserting your wiring exists.
12. **Peer sessions own nearby code.** Do not edit anything outside the files your prompt lists —
   in particular not `cd_p03_portal/controllers/p03_generic_api.py`, `form_fields.py`,
    `static/src/p03_workspace.js`, nor other areas' addons.
13. **Usage budget.** The account has a shared usage cap. Work economically: read only what you
    need (targeted greps and line ranges, not whole large files twice); do not re-run long
    suites more than once; stop when your list is done.

## How to run things
Use PowerShell (Git-Bash breaks PYTHONPATH for odoo-bin).
```powershell
$W = "C:\software_project\software_project_14\1000 fix\a09erp-wt\1000_fix_codebase"; Set-Location $W
$env:PYTHONPATH = $W; $env:TZ = "UTC"
# upgrade YOUR modules on YOUR db (after a change that adds fields/models/data):
.\.venv\Scripts\python.exe vendor/odoo/odoo-bin -c infra/odoo-conf/local.resolved.conf -d <DB> -u <mod1>,<mod2> --stop-after-init --no-http --log-level=warn > <your scratch>\up.log 2>&1
#   (Odoo exits 0 even when the registry fails to load: always grep up.log for ERROR|CRITICAL|Traceback)
# read-only probe:
Get-Content <probe.py> | .\.venv\Scripts\python.exe vendor/odoo/odoo-bin shell -c infra/odoo-conf/local.resolved.conf -d fix_real_a09 --no-http --log-level=warn
# tests (do NOT add another -q: pyproject already has one and a second hides the summary line):
$env:FIX_TEST_DB = "<DB>"; .\.venv\Scripts\python.exe -m pytest <paths> -p no:cacheprovider > <your scratch>\pytest.log 2>&1
```
- Your scratch folder is named in your prompt; it is the only place outside the worktree you write.
- Machine is shared and slow: one Odoo process of your own at a time; read the pytest summary
  line from the log; never pipe pytest into `head`.
- If a registry load fails with "column ... does not exist" for a module you do not own, `-u`
  that module on YOUR db too.
- Fixtures: reuse the company's existing `fix.entity`; `res.partner` has no `mobile`;
  a test that depends on config params sets them itself; creating a user who is also an employee
  may trigger the joiner event — use `with_context(tracking_disable=True)` where the estate does.

## Report back (final message, under ~1,200 words)
For each finding id: **FIXED** (what changed, file:line, test name) · **OWNER** (the decision and
your recommended value) · **NOT-A-DEFECT** (evidence) · **DEFERRED** (why).
Also: test counts (new tests, mutation results, the module suites before vs after), every file you
changed, "Needs from others", the form fields added/removed (for the whitelist), the manifests you
bumped and the modules the lead must `-u` on deploy.
