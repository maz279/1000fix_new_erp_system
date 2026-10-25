# A08 · Finance & Treasury — Audit Findings and Target Specification (2026-10-26)

Basis: the code at `38275123` (branch `feature/production-readiness-remediation`).
Sources for the target:
- a live inspection of all eight modules in the P03 workspace;
- the backend inventory below;
- web research on SAP S/4HANA, Dynamics 365 Finance, NetSuite, Odoo 19 and OCA, plus Bangladesh NBR, Bangladesh Bank and PwC tax summaries. The sourced research notes are in `audit_analysis/A08_FINANCE_RESEARCH.md`.

Bangladesh statutory values that could not be confirmed against a primary NBR text are marked "verify with the company's VAT/tax adviser". They must be stored as effective-dated master data, never hard-coded.

## 1. What the audit found

### 1.1 Workspace vs backend coverage

| Module | Registry screens | Wired before | Unwired before |
|---|---|---|---|
| M19 GL | 14 | 14 | 0 |
| M20 AR | 15 | 15 | 0 |
| M52 AP & Expense | 12 | 3 | 9 |
| M50 Treasury | 15 | 5 | 10 |
| M51 Tax (BD) | 13 | 7 | 6 |
| M53 Rev Rec & Settlement | 9 | 4 | 5 |
| M49 Fixed Assets | 10 | 2 | 8 |
| M54 Costing & FP&A | 14 | 2 | 12 |
| **Total** | **102** | **52** | **50** |

### 1.2 Discrepancies seen on screen
- **Unrelated data on unwired screens.** Every unwired finance screen fell back to the generic service-order grid. It showed repair filters ("Diagnosing", "QC Check", "My Branch (Elephant Rd)", "SLA At-Risk") and repair cards. For example, *M52 Payment Runs* listed "SO000062 Galaxy A55". **Fixed in `35d42497`:** such a screen now shows an honest "not built yet" panel.
- **Finance data visible to any employee.** The generic finance list API read with `sudo()` for any internal user, bypassing the accounting access rules, and returned raw exception text. **Fixed in `35d42497`.**
- **No way to create or open records.** Model lists could not create a record or open one. **Fixed in `35d42497`:** "+ New" and "Open full record" open the model's own Odoo form in a dialog.

### 1.3 Built in the backend but unreachable from the workspace

| Area | Unreachable models | Unreachable actions |
|---|---|---|
| GL | `fix.chart.loader` (load/reconcile/link) | `fix.financial.report.bridge.action_generate_report`, `fix.period.close.action_fail_close_target` |
| Multi-entity | `fix.consolidation.book` (run, eliminations), `fix.elimination.entry`, `fix.intercompany.rule`, `fix.intercompany.transaction` (mirror, match), `fix.nil.return.generator` (verify, generate packs, record NBR acknowledgement) | — |
| AR | — | `fix.ar.invoice.action_register_paid`, `fix.credit.profile.action_toggle_hold` |
| Tax | — | `fix.vat.return.action_file_online`, `fix.vat.return.action_subledger_reconciliation` |
| Settlement | `fix.payout.reconciliation` (run) | `fix.seller.statement.action_issue_statement`, `fix.seller.statement.action_settle_statement`, `fix.payout.run.action_query_status`, `fix.payout.run.action_post_payout_to_gl` |
| Subscriptions / AMC | `fix.subscription` (generate charge, dunning, reinstate, refund) | `fix.revenue.schedule.action_recognize_period` |

### 1.4 Standard modules available but not installed
These ship with vendor Odoo 19 or OCA:
- `account_asset_management`
- `account_check_printing`, `account_check_deposit`
- `account_debit_note`
- `account_financial_report`
- `mis_builder`, `mis_builder_budget`, `mis_builder_cash_flow`
- `partner_statement`
- `account_tax_balance`
- `hr_expense`
- `purchase`
- `l10n_bd`

Decision: **do not install** these in this pass. The custom `fix.*` finance models already own these concepts (assets, budgets, vendor bills, expense claims, Mushak). Installing parallel standard modules would create two sources of truth. A later, separate decision can migrate onto OCA.

## 2. Rules for every A08 screen

1. Every registry screen is backed by a real model or a real computation over posted data. Placeholders, constants and demo rows are not allowed. A screen that needs an external party it cannot reach shows that honestly, for example "bank file generated — awaiting the bank's confirmation".
2. Each screen is declared in `static/src/a08/<module>.js` (`MODULE`, `SCREENS`, `REPORT_ROUTES`, `FORM_MODELS`, `CREATE`). Its backend is declared in `controllers/a08/<module>.py`:
   - `SURFACES`: model → order, limit and the workflow methods screens may call;
   - optional `kpis(env)` for the module's KPI tiles;
   - optional `REPORTS = {name: fn(env, date_from=None, date_to=None, **params)}`.

   There are two screen kinds:
   - **`model_list`**, the default for record screens:
     `{kind: 'model_list', model, cols, stateField?, domain?, actions?: [{m, l}], create?: false, context?}`.
     The workspace adds "+ New" and "Open full record", both of which open the model's own form.
   - **`table_report`**, for computed screens (ageing, forecasts, schedules, P&L, calendars):
     `{kind: 'table_report', module: 'M52', report: 'ap_ageing', params?, period?: false}`.
     The report function returns `{cols, labels, rows, totals?, notes?, title?, empty?}` and reads with the caller's environment, so the models' own access rules apply.

   Do not edit the shared workspace files: `p03_workspace.js/.xml`, `p03_modules_meta.js`, `p03_i18n.js`, `p03_generic_api.py` and `p03_finance_api.py`.
3. Rates, thresholds and statutory due days are effective-dated master data (`date_from`/`date_to`) with seeded defaults, so the adviser can correct them without code.
4. Money uses `Monetary` fields with the company currency (BDT). Postings go through `account.move` on configured accounts. A missing account fails closed; nothing is created silently.
5. Access control:
   - Read for `account.group_account_readonly`.
   - Write for `account.group_account_user`.
   - Approvals and settings for `account.group_account_manager`.
   - Never `base.group_user` write on financial records.
   - Company record rules on every model.
6. Every user-visible string has a Bengali counterpart. Registry entries carry `bn`. Model and field strings go into the addon's `bn_BD.po`/`.pot`. Bengali text must not contain Latin words outside the whitelist in `tests/test_i18n_separation.py`.
7. Every new model and action has ORM tests under the addon's `tests/`, run with the `odoo_env` fixture against `fix_test`. Every touched module is upgraded on `fix_dev` and `fix_test`.

## 3. Target per module
Each module has five kinds of change:
- **keep:** stays as wired;
- **build:** an existing registry screen gets a real backend;
- **rename:** a screen changes name or scope;
- **move out:** the screen belongs to another area; finance keeps only the posting;
- **add:** a screen not yet in the registry.

### M19 · Financial Accounting & GL (`cd_gl_ext`, `cd_multi_entity`)
- **Keep:** all 14 screens.
- **Add — Ledger group:**
  - **CoA Master Loader**: `fix.chart.loader` with load, reconcile and link actions.
  - **Recurring & Accrual Journals**: `fix.journal.template`, plus a generate action if one is missing.
- **Add — new "Group & Inter-Branch" group:**
  - **Consolidation Books**: run, generate eliminations.
  - **Eliminations**.
  - **Inter-Company / Inter-Branch Transactions**: mirror, match, due-to/due-from balances.
  - **Inter-Company Rules**.
- **Add — Close group:**
  - **Statutory Report Bridge**: `fix.financial.report.bridge`.
  - **Nil-Return Packs**: `fix.nil.return.generator`, under Close or cross-linked from M51.

### M20 · AR, Invoicing & Collections (`cd_billing_engine`)
- **Keep:** all 15 screens.
- **Wire:** `action_register_paid` (invoice) and `action_toggle_hold` (credit profile) on their screens.
- **Add — Customer VDS Certificates (Mushak 6.6 received):** corporate customers deduct VDS from 1000 FiX invoices. Record each certificate against the invoice, settle the receivable for the VDS part, and claim it in the 9.1 return. This is a new model.

### M52 · AP & Employee Expense (`cd_ap_ext`)
- **Keep:** Vendor Bills, Match Exceptions, Expense Claims.
- **Build:**
  - **Approval Workflow:** an amount-based approval matrix on vendor bills with states draft → to approve → approved → rejected, plus an approver log.
  - **Payment Runs:** a payment proposal that selects approved, due bills, nets debit notes, applies TDS/VDS, gets approval, then creates `fix.payment.execution` rows on the BEFTN/RTGS/NPSB/cheque rail. The bank confirmation comes later.
  - **TDS / VDS at Source:** deduction lines per bill or payment from effective-dated rate tables. The ITA 2023 section is shown. A payee without a return-filing proof is deducted at 1.5x (verify).
  - **Debit / Credit Notes:** vendor notes linked to bills (Mushak 6.8/6.7 references).
  - **Advances & Floats:** employee advances with settlement against claims and recovery of any balance.
  - **Per-Diem & Mileage:** effective-dated rate master; claim lines computed from it.
  - **Expense Policy:** limits per category and grade, enforced on claim submission.
  - **AP Ageing:** buckets from bill due dates.
  - **GRNI Accruals:** goods received but not invoiced, from receipts recorded on vendor purchase orders (`cd_vendor_portal` / `cd_inventory` models; investigate). If there is no receipt source, show the honest state.
- **Add — Vendor Tax Profile:** TIN, BIN, return-filing proof and its expiry; this drives TDS/VDS.

### M50 · Treasury & Banking (`cd_cash_position`)
- **Keep:** Cash Position, Statements Import, Auto Reconciliation, BEFTN/RTGS Instructions, MFS Disbursement.
- **Build:**
  - **Bank Account Master:** wire Odoo `account.journal` (type bank) and `res.partner.bank` through a finance view; add the BD fields (branch routing number, account type).
  - **Branch Cash Consolidation:** from `cd_front_desk` cash shifts, per branch per day, with deposit reconciliation.
  - **Rider COD Settlement:** COD collected per rider/trip against deposits and variances, from the logistics models if present. Finance owns only the settlement.
  - **Petty Cash (Imprest):** imprest funds per branch, vouchers, top-ups and reconciliation.
  - **Cheque Management:** issued and received cheques, post-dated, cleared, bounced.
  - **Gateway / MFS Settlement:** a bKash/Nagad/SSLCOMMERZ settlement batch with three-way matching of receipts, gateway report and bank credit, and a fees line. The gateway report arrives as an import with a CSV parser; no gateway API is called.
  - **Cash-in-Transit:** deposits between branch and bank.
  - **Cash-Flow Forecast:** a computed 13-week view from AR due dates, AP due dates, payment runs and recurring items, with actuals vs forecast.
  - **Facilities & Covenants:** loans and overdraft limits, utilisation, repayment schedule, covenant tests.
  - **FX Holdings:** foreign-currency balances per bank journal, valued at the latest rate.

### M51 · Tax & Regulatory (BD) (`cd_tax_engine_bd`)
- **Keep:** Mushak 6.1, 6.2, 6.3, VAT Return 9.1, TDS Register, Certificates, Tax Determination.
- **Wire:** `action_file_online` and `action_subledger_reconciliation` on 9.1.
- **Build:**
  - **Challans (A-Challan / e-payment):** treasury deposits linked to VAT, TDS and VDS liabilities. The challan number and date are user-entered.
  - **Input Credit Tracking:** input VAT per purchase (6.1), eligibility, and claim period.
  - **VDS:** VDS deducted on vendor payments, deposit, and Mushak 6.6 certificates issued. Service-code rates are effective-dated.
  - **Rename "High-Value NID Capture" to "Mushak 6.10 High-Value Register":** transactions above the threshold (BDT 200,000; verify).
  - **Statutory Calendar:** computed due dates for 9.1 (15th), TDS/VDS deposits, quarterly withholding return (25th after the quarter) and annual returns, with status. Due days are master data.
  - **Audit Support Pack:** a per-period export bundle of the registers with checksums.
- **Add:**
  - **Tax Rate Master:** effective-dated VAT and TDS/VDS rates with sections, and the non-filer multiplier.
  - **Credit / Debit Note Register (6.7 / 6.8).**

### M53 · Revenue Recognition & Settlement (`cd_settlement_ext`, `cd_subscription`, plus finance-side reads of `cd_partner` and `cd_marketplace`)
- **Keep:** Revenue Schedules, Commission Ledger, Payout Runs, Seller Statements.
- **Wire:** seller statement issue/settle; payout query status and post to GL; revenue recognise-period.
- **Build:**
  - **Performance Obligations (IFRS 15):** per contract — AMC service, workmanship warranty, parts — with allocation of the transaction price and links to schedules.
  - **Contract Assets & Liabilities:** computed from billed vs recognised per contract.
  - **Partner / Referral Payouts:** partner commissions payable from `cd_partner`, paid in payout runs.
  - **Escrow & Clawbacks:** marketplace amounts held during disputes and clawbacks against future payouts.
- **Rename "Incentive Schemes" to "Commission Schemes":** seller and partner commission rate tables. Technician incentives **move out** to Payroll (A09).
- **Add:**
  - **AMC & Subscription Contracts:** `fix.subscription` with generate charge, dunning, reinstate and refund.
  - **Payout Reconciliation:** `fix.payout.reconciliation`, run.
  - **Warranty Provision (IAS 37):** workmanship-warranty provision per period from repair revenue and claim history, posted to GL.

### M49 · Fixed Assets & Capex (`cd_fixed_asset_ext`)
- **Keep:** Asset Register, CWIP.
- **Build:**
  - **Capex Requests:** request → approve → link to the capital budget → CWIP.
  - **Capital Budget.**
  - **Transfers & Custodians:** branch and custodian moves with a history.
  - **Dual-Book Depreciation:** book (straight-line over useful life) and tax (ITA 2023 Third Schedule reducing-balance rates; master data, verify) run per period with GL posting.
  - **Schedules & Movements:** opening, additions, disposals, depreciation and closing per category.
  - **Revaluation & Impairment (IAS 16 / 36).**
  - **Disposal & Write-Off:** proceeds and gain/loss posting.
  - **Physical Verification:** campaigns, scanned tags, missing/found results.
- **Add — Leases (IFRS 16):** branch rents as right-of-use asset and lease liability, with the schedule, interest and depreciation postings.

### M54 · Costing, Budget & FP&A (`cd_fpa`)
- **Keep:** Operating & Capital Budgets, Allocation Cycles.
- **Build:**
  - **Cost Pools & Elements.**
  - **Job / Work-Order Costing:** per service order, parts consumed (inventory consumption) plus labour hours × the loaded technician rate, against revenue.
  - **Technician Loaded Cost:** payroll cost plus overhead share divided by productive hours, per period.
  - **Business-Line P&L:** from the GL by business-line dimension. The registry says 14 lines; the label must come from master data.
  - **Branch Profitability.**
  - **Customer Profitability.**
  - **Unit Economics.**
  - **Budget Workflow:** draft → submitted → approved, by version.
  - **Variance Analysis:** budget vs actual from the GL.
  - **Rolling Forecast.**
  - **Scenario Modelling:** driver-based versions.
  - **Board Pack:** a period summary assembled from the above.

### Moved out of A08
These go to their owning areas; finance keeps only the posting and reconciliation:
- **Technician incentives** → Payroll (A09).
- **Rider COD app** → Logistics.
- **Seller onboarding and KYC** → the Marketplace portal.

## 4. Out of scope (external)
- Live gateway, bank and NBR APIs.
- Adviser sign-off of the statutory rate and form matrix.
- Installing OCA or standard finance modules: needs a separate decision.
