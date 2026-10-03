---
id: SP-009
title: SOP — Pick-and-Drop and Reverse Logistics
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Logistics
author: Business Process Lead with Logistics Operations
reviewers: [Operations Director, Logistics Coordinators, Finance Manager, Quality Manager, HSE Lead, Legal Counsel, Localisation Lead]
approver: Operations Director
content_class: C
purpose: >
  Devices in transit are the company's highest-value uninsured exposure. This SOP governs
  booking, packing, sealing, custody transfer, transit exception handling and return across
  50–150 riders and third-party couriers, so that every device movement has an unbroken evidence
  chain. Custody-break target is zero and proof-of-delivery completeness target is 100%; neither
  is achievable without a single packing and scanning standard.
traces_to: [M03, P09, M15, M17, DT-026, DT-027, DT-028, MD-005, SP-004, SP-005, SP-019, SP-030]
priority: P1
wave: W3
bilingual: yes
bn_counterpart: SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M03_Logistics_Pickup_and_Delivery.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §4 BRU-LOG-01…BRU-LOG-08
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P09_Logistics_and_Rider_Application.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-018 on-time collection/delivery, KPI-019 chain-of-custody exceptions (target zero)
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.5.4 — preservation of outputs during processing and delivery, to the extent necessary to ensure conformity
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Pick-and-Drop and Reverse Logistics

| Item | Value |
|---|---|
| SOP ID | `SP-009` |
| Process owner | Operations Director (R05); executed under Logistics Coordinator (R15) |
| Roles performing | `R15` Logistics Coordinator · `R16` Rider / Delivery Agent · `R08` Service Centre Agent · `R18` Branch Store Keeper · `R38` courier partner |
| Systems used | `P09` Logistics and Rider Application · `P03` (`UI-024`) · `M03` · `M17` |
| Frequency / volume | Continuous; 50–150 riders plus third-party couriers across the zones in `MD-005` |
| ISO 9001 clause reference | **8.5.4** preservation · 8.5.3 customer property · 8.5.2 identification and traceability |

---

## 1. Purpose and Outcome

**Purpose.** To move a customer's device, a spare part or a consignment between two points with
custody documented at every transfer, packaging appropriate to the item, and evidence sufficient
to establish who held it when.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Every custody transfer carries a scan and an identity capture from **both** parties | `BRU-LOG-01` |
| The consignment cannot be closed without proof of delivery | `BRU-LOG-02` |
| Seal number at receipt matches the seal number at dispatch | Seal reconciliation |
| The device that arrived is the device that left | Serial scanned at both ends |
| Zero custody-chain exceptions | `KPI-019` |
| POD completeness at 100% | `DT-028` |

---

## 2. Scope

**Applies to:** collection of a device from a customer, delivery of a repaired device to a
customer, inter-branch and branch-to-warehouse transfer, movement to and from a sub-contracted
workshop, return to vendor, and movement of items to a recycling or refurbishment partner.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| The customer bringing the device to a branch | `SP-007` |
| A technician carrying parts as van stock | `SP-016` |
| Goods inbound from a supplier to the warehouse | `SP-018` |
| Import consignments and customs clearance | `M44`; this SOP resumes at the warehouse gate |
| Cash carried by a rider | `SP-019` — the cash rules are separate from the goods rules |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Consignment | One or more items moving together under a single manifest |
| Custody transfer | The documented handover of physical responsibility between two identified parties |
| Seal | The tamper-evident numbered closure on a packed consignment |
| Manifest | `DT-027` — contents, route, handling instructions and seal number |
| POD | Proof of delivery — `DT-028`, comprising recipient identity, photograph, OTP or signature, GPS and timestamp |
| Custody break | Any point where the chain of documented responsibility is incomplete |
| Restricted item | Lithium battery, refrigerant, or any item requiring carrier certification (`BRU-LOG-05`) |
| Declared value | The value recorded for insurance and dual-signature purposes (`BRU-LOG-03`) |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Approved collection or delivery booking | `M03` | Zone is serviceable (`MD-005`); charge or waiver resolved (`BRU-LOG-07`) |
| Rider assigned and on shift | `M55` | Rider certified for any restricted item in the load (`BRU-LOG-05`) |
| Packaging materials to standard | `MD-023` | Correct box grade, cushioning and anti-static bag available |
| Numbered seals in stock | `M15` | Seals are controlled stationery; the range issued is recorded |
| `P09` synced | `P09` | Rider holds the manifest offline |
| Vehicle checked | `M46`, `SP-032` | Daily vehicle check completed |
| Declared value known | `M17` | Above the threshold, dual signature and insurance flag apply (`BRU-LOG-03`) |

---

## 5. Procedure

### 5.1 Collection from a customer

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R15 | Confirm the booking, address, window and any access constraint | `P03` | Booking confirmed | 2 min |
| 2 | R16 | Travel; the customer receives tracking automatically | `P09` | Departure timestamp | — |
| 3 | R16 | Arrive; record arrival with GPS. Identify yourself with badge and job reference | `P09` | Geotagged arrival | 1 min |
| 4 | R16 | Inspect the device **with the customer**. Photograph front, back and every defect. This is the condition baseline for transit | `P09` capture | Condition record + photographs | 3 min |
| 5 | R16 | Record accessories. Advise the customer to retain SIM and memory card | `P09` | Accessory list | 1 min |
| 6 | R16 | Give the data-backup warning and capture the acknowledgement | `P09` | Acknowledgement | 1 min |
| 7 | R16 | Pack to the `MD-023` standard for the device class; apply the anti-static bag where required | — | Packed | 2 min |
| 8 | R16 | Seal the package; record the seal number | `P09` | Seal number bound to the consignment | 30 s |
| 9 | R16 + customer | **Both parties scan and identify.** Customer signs or confirms by OTP | `P09` | Custody transfer (`BRU-LOG-01`) | 1 min |
| 10 | R16 | Issue the customer's copy of the collection receipt | `P09` / print | `DT-002` variant issued | 30 s |
| 11 | R16 | Depart; the consignment is In transit | `P09` | Status updated | — |

### 5.2 Arrival at the branch or workshop

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 12 | R18 / R08 | **Check the seal number before opening.** A mismatch stops the process (§6) | `P03` | Seal verified |
| 13 | R18 / R08 | Scan and identify; both parties recorded | `P03` | Custody transfer completed |
| 14 | R18 / R08 | Open, inspect against the collection photographs, and record any discrepancy immediately | `P03` | Receipt condition record |
| 15 | R18 / R08 | Place into the workshop queue or store location | `M15` | Location recorded |

### 5.3 Delivery to a customer

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 16 | R18 | Pack the completed device; include accessories, replaced parts if the customer requested them, and the `DT-007` completion report | — | Packed |
| 17 | R18 | Seal; record the seal number; hand to the rider with a scan by both | `P03` / `P09` | Custody transfer |
| 18 | R16 | Deliver. **Verify recipient identity** — the named customer, or a person they nominated in the system | `P09` | Identity verification |
| 19 | R16 | Collect payment if due | `P09` · `SP-019` | `DT-016` receipt |
| 20 | R16 | Capture POD: recipient identity, photograph, OTP or signature, GPS, timestamp | `P09` | `DT-028` POD (`BRU-LOG-02`) |
| 21 | R16 | Close the consignment | `P09` | Delivered |

### 5.4 Inter-branch and warehouse transfer

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 22 | R18 | Raise the transfer; source Branch Manager approves (`BRU-INV-02`, `SOD-44`) | `SP-004` A-50 |
| 23 | R18 | Pack, seal, and produce `DT-026` stock transfer note and gate pass | `DT-026` |
| 24 | R16 / courier | Move under manifest `DT-027` | `BRU-LOG-01` |
| 25 | Destination R18 | Verify seal, scan, count, and **confirm receipt** — the transfer is not complete until confirmed | `BRU-INV-02` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 3 | Customer not present | Wait the grace period, call twice, record a failed collection with geotagged evidence, re-attempt per policy (`BRU-LOG-08`) | R15 |
| 4 | Device condition differs materially from what was booked | Record and photograph it, tell the customer, and proceed only if they accept the record | R16; R15 if disputed |
| 7 | Item is a restricted item and the rider is not certified | **Do not carry it.** Reassign to a certified carrier (`BRU-LOG-05`) | R15 |
| 7 | Battery swollen or device water-damaged | Special packing per `SP-030`; may not travel with other items | R15 + HSE |
| 8 | Declared value above the threshold | Dual signature and insurance flag required before departure (`BRU-LOG-03`) | R15; CFO informed |
| 12 | **Seal broken, missing or mismatched** | **Stop. Do not open. Photograph. Movement is blocked automatically** (`BRU-LOG-04`). Escalate immediately | R15 + R06 → R05; Security if theft suspected (`SP-005` OP-E11) |
| 14 | Weight or contents discrepancy on opening | As above — incident raised, onward movement blocked | R15 + R06 |
| 18 | Recipient is not the named customer and not a nominated person | **Do not hand over.** Return to branch. No exceptions at the door | R15 |
| 18 | Recipient refuses to accept | Record the reason, return to origin, apply charge rules (`BRU-LOG-08`) | R15 |
| 19 | Customer disputes the amount due | Do not hand over against an unpaid disputed balance without R06 authority; route to `SP-028` | R06 |
| 20 | POD capture fails (no signal, dead device) | Capture on the paper manifest with signature, photograph it, and sync within 24 hours. **A consignment is never closed without POD** | R15 |
| — | Vehicle accident with a customer device on board | Safety first (`SP-030`); then secure and photograph the device; treat as a custody incident | HSE + R15 → R05 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Inter-branch stock transfer | Any | Source R06 Branch Manager; destination confirms receipt (`SP-004` A-50) | R17 Inventory Manager |
| Inter-branch transfer above the value threshold — raise and approve separated | Any | Different people (`SOD-44`) | R17 |
| Waive a logistics charge | Automatic where entitled (`BRU-LOG-07`) | Computed | — |
| Waive a logistics charge outside entitlement | ≤ BDT 1,000 | R15 Logistics Coordinator | R06 |
| Carry a consignment above the declared-value threshold | Any | R15 with dual signature and insurance flag | CFO |
| Release a device to someone other than the named customer | Any | R06 Branch Manager, with recorded authority from the customer | R05 |
| Write off a device lost in transit | ≤ BDT 25,000 | R17 Inventory Manager | CFO above (`SP-004` A-48) |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Seal break or weight discrepancy | Movement blocked automatically; photograph; do not open | R15, R06 → R05; Security if theft suspected | Custody incident (`BRU-LOG-04`) |
| Device lost in transit | Treat as a custody incident from the outset, not an administrative delay. Inform the customer within the same business day | R15 → R05; CFO; Legal if a claim is likely | Loss record; ISO 8.5.3 report |
| Device damaged in transit | Photograph, quarantine, assess against the collection condition record | R15, R32 Quality Manager | Damage record → `SP-028` |
| Courier partner fails to deliver within the promise | Re-attempt per policy, then escalate to the partner's account manager | R15 → R19 Procurement | Vendor performance (`M42`) |
| Restricted item found in a load without certification | Stop the movement; offload safely | R15 + HSE | Safety record |
| Rider unreachable during a run | Contact per the lone-worker protocol; escalate as a welfare concern if unresolved | R15 → R06 → HSE | Lone-worker log |
| `P09` unavailable | Fallback in §9 | R15, R33 via `SP-031` | Paper manifest |
| Cash collected on delivery not reconciled at shift end | Zero tolerance for unexplained variance (`BRU-LOG-06`) | R15 + R26 Finance Manager | `SP-019` |
| Repeated failed deliveries to one address | Contact the customer to re-arrange; after the configured attempts the device returns to branch and the uncollected clock starts (`BRU-SRM-16`) | R15 → R06 | Order note |

---

## 9. Manual Fallback

Logistics cannot stop when `P09` does. Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Coordinator issues a **pre-numbered paper manifest** listing every item, serial and seal number |
| 2 | Each custody transfer is signed by both parties on the manifest, with printed name and mobile number |
| 3 | Condition photographs are taken on the rider's phone; image references noted against the item line |
| 4 | POD is captured on the manifest: recipient name, signature, NID last four digits, time |
| 5 | Payment uses the **pre-numbered manual receipt book** (`SP-019`) |
| 6 | **Back-enter every manifest within 24 hours**, preserving original timestamps and seal numbers |
| 7 | R15 reconciles paper manifests against the system and signs the reconciliation |

> Seal numbers remain the primary control during an outage. The seal is a physical control that
> does not depend on any system, which is why it is mandatory rather than optional.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| No custody transfer without a scan and dual identity capture | Preventive (`BRU-LOG-01`) | Per transfer | Hard block |
| Consignment cannot close without POD | Preventive (`BRU-LOG-02`) | Per consignment | Hard block |
| Seal break blocks onward movement automatically | Preventive (`BRU-LOG-04`) | Per event | Hard block + incident |
| Restricted items only with a certified carrier | Preventive (`BRU-LOG-05`) | Per load | Hard block |
| Above-threshold consignments require dual signature and insurance flag | Preventive (`BRU-LOG-03`) | Per consignment | Hard block |
| Seal stock is controlled and ranges are reconciled | Preventive | Weekly | Seal register |
| Rider cash reconciled per rider per shift | Preventive (`BRU-LOG-06`) | Per shift | Reconciliation record |
| Custody-chain completeness report | Detective | Daily | `KPI-019` |
| On-time collection and delivery | Detective | Daily | `KPI-018` |
| Transit damage and loss trend | Detective | Monthly | Loss register → `SP-029` |
| Route and POD audit by `P11` field auditor | Detective | Sampled | Audit record |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Raise an inter-branch transfer | Approve it above the value threshold (`SOD-44`) | Threshold block | At single-person sites, approval routes to R17 Inventory Manager off-site |
| Collect cash on delivery | Reconcile the cash book (`SOD-12`) | Hard block at assignment | Rider hands cash to R29 Cashier against a receipt; reconciliation performed by another person |
| Report an item lost in transit | Approve its write-off (`SOD-51`) | Hard block | Write-off approval sits with R17 or CFO |
| Flag a device lost or stolen | Clear that flag (`SOD-54`) | Hard block | — |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-018` | On-time collection and delivery | unmeasured | 90%; stretch 93% |
| `KPI-019` | Chain-of-custody exceptions | untracked | **Zero** |
| POD completeness | Consignments closed with a complete `DT-028` | unmeasured | 100% |
| Transit loss value | Value of devices lost in transit per period | untracked | Zero |
| Seal reconciliation exceptions | Seals issued but unaccounted | untracked | Zero |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-026` Stock Transfer Note and Gate Pass | Inter-branch movement |
| `DT-027` Delivery Challan and Logistics Manifest | The manifest at step 24 |
| `DT-028` Proof of Delivery and Custody Record | The POD at step 20 |
| `UI-019` `P09` Logistics and Rider App UI Copy Pack | The screens used |
| [`SP-007_SOP_Walk_In_Intake_and_Front_Desk.md`](SP-007_SOP_Walk_In_Intake_and_Front_Desk.md) | The counter equivalent of the custody transfer |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](SP-010_SOP_Workshop_and_Depot_Repair.md) | Receives the device at step 15 |
| [`SP-019_SOP_Cash_Collection_and_Banking.md`](SP-019_SOP_Cash_Collection_and_Banking.md) | Cash on delivery |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Restricted items and road incidents |
| [`../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | §11 |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-023_Unit_of_Measure_and_Packaging_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-023_Unit_of_Measure_and_Packaging_Register.md) | Packing standards |
| `TR-020` Course Pack — Rider and Logistics | Trains this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Operations Director (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Every custody transfer point names both parties and the evidence
- [x] Seal-break path stops the process rather than logging it
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback preserves the seal as the primary physical control
- [x] Segregation of duties cites `SP-006`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
