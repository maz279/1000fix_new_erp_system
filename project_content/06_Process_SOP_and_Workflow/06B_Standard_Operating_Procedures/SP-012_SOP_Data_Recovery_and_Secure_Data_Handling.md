---
id: SP-012
title: SOP — Data Recovery and Secure Data Handling
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Services with Security
author: Business Process Lead with Data Services and Information Security
reviewers: [CTO, Data Protection Officer, Legal Counsel, Quality Manager, Operations Director, Localisation Lead]
approver: Chief Technology Officer with Legal Counsel
content_class: C
purpose: >
  Data services touch the most sensitive material the company ever handles — a customer's entire
  personal or corporate data set, on a device they have lost access to. Access is restricted to
  the assigned case only, every access is logged, and the destruction certificate requires two
  distinct identities. This SOP defines the chain of custody, the isolated environment, the
  evidence and the destruction path, because a single mishandled case is a data-protection
  incident with contractual and reputational consequence out of all proportion to its revenue.
traces_to: [M06, M17, P03, DT-034, LG-009, LG-011, SP-004, SP-005, SP-025, SP-026, BRU-SEC-03, BRU-SEC-04, BRU-DTS-01]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: SP-012_SOP_Data_Recovery_and_Secure_Data_Handling_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06_Data_Services_and_Secure_Data_Handling.md — BRU-DTS-01, operator cannot be witness, certificate requires two distinct identities
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §11 BRU-SEC-03, BRU-SEC-04, BRU-AIM-03 (recovered data is never training data)
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §4 tier T5 — access to a data-recovery case limited to the assigned team, every access logged
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-073 data recovery success rate 82%, KPI-074 data-services custody exceptions zero
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.5.3 — property belonging to customers, including data, shall be identified, verified, protected and safeguarded
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Data Recovery and Secure Data Handling

| Item | Value |
|---|---|
| SOP ID | `SP-012` |
| Process owner | Chief Technology Officer with Legal Counsel |
| Roles performing | `R14` Data Services Technician · `R32` Quality Manager (witness) · `R33` IT / System Administrator · Data Protection Officer |
| Systems used | `P03` restricted data-services case view · `M06` · `M17` · isolated recovery environment |
| Frequency / volume | Low volume, high consequence. 5–12 technicians |
| ISO 9001 clause reference | **8.5.3** customer property · 8.5.1 controlled conditions · 7.5.3 control of documented information · 8.7 nonconforming outputs |

---

## 1. Purpose and Outcome

**Purpose.** To attempt recovery of a customer's data, or to destroy it verifiably, without any
person other than the assigned team seeing it, and with an evidence chain that would satisfy a
corporate client's auditor or a regulator.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Only the assigned team ever accessed the case | Access log; zero unassigned accesses (`BRU-SEC-03`) |
| The customer received their data, or a clear statement of why not | Handover record |
| Recovered data was purged at the agreed date | Purge log (`BRU-SEC-04`) |
| Destruction, where performed, is certified by two distinct identities | `DT-034` with operator and witness (`BRU-DTS-01`, `SOD-58`) |
| Zero custody exceptions | `KPI-074` |
| No recovered data ever entered a model, a test environment or a report | `BRU-AIM-03`, `BRU-SEC-08` |

---

## 2. Scope

**Applies to:** logical and physical data recovery from customer storage media; forensic-adjacent
data extraction where contracted; secure erasure and physical destruction of customer media; and
the handling of any device whose data is in 1000FiX possession as part of a data-services case.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Ordinary repair where data is incidentally present | `SP-010` — with the data-access-note rules of `SP-007` step 10 |
| Erasure of a device acquired through trade-in | `SP-025`; this SOP supplies the destruction and certification method |
| Disposal of company-owned end-of-life media | `SP-026` |
| Remote access to a live customer system | `SP-011` |
| Personal-data handling in ordinary business systems | `LG-009` and the platform controls in `M29` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Case | A data-services engagement, access-restricted to its assigned team (tier T5) |
| Isolated environment | A physically and logically separated workstation and storage area with no general network path and no removable-media egress |
| Chain of custody | The unbroken documented record of who held the media, when, and for what purpose |
| Operator | The person performing a destruction |
| Witness | A second, distinct person who observes and attests to the destruction (`SOD-58`) |
| Purge date | The agreed date at which recovered data is destroyed from 1000FiX systems (`BRU-SEC-04`) |
| Hold | A documented instruction that suspends the purge — legal, dispute or customer instruction |
| Image | A bit-level copy of the source media, worked on in place of the original |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Signed data-services engagement | `LG-011` | Scope, purge date, liability and success-fee terms agreed **before** the media is worked on |
| Case created with an assigned team | `M06` | Access restricted to that team (`BRU-SEC-03`, T5) |
| Media logged into the isolated environment | `M17` + custody log | Serial or unique identifier recorded and photographed |
| Isolated workstation available | `M47` | No general network, no unlogged removable media |
| Technician authorised and trained | `M22`, `M29` | Step-up authentication for case access (`BRU-SEC-02`) |
| Destination media for recovered data | `M15` | New or verifiably erased; never re-used from another case |
| Witness available for any destruction | Roster | Operator and witness must be different people |

---

## 5. Procedure

### 5.1 Intake into the data-services chain

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R14 | Receive the media from `SP-007` or `SP-009` **into the restricted chain**, not into the general workshop | `P03` case view | Custody transfer into T5 | 5 min |
| 2 | R14 | Photograph the media; record every identifier; note visible physical damage | `P03` | Condition record | 5 min |
| 3 | R14 | Confirm the engagement terms are signed, including the **purge date** and the success-fee basis | `M06` · `LG-011` | Terms confirmed | 3 min |
| 4 | R14 | Set the customer's expectation explicitly: recovery is **never guaranteed**, and partial recovery is a common outcome | `P03` / call | Expectation recorded | 5 min |
| 5 | R14 | Store the media in the secured data-services store; log the location | `P03` | Location logged | 2 min |

### 5.2 Assessment and recovery

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 6 | R14 | Assess in the isolated environment. **Do not write to the source media at any point** | Isolated workstation | Assessment record | 30–90 min |
| 7 | R14 | Take a bit-level image where the media permits. All subsequent work is on the image | Isolated workstation | Image created, hashed |
| 8 | R14 | Report feasibility and quote. Recovery proceeds only on the customer's approval of the quote | `P03` · `DT-005` | Approved quotation |
| 9 | R14 | Perform recovery on the image. Record the method and each attempt, including failures | `P03` | Recovery log |
| 10 | R14 | **Verify recovered data by structure and integrity, not by reading content.** Open files only to the minimum extent needed to confirm integrity | Isolated workstation | Verification record |
| 11 | R14 | Produce the recovery manifest — what was recovered, what was not, and the confidence in each | `P03` | Manifest |
| 12 | R14 | Write recovered data to new destination media; hash it | Isolated workstation | Destination media hashed |

### 5.3 Handover

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 13 | R14 | Verify the recipient's identity — the customer or their authorised representative only | `P03` | Identity verification |
| 14 | R14 | Hand over the destination media and the original media together, against signature | `P03` · `DT-009` | Handover record |
| 15 | R14 | Explain the manifest, including what could not be recovered | — | Briefing recorded |
| 16 | R14 | Set the purge timer for the working copies held by 1000FiX | `M06` | Purge scheduled (`BRU-SEC-04`) |
| 17 | System | Purge working copies at the agreed date unless a documented hold applies | `M06` | Purge log |

### 5.4 Secure destruction

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 18 | R14 | Confirm the destruction instruction and the standard to be applied | `P03` | Instruction recorded |
| 19 | R14 (operator) + R32 or another authorised person (witness) | Perform the destruction — cryptographic erase, overwrite, degauss or physical destruction as specified. **Operator and witness must be different people** (`SOD-58`) | — | Destruction performed |
| 20 | Both | Photograph the destroyed media with its identifier visible | `P03` capture | Photographic evidence |
| 21 | Both | Issue `DT-034` Data Destruction Certificate carrying **both identities**, the method, the standard, the date and a certificate number | `DT-034` | Certificate issued |
| 22 | R14 | Make the certificate available to the customer through `P01` or `P04` | Portal | Certificate downloadable |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 3 | Terms not signed | **Do not begin work.** No assessment, no imaging | R14; escalate to R22 Account Manager |
| 6 | Media is physically failing and imaging may destroy it | Advise the customer of the risk in writing and obtain explicit acceptance before proceeding | Customer, recorded |
| 6 | The environment is not isolated (network present, another case's media on the bench) | Stop. One case per bench at a time | R14 → CTO |
| 10 | Content that appears unlawful is encountered | **Stop immediately. Do not examine further. Do not discuss it.** Escalate to Legal Counsel and the DPO only | Legal Counsel; L4-direct |
| 10 | Content that is clearly outside the engagement scope but lawful | Do not read it; do not mention it in the manifest beyond its existence as a file | R14 |
| 11 | Recovery failed entirely | Report honestly with the methods attempted. Charge per the agreed no-recovery basis in `LG-011` | R14 |
| 13 | The person collecting is not the customer or a recorded authorised representative | **Do not hand over.** No exceptions | R14 → CTO |
| 17 | Purge date reached but a dispute or legal hold is open | Purge is suspended by the documented hold only; never by informal request | Legal Counsel |
| 19 | No witness available | **Destruction does not proceed.** The certificate is invalid with one identity (`BRU-DTS-01`) | — |
| — | A person outside the assigned team requests access | Refused and logged as a control event, not a service request | CTO |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Data destruction | Any | R14 operator **+ a distinct witness** (`SP-004` A-75, `SOD-58`) | R32 Quality Manager as witness |
| Add a person to a case team | Any | CTO; logged | — |
| Suspend a scheduled purge | Any | Legal Counsel, with a documented hold | CTO |
| Proceed on failing media with destructive risk | Any | Customer's recorded written acceptance | R22 |
| Recovery quotation | Per `SP-004` estimate bands | As `SP-004` A-01…A-04 | — |
| Export any recovered data from the isolated environment | **None — prohibited except the customer handover at step 14** | — | — |
| Use recovered data for testing, training or demonstration | **None — prohibited** (`BRU-AIM-03`, `BRU-SEC-08`) | — | — |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Unassigned access to a case | Blocked automatically; treated as a control violation | **L4-direct: CTO** (`SP-005` TE-E11) | Security incident |
| Media lost inside the facility | Immediate custody trace; treat as a personal-data incident from the outset, not as a mislaid item | CTO, DPO, Legal, customer | Breach register (`LG-009`) |
| Recovered data copied outside the isolated environment | Contain, identify every copy, destroy; report as a potential breach | **L4-direct: CTO + DPO + Legal** | Breach register |
| Unlawful content encountered | Stop; preserve; escalate to Legal Counsel only. Do not inform the customer without legal advice | Legal Counsel, CTO | Restricted record |
| Destruction performed without a witness | The certificate is void. Re-perform where possible; report the control failure | CTO, Quality Manager | Nonconformity → `SP-029` |
| Purge failed to execute | Investigate, purge manually, and report — an unpurged data set past its date is a live exposure | CTO, DPO | Purge exception |
| Customer disputes the recovery outcome | Route to `SP-028`; the recovery log and manifest are the evidence | R22, R32 | Complaint record |
| Isolated environment compromised | Disconnect; preserve; do not remediate before evidence capture | CTO + Legal | Security incident |

---

## 9. Manual Fallback

| Situation | Fallback |
|---|---|
| `P03` case view unavailable | Custody, access and actions are recorded on the **pre-numbered restricted paper case log**, held in the secured area and never removed from it. Back-entered within 24 hours |
| Certificate generation unavailable | Issue the **pre-numbered manual destruction certificate**, signed by operator and witness, photographed, and re-issued from the system when available. The manual certificate remains on file |
| Isolated workstation unavailable | **Work stops.** There is no fallback that permits recovery on a general-purpose machine |
| Witness roster gap | Destruction is scheduled, not improvised. No fallback |

> Two of these four state that there is no fallback. That is deliberate: for this process, an
> availability failure must not become a control failure.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Case access limited to the assigned team | Preventive (`BRU-SEC-03`, T5) | Continuous | Record rules; access log |
| Every case access logged | Detective | Continuous | Access log reviewed weekly |
| Step-up authentication for case access | Preventive (`BRU-SEC-02`) | Per access | Auth log |
| Source media never written to | Preventive, procedural | Per case | Imaging record and hashes |
| Operator ≠ witness on destruction | Preventive (`BRU-DTS-01`, `SOD-58`) | Per destruction | Certificate with two identities |
| Recovered data purged at the agreed date | Preventive (`BRU-SEC-04`) | Per case | Purge log |
| No egress from the isolated environment | Preventive | Continuous | Environment configuration |
| Recovered data never used as training data | Preventive (`BRU-AIM-03`) | Continuous | Model data lineage |
| Custody exceptions | Detective | Monthly | `KPI-074` — target zero |
| Certificate completeness sampled | Detective | Quarterly | Quality review |
| Case-team membership reviewed | Detective | Per access-certification cycle (`AUT-052`) | Certification record |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Perform a destruction | Witness it (`SOD-58`) | Hard block — certificate requires two identities | **None. This control has no compensating alternative**; the destruction waits for a witness |
| Be assigned to a case | Approve access for oneself (`SOD-09`) | Hard block | — |
| Prepare a records-disposal batch | Approve it (`SOD-23`) | Hard block | — |
| Hold case access | Administer the access rules for cases | Hard block at assignment | CTO administers; R14 has no administrative rights |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-073` | Data recovery success rate | no baseline stated in `06-02` | 82% |
| `KPI-074` | Data-services custody exceptions | no baseline stated in `06-02` | **Zero** |
| Certificates issued with two distinct identities | Completeness of `DT-034` | untracked | 100% |
| Purges executed on the agreed date | Purge timeliness | untracked | 100% |
| Unassigned access attempts | Attempts blocked by T5 rules | untracked | Trend to zero |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-034` Data Destruction Certificate | The output of step 21 |
| `LG-011` Data Services Engagement Terms | Signed before any work (step 3) |
| `LG-009` Data Protection and Privacy Policy | Breach handling and personal-data duties |
| [`SP-007_SOP_Walk_In_Intake_and_Front_Desk.md`](SP-007_SOP_Walk_In_Intake_and_Front_Desk.md) | Routes data cases into this restricted chain |
| [`SP-025_SOP_TradeIn_Refurbishment_and_Resale.md`](SP-025_SOP_TradeIn_Refurbishment_and_Resale.md) | Consumes this destruction method (`BRU-TRF-01`) |
| [`SP-026_SOP_EWaste_Collection_and_Disposal.md`](SP-026_SOP_EWaste_Collection_and_Disposal.md) | Consumes it again (`BRU-ESG-01`) |
| [`../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | `SOD-58` |
| [`../06A_Process_Architecture/SP-005_Escalation_Matrix.md`](../06A_Process_Architecture/SP-005_Escalation_Matrix.md) | TE-E9, TE-E11 |
| `TR-002` Role-Based Curriculum Map | **No course pack exists for R14 Data Services Technician** — gap raised in `AUDIT-006` |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | CTO with Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Chain of custody defined from intake to destruction
- [x] Operator/witness separation stated as having **no** compensating control
- [x] The unlawful-content path stops examination rather than continuing it
- [x] Prohibitions stated explicitly where no approval path exists
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] `LG-011` written and cross-checked — **outstanding; `LG` category not yet authored**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending CTO and Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
