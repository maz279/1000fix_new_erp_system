---
id: SP-013
title: SOP — Estimate, Approval and Rework Control
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations with Quality
author: Business Process Lead with Commercial and Quality
reviewers: [Operations Director, CCO, Quality Manager, Finance Manager, Branch Managers Forum, Legal Counsel, Localisation Lead]
approver: Operations Director
content_class: C
purpose: >
  Estimates are where margin is made or lost and where the second most common customer dispute
  begins — scope growing mid-repair. This SOP governs how an estimate is built from standard
  times and rates, how it is approved, how a revision is handled at the cumulative value rather
  than the delta, how a decline is recorded, and how rework is classified and costed. A repeat
  order for the same device and fault within 30 days is auto-flagged as rework; this SOP defines
  what happens next, which the rule does not.
traces_to: [M36, M11, M01, M23, DT-005, DT-006, MD-025, MD-026, MD-029, SP-004, SP-005, SP-010, SP-029]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: SP-013_SOP_Estimate_Approval_and_Rework_Control_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-06, BRU-SRM-07, BRU-SRM-08, BRU-SRM-13, BRU-SRM-19
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M36_Quotation_Estimation_and_Tender_Management.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md — FR-PRC-035, proposer cannot approve a price change or below-floor discount
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-008 estimate approval conversion, KPI-005 rework rate, KPI-033 gross margin on paid repair
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.2.2 and 8.2.3 — determining and reviewing requirements for products and services before committing to supply
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Estimate, Approval and Rework Control

| Item | Value |
|---|---|
| SOP ID | `SP-013` |
| Process owner | Operations Director (R05) with Quality Manager (R32) for the rework path |
| Roles performing | `R08` Service Centre Agent · `R09` Workshop Supervisor · `R10`–`R12` Technicians · `R06` Branch Manager · `R32` Quality Manager |
| Systems used | `P03` (`UI-038` estimate and approval flow) · `P02` · `P01`/`P04` customer approval · `M36` · `M11` |
| Frequency / volume | Every chargeable service order; the primary commercial control in the service business |
| ISO 9001 clause reference | **8.2.3** review of requirements before commitment · 8.7 nonconforming outputs (rework) · 10.2 nonconformity and corrective action |

---

## 1. Purpose and Outcome

**Purpose.** To produce an estimate the customer understands and accepts, to obtain and record
approval at the right authority, to handle scope growth without dispute, and to identify and cost
rework so that it is corrected rather than absorbed.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Every estimate is built from `MD-025` standard actions and `MD-029` rates, not from judgement | Estimate line source |
| Approval is documented above BDT 5,000 and branch-approved above BDT 25,000 | `BRU-SRM-07`, `BRU-SRM-08` |
| Revisions are approved at the **cumulative** value | `SP-004` A-05 |
| Expired estimates are re-issued, never extended | `BRU-SRM-13` |
| Declines carry a reason code that feeds pricing | `MD-026` |
| Rework is classified, costed and attributed, not silently repeated | `BRU-SRM-06` → `SP-029` |

---

## 2. Scope

**Applies to:** repair estimates and quotations for consumer and corporate service work, at the
counter, in the workshop and in the field; their revision; their decline; and the classification
and cost attribution of rework.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Contract and AMC quotation | `SP-015` |
| Tender and large corporate bid | `M36` tender path; `SP-015` for the contract that follows |
| Rate card and price-floor setting | `M11`, approved per `SP-004` A-15/A-16 |
| Warranty work, where the brand pays | `SP-014` — no customer estimate, but the same evidence discipline |
| Trade-in valuation | `SP-025` |
| The quality audit and CAPA process that rework feeds | `SP-029` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Estimate | A priced proposal for identified work, with a stated validity period (`DT-005`) |
| Revision | A changed estimate on the same order, issued as `DT-006` with the delta and the cumulative total both shown |
| Validity | The period during which the estimate stands; it expires rather than lapses (`BRU-SRM-13`) |
| Decline | The customer's refusal, recorded with a reason code from `MD-026` |
| Rework | A repeat order for the same device and fault category within 30 days (`BRU-SRM-06`) |
| Warranty rework | Rework inside the repair warranty period — not chargeable to the customer |
| Cost attribution | Assignment of rework cost to its cause: technician, part, diagnosis, process or customer |
| Standard time | The `MD-025` labour allowance for a repair action |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Completed diagnosis with a fault code | `SP-008`, `SP-010` | An estimate before diagnosis is a guess and is prohibited |
| Current rate card | `MD-029` | Effective-dated; the version in force at the order date applies |
| Standard repair actions and times | `MD-025` | The estimate's labour line must be traceable to an action code |
| Parts prices and availability | `M15` | An estimate quoting an unavailable part sets a date it cannot meet |
| Entitlement resolved | `M08`, `M09`, `M10` | Warranty, AMC or Privilege changes what is chargeable (`BRU-WTY-06` — Privilege discounts apply to labour only) |
| Customer contact channel confirmed | `M27` | An estimate the customer never sees expires and is counted as a loss |

---

## 5. Procedure

### 5.1 Build and issue

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R09 / R10–R12 | Confirm the diagnosis and the fault code | `P03` / `P02` | Fault code | 2 min |
| 2 | System | Draft the estimate from the fault code and the standard repair mapping (`AUT-004`) | `M36` | Draft estimate | — |
| 3 | R09 / R08 | Review each line: is the action necessary, is the part correct, is the time the standard time | `P03` | Reviewed lines | 5 min |
| 4 | R09 / R08 | Apply entitlement — warranty, AMC scope, Privilege labour discount (`BRU-WTY-06`) | `P03` | Entitlement applied | 2 min |
| 5 | R09 / R08 | Add taxes, set validity, add any out-of-scope observation as a **separate advisory line, not a charge** | `P03` | Estimate complete | 3 min |
| 6 | R09 / R08 | Check the total against the price floor. Below floor requires CCO approval and **the proposer may not approve** (`SOD-14`) | `P03` | Floor check | 1 min |
| 7 | R09 / R08 | Issue on the customer's preferred channels; the expiry timer starts (`AUT-005`) | `P03` · `NT-*` | `DT-005` issued | 1 min |
| 8 | R09 / R08 | Explain it to the customer in their language: what is wrong, what will be done, what it costs, how long | — | Explanation recorded | 5 min |

### 5.2 Approval

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 9 | Customer | Approve, decline or defer | `P01` / `P04` / signature / OTP | Customer decision |
| 10 | R06 | Where the total exceeds BDT 25,000, add branch manager approval (`BRU-SRM-08`) | `P03` | Internal approval |
| 11 | R05 | Where the total exceeds BDT 100,000, add Operations Director approval | `P03` | Internal approval |
| 12 | System | On approval: reserve parts, release the work order, notify the technician (`AUT-006`) | `M15` · `M01` | Work released |
| 13 | System | At 24h and 48h without a response, remind; at expiry, expire (`AUT-005`, `BRU-SRM-13`) | `NT-*` | Reminder and expiry log |

### 5.3 Revision

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 14 | R10–R12 | **Stop work** the moment the required work exceeds what was approved | `P03` / `P02` | Work paused |
| 15 | R09 | Build the revision, showing the original, the variation, the reason, and the **cumulative total** | `P03` | `DT-006` |
| 16 | R09 | Re-approve at the band of the cumulative total, not the delta (`SP-004` A-05) | `P03` | Re-approval |
| 17 | R09 | Where the customer declines the revision: complete only the originally approved work if that is safe and coherent, otherwise reassemble and return | `P03` | Decision recorded |

### 5.4 Decline handling

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 18 | R08 / R09 | Record the decline with a reason code from `MD-026` — price, time, customer bought a replacement, went elsewhere, no response | `MD-026` |
| 19 | R08 / R09 | Charge only the agreed diagnostic fee; reassemble the device to its intake condition | `SP-004` A-08/A-09 |
| 20 | R08 | Offer the alternatives the decline reason suggests — trade-in (`SP-025`), refurbished replacement, payment plan | `M14`, `M10` |
| 21 | R32 | Review decline reasons monthly; a rising price-decline rate is a pricing signal, not a sales failure | `M11`, `KPI-008` |

### 5.5 Rework control

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 22 | System | Flag a repeat order for the same device and fault category within 30 days; link it to the original (`BRU-SRM-06`, `AUT-011`) | `M01` | Rework flag and link |
| 23 | R32 | Classify the rework cause: **diagnosis** · **workmanship** · **part failure** · **process** · **customer-caused** · **not rework (different fault)** | `P03` · `M23` | Classification |
| 24 | R32 | Attribute cost accordingly — 1000FiX absorbs diagnosis, workmanship and process; part failure is recovered from the supplier (`SP-017`); customer-caused is chargeable | `M54` | Cost attribution |
| 25 | R32 | Where inside the repair warranty period, the customer is **not charged**, regardless of cause other than customer-caused damage | `M09` | Charge decision |
| 26 | R32 | Raise a nonconformity for workmanship, diagnosis and process causes; CAPA follows (`BRU-QMS-02`) | `M23` → `SP-029` | Nonconformity |
| 27 | R32 | Notify the original technician's manager. **The purpose is correction and training, not blame** | `NT-*` | Notification |
| 28 | R32 | Trend rework by technician, device family, fault code and part. A part failing repeatedly is a supplier issue, not a technician issue | `RP-*` | Monthly analysis |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 3 | The drafted estimate is materially above or below the standard | Investigate before issuing. A large variance is either a wrong diagnosis or a wrong standard time | R09 |
| 5 | Additional faults found that the customer did not report | List them as **advisory**, priced separately, and let the customer choose. Never bundle them into the approved figure | R09 |
| 6 | Total falls below the price floor | CCO approval required; **the person proposing may not approve** (`SOD-14`, `SP-004` A-15) | CCO |
| 9 | Customer approves verbally only | Capture OTP or signature. Work above BDT 5,000 does not start on a verbal approval (`BRU-SRM-07`) | R08/R09 |
| 13 | Estimate expires | **Re-issue at current prices. Do not extend the old one** (`BRU-SRM-13`) | R09 |
| 14 | Scope growth is discovered mid-repair with the device already open | Stop and revise. If the customer is uncontactable, the device waits — it is not completed at a higher price and billed afterwards | R09 |
| 16 | Third revision on the same order | Flag to R06 Branch Manager. Repeated revision is a diagnosis defect (`SP-004` §4.5 anti-avoidance) | R06 |
| 17 | Partial completion would leave the device unsafe or non-functional | Do not part-complete. Reassemble to intake condition and return | R09 |
| 23 | Cause is disputed between workshop and quality | R32 decides; the technician may append their statement to the record | R32 |
| 23 | The "rework" is a genuinely different fault | Classify as **not rework** with the evidence. The flag is automatic; the classification is human | R32 |
| 25 | Rework is outside the repair warranty period and not 1000FiX-caused | Chargeable, but explain the analysis to the customer before charging | R06 |
| 27 | The same technician appears repeatedly in workmanship rework | Competence review and re-certification assessment, not a disciplinary reflex | R32 + R30 HR Manager |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Estimate | > BDT 5,000 | Customer + system record (`BRU-SRM-07`) | — |
| Estimate | > BDT 25,000 | Customer + R06 Branch Manager (`BRU-SRM-08`) | R05 |
| Estimate | > BDT 100,000 | Customer + R05 Operations Director | CCO |
| Revised estimate | Cumulative crosses a band | Re-approval at the cumulative band (`SP-004` A-05) | As above |
| Discount | ≤ 10% / ≤ 20% / ≤ 35% / > 35% | R08 / R06 / R21 / CCO (`SP-004` A-11…A-14) | Next level |
| Below price floor | Any | CCO; proposer excluded (`SOD-14`) | — |
| Waive or reduce a diagnostic fee | ≤ 1,000 / > 1,000 | R08 / R06 (`SP-004` A-08/A-09) | R05 |
| Charge a customer for rework inside the repair warranty | Any | R06 Branch Manager, with the classification evidence | R05 |
| Reopen a closed order outside the repair warranty | Any | R06 (`BRU-SRM-19`, class **A**) | R05 |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Work performed above the approved value without re-approval | Stop. Do not bill the excess. Record it as a control breach and review with the technician | R06 → R05 | Control exception; `SP-006` reporting |
| Customer disputes an approved charge | Do not argue at the counter. Route to `SP-028` with the approval evidence | R06 | Complaint record |
| Estimate issued on a wrong diagnosis and accepted | Revise honestly, explain, and absorb the difference where 1000FiX erred | R09 → R06 | Nonconformity |
| Parts price changed between estimate and execution | The estimate stands for its validity period. Margin variance is reported, not passed to the customer | R26 Finance Manager | Margin exception |
| Rework flag raised on a device that is not the same device | Data defect — correct the device identity (`M17`) and re-evaluate | R32, MDM | Data quality record |
| Rework classified as "not rework" repeatedly by the same reviewer | Sampled by internal audit; classification is a control, not an administrative choice | Internal Audit | `SP-029` |
| Estimate never delivered — wrong contact details | Counted as a process failure, not a customer decline. Correct the party record | R08 | `MD-013` data quality |
| Below-floor sale approved by the proposer | `SOD-14` violation; blocked by the engine, reported if attempted | CCO, CFO | `SP-006` exception report |

---

## 9. Manual Fallback

Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Build the estimate on the **pre-numbered manual estimate pad**, using the printed rate card held at every branch and updated at each rate change |
| 2 | Two copies: customer and branch. The customer signs the branch copy |
| 3 | Above BDT 25,000 the Branch Manager countersigns the branch copy at the time — not retrospectively |
| 4 | Telephone approval is acceptable **only** when the approver records it in `P03` at the time; otherwise it is an `SP-004` OF-03 exception reviewed within 24 hours |
| 5 | **Back-enter every manual estimate within 24 hours**, preserving the original date and the approval evidence |
| 6 | R06 reconciles the pad against the system and signs it. Unused pad numbers are accounted for |

> The printed rate card must be reissued to every branch on every rate change. A branch working
> from a superseded printed card during an outage produces unenforceable estimates — this is
> owned by `MD-029` distribution, not by this SOP.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Estimate lines traceable to `MD-025` action codes and `MD-029` rates | Preventive | Per estimate | Line source |
| Documented approval above BDT 5,000 | Preventive (`BRU-SRM-07`) | Per estimate | Hard block |
| Branch manager approval above BDT 25,000 | Preventive (`BRU-SRM-08`) | Per estimate | Hard block |
| Expired estimates cannot be extended | Preventive (`BRU-SRM-13`) | Per estimate | Hard block |
| Below-floor approval separated from proposal | Preventive (`SOD-14`) | Per case | Hard block |
| Revision re-approved at cumulative value | Preventive (`SP-004` A-05) | Per revision | Hard block |
| Rework auto-flagged and linked | Detective → preventive (`BRU-SRM-06`) | Per order | Rework link |
| Third-revision flag | Detective | Per order | Branch manager review |
| Split-transaction detection near band ceilings | Detective (`SP-004` AA-12) | Monthly | Internal Audit report |
| Decline-reason analysis | Detective | Monthly | `KPI-008`, pricing input |
| Rework trend by cause, technician, part and device | Detective | Monthly | `KPI-005` → `SP-029` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Propose a price change or below-floor discount | Approve it (`SOD-14`) | Hard block | — |
| Perform the repair | Classify the rework arising from it (`SOD-19` pattern; classification sits with R32) | Hard block | At single-technician sites, classification is performed remotely by R32 |
| Author a catalogue or standard-time change | Approve it (`SOD-13`) | Hard block | — |
| Create a credit note arising from an estimate dispute | Approve it (`SOD-04`) | Hard block | — |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-008` | Estimate approval conversion | unmeasured | 72%; stretch 78% |
| `KPI-005` | Rework rate | unmeasured | < 5%; stretch < 3% |
| `KPI-033` | Gross margin on paid repair | index only | +2 pts; stretch +4 pts |
| `KPI-032` | Quotation-to-order conversion | unmeasured | 72%; stretch 78% |
| Revision rate | Orders with one or more estimate revisions | untracked | To be set from `SP-002` baseline |
| Rework cost absorbed | Value of rework attributed to 1000FiX causes | untracked | Falling quarter on quarter |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-005` Repair Estimate and Quotation | Issued at step 7 |
| `DT-006` Revised Estimate and Approval Record | Issued at step 15 |
| `UI-038` Estimate and Approval Flow Copy | The screens and messages used |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](SP-010_SOP_Workshop_and_Depot_Repair.md) | Where revision is triggered at the bench |
| [`SP-008_SOP_On_Site_Field_Service_Visit.md`](SP-008_SOP_On_Site_Field_Service_Visit.md) | Field estimating |
| [`SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Consumes the rework nonconformity |
| [`SP-017_SOP_Procurement_to_Payment.md`](SP-017_SOP_Procurement_to_Payment.md) | Recovery of part-failure rework from the supplier |
| [`../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) | §7 bands and A-05 |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Decline reason codes |
| [`../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md`](../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md) | Rates and floors |
| `TR-007` Course Pack — Service Centre Agent · `TR-010` Course Pack — Workshop Supervisor | Train this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Operations Director (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Revision approved at cumulative value, stated explicitly and repeatedly
- [x] Rework classification includes "not rework" as a valid, evidenced outcome
- [x] Cost attribution names who absorbs which cause
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback flags the superseded-rate-card risk it creates
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
