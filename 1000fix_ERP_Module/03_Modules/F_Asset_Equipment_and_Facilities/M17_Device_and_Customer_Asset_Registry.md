---
id: FIX-ERP2-M17
module_id: M17
module_code: AST
module_name: Device & Customer Asset Registry
category: F — Asset, Equipment & Facilities
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Service Operations Director
system_owner: Service Platform Squad
priority: P1
wave: W2
---

# M17 — Device & Customer Asset Registry
### Category F · Code `AST` · Existing (re-scoped in v2.1)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M17 |
| **Module code** | `AST` |
| **Category** | F — Asset, Equipment & Facilities |
| **Status** | Existing (re-scoped in v2.1 — telemetry, health scoring and failure prediction moved to **M48**; tool register and calibration moved to **M45**; brand and model master data confirmed to **M37**) |
| **Priority** | **P1** |
| **Delivery wave** | W2 (Months 5–8), with an identity-core slice in W1 |
| **Business owner** | Service Operations Director |
| **System owner** | Service Platform Squad |
| **Delivery layers** | L1 Odoo `stock.lot` / `repair` foundations · L2 OCA `field-service` equipment models · L4 identity-resolution service · L5 custom registry, estate, genealogy and maintenance-plan engines |
| **Custom modules** | `cd_asset_registry`, `cd_asset_estate`, `cd_maintenance_plan`, `cd_asset_identity`, `cd_asset_genealogy` |
| **Requirement range** | FR-AST-001 … FR-AST-052 |
| **Requirement count** | **52** *(measured — supersedes the 34 estimate in `02-02` and the 42 allocation in `05-01`; within the 001–065 block reserved in `05-01`)* |
| **Effort estimate** | **26 person-weeks** *(measured — supersedes the 18 PW estimate)* |
| **Depends on** | M37 Catalogue · M33 Party Master · M64 MDM · M29 Identity · M30 Platform Admin · M28 Integration · M24 Documents |
| **Depended on by** | M01, M02, M03, M04, M05, M06, M31, M07, M08, M09, M10, M12, M13, M14, M15, M18, M20, M23, M25, M26, M34, M36, M48, M62, M22, M59, M61 |

---

## 2. Purpose

M17 is **the identity layer of the physical world** for 1000FiX. It answers four questions
about every device the Company touches: *what is this thing, whose is it, where has it been,
and what has been done to it?*

Every service transaction in the ERP begins with a device. A service order without a device
identity is a piece of paper. A warranty claim without device identity is rejected. A repeat
fault cannot be detected, a corporate contract cannot be entitled, a part cannot be proven
compatible, and a technician cannot be told what the last engineer found — unless the device
has one permanent, unambiguous identity that outlives every transaction attached to it.

M17 holds that identity. It does not perform service, it does not price it, and it does not
own the telemetry the device emits. It holds the **asset** — permanently, from the moment
1000FiX first sees the device to the moment it is recycled — and it projects onto that asset
everything the rest of the system does to it.

### Why It Exists

The v1.0 BRD treated the device registry as a field on the customer record (BR-CRM-002). That
placement is the single most consequential modelling error in the v1.0 design, and it fails in
four specific ways.

First, **devices outlive customer relationships.** A laptop sold, traded in, refurbished and
resold has three owners and one identity. Storing the device under the customer destroys the
history at the moment of transfer — exactly when it becomes most valuable.

Second, **corporate estates are not a list of devices.** A corporate client with 400 machines
across 6 sites and 12 departments needs an estate structure, and a contract that entitles
*those* assets, not *that customer*. The SOW commitment — *"register all 100 devices with
serial nos."* — is an estate onboarding requirement, not a CRM field.

Third, **warranty revenue depends on device evidence.** 1000FiX is authorised warranty partner
for 17+ brands. A claim is paid on the strength of serial, purchase date, fault, parts fitted
and prior history. Where that evidence is assembled by hand from three systems, claims are
rejected and revenue leaks.

Fourth, **the same device is touched by six modules.** Intake (M04), order (M01), field visit
(M02), workshop (M31), logistics (M03) and data services (M06) all need the same identity. If
each holds its own copy, the Company has six answers to one question.

M17 is P1 and lands in Wave 2 — with an identity-core slice in Wave 1 — because M01 and M04
cannot open a service order without it.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-CRM-002 | "Maintain a device registry per customer: brand, model, serial number, purchase date, warranty expiry, condition" |
| ERP BRD BR-SRM-005 | "Link each service order to a specific customer record and device record (by serial number)" |
| ERP BRD BR-SRM-006 | "Display complete service history for any device when a new service order is created" |
| ERP BRD BR-SRM-016 | "Flag rework cases (same device returning for same issue within 30 days)" — requires device-level history |
| ERP BRD BR-SRM-020 | "Technicians require access to complete device and customer history from the service order on mobile" |
| ERP BRD BR-FSM-016 | "Technicians require device repair history, diagnostic guides and troubleshooting references on mobile" |
| ERP BRD BR-CWM-005 | "Auto-validate warranty status when a service order is created (by serial number + purchase date)" |
| ERP BRD BR-CWM-001 | AMC contracts list "covered devices" — entitlement attaches to assets, not to customers |
| ERP BRD BR-CWM-008 | Warranty claims must carry diagnostic report and parts used — device-level evidence |
| ERP BRD BR-CRM-007 | "Manage corporate/B2B accounts with multiple contacts, multiple locations and bulk service capabilities" |
| ERP BRD BR-INV-009 | Parts catalogue carries "compatibility mapping to device brands and models" — compatibility is resolved against the asset's model |
| ERP BRD BR-INV-005 | Serial-number tracking for high-value parts — the counterpart of asset serial tracking |
| Scope Expansion Delta §M17 | "Corporate customer's asset listing… register all 100 devices with serial nos."; asset estates unmanaged; AMC entitlement cannot be tied to specific assets |
| Company Profile §Authorized Service Partnerships | 17+ brands; warranty claims are evidenced at device level |
| Company Profile §Core Services | Five device families — IT, mobile, appliance, server, peripheral — each with different identifier conventions |
| `_CATEGORY_OVERVIEW.md` §3 | "M17 never holds a company tool. M45 never holds a customer device." |
| `_CATEGORY_OVERVIEW.md` §4 | Telemetry is a separate data problem and belongs to M48 |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M17 is referenced by more modules than any other module
> in Category F, and the v2.0 draft loaded it with three unrelated concerns. Two capability
> groups have been moved out and are claimed by the modules named below; both sides of every
> boundary agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The permanent asset identity: one record per physical device, immutable ID, never reused |
| 2 | The multi-identifier model — serial, IMEI, MAC, asset tag, brand service tag, customer's own number, QR label |
| 3 | Identifier validation, identity resolution at intake, fuzzy matching and agent confirmation |
| 4 | Provisional identity, so intake is never blocked by an unreadable serial |
| 5 | Duplicate detection, controlled merge and reversible merge lineage |
| 6 | Asset labelling programme: QR/asset-tag generation, printing, association and re-labelling |
| 7 | Actual configuration and specification of the individual unit, where it differs from the model default |
| 8 | Component, accessory and asset-relationship model (parent, child, installed-in, replaced-by) |
| 9 | Ownership record and ownership history, with effective dates and transfer evidence |
| 10 | Custody state and the immutable custody chain across branch, technician, courier and workshop |
| 11 | Current location and location history |
| 12 | Asset population classification: customer-owned · rental pool · refurbishment stock · trade-in intake · e-waste pending |
| 13 | Consolidated service history projected from M01, M02, M31, M03, M05 and M06 |
| 14 | Part and component genealogy — which part serial went into which asset, when, and under what warranty |
| 15 | Rework and repeat-fault detection at asset level |
| 16 | Structured fault and symptom history |
| 17 | Warranty dates, entitlement resolution and coverage-conflict priority for a given asset at a given time |
| 18 | Repair warranty on 1000FiX's own work, per repair and per part |
| 19 | Warranty evidence assembly for M09 claims |
| 20 | Corporate asset estates: customer → site → department → user hierarchy |
| 21 | Bulk estate registration, estate reconciliation and stray/gap reporting |
| 22 | Plan-driven preventive maintenance schedules for customer assets |
| 23 | Condition grading with photographic evidence at each custody transfer |
| 24 | End-of-life routing decision and hand-off to M14 or M18 |
| 25 | Asset data-quality scoring, worklists and enrichment campaigns |
| 26 | Asset search, asset APIs for six portals, and asset domain events |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Telemetry ingestion, time-series storage, retention and downsampling** | **M48** IoT & Predictive Maintenance | Unbounded time-series volume must never sit in a transactional registry. See `_CATEGORY_OVERVIEW.md` §4 |
| **Asset health scoring and failure prediction** | **M48** (models from **M26**) | M17 displays the health index; it does not compute it |
| **Company-owned tools, test and diagnostic equipment** | **M45** Enterprise Asset & Test Equipment | A multimeter is issued and returned; a customer's laptop is received and delivered. Different lifecycle, different regulator, different owner |
| **Calibration records and certificates** | **M45** | Calibration applies to measuring equipment, never to a customer device |
| **Company vehicles** | **M46** Fleet & Vehicle Management | Vehicles carry statutory documents and fuel economics that no device has |
| **Buildings, premises and branch infrastructure** | **M47** Facility & Workplace | Premises are leased, licensed and maintained — a different asset class entirely |
| **Brand and model master data, specification templates, compatibility matrix** | **M37** Catalogue | The catalogue defines the *model*; M17 tracks the *instance* |
| **Customer and party identity, hierarchy and contacts** | **M33** Party Master | M17 references a party as owner; it never defines one |
| **The service order, work order, visit and repair transactions** | **M01, M31, M02** | M17 projects their outcomes onto the asset; it does not perform them |
| **Warranty claim lifecycle, submission and reconciliation** | **M09** Warranty & Claims | M17 supplies the evidence; M09 runs the claim |
| **Contract, AMC/RAMC and entitlement definition** | **M08** Contract Lifecycle | M17 resolves *which* entitlements apply to an asset; M08 defines what they mean |
| **Contract-driven preventive maintenance scheduling** | **M08** | Contract PM is a contractual obligation; M17 owns only plan-driven PM where no contract exists |
| **Spare part stock, serials and ownership classes** | **M15** Inventory | M15 owns the part until it is fitted; M17 owns it from the moment it becomes part of an asset |
| **Rental agreement, rate, availability and utilisation** | **M13** Rental & EaaS | M13 adds rental attributes to an M17 identity; it never creates a second identity |
| **Trade-in valuation, refurbishment grading and resale** | **M14** Trade-In & Refurbishment | M14 changes the asset's condition and population; M17 records that it happened |
| **E-waste batch, disposal certificate and recycler compliance** | **M18** E-Waste | M17 routes the asset out; M18 disposes of it lawfully |
| **Fixed-asset capitalisation and depreciation of rental-pool units** | **M49** Fixed Assets | M17 holds the operational identity; M49 holds the capital view |
| **Managed-endpoint monitoring overlay for MSP clients** | **M05** Remote Support & Managed Services | M05 adds a monitoring overlay to an M17 asset |
| **Media items removed from a device for data recovery** | **M06** Data Services | M06 owns the media while it is in the lab; M17 owns the parent device |
| **Customer consent and communication preference** | **M33 / M07** | Consent attaches to a person, not to a device |

### 3.3 Shared Concepts

| Concept | M17's Role | Owning Module |
|---|---|---|
| Asset / device | **Owns** — the defining concept of this module | M17 |
| Brand, model, specification template | References; stores the *actual* configuration of the instance | M37 |
| Owner party | References; owns the ownership *history* linking asset to party over time | M33 / M17 |
| Serial number | Owns for assets; M15 owns serials for parts in stock; the two meet at genealogy | M17 / M15 |
| Service history | Owns the projection; M01/M31/M02 own the transactions | M17 / M01 |
| Warranty dates and entitlement | Owns resolution against the asset; M08 and M09 own definition and claim | M17 / M08 / M09 |
| Custody | Owns the chain; M03 and M04 generate the events | M17 / M03 / M04 |
| Condition grade | Owns the grade on the asset; M14 owns refurbishment grading, M13 owns rental condition reports | M17 / M14 / M13 |
| Preventive maintenance plan | Owns plan-driven schedules; M08 owns contract-driven schedules; M45 owns own-equipment plans | M17 / M08 / M45 |
| Asset health index | Displays; M48 computes | M48 |
| Estate | **Owns**; M33 owns the party hierarchy the estate hangs from | M17 / M33 |
| Asset tag / label | Owns generation and association; M41 owns warehouse location labels | M17 / M41 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA Asset Management & Service — Technical Objects** | *Equipment* as an individual physical object maintained as an autonomous unit, installable at a *functional location* or within a superior piece of equipment for a period, and usable at different installation locations across its life | **The equipment/installation-location separation is the single most influential external reference for M17.** An asset has one identity and a *sequence* of installation locations, owners and custodians — never an identity per location. Also adopted: equipment categories driving different attribute sets and maintenance behaviour | SAP's full functional-location hierarchy for plant structures. Our "location" is a branch, a customer site or a van, not a process plant |
| **SAP Installed Base Management (CS-IB)** | An installed base as a structured, time-dependent hierarchy of serviceable items — materials, equipment, functional locations and BOMs — at a customer | The **installed-base concept for corporate estates**: a customer's estate is a structure, versioned over time, not a flat device list. This is the direct answer to the SOW's "register all 100 devices" | The full IBase/IBase-component modelling depth; our estates are three levels (site → department → user) |
| **PTC ServiceMax — Installed Base / Asset 360** | Instant access to on-site assets, service history and appointment info **including offline**; assets tracked by serial, batch or product number; work orders passed through an automated entitlement engine validating warranty and contract coverage | **Two things adopted outright.** (a) The **entitlement engine pattern** — every incoming job resolves entitlement against the asset before work is authorised, which is our defence against unbilled work and rejected claims. (b) **Offline asset history on the technician device**, because Bangladesh field connectivity is not a given | Its Salesforce platform coupling and IoT-centric asset-360 licensing |
| **Microsoft Dynamics 365 Field Service — Customer Assets** | Customer asset hierarchy with parent/child sub-assets, asset-to-work-order linkage, functional location on the asset | The **parent/child sub-asset model**, used for board-level and component-level repair genealogy — essential for a business doing Level 3 board repair | Its connected-field-service IoT bundling; that is M48's job here |
| **IFS Cloud — Serialised Object / Equipment** | A serialised object with a complete lifetime event log, position/structure history, and warranty per object and per component | **Component-level warranty**: a replaced motherboard carries its own warranty independent of the parent device's. Also adopted: the lifetime event log as an append-only structure | IFS's aviation-grade configuration-control depth |
| **Oracle Fusion Cloud — Installed Base Assets** | Asset transactions maintaining a full genealogy of install, move, transfer, split and merge | **Merge and split as first-class, logged, reversible transactions** rather than data fixes. Duplicate assets are inevitable at 250,000 customers/month; the question is whether merging them is auditable | Oracle's asset-transaction framework depth and its costing integration |
| **Salesforce Field Service — Asset hierarchy & Asset Warranty** | Asset warranty terms, asset service history, asset relationships | Warranty terms held **on the asset**, with distinct manufacturer, extended and workmanship layers | — |
| **GSMA IMEI / TAC allocation practice** | 15-digit IMEI = Type Allocation Code + serial + Luhn check digit; duplicate IMEI across two devices means at least one is fraudulent | **Identifier validation and duplicate-IMEI detection as a counterfeit signal.** A duplicate identifier is not a data-quality nuisance — it is a grey-market indicator, and in a market where counterfeit devices circulate it must raise a quality event | Building a TAC database. We validate structure and check digit, and flag duplicates; we do not attempt authoritative device attestation |
| **Odoo 19 CE `stock.lot` + `repair` + OCA `field-service`** | Serial/lot object, repair order against a lot, FSM equipment model | The transactional substrate for serial identity and repair linkage. OCA `fieldservice_equipment` supplies a workable location-and-equipment base | Odoo's `stock.lot` alone is far too weak: it has no ownership history, no custody chain, no multi-identifier model and no estate structure. This is why M17 carries a high custom share |
| **Master-data "golden record" practice** | Multi-attribute matching, survivorship rules, merge with lineage, stewardship worklists | The **golden-record discipline applied to devices**: candidate matching with a confidence score, human confirmation above a threshold, and a stewardship queue for unresolved identities | Buying an MDM platform. M64 provides governance; M17 provides the matching for its own domain |

**Design position.** Five deliberate differences from the benchmark.

First, **identity resolution never blocks intake.** Every tier-one system assumes the asset
exists, or that a clerk will create it correctly. At a 1000FiX counter, a customer arrives with
a laptop whose serial label has worn off, at a queue-managed front desk, in Bengali, in under
two minutes. M17 therefore permits a **provisional asset** — a real identity, flagged
incomplete, usable for intake and diagnosis, but which **cannot reach warranty claim or
invoice** until it is resolved. The alternative, in practice, is either a blocked queue or a
registry full of "SN-UNKNOWN-047" records. We have chosen the failure mode we can measure and
clear.

Second, **ownership is a history, not a field.** SAP, Oracle and Dynamics all support a current
owner. Because 1000FiX buys devices back (M14), rents them out (M13) and resells them, an asset
may have four owners in its life and its service history must survive all four. Ownership is
therefore a dated relationship table, and the asset's history is never re-parented.

Third, **the registry projects, it does not duplicate.** M17 stores no service order fields.
It subscribes to domain events from M01, M02, M31, M03, M05 and M06 and maintains a projection.
This is why the asset timeline is instantaneous while remaining a single source of truth: the
transaction lives in its owning module, the *view* lives here.

Fourth, **estates are reconciled, not merely recorded.** A corporate estate declared at
contract signature diverges from reality within months — machines are retired, moved and added
without telling the service partner. M17 runs a standing reconciliation between the declared
estate and the assets actually seen in service, producing gaps (declared, never seen) and
strays (seen, never declared). This report is the practical basis for contract true-up
conversations, and no benchmark system does it as a routine.

Fifth, **no telemetry, at any price.** The v2.0 draft placed telemetry inside M17. A registry
carrying millions of points per asset per year stops being a registry. M48 owns the time-series
platform; M17 holds a foreign key and a health index it did not compute.

---

## 5. Functional Areas & Features

### 5.1 Asset Identity & Identification

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AST-001 | Asset record | Maintain exactly one record per physical asset, with a permanent system-generated asset ID that is never reused, never edited and never re-parented on ownership change | **P0** | L5 |
| FR-AST-002 | Multi-identifier model | Hold any number of typed identifiers against an asset — manufacturer serial, IMEI, MAC address, 1000FiX asset tag, brand service tag, customer's own asset number, part number — each independently searchable and each retaining its source and capture date | **P0** | L5 |
| FR-AST-003 | Identifier validation | Validate identifier structure by type on capture, including IMEI length, TAC structure and Luhn check digit, MAC format, and configurable per-brand serial patterns, warning on failure without blocking capture | P1 | L5 |
| FR-AST-004 | Identity resolution | Resolve an inbound identifier against all identifier types across the whole estate, returning ranked candidate assets with a confidence score, and requiring explicit confirmation below a configurable confidence threshold (BR-SRM-005) | **P0** | L4/L5 |
| FR-AST-005 | Provisional identity | Permit creation of a provisional asset where identification is incomplete, marked as such, usable for intake and diagnosis, and blocked from warranty claim and invoice until resolved | **P0** | L5 |
| FR-AST-006 | Duplicate detection | Detect probable duplicate assets on creation and on a scheduled sweep, using identifier, model, owner and history signals, and queue them for stewardship | **P0** | L5 |
| FR-AST-007 | Controlled merge | Merge duplicate assets only through an approved transaction that retains full lineage of both records, re-points all history to the survivor, and remains reversible for a configurable period | **P0** | L5 |
| FR-AST-008 | Asset labelling | Generate, print and associate a durable 1000FiX QR asset tag, support re-labelling of a damaged tag with the prior tag retained in history, and record the labelling technician and date | P1 | L3/L5 |
| FR-AST-009 | Scan resolution | Resolve any identifier by camera or handheld scan from the technician app, admin portal, front desk and customer portal, returning the asset in ≤ 1 second | **P0** | L5 |
| FR-AST-010 | Identifier conflict | Detect the same identifier presented against two different assets, block automatic resolution, quarantine both for review and raise a quality event as a potential counterfeit or grey-market signal | P1 | L5 |

### 5.2 Asset Master, Specification & Structure

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AST-011 | Catalogue linkage | Link every asset to its brand, model and category in M37, and inherit the model's specification template, diagnostic checklist set and default maintenance profile | **P0** | L5 |
| FR-AST-012 | Actual configuration | Record the individual unit's actual configuration where it differs from the model default — memory, storage, processor, display, battery, firmware, operating system, installed options — and retain configuration history | P1 | L5 |
| FR-AST-013 | Asset category behaviour | Drive attribute sets, mandatory identifiers, diagnostic templates and maintenance defaults from an asset category taxonomy covering IT, mobile, appliance, server, network and peripheral families | **P0** | L5 |
| FR-AST-014 | Asset relationships | Model parent/child, installed-in, component-of, replaced-by and accessory-of relationships between assets and components, with effective dates | P1 | L5 |
| FR-AST-015 | Accessory register | Record accessories received with a device at intake — charger, bag, stylus, remote, cables — as a checklist that must be reconciled at return | **P0** | L5 |
| FR-AST-016 | Documents and evidence | Attach purchase invoice, warranty card, condition photographs, diagnostic reports and delivery evidence to the asset through M24, with retention policy applied | P1 | L2/L5 |

### 5.3 Ownership, Custody & Location

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AST-017 | Ownership history | Hold ownership as a dated relationship to an M33 party, retaining every prior owner, the transfer reason and the supporting evidence, and never deleting history on transfer | **P0** | L5 |
| FR-AST-018 | Ownership transfer | Record an ownership change arising from sale, trade-in, corporate reassignment, insurance write-off or resale, with the acquiring party, effective date and evidence document | P1 | L5 |
| FR-AST-019 | Custody state | Maintain the current custodian of the physical asset — customer, branch, named technician, courier, workshop, rental customer, recycler — as a single authoritative state | **P0** | L5 |
| FR-AST-020 | Custody chain | Record every custody transfer as an immutable event carrying from-party, to-party, timestamp, location, evidence and signature reference, projected from M03, M04, M31 and M02 | **P0** | L5 |
| FR-AST-021 | Location history | Maintain current physical location and full location history at branch, workshop, van, customer site or third-party granularity | P1 | L5 |
| FR-AST-022 | Population classification | Classify every asset into exactly one population — customer-owned · rental pool · refurbishment stock · trade-in intake · marketplace-listed · e-waste pending · company-issued-to-customer — governing which modules may act on it | **P0** | L5 |
| FR-AST-023 | Lost, stolen and disputed register | Flag an asset as lost, stolen or ownership-disputed, block its release, notify the branch network, and record the resolution | P1 | L5 |

### 5.4 Service History & Genealogy

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AST-024 | Consolidated history | Project every service order, workshop repair, field visit, remote session, data-recovery case, logistics movement and rental period onto the asset as a single chronological timeline (BR-SRM-006) | **P0** | L5 |
| FR-AST-025 | Timeline presentation | Present the timeline with date, event type, branch, technician, symptom, diagnosis, outcome, parts fitted and cost, filtered by role — cost visible only to permitted roles | **P0** | L5 |
| FR-AST-026 | Offline history | Make the last twelve months of an assigned asset's history available offline in the technician application, refreshed on sync (BR-SRM-020, BR-FSM-016, AS-13) | **P0** | L5 |
| FR-AST-027 | Part genealogy | Record, for every part consumed on the asset, the part serial or lot, the fitting date, the technician, the causing job, the part's own warranty period and the ownership class it was drawn from (BR-INV-005) | **P0** | L5 |
| FR-AST-028 | Component swap genealogy | Record component-level replacement — board, panel, battery, drive — with the removed component's disposition (returned to customer, harvested, scrapped, returned to brand) | P1 | L5 |
| FR-AST-029 | Repeat-fault detection | Detect the same asset returning with the same symptom or fault code within a configurable window, flag it as rework, and surface it at intake before the order is created (BR-SRM-016) | **P0** | L5 |
| FR-AST-030 | Fault and symptom history | Maintain a structured fault history using the coded symptom and resolution taxonomy shared with M23 and M61, queryable across the estate | P1 | L5 |
| FR-AST-031 | Reverse genealogy | Resolve, from a part serial or batch, every asset it was fitted to, and from an asset, every part it has ever carried — in both directions, for recall and claim purposes | P1 | L5 |

### 5.5 Warranty & Entitlement Context

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AST-032 | Warranty dates | Hold manufacturer warranty start and end for the asset, derived from purchase evidence, brand lookup or a configurable default from date of manufacture, with the derivation basis recorded (BR-CWM-005) | **P0** | L5 |
| FR-AST-033 | Entitlement resolution | Return, for a given asset at a given date, every active entitlement — manufacturer warranty, extended warranty, protection plan, AMC/RAMC, MSP contract, rental agreement, workmanship warranty — with its source and remaining term | **P0** | L5 |
| FR-AST-034 | Coverage priority | Apply a configurable priority order when several entitlements cover the same event, returning the governing entitlement and the reason it was selected | **P0** | L5 |
| FR-AST-035 | Workmanship warranty | Hold 1000FiX's own warranty on each repair performed and each part fitted, at repair and component granularity, and detect a return within that period | **P0** | L5 |
| FR-AST-036 | Claim evidence assembly | Assemble, on request from M09, a claim evidence pack containing identity, identifiers, ownership, purchase evidence, fault history, diagnostic report, parts genealogy and photographs (BR-CWM-008) | **P0** | L5 |
| FR-AST-037 | Warranty expiry visibility | Surface approaching manufacturer and extended warranty expiry to M07, M08 and M10 as a commercial trigger, and to the customer through P01 | P1 | L5 |

### 5.6 Corporate Asset Estates

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AST-038 | Estate structure | Model a corporate customer's asset estate as customer → site → department → assigned user, with each asset placed at exactly one node and moves recorded with effective dates | **P0** | L5 |
| FR-AST-039 | Bulk estate registration | Register an estate in bulk at contract onboarding from a validated file or portal upload, resolving each row against existing assets, reporting rejects line by line, and committing as a set | **P0** | L5 |
| FR-AST-040 | Estate reconciliation | Compare the declared estate against assets actually seen in service and produce, per customer, a gap list (declared, never seen), a stray list (seen, never declared) and a movement list | P1 | L5 |
| FR-AST-041 | Estate self-service | Expose the estate to the corporate portal for viewing, searching, requesting additions and retirements, and recording moves between sites, departments and users, subject to approval | P1 | L5 |
| FR-AST-042 | Estate entitlement | Apply contract coverage at estate, site, department or individual-asset level, and reject a service request for an asset outside the covered scope with a clear reason (BR-CWM-001) | **P0** | L5 |
| FR-AST-043 | Estate analytics | Report estate age profile, failure rate per model, cost to serve per asset, refresh candidates and coverage gaps, exposed to M07 for whitespace and to the account manager for quarterly review | P1 | L5 |

### 5.7 Condition, Lifecycle & Maintenance Plans

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AST-044 | Condition grade | Hold a standardised condition grade on the asset, updated at each custody transfer with mandatory photographic evidence, and retain the grade history | **P0** | L5 |
| FR-AST-045 | Asset lifecycle state | Enforce the asset lifecycle state machine in §8.1, with every transition guarded, actor-attributed and event-emitting | **P0** | L5 |
| FR-AST-046 | Plan-driven maintenance | Define preventive maintenance plans per asset or asset category, triggered by elapsed time, usage counter or telemetry-derived condition, generating due work into M01 — for assets not covered by a contract PM schedule owned by M08 | P1 | L5 |
| FR-AST-047 | Maintenance plan compliance | Report plan adherence, overdue maintenance and skipped visits per asset, per estate and per branch | P2 | L5 |
| FR-AST-048 | End-of-life routing | On an end-of-life decision, route the asset to M14 for refurbishment and resale, to M18 for lawful disposal, or to return-to-customer, recording the decision, its approver and its basis | P1 | L5 |
| FR-AST-049 | Health index display | Display the asset health index and any open failure prediction supplied by M48, without computing either | P2 | L5 |

### 5.8 Data Quality, Search & Interfaces

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-AST-050 | Data-quality score | Compute a completeness and confidence score per asset from mandatory attribute coverage, identifier verification, ownership evidence and history continuity, and report it by branch and by estate | P1 | L5 |
| FR-AST-051 | Stewardship worklist | Maintain a prioritised worklist of provisional identities, unresolved duplicates, identifier conflicts and low-quality records, assigned by branch, with ageing and escalation | P1 | L5 |
| FR-AST-052 | Asset search and APIs | Expose asset search and retrieval APIs — by identifier, owner, estate node, model, location and history predicate — meeting the latency budget in §6, consumed by M01, M02, M04, M31, M09 and portals P01–P04 and P08 | **P0** | L5 |

> **Cross-cutting.** Asset analytics, age profiling and failure-rate reporting are delivered as
> analytics over the registry and are specified in §14 rather than as separate transactional
> requirements. Telemetry-derived condition (FR-AST-046) is available only where M48 is live
> from Wave 8; before that, plans are time- and usage-triggered only.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Immutable asset identity** | The asset ID is generated once, is never edited by any role including administrators, and is never reused after merge or deletion. Enforced at database level |
| T-02 | **Identifier index performance** | Identifier lookup across all types and the full estate returns in ≤ 200 ms at p95 at a volume of 3 million assets and 9 million identifiers; the index is partial and case-normalised |
| T-03 | **Resolution service** | Identity resolution runs as a separate service (L4) with deterministic exact-match, normalised-match and fuzzy-match tiers, returning a confidence score with an explainable match reason. The service is stateless and horizontally scalable |
| T-04 | **Match explainability** | Every automatic resolution stores which identifier and which rule produced the match, so a wrong match can be diagnosed rather than guessed at |
| T-05 | **Append-only history** | Ownership, custody, location, condition and configuration histories are insert-only. A correction is a new dated row with a correction reason, never an update |
| T-06 | **Event-driven projection** | The service-history timeline is a projection built from domain events consumed through the outbox (AS-08). M17 never reads another module's tables (AS-01), and projection lag is monitored with an alert above 60 seconds |
| T-07 | **Projection rebuild** | The timeline projection is fully rebuildable from the event log within a bounded window, so a projection defect is recoverable without data loss |
| T-08 | **Merge integrity** | Merge is a single transaction that re-points every foreign reference, writes a merge-lineage record and remains reversible for a configurable period. A merge that cannot re-point every reference is rejected whole |
| T-09 | **Offline asset history** | The technician app holds the last twelve months of history for assigned assets in an append-only local journal, synchronising with server-side conflict resolution (AS-13) |
| T-10 | **Bulk import integrity** | Estate loads are staged, validated against M37 for model existence and against M33 for the owning party, resolved against existing assets, and committed or rejected as a set with a line-level reject report |
| T-11 | **Scale envelope** | 3 million assets, 9 million identifiers, 30 million history events at year three; the timeline is partitioned by asset and the event store by month |
| T-12 | **Multi-entity isolation** | Every asset carries `company_id` and `operating_unit_id`; record rules restrict branch visibility, with a controlled cross-branch search right for identity resolution only (AS-03) |
| T-13 | **Identifier normalisation** | Identifiers are stored raw and normalised (case, whitespace, common OCR confusions O/0 and I/1) with matching performed on the normalised form and display on the raw form |
| T-14 | **Field-level encryption** | Customer-linked identifiers that constitute personal data in combination are field-encrypted per AS-14; asset photographs are stored with access control and retention |
| T-15 | **Label generation** | Asset tags render as QR and Code-128 on thermal label stock, encode the asset ID rather than a serial, and remain resolvable after ownership change |
| T-16 | **Bengali support** | Asset descriptions, condition notes and fault text accept and render Bengali; all asset screens are fully translated (AS-12) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M17 |
|---|---|---|
| **Front-desk agent** | Types the brand, model and serial again for a returning customer; cannot tell whether the device has been here before | Scans or searches once; the device, its owner, its history and its coverage appear before the order is opened |
| **Technician** | Opens the device with no idea what the last engineer did to it | Sees the full timeline and previous diagnosis before travelling, offline, on the phone |
| **Workshop supervisor** | Discovers a repeat failure by memory or by accident | Repeat-fault flag raised automatically at intake, before labour is spent again |
| **Warranty claims officer** | Assembles claim evidence from three systems and a folder of photographs | Requests an evidence pack; it is assembled from the asset record in seconds |
| **Corporate account manager** | Cannot say what the client actually owns, or which machines are covered | Holds a reconciled estate, an age profile and a refresh conversation backed by data |
| **Corporate client's IT manager** | Emails a spreadsheet and hopes it is honoured | Sees the estate in the portal, requests moves and retirements, sees coverage per machine |
| **Branch manager** | Cannot explain a rework rate | Sees rework by asset, by model and by technician, with the history behind each case |
| **Procurement / inventory** | Guesses part compatibility from the model name a customer reported | Compatibility resolved from the asset's confirmed model in M37 |
| **Quality manager** | Investigates a systemic fault by anecdote | Queries fault codes across the installed base of a model and produces a brand-facing report |
| **Finance** | Cannot evidence which device generated which revenue | Every job, part and invoice traces to an asset identity that survives the transaction |

### 7.2 Quantified Business Benefit

M17 is an **enabling module**: it carries no benefit line of its own in the Scope Charter
§6.2 register, because the value it creates is realised inside the modules that depend on it.
The table below states that dependency explicitly rather than claiming the benefit twice.

| Benefit | Mechanism | Value |
|---|---|---|
| **Warranty revenue recovery** | Claim evidence — identity, purchase basis, fault history, part genealogy — assembled automatically instead of by hand; claims rejected for missing device evidence fall to near zero | Enables **BDT 100 lac/year** (Scope Charter §6.2, M09). M09 cannot deliver it without M17 |
| **AMC/RAMC renewal uplift** | Entitlement resolved per asset; expiry visible; estate age profile drives the refresh and renewal conversation | Enables **BDT 72 lac/year** (§6.2, M08) |
| **Customer retention** | Device history recognised on return; the customer is not asked the same questions twice | Contributes to **BDT 78 lac/year** (§6.2, M07 + M10 + M27) |
| **Technician productivity** | Prior diagnosis available before the visit; fewer second visits caused by unknown history | Contributes to **BDT 130 lac/year** (§6.2, M02 + M26) |
| **Rework reduction** | Repeat faults detected at intake rather than after labour and parts are spent again | Direct labour and parts avoidance; supports KPI-004 first-time fix 88% |
| **Corporate contract true-up** | Estate reconciliation converts an unmeasured entitlement dispute into a numbered conversation | Protects contract margin; prevents servicing uncovered assets free |
| **Cross-sell into the installed base** | Whitespace analysis against the estate (consumed by M07) | Revenue from existing customers at materially lower acquisition cost |
| **Counterfeit and grey-market defence** | Duplicate and conflicting identifiers raise a quality event rather than passing silently | Protects brand authorisation — the loss of one authorisation would exceed the entire M17 build cost |

> **Register action.** M17 has no line in the Scope Charter §6.2 benefit register. This is
> correct for an enabling module, but the dependency above should be recorded in `00-02` so
> that a decision to descope or delay M17 is visibly a decision to forgo BDT 100 lac of M09
> benefit. Recorded as an audit action.

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **ISO 9001 traceability** | Clause 8.5.2 requires identification and traceability of outputs. A device identity that survives every transaction is the practical mechanism, and 1000FiX's ISO status is a tender qualifier and a stated competitive advantage |
| **Brand partner assurance** | A brand auditing its authorised partner can be shown the complete life of any device it warranties, on demand |
| **Evidential defensibility** | Custody chain with signature and photographic evidence at every transfer is what protects the Company in a damage or loss dispute |
| **Data-services integrity** | M06 handles customer data-bearing media. Chain of custody at asset level is the control that makes the ISMS claim — "your device and data are secure" — verifiable rather than promotional |
| **Foundation for prediction** | M48 and M26 cannot predict failure without a clean installed base and a clean fault history. Two years of M17 data is the precondition for predictive maintenance |
| **Circular-economy foundation** | M14 refurbishment and M18 recycling both need to know a device's full life. Environmental reporting on materials recovered is only credible if the device is traceable |
| **Expansion readiness** | An entity- and operating-unit-scoped registry means a second country adds branches, not a second registry (BO-18) |

---

## 8. Lifecycle & State Models

### 8.1 Asset Lifecycle

```
              ┌───────────────┐
   first seen │  PROVISIONAL  │  identified incompletely at intake;
   at intake  │  (unresolved) │  cannot reach claim or invoice
              └───────┬───────┘
                      │ identity resolved and confirmed
              ┌───────▼───────┐
              │  REGISTERED   │  ◄── bulk estate load enters here
              └───────┬───────┘
                      │
              ┌───────▼───────┐
   ┌──────────►    ACTIVE     ◄──────────┐   in the owner's use
   │          └──┬─────┬──────┘          │
   │             │     │                 │
   │   received  │     │ deployed to     │ returned
   │   for       │     │ rental / refurb │
   │   service   │     │                 │
   │  ┌──────────▼──┐  │        ┌────────┴──────────┐
   │  │ IN CUSTODY  │  └───────►│  RENTED OUT (M13) │
   │  │  (1000FiX)  │           │  IN REFURB  (M14) │
   │  └──┬───────┬──┘           │  LISTED     (M12) │
   │     │       │              └────────┬──────────┘
   │     │       │ diagnosis and repair  │
   │  ┌──▼───────▼──┐                    │
   │  │UNDER SERVICE│                    │
   │  └──┬───────┬──┘                    │
   │     │       │ irreparable / written off
   │  ┌──▼─────┐ │                       │
   │  │AWAITING│ │                       │
   │  │COLLECT.│ │                       │
   │  └──┬─────┘ │                       │
   └─────┘       │                       │
                 │                       │
          ┌──────▼───────────────────────▼──────┐
          │           END OF LIFE                │
          └───┬──────────────┬───────────────┬──┘
              │              │               │
      ┌───────▼────┐  ┌──────▼──────┐  ┌─────▼──────┐
      │ REFURBISHED│  │  RECYCLED   │  │  RETURNED  │
      │  → resale  │  │   (M18)     │  │ TO CUSTOMER│
      │   (M14)    │  │             │  │  as-is     │
      └────────────┘  └─────────────┘  └────────────┘

   Orthogonal flags, settable from any state:
      LOST · STOLEN · OWNERSHIP DISPUTED · IDENTIFIER CONFLICT (quarantined)
      DORMANT (no event for a configurable period)
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Provisional | Intake proceeds without a confirmed identifier | Front-desk agent / technician |
| Provisional | Registered | Identity resolved and confirmed above the confidence threshold, or a verified identifier captured | Agent / stewardship officer |
| — | Registered | Bulk estate load validated and committed, or customer self-registration verified | System / account manager |
| Registered | Active | Owner confirmed and asset released to the owner's use | System |
| Active | In custody | Custody accepted at branch, from a courier, or by a technician on site | Branch / rider / technician |
| In custody | Under service | Diagnosis started against a service or repair order | Technician |
| Under service | Awaiting collection | Work complete and QC passed | Workshop supervisor |
| Awaiting collection | Active | Released to the customer with signature and condition evidence | Front desk |
| Active | Rented out | Allocated to a rental agreement (M13); asset must be in the rental-pool population | Rental officer |
| Active / Under service | In refurbishment | Trade-in accepted or refurbishment decision approved (M14) | Retail / refurbishment officer |
| Under service | End of life | Irreparable, or repair cost exceeds the approved threshold, with customer decision recorded | Workshop supervisor + customer |
| End of life | Refurbished | Economic recovery assessed as viable by M14 grading | Refurbishment officer |
| End of life | Recycled | No recovery value; routed to M18 with a disposal certificate | Quality manager |
| End of life | Returned to customer | Customer elects to take the device back unrepaired | Front desk |
| Any | Lost / Stolen | Reported and recorded with evidence; release blocked | Branch manager |
| Any | Identifier conflict | The same identifier detected on another asset | System, automatic |
| Any | Dormant | No event for the configured period | System, nightly |

### 8.2 Identity Resolution State

```
   inbound identifier
          │
   ┌──────▼───────┐   exact match on a verified identifier
   │  EXACT       ├──────────────────────────────► RESOLVED (confidence 1.00)
   └──────┬───────┘
          │ no exact match
   ┌──────▼───────┐   normalised match (case, whitespace, OCR confusions)
   │  NORMALISED  ├──────────────────────────────► RESOLVED (confidence 0.85–0.99)
   └──────┬───────┘
          │
   ┌──────▼───────┐   fuzzy on identifier + model + owner + locality
   │  FUZZY       ├──► CANDIDATES ──► agent confirms ──► RESOLVED (confidence recorded)
   └──────┬───────┘                └► agent rejects  ──► NEW ASSET
          │ no candidate above the floor
   ┌──────▼───────┐
   │  UNRESOLVED  ├──────────────────────────────► PROVISIONAL ASSET + stewardship task
   └──────────────┘
```

| Outcome | Threshold | Consequence |
|---|---|---|
| Resolved automatically | ≥ 0.95 | Asset attached to the transaction; match reason logged |
| Confirmed by agent | 0.60 – 0.95 | Candidates presented ranked; agent selects or rejects; selection logged |
| Provisional | < 0.60 or no candidate | Provisional asset created; stewardship task raised; claim and invoice blocked |
| Conflict | Same identifier, two assets | Both quarantined; quality event raised to M23; no automatic resolution |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-AST-01 | Every service order, repair order, field visit, rental agreement and warranty claim references exactly one asset | **H** | Service Operations Director |
| BRU-AST-02 | An asset ID is permanent: never edited, never reused, never re-parented on ownership change | **H** | CTO |
| BRU-AST-03 | An asset in provisional identity state cannot reach warranty claim submission or customer invoice | **H** | Warranty Claims Officer |
| BRU-AST-04 | A duplicate merge requires approval, retains full lineage of both records, and is reversible within the configured window | **H** | Quality Manager |
| BRU-AST-05 | The same identifier value of the same type may not resolve to two active assets; both are quarantined and a quality event raised | **H** | Quality Manager |
| BRU-AST-06 | Ownership history is never deleted or overwritten; a change of owner is a new dated row | **H** | CTO |
| BRU-AST-07 | Service history is never deleted, and never re-parented when ownership changes | **H** | Service Operations Director |
| BRU-AST-08 | An asset cannot be released from custody without a recorded condition grade, photographic evidence and an accessory reconciliation | **H** | Branch Operations Lead |
| BRU-AST-09 | An asset flagged lost, stolen or ownership-disputed cannot be released to any party until the flag is cleared by the Branch Manager | **H** | Branch Manager |
| BRU-AST-10 | An asset belongs to exactly one population at any time; a population change is a reason-coded, separately reported transaction | **H** | Service Operations Director |
| BRU-AST-11 | A rental-pool or refurbishment-stock asset may not be recorded as customer-owned without an ownership-transfer transaction | **H** | Finance Manager |
| BRU-AST-12 | Brand, model and category are read from M37; they may not be free-typed on the asset | **H** | Chief Commercial Officer |
| BRU-AST-13 | An asset returning with the same fault code within the configured rework window is flagged before the new order is created | **C** | Quality Manager |
| BRU-AST-14 | Entitlement is resolved against the asset at the event date, not at the query date | **C** | Chief Commercial Officer |
| BRU-AST-15 | Where multiple entitlements cover an event, the configured priority order governs and the selection reason is recorded | **C** | Chief Commercial Officer |
| BRU-AST-16 | Manufacturer warranty dates are recorded with their derivation basis; a defaulted date is flagged and cannot alone support a claim | **H** | Warranty Claims Officer |
| BRU-AST-17 | A corporate asset outside the contracted estate scope is not serviced under contract; the request is repriced or approved as an exception | **A** | Account Manager |
| BRU-AST-18 | An estate bulk load commits as a set; any validation failure rejects the whole batch with a line-level report | **H** | Account Manager |
| BRU-AST-19 | An asset routed to end of life requires a recorded decision, an approver and a customer instruction where the asset is customer-owned | **H** | Workshop Supervisor |
| BRU-AST-20 | Cost, margin and internal notes on the asset timeline are never visible to any external portal | **H** | CFO |
| BRU-AST-21 | Asset photographs and condition evidence are retained for the statutory period defined by M24 retention policy | **H** | Quality Manager |
| BRU-AST-22 | A provisional asset unresolved beyond the configured ageing threshold escalates to the Branch Manager and is included in the branch data-quality score | **C** | Branch Manager |
| BRU-AST-23 | M17 never holds a company-owned tool, vehicle, or premises; those belong to M45, M46 and M47 respectively | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.asset` | `fix_asset` | The permanent asset identity | asset_uid, model_id (M37), category_id, population, lifecycle_state, condition_grade, current_owner_party_id, current_custodian_type, current_custodian_id, current_location_id, data_quality_score, provisional, health_index, company_id, operating_unit_id, first_seen_at, dormant_since |
| `fix.asset.identifier` | `fix_asset_identifier` | Any identifier bound to an asset | asset_id, identifier_type, value_raw, value_normalised, verified, verification_source, captured_by, captured_at, superseded_at |
| `fix.asset.ownership` | `fix_asset_ownership` | Dated ownership relationship | asset_id, party_id (M33), owned_from, owned_to, acquisition_reason, evidence_document_id, recorded_by |
| `fix.asset.custody` | `fix_asset_custody` | Immutable custody event | asset_id, from_party_type, from_party_id, to_party_type, to_party_id, occurred_at, location_id, source_module, source_doc_id, signature_ref, evidence_ids, condition_grade_at_transfer |
| `fix.asset.location.history` | `fix_asset_location_history` | Where the asset has been | asset_id, location_type, location_id, from_at, to_at, source_doc_id |
| `fix.asset.configuration` | `fix_asset_configuration` | The unit's actual specification over time | asset_id, attribute_code, value, unit, effective_from, effective_to, source (intake/diagnostic/customer/brand) |
| `fix.asset.relationship` | `fix_asset_relationship` | Structure between assets and components | parent_asset_id, child_asset_id, relationship_type, effective_from, effective_to, established_by_doc_id |
| `fix.asset.accessory` | `fix_asset_accessory` | Accessories received and returned | asset_id, service_order_id, accessory_code, quantity, received_at, returned_at, discrepancy_flag |
| `fix.asset.service.history` | `fix_asset_service_history` | Projection of every transaction touching the asset | asset_id, event_type, source_module, source_doc_id, occurred_at, branch_id, technician_id, symptom_code, diagnosis_code, outcome_code, parts_summary, cost_total, entitlement_applied |
| `fix.asset.fault` | `fix_asset_fault` | Structured fault history | asset_id, fault_code, symptom_code, reported_at, confirmed_at, resolution_code, recurrence_of_fault_id, service_order_id |
| `fix.part.genealogy` | `fix_part_genealogy` | Which part went into which asset | asset_id, part_id (M37), part_serial, lot_id, fitted_at, fitted_by, service_order_id, ownership_class (M15), part_warranty_until, removed_at, removed_part_disposition |
| `fix.asset.warranty` | `fix_asset_warranty` | Warranty layers on the asset | asset_id, warranty_type (manufacturer/extended/protection/workmanship), start_date, end_date, derivation_basis, source_contract_id, component_scope, remaining_term_days |
| `fix.asset.entitlement.view` | `fix_asset_entitlement_view` | Resolved coverage at a point in time | asset_id, as_of, entitlement_type, source_module, source_doc_id, priority_rank, governing, selection_reason |
| `fix.asset.estate` | `fix_asset_estate` | A corporate customer's estate | customer_party_id, name, contract_id (M08), declared_count, reconciled_at, coverage_scope, portal_visible |
| `fix.asset.estate.node` | `fix_asset_estate_node` | Site, department or user node | estate_id, parent_node_id, node_type (site/department/user), name, address_id, contact_party_id, cost_centre |
| `fix.asset.estate.placement` | `fix_asset_estate_placement` | An asset at an estate node, over time | asset_id, estate_id, node_id, placed_from, placed_to, moved_by, move_reason |
| `fix.asset.estate.reconciliation` | `fix_asset_estate_reconciliation` | Declared vs observed | estate_id, run_at, declared_count, observed_count, gap_lines, stray_lines, movement_lines, statement_doc_id, acknowledged_at |
| `fix.maintenance.plan` | `fix_maintenance_plan` | Plan-driven PM for customer assets | scope_type (asset/category/estate), scope_id, trigger_type (elapsed/usage/condition), interval_value, interval_uom, task_template_id, next_due_at, last_completed_at, active |
| `fix.asset.condition.history` | `fix_asset_condition_history` | Grade over time with evidence | asset_id, grade, assessed_at, assessed_by, custody_event_id, evidence_ids, notes |
| `fix.asset.merge` | `fix_asset_merge` | Merge lineage | survivor_asset_id, merged_asset_id, merged_at, merged_by, approved_by, reason, reversible_until, reversed_at, reference_map |
| `fix.asset.identity.resolution` | `fix_asset_identity_resolution` | Every resolution attempt and its reason | inbound_identifier, inbound_type, resolved_asset_id, confidence, match_tier, match_rule, confirmed_by, occurred_at, source_channel |
| `fix.asset.quality.issue` | `fix_asset_quality_issue` | Stewardship worklist | asset_id, issue_type (provisional/duplicate/conflict/incomplete), severity, raised_at, assigned_branch_id, assigned_to, state, resolved_at, resolution |
| `fix.asset.label` | `fix_asset_label` | Physical tag association | asset_id, label_code, label_type, printed_at, applied_by, applied_at, replaced_label_code, active |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.catalogue.item` — brand, model, category, specification template, compatibility | **M37** | Read via API; cached projection |
| `fix.party` — customer, corporate account, brand, recycler | **M33** | Read via API |
| `fix.service.order`, `fix.work.order`, `fix.repair.order` | M01 / M02 / M31 | Event projection only; never a direct table read |
| `fix.visit`, `fix.technician.profile` | M02 | Event projection |
| `fix.consignment`, `fix.custody.event` | M03 | Event projection into the custody chain |
| `fix.stock.serial`, `fix.stock.issue` | M15 | Event projection into part genealogy |
| `fix.contract`, `fix.entitlement`, `fix.contract.schedule` | M08 | Read via API for entitlement resolution |
| `fix.brand.claim`, `fix.warranty.register` | M09 | Read for claim linkage; supply evidence |
| `fix.rental.asset`, `fix.rental.line` | M13 | Read for rental period on the timeline |
| `fix.refurb.grade`, `fix.tradein.offer` | M14 / M37 | Read for condition and population change |
| `fix.ewaste.item`, `fix.disposal.certificate` | M18 | Read for end-of-life closure |
| `fix.asset.health`, `fix.failure.prediction` | **M48** | Read only — computed there, displayed here |
| `fix.document`, `fix.retention.class` | M24 | Read/write attachments under policy |
| `fix.branch`, `fix.entity`, `fix.branch` | M30 | Read |
| `fix.fault.taxonomy` | M37 | Read |

> **Register action — entity reallocation.** `05-02` §M17 lists 18 owned entities including
> `fix.brand`, `fix.model`, `fix.calibration.record`, `fix.telemetry.stream`,
> `fix.telemetry.point`, `fix.asset.health`, `fix.failure.prediction` and `fix.tool.register`.
> Under the v2.1 re-scope: **`fix.brand` and `fix.model` belong to M37**;
> **`fix.calibration.record` and `fix.tool.register` belong to M45**; **`fix.telemetry.*`,
> `fix.asset.health` and `fix.failure.prediction` belong to M48**. `05-02` requires
> amendment. Recorded as an audit action.

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-AST-01 | An identifier is presented at any channel — counter, portal, technician app, contact centre | Run identity resolution, return ranked candidates with confidence and match reason, auto-attach above the threshold | Create a provisional asset and raise a stewardship task; never block the transaction |
| AUT-AST-02 | A provisional asset is created | Raise a stewardship task to the owning branch with an ageing clock, and block claim and invoice on that asset | Task remains open and reportable; escalation at threshold |
| AUT-AST-03 | Nightly | Sweep for probable duplicates across identifiers, model, owner and history signals; queue candidates for stewardship | Retain the previous candidate set and alert |
| AUT-AST-04 | The same identifier resolves to two active assets | Quarantine both, block automatic resolution, raise a quality event to M23 and notify the Quality Manager | Immediate hard block |
| AUT-AST-05 | A service order, repair, visit, remote session or logistics movement completes | Project the outcome onto the asset timeline, update condition, location and custody | Retry through the outbox; alert if projection lag exceeds 60 seconds |
| AUT-AST-06 | A part is consumed on a job (`stock.consumed` from M15) | Write the part genealogy row including serial, warranty period and ownership class | Queue and retry; the job cannot close with unwritten genealogy for a serial-controlled part |
| AUT-AST-07 | An asset is presented at intake | Check the rework window for the same fault code, flag repeat failure, and surface prior diagnosis before the order is created (BR-SRM-016) | Present history without the flag; log the evaluation failure |
| AUT-AST-08 | A service order is created | Resolve entitlements as at the event date, return the governing coverage and the reason, and pass it to M01 | Fall back to manual entitlement selection with an exception record |
| AUT-AST-09 | M09 requests claim evidence | Assemble the evidence pack — identity, ownership, purchase basis, fault history, diagnostics, genealogy, photographs — and attach it to the claim | Raise an evidence-incomplete exception naming the missing element |
| AUT-AST-10 | Manufacturer or extended warranty approaches expiry at the configured horizons | Notify M08, M07 and M10 for renewal and protection-plan offers, and surface to the customer through P01 | Alert only |
| AUT-AST-11 | An estate file is uploaded | Validate every line against M37 and M33, resolve against existing assets, and commit or reject as a set with a line-level report | Reject whole; retain the staged file for correction |
| AUT-AST-12 | Monthly, per corporate estate | Run reconciliation of declared versus observed assets, produce gap, stray and movement lists, and publish to P04 and the account manager | Escalate to the account manager |
| AUT-AST-13 | A maintenance plan falls due | Create the due work in M01 against the asset, addressed to the covering branch, and notify the owner | Raise an overdue-maintenance exception |
| AUT-AST-14 | Custody transfer recorded without a condition grade or accessory reconciliation | Block the release and prompt for the missing evidence | Hard block |
| AUT-AST-15 | An asset receives no event for the configured dormancy period | Mark dormant, exclude from active-estate counts, and add to the re-engagement list for M07 and M10 | Report only |
| AUT-AST-16 | M48 publishes a failure prediction or a health-index change | Update the displayed health index, and where a maintenance plan is condition-triggered, evaluate whether work is now due | Retain the previous index and alert |
| AUT-AST-17 | An asset is routed to end of life | Notify M14 or M18 by route, close open plans and entitlements, and record the disposal or refurbishment reference on the asset | Manual routing task |
| AUT-AST-18 | Nightly | Recompute data-quality scores, refresh the stewardship worklist, and publish branch and estate quality reports | Retain previous scores and alert |

---

## 12. Interfaces

### 12.1 Upstream — M17 Consumes

| Source | What | Mechanism |
|---|---|---|
| M37 Catalogue | Brand, model, category, specification template, serial-format rules, compatibility | REST + cached projection |
| M33 Party Master | Customer, corporate account, brand and recycler identity | REST |
| M64 MDM | Asset category, identifier-type and taxonomy governance | Event projection |
| M01 Service Order | Order created, diagnosed, completed, closed | Events |
| M31 Workshop | Repair outcome, component swap, QC result | Events |
| M02 Field Service | Visit completed, on-site condition, photographs | Events |
| M03 Logistics | Collection, custody transfer, delivery, proof of delivery | Events |
| M04 Front Desk | Intake, storage, collection, accessory checklist | Events |
| M05 Managed Services | Monitored-asset onboarding and configuration change | Events |
| M06 Data Services | Media removal and return against the parent device | Events |
| M15 Inventory | Part consumed, serial issued, recall declared | Events |
| M08 Contracts | Contract coverage, entitlement definition, contract PM schedule | REST |
| M09 Warranty | Claim raised, claim outcome | Events |
| M13 Rental | Rental allocation, return, condition report | Events |
| M14 Refurbishment | Trade-in accepted, grading result, resale | Events |
| M18 E-Waste | Disposal certificate, recycling batch closure | Events |
| M48 IoT & Predictive | Health index, failure prediction, condition trigger | Events |
| M24 Documents | Attachment storage and retention policy | REST |

### 12.2 Downstream — M17 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 Service Order | Asset identity, specification, history, entitlement, rework flag | REST `GET /api/v1/assets/{id}` + events |
| M04 Front Desk | Identity resolution at the counter, inline registration, accessory checklist | REST |
| M02 Field Service | Asset identity and offline history for the assigned job | REST + sync payload |
| M31 Workshop | Identity, configuration, component structure, prior repairs | REST |
| M03 Logistics | Item identity and declared basis for custody and valuation | REST |
| M05 Managed Services | Asset identity for monitored estates | REST |
| M06 Data Services | Parent device identity for a media item | REST |
| M09 Warranty | Claim evidence pack, warranty dates, part genealogy | REST |
| M08 Contracts | Covered-asset resolution and estate scope | REST |
| M07 CRM | Estate for whitespace, refresh and quarterly review | REST + events |
| M10 Loyalty | Device ownership as a segmentation and campaign input | Events |
| M13 Rental | Asset identity for rental units | REST |
| M14 Refurbishment | Asset identity, history and condition for grading | REST |
| M15 Inventory | Model confirmation for part compatibility resolution | REST |
| M18 E-Waste | Asset identity and material composition basis | REST |
| M23 Quality | Fault patterns, identifier conflicts, rework cases | Events |
| M26 AI/ML | Installed-base and fault history features for failure models | Warehouse extract |
| M48 IoT | Asset identity that every telemetry stream must bind to | REST |
| M25 BI / M62 Data Platform | Asset, history, estate and quality facts | Warehouse extract |
| P01 Customer Portal | My devices, history, warranty status, service booking by device | REST |
| P02 Technician App | Asset history offline, condition capture, identifier scan | REST + sync |
| P03 Admin Portal | Full registry, stewardship, estate management | REST |
| P04 Corporate Portal | Estate view, moves, additions, retirements, coverage | REST |
| P08 Brand Portal | Installed-base and fault reporting for the brand's own models | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `asset.registered` | asset, identifiers, model, owner, population, provisional flag | M01, M07, M15, M62 |
| `asset.identity_resolved` | asset, inbound identifier, confidence, match tier, confirmer | M23, M62 |
| `asset.provisional_raised` | asset, branch, missing identifiers | M23, M04 |
| `asset.merged` | survivor, merged asset, approver, reference map | M01, M09, M15, M62 |
| `asset.identifier_conflict` | identifier, competing assets, evidence | M23, M15, M29 |
| `asset.ownership_transferred` | asset, from party, to party, reason, effective date | M07, M09, M20, M13, M14 |
| `asset.custody_transferred` | asset, from, to, location, evidence, condition grade | M03, M04, M24, M23 |
| `asset.condition_changed` | asset, grade, evidence, assessor | M13, M14, M09 |
| `asset.population_changed` | asset, from population, to population, reason, approver | M13, M14, M15, M49 |
| `asset.repeat_fault_detected` | asset, fault code, prior order, interval | M01, M23, M34 |
| `asset.genealogy_recorded` | asset, part serial, warranty until, job | M09, M15 |
| `asset.warranty_expiring` | asset, warranty type, expiry date, owner | M08, M07, M10, M27 |
| `asset.entitlement_resolved` | asset, as-of, governing entitlement, reason | M01, M08, M20 |
| `asset.estate_reconciled` | estate, gaps, strays, movements | M07, M08, M04 |
| `asset.maintenance_due` | asset, plan, due date, task template | M01, M02 |
| `asset.end_of_life` | asset, route, approver, basis | M14, M18, M49 |
| `asset.flagged` | asset, flag type (lost/stolen/disputed), evidence | M03, M04, M29 |
| `asset.quality_issue_raised` | asset, issue type, severity, branch | M23, M64 |
| `asset.model_unknown` | serial or IMEI, captured brand, captured model string, category hint, first-seen source | M37, M64, M26 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-AST-01 | Brand warranty-lookup services (Dell, HP, Lenovo, Acer and others, where exposed) | Outbound | Verify manufacturer warranty status and purchase date by serial or service tag; file or manual fallback where no interface exists |
| INT-AST-02 | 1000FiX public web platform — device report and warranty check | Bidirectional | Customer-facing device lookup and warranty-extension eligibility |
| INT-AST-03 | Thermal label printers at branches and workshops | Outbound | Asset-tag printing in Code-128 and QR |
| INT-AST-04 | Handheld scanners and Android scan devices | Inbound | Identifier capture at intake, custody transfer and stocktake |
| INT-AST-05 | Corporate client asset-management systems | Inbound | Estate file exchange at onboarding and periodic refresh; CSV/Excel in W2, API by exception |
| INT-AST-06 | Legacy order-tracking system and branch spreadsheets | Inbound, one-time | Historical device and service-history migration; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/assets/{id}` | GET | Full asset record with identity, owner, custody, condition and coverage | M01, M02, M31, P01–P04 |
| `/api/v1/assets/resolve` | POST | Resolve an identifier to ranked candidates with confidence and reason | M04, M01, P02, P10 |
| `/api/v1/assets` | POST | Register an asset, including provisional registration | M04, M01, P01 |
| `/api/v1/assets/{id}/identifiers` | POST | Add or verify an identifier | M04, M31, P02 |
| `/api/v1/assets/{id}/history` | GET | Timeline, filtered by role and paginated | M01, M02, P01–P04 |
| `/api/v1/assets/{id}/genealogy` | GET | Parts and components fitted, both directions | M09, M15, M31 |
| `/api/v1/assets/{id}/entitlements` | GET | Resolved coverage as at a supplied date | M01, M08, M20 |
| `/api/v1/assets/{id}/evidence-pack` | POST | Assemble a warranty claim evidence pack | M09 |
| `/api/v1/assets/{id}/custody` | POST | Record a custody transfer with evidence | M03, M04, P02, P09 |
| `/api/v1/assets/{id}/condition` | POST | Record a condition grade with photographs | M04, M31, P02 |
| `/api/v1/assets/merge` | POST | Request an approved duplicate merge | P03 |
| `/api/v1/estates/{id}` | GET | Estate structure and placements | P04, M07, M08 |
| `/api/v1/estates/{id}/bulk-load` | POST | Bulk estate registration, validated and set-committed | P04, M07 |
| `/api/v1/estates/{id}/reconciliation` | GET | Latest declared-versus-observed reconciliation | P04, M07 |
| `/api/v1/assets/search` | GET | Search by identifier, owner, estate node, model, location, history predicate | P03, P04, M25 |
| `/api/v1/assets/{id}/maintenance-plans` | GET/POST | Read and define plan-driven maintenance | M01, P03, P04 |
| `/api/v1/assets/quality/worklist` | GET | Stewardship worklist by branch | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R05 Operations Director | R U A | All branches; approves merges and population changes |
| R06 Branch Manager | C R U A | Own branch; clears lost/stolen flags, resolves stewardship escalations |
| R08 Service Centre Agent | C R U | Own branch — register, resolve identity, capture condition and accessories |
| R09 Workshop Supervisor | C R U | Own workshop — configuration, component structure, condition |
| R10 / R11 / R12 Technician | R U | Assigned assets only — history read, condition and identifier capture |
| R32 Quality Manager / ISO Coordinator | R U A | All — identifier conflicts, duplicate approval, fault taxonomy, quality events |
| R28 Warranty Claims Officer | R | All — evidence packs, warranty dates, genealogy |
| R22 Account Manager (Corporate) | C R U | Assigned accounts — estate structure, bulk load, reconciliation |
| R21 Sales Manager | R | Assigned segment — estate for whitespace and refresh |
| R15 Logistics Coordinator / R16 Rider / Delivery Agent | R U | Own manifest — custody transfer and condition evidence only |
| R17 Inventory Manager | R | All — genealogy for recall and part traceability |
| R25 Retail / Refurbishment Officer | R U | Refurbishment and trade-in population only |
| R26 Finance Manager / R27 Finance Officer | R | All — asset basis for revenue and claim reconciliation |
| R33 IT / System Administrator | R U | Configuration, taxonomy and technical support; **no merge right** |
| R02 Chief Technology Officer | R A | All; approves taxonomy and identifier-type changes |
| R36 Customer (P01) | R | Own devices only — identity, history summary, warranty status; never cost, never internal notes |
| R37 Corporate Portal User (P04) | R U | Own company's estate; role-scoped — Requester views, Admin requests moves, Approver approves |
| R38 Brand Partner (P08) | R | Installed base and fault statistics for the brand's own models only; never customer identity |

**Field-level restrictions.** `cost_total`, `margin` and `internal_note` on the asset timeline
are visible only to R01–R05, R06, R17, R21, R22, R26 and R27 (per `05-04` §5) and are never
exposed to P01, P04, P07, P08 or P12. Customer identity is stripped from every brand-portal
view. `recovered_data_index` and any data-services detail remain owned and restricted by M06.
Photographic condition evidence is visible to internal roles and to the owning customer only.

**Segregation of duties.**
- The user who creates a provisional asset may not approve its merge into another asset.
- The user who flags an asset lost or stolen may not clear the flag.
- A technician may not change the ownership of an asset in their own custody.
- **SOD-10 supported here:** the asset population change from customer-owned to
  refurbishment stock is separated from trade-in valuation (M14) and from resale (M12/M38).

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Asset registry coverage** | Operations Director, Quality Manager | Weekly | Assets registered, provisional outstanding, duplicates queued, conflicts open, by branch |
| **Data-quality scorecard** | Branch Manager, Quality Manager | Weekly | Completeness by branch and by estate, ageing of stewardship items, trend against the > 95% target |
| Identity-resolution performance | CTO, Quality Manager | Monthly | Auto-resolution rate, agent-confirmation rate, provisional rate, false-match reports |
| **Corporate estate reconciliation** | Account Manager, corporate client (P04), CCO | Monthly | Declared, observed, gaps, strays, movements, coverage exceptions |
| Estate age and refresh profile | Account Manager, Sales Manager | Quarterly | Age bands, failure rate by model, refresh candidates, whitespace |
| Device service history enquiry | Front desk, technician, workshop | On demand | Full timeline for any asset, both directions of genealogy |
| **Repeat-fault and rework register** | Quality Manager, Branch Manager, Operations Director | Weekly | Assets returning within the rework window, by branch, technician, model and fault code |
| Installed-base fault analysis | Quality Manager, brand partner (P08) | Monthly | Fault code frequency by model across the installed base, with population size |
| Warranty coverage and expiry pipeline | CCO, Account Manager, Marketing | Monthly | Assets by coverage state, expiries at 90/60/30 days, protection-plan opportunity |
| Custody exception report | Branch Operations Lead, Quality Manager | Daily | Releases without condition evidence, accessory discrepancies, overdue custody |
| Lost, stolen and disputed register | Branch Manager, Legal, Operations Director | Weekly | Open flags, ageing, resolution |
| Identifier conflict and counterfeit register | Quality Manager, Procurement, brand partners | Weekly | Duplicate and conflicting identifiers, source channel, disposition |
| Merge and lineage register | Quality Manager, Internal Audit | Monthly | Every merge with requester, approver, reason and reversibility window |
| End-of-life routing | Quality Manager, Retail Head, CFO | Monthly | Assets routed to refurbishment, recycling and return, with basis and value |
| Maintenance-plan adherence | Operations Director, Account Manager | Monthly | Plans due, completed, overdue, by estate and branch |
| Asset population movement | CFO, Retail Head | Monthly | Population changes with approver and financial consequence |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | Devices with complete registry data | unmeasured | 90% | **> 95%** |
| — | Assets identified at intake without manual entry | unmeasured | 80% | **> 90%** |
| — | Corporate estates reconciled | unmeasured | 70% | **> 90% of contracted estates** |
| — | Automatic identity resolution rate | 0% | 75% | **88%** |
| — | Provisional assets outstanding beyond 7 days | n/a | < 8% | **< 2%** |
| — | Duplicate asset rate in the active registry | unknown | < 2% | **< 0.5%** |
| — | Service orders opened against a confirmed asset | ~0% | 95% | **100%** |
| — | Warranty claims rejected for missing device evidence | unmeasured | < 5% | **< 1%** |
| — | Serial-controlled parts with genealogy written | ~0% | **100%** | **100%** |
| — | Repeat faults detected at intake rather than after repair | 0% | 85% | **98%** |
| — | Custody transfers with condition evidence | unmeasured | 95% | **99.5%** |
| — | Asset history retrieval latency (p95) | n/a | ≤ 800 ms | **≤ 500 ms** |
| — | Estate reconciliation variance accepted by the client | n/a | 70% | **90%** |
| **KPI-004** *(supported)* | First-time fix rate | 72% | 82% | **88%** |
| **KPI-041** *(supported)* | Warranty claims with complete evidence | unmeasured | 92% | **98%** |

> **Register note.** M17 has **no KPI-0nn identifiers allocated** in the programme KPI register.
> The category-level targets in `_CATEGORY_OVERVIEW.md` §7 (registry completeness > 95%,
> identification without manual entry > 90%, estates reconciled > 90%) are adopted verbatim
> above. All thirteen unnumbered metrics require allocation in the KPI register
> (`06-02`, not yet issued). Recorded as an audit action. KPI-004 and KPI-041 are owned by
> M02 and M09 respectively and are shown here as *supported*, not claimed.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `stock.lot` serial foundation, `repair` linkage, `product` model reference, `mail.thread` chatter and activity | 12% |
| L2 | OCA `field-service` equipment models, OCA `partner-contact` for estate contacts, OCA `dms` for evidence | 14% |
| L4 | Identity-resolution service (standalone Python/FastAPI, deterministic + fuzzy tiers) | 8% |
| L5 | `cd_asset_registry`, `cd_asset_identity`, `cd_asset_estate`, `cd_asset_genealogy`, `cd_maintenance_plan` | 66% |

> The custom share is high and deliberately so. `02-01` §11 indicates M17 as L1 ●, L2 ●●,
> L4 ●, L5 ●● — broadly consistent in shape, but the measured allocation is more custom than
> that summary suggests. No off-the-shelf Odoo or OCA component provides a multi-identifier
> model, an ownership history, a custody chain or an estate structure; each has to be built.
> Nothing was rejected in favour of custom code where a viable community module existed.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 5 of 5 identifiers below are claimed by another module: **CD-075** also claimed by M55; **CD-076** also claimed by M56; **CD-077** also claimed by M56; **CD-157** also claimed by M19, M29; **CD-158** also claimed by M19, M29. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-075 | `cd_asset_registry` — asset identity, population, lifecycle state machine, configuration, relationships, accessories, condition history, labelling | Odoo module | 7 PW |
| **CD-157** | `cd_asset_identity` — multi-identifier model, validation, resolution client, duplicate detection, controlled merge with lineage, stewardship worklist, data-quality scoring | Odoo module + L4 service | 7 PW |
| CD-076 | `cd_asset_estate` — estate hierarchy, placement history, bulk load, reconciliation engine, portal surface, estate analytics | Odoo module | 5 PW |
| **CD-158** | `cd_asset_genealogy` — service-history projection, part and component genealogy, fault history, repeat-fault detection, entitlement resolution, claim evidence assembly | Odoo module | 5 PW |
| CD-077 | `cd_maintenance_plan` — plan definition, elapsed/usage/condition triggers, due-work generation, adherence reporting | Odoo module | 2 PW |

> **CD register reallocation.** `02-05` §5.2 allocated **CD-075…079** to M17 as
> `cd_asset_registry`, `cd_asset_estate`, `cd_maintenance_plan`, `cd_telemetry`,
> `cd_asset_health`. Under the v2.1 re-scope, **`cd_telemetry` (CD-078) and `cd_asset_health`
> (CD-079) move to M48**, retaining their IDs. Two new IDs, **CD-157 and CD-158**, are claimed
> from the extension block reserved for modules M31–M67, continuing from CD-156 which is the
> highest ID claimed by Category E. **All CD IDs remain provisional** pending the unified CD
> register required by audit finding M-01 in `02-05`.
>
> **Category F CD block (for cross-module coherence).** CD-075…077 + CD-157…158 M17 ·
> CD-159…162 M45 · CD-163…166 M46 · CD-167…170 M47 · CD-078…079 + CD-171…173 M48.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M17 is scheduled in **W2** (P1) but declares a dependency on 1 module(s) that land later: **M24** (W3). One of three things must be true before the W2 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W2 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M17 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W2 plan for M17 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M37 Catalogue | An asset must reference a brand, model and category that already exist |
| M33 Party Master | An owner must be identifiable before ownership can be recorded |
| M29 Identity, M30 Platform Admin, M28 Integration | Record rules, entity and operating-unit model, event outbox — the projection depends entirely on the outbox |
| M64 MDM | Asset category and identifier-type governance before a large registry load |
| M24 Documents | Condition evidence and purchase documents need a store with retention policy |
| M01 Service Order | Bidirectional: M01 depends on M17 for identity, M17 depends on M01's events for history. Delivered in the same wave with M17's identity core first |

**Delivers into:** M01, M04, M02, M31, M03, M05, M06, M08, M09, M13 and M14 all require asset
identity. M17's identity core is therefore a **Wave 1 prerequisite** even though the full module
completes in Wave 2, and it sits with M01 on the critical path.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Legacy order-tracking system — device records attached to orders | Unknown; estimated 300,000–600,000 distinct devices | `fix.asset`, `fix.asset.identifier` | W1–W2 |
| Legacy service history | 24–36 months where recoverable | `fix.asset.service.history` | W2, best-effort |
| Branch spreadsheets — corporate device lists | 51+ files, unstructured | `fix.asset.estate`, `fix.asset.estate.placement` | W2, client-confirmed |
| Corporate client estate declarations | Held by each client | `fix.asset.estate` | W2, per contract |
| Warranty records held per brand | 17+ brands, various formats | `fix.asset.warranty` | W2–W3 |
| Rental pool device list | Held operationally | `fix.asset` (rental-pool population) | W2, confirmed by count |

> **Migration position.** Legacy device records are loaded as **provisional identities unless
> they carry a verified identifier**, and are cleared through the stewardship worklist rather
> than being silently trusted. Loading unverified records as confirmed would permanently
> contaminate the duplicate rate and the data-quality score, and would make the > 95%
> completeness target unmeasurable. The alternative — clearing 600,000 records by hand before
> go-live — is not available, so the registry starts partly provisional **by design**, with a
> published burn-down. This is the single largest data commitment M17 asks of the business, and
> it must be planned as a twelve-month clearance programme, not a cutover task.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every service order, repair order, field visit and warranty claim in production references exactly one asset | Full-table assertion query with zero exceptions |
| AC-02 | An asset ID cannot be edited or reused by any role, including system administrator | Negative test across UI, API and direct ORM call |
| AC-03 | Identity resolution across 3 million assets returns ranked candidates in ≤ 200 ms at p95 | Performance test at production data volume |
| AC-04 | A provisional asset cannot reach warranty claim submission or customer invoice through any path — UI, API or bulk | Negative test suite covering all three paths |
| AC-05 | A duplicate merge re-points every reference, retains lineage, and is fully reversible within the configured window | Scripted merge and reverse with reference-integrity assertion |
| AC-06 | The same identifier presented against two assets quarantines both and raises a quality event | Scripted conflict scenario |
| AC-07 | Ownership transfer preserves the complete prior service history and prior owner record | Scripted trade-in → refurbish → resale scenario across M14 and M12 |
| AC-08 | The asset timeline reflects a completed service order within 60 seconds of closure | Projection-lag test under load |
| AC-09 | The timeline projection is rebuildable from the event log with byte-identical results | Rebuild test on a production-sized dataset |
| AC-10 | Twelve months of assigned-asset history is available offline on the technician app for a full shift and reconciles on sync | Offline test with 20 technicians over five shifts |
| AC-11 | Serial-controlled part consumption always writes a genealogy row; a job cannot close without one | Negative test |
| AC-12 | Reverse genealogy resolves every asset carrying a given part serial or batch in ≤ 500 ms | Performance and correctness test, including a scripted recall |
| AC-13 | Entitlement resolution returns the governing coverage and its selection reason for an asset with four overlapping entitlements | Scripted scenario across M08, M09 and M13 |
| AC-14 | A claim evidence pack assembles completely and is accepted by at least three brand partners | Signed brand acknowledgements |
| AC-15 | A repeat fault within the rework window is flagged at intake, before the order is created | Scripted scenario |
| AC-16 | A 400-line estate loads, validates, resolves against existing assets and commits or rejects as a set with a line-level report | Scripted bulk load including deliberate rejects |
| AC-17 | Estate reconciliation produces gaps, strays and movements, and is accepted by at least three corporate clients | Signed client acknowledgements |
| AC-18 | An asset cannot be released from custody without condition grade, photographic evidence and accessory reconciliation | Negative test |
| AC-19 | Cost, margin and internal notes are absent from every P01, P04 and P08 response payload | Automated payload inspection across all external endpoints |
| AC-20 | Registry completeness reaches > 95% and identification-without-manual-entry > 90% by Wave 8 | Twelve consecutive monthly data-quality reports |
| AC-21 | All front-desk, technician and customer-facing asset screens are complete in Bengali | Translation coverage report (AS-12) |
| AC-22 | Service Operations Director and Quality Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 22 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | How many distinct devices exist in the legacy order-tracking system, and what proportion carry a usable serial? This determines the size of the provisional burn-down. | CTO / Service Operations Director | W1 minus 2 months |
| Q-02 | Is the twelve-month provisional-clearance programme accepted as a business commitment, with named branch responsibility? | Operations Director / CEO | W1 |
| Q-03 | Which brands expose a warranty-lookup interface by serial or service tag, and on what terms? Which require manual or file-based verification? | Warranty Claims Officer / CCO | W2 design |
| Q-04 | What is the rework window — 30 days per BR-SRM-016, or per service type and device family? | Quality Manager | W2 build |
| Q-05 | What is the automatic identity-resolution confidence threshold, and who owns the false-match review? | Quality Manager / CTO | W2 build |
| Q-06 | Is an asset-tag labelling programme approved, including tag stock, printers at 51+ branches, and the labour to apply tags at intake? | Branch Operations Lead / Procurement | W2 minus 2 months |
| Q-07 | Which corporate clients have declared estates today, in what format, and who confirms them? | Account Managers / CCO | W2 |
| Q-08 | What is the coverage-priority order when manufacturer warranty, AMC and a protection plan all apply? | CCO / Finance Director | W2 design |
| Q-09 | Is customer self-registration of devices through P01 permitted, and what verification is required before such a record is treated as confirmed? | CCO / Quality Manager | W2 design |
| Q-10 | What is the retention period for asset photographs and condition evidence, given storage cost at 250,000 jobs per month? | Quality Manager / CFO | W2 build |
| Q-11 | Does the Company accept devices for service without any recoverable identifier, and if so under what liability terms? | Operations Director / Legal | W2 build |
| Q-12 | Which fault taxonomy is authoritative — an existing internal list, a brand-mandated code set, or a new one built with M23 and M61? | Quality Manager | W2 design |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3 (M17 versus M45), §4 (why IoT is separate), §5 (boundary map),
§7 (category KPIs), §9 (risks) ·
`M45_Enterprise_Asset_and_Test_Equipment.md` · `M46_Fleet_and_Vehicle_Management.md` ·
`M47_Facility_Branch_Infrastructure_and_Workplace.md` ·
`M48_IoT_Telemetry_and_Predictive_Maintenance.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` §3, §12 ·
`03_Modules/A_Service_Delivery_and_Operations/M04_Branch_and_Front_Desk_Operations.md` §3 ·
`03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md` §3 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M37_Product_and_Service_Catalogue_Management.md` §3 ·
`03_Modules/D_Circular_and_Asset_Based_Business/M13_Rental_and_Equipment_as_a_Service.md` §3, §9 BRU-RNT-17 ·
`03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md` §3, §12 ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 (AS-01, AS-03, AS-08, AS-12, AS-13, AS-14) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category F ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 (CD-075…079) ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §M17 AST ·
`05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §M17 AST ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §1, §5, §6 SOD-10 ·
`00_Governance_and_Charter/00-03_Scope_Expansion_Delta_v1_to_v2.md` §M17

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-CRM-002, BR-CRM-007,
BR-SRM-005, BR-SRM-006, BR-SRM-016, BR-SRM-020, BR-FSM-016, BR-CWM-001, BR-CWM-005, BR-CWM-008,
BR-INV-005, BR-INV-009 ·
`1000FiX_Services_Company_Profile.md` §Core Services, §Authorized Service Partnerships,
§Quality & Certification, §Digital Presence

**External benchmark**
[SAP S/4HANA Technical Objects — equipment and functional location](https://help.sap.com/docs/SAP_S4HANA_CLOUD/2dfa044a255f49e89a3050daf3c61c11/5f293f33b16b40b381d6d09063887c15.html) —
equipment as an autonomous maintainable object installable at a location for a period ·
[SAP Functional Location](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/9a02a02d849d4b38a7320d94a71d2a22/8429a8846102407a9a4489860ae421e8.html) ·
[SAP equipment and serial numbers](https://learning.sap.com/courses/exploring-business-processes-in-sap-s-4hana-asset-management/using-equipment-and-serial-numbers_edd6b2ef-0a26-4eb9-8e0b-b1f8ee03e41c-1) ·
[SAP equipment replication to Service Cloud](https://userapps.support.sap.com/sap/support/knowledge/en/3517827) —
installed base for after-sales service ·
[PTC ServiceMax Installed Base Management](https://www.ptc.com/en/technologies/service-lifecycle-management/installed-base-management) —
asset history, location and components at customer sites ·
[ServiceMax Asset 360](https://www.ptc.com/en/products/servicemax/asset-360) and
[ServiceMax Core](https://www.ptc.com/en/products/servicemax/core) — offline installed-base
access and the automated entitlement engine validating warranty and contract coverage ·
[ServiceMax Installed Product Management — 360° asset view](https://twopirconsulting.com/blog/servicemax-installed-product-management-360-asset-view/) —
tracking by serial, batch or product number ·
[Microsoft Dynamics 365 Field Service customer assets](https://learn.microsoft.com/en-us/dynamics365/field-service/customer-assets) —
parent/child sub-asset hierarchy ·
[GSMA IMEI structure — TAC, serial and Luhn check digit](https://www.emnify.com/blog/imei-number) ·
[IMEI structure validation and TAC lookup](https://hicelltek.com/en/tac-lookup/) ·
[Duplicate IMEI as a fraud indicator](https://www.phonecheck.com/blog/fake-imei-numbers-how-to-detect-fraudulent-devices-before-you-buy-or-resell) ·
[Duplicate-identifier rejection in asset registries](https://support.gpsgate.com/hc/en-us/articles/14955277207196-Understanding-IMEI-Duplicate-Error-in-GpsGate) ·
ISO 9001:2015 clause 8.5.2 — identification and traceability

---

*Module M17 · Category F · 1000FiX ERP System v2.0 · CONFIDENTIAL*
