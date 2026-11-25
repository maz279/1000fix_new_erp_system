---
id: TS-004
title: SIT Scenario Library — Module Categories E to G
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead
author: QA Lead with test analysts, Inventory, Procurement and Finance business owners
reviewers: [Solution Architect, CFO delegate, Finance Manager, Inventory Manager, Procurement Officer, Logistics Manager, Quality Manager]
approver: QA Lead with Finance Manager
content_class: E
purpose: >
  The system integration scenarios that cross the boundaries between the nineteen modules of
  categories E to G — supply chain and inventory, assets and facilities, finance and treasury. The
  stock-to-ledger and procure-to-pay chains are the two places on this programme where a defect is
  both silent and cumulative: stock that does not tie to valuation and a three-way match that
  tolerates the wrong difference both produce a general ledger that looks reconciled and is not,
  and neither module reports an error. Financial go-live is blocked on these chains being proven,
  not asserted.
traces_to: [M15, M16, M17, M19, M20, M41, M42, M43, M44, M45, M46, M47, M48, M49, M50, M51, M52, M53, M54, 05-05, 05-06 §11, 05-06 §8, 06-02 §4, MD-035, MD-037, MD-039, MD-040, DT-010, DT-014, TS-001, TS-002, TS-003, TS-005, TS-009, TS-012, TS-018, DM-007, DM-008]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/ — category folders E (6 modules), F (5), G (8); each module file §5 requirement tables, §9 business rules, §17 acceptance criteria; E, F and G each carry a _CATEGORY_*_AUDIT_REPORT.md
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §6 BRU-INV-*/BRU-SCM-*, §7 BRU-FIN-*/BRU-BIL-*, §12.3 AUT-031…AUT-040, §12.4 AUT-043…AUT-046
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §8 Data Integrity DI-01…DI-08 — decimal arithmetic in money paths, every posting reconcilable to its source, nightly cross-system reconciliation with divergence alerting
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 3 G3-01…G3-09 — the criteria this library evidences, including "Mushak invoices accepted with zero NBR exceptions" and "financial history migrated and reconciled to the trial balance"
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# SIT Scenario Library — Module Categories E to G

| Item | Value |
|---|---|
| Test level | **SIT** — method defined in `TS-003` §2.1 and §3.1 |
| Role executing | Test analysts, with `R17`, `R18`, `R19`, `R20`, `R26`, `R27`, `R29` as scenario witnesses |
| Modules covered | **19** — `E` (`M15`, `M16`, `M41`–`M44`) · `F` (`M17`, `M45`–`M48`) · `G` (`M19`, `M20`, `M49`–`M54`) |
| Portals covered | `P03`, `P05`, `P06`, `P09` |
| Environment | `SIT` (`TS-001` §4.7) |
| Test data set | `TS-002` — personas 4, 5, 8; sets `M-01`…`M-08`, `D-08`, `D-09` |
| Wave | W3 · **but `M15`, `M19` and `M20` are consumed from W1** — open item `O-01` |

> **Template conformance.** As `TS-003`: `TPL_Test_Script.md` applied at library level, all six
> sections retained in order with library-level interpretation.

> **Method by reference, not restatement.** The sixteen shared SIT rules (`SL-01`…`SL-16`) and the
> eight-phase step pattern live in [`TS-003_SIT_Scenario_Library_Categories_A_to_D.md`](TS-003_SIT_Scenario_Library_Categories_A_to_D.md)
> §2.1 and §3.1. This file adds only the rules that money and stock require and that prose
> boundaries do not (§2.1).

---

## 1. Traceability

### 1.1 The boundary map

Nineteen modules, **sixteen boundaries that carry a financial or custodial obligation**.

| # | Boundary | Obligation crossing it | Scenarios |
|---:|---|---|---|
| BD-19 | `M43` → `M16` | Forecast becomes a requisition with the right quantity | `SIT-E-001`, `002` |
| BD-20 | `M16` → `M42` | PO only to an active, approved vendor; performance recorded | `SIT-E-003`, `004` |
| BD-21 | `M16` → `M41` → `M15` | Receipt, inspection, quarantine, availability | `SIT-E-005`…`007` |
| BD-22 | `M44` → `M15`/`M19` | Landed cost allocated before final valuation | `SIT-E-008` |
| BD-23 | `M16` → `M52` → `M50` | Three-way match, payment schedule, TDS, disbursement | `SIT-E-009`…`012` |
| BD-24 | `M15` → `M19` | **Every stock movement produces a correct, reconcilable posting** | `SIT-E-013`, `014` |
| BD-25 | `M17` → `M09`/`M01` | Asset identity carries warranty and service history | `SIT-F-001`, `002` |
| BD-26 | `M45` → `M23` | Calibration currency gates measurement-dependent work | `SIT-F-003`, `004` |
| BD-27 | `M46` → `M02`/`M52` | Vehicle availability, fuel and maintenance cost attribution | `SIT-F-005`, `006` |
| BD-28 | `M48` → `M05`/`M01` | Telemetry threshold becomes a ticket, then a proactive booking | `SIT-F-007`, `008` |
| BD-29 | `M49` → `M19` | Capitalisation, depreciation, disposal | `SIT-F-009`, `010` |
| BD-30 | `M20` → `M19` | Invoice, receipt and credit note post correctly and reconcile | `SIT-G-001`…`004` |
| BD-31 | `M20` → `M51` | **VAT on every invoice; Mushak output and return derivation** | `SIT-G-005`…`008` |
| BD-32 | `M50` → `M19`/`M20` | Bank import, auto-match, exceptions only | `SIT-G-009`…`011` |
| BD-33 | `M53` → `M12`/`M20` | Revenue recognition, commission, settlement, payout | `SIT-G-012`…`014` |
| BD-34 | `M54` → `M19`/`M36` | Cost centre, budget check, contract profitability | `SIT-G-015`…`018` |

### 1.2 Traceability obligation

As `TS-003` §1.3, with two additions that apply only to this library:

| Field | Source of truth |
|---|---|
| **Ledger effect** | `MD-035` chart of accounts — the expected debit and credit accounts, stated before execution (`TX-08`) |
| **Tax treatment** | `MD-037` tax code and Mushak mapping — the expected code, rate and Mushak form |

**A financial scenario whose expected result does not name the accounts is not a financial
scenario.** "The invoice posted" is not verifiable; "AR debited 11,500, revenue credited 10,000,
output VAT credited 1,500, all in `BDT` to two decimals" is.

---

## 2. Preconditions

### 2.1 Additional rules for money and stock boundaries

`SL-01`…`SL-16` apply in full. These six are added:

| # | Rule |
|---|---|
| **SL-17** | Every financial scenario states its **expected journal** — accounts, amounts, currency, dimension — before execution, from `MD-035` and `MD-036` |
| **SL-18** | Every posting is verified as **reconcilable to its source transaction** (`DI-02`), by navigating from the ledger line back to the document, not only forward |
| **SL-19** | Stock is verified as **quantity, location and valuation basis simultaneously** (`SL-09`), and consignment stock is confirmed excluded from own-stock valuation (`BRU-INV-04`) |
| **SL-20** | **A control total is taken before and after** every scenario that moves money or stock, and the difference is asserted — not inspected |
| **SL-21** | No money path is verified with a floating-point comparison. Decimal to two places, exact (`DI-01`, `AS-10`) |
| **SL-22** | Where a scenario has a **nightly reconciliation** counterpart (`DI-07`), the reconciliation is run and its divergence report asserted empty before the scenario passes |

### 2.2 Environment and data preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | `SIT` at a single declared release across all 19 modules; `TS-003` preconditions 1–4 met | Release manifest |
| 2 | `MD-035` chart of accounts loaded and the fiscal year open (`MD-041`, July–June) | Load log; period status |
| 3 | `MD-037` tax codes, VAT rates and Mushak mapping loaded; the Company BIN configured | Configuration evidence; `BRU-FIN-01` depends on it |
| 4 | `MD-039` currency, FX and rounding policy configured; a USD rate loaded for `SIT-G-013` | Rate table |
| 5 | `MD-040` document sequences configured — a Mushak challan with a wrong or reused sequence is non-compliant | Sequence register |
| 6 | Opening balances from `TS-002` `M-08` loaded and **tied to a stated trial balance** | Signed control total |
| 7 | Vendor master with one active, one inactive and one unapproved vendor (`BRU-SCM-02`) | `TS-002` persona 5 |
| 8 | Warehouse and location master with a quarantine location configured (`BRU-INV-07`) | `MD-004` |
| 9 | Bank statement import file in the production format, with two unmatchable lines | `M50` sandbox |
| 10 | Role accounts for `R17`–`R20`, `R26`, `R27`, `R29`, and **two separate users** to exercise `SOD-01`…`SOD-05` and `SOD-12` | **Does not exist** — `TS-002` `O-04` |

---

## 3. Scripts

Step pattern per `TS-003` §3.1, with phase **P5 Verify money and stock** expanded into P5a ledger,
P5b tax and P5c valuation for this library.

### 3.1 Category E — Supply Chain & Inventory · 14 scenarios

`M15` `M16` `M41` `M42` `M43` `M44`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-E-001` | Stock reaching reorder point drafts a requisition with the recommended quantity and alerts the owner | BD-19 | `AUT-031` | P1 |
| `SIT-E-002` | **PO refused for an item whose network-wide stock already exceeds maximum**, then permitted on authorised override with a reason | BD-19 | `BRU-INV-03`(A) `SL-05` | P1 |
| `SIT-E-003` | **PO cannot be issued to an inactive or unapproved vendor**; issued to an approved one and acknowledgement tracked | BD-20 | `BRU-SCM-02`(H) `AUT-032` | **P0** |
| `SIT-E-004` | Late delivery and a quality rejection both land on the vendor scorecard and are visible in `P05` | BD-20 | `KPI-048` | P2 |
| `SIT-E-005` | Goods received, inspected, stock updated, three-way match triggered | BD-21 | `AUT-033` | **P0** |
| `SIT-E-006` | **Goods failing inspection go to quarantine and never to available stock**; a subsequent issue attempt against them fails | BD-21 | `BRU-INV-07`(H) | **P0** |
| `SIT-E-007` | Serialised part has its serial captured at both receipt and issue; **issue without a serial is refused** | BD-21 | `BRU-INV-08`(H) | P1 |
| `SIT-E-008` | **Imported stock cannot be valued as final until landed cost is allocated**; allocation changes unit cost and the ledger | BD-22 | `BRU-SCM-04`(C) `SL-19` | **P0** |
| `SIT-E-009` | Three-way match within tolerance routes the vendor invoice to the payment schedule | BD-23 | `BRU-SCM-01`(H) `AUT-034` | **P0** |
| `SIT-E-010` | **Match outside tolerance blocks approval** and lands in a named exception queue with the difference stated | BD-23 | `BRU-SCM-01`(H) `AUT-034` failure path | **P0** |
| `SIT-E-011` | **The same user cannot create a vendor and approve that vendor's invoice**; a second user completes it | BD-23 | `BRU-SCM-03`(H) `SOD-01` `SOD-02` | **P0** |
| `SIT-E-012` | **TDS deducted at the correct rate before payment proceeds**; payment blocked otherwise | BD-23 | `BRU-FIN-09`(H) | **P0** |
| `SIT-E-013` | Every stock movement type — receipt, issue, transfer, adjustment, return, scrap — produces the expected journal and reconciles back to its document | BD-24 | `SL-17` `SL-18` `DI-02` | **P0** |
| `SIT-E-014` | **Inter-branch transfer requires source approval and destination confirmed receipt**; in-transit stock is valued and visible | BD-24 | `BRU-INV-02`(H) | P1 |

### 3.2 Category F — Asset, Equipment & Facilities · 10 scenarios

`M17` `M45` `M46` `M47` `M48`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-F-001` | Customer asset carries warranty state and full service history into every new order; ownership transfer moves the history | BD-25 | `BRU-SRM-01`(H) `BRU-SRM-02`(H) | **P0** |
| `SIT-F-002` | Corporate estate of 340 assets (`TS-002` `D-08`) bulk-uploaded, assigned to sites and departments, with 6 invalid rows rejected and reported per row | BD-25 | `NFR-041` bulk with progress feedback | P1 |
| `SIT-F-003` | **Measurement-dependent work is refused on test equipment whose calibration has lapsed**, then permitted after recalibration | BD-26 | `BRU-ESG-04`(H) `MD-046`; `M23` clause | **P0** |
| `SIT-F-004` | Calibration due date generates the task and, on lapse, removes the equipment from the assignable pool | BD-26 | `AUT-041` pattern; `BRU-CTR-07`(H) | P1 |
| `SIT-F-005` | Vehicle unavailable for maintenance removes its rider from the dispatch pool for the period | BD-27 | `BRU-FSM-01`(H) | P1 |
| `SIT-F-006` | Fuel and maintenance cost attribute to the vehicle, the cost centre and the branch | BD-27 | `MD-036`; `SL-17` | P2 |
| `SIT-F-007` | Telemetry threshold breach raises an alert, correlates, and opens a ticket where the rule requires | BD-28 | `AUT-038` | P1 |
| `SIT-F-008` | Predicted failure above confidence notifies the account manager and proposes a proactive booking; **the recommendation requires human confirmation** | BD-28 | `AUT-039` `BRU-AIM-01`(H) | P1 |
| `SIT-F-009` | Asset capitalised from a PO receipt, depreciated on schedule, and the schedule ties to the ledger | BD-29 | `MD-044`; `SL-17` `SL-18` | **P0** |
| `SIT-F-010` | Asset disposal posts gain or loss correctly and **write-off above `BDT 25,000` requires CFO approval** | BD-29 | `05-04` §7; `BRU-INV-06`(H) | P1 |

### 3.3 Category G — Finance & Treasury · 18 scenarios

`M19` `M20` `M49` `M50` `M51` `M52` `M53` `M54`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-G-001` | Job closure auto-generates the invoice with the expected journal; delivery on the customer's preferred channel with a payment link | BD-30 | `BRU-BIL-01`(C/A) `AUT-008` `AUT-022` | **P0** |
| `SIT-G-002` | **Payment cannot be recorded against a cancelled invoice**; a valid payment matches, marks paid, posts and receipts | BD-30 | `BRU-FIN-03`(H) `AUT-024` | **P0** |
| `SIT-G-003` | **Credit note requires Finance Manager approval and the creator cannot approve it**; the reversal journal is exact | BD-30 | `BRU-FIN-04`(H) `SOD-04` | **P0** |
| `SIT-G-004` | Dunning sequence fires at 7/14/21/30 days and enters collections at 30 | BD-30 | `AUT-023` | P1 |
| `SIT-G-005` | **Every customer invoice carries VAT at the applicable rate and displays the Company BIN**; a missing BIN blocks issue | BD-31 | `BRU-FIN-01`(H) `NFR-021` | **P0** |
| `SIT-G-006` | Mushak 6.3 challan renders with every mandatory field, the correct sequence from `MD-040`, and bilingual layout per `DT-010` | BD-31 | `NFR-021`; `DT-010` | **P0** |
| `SIT-G-007` | **Input VAT credit is refused where no valid Mushak 6.3 exists** | BD-31 | `NFR-101` | **P0** |
| `SIT-G-008` | Mushak 9.1 return derives from the sales and purchase registers with no manual adjustment, and ties to the ledger | BD-31 | `NFR-100`; `DT-011`, `DT-014` | **P0** |
| `SIT-G-009` | Bank statement imported; auto-match rate measured; **only exceptions presented** | BD-32 | `AUT-044`; `KPI-051` | **P0** |
| `SIT-G-010` | Two unmatchable lines route to manual reconciliation without blocking the matched remainder | BD-32 | `AUT-044` failure path | P1 |
| `SIT-G-011` | **Branch cash reconciled and closed daily; an unclosed shift blocks the next shift's opening**; the cash handler cannot reconcile their own cash book | BD-32 | `BRU-FIN-10`(H) `SOD-12` | **P0** |
| `SIT-G-012` | Deferred revenue released only per the recognition schedule; **manual release requires CFO approval** | BD-33 | `BRU-BIL-06`(H) | **P0** |
| `SIT-G-013` | Brand claim valued in the agreed currency at the completion-date rate; period-end revaluation posts at the official rate | BD-33 | `BRU-WTY-05`(C) `BRU-FIN-07`(C) | P1 |
| `SIT-G-014` | Marketplace transactions account per the **declared principal-or-agent model**, and the model cannot vary by transaction | BD-33 | `BRU-FIN-08`(H) | **P0** |
| `SIT-G-015` | Requisition above a role's threshold escalates through the `05-04` §7 ladder to the correct approver | BD-34 | `05-04` §7 | P1 |
| `SIT-G-016` | Cost and revenue land on the right cost centre, business line and dimension for every transaction type | BD-34 | `MD-036`; `SL-17` | P1 |
| `SIT-G-017` | Contract profitability reflects delivered cost including parts, labour and logistics, and identifies a negative-margin contract | BD-34 | `KPI-031` | P1 |
| `SIT-G-018` | **A financial period cannot be closed while unposted entries exist**; a hard-closed period cannot be posted to without logged CFO reopening | BD-34 | `BRU-FIN-05`(H) `BRU-FIN-06`(H) `AUT-043` | **P0** |

**Library total: 42 scenarios · 24 at `P0` · 15 at `P1` · 3 at `P2`.**

### 3.4 Negative and edge cases

`TS-003` §3.6 `E-01`…`E-08` apply. These are specific to money and stock:

| # | Condition | Expected system behaviour |
|---|---|---|
| F-01 | Stock issued and the job cancelled in the same second | One outcome; stock returned or held, never both counted |
| F-02 | Payment callback received twice from the gateway | One receipt, one posting (`DI-05`, `SL-11`); the duplicate logged |
| F-03 | Invoice raised, then the underlying job is reopened as rework | Invoice not silently altered; a credit note or an adjustment with an audit trail (`BRU-SRM-19`) |
| F-04 | Tax rate changes with in-flight orders | Rate applied is the rate at the tax point, not the current rate (`CG-006` §5 statutory pinning) |
| F-05 | FX rate missing for a revaluation date | Blocked with a stated reason; **not defaulted to the last rate silently** |
| F-06 | Negative stock attempted through an API call | Refused at the model layer (`BR-STD-01`, `SL-04`) |
| F-07 | Cycle count posted against a location while a transfer is in transit | In-transit quantity is not double-counted; the count variance excludes it |
| F-08 | A journal that does not balance | Rejected atomically; **no partial posting** (`NFR-029` ACID with full rollback) |
| F-09 | Rounding remainder on a 3-way cost allocation | Allocated per `MD-039`; total unchanged to the paisa (`SL-21`) |
| F-10 | Nightly cross-system reconciliation finds a divergence | Divergence alert raised; dependent dashboard refresh blocked (`DI-07`, `AUT-059`) |

### 3.5 Bilingual check

English-only library (`CG-010` §3.2). It asserts bilingual behaviour at the two boundaries where a
customer or an employee sees the output:

| Element | EN | BN | Truncation |
|---|:--:|:--:|:--:|
| Mushak 6.3 challan rendering, `SIT-G-006` — bilingual statutory layout per `DT-010` and `BN-015` | ● | ● | ● |
| Amount grouping, `SIT-G-001`/`006` — `12,34,567` in the Bengali locale, `1,234,567` in English, same value | ● | ● | ● |

---

## 4. Exit Criteria

`TS-003` §4 thresholds apply in full. These are additional and stricter:

| Criterion | Threshold |
|---|---|
| Expected journal stated **before** execution for every financial scenario | 100% (`SL-17`, `TX-08`) |
| Postings reconcilable backwards from ledger to document | 100% (`SL-18`, `DI-02`) |
| Control totals asserted before and after | 100% of money- and stock-moving scenarios (`SL-20`) |
| Money comparisons in exact decimal | 100%; **any floating-point comparison found is a Critical defect** (`SL-21`, `AS-10`) |
| Nightly reconciliation divergence report | Empty (`SL-22`, `DI-07`) |
| Mushak scenarios `SIT-G-005`…`008` | **100% pass, no tolerance** — `G3-04` requires zero NBR exceptions |
| Segregation-of-duties scenarios (`SOD-01`…`05`, `SOD-12`) | 100% blocked with two distinct users |
| Opening-balance tie to trial balance | Exact — `G3-08` |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Two escalations are automatic in this library**, regardless of the raiser's severity assessment:

| Trigger | Escalation |
|---|---|
| Any defect where a posting does not reconcile to its source, or a control total does not tie | **Critical**, to CFO and CTO — `DI-02` is a `P0` data-integrity requirement and the failure is cumulative |
| Any defect in Mushak output, VAT computation or the 9.1 derivation | **Critical**, to CFO with Legal — the exposure is statutory, not operational (`NFR-021`, `NFR-100`, `NFR-101`) |

---

## 6. Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| QA Lead | | | |
| Solution Architect | | | |
| Finance Manager (`R26`) — categories G, and the E→G postings | | | |
| Inventory Manager (`R17`) — category E | | | |
| Procurement Officer (`R19`) — procure-to-pay | | | |
| CFO delegate — Mushak and period-close scenarios | | | |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This library is registered at W3, and three of its modules are consumed earlier.** `M15` inventory and `M19`/`M20` finance appear in `06-02` `G1-05` (migration reconciliation), `G2-06` (inventory accuracy ≥ 95% by count) and `G2-07` (van-stock variance < 2%) at W1 and W2. **The stock-to-ledger boundary is therefore tested after the gates that depend on it** | Programme Content Lead with QA Lead | **W1 — register correction** |
| **O-02** | **Mushak scenarios need external validation, not internal agreement.** `SIT-G-006`, `-007`, `-008` verify that output *matches the specification*; `G3-04` requires that the NBR *accepts* it. `DT-010` and `AUT-007` in `AUDIT-007` already record 26 `DT` files blocked on external verification, and this library inherits the block | CFO with Legal Counsel and an external VAT adviser | **W3 — before `G3`** |
| **O-03** | **Segregation-of-duties scenarios need two distinct users per rule and the permission engine configured to block** (`NFR-064`). No role accounts exist (`TS-002` `O-04`) and `SP-006` records the same register with no verification path | `M29` owner with CFO | **W1** |
| **O-04** | **`PERF`-scale valuation is untested at SIT volumes.** `SIT-E-013` proves each movement type posts correctly at 1,800 devices; the `NFR-053` target is 5 million service orders a year. Correct-but-slow posting is a `TS-014` finding, but **correct-but-non-atomic-under-load is a data-integrity failure this library cannot see** | QA Lead with Platform Engineering | **W3 — coordinate with `TS-014`** |
| **O-05** | **`DM-007` and `DM-008` mapping workbooks are unwritten** (Category 12 unstarted). `SIT-E-013` and `SIT-G-018` assume an opening position that migration supplies; without the workbooks the control totals in precondition 6 have no agreed derivation | Data Migration Lead | **W1** |
| **O-06** | **Nightly cross-system reconciliation (`DI-07`) has no owning specification.** `SL-22` requires its divergence report to be empty before a scenario passes, and no document defines which systems it spans, what it compares or who receives the alert | Solution Architect with Finance Manager | **W3** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at library level; interpretation declared
- [x] **Method taken by reference from `TS-003` §2.1 and §3.1 rather than restated (`CP-01`)**
- [x] Six additional rules stated, covering journals, reconcilability, control totals and decimal exactness
- [x] Sixteen financial and custodial boundaries derived and mapped
- [x] 42 scenarios enumerated with boundary, rule class, automation and priority
- [x] **Expected journal required before execution — the discipline that makes a financial pass verifiable**
- [x] Ten money-and-stock edge cases stated, including non-atomic posting and duplicate gateway callbacks
- [x] Two automatic Critical escalations defined so severity is not negotiated on statutory output
- [x] Exit criteria stricter than the sibling libraries where statutory exposure requires it
- [x] All `BRU-`, `SOD-`, `AUT-`, `DI-`, `NFR-` and `KPI-` identifiers resolve to their owning register
- [x] All internal links resolve
- [x] Six open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 42 per-step grids and their expected journals instantiated — outstanding**
- [ ] **`O-02` external Mushak validation — outstanding; blocking `G3-04`**
- [ ] **`O-05` `DM-007`/`DM-008` unwritten — outstanding; blocks the opening-position control totals**
- [ ] Named approvers recorded — **pending QA Lead and Finance Manager**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
