---
id: FIX-ERP2-011
title: Feature & Function Register
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Feature & Function Register
# ~2,352 Functional Requirements Across 67 Modules

> **Revision 2.1 — audit findings C-01, C-02, C-03, H-02.** This register previously covered
> 30 modules and stated a total of 1,180 requirements. It now covers the 67-module
> architecture. Category A figures are **measured** from completed specifications; Categories
> B–K are **estimated** pending their module files and must not be used for contractual
> commitment (rule RG-05).
>
> Three corrections were applied:
> - **M31 `WSR`** was registered — it previously had no identifier allocation (finding C-02)
> - **M04** retains its permanent code **`FRD`**; the code `BFO` used briefly in drafting is
>   retired and will never be reissued (finding C-03)
> - Totals restated with the provisional marking (finding H-02)

> Documents 05–09 carry the **primary requirement tables** for each module. This document
> holds the **register structure**, the **ID allocation**, the **requirement blocks deferred
> from Documents 05–09**, and the **traceability** back to the v1.0 baseline.

---

## 1. Register Structure

### 1.1 Identifier Format

```
FR-<MOD>-nnn        Functional requirement
FN-<MOD>-nnn.m      Function — a discrete system behaviour within a feature
```

A **feature** is what a user recognises ("estimate approval loop").
A **function** is what the system does to deliver it ("send quotation on channel X",
"start expiry timer", "auto-cancel on expiry"). Functions are numbered as decimal
extensions of their parent requirement and are elaborated during sprint analysis.

### 1.2 Requirement Attributes

Every requirement in the register carries:

| Attribute | Description |
|---|---|
| `id` | FR-<MOD>-nnn |
| `module` | M01–M30 |
| `title` | Short feature name |
| `statement` | "The system shall…" |
| `priority` | P0 / P1 / P2 / P3 |
| `wave` | W1–W9 |
| `layer` | L1–L6 |
| `source` | v1.0 requirement ID, business-plan section, SOW section, or IMPL doc |
| `roles` | Roles that exercise it |
| `acceptance` | Testable acceptance criterion |
| `depends_on` | Other requirement IDs |
| `status` | Proposed / Approved / Built / Verified / Deferred / Superseded |

### 1.3 ID Allocation

| Module | Code | Range | Allocated | Reserved For Growth |
|---|---|---|---:|---|
| M01 | SRM | FR-SRM-001 … 088 | 88 | 089–140 |
| **M31** | **WSR** | **FR-WSR-001 … 058** | **58** | **059–090** |
| M02 | FSM | FR-FSM-001 … 074 | 74 | 075–110 |
| M03 | LOG | FR-LOG-001 … 042 | 42 | 043–070 |
| M04 | FRD | FR-FRD-001 … 032 | 32 | 033–060 |
| M05 | RMS | FR-RMS-001 … 061 | 61 | 062–100 |
| M06 | DTS | FR-DTS-001 … 034 *(plus 020a–020c)* | 34 | 035–060 |
| M07 | CRM | FR-CRM-001 … 055 | 55 | 056–080 |
| M08 | CTR | FR-CTR-001 … 052 | 52 | 053–075 |
| M09 | WTY | FR-WTY-001 … 048 | 48 | 049–070 |
| M10 | LOY | FR-LOY-001 … 041 | 41 | 042–060 |
| M11 | SLS | FR-SLS-001 … 046 | 46 | 047–070 |
| M12 | ECM | FR-ECM-001 … 079 | 79 | 080–110 |
| M13 | RNT | FR-RNT-001 … 044 | 44 | 045–060 |
| M14 | TRF | FR-TRF-001 … 039 | 39 | 040–060 |
| M15 | INV | FR-INV-001 … 063 | 63 | 064–090 |
| M16 | SCM | FR-SCM-001 … 040 | 40 | 041–060 |
| M17 | AST | FR-AST-001 … 042 | 42 | 043–065 |
| M18 | ESG | FR-ESG-001 … 026 | 26 | 027–040 |
| M19 | FIN | FR-FIN-001 … 068 | 68 | 069–100 |
| M20 | BIL | FR-BIL-001 … 051 | 51 | 052–075 |
| M21 | HRM | FR-HRM-001 … 052 | 52 | 053–075 |
| M22 | LMS | FR-LMS-001 … 030 | 30 | 031–045 |
| M23 | QMS | FR-QMS-001 … 037 | 37 | 038–055 |
| M24 | DMS | FR-DMS-001 … 030 | 30 | 031–045 |
| M25 | BID | FR-BID-001 … 045 | 45 | 046–065 |
| M26 | AIM | FR-AIM-001 … 038 | 38 | 039–055 |
| M27 | CCE | FR-CCE-001 … 047 | 47 | 048–070 |
| M28 | IPF | FR-IPF-001 … 058 | 58 | 059–080 |
| M29 | SEC | FR-SEC-001 … 044 | 44 | 045–065 |
| M30 | ADM | FR-ADM-001 … 035 | 35 | 036–050 |
| Portals | P01–P12 | FR-POR-001 … 140 | 140 | 141–180 |
| | | | **1,180** *(30-module basis — superseded)* | |

### 1.3a Restated Allocation — 67 Modules

> Ranges for M07–M30 and M32–M67 are allocated as each category's specifications are written,
> under register rule **RG-01** (register-first). Until then, the figures below are estimates.

| Category | Modules | Requirements | Basis |
|---|---:|---:|---|
| **A — Service Delivery & Operations** | 7 | **388** | **Measured** — all 7 specifications complete |
| B — Customer Engagement & Experience | 7 | 243 | Estimated |
| C — Commercial, Pricing & Revenue | 9 | 356 | Estimated |
| D — Circular & Asset-Based Business | 3 | 109 | Estimated |
| E — Supply Chain & Inventory | 6 | 192 | Estimated |
| F — Asset, Equipment & Facilities | 5 | 134 | Estimated |
| G — Finance & Treasury | 8 | 258 | Estimated |
| H — People & Workforce | 7 | 204 | Estimated |
| I — Governance, Risk, Quality & Knowledge | 4 | 118 | Estimated |
| J — Data, Analytics & Intelligence | 4 | 130 | Estimated |
| K — Platform & Technology | 7 | 220 | Estimated |
| **Total** | **67** | **~2,352** | 7 of 67 measured |

**Category A measured breakdown**

| Module | Code | Range | Count |
|---|---|---|---:|
| M01 | `SRM` | FR-SRM-001 … 088 | 88 |
| M31 | `WSR` | FR-WSR-001 … 058 | 58 |
| M02 | `FSM` | FR-FSM-001 … 074 | 74 |
| M03 | `LOG` | FR-LOG-001 … 042 | 42 |
| M04 | `FRD` | FR-FRD-001 … 032 | 32 |
| M05 | `RMS` | FR-RMS-001 … 061 | 61 |
| M06 | `DTS` | FR-DTS-001 … 034 | 34 |
| | | **Total** | **388** |

### 1.3c Category B Allocation — reserved under rule RG-01

| Module | Code | Range | Count | Reserved for Growth |
|---|---|---|---:|---|
| M33 | `CPM` | FR-CPM-001 … 052 | 52 | 053–090 |
| M07 | `CRM` | FR-CRM-001 … 046 | 46 | 047–080 |
| M10 | `LOY` | FR-LOY-001 … 044 | 44 | 045–070 |
| M27 | `CCE` | FR-CCE-001 … 058 | 58 | 059–095 |
| M32 | `CAI` | FR-CAI-001 … 038 | 38 | 039–065 |
| M34 | `CXM` | FR-CXM-001 … 042 | 42 | 043–070 |
| M35 | `MKT` | FR-MKT-001 … 040 | 40 | 041–070 |
| | | **Total** | **320** | |

> **Variance note.** The register estimate for Category B was 243 requirements. The measured
> figure is **320** — an under-estimate of 32%, consistent with the 23% under-estimate
> observed in Category A. The estimation correction factor applied to Categories C–K should be
> revised upward from 23% to **30%** (audit finding H-02).

### 1.3d Category H Allocation — reserved under rule RG-01

| Module | Code | Range | Count | Reserved for Growth |
|---|---|---|---:|---|
| M21 | `HCM` | FR-HCM-001 … 046 | 46 | 047–080 |
| M55 | `WFM` | FR-WFM-001 … 052 | 52 | 053–090 |
| M56 | `PAY` | FR-PAY-001 … 054 | 54 | 055–090 |
| M57 | `PIC` | FR-PIC-001 … 042 | 42 | 043–070 |
| M22 | `LMS` | FR-LMS-001 … 040 | 40 | 041–070 |
| M58 | `TAO` | FR-TAO-001 … 034 | 34 | 035–060 |
| M59 | `HSE` | FR-HSE-001 … 042 | 42 | 043–070 |
| | | **Total** | **310** | |

> **Variance note.** The register estimate for Category H was 204 requirements. The measured
> figure is **310** — an under-estimate of 52%, the largest so far (A: +23%, B: +32%). The
> cause is statutory density: Bangladesh Labour Act, NBR tax, provident fund, gratuity and
> ISO 45001 obligations generate requirements that a generic HCM estimate does not anticipate.
> **The correction factor for the remaining categories should be reviewed again** — see
> `02-02` §3.

### 1.3b Retired Identifier Prefixes

| Prefix | History |
|---|---|
| `FR-BFO-` | **Retired.** Used briefly for M04 during drafting before the permanent `FR-FRD-` allocation was applied. Never issued to a build ticket, never to be reissued. *(Audit finding C-03.)* |

---

## 2. Distribution

### 2.1 By Priority

| Priority | Count | % | Definition |
|---|---:|---:|---|
| P0 | 268 | 22.7% | Regulatory, safety or go-live blocking |
| P1 | 512 | 43.4% | Core business capability |
| P2 | 316 | 26.8% | Important, deferrable one wave |
| P3 | 84 | 7.1% | Desirable, opportunistic |

### 2.2 By Wave

| Wave | Count | Cumulative |
|---|---:|---:|
| W1 | 142 | 142 |
| W2 | 178 | 320 |
| W3 | 156 | 476 |
| W4 | 189 | 665 |
| W5 | 148 | 813 |
| W6 | 134 | 947 |
| W7 | 121 | 1,068 |
| W8 | 79 | 1,147 |
| W9 | 33 | 1,180 |

### 2.3 By Delivery Layer

| Layer | Count | % |
|---|---:|---:|
| L1 — Odoo 19 CE native | 330 | 28.0% |
| L2 — OCA modules | 283 | 24.0% |
| L3 — Free third-party modules | 47 | 4.0% |
| L4 — Standalone open source | 201 | 17.0% |
| L5 — Custom development | 295 | 25.0% |
| L6 — Commercial SaaS | 24 | 2.0% |

---

# 3. Requirement Blocks Deferred From Documents 05–09

The module specifications enumerate the primary requirements and note that certain ranges are
"catalogued in Doc 11". Those ranges are set out below.

## 3.1 M01 SRM — FR-SRM-063 … FR-SRM-088 (Business-Line Extensions)

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SRM-063 | Rental service intake | Create a service order for a rental asset with the contract, deposit and liability context carried in | P2 |
| FR-SRM-064 | Rental swap-out | Convert an irreparable rental fault into an asset swap with logistics and agreement update | P2 |
| FR-SRM-065 | Data-service intake | Create a data-services case as a specialised service order with confidentiality controls applied at creation | P2 |
| FR-SRM-066 | Refurbishment intake | Create a refurbishment work order from a trade-in, an unrepairable job or a rental retirement | P2 |
| FR-SRM-067 | Recycling intake | Create a collection record for an end-of-life device with disposition triage | P3 |
| FR-SRM-068 | Marketplace job creation | Create a service order from a marketplace transaction with the seller as the executing party | P1 |
| FR-SRM-069 | MSP-generated work | Create a service order from a managed-services alert, ticket or scheduled task | P1 |
| FR-SRM-070 | Contract-generated work | Create scheduled preventive work orders from contract maintenance plans | P1 |
| FR-SRM-071 | Warranty-claim-driven rework | Create rework orders arising from a brand-rejected claim requiring re-inspection | P1 |
| FR-SRM-072 | Bulk corporate site visit | Plan a single visit covering many devices at one site, with per-device outcomes | P1 |
| FR-SRM-073 | Recall campaign handling | Execute a brand recall campaign as a batch of service orders against affected serials | P2 |
| FR-SRM-074 | Insurance-funded repair | Handle repairs funded by a third-party insurer with assessment, approval and direct billing | P3 |
| FR-SRM-075 | Goodwill repair | Record a repair performed at no charge with cost attribution and approval | P2 |
| FR-SRM-076 | Loan device management | Issue and track a loan device to a customer while their device is in repair | P2 |
| FR-SRM-077 | Multi-fault handling | Handle multiple independent faults on one device with separate estimates and approvals | P2 |
| FR-SRM-078 | Job cost roll-up | Roll up all costs (labour, parts, logistics, sub-contract, overhead) per service order for margin analysis | P1 |
| FR-SRM-079 | Service order templates | Apply templates that pre-populate scope, checklist, parts and time for common jobs | P2 |
| FR-SRM-080 | Priority override | Allow authorised roles to override calculated priority with a logged reason | P1 |
| FR-SRM-081 | Customer-preferred technician | Honour a customer's request for a specific technician where feasible | P3 |
| FR-SRM-082 | Repeat-visit linkage | Link all visits belonging to one customer problem into a single case view | P1 |
| FR-SRM-083 | Device photo library | Maintain the full photo history for a device across all its service events | P2 |
| FR-SRM-084 | Service order search | Search service orders by any attribute, including free-text and Bengali content | P1 |
| FR-SRM-085 | Saved views & filters | Let users save and share list views and filters | P2 |
| FR-SRM-086 | Bulk operations | Perform bulk state changes, assignments and notifications with preview and confirmation | P1 |
| FR-SRM-087 | Service order archival | Archive closed orders older than the operational window while keeping them retrievable | P2 |
| FR-SRM-088 | Legacy order lookup | Look up migrated historical service records with their original references | P1 |

## 3.2 M02 FSM — FR-FSM-041 … FR-FSM-074

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FSM-041 | Van stock par levels | Define per-technician par levels by part, based on their skill profile and job mix | P1 |
| FR-FSM-042 | Van stock visibility in dispatch | Consider van stock when scoring candidate technicians for a job | P1 |
| FR-FSM-043 | Field parts transfer | Transfer a part directly between two technicians in the field with scanning | P2 |
| FR-FSM-044 | Technician performance instrumentation | Capture every measurable event needed for scorecards and incentives | P1 |
| FR-FSM-045 | Dispatcher productivity tools | Provide bulk assign, filter presets, keyboard shortcuts and undo | P1 |
| FR-FSM-046 | Assignment explanation | Show the dispatcher why a technician was recommended, in plain language | P1 |
| FR-FSM-047 | Manual override logging | Record every override of an automatic assignment with reason, feeding model improvement | P1 |
| FR-FSM-048 | Site visit planning | Plan multi-device corporate site visits with duration estimation and crew composition | P1 |
| FR-FSM-049 | External engineer dispatch | Dispatch to a marketplace seller with commercial terms, quality obligations and tracking | P2 |
| FR-FSM-050 | Sub-contractor dispatch | Dispatch to a contracted sub-contractor with PO linkage | P2 |
| FR-FSM-051 | Appointment reminders | Remind the customer at booking, day-before and on-the-day with reschedule options | P1 |
| FR-FSM-052 | Slot capacity management | Manage bookable capacity by branch, skill and slot, preventing overbooking | P1 |
| FR-FSM-053 | Working-hours and overtime awareness | Prevent scheduling that would breach working-time rules without approval | P1 |
| FR-FSM-054 | Technician preferences | Record technician constraints (vehicle, licence, physical, geographic) affecting assignment | P2 |
| FR-FSM-055 | Standby & emergency rota | Manage the after-hours rota and dispatch from it | P1 |
| FR-FSM-056 | Field cash reconciliation | Reconcile cash collected in the field daily against jobs and deposits | P1 |
| FR-FSM-057 | Technician expense capture | Capture travel and incidental expenses in the field for reimbursement | P2 |
| FR-FSM-058 | Vehicle assignment | Assign vehicles to technicians and record usage, fuel and issues | P2 |
| FR-FSM-059 | Field incident reporting | Report accidents, hazards, abuse or security incidents from the field | P2 |
| FR-FSM-060 | Photo quality validation | Reject blurred, dark or duplicate evidence photos at capture time | P2 |
| FR-FSM-061 | Data-usage optimisation | Compress and defer non-critical uploads to reduce technician data cost | P1 |
| FR-FSM-062 | Battery and background optimisation | Manage location and sync frequency to preserve device battery | P1 |
| FR-FSM-063 | App update management | Deliver forced and optional app updates with version compatibility enforcement | P1 |
| FR-FSM-064 | Device enrolment | Register technician devices and revoke access on loss or exit | P1 |
| FR-FSM-065 | Dispatch simulation | Simulate the effect of a scheduling decision before committing it | P3 |
| FR-FSM-066 | Historical route replay | Replay a technician's actual route and events for investigation | P2 |
| FR-FSM-067 | SLA-aware sequencing | Sequence a route so SLA-critical jobs are protected even at travel cost | P1 |
| FR-FSM-068 | Zone rebalancing | Recommend zone or roster changes where demand and capacity are mismatched | P2 |
| FR-FSM-069 | Technician availability self-service | Let technicians declare availability and request schedule changes | P2 |
| FR-FSM-070 | Job handover between technicians | Hand over an in-progress job with full context and custody | P2 |
| FR-FSM-071 | Customer rescheduling | Let the customer reschedule from the tracking link within policy | P1 |
| FR-FSM-072 | No-access photo evidence | Capture geotagged evidence when access is refused or the customer is absent | P1 |
| FR-FSM-073 | Dispatch analytics | Report assignment quality, override rate, travel efficiency and capacity utilisation | P1 |
| FR-FSM-074 | Dispatch API | Expose dispatch operations to portals and external systems | P1 |

## 3.3 M03 LOG — FR-LOG-027 … FR-LOG-042

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOG-027 | Rider mobile application | Provide the full rider workflow offline with queued sync | P1 |
| FR-LOG-028 | Hub operations | Manage sorting, staging and dispatch at logistics hubs | P2 |
| FR-LOG-029 | Load planning | Plan rider loads by weight, volume and value limits | P2 |
| FR-LOG-030 | Cash on delivery | Collect and reconcile cash on delivery per rider per shift | P1 |
| FR-LOG-031 | Insurance & declared value | Record declared value and apply insurance where taken | P2 |
| FR-LOG-032 | Loss & damage claims | Manage claims for lost or damaged consignments through to settlement | P1 |
| FR-LOG-033 | Customer rescheduling | Let customers reschedule a collection or delivery from the tracking link | P1 |
| FR-LOG-034 | Delivery windows | Offer and honour committed delivery windows | P1 |
| FR-LOG-035 | Address validation & geocoding | Validate and geocode addresses, learning from previous successful deliveries | P1 |
| FR-LOG-036 | Recipient authorisation | Allow a customer to nominate an alternative recipient with verification | P2 |
| FR-LOG-037 | Restricted items | Flag and control movement of batteries and other restricted items | P1 |
| FR-LOG-038 | Consolidated movements | Consolidate multiple items travelling the same route into one movement | P2 |
| FR-LOG-039 | Inter-branch scheduled runs | Operate scheduled shuttle runs between branches and hubs | P2 |
| FR-LOG-040 | Logistics cost allocation | Allocate logistics cost to the job, contract or business line that caused it | P1 |
| FR-LOG-041 | Carrier performance | Score internal riders and external couriers on cost, time and quality | P1 |
| FR-LOG-042 | Logistics analytics | Report volume, cost per consignment, on-time performance and exception causes | P1 |

## 3.4 M04 FRD — FR-FRD-025 … FR-FRD-031

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FRD-025 | Self-service kiosk | Provide a kiosk for token issue, status check and appointment check-in | P2 |
| FR-FRD-026 | Receipt & label printing | Print receipts, job sheets, device labels and gate passes from the counter | P1 |
| FR-FRD-027 | Multi-counter configuration | Configure counters per branch with capability and staffing | P2 |
| FR-FRD-028 | Counter performance analytics | Report throughput, handling time and queue metrics per counter and agent | P2 |
| FR-FRD-029 | Customer feedback at counter | Capture a quick satisfaction rating at handover | P2 |
| FR-FRD-030 | Branch notice board | Publish branch-level announcements and targets to counter staff | P3 |
| FR-FRD-031 | Emergency procedures | Provide quick access to emergency and escalation procedures | P3 |

## 3.5 M05 RMS — FR-RMS-039 … FR-RMS-061

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RMS-039 | Backup service oversight | Monitor client backup jobs, report failures and drive remediation | P2 |
| FR-RMS-040 | Cloud subscription management | Track client cloud subscriptions, licences, usage and renewal | P2 |
| FR-RMS-041 | Cloud cost reporting | Report client cloud spend and optimisation recommendations | P3 |
| FR-RMS-042 | DR/BC plan register | Maintain client disaster-recovery and continuity plans | P2 |
| FR-RMS-043 | DR test tracking | Schedule, execute and evidence DR tests with results reporting | P2 |
| FR-RMS-044 | Security posture reporting | Report client endpoint protection, patch and vulnerability posture | P2 |
| FR-RMS-045 | IT strategy deliverables | Track consulting deliverables, roadmaps and recommendations per client | P3 |
| FR-RMS-046 | Technology roadmap | Maintain a per-client technology roadmap with refresh recommendations | P3 |
| FR-RMS-047 | Client onboarding project | Run a structured onboarding project for each new MSP client | P1 |
| FR-RMS-048 | Client offboarding | Run controlled offboarding with agent removal, data return and access revocation | P1 |
| FR-RMS-049 | Client contact management | Maintain authorised contacts, their permissions and escalation preferences | P1 |
| FR-RMS-050 | Client self-service portal scope | Define exactly what each client may see and do in P04 | P1 |
| FR-RMS-051 | Asset discovery | Discover assets on the client network and reconcile against the registered estate | P2 |
| FR-RMS-052 | Licence compliance | Report software licence compliance across the client estate | P3 |
| FR-RMS-053 | Warranty tracking of client assets | Track manufacturer warranty across the client estate and alert on expiry | P2 |
| FR-RMS-054 | Automation library | Maintain reusable automation scripts with approval and execution audit | P2 |
| FR-RMS-055 | Scheduled tasks | Run scheduled maintenance tasks on client assets with evidence | P2 |
| FR-RMS-056 | Agent health | Monitor and remediate monitoring-agent health and coverage gaps | P1 |
| FR-RMS-057 | Alert noise reduction | Tune, suppress and correlate alerts to keep signal-to-noise usable | P1 |
| FR-RMS-058 | Client CSAT | Measure satisfaction per ticket and per period for MSP clients | P1 |
| FR-RMS-059 | Profitability per client | Report cost to serve vs contract value per MSP client | P2 |
| FR-RMS-060 | Capacity planning | Forecast MSP team capacity against contracted estate growth | P2 |
| FR-RMS-061 | MSP analytics | Report the full MSP operational and commercial picture | P1 |

## 3.6 M06 DTS — FR-DTS-025 … FR-DTS-034

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-DTS-025 | Cleanroom scheduling | Schedule and log cleanroom usage per case | P3 |
| FR-DTS-026 | Specialist equipment tracking | Track use of specialist recovery equipment and consumables | P3 |
| FR-DTS-027 | Partner lab referral | Refer cases beyond internal capability to a partner lab with custody and commercial terms | P3 |
| FR-DTS-028 | Case prioritisation | Prioritise cases by criticality, contract and customer tier | P2 |
| FR-DTS-029 | Customer communication controls | Restrict what case detail may be communicated and by whom | P1 |
| FR-DTS-030 | Case cost tracking | Track labour, consumables and partner cost per case | P2 |
| FR-DTS-031 | Backup storage provisioning | Provision and track storage allocated per customer backup plan | P2 |
| FR-DTS-032 | Restore request handling | Handle customer restore requests with SLA and verification | P2 |
| FR-DTS-033 | Data-services compliance reporting | Report on custody, access, retention and destruction for audit | P1 |
| FR-DTS-034 | Data-services analytics | Report volume, success rate, turnaround, revenue and margin | P2 |

## 3.7 M07 CRM — FR-CRM-033 … FR-CRM-055

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-CRM-033 | Household grouping | Group family members at one address for RAMC and appliance services | P2 |
| FR-CRM-034 | Corporate contact roles | Define contact roles (approver, requester, finance, technical) with matching permissions | P1 |
| FR-CRM-035 | Approval chain configuration | Configure the client's internal approval chain for requests and spend | P1 |
| FR-CRM-036 | Portal identity linkage | Link a portal login to the correct customer record with verification | P0 |
| FR-CRM-037 | Customer merge audit | Preserve a full audit of every merge with reversal capability | P1 |
| FR-CRM-038 | Data-subject requests | Handle access, correction and erasure requests within legal constraints | P1 |
| FR-CRM-039 | Blacklist & fraud flags | Flag customers for non-payment, abuse or fraud with controlled visibility | P1 |
| FR-CRM-040 | Customer notes | Maintain internal notes with visibility control and audit | P1 |
| FR-CRM-041 | Relationship mapping | Map relationships between customers (group companies, referrers, family) | P2 |
| FR-CRM-042 | Customer documents | Attach and manage customer documents with retention | P1 |
| FR-CRM-043 | Preferred language & channel | Record and honour preferred language and contact channel everywhere | P0 |
| FR-CRM-044 | Do-not-contact | Honour do-not-contact instructions absolutely, including operational messages where lawful | P0 |
| FR-CRM-045 | Customer timeline | Present a chronological timeline of every event in the relationship | P1 |
| FR-CRM-046 | Anniversary & birthday triggers | Trigger appropriate contact on meaningful dates | P3 |
| FR-CRM-047 | Win-back segmentation | Identify and segment lapsed customers for reactivation | P2 |
| FR-CRM-048 | Referral attribution | Attribute a customer to the referrer who introduced them, permanently | P1 |
| FR-CRM-049 | Acquisition source tracking | Record and report acquisition source and cost per customer | P2 |
| FR-CRM-050 | Corporate hierarchy roll-up | Roll up activity, spend and satisfaction across a corporate group | P1 |
| FR-CRM-051 | Account team assignment | Assign account managers and support teams to accounts | P1 |
| FR-CRM-052 | Customer-facing API | Expose customer profile operations to portals securely | P0 |
| FR-CRM-053 | Bulk customer operations | Perform controlled bulk updates with preview and rollback | P1 |
| FR-CRM-054 | Customer data quality dashboard | Report completeness, duplication and staleness of customer data | P1 |
| FR-CRM-055 | CRM analytics | Report acquisition, retention, value, satisfaction and segment performance | P1 |

## 3.8 Remaining Deferred Blocks — Summary

The remaining deferred ranges follow the same pattern and are elaborated in the requirement
management tool at sprint-analysis time. Their scope is:

| Module | Range | Scope of Deferred Requirements |
|---|---|---|
| M08 CTR | 031–052 | Template library, obligation tracking, healthcare calibration schedules, contract portal self-service, bulk contract operations, contract analytics |
| M09 WTY | 033–048 | Brand portal interactions, rate-card management, brand audit packs, warranty product actuarial reporting, recall handling, claim analytics |
| M10 LOY | 031–041 | In-app ad placement, gamification, anniversary triggers, win-back journeys, loyalty cost accounting, loyalty analytics |
| M11 SLS | 029–046 | Promotion integration, corporate tender/RFP response, rental tariff structures, refurbished grade pricing, competitor price tracking, pricing analytics |
| M12 ECM | 054–079 | Seller mobile experience, bulk listing management, seller promotions, search ranking, seller analytics, international seller and customer handling, marketplace tax reporting |
| M13 RNT | 030–044 | Rental portal self-service, rental insurance products, subscription rental, fleet purchasing, rental analytics |
| M14 TRF | 031–039 | Trade-in mobile experience, market price feeds, donation programme, refurbishment analytics |
| M15 INV | 047–063 | Warehouse mobile operations, put-away strategy, bin optimisation, hazardous-material handling, import tracking, inventory analytics |
| M16 SCM | 028–040 | Budget control, catalogue punch-out, blanket orders, supplier collaboration, procurement analytics |
| M17 AST | 037–042 | Asset search and analytics, asset APIs for portals, asset data-quality management |
| M18 ESG | 022–026 | Donation programme, refrigerant recovery logs, supplier ESG assessment |
| M19 FIN | 053–068 | Inter-company reconciliation, consolidation, audit support, financial controls testing, treasury, financial analytics |
| M20 BIL | 037–051 | Advertising billing, deposit accounting, prepaid packages, billing analytics, revenue assurance controls |
| M21 HRM | 039–052 | Recruitment, disciplinary records, health and safety, workforce analytics, HR compliance reporting |
| M22 LMS | 025–030 | Training cost tracking, external providers, effectiveness measurement, learning analytics |
| M23 QMS | 036–037 | Business-continuity planning, quality analytics |
| M24 DMS | 026–030 | Portal document sharing, customer document access, document analytics |
| M25 BID | 033–045 | Feature store for M26, embedded analytics APIs, warehouse cost management, BI adoption analytics |
| M26 AIM | 025–038 | Per-model implementation detail, evaluation harnesses, labelled-data collection, ML operations runbook |
| M27 CCE | 044–047 | Video support calls, social listening, contact-centre integration with complaint handling |
| M28 IPF | 035–058 | Full external integration implementations, sandbox environments, partner onboarding, API analytics |
| M29 SEC | 041–044 | Security awareness training linkage, third-party security assessment, security metrics dashboard |

---

# 4. Portal Requirements — FR-POR-001 … FR-POR-140

Portal requirements are those that belong to the *surface* rather than a module: navigation,
layout, offline behaviour, accessibility, performance and portal-specific composition. They
are allocated as follows.

| Portal | Range | Count |
|---|---|---:|
| P01 Customer | FR-POR-001 … 026 | 26 |
| P02 Technician | FR-POR-027 … 048 | 22 |
| P03 Admin | FR-POR-049 … 066 | 18 |
| P04 Corporate B2B | FR-POR-067 … 082 | 16 |
| P05 Vendor | FR-POR-083 … 091 | 9 |
| P06 Analytics | FR-POR-092 … 098 | 7 |
| P07 Marketplace Seller | FR-POR-099 … 114 | 16 |
| P08 Brand Partner | FR-POR-115 … 121 | 7 |
| P09 Logistics & Rider | FR-POR-122 … 129 | 8 |
| P10 Contact Centre | FR-POR-130 … 135 | 6 |
| P11 Field Auditor | FR-POR-136 … 138 | 3 |
| P12 Partner & Referral | FR-POR-139 … 140 | 2 |

### Cross-Portal Requirements (applied to every portal)

| FR ID | Requirement | Pri |
|---|---|:--:|
| FR-POR-X01 | Every portal authenticates through the central identity provider with no local credential store | P0 |
| FR-POR-X02 | Every portal calls the ERP only through the API gateway with a portal-specific credential | P0 |
| FR-POR-X03 | Every portal supports Bengali and English with the correct default per audience | P0 |
| FR-POR-X04 | Every web portal meets WCAG 2.1 AA | P1 |
| FR-POR-X05 | Every web portal is responsive from 320 px with no horizontal scrolling | P1 |
| FR-POR-X06 | Every portal uses the shared 1000FiX design system | P1 |
| FR-POR-X07 | Every portal instruments its critical funnels and reports to M25 | P1 |
| FR-POR-X08 | Every portal error message states what happened and what to do next, in the user's language | P1 |
| FR-POR-X09 | No portal implements a business rule; client validation is for convenience only | P0 |
| FR-POR-X10 | Every portal honours the session, timeout and MFA policy defined centrally | P0 |

---

# 5. Traceability to the v1.0 Baseline

## 5.1 v1.0 Requirement Mapping

| v1.0 Source | v1.0 IDs | v2.0 Location | Status |
|---|---|---|---|
| BRD §8.1 Service & Repair | BR-SRM-001…020 | FR-SRM-001…020 | Retained |
| BRD §8.2 Field Service | BR-FSM-001…017 | FR-FSM-001…017, FR-LOG-001…005 | Retained, partly relocated |
| BRD §8.3 Inventory | BR-INV-001…015 | FR-INV-001…015 | Retained |
| BRD §8.4 CRM | BR-CRM-001…010 | FR-CRM-001…010 | Retained |
| BRD §8.5 Financial | BR-FIN-001…015 | FR-FIN-001…015, FR-BIL-001…010 | Retained, partly relocated |
| BRD §8.6 HR & Payroll | BR-HRM-001…012 | FR-HRM-001…012, FR-LMS-012…016 | Retained, partly relocated |
| BRD §8.7 Contract & Warranty | BR-CWM-001…012 | FR-CTR-001…012, FR-WTY-001…012 | Retained, split |
| BRD §8.8 Procurement | BR-SCM-001…007 | FR-SCM-001…007 | Retained |
| BRD §8.9 BI | BR-BI-001…010 | FR-BID-001…010 | Retained |
| BRD §8.10 Document Mgmt | BR-DMS-001…005 | FR-DMS-001…005 | Retained |
| BRD §8.11 Quality | BR-QMS-001…005 | FR-QMS-001…005 | Retained |
| BRD §9 Non-Functional | NFR-001…030 | NFR-001…030 in Doc 16 | Retained |
| BRD §10 Business Rules | BRU-* | BRU-* in Doc 15 | Retained |
| RFP §5–§10 | 405 requirements | Distributed across FR-* | All mapped |
| URD §6–§10 User Stories | US-* | Mapped to FR-* acceptance criteria | All mapped |
| Tech Stack §7 Custom Modules | CD-01…20 | CD-001…020 in Doc 19 | Retained |

## 5.2 Superseded Requirements

| v1.0 ID | Superseded By | Reason |
|---|---|---|
| INT-022 (Rasa 3.6 chatbot) | FR-CCE-017 … FR-CCE-025 | LLM approach; Rasa OSS in maintenance mode (divergence already recorded in v1.0 Technology Stack Spec §6.10) |
| INT-019 (Google Routes / Timefold) | FR-FSM-012 … FR-FSM-016 | VROOM + OSRM with selective traffic API (divergence already recorded in v1.0 Technology Stack Spec §6.7) |
| BR-BI-007 (drag-and-drop report builder) | FR-BID-018 | Semantic-layer self-service supersedes the point tool |
| BR-DMS-003 (DMS approval workflows) | FR-IPF-020 | One platform-wide workflow engine serves all modules |

**No v1.0 requirement has been deleted.**

---

# 6. Requirement Governance

| Rule | Detail |
|---|---|
| **Ownership** | Every requirement has a named business owner who accepts it at UAT |
| **Immutability of IDs** | An ID is never reused. If a requirement is withdrawn, the ID is retired |
| **Change control** | Adding or changing a P0/P1 requirement requires Steering Committee approval; P2/P3 requires PMO approval |
| **Acceptance criteria** | No requirement enters a sprint without a testable acceptance criterion |
| **Traceability** | Every requirement links to at least one test case and one demo scenario before it can be marked Verified |
| **Coverage reporting** | The PMO reports requirement status by module and wave every fortnight |
| **Deferral discipline** | A deferred requirement moves wave with a recorded reason and a new target; it is never silently dropped |

---

*Next document: `12_Data_Model_and_Entity_Catalog.md`*
