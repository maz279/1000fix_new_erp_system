---
id: TR-012
title: Course Pack — Inventory and Store Keeper
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Inventory and Warehouse Operations
reviewers: [Inventory Manager, Operations Director, Finance Manager, Quality Manager, HSE Lead, Localisation Lead]
approver: Inventory Manager with Operations Director
content_class: D
purpose: >
  Trains 51+ branch store keepers, 15–30 warehouse operatives and 5–10 inventory managers. Stock
  accuracy is a prerequisite for every downstream promise the company makes — a part that the system
  says exists and does not is a broken SLA, a second visit and a customer who was told a date that
  was never achievable.
traces_to: [M15, M41, M43, M22, M18, P03, MD-004, MD-022, MD-023, MD-026, MD-047, TR-001, TR-002, TR-004, TR-006, TR-022, UI-027, SP-016, SP-018, SP-025, KB-009, KB-013]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: TR-012_Course_Pack_Inventory_and_Store_Keeper_BN.md
sources:
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md and SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md — the governing procedures
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-INV-01 stock cannot be issued against an unapproved paid repair; BRU-INV-02 transfer approval; BRU-INV-05 expired shelf-life stock cannot be issued; BRU-INV-06 adjustments above threshold require approval with a reason; BRU-INV-07 goods failing inspection go to quarantine; BRU-INV-08 serialised parts captured at receipt and issue; BRU-WTY-04 brand consignment cannot be consumed on non-warranty jobs
    verified: 2026-08-17
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md — part_class affects warranty and claim eligibility; hazard_class drives handling and transport
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Inventory and Store Keeper

| Item | Value |
|---|---|
| Audience role(s) | `R18` Branch Store Keeper · `R20` Warehouse Operative · `R17` Inventory Manager · **`R25` Retail / Refurbishment Officer (delta, `TR-002` §7.4)** |
| Headcount | 51+ store keepers · 15–30 operatives · 5–10 managers · 5–15 refurbishment officers |
| Duration | **Core 6 hours** + warehouse module 3 h (`R20`) + manager module 3 h (`R17`) + **refurbishment delta 3 h (`R25`)** |
| Delivery mode | Classroom with sandbox and physical stock handling |
| Language | Bengali primary |
| Prerequisites | Layer 1 universal core |
| Certification outcome | Functional competence record (`TR-006` cell 4) |
| Wave | W1 (core) · W3 (warehouse) · W5 (refurbishment delta) |

> **This pack carries a role it was not originally designed for.** `TR-002` §7.4 routes `R25`
> Retail / Refurbishment Officer here as an interim control because no `TR` pack exists for
> `SP-025`. `CU-16` requires that compromise to be declared, and §3.4 declares it.

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | Issue, consume, return and reconcile parts including van stock, to `SP-016` | Sandbox + practical |
| 2 | Recognise and respect the issue blocks — unapproved repair, expired stock, consignment | Items keyed to `BRU-INV-01`/`-05`, `BRU-WTY-04` |
| 3 | Capture serials at receipt and issue for serialised parts | Practical keyed to `BRU-INV-08` |
| 4 | Perform a cycle count, investigate a variance, and escalate above threshold | Practical + items |
| 5 | Raise and receive an inter-branch transfer correctly | Sandbox keyed to `BRU-INV-02` |
| 6 | Quarantine failed goods and route them correctly | Practical keyed to `BRU-INV-07` |
| 7 | **Handle hazardous stock — lithium, refrigerant, chemical — to `KB-013`** | **Critical practical** |
| 8 | Read `part_class` and understand its warranty and claim consequence | Items keyed to `MD-022`, `KB-009` |
| 9 | Apply the correct reason code to every adjustment and exception | Sandbox |
| 10 | *(Warehouse)* Receive, inspect, put away and pick to `SP-018` | Practical |
| 11 | *(Manager)* Read network stock, set min/max, act on replenishment signals | Sandbox |
| 12 | *(Refurbishment delta)* Execute data erasure and grading to `SP-025` with the certificate produced | **Critical practical** |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Production access to stock transactions · van-stock custody | Layer 1 core | On release (`TR-024`); 24 months. **Hazardous-stock handling annually** |

---

## 3. Module Outline

### 3.1 Core — 6 hours (all audiences)

| # | Module | Duration | Method |
|---:|---|---|---|
| 1 | Why stock accuracy is everyone else's promise | 30 min | Facilitated |
| 2 | The inventory console and the location tree | 45 min | Walkthrough — `UI-027`, `MD-004` |
| 3 | **Issue, consume, return** — and the blocks | 75 min | Sandbox + items |
| 4 | **Van stock and reconciliation** | 60 min | Practical |
| 5 | Serials, `part_class` and what they mean downstream | 45 min | Practice — `MD-022`, `KB-009` |
| 6 | Counts, variances and adjustment authority | 60 min | Practical |
| 7 | Transfers and quarantine | 45 min | Sandbox |
| 8 | **Hazardous stock handling and storage** | 60 min | Practical — `KB-013` §4, §5, §6 |
| 9 | Reason codes and exceptions | 30 min | Sandbox — `MD-026` |

### 3.2 Warehouse module — 3 hours (`R20`, W3)

Receipt and inspection · put-away and location discipline · picking accuracy · cycle-count
execution · `SP-018` variance escalation.

### 3.3 Inventory manager module — 3 hours (`R17`)

Network stock view · min/max setting · replenishment signals from `M43` · consignment control
(`BRU-INV-04`) · obsolescence · **substitution patterns as a demand signal** (`KB-009` `PC-10`).

### 3.4 Refurbishment delta — 3 hours (`R25`, W5) — *declared interim route*

| Content | Source |
|---|---|
| Trade-in assessment and grading | `SP-025` |
| **Certified data erasure or physical destruction** | `SP-025`, `BRU-ESG-01` — **no device leaves without a record** |
| Consumer disclosure on refurbished sale | `KB-009` `PC-07`, `LG-013` |
| Refurbished stock as a distinct `part_class` | `MD-022` |
| Warranty on refurbished items | `MD-031` |

**`PK-05`: this delta is an interim control, not equivalence.** `R25` performs a distinct role with
data-protection and consumer-law obligations that an inventory pack is not designed to carry. The
gap is `TR-002` `O-03`.

---

## 4. Facilitator Guide

| Module | Talking points | Common misconceptions |
|---|---|---|
| 1 | A part the system says exists and does not is a broken promise made three days ago by someone else | *"It's only stock."* |
| 3 | `BRU-INV-01` blocks issue against an unapproved paid repair. The block protects the branch from unrecoverable cost | *"The technician needs it now."* |
| 4 | Van stock is the least controlled inventory in field service and the easiest to lose | *"He'll bring back what he doesn't use."* |
| 5 | `part_class` decides whether a warranty claim survives. Issuing a `compatible` part on a brand job costs the claim | *"A part is a part."* |
| 6 | A variance is information, not an accusation. **Hiding a variance is the offence** | *"I'll adjust it quietly."* |
| 8 | A swollen cell in a parts bin is a fire in a stockroom. Segregation is not optional (`KB-013` §4.3) | *"It's just a battery."* |
| 3.4 | An erasure certificate is the company's defence. A device sold without one is an unbounded liability | *"We wiped it, that's enough."* |

---

## 5. Participant Workbook Contents

Issue and return flow · van reconciliation sheet · serial capture rules · `part_class` consequence
table · count and variance thresholds · transfer and quarantine flows · **hazardous stock storage
card** (`KB-013` extract) · reason codes · **my access scope and adjustment authority**.

---

## 6. Exercises

| # | Exercise | System / sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Issue eight parts, two blocked | Sandbox | Unapproved repair, expired stock | Both blocks respected; **no workaround** |
| 2 | Van reconciliation with a discrepancy | Practical + sandbox | Van stock scenario | Discrepancy found, coded, escalated |
| 3 | Serial capture on receipt and issue | Practical | Serialised parts | 100% captured |
| 4 | **Cycle count with two variances** | Practical | Seeded count | Both found; correct threshold action |
| 5 | Transfer out and in | Sandbox | Transfer scenario | Approval and confirmation both honoured |
| 6 | Quarantine a failed receipt | Practical | Failed inspection | Quarantined, **not returned to available stock** |
| 7 | **Hazardous stock sort** | Practical | Mixed bin incl. inert swollen cell | Correct segregation and storage |
| 8 | `part_class` decision | Scenario | Brand warranty job, `compatible` part available | Refuses; escalates for the correct part |
| 9 | *(Delta)* Erasure and certificate | Practical | Trade-in device | Erasure performed and certificate produced |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification |
|---|---:|---:|---:|---|
| `TR-006` cell 4 form, 30 items | 30% | 80%, **100% on block and hazard items** | 3 | 24 months |
| Core practicals (2, 3, 4, 6) | 30% | All passed | 3 | 24 months |
| **Hazardous stock (exercise 7)** | 20% | Passed | 2 | **Annual** |
| Sandbox (1, 5, 8) | 20% | All passed | 3 | 24 months |
| **OJT sign-off — 5 days** | Gate | Inventory Manager delegate | — | — |
| *(Delta)* Erasure practical | Gate for `R25` | Passed | 2 | Annual |

> Conforms to [`../08A_Framework/TR-004_Assessment_and_Certification_Policy.md`](../08A_Framework/TR-004_Assessment_and_Certification_Policy.md).

---

## 8. Job Aids Produced

Issue-block quick card · van reconciliation sheet · `part_class` consequence card · count and
adjustment thresholds · **hazardous stock storage card** (from `KB-013`) · quarantine flow · reason
codes · *(delta)* erasure certificate checklist. All in `TR-022` except the hazard card, which is
sourced from `KB-013` (`CP-01`).

---

## 9. Trainer Requirements

L&D trainer with an experienced store keeper co-delivering · **HSE approval and delivery for module
8** · sandbox with realistic stock · physical: mixed stock bin including an inert swollen cell,
serialised parts, a failed-inspection item · cohort maximum 12 · **51+ store keepers means 5–6
cohorts**.

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Confidence handling a variance and a block | Diagnostic only (`LS-02`) |
| **Learning** | Assessment and practical pass | > 85% first attempt |
| **Behaviour** | Stock accuracy · van reconciliation completeness · unexplained adjustments · block-workaround attempts · hazardous storage compliance | Accuracy rising; workarounds zero |
| **Result** | **Stock accuracy** and parts availability, feeding `KPI-004` first-time fix · claim rejections attributable to `part_class` falling | Per `06-02`, `RP-001` |

**Required Drivers** (`LS-04`): reinforce — store job aids · encourage — Inventory Manager reviews
first month's counts · monitor — accuracy and adjustment patterns · reward — competence record;
branch stock accuracy visible in `P06`.

---

## 11. Related Documents

[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-025_SOP_TradeIn_Refurbishment_and_Resale.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-025_SOP_TradeIn_Refurbishment_and_Resale.md) *(delta)* ·
[`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) ·
`KB-009` substitution notes · `KB-013` §4–§6 hazard data · `UI-027` inventory console copy ·
[`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) cell 4.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | `TS-002` sandbox and physical stock training set do not exist | Test Lead with Inventory | **W1** |
| **O-02** | **`MD-022` is unpopulated**, so `part_class` and `hazard_class` teaching has no live data | MDM with Inventory | **W1** |
| **O-03** | **The `R25` delta (§3.4) is an interim control** carrying data-protection and consumer-law obligations. `TR-002` `O-03` records that a proper route is needed | Training Lead with Legal | W5 |
| **O-04** | Inert swollen-cell training units — same gap as `TR-005` `O-06`, `TR-007` `O-03`, `TR-009` `O-05` | HSE Lead | **W1** |
| **O-05** | `TR-006` cell 4 items land W2 while this pack is W1 (`TR-006` `O-01`) | L&D | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable (`DS-02`); Level 4 measure named (`LS-01`)
- [x] **The `R25` interim route declared in-pack as `CU-16` requires (`PK-05`)**
- [x] Every issue block taught as a control rather than an obstacle
- [x] Hazardous stock handling made a critical, annually-refreshed practical
- [x] `part_class` taught with its warranty and claim consequence
- [x] OJT sign-off gate present (`LS-03`); all four Required Drivers named (`LS-04`)
- [x] All internal links resolve
- [x] `BRU-INV-01`…`-08`, `BRU-WTY-04`, `BRU-ESG-01` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-02` `MD-022` populated — outstanding**
- [ ] **`O-03` proper route for `R25` — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Inventory Manager and Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
