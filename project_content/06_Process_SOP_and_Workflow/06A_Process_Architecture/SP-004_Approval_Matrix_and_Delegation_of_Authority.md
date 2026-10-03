---
id: SP-004
title: Approval Matrix and Delegation of Authority
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance and Governance — CFO accountable
author: Business Process Lead with Finance and Governance
reviewers: [CFO, CEO, CCO, CTO, Operations Director, HR Manager, Quality Manager, Legal Counsel, Internal Audit]
approver: Chief Financial Officer, ratified by the Board
content_class: C
purpose: >
  States who may approve what, to what value, in whose absence, and what happens when nobody
  with authority is available. Estimates, discounts, purchases, credit notes, write-offs,
  refunds, compensation, payroll, access and configuration changes all need an authority limit
  configured in the workflow engine before W1 build. Without this file the engine is configured
  from thresholds scattered across eleven module specifications, and the delegation rules — which
  exist nowhere today — are invented per branch.
traces_to: [05-04 §7, 05-05, M60, M24, SP-001, SP-005, SP-006, MD-008, MD-009, NT-022]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §7 Approval Authority Matrix — 28 rows, enumerated 2026-08-15; the canonical source for every threshold restated here
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2–§11 business rules carrying an approval consequence (BRU-SRM-07/08, BRU-FIN-04/06, BRU-INV-06, BRU-HRM-06, BRU-CTR-08, BRU-RNT-03, BRU-TRF-05, BRU-ADM-01/02, BRU-SEC-05)
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §Governance — SoD exception authority (CFO or CTO, time-boxed)
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 5.3 — organisational roles, responsibilities and authorities assigned, communicated and understood
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SP-004 — Approval Matrix and Delegation of Authority

> ⚠ **`05-04` §7 is the source. This file does not compete with it.**
> Every threshold in §4.2 that already exists in `05-04` §7 is reproduced **verbatim** and marked
> **`[05-04]`**. Rows marked **`[NEW]`** are authorities the programme needs and `05-04` §7 does
> not contain — they are proposed here and must be **registered into `05-04` §7 before W1 build**,
> not left to live only in this file. That is rule `RG-01` register-first, applied honestly:
> a process document may not become a second, competing authority register.

---

## 1. Purpose

The workflow engine cannot be configured from prose. Before W1 build, someone must answer, for
every value-bearing decision in the company: **who, up to what, and what happens if they are on
leave.**

`05-04` §7 answers the first two questions for 28 transaction types. It does not answer the
third at all, and it is silent on 64 further decision types that carry money or risk. This file:

1. **consolidates** every approval threshold in the programme into one table, citing its source;
2. **identifies the gaps** in `05-04` §7 and proposes the missing authorities;
3. **defines delegation** — absence, acting-up, time-boxing, revocation — which currently exists
   nowhere in the programme documentation;
4. **defines the anti-avoidance rules** without which value bands are decorative.

---

## 2. Scope

**In scope:** every decision in the 1000FiX ERP that requires a named person to authorise it,
across service, commercial, supply chain, finance, people, quality, data and platform.

**Out of scope**

| Not covered here | Owned by |
|---|---|
| Which duties may not be combined in one person | `SP-006` Segregation of Duties Register |
| Where an unanswered approval escalates, and how fast | `SP-005` Escalation Matrix |
| The permission model that enforces these limits technically | `05-04` §2–§5, `M29`, `M30` |
| Approval request and reminder wording | `NT-022` |
| Position and reporting-line data that delegation resolves against | `MD-008`, `MD-009` |
| Board-reserved matters and statutory director authority | Company constitution — outside the ERP |

---

## 3. Audience

CFO and Finance (owners), configuration engineers building the workflow engine, every manager
who holds or exercises authority, internal and external auditors, and the authors of the 28 SOPs
in `06B` — whose §7 "Approvals and Authority Limits" table must reconcile with this file exactly.

---

## 4. Content

### 4.1 Principles

| # | Principle | Consequence |
|---|---|---|
| **AA-01** | **Authority attaches to a position, never to a person** | `MD-008` positions carry limits. A person inherits their position's limit. A leaver's authority disappears with their position assignment, not with a manual cleanup |
| **AA-02** | **Limits are configuration, not code** (`BR-STD-03`) | Every figure here is a configured parameter with an effective date. Changing one is a change record, not a release |
| **AA-03** | **Enforced at the model layer** (`BR-STD-01`) | An approval limit bypassable by an API call is not a limit |
| **AA-04** | **No self-approval, at any value** | A requester is never their own approver, even where their own limit would cover it. Enforced technically, not by convention |
| **AA-05** | **Splitting to avoid a threshold is a breach** | §4.5 defines detection. This is the single most common circumvention of any approval matrix |
| **AA-06** | **Every approval and every rejection is recorded with a reason and a timestamp** (`BR-STD-06`) | An approval with no recorded basis is not evidence |
| **AA-07** | **Absence never removes the control** | Delegation moves the authority to a named alternate; it never lowers the threshold or skips the step (§4.6) |
| **AA-08** | **Cumulative authority is bounded** | Holding two positions does not sum their limits; the higher applies, never the total |
| **AA-09** | **Overrides exist only where designed** (`BR-STD-06`) | A rule of class **H** cannot be approved around. Only class **A** rules have an override path, and the override is logged with reason and approver |
| **AA-10** | **The matrix is one document** | An SOP restating a limit in its own words creates a second version. SOPs cite `SP-004 §<band>` (`PD-13`) |

### 4.2 The consolidated approval matrix

Currency is BDT throughout. **`[05-04]`** = reproduced from `05-04` §7 without change.
**`[NEW]`** = proposed here; not yet in `05-04` §7; requires registration before W1 build.

#### 4.2.1 Service and repair

| # | Decision | Threshold | Approver | Source |
|---|---|---|---|---|
| A-01 | Repair estimate | Any | Customer | `[05-04]` |
| A-02 | Repair estimate | > 5,000 | Customer + system record | `[05-04]` `BRU-SRM-07` |
| A-03 | Repair estimate | > 25,000 | Customer + R06 Branch Manager | `[05-04]` `BRU-SRM-08` |
| A-04 | Repair estimate | > 100,000 | Customer + R05 Operations Director | `[05-04]` |
| A-05 | **Revised estimate — variation** | Cumulative total crosses a band | **Re-approval at the band of the cumulative total, not the delta** | `[NEW]` — closes the most common scope-growth dispute (`DT-006`) |
| A-06 | **Beyond economic repair declaration** | Any | R09 Workshop Supervisor + a second technician, with photographic evidence | `[NEW]` from `BRU-SRM-12` (rule exists; approver never named) |
| A-07 | **Reopen a closed order outside the repair warranty period** | Any | R06 Branch Manager | `[NEW]` — `BRU-SRM-19` is class **A**; the override approver was unnamed |
| A-08 | **Waive or reduce a diagnostic / call-out fee** | ≤ 1,000 | R08 Service Centre Agent | `[NEW]` |
| A-09 | Same | > 1,000 | R06 Branch Manager | `[NEW]` |
| A-10 | **Dispose of an uncollected device after the abandonment notice period** | Any | R06 Branch Manager + Legal Counsel | `[NEW]` from `BRU-SRM-16`; carries statutory notice consequence — see `LG-014` |

#### 4.2.2 Commercial, pricing and contract

| # | Decision | Threshold | Approver | Source |
|---|---|---|---|---|
| A-11 | Discount | ≤ 10% | R08 Service Centre Agent | `[05-04]` |
| A-12 | Discount | ≤ 20% | R06 Branch Manager | `[05-04]` |
| A-13 | Discount | ≤ 35% | R21 Sales Manager | `[05-04]` |
| A-14 | Discount | > 35% | CCO | `[05-04]` |
| A-15 | **Below price-floor sale** | Any | CCO — **never the proposer** (`SOD-14`) | `[NEW]` from `M11` `FR-PRC-035` |
| A-16 | **Price list / rate card change** | Any | CCO on CFO recommendation; proposer excluded (`SOD-14`) | `[NEW]` |
| A-17 | Contract — standard terms | Any value | R21 Sales Manager | `[05-04]` |
| A-18 | Contract — non-standard terms | Any value | CCO + CFO | `[05-04]` |
| A-19 | **Contract non-standard terms — the negotiator is excluded** | Any | Approver must not be the account manager who negotiated (`SOD-15`) | `[NEW]` from `M08` |
| A-20 | **Service credit — automatic from measured breach** | Any | None — computed (`BRU-CTR-08`, class **C**) | `[05-04]`-adjacent |
| A-21 | **Service credit — manual** | Any | CFO | `[NEW]` from `BRU-CTR-08` (rule exists; not in §7) |
| A-22 | **Contract suspension for non-payment** | Any | CFO, only after the defined notice sequence (`BRU-CTR-05`) | `[NEW]` |
| A-23 | **Subscription amendment credit** | Any | Not the person who amended (`SOD-16`) | `[NEW]` |

#### 4.2.3 Finance

| # | Decision | Threshold | Approver | Source |
|---|---|---|---|---|
| A-24 | Credit note | ≤ 10,000 | R27 Finance Officer | `[05-04]` |
| A-25 | Credit note | > 10,000 | R26 Finance Manager | `[05-04]` `BRU-FIN-04` |
| A-26 | **Credit note — creator excluded** | Any | Creator may never approve (`SOD-04`) | `[05-04]` §6 |
| A-27 | **Customer refund** | ≤ 10,000 | R26 Finance Manager | `[NEW]` — refunds are not in `05-04` §7 at all |
| A-28 | **Customer refund** | > 10,000 | CFO | `[NEW]` |
| A-29 | **Refund to a method other than the original** | Any | CFO (`BRU-BIL-05` allows store credit only with customer consent) | `[NEW]` |
| A-30 | **Bad-debt write-off** | ≤ 50,000 | R26 Finance Manager | `[NEW]` |
| A-31 | **Bad-debt write-off** | > 50,000 | CFO; > 500,000 CFO + CEO | `[NEW]` |
| A-32 | **Reopen a hard-closed accounting period** | Any | CFO, logged (`BRU-FIN-06`) | `[NEW]` |
| A-33 | **Manual journal entry** | ≤ 100,000 | R26 Finance Manager | `[NEW]` |
| A-34 | **Manual journal entry** | > 100,000 | CFO | `[NEW]` |
| A-35 | **Manual invoice for a completed job** | Any | R26 Finance Manager (`BRU-BIL-01`, class **A**) | `[NEW]` |
| A-36 | **Deferred revenue manual release** | Any | CFO (`BRU-BIL-06`) | `[NEW]` |
| A-37 | **Cash receipt without NID above the reporting threshold** | > 50,000 | Blocked — class **H** (`BRU-FIN-02`). **No approval path exists** | `[05-04]`-adjacent |
| A-38 | **Petty cash / branch float replenishment** | ≤ 25,000 | R06 Branch Manager | `[NEW]` |
| A-39 | **Employee expense claim** | ≤ 10,000 | Line manager | `[NEW]` |
| A-40 | **Employee expense claim** | > 10,000 | Line manager + R26 Finance Manager | `[NEW]` |
| A-41 | **Budget virement between cost centres** | ≤ 500,000 | R26 Finance Manager | `[NEW]` |
| A-42 | **Budget virement between cost centres** | > 500,000 | CFO | `[NEW]` |

#### 4.2.4 Supply chain and inventory

| # | Decision | Threshold | Approver | Source |
|---|---|---|---|---|
| A-43 | Purchase requisition | ≤ 50,000 | R17 Inventory Manager | `[05-04]` |
| A-44 | Purchase requisition | ≤ 500,000 | Procurement Manager | `[05-04]` |
| A-45 | Purchase requisition | ≤ 2,000,000 | CFO | `[05-04]` |
| A-46 | Purchase requisition | > 2,000,000 | CEO | `[05-04]` |
| A-47 | Inventory write-off | ≤ 25,000 | R17 Inventory Manager | `[05-04]` |
| A-48 | Inventory write-off | > 25,000 | CFO | `[05-04]` |
| A-49 | **Stock adjustment (variance) above the configured threshold** | Per `MD-048` config | R17 Inventory Manager with reason code (`BRU-INV-06`); **never the counter** (`SOD-05`) | `[NEW]` |
| A-50 | **Inter-branch stock transfer** | Any | Source R06 Branch Manager + destination confirmed receipt (`BRU-INV-02`) | `[NEW]` |
| A-51 | **Purchase order that would exceed network maximum stock** | Any | Procurement Manager override, logged (`BRU-INV-03`, class **A**) | `[NEW]` |
| A-52 | **Return to vendor / debit advice** | Any | R17 Inventory Manager + R26 Finance Manager | `[NEW]` |
| A-53 | **Vendor onboarding / activation** | Any | Procurement Manager — **never the person who will approve that vendor's invoices** (`SOD-01`, `BRU-SCM-03`) | `[05-04]` §6 |
| A-54 | **Three-way match tolerance override** | Within configured tolerance | Automatic; outside it, R26 Finance Manager | `[NEW]` |
| A-97 | **Vendor bank-detail change** | Any | R26 Finance Manager, after verification through an **independently sourced** contact; the requester may never approve (`SOD-40`) | `[NEW]` — the single most common ERP payment fraud; absent from `05-04` §7 entirely |

#### 4.2.5 People

| # | Decision | Threshold | Approver | Source |
|---|---|---|---|---|
| A-55 | Payroll run | Any | R30 HR Manager + CFO (two approvals, `BRU-HRM-06`) | `[05-04]` |
| A-56 | **Payroll bank file release** | Any | A third person — not the preparer, not the approver (`SOD-03`, `SOD-29`) | `[NEW]` from `M56` |
| A-57 | **Overtime** | Any | Line manager, **pre-approved before it counts for payroll** (`BRU-HRM-02`); requester excluded (`SOD-27`) | `[NEW]` |
| A-58 | **Leave that takes coverage below the configured minimum** | Any | R06 Branch Manager override, logged (`BRU-HRM-04`, class **A**) | `[NEW]` |
| A-59 | **Attendance exception regularisation above the threshold count** | Per config | Verifier must not be the regulariser (`SOD-28`) | `[NEW]` |
| A-60 | **Retrospective effective-date change to an employee record** | Any | R30 HR Manager, not the processor (`SOD-26`) | `[NEW]` |
| A-61 | **Salary structure for a newly created employee record** | Any | Not the creator of the record (`SOD-25`) | `[NEW]` |
| A-62 | **Recruitment requisition** | Any | Line manager + R30 HR Manager; > 1 headcount CFO | `[NEW]` |
| A-63 | **Incentive payment outside the calculated schedule** | Any | CFO — `M57` calculates, only `M56` pays (`SOD-30`) | `[NEW]` |

#### 4.2.6 Quality, safety and circular business

| # | Decision | Threshold | Approver | Source |
|---|---|---|---|---|
| A-64 | **Compensation to a complainant** | ≤ 5,000 | R06 Branch Manager | `[NEW]` — complaint compensation is not in `05-04` §7 |
| A-65 | **Compensation to a complainant** | ≤ 25,000 | R05 Operations Director | `[NEW]` |
| A-66 | **Compensation to a complainant** | > 25,000 | CCO + CFO | `[NEW]` |
| A-67 | **Compensation above the branch threshold — owner excluded** | Any | Approver must not own the complaint (`SOD-22`) | `[NEW]` |
| A-68 | **CAPA closure** | Any | R32 Quality Manager; effectiveness verifier must not be the person who performed the action (`SOD-19`, `BRU-QMS-03`) | `[NEW]` |
| A-69 | **QC waiver** | **None. Class H — no approval path exists** (`BRU-SRM-04`) | — | `[NEW]` — recorded so nobody looks for one |
| A-70 | Trade-in offer | ≤ 30,000 | R25 Retail / Refurbishment Officer | `[05-04]` |
| A-71 | Trade-in offer | > 30,000 | Retail Manager + Finance | `[05-04]` |
| A-72 | **Refurbishment grade override** | Any | R32 Quality Manager with recorded justification (`BRU-TRF-05`, class **A**) | `[NEW]` |
| A-73 | **Discretionary rental damage charge** | Any | Retail Manager (`BRU-RNT-03`) | `[NEW]` |
| A-74 | **E-waste disposal batch release** | Any | R32 Quality Manager; preparer excluded (`SOD-23` pattern) | `[NEW]` |
| A-75 | Data destruction | Any | R14 Data Services Technician + witness (operator ≠ witness) | `[05-04]` |

#### 4.2.7 Marketplace and partner

| # | Decision | Threshold | Approver | Source |
|---|---|---|---|---|
| A-76 | Marketplace seller approval | Any | R24 Marketplace Operations Officer | `[05-04]` |
| A-77 | Marketplace seller payout — standard | Any | Automatic on schedule | `[05-04]` |
| A-78 | Marketplace seller payout — held or disputed | Any | R26 Finance Manager | `[05-04]` |
| A-79 | **Seller approval and payout approval are incompatible** | Any | Different people (`SOD-06`) | `[05-04]` §6 |
| A-80 | **Seller suspension or removal** | Any | R24 Marketplace Operations Officer; removal above the threshold CCO | `[NEW]` |
| A-81 | **Marketplace dispute decision** | Any | R24 — decided by 1000FiX, never the parties (`BRU-ECM-09`) | `[NEW]` |
| A-82 | **Partner MDF allocation** | Any | Allocator may not approve the claim against it (`SOD-18`) | `[NEW]` |
| A-83 | **Loyalty points adjustment** | Any | Approver ≠ requester (`SOD-17`) | `[NEW]` |
| A-84 | **Campaign above the budget threshold** | Per config | Builder may not approve (`SOD-23`); budget approver ≠ campaign owner (`SOD-24`) | `[NEW]` |

#### 4.2.8 Platform, data and access

| # | Decision | Threshold | Approver | Source |
|---|---|---|---|---|
| A-85 | Access request — standard role | Any | Line manager | `[05-04]` |
| A-86 | Access request — privileged role | Any | Line manager + R33 IT Administrator + CTO | `[05-04]` |
| A-87 | SoD exception | Any | CFO or CTO, time-boxed | `[05-04]` |
| A-88 | **SoD exception — beneficiary excluded** | Any | Grantor may not be the beneficiary (`SOD-22`) | `[NEW]` |
| A-89 | **Master data change above the significance threshold** | Per `MD-001` | Data domain owner (`BRU-ADM-01`) | `[NEW]` |
| A-90 | **Production configuration change** | Any | Traceable to an approved change record (`BRU-ADM-02`); CAB per `SP-031` | `[NEW]` |
| A-91 | **Emergency change** | Any | CTO or delegate, with retrospective CAB review within 2 business days | `[NEW]` |
| A-92 | **Bulk personal-data export** | Any | Data Protection Officer + CTO, logged (`BRU-SEC-05`) | `[NEW]` |
| A-93 | **Legal hold placement or release** | Any | Legal Counsel only — reserved to `M60`, not exercisable in `M24` | `[NEW]` |
| A-94 | **Document disposal batch** | Any | Preparer may not approve (`SOD-23`) | `[NEW]` |
| A-95 | **AI guard-rail removal** | Any | Not the sole approval of its author (`SOD-20`); CTO countersign | `[NEW]` |
| A-96 | **Model recommendation with material customer or financial impact** | Any | Human confirmation mandatory (`BRU-AIM-01`) | `[NEW]` |

**Count: 97 authorities. 28 reproduced verbatim from the 28 rows of `05-04` §7; 3 derived from `05-04` §6 segregation rules; 2 adjacent (computed or hard-blocked, no approver exists); 64 proposed `[NEW]`.**

> **This is the principal finding of this file.** `05-04` §7 covers fewer than a third (28 of 97) of the
> decisions the workflow engine must gate. The remaining 63 are derivable from `05-05` rules and
> module text but have never been collected, and in 41 of the 64 the rule exists while the *approver*
> is unnamed. Configuring the engine from `05-04` §7 alone would leave 63 value-bearing decisions
> ungated. Registration action in §6.

### 4.3 Reading the bands

| Convention | Meaning |
|---|---|
| `≤ X` | Inclusive of X |
| `> X` | Strictly above X |
| Two approvers joined by `+` | **Both** required, in sequence, by different people |
| "Customer + …" | Customer approval is necessary but never sufficient; the internal approval is additional |
| Currency | BDT, VAT-exclusive, per transaction, at the transaction date |
| A band with no upper bound | The final authority; there is nothing above it inside the ERP |

**Rule AA-11.** Bands are evaluated on the **gross value of the whole transaction**, never on the
incremental amount. A 4,000 estimate revised to 6,000 is a 6,000 decision (A-02), not a 2,000 one.

### 4.4 Currency, tax and multi-entity treatment

| Question | Answer |
|---|---|
| VAT-inclusive or exclusive? | **Exclusive.** Bands are compared against the pre-VAT value so that a VAT rate change does not silently move transactions between bands |
| Foreign currency? | Converted at the rate in force at the transaction date per `MD-039`; the band is applied to the BDT equivalent |
| Multi-entity? | Bands apply per legal entity (`MD-002`). A group-level aggregate does not lower an entity-level approver's authority |
| Recurring transactions? | Evaluated on **annual contract value**, not the monthly instalment. A 30,000/month AMC is a 360,000 decision |

### 4.5 Anti-avoidance

**Rule AA-12 — split detection.** The system flags, for review by the process owner and Internal
Audit:

| Pattern | Detection |
|---|---|
| Two or more transactions to the same counterparty, same category, within 7 days, whose combined value crosses a band the individual values do not | Automatic flag, reviewed monthly |
| A requisition reduced in value and re-submitted within 48 hours after a rejection | Automatic flag, immediate |
| Repeated approvals within 5% below a band ceiling by the same approver | Trend report, quarterly, to Internal Audit |
| An estimate revised upward more than twice on one order | Flag to R06 Branch Manager (`DT-006`) |

**Rule AA-13.** A flag is not an accusation and does not block the transaction. It creates a
reviewed record. Blocking legitimate work to prevent a pattern that is usually innocent is worse
than reviewing it — but an unreviewed pattern is how threshold controls are defeated everywhere.

### 4.6 Delegation of authority

**This section has no upstream source. It does not exist in `05-04`, `05-05` or `00-04`.** It is
authored here because the workflow engine cannot be built without it, and is submitted for CFO
approval as new governance.

| # | Rule |
|---|---|
| **DL-01** | Delegation is **from a position to a named person**, recorded in the system, never verbal and never by email |
| **DL-02** | A delegation is **time-boxed** with an explicit end date. There is no open-ended delegation |
| **DL-03** | A delegate exercises the delegator's limit **or their own, whichever is lower** — with one exception: a formal *acting-up* appointment (DL-08) confers the full limit |
| **DL-04** | Delegation **cannot cross a segregation-of-duties boundary**. A delegate who would then hold both sides of an `SOD-` pair is refused by the engine, and the authority escalates upward instead (`SP-005`) |
| **DL-05** | **Sub-delegation is prohibited** unless explicitly permitted in the delegation record, and never beyond one further level |
| **DL-06** | Delegation is **revocable immediately** by the delegator or by their superior, and is revoked automatically on the delegate's leaver event (`AUT-048`) |
| **DL-07** | **CFO and CEO authorities (A-31, A-45, A-46) may be delegated only by written Board-minuted resolution**, not within the ERP |
| **DL-08** | **Acting-up**: where a position is vacant, the superior appoints an acting holder for a stated period. The acting holder carries the full position limit and is recorded in `MD-008` |
| **DL-09** | **Upward escalation is the default on absence.** If no delegation exists and the approver is unavailable beyond the `SP-005` timer, the authority rises one level. It never falls, and it is never skipped (`AA-07`) |
| **DL-10** | Every delegation, every exercise of a delegated authority and every automatic upward escalation appears on the **monthly delegation report** to the CFO and Internal Audit |
| **DL-11** | Delegation records are **effective-dated and retained**; the question "who could approve this on that date?" must be answerable years later (`M24` retention, `LG-010`) |

**Absence ladder — what actually happens**

| Situation | Behaviour |
|---|---|
| Approver available | Normal approval |
| Approver on planned leave with a recorded delegation | Delegate approves within DL-03 limits |
| Approver on planned leave, no delegation recorded | Request escalates one level up after the `SP-005` timer (DL-09) |
| Approver unavailable unexpectedly (illness, disconnection) | Same as above; the timer is the control, not the reason |
| Position vacant | Acting-up appointment (DL-08); until one exists, authority sits with the superior |
| Both approver and their superior unavailable | Rises again. There is always a terminal approver — CEO for commercial, CFO for financial, CTO for platform |
| Out-of-hours, safety-critical (`SP-030`) or customer-safety decision | The on-call ladder in `SP-005` §4.4 applies and **acts first, seeks approval after**, with a mandatory record within 24 hours |

### 4.7 Authority in the field and offline

Field technicians and riders work disconnected. `P02` and `P09` queue actions for sync
(`UI-009`).

| # | Rule |
|---|---|
| **OF-01** | An approval **cannot be granted offline by the approver's device**. Approval requires the request to have reached the approver |
| **OF-02** | A technician may **capture** a customer's approval offline (signature or OTP against a cached estimate); the *internal* approval band still applies on sync, and work above that band must not start until it clears |
| **OF-03** | Where work above a band has genuinely started before a sync — an emergency, a safety risk, a customer stranded — it is recorded as an **exception with a reason code** and reviewed by R06 Branch Manager within 24 hours. It is not backdated as an approval |
| **OF-04** | Cash collected in the field remains within the `SP-019` limits regardless of connectivity |

### 4.8 What is deliberately not gated

Stated so that the absence is understood as a decision.

| Decision | Why no approval |
|---|---|
| Assigning a job to a technician | Rules (`BRU-FSM-01`, `-02`, `BRU-SRM-09`) constrain it. Adding an approval would break the 3-minute intake and 8–9 jobs/day targets |
| Issuing an invoice on job closure | Automatic (`AUT-008`); the approval was the estimate. `KPI-054` requires 95% within one hour |
| Automatic service credit calculation | Computed from measured breach (`BRU-CTR-08`, class **C**). Making it approvable would make it negotiable |
| Sending a routine notification | Governed by consent (`NT-002`) and frequency (`NT-003`) rules, not approval |
| A standard-price sale within the rate card | The rate card was approved (A-16) |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-04` §7 | The source of the 33 `[05-04]` rows; the destination of the 63 `[NEW]` rows |
| `05-05` §2–§11 | Rule identifiers and classes cited throughout |
| [`SP-005_Escalation_Matrix.md`](SP-005_Escalation_Matrix.md) | Timers behind DL-09 and the absence ladder |
| [`SP-006_Segregation_of_Duties_Register.md`](SP-006_Segregation_of_Duties_Register.md) | The `SOD-` pairs that constrain delegation (DL-04) |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-008_Organisation_Structure_and_Position_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-008_Organisation_Structure_and_Position_Master.md) | Positions carry limits (`AA-01`); acting-up recorded here |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-039_Currency_FX_and_Rounding_Standard.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-039_Currency_FX_and_Rounding_Standard.md) | FX treatment in §4.4 |

| Depended on by |
|---|
| All 28 SOPs in `06B` — each §7 table cites a band here · `M60` GRC control testing · `NT-022` approval request messages · `TS-005` authority negative tests · `M30` workflow engine configuration · `DT-005`, `DT-006`, `DT-021`, `DT-023` approval blocks |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually, and at each wave boundary |
| Trigger for out-of-cycle review | Any change to `05-04` §7; a new `BRU-` rule carrying an approval; an organisational restructure; an Internal Audit finding; material inflation moving the real value of a band |
| Owner | CFO |
| Change control | Any threshold change requires CFO approval and, above A-45, Board ratification. Logged in `RF-006` |
| Effective dating | **Yes.** A transaction is judged by the matrix version in force at its date |

**Registration actions raised by this file** *(rule `RG-01` — a process document must not become a second authority register)*

| # | Action | Owner | Needed by |
|---|---|---|---|
| RA-01 | Register the **64 `[NEW]` authorities into `05-04` §7**, or formally record `SP-004` §4.2 as the authority register with `05-04` §7 reduced to a pointer. **One of the two must happen; two competing registers must not both exist** | CFO + Enterprise Architecture | **Before W1 build** |
| RA-02 | Approve §4.6 delegation rules `DL-01`…`DL-11` as new governance — they have no upstream source | CFO, ratified by the Board | Before W1 build |
| RA-03 | Name the 41 approvers where `05-05` or a module file states a rule but never names who approves | Domain owners via the Business Owners Forum | Before W1 build |
| RA-04 | Confirm every `[NEW]` currency band against current commercial reality — the values proposed here are derived from the `05-04` §7 ladder and are **not** yet validated against actual transaction distributions | CFO with Finance | Before W1 build |

> **RA-04 is a stated limitation, not an oversight.** The `[NEW]` bands are internally consistent
> with the `[05-04]` ladder. They have not been tested against the volume of transactions that
> would actually fall in each band, because `SP-002` baseline data does not yet exist. A band set
> too low buries managers in approvals; too high, and the control is theatre.

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3)
- [x] Every threshold cites its source, distinguishing reproduced from proposed
- [x] Principles stated and enforceable at the model layer (`BR-STD-01`)
- [x] Delegation rules complete, including absence, acting-up, sub-delegation and revocation
- [x] Anti-avoidance detection specified
- [x] Offline and field behaviour specified
- [x] Deliberate non-gating stated explicitly
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **RA-01 register reconciliation with `05-04` §7 — outstanding; blocks `Approved`**
- [ ] RA-02 delegation governance approved by CFO and Board — **outstanding**
- [ ] RA-03 the 41 unnamed approvers named — **outstanding**
- [ ] RA-04 bands validated against transaction distributions — **outstanding, depends on `SP-002`**
- [ ] Named approver recorded — **pending CFO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
