---
id: FIX-ERP2-M06
module_id: M06
module_code: DTS
module_name: Data Services & Secure Data Handling
category: A — Service Delivery & Operations
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Technical Services Head
system_owner: Platform Squad
priority: P2
wave: W6
---

# M06 — Data Services & Secure Data Handling
### Category A · Code `DTS` · New in v2.0, retained in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M06 |
| **Module code** | `DTS` |
| **Category** | A — Service Delivery & Operations |
| **Status** | Existing (introduced in v2.0, retained in v2.1) |
| **Priority** | **P2** commercially · **P0** for the destruction-certificate control |
| **Delivery wave** | W6 (Months 23–26) |
| **Business owner** | Technical Services Head |
| **System owner** | Platform Squad |
| **Delivery layers** | L5 (custom) with L4 storage and encryption services |
| **Custom modules** | `cd_data_case`, `cd_media_custody`, `cd_destruction_cert` |
| **Requirement range** | FR-DTS-001 … FR-DTS-034 |
| **Requirement count** | 34 |
| **Effort estimate** | 18 person-weeks |
| **Depends on** | M01 Service Order · M17 Asset Registry · M29 Identity & Security · M24 Documents · M03 Logistics |
| **Depended on by** | **M14 Refurbishment (hard gate)** · **M18 E-Waste (hard gate)** · M05 MSP · M39 Subscription · M20 Receivable · M23 Quality · M26 |

---

## 2. Purpose

M06 does two things that look unrelated and are in fact the same thing: it **recovers
customers' data when they have lost it**, and it **destroys customers' data when the device
leaves 1000FiX's hands**.

Both are billable services. Both put the Company in temporary possession of information it
must never read, copy, retain or lose. M06 is therefore the most **confidentiality-critical**
module in the entire ERP — the only one where a single failure is a regulatory incident
rather than an operational one.

It is also the module that **gates two other business lines**. No device may be refurbished
and resold (M14), and no device may be sent for recycling (M18), without a certified data
destruction record produced here. That gate is a hard block with no override.

### Why It Exists

The business plan describes seven data recovery specialisms and five backup service types in
detail. It describes data wiping and privacy protection as part of the refurbishment process,
and data destruction as part of the recycling process. All of it is currently done — where it
is done at all — on job cards with no chain of custody, no access control, no retention limit
and no certificate.

For a company that is **ISO 9001:2015 certified**, holds an **ISMS policy**, and advertises
"100% secure — your device and data are secure", that is an exposure that scales with volume.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Business Plan §Data Recovery Services | Seven specialisms: hard drive, SSD, RAID, USB flash, memory card, mobile phone, email and database recovery |
| Business Plan §Data Backup Solutions | Five service types: cloud backup, on-site backup, hybrid backup, continuous data protection, data archiving |
| Business Plan §Refurbishment — Data Wiping and Privacy Protection | "1000fix Ltd. ensures that all customer data is securely wiped… industry-standard data-wiping techniques or specialized software tools to ensure complete data removal" |
| Business Plan §Recycling — Data Destruction | "Before recycling devices, 1000fix Ltd. ensures that all customer data is securely wiped… to protect customer privacy" |
| Company Profile §ISMS Policy | "Information Security Management System policy — data protection and privacy — secure device handling (100% secure)" |
| Company Profile §Customer Benefits | "100% secure device and data handling" is a published customer promise |
| ERP BRD NFR-023 *(corrected)* | The v1.0 BRD cited the **Digital Security Act 2018**. That statute was repealed by the Cyber Security Act 2023, which was itself repealed by the **Cyber Security Ordinance 2025**. The current obligation is the Cyber Security Ordinance 2025 together with the ICT Act 2006. *(Audit finding C-04a.)* |
| **Personal Data Protection Act 2026 (Law 63 of 2026)** | **Not referenced in any v1.0 or v2.0 document.** Enacted April 2026; enforcement mechanisms activate ~13 May 2027. Governs consent, transparency notices, data-subject rights, breach notification to the National Data Management Authority, Chief Data Officer appointment, five-year processing records and restriction on cross-border transfer of sensitive personal data. *(Audit finding C-04b.)* |
| ERP BRD NFR-025 | ISO 27001 security control alignment |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Data recovery case management across all seven specialisms |
| 2 | Media chain of custody under sealed-container and dual-control conditions |
| 3 | Free evaluation stage with recoverability assessment and firm quotation |
| 4 | Recovery methodology logging and attempt tracking |
| 5 | Recovered-data inventory without content exposure |
| 6 | Secure data handover and verified purge with certificate |
| 7 | Backup plan definition, job monitoring and restore testing |
| 8 | Backup capacity metering and usage-based billing basis |
| 9 | Data archival and retrieval services |
| 10 | Data migration as a service |
| 11 | **Secure data destruction: erasure, physical destruction, verification and certification** |
| 12 | Bulk corporate decommissioning projects |
| 13 | Cleanroom and specialist equipment scheduling |
| 14 | Partner laboratory referral with custody continuity |
| 15 | The access-control and audit regime that makes all of the above defensible |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Customer-facing service order, tracking and communication | **M01** | M06 creates a confidentiality-controlled case linked to a service order; the customer-facing view stays in M01 |
| Physical movement of media between sites | **M03** | Custody in transit is logistics; custody in the lab is M06 |
| Device refurbishment and grading | **M14** | M06 provides the certificate; M14 does the bench work |
| Recycling, partner transfer and disposal certificates | **M18** | M06 destroys the data; M18 disposes of the device |
| Backup **execution** on client infrastructure | **M05** | M05 monitors client backup jobs; M06 defines and sells the service |
| Pricing and quotation | **M11** / **M36** | Commercial decisions |
| Billing and invoicing | **M20** / **M39** | Only Category C and G handle money |
| 1000FiX's own internal backups and disaster recovery | **M30** / **M60** | Internal continuity is not a customer service |
| Encryption key management for the platform | **M29** | M06 uses the platform's key service; it does not operate one |
| Security incident response | **M60** / **M29** | M06 detects and reports; GRC investigates |

### 3.3 Shared Concepts

| Concept | M06's Role | Owning Module |
|---|---|---|
| Data case | Owns | M06 |
| Service order | Parent, with restricted visibility | M01 |
| Media item | Owns while in the lab | M17 owns the asset identity |
| Destruction certificate | Owns and issues | M24 retains |
| Custody event | Raises into the shared ledger | M03 |
| Backup plan | Owns the definition | M05 monitors execution |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **NIST SP 800-88 Revision 2** *(published 26 September 2025)* | A **programme-focused** framework: establish an enterprise media sanitisation programme as part of disposal or reuse, aligned to SP 800-53 and ISO/IEC 27040, with trust established in vendor implementation of sanitisation techniques | **The entire framework**, in its current revision. Programme framing; per-device Certificate of Sanitization; serial-number-level chain-of-custody evidence; vendor-trust verification | Nothing — this is the governing standard |
| **IEEE 2883** *(the technique standard r2 defers to)* | Prescriptive sanitisation techniques by media type | **Named as the Company's approved technique standard.** r2 removed technique detail and requires compliance with IEEE 2883, NSA specifications, or an organisationally approved standard | Inventing an internal technique standard where an accredited one exists |
| **ISO/IEC 19790** | Zeroization practice for cryptographic key management | Applied to cryptographic erase, which is the one technique r2 retains in detail | — |
| **ISO/IEC 27040** | Storage security | Alignment reference, per r2 | Full storage-security scope — that is M29's concern |
| ~~NIST SP 800-88 Revision 1~~ | ~~Clear / Purge / Destroy categories~~ | **Withdrawn 26 September 2025.** This module was originally drafted on r1; audit finding **H-01** required rebasing on r2 | — |
| **Enterprise ITAD / reverse-logistics practice** | Serialised asset tag on arrival opening a chain-of-custody log that follows the device through every stage; tamper-proof certificate of destruction per device | Per-item chain-of-custody log opened at intake; tamper-evident certificate | — |
| **Data recovery laboratory practice** | Free evaluation, no-recovery-no-fee, cleanroom for mechanical work, imaging before recovery attempts, chip-off for mobile | Evaluation-then-quotation model; image-first methodology; cleanroom booking as a constrained resource | — |
| **ISO/IEC 27001 Annex A controls** | Access control, secure disposal, media handling, logging and monitoring, supplier confidentiality | Least privilege, dual control, full access logging, staff confidentiality undertakings | Full ISMS scope — that is M60's concern |
| **Backup-as-a-service platforms** | Plan definition, job monitoring, restore testing, capacity metering | Restore testing as a mandatory, evidenced obligation — the part most providers skip | — |

**Design position.** Four deliberate differences, all more conservative than the benchmark.

First, **the destruction gate is absolute**. Most systems treat a wipe certificate as a
record. Here it is a **state-machine precondition** on two other modules: M14 cannot start
refurbishment and M18 cannot transfer to a recycler without it. There is no override, no
supervisor bypass and no "pending certificate" pathway.

Second, **recovered data is never a searchable asset**. The system records *that* files were
recovered, their types, counts and sizes — never their names or content. Nothing in the ERP
can be used to browse a customer's recovered data.

Third, **retention is time-boxed and enforced by the system**. Recovered data is purged
automatically at the agreed date, and the purge itself produces a certificate. The default is
deletion; retention requires a documented hold.

Fourth, **dual control on the secure area**. Media entering or leaving the controlled
environment requires two signatures. This is disproportionate for most repair work and exactly
proportionate for a facility holding other people's data.

---

## 5. Functional Areas & Features

### 5.1 Data Recovery Case Management

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DTS-001 | Case intake | Open a recovery case recording media type, failure symptoms, criticality, target data description and the customer's declarations | P2 | L5 |
| FR-DTS-003 | Free evaluation stage | Record a no-charge evaluation producing a recoverability assessment and a firm quotation before any chargeable work | P2 | L5 |
| FR-DTS-004 | Methodology log | Record the technique applied — logical, firmware, mechanical, chip-off, RAID reconstruction — and every step taken, with the operator's identity | P2 | L5 |
| FR-DTS-005 | Success-based pricing | Support no-recovery-no-fee and tiered pricing by data volume and complexity | P2 | L5 |
| FR-DTS-006 | Recovered-data inventory | List recovered volumes and file counts by type and size **without exposing file names or content** | P1 | L5 |
| FR-DTS-007 | Secure handover | Deliver recovered data on approved media or by secure transfer, with a signed receipt from a verified recipient | P1 | L5 |
| FR-DTS-025 | Cleanroom scheduling | Schedule and log cleanroom usage per case as a constrained resource | P3 | L5 |
| FR-DTS-026 | Specialist equipment tracking | Track use of specialist recovery equipment and consumables against the case | P3 | L5 |
| FR-DTS-027 | Partner laboratory referral | Refer a case beyond internal capability to a partner laboratory with custody continuity and commercial terms | P3 | L5 |
| FR-DTS-028 | Case prioritisation | Prioritise cases by criticality, contract and customer tier | P2 | L5 |
| FR-DTS-030 | Case costing | Track labour, consumables, equipment time and partner cost per case | P2 | L5 |

### 5.2 Chain of Custody & Access Control

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DTS-002 | Media chain of custody | Track physical media through evaluation, cleanroom, imaging, recovery, verification and return under sealed-container control | **P0** | L5 |
| FR-DTS-009 | Access restriction | Restrict access to a case workspace to named, MFA-authenticated, case-assigned staff only | **P0** | L5 |
| FR-DTS-010 | Confidentiality undertaking | Capture staff confidentiality undertakings per case, and customer NDAs where required | **P0** | L5 |
| FR-DTS-029 | Communication controls | Restrict what case detail may be communicated, to whom, and by which role | P1 | L5 |
| FR-DTS-033 | Compliance reporting | Report on custody, access, retention and destruction for internal and external audit | P1 | L5 |

### 5.3 Data Retention & Purge

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DTS-008 | Time-boxed retention | Hold recovered data only for the agreed window, then purge verifiably and issue a purge certificate | **P0** | L5 |
| FR-DTS-008b | Hold override | Permit retention beyond the window only under a documented, approved and time-limited hold | **P0** | L5 |

### 5.4 Secure Data Destruction

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DTS-019 | Wipe request | Accept a destruction request from refurbishment (M14), recycling (M18), a customer, or a corporate decommission project | P1 | L5 |
| FR-DTS-020 | Method and standard | Record the sanitisation technique applied **per IEEE 2883**, selected by data confidentiality, media type and final disposition under the Company's documented sanitisation programme, and verify completion | **P0** | L5 |
| FR-DTS-020a | Cryptographic erase | Where cryptographic erase is used, apply **ISO/IEC 19790** zeroization practice to the key material and record the key-destruction evidence as the sanitisation evidence | **P0** | L5 |
| FR-DTS-020b | Vendor trust verification | Where a sanitisation tool or a third-party service is used, record the evidence establishing trust in that vendor's implementation, per SP 800-88r2 | P1 | L5 |
| FR-DTS-020c | Sanitisation programme documentation | Maintain the Company's media sanitisation programme document — scope, roles, approved standard, technique matrix by media type, verification method, review cycle — as a controlled document in M24 | **P0** | L5 |
| FR-DTS-021 | Physical destruction | Record shredding, degaussing or crushing where erasure is not possible, with photographic evidence and a witness | P1 | L5 |
| FR-DTS-022 | Certificate of destruction | Issue a serialised, verifiable certificate per device recording method, standard, operator, date, witness and verification result | **P0** | L5 |
| FR-DTS-023 | Bulk decommission projects | Manage corporate bulk decommissioning with reconciliation against the client's declared asset list | P2 | L5 |
| FR-DTS-024 | Exception handling | Handle media that cannot be erased or verified, with escalation, physical destruction fallback and customer notification | P1 | L5 |

### 5.5 Backup, Archival & Migration Services

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DTS-011 | Backup plan definition | Define a customer's backup plan: scope, schedule, retention, destination (cloud, on-site, hybrid), encryption | P2 | L5 |
| FR-DTS-012 | Backup job monitoring | Monitor job outcomes and raise incidents on failure or missed schedule | P2 | L5 |
| FR-DTS-013 | Restore testing | Schedule and record periodic restore tests with evidence supporting the customer's own DR obligations | P2 | L5 |
| FR-DTS-014 | Capacity and usage billing | Meter storage consumed and provide the billing basis against the subscription tier, with overage | P2 | L5 |
| FR-DTS-015 | Archival service | Manage long-term archival with retrieval SLAs and retrieval charging | P3 | L5 |
| FR-DTS-016 | Continuous data protection | Track CDP-enabled assets and their recovery point coverage | P3 | L5 |
| FR-DTS-017 | Migration job | Manage device-to-device or platform migrations as a service with scope, checklist and verification | P3 | L5 |
| FR-DTS-018 | Migration verification | Record source and target counts and integrity verification, with customer sign-off | P3 | L5 |
| FR-DTS-031 | Backup storage provisioning | Provision and track storage allocated per customer backup plan | P2 | L5 |
| FR-DTS-032 | Restore request handling | Handle customer restore requests with SLA and verification | P2 | L5 |
| FR-DTS-034 | Data-services analytics | Report volume, success rate, turnaround, revenue and margin across all data services | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Per-case encryption keys** | Recovered data is encrypted at rest with a key unique to the case, destroyed at purge; key destruction is the purge |
| T-02 | **Content isolation** | No ERP query path can return the content or file names of recovered data; the inventory holds counts, types and sizes only |
| T-03 | **Named-user access enforcement** | Case workspace access is an explicit allow-list; role membership alone never grants access |
| T-04 | **Step-up authentication** | Opening a case workspace requires re-authentication regardless of an active session |
| T-05 | **Complete access logging** | Every read, list, copy, transfer and deletion within a case is logged immutably with actor, time and action, retained five years |
| T-06 | **Egress control** | Recovered data cannot leave the controlled environment except through the approved handover path; all other egress is blocked and alerted |
| T-07 | **Automated purge with proof** | Purge executes on schedule, verifies destruction, records the result and issues the certificate without human initiation |
| T-08 | **Tamper-evident certificates** | Destruction and purge certificates are hashed and countersigned; a verification endpoint confirms authenticity by certificate number |
| T-09 | **Dual-control enforcement** | Media entering or leaving the secure area requires two distinct authenticated signatures; the system rejects a single-signature record |
| T-10 | **Serial-level traceability** | Every certificate binds to a media serial number, so a certificate can be produced for any specific device on demand |
| T-11 | **Gate API** | The destruction-gate check exposed to M14 and M18 is a synchronous call that fails closed — no certificate means no proceed |
| T-12 | **Air-gap compatibility** | The recovery workspace operates on an isolated network segment; case records synchronise to the ERP without exposing the data environment |
| T-13 | **Performance** | Gate check ≤ 200 ms; certificate generation ≤ 3 s; certificate verification lookup ≤ 500 ms |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M06 |
|---|---|---|
| **Data services technician** | Works from a job card; no controlled workspace; retention by memory | Case workspace with named access, methodology logging, automatic purge |
| **Technical Services Head** | Cannot quote data recovery consistently or measure success rate | Evaluation-to-quotation flow, success rate by media type, margin per case |
| **Refurbishment officer** | Assumes the device was wiped | Cannot start work until the certificate exists — the system will not let them |
| **Quality manager** | Has no evidence of data handling for an ISO audit | Complete custody, access and destruction records for any period |
| **Corporate client** | Decommissions 300 laptops on trust | Receives a serialised certificate per device, reconciled to their own asset list |
| **Account manager** | Cannot answer "how do you handle our data?" in a tender | Has a documented, auditable process to put in the tender response |
| **CFO** | Carries an unquantified data-breach exposure | Carries a controlled, evidenced process — materially better insurability |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Data services revenue** | A deliverable, chargeable service line with consistent pricing and measured success | **BDT 30 lac/year** at steady state |
| **Backup subscription revenue** | Recurring revenue with metered capacity billing | Included in the above; grows with the MSP base |
| **Enables refurbishment revenue** | M14 cannot legally operate without certified destruction | Precondition for **BDT 65 lac/year** |
| **Enables recycling revenue** | M18 cannot transfer to a recycler without it | Precondition for **BDT 12 lac/year** |
| **Corporate decommission contracts** | Bulk decommissioning with per-device certification is a saleable service to every corporate client | New revenue line, sized after Wave 6 |
| **Tender qualification** | Corporate and government tenders increasingly require documented data handling | Removes a disqualifier from bids the Company currently cannot win |
| **Avoided breach cost** | A single publicised incident of a resold device containing customer data would cost more than the module | Risk avoidance, unquantified but material |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Makes the ISMS claim true** | The Company already publishes "100% secure — your device and data are secure". M06 is what makes that statement defensible rather than aspirational |
| **ISO 27001 readiness** | Media handling, secure disposal, access control and logging are among the most-tested Annex A controls |
| **Digital Security Act 2018 posture** | Documented consent, access control, retention limits and destruction evidence are the practical requirements |
| **Trust in the highest-anxiety moment** | A customer handing over a failed drive with their business on it is at their most anxious; visible process is what converts anxiety into loyalty |
| **Staff protection** | Named access and logging protect honest technicians from suspicion when a customer alleges data misuse |
| **Insurance and liability** | Documented process materially improves professional indemnity terms |
| **A moat competitors cannot casually copy** | Building this properly takes discipline, not money; most local competitors will not |

---

## 8. Lifecycle & State Models

### 8.1 Data Recovery Case

```
   ┌──────────────┐
   │   RECEIVED   │  media booked in under seal, dual signature
   └──────┬───────┘
          │ assigned to a named technician
   ┌──────▼───────┐
   │  EVALUATION  │  no charge · recoverability assessed · no write operations
   └──────┬───────┘
          │
   ┌──────▼───────────┐
   │ QUOTED           │  firm price issued to the customer
   └──────┬───────────┘
          │ customer accepts                    │ customer declines
   ┌──────▼───────┐                      ┌──────▼──────────┐
   │   IMAGING    │  work on the image,  │  RETURN MEDIA   │
   └──────┬───────┘  never the original  └─────────────────┘
          │
   ┌──────▼───────┐
   │   RECOVERY   │◄── multiple attempts, each logged with method
   └──────┬───────┘
          │
   ┌──────▼───────────┐   unsuccessful
   │  VERIFICATION    │──────────────► NO RECOVERY ──► return media, no fee
   └──────┬───────────┘
          │ successful
   ┌──────▼───────┐
   │  HANDOVER    │  recipient verified · signed receipt · media returned
   └──────┬───────┘
          │ retention window starts
   ┌──────▼───────────┐
   │ RETENTION HOLD   │  agreed window, e.g. 14 or 30 days
   └──────┬───────────┘
          │ window elapses (or documented hold extends it)
   ┌──────▼───────┐
   │    PURGED    │  automatic · verified · purge certificate issued
   └──────┬───────┘
          │
   ┌──────▼───────┐
   │    CLOSED    │
   └──────────────┘
```

### 8.2 Destruction Request

```
   REQUESTED ──► METHOD SELECTED ──► IN PROGRESS ──► VERIFIED ──► CERTIFIED ──► CLOSED
   (M14/M18/       (Clear / Purge /                     │
    customer/       Destroy, by                          └──► FAILED ──► PHYSICAL
    corporate)      confidentiality                                       DESTRUCTION
                    and disposition)                                          │
                                                                              ▼
                                                                          CERTIFIED
```

**The gate:** M14 and M18 query the certificate by media serial. A response of anything other
than `CERTIFIED` blocks their state transition. The call fails closed.

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-DTS-01 | Media entering or leaving the secure area requires two distinct authenticated signatures | **H** | Technical Services Head |
| BRU-DTS-02 | Case workspace access is limited to named, case-assigned, MFA-authenticated staff | **H** | CTO |
| BRU-DTS-03 | Every access to a case workspace is logged immutably and retained for five years | **H** | CTO |
| BRU-DTS-04 | Recovery work is performed on an image, never on the original media, wherever technically possible | **H** | Technical Services Head |
| BRU-DTS-05 | Recovered data is encrypted at rest with a case-specific key | **H** | CTO |
| BRU-DTS-06 | Recovered data is purged automatically at the agreed date unless a documented, approved and time-limited hold applies | **H** | CTO |
| BRU-DTS-07 | Recovered data may not leave the controlled environment except through the approved handover path | **H** | CTO |
| BRU-DTS-08 | The sanitisation technique is selected by data confidentiality, media type and final disposition under the Company's documented sanitisation programme, applying **IEEE 2883** as the approved technique standard per **NIST SP 800-88r2** | **C** | Quality Manager |
| BRU-DTS-16 | Recovered customer data and its index are held in a **Bangladesh-resident** store; they may not be replicated to a foreign region *(PDPA 2026, NFR-099 / NFR-086)* | **H** | CTO |
| BRU-DTS-17 | A breach affecting customer data held under a data case is assessed for significant damage and, where the threshold is met, **notified to the National Data Management Authority** within the prescribed timeframe | **H** | CDO / CTO |
| BRU-DTS-18 | Case records are retained for a minimum of five years as processing records under the PDPA 2026, independently of the purge of the data itself | **H** | Quality Manager |
| BRU-DTS-09 | **No device proceeds to refurbishment, resale or recycling without a valid certificate of destruction** | **H** | Quality Manager |
| BRU-DTS-10 | Where erasure cannot be verified, physical destruction is mandatory | **H** | Quality Manager |
| BRU-DTS-11 | Every certificate binds to a specific media serial number; blanket certificates are not permitted | **H** | Quality Manager |
| BRU-DTS-12 | Staff confidentiality undertakings are recorded per case before access is granted | **H** | HR Director |
| BRU-DTS-13 | Case details may be communicated only by authorised roles and only to the verified customer contact | **H** | Technical Services Head |
| BRU-DTS-14 | Recovered customer data is never used as training data for any model | **H** | CTO |
| BRU-DTS-15 | A partner laboratory referral requires a signed confidentiality agreement and continuous custody documentation | **H** | Technical Services Head |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.data.case` | `fix_data_case` | The confidentiality-controlled engagement | name, service_order_id, partner_id, case_type, media_type, criticality, state, assigned_team, opened_at, closed_at, confidentiality_level |
| `fix.media.item` | `fix_media_item` | Physical media held | data_case_id, asset_id, media_type, serial, capacity, seal_number, current_location, condition |
| `fix.media.custody.event` | `fix_media_custody_event` | Dual-control custody ledger | media_item_id, event_type, from_party, to_party, signature_1, signature_2, occurred_at, location, evidence_ref |
| `fix.recovery.attempt` | `fix_recovery_attempt` | Methodology log | data_case_id, sequence, method, equipment_ids, operator_id, started_at, ended_at, outcome, notes |
| `fix.recovered.inventory` | `fix_recovered_inventory` | Metadata only — never content | data_case_id, file_type, file_count, total_size_bytes, volume_label, recovered_at |
| `fix.case.access.log` | `fix_case_access_log` | Immutable access audit | data_case_id, actor_id, action, occurred_at, ip, session_ref |
| `fix.confidentiality.undertaking` | `fix_confidentiality_undertaking` | Staff and customer agreements | data_case_id, party_id, undertaking_type, signed_at, document_ref |
| `fix.wipe.request` | `fix_wipe_request` | Destruction request | source_module, source_ref, media_item_id, requested_by, confidentiality_level, disposition, state |
| `fix.destruction.certificate` | `fix_destruction_certificate` | The gate artefact | certificate_number, media_serial, asset_id, method, standard, operator_id, witness_id, executed_at, verification_result, hash, verification_url |
| `fix.purge.certificate` | `fix_purge_certificate` | Recovered-data purge proof | data_case_id, purged_at, method, verification_result, hash |
| `fix.cleanroom.booking` | `fix_cleanroom_booking` | Constrained resource scheduling | data_case_id, room_id, booked_from, booked_to, operator_id |
| `fix.backup.plan` | `fix_backup_plan` | Customer backup service definition | partner_id, contract_id, scope, schedule, retention_days, destination, encryption, capacity_gb |
| `fix.backup.run` | `fix_backup_run` | Job outcome | backup_plan_id, started_at, ended_at, outcome, bytes_transferred, error_ref |
| `fix.restore.test` | `fix_restore_test` | Evidenced restore verification | backup_plan_id, scheduled_for, executed_at, scope_tested, outcome, evidence_ref |
| `fix.migration.job` | `fix_migration_job` | Data migration as a service | partner_id, source_desc, target_desc, scope, verification_result, signed_off_by |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.service.order` | M01 | Parent, with restricted visibility |
| `fix.asset` | M17 / M49 | Read identity of the device the media came from |
| `fix.party` | M33 | Read customer and verified contacts |
| `fix.consignment` | M03 | Movement of media between sites |
| `fix.document` | M24 | Certificates and undertakings retained |
| `fix.tool.register` | M45 | Specialist recovery equipment |
| `fix.encryption.key.ref` | M29 | Per-case key material |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-DTS-01 | Data case opened | Apply the confidentiality classification, restrict visibility, require staff undertakings before access is granted | Case cannot proceed; alert Technical Services Head |
| AUT-DTS-02 | Media booked in | Require dual signature; generate a seal record; open the custody ledger for the item | Reject single-signature booking |
| AUT-DTS-03 | Evaluation completed | Produce the recoverability assessment; request a quotation from M36; notify the customer | Manual quotation task |
| AUT-DTS-04 | Customer accepts the quotation | Release the case to imaging; schedule the cleanroom if required | Manual scheduling |
| AUT-DTS-05 | Recovery completed | Generate the inventory (metadata only); notify the customer that data is ready for handover | Manual notification |
| AUT-DTS-06 | Handover completed | Start the retention clock; schedule the automatic purge at the agreed date | Manual purge scheduling with escalation |
| AUT-DTS-07 | Retention window elapses | Execute the purge, verify destruction, issue the purge certificate, notify the customer | **Escalate immediately** — an unpurged case beyond its window is a control failure |
| AUT-DTS-08 | Wipe request received from M14 or M18 | Select the method by confidentiality and disposition; queue for execution | Block the source module's transition |
| AUT-DTS-09 | Destruction verified | Issue the serialised certificate; publish it to the gate API; file it in M24 | Retry; escalate on repeated failure |
| AUT-DTS-10 | Erasure verification fails | Route to physical destruction; notify the requester; record the exception | Escalate to Quality Manager |
| AUT-DTS-11 | Backup job fails twice consecutively | Raise a priority incident; notify the customer and the account manager | Escalate |
| AUT-DTS-12 | Restore test due | Schedule, execute, record and publish the evidence to the customer | Escalate — an untested backup is an unproven backup |
| AUT-DTS-13 | Case idle beyond threshold | Alert the Technical Services Head — media held without progress is a custody risk | Escalate |
| AUT-DTS-14 | Attempted egress outside the approved path | Block, log, alert security immediately | Block and alert |

---

## 12. Interfaces

### 12.1 Upstream — M06 Consumes

| Source | What | Mechanism |
|---|---|---|
| M01 Service Order | Data-service intake as a confidentiality-controlled order | Command + event |
| M14 Refurbishment | Wipe request before refurbishment | Command |
| M18 E-Waste | Wipe request before recycling | Command |
| M05 Managed Services | Backup plan definitions and corporate decommission projects | Command |
| M03 Logistics | Media arrival and departure custody events | Event |
| M17 Asset Registry | Device identity for the media's parent asset | REST |
| M33 Party Master | Customer identity and verified contacts | REST |
| M29 Identity | Named access grants, MFA, step-up, key material | Service |
| M45 Test Equipment | Specialist recovery equipment identity | REST |

### 12.2 Downstream — M06 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M14 Refurbishment** | **Destruction certificate — hard gate** | Synchronous REST, fails closed |
| **M18 E-Waste** | **Destruction certificate — hard gate** | Synchronous REST, fails closed |
| M01 Service Order | Case status for the customer-facing timeline, without content detail | Event |
| M20 Receivable | Billable events: evaluation fee, recovery fee, destruction fee, storage overage | Events |
| M39 Subscription | Backup subscription usage and capacity basis | Events |
| M24 Documents | Certificates, undertakings, custody records for retention | Command |
| M23 Quality | Custody exceptions, verification failures, control breaches | Events |
| M60 GRC | Access anomalies and potential security incidents | Events |
| M25 Business Intelligence | Case volume, success rate, turnaround, margin | Warehouse extract (metadata only) |
| P01 Customer Portal | Case status, certificate download, backup status | REST |
| P04 Corporate Portal | Bulk decommission reconciliation and per-device certificates | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `data_case.opened` | case, customer, media type, classification | M01, M25 |
| `data_case.evaluated` | case, recoverability, quotation request | M36, M27 |
| `data_case.recovered` | case, inventory summary (counts and sizes only) | M01, M20, M27 |
| `data_case.handed_over` | case, recipient verification, retention window start | M01, M24 |
| `data.purged` | case, purge certificate, verification result | M24, M23 |
| `wipe.certified` | media serial, certificate number, method, standard | **M14**, **M18**, M24 |
| `wipe.failed` | media serial, reason, escalation to physical destruction | M14, M18, M23 |
| `custody.dual_control_recorded` | media item, both signatories, location | M03, M24 |
| `case.access_logged` | case, actor, action | M29, M60 |
| `case.egress_blocked` | case, actor, attempted action | M29, M60, management |
| `backup.run_failed` | plan, customer, consecutive failures | M05, M27 |
| `restore.test_completed` | plan, outcome, evidence | M05, P04 |
| `data.usage_reported` | case or subscription id, customer, period, backup storage volume, retention consumption | M39, M53, M20 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/data-cases` | POST | Open a data case | M01, P03 |
| `/api/v1/data-cases/{id}` | GET | Case detail — access-controlled, no content | P03 (named users only) |
| `/api/v1/data-cases/{id}/attempt` | POST | Record a recovery attempt | P03 |
| `/api/v1/data-cases/{id}/handover` | POST | Record verified handover | P03 |
| `/api/v1/wipe-requests` | POST | Request destruction | M14, M18, P03 |
| **`/api/v1/destruction-certificates/verify`** | **GET** | **Gate check by media serial — fails closed** | **M14, M18** |
| `/api/v1/destruction-certificates/{number}` | GET | Public certificate verification | Customer, auditor |
| `/api/v1/backup-plans` | GET / POST | Backup plan management | M05, P03 |
| `/api/v1/backup-plans/{id}/restore-tests` | GET / POST | Restore test scheduling and evidence | M05, P04 |
| `/api/v1/data-services/analytics` | GET | Volume, success rate, turnaround (metadata only) | P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R14 Data Services Technician | C R U D | **Own assigned cases only** — never all cases |
| Technical Services Head | C R U D A | All cases — with logged access |
| R32 Quality Manager / ISO Coordinator | R | Custody, certificates, exceptions — **not case content** |
| R33 IT / System Administrator | — | **No access to case workspaces**; platform administration only |
| R02 Chief Technology Officer | R | With explicit approval and logging — for investigation only |
| R08 Service Centre Agent | C R | Case creation and status only — no workspace access |
| R34 Contact Centre Agent | R | Status only, for customer enquiry |
| R26 Finance Manager | R | Billable events and costing — no case detail |
| R36 Customer | R | Own case status and certificates only |
| R37 Corporate Portal User | R | Own organisation's decommission project and certificates |

**This is the strictest permission model in the ERP.** Membership of a role never grants
access to a case; access is granted per case, to a named individual, and every access is
logged. Even the IT Administrator has no path into a case workspace.

**Field-level restrictions:** recovered-data inventory shows type, count and size only. File
names and content are not stored in the ERP at all.

**Segregation of duties:** the operator performing a destruction cannot be the witness
(BRU-DTS-01, and the certificate requires two distinct identities).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Case board | Data services team | Real time | Open cases by state, age, criticality, custody location |
| Custody exception report | Quality Manager, Technical Services Head | Daily | Single-signature attempts, seal breaks, unaccounted media, overdue purges |
| Access audit report | CTO, GRC | Weekly | Who accessed which case, when, and what action — with anomaly flags |
| Retention compliance | Quality Manager | Daily | Cases approaching or past their purge date |
| Destruction certificate register | Quality Manager, corporate clients | On demand | All certificates by period, client, method and media serial |
| Recovery success rate | Technical Services Head | Monthly | Success rate by media type, failure mode and technique |
| Case turnaround | Technical Services Head | Monthly | Evaluation-to-quotation and quotation-to-handover times |
| Case profitability | CFO, Technical Services Head | Monthly | Revenue against labour, consumables, equipment and partner cost |
| Backup service health | Technical Services Head, M05 | Weekly | Job success rates, consecutive failures, restore test currency |
| Bulk decommission reconciliation | Corporate client, account manager | Per project | Declared assets against certificates issued, with exceptions |
| ISO evidence pack | Quality Manager, auditor | Per audit | Custody, access, retention, destruction and undertaking records for a period |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-073 | Recovery success rate on accepted cases | unmeasured | 78% | **> 82%** |
| KPI-074 | Chain-of-custody exceptions | untracked | **0** | **0** |
| — | Average recovery turnaround | unmeasured | < 10 days | **< 7 days** |
| — | Certificates issued within 24 h of destruction | n/a | **100%** | **100%** |
| — | Cases purged on schedule | n/a | **100%** | **100%** |
| — | Cases held past retention without a documented hold | n/a | **0** | **0** |
| — | Unauthorised access attempts to a case workspace | n/a | **0** | **0** |
| — | Devices released to M14 or M18 without a certificate | n/a | **0** | **0** |
| — | Backup job success rate for managed customers | n/a | 98% | **> 99%** |
| — | Restore tests completed on schedule | n/a | **100%** | **100%** |
| — | Data services gross margin | n/a | 45% | **> 55%** |
| — | Bulk decommission reconciliation accuracy | n/a | **100%** | **100%** |

**Five of these targets are zero or one hundred per cent.** That is deliberate: in this module
a partial score is a control failure, not a performance gap.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L4 | Object storage with per-case encryption, key management service, isolated network segment | 22% |
| L5 | `cd_data_case`, `cd_media_custody`, `cd_destruction_cert` | 78% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-031 | `cd_data_case` — case, workspace, access control, methodology log, inventory | Odoo module | 7 PW |
| CD-032 | `cd_media_custody` — dual-control custody, seals, cleanroom booking | Odoo module | 4 PW |
| CD-033 | `cd_destruction_cert` — wipe request, method selection, certificate, **gate API**, verification endpoint | Odoo module + service | 5 PW |
| CD-034 | Backup service management — plan, monitoring, restore test, capacity metering | Odoo module | 2 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M29 Identity & Security | Named access, MFA, step-up, key management and audit are the foundation of the entire module |
| M24 Documents | Certificates and undertakings must be retained |
| M01 Service Order | The case has a customer-facing parent |
| M17 Asset Registry | Media links to a device |
| M03 Logistics | Media movement between sites |
| **M06 must be live in or before Wave 6** | M14 Refurbishment and M18 E-Waste cannot launch without the destruction gate |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing data recovery job cards | Current work only | `fix.data.case` | W6 cutover |
| Historical recovery records | **Not migrated** — historical cases contain no residual data and no certificates exist | — | — |

There is nothing meaningful to migrate. Critically, **any customer data currently held from
past recovery work must be audited and purged before Wave 6 go-live** — this is a
pre-implementation remediation task, not a migration.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A case workspace cannot be accessed by anyone not explicitly named on the case, including administrators | Negative test through UI, API and database role |
| AC-02 | Media cannot be booked in or out with a single signature | Negative test |
| AC-03 | Recovered data is encrypted with a case-specific key, and purge destroys the key | Cryptographic verification |
| AC-04 | Automatic purge executes on schedule and issues a verifiable certificate | Scripted scenario over a compressed retention window |
| AC-05 | **M14 cannot start refurbishment without a valid certificate for the device's media** | Negative test |
| AC-06 | **M18 cannot transfer a device to a recycler without a valid certificate** | Negative test |
| AC-07 | The gate API fails closed when unavailable — the calling module blocks rather than proceeds | Fault-injection test |
| AC-08 | Every access to a case is logged with actor, action and time, and is immutable | Audit log review and tamper test |
| AC-09 | Attempted egress outside the approved path is blocked and alerted | Penetration test |
| AC-10 | A certificate can be verified independently by its number | Public verification endpoint test |
| AC-11 | Sanitisation method selection follows NIST SP 800-88 by confidentiality and disposition | Configuration review and test matrix |
| AC-12 | No ERP query path returns recovered file names or content | Data-model review and query audit |
| AC-13 | A bulk decommission reconciles the client's declared asset list to certificates issued, with exceptions listed | Scripted project with 100 assets |
| AC-14 | Restore tests execute on schedule and produce customer-facing evidence | Two consecutive cycles |
| AC-15 | Any customer data held from pre-implementation recovery work has been audited and purged | Remediation completion record |
| AC-16 | Security review completed with zero critical or high findings | Independent security review |
| AC-17 | Technical Services Head and Quality Manager sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Does 1000FiX operate a cleanroom today, or is mechanical recovery referred to a partner? | Technical Services Head | W6 minus 3 months |
| Q-02 | What is the default retention period for recovered data — 14 days, 30 days, or customer-elected? | Legal / Technical Services Head | W6 build |
| Q-03 | Is the recovery workspace on an isolated network segment today? If not, what is the plan? *(decision D-08)* | CTO | W6 minus 2 months |
| Q-04 | Which partner laboratories are used, and are confidentiality agreements in place? | Technical Services Head / Legal | W6 minus 2 months |
| Q-05 | Does the Company hold professional indemnity cover for data loss during recovery? | CFO / Legal | W6 minus 3 months |
| Q-06 | What sanitisation standard will be quoted to corporate clients — NIST SP 800-88 Purge as default? | Quality Manager | W6 build |
| Q-07 | **Is there customer data currently held from past recovery work?** If so, an audit and purge is required before go-live. | Technical Services Head | **Immediately** |
| Q-08 | Will backup services be delivered on 1000FiX infrastructure or a partner cloud? This determines data residency. | CTO / Legal | W6 minus 3 months |

**Q-07 is not a design question.** It is an active exposure that should be investigated now,
independently of the ERP programme.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` · `M14_TradeIn_Refurbishment_and_Resale.md` (gate consumer) ·
`M18_EWaste_Recycling_and_Circular_Economy.md` (gate consumer) ·
`03_Modules/D_Circular_and_Asset_Based_Business/_CATEGORY_OVERVIEW.md` §4 (the non-negotiable gate) ·
`03_Modules/K_Platform_and_Technology/M29_Identity_Access_and_Information_Security.md` ·
`05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §10 (S3 classification)

**Workspace evidence**
`1000fix_business/Business planning for 1000 fix.docx` §Data Recovery Services (seven
specialisms), §Data Backup Solutions (five types), §Refurbishment — Data Wiping and Privacy
Protection, §Recycling — Data Destruction ·
`1000FiX_Services_Company_Profile.md` §ISMS Policy, §Customer Benefits ("100% secure") ·
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` NFR-023, NFR-025

**External benchmark**
**NIST SP 800-88** *Guidelines for Media Sanitization* — Clear, Purge and Destroy categories
selected by information confidentiality, media type, risk, whether media leaves organisational
control, and final disposition; Certificate of Sanitization; serial-number-level
chain-of-custody evidence · **NIST SP 800-88 Rev. 2** — programme-focused framework for
consistent sanitisation before reuse, resale, redeployment or disposal ·
Enterprise ITAD and reverse-logistics practice — serialised asset tag opening a
chain-of-custody log maintained through every stage, tamper-proof per-device certificate ·
ISO/IEC 27001 Annex A — media handling, secure disposal, access control, logging ·
Data recovery laboratory practice — free evaluation, no-recovery-no-fee, image-first
methodology, cleanroom for mechanical work

---

*Module M06 · Category A · 1000FiX ERP System v2.0 · CONFIDENTIAL*
