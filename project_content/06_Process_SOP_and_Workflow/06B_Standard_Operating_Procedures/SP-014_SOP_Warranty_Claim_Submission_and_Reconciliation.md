---
id: SP-014
title: SOP — Warranty Claim Submission and Reconciliation
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Warranty
author: Business Process Lead with Warranty Operations and Finance
reviewers: [CFO, Finance Manager, Operations Director, Quality Manager, Account Management, Legal Counsel, Localisation Lead]
approver: Chief Financial Officer
content_class: C
purpose: >
  Warranty revenue recovery is the largest single benefit line in the programme business case,
  and the baseline leakage is 15–20%. The portal does not determine whether the target is met;
  this process does. It governs eligibility, evidence assembly, submission inside the brand's
  window, query response, decision handling and financial reconciliation of the remittance, so
  that a claim is complete at first submission and paid within 45 days of service.
traces_to: [M09, M01, M20, M19, M50, P08, DT-033, DT-032, MD-011, MD-017, MD-031, SP-004, SP-005, SP-010, SP-020]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M09_Warranty_Protection_Plans_and_Claims.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §5 BRU-WTY-01…BRU-WTY-08; §12.2 AUT-018…AUT-021
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-037…KPI-041 — claims within 72h, leakage 15–20% baseline, first-submission approval, days to reimbursement 60–120 baseline
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P08_Brand_Partner_Portal.md
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.4 — control of externally provided processes, products and services; and clause 7.5.3 documented information required as evidence
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Warranty Claim Submission and Reconciliation

| Item | Value |
|---|---|
| SOP ID | `SP-014` |
| Process owner | Chief Financial Officer; executed under Warranty Claims (R28) |
| Roles performing | `R28` Warranty Claims Officer · `R10`–`R12` Technicians · `R09` Workshop Supervisor · `R26` Finance Manager · `R32` Quality Manager |
| Systems used | `P03` Warranty console (`UI-033`) · `P08` Brand Partner Portal · `M09` · `M20` · `M19` |
| Frequency / volume | Every warranty service order; 4–10 claims officers against 17+ brand partners |
| ISO 9001 clause reference | **8.4** externally provided processes · 7.5.3 documented information as evidence · 8.5.2 traceability |

---

## 1. Purpose and Outcome

**Purpose.** To convert every completed warranty repair into a claim that is complete at first
submission, accepted by the brand without query, and reconciled to cash in the ledger — and to
stop claims expiring unsubmitted, which is where the 15–20% leakage comes from.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| A claim exists within 24 hours of every warranty order closing | `BRU-WTY-02`, `AUT-018` |
| The evidence pack is complete at submission | `BRU-WTY-01`; `KPI-041` target 96% |
| Submission is inside the brand's window | `BRU-WTY-08`; `KPI-037` target 92% within 72 hours |
| The claim is approved at first submission | `KPI-039` target 90% |
| The remittance is matched to the claim in the ledger | `AUT-021`; unmatched flagged |
| Days from service to reimbursement fall from 60–120 to under 45 | `KPI-040` |

---

## 2. Scope

**Applies to:** claims against brand partners and manufacturers for warranty repairs performed by
1000FiX, including parts recovery, labour recovery and goodwill claims, across all 17+ brand
relationships in `MD-017`.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Warranty granted by 1000FiX on its own repair | `DT-032`; disputes go to `SP-028` |
| Protection plans and extended warranty sold to customers | `SP-015` and `M09` product side |
| Customer-facing warranty eligibility explanation at intake | `SP-007` step 5 |
| Return of defective parts to a supplier for credit | `SP-017` |
| Marketplace seller warranty obligations | `SP-024` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Claim | A request to a brand for reimbursement of a warranty repair |
| Evidence pack | `DT-033` — diagnosis, photographs, parts, technician certification, purchase proof |
| Brand window | The period within which the brand accepts a claim, per the agreement in `MD-017` |
| Query | A brand's request for more information, which pauses their clock and starts ours |
| Rejection | A brand's refusal; may be appealed once with new evidence |
| Leakage | Warranty value earned but never recovered — expired, rejected or never claimed |
| Remittance | The brand's payment, covering many claims, requiring matching |
| Goodwill claim | A claim outside strict entitlement that the brand may accept at discretion |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Closed warranty work order | `M01` | Order Completed with QC passed (`BRU-SRM-04`) |
| Device warranty active at the request date | `M09`, `M17` | `BRU-SRM-02` — checked at intake, not at claim time |
| Technician certified for that brand | `M22`, `MD-011` | `BRU-SRM-09`; an uncertified technician's work is rejected by the brand and is unrecoverable |
| Before-photographs | `SP-008`/`SP-010` | Mandatory on every warranty job (`BRU-SRM-17`); a job cannot close without them |
| Replaced parts list with serials | `M15` | `BRU-INV-08` serial capture at issue and consumption |
| Brand agreement terms | `MD-017` | Window, format, rates and evidence requirements differ per brand |
| Purchase proof | Customer or brand registry | Frequently the missing element; chased at intake, not at claim |

---

## 5. Procedure

### 5.1 Claim creation and eligibility

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | System | Create the claim automatically within 24 hours of the warranty order closing (`BRU-WTY-02`, `AUT-018`) | `M09` | Claim record | — |
| 2 | System | Assemble the evidence pack from the order and validate completeness | `M09` | Completeness score |
| 3 | R28 | Check eligibility: coverage active at the request date, fault within scope, not a duplicate within 90 days (`BRU-WTY-03`) | `P03` warranty console | Eligibility result | 5 min |
| 4 | R28 | Confirm the technician's certification was current **at the date of work**, not today | `MD-011` | Certification check | 2 min |
| 5 | R28 | Value the claim in the agreed currency at the rate prevailing on the **service completion date** (`BRU-WTY-05`) | `P03` · `MD-039` | Claim value | 3 min |

### 5.2 Evidence assembly

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 6 | R28 | Verify the pack against `DT-033` and that brand's specific requirements | `P03` · `MD-017` | Pack verified |
| 7 | R28 | Where an element is missing, request it from the workshop or the customer **immediately**, not at submission | `NT-*` | Request logged |
| 8 | R28 | Where purchase proof is unavailable, use the brand's registry lookup or the device registration record before treating it as unobtainable | `M17` | Proof or documented absence |
| 9 | R28 | Confirm replaced parts are recorded with serials and that brand-supplied warranty parts were used where required (`BRU-WTY-04`) | `M15` | Parts verified |

### 5.3 Submission

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 10 | System | Submit in the brand's required format once validated (`AUT-019`) | `P08` / brand channel | Submission record with timestamp |
| 11 | R28 | Where the automated channel fails, submit manually through the brand's route and record it | `P03` | Manual submission record |
| 12 | R28 | Confirm the brand's acknowledgement. **An unacknowledged submission is not a submission** | `P03` | Acknowledgement |

### 5.4 Query and decision

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 13 | R28 | Respond to queries within the brand's stated period; escalate internally if the answer sits with the workshop | `P08` | Query response |
| 14 | System | Update on decision: approval queues for billing; rejection opens a dispute task (`AUT-020`) | `M09` | Decision recorded |
| 15 | R28 | On rejection, analyse the reason, correct the deficiency, and appeal once where the evidence supports it | `P03` | Appeal record |
| 16 | R28 | Where the rejection is valid, record the leakage with its cause — this is the input that stops it recurring | `M09` → `SP-029` | Leakage record |

### 5.5 Billing and reconciliation

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 17 | R26 | Raise the invoice to the brand for approved claims | `M20` | Invoice |
| 18 | System | Match the brand's remittance to claims; flag unmatched (`AUT-021`) | `M50` · `M19` | Matching record |
| 19 | R26 | Investigate unmatched and short-paid items; short payment is a dispute, not a rounding adjustment | `P03` | Dispute record |
| 20 | R26 | Post to the ledger; release the accrual | `M19` | Ledger posting |
| 21 | R28 | Report leakage, ageing and first-submission approval rate monthly | `RP-*` | Warranty performance report |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 3 | Coverage was not active at the request date | Not a warranty claim. Convert to a paid repair and inform the customer **before** work, not after | R28 → R08 |
| 3 | Duplicate claim for the same serial and fault within 90 days | Blocked (`BRU-WTY-03`). Investigate whether this is rework (`SP-013`) | R32 |
| 4 | Technician certification had lapsed at the date of work | The claim will be rejected. Record it as leakage with cause "certification lapse" and escalate — this is preventable and `KPI-063` targets zero | R32 + R30 HR Manager |
| 6 | Evidence element missing and unobtainable | Submit with a documented explanation only where the brand permits; otherwise record as leakage before the window closes | R28 |
| 7 | Workshop does not supply the missing evidence within the configured period | Escalate to R09, then R06. The window does not pause for internal delay | R28 → R09 → R06 |
| 10 | Brand's window is at 75% consumed | Escalate (`SP-005` CO-E5) and submit with what exists rather than let it expire | R28 + R26 |
| 12 | No acknowledgement from the brand | Chase; do not assume receipt. Record every chase | R28 |
| 14 | Second rejection on the same claim | Escalate to R26 Finance Manager; assess whether to pursue commercially | R26 → CCO |
| 14 | Rejection reason indicates a systemic evidence gap | Raise a nonconformity — one claim is a loss, a pattern is a process defect | R32 → `SP-029` |
| 18 | Remittance short-paid without explanation | Treat as a dispute with the brand, tracked to resolution | R26 → R22 Account Manager for the brand relationship |
| — | A brand changes its evidence requirements | Update `MD-017` and the `DT-033` pack **before** the next submission, not after the first rejection | R28 + R32 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Submit a claim | Any | R28 Warranty Claims Officer | R26 |
| Write off a rejected claim as leakage | ≤ BDT 50,000 | R26 Finance Manager (`SP-004` A-30) | CFO |
| Write off a rejected claim as leakage | > BDT 50,000 | CFO (`SP-004` A-31) | CEO above BDT 500,000 |
| Raise a claim and approve its write-off | **Incompatible** (`SOD-11`) | Different people | — |
| Accept a short payment as final | Any | R26 Finance Manager | CFO |
| Pursue a brand dispute beyond the portal process | Any | R28 with CCO (`SP-005` L5 path) | CFO |
| Submit a goodwill claim outside strict entitlement | Any | R28; R26 above the value threshold | CCO |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Claim window expiring | Escalate before expiry, not after (`BRU-WTY-08`, `SP-005` CO-E5) | R28 + R26 | Leakage risk register |
| Brand portal unavailable | Manual submission per §9; record the outage and the manual route | R28, R33 | Submission record |
| Brand changes format without notice | Escalate to the brand relationship owner; hold submissions rather than submit in a rejected format | R22, R28 | `MD-017` update |
| Systematic rejection by one brand | Treat as a commercial issue, not a claims issue | CCO, CFO | Brand performance review |
| Warranty part shortage delaying the repair and therefore the claim | The claim window runs from service, not from part availability. Escalate the shortage | R17 via `SP-016` | Parts exception |
| Claim submitted for work done by an uncertified technician | Do not submit knowingly. Record as leakage with cause and raise a nonconformity | R32, R30 | `SP-029` CAPA |
| Fraudulent claim suspected — internal | **L4-direct: CFO + Internal Audit**, restricted | As stated | Restricted record |
| Remittance received with no claim reference | Hold in suspense; do not post to revenue until matched | R26 | Suspense account |
| Claim value materially different from the repair value | Investigate before submission; a systematic difference is a pricing or a coding defect | R28 + R26 | Margin exception |

---

## 9. Manual Fallback

Claims depend on brand portals that 1000FiX does not control. `IP-09` requires a defined manual
fallback for every P0 integration. Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Assemble the evidence pack as a PDF from `P03`; where `P03` is down, from the printed `DT-003` job card and the workshop photograph store |
| 2 | Submit through the brand's email or agent route, with a **1000FiX claim reference in the subject line** |
| 3 | Record the submission in the **pre-numbered manual claims log**: claim reference, brand, order, value, date submitted, route |
| 4 | Obtain and file the brand's acknowledgement; chase at the configured interval |
| 5 | **Back-enter every manual submission within 24 hours** of system restoration, preserving submission dates — the date is the control, since the window turns on it |
| 6 | R26 reconciles the manual log against the system monthly and signs it |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Claim auto-created within 24h of warranty closure | Preventive (`BRU-WTY-02`) | Per order | Claim creation log |
| Claim cannot be submitted without the mandatory evidence set | Preventive (`BRU-WTY-01`) | Per claim | Hard block |
| Duplicate claims within 90 days blocked | Preventive (`BRU-WTY-03`) | Per claim | Hard block |
| Brand warranty parts cannot be consumed on non-warranty jobs | Preventive (`BRU-WTY-04`) | Per issue | Hard block |
| Claim valued at the completion-date rate | Preventive (`BRU-WTY-05`) | Per claim | Computed |
| Uncertified technician cannot take brand warranty work | Preventive (`BRU-SRM-09`) | Per assignment | Hard block |
| Claim raise and write-off approval separated | Preventive (`SOD-11`) | Per write-off | Hard block |
| Window-expiry escalation before the deadline | Detective → preventive (`BRU-WTY-08`) | Continuous | Escalation log |
| Ageing of unsubmitted and undecided claims | Detective | Weekly | Ageing report |
| Rejection-reason analysis | Detective | Monthly | `SP-029` input |
| Remittance matching and suspense clearance | Detective | Monthly, at close (`SP-020`) | Reconciliation |
| Leakage register with cause | Detective | Monthly | `KPI-038` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Raise a warranty claim | Approve its write-off (`SOD-11`) | Hard block | — |
| Perform the repair being claimed | Approve the claim | Hard block | Technician evidence is verified by R28, who did not perform the work |
| Create a credit note arising from a claim adjustment | Approve it (`SOD-04`) | Hard block | — |
| Own the brand relationship | Approve the write-off of that brand's rejected claims | Threshold block | Write-off approval sits with Finance, not with Account Management |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-037` | Claims submitted within 72 hours | ~50% at 30–90 days | 92%; stretch 95% |
| `KPI-038` | Warranty revenue leakage | 15–20% | 5%; stretch < 2% |
| `KPI-039` | First-submission approval rate | unmeasured | 90%; stretch 92% |
| `KPI-040` | Days from service to reimbursement | 60–120 | 55; stretch < 45 |
| `KPI-041` | Claims with complete evidence at submission | unmeasured | 96%; stretch 98% |
| `KPI-063` | Claims rejected for uncertified technician | unknown | **Zero** |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-033` Warranty Claim Evidence Pack | The pack assembled at step 6 |
| `DT-032` Warranty Certificate and Extension Document | 1000FiX's own warranty, distinct from the brand's |
| `UI-033` Workspace — Warranty Console Copy | The screens used |
| `UI-018` `P08` Brand Partner Portal UI Copy Pack | The submission surface |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](SP-010_SOP_Workshop_and_Depot_Repair.md) | Produces the evidence this SOP depends on |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](SP-020_SOP_Month_End_and_Year_End_Close.md) | Accrual and reconciliation of unremitted claims |
| [`SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Consumes rejection-pattern nonconformities |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) | Windows, formats, rates per brand |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Certification validity at the date of work |
| `TR-014` Course Pack — Finance Officer and Manager | **No dedicated pack exists for R28 Warranty Claims Officer** — gap raised in `AUDIT-006` |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Certification validity checked at the date of work, not at claim time
- [x] Window-expiry escalation fires before expiry, not after
- [x] Leakage is recorded with a cause, so it feeds correction
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback preserves the submission date as the controlling fact
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Per-brand evidence requirements confirmed in `MD-017` for all 17+ brands — **outstanding**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending CFO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
