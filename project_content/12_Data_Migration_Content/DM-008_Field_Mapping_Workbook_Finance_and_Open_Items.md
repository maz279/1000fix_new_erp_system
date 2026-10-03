---
id: DM-008
title: Field Mapping Workbook — Finance and Open Items
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration with Finance
author: Data Migration analysts with the Financial Controller
reviewers: [CFO, Financial Controller, Tax Manager, External Auditor, Master Data Owner, Warehouse Manager, QA Lead]
approver: CFO
content_class: C
purpose: >
  Maps the opening trial balance, open receivables and payables, bank and cash positions, tax
  opening positions and fixed-asset opening values to the ERP finance model, at the document level
  the ledger requires rather than as balances. Financial migration is the least forgiving in the
  programme: it must balance exactly, be auditable, tie every control account to its subledger, and
  carry the Mushak 6.3 sequence across cutover without a gap, because a sequence discontinuity is
  the first thing an NBR audit looks for and cannot be corrected afterwards.
traces_to: [M19, M20, M50, M51, M52, M49, M53, M54, MD-035, MD-036, MD-037, MD-038, MD-039, MD-040, DM-001, DM-002, DM-003, DM-004, DM-007, DM-011, DM-013, DM-014]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: DM-008_Field_Mapping_Finance_and_Open_Items.xlsx
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M19 §16.4 — migration position non-negotiable; opening balances from a trial balance signed by the CFO and agreed with the external auditor, every control account reconciled to its subledger, and one full parallel month-end close reconciled line by line before the legacy system is retired; FR-FIN-045 opening balance load; fix.opening.balance.load entity
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M20 §16.4 — open items migrate at open-item level never as a customer balance total; every item carries its original document number and date; the total must reconcile exactly to the receivable control account; each of the top 50 customer balances confirmed with the customer in writing
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M51 §16.4 — the Mushak 6.3 sequence must continue without a gap or a reset across cutover; the opening input VAT credit balance must be agreed to the last filed Mushak 9.1; W3-period VAT register reconstruction is a defined migration task
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M50 §16.4 and M52 §16.4 and M49 §16.4 and M53 §16.4 — cash counted and witnessed; bank balances from the bank's statement; vendor bank details re-verified by independent call-back; fixed assets physically verified; deferred revenue rebuilt obligation by obligation
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 §Gate 3 — G3-04 Mushak invoices accepted with zero NBR exceptions; G3-05 first full month-end closed within 5 days; G3-08 financial history migrated and reconciled to the trial balance; G3-09 branch cash reconciling daily
    verified: 2026-08-18
    class: P1
  - source: Value Added Tax and Supplementary Duty Act 2012 with the VAT and SD Rules 2016 — Mushak 6.3 is the prescribed tax invoice under Rule 40(1); VAT records must be preserved for a minimum of five years
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# DM-008 — Field Mapping Workbook: Finance and Open Items

> Governs `DM-008_Field_Mapping_Finance_and_Open_Items.xlsx`. The markdown governs; the workbook
> loads.
>
> **Template conformance note.** As `DM-004`: `TPL_Master_Data_Specification.md` retained in full;
> the `CG-009` source-to-target column set is inherited from `DM-004` §2.1 (`CP-01`).
>
> **Identifier note (`CG-005` §3.3).** `DM-008` is a **content** identifier; `05-02` `DM-07`
> (modelling standard — monetary fields with an explicit `currency_id`, never floats) and `DM-03`
> (dimensional context) are cited with their document prefix.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Financial accounting, receivables, payables, treasury, tax and fixed assets |
| Owning module | `M19` FIN; `M20` ARB; `M52` APE; `M50` TRE; `M51` TAX; `M49` FXA; `M53` REV; `M54` FPA |
| Data steward | Financial Controller |
| Golden source | **The CFO-signed, auditor-agreed trial balance** — not the accounting software export |
| Refresh cadence | Once, at cutover, with a delta for the parallel-run period |
| Environments | Dev · SIT · UAT · Prod — bank account numbers masked in non-production (`NFR-086c`) |
| Content class | C — Operational-critical *(with Class A consequence at the `M51` boundary — see §2.7)* |
| Effective-dated | no |
| **Build wave** | **W1** *(the register wave — `MS-22`)* |
| **Load wave** | **W3** — `M19`, `M20`, `M50`, `M52` §16.4 and `06-01` W3; **tax W4** (`M51`); **fixed assets and budget W5–W6** (`M49`, `M54`) |

**Consequence of absence (`CP-03`).** `M19` §16.4 states it as a category risk: *"financial history
migration does not reconcile — opening balances wrong forever."* An opening balance is not a
starting value that can be improved later; it is the anchor every subsequent figure is measured
against.

| Failure | Consequence |
|---|---|
| Open items loaded as customer balance totals | *"A migrated balance without its underlying invoices cannot be collected, disputed or credited, and it destroys ageing accuracy from day one"* (`M20`) |
| Cash loaded from the book balance rather than counted | `G3-09` daily branch cash reconciliation never reaches target; every exception is contaminated |
| Bank balance loaded from the legacy book | Reconciling items are invisible; the first bank reconciliation cannot be completed |
| **Mushak 6.3 sequence reset at cutover** | **The first thing an NBR audit looks for, and it cannot be corrected afterwards** |
| Deferred revenue loaded as a total | `M53`'s central control — *deferred revenue reconciled to contracts, 100%* — is unachievable from day one |
| Vendor bank details carried unverified | **Migration is the single most attractive moment for a payment-redirection fraud** (`M52`) |
| Chart of accounts migrated as-is by default | The rationalisation decision (`M19` `Q-02`) is made by omission, permanently |

---

## 2. Record structure

Target structures are `05-02` §6 (`M19`, `M20`) and `MD-035`, `MD-037`, `MD-038`, `MD-040`. Not
restated (`CP-01`). Mapping column set: `DM-004` §2.1.

### 2.1 The five finance origins

**`FO-01`: every finance figure entering the ledger carries an `origin`, and each origin has a
different signatory.**

| `origin` | Population | Evidence | Signed by |
|---|---|---|---|
| **`trial_balance`** | Opening GL balances | The trial balance itself | **CFO, agreed with the external auditor** |
| **`open_item`** | AR, AP, advances, retention, deposits, disputes | The original document — number, date, amount | Financial Controller; **top 50 AR balances confirmed with the customer in writing** |
| **`counted`** | Cash at branches, technician floats, petty cash, cheque stock | Witnessed count sheet, signed | Branch manager **and** Financial Controller |
| **`third_party_confirmed`** | Bank balances and reconciling items; gateway clearing balances; brand consignment settlement | **The bank's / provider's / brand's own statement** | Financial Controller with the counterparty's document |
| **`statutory_agreed`** | Opening input VAT credit; tax-book WDV; Mushak sequence position | Last filed Mushak 9.1; last filed income-tax return; tax consultant's agreement | **CFO with the tax consultant** |

> **`FO-02`.** No finance figure loads with `origin = extracted`. The accounting software export is
> an **input to** the trial balance, not the trial balance. This distinction is the entire content
> of `M19`'s non-negotiable position.

### 2.2 Map A — chart of accounts

| Source | Target | Rule |
|---|---|---|
| Legacy CoA, 400–800 accounts | `MD-035` structure → `fix.gl.account` | **`FO-03`** — mapped **and rationalised**, or mapped as-is; the choice is `M19` `Q-02` and is **unresolved** |
| Legacy account → new account | Cross-reference table | Retained permanently. Comparatives, the parallel close and any audit query all need it |
| Dimension requirements | `requires_dimension` per `MD-035` | **`FO-04`** — legacy accounts carry no dimensional history. Migrated postings take a `MIGRATION` cost centre and business line, **never a guessed one** (`05-02` `DM-03`) |
| Control accounts | `is_control_account`, `control_subledger` | Every control account must have a subledger population loaded and reconciling (`FO-08`) |
| Statutory grouping | `statutory_group` | **Verified at gate G6** (`MD-035`); a migrated account with no statutory group cannot appear in a statutory report |

> **`FO-03` is the highest-leverage unresolved decision in this workbook.** Rationalising 400–800
> accounts into a governed chart is a finance design exercise with a **W3 minus 3 months** lead
> time. Migrating as-is is a one-week task that imports every legacy compromise permanently.
> `M19` §16.4 states the recommendation plainly — *"a rationalised chart is strongly recommended"* —
> and the decision has not been taken.

### 2.3 Map B — opening trial balance

| Source field | Target | Transform |
|---|---|---|
| Account | `account_id` | Through the `FO-03` cross-reference |
| Debit / Credit | `debit`, `credit` | `05-02` `DM-07` monetary with explicit `currency_id`; **never a float** |
| Entity | `company_id` | → `MD-002`; the chart is per entity (`MD-035`) |
| As-at date | `date` | The cutover instant, `Asia/Dhaka` (`MS-17`) |
| — | `journal_id` | A dedicated **opening-balance journal**, never a normal operational journal |
| — | `ref` | `OPENING-<entity>-<cutover-date>` |
| — | `cost_center_id`, `business_line_id` | `MIGRATION` dimension values (`FO-04`) |
| — | `fix.opening.balance.load` control row | `M19` provides this entity explicitly: `entity_id`, `as_at_date`, `source`, `staged_rows`, `validated_rows`, `rejected_rows`, `reconciliation_doc_id`, `signed_off_by` |

> **`FO-05`.** `FR-FIN-045` — *"Load and prove migrated opening balances, with a reconciliation
> report signed by the CFO before cutover"* — is `P0`. The `fix.opening.balance.load` row is the
> evidence artefact, and `signed_off_by` is not optional.

> **`FO-06` — the journal must balance to zero.** A trial balance that does not balance is not
> loaded with a suspense plug. The difference is investigated and resolved in the source before
> cutover. A migration suspense account is a permanent monument to an unresolved question.

### 2.4 Map C — open receivables and payables

**`FO-07`: open items migrate at open-item level, never as a balance.**

| Source field | Target (`AR` / `AP`) | Rule |
|---|---|---|
| Invoice number | `legacy_document_number` **and** display reference | `M20`: *"every migrated open item must carry its original document number and date"* |
| Invoice date | `invoice_date` | `T-11`; drives ageing. **Ageing is recomputed from the date, never migrated as a bucket** |
| Due date / terms | `date_due` | From `MD-038` payment terms where derivable, else the source date |
| Customer / vendor | `partner_id` | FK into `DM-004`; **reject if unresolved** |
| Original amount | `amount_total` | `05-02` `DM-07`, explicit `BDT` |
| Outstanding amount | `amount_residual` | **Both original and outstanding are required**; outstanding alone loses the payment history context |
| Currency | `currency_id` | Explicit; `MD-039` |
| Tax breakdown | `tax_ids` | Where the source records it; otherwise the item loads **tax-summarised and flagged** — see `FO-11` |
| Dispute flag | `fix.ar.dispute` | `M20` migrates open disputes as their own records |
| Credit notes, unapplied receipts, on-account | `fix.ar.credit.note`, `fix.ar.receipt` | **Unapplied is a state, not a residue** — loaded as unapplied, matched later by the business |
| Deposits and retention | `fix.ar.deposit`, `fix.ap.retention` | Current only |
| Employee advances | `fix.employee.advance` | **Confirmed in writing by each employee before migration**; an unacknowledged advance escalates to HR (`M52`) |

> **`FO-08` — the control-account gate.** The sum of migrated AR open items must equal the
> receivable control account in the opening trial balance **exactly**. Not within tolerance. The
> same for AP. `DM-013` reports it; `DM-003` `SQ-05` places the gate at the tier boundary.

> **`FO-09` — vendor bank details are unverified until called back.** `M52` §16.4: migration is
> *"the single most attractive moment for a payment-redirection fraud"*, and a migrated bank account
> is treated as **unverified until an independent call-back is recorded**. The account loads; the
> payment does not run against it until verification exists.

### 2.5 Map D — treasury, bank and cash

| Target | Source / origin | Rule |
|---|---|---|
| `fix.bank.account`, mandates | `SRC-021` bank portals | W3 minus 2 months; account numbers are **S3** |
| Opening bank balance | **`third_party_confirmed`** — the bank's statement | **Never the legacy book balance** (`M50`) |
| Reconciling items | Bank statement versus book | **Each individually identified and aged**; an aggregate difference is not a reconciling item |
| Branch till and safe balances | **`counted`**, witnessed and signed | 51+ branches |
| Technician floats and rider balances | **`counted`** | 200–400 staff |
| Petty cash imprests | **`counted`** | All locations |
| Unused cheque stock | **`counted`** against the register | Physical count |
| Gateway / MFS clearing balances | **`third_party_confirmed`**, reconstructed from settlement history and **confirmed with the provider in writing** | bKash, Nagad, SSLCOMMERZ |
| Open LCs, guarantees, facilities | Extracted, current only | With `M44` at W6 |

> **`FO-10`.** `G3-09` requires branch cash reconciling daily across all live branches, and `M50`
> targets > 94% reconciliation. Both are unreachable from a book-balance opening position, for the
> identical reason `M15` gives for stock — which `M50` §16.4 states explicitly, citing `M15`.

### 2.6 Map E — tax opening positions

**This is the section with statutory consequence, and it is where `M51` sets absolute constraints.**

| Item | Rule | Consequence of error |
|---|---|---|
| **Mushak 6.3 sequence position** | **`FO-12`** — the sequence **continues without a gap or a reset across cutover**. The cutover number is **agreed with the tax consultant, recorded, and asserted immediately after go-live** | *"The first thing an NBR audit looks for, and it cannot be corrected afterwards"* |
| Opening input VAT credit | **`FO-13`** — agreed to the **last filed Mushak 9.1**, not to a book balance. Any difference is **resolved before cutover, never carried** | An unsupportable input credit claim |
| Tax registrations — BIN, TIN, circle, premises | Loaded per entity from the registration documents | Wrong premises code invalidates the invoice |
| Statutory rate pack | `MD-037`; **fiscal-year pinned**, `verified_by` and `verified_on` required at gate **G6** | A wrong rate produces unlawful invoices at scale |
| Prior-year pack | Loaded as `superseded`, for backdated transactions and comparatives | Backdated corrections use the wrong rate |
| **W3-period VAT register reconstruction** | **`FO-14`** — 3–5 months of `M20`/`M52` transactions posted between W3 go-live and W4 tax go-live must be **reconstructed into the VAT registers**. `M51` names it *"a defined migration task"* | A gap in the VAT register for the company's own live months |
| Open withholding deposits and unissued certificates | Current only | Unissued certificates are a supplier obligation |
| Mushak 6.6 received but unclaimed | Current only | Lost recoverable credit |
| Party tax profile — BIN/TIN, payee type, PSR status | All active parties, via `DM-004` at W4 minus 1 month | Wrong VDS rate applied at source |
| Tax depreciation opening WDV | **`statutory_agreed`** — **must tie to the last filed income-tax return** | Misstated tax position, carried forward |

> **`FO-15` — retention.** VAT records must be preserved for a minimum of **five years** under the
> VAT and SD Act 2012 regime, and the programme's own retention schedule (BRD §11.7) sets **seven
> years** for VAT and financial records. **Seven exceeds five; both are satisfied by applying
> seven.** Migrated statutory documents inherit the seven-year class on capture (`M24`), and
> `NFR-088` enforces retention in the system rather than by policy.

### 2.7 Map F — fixed assets, revenue and budget

| Target | Origin | Rule | Wave |
|---|---|---|:--:|
| `fix.asset.book` (accounting) | **`counted`** then valued | Opening cost and accumulated depreciation **must reconcile to `M19`**. Assets found and not on the list are registered at **CFO- and auditor-approved deemed cost**; listed assets not found are **written off before cutover with approval**, never carried as an unexplained balance | W5 |
| `fix.asset.book` (tax) | **`statutory_agreed`** | Opening written-down values **agreed with the tax consultant** and tied to the last filed return | W5 |
| `fix.asset.cwip` | Extracted | Open capital projects | W5 |
| `fix.contract.liability` — deferred revenue | **Rebuilt** | **`FO-16`** — *"rebuilt from the underlying contracts, obligation by obligation — not loaded as a total."* Where the legacy records cannot support the reconstruction, the difference is quantified and **written off under CFO and external-auditor approval before cutover** | W4 |
| `fix.commission.ledger` | Extracted | Open partner and referral balances, current only | W4 |
| `fix.budget` | Extracted | **Current-year budget as an approved locked version**, so variance measurement begins immediately | W6 |
| `fix.cost_center`, `fix.cost.element` | Authored | 60–120 centres; **allocation cycles are designed, not migrated** (`M54`) | W6 minus 2 months |

### 2.8 Historical financial data

| Population | Disposition | Target |
|---|---|---|
| Prior-year comparatives, summary level | `M` live | Comparative journals, 1–2 years — **depth unresolved, `M19` `Q-06`** |
| Historical AR and AP invoices, 2 years | **`A` archive** | **Warehouse (`M62`) only — explicitly not the operational ledger** |
| Historical bank statements, 1–2 years | `A` archive | Warehouse only, best-effort |
| Historical ageing | **`L` leave** | Not migrated; ageing is recomputed from document dates |
| 51+ branch spreadsheets | **`L` leave** | Retained as reference documents in `M24` |
| Historical disposals, 2 years | `A` archive | Warehouse only |
| Exchange-rate history, 2 years | `M` live | `fix.currency.rate` |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key — open items | Original document number + entity + partner |
| Natural key — GL | Account code + entity (`MD-035`) |
| Surrogate key | System-generated move and line ids |
| Legacy key | `legacy_source_system` + `legacy_record_id` on every posting and open item (`MS-18`, BRD `MIG-010`) |
| **Statutory sequences** | Migrated documents **never** consume a `MD-040` `is_statutory` sequence (`SH-11`). The Mushak sequence is asserted to its cutover position and continues forward only |
| Reuse policy | Never reused; a reversed migration posting keeps its id and carries a reversal entry |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `FO-01` | Every finance figure carries an `origin` and the signature that origin requires | **H** | `ERR-FIN-001` |
| `FO-02` | No finance figure loads with `origin = extracted`; the export is an input to the trial balance, not the balance | **H** | `ERR-FIN-002` |
| `FO-03` | The chart-of-accounts rationalisation decision must be recorded before the CoA load | **H** | `ERR-FIN-003` |
| `FO-04` | Migrated postings take `MIGRATION` dimension values; a dimension is never guessed | **H** | `ERR-FIN-004` |
| `FO-05` | A `fix.opening.balance.load` control row with `signed_off_by` exists before the opening journal posts | **H** | `ERR-FIN-005` |
| `FO-06` | The opening journal balances to zero; no suspense plug is permitted | **H** | `ERR-FIN-006` |
| `FO-07` | Open items load at document level; a balance total is rejected | **H** | `ERR-FIN-007` |
| `FO-08` | Migrated open-item totals equal their control account **exactly**, both AR and AP | **H** | `ERR-FIN-008` |
| `FO-09` | A migrated vendor bank account is `unverified` until an independent call-back is recorded; no payment runs against it | **H** | `ERR-FIN-009` |
| `FO-10` | Cash and bank opening positions load only from a witnessed count or the counterparty's own statement | **H** | `ERR-FIN-010` |
| `FO-11` | An open item with no tax breakdown loads tax-summarised **and flagged**; it is never assigned a guessed tax code | **H** | `ERR-FIN-011` |
| `FO-12` | The Mushak 6.3 sequence continues without gap or reset; the cutover position is agreed, recorded and asserted | **H** | `ERR-FIN-012` |
| `FO-13` | Opening input VAT credit ties to the last filed Mushak 9.1; a difference blocks cutover | **H** | `ERR-FIN-013` |
| `FO-14` | The W3-period VAT register reconstruction is completed before the W4 tax go-live | **H** | `ERR-FIN-014` |
| `FO-15` | Migrated statutory documents inherit the seven-year retention class on capture (`NFR-088`) | **H** | `ERR-FIN-015` |
| `FO-16` | Deferred revenue is rebuilt obligation by obligation; a total is rejected | **H** | `ERR-FIN-016` |
| `FO-17` | Fixed-asset opening values load only after physical verification; unfound assets are written off with approval before cutover | **H** | `ERR-FIN-017` |
| `FO-18` | The W2 stock value frozen by `DM-007` `IV-08` appears unchanged as the stock control account | **H** | `ERR-FIN-018` |
| `FO-19` | Monetary values carry an explicit currency and are never floats (`05-02` `DM-07`) | **H** | `ERR-FIN-019` |
| `FO-20` | Ageing is recomputed from document dates; migrated ageing buckets are rejected | **H** | `ERR-FIN-020` |
| `FO-21` | Historical invoices load to the warehouse only, never to the operational ledger | **H** | `ERR-FIN-021` |
| `FO-22` | Every loaded row carries the three control values (`MS-18`) | **H** | `ERR-FIN-022` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `MD-035` chart of accounts, `MD-036` dimensions | N:1 | Seed tiers 1 and 4, **before everything** |
| `MD-037` tax codes, `MD-038` payment methods and banks, `MD-039` currency, `MD-040` sequences | N:1 | Seed tier 4, before |
| `DM-004` party | N:1 | Tier `X1` — every open item needs its partner |
| `DM-007` inventory | N:1 | **`IV-08` frozen stock value feeds the stock control account** |
| `DM-010` contracts | N:1 | **`FO-16` deferred revenue is rebuilt from contracts**, so contracts precede revenue |
| `DM-005` asset | N:1 | Physical verification precedes fixed-asset valuation |
| The signed trial balance | 1:1 | **Nothing loads before it exists** |

| Depended on by |
|---|
| `DM-009` payroll GL posting accounts · every `M51` statutory return · `G3-04`, `G3-05`, `G3-08`, `G3-09` · `RP-009` statutory report formats · the parallel month-end close |

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | `SRC-004` accounting software · `SRC-021` bank portals · `SRC-020` gateway portals · `SRC-016` AP records · `SRC-017` fixed-asset spreadsheets · `SRC-043` NBR statutory pack · **witnessed counts** |
| Who supplies it | Financial Controller, under the CFO |
| Collection method | Database extract → **reconciled into a signed trial balance**; third-party statements; witnessed physical counts |
| Known quality issues | No dimensional history; 400–800 accounts of unknown rationality; branch spreadsheets consolidated manually with a 15–20 day close; ageing not maintained; tax registers maintained outside the accounting system |
| Cleansing rules applied | `DM-011` |
| Re-verification | **One full parallel month-end close**, reconciled line by line and signed, before the legacy system is retired (`M19`) |

---

## 7. Volumes

| Population | Rows | Origin | Wave |
|---|---:|---|:--:|
| Chart of accounts | 400–800 | Extracted → rationalised | W3 minus 2 months |
| Opening trial balance | 1 balanced set per entity | `trial_balance` | W3 |
| Prior-year comparatives | 1–2 years, summary | `trial_balance` | W3 |
| **Open customer invoices** | **8,000–15,000 open items** | `open_item` | W3 |
| Open vendor invoices | 800–2,000 open items | `open_item` | W3 |
| Bank accounts and mandates | 12–25 | `third_party_confirmed` | W3 |
| Branch cash positions | 51+ | `counted` | W3 |
| Technician and rider floats | 200–400 | `counted` | W3 |
| Fixed assets | 8,000–20,000 | `counted` → valued | W5 |
| Historical financial records | **1,000,000+** *(`05-02` §12)* | Archive → warehouse | W3–W4 |
| Current-year budget | All cost centres | Extracted | W6 |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add a mapping row | Migration analyst |
| Who may set `business_confirmed` | Financial Controller |
| Who may set `signed_off` | **CFO**, with the external auditor's agreement on the trial balance and the tax consultant's on `statutory_agreed` items |
| Approval required | CFO for every write-off, deemed cost and rationalisation decision; Tax Manager with the tax consultant for every `M51` item |
| Effective dating | Statutory rates are fiscal-year pinned (`CG-006` §5); the mapping is not effective-dated |
| Archive rule | Records archived (`active = FALSE`), never deleted (`05-02` `DM-06`) |
| Logged in | `RF-006`; the reconciliation is retained as an `M24` document for seven years (`FO-15`) |

---

## 9. Sample rows

```csv
map_id,source_id,source_field,source_type,source_example,target_entity,target_field,transform_rule,default_value,required_at_target,sensitivity,residency_restricted,dq_rule,unmapped_disposition,owner,status
FMAP-000501,SRC-004,Account Code,text,4010,fix.gl.account,account_code,FO-03 map through the rationalisation cross-reference; the legacy code is retained permanently,,TRUE,S1,FALSE,DQ-FIN-001,,Financial Controller,proposed
FMAP-000506,TB,Debit,decimal,1284500.00,account.move.line,debit,05-02 DM-07 monetary with explicit BDT currency_id; never a float,,TRUE,S2,FALSE,DQ-FIN-006,,CFO,proposed
FMAP-000512,SRC-004,Customer Balance,decimal,84200.00,,,FO-07 balance totals are rejected; open items load at document level only,,FALSE,S2,FALSE,,escalated,Financial Controller,proposed
FMAP-000518,SRC-004,Invoice No,text,INV-2025-004182,fix.ar.open.item,legacy_document_number,Verbatim; retained and displayed so the customer can identify the item,,TRUE,S1,FALSE,DQ-FIN-018,,Financial Controller,proposed
FMAP-000524,SRC-016,Vendor Bank A/C,text,MASKED,res.partner.bank,acc_number,FO-09 loads as unverified; no payment runs until an independent call-back is recorded,,FALSE,S3,FALSE,DQ-FIN-024,,CFO,proposed
FMAP-000531,SRC-043,Mushak 6.3 last serial,text,DHK-001-2026-004417,fix.mushak.sequence,current_value,FO-12 asserted to the agreed cutover position; no gap and no reset,,TRUE,S1,FALSE,DQ-FIN-031,,Tax Manager,proposed
```

---

## 10. Migration notes

**Four Gate 3 criteria and one Gate 4 dependency run through this workbook.**

| Gate | Criterion | Served by |
|---|---|---|
| `G3-04` | Mushak invoices accepted with **zero NBR exceptions** | `FO-12`, `FO-13`, `MD-037` G6 verification |
| `G3-05` | First full month-end closed within 5 days | The parallel close, and `FO-06`/`FO-08` leaving nothing unexplained |
| `G3-08` | Financial history migrated and **reconciled to the trial balance** | `FO-05`, `FO-08`, `FO-18` |
| `G3-09` | Branch cash reconciling daily | `FO-10` |
| `G4` | Contract and warranty engine live | `FO-16` deferred revenue, rebuilt from `DM-010` contracts |

**The parallel close is the real acceptance test.** `M19` §16.4 requires *one full parallel
month-end close* run in the legacy system and in `M19`, reconciled line by line and signed, before
the legacy system is retired. `05-02` §12 `MIG-07` requires a **two-week parallel run** on service
orders and finance. Neither is a testing activity — both are finance-team effort, in addition to
running a normal close, and neither appears in the `06-01` resourcing plan.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.md) | The target chart and its control-account semantics |
| [`../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | Rates, Mushak forms and the G6 verification requirement |
| [`../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-040_Document_Sequence_and_Numbering_Mask_Register.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-040_Document_Sequence_and_Numbering_Mask_Register.md) | `is_statutory`, `gap_policy = no_gaps`, and the sequence `FO-12` asserts |
| [`DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md`](DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md) | The frozen stock value `FO-18` requires |
| [`DM-010_Field_Mapping_Workbook_Contracts_Warranty_and_Claims.md`](DM-010_Field_Mapping_Workbook_Contracts_Warranty_and_Claims.md) | The contracts `FO-16` rebuilds deferred revenue from |
| [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) | The reconciliation the CFO signs |
| `M19` §16.4 · `M20` §16.4 · `M50` §16.4 · `M51` §16.4 · `M52` §16.4 · `M49` §16.4 · `M53` §16.4 | The migration positions implemented here |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Five finance origins with distinct signatories, open-item-level rule, suspense plug prohibited, exact control-account gate, Mushak sequence continuity, vendor bank call-back, deferred revenue rebuilt not loaded, stock-value freeze honoured | CFO (pending) |

---

## 13. Open items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **`M19` `Q-02` unresolved** — rationalise the chart of accounts before migration, or migrate as-is. `FO-03` blocks the CoA load until it is recorded, and rationalisation carries a **three-month** lead time. Defaulting by omission imports every legacy compromise permanently | CFO | **W3 minus 3 months** |
| **`O-02`** | **`M19` `Q-06` unresolved** — how many comparative years are required for statutory and board reporting. Volume, effort and the archive/live boundary all depend on it | CFO | **W3 minus 2 months** |
| **`O-03`** | **The Mushak 6.3 cutover sequence position has no agreed process.** `FO-12` requires it agreed with the tax consultant, recorded and asserted immediately after go-live; no owner, no procedure and no rehearsal exists, and the error is uncorrectable | Tax Manager with the tax consultant | **W4 cutover — rehearsed at W3** |
| **`O-04`** | **The parallel month-end close and the two-week parallel run are unresourced.** Both are mandatory (`M19` §16.4, `05-02` §12 `MIG-07`) and both are finance-team effort on top of a normal close. Neither appears in `06-01` | CFO with Programme Director | **W3 minus 2 months** |
| **`O-05`** | **Top-50 customer balance confirmations have no process.** `M20` requires each confirmed **in writing** before cutover; obtaining fifty written confirmations is weeks of account-management effort with no owner | Financial Controller with CCO | **W3 minus 1 month** |
| **`O-06`** | **The `MD-037` G6 external verification has not been performed.** Every rate carries `verified_by` and `verified_on` as G6 evidence; the tax adviser has not been engaged, and an unverified rate produces unlawful invoices at scale from `G3-04` | CFO with Tax Manager | **W3** |
| **`O-07`** | **The W3-period VAT register reconstruction (`FO-14`) is scoped but unowned.** Three to five months of live `M20`/`M52` transactions must be reconstructed into `M51` registers at W4; the effort has not been estimated | Tax Manager | **W4** |
| **`O-08`** | The register places this file at **W1** while every finance load is **W3–W6**. The build/load distinction is recorded in §1 per `MS-22`; the register row should carry the same clarification so a delivery planner does not read W1 as a load date | Programme Content Lead | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; mapping column set inherited from `DM-004` §2.1 (`CP-01`)
- [x] Five finance origins defined, each with its own signatory, and `extracted` prohibited as an origin
- [x] **Open-item-level rule implemented literally** (`FO-07`), with both original and outstanding amounts required
- [x] **Suspense plug prohibited** (`FO-06`) and the exact control-account gate stated (`FO-08`)
- [x] Dimensional gap handled by a `MIGRATION` dimension rather than a guess (`FO-04`)
- [x] **Mushak 6.3 sequence continuity made a hard rule** with the uncorrectable consequence stated
- [x] Opening input VAT credit tied to the last filed Mushak 9.1, not to a book balance
- [x] W3-period VAT register reconstruction carried as a named migration task
- [x] Vendor bank details loaded as unverified pending independent call-back (`FO-09`)
- [x] Deferred revenue rebuilt obligation by obligation, with the write-off path approved rather than absorbed
- [x] Fixed-asset opening values gated on physical verification, with deemed cost and write-off both approved
- [x] Cross-workbook stock value freeze honoured (`FO-18` ↔ `DM-007` `IV-08`)
- [x] Retention reconciled — statutory five-year minimum versus the programme's seven-year class, with the stricter applied
- [x] Ageing recomputed rather than migrated (`FO-20`)
- [x] Sample rows included and parse as CSV
- [x] Archive rule states records are archived, never deleted (`05-02` `DM-06`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] **`O-01` chart-of-accounts decision unresolved — `FO-03` blocks the load**
- [ ] **`O-03` Mushak sequence cutover has no owner and the error is uncorrectable**
- [ ] **`O-04` parallel close unresourced**
- [ ] **`O-06` `MD-037` G6 verification not performed**
- [ ] Named approver recorded — **pending CFO**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
