---
id: DM-010
title: Field Mapping Workbook — Contracts, Warranty and Claims
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration with Commercial
author: Data Migration analysts with Commercial Operations
reviewers: [Chief Commercial Officer, Finance Director, CFO, Quality Manager, Legal Counsel, Master Data Owner, QA Lead]
approver: Chief Commercial Officer with Finance Director
content_class: C
purpose: >
  Maps active contracts, entitlement positions, covered assets, warranty registrations, protection
  policies, in-flight brand claims, subscriptions, loyalty memberships and brand authorisations to
  the ERP commercial model. Contract-type and warranty-type service orders are blocked by hard
  business rules unless this data is correct and complete, so an error here does not degrade a
  report — it stops a branch from booking a job for a customer who is entitled, or lets it book one
  for a customer who is not.
traces_to: [M08, M09, M39, M53, M40, M10, M13, M05, M23, MD-031, MD-032, MD-028, MD-034, MD-017, MD-014, DM-001, DM-002, DM-003, DM-004, DM-005, DM-008, DM-011, DM-013]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
data_file: DM-010_Field_Mapping_Contracts_Warranty_and_Claims.xlsx
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M08 §16.4 — entitlement balances migrated as an opening grant movement with a declared as-at date and a reconciliation note, never as an edited balance; a contract whose remaining entitlement cannot be evidenced migrates with a zero opening balance and is flagged for customer confirmation before the first covered job
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M09 §16.4 — outstanding claims migrate live only where the submission and approval evidence exists; anything else migrates as archive and is written off through the governed process; profiling the current outstanding claim book is a Wave 3 prerequisite
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M39 §16.4 and M40 §16.4 — subscriptions migrate with a declared as-at period and an opening MRR reconciling to the last manually issued invoice; unreconciled subscriptions migrate in Draft and are not billed; brand authorisations migrate with the source document attached and the expiry verified against that document
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md and MD-032_Contract_and_AMC_Template_Catalogue.md §2 — coverage terms, exclusions bound verbatim to LG-013 and LG-015, renewal type and notice period
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M10 §16.4 — existing Privilege members must be migrated with their actual remaining term, not a reset term
    verified: 2026-08-18
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §6.3 — warranty revenue leakage 15–20% against a < 2% benchmark; claim submission 30–90 days against < 7
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# DM-010 — Field Mapping Workbook: Contracts, Warranty and Claims

> Governs `DM-010_Field_Mapping_Contracts_Warranty_and_Claims.xlsx`. The markdown governs; the
> workbook loads.
>
> **Template conformance note.** As `DM-004`: `TPL_Master_Data_Specification.md` retained in full;
> the `CG-009` source-to-target column set is inherited from `DM-004` §2.1 (`CP-01`).
>
> **Identifier note (`CG-005` §3.3).** `DM-010` is a **content** identifier; `05-02` `DM-08`
> (modelling standard — UTC storage, `Asia/Dhaka` presentation) is cited with its document prefix,
> and matters here because every entitlement and coverage window is a date range.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Contract, entitlement, warranty, claim, subscription and loyalty |
| Owning module | `M08` CTR; `M09` WTY; `M39` SUB; `M53` REV; `M40` PCM; `M10` LOY |
| Data steward | Commercial Operations, with the Finance Director accountable for the claim book |
| Golden source | **The executed contract document** — not the tracking spreadsheet |
| Refresh cadence | Once at cutover, with deltas through the parallel run |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | **yes** — contracts, entitlements and coverage are all date-bounded |
| **Build wave** | **W2** *(the register wave — `MS-22`)* |
| **Load wave** | **W4** — `M08`, `M09`, `M39`, `M53`, `M40` §16.4 and `06-01` W4; **loyalty W2**, **rental W6**, **quality W5** |

**Consequence of absence (`CP-03`).** The register's justification is exact: *"Contract-type and
warranty-type orders are blocked by hard rules unless this data is correct and complete."* That is
the whole risk, and it points both ways:

| Direction of error | What the branch experiences |
|---|---|
| Entitlement **understated or missing** | A customer with a paid AMC is refused a covered job, at the counter, in front of them |
| Entitlement **overstated** | Free work is performed against an entitlement that does not exist, and nobody notices until margin analysis |
| Warranty registration **inferred** | A warranty-type order is accepted that the brand will reject — adding to a **15–20% revenue-leakage** baseline |
| Claim loaded **live without evidence** | A receivable is asserted that cannot be collected; the balance sheet carries a fiction |
| Subscription loaded **unreconciled** | Double-billing at cutover — *"the single largest reputational risk of Wave 4"* (`M39`) |
| Brand authorisation **unevidenced** | Warranty work performed without current authorisation — an operational and contractual exposure |

---

## 2. Record structure

Target structures are `05-02` §4.1 (`M08` 14 entities, `M09` 13 entities, `M10` 15 entities) and
`MD-031`, `MD-032`, `MD-034`. Not restated (`CP-01`). Mapping column set: `DM-004` §2.1.

### 2.1 The evidence ladder

**`CW-01`: every commercial position loads at the level its evidence supports, and no higher.**

| Rung | Evidence held | Loads as | Operational effect |
|:--:|---|---|---|
| **1** | **Executed contract document** with dates, scope and price | `active`, fully enforceable | Entitlement validates at intake; billing runs |
| **2** | Tracking-spreadsheet row **plus** a customer-confirmable reference | `active` with a **zero opening entitlement balance**, flagged | Contract exists; **entitlement must be confirmed before the first covered job** |
| **3** | Spreadsheet row only, unconfirmable | `draft` | **Not billed, not consumable** until Commercial confirms |
| **4** | Expired, superseded or unidentifiable | `archive` | Retrieval only; excluded from base and renewal KPIs |

> **`CW-02` — the conservative choice is deliberate and must be communicated.** `M08` §16.4:
> *"Any contract whose remaining entitlement cannot be evidenced is migrated with a zero opening
> balance and flagged for customer confirmation before the first covered job — **a deliberately
> conservative choice that must be communicated to account managers before Wave 4 cutover**."*
>
> A zero opening balance on a live contract will produce counter conflict on day one **unless
> account managers know it is coming and why**. That communication is `CM-013` and `EO`-side
> content; this workbook's obligation is to make the population countable in advance so the
> conversation can be prepared.

### 2.2 Map A — `fix.contract`

| Source field *(typical)* | `SRC` | Target | Transform |
|---|---|---|---|
| Contract / AMC reference | `SRC-010`, `SRC-031` | `legacy_record_id`; new `name` from the **reserved migration sequence block** (`DM-006` `SH-10`) | Verbatim legacy reference retained and searchable |
| Customer | `SRC-010` | `partner_id` | FK into `DM-004`; **reject if unresolved** |
| Contract type / package name | `SRC-010` | `template_code` → `MD-032` | `T-05`; unmapped package escalates to the CCO — **a new `MD-032` template is created deliberately, never invented by the load** |
| Tier | `SRC-010` | `tier` → `MD-032` | From the `VB-010` ladders |
| Start / end date | `SRC-010`, contract document | `date_start`, `date_end` | `T-11`; **UTC stored, `Asia/Dhaka` presented** (`05-02` `DM-08`) |
| Value / price | `SRC-010` | `contract_value` | `05-02` `DM-07`, explicit `BDT` |
| Renewal terms | Contract document | `renewal_type`, `notice_period_days` → `MD-032` | **`CW-03`** — see below |
| Covered scope | Contract document | `covers` multi-enum → `MD-032` | From the document, never from the package name alone |
| Exclusions | — | **Not mapped.** `MD-032` `excluded_items` must match `LG-015`; `MD-031` `exclusions` must match `LG-013` **verbatim** | **`CW-04`** |
| SLA band | `SRC-010` | `sla_band_code` → `MD-028` | Where the contract states one; otherwise the template default, **flagged** |
| Status | Derived | `state` | Per the evidence ladder (`CW-01`) |
| — | `fix.document` link | The scanned original (`M24`), for every rung-1 contract | |

> **`CW-03` — auto-renewal is not migrated silently.** `MD-032` carries `renewal_type` including
> `auto` and `auto_with_notice`. A migrated contract set to auto-renew will renew and invoice
> without a human decision. **Every migrated contract loads `renewal_type = manual` unless the
> executed document explicitly provides for automatic renewal**, and the first renewal cycle after
> cutover is reviewed by Commercial rather than executed by the system.

> **`CW-04` — exclusions are never migrated as text.** They are a legal artefact bound verbatim to
> `LG-013` and `LG-015`. A migrated free-text exclusion clause would create a second, divergent
> statement of the same term — the `CP-01` failure with contractual consequence. The contract points
> at its `MD-032`/`MD-031` template; the template points at the legal source.

### 2.3 Map B — entitlement

**`CW-05`: entitlement is migrated as an opening `grant` movement, never as an edited balance.**

| Element | Rule |
|---|---|
| Target | `fix.entitlement` with one `fix.entitlement.consumption` row of type `grant` |
| `as_at_date` | **Declared explicitly** on the grant — the date the balance was true |
| Reconciliation note | **Mandatory free-text** on the grant, stating how the balance was established and by whom |
| Evidence rung 1 | Grant = the evidenced remaining entitlement |
| Evidence rung 2 or lower | **Grant = zero**, contract flagged `entitlement_unconfirmed` |
| Prohibited | Writing a balance directly to `fix.entitlement`; back-dating consumption to make a balance arrive at a desired figure |
| Why | A balance with no movement history cannot be explained to the customer who disputes it, and cannot be audited |

### 2.4 Map C — covered assets

| Source | Target | Rule |
|---|---|---|
| Asset lists attached to contracts | `fix.contract.covered.asset` | FK into `DM-005`; **a `provisional` asset is permitted, an unresolved asset is not** |
| Corporate estate declarations | Via `DM-005` `fix.asset.estate` | **Client-confirmed only** (`DA-05`) |
| `max_covered_assets` | From `MD-032` template | **`CW-06`** — where the migrated asset count exceeds the template limit, the contract loads and **raises an exception**; the excess is not silently truncated |
| Assets named in the contract but not found in `M17` | — | Loaded to the contract as **unmatched coverage lines**, flagged; the customer's contract says they are covered even if our registry has never seen the device |

> **`CW-06`** matters because coverage is what `M08` validates at intake. Truncating an over-limit
> contract makes some of a customer's devices silently uncovered; refusing to load it makes all of
> them uncovered. Loading with an exception preserves the customer's position and surfaces the
> commercial question.

### 2.5 Map D — warranty registrations and protection policies

| Source | Target | Rule |
|---|---|---|
| Sold extended-warranty records | `fix.protection.policy` | Rung 1 evidence required — this is a **sold product** with a liability behind it |
| Manufacturer warranty from purchase records | `fix.warranty.register` | Via `DM-005` §2.5 — `registered` where documented, `derived` and **advisory** otherwise (`DA-06`) |
| Device warranty from sampled service history | `fix.warranty.register` | **`confidence = derived`** (`M09` §16.4), advisory only |
| Repair warranty from past 1000FiX jobs | `fix.repair.warranty` | Only where a service report exists; `MD-025` `grants_repair_warranty` governs the type |
| Refurbished-unit warranties | `fix.refurb.warranty` | W6, with `M14`; **live warranties only** |
| Warranty type | → `MD-031` `warranty_type_code` | `T-05`; an unmapped type escalates to Commercial |
| `starts_from` | → `MD-031` | purchase_date / service_completion / activation — **taken from the type, not guessed per record** |

> **`CW-07`.** No migrated warranty makes a customer-facing promise the company cannot evidence.
> A `derived` registration is visible to an agent as *"probable, verify"* and never auto-classifies
> an order as warranty-type. This is the same rule as `DM-005` `DA-06`, restated at the commercial
> boundary because that is where the money is.

### 2.6 Map E — brand claims

**The claim book is a real asset of unknown size, and profiling it is a W3 prerequisite.**

| Source | Loads as | Rule |
|---|---|---|
| Outstanding claim **with** submission and approval evidence | `fix.brand.claim`, live, **Receivable** state | Feeds the `DM-008` AR open-item population and must tie to the control account (`FO-08`) |
| Outstanding claim **without** evidence | `archive` state | **Written off through the governed process, never silently absorbed** (`M09` §16.4) |
| Email-based claim history (`SRC-024`) | `archive` | 12–24 months, retrieval only |
| Brand rate cards and claim rules | `fix.brand.claim.rule`; rates via `M11` | ~400 rate lines across 17+ brands |
| Consignment part balances | `fix.consignment.part.record` | Per brand; must agree with the `DM-007` `IV-05` brand-confirmed balance |
| Claim evidence documents | `fix.claim.evidence` → `M24` | Attached where it exists; **a live claim with no attached evidence is a contradiction and is rejected** |

> **`CW-08` — profiling the claim book is a Wave 3 prerequisite, not a Wave 4 task.** `M09` §16.4:
> *"the recoverable balance is a real asset whose size is currently unknown, and the Wave 4 business
> case depends on it."* Against a **15–20% leakage** baseline and 30–90 day submission delays
> (BRD §6.3), the difference between the evidenced and unevidenced populations is a material
> financial number that nobody currently holds.

### 2.7 Map F — subscriptions, revenue obligations and loyalty

| Target | Source | Rule |
|---|---|---|
| `fix.subscription`, `fix.billing.schedule` | `SRC-010` AMC/RAMC billing schedules | **`CW-09`** — declared as-at period and an opening MRR that **reconciles to the last manually issued invoice for that customer**. Unreconciled → **`Draft`, not billed** |
| Payment mandates and standing instructions | Bank and gateway records | Via `DM-008`; **never assumed to still be valid** |
| `fix.performance.obligation`, `fix.contract.liability` | Rebuilt from contracts | **`FO-16`** — obligation by obligation, never a total. This workbook supplies the contracts that rebuild it |
| `fix.privilege.member` | Manual Privilege records | **`CW-10`** — **actual remaining term, never a reset term.** `M10` §16.4: resetting expiry *"would either give away value or curtail a paid entitlement — both create disputes at the counter in Wave 2"* |
| `fix.points.ledger` | — | **Not migrated** (`L`) — no ledger has ever been kept |
| Outstanding promotional commitments | `fix.voucher` or goodwill points | Profiled; loaded as explicit vouchers so the commitment is visible |
| `fix.msp.contract.instance` | Corporate AMC clients with IT scope | W5; client estates are **discovered and onboarded**, not migrated (`M05`) |
| `fix.rental.agreement`, `fix.rental.deposit` | Rental log books | W6; deposits **reconciled to the Finance liability balance**; units on hire without an outbound report are **baseline unknown** and damage cannot be charged |

### 2.8 Map G — brand authorisations and quality records

| Target | Source | Rule |
|---|---|---|
| `fix.brand.authorisation`, `fix.brand.obligation` | Brand authorisation documents (17+) | **`CW-11`** — migrated **with the source document attached and the expiry date verified against that document**, not against a spreadsheet. *"Any authorisation whose current validity cannot be evidenced is migrated flagged and escalated immediately — an unevidenced authorisation is a live operational risk, not a data-quality issue"* (`M40`) |
| Brand partner contacts | Via `DM-004` party roles | 60–100 contacts |
| `fix.nonconformance`, `fix.capa` | Paper ISO records | **Open only, and only where the Quality Manager confirms it is genuinely open**; history is `archive` and excluded from KPI computation (`M23`) |
| `fix.qms.certificate` | ISO 9001 / 27001 certificates | With surveillance history |

> **`CW-11` is the only rule in this workbook that can stop work on day one.** `MD-011` binds
> certification and brand authorisation, and `BRU-SRM-09` blocks assignment of warranty work to an
> uncertified technician. An expired-but-unnoticed authorisation and an unevidenced one have the
> same operational consequence; the difference is that this rule makes the second one visible.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | Contract reference + entity |
| Public key | New `name` from the reserved `MD-040` migration block (`SH-10`); the legacy reference is retained and searchable |
| Surrogate key | System-generated contract, entitlement and claim ids |
| Legacy key | `legacy_source_system` + `legacy_record_id` (`MS-18`) |
| Effective dating | Contract, coverage and entitlement rows are date-bounded; a superseded term is a new row, never an overwrite |
| Reuse policy | Never reused; a contract replaced at renewal is a new record linked to its predecessor |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `CW-01` | Every commercial position loads at the rung its evidence supports, and no higher | **H** | `ERR-CTW-001` |
| `CW-02` | A rung-2 contract loads with zero entitlement and the `entitlement_unconfirmed` flag | **H** | `ERR-CTW-002` |
| `CW-03` | A migrated contract loads `renewal_type = manual` unless the executed document provides otherwise | **H** | `ERR-CTW-003` |
| `CW-04` | Exclusions are never migrated as free text; the template binding to `LG-013`/`LG-015` governs | **H** | `ERR-CTW-004` |
| `CW-05` | Entitlement loads as a `grant` movement with a declared as-at date and a reconciliation note | **H** | `ERR-CTW-005` |
| `CW-06` | Coverage exceeding the template limit loads with an exception; it is never truncated | **H** | `ERR-CTW-006` |
| `CW-07` | A derived warranty is advisory and never auto-classifies an order as warranty-type | **H** | `ERR-CTW-007` |
| `CW-08` | A live claim without attached evidence is rejected; unevidenced claims load to archive | **H** | `ERR-CTW-008` |
| `CW-09` | A subscription whose opening MRR does not reconcile loads `Draft` and is not billed | **H** | `ERR-CTW-009` |
| `CW-10` | Loyalty members load with their actual remaining term; a reset term is rejected | **H** | `ERR-CTW-010` |
| `CW-11` | A brand authorisation loads only with its source document and a document-verified expiry; unevidenced authorisations are flagged and escalated | **H** | `ERR-CTW-011` |
| `CW-12` | An unmapped contract package or warranty type escalates to Commercial; the load never creates an `MD-031`/`MD-032` entry | **H** | `ERR-CTW-012` |
| `CW-13` | Consignment part balances must agree with the `DM-007` `IV-05` brand-confirmed figure | **H** | `ERR-CTW-013` |
| `CW-14` | Live claims feed the `DM-008` AR population and must tie to the control account (`FO-08`) | **H** | `ERR-CTW-014` |
| `CW-15` | A contract with an unresolved `partner_id` is rejected | **H** | `ERR-CTW-015` |
| `CW-16` | Only genuinely-open CAPAs and findings load live, on the Quality Manager's confirmation | **H** | `ERR-CTW-016` |
| `CW-17` | Rental deposits reconcile to the Finance liability balance before load | **H** | `ERR-CTW-017` |
| `CW-18` | A rental unit on hire without an outbound condition report loads `baseline_unknown` | **C** | `WRN-CTW-018` |
| `CW-19` | Payment mandates are never assumed valid; each is re-confirmed before the first collection | **H** | `ERR-CTW-019` |
| `CW-20` | Profiling reported and accepted before load — **claim-book profiling is a W3 prerequisite** | **H** | `ERR-CTW-020` |
| `CW-21` | Every loaded row carries the three control values (`MS-18`) | **H** | `ERR-CTW-021` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `MD-032` contract templates, `MD-031` warranty types, `MD-028` SLA bands, `MD-034` loyalty tiers | N:1 | Seed tier 6, **before** |
| `MD-017` brand register, `MD-011` certifications | N:1 | Seed tiers 7 and 8 |
| `DM-004` party | N:1 | Tier `X1`, before |
| `DM-005` asset | N:1 | Tier `X3`, before — coverage needs assets |
| `DM-007` consignment balances | 1:1 | `CW-13` cross-check |
| `DM-008` finance | **bidirectional** | Live claims feed AR (`CW-14`); deferred revenue is rebuilt **from** these contracts (`FO-16`) |
| [`../10_Legal_Policy_and_Compliance/LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md`](../10_Legal_Policy_and_Compliance/LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md) · [`../10_Legal_Policy_and_Compliance/LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md`](../10_Legal_Policy_and_Compliance/LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md) | N:1 | Written 2026-08-17, both `Draft`. `CW-04` binds to them; **neither is approved, and `MD-031`/`MD-032` require the binding to be verbatim** (`O-04`) |

| Depended on by |
|---|
| `M08` entitlement validation at intake · `M09` claim automation · `M53` deferred revenue · `M20` consolidated B2B invoicing · `G4-01`, `G4-02`, `G4-03`, `G4-08` · `CM-013` customer transition |

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | `SRC-010` AMC/RAMC spreadsheets · `SRC-031` contract originals (paper) · `SRC-019` brand portals · `SRC-024` claim email archive · `SRC-025` brand rate cards · Privilege records · rental log books |
| Who supplies it | Chief Commercial Officer for contracts and subscriptions; Finance Director for claims; Quality Manager for ISO records |
| Collection method | **Document retrieval and verification**, then spreadsheet reconciliation; portal download for claims |
| Known quality issues | Contracts tracked in spreadsheets with renewal dates maintained by hand; **contract profitability unknown**; entitlement consumption not tracked at all; claims lost in email threads; brand rate cards held as email attachments with indistinguishable versions |
| Cleansing rules applied | `DM-011` |
| Re-verification | Claim-book profiling at W3; brand confirmations at W4; renewal review after the first post-cutover cycle (`CW-03`) |

---

## 7. Volumes

| Population | Rows | Rung / origin | Wave |
|---|---:|---|:--:|
| Active AMC / RAMC contracts | **3,000–5,000** | Mixed — the rung split is unknown | W4 |
| Corporate AMC agreements (documents) | ~150 | Rung 1 | W4 |
| MSP agreements | ~40 | Rung 1 | W4–W5 |
| Brand partner authorisations | 17+ | Rung 1 required (`CW-11`) | W4 |
| Rental master agreements | ~30 | Rung 1 | W6 |
| Historic expired contracts | Unknown | Archive | W4 |
| **Outstanding brand claims** | **~2,000, of unknown recoverable value** | Split by evidence | W4 |
| Email claim history | 12–24 months | Archive | W4 |
| Brand rate lines | ~400 | Extracted | W4 |
| Sold extended warranties | Unknown | Rung 1 required | W4 |
| Device warranty registrations | **Sampled from 500,000+ records** | `derived` | W4 |
| Subscriptions / billing schedules | 3,000–5,000 | Reconciled or `Draft` | W4 |
| Privilege members | To be profiled | Actual remaining term | **W2** |
| Open rental agreements and deposits | Live only | Rung 1 | W6 |
| Open CAPAs and audit findings | To be profiled | Confirmed open only | W5 |

> **The rung split is the number that matters and nobody has it.** Of 3,000–5,000 contracts, how
> many have a retrievable executed document? That single figure determines how many customers meet a
> zero entitlement balance at the counter, and it is unknown until the documents are retrieved.

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add a mapping row | Migration analyst |
| Who may set `business_confirmed` | Chief Commercial Officer; Finance Director for claims |
| Who may set `signed_off` | **CCO with Finance Director** |
| Approval required | CFO for any claim write-off; Legal Counsel for any exclusion or renewal-term treatment; Quality Manager for ISO record classification |
| Effective dating | **Yes** — every contract, coverage and entitlement row is date-bounded |
| Archive rule | Records archived (`active = FALSE`), never deleted (`05-02` `DM-06`) |
| Logged in | `RF-006`; contract originals filed as `M24` documents linked to the contract |

---

## 9. Sample rows

```csv
map_id,source_id,source_field,source_type,source_example,target_entity,target_field,transform_rule,default_value,required_at_target,sensitivity,residency_restricted,dq_rule,unmapped_disposition,owner,status
CMAP-000701,SRC-010,AMC Ref,text,AMC/CORP/2024/0188,fix.contract,legacy_record_id,Verbatim; a new name is generated from the MD-040 reserved migration block,,TRUE,S1,FALSE,DQ-CTR-001,,Chief Commercial Officer,proposed
CMAP-000705,SRC-010,Visits Remaining,int,3,fix.entitlement.consumption,quantity,CW-05 loads as a grant movement with a declared as_at_date and a reconciliation note; rung 2 or lower loads zero and flags entitlement_unconfirmed,0,TRUE,S1,FALSE,DQ-CTR-005,,Chief Commercial Officer,proposed
CMAP-000709,SRC-010,Auto Renew,boolean,Y,fix.contract,renewal_type,CW-03 loads manual unless the executed document provides for automatic renewal,manual,TRUE,S1,FALSE,DQ-CTR-009,,Legal Counsel,proposed
CMAP-000714,SRC-010,Exclusions,text,"as per terms",,,CW-04 exclusions are never migrated as text; the MD-032 template binding to LG-015 governs,,FALSE,S1,FALSE,,dropped_with_reason,Legal Counsel,proposed
CMAP-000722,SRC-019,Claim Status,text,submitted 12-Mar,fix.brand.claim,state,CW-08 live Receivable only with submission and approval evidence attached; otherwise archive and governed write-off,archive,TRUE,S1,FALSE,DQ-CLM-002,,Finance Director,proposed
CMAP-000731,Privilege,Member Expiry,date,2027-02-11,fix.privilege.member,date_end,CW-10 actual remaining term; a reset term is rejected,,TRUE,S1,FALSE,DQ-LOY-001,,Marketing Head,proposed
```

---

## 10. Migration notes

**Four Gate 4 criteria depend on this workbook**, and `06-01` marks Gate 4 as *v1.0 scope complete*.

| Gate | Criterion | Served by |
|---|---|---|
| `G4-01` | Warranty claims auto-created within 24 h and submitted within 72 h | §2.5, §2.6 — against a 30–90 day baseline |
| `G4-02` | First-submission approval rate ≥ 90% | `CW-08` — only evidenced claims enter the live pipeline |
| `G4-03` | Contract engine operating all live product families | §2.2 — every migrated contract resolves to an `MD-032` template |
| `G4-08` | Consolidated B2B invoicing operating correctly | §2.7 subscriptions and the `DM-004` corporate hierarchy |

**The commercial prize and the migration risk are the same number.** BRD §6.3 puts warranty revenue
leakage at **15–20%** against a **< 2%** benchmark, and §6.4 values unclaimed or delayed warranty
revenue at **BDT 80–120 lac per year**. `M09`'s migration rule protects that prize by refusing to
load unevidenced claims as receivables — which means the opening claim book will look **smaller**
than the business expects. That is the correct outcome and it must be explained before it is
reported, not after.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-032_Contract_and_AMC_Template_Catalogue.md`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-032_Contract_and_AMC_Template_Catalogue.md) | Contract templates, renewal terms and the `LG-015` exclusion binding |
| [`../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md) | Warranty types and the `LG-013` exclusion binding |
| [`DM-005_Field_Mapping_Workbook_Device_and_Asset.md`](DM-005_Field_Mapping_Workbook_Device_and_Asset.md) | Covered assets and the derived-warranty rule this file restates commercially |
| [`DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md`](DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md) | Live claims into AR; contracts into deferred revenue |
| [`DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md`](DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md) | Consignment part balances (`CW-13`) |
| [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) | The rung-split report Commercial signs |
| `M08` §16.4 · `M09` §16.4 · `M39` §16.4 · `M40` §16.4 · `M10` §16.4 · `M23` §16.4 | The migration positions implemented here |
| `CM-013` Customer Migration and Transition Pack | Where the `CW-02` conversation is prepared |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Four-rung evidence ladder, entitlement as an opening grant movement, auto-renewal defaulted off, exclusions excluded from mapping, claim book split by evidence, subscriptions gated on MRR reconciliation, loyalty terms preserved | Chief Commercial Officer (pending) |

---

## 13. Open items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **The claim-book profiling is a W3 prerequisite and has not started.** `M09` §16.4 says the recoverable balance is *"a real asset whose size is currently unknown, and the Wave 4 business case depends on it"* | Finance Director | **W3 — prerequisite** |
| **`O-02`** | **The contract rung split is unknown.** Of 3,000–5,000 contracts, the share with a retrievable executed document determines how many customers meet a zero entitlement balance. Nobody has counted | Chief Commercial Officer | **W4 minus 3 months** |
| **`O-03`** | **`CW-02` requires account managers to be briefed before W4 cutover** and that briefing has no owner. `CM-013` is unwritten (Category 16 not started) | Change Lead with CCO | **W4 minus 1 month** |
| **`O-04`** | **`LG-013` and `LG-015` were written on 2026-08-17 and stand at `Draft`.** `CW-04` binds every migrated contract's exclusions to them and `MD-031`/`MD-032` require the binding to be **verbatim**. A `Draft` legal text can still change, so **every migrated exclusion is provisional until both reach `Approved`** — and `CG-002` §5.2 makes Legal Counsel the approver | Legal Counsel | **W4 — approval, not authoring** |
| **`O-05`** | **Whether brand portals permit bulk claim export is unconfirmed** (`DM-005` `O-06` carries the same question for warranty). Per-claim manual retrieval across 17+ brands changes §2.6 from an extract into a programme | Finance Director with Data Migration | **W3** |
| **`O-06`** | **Payment mandate validity is unverified.** `CW-19` prohibits assuming a migrated mandate still authorises collection; re-confirming several thousand mandates before the first billing run has no plan | CFO with CCO | **W4 minus 2 months** |
| **`O-07`** | The register places this file at **W2** while the contract, warranty and subscription loads are **W4**. Loyalty (`W2`) is the only W2 population. §1 records both waves per `MS-22`; the register row should carry the same clarification | Programme Content Lead | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; mapping column set inherited from `DM-004` §2.1 (`CP-01`)
- [x] **Four-rung evidence ladder** defined, with the deliberate conservatism made explicit and its communication obligation named
- [x] **Entitlement as an opening `grant` movement** with declared as-at date and mandatory reconciliation note (`CW-05`)
- [x] Auto-renewal defaulted off unless the executed document provides otherwise (`CW-03`)
- [x] **Exclusions excluded from mapping** and bound to `LG-013`/`LG-015` through the template (`CW-04`)
- [x] Over-limit coverage loaded with an exception rather than truncated (`CW-06`)
- [x] Derived warranties kept advisory at the commercial boundary (`CW-07`)
- [x] Claim book split by evidence, with unevidenced claims written off through a governed process
- [x] Subscriptions gated on MRR reconciliation, with `Draft`-and-unbilled as the fallback
- [x] Loyalty migrated with actual remaining term (`CW-10`)
- [x] Brand authorisations gated on document-verified expiry, with escalation for the unevidenced
- [x] Cross-workbook consistency stated with `DM-005`, `DM-007` and `DM-008`
- [x] Volumes stated, with the unknown rung split named as the number that matters
- [x] Sample rows included and parse as CSV
- [x] Archive rule states records are archived, never deleted (`05-02` `DM-06`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] **`O-01` claim-book profiling unstarted — a W3 prerequisite**
- [ ] **`O-04` `LG-013`/`LG-015` at `Draft` — `CW-04` binds verbatim to unapproved legal text**
- [ ] Named approver recorded — **pending CCO with Finance Director**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
