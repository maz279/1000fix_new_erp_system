# M19 Financial Accounting & GL — sub-module capture-button audit

Date: 13 Nov 2026 · Scope: the 12 Function Register sub-module pages of M19 in the P03 workspace
· Live server checked: 8069 = `fix_real`

## 1. What was reported

Not every M19 sub-module page had a relevant button to record its data.

## 2. How the audit was done

- **What M19 should do.** Module spec `1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M19_Financial_Accounting_and_General_Ledger.md`:
  §5 FR-FIN-001…046, §8 lifecycles, §9 BRU-FIN-11…26, §10 owned entities.
- **What the code allows.** Models in `cd_gl_ext`, `cd_multi_entity`, `cd_rbac_ext` (SoD), `cd_dms` (retention), and their `ir.model.access.csv` (who may create).
- **What the workspace shows.** Registry `cd_p03_portal/static/src/a08/m19.js`, the engine's `fregCreate` / `fregPanels` (`p03_workspace.js`), the server whitelist `controllers/a08/m19.py`.
- **What a user sees.** Each page was evaluated with the engine's own code in node over the real merged registry, then clicked through live on 8069 (`?debug=assets`).
- **Classification:** a record a person enters → "+ New" and/or a form chip; a record written by posting or a workflow → no button, with a note saying where it comes from.

## 3. Findings (before the fix)

| # | Page | What it showed | Verdict |
|---|---|---|---|
| 1 | CoA & Dimensions | "+ New Chart of Accounts — Account"; no chips | Partly. Control Account Change (FR-FIN-002/006) and the CoA loader run were reachable only from lists |
| 2 | Journals | **No "+ New".** Chips: Journal Entry, Partner-Ledger Take-on | **Missing button.** The page grid is the journal register (`account.journal`), so the engine never offered the module's journal-entry editor — the page's main capture (FR-FIN-011) |
| 3 | Subledger Posting Engine | Nothing | OK by design (dimension lines are written by posting), but undeclared |
| 4 | Fiscal Calendar & Close | "+ New Period Close"; no chips | Partly. **Period Reopen Request** (FR-FIN-019, BRU-FIN-06) had a form and a list on the page but no chip |
| 5 | Multi-Entity & Consolidation | "+ New Consolidation Book"; chip Intercompany Charge | Partly. **Intercompany Rule** and **Transfer-Pricing Rate** forms existed but were on no chip; the IC Rules list and Due-To/Due-From screen were on no page at all |
| 6 | Multi-Currency | "+ New FX Revaluation Run"; no chips | Partly (form reachable only via the button) |
| 7 | Statutory Statements | "+ New Financial Report Bridge"; chip Nil Return | Partly. The Nil-Return Packs list was on no page |
| 8 | Audit & Retention | **Nothing** | **Missing.** See §5: the capture the spec names here (auditor access, FR-FIN-043) has no model; retention (FR-FIN-046) is an M24 master |
| 9 | Accrual Framework | "+ New Recurring Journal Template"; chips Template, Allocation Rule | OK |
| 10 | Controls & SoD | **Nothing** | **Missing.** Page lists `fix.sod.control` (an M29 master) and offered no way to propose a control-account change (BRU-FIN-13) or an SoD exception |
| 11 | Legacy AR Control Archive | "+ New Legacy GL Control-Ledger Import" | OK |
| 12 | Legacy Bank-Ledger Take-on | "+ New Legacy Bank-Ledger Take-on" | OK |

Result: **4 of 12 pages had no "+ New"** (2, 3, 8, 10), and three of them had no capture at all. Six pages hid forms that existed. Four M19 screens (IC Rules, Due-To/Due-From, Nil-Return Packs, CoA Register Pack) were on no sub-module page.

## 4. What was changed

**`static/src/a08/m19.js`** (registry), **`static/src/p03_workspace.js`** (one engine clause):

| Page | Now offers (verified live on 8069) |
|---|---|
| 1 CoA & Dimensions | "+ New Chart of Accounts — Account"; chips Chart of Accounts Account, **Control Account Change**, **Chart Loader**; CoA Register Pack on the page |
| 2 Journals | **"+ Journal Entry"** (the in-workspace editor: draft → SoD review); chips Journal Entry, Partner-Ledger Take-on |
| 3 Subledger Posting Engine | No button, now declared (`create: false`); the panel says records are not typed in |
| 4 Fiscal Calendar & Close | "+ New Period Close"; chips Period Close, **Period Reopen Request** |
| 5 Multi-Entity & Consolidation | "+ New Consolidation Book"; chips Consolidation Book, Intercompany Charge, **Intercompany Rule**, **Transfer-Pricing Rate**; IC Rules + Due-To/Due-From on the page |
| 6 Multi-Currency | "+ New FX Revaluation Run"; chip FX Revaluation Run |
| 7 Statutory Statements | "+ New Financial Report Bridge"; chips Financial Report Bridge, Nil Return Declaration; Nil-Return Packs on the page |
| 8 Audit & Retention | Chip **Retention Policy** (opens M24's form). No "+ New" — see §5 |
| 10 Controls & SoD | **"+ New Control Account Change"**; chips Control Account Change, **SoD Exception**, **SoD Control** (M29's forms); Control Changes list on the page; SoD rows open M29's form |

Engine: `fregCreate` accepts `create: 'module'` — a page whose grid lists another model may declare that its capture is the module's own button (only M19/2 uses it; the create-button guard pins that).

Why SoD Control and Retention Policy are chips, not a page's "+ New": `ir.model.access` lets only `base.group_system` create `fix.sod.control` and `fix.retention.class`. A finance user's Save would be refused, so a page button would be a trap. The chips stay for administrators; the guard test reads the ACL files and fails if that ever changes.

Tests:
- New `tests/test_m19_capture_buttons.py` — 33 tests; **10 fail on the old registry** (pages 1, 2, 4, 6, 8, 10, the Journals editor, the mastered-elsewhere chips, the Controls button, forms on no page); all 33 pass now.
- `test_submodule_create_button.py` — rule allows a *declared* module button, and pins M19/2 as the only one.
- Estate (`test_estate_module_pages.py`), sub-module mapping, M19 registry, M01 pages — green for M19. The one remaining failure in those suites (`M18-form-cert: no pick instruction`) is in `m18.js`, which another session has uncommitted edits in.

## 5. Gaps that need a build or an owner decision (not buttons)

| FR | What is missing | Effect |
|---|---|---|
| FR-FIN-009 / BRU-FIN-17/18 | **Posting rules** as versioned records (author → test fixture → approve → activate). Posting today is coded per subledger | Subledger Posting Engine page cannot have a capture until the model exists |
| FR-FIN-043 / BRU-FIN-26 | **External auditor access grant** (scope, period, expiry, log) | Audit & Retention has no finance-entered record |
| FR-FIN-033 | **Rate tables** by type with approved manual override | No workspace capture for FX rates anywhere; revaluation reads Odoo rates |
| FR-FIN-004 | **Dimension cross-validation rules** | No model |
| FR-FIN-014 | **Bulk journal import** (all-or-nothing) | Only the legacy take-on lanes exist |

Data note (fix_real, 13 Nov): the Control Account Change form's Statutory Account picker is empty — the MD-035 statutory chart (`fix.chart.account`) has no rows on fix_real, so no control change can be proposed until the CoA Master Loader is run there.

## 6. Deployment state

- JS only, no Python, no model change. Uncommitted.
- Live for a `?debug=assets` session now. The production bundle on 8069 (`bb2bba0`, checked 13 Nov ~02:00) does **not** contain it yet: users see it after the next 8069 restart / asset rebuild.
- During the audit the Postgres container went into crash recovery (~01:02–02:00 local, full fsync of the data directory); it was not caused by this work and recovered on its own.
