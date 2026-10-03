---
id: SP-007
title: SOP — Walk-In Intake and Front Desk
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations
author: Business Process Lead with Branch Operations
reviewers: [Operations Director, Branch Managers Forum, Quality Manager, Legal Counsel, Localisation Lead, Content Design]
approver: Operations Director
content_class: C
purpose: >
  The single most-repeated process in the company: 150–250 Service Centre Agents receiving
  customer devices across 51+ branches against a 3-minute target. It is the point where custody
  of a customer's property transfers to 1000FiX, where the condition record that settles every
  later dispute is created, and where the customer's expectation of cost and time is set.
  Performed inconsistently, it produces the company's most common customer conflict.
traces_to: [M04, M01, M17, P03, DT-002, MD-024, MD-003, SP-004, SP-005, SP-019, BRU-SRM-01]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: SP-007_SOP_Walk_In_Intake_and_Front_Desk_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M04_Branch_and_Front_Desk_Operations.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-01, BRU-SRM-16, BRU-SRM-20; §12.1 AUT-001
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-010 walk-in intake time — baseline ~10 min, target < 4 min, stretch < 3 min
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.5.3 — property belonging to customers or external providers shall be identified, verified, protected and safeguarded; loss or damage reported
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Walk-In Intake and Front Desk

| Item | Value |
|---|---|
| SOP ID | `SP-007` |
| Process owner | Operations Director (R05); executed under Branch Manager (R06) |
| Roles performing | `R08` Service Centre Agent · `R06` Branch Manager · `R29` Cashier |
| Systems used | `P03` Admin Operations Portal — Service Intake workspace (`UI-023`) · `M04` · `M01` · `M17` |
| Frequency / volume | Continuous during opening hours. The highest-volume process in the company across 51+ branches |
| ISO 9001 clause reference | **8.5.3** property belonging to customers · 8.2.1 customer communication · 8.5.2 identification and traceability · 7.5.3 control of documented information |

---

## 1. Purpose and Outcome

**Purpose.** To receive a customer's device into 1000FiX custody with an identification and
condition record complete enough to (a) diagnose it, (b) return it correctly, and (c) settle any
later dispute about what was handed over and in what state.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| A service order exists with an identified device | `BRU-SRM-01` satisfied; order visible in `P03` |
| The customer holds a signed or digitally acknowledged `DT-002` intake receipt | Receipt number recorded against the order |
| The device carries a scannable tag matching the order | `DT-044` label affixed |
| The customer can state, unprompted, what happens next and roughly when | Expectation set — the main driver of subsequent enquiry volume |
| Elapsed time from queue call to customer leaving the counter is under 3 minutes | `KPI-010` |

---

## 2. Scope

**Applies to:** all walk-in receipts of a customer-owned device at any branch, service centre or
kiosk in `MD-003`, for any service type — paid repair, warranty, AMC, contract, trade-in
assessment, data recovery drop-off — in both Bengali and English.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Device collected from the customer by rider or courier | `SP-009` Pick-and-Drop and Reverse Logistics |
| Technician attending the customer's premises | `SP-008` On-Site Field Service Visit |
| Booking made by phone, app or web with no device present | `SP-034` (contact centre) / `M38`; this SOP resumes when the device arrives |
| Return of a completed device to the customer | §5 step 14 of this SOP hands over to `SP-007` release steps; the full release path is in `SP-010` §5 and `DT-009` |
| Corporate bulk drop-off of multiple assets | `SP-015`; use the bulk-intake variant in §5.3 |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Intake | The transfer of physical custody of a customer device to 1000FiX |
| Condition record | The structured description and photographic evidence of the device state at intake |
| Declared fault | The problem **as the customer describes it**, in their words — not the agent's diagnosis |
| Symptom code | The structured classification from `MD-024`, chosen by the agent |
| Token | The queue position issued on arrival |
| Accessories | Anything handed over with the device — charger, case, SIM, memory card, stylus, box |
| Data-access note | A password, PIN or unlock pattern supplied by the customer to permit testing |
| Service order | The canonical record (`CG-004`); never called a job, ticket or case in customer-facing text |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| The customer and the device are present | — | The device is physically at the counter |
| Branch is open and the shift is started | `M04` | The prior shift's cash was closed (`BRU-FIN-10`) — an unclosed shift blocks the counter |
| Agent is logged in to `P03` with their own credentials | `M29` | Never a shared login; every intake is attributable |
| Intake workstation has a working camera and label printer | `M47` | Photographs and `DT-044` labels are mandatory outputs |
| Device catalogue is current | `MD-021` | Make and model must be selectable, not typed free-text |
| Symptom taxonomy is current | `MD-024` | The declared fault must map to a code |
| Price list is current | `MD-029` | Any indicative figure quoted must come from the rate card |

---

## 5. Procedure

### 5.1 Standard intake

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R08 | Call the token. Greet in the customer's language; default to Bengali unless the customer opens in English | `P03` queue panel | Token called, timestamped | 5 s |
| 2 | R08 | Ask what has happened, in the customer's words. **Do not interrupt to categorise** | — | — | 20 s |
| 3 | R08 | Identify the customer: mobile number first; if not found, name and NID. Create or confirm the party record | `P03` · `M33` | Party record confirmed | 20 s |
| 4 | R08 | Identify the device: scan the serial or IMEI if present; otherwise select make and model from `MD-021` and enter the identifier manually | `P03` · `M17` | Device registered or matched (`BRU-SRM-01`) | 25 s |
| 5 | R08 | Check entitlement — warranty, AMC, contract, Privilege tier. State the result aloud to the customer | `P03` · `M09` `M08` `M10` | Entitlement resolved; service type set | 15 s |
| 6 | R08 | Record the declared fault verbatim, then select the symptom code | `P03` · `MD-024` | Declared fault + symptom code | 20 s |
| 7 | R08 | **Inspect the device with the customer watching.** State each mark aloud as you record it: screen, body, ports, corrosion, prior repair, swelling, moisture indicator | `P03` condition panel | Condition record | 30 s |
| 8 | R08 | Photograph the device — front, back, and each recorded defect. Minimum four images | `P03` capture | Photographic evidence attached | 25 s |
| 9 | R08 | Record accessories handed over, item by item. **Advise the customer to retain SIM and memory card** wherever the repair does not require them | `P03` accessories panel | Accessory list | 15 s |
| 10 | R08 | Give the **data-backup warning** and record the customer's acknowledgement. Capture a data-access note **only if the customer offers it and consents** (`BRU-SRM-20`) | `P03` consent panel | Acknowledgement recorded; consent flag | 20 s |
| 11 | R08 | State the expectation: what happens next, when the estimate or update will come, and how they will be contacted. Give an **indicative** price band from `MD-029` only — never a firm figure before diagnosis | — | Expectation set verbally | 20 s |
| 12 | R08 | Take any advance payment due and issue the receipt | `P03` · `M20` · `SP-019` | `DT-016` money receipt | 20 s |
| 13 | R08 | Generate and print `DT-002`; obtain the customer's signature or OTP acknowledgement; hand them their copy | `P03` print · `DT-002` | Signed intake receipt | 25 s |
| 14 | R08 | Print and affix the `DT-044` device tag; place the device in the secured intake bin or forward per §5.2 | Label printer · `M15` | Device tagged and located | 15 s |
| 15 | R08 | Close the intake. The order enters triage automatically (`AUT-001`) | `P03` | Service order in Received state | 5 s |

**Target elapsed: under 3 minutes** (`KPI-010` stretch). Steps 7 and 8 are the two most often
rushed and are the two that settle disputes. Do not compress them; compress steps 3–6 with
practice.

### 5.2 Routing after intake

| Situation | Action | Governed by |
|---|---|---|
| Repairable at this branch | Assign to the branch workshop queue | `SP-010` |
| Requires a workshop elsewhere | Raise a consignment; device moves under custody scan (`BRU-SCM-05`) | `SP-009` |
| Requires an L3 specialist | Route to a workshop with the equipment and a certified specialist (`BRU-SRM-14`) | `SP-010` |
| Data recovery | Route to the restricted data-services path — **do not open the device** | `SP-012` |
| Trade-in assessment | Route to assessment; the device remains the customer's until an offer is accepted | `SP-025` |
| Brand warranty | Confirm technician certification is available before promising a date (`BRU-SRM-09`) | `SP-014` |

### 5.3 Bulk intake variant (corporate, 5+ devices)

| Step | Change from §5.1 |
|---|---|
| 1 | Handle away from the walk-in counter; book an appointment. Bulk intake at the counter destroys the queue |
| 3 | Identify the corporate account and the authorised representative, not an individual consumer |
| 7–8 | Condition record per device is still mandatory. **The per-device requirement is not waived by volume** — it is the reason bulk disputes are unwinnable without it |
| 13 | One consolidated `DT-002` listing every device and serial, signed once |
| — | Target time does not apply; `KPI-010` measures walk-in only |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 3 | Customer will not provide identification | Proceed with mobile number only; flag the order. Device release will require the same number plus the receipt | R08 |
| 4 | Serial or IMEI unreadable or absent | Record the reason, photograph the location where it should be, and register a provisional asset. **Flag for verification before release** | R08; R06 if the device is high value |
| 5 | Entitlement disputed by the customer | Do not argue at the counter. Accept the device as paid-repair, flag entitlement for review, and tell the customer it will be re-checked | R08, escalate to R06 |
| 7 | Device is visibly damaged beyond the declared fault | Record it, photograph it, and **state it to the customer before they sign**. Note their response | R08 |
| 7 | Battery is swollen, the device is water-damaged, or there is a burning smell | **Do not place it in the standard bin.** Isolate per `SP-030`; safety takes precedence over the time target | R08 → R06 immediately |
| 10 | Customer refuses the data-backup warning acknowledgement | Record the refusal on `DT-002`. Do not proceed without the record | R08 |
| 10 | Customer volunteers a password | Record only with explicit consent; it is purged at handover (`BRU-SRM-20`) | R08 |
| 11 | Customer demands a firm price now | Give the rate-card band and explain that a firm estimate follows diagnosis. **Do not commit a figure** | R08; R06 may commit within `SP-004` A-08 |
| 12 | Cash advance above BDT 50,000 | NID must be recorded (`BRU-FIN-02`) — hard block, no approval path | R08 |
| — | The device is suspected stolen (customer cannot identify it, or provenance is implausible) | Complete intake, do not release, and escalate immediately. Do not accuse | R06 → R05, per `SP-005` |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Waive or reduce a diagnostic fee | ≤ BDT 1,000 | R08 Service Centre Agent | R06 |
| Waive or reduce a diagnostic fee | > BDT 1,000 | R06 Branch Manager | R05 after the `SP-005` timer |
| Accept a device with no identifiable serial | Any | R08; R06 above the high-value threshold | R06 |
| Accept a bulk corporate intake outside appointment | Any | R06 | R05 |
| Priority upgrade at the counter | Any | R06 — never R08 | R07 Dispatch Manager |

> Must reconcile exactly with `SP-004`. No figure in this table may differ from `SP-004` §4.2.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| `P03` unavailable | Switch to the manual fallback in §9 | R06, then R33 IT Administrator via `SP-031` | Paper intake register; back-entered within 4 hours |
| Label printer failed | Hand-write the tag using the order number and affix; reprint when available | R06 | Order note |
| Camera unavailable | **Do not proceed without photographs.** Use a branch-issued device; if none, the Branch Manager must authorise intake and personally witness the condition record | R06 | Order note with the authorisation |
| Customer refuses to sign `DT-002` | Do not take custody. A device accepted without a signed condition record cannot be defended in a dispute | R06 | Declined-intake log |
| Device unsafe (swelling, burning, leaking) | Isolate; follow `SP-030`; inform the customer that special handling applies | R06, HSE Lead | Safety incident record |
| Queue exceeds the configured length | R06 opens an additional counter or activates the appointment-only mode | R06 → R05 | Branch console |
| Suspected stolen device | Complete intake; do not release; escalate. Do not detain the customer | R06 → R05 → Legal Counsel | Restricted flag on the order |
| Customer becomes abusive | Follow the branch de-escalation protocol in `SP-032`; do not continue intake alone | R06 | Incident record |
| Duplicate order for the same device and fault within 30 days | System flags rework automatically (`BRU-SRM-06`) — tell the customer it is linked to the earlier repair | R32 Quality Manager | Rework link on the order |

---

## 9. Manual Fallback

`P03` is not a P0 integration, but intake is a P0 process — a branch that cannot take in devices
is closed. Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Switch to the **pre-numbered paper intake book**. Every branch holds one; the Branch Manager verifies its presence at each shift start (`SP-032`) |
| 2 | Record: date, time, agent name, customer name and mobile, device make/model/serial, declared fault, condition notes, accessories, and the customer's signature |
| 3 | Photograph the device on a branch-issued camera or phone; note the image reference in the book |
| 4 | Issue the **carbon copy** to the customer as the interim `DT-002`. Tell them a system receipt will follow |
| 5 | Hand-write the device tag with the paper book's sequence number |
| 6 | **Back-enter every paper intake into `P03` within 4 hours of service restoration**, preserving the original timestamps |
| 7 | R06 reconciles the paper book against `P03` at the end of the outage and signs the reconciliation |

> The paper book is pre-numbered so that a missing page is visible. An unnumbered pad is not a
> fallback control.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Every intake has ≥ 4 photographs | Preventive, system | Per transaction | Image count on the order |
| Every intake has a signed or OTP-acknowledged `DT-002` | Preventive, system | Per transaction | Receipt record |
| Device cannot be created without an identifier or a recorded reason | Preventive (`BRU-SRM-01`) | Per transaction | Hard block |
| Every intake attributable to a named agent | Preventive | Per transaction | No shared logins (`M29`) |
| Data-access note purged at handover | Preventive (`BRU-SRM-20`) | Per transaction | Purge log |
| Cash receipt above BDT 50,000 requires NID | Preventive (`BRU-FIN-02`) | Per transaction | Hard block |
| Intake time monitored per agent and per branch | Detective | Daily | `KPI-010` report |
| Condition-record completeness sampled | Detective | Weekly, 5% sample | Quality review record (`P11`) |
| Paper-book reconciliation after any outage | Detective | Per outage | Signed reconciliation |
| Dispute rate traced back to intake completeness | Detective | Monthly | `SP-028` complaint analysis |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Handle counter cash | Reconcile the counter cash book (`SOD-12`) | Hard block at assignment | **At C4/C5 single-person sites this is structurally violated.** Apply the blind-declaration and remote-variance controls in `SP-006` §4.6 |
| Take intake | Perform the independent QC on the same device (`SOD-07`) | Hard block above threshold | Remote photographic QC review by R09 |
| Create the party record | Approve that customer's credit limit (`SOD-08`) | Warning + approval | Credit limit approval sits with Finance, never at the counter |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-010` | Walk-in intake time, token call to counter release | ~10 min | < 4 min; stretch < 3 min |
| `KPI-009` | Devices uncollected > 30 days | unmeasured | < 1%; stretch < 0.5% |
| `KPI-020` | CSAT — intake is the first contact and weights it heavily | 3.8/5 | 4.4/5; stretch 4.7/5 |
| Condition-record completeness | Photographs ≥ 4 and all condition fields recorded | unmeasured | 100% |
| Intake-attributable disputes | Disputes where the condition record was inadequate | unmeasured | Zero |

> Three of these five have no measured baseline. `SP-002` T2 sampling at 12 branches supplies
> them before the W1 gate.

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-002` Service Intake Receipt and Device Handover Form | The output of step 13 — the custody document |
| `DT-009` Device Release and Collection Receipt | Closes the custody chain this SOP opens |
| `DT-044` Label, Barcode and QR Format Specification | The tag applied at step 14 |
| `UI-023` Workspace — Service Intake Copy | The screen this SOP is performed on |
| [`../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) | §7 limits |
| [`../06A_Process_Architecture/SP-005_Escalation_Matrix.md`](../06A_Process_Architecture/SP-005_Escalation_Matrix.md) | §8 escalation destinations |
| [`../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | §11 controls and compensating controls |
| [`SP-019_SOP_Cash_Collection_and_Banking.md`](SP-019_SOP_Cash_Collection_and_Banking.md) | Step 12 payment handling |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Unsafe device handling |
| [`SP-032_Operational_Checklist_Library.md`](SP-032_Operational_Checklist_Library.md) | Shift-start checks that precondition this SOP |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) | Symptom coding at step 6 |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Device selection at step 4 |
| `TR-007` Course Pack — Service Centre Agent | Trains this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Operations Director (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Every step names who, the system, the evidence produced and a time
- [x] Decision points include the failure and safety branches, not only the happy path (`PD-12`)
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback specified with a back-entry deadline
- [x] Segregation of duties cites `SP-006` and names the small-site compensating control
- [x] Every factual claim carries a source and a verification date
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Walked end-to-end in UAT by someone who did not write it (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
