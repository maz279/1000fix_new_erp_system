---
id: FIX-ERP2-M51
module_id: M51
module_code: TAX
module_name: Tax & Regulatory Compliance (Bangladesh)
category: G — Finance & Treasury
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Financial Officer
system_owner: Finance Squad
priority: P0
wave: W4
---

# M51 — Tax & Regulatory Compliance (Bangladesh)
### Category G · Code `TAX` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M51 |
| **Module code** | `TAX` |
| **Category** | G — Finance & Treasury |
| **Status** | ★ **New** — extracted from the v2.0 M19 monolith after enterprise benchmarking |
| **Priority** | **P0** |
| **Delivery wave** | W4 (Months 14–18) |
| **Business owner** | Chief Financial Officer |
| **System owner** | Finance Squad |
| **Delivery layers** | L1 Odoo `account` (tax objects) · L2 OCA `account-fiscal-rule`, `account-financial-reporting`, `l10n` patterns · L5 custom Bangladesh tax engine, Mushak forms, registers, returns and withholding |
| **Custom modules** | `cd_tax_engine_bd`, `cd_mushak`, `cd_vat_register`, `cd_vat_return`, `cd_tds`, `cd_nid`, `cd_income_tax_schedules` |
| **Requirement range** | FR-TAX-001 … FR-TAX-045 |
| **Requirement count** | **45** *(measured — supersedes the 34 estimate in `02-02`)* |
| **Effort estimate** | **26 person-weeks** *(measured — supersedes the 20 PW estimate)* |
| **Depends on** | M19 GL · M20 Receivables · M52 Payables · M50 Treasury · M33 Party Master · M37 Catalogue · M65 Country Pack · M28 Integration · M29 Identity |
| **Depended on by** | M20, M52, M50, M19, M53, M49, M54, M44, M21, M12, M13, M14, M38, M25, M39, M56, M65 |

---

## 2. Purpose

M51 is the module that keeps 1000FiX **lawfully in business in Bangladesh**.

Everything it does is a condition of operating, not a feature. A sale without a compliant
Mushak 6.3 is an offence. A VAT return that does not reconcile to the registers behind it
invites an audit. A vendor payment made without deducting tax at source makes the Company
liable for the vendor's tax, plus a fifty-percent surcharge. None of these are optimisations.

M51 exists because tax in Bangladesh has two properties that make it unsuitable for embedding in
a ledger. First, it **changes every July** — the Finance Ordinance and its SROs revise rates,
service codes, thresholds and forms annually, and a rate change must never require a code
release. Second, it is **determinative, not descriptive**: the tax treatment of a transaction
must be decided *before* the invoice is issued or the payment is released, and every other module
must be able to ask for that decision without knowing anything about tax law.

So M51 is built as two things: a **determination service** that answers "what is the tax
treatment of this transaction", and a **compliance engine** that maintains the registers, files
the returns, deposits the challans and issues the certificates that the NBR requires.

The target is unambiguous and appears in the category KPI table as an absolute: **zero tax
compliance findings.**

### Why It Exists

1000FiX has fourteen revenue streams, imports parts for seventeen-plus brands, operates a
marketplace with third-party sellers, rents equipment, resells refurbished devices, and pays
several hundred vendors and sub-contractors. Each of those attracts a different VAT treatment, a
different withholding section, or both. The v2.0 draft put all of it inside M19 as
`cd_mushak`, `cd_vat_register` and `cd_tds` — three modules of tax logic living inside the
statutory ledger, guaranteeing that every July's SRO would destabilise the book of record.

There is also a specific, unresolved and expensive question. **The VAT treatment of the
marketplace — principal or agent — is open decision D-03, and it blocks Wave 7.** NBR guidance
indicates that VAT applies to the platform's commission and service charges rather than to the
gross transaction value, but the Company's position must be established with a formal external
tax opinion before the marketplace is built, not after. Getting it wrong means restatement and
penalty across every marketplace transaction ever processed. `_CATEGORY_OVERVIEW.md` §10 rates
this as the **highest commercial risk in the programme**.

M51 is P0. It lands in Wave 4 rather than Wave 3 only because the transaction volume it must
govern does not exist until M20 and M52 are live — but its determination service is required by
both of those in Wave 3, which is the sequencing tension recorded in §18 Q-01.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-FIN-005 | "Automatically calculate and apply Bangladesh VAT on all applicable transactions" |
| ERP BRD BR-FIN-006 | "Generate Bangladesh NBR-compliant tax invoices (Mushak format)" |
| ERP BRD NFR-021 | "Bangladesh VAT (Mushak) invoice format compliance" |
| ERP BRD NFR-022 | "Bangladesh NBR income tax computation compliance" |
| ERP BRD BRU-FIN-01 | Every invoice carries VAT at the applicable rate and the Company's registration number |
| ERP BRD BRU-FIN-02 | Cash receipts above BDT 50,000 require the customer's NID per NBR guidelines |
| ERP BRD Automation A11 | "VAT return auto-compiled from invoice and payment data" replaces manual VAT calculation |
| ERP BRD §Data Retention | Financial transactions retained 7 years — Bangladesh Companies Act / NBR |
| ERP BRD STK-19 | Bangladesh NBR is a stakeholder: VAT compliance and tax filing |
| Business Objective BO-10 | "Ensure full Bangladesh regulatory compliance (VAT, tax, labor law) with zero manual intervention" — baseline manual and error-prone, target **zero non-compliance incidents**, owner CFO |
| `05-05` BRU-FIN-08 | "Marketplace transactions are accounted per the declared principal-or-agent model; the model cannot vary by transaction" |
| `05-05` BRU-FIN-09 | "TDS is deducted at the correct rate on every applicable vendor payment; the payment cannot proceed otherwise" |
| `_CATEGORY_OVERVIEW.md` §6 | The complete table of Bangladesh statutory obligations: Mushak 6.3, registers 6.1/6.2/6.2.1/6.5/6.6, Mushak 9.1 monthly, input VAT credit, TDS/VDS, challans and certificates, income-tax schedules, July–June fiscal year, high-value cash NID, import duty and VAT |
| `_CATEGORY_OVERVIEW.md` §8 | VAT returns filed on time with zero adjustment: 100% · **Tax compliance findings: Zero** |
| `_CATEGORY_OVERVIEW.md` §10 | Decision **D-03** — marketplace VAT treatment — critical risk; external tax opinion required before Wave 7 build |
| VAT & SD Act 2012 / VAT & SD Rules 2016 | Rule 40(1) prescribes the Mushak 6.3 tax invoice; Mushak 9.1 is the monthly return, due by the 15th |
| Income Tax Act 2023 | Withholding sections, Third Schedule depreciation, corporate rates, July–June income year |
| Finance Ordinance 2025 / SRO 182-Ain/2025/310-Mushak / VDS Rules 2025 | FY 2025–26 TDS and VDS rates; VDS mandatory for 45 specified services; Mushak 6.6 within 3 working days of return filing |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M51 owns *tax as a discipline*. Every other module owns
> the transaction that tax applies to. Both sides of every boundary agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | **The tax determination service**: given a transaction context, return the applicable treatment, rate, code and statutory basis |
| 2 | The Bangladesh country tax pack: rates, thresholds, service codes, sections, forms and effective dates as configuration |
| 3 | VAT registration data: BIN, VAT circle, commissionerate, registered premises |
| 4 | Output VAT determination on every taxable supply across all 14 revenue streams |
| 5 | Input VAT determination and credit eligibility on every purchase and import |
| 6 | Supplementary Duty (SD) where applicable |
| 7 | **Mushak 6.3** tax invoice: prescribed format, mandatory elements, sequence and issuance rules |
| 8 | **Mushak registers**: 6.1 purchase, 6.2 sales, 6.2.1, 6.5 stock transfer, 6.6 VDS certificate, 6.7/6.8 credit and debit notes |
| 9 | **Mushak 9.1** monthly VAT return: compilation, reconciliation, review, filing and payment |
| 10 | Input VAT credit tracking, offset, carry-forward and refund application |
| 11 | Decreasing and increasing adjustments, including VDS credit claims |
| 12 | **VAT Deduction at Source (VDS)**: identification of the 45 specified services, rate application, deposit, and Mushak 6.6 certificate issuance |
| 13 | **Tax Deducted at Source (TDS)**: section determination, rate application by payee type, PSR and bank-transfer surcharge conditions |
| 14 | Challan generation and deposit tracking (A-Challan / Treasury Challan) with bank confirmation |
| 15 | Withholding certificate issuance to vendors and the withholding return |
| 16 | High-value cash transaction NID capture rule, threshold and evidence |
| 17 | Corporate income tax: taxable income computation schedules, tax depreciation under the Third Schedule, disallowances, advance tax |
| 18 | Import duty and VAT at import, its accounting into landed cost, and the input credit that follows |
| 19 | **The marketplace principal-vs-agent VAT model** (decision D-03) and its consistent application |
| 20 | Tax positions, exemptions, reduced rates and their evidence |
| 21 | Statutory calendar: every filing, deposit and certificate obligation with its deadline and owner |
| 22 | Tax audit support: reconciliations, extracts, evidence packs and query response |
| 23 | Tax provision and deferred tax computation raised to M19 |
| 24 | Change management for annual statutory revisions, with effective-dated versioning |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Journal posting of tax liabilities, credits, provisions and deferred tax | **M19** General Ledger | Only Category G's ledger creates journal entries; M51 determines and computes |
| Invoice creation, numbering, delivery and presentation | **M20** Receivables | M51 supplies the Mushak format, sequence rules and determination; M20 renders and issues |
| Receipt capture, including the NID field itself | **M20** Receivables (counter: **M04**) | M51 owns the rule and the threshold; M20 captures and stores |
| Vendor invoice, approval and payment authorisation | **M52** Payables | M52 applies the deduction M51 determines |
| Bank transfer of a challan deposit | **M50** Treasury & Cash | M51 instructs; M50 executes and confirms |
| Price determination and whether a price is VAT-inclusive | **M11** Pricing (Category C) | Pricing is commercial; M51 determines the tax on whatever price is set |
| Product and service classification for catalogue purposes | **M37** Catalogue | M37 holds the classification; M51 maps it to a tax code |
| Import documentation, bill of entry, customs clearance, landed-cost allocation | **M44** Import & Landed Cost | M44 owns the shipment; M51 owns the duty and VAT treatment and the credit |
| Payroll income tax on salaries, and employee tax certificates | **M21** HR & Payroll | Employee withholding is a payroll lifecycle |
| Labour law, provident fund and gratuity compliance | **M21** HR & Payroll | Different statute, different owner |
| Fixed asset register and book depreciation | **M49** Fixed Assets | M49 owns the register and book depreciation; M51 computes tax depreciation from it |
| Revenue recognition timing under IFRS/BFRS | **M53** Revenue & Settlement | Accounting revenue and taxable supply are different concepts with different timing |
| Environmental and e-waste regulatory compliance | **M18** E-Waste & Circular Economy | Different regulator |
| Data protection and Digital Security Act compliance | **M29** Identity / **M30** Platform | Different statute |
| ISO 9001 and quality compliance | **M23** Quality Management | Different framework |
| Country pack framework and multi-country abstraction | **M65** Country & Localisation Pack | M65 owns the framework; M51 is the Bangladesh content within it |

### 3.3 Shared Concepts

| Concept | M51's Role | Owning Module |
|---|---|---|
| Tax determination | **Owns** — the defining service of this module | M51 |
| Tax code and rate | **Owns** | M51 |
| Mushak 6.3 | Owns the format, sequence rules and register; M20 renders and issues | M51 / M20 |
| VAT register | **Owns** | M51 |
| VAT return | **Owns** | M51 |
| Input VAT credit | **Owns** the eligibility and the balance; M19 holds the account | M51 / M19 |
| TDS / VDS | **Owns** determination, deposit and certificate; M52 applies at payment | M51 / M52 |
| Challan | **Owns** the obligation and the record; M50 executes the deposit | M51 / M50 |
| Customer / vendor BIN and TIN | Validates and uses; M33 holds the master | M51 / M33 |
| NID on high-value cash | **Owns** the rule and threshold; M20/M04 capture | M51 / M20 / M04 |
| Tax depreciation | **Owns** the computation; M49 owns the asset and book depreciation | M51 / M49 |
| Import duty and VAT | Owns the tax treatment and credit; M44 owns the shipment and landed cost | M51 / M44 |
| Marketplace principal/agent model | **Owns** the declared model (D-03); M12 and M53 implement its commercial consequence | M51 / M12 / M53 |
| Country pack | Provides the Bangladesh content; M65 owns the framework | M51 / M65 |
| Statutory calendar | **Owns** for tax obligations; M23 owns the wider compliance calendar | M51 / M23 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — Tax (FI-TX) & Advanced Compliance Reporting (ACR)** | Tax codes and jurisdiction determination per transaction; country-specific statutory report definitions delivered as content and updated with legal change packages; e-document framework for country-mandated invoice formats | **The separation of the tax engine from the statutory report content, with the report content shipped and versioned independently.** This is precisely what an annual Finance Ordinance demands. Also adopted: the e-document concept for the Mushak 6.3, treated as a statutory document object with its own sequence and lifecycle, not a print layout of an invoice | ACR's global report catalogue and SAP's tax-service subscription model; Bangladesh content does not exist and must be built regardless |
| **Oracle Fusion Cloud — Tax (Oracle Tax)** | A rules-based determination engine with tax regimes, statuses, rates, jurisdictions and rules evaluated in a defined order; tax reporting ledger separate from the GL | **The determination-service architecture**: other modules ask, the engine answers, and the answer carries its rule and basis. And **the tax reporting ledger as a separate store** — the VAT registers are not a view over the GL, they are a maintained record with their own integrity, which is what makes return-to-register-to-ledger reconciliation possible | Oracle's multi-jurisdiction/regime hierarchy depth; one country, one regime |
| **Microsoft Dynamics 365 Finance — Tax, Electronic Reporting (ER)** | Tax calculation service; Electronic Reporting configurations that define statutory formats as data, editable without code | **Electronic Reporting's core idea — a statutory format is data, not code.** Every Mushak form and the 9.1 return are defined as versioned format configurations. When NBR revises a form, the change is a configuration release with a test fixture, not a development cycle | The full ER designer surface; we ship a constrained form-definition model |
| **Avalara / Vertex / regional tax-engine practice** | Centralised determination called by every transactional system; content updated by the vendor; audit-ready transaction-level record with the rule that produced it | **Every determination is stored with its inputs, rule version and statutory basis.** Three years later, in an NBR audit, the question is not "what rate did you charge" but "why", and the answer must be retrievable per transaction | Third-party engine subscription — no vendor provides Bangladesh VAT and NBR withholding content at usable depth |
| **Indian GST-era ERP localisations (a close structural analogue)** | Statutory invoice numbering with continuity, purchase and sales registers reconciled to the return, input credit matching against supplier filings, TDS/TCS at source with certificates | **Register-first design**: the return is compiled *from* the registers, and the registers are reconciled *to* the ledger, in that order. Implementations that compile a return directly from GL balances fail at the first audit because they cannot produce the transaction-level register behind the number | Supplier-filing matching (GSTR-2A equivalent) — no NBR facility exists today, though our design does not preclude it |
| **NBR VAT & SD Act 2012 / Rules 2016 practice** | Mushak 6.3 at time of supply under Rule 40(1) with mandatory elements; registers 6.1, 6.2, 6.2.1, 6.5, 6.6; monthly Mushak 9.1 by the 15th; input credit only against valid Mushak 6.3 from an active BIN; 5-year Mushak retention | Implemented directly as the module's statutory core, with the Companies Act 7-year retention taking precedence where it is longer | — |
| **Income Tax Act 2023 and the FY 2025–26 withholding regime** | s.89 contractor/supplier rates; s.90 service rates split by individual (15%) and non-individual (7.5%) payee; s.109/110 rent at 10%; s.114 electricity at 4%; s.116 foreign buyer agent commission at 7.5%; deposit deadlines by month with a compressed June schedule; s.142 50% surcharge where the payee has no PSR or payment is not by bank transfer | **Payee type, PSR status and payment method as determination inputs, not afterthoughts.** The same service to the same vendor attracts a different rate depending on whether the vendor is an individual and whether they can produce a PSR. A determination engine that takes only "service type" is wrong on a large share of our payments | — |
| **Odoo 19 CE `account` taxes + OCA `account-fiscal-rule`** | Tax objects, tax groups, fiscal positions mapping taxes by partner and country | The transactional substrate for carrying a tax code on a line. Fiscal positions handle the simple cases (exempt customer, zero-rated export) | Odoo's tax computation as the determination authority — it cannot express payee-type, PSR-conditional or service-code-driven rules |

**Design position.** Six deliberate positions.

First, **tax is a country pack, not code**. Every rate, threshold, service code, section, form
layout and deadline is effective-dated configuration under M65's framework. The July Finance
Ordinance is a content release with a test fixture and a CFO approval, not a sprint. This is
the single most important design decision in the module, and `_CATEGORY_OVERVIEW.md` §10 names
it as the mitigation for mid-programme statutory change.

Second, **determination is a service, and it is authoritative**. M20 does not compute VAT; M52
does not compute TDS. They ask, and they store the reference to the answer. The corollary is
that the determination service must be available, fast, and versioned — and that when it is
unavailable, the dependent operation **fails closed** rather than guessing.

Third, **registers are records, not views**. The Mushak registers are maintained, immutable
after period close, and reconciled to the ledger — not generated on demand from GL balances. The
return compiles from the registers. This ordering is what makes "filed on time with zero
adjustment" achievable.

Fourth, **withholding is a gate**. Under BRU-FIN-09 a payment cannot proceed without a
determination. There is no fail-open path, because failing open transfers a vendor's tax
liability onto 1000FiX with a fifty-percent surcharge attached.

Fifth, **every determination is explainable per transaction, for seven years**. Inputs, rule
version, rate, statutory basis and outcome are stored on the transaction. An NBR audit is
answered by query, not by reconstruction.

Sixth, **the marketplace VAT model is declared once and applied without exception**. BRU-FIN-08
forbids per-transaction variation. Until decision D-03 is settled by external opinion, the
marketplace configuration is *absent*, not defaulted — a defaulted position that turns out to be
wrong is worse than no position at all, because it produces filed returns that must be restated.

---

## 5. Functional Areas & Features

### 5.1 Tax Determination Service & Country Pack

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TAX-001 | Determination service | Given a transaction context — supply type, item classification, customer or vendor type and registration, place, date, revenue stream and value — return the applicable tax treatment, rate, code, statutory basis and rule version (BR-FIN-005) | **P0** | L5 |
| FR-TAX-002 | Determination record | Store every determination with its inputs, rule version, outcome and statutory reference, linked to the transaction, retrievable for seven years | **P0** | L5 |
| FR-TAX-003 | Country tax pack | Hold all rates, thresholds, service codes, withholding sections, exemptions, form layouts and deadlines as effective-dated configuration under the M65 framework, with no tax value hard-coded anywhere | **P0** | L5 |
| FR-TAX-004 | Rule authoring and versioning | Author, test against fixtures, approve, version and activate a tax rule with an effective date, without a code release | **P0** | L5 |
| FR-TAX-005 | Annual revision workflow | Support the July statutory revision as a controlled release: new versions prepared in advance, tested, approved by the CFO, and activated on the effective date with the prior version retained | **P0** | L5 |
| FR-TAX-006 | Registration data | Hold BIN, TIN, VAT circle, commissionerate and registered premises per legal entity, and display them where statute requires | **P0** | L5 |
| FR-TAX-007 | Counterparty tax status | Validate and hold customer and vendor BIN, TIN, registration status, payee type (individual or non-individual) and PSR status, and use them as determination inputs | **P0** | L5 |
| FR-TAX-008 | Fail-closed behaviour | Refuse to return a default or assumed treatment when determination cannot be completed, and cause the calling operation to halt rather than proceed | **P0** | L5 |

### 5.2 Output VAT, Mushak 6.3 & Supply-Side Compliance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TAX-009 | Output VAT determination | Determine output VAT on every taxable supply across all 14 revenue streams, including standard, reduced, zero-rated and exempt treatments | **P0** | L5 |
| FR-TAX-010 | Mushak 6.3 format | Define the statutory tax invoice format per Rule 40(1) with all mandatory elements — supplier name and BIN, buyer name and BIN, issue date, description, taxable value, VAT amount and total — in Bengali and English (BR-FIN-006, NFR-021) | **P0** | L5 |
| FR-TAX-011 | Mushak 6.3 sequence control | Maintain the statutory document sequence per entity and premises, gapless and non-reusable, and record every issued, cancelled and unused number | **P0** | L5 |
| FR-TAX-012 | Issuance timing rule | Enforce that a Mushak 6.3 is issued at the time of supply, and report any supply where issuance is late | **P0** | L5 |
| FR-TAX-013 | Supplementary Duty | Determine and apply SD where applicable to a supply, and report it separately in the return | P2 | L5 |
| FR-TAX-014 | Credit and debit notes | Define the statutory credit note (Mushak 6.7) and debit note (Mushak 6.8) treatments and their register and return effects | **P0** | L5 |
| FR-TAX-015 | Exemptions and reduced rates | Hold exemption and reduced-rate positions with their SRO basis and validity, and apply them only where evidenced | **P0** | L5 |
| FR-TAX-016 | Zero-rated and export supply | Determine zero-rated treatment for qualifying supplies and hold the evidence the treatment requires | P2 | L5 |

### 5.3 Input VAT, Registers & the Mushak 9.1 Return

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TAX-017 | Input VAT determination | Determine input VAT on every purchase and import, and assess credit eligibility — valid Mushak 6.3, active supplier BIN, permitted purpose | **P0** | L5 |
| FR-TAX-018 | Input credit ledger | Maintain the input VAT credit balance with claims, offsets, carry-forward, disallowances and refund applications | **P0** | L5 |
| FR-TAX-019 | Mushak 6.1 purchase register | Maintain the statutory purchase register from every purchase, import and expense with input VAT | **P0** | L5 |
| FR-TAX-020 | Mushak 6.2 / 6.2.1 sales registers | Maintain the statutory sales registers from every taxable supply | **P0** | L5 |
| FR-TAX-021 | Mushak 6.5 stock transfer register | Maintain the register of stock transfers between registered premises | P1 | L5 |
| FR-TAX-022 | Mushak 6.6 VDS certificate register | Maintain the register of VAT deducted or collected at source, both issued and received | **P0** | L5 |
| FR-TAX-023 | Register immutability | Lock every register at period close so that a filed period cannot be silently altered; corrections are made by an adjustment that is separately visible | **P0** | L5 |
| FR-TAX-024 | Register-to-ledger reconciliation | Reconcile every register to its GL control account before the return is compiled, and report any difference | **P0** | L5 |
| FR-TAX-025 | Mushak 9.1 compilation | Compile the monthly VAT return from the registers — output by rate, input with credit, VAT calculation, SD and declaration — with every figure traceable to its transactions (Automation A11) | **P0** | L5 |
| FR-TAX-026 | Return review and approval | Present the compiled return with variance against prior periods, require review and CFO approval before filing, and retain the approved version | **P0** | L5 |
| FR-TAX-027 | Return filing and payment | Support filing by the 15th of the following month through the NBR online facility, record the acknowledgement, and instruct M50 to pay the net VAT by the same date | **P0** | L5 |
| FR-TAX-028 | Adjustments | Support decreasing adjustments (including VDS credit claims under Mushak 6.6) and increasing adjustments, each with a reason and evidence | **P0** | L5 |
| FR-TAX-029 | Refund application | Prepare and track a refund application where the credit balance qualifies | P2 | L5 |

### 5.4 Withholding — TDS & VDS

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TAX-030 | VDS applicability | Identify whether a purchase falls within the specified services requiring VAT deduction at source, by service code, and determine the rate for the period | **P0** | L5 |
| FR-TAX-031 | VDS exemptions | Apply the exemption set — manufacturer supply with a valid Mushak 6.3, utilities, exempt and zero-rated supplies, EFD/SDC invoices with purchaser name and BIN — rather than deducting by default | **P0** | L5 |
| FR-TAX-032 | TDS section determination | Determine the withholding section and rate for every payment by nature of payment, payee type (individual or non-individual) and payee status | **P0** | L5 |
| FR-TAX-033 | Surcharge conditions | Apply the elevated rate automatically where the payee cannot produce a valid PSR or where payment is not made by bank transfer, and record which condition applied | **P0** | L5 |
| FR-TAX-034 | Deduction gate | Prevent M52 from releasing any applicable payment without a completed determination, with no fail-open path (BRU-FIN-09) | **P0** | L5 |
| FR-TAX-035 | Challan generation and deposit | Generate the deposit obligation per section and period, instruct M50 to deposit by the statutory deadline, and record the challan reference and bank confirmation | **P0** | L5 |
| FR-TAX-036 | Deposit deadline calendar | Apply the statutory deposit schedule including the compressed June deadlines, and alert before each deadline with the amount and the owner named | **P0** | L5 |
| FR-TAX-037 | Certificate issuance | Issue the withholding certificate to each payee — Mushak 6.6 for VDS within the statutory window, and the income-tax withholding certificate for TDS — and make it available in P05 | **P0** | L5 |
| FR-TAX-038 | Withholding returns | Compile the periodic withholding statements required by the NBR from the deduction records | P1 | L5 |
| FR-TAX-039 | VDS received | Record VDS deducted from 1000FiX by its own customers, hold the Mushak 6.6 received, and claim the decreasing adjustment in the return | **P0** | L5 |

### 5.5 Income Tax, Import Tax & Special Regimes

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TAX-040 | Tax depreciation | Compute tax depreciation from M49's asset register under the Third Schedule — normal rates on written-down value, initial allowance on purchase cost — maintaining a tax book separate from the accounting book | P1 | L5 |
| FR-TAX-041 | Taxable income schedules | Prepare the corporate income-tax computation schedules from the ledger — accounting profit, disallowances, allowances, depreciation reconciliation and taxable income — for the July–June income year (NFR-022) | P1 | L5 |
| FR-TAX-042 | Advance tax and provision | Track advance income tax paid, compute the current and deferred tax provision, and raise both to M19 | P1 | L5 |
| FR-TAX-043 | Import duty and VAT | Determine the duty, VAT and advance tax at import from M44's bill of entry, confirm their accounting into landed cost, and register the import VAT credit | **P0** | L5 |
| FR-TAX-044 | High-value cash NID rule | Own the statutory threshold and the rule requiring the customer's NID on cash receipts above it, expose it to M20 and M04, and report every occurrence and every exception (BRU-FIN-02) | **P0** | L5 |
| FR-TAX-045 | Marketplace principal/agent model | Hold the declared principal-or-agent VAT model for marketplace transactions as a single configured position that cannot vary by transaction, and apply it consistently to determination, registers and returns (BRU-FIN-08, decision **D-03**) | **P0** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Determination as a versioned, side-effect-free service** | The determination call is idempotent and pure: the same inputs and the same effective date always return the same result. It writes a determination record but changes no transactional state. This is what makes a three-year-old determination reproducible |
| T-02 | **No tax value in code** | Rates, thresholds, service codes, sections and deadlines exist only as country-pack data. A static-analysis check in CI fails the build on any numeric tax literal in application code |
| T-03 | **Effective-dated rule evaluation** | Every rule carries `effective_from` and `effective_to`. Determination uses the transaction's tax point date, never the system date, so a backdated transaction is determined under the law that applied to it |
| T-04 | **Fail closed** | On determination failure, service unavailability or an unmapped context, the service returns an explicit error. Calling modules must halt. No default rate, no zero, no last-known value. Enforced by contract test in M20, M52 and M50 |
| T-05 | **Determination performance** | p95 ≤ 150 ms per determination; the service sits in the synchronous invoice-issuance and payment-release paths and must not become the constraint on the 1-hour invoicing target |
| T-06 | **Statutory sequence integrity** | Mushak 6.3 sequences are gapless per entity and premises under concurrency and rollback; a rolled-back issuance records a cancelled number rather than leaving a gap. Sequence state is never reset, re-based or edited |
| T-07 | **Register append-and-lock** | Register lines are insert-only within an open period and immutable after period lock. A correction is an adjustment line referencing the original, never an edit |
| T-08 | **Form definitions as data** | Every Mushak form and the 9.1 return are versioned format definitions with field mappings and validation rules, rendered by a generic engine. An NBR format revision is a configuration release with a fixture |
| T-09 | **Bengali statutory rendering** | Statutory documents render in Bengali with Bengali numerals where the prescribed format requires them, and the rendering is validated against the prescribed layout, not merely translated (AS-12) |
| T-10 | **Three-way reconciliation** | Return ↔ register ↔ ledger reconciliation is executed and stored as evidence for every filed period. A return cannot be marked filed without it |
| T-11 | **Retention** | Mushak documents, registers, returns, challans, certificates and determination records retained **seven years** (Companies Act, which exceeds the 5-year VAT requirement) and remain queryable throughout |
| T-12 | **Volume envelope** | ~400,000–500,000 output determinations/year (one per invoice line group), ~20,000 input determinations/year, ~15,000 withholding determinations/year, ~12 VAT returns and ~150 challans/year per entity |
| T-13 | **Event emission via outbox** | Every tax state change emits a domain event through the transactional outbox (AS-08); M19 consumes for posting, M20/M52 for confirmation |
| T-14 | **Multi-entity scoping** | Registration, registers, returns and challans are per legal entity; a determination is always entity-scoped and no register line can cross entities (AS-03) |
| T-15 | **Country-pack portability** | The Bangladesh pack is one implementation of M65's country-pack contract. A second country is a new pack against the same engine, supporting BO-18's ≤ 12-week target |
| T-16 | **NID handling** | Customer NID captured under the high-value cash rule is field-level encrypted, masked, access-logged, and used only for the statutory purpose (AS-14) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M51 |
|---|---|---|
| **CFO** | Signs a VAT return compiled by hand from spreadsheets, and carries the personal exposure that comes with it | Approves a return compiled from locked registers, reconciled to the ledger, with every figure traceable |
| **Finance officer (VAT)** | Spends the first week of every month building the return | Reviews a compiled return and works the variances |
| **Finance officer (payables)** | Looks up a withholding rate in a circular, or asks a colleague | Never touches a rate; the determination is applied and evidenced automatically |
| **Tax consultant** | Reconstructs registers from invoices at year end | Receives complete, locked registers and reconciliations; advises rather than compiles |
| **Counter cashier** | May or may not remember the NID rule on a large cash payment | Cannot complete the receipt without it |
| **Vendor** | Chases a withholding certificate by phone | Downloads it from P05 within the statutory window |
| **Branch staff** | Issue an invoice that may not be Mushak-compliant | Cannot issue a non-compliant document; the format is the only format |
| **NBR auditor** | Requests schedules that take weeks to prepare | Receives a period evidence pack with transaction-level traceability |
| **CEO / board** | Carries an unquantified compliance exposure | Sees a compliance dashboard with deadlines, filings and findings |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Penalty and interest avoidance — VAT** | Returns filed by the 15th, compiled from reconciled registers | Avoids the BDT 5,000+ per-return late penalty and 2% monthly interest, and the BIN suspension risk of consecutive missed returns |
| **Withholding liability avoidance** | Deduction as a hard gate on every applicable payment, with correct payee-type and PSR conditions | Avoids becoming liable for vendors' tax plus the **s.142 50% surcharge** — the single largest quantifiable statutory exposure in the business |
| **Input VAT credit recovery** | Every eligible input credit identified, evidenced and claimed rather than lost through missing documentation | On a business importing parts for 17+ brands, unclaimed input credit is a recurring, invisible cost |
| **Audit cost and disruption reduction** | Evidence packs generated rather than reconstructed | Shortens NBR fieldwork and removes the diversion of the finance team for weeks |
| **Administrative labour released** | Manual VAT compilation, rate lookup and certificate preparation eliminated | A material share of the **BDT 62 lac** cross-module administrative saving |
| **Marketplace risk containment** | A single declared VAT model, applied without exception, evidenced by external opinion | Avoids the restatement-and-penalty scenario rated as the **highest commercial risk in the programme** |
| **Statutory change absorption** | Annual Finance Ordinance handled as a configuration release | Removes the annual re-development cost and the compliance gap between enactment and implementation |
| **Close acceleration** | Tax positions determined continuously, registers reconciled before close | Direct contributor to the ≤ 3-day close (KPI-050) |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Licence to operate** | Every item in this module is a condition of trading in Bangladesh. There is no version of the business that does not need it |
| **Zero tax compliance findings** | The stated target in `_CATEGORY_OVERVIEW.md` §8 is an absolute, not a percentage. It is achievable only where determination is systematic and evidence is automatic |
| **Personal exposure reduction for officers** | Tax non-compliance in Bangladesh carries personal consequences for company officers. A system that makes the correct treatment the only available treatment is a governance protection, not merely a finance tool |
| **Credibility with the regulator** | An organisation that answers an NBR query with a transaction-level extract in a day is treated differently from one that asks for an extension |
| **Brand partner and corporate client assurance** | Corporate and government clients require compliant tax invoices; failure to supply one blocks their own input credit and ends the relationship |
| **ISO 9001 and governance conformance** | Documented, controlled statutory processes with evidence retention |
| **Second-country readiness** | The Bangladesh pack proves the country-pack contract. A second country becomes content, not architecture (BO-18) |
| **Institutional knowledge capture** | Tax treatment stops living in one consultant's head and becomes versioned, tested, approved configuration |

---

## 8. Lifecycle & State Models

### 8.1 The VAT Period Cycle

```
   PERIOD OPEN
       │  every supply and purchase determined at its tax point
       ▼
  ┌──────────────────────────────────────────────────────┐
  │  REGISTERS ACCUMULATING                              │
  │  6.1 purchase · 6.2 / 6.2.1 sales · 6.5 transfers    │
  │  6.6 VDS · 6.7 / 6.8 credit and debit notes          │
  └───────────────────────┬──────────────────────────────┘
                          │ period end
                          ▼
  ┌──────────────────────────────────────────────────────┐
  │  REGISTER-TO-LEDGER RECONCILIATION                    │
  └──────┬───────────────────────────────────┬───────────┘
         │ reconciled                        │ difference
         ▼                                   ▼
  ┌──────────────┐                    ┌──────────────────┐
  │ REGISTERS    │                    │ RECONCILIATION   │
  │ LOCKED       │                    │ EXCEPTION        │──► blocks compilation
  └──────┬───────┘                    └──────────────────┘
         │ compile
         ▼
  ┌──────────────┐   variance review   ┌──────────────────┐
  │ RETURN       │────────────────────►│ RETURN AMENDED   │
  │ COMPILED     │                     │ (pre-filing)     │
  └──────┬───────┘                     └────────┬─────────┘
         │◄─────────────────────────────────────┘
         │ CFO approval
         ▼
  ┌──────────────┐   filed by the 15th, net VAT paid same date
  │  APPROVED    │───────────────────────────────────────┐
  └──────────────┘                                       ▼
                                                  ┌──────────────┐
                                                  │    FILED     │
                                                  └──────┬───────┘
                                                         │ NBR query / self-identified error
                                                         ▼
                                                  ┌──────────────┐
                                                  │   AMENDED    │ (separately evidenced)
                                                  └──────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Registers accumulating | Period opens; determinations write register lines at each tax point | System |
| Registers accumulating | Reconciliation | Period end reached | System |
| Reconciliation | Registers locked | Every register agrees with its GL control account | Finance Officer / Finance Manager |
| Reconciliation | Reconciliation exception | Any unexplained difference — **blocks return compilation** | System |
| Registers locked | Return compiled | Compilation run from locked registers | System |
| Return compiled | Approved | Reviewed with prior-period variance analysis; approved by the CFO | CFO |
| Approved | Filed | Filed through the NBR facility by the 15th; acknowledgement recorded; net VAT paid | Finance Manager |
| Filed | Amended | An error is identified or an NBR query requires it; amendment separately evidenced and reported | CFO |

### 8.2 Withholding Lifecycle

```
  PAYMENT PROPOSED IN M52
        │
        ▼
  ┌──────────────────┐  no determination possible  ┌──────────────────┐
  │  DETERMINATION   │────────────────────────────►│  PAYMENT BLOCKED │
  │  REQUESTED       │                             │  (fail closed)   │
  └────────┬─────────┘                             └──────────────────┘
           │ section, rate, payee type, PSR, method
           ▼
  ┌──────────────────┐
  │   DETERMINED     │  ── elevated rate applied where no PSR
  └────────┬─────────┘     or payment not by bank transfer (s.142)
           │ payment released by M52, executed by M50
           ▼
  ┌──────────────────┐
  │   DEDUCTED       │  liability to NBR recognised
  └────────┬─────────┘
           │ deposit obligation created, deadline calendared
           ▼
  ┌──────────────────┐  deadline approaching  ┌──────────────────┐
  │  DEPOSIT DUE     │───────────────────────►│  DEADLINE ALERT  │
  └────────┬─────────┘                        └──────────────────┘
           │ M50 deposits; challan reference recorded
           ▼
  ┌──────────────────┐
  │   DEPOSITED      │
  └────────┬─────────┘
           │ within the statutory window
           ▼
  ┌──────────────────┐
  │ CERTIFICATE      │  Mushak 6.6 (VDS) · TDS certificate
  │ ISSUED           │  published to the payee in P05
  └──────────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Determination requested | M52 proposes a payment on an applicable category | M52 |
| Determination requested | Payment blocked | Determination cannot complete for any reason | System — **fail closed** |
| Determination requested | Determined | Section, rate, payee type, PSR status and payment method all resolved | System |
| Determined | Deducted | M52 releases and M50 executes the net payment | M52 / M50 |
| Deducted | Deposit due | Deposit obligation created with the statutory deadline | System |
| Deposit due | Deposited | M50 confirms the treasury deposit and the challan reference is recorded | M50 / Finance Officer |
| Deposited | Certificate issued | Certificate generated within the statutory window and published to the payee | System |

### 8.3 Country Pack Version Lifecycle

| State | Meaning | Exit Condition |
|---|---|---|
| Drafted | New rates, codes or forms entered ahead of the Finance Ordinance effective date | Fixtures attached |
| Tested | Executed against the regression fixture set and against sample real transactions | All fixtures pass |
| Reviewed | Checked by the external tax consultant against the enacted statute | Consultant sign-off recorded |
| Approved | Approved by the CFO with the effective date set | Effective date reached |
| Active | In use for transactions whose tax point falls in its validity window | Superseded |
| Superseded | Replaced by a later version | **Retained permanently** — prior determinations reference it |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-TAX-01 | No tax rate, threshold, service code or deadline exists in application code; all are country-pack configuration | **H** | CTO |
| BRU-TAX-02 | Determination uses the transaction's tax point date, never the system date | **H** | CFO |
| BRU-TAX-03 | Determination fails closed: on any failure the calling operation halts, and no default, zero or last-known treatment is applied | **H** | CFO |
| BRU-TAX-04 | Every taxable supply produces a Mushak 6.3 at the time of supply, displaying the Company's BIN (BRU-FIN-01) | **H** | CFO |
| BRU-TAX-05 | Mushak 6.3 sequences are gapless per entity and premises; a number is never reused, re-based or edited | **H** | CFO |
| BRU-TAX-06 | Input VAT credit is claimed only against a valid Mushak 6.3 from an active supplier BIN | **H** | CFO |
| BRU-TAX-07 | TDS/VDS is deducted at the determined rate on every applicable payment; the payment cannot proceed otherwise (BRU-FIN-09) | **H** | CFO |
| BRU-TAX-08 | Where the payee cannot produce a valid PSR, or payment is not made by bank transfer, the elevated rate applies automatically and the condition is recorded | **C** | CFO |
| BRU-TAX-09 | A deduction is deposited by its statutory deadline; an approaching deadline escalates to the CFO | **H** | CFO |
| BRU-TAX-10 | A withholding certificate is issued to the payee within the statutory window of the triggering event | **H** | Finance Manager |
| BRU-TAX-11 | Registers are locked at period close; corrections are adjustment lines referencing the original, never edits | **H** | CFO |
| BRU-TAX-12 | A return cannot be compiled until every register reconciles to its GL control account | **H** | CFO |
| BRU-TAX-13 | A return cannot be filed without CFO approval of the compiled version | **H** | CFO |
| BRU-TAX-14 | The VAT return is filed and the net VAT paid by the 15th of the following month | **H** | CFO |
| BRU-TAX-15 | A filed return is never altered; a correction is a separately evidenced amendment | **H** | CFO |
| BRU-TAX-16 | Marketplace transactions are accounted per the single declared principal-or-agent model; the model cannot vary by transaction (BRU-FIN-08) | **H** | CFO |
| BRU-TAX-17 | **The marketplace model is not configured until decision D-03 is settled by external tax opinion**; until then, marketplace determination is refused rather than defaulted | **H** | CFO |
| BRU-TAX-18 | A cash receipt above the statutory threshold cannot be completed without the customer's NID (BRU-FIN-02) | **H** | CFO |
| BRU-TAX-19 | Customer NID captured for the cash rule is used only for that statutory purpose, is encrypted, and every access is logged | **H** | CTO |
| BRU-TAX-20 | Tax depreciation is computed on a tax book separate from the accounting book; the two are never merged | **H** | CFO |
| BRU-TAX-21 | The income year is July to June, matching the fiscal year (BRU-FIN-19) | **H** | CFO |
| BRU-TAX-22 | A country-pack version is activated only after fixtures pass, the external consultant signs off, and the CFO approves | **H** | CFO |
| BRU-TAX-23 | A country-pack version is never edited in place; every determination references the version that produced it | **H** | CTO |
| BRU-TAX-24 | Tax documents, registers, returns, challans, certificates and determination records are retained seven years and remain queryable | **H** | CFO |
| BRU-TAX-25 | An exemption or reduced rate is applied only where its SRO basis and evidence are recorded and valid at the tax point | **H** | CFO |
| BRU-TAX-26 | VDS is not deducted where a statutory exemption applies; deducting by default is as much an error as failing to deduct | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.tax.registration` | `fix_tax_registration` | Entity registration data | entity_id, bin, tin, vat_circle, commissionerate, registered_premises_json, effective_from, effective_to |
| `fix.tax.pack.version` | `fix_tax_pack_version` | Country pack release | country, version, description, statutory_basis (Finance Ordinance / SRO), effective_from, effective_to, state, fixture_result, consultant_signoff_ref, approved_by, approved_at |
| `fix.tax.code` | `fix_tax_code` | Tax code definition | pack_version_id, code, name_en, name_bn, type (vat/sd/tds/vds/ait/customs), rate, basis, gl_account_id, register_target, reportable_as |
| `fix.tax.rule` | `fix_tax_rule` | Determination rule | pack_version_id, sequence, condition_json (supply type, item class, party type, place, value band, revenue stream), result_tax_code_id, statutory_reference, effective_from, effective_to |
| `fix.tax.rule.fixture` | `fix_tax_rule_fixture` | Rule test case | rule_id, sample_context_json, expected_result_json, last_run_at, last_result |
| `fix.tax.determination` | `fix_tax_determination` | **The audit spine — one per determined transaction** | transaction_type, transaction_ref, entity_id, tax_point_date, context_json, pack_version_id, rule_id, tax_code_id, taxable_base, tax_amount, statutory_reference, determined_at, outcome |
| `fix.party.tax.profile` | `fix_party_tax_profile` | Counterparty tax status | party_id, bin, bin_active, tin, payee_type (individual/non_individual), psr_status, psr_verified_at, exemption_certificate_ref, withholding_category, verified_by |
| `fix.mushak.sequence` | `fix_mushak_sequence` | Statutory document sequence | entity_id, premises_id, form_type, current_number, allocated_count, cancelled_count, never_reset_assertion |
| `fix.mushak.document` | `fix_mushak_document` | Issued statutory document | form_type (6.3/6.7/6.8), sequence_number, entity_id, premises_id, counterparty_party_id, counterparty_bin, issue_datetime, taxable_value, vat_amount, sd_amount, total, source_module, source_doc_id, state (issued/cancelled), document_id (M24), late_issuance_flag |
| `fix.vat.register.line` | `fix_vat_register_line` | Register entry | register_type (6.1/6.2/6.2.1/6.5/6.6/6.7/6.8), entity_id, period_id, line_date, counterparty_party_id, counterparty_bin, document_reference, taxable_value, vat_amount, sd_amount, credit_eligible, disallow_reason, source_doc_type, source_doc_id, locked_at, adjustment_of_line_id |
| `fix.vat.register.lock` | `fix_vat_register_lock` | Period lock and reconciliation proof | register_type, entity_id, period_id, line_count, total_taxable, total_vat, gl_control_balance, difference, reconciled_at, locked_by |
| `fix.input.credit.ledger` | `fix_input_credit_ledger` | Input VAT credit position | entity_id, period_id, opening_balance, claimed, offset_against_output, disallowed, refund_applied, carried_forward, closing_balance |
| `fix.vat.return` | `fix_vat_return` | Mushak 9.1 | entity_id, period_id, form_version, compiled_at, output_by_rate_json, input_json, adjustments_json, sd_json, net_payable, net_refundable, state, prior_period_variance_json, approved_by, approved_at, filed_at, nbr_acknowledgement_ref, payment_instruction_id, amendment_of_id |
| `fix.vat.adjustment` | `fix_vat_adjustment` | Decreasing / increasing adjustment | return_id, type, reason_code, amount, evidence_doc_id, mushak_6_6_ref, approved_by |
| `fix.withholding.determination` | `fix_withholding_determination` | TDS/VDS decision on a payment | payment_line_ref (M52), payee_party_id, payment_nature, section_or_service_code, payee_type, psr_status, payment_method, base_amount, rate, surcharge_applied, surcharge_reason, deducted_amount, pack_version_id, determined_at |
| `fix.withholding.exemption` | `fix_withholding_exemption` | Why no deduction was made | payment_line_ref, exemption_type (manufacturer_mushak/utility/exempt_supply/efd_invoice/other), evidence_ref, applied_by |
| `fix.tax.deposit.obligation` | `fix_tax_deposit_obligation` | What must be deposited and by when | entity_id, tax_type, section_or_code, period, deduction_line_ids, total_amount, statutory_deadline, state, alert_sent_at, escalated_at |
| `fix.tax.challan` | `fix_tax_challan` | Deposit record | obligation_id, challan_type (a_challan/tr), challan_reference, bank_id, deposit_date, amount, payment_instruction_id (M50), confirmation_ref, document_id, state |
| `fix.withholding.certificate` | `fix_withholding_certificate` | Certificate issued to a payee | type (mushak_6_6/tds_certificate), payee_party_id, period, deduction_line_ids, amount, challan_id, issue_deadline, issued_at, document_id, delivered_to_portal_at, copy_to_circle_at |
| `fix.withholding.received` | `fix_withholding_received` | VDS/TDS deducted from 1000FiX | customer_party_id, invoice_id (M20), amount, certificate_ref, certificate_received_at, claimed_in_return_id, state |
| `fix.tax.calendar.obligation` | `fix_tax_calendar_obligation` | Statutory calendar entry | entity_id, obligation_type, description, frequency, due_rule, next_due_date, owner_role, state, last_completed_at, evidence_ref |
| `fix.tax.depreciation.book` | `fix_tax_depreciation_book` | Tax book by asset | asset_id (M49), asset_class, third_schedule_rate, initial_allowance_rate, initial_allowance_claimed, opening_wdv, addition, depreciation_charge, closing_wdv, income_year |
| `fix.income.tax.computation` | `fix_income_tax_computation` | Corporate tax schedules | entity_id, income_year, accounting_profit, disallowances_json, allowances_json, depreciation_reconciliation_json, taxable_income, tax_rate, tax_liability, advance_tax_paid, balance_payable, state, prepared_by, reviewed_by |
| `fix.advance.tax` | `fix_advance_tax` | AIT paid | entity_id, income_year, instalment, amount, challan_ref, paid_at |
| `fix.tax.provision` | `fix_tax_provision` | Current and deferred tax | entity_id, period_id, current_tax, deferred_tax_movement, temporary_differences_json, raised_to_gl_at |
| `fix.import.tax.record` | `fix_import_tax_record` | Duty and VAT at import | import_consignment_id (M44), bill_of_entry_ref, customs_duty, import_vat, ait, supplementary_duty, total, credit_eligible_vat, registered_in_period_id |
| `fix.high.value.cash.record` | `fix_high_value_cash_record` | NID capture evidence | receipt_id (M20), customer_party_id, amount, threshold_applied, nid_captured (encrypted), captured_by, captured_at, exception_flag, exception_reason |
| `fix.marketplace.tax.model` | `fix_marketplace_tax_model` | The D-03 declared position | entity_id, model (principal/agent), basis_of_charge, rate, external_opinion_ref, declared_by, declared_at, effective_from, state |
| `fix.tax.audit.pack` | `fix_tax_audit_pack` | Evidence pack for NBR | entity_id, period_from, period_to, scope, registers_ref, returns_ref, reconciliations_ref, determination_extract_ref, generated_at, generated_by, provided_to |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.gl.line`, `fix.gl.account`, `fix.fiscal.period` | M19 | Read for register-to-ledger reconciliation and period state |
| `fix.ar.invoice`, `fix.ar.credit.note`, `fix.ar.receipt` | M20 | Read as the supply-side source; supply determination and Mushak format |
| `fix.ap.invoice`, `fix.ap.payment.line` | M52 | Read as the purchase and payment source; supply withholding determination |
| `fix.payment.instruction`, `fix.bank.account` | M50 | Instruct challan deposits; receive confirmation |
| `fix.party`, `fix.party` | M33 | Read BIN, TIN and party type |
| `fix.catalogue.item`, `fix.catalogue.category` | M37 | Read classification to map to a tax code and VDS service code |
| `fix.import.consignment`, `fix.bill.of.entry`, `fix.landed.cost` | M44 | Read for import duty, VAT and credit registration |
| `fix.asset`, `fix.depreciation.run` | M17 / M49 | Read the register as the basis for tax depreciation |
| `fix.revenue.schedule`, `fix.settlement.cycle` | M53 | Read; note that accounting revenue and taxable supply differ in timing |
| `fix.marketplace.job`, `fix.marketplace.fee` | M12 | Read for marketplace determination under the declared model |
| `fix.payroll.run` | M56 | Read employee withholding for consolidated statutory reporting only |
| `fix.country.pack`, `fix.locale.pack` | M65 | The framework M51's Bangladesh content plugs into |
| `fix.document` | M24 | Store Mushak documents, returns, challans and certificates |
| `fix.branch.shift`, `fix.cash.movement` | M04 | Read for the high-value cash rule at the counter |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-TAX-01 | A module requests determination | Evaluate the active pack version at the transaction's tax point, return the treatment with its rule and basis, and write the determination record | **Return an explicit error; the calling operation halts.** No default, no zero, no last-known value |
| AUT-TAX-02 | An invoice is issued in M20 | Allocate the Mushak 6.3 sequence number, record the statutory document, and write the sales register line | Block issuance; an invoice without a statutory number is never released |
| AUT-TAX-03 | A supply occurs without a Mushak 6.3 issued within the statutory timing | Flag late issuance and report it on the daily compliance exception list | Unconditional flag |
| AUT-TAX-04 | A purchase or import invoice is approved in M52 | Determine input VAT, assess credit eligibility, and write the purchase register line | Hold the register line and alert; never assume eligibility |
| AUT-TAX-05 | M52 proposes a payment | Determine the withholding section, rate, payee type, PSR condition and payment method, and return the deduction | **Refuse; M52 cannot release the payment** (BRU-FIN-09) |
| AUT-TAX-06 | A deduction is made | Create the deposit obligation with its statutory deadline and add it to the tax calendar | Obligation created manually with an alert |
| AUT-TAX-07 | A deposit deadline approaches | Alert the Finance Manager, then the CFO, with the amount, section and deadline named; escalate daily | Escalation is unconditional |
| AUT-TAX-08 | Deposit deadline reached | Instruct M50 to deposit and record the challan reference on confirmation | High-priority exception to the CFO |
| AUT-TAX-09 | A challan is confirmed | Generate the withholding certificate, publish it to the payee in P05 within the statutory window, and record the circle-office copy obligation | Certificate queued and escalated |
| AUT-TAX-10 | A Mushak 6.6 is received from a customer | Record the VDS deducted from 1000FiX and queue the decreasing adjustment for the next return | Record as pending certificate and age it |
| AUT-TAX-11 | Period end | Reconcile every register to its GL control account and publish the result to the close checklist | Report the difference and **block return compilation** |
| AUT-TAX-12 | Registers reconciled | Lock the registers, record the lock proof, and compile the Mushak 9.1 | Compilation blocked |
| AUT-TAX-13 | Return compiled | Produce prior-period variance analysis and route to the CFO for approval | Return remains compiled and appears on the overdue-filing risk report |
| AUT-TAX-14 | Return approved | File through the NBR facility, record the acknowledgement, and instruct M50 to pay the net VAT by the 15th | High-priority escalation to the CFO; filing is never silently missed |
| AUT-TAX-15 | Cash receipt at or above the statutory threshold | Require the NID before the receipt can complete, and record the evidence | Hard block at the counter |
| AUT-TAX-16 | Import bill of entry received from M44 | Determine duty, VAT and AIT, confirm accounting into landed cost, and register the import VAT credit | Hold and alert; credit is never assumed |
| AUT-TAX-17 | A marketplace transaction requires determination and D-03 is unsettled | **Refuse determination** and report; marketplace transactions cannot be processed until the model is declared | Hard block — by design |
| AUT-TAX-18 | Finance Ordinance / SRO published (annual, and on interim change) | Open a new pack version, notify the CFO and the tax consultant, and schedule fixture testing before the effective date | Alert repeats until the version is prepared |
| AUT-TAX-19 | Pack version reaches its effective date | Activate the approved version; refuse activation of any version whose fixtures have not passed and which lacks consultant and CFO sign-off | Prior version remains active and a critical alert is raised |
| AUT-TAX-20 | Year end (June) | Compute tax depreciation from M49's register, prepare income-tax computation schedules, and raise the current and deferred tax provision to M19 | Block the year-end close task and report |
| AUT-TAX-21 | Daily | Publish the compliance dashboard: obligations due, filings pending, certificates outstanding, late Mushak issuances, register differences and determination failures | Report with a data-availability warning |
| AUT-TAX-22 | NBR query or audit notice recorded | Generate the tax audit pack for the scope and period, and open a response task with a deadline | Pack generated manually with an alert |

---

## 12. Interfaces

### 12.1 Upstream — M51 Consumes

| Source | What | Mechanism |
|---|---|---|
| M20 Receivables | Invoices, credit notes and receipts as supply-side transactions requiring determination and register entry | REST (determination) + events |
| M52 Payables | Purchase invoices and proposed payments requiring input VAT and withholding determination | REST + events |
| M50 Treasury & Cash | Challan deposit confirmation with bank reference and date; payment method used (bank transfer or otherwise) | Events |
| M19 General Ledger | Control-account balances for register reconciliation; period state; posted transactions for income-tax schedules | REST |
| M44 Import & Landed Cost | Bill of entry, customs duty, import VAT and AIT | Events + REST |
| M49 Fixed Assets | Asset register, classes, additions and disposals as the basis for tax depreciation | REST |
| M53 Revenue & Settlement | Revenue and settlement transactions where the tax point differs from the accounting recognition | Events |
| M12 Marketplace | Marketplace transactions requiring determination under the declared model | REST |
| M33 Party Master | Customer and vendor BIN, TIN, party type | REST |
| M37 Catalogue | Item and service classification mapped to tax codes and VDS service codes | REST |
| M65 Country & Localisation Pack | The country-pack framework the Bangladesh content plugs into | Framework |
| M21 HR & Payroll | Employee withholding totals for consolidated statutory reporting | REST |
| M04 Branch Operations | Counter cash receipts subject to the high-value NID rule | Events |

### 12.2 Downstream — M51 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M20 Receivables | Tax determination per invoice line; Mushak 6.3 format, sequence and issuance rules; NID threshold rule | REST |
| M52 Payables | Withholding determination per payment line; the release gate | REST |
| M50 Treasury & Cash | Challan deposit instructions; the NID threshold for deposit control | Commands + REST |
| M19 General Ledger | Tax liabilities, input credit, adjustments, provisions and deferred tax as financial events for posting | Events |
| M49 Fixed Assets | Tax depreciation rates and the tax book, for the register-to-tax reconciliation | REST |
| M53 Revenue & Settlement | Tax treatment of settlements, commissions and payouts under the declared marketplace model | REST |
| M54 Costing & FP&A | Effective tax rate and tax cost by business line | REST + extract |
| M44 Import & Landed Cost | Confirmation that import tax is correctly treated and credited | Events |
| M23 Quality / Compliance | Statutory obligations, deadlines and findings for the compliance register | Events |
| M25 BI / M62 Data Platform | Tax determination, register, return and compliance facts | Warehouse extract |
| P05 Vendor & Supplier Portal | Withholding certificates (Mushak 6.6, TDS certificates) | REST |
| P04 Corporate B2B Portal | Compliant tax invoices and the customer's own VDS position | REST |
| P03 Admin Portal | Full tax workspace | Native |
| P06 Analytics Dashboard | Compliance dashboard and tax position | REST |
| NBR (via authorised filing) | Mushak 9.1 returns, withholding statements, challans | External |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `tax.determined` | transaction, tax point, code, rate, base, amount, rule version, statutory basis | M19, M20, M52, M25 |
| `tax.determination_failed` | transaction, context, failure reason | M20, M52, M23, CFO |
| `tax.mushak_issued` | form type, sequence number, entity, counterparty, values | M20, M19, M24 |
| `tax.mushak_late_issuance` | supply, expected time, actual time | M23, CFO |
| `tax.register_line_written` | register type, period, values, source document | M19, M25 |
| `tax.register_reconciled` / `tax.register_variance` | register, period, register total, GL total, difference | M19, M23 |
| `tax.registers_locked` | period, registers, totals, lock proof | M19, M24 |
| `tax.return_compiled` | entity, period, net payable, variance analysis | M19, M50, CFO |
| `tax.return_filed` | entity, period, acknowledgement reference, amount paid | M19, M23, M24, M25 |
| `tax.return_amended` | original return, amendment, reason | M19, M23, CFO |
| `tax.withholding_determined` | payee, section, rate, base, surcharge condition | M52, M19 |
| `tax.withholding_deducted` | payee, amount, payment reference, deposit obligation | M19, M52, M50 |
| `tax.deposit_due` / `tax.deposit_overdue` | tax type, section, amount, deadline | M50, CFO, M23 |
| `tax.challan_deposited` | obligation, challan reference, bank, date, amount | M19, M52, M50 |
| `tax.certificate_issued` | payee, type, period, amount, document | M52, P05, M42 |
| `tax.high_value_cash_recorded` | receipt, amount, NID captured flag | M50, M20, M23 |
| `tax.pack_version_activated` | country, version, statutory basis, effective date, approver | M19, M20, M52, M65, M23 |
| `tax.provision_raised` | entity, period, current tax, deferred movement | M19, M54 |
| `tax.compliance_exception` | type, description, severity, owner | M23, CFO, M25 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-TAX-01 | NBR VAT online system (`vat.gov.bd`) | Bidirectional | Mushak 9.1 filing and acknowledgement; BIN verification where the facility permits |
| INT-TAX-02 | NBR income-tax e-filing facility | Outbound | Withholding statements and return submission support |
| INT-TAX-03 | A-Challan / Treasury Challan deposit (via banks, executed by M50) | Outbound | Deposit of VAT, VDS and TDS |
| INT-TAX-04 | External tax consultant / advisory firm | Bidirectional | Country-pack review and sign-off; **the D-03 marketplace opinion**; audit query support |
| INT-TAX-05 | NBR SRO and Finance Ordinance publication monitoring | Inbound | Annual and interim statutory change intake |
| INT-TAX-06 | Bangladesh Customs / ASYCUDA bill of entry (via M44) | Inbound | Import duty, VAT and AIT data |
| INT-TAX-07 | Legacy VAT registers and return workings | Inbound, one-time | Opening credit balance and open positions; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/tax/determine` | POST | **The determination service** — returns treatment, rate, code, basis and rule version | M20, M52, M50, M53, M12, M44, M13, M14, M38 |
| `/api/v1/tax/determinations/{ref}` | GET | Retrieve a stored determination with its full basis | P03, auditor, M20, M52 |
| `/api/v1/tax/mushak/sequence` | POST | Allocate a statutory document number | M20 |
| `/api/v1/tax/mushak/format/{form}` | GET | Statutory format definition for rendering | M20 |
| `/api/v1/tax/registers/{type}` | GET | Register lines for a period, with totals | P03, auditor, M19 |
| `/api/v1/tax/registers/{type}/reconcile` | POST | Run register-to-ledger reconciliation | P03 |
| `/api/v1/tax/returns/{entity}/{period}` | GET · POST | Compile, review, approve and file the Mushak 9.1 | P03 |
| `/api/v1/tax/input-credit/{entity}` | GET | Input credit balance and movement | P03, P06 |
| `/api/v1/tax/withholding/determine` | POST | Withholding determination for a proposed payment | M52 |
| `/api/v1/tax/withholding/deductions` | GET | Deductions by section, period and payee | P03, M52 |
| `/api/v1/tax/obligations` | GET | Statutory calendar with due dates, owners and status | P03, P06 |
| `/api/v1/tax/challans` | POST · GET | Deposit obligations and challan records | P03, M50 |
| `/api/v1/tax/certificates/{payee}` | GET | Withholding certificates for a payee | P05, P03 |
| `/api/v1/tax/nid-threshold` | GET | The high-value cash threshold and rule | M20, M04, M50 |
| `/api/v1/tax/pack-versions` | GET · POST | Author, test, approve and activate a country-pack version | P03 |
| `/api/v1/tax/marketplace-model` | GET · POST | The declared principal/agent position (D-03) | M12, M53, M20, P03 |
| `/api/v1/tax/audit-pack` | POST | Generate an evidence pack for a scope and period | P03, auditor |
| `/api/v1/tax/income-tax/{entity}/{year}` | GET | Income-tax computation schedules | P03, auditor |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R03 Chief Financial Officer | R U A | All entities; approves pack versions, returns, the marketplace model and amendments |
| R26 Finance Manager | C R U A | All entities; compiles returns, manages obligations and certificates, resolves register variances |
| R27 Finance Officer | C R | Assigned scope; register review, certificate issuance, challan tracking — **cannot approve a return or activate a pack version** |
| R02 Chief Technology Officer | R | Pack-version technical review, determination-service operations; **no approval rights** |
| R33 IT / System Administrator | R | Configuration support; **no tax rate authorship, no approval** |
| R32 Quality Manager / ISO Coordinator | R | Compliance calendar, exceptions and findings register |
| R29 Cashier / Counter Finance | R | The NID rule prompt only; no other tax visibility |
| R19 Procurement Officer | R | Vendor withholding position and certificates for their vendors |
| R28 Warranty Claims Officer | R | Tax treatment of claim invoices only |
| R01 Chief Executive Officer | R | Compliance dashboard and filing status |
| R38 External Tax Consultant | R U | Scoped: pack-version review and sign-off, audit-pack access; **cannot activate or file** |
| R38 External Auditor | R | Scoped read-only — registers, returns, reconciliations, determinations |
| R38 Vendor | R | Own withholding certificates only (P05) |
| R37 Corporate Portal User | R | Own tax invoices and own VDS position only (P04) |

**Field-level restrictions.** Customer NID captured under the high-value cash rule is
field-level encrypted, masked to all roles, and unmaskable only by R03 and R26 with every access
logged (AS-14, BRU-TAX-19). Counterparty PSR status and exemption certificates are visible to
R03, R26, R27 and R19 only.

**Segregation of duties.**
- The user who authors a country-pack version cannot approve or activate it.
- The user who compiles a return cannot approve it; approval is CFO-only.
- The user who determines a withholding cannot release the payment it applies to — the determination is in M51 and the release is in M52, by two different roles in two different modules.
- R33 IT / System Administrator can operate the service but can never author a tax rate or approve a version.
- The external tax consultant can review and sign off but can never activate a version or file a return.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Compliance dashboard** | CFO, CEO, board | Real time | Obligations due, filings status, certificates outstanding, deposits pending, determination failures, findings — against the zero-findings target |
| **Statutory calendar** | CFO, Finance Manager | Continuous | Every filing, deposit and certificate obligation with deadline, owner and status |
| **Mushak 9.1 return pack** | CFO, tax consultant, NBR | Monthly | The return with its register backing, reconciliation and variance analysis |
| **Register-to-ledger reconciliation** | CFO, Finance Manager, auditor | Monthly | Each register against its GL control account, with differences and explanations |
| **VAT position summary** | CFO, Finance Manager | Monthly | Output by rate, input claimed and disallowed, adjustments, net position, credit carried forward |
| **Input credit ageing and disallowance** | CFO, Finance Manager, Procurement | Monthly | Credits claimed, disallowed with reason, and at risk through missing documentation |
| **Mushak issuance compliance** | CFO, Quality Manager | Weekly | Documents issued, sequence continuity assertion, late issuances, cancellations |
| **Withholding summary** | CFO, Finance Manager | Monthly | Deductions by section and service code, surcharge cases, base and rate distribution |
| **Deposit and challan register** | CFO, auditor | Monthly | Obligations, deadlines, deposits, challan references and any late deposit |
| **Certificate issuance tracker** | Finance Manager, Procurement | Weekly | Certificates due, issued within window, overdue, by payee |
| **VDS received and claimed** | CFO, Finance Manager | Monthly | Mushak 6.6 received from customers, claimed as decreasing adjustment, pending |
| **High-value cash register** | CFO, Quality Manager, auditor | Monthly | Every receipt above the threshold with NID evidence, and any exception |
| **Determination failure report** | CFO, CTO | Daily | Every failed determination with the transaction it halted — a leading indicator of a country-pack gap |
| **Country pack version register** | CFO, CTO, auditor, tax consultant | On change | Every version with statutory basis, fixtures, consultant sign-off, approval and effective dates |
| **Effective tax rate by business line** | CFO, CCO, M54 | Quarterly | Tax cost across the 14 revenue streams |
| **Income tax computation pack** | CFO, tax consultant, auditor | Annual | Schedules, depreciation reconciliation, disallowances, advance tax and liability |
| **Tax audit evidence pack** | NBR, CFO, tax consultant | On demand | Registers, returns, reconciliations and transaction-level determination extract for the scope |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| **KPI-057** | VAT returns filed on time with zero adjustment *(re-owned from M19 — see register note)* | manual | 100% | **100%** |
| **KPI-058** | Tax compliance findings *(re-owned from M19)* | unmeasured | **Zero** | **Zero** |
| — | Withholding deposits made by the statutory deadline | unmeasured | 100% | **100%** |
| — | Withholding certificates issued within the statutory window | manual | 98% | **100%** |
| — | Payments released without a withholding determination | unknown | **Zero** | **Zero** |
| — | Mushak 6.3 sequence gaps or reuse | unknown | **Zero** | **Zero** |
| — | Supplies with a late Mushak 6.3 issuance | unmeasured | < 1% | **Zero** |
| — | Register-to-ledger unexplained differences at period close | unmeasured | < 3 | **Zero** |
| — | Input VAT credit lost through missing or invalid documentation | unknown | < 2% | **< 0.5%** |
| — | Determination failures outstanding beyond 24 hours | n/a | < 5 | **Zero** |
| — | Elapsed time to compile the Mushak 9.1 from period close | 5–7 days | < 1 day | **< 4 hours** |
| — | Country-pack version activated by its statutory effective date | n/a | 100% | **100%** |
| — | High-value cash receipts with NID evidence | unmeasured | 100% | **100%** |
| — | NBR query response time | weeks | < 5 days | **< 2 days** |
| — | Late-filing penalties or interest incurred | unknown | **Zero** | **Zero** |

> **Register note.** **KPI-057** and **KPI-058** are allocated to **M19** in `06-02` §2.7. Under
> the v2.1 re-scope, tax compliance is owned by **M51**; the register requires updating —
> recorded as audit action **A-01**. The thirteen unnumbered metrics are new to this
> specification and require allocation in `06-02` — audit action **A-02**.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `account` — tax objects, tax groups, tax lines on documents | 12% |
| L2 | OCA `account-fiscal-rule` (fiscal positions and simple mapping), `account-financial-reporting`, `l10n` structural patterns | 12% |
| L3 | Free form-rendering and PDF utilities | 3% |
| L5 | `cd_tax_engine_bd`, `cd_mushak`, `cd_vat_register`, `cd_vat_return`, `cd_tds`, `cd_nid`, `cd_income_tax_schedules` | **73%** |

> **The highest custom share of any module in the programme, and unavoidably so.** No Bangladesh
> localisation of adequate depth exists in the Odoo ecosystem, and no commercial tax engine
> carries NBR content. Every Mushak form, every register, the 9.1 return, the withholding regime
> and the country-pack framework must be built. This is also why M51 is the module whose
> effort estimate most exceeds the `02-02` figure.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 5 of 7 identifiers below are claimed by another module: **CD-083** also claimed by M57; **CD-084** also claimed by M22; **CD-085** also claimed by M22; **CD-086** also claimed by M22; **CD-173** also claimed by M48. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-173** | `cd_tax_engine_bd` — determination service, rule model, effective-dated evaluation, country-pack versioning and fixtures, fail-closed contract, party tax profiles | Odoo module + service | **7 PW** |
| CD-083 | `cd_mushak` — statutory document formats as versioned data, sequence control, issuance timing rules, Bengali statutory rendering, credit and debit notes | Odoo module | **5 PW** |
| CD-084 | `cd_vat_register` — registers 6.1, 6.2, 6.2.1, 6.5, 6.6, 6.7, 6.8; append-and-lock; register-to-ledger reconciliation; input credit ledger | Odoo module | **5 PW** |
| **CD-174** | `cd_vat_return` — Mushak 9.1 compilation from locked registers, variance analysis, approval, filing, acknowledgement, adjustments and refund application | Odoo module | 4 PW |
| CD-085 | `cd_tds` — TDS and VDS determination by section and service code, payee type and PSR conditions, deposit obligations and calendar, challans, certificate issuance, VDS received | Odoo module | **5 PW** |
| CD-086 | `cd_nid` — high-value cash threshold rule, NID capture contract for M20/M04, encrypted storage, evidence register and exception reporting | Odoo module | 1 PW |
| **CD-175** | `cd_income_tax_schedules` — Third Schedule tax depreciation book, taxable income computation, disallowances, advance tax, current and deferred provision | Odoo module | 3 PW |

> **CD register reallocation.** `02-05` §5.2 allocated **CD-083** (`cd_mushak`), **CD-084**
> (`cd_vat_register`), **CD-085** (`cd_tds`) and **CD-086** (`cd_nid`) to **M19**. All four move
> to **M51** under the v2.1 re-scope. Three new IDs, **CD-173…175**, are claimed from the
> Category G block defined in `M19` §16.2. **All CD IDs remain provisional** pending the unified
> CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M51 is scheduled in **W4** (P0) but declares a dependency on 1 module(s) that land later: **M65** (W9). One of three things must be true before the W4 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W4 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M51 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W4 plan for M51 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M19 General Ledger (W3) | Register-to-ledger reconciliation and tax posting |
| M20 Receivables (W3) | The supply side; Mushak 6.3 issuance is executed by M20 |
| M52 Payables (W3) | The purchase and withholding side |
| M50 Treasury & Cash (W3) | Challan deposit execution |
| M65 Country & Localisation Pack | The framework M51's content plugs into. **M65 is W9** — M51 ships its own effective-dated versioning in W4 and is refactored onto M65's contract in W9. Recorded in §18 Q-05 |
| M33 Party Master | BIN, TIN and party type as determination inputs |
| M37 Catalogue | Classification-to-tax-code mapping |
| M44 Import & Landed Cost | Import duty and VAT. **M44 is W6** — import tax records are entered from the bill of entry manually until then |
| M49 Fixed Assets | Tax depreciation basis. **M49 is W5** — FR-TAX-040 activates with M49 |
| M12 Marketplace | **Blocked by decision D-03** — the marketplace VAT model must be settled before Wave 7 build |
| **External tax opinion (D-03)** | **Not a system dependency but a hard gate.** The marketplace model cannot be configured, and marketplace determination is refused, until it exists |

> **The Wave 3 / Wave 4 tension.** M20 and M52 need determination in Wave 3; M51 lands in
> Wave 4. Two provisional arrangements operate in the W3 window and are retired at M51 go-live:
> (a) M20 runs against a **standard-rate determination stub** and the VAT registers are
> **reconstructed** on M51 go-live from the issued invoices; (b) M52 runs against a
> **CFO-maintained provisional rate table** with the identical fail-closed hard-gate behaviour.
> Both are recorded as blocking questions in the receiving modules (`M20` §18 Q-03, `M52` §18
> Q-02) and here as Q-01. **The reconstruction of W3 VAT registers is a defined, resourced
> migration task, not an assumption.**

**Delivers into:** M20 (determination and Mushak), M52 (withholding gate), M50 (challans),
M19 (tax postings and provisions), M49 (tax depreciation), M53 (settlement tax treatment),
M12 (marketplace model), M54 (effective tax rate).

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Entity registration data (BIN, TIN, circle, premises) | Per entity | `fix.tax.registration` | W4 minus 2 months |
| Current-year statutory rates, codes and forms | Full FY pack | `fix.tax.pack.version` and children | W4 minus 3 months |
| Prior-year pack (for backdated transactions and comparatives) | 1–2 years | `fix.tax.pack.version` (superseded) | W4 minus 2 months |
| Opening input VAT credit balance | Per entity | `fix.input.credit.ledger` | W4 cutover, NBR-position confirmed |
| Mushak 6.3 sequence position at cutover | Per entity and premises | `fix.mushak.sequence` | **W4 cutover — continuity critical** |
| **W3-period VAT registers (reconstruction)** | 3–5 months of M20/M52 transactions | `fix.vat.register.line` | **W4 — defined migration task** |
| Open withholding deposits and unissued certificates | Current only | `fix.tax.deposit.obligation`, `fix.withholding.certificate` | W4 cutover |
| Mushak 6.6 received but unclaimed | Current only | `fix.withholding.received` | W4 cutover |
| Customer and vendor BIN/TIN, payee type, PSR status | All active parties | Via M33 masters + `fix.party.tax.profile` | W4 minus 1 month |
| Tax depreciation opening WDV per asset | Per asset (with M49, W5) | `fix.tax.depreciation.book` | W5 |
| Prior-year filed returns and challans | 2 years | `fix.vat.return`, `fix.tax.challan` (reference only) | W4, best-effort |

> **Migration position — non-negotiable.** The **Mushak 6.3 sequence must continue without a
> gap or a reset across cutover**. A sequence discontinuity is the first thing an NBR audit
> looks for, and it cannot be corrected afterwards. The cutover number is agreed with the tax
> consultant, recorded, and asserted immediately after go-live. Separately, the **opening input
> VAT credit balance must be agreed to the last filed Mushak 9.1**, not to a book balance, and
> the difference — if any — resolved before cutover rather than carried.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | No tax rate, threshold, service code or deadline exists as a literal in application code | CI static-analysis check plus code review |
| AC-02 | Determination uses the transaction's tax point date; a backdated transaction is determined under the law in force at that date | Scripted scenario across a rate-change boundary |
| AC-03 | Determination fails closed: with the service unavailable, M20 cannot issue an invoice and M52 cannot release a payment | Negative test with the service disabled, in both consumers |
| AC-04 | Every determination stores its inputs, rule version, rate, statutory basis and outcome, retrievable for seven years | Full-table assertion plus an archive query test |
| AC-05 | Determination p95 latency is ≤ 150 ms at production volume | Performance test |
| AC-06 | Mushak 6.3 sequences are gapless per entity and premises under concurrency and rollback, and a number is never reused | Concurrency test at 100 parallel issuances plus a continuity audit |
| AC-07 | Every issued Mushak 6.3 carries all mandatory elements per Rule 40(1) and renders correctly in Bengali | Statutory format review by the external tax consultant |
| AC-08 | The Mushak 6.3 sequence continues without a gap or reset across cutover | Sequence assertion signed by the tax consultant post-go-live |
| AC-09 | Registers are append-only within an open period and immutable after lock; corrections appear only as referencing adjustments | Negative test plus a full-table assertion |
| AC-10 | A return cannot be compiled while any register fails to reconcile to its GL control account | Negative test |
| AC-11 | A return cannot be filed without CFO approval of the compiled version | Negative test |
| AC-12 | Twelve consecutive VAT returns are filed by the 15th with zero subsequent adjustment | Twelve monthly filing records (KPI-057) |
| AC-13 | Every figure in a filed return traces to its register lines and thence to its source transactions | Traceability test on every return line |
| AC-14 | No payment is released without a withholding determination, including where the payee type or PSR status is unknown | Negative test per condition |
| AC-15 | The elevated rate applies automatically where the payee has no valid PSR or payment is not by bank transfer, and the condition is recorded | Scripted scenario per condition and in combination |
| AC-16 | VDS is not deducted where a statutory exemption applies, and the exemption basis is recorded | Negative test across each exemption type |
| AC-17 | Every withholding deposit is made by its statutory deadline, including under the compressed June schedule | Twelve months of deposit records |
| AC-18 | Every withholding certificate is issued within the statutory window and is available to the payee in P05 | Twelve months of certificate records |
| AC-19 | A cash receipt at or above the statutory threshold cannot complete without NID capture, through any path | Negative test on counter, portal and API |
| AC-20 | Customer NID is encrypted, masked to all roles by default, and every unmasking is logged | Security review and log inspection |
| AC-21 | A country-pack version cannot be activated without passing fixtures, consultant sign-off and CFO approval | Negative test per missing precondition |
| AC-22 | A statutory rate change is delivered as a configuration release with no code deployment | Rehearsed change against a simulated SRO |
| AC-23 | **Marketplace determination is refused while decision D-03 is unsettled**, and no default treatment is applied | Negative test |
| AC-24 | Once D-03 is declared, the model applies without exception to every marketplace transaction | Full-table assertion after declaration |
| AC-25 | The W3-period VAT registers are reconstructed completely and reconcile to the M19 ledger for those periods | CFO- and consultant-signed reconciliation |
| AC-26 | The opening input VAT credit balance agrees to the last filed Mushak 9.1 | Consultant-signed agreement |
| AC-27 | A tax audit evidence pack for any period generates on demand with transaction-level determination detail | Timed generation test |
| AC-28 | All statutory documents render in Bengali to the prescribed layout, not merely translated | Format review by the external tax consultant |
| AC-29 | CFO and the external tax consultant sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 29 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **M20 and M52 need determination in W3; M51 lands in W4.** Are the provisional stubs — a standard-rate determination stub for M20 with W3 register reconstruction, and a CFO-maintained rate table for M52 — approved, resourced and reconciled? Or must M51's determination service be pulled forward to W3? | CFO / CTO / Programme Director | **W3 minus 4 months — blocking for M20 and M52** |
| Q-02 | **Decision D-03: is 1000FiX a principal or an agent for marketplace VAT?** NBR guidance indicates VAT on commission and service charges rather than gross transaction value, but the Company's position requires a formal external tax opinion. **This blocks Wave 7 and is the highest-rated commercial risk in the programme** | CFO / CEO / external tax counsel | **Before Wave 7 build — blocking** |
| Q-03 | Which external tax consultant or firm signs off each country-pack version, on what engagement terms, and within what turnaround? The annual July release depends on this being contracted, not ad hoc | CFO | W4 minus 3 months |
| Q-04 | What is 1000FiX's VAT registration structure — one BIN per legal entity, or separate registrations per premises? Register scope, sequence scope and return count all depend on it | CFO / tax consultant | **W4 minus 3 months — structural** |
| Q-05 | M65 Country Pack is W6 but M51 is W4. Is M51 shipping its own versioning in W4 and refactoring onto M65's contract in W6 accepted, with the refactor budgeted? | CTO / CFO | W4 design |
| Q-06 | Which of the 14 revenue streams attract a reduced rate, an exemption or a special treatment, and what is the SRO basis for each? Rental, refurbished resale, data services and managed services each need a determined position | CFO / tax consultant | **W4 design — determines the rule set** |
| Q-07 | Which purchase categories fall within the 45 VDS-specified services, and what are their service codes? Repairing and servicing of taxable goods (S031.00) is directly relevant to sub-contracted work | CFO / tax consultant | W4 design |
| Q-08 | Is the high-value cash threshold BDT 50,000 as stated in the BRD, and is it current? The rule is configuration, but the current value must be confirmed against the prevailing NBR position | CFO / tax consultant | W4 build |
| Q-09 | Does the NBR filing facility support a machine interface for Mushak 9.1 submission, or is filing manual with the system preparing the data? | CFO / CTO | W4 design |
| Q-10 | Is 1000FiX using an EFD or SDC device at any branch counter, and does that change the Mushak issuance or VDS exemption treatment for those transactions? | CFO / tax consultant | W4 design |
| Q-11 | Is the corporate income tax rate the private-company rate, and are any reduced or sectoral rates applicable? | CFO / tax consultant | W5 |
| Q-12 | How many prior years of registers and returns must be available in the system rather than as archived documents? | CFO / tax consultant | W4 minus 2 months |
| Q-13 | Is turnover tax relevant to any group entity, or is every entity within the standard VAT regime? | CFO / tax consultant | W4 design |
| Q-14 | What is the escalation path and decision authority when a statutory change is enacted with an effective date earlier than the pack can be prepared and approved? | CFO / CTO | W4 build |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2 (module definition), §4 (money flow), §5 (boundary map),
**§6 (Bangladesh statutory obligations — the definitive scope table)**, §8 (KPIs), §9 (delivery
sequence), §10 (risks — **D-03**) ·
`M19_Financial_Accounting_and_General_Ledger.md` (posting engine, control accounts, July–June
fiscal year, Category G CD block) ·
`M20_Accounts_Receivable_Invoicing_and_Collections.md` (Mushak 6.3 issuance, NID capture,
determination consumption) ·
`M52_Accounts_Payable_and_Employee_Expense.md` (withholding gate at payment release) ·
`M50_Treasury_Cash_and_Banking.md` (challan deposit execution) ·
`M53_Revenue_Recognition_Commission_and_Settlement.md` (tax point vs recognition timing) ·
`M49_Fixed_Assets_and_Capital_Investment.md` (asset register as the tax depreciation basis) ·
`M54_Cost_Accounting_Budgeting_and_FPA.md` (effective tax rate by business line) ·
`03_Modules/E_Supply_Chain_and_Inventory/M44_Import_Trade_Compliance_and_Landed_Cost.md` ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md`
(the transactions D-03 governs) ·
`03_Modules/K_Platform_and_Technology/M65_Multi_Entity_Multi_Country_and_Localisation.md` (the framework) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category G, §7 ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 ·
`05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` BRU-FIN-01,
BRU-FIN-02, BRU-FIN-08, BRU-FIN-09 ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` NFR-021, NFR-022 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §2.7 (KPI-057,
KPI-058), BO-10, BO-18

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-FIN-005, BR-FIN-006,
BRU-FIN-01, BRU-FIN-02, NFR-021, NFR-022, Automation A11, STK-19 (NBR as stakeholder),
§Data Retention (7 years, Companies Act / NBR), §Process 5 (Mushak VAT invoice in the
invoice-to-cash flow) · `1000FiX_Services_Company_Profile.md` §Authorized Service Partnerships
(imports for 17+ brands), §Core Services (the 14 revenue streams requiring distinct treatments)

**External benchmark and statutory basis**
[Mushak 6.3 VAT invoice — Rule 40(1), VAT & SD Rules 2016: mandatory elements, BIN display, retention](https://rakibhassan.eu/mushak-6-3-vat-invoice-bangladesh/) ·
[Mushak 9.1 VAT return — structure, 15th-of-month deadline, supporting registers (6.1, 6.2, 6.3, 6.5, 6.6, 6.7/6.8), input credit conditions, late-filing penalty and 2% monthly interest, BIN suspension risk](https://rakibhassan.eu/vat-return-bangladesh-mushak-9-1-guide/) ·
[VAT & SD Act 2012 — scope and compliance obligations](https://smartvat.com.bd/blog/vat-act-2012-bangladesh-business-guide/) ·
[TDS & VDS rates Bangladesh FY 2025–26 — s.89 contractor/supplier, s.90 services split by individual (15%) and non-individual (7.5%), s.109/110 rent 10%, s.114 electricity 4%, s.116 foreign buyer agent 7.5%; deposit deadlines including the compressed June schedule; Mushak 6.6 within 3 working days of return filing; s.142 50% surcharge for no PSR or non-bank payment; VDS exemption set](https://rakibhassan.eu/tds-vds-rates-bangladesh-2025-26/) ·
[ICAB — changes in VAT Deduction & Collection at Source 2025-26](https://www.icab.org.bd/icabadmin/uploads/ckeditor/5679Changes_in_VDS_2025-26.pdf) ·
[VDS rates by service code, SRO 182-Ain/2025/310-Mushak — VDS mandatory for 45 specified services](https://www.caripon.com/vat-deduction-rate-2025-26-in-bangladesh/) ·
[Income Tax Act 2023 Third Schedule — depreciation rates: building 5%, factory building 10%, furniture and office equipment 10%, plant and machinery 10%, motor vehicles 10% (20% for hire), computer hardware 25%; initial allowance 10% buildings / 25% machinery; accelerated 50/30/20](https://www.taxvatpoint.com/income-tax-act-2023-3rd-schedule-part-1/) ·
[Deloitte Bangladesh tax highlights — corporate rates](https://www.deloitte.com/content/dam/assets-shared/docs/services/consulting/2024/dttl-tax-bangladeshhighlights-2023.pdf) ·
[NBR guidance on e-commerce VAT — VAT applies to the platform's commission and service charges, not the gross transaction value; the evidence base for decision D-03](https://www.tbsnews.net/bangladesh/vat-e-commerce-agencies-commissions-only-not-customers) ·
[Online marketplace VAT treatment discussion](https://www.tbsnews.net/nbr/online-marketplaces-may-be-exempted-vat-challans-636998) ·
[NBR VAT FAQ](https://nbr.gov.bd/faq/vat-faq/eng) ·
SAP S/4HANA Advanced Compliance Reporting — statutory report content shipped and versioned
separately from the engine · Oracle Fusion Tax — determination as a service with a separate tax
reporting ledger · Microsoft Dynamics 365 Electronic Reporting — statutory formats as
configuration data rather than code

---

*Module M51 · Category G · 1000FiX ERP System v2.0 · CONFIDENTIAL*
