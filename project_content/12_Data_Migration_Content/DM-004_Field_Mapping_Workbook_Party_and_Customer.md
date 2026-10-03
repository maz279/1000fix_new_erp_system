---
id: DM-004
title: Field Mapping Workbook — Party and Customer
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration with MDM
author: Data Migration analysts with the Master Data Owner
reviewers: [Chief Commercial Officer, Master Data Owner, Legal Counsel, Chief Data Officer, Security Lead, Localisation Lead, QA Lead]
approver: Master Data Owner with Chief Commercial Officer
content_class: C
purpose: >
  Maps every source field in the customer, corporate-account, vendor, seller, rider, partner and
  employee-as-party estate to its target field in the ERP party model, with the transformation rule,
  default value, sensitivity handling and disposition of every field that is not mapped. Customer
  data is the most duplicated, least structured legacy data in the estate and the one users notice
  on day one; a wrong mapping here propagates into every service order, invoice, claim and
  notification the system will ever produce.
traces_to: [M33, M07, M12, M29, M40, M42, MD-013, MD-007, MD-006, MD-014, MD-015, MD-016, MD-017, MD-018, DM-001, DM-002, DM-003, DM-011, DM-012, DM-013]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: DM-004_Field_Mapping_Party_and_Customer.xlsx
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33 §16.4 — 100,000+ customer records, ~2,000 corporate accounts, 100,000+ addresses; the three migration rules (profile before load, no consent inferred, sensitive fields last); AC-13 and AC-14
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md §2 record structure and §2.1 the eleven party roles
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-007_Address_Format_and_Validation_Standard.md §2 — address record structure including computed zone_code and is_verified semantics
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §Data protection — NFR-086 split-residency architecture; NFR-086c masking in non-production; §PDPA table NFR-090 to NFR-093 consent, transparency notice and data-subject rights
    verified: 2026-08-18
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §11.6.2 — MIG-010 legacy identifiers retained on every record, MIG-011 Bengali text conversion and encoding normalisation to UTF-8, MIG-014 residency classification applied at migration, MIG-015 lawful basis and transparency notice for migrated data subjects
    verified: 2026-08-18
    class: P1
  - source: Master data management practice — attribute-level survivorship producing the golden record field by field, with deterministic matching preferred over fuzzy and thresholds set as a documented business risk decision before migration begins
    verified: 2026-08-18
    class: P3
supersedes: none
review_due: 2027-02-18
---

# DM-004 — Field Mapping Workbook: Party and Customer

> Governs `DM-004_Field_Mapping_Party_and_Customer.xlsx`. The markdown governs; the workbook loads.
>
> **Template conformance note.** `CG-009` §3 allocates `TPL_Master_Data_Specification.md` to this
> file and requires mapping workbooks to *"add a source-to-target column set"*. That addition is
> §2.1, and §2.2–§2.8 are the maps themselves. Every template section is retained in order.
>
> **Identifier note (`CG-005` §3.3).** `DM-004` is a **content** identifier. `05-02` `DM-07`
> (modelling standard — monetary fields) and `DM-09` (UTF-8 and `bn_BD` collation) are cited with
> their document prefix.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Party and customer |
| Owning module | `M33` Customer & Party Master Management; `M07` for account assignment |
| Data steward | Master Data Owner, with the Chief Commercial Officer accountable for customer data |
| Golden source | This mapping; the source data is `SRC-008`, `SRC-009`, `SRC-001`, `SRC-003`, `SRC-016` |
| Refresh cadence | Once per wave, plus deltas during the parallel run |
| Environments | Dev · SIT · UAT · Prod — **`S3` fields masked in all non-production (`NFR-086c`)** |
| Content class | C — Operational-critical |
| Effective-dated | no |
| **Build wave** | **W1** *(the register wave — `MS-22`)* |
| **Load wave** | **W1** — `M33` §16.4, `06-01` W1, tier `X1`/`X2` in `DM-003` §4.4 |

**Consequence of absence (`CP-03`).** `M33` §16.4 opens with one sentence: *"Migration is the largest
risk in this module."* The reason is arithmetic. **100,000+ customer records** whose duplicate rate
has never been measured become the `partner_id` on every service order, the bill-to on every
invoice, the recipient of every notification, and the identity a customer authenticates against.
`ASM-03` assumes the source is exportable at **≥ 80% quality** and states plainly that the
assumption is unproven; `00-04` `RSK-014` carries the residual risk at High/High.

Without a declared field map:

| Failure | Consequence |
|---|---|
| Mobile numbers loaded as stored | Excel strips the leading zero from `01712345678`; the **principal identity key** (`MD-013`) is wrong for an unknown share of 100,000 records |
| Bengali names loaded without conversion | Legacy Bengali held in a non-Unicode encoding renders as mojibake; search, matching and every notification break (BRD `MIG-011`) |
| Free-text address loaded into structured fields | `zone_code` cannot compute, dispatch cannot route, and `MD-007` validation rejects at first edit |
| Consent inferred from an existing marketing flag | Direct breach of `M33` §16.4 rule 2 and `MS-20`; unlawful processing at 100,000 scale |
| NID/TIN loaded with the main record | Direct breach of `NFR-086` before the resident store is verified |
| Unmapped fields silently dropped | The business discovers at UAT that a field it relies on daily was never carried, and the source is decommissioned at W2 |

---

## 2. Record structure

The target structure is `MD-013` §2 (`fix.party`) and `MD-007` §2 (`fix.address`). It is **not
restated here** — `CP-01`. What is defined here is the structure of the **mapping**.

### 2.1 Mapping-workbook column set *(the `CG-009` declared addition)*

Every row in `DM-004_Field_Mapping_Party_and_Customer.xlsx` carries these columns. **This is the
canonical definition for all seven mapping workbooks** — `DM-005`…`DM-010` reference it rather than
restate it (`CP-01`), and `DM-012` §2.4 issues it as an authoring template.

| Column | Type | Req | Constraint | Description |
|---|---|:--:|---|---|
| `map_id` | char(11) | ✔ | `PMAP-nnnnnn`, permanent | One row per source field |
| `source_id` | fk | ✔ | → `DM-002` `SRC-nnn` | Which source the field comes from |
| `source_field` | text(120) | ✔ | As it literally appears — column header, form label or field name | **Never normalised** — the analyst must find it |
| `source_type` | text(40) | ✔ | Observed, not assumed | |
| `source_example` | text(200) | ✔ | A real value, masked if `S2`+ | Makes the transform reviewable |
| `target_entity` | text(60) | | `fix.*` model; blank where unmapped | |
| `target_field` | text(60) | | Column in `MD-013` / `MD-007` | |
| `target_type` | text(40) | | From the `MD` specification | |
| `transform_rule` | text(600) | ✔ | Executable description; see §2.3 | **"Direct" is a valid value; blank is not** |
| `default_value` | text(120) | | Applied only when the source is null | |
| `required_at_target` | bool | ✔ | From the `MD` `Req` column | Drives the reject/hold decision |
| `sensitivity` | enum | ✔ | S0 / S1 / S2 / S3 (`05-02` §10) | Drives residency and masking |
| `residency_restricted` | bool | ✔ | `NFR-086` set | `TRUE` defers the field to a later step |
| `dq_rule` | fk | | → `DM-011` rule id | The validation applied before load |
| `unmapped_disposition` | enum | ✔ | See §2.4 | Required when `target_field` is blank |
| `owner` | text(120) | ✔ | The business role that confirms the mapping | |
| `status` | enum | ✔ | proposed / business_confirmed / tested / signed_off | Load blocked below `tested` |

### 2.2 Map A — `fix.party` core

| Source field *(typical)* | `SRC` | Target | Transform | Default | Sens |
|---|---|---|---|---|:--:|
| *(none — generated)* | — | `party_id` | Generated UUID at load | — | S0 |
| `Customer Type` / inferred from presence of a company name | `SRC-008` | `party_type` | `organisation` where `legal_name` or `BIN` present, else `individual`. **Fixed at creation and never changed** (`MD-013`) | `individual` | S0 |
| `Customer Name` | `SRC-008` | `display_name_en` | Trim; collapse internal whitespace; title-case only where the source is upper-case throughout | — | S1 |
| `Customer Name (Bangla)` where present | `SRC-008` | `display_name_bn` | **Encoding conversion to UTF-8 before any other transform** (`05-02` `DM-09`, BRD `MIG-011`). See §2.5 | null | S1 |
| `Company Name` | `SRC-009` | `legal_name` | Organisation only; trim | — | S1 |
| `Mobile` / `Phone` / `Contact No` | `SRC-008` | `primary_mobile` | **§2.3 rule `T-01`** — the single most important transform in this workbook | **Reject** | S2 |
| `Alt Phone` / second number in one cell | `SRC-008` | `alt_mobile` | `T-01`, after splitting multi-value cells on `/`, `,` or `;` | null | S2 |
| `Email` | `SRC-008` | `email` | Lower-case; trim; syntax-validate; **do not verify deliverability at load** | null | S2 |
| `NID` / `NID No` | `SRC-008` | `nid_number` | **`T-08` — deferred step.** `residency_restricted = TRUE` | null | **S3** |
| `BIN` | `SRC-009` | `bin` | Trim; strip separators; organisation only | null | S2 |
| `TIN` | `SRC-009` | `tin` | **`T-08` — deferred step** | null | **S3** |
| *(built from address rows)* | `SRC-008` | `primary_address_id` | FK set after Map C loads | null | S1 |
| `Customer Category` / `Type` free text | `SRC-008` | `segment_code` | **`T-05`** — map to `MD-014` via an agreed value list; unmapped values → default segment **and a review row** | `SEG-RETAIL` *(pending `O-02`)* | S1 |
| *(absent in source)* | — | `preferred_language` | **Default `bn`** — `PS-03` makes Bengali the default; `MD-013` sets `default bn` | `bn` | S0 |
| `Parent Company` | `SRC-009` | `parent_party_id` | **`T-06`** — resolve by name match to a loaded organisation; unresolved → null **and a review row**, never a guess | null | S1 |
| *(computed)* | — | `match_confidence` | **Computed by `DM-011` matching. Never supplied** | — | S0 |
| *(computed)* | — | `golden_record_id` | Set by the merge process only (`DM-011` §survivorship) | null | S0 |
| `Marketing Opt-in` / `SMS OK` / any consent-like flag | `SRC-008` | `consent_state` | **`T-09` — NOT MAPPED.** `M33` §16.4 rule 2 and `MS-20`: **no consent is inferred**. The source flag is carried to the legacy payload for audit and the target loads the "not captured" state | *(not captured)* | S2 |
| `Status` / `Active` | `SRC-008` | `active` | `TRUE` unless the source explicitly marks inactive | `TRUE` | S0 |
| *(control)* | — | `legacy_source_system` | `source_id` (`MS-18`, BRD `MIG-010`) | — | S0 |
| *(control)* | — | `legacy_record_id` | The source row key, verbatim | — | S0 |
| *(control)* | — | `migration_batch_id` | Assigned by `DM-003` tier `X0` | — | S0 |

### 2.3 Transformation rules

| # | Rule | Detail |
|---|---|---|
| **`T-01`** | **Bangladesh mobile normalisation** | Strip spaces, hyphens, brackets and `+`. Accept `8801XXXXXXXXX`, `01XXXXXXXXX`, `1XXXXXXXXX`. **Re-add the leading zero lost to spreadsheet numeric coercion.** Emit `01[3-9]XXXXXXXX` (`MD-013`). Anything else → reject to remediation, never truncate or pad |
| **`T-02`** | Landline and non-mobile numbers | Not a `primary_mobile`. Carried to a contact-point row with `channel = landline`; **never coerced into the identity key** |
| **`T-03`** | Multi-value cells | `01712345678 / 01812345678` splits to primary + alt. A cell with three or more numbers produces one alt and a review row |
| **`T-04`** | Name cleansing | Trim; collapse whitespace; strip honorifics into a separate attribute *(Mr, Mrs, Md., Alhaj, Eng.)*; **never reorder name parts** — Bangladeshi name order is not reliably first/last |
| **`T-05`** | Controlled-value mapping | Every free-text categorical maps through an **agreed value list** signed by the CCO. An unmapped value takes the default **and raises a review row**; it is never invented |
| **`T-06`** | Hierarchy resolution | Parent resolved by exact then normalised name match to an already-loaded organisation. Unresolved stays null with a review row (`MD-015`) |
| **`T-07`** | Role assignment | Roles are additive (`MD-013` §2.1). A source row appearing in the customer file **and** the vendor file yields **one party with two roles**, not two parties. See §2.6 |
| **`T-08`** | **Residency-deferred fields** | `nid_number`, `tin`, `passport_number` load in a **separate later step**, only after the Bangladesh-resident store is live and verified (`NFR-086`, `MS-21`, `SQ-10`). Until then the column is null and the source value stays in the extract, encrypted, unloaded |
| **`T-09`** | **Consent is not migrated** | No source flag maps to `consent_state`. The flag is preserved in the legacy payload for audit only |
| **`T-10`** | Bengali encoding conversion | See §2.5 |
| **`T-11`** | Dates | Source dates are parsed against a **declared** source format per file. Ambiguous `dd/mm` vs `mm/dd` is resolved by profiling, not by the parser's default. Stored UTC, presented `Asia/Dhaka` (`05-02` `DM-08`) |
| **`T-12`** | Money | Any monetary value carries an explicit currency; `BDT` unless the source states otherwise (`05-02` `DM-07`, `MD-039`) |

### 2.4 Unmapped-field disposition

**`PM-05`: every source field has a disposition. A field with no target and no disposition blocks
the workbook from reaching `business_confirmed`.**

| Disposition | Meaning | Example |
|---|---|---|
| `carried_to_legacy_payload` | Retained verbatim in the migration payload, queryable, not in the operational model | The source marketing-consent flag (`T-09`) |
| `carried_to_notes` | Appended to a free-text note on the target record | Branch remarks such as *"pays late, call before delivery"* |
| `carried_to_contact_point` | Becomes a child row rather than a party column | Landlines, second emails, office reception numbers |
| `deferred_to_wave` | Mapped, but loaded in a later wave | `nid_number` (`T-08`); loyalty tier *(W2, `DM-010`)* |
| `dropped_with_reason` | Deliberately not carried; the reason and the approver are recorded | Free-text `"Follow up"` columns with no consistent meaning |
| `escalated` | Neither the analyst nor the owner can decide | A column whose meaning nobody in the business can state |

> **`PM-06`.** `dropped_with_reason` requires the **business owner's** name, not the analyst's. The
> most expensive discovery in a migration is a dropped field that mattered, found after the source
> is decommissioned — and `SRC-008` decommissions at **W2**.

### 2.5 Bengali text — the encoding step nobody plans for

BRD `MIG-011` requires *"Bengali text conversion and encoding normalisation to UTF-8"*, and `05-02`
`DM-09` requires UTF-8 throughout with `bn_BD` collation. **The requirement implies that some source
Bengali is not Unicode**, which is the common position for legacy Bangladeshi office estates where
Bengali was typed in a legacy ASCII-mapped keyboard layout rather than in Unicode.

**Position (provisional under `CG-012` `EV-03`).** The mapping assumes three possible encodings per
source file — UTF-8, a legacy ASCII-mapped Bengali encoding, or mixed — and requires:

| Step | Rule |
|:--:|---|
| 1 | **Detect encoding per file, not per estate.** Fifty-one branch files may carry three encodings |
| 2 | Convert to UTF-8 **before** any trimming, matching or comparison. A match run on mis-decoded text produces confident nonsense |
| 3 | Normalise to a single Unicode normalisation form so that visually identical conjuncts compare equal |
| 4 | **Round-trip sample 200 rows per file to a native reader** before the file is accepted |
| 5 | A file that cannot be decoded confidently is **not loaded**; it goes to remediation |

> **`O-03`.** The actual encoding in use across `SRC-005`…`SRC-013` has not been profiled. This
> position is provisional and must be confirmed at profiling.
> [`BN-004`](../11_Localisation_Bengali/BN-004_Do_Not_Translate_and_Transliteration_Register.md)
> transliteration and
> [`BN-006`](../11_Localisation_Bengali/BN-006_Bengali_Typography_Font_and_Numeral_Standard.md)
> typography **were written on 2026-08-17 and stand at `Draft`, both registered W1** *(enumerated
> 2026-08-18)*. What is still outstanding is narrower and specific to migration: **the
> transliteration register is written for product content, and its applicability to
> matching legacy customer names across scripts has not been confirmed by Localisation.**

### 2.6 Map B — `fix.party.role`

`MD-013` §2.1 defines eleven roles. A party holds one or more; they are additive and time-bounded.

| Source | Role granted | Note |
|---|---|---|
| `SRC-008` customer master | `customer` | The bulk of the 100,000+ |
| `SRC-009` corporate account lists | `corporate_client` + `customer` | ~2,000; also creates the hierarchy in Map D |
| `SRC-013` HR spreadsheets *(W5)* | `employee` | Employee parties are created at W1 for branch and technician records, and completed at W5 by `DM-009` |
| `SRC-016` vendor and supplier lists *(W3)* | `vendor` | **See §2.8 — vendors are parties and are mapped here, not in a separate workbook** |
| Sub-contractor list *(W7)* | `seller` | **`Registered` state only.** `M12` §16.4: no existing sub-contractor is migrated as an Approved seller |
| Rider master *(W3)* | `rider` | 50–150 |
| Courier partner contracts *(W3)* | `courier_partner` | 3–5 |
| Brand authorisation documents *(W4)* | `brand_partner` | 17+; the party, not the agreement (`DM-010` owns the agreement) |
| Informal referral arrangements *(W7)* | `referral_partner` | `Prospect` state; full onboarding required |
| Recycling partner list *(W8)* | `recycling_partner` | Certification re-verified, not carried |

> **`PM-07`.** A party appearing in two source estates is **one party with two roles** (`T-07`).
> Loading it twice creates a duplicate that `DM-011` will then have to merge, and merging a party
> that has already transacted under both identities is materially harder than not splitting it.
> `MD-013` §2.1 notes that an `employee` + `seller` combination is a segregation-of-duties question
> for `SP-006`, **not a data error** — the load must not suppress it.

### 2.7 Map C — `fix.address`

| Source field *(typical)* | Target | Transform | Note |
|---|---|---|---|
| *(generated)* | `address_id` | UUID | |
| — | `party_id` | FK from Map A | |
| `Address Type` free text | `address_label` | `T-05` against Home / Office / Site / Other | Customer-tagged in `P01` |
| `Division` | `division_code` | `T-05` → `MD-006` `geo_code`, **including alternate names** — Chittagong/Chattogram, Jessore/Jashore, Comilla/Cumilla | `MD-006` carries `alt_names_en` for exactly this |
| `District` | `district_code` | `T-05` → `MD-006` | |
| `Thana` / `Upazila` / `PS` | `upazila_code` | `T-05` → `MD-006`; **`PS` (police station) commonly means thana** | Highest failure rate in the address map |
| `Post Code` | `postcode` | 4 digits; strip text | |
| `Area` / `Locality` | `area_name` | Trim | Required at target |
| `Road` / `Block` / `Sector` | `road_or_block` | Trim | |
| `House` / `Holding` | `house_or_holding` | Trim | |
| `Flat` / `Floor` | `floor_flat` | Trim | |
| `Landmark` / `Beside` / `Near` | `landmark` | Trim | **Load-bearing in Bangladesh** (`MD-007`) — never dropped |
| Single free-text address blob | `free_text_bn` | Carried **verbatim** after encoding conversion | **`PM-08`** — see below |
| — | `zone_code` | **Not supplied. Computed** from geometry (`SQ-04`) | |
| — | `is_verified` | **`FALSE` for every migrated address.** `MD-007`: set `TRUE` only by a completed delivery | No migrated address is verified |
| — | `latitude` / `longitude` / `gps_*` | Null unless the source genuinely holds a captured coordinate | `gps_source` never set to `device` on migration |

> **`PM-08` — the free-text address rule.** Where the source holds one unstructured address string,
> it is loaded **verbatim into `free_text_bn` and parsed on a best-effort basis into the structured
> fields**. Both are kept. Parsing without keeping the original destroys the only evidence of what
> the customer actually wrote, and Bangladeshi addressing is not reliably parseable — the landmark
> often carries more delivery value than the road.

### 2.8 Map D — hierarchy, profile and contact points

| Target | Source | Rule |
|---|---|---|
| `fix.party.hierarchy` | `SRC-009` corporate lists | Group → company → division → site (`05-02` §2). Unresolvable levels are left flat with a review row, never invented (`MD-015`) |
| `fix.customer.profile` | `SRC-008`, `SRC-001` | Preferences, channel, acquisition source where genuinely present; **not inferred** |
| `fix.contact.point` | `SRC-008` overflow columns | Landlines, second emails, office numbers (`T-02`) |
| `fix.credit.profile` | `SRC-010`, `SRC-016` | Corporate and contract accounts only; terms and limits from `M20` §16.4 *(W3, `DM-008`)* |
| `fix.identity.document` | `SRC-008`, `SRC-030` | **Deferred step `T-08`**; `S3`; encrypted; access-logged |
| `fix.consent.record` | — | **No rows are created by migration** (`T-09`, `MS-20`) |
| Account assignment (`M07`) | `SRC-009` | Account manager per corporate party; role resolved against `MD-009` |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | **`primary_mobile`** — `MD-013` calls it *"the principal identity key"*. This is why `T-01` is the highest-risk transform in the workbook |
| Surrogate key | `party_id` UUID, generated at load, permanent |
| Legacy key | `legacy_source_system` + `legacy_record_id`, immutable, indexed — `FR-SRM-088` requires lookup by original reference |
| Code format | No human-readable party code; parties are found by mobile, name or legacy reference |
| Reuse policy | A `party_id` is never reused. A merged loser retains its id and points to the survivor through `golden_record_id` (`MD-013`) |
| Collision policy | Two source rows resolving to the same `primary_mobile` are a **match candidate**, not an error. `DM-011` decides |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `PM-01` | A source field with no `transform_rule` blocks the workbook from `business_confirmed` | **H** | `ERR-PMP-001` |
| `PM-02` | A row whose `primary_mobile` fails `T-01` is rejected to remediation; it is never truncated, padded or defaulted | **H** | `ERR-PMP-002` |
| `PM-03` | A row with no usable `primary_mobile` **and** no email loads only to the archive area, flagged (`MS-10`) | **A** | `ERR-PMP-003` |
| `PM-04` | `consent_state` may not be populated from any source field (`MS-20`, `M33` `AC-14`) | **H** | `ERR-PMP-004` |
| `PM-05` | Every source field carries a disposition (§2.4) | **H** | `ERR-PMP-005` |
| `PM-06` | `dropped_with_reason` requires the business owner's recorded name | **H** | `ERR-PMP-006` |
| `PM-07` | One party per real-world entity; a second role is added, not a second party | **H** | `ERR-PMP-007` |
| `PM-08` | A free-text address is preserved verbatim as well as parsed | **H** | `ERR-PMP-008` |
| `PM-09` | `zone_code`, `match_confidence` and `golden_record_id` may not be supplied by the load (`SQ-04`) | **H** | `ERR-PMP-009` |
| `PM-10` | `is_verified` is `FALSE` on every migrated address | **H** | `ERR-PMP-010` |
| `PM-11` | `residency_restricted` fields may not load before the resident store is verified (`NFR-086`, `MS-21`) | **H** | `ERR-PMP-011` |
| `PM-12` | Non-production loads are masked on every `S2` and `S3` field (`NFR-086c`) | **H** | `ERR-PMP-012` |
| `PM-13` | Bengali text loads only from a file whose encoding was detected, converted and sample-verified (§2.5) | **H** | `ERR-PMP-013` |
| `PM-14` | `preferred_language` defaults to `bn`, never to `en` (`PS-03`, `MD-013`) | **S** | `WRN-PMP-014` |
| `PM-15` | An unmapped controlled value takes the default **and** raises a review row; it is never invented (`T-05`) | **C** | `WRN-PMP-015` |
| `PM-16` | Profiling must be `reported` and accepted by the CCO before any load (`MS-04`, `M33` rule 1) | **H** | `ERR-PMP-016` |
| `PM-17` | Every loaded row carries the three control values (`MS-18`) | **H** | `ERR-PMP-017` |
| `PM-18` | A seller-role party loads in `Registered` state only (`M12` §16.4) | **H** | `ERR-PMP-018` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `MD-006` geography | N:1 | Seed tier 0 — **before** Map C |
| `MD-002` entity, `MD-003` branch, `MD-005` zone | N:1 | Seed tiers 1–2 — zone before address computation |
| `MD-014` segment, `MD-015` hierarchy standard | N:1 | Seed tier 6 |
| `MD-007` address standard | 1:N | Governs Map C |
| `DM-002` source register | N:1 | Profiling accepted before load (`PM-16`) |
| `DM-011` quality rules | N:1 | Matching and survivorship run **after** Map A stages, **before** commit |

| Depended on by |
|---|
| `DM-005` device ownership · `DM-006` service order `partner_id` · `DM-008` AR open items · `DM-010` contract holder and warranty registrant · `DM-009` employee-party linkage · every notification, invoice and portal identity |

> Load order for migrated entities is consolidated in `DM-003` §4.4; seed order in `MD-048`. Update
> together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | `SRC-008` customer spreadsheets · `SRC-009` corporate account lists · `SRC-001`/`SRC-002` legacy tracking applications · `SRC-003` website submissions · `SRC-016` vendor lists · `SRC-047` portal accounts |
| Who supplies it | Chief Commercial Officer for customer and corporate; Procurement Manager for vendor; Security Lead for portal identities |
| Collection method | Spreadsheet collection plus database extract; **profiling before any load** (`M33` rule 1) |
| Known quality issues | Duplicate rate **unmeasured**; `ASM-03`'s ≥ 80% quality assumption **unproven**; mobile numbers coerced to numeric by spreadsheet software; Bengali encoding unknown; address held as free text; corporate hierarchy implicit in people's heads |
| Cleansing rules applied | `DM-011` |
| Re-verification | At profiling, and again on the delta extract before cutover |

---

## 7. Volumes

| Population | Rows | Source | Wave |
|---|---:|---|:--:|
| Individual customers | **100,000+** | `SRC-008` | W1 |
| Addresses | **100,000+** | `SRC-008` | W1 |
| Corporate accounts | ~2,000 | `SRC-009` | W1 |
| Customer portal identities | **250,000+** | `SRC-047` | W2 |
| Internal user accounts | 150–250 | `SRC-046` | W1 |
| Technicians | 200–400 | `SRC-005`, HR | W2 |
| Vendors and suppliers | 40–120 active; 200–400 historical | `SRC-016` | W3 |
| Riders | 50–150 | Rider master | W3 |
| Courier partners | 3–5 | `SRC-025` | W3 |
| Brand partners | 17+ | `SRC-019` | W4 |
| Sellers *(Registered only)* | 50–150 | Sub-contractor list | W7 |
| **DND registry** | **250,000+ numbers** | `M27` §16.4 | W4 |

> **The DND registry is 250,000+ rows and is not a party attribute.** It loads to `fix.dnd.registry`
> and is refreshed thereafter. It is listed here because it is the only party-adjacent dataset whose
> volume exceeds the party master itself, and it is easily missed.

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add a mapping row | Migration analyst |
| Who may set `business_confirmed` | The named business owner in the `owner` column — **CCO for customer fields** |
| Who may set `signed_off` | Master Data Owner with the Chief Commercial Officer |
| Approval required | CCO for any `dropped_with_reason`; Legal Counsel for any change touching `consent_state` or `S3` fields |
| Effective dating | Not effective-dated; the workbook is versioned per wave |
| Archive rule | Superseded mapping versions are archived, never deleted (`CP-10`, `05-02` `DM-06`) |
| Logged in | `RF-006` for any disposition change; `DM-013` records what actually loaded |

---

## 9. Sample rows

```csv
map_id,source_id,source_field,source_type,source_example,target_entity,target_field,transform_rule,default_value,required_at_target,sensitivity,residency_restricted,dq_rule,unmapped_disposition,owner,status
PMAP-000101,SRC-008,Mobile,text,1712345678,fix.party,primary_mobile,T-01 BD mobile normalisation; re-add lost leading zero; emit 01[3-9]XXXXXXXX,,TRUE,S2,FALSE,DQ-PARTY-004,,Chief Commercial Officer,proposed
PMAP-000107,SRC-008,Customer Name (Bangla),text,<bengali>,fix.party,display_name_bn,T-10 encoding detect and convert to UTF-8 then normalise,,FALSE,S1,FALSE,DQ-PARTY-011,,Localisation Lead,proposed
PMAP-000114,SRC-008,SMS OK,boolean,Y,,,T-09 consent is never inferred; source flag retained for audit only,,FALSE,S2,FALSE,,carried_to_legacy_payload,Legal Counsel,proposed
PMAP-000121,SRC-008,NID No,text,MASKED,fix.identity.document,nid_number,T-08 deferred to the resident-store step; not loaded at W1,,FALSE,S3,TRUE,DQ-PARTY-021,deferred_to_wave,Chief Data Officer,proposed
PMAP-000140,SRC-008,Address,text,"House 12, Road 4, Shewrapara, near Rupali Bank, Mirpur, Dhaka",fix.address,free_text_bn,PM-08 preserve verbatim and parse best-effort into structured fields,,FALSE,S2,FALSE,DQ-ADDR-002,,Chief Commercial Officer,proposed
PMAP-000155,SRC-008,Follow up,text,call later,,,No consistent meaning across branches; not carried,,FALSE,S1,FALSE,,dropped_with_reason,Chief Commercial Officer,proposed
```

---

## 10. Migration notes

**This workbook is the entry point of the entire migration.** Tier `X1` in `DM-003` §4.3 has no
predecessor other than seed data, and eight later tiers hold a foreign key into it.

Three `M33` acceptance criteria are discharged here and nowhere else:

| Criterion | How this workbook discharges it |
|---|---|
| `AC-13` — migration reconciles: source count, loaded count, rejected count and duplicate count all accounted for, **signed by the CCO** | §2.1 `status` gate + `DM-013` reconciliation classes |
| `AC-14` — **no migrated party carries an inferred consent record** | `T-09`, `PM-04` |
| `G1-05` — customer and device data migrated and reconciled, **evidence: signed reconciliation** | With `DM-005` and `DM-013` |

**The lawful basis for the processing itself is not settled here and cannot be.** BRD `MIG-015`
requires a recorded lawful basis and transparency-notice treatment for migrated data subjects;
`05-06` §PDPA `NFR-092` requires the notice before or during processing.
[`LG-008`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md) exists at
`Draft` but is **registered at W2, one wave after the processing it must cover**, and it is consent
copy rather than a lawful-basis determination for a bulk migration. This is `DM-001` `O-03` and is
repeated as `O-01` below because it blocks this file specifically.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md) | The target record structure and the eleven roles |
| [`../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-007_Address_Format_and_Validation_Standard.md`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-007_Address_Format_and_Validation_Standard.md) | The address target and the computed `zone_code` |
| [`../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-006_Bangladesh_Geographic_Hierarchy.md`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-006_Bangladesh_Geographic_Hierarchy.md) | `alt_names_en` — the alternate district names `T-05` depends on |
| [`DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md`](DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) | Matching, survivorship and the thresholds that decide merges |
| [`DM-012_Migration_Load_Template_Pack.md`](DM-012_Migration_Load_Template_Pack.md) | The file the business fills in from this mapping |
| [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) | The report the CCO signs |
| `M33` §16.4 · `M07` §16.4 · `M29` §16.4 | The migration positions this workbook implements |
| [`../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md) | Written 2026-08-17, `Draft`, **W2 — one wave after the W1 processing** (`O-01`) |
| [`../11_Localisation_Bengali/BN-004_Do_Not_Translate_and_Transliteration_Register.md`](../11_Localisation_Bengali/BN-004_Do_Not_Translate_and_Transliteration_Register.md) · [`../11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md`](../11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md) | Written 2026-08-17, `Draft`, W1 — applicability to cross-script **matching** unconfirmed (`O-03`) |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Four maps, twelve transformation rules, six unmapped dispositions, eighteen validation rules; consent explicitly excluded from mapping; residency fields deferred to a separate step | Master Data Owner (pending) |

---

## 13. Open items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **No lawful basis is recorded for the 100,000+ data subjects processed at W1, and the transparency notice arrives a wave late.** BRD `MIG-015` and `05-06` §PDPA `NFR-092` both require a notice before or during processing; `LG-008` exists at `Draft` but is registered **W2**. `AUDIT-010` HC-01 raised the same class of question for W2 transcript mining and remains open | Legal Counsel with Chief Data Officer | **W1 — before the first party load** |
| **`O-02`** | **The segment value list does not exist.** `T-05` maps free-text customer categories to `MD-014` segments; the agreed value list and the default segment are unconfirmed, and a wrong default silently mis-tiers 100,000 customers | Chief Commercial Officer with Master Data Owner | **W1 minus 1 month** |
| **`O-03`** | **Source Bengali encoding is unprofiled.** `BN-004` transliteration and `BN-006` typography exist at `Draft` (written 2026-08-17, W1), but neither was authored for **record matching**, and Localisation has not confirmed that the transliteration rules are usable as a cross-script comparison basis for 100,000 legacy names | Localisation Lead with Data Migration | **W1 — before matching** |
| **`O-04`** | **The resident store is unproven.** `ASM-21` is not proven and decision `D-13` blocks the W1 architecture. If the store is unavailable at W1, `T-08` defers `nid`, `tin` and `passport` indefinitely and a second identity pass must be planned and funded | CTO with Legal Counsel | **W1** |
| **`O-05`** | **Vendor and supplier parties are mapped here** (§2.6, §2.8) although the file is titled *Party and Customer* and the register describes it as customer-focused. The alternative reading — that vendors have no workbook — would leave `M16`, `M42` and `M52` without a party mapping. The register row should be clarified | Programme Content Lead | W3 |
| **`O-06`** | Corporate hierarchy exists only in account managers' knowledge (`SRC-009`, `SRC-040`). `T-06` will leave an unknown share unresolved, and `MD-015` hierarchy-dependent pricing and consolidated invoicing degrade silently for those accounts | Chief Commercial Officer | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; the `CG-009` source-to-target column set added as §2.1 and **declared**
- [x] Target structure referenced, not restated (`CP-01`)
- [x] Every mapped field carries a transform rule; "Direct" permitted, blank prohibited (`PM-01`)
- [x] Bangladesh mobile normalisation specified as the highest-risk transform, including the lost-leading-zero case
- [x] **Consent explicitly excluded from mapping**, discharging `M33` `AC-14` and `MS-20`
- [x] **Residency-restricted fields deferred to a separate gated step** (`NFR-086`, `T-08`)
- [x] Bengali encoding conversion made a precondition of matching, with the position marked provisional under `EV-03`
- [x] Free-text address preserved verbatim as well as parsed (`PM-08`)
- [x] Computed fields prohibited from being supplied (`PM-09`)
- [x] Every source field given one of six dispositions; `dropped_with_reason` requires the business owner
- [x] One party per real-world entity across eleven roles (`PM-07`)
- [x] Volumes stated per population, including the 250,000+ DND registry that is easily missed
- [x] Sample rows included and parse as CSV
- [x] Archive rule states records are archived, never deleted (`05-02` `DM-06`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] **`O-01` no lawful-basis confirmation or transparency notice for 100,000+ migrated data subjects**
- [ ] **`O-03` source Bengali encoding unprofiled; `BN-004` applicability to matching unconfirmed**
- [ ] Named approver recorded — **pending Master Data Owner with CCO**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
