# A04 ERP audit: builder brief (read all of it before touching code)

You are one of five builder streams fixing defects found by the A04 ERP audit of the
Commercial, Pricing & Revenue area of 1000 FiX Services Ltd's Odoo 19 estate. 1000 FiX does
after-sales repair in Bangladesh, in BDT, with 15% VAT; the business day is Asia/Dhaka.
The lead integrates, commits and deploys.

The audit findings, with probe evidence, are in `audit_analysis/evidence_a04_erp/R1..R5_*.md`
in the worktree. Your prompt lists your finding ids. Read the full rows for your ids, and
re-verify each one in code before you fix it, because auditors are sometimes wrong. A finding
that does not hold up is NOT-A-DEFECT with evidence.

## Where
- **Worktree.** All streams and the lead share one worktree:
  `C:\software_project\software_project_14\1000 fix\a04erp-wt`.
  - Code root: `...\a04erp-wt\1000_fix_codebase` (called CODE below).
  - Specs: `...\a04erp-wt\1000fix_ERP_Module\03_Modules\C_Commercial_Pricing_and_Revenue\M*.md`.
- **Your test database** is a clean test template at HEAD, named in your prompt. pytest uses it,
  and its seed event backlog is already marked relayed.
- **fix_real reference.** `fix_real_a04` is a copy of production fix_real: the 376-account
  legacy chart, AR control 100201, 73 branches with their own OUs, and real users. You may
  run READ-ONLY probes on it (end every script with `env.cr.rollback()`) to check accounts,
  params and role holders. Never `-u` it, and never commit to it.
- **Disk is nearly full (about 24 GB free).** Do not create, clone or restore any database.

## Hard rules
1. **Edit only the files your prompt says you own.** Another stream or the lead owns
   everything else. If a fix needs a change elsewhere, don't make it: write it under
   "Needs from others" in your report.
2. **Never run** `git commit`, `git stash`, `git checkout`, branch or push. The lead commits.
3. **Leave alone** ports 8069/8089/8090, the databases fix_real, fix_dev and other sessions'
   databases, and any process you did not start. Never `-u` a DB other than your own.
4. **Don't fabricate business data:** prices, statutory rates, account codes that are not in
   the chart, approver appointments, gateway secrets.
   - If a fix needs a business figure, build the mechanism fail-closed and list it as OWNER.
   - An account choice becomes an `ir.config_parameter` account role. Its default should be an
     account that EXISTS on the fix_real chart, with the right type. Name the recommended code,
     and the owner confirms it.
5. **Tests.** Every fix ships with an executable test against the ORM (the pytest `odoo_env`
   fixture, rolled back), never a source-text assertion.
   - Run the test as a real non-superuser where access matters: `.with_user(user)`, plus a
     fresh env for ACL checks. A sudo read can prefetch the record and hide an ACL problem.
   - Then do a mutation check: re-introduce each defect and confirm a test goes red. Build
     each test so ONLY the new rule can refuse it.
6. **File format.** Write files with LF endings. Write test files with the Write tool,
   because heredocs mangle "\n".
7. **New model, field or P03 surface.**
   - Bump that module's `__manifest__` version (patch digit) and add ACL rows. Add a
     company-isolation `ir.rule` if it has company_id.
   - Declare the surface in `controllers/a04/m<NN>.py`, with whitelisted actions only.
   - A P03 form field the user types goes in the form's `fields` in `static/src/a04/m<NN>.js`.
     Then regenerate the whitelist:
     `python addons/platform/cd_p03_portal/controllers/form_fields.py --a04`
     (add `--a08` only if you changed an a08 fragment).
   - A GUARDED field must never be editable on a form: mark it `readonly: true`.
   - A model that guards fields inherits `fix.guarded.mixin`, writes via `self._guarded().write(...)`,
     and lists the field in `_fix_guarded_fields()`.
   - Creating via `super(..., self._guarded()).create()` RETURNS records that carry the guard
     token, so return `self.browse(records.ids)`.
8. **Business dates.** The business day is Asia/Dhaka (UTC+6). Use `fields.Date.context_today` or
   a Dhaka conversion, never `date.today()` or naive UTC midnights.
9. **Report packs and KPIs** in `controllers/a04/m<NN>.py` must read through
   `controllers/a04/_scope.py`. Use `scoped(env, model, domain, date_field, date_from, date_to)`
   instead of `env[model].sudo().search([...])`, so each pack honours the caller's companies
   and the requested period. Pick the business date field of each pack. A KPI exception must
   be logged, not swallowed silently.
10. **Money must reach the ledger the estate's way:**
    - customer documents go through M20 (`fix.ar.invoice` / `fix.ar.receipt` / credit notes in
      cd_billing_engine);
    - supplier or partner payouts go through M53/M50 (`fix.payment.execution` /
      settlement ledger);
    - GL is fix.gl / account.move as already used.
    Follow an existing working pattern in the estate; don't invent a parallel ledger. Show the
    resulting journal lines in a test (account codes, debit/credit, tax line, OU).
11. **Events.** An event someone must act on needs a consumer. Use a literal event name, and
    put a consumer row in the module's data, following the existing `fix.event.consumer`
    pattern. A cron method with no `ir.cron` record never runs. Write a `TestDeployment`
    test asserting your wiring exists: cron, consumer, ACL, surface.
12. **Peer sessions own nearby code.** Do not edit these functions:
    - **A05 session:**
      - the refurbished-unit checkout re-check in `cd_storefront/models/fix_storefront.py`
        (graded stock state, wipe, NEIR);
      - the refurbished return path in `cd_storefront/models/fix_storefront_refund.py`;
      - `action_list_refurb_resale` and the refurbished sale in `cd_marketplace/models/fix_marketplace.py`;
      - the COGS leg in `cd_storefront_finance/models/fix_storefront_books.py`;
      - "no zero VAT line" and rental deferral in cd_billing_engine.
    - **A02 session:** the M01 estimate → invoice equality. Keep estimate lines
      `quantity × unit_price` so `_fix_assert_matches_accepted_quotation` and
      `fix_order_settlement.py` still hold.

## The M11 price service (stream B1 builds it; everyone else calls it)
B1 creates this API first (within its first hour) in cd_rate_card. Other streams code against
this exact signature:
```python
env["fix.rate.card"].price_for(
    product,                 # product.product | product.template | fix.catalogue.item | str code
    partner=None,            # res.partner (customer); tier/contract precedence read from it
    channel="quotation",     # 'service' (M01), 'quotation' (M36), 'storefront' (M38),
                             # 'marketplace' (M12), 'contract' (M08), 'subscription' (M39), 'reseller' (M40)
    qty=1.0, date=None, company=None, contract=None, currency=None,
)
# -> dict:
#   price      float | None   VAT-EXCLUSIVE unit price in BDT; None = no released price
#   source     str            'contract' | 'customer' | 'tier' | 'card' | 'promotion' | ...
#   card_id    int | False
#   floor      float          the minimum allowed unit price (price floor / cost margin floor)
#   cost       float          M15 average cost when known, else 0.0
#   reason     str            why price is None
env["fix.rate.card"].check_sale_price(product, unit_price, channel, partner=None, date=None,
                                      company=None, override=None)
# raises UserError when unit_price is below the floor and no single-use approved override
# is bound to this line
```
Channels that face customers (`storefront`, `marketplace`) refuse a line whose price is None.
Read the B1 code once it exists; the docstring is authoritative if it differs.

## How to run things
Use PowerShell. Git Bash breaks PYTHONPATH for odoo-bin.
```
$W = "C:\software_project\software_project_14\1000 fix\a04erp-wt\1000_fix_codebase"; Set-Location $W
$env:PYTHONPATH = $W; $env:TZ = "UTC"
# upgrade YOUR modules on YOUR db (after code changes that add fields/models/data):
.\.venv\Scripts\python.exe vendor/odoo/odoo-bin -c infra/odoo-conf/local.resolved.conf -d <DB> -u <mod1>,<mod2> --stop-after-init --no-http --log-level=warn
# tests (each test is rolled back):
$env:FIX_TEST_DB = "<DB>"; .\.venv\Scripts\python.exe -m pytest <paths> -p no:cacheprovider -q > <your scratch>\pytest.log 2>&1
```
- Your scratch folder is `C:\Users\DELL\AppData\Local\Temp\a04erp\<stream>\`. Use it only.
- Never pipe pytest into `head`. Run long suites in the background and read the log.
- **Shared worktree trap.** Other streams' new model fields are in the code but not in YOUR
  database until their modules are upgraded on it. If a registry load fails with "column
  ... does not exist" for a module you don't own, `-u` that module on your DB too. That is
  allowed on your own DB.
- **Fixtures:**
  - a fixture that creates a `fix.entity` must reuse the company's existing entity;
  - `res.partner` has no `mobile` field;
  - a test that depends on config params must set them itself.

## Report back (final message, under ~1,500 words)
For each finding id, give one of:
- **FIXED:** what changed, file:line, and the test name;
- **OWNER:** the decision needed, and the recommended value;
- **NOT-A-DEFECT:** the evidence;
- **DEFERRED:** why.

Also include:
- test counts: your new tests, mutation results, and your modules' existing suites before vs after;
- every file you changed;
- "Needs from others";
- the manifest versions you bumped, and the modules the lead must `-u` on deploy.

Your report is returned as text; you cannot write report files outside your scratch folder.
