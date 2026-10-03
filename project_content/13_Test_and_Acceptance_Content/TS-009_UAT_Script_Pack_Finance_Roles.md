---
id: TS-009
title: UAT Script Pack — Finance Roles
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance with QA Lead
author: QA Lead with Finance Manager, tax function and Content Design
reviewers: [CFO, Finance Manager, Finance Officer representatives, Cashier representatives, Tax adviser, Localisation Lead, Quality Manager]
approver: CFO with QA Lead
content_class: E
purpose: >
  The acceptance scripts executed by the finance function itself, including verification of every
  statutory output the company issues in Bangladesh. Mushak correctness is not a developer's
  judgement and it is not QA's: a Mushak 6.3 challan that does not comply is an unlawful invoice, and
  a Mushak 9.1 return derived from a register the finance team has not tied out is a filing the CFO
  signs on trust. Gate 3 requires Mushak invoices accepted with zero NBR exceptions — that is a
  claim about a regulator's behaviour, and only the function that files can make it.
traces_to: [M19, M20, M49, M50, M51, M52, M53, M54, 05-04, 05-04 §7, 05-05, 05-06 §6, 05-06 §8, 06-02 §4, MD-035, MD-036, MD-037, MD-038, MD-039, MD-040, MD-041, SP-019, SP-020, DT-010, DT-011, DT-012, DT-013, DT-014, DT-015, DT-016, DT-017, DT-018, DT-019, DT-020, TR-014, UI-029, BN-015, TS-001, TS-002, TS-004, TS-006, TS-012, TS-018, DM-008]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: TS-009_UAT_Script_Pack_Finance_Roles_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §6.1 statutory currency table (VAT and Supplementary Duty Act 2012 in force, verified 2026-08-12), §6.2 NFR-021 Mushak 6.3 compliance, NFR-022 NBR income tax, NFR-100 Mushak 9.1 filed by the 15th through vat.gov.bd, NFR-101 input credit only against a valid Mushak 6.3; §8 DI-01 decimal arithmetic in money paths
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §1.1 R03 CFO, §1.5 R26 2–4, R27 10–20, R29 51+; §3.4 Pillar D permission matrix; §5 field-level permissions on salary, bank_account, nid_number, customer_credit_limit; §6 SOD-01, SOD-04, SOD-12; §7 credit-note and write-off bands
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 1 G1-05; Gate 3 G3-01…G3-09 including G3-04 Mushak accepted with zero NBR exceptions, G3-05 first month-end closed within 5 days, G3-08 financial history reconciled to the trial balance; §2.7 KPI-050…058
    verified: 2026-08-19
    class: P1
  - source: project_content/05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md §337 — the document-sequence rule in MD-040 is tested explicitly in TS-009; and §359 which names this pack as where Mushak correctness is proven by Finance
    verified: 2026-08-19
    class: P1
  - source: Mushak 6.3 is the official tax invoice prescribed under Rule 40(1) of the VAT and SD Rules 2016 and must carry the name, address and BIN of both supplier and buyer, a unique invoice number, the date and time of issue, line description, quantity, unit price, value, VAT, supplementary duty and total payable. https://rakibhassan.eu/mushak-6-3-vat-invoice-bangladesh/ and https://taxsummaries.pwc.com/bangladesh/corporate/other-taxes
    verified: 2026-08-19
    class: P2
supersedes: none
review_due: 2027-02-19
---

# UAT Script Pack — Finance Roles

| Item | Value |
|---|---|
| Test level | **UAT** — method in [`TS-006`](TS-006_UAT_Script_Pack_Service_Operations_Roles.md) §2.1 and §3.2 |
| Roles executing | `R03` `R26` `R27` `R29` — **4 roles, 63–75 people** |
| Modules covered | `M19` `M20` `M49` `M50` `M51` `M52` `M53` `M54` |
| Portals covered | `P03` Finance Console (`UI-029`), `P06` |
| Environment | `UAT` — frozen for the cycle |
| Test data set | `TS-002` — sets `M-01`…`M-08`; persona 1, 4, 5 |
| Wave | W1 · `P0` — `G1-05` and the whole of `G3` depend on it |

> **Template conformance.** As `TS-006`: `TPL_Test_Script.md` at pack level, all six sections
> retained in order with pack-level interpretation.

> **Method by reference.** `UA-01`…`UA-18` (`TS-006` §2.1), `UA-19`–`UA-20` (`TS-007` §2.1) and
> `UA-24` (`TS-008` §2.1) apply. This pack adds `UA-27`…`UA-31` (§2.1), which exist because a
> statutory output has an external judge.

---

## 1. Traceability

### 1.1 The three things only finance can verify

`TS-004` §3.3 already proves at SIT that the Mushak challan renders every field the specification
lists and that the return derives from the registers. **That is not the same as compliance.** Three
judgements are outside QA's competence and outside the specification:

| Judgement | Why only finance can make it |
|---|---|
| **Is this output compliant?** | Compliance is against the VAT and SD Act 2012 and Rule 40(1) of the VAT and SD Rules 2016, not against `DT-010`. `DT-010` is our reading of the rule; finance and the tax adviser own the reading |
| **Will the NBR accept it?** | `G3-04` requires *"Mushak invoices accepted with zero NBR exceptions"*. Acceptance is an event at `vat.gov.bd`, not a test result |
| **Does the ledger say what happened?** | A posting can be correct against `MD-035` and wrong against the business. Only the person who signs the accounts can say which |

**`UA-27` follows from this**: a statutory script's expected result is stated by the finance
function, in advance, in its own words — and where the reading of the instrument is uncertain, the
script is blocked, not guessed (`CG-013` legal escalation).

### 1.2 Traceability obligation

Per `TS-006` §1.2, `TS-007` `UA-20` and `TS-004` §1.2, with three required columns:

| Field | Source |
|---|---|
| **Statutory instrument** | The Act, rule or NBR instruction the script verifies, with a verification date (`CG-012`, `CM-R8`) |
| **Expected journal** | Accounts and amounts from `MD-035`/`MD-036`, stated before execution (`SL-17`) |
| **Document template** | The `DT` file whose rendered output the script inspects |

### 1.3 Role coverage

| Role | Headcount | Scripts | `P0` | Language | Scope | SOP | Course pack |
|---|---:|---:|---:|---|---|---|---|
| `R26` Finance Manager | 2–4 | **16** | 10 | English | all entities | `SP-019`, `SP-020` | `TR-014` |
| `R27` Finance Officer | 10–20 | 14 | 8 | English | assigned scope | `SP-019`, `SP-020` | `TR-014` |
| `R29` Cashier / Counter Finance | **51+** | 10 | 6 | **Bengali** | own counter and shift | `SP-019` | **none — `O-05`** |
| `R03` CFO | 1 | 6 | 4 | English | all entities | `SP-020` | **none — `O-05`** |
| **Total** | **63–75** | **46** | **28** | | | | |

**`R29` is why this pack is bilingual.** Fifty-one-plus cashiers work the counter in Bengali, hand
over the Mushak challan and the money receipt, and are the last human between the system and the
customer's proof of payment. `CG-010` §3.3's test is met by them alone.

---

## 2. Preconditions

### 2.1 Additional rules for statutory and financial scripts

| # | Rule |
|---|---|
| **UA-27** | **The finance function states the expected result of a statutory script in its own words, in advance.** Where the reading of the instrument is uncertain, the script is blocked and escalated under `CG-013`, never executed on an assumed reading |
| **UA-28** | Statutory output is verified **on the rendered artefact** — the printed or PDF challan, register or return — not on a screen field. A field that is correct in the form and absent from the print is a compliance defect |
| **UA-29** | Every statutory script records the **instrument and the verification date** of the reading it tests, so a Finance Act change re-opens it automatically (`CG-006` §5 statutory pinning) |
| **UA-30** | **Numbers are tied out, not inspected.** Every register, return and reconciliation script states a control total and asserts it (`SL-20`); a visual check is recorded as a visual check and does not satisfy exit |
| **UA-31** | Statutory-output evidence is filed as a **compliance record** through `M24`, not as a test artefact, and is retained per `TS-001` §4.6 `EV-04` |

### 2.2 Additional preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | `TS-006` preconditions 1–4, 7, 9; `TS-004` preconditions 2–6 met | Exit records |
| 2 | Company BIN configured as the **13-digit e-BIN**; a buyer BIN present for a B2B case | `NFR-021`; `TS-002` §4.6 |
| 3 | `MD-037` tax codes covering standard-rated, exempt, zero-rated and supplementary-duty lines | `TS-002` `M-02` |
| 4 | `MD-040` document sequences configured for every statutory document, with **no reuse and no gap** | `DT-010` §337 |
| 5 | `MD-041` fiscal calendar open on a July–June year, with a period available to close | `G3-05` |
| 6 | Opening balances loaded and **tied to a signed trial balance** | `G3-08`; `DM-008` — **unwritten**, `O-04` |
| 7 | Payment gateways in sandbox: bKash, Nagad, card, bank transfer, with failure, timeout and duplicate-callback triggers | `TS-002` `M-05` |
| 8 | A bank statement in the production format with two unmatchable lines | `AUT-044` |
| 9 | Thermal receipt printer and A4 printer, with Bengali rendering verified on both | `05-06` §10; `UA-28` |
| 10 | Two distinct accounts per SoD rule (`SOD-01`, `SOD-04`, `SOD-12`) | `TS-002` `O-04` |
| 11 | **The tax adviser available to confirm readings** under `UA-27` | `O-01` |

---

## 3. Scripts

### 3.1 Block A — `R26` Finance Manager · 16 scripts

`SP-019`, `SP-020` · `TR-014` · all entities

| Script | The job | Instrument / rules | Pri |
|---|---|---|:--:|
| `UAT-R26-001` | **Inspect a rendered Mushak 6.3 challan and confirm every mandatory field is present and correct** — supplier and buyer name, address and BIN, unique number, date and time of issue, line description, quantity, unit price, value, VAT, supplementary duty, total payable | VAT and SD Act 2012; Rule 40(1) VAT and SD Rules 2016; `DT-010`; `UA-27` `UA-28` | **P0** |
| `UAT-R26-002` | Confirm the challan sequence is unique, unbroken and non-reusable across a day's issuing | `MD-040`; `DT-010` §337 | **P0** |
| `UAT-R26-003` | **Tie the sales register (Mushak 6.2) to the ledger and to the challans issued** | `DT-011`; `UA-30` | **P0** |
| `UAT-R26-004` | **Tie the purchase register (Mushak 6.1) to vendor invoices and confirm input credit is claimed only against valid Mushak 6.3** | `NFR-101`; `DT-012`; `UA-30` | **P0** |
| `UAT-R26-005` | **Derive the Mushak 9.1 return with no manual adjustment and tie it to both registers** | `NFR-100`; `DT-014`; `UA-30` | **P0** |
| `UAT-R26-006` | Issue a VDS certificate (Mushak 6.6) and confirm the deduction matches the vendor payment | `DT-013`; `BRU-FIN-09`(H) | **P0** |
| `UAT-R26-007` | **Close a financial period and be refused while unposted entries exist** | `BRU-FIN-05`(H) | **P0** |
| `UAT-R26-008` | Run the month-end close checklist to completion and measure the elapsed days | `AUT-043`; `G3-05` ≤ 5 days; `KPI-050` | **P0** |
| `UAT-R26-009` | Approve a credit note above `BDT 10,000`, and **be refused approving one you created** | `BRU-FIN-04`(H) `SOD-04`; `05-04` §7 | **P0** |
| `UAT-R26-010` | Confirm every invoice was generated automatically on job closure, and that a manual one for a completed job required approval | `BRU-BIL-01`(C/A); `G3-01` 100%; `KPI-053` | **P0** |
| `UAT-R26-011` | Review the bank reconciliation and confirm the auto-match rate, with only exceptions presented | `AUT-044`; `G3-02` ≥ 90%; `KPI-051` | P1 |
| `UAT-R26-012` | Confirm a consolidated corporate invoice cannot issue until every constituent job is completed and priced | `BRU-BIL-07`(H); `DT-020`; `G4-08` | P1 |
| `UAT-R26-013` | Confirm foreign-currency balances revalued at period end at the official rate | `BRU-FIN-07`(C); `MD-039` | P1 |
| `UAT-R26-014` | Confirm deferred revenue released only on schedule, and that a manual release needed CFO approval | `BRU-BIL-06`(H) | P1 |
| `UAT-R26-015` | **Try to create a vendor and then approve that vendor's invoice, and be refused** | `BRU-SCM-03`(H) `SOD-01` | P1 |
| `UAT-R26-016` | Confirm days-sales-outstanding and revenue-leakage figures for the period against source records | `KPI-052`, `KPI-056`; `UA-19` `SL-26` | P2 |

### 3.2 Block B — `R27` Finance Officer · 14 scripts

`SP-019`, `SP-020` · `TR-014` · assigned scope only

| Script | The job | Instrument / rules | Pri |
|---|---|---|:--:|
| `UAT-R27-001` | Issue an invoice and confirm VAT at the applicable rate with the Company BIN displayed | `BRU-FIN-01`(H); `NFR-021` | **P0** |
| `UAT-R27-002` | Issue an invoice with mixed standard, exempt and zero-rated lines and confirm each line's treatment | `MD-037`; `TS-002` `M-02`; `UA-19` | **P0** |
| `UAT-R27-003` | Record a payment and confirm it matched, marked paid, posted and receipted | `AUT-024`; `DT-016` | **P0** |
| `UAT-R27-004` | **Try to record a payment against a cancelled invoice, and be refused** | `BRU-FIN-03`(H) | **P0** |
| `UAT-R27-005` | Raise a credit note up to `BDT 10,000` and confirm the reversal journal is exact | `05-04` §7; `DT-015`; `SL-17` | **P0** |
| `UAT-R27-006` | **Try to approve your own credit note, and be refused** | `SOD-04` | **P0** |
| `UAT-R27-007` | Handle a refund to the original payment method, and store credit where the customer accepts it | `BRU-BIL-05`(C) | **P0** |
| `UAT-R27-008` | Confirm a duplicate gateway callback produced one receipt and one posting | `DI-05`; `TS-002` `M-05` | **P0** |
| `UAT-R27-009` | Work the dunning series at 7/14/21/30 days and enter collections at 30 | `AUT-023`; `DT-018` | P1 |
| `UAT-R27-010` | Issue a customer statement of account that the customer can reconcile | `DT-017`; `UA-30` | P1 |
| `UAT-R27-011` | Issue a proforma invoice and an advance request, and confirm neither is a tax invoice | `DT-019`; `NFR-021` | P1 |
| `UAT-R27-012` | Confirm a subscription cycle billed with proration and usage, and that a missed cycle raised an exception rather than a silent skip | `BRU-BIL-02`(H) `AUT-025` | P1 |
| `UAT-R27-013` | **Try to see or act outside your assigned scope, and be refused** | `05-04` §3.4 `(scope)` | P1 |
| `UAT-R27-014` | Confirm you cannot see `salary`, `bank_account` beyond your grant, or `customer_credit_limit` outside the permitted set | `05-04` §5 | P2 |

### 3.3 Block C — `R29` Cashier / Counter Finance · 10 scripts

`SP-019` · **Bengali** · 51+ people · own counter and shift only · **no course pack** — `O-05`

| Script | The job | Instrument / rules | Pri |
|---|---|---|:--:|
| `UAT-R29-001` | Take a counter payment and **hand over a Mushak 6.3 challan the customer can read, in Bengali** | `NFR-021`; `DT-010`; `BN-015`; `UA-09` `UA-28` | **P0** |
| `UAT-R29-002` | Issue a money receipt on the thermal printer, in Bengali, and confirm it prints legibly | `DT-016`; `05-06` §10; `UA-28` | **P0** |
| `UAT-R29-003` | **Take a cash receipt above `BDT 50,000` and be required to record the customer's NID** | `BRU-FIN-02`(H); `TS-002` `M-01` | **P0** |
| `UAT-R29-004` | Confirm the amount shows as `12,34,567` in Bengali and `1,234,567` in English — the same value | `05-06` §9; `TS-002` `M-04` | **P0** |
| `UAT-R29-005` | Close your shift, reconcile the cash, and confirm the variance is zero or explained | `BRU-FIN-10`(H); `SP-019` | **P0** |
| `UAT-R29-006` | **Try to open a shift with the previous one unclosed, and be refused** | `BRU-FIN-10`(H) | **P0** |
| `UAT-R29-007` | **Try to reconcile the cash book for cash you handled, and be refused** | `SOD-12` | P1 |
| `UAT-R29-008` | Take a bKash and a Nagad payment at the counter and confirm both reconcile | `NFR-042`; `G3-03` | P1 |
| `UAT-R29-009` | Handle a failed payment at the counter without losing the transaction | `NFR-050`; `PS-09` | P1 |
| `UAT-R29-010` | **Try to see another counter's or another shift's cash, and be refused** | `05-04` §3.4 `(own shift)` | P1 |

### 3.4 Block D — `R03` CFO · 6 scripts

`SP-020` · **no course pack** — `O-05`

| Script | The job | Instrument / rules | Pri |
|---|---|---|:--:|
| `UAT-R03-001` | **Sign the Mushak 9.1 return, having tied it out yourself** | `NFR-100`; `UA-27` `UA-30`; `KPI-057` | **P0** |
| `UAT-R03-002` | **Reopen a hard-closed period and confirm the reopening is logged** | `BRU-FIN-06`(H) | **P0** |
| `UAT-R03-003` | Confirm the financial history migrated ties exactly to the trial balance | `G3-08`; `UA-30`; `DM-008` | **P0** |
| `UAT-R03-004` | Approve payroll jointly with the HR Manager, and **be refused approving it alone** | `BRU-HRM-06`(H) `SOD-03`; `TS-010` | **P0** |
| `UAT-R03-005` | Approve an SoD exception, time-boxed, and see it on the standing exception report | `BRU-SEC-07`(H); `05-04` §6 | P1 |
| `UAT-R03-006` | Confirm the declared marketplace principal-or-agent accounting model and that it does not vary by transaction | `BRU-FIN-08`(H); `G7-05` | P1 |

**Pack total: 46 scripts · 28 at `P0` · 15 at `P1` · 3 at `P2`.**

### 3.5 Negative and edge cases

| # | Condition | Expected system behaviour |
|---|---|---|
| N-01 | Challan issued, then the job is reopened as rework | Challan not altered; a credit note or adjustment with a full audit trail (`BRU-SRM-19`) |
| N-02 | VAT rate changes with in-flight orders | The rate at the tax point applies, not the current rate (`CG-006` §5) |
| N-03 | Two cashiers receipt the same invoice simultaneously | One receipt; the second is told it is paid, not given a duplicate |
| N-04 | Sequence generator restarts or is reset | **Blocked**; a reused statutory sequence is a compliance defect (`MD-040`) |
| N-05 | Challan printed to a printer that cannot render Bengali | Detected before issue, not discovered by the customer (`05-06` §10) |
| N-06 | Rounding remainder on a multi-line invoice | Allocated per `MD-039`; total unchanged to the paisa; **no floating-point comparison anywhere** (`DI-01`, `SL-21`) |
| N-07 | Payment received in a closed period | Held with a stated reason; never posted into a closed period (`BRU-FIN-06`) |
| N-08 | Bank statement re-imported | Idempotent; no duplicate matches (`DI-05`) |
| N-09 | Buyer BIN absent on a B2B sale | Blocked or flagged per the finance function's reading of Rule 40(1) — **`UA-27` applies; this is one of the readings `O-01` must confirm** |
| N-10 | Credit note that would take an invoice negative | Refused; a refund path used instead |

### 3.6 Bilingual check

**Bilingual pack.** Bengali is the execution language for `R29` — 51+ of the 63–75 people in scope.
All `R29` scripts and every statutory artefact a customer receives are verified in both languages.

| Element | EN correct | BN correct | Truncation |
|---|:--:|:--:|:--:|
| **Mushak 6.3 challan as printed** (`DT-010`, `BN-015`) | ● | ● | **● — a truncated statutory field is a compliance defect** |
| Money receipt on the thermal printer (`DT-016`) | ● | ● | ● |
| Customer statement of account (`DT-017`) | ● | ● | ● |
| Finance Console labels for `R29` paths (`UI-029`) | ● | ● | ● at 1366×768 |
| Amount grouping — `12,34,567` versus `1,234,567` (`05-06` §9) | ● | ● | ● |
| Bengali month names and DD/MM/YYYY on statutory documents (`MD-041`) | ● | ● | ● |
| Validation and error messages on payment paths (`UI-004`) | ● | ● | ● |

---

## 4. Exit Criteria

`TS-006` §4 applies. Additional, and this pack's are the strictest in Category 13:

| Criterion | Threshold |
|---|---|
| `P0` scripts passed | **100% — no tolerance, no deferral** |
| `P1` scripts passed | ≥ 98% |
| Statutory scripts with a finance-stated expected result agreed in advance | **100%** (`UA-27`) |
| Statutory scripts verified on the **rendered artefact** | 100% (`UA-28`) |
| Statutory scripts recording instrument and verification date | 100% (`UA-29`) |
| Control totals stated and asserted | 100% of register, return and reconciliation scripts (`UA-30`) |
| **`G3-04` Mushak accepted by the NBR** | **Zero exceptions** — and see `O-02`: this cannot be evidenced in `UAT` |
| **`G3-05` first month-end close** | **Within 5 days** |
| **`G3-08` financial history tied to trial balance** | **Exact** |
| `G3-01` invoices generated automatically | 100% |
| `G3-02` payment auto-match | ≥ 90% |
| SoD refusals (`SOD-01`, `SOD-04`, `SOD-12`) | 3 of 3 blocked with distinct users |
| Bengali verification of every customer-facing statutory artefact | **100%** |
| Open Critical or High defects | **Zero.** High defects are **not deferrable** in this pack — see §5 |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**This pack overrides the programme's deferral rule.** `TX-16` permits a High defect to be deferred
by a named decision. **Here it does not**, for a stated reason: a defect in statutory output is not a
quality trade-off but a legal exposure, and the deferral decision would be a decision to issue
non-compliant documents. Two automatic escalations:

| Trigger | Escalation |
|---|---|
| Any defect in Mushak output, VAT computation, the 9.1 derivation, or a statutory document sequence | **Critical**, to CFO with Legal Counsel; **not deferrable** (`NFR-021`, `NFR-100`, `NFR-101`, `MD-040`) |
| Any defect where a posting does not reconcile to its source or a control total does not tie | **Critical**, to CFO and CTO (`DI-02`; same rule as `TS-004` §5) |

---

## 6. Sign-off

| Role | Super-user name | Release | Pack version | Date | Signature |
|---|---|---|---|---|---|
| `R26` Finance Manager | | | | | |
| `R27` Finance Officer | | | | | |
| `R29` Cashier | | | | | |
| `R03` CFO | | | | | |
| **Pack acceptance** — CFO | | | | | |
| **Statutory reading confirmed** — external tax adviser | | | | | |

> **The last row is not a formality.** `CG-002` §5.1 requires class-A statutory content to carry
> external verification, and `AUDIT-007` recorded 26 `DT` files blocked on exactly that. This pack
> verifies those documents; it inherits the same block.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`UA-27` requires the finance function and the tax adviser to state statutory expected results in advance, and no external verification has been obtained.** `AUDIT-007` records 26 `DT` files blocked on gate `G6` external verification; `DT-010` is one of them. **This pack cannot state a compliant expected result for `UAT-R26-001`…`006` until that verification exists**, and `N-09` is a specific unresolved reading | CFO with Legal Counsel and an external VAT adviser | **W1 — before the first statutory script is written** |
| **O-02** | **`G3-04` cannot be evidenced in a test environment.** "Mushak invoices accepted with zero NBR exceptions" is an outcome at `vat.gov.bd` on real filings. UAT can prove the output matches the confirmed reading; **acceptance is provable only in production, one filing cycle after go-live.** The gate criterion as written is unmeetable at the gate, and either its wording or its timing must change | CFO with Programme Manager | **W3 — before `G3`** |
| **O-03** | **`R29` is a 51+-headcount Bengali-first role with no course pack and no Bengali counterpart of this pack.** `UA-03`, `UA-04` and `UA-09` all require both. The cashier is the last person between a statutory document and a customer | L&D Lead with Localisation Lead | **W1** |
| **O-04** | **`DM-008` finance and open-items mapping workbook is unwritten** (Category 12 unstarted). `UAT-R03-003` and `G3-08` require an exact tie to a trial balance that has no agreed derivation; precondition 6 cannot be met. `TS-004` `O-05` records the same gap | Data Migration Lead with Finance | **W1** |
| **O-05** | **`R03` and `R29` have no course pack.** `08B` holds `TR-014` for Finance Officer and Manager and nothing for the CFO or the cashier. `TS-006` `O-07` and `TS-007` `O-05` record the same pattern; **this is now the third pack in which roles cannot satisfy `UA-03`** | L&D Lead | **W1** |
| **O-06** | **Test evidence for statutory scripts is a compliance record, not a test artefact** (`UA-31`, `TS-001` §4.6 `EV-04`), and the retention period is unratified (`TS-001` `O-06`). Filing it as test evidence risks destroying it inside a statutory window under `NFR-088` | Quality Manager with CFO | **W1** |
| **O-07** | **`SP-020` month-end and year-end close is cited as the SOP for `UAT-R26-008` and `G3-05` sets 5 days.** The SOP exists; **what does not exist is a baseline for the current 15–20-day close**, and `06-02` §6 requires every KPI baseline to be measured and signed off *before* the wave begins. `KPI-050` has a stated baseline range, not a measurement | Finance Manager with PMO | **W1 — before `G3`** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; interpretation declared
- [x] **Method taken by reference from `TS-006`, `TS-007` and `TS-008` rather than restated (`CP-01`)**
- [x] Five additional rules stated, all following from the existence of an external judge
- [x] **The three judgements only finance can make are named, and `UA-27` follows from them**
- [x] 46 scripts enumerated across 4 roles with instrument, rules and priority
- [x] Every Mushak form verified against its own `DT` template, on the rendered artefact
- [x] Mushak 6.3 mandatory-field list sourced externally with a verification date (`CM-R8`)
- [x] Ten finance edge cases stated, including sequence reset and closed-period receipt
- [x] **Bilingual status justified by the 51+ cashiers, and a truncated statutory field classified as a compliance defect**
- [x] **The programme's High-defect deferral rule explicitly overridden, with the reason stated**
- [x] External tax-adviser signature required in the sign-off block, inheriting the `AUDIT-007` block honestly
- [x] All internal links resolve
- [x] Seven open items recorded, including the unmeetable-at-the-gate finding in `O-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 46 per-step grids with finance-stated expected results — outstanding; blocked by `O-01`**
- [ ] **`O-01` no external statutory verification — outstanding; blocking**
- [ ] **`O-02` `G3-04` unmeetable in `UAT` — outstanding; gate wording or timing must change**
- [ ] **`O-04` no signed trial balance — outstanding; `G3-08` has no derivation**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending CFO and QA Lead; external verifier not appointed**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
