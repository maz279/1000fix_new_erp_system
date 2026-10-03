---
id: RQ-002
title: System Requirements Specification (SyRS)
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer
approver: ERP Design Authority
standards_basis: ISO/IEC/IEEE 29148:2018 §9.5 (SyRS content) · §5.2.4–5.2.8 · ISO/IEC/IEEE 15288:2023 (system life cycle context)
traces_to: PGD-000 RQ-002 row · 05-06 §10 (environmental and device support) · 06-01 §6 (rollout geography) · audit OP-01, OP-02 (no lawful DR path, dr environment unsized)
depends_on: RQ-001 (software boundary), RQ-005 (management plan)
verified_on: 2026-08-18
priority: P1
needed_by: W1
enumerated_on: 2026-08-18 02:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RQ-002 — System Requirements Specification
# The System Above the Software Boundary

### Category 01 · Code `RQ` · ISO/IEC/IEEE 29148:2018 §9.5

---

> **Why this document exists separately from the SRS.** ISO/IEC/IEEE 29148:2018 distinguishes the
> **System** Requirements Specification (§9.5) from the **Software** Requirements Specification
> (§9.6) because a system is more than its software. 1000FiX will deploy an ERP into 51+ branches
> across eight divisions of Bangladesh, onto 200–400 Android devices carried outdoors by
> technicians on 3G, with thermal printers, barcode scanners, biometric readers and GPS, over
> connectivity the Company does not control, powered by a grid that is not continuous.
>
> **None of that has a requirement owner today.** `05-06` §10 lists supported devices in a
> capability table; it states no obligation on the system, no measurement, and no verification.
> Every one of those conditions can defeat a perfectly correct piece of software.
>
> `SYR-001` … `SYR-058` in §4 are the requirements on the **system**. Where a system requirement
> is discharged by software, it names the `SWR` or `FR` that discharges it. Where it is discharged
> by hardware, network, facility, contract or procedure, it names the owner who must deliver it.

---

## 1. Purpose

The software will be correct and the deployment will still fail if a branch has no reliable
power, if a technician's device cannot hold a day's job data, if the barcode scanner in Khulna is
a different model from the one tested in Dhaka, or if the disaster-recovery site holding
Bangladesh-resident personal data turns out to be in Singapore. This document states, as testable
requirements, what the **system** — hardware, network, facilities, devices, third-party services
and the people-facing environment — shall provide so that the software specified in `RQ-001` can
do its job.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | System purpose, scope and overview above the software boundary (§4.1–4.4) |
| 2 | System-level functional, usability and performance requirements (§4.5–4.7) |
| 3 | System interfaces, operations, and modes and states (§4.8–4.10) |
| 4 | Physical characteristics — devices, peripherals, branch hardware (§4.11) |
| 5 | Environmental conditions — climate, power, connectivity, light, handling (§4.12) |
| 6 | System security requirements above the software (§4.13) |
| 7 | Information management requirements — residency, retention, custody (§4.14) |
| 8 | Policy and regulation requirements binding the system (§4.15) |
| 9 | System life-cycle sustainment — spares, support, device refresh (§4.16) |
| 10 | Packaging, handling, shipping and transportation of system elements (§4.17) |
| 11 | Verification (§4.18) and assumptions and dependencies (§4.19) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| What the software shall do | `RQ-001` | This document is §9.5; that document is §9.6 |
| Network topology, VPCs, subnets, TLS termination | `PE-001` | A design realising `SYR-020`–`SYR-027`, not a requirement |
| Environment sizing and the `dr` environment | `PE-002`, `PE-007` | Design; this document states the obligation those designs must satisfy |
| Device procurement and vendor selection | `CO-006` | Commercial |
| Data residency architecture | `SC-007` | Design realising `SYR-041`–`SYR-044` |
| Quality-attribute targets on the software | `RQ-006` | Software attributes |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Platform engineering | The obligations `PE-001` … `PE-009` must satisfy |
| Procurement | The device, peripheral and connectivity specification to buy against (`CO-006`) |
| Branch operations | Site readiness criteria for the T−4 assessment in `06-01` §6 |
| Rollout manager | The per-site gate: a site that fails §4.12 is not ready |
| CISO / DPO | Physical and residency obligations the software cannot discharge alone |
| Implementation vendor | What is provided *to* the software, so it is not priced as a software problem |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure |
|---|---|---|---|
| ISO/IEC/IEEE 29148:2018 | §9.5.1–9.5.19 | §4.1–§4.19 map one-to-one onto the nineteen SyRS content clauses in the standard's order and under its names | None |
| ISO/IEC/IEEE 29148:2018 | §5.2.4, §5.2.5, §5.2.7 | Every `SYR` uses the mandated construct, satisfies the nine characteristics and avoids the banned language | None |
| ISO/IEC/IEEE 29148:2018 | §5.2.8 | Attributes per `RQ-001` §3.10.3, with `layer` and `fit_gap` not applicable at system level | Two attributes marked `n-a` |
| ISO/IEC/IEEE 15288:2023 | System life cycle processes | §4.16 sustainment written against the life-cycle model | Cited for context only |

**Verified on 2026-08-18.** ISO/IEC/IEEE 29148:2018 is the current second edition.

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06` §10 | Device and browser support matrix; peripherals; network floor |
| `.../05-06` §2, §6.4 | Availability tiers; split-residency position; `NFR-086`, `NFR-007` |
| `.../06_Delivery_and_Implementation/06-01` §6 | Rollout geography; the T−4 → T+4 per-site pattern |
| `.../02_Architecture/02-05` §8 | Production sizing at Wave 8 steady state |
| `../../primary-doc/…BRD.md` §6 | Current-state operating conditions across the branch estate |
| `../../project_content/17_Operations_Support_and_Runbooks/` | Operational content presuming infrastructure that is not yet specified |
| `RQ-001` §3.7, §3.12 | The software's limitations and the programme-level software requirements this document sits above |

### 2.3 Audit findings this document addresses

| Finding | Source | Treatment |
|---|---|---|
| `OP-01` (critical) | Repository audit | **There is no lawful DR path for Bangladesh-resident personal data.** `SYR-044` states the obligation as a requirement so that `PE-007` and `SC-007` have something to satisfy. **Not closed here** — it needs a resident DR target to exist |
| `OP-02` (critical) | Repository audit | The `dr` environment is named in the architecture and sized nowhere. `SYR-045` makes DR capability a system requirement with `NFR-007` as its target | Closed by `PE-002` + `PE-007` |
| `C-05` (critical) | `00-06` | Singapore-region topology may be unlawful. `SYR-041`–`SYR-043` express residency as a system obligation independent of the chosen topology | Closes with the `DEP-31` legal opinion |
| `M-09` | `00-06` | Wave capacity never validated against effort. `SYR-055` makes per-site readiness a measured gate rather than an assumption | Partially — `GV-007` completes |

---

# 3. System Overview

## 3.1 System purpose *(§9.5.2)*

The system exists to make after-sales service in Bangladesh **measurable and coordinable at
national scale**. Its purpose is not to run software; it is to place a working, connected,
powered, staffed and instrumented capability into 51+ physical locations and into the hands of
several hundred people who work outdoors, so that every service event that occurs in the physical
world is captured once, at the point it happens, in a form the ERP can act on.

## 3.2 System scope *(§9.5.3)*

| Element | In the system | Not in the system |
|---|---|---|
| ERP software and 12 portals | ✔ | |
| Branch counter hardware — workstations, printers, scanners, queue displays, kiosks | ✔ | |
| Field devices — technician, rider and auditor handsets, chargers, mounts | ✔ | |
| Biometric attendance terminals | ✔ | |
| Branch and HQ connectivity — primary and failover | ✔ | Public internet backbone |
| Power — mains, UPS, generator where present | ✔ | National grid |
| Hosting, network and DR infrastructure | ✔ | |
| Third-party services — payment rails, NBR portal, BEFTN, SMS/WhatsApp, couriers | Interface obligations only | The services themselves |
| Vehicles | Telemetry and assignment only | Fleet ownership (`M46` manages, does not specify) |
| Customer-owned devices under repair | Custody and identity only | |

## 3.3 System overview *(§9.5.4)*

```
   PHYSICAL ESTATE                     CONNECTIVITY                 PLATFORM
   ┌──────────────────────┐            ┌──────────────┐             ┌──────────────────┐
   │ 51+ branches         │  primary   │ Fixed line   │             │ Application tier │
   │  · counter WS        ├───────────▶│ + LTE        ├────────────▶│ Odoo 19 CE + OCA │
   │  · thermal + label   │  failover  │ failover     │   TLS 1.2+  │ + custom + svcs  │
   │  · scanner, pad      │            └──────────────┘             ├──────────────────┤
   │  · queue display     │                                         │ Data tier        │
   │  · biometric term.   │            ┌──────────────┐             │ PostgreSQL 16    │
   │  · UPS               │            │ 3G / 4G      │             │ Timescale ·      │
   ├──────────────────────┤   mobile   │ intermittent │             │ ClickHouse ·     │
   │ 200–400 technicians  ├───────────▶│ 24 h offline ├────────────▶│ MinIO            │
   │ ~100 riders          │            │ tolerated    │             ├──────────────────┤
   │  · Android 11+ 3 GB  │            └──────────────┘             │ Resident store   │
   │  · GPS, camera       │                                         │ (Bangladesh)     │
   │  · vehicle mount     │            ┌──────────────┐             ├──────────────────┤
   ├──────────────────────┤            │ Third-party  │             │ DR target        │
   │ Warehouses / hubs    │◀──────────▶│ bKash·Nagad· │◀───────────▶│ (SYR-044:        │
   │  · scanners, labels  │            │ NBR·BEFTN·   │             │  lawful location │
   └──────────────────────┘            │ SMS·courier  │             │  UNRESOLVED)     │
                                       └──────────────┘             └──────────────────┘
```

## 3.4 Environment of use

| Condition | Reality | System consequence |
|---|---|---|
| Climate | 10–40 °C ambient; monsoon June–October; humidity to 95% | Device and printer selection; sealed enclosures at outdoor points |
| Power | Load-shedding and voltage instability in parts of the estate | UPS at every branch; device battery endurance is a requirement, not a preference |
| Connectivity | Fixed-line availability varies by division; 3G is the realistic floor outside metros | 24-hour offline is a system property, not an app feature |
| Light | Direct sunlight for field work; low light in workshops | Screen legibility requirement |
| Handling | Devices carried on motorcycles, used with gloves and wet hands | Drop, ingress and one-handed-use requirements |
| Literacy and language | Bengali-first; variable English literacy | Bengali rendering on **every** output device, including thermal print |
| Security of premises | Branch counters are public-facing | Physical access control on any terminal holding personal data |

---

# 4. System Requirements

*Structured per ISO/IEC/IEEE 29148:2018 §9.5. Identifier space `SYR-nnn` — swept across all four
repositories at 2026-08-18 02:15 (+06), zero prior occurrences; reservation to be ratified by
`RR-002`.*

## 4.5 Functional requirements *(§9.5.5)*

| ID | Requirement | Pri | Verif. | Discharged by |
|---|---|:--:|:--:|---|
| `SYR-001` | The system shall capture every service event at the location and time it occurs, without requiring a subsequent transcription step. | **P0** | Demonstration | `RQ-001` + field devices |
| `SYR-002` | The system shall permit a branch to complete walk-in intake, handover and payment when the branch's primary connectivity is unavailable, and shall reconcile the resulting records on restoration. | **P0** | Test | `SWR-030`–`SWR-032`, `SYR-024` |
| `SYR-003` | The system shall identify a customer-owned device uniquely by serial, IMEI or asset tag captured by scan, and shall accept keyboard entry only where a scan fails. | **P0** | Test | `M17`, `SYR-030` |
| `SYR-004` | The system shall record physical custody of a customer-owned device at every transfer between parties, with the transferring and receiving identities. | **P0** | Test | `M01`, `M03`, `M31` |
| `SYR-005` | The system shall produce a printed customer-facing document at the point of counter transaction, in the language recorded for that customer. | **P0** | Demonstration | `SYR-031`, `DT-*` |
| `SYR-006` | The system shall record employee attendance by biometric verification at branch locations designated for it. | P1 | Test | `M55`, `SYR-033` |
| `SYR-007` | The system shall report the position of each technician and rider on shift at intervals not exceeding 30 seconds while the device has connectivity. | P1 | Test | `M02`, `SYR-029` |
| `SYR-008` | The system shall accept payment by cash, card, bKash, Nagad, SSLCOMMERZ and bank transfer at every branch counter. | **P0** | Demonstration | `M20`, `IN-007` |

## 4.6 Usability requirements *(§9.5.6)*

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-009` | The system shall permit a trained counter agent to complete a walk-in intake within 3 minutes, measured from customer arrival at the counter to receipt issue, over 20 consecutive observed transactions. | **P0** | Test |
| `SYR-010` | The system shall permit a new service agent to reach declared competence within 4 hours of training. | P1 | Demonstration |
| `SYR-011` | The system shall present every field-device screen legibly in direct sunlight at the device's maximum brightness. | P1 | Demonstration |
| `SYR-012` | The system shall permit a technician wearing work gloves to complete every field workflow step without removing them. | P1 | Demonstration |
| `SYR-013` | The system shall permit one-handed operation of the rider workflow. | P1 | Demonstration |

## 4.7 Performance requirements *(§9.5.7)*

*Software latency targets are `RQ-006`'s. These are requirements on the **system**.*

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-014` | The system shall sustain full branch operation at each site for not less than 4 hours of mains power interruption. | **P0** | Test |
| `SYR-015` | The system shall complete a field device's synchronisation of 24 hours of accumulated offline work within 30 seconds on a 3G connection. | **P0** | Test |
| `SYR-016` | The system shall support a field device duty cycle of one 8-hour shift on a single charge, excluding turn-by-turn navigation. | **P0** | Test |
| `SYR-017` | The system shall consume not more than the data volume budgeted per technician per shift in `RQ-006`, with non-critical uploads deferred to connectivity classified unmetered. | P1 | Test |
| `SYR-018` | The system shall support 800 concurrent internal users and 75,000 concurrent portal users at the Wave 8 steady state. | **P0** | Test |
| `SYR-019` | The system shall print a counter receipt within 5 seconds of the print instruction, including Bengali glyph rendering. | P1 | Test |

## 4.8 System interface requirements *(§9.5.8)*

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-020` | The system shall connect every branch to the platform over an encrypted channel using TLS 1.2 as the minimum and TLS 1.3 where both endpoints support it. | **P0** | Inspection |
| `SYR-021` | The system shall provide each branch with a failover connectivity path independent of its primary carrier. | **P0** | Demonstration |
| `SYR-022` | The system shall interface with the NBR VAT Online portal (vat.gov.bd) for Mushak 6.3 issue and Mushak 9.1 return submission. | **P0** | Demonstration |
| `SYR-023` | The system shall interface with BEFTN for payroll and vendor disbursement. | **P0** | Demonstration |
| `SYR-024` | The system shall queue and retain, on the originating device or branch workstation, every transaction created while its connectivity is unavailable, and shall lose no queued transaction on device restart or power loss. | **P0** | Test |
| `SYR-025` | The system shall interface with each brand partner's claim channel by the mechanism that partner supports, and shall record the mechanism per partner. | P1 | Inspection |
| `SYR-026` | The system shall interface with contracted courier services for consignment creation and tracking. | P1 | Demonstration |
| `SYR-027` | The system shall deliver customer notifications by SMS, WhatsApp and email through contracted gateways, and shall fail over between SMS providers without message loss. | **P0** | Test |

## 4.9 System operations *(§9.5.9)*

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-028` | The system shall be operable during Bangladesh business hours 09:00–22:00 BST with availability not below the `NFR-006` target, and 24×7 at the `NFR-045` target for managed services. | **P0** | Test |
| `SYR-029` | The system shall be monitored such that a component failure raises an alert to a named on-call recipient within the interval defined in `SV-004`. | **P0** | Demonstration |
| `SYR-030` | The system shall provide each branch with barcode and QR scanning capability at every intake and handover point. | **P0** | Inspection |
| `SYR-031` | The system shall provide each branch with thermal receipt printing and adhesive label printing, both rendering Bengali correctly. | **P0** | Test |
| `SYR-032` | The system shall provide a customer signature capture device at every handover point. | P1 | Inspection |
| `SYR-033` | The system shall provide biometric attendance terminals at every location designated in `M55`. | P1 | Inspection |
| `SYR-034` | The system shall schedule planned maintenance outside 08:00–23:00 BST, not exceeding 4 hours per month, announced 72 hours in advance. | P1 | Inspection |
| `SYR-035` | The system shall provide every P0 external integration with a documented and exercised manual fallback procedure. | **P0** | Demonstration |

## 4.10 System modes and states *(§9.5.10)*

| Mode | Definition | Entry | Exit | Requirement |
|---|---|---|---|---|
| **Normal** | Connectivity, power and platform all available | Default | Any degradation | — |
| **Degraded — connectivity** | A site or device has lost its network path | Loss detected | Restoration | `SYR-036` |
| **Degraded — platform** | A platform component is unavailable; the rest continues | Component alert | Component restored | `SYR-037` |
| **Offline** | A field device operates with no network for up to 24 hours | Connectivity loss | Reconnection | `SYR-002`, `SYR-015` |
| **Maintenance** | Planned change in progress | Announced window | Window close | `SYR-034` |
| **Disaster recovery** | Primary site unavailable; service runs from the DR target | DR declaration | Failback | `SYR-045` |
| **Manual fallback** | System unavailable; the branch operates on paper | Declared by branch manager | Restoration and back-capture | `SYR-038` |

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-036` | On loss of connectivity at a site or device, the system shall continue to accept the workflows declared offline-capable and shall indicate the degraded state to the user. | **P0** | Test |
| `SYR-037` | On failure of a non-essential platform component, the system shall continue to serve every capability not dependent on it, and shall not present a whole-system failure. | **P0** | Test |
| `SYR-038` | On entry to manual fallback, the system shall provide the branch with the printed forms and the back-capture procedure required to reconcile on restoration, and shall reconcile without duplicate records. | **P0** | Demonstration |

## 4.11 Physical characteristics *(§9.5.11)*

| ID | Element | Requirement | Pri | Verif. |
|---|---|---|:--:|:--:|
| `SYR-039` | Field device | The system shall operate on Android 11 or later with not less than 3 GB RAM, 32 GB storage, GPS, camera and 4G. | **P0** | Inspection |
| `SYR-040` | Field device ruggedness | The system shall provide field devices with protection sufficient to survive a 1.2 m drop onto a hard surface and ingress of dust and rain at the level specified in procurement. | P1 | Test |
| `SYR-046` | Branch workstation | The system shall provide each counter position with a workstation displaying not less than 1366×768. | **P0** | Inspection |
| `SYR-047` | Peripherals | The system shall standardise thermal printers, label printers, scanners, signature pads, queue displays, kiosks and biometric terminals to a single approved model per class across the estate, with a documented exception procedure. | P1 | Inspection |
| `SYR-048` | Power | The system shall provide each branch with uninterruptible power sufficient for `SYR-014`, and shall alert on UPS battery health. | **P0** | Test |
| `SYR-049` | Vehicle fitment | The system shall provide a device mount and charging capability in every vehicle assigned to a rider or technician. | P2 | Inspection |
| `SYR-050` | Consumables | The system shall specify a single approved thermal paper and label stock that renders Bengali legibly and remains legible for the retention period of the document printed on it. | P1 | Test |

> **`SYR-047` is the requirement that prevents the most common national-rollout failure.** A
> second scanner model bought locally in Rajshahi because the approved one was out of stock is
> how a tested integration becomes an untested one at a site nobody visits.

## 4.12 Environmental conditions *(§9.5.12)*

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-051` | The system shall operate in ambient conditions from 10 °C to 40 °C and relative humidity to 95% non-condensing. | **P0** | Test |
| `SYR-052` | The system shall remain operable at outdoor points of use during monsoon rainfall. | P1 | Demonstration |
| `SYR-053` | The system shall present field-device output legibly at an illuminance representative of direct Bangladeshi daylight. | P1 | Test |
| `SYR-054` | The system shall provide sufficient illumination at every workshop inspection and photographic evidence point for photographic evidence to satisfy the acceptance criteria in `M31`. | P2 | Inspection |
| `SYR-055` | The system shall assess each site against a documented readiness standard covering connectivity, power, hardware, physical security and staffing, not less than 4 weeks before that site's go-live, and shall record the assessment result as a go-live gate. | **P0** | Inspection |

## 4.13 System security requirements *(§9.5.13)*

*Software security is `RQ-006` and `SC-001`. These are obligations the software cannot discharge.*

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-056` | The system shall restrict physical access to any terminal, server or storage device holding personal data to authorised personnel, and shall record that authorisation. | **P0** | Inspection |
| `SYR-057` | The system shall enrol every field device to a managed identity, and shall permit remote revocation of that device's access on loss, theft or the holder's departure. | **P0** | Demonstration |
| `SYR-058` | The system shall render customer-owned media and recovered customer data physically secure while in 1000FiX custody, with access recorded per access event. | **P0** | Inspection |

## 4.14 Information management requirements *(§9.5.14)*

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-041` | The system shall hold every data field classified `resident` — national identity number, passport number, TIN, biometric template, recovered customer data and its index, and marketplace seller KYC and criminal-record documents — in a data store physically located in Bangladesh. | **P0** | Inspection |
| `SYR-042` | The system shall permit a record to be assembled from a resident store and a regional store by a resident key, and shall not duplicate a `resident` field into the regional store to achieve it. | **P0** | Analysis |
| `SYR-043` | The system shall record an Authority notification and a documented safeguard before executing any cross-border transfer of a `resident` field. | **P0** | Inspection |
| `SYR-044` | The system shall provide a disaster-recovery target for `resident` data that is itself lawful under the Personal Data Protection Act 2026. | **P0** | Inspection |
| `SYR-045` | The system shall restore service after loss of the primary site within the recovery time objective of `NFR-007`, losing not more than the recovery point objective of `NFR-007`, demonstrated by a full failover exercise twice yearly. | **P0** | Test |

> **`SYR-044` is currently unsatisfiable and is stated anyway.** Audit `OP-01` records that no
> lawful DR path exists for Bangladesh-resident personal data: there is no resident DR target, and
> the alternative — replicating resident data to a regional DR site — is a regulated act under
> `NFR-086b`. Writing the requirement is what converts a finding into something a design
> (`PE-007`, `SC-007`) is obliged to answer. It is registered as a **go-live blocker** and
> escalated to `GV-005` RAID.

## 4.15 Policy and regulation requirements *(§9.5.15)*

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-059` | The system shall comply with the Personal Data Protection Act 2026 (Law 63 of 2026) in its physical, network and hosting arrangements as well as in software. | **P0** | Inspection |
| `SYR-060` | The system shall comply with the Cyber Security Ordinance 2025 and the ICT Act 2006. | **P0** | Inspection |
| `SYR-061` | The system shall maintain the evidence required for ISO 9001:2015 certification of the service operation, including the documented information required by clause 4.4.2. | **P0** | Inspection |
| `SYR-062` | The system shall comply with Bangladesh e-waste and environmental handling rules for every device, battery and component it takes into custody or retires. | P1 | Inspection |
| `SYR-063` | The system shall comply with the Bangladesh Labour Act 2006 as amended in its working-time, attendance and roster arrangements. | **P0** | Inspection |

## 4.16 System life-cycle sustainment requirements *(§9.5.16)*

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-064` | The system shall maintain a spares holding for every hardware class in `SYR-047` sufficient to replace a failed unit at any site within the interval defined in `SV-002`. | P1 | Inspection |
| `SYR-065` | The system shall define a refresh cycle for field devices and branch peripherals, and shall record each unit's in-service date and expected replacement date. | P2 | Inspection |
| `SYR-066` | The system shall support the software supply chain for 36 months of programme delivery plus the support period in `CO-003`, including a defined response to end-of-support of any bundled open-source component. | **P0** | Analysis |
| `SYR-067` | The system shall retain, for every device it retires, the evidence of data sanitisation required by `M06`. | **P0** | Inspection |

## 4.17 Packaging, handling, shipping and transportation *(§9.5.17)*

| ID | Requirement | Pri | Verif. |
|---|---|:--:|:--:|
| `SYR-068` | The system shall package a customer-owned device in custody such that its condition at handover is evidenced by photographic record at both ends of every movement. | **P0** | Demonstration |
| `SYR-069` | The system shall control the movement of restricted items — lithium batteries in particular — in accordance with the applicable carriage rules, and shall block a consignment that breaches them. | **P0** | Test |
| `SYR-070` | The system shall record declared value and applied insurance for every consignment carrying customer property. | P1 | Inspection |
| `SYR-071` | The system shall deliver, install and commission branch hardware at each site not less than 2 weeks before that site's go-live. | P1 | Inspection |

## 4.18 Verification *(§9.5.18)*

Methods are the four defined in `RQ-001` §3.19.1 — Inspection, Analysis, Demonstration, Test —
allocated one per requirement under rules `VM-01`–`VM-06`. Two verification events are specific
to this document:

| # | Event | Covers | When |
|---|---|---|---|
| SV-01 | **Site readiness assessment** | `SYR-046`–`SYR-055`, `SYR-056`, `SYR-071` | T−4 weeks per site, per `06-01` §6 |
| SV-02 | **Field condition trial** | `SYR-011`–`SYR-017`, `SYR-039`, `SYR-040`, `SYR-051`–`SYR-053` | Before Wave 2 mobile release, in monsoon and dry conditions |

**Count check, regenerated before issue (`PG-M10`):** `SYR-001` … `SYR-071` — 71 identifiers
allocated, 71 requirement rows present across §4.5–§4.17, no gaps, no duplicates.

## 4.19 Assumptions and dependencies *(§9.5.19)*

| # | Assumption or dependency | If it fails |
|---|---|---|
| SA-01 | A lawful Bangladesh-resident DR target can be obtained | `SYR-044` fails; go-live for any module holding resident data is blocked |
| SA-02 | Failover connectivity is procurable at every one of the 51+ sites | `SYR-021` fails at the affected sites; those sites operate permanently in offline-tolerant mode |
| SA-03 | A single approved model per peripheral class is available nationally for the programme duration | `SYR-047` degrades to a multi-model estate with per-model test burden |
| SA-04 | Sites can be assessed 4 weeks ahead of go-live | `SYR-055` becomes a post-hoc record rather than a gate |
| SA-05 | Bengali renders correctly on the selected thermal printers | `SYR-031` fails and every counter document is non-compliant |
| SD-01 | `PE-001`, `PE-002`, `PE-007` design against these requirements | The requirements have no realisation |
| SD-02 | `CO-006` procures against `SYR-039`, `SYR-046`–`SYR-050` | Procurement buys to price rather than to specification |

---

# 5. Decisions Recorded

| # | Decision | Options | Chosen | Rationale |
|---|---|---|---|---|
| D-01 | Whether system requirements belong in the SRS | (a) One combined document; (b) separate SyRS | **(b)** | 29148 separates §9.5 from §9.6 precisely because the audiences and the owners differ. Procurement cannot buy from an SRS |
| D-02 | Whether to state `SYR-044` knowing it is unsatisfiable today | (a) Omit until a lawful target exists; (b) state it | **(b)** | A requirement is how a finding becomes an obligation. Omitting it leaves `OP-01` as an audit note with no owner |
| D-03 | Single approved peripheral model vs per-site procurement | (a) Per-site; (b) single model with exception procedure | **(b)** | Test surface scales with model count, and no test budget covers 51 variants |
| D-04 | Offline tolerance as an app feature or a system property | (a) App feature; (b) system property | **(b)** | It constrains device, storage, battery, sync and reconciliation — four of which are not software |

---

# 6. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Where is the lawful resident DR target, and at what cost? | CTO | **Now** | `SYR-044`, `SYR-045`, every go-live holding resident data |
| Q-02 | Is failover connectivity available at all 51+ sites, and at which are they carrier-diverse in name only? | Platform Lead | W1 | `SYR-021` |
| Q-03 | What are the per-technician data volume budget and the tariff assumption behind it? | Ops Director | W2 | `SYR-017` |
| Q-04 | Which biometric modality is used, and does it create sensitive personal data requiring a specific consent under `SWR-019`? | DPO | W1 | `SYR-006`, `SYR-033` |
| Q-05 | What ingress and drop rating is actually being procured for field devices? | Procurement | W1 | `SYR-040` |
| Q-06 | Does the approved thermal printer render Bengali conjuncts correctly at 203 dpi? | Ops Director | W1 | `SYR-031`, `SYR-050` |

---

# 7. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | All nineteen §9.5 clauses present and populated | §4.1–§4.19 clause map |
| AC-02 | Every `SYR` uses the §5.2.4 construct and passes the §5.2.7 language check | Check run at issue |
| AC-03 | Every `SYR` carries a priority and exactly one verification method | §4 tables |
| AC-04 | The `SYR` space was swept for collisions before allocation | Sweep 02:15 (+06) |
| AC-05 | Every requirement discharged by software names the `SWR` or module that discharges it | §4.5, §4.8 |
| AC-06 | The identifier count reconciles to the row count | §4.18 count check |
| AC-07 | Unsatisfiable requirements are stated, not omitted, and escalated to RAID | `SYR-044`, Q-01 |

---

# 8. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-001` §3.7 | Software limitations that this system must accommodate |
| Upstream | `05-06` §10 | Device and environment capability table, converted here into obligations |
| Upstream | `06-01` §6 | Rollout geography and the T−4 site pattern realised as `SYR-055` |
| Downstream | `PE-001`, `PE-002`, `PE-005`, `PE-007`, `PE-008` | Infrastructure designs satisfying §4.8–§4.14 |
| Downstream | `SC-007` | Residency design satisfying `SYR-041`–`SYR-044` |
| Downstream | `CO-006` | Procurement plan buying against §4.11 |
| Downstream | `RL-004` | Branch rollout plan consuming `SYR-055` |
| Downstream | `SV-002`, `SV-004` | Service levels and paging satisfying `SYR-029`, `SYR-064` |
| Downstream | `QA-006` | Performance test plan verifying `SYR-014`–`SYR-019` |
| Lateral | `RQ-006` | Software quality attributes; `NFR-006`, `NFR-007`, `NFR-045` are cited, not restated |

---

# 9. References

**Within this repository**
[`RQ-001`](RQ-001_Software_Requirements_Specification.md) ·
[`RQ-004`](RQ-004_Requirements_Traceability_Matrix.md) ·
[`RQ-005`](RQ-005_Requirements_Management_Plan.md) ·
[`RQ-006`](RQ-006_Non_Functional_Requirements_Specification.md) ·
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md)

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06` §2, §6.4, §9, §10 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` §6 ·
`../../1000fix_ERP_Module/02_Architecture/02-05` §8 ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §6

**External standards**

| Reference | Verified on |
|---|---|
| ISO/IEC/IEEE 29148:2018 §9.5 | 2026-08-18 |
| ISO/IEC/IEEE 15288:2023 | 2026-08-18 |
| Personal Data Protection Act 2026 (Law 63 of 2026) | 2026-08-12 |
| Cyber Security Ordinance 2025 | 2026-08-12 |
| Bangladesh Labour Act 2006 (as amended) | 2026-08-12 |
| ISO 9001:2015 clause 4.4.2 | 2026-08-18 |

---

# 10. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. `SYR-001`…`SYR-071` specified across all nineteen §9.5 clauses; `SYR-044` raised as an unsatisfiable go-live blocker | *Pending — `GV-002`* |

---

*`RQ-002` · Category 01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
