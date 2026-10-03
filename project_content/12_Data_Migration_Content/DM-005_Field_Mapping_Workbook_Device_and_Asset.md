---
id: DM-005
title: Field Mapping Workbook — Device and Asset
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration
author: Data Migration analysts with the Device Registry steward
reviewers: [Service Ops Director, Master Data Owner, Quality Manager, Logistics Manager, CFO, QA Lead]
approver: Service Ops Director with Master Data Owner
content_class: C
purpose: >
  Maps every source field describing a customer device, corporate estate asset, vehicle, tool,
  refurbished unit or IT asset to its target in the ERP asset model, including the identifier
  resolution hierarchy that decides whether a migrated record is a confirmed identity or a
  provisional one. Device identity is mandatory at intake, and an unmigrated or mis-identified
  device history destroys warranty entitlement and rework detection on the first day the branch
  uses the system.
traces_to: [M17, M45, M46, M48, M14, M18, M66, M09, MD-021, MD-022, MD-031, MD-024, MD-045, MD-046, DM-001, DM-002, DM-003, DM-006, DM-010, DM-011, DM-013]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: DM-005_Field_Mapping_Device_and_Asset.xlsx
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M17 §16.4 — 300,000–600,000 distinct devices; legacy records loaded as provisional identities unless they carry a verified identifier; a published burn-down planned as a twelve-month clearance programme, not a cutover task
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md §2 — model_code, serial_format_regex, imei_applicable, warranty_months_standard, five device families
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §11 — fix_asset unique partial indexes on serial_no, imei and asset_tag; §3.1 fix.asset.service.history and fix.rework.link
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M45 §16.4 and M46 §16.4 — calibration loads only where a certificate exists and traceability is verifiable; a statutory document without scanned evidence loads as expired
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M09 §16.4 — device warranty data derived from 500,000+ sampled historical records with confidence = derived
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# DM-005 — Field Mapping Workbook: Device and Asset

> Governs `DM-005_Field_Mapping_Device_and_Asset.xlsx`. The markdown governs; the workbook loads.
>
> **Template conformance note.** As `DM-004`: `TPL_Master_Data_Specification.md` retained in full,
> with the `CG-009` source-to-target column set applied from `DM-004` §2.1 rather than restated
> (`CP-01`).
>
> **Identifier note (`CG-005` §3.3).** `DM-005` is a **content** identifier; `05-02` `DM-06`
> (modelling standard — soft delete) is cited with its document prefix.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Device, customer asset and enterprise asset |
| Owning module | `M17` Device & Customer Asset Registry; `M45`, `M46`, `M66` for enterprise classes |
| Data steward | Device Registry steward, reporting to the Service Ops Director |
| Golden source | This mapping; sources `SRC-001`, `SRC-002`, `SRC-005`, `SRC-017`, `SRC-019`, `SRC-033`, `SRC-035` |
| Refresh cadence | Once per wave, plus a **twelve-month provisional-identity burn-down** |
| Environments | Dev · SIT · UAT · Prod — serials and IMEIs masked in non-production (`NFR-086c`) |
| Content class | C — Operational-critical |
| Effective-dated | no |
| **Build wave** | **W1** *(the register wave — `MS-22`)* |
| **Load wave** | **W1–W3** — `M17` §16.4; enterprise asset classes at **W5–W6** (`M45`, `M46`, `M66`) |

**Consequence of absence (`CP-03`).** `M17` §16.4 states the position that governs this whole file:

> *"Legacy device records are loaded as **provisional identities unless they carry a verified
> identifier**, and are cleared through the stewardship worklist rather than being silently trusted.
> Loading unverified records as confirmed would permanently contaminate the duplicate rate and the
> data-quality score, and would make the > 95% completeness target unmeasurable."*

The alternative — clearing 600,000 records by hand before go-live — *"is not available"*. **So the
registry starts partly provisional by design.** That is only defensible if the mapping declares
which records are provisional, why, and how they clear. Without this file the same 600,000 records
load as if they were all trustworthy, and:

| Failure | Consequence |
|---|---|
| Serial and IMEI loaded without format validation | `05-02` §11 declares unique partial indexes on `serial_no`, `imei` and `asset_tag`; junk values collide and legitimate loads fail |
| Free-text make/model loaded as-is | ~4,000 model references never resolve to `MD-021`; guided diagnosis, parts compatibility and repair-level routing all lose their root |
| Warranty status inferred and loaded as fact | A warranty-type service order is accepted that the brand will not reimburse — direct revenue loss against a 15–20% leakage baseline |
| Device history not linked to the device | `BRU`-level rework detection and repeat-fault analysis both fail silently |
| Every record loaded as confirmed | The completeness KPI reads 100% on day one and means nothing |

---

## 2. Record structure

Target structures are `05-02` §6 (`fix.asset` and its 17 siblings) and `MD-021` §2 for the model
catalogue they resolve against. Not restated (`CP-01`). The mapping column set is `DM-004` §2.1.

### 2.1 The identifier resolution hierarchy — the core of this workbook

**`DA-01`: a migrated asset's `identity_confidence` is set by the strongest identifier it carries,
and by nothing else.**

| Rank | Identifier | Test | Resulting `identity_confidence` |
|:--:|---|---|:--:|
| 1 | **IMEI** | 15 digits, checksum-valid, and `MD-021` `imei_applicable = TRUE` for the resolved model | `confirmed` |
| 2 | **Serial number** | Matches `MD-021` `serial_format_regex` for the resolved model | `confirmed` |
| 3 | Serial number, no regex available for that model | Non-empty, plausible length, not a placeholder | `probable` |
| 4 | **Asset tag** (corporate estate) | Client-issued tag confirmed by the client | `probable` |
| 5 | Make + model + customer + approximate purchase date | Resolves to exactly one candidate | `provisional` |
| 6 | Anything weaker | — | `provisional`, **and flagged for stewardship** |

> **`DA-02` — placeholder detection.** `N/A`, `NA`, `-`, `0`, `00000`, `XXXX`, `NOT FOUND`,
> `SERIAL NO`, a repeated single character, and the literal column header are **placeholders, not
> identifiers**. A placeholder never produces `confirmed` or `probable`. This list is extended at
> profiling and versioned in `DM-011`.

> **`DA-03` — the burn-down is a deliverable.** Every `provisional` record enters the stewardship
> worklist with an owner and a target date. `M17` requires a **published burn-down** over twelve
> months. A migration that creates 400,000 provisional records and no burn-down has not migrated
> the registry; it has moved a problem.

### 2.2 Map A — `fix.asset` core

| Source field *(typical)* | `SRC` | Target | Transform | Default | Sens |
|---|---|---|---|---|:--:|
| *(generated)* | — | `asset_id` | UUID | — | S0 |
| `Serial` / `SL No` / `Serial No` | `SRC-001`, `SRC-005` | `serial_no` | `D-01` — trim, upper-case, strip spaces and hyphens **only where the model regex expects none**; placeholder test (`DA-02`) | null | S2 |
| `IMEI` / `IMEI 1` | `SRC-001` | `imei` | `D-02` — digits only; 15-digit length and checksum test; **second IMEI becomes a second identifier row, not a truncation** | null | S2 |
| `Asset Tag` / `Client Tag` | `SRC-005` | `asset_tag` | Trim; scope to the owning corporate party | null | S1 |
| `Brand` / `Make` | `SRC-001`, `SRC-005` | *(resolves)* `brand_code` | `D-03` — `T-05` mapping against `MD-017`, including known misspellings and local spellings | **Unresolved → `UNKNOWN` brand + review row** | S0 |
| `Model` / `Model No` | `SRC-001` | `model_code` | `D-04` — resolve against `MD-021` `model_name` **then `model_aliases`**; `MD-021` carries aliases because *"market names differ from official ones"* | **Unresolved → provisional model + review row** | S0 |
| `Type` / `Category` | `SRC-005` | `device_family_code`, `category_code` | `T-05` → `MD-021` §2.1 five families | Derived from the resolved model | S0 |
| `Customer` / `Customer ID` | `SRC-001` | `owner_party_id` | FK into `DM-004` Map A; **resolved by the same key `DM-004` loaded on** | **Reject to remediation** | S1 |
| `Purchase Date` / `DOP` | `SRC-001` | `purchase_date` | `T-11` declared source format; **a date after the extract date is rejected, not clamped** | null | S1 |
| `Warranty Till` / `Warranty` free text | `SRC-001` | *(feeds Map D)* | **Never loaded directly as entitlement.** See §2.5 | — | S1 |
| `Condition` / `Grade` | `SRC-017` | `condition_grade` | `T-05` against the `M14` grading standard; **unmapped → null, never a guessed grade** | null | S1 |
| `Location` / `Branch` | `SRC-005` | `current_branch_id` | `T-05` → `MD-003` | Reject | S0 |
| *(computed)* | — | `identity_confidence` | **Computed by §2.1. Never supplied** | — | S0 |
| *(computed)* | — | `active` | `TRUE`; archived, never deleted (`05-02` `DM-06`) | `TRUE` | S0 |
| *(control)* | — | `legacy_source_system`, `legacy_record_id`, `migration_batch_id` | `MS-18` | — | S0 |

### 2.3 Map B — `fix.asset.identifier`

One asset may carry several identifiers over its life. **`DA-04`: identifiers are rows, not columns.**

| Source | `identifier_type` | Rule |
|---|---|---|
| `Serial` | `serial` | Primary where the model regex validates |
| `IMEI 1`, `IMEI 2` | `imei` | Dual-SIM devices carry two; both are rows |
| `Asset Tag` | `client_tag` | Scoped to the corporate party |
| `Box No` / internal reference | `legacy_ref` | Retained for lookup (`FR-SRM-088`) |
| Brand service-portal reference | `brand_ref` | Where the brand portal (`SRC-019`) exposes one |

> A device whose serial was recorded differently across three branch files produces **one asset with
> three identifier rows and a stewardship task**, not three assets. `DM-011` §matching decides which
> rows belong together; this workbook decides that they *can*.

### 2.4 Map C — ownership, estates and custody

| Target | Source | Rule |
|---|---|---|
| `fix.asset.ownership` | `SRC-001`, `SRC-005` | Owner party + effective-from. **Ownership is time-bounded**; a device resold or traded in later gets a new ownership row, never an overwrite |
| `fix.asset.estate` | `SRC-005` branch corporate device lists; client estate declarations | **`DA-05`: an estate row is loaded only when the client has confirmed it.** `M17` §16.4 marks these *client-confirmed*; an unconfirmed estate drives contract coverage the client has not agreed |
| `fix.asset.custody` | `SRC-017`, `SRC-028` | Devices currently held at branches or on the bench at cutover — from the **count**, not from the spreadsheet (`M04` §16.4, ~5,000 devices) |
| `fix.rental.asset` | `SRC-037` rental log books | W6; identity created here first, rental attributes in `DM-010` |
| `fix.refurb.unit` | `SRC-037` tally sheets | W6; **every unit re-assessed against the destruction gate before listing** (`M14` §16.4) |

### 2.5 Map D — warranty derivation, and why it is not a mapping

`M09` §16.4 migrates *"device warranty data from service history — 500,000+ historical records,
sampled — to `fix.warranty.register` with **confidence = derived**"*.

**`DA-06`: a warranty entitlement is never inferred into a live, enforceable state.**

| Source evidence | Loads as | Effect at intake |
|---|---|---|
| Purchase invoice or brand registration present | `registered`, live | Warranty-type order permitted |
| Purchase date present, no document | `derived`, **advisory only** | Agent is prompted to verify; the order is not auto-classified as warranty |
| "Under warranty" free-text flag, no date | **Not loaded** | Nothing asserted |
| Repair warranty from a past 1000FiX job with a service report | `derived`, advisory | Rework detection uses it; billing does not |

> **Why this matters commercially.** `MD-031` binds warranty exclusions to `LG-013` verbatim and
> `M09` gates brand claims on evidence. A device loaded as *in warranty* on a guess produces a job
> performed free that the brand then rejects. At the current 15–20% claim-leakage baseline
> (BRD §6.3) the programme cannot afford to import a new leakage channel on day one.

### 2.6 Map E — service history linkage

| Target | Source | Rule |
|---|---|---|
| `fix.asset.service.history` | `SRC-001`, `SRC-026` | 24–36 months where recoverable, **best-effort** (`M17` §16.4). Linked by asset, and **only where the asset resolved to `confirmed` or `probable`** |
| `fix.part.genealogy` | — | **Not migrated.** No source records which part went into which device |
| `fix.rework.link` | — | **Not migrated; computed forward.** `M01` §16.4 excludes migrated historical orders from rework and KPI calculation |

> **`DA-07`.** A history row attached to a `provisional` asset is loaded to the **archive area,
> flagged**, not to the operational history. Attaching history to an identity nobody has verified
> creates a repeat-fault signal that may belong to a different device.

### 2.7 Map F — enterprise asset classes *(W5–W6)*

| Class | Module | Load wave | The rule that governs the mapping |
|---|---|:--:|---|
| Test equipment and tools | `M45` | W5 | Opening register from a **physical audit at every branch and workshop** — the list is not the source. Calibration loads **only where the certificate exists and traceability is verifiable**; otherwise the instrument enters **out of service** |
| Fleet vehicles | `M46` | W5 | Every statutory document loads **with scanned evidence and its real expiry**, verified against the physical document. **No evidence → loads as expired → vehicle off-road.** Driver licences verified against the physical licence |
| Fixed assets | `M49` | W5 | **Physical verification at cutover.** Unlisted assets found are registered at CFO- and auditor-approved deemed cost; listed assets not found are written off before cutover. Financial values are `DM-008` |
| IT assets | `M66` | W6 | **Physical audit across 51+ branches, workshop, warehouse and corporate office**, reconciling every device to an employee and a cost centre |
| Site infrastructure and safety equipment | `M47` | W7 | Established by **physical survey**, scheduled on the same visit as the `M45` audit (`M47` §16.4) |

> **`DA-08`.** All five classes are `DM-001` disposition **`C`** — the mapping in this workbook
> maps the **count sheet** to the target, not a legacy list to the target. Three of them
> (`M45`, `M49`, `M66`) currently have **no count instruction and no named owner** — `DM-001` `O-06`.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | **IMEI, else serial, else asset tag** — in that order, scoped by model where a regex exists |
| Surrogate key | `asset_id` UUID, generated at load, permanent |
| Legacy key | `legacy_source_system` + `legacy_record_id`; a device recorded in three branch files carries three legacy references against one asset |
| Code format | No human-readable device code; devices are found by identifier or by owner |
| Reuse policy | Never reused. A duplicate resolved by merge retains its id and points to the survivor |
| Uniqueness | `05-02` §11 declares **unique partial indexes** on `serial_no`, `imei` and `asset_tag` — the load must respect them or fail loudly, never by silently dropping the second row |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `DA-01` | `identity_confidence` is computed from the identifier hierarchy and may not be supplied | **H** | `ERR-DAM-001` |
| `DA-02` | A placeholder value never yields `confirmed` or `probable` | **H** | `ERR-DAM-002` |
| `DA-03` | Every `provisional` asset is created with a stewardship task, an owner and a target date | **H** | `ERR-DAM-003` |
| `DA-04` | Identifiers are child rows; a second IMEI is never truncated away | **H** | `ERR-DAM-004` |
| `DA-05` | An estate row loads only where the client has confirmed it | **H** | `ERR-DAM-005` |
| `DA-06` | Warranty is never inferred into a live enforceable state; derived entitlements are advisory | **H** | `ERR-DAM-006` |
| `DA-07` | History attached to a `provisional` asset loads to archive, flagged | **H** | `ERR-DAM-007` |
| `DA-08` | Disposition `C` classes map from the signed count sheet, never from a legacy list | **H** | `ERR-DAM-008` |
| `DA-09` | An IMEI failing the 15-digit checksum is rejected to remediation, never stored | **H** | `ERR-DAM-009` |
| `DA-10` | A serial failing `MD-021` `serial_format_regex` for its resolved model downgrades confidence; it does not block the load | **S** | `WRN-DAM-010` |
| `DA-11` | An unresolved model creates a provisional model **and** a `MD-021` catalogue review row — it never invents a catalogue entry | **C** | `WRN-DAM-011` |
| `DA-12` | An asset with no resolvable owner party is rejected to remediation (`fix.asset` has no orphan state) | **H** | `ERR-DAM-012` |
| `DA-13` | A calibration record loads only with a verifiable certificate; otherwise the instrument loads `out_of_service` (`M45`) | **H** | `ERR-DAM-013` |
| `DA-14` | A statutory vehicle or site document without scanned evidence loads as **expired** (`M46`, `M47`) | **H** | `ERR-DAM-014` |
| `DA-15` | Purchase or warranty dates in the future relative to the extract are rejected, never clamped | **H** | `ERR-DAM-015` |
| `DA-16` | Unique partial indexes are respected; a collision is a reconciliation exception, never a silent drop | **H** | `ERR-DAM-016` |
| `DA-17` | Profiling reported and accepted before load (`MS-04`) | **H** | `ERR-DAM-017` |
| `DA-18` | Every loaded row carries the three control values (`MS-18`) | **H** | `ERR-DAM-018` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `DM-004` party | N:1 | **Before** — `owner_party_id` must resolve (`DM-003` tier `X1` → `X3`) |
| `MD-021` device catalogue | N:1 | Seed tier 5 — model resolution and serial regex |
| `MD-017` brand register | N:1 | Seed tier 7 |
| `MD-022` parts catalogue | N:1 | Compatibility root, for later parts genealogy |
| `MD-045` fleet master, `MD-046` test equipment | N:1 | Seed tier 8 — enterprise classes |
| `DM-011` quality rules | N:1 | Matching and placeholder register |

| Depended on by |
|---|
| `DM-006` service order `asset_id` · `DM-010` covered assets and warranty registrations · `DM-007` van and consignment stock location context · `DM-008` fixed-asset financial values · `M48` model training label set |

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | `SRC-001`/`SRC-002` legacy tracking (device records attached to orders) · `SRC-005` branch spreadsheets · `SRC-019` brand portals (warranty) · `SRC-033` vehicle folders · `SRC-035` calibration folders · physical counts for enterprise classes |
| Who supplies it | Service Ops Director for customer devices; Quality Manager for tools and calibration; Logistics Manager for fleet; CFO for fixed assets; CTO for IT assets |
| Collection method | Database extract plus spreadsheet collection; **physical audit** for all `M45`, `M46`, `M49`, `M66`, `M47` classes |
| Known quality issues | Volume *"unknown; estimated 300,000–600,000"*; serials absent, mistyped or placeholder; make/model free text with ~4,000 distinct strings; warranty status recorded as prose; the same device recorded independently in several branch files |
| Cleansing rules applied | `DM-011` |
| Re-verification | Continuous through the twelve-month burn-down (`DA-03`) |

---

## 7. Volumes

| Population | Rows | Source | Wave |
|---|---:|---|:--:|
| Customer devices | **300,000–600,000** *(estimate; unprofiled)* | `SRC-001`, `SRC-005` | W1–W2 |
| Device service history | 24–36 months, best-effort | `SRC-001` | W2 |
| Corporate estate devices | 51+ unstructured files | `SRC-005` | W2 |
| Warranty records held per brand | 17+ brands, various formats | `SRC-019` | W2–W3 |
| Devices held at branches at cutover | ~5,000 | Count | W1 |
| Rental pool devices | Operational holding | `SRC-037` | W2, confirmed by count |
| Vehicles | 150–400 | `SRC-033` | W5 |
| Drivers | 200–400 | `SRC-033` | W5 |
| Test equipment and tools | 51+ site sets | Physical audit | W5 |
| Fixed assets | 8,000–20,000 | Physical verification | W5 |
| IT assets | ~2,500 | Physical audit | W6 |
| Site infrastructure | 1,500–4,000 | Physical survey | W7 |
| E-waste backlog | All held stock | Count | W8 |

> **The device count is the least certain number in the migration.** `M17` says *"Unknown; estimated
> 300,000–600,000"* — a factor-of-two range on the second-largest dataset in the estate. Profiling
> `SRC-001` and `SRC-002` is therefore the highest-value early task in this workbook, and both
> sources **decommission at W2** (`SI-07`).

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add a mapping row | Migration analyst |
| Who may set `business_confirmed` | Service Ops Director (customer devices); Quality Manager (tools); CFO (fixed assets) |
| Who may set `signed_off` | Service Ops Director with Master Data Owner |
| Approval required | Quality Manager for any calibration rule change; CFO for any fixed-asset value rule; **Service Ops Director for any change to the identifier hierarchy** |
| Effective dating | Ownership rows are effective-dated; the mapping is not |
| Archive rule | Records archived (`active = FALSE`), never deleted (`05-02` `DM-06`) |
| Logged in | `RF-006`; burn-down progress published monthly per `DA-03` |

---

## 9. Sample rows

```csv
map_id,source_id,source_field,source_type,source_example,target_entity,target_field,transform_rule,default_value,required_at_target,sensitivity,residency_restricted,dq_rule,unmapped_disposition,owner,status
DMAP-000201,SRC-001,IMEI,text,352094081234567,fix.asset,imei,D-02 digits only; 15-digit checksum; second IMEI becomes a second identifier row,,FALSE,S2,FALSE,DQ-ASSET-002,,Service Ops Director,proposed
DMAP-000204,SRC-001,Serial,text,5CD1234ABC,fix.asset,serial_no,D-01 trim and upper-case; placeholder test DA-02; validate against MD-021 serial_format_regex for the resolved model,,FALSE,S2,FALSE,DQ-ASSET-004,,Service Ops Director,proposed
DMAP-000209,SRC-001,Model,text,HP Pavilion 15-eg2xxx,fix.asset,model_code,D-04 resolve against MD-021 model_name then model_aliases; unresolved creates a provisional model and a catalogue review row,,TRUE,S0,FALSE,DQ-ASSET-007,,Master Data Owner,proposed
DMAP-000215,SRC-001,Warranty Till,text,under warranty,fix.warranty.register,,DA-06 free text with no date asserts nothing and is not loaded,,FALSE,S1,FALSE,,dropped_with_reason,Finance Director,proposed
DMAP-000230,SRC-035,Calibration Due,date,2026-11-30,fix.calibration.record,next_due_date,DA-13 loads only with a verifiable certificate; otherwise the instrument loads out_of_service,,FALSE,S1,FALSE,DQ-ASSET-019,,Quality Manager,proposed
```

---

## 10. Migration notes

`G1-05` — *customer and device data migrated and reconciled, evidence: signed reconciliation* — is a
**Gate 1 criterion at month 4**. It is discharged jointly by this workbook and `DM-004`.

**What "reconciled" can honestly mean here.** Given that an unknown share of 600,000 records will
load `provisional` by design, the reconciliation cannot claim identity correctness. `DM-013` §exception
classes therefore requires the device reconciliation to report **four** figures, not one: source
count, loaded count, rejected count, and **`confirmed` / `probable` / `provisional` split**. A
reconciliation that reports only "600,000 in, 600,000 out" satisfies the wording of `G1-05` and
tells the Steering Committee nothing.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Model resolution, serial regex, IMEI applicability |
| [`../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md) | The warranty types a derived entitlement may reference |
| [`DM-004_Field_Mapping_Workbook_Party_and_Customer.md`](DM-004_Field_Mapping_Workbook_Party_and_Customer.md) | The owner party every asset resolves to |
| [`DM-006_Field_Mapping_Workbook_Service_History_and_Jobs.md`](DM-006_Field_Mapping_Workbook_Service_History_and_Jobs.md) | Orders that reference these assets |
| [`DM-010_Field_Mapping_Workbook_Contracts_Warranty_and_Claims.md`](DM-010_Field_Mapping_Workbook_Contracts_Warranty_and_Claims.md) | Covered assets and warranty registrations |
| [`DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md`](DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) | The placeholder register and device matching rules |
| `M17` §16.4 · `M45` §16.4 · `M46` §16.4 · `M09` §16.4 | The migration positions implemented here |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Six maps, a six-rank identifier hierarchy producing three confidence states, warranty derivation made advisory, enterprise asset classes bound to physical counts | Service Ops Director (pending) |

---

## 13. Open items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **The device population is unprofiled** — *"unknown; estimated 300,000–600,000"*. A factor-of-two range on the second-largest dataset makes the W1 window, the burn-down and the stewardship resourcing all unsizeable. **Both source systems decommission at W2** | Service Ops Director with Data Migration | **W1 — immediately** |
| **`O-02`** | **The twelve-month provisional burn-down has no resourced owner.** `M17` calls it *"the single largest data commitment M17 asks of the business"* and requires a published burn-down; no stewardship capacity is named in `06-01` beyond the 20% data-owner allocation | Service Ops Director with Programme Director | **W1** |
| **`O-03`** | **`MD-021` model coverage versus ~4,000 legacy model strings is unmeasured.** `D-04` resolves against `model_name` and `model_aliases`; the share that will fail to resolve — and therefore the size of the catalogue review backlog — is unknown | Master Data Owner | **W1 minus 1 month** |
| **`O-04`** | **Three enterprise `C` classes have no count instruction**: `M45` test equipment (W5), `M49` fixed assets (W5), `M66` IT assets (W6). Same item as `DM-001` `O-06`, recorded here because §2.7 depends on it | Data Migration Lead with CFO and CTO | **W5 minus 3 months** |
| **`O-05`** | **`MD-024` fault codes are unpopulated** (`AUDIT-008` KB-11), so `MD-021` `typical_fault_codes` cannot be validated on load and the migrated history in §2.6 cannot be back-mapped to a code taxonomy. `DM-006` carries the same dependency | Technical analyst (MDM) | **W2** |
| **`O-06`** | Whether brand portals (`SRC-019`) permit bulk export of warranty registrations, or only per-device lookup, is unconfirmed. Per-device lookup across 17+ brands changes §2.5 from an extract into a manual programme | Finance Director with Data Migration | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; mapping column set inherited from `DM-004` §2.1, not restated (`CP-01`)
- [x] **Identifier resolution hierarchy defined with six ranks and three confidence states** — the file's central mechanism
- [x] Placeholder detection specified rather than assumed (`DA-02`)
- [x] Provisional identities made a declared design position with a required burn-down (`DA-03`)
- [x] Identifiers modelled as rows, so dual-IMEI and multi-branch records are not truncated
- [x] **Warranty derivation made advisory, never live-enforceable** (`DA-06`), with the commercial reason stated
- [x] History linkage gated on identity confidence (`DA-07`)
- [x] Five enterprise asset classes bound to physical counts, with the three unowned counts named
- [x] `05-02` §11 unique partial indexes respected explicitly (`DA-16`)
- [x] Volumes stated with their uncertainty carried, not smoothed away
- [x] Sample rows included and parse as CSV
- [x] Archive rule states records are archived, never deleted (`05-02` `DM-06`)
- [x] `G1-05` reconciliation redefined to report the confidence split, not a single count
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] **`O-01` device population unprofiled; both sources decommission at W2**
- [ ] **`O-02` burn-down unresourced**
- [ ] Named approver recorded — **pending Service Ops Director with Master Data Owner**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
