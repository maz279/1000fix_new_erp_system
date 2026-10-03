---
id: DM-012
title: Migration Load Template Pack
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration
author: Data Migration with Platform Engineering
reviewers: [Master Data Owner, CFO, HR Director, Warehouse Manager, Chief Commercial Officer, Branch Operations Lead, Localisation Lead, QA Lead]
approver: Data Migration Lead with Master Data Owner
content_class: C
purpose: >
  Issues the machine-readable load templates that business owners fill in, with column definitions,
  types, required flags, controlled-value lists, worked examples and the file conventions every
  template obeys. Business owners are accountable for supplying and cleansing their own data, and
  they can only discharge that accountability against a template they understand; a template that
  is ambiguous about encoding, dates, decimals or blanks produces fifty-one differently-wrong files
  and a rejection rate nobody can attribute.
traces_to: [MD-048, M64, M30, DM-001, DM-002, DM-003, DM-004, DM-005, DM-006, DM-007, DM-008, DM-009, DM-010, DM-011, DM-013, DM-014, CG-011]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: DM-012_Load_Template_Register.csv
effective_dated: no
sources:
  - source: project_content/02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md §2 — load-index record structure, reload policy enum, masking_required, row_count_expected, owner_signoff_required; §4 LDX-01 to LDX-07
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 — DM-07 monetary fields with an explicit currency and never floats; DM-08 stored UTC and presented Asia/Dhaka with durations in minutes; DM-09 UTF-8 throughout with bn_BD collation
    verified: 2026-08-18
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §11.6.2 — MIG-003 cleansing performed in the source with the business data owner accountable; MIG-008 migration tooling delivered to the Company, repeatable and re-runnable; MIG-011 Bengali text conversion and encoding normalisation to UTF-8
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M64 §16.4 — each migration batch is scored against its domain rules before acceptance and failing records are rejected to a remediation queue
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# DM-012 — Migration Load Template Pack

> Governs `DM-012_Load_Template_Register.csv` and the template files it indexes. The markdown
> governs; the templates are issued from it.
>
> **Template conformance note.** `CG-009` §3 allocates `TPL_Master_Data_Specification.md`. This file
> governs a **pack of templates** rather than one dataset; every template section is retained in
> order and answered at pack level. Declared here (`CP-09`, `E7`).
>
> **Identifier note (`CG-005` §3.3).** `DM-012` is a **content** identifier; `05-02` `DM-07`,
> `DM-08` and `DM-09` (modelling standards — money, time and text) are cited with their document
> prefix and are the three rules every template convention exists to satisfy.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Migration tooling and interchange |
| Owning module | `M64` for validation; `M30` for the configuration the templates target |
| Data steward | Data Migration Lead |
| Golden source | This pack — **templates are issued, never hand-made** |
| Refresh cadence | Per wave; a template version is pinned to the wave that consumes it |
| Environments | All — the same template is used for dev, SIT, UAT and production loads |
| Content class | C — Operational-critical |
| Effective-dated | no |
| **Build wave** | **W1** |
| **Load wave** | **W1 onward** — every wave uses the pack |

**Consequence of absence (`CP-03`).** BRD `MIG-003` and `00-04` `DEP-05` both put source cleansing
and extraction on the **business data owner**, per wave. That accountability is only dischargeable
against something concrete. The register's justification is exact: *"Business owners provide data;
they can only do so against a template they understand."*

What happens without an issued pack is predictable and expensive:

| Failure | Consequence |
|---|---|
| Fifty-one branches each invent a column layout | Fifty-one bespoke parsers, or fifty-one manual reformatting exercises |
| Dates typed as `04/05/2026` with no declared format | 4 May or 5 April — a silent, systematic error across a whole file |
| Mobile numbers in a numeric column | The leading zero is gone before the file ever reaches the migration team |
| Bengali typed in a legacy encoding | Mojibake at load, discovered after matching has already run |
| Blank versus `NULL` versus `N/A` versus `-` | Four representations of "no value", three of which become values |
| A file with no version and no row count | Nobody can say which version was loaded, or whether it was complete |

---

## 2. Record structure

### 2.1 The template register — `DM-012_Load_Template_Register.csv`

| Column | Type | Req | Constraint | Description |
|---|---|:--:|---|---|
| `template_id` | char(11) | ✔ | `MLT-nnn`, permanent | |
| `template_name` | text(120) | ✔ | | The file business owners receive |
| `target_entity` | text(60) | ✔ | `fix.*` model | |
| `owning_workbook` | fk | ✔ | → `DM-004`…`DM-010` | The mapping that defines its columns |
| `load_tier` | fk | ✔ | → `DM-003` `X0`…`X9` | Where it sits in the sequence |
| `load_wave` | enum | ✔ | W0…W9 | |
| `supplier_role` | text(120) | ✔ | The business role that fills it in | Never a person's name |
| `reload_policy` | enum | ✔ | full_replace / upsert / append_only / **never_reload** | Same enum as `MD-048` |
| `masking_required` | bool | ✔ | | `NFR-086c` |
| `row_count_expected` | int | | | Reconciliation control (`MD-048` `LDX-04`) |
| `owner_signoff_required` | bool | ✔ | Always TRUE for production | `MD-048` `LDX-03` |
| `version` | text(12) | ✔ | `v<major>.<minor>` | **Pinned to the wave** |
| `active` | bool | ✔ | | |

### 2.2 File conventions — the rules every template obeys

**`LT-01`: one set of conventions for the whole pack. A template that varies from them is defective,
not customised.**

| # | Convention | Value | Why |
|---|---|---|---|
| `F-01` | Format | **UTF-8 CSV, no byte-order mark**, `\n` line endings | `05-02` `DM-09`; BOM breaks naive parsers, and the estate has several |
| `F-02` | Delimiter | Comma; fields containing a comma, quote or newline are double-quoted with `""` escaping (RFC 4180) | Bengali addresses contain commas routinely |
| `F-03` | Header | **Row 1 is the technical column name**, exactly as specified. Human labels live in the accompanying guide, never in the file | A renamed header is an unparseable file |
| `F-04` | **Dates** | **`YYYY-MM-DD`**, ISO 8601, no other form accepted | Removes the `dd/mm` versus `mm/dd` ambiguity entirely |
| `F-05` | **Timestamps** | `YYYY-MM-DDTHH:MM:SS+06:00` — explicit `Asia/Dhaka` offset | `05-02` `DM-08` stores UTC; the offset makes the conversion unambiguous |
| `F-06` | Durations | **Integer minutes** | `05-02` `DM-08` |
| `F-07` | **Decimals** | `.` as the decimal separator; **no thousands separator**; no currency symbol in the value | `05-02` `DM-07` |
| `F-08` | **Money** | Two columns — `amount` and `currency` (ISO 4217, `BDT` unless stated) | `05-02` `DM-07`: never a float, always an explicit currency |
| `F-09` | Booleans | `TRUE` / `FALSE`, upper case. **Not** `Y`/`N`, `1`/`0`, `Yes`/`No` | |
| `F-10` | **Empty** | **A blank cell means "no value".** `NULL`, `N/A`, `-`, `NA` and `0` are **values** and will be rejected or treated literally | The single most common source of silent error |
| `F-11` | Multi-value | Semicolon-separated within one cell, no spaces around the separator | Matches `MD-048` `depends_on` convention |
| `F-12` | Numerals | **Western Arabic digits in all data fields**, including Bengali-language rows | Bengali numerals are a presentation choice (`BN-007`), not a storage form |
| `F-13` | Bengali text | UTF-8 Unicode only; **legacy-encoded Bengali must be converted before the file is submitted** | `DM-011` `C-03`; conversion after matching is too late |
| `F-14` | Phone numbers | **Text column, never numeric.** `01712345678` with the leading zero intact | The leading zero is lost the moment a spreadsheet treats it as a number |
| `F-15` | Identifiers | Text; leading zeros significant and preserved | |
| `F-16` | File name | `<template_id>_<source_id>_<YYYYMMDD>_v<n>.csv` | Makes the version, source and date visible in a listing |
| `F-17` | Row limit | 50,000 rows per file; larger sets split with `__partnn` (`CG-005` §5 multi-part convention) | Spreadsheet tools fail unpredictably above this |

> **`LT-02` — the spreadsheet trap is designed around, not warned about.** `F-14` and `F-15` exist
> because Excel silently coerces `01712345678` to `1712345678`. A template distributed as `.xlsx`
> with those columns pre-formatted as **Text** prevents the coercion at the point it would happen;
> a template distributed as `.csv` with a warning in a covering email does not. **Templates are
> therefore issued in both forms**: an `.xlsx` for filling in, with formats and validation applied,
> and a `.csv` specification for the pipeline.

### 2.3 The control block — on every template

**`LT-03`: every load file carries the same six control columns, and the loader populates none of
them for the business owner.**

| Column | Filled by | Purpose |
|---|---|---|
| `source_id` | Business owner | → `DM-002` `SRC-nnn`; which estate this file came from |
| `legacy_record_id` | Business owner | **The source's own key, verbatim** — `MS-18`, BRD `MIG-010`, `FR-SRM-088` |
| `row_seq` | Template | Line number within the file, for error reporting |
| `migration_batch_id` | Loader | Assigned at tier `X0` (`DM-003`) |
| `submitted_by` | Business owner | The role submitting; paired with `submitted_on` |
| `submitted_on` | Business owner | `F-04` date |

> **`LT-04`.** A file with a blank `legacy_record_id` cannot be reconciled, re-run or looked up. It
> is rejected at the door, before any content validation, with a message that says so.

### 2.4 The mapping-workbook template

The seven mapping workbooks (`DM-004`…`DM-010`) share one structure, defined canonically in
[`DM-004_Field_Mapping_Workbook_Party_and_Customer.md`](DM-004_Field_Mapping_Workbook_Party_and_Customer.md) §2.1
and **not restated here** (`CP-01`). This pack issues it as `MLT-000`, an empty workbook with:

- the seventeen mapping columns, in order, with data validation on the enum columns;
- the `unmapped_disposition` list from `DM-004` §2.4;
- the `status` progression `proposed → business_confirmed → tested → signed_off`, with the file
  locked against load until `tested`;
- a first sheet carrying the workbook's `owning module`, build wave, load wave and named owner.

### 2.5 The template inventory

| ID | Template | Target | Workbook | Tier | Wave | Supplier role |
|---|---|---|---|:--:|:--:|---|
| `MLT-000` | Field mapping workbook (blank) | — | all | — | W1 | Migration analyst |
| `MLT-001` | Migration batch register | control | `DM-003` | `X0` | W1 | Data Migration |
| `MLT-002` | Party — individual | `fix.party` | `DM-004` | `X1` | W1 | Chief Commercial Officer |
| `MLT-003` | Party — organisation and hierarchy | `fix.party`, `fix.party.hierarchy` | `DM-004` | `X1` | W1 | Chief Commercial Officer |
| `MLT-004` | Address | `fix.address` | `DM-004` | `X1` | W1 | Chief Commercial Officer |
| `MLT-005` | Party role | `fix.party.role` | `DM-004` | `X1` | W1 | Per role owner |
| `MLT-006` | Identity document *(`S3`, deferred)* | `fix.identity.document` | `DM-004` | `X2` | **Gated** | Chief Data Officer |
| `MLT-007` | Asset — customer device | `fix.asset` | `DM-005` | `X3` | W1 | Service Ops Director |
| `MLT-008` | Asset identifier | `fix.asset.identifier` | `DM-005` | `X3` | W1 | Service Ops Director |
| `MLT-009` | Asset ownership and estate | `fix.asset.ownership`, `fix.asset.estate` | `DM-005` | `X3` | W1–W2 | Service Ops Director |
| `MLT-010` | Service order | `fix.service.order` | `DM-006` | `X5` | W1–W2 | Branch Operations Lead |
| `MLT-011` | Work order | `fix.work.order` | `DM-006` | `X5` | W2 | Branch Operations Lead |
| `MLT-012` | **Stock count sheet** | `fix.stock.quant` | `DM-007` | `X6` | W2 | Warehouse Manager |
| `MLT-013` | **Van count sheet** | `fix.van.stock` | `DM-007` | `X6` | W2 | Branch Operations Lead |
| `MLT-014` | Consignment balance confirmation | `fix.consignment.balance` | `DM-007` | `X6` | W2 | Finance Director |
| `MLT-015` | Open purchase commitment | `purchase.order` | `DM-007` | `X6` | W3 | Procurement Manager |
| `MLT-016` | Chart of accounts cross-reference | `fix.gl.account` | `DM-008` | `X7` | W3 | Financial Controller |
| `MLT-017` | **Opening trial balance** | `account.move.line` | `DM-008` | `X7` | W3 | CFO |
| `MLT-018` | AR open item | `fix.ar.open.item` | `DM-008` | `X7` | W3 | Financial Controller |
| `MLT-019` | AP open item | `fix.ap.open.item` | `DM-008` | `X7` | W3 | Financial Controller |
| `MLT-020` | **Cash count sheet** | `fix.branch.cash.day` | `DM-008` | `X7` | W3 | Branch manager |
| `MLT-021` | Bank position and reconciling items | `fix.bank.balance` | `DM-008` | `X7` | W3 | Financial Controller |
| `MLT-022` | Tax opening position | `fix.input.credit.ledger` | `DM-008` | `X7` | W4 | Tax Manager |
| `MLT-023` | Contract and coverage | `fix.contract` | `DM-010` | `X4` | W4 | Chief Commercial Officer |
| `MLT-024` | Entitlement opening grant | `fix.entitlement.consumption` | `DM-010` | `X4` | W4 | Chief Commercial Officer |
| `MLT-025` | Warranty registration | `fix.warranty.register` | `DM-010` | `X4` | W4 | Finance Director |
| `MLT-026` | Brand claim | `fix.brand.claim` | `DM-010` | `X4` | W4 | Finance Director |
| `MLT-027` | Subscription and opening MRR | `fix.subscription` | `DM-010` | `X4` | W4 | Financial Controller |
| `MLT-028` | Employee master | `hr.employee` | `DM-009` | `X8` | W5 | HR Operations Manager |
| `MLT-029` | **YTD payroll balance** | `fix.payroll.balance` | `DM-009` | `X8` | W5 | **HR Director with CFO** |
| `MLT-030` | Leave balance agreement | `fix.leave.entitlement` | `DM-009` | `X8` | W5 | HR Operations Manager |
| `MLT-031` | Competency assessment | `fix.employee.competency` | `DM-009` | `X8` | W5 | Line supervisor |
| `MLT-032` | **Fixed asset verification sheet** | `fix.asset.book` | `DM-008` | `X7` | W5 | CFO |
| `MLT-033` | Archive load — historical orders | archive | `DM-006` | `X9` | W2–W6 | Service Ops Director |
| `MLT-034` | Delegation of authority | `fix.authority.matrix` | `DM-003` | `X0` | W3 | CFO |

> **Thirty-five templates. Six of them are count sheets, not extracts** (`MLT-012`, `-013`,
> `-020`, `-032`, and the `M45`/`M66` sheets that do not yet exist — `DM-001` `O-06`). A count sheet
> is a different artefact: it is printed, carried, written on by two people, signed, and only then
> transcribed. Its template must be usable **on paper**.

### 2.6 The count-sheet variant

**`LT-05`: count-sheet templates are designed for the physical act, not for the database.**

| Requirement | Reason |
|---|---|
| Printable on A4, portrait, one location per page | It is carried around a store room |
| **Pre-populated with the expected item list** from the spreadsheet estate | Counters need to know where to look — the spreadsheets' only legitimate use (`DM-007` `IV-02`) |
| A **blank row block** for items found that are not on the list | Unlisted stock is the finding, not an inconvenience |
| Two counter-signature blocks and a supervisor block | `IV-13` |
| Location, date and **exact time** printed, not written | The count instant must fall inside the freeze window (`IV-14`) |
| A separate **variance column left blank at count time** | A counter who can see the expected figure counts toward it |
| Sequential page numbering with a declared page count | A missing page is a silent partial count |

> **The single most important design rule on a count sheet is the last one but one.** If the
> expected quantity is printed next to the count box, the count converges on the expectation and the
> exercise measures nothing. `M15`'s entire non-negotiable position depends on the count being
> independent.

### 2.7 Accessibility and language of the templates

| Rule | Detail |
|---|---|
| **`LT-06`** | Templates are **English-only** in their technical columns (`CG-010` §3.2 — `DM` is English-only), but the **accompanying completion guide for count sheets and branch-filled templates is Bengali-first** |
| Why | The people filling `MLT-012`, `-013` and `-020` are branch and store staff across 51+ sites. `CG-010` classifies the *content file* as English-only; it does not make the **instruction to a store keeper** English-only |
| Owner | The Bengali guide is `CM`/`TR` content, referenced from here — this pack does not author it |
| Accessibility | Count sheets follow `CG-011` for print: minimum type size, adequate contrast, no colour-only encoding — they are used in poorly lit store rooms |

> This is recorded as `O-04` because it is a **gap between two correct rules**: Category 12 is
> English-only, and the audience for six of its templates is not.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `template_id` |
| Code format | `MLT-nnn`, permanent, never reused |
| Version | `v<major>.<minor>`, **pinned to the wave that consumes it** (`CG-006` §5, `CP-08`) |
| File identity | `<template_id>_<source_id>_<YYYYMMDD>_v<n>.csv` (`F-16`) |
| Relationship to `_templates/` | **Different register.** `TPL_` in `project_content/_templates/` are *authoring* templates for content files (`CG-009`); `MLT-nnn` are *data* templates for load files |
| **Why not `TPL-DM-nnn`** | The obvious name was rejected because `CG-005` §3.2 **reserves `DM-015`…`DM-060` for future Data Migration content files**, and any repository-wide search for `DM-0nn` would return `TPL-DM-015` as if it were content `DM-015`. That is the same class of failure `CG-005` §3.3 registered for the `DM` space, and the `MLT-` prefix avoids creating a third one. Logged in `RF-006` |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `LT-01` | A load file must be an issued template version; hand-made files are rejected unopened | **H** | `ERR-LTP-001` |
| `LT-02` | Templates are issued in both `.xlsx` (formatted, validated) and `.csv` (specification) form | **C** | `WRN-LTP-002` |
| `LT-03` | The six control columns are present on every template | **H** | `ERR-LTP-003` |
| `LT-04` | A blank `legacy_record_id` rejects the file before content validation | **H** | `ERR-LTP-004` |
| `LT-05` | Count-sheet templates are printable and do not display the expected quantity beside the count box | **H** | `ERR-LTP-005` |
| `LT-06` | Branch-filled templates ship with a Bengali completion guide | **H** | `ERR-LTP-006` |
| `LT-07` | Header row must match the specification **exactly**; a renamed, reordered or inserted column rejects the file | **H** | `ERR-LTP-007` |
| `LT-08` | Dates that are not `YYYY-MM-DD` reject the row; the loader never guesses a format | **H** | `ERR-LTP-008` |
| `LT-09` | A phone or identifier column arriving numeric rejects the **file**, not the row — the leading zeros are already gone | **H** | `ERR-LTP-009` |
| `LT-10` | Monetary values require a paired currency column | **H** | `ERR-LTP-010` |
| `LT-11` | `NULL`, `N/A`, `-` and `NA` in a blank-permitted column are treated as placeholder values and rejected (`DM-011` `C-07`) | **H** | `ERR-LTP-011` |
| `LT-12` | Non-UTF-8 bytes reject the file (`05-02` `DM-09`) | **H** | `ERR-LTP-012` |
| `LT-13` | Bengali numerals in a data field reject the row (`F-12`) | **H** | `ERR-LTP-013` |
| `LT-14` | A file exceeding 50,000 rows must be split with the `__partnn` convention | **H** | `ERR-LTP-014` |
| `LT-15` | Actual row count must match `row_count_expected` within the declared tolerance, or the load rolls back (`MD-048` `LDX-04`) | **H** | `ERR-LTP-015` |
| `LT-16` | A production load requires the domain owner's recorded sign-off (`MD-048` `LDX-03`) | **H** | `ERR-LTP-016` |
| `LT-17` | `masking_required` blocks an unmasked load to any non-production environment (`NFR-086c`, `MD-048` `LDX-02`) | **H** | `ERR-LTP-017` |
| `LT-18` | `never_reload` templates require CFO or CTO approval to re-run (`MD-048` `LDX-05`, `SQ-06`) | **A** | `ERR-LTP-018` |
| `LT-19` | A template version must be pinned to the wave loading it | **H** | `ERR-LTP-019` |
| `LT-20` | A mapping workbook below `status = tested` may not drive a load | **H** | `ERR-LTP-020` |
| `LT-21` | Validation runs **in the template** where the tool allows, so the supplier sees the error before submitting | **S** | `WRN-LTP-021` |

> **`LT-21` is the difference between a pack that works and a pack that generates rework.** A
> Warehouse Manager who discovers at submission that 400 rows are wrong has to find and fix them
> without knowing which. Data validation applied inside the issued `.xlsx` catches the same errors at
> the moment of typing.

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `DM-004`…`DM-010` mappings | 1:1 per template | **Before** — the mapping defines the columns |
| [`DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md`](DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) | N:1 | Each template column carries the `dq_rule` that will judge it |
| [`DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md`](DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md) | N:1 | `load_tier` and `load_wave` |
| [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md) | — | **Shared enums and shared `LDX-` rules** — reload policy, masking, sign-off, row count |
| `UI-004` error messages | N:1 | Every rejection is explainable |
| `CG-011` accessibility | N:1 | Print legibility for count sheets |

| Depended on by |
|---|
| Every business owner supplying data · [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) — `row_count_expected` is a reconciliation control · [`DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) — count sheets are cutover artefacts |

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | The `MD` target specifications, through the `DM-004`…`DM-010` mappings |
| Who supplies it | Data Migration issues; business owners fill |
| Collection method | **Derivation** — a template column exists because a mapping row exists. A column with no mapping row is removed, not explained |
| Known quality issues | Templates cannot be final before their mapping reaches `business_confirmed`; six count-sheet variants have physical design constraints that a database-derived template will not meet unless deliberately applied |
| Cleansing rules applied | `DM-011`, cited per column |
| Re-verification | At each wave; a template whose mapping changes is re-issued with a new minor version |

---

## 7. Volumes

| Item | Count |
|---|---:|
| Templates in the pack | **35** |
| of which count sheets | 4 issued, **2 outstanding** (`M45`, `M66` — `DM-001` `O-06`) |
| of which `S3`-bearing and residency-gated | 3 |
| of which `never_reload` | 2 — `MLT-017` opening trial balance, `MLT-029` YTD payroll |
| Business roles who must fill at least one | **13** |
| Sites that will fill a count sheet | **51+** |
| Expected files per wave at W2 | 51 stock sheets + 51 van sheets + 17 brand confirmations ≈ **119** |

> **The pack's real load is the 119 files at W2**, arriving from 51 locations over a short window,
> each of which must be parsed, validated, chased and reconciled. That is a coordination task with a
> named owner, not a mailbox.

---

## 8. Change control

| Item | Value |
|---|---|
| Who may issue a template | Data Migration Lead only |
| Who may change a column | The owning mapping's business owner, through the mapping — **never in the template directly** |
| Approval required | Master Data Owner for a structural change; CFO for `MLT-017`, `-020`, `-032`; HR Director with CFO for `MLT-029` |
| Versioning | Minor for clarification; **major for any column change**, which invalidates files already in flight |
| Effective dating | Not effective-dated; version-pinned to a wave |
| Archive rule | Superseded templates archived with a `SUPERSEDED_` prefix, never deleted (`CP-10`) |
| Logged in | `RF-006`; issued versions and their recipients recorded per wave |

---

## 9. Sample rows

`DM-012_Load_Template_Register.csv`:

```csv
template_id,template_name,target_entity,owning_workbook,load_tier,load_wave,supplier_role,reload_policy,masking_required,row_count_expected,owner_signoff_required,version,active
MLT-002,Party_Individual,fix.party,DM-004,X1,W1,Chief Commercial Officer,upsert,TRUE,100000,TRUE,v1.0,TRUE
MLT-012,Stock_Count_Sheet,fix.stock.quant,DM-007,X6,W2,Warehouse Manager,full_replace,FALSE,,TRUE,v1.0,TRUE
MLT-017,Opening_Trial_Balance,account.move.line,DM-008,X7,W3,CFO,never_reload,FALSE,1,TRUE,v1.0,TRUE
MLT-029,YTD_Payroll_Balance,fix.payroll.balance,DM-009,X8,W5,HR Director with CFO,never_reload,TRUE,500,TRUE,v1.0,TRUE
```

`MLT-002_Party_Individual` — issued header and one worked row:

```csv
source_id,legacy_record_id,row_seq,submitted_by,submitted_on,party_type,display_name_en,display_name_bn,primary_mobile,alt_mobile,email,segment_code,preferred_language,active
SRC-008,MIR-CUST-004182,1,Chief Commercial Officer,2026-11-02,individual,Md Rafiqul Islam,মোঃ রফিকুল ইসলাম,01712345678,,rafiq@example.com,SEG-RETAIL,bn,TRUE
```

`MLT-012_Stock_Count_Sheet` — issued header and one worked row:

```csv
source_id,legacy_record_id,row_seq,submitted_by,submitted_on,location_code,part_code,part_description_as_found,uom_code,counted_qty,condition,owner,counter_1,counter_2,count_datetime
COUNT,MIRPUR-2026-11-14-P0037,37,Warehouse Manager,2026-11-14,BR-MIRPUR-STORE,PRT-004182,LCD panel 15.6 FHD,PCS,37,good,COMPANY,A Karim,S Akter,2026-11-14T21:30:00+06:00
```

---

## 10. Migration notes

**This pack is where BRD `MIG-008` is discharged in content terms.** `MIG-008` requires the
migration tooling to be *"delivered to the Company, repeatable and re-runnable"*. Templates are the
half of that tooling the business touches, and they outlive the migration: the same count-sheet
design becomes the `M15` cycle-count sheet, and the same party template becomes the bulk-onboarding
format for corporate clients.

**Two templates carry `never_reload`** — the opening trial balance and the YTD payroll balance.
They are the two datasets where a re-run is more dangerous than a failure (`SQ-06`, `HP-09`), and
the flag exists so the loader refuses rather than relying on someone remembering.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md) | Shared enums and the `LDX-` rules this pack mirrors for migrated data |
| [`DM-004_Field_Mapping_Workbook_Party_and_Customer.md`](DM-004_Field_Mapping_Workbook_Party_and_Customer.md) | The canonical mapping column set issued as `MLT-000` |
| [`DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md`](DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md) | The count-sheet requirements `LT-05` implements |
| [`DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md`](DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) | The rules each column is judged by |
| [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) | `row_count_expected` as a control total |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | Print legibility for count sheets |
| `UI-004` validation message library | Where every `ERR-LTP-*` must resolve |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Seventeen file conventions, a six-column control block, thirty-five templates, a count-sheet variant designed for the physical act, dual `.xlsx`/`.csv` issue to defeat spreadsheet coercion, and the Bengali completion-guide requirement | Data Migration Lead (pending) |

---

## 13. Open items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **Templates cannot be finalised before their mappings reach `business_confirmed`**, and no mapping has an assigned business owner yet. The pack is specified; it is not issued | Data Migration Lead | **W1** |
| **`O-02`** | **Two count-sheet templates are missing** — `M45` test equipment and `M66` IT assets — because the counts themselves have no owner (`DM-001` `O-06`) | Data Migration Lead with CTO and CFO | **W5 minus 3 months** |
| **`O-03`** | **The `ERR-LTP-*` and every other migration `ERR-*` family must be registered in `UI-004`.** `DM-011` `O-07` carries the same item for the `DQ` families | Content Design with Data Migration | **W1** |
| **`O-04`** | **`CG-010` §3.2 makes Category 12 English-only, but six templates are filled in by branch and store staff across 51+ sites.** `LT-06` requires a Bengali completion guide; no `CM` or `TR` file owns it, and both categories are unwritten | Programme Content Lead with Localisation Lead | **W2 — before the count** |
| **`O-05`** | **No file-transfer mechanism is specified.** 119 files arrive at W2 from 51 locations, several carrying `S2` data. Email is the current practice and is not an acceptable channel for `S2` personal data under the PDPA 2026 | CTO with Security Lead | **W2 minus 2 months** |
| **`O-06`** | **In-template validation (`LT-21`) depends on the tooling the business actually has.** If branches receive `.csv` because they lack a spreadsheet tool that supports validation, the whole error-prevention design degrades to a covering note | Data Migration Lead with Branch Operations Lead | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; the template-pack adaptation is **declared**, not silent
- [x] Template register structure defined, with `MD-048`'s enums reused rather than re-invented
- [x] **Seventeen file conventions specified**, each traced to `05-02` `DM-07`/`DM-08`/`DM-09` or to an observed failure mode
- [x] The blank-versus-`NULL` ambiguity closed explicitly (`F-10`, `LT-11`)
- [x] **The spreadsheet leading-zero trap designed around** via dual `.xlsx`/`.csv` issue (`LT-02`, `F-14`)
- [x] Six-column control block defined and bound to `MS-18` and `FR-SRM-088`
- [x] Mapping-workbook structure referenced, not restated (`CP-01`)
- [x] Thirty-five templates inventoried with target, workbook, tier, wave and supplier role
- [x] **Count-sheet variant specified for the physical act**, including the independence rule that expected quantities are never printed beside the count box
- [x] `never_reload` applied to exactly the two datasets where a re-run is worse than a failure
- [x] Accessibility and the Bengali-guide gap raised rather than papered over
- [x] Sample rows included for the register and for two templates, and parse as CSV
- [x] All internal links resolve
- [x] Bengali counterpart — n/a for the file itself, `bilingual: no` per `CG-010` §3.2; **the completion guide gap is `O-04`**
- [ ] **`O-01` pack specified but not issued — mappings have no business owners**
- [ ] **`O-04` six templates have a Bengali-first audience and no Bengali guide**
- [ ] **`O-05` no secure file-transfer mechanism for 119 files carrying personal data**
- [ ] Named approver recorded — **pending Data Migration Lead with Master Data Owner**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
