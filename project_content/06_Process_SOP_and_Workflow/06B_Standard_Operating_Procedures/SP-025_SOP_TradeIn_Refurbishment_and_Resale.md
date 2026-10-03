---
id: SP-025
title: SOP — Trade-In, Refurbishment and Resale
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Refurbishment
author: Business Process Lead with Retail and Refurbishment Operations
reviewers: [CCO, CFO, Legal Counsel, Data Protection Officer, Quality Manager, Inventory Manager, Localisation Lead]
approver: Chief Commercial Officer with Legal Counsel
content_class: C
purpose: >
  Trade-in combines a data-protection obligation with an inventory and consumer-sales process,
  and neither can be improvised. No device proceeds to refurbishment or resale without a
  certified data destruction record, no refurbished unit is listed without a completed QA
  protocol and an assigned grade, and battery health and known defects must be disclosed on
  every listing. This SOP is where those three rules are actually operated.
traces_to: [M14, M06, M15, M17, M23, M37, DT-036, DT-038, DT-034, LG-013, LG-019, MD-021, SP-004, SP-005, SP-012, SP-016, SP-026]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: SP-025_SOP_TradeIn_Refurbishment_and_Resale_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M14_TradeIn_Refurbishment_and_Resale.md — QA technician and grade override approver are incompatible
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §9 BRU-TRF-01…BRU-TRF-05, BRU-ESG-01
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-077 refurbishment yield 88%, KPI-078 refurbished units sold per year 12,000
    verified: 2026-08-15
    class: P1
  - source: Bangladesh Consumer Rights Protection Act 2009 — obligations regarding the sale of goods and the prohibition on misleading representation about the condition of goods; specific section references to be confirmed by Legal Counsel
    verified: 2026-08-15
    class: P3
  - source: ISO 9001:2015 clause 8.5.1 controlled conditions, and clause 8.6 release of products and services
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Trade-In, Refurbishment and Resale

| Item | Value |
|---|---|
| SOP ID | `SP-025` |
| Process owner | Chief Commercial Officer; executed under Retail / Refurbishment (R25) |
| Roles performing | `R25` Retail / Refurbishment Officer · Retail Manager · `R14` Data Services Technician · `R32` Quality Manager · `R10`–`R12` Technicians |
| Systems used | `P03` (`UI-027`, `UI-031`) · `M14` · `M17` · `M15` · `M23` |
| Frequency / volume | Target 12,000 refurbished units sold per year at scale (`KPI-078`) |
| ISO 9001 clause reference | 8.5.1 controlled conditions · **8.6** release of products · 8.7 nonconforming outputs · 8.2.1 customer communication |

---

## 1. Purpose and Outcome

**Purpose.** To acquire a customer's device fairly, erase its data verifiably, restore it to a
defensible standard, grade it honestly, disclose its condition, and sell it with a warranty the
company can stand behind.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Provenance and identity checks passed before any offer was paid | `BRU-TRF-02` |
| A certified data destruction record exists before refurbishment or resale | `BRU-TRF-01`, `DT-034` |
| Ownership transfer was documented and signed by the customer | `DT-038` |
| The unit passed the QA test protocol and carries an assigned grade | `BRU-TRF-03` |
| Battery health and known defects are disclosed on the listing | `BRU-TRF-04` |
| Any grade override carries a recorded justification by someone other than the QA technician | `BRU-TRF-05`, `SOD-56` |
| Returns and disputes on refurbished units stay within tolerance | Return rate |

---

## 2. Scope

**Applies to:** trade-in assessment and acquisition; data erasure of acquired devices;
refurbishment; grading and QA; listing, disclosure and sale; refurbished-unit warranty; and
disposition of units that fail refurbishment.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Repair of a customer's own device | `SP-010` |
| Data recovery for a customer | `SP-012`; this SOP consumes its destruction method |
| Disposal of units that cannot be refurbished | `SP-026` |
| Rental asset servicing | `SP-027` |
| Parts harvested from failed units into stock | `SP-016`, with grading per `MD-022` |
| E-commerce storefront operation | `M38` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Trade-in | Acquisition of a customer's device against value, cash or credit |
| Provenance check | Verification that the device is lawfully the customer's to sell, including stolen-device screening where available |
| Erasure | Verified data destruction to the applicable standard (`SP-012`) |
| Refurbishment | Restoration to a defined functional and cosmetic standard |
| Grade | The published condition classification, assigned from the QA outcome |
| Disclosure | The published statement of battery health, known defects and warranty |
| Yield | The proportion of acquired units that reach a saleable grade (`KPI-077`) |
| Override | A supervisor's change to an assigned grade, requiring recorded justification |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Device catalogue and model data | `MD-021` | Model, variant and specification identifiable |
| Trade-in valuation model | `M14`, `M11` | Values effective-dated; not negotiated ad hoc at the counter |
| Grading standard | `M14`, `LG-019` | Grade definitions published and used consistently |
| QA test protocol per device class | `M23` | Defines what "passed" means |
| Erasure capability | `SP-012` | Method, operator and witness available |
| Warranty terms for refurbished units | `LG-013` | Coverage and exclusions defined before sale |
| Consumer disclosure requirements | Legal Counsel | Confirmed against applicable consumer law |

---

## 5. Procedure

### 5.1 Assessment and offer

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | R25 | Identify the device: model, variant, serial or IMEI; register it | `M17` | Device identified |
| 2 | R25 | **Provenance and identity checks**, including stolen-device screening where available (`BRU-TRF-02`) | `P03` | Provenance record |
| 3 | R25 | Functional and cosmetic assessment against the grading standard; photograph | `P03` | Assessment record |
| 4 | R25 | Check battery health and record it — it drives both the offer and the later disclosure | `P03` | Battery health |
| 5 | R25 | Produce the offer from the valuation model, showing the deductions applied and why | `P03` | Offer |
| 6 | Customer | Accept or decline. On decline, return the device as received | `P03` | Decision |

### 5.2 Acquisition and erasure

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 7 | R25 | Execute `DT-038` trade-in offer and acceptance record: assessment, offer, deduction, **ownership transfer declaration** and data-erasure confirmation | `DT-038` | Signed record |
| 8 | R25 | Advise the customer to remove accounts and activation locks; record whether they did | `P03` | Account-removal record |
| 9 | R25 | Pay or credit per the accepted offer | `M20`, `SP-019` | Payment record |
| 10 | R25 | Move the device into refurbishment stock; it is now company property | `M15` | Stock movement |
| 11 | R14 / trained operator | **Erase to the applicable standard, with operator and witness** (`SP-012` §5.4, `SOD-58`) | `SP-012` | `DT-034` destruction certificate |
| 12 | System | Block any onward movement without a certificate on file (`BRU-TRF-01`) | `M14` | Hard block |

### 5.3 Refurbishment and grading

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 13 | R10–R12 | Refurbish: replace failed components, clean, restore firmware to a clean supported state | `P03` · `SP-010` | Work record |
| 14 | R10–R12 | Record every part fitted against the unit | `M15` | Parts record |
| 15 | R32 or QA technician | Run the **full QA test protocol** for the device class; record each result | `M23` | QA record |
| 16 | System | Assign the grade from the QA outcome and the cosmetic assessment | `M14` | Grade assigned |
| 17 | R32 (**not the QA technician**) | Approve any grade override with a recorded justification (`BRU-TRF-05`, `SOD-56`) | `P03` | Override record |
| 18 | R25 | Issue `DT-036` refurbishment grading and certification record: grade applied, tests performed, parts replaced, warranty granted, disclosure statement | `DT-036` | Certificate |

### 5.4 Listing and sale

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 19 | R25 | List only units with a completed QA protocol and an assigned grade (`BRU-TRF-03`) | `M37`, `M38` | Listing |
| 20 | R25 | **Disclose battery health and known defects on the listing** (`BRU-TRF-04`) | `M38` | Disclosure published |
| 21 | R25 | State the grade definition plainly — a grade letter alone is not a disclosure | `M38` · `LG-019` | Grade explanation |
| 22 | R25 | Sell with the refurbished warranty terms attached (`LG-013`) | `M20`, `DT-032` | Sale and warranty |
| 23 | R25 | Handle returns under the published policy; a return within the disclosure period is analysed for grading accuracy | `SP-028` | Return record |

### 5.5 Failed units

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 24 | R25 | Where refurbishment is uneconomic, harvest usable parts into stock with their own grading | `SP-016`, `MD-022` |
| 25 | R25 | Route the remainder to e-waste. **The destruction certificate must already exist** (`BRU-ESG-01`) | `SP-026` |
| 26 | R25 | Record the yield outcome and its cause, so acquisition pricing can learn from it | `KPI-077` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 2 | Provenance cannot be established | **Do not offer.** Return the device and record the reason. Do not accuse the customer | R25 → Retail Manager |
| 2 | Device screens as stolen | Do not pay, do not release, and escalate immediately | Retail Manager → R05 + Legal |
| 4 | Battery is swollen or damaged | Safety handling per `SP-030`; the unit may be non-viable and must not be stored with others | HSE + R25 |
| 5 | Customer disputes the valuation | Explain the deductions from the model. **Do not negotiate outside the model at the counter** — that is how valuation integrity is lost | Retail Manager within `SP-004` A-70/A-71 |
| 8 | Activation lock or account remains on the device | The device cannot be refurbished or resold. Either the customer removes it or the offer is void | R25 |
| 11 | Erasure cannot be completed (device will not boot, storage failed) | Physical destruction of the storage medium, certified, before any onward movement | R14 + witness |
| 12 | A unit is found in refurbishment with no destruction certificate | Stop; quarantine; certify before anything else. This is a data-protection exposure, not a paperwork gap | R32 + DPO |
| 15 | QA fails | Return to refurbishment or route to disposition. **Do not downgrade to avoid a repair** | R32 |
| 17 | The QA technician wishes to change the grade | **Blocked** (`SOD-56`). Override sits with R32 | — |
| 20 | Battery health is poor but the unit is functional | Disclose it plainly and price accordingly. Non-disclosure is the source of returns, disputes and consumer-protection exposure | R25 |
| 23 | Return rate for a grade rises | The grade definition or its application is wrong. Investigate the grading, not only the units | R32 |
| — | A unit is requested for internal use or demonstration | It leaves refurbishment stock through a recorded transfer, never informally | R17 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Trade-in offer | ≤ BDT 30,000 | R25 Retail / Refurbishment Officer (`SP-004` A-70) | Retail Manager |
| Trade-in offer | > BDT 30,000 | Retail Manager + Finance (`SP-004` A-71) | CFO |
| Value a trade-in + purchase it + resell it | **Incompatible** (`SOD-10`) | Different people | — |
| Grade override | Any | R32 Quality Manager, with recorded justification (`SP-004` A-72, `SOD-56`) | Retail Manager |
| Offer outside the valuation model | Any | Retail Manager, with the reason recorded | CCO |
| Data destruction | Any | Operator + distinct witness (`SP-004` A-75, `SOD-58`) | — |
| Sell below the refurbished price floor | Any | CCO; proposer excluded (`SOD-14`) | — |
| Accept a return outside the published policy | Any | Retail Manager | CCO |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Unit found without a destruction certificate | Quarantine; certify; investigate the process gap | R32, DPO | Data-protection exposure record |
| Customer data found on a listed or sold unit | **L4-direct: CTO + DPO + Legal.** Recall the unit; notify the affected customer | As stated | Breach register (`LG-009`) |
| Stolen device identified after acquisition | Preserve; do not sell; cooperate with the lawful process | Legal, R05 | Restricted record |
| Grade disputed by a buyer | Re-inspect against the published definition; refund or replace where the grade was wrong | R32, `SP-028` | Complaint record |
| Battery incident in storage or in a customer's hands | Safety response (`SP-030`); assess the batch, not only the unit | HSE, R32, CCO | Safety incident + recall assessment |
| Refurbishment yield below forecast | Acquisition pricing or assessment accuracy is wrong; investigate both | R25 → CCO | Yield analysis |
| Parts harvested but not recorded into stock | Inventory control failure; reconcile and correct | R17 | Stock exception |
| Listing published without disclosure | Remove the listing immediately; review how it passed | R25, R32 | Nonconformity |
| Offer paid before provenance clearance | Control failure; recover if possible; review the sequence | Retail Manager, CFO | Control exception |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | Assessment and offer are recorded on the **pre-numbered manual trade-in form**, with photographs referenced |
| 2 | `DT-038` is completed and signed in wet ink, including the ownership transfer declaration |
| 3 | **Erasure and its certification do not proceed manually beyond the `SP-012` §9 fallback** — the operator/witness certificate is still required |
| 4 | Grading uses the **printed QA protocol checklist**, signed by the QA technician and, for any override, by R32 |
| 5 | **Listing does not occur during an outage.** A unit is listed only when its QA and grade records exist in the system |
| 6 | **Back-enter every acquisition, erasure, QA and grade record within 48 hours** |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| No refurbishment or resale without a certified destruction record | Preventive (`BRU-TRF-01`) | Per unit | Hard block |
| Provenance and identity checks before payment | Preventive (`BRU-TRF-02`) | Per acquisition | Hard block |
| No listing without a completed QA protocol and assigned grade | Preventive (`BRU-TRF-03`) | Per listing | Hard block |
| Battery health and known defects disclosed | Preventive (`BRU-TRF-04`) | Per listing | Hard block |
| Grade override requires recorded justification by a non-QA approver | Preventive (`BRU-TRF-05`, `SOD-56`) | Per override | Hard block |
| Value/purchase/resell separation | Preventive (`SOD-10`) | At assignment | Hard block |
| Destruction operator ≠ witness | Preventive (`SOD-58`) | Per destruction | Certificate |
| Grade override rate by technician and by grade | Detective | Monthly | Quality report |
| Return rate by grade | Detective | Monthly | Grading accuracy analysis |
| Yield by acquisition cohort | Detective | Monthly | `KPI-077` |
| Units in refurbishment without a certificate | Detective | Weekly | Exception report — target zero |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Value a trade-in | Purchase it and resell it (`SOD-10`) | Hard block at assignment | Above the value band, Finance countersigns |
| Perform refurbishment QA | Approve a grade override (`SOD-56`) | Hard block | Override routes to R32, who may be remote |
| Perform a data destruction | Witness it (`SOD-58`) | Hard block | **None** |
| Assess a device for acquisition | Approve an offer outside the model | Hard block | Retail Manager approves; CCO above threshold |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-077` | Refurbishment yield | no baseline stated in `06-02` | 88% |
| `KPI-078` | Refurbished units sold per year | no baseline stated in `06-02` | 12,000 |
| Units without a destruction certificate | Control violations | untracked | **Zero** |
| Return rate on refurbished units | Returns as a proportion of sales, by grade | untracked | To be set |
| Grade override rate | Overrides as a proportion of graded units | untracked | Low and explained |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-038` Trade-In Offer and Acceptance Record | Executed at step 7 |
| `DT-034` Data Destruction Certificate | Produced at step 11 |
| `DT-036` Refurbishment Grading and Certification Record | Issued at step 18 |
| `DT-032` Warranty Certificate | Attached at sale |
| `LG-019` Refurbished Goods Grading and Disclosure Terms | Grade definitions and disclosure obligations |
| [`SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) | The erasure and certification method |
| [`SP-026_SOP_EWaste_Collection_and_Disposal.md`](SP-026_SOP_EWaste_Collection_and_Disposal.md) | Disposition of failed units |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](SP-010_SOP_Workshop_and_Depot_Repair.md) | Refurbishment work discipline |
| [`SP-028_SOP_Complaint_Escalation_and_Compensation.md`](SP-028_SOP_Complaint_Escalation_and_Compensation.md) | Grade disputes and returns |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Model identification |
| `TR-002` Role-Based Curriculum Map | **No course pack exists for R25 Retail / Refurbishment Officer** — gap raised in `AUDIT-006` |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | CCO with Legal Counsel (pending) |

**Open items**

| # | Item | Owner | Needed by |
|---|---|---|---|
| O-01 | Confirm consumer-law disclosure obligations for refurbished goods in Bangladesh, including any mandatory statement and cooling-off provision. Cited here at class **P3** (secondary) | Legal Counsel | Before `Approved` |
| O-02 | Confirm whether a stolen-device screening service is available and lawful to use; `BRU-TRF-02` says "where available" and that ambiguity must be resolved | Legal Counsel + CCO | Before W5 |
| O-03 | Publish the grade definitions in `LG-019` and align the listing copy in `UI-*` | CCO + Content Design | Before W5 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] The destruction-certificate precondition stated as a hard block on onward movement
- [x] Disclosure treated as a control, with the grade letter alone declared insufficient
- [x] "Do not downgrade to avoid a repair" stated at the QA decision point
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] O-01 consumer-law obligations verified — **outstanding**
- [ ] O-02 stolen-device screening availability resolved — **outstanding**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approvers recorded — **pending CCO and Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
