---
id: CG-004
title: Terminology and Controlled Vocabulary Standard
project: 1000FiX ERP System v2.0
content_type: Standard
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture
author: Enterprise Architecture with Content Design
reviewers: [Content Design Lead, Localisation Lead, Business Owners Forum, Legal & Compliance]
approver: Architecture Review Board
purpose: >
  Fixes one approved term for every business object and action in the ERP, binds each term to
  the data entity it names, and bans the synonyms. "Job", "ticket", "order", "case" and
  "request" cannot all mean fix.service.order. Ambiguity here propagates into UI, training,
  SOPs, reports, statutory documents and every Bengali translation, and cannot be corrected
  cheaply once 452 files cite it.
traces_to: [05-02 Entity Catalogue, 05-01 §1, CG-003, BN-003, MD-027, RP-001]
priority: P0
wave: W0
bilingual: no
bn_counterpart: BN-003 (Bilingual Terminology Glossary — binds Bengali equivalents to this file)
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 Data Model & Entity Catalogue — fix.* model register
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/02_Architecture/02-02 §5 complete 67-code module register
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 Role register R01–R38
    verified: 2026-08-15
  - source: 1000_fix_corporate_website project_content BN-002 Bengali Glossary/Terminology v1.0
    verified: 2026-08-15
supersedes: none
review_due: 2026-11-15
---

# CG-004 — Terminology and Controlled Vocabulary Standard

> **The single most expensive content decision in the programme.** Every term fixed here is
> cited by UI labels, error messages, notifications, printed documents, SOPs, training, reports,
> API field descriptions and Bengali translations. A term changed after Wave 2 is a
> co-ordinated edit across hundreds of files and a re-translation.
>
> **Fix the vocabulary before the first label is written.**

---

## 1. Why a controlled vocabulary, not a glossary

A glossary explains terms to readers. A **controlled vocabulary decides which term exists at
all** and forbids the rest. The difference matters because the failure mode is not that readers
misunderstand a word — it is that four teams independently choose four different words for the
same object and every downstream artefact inherits the divergence.

The workspace already contains evidence of this happening:

| Evidence | What it shows |
|---|---|
| `M42` carries module code `SRM2` because `SRM` was permanently allocated to `M01` — *Supplier Relationship Management* and *Service & Repair Management* collide on the natural abbreviation (`02-02` §5 code note) | Two domains reached for the same three letters. Only a register prevented the collision |
| `M04` briefly used code `BFO` in drafting before reverting to its permanent code `FRD`; `BFO` is now retired and will never be reissued (audit finding C-03) | An identifier used in drafting propagates faster than it can be recalled |
| The website content set uses *Localization*; the ERP set uses *Localisation* (`CG-003` §1.1) | The same programme, two spellings of the same domain, already shipped |

This file exists so that the fourth and subsequent instances do not happen.

---

## 2. Governing rules

| # | Rule |
|---|---|
| **T-01** | **One term, one meaning.** A term in this vocabulary means exactly one thing across all 452 content files, twelve portals and both languages. |
| **T-02** | **One meaning, one term.** Where two words describe the same object, one is approved and the other is banned. Synonyms are not "acceptable variants"; they are defects. |
| **T-03** | **Every business-object term binds to an entity.** The approved term names a `fix.*` model from `05-02`. A term with no entity behind it is either a concept (allowed, §6) or scope creep (refused). |
| **T-04** | **The entity owner owns the term.** The module that owns the entity in `05-02` owns its approved term, its definition and any change to it. |
| **T-05** | **Statutory terms are never paraphrased.** Where an instrument names a thing — *Mushak 6.3*, *VDS*, *BIN* — that name is used exactly, in both languages, and appears in the do-not-translate register (`BN-004`). |
| **T-06** | **Internal state names and customer-facing labels are different things.** The internal state lives in `05-02` DM-10; the customer-facing label lives in `MD-027`. Never show an internal state name to a customer. |
| **T-07** | **A term is not approved until its Bengali equivalent is approved.** `BN-003` and this file are ratified together, never separately (`T-13`). |
| **T-08** | **Register-first.** A new term is added to this vocabulary before it appears in any content file. This is `RG-01` applied to words. |
| **T-09** | **Terms are permanent in the same sense IDs are.** A term may be deprecated; its meaning may not be reassigned to a different object. |
| **T-10** | **Precedence resolves conflict**, in the order set out in §3. |
| **T-11** | **Role names come from `05-04`, not from job adverts.** Content refers to a role by its registered name. |
| **T-12** | **Module and portal references use IDs**, not paraphrases: `M01`, `P02`. Never "the service module". |
| **T-13** | **Changing an approved term requires** the entity owner's agreement, Architecture Review Board ratification, a Bengali re-approval, an impact list of every citing file, and a logged decision in `RF-006`. |

---

## 3. Precedence — which term wins

When two candidate terms are both defensible, apply this order. Stop at the first rule that
decides.

| # | Precedence | Rationale | Example |
|---:|---|---|---|
| 1 | **Statutory or regulatory name** | The instrument's wording is not ours to improve | *Mushak 6.3*, not "VAT invoice form" |
| 2 | **Contractually binding name** | The term appears in signed agreements | *Service credit*, as defined in `LG-015` |
| 3 | **The term already used in an approved specification** | 123 approved documents already use it; changing costs more than it saves | *Service order* (used throughout `M01`, `M31`, `P01`, `P03`) |
| 4 | **The term the business uses today** | Training cost is lower and adoption higher | *Branch* over *operating unit* in internal content |
| 5 | **The term the customer understands** | Applies only to customer-facing surfaces | *Repair estimate* over *quotation* on `P01` |
| 6 | **The Odoo or technical model name** | Last resort; developer-facing content only | `operating_unit_id` in API documentation |

> **Precedence 4 versus 5 conflict.** Where internal and customer-facing surfaces genuinely need
> different words, both are approved and the vocabulary records **which surface uses which**.
> This is not a synonym; it is a registered surface-specific term (see *branch* / *service
> centre* in §4.1). Any such pair must be explicitly recorded here — an unrecorded pair is a
> defect.

---

## 4. The controlled vocabulary

Terms are grouped by domain. Each row gives the approved term, the entity it binds to, the
owning module, its definition, and the banned alternatives.

> **Coverage.** This issue covers the **core transactional vocabulary** — the terms that appear
> across more than one module and therefore cannot be settled locally. Domain-specific terms
> that appear in one module only are settled in that module's `MD` or `SP` file and registered
> here on first cross-module use. `RF-001` holds the full glossary including terms that are
> explanatory rather than controlled.

### 4.1 Organisation and network

| Approved term | Entity | Owner | Definition | Banned |
|---|---|---|---|---|
| **branch** | `fix.branch` | `M04` | A physical 1000FiX operating location. Used in internal content. | outlet, shop, store, unit, location (bare) |
| **service centre** | `fix.branch` | `M04` | The same object, on customer-facing surfaces. Registered surface-specific pair with *branch*. | service center (en-US), workshop (means something else) |
| **workshop** | `fix.branch` (type) | `M31` | A branch or depot location where bench repair is performed. Not a synonym for branch. | lab, back office, repair room |
| **zone** | `fix.zone` | `M02` | A dispatch and territory boundary used for routing, charging and SLA. | area, region, territory, sector |
| **entity** | `fix.entity` | `M65` | A legal company within the group, with its own tax identity. | company (ambiguous), organisation |
| **business line** | `fix.business.line` | `M54` | A revenue-stream reporting dimension. One of fourteen. | vertical, stream (bare), division |
| **cost centre** | `fix.cost.center` | `M54` | A financial reporting dimension. Note: entity name uses US spelling; **content uses en-GB**. | cost center (in content), department (means something else) |

> **Spelling exception recorded.** The model is `fix.cost.center` and the column is
> `cost_center_id`. Technical identifiers are never re-spelled (`CG-003` §1.1). All prose,
> labels and documents write **cost centre**. This divergence is deliberate and registered.

### 4.2 Party and people

| Approved term | Entity | Owner | Definition | Banned |
|---|---|---|---|---|
| **party** | `fix.party` | `M33` | Any person or organisation the company deals with. The umbrella object. | entity (means a legal company), contact, record |
| **customer** | `fix.party` + role | `M33` | A party that buys or receives service. Default term on all consumer surfaces. | consumer, end user, client (reserved), buyer |
| **client** | `fix.party` + role | `M07` | **Reserved** for a contracted corporate or government account. Never used for an individual. | — |
| **technician** | `fix.technician.profile` | `M21` | An employee who performs repair or field work. | tech, mechanic, engineer (reserved), serviceman |
| **engineer** | `fix.party` + seller role | `M12` | **Reserved** for an external marketplace freelance engineer. Never used for an employee. | — |
| **seller** | `fix.party` + role | `M12` | An approved marketplace participant — freelance engineer or shop. | vendor (reserved), partner (reserved), merchant |
| **vendor** | `fix.party` + role | `M16` | **Reserved** for a supplier of parts, services or logistics. | supplier is an accepted synonym in procurement content only; see note |
| **brand partner** | `fix.brand` | `M09` | An authorised manufacturer whose warranty work the company performs. | OEM (permitted in technical content only), principal, manufacturer (bare) |
| **partner** | `fix.alliance.partner` | `M40` | **Reserved** for an alliance, referral or channel partner. Never a vendor or seller. | — |
| **employee** | `hr.employee` (ext) | `M21` | A person employed by an entity in the group. | staff member, resource, headcount |
| **rider** | `fix.party` + role | `M03` | A person performing collection and delivery. | courier (means the partner organisation), driver, delivery boy |

> **vendor / supplier.** `05-02` and `M16` use both. *Vendor* is approved for UI labels, master
> data and documents; *supplier* is permitted in procurement prose and in the registered
> compound *Supplier Relationship Management* (`M42`). This is the one accepted near-synonym in
> the vocabulary and it is registered rather than tolerated.

### 4.3 Service and work

| Approved term | Entity | Owner | Definition | Banned |
|---|---|---|---|---|
| **service order** | `fix.service.order` | `M01` | The record of a customer's request for service on a device, from intake to closure. **The single most-cited object in the system.** | job, ticket, case, request, repair order, work request, SR (in prose) |
| **job** | `fix.dispatch.job` | `M02` | A dispatchable unit of field work derived from a service order. Not a synonym for service order. | visit, call, assignment, task |
| **work order** | `fix.work.order` | `M31` | A workshop or bench execution record derived from a service order. | repair job, bench ticket |
| **task** | `fix.work.order.task` | `M31` | A step within a work order. | activity (reserved), step, operation |
| **service request** | — | `M01` | The customer's **act** of requesting, before a service order exists. A phase, not an entity. | enquiry, lead (reserved), booking (permitted on `P01` only) |
| **estimate** | `fix.estimate` | `M01` | A priced proposal for repair work on a specific device, requiring customer approval. | quote, quotation (reserved), proposal, costing |
| **quotation** | — | `M36` | **Reserved** for a commercial quotation to an organisation, including tender responses. | — |
| **diagnosis** | `fix.device.condition.log` | `M31` | The technician's confirmed determination of the fault. | assessment (reserved), finding (reserved), analysis |
| **fault** | `MD-024` code | `M01` | The confirmed technical defect, coded. | issue, problem, defect (reserved for quality), error |
| **symptom** | `MD-024` code | `M01` | What the customer reports, before diagnosis. Distinct from fault. | complaint (reserved), issue, problem |
| **rework** | `fix.service.order` flag | `M23` | A repeat service order for the same device and fault category within the defined window (`BRU-SRM-06`). | redo, repeat repair, comeback, callback |
| **service report** | `fix.service.report` | `M01` | The record given to the customer on completion. | job sheet, completion note, closure report |
| **consignment** | `fix.consignment` | `M03` | A shipment of one or more devices or parts under custody. | shipment, parcel, package, delivery (ambiguous) |
| **custody** | `fix.asset.custody` | `M17` | Documented possession of a customer's device by a named party at a point in time. | possession, holding, handover (an event, not a state) |

### 4.4 Commercial

| Approved term | Entity | Owner | Definition | Banned |
|---|---|---|---|---|
| **contract** | `fix.contract` | `M08` | A binding commercial agreement for recurring service. Covers AMC, RAMC and MSP. | agreement (reserved for legal instruments), deal, package |
| **AMC** | `fix.contract` (type) | `M08` | Annual Maintenance Contract — corporate. Expand on first use in customer content. | annual contract, maintenance plan |
| **RAMC** | `fix.contract` (type) | `M08` | Residential Annual Maintenance Contract — consumer. | home AMC, residential plan |
| **entitlement** | `fix.contract.line` | `M08` | What a contract permits its holder to consume — visits, hours, coverage. | allowance, credit (reserved), quota, benefit (reserved) |
| **covered asset** | `fix.contract.covered.asset` | `M08` | A device listed on an active contract. Gating object for `BRU-SRM-03`. | contracted device, enrolled asset |
| **warranty** | `fix.warranty.register` | `M09` | A commitment to remedy a defect at no or reduced cost within a period. | guarantee, cover (bare) |
| **protection plan** | `fix.warranty.product` | `M09` | A purchased product extending or adding warranty-type cover. | extended warranty (permitted in marketing only), insurance (**never** — regulatory meaning) |
| **claim** | `fix.warranty.claim` | `M09` | A submission to a brand partner for reimbursement of warranty work. | reimbursement request, brand claim |
| **rate card** | `fix.brand.rate.card` | `M11` | A versioned, effective-dated schedule of labour and parts prices for a defined audience. | price sheet, tariff, pricing table |
| **price list** | `product.pricelist` (ext) | `M11` | The catalogue-level pricing applicable to a customer segment. | pricing, rates (bare) |
| **service credit** | `fix.contract.sla` | `M08` | A contractual financial remedy for an SLA breach. Legally defined in `LG-015`. | penalty, compensation (reserved), refund (reserved) |
| **subscription** | `fix.contract` (type) | `M39` | A recurring-revenue product billed on a cycle. | plan (bare), membership (reserved) |
| **membership** | `fix.loyalty.member` | `M10` | **Reserved** for the Privilege loyalty programme. | subscription, plan |
| **commission** | `fix.commission.entry` | `M53` | Amount retained or paid on a marketplace or partner transaction. | fee (reserved), charge (reserved), cut |

### 4.5 Finance and statutory

| Approved term | Entity | Owner | Definition | Banned |
|---|---|---|---|---|
| **invoice** | `account.move` (ext) | `M20` | A demand for payment. In Bangladesh VAT context, see *Mushak 6.3*. | bill, statement (reserved), receipt (reserved) |
| **Mushak 6.3** | `fix.mushak.invoice` | `M51` | The statutory VAT tax invoice prescribed by the National Board of Revenue. **Never paraphrased or translated.** | VAT invoice form, tax challan, NBR invoice |
| **challan** | — | `M03` / `M51` | Used only in the registered compounds *delivery challan* and *Mushak challan*. Never alone. | — |
| **receipt** | `fix.cash.movement` | `M20` | Acknowledgement that money was received. | payment slip, money receipt (permitted as the registered document title on `DT-016`) |
| **statement** | — | `M20` | A periodic account summary. Never a synonym for invoice. | account summary, ledger (reserved) |
| **credit note** | `account.move` (ext) | `M20` | The statutory adjustment document reducing a previously issued invoice. | refund note, adjustment, reversal |
| **VDS** | — | `M51` | VAT Deducted at Source. Statutory term; certificate is Mushak 6.6. | withholding VAT, source VAT |
| **BIN** | `fix.entity` field | `M51` | Business Identification Number issued by the NBR. | VAT number, VAT registration |
| **TIN** | `fix.party` field | `M51` | Taxpayer Identification Number. Classified sensitive under `05-06` NFR-086. | tax number, tax ID |
| **charge** | `fix.charge` | `M11` | A priced line applied to a service order. | fee (reserved), cost (reserved), levy |
| **fee** | — | `M12` | **Reserved** for a platform, registration or payout fee in the marketplace context. | — |
| **cost** | — | `M54` | **Reserved** for internal cost accounting. Never what a customer pays. | — |
| **price** | `fix.catalogue.item` | `M11` | What the customer pays before tax. | rate (reserved), cost, charge |

### 4.6 Supply chain and asset

| Approved term | Entity | Owner | Definition | Banned |
|---|---|---|---|---|
| **part** | `fix.part` | `M15` | A stocked component or consumable used in repair. | spare, spare part (permitted in customer content), component, item (reserved) |
| **item** | `fix.catalogue.item` | `M37` | **Reserved** for a sellable catalogue entry — product or service. | — |
| **device** | `fix.asset` | `M17` | A customer's equipment under service. | unit, machine, product (reserved), equipment (reserved) |
| **asset** | `fix.asset` | `M17` / `M45` | The umbrella object for any tracked physical thing. A *device* is a customer-owned asset; *equipment* is company-owned. | — |
| **equipment** | `fix.asset` (company) | `M45` | **Reserved** for company-owned tools and test equipment. | — |
| **stock** | `stock.quant` (ext) | `M15` | Quantity of a part at a location. | inventory (reserved), holding |
| **inventory** | — | `M15` | **Reserved** for the function and the count activity, not the quantity. | — |
| **van stock** | `fix.van.stock` | `M15` | Parts held on a technician's vehicle, under that technician's custody. | boot stock, mobile stock, technician stock |
| **location** | `fix.stock.location` | `M41` | A physical or logical storage position. Always qualified: *stock location*, *branch location*. | place, site (reserved), bin (a level of location) |
| **site** | `fix.address` | `M07` | **Reserved** for a corporate client's premises. | — |
| **transfer** | `fix.transfer.request` | `M15` | Movement of stock between locations. | move, shift, relocation |

### 4.7 Quality, governance and platform

| Approved term | Entity | Owner | Definition | Banned |
|---|---|---|---|---|
| **complaint** | `fix.complaint` | `M34` | A customer's formal expression of dissatisfaction, tracked to closure. | grievance, escalation (reserved), issue |
| **escalation** | — | `M27` | The act of raising something to a higher authority under `SP-005`. Never a synonym for complaint. | — |
| **non-conformance** | `fix.audit.finding` | `M23` | A departure from a defined requirement, raised as an NCR. | defect (reserved), problem, failure |
| **defect** | — | `M23` / `TS-018` | **Reserved** for a software or product defect. | bug (permitted in engineering content only) |
| **CAPA** | `fix.capa` | `M23` | Corrective and Preventive Action. ISO 9001 term; never paraphrased. | fix, remediation, action plan |
| **finding** | `fix.audit.finding` | `M23` | An observation raised during an audit, classified by severity. | issue, observation (a lesser class within findings) |
| **role** | `05-04` `Rnn` | `M29` | A registered access and responsibility profile. Named exactly as registered. | permission group, profile, user type |
| **permission** | — | `M29` | A specific granted capability within a role. | right, access (bare), privilege |
| **portal** | `Pnn` | `M30` | One of the twelve registered user-facing surfaces. Referenced by ID. | app (reserved), site, front end |
| **application** | `Pnn` | `M30` | A native mobile surface. `P02`, `P09`, `P11` are applications; the rest are portals. | app is permitted in customer-facing content only |
| **module** | `Mnn` | `M30` | One of the 67 registered ERP capability modules. Referenced by ID. | component, subsystem, function (reserved) |
| **event** | `05-03` catalogue | `M28` | A published domain event. Named `<object>.<past-tense-verb>`. | message, trigger (the cause, not the event), signal |

### 4.8 Actions — verbs

Verbs are as controlled as nouns. A user who learns that **approve** means one thing must not
meet **authorise**, **confirm** and **accept** doing the same job on three other screens.

| Approved verb | Meaning | Banned for this meaning |
|---|---|---|
| **create** | Bring a new record into existence | add, new, raise (reserved), open (reserved), register (reserved) |
| **raise** | **Reserved**: create a claim, NCR, complaint or requisition | — |
| **register** | **Reserved**: record a device, party or certification in a master register | — |
| **assign** | Attach a person to work | allocate (reserved), dispatch (reserved), give, route |
| **allocate** | **Reserved**: attach stock, budget or an identifier | — |
| **dispatch** | **Reserved**: release a job to the field | — |
| **approve** | Give the authority for something to proceed | authorise (reserved), accept (reserved), confirm (reserved), sign off, OK |
| **authorise** | **Reserved**: grant a permission or an override under `BR-STD-06` | — |
| **accept** | **Reserved**: a counterparty agreeing to terms or an offer | — |
| **confirm** | **Reserved**: a user verifying an action in a dialog | — |
| **reject** | Decline with a recorded reason, ending the flow | decline (reserved), deny, refuse, return (reserved) |
| **decline** | **Reserved**: a technician or seller not taking offered work | — |
| **cancel** | End a record before completion, by request | void (reserved), abort, kill, terminate, delete |
| **void** | **Reserved**: nullify a posted financial document | — |
| **close** | End a record that has run its course | complete (reserved), finish, resolve (reserved) |
| **complete** | **Reserved**: work is done and quality-passed | — |
| **resolve** | **Reserved**: a complaint or incident reaching an outcome | — |
| **submit** | Send a record to another party for action | send (reserved), post (reserved), forward |
| **post** | **Reserved**: commit a financial entry to the ledger | — |
| **issue** | Release a part, document or certificate | give, hand over (reserved), release (reserved) |
| **hand over** | **Reserved**: transfer custody of a device between named parties | — |
| **release** | **Reserved**: free a hold or reservation | — |
| **reschedule** | Change an appointment to a new time | postpone, move, delay |
| **escalate** | Raise to a higher authority per `SP-005` | flag (reserved), elevate, push up |
| **flag** | **Reserved**: mark a record for attention without changing state | — |
| **archive** | Set `active = False` per `05-02` DM-06 | delete, remove, purge |
| **delete** | Permanent destruction. **Applies to almost nothing in this system.** | — |

> **Note on *delete*.** `05-02` DM-06 requires business records to be archived, never
> hard-deleted. If content offers a user "Delete", the content is wrong or the system is
> breaching DM-06. Either way it is a defect.

---

## 5. Surface-specific registered pairs

The complete list of cases where two approved terms name one object, split by surface. **Any
pair not on this list is a defect, not a variation.**

| Object | Internal term | Customer-facing term | Entity | Registered by |
|---|---|---|---|---|
| Operating location | branch | service centre | `fix.branch` | `M04` |
| Priced repair proposal | estimate | estimate | `fix.estimate` | `M01` |
| Native mobile surface | application | app | `Pnn` | `M30` |
| Stocked component | part | spare part | `fix.part` | `M15` |
| Recurring corporate agreement | contract | AMC | `fix.contract` | `M08` |
| Recurring consumer agreement | contract | RAMC | `fix.contract` | `M08` |
| Loyalty scheme | loyalty programme | Privilege | `fix.loyalty.member` | `M10` |

---

## 6. Concepts without entities

Terms that are controlled but name a concept, phase or measure rather than a stored object.
They still have one approved form and banned alternatives.

| Term | Meaning | Banned |
|---|---|---|
| **turnaround time (TAT)** | Elapsed time from intake to release, measured per `RP-001` | turnaround, cycle time, TT |
| **first-time fix** | A service order resolved without a second visit or return | FTF (in customer content), right first time |
| **SLA** | The contractual commitment defined in `MD-028` and `LG-015` | service level (bare), response guarantee |
| **wave** | One of the nine delivery phases `W1`–`W9` | phase, sprint, stage, release (reserved) |
| **release** | A deployed software version | version (the number, not the event), build, drop |
| **hypercare** | The defined intensive-support period after a wave go-live | warranty period, stabilisation, post-go-live support |
| **cutover** | The transition from legacy to ERP for a defined scope | migration (the data activity), switchover, go-live (the moment) |
| **go-live** | The moment a wave becomes the system of record for its scope | launch, release, cutover |

---

## 7. Bengali binding

`BN-003` holds the approved Bengali equivalent for every term in this file. The two documents
are ratified together (`T-07`) and neither is authoritative alone.

| Category | Bengali approach | Reference |
|---|---|---|
| Statutory names | Never translated. Used in Latin script in Bengali content | `BN-004` do-not-translate register |
| Brand and product names | Never translated | `BN-004` |
| Technical identifiers, model names, codes | Never translated | `BN-004` |
| Common device terms | Transliterated where that is the natural usage — ল্যাপটপ, এসি, প্রিন্টার | `BN-003`, informed by the existing website glossary |
| Business objects | Translated where a settled Bengali term exists; transliterated where it does not | `BN-003` |
| Approved verbs | Translated. Verb consistency matters more in Bengali than in English because inflection multiplies the surface forms | `BN-003` |

> **Register decision required.** The corporate website's `BN-001` selected modern colloquial
> Bengali (চলিত ভাষা) for marketing content. The ERP serves branch staff, field technicians and
> statutory documents alongside consumers. **`BN-002` must decide whether one register serves
> all ERP surfaces or whether statutory and legal content uses a more formal register**, and the
> decision must be logged in `RF-006` before any `BN` string bundle is produced. This file
> records the question; `BN-002` answers it.

---

## 8. Adding, deprecating and changing terms

### 8.1 Adding

| Step | Action | Who |
|---|---|---|
| 1 | Establish that no approved term already covers the meaning | Requester |
| 2 | Identify the entity it binds to, or declare it a concept (§6) | Entity owner |
| 3 | Propose the term, definition and banned alternatives | Requester |
| 4 | Propose the Bengali equivalent | Localisation Lead |
| 5 | Ratify at the fortnightly terminology board (`CG-002` §8) | Architecture Review Board delegate |
| 6 | Add to this file and to `BN-003` in the same change | Enterprise Architecture |
| 7 | Log in `RF-006` | Programme Content Lead |

### 8.2 Deprecating

A term is deprecated, never deleted. The row stays with status `DEPRECATED`, the date, the
replacement term, and the reason. Deprecated terms are added to the automated lint list (§9) so
that reintroduction is caught.

### 8.3 Changing an approved term

The most expensive operation in this standard. Required, per `T-13`:

1. Entity owner's written agreement
2. Architecture Review Board ratification
3. Bengali re-approval by the Localisation Lead
4. **An impact list**: every content file, string key, document template, report and training
   asset that cites the term, produced by search, not by memory
5. A co-ordinated change across every item on that list in one release
6. A decision record in `RF-006` including the impact list

**No term change is permitted mid-wave.** Term changes land at wave boundaries only.

---

## 9. Enforcement

| Mechanism | How |
|---|---|
| **Automated lint** | Banned terms from §4 and §8.2 are a CI check on the content repository. A banned term fails the build with the approved replacement named in the failure message |
| **Entity binding check** | Every business-object term in §4 must resolve to a `fix.*` model present in `05-02`. Checked at each wave audit (`AUDIT_Checklist_Recurring.md` §F) |
| **Definition of Done** | `CG-008` includes terminology conformance as a gate item |
| **Bengali parity check** | Every term in this file must have a row in `BN-003`. A missing row blocks approval of both files |
| **Audit sampling** | `AUDIT_Checklist_Recurring.md` §E6 — target terminology defect rate below 2% |

**Waiver.** A banned term may be used only inside:

1. a direct quotation;
2. a statutory instrument's own wording;
3. a third-party product name;
4. a code identifier; or
5. **a governance, style or training document citing the term as a banned example** — a style
   guide cannot forbid a word without naming it.

Any other use is a defect and is fixed, not waived.

> **Case 5 was added on 2026-08-15** after the automated check flagged legitimate negative
> examples in `VB-001` §4 and §8, `VB-002` §7 and `VB-006`. The automated lint in §9 excludes
> files whose `content_type` is `Standard`, `Policy` or `Governance` **from the banned-term
> check within do-not tables and worked examples only** — banned terms used as instruction in
> those same files remain defects.

---

## 10. Known open questions

| # | Question | Blocking | Owner | Target |
|---|---|---|---|---|
| 1 | Bengali register — one register for all ERP surfaces, or a formal register for statutory and legal content? | `BN-002`, all `BN` bundles | Localisation Lead | Before W1 |
| 2 | Does *service order* remain the approved term on `P01`, where customers say "booking"? | `UI-011`, `UI-037` | Content Design Lead with `M01` owner | Before W2 |
| 3 | *Engineer* is reserved for marketplace freelancers, but corporate clients call our staff engineers. Is a third surface-specific pair needed for `P04`? | `UI-014`, `EO-007` | `M12` and `M07` owners | Before W4 |
| 4 | Roles R39–R46 are used in module files but unregistered in `05-04` (audit `00-07` H2-07). Their names cannot be controlled until they are registered. | `MD-009`, all role citations | HR + Security | Before W1 access control |

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`CG-003_ERP_Product_Content_Style_Guide.md`](CG-003_ERP_Product_Content_Style_Guide.md) | How the approved term is written; this file decides which term |
| [`CG-005_Content_ID_and_Naming_Convention.md`](CG-005_Content_ID_and_Naming_Convention.md) | Identifier spaces; the same register-first discipline |
| [`CG-010_Bilingual_Content_Policy.md`](CG-010_Bilingual_Content_Policy.md) | Which content carries the Bengali terms |
| `BN-003` Bilingual Terminology Glossary | The Bengali binding; ratified with this file |
| `BN-004` Do-Not-Translate and Transliteration Register | Terms that never change form |
| `MD-027` Status and Lifecycle State Label Register | Customer-facing state labels (`T-06`) |
| `RP-001` KPI Dictionary | Metric names, which are controlled terms in the measurement domain |
| `RF-001` ERP Glossary and Acronym Register | The full explanatory glossary, superset of this file |
| `05-02` Data Model and Entity Catalogue | The entities every business-object term binds to |
| `05-04` Role Register | The registered role names content must use (`T-11`) |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Thirteen governing rules, six-level precedence order, core transactional vocabulary across seven domains, controlled verb list, registered surface-specific pairs, four open questions | Architecture Review Board (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Every business-object term binds to a `fix.*` model verified present in `05-02`
- [x] Precedence order stated and the internal/customer conflict resolved by registered pairs
- [x] Banned lists populated for every approved term
- [x] Statutory terms marked do-not-translate and routed to `BN-004`
- [x] All internal links resolve
- [ ] `BN-003` Bengali row exists for every term — **blocked; `BN-003` not yet written (`T-07`)**
- [ ] Named approver recorded — **pending Architecture Review Board**
- [x] Registered in the Content Master Index
- [x] Open questions listed with owners rather than silently deferred

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
