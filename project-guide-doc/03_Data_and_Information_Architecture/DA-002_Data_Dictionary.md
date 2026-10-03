---
id: DA-002
title: Data Dictionary
category: 03 — Data & Information Architecture
code: DA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Data Architect
approver: Chief Data Officer (unappointed — see DA-003)
standards_basis: >
  ISO/IEC 11179-1:2023 · ISO/IEC 11179-6:2023 (registration) · ISO/IEC 11179-31:2023 ·
  DAMA-DMBOK 2.0 (2024 maintenance revision) · ISO/IEC 25012 (data quality model)
traces_to: >
  PGD-000 DA-002 · audit F3 (critical, AUDIT-013 LG-01) · DA-001 (structure) ·
  DA-005 (classification) · SC-003 (DPIA) · SC-007 (residency) · DM-004…DM-010
depends_on: DA-001 · DA-005 · AR-008 · BE-005
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 14:30 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# DA-002 — Data Dictionary

### Category 03 · Code `DA` · ISO/IEC 11179-1:2023 · ISO/IEC 11179-6:2023 registration

---

> **`DA-002` is a registry, not a document.** There are **5,301 distinct field names across 11,622
> declared attributes in 1,335 tables**. A single markdown file listing them would be unreadable,
> unmaintainable and stale within a wave.
>
> This document establishes: **(a)** the mandatory metadata every data element carries, **(b)** the
> registration procedure and its authority, **(c)** the generation rule that keeps the registry true,
> **(d)** the reconciliation checks that make the `F3` class of defect impossible, and **(e)** one
> **fully worked exemplar** so that "registered in `DA-002`" has a referent.

---

## 1. Purpose

A data dictionary is not documentation. It is the artefact that makes **"does this field exist?"** a
query rather than an argument.

The estate already knows what happens without one. Audit **`F3` / `LG-01` (critical, `AUDIT-013`)**
found that `DT-031` — the SLA annex printed to corporate customers — maps **nine `MD-028` fields, and
none of the nine exists**:

| `DT-031` references | Reality in `MD-028` |
|---|---|
| `MD-028.priority_code` | The field is `sla_band_code` |
| `MD-028.priority_name_en` / `_bn` | The fields are `band_name_en` / `band_name_bn` |
| `MD-028.response_target` | The field is `response_target_min` |
| `MD-028.resolution_target` | The field is `resolution_target_min` |
| `MD-028.coverage_window` | The fields are `clock_runs` and `business_calendar_code` |
| **`MD-028.definition`** | **No such field** |
| **`MD-028.measurement_basis`** | **No such field** |
| **`MD-028.clock_start_event`** | **No such field** |
| **`MD-028.clock_stop_event`** | **No such field** |

`DT-031` `FM-31-a` states that every value in its commitments table is *"read from `MD-028`, not
entered"*. **Two of the missing fields are substantive**: `MD-028` has **no clock start or stop event
field at all**, while `DT-031` §1.1 names *when the clock starts and stops* as one of the four
ambiguities *"every SLA dispute the company will ever have"* is about.

**A build to `DT-031` would be a build against a schema that does not exist.** That is what a data
dictionary prevents, and it is why `DA-002` is P0.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The measured data-element population |
| 2 | **The mandatory metadata set** — 24 attributes per data element |
| 3 | The registration procedure, authority and lifecycle (ISO/IEC 11179-6) |
| 4 | **The generation rule** — what is derived from code, what is authored, and why |
| 5 | Naming reconciliation across the 4,020 singleton field names |
| 6 | **The four reconciliation checks** that close the `F3` class |
| 7 | The PII and PDPA sensitivity flags that `SC-003` and `SC-007` consume |
| 8 | A worked exemplar — `fix_service_order` and `MD-028` |
| 9 | Coverage measurement and the production schedule |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Table structure, types, constraints, indexes | `DA-001` | Structure there; meaning here |
| The classification scheme itself | `DA-005` | This registry carries the class; `DA-005` defines it |
| Code list values | `DA-009` | This registry names the code list; `DA-009` holds its members |
| Warehouse field semantics | `DA-007`, `RP-006` | `RP-006` §4.2 already registers 16 attributes per certified dataset |
| Business glossary terms | `RR-001` | A term is not a field |
| Retention periods | `DA-006`, `LG-009` | Referenced, not restated |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Developers** | The answer to "does this field exist, and what does it mean" |
| **`SC-003` DPIA author** | §8 — the PII and sensitivity flags are the DPIA's input, and it cannot be written from opinion |
| **`SC-007` residency design** | §8.3 residency classification per field |
| Migration team | `DM-004`…`DM-010` map source fields to targets that must be registered first |
| Content authors (`DT-*`, `MD-*`) | §7's check `RC-2` is what stops the next `F3` |
| QA | Valid-value sets are directly testable |
| Data stewards (`DA-003`) | The artefact they steward |

---

## 2. Basis and Measurement

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **ISO/IEC 11179-1:2023** (Edition 4) | §3's metadata set follows the data-element / data-element-concept / value-domain structure | Full at the conceptual level |
| **ISO/IEC 11179-6:2023** Registration | §4 registration statuses, authority and lifecycle | **Departure:** the standard's six registration statuses are reduced to four (§4.2). Rationale: `Preferred`/`Superseded`/`Retired` distinctions add ceremony a 5,301-element registry built in nine waves cannot sustain. Stated rather than silently omitted |
| **ISO/IEC 11179-31:2023** | Data-element metamodel informs §3's attribute set | The metamodel is not instantiated as a database schema; the registry is generated (§5) |
| **DAMA-DMBOK 2.0** (2024 maintenance revision) | Metadata management knowledge area | DMBOK 3.0 is in development, **not released** (verified 2026-08-18) |
| **ISO/IEC 25012** | Data quality characteristics referenced in the quality-rule attribute | Full quality model is `DA-008`'s |

### 2.2 The measured population

Counted at **2026-08-18 14:30 (+06)**; method in `DA-001` §15.

| Measure | Count |
|---|---:|
| Tables to document | **1,335** |
| Declared attribute mentions | **11,622** |
| **Distinct field names** | **5,301** |
| Field names appearing exactly once | **4,020** (76%) |
| Field names in ≥ 100 entities | **5** — `state`, `code`, `name`, `approved_by`, `entity_id` |
| **Estimated total data elements** *(11,622 declared + the standard column contract across 1,335 tables)* | **~17,000–19,000** |
| Fields currently registered anywhere | **0** |

> **The estimate is stated as a range and labelled.** The declared 11,622 is a summary, not a column
> list (`DA-001` §2.4); adding `DA-001` §3's contract — five Tier-1 columns universally, three Tier-2,
> three Tier-3 on transactional tables — gives the range. **It is an order-of-magnitude figure for
> planning, not a contractual count**, and it is stated because an unstated estimate of that size is a
> worse error than an imprecise one (the `PGD-A1-05` lesson).

### 2.3 Findings this document raises

| ID | Finding |
|---|---|
| **`PGD-A5-04`** | **`DA-002` is a ~17,000–19,000-element registry, recorded in `PGD-000` as one ⛔ row.** Its effort is in neither `GV-004` nor `CO-005`. **Fifth extension of `PGD-A1-05`** |
| **`PGD-A5-05`** | **4,020 of 5,301 field names (76%) appear in exactly one entity.** Some is genuine domain specificity; some is 67 authors naming the same concept differently. §6 is the reconciliation, and it cannot be done by inspection |

### 2.4 Source material

| Source | Contribution |
|---|---|
| All 67 module specifications §10.1 | The 11,622 declared attributes |
| `./DA-001_*.md` §3, §4 | Structure, types and the standard column contract |
| `../../project_content/_AUDIT/AUDIT-013_Category_10_LG_Content_Audit.md` `LG-01` | **The `F3` finding** — the motivating defect |
| `../../project_content/02_Master_Data_and_Configuration/` — 48 `MD-*` files §2 "Record structure" | **48 already-authored field-level record structures**, the best existing input |
| `../../project_content/14_Reporting_Analytics_and_KPI/RP-006_BI_Semantic_Layer_Data_Dictionary.md` §4.2 | The 16-attribute dataset schema — the warehouse-side precedent |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §10 | Classification S0–S3 |

> **The 48 `MD-*` files are a genuine asset and should be credited.** Each carries a §2 "Record
> structure" table with column, type, required flag, constraint, Bengali flag and description — which
> is **six of this document's 24 attributes, already authored, for the master-data domains**. `DA-002`
> ingests them rather than re-authoring them (§5.3).

---

## 3. The Mandatory Metadata Set

**Twenty-four attributes per data element.** A registration missing a mandatory attribute is
incomplete and cannot reach `Registered` status.

### 3.1 Identity and structure

| # | Attribute | Mandatory | Source | Notes |
|---:|---|:--:|---|---|
| 1 | `element_id` | ✔ | Generated | `DE-<table>-<column>`, permanent |
| 2 | `table_name` | ✔ | Code | Physical table |
| 3 | `column_name` | ✔ | Code | Physical column |
| 4 | `odoo_model` / `odoo_field` | ✔ | Code | The ORM-level name |
| 5 | `data_type` | ✔ | Code | `DA-001` §4.2 domain |
| 6 | `length_precision` | ✔ | Code | `varchar(n)`, `numeric(16,2)` |
| 7 | `nullable` | ✔ | Code | |
| 8 | `default_value` | — | Code | |

### 3.2 Meaning

| # | Attribute | Mandatory | Source | Notes |
|---:|---|:--:|---|---|
| 9 | `business_name` | ✔ | **Authored** | The name a business user says |
| 10 | `business_name_bn` | ✔ where user-facing | **Authored** | Bengali counterpart (`AS-12`) |
| 11 | **`definition`** | ✔ | **Authored** | **One sentence stating what the value *is*.** The most-read attribute |
| 12 | `data_element_concept` | ✔ | **Authored** | ISO/IEC 11179 object-class + property — e.g. *service order · promised completion* |
| 13 | `unit_of_measure` | ✔ where numeric | Authored | Minutes, BDT, kg, percent-as-fraction |
| 14 | `example_value` | ✔ | Authored | A real, non-personal example |

> **Attribute 11 is the one `MD-028` did not have**, and its absence is half of finding `F3`. A field
> with a name and a type and no definition is a field two people will use differently.

### 3.3 Values and rules

| # | Attribute | Mandatory | Source | Notes |
|---:|---|:--:|---|---|
| 15 | `value_domain` | ✔ | Code + `DA-009` | Free / range / **code list `CL-nnn`** / FK target |
| 16 | `valid_values` | ✔ where enumerated | **`DA-009`** — referenced, never copied | A copied enumeration diverges |
| 17 | `validation_rules` | ✔ | Code + `05-05` | Check constraints and `BRU-*` rules acting on it |
| 18 | `quality_rules` | — | `DA-008` | The `DI-06` tests, where any |

### 3.4 Governance and protection

| # | Attribute | Mandatory | Source | Notes |
|---:|---|:--:|---|---|
| 19 | `owning_module` | ✔ | `AR-005` | The single owner (`Mnn`) |
| 20 | `data_owner` / `data_steward` | ✔ | **`DA-003`** | Role, never a person |
| 21 | **`classification`** | ✔ | **`DA-005`** | `S0` · `S1` · `S2` · `S3` |
| 22 | **`is_personal_data`** + `pdpa_category` | ✔ | **`DA-005`** | The **DPIA input**. Ordinary / sensitive / restricted |
| 23 | **`residency_class`** | ✔ | **`DA-005`, `SC-007`** | `none` · `resident` — and see `DA-001` §10.4 |
| 24 | `retention_class` | ✔ | **`LG-009`** — referenced | `RC-01`…`RC-27` |

### 3.5 Why 24 and not 12

Attributes 21–24 are the four the estate cannot currently answer, and they are the four with legal
consequence:

| Question a regulator asks | Answered by | Currently answerable? |
|---|---|---|
| *What personal data do you hold?* | 22 across 17,000+ elements | **No** |
| *Which of it is sensitive?* | 22 `pdpa_category` | **No** |
| *Where does it live?* | 23 | **Only for the 7 fields in `05-06` §6.4** |
| *How long do you keep it?* | 24 → `LG-009` | Policy exists; **the field-level mapping does not** |

> **`SC-003` (DPIA) and `SC-007` (residency) are both P0 and both blocked on attribute 22 and 23.**
> A DPIA written without a field-level personal-data inventory is a DPIA written from opinion, and
> PDPA enforcement activates around **13 May 2027 — inside Wave 4**.

---

## 4. Registration

### 4.1 Authority

| Role | Authority |
|---|---|
| **Registration Authority** | **Data Architect** — accepts a registration as complete |
| **Submitting Organisation** | The owning module's squad |
| **Steward** | Per `DA-003` §3 domain assignment |
| **Approver for `S3` / personal / resident** | **Chief Data Officer** — unappointed (`DA-003` `PGD-A5-07`) |

### 4.2 Registration status (ISO/IEC 11179-6, reduced to four)

| Status | Meaning | Gate |
|---|---|---|
| **`Candidate`** | Exists in code; metadata incomplete | Generated automatically (§5) |
| **`Registered`** | All 24 mandatory attributes present | Attributes 9–14 authored; 19–24 assigned |
| **`Superseded`** | Replaced; the successor is named | A successor `element_id` |
| **`Retired`** | No longer in the schema | **Never deleted** — a retired element is how an old report is still explicable |

> **A `Candidate` element may be built against; it may not be *published* in a `DT-*` template, an
> API contract or a report.** That single rule is what would have caught `F3`.

### 4.3 The lifecycle rules

| # | Rule |
|---|---|
| **RG-01** | **A column may not be added to the schema without a `Candidate` registration.** Generation makes this automatic (§5) |
| **RG-02** | A column may not reach production without `Registered` status |
| **RG-03** | `element_id` is **permanent**. A renamed column is a new element plus a `Superseded` link |
| **RG-04** | Changing attribute 11 (`definition`) is a **change, not a correction** — consumers are notified |
| **RG-05** | Changing 21, 22 or 23 requires **CDO approval** and triggers re-assessment in `SC-003` |
| **RG-06** | A retired element is retained permanently (§4.2) |

---

## 5. Generation — the Rule That Keeps the Registry True

### 5.1 The problem with a hand-maintained dictionary

A 17,000-element dictionary maintained by hand diverges from the schema within one wave. The estate
has already proved this at 1/60th the scale: `MD-028` has 20-odd fields and `DT-031` was wrong about
nine of them.

### 5.2 What is generated and what is authored

| Attributes | Source | Mechanism |
|---|---|---|
| **1–8** structure | **Generated from the Odoo model registry and PostgreSQL catalogue** | CI job, every build |
| **15, 17** value domain and validation | **Generated** from field definitions, constraints and `05-05` rules | CI job |
| **19** owning module | **Generated** from the module that declares the model | CI job |
| **9–14** meaning | **Authored** — a machine cannot write a definition | Registry UI / PR |
| **20–24** governance and protection | **Authored / assigned** | Steward + CDO |

> **The split is the design.** Roughly **60% of each entry is generated and cannot drift**; the
> remaining 40% is human judgement that a machine cannot supply. A dictionary that generates nothing
> is stale; one that generates everything is meaningless.

### 5.3 Ingesting the 48 `MD-*` record structures

Each `MD-*` file's §2 carries `Column | Type | Req | Constraint | BN | Description`. That is
attributes **3, 5, 7, 17, 10 and 11** already authored for the master-data domains.

| # | Rule |
|---|---|
| **IN-01** | The 48 §2 tables are **ingested as authored input**, not re-keyed |
| **IN-02** | Where an `MD-*` §2 row and the generated schema disagree, **the schema wins and a finding is raised against the `MD-*` file** — this is exactly the `F3` shape, detected automatically |
| **IN-03** | The `MD-*` file remains the **content** authority (valid values, sample rows); `DA-002` becomes the **structural** authority |

### 5.4 Publication

| Surface | Content |
|---|---|
| Developer portal | Searchable registry, filtered by module, table, classification |
| **Generated markdown per module** | Committed alongside the module, so a developer reads it in the repository |
| **PII / residency extract** | The `SC-003` and `SC-007` input — attributes 21–23 across all elements |
| **Retention extract** | The `DA-006` input — attribute 24 joined to `LG-009` |
| API | Machine-readable, for `IN-002` contract generation and `DA-007` lineage |

---

## 6. Naming Reconciliation

> **`PGD-A5-05` — 4,020 of 5,301 field names (76%) appear in exactly one entity.**

### 6.1 What the number does and does not mean

| Reading | Assessment |
|---|---|
| "The model is badly named" | **Overstated.** An ERP with 1,335 tables across 14 revenue streams genuinely has thousands of single-use domain fields. `refurb_grade_code` belongs in one table |
| "Some concepts are named differently by different authors" | **Almost certainly true**, and it is invisible without the registry |
| "It can be fixed by inspection" | **False.** 5,301 names cannot be eyeballed; this is a registry query |

### 6.2 The reconciliation procedure

| Step | Action |
|---|---|
| 1 | Generate the registry (§5) so all 5,301 names carry a table, type and module |
| 2 | **Cluster by `data_element_concept`** (attribute 12) — the ISO/IEC 11179 object-class + property pair. Two fields with the same concept and different names are the candidates |
| 3 | Cluster by type + length + value domain, within a domain |
| 4 | **Steward review** — a human rules "same concept" or "different concept" |
| 5 | Same concept → **register a preferred name**; the variants become `Superseded` where a rename is cheap, or carry an alias where it is not |
| 6 | Publish the preferred-name list to `RR-001` and `AR-007` N-08's abbreviation register |

### 6.3 Where reconciliation is mandatory rather than desirable

| Class | Why |
|---|---|
| **Money fields** | A `total`, an `amount` and a `value` that mean the same thing produce three different report columns |
| **Party references** | `partner_id`, `party_id`, `customer_id` for one kernel concept breaks every join and every DPIA extract |
| **Date semantics** | `completed_date` vs `completion_date` vs `closed_at` — SLA measurement depends on which is meant |
| **Status/state** | Covered by `MD-027`, but 348 `state` fields need their code lists reconciled (`DA-009`) |

---

## 7. Reconciliation Checks — Closing the `F3` Class

**Four checks, all mechanical.** These are what make a repeat of `F3` a build failure rather than an
audit finding.

| # | Check | What it compares | Enforcement |
|---|---|---|---|
| **RC-1** | **Schema ↔ registry** | Every column has a registration; every registration has a column | **CI, blocking.** A column with no registration fails the build |
| **RC-2** | **Citation ↔ registry** | **Every `<file>.<field>` reference in any `DT-*`, `MD-*`, `LG-*`, `RP-*`, `TS-*` or module file resolves to a registered element** | **CI, blocking on the content repository.** **This is the check that catches `F3` directly** |
| **RC-3** | **Classification completeness** | Every element has attributes 21, 22, 23 assigned | Blocking before a wave gate; feeds `SC-003` |
| **RC-4** | **Retention completeness** | Every element carrying personal data has a `retention_class` resolving in `LG-009` | Blocking before a wave gate; feeds `DA-006` |

### 7.1 What `RC-2` would have caught, and when

`DT-031` cites nine `MD-028` fields. Under `RC-2`, the build of `DT-031` fails on the first of the
nine, naming the field and the register it is not in. **The audit found this in August 2026; `RC-2`
would have found it at the moment `DT-031` was written.**

> **`RC-2` is the highest-value check in this document and the least obvious**, because it operates on
> the *content* repository, not the code repository. `AR-012` `FF-36` registers it.

---

## 8. Personal Data, Sensitivity and Residency

### 8.1 Why these three attributes sit here and not in `DA-005`

`DA-005` defines the **scheme**. `DA-002` holds the **assignment, per field**. A scheme with no
per-field assignment cannot answer a regulator, and a per-field assignment with no scheme is
inconsistent.

### 8.2 The personal-data flag (attribute 22)

| Value | Meaning | Consequence |
|---|---|---|
| `not_personal` | Not related to an identified or identifiable person | None |
| `personal` | Ordinary personal data | Purpose + lawful basis required (NFR-090); erasure in scope (NFR-093) |
| **`sensitive`** | Heightened category under PDPA 2026 | **Specific consent or a legitimate ground** (NFR-091); heightened controls |
| **`restricted`** | Government unique identifiers, biometric, genetic, criminal-record | **`DA-001` §10 residency; NFR-099 transfer restriction** |

> **The `restricted` value is where `DA-001` §10.4's finding bites.** The estate's classification is by
> **field type**; the reported statutory definition is by **impact**. Until `DEP-31` resolves it,
> attribute 22 records the field-type assignment **and** carries a `basis` note recording that the
> statutory category may be broader or narrower. Guessing silently would be worse than either.

### 8.3 Residency (attribute 23)

| Value | Meaning |
|---|---|
| `none` | May live in the regional store |
| **`resident`** | `DA-001` §10 applies — value in Z4, `resident_key` in Z3 |
| **`resident_pending`** | **Classification unresolved pending `DEP-31`.** Treated as `resident` until decided — the conservative direction |

### 8.4 The extract `SC-003` needs

The DPIA cannot be written without this, and it does not currently exist in any form:

| Column | Source |
|---|---|
| Table, column, business name, definition | 2, 3, 9, 11 |
| Personal-data category | 22 |
| Classification | 21 |
| Residency | 23 |
| Owning module and data owner | 19, 20 |
| Processing purpose | `LG-008` `P-01`…`P-20`, joined via 24 |
| Lawful basis | `LG-008`, joined |
| Retention | 24 → `LG-009` `RC-01`…`RC-27` |
| Third-party disclosure | `AP-012` Data Sharing Register |

---

## 9. Worked Exemplar

*Abridged to demonstrate every attribute. The issued registry carries all elements at this depth.*

### 9.1 `fix_service_order.promised_date`

| # | Attribute | Value |
|---:|---|---|
| 1 | `element_id` | `DE-fix_service_order-promised_date` |
| 2–4 | Table / column / model | `fix_service_order` · `promised_date` · `fix.service.order` / `promised_date` |
| 5–7 | Type / precision / nullable | `timestamp` (UTC) · — · `NOT NULL` |
| 8 | Default | None — computed at `received` and frozen |
| 9–10 | Business name | *Promised completion date* / *প্রতিশ্রুত সমাপ্তির তারিখ* |
| **11** | **Definition** | **The date and time by which the company has committed to complete this service order, derived from the SLA policy in force when the order was received, and never recalculated afterwards** |
| 12 | Data element concept | Service order · promised completion · timestamp |
| 13 | Unit | — (timestamp, UTC; presented `Asia/Dhaka`) |
| 14 | Example | `2026-08-21T11:30:00Z` |
| 15 | Value domain | Range — must be ≥ `create_date` |
| 16 | Valid values | n/a |
| 17 | Validation | `ck_promised_after_created`; frozen after `received` (`AR-003` §6.10 DN-02) |
| 18 | Quality rules | Timeliness — a null on an order past `received` is a defect |
| 19 | Owning module | **M01 SRM** |
| 20 | Owner / steward | Service Operations Director / Service Ops MDM analyst |
| **21** | **Classification** | **S1 Internal** |
| **22** | **Personal data** | `not_personal` — a date about an order, not about a person |
| **23** | **Residency** | `none` |
| 24 | Retention class | **`RC-01`** — warranty period + limitation period |

> **Attribute 11 carries the design decision.** *"never recalculated afterwards"* is `DN-02`, and it is
> the difference between a commitment and an estimate. A developer who reads only the type sees a
> nullable timestamp and writes a recalculation.

### 9.2 `MD-028` — the exemplar that closes `F3`

`DA-002` registers the SLA band register's fields, **including the three `F3` found missing**. Each
must exist in `MD-028` §2 before it can be registered — which is the correction `AUDIT-013` `R-01`
requires.

| Element | Definition | Status |
|---|---|---|
| `sla_band_code` | The permanent code identifying an SLA band | `Registered` |
| `band_name_en` / `_bn` | Customer-facing band name | `Registered` |
| `response_target_min` | Minutes from clock start to first substantive response | `Registered` |
| `resolution_target_min` | Minutes from clock start to resolution | `Registered` |
| `clock_runs` | Whether the clock runs continuously or on the business calendar | `Registered` |
| `business_calendar_code` | The calendar governing the clock — `MD-041` | `Registered` |
| **`definition`** | **The band's meaning, printed verbatim on `DT-031`, never paraphrased** | **`Candidate` — field does not yet exist in `MD-028`** |
| **`clock_start_event`** | **The domain event that starts the clock** — `AR-009` registered name | **`Candidate` — field does not yet exist** |
| **`clock_stop_event`** | **The domain event that stops it** | **`Candidate` — field does not yet exist** |
| `measurement_basis` | How attainment is computed | `Candidate` |

> **`clock_start_event` and `clock_stop_event` must hold a registered `AR-009` event name**, not free
> text. That makes *"when does the clock start"* — the question `DT-031` §1.1 says every SLA dispute is
> about — a **foreign key**, resolvable in the event catalogue, rather than a sentence two parties
> read differently.

---

## 10. Coverage and Production Schedule

### 10.1 The denominator

| Class | Count |
|---|---:|
| Tables | **1,335** |
| Declared attributes | **11,622** |
| **Estimated total elements** | **~17,000–19,000** |
| **Registered today** | **0** |
| **Coverage** | **0%** |

### 10.2 Production rule

**`DA-002` follows `AR-003`'s rule: a module's elements are registered one wave before the wave that
builds it.** Registration is an `AR-003` design-gate exit criterion (`X-11`, added by this document).

| Wave | Registers | Elements *(est.)* |
|:--:|---|---:|
| **W0** | Platform + kernel: M28, M29, M30, M33, M37, M24-core, M21-core | ~1,800 |
| W1 | Service core: M01, M04, M17, M31 | ~1,400 |
| W2 | Field + inventory: M02, M15, M10, M64 | ~1,500 |
| W3 | Money + movement: M19, M20, M52, M50, M11, M36, M03, M16, M41, M24, M63 | ~3,400 |
| W4 | Agreements: M08, M09, M39, M51, M53, M27, M32, M34, M25, M62, M42 | ~3,200 |
| W5 | People + MSP: M21, M55, M56, M57, M22, M23, M05, M45, M46, M49 | ~2,800 |
| W6 | New lines: M13, M14, M06, M26, M43, M44, M54, M58, M59, M60, M61, M66 | ~2,900 |
| W7 | Channel: M38, M12, M40, M47, M67 | ~1,600 |
| W8 | Intelligence: M48, M18 | ~600 |
| W9 | M65 | ~300 |

> **W0 and W3 are the two that matter.** W0 registers the kernel, which every later element references.
> W3 registers the finance elements, where attribute 24 (retention) carries a **statutory 7-year**
> obligation and attribute 21 carries `S2`/`S3`.

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is the ~17,000–19,000-element registration effort funded?** (`PGD-A5-04`) | Programme Director | **W0** | The whole schedule |
| **Q-02** | Who is Registration Authority before a **Chief Data Officer** is appointed? Attributes 21–23 need CDO approval and the post is unfilled | CTO / `DA-003` | **W0 — blocking** | Every `S3` / personal / resident element |
| **Q-03** | Is `RC-2` (citation check on the **content** repository) accepted? It changes the content authoring workflow | Content Lead / Enterprise Architecture | W1 | The `F3` closure |
| **Q-04** | Are the three missing `MD-028` fields added, per `AUDIT-013` `R-01`? | Enterprise Architecture with Legal | **Before `MD-028`, `DT-031` or `LG-015` reach `Approved`** | `F3`; §9.2 |
| **Q-05** | Does the naming reconciliation (§6) run before or after W0 registration? Before is cheaper; after has better data | Data Architect | W0 | ~245-name scale, unknown |
| **Q-06** | Does `attribute 22` use the field-type basis or await `DEP-31`'s impact-based ruling? (`DA-001` §10.4) | DPO / Legal | **W1** | `SC-003`; `SC-007` |

---

## 12. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-D2-01 | Form | Markdown document; **generated registry** | **Registry** | 17,000 elements cannot be hand-maintained; `F3` proves it at 1/60th scale | A build artefact, not a file |
| D-D2-02 | Generation split | All authored; all generated; **60/40** | **Generated structure + authored meaning** | A machine cannot write a definition; a human cannot keep 17,000 types current | §5.2 |
| D-D2-03 | Attribute count | 12 minimal; **24** | **24** | The four with legal consequence (21–24) are exactly the four the estate cannot answer today | `SC-003` and `SC-007` become derivable |
| D-D2-04 | ISO 11179 statuses | Six; **four** | **Four** | `Preferred`/`Superseded`/`Retired` ceremony is unsustainable at this scale and cadence | Departure declared in §2.1 |
| D-D2-05 | `MD-*` ingestion | Re-author; **ingest as input** | **Ingest** | 48 files already carry 6 of 24 attributes; re-keying would introduce the divergence this document exists to prevent | `IN-02` raises findings automatically |
| D-D2-06 | Citation checking | Review; **`RC-2` in CI on the content repo** | **`RC-2`** | `F3` was found by an auditor 8 months after `DT-031` was written | Changes the content authoring workflow |
| D-D2-07 | Unresolved residency | Assume `none`; **`resident_pending`** | **`resident_pending`, treated as resident** | The conservative direction; a wrongly-regional restricted field is a notifiable event | Some fields over-protected until `DEP-31` |

---

## 13. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The population is counted with a reproducible method | §2.2; `DA-001` §15 |
| AC-02 | Every data element carries 24 mandatory attributes | §3 |
| AC-03 | Registration has an authority, four statuses and six lifecycle rules | §4 |
| AC-04 | The generated/authored split is declared per attribute | §5.2 |
| AC-05 | **Four reconciliation checks exist, and `RC-2` closes the `F3` class mechanically** | §7 |
| AC-06 | PII, sensitivity and residency are per-field, and the `SC-003` extract is specified | §8 |
| AC-07 | A worked exemplar covers every attribute, including the `F3` fields | §9 |
| AC-08 | Coverage is stated against a counted denominator with a wave schedule | §10 |
| AC-09 | The estimate is labelled as an estimate | §2.2 |

**Definition of done.** Complete when every criterion is met, Q-01 and Q-02 are resolved, and
`PGD-000`'s `DA-002` row is updated. **`DA-002` reaches ✅ as a *standard and registry design* on
issue; as a *populated registry* it tracks §10.2** — 0% today, and it says so.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `DA-001` | Structure — attributes 1–8, 15, 17 |
| Upstream | `DA-005` | Classification scheme — attributes 21–23 |
| Upstream | `DA-003` | Owners and stewards — attribute 20 |
| Upstream | `DA-009` | Code lists — attributes 15, 16 |
| Upstream | `LG-009` | Retention classes — attribute 24 |
| Downstream | **`SC-003` DPIA** | §8.4 extract — **currently unobtainable** |
| Downstream | **`SC-007` residency** | Attribute 23 |
| Downstream | `DA-006` | Attribute 24 join |
| Downstream | `DA-008` | Attribute 18 |
| Downstream | `IN-002`, `IN-003` | API and event payload schemas derive from registered elements |
| Downstream | `MG-003`, `DM-004`…`DM-010` | Mapping targets |
| Downstream | `AR-012` `FF-36` | `RC-2` citation check |
| Lateral | The 48 `MD-*` files §2 | Ingested (§5.3), not superseded |
| Lateral | `RP-006` §4.2 | The warehouse-side equivalent; 16 attributes per dataset |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md` ·
`./DA-003_Data_Governance_Framework_and_Stewardship_Model.md` ·
`./DA-005_Data_Classification_and_Handling_Standard.md` ·
`./DA-006_Data_Retention_Archival_and_Deletion_Design.md` ·
`./DA-009_Reference_Data_and_Code_List_Register.md` ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md`

**Workspace**
`../../project_content/_AUDIT/AUDIT-013_Category_10_LG_Content_Audit.md` `LG-01` ·
`../../project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md` ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-006_BI_Semantic_Layer_Data_Dictionary.md` §4.2 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §10

**External standards**

| Standard | Version | Verified |
|---|---|---|
| [ISO/IEC 11179-1:2023 — Framework](https://www.iso.org/standard/78914.html) | Edition 4, January 2023 | 2026-08-18 |
| [ISO/IEC 11179-6:2023 — Registration](https://www.iso.org/standard/78916.html) | 2023 | 2026-08-18 |
| [ISO/IEC 11179-31:2023 — Data specification registration](https://www.iso.org/standard/78925.html) | 2023 | 2026-08-18 |
| [DAMA-DMBOK](https://www.damadmbok.org/) | 2.0 (2024 maintenance revision) | 2026-08-18 |
| [Bangladesh PDPA 2026](https://securiti.ai/bangladesh-personal-data-protection-act-overview/) | Enforcement ~13 May 2027 | 2026-08-18 |

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Establishes a **generated registry** of ~17,000–19,000 data elements with 24 mandatory attributes, four registration statuses and **four reconciliation checks — `RC-2` closes the `F3` class mechanically**. Raises `PGD-A5-04` (registry unfunded) and `PGD-A5-05` (76% singleton field names) | *Pending — CDO, unappointed* |

---

*`DA-002` · Category 03 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
