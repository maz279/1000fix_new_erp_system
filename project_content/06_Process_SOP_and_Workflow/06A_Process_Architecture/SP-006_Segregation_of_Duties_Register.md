---
id: SP-006
title: Segregation of Duties Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Governance and Security — CFO and CTO jointly accountable
author: Business Process Lead with Governance, Risk and Compliance
reviewers: [CFO, CTO, Internal Audit, Quality Manager, HR Manager, Enterprise Architecture, Legal Counsel]
approver: Chief Financial Officer and Chief Technology Officer, jointly
content_class: C
purpose: >
  The single register of every incompatible duty pair in the 1000FiX ERP, its enforcement point,
  its compensating control where separation is impossible, and its test. Audit 00-07 finding
  H2-06 records that 05-04 §6 registers SOD-01…SOD-12 while module files use SOD-01…SOD-30 —
  eighteen controls used and unregistered. This file closes that finding, and reports two further
  defects found while closing it: nine identifier collisions and 138 incompatible-duty statements
  carrying no identifier at all. An external auditor asking for the SoD matrix must receive one
  document that reconciles with the system.
traces_to: [00-07 H2-06, 05-04 §6, 05-05 BRU-SEC-07, M60, M29, SP-004, SP-002, MD-008, MD-009, NFR-064]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §6 — SOD-01…SOD-12 with risk and enforcement, reproduced verbatim in §4.2
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-07 finding H2-06 and rule RG-01 (extended) — register-first for every programme-wide identifier space including SOD-
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/_MODULE_SET_AUDIT_REPORT.md finding A3-18 — SOD-13…SOD-30 used but never registered, carried from H2-06
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/ — all 67 module files, Segregation of duties sections, extracted 2026-08-15; 61 of 67 carry such a section, 30 distinct SOD- identifiers are in use, 17 statements carry an identifier and 138 do not
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-064 — segregation of duties enforced by the permission engine, priority P0
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 5.3 and clause 9.2 — assigned authorities, and internal audit of the QMS at planned intervals
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SP-006 — Segregation of Duties Register

> **This file closes audit `00-07` finding **H2-06** and module-set finding **A3-18**.**
> It also opens two new findings that closing H2-06 exposed. Both are reported here in full
> rather than fixed silently, per the convention inherited from `00-07`: *the cause matters more
> than the fix.*

---

## 1. Purpose

Segregation of duties is an **audit control**, not documentation. An external auditor, a brand
partner's compliance reviewer, or an ISO 9001 surveillance auditor will ask one question: *show
me your segregation-of-duties matrix, and show me that the system enforces it.*

Today the answer is three inconsistent documents:

| Where | What it says |
|---|---|
| `05-04` §6 | 12 controls, `SOD-01`…`SOD-12`, with risk and enforcement mode |
| 67 module files | 30 distinct `SOD-` identifiers in use, plus 138 further incompatible-duty statements with no identifier |
| `05-06` `NFR-064` | "Segregation of duties enforced by the permission engine" — P0, with no reference to which controls |

`NFR-064` is a P0 non-functional requirement to enforce a set that is not defined. That is the
gap this file closes.

---

## 2. Scope

**In scope:** every incompatible duty pair across the 67 modules and 12 portals; the enforcement
point for each; the compensating control where separation is not achievable; the exception
process; and the testing regime.

**Out of scope**

| Not covered here | Owned by |
|---|---|
| Value thresholds and who may approve | `SP-004` |
| The permission model, roles and record rules | `05-04` §1–§5, `M29` |
| Where an SoD violation escalates | `SP-005` TE-E12 |
| Control testing execution and deficiency management | `M60` GRC |
| Access certification cycles | `AUT-052`, `M29` |

**Register authority.** The Content Master Index §4 (Category 06) designates this file as *"the
register that closes that finding"*. It is therefore **the authoritative SoD register** for the
programme, and `05-04` §6 must be reduced to a pointer to it. Two registers must not both exist —
that is exactly the condition that produced H2-06. Action **RA-06** in §6.

---

## 3. The findings

### 3.1 Finding closed — H2-06 / A3-18: eighteen unregistered controls

`SOD-13`…`SOD-30` were used across module files with no entry in any register. All eighteen are
registered in §4.3 with a definition harvested from the module that uses them, an enforcement
mode and an owner. **Closed.**

### 3.2 New finding SD-01 — nine identifier collisions

**Severity: HIGH.** While harvesting the eighteen definitions, nine `SOD-` numbers were found
carrying **two different meanings in two different module files**.

| ID | Meaning A | Used by | Meaning B | Used by |
|---|---|---|---|---|
| `SOD-15` | Contract negotiator cannot approve its non-standard terms | `M08` | Merge steward cannot have created either record within 24h | `M33` |
| `SOD-16` | Subscription amender cannot approve a credit arising from it | `M39` | Person recording a win cannot approve their own commission attribution change | `M07` |
| `SOD-17` | Return inspector cannot approve a refund above threshold | `M38` | Points-adjustment approver cannot be the requester | `M10` |
| `SOD-18` | MDF allocator cannot approve a claim against it | `M40` | Wallet payout approval separated from wallet credit creation | `M10` |
| `SOD-19` | CAPA performer cannot verify its effectiveness | `M23` | A supervisor cannot evaluate their own handled conversations | `M27` |
| `SOD-20` | An auditor cannot audit their own area or prior work | `M23` | Guard-rail author cannot be sole approver of its removal | `M32` |
| `SOD-21` | Control owner cannot record the test conclusion for their own control | `M60` | Person whose score is under anomaly investigation cannot participate in it | `M34` |
| `SOD-22` | SoD-exception grantor cannot be its beneficiary | `M60` | Compensation approval separated from complaint ownership above the branch threshold | `M34` |
| `SOD-23` | Disposal-batch preparer cannot approve it | `M24` | Campaign builder cannot approve it above threshold | `M35` |

**Why it matters.** These are not naming inconveniences. `M60` will *test* `SOD-21` as
"control owner cannot conclude on their own control" and report it green. `M34` will believe its
CSAT anomaly control is tested. It is not. A collided identifier produces **false assurance**,
which is worse than an absent control, because nobody looks for it.

**Why it happened.** Each module author wrote `(to be registered in 05-04 §6)` and took the next
number that looked free from their own vantage point. There was no allocation authority for the
`SOD-` space. This is the identical failure mode as `00-07` H2-04/H2-05 (custom-development and
KPI identifier collisions) and portal audit X-01, and it is the reason rule `RG-01` was extended
to every programme-wide identifier space. **The `SOD-` space is the one where the rule was
extended but never applied.**

**Resolution.** Meaning **A** retains the original number in every case — chosen because in eight
of the nine, module A explicitly claimed registration with `(to be registered in 05-04 §6)`.
Meaning **B** is reallocated to `SOD-31`…`SOD-39` in §4.4. The nine module files must be
corrected; action **RA-07**.

### 3.3 New finding SD-02 — 138 incompatible-duty statements carry no identifier at all

**Severity: HIGH.** Sixty-one of the 67 module files carry a **Segregation of duties** section.
Extracting every list or table item from those sections on 2026-08-15:

| | Count |
|---|---:|
| Statements carrying an `SOD-` identifier | 17 |
| Statements carrying **no identifier** | **138** |

A statement such as *"the requester of a bank-detail change cannot approve it"* (`M42`) is a
high-value anti-fraud control — vendor bank-detail substitution is one of the most common payment
frauds in any ERP. It has no identifier, so it cannot be tested by `M60`, cannot be reported to an
auditor, and cannot be configured deliberately in the permission engine. It will be implemented
if the developer reading `M42` notices it, and not otherwise.

**Resolution.** The 21 highest-consequence statements — those touching cash, custody, statutory
records, asset write-off or personal data — are registered here as `SOD-40`…`SOD-60`. The
remainder are scheduled for harvest and de-duplication into `SOD-61` onwards before W1 build;
action **RA-08**.

> The register is therefore **complete for the controls it names and explicitly incomplete for
> the rest**, with the incompleteness quantified. That is a better position than an apparently
> complete register of twelve.

---

## 4. The register

### 4.1 How to read it

| Column | Meaning |
|---|---|
| **ID** | Permanent. Never reused, never renumbered (`CP-02`, `RG-01`) |
| **Duty A / Duty B** | The two duties that may not be held by the same natural person for the same transaction |
| **Risk** | What happens if they are combined |
| **Mode** | **Hard block** — the engine refuses · **Threshold** — blocked above a value · **Warning + approval** — permitted with recorded authorisation · **Detective** — not preventable; found by report |
| **Point** | Where enforcement happens: *assignment* (at role grant), *transaction* (at the action), or *report* |
| **Owner** | Accountable for the control being in force and tested |

**Rule SD-R1.** "The same natural person" — not the same role, not the same team. Two people
holding the same role satisfy separation. One person holding two roles does not.

**Rule SD-R2.** Separation applies **to the same transaction or record**, not to the duty in
general. A Finance Manager may approve credit notes and may create credit notes — but never both
on the same credit note (`SOD-04`).

**Rule SD-R3.** Enforcement at *assignment* is strongest and is preferred wherever the duties are
never legitimately combined. Enforcement at *transaction* is used where a role must hold both
capabilities for different records. `05-04` §6 already specifies that the permission engine
evaluates SoD at role assignment and blocks incompatible combinations; this register extends the
same mechanism.

**Rule SD-R4.** A control whose mode is **Detective** is not a weaker control by choice — it is
one where prevention is technically impossible. Every detective control names the report, its
frequency and its reviewer, or it is not a control.

### 4.2 `SOD-01` … `SOD-12` — reproduced from `05-04` §6

Reproduced **verbatim**. Where this file adds a column `05-04` does not have (Point, Owner), the
addition is marked ⊕.

| ID | Duty A + Duty B | Risk | Mode | Point ⊕ | Owner ⊕ |
|---|---|---|---|---|---|
| `SOD-01` | Create vendor + approve vendor invoice | Fictitious vendor payment | Hard block | Assignment | CFO |
| `SOD-02` | Raise purchase order + receive goods + approve invoice | Purchase fraud | Hard block (any two permitted, not all three) | Assignment | CFO |
| `SOD-03` | Process payroll + approve payroll | Payroll fraud | Hard block | Assignment | CFO |
| `SOD-04` | Create credit note + approve credit note | Revenue leakage | Hard block | Transaction | CFO |
| `SOD-05` | Adjust inventory + perform the count that justifies it | Inventory theft concealment | Hard block | Transaction | CFO |
| `SOD-06` | Approve marketplace seller + approve their payout | Collusion | Hard block | Assignment | CFO |
| `SOD-07` | Repair a device + perform its independent QC | Quality concealment | Hard block above value threshold | Transaction | Quality Manager |
| `SOD-08` | Create customer + approve their credit limit | Credit fraud | Warning + approval | Transaction | CFO |
| `SOD-09` | Administer users + approve access requests for self | Privilege escalation | Hard block | Transaction | CTO |
| `SOD-10` | Value a trade-in + purchase it + resell it | Asset misappropriation | Hard block | Assignment | CFO |
| `SOD-11` | Raise a warranty claim + approve its write-off | Claim manipulation | Hard block | Transaction | CFO |
| `SOD-12` | Handle cash + reconcile the cash book | Cash misappropriation | Hard block | Assignment | CFO |

### 4.3 `SOD-13` … `SOD-30` — registered here, closing H2-06

Definitions harvested from the module that uses the identifier. Where a collision existed, the
**meaning A** definition from §3.2 is the one registered.

| ID | Duty A + Duty B | Risk | Mode | Point | Owner | Harvested from |
|---|---|---|---|---|---|---|
| `SOD-13` | Author a catalogue item change + approve that change | Unreviewed price, scope or specification entering the catalogue | Hard block | Transaction | CCO | `M37` (`BRU-CAT-05`) |
| `SOD-14` | Propose a price change or below-floor discount + approve it | Margin erosion by a single actor | Hard block | Transaction | CCO | `M11` (`FR-PRC-035`) |
| `SOD-15` | Negotiate a contract + approve its non-standard terms | Terms conceded to win a deal, unreviewed | Hard block | Transaction | CCO + Legal | `M08` |
| `SOD-16` | Amend a subscription + approve a credit arising from that amendment | Revenue leakage through self-served credits | Hard block | Transaction | CFO | `M39` |
| `SOD-17` | Inspect a return + approve the refund above the threshold | Refund fraud | Threshold | Transaction | CFO | `M38` |
| `SOD-18` | Allocate partner MDF + approve a claim against it | Channel-funds misappropriation | Hard block | Transaction | CFO | `M40` |
| `SOD-19` | Perform a CAPA action + verify its effectiveness | Ineffective corrective action closed as effective | Hard block | Transaction | Quality Manager | `M23` (`BRU-QMS-03`) |
| `SOD-20` | Audit an area + be responsible for that area or its prior work | Loss of audit independence — an ISO 9001 clause 9.2 requirement | Hard block | Assignment | Quality Manager | `M23` |
| `SOD-21` | Own a control + record the test conclusion for that control | False assurance in the control framework | Hard block | Transaction | CFO | `M60` |
| `SOD-22` | Grant an SoD exception + be the beneficiary of it | The exception process defeats itself | Hard block | Transaction | CFO / CTO | `M60` |
| `SOD-23` | Prepare a records-disposal batch + approve it | Premature or unlawful destruction of records | Hard block | Transaction | Quality Manager + Legal | `M24` |
| `SOD-24` | Own a campaign + approve its budget | Marketing spend without independent challenge | Hard block | Transaction | CFO | `M35` |
| `SOD-25` | Create an employee record + approve that employee's salary structure | Ghost employee, or inflated pay | Hard block | Transaction | CFO | `M21` |
| `SOD-26` | Process a retrospective effective-date change + approve it | Backdated entitlement or pay | Hard block | Transaction | HR Manager | `M21` |
| `SOD-27` | Request overtime + approve it | Payroll inflation | Hard block | Transaction | HR Manager | `M55` (`BRU-HRM-02`) |
| `SOD-28` | Verify an attendance period + regularise the exceptions within it above the threshold count | Unverified time paid | Threshold | Transaction | HR Manager | `M55` |
| `SOD-29` | Approve a payroll run + release the bank file | Payment diversion after approval | Hard block | Transaction | CFO | `M56` |
| `SOD-30` | Calculate an incentive (`M57`) + disburse it (`M56`) | Self-directed incentive payment | Hard block | Assignment | CFO | `M56`, `M57` |

### 4.4 `SOD-31` … `SOD-39` — collision resolution (finding SD-01)

The **meaning B** controls from §3.2, reallocated to their own identifiers. **The nine module
files must be corrected to cite these numbers** — action `RA-07`.

| ID | Duty A + Duty B | Risk | Mode | Point | Owner | Corrects the citation in |
|---|---|---|---|---|---|---|
| `SOD-31` | Execute a party-record merge + have created either record within the preceding 24 hours | Fabricated duplicate merged to obscure a record | Hard block | Transaction | MDM Lead | `M33` (currently cites `SOD-15`) |
| `SOD-32` | Record a sales win + approve a change to its own commission attribution | Commission manipulation | Hard block | Transaction | CFO | `M07` (currently cites `SOD-16`) |
| `SOD-33` | Request a loyalty-points adjustment + approve it | Points issued to self or an accomplice | Hard block | Transaction | CCO | `M10` (currently cites `SOD-17`) |
| `SOD-34` | Create a wallet credit + approve the wallet payout | Cash-equivalent misappropriation | Hard block | Transaction | CFO | `M10` (currently cites `SOD-18`) |
| `SOD-35` | Handle a conversation + perform its quality evaluation | Self-scored quality; `KPI-027` becomes unreliable | Hard block | Transaction | Contact Centre Supervisor | `M27` (currently cites `SOD-19`) |
| `SOD-36` | Author an AI guard rail + be the sole approver of its removal | A safety, pricing or certification guard rail removed by one person (`BRU-AIM-02`) | Hard block | Transaction | CTO | `M32` (currently cites `SOD-20`) |
| `SOD-37` | Be the subject of a score-anomaly investigation + participate in that investigation | Suppressed finding | Hard block | Transaction | Quality Manager | `M34` (currently cites `SOD-21`) |
| `SOD-38` | Own a complaint + approve compensation on it above the branch threshold | Compensation used to close a complaint quietly | Threshold | Transaction | CCO | `M34` (currently cites `SOD-22`) |
| `SOD-39` | Build a campaign + approve it above the threshold | Unreviewed customer communication and spend | Threshold | Transaction | CCO | `M35` (currently cites `SOD-23`) |

### 4.5 `SOD-40` … `SOD-60` — the highest-consequence unnumbered controls (finding SD-02)

Twenty-one controls that existed in module text with no identifier. Selected because each touches
cash, custody, a statutory record, an asset write-off or personal data.

| ID | Duty A + Duty B | Risk | Mode | Point | Owner | From |
|---|---|---|---|---|---|---|
| `SOD-40` | Request a vendor bank-detail change + approve it | **Payment diversion — the single most common ERP payment fraud** | Hard block | Transaction | CFO | `M42` |
| `SOD-41` | Prepare a journal entry + approve it | Unreviewed ledger manipulation (`BRU-FIN-11`) | Hard block, any value | Transaction | CFO | `M19` |
| `SOD-42` | Hold posting rights + administer posting rules | The rules that constrain posting altered by the poster (`BRU-FIN-25`) | Hard block | Assignment | CFO | `M19` |
| `SOD-43` | Reopen an accounting period + post into it | Retrospective result manipulation | Hard block | Transaction | CFO | `M19` |
| `SOD-44` | Raise an inter-branch stock transfer + approve it above the value threshold | Stock diversion between 51+ locations | Threshold | Transaction | Inventory Manager | `M15` |
| `SOD-45` | Quarantine stock + approve its write-off | Good stock written off and removed | Hard block | Transaction | Inventory Manager | `M15` |
| `SOD-46` | Raise a purchase requisition + approve it | Self-authorised spend | Hard block, any value | Transaction | CFO | `M16` |
| `SOD-47` | Award a sourcing event + approve the resulting purchase order above the competitive threshold | Directed award | Threshold | Transaction | Procurement Manager | `M16` |
| `SOD-48` | Override a put-away directive + approve the override | Stock placed where it is not recorded | Hard block | Transaction | Inventory Manager | `M41` |
| `SOD-49` | Record an assessed customs duty + be the sole approver of a duty-variance acceptance | Understated landed cost; statutory exposure | Hard block | Transaction | CFO | `M44` |
| `SOD-50` | Classify an HS code + approve its reclassification | Duty avoidance | Hard block | Transaction | CFO + Legal | `M44` |
| `SOD-51` | Report an asset lost or damaged + approve its write-off | Asset misappropriation (`BRU-EAM-12`) | Hard block | Transaction | CFO | `M45` |
| `SOD-52` | Perform a calibration + approve a change to that instrument's calibration status | Out-of-calibration equipment declared fit; every measurement taken with it is void | Hard block | Transaction | Quality Manager | `M45` |
| `SOD-53` | Report a vehicle incident as the driver + close the resulting insurance claim | Claim manipulation | Hard block | Transaction | CFO | `M46` |
| `SOD-54` | Flag an asset lost or stolen + clear that flag | Stolen device laundered back into the registry | Hard block | Transaction | Inventory Manager | `M17` |
| `SOD-55` | Inspect a rental asset on return + approve the damage charge | Charge inflated or suppressed | Hard block | Transaction | Retail Manager | `M13` |
| `SOD-56` | Perform refurbishment QA + approve a grade override | Grade ceases to be an independent measurement (`BRU-TRF-05`) | Hard block | Transaction | Quality Manager | `M14` |
| `SOD-57` | Triage an item for disposal + authorise its transfer to a recycling partner | An item declared worthless and removed by one person | Hard block | Transaction | Quality Manager | `M18` |
| `SOD-58` | Perform a data destruction + witness it | The destruction certificate requires two distinct identities (`BRU-DTS-01`); corporate and regulatory evidence | Hard block | Transaction | CTO + Legal | `M06` |
| `SOD-59` | Execute a change in a client environment + be its sole approver | Unreviewed change to a customer's estate (`BRU-RMS-08`) | Hard block | Transaction | CTO | `M05` |
| `SOD-60` | Impose a marketplace consequence + decide the appeal against it | No effective appeal (`BRU-MKP-18`) | Hard block | Transaction | Marketplace Operations | `M12` |

**Register total: 60 controls.** 12 reproduced · 18 registered closing H2-06 · 9 collision
reallocations · 21 harvested from unnumbered statements.

### 4.6 Where separation is impossible — compensating controls

`SP-002` §4.3 identifies branch clusters **C4** (district, single-shift, 15–20 branches) and
**C5** (kiosk, 4–8 sites) where one person routinely performs intake, holds cash and closes the
day. `SOD-12` is violated at those sites **today, structurally, by the staffing model.**

Two responses were considered:

| Option | Rejected because |
|---|---|
| Weaken `SOD-12` to a warning network-wide | Degrades the control at the 30+ sites where separation *is* achievable, to accommodate the sites where it is not. `PD-09` forbids designing to the smallest site |
| Staff every site to two people | Not a decision this register can make; it is a commercial one with a headcount cost |

**Adopted: site-scoped compensating controls, time-boxed and reported.**

| # | Rule |
|---|---|
| **CC-01** | A compensating control is **site-scoped and named**, recorded against the branch in `MD-003`, never a global relaxation |
| **CC-02** | Every compensating control has an **expiry date** and is re-approved, not renewed by default |
| **CC-03** | The compensating control must be **independent of the person it compensates for**. A checklist signed by the same person is not a control |
| **CC-04** | Compensating controls are listed on the **monthly SoD exception report** to the CFO and Internal Audit, by site |
| **CC-05** | A site under a compensating control is **prioritised in the internal audit plan** (`SP-029`) |

**The compensating control set for single-person sites**

| Violated control | Compensating control | Independent because |
|---|---|---|
| `SOD-12` cash handling + reconciliation | Daily blind cash declaration submitted before the system balance is visible to the declarer; variance auto-reported to R06 Branch Manager at another site and to Finance | The declarer cannot see the expected figure |
| `SOD-12` (cont.) | Weekly surprise count by the cluster manager or a `P11` field auditor | Performed by someone who is not at the site |
| `SOD-05` adjust + count | Adjustments above zero value are **routed to R17 Inventory Manager** for approval, always, at these sites — no local threshold | Approval leaves the site entirely |
| `SOD-07` repair + QC | Photographic QC evidence reviewed remotely by R09 Workshop Supervisor for every job above the threshold | The reviewer is remote and independent |
| `SOD-01` / `SOD-46` procurement | Local purchasing capability removed entirely; all spend routed to central procurement | The duty does not exist locally |

> **Note the pattern:** every compensating control either (a) removes the duty from the site, or
> (b) moves the second duty to an independent person elsewhere. It never asks the same person to
> check themselves more carefully. A control that relies on the diligence of the person it
> constrains is not a control.

### 4.7 The exception process

| # | Rule |
|---|---|
| **EX-01** | An SoD exception is granted only by **CFO or CTO** (`05-04` §7, `SP-004` A-87) |
| **EX-02** | The grantor may **not** be the beneficiary (`SOD-22`) |
| **EX-03** | Every exception is **time-boxed**. There is no permanent exception |
| **EX-04** | Every exception states the **compensating control** that applies for its duration |
| **EX-05** | Exceptions appear on a **standing exception report reviewed quarterly** (`05-04` §6) and on the monthly report to Internal Audit |
| **EX-06** | An exception on a **hard-block** control additionally requires Internal Audit to be informed before it takes effect, not after |
| **EX-07** | Exception count is a **governance metric**. A rising count is a finding for `M60`, not an administrative fact |
| **EX-08** | On expiry the access is **removed automatically**, not on a reminder |

### 4.8 Enforcement and testing

| Layer | What it does |
|---|---|
| **Role assignment** (`M29`) | Evaluates every assignment-point control at grant and blocks the combination (`05-04` §6, `BRU-SEC-07`) |
| **Transaction** (model layer) | Evaluates transaction-point controls at the action. Enforced at the model layer, never only in the UI (`BR-STD-01`) — an SoD rule bypassable by API is not a rule |
| **Access certification** (`AUT-052`) | Managers re-confirm access each cycle; unconfirmed access is revoked at the deadline |
| **Control testing** (`M60`) | Tests each control, including by **controlled violation attempt** with a deliberately mis-provisioned account |
| **Detective reports** | For the controls that cannot be prevented, per `SD-R4` |
| **Internal audit** (`SP-029`) | Samples the operation of the controls, not only their configuration |

**Testing gap.** `M60` acceptance criterion **AC-07** currently reads *"All twelve SoD rules from
`05-04` §6 are tested"*. With this register at **60** controls, AC-07 tests **20%** of them and
will report a pass. `M60` AC-07 must be restated to reference this register rather than a count —
action `RA-09`. Left uncorrected it produces the same false assurance as finding SD-01, at scale.

### 4.9 What is deliberately not segregated

| Combination | Why it is permitted |
|---|---|
| Diagnose a fault + perform the repair | The same technician doing both is the efficient design; the control is independent QC (`SOD-07`), not diagnostic separation |
| Take a booking + create the service order | Separating them would break the 3-minute intake target for no fraud benefit |
| Approve credit notes generally + create credit notes generally | `SD-R2` — the control is per-record (`SOD-04`), not per-capability |
| Hold two roles whose duties never intersect | SoD constrains conflicting duties, not multi-skilling. Over-application makes small sites unworkable and drives shared logins, which destroys accountability entirely |

> The last row matters. An SoD register applied without judgement produces password sharing.
> Every control in §4.2–4.5 earns its place by naming a specific risk.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-04` §6 | Source of `SOD-01`…`SOD-12`; must be reduced to a pointer (`RA-06`) |
| `05-04` §7 / [`SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](SP-004_Approval_Matrix_and_Delegation_of_Authority.md) | Exception authority; delegation may not cross an SoD boundary (`DL-04`) |
| [`SP-002_As_Is_Process_Baseline_Register.md`](SP-002_As_Is_Process_Baseline_Register.md) | Identifies the sites where separation is structurally impossible |
| [`SP-005_Escalation_Matrix.md`](SP-005_Escalation_Matrix.md) | TE-E12 — detected violation escalation |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-008_Organisation_Structure_and_Position_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-008_Organisation_Structure_and_Position_Master.md) | Resolves duties to positions |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md) | Role-to-duty mapping |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-003_Branch_and_Service_Centre_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-003_Branch_and_Service_Centre_Master.md) | Site-scoped compensating controls (`CC-01`) |
| `M29`, `M60` | Enforcement and testing |

| Depended on by |
|---|
| All 28 SOPs in `06B` §11 tables · `M29` permission engine configuration · `M60` control testing · `TS-007` SoD negative tests · `SP-029` internal audit plan · `RP-009` governance reporting · `NFR-064` |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly with the exception report; fully re-validated annually |
| Trigger for out-of-cycle review | A new module; an organisational restructure; a fraud or near-miss; an external audit finding; any module file introducing an incompatible-duty statement |
| Owner | CFO and CTO jointly |
| Change control | Adding a control requires CFO or CTO approval; **removing or weakening one requires both, plus Internal Audit's written non-objection**. Logged in `RF-006` |
| Allocation authority | **`SOD-` identifiers are allocated only by the owner of this file.** No module file may introduce one (`RG-01`). This is the rule whose absence caused SD-01 |

**Actions raised**

| # | Action | Owner | Needed by | Finding |
|---|---|---|---|---|
| RA-05 | Ratify this register as the authoritative SoD matrix for the programme | CFO + CTO | Before W1 build | H2-06 |
| RA-06 | Reduce `05-04` §6 to a pointer to this file, so two registers do not coexist | Enterprise Architecture | Before W1 build | H2-06 |
| RA-07 | Correct the nine module files citing collided identifiers to `SOD-31`…`SOD-39` (`M33`, `M07`, `M10` ×2, `M27`, `M32`, `M34` ×2, `M35`) | Module owners via Enterprise Architecture | **Before W1 build — false assurance until done** | SD-01 |
| RA-08 | Harvest and de-duplicate the remaining unnumbered incompatible-duty statements into `SOD-61` onwards | GRC with Business Process Lead | Before W1 build | SD-02 |
| RA-09 | Restate `M60` acceptance criterion AC-07 to reference this register rather than "all twelve" | Quality Manager + CTO | Before W1 build | §4.8 |
| RA-10 | Configure the permission engine against the 60 registered controls and prove each by controlled violation attempt | CTO with `M29` team | W1 build | `NFR-064` |
| RA-11 | Approve the §4.6 compensating control set and record it per site in `MD-003` | CFO + Operations Director | Before W1 go-live | `SOD-12` structural violation |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3)
- [x] `SOD-01`…`SOD-12` reproduced verbatim from `05-04` §6, additions marked
- [x] `SOD-13`…`SOD-30` registered with harvested definitions — **closes H2-06 / A3-18**
- [x] Identifier collisions found, reported as finding SD-01 and resolved as `SOD-31`…`SOD-39`
- [x] Unnumbered statements counted (138), reported as finding SD-02, top 21 registered as `SOD-40`…`SOD-60`
- [x] Every control carries a risk, a mode, an enforcement point and an owner
- [x] Compensating controls specified for sites where separation is structurally impossible
- [x] Exception process specified, time-boxed, with the grantor-beneficiary exclusion
- [x] Testing gap in `M60` AC-07 identified
- [x] Deliberate non-segregation stated, with the shared-login argument
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] RA-05 ratified by CFO and CTO — **outstanding; blocks `Approved`**
- [ ] RA-06 `05-04` §6 reduced to a pointer — **outstanding; two registers currently coexist**
- [ ] RA-07 nine module citations corrected — **outstanding; false assurance until done**
- [ ] RA-08 remaining statements harvested — **outstanding; register explicitly incomplete**
- [ ] RA-09 `M60` AC-07 restated — **outstanding**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
