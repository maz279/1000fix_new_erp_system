---
id: TS-003
title: SIT Scenario Library — Module Categories A to D
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead
author: QA Lead with test analysts and module business owners
reviewers: [Solution Architect, Operations Director, CCO delegate, Quality Manager, Customer Service Manager, Retail Operations Head]
approver: QA Lead with Operations Director
content_class: E
purpose: >
  The system integration scenarios that cross the boundaries between the twenty-six modules of
  categories A to D — service delivery, customer engagement, commercial and the circular business —
  and the shared SIT method the two sibling libraries reuse. Module-level testing proves each module
  does what its own specification says; nothing in it proves that a warranty order created in M01
  reaches a claim in M09 with the evidence M09 requires, or that a trade-in in M14 cannot proceed
  without the destruction certificate M06 issues. Category boundaries are where integration defects
  live, and they are invisible to the teams on either side of them.
traces_to: [M01, M02, M03, M04, M05, M06, M07, M08, M09, M10, M11, M12, M13, M14, M18, M27, M31, M32, M33, M34, M35, M36, M37, M38, M39, M40, 05-05, 05-06 §11, 05-06 §12, 06-02 §4, SP-001, TS-001, TS-002, TS-004, TS-005, TS-012, TS-018]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/ — category folders A (7 modules), B (7), C (9), D (3); each module file §5 requirement tables, §9 business rules and §17 acceptance criteria
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §2–§9 and §12 — the BRU- rules and AUT-001…AUT-030 automations these scenarios cross; BR-STD-01 (a rule bypassed by an API call is not a rule)
    verified: 2026-08-19
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-001_Process_Architecture_and_Value_Stream_Map.md §109 and §298 — the value-stream table is the declared basis of cross-module test scenarios
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# SIT Scenario Library — Module Categories A to D

| Item | Value |
|---|---|
| Test level | **SIT** — the category-boundary level defined in `TS-001` §4.1 |
| Role executing | Test analysts, with `R05`, `R06`, `R07`, `R08`, `R09`, `R28` as scenario witnesses |
| Modules covered | **26** — `A` (`M01`–`M06`, `M31`) · `B` (`M07`, `M10`, `M27`, `M32`–`M35`) · `C` (`M08`, `M09`, `M11`, `M12`, `M36`–`M40`) · `D` (`M13`, `M14`, `M18`) |
| Portals covered | `P01`, `P02`, `P03`, `P07`, `P08`, `P09`, `P10` (as surfaces, not as subjects) |
| Environment | `SIT` (`TS-001` §4.7) |
| Test data set | `TS-002` — personas 1, 2, 3, 6, 7, 8, 9, 11 |
| Wave | W2 · **but category A modules go live at W1** — open item `O-01` |

> **Template conformance.** `TPL_Test_Script.md` applied at **library level**: this file specifies
> and enumerates scenarios; the step-by-step grids are instantiated per scenario at execution. All
> six template sections are retained in order with library-level interpretation — §1 Traceability
> becomes the boundary-to-scenario map, §3 Scripts becomes the scenario inventory with its step
> pattern, §5 and §6 become the recording obligations. The same containment pattern that
> `AUDIT-008` KB-10, `AUDIT-009` TR-11 and `AUDIT-010` HC-11 recorded for three other templates
> applies here, and is the subject of `O-06`.

> **This file carries the shared SIT method.** `TS-004` and `TS-005` reference §2.1 and §3.1 rather
> than restating them (`CP-01`). Changing the method changes it here, once.

---

## 1. Traceability

### 1.1 What SIT is, and what it is not

| Level | Question it answers | Owner |
|---|---|---|
| CI **Integration** / **Contract** / **Event** | Did the message conform, arrive once, and validate against its OpenAPI schema? (`AS-07`, `AS-08`, `DI-05`) | Engineering |
| **SIT — this file** | Did the **business outcome** on the far side of the boundary come out right? | QA |
| **E2E** (`TS-012`) | Does a whole revenue stream run end to end, from demand to cash to report? | Programme + QA |
| **UAT** (`TS-006`–`TS-011`) | Can the role that owns the work do it, in their own language, and sign for it? | Business owners |

A contract test confirms `M15` accepted the stock movement `M01` emitted. **A SIT scenario confirms
that the part left van stock, the job cost changed, the invoice line appeared and the ledger moved
by the right amount.** Only the second can be signed by an owner, and only the second catches the
defect where both modules are individually correct and the *business meaning* is wrong.

### 1.2 The boundary map

Twenty-six modules produce far more than twenty-six pairwise boundaries. The library is derived
from the **eighteen boundaries that carry a business obligation**, not from the full cross-product.

| # | Boundary | Obligation crossing it | Scenarios |
|---:|---|---|---|
| BD-01 | `M01` → `M02` | Order becomes a dispatchable job with SLA and skill requirements | `SIT-A-001`…`003` |
| BD-02 | `M01` → `M31` | Order becomes a workshop job at the right repair level | `SIT-A-004`, `005` |
| BD-03 | `M01`/`M31` → `M15` | Parts reserved, issued, returned; van and branch stock move | `SIT-A-006`, `007` |
| BD-04 | `M01` → `M17` | Device identity, history and warranty state | `SIT-A-008`, `009` |
| BD-05 | `M01` → `M20` | Completion becomes a priced, tax-correct invoice | `SIT-A-010`, `011` |
| BD-06 | `M02` → `M03` | Field job becomes a consignment with custody | `SIT-A-012` |
| BD-07 | `M01` → `M23` | QC gate, rework detection, non-conformance | `SIT-A-013`, `014` |
| BD-08 | `M06` → `M01`/`M24` | Data-services custody, purge and certificate | `SIT-A-015`, `016` |
| BD-09 | `M33` → `M01`/`M07` | One party record behind every order and conversation | `SIT-B-001`…`003` |
| BD-10 | `M27`/`M32` → `M01` | A conversation becomes an order without leaving the conversation | `SIT-B-004`…`007` |
| BD-11 | `M34` → `M23` | Complaint becomes a non-conformance and a CAPA | `SIT-B-008`, `009` |
| BD-12 | `M10` → `M11`/`M20` | Entitlement and points affect price and invoice | `SIT-B-010`…`012` |
| BD-13 | `M08` → `M01`/`M02` | Contract generates scheduled work and gates entitlement | `SIT-C-001`…`004` |
| BD-14 | `M09` → `M08`/`M15`/`M20` | Warranty claim, evidence, consignment parts, reimbursement | `SIT-C-005`…`009` |
| BD-15 | `M11`/`M36` → `M01`/`M20` | Rate card and quotation become the priced order | `SIT-C-010`…`012` |
| BD-16 | `M12` → `M01`/`M20`/`M23` | Marketplace job held to owned-job standards; commission and payout | `SIT-C-013`…`016` |
| BD-17 | `M13` → `M17`/`M20` | Rental condition, deposit, damage, billing | `SIT-D-001`…`004` |
| BD-18 | `M14`/`M18` → `M06`/`M23` | Trade-in and e-waste blocked without a destruction certificate | `SIT-D-005`…`010` |

### 1.3 Traceability obligation per scenario

Every scenario, at authoring time, records:

| Field | Source of truth |
|---|---|
| Requirement identifiers | Module §5 tables (`FR-<MOD>-nnn`) |
| Acceptance criteria | Module §17 |
| Business rules exercised, with class | `05-05` (`H` / `A` / `S` / `C`) |
| Automations exercised | `05-05` §12 (`AUT-nnn`) |
| Events crossed | Module §event tables |
| Personas and data | `TS-002` |
| Gate criterion evidenced | `06-02` §4 |

**A scenario with an empty business-rule column is a suspect scenario.** A boundary that crosses no
rule is usually a boundary that has not been understood.

---

## 2. Preconditions

### 2.1 Shared SIT rules — referenced by `TS-004` and `TS-005`

| # | Rule |
|---|---|
| **SL-01** | A SIT scenario states its **business outcome** as the expected result, never a message or a status alone. "Order status = Assigned" is not an outcome; "the technician's queue shows the job with a 4-hour SLA and the customer has been acknowledged on their preferred channel" is |
| **SL-02** | Every scenario crosses **at least one module boundary**. A single-module scenario belongs in that module's own test set |
| **SL-03** | Every class `H` rule on the boundary is exercised **twice**: once satisfied, once breached and blocked. The breach attempt is a numbered step, not a note (`TX-06`) |
| **SL-04** | Every class `H` rule carries an **API-level breach attempt** as well as a UI one, because `BR-STD-01` states that a rule bypassed by an API call is not a rule (`TX-07`) |
| **SL-05** | Class `A` (approved-override) rules are exercised three ways: blocked, overridden by an authorised role with a recorded reason, and **override attempted by an unauthorised role and refused** |
| **SL-06** | Class `C` (computed) rules are verified by **independent recomputation**, not by reading the value the system displayed |
| **SL-07** | Every automation (`AUT-nnn`) on the boundary is tested in its **success path and its declared failure behaviour**. `05-05` §12 states a failure behaviour for every automation; an untested fallback is a fallback that does not exist |
| **SL-08** | Money crossing a boundary is verified **on both sides and in the ledger**, to the paisa, using decimal arithmetic (`DI-01`, `DI-02`) |
| **SL-09** | Stock crossing a boundary is verified as **quantity, location and valuation**, not quantity alone (`BRU-INV-04` makes consignment stock a separate valuation) |
| **SL-10** | An event-driven outcome is verified **after** the event's target latency (`NFR-043`, 5 s p95), and the scenario records whether it arrived inside it |
| **SL-11** | Idempotency is tested on every write boundary: the same event delivered twice produces one business effect (`DI-05`, `AS-08`) |
| **SL-12** | Where a boundary has a documented manual fallback (`NFR-050`), the fallback is exercised at least once per wave |
| **SL-13** | Audit-trail completeness is asserted at every boundary crossing — who, what, when, before, after (`NFR-014`) |
| **SL-14** | A scenario is **not** re-executed to fix a failure. The defect is raised (`TS-018`), fixed, and the scenario re-executed as a new run against a new release identifier (`TX-15`) |
| **SL-15** | Scenarios are executed in **dependency order** within a boundary group; a scenario whose precondition is another scenario's outcome states that dependency explicitly |
| **SL-16** | Every scenario names an **owning module business owner** who is notified of its result, whether or not they attend |

### 2.2 Environment and data preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | `SIT` environment at a single, declared release across all 26 modules | Release manifest recorded in the run record; a mixed-release SIT run is void (`TX-15`) |
| 2 | CI unit, integration, contract and event suites green | Pipeline evidence attached to the run record (`TX-13`) |
| 3 | `TS-002` `SIT` profile loaded: 1,200 parties, 1,800 devices, 6,000 historical jobs, 400 open | Load log with row counts and control totals (`TD-18`) |
| 4 | All `MD` masters configured — branches, zones, catalogue, fault, resolution, reason, status, SLA, tax, price lists | `MD-048` load index; a missing code set makes a passing scenario meaningless (`TD-04`) |
| 5 | Role accounts for `R05`–`R12`, `R15`–`R18`, `R21`, `R22`, `R24`, `R25`, `R28`, `R29`, `R34`, `R36`, `R38` | **Does not exist** — `TS-002` `O-04` |
| 6 | Notification channels pointed at a sandbox, not at live SMS or WhatsApp | Gateway configuration; `TS-002` `O-03` |
| 7 | Payment gateways in sandbox with success, failure, timeout and duplicate-callback triggers available | bKash, Nagad, card sandbox credentials |
| 8 | Event platform (`M28`) observable — dead-letter queue and correlation ids visible to the tester | `NFR-092` distributed tracing with a single correlation id |
| 9 | Brand partner sandbox (`P08`) or a stubbed claim endpoint for `SIT-C-005`…`009` | Stub is acceptable at SIT; a real partner is required at UAT |

---

## 3. Scripts

### 3.1 The scenario step pattern — referenced by `TS-004` and `TS-005`

Each scenario instantiates this pattern; the per-step grid from `TPL_Test_Script.md` §3 is
completed at execution.

| Phase | Step content |
|---|---|
| **P1 Establish** | Bring the source module to the state the boundary requires, and **record the far-side baseline** — stock, balance, queue depth, ledger position |
| **P2 Act** | Perform the single business action that crosses the boundary |
| **P3 Verify near side** | Source-module state, audit entry, event emitted with correct payload |
| **P4 Verify far side** | Target-module business outcome per `SL-01`, within the latency in `SL-10` |
| **P5 Verify money and stock** | `SL-08`, `SL-09` — both sides and the ledger |
| **P6 Breach** | Attempt the class `H` breach, at UI and at API (`SL-03`, `SL-04`) |
| **P7 Idempotency** | Re-deliver the event; assert one business effect (`SL-11`) |
| **P8 Fallback** | Where applicable, disable the automation and exercise the declared failure behaviour (`SL-07`, `SL-12`) |

### 3.2 Category A — Service Delivery & Operations · 16 scenarios

`M01` `M02` `M03` `M04` `M05` `M06` `M31`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-A-001` | Paid on-site order created at intake becomes a dispatchable job with skill and SLA, technician and customer notified | BD-01 | `BRU-SRM-01`(H) `BRU-FSM-01`(H) `BRU-FSM-02`(H) `AUT-001` `AUT-002` `AUT-003` | **P0** |
| `SIT-A-002` | **Warranty-type order refused for a device out of warranty**, then accepted after a valid extension is registered | BD-01, BD-04 | `BRU-SRM-02`(H) `BRU-WTY-07`(H) | **P0** |
| `SIT-A-003` | Privilege Diamond member's order receives priority-1 SLA automatically, and the escalation ladder fires at 50/75/90/100% | BD-01, BD-12 | `BRU-SRM-10`(C) `BRU-SRM-15`(C) `AUT-009` | P1 |
| `SIT-A-004` | Walk-in intake routes to workshop at repair level L2, bench assigned, WIP board reflects it | BD-02 | `BRU-SRM-14`(H) `FR-WSR-*` | **P0** |
| `SIT-A-005` | **L3 board-level job refused at a workshop without the equipment or a certified specialist**, then accepted at a qualified site | BD-02 | `BRU-SRM-14`(H) `BRU-SRM-09`(H) `BRU-HRM-01`(H) | **P0** |
| `SIT-A-006` | Parts reserved on estimate approval, issued to the job, van stock and branch stock both move, job cost updates | BD-03 | `BRU-SRM-11`(H) `BRU-INV-01`(H) `BRU-FSM-08`(H) `AUT-006` | **P0** |
| `SIT-A-007` | Unused part returned from van; valuation restored; **expired-shelf-life part refused for issue** | BD-03 | `BRU-INV-05`(H) `BRU-INV-08`(H) `AUT-035` | P1 |
| `SIT-A-008` | Unregistered device registered as part of intake and appears in the registry with full history thereafter | BD-04 | `BRU-SRM-01`(H) | **P0** |
| `SIT-A-009` | Second order for the same device and fault category within 30 days is flagged as rework, linked, and quality and the original technician's manager notified | BD-04, BD-07 | `BRU-SRM-06`(C) `AUT-011` | P1 |
| `SIT-A-010` | QC pass generates the service report and raises the invoice with correct VAT and BIN; **invoice refused on a non-completed order** | BD-05 | `BRU-SRM-05`(H) `BRU-FIN-01`(H) `BRU-BIL-01`(C/A) `AUT-008` | **P0** |
| `SIT-A-011` | On-site payment collected by the technician reconciles to the branch cash book by shift end; **unclosed shift blocks the next shift's opening** | BD-05 | `BRU-FSM-07`(H) `BRU-FIN-10`(H) | **P0** |
| `SIT-A-012` | Field job requiring depot repair becomes a consignment; custody captured at both handovers; **closure refused without proof of delivery** | BD-06 | `BRU-LOG-01`(H) `BRU-LOG-02`(H) | P1 |
| `SIT-A-013` | **Order cannot reach Completed with an incomplete quality checklist**; independent QC enforced above `BDT 25,000` | BD-07 | `BRU-SRM-04`(H) `BRU-SRM-18`(H) `BRU-QMS-01`(H) `SOD-07` | **P0** |
| `SIT-A-014` | Failed QC raises a non-conformance routed to the process owner, and the job returns to the bench | BD-07 | `BRU-QMS-02`(H) `AUT-049` | P1 |
| `SIT-A-015` | Data-recovery case: custody chain, access limited to the assigned technician, every access logged, purge at the agreed date, certificate issued | BD-08 | `BRU-SEC-03`(H) `BRU-SEC-04`(H) `BRU-SRM-20`(H) | **P0** |
| `SIT-A-016` | **Beyond-economic-repair declaration refused without photographic evidence and a second technician's confirmation** | BD-04, BD-07 | `BRU-SRM-12`(H) | P1 |

### 3.3 Category B — Customer Engagement & Experience · 12 scenarios

`M07` `M10` `M27` `M32` `M33` `M34` `M35`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-B-001` | Party created once in `M33` is the same party in `M01`, `M07`, `M20` and `P01`; a change to it propagates | BD-09 | `M64` golden record; `NFR-014` | **P0** |
| `SIT-B-002` | Two near-duplicate parties from the `TS-002` `N-02` set are matched, merged with survivorship applied, and every child record follows | BD-09 | `DM-011` match/merge; `BRU-ADM-01`(H) | **P0** |
| `SIT-B-003` | Corporate hierarchy: a request raised by a site user rolls to the parent account for consolidated invoicing | BD-09 | `BRU-BIL-07`(H) | P1 |
| `SIT-B-004` | Inbound call identified by number pops Customer 360 in `P10`; a service order is created without leaving the conversation; disposition coded | BD-10 | `AUT-001`; `KPI-027` | **P0** |
| `SIT-B-005` | WhatsApp enquiry handled by `M32`, escalated to a human with full context and transcript intact | BD-10 | `BRU-CAI-*` (`M32` §9); `FR-CAI-019` | P1 |
| `SIT-B-006` | AI assistant answers in Bengali, declines an ungrounded question, and hands over — the disclosure and handover read as one message | BD-10 | `M32` guardrails; `HC-018`/`HC-019` seam | P1 |
| `SIT-B-007` | Same customer across four channels in one day appears as **one** conversation history | BD-10 | `KPI-016` conversations captured 100% | P1 |
| `SIT-B-008` | Complaint raised in `P01` becomes a non-conformance with root cause and CAPA; **cannot be closed without confirming the outcome with the customer** | BD-11 | `BRU-QMS-04`(H) `BRU-QMS-02`(H) `AUT-049` | **P0** |
| `SIT-B-009` | Repeated non-conformance in the same process escalates severity automatically and is tabled for management review | BD-11 | `BRU-QMS-05`(C); **`BRU-QMS-09`(C) and `AUT-QMS-06` resolve in `M23` §9 and §12, not in `05-05`** | P2 |
| `SIT-B-010` | Privilege tier discount applies to **labour only**, never to parts, consumables or transport, and the invoice proves it line by line | BD-12 | `BRU-WTY-06`(C) | **P0** |
| `SIT-B-011` | Points earned on a completed job, redeemed against a later invoice, and reversed when that job is refunded | BD-12 | `AUT-029` `AUT-030` `BRU-BIL-04`(C) | P1 |
| `SIT-B-012` | Campaign-sourced lead converts to a customer and the attribution survives into `M25` reporting | BD-09, BD-12 | `KPI-035` | P2 |

### 3.4 Category C — Commercial, Pricing & Revenue · 16 scenarios

`M08` `M09` `M11` `M12` `M36` `M37` `M38` `M39` `M40`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-C-001` | **Contract cannot be activated without a covered asset, entitlements, a billing frequency and approval**; then activates and generates the full preventive schedule for the term | BD-13 | `BRU-CTR-01`(H) `AUT-016` | **P0** |
| `SIT-C-002` | **AMC-type order refused for a device not on the covered-asset list**, then accepted after the asset is added | BD-13 | `BRU-SRM-03`(H) | **P0** |
| `SIT-C-003` | Entitlement over-consumption is either blocked or flagged for billing per configuration — **never silently absorbed** | BD-13 | `BRU-CTR-04`(H) `BRU-CTR-02`(H) | **P0** |
| `SIT-C-004` | Contract expiry cancels future scheduled work orders and notifies the customer; renewal outreach fires at −90/−60/−30/−15 days | BD-13 | `BRU-CTR-03`(C) `AUT-015` `AUT-017` | P1 |
| `SIT-C-005` | Warranty work order closes; claim auto-created within 24 h with a complete evidence pack | BD-14 | `BRU-WTY-02`(C) `AUT-018` | **P0** |
| `SIT-C-006` | **Claim submission refused without a completed work order, serial, before-photo, diagnosis and replaced-parts list** | BD-14 | `BRU-WTY-01`(H) `BRU-SRM-17`(H) | **P0** |
| `SIT-C-007` | **Duplicate claim for the same serial and fault within 90 days is blocked** | BD-14 | `BRU-WTY-03`(H) | P1 |
| `SIT-C-008` | **Brand consignment part cannot be consumed on a non-warranty job**; consignment stock stays out of own-stock valuation | BD-14, BD-03 | `BRU-WTY-04`(H) `BRU-INV-04`(C) | **P0** |
| `SIT-C-009` | Brand remittance received, matched to claims, posted to the ledger; unmatched items flagged, not absorbed | BD-14 | `AUT-021` `BRU-WTY-05`(C) | P1 |
| `SIT-C-010` | Quotation built from the rate card converts to an order at the quoted price; **an expired estimate requires re-issue, not extension** | BD-15 | `BRU-SRM-13`(H) `AUT-005` | **P0** |
| `SIT-C-011` | Estimate above `BDT 5,000` blocks work until documented customer approval; above `BDT 25,000` also requires branch manager approval | BD-15 | `BRU-SRM-07`(H) `BRU-SRM-08`(H); `05-04` §7 | **P0** |
| `SIT-C-012` | Discount above the executing role's authority is refused, then approved by the authorised role with the reason recorded | BD-15 | `05-04` §7; `SL-05` | P1 |
| `SIT-C-013` | **Seller cannot transact until documents are verified, the agreement is signed and an administrator has approved** | BD-16 | `BRU-ECM-01`(H) `BRU-ECM-07`(H) | **P0** |
| `SIT-C-014` | Marketplace job held to identical evidence, QC and warranty standards as an owned job | BD-16 | `BRU-ECM-03`(H) `BRU-FSM-12`(H) | **P0** |
| `SIT-C-015` | Commission accrues after the hold period; **payout blocked entirely while a dispute is open**; reversed on refund | BD-16 | `BRU-BIL-03`(H) `BRU-BIL-04`(C) `AUT-026` `AUT-027` | **P0** |
| `SIT-C-016` | **Seller access to customer contact data expires the defined period after job completion** | BD-16 | `BRU-ECM-05`(H) `EA-04` | P1 |

### 3.5 Category D — Circular & Asset-Based Business · 10 scenarios

`M13` `M14` `M18`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-D-001` | **Rental asset cannot be dispatched without a completed pre-dispatch condition report**; deposit received before handover | BD-17 | `BRU-RNT-01`(H) `BRU-RNT-02`(H) | **P0** |
| `SIT-D-002` | Damage charge derived from the outbound-versus-inbound condition difference; a discretionary charge requires approval | BD-17 | `BRU-RNT-03`(C/A) | P1 |
| `SIT-D-003` | **Returned asset re-enters the available pool only after cleaning, servicing and functional test** | BD-17 | `BRU-RNT-04`(H) | P1 |
| `SIT-D-004` | Overdue rental accrues charges automatically per tariff with escalating notification | BD-17 | `BRU-RNT-05`(C) | P2 |
| `SIT-D-005` | **No trade-in device proceeds to refurbishment or resale without a certified data destruction record** | BD-18 | `BRU-TRF-01`(H) `BRU-ESG-01`(H) | **P0** |
| `SIT-D-006` | Provenance and stolen-device screening must pass before a trade-in offer is paid | BD-18 | `BRU-TRF-02`(H) | **P0** |
| `SIT-D-007` | **Refurbished unit cannot be listed without a completed QA protocol and an assigned grade**; battery health and known defects disclosed on the listing | BD-18 | `BRU-TRF-03`(H) `BRU-TRF-04`(H) | **P0** |
| `SIT-D-008` | Supervisor grade override requires a recorded justification; **the same user cannot value, purchase and resell** | BD-18 | `BRU-TRF-05`(A) `SOD-10` | P1 |
| `SIT-D-009` | **E-waste transfer refused to a partner whose certification lapsed at the transfer date**; disposal certificate retrievable per unit | BD-18 | `BRU-ESG-02`(H) `BRU-ESG-03`(H) `AUT-040` | **P0** |
| `SIT-D-010` | Hazardous item follows its handling, storage and transport rules; **a rider without the certification cannot be assigned it** | BD-18, BD-06 | `BRU-ESG-04`(H) `BRU-LOG-05`(H) | P1 |

**Library total: 54 scenarios · 26 at `P0` · 22 at `P1` · 6 at `P2`.**

### 3.6 Negative and edge cases

Beyond the 25 breach attempts embedded above (`SL-03`), these conditions are exercised at the
boundary itself rather than inside any module:

| # | Condition | Expected system behaviour |
|---|---|---|
| E-01 | Target module unavailable when the event fires | Event retained in the outbox and delivered on recovery; **no business action lost** (`AS-08`, `DI-05`) |
| E-02 | Same event delivered three times | One business effect; two ignored idempotently (`SL-11`) |
| E-03 | Event with a payload field the consumer does not recognise | Consumed without failure; unknown field logged, not dropped silently |
| E-04 | Automation's external dependency fails (payment gateway, brand endpoint, SMS) | The **declared** failure behaviour from `05-05` §12 executes, and the resulting manual task appears in a named queue (`SL-07`) |
| E-05 | Two users act on the same record simultaneously across a boundary | Server-authoritative resolution; the loser is told what happened and what to do (`PS-09`) |
| E-06 | A `MD` code is retired mid-scenario | In-flight records retain the historical code; new records cannot use it |
| E-07 | Money crosses a boundary with a rounding remainder | Remainder allocated per `MD-039`; no paisa created or destroyed (`DI-01`) |
| E-08 | Boundary crossed by an API caller with a valid credential but no scope for the target | Refused at the model layer, not at the view (`BR-STD-01`, `EA-11`) |

### 3.7 Bilingual check

This library is English-only (`CG-010` §3.2) and its scenarios are executed by test analysts. It
nevertheless **asserts** bilingual behaviour at three boundaries, because the defect is only
visible when the boundary is crossed:

| Element | EN | BN | Truncation |
|---|:--:|:--:|:--:|
| Customer acknowledgement sent on `SIT-A-001` in the customer's preferred language | ● | ● | Checked against the `TS-002` `B-04` expansion set |
| Technician notification on `SIT-A-001`, `SIT-A-005` | ● | ● | ● |
| Invoice rendering on `SIT-A-010` — number grouping switches with locale (`TS-002` `M-04`) | ● | ● | ● |

---

## 4. Exit Criteria

| Criterion | Threshold |
|---|---|
| `P0` scenarios passed | **100% — no tolerance** |
| `P1` scenarios passed | ≥ 95% |
| `P2` scenarios passed | ≥ 85% |
| Class `H` rules on in-scope boundaries breached and blocked | **100%**, at UI **and** at API (`SL-04`) |
| Class `C` rules independently recomputed | 100% (`SL-06`) |
| Automations with their failure behaviour exercised | 100% of automations on in-scope boundaries (`SL-07`) |
| Open Critical defects | **Zero** |
| Open High defects | Zero, or deferred by named decision under `TS-018` |
| Idempotency assertions | 100% of write boundaries (`SL-11`) |
| Audit-trail completeness assertions | 100% of boundary crossings (`SL-13`) |
| Money and stock verified on both sides and in the ledger | 100% of financial and inventory scenarios |
| Traceability | Every scenario resolves to ≥ 1 requirement or §17 criterion (`TX-01`) |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Boundary defects are routed to two owners**, not one: the emitting module and the consuming
module. `TS-018` §5 carries the rule, because the commonest outcome of a boundary defect with one
owner is that each side declares the other at fault.

---

## 6. Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| QA Lead | | | |
| Solution Architect | | | |
| Operations Director (`R05`) — categories A, D | | | |
| CCO delegate — categories B, C | | | |
| Quality Manager (`R32`) — QC and non-conformance boundaries | | | |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This library is registered at W2; category A modules go live at W1.** `M01`, `M02`, `M04` and `M31` are W1 deliverables and `06-02` `G1-02` requires the full service-order lifecycle operating end to end at Month 4. The 16 `SIT-A-*` scenarios are consumed one wave before the file exists — the same sequencing shape `AUDIT-008`, `-009` and `-010` each recorded | Programme Content Lead with QA Lead | **W1 — register correction** |
| **O-02** | **`SIT` role accounts do not exist** (precondition 5). Nineteen roles are needed and `05-04` §10 criterion 6 makes negative testing a role-release condition. `TS-002` `O-04` | `M29` owner | **W1** |
| **O-03** | **Brand partner sandbox for `SIT-C-005`…`009`.** A stub is acceptable at SIT, but the claim format is partner-specific and 17+ partners submit differently; a stub built on an assumed format tests the assumption | Warranty Claims Officer (`R28`) with Platform Engineering | **W2** |
| **O-04** | **`M32` conversational AI is a W6 module** but `SIT-B-005`, `-006`, `-007` are W2 scenarios on the `M27`→`M01` boundary. Either the AI-mediated variants defer to W6, or the boundary is tested with a human agent only and the AI path retested later. **Recorded so it is a decision, not an omission** | QA Lead with Contact Centre | W2 |
| **O-05** | **`SP-001` value-stream map is the declared basis of cross-module scenarios** (`SP-001` §109, §298) and it names `TS-003` reciprocally. The 18 boundaries here were derived from module specifications; **they have not been reconciled against `SP-001`'s stream boundaries**, and the two must agree or one is wrong | QA Lead with Business Process Analysts | **W2 — before execution** |
| **O-06** | **`TPL_Test_Script.md` has no library-level variant.** Fifteen Category 13 files apply an article-shaped template at library level, exactly as `KB`, `TR` and `HC` did. `AUDIT-008` R-05, `AUDIT-009` R-09 and `AUDIT-010` R-10 have asked for a specification variant three times | Content Design | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at library level; all six sections retained in order and the interpretation declared
- [x] **SIT defined against CI integration and against E2E, so the level's boundary is unambiguous (`TS-001` §4.1)**
- [x] Eighteen business-obligation boundaries derived and mapped to scenarios
- [x] **Sixteen shared SIT rules stated once here for reuse by `TS-004` and `TS-005` (`CP-01`)**
- [x] Eight-phase step pattern defined, including breach, idempotency and fallback phases
- [x] 54 scenarios enumerated with boundary, rule class, automation and priority
- [x] Every class `H` rule cited resolves in `05-05`; `M32`-scoped `BRU-CAI-*` attributed to `M32` §9
- [x] Negative and edge cases stated at the boundary rather than inside a module
- [x] Numeric exit criteria with no tolerance on `P0` or on hard-rule breach coverage
- [x] Dual-owner routing rule for boundary defects recorded
- [x] All internal links resolve
- [x] Six open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 54 per-step grids instantiated — outstanding; this file specifies and enumerates**
- [ ] **`O-01` W1/W2 sequencing — outstanding; blocking `G1-02` evidence**
- [ ] **`O-05` reconciliation against `SP-001` value streams — outstanding**
- [ ] Named approvers recorded — **pending QA Lead and Operations Director**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
