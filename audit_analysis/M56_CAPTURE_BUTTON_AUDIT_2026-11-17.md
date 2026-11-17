# M56 Payroll, Benefits & Statutory Compliance: Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M56 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M56_Payroll_Benefits_and_Statutory_Compliance.md`. Sections used:
  - §3: scope (18 capabilities);
  - §5: FR-PAY-001 … 054;
  - §8: the payroll-run and final-settlement lifecycles;
  - §9: BRU-PAY-01 … 18;
  - §10.1: the 22 owned entities;
  - §13: roles and the three-way segregation;
  - §16.4: data migration (opening balances);
  - §18: open questions Q-01 … Q-10.
- Code:
  - `cd_p03_portal/static/src/a09/m56.js`: the page registry (10 sub-module pages);
  - `cd_p03_portal/controllers/a09/m56.py`: surfaces, reports and KPIs;
  - `cd_payroll_bd/models/*.py`: the payroll engine, statutory pack, off-cycle payments, recoveries, bank returns, gratuity accrual.
- Live data (fix_real, read-only count on 17 Nov):
  - **no** payroll run, payslip, off-cycle payment, recovery, certificate or return;
  - **no** active employment contract, so the gratuity cron accrues nothing;
  - 1 statutory pack (the seeded baseline);
  - 4 Payroll Managers and **0** Payroll Officers.

## 1. What was there (HEAD c5feece6)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Gross-to-Net Engine | **none** | Salary Structure | No "+ New" although the page's own master (salary structure) has a form. |
| 2 | BD Income Tax | **none** | **none** | The page **captured nothing**. **No investment declaration** (FR-PAY-013 P0, FR-PAY-014, BRU-PAY-10 H): the payslip sent the engine `investment_allowance = 0.0` with the comment "there is no declaration model", so **no employee ever received the investment rebate**. The statutory pack list (FR-PAY-009 P0) sat on no page. |
| 3 | Provident Fund | **none** | **none** | The page **captured nothing**. **No PF membership** (FR-PAY-020 P0): every payslip deducted 10% + 10% whatever the employee's membership; the employee master's "RPF Member" flag is read by nothing. |
| 4 | Gratuity | **none** | **none** | The page **captured nothing**; the monthly provision register sat on no page. **No opening provision** (FR-PAY-022, §16.4, Q-05): the first monthly accrual treated an employee's whole historical liability as that month's movement and posted it as **one month's expense** (Dr gratuity expense / Cr provision), although the legacy books may already carry it. |
| 5 | Bonus & Encashment | Bonus Run | Bonus Run | The page lists WPPF allocations with no chip; bonus lines and WPPF beneficiaries sat on no page. |
| 6 | Loans & Advances | Off-Cycle Payment | **none** | **A salary advance was paid and never recovered** (FR-PAY-031/032 P1, FR-PAY-033): nothing deducted it, nothing recorded what the employee owed. The page listed every off-cycle payment, not advances. |
| 7 | Runs & Off-Cycle | Payroll Run | Payroll Run | Off-cycle payments listed with no chip; the variance review and overpayment recoveries sat on no page. |
| 8 | BEFTN & Payslips | **none** | **none** | The page **captured nothing**: no way to import the bank's return (FR-PAY-048) or the MFS provider's; bank and MFS returns, bank-change confirmations and My Payslips sat on no page. |
| 9 | Returns & Certificates | Withholding Return | **none** | Certificates listed with no chip. |
| 10 | Final Settlement | Off-Cycle Payment (preset) | Final Settlement | The chip opened a plain off-cycle payment (type Arrear), and the "Final Settlements" list showed **every** off-cycle payment; nominee accounts (BLA s.19) sat on no page. |

In all, 15 working lists had no page. Guard `cd_p03_portal/tests/test_m56_capture_buttons.py` on HEAD: **21 of 32 tests fail.**

## 2. What was built

### Backend: `cd_payroll_bd` 19.0.0.4.0

Every decision is taken by someone other than the person who recorded it. Stamps are guarded fields, never typed.

| Page | Record | Holds | Rules |
|---|---|---|---|
| 2 | `fix.investment.declaration` (FR-PAY-013/014, BRU-PAY-10) | Employee, income year (e.g. 2025-26), investment type (Sanchayapatra, DPS, life premium, listed shares, government securities, approved pension, other), amount invested, evidence, certificate/policy number. | Recorded by payroll. **Validated by a second payroll user: never the recorder, never the employee**, with evidence attached, at the declared amount or a lower eligible amount; or rejected with a reason. Frozen once decided. **The payslip calculation now sends the fiscal year's validated eligible amounts** to the engine; declared, rejected and other-year declarations do not count. |
| 3 | `fix.pf.member` (FR-PAY-020) | Employee, date joined the fund, employee and employer rates (% of basic), opening balances taken on and their date, evidence. | Recorded by payroll, **approved by a Payroll Manager who did not record it**; one open membership per employee; leaving the fund needs a reason. **Once the company keeps the register (one approved membership), members contribute at their own rates and non-members not at all. Until then the calculation is unchanged** (10% + 10%), so nothing moves before payroll takes the register on. |
| 4 | `fix.payroll.gratuity.opening` (FR-PAY-022, Q-05) | Employee, as-of month end, the provision the legacy books carry, legacy ledger/schedule reference, evidence. | Approved by a **second Payroll Manager** with the schedule attached; one per employee; **refused once the monthly register already carries the employee**. **The first monthly accrual moves from the approved opening**, so only the real movement is posted. |
| 6 | Advance recovery schedule (`fix.payroll.recovery`, new `recovery_type = advance`) (FR-PAY-031/032/033) | The advance it recovers, the amount owed (defaults to the whole advance), the monthly instalment, the repayment terms. | Routed through the M63 inbox like an overpayment recovery (a Payroll Manager who did not prepare it). Never more than the advance; one schedule per advance; same employee and company. **A salary advance is released to the bank only once its approved schedule covers the whole amount.** Each monthly run deducts the instalment after tax (within the company's monthly cap and the slip's net) until repaid; **never from a festival bonus or another off-cycle payment**. Overpayment recoveries are unchanged (their approval digest is untouched). |

Security and data:
- ACLs: payroll officers (Payroll Managers imply them) read, write and create; nobody deletes. Plain users have no access.
- Company and operating-unit isolation rules from `generate-isolation-rules.py`. Only the cd_payroll_bd file was kept; the generator's pre-existing drift in four other modules was reverted.
- Load order: `models/fix_payroll_capture.py` extends `fix.payroll.offcycle`, so it is imported last.
- `correction_slip_id` on a recovery is no longer NOT NULL (an advance has no payslip); the constraint still requires it for an overpayment.

### Workspace: `m56.js`, `controllers/a09/m56.py`, `controllers/a09/writable.py`

- Five new lists, each in the navigation: Salary Advances, Advance Recovery Schedules, Investment Declarations, Provident Fund Members, Gratuity Opening Provisions. Final Settlements, Overpayment Recoveries, Salary Advances and Advance Recovery Schedules now show only their own slice.
- Six new forms, all tabbed: Salary Advance and Final Settlement Payment preset their payment type; Advance Recovery Schedule presets its type; Investment Declaration; Provident Fund Membership; Gratuity Opening Provision.
- `writable.py` regenerated with `form_fields.py --a09`; only the M56 entries changed.

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Gross-to-Net Engine | **Salary Structure** | Salary Structure |
| 2 BD Income Tax | **Investment Declaration** | **Investment Declaration**, **Statutory Pack** |
| 3 Provident Fund | **PF Membership** | **PF Membership** |
| 4 Gratuity | **Gratuity Opening Provision** | **Gratuity Opening Provision** |
| 5 Bonus & Encashment | Bonus Run | Bonus Run, **WPPF Allocation** |
| 6 Loans & Advances | **Salary Advance** (preset) | **Salary Advance**, **Advance Recovery Schedule** |
| 7 Runs & Off-Cycle | Payroll Run | Payroll Run, **Off-Cycle Payment**, **Overpayment Recovery** |
| 8 BEFTN & Payslips | **BEFTN Bank Return** | **BEFTN Bank Return**, **MFS Provider Return** |
| 9 Returns & Certificates | Withholding Return | **Withholding Return**, **Tax Certificate** |
| 10 Final Settlement | Final Settlement Payment (preset) | **Final Settlement** (now preset), **Nominee Account** |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m56_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. | **HEAD c5feece6: 21 of 32 fail.** After: **32/32.** |
| Live tests `cd_payroll_bd/tests/test_m56_capture_live.py`, run as non-admin payroll users (officer, two Payroll Managers, a releaser, a plain user) on a private clone `fix_test_m56` (`-u all`, exit 0, no errors). Advances and schedules go through the real M63 inbox and BEFTN release; one case goes through `/p03/model/write` and `/p03/model/action`. | **9/9.** |
| Mutation check: each rule removed in turn (advance released without a schedule; advance taken from any payment; instalment ignored; schedule above the advance; two schedules per advance; investment back to 0; unvalidated declarations counted; recorder validates own; employee validates own; eligible above declared; PF register ignored; non-members still contribute; officer approves a membership; opening ignored by the accrual; opening approved after accruals). | **14 of 15 turned the tests red;** the source was restored byte for byte. The survivor ("unvalidated declarations counted") is equivalent: a draft declaration has no eligible amount (set only by validation, never typed), so counting it adds 0. |
| Workspace endpoints and UI on a private server (port 8093) on the clone. | All 29 M56 lists and 22 forms served through `/p03/model/records` and `/p03/model/form` with no error. Every page shows the "+ New" and chips of the table in §2. An Investment Declaration was saved from the tabbed form (INV/67, Declared). "+ New Salary Advance" on page 6 opens the form with the payment type preset to Salary Advance. |
| Regression on the same clone: every `cd_payroll_bd` test, the M56 guard, the estate page guard, the A09 write whitelist, control suite and people controls, KPI tiles, screen wiring and the Bengali payslip renderer. | **1,222 passed, 2 failed.** The 2 failures (`test_the_relay_delivers_hse_compensation_awarded`, `..._recognition_awarded`) **fail identically on the unchanged base code**: the template `fix_test` holds 53,624 unrelayed outbox events, and the relay takes the oldest 500, so the test's event is never reached. Not caused by this change. |
| `ruff` 0.8.4 check and format | Clean. |

## 4. Not built here (owner decisions or other modules)

- **PF fund rules** (spec Q-03): whether a recognised fund exists and its rates is the owner's answer. The register lets payroll record it; until a membership is approved, the calculation stays at 10% + 10% for everyone, as today. The PF member ledger, interest credit and withdrawal (FR-PAY-021) follow once the fund rules are known.
- **The employee master's "RPF Member" flag** is still read by nothing; the membership register is now the authority. Whether to retire the flag is an M21 decision.
- **Investment rebate rate and cap** (spec §19: 10%, investment capped at BDT 750,000): the engine's own rebate formula (15% of the investment, limited by its taxable-income test) is unchanged. Spec Q-01 says the pack must come from the enacted Finance Act; that is the tax advisor's call, not a capture.
- **Loans with interest** (FR-PAY-031: "interest treatment") and the aggregate deduction limit as a proportion of net pay (BRU-PAY-12): a schedule recovers the principal within the company's monthly cap and the slip's net. An interest-bearing loan product needs a policy.
- **Earnings and deduction elements** (FR-PAY-001/002) as configuration: the engine computes from code (`libs/py/payroll_engine`). A configurable element table that the engine does not read would be decorative, so none was built.
- **Salary structure** is captured in M56 but the calculation reads the employment contract (M21); the spec puts the structure in M21.
- **Data**: fix_real holds no payroll run, contract, declaration, membership or opening provision, and **no Payroll Officer**. Every capture here needs a Payroll Officer to record and a Payroll Manager to decide: appointing the officer is spec Q-09.

## 5. State

**Deployed on fix_real (8069) and fix_dev (8090) on 18 Nov 2026**, on the user's approval ("Commit and deploy"):

1. Fix commit **e20aa6d0** landed on `fix/a03-live-data-and-pending-work` by compare-and-swap from c99d0ec3, after the M58 session's deploy finished (it asked other sessions to hold). It was rebased over M51, M55 and M58; `controllers/a09/writable.py` was regenerated with `form_fields.py --a09`, and only the M56 entries differ from M58's. The combined tree passed 699 static checks (M58's guard included) and the M56 live tests plus the A09 control suites on the clone. **Not pushed.**
2. Backups in `_migration/backups`: `fix_real_pre_m56_capture_2026-11-18.dump` (50.1 MB), `fix_dev_pre_m56_capture_2026-11-18.dump` (45.7 MB).
3. `-u cd_payroll_bd,cd_p03_portal` on fix_real and fix_dev: exit 0, no errors; cd_payroll_bd 19.0.0.4.0 on both. The version-gap check (every installed `cd_` module against the shared checkout) is 0 on both.
4. Restarts: 8069 PID 63524 became 50664 (155 modules, no error line, login 200); 8090 PID 47236 became 50852 (151 modules, no error line, login 200).
5. Both databases build the backend bundle ae3f144, which carries every new M56 form and list.

fix_real holds no payroll run, contract, declaration, membership or opening provision, so the new lists are empty until payroll records them; it has **no Payroll Officer** (spec Q-09).

Cleanup: the clone `fix_test_m56` and its filestore were dropped, the private server's launch entry removed, and the worktree removed; branch `fix/m56-capture-buttons` is kept.
