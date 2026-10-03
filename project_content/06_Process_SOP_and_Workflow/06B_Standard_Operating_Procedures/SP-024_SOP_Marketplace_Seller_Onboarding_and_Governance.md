---
id: SP-024
title: SOP — Marketplace Seller Onboarding and Governance
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Marketplace Operations
author: Business Process Lead with Marketplace Operations
reviewers: [CCO, CFO, Legal Counsel, Quality Manager, Data Protection Officer, Operations Director, Localisation Lead]
approver: Chief Commercial Officer with Legal Counsel
content_class: C
purpose: >
  A seller cannot transact until documents are verified, the agreement is signed and an
  administrator has approved. Marketplace jobs are held to the same evidence, QC and warranty
  standards as owned jobs, because the customer experiences them as 1000FiX. This SOP governs
  verification, agreement, approval, monitoring, warning, suspension and removal for 500–2,000
  sellers, with the collusion controls that separate seller approval from payout approval.
traces_to: [M12, P07, M53, M23, M20, DT-039, LG-018, MD-018, SP-004, SP-005, SP-006, SP-013, SP-028, SP-029]
priority: P2
wave: W7
bilingual: yes
bn_counterpart: SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md — SOD-06, EA-04, BRU-MKP-03, BRU-MKP-18 appeal decided by a different operator
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §8 BRU-ECM-01…BRU-ECM-10; §12.2 AUT-026, AUT-027
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P07_Marketplace_Seller_Portal_and_Application.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-079 approved active sellers 500, KPI-081 marketplace dispute rate < 1.5%, KPI-082 seller payout accuracy 100%
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.4 — control of externally provided processes; the extent of control applied where an external provider performs a process on the organisation's behalf
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Marketplace Seller Onboarding and Governance

| Item | Value |
|---|---|
| SOP ID | `SP-024` |
| Process owner | Chief Commercial Officer; executed under Marketplace Operations (R24) |
| Roles performing | `R24` Marketplace Operations Officer · `R26` Finance Manager · `R32` Quality Manager · Legal Counsel · `R38` seller (external party) |
| Systems used | `P03` Marketplace console (`UI-034`) · `P07` Seller Portal and App · `M12` · `M53` |
| Frequency / volume | 500–2,000 sellers at scale; continuous onboarding and monitoring |
| ISO 9001 clause reference | **8.4** externally provided processes · 8.4.2 extent of control · 8.7 nonconforming outputs |

---

## 1. Purpose and Outcome

**Purpose.** To admit only sellers who are verified, qualified and contracted; to hold their work
to the same standard as 1000FiX's own; and to reduce, suspend or remove them promptly when they
fall below it — while paying them accurately enough that they trust the platform.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| No seller transacted before verification, signature and admin approval | `BRU-ECM-01` |
| No seller lists in a category they are not qualified for | `BRU-ECM-07` |
| Marketplace jobs meet the same evidence, QC and warranty standards as owned jobs | `BRU-ECM-03` |
| Seller approval and payout approval were never the same person | `SOD-06`, `BRU-MKP-03` |
| Disputes are decided by 1000FiX, with the decision and its evidence recorded | `BRU-ECM-09` |
| Seller access to customer data is limited to awarded jobs and expires | `BRU-ECM-05`, `EA-04` |
| Payout accuracy at 100% | `KPI-082` |

---

## 2. Scope

**Applies to:** seller application, document verification, category qualification, agreement,
approval, activation, performance monitoring, warning, visibility reduction, suspension, removal,
appeal, and payout governance.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| The service delivery itself — the seller performs it | `SP-008` standards apply to them by contract (`BRU-ECM-03`) |
| Vendor (goods supplier) onboarding | `SP-017` |
| Employee recruitment | `SP-023` |
| Referral and channel partners | `M40`; `SP-004` A-82 for MDF |
| Customer complaint handling about a seller job | `SP-028`; the seller consequence path is here |
| Payout calculation mechanics | `M53`, `DT-039` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Seller | An independent service provider transacting through `P07` |
| Category qualification | Verified competence permitting a seller to list in a service category (`BRU-ECM-07`) |
| Performance score | The composite measure driving visibility, warning and suspension (`BRU-ECM-04`) |
| Visibility reduction | Automatic demotion in listing when the score falls below the configured threshold |
| Suspension | Temporary removal of the ability to transact |
| Removal | Permanent termination of the seller relationship |
| Hold period | The configured delay before a completed job's commission is paid (`BRU-BIL-03`) |
| Dispute | A disagreement about a job's outcome, decided by 1000FiX (`BRU-ECM-09`) |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Seller category standards | `MD-018` | What qualification each category requires |
| Seller agreement template | `LG-018` | Approved by Legal; not negotiated per seller |
| Verification requirements | `MD-018`, Legal | Identity, trade licence, tax registration, bank account, insurance where required |
| Category qualification assessment | `M22` | `BRU-LMS-02` — a marketplace engineer cannot be activated in a category without passing its qualification |
| Payout configuration | `M53`, `MD-038` | Commission, fees, hold period and cycle |
| Data-access rules | `05-04` EA-04 | Customer data limited to awarded jobs, expiring after completion |

---

## 5. Procedure

### 5.1 Application and verification

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | Seller | Apply through `P07` with business and personal details | `P07` | Application |
| 2 | R24 | Verify identity, trade licence, tax registration and bank account against the `MD-018` requirement set | `P03` | Verification record |
| 3 | R24 | Verify bank account ownership independently. **A bank account that does not belong to the verified entity is refused** | `P03` | Bank verification |
| 4 | R24 | Assess category qualification; a seller may list only where qualified (`BRU-ECM-07`, `BRU-LMS-02`) | `M22` | Qualification record |
| 5 | R24 | Where the category involves brand warranty work, confirm the required certification (`MD-011`) | `MD-011` | Certification check |

### 5.2 Agreement and approval

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 6 | Seller | Digitally sign the seller agreement (`LG-018`) | `M24` | Signed agreement |
| 7 | R24 | **Administrator approval** — the third precondition (`BRU-ECM-01`) | `P03` | Approval record |
| 8 | System | Activate; the seller may now transact in their qualified categories only | `M12` | Activation |
| 9 | R24 | Deliver seller onboarding: standards, evidence requirements, QC expectations, dispute process, payout mechanics | `P07`, `EO-*` | Onboarding record |

### 5.3 In-life monitoring

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 10 | System | Score performance continuously: completion, on-time, evidence completeness, QC pass, rework, rating, dispute rate | `M12` | Performance score |
| 11 | System | Below the visibility threshold, reduce visibility automatically; below the suspension threshold, suspend (`BRU-ECM-04`) | `M12` | Automatic action |
| 12 | R24 | Review scored actions weekly; a score-driven action still needs a human check for data defects | `P03` | Review record |
| 13 | R32 | Sample marketplace job evidence to the same standard as owned jobs (`BRU-ECM-03`) | `M23` | Quality sample |
| 14 | R24 | Monitor registration and certification expiry; expiry suspends automatically (`BRU-ECM-08`) | `M12` | Expiry monitoring |
| 15 | R24 | Confirm reviews come only from customers with a completed transaction (`BRU-ECM-02`) | `M12` | Review integrity |

### 5.4 Warning, suspension and removal

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 16 | R24 | Issue a warning with the specific evidence and the required improvement | `P07` · `NT-*` | Warning record |
| 17 | R24 | Suspend where the threshold, a safety issue or a verification lapse requires it | `P03` | Suspension |
| 18 | R24 | Remove where the agreement permits; above the threshold, CCO approves (`SP-004` A-80) | `P03` | Removal |
| 19 | **A different operator** | Decide any appeal. **The operator who imposed the consequence may not decide the appeal** (`BRU-MKP-18`, `SOD-60`) | `P03` | Appeal decision |
| 20 | R24 | On suspension or removal, revoke customer-data access immediately (`EA-04`) | `M29` | Access revocation |
| 21 | R26 | Hold payouts while a dispute is open; release on resolution (`BRU-BIL-03`) | `M53` | Payout hold |

### 5.5 Disputes and payouts

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 22 | R24 | Gather evidence from both parties; **1000FiX decides, not the parties** (`BRU-ECM-09`) | `P03` | Dispute record |
| 23 | R24 | Record the decision and its evidence; communicate to both parties | `P07` · `NT-*` | Decision |
| 24 | System | Reverse commission automatically where a transaction is refunded or a dispute is decided against the seller (`BRU-BIL-04`) | `M53` | Reversal |
| 25 | System | After the hold period, accrue commission and add to the payout run (`AUT-026`) | `M53` | Accrual |
| 26 | R26 | Approve held or disputed payouts. **Never the person who approved the seller** (`SOD-06`) | `P03` | Payout approval |
| 27 | System | Produce the payout statement showing gross, commission, fees, adjustments, holds and net (`DT-039`) | `DT-039` | Statement issued |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 2 | A verification document is missing or inconsistent | Do not approve. **Verification is a precondition, not a formality** (`BRU-ECM-01`) | R24 |
| 3 | Bank account is in a different name from the verified entity | Refuse. This is the standard payout-fraud pattern | R24 → R26 |
| 4 | Seller wishes to list outside their qualification | **Blocked** (`BRU-ECM-07`). Offer the qualification path | R24 |
| 7 | Seller is approved by the same person who will approve their payouts | **Blocked** (`SOD-06`) | — |
| 11 | Automatic suspension appears to be caused by a data defect | Investigate before it stands; a wrongly suspended seller loses income and trust | R24 |
| 13 | Marketplace job evidence falls short of the owned-job standard | The same nonconformity path applies (`SP-029`). The customer cannot tell the difference and neither should the standard | R32 |
| 16 | Warning concerns a safety issue | Suspend first, warn second. Safety is not a performance conversation | R24 → R05 |
| 19 | The only available reviewer imposed the consequence | The appeal waits. `SOD-60` has no compensating control at this scale | R24's manager |
| 21 | Dispute is open and a payout is due | **Blocked entirely while the dispute is open** (`BRU-BIL-03`) | — |
| 22 | Evidence is inconclusive | Decide on the balance of the recorded evidence and say so plainly. An undecided dispute damages both parties | R24 |
| 26 | Payout accuracy is questioned | Investigate before releasing; `KPI-082` targets 100% and seller trust rests almost entirely on payout transparency | R26 |
| — | Seller solicits the customer directly to bypass the platform | Contractual breach; evidence, warn, then remove per the agreement | R24 + Legal |
| — | Seller retains or misuses customer data after a job | Data-protection incident, not only a contract breach | DPO + CTO (`SP-005` TE-E9 pattern) |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Seller approval | Any | R24 Marketplace Operations Officer (`SP-004` A-76) | CCO |
| Seller payout — standard | Any | Automatic on schedule (`SP-004` A-77) | — |
| Seller payout — held or disputed | Any | R26 Finance Manager (`SP-004` A-78) | CFO |
| Seller approval + payout approval | **Incompatible** (`SOD-06`) | Different people | — |
| Seller suspension | Any | R24 (`SP-004` A-80) | CCO |
| Seller removal above the threshold | Any | CCO | CEO |
| Appeal decision | Any | An operator other than the one who imposed the consequence (`SOD-60`) | R24's manager |
| Dispute decision | Any | R24 — decided by 1000FiX, never the parties (`SP-004` A-81) | CCO |
| Commission or fee variation for one seller | Any | CCO + CFO | CEO |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Seller transacts before full approval | Control failure; suspend and investigate how it was possible | R24, CTO | Control exception |
| Seller performs work in an unqualified category | Suspend the category; review the completed jobs for quality exposure | R24, R32 | Nonconformity |
| Customer harmed or property damaged by a seller | Treat as a 1000FiX complaint first (`SP-028`); recover from the seller second | R05, Legal, R24 | Complaint + claim |
| Payout error | Correct immediately and explain; payout errors are existential for seller trust | R26 (`SP-005` CO-E6) | Payout correction |
| Dispute rate above the threshold | Root-cause analysis of the category, the seller cohort or the process — not seller-by-seller only | R24 → CCO | `KPI-081` review |
| Fake or incentivised reviews detected | Remove; warn or suspend; only completed-transaction customers may review (`BRU-ECM-02`) | R24 | Review integrity record |
| Seller registration or certification expired | Automatic suspension (`BRU-ECM-08`); reinstate on renewal | R24 | Expiry log |
| Seller data-access misuse | Revoke; report as a data-protection incident | DPO, CTO | Breach register |
| Collusion suspected between an operator and a seller | **L4-direct: CFO + Internal Audit**, restricted | As stated | Restricted record |
| `P07` unavailable | Sellers cannot accept jobs; route affected demand to owned capacity and inform sellers | R24, R33 | Outage record |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | Verification documents are collected and checked offline against the `MD-018` requirement set; the checklist is signed by R24 |
| 2 | The seller agreement is executed with wet ink where e-signature is unavailable and scanned into `M24` within 2 business days |
| 3 | **Activation does not occur manually.** A seller is activated only in the system, because the category, qualification and data-access controls are system-enforced |
| 4 | During a `P07` outage, jobs are not manually allocated to sellers — demand routes to owned capacity |
| 5 | Payouts are not released manually except by CFO approval against a reconciled statement |
| 6 | **Back-enter verification and agreement records within 48 hours** |

> Rows 3–5 are deliberate refusals. The marketplace's controls are almost entirely system-side;
> a manual path around them would be a manual path around the controls.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| No transaction before verification, signature and approval | Preventive (`BRU-ECM-01`) | Per seller | Hard block |
| Category listing restricted to verified qualification | Preventive (`BRU-ECM-07`) | Continuous | Hard block |
| Seller approval and payout approval separated | Preventive (`SOD-06`, `BRU-MKP-03`) | Per seller | Hard block |
| Appeal decided by a different operator | Preventive (`SOD-60`, `BRU-MKP-18`) | Per appeal | Hard block |
| Reviews only from completed transactions | Preventive (`BRU-ECM-02`) | Per review | Hard block |
| Customer data limited to awarded jobs and expiring | Preventive (`BRU-ECM-05`, `EA-04`) | Continuous | Record rules |
| Payout held while a dispute is open | Preventive (`BRU-BIL-03`) | Per payout | Hard block |
| Commission reversed on refund or adverse dispute | Preventive (`BRU-BIL-04`) | Per event | Computed |
| Registration expiry suspends automatically | Preventive (`BRU-ECM-08`) | Continuous | Suspension log |
| Marketplace job evidence sampled to the owned standard | Detective (`BRU-ECM-03`) | Weekly | Quality sample |
| Dispute rate and cause analysis | Detective | Monthly | `KPI-081` |
| Payout accuracy reconciliation | Detective | Per payout run | `KPI-082` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Approve a seller | Approve that seller's payout (`SOD-06`) | Hard block at assignment | — |
| Impose a marketplace consequence | Decide the appeal against it (`SOD-60`) | Hard block | **None. The appeal waits for a second operator** |
| Decide a dispute | Release the payout affected by it | Hard block | Payout release sits with Finance |
| Verify seller documents | Approve the seller where the value or risk threshold applies | Detective review | R24's manager samples verifications |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-079` | Approved active marketplace sellers | no baseline stated in `06-02` | 500 |
| `KPI-080` | Marketplace share of job volume | no baseline stated in `06-02` | 25% |
| `KPI-081` | Marketplace dispute rate | no baseline stated in `06-02` | < 1.5% |
| `KPI-082` | Seller payout accuracy | no baseline stated in `06-02` | **100%** |
| Time to onboard | Application to activation | untracked | To be set |
| Sellers transacting outside qualification | Control violations | untracked | **Zero** |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-039` Marketplace Seller Payout Statement | Issued at step 27 |
| `LG-018` Marketplace Seller Agreement | Signed at step 6 |
| `UI-034` Workspace — Marketplace Console Copy · `UI-017` `P07` Seller Portal Copy Pack | The screens used |
| [`SP-028_SOP_Complaint_Escalation_and_Compensation.md`](SP-028_SOP_Complaint_Escalation_and_Compensation.md) | Customer complaints about seller jobs |
| [`SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Nonconformities from sampled seller work |
| [`SP-008_SOP_On_Site_Field_Service_Visit.md`](SP-008_SOP_On_Site_Field_Service_Visit.md) | The delivery standard sellers are contractually held to |
| [`../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | `SOD-06`, `SOD-60` |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md) | Categories and standards |
| `EO-006` Marketplace Seller Onboarding Pack | The seller-facing onboarding content |
| `TR-019` Course Pack — Marketplace and Seller Operations | Trains this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | CCO with Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] The three preconditions to transacting stated and enforced
- [x] Appeal separation stated as having no compensating control
- [x] Manual fallback explicitly refuses to route around system-side controls
- [x] Seller work held to the owned-job quality standard
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] `LG-018` seller agreement written and reconciled with §7 — **outstanding; `LG` category not yet authored**
- [ ] Performance, visibility and suspension thresholds configured — **outstanding**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approvers recorded — **pending CCO and Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
