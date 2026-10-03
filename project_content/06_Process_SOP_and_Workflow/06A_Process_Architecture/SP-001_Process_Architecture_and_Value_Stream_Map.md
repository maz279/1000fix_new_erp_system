---
id: SP-001
title: Process Architecture and Value Stream Map
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Business Process Lead
author: Business Process Lead with Enterprise Architecture
reviewers: [Enterprise Architecture, Operations Director, Finance Manager, HR Manager, Quality Manager, Programme Content Lead]
approver: Chief Operating sponsor — Operations Director
content_class: E
purpose: >
  Maps the five end-to-end value streams the business actually runs — request-to-cash,
  procure-to-pay, hire-to-retire, claim-to-reimbursement and lead-to-contract — onto the 67
  modules and 12 portals that serve them. The module catalogue is organised by capability; the
  business is not. Without this mapping nobody can see where a stream breaks, which module owns
  a handover, or which SOP covers a gap between two modules.
traces_to: [02-01, 02-02, 05-01, 05-05, 06-01, 06-02, SP-002, SP-003, SP-004, SP-005, SP-006]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md — 67 modules, categories A–K
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §12 Automation Catalogue AUT-001…AUT-054
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI register KPI-001…KPI-095
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 4.4 — Quality management system and its processes (process approach, sequence and interaction)
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SP-001 — Process Architecture and Value Stream Map

> **Read this before writing any other `SP` file.** Every SOP in `06B` names the value stream it
> serves and the handover it protects. Those names come from here. An SOP that cannot be placed
> on a stream in §4 is either mis-scoped or is documenting something the business does not need.

---

## 1. Purpose

The 67 module specifications are organised by **capability** — service delivery, commercial,
supply chain, finance, people, platform. That organisation is correct for building software and
wrong for running a company. No customer experiences "M01 Service Request and Order Management".
A customer experiences *"I booked a repair on Friday, a technician came on Saturday, I paid on
Sunday and the invoice arrived on Monday"* — a single stream crossing eleven modules, four
portals, two payment rails and three physical custody transfers.

This file is the translation layer. It states:

- the **five value streams** the business runs;
- the **stages** in each, and which module owns each stage;
- the **handovers between modules**, which is where value is lost;
- the **measurement point** for each stream, tied to the `06-02` KPI register;
- which **SOP in `06B`** governs the human work at each stage.

Without it: modules are built and tested individually, each passes its own acceptance criteria,
and the end-to-end stream still fails — because nobody owned the seam. This is the single most
common ERP failure mode and it is a process-architecture failure, not a code failure.

---

## 2. Scope

**In scope**

- The five enterprise value streams and their decomposition to Level 2 (stage) and Level 3 (activity).
- The module, portal, role and SOP responsible at each stage.
- Handover points, their failure modes and their controls.
- The stream-level measurement model.

**Out of scope**

| Not covered here | Owned by |
|---|---|
| Current-state processes, variation and workarounds | `SP-002` As-Is Process Baseline Register |
| Notation, decomposition depth and diagram conventions | `SP-003` To-Be Process Design Standard |
| Who may approve what, to what value | `SP-004` Approval Matrix and Delegation of Authority |
| Escalation destinations and timers | `SP-005` Escalation Matrix |
| Incompatible duty pairs | `SP-006` Segregation of Duties Register |
| Step-level instructions for a person | The 28 SOPs in `06B` |
| Module capability and functional requirements | `1000fix_ERP_Module/03_Modules/` |

---

## 3. Audience

| Reader | Uses it to |
|---|---|
| Business Process Lead | Author and review the `06B` SOP set; find unowned seams |
| Enterprise Architecture | Validate that module boundaries follow stream boundaries |
| Programme delivery (PMO) | Sequence waves so a stream goes live whole, not in fragments |
| Test lead (`TS-003`) | Build end-to-end test scenarios that cross modules |
| Training designer (`TR-002`) | Teach a role its place in a stream, not a list of screens |
| Internal and ISO 9001 auditors | Evidence of clause 4.4 — determined processes, their sequence and their interaction |
| Change management (`CM-004`) | Explain to staff what changes about the *work*, not the software |

---

## 4. Content

### 4.1 The process hierarchy

Four levels. `SP-003` fixes the notation; this file fixes the levels.

| Level | Name | Example | Where it is documented |
|---:|---|---|---|
| **L0** | Value stream | Request-to-cash | This file, §4.3 |
| **L1** | Stage | Diagnose and estimate | This file, §4.4–4.8 |
| **L2** | Process | Build and issue a repair estimate | The relevant `06B` SOP |
| **L3** | Activity / step | Apply the standard repair time from `MD-025` | The step table in that SOP, §5 |

**Rule PA-01.** A stage (L1) has exactly one owning module and exactly one accountable role.
Two owners means the stage is drawn wrong.

**Rule PA-02.** Every L1→L1 handover is either inside one module (safe) or across modules
(controlled). Cross-module handovers are enumerated in §4.9 and each carries a named control.

**Rule PA-03.** Every L2 process has an SOP in `06B` **or** an explicit statement in §4.9 that it
is fully automated and needs none. There is no third state.

### 4.2 The five value streams

| # | Value stream | Starts when | Ends when | Modules | Portals | Primary KPI |
|---|---|---|---|---:|---|---|
| **VS-1** | **Request-to-cash** | A customer asks for service on any channel | Cash is banked and the job is closed | 24 | `P01` `P02` `P03` `P09` `P10` | `KPI-002` TAT, `KPI-054` invoice within 1h |
| **VS-2** | **Procure-to-pay** | A need for a part, service or asset is identified | The supplier is paid and the ledger balanced | 11 | `P03` `P05` | `KPI-049` three-way match exceptions |
| **VS-3** | **Hire-to-retire** | A position is approved as vacant | The leaver's access is revoked and final pay settled | 9 | `P03` | `KPI-059` payroll processing time |
| **VS-4** | **Claim-to-reimbursement** | A warranty job closes | The brand's remittance is matched in the ledger | 8 | `P02` `P03` `P08` | `KPI-040` days to reimbursement |
| **VS-5** | **Lead-to-contract** | A prospect or renewal signal appears | A contract is active with entitlements live | 10 | `P03` `P04` `P06` | `KPI-028` renewal rate |

> Two further streams exist but are **variants**, not separate streams, and are documented as
> branches: **asset-to-disposal** (trade-in → refurbishment → resale → e-waste) is a branch of
> VS-1 from the intake stage; **incident-to-resolution** (complaints, quality events, internal
> IT) is a cross-cutting loop attached to every stream at the exception point. Treating them as
> separate top-level streams was rejected — see the decision log in §4.11.

### 4.3 Stream map — the one-page view

```
                 ┌──────────────────────────── VS-5 LEAD-TO-CONTRACT ────────────────────────────┐
                 │  Lead → Qualify → Quote → Approve → Sign → Activate → Entitlements live       │
                 │  M07    M07       M36     SP-004    M24     M08        M08                     │
                 └──────────────────────┬──────────────────────────────────────────────────────────┘
                                        │ entitlement check
                                        ▼
 ┌──────────────────────────────── VS-1 REQUEST-TO-CASH ─────────────────────────────────────────┐
 │ Capture → Triage → Schedule → Custody → Diagnose → Estimate → Approve → Repair → QC →         │
 │  M01/M27   M26/M01  M02/M04    M03/M04   M31/M02   M36/M11    customer   M31/M02  M23         │
 │                                                                                                │
 │ → Release → Invoice → Collect → Bank → Close → Feedback                                        │
 │    M04/M03   M20      M20/M50   M50    M01     M34                                             │
 └───────┬─────────────────────────────────────────────────────┬──────────────────────────────────┘
         │ parts demand                                        │ warranty job
         ▼                                                     ▼
 ┌──── VS-2 PROCURE-TO-PAY ─────┐            ┌──── VS-4 CLAIM-TO-REIMBURSEMENT ─────────────────┐
 │ Requisition → Source → PO →  │            │ Eligibility → Evidence → Submit → Query →        │
 │  M16          M16      M16   │            │  M09          M09        M09/P08   M09           │
 │ → Receive → Match → Pay      │            │ → Decision → Bill brand → Remittance → Match     │
 │   M41/M15    M52    M52/M50  │            │    M09        M20         M50         M19        │
 └──────────────────────────────┘            └──────────────────────────────────────────────────┘

 ┌──── VS-3 HIRE-TO-RETIRE ──────────────────────────────────────────────────────────────────────┐
 │ Requisition → Recruit → Offer → Join → Provision → Train/Certify → Perform → Pay → Exit       │
 │  M58          M58       M58     M21    M29/M30     M22            M57       M56   M21/M29     │
 └────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 VS-1 Request-to-cash — stage detail

| # | Stage | Owning module | Accountable role | Portal | SOP | Exit condition |
|---:|---|---|---|---|---|---|
| 1 | Capture the request | `M01` (`M27` for voice, `M38` for web) | R08 Service Centre Agent / R34 Contact Centre Agent | `P01` `P03` `P10` | `SP-007`, `SP-034` | Service order exists with an identified device (`BRU-SRM-01`) |
| 2 | Triage and classify | `M01` with `M26` | R08 / R13 Remote Support Engineer | `P03` `P10` | `SP-033` | Fault symptom coded from `MD-024`; delivery mode chosen |
| 3 | Schedule and assign | `M02` | R07 Dispatch Manager | `P03` | `SP-008` | Technician assigned, skill-matched (`BRU-FSM-02`), inside capacity (`BRU-FSM-01`) |
| 4 | Take custody | `M04` walk-in · `M03` pick-and-drop · `M02` on-site | R08 / R16 Rider | `P03` `P09` | `SP-007`, `SP-009` | `DT-002` intake receipt signed; custody scan recorded (`BRU-LOG-01`) |
| 5 | Diagnose | `M31` bench · `M02` field | R10/R11/R12 Technician | `P02` `P03` | `SP-010`, `SP-008` | `DT-004` diagnostic report with fault codes and evidence |
| 6 | Estimate | `M36` with `M11` | R09 Workshop Supervisor / R06 Branch Manager | `P03` | `SP-013` | `DT-005` issued; validity clock running (`BRU-SRM-13`) |
| 7 | Obtain approval | `M36` | Customer, plus internal per `SP-004` | `P01` `P04` | `SP-013` | Documented approval above BDT 5,000 (`BRU-SRM-07`), plus branch manager above BDT 25,000 (`BRU-SRM-08`) |
| 8 | Reserve and issue parts | `M15` | R18 Branch Store Keeper | `P03` | `SP-016` | Parts issued only against an approved paid repair (`BRU-SRM-11` / `BRU-INV-01`) |
| 9 | Repair | `M31` / `M02` | Technician at the certified level (`BRU-SRM-14`) | `P02` `P03` | `SP-010`, `SP-008` | Work recorded; before/after photos on warranty jobs (`BRU-SRM-17`) |
| 10 | Quality control | `M23` | R32 Quality Manager / independent second person above BDT 25,000 (`BRU-SRM-18`) | `P03` `P11` | `SP-029`, `SP-032` | `DT-008` checklist passed — mandatory to reach Completed (`BRU-SRM-04`) |
| 11 | Release / deliver | `M04` / `M03` | R08 / R16 | `P03` `P09` | `SP-007`, `SP-009` | `DT-009` release receipt; identity verified; custody chain closed |
| 12 | Invoice | `M20` | R27 Finance Officer (automatic — `AUT-008`) | `P03` | — automated, see §4.9 H-07 | Compliant Mushak 6.3 (`DT-010`) issued; BIN displayed (`BRU-FIN-01`) |
| 13 | Collect and bank | `M20` `M50` | R29 Cashier / R16 Rider | `P03` `P09` | `SP-019` | Receipt issued (`DT-016`); shift reconciled and closed (`BRU-FIN-10`) |
| 14 | Close | `M01` | R09 / R06 | `P03` | `SP-010` | Order Completed; rework flag evaluated (`BRU-SRM-06`) |
| 15 | Feedback | `M34` | R32 / CX | `P01` | `SP-028` | CSAT captured (`AUT-010`); complaints routed to `SP-028` |

**Stream measurement.** Start = stage 1 timestamp. End = stage 13 banking confirmation.
Reported as `KPI-002` (IT equipment TAT < 24h stretch) and `KPI-003` (appliance on-site < 4h
stretch). Stage-level dwell time is the diagnostic; the stream time is the commitment.

### 4.5 VS-2 Procure-to-pay — stage detail

| # | Stage | Owning module | Accountable role | Portal | SOP | Exit condition |
|---:|---|---|---|---|---|---|
| 1 | Identify need | `M43` demand signal · `M15` reorder point | R17 Inventory Manager | `P03` | `SP-017` | `AUT-031` draft requisition exists |
| 2 | Requisition and approve | `M16` | Per `SP-004` value bands | `P03` | `SP-017` | `DT-021` approved; budget reference recorded |
| 3 | Source / RFQ | `M16` with `M42` | R19 Procurement Officer | `P03` `P05` | `SP-017` | `DT-022` issued to active approved vendors only (`BRU-SCM-02`) |
| 4 | Raise purchase order | `M16` | R19 with `SP-004` approval | `P03` `P05` | `SP-017` | `DT-023` transmitted (`AUT-032`) |
| 5 | Receive and inspect | `M41` `M15` | R20 Warehouse Operative | `P03` | `SP-018` | `DT-024` GRN; failed goods to quarantine (`BRU-INV-07`) |
| 6 | Landed cost (imports) | `M44` | R26 Finance Manager | `P03` | `SP-017` | Allocated before final valuation (`BRU-SCM-04`) |
| 7 | Three-way match | `M52` | R27 Finance Officer | `P03` | `SP-017` | Matched within tolerance (`BRU-SCM-01`); exceptions queued |
| 8 | Pay | `M52` `M50` | R26 with `SP-004` approval | `P03` | `SP-017` | TDS deducted at the correct rate (`BRU-FIN-09`); `DT-013` VDS certificate issued where applicable |
| 9 | Vendor performance | `M42` | R19 | `P03` `P05` | `SP-017` | Scorecard updated; `KPI-048` on-time delivery |

### 4.6 VS-3 Hire-to-retire — stage detail

| # | Stage | Owning module | Accountable role | SOP | Exit condition |
|---:|---|---|---|---|---|
| 1 | Position approved vacant | `M58` with `MD-008` | R30 HR Manager | `SP-023` | Requisition approved per `SP-004` |
| 2 | Source and assess | `M58` | R31 HR Officer | `SP-023` | Shortlist with recorded assessment |
| 3 | Offer and contract | `M58` `M21` | R30 | `SP-023` | `DT-042` offer issued and accepted |
| 4 | Join and provision | `M21` `M29` `M30` | R30 + R33 IT Administrator | `SP-023` | `AUT-047` identity, role-from-position, portal access, mandatory training assigned |
| 5 | Train and certify | `M22` | R32 Quality Manager | `SP-023`, `TR-*` | Mandatory training complete (`BRU-LMS-01`); certification current (`BRU-HRM-01`) |
| 6 | Roster and attend | `M55` | R06 Branch Manager | `SP-022` | Attendance verified and locked before payroll (`BRU-HRM-05`) |
| 7 | Perform and reward | `M57` | R30 | `SP-023` | Incentive only above the monthly job threshold (`BRU-HRM-03`) |
| 8 | Pay | `M56` | R26 CFO + R30, two approvals (`BRU-HRM-06`) | `SP-021` | BEFTN file released; payslips distributed (`AUT-046`, `DT-041`) |
| 9 | Exit | `M21` `M29` | R30 + R33 | `SP-023` | Access revoked within one hour (`BRU-SEC-06`, `AUT-048`); clearance issued |

### 4.7 VS-4 Claim-to-reimbursement — stage detail

| # | Stage | Owning module | Accountable role | Portal | SOP | Exit condition |
|---:|---|---|---|---|---|---|
| 1 | Warranty job closes | `M01` `M09` | R10–R12 Technician | `P02` | `SP-014` | Claim auto-created within 24h (`BRU-WTY-02`) |
| 2 | Eligibility check | `M09` | R28 Warranty Claims Officer | `P03` | `SP-014` | Coverage active at request date (`BRU-SRM-02`); not a duplicate within 90 days (`BRU-WTY-03`) |
| 3 | Assemble evidence | `M09` | R28 | `P03` | `SP-014` | `DT-033` pack complete — work order, serial, before-photo, diagnosis, parts list (`BRU-WTY-01`) |
| 4 | Submit to brand | `M09` | R28 | `P08` | `SP-014` | Submitted in the brand's format (`AUT-019`), inside the brand window (`BRU-WTY-08`) |
| 5 | Answer queries | `M09` | R28 | `P08` | `SP-014` | Query closed within the brand's clock |
| 6 | Decision | `M09` | R28 / R26 on rejection | `P08` | `SP-014` | Approved → billing; rejected → dispute task (`AUT-020`) |
| 7 | Bill and reconcile | `M20` `M19` `M50` | R26 Finance Manager | `P03` | `SP-014`, `SP-020` | Remittance matched; unmatched flagged (`AUT-021`) |

### 4.8 VS-5 Lead-to-contract — stage detail

| # | Stage | Owning module | Accountable role | Portal | SOP | Exit condition |
|---:|---|---|---|---|---|---|
| 1 | Lead or renewal signal | `M07` · `M08` renewal at T−90 (`AUT-015`) | R21 Sales Manager / R22 Account Manager | `P03` `P06` | `SP-015` | Opportunity created with a source |
| 2 | Qualify and scope | `M07` `M17` | R22 | `P03` | `SP-015` | Covered-asset list drafted from the device registry |
| 3 | Price and quote | `M36` `M11` | R22 within `SP-004` discount authority | `P03` `P04` | `SP-015` | RAMC priced from registered appliances, never flat (`BRU-CTR-06`) |
| 4 | Approve non-standard terms | `M08` `M60` | Legal + CCO per `SP-004`; **not the negotiator** (`SOD-15`) | `P03` | `SP-015` | Approval recorded before signature |
| 5 | Sign | `M24` | R22 + customer | `P04` | `SP-015` | `DT-030` executed; signed document immutable (`BRU-DMS-03`) |
| 6 | Activate | `M08` | R22 | `P03` `P04` | `SP-015` | Assets, entitlements, billing frequency and approval all present (`BRU-CTR-01`) |
| 7 | Schedule preventive work | `M08` `M02` | R07 Dispatch Manager | `P03` | `SP-015` | Full PM schedule generated for the term (`AUT-016`) |
| 8 | Bill and recognise | `M39` `M53` | R26 | `P03` | `SP-020` | Cycle billed; missed cycle raises an exception, never a silent skip (`BRU-BIL-02`) |

### 4.9 Handovers — where value is lost

A handover is a point where accountability transfers. Each is listed with its failure mode and
the control that stops it. **These are the rows that justify the `06B` SOP set.**

| # | Handover | From → To | Failure mode if uncontrolled | Control | SOP |
|---|---|---|---|---|---|
| H-01 | Request → dispatch | `M01` → `M02` | Job sits in the queue unassigned; SLA consumed silently | `AUT-002` scoring + `AUT-009` escalation at 50/75/90/100% | `SP-005`, `SP-008` |
| H-02 | Customer → company custody | Customer → `M04`/`M03` | Condition disputes at release; the most common customer conflict | `DT-002` signed condition capture + photographs | `SP-007`, `SP-009` |
| H-03 | Branch → workshop | `M04` → `M31` | Device untraceable between two systems of record | Consignment with custody scan (`BRU-SCM-05`, `BRU-LOG-01`) | `SP-009`, `SP-010` |
| H-04 | Diagnosis → estimate | `M31` → `M36` | Estimate not grounded in fault codes; margin lost | `AUT-004` drafts from fault code + `MD-025` standard times | `SP-013` |
| H-05 | Estimate → parts | `M36` → `M15` | Parts issued against unapproved work | `BRU-INV-01` hard block | `SP-016` |
| H-06 | Repair → QC | `M31`/`M02` → `M23` | Self-certified quality; rework and warranty exposure | `SOD-07` + `BRU-SRM-18` independent QC above BDT 25,000 | `SP-029` |
| H-07 | Completion → invoice | `M01` → `M20` | Delivered work never billed — revenue leakage | `BRU-SRM-05` + `AUT-008`; **fully automated, no SOP required** | — |
| H-08 | Invoice → cash | `M20` → `M50` | Cash collected but not banked | Daily reconciliation; unclosed shift blocks the next (`BRU-FIN-10`) | `SP-019` |
| H-09 | Warranty job → claim | `M01` → `M09` | Claim never raised; 15–20% warranty leakage in the baseline | `BRU-WTY-02` auto-create within 24h | `SP-014` |
| H-10 | Claim → brand | `M09` → `P08` | Submitted late or incomplete; claim expires | `BRU-WTY-08` leakage escalation before expiry | `SP-014` |
| H-11 | Requisition → PO | `M16` internal | Spend without authorisation | `SP-004` value bands enforced at the model layer (`BR-STD-01`) | `SP-017` |
| H-12 | Goods → stock | `M41` → `M15` | Unfit goods enter available stock | `BRU-INV-07` quarantine | `SP-018` |
| H-13 | Invoice → payment | `M52` → `M50` | Duplicate or fictitious payment | Three-way match (`BRU-SCM-01`) + `SOD-01`, `SOD-02` | `SP-017` |
| H-14 | Attendance → payroll | `M55` → `M56` | Paying for unverified time | `BRU-HRM-05` lock before finalisation | `SP-021`, `SP-022` |
| H-15 | Payroll → bank | `M56` → `M50` | Preparer releases their own run | `SOD-03` + `SOD-29` three-way prepare/approve/release | `SP-021` |
| H-16 | Leaver → access revocation | `M21` → `M29` | Orphaned accounts; `KPI-090` requires zero beyond 24h | `AUT-048` one-hour revocation (`BRU-SEC-06`) | `SP-023`, `SP-031` |
| H-17 | Van → branch stock | `M02` → `M15` | Van stock is the least-controlled inventory in the company | `AUT-035` shift-end reconciliation; variance to branch manager | `SP-016` |
| H-18 | Trade-in → refurbishment | `M14` → `M31` | Customer data leaves the company on a resold device | `BRU-TRF-01` certified destruction before refurbishment | `SP-025`, `SP-012` |
| H-19 | Scrap → recycling partner | `M18` → external | Environmental non-compliance; certificate unavailable to a corporate client's ESG audit | `BRU-ESG-02` partner certification current at transfer date | `SP-026` |
| H-20 | Complaint → CAPA | `M34` → `M23` | Complaint closed without learning; recurrence | `BRU-QMS-02` root cause + CAPA mandatory before closure | `SP-028`, `SP-029` |
| H-21 | Marketplace job → owned quality standard | `M12` → `M23` | Third-party work damages the 1000FiX brand | `BRU-ECM-03` identical evidence, QC and warranty standards | `SP-024` |
| H-22 | Contract signature → entitlement | `M24` → `M08` | Customer is billed for cover the system does not grant | `BRU-CTR-01` activation preconditions | `SP-015` |

**Twenty-two cross-module handovers. Twenty-one carry an SOP; one (H-07) is fully automated and
is recorded here as deliberately SOP-free** — that is the `PA-03` disclosure, not an omission.

### 4.10 Stream-to-wave mapping

A stream is only useful when it goes live end to end. `06-01` sequences by portal and module;
this table states what that means for streams, and it is the basis of the `TS-003` end-to-end
test scope.

| Stream | First usable in | Complete in | Fragmented across | Risk if a wave slips |
|---|---|---|---|---|
| VS-1 Request-to-cash | **W1** (branch, walk-in) | **W3** (with logistics and payments) | W1 → W3 | The core stream is the company; a slip here delays every other benefit case |
| VS-2 Procure-to-pay | **W3** | **W3** | Single wave | Parts availability (`KPI-043`) stays at baseline, dragging first-time fix |
| VS-3 Hire-to-retire | **W5** | **W5** | Single wave | Payroll stays manual for 500+ employees for a further wave |
| VS-4 Claim-to-reimbursement | **W4** | **W4** | Single wave | 15–20% warranty leakage continues; the largest single recoverable value in the case |
| VS-5 Lead-to-contract | **W2** | **W4** (with `P04` corporate) | W2 → W4 | Contract revenue compounding is deferred; renewals handled manually |

> **Finding for the PMO.** VS-1 is fragmented across three waves and VS-5 across two. Between
> W1 and W3 the request-to-cash stream runs with a manual logistics and payment tail. That
> interim state needs its own transitional SOPs and is **not** currently in the `06B` set —
> raised as a recommendation in `AUDIT-006` §6.

### 4.11 Decisions taken while authoring

Logged here and in `RF-006` per `CG-008`.

| # | Decision | Alternative rejected | Why |
|---|---|---|---|
| D-SP001-1 | Five value streams, not seven | Adding asset-to-disposal and incident-to-resolution as top-level streams | Both are branches/loops, not independent streams. Seven top-level streams would have duplicated the intake and quality stages three times and made §4.9 unreadable |
| D-SP001-2 | Value streams named in the industry-standard idiom (request-to-cash, procure-to-pay) | 1000FiX-specific names | Auditors, consultants and new hires already know these names. `CG-004` terminology governs business objects, not process idioms |
| D-SP001-3 | H-07 recorded as deliberately SOP-free | Writing an SOP for automated invoicing | `PA-03` requires an explicit statement rather than an empty file. Writing an SOP nobody executes is how SOP sets rot |
| D-SP001-4 | Handover control column cites the existing `BRU-` rule, never a new rule | Inventing process-level rules here | `05-05` is the rule register (`RG-01` register-first). A process document that mints rules re-creates finding H2-06 |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `1000fix_ERP_Module/02-01` System map | Module boundaries; a stage cannot cross a module boundary invisibly |
| `1000fix_ERP_Module/02-02` Module register | Canonical `Mnn` identifiers used in §4.4–4.8 |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | The SLA clock that measures VS-1 |
| `05-04` Role matrix | The accountable role per stage; `Rnn` identifiers |
| `05-05` Business rules and automations | Every control in §4.9 |
| `06-01` Roadmap | The wave mapping in §4.10 |
| `06-02` KPI register | Stream measurement points |
| [`SP-003_To_Be_Process_Design_Standard_and_Notation.md`](SP-003_To_Be_Process_Design_Standard_and_Notation.md) | Notation and decomposition depth used in §4.1 |

| Depended on by |
|---|
| All 28 SOPs in `06B` · `SP-002` (baseline is compared stream by stream) · `SP-004` (authority is placed on stages) · `SP-005` (escalation follows the stream) · `TS-003` end-to-end test scenarios · `TR-002` role-based curriculum map · `RP-002` operational KPI definitions · `CM-004` change impact by process |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Every wave boundary, with the `AUDIT_Checklist_Recurring.md` run |
| Trigger for out-of-cycle review | Any module boundary change in `02-02`; any new `BRU-` rule that creates a handover control; any SOP added to or removed from `06B`; any change to `06-01` wave sequencing |
| Owner | Business Process Lead |
| Change control | Structural change (a stream added, a stage re-owned) requires Operations Director approval and a `RF-006` entry |
| Enumeration rule | The "24 modules", "22 handovers" and "28 SOPs" figures in this file are counted from §4.4–4.9 and the `06B` folder, never projected (`CP-11`) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3 — architecture, not a procedure)
- [x] Every factual claim carries a source and a verification date
- [x] Terminology matches `CG-004`
- [x] All internal links resolve
- [x] Every stage names an owning module, an accountable role and an exit condition (`PA-01`)
- [x] Every cross-module handover names a control and an SOP, or states why it needs none (`PA-03`)
- [x] Decisions logged for `RF-006`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Named approver recorded — **pending Operations Director**
- [ ] `SP-002` baseline reconciled stream by stream — **pending `SP-002` field work**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
