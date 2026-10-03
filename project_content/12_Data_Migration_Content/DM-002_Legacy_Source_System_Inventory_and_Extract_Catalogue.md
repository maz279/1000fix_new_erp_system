---
id: DM-002
title: Legacy Source System Inventory and Extract Catalogue
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration Lead
author: Data Migration with Platform Engineering
reviewers: [CTO, CFO, Security Lead, Master Data Owner, Branch Operations Lead, HR Director, Procurement Manager, QA Lead]
approver: Data Migration Lead with CTO
content_class: E
purpose: >
  Registers every system, file, portal, folder and paper archive from which data is extracted for
  migration, together with its owner, extract method, access constraint, refresh window, encoding,
  known quality issues and decommission wave. Sources discovered mid-migration are the most common
  cause of cutover slippage, and this estate has no system integration at all, which means the
  sources are spreadsheets and paper held by people rather than databases held by IT.
traces_to: [01-05, 05-02, M01, M15, M17, M19, M24, M28, M29, M33, M50, M56, M64, DM-001, DM-003, DM-011, DM-014]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
data_file: DM-002_Source_System_Register.csv
effective_dated: no
sources:
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §6.1 current system landscape and §6.5 legacy decommission commitment — 19 legacy systems and practices with their replacing module and wave
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/ — §16.4 of all 67 module specifications, enumerated 2026-08-18; every source in §2.2 is named by at least one module
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §12 — eleven source domains with volume and target; §1 DM-09 UTF-8 with bn_BD collation
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §Security — NFR-086c non-production environments never contain unmasked residency-classified data; OPS-07 migration reversibility
    verified: 2026-08-18
    class: P1
  - source: primary-doc/1000FiX_ERP_Technology_Stack_Specification.md — station.1000fix.com and 123.0.26.238/orderTracking listed as database extracts targeting M01 and P01 at W2
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# DM-002 — Legacy Source System Inventory and Extract Catalogue

> Governs `DM-002_Source_System_Register.csv`. The markdown governs; the data file loads.
>
> **Template conformance note.** `CG-009` §3 allocates `TPL_Master_Data_Specification.md` to this
> file. The template is designed for a dataset that loads into the ERP; this register describes
> **systems the ERP extracts from**. Every template section is retained in order and answered at
> source-register level: §2 is the register's own schema, §4 validates registry completeness rather
> than payload, §7 states source volumes rather than target rows. The interpretation is declared
> here so the adaptation is visible rather than silent (`CP-09`, `E7`).
>
> **Identifier note (`CG-005` §3.3).** `DM-002` is a **content** identifier. `05-02` `DM-09`
> (modelling standard — UTF-8 and `bn_BD` collation) is cited with its document prefix throughout.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Migration control |
| Owning module | `M28` for extract execution; `M64` for quality assessment |
| Data steward | Data Migration Lead |
| Golden source | This register |
| Refresh cadence | **Continuous** — a source discovered is a source registered the same day |
| Environments | Dev · SIT · UAT · Prod *(extract targets `staging` only)* |
| Content class | E — Internal governance |
| Effective-dated | no |
| Build wave | **W0** |
| First extract wave | **W1** |

**Consequence of absence (`CP-03`).** `05-02` §12 lists **eleven** source domains. Extracting §16.4
from all 67 module specifications on 2026-08-18 produced **forty-eight distinct sources**. The gap is
not an error in `05-02` — it lists domains, not systems — but a migration planned against eleven
domains will meet thirty-seven unplanned sources, most of them held by a named individual in a
folder, and each one discovered at the moment it is needed.

**Seventeen of the forty-eight are not systems at all.** They are paper, whiteboards, sign-in books,
email folders and personal knowledge. An extract plan written for databases will not touch them.

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `source_id` | char(7) | ✔ | `SRC-nnn`, permanent, never reused | — | |
| `source_name` | text(160) | ✔ | | — | As the business calls it, not as IT calls it |
| `source_class` | enum | ✔ | See §2.1 | — | Determines the extract method |
| `custodian_role` | text(120) | ✔ | A role, never a person's name in the register | — | `RF-010` names the person |
| `physical_location` | text(200) | ✔ | | — | Branch, server, mailbox, cabinet, portal URL |
| `holds_personal_data` | bool | ✔ | | — | Drives `NFR-086` handling |
| `sensitivity_max` | enum | ✔ | S0 / S1 / S2 / S3 (`05-02` §10) | — | Highest class held |
| `extract_method` | enum | ✔ | See §2.1 | — | |
| `extract_owner` | text(120) | ✔ | | — | Who physically produces the extract |
| `access_constraint` | text(240) | ✔ | | — | **The most commonly underestimated column** |
| `encoding_observed` | text(40) | ✔ | Observed, not assumed | — | `05-02` `DM-09` requires UTF-8 at target |
| `refresh_window` | enum | ✔ | one_off / daily / weekly / on_demand / delta_until_cutover | — | |
| `first_extract_wave` | enum | ✔ | W0…W9 | — | |
| `decommission_wave` | enum | | W0…W9; null = retained | — | From BRD §6.5 |
| `known_quality_issues` | text(600) | ✔ | | — | Stated before profiling, updated after |
| `profiling_status` | enum | ✔ | not_started / in_progress / reported / accepted | — | `MS-04` gate |
| `target_workbooks` | multi-fk | ✔ | → `DM-004`…`DM-010` | — | |
| `active` | bool | ✔ | | — | |

### 2.1 Source classes and their extract methods

| Class | Definition | Extract method | Count | Effort characteristic |
|---|---|---|---:|---|
| **`DB`** | A queryable database behind an application | `database_extract` | 4 | Low effort, high confidence |
| **`SS`** | Spreadsheet estate — many files, many owners, no schema | `spreadsheet_collection` | 14 | **Collection is the hard part, not parsing** |
| **`PORTAL`** | A third party's portal we can log into but not query | `portal_download` | 5 | Rate-limited, manual, often no bulk export |
| **`MAIL`** | An email folder used as a record system | `mailbox_export` | 2 | Unstructured; requires human triage |
| **`PAPER`** | Physical documents, files, books, whiteboards | `document_scan` + `manual_transcription` | 12 | **Highest cost per record in the estate** |
| **`PEOPLE`** | Knowledge held only in people's heads | `interview_capture` | 3 | Not an extract; an authoring exercise (`DM-001` disposition `N`) |
| **`PUB`** | An externally published authoritative register | `published_register` | 4 | Loaded as fact; version-pinned |
| **`CFG`** | Configuration, credential and scheduled-job stores | `survey` + `rotate_or_reset` | 4 | Never carried across; rotated or reset |
| | | **Total** | **48** | |

> **Why `PEOPLE` is in an extract catalogue.** `M22` §16.4 requires the initial competency matrix to
> be constructed through supervisor assessment of 500+ employees; `M63` requires the
> delegation-of-authority matrix to be captured from current practice; `M65` requires the statutory
> obligation register to be *"discovered, not migrated"*. If these are not in the source inventory
> they are in nobody's plan.

### 2.2 The source register

Derived by enumeration of BRD §6.1, BRD §6.5 and all 67 module `§16.4` sections on **2026-08-18**.

#### A. Application databases — `DB`

| ID | Source | Custodian | Holds PII | Max | First extract | Decommission | Known quality issues |
|---|---|---|:--:|:--:|:--:|:--:|---|
| `SRC-001` | `station.1000fix.com` order-tracking application | CTO | ✔ | S2 | W1 | **W2** | Volume unknown; *"to be profiled"* (`M01` §16.4). Standalone, no ERP linkage |
| `SRC-002` | Legacy tracker `123.0.26.238/orderTracking` | CTO | ✔ | S2 | W1 | **W2** | **Unsupported, unsecured, no integration** (RFP §current state). Volume unknown |
| `SRC-003` | WordPress site `1000fix.com` — booking submissions and FAQ content | Marketing Head | ✔ | S2 | W1 | W2 *(booking)* | 5–7 s load; basic booking only; submissions may exist only as email |
| `SRC-004` | Standalone accounting software | CFO | — | S2 | **W3 minus 2 months** | **W3** | Chart of 400–800 accounts, **rationalisation decision unresolved** (`M19` `Q-02`); no dimensional history |

#### B. Spreadsheet estate — `SS`

| ID | Source | Custodian | Files | Holds PII | First extract | Decommission | Known quality issues |
|---|---|---|---|:--:|:--:|:--:|---|
| `SRC-005` | Branch service order spreadsheets | Branch Operations Lead | **51+** | ✔ | W1 | **W2** | ~50,000 open and recent; per-branch formats; inconsistent order numbering (BRD §6.2 process 1) |
| `SRC-006` | Branch inventory spreadsheets | Warehouse Manager | **51+** | — | W2 | **W2** | **~75% accurate — explicitly not loaded as opening balances** (`M15` §16.4) |
| `SRC-007` | Central warehouse stock records | Warehouse Manager | few | — | W2 | W2 | ~10,000 SKUs; same accuracy exposure |
| `SRC-008` | Customer master spreadsheets | Chief Commercial Officer | many | **✔** | W1 | W2 | **100,000+ rows; duplicate rate unmeasured; `ASM-03` assumes ≥ 80% quality and it is unproven** |
| `SRC-009` | Corporate account lists held by account managers | Chief Commercial Officer | ~10 | ✔ | W1 | W2 | ~2,000 accounts; held individually, not centrally; hierarchy implicit |
| `SRC-010` | AMC / RAMC tracking spreadsheets | Chief Commercial Officer | several | ✔ | W4 minus 2 months | **W4** | 3,000–5,000 contracts; entitlement consumption not tracked; renewal dates manually maintained |
| `SRC-011` | Branch service price sheets | Chief Commercial Officer | **51+ variants** | — | W1 | W3 | **~1,200 price points, inconsistent between branches** (`M11` §16.4) — conflicts must go to the CCO, never resolved silently |
| `SRC-012` | Parts price and inventory lists | Warehouse Manager | several | — | W1 | W3 | **~18,000 rows, estimated 30–40% duplication** (`M37` §16.4) |
| `SRC-013` | HR spreadsheets | HR Director | several | **✔** | W5 | **W5** | 500+ employees; service history incomplete (`M21` §16.4) |
| `SRC-014` | Excel payroll workbook | HR Director | 1 | **✔** | W5 | **W5** | **3-day cycle, manual tax**; YTD balances are the only migratable content and must be exact (`M56` §16.4) |
| `SRC-015` | Leave balance spreadsheets | HR Director | several | ✔ | W5 | W5 | Balances must be **agreed with each employee before cutover** (`M55` §16.4) |
| `SRC-016` | Vendor and supplier lists, accounts-payable records | Procurement Manager | several | ✔ | W3 | W3 | 40–120 active, 200–400 historical; **bank details must be independently re-verified** (`M52` §16.4) |
| `SRC-017` | Legacy fixed-asset spreadsheets | CFO | several | — | W5 minus 2 months | **W5** | 8,000–20,000 assets; **not loaded as opening balances — physical verification governs** (`M49` §16.4) |
| `SRC-018` | Open tender register and bid-bond schedule | Chief Commercial Officer | 1–2 | — | W3 | W3 | ~30 tenders, ~15 bonds; compliance matrices must be rebuilt manually |

#### C. Third-party portals — `PORTAL`

| ID | Source | Custodian | Holds PII | First extract | Decommission | Known quality issues |
|---|---|---|:--:|:--:|:--:|---|
| `SRC-019` | Brand partner claim portals (17+) | Finance Director | ✔ | W3 *(profiling)* | W4 | **~2,000 open claims; the recoverable balance is a real asset of unknown size** — profiling is a W3 prerequisite (`M09` §16.4) |
| `SRC-020` | Payment gateway and MFS settlement portals — bKash, Nagad, SSLCOMMERZ | CFO | ✔ | W3 | Retained *(becomes an integration)* | Open clearing balances must be reconstructed **and confirmed with the provider in writing** (`M50` §16.4) |
| `SRC-021` | Bank portals — statements, mandates, facilities | CFO | ✔ | W3 minus 2 months | Retained | **Bank balances come from the bank's statement, never the legacy book balance** (`M50` §16.4) |
| `SRC-022` | Telematics provider portal | Logistics Manager | ✔ | W5 | Retained | 12–24 months of history *"where the provider retains it"* (`M48` §16.4) |
| `SRC-023` | Recruitment channel portals | HR Director | **✔** | — | — | **Disposition `P`** — historical applications are purged, not migrated (`M58` §16.4, PDPA 2026) |

#### D. Email as a record system — `MAIL`

| ID | Source | Custodian | Holds PII | First extract | Decommission | Known quality issues |
|---|---|---|:--:|:--:|:--:|---|
| `SRC-024` | Warranty claim email archive | Finance Director | ✔ | W4 | **W4** | 12–24 months; **claims lost in threads; 15–20% revenue leakage attributed to this practice** (BRD §6.2 process 7) |
| `SRC-025` | Brand rate cards received as email attachments | Chief Commercial Officer | — | W3 | W3 | ~400 rate lines across 17+ brands; versions indistinguishable without the covering mail |

#### E. Paper and physical records — `PAPER`

| ID | Source | Custodian | Volume | First extract | Decommission | Known quality issues |
|---|---|---|---|:--:|:--:|---|
| `SRC-026` | Paper service history archive | Service Ops Director | **500,000+** | W2 | W6 | **Disposition `A`.** OCR-indexed into `M24`; digitised **by priority of need, not chronology** (`M24` §16.4) |
| `SRC-027` | Paper service forms and QC checklists in circulation | Service Ops Director | Daily flow | W1 | **W2** | Keyed 1–3 days late today; forms lost; photos not standardised (BRD §6.2 process 4) |
| `SRC-028` | Workshop whiteboards and paper job cards | Service Ops Director | ~500 devices WIP | W2 | **W2** | Current WIP only; **captured during a single cutover count**, not extracted |
| `SRC-029` | Attendance sign-in books | HR Director | 51+ sites | — | **W5** | **Disposition `L`** — *"not machine-readable and not reliable"* (`M55` §16.4) |
| `SRC-030` | Employee personnel files | HR Director | 500+ | W5 | W5 | Contracts, certificates, NID copies; **S3 content; residency rules apply** |
| `SRC-031` | Contract and agreement originals | Quality Manager | ~3,000–5,000 | W4 | Retained *(physical originals registered)* | Where a paper original must legally be retained, the scan **and** the physical record are both registered (`M24` §16.4) |
| `SRC-032` | ISO / QMS paper records | Quality Manager | 3 certification cycles | W5 | **W5** | **Disposition `A`** for history; only confirmed-open CAPAs and findings migrate live |
| `SRC-033` | Vehicle registration folders, insurance policies, driver licences | Logistics Manager | 150–400 vehicles; 200–400 drivers | W5 | W5 | **A document without scanned evidence loads as expired**, taking the vehicle off-road (`M46` §16.4) |
| `SRC-034` | Lease, tenancy, trade and fire licence documents | Branch Operations Lead | 51+ sites | W7 | W7 | **Loaded from the physical document, scanned and hashed** — never from a summary spreadsheet (`M47` §16.4) |
| `SRC-035` | Branch calibration certificate folders | Quality Manager | Unknown | W5 | W5 | **A calibration loads only where the certificate exists and traceability is verifiable**; otherwise the instrument enters *out of service* (`M45` §16.4) |
| `SRC-036` | Data recovery job cards | Technical Services Head | Current work | W6 | **W6** | Residual customer data held from past work is **disposition `P`** — audited and purged before W6 |
| `SRC-037` | Rental log books and refurbishment tally sheets | Corporate Services Head / Retail Operations Head | WIP only | W6 | **W6** | History not migrated — no condition evidence, no grading standard, no cost records |

#### F. Knowledge held by people — `PEOPLE`

| ID | Source | Custodian | Scale | Needed by | Note |
|---|---|---|---|:--:|---|
| `SRC-038` | Supervisor knowledge of technician competency | HR Director | **500+ employees** | **Well before W5** | `M22` §16.4 — *"the hard one"*. Not an extract; a structured assessment programme |
| `SRC-039` | Delegation-of-authority limits in current practice | CFO | All limits in force | **W3 cutover** | `M63` §16.4 — must be agreed, then encoded as decision tables |
| `SRC-040` | Statutory obligation knowledge held by finance and HR | CFO with HR Director | Multi-week exercise | W1–W4 | `M65` §16.4 — *"the highest-value non-software deliverable in M65"* |

#### G. Published external registers — `PUB`

| ID | Source | Custodian | Version pinning | First load | Note |
|---|---|---|---|:--:|---|
| `SRC-041` | Bangladesh administrative geography — divisions, districts, upazilas, unions/wards | Master Data Owner | `MD-006` `source_version` column | W1 | 8 / 64 / ~495; loaded as fact |
| `SRC-042` | Public holiday gazette | HR Director | Annual | W1 | `MD-041`; reloaded annually |
| `SRC-043` | NBR statutory pack — rates, codes, forms, tariff schedule | CFO | **Fiscal-year pinned** (`CG-006` §5) | W4 minus 3 months | `MD-037`, `MD-043`; **`verified_by` and `verified_on` required at gate G6** |
| `SRC-044` | Bangladesh Bank / AD bank exchange rates | CFO | Daily connector after W3 | W3 | 2 years of history loaded once (`M19` §16.4) |

#### H. Configuration and credential stores — `CFG`

| ID | Source | Custodian | Treatment |
|---|---|---|---|
| `SRC-045` | Integration credentials in configuration files and developers' notes | CTO | **Moved to vault and rotated on migration**, on the assumption that anything previously in plain text is compromised (`M28` §16.4) |
| `SRC-046` | Internal user accounts and passwords | Security Lead | **All credentials reset**, never carried (`M29` §16.4) |
| `SRC-047` | Customer portal accounts | Security Lead | Migrated with **forced re-authentication on first use**, not a mass reset — avoids a support incident at 250,000+ scale |
| `SRC-048` | Legacy cron jobs and scheduled scripts | CTO | **Surveyed and registered** — *"an unregistered job that stops running is invisible"* (`M30` §16.4) |

> **Count, enumerated 2026-08-18.** Forty-eight registered sources: `DB` 4 · `SS` 14 · `PORTAL` 5 ·
> `MAIL` 2 · `PAPER` 12 · `PEOPLE` 3 · `PUB` 4 · `CFG` 4. **Four are queryable databases. Fifteen
> are paper or people; seventeen if the two email archives are counted.** This distribution is the
> single most important fact in the file, and it is why the migration plan cannot be an ETL plan.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `source_id` |
| Surrogate key | None — the register is small and human-maintained |
| Code format | `SRC-nnn`, allocated in discovery order, **never in category order** |
| Reuse policy | **Never reused.** A retired source is marked `active = FALSE` with the retirement date and the decommission evidence; the ID stays (`CP-02` equivalent for data) |
| Relationship to content IDs | `SRC-nnn` is a **data** identifier inside `DM-002`, not a content identifier. It is never written without the `SRC-` prefix |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `SI-01` | No extract may run against a source whose `profiling_status` is `not_started` (`MS-04`, `05-02` `MIG-01`) | **H** | `ERR-SRC-001` |
| `SI-02` | A source with `holds_personal_data = TRUE` may not be extracted to a non-production environment without masking (`NFR-086c`) | **H** | `ERR-SRC-002` |
| `SI-03` | A source with `sensitivity_max = S3` may not be extracted before the Bangladesh-resident store is live and verified (`NFR-086`, `MS-21`) | **H** | `ERR-SRC-003` |
| `SI-04` | Every extract declares `encoding_observed`; an extract with an undeclared encoding is rejected (`05-02` `DM-09`) | **H** | `ERR-SRC-004` |
| `SI-05` | A source named in any module `§16.4` with no row in this register is a **registry breach** and blocks the wave gate | **H** | `ERR-SRC-005` |
| `SI-06` | A `PAPER` or `PEOPLE` source with `first_extract_wave` inside the wave it serves warns — both classes need lead time measured in months | **S** | `WRN-SRC-006` |
| `SI-07` | A source with a `decommission_wave` that has passed while `active = TRUE` blocks the gate (BRD §6.5: *"a wave gate is not passed while its legacy process is still running beyond the agreed parallel-run period"*) | **H** | `ERR-SRC-007` |
| `SI-08` | `access_constraint` may not be blank. "None" is a valid value; blank is not | **H** | `ERR-SRC-008` |
| `SI-09` | A `PUB` source without a pinned version may not load (`CG-006` §5 statutory pinning) | **H** | `ERR-SRC-009` |
| `SI-10` | A credential-bearing source (`SRC-045`, `SRC-046`) may not be marked migrated until rotation or reset is evidenced (`MS-25`) | **H** | `ERR-SRC-010` |
| `SI-11` | Two sources claiming to be golden for the same target attribute warn and are escalated to the Master Data Owner | **S** | `WRN-SRC-011` |
| `SI-12` | `known_quality_issues` may not be blank after `profiling_status = reported` | **C** | `WRN-SRC-012` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| [`DM-001_Data_Migration_Strategy_and_Scope_Register.md`](DM-001_Data_Migration_Strategy_and_Scope_Register.md) | 1:N | **Before** — a source with no in-scope dataset is not extracted |
| `MD-002` legal entity, `MD-003` branch | N:1 | Custodian and location resolve to registered branches |
| `05-04` role matrix | N:1 | `custodian_role` resolves to a registered role |

| Depended on by |
|---|
| [`DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md`](DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md) · `DM-004`…`DM-010` field mappings · [`DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md`](DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) profiling · [`DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) freeze scope · `CM-012` branch readiness |

> Load order is consolidated in `MD-048` for seed data and `DM-003` for migrated data. Update both
> together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | BRD §6.1 and §6.5; the `§16.4` section of all 67 module specifications |
| Who supplies it | Data Migration Lead, from the custodians named in each row |
| Collection method | **Enumeration** (`RG-06`) — extract every §16.4 source table, deduplicate by system rather than by module, then walk the BRD landscape diagram for anything no module claimed |
| Known quality issues | **A source held by one person is invisible until that person is asked.** Nineteen of forty-eight are paper or people; discovery is not complete and cannot be declared complete |
| Cleansing rules | `DM-011` |
| Re-verification | At every wave boundary, and whenever a module §16.4 changes |

---

## 7. Volumes

| Source class | Sources | Records in scope | Extract characteristic |
|---|---:|---|---|
| `DB` | 4 | Unknown for three of the four — *"to be profiled"* | One-off SQL extract plus delta |
| `SS` | 14 | 100,000+ customers · ~50,000 orders · ~18,000 parts rows · 8,000–20,000 assets · 500+ employees | **Collection of 51+ files per estate is the constraint, not parsing** |
| `PORTAL` | 5 | ~2,000 claims; settlement history per provider | Manual, rate-limited, often no bulk export |
| `MAIL` | 2 | 12–24 months of claim correspondence | Human triage required |
| `PAPER` | 12 | **500,000+ service records**; 3,000–5,000 contracts; 51+ site document sets | **Highest cost per record; digitised by priority of need** |
| `PEOPLE` | 3 | 500+ competency assessments; all authority limits; the obligation set | Months of elapsed time, not compute |
| `PUB` | 4 | 8 / 64 / ~495 geography nodes; full tariff chapters | Loaded as fact, version-pinned |
| `CFG` | 4 | 150–250 internal accounts · 250,000+ portal accounts · all configuration and cron entries | Survey and rotate; nothing is carried across |
| **Total** | **48** | | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | **Anyone may report a source; only the Data Migration Lead may register one** |
| Who may deactivate | Data Migration Lead, on evidenced decommission |
| Approval required | CTO for a `DB` source; CFO for any finance-bearing source; Security Lead for any `S3` source |
| Effective dating | Not effective-dated; `first_extract_wave` and `decommission_wave` carry the timeline |
| Archive rule | Records are archived (`active = FALSE`), never deleted (`05-02` `DM-06`) |
| Logged in | `RF-006` for any addition, disposition change or decommission |

---

## 9. Sample rows

```csv
source_id,source_name,source_class,custodian_role,holds_personal_data,sensitivity_max,extract_method,access_constraint,encoding_observed,refresh_window,first_extract_wave,decommission_wave,profiling_status,target_workbooks,active
SRC-001,station.1000fix.com order tracking,DB,CTO,TRUE,S2,database_extract,No documented schema; hosting vendor access required,unknown_pending_profiling,delta_until_cutover,W1,W2,not_started,DM-004;DM-005;DM-006,TRUE
SRC-006,Branch inventory spreadsheets,SS,Warehouse Manager,FALSE,S1,spreadsheet_collection,51+ files held locally at each branch,windows-1252_mixed,one_off,W2,W2,not_started,DM-007,TRUE
SRC-008,Customer master spreadsheets,SS,Chief Commercial Officer,TRUE,S3,spreadsheet_collection,Held across several teams; NID columns present in some files,mixed_ascii_and_bengali_legacy,one_off,W1,W2,not_started,DM-004,TRUE
SRC-026,Paper service history archive,PAPER,Service Ops Director,TRUE,S2,document_scan,Physical archive at branch and central store,n/a,one_off,W2,W6,not_started,DM-006,TRUE
SRC-038,Supervisor knowledge of technician competency,PEOPLE,HR Director,TRUE,S2,interview_capture,Requires supervisor time across 51+ sites,n/a,one_off,W5,,not_started,DM-009,TRUE
SRC-043,NBR statutory pack,PUB,CFO,FALSE,S0,published_register,Published; adviser verification required at G6,utf8,on_demand,W4,,accepted,DM-008,TRUE
```

---

## 10. Migration notes

This register is **migration control content**: it is never loaded into an operational table. It is
loaded into the migration staging environment as the control table that `DM-003` sequences against
and `DM-013` reconciles to.

**The `station.1000fix.com` and `123.0.26.238` extracts are the only two sources in the estate that
could be re-extracted after decommission — and they cannot.** BRD §6.5 commits to withdrawing both
at W2. Any data not extracted before that date is lost. `SI-07` exists for this reason.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`DM-001_Data_Migration_Strategy_and_Scope_Register.md`](DM-001_Data_Migration_Strategy_and_Scope_Register.md) | The disposition that decides whether a source is extracted at all |
| [`DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md`](DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md) | Extract order derived from load order |
| [`DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md`](DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) | The profiling that `SI-01` gates on |
| [`DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) | Which sources freeze, and when |
| `01-05` *(planned)* | The research document this register was expected to trace to — **it does not exist** |
| `M28` §16.4 · `M29` §16.4 · `M30` §16.4 | Credential rotation, account reset and scheduled-job survey |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Forty-eight sources registered in seven classes, derived by enumeration of BRD §6.1/§6.5 and all 67 module §16.4 sections | Data Migration Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; the source-register adaptation is **declared**, not silent
- [x] Record structure names column, type, required flag, constraint and Bengali requirement
- [x] Keys, code format and reuse prohibition stated
- [x] Every validation rule carries a class and an error message ID
- [x] Load dependencies stated and reconciled with `DM-003` and `MD-048`
- [x] Golden source and acquisition method named; method is **enumeration**, dated
- [x] Volumes stated per source class
- [x] Sample rows included and parse as CSV
- [x] Archive rule states records are archived, never deleted (`05-02` `DM-06`)
- [x] Every source traced to the module §16.4 or BRD section that names it
- [x] `PAPER`, `PEOPLE` and `MAIL` made first-class classes, so the seventeen non-system sources are visible
- [x] Decommission waves carried from BRD §6.5 with the gate consequence stated (`SI-07`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] **Profiling not started on any source** — `SI-01` blocks every extract until it is
- [ ] Named approver recorded — **pending Data Migration Lead with CTO**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
