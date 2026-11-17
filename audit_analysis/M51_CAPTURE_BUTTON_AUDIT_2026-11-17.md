# M51 Tax & Regulatory (BD): Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M51 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M51_Tax_and_Regulatory_Compliance_Bangladesh.md`. Sections used:
  - §3: scope boundary (what M51 owns, what M20, M52, M50 and M44 own);
  - §5: FR-TAX-001 … 045;
  - §8: the VAT period cycle (Filed → Amended), the withholding lifecycle and the country-pack version lifecycle;
  - §9: BRU-TAX-01 … 26;
  - §10.1: the owned entities; §11: AUT-TAX-01 … 22; §13: roles and segregation of duties.
- Research: `audit_analysis/A08_FINANCE_RESEARCH.md` (M51 table) and `A08_FINANCE_TARGET_SPEC.md` (M51).
- Code:
  - `cd_p03_portal/static/src/a08/m51.js`: the page registry (9 sub-module pages);
  - `cd_p03_portal/controllers/a08/m51.py`: surfaces, reports and KPIs;
  - `cd_tax_engine_bd/models/*.py`: the tax models;
  - `cd_billing_engine/models/fix_ar_engine.py`: the receipt's high-value cash rule.
- Live data (fix_real, read-only count on 17 Nov):
  - no VAT return, register row, withholding line, challan, input credit, VDS certificate received, audit pack or filing yet;
  - 23 vendor tax profiles; 4 statutory parameters, all flagged "verify with adviser";
  - **no** `cd_billing_engine.nid_cash_threshold` set, so the receipt applied its hard-coded BDT 50,000;
  - 1 user holds Tax Return Filing Approver (the CFO appointment).

## 1. What was there (HEAD 94bf9e99)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Determination Service | VAT Treatment | Tax Rate | Lists **statutory parameters** with no chip, although the form existed. **No record of the declared marketplace VAT model** (FR-TAX-045 P0, BRU-TAX-16/17 H, decision D-03): the "Marketplace VAT Model" report route only opened the treatment list. |
| 2 | VAT Output/Input | Input VAT Adjustment | Input VAT Adjustment | None. |
| 3 | Mushak Registers | **none** | VAT Register Correction | No "+ New": a register row is written by the engine, but the page's own capture (the correction) was only a chip. |
| 4 | VAT Return 9.1 | VAT Return | **none** | **A filed return could not be amended** (BRU-TAX-15 H, §8.1 "Filed → Amended"): an error found after filing, or an NBR query, had nowhere to go. The SD & AT Liability report sat on no page. |
| 5 | VDS | **none** | **none** | The page captured nothing. **VDS deducted by our own customers** (Mushak 6.6 received, FR-TAX-039 P0) lived only in M20, and the vendor's VDS exemption (BRU-TAX-26) only in M52. |
| 6 | TDS | TDS Return | TDS Return | The vendor's **PSR status**, which decides the 50% surcharge (FR-TAX-007, BRU-TAX-08), was reachable only from M52. |
| 7 | Challans & Certificates | Challan | Challan | None (certificates are issued from a deposited deduction, by design). |
| 8 | High-Value Register | **none** | **none** | The page captured nothing. The **NID threshold** was a hard-coded BDT 50,000 inside M20 (FR-TAX-044: M51 owns it; BRU-TAX-01: no threshold in code), and the Mushak 6.10 threshold could be changed only from page 1. |
| 9 | Calendar & Audit | Statutory Due Rule | Filing Evidence | Lists **audit packs** with no chip, although the form existed. **No record of an NBR query, audit notice or assessment** (AUT-TAX-22, §3.1 item 22): nothing to hold its scope, deadline, owner, response or outcome. |

Guard `cd_p03_portal/tests/test_m51_capture_buttons.py` on HEAD: **17 of 33 tests fail.** The failures cover pages 1, 3, 4, 5, 6, 8 and 9, the parameter list with no capture, the orphan SD & AT report, the three missing records and the hard-coded threshold.

## 2. What was built

### Backend: `cd_tax_engine_bd` 19.0.1.1.0, new file `models/fix_tax_capture.py`

Every decision is taken by someone other than the person who prepared it. Stamps and derived figures are guarded fields, never typed. Nothing is deleted (no delete right for anyone).

| Page | Record | Holds | Rules |
|---|---|---|---|
| 1 | `fix.marketplace.tax.model` (FR-TAX-045, BRU-TAX-16/17) | Company, declared model (principal: VAT on the full sale; agent: VAT on the commission and fees), VAT rate, the external tax opinion and its file, validity. | A statutory master row, on the existing two-step sign-off: proposed by an Accounting Administrator, the external opinion recorded as the adviser confirmation, **activated by the CFO (filing approver) who did neither**, and refused without the opinion file. Never edited in place; a change is a new proposal whose activation closes the old window. Two positions in force for one company are refused. **Until one is active, `get_declared` / `determine` refuse marketplace VAT determination** (never defaulted). **None is seeded:** D-03 is open. |
| 4 | `fix.vat.return.amendment` (BRU-TAX-15, §8.1) | The filed return, why (our own error, NBR query, NBR audit), the NBR notice, what was wrong, the corrected output and input VAT, the working papers; computed: the corrected net, the net as last filed, the difference. | Only a filed return is amended, one amendment at a time. Submitted with the working papers by an accountant, then frozen. **Approved by the CFO who did not prepare it.** Filed with the NBR acknowledgement and its file; additional VAT needs the challan that paid it. **The original return is never touched**: it shows the amendments and the net as amended. Publishes `vat_return.amended` (registered, 542 events). |
| 9 | `fix.tax.notice` (AUT-TAX-22) | Notice type, tax, issuing office, reference, received date, scope, what NBR asks, response deadline, owner, amount in dispute, the notice file; our response with its file; the outcome and tax assessed. | Creating a notice gives its owner a to-do with the deadline. **Generate Audit Pack for Scope** builds and seals the existing audit pack for the notice's period. The response is recorded only with its reference, date and file; the notice is then frozen. **Closed by an Accounting Administrator who did not record the response**, with the outcome (an assessment needs its amount). A daily job reminds the owner before the deadline and escalates an overdue notice to the Accounting Administrators and the CFO. |

Also:
- **NID threshold moved to M51** (FR-TAX-044, BRU-TAX-01): new statutory parameter key `nid_cash_threshold`, seeded at BDT 50,000 (the value M20 applied, flagged "verify with adviser", so it joins the Sign-Off Queue). `fix.ar.receipt._nid_threshold` (M20, also used by the storefront COD bridge) now reads the M51 row in force, company row first; the legacy system parameter is read only where no row exists, and with neither the receipt is refused rather than defaulted. On fix_real this keeps the threshold at 50,000.
- ACLs: the read-only finance group reads; accountants write amendments and notices; Accounting Administrators propose the marketplace model; the filing approver (CFO) reads and decides; nobody deletes.
- Company and branch isolation rules from `generate-isolation-rules.py`. Only the cd_tax_engine_bd file was kept; the generator's pre-existing drift in four other modules was reverted.
- Two sequences (VRA/, TXN/) and one daily job (NBR notice deadlines).
- Load order: the new file extends `fix.vat.return`, so it is imported after `fix_tax_returns_a08`.

### Workspace: `m51.js`, `controllers/a08/m51.py`, `writable.py`

- Six new lists, on their pages and in the navigation: Marketplace VAT Model (D-03), 9.1 Amendments (Filed Returns), NBR Notices & Queries, High-Value Thresholds, VDS Deducted by Customers (6.6 Received, M20's record), Vendor Tax Status (PSR, Exemptions; M52's record).
- Three new forms; the amendment and the notice are tabbed (AGENTS.md).
- The marketplace model joins the Sign-Off Queue; a new tile counts open NBR notices.
- The SD & AT Liability report is placed on page 4.
- `writable.py` was regenerated with `form_fields.py --a08`; only the three new models were added.

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Determination Service | VAT Treatment | Tax Rate, **Tax Parameter**, **Marketplace VAT Model** |
| 2 VAT Output/Input | Input VAT Adjustment | Input VAT Adjustment |
| 3 Mushak Registers | **VAT Register Correction** | VAT Register Correction |
| 4 VAT Return 9.1 | VAT Return (Mushak 9.1) | **VAT Return (Mushak 9.1)**, **VAT Return Amendment** |
| 5 VDS | **VDS Certificate (received, M20's form)** | **VDS Certificate Received**, **Vendor Tax Profile** (M52's form) |
| 6 TDS | TDS Return | TDS Return, **Vendor Tax Profile** |
| 7 Challans & Certificates | Challan | Challan |
| 8 High-Value Register | **Tax Parameter** (thresholds) | **Tax Parameter** |
| 9 Calendar & Audit | Statutory Due Rule | Filing Evidence, **Tax Audit Pack**, **NBR Notice** |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m51_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. | **HEAD 94bf9e99: 17 of 33 fail.** After: **33/33.** |
| Live tests `cd_tax_engine_bd/tests/test_m51_capture_live.py`. They run as non-admin users (two accountants, two Accounting Administrators, the filing approver, a plain user) on a private clone `fix_test_m51` (`-u all`, exit 0, 0 errors). The amendment tests file a real 9.1 through the proper path first. | **16/16, no skips.** |
| Mutation check: each rule removed in turn (amendment approver ≠ preparer, needs the CFO, needs working papers, needs its challan, frozen once submitted, one in progress; marketplace refused until declared, activation needs the opinion, cannot vary; notice closer ≠ responder, response needs evidence, pack generated once, overdue escalation, frozen once responded; M20 reads the M51 threshold). | **15 of 15 mutations turned a live test red**, each the test written for that rule; the source was restored byte for byte. |
| Existing portal guards: M51 registry and reports, A08 write whitelist, A08 control suite, estate module pages, M49/M50 capture guards. | **1,123 passed, 0 failed** (34 skips are the control suite's by-design "no workflow-controlled fields" cases). |
| Regression: every test of `cd_tax_engine_bd`, `cd_billing_engine`, `cd_storefront_finance` and `cd_front_desk_finance` (the last two installed on the clone for this run), on this change and on an identical clone built from HEAD 94bf9e99. | **This change: 538 passed, 4 failed. HEAD: 522 passed, 4 failed. The 4 failures are identical** (A09 salary-TDS relay tests, unrelated to M51); the extra 16 are the new live tests. One existing test needed a change: the M51 operability test now checks list actions against the merged A08 registry the server serves, because page 5 lists M20's VDS certificates with M20's actions. The storefront NID tests now set the threshold as an M51 company row. |
| Workspace endpoints on a private server (port 8083), signed in to the clone. | All 6 new lists serve every column (none dropped). Each new form's editable inputs are exactly its whitelist (notice 20, amendment 11, marketplace model 10). Through `/p03/model/write`: an NBR notice saved (TXN/2026/0019), a typed `state` refused, **Generate Audit Pack for Scope** built and linked pack 4; a marketplace model saved as a proposal (a typed `active` stayed proposed). |
| UI walk on the same server, read from the live page. | All 9 pages show the "+ New" and chips in the table above. The NBR Notice and VAT Return Amendment chips open their tabbed forms. |
| `generate-isolation-rules.py`, `form_fields.py --a08`, pinned ruff 0.8.4 | Only the cd_tax_engine_bd / M51 entries changed. Format and lint are clean. |

Found only by running: a refused `create` inside `pytest.raises` without a savepoint left its row in the transaction and broke the next step of the test; the refused creates now run in savepoints.

## 4. Not built here (owner decisions or other modules)

- **The D-03 marketplace position itself.** The record exists; declaring it needs the external tax opinion and the CFO. Nothing in the estate determines marketplace VAT today, so no flow is blocked by its absence.
- **Country-pack versions, rules and fixtures** (FR-TAX-003/004, `fix.tax.pack.version`, `fix.tax.rule.fixture`): the estate versions each rate, parameter, treatment and calendar row with its own adviser + CFO sign-off instead of a pack release. Moving to pack-level releases is an architecture change, not a missing button.
- **Per-transaction determination record** (FR-TAX-002, `fix.tax.determination`), **Mushak 6.3 sequence / statutory document** (FR-TAX-011), **register lock rows** (FR-TAX-023): engine records written by posting, not captures.
- **Income-tax computation, advance tax, tax provision** (FR-TAX-041/042, P1) and the **tax depreciation book** (FR-TAX-040, P1; the Third Schedule rates are already M51 master data read by M49): year-end computations with no page in the M51 registry today; a new page is a scope decision for the owner.
- **Import tax record** (FR-TAX-043): M44's Bill of Entry carries duty, VAT and AT (reported on page 4 as SD & AT Liability); the import VAT credit is an input credit.
- **Mushak 6.5 stock transfer register** (FR-TAX-021, P1): needs registered-premises data (FR-TAX-006) that no source file holds.
- **Withholding received (TDS deducted by customers)**: M20 records VDS certificates received; customer TDS certificates live in M20's own screens.
- **Owner actions on fix_real:** confirm the NID threshold (BDT 50,000) and the Mushak 6.10 threshold (BDT 200,000) with the adviser and have the CFO sign them off; appoint a second filing approver if the one holder may also prepare returns.

## 5. State

- Landed on the working branch `fix/a03-live-data-and-pending-work`: fix c3820c11 and report 3d6f64f9, rebased onto c5feece6 (after M54, M53, M52 and the M49 gaps) and fast-forwarded by compare-and-swap. **Not pushed.**
- After the rebase the clone was upgraded with every module changed since 94bf9e99 (exit 0, 0 errors) and the guards and regression re-run: **1,611 passed, 4 failed**: the same 4 A09 salary-TDS relay tests that fail on HEAD.
- **Deployed on fix_real (8069) on 17 Nov 2026**, in one combined run with M55 by the M55 session, on the user's approval:
  1. Backup `fix_real_pre_m55_capture_2026-11-17.dump` (49.9 MB).
  2. `-u cd_attendance,cd_tax_engine_bd,cd_billing_engine,cd_p03_portal` exited 0 with no ERROR lines; the version-gap check over 83 cd_ modules was clean.
  3. 8069 restarted once: PID 78988 became 28840 (supervisor 23964); 155 modules loaded; login answers 200.
- Verified by this session afterwards (read-only):
  - 8069 is PID 28840 serving `-d fix_real`; cd_tax_engine_bd is 19.0.1.1.0;
  - the three new tables exist with 12 access rows and 6 isolation rules, all empty: **no marketplace VAT model is declared**, as D-03 requires;
  - `nid_cash_threshold` = 50,000, active, statutory default (no company): counter receipts keep the same limit;
  - the NBR notice deadline job is active;
  - the served workspace bundle 03f2536 carries the three new forms, the new lists and the new "+ New" of pages 3, 5 and 8. The pages were not opened in a browser on 8069 (no session there).
- **fix_dev (8090) is not upgraded.**
- The NID threshold row (BDT 50,000) and the new models arrive with that upgrade; nothing else changes for the counter.
