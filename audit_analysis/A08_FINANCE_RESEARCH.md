# A08 Finance & Treasury: Reference Research for 1000 FiX (Odoo 19 CE + custom)

Research date: 2026-10-25. Scope: what a top-class ERP provides per module, Bangladesh statutory requirements, industry-specific functions and out-of-scope items.

**Labels**
- **CORE**: must-have for 1000 FiX at go-live or year 1.
- **ADV**: advanced. Phase it in later, or skip it.
- **[OCA]**: an OCA module can cover the item on Odoo CE.
- **[CUSTOM]**: needs a custom build.

**Evidence levels**
- **verified**: confirmed against an authoritative secondary source such as PwC, IFRS.org or IFAC.
- **secondary**: comes from a blog or vendor source only.
- **unverified**: I could not confirm it.

> Key platform caveat: Odoo **Community** ships "Invoicing", not the full Accounting app. Odoo's documentation describes Invoicing as a standalone app and Accounting as the fuller solution ([Odoo 19 Accounting docs](https://www.odoo.com/documentation/19.0/applications/finance/accounting.html)). The following are Enterprise features in Odoo, to the best of my knowledge (not confirmed from the editions page, whose table did not render): the bank reconciliation widget, financial reports, assets, deferred revenue/expense, budgets, follow-ups, bank sync, consolidation and the tax-return report. On CE they must come from OCA or custom code. Confirmed on OCA 19.0: `account_reconcile_oca` and `account_statement_base` exist ([OCA/account-reconcile 19.0](https://github.com/OCA/account-reconcile/tree/19.0)). `account-financial-tools` has 41 modules on 18.0, including asset management, fiscal year, lock dates, netting, loans, spread cost/revenue and move templates ([OCA/account-financial-tools 18.0](https://github.com/OCA/account-financial-tools/tree/18.0)); I did not confirm their 19.0 port status. Check each OCA repo's 19.0 branch before committing to it.

Benchmark ERP references used for the feature lists. These are general product knowledge from vendor documentation, not per-feature fetched pages:
- SAP S/4HANA Finance: Universal Journal, Bank Reconciliation, Cash Management, Payment Run F110, Asset Accounting, RAR, Group Reporting. https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE
- Microsoft Dynamics 365 Finance: cash forecast across currencies and legal entities, filterable by bank account and dimensions, ML-based customer payment prediction ([MS Learn, cash forecast](https://learn.microsoft.com/hr-hr/dynamics365/finance/finance-insights/cash-flow-forecast-intro)). Also vendor payment proposals, three-way matching, subscription billing and revenue recognition. https://learn.microsoft.com/en-us/dynamics365/finance/
- Oracle NetSuite: Advanced Revenue Management, SuiteBilling, Fixed Assets Management and the Bank Reconciliation workspace. https://docs.oracle.com/en/cloud/saas/netsuite/
- Odoo 19 docs, as listed in the caveat above.

---

## M19 Financial Accounting & General Ledger

| Sub-module / screen | Functions | Tag |
|---|---|---|
| Chart of Accounts (BD, BFRS-aligned) | Account groups and types; mapping to the statement of financial position, P&L, cash-flow and notes lines; account code length control | CORE |
| Multi-branch / analytic dimensions | Branch (51+), division (8), service line (IT/mobile/appliance), channel (walk-in/on-site/pick-drop/B2B/marketplace), cost centre, technician team. Odoo 17+ analytic plans plus Odoo "branches" (sub-companies). | CORE |
| Journals & sequences | Separate journal and gap-free sequence per branch and document type. Mushak 6.3 needs a separate series per location ([VAT slideshow, secondary](https://www.slideshare.net/slideshow/vat-accounting-system-new-vat/238108531)). [OCA account_journal_general_sequence / account_move_name_sequence] | CORE |
| Journal entry workbench | Manual journal entries with attachments, recurring/template entries [OCA account_move_template], reversal and auto-reversal accruals, maker-checker approval on manual journal entries | CORE |
| Period & year-end close | Fiscal year July–June [OCA account_fiscal_year], lock dates per journal [OCA account_journal_lock_date], close checklist / task cockpit, retained earnings roll, year-end closing entries | CORE (checklist = ADV) |
| Inter-branch / inter-company | Due-to/due-from per branch, auto-balancing, elimination; inter-company if group entities exist (check whether 1000 FiX has sister companies) | CORE (inter-branch), ADV (inter-co, consolidation) |
| Multi-currency | BDT functional currency; USD/CNY for parts imports; Bangladesh Bank rate import; realized and unrealized FX revaluation (IAS 21) | CORE |
| Financial statements | Statement of financial position, P&L/OCI, changes in equity, cash flow (indirect), trial balance, GL, partner ledger, aged balances. [OCA account-financial-reporting, mis_builder] | CORE |
| Statutory pack & notes | BFRS/IFRS note disclosures, Companies Act schedule formats, audit trail and inalterability report; auditor (ICAB firm) read-only access | CORE |
| Audit trail | Immutable posted entries, posting user and date [OCA account_move_post_date_user], hash chain | CORE |
| Consolidation / group reporting | Multi-entity consolidation, minority interest | ADV |
| Continuous close / AI anomaly detection | Duplicate journal entry detection, unusual posting alerts | ADV |

## M20 Accounts Receivable, Invoicing & Collections

| Sub-module / screen | Functions | Tag |
|---|---|---|
| Customer invoicing | Invoice from the job card or service order (labour + parts + call-out fee), Mushak 6.3 print and PDF, multi-tax lines (VAT/SD), cash rounding, B2C walk-in receipts | CORE |
| Credit notes / debit notes | Linked to the original invoice; legal Mushak 6.7 / 6.8 output (see BD section) | CORE |
| Payment receipt & allocation | Cash, card (SSLCOMMERZ), bKash, Nagad, bank transfer and cheque; partial payments; advance/deposit receipts against bookings; unapplied cash | CORE |
| Customer statements & dunning | Follow-up levels, SMS/email reminders (Bangla), statement of account. [OCA credit-control / account_credit_control] | CORE |
| Credit management | Credit limits for B2B/corporate, hold on overdue, credit-limit approval workflow | CORE (B2B) |
| Aged receivables cockpit | Ageing by branch, channel and customer type; DSO; collector worklist | CORE |
| B2B billing | Consolidated monthly billing across many sites/tickets, PO-number capture, customer portal invoice download | CORE |
| Recurring / contract billing | AMC instalment billing schedules (links to M53) | CORE |
| OEM warranty claim receivables | Claim invoice to Samsung/Walton etc. per batch of warranty jobs; claim status (submitted/approved/rejected/short-paid); write-off of rejected claims | CORE (industry) |
| Expected credit loss (IFRS 9) | Provision matrix by ageing bucket and segment; bad-debt write-off approval | CORE (simple matrix) |
| Payment prediction / collections AI | Customer payment-date prediction (D365 Finance Insights style) | ADV |
| Lockbox / auto-cash application | Automatic matching of bank receipts to invoices with rules | ADV (partly covered by M50 reconciliation models) |
| E-invoicing / EFD integration | NBR EFD/SDC for retail counters, if mandated for the business category (see BD section) | CORE if mandated, else ADV |

## M52 Accounts Payable & Employee Expense

| Sub-module / screen | Functions | Tag |
|---|---|---|
| Vendor master & onboarding | TIN, BIN, bank (routing number), MFS wallet, TDS/VDS category, "return proof submitted" flag (PwC: payee without proof of return suffers WHT at 1.5x) | CORE |
| Vendor bills | From PO/receipt; OCR digitisation (ADV); Mushak 6.3 capture (supplier BIN and invoice number) for input credit | CORE |
| 2-way / 3-way match | PO ↔ GRN ↔ bill with price and quantity tolerances; match-exception queue | CORE |
| TDS/VDS at bill or payment | Auto-compute income tax withholding (ITA 2023 s.89/90/94/109) and VDS; withholding liability accounts; certificate generation (see BD section) | CORE |
| Payment proposal / payment run | Due-date and discount selection, approval workflow (amount-based multi-level), batch payment, BEFTN/RTGS/NPSB bank file, cheque printing. [OCA account_payment_order + custom BD bank formats] | CORE |
| Vendor advances & netting | Supplier advances, AR/AP netting for parties that are both [OCA account_netting] | CORE |
| Employee expense claims | Mobile receipt capture, per-diem/mileage for on-site technicians, approval, reimbursement via payroll or bKash | CORE |
| Employee advances / imprest | Technician cash advances, settlement against expense claims, ageing of open advances | CORE (industry) |
| Corporate card / fuel card reconciliation | Import of card statements and matching | ADV |
| Vendor portal | Bill status and remittance advice (overlaps with Vendor & Partner Portal, A-area 6) | ADV |
| Supplier statement reconciliation | Upload vendor statement and auto-match | ADV |

## M50 Treasury & Banking

| Sub-module / screen | Functions | Tag |
|---|---|---|
| Bank accounts master | Multiple banks/branches; MFS merchant wallets (bKash, Nagad) treated as cash-equivalent accounts; gateway clearing accounts (SSLCOMMERZ) | CORE |
| Statement import | CSV/MT940/CAMT import (BD banks mostly CSV/Excel); MFS settlement report import | CORE |
| Bank reconciliation workbench | Match, split, write-off, reconciliation models/rules, partial reconciliation. [OCA account_reconcile_oca 19.0 confirmed] | CORE |
| Gateway / MFS settlement reconciliation | Three-way match: order or receipt ↔ gateway transaction report (fees, VAT on fees) ↔ bank/wallet settlement credit; auto-book MDR fees | CORE (industry) |
| Cash management (branch cash) | Daily branch cash book, cash count/denomination, Z-report vs system, deposit slips [OCA account_cash_deposit], cash-in-transit, excess/shortage | CORE |
| Petty cash / imprest | Imprest float per branch, replenishment request and approval | CORE |
| Payments execution | BEFTN/RTGS/NPSB files or host-to-host; positive pay; payment status | CORE (file), ADV (H2H API) |
| Cheque management | Post-dated cheques received and issued, cheque deposit [OCA account_check_deposit], bounce handling | CORE |
| Cash position & forecast | Daily cash position; 13-week forecast from open AR/AP, payroll and tax calendar; scenarios (D365-style snapshots) | CORE (position), ADV (forecast) |
| Bank guarantees / LC / loans | Performance guarantees for corporate tenders; import LCs for parts; term loans and overdraft with amortisation [OCA account_loan]; covenant tracking | ADV (LC/guarantee may be CORE if tendering) |
| Investments / FDR | Fixed deposit register, accrued interest, maturity alerts, AIT on interest | ADV |
| Bank charges & FX | Auto-booking of charges; FX deals | ADV |

## M51 Tax & Regulatory (Bangladesh)

| Sub-module / screen | Functions | Tag |
|---|---|---|
| Tax master | VAT rates by service code/HS code (15% standard; reduced 1.5/2/2.4/4.5/5/7.5/10%), SD, VDS rates by service code, TDS sections and rates, effective-dated | CORE |
| VAT registers | Mushak 6.1 purchase register, 6.2 sales register, 6.2.1 purchase-sales register; generated per BIN (central or branch registration) | CORE |
| VAT documents | 6.3 tax invoice, 6.4, 6.5 transfer, 6.6 VDS certificate, 6.7 credit note, 6.8 debit note, 6.10 high-value transactions | CORE |
| Monthly VAT return | Mushak 9.1 working, with notes/schedules, input-output reconciliation, carry-forward; export/upload support for the NBR IVAS portal | CORE |
| VDS management | Received side (corporate customers deduct VDS, 6.6 received → adjust in 9.1) and paid side (1000 FiX as withholding entity: deduct, deposit, issue 6.6) | CORE |
| Income tax withholding | TDS at bill/payment, deposit via A-challan/e-payment, withholding certificates, quarterly withholding return | CORE |
| Advance income tax / tax provision | AIT on imports and receipts (tracked as a tax asset), current tax provision, deferred tax (IAS 12), minimum tax computation | CORE |
| Challan register | A-challan / e-payment reference capture, linking each challan to the liabilities it settles | CORE |
| Tax calendar & compliance cockpit | Due dates, status, evidence, penalty/interest calculator | CORE |
| Tax audit / assessment tracking | Notices, assessments, appeals, disputed amounts (contingent liabilities) | ADV |
| Transfer pricing | Only if related-party international transactions exist | ADV / likely N/A |

## M53 Revenue Recognition & Settlement

| Sub-module / screen | Functions | Tag |
|---|---|---|
| IFRS 15 contract engine | Contracts, performance obligations (PO), standalone selling price (SSP) and allocation for bundles (e.g. AMC + parts discount + priority SLA) | CORE (simple), ADV (full SSP allocation) |
| Deferred revenue schedules | AMC fees received upfront → contract liability → recognise monthly (straight line for stand-ready obligation) or per visit. Odoo deferred revenue is Enterprise; OCA account_spread_cost_revenue | CORE |
| Point-in-time revenue | Repair job revenue on job completion/delivery; contract asset for unbilled completed jobs (WIP at month end) | CORE |
| Extended warranty sold | Warranty sold separately = service-type warranty → separate PO, deferred revenue | CORE (if sold) |
| Marketplace settlement | Principal vs agent determination (IFRS 15 B34–B38): for third-party seller sales, recognise only commission (net). Seller ledger, commission, fees, TDS/VDS deduction, payout batches, statements. | CORE (industry) |
| COD settlement | Rider/courier collections → COD receivable per rider/3PL → remittance matching → short/excess | CORE (industry) |
| Gateway settlement | Gross receipt vs net settlement; MDR fees; refunds/chargebacks (shared with M50) | CORE |
| OEM reimbursement settlement | Warranty job revenue billed to OEM; variable consideration (expected rejection rate) constraint | CORE (industry) |
| Revenue waterfall / RPO disclosure | Remaining performance obligations, deferred revenue roll-forward | ADV |
| Contract modifications / ASC 606-style full engine (SAP RAR / NetSuite ARM) | — | ADV |

## M49 Fixed Assets & Capex

| Sub-module / screen | Functions | Tag |
|---|---|---|
| Asset register | Asset classes (tools and diagnostic equipment, vans/motorbikes, IT, furniture, branch fit-out/leasehold improvements), tag/barcode, location = branch, custodian = technician | CORE |
| Acquisition | From vendor bill / PO; CWIP / AUC for branch fit-outs → capitalise [OCA account_asset_transfer] | CORE |
| Depreciation | Straight-line/reducing balance, prorata, batch run [OCA account_asset_management, account_asset_compute_batch]; separate tax depreciation per ITA 2023 Third Schedule (unverified detail) → deferred tax | CORE (book), CORE (tax book, for deferred tax) |
| Transfers / disposals | Inter-branch transfer, sale/scrap with gain/loss | CORE |
| Low-value assets | Expense or pool small tools [OCA account_asset_low_value]; tool-kit issued to technicians tracked as custody, not capitalised | CORE |
| Physical verification | Periodic count via mobile scan, reconcile register | CORE |
| Leases (IFRS 16) | Branch rent leases (51+ branches): ROU asset, lease liability, discount rate (IBR), payment schedule, interest/depreciation, modifications/renewals; short-term/low-value exemption; rent payments carry TDS (s.109) and VDS | CORE (industry) |
| Revaluation (IAS 16) / impairment (IAS 36) | Revaluation model, CGU impairment test for loss-making branches | ADV (impairment indicator check is CORE annually) |
| Capex budgets & requests | Capex request → approval → PO, budget vs actual per project | CORE (simple), ADV (full project capex) |
| Componentisation, asset insurance, maintenance link | — | ADV |

## M54 Costing, Budget & FP&A

| Sub-module / screen | Functions | Tag |
|---|---|---|
| Job costing | Cost per service job: parts (FIFO/AVCO from stock), technician loaded labour (hours × rate), travel/fuel, logistics → job margin | CORE (industry) |
| Technician loaded cost rate | Salary + benefits + incentives + vehicle + tools depreciation + training ÷ productive hours; period recalculation | CORE |
| Branch P&L / profitability | Allocation of HQ overheads (rent, call centre, IT) by drivers (tickets, revenue) | CORE |
| Service-line & brand profitability | OEM warranty vs out-of-warranty vs AMC vs marketplace margin | CORE |
| Budgeting | Annual budget (July–June) by branch × account × month; versions; approval; budget vs actual with variance. Odoo budgets = Enterprise; OCA account-budgeting / mis_builder_budget | CORE |
| Budget control | Commitment/encumbrance checks on PO and expense | ADV |
| Rolling forecast / driver-based planning | Ticket volume × mix × price drivers; scenario | ADV |
| KPI dashboards | Gross margin per job, first-time-fix cost, parts cost %, DSO/DPO, cash conversion | CORE (overlaps with A-area 7 Analytics/Metabase) |
| Standard costing / activity-based costing (ABC) | — | ADV |

---

## Bangladesh Statutory Requirements

> Institutional change: the Revenue Policy and Revenue Management Ordinance 2025 dissolved the NBR into a Revenue Policy Division and a Revenue Management Division. As of reports through Aug 2026 the split was still being implemented, with the NBR still operating under an acting chairman ([Dhaka Tribune](https://www.dhakatribune.com/bangladesh/381065/govt-dissolves-nbr-splits-revenue-sector-into-two), [Daily Star, rules of business](https://www.thedailystar.net/news/nbr-split-rules-business-approved-4086301), [Bonik Barta opinion](https://en.bonikbarta.com/opinion/necXcymEdZfXpt1P)). Keep authority names configurable. Status in Oct 2026: unverified.

### 1. VAT and Supplementary Duty Act 2012 / VAT & SD Rules 2016

| Item | Requirement | Evidence |
|---|---|---|
| Standard rate | 15% | verified ([PwC, last reviewed 31 Jul 2026](https://taxsummaries.pwc.com/bangladesh/corporate/other-taxes)) |
| Reduced rates | 1.5%, 2%, 2.4%, 4.5%, 5%, 7.5%, 10% (Second Schedule); goods from a non-manufacturer at 7.5% → "procurement provider" | verified (PwC) |
| Repair/maintenance service rate | Service code S031.00 (repair & maintenance). Which VAT rate applies to 1000 FiX's repair services (15% vs a reduced rate) and to parts sold separately: **unverified**. Needs the current Second/Third Schedule and SROs. | unverified |
| Registration / turnover tax | PwC: registration if turnover > BDT 5m; turnover tax 4% for BDT 3m–5m (enlistment). A secondary source claims BDT 8m. FY2026-27 budget introduced a simplified fixed-amount turnover tax for small retailers. Irrelevant to 1000 FiX (well above the threshold), but marketplace sellers may be enlisted, not registered → their invoices may not support input credit. | PwC verified; 8m figure unverified ([vatupdate](https://www.vatupdate.com/2026/06/16/budget-2026-27-introduces-simplified-turnover-tax-and-sweeping-indirect-tax-incentives/)) |
| Mushak 6.1 | Purchase register | secondary ([iBOS](https://ibos.io/?p=84691)) |
| Mushak 6.2 | Sales register | secondary |
| Mushak 6.2.1 | Purchase-sales register (for traders / commercial importers) | from domain knowledge, unverified online |
| Mushak 6.3 | Tax invoice, Rule 40(1). Required fields: serial number (per fiscal year, per location), date/time, supplier and buyer name/BIN/address, description, quantity, value, VAT rate and amount, SD, signature. Two copies. | secondary ([rakibhassan](https://rakibhassan.eu/mushak-6-3-vat-invoice-bangladesh/), [slideshare](https://www.slideshare.net/slideshow/vat-accounting-system-new-vat/238108531)) |
| Mushak 6.4 | Contractual production invoice (movement of inputs/outputs between principal and contract manufacturer); likely N/A for 1000 FiX | secondary |
| Mushak 6.5 | Transfer invoice (goods moved between branches/warehouses of a central-registered entity). **Relevant**: parts moved between 51+ branches. | from domain knowledge; I could not confirm it online |
| Mushak 6.6 | VDS certificate issued by the withholding entity to the supplier. Contents: both BINs, related 6.3 number, VDS amount, challan number. Deadline reported as 3 working days after deposit (one source) or by the 8th–10th of the next month (another); **conflicting**. | secondary ([rakibhassan 6.6](https://rakibhassan.eu/mushak-6-6-vds-certificate-guide-in-bd-2026/)) |
| Mushak 6.7 / 6.8 | Credit note / debit note (returns, price changes); adjusted in 9.1 | domain knowledge; current form numbers not confirmed from a primary source |
| Mushak 6.10 | Information on purchase/sale invoices above BDT 200,000 (Rule 42); submitted with the return; exception for NBR-approved POS/ECR/computer systems (as reported) | secondary |
| Mushak 9.1 | Monthly VAT return due by the 15th of the following month: output, input, VDS, adjustments, payment (challan) | secondary; 15th widely reported |
| VDS | Withholding entities (PwC): government bodies, approved NGOs, banks/FIs, educational institutions, **limited companies**, entities with turnover > BDT 100m. **1000 FiX (a Ltd company) is a withholding entity.** Rates 2–15% by service code. Excluded: fuel, gas, WASA, electricity, telephone and mobile bills. Deposit deadline: conflicting secondary sources ("within 15 working days" vs "by the 7th of next period" citing s.14(6) and an SRO, rakibhassan blog). VDS section in the Act is commonly cited as s.49: **unverified**. | PwC verified for entities and rates; deadlines unverified ([PwC](https://taxsummaries.pwc.com/bangladesh/corporate/other-taxes), [rakibhassan TDS/VDS](https://rakibhassan.eu/tds-vds-rate-bangladesh-2025-26/)) |
| VDS on branch rent | Rent service S074.00, VDS 15% (secondary). Also affects the IFRS 16 payment schedule. | secondary |
| VDS received | Corporate/B2B and government customers will deduct VDS on 1000 FiX's repair invoices → receivable shortfall must be matched to the 6.6 received and claimed in 9.1 | domain logic |
| EFD/SDC | NBR mandated EFD in 25 retail sectors (2019) and for highway hotels/restaurants (2025); devices report to EFDMS. Whether repair service centres are covered: **unverified**. | ([Daily Star 2019](https://www.thedailystar.net/news/business/businesses-have-use-electronic-fiscal-devices-nov-1-1620505), [BSS 2025](https://www.bssnews.net/business/251078)) |
| e-payment | VAT, SD, turnover tax and penalties payable by e-payment from a bank account via RTGS → IVAS / iBAS++ confirmation; e-VAT refunds via BEFTN (Jan 2026) | news ([Daily Star](https://www.thedailystar.net/business/news/nbr-takes-one-big-step-towards-automation-1931693)) |

### 2. Income Tax Act 2023 (withholding / TDS) and corporate tax

| Item | Requirement (FY2025-26 basis; check the Finance Act 2026) | Evidence |
|---|---|---|
| s.89 contractors/suppliers | Annexure rates 0.5%–10%; manufacturing/construction/engineering 5%; items not listed 5%; cement/iron 2%; industrial raw/packing materials 3%. Base excludes VAT. One source reports a 3/5/7% slab system instead: **conflict**; PwC shows item-based rates. | PwC ([WHT](https://taxsummaries.pwc.com/bangladesh/corporate/withholding-taxes)) |
| s.90 services | Advisory/consultancy 7.5% (company) / 15% (individual); technical services 10% / 15%; cleaning, security and manpower 10% on commission or 1% on gross; catering, event, courier and training 2% of gross; **sharing-economy platform services (incl. repair) 2%**; other services 10% | PwC |
| s.94 commission | Commission/discount/fees 10%; distributor promotion 1.5%; indenting commission 7.5% | PwC (section number from secondary sources) |
| s.109 rent | House property, premises and warehouses 10% (raised from 5% in FY2025-26 per secondary sources) | PwC (rate); section number secondary |
| Penalty rate | WHT increases by 50% if the payee does not show proof of return submission (PSR) | PwC |
| Withholding return | Quarterly, due on the 25th of the month after quarter-end; Withholder ID being replaced by TIN | PwC |
| Deposit deadline / certificates | Exact deposit days and certificate form/timing (Withholding Tax Rules 2024 referenced): **unverified** | secondary |
| Corporate tax | Non-listed company 27.5%, or 25% if all transactions go through bank transfer (the full cash-limit conditions are not stated by PwC; **unverified**). Minimum tax on gross receipts 1% (general). The FY2026-27 budget reportedly replaces minimum-tax withholding with a refundable advance tax (details unverified). | PwC ([CIT](https://taxsummaries.pwc.com/bangladesh/corporate/taxes-on-corporate-income)); KPMG ([FY27](https://kpmg.com/us/en/taxnewsflash/news/2026/07/tnf-bangladesh-tax-measures-in-national-budget-fy-2026-2027.html)) |
| Income year | Typically 1 July–30 June; assessment year starts 1 July after year end | PwC |
| Governing SRO | TDS rates per SRO 161-Law/Income Tax-36/2024 as amended by Finance Ordinance 2025 | secondary ([rakibhassan](https://rakibhassan.eu/tds-vds-rate-bangladesh-2025-26/)) |

### 3. Payments: challans and rails

- **A-challan (automated challan) under iBAS++ / SPFMS**: replaced manual treasury challans. It covers about 196 revenue types including income tax and VAT, payable at Bangladesh Bank and scheduled bank branches ([Dhaka Tribune](https://www.dhakatribune.com/amp/business/225908/automated-challan-system-launched), [TBS](https://www.tbsnews.net/economy/nbr/automated-challan-system-launched-142762)). The ERP should store the challan number, date, bank, code and amount, and link them to each liability.
- **BD-RTGS**: customer BDT transfers of BDT 100,000 and above; no minimum for government payments. Hours revised from 5 Oct 2025 (timetable not found) ([UNB](https://unb.com.bd/category/Business/this-is-how-rtgs-funds-transfer-works/115300), [TBS](https://www.tbsnews.net/node/1445526)).
- **BEFTN**: batch clearing in 3 sessions per working day; suited to vendor and seller payouts. Per-bank limits apply.
- **NPSB**: real-time and 24/7. Per-transaction and daily limits are conflicting and appear to be bank-set: **unverified** ([nsave](https://nsave.com/bangladesh/npsb)).
- The ERP should generate bank-specific bulk files (BEFTN CSV formats differ by bank: **unverified**, needs confirmation from the company's banks) and capture the 9-digit routing number (domain knowledge).

### 4. Financial reporting framework and company law

- **Financial Reporting Act 2015**: the FRC issues IFRS-conforming standards for Public Interest Entities. PIE tests per the FRC: revenue ≥ BDT 500m, or any two of external liabilities ≥ BDT 100m, assets ≥ BDT 300m, ≥ 50 employees. **1000 FiX is very likely a PIE**, so IFRS as adopted in Bangladesh applies ([IFRS.org profile](https://ifrs.org/use-around-the-world/use-of-ifrs-standards-by-jurisdiction/view-jurisdiction/bangladesh), [IFAC](https://ifac.org/about-ifac/membership/profile/bangladesh), [FRC presentation Nov 2025](https://www.ifrs.org/content/dam/ifrs/meetings/2025/november/eeg/ap7-frc-bangladesh-presentation.pdf)). The FRC's formal IFRS adoption was still "in process", with legacy BFRS (ICAB) applicable meanwhile. Design for full IFRS, including IFRS 9, 15 and 16 and IAS 12, 16, 36 and 37.
- **Companies Act 1994**:
  - s.183: balance sheet and P&L laid before the AGM, audited.
  - AGM within 15 months of the previous one.
  - ss.210–213: auditor appointment by the AGM; only ICAB chartered accountants.
  - Section details come from secondary sources ([Financial Express](https://thefinancialexpress.com.bd/columns/to-hold-or-not-to-hold-agm-without-audited-financials-1662309584)). RJSC annual return (Schedule X) filing timing: **unverified**.
- **Fiscal year**: July–June aligns with the government and income tax year. The ERP must support a July–June fiscal year, monthly VAT periods and quarterly withholding periods.

### 5. 2024–2026 changes to flag

- **Finance Ordinance 2025** (effective 1 Jul 2025), per [KPMG](https://kpmg.com/us/en/taxnewsflash/news/2025/06/bangladesh-income-tax-vat-proposals-finance-ordinance-2025.html):
  - AIT on manufacturer raw-material imports cut from 3% to 2%.
  - AIT for commercial importers raised from 5% to 7.5%.
  - VAT rate changes on online sales of goods.
  - Rent TDS raised from 5% to 10% (secondary).
- **Jan 2025 VAT ordinance**: VAT and SD rate increases on many items, partly rolled back the same month ([DFDL](https://www.dfdl.com/insights/legal-and-tax-updates/bangladesh-updates-on-amendments-to-the-vat-law/)).
- **NBR split ordinance 2025**: see the institutional note at the top of this section.
- **Finance Act 2026** (FY2026-27, budget presented 11 Jun 2026):
  - Refundable advance tax replaces minimum-tax withholding.
  - Simplified turnover tax for small businesses.
  - VAT on locally made TVs/refrigerators cut from 15% to 7.5% (relevant if the marketplace sells appliances).
  - Online advertising VAT 5%.
  - Startup VAT exemptions.
  - Sources: [Bonik Barta](https://en.bonikbarta.com/bangladesh/OPVCMmIjzrJaYw4n/), [Daily Star](https://www.thedailystar.net/business/bangladesh-budget-2026-27/news/budget-fy27-who-stands-win-and-lose-tax-changes-4195716). **I could not read the PwC "Finance Act 2026 key amendments" PDF (403).** Detailed TDS/VDS changes for FY2026-27 are unverified.
- **E-VAT refund via BEFTN** (Jan 2026).
- **Design implication**: all rates must be effective-dated master data, never hard-coded.

### 6. Could not confirm

- Exact current VAT rate for repair services and parts.
- VDS section number and deposit deadline.
- 6.6 issuance deadline.
- Current official 6.2.1/6.5/6.7/6.8 form titles (from a primary NBR source).
- TDS deposit timing and certificate form.
- Full conditions for the 25% corporate rate.
- NPSB limits and bank file formats.
- RJSC filing dates.
- Whether repair centres are under the EFD mandate.
- Detailed Finance Act 2026 withholding changes.

Get a Bangladeshi VAT consultant or ICAB firm to sign off a rate/form matrix before build.

---

## Industry-Specific Finance Functions (multi-branch repair/service)

| Function | Accounting treatment / design | Module | Source |
|---|---|---|---|
| Warranty provision (own workmanship warranty, e.g. 30–90 days on repairs) | Assurance-type warranty → IAS 37 provision based on historical rework rate × cost; release on expiry. Service-type (sold extended warranty) → IFRS 15 separate PO, deferred revenue. | M19/M53 | IFRS 15.B28–B33 ([IFRS 15](https://www.ifrs.org/issued-standards/list-of-standards/ifrs-15-revenue-from-contracts-with-customers/)) |
| OEM warranty claim receivables | Warranty job closed → claim line to OEM (labour rate per OEM tariff + parts, or parts replaced free from OEM consignment) → claim batch invoice → receivable ageing by OEM → rejection/short-pay write-off; expected rejection estimated as variable consideration. OEM-supplied consignment parts: off-balance-sheet stock register. | M20/M53 | domain + IFRS 15 variable consideration |
| Parts consumption costing / COGS per job | Stock moves from technician van/branch to job → COGS on job completion (perpetual valuation, AVCO or FIFO); returned/defective part (core return) credits; scrap. | M54 + Inventory | Odoo [inventory valuation](https://www.odoo.com/documentation/19.0/applications/finance/accounting/get_started/inventory_valuation.html) |
| Technician van stock | Each van = internal location/warehouse; periodic count and variance write-off charged to cost or recoverable from technician (recovery via payroll deduction → payroll owns the deduction) | Inventory + M54 | domain |
| Technician loaded cost | Loaded hourly rate (see M54) applied to timesheets for job costing; variance to actual payroll cost | M54 | domain |
| Branch cash & imprest | Daily cash book, deposit ≤ next banking day, imprest ceiling, surprise cash counts, shortage recovery | M50 | domain |
| COD reconciliation | Rider/3PL collected → COD receivable per rider → remittance (cash deposit or MFS) → difference queue; courier COD statements with fees | M53/M50 | domain |
| MFS/gateway settlement | bKash/Nagad/SSLCOMMERZ: gross receipts in clearing account, settlement net of MDR (and VAT on MDR), T+n lag, refunds/chargebacks. Daily three-way reconciliation. | M50/M53 | domain |
| Marketplace commission & seller payouts | Agent → recognise commission only; seller payable ledger; deductions (commission, fees, returns, TDS where applicable, VDS on the commission service if relevant); payout batch via BEFTN/MFS; seller statement + tax certificate. Applicable TDS for e-commerce seller payouts (s.89 supply vs platform rule): **unverified**. | M53/M52/M51 | IFRS 15 B34–B38; PwC WHT |
| AMC deferred revenue (IFRS 15) | Upfront/periodic AMC billing → contract liability → ratable recognition (stand-ready); parts included in AMC → cost accrual; onerous contract test (IAS 37) for underpriced AMCs | M53 | IFRS 15 |
| Branch rent leases (IFRS 16) | 51+ leases: ROU + liability; IBR per tenor; rent advance (common in BD) → part of ROU; TDS 10% + VDS 15% on rent payments drive the cash schedule; lease register with renewal options | M49 | [IFRS 16](https://www.ifrs.org/issued-standards/list-of-standards/ifrs-16-leases/) |
| Corporate B2B / government customers | VDS and TDS deducted by customers → reconcile short receipts to 6.6/TDS certificates → tax credits | M20/M51 | PwC |
| Pick-and-drop logistics cost | Rider/courier cost allocated to jobs | M54 | domain |
| ISO 9001 | Not a finance statute, but finance controls (approvals, audit trail, documented procedures) support ISO audits | M19 | — |

---

## Out of Scope for A08 (move elsewhere)

| Commonly built in finance | Belongs in | Finance keeps |
|---|---|---|
| Technician incentives/commissions calculation, salary, PF/gratuity, salary TDS (s.86 / employee tax) | **Payroll/HR** | Payroll journal posting, payroll liability clearing |
| Employee loan schedules / salary advances deduction | Payroll | Advance GL accounts |
| Marketing campaigns, promo/coupon design, loyalty points rules | **CRM/Marketing** | Liability for loyalty points (IFRS 15 material right) and discount accounting only |
| Customer quotations, pricing/price lists, service tariffs | Sales/Service | Revenue posting |
| Purchase requisition, RFQ, supplier evaluation | **Procurement** | 3-way match and bill |
| Inventory operations (van stock transfers, cycle counts, reorder) | **Inventory/Supply chain** | Valuation and COGS |
| Warranty eligibility checks, OEM claim *technical* submission portals, RMA | **Service Ops / Warranty** | Claim receivable and settlement |
| Seller onboarding, KYC, catalog, order management | **Marketplace / Vendor Portal** | Seller ledger, payouts, tax |
| Rider dispatch, COD collection app | **Logistics** | COD receivable reconciliation |
| Dispatch optimisation, SLA tracking, technician scheduling | Field Service / AI | — |
| BI dashboards and data warehouse (Metabase) | **Analytics & BI (area 7)** | Certified finance datasets/KPIs |
| Contract (AMC) entitlement/SLA management | Service contracts / B2B Portal | Billing schedule + deferred revenue |
| Fleet maintenance scheduling | Fleet | Vehicle assets/depreciation |
| Document management/e-signature | Platform | — |
