# M19 Financial Accounting & GL: data-capture audit, second pass

**Date:** 19 Nov 2026 · **Estate:** fix_real on port 8069 (fix_dev on 8090) · **Branch:** `fix/m19-capture-pass2` · **Status:** see §7

## 1. The question

The user again saw M19 sub-module pages "without a relevant data capture button". The 13 Nov pass ([M19_CAPTURE_BUTTON_AUDIT_2026-11-13.md](M19_CAPTURE_BUTTON_AUDIT_2026-11-13.md)) wired the forms that already existed. It also left two pages with no "+ New" and listed five spec records that had no model. This pass checks each page against the spec record it should capture, and builds the missing records.

## 2. Method

1. **Spec:** `1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M19_Financial_Accounting_and_General_Ledger.md`. That is FR-FIN-001…046 (§5), the posting-rule lifecycle (§8.3), BRU-FIN-11…26 (§9) and the 27 owned entities (§10.1).
2. **Code, as the user sees it:** the workspace's own page rule (`fregCreate` / `fregPanels` in `p03_workspace.js`), **executed in node** over the real merged registry (the `test_m19_capture_buttons.py` probe). It lists every page's "+ New" and chips.
3. **Model inventory:** every `_name` in `cd_gl_ext`, `cd_multi_entity` and the finance modules was matched to the spec's §10.1 entities. Each workspace screen was checked for a capture of each entity.
4. **Live data (read-only):** counts on fix_real and fix_dev.

## 3. Findings (HEAD fdc8fef7)

| # | Page | What the page offered | What the spec requires, missing |
|---|---|---|---|
| **3** | Subledger Posting Engine | **No "+ New", no chip** | FR-FIN-008/009/010 (P0), BRU-FIN-17/18 (H): **versioned posting rules**, tested against fixtures, approved by the CFO or a delegate, never edited in place. Each entry should name the rule version that produced it. No model existed. |
| **8** | Audit & Retention | **No "+ New"**; only the M24 Retention Policy chip, which administrators alone can save | FR-FIN-043, BRU-FIN-26 (H): **external auditor access**, read-only, time-limited, limited to nominated entities and periods, and logged. No model existed. |
| 6 | Multi-Currency | "+ FX Revaluation Run" | FR-FIN-033 (P0): **dated rate tables by type** (spot/average/closing/statutory) with approved overrides. **No workspace screen could enter a rate**, but the revaluation refuses to run without an official closing rate (`_closing_rate`). fix_real holds only demo rates dated 2010-01-01, so page 6's own button could never complete a run. |
| 1 | CoA & Dimensions | "+ Chart of Accounts Account" and its chips | FR-FIN-004 (P0), BRU-FIN-22 (H): **dimension cross-validation rules**, rejected at posting on every path. There was no model, so nothing enforced the rule. |
| 4 | Fiscal Calendar & Close | "+ Period Close", reopen request | FR-FIN-018 (P0), BRU-FIN-19 (H): the **July–June fiscal year**. No screen created a fiscal year, and nothing refused another span. fix_real has 0 fiscal years and its company year ends on **31 December**. |
| 2, 5, 7, 9–12 | | correct for their spec records | |

Not built in this pass (§6): bulk journal import (FR-FIN-014, P1), reporting hierarchies (FR-FIN-005, P1), chart versioning (FR-FIN-007, P1).

## 4. What was built

`cd_gl_ext` 19.0.2.5.0, new file `models/fix_gl_capture.py` (imported last):

| Page | Record | Rules it enforces |
|---|---|---|
| 3 | `fix.gl.posting.rule` (+ `.line`, `.fixture`): source, version, effective date; debit/credit lines with shares; fixtures = expected lines per sample amount | **Draft → Tested → Active → Superseded** (§8.3). Test requires a debit and credit side each summing to 100% and ≥1 fixture, and every fixture case must reproduce exactly. Approval is by an Accounting Administrator who neither created nor last changed it, and the fixtures are re-run at approval (BRU-FIN-17). A tested rule, its lines and its fixtures are **never edited**. "Draft a New Version" copies it (BRU-FIN-18), and approval supersedes the previous version, which is kept and cannot be deleted. **Engine:** `post_with_dimensions` and `post_existing_moves` find the version in force for the source on the entry date. While one exists, a line on an account the rule does not post to is refused. The posting log records `posting_rule_id` (FR-FIN-010). Manual journals are not a rule source. |
| 8 | `fix.auditor.access.grant`: login, firm, engagement letter, entities, audited period, access window | The window is at most 90 days (`cd_gl_ext.auditor_access_max_days`). It is granted by an Accounting Administrator other than the requester. The login must be internal, hold **no group that can change the books** (billing/accountant/adviser/admin), and have no company outside the grant. Granting adds the new **`group_external_auditor`** (implies Accounting read-only). Its record rules limit journal entries and items to the **granted entities and audited period**. It is frozen once granted. **Lapses by itself** (hourly job) or on revocation, which removes the group. Sign-ins in the window are counted from the login log. |
| 6 | `fix.currency.rate.entry`: currency, type (spot/closing/average/statutory), date, BDT per unit, source (Bangladesh Bank / treasury / manual override + reason) | Entered → submitted (frozen) → approved by an Accounting Administrator other than the entrant. There is one approved rate per currency/type/day. An approved **spot or closing** rate is written to the ledger rate table (`res.currency.rate`, exact via `inverse_company_rate`), which the FX revaluation and every conversion read. A closing rate wins over a spot rate of the same day. Average and statutory rates are kept for reporting. |
| 1 | `fix.gl.crossvalidation.rule`: account-code prefix, dimension, effect (must not carry / must carry one of), values | Activated by an Accounting Administrator who did not write it, and frozen once active (retire and rewrite). **Checked inside `_validate_move_against_chart`**, so every path is covered: manual draft, routing, template, allocation, sub-ledger and API. It applies whether or not the statutory chart is linked (fix_real has no linked chart). |
| 4 | `account.fiscal.year` (OCA) | Constraint: **1 July to 30 June** (BRU-FIN-19), on every path. |

Workspace (`cd_p03_portal`):
- `a08/m19.js` adds 5 lists, 5 forms (the posting rule has a lines grid and a fixtures grid) and 5 chips. It also changes the page mappings: page 3's record is the posting rule, page 8's is the auditor grant, and page 6's is the exchange rate (with the revaluation as a chip).
- `controllers/a08/m19.py` serves the five models and their workflow actions.
- `writable.py` was regenerated. No workflow field is writable.

### Pages now

| # | Page | "+ New" | Chips |
|---|---|---|---|
| 1 | CoA & Dimensions | + Chart of Accounts Account | Account, **Cross-Validation Rule**, Control Account Change, Chart Loader |
| 2 | Journals | + Journal Entry (editor) | Journal Entry, Partner-Ledger Take-on |
| 3 | Subledger Posting Engine | **+ Posting Rule** | **Posting Rule** |
| 4 | Fiscal Calendar & Close | + Period Close | Period Close, Reopen Request, **Fiscal Year (July–June)** |
| 5 | Multi-Entity & Consolidation | + Consolidation Book | Book, IC Charge, IC Rule, TP Rate |
| 6 | Multi-Currency | **+ Exchange Rate** | **Exchange Rate**, FX Revaluation Run |
| 7 | Statutory Statements | + Financial Report Bridge | Bridge, Nil Return |
| 8 | Audit & Retention | **+ External Auditor Access** | **External Auditor Access**, Retention Policy (M24) |
| 9 | Accrual Framework | + Recurring Journal Template | Template, Allocation Rule |
| 10 | Controls & SoD | + Control Account Change | Control Change, SoD Exception, SoD Control |
| 11 | Legacy AR Control Archive | + Legacy GL Control-Ledger Import | same |
| 12 | Legacy Bank-Ledger Take-on | + Legacy Bank-Ledger Take-on | same |

## 5. Evidence

All runs used a private clone, `fix_test_m19c2` (from `fix_test_m55`, then `-u all`: 166 modules, exit 0, no ERROR), with worktree code only.

- **Guard** `cd_gl_ext/tests/test_m19_capture_pass2.py`: **25 tests, 25 passed, 0 skipped.** Every save goes through `/p03/model/write` or `/p03/model/action` as a non-admin Accountant or Accounting Administrator. The registry part runs the engine's own page rule in node. The pass-1 guard `test_m19_capture_buttons.py` was reclassified (pages 3 and 8 are now "form"). Together with the estate-page and sub-module-button guards, every test passes.
- **Defect the guard caught while building:** the auditor's period scope was first written as a *group* record rule. It was OR-ed with the read-only accounting group's own "all journal items" rule and restricted nothing; the auditor saw an entry outside the audited period. The scope rules are now **global** rules that narrow only for an External Auditor.
- **Mutation check** (`scratchpad/m19/mutate.py`): 27 defects re-introduced one at a time, each find-string preflighted to match exactly once.
  - The first run killed 21/27. All six survivors were guard gaps, not code gaps:
    - In four maker/approver checks the maker lacked the approving role, so the role check refused them first.
    - Two freeze checks were only tried through the endpoint, whose form lock hid the model rule.
  - A test where an Accounting Administrator makes and then tries to approve their own rule, rate and grant, plus model-level freeze checks, was added. The survivors were re-run: **6/6 killed, 27/27 in total.**
  - Source files were verified byte-identical afterwards.
- **Live walk** (headless Chromium, private server on 8195 over the clone, admin session): all 12 pages show the "+ New" and chips in the table in §4. Each "+ New" opens its form with no error dialog, and there were 0 console errors.
  - The five new lists were requested with their declared columns: all served, **0 columns dropped**.
  - The clone first raised "Oops: web_tour bundle failed to load". Its asset rows pointed at the template database's filestore; once those rows were cleared, the bundles regenerated. This is environmental and not on fix_real/fix_dev.
- **Regression:**
  - **Finance and multi-entity** (`addons/domain/g_finance`, `cd_multi_entity`): 1,816 tests.
    - 2 failures caused by this change were fixed and re-run green: the mocked posting test now declares the two models the posting API consults, and the fiscal-year bridge test uses a July–June year.
    - 4 failures remain in `cd_tax_engine_bd/test_a09_salary_tds.py` (salary/bonus TDS event relay). They fail identically on the unchanged base `fdc8fef7` against the same database, so they are not caused by this change.
  - **Workspace** (`cd_p03_portal`, A08/M19/estate/sub-module/whitelist/registry selection): **3,313 tests, 0 failures**, 40 skipped.
  - **After rebasing onto the shared tip** (M15/M17/M18/M20/M21 landed meanwhile): `writable.py` regenerates identically. The guard plus the M19, estate, sub-module and M19-registry suites gave **681 tests, 0 failures**.

## 6. Not done / open

1. **fix_real's company fiscal year ends 31 December** (`res_company.fiscalyear_last_month = 12`) for all three companies, which contradicts BRU-FIN-19. Changing it on live data is the owner's decision; the new constraint only governs fiscal-year records.
2. **No rate is loaded on fix_real** beyond the 2010 demo rows. Until a Bangladesh Bank closing rate is entered and approved, the FX revaluation cannot run.
3. **Posting rules govern, they do not yet generate.** Sub-ledgers still build their own lines in code. An active rule restricts which accounts its source may hit and is named on every posting, but the lines are not produced from `line_ids`. That would need each sub-ledger rewired (FR-FIN-008 in full).
4. **FR-FIN-017 (review queue declared by the rule) and BRU-FIN-25 (posting-rights vs rule administration)** are not enforced. BRU-FIN-25 as written conflicts with the CFO approving rules, so it needs an owner decision.
5. While a grant is active, adding a write group to the auditor login is not blocked. The check runs at grant time.
6. Not built (P1): bulk journal import (FR-FIN-014), reporting hierarchies (FR-FIN-005), chart versioning (FR-FIN-007).

## 7. State

- **Landed** `f98fd00f` (fix) and `2ea571e7` (tests) on `fix/a03-live-data-and-pending-work`, by compare-and-swap from `a62539f3`. The main checkout was fast-forwarded with `read-tree -m -u` and is clean.
- **Pushed** `a62539f3..2ea571e7`, plus branch `fix/m19-capture-pass2`.
- **Not yet deployed.** fix_real (8069) and fix_dev (8090) need `-u cd_gl_ext,cd_p03_portal` and one restart before users see the new pages. That waits on the owner's go-ahead and is coordinated with the M18 session, which also needs a restart.
