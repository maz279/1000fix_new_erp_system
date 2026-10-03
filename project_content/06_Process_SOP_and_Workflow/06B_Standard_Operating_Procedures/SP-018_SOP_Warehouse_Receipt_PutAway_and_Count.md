---
id: SP-018
title: SOP — Warehouse Receipt, Put-Away and Count
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Warehouse
author: Business Process Lead with Warehouse Operations
reviewers: [Inventory Manager, Finance Manager, Quality Manager, Internal Audit, HSE Lead, Localisation Lead]
approver: Chief Financial Officer
content_class: C
purpose: >
  Stock accuracy underpins parts availability, which underpins first-time fix and turnaround
  time. This SOP governs receiving, inspection, put-away, picking, cycle counting and variance
  escalation, with the counting and adjustment duties held apart. Inventory accuracy today is
  75%; the target is 96%, and it will not be reached by better software alone — it is reached by
  counting on a schedule and by never letting the person who counts approve the adjustment.
traces_to: [M41, M15, M16, P03, DT-024, DT-029, DT-044, MD-004, MD-023, SP-004, SP-005, SP-016, SP-017]
priority: P2
wave: W3
bilingual: yes
bn_counterpart: SP-018_SOP_Warehouse_Receipt_PutAway_and_Count_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M41_Warehouse_Management.md — put-away override separation, bin blocking/unblocking separation, SOD-05 applied at the device
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §6 BRU-INV-05, BRU-INV-06, BRU-INV-07, BRU-INV-08; §12.3 AUT-033, AUT-036
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-042 inventory accuracy 75% baseline, KPI-045 inventory turns, KPI-046 dead stock
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.4.2 verification of externally provided product, and clause 8.5.4 preservation
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Warehouse Receipt, Put-Away and Count

| Item | Value |
|---|---|
| SOP ID | `SP-018` |
| Process owner | Chief Financial Officer; executed under Inventory Manager (R17) |
| Roles performing | `R20` Warehouse Operative · `R18` Branch Store Keeper · `R17` Inventory Manager · `R32` Quality Manager · `R19` Procurement Officer |
| Systems used | `P03` Inventory console (`UI-027`) · `M41` · `M15` |
| Frequency / volume | Continuous receiving; cycle counting on the `AUT-036` ABC schedule |
| ISO 9001 clause reference | **8.4.2** verification of externally provided product · 8.5.4 preservation · 8.5.2 identification and traceability · 8.7 nonconforming outputs |

---

## 1. Purpose and Outcome

**Purpose.** To bring goods into the network accurately, store them where the system says they
are, pick them correctly, and keep the physical and system positions in agreement through
counting rather than through an annual reconciliation.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| What was received matches what was ordered, or the difference is recorded | `DT-024` GRN |
| Goods failing inspection went to quarantine, never to available stock | `BRU-INV-07` |
| Every location holds what the system says it holds | Cycle count accuracy |
| Nobody approved an adjustment to a count they performed | `SOD-05` |
| Serialised items are traceable end to end | `BRU-INV-08` |
| Inventory accuracy rises from 75% toward 96% | `KPI-042` |

---

## 2. Scope

**Applies to:** the central warehouse, regional stores and branch stores — receiving, inspection,
put-away, replenishment picking, cycle counting, full physical counts, bin management, and
variance escalation.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Purchasing and vendor payment | `SP-017` |
| Issue of parts to a repair or a van | `SP-016` |
| Movement between sites | `SP-009` |
| Disposal of obsolete or scrap stock | `SP-026` |
| Import clearance and landed cost | `M44` |
| Customer devices held in service | `SP-007`, `SP-010` — those are customer property, not stock |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| GRN | Goods receipt note with inspection outcome (`DT-024`) |
| Put-away | Placing received goods into a system-recorded location |
| Directive | The system's recommended put-away location |
| Bin | The smallest addressable storage location in `MD-004` |
| Cycle count | Rolling counts of a subset of stock on a schedule, by ABC class |
| Full count | A whole-site count, typically at year end or before a cutover |
| Blind count | A count performed without sight of the expected quantity |
| Variance | Physical minus system quantity |
| Quarantine | A location holding stock that must not be issued |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Open purchase order | `SP-017` | Receiving without a PO has no reference to match against |
| Location tree | `MD-004` | Every bin exists and is labelled per `DT-044` |
| Packaging and UOM standards | `MD-023` | Quantity conversions are defined, not calculated at the dock |
| Labelling capability | `DT-044` | An unlabelled bin cannot be counted reliably |
| Count schedule | `AUT-036` | ABC classification current |
| Inspection criteria | `M42`, `R32` | What "acceptable" means for this item class |
| Safety equipment and racking condition | `SP-030`, `M47` | Manual handling and working-at-height controls in force |

---

## 5. Procedure

### 5.1 Receive and inspect

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R20 | Check the consignment against the manifest and the PO before unloading. Refuse a delivery with no reference | `P03` | Delivery check | 5 min |
| 2 | R20 | Verify seals where present; record any break as a custody incident (`SP-009` §6) | `P03` | Seal record | 2 min |
| 3 | R20 | Count received quantity in the ordered UOM, converting per `MD-023` | `P03` | Count |
| 4 | R20 | Inspect condition and specification against the criteria for the item class | `P03` | Inspection outcome |
| 5 | R20 | Scan serials for serialised items (`BRU-INV-08`) | Scanner | Serials captured |
| 6 | R20 | Raise the GRN recording accepted, rejected and short quantities separately | `DT-024` | GRN |
| 7 | R20 | Route failed goods to **quarantine**, never to available stock (`BRU-INV-07`) | `M15` | Quarantine record |
| 8 | System | Update stock, allocate landed cost where applicable, trigger three-way match (`AUT-033`) | `M52` | Match triggered |

### 5.2 Put-away

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 9 | R20 | Accept the system put-away directive, or override with a reason | `P03` | Put-away task |
| 10 | R20 | Move to the bin; scan bin and item to confirm | Scanner | Location confirmed |
| 11 | R17 | Approve any override of a put-away directive. **The operative may not approve their own override** (`SOD-48`) | `P03` | Override approval |
| 12 | R20 | Apply shelf-life and lot data where applicable | `P03` | Lot/expiry recorded |

### 5.3 Pick and replenish

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 13 | R20 | Pick against the requisition or transfer, scanning bin and item | Scanner | Pick confirmation |
| 14 | R20 | Where the bin is short, record the shortfall **at the bin** rather than picking from elsewhere silently | `P03` | Shortfall record |
| 15 | R20 | Replenish forward pick locations from bulk on the replenishment task | `P03` | Replenishment record |
| 16 | R20 | Stage and hand over for despatch under `SP-009` | `P03` | Custody transfer |

### 5.4 Cycle counting

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 17 | System | Generate the count task list by ABC class and location (`AUT-036`) | `M41` | Count tasks |
| 18 | R20 | Count **blind** — the expected quantity is not displayed | `P03` count mode | Counted quantity |
| 19 | System | Compare; where within tolerance, close; where outside, generate a recount task | `M41` | Variance |
| 20 | R20 (different person from step 18 where possible) | Recount | `P03` | Second count |
| 21 | R17 | Investigate the confirmed variance: mis-pick, mis-put-away, unrecorded issue, damage, or loss | `P03` | Investigation record |
| 22 | R17 | Approve the adjustment with a reason code. **The counter may not approve** (`SOD-05`) | `DT-029` | Adjustment approval |
| 23 | R17 | Above the write-off band, CFO approves (`SP-004` A-48) | `P03` | Write-off approval |

### 5.5 Full count

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 24 | R17 | Freeze movement for the count window; publish the freeze in advance | `SP-032` |
| 25 | R20 + independent counters | Count in pairs; one counts, one records; blind to system quantities | `SOD-05` |
| 26 | R17 | Reconcile, recount exceptions, and produce the variance report | `DT-029` |
| 27 | CFO | Approve the net adjustment; Internal Audit observes a sample | `SP-004` A-47/A-48 |
| 28 | R17 | Release the freeze and record the accuracy achieved | `KPI-042` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 1 | Delivery arrives with no PO reference | Do not receive into stock. Hold in the receiving bay pending identification | R17 |
| 2 | Seal broken | Custody incident; photograph; do not open until instructed (`BRU-LOG-04`) | R15 + R17 |
| 3 | Quantity short | Record the actual, not the ordered. The GRN is the truth, the PO is the intention | R20 |
| 4 | Goods fail inspection | Quarantine (`BRU-INV-07`); notify procurement and quality; decide return, rework or concession | R32 + R19 |
| 4 | Item is not what was ordered | Do not put it away. Substitution decided by procurement, not at the dock | R19 |
| 5 | Serial already exists in the system | Stop. A duplicate serial is either a data defect or a counterfeit | R17 + R32 |
| 9 | Directive location is full or unsuitable | Override with a reason; approval by R17 (`SOD-48`) | R17 |
| 14 | Bin is short at picking | Record at the bin. Silent picking from another location destroys the count trail | R20 |
| 18 | The counter can see the expected quantity | Stop. A sighted count is not a count | R17 |
| 19 | Variance within tolerance | Close and adjust automatically; the tolerance is configured, not judged per case | System |
| 21 | Variance pattern concentrated in one item, bin or shift | Investigate as a control matter, not as a counting error | R17 → CFO |
| 21 | Variance indicates possible theft | **L4-direct: CFO + Internal Audit**, restricted. Do not confront locally | As stated |
| 24 | Business cannot afford a full freeze | Count by zone with movement locked per zone; never count a moving location | R17 |
| — | Expired or shelf-life-exceeded stock found | Quarantine; it cannot be issued (`BRU-INV-05`); route to disposal | R17, `SP-026` |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Stock adjustment above the configured threshold | Per config | R17 Inventory Manager with reason code (`SP-004` A-49, `BRU-INV-06`) | CFO |
| Inventory write-off | ≤ BDT 25,000 | R17 (`SP-004` A-47) | CFO |
| Inventory write-off | > BDT 25,000 | CFO (`SP-004` A-48) | CEO |
| Approve an adjustment to a count you performed | **Incompatible** (`SOD-05`) | Different person | — |
| Put-away directive override | Any | R17 (`SOD-48`) | Warehouse Manager |
| Quarantine release to available stock | Any | R32 Quality Manager | R17 |
| Quarantine + approve write-off of the same stock | **Incompatible** (`SOD-45`) | Different people | — |
| Bin block / unblock beyond the duration threshold | Any | Different actors (`M41`) | R17 |
| Accept goods with a concession against specification | Any | R32 with R19; recorded | R17 |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Goods failed inspection | Quarantine; supplier nonconformity | R32, R19 (`SP-005` SC-E5) | `M42` nonconformity |
| Duplicate serial detected | Halt receipt of that line; investigate provenance | R17, R32 | Data/counterfeit record |
| Damage found after put-away | Move to quarantine; assess cause — transit, handling or supplier | R17 | Damage record |
| Repeated variance in the same bin | Physical investigation of the bin, its labelling and its neighbours | R17 | Investigation record |
| Count task overdue | Escalate; an unexecuted cycle count is an unmeasured position | R17 → CFO | Count compliance report |
| Adjustment approved by the counter | `SOD-05` violation; blocked by the engine, reported if attempted | CFO, Internal Audit | `SP-006` exception report |
| Racking, forklift or manual-handling incident | Safety first (`SP-030`); isolate the area | HSE, R17 | Safety incident |
| `P03` unavailable | Fallback in §9 | R17, R33 | Paper GRN and count sheets |
| Stock found in an unrecorded location | Record it into a location before doing anything else. Unlocated stock is not stock | R17 | Adjustment record |

---

## 9. Manual Fallback

Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Receive on the **pre-numbered manual GRN book**: PO number, supplier, item, quantity ordered, quantity received, quantity rejected, serials, inspector, signature |
| 2 | Put-away is recorded on the GRN copy with the bin code; a second person countersigns the bin allocation |
| 3 | Picking uses printed pick lists; the picker signs and the bin is annotated |
| 4 | Cycle counts use **pre-numbered blind count sheets** — the sheet shows the item and the bin, never the expected quantity |
| 5 | Adjustments are **not** made during an outage. Variances are held on the count sheet and entered on restoration, so that the `SOD-05` approval path is preserved |
| 6 | **Back-enter every GRN, put-away and count within 48 hours**, preserving dates |
| 7 | R17 reconciles the books against the system and signs; Internal Audit samples the count sheets |

> Row 5 is deliberate. Deferring an adjustment costs accuracy for a day. Making one without the
> approval path costs the control entirely.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Failed-inspection goods to quarantine | Preventive (`BRU-INV-07`) | Per receipt | Hard block |
| Serialised items scanned at receipt and issue | Preventive (`BRU-INV-08`) | Per item | Hard block |
| Expired stock cannot be issued | Preventive (`BRU-INV-05`) | Per issue | Hard block |
| Count and adjustment approval separated | Preventive (`SOD-05`) | Per adjustment | Hard block |
| Put-away override approved by another person | Preventive (`SOD-48`) | Per override | Hard block |
| Quarantine and write-off approval separated | Preventive (`SOD-45`) | Per case | Hard block |
| Blind counting enforced in the count screen | Preventive | Per count | Count mode |
| Adjustments above threshold require a reason code | Preventive (`BRU-INV-06`) | Per adjustment | Hard block |
| Cycle count schedule completion | Detective | Monthly | Count compliance report |
| Inventory accuracy by location and class | Detective | Monthly | `KPI-042` |
| Dead stock disposition | Detective (`AUT-037`) | Quarterly | `KPI-046` |
| Internal audit observation of counts | Detective | Per full count | Audit record |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Perform a count | Approve the adjustment arising (`SOD-05`) | Hard block | At branch stores with one keeper, adjustments route to R17 with no local threshold |
| Quarantine stock | Approve its write-off (`SOD-45`) | Hard block | — |
| Override a put-away directive | Approve the override (`SOD-48`) | Hard block | — |
| Block a bin | Unblock it beyond the duration threshold | Different actors (`M41`) | — |
| Receive goods | Raise the PO **and** approve the invoice (`SOD-02`) | Any two permitted, never all three | Invoice approval routes to central Finance |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-042` | Inventory accuracy | 75% | 96%; stretch 98% |
| `KPI-045` | Inventory turns per year | unmeasured | 4.5; stretch 6+ |
| `KPI-046` | Dead stock as % of value | unmeasured | < 8%; stretch < 5% |
| Cycle count schedule completion | Counts executed against those due | untracked | 100% |
| Receipt-to-put-away time | Dock to system-recorded location | untracked | To be set from `SP-002` baseline |
| Adjustments approved by the counter | `SOD-05` violations | untracked | **Zero** |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-024` Goods Receipt Note and Inspection Record | Step 6 |
| `DT-029` Physical Count and Stock Adjustment Sheet | Steps 22 and 26 |
| `DT-044` Label, Barcode and QR Format Specification | Bin and item labelling |
| `UI-027` Workspace — Inventory Console Copy | The screens used |
| [`SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) | Downstream issue |
| [`SP-017_SOP_Procurement_to_Payment.md`](SP-017_SOP_Procurement_to_Payment.md) | Upstream purchase and match |
| [`SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) | Despatch custody |
| [`SP-026_SOP_EWaste_Collection_and_Disposal.md`](SP-026_SOP_EWaste_Collection_and_Disposal.md) | Obsolete and scrap disposal |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md) | Location and bin structure |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-023_Unit_of_Measure_and_Packaging_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-023_Unit_of_Measure_and_Packaging_Register.md) | UOM conversion |
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
- [x] Blind counting specified and enforced in the screen, not by instruction alone
- [x] Adjustments deferred rather than made without the approval path during an outage
- [x] §7 reconciles with `SP-004`
- [x] Segregation of duties cites `SP-006`, including the new `SOD-45` and `SOD-48`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Count tolerances and ABC classification configured — **outstanding, depends on `SP-002`**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending CFO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
