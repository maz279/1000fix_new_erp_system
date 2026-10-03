---
id: DM-011
title: Data Quality Rules, Cleansing and Deduplication Standard
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration with MDM
author: Data Migration with the Master Data Owner
reviewers: [Master Data Owner, Chief Commercial Officer, CFO, Service Ops Director, Localisation Lead, Security Lead, QA Lead]
approver: Master Data Owner with CTO
content_class: C
purpose: >
  Defines the profiling dimensions every source is measured on, the validation and cleansing rules
  applied before load, the matching and survivorship logic that produces a golden record, the
  thresholds that decide auto-merge against manual review, and the remediation queue that rejected
  records enter. Migrating dirty data into a system with hard business rules produces mass
  transaction failure on day one, and setting the match threshold after the load has begun means
  choosing between a merge you cannot undo and a duplicate you cannot find.
traces_to: [M64, M33, M17, MD-013, MD-007, MD-021, MD-022, RP-016, DM-001, DM-002, DM-003, DM-004, DM-005, DM-006, DM-007, DM-008, DM-009, DM-010, DM-012, DM-013]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: DM-011_Data_Quality_Rule_Register.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M64 §16.4 — M64's migration contribution is a quality assessment gate on every other module's load; each batch is scored against its domain rules before acceptance and records failing a blocking rule are rejected to a remediation queue rather than loaded; ~300–500 quality rules authored per domain from W2
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33 §16.4 — profile before load; duplicate rate, completeness and validity measured on the source before any load and reported to the CCO; _CATEGORY_OVERVIEW.md §risks — duplicate and fragmented customer records surviving migration rated Critical
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §12 MIG-01 and MIG-02 — every migration is preceded by a profiling report quantifying completeness, validity and duplication; cleansing happens in the source or a staging layer, never silently during load
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 — ASM-03 existing customer and device data exportable at ≥ 80% quality, consequence stated if false; RSK-014 migration quality below usable threshold rated High/High
    verified: 2026-08-18
    class: P1
  - source: Master data management practice — deterministic matching preferred, then composite, with fuzzy as a fallback only; attribute-level survivorship building the golden record field by field with an authoritative source and a survivorship rule per attribute; threshold tuning treated as a documented business risk decision taken before migration begins; organisations without an active data-quality programme commonly carry duplicate rates of 10–30 per cent
    verified: 2026-08-18
    class: P3
supersedes: none
review_due: 2027-02-18
---

# DM-011 — Data Quality Rules, Cleansing and Deduplication Standard

> Governs `DM-011_Data_Quality_Rule_Register.csv`. The markdown governs; the data file loads.
>
> **Template conformance note.** `CG-009` §3 allocates `TPL_Master_Data_Specification.md`. This file
> governs a **rule register** rather than a business dataset; every template section is retained in
> order and answered at rule-register level. The interpretation is declared here (`CP-09`, `E7`).
>
> **Identifier note (`CG-005` §3.3).** `DM-011` is a **content** identifier; `05-02` `DM-09`
> (modelling standard — UTF-8 with `bn_BD` collation) is cited with its document prefix and matters
> here because matching runs on text.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Migration data quality — all domains |
| Owning module | `M64` MDM — the quality-assessment gate on every load |
| Data steward | Master Data Owner |
| Golden source | This rule register |
| Refresh cadence | Per wave, and whenever a domain's rules change |
| Environments | Dev · SIT · UAT · Prod — rules run identically in all four |
| Content class | C — Operational-critical |
| Effective-dated | no |
| **Build wave** | **W1** |
| **Load wave** | **W1 onward** — every load in every wave passes through these rules |

**Consequence of absence (`CP-03`).** The 1000FiX ERP is a **hard-rule system**. `05-05` catalogues
business rules that block; `05-02` `DM-12` enforces foreign keys at the database level; `MD-013`
makes the mobile number the principal identity key; `BRU-SRM-09` blocks dispatch on certification.
A legacy estate of spreadsheets has none of these constraints, which is exactly why it produced the
data it did.

**Loading unconstrained data into a constrained system does not degrade gracefully.** It produces
mass transaction failure on the first working morning: orders that cannot be created because the
customer has no valid mobile, invoices that cannot post because a dimension is missing, dispatch
that cannot assign because a certification does not resolve.

Two further facts make this file `P0`:

| Fact | Source | Consequence |
|---|---|---|
| **The duplicate rate has never been measured** | `M33` §16.4 requires it measured *before* any load | The programme does not know whether it is migrating 100,000 customers or 70,000 customers three times |
| Duplicate and fragmented customer records surviving migration is rated **Critical** | `03_Modules/B/_CATEGORY_OVERVIEW.md` §risks | It is *"Critical — undermines every downstream module"* |

`ASM-03` assumes the source is exportable at **≥ 80% quality** and states the consequence if false:
*"Migration effort increases materially; manual cleansing programme required."* **Nothing has tested
the assumption.** Profiling (§2.2) is how it gets tested, and it must happen before the effort is
committed, not after.

---

## 2. Record structure

### 2.1 The quality-rule register

| Column | Type | Req | Constraint | Description |
|---|---|:--:|---|---|
| `rule_id` | char(14) | ✔ | `DQ-<DOMAIN>-nnn`, permanent | e.g. `DQ-PARTY-004` |
| `domain` | enum | ✔ | party / address / asset / order / inventory / finance / hr / contract / claim | Matches the `M64` domain register |
| `dimension` | enum | ✔ | See §2.2 | The quality dimension measured |
| `rule_text` | text(400) | ✔ | Executable description | |
| `severity` | enum | ✔ | **blocking / correctable / advisory** | Determines what happens on failure |
| `applies_at` | enum | ✔ | profile / extract / stage / load / post_load | Where in the pipeline it runs |
| `auto_fix` | bool | ✔ | | TRUE only for `correctable` |
| `fix_rule` | text(400) | | Required when `auto_fix` | The transformation applied |
| `target_field` | text(80) | ✔ | | |
| `error_message_id` | fk | ✔ | → `UI-004` | Every failure has a message |
| `owner` | text(120) | ✔ | The business role that owns the threshold | |
| `threshold` | text(80) | | For measured rules | e.g. *"≥ 98% populated"* |
| `active` | bool | ✔ | | |

> **`DQ-01` — three severities, three behaviours, no fourth.**
>
> | Severity | Behaviour on failure |
> |---|---|
> | **`blocking`** | The record is **rejected to the remediation queue**. It does not load, and it is not silently dropped |
> | **`correctable`** | The declared `fix_rule` is applied **in the staging layer**, the original value is retained, and the correction is counted |
> | **`advisory`** | The record loads, flagged, and the count appears in the reconciliation |
>
> There is no "load it anyway and fix it later" severity. `05-02` §12 `MIG-02` prohibits silent
> cleansing during load; `M64` §16.4 requires rejection to a remediation queue rather than loading.

### 2.2 Profiling dimensions

**`DQ-02`: every source is profiled on six dimensions before any load, and the report goes to the
named business owner.** This is `05-02` §12 `MIG-01`, BRD `MIG-002` and `M33` §16.4 rule 1.

| Dimension | Question | Measure | Why it is here |
|---|---|---|---|
| **Completeness** | Is the field populated? | % non-null, per field, per source file | Required-at-target fields with low completeness predict the rejection volume |
| **Validity** | Does the value match its declared form? | % passing the format rule | The BD mobile format is the highest-value single check |
| **Uniqueness** | How many records describe the same real thing? | Estimated duplicate rate, per candidate key | **The measurement `M33` demands and nobody has** |
| **Consistency** | Do related fields agree, within and across sources? | % of cross-field contradictions | District/upazila mismatches; contract dates versus entitlement periods |
| **Conformity** | Do categorical values map to a controlled list? | % resolving to `MD-nnn` | Drives the size of the value-list exercise |
| **Timeliness** | How stale is the record? | Age distribution of last-touched date | An address last touched in 2019 is not a current address |

Profiling output is a **per-source report**, not a global one. Fifty-one branch files have fifty-one
different qualities, and an average across them tells nobody which branch to visit.

### 2.3 Cleansing — where it happens

| Rule | Detail |
|---|---|
| **`DQ-03`** | Cleansing happens **in the source, or in the staging layer** — never silently during the load (`05-02` `MIG-02`, BRD `MIG-003`) |
| **`DQ-04`** | **The business data owner is accountable for source cleansing** (BRD `MIG-003`, `00-04` `DEP-05`). The migration team cleanses in staging; it does not decide what is correct |
| **`DQ-05`** | Every staging correction **retains the original value** in the legacy payload, so the correction is reversible and auditable |
| **`DQ-06`** | A correction rate above the declared threshold for a source **stops the load** and returns the file — a 40%-corrected file is not a cleansed file, it is a rewritten one |
| **`DQ-07`** | Bengali text is normalised to UTF-8 **before** any cleansing, matching or comparison (`DM-004` §2.5, `05-02` `DM-09`) |

### 2.4 The standard cleansing transformations

| # | Transformation | Applies to | Severity |
|---|---|---|:--:|
| `C-01` | Trim leading/trailing whitespace; collapse internal runs | All text | correctable |
| `C-02` | Strip non-printing and zero-width characters | All text | correctable |
| `C-03` | Encoding detection and UTF-8 conversion | Bengali text | correctable *(with `DQ-13` sample verification)* |
| `C-04` | Unicode normalisation to one form | Bengali text | correctable |
| `C-05` | BD mobile normalisation, including restoring the leading zero lost to numeric coercion | Phone fields | correctable → **blocking if it fails** |
| `C-06` | Case normalisation — upper for identifiers, preserved for names | Identifiers, names | correctable |
| `C-07` | Placeholder detection and nulling — `N/A`, `-`, `0`, `XXXX`, repeated characters, the column header | All | correctable |
| `C-08` | Date parsing against a **declared per-file source format**; never the parser default | Dates | blocking on ambiguity |
| `C-09` | Numeric parsing with thousands separators and Bengali numerals handled explicitly | Numerics | correctable |
| `C-10` | Multi-value cell splitting on `/`, `,`, `;` | Phones, emails, model lists | correctable |
| `C-11` | Honorific extraction from names — Md., Mr, Mrs, Alhaj, Eng. | Names | correctable |
| `C-12` | Controlled-value mapping through a signed value list | All categoricals | blocking if unmapped **and** no default is approved |
| `C-13` | Currency normalisation to explicit `BDT` (`05-02` `DM-07`) | Monetary | blocking |
| `C-14` | Timezone normalisation — stored UTC, presented `Asia/Dhaka` (`05-02` `DM-08`) | Timestamps | correctable |

> **`DQ-08` — `C-07` is not cosmetic.** A placeholder that survives cleansing becomes a *value*.
> `XXXX` as a serial number matches every other `XXXX` in the estate and produces a large, confident,
> entirely false duplicate cluster. The placeholder register is versioned here and extended at every
> profiling run.

### 2.5 Matching — deterministic first, fuzzy last

**`DQ-09`: matching runs in three passes, in this order, and a record matched in an earlier pass is
never re-evaluated by a later one.**

| Pass | Method | Party keys | Asset keys | Confidence |
|:--:|---|---|---|---|
| **1** | **Deterministic** — exact match on a strong identifier | `primary_mobile` after `C-05`; `bin`; `nid` *(resident store only)* | `imei`; `serial` + resolved `model_code` | 1.00 |
| **2** | **Composite** — exact match on a combination, none of which is sufficient alone | normalised name + upazila + any phone; legal name + BIN prefix | serial alone + owner party; asset tag + owner party | 0.85–0.99 |
| **3** | **Fuzzy** — similarity scoring, **candidate generation only** | name similarity + address similarity + phone edit distance | model + owner + purchase-date proximity | 0.50–0.85 |

| Rule | Detail |
|---|---|
| **`DQ-10`** | **Fuzzy matching never auto-merges.** It generates candidates for human review. Pass 3 output above the review threshold enters the stewardship queue; nothing else |
| **`DQ-11`** | Bengali and romanised forms of the same name must be comparable. This requires the [`BN-004`](../11_Localisation_Bengali/BN-004_Do_Not_Translate_and_Transliteration_Register.md) transliteration register, which exists at `Draft` but was **written for product content, not for record matching** (`O-03`) |
| **`DQ-12`** | Matching runs **within and across sources**. The same customer in a branch spreadsheet and the legacy tracker is one party (`DM-004` `PM-07`); the same job in both is one order (`DM-006`) |
| **`DQ-13`** | A source whose encoding conversion has not been sample-verified may not enter matching — a match run on mis-decoded text produces confident nonsense |

### 2.6 Thresholds — set before the load, by the business

**`DQ-14`: the thresholds below are a documented business risk decision, taken and signed before
migration begins.** They are the trade-off between a false merge (two customers become one — hard to
undo, visible to both) and a false split (one customer stays two — recoverable, but degrades
service, loyalty and history).

| Band | Score | Action | Rationale |
|---|---|---|---|
| **Auto-merge** | ≥ **0.95** | Merged automatically; survivorship applied per §2.7 | Deterministic or near-deterministic; false-merge risk minimal |
| **Review** | **0.80 – 0.95** | **Stewardship queue** — a human decides | The band where both error types are real |
| **Weak candidate** | **0.65 – 0.80** | Recorded as a *possible link*, **not merged**, surfaced in the ongoing burn-down | Preserves the signal without acting on it |
| **No match** | < 0.65 | Treated as distinct | |

> **`DQ-15` — asymmetric caution on the customer domain.** For `fix.party`, the auto-merge threshold
> is **0.95 and requires a pass-1 or pass-2 match**; a pass-3 score of 0.96 does not auto-merge. A
> wrongly merged customer exposes one person's service history, addresses and contact details to
> another — a personal-data incident under the PDPA 2026, not a data-quality defect.

> **`DQ-16` — the review queue must be sized before the threshold is set.** If profiling shows a
> 15% duplicate rate on 100,000 customers, and the review band captures a third of the candidate
> pairs, the stewardship queue is in the **thousands of decisions**. At two minutes each that is
> weeks of work by someone who can recognise a customer. **Setting a threshold without sizing its
> queue is choosing a number and discovering its cost later.**

### 2.7 Survivorship — attribute by attribute

**`DQ-17`: the golden record is built field by field, not by choosing a winning record.**

| Attribute class | Survivorship rule | Rationale |
|---|---|---|
| Identity keys — mobile, NID, BIN | **Most recently verified**, then most frequently occurring | The number that reaches the customer wins |
| Names | **Longest complete form** from the most authoritative source | Truncation loses information; expansion does not |
| Bengali name | From the source with verified encoding | An un-verified encoding is not a candidate |
| Address | **Most recently used** — an address with a completed delivery beats an older one | `MD-007` `is_verified` is set only by a completed delivery |
| Segment, tier, credit terms | **From the commercially authoritative source**, never the most recent edit | A branch spreadsheet does not outrank a signed contract |
| Consent | **Never survives from either record** — no consent is inferred (`MS-20`) | |
| Dates — joining, purchase, contract start | **Earliest evidenced**, from a document where one exists | |
| Free text — notes, remarks | **Concatenated with source attribution**, never discarded | Loses nothing; costs nothing |
| Balances and quantities | **Never merged.** A merge candidate carrying a balance is escalated | Two balances are two facts, not one |

| Rule | Detail |
|---|---|
| **`DQ-18`** | Every attribute in the golden record carries its **authoritative source, its survivorship rule and the date it won** |
| **`DQ-19`** | The merge loser is **retained** with `golden_record_id` pointing at the survivor (`MD-013`); it is never deleted (`05-02` `DM-06`) |
| **`DQ-20`** | **Merges are reversible for the duration of the burn-down.** An un-mergeable merge is an auto-merge threshold set too low |

### 2.8 The remediation queue

| Rule | Detail |
|---|---|
| **`DQ-21`** | Every `blocking` rejection enters the remediation queue with the rule that rejected it, the source record verbatim, and a named owner |
| **`DQ-22`** | The queue has a **declared drain rate and a target date per wave**. A queue with no drain rate is a bin |
| **`DQ-23`** | Records still in the queue at the wave gate are **reported in the reconciliation** (`DM-013`), by count and by rule — not carried silently into the next wave |
| **`DQ-24`** | A rule producing rejections above its declared tolerance is **reviewed before the records are** — a 30% rejection rate usually indicts the rule or the source, not the records |
| **`DQ-25`** | Remediation output re-enters at the same tier in `DM-003`, in the same order, never as a shortcut load |

### 2.9 The `M64` gate — and its timing problem

`M64` §16.4 defines its own migration contribution precisely:

> *"Its migration contribution is a **quality assessment gate on every other module's load**: each
> migration batch is scored against its domain rules before acceptance, and records failing a
> blocking rule are rejected to a remediation queue rather than loaded."*

**`M64` is a W2 module. Tiers `X1`–`X5` load at W1.** The gate that scores every batch arrives one
wave after the batches it is supposed to score.

**`DQ-26` — the interim gate.** Until `M64` is live, this standard is enforced by the migration
pipeline itself, with the same three severities, the same rejection behaviour and the same queue,
and **the results are re-scored by `M64` when it arrives**. An interim gate that produces no
comparable evidence is not a gate. Recorded as `O-01`.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `rule_id` |
| Code format | `DQ-<DOMAIN>-nnn` — domain uppercase, three digits, permanent |
| Reuse policy | Never reused. A withdrawn rule is `active = FALSE` with the withdrawal date and reason |
| Relationship to `M64` | These rule ids are the migration-time expression of the ~300–500 `M64` domain quality rules; **the same rule keeps the same id in both** so pre- and post-go-live quality are comparable |
| Relationship to `UI-004` | Every rule carries an `error_message_id` resolving in `UI-004`, so a rejection is explainable to a human |

---

## 4. Validation rules

*(Rules governing the register itself. Class per `05-05` §1.)*

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `DQ-01` | Three severities only; no "load anyway" behaviour exists | **H** | `ERR-DQR-001` |
| `DQ-02` | No load runs against a source with no accepted profiling report | **H** | `ERR-DQR-002` |
| `DQ-03` | Cleansing occurs in the source or staging, never during load | **H** | `ERR-DQR-003` |
| `DQ-05` | Every staging correction retains the original value | **H** | `ERR-DQR-005` |
| `DQ-06` | A correction rate above the source's declared threshold stops the load | **H** | `ERR-DQR-006` |
| `DQ-10` | Fuzzy matches never auto-merge | **H** | `ERR-DQR-010` |
| `DQ-13` | Unverified encoding blocks entry to matching | **H** | `ERR-DQR-013` |
| `DQ-14` | Thresholds are signed before the first load and versioned thereafter | **H** | `ERR-DQR-014` |
| `DQ-15` | Party auto-merge requires a pass-1 or pass-2 match at ≥ 0.95 | **H** | `ERR-DQR-015` |
| `DQ-16` | A threshold change requires the resulting queue size to be recomputed and accepted | **H** | `ERR-DQR-016` |
| `DQ-17` | Survivorship is attribute-level; whole-record survivorship is prohibited | **H** | `ERR-DQR-017` |
| `DQ-18` | Every golden attribute records its source, rule and date | **C** | `WRN-DQR-018` |
| `DQ-19` | Merge losers are retained and linked, never deleted | **H** | `ERR-DQR-019` |
| `DQ-20` | Merges are reversible through the burn-down period | **H** | `ERR-DQR-020` |
| `DQ-21` | Every blocking rejection enters the queue with rule, record and owner | **H** | `ERR-DQR-021` |
| `DQ-23` | Queue contents are reported at the wave gate by count and by rule | **H** | `ERR-DQR-023` |
| `DQ-24` | A rule above its rejection tolerance is reviewed before its records are | **C** | `WRN-DQR-024` |
| `DQ-26` | The interim gate produces evidence comparable with `M64`'s | **H** | `ERR-DQR-026` |
| `DQ-27` | Balances and quantities are never merged; such candidates escalate | **H** | `ERR-DQR-027` |
| `DQ-28` | Rule ids are shared with `M64` so quality is comparable across the go-live boundary | **C** | `WRN-DQR-028` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| [`DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md`](DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md) | 1:N | Profiling status per source is the `DQ-02` gate |
| `MD-006`, `MD-013`, `MD-021`, `MD-022`, `MD-026`, `MD-027` | N:1 | Conformity rules resolve against them |
| `UI-004` error message library | N:1 | Every rule needs its message |
| [`../11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md`](../11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md) · [`../11_Localisation_Bengali/BN-004_Do_Not_Translate_and_Transliteration_Register.md`](../11_Localisation_Bengali/BN-004_Do_Not_Translate_and_Transliteration_Register.md) | N:1 | Written 2026-08-17, `Draft`. `DQ-11` needs a **matching-grade** transliteration basis; confirmation outstanding (`O-03`) |
| `M64` domain rule register | 1:1 | **Shared ids** (`DQ-28`) |

| Depended on by |
|---|
| `DM-004` … `DM-010` — every mapping cites `dq_rule` · [`DM-012_Migration_Load_Template_Pack.md`](DM-012_Migration_Load_Template_Pack.md) validation columns · [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) exception classes · `RP-016` data quality scorecard · `M64` post-go-live quality |

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | The `MD` specifications' §4 validation rules; the `05-05` business rules that will block at runtime; the profiling results per source |
| Who supplies it | Master Data Owner, with each domain's business owner setting its thresholds |
| Collection method | **Derivation** — a migration quality rule exists because a runtime rule or a target constraint exists. Rules invented independently drift from what the system will actually enforce |
| Known quality issues | Rules cannot be complete before profiling; the register grows through W1 and stabilises at W2 with `M64` |
| Cleansing rules applied | n/a — this file *is* the cleansing standard |
| Re-verification | Every wave; and whenever an `MD` §4 rule changes |

---

## 7. Volumes

| Item | Count | Note |
|---|---:|---|
| Quality rules at W1 | **Target ~120–180** across nine domains | Derived from the `MD` §4 rules and the `05-05` blocking set |
| Quality rules at steady state | **~300–500** | `M64` §16.4 |
| Sources to profile | **48** | `DM-002` |
| Party records to match | **100,000+** | Duplicate rate **unmeasured** |
| Asset records to match | **300,000–600,000** | Population itself unmeasured |
| Expected review-queue volume | **Unknown until profiling** | `DQ-16` — this is the number that sizes the stewardship team |

> **The honest position on duplicate rate.** Organisations without an active data-quality programme
> commonly carry duplicate rates in the **10–30%** range, and best-in-class operations hold below
> 1%. 1000FiX has never run such a programme, and `ASM-03` assumes ≥ 80% quality without evidence.
> **This file does not adopt a figure.** Under `CG-012` `EV-05`, a quantitative claim about the
> business cites its system of record; there is none, so the number is produced by profiling
> (§2.2) and until then the planning range stays explicitly open.

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add a rule | Migration analyst or domain steward |
| Who may set a threshold | **The domain's business owner** — CCO for party, Service Ops Director for asset, CFO for finance, HR Director for people |
| Who may approve a rule as `blocking` | Master Data Owner |
| Approval required | **CTO and Master Data Owner for any threshold change after the first load**, with the recomputed queue size |
| Effective dating | Not effective-dated; versioned per wave |
| Archive rule | Withdrawn rules are `active = FALSE`, never deleted |
| Logged in | `RF-006`; threshold decisions logged with the signing owner and the queue size accepted |

---

## 9. Sample rows

```csv
rule_id,domain,dimension,rule_text,severity,applies_at,auto_fix,fix_rule,target_field,error_message_id,owner,threshold,active
DQ-PARTY-004,party,validity,primary_mobile must match 01[3-9] followed by 8 digits after C-05 normalisation,blocking,stage,TRUE,C-05 restore leading zero and strip separators,fix.party.primary_mobile,ERR-PMP-002,Chief Commercial Officer,>= 97% valid,TRUE
DQ-PARTY-011,party,conformity,display_name_bn must be valid UTF-8 and pass sample verification before matching,blocking,extract,TRUE,C-03 detect and convert encoding then C-04 normalise,fix.party.display_name_bn,ERR-PMP-013,Localisation Lead,100% of files sample-verified,TRUE
DQ-PARTY-030,party,uniqueness,pass-3 fuzzy candidates in the 0.80-0.95 band enter the stewardship queue and never auto-merge,blocking,post_load,FALSE,,fix.party,ERR-DQR-010,Master Data Owner,queue drained by W2 gate,TRUE
DQ-ASSET-004,asset,validity,serial_no must not be a registered placeholder value,correctable,stage,TRUE,C-07 null the value and downgrade identity_confidence,fix.asset.serial_no,ERR-DAM-002,Service Ops Director,,TRUE
DQ-FIN-008,finance,consistency,sum of migrated AR open items must equal the receivable control account exactly,blocking,post_load,FALSE,,account.move.line,ERR-FIN-008,CFO,exact,TRUE
DQ-HR-006,hr,completeness,ytd_tax must be present and reconciled per employee before the first live payroll run,blocking,load,FALSE,,fix.payroll.balance,ERR-HRP-007,HR Director,100%,TRUE
```

---

## 10. Migration notes

**This file is the difference between a migration that fails visibly and one that fails invisibly.**

A `blocking` rule produces a rejection, a queue entry and a number in the reconciliation — a visible
failure with an owner. A missing rule produces a loaded record that satisfies the database and
violates the business, and it surfaces weeks later as an inexplicable operational problem.

**The single most important decision in this file is §2.6, and it must be taken before the first
load.** Once records are merged, the threshold that merged them is history. `DQ-20` keeps merges
reversible through the burn-down precisely so that a threshold set slightly wrong is recoverable —
but only within the window, and only if the reversal capability was built rather than assumed.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md`](DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md) | `profiling_status` is the `DQ-02` gate |
| [`DM-004_Field_Mapping_Workbook_Party_and_Customer.md`](DM-004_Field_Mapping_Workbook_Party_and_Customer.md) | The domain with the highest match risk and the `DQ-15` asymmetry |
| [`DM-005_Field_Mapping_Workbook_Device_and_Asset.md`](DM-005_Field_Mapping_Workbook_Device_and_Asset.md) | The placeholder register and identity confidence |
| [`DM-012_Migration_Load_Template_Pack.md`](DM-012_Migration_Load_Template_Pack.md) | Templates carry the rule ids that will judge their content |
| [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) | Rejection and queue reporting |
| [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md) | `match_confidence` and `golden_record_id` semantics |
| `RP-016` Data Quality Scorecard | The post-migration continuation of these measures — **unwritten; Category 14 held zero files at enumeration 2026-08-18** |
| `M64` §16.4 | The gate this standard anticipates and shares ids with |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Three severities, six profiling dimensions, fourteen cleansing transformations, three-pass matching with fuzzy restricted to candidate generation, four threshold bands with an asymmetric party rule, attribute-level survivorship, a queue with a declared drain rate, and an interim gate covering the `M64` timing gap | Master Data Owner (pending) |

---

## 13. Open items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **`M64` arrives at W2; tiers `X1`–`X5` load at W1.** `DQ-26` specifies an interim gate producing comparable evidence, but the interim gate has no build owner and no place in any plan | Master Data Owner with CTO | **W1 — blocking** |
| **`O-02`** | **No source has been profiled.** `DQ-02` blocks every load; `ASM-03`'s ≥ 80% quality assumption is untested; the duplicate rate `M33` requires measured *before* any load does not exist | Data Migration Lead with domain owners | **W1 — immediately** |
| **`O-03`** | **`BN-004` and `BN-003` exist at `Draft` (written 2026-08-17) but were authored for product content, not for record matching.** `DQ-11` requires Bengali and romanised forms of the same *customer name* to be comparable — a transliteration basis with a defined comparison function, which a do-not-translate register does not by itself provide | Localisation Lead with Master Data Owner | **W1 — before matching** |
| **`O-04`** | **Thresholds are unsigned and their queue sizes uncomputed.** `DQ-14` and `DQ-16` require both before the first load. The decision belongs to four domain owners who have not been asked | Master Data Owner with CCO, CFO, Service Ops Director, HR Director | **W1 — before the first load** |
| **`O-05`** | **Merge reversibility (`DQ-20`) is a build requirement with no specification.** `06-03` does not exist (`DM-001` `O-01`), so nothing states how a merge is unwound or for how long the capability persists | CTO with Platform Engineering | **W1** |
| **`O-06`** | **Stewardship capacity is unsized and unfunded.** The review queue, the `DM-005` provisional-identity burn-down and the `DM-007` quarantine population all drain into the same human capability. `06-01` allocates 20% of a data owner | Programme Director with Master Data Owner | **W1** |
| **`O-07`** | **`UI-004` message ids cited here must exist.** Every rule carries an `error_message_id`; the migration-specific `ERR-*` families in `DM-004`…`DM-010` are new and are not yet registered in `UI-004` | Content Design with Data Migration | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; the rule-register adaptation is **declared**, not silent
- [x] Rule register structure defined with severity, pipeline stage, owner, threshold and message id
- [x] **Three severities with no "load anyway" option**, aligned to `05-02` `MIG-02` and `M64`
- [x] Six profiling dimensions defined and made a precondition of loading (`DQ-02`)
- [x] Cleansing located in source or staging, with originals retained and a correction-rate stop
- [x] Fourteen standard transformations enumerated, including the Bengali encoding and placeholder cases
- [x] **Three-pass matching with fuzzy restricted to candidate generation** (`DQ-10`)
- [x] **Thresholds presented as a business risk decision to be signed before load**, with the party asymmetry justified on personal-data grounds
- [x] **Review-queue sizing made a precondition of setting a threshold** (`DQ-16`)
- [x] Attribute-level survivorship specified per attribute class, with balances excluded from merging
- [x] Merge losers retained and linked; merges reversible through the burn-down
- [x] Remediation queue given a drain rate, a wave-gate report and a rule-review trigger
- [x] **The `M64` W1/W2 timing gap identified and covered by a specified interim gate**
- [x] Duplicate rate **not** asserted — profiling named as the only acceptable source (`CG-012` `EV-05`)
- [x] Sample rows included and parse as CSV
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] **`O-02` no source profiled — `DQ-02` blocks every load**
- [ ] **`O-04` thresholds unsigned and queue sizes uncomputed**
- [ ] **`O-01` the `M64` gate arrives one wave after the loads it must score**
- [ ] Named approver recorded — **pending Master Data Owner with CTO**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
