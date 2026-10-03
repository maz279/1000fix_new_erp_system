---
id: TS-012
title: End-to-End Business Scenario Pack
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme with QA Lead
author: QA Lead with Solution Architect and the fourteen revenue-stream owners
reviewers: [CTO, CEO delegate, CFO, CCO, Operations Director, Solution Architect, Quality Manager, Programme Manager]
approver: CTO with Programme Manager
content_class: E
purpose: >
  One demonstrable end-to-end scenario for each of the fourteen revenue streams the company intends
  to run in this system, plus the four enterprise journeys that support them, reconciled against the
  fifteen critical journeys already named in the non-functional specification. The programme's own
  success criterion is that all fourteen revenue streams transact end to end with zero shadow
  spreadsheets; that is not provable by module tests, by SIT or by UAT, because each of those looks
  at a segment. A revenue stream that has never been run from demand through delivery to cash and
  into a report has not been shown to exist.
traces_to: [README, 05-06 §11, 06-02 §4, 06-02 §5, M01, M05, M06, M08, M09, M11, M12, M13, M14, M15, M18, M19, M20, M21, M23, M31, M38, M39, M35, M56, M51, SP-001, TS-001, TS-002, TS-003, TS-004, TS-005, TS-006, TS-007, TS-008, TS-009, TS-010, TS-011, TS-013, TS-018, RF-003]
priority: P0
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/README.md §The Fourteen Revenue Streams — the fourteen streams and their owning modules
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §11 Critical Journeys Covered by End-to-End Tests — fifteen numbered journeys; §11 End-to-end row requires them automated and run nightly
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §5 Programme-Level Success Criteria criterion 1 — all 14 revenue streams transact end to end in the ERP, with zero shadow spreadsheets in any revenue process; §4 gate criteria per wave
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# End-to-End Business Scenario Pack

| Item | Value |
|---|---|
| Test level | **End-to-end** — `05-06` §11 level 6; automated and run nightly |
| Role executing | Multi-role by design; each scenario names its role chain |
| Modules covered | All 67 are reachable; each scenario names its own chain |
| Portals covered | All 12, as the surfaces the chain passes through |
| Environment | `UAT` for the demonstrated runs; `SIT` for the automated nightly suite |
| Test data set | `TS-002` — data spanning a whole journey, not a single step |
| Wave | W2 · `P0`, with scenarios activating as their streams go live |

> **Template conformance.** `TPL_Test_Script.md` at pack level: this file reconciles, enumerates and
> specifies; per-scenario step grids are instantiated at execution. All six sections retained in
> order.

---

## 1. Traceability

### 1.1 A register conflict, reconciled

The register's justification for this file is *"one end-to-end scenario per revenue stream"* and
traces it to `README` §Fourteen Revenue Streams. **But `05-06` §11 already enumerates fifteen
critical journeys covered by end-to-end tests, and the two lists are not the same list.**

| | Count | Basis |
|---|---:|---|
| `README` §Fourteen Revenue Streams | **14** | How the company makes money |
| `05-06` §11 Critical Journeys | **15** | What must be proven end to end |

Neither is wrong and neither contains the other:

| `05-06` §11 omits | Which is revenue stream |
|---|---|
| Warranty extension and protection product sale | 4 |
| Spare parts and accessories sale | 5 |
| Data backup and archival subscription | 9 |
| Advertising, boost and lead placement | 14 |

| `05-06` §11 includes | Which is not a revenue stream |
|---|---|
| Purchase requisition → PO → receipt → three-way match → payment | Procure to pay |
| Payroll cycle → attendance lock → BEFTN → payslips → posting | Hire to pay |
| Complaint → non-conformance → root cause → CAPA → closure | Quality loop |
| Month-end close → reconciliation → VAT return → management pack | Record to report |

And `05-06` §11 splits one revenue stream across three journeys (book online, walk-in, pick-and-drop
are all **stream 2**, out-of-warranty paid repair, in three delivery modes) and merges two into one
(journey 9 covers streams 10 **and** 11).

**The reconciliation adopted here: 18 scenarios, 20 executions.**

| Set | Count |
|---|---:|
| Revenue-stream scenarios, one per stream | **14** |
| Enterprise support scenarios, from `05-06` §11 journeys 12–15 | **4** |
| **Scenarios** | **18** |
| Delivery-mode variants of `E2E-02` (walk-in, on-site, pick-and-drop) | +2 |
| **Executions** | **20** |

**Why this reconciliation and not the alternative.** Adopting `05-06` §11's fifteen unchanged would
leave four revenue streams with no end-to-end proof, and `06-02` §5 criterion 1 makes all fourteen a
programme success criterion. Adopting the fourteen unchanged would drop procure-to-pay, payroll,
the quality loop and month-end — the four journeys that carry the most `P0` business rules on the
programme. **The union is the only set that satisfies both documents**, and the mapping in §1.2
proves that every item in each source list is covered.

> **This conflict is reported, not silently resolved.** A future reader finding "18" beside a
> register that says "one per revenue stream" and a specification that says fifteen would reasonably
> treat one as an error. Raised as a finding in the Category 13 audit, and `05-06` §11 should carry
> a cross-reference to this file.

### 1.2 Coverage mapping — both source lists, proved

| `E2E` | Scenario | Revenue stream | `05-06` §11 journey |
|---|---|---:|---:|
| `E2E-01` | Authorised brand warranty service → claim → reimbursement → reconciliation | 1 | 4 |
| `E2E-02a` | **Walk-in** paid repair → workshop → estimate → QC → handover → pay | 2 | 2 |
| `E2E-02b` | **On-site** booking → dispatch → field repair → invoice → pay → survey | 2 | 1 |
| `E2E-02c` | **Pick-and-drop** collection → workshop → return delivery → invoice | 2 | 3 |
| `E2E-03` | AMC/RAMC sale → activation → preventive schedule → visit → renewal | 3 | 5 |
| `E2E-04` | Warranty extension sale → registration → claim under the extension | 4 | **—** |
| `E2E-05` | Spare part / accessory sale → pick → dispatch → invoice → return | 5 | **—** |
| `E2E-06` | MSP alert → ticket → remote resolution → SLA measurement → monthly report | 6 | 6 |
| `E2E-07` | Rental reservation → delivery → return → damage assessment → billing | 7 | 8 |
| `E2E-08` | Data recovery case → custody → recovery → handover → purge certificate | 8 | 11 |
| `E2E-09` | Backup / archival subscription → activation → cycle billing → renewal | 9 | **—** |
| `E2E-10` | Trade-in → offer → intake → data wipe → refurbishment → grading → resale | 10, 11 | 9 |
| `E2E-11` | Refurbished device sale → warranty → after-sales service on it | 10 | *(extends 9)* |
| `E2E-12` | E-waste collection → triage → destruction → recycling → disposal certificate | 12 | 10 |
| `E2E-13` | Marketplace order → seller quote → selection → job → review → commission → payout | 13 | 7 |
| `E2E-14` | Advertising / boost purchase → placement → impressions → billing → performance | 14 | **—** |
| `E2E-15` | Purchase requisition → PO → receipt → inspection → three-way match → payment | — | 12 |
| `E2E-16` | Payroll cycle → attendance lock → calculation → approval → BEFTN → payslips → posting | — | 13 |
| `E2E-17` | Complaint → non-conformance → root cause → CAPA → verification → closure | — | 14 |
| `E2E-18` | Month-end close → reconciliation → VAT return → management pack | — | 15 |

**All 14 streams covered. All 15 journeys covered. Zero orphans in either direction.**

> `E2E-11` is the one scenario in neither source list. It is included because stream 10 has **two**
> distinct ends — the refurbished unit is sold, and then it is *serviced under the warranty the sale
> created*. `BRU-TRF-04` requires battery health and known defects disclosed at sale, and the
> consequence of a wrong disclosure only appears when the buyer returns. Recorded so the addition is
> a decision, not scope creep (`CP-04`).

### 1.3 Traceability obligation per scenario

| Field | Source |
|---|---|
| Revenue stream and `05-06` §11 journey | §1.2 above |
| Module chain, in order | Module §5 tables |
| Role chain, in order | `05-04` — every scenario is multi-role |
| Portal chain | `04-00` |
| Business rules crossed | `05-05`, with class |
| Automations relied on | `05-05` §12 |
| **Cash outcome** | The revenue recognised, invoiced and collected — for the 14 revenue scenarios, stated as a number |
| **Report outcome** | The `RP` report or `P06` dashboard the completed journey must appear in |
| Wave and gate | `06-01`, `06-02` §4 |

**The last two columns are what make this pack end-to-end rather than long.** `06-02` §5 criterion 1
requires *"zero shadow spreadsheets in any revenue process"*. A scenario that ends at job closure
proves the operation; a scenario that ends at the ledger and the dashboard proves the *stream*.
`EE-03` makes it a rule.

---

## 2. Preconditions

### 2.1 Rules

| # | Rule |
|---|---|
| **EE-01** | **A scenario runs on one release, in one environment, without a manual intervention that is not itself part of the business process.** A tester who fixes data mid-journey has run a demonstration |
| **EE-02** | **Every scenario is multi-role.** The handoffs between roles are the point; a scenario executed by one super-user with all permissions proves nothing about the seams `SP-004` and `SP-005` govern |
| **EE-03** | **Every revenue scenario ends at cash and at a report** — invoice issued, payment received, revenue recognised, the journey visible in its `RP` report or `P06` dashboard. A scenario ending at delivery is truncated |
| **EE-04** | **Every scenario states its cash outcome as a number before it runs** and asserts it after (`UA-19`, `SL-17`) |
| **EE-05** | **No shadow artefact.** If completing the journey requires a spreadsheet, an email or a WhatsApp message outside the system, the scenario **fails** and the gap is recorded — this is the direct test of `06-02` §5 criterion 1 |
| **EE-06** | Each scenario is **demonstrated once to its business owner** in the target wave, and **automated for the nightly suite** thereafter (`05-06` §11) |
| **EE-07** | A scenario is **activated when its stream goes live**, not before. A W7 stream cannot be demonstrated at W2; the pack states the activation wave per scenario and reports coverage against **live** streams, not against 18 |
| **EE-08** | Every scenario's **statutory outputs are the real templates** — Mushak 6.3 on any sale, a destruction certificate on any wipe, a disposal certificate on any recycle — inspected as rendered (`UA-28`) |
| **EE-09** | Every scenario carries **at least one deliberate exception branch** taken on a second run: a declined estimate, a failed payment, a rejected claim, a returned item. A stream proven only on its happy path is proven for a business that does not exist |
| **EE-10** | The nightly automated suite must be **green for five consecutive nights** before a wave gate (`TS-001` §4.5) |

### 2.2 Preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | SIT exit for every module in the chain, on one release (`TS-003`–`TS-005`) | Exit records |
| 2 | UAT complete for every role in the chain (`TS-006`–`TS-011`) | Sign-off records |
| 3 | `TS-002` data spanning the whole journey, internally consistent (`TD-09`, `TD-10`) | Load log with control totals |
| 4 | All 12 portals deployed at the same release for the scenarios that traverse them | Release manifest |
| 5 | Payment, notification and brand-partner sandboxes live simultaneously | `TS-002` `O-03`; `TS-003` `O-03` |
| 6 | The `RP` report or dashboard each scenario ends in | **Category 14 unwritten** — `O-03` |
| 7 | A named business owner per scenario, available for the demonstration (`EE-06`) | `06-01` §4; `TS-001` `O-09` |
| 8 | Automation harness able to run 18 scenarios nightly | `06-04` — **does not exist**, `TS-001` `O-01` |

---

## 3. Scripts

### 3.1 The 18 scenarios

Activation wave per `EE-07`; owner is the accountable business function.

| `E2E` | Scenario | Module chain | Role chain | Wave | Gate | Pri |
|---|---|---|---|:--:|:--:|:--:|
| `E2E-01` | Brand warranty service to reimbursement | `M01`→`M02`/`M31`→`M15`→`M23`→`M09`→`M20`→`M19` | `R08`→`R07`→`R10`→`R09`→`R28`→`R26` | W2→W4 | `G4-01` | **P0** |
| `E2E-02a` | Walk-in paid repair | `M04`→`M01`→`M31`→`M15`→`M23`→`M20` | `R08`→`R09`→`R12`→`R18`→`R29` | **W1** | `G1-02`, `G1-03` | **P0** |
| `E2E-02b` | On-site paid repair | `M01`→`M02`→`M15`→`M23`→`M20`→`M34` | `R36`→`R07`→`R10`→`R26` | W2 | `G2-01` | **P0** |
| `E2E-02c` | Pick-and-drop repair | `M01`→`M03`→`M31`→`M03`→`M20` | `R08`→`R15`→`R16`→`R09`→`R29` | W3 | `G3-07` | **P0** |
| `E2E-03` | AMC sale to renewal | `M07`→`M08`→`M02`→`M20`→`M08` | `R21`/`R22`→`R07`→`R10`→`R26` | W4 | `G4-03`, `G4-04` | **P0** |
| `E2E-04` | Warranty extension sale to claim under it | `M09`→`M17`→`M01`→`M09` | `R08`/`R36`→`R28` | W4 | `G4-01` | P1 |
| `E2E-05` | Part / accessory sale to return | `M37`/`M38`→`M15`→`M41`→`M03`→`M20` | `R36`→`R18`/`R20`→`R16`→`R27` | W3 | `G3-01` | P1 |
| `E2E-06` | MSP alert to monthly service report | `M48`→`M66`/`M05`→`M01`→`M08`→`M20`→`M25` | `R13`→`R22`→`R26` | W5 | `G5-05` | **P0** |
| `E2E-07` | Rental to damage billing | `M13`→`M17`→`M03`→`M13`→`M20` | `R25`→`R15`→`R16`→`R27` | W6 | `G6-01` | P1 |
| `E2E-08` | Data recovery to purge certificate | `M06`→`M24`→`M20` | `R08`→`R14`→`R27` | W6 | `G6-03` | **P0** |
| `E2E-09` | Backup subscription to renewal | `M39`→`M06`→`M20`→`M53` | `R22`→`R27`→`R26` | W6 | `G6` | P2 |
| `E2E-10` | Trade-in to resale | `M14`→`M06`→`M23`→`M15`→`M38`→`M20` | `R25`→`R14`→`R32`→`R27` | W6 | `G6-02` | **P0** |
| `E2E-11` | Refurbished sale to after-sales service on it | `M38`→`M09`→`M01`→`M31`→`M20` | `R25`→`R36`→`R08`→`R12` | W6 | `G6` | P1 |
| `E2E-12` | E-waste collection to disposal certificate | `M18`→`M03`→`M23`→`M24`→`M20` | `R08`→`R16`→`R32`→`R38` | W8 | `G8-04` | P1 |
| `E2E-13` | Marketplace order to seller payout | `M12`→`M01`→`M23`→`M53`→`M20` | `R36`→`R38`→`R24`→`R26` | W7 | `G7-02`, `G7-03` | **P0** |
| `E2E-14` | Boost purchase to performance reporting | `M12`/`M35`→`M20`→`M25` | `R38`→`R24`→`R23`→`R27` | W7 | `G7` | P2 |
| `E2E-15` | Requisition to vendor payment | `M43`→`M16`→`M41`→`M52`→`M50`→`M19` | `R17`→`R19`→`R20`→`R27`→`R26` | W3 | `G3-06` | **P0** |
| `E2E-16` | Payroll cycle to ledger | `M55`→`M56`→`M50`→`M19` | `R31`→`R30`→`R03` | W5 | `G5-01`, `G5-02` | **P0** |
| `E2E-17` | Complaint to CAPA closure | `M34`→`M23`→`M60` | `R08`/`R34`→`R32`→`R06` | W4 | `G5-04` | P1 |
| `E2E-18` | Month-end close to VAT return and management pack | `M19`→`M51`→`M25` | `R27`→`R26`→`R03` | W3 | `G3-05`, `G3-04` | **P0** |

**Pack total: 18 scenarios · 20 executions · 11 at `P0` · 6 at `P1` · 3 at `P2`.**

### 3.2 Wave activation profile

`EE-07` means coverage is reported against live streams, not against 18. This is that table.

| Wave | Scenarios activating | Cumulative live | Coverage denominator |
|:--:|---|---:|---|
| **W1** | `E2E-02a` | 1 | 1 |
| **W2** | `E2E-01` (partial), `E2E-02b` | 3 | 3 |
| **W3** | `E2E-02c`, `E2E-05`, `E2E-15`, `E2E-18` | 7 | 7 |
| **W4** | `E2E-01` (complete), `E2E-03`, `E2E-04`, `E2E-17` | 10 | 10 |
| **W5** | `E2E-06`, `E2E-16` | 12 | 12 |
| **W6** | `E2E-07`, `E2E-08`, `E2E-09`, `E2E-10`, `E2E-11` | 17 | 17 |
| **W7** | `E2E-13`, `E2E-14` | 19 | 19 |
| **W8** | `E2E-12` | **20 executions / 18 scenarios** | 20 |

> **`E2E-01` is the only scenario that activates twice.** The service and claim-creation half runs
> from W2; brand submission, approval and reimbursement are W4 capabilities. Running it as one
> scenario at W2 would fail on an absent capability and be recorded as a defect. Stated so it is not
> mistaken for either.

### 3.3 The scenario step pattern

| Phase | Content |
|---|---|
| **X1 Demand** | The stream's demand event, from its real channel — a customer booking, an alert, a requisition, a seller quote |
| **X2 Commitment** | Estimate, quotation, contract or agreement, with its approval at the real authority level |
| **X3 Delivery** | The operational work, executed by the real role chain, with evidence and QC |
| **X4 Statutory output** | The rendered document the stream requires (`EE-08`) |
| **X5 Cash** | Invoice, payment, receipt, and the posting — asserted as the number stated in advance (`EE-04`) |
| **X6 Recognition** | Revenue recognised, commission or claim settled, deferrals released |
| **X7 Report** | The journey visible in its `RP` report or `P06` dashboard (`EE-03`) |
| **X8 Exception branch** | The second run's deliberate failure branch (`EE-09`) |
| **X9 Shadow check** | An explicit assertion that no step required an artefact outside the system (`EE-05`) |

### 3.4 Exception branches — one per scenario

| `E2E` | Exception branch taken on the second run |
|---|---|
| `E2E-01` | Brand rejects the claim for insufficient evidence; dispute opened and resubmitted |
| `E2E-02a` | Customer declines the estimate; device released unrepaired with a charge decision |
| `E2E-02b` | Payment fails at the customer's door; recovery without losing the job |
| `E2E-02c` | Customer absent at return delivery; re-attempt then return to origin |
| `E2E-03` | Entitlement exhausted mid-term; over-consumption billed rather than absorbed |
| `E2E-04` | Device fails extension eligibility; sale refused |
| `E2E-05` | Item returned; refund to the original method; stock and ledger reversed |
| `E2E-06` | SLA breached; service credit computed automatically |
| `E2E-07` | Asset returned damaged; charge derived from the condition-report difference |
| `E2E-08` | Legal hold applied; purge blocked at the agreed date |
| `E2E-09` | Billing cycle missed; exception raised rather than a silent skip |
| `E2E-10` | Wipe certificate missing; refurbishment blocked |
| `E2E-11` | Buyer returns the unit against the disclosed grade; warranty applies |
| `E2E-12` | Partner certification lapsed at the transfer date; transfer blocked |
| `E2E-13` | Dispute opened; payout blocked; commission reversed on the decision |
| `E2E-14` | Boost purchased but the disclosure suppressed — must be impossible |
| `E2E-15` | Three-way match outside tolerance; payment blocked |
| `E2E-16` | BEFTN file rejected by the bank; no partial disbursement |
| `E2E-17` | CAPA fails effectiveness verification; reopened with severity escalated |
| `E2E-18` | Unposted entries present; period close refused |

### 3.5 Bilingual check

English-only pack (`CG-010` §3.2), executed by the programme. It asserts bilingual output at the
three points in every revenue journey where a Bengali reader receives something:

| Element | EN | BN | Truncation |
|---|:--:|:--:|:--:|
| Every customer notification on the journey (`NT` set) | ● | ● | ● |
| Every statutory or customer-facing document at `X4` (`DT` set, `BN-015`) | ● | ● | ● |
| Every technician- or rider-facing step at `X3` (`UI-012`, `UI-019`) | ● | ● | ● |

---

## 4. Exit Criteria

| Criterion | Threshold |
|---|---|
| Scenarios demonstrated to their business owner in the target wave | **100% of scenarios live in that wave** (`EE-06`, `EE-07`) |
| `P0` scenarios passed | **100%** |
| `P1` scenarios passed | ≥ 95% |
| Cash outcome asserted against a pre-stated number | 100% of the 14 revenue scenarios (`EE-04`) |
| Journey visible in its report or dashboard | 100% (`EE-03`) |
| **Shadow-artefact assertions clean** | **100% — any scenario requiring an out-of-system artefact fails** (`EE-05`) |
| Exception branches executed | 18 of 18 (`EE-09`) |
| Statutory outputs inspected as rendered | 100% (`EE-08`) |
| Nightly automated suite before a wave gate | **Green for 5 consecutive nights** (`EE-10`) |
| Manual interventions during a run | **Zero** (`EE-01`) |
| Multi-role execution | 100%; a single-super-user run is void (`EE-02`) |
| **`06-02` §5 criterion 1 at Month 36** | **All 14 revenue streams demonstrated end to end, zero shadow spreadsheets** |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Two routing rules:**

| Trigger | Route |
|---|---|
| A scenario fails at a **seam** between two modules or two roles | Routed to both owners **and** to the Solution Architect. Seam defects with one owner are the ones that stay open (`TS-003` §5) |
| A scenario can only be completed with an artefact outside the system (`EE-05`) | **Not a defect — a scope gap**, routed to the Programme Manager and the stream owner. `06-02` §5 criterion 1 makes it a programme-level failure, and logging it as a defect hides it in a defect count |

---

## 6. Sign-off

One signature per scenario, by the stream or process owner, in the wave the scenario activates.

| `E2E` | Owner | Wave | Release | Date | Signature |
|---|---|:--:|---|---|---|
| `E2E-01` | Finance Director (warranty recovery) | W4 | | | |
| `E2E-02a/b/c` | Operations Director | W1/W2/W3 | | | |
| `E2E-03` | CCO | W4 | | | |
| `E2E-04` | CCO | W4 | | | |
| `E2E-05` | Inventory Manager | W3 | | | |
| `E2E-06` | Corporate Services Head | W5 | | | |
| `E2E-07` | Corporate Services Head | W6 | | | |
| `E2E-08` | Technical Services Head | W6 | | | |
| `E2E-09` | Technical Services Head | W6 | | | |
| `E2E-10` | Retail Operations Head | W6 | | | |
| `E2E-11` | Retail Operations Head | W6 | | | |
| `E2E-12` | Quality Manager | W8 | | | |
| `E2E-13` | CCO | W7 | | | |
| `E2E-14` | CCO | W7 | | | |
| `E2E-15` | Procurement with CFO | W3 | | | |
| `E2E-16` | HR Manager with CFO | W5 | | | |
| `E2E-17` | Quality Manager | W4 | | | |
| `E2E-18` | CFO | W3 | | | |
| **Pack acceptance** — CTO with Programme Manager | | | | | |

> The owner column is taken from `06-02` §3.5 Benefit Ownership, so **the person who signs that the
> stream works is the person accountable for the benefit it is supposed to produce.** Naming a
> different signatory would separate proof from consequence.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`E2E-02a` activates at W1 and this pack is registered at W2.** `06-02` `G1-02` requires the full service-order lifecycle operating end to end at Month 4 and `G1-03` times the walk-in intake inside it. **The one scenario the first gate depends on is in a W2 file** — the fifth instance of the same sequencing shape in this category | Programme Content Lead with QA Lead | **W1 — register correction** |
| **O-02** | **The register says "one end-to-end scenario per revenue stream"; `05-06` §11 says fifteen journeys; this pack says 18 scenarios in 20 executions** (§1.1). The reconciliation is stated and proved, but **the two source documents still disagree with each other and with the register.** `05-06` §11 should carry a cross-reference to this file and the register row should be restated | Enterprise Architecture with Programme Content Lead | **W2** |
| **O-03** | **`EE-03` requires every scenario to end in a report, and Category 14 `RP` is unwritten.** `RP-001` KPI dictionary, `RP-002` report catalogue and `RP-003`/`RP-004` dashboards do not exist, so `X7` has no target. The same dependency is recorded at `TS-005` `O-04`, `HC-008` `O-01`, `TR-011` `O-01` and `TS-006` `O-06` — **four categories now block on `RP-001`** | BI Lead | **W1 — precedes four categories** |
| **O-04** | **No automation harness exists** for the nightly suite `05-06` §11 requires and `EE-10` gates on. `06-04` is absent (`TS-001` `O-01`). Eighteen multi-module, multi-portal scenarios run nightly is a substantial engineering deliverable that appears in no plan | CTO with Platform Engineering | **W2** |
| **O-05** | **`EE-05` shadow-artefact assertion has no baseline.** `06-02` §5 criterion 1 targets zero shadow spreadsheets in any revenue process, and `06-02` §6 requires every KPI baseline measured and signed off before the wave begins. **Nobody has enumerated the spreadsheets currently in use**, so "zero" has no starting point and no scenario can show improvement | Programme Manager with stream owners | **W2** |
| **O-06** | **`E2E-14` cannot be fully specified.** Stream 14 is advertising, boost and lead placement across `M12` and `M35`; the module set gives the mechanism, and **no rate card, inventory model or performance-measurement definition exists** for it in `MD-029` or `MD-030`. It is the least-specified of the fourteen streams and its scenario is correspondingly thin | CCO with Marketing | **W7** |
| **O-07** | **Five scenarios traverse a portal that is not live in their activation wave.** `E2E-05` (W3) touches `M38` e-commerce whose customer surface is `P01`-W2 but whose native app is W6; `E2E-11` and `E2E-09` assume `P01` shop capability at W6. Each needs its portal dependency confirmed against `06-01` before the scenario is written | Solution Architect with QA Lead | **W3** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; interpretation declared
- [x] **The register / `05-06` §11 conflict identified, reconciled to 18 scenarios, and reported rather than silently resolved**
- [x] Coverage mapping proves all 14 revenue streams and all 15 `05-06` journeys are covered, with zero orphans either way
- [x] The one added scenario (`E2E-11`) justified as a decision under `CP-04`
- [x] Ten rules stated, including the cash-and-report ending and the shadow-artefact assertion
- [x] **`EE-05` makes `06-02` §5 criterion 1 directly testable rather than aspirational**
- [x] 18 scenarios enumerated with module chain, role chain, wave, gate and priority
- [x] Wave activation profile stated, so coverage is reported against live streams (`EE-07`)
- [x] `E2E-01`'s double activation stated explicitly to prevent a false W2 failure
- [x] Nine-phase step pattern defined, ending at the report and the shadow check
- [x] One deliberate exception branch specified per scenario — 18 of 18
- [x] Shadow-artefact findings routed as scope gaps, not defects, with the reason recorded
- [x] Sign-off owners taken from `06-02` §3.5 so proof and benefit accountability sit with the same person
- [x] All internal links resolve
- [x] Seven open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 20 per-execution step grids with pre-stated cash outcomes — outstanding**
- [ ] **`O-01` `E2E-02a` needed at W1 — outstanding; blocking `G1-02`**
- [ ] **`O-03` `RP-001` unwritten — outstanding; `X7` has no target in any scenario**
- [ ] **`O-04` no automation harness — outstanding; `EE-10` ungateable**
- [ ] Named approvers recorded — **pending CTO and Programme Manager**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
