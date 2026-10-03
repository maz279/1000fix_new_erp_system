---
id: FIX-ERP2-M37
module_id: M37
module_code: CAT
module_name: Product & Service Catalogue Management
category: C — Commercial, Pricing & Revenue
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Commercial Squad
priority: P0
wave: W1
---

# M37 — Product & Service Catalogue Management
### Category C · Code `CAT` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M37 |
| **Module code** | `CAT` |
| **Category** | C — Commercial, Pricing & Revenue |
| **Status** | ★ New — created in v2.1 after enterprise benchmarking identified that no module owned the definition of a sellable item |
| **Priority** | **P0** — nothing can be sold, quoted, contracted or repaired without it |
| **Delivery wave** | W1 (Months 1–4) |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `product`, `uom`) + L2 (OCA `product_variant_*`, `product_attribute_*`) + L5 (custom) |
| **Custom modules** | `cd_catalogue`, `cd_repair_bom`, `cd_service_product`, `cd_fault_taxonomy`, `cd_catalogue_publish` |
| **Requirement range** | FR-CAT-001 … FR-CAT-046 |
| **Requirement count** | **46** *(measured; the register's pre-specification estimate was 34)* |
| **Effort estimate** | **24 person-weeks** *(measured; register estimate 18 PW)* |
| **Depends on** | M29 Identity · M28 Integration · M30 Platform Admin · M64 Master Data Management |
| **Depended on by** | M01, M02, M07, M08, M09, M10, M11, M12, M13, M14, M15, M16, M17, M20, M25, M26, M31, M36, M38, M39, M41, M43, M45, M51, M53, M61, M64 — **27 modules** |

> **Register note.** Under rule RG-01 the register entry existed before this specification was
> written. The measured requirement count and effort exceed the pre-specification estimate by
> 35% and 33% respectively, consistent with the 23% correction factor observed in Category A.
> `02-02` §3 must be restated when all nine Category C specifications are complete.

---

## 2. Purpose

M37 is the **definition of everything 1000FiX can sell, quote, contract, repair, rent, refurbish
or recycle**. It is the noun catalogue of the business: a service, a spare part, an accessory, a
repair kit, an AMC package, a protection plan, a rental SKU, a refurbished device grade, a
managed-service tier, a data-recovery class, a recycling service — each defined once, in one
place, with one identifier, one description, one unit of measure and one set of applicability
rules.

It carries **no price**. A price is a commercial decision that changes with customer, channel,
season and negotiation; a definition is a fact about the offering. Separating the two is the
single most important structural decision in Category C, and it is why M37 exists as a module
rather than as a table inside M11.

### Why It Exists

Today "what we sell" is not written down anywhere authoritative. Service names differ between
branches, between the price list and the invoice, and between the website and the job sheet.
The same repair is called four things in four places. There is no standard repair time, so
labour is estimated by feel; there is no repair bill of material, so parts are picked from
memory; there is no fault taxonomy, so warranty claims are rejected for inconsistent coding.

The v1.0 plan had no catalogue module at all. Benchmarking against SAP *Product Master* /
*Service Product*, Oracle *Product Hub*, and Dynamics 365 *Product Catalog* showed that every
comparable enterprise treats the catalogue as a **P0 foundation delivered before any selling
module**. M37 was created to close that gap. Fourteen revenue streams cannot be run from an
undefined product set.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.11 (BR-SLS-*) | Rate cards and service pricing presuppose a defined service list that does not exist |
| ERP BRD §10.1 BRU-SRM-01 | A service order requires an identified device and a classified service — both catalogue objects |
| ERP URD §7 (US-SLS-*, US-INV-*) | Agents and storekeepers require searchable, unambiguous item lookup |
| Company Profile §Core Services | The service families 1000FiX publicly commits to deliver |
| Business Plan §Service Portfolio, §RAMC Packages | Six residential AMC packages, five mobile/appliance service products, six managed-service tiers — all requiring formal definition |
| Business Plan §Rental, §Refurbishment | Rental asset categories and refurbished grade bands |
| Service App SOW §Service Selection | "The app should show service categories and sub-categories with description and indicative price" — the app consumes a published catalogue |
| Integrated Portal Roadmap §Catalogue Sync | Website and app must render from a single catalogue source |
| `02-02` Module Catalogue Master Register §2 Category C | Registers M37 as P0, W1, CCO-owned |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree. Where this
> table assigns a capability to another module, that module's specification must claim it.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The unified item master covering every sellable and serviceable thing: service, part, accessory, kit, plan, subscription, rental SKU, refurbished grade, recycling service, digital service |
| 2 | Item type taxonomy and the typed extension model that lets one core object carry fourteen revenue streams |
| 3 | Service product definition: scope of work, inclusions, exclusions, prerequisites, standard duration, required skill level, required certification, applicable delivery modes |
| 4 | **Repair bill of material (rBOM)** — the standard parts, consumables and quantities for a defined repair operation on a defined model |
| 5 | **Standard repair time (SRT)** — the labour time allowance per operation, per model, per repair level |
| 6 | Repair operation catalogue: the named, coded operations a technician can perform |
| 7 | Kits and bundles: composition, substitution rules, explosion behaviour at quotation and at issue |
| 8 | Product hierarchy: category → sub-category → family → item, with unlimited depth and a single active tree |
| 9 | Attribute and variant model: attributes, attribute sets, allowed values, variant generation, variant-level identity |
| 10 | Brand, model and device-category master — the reference spine linking devices, parts, services and claims |
| 11 | **Fault, symptom and root-cause taxonomy** — the coding system consumed by M01, M09, M23 and M26 |
| 12 | Part identity: manufacturer part number, OEM cross-reference, alternates, supersessions, interchangeability |
| 13 | Contract product family definitions (14 families) and protection product definitions (7 families) as catalogue templates |
| 14 | Rental SKU definitions and refurbished grade bands (A / B / C / D) with grade criteria |
| 15 | Item applicability rules: which items may be sold on which channel, in which branch, to which customer segment, in which entity |
| 16 | Unit-of-measure master, UoM categories and conversion factors |
| 17 | Tax classification per item (VAT rate class, SD applicability, HS code) — the classification, not the calculation |
| 18 | Revenue-recognition classification per item (point-in-time, over-time, usage-based) — the classification, not the posting |
| 19 | Item lifecycle: draft → review → active → restricted → discontinued → obsolete, with governed transitions |
| 20 | Multilingual item content: Bengali and English name, short description, long description, customer-facing wording |
| 21 | Digital assets: images, diagrams, datasheets, service manuals, safety notes — reference and publication |
| 22 | Catalogue publication: the versioned, channel-specific projections consumed by portals, apps, marketplace and print |
| 23 | Catalogue search and the item-resolution API used at intake, quotation, procurement and billing |
| 24 | Catalogue governance: approval workflow, change history, effective dating, deprecation notice periods |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Any price, rate, cost or discount | **M11** Pricing | A price is a commercial decision with its own validity, currency and customer applicability. A catalogue item never carries a price field |
| Standard cost and valuation | **M15** Inventory | Cost is an inventory and accounting property, not a definitional one |
| Stock levels, reservation, movement, lot and serial tracking | **M15** Inventory / **M41** Warehouse | The catalogue defines what a part *is*; inventory knows where it is and how many |
| Vendor part numbers, sourcing and lead times | **M16** Procurement / **M42** Supplier | Sourcing is a supplier relationship, not an item definition |
| The individual customer device and its history | **M17** Asset Registry | The catalogue defines the *model*; M17 tracks the *instance* |
| The quotation document that selects catalogue items | **M36** Quotation | A quotation is a commercial instrument with legal weight |
| Contract terms, entitlements and covered assets | **M08** Contract | M37 supplies the contract *product template*; M08 instantiates the agreement |
| Warranty entitlement and claim | **M09** Warranty | M37 defines the protection *product*; M09 sells, honours and claims it |
| Billing schedule, proration and MRR mechanics | **M39** Subscription | M37 defines the plan; M39 turns it into money owed |
| Storefront merchandising, SEO copy, promotions, cart | **M38** E-Commerce | M38 consumes a published catalogue and decorates it for selling |
| Marketplace seller listings | **M12** Marketplace | A seller listing references the catalogue taxonomy; it is not a catalogue item |
| Tax rate values and return filing | **M51** Tax | M37 classifies; M51 rates and files |
| Revenue-recognition posting and schedules | **M53** Revenue & Settlement | M37 classifies; M53 posts |
| Quality checklist content | **M23** Quality | Checklists are quality artefacts referencing catalogue operations |
| Knowledge articles and repair guides | **M61** Knowledge Management | M37 links to them; it does not author them |
| Master-data workflow engine, survivorship and golden-record rules | **M64** MDM | M64 provides the governance machinery; M37 is its largest tenant |

### 3.3 Shared Concepts

| Concept | M37's Role | Owning Module |
|---|---|---|
| Item / product | **Owner** — defines identity, attributes, lifecycle | M37 |
| Price | Never stored; resolved by request | M11 |
| Standard cost | Referenced for margin display only | M15 |
| Brand and model | **Owner** of the master; M17 references per device | M37 |
| Fault code | **Owner** of the taxonomy; M01 assigns per order | M37 |
| Repair operation | **Owner**; M31 and M02 execute | M37 |
| rBOM | **Owner**; M31 consumes at repair planning; M15 issues against it | M37 |
| Contract product family | **Owner** of the template; M08 owns the instance | M37 |
| Protection product | **Owner** of the definition; M09 owns the policy | M37 |
| UoM | **Owner**; every module converts through it | M37 |
| Tax class | **Owner** of the assignment; M51 owns the rate | M37 |
| Published catalogue | **Owner** of the projection; M38, M12, P01, P04, P07 consume | M37 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA** — Product Master, Service Product Master, Service Bill of Material | A single material master with views (basic, sales, purchasing, accounting) and a separate service-product type carrying duration and resource requirements | The **views concept** — one item, many functional facets, each governed by a different owner; and the separation of service product from material | SAP's material-type proliferation and industry-sector coupling; unnecessary at our item volume |
| **SAP Condition Technique** (contrast) | Prices live entirely outside the product master | **Adopted as an absolute rule** — no price field on any catalogue object | — |
| **Oracle Fusion Cloud — Product Hub** | Item classes, attribute groups, item rules, new-item request workflow, publication to spokes | The **item class + attribute group** model, the **new-item request** governance workflow, and **publication to downstream spokes** as a first-class function | Oracle's full data-quality scoring engine; M64 provides a lighter equivalent |
| **Microsoft Dynamics 365** — Product Catalog, Product Families, Bundles, Kits | Product family inheritance, bundles with required/optional lines, unit groups | Family-level attribute inheritance and the **bundle with optional lines** pattern used for AMC packages and protection add-ons | Dataverse-specific product-relationship modelling |
| **IFS Cloud** — Service Catalogue, Standard Jobs, Maintenance BOM | Standard job with predefined tasks, materials, tools, skills and duration | The **standard job** concept in full — this is the direct ancestor of our repair operation + rBOM + SRT triple | IFS's plant-maintenance orientation (work-centre routing) |
| **Automotive labour-time guides** (Mitchell / Alldata / Haynes class) | Published flat-rate labour times per operation per model | The **flat-rate principle**: quote and pay against a published standard time, not against a guess | Buying a third-party time guide — no such product covers Bangladeshi mobile, appliance and IT repair; 1000FiX must build its own from measured M01/M31 data |
| **PIM platforms** (Pimcore / Akeneo class) | Multi-channel, multi-locale content enrichment and channel-specific publication | **Channel-specific publication with completeness scoring** — an item cannot be published to a channel until that channel's required attributes are complete | A separate PIM product; the L6 licence cost is not justified at our SKU count |
| **Odoo 19 + OCA** — `product`, `uom`, `product_variant_configurator`, `product_attribute_value_menu` | Product template/variant, attribute lines, UoM categories | The **template/variant** foundation and UoM engine as the L1/L2 base | Odoo's assumption that `list_price` lives on the product — this field is disabled and its use is blocked by test |

**Design position.** 1000FiX differs from the benchmarks in four deliberate ways.

First, **one catalogue spans fourteen revenue streams**. SAP and Oracle would model rental,
refurbishment, subscription and marketplace items in separate masters. We model one core item
with typed extensions, because a refurbished laptop must be able to appear in a quotation
alongside a repair service and an AMC plan without three integration layers between them.

Second, **the repair bill of material and standard repair time are first-class catalogue
objects, not workshop configuration**. This is the mechanism that converts repair from craft to
process: it makes estimates consistent, makes technician performance measurable against a
standard rather than an opinion, and makes warranty claims defensible to brand partners.

Third, **the catalogue is bilingual at the definition level, not the presentation level**. The
Bengali customer-facing name of a service is a governed attribute with its own approval, not a
translation string, because it appears on a legal invoice and a signed job sheet.

Fourth, **1000FiX must generate its own standard times**. No purchasable labour-time guide
covers this market or this device mix. M37 therefore ships with a *provisional* SRT set and a
feedback loop from M01/M31 actuals, with M26 recalibrating quarterly. This is stated as a
programme risk, not hidden as an assumption.

---

## 5. Functional Areas & Features

### 5.1 Item Master & Taxonomy

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAT-001 | Unified item master | Maintain a single item master in which every sellable or serviceable thing — service, part, accessory, kit, plan, rental SKU, refurbished unit, subscription, recycling service — exists as one record with one permanent identifier | P0 | L1 |
| FR-CAT-002 | Item typing | Classify every item by item type, and drive the visible fields, mandatory attributes, lifecycle and downstream behaviour from that type without code change | P0 | L5 |
| FR-CAT-003 | Typed extensions | Hold type-specific attributes in typed extension records (service, part, plan, rental, refurbished, digital) rather than as nullable columns on the core item | P0 | L5 |
| FR-CAT-004 | Product hierarchy | Maintain a category → sub-category → family → item hierarchy of unlimited depth, with exactly one active commercial tree and any number of alternate presentation trees | P0 | L1 |
| FR-CAT-005 | Attribute sets | Define attributes and attribute sets per item class, with data type, allowed values, unit, mandatory flag and per-channel requirement | P0 | L2 |
| FR-CAT-006 | Variants | Generate variants from attribute combinations, each with its own identifier, barcode and independent lifecycle state | P1 | L1 |
| FR-CAT-007 | Item numbering | Generate item codes from a configurable, type-aware mask with no gaps and no reuse, and preserve legacy codes as searchable aliases | P0 | L5 |
| FR-CAT-008 | Bilingual content | Hold Bengali and English name, short description, long description and customer-facing wording as governed, separately approvable attributes | P0 | L5 |
| FR-CAT-009 | Unit of measure | Maintain UoM categories, base units, conversion factors and per-item purchase / stock / sales units with automatic conversion at every boundary | P0 | L1 |
| FR-CAT-010 | Barcode and identifier registry | Register EAN, UPC, internal barcode, QR payload and manufacturer part number against an item, and resolve any of them to the item in one call | P1 | L2 |
| FR-CAT-011 | Universal catalogue search | Search the catalogue by code, name, alias, barcode, attribute, brand, model or free text in Bengali and English, returning ranked results in under 300 ms | P0 | L5 |
| FR-CAT-012 | Item cloning | Create a new item from an existing one, copying selected facets, with mandatory review before activation | P2 | L1 |

### 5.2 Service Product Definition

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAT-013 | Service product record | Define each service with scope of work, explicit inclusions and exclusions, prerequisites, deliverables and customer-facing description in both languages | P0 | L5 |
| FR-CAT-014 | Delivery mode applicability | Declare which of the nine delivery modes each service supports — walk-in, on-site, pick & drop, workshop, remote, managed, rental service, data service, marketplace | P0 | L5 |
| FR-CAT-015 | Skill and certification requirement | Declare the minimum repair level, skill profile and brand certification required to perform a service, for dispatch gating in M02 and M31 | P0 | L5 |
| FR-CAT-016 | Standard duration | Hold a standard duration per service per delivery mode, used for appointment sizing, capacity planning and SLA derivation | P0 | L5 |
| FR-CAT-017 | Service dependency | Declare prerequisite services, mutually exclusive services and recommended companion services | P2 | L5 |
| FR-CAT-018 | Warranty-on-service default | Declare the default repair-warranty period per service and repair level, consumed by M01 at handover | P1 | L5 |
| FR-CAT-019 | Consent and compliance flags | Flag services requiring explicit customer consent, data-handling declaration, hazardous-material handling or regulatory certification | P1 | L5 |
| FR-CAT-020 | Service-level template | Declare the default SLA template per service, which M08 may override contractually | P1 | L5 |

### 5.3 Repair Operations, rBOM & Standard Times

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAT-021 | Repair operation catalogue | Maintain a coded catalogue of repair operations — the named, discrete actions a technician performs — scoped by device category | P0 | L5 |
| FR-CAT-022 | Repair bill of material | Define, per operation per model, the standard parts and consumables with quantities, criticality and permitted alternates | P0 | L5 |
| FR-CAT-023 | Standard repair time | Hold a standard labour-time allowance per operation, per model, per repair level, with an effective-dated version history | P0 | L5 |
| FR-CAT-024 | SRT calibration feed | Accept measured actual durations from M01 and M31, present variance against standard, and support governed re-baselining of the SRT | P1 | L5 |
| FR-CAT-025 | Operation-to-fault mapping | Map fault codes to the repair operations that typically resolve them, to drive estimate pre-population in M36 | P1 | L5 |
| FR-CAT-026 | Tooling and equipment requirement | Declare the test equipment, tools and workstation class required by an operation, consumed by M31 bench allocation and M45 | P2 | L5 |
| FR-CAT-027 | Repair level classification | Classify every operation as Level 1 (basic), Level 2 (component) or Level 3 (board / micro-soldering) | P0 | L5 |
| FR-CAT-028 | rBOM explosion | Explode an rBOM into estimate lines at quotation and into requisition lines at execution, honouring alternates and stock availability signals from M15 | P0 | L5 |

### 5.4 Part, Brand & Model Master

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAT-029 | Part definition | Define spare parts and accessories with specification, manufacturer part number, OEM reference, physical attributes and handling class | P0 | L1 |
| FR-CAT-030 | Cross-reference and alternates | Maintain OEM ↔ aftermarket cross-references, approved alternates and compatibility with brand/model, with a directional quality note | P0 | L5 |
| FR-CAT-031 | Supersession chain | Record part supersession with effective date and automatically resolve a superseded part to its successor at every point of use | P1 | L5 |
| FR-CAT-032 | Brand and model master | Maintain the brand, model, model-year and device-category master, including authorised-service status per brand | P0 | L5 |
| FR-CAT-033 | Model compatibility matrix | Declare which parts and operations apply to which models, and block incompatible selection at estimate and issue | P0 | L5 |
| FR-CAT-034 | Genuine / OEM / aftermarket grading | Classify every part by provenance grade and surface that grade on every customer-facing document | P0 | L5 |
| FR-CAT-035 | Hazardous and restricted classification | Flag batteries, refrigerants and other restricted items with handling, storage, transport and disposal constraints consumed by M03, M41 and M18 | P1 | L5 |

### 5.5 Commercial Product Templates

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAT-036 | Contract product templates | Define all fourteen contract product families as templates carrying default scope, entitlement structure, visit schedule, SLA and covered-asset rules, consumed by M08 | P0 | L5 |
| FR-CAT-037 | Protection product definitions | Define the seven protection product families with coverage scope, exclusions, term, claim limits and eligibility rules, consumed by M09 | P0 | L5 |
| FR-CAT-038 | Subscription plan definitions | Define subscription plans with billing frequency, commitment term, included quantities and overage units, consumed by M39 | P1 | L5 |
| FR-CAT-039 | Rental SKU definitions | Define rental SKUs with asset class, minimum hire period, deposit basis, condition standard and return criteria, consumed by M13 | P2 | L5 |
| FR-CAT-040 | Refurbished grade bands | Define grade bands A–D with objective cosmetic and functional criteria, warranty implication and permitted sales channels, consumed by M14 and M38 | P2 | L5 |
| FR-CAT-041 | Bundles and kits | Define bundles with required and optional lines, substitution rules and explosion behaviour, so an AMC package or a repair kit is one selectable thing | P1 | L2 |

### 5.6 Classification, Publication & Governance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CAT-042 | Fault and symptom taxonomy | Maintain the symptom → category → sub-category → fault code → root-cause taxonomy in both languages, versioned, with brand-specific code mapping for claims | P0 | L5 |
| FR-CAT-043 | Tax and revenue classification | Assign a VAT class, SD applicability, HS code and revenue-recognition pattern to every item, and block activation where any is absent | P0 | L5 |
| FR-CAT-044 | Channel applicability and publication | Publish channel-specific, versioned catalogue projections to portal, app, corporate portal, marketplace, POS and print, with per-channel completeness scoring that blocks incomplete publication | P0 | L5 |
| FR-CAT-045 | Item lifecycle governance | Enforce the item lifecycle with an approval workflow, effective dating, a deprecation notice period, and a hard block on deleting any item ever transacted | P0 | L5 |
| FR-CAT-046 | Change history and impact preview | Maintain full attribute-level change history, and before any change is committed show which contracts, quotations, listings, subscriptions and open orders reference the item | P1 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

Engineering behaviours the module must exhibit. Not user-visible; decisive for production
survival.

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Read-optimised projection** | The catalogue is read thousands of times per write. Every consumer reads a denormalised, versioned projection, never the normalised master |
| T-02 | **Immutable identity** | An item's internal identifier is permanent. Renaming, re-coding and re-categorising never break a historical document reference |
| T-03 | **Effective-dated attributes** | Every commercially significant attribute is effective-dated; a document raised in the past resolves the definition that was true then |
| T-04 | **No price field** | The schema contains no price, cost, discount or margin column on any catalogue object. Enforced by migration test, not by convention |
| T-05 | **Bitemporal audit** | Attribute changes are recorded with both valid-time and transaction-time, so "what did the catalogue say on 3 March" is answerable |
| T-06 | **Bulk load pipeline** | Bulk create and update of 50,000 items with staged validation, per-row error reporting, dry-run and atomic commit or rollback |
| T-07 | **Search index** | A dedicated search index over code, alias, barcode, Bengali and English text with GIN trigram support; index lag under 5 seconds after publication |
| T-08 | **rBOM explosion performance** | A three-level rBOM explosion with alternate resolution completes in ≤ 120 ms p95 |
| T-09 | **Publication as an event** | Each publication emits a versioned `catalogue.published` event carrying a content hash, so consumers can detect and reconcile drift |
| T-10 | **Idempotent sync** | Consumers may replay any publication version safely; publication is a full-state snapshot plus a delta, never a delta alone |
| T-11 | **Referential guard** | Deletion is impossible for any item referenced by a transaction, contract, subscription or listing; discontinuation is the only route |
| T-12 | **Localisation integrity** | Bengali content is UTF-8 with ICU collation; an item cannot be published to a customer channel with an untranslated customer-facing field |
| T-13 | **Attribute schema evolution** | New attributes and attribute sets are added by configuration without migration or downtime |
| T-14 | **Concurrency** | Optimistic locking on the item record; concurrent edits to different facets of the same item do not conflict |
| T-15 | **Performance envelope** | Item read ≤ 80 ms p95 · search ≤ 300 ms p95 · publication of the full catalogue ≤ 4 minutes · API availability 99.95% |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M37 |
|---|---|---|
| **Service centre agent** | Types a free-text service description; every agent words it differently; the invoice never matches the job sheet | Selects a defined service in two keystrokes; the wording on job sheet, quotation and invoice is identical by construction |
| **Technician** | Decides which parts a repair needs from memory; requests them one at a time | Opens the repair operation and sees the standard parts list; requisitions the whole rBOM in one action |
| **Workshop supervisor** | Cannot say whether a four-hour repair was slow or normal | Compares actual against standard repair time on every job |
| **Estimator / quotation officer** | Rebuilds every estimate from scratch | Estimate pre-populates from fault code → operation → rBOM → SRT; only exceptions need thought |
| **Inventory manager** | Holds parts under inconsistent names and duplicate codes | One part, one code, with alternates and supersessions declared |
| **Warranty officer** | Claims rejected by brands for non-standard fault coding | Submits brand-mapped fault codes generated automatically from the taxonomy |
| **Account manager** | Describes an AMC package differently in every proposal | Selects a contract product template; scope and entitlements are identical every time |
| **Marketing / digital** | Maintains the website service list by hand, permanently out of date | Website, app and marketplace render from the published catalogue; changes propagate in minutes |
| **Finance officer** | Applies VAT by judgement per line | Every item carries its tax class; VAT is deterministic |
| **CCO** | Cannot answer "what do we actually sell, and where?" | Sees the full offer set with channel coverage and completeness on one screen |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Estimate accuracy and speed** | Fault → operation → rBOM → SRT pre-population removes the blank-page estimate | Enables the M36 target of **< 2 h quotation turnaround** and the **> 78% conversion** KPI |
| **Margin protection on paid repair** | Standard times and standard parts remove the systematic under-quoting caused by guesswork | A material component of the **+4 percentage-point gross-margin** target owned by M11 |
| **Warranty claim acceptance** | Standardised, brand-mapped fault coding and evidence of standard parts removes the largest single rejection cause | Directly supports the **> 92% claim approval** target and the **BDT 100 lac/year** recovery owned by M09 |
| **Parts requisition efficiency** | rBOM explosion replaces item-by-item requests | Reduces parts-related job holds; supports the M15 availability targets |
| **Catalogue maintenance labour** | One definition published to six channels replaces six hand-maintained lists | Removes an estimated 1.5 FTE-equivalent of recurring content maintenance across commercial and marketing |
| **Duplicate and dead SKU elimination** | One item master with duplicate detection at creation | Reduces the inventory carrying cost of duplicate part codes; feeds the M15 **BDT 34 lac/year** inventory benefit |
| **Revenue-stream enablement** | Rental, refurbishment, subscription and marketplace items cannot exist without definitions | **Precondition** for the BDT 48 + 65 + 84 lac/year benefits attributed to M13, M14 and M12 |

> **Discipline note.** M37 is an enabling module. Except where stated, it does not *realise*
> benefit itself; it makes other modules' benefits achievable. No standalone monetary figure
> should be carried into the business case for M37, and none is claimed here.

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **A common vocabulary** | 51+ branches stop using different words for the same work. Training, reporting and comparison become possible for the first time |
| **Repair as a process, not a craft** | Standard operations and times convert tacit technician knowledge into institutional knowledge that survives resignation |
| **Audit and certification defensibility** | ISO 9001 requires defined, controlled processes; a governed operation catalogue with change history is direct evidence |
| **Brand partner credibility** | Authorised-service status is retained by demonstrating standard procedures and coding — the catalogue is the artefact that proves it |
| **Analytical foundation** | Every M25 comparison and every M26 model — duration prediction, parts forecasting, fault classification — requires a stable taxonomy. Without M37 they cannot be built |
| **Change capability** | A new service line becomes a catalogue entry with an approval, not a software project |
| **Regulatory readiness** | Item-level tax classification and HS coding make NBR VAT and import compliance mechanical rather than interpretive |

---

## 8. Lifecycle & State Model

M37 owns the **item lifecycle**. Every catalogue object follows it.

```
              ┌──────────┐
              │  DRAFT   │  created; not visible outside the catalogue team
              └────┬─────┘
                   │ submit for review (completeness rules evaluated)
              ┌────▼─────┐
              │ IN REVIEW│──── reject ──► back to DRAFT (with reason)
              └────┬─────┘
                   │ approve (CCO or delegate; tax + revenue class mandatory)
              ┌────▼─────┐
     ┌───────►│  ACTIVE  │  sellable, quotable, contractable, stockable
     │        └────┬─────┘
     │             │
     │        ┌────▼───────────┐  sellable to existing customers /
     │        │   RESTRICTED   │  named channels only; new sale blocked
     │        └────┬───────────┘
     │             │ discontinue (notice period starts)
     │        ┌────▼───────────┐
     │        │ DISCONTINUED   │  no new sale; existing contracts honoured;
     │        └────┬───────────┘  service and parts still supportable
     │             │ end of support commitment
     │        ┌────▼───────────┐
     │        │   OBSOLETE     │  historical reference only
     │        └────────────────┘
     │
     └──── reactivate (approval + reason; new version created)

  Deletion does not exist for any item that has ever been referenced.
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Draft | In Review | All mandatory attributes for the item class complete; Bengali and English customer-facing names present | Catalogue Officer |
| In Review | Active | Tax class, revenue class and hierarchy assigned; duplicate check passed; approver is not the author | CCO or delegate |
| In Review | Draft | Rejection reason recorded | Reviewer |
| Active | Restricted | Restriction reason and permitted channels/customers declared | Catalogue Officer + CCO |
| Active / Restricted | Discontinued | Successor item declared or explicit "no successor" justification; notice period set | CCO |
| Discontinued | Obsolete | No open contract, subscription, listing or order references the item | System (scheduled evaluation) |
| Discontinued | Active | Reactivation approval with reason; a new effective-dated version is created | CCO |
| Any | *Deleted* | **Impossible** where any reference exists (BRU-CAT-03) | — |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-CAT-01 | No catalogue object may hold a price, cost, discount or margin value | **H** | CCO |
| BRU-CAT-02 | An item cannot become Active without a tax class, a revenue-recognition class and a position in the commercial hierarchy | **H** | CFO |
| BRU-CAT-03 | An item that has ever been referenced by a transaction, contract, subscription or listing can never be deleted — only discontinued | **H** | CTO |
| BRU-CAT-04 | An item cannot be published to a customer-facing channel without complete Bengali and English customer-facing content | **H** | CCO |
| BRU-CAT-05 | The approver of an item change may not be its author | **H** | CCO |
| BRU-CAT-06 | A repair operation cannot be Active without a repair level, a required skill profile and a standard repair time | **H** | Quality Manager |
| BRU-CAT-07 | An rBOM line may reference only parts compatible with the operation's declared models | **H** | Quality Manager |
| BRU-CAT-08 | A superseded part automatically resolves to its successor at every point of use; the superseded code remains searchable forever | **C** | Inventory Manager |
| BRU-CAT-09 | Discontinuation requires a declared successor or a recorded justification for having none | **A** | CCO |
| BRU-CAT-10 | A discontinued item remains fully serviceable for the life of every contract that covers it | **H** | CCO |
| BRU-CAT-11 | Standard repair times may be re-baselined only through the governed calibration workflow, never edited in place | **H** | Ops Director |
| BRU-CAT-12 | Any change to an Active item's scope, inclusions or exclusions creates a new effective-dated version; it never overwrites history | **H** | CCO |
| BRU-CAT-13 | Duplicate detection on name, code, barcode and manufacturer part number runs before an item may leave Draft | **C** | Catalogue Officer |
| BRU-CAT-14 | An item restricted from a channel cannot be listed, quoted or sold on that channel by any route, including API | **H** | CCO |
| BRU-CAT-15 | Hazardous-classified items carry mandatory handling, transport and disposal constraints that downstream modules cannot override | **H** | Quality Manager |
| BRU-CAT-16 | A contract product template in use by an active contract cannot be structurally changed; a new template version is required | **H** | CCO |

*Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.catalogue.item` | `fix_catalogue_item` | The universal item master | code, item_type, name_en, name_bn, category_id, uom_id, state, tax_class_id, revenue_class, effective_from, effective_to |
| `fix.catalogue.category` | `fix_catalogue_category` | Hierarchy nodes | parent_id, code, name_en, name_bn, tree_type, sequence |
| `fix.catalogue.attribute` | `fix_catalogue_attribute` | Attribute definitions | code, data_type, uom_id, allowed_values, is_variant_axis |
| `fix.catalogue.attribute.set` | `fix_catalogue_attribute_set` | Attribute sets per item class | item_type, attribute_ids, mandatory_ids, channel_required_json |
| `fix.catalogue.item.attribute` | `fix_catalogue_item_attribute` | Item attribute values | item_id, attribute_id, value, valid_from, valid_to |
| `fix.service.product` | `fix_service_product` | Service-type extension | item_id, scope, inclusions, exclusions, delivery_modes, repair_level, skill_profile_id, cert_required_id, std_duration_min, default_sla_template_id, repair_warranty_days |
| `fix.repair.operation` | `fix_repair_operation` | Coded repair operations | code, name_en, name_bn, device_category_id, repair_level, tooling_ids, hazard_flags |
| `fix.repair.bom` | `fix_repair_bom` | rBOM header | operation_id, model_id, version, state, effective_from |
| `fix.repair.bom.line` | `fix_repair_bom_line` | rBOM lines | bom_id, part_item_id, qty, uom_id, criticality, alternate_group |
| `fix.standard.repair.time` | `fix_standard_repair_time` | SRT register | operation_id, model_id, repair_level, minutes, source, confidence, version, effective_from |
| `fix.part.item` | `fix_part_item` | Part-type extension | item_id, mpn, oem_ref, provenance_grade, hazard_class, physical_attrs_json |
| `fix.part.crossref` | `fix_part_crossref` | Alternates and cross-references | part_item_id, alt_item_id, relation_type, direction, quality_note |
| `fix.part.supersession` | `fix_part_supersession` | Supersession chain | from_item_id, to_item_id, effective_from, reason |
| `fix.brand` | `fix_brand` | Brand master | code, name, authorised_service, claim_portal_ref |
| `fix.device.model` | `fix_device_model` | Model master | brand_id, model_code, device_category_id, model_year, specifications_json |
| `fix.model.compatibility` | `fix_model_compatibility` | Part/operation ↔ model matrix | model_id, item_id, operation_id, compatible, note |
| `fix.fault.taxonomy` | `fix_fault_taxonomy` | Symptom/fault/root-cause tree | parent_id, level, code, name_en, name_bn, device_category_id, version |
| `fix.fault.brand.map` | `fix_fault_brand_map` | Brand claim-code mapping | fault_id, brand_id, brand_code, brand_description |
| `fix.contract.product.template` | `fix_contract_product_template` | 14 contract families | item_id, family, entitlement_structure_json, visit_schedule_json, sla_template_id, covered_asset_rules_json, version |
| `fix.protection.product` | `fix_protection_product` | 7 protection families | item_id, family, coverage_scope, exclusions, term_months, claim_limit_json, eligibility_rules_json |
| `fix.subscription.plan.def` | `fix_subscription_plan_def` | Plan definitions | item_id, billing_frequency, commitment_months, included_qty_json, overage_uom_id |
| `fix.rental.sku` | `fix_rental_sku` | Rental definitions | item_id, asset_class_id, min_hire_period, deposit_basis, condition_standard, return_criteria |
| `fix.refurb.grade` | `fix_refurb_grade` | Grade bands A–D | code, cosmetic_criteria, functional_criteria, warranty_days, permitted_channels |
| `fix.catalogue.bundle` | `fix_catalogue_bundle` | Bundles and kits | item_id, line_ids, explode_at, substitution_rules_json |
| `fix.catalogue.publication` | `fix_catalogue_publication` | Channel projections | channel, version, content_hash, item_count, published_at, published_by |
| `fix.catalogue.change.log` | `fix_catalogue_change_log` | Bitemporal change record | item_id, attribute, old_value, new_value, valid_from, txn_time, actor_id, reason |
| `fix.uom` / `fix.uom.category` | `fix_uom`, `fix_uom_category` | UoM master | category_id, name, factor, rounding, type |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.tax.code` rate values | M51 Tax | Live read for validation display |
| `fix.stock.quant` | M15 Inventory | Live read for rBOM alternate resolution |
| `fix.standard.cost` | M54 | Live read, margin display only, never stored |
| `fix.competency`, `fix.competency` | M22 Competency | Live read for service skill requirements |
| `fix.contract.sla` | M08 Contract | Live read for default SLA assignment |
| `fix.knowledge.article` | M61 Knowledge | Reference link only |
| `fix.document` (manuals, datasheets) | M24 Document | Reference by document id |
| `fix.mdm.change.request` | M64 MDM | Governance workflow host |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-CAT-01 | Item submitted for review | Run completeness, duplicate and classification checks; attach the result to the review task | Block submission with a per-field reason list |
| AUT-CAT-02 | Item activated | Publish to every channel for which the item is applicable and complete; emit `catalogue.item_activated` | Publish to complete channels only; raise a task listing incomplete channels |
| AUT-CAT-03 | Item changed | Compute the reference impact set (contracts, subscriptions, listings, open orders, quotations) and present it before commit | Block the commit and escalate to the Catalogue Officer |
| AUT-CAT-04 | Part superseded | Re-point open requisitions and rBOM lines to the successor; notify M15 and M16 | Flag affected documents for manual review |
| AUT-CAT-05 | Nightly SRT variance scan | Compare M01/M31 actuals against standard; flag operations whose median actual deviates beyond the configured band | Log and retry next cycle |
| AUT-CAT-06 | Quarterly SRT calibration window | Open a governed re-baselining task per flagged operation with the measured distribution attached | Escalate to Operations Director |
| AUT-CAT-07 | Discontinuation date reached | Block new sale, notify M11, M36, M38, M12 and affected account managers, and generate the successor migration list | Retry; escalate after two failures |
| AUT-CAT-08 | Item referenced by a channel with missing required attributes | Withhold that channel's publication and raise a completeness task | — |
| AUT-CAT-09 | New device model registered in M17 without a catalogue model record | Create a draft model record and assign it for enrichment | Queue for manual creation |
| AUT-CAT-10 | Fault taxonomy version published | Notify M01, M09, M23 and M26; re-map open brand claim codes | Hold the version and alert the Quality Manager |
| AUT-CAT-11 | Contract product template version created | Notify M08 of the new version; existing contracts remain on their bound version | Escalate to CCO |
| AUT-CAT-12 | Bulk import completed | Produce a per-row outcome report and route failures to the owning officer | Roll back the batch atomically |

---

## 12. Interfaces

### 12.1 Upstream — M37 Consumes

| Source | What | Mechanism |
|---|---|---|
| M64 MDM | New-item request workflow, survivorship rules, governance approvals | Workflow host + API |
| M30 Platform Admin | Entity, branch, channel and language configuration | Configuration read |
| M51 Tax | Valid tax classes and HS code list | REST `GET /api/v1/tax/classes` |
| M15 Inventory | Stock availability signal for alternate resolution; standard cost for margin display | REST |
| M22 Competency | Skill profiles and certification definitions | Master data projection |
| M01 SRM · M31 WSR | Actual labour durations and parts consumed, for SRT and rBOM calibration | Warehouse extract + event `service_order.closed` |
| M17 Asset Registry | Newly encountered device models requiring catalogue registration | Event `asset.model_unknown` |
| M23 Quality | Non-conformance evidence implicating a part or operation definition | Event `quality.ncr_raised` |
| M24 Document | Manuals, datasheets, safety notices | Document reference API |

### 12.2 Downstream — M37 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M11 Pricing | The item set against which every price is defined | Master data projection |
| M36 Quotation | Items, operations, rBOM, SRT and fault→operation mapping for estimate build-up | REST + projection |
| M08 Contract | Contract product templates and covered-service definitions | REST + projection |
| M09 Warranty | Protection product definitions and the brand-mapped fault taxonomy | REST + projection |
| M39 Subscription | Subscription plan definitions | REST |
| M38 E-Commerce | Published storefront catalogue with content and media | Publication event + REST |
| M12 Marketplace | Category taxonomy and permitted listing item set | Publication event + REST |
| M01 SRM | Service definitions, fault taxonomy, delivery-mode applicability, default SLA and repair-warranty | Master data projection |
| M31 WSR · M02 FSM | Repair operations, rBOM, SRT, tooling and skill requirements | Master data projection |
| M15 INV · M41 WMS | Part definitions, UoM, hazard class, alternates and supersessions | Master data projection |
| M16 PRO · M42 SRM2 | Item definitions for sourcing and supplier catalogue matching | REST |
| M13 RNT · M14 TRF · M18 ESG | Rental SKUs, refurbished grades, recycling service definitions | REST |
| M20 ARB · M51 TAX · M53 REV | Tax class and revenue-recognition class per invoiced item | Projection |
| M25 BID · M26 AIM | The dimensional spine for every product, service and fault analysis | Warehouse extract |
| P01 / P04 / P07 portals | Channel-specific published catalogue | REST via M28 |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `catalogue.item_created` | item id, code, type, category | M64, M25 |
| `catalogue.item_activated` | item id, type, channels, effective_from | M11, M36, M38, M12, M15 |
| `catalogue.item_changed` | item id, changed attributes, valid_from, impact summary | All consuming modules |
| `catalogue.item_restricted` | item id, restriction scope, reason | M11, M36, M38, M12 |
| `catalogue.item_discontinued` | item id, successor id, notice period, last order date | M08, M11, M15, M16, M38, M12 |
| `catalogue.part_superseded` | from item, to item, effective_from | M15, M16, M31, M41 |
| `catalogue.rbom_versioned` | operation id, model id, version | M31, M36, M15 |
| `catalogue.srt_rebaselined` | operation id, model id, old minutes, new minutes, evidence ref | M36, M11, M02, M31, M57 |
| `catalogue.fault_taxonomy_published` | version, affected codes, brand mappings | M01, M09, M23, M26 |
| `catalogue.published` | channel, version, content hash, item count | M38, M12, P01, P04, P07 |
| `catalogue.template_versioned` | template id, family, version | M08, M09, M39 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-CAT-01 | Brand partner parts catalogues (17+ partners) | Inbound | Import OEM part numbers, model lists and supersession bulletins |
| INT-CAT-02 | Brand partner fault-code schedules | Inbound | Maintain brand claim-code mapping |
| INT-CAT-03 | 1000FiX corporate website / Next.js platform | Outbound | Publish the customer-facing service and product catalogue |
| INT-CAT-04 | NBR HS code reference | Inbound | Validate HS classification for imported parts |
| INT-CAT-05 | Object storage / CDN | Outbound | Publish catalogue media |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/catalogue/items` | GET | Query the item set with filters and paging | All modules, portals |
| `/api/v1/catalogue/items/{id}` | GET | Full item definition including typed extension | All modules |
| `/api/v1/catalogue/items` | POST | Create a draft item | P03, bulk loader |
| `/api/v1/catalogue/items/{id}/transition` | POST | Lifecycle transition with guard evaluation | P03 |
| `/api/v1/catalogue/resolve` | POST | Resolve a code, alias, barcode or MPN to an item | P02, P03, P09, POS |
| `/api/v1/catalogue/search` | GET | Ranked bilingual search | P01, P03, P07 |
| `/api/v1/catalogue/operations/{id}/rbom` | GET | Exploded rBOM for a model with alternates | M36, M31, M15 |
| `/api/v1/catalogue/operations/{id}/srt` | GET | Standard repair time for a model and repair level | M36, M02, M31 |
| `/api/v1/catalogue/faults` | GET | Fault taxonomy, optionally brand-mapped | M01, M09, P02 |
| `/api/v1/catalogue/templates/contract` | GET | Contract product templates | M08 |
| `/api/v1/catalogue/templates/protection` | GET | Protection product definitions | M09 |
| `/api/v1/catalogue/publications/{channel}` | GET | Current published projection with version and hash | M38, M12, portals |
| `/api/v1/catalogue/bulk` | POST | Bulk create/update with dry-run | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R04 Chief Commercial Officer | C R U D A | All |
| R21 Sales Manager | R, propose | All (proposes changes; cannot approve) |
| R22 Account Manager (Corporate) | R | All |
| R17 Inventory Manager | C R U (part facet) | Part and UoM domain |
| R19 Procurement Officer | R, propose (part facet) | Part domain |
| R32 Quality Manager / ISO Coordinator | C R U A | Operations, rBOM, SRT, fault taxonomy, hazard class |
| R05 Operations Director | R, A (SRT re-baseline) | All |
| R26 Finance Manager | R, A (tax and revenue class) | All |
| R23 Marketing Manager | R U (media and marketing copy only) | Customer-facing content |
| R24 Marketplace Operations Officer | R | Taxonomy and permitted listing set |
| R08 Service Centre Agent | R | Active items only |
| R10 / R11 / R12 Technician | R | Operations, rBOM, SRT, parts |
| R33 IT / System Administrator | R U (configuration) | Attribute schema, channels |
| R36 / R37 / R38 External | R | Published channel projection only |
| — Catalogue Officer *(new position under R04)* | C R U | All facets; cannot approve own change |

**Field-level restrictions.** `standard_cost` and any margin-bearing display field are visible
only to R01–R05, R17, R21, R22, R26 and R27. Supplier-linked fields on the part facet are
hidden from all external portals. `internal_note` is never exposed externally.

**Segregation of duties.** The author of an item change cannot approve it (BRU-CAT-05,
mechanised as SOD-13, to be registered in `05-04` §6). The officer who re-baselines a standard
repair time cannot be the technician whose actuals drove the change.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Catalogue completeness dashboard | CCO, Catalogue Officer | Real time | Items by state and type; per-channel completeness; blocked publications |
| Channel coverage matrix | CCO, Marketing | Weekly | Which items are published to which channel, and the gaps |
| SRT variance report | Ops Director, Quality Manager | Weekly | Standard vs actual by operation and model, with distribution and outlier flags |
| rBOM accuracy report | Quality Manager, Inventory Manager | Monthly | Planned vs actual parts consumption per operation; unplanned-part frequency |
| Item usage and dead-SKU analysis | CCO, Inventory Manager | Monthly | Items never transacted; items with declining use; discontinuation candidates |
| Duplicate and near-duplicate register | Catalogue Officer | Weekly | Candidate duplicates by name, MPN, barcode and attribute similarity |
| Fault taxonomy coverage | Quality Manager, Warranty Officer | Monthly | Faults coded vs "other"; brand mapping gaps causing claim rejection |
| Supersession impact report | Inventory Manager, Procurement | On event | Open documents affected by a supersession, with resolution status |
| Catalogue change audit | CCO, Quality Manager, external auditor | On demand | Full attribute-level change history with actor, reason and impact set |
| New-item cycle time | CCO | Monthly | Draft → Active elapsed time by item type and reviewer |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| KPI-C37-01 | Catalogue items with complete definition for their class | 0% *(no catalogue exists)* | 90% | **100%** |
| KPI-C37-02 | Services with a defined standard duration and repair level | 0% | 85% | **100%** |
| KPI-C37-03 | Top-200 repair operations with an approved rBOM | 0% | 70% | **100%** |
| KPI-C37-04 | Top-200 repair operations with an approved SRT | 0% | 70% | **100%** |
| KPI-C37-05 | Median SRT variance (actual vs standard) | unmeasured | ≤ ±25% | **≤ ±12%** |
| KPI-C37-06 | Faults coded to a specific code rather than "other" | unmeasured | 80% | **> 95%** |
| KPI-C37-07 | Claim rejections attributed to fault-coding error | unmeasured | < 8% | **< 2%** |
| KPI-C37-08 | Duplicate active items | unknown | < 2% | **< 0.5%** |
| KPI-C37-09 | New-item draft-to-active cycle time | n/a | < 5 working days | **< 2 working days** |
| KPI-C37-10 | Channel publication lag after activation | n/a | < 30 min | **< 5 min** |
| KPI-C37-11 | Items sold with a missing tax class | n/a | 0 | **0** |
| KPI-C37-12 | Catalogue API availability | n/a | 99.9% | **99.95%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `product`, `uom`, `product_brand` | 22% |
| L2 | OCA `product_variant_configurator`, `product_attribute_value_menu`, `product_multi_category`, `product_supplierinfo_*`, `base_multi_image` | 20% |
| L5 | `cd_catalogue`, `cd_repair_bom`, `cd_service_product`, `cd_fault_taxonomy`, `cd_catalogue_publish` | 58% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C37-01 | `cd_catalogue` — unified item master, typed extensions, lifecycle, bitemporal history | Odoo module | 7 PW |
| CD-C37-02 | `cd_service_product` — service definition, delivery modes, skills, durations, templates | Odoo module | 4 PW |
| CD-C37-03 | `cd_repair_bom` — operations, rBOM, SRT, explosion engine, calibration workflow | Odoo module | 6 PW |
| CD-C37-04 | `cd_fault_taxonomy` — symptom/fault/root-cause tree with brand mapping | Odoo module | 2 PW |
| CD-C37-05 | `cd_catalogue_publish` — channel projections, completeness scoring, publication events | Odoo module | 3 PW |
| CD-C37-06 | Catalogue read API, search index and resolution service | Service | 2 PW |
| | | **Total** | **24 PW** |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M37 is scheduled in **W1** (P0) but declares a dependency on 1 module(s) that land later: **M64** (W2). One of three things must be true before the W1 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W1 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M37 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W1 plan for M37 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M29 Identity | Every catalogue change carries an actor and an approval identity |
| M28 Integration | Publication is event-driven; every consumer reads through the gateway |
| M30 Platform Admin | Channels, entities, branches and languages must exist before applicability rules can be declared |
| M64 MDM | Provides the new-item request workflow and duplicate/survivorship machinery |

**M37 must complete before M11, M36, M01 full scope, M15 and M38 can be accepted.** It is the
first commercial module and blocks the widest set of downstream work of any module in
Category C.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Branch service price lists (spreadsheets, 51+ variants) | ~1,200 distinct service descriptions, heavily duplicated | `fix.catalogue.item` + `fix.service.product` | W1 |
| Parts inventory spreadsheets | ~18,000 rows, estimated 30–40% duplication | `fix.catalogue.item` + `fix.part.item` | W1 |
| Brand partner parts catalogues (17+) | ~60,000 OEM part references | `fix.part.crossref`, `fix.part.supersession` | W1–W2 |
| Brand/model lists from service records | ~4,000 model references | `fix.brand`, `fix.device.model` | W1 |
| AMC/RAMC package descriptions | 14 families, ~40 variants | `fix.contract.product.template` | W1 |
| Protection product wordings | 7 families | `fix.protection.product` | W1 |
| Historic job records (for provisional SRT) | 500,000+ paper and digital records, sampled | `fix.standard.repair.time` (source = "provisional") | W1–W2 |

**Migration rule.** No item enters the catalogue in Active state through migration. Every
migrated item lands in Draft or In Review and requires an owner's approval. This is deliberately
slow and is the single largest change-management task of Wave 1; it is also the only way the
duplication in the source data does not become permanent.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every one of the fourteen revenue streams has at least one fully defined, Active, publishable item | Demonstration per stream |
| AC-02 | No catalogue table contains a price, cost, discount or margin column | Schema inspection + automated test |
| AC-03 | An estimate in M36 pre-populates from fault code → operation → rBOM → SRT with no manual line entry | End-to-end demonstration |
| AC-04 | An rBOM explodes to requisition lines in M15 honouring alternates and supersessions | Scripted scenario |
| AC-05 | A superseded part resolves to its successor everywhere, including open documents | Negative and positive test |
| AC-06 | An item cannot be published to a customer channel with incomplete Bengali content | Negative test via UI and API |
| AC-07 | An item that has been transacted cannot be deleted by any route | Negative test via UI, API and direct ORM call |
| AC-08 | A change to an Active item shows its full reference impact set before commit | Demonstration on a referenced item |
| AC-09 | The full catalogue publishes to all six channels in under 4 minutes with a verifiable content hash | Performance test |
| AC-10 | Search returns ranked bilingual results in ≤ 300 ms p95 over the full catalogue | Load test report |
| AC-11 | The fault taxonomy maps to the claim codes of at least the top five brand partners | Mapping coverage report |
| AC-12 | Bulk load of 50,000 items completes with per-row error reporting and atomic rollback on failure | Migration dry-run report |
| AC-13 | All 14 contract product families and 7 protection families instantiate in M08/M09 without code change | Template instantiation test |
| AC-14 | Named business super-users sign off UAT for all P0 and P1 requirements | Signed UAT record |
| AC-15 | Zero critical or high security findings | Security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Who holds the Catalogue Officer position, and does it sit under Commercial or Quality? The rBOM/SRT domain is technical; the selling domain is commercial | CCO / Ops Director | W1 build start |
| Q-02 | What is the acceptable provisional-SRT confidence band at go-live, given that standards will initially be derived from sampled historical records? | Ops Director / Quality | W1 build |
| Q-03 | Do brand partners permit 1000FiX to hold and redistribute their parts catalogues inside the ERP, and under what licence terms? | CCO / Legal | W1 build |
| Q-04 | Is the refurbished grade scale (A–D) contractually committed anywhere, or can it be defined freely? | Retail Operations Head | W6 (M14) |
| Q-05 | Should the catalogue carry a single global hierarchy or per-country hierarchies once M65 multi-country is live? | CTO / CCO | W9 (M65) |
| Q-06 | Which party owns the customer-facing Bengali wording — Marketing or Commercial — given it appears on legal invoices? | CCO / Marketing Head | W1 build |

---

## 19. References

**Internal**
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2, §6, §8 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-02_Data_Model_and_Entity_Catalogue.md` · `05-04_Role_Permission_and_Access_Matrix.md` ·
`05-05_Business_Rules_and_Automation_Catalogue.md` ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` §3.3

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.11, §10.1 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §7 ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Service Selection ·
`1000FiX_Services_Company_Profile.md` §Core Services ·
`1000FiX Business Plan` §Service Portfolio, §RAMC Packages, §Rental, §Refurbishment

**External benchmark**
SAP S/4HANA product master, service product and service bill of material ·
SAP condition technique — the price-outside-the-product principle ·
Oracle Fusion Cloud Product Hub — item classes, attribute groups, new-item request, publication ·
Microsoft Dynamics 365 product families, bundles and kits ·
IFS Cloud standard jobs and maintenance BOM ·
Automotive flat-rate labour-time guide practice ·
PIM platform practice (Pimcore, Akeneo) — channel completeness scoring ·
Odoo 19 `product` / `uom` and OCA product-variant module family

---

*Module M37 · Category C · 1000FiX ERP System v2.0 · CONFIDENTIAL*
