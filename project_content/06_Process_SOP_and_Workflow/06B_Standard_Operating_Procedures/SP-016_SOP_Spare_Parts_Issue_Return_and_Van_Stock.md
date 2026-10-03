---
id: SP-016
title: SOP — Spare Parts Issue, Return and Van Stock
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Inventory
author: Business Process Lead with Inventory Operations
reviewers: [Inventory Manager, Operations Director, Finance Manager, Quality Manager, Branch Managers Forum, Localisation Lead]
approver: Chief Financial Officer
content_class: C
purpose: >
  Parts cannot be issued against an unapproved paid repair, and van stock is the least-controlled
  inventory in field service. This SOP governs requisition, issue, consumption recording, unused
  return, van reconciliation and discrepancy handling. Inventory accuracy underpins parts
  availability, which underpins first-time fix and turnaround; van stock variance is the point
  where inventory quietly leaves the company.
traces_to: [M15, M41, M02, M31, P02, P03, DT-024, DT-029, MD-022, MD-023, SP-004, SP-005, SP-008, SP-010, SP-018]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md — SOD-05 enforcement, transfer and quarantine separations
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §6 BRU-INV-01…BRU-INV-08; §2 BRU-SRM-11; §3 BRU-FSM-08; §12.3 AUT-035
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-042 inventory accuracy 75% baseline, KPI-047 van stock variance untracked
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.5.2 identification and traceability, and clause 8.5.4 preservation
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Spare Parts Issue, Return and Van Stock

| Item | Value |
|---|---|
| SOP ID | `SP-016` |
| Process owner | Chief Financial Officer; executed under Inventory Manager (R17) |
| Roles performing | `R18` Branch Store Keeper · `R10`–`R12` Technicians · `R09` Workshop Supervisor · `R17` Inventory Manager · `R20` Warehouse Operative |
| Systems used | `P03` Inventory console (`UI-027`) · `P02` · `M15` · `M41` |
| Frequency / volume | Continuous. Every repair consumes parts; 200–400 technicians hold van stock |
| ISO 9001 clause reference | **8.5.2** identification and traceability · 8.5.4 preservation · 7.1.5 monitoring resources |

---

## 1. Purpose and Outcome

**Purpose.** To move a part from store to a repair with its consumption recorded against the
right order, to return what is not used, and to reconcile van stock so that the difference
between what a technician holds and what the system says they hold is always known and always
small.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| No part was issued against an unapproved paid repair | `BRU-SRM-11` / `BRU-INV-01` |
| Every serialised part was scanned at issue and at consumption | `BRU-INV-08` |
| Unused parts were returned the same shift, not held "just in case" | Return record |
| Van stock reconciles at shift end | `AUT-035`; `KPI-047` |
| Brand warranty stock was never consumed on a non-warranty job | `BRU-WTY-04` |
| Inventory accuracy rises from 75% to 96%+ | `KPI-042` |

---

## 2. Scope

**Applies to:** issue and return of spare parts and consumables at branch stores and workshops;
van stock replenishment, holding and reconciliation; parts reservation against approved work; and
discrepancy handling.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Goods inbound from a supplier | `SP-018` receipt, put-away and count |
| Purchase of parts | `SP-017` |
| Return to vendor for credit | `SP-017` |
| Physical stock count and adjustment authorisation | `SP-018`; the counting/adjustment separation is `SOD-05` |
| Movement of parts between branches | `SP-009` |
| Disposal of scrap and failed parts | `SP-026` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Van stock | Parts held by a technician, owned by the issuing branch until consumed against an order |
| Reservation | Parts allocated to an approved order but not yet issued |
| Consumption | The recorded fitting of a part to a specific order — the point of ownership transfer |
| Return | An issued part coming back unused |
| Variance | The difference between physical count and system quantity |
| Consignment stock | Brand-owned stock held by 1000FiX, excluded from own-stock valuation (`BRU-INV-04`) |
| Warranty stock | Brand-supplied parts usable only on that brand's warranty work (`BRU-WTY-04`) |
| Serialised part | A part tracked by individual serial number |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Approved order for chargeable work | `SP-013` | **Parts cannot be issued against an unapproved paid repair** (`BRU-INV-01`) |
| Part catalogue and compatibility matrix | `MD-022` | The part must be compatible with the device model |
| Stock location tree | `MD-004` | Branch store, workshop store and van locations exist and are distinct |
| Van stock maximum per item per technician | Configuration | `BRU-FSM-08` caps the holding |
| Technician logged in | `M29` | Every issue is attributable |
| Shelf life checked where applicable | `M15` | Expired stock cannot be issued (`BRU-INV-05`) |

---

## 5. Procedure

### 5.1 Requisition and issue — workshop

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R10–R12 | Requisition the part against the order. Compatibility is checked against `MD-022` | `P03` | Requisition | 1 min |
| 2 | System | Verify the order is approved where chargeable; block otherwise (`BRU-INV-01`) | `M15` | Approval check | — |
| 3 | System | Verify stock class — brand warranty stock only on that brand's warranty work (`BRU-WTY-04`) | `M15` | Class check | — |
| 4 | R18 | Pick the part; scan the serial where serialised (`BRU-INV-08`); check shelf life (`BRU-INV-05`) | `P03` · scanner | Issue record with serial | 2 min |
| 5 | R18 | Issue to the order, not to the person. Stock moves from store to order, and the order carries the cost | `M15` | Stock movement | 30 s |
| 6 | R10–R12 | Confirm receipt at the bench | `P03` | Receipt confirmation | 30 s |

### 5.2 Van stock — replenishment

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 7 | R10–R12 | Request replenishment against the van's configured list and maximum (`BRU-FSM-08`) | `P02` | Replenishment request |
| 8 | R18 | Pick, scan and issue to the **van stock location**, not to an order | `P03` · `MD-004` | Van stock movement |
| 9 | R10–R12 | Confirm receipt item by item. **A technician who confirms without counting owns the variance** | `P02` | Confirmation |
| 10 | R18 | Record the issue against the technician's van location; the branch still owns the value | `M15` | Location record |

### 5.3 Consumption in the field

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 11 | R10–R12 | Record the part consumed against the order at the point of fitting, not at end of day | `P02` | Consumption record |
| 12 | R10–R12 | Scan the serial for serialised parts, at consumption as well as at issue (`BRU-INV-08`) | `P02` | Serial captured |
| 13 | R10–R12 | Where offline, the consumption queues and syncs (`AUT-014`) | `P02` | Queued entry |
| 14 | R10–R12 | Retain the replaced part where the brand, the warranty or the customer requires its return | — | Retained-part record |

### 5.4 Return

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 15 | R10–R12 | Return unused parts to store **the same shift**. Parts held over are treated as van stock and counted | `P03`/`P02` | Return record |
| 16 | R18 | Inspect the returned part. Damaged or opened parts go to quarantine, not back to available stock (`BRU-INV-07`) | `P03` | Condition assessment |
| 17 | R18 | Return to the correct location and class. A warranty part returns to warranty stock, never to general stock | `M15` | Stock movement |
| 18 | R18 | Route failed or defective new parts to the vendor-return path | `SP-017` | Return-to-vendor record |

### 5.5 Shift-end van reconciliation

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 19 | System | At shift end, reconcile van stock and report variance to the branch manager (`AUT-035`) | `M15` | Variance report |
| 20 | R10–R12 | Count physically against the system list — **count first, then look at the expected figure** | `P02` | Blind count |
| 21 | R10–R12 | Explain any variance with a reason code | `P02` · `MD-026` | Variance explanation |
| 22 | R06 | Review variances daily. Repeated unexplained variance is escalated, not accumulated | `P03` | Review record |
| 23 | R17 | Approve any adjustment arising. **The counter may not approve the adjustment** (`SOD-05`) | `P03` | Adjustment approval |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 2 | Order is not approved | **Blocked, class H, no override** (`BRU-INV-01`). Obtain approval first | — |
| 3 | Only brand warranty stock is available for a paid job | **Blocked** (`BRU-WTY-04`). Source the part through the normal route or hold the job | R17 |
| 4 | Part is past shelf life | **Blocked** (`BRU-INV-05`). Quarantine it and report | R17 |
| 4 | Serial on the part does not match the system | Stop. Do not issue. Investigate — a serial mismatch is a traceability break | R18 → R17 |
| 4 | Part not in stock at this location | Check network stock (`AUT-007`); raise a transfer (`SP-009`) or a purchase (`SP-017`); place the job on hold with an approved reason so the SLA clock pauses (`BRU-SRM-15`) | R17 |
| 7 | Requested replenishment exceeds the van maximum | **Blocked** (`BRU-FSM-08`). A technician carrying more than the maximum is carrying uncontrolled inventory | R17 |
| 11 | A part is fitted that was not the one issued | Record what was actually fitted. The record follows the physical reality, never the plan | R10–R12 |
| 15 | Technician wishes to retain a part for a likely future job | Not permitted outside the van stock list. "Just in case" holdings are the origin of van variance | R17 |
| 16 | Returned part is damaged | Quarantine; assess whether it is technician-caused, transit-caused or a supplier defect | R18 → R17 |
| 21 | Variance is unexplained | Do not close the shift with an unexplained variance; escalate the same day (`SP-005` SC-E2) | R06 |
| 23 | Adjustment above the configured threshold | R17 with a reason code (`BRU-INV-06`); above the write-off band, CFO (`SP-004` A-48) | CFO |
| — | Counterfeit or non-genuine part identified | Quarantine immediately; do not return it to stock or to the vendor without instruction | R32, R19 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Issue parts against an unapproved paid repair | **None — class H, no override** | — | — |
| Stock adjustment above the configured threshold | Per config | R17 Inventory Manager with reason code (`SP-004` A-49) | CFO |
| Inventory write-off | ≤ BDT 25,000 | R17 Inventory Manager (`SP-004` A-47) | CFO |
| Inventory write-off | > BDT 25,000 | CFO (`SP-004` A-48) | CEO |
| Adjust inventory + perform the count justifying it | **Incompatible** (`SOD-05`) | Different people | — |
| Exceed the van stock maximum | Any | R17, time-boxed and reviewed | — |
| Quarantine stock + approve its write-off | **Incompatible** (`SOD-45`) | Different people | — |
| Inter-branch transfer | Any | Source R06 + destination confirmation (`SP-004` A-50) | R17 |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Stockout blocking a job | Network search, transfer or purchase; job on hold with an approved reason; customer given a revised ETA | R17, R06 (`SP-005` SC-E1) | Hold record |
| Van variance beyond tolerance | Investigate the same day. Repeated variance by one technician is a control matter, handled with HR, not informally | R06, R17 | Variance register |
| Serial mismatch | Traceability break; stop issue; investigate the chain | R17 | Data quality / custody record |
| Part fitted but never recorded | Found at reconciliation. Record retrospectively with the reason; a pattern indicates the recording step is being skipped in the field | R09, R17 | Exception record |
| Damaged part on receipt from store | Return before leaving the counter; do not accept and reconcile later | R18 | Condition record |
| Warranty stock consumed on a non-warranty job | Blocked; if found post-hoc, correct the stock class and report as a control failure | R17, R28 | Nonconformity |
| Expired stock found in a van | Remove and quarantine; review why it was issued or retained | R17 | Quarantine record |
| `P02`/`P03` unavailable | Fallback in §9 | R18, R33 | Manual issue book |
| Theft suspected | **L4-direct: CFO + Internal Audit**, restricted. Do not confront locally | As stated | Restricted record |

---

## 9. Manual Fallback

Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Use the **pre-numbered manual store issue book**: date, order number, part number, description, quantity, serial, issuer, receiver, both signatures |
| 2 | Van replenishment uses the same book, marked "VAN" with the technician's name and van location |
| 3 | Consumption in the field is recorded on the paper job card (`SP-008` §9) and cross-referenced to the issue book number |
| 4 | Returns are entered in the book with a "RET" prefix and countersigned by the store keeper |
| 5 | **Back-enter every movement within 24 hours**, preserving dates |
| 6 | R17 reconciles the book against the system after the outage and signs it; unused book numbers are accounted for |
| 7 | Shift-end van reconciliation continues manually — it is a physical count and does not require a system |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Parts cannot be issued against an unapproved paid repair | Preventive (`BRU-INV-01`) | Per issue | Hard block |
| Brand warranty parts restricted to warranty work | Preventive (`BRU-WTY-04`) | Per issue | Hard block |
| Serialised parts scanned at issue and consumption | Preventive (`BRU-INV-08`) | Per part | Hard block |
| Expired stock cannot be issued | Preventive (`BRU-INV-05`) | Per issue | Hard block |
| Van holding capped per item per technician | Preventive (`BRU-FSM-08`) | Continuous | Hard block |
| Failed-inspection goods to quarantine | Preventive (`BRU-INV-07`) | Per receipt | Hard block |
| Count and adjustment approval separated | Preventive (`SOD-05`) | Per adjustment | Hard block |
| Consignment stock excluded from own-stock valuation | Preventive (`BRU-INV-04`) | Continuous | Computed |
| Shift-end van reconciliation | Detective (`AUT-035`) | Per shift | Variance report |
| Cycle count by ABC class | Detective (`AUT-036`) | Per schedule | Count record |
| Inventory accuracy | Detective | Monthly | `KPI-042` |
| Dead stock disposition | Detective (`AUT-037`) | Quarterly | `KPI-046` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Perform the count | Approve the adjustment arising from it (`SOD-05`) | Hard block | At single-person sites, all adjustments route to R17 off-site with no local threshold (`SP-006` §4.6) |
| Quarantine stock | Approve its write-off (`SOD-45`) | Hard block | — |
| Raise an inter-branch transfer | Approve it above the value threshold (`SOD-44`) | Threshold block | Approval routes to R17 |
| Hold procurement authority | Adjust the stock balances that justify buying (`M15`: R19 has read-only stock access) | Hard block at assignment | — |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-042` | Inventory accuracy | 75% | 96%; stretch 98% |
| `KPI-043` | Part availability at first request | unmeasured | 88%; stretch 93% |
| `KPI-044` | Stockout-caused job delays | unmeasured | < 6%; stretch < 3% |
| `KPI-045` | Inventory turns per year | unmeasured | 4.5; stretch 6+ |
| `KPI-046` | Dead stock as % of value | unmeasured | < 8%; stretch < 5% |
| `KPI-047` | Van stock variance | untracked | < 2%; stretch < 1% |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-024` Goods Receipt Note and Inspection Record | Inbound counterpart |
| `DT-029` Physical Count and Stock Adjustment Sheet | Count and adjustment authorisation |
| `UI-027` Workspace — Inventory Console Copy | The screens used |
| [`SP-008_SOP_On_Site_Field_Service_Visit.md`](SP-008_SOP_On_Site_Field_Service_Visit.md) | Field consumption and shift-end reconciliation |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](SP-010_SOP_Workshop_and_Depot_Repair.md) | Bench consumption |
| [`SP-017_SOP_Procurement_to_Payment.md`](SP-017_SOP_Procurement_to_Payment.md) | Replenishment and vendor return |
| [`SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md`](SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md) | Counting and adjustment |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | Compatibility check at step 1 |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md) | Location tree including van locations |
| `TR-012` Course Pack — Inventory and Store Keeper | Trains this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Parts issued to an order, not to a person, stated explicitly
- [x] Blind count specified before the expected figure is shown
- [x] Van stock treated as controlled inventory with a cap and a daily reconciliation
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback keeps the physical count in force during an outage
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Van stock maximums configured per role and device family — **outstanding, depends on `SP-002`**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending CFO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
