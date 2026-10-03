---
id: FIX-ERP2-M64
module_id: M64
module_code: MDM
module_name: Master Data Management & Configuration
category: K — Platform & Technology
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Platform Squad
priority: P1
wave: W2
---

# M64 — Master Data Management & Configuration
### Category K · Code `MDM` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M64 |
| **Module code** | `MDM` |
| **Category** | K — Platform & Technology |
| **Status** | ★ **New** — split out of M30 after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | W2 (Months 5–8) — *before the data volume arrives* |
| **Business owner** | Chief Technology Officer *(with a data steward named per domain — see §13)* |
| **System owner** | Platform Squad |
| **Delivery layers** | L1 Odoo `base` · L2 OCA `server-tools`, `base_exception` · L5 custom stewardship, quality, reference-data and parameter engines |
| **Custom modules** | `cd_mdm`, `cd_data_quality`, `cd_reference_data` |
| **Requirement range** | FR-MDM-001 … FR-MDM-034 |
| **Requirement count** | **34** *(measured — supersedes the 26 estimate in `02-02`; **new range allocation** under `05-01` §1.3a)* |
| **Effort estimate** | **17 person-weeks** *(measured — supersedes the 14 PW estimate)* |
| **Depends on** | M30 Platform Admin · M29 Identity · M28 Integration · M33 Party Master · M37 Catalogue |
| **Depended on by** | M33, M37, M15, M16, M42, M11, M19, M21, M54, M63, M62, M25 — **and every module that reads a code list or a business threshold** |

---

## 2. Purpose

M64 exists because of a failure mode that no amount of platform engineering prevents:
**the system runs perfectly on wrong data.**

M30 keeps the platform running. M29 controls who may act. M28 moves the messages. None of them
notices that the same brand has been entered four times with four spellings, that a part
number was created without a compatibility mapping, that a branch code was invented on a
Tuesday afternoon, or that a discount ceiling was changed by someone who had no authority to
change it.

M64 owns **who may create or change master data, through what approval, and whether the result
is any good**. It also owns the **business parameters** — thresholds, ceilings, periods and
tolerances — that the rest of the estate reads and M63 executes, so that changing a rule of the
business does not require a code release.

The category overview states the distinction exactly: *M30's failure mode is that the system
does not run. M64's failure mode is that the system runs perfectly on wrong data.* The second
is worse, because it is invisible.

### Why It Exists

**Because the volume arrives in Wave 2.** M15 loads roughly 10,000 parts across 51+ locations
in W2. M33 loads a customer base measured in hundreds of thousands. Governing data after it
has arrived is remediation; governing it before is management. That is why M64 lands in W2 —
*before the data volume arrives*, as the category delivery sequence puts it.

**Because master data is the substrate of every KPI in the programme.** Inventory accuracy
(BO-03) depends on part master quality. Warranty recovery (BO-04) depends on brand and model
mapping. Dynamic pricing depends on price-book integrity. A duplicate customer record breaks
Customer 360, loyalty, and the PDPA data-subject rights that M29 must execute.

**Because business rules change more often than code should.** Promise 6 of the platform
contract is that *business thresholds, approval chains and rule parameters change without a
code release*. M64 stores them; M63 executes them. Without M64 those values live in code, and
every policy change becomes a development ticket.

**Because governance that is bureaucracy gets bypassed.** The category risk is explicit:
*"Master data governance treated as bureaucracy and bypassed — the system runs perfectly on
wrong data."* The mitigation is equally explicit: **the stewardship workflow is the only path
to change; direct edits are blocked.** Not discouraged — blocked.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §2 | M64 owns "master data ownership, stewardship workflows, data quality rules, reference data distribution, business-rule parameters" |
| `_CATEGORY_OVERVIEW.md` §5 | **The M30/M64 boundary**: technical configuration versus business master data governance; audiences, failure modes and analogues (SAP MDG, Oracle Product/Customer Hub, Informatica MDM) |
| `_CATEGORY_OVERVIEW.md` §6 | M64 owns master data ownership, stewardship and quality rules — **M37 owns catalogue content, M33 owns party content**; M64 stores business-rule parameters, **M63 executes them**; M64 does not define access |
| `_CATEGORY_OVERVIEW.md` §7 promise 6 | "Business thresholds, approval chains and rule parameters change without a code release" — M64 with M63 |
| `_CATEGORY_OVERVIEW.md` §9 | **Master data changes made through the approved workflow: 100%**; **master data quality score > 97%** |
| `_CATEGORY_OVERVIEW.md` §10 | W2 delivery — "data governance before volume arrives" |
| `_CATEGORY_OVERVIEW.md` §11 | Risk: governance bypassed; mitigation "stewardship workflow is the only path to change; direct edits blocked" |
| `05-05` §11 BRU-ADM-01 | "Master data changes above the defined significance require approval before taking effect" — **the rule M64 inherits and executes** |
| `05-02` §M30 | `fix.master.data.domain` and `fix.mdm.change.request` allocated to M30 in the 30-module register — **reallocated to M64 in v2.1** |
| `05-06` NFR-027 | No-code configuration for workflows, forms, **thresholds** and business rules |
| `05-06` DI-06 | Data quality tests run on every warehouse load; failures block dependent refreshes |
| `05-06` DI-03 | Referential integrity enforced at the database level, not only in application code |
| `02-01` §3 | The shared kernel — party, product, location, entity, document, event — "changing a kernel concept requires architectural review" |

---

## 3. Scope Boundary

> **The rule:** M64 owns **the governance of master data, not the data itself**. M33 owns what
> a customer *is*; M64 owns who may create one, through what approval, and whether the record
> meets quality standard. The same split applies to every domain.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | **Master data domain register** — every governed domain with its owning module, data steward, criticality and change significance |
| 2 | Data ownership model: business owner, data steward, technical custodian per domain |
| 3 | **Stewardship workflow** — request, enrich, validate, approve, publish — as the only path to change governed data |
| 4 | Change significance classification: which changes need approval, at what level, and which are routine |
| 5 | Direct-edit prevention on governed attributes |
| 6 | Bulk change governance: mass update proposals reviewed and approved as a set |
| 7 | **Data quality rule engine** — completeness, validity, format, range, referential, uniqueness, consistency and timeliness rules |
| 8 | Data quality scoring per record, per domain and estate-wide |
| 9 | Quality dashboards, exception worklists and remediation tracking |
| 10 | Quality gating: preventing a record from being published or used while it fails a blocking rule |
| 11 | **Duplicate detection and matching** across governed domains |
| 12 | Golden-record survivorship rules — which source wins per attribute on merge |
| 13 | Merge, unmerge and merge audit |
| 14 | **Reference data and code list management** — the single source for every enumerated value in the estate |
| 15 | Code list versioning, effective dating and distribution to all consumers |
| 16 | Cross-reference mapping between internal codes and external codes (brand part numbers, HS codes, bank codes, tax codes) |
| 17 | **Business rule parameters and thresholds** — the values M63 executes and every module reads |
| 18 | Parameter approval, versioning, effective dating and rollback |
| 19 | Hierarchy and classification management: product, spend, cost centre roll-ups, customer segmentation trees |
| 20 | Data lineage: where an attribute originated and what depends on it |
| 21 | **Impact analysis** before a master data or parameter change |
| 22 | Master data audit: who changed what, when, under which approval |
| 23 | Data quality contribution to the warehouse load gate (DI-06) |
| 24 | Onboarding governance for new master data domains as modules are built |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Party content** — customer, supplier, employee, seller record and its attributes | **M33** Party Master | M33 owns what a party *is*; M64 governs how one comes into existence and whether it is good enough. Both sides agree in `_CATEGORY_OVERVIEW.md` §6 |
| **Catalogue content** — part, product, service definition, compatibility, supersession | **M37** Catalogue | Same split. M37 authors; M64 governs |
| Consent, lawful basis, transparency notice | **M33** | A privacy concept, not a quality one |
| Duplicate resolution *for parties specifically* | **M33** (using M64's engine) | M33 owns the party merge decision and its customer-facing consequences; M64 provides matching, survivorship and audit |
| **Business rule execution, workflow, approval routing** | **M63** Process Automation | **M64 stores the parameter; M63 executes the rule.** The clearest boundary in the module: a number versus what is done with it |
| Technical configuration — timeouts, batch sizes, feature flags, environments | **M30** | M30's failure mode is the system not running; M64's is the system running on wrong data |
| Organisation structure — entity, branch, zone, cost centre objects | **M30** | M64 governs *changes* to the branch code and hierarchy; M30 owns the object and provisions it |
| Country pack, locale, currency and translation content | **M65** | Jurisdiction reference data is M65's; M64 governs its change process |
| Access control, roles, record rules | **M29** | **M64 does not define access** — stated explicitly in the category boundary map |
| Data warehouse, pipelines, analytical models | **M62** Data Platform | M64 supplies the quality gate; M62 runs the pipeline |
| Business intelligence and reporting | **M25** | — |
| Document management and retention | **M24** | — |
| Financial chart of accounts *content* | **M19** | M64 governs its change process; M19 owns its accounting meaning |
| Inventory ownership classes and their rules | **M15** | Business rules embedded in a domain module, not parameters |
| Enterprise risk register and control testing | **M60** GRC | — |

### 3.3 Shared Concepts

| Concept | M64's Role | Owning Module |
|---|---|---|
| Master data record | **Governs** creation, change, approval and quality; the domain module owns the content | M64 / domain module |
| Data steward | **Owns** the role and its assignment per domain | M64 |
| Data quality rule | **Owns** | M64 |
| Golden record | **Owns** matching and survivorship; the domain module owns the merge decision | M64 / domain module |
| Reference data / code list | **Owns** | M64 |
| Business parameter | **Owns** the value; **M63 executes** | M64 / M63 |
| Technical parameter | Refers; M30 owns | M30 |
| Hierarchy | **Owns** the structure and its governance; the domain module owns its meaning | M64 / domain module |
| Lineage | **Owns** for master data; M62 owns analytical lineage | M64 / M62 |
| Change approval | **Owns** the master data workflow; M29 enforces who may approve | M64 / M29 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Master Data Governance (MDG)** | The governance layer over master data: a single governed model per domain, **golden records** for customer, product, vendor and finance, **workflows and sub-workflows with roles, responsibilities and data stewardship** ensuring accountability and visibility of every creation and update across the organisational hierarchy, and automated validation for formats, classifications, tax fields and regulatory checks | **MDG is the primary reference for M64.** Adopted whole: the **domain-plus-steward-plus-workflow** structure; **change requests as the only path to governed data**; validation rules attached to the domain rather than scattered through application code; and the principle that governance preserves *semantics and relationships between entities*, not just field values | SAP MDG's data model extensibility framework and its consolidation/central-governance duality. We implement central governance only — 1000FiX has one ERP, not a federated landscape |
| **Oracle Product Hub / Customer Hub** | Domain-specific hubs with import, cleanse, match, merge and publish; attribute-level survivorship | **Attribute-level survivorship** — on merge, each attribute is resolved by its own rule rather than the whole record taking one source. A customer's best address and best phone often come from different records | Separate hubs per domain; one governance engine serves all domains, because our domain count is manageable and consistency matters more than depth |
| **Informatica MDM / data governance practice** | Match-and-merge engines, data quality scorecards, stewardship consoles, lineage | The **stewardship console as a worklist**, not a report. A steward needs "here are the 40 records you must fix today", ranked — not a quality percentage | Commercial MDM licensing; the cost is unjustifiable against 1000FiX's data volume |
| **Master data governance best practice (2025)** | Assign dedicated data owners; maintain a golden record per entity; embed automation; continuous monitoring, training and steward–business collaboration | **A named steward per domain, drawn from the business rather than from IT.** The category is explicit that M64's audience is *"data stewards in each business function"*. A steward who does not use the data cannot judge whether it is right | Governance councils and formal charters as a Wave 2 deliverable; they follow adoption, they do not create it |
| **Data quality dimension frameworks** | Completeness, validity, accuracy, consistency, uniqueness, timeliness as measurable dimensions | The six dimensions as the **rule taxonomy**, so that a quality score is decomposable and actionable rather than a single opaque number | Accuracy measured against an external truth source; largely unavailable in the Bangladesh context and replaced by validity and consistency rules |
| **Reference data management practice** | Centrally governed code lists, versioned and effective-dated, distributed to consumers | **Code lists as versioned, effective-dated, distributed reference data**, so that a value retired today does not break a document written last year | — |

**Design position.** Five deliberate differences.

First, **M64 governs but does not own content, and this is the hardest boundary in Category K
to hold**. It would be simpler to make M64 the home of the part master and the customer master.
It would also be wrong: part definition belongs with the module that reasons about
compatibility and supersession (M37), and customer definition belongs with the module that
reasons about consent and relationships (M33). M64 supplies the workflow, the rules and the
score. The alternative — a central MDM that owns all master data — creates a bottleneck between
every business team and its own data, which is precisely how governance comes to be experienced
as bureaucracy.

Second, **the stewardship workflow is the only path, and direct edits are blocked in the ORM**.
The category risk names bypass as the failure mode. A governance process that a determined user
can route around by opening the record directly will be routed around. Governed attributes are
therefore read-only on the record form; the only write path is an approved change request.

Third, **quality is a gate, not a report**. A blocking rule prevents publication. A part with no
compatibility mapping cannot be made orderable; a customer with an invalid phone cannot be used
for a service order requiring notification. Reporting quality without gating it produces
dashboards that decline gracefully for years.

Fourth, **stewards are business people, and the console is built for them**. The steward for
parts is in the warehouse, not in IT. The console is a ranked worklist in Bengali and English,
not a data-modelling tool. If a steward needs training to use it, the design has failed.

Fifth, **business parameters are separated from technical configuration by the failure-mode
test**. Would getting this wrong break the system, or break the business? A batch size breaks
the system — M30. A discount ceiling breaks the business — M64. The test is stated because the
boundary will be contested for perhaps 50–100 parameters, and a rule that resolves the argument
is worth more than a list that will be incomplete.

---

## 5. Functional Areas & Features

### 5.1 Domain Register, Ownership & Stewardship

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MDM-001 | **Master data domain register** | Maintain every governed domain with its owning module, business owner, named data steward, technical custodian, criticality, record volume and governance level | **P0** | L5 |
| FR-MDM-002 | Governed attribute register | Declare, per domain, which attributes are governed — and therefore not directly editable — and which are freely maintainable | **P0** | L5 |
| FR-MDM-003 | Change significance model | Classify each governed attribute's change significance: routine, significant (requires steward approval) or critical (requires business-owner approval), per BRU-ADM-01 | **P0** | L5 |
| FR-MDM-004 | Steward assignment | Assign and maintain named stewards per domain with deputies, and route work to the deputy on absence | **P0** | L5 |
| FR-MDM-005 | **Steward console** | Present each steward a ranked worklist — pending change requests, failing quality rules, suspected duplicates, expiring reference data — with the business impact of each, in Bengali and English | **P0** | L5 |
| FR-MDM-006 | Domain onboarding | Onboard a new master data domain as each module is built, with its rules, steward and significance model, so governance keeps pace with delivery | P1 | L5 |

### 5.2 Change Control & Stewardship Workflow

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MDM-007 | **Change request** | Create a master data change request for any create, update, deactivate or merge on a governed attribute, capturing the proposer, justification, before and after values | **P0** | L5 |
| FR-MDM-008 | **Direct-edit prevention** | Block direct modification of a governed attribute through the UI, the API, an import or a script; the only write path is an approved change request | **P0** | L5 |
| FR-MDM-009 | Enrichment and validation stage | Route a request through enrichment (mandatory attributes completed) and validation (quality rules evaluated) before it reaches approval | **P0** | L5 |
| FR-MDM-010 | Approval routing | Route by domain, change significance and value, with steward, business owner and — for critical domains — architectural review (`02-01` §3 kernel concepts) | **P0** | L5 |
| FR-MDM-011 | Publication | Publish an approved change atomically to the owning module, with effective dating where the domain supports it | **P0** | L5 |
| FR-MDM-012 | Rejection and rework | Reject with a reason and return to the proposer for rework, retaining the full history | **P0** | L5 |
| FR-MDM-013 | **Bulk change governance** | Govern mass updates as a single reviewable set with a preview of every affected record, an approval, and all-or-nothing application | **P0** | L5 |
| FR-MDM-014 | Emergency change path | Provide a loud, time-boxed emergency path with immediate notification and mandatory retrospective approval, mirroring M30's pattern | P1 | L5 |
| FR-MDM-015 | Change audit | Retain the immutable record of every governed change: proposer, approvers, values, justification, publication time — queryable by record and by steward | **P0** | L5 |

### 5.3 Data Quality

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MDM-016 | **Quality rule engine** | Define and evaluate rules across six dimensions — completeness, validity, consistency, uniqueness, referential integrity and timeliness — per domain and per attribute | **P0** | L2/L5 |
| FR-MDM-017 | Rule classification | Classify each rule as blocking (prevents publication or use), warning (permits with a flag) or advisory (measured only) | **P0** | L5 |
| FR-MDM-018 | **Quality gating** | Prevent a record failing a blocking rule from being published, or from being used in the operations its rule protects | **P0** | L5 |
| FR-MDM-019 | Quality scoring | Compute a quality score per record, per domain and estate-wide, decomposable by dimension and rule | **P0** | L5 |
| FR-MDM-020 | Continuous evaluation | Re-evaluate quality on change and on a schedule, so that a record that degrades through an external change is detected | **P0** | L5 |
| FR-MDM-021 | Remediation worklist | Present failing records as a prioritised worklist ranked by business impact, with bulk remediation where the fix is uniform | **P0** | L5 |
| FR-MDM-022 | **Warehouse load gate** | Publish quality results to M62 so that a failing data quality test blocks dependent warehouse refreshes (DI-06) | P1 | L5 |
| FR-MDM-023 | Quality trend and attribution | Report quality trend by domain and steward, and attribute degradation to its cause — migration, integration, manual entry or external change | P1 | L5 |

### 5.4 Matching, Golden Record & Hierarchies

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MDM-024 | **Duplicate detection** | Detect suspected duplicates within a domain using configurable deterministic and fuzzy matching, tuned per domain, including Bengali text | **P0** | L5 |
| FR-MDM-025 | Match review | Present suspected duplicates to the steward with the evidence and a confidence score; auto-merge only above a domain-specific threshold | **P0** | L5 |
| FR-MDM-026 | **Attribute-level survivorship** | Resolve a merge attribute by attribute using declared survivorship rules — most recent, most complete, most trusted source, or steward decision | **P0** | L5 |
| FR-MDM-027 | Merge, unmerge and audit | Execute a merge with full lineage, notify every module holding a reference, and support unmerge where the merge was wrong | **P0** | L5 |
| FR-MDM-028 | Hierarchy management | Maintain governed hierarchies — product and service classification, spend category, cost centre roll-up, customer segmentation — with versioning and effective dating | P1 | L5 |
| FR-MDM-029 | Hierarchy integrity | Prevent cycles, orphans and level violations in any governed hierarchy | **P0** | L5 |

### 5.5 Reference Data & Business Parameters

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-MDM-030 | **Reference data and code lists** | Maintain every enumerated value in the estate — fault codes, condition grades, reason codes, statuses, units of measure, document types — as governed, versioned, effective-dated reference data with Bengali and English labels | **P0** | L5 |
| FR-MDM-031 | Reference data distribution | Distribute code lists to every consumer through API and event, so no module holds its own copy; a retired value remains resolvable for historical records | **P0** | L5 |
| FR-MDM-032 | **Cross-reference mapping** | Map internal codes to external codes — brand part numbers, HS codes, bank and branch codes, tax codes, courier service codes — with effective dating and a named owner | **P0** | L5 |
| FR-MDM-033 | **Business parameter registry** | Maintain business thresholds, ceilings, periods, tolerances and rates — approval bands, discount ceilings, SLA targets, warranty periods, match tolerances, dead-stock days, credit limits — with owner, scope, validation, approval requirement and effective dating; **M63 executes them** | **P0** | L5 |
| FR-MDM-034 | **Lineage and impact analysis** | Record where each governed attribute and parameter originates and which modules, reports, rules and integrations depend on it; present the impact of a proposed change **before** it is approved | **P0** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Direct-edit prevention at the ORM layer** | Governed attributes are write-protected in the ORM, not only in the UI. An import, a script, an API call and a developer console attempt all fail identically. This is what makes the category's "direct edits blocked" mitigation real |
| T-02 | **Change request atomicity** | Publication applies every attribute of a request atomically to the owning module; a partial publication is impossible |
| T-03 | **Rule evaluation performance** | A record's full rule set evaluates in ≤ 50 ms on save; a domain-wide re-evaluation of 100,000 records completes within a 30-minute window |
| T-04 | **Bengali-aware matching** | Duplicate matching handles Bengali text with ICU `bn-BD` collation, transliteration variants and common phonetic spellings — a customer entered once in Bengali and once in English is one customer |
| T-05 | **Survivorship determinism** | Given the same candidate records and rules, a merge produces the same golden record. The rule applied per attribute is stored on the merge record |
| T-06 | **Unmerge integrity** | An unmerge restores the constituent records with their pre-merge state and re-points references, without losing changes made after the merge |
| T-07 | **Reference data resolution** | Code list lookup is cached with invalidation on publication; resolution ≤ 2 ms. A retired value remains resolvable indefinitely for historical records |
| T-08 | **Parameter resolution** | Business parameter resolution mirrors M30's configuration resolution in shape and latency, so consumers use one pattern for both — but the two registries remain separate |
| T-09 | **Effective dating** | Reference values, parameters and hierarchies are effective-dated; a document written last year resolves against the values in force then |
| T-10 | **Impact analysis completeness** | Lineage is derived from actual dependencies — API consumers, event subscribers, report definitions, rule references — not from a manually maintained list, so it cannot drift |
| T-11 | **Event emission** | Every publication, merge, reference change and parameter change emits through the outbox (AS-08), so consumers react rather than poll |
| T-12 | **Quality score reproducibility** | A score stores its rule-set version and inputs; a historical score can be explained |
| T-13 | **Scale envelope** | ~10,000 parts, 250,000+ customers per month, 5,000 sellers, 400+ suppliers, ~200 code lists, ~300 business parameters; ~50,000 change requests per year at Wave 8 |
| T-14 | **Multi-entity scoping** | Governed data, parameters and reference values carry entity scope where they vary by entity, so a second country does not fork the domain (AS-03) |
| T-15 | **No access decisions** | M64 makes no authorisation decision. Steward and approver rights are M29 roles; M64 asks M29 whether the actor may approve |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M64 |
|---|---|---|
| **Warehouse / parts steward** | Anyone can create a part number; duplicates and gaps discovered when a job fails | Creates through a request with mandatory attributes; the system will not accept an incomplete part |
| **Branch agent** | Creates a customer record on every visit because searching is unreliable | Duplicate detection at entry; one customer, one record |
| **Procurement** | Supplier and spend category names drift; spend analysis is unreliable | Governed supplier and category master; spend analysis means something |
| **Finance** | Discount ceilings and approval bands live in code or in memory | Business parameters with owners, approval and effective dates |
| **Data steward** *(a new role)* | Does not exist | Owns a domain, works a ranked daily worklist, is measured on quality |
| **CCO / CFO** | Changing a business rule means a development ticket and a release | Changes a parameter with approval; the rule takes effect without a release |
| **Business analyst** | Cannot tell what depends on a code value before changing it | Impact analysis before approval |
| **Developer** | Adds a new status value in code, in one module | Requests it as reference data; every module receives it |
| **Auditor** | Cannot establish who changed a master value or why | Immutable change trail with justification and approver |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Inventory accuracy protection** | Governed part master with mandatory compatibility, unit of measure and classification | **BO-03 (75% → 98%+) is unreachable on a poor part master.** M64 is a precondition for the **BDT 34 lac/year** inventory benefit, not an addition to it |
| **Warranty revenue recovery** | Governed brand, model and fault-code master with correct external cross-references | **BO-04** and the **BDT 100 lac/year** warranty recovery depend on claims matching the brand's own reference data. A mis-mapped model number is a rejected claim |
| **Customer 360 integrity** | Duplicate detection and attribute-level survivorship on the party master | Duplicates break Customer 360, loyalty tier calculation, churn prediction and — materially — **PDPA data-subject rights**, which cannot be executed against a fragmented identity |
| **Change without a code release** | Business parameters registered, approved and effective-dated | **> 95% of configuration changes without a code release** (with M30). Each avoided release is days of development and deployment risk, and it removes IT from the path of a business decision |
| **Pricing and margin integrity** | Governed price books, discount ceilings and approval bands | Protects the **BDT 40 lac/year** dynamic-pricing margin uplift, which is only as good as the parameters behind it |
| **Spend analysis reliability** | Governed supplier and spend category master | Makes M16's category strategy and M42's concentration analysis possible at all |
| **Reduced rework and failed jobs** | Blocking quality rules stop bad data entering | A part with no compatibility mapping causes a technician journey that cannot succeed. Prevention is far cheaper than the failed visit |
| **Analytics trust** | Quality gate on the warehouse load (DI-06) | **BO-17 (decisions on live data, zero manual reporting packs)** fails the moment a leader finds one wrong number. Quality gating is what protects adoption |
| **Migration quality** | Governance live in W2, before the W2–W3 data volume | Governing at load is a fraction of the cost of remediating afterwards, and it is the difference between M43's forecasting being possible in W6 and not |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **ISO 9001 conformance** | Control of documented information and data integrity are explicit clauses; a governed change trail is direct evidence |
| **PDPA 2026 support** | Accuracy is a data-protection principle. Rectification within 30 days (NFR-093) requires knowing which record is authoritative |
| **Accountability for data** | Named stewards convert "the data is bad" from a complaint into an owned responsibility |
| **Institutional knowledge capture** | Why a code exists, who owns it and what depends on it stops being tribal knowledge |
| **Change confidence** | Impact analysis before approval means a business change is made knowingly rather than hopefully |
| **Multi-country readiness** | Entity-scoped governed data means a second country extends the domains rather than forking them (**BO-18**) |
| **Foundation for AI** | M26's models are trained on this data. Poor master data produces confidently wrong predictions, which is worse than no predictions |

---

## 8. Lifecycle & State Models

### 8.1 Master Data Change Request

```
        ┌──────────────┐
        │    DRAFT     │  proposer, domain, records, before/after, justification
        └──────┬───────┘
               │ submitted
        ┌──────▼───────┐
        │  ENRICHMENT  │  mandatory attributes completed for the domain
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │  VALIDATION  │  quality rules evaluated (FR-MDM-016)
        └──┬────────┬──┘
   blocking│        │ passes / warnings only
   failure │        │
        ┌──▼──────┐ │
        │ FAILED  │ │  returned with the failing rules named
        │ QUALITY │ │
        └──┬──────┘ │
           │ fixed  │
           └────────┤
                    │
        ┌───────────▼──────┐
        │ IMPACT ANALYSED  │  what depends on this? (FR-MDM-034)
        └───────────┬──────┘
                    │
        ┌───────────▼──────┐
        │ PENDING APPROVAL │  routed by domain, significance and value
        └──┬─────────┬─────┘
   approved│         │ rejected
           │    ┌────▼─────┐
           │    │ REJECTED │ reason recorded; returns to proposer for rework
           │    └──────────┘
        ┌──▼────────┐
        │ APPROVED  │
        └──┬────────┘
           │ published atomically to the owning module (T-02)
        ┌──▼────────┐
        │ PUBLISHED │ ──► domain event; consumers updated; effective-dated
        └──┬────────┘
           │
        ┌──▼────────┐
        │  CLOSED   │ immutable; queryable by record and by steward
        └───────────┘

   EMERGENCY PATH (FR-MDM-014)
   ────────────────────────────
   EMERGENCY ──► applied directly · multi-party notification · time-boxed
       │
       └──► retrospective approval mandatory within 24 h
                 ✖ not approved ──► **reverted automatically**; escalated
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Draft | Any user proposes a change to a governed attribute | Proposer |
| Draft | Enrichment | Domain, records and justification present | Proposer |
| Enrichment | Validation | Every mandatory attribute for the domain is complete | System |
| Validation | Failed quality | A blocking rule fails (FR-MDM-018) | System |
| Validation | Impact analysed | No blocking failure; warnings recorded | System |
| Impact analysed | Pending approval | Impact presented to the approver | System |
| Pending approval | Approved | Approver holds authority for the domain and significance; **M29 confirms the right** | Steward / business owner / architecture review |
| Pending approval | Rejected | Reason recorded | Approver |
| Approved | Published | Applied atomically to the owning module with effective dating | System |
| Published | Closed | Consumers notified; audit sealed | System |

### 8.2 Duplicate Resolution & Merge

```
   Detection: on entry · scheduled sweep · steward-initiated
        │
   ┌────▼──────────┐
   │  SUSPECTED    │  candidate pair with a confidence score
   └────┬──────┬───┘
        │      │ confidence above the domain auto-merge threshold
        │      └────────────────────────────┐
        │ below threshold                   │
   ┌────▼──────────┐                        │
   │ STEWARD       │  evidence presented    │
   │ REVIEW        │  side by side          │
   └──┬─────────┬──┘                        │
      │         │ not a duplicate           │
      │    ┌────▼──────────┐                │
      │    │ DISMISSED     │ recorded so    │
      │    │               │ the same pair  │
      │    └───────────────┘ is not re-raised
      │ confirmed                           │
   ┌──▼─────────────────────────────────────▼──┐
   │        SURVIVORSHIP APPLIED               │
   │  attribute by attribute (FR-MDM-026):     │
   │  most recent · most complete ·            │
   │  most trusted source · steward decision   │
   └──┬────────────────────────────────────────┘
      │
   ┌──▼────────┐
   │  MERGED   │ ──► golden record published;
   └──┬────────┘     every module holding a reference notified
      │
      │ merge found to be wrong
   ┌──▼─────────┐
   │ UNMERGED   │ constituents restored with pre-merge state;
   └────────────┘ post-merge changes preserved (T-06)
```

### 8.3 Reference Value & Business Parameter

```
   PROPOSED ──► impact analysed: who consumes this value?
       │
       ▼
   APPROVED ──► owner and approver recorded
       │
       ▼
   EFFECTIVE ──► distributed by API and event;
       │         resolves for documents dated in its window
       │
       ├──► superseded by a new version ──► SUPERSEDED
       │                                     (still resolvable historically)
       ▼
   RETIRED ──► no longer selectable for new records;
               **remains resolvable indefinitely** for historical records (T-07)
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-MDM-01 | **A governed attribute can be changed only through an approved change request.** Direct edits are blocked in the UI, the API, imports and scripts | **H** | CTO |
| BRU-MDM-02 | Master data changes above the defined significance require approval before taking effect *(inherits BRU-ADM-01 from `05-05` §11)* | **H** | CTO |
| BRU-MDM-03 | Every governed domain has a named data steward and a named business owner; a domain without both cannot be activated | **H** | CTO |
| BRU-MDM-04 | The data steward is drawn from the business function that uses the data, not from IT | **C** | CTO |
| BRU-MDM-05 | A record failing a blocking quality rule cannot be published or used in the operation the rule protects | **H** | CTO |
| BRU-MDM-06 | A change request cannot be approved by its proposer | **H** | CTO |
| BRU-MDM-07 | Impact analysis is presented to the approver before approval; approving without it is not possible | **H** | CTO |
| BRU-MDM-08 | A bulk change is reviewed and approved as a set and applied all-or-nothing | **H** | CTO |
| BRU-MDM-09 | An emergency master data change requires retrospective approval within 24 hours or is reverted automatically | **H** | CTO |
| BRU-MDM-10 | Auto-merge occurs only above the domain's configured confidence threshold; below it, a steward decides | **H** | CTO |
| BRU-MDM-11 | Survivorship is resolved attribute by attribute using declared rules, and the rule applied is stored on the merge | **C** | CTO |
| BRU-MDM-12 | A merge notifies every module holding a reference to the merged records | **H** | CTO |
| BRU-MDM-13 | A retired reference value remains resolvable indefinitely for historical records; it is never deleted | **H** | CTO |
| BRU-MDM-14 | No module holds its own copy of a governed code list; all consume the distributed reference data | **H** | CTO |
| BRU-MDM-15 | **M64 stores business parameters; M63 executes them. M64 contains no rule execution logic** | **H** | CTO |
| BRU-MDM-16 | A business parameter change follows the same request, approval and effective-dating discipline as master data | **H** | CTO |
| BRU-MDM-17 | Reference values, parameters and hierarchies are effective-dated; historical documents resolve against the values in force at the time | **C** | CTO |
| BRU-MDM-18 | A governed hierarchy may not contain a cycle, an orphan or a level violation | **H** | CTO |
| BRU-MDM-19 | **M64 makes no access decision**; steward and approver rights are M29 roles verified at approval time | **H** | CTO |
| BRU-MDM-20 | Changing a shared kernel concept — party, product, location, entity, document, event — requires architectural review in addition to domain approval (`02-01` §3) | **H** | CTO |
| BRU-MDM-21 | Data quality results gate dependent warehouse refreshes; a failing test blocks the load (DI-06) | **H** | CTO |
| BRU-MDM-22 | Every change request retains its justification; an approval without a stated reason is not accepted | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

Includes the two entities reallocated from M30 (`05-02` §M30) under the v2.1 re-scope.

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.master.data.domain` | `fix_master_data_domain` | **The governed domain register** *(from M30)* | code, name, owning_module, business_owner_id, steward_id, deputy_steward_id, technical_custodian_id, criticality, record_volume, governance_level, is_kernel_concept, active |
| `fix.governed.attribute` | `fix_governed_attribute` | Which attributes are governed | domain_id, model, field, governed, change_significance (routine/significant/critical), mandatory, editable_directly, description_bn, description_en |
| `fix.mdm.change.request` | `fix_mdm_change_request` | **The only path to governed data** *(from M30)* | number, domain_id, change_type (create/update/deactivate/merge/bulk), proposer_id, justification, records_affected, before_json, after_json, state, quality_result, impact_summary_ref, emergency, created_at, published_at |
| `fix.mdm.change.approval` | `fix_mdm_change_approval` | Approval record | change_request_id, approver_id, authority_basis, decision, reason, impact_reviewed, decided_at, architectural_review_ref |
| `fix.data.steward.assignment` | `fix_data_steward_assignment` | Steward and deputy per domain | domain_id, steward_id, deputy_id, business_function, effective_from, effective_to, assigned_by |
| `fix.quality.rule` | `fix_quality_rule` | The rule engine | code, domain_id, model, field, dimension (completeness/validity/consistency/uniqueness/referential/timeliness), expression, classification (blocking/warning/advisory), message_bn, message_en, owner_id, version, active |
| `fix.quality.result` | `fix_quality_result` | Evaluation outcome per record | rule_id, model, res_id, passed, evaluated_at, rule_set_version, failure_detail, remediated_at, remediated_by |
| `fix.quality.score` | `fix_quality_score` | Aggregated scoring | scope (record/domain/estate), scope_id, period, completeness, validity, consistency, uniqueness, referential, timeliness, weighted_score, record_count, computed_at |
| `fix.quality.remediation` | `fix_quality_remediation` | Steward worklist item | quality_result_id, domain_id, priority, business_impact, assigned_to, due_by, state, resolution, resolved_at |
| `fix.match.rule` | `fix_match_rule` | Duplicate detection configuration | domain_id, algorithm (deterministic/fuzzy/hybrid), attributes, weights, bengali_normalisation, auto_merge_threshold, review_threshold, active |
| `fix.match.candidate` | `fix_match_candidate` | A suspected duplicate pair | domain_id, record_a_id, record_b_id, confidence, matched_attributes, detected_at, state (suspected/reviewing/merged/dismissed), dismissed_reason |
| `fix.survivorship.rule` | `fix_survivorship_rule` | Attribute-level merge resolution | domain_id, field, strategy (most_recent/most_complete/most_trusted/steward), trusted_source_order, priority |
| `fix.mdm.merge` | `fix_mdm_merge` | Merge execution and audit | domain_id, surviving_id, merged_ids, attribute_resolutions_json, executed_by, executed_at, references_notified, unmerged_at, unmerge_reason |
| `fix.reference.list` | `fix_reference_list` | **Code list master** | code, name_bn, name_en, domain_id, owner_id, description, allows_custom_values, entity_scoped, version, active |
| `fix.reference.value` | `fix_reference_value` | A value within a list | list_id, code, label_bn, label_en, sort_order, parent_value_id, attributes_json, effective_from, effective_to, state (effective/superseded/retired), superseded_by_id |
| `fix.reference.crossref` | `fix_reference_crossref` | Internal ↔ external mapping | list_id, internal_value_id, external_system, external_code, external_label, effective_from, effective_to, owner_id, verified_at |
| `fix.business.parameter` | `fix_business_parameter` | **Thresholds and rule values M63 executes** | key, name_bn, name_en, domain_id, type, value, unit, scope_level (global/entity/branch/segment), scope_id, owner_id, validation_rule, requires_approval, effective_from, effective_to, description |
| `fix.business.parameter.version` | `fix_business_parameter_version` | Parameter change history | parameter_id, version, previous_value, new_value, change_request_id, approved_by, effective_from, reason |
| `fix.mdm.hierarchy` | `fix_mdm_hierarchy` | Governed hierarchies | code, name, domain_id, type (classification/rollup/segmentation), max_depth, owner_id, version, effective_from |
| `fix.mdm.hierarchy.node` | `fix_mdm_hierarchy_node` | A node within a hierarchy | hierarchy_id, code, label_bn, label_en, parent_node_id, level, sort_order, mapped_records_count, active |
| `fix.mdm.lineage` | `fix_mdm_lineage` | Origin and dependency graph | source_type (attribute/reference/parameter), source_id, dependent_type (module/report/rule/integration/api), dependent_ref, dependency_kind, discovered_at, last_verified_at |
| `fix.mdm.impact.analysis` | `fix_mdm_impact_analysis` | Pre-approval impact | change_request_id, dependents_json, affected_record_count, affected_modules, affected_reports, risk_note, generated_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party`, party attributes | **M33** | Governed; M33 owns content, M64 owns the change path |
| `fix.catalogue.item`, part and service definitions | **M37** | Governed; same split |
| `fix.branch`, `fix.entity`, `fix.cost.center`, `fix.business.line` | **M30** / **M54** | Governed change process; M30 owns the objects |
| `fix.supplier.profile`, spend categories | M42 | Governed |
| Chart of accounts, tax codes | M19 / M51 | Governed change process; M19 owns accounting meaning |
| `fix.stock.ownership.class` | M15 | Reference data distributed by M64 |
| `fix.role`, approver rights | **M29** | **M64 asks M29 whether the actor may approve; it makes no access decision** |
| `fix.config.parameter` | M30 | Referenced for boundary clarity; **technical parameters are not M64's** |
| `fix.country.pack`, locale reference data | M65 | Governed change process; M65 owns jurisdiction content |
| Business rule definitions and workflow | **M63** | **M63 executes the parameters M64 stores** |
| Warehouse load state, data quality gate | M62 | Publish quality results |
| `fix.document` | M24 | Attachments to change requests |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-MDM-01 | Direct edit attempted on a governed attribute | Block; explain which domain governs it; offer to open a change request pre-populated | **Hard block** on every path — UI, API, import, script |
| AUT-MDM-02 | Change request submitted | Check mandatory attributes, evaluate quality rules, generate impact analysis, route to the right approver | Hold in enrichment; notify the proposer with what is missing |
| AUT-MDM-03 | Blocking quality rule fails on a request | Return to the proposer naming the failing rules in their language | Hard block on progression |
| AUT-MDM-04 | Change request approved | Publish atomically to the owning module with effective dating; emit the domain event; notify consumers | Retry; hold as approved-unpublished and alert |
| AUT-MDM-05 | Change request idle beyond its SLA | Escalate to the deputy steward, then to the business owner | Report on the ageing worklist |
| AUT-MDM-06 | Emergency change applied | Notify the steward, business owner and CTO immediately; start the 24-hour clock | Escalate |
| AUT-MDM-07 | Emergency change not retrospectively approved within 24 hours | **Revert automatically**; escalate to CTO | Hard revert |
| AUT-MDM-08 | Record created or changed in a governed domain | Evaluate its quality rules; score it; add failures to the steward worklist ranked by business impact | Queue and retry |
| AUT-MDM-09 | Scheduled (nightly) | Re-evaluate quality across all governed domains; recompute scores; detect records degraded by external change | Retain previous scores; alert |
| AUT-MDM-10 | Quality score for a domain falls below its threshold | Alert the steward and business owner with the contributing rules and trend | Report only |
| AUT-MDM-11 | Record entered in a governed domain | Run duplicate detection; auto-merge above the domain threshold, otherwise raise a candidate for steward review | Raise the candidate for review |
| AUT-MDM-12 | Merge executed | Apply survivorship attribute by attribute; publish the golden record; **notify every module holding a reference** | Retry notification; report unnotified references |
| AUT-MDM-13 | Reference value published or retired | Distribute to every consumer by API cache invalidation and event; keep the retired value resolvable | Retry; alert on stale consumers |
| AUT-MDM-14 | Business parameter change approved | Publish with its effective date; notify M63 and every consuming module; version the previous value | Retain the previous value; alert |
| AUT-MDM-15 | Change proposed to an attribute, reference value or parameter | Generate impact analysis from live lineage before it reaches approval | Block approval without impact analysis |
| AUT-MDM-16 | Nightly | Refresh lineage from actual dependencies — API consumers, event subscribers, report definitions, rule references | Retain previous lineage; flag as stale |
| AUT-MDM-17 | Data quality evaluation completes for a warehouse-relevant domain | Publish the gate result to M62; a failure blocks dependent refreshes (DI-06) | Block the refresh; alert |
| AUT-MDM-18 | New module reaches its wave gate | Require its master data domains, stewards, rules and significance model to be registered before release | **Block the release** |
| AUT-MDM-19 | Reference value or parameter approaching its effective-to date | Notify the owner to extend, supersede or retire | Report only |
| AUT-MDM-20 | Hierarchy change proposed | Validate for cycles, orphans and level violations before approval | Reject with the violation identified |

---

## 12. Interfaces

### 12.1 Upstream — M64 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M29 Identity** | Approver rights verification; steward role assignment | REST (M64 makes no access decision) |
| **M30 Platform Admin** | Entity, branch and cost-centre objects whose changes M64 governs; technical parameter registry for boundary clarity | REST |
| **M33 Party Master** | Party records and attributes under governance | REST + events |
| **M37 Catalogue** | Part, product and service definitions under governance | REST + events |
| **M28 Integration** | Event outbox; API consumer registry for lineage discovery | Framework |
| M62 Data Platform | Report and pipeline definitions for lineage discovery | REST |
| M63 Process Automation | Rule definitions referencing parameters, for lineage | REST |
| M42 / M16 / M19 / M21 / M11 | Domain content whose change process M64 governs | REST |
| M65 Localisation | Jurisdiction reference data under governance | REST |
| M24 Documents | Attachments and evidence on change requests | REST |

### 12.2 Downstream — M64 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M63 Process Automation** | **Business parameters and thresholds that M63 executes** | REST + events |
| **Every module** | Reference data and code lists; governed change publication; quality results | REST + events |
| **M33 Party Master** | Duplicate candidates, survivorship rules, merge execution, quality results | REST + events |
| **M37 Catalogue** | Quality results, classification hierarchies, governed change publication | REST + events |
| M15 / M16 / M42 | Part, supplier and spend-category quality and reference data | Events |
| M11 Pricing | Price-book governance, discount ceilings, approval bands | REST |
| M19 / M51 / M54 | Chart of accounts, tax code and cost-centre governance | Events |
| **M62 Data Platform** | **Quality gate results that block dependent warehouse refreshes** | Events |
| M25 BI | Quality scores, stewardship metrics, hierarchy structures for reporting | Warehouse extract |
| M26 AI/ML | Quality and lineage context for training data selection | Warehouse extract |
| M29 Identity | Governed changes as audit evidence | Events |
| M60 GRC | Data governance control evidence | Events |
| P03 Admin Portal | The steward console | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `mdm.change_requested` | request, domain, records, proposer, significance | steward, business owner |
| `mdm.change_approved` | request, approver, impact summary | owning module |
| `mdm.change_published` | domain, records, attributes changed, effective from | **owning module + all consumers** |
| `mdm.change_rejected` | request, reason, approver | proposer |
| `mdm.emergency_change` | request, records, actor, notification recipients | steward, business owner, CTO |
| `mdm.emergency_reverted` | request, reason, reverted at | CTO, steward |
| `mdm.quality_failed` | domain, record, rules failed, classification | owning module, steward |
| `mdm.quality_score_published` | scope, period, dimensions, weighted score, trend | M25, M62, business owner |
| `mdm.quality_gate_result` | domain, pass/fail, failing rules | **M62** (warehouse load gate) |
| `mdm.duplicate_detected` | domain, candidate pair, confidence | steward, owning module |
| `mdm.records_merged` | domain, surviving id, merged ids, attribute resolutions | **all modules holding a reference** |
| `mdm.records_unmerged` | domain, restored ids, reason | all modules holding a reference |
| `mdm.reference_published` | list, value, labels, effective from | **all consumers** |
| `mdm.reference_retired` | list, value, retired at, successor | all consumers |
| `mdm.crossref_changed` | list, internal code, external system, external code | M09, M44, M16, M19 |
| `mdm.parameter_changed` | parameter, previous value, new value, effective from, approver | **M63** + consuming modules |
| `mdm.hierarchy_changed` | hierarchy, nodes added/moved/removed, version | owning module, M25 |
| `mdm.steward_assigned` | domain, steward, deputy, effective from | M29, M21 |
| `mdm.domain_registered` | domain, owning module, steward, criticality | M30, M62 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-MDM-01 | Brand partner part-number and model catalogues | Inbound | External cross-reference for warranty claim matching (supports M09 and M15) |
| INT-MDM-02 | **NBR tariff / HS code schedule** | Inbound | HS code cross-reference maintained as governed reference data (consumed by M44) |
| INT-MDM-03 | Bangladesh Bank branch and routing code list | Inbound | Bank and branch reference data for M50 and M52 |
| INT-MDM-04 | Bangladesh administrative geography (divisions, districts, upazilas) | Inbound | Address hierarchy reference data (consumed by M33, M30, M65) |
| INT-MDM-05 | Standard unit-of-measure and currency code lists (ISO) | Inbound | Governed reference data |
| INT-MDM-06 | Legacy master data extracts | Inbound, one-time | Migration staging with quality assessment before load |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/mdm/domains` | GET/POST | Domain register with stewards and governance level | P03, all modules |
| `/api/v1/mdm/change-requests` | GET/POST | Raise and track a governed change | P03, all modules |
| `/api/v1/mdm/change-requests/{id}/approve` | POST | Approve or reject with reason | P03 |
| `/api/v1/mdm/change-requests/{id}/impact` | GET | Impact analysis before approval | P03 |
| `/api/v1/mdm/steward/worklist` | GET | **The steward's ranked daily worklist** | P03 |
| `/api/v1/mdm/quality/rules` | GET/POST | Quality rule definition per domain | P03 |
| `/api/v1/mdm/quality/evaluate` | POST | Evaluate a record against its domain rules | All modules |
| `/api/v1/mdm/quality/score` | GET | Score by record, domain or estate, decomposed by dimension | P03, P06, M62 |
| `/api/v1/mdm/quality/gate/{domain}` | GET | **Warehouse load gate result** | **M62** |
| `/api/v1/mdm/duplicates` | GET | Suspected duplicates for review | P03, M33, M37 |
| `/api/v1/mdm/duplicates/{id}/merge` | POST | Execute a merge with survivorship | P03, M33 |
| `/api/v1/mdm/merges/{id}/unmerge` | POST | Reverse a merge | P03 |
| `/api/v1/reference/{list}` | GET | **Resolve a code list — called by every module** | **All modules, all portals** |
| `/api/v1/reference/{list}/values/{code}` | GET | Resolve one value, including retired values historically | All modules |
| `/api/v1/mdm/reference` | POST | Propose a reference value change | P03 |
| `/api/v1/mdm/crossref` | GET | Internal ↔ external code mapping | M09, M44, M16, M19 |
| `/api/v1/parameters/{key}` | GET | **Resolve a business parameter for a scope** | **M63, all modules** |
| `/api/v1/mdm/parameters` | GET/POST | Parameter registry and change proposal | P03 |
| `/api/v1/mdm/hierarchies/{code}` | GET | Governed hierarchy structure | M25, M16, M37, M62 |
| `/api/v1/mdm/lineage/{type}/{id}` | GET | What depends on this attribute, value or parameter | P03, all modules |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R02 Chief Technology Officer | C R U D A | All domains; approves kernel-concept changes with architectural review |
| **Data Steward** *(a domain-scoped grant, not a distinct `05-04` role — see the note below)* | C R U A | **Own domain only**: change request review, quality remediation, duplicate resolution, reference data proposal |
| R17 Inventory Manager | C R U A | Steward grant for the **part and stock reference** domains |
| R19 Procurement Officer | C R U A | Steward grant for the **supplier and spend category** domains |
| R04 Chief Commercial Officer | C R U A | Business owner for **customer, catalogue, pricing** domains |
| R26 Finance Manager | C R U A | Steward grant for **chart of accounts, tax code, cost centre** domains |
| R30 HR Manager | C R U A | Steward grant for **employee and position** domains |
| R32 Quality Manager / ISO Coordinator | C R U A | Steward grant for **fault code, checklist, condition grade** domains |
| R03 Chief Financial Officer | R A | Business parameters with financial consequence: approval bands, credit limits, discount ceilings, write-off thresholds |
| R33 IT / System Administrator | R U | Rule configuration, matching thresholds, technical operation; **no approval rights on business content** |
| R06 Branch Manager | C R | Propose changes; no approval rights |
| All internal users | C R | **Propose** a change request; read reference data |

> **Role gap — audit action.** `05-04` §1 contains **no Data Steward role**. M64 is designed
> around named stewards drawn from business functions, and the specification currently
> implements this as a **domain-scoped grant layered on existing business roles** (R17, R19,
> R26, R30, R32 and others). Whether Data Steward becomes a distinct role — **R39/R40** — is an
> open question (Q-02) and an audit action against `05-04`. The same gap was recorded for Demand
> Planner in Category E.

**Field-level restrictions.** Business parameters with financial consequence display their
value only to R01–R05, R26, R27 and the named owner. A steward sees the parameters in their own
domain, not the estate's.

**Segregation of duties.**
- **A proposer cannot approve their own change request** (BRU-MDM-06) — hard block.
- A steward cannot approve a change to a parameter they own where the change benefits their own performance measure; such parameters route to the business owner.
- The person who defines a quality rule cannot be the sole approver of an exception to it.
- IT administrators configure the engine and **cannot approve business content**.
- Merge execution and merge approval are separate actors above a domain-specific record-count threshold.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Steward console** | Data stewards | Real time | Ranked worklist: pending requests, failing rules, duplicate candidates, expiring reference data — with business impact per item |
| **Master data quality scorecard** | CTO, business owners, stewards | Monthly | Score by domain and dimension against the **> 97% target**; trend; top failing rules |
| **Governance compliance** | CTO, Internal Audit | Monthly | **Share of changes made through the approved workflow — target 100%**; blocked direct-edit attempts; emergency changes and their regularisation |
| Change request throughput | CTO, business owners | Weekly | Requests by domain and state, ageing, SLA attainment, rejection reasons |
| Duplicate and merge activity | Stewards, M33, M37 | Monthly | Candidates detected, auto-merged, steward-merged, dismissed, unmerged; match-rule effectiveness |
| **Reference data register** | All module owners | On change | Every code list, its values, owners, versions and consumers |
| Cross-reference coverage | M09, M44, M16 owners | Monthly | External mappings present and verified — brand part numbers, HS codes, bank codes — with gaps highlighted |
| **Business parameter register** | CFO, CCO, business owners | On change | Every parameter, its value, owner, scope, effective date and last change |
| Parameter change log | CFO, Internal Audit | Monthly | Every business parameter change with approver, justification and impact |
| Impact analysis coverage | CTO | Monthly | Changes approved with impact analysis reviewed — target 100% |
| Lineage completeness | CTO, M62 | Quarterly | Attributes and parameters with discovered lineage; stale lineage |
| Quality gate effect | M62, CTO | Monthly | Warehouse refreshes blocked by quality failures and their causes |
| Migration data quality | CTO, migration leads | Per cutover | Quality assessment of each load before and after, with rejected records |
| Steward performance | CTO, business owners | Quarterly | Worklist ageing, remediation rate, domain quality trend by steward |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | **Master data changes made through the approved workflow** | 0% | 95% | **100%** |
| — | **Master data quality score** | unmeasured | 92% | **> 97%** |
| — | Blocked direct-edit attempts *(evidence the control is working)* | n/a | tracked | tracked |
| — | Governed domains with a named steward and business owner | 0% | **100%** | **100%** |
| — | Duplicate records in governed domains | unknown | < 2% | **< 0.5%** |
| — | Duplicates detected at entry rather than after | 0% | 80% | **95%** |
| — | Change requests approved within SLA | n/a | 90% | **97%** |
| — | Changes approved with impact analysis reviewed | 0% | **100%** | **100%** |
| — | Emergency master data changes regularised within 24 hours | n/a | 95% | **100%** |
| — | Modules holding a private copy of a governed code list | unknown | **Zero** | **Zero** |
| — | Business parameter changes requiring a code release | 100% | < 15% | **< 5%** |
| — | Configuration changes without a code release *(shared with M30)* | unmeasured | 85% | **> 95%** |
| — | Warehouse refreshes blocked by a quality gate failure | n/a | tracked | **< 1%** |
| — | Reference values retired but still resolvable historically | n/a | **100%** | **100%** |
| — | Cross-reference coverage for warranty-critical brand codes | unknown | 90% | **99%** |

> **Register note.** `_CATEGORY_OVERVIEW.md` §9 names **master data changes through the approved
> workflow (100%)** and **master data quality score (> 97%)** as the category KPIs owned by M64.
> **Neither has a canonical `KPI-0nn` identifier** — `06-02` §2.6 ends at KPI-049 with no
> platform or data-governance section. Allocation for all fifteen metrics is an audit action.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `base` — ORM write hooks, `ir.model` metadata, base validation | 12% |
| L2 | OCA `server-tools` (technical utilities, audit hooks), `base_exception` (rule-driven blocking), `partner-contact` matching helpers | 18% |
| L5 | `cd_mdm`, `cd_data_quality`, `cd_reference_data` | 70% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 2 of 3 identifiers below are claimed by another module: **CD-160** also claimed by M19, M45; **CD-161** also claimed by M20, M45. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-134 | `cd_mdm` — domain register, governed attribute model, **direct-edit prevention**, change request workflow, approval routing, bulk change governance, emergency path, change audit, **steward console**, lineage and impact analysis | Odoo module + frontend | 8 PW |
| **CD-160** | `cd_data_quality` — rule engine across six dimensions, classification and gating, scoring, continuous evaluation, remediation worklist, **warehouse load gate**, duplicate matching with Bengali normalisation, attribute-level survivorship, merge and unmerge | Odoo module + service | 6 PW |
| **CD-161** | `cd_reference_data` — code list master, versioning and effective dating, distribution and cache invalidation, cross-reference mapping, **business parameter registry**, parameter versioning, hierarchy management and integrity | Odoo module | 3 PW |

> CD-134 `cd_mdm` is **reallocated from M30**, where `02-05` §5.2 originally placed it.
> CD-160 and CD-161 are claimed from the extension block for modules M31–M67. **All CD IDs
> remain provisional** pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M30 Platform Admin (W1)** | Entity, branch and cost-centre objects; the technical/business parameter boundary must be settled before the hand-off |
| **M29 Identity (W1)** | Approver rights verification; steward role grants |
| **M28 Integration (W1)** | Event outbox for publication and distribution; API registry for lineage discovery |
| **M33 Party Master (W1)** | The first governed domain, and the largest by volume |
| **M37 Catalogue (W1)** | The second governed domain, and the one M15 depends on in W2 |
| M62 Data Platform (W4) | The warehouse load gate connects at W4; quality evaluation works standalone before then |
| M63 Process Automation (W3) | **M63 executes the parameters M64 stores.** Until W3, parameters are read directly by modules; the M63 hand-off is additive, not disruptive |
| M60 GRC (W6) | Governance control evidence; not blocking |

> **The W2 placement is the point.** M64 must be live **before** M15 loads ~10,000 parts across
> 51+ locations and before M33's customer base reaches volume. Governing at load costs a
> fraction of remediating afterwards, and it is a precondition for M43's forecasting in W6 —
> which depends on two years of clean consumption history that only exists if the part master
> was right from the start.
>
> **Two hand-offs must be planned, not discovered.** Business parameters transfer from M30 to
> M64 at W2 (M30 Q-10), and parameter *execution* transfers to M63 at W3. Both are ownership
> migrations of live configuration.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Domain register | ~25 domains | `fix.master.data.domain` | W2, **authored** as each module is built |
| Quality rules | ~300–500 rules | `fix.quality.rule` | W2 onward, authored per domain |
| Code lists | ~200 lists, ~5,000 values | `fix.reference.value` | W2, extracted from code and legacy systems |
| Business parameters | ~300 parameters | `fix.business.parameter` | **W2, extracted from M30 and from code** |
| Cross-references (brand part numbers, bank codes) | Held by brands and in spreadsheets | `fix.reference.crossref` | W2–W3, collected |
| Hierarchies | Product, spend, cost centre | `fix.mdm.hierarchy` | W2, authored |
| Legacy master data | Assessed, not migrated by M64 | — | W2, **quality-assessed before the owning module loads it** |

> **Position on migration.** M64 migrates almost no data of its own. Its migration contribution
> is a **quality assessment gate on every other module's load**: each migration batch is scored
> against its domain rules before acceptance, and records failing a blocking rule are rejected
> to a remediation queue rather than loaded. This is the practical expression of "governance
> before volume", and it will make some migrations slower and all of them better.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A governed attribute cannot be changed directly through the UI, the API, an import or a script | Negative test on all four paths, per governed domain |
| AC-02 | 100% of changes to governed attributes in production trace to an approved change request | Full-population assertion query over four weeks |
| AC-03 | A change request cannot be approved by its proposer | Negative test |
| AC-04 | A record failing a blocking quality rule cannot be published or used in the protected operation | Negative test per blocking rule |
| AC-05 | Master data quality score reaches 92% at Wave 4 and exceeds 97% at Wave 8 | Monthly scorecards |
| AC-06 | Every governed domain has a named steward and business owner; a domain without both cannot be activated | Registry assertion plus negative test |
| AC-07 | Impact analysis is generated and presented before approval; approval without it is impossible | Negative test |
| AC-08 | A bulk change is previewed, approved as a set, and applied all-or-nothing | Scripted scenario with an induced mid-batch failure |
| AC-09 | An emergency change not regularised within 24 hours reverts automatically | Time-shifted scenario |
| AC-10 | Duplicate detection identifies a customer entered once in Bengali and once in English as one candidate | Bengali matching test set |
| AC-11 | Merge applies survivorship attribute by attribute per declared rules, reproducibly | Merge determinism test |
| AC-12 | A merge notifies every module holding a reference, and an unmerge restores pre-merge state without losing post-merge changes | End-to-end merge and unmerge scenario |
| AC-13 | A retired reference value remains resolvable for a document written before its retirement | Historical resolution test |
| AC-14 | No module holds a private copy of a governed code list | Code audit plus reference API traffic analysis |
| AC-15 | A business parameter change takes effect without a code release and is read correctly by M63 and consuming modules | End-to-end scenario (from W3) |
| AC-16 | Reference values, parameters and hierarchies resolve correctly against a past effective date | Effective-dating test |
| AC-17 | A governed hierarchy change containing a cycle, orphan or level violation is rejected | Negative test |
| AC-18 | A failing data quality gate blocks the dependent warehouse refresh | Integration test with M62 (from W4) |
| AC-19 | Every migration batch is quality-assessed before acceptance, with failing records rejected to remediation | Migration records for M15 and M33 loads |
| AC-20 | Lineage is derived from actual dependencies and refreshes nightly | Lineage accuracy test against a known dependency |
| AC-21 | Rule evaluation completes in ≤ 50 ms on save and reference resolution in ≤ 2 ms | Performance test |
| AC-22 | The steward console is complete in Bengali and usable by a business steward without technical training | Field test with three stewards from different functions (AS-12) |
| AC-23 | M64 makes no authorisation decision; approver rights are verified with M29 | Code review and negative test |
| AC-24 | CTO and at least three named business data stewards sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 24 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Which parameters are business (M64) and which are technical (M30)?** The failure-mode test resolves the principle, but 50–100 parameters need individual classification before the W2 hand-off. This is the reciprocal of **M30 Q-04**. | CTO / business owners | **W2 minus 1 month** |
| Q-02 | **Is Data Steward a distinct role (R39/R40) in `05-04`, or a domain-scoped grant on existing business roles?** The answer affects the SoD model and the headcount conversation. | HR Director / CTO | W2 design |
| Q-03 | **Who are the named stewards per domain, and does their line management accept the time commitment?** Stewardship is real work — a worklist every day. Governance fails when stewards are nominated without their manager's agreement. | Business owners / HR Director | **W2 minus 2 months** |
| Q-04 | What is the quality score weighting per dimension, and what threshold triggers escalation per domain? A part master and a marketing segment should not be held to the same standard. | CTO / business owners | W2 build |
| Q-05 | What are the auto-merge confidence thresholds per domain? Too low and customers are wrongly merged; too high and stewards drown in candidates. | Stewards / CCO | W2 build |
| Q-06 | Do brand partners supply their part-number and model catalogues in a machine-readable form (INT-MDM-01)? Warranty claim matching depends on it, and manual maintenance at this scale is not viable. | CCO / Warehouse Manager | W3 |
| Q-07 | **When exactly does parameter execution transfer to M63 (W3), and who runs that migration?** M64 stores; M63 executes. Between W2 and W3, modules read parameters directly. | CTO | W3 planning |
| Q-08 | Does the migration quality gate have authority to **reject** a migration batch, or only to report on it? If only to report, "governance before volume" is not real. | CTO / programme manager | **W2 minus 1 month** |
| Q-09 | What is the escalation when a steward's domain quality score stays below threshold for three consecutive months? Governance without consequence decays. | CTO / business owners | W4 |
| Q-10 | How are governed changes handled during a wave cutover, when large volumes of master data are created legitimately and at speed? A blanket exemption would undermine the control. | CTO / programme manager | W2 build |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2, §5 (**the M30/M64 boundary — audiences, failure modes, analogues**),
§6 (boundary map — M37 owns catalogue content, M33 owns party content, M63 executes rules),
§7 promise 6, §9 (category KPIs), §10 (W2 — "data governance before volume arrives"),
§11 (bypass risk and its mitigation) ·
`M30_Platform_Administration_and_Configuration.md` §3.2, §16.3, Q-04, Q-10 (**the reciprocal boundary and the W2 hand-off**) ·
`M29_Identity_Access_and_Information_Security.md` (approver rights; M64 makes no access decision) ·
`M28_Integration_API_and_Event_Platform.md` (event distribution, lineage discovery) ·
`M65_Multi_Entity_Multi_Country_and_Localisation.md` (jurisdiction reference data) ·
`M63` Process Automation & Workflow Orchestration *(Category J — **executes the parameters M64 stores**)* ·
`M33` Customer & Party Master Management *(Category B — owns party content)* ·
`M37` Product & Service Catalogue Management *(Category C — owns catalogue content)* ·
`M62` Data Platform, Warehouse & Governance *(Category J — the quality load gate)* ·
`05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` §11 (**BRU-ADM-01**) ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md`
NFR-027, **DI-03, DI-06**, AS-03, AS-08, AS-12 ·
`05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §M30
(`fix.master.data.domain`, `fix.mdm.change.request` — **reallocated to M64**) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §1 (**no Data Steward role — audit action**) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §3 (**the shared kernel and architectural review**) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 (CD-134 reallocated from M30)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-INV-009, BR-INV-010
(part catalogue and classification — governed here, authored in M37) ·
Executive Summary §6.2 (inventory, warranty and pricing benefits that depend on master data quality)

**External benchmark**
[SAP Master Data Governance — golden records, governed model, data quality rules, stewardship workflows](https://www.sap.com/products/data-cloud/master-data-governance.html) ·
[SAP MDG — workflows, roles, responsibilities and data stewardship across the organisational hierarchy](https://www.verdantis.com/sap-master-data-governance/) ·
[SAP MDG complete guide 2025 — governance framework and accountability](https://mdpgroup.com/en/blog/sap-master-data-governance-sap-mdg/) ·
[Master data governance best practice — dedicated data owners, golden record per entity, continuous monitoring, steward–business collaboration](https://insightsoftware.com/encyclopedia/master-data-governance/) ·
[Maintaining data quality with SAP MDG — validation for formats, classifications and regulatory checks](https://fastercapital.com/content/Maintaining-Data-Quality-with-SAP-Master-Data-Governance.html) ·
Oracle Product Hub and Customer Hub — attribute-level survivorship, match and merge ·
Informatica MDM — stewardship console, data quality scorecards, lineage

---

*Module M64 · Category K · 1000FiX ERP System v2.0 · CONFIDENTIAL*
