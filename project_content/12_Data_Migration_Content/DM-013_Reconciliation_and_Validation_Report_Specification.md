---
id: DM-013
title: Reconciliation and Validation Report Specification
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration with Finance
author: Data Migration with the Financial Controller and QA
reviewers: [CFO, Chief Commercial Officer, Service Ops Director, HR Director, Warehouse Manager, Master Data Owner, QA Lead, External Auditor]
approver: CFO with Data Migration Lead
content_class: C
purpose: >
  Specifies the report that proves a migration load is correct: the reconciliation classes, the
  control totals per domain, the exception categories, the acceptance thresholds and the sign-off
  form the accountable business owner signs. Migration is not done when it loads; it is done when it
  reconciles and someone signs the reconciliation, and a signed reconciliation is a wave-gate
  criterion at three of the five gates.
traces_to: [TS-018, M19, M20, M33, M17, M15, M56, M64, 06-02, DM-001, DM-002, DM-003, DM-004, DM-005, DM-006, DM-007, DM-008, DM-009, DM-010, DM-011, DM-012, DM-014, RP-016]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: DM-013_Reconciliation_Control_Register.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §12 MIG-04 — reconciliation counts and control totals are signed off by the business owner before cutover; MIG-01 profiling precedes every load
    verified: 2026-08-18
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §11.6.2 — MIG-004 validation rules and reconciliation reports with control totals on every load; MIG-006 signed reconciliation by the named data owner as a wave gate criterion; MIG-013 financial history reconciled to the trial balance before Gate 3
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 §Gates — G1-05 customer and device data migrated and reconciled, evidence signed reconciliation; G2-06 inventory accuracy verified by count; G3-08 financial history reconciled to the trial balance
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33 §16.4 AC-13 — migration reconciles when source count, loaded count, rejected count and duplicate count are all accounted for, signed by the CCO
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §Quality — data migration reconciliation and control totals on every load, before every cutover
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# DM-013 — Reconciliation and Validation Report Specification

> Governs `DM-013_Reconciliation_Control_Register.csv` and the report it produces. The markdown
> governs; the register configures.
>
> **Template conformance note.** `CG-009` §3 allocates `TPL_Master_Data_Specification.md`. This file
> governs a **report specification and its control register**; every template section is retained in
> order and answered at that level. Declared here (`CP-09`, `E7`).
>
> **Identifier note (`CG-005` §3.3).** `DM-013` is a **content** identifier.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Migration assurance |
| Owning module | `M64` for the quality gate; `M19` for the financial reconciliation |
| Data steward | Data Migration Lead, with the Financial Controller for finance domains |
| Golden source | This specification |
| Refresh cadence | **Every load, in every environment** — dry runs produce the same report as production |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |
| **Build wave** | **W1** |
| **Load wave** | **W1 onward** |

**Consequence of absence (`CP-03`).** The register's justification is the sentence this whole file
implements: *"Migration is not 'done' when it loads; it is done when it reconciles and someone signs
the reconciliation."*

Three programme commitments make the signed reconciliation a gate rather than a report:

| Commitment | Source |
|---|---|
| **Reconciliation counts and control totals are signed off by the business owner before cutover** | `05-02` §12 `MIG-04` |
| **Signed reconciliation by the named data owner is a wave-gate criterion** | BRD `MIG-006` |
| Migration reconciles when **source, loaded, rejected and duplicate counts are all accounted for**, signed by the CCO | `M33` `AC-13` |

Without a specification, "reconciled" means whatever the person writing the slide decides it means —
and the most common meaning is *"the same number of rows came out as went in"*, which is satisfied by
a migration that loaded every record into the wrong customer.

---

## 2. Record structure

### 2.1 The five reconciliation classes

**`RV-01`: every load is reconciled on all five classes that apply to it. A class that does not
apply is stated as not applicable, with the reason — it is never simply absent.**

| Class | Question | Typical control | Applies to |
|:--:|---|---|---|
| **R1 — Completeness** | Did every source record reach a decision? | `source = loaded + rejected + deliberately_excluded` | **All loads** |
| **R2 — Control total** | Do the values agree? | Sum of a monetary or quantity column, source versus target | Finance, inventory, payroll, contracts |
| **R3 — Referential** | Does every foreign key resolve? | Zero orphans per relationship | All loads with a parent |
| **R4 — Business rule** | Would the loaded record be legal in the running system? | Zero `blocking` `DM-011` failures post-load | All loads |
| **R5 — Semantic** | Does the record mean what it meant? | Distribution comparison, sampled record inspection | **All loads** |

> **`RV-02` — R1 is an identity, not a comparison.** `source = loaded + rejected + excluded`, with
> no residual. A load reporting 98,400 loaded from 100,000 source and 900 rejected has **700
> unaccounted records** and has not reconciled, regardless of how good 98.4% sounds.

> **`RV-03` — R5 is the class that catches the errors the others cannot.** Row counts and control
> totals both pass when every record loads against the wrong parent, when every date shifts by a
> month, or when a status maps to the wrong state. R5 is a **distribution comparison plus a sampled
> human inspection**, and it is mandatory. It is also the class most often dropped, because it
> cannot be fully automated.

### 2.2 R5 semantic checks — what is actually compared

| Check | Method | Threshold |
|---|---|---|
| **Categorical distribution** | Source status/type distribution versus target, per source file | No category shifting by more than a declared tolerance without explanation |
| **Date distribution** | Histogram by month, source versus target | No systematic shift; a one-month displacement indicates a format error |
| **Numeric distribution** | Min, max, mean, and the count of zeros and negatives | A new population of zeros indicates a parse failure |
| **Null profile** | Per-field null rate, source versus target | An increase indicates dropped mappings |
| **Sampled inspection** | **A stratified sample of records, read end to end by the business owner** | Sample size per §2.5; **any semantic defect fails the load** |
| **Bengali rendering** | A sample of Bengali fields **rendered and read by a native speaker** | Zero mojibake tolerated |
| **Round-trip** | Take a loaded record, find its source record by `legacy_record_id`, compare field by field | 100% match on mapped fields |

> **`RV-04` — the sampled inspection is done by the business owner, not by the migration team.** The
> migration team can prove the data moved; only the person who knows the business can say the record
> still means what it meant. This is the same principle `TS-006` applies to UAT scripts.

### 2.3 Control totals by domain

**`RV-05`: each domain's control totals are declared in `DM-013_Reconciliation_Control_Register.csv`
before its first load, and are not changed after a load has run.**

| Domain | Control totals | Tolerance | Signed by |
|---|---|---|---|
| **Party** | Record count; count by party type; count by segment; **duplicate count after matching**; count with valid mobile | **Zero unaccounted** (R1); duplicate count reported, not thresholded | **CCO** (`M33` `AC-13`) |
| **Address** | Address count; count with resolved geography to upazila level; count with computed zone | Zero unaccounted | CCO |
| **Asset** | Record count; **`confirmed` / `probable` / `provisional` split**; count by device family; identifier-collision count | Zero unaccounted; **the confidence split is reported, never summarised to one number** (`DM-005` §10) | Service Ops Director |
| **Service history** | Record count by `migration_class`; count by target state; count with resolved asset; count with resolved party | Zero unaccounted | Service Ops Director |
| **Inventory** | **Counted quantity by part × location**; total counted lines; quarantine line count; **count-versus-spreadsheet variance** (`IV-03`); consignment quantity by brand | Zero unaccounted; variance **reported as the baseline measurement** | Warehouse Manager |
| **Finance — GL** | **Total debits = total credits**; balance per control account; count of accounts loaded | **Exact. No tolerance** | **CFO with the external auditor** |
| **Finance — AR/AP** | **Sum of open items = control account balance**; item count; ageing distribution; count by currency | **Exact** (`FO-08`) | Financial Controller, countersigned by CFO |
| **Finance — cash and bank** | Counted cash per location; bank balance per account; reconciling-item count and total | **Exact** | Financial Controller |
| **Tax** | Opening input credit versus last filed Mushak 9.1; **Mushak 6.3 sequence position** | **Exact** (`FO-13`) | CFO with the tax consultant |
| **Contracts** | Contract count by evidence rung; entitlement grant total; covered-asset count; **count flagged `entitlement_unconfirmed`** | Zero unaccounted; **the rung split is the headline figure** | CCO |
| **Claims** | Live claim count and value; archived claim count and value; **the difference is the write-off exposure** | Zero unaccounted | Finance Director with CFO |
| **People** | Employee count; **YTD balance per element, per employee**; leave-balance agreement count; competency coverage % | **Exact on YTD** | **HR Director with CFO** (`M56`) |
| **Archive** | Record count; count retrievable by legacy reference (sampled) | Zero unaccounted | Service Ops Director |

### 2.4 Exception categories

**`RV-06`: every record that did not load is in exactly one category, and every category has an
owner and a disposition.**

| # | Category | Meaning | Disposition | Blocks the gate? |
|:--:|---|---|---|:--:|
| **E1** | **Rejected — blocking rule** | Failed a `DM-011` `blocking` rule | Remediation queue with the rule id | **Yes, above tolerance** |
| **E2** | **Rejected — referential** | A foreign key did not resolve | Remediation queue; usually a sequencing or upstream-load defect | **Yes** |
| **E3** | **Held — evidence** | Loaded at a lower rung, or held, pending evidence (`CW-01`, `DA-01`) | Business follow-up with a target date | No — **but the count is reported** |
| **E4** | **Held — residency** | `S3` field deferred pending resident-store verification (`MS-21`) | Second-pass load | No — reported |
| **E5** | **Excluded — by disposition** | `DM-001` disposition `L` or `P`; deliberately not migrated | None; the decision is the record | No |
| **E6** | **Quarantined** | Real physical stock with an unresolvable part (`IV-04`) | Stewardship queue | No — reported |
| **E7** | **Merged** | Absorbed into a golden record (`DQ-17`) | Loser retained and linked | No — **the merge count is a headline figure** |
| **E8** | **Duplicate — unresolved** | Match candidate in the review band, undecided | Stewardship queue | **Yes, above tolerance** |
| **E9** | **Semantic defect** | Loaded, but R5 inspection found it means something different | **Roll back and re-run** | **Yes — always** |

> **`RV-07`.** E5 must be reported even though nothing failed. A business owner reading a
> reconciliation needs to see that 500,000 paper records were deliberately excluded, not wonder
> where they went. A silent exclusion is indistinguishable from a loss.

### 2.5 Acceptance thresholds

**`RV-08`: thresholds are set per domain, before the first load, by the accountable owner, and are
recorded in the control register.** Where the module set already states a threshold, that value is
adopted, not re-derived.

| Domain | Threshold | Source of the number |
|---|---|---|
| Finance — GL, AR/AP, cash, bank, tax | **Exact. Zero variance** | `M19`, `M20`, `M51` §16.4 |
| Payroll YTD | **Exact, per employee** | `M56` §16.4 |
| Inventory accuracy at migrated locations | **≥ 95%, verified by count** | `06-02` `G2-06` |
| Van stock daily variance | **< 2%** | `06-02` `G2-07` |
| Party — E1+E2 rejection rate | **Declared at profiling**, not assumed | `DM-011` `O-04` |
| Party — E8 unresolved duplicates at gate | **Zero at the wave gate**; the queue must be drained | `DQ-22` |
| Asset — provisional share | **No threshold; a published burn-down instead** | `M17` §16.4 |
| Any domain — E9 semantic defects | **Zero** | `RV-03` |
| Any domain — R1 unaccounted records | **Zero** | `RV-02` |

> **`RV-09` — a threshold not met is not a judgement call.** It produces one of three recorded
> outcomes: **pass**, **conditional pass with a dated remediation plan** (the `06-02` §Gates
> convention for partial passes), or **fail**. "Broadly reconciled" is not an outcome.

### 2.6 The report structure

Every load, in every environment, produces the same report. **`RV-10`: a dry run produces an
identical report to a production run**, so that the two are comparable and the production result is
not the first time anyone has seen the format.

| § | Section | Contents |
|---|---|---|
| 1 | **Header** | Load id, batch id, template versions, source ids, environment, start and end instant, operator |
| 2 | **R1 completeness** | Source, loaded, rejected, excluded, **unaccounted** — per source file, then total |
| 3 | **R2 control totals** | Declared totals, source value, target value, variance, tolerance, result |
| 4 | **R3 referential** | Per relationship: rows, resolved, orphaned |
| 5 | **R4 business rule** | Per `DM-011` rule: evaluated, passed, failed, severity |
| 6 | **R5 semantic** | Distribution comparisons; sample size, sample result, inspector, Bengali render check |
| 7 | **Exceptions** | E1–E9 counts, each with owner, target date and queue reference |
| 8 | **Threshold assessment** | Per threshold: value, target, **pass / conditional / fail** |
| 9 | **Rollback readiness** | Rollback rehearsed on this tier: yes/no; **measured duration** (`SQ-08`) |
| 10 | **Sign-off** | §2.7 |

### 2.7 The sign-off form

**`RV-11`: the signature is on a statement, not on a number.** A signatory who signs "I have seen the
report" has not accepted anything.

> **Migration reconciliation sign-off — <domain>, <wave>, <environment>**
>
> I confirm that:
>
> 1. every source record is accounted for as loaded, rejected or deliberately excluded, with no
>    residual;
> 2. the control totals in §3 agree within their declared tolerance, and I set that tolerance;
> 3. I or my nominee inspected the §6 sample and the records mean what they meant in the source;
> 4. the exceptions in §7 are ones I accept, with the owners and dates shown;
> 5. I understand which populations were **deliberately not migrated** and I accept that decision.
>
> Name · Role · Date · Signature

| Domain | Signatory | Countersignatory |
|---|---|---|
| Party, address, contracts, claims | **Chief Commercial Officer** | Master Data Owner |
| Asset, service history, archive | **Service Ops Director** | Master Data Owner |
| Inventory | **Warehouse Manager** | CFO *(valuation)* |
| Finance — all | **CFO** | **External auditor** *(trial balance only)* |
| Tax | **CFO** | Tax consultant |
| People and payroll | **HR Director** | **CFO** |

> **`RV-12`.** No production load is declared complete without the signed form filed as an `M24`
> document, retained for **seven years** for finance and statutory domains (`FO-15`, `NFR-088`).

### 2.8 Cross-workbook reconciliations

Some reconciliations span two workbooks and belong to neither alone. They are declared here so they
are nobody's optional extra.

| # | Reconciliation | Between | Rule |
|:--:|---|---|---|
| X1 | Opening stock value | `DM-007` `IV-08` → `DM-008` `FO-18` | The W2 frozen value appears unchanged as the W3 stock control account |
| X2 | Live claims | `DM-010` `CW-14` → `DM-008` `FO-08` | Migrated live claims are part of the AR open-item population and tie to the control account |
| X3 | Consignment balances | `DM-007` `IV-05` ↔ `DM-010` `CW-13` | Brand-confirmed quantity and the claim-side consignment record agree |
| X4 | Deferred revenue | `DM-010` contracts → `DM-008` `FO-16` | Rebuilt obligation totals reconcile to the contract population |
| X5 | Employee party | `DM-009` → `DM-004` `PM-07` | Every employee is one party with an added role, never a second party |
| X6 | Asset ↔ order | `DM-005` → `DM-006` `SH-13` | Every migrated order's asset resolves; the provisional share is reported |
| X7 | Fixed assets | `DM-005` §2.7 → `DM-008` §2.7 | Physically verified register agrees with the accounting-book opening values |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `load_id` — one per tier per environment per attempt |
| Batch linkage | `migration_batch_id`, written on every loaded row (`MS-18`) |
| Control register key | `control_id` — `RC-<DOMAIN>-nnn`, permanent |
| Report identity | `<load_id>_<domain>_<environment>_<YYYYMMDD>` |
| Retention | Finance and statutory reports **seven years**; others per the `M24` class |
| Reuse policy | A re-run produces a **new** `load_id`. A report is never overwritten |

---

## 4. Validation rules

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `RV-01` | All applicable classes are reconciled; a non-applicable class is stated with its reason | **H** | `ERR-REC-001` |
| `RV-02` | R1 must balance with zero unaccounted records | **H** | `ERR-REC-002` |
| `RV-03` | R5 semantic reconciliation is mandatory on every load | **H** | `ERR-REC-003` |
| `RV-04` | The R5 sample is inspected by the business owner or their nominee, not by the migration team | **H** | `ERR-REC-004` |
| `RV-05` | Control totals are declared before the first load and are not changed afterwards | **H** | `ERR-REC-005` |
| `RV-06` | Every non-loaded record is in exactly one exception category with an owner | **H** | `ERR-REC-006` |
| `RV-07` | Deliberately excluded populations are reported, not omitted | **H** | `ERR-REC-007` |
| `RV-08` | Thresholds are set per domain before the first load by the accountable owner | **H** | `ERR-REC-008` |
| `RV-09` | A threshold miss produces pass, conditional-with-plan, or fail — nothing else | **H** | `ERR-REC-009` |
| `RV-10` | A dry run produces an identical report format to a production run | **H** | `ERR-REC-010` |
| `RV-11` | Sign-off is against the five-point statement, not a bare acknowledgement | **H** | `ERR-REC-011` |
| `RV-12` | No production load is complete without the signed form filed in `M24` | **H** | `ERR-REC-012` |
| `RV-13` | The seven cross-workbook reconciliations (§2.8) are run and reported at their waves | **H** | `ERR-REC-013` |
| `RV-14` | Rollback rehearsal status and measured duration appear in every report (`SQ-08`) | **H** | `ERR-REC-014` |
| `RV-15` | Bengali sample rendering is checked by a native speaker; mojibake fails the load | **H** | `ERR-REC-015` |
| `RV-16` | A semantic defect (E9) rolls back and re-runs; it is never accepted with a remediation plan | **H** | `ERR-REC-016` |
| `RV-17` | Reports are immutable; a correction is a new `load_id` | **H** | `ERR-REC-017` |
| `RV-18` | Reconciliation figures are **enumerated from the loaded data**, never taken from the load script's own counters | **H** | `ERR-REC-018` |

> **`RV-18` is `RG-06` applied to migration.** A loader reporting its own success is a document
> reading what it says about itself. Every figure in the report is produced by querying the target
> and the source independently of the process that moved the data.

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| [`DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md`](DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) | N:1 | R4 evaluates its rules; E1 cites its rule ids |
| [`DM-012_Migration_Load_Template_Pack.md`](DM-012_Migration_Load_Template_Pack.md) | N:1 | `row_count_expected` is an R1 control |
| [`DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md`](DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md) | N:1 | The tier boundary is where the gate sits (`SQ-05`) |
| `DM-004`…`DM-010` | N:1 | Each declares its control totals |
| [`../13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md`](../13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md) | N:1 | Severity language shared with QA. Written 2026-08-18, `Draft`, W1 — **the two severity scales must now be reconciled rather than invented** (`O-02`) |
| `M24` document management | 1:N | Where signed forms are retained |

| Depended on by |
|---|
| [`DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) — the go/no-go reads this report · `06-02` `G1-05`, `G2-06`, `G3-08` · `M33` `AC-13` · `M01` `AC-13` · `RP-016` scorecard baseline |

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | The source extracts and the loaded target, queried **independently** (`RV-18`) |
| Who supplies it | The migration pipeline produces §2–§9; the business owner produces §6 sample results and §10 |
| Collection method | **Enumeration** (`RG-06`, `CP-11`) — never the loader's own counters |
| Known quality issues | R5 cannot be fully automated and is therefore the class most at risk of being skipped under cutover time pressure |
| Cleansing rules applied | n/a — this file reports on cleansing, it does not perform it |
| Re-verification | Every load, every environment |

---

## 7. Volumes

| Item | Count |
|---|---:|
| Reconciliation classes | 5 |
| Exception categories | 9 |
| Domains with declared control totals | 13 |
| Cross-workbook reconciliations | 7 |
| Signatory roles | 7, plus 2 external countersignatories |
| Reports per wave *(dry run + production, per tier)* | **≥ 20 at W1**, more at W3 |
| Retention | 7 years for finance and statutory; per `M24` class otherwise |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add a control | The domain's business owner, through the Data Migration Lead |
| Who may change a threshold | **Only before the first load**, by the accountable owner, recorded in `RF-006` |
| Approval required | CFO for any finance tolerance; Master Data Owner for any structural change |
| Effective dating | Not effective-dated; controls are versioned per wave |
| Archive rule | Reports are **immutable and retained**, never amended (`RV-17`) |
| Logged in | `RF-006`; signed forms in `M24` |

---

## 9. Sample rows

`DM-013_Reconciliation_Control_Register.csv`:

```csv
control_id,domain,class,control_name,source_query_ref,target_query_ref,tolerance,signatory_role,wave,active
RC-PARTY-001,party,R1,Source equals loaded plus rejected plus excluded,SRC-008 row count,fix.party where migration_batch_id,0 unaccounted,Chief Commercial Officer,W1,TRUE
RC-PARTY-004,party,R5,Segment distribution source versus target,SRC-008 group by category,fix.party group by segment_code,declared per file,Chief Commercial Officer,W1,TRUE
RC-ASSET-002,asset,R2,Identity confidence split reported,n/a,fix.asset group by identity_confidence,report only,Service Ops Director,W1,TRUE
RC-FIN-001,finance,R2,Total debits equal total credits,trial balance,account.move.line sum,exact,CFO,W3,TRUE
RC-FIN-004,finance,R2,AR open item total equals receivable control account,AR ageing,fix.ar.open.item sum,exact,CFO,W3,TRUE
RC-HR-002,hr,R2,YTD tax per employee equals reconciled source,payroll workbook per employee,fix.payroll.balance per employee,exact,HR Director,W5,TRUE
RC-INV-003,inventory,R2,Counted quantity versus spreadsheet variance reported as baseline,SRC-006 quantity,fix.stock.quant quantity,report only,Warehouse Manager,W2,TRUE
```

---

## 10. Migration notes

**This specification is what makes three wave gates auditable.**

| Gate | Criterion | Evidence this file produces |
|---|---|---|
| `G1-05` | Customer and device data migrated and reconciled | The party and asset reports, signed by the CCO and the Service Ops Director |
| `G2-06` | Inventory accuracy ≥ 95% at migrated locations, verified by count | The inventory report, including the `IV-03` variance baseline |
| `G3-08` | Financial history migrated and reconciled to the trial balance | The GL, AR/AP, cash and tax reports, signed by the CFO with the external auditor |

**The most likely failure of this file is not that it is wrong — it is that R5 gets skipped.** Under
cutover pressure, at 03:00, with a window closing, the class that requires a business owner to sit
and read twenty records is the one that gets deferred to "the morning". `RV-03` makes it mandatory
and `RV-16` makes an E9 defect a rollback rather than a remediation item, because a semantic error
discovered in the morning has already been transacted against.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md`](DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) | The rules R4 evaluates and E1 cites |
| [`DM-012_Migration_Load_Template_Pack.md`](DM-012_Migration_Load_Template_Pack.md) | `row_count_expected` and template versions in the report header |
| [`DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) | The go/no-go decision this report feeds |
| [`DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md`](DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md) | The exact-tolerance finance controls |
| [`DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md`](DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md) | The `IV-03` variance that becomes the `RP-016` baseline |
| [`../13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md`](../13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md) | Shared severity language. Category 13 completed 18 of 18 on 2026-08-18 |
| `RP-016` Data Quality Scorecard | Continues these measures after go-live — **unwritten; Category 14 held zero files at enumeration 2026-08-18** |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Five reconciliation classes with R1 as an identity and R5 mandatory, nine exception categories, thirteen domain control-total sets, a five-point sign-off statement, seven cross-workbook reconciliations, and independent enumeration required (`RV-18`) | CFO (pending) |

---

## 13. Open items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **No thresholds have been set**, because no source has been profiled (`DM-011` `O-02`). `RV-08` requires them before the first load and `RV-05` forbids changing them afterwards | Domain owners with Data Migration Lead | **W1 — before the first load** |
| **`O-02`** | **`TS-018` now exists** (written 2026-08-18, `Draft`, W1) and **the two severity scales have not been reconciled.** This file classifies migration exceptions `E1`–`E9`; `TS-018` classifies test defects on its own severity and triage scale. A go/no-go conversation that mixes an `E1` rejection with a Severity-1 defect is a conversation about two different things | QA Lead with Data Migration Lead | **W1 — reconcile, no longer author** |
| **`O-03`** | **R5 sampling capacity is unresourced.** Every domain owner must read a stratified sample inside the cutover window. Nobody has estimated the time or named the nominees | Data Migration Lead with domain owners | **W1 minus 1 month** |
| **`O-04`** | **The external auditor has not been engaged** on the opening trial balance. `M19` §16.4 requires the TB *agreed with the external auditor*, and §2.7 makes them a countersignatory | CFO | **W3 minus 3 months** |
| **`O-05`** | **`RV-14` requires a measured rollback duration** in every report, and no rollback has been rehearsed (`DM-003` `O-04`). Until one is, every report carries an unanswerable field | Data Migration Lead with CTO | **W1** |
| **`O-06`** | **`RP-016` is unwritten** *(enumerated 2026-08-18; Category 14 held zero files)*, so the post-migration continuation of these measures has no owner. `IV-03`'s variance baseline and the asset confidence split are both designed to feed it | BI Lead with Master Data Owner | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; the report-specification adaptation is **declared**
- [x] **Five reconciliation classes**, with R1 defined as an identity that must balance to zero residual
- [x] **R5 semantic reconciliation made mandatory** and specified in enough detail to be executed
- [x] R5 inspection assigned to the business owner, not the migration team (`RV-04`)
- [x] Thirteen domains given explicit control totals, adopting the module set's stated thresholds rather than re-deriving them
- [x] **Nine exception categories**, each with owner, disposition and gate consequence
- [x] Deliberately excluded populations required to be reported (`RV-07`)
- [x] Threshold outcomes restricted to pass / conditional-with-plan / fail
- [x] Report structure fixed so dry runs and production runs are comparable
- [x] **Sign-off written as a five-point statement**, not an acknowledgement, with signatories and countersignatories per domain
- [x] **Seven cross-workbook reconciliations declared** so no seam is nobody's job
- [x] Independent enumeration required — the loader may not report its own success (`RV-18`, `RG-06`)
- [x] Sample control-register rows included and parse as CSV
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2; **Bengali render check is `RV-15`**
- [ ] **`O-01` no thresholds set — `RV-08` blocks the first load**
- [ ] **`O-03` R5 sampling capacity unresourced — the class most likely to be skipped**
- [ ] **`O-04` external auditor not engaged**
- [ ] Named approver recorded — **pending CFO with Data Migration Lead**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
