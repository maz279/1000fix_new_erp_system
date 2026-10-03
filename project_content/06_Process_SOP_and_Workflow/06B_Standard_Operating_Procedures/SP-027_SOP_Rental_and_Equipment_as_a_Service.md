---
id: SP-027
title: SOP — Rental and Equipment-as-a-Service
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Rental Operations
author: Business Process Lead with Retail and Rental Operations
reviewers: [CCO, CFO, Legal Counsel, Operations Director, Quality Manager, Inventory Manager, Localisation Lead]
approver: Chief Commercial Officer with Legal Counsel
content_class: C
purpose: >
  Equipment-as-a-Service places company assets in customer hands. A rental asset cannot be
  dispatched without a completed pre-dispatch condition report, the agreement requires a signed
  condition report and the deposit before handover, damage charges derive from the difference
  between outbound and inbound condition reports, and a returned asset re-enters the pool only
  after cleaning, servicing and a functional test. This SOP is the explicit recovery and damage
  process those rules imply.
traces_to: [M13, M17, M45, M20, M53, DT-037, LG-017, MD-044, MD-046, SP-004, SP-005, SP-009, SP-010, SP-019, SP-028]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: SP-027_SOP_Rental_and_Equipment_as_a_Service_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M13_Rental_and_Equipment_as_a_Service.md — inbound condition inspector and damage assessment approver are incompatible
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §9 BRU-RNT-01…BRU-RNT-05
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-075 rental fleet utilisation 68%, KPI-076 rental damage recovery rate 85%
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.5.1 controlled conditions and clause 8.5.5 post-delivery activities
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Rental and Equipment-as-a-Service

| Item | Value |
|---|---|
| SOP ID | `SP-027` |
| Process owner | Chief Commercial Officer; executed under Rental Operations |
| Roles performing | `R25` Retail / Refurbishment Officer · Retail Manager · `R22` Account Manager · `R18` Branch Store Keeper · `R10`–`R12` Technicians · `R26` Finance Manager |
| Systems used | `P03` (`UI-027`, `UI-032`) · `M13` · `M17` · `M45` · `M20` |
| Frequency / volume | Fleet-scale; target 68% utilisation (`KPI-075`) |
| ISO 9001 clause reference | 8.5.1 controlled conditions · **8.5.5** post-delivery activities · 8.5.3 customer property (customer data on rented devices) |

---

## 1. Purpose and Outcome

**Purpose.** To place company-owned equipment with a customer against a contract and a deposit,
support it in life, recover it in a known condition, charge fairly for damage, and return it to
the available pool fit for the next hire.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| No asset was dispatched without a completed pre-dispatch condition report | `BRU-RNT-01` |
| The agreement was signed and the deposit received before handover | `BRU-RNT-02`, `DT-037` |
| Damage charges derive from the outbound-versus-inbound difference, not from opinion | `BRU-RNT-03` |
| Discretionary charges were approved, not applied at the counter | `SP-004` A-73 |
| The asset re-entered the pool only after cleaning, servicing and a functional test | `BRU-RNT-04` |
| Overdue rentals accrued per the tariff with escalating notice | `BRU-RNT-05` |
| Damage recovery reaches 85% | `KPI-076` |

---

## 2. Scope

**Applies to:** short-term and long-term rental of company-owned devices and equipment,
equipment-as-a-service arrangements, swap and replacement during hire, recovery, damage
assessment, and return to the available pool.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Sale of refurbished equipment | `SP-025` |
| Repair of a customer's own device | `SP-010` |
| AMC and managed-service contracts | `SP-015` |
| Internal asset issue to employees | `SP-023` step 11, `M45` |
| Delivery and collection logistics | `SP-009` |
| Disposal of retired rental assets | `SP-026` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Rental asset | Company-owned equipment in the rental pool, registered in `M45` |
| Condition report | The structured, photographed record of an asset's state at a point in time |
| Outbound / inbound | The condition reports taken at dispatch and at return |
| Deposit | The security amount held against damage, loss or non-return |
| Swap | Replacement of a rented asset during the hire, with both condition reports taken |
| Fair wear and tear | Deterioration expected from normal use, not chargeable |
| Overdue | Continued possession past the agreed return date |
| Pool | The set of assets available to rent |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Asset registered and in the pool | `M45`, `M17` | Serial, specification and ownership recorded |
| Asset serviced and functionally tested | `BRU-RNT-04` | An asset returning to the pool untested becomes the next customer's complaint |
| Rental agreement template | `LG-017`, `DT-037` | Terms approved by Legal; not negotiated per hire |
| Tariff and deposit schedule | `M11` | Effective-dated |
| Fair-wear-and-tear definition | `LG-017` | Published, so that damage charging is defensible |
| Insurance position | CFO | What is insured, what is the customer's liability |
| Calibration where applicable | `MD-046` | Test and measurement equipment must be in calibration when rented |

---

## 5. Procedure

### 5.1 Booking and contracting

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | R25 / R22 | Check availability for the requested period; reserve the asset | `M13` | Reservation |
| 2 | R25 | Verify the customer: identity, address, and creditworthiness where the value requires it | `M33` | Verification |
| 3 | R25 | Issue the rental agreement from `DT-037`: term, tariff, deposit, liability, return condition standard | `DT-037` | Agreement issued |
| 4 | Customer | Sign the agreement | `M24` | Signed agreement |
| 5 | R26 | Receive the deposit. **Handover does not occur before the deposit is received** (`BRU-RNT-02`) | `M20`, `SP-019` | Deposit record |

### 5.2 Pre-dispatch and handover

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 6 | R18 / R10–R12 | Complete the **outbound condition report**: functional test, cosmetic state, accessories, meter readings, photographs of every face (`BRU-RNT-01`) | `P03` capture | Outbound report |
| 7 | R18 | Confirm calibration validity where applicable | `MD-046` | Calibration record |
| 8 | R25 | Review the report with the customer; both acknowledge it | `P03` | Joint acknowledgement |
| 9 | R25 / R16 | Hand over with custody scan and identity capture (`SP-009`) | `P09`/`P03` | Custody transfer |
| 10 | R25 | Brief the customer: correct use, what is fair wear, what is chargeable, what to do on fault | — | Briefing recorded |

### 5.3 In-life support

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 11 | R25 | Handle faults during hire: repair on site, swap, or recover and replace | `SP-008`, `SP-010` |
| 12 | R25 | On a swap, take an inbound report for the returned asset and an outbound report for the replacement. **Both, every time** | `BRU-RNT-01` |
| 13 | R26 | Bill the rental on the agreed cycle; missed cycles raise an exception, never a silent skip (`BRU-BIL-02`) | `SP-015` |
| 14 | System | On approaching the return date, notify the customer | `NT-*` |
| 15 | System | Where overdue, accrue charges per the tariff with escalating notification (`BRU-RNT-05`) | `M13` |

### 5.4 Return and damage assessment

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 16 | R18 / R10–R12 | Complete the **inbound condition report** to the same structure as the outbound | `P03` capture | Inbound report |
| 17 | System | Compute the difference between outbound and inbound (`BRU-RNT-03`) | `M13` | Difference report |
| 18 | R25 | Classify each difference: fair wear and tear, chargeable damage, missing item, or pre-existing | `P03` | Classification |
| 19 | **Retail Manager — not the inspector** | Approve the damage charge (`SOD-55`, `SP-004` A-73) | `P03` | Charge approval |
| 20 | R25 | Present the charge to the customer with both condition reports side by side | `P03` | Customer notification |
| 21 | R26 | Settle: deduct from the deposit, refund the balance, or invoice the excess | `M20` | Settlement |
| 22 | R25 | Where the customer disputes it, route to `SP-028`. **Do not retain a deposit against a disputed charge without following the process** | `SP-028` | Dispute record |

### 5.5 Return to pool

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 23 | R10–R12 | Clean, service and functionally test. **Only then does the asset re-enter the available pool** (`BRU-RNT-04`) | `SP-010` |
| 24 | R18 | Re-calibrate where applicable | `MD-046` |
| 25 | R25 | Where the asset is no longer serviceable, retire it: data erasure, then disposal or resale | `SP-012`, `SP-025`, `SP-026` |
| 26 | R26 | Depreciate and account per `MD-044` | `SP-020` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 2 | Customer verification is weak for a high-value asset | Require a larger deposit, a shorter term, or decline. Company assets in unverified hands are unrecoverable | Retail Manager |
| 5 | Customer asks to take the asset and pay the deposit later | **Refused** (`BRU-RNT-02`). This is the single most common route to a non-returned asset | — |
| 6 | Pre-dispatch condition report incomplete | **Asset does not dispatch** (`BRU-RNT-01`). Without the outbound baseline, no damage is ever provable | — |
| 7 | Calibration has expired | The asset does not go out. Every measurement the customer takes with it would be void | R32 |
| 12 | A swap is performed without both reports | The chain of condition evidence is broken and damage becomes unattributable | R25 |
| 15 | Asset overdue beyond the escalation ladder | Formal recovery process with legal advice; the deposit is rarely sufficient for a lost asset | Retail Manager → Legal |
| 18 | The classification is arguable | Default to fair wear and tear unless the evidence supports otherwise. A disputed charge costs more than it recovers | Retail Manager |
| 19 | The inspector wishes to approve the charge | **Blocked** (`SOD-55`) | — |
| 20 | The customer denies causing the damage | Present both reports; if the outbound report is weak, the charge is not defensible and should not be pursued | Retail Manager |
| 23 | The asset fails its post-return functional test | It does not re-enter the pool. Repair or retire it | R32 |
| 25 | The asset held customer data | Erase and certify before disposal or resale (`BRU-ESG-01`, `BRU-TRF-01`) | R14 + witness |
| — | Asset not returned and the customer is uncontactable | Treat as a loss; pursue recovery; write off only on approval | CFO |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Discretionary damage charge | Any | Retail Manager (`SP-004` A-73, `BRU-RNT-03`) | CCO |
| Inspect the return + approve the damage charge | **Incompatible** (`SOD-55`) | Different people | — |
| Waive a damage charge | ≤ BDT 10,000 | Retail Manager | CCO |
| Waive a damage charge | > BDT 10,000 | CCO + CFO | CEO |
| Reduce or waive a deposit | Any | Retail Manager, recorded | CFO |
| Extend a hire beyond the agreed term | Any | R25 within the tariff; Retail Manager outside it | CCO |
| Write off a non-returned asset | ≤ BDT 25,000 / > 25,000 | R17 / CFO (`SP-004` A-47/A-48) | CEO |
| Dispatch without a completed condition report | **None — class H, no override** (`BRU-RNT-01`) | — | — |
| Handover before the deposit is received | **None — class H, no override** (`BRU-RNT-02`) | — | — |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Asset returned damaged beyond the deposit | Assess, charge, and pursue the balance; involve the insurer where covered | Retail Manager, R26, CFO | Damage and claim record |
| Asset not returned | Escalating notice per `BRU-RNT-05`; then formal recovery with legal advice | Retail Manager → Legal | Recovery record |
| Asset lost by 1000FiX during delivery or collection | Custody incident (`SP-009`); the customer is not charged | R15, R05 | Custody incident |
| Customer data found on a returned asset | Erase and certify; if it left the company on a re-hired asset, it is a breach | DPO, CTO | Breach register |
| Outbound report missing or inadequate | The charge is not pursued. Record why, and correct the process | Retail Manager, R32 | Nonconformity |
| Safety fault reported by the customer | Stop-use instruction immediately; recover the asset; assess the fleet, not only the unit | HSE, R32, CCO | Safety incident + fleet review |
| Utilisation persistently below target | Fleet mix, pricing or availability is wrong; analyse before buying more assets | CCO, CFO | `KPI-075` review |
| Deposit not refunded promptly on a clean return | Treat as a service failure; deposits held without cause damage trust | R26 | Complaint risk |
| Asset re-entered the pool untested | Control failure; recall it and test | R32 | Nonconformity |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | Condition reports are completed on the **pre-numbered manual condition report form** with photographs taken on a branch camera and referenced |
| 2 | The rental agreement is executed in wet ink from the controlled `DT-037` pack and scanned into `M24` within 2 business days |
| 3 | The deposit is receipted on the pre-numbered manual receipt book (`SP-019` §9) |
| 4 | **Dispatch without a completed condition report remains prohibited.** The form is the control, not the system |
| 5 | Damage assessment uses the two paper reports; approval is signed by the Retail Manager, not the inspector |
| 6 | **Back-enter every agreement, condition report and settlement within 48 hours** |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| No dispatch without a completed pre-dispatch condition report | Preventive (`BRU-RNT-01`) | Per hire | Hard block |
| No handover before signed agreement and deposit | Preventive (`BRU-RNT-02`) | Per hire | Hard block |
| Damage charge derived from the outbound/inbound difference | Preventive (`BRU-RNT-03`) | Per return | Computed |
| Inspector ≠ damage charge approver | Preventive (`SOD-55`) | Per charge | Hard block |
| Asset re-enters the pool only after clean, service and test | Preventive (`BRU-RNT-04`) | Per return | Hard block |
| Overdue charges accrue automatically with notice | Preventive (`BRU-RNT-05`) | Continuous | Computed |
| Calibration validity checked at dispatch | Preventive | Per hire | Calibration record |
| Deposit refunded promptly on clean return | Detective | Weekly | Deposit ageing |
| Damage recovery rate | Detective | Monthly | `KPI-076` |
| Fleet utilisation | Detective | Monthly | `KPI-075` |
| Assets overdue | Detective | Weekly | Overdue register |
| Disputed damage charges | Detective | Monthly | Dispute analysis |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Inspect an asset on return | Approve the damage charge (`SOD-55`) | Hard block | Approval routes to Retail Manager, who may be remote and reviews the photographs |
| Hold the deposit | Approve its retention against damage | Hard block | Deposit settlement sits with Finance |
| Report an asset lost or damaged | Approve its write-off (`SOD-51`) | Hard block | — |
| Value an asset for retirement | Purchase it personally or resell it (`SOD-10`) | Hard block | — |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-075` | Rental fleet utilisation | no baseline stated in `06-02` | 68% |
| `KPI-076` | Rental damage recovery rate | no baseline stated in `06-02` | 85% |
| Assets not returned | Count and value per period | untracked | Falling to near zero |
| Dispatches without a condition report | Control violations | untracked | **Zero** |
| Deposit refund time | Clean return to refund | untracked | To be set |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-037` Rental Agreement and Asset Handover Record | Issued at step 3 |
| `LG-017` Rental and Equipment-as-a-Service Terms | The binding terms, including fair wear and tear |
| `UI-027` Workspace — Inventory Console Copy · `UI-032` Contract Console Copy | The screens used |
| [`SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) | Delivery and collection custody |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](SP-010_SOP_Workshop_and_Depot_Repair.md) | Servicing between hires |
| [`SP-025_SOP_TradeIn_Refurbishment_and_Resale.md`](SP-025_SOP_TradeIn_Refurbishment_and_Resale.md) | Resale of retired assets |
| [`SP-026_SOP_EWaste_Collection_and_Disposal.md`](SP-026_SOP_EWaste_Collection_and_Disposal.md) | Disposal of retired assets |
| [`SP-028_SOP_Complaint_Escalation_and_Compensation.md`](SP-028_SOP_Complaint_Escalation_and_Compensation.md) | Damage charge disputes |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-044_Asset_Class_and_Depreciation_Schedule_Register.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-044_Asset_Class_and_Depreciation_Schedule_Register.md) | Depreciation of rental assets |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md) | Calibration of rented instruments |
| `TR-002` Role-Based Curriculum Map | **No course pack exists for Rental Operations** — gap raised in `AUDIT-006` |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | CCO with Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] The two class-H preconditions (condition report, deposit) stated with no override path
- [x] "Default to fair wear and tear unless the evidence supports otherwise" stated at the decision point
- [x] Weak outbound report explicitly makes a charge unpursuable
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] `LG-017` written with a published fair-wear-and-tear definition — **outstanding; `LG` category not yet authored**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approvers recorded — **pending CCO and Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
