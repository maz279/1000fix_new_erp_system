---
id: DM-006
title: Field Mapping Workbook — Service History and Jobs
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration
author: Data Migration analysts with Service Operations
reviewers: [Service Ops Director, Branch Operations Lead, Quality Manager, Master Data Owner, Customer Service Manager, QA Lead]
approver: Service Ops Director
content_class: C
purpose: >
  Maps legacy service orders, workshop job cards, field jobs, consignments and their evidence to the
  ERP service model, normalising an estate of branch-invented statuses onto MD-027, back-mapping
  free-text faults and repairs onto MD-024 and MD-025, and separating the small live population from
  the 500,000-plus historical archive. Service history drives repeat-fault detection, warranty
  argument, loyalty and the customer's own belief that the new system knows them; loaded wrongly it
  silently corrupts SLA, rework and every operational KPI from day one.
traces_to: [M01, M31, M02, M03, M04, M34, M06, M24, MD-024, MD-025, MD-026, MD-027, MD-028, DM-001, DM-002, DM-003, DM-004, DM-005, DM-011, DM-013]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
data_file: DM-006_Field_Mapping_Service_History_and_Jobs.xlsx
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M01 §16.4 — ~50,000 open and recent orders from branch spreadsheets, station.1000fix.com and 123.0.26.238 to archive, 500,000+ paper historical; migrated historical orders retain their legacy reference and are excluded from SLA, rework and KPI calculations; AC-13
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01 §FR-SRM-088 — legacy order lookup by original reference, priority P1
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md §2 — state_key, allowed_next_states transition map, is_terminal, requires_reason
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md and MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md §2 — code structure, action classes, standard minutes
    verified: 2026-08-18
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §6.2 processes 1, 2, 4 — paper service form keyed 1–3 days later, forms lost, photos not standardised, order number inconsistent
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# DM-006 — Field Mapping Workbook: Service History and Jobs

> Governs `DM-006_Field_Mapping_Service_History_and_Jobs.xlsx`. The markdown governs; the workbook
> loads.
>
> **Template conformance note.** As `DM-004`: `TPL_Master_Data_Specification.md` retained in full;
> the `CG-009` source-to-target column set is inherited from `DM-004` §2.1 (`CP-01`).
>
> **Identifier note (`CG-005` §3.3).** `DM-006` is a **content** identifier; `05-02` `DM-10`
> (modelling standard — explicit state machines) is cited with its document prefix.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Service delivery history |
| Owning module | `M01` SRM; `M31` workshop; `M02` field; `M03` logistics |
| Data steward | Service Operations, per branch |
| Golden source | This mapping; sources `SRC-001`, `SRC-002`, `SRC-005`, `SRC-026`, `SRC-027`, `SRC-028` |
| Refresh cadence | Once per wave, plus deltas through the parallel run |
| Environments | Dev · SIT · UAT · Prod — customer names and contact details masked in non-production |
| Content class | C — Operational-critical |
| Effective-dated | no |
| **Build wave** | **W2** *(the register wave — `MS-22`)* |
| **Load wave** | **W1–W2 live** (`M01` §16.4), **W2–W6 archive** |

**Consequence of absence (`CP-03`).** The estate has no service order system. It has 51+ branch
spreadsheets, two unconnected tracking portals, whiteboards, and half a million paper forms keyed
one to three days late by whoever had time (BRD §6.2 processes 1, 2 and 4). Order numbering is
described as *"inconsistent"*.

Two things therefore have to be true and are not automatic:

1. **The small live population must be genuinely live** — ~50,000 open and recent orders and ~500
   workshop WIP devices that branch staff will pick up and continue on the first morning.
2. **The large historical population must be genuinely inert** — 500,000+ records that are findable
   by a customer's old reference and invisible to every calculation.

Get the boundary wrong in either direction and: an SLA clock starts on a job that closed last year;
first-time-fix rate is computed against records with no diagnosis; rework detection fires on a
repeat that is really a re-key; or a customer at the counter is told the company has no record of
the repair they collected last month.

---

## 2. Record structure

Target structures are `05-02` §3.1 (`M01` — 26 entities) and `MD-027` for state labels. Not
restated (`CP-01`). Mapping column set: `DM-004` §2.1.

### 2.1 The live / archive boundary

**`SH-01`: every migrated order carries `migration_class`, set at extract and never editable.**

| `migration_class` | Population | Lands in | Participates in |
|---|---|---|---|
| **`live`** | Open orders and orders closed within the declared recency window | Operational tables | Everything — the branch continues working on them |
| **`recent_closed`** | Closed inside the window, retained for customer lookup and warranty argument | Operational tables, closed state | Customer 360 and warranty argument only — **excluded from SLA, TAT, first-time-fix and rework** |
| **`archive`** | Everything older, plus every paper and legacy-tracker record | Archive area, flagged | **Nothing.** Retrieval by legacy reference only (`FR-SRM-088`) |

> **`SH-02`.** `M01` §16.4 states the exclusion for migrated historical orders without qualification:
> *"retain their legacy reference for lookup and are excluded from SLA, rework and KPI
> calculations."* This workbook extends the same exclusion to `recent_closed`, because a record
> whose SLA policy, hold reasons and diagnosis were never captured cannot produce a meaningful TAT
> — including it would make W2 baselines look worse or better than reality and nobody could say
> which.

> **`SH-03` — the recency window is unresolved.** `M01` `Q-04` asks *"How far back should the
> historical service archive be migrated — 3, 5 or all years?"* and is open (`DM-001` `O-02`). Until
> it is answered, the boundary between `recent_closed` and `archive` cannot be set, and the volume
> of the live load is unknown.

### 2.2 Map A — `fix.service.order`

| Source field *(typical)* | `SRC` | Target | Transform | Default |
|---|---|---|---|---|
| `Job No` / `Order No` / `SL` | `SRC-005`, `SRC-001` | `legacy_record_id` **and** `fix.asset.identifier` style lookup key | Verbatim. **A new `name` is generated by `MD-040` sequence; the legacy number is never reused as the new one** | — |
| *(generated)* | — | `name` | New sequence from `MD-040`, in a **reserved migration block** (§2.7) | — |
| `Customer` / `Customer Name` / phone | `SRC-005` | `partner_id` | FK into `DM-004`; resolved on the same key | **Reject to remediation** |
| `Device` / `Serial` / `IMEI` | `SRC-005` | `asset_id` | FK into `DM-005`; **a `provisional` asset is permitted, a missing asset is not** | Reject |
| `Type` / `Service Type` | `SRC-005` | `order_type` | `T-05` → `MD-020` service types | Reject |
| `Warranty` / `Chargeable` free text | `SRC-005` | `order_type` qualifier | **Never sets a warranty entitlement** — `DM-005` `DA-06` governs | `chargeable` |
| `Branch` | `SRC-005` | `branch_id` | `T-05` → `MD-003` | Reject |
| `Status` / `Stage` free text | `SRC-005` | `state` | **`SH-04` — see §2.3** | Reject |
| `Complaint` / `Problem` free text | `SRC-005` | `complaint_text` | Verbatim after encoding conversion; **never discarded in favour of a code** | — |
| *(derived)* | — | `fault_code_id` | **§2.4 back-mapping — advisory, `derived` confidence** | null |
| `Received Date` | `SRC-005` | `create_date` | `T-11`; **the source system's own timestamp where one exists, else the recorded date at 00:00 `Asia/Dhaka`** | Reject |
| `Promised` / `Delivery Date` | `SRC-005` | `promised_date` | `T-11`; **loaded but not used to compute SLA attainment** (`SH-02`) | null |
| `Closed Date` | `SRC-005` | `date_done` | `T-11` | null |
| `Amount` / `Bill` | `SRC-005` | `total_price` | `T-12` with explicit `BDT` (`05-02` `DM-07`); **`live` orders only** | null |
| — | `sla_policy_id` | | **Not migrated.** `SH-05` — see below | null |
| — | `SRC-005` | `business_line_id` | `T-05` → `MD-036`; default to the general service line where the source predates the concept | Default + review row |
| *(computed)* | — | `migration_class` | §2.1 | — |
| *(control)* | — | `legacy_source_system`, `legacy_record_id`, `migration_batch_id` | `MS-18` | — |

> **`SH-05` — no migrated order carries an SLA policy or an SLA clock.** `MD-028` SLA bands did not
> exist when these orders were taken; attaching one retrospectively invents a commitment the company
> never made and then measures itself against it. `fix.sla.clock` rows are **not created** for any
> migrated order, in any class.

### 2.3 Status normalisation — `SH-04`

The single most error-prone map in this workbook. Fifty-one branches invented their own words.

| Rule | Detail |
|---|---|
| **Target** | `MD-027` `state_key` for `fix.service.order` — the technical value, **never the customer label** |
| **Method** | A signed value list mapping every observed source string to exactly one `state_key`, produced at profiling by extracting **distinct** status strings per source file |
| **Terminal states** | A migrated order in a non-terminal state must have a valid `allowed_next_states` path to a terminal one, or it can never be closed (`MD-027`) |
| **`requires_reason` states** | Where `MD-027` marks a state as requiring a reason (`MD-026`), a migrated order entering it carries `RSN-MIGRATION`, a dedicated reason code, **not a guessed operational reason** |
| **Unmappable** | Loads as `archive` regardless of age, flagged. It never guesses at a live state |
| **Ambiguity** | `"Done"` may mean repaired, delivered or billed. **The three are different states.** Ambiguity is resolved per source file with the branch, and recorded — not resolved by the analyst |
| **Prohibited** | Loading the source string into the state field; creating a new `MD-027` state to accommodate legacy vocabulary |

> **`SH-06`.** A new `MD-027` state may not be created to hold migrated data. `MD-027` is the
> transition map the running system executes (`05-02` `DM-10`); adding a legacy-only state adds a
> node with no outbound transitions and a permanently stuck population.

### 2.4 Fault and resolution back-mapping

`M01` §16.4 and the register both call this *"fault and resolution code back-mapping"*. It is
**derivation from free text**, and it is treated with the same caution as warranty derivation.

| Step | Rule |
|:--:|---|
| 1 | Extract distinct complaint and repair strings per source; rank by frequency |
| 2 | The **top strings by volume** are mapped by a technical analyst to `MD-024` symptom/fault codes and `MD-025` resolution codes — the same population `M37` uses to seed provisional standard repair times |
| 3 | Every derived code is written with `code_confidence = derived` |
| 4 | **The original free text is always retained** in `complaint_text` and the service-report findings — the code never replaces the words |
| 5 | Unmapped strings leave the code null. **Null is a correct answer; a wrong code is not** |
| 6 | Derived codes are **excluded from `MD-025` `standard_minutes` calibration and from `KB-014` labour norms** — deriving a norm from a derived code is circular |

> **`SH-07`.** `MD-024` is **unpopulated** (`AUDIT-008` KB-11), which means the target taxonomy this
> map resolves into does not yet contain values. Back-mapping cannot begin until it does. Recorded
> as `O-02`, and the same dependency `DM-005` `O-05` carries.

### 2.5 Map B — work orders, workshop and field

| Target | Source | Rule |
|---|---|---|
| `fix.work.order` | `SRC-005` where the source distinguishes a visit or bench task; `SRC-028` workshop cards | **One work order per migrated order minimum.** Where the source has no work-order concept, a single synthetic work order is created carrying the recorded technician and dates, flagged `synthetic = TRUE` |
| `fix.work.order.task` | — | **Not migrated.** No source records task breakdown |
| `fix.repair.order` (`M31`) | `SRC-028` whiteboards and paper job cards | **~500 devices, current WIP only, captured during a single cutover count** (`M31` §16.4) — a count, not an extract |
| `fix.dispatch.job` / `fix.visit` (`M02`) | Open field jobs | ~1,000 at cutover. **Zones and skill profiles are authored, not migrated** (`M02` §16.4, disposition `N`) |
| `fix.consignment` + legs + items (`M03`) | Open pick-and-drop jobs | ~200, current only. **Chain of custody starts at migration** — no historical custody events exist |
| `fix.diagnostic.result` | — | **Not migrated.** No structured diagnosis exists; `M01` guided diagnosis begins at go-live |
| `fix.qc.result` | — | **Not migrated.** Paper QC checklists are `A`/`L`; `M23` rationalises the templates first |
| `fix.custody.event` | `SRC-028` count | One inbound custody event per device physically held at cutover, evidenced by the count sheet (`M04` §16.4, ~5,000 devices) |
| `fix.complaint` (`M34`) | Existing complaint records | **Open only**, W4. Historical satisfaction data is disposition `L` |
| `fix.data.case` (`M06`) | Data recovery job cards | **Current work only**, W6. Residual customer data from past work is disposition `P` — audited and purged |

### 2.6 Map C — evidence and documents

| Evidence type | Source | Target | Rule |
|---|---|---|---|
| Signed paper service forms | `SRC-026`, `SRC-027` | `fix.document` (`M24`), archive class, OCR-indexed | **Digitised by priority of need, not chronology** (`M24` §16.4). Classified and given a retention class **on capture** |
| Photographs attached to jobs | `SRC-001` | `fix.document` linked to the order | *"Photos not standardised"* (BRD §6.2). Loaded as-is; **no quality assertion is made** |
| Customer signatures on paper | `SRC-026` | Part of the scanned document | **Never converted into an e-signature record.** A scanned wet signature is not an `M24` signature envelope, and presenting it as one would misstate the evidence chain |
| Service reports | `SRC-026` | `fix.service.report` for `live` and `recent_closed`; document only for `archive` | |

> **`SH-08`.** Evidence volume is the largest single number in the migration — 500,000+ paper
> records — and **no mapping workbook in Category 12 owns the `M24` document migration** (`DM-001`
> `O-04`). This section maps the *linkage*; it does not map the document estate itself. The
> distinction is stated so the gap is not hidden by this file's existence.

### 2.7 Numbering and the reserved migration block

| Rule | Detail |
|---|---|
| **`SH-09`** | Migrated orders receive **new** numbers from `MD-040` sequences. Legacy numbers are inconsistent across 51 branches and cannot be trusted to be unique |
| **`SH-10`** | Migrated orders draw from a **reserved sequence block** declared in `MD-040`, distinct from the live operational block, so that a migrated number is visually identifiable and a sequence collision at cutover is impossible |
| **`SH-11`** | `MD-040` `is_statutory` sequences are **never** used for migrated records. Statutory sequences must be gap-free (`gap_policy = no_gaps`); consuming numbers for historical records would corrupt the statutory series |
| **`SH-12`** | The legacy number is indexed and searchable at the counter and in `P01` — this is `FR-SRM-088`, and it is what protects the customer relationship at go-live |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | Source order number **within a source** — it is not unique across sources |
| Surrogate key | `service_order_id` UUID |
| Public key | New `name` from the reserved `MD-040` migration block (`SH-10`) |
| Legacy key | `legacy_source_system` + `legacy_record_id`, indexed, exposed at the counter (`FR-SRM-088`) |
| Reuse policy | Never reused; a de-duplicated order retains its id and links to the survivor |
| Cross-source duplicates | The same job recorded in a branch spreadsheet **and** the legacy tracker is one order with two legacy references — `DM-011` decides |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `SH-01` | Every migrated order carries `migration_class`, set at extract, not editable | **H** | `ERR-SVH-001` |
| `SH-02` | `recent_closed` and `archive` orders are excluded from SLA, TAT, first-time-fix, rework and every KPI | **H** | `ERR-SVH-002` |
| `SH-03` | The recency window must be a declared, approved value before the live load runs | **H** | `ERR-SVH-003` |
| `SH-04` | `state` is set only from the signed status value list; the source string is never loaded into the state field | **H** | `ERR-SVH-004` |
| `SH-05` | No migrated order carries an SLA policy or an SLA clock | **H** | `ERR-SVH-005` |
| `SH-06` | No `MD-027` state is created to accommodate legacy vocabulary | **H** | `ERR-SVH-006` |
| `SH-07` | A derived fault or resolution code carries `code_confidence = derived` and is excluded from labour-norm calibration | **H** | `ERR-SVH-007` |
| `SH-08` | Free-text complaint and findings are always retained alongside any derived code | **H** | `ERR-SVH-008` |
| `SH-09` | Migrated orders receive new numbers; legacy numbers are never reused as the operational key | **H** | `ERR-SVH-009` |
| `SH-10` | Migrated numbering draws only from the reserved migration block | **H** | `ERR-SVH-010` |
| `SH-11` | Statutory sequences are never consumed by migration | **H** | `ERR-SVH-011` |
| `SH-12` | The legacy reference is indexed and retrievable (`FR-SRM-088`) | **H** | `ERR-SVH-012` |
| `SH-13` | An order whose asset does not resolve is rejected; a `provisional` asset is acceptable | **H** | `ERR-SVH-013` |
| `SH-14` | A non-terminal migrated state must have a valid transition path to a terminal state | **H** | `ERR-SVH-014` |
| `SH-15` | A state requiring a reason receives `RSN-MIGRATION`, never a guessed operational reason | **H** | `ERR-SVH-015` |
| `SH-16` | A scanned wet signature is never recorded as an e-signature envelope | **H** | `ERR-SVH-016` |
| `SH-17` | A synthetic work order is flagged `synthetic = TRUE` | **C** | `WRN-SVH-017` |
| `SH-18` | Profiling reported and accepted before load (`MS-04`) | **H** | `ERR-SVH-018` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `DM-004` party | N:1 | Tier `X1`, before |
| `DM-005` asset | N:1 | Tier `X3`, before |
| `MD-020` service types, `MD-026` reason codes, `MD-027` states | N:1 | Seed tier 5, before |
| `MD-024`, `MD-025` taxonomies | N:1 | Seed tier 5 — **currently unpopulated** (`O-02`) |
| `MD-040` sequences with a reserved migration block | N:1 | Seed tier 4, before |
| `MD-003` branch, `MD-036` business line | N:1 | Seed tiers 2 and 1 |

| Depended on by |
|---|
| `DM-010` warranty argument and claim history · `M17` device service history · `M43` consumption baseline *(warehouse only)* · `M48` fault label set · customer-facing history in `P01` |

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | `SRC-005` branch spreadsheets (51+) · `SRC-001`/`SRC-002` legacy trackers · `SRC-026` paper archive · `SRC-027` forms in circulation · `SRC-028` workshop whiteboards |
| Who supplies it | Branch Operations Lead for spreadsheets; CTO for the tracker extracts; Service Ops Director overall |
| Collection method | Spreadsheet collection · database extract · **document scan** · **cutover count** for WIP |
| Known quality issues | Inconsistent order numbering; branch-invented statuses; complaint and repair recorded as free text; forms keyed 1–3 days late; forms lost; photos unstandardised; **the same job present in a spreadsheet and a tracker** |
| Cleansing rules applied | `DM-011` |
| Re-verification | Delta extract immediately before cutover; the two trackers **decommission at W2** |

---

## 7. Volumes

| Population | Rows | Class | Wave |
|---|---:|---|:--:|
| Open and recent branch orders | **~50,000** | `live` / `recent_closed` | W1–W2 |
| Workshop WIP | ~500 devices | `live` (count) | W2 |
| Open field jobs | ~1,000 | `live` | W2 |
| Open consignments | ~200 | `live` | W3 |
| Devices held at branches | ~5,000 custody events | `live` (count) | W1 |
| `station.1000fix.com` records | **Unknown — to be profiled** | `archive` | W2 |
| `123.0.26.238` records | **Unknown** | `archive` | W2 |
| Paper service history | **500,000+** | `archive` | W2–W6 |
| Open complaints | To be profiled | `live` | W4 |
| Data recovery cases | Current only | `live` | W6 |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add a mapping row | Migration analyst |
| Who may set `business_confirmed` | Service Ops Director; **the status value list additionally requires the originating branch to confirm its own vocabulary** |
| Who may set `signed_off` | Service Ops Director |
| Approval required | Service Ops Director for the recency window; Master Data Owner for any `MD-027` or `MD-040` interaction; Quality Manager for evidence handling |
| Effective dating | Not effective-dated |
| Archive rule | Records archived (`active = FALSE`), never deleted (`05-02` `DM-06`) |
| Logged in | `RF-006`; the status value list is versioned as a signed annexe to the workbook |

---

## 9. Sample rows

```csv
map_id,source_id,source_field,source_type,source_example,target_entity,target_field,transform_rule,default_value,required_at_target,sensitivity,residency_restricted,dq_rule,unmapped_disposition,owner,status
SMAP-000301,SRC-005,Job No,text,MIR/2025/04412,fix.service.order,legacy_record_id,SH-09 verbatim; a new name is generated from the MD-040 reserved migration block,,TRUE,S1,FALSE,DQ-ORDER-001,,Service Ops Director,proposed
SMAP-000305,SRC-005,Status,text,Done,fix.service.order,state,SH-04 signed value list only; Done is ambiguous across repaired/delivered/billed and is resolved per source file with the branch,,TRUE,S1,FALSE,DQ-ORDER-006,,Branch Operations Lead,proposed
SMAP-000309,SRC-005,Problem,text,screen flickering after charging,fix.service.order,complaint_text,Verbatim after encoding conversion; the derived MD-024 code never replaces the words,,FALSE,S1,FALSE,DQ-ORDER-009,,Service Ops Director,proposed
SMAP-000312,SRC-005,Promised Date,date,2025-04-18,fix.service.order,promised_date,T-11 declared source format; loaded but excluded from SLA attainment per SH-02 and SH-05,,FALSE,S1,FALSE,DQ-ORDER-012,,Service Ops Director,proposed
SMAP-000320,SRC-026,Customer signature,image,scanned,fix.document,,SH-16 scanned wet signature is filed as a document and never as an e-signature envelope,,FALSE,S2,FALSE,,carried_to_legacy_payload,Quality Manager,proposed
```

---

## 10. Migration notes

**Two `M01` acceptance criteria are discharged here.**

| Criterion | How |
|---|---|
| `AC-13` — *migrated historical orders are retrievable by legacy reference and excluded from KPIs*, evidence: migration reconciliation report | `SH-02`, `SH-12`, and the `DM-013` class report |
| `FR-SRM-088` — legacy order lookup | `SH-12`, with the legacy reference indexed at the counter and in `P01` |

**The customer-facing consequence is the reason this file is `P1` and not `P2`.** `CM-013` Customer
Migration and Transition Pack commits to transitioning existing customers *"without losing their
service history in their own eyes"*. That promise is kept by `SH-12` and by nothing else: a customer
holding a slip with an old job number must be found, at the counter, in the first week.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md) | The state targets and the transition map |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) · [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | The back-mapping targets |
| [`../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-040_Document_Sequence_and_Numbering_Mask_Register.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-040_Document_Sequence_and_Numbering_Mask_Register.md) | The reserved migration numbering block |
| [`DM-005_Field_Mapping_Workbook_Device_and_Asset.md`](DM-005_Field_Mapping_Workbook_Device_and_Asset.md) | The asset every order references |
| [`DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md`](DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) | Cross-source order de-duplication |
| `M01` §16.4 · `M31` §16.4 · `M02` §16.4 · `M03` §16.4 · `M04` §16.4 | The migration positions implemented here |
| `CM-013` Customer Migration and Transition Pack | The customer promise `SH-12` keeps |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Three-class live/archive boundary, status normalisation against `MD-027` with a prohibition on new states, derived fault codes made advisory, reserved migration numbering block, evidence linkage separated from document migration | Service Ops Director (pending) |

---

## 13. Open items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **`M01` `Q-04` is unresolved** — 3, 5 or all years of service history. Until it is answered the `recent_closed` / `archive` boundary cannot be set, the live volume is unknown, and `SH-03` blocks the load | Ops Director with CTO | **W2 planning** |
| **`O-02`** | **`MD-024` and `MD-025` are unpopulated** (`AUDIT-008` KB-11). §2.4 back-maps into taxonomies that currently have no values. `DM-005` `O-05` carries the same dependency | Technical analyst (MDM) | **W2 — blocking** |
| **`O-03`** | **`MD-040` has no declared reserved migration block.** `SH-10` and `SH-11` require one; the register defines sequences for live documents only | Master Data Owner with CFO | **W1** |
| **`O-04`** | **The status value list does not exist and cannot be written centrally.** It requires extracting distinct status strings from 51+ branch files and confirming meaning **with each branch**. This is weeks of branch-manager time and is not in any plan | Branch Operations Lead | **W2 minus 2 months** |
| **`O-05`** | **Neither legacy tracker has been profiled** and both decommission at W2 (`SI-07`). Their record counts, overlap with the branch spreadsheets, and encoding are all unknown | CTO with Data Migration | **W1 — immediately** |
| **`O-06`** | **No workbook owns the `M24` document estate** (500,000+ records). §2.6 maps evidence *linkage* only. Same item as `DM-001` `O-04` | Programme Content Lead with Quality Manager | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; mapping column set inherited from `DM-004` §2.1 (`CP-01`)
- [x] Three-class live/archive boundary defined and bound to `M01` §16.4's exclusion rule
- [x] Exclusion extended to `recent_closed` with the reasoning stated, not assumed
- [x] Status normalisation specified as a signed, branch-confirmed value list, with new-state creation prohibited (`SH-06`)
- [x] Fault and resolution back-mapping made advisory, with free text always retained and labour-norm circularity prevented
- [x] **No SLA policy or clock on any migrated order** (`SH-05`) with the reasoning recorded
- [x] Numbering: new sequence, reserved migration block, statutory sequences protected
- [x] `FR-SRM-088` legacy lookup made a validation rule, not an aspiration
- [x] Scanned signatures explicitly excluded from the e-signature evidence chain (`SH-16`)
- [x] Evidence linkage separated from document migration, with the uncovered gap named rather than hidden
- [x] Volumes stated with the two unprofiled trackers marked unknown
- [x] Sample rows included and parse as CSV
- [x] Archive rule states records are archived, never deleted (`05-02` `DM-06`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] **`O-01` recency window unresolved — `SH-03` blocks the live load**
- [ ] **`O-02` `MD-024`/`MD-025` unpopulated — back-mapping cannot start**
- [ ] **`O-04` status value list requires 51 branch conversations that are in no plan**
- [ ] Named approver recorded — **pending Service Ops Director**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
