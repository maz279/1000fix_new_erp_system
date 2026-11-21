# A06 ERP audit - builder brief (read fully before touching code)

You are one of five builder streams fixing defects found by the A06 Supply Chain ERP audit of
1000 FiX Services Ltd's Odoo 19 estate (after-sales repair, Bangladesh; ~73 branches, central and
brand warehouses, field vans). The lead integrates, commits, deploys. Read first:
- `audit_analysis/A06_ERP_AUDIT_LEDGER_2026-11-20.md` - every finding with file:line evidence and,
  at the top, the OWNER DECISIONS D1-D8 and the lead's defaults. They are binding.
- the specs `1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M1x_*.md` for your modules.
Finding ids: money X01-X37, M15 A01-A38, M41 F01-F32, M16/M42 F01-F45 (call them P01-P45 in your
report to avoid clashing with M41), M43-01..23, M44-01..27.

## Where
- Your OWN git worktree (named in your prompt), branch `fix/a06-<stream>`; code root
  `<worktree>\1000_fix_codebase` (CODE). The lead merges the five branches. You may `git add` and
  `git commit` on YOUR branch only (small commits, conventional messages, e.g.
  `fix(CD-M15-01): ...`, ending with the line `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`).
  Never push, never rebase, never touch another branch or worktree, never `git stash`.
  Commits run the pre-commit hook; never `--no-verify`. If `pre-commit.exe` is blocked (Smart App
  Control), the hook falls back to `python -m pre_commit` by itself.
- Your OWN databases (named in your prompt):
  - a test DB (clone of the upgraded test template) for pytest;
  - a copy of production fix_real (real 376-account legacy chart, 603 warehouses, 17,461 on-hand
    lines, BDT 165.26M stock, 3 companies, 0 POs/receipts/transfers) for realistic probes.
- Postgres 127.0.0.1:5433, user `fix`, password `change-me-dev-only` (docker container
  `compose-postgres-1`).

## Hard rules
1. Edit only the files your prompt says you own. If a fix needs a change elsewhere, make the smallest
   possible clearly-commented hunk ONLY where your prompt allows it; otherwise write it under
   "Needs from others" in your report. Shared files (a module's `__manifest__.py` version/data list,
   `security/ir.model.access.csv`, data xml) - you may append your own lines; the lead resolves merges.
   `cd_p03_portal/controllers/a06/writable.py` is GENERATED: never hand-edit; the lead regenerates it.
2. Never touch ports 8069/8089/8090 or the databases fix_real / fix_dev / fix_a06real / fix_test_a06,
   never stop a process you did not start, never run -u on a DB other than yours.
3. Don't fabricate business data (rates, account codes not in the chart, approver appointments, costs).
   Account codes come from D2/D5/D6 (all exist in fix_real's chart). If a fix needs a figure nobody gave,
   build it fail-closed behind an `ir.config_parameter` and list it as OWNER.
4. Every fix ships with an executable test against the ORM (pytest `odoo_env` fixture, rolled back),
   never a source-text assertion. First make the test reproduce the defect (red on the base code), then
   fix (green). Then a mutation check: re-introduce each defect and confirm a test goes red; build the
   test so ONLY the new rule can refuse it (an older control refusing first hides a dead rule).
5. Write files with LF endings, using the Write/Edit tools (bash heredocs mangle "\n").
6. A new model / field / P03 surface: bump that module's `__manifest__` version (patch digit), add ACL rows,
   record rules for company scoping. A model that guards fields inherits `fix.guarded.mixin`, writes via
   `self._guarded().write(...)`, and lists the field in `_fix_guarded_fields()`. Never let a P03 form write
   a state, stamp, approver or amount-derived field.
7. Dates: the business day is Asia/Dhaka (UTC+6). Use `fields.Date.context_today` or a Dhaka conversion,
   never `date.today()` / naive UTC midnight in anything business-dated.
8. P03 reports/KPIs: filter `("company_id", "in", env.companies.ids)` where the model has company_id, and
   honour `date_from`/`date_to`. Every report keeps its CSV/Excel/PDF/Email bar.
9. A cron method needs an `ir.cron` record; an event consumer needs its consumer record; both need a
   deployment test asserting the wiring exists (a unit test calling the method directly proves nothing
   about whether it runs).
10. A new field's DEFAULT is applied to every existing row on upgrade - check it against your constraints
    and against fix_real data (run `-u` on your fix_real copy, 0 errors).
11. Money: amounts in company currency are rounded to 0.01; a posting is balanced or refused; every
    journal line carries the branch's operating unit (cd_gl_ext `post_with_dimensions` /
    `_attach_dimensions` - never the company's first OU).

## How to run things (PowerShell; Git Bash breaks PYTHONPATH for odoo-bin)
```
$W = "<worktree>\1000_fix_codebase"; Set-Location $W; $env:PYTHONPATH = $W
# upgrade your modules on YOUR db:
.\.venv\Scripts\python.exe vendor/odoo/odoo-bin -c infra/odoo-conf/local.resolved.conf -d <DB> -u <mod1>,<mod2> --stop-after-init --no-http --log-level=warn
# tests (rolled back per test):
$env:FIX_TEST_DB = "<DB>"; $env:PGPORT="5433"; .\.venv\Scripts\python.exe -m pytest <paths> -p no:cacheprovider -q --junitxml=<scratch>\junit.xml *> <scratch>\pytest.log
```
The conftest prints no summary line: read the junit xml. Never pipe pytest into `head`. Long runs: run
in the background and read the log. Fixture traps: a fixture creating a `fix.entity` for the company must
reuse the company's existing entity; `res.partner` has no `mobile` field; tests that read config params
must set the params they depend on. Between 00:00 and 06:00 Dhaka, tests using UTC "today" disagree
with Dhaka-day code. `sudo()` keeps `env.uid`: to prove code runs as the user assert `not env.su`.
A `rec.sudo().field` read prefetches into a cache that later non-sudo reads may hit: only a mutation that
restores the original code proves an ACL claim.
Static P03 guards: load the m1x.js fragments the way existing tests in `cd_p03_portal/tests/` do
(e.g. `test_m41_capture_pass2.py`, `test_a06_final_m16.py`). Every list column / form field / grid column
must exist on its model; every button must be a SURFACES action that exists.

## Report back (final message, under ~1,500 words; you may not be able to write report files - put it in
the message)
Per finding id: FIXED (what, file:line, test name) / OWNER (what figure is missing) / NOT-A-DEFECT
(evidence) / DEFERRED (why - only for genuinely large new features; P0/P1 may not be deferred).
Test counts: your new tests, mutation results (n/m red), the existing suites of your modules before vs
after (both on your test DB). Commits on your branch (hash + subject). Files changed. "Needs from others".
Manifest versions bumped. Anything you need the lead to do at deploy (params to set, data repairs).
