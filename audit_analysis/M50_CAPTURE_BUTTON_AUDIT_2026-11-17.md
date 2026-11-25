# M50 Treasury & Banking: Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M50 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M50_Treasury_Cash_and_Banking.md`. Sections used:
  - §5: FR-TRE-001 … 042;
  - §8: the cash journey, the payment instruction lifecycle and the LC lifecycle;
  - §9: BRU-TRE-01 … 26;
  - §10.1: the 37 owned entities;
  - §13: roles.
- Research: `audit_analysis/A08_FINANCE_RESEARCH.md` (M50 table) and `A08_FINANCE_TARGET_SPEC.md` (M50).
- Code:
  - `cd_p03_portal/static/src/a08/m50.js`: the page registry (9 sub-module pages, 37 screens in the navigation);
  - `cd_p03_portal/controllers/a08/m50.py`: surfaces, reports and KPIs;
  - `cd_cash_position/models/*.py`: the treasury models.
- Live data (fix_real, read-only count on 17 Nov):
  - 38 bank journals (14 operating banks, 2 MFS wallets, 7 gateway/POS accounts, 15 legacy POS journals). **None has a signatory recorded.** All are BDT.
  - 6 cheques and 2 payment gateways; every other M50 list is empty: statements, reconciliations, payments, deposits, settlements, COD, imprest, facilities, forecast items.
  - 4 users hold Accounting Administrator and 1 holds Accountant, so every two-person step below can be staffed.

## 1. What was there (HEAD 297241f9)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Bank Masters | Bank / Cash Account | **none** | **No mandate or signatory record** (FR-TRE-002 P0, BRU-TRE-20 class H). "Authorised Signatories" was a free-text note on the journal: anyone with journal write could overwrite it, with no approval, limit, validity or history. |
| 2 | Statement & Recon | **Statement Line** | Statement Import, Reconciliation Statement | The "+ New" opened a bank statement **line**, which the model refuses to create (a typed line is not bank evidence). **No matching rule** (FR-TRE-008 P0, FR-TRE-010 P0): bank charges, interest and tax on interest could only be booked one line at a time, by hand, so they sat in the exception queue. |
| 3 | Cash Position & Consolidation | **none** | Cash Deposit | No "+ New" on the page; the cash deposit (cash in transit) existed only as a chip. |
| 4 | Payment Execution | Payment Instruction | Payment Instruction, Cheque Book | The page lists **cheques** (received and issued, PDC, bounce) with no chip, although the form existed. The cheque register report sat on no page. |
| 5 | Gateway/MFS Settlement | Gateway Settlement | Rider COD, Courier COD | The Settlement Exceptions list **could not be acted on**: no owner, no provider ticket, no resolution, no approval (FR-TRE-027 P0, BRU-TRE-10 class H: "a reportable exception with a named owner"). The COD report sat on no page. |
| 6 | Forecasting | Recurring Cash Item | **none** | The 13-week forecast was computed live and **never kept**, so what had been forecast could not be compared with what happened (BRU-TRE-26 class H, FR-TRE-038). |
| 7 | Facilities & Trade Finance | Bank Facility | Facility Amendment | The page lists **covenants** with no chip, although the form existed. |
| 8 | FX | **none** | **none** | The page captured nothing. **No FX conversion record** (FR-TRE-042), and M19's FX revaluation form was not reachable from it. |
| 9 | Controls | Imprest Count | Imprest Top-Up | The page lists **imprest funds** and **imprest vouchers** with no chip, although both forms existed. |

Guard `cd_p03_portal/tests/test_m50_capture_buttons.py` on HEAD: **21 of 36 tests fail.** The failures cover all 9 pages, the line offered as "+ New", the creatable lists with no capture, the missing records, the legacy signatory note, and the rule and case actions.

## 2. What was built

### Backend: `cd_cash_position` 19.0.1.5.0, new file `models/fix_treasury_capture.py`

Every decision is taken by someone other than the person who raised it (`require_other_person`). Stamps and derived figures are guarded fields, never typed. Nothing is deleted except a draft.

| Page | Record | Holds | Rules |
|---|---|---|---|
| 1 | `fix.bank.mandate` (FR-TRE-002, BRU-TRE-20) | Bank account, signatory (employee), signing rule (alone, with any other signatory, or jointly with named signatories), limit per instrument or no limit, validity, the board resolution or bank letter, and the mandate it replaces. | Submitted by an accountant; **approved by an Accounting Administrator who did not request it** (the CFO tier until a CFO group exists). An approved mandate is never edited: a change is a new mandate that **supersedes** the old one on approval, so the history stays. Revocation needs a reason. The journal now shows its **Active Signatories** computed from approved, in-date mandates; the old free-text note is read-only. |
| 2 | `fix.bank.matching.rule` (FR-TRE-008/010) | What it books (bank charge, interest received, interest charged, tax deducted on interest, unadvised debit), direction, narration keywords, amount band, bank account (or all), priority, effective date. | **Approved by a second person** and then frozen. A change is a **new version** that retires the approved one when it is approved. **Auto-Match runs the approved rules after the document layers**: a matching line is posted (Dr expense / Cr bank, or Dr bank / Cr income) and leaves the exception queue as a "bank-originated entry". An unadvised debit is flagged and alerted, **never booked**. Test against Unmatched Lines is a dry run. Two account roles were added: `interest_income` and `tax_on_interest`. |
| 5 | `fix.settlement.exception` (FR-TRE-027, BRU-TRE-10) | The settlement line, its exception type and amount (stamped from the line), **owner**, provider case or ticket, age, and the resolution with its evidence. | Opened from the Settlement Exceptions list ("Open Exception Case", owned by the person who opens it) or the form; one open case per line. Raised with the provider only with a ticket number. A resolution is proposed with evidence; "receipt booked" is accepted only if the line now matches. **Approved by someone other than the proposer**, and the settlement re-runs its match. A daily job alerts on lines unmatched for over 7 days with no case, and gives overdue cases a to-do for their owner. |
| 6 | `fix.cash.forecast.version` (+ weeks) (FR-TRE-038, BRU-TRE-26) | Scenario and assumptions; saving freezes the 13-week forecast week by week: inflow, outflow, net, projected closing, opening balance. | **Never edited or deleted.** Measure Against Actuals (and a daily job) fills each week once it has ended: the actual net movement of the bank and cash accounts, the variance and an accuracy %. The version shows weeks measured and mean accuracy. |
| 8 | `fix.fx.conversion` (FR-TRE-042) | Deal date, bank deal ticket, the account sold from and bought into, both amounts; computed rate achieved. | One side must be in the company currency and the two currencies must differ. **Approved and posted by an Accounting Administrator who did not prepare it**: the foreign leg at the book rate (with its foreign amount), the company-currency leg at what was paid or received, and the difference to the company's exchange gain or loss account. |

Security and data:
- ACLs: the read-only finance group reads, accountants and administrators write, and nobody deletes. Forecast weeks are written only by the model.
- Company and branch isolation rules come from `generate-isolation-rules.py`. Only the cd_cash_position file was kept; the generator's pre-existing drift in four other modules was reverted.
- Three sequences: SXC/, CFV/, FXC/. Two daily jobs: settlement exceptions over 7 days, and forecast accuracy.
- Load order: the new file extends the statement line and the gateway settlement line, so it is imported last (`# ruff: noqa: I001`).

### Workspace: `m50.js`, `controllers/a08/m50.py`, `writable.py`

- Six new lists, on their pages and in the navigation: Bank Mandates & Signatories, Matching Rules, Settlement Exception Cases, Forecast Versions, Forecast Accuracy (weeks), FX Conversions.
- Five new forms. Mandate, Matching Rule and FX Conversion are tabbed (AGENTS.md).
- Changes to existing screens:
  - Auto Reconciliation (statement lines) has no "+ New"; it gains **Apply Matching Rules** and shows what a line was booked as;
  - the statement line form shows the rule and the entry posted;
  - Settlement Exceptions gains **Open Exception Case**;
  - the bank account form shows **Active Signatories (approved mandates)**; the legacy note is read-only.
- Orphan screens placed: the cheque register on page 4, the COD report on page 5.
- The FX page links M19's **FX Revaluation Run** form (M19 owns the month-end revaluation).
- `writable.py` was regenerated with `form_fields.py --a08`; only the M50 entries changed.

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Bank Masters | Bank / Cash Account | **Bank Mandate** |
| 2 Statement & Recon | **Bank Statement Import** | Bank Statement Import, Reconciliation Statement, **Matching Rule** |
| 3 Cash Position & Consolidation | **Cash Deposit** | Cash Deposit |
| 4 Payment Execution | Payment Instruction | Payment Instruction, **Cheque**, Cheque Book |
| 5 Gateway/MFS Settlement | Gateway Settlement | **Settlement Exception**, Rider COD, Courier COD |
| 6 Forecasting | Recurring Cash Item | **Forecast Version** |
| 7 Facilities & Trade Finance | Bank Facility | Facility Amendment, **Facility Covenant** |
| 8 FX | **FX Conversion** | **FX Conversion**, **FX Revaluation Run** (M19) |
| 9 Controls | Imprest Count | **Imprest Fund**, **Imprest Voucher**, Imprest Top-Up |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m50_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. | **HEAD 297241f9: 21 of 36 fail.** After: **36/36.** |
| Live tests `cd_cash_position/tests/test_m50_capture_live.py`. They run as non-admin finance users (two accountants, two Accounting Administrators, a plain user) on a private clone `fix_test_m50` (`-u all`, exit 0). | **17/17.** |
| Mutation check: each rule removed in turn. The rules were: mandate approver ≠ requester, approved mandate frozen, approval supersedes the old mandate, rule approver ≠ submitter, approved rule frozen, rule direction, rule amount band, auto-match applies the rules, resolution approver ≠ proposer, case needs the provider ticket, forecast version frozen, FX approver ≠ preparer. | **12 of 12 mutations turned the live tests red;** the source was restored byte for byte. |
| Regression on the same clone: every `cd_cash_position` test (statement import and auto-match, payments, deposits, cheques, COD, courier, imprest, facilities, gateway, payroll and A04/A05 consumers) plus the M50 guard and the estate page guard. | **861 tests: 0 failures, 0 errors, 0 skipped.** |
| Workspace endpoints on a private server (port 8082), signed in to the clone. | All 6 new lists serve every column (none silently dropped); each new form's editable inputs are exactly its intended fields. Through `/p03/model/write`: a mandate was saved and submitted, its self-approval refused on segregation of duties, a typed `state` refused; a matching rule and a forecast version (CFV/2026/0004, 13 weeks) saved. |
| UI walk on the same server. | All 9 pages show the "+ New" and the chips in the table above (read from the live page). The Matching Rule chip opens its tabbed form with "Book As" as a choice list; the FX page's FX Revaluation Run chip opens M19's form. A Forecast Version was saved from the form: CFV/2026/0005, first week 2026-11-16, scenario and assumptions then read-only. |
| `generate-isolation-rules.py`, `form_fields.py --a08`, pinned ruff 0.8.4 | Only the cd_cash_position / M50 entries changed. Format and lint are clean. |

Four defects were found only by the live run and fixed before the evidence above:
- Odoo 19 has no `env.sudo()`: the rule posting and the FX posting failed, and the rule's savepoint hid it as "line not booked". Both now use `env(su=True)`.
- The open-case field on a settlement line did not refresh after a case was created (missing `@api.depends`).
- Accounting Administrators could not read forecast weeks: in this estate the administrator group does not imply the accountant group, so every model needs its own administrator ACL row.
- A rule's amount band and an approval's segregation of duties needed their own tests, or a mutation survived.

## 4. Not built here (owner decisions or other modules)

- **Beneficiary whitelist** (FR-TRE-034, BRU-TRE-13): a payee bank account is already paid only once it is confirmed through the supplier bank-change approval (cd_ap_ext B2, confirmed by the Operations Director). A separate "first payment to this account" gate would block every existing payment flow and is an owner decision.
- **Daily balance history** (FR-TRE-004) and **liquidity policy / sweeps** (FR-TRE-039 P1): derived from imported statements and the GL; no capture is missing for them today.
- **Field (technician) cash reconciliation** (FR-TRE-017): there is no technician cash collection record in M02 to reconcile against; it needs M02's field-collection hand-off first.
- **Individual LCs and bank guarantees**: LCs live in M44 (`fix.import.lc`) and tender guarantees in A04 (`fix.tender.bond`); M50 holds their facility limits and expiry alerts.
- **Provider fee analysis** (FR-TRE-029 P2) and the **bank relationship record** (FR-TRE-005 P2) are reports, not captures.
- **CFO approval**: the spec asks the CFO to approve mandates. There is no CFO group in Odoo (R-03 is a role record), so an Accounting Administrator other than the requester approves until the owner maps R-03 to a group.
- **Matching-rule accounts**: `cd_cash_position.account_code.interest_income` and `.tax_on_interest` must be set on fix_real before rules of those kinds can be approved (approval refuses a rule whose account is not configured).

## 5. State

- Built and tested in worktree `m50cap-wt`. Fix commit 4d8f2bf9 is on the working branch `fix/a03-live-data-and-pending-work`, moved by compare-and-swap from 297241f9 (the M49 tip). **Not pushed.**
- **Deployed on fix_real (8069) on 17 Nov 2026**, on the user's approval:
  1. Backup `fix_real_pre_m50_capture_2026-11-17.dump` (47.2 MB, reads back with pg_restore: 50,075 entries).
  2. `-u cd_cash_position,cd_p03_portal` on fix_real exited 0. cd_cash_position is now 19.0.1.5.0.
  3. Before the restart, all 83 installed cd_ modules matched their code.
  4. 8069 was restarted once: PID 30868 became 52108 (supervisor 23964), login answering after 9 s. The log shows 155 modules loaded and no errors; the only warnings are long-standing ones from other modules.
- Verified on the live server:
  - all 6 new models are served, Auto Reconciliation offers Apply Matching Rules and Settlement Exceptions offers Open Exception Case;
  - both new daily jobs are registered;
  - bundle a86519c carries the 5 new forms and the new actions.
- Between the upgrade and the restart, the old process ran the two new daily jobs once and logged a `KeyError` (it did not yet know the new models). The restarted process runs them normally.
- fix_real holds **no** rows in the new records yet, and no mandate for any of its 38 bank accounts: recording who signs on each account is a data take-on for the finance team.
- Before matching rules of those kinds can be approved, the owner sets `cd_cash_position.account_code.interest_income` and `.tax_on_interest`.
- **fix_dev (8090) upgraded the same day**, on the user's request:
  - Backup `fix_dev_pre_m50_capture_2026-11-17.dump` (38.8 MB, reads back).
  - Before the upgrade, cd_cash_position was fix_dev's only version gap across its 80 installed cd_ modules. `-u cd_cash_position,cd_p03_portal` exited 0.
  - 8090 restarted straight after: PID 35160 became 45588 (supervisor 37700) in 11 s, with no log errors. The old process logged the same two harmless cron `KeyError`s in the 40 s before the restart.
  - The same records and actions are served, and the bundle is a86519c, the same as fix_real.
