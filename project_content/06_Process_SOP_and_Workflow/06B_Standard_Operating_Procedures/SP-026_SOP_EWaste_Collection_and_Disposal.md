---
id: SP-026
title: SOP — E-Waste Collection and Disposal
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Sustainability
author: Business Process Lead with Sustainability and Quality
reviewers: [Quality Manager, Legal Counsel, CFO, Operations Director, HSE Lead, Data Protection Officer, Localisation Lead]
approver: Chief Financial Officer with Legal Counsel
content_class: C
purpose: >
  Environmental non-compliance is a regulatory and reputational risk that corporate clients
  audit. No device leaves for recycling without a certified wipe or physical destruction record,
  e-waste may be transferred only to a partner whose certification is current at the transfer
  date, and every recycled unit must have a retrievable disposal certificate. This SOP operates
  those three rules across collection, segregation, hazardous handling, partner transfer,
  certification and material-recovery reporting.
traces_to: [M18, M06, M15, M17, DT-035, DT-034, MD-047, LG-020, SP-004, SP-005, SP-012, SP-018, SP-025, SP-030]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: SP-026_SOP_EWaste_Collection_and_Disposal_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M18_EWaste_Recycling_and_Circular_Economy.md — triage assessor and transfer authoriser for the same item are incompatible
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §9 BRU-ESG-01…BRU-ESG-04; §12.3 AUT-040
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-083 e-waste diversion from landfill 92%, KPI-084 disposal certificates on file 100%
    verified: 2026-08-15
    class: P1
  - source: Bangladesh Hazardous Waste (E-waste) Management Rules 2021, made under the Bangladesh Environment Conservation Act 1995 and published by the Department of Environment on 10 June 2021 — registration of manufacturers, traders, sellers, transporters, repairers, collection centres, recyclers and dismantlers with the DoE; approved e-waste management plan; phased collection targets
    verified: 2026-08-15
    class: P2
  - source: ISO 9001:2015 clause 8.5.4 preservation and clause 8.7 control of nonconforming outputs; ISO 14001 alignment noted but not certified
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — E-Waste Collection and Disposal

| Item | Value |
|---|---|
| SOP ID | `SP-026` |
| Process owner | Sustainability lead, accountable to CFO |
| Roles performing | Sustainability lead · `R25` Retail / Refurbishment Officer · `R18` Branch Store Keeper · `R32` Quality Manager · `R14` Data Services Technician · `R38` recycling partner |
| Systems used | `P03` (`UI-027`, `UI-031`) · `M18` · `M15` · `M17` |
| Frequency / volume | Continuous accumulation; batched transfer on the partner schedule |
| ISO 9001 clause reference | 8.5.4 preservation · 8.7 nonconforming outputs · 8.4 externally provided processes (the recycling partner) |

> ⚠ **Regulatory content.** The Bangladesh Hazardous Waste (E-waste) Management Rules 2021 impose
> registration and reporting obligations. The citation below is drawn from secondary sources and
> is marked **class P2**. **Legal Counsel must confirm which obligations apply to 1000FiX and in
> which capacity — repairer, collection centre, trader — before this file leaves `Draft`**
> (action O-01, §14).

---

## 1. Purpose and Outcome

**Purpose.** To collect, segregate, store and dispose of end-of-life electronic equipment
lawfully and safely, with no customer data leaving the company on it, through partners who are
certified at the moment of transfer, and with a certificate retrievable for every unit.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| No device left without a certified wipe or physical destruction record | `BRU-ESG-01` |
| Every partner's certification was current **at the transfer date** | `BRU-ESG-02` |
| Every recycled unit has a retrievable disposal certificate | `BRU-ESG-03`, `KPI-084` |
| Hazardous items followed their specific handling, storage and transport rules | `BRU-ESG-04` |
| Diversion from landfill reaches 92% | `KPI-083` |
| Corporate clients can obtain evidence for their own ESG reporting | `DT-035` |

---

## 2. Scope

**Applies to:** end-of-life devices arising from repair, trade-in, refurbishment failure, rental
retirement and internal asset disposal; batteries and other hazardous components; packaging and
consumable waste arising from service; and the transfer of all of these to authorised partners.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Data erasure method and certification | `SP-012` — this SOP consumes it |
| Refurbishment and resale of viable units | `SP-025` |
| Parts harvested back into serviceable stock | `SP-016` |
| Return of defective parts to a supplier | `SP-017` |
| General facility waste that is not e-waste or hazardous | `M47` facilities |
| Customer-owned devices still in custody | `SP-007`, `SP-009` — these are not waste until ownership transfers |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| E-waste | End-of-life electrical and electronic equipment and its components |
| Triage | The assessment deciding whether an item is repairable, harvestable or waste |
| Hazardous item | Battery, refrigerant, mercury-containing lamp, CRT, or any item classified as hazardous |
| Batch | A grouped set of items transferred together under one manifest |
| Authorised partner | A recycler or dismantler holding a current authorisation, recorded in `MD-047` |
| Material recovery | The reported outcome of what the partner recovered from the batch |
| Diversion | The proportion of e-waste kept out of landfill |
| Disposal certificate | `DT-035` — the retrievable evidence for a unit or batch |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Item declared end-of-life | `SP-025` triage, or asset retirement | The decision is recorded, with who made it |
| Data destruction certificate | `SP-012` | **Required before the item may leave** (`BRU-ESG-01`) |
| Partner register with current authorisations | `MD-047` | Certification validity checked at the transfer date, not at onboarding (`BRU-ESG-02`) |
| Segregated, secure storage | `M47` | Hazardous items stored per their rules (`BRU-ESG-04`) |
| Transport arrangements | `SP-009` | Restricted items only with a certified carrier (`BRU-LOG-05`) |
| Regulatory position confirmed | Legal Counsel | Which obligations apply to 1000FiX under the 2021 Rules — see O-01 |

---

## 5. Procedure

### 5.1 Triage and declaration

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | R25 / R10–R12 | Assess the item: repairable, harvestable for parts, or waste | `P03` | Triage record |
| 2 | R25 | Record the decision with its reason. **The person who declares an item worthless may not alone authorise its transfer** (`SOD-57`) | `P03` | Declaration |
| 3 | R17 | Where parts are harvestable, remove and record them into stock before the remainder becomes waste | `SP-016` | Parts recovery |
| 4 | System | Verify a destruction certificate exists; batch for transfer only if it does (`AUT-040`, `BRU-ESG-01`) | `M18` | Hard block or batching |

### 5.2 Data destruction

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 5 | R14 / trained operator | Erase or physically destroy the storage medium to the applicable standard, with operator and witness (`SOD-58`) | `SP-012` §5.4 | `DT-034` certificate |
| 6 | R14 | Photograph destroyed media with identifiers visible | `P03` | Photographic evidence |
| 7 | System | Bind the certificate to the item record so it is retrievable per unit | `M17` | Certificate binding |

### 5.3 Segregation and storage

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 8 | R18 | Segregate by material stream and by hazard class | `MD-047` | Segregation record |
| 9 | R18 | Store hazardous items per their specific rules — ventilation, containment, separation, fire precautions (`BRU-ESG-04`) | `M47`, `SP-030` | Storage compliance |
| 10 | R18 | **Store batteries separately, in fire-resistant containment, away from other stock.** Damaged and swollen cells are isolated individually | `SP-030` | Battery storage record |
| 11 | R18 | Record accumulated quantities; do not exceed the site's permitted holding | `M18` | Holding record |

### 5.4 Partner transfer

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 12 | Sustainability lead | **Verify the partner's authorisation is current at the transfer date** (`BRU-ESG-02`) | `MD-047` | Authorisation check |
| 13 | Sustainability lead | Compose the batch: item list, serials, weights, material composition, hazard classes | `M18` | Batch manifest |
| 14 | R32 | **Approve the batch release. The preparer may not approve** (`SP-004` A-74) | `P03` | Release approval |
| 15 | R18 + partner | Transfer under custody with scan and dual identity (`BRU-LOG-01`, `SP-009`) | `P09`/`P03` | Custody transfer |
| 16 | Sustainability lead | Obtain the partner's receipt and, subsequently, the material-recovery report | `M18` | Receipt and recovery report |
| 17 | Sustainability lead | Issue `DT-035` disposal and material recovery certificate; bind it to every unit in the batch (`BRU-ESG-03`) | `DT-035` | Certificate issued |
| 18 | Sustainability lead | Make certificates available to corporate clients for their ESG reporting | `P04` | Client availability |

### 5.5 Reporting

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 19 | Sustainability lead | Report volumes, diversion rate and material recovery monthly | `KPI-083` |
| 20 | Sustainability lead | Report certificate completeness — target 100% | `KPI-084` |
| 21 | Sustainability lead | Make any regulatory return required of 1000FiX under the 2021 Rules, on its due date | Legal Counsel, O-01 |
| 22 | R32 | Include e-waste handling in the internal audit programme | `SP-029` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 2 | The triage assessor is also the only available transfer authoriser | The transfer waits (`SOD-57`). A single person deciding an item is worthless **and** sending it away is the classic asset-diversion pattern | R32 |
| 4 | No destruction certificate exists | **Blocked** (`BRU-ESG-01`, `AUT-040`). The item does not move | — |
| 5 | The device will not power on and its storage cannot be erased logically | Physically destroy the storage medium and certify that | R14 + witness |
| 9 | A hazardous item's handling rule is unclear | Do not improvise. Hold it segregated and seek the rule | HSE + Legal |
| 10 | A battery is swollen, leaking or hot | Isolate immediately in fire-resistant containment; treat as a safety event (`SP-030`) | HSE |
| 11 | Accumulated holding approaches the permitted limit | Arrange transfer before the limit, not after. Exceeding a permitted holding is a regulatory breach | Sustainability lead → CFO |
| 12 | Partner authorisation has lapsed or cannot be verified | **Do not transfer** (`BRU-ESG-02`). Use another authorised partner or continue lawful storage | Sustainability lead |
| 13 | An item in the batch still holds customer data | Remove it from the batch; certify it; then reinstate | R14, DPO |
| 16 | The partner does not return a material-recovery report | Chase; escalate; a partner who cannot evidence recovery cannot evidence lawful disposal | Sustainability lead → CFO |
| 17 | A certificate cannot be produced for a unit | The unit is a gap in the register (`BRU-ESG-03`). Investigate; do not close the batch | R32 |
| — | A corporate client requests evidence for a device they supplied | Provide the certificate; this is a contracted deliverable, not a favour | Account Manager |
| — | E-waste is offered informally to staff or third parties | Refused. Disposal is through authorised routes only, and data-bearing devices never leave informally | Sustainability lead |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Declare an item end-of-life | Any | R25 or R10–R12 with a recorded reason | R32 |
| E-waste batch release | Any | R32 Quality Manager; **preparer excluded** (`SP-004` A-74, `SOD-57`) | Sustainability lead's manager |
| Data destruction | Any | Operator + distinct witness (`SP-004` A-75, `SOD-58`) | — |
| Transfer to a partner whose authorisation is not current | **None — class H, no override** (`BRU-ESG-02`) | — | — |
| Exceed the permitted site holding | **None — regulatory limit** | — | — |
| Write off the residual value of scrapped assets | ≤ BDT 25,000 / > 25,000 | R17 / CFO (`SP-004` A-47/A-48) | CEO |
| Onboard a new recycling partner | Any | Sustainability lead + Legal Counsel, recorded in `MD-047` | CFO |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Item transferred without a destruction certificate | **L4-direct: CTO + DPO + Legal.** Recall from the partner if possible | As stated | Data-protection exposure |
| Partner authorisation lapsed mid-relationship | Suspend transfers immediately; verify past transfers made while lapsed | Sustainability lead, Legal (`SP-005` L5) | Compliance record |
| Battery fire or thermal event in storage | Emergency response (`SP-030`); assess the storage arrangement, not only the cell | HSE, R05, CEO | Safety incident |
| Hazardous item found in general waste | Retrieve if safe; investigate the segregation failure | HSE, R32 | Nonconformity |
| Certificate missing for a disposed unit | Reconstruct from the batch manifest and the partner receipt; where impossible, record the gap honestly | R32 | `KPI-084` exception |
| Partner cannot evidence lawful downstream disposal | Suspend; audit the partner; consider termination | Sustainability lead, CFO, Legal | Partner audit |
| Regulatory inspection or enquiry | **Direct to CFO + Legal Counsel. No one else responds to a regulator** (`SP-005` §4.8) | As stated | Restricted record |
| Diversion rate falling | Investigate the material streams and the partner mix | Sustainability lead | `KPI-083` review |
| E-waste accumulating beyond the holding limit | Arrange emergency transfer; report the breach if the limit was exceeded | CFO, Legal | Compliance record |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | Triage, batching and transfer are recorded on the **pre-numbered manual e-waste batch sheet**: item, serial, weight, hazard class, destruction certificate reference |
| 2 | Destruction certification follows the `SP-012` §9 manual path — operator and witness, wet ink, photographed |
| 3 | **Partner authorisation is verified from the paper certificate held on file, dated.** The `BRU-ESG-02` check is not waived because a system is down |
| 4 | Custody transfer is signed by both parties on the batch sheet |
| 5 | **Back-enter every batch within 48 hours**, binding certificates to unit records |
| 6 | R32 reconciles batch sheets against the system and signs |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| No transfer without a certified wipe or destruction record | Preventive (`BRU-ESG-01`, `AUT-040`) | Per item | Hard block |
| Partner certification current at the transfer date | Preventive (`BRU-ESG-02`) | Per transfer | Hard block |
| Retrievable disposal certificate per unit | Preventive (`BRU-ESG-03`) | Per unit | Certificate binding |
| Hazardous handling, storage and transport rules applied | Preventive (`BRU-ESG-04`) | Continuous | Storage compliance |
| Triage assessor ≠ transfer authoriser | Preventive (`SOD-57`) | Per batch | Hard block |
| Destruction operator ≠ witness | Preventive (`SOD-58`) | Per destruction | Certificate |
| Restricted items only with certified carriers | Preventive (`BRU-LOG-05`) | Per movement | Hard block |
| Site holding within permitted limits | Preventive | Continuous | Holding record |
| Partner authorisation expiry monitoring | Detective | Monthly | `MD-047` review |
| Certificate completeness | Detective | Monthly | `KPI-084` |
| Diversion rate and material recovery | Detective | Monthly | `KPI-083` |
| Partner audit | Detective | Annually | Audit record |
| Internal audit of e-waste handling | Detective | Per audit plan | `SP-029` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Triage an item as waste | Authorise its transfer out (`SOD-57`) | Hard block | Batch release approval routes to R32, who may be remote |
| Perform a data destruction | Witness it (`SOD-58`) | Hard block | **None** |
| Prepare a disposal batch | Approve it (`SOD-23` pattern) | Hard block | — |
| Onboard a recycling partner | Approve payments to that partner | Hard block (`SOD-01`) | Payment approval sits with Finance |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-083` | E-waste diversion from landfill | no baseline stated in `06-02` | 92% |
| `KPI-084` | Disposal certificates on file | no baseline stated in `06-02` | **100%** |
| Items transferred without a destruction certificate | Control violations | untracked | **Zero** |
| Transfers to a partner with lapsed authorisation | Compliance violations | untracked | **Zero** |
| Hazardous storage nonconformities | Findings per audit | untracked | Zero |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-035` E-Waste Disposal and Material Recovery Certificate | Issued at step 17 |
| `DT-034` Data Destruction Certificate | Precondition at step 5 |
| `LG-020` Environmental and Circular Economy Policy | The policy this SOP operates |
| [`SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) | Destruction method and certification |
| [`SP-025_SOP_TradeIn_Refurbishment_and_Resale.md`](SP-025_SOP_TradeIn_Refurbishment_and_Resale.md) | Source of failed units |
| [`SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) | Custody on transfer; restricted-item carriage |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Battery and hazardous handling safety |
| [`SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md`](SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md) | Segregated storage discipline |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md) | Material streams and authorised partners |
| `TR-002` Role-Based Curriculum Map | **No course pack exists for the Sustainability role** — gap raised in `AUDIT-006` |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | CFO with Legal Counsel (pending) |

**Open items**

| # | Item | Owner | Needed by |
|---|---|---|---|
| O-01 | **Confirm which obligations under the Bangladesh Hazardous Waste (E-waste) Management Rules 2021 apply to 1000FiX, in which registered capacity (repairer, collection centre, trader), and what registration, management plan, collection targets and returns follow.** Cited here at class **P2** from secondary sources; a Class-C file operating a regulatory duty still requires a primary source under `CG-012` | Legal Counsel + Sustainability lead | **Before `Approved`** |
| O-02 | Record confirmed permitted holding limits per site in `MD-047` and in `MD-003` | Sustainability lead | Before W5 |
| O-03 | Verify each partner's authorisation and record its expiry in `MD-047` with a monitoring rule | Sustainability lead | Before W5 |
| O-04 | Decide whether ISO 14001 certification is pursued; this SOP is written to be compatible with it but does not assume it | CFO | Before W6 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Destruction certificate stated as a hard precondition to any movement
- [x] Partner authorisation checked at the transfer date, not at onboarding, including in the manual fallback
- [x] Battery storage and thermal-event handling specified
- [x] Regulatory enquiry routed to CFO and Legal only
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **O-01 regulatory position confirmed against the enacted Rules — outstanding; blocks `Approved`**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approvers recorded — **pending CFO and Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
