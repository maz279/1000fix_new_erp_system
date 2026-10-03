---
id: MG-002
title: Legacy System Profiling and Extract Specification
category: 09 — Data Migration & Cutover
code: MG
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration Lead
approver: Chief Technology Officer
standards_basis: >
  ISO/IEC 25012:2008 — data quality model (inherent characteristics) · ISO 8000-61:2016 —
  data quality planning and control · PDMv2 (Practical Data Migration, BCS 2012) — Landscape
  Analysis and Data Quality Rules · DAMA-DMBOK 2.0 Ch. 13 §2.3 — data profiling
traces_to: >
  PGD-000 MG-002 · AUDIT-011 DM-03 (HIGH) · GV-005 ISS-006 (Critical) · GV-009 G1-05 ·
  BRD MIG-002, MIG-011 · 05-02 §12 MIG-01 · M33 §16.4 rule 1 · 00-04 ASM-03, RSK-014, DEP-05 ·
  DM-002 (48 sources) · DM-011 profiling dimensions
depends_on: MG-001 · DM-001 · DM-002 · DM-011 · DA-005 · SC-007 · SC-010
verified_on: 2026-08-18
priority: P0
needed_by: Now
enumeration_timestamp: 2026-08-18 22:20 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# MG-002 — Legacy System Profiling and Extract Specification

### Category 09 · Code `MG` · ISO/IEC 25012 · ISO 8000-61:2016 · PDMv2 · DAMA-DMBOK 2.0

---

> **Local rule prefix: `LPX-nn`.** Verified unused across the workspace at 2026-08-18 22:20 (+06).
> The `MG-nn` space is `DA-001` §12 / `AR-007` schema-change rules and is **not** used here — see
> `MG-001`'s identifier notice.

---

## 1. Purpose

**Forty-eight legacy sources are registered. Nobody has looked inside any of them.**

`DM-002` inventories the estate — 48 sources across eight classes, with custodians, access
constraints and known issues. Every one of them carries `profiling_status = not_started`, enumerated
2026-08-18 and confirmed unchanged at this issue. `AUDIT-011` `DM-03` records it as **HIGH**;
`GV-005` `ISS-006` records it as **Critical**, open; `GV-009` marks gate criterion `G1-05` **at
risk** for the same reason.

Three independent authorities forbid a load before profiling — `05-02` `MIG-01`, BRD `MIG-002`, and
`M33` §16.4 rule 1 — and the estate implements all three as hard rules (`MS-04`, `DQ-02`, `SI-01`,
`PM-16`). **The result is that every load in the programme is currently blocked, and the thing that
unblocks them has no specification.** This document is that specification.

It states what "profiled" means, how each of the eight source classes is measured, what an extract
must contain to be admissible, how its integrity is proven, and in what order the 48 are done.

### 1.1 Why this is the highest-leverage document in the category

| Blocked today | Unblocked by profiling | Named in |
|---|---|---|
| Every one of the seven mapping workbooks — written against **assumed** structure | Measured structure, so the mappings become specifications | `MST-13`; `AUDIT-011` `DM-03` |
| The `DM-011` match thresholds — unset, and their review queue unsized | A measured duplicate rate, so the queue can be priced before a threshold is set | `AUDIT-011` `DM-04`; `DQ-14`, `DQ-16` |
| The migration-execution estimate — excluded from `GV-007` as unknowable | Volumes and quality per source | `GV-007` §7.3; `MST-28` |
| `ASM-03` — the assumption that customer and device data is exportable at **≥ 80% quality** | The test of the assumption. Nothing has tested it | `00-04` `ASM-03`; `RSK-014` High/High |
| The device population, known only to a **factor of two** (300,000–600,000) | A count | `M17` §16.4 |
| The W1 cutover window arithmetic | Row counts to divide by throughput | `MG-005`, `MG-006` |

> **`LPX-01` — profiling is not a phase, it is a gate.** No source proceeds to extract, no workbook
> proceeds to build, and no wave-gate migration criterion is submitted, until the source's profile
> report is **accepted by its data owner** (§7.4). `DM-002` `SI-01` already blocks the extract; this
> document defines the acceptance that releases it.

### 1.2 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The definition of "profiled" and its acceptance test (§3) |
| 2 | The profiling dimensions and their measures, mapped to ISO/IEC 25012 (§4) |
| 3 | A profiling method **per source class** — including the four classes that cannot be profiled by software (§5) |
| 4 | Encoding discovery and Bengali normalisation (§6) |
| 5 | The extract specification: manifest, integrity proof, chain of custody, delivery (§7) |
| 6 | Freeze points, delta extraction and re-extraction rules (§8) |
| 7 | The profiling programme: sequence, critical path, effort model (§8.4, §9) |
| 8 | Personal data and residency during profiling and extract (§10) |
| 9 | The profile report specification (§11) |
| 10 | Rules `LPX-01`…`LPX-43` (§12) |

**Explicitly out of scope**

| Topic | Owned by |
|---|---|
| The source register itself — which sources exist, custodians, access constraints | **`DM-002`** |
| Which datasets from a source are in scope | **`DM-001`** dispositions |
| Cleansing, matching, survivorship, thresholds | **`DM-011`**; executed by **`MG-003`** §9 |
| Field-level mapping | `DM-004`…`DM-010` |
| Transformation and load | **`MG-003`** |
| Reconciliation of the load | **`MG-004`** |
| Post-go-live quality measurement | `DA-008`; `RP-016` |
| Legacy retirement after extract | `RL-006` ⛔ |

### 1.3 Intended audience

| Audience | Use |
|---|---|
| **Data Migration Lead** | §8.4 sequence; §9 effort; the whole document is the S1 stream's method |
| **Source custodians** (14 named roles in `DM-002`) | §5 — what will be asked of them, and how much of their time |
| **Domain owners** (CCO, CFO, HR Director, Service Ops Director) | §7.4 — what they are accepting when they accept a profile |
| **Migration engineers** | §4 measures; §6 encoding; §7 extract format |
| **Head of InfoSec / DPO** | §10 — profiling is processing |
| **PMO / `GV-007`** | §9 — the effort model that replaces "unknowable" |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure |
|---|---|---|---|
| **ISO/IEC 25012:2008** | Inherent characteristics: accuracy, completeness, consistency, credibility, currentness | §4 measures map one-to-one; each measure states its formula | ISO/IEC 25012 also defines *system-dependent* characteristics (availability, portability, recoverability). Not profiled — they describe the target, not the source |
| **ISO 8000-61:2016** | *Data quality planning* (7.2) and *data quality control* (7.3) | §3 acceptance is planning; §11 report is control output | The *improvement* process (7.5) belongs to `DA-008`, post-go-live |
| **DAMA-DMBOK 2.0** | Ch. 13 §2.3 Data Profiling; Ch. 8 Data Integration | §4 column/table/cross-table profiling structure | DMBOK assumes machine-readable sources. §5.5–5.8 extend it to paper, email, portals and people, which DMBOK does not cover |
| **PDMv2** (BCS, 2012) | Landscape Analysis; Data Quality Rules | `DM-002` is Landscape Analysis; this document is the measurement arm | PDMv2's *System Retirement Plans* are `RL-006`, not here |
| **BRD `MIG-002`** | Profiling before every load, reported to the data owner | §7.4 acceptance names the owner per source | — |
| **BRD `MIG-011`** | Bengali conversion and UTF-8 normalisation | §6 | — |

> **DMBOK does not profile paper.** Twelve of 48 sources are physical documents and three are human
> knowledge. Every commercial profiling tool assumes a queryable source. §5.5–5.8 specify what
> profiling means where no software can run, because the alternative — declaring them out of scope —
> is how 500,000+ paper records become a W3 surprise.

### 2.2 The measured shape of the estate

Counted from `DM-002` §2.1 and §2.2 on 2026-08-18 22:20 (+06). **This distribution is the single
most important input to the plan.**

| Class | Sources | Machine-profilable? | Constraint |
|---|---:|:--:|---|
| `DB` Application databases | **4** | ✔ | Undocumented schemas; vendor access |
| `SS` Spreadsheet estate | **14** | Partly | **Collection across 51+ branches** |
| `PORTAL` Third-party portals | **5** | ✘ | Rate-limited; no bulk export |
| `MAIL` Email as record system | **2** | ✘ | Human triage of threads |
| `PAPER` Physical records | **12** | ✘ | Sampling only; highest cost per record |
| `PEOPLE` Human knowledge | **3** | ✘ | An authoring programme, not an extract |
| `PUB` Published registers | **4** | ✔ | Version pinning; adviser verification |
| `CFG` Configuration/credentials | **4** | ✔ | Survey; nothing is carried |
| **Total** | **48** | **12 of 48** | |

> **`LPX-02`.** **Thirty-six of forty-eight sources cannot be profiled by running a query.** Any
> plan, tool selection or estimate that assumes otherwise is wrong by a factor of three. This is the
> arithmetic behind `MG-001` §11.2 and it is why §9's effort model is dominated by custodian
> availability rather than compute.

### 2.3 Findings this document addresses

| Finding | Source | Position |
|---|---|---|
| `AUDIT-011` `DM-03` — every load blocked; 48 sources unprofiled | `AUDIT-011` | **Specified here; performed by the S1 stream.** §8.4 sequences it, §9 sizes it |
| `GV-005` `ISS-006` — Critical, open | `GV-005` | The remediation path is this document plus funding (`Q-02`) |
| `AUDIT-011` `DM-04` — match thresholds unset, queue unsized | `AUDIT-011` | §4.4 makes the duplicate measure a **mandatory** profiling output, so the queue can be sized before a threshold is chosen |
| `GV-009` `G1-05` at risk | `GV-009` | §8.4 places the `G1-05` sources first |
| `00-04` `ASM-03` — ≥ 80% quality assumed, untested | `00-04` | §11.3 makes the assumption an explicit line in every profile report, tested rather than carried |

---

## 3. What "Profiled" Means

**`LPX-03`: a source is profiled when all six conditions hold. Fewer than six is `in_progress`.**

| # | Condition | Evidence |
|:--:|---|---|
| 1 | Every **dataset** the source contributes (per `DM-001` §4.2) has been located inside it | A dataset-to-source-object map |
| 2 | Its **structure** is recorded as observed, not as described | A schema listing, a column inventory, or a documented sample structure for non-machine sources |
| 3 | Its **volume** is counted, not estimated — or, where counting is impossible, **sampled with a stated confidence interval** | A row/record count with its method |
| 4 | The **six measures** of §4 are computed for every in-scope field | The profile report §3 |
| 5 | Its **encoding** is observed and recorded | §6; `DM-002` `encoding_observed`; `SI-04` |
| 6 | The report is **accepted by the named data owner** | A signed acceptance, §7.4 |

> **`LPX-04` — "estimated" is a permitted answer and "unknown" is not.** Twelve `PAPER` sources
> cannot be counted exhaustively; a sampled estimate with a stated method and interval satisfies
> condition 3. What does not satisfy it is `DM-002`'s current *"to be profiled"* and *"TBD"*, which
> appear against `SRC-001`, `SRC-002` and `SRC-026`, the three largest unknowns in the estate.

> **`LPX-05` — profiling measures the source, never the target.** A profile that reports how well
> the source fits `DA-001` is a *mapping assessment* and belongs in the workbook. Mixing the two
> hides source defects behind mapping decisions.

### 3.1 The five profiling statuses

`DM-002` declares the enum; this document defines the transitions.

| Status | Meaning | Entry condition | Who sets it |
|---|---|---|---|
| `not_started` | Nothing done | Default | — |
| `in_progress` | Access obtained; measurement under way | Custodian engaged; access constraint cleared | Migration analyst |
| `reported` | All six §3 conditions 1–5 met; report issued | Report published to the data owner | Data Migration Lead |
| **`accepted`** | The data owner has accepted the report | Signed acceptance (§7.4) | **Data owner** |
| `superseded` | A material change re-opened it | §8.5 trigger fired | Data Migration Lead |

> **`LPX-06`.** `SI-01` blocks extract on `not_started`. **This document raises the bar: extract
> requires `accepted`, not `reported`.** A report nobody read is not a control. Recorded as decision
> `MG-002-D-01`; it is a deliberate tightening of `DM-002` `SI-01` under `MST-02` (technical
> mechanism), and `DM-002` should be updated to match — raised as `Q-05`.

---

## 4. Profiling Dimensions and Measures

`DM-011` §2.2 selects the profiling dimensions and `DA-008` §3 maps four of them to ISO/IEC 25012.
Under `MST-04` those are adopted, not re-derived. **This section supplies what neither states: the
formula, the unit and the acceptance line for each.**

### 4.1 The six measures

| # | Measure | ISO/IEC 25012 | Formula | Unit | Reported per |
|:--:|---|---|---|---|---|
| **P1** | **Completeness** | Completeness | `non_null_and_non_blank / applicable_rows` | % | Field |
| **P2** | **Validity** | Syntactic accuracy | `rows_passing_the_field_rule / non_null_rows` | % | Field × rule |
| **P3** | **Uniqueness / duplication** | Uniqueness | `1 − (duplicate_candidate_records / population)` | % + **candidate count** | Entity |
| **P4** | **Consistency** | Consistency | `rows_where_the_cross_field_rule_holds / rows_where_it_applies` | % | Rule |
| **P5** | **Currentness** | Currentness | Distribution of `last_modified` or the best available proxy | Histogram | Dataset |
| **P6** | **Credibility** | Credibility | Agreement rate against an independent source, where one exists | % + source named | Field |

> **`LPX-07` — P3 reports a count, not only a rate.** `AUDIT-011` `DM-04` shows why: a 15% duplicate
> rate on 100,000 parties is meaningless to a resourcing decision, while *"an estimated 4,900
> candidate pairs land in the 0.80–0.95 review band"* is a staffing number. **`DQ-16` requires the
> review-queue size to be computed and accepted before a threshold is set; P3's candidate count is
> the only input that makes that possible.**

> **`LPX-08` — P6 is reported as "no independent source" where none exists, never omitted.** For
> `SRC-008` (customer master) there is no second source; for `SRC-021` (bank portals) the bank's own
> statement **is** the independent source and outranks the book (`M50` §16.4). The asymmetry matters
> and disappears if P6 is silently skipped.

### 4.2 Profiling levels

DMBOK's three levels are used unchanged, because the defects they find are different.

| Level | What is examined | Finds |
|---|---|---|
| **L1 — Column** | One field at a time: null rate, distinct values, min/max, length, pattern, frequency | Format drift, unexpected sentinels (`0000-00-00`, `N/A`, `-`), truncation |
| **L2 — Table** | Field combinations within a record | Broken cross-field rules; a *"closed"* order with no closure date; a warranty ending before it started |
| **L3 — Cross-table / cross-source** | Relationships between datasets and across sources | Orphans; the same customer in three spreadsheets under three names; a device with no owner |

> **`LPX-09` — L3 is mandatory across sources, not only within one.** The estate has **no system
> integration at all** (BRD §6.1). The same customer exists independently in `SRC-003`, `SRC-005`,
> `SRC-008` and `SRC-009` with no key connecting them. **An L1-and-L2-only profile will report four
> clean sources and miss that they describe one population.** This is the defect that determines the
> real W1 party volume, and it is invisible to per-source profiling.

### 4.3 Sentinel and null-equivalent discovery

**`LPX-10`: the null-equivalent set is discovered per source, never assumed.** Spreadsheet estates
maintained by 51 branches over years accumulate their own conventions for "no value".

| Class of sentinel | Examples observed in spreadsheet estates | Treatment |
|---|---|---|
| Textual nulls | `N/A`, `NA`, `-`, `--`, `nil`, `none`, `unknown`, `?`, `TBA` | Registered and counted as null in P1 |
| Zero-as-absent | `0` in a price or quantity column where zero is not a real value | Flagged; **the data owner decides**, not the analyst |
| Impossible dates | `0000-00-00`, `1900-01-01`, `1970-01-01` | Registered as null; **the epoch dates specifically indicate a prior failed conversion** |
| Placeholder identity | `01700000000`, `test`, `abc`, repeated single digits in a mobile column | Counted separately — these fail validity **and** signal a data-entry workaround |
| Bengali textual nulls | Bengali equivalents of "none"/"unknown" | Registered; requires a Bengali reader (§6.3) |

> The sentinel register per source is an output of profiling and an input to `MG-003` §7's
> transformation rules. A sentinel discovered at load time is a defect found in the wrong place.

### 4.4 Mandatory measures by domain

Not every measure matters everywhere. **`LPX-11`: these combinations are mandatory and may not be
waived**, because a named downstream decision depends on each.

| Domain | Mandatory measures | The decision that depends on it |
|---|---|---|
| **Party / customer** | P1, P2, P3 **with candidate count**, P5 | The `DM-011` match threshold and its queue (`DQ-14`, `DQ-16`); `ASM-03` |
| **Device / asset** | P1, P3, **the population count** | The 300,000–600,000 uncertainty; the provisional-identity burn-down (`M17`) |
| **Service history** | P1, P5, L3 to party and asset | The archive/live split; `M01` `Q-04` historical depth |
| **Inventory** | P1, P2 — **and no P3** | Counted, not loaded (`M15`). Profiling measures the **spreadsheet**, to size the variance, not to load it |
| **Finance** | P1, P2, P4, **P6 against the trial balance and bank statements** | `G3-08`; the opening TB (`M19`, `M50`) |
| **HR / payroll** | P1, P2, P4, P6 against payslips | `G5-01`; YTD exactness (`M56`) |
| **Contracts / claims** | P1, P5, **evidence-rung distribution** | The `CW-01` evidence rungs; the claim write-off exposure (`M09`) |
| **Catalogue / pricing** | P1, **P3 — the 30–40% duplication estimate**, P4 across 51 branch sheets | `M37`'s W1 task; the `M11` price-conflict escalation to the CCO |

> **Note the inventory row.** `M15` refuses to load the spreadsheets, so profiling them might look
> pointless. It is not: the **spreadsheet-versus-count variance** is `DM-013`'s declared baseline
> measurement (`IV-03`), and it cannot be computed unless the spreadsheet was profiled before the
> count. Profiling a source that will never be loaded is correct here, and the reason must be
> written down or someone will optimise it away.

---

## 5. Profiling Method by Source Class

### 5.1 `DB` — application databases (4 sources)

| Step | Action | Output |
|:--:|---|---|
| 1 | Obtain a **read-only** credential and a schema dump. `SRC-001` and `SRC-002` require hosting-vendor access — the longest-lead access constraint in the estate | Connection; DDL |
| 2 | Inventory tables, columns, types, keys, indexes **as they exist**, not as documented | Structure listing |
| 3 | Run L1 on every in-scope column; L2 on every declared and inferred record rule; L3 across tables | Measures P1–P4 |
| 4 | Determine `last_modified` availability; where absent, find a proxy (an insert-ordered key, an audit table) | P5, with the proxy named |
| 5 | Detect encoding per text column (§6) | `encoding_observed` |
| 6 | Take a **full point-in-time extract immediately**, not at the wave — see `LPX-12` | An archived extract with a manifest |

> **`LPX-12` — `SRC-001` and `SRC-002` are extracted at profiling time, not at load time.** BRD §6.5
> withdraws both at **W2**; `DM-002` §10 records that they are *"the only two sources in the estate
> that could be re-extracted after decommission — and they cannot"*. **A full extract is taken and
> archived at first contact**, before any decision about what is in scope, because the cost of
> storing an unnecessary extract is trivial against the cost of an unavailable one. This is the only
> place in this category where extraction precedes scoping, and it is deliberate.

### 5.2 `SS` — the spreadsheet estate (14 sources, 51+ files each in several cases)

**The hard part is collection, not parsing.** `DM-002` says so; §9 prices it.

| Step | Action | Note |
|:--:|---|---|
| 1 | **Collection round** — a request to each custodian, tracked per branch | 51+ replies for `SRC-005`, `SRC-006`, `SRC-011`; **the response rate is the schedule** |
| 2 | Register **every file received** with its origin, filename, size, sheet count and modification date | A file arriving without a recorded origin is unusable — `LPX-13` |
| 3 | **Structural clustering** — group the files by column signature | 51 branch files are rarely 51 formats; they are typically 4–8 variants. The variant count is the mapping effort |
| 4 | Profile **per variant**, then aggregate to the source | Profiling each file separately produces 51 reports nobody reads |
| 5 | Detect merged cells, multi-row headers, embedded totals, hidden sheets, formulas-as-values | These break naive parsers silently, producing shifted columns rather than errors |
| 6 | L3 across variants and across sources (`LPX-09`) | The real population |

> **`LPX-13`.** Every collected file carries an **origin record** — branch, custodian, date received,
> file hash. A spreadsheet whose branch is unknown cannot be reconciled to a branch's opening
> position, and at 51 branches that is not a hypothetical.

> **`LPX-14` — the collection round starts before the profiling method is finalised.** Collection is
> elapsed-time bound and measurement is effort-bound. Waiting for a perfect method before asking 51
> branch managers for their files spends the scarcest resource — calendar — on the cheapest activity.

### 5.3 `PORTAL` — third-party portals (5 sources)

| Step | Action |
|:--:|---|
| 1 | Confirm access per portal — **17+ brand portals for `SRC-019` alone**, each with its own credentials and its own owner |
| 2 | Establish whether **any** bulk export exists. Where it does not, profiling is by **paged manual sampling** |
| 3 | Sample to a stated confidence interval; record the sampling frame and the rate limit encountered |
| 4 | For `SRC-020` and `SRC-021`, obtain the **provider's own written statement of balances** — the provider is the authority, not our record (`M50` §16.4) |

> **`LPX-15`.** For a `PORTAL` source, the profile records the **extraction rate achieved** (records
> per hour, given the rate limit) as a first-class output. `MG-006`'s cutover window arithmetic needs
> it, and it cannot be inferred later.

### 5.4 `MAIL` — email as a record system (2 sources)

| Step | Action |
|:--:|---|
| 1 | Export the mailbox or folder to a preserved format with headers intact |
| 2 | **Thread reconstruction** — a claim is a conversation, not a message (`SRC-024`) |
| 3 | Sample-triage to establish: how many threads represent a distinct record; what proportion carry an attachment that *is* the record; what proportion are unresolvable |
| 4 | Report the **unresolvable proportion** as a headline figure |

> **`LPX-16`.** For `SRC-024`, the unresolvable proportion is a **financial exposure**, not a data
> quality statistic: BRD §6.2 process 7 attributes **15–20% revenue leakage** to claims lost in
> threads. The profile reports it in currency as well as in percent, to the Finance Director.

### 5.5 `PAPER` — physical records (12 sources)

**No software runs here.** Profiling is a physical survey.

| Step | Action | Output |
|:--:|---|---|
| 1 | **Locate** — which cabinet, which branch, which store. `SRC-026` is *"physical archive at branch and central store"*, which is 52 locations | A location inventory |
| 2 | **Measure the extent** — linear metres of file, number of boxes, number of books. Convert to a record estimate using a **counted sample of a representative unit** | Volume ± interval |
| 3 | **Condition survey** — legibility, completeness, water/insect damage, Bengali handwriting proportion | A condition grade per location |
| 4 | **Structure sample** — read 30–50 documents per format; record which fields are reliably present | A field-presence profile |
| 5 | **Retention check** — what must be retained physically for legal reasons even after scanning (`SRC-031`) | A retention flag per class |

> **`LPX-17` — a `PAPER` profile reports metres and boxes before it reports records.** A record
> estimate derived from a linear measurement and a counted sample is defensible; a record estimate
> derived from someone's recollection is the `500,000+ (to be profiled)` figure currently in
> `DM-002`, which has been carried unchallenged since the module specifications were written.

> **`LPX-18`.** The `PAPER` condition survey is the input to `M24`'s digitisation-by-priority-of-need
> rule. A source in poor condition is digitised **earlier**, not later, because its content is
> decaying — the opposite of a priority ordering based on business need alone.

### 5.6 `PEOPLE` — knowledge held by people (3 sources)

**These are not extracts and calling them extracts is the error.** `DM-002` says so; `DM-001`
dispositions them `N` — author new.

| Source | What "profiling" means here | Output |
|---|---|---|
| `SRC-038` Supervisor knowledge of technician competency | **Design and pilot the assessment instrument**; measure how long one supervisor takes to assess one technician; count supervisors and technicians | An elapsed-time model for 500+ assessments |
| `SRC-039` Delegation-of-authority limits in current practice | Interview the CFO and finance team; **surface disagreements**, which are the actual finding | A draft limit set with contested items marked |
| `SRC-040` Statutory obligation knowledge | Structured elicitation with finance and HR; cross-check against `SC-008` | An obligation list with confidence per item |

> **`LPX-19`.** A `PEOPLE` source's profile output is an **effort and elapsed-time model**, not a
> data quality measure. Its purpose is to let `GV-004` schedule the authoring programme. `M65` calls
> `SRC-040` *"the highest-value non-software deliverable"*; it is currently in no plan.

### 5.7 `PUB` — published external registers (4 sources)

| Step | Action |
|:--:|---|
| 1 | Obtain the published artefact and **pin its version** (`CG-006` §5; `DM-002` `SI-09`) |
| 2 | Verify completeness against the publisher's stated counts — 8 divisions / 64 districts / ~495 upazilas for `SRC-041` |
| 3 | For `SRC-043` (NBR pack) and payroll slabs, record that **verification is by an engaged adviser** and is a `G6` gate item |
| 4 | Record the publication date and the next expected revision |

> **`LPX-20`.** A `PUB` source is *loaded as fact* and therefore profiled for **currency and
> completeness only**. Its accuracy is the publisher's, not ours — but `AUDIT-011` `DM-09` records
> that **no tax adviser is engaged**, so `SRC-043`'s verification gate is unperformed and both
> `MD-037` and `MD-043` are blocked behind it. Profiling cannot fix that; it can stop it being
> forgotten.

### 5.8 `CFG` — configuration and credential stores (4 sources)

| Step | Action |
|:--:|---|
| 1 | **Survey, do not extract.** A credential store is inventoried by count and location, never copied |
| 2 | Count credentials by type and system; identify anything in plain text |
| 3 | For `SRC-048` (cron jobs), enumerate every scheduled job with its schedule, owner and last-success evidence |
| 4 | Record the rotation/reset plan per credential class |

> **`LPX-21` — a `CFG` profile never records a credential value, in any artefact, including this
> one.** `M28` §16.4's position stands: anything held in plain text is assumed compromised and is
> rotated on migration (`MS-25`). The profile records *that* a credential exists and *where*, and
> nothing more. A profile report containing a password is a security incident.

---

## 6. Encoding and Bengali Normalisation

### 6.1 Why this has its own section

BRD `MIG-011` and `05-02` `DM-09` require UTF-8 at the target; `DM-001` `MS-26` requires
normalisation **at extract, before any matching or loading**. `DM-002` requires `encoding_observed`
to be *observed, not assumed*, and `SI-04` rejects an extract with an undeclared encoding.

**None of them says how to observe it**, and getting it wrong is silent: a mis-decoded Bengali name
matches nothing, deduplicates against nothing, and prints as mojibake on an invoice three years
later.

### 6.2 The method

| Step | Action | Rule |
|:--:|---|---|
| 1 | **Detect per file and per column**, not per source. A 51-file spreadsheet estate routinely carries several encodings | `LPX-22` |
| 2 | Candidate set: UTF-8, UTF-8 with BOM, UTF-16LE/BE, Windows-1252, ISO-8859-1, and **legacy Bengali fonts encoded as Latin bytes** (Bijoy/ASCII-mapped) | — |
| 3 | Confirm by **rendering a sample and having a Bengali reader confirm it**, never by a detector's confidence score alone | `LPX-23` |
| 4 | Normalise to **UTF-8, Unicode NFC** at extract; record the source encoding in the manifest | `LPX-24` |
| 5 | Re-run P1/P2 **after** normalisation; a value that was invalid because it was mis-decoded is not a data defect | — |

> **`LPX-23` — automatic detection is not sufficient for Bengali.** Legacy Bengali content encoded
> with a Bijoy-style ASCII font mapping is **valid Windows-1252** at the byte level. Every detector
> will report it as correctly decoded Latin text. It is only recognisable by a human reading the
> rendered output and seeing nonsense. `DM-013` `RV-03` already requires a native speaker for the
> post-load render check; **this document requires one at profiling too**, which is three years
> earlier and far cheaper.

> **`LPX-24` — normalise to NFC and record it.** Bengali conjuncts and vowel signs have multiple
> Unicode representations that compare unequal byte-wise. Two identical-looking names in NFC and NFD
> will not deduplicate. `05-02` `DM-09` mandates `bn_BD` collation at the target; NFC at extract is
> what makes that collation meaningful.

### 6.3 Mixed-script fields

| Situation | Position |
|---|---|
| A name field containing Bengali and Latin in the same value | Preserved as-is; **not transliterated**. `DA-002` carries the bilingual field pattern |
| A numeral field containing Bengali digits (০–৯) | **Normalised to ASCII digits** for any numeric or identifier field; preserved where the field is display text (`BN-007` numerals convention) |
| An address in Bengali with an English district | Preserved; geography resolution is by `MD-006` code, not by string match |

---

## 7. The Extract Specification

### 7.1 What an extract is

**`LPX-25`: an extract is a point-in-time, immutable, manifested copy of a source, taken by a
recorded procedure, with an integrity proof.** A file emailed by a branch manager is a *file*, not
an extract, until it has been registered under §7.2.

### 7.2 The extract manifest — mandatory fields

Every extract, of every class, carries a manifest. Machine-produced extracts generate it; manual
collections have it completed by the receiving analyst.

| Field | Type | Why |
|---|---|---|
| `extract_id` | `EXT-nnnnn` | The unit of lineage; referenced by `migration_batch_id` |
| `source_id` | → `DM-002` `SRC-nnn` | The source |
| `source_object` | text | Table, file name, mailbox folder, cabinet reference |
| `extract_instant` | timestamptz | **Exact `Asia/Dhaka` instant**, stored UTC (`05-02` `DM-08`) |
| `extract_method` | enum | Per `DM-002` §2.1 |
| `operator_role` | text | Who took it |
| `record_count` | bigint | **Counted at extract**, by the extractor |
| `byte_size` | bigint | |
| `content_hash` | `sha256` | The integrity proof, §7.3 |
| `encoding_source` | text | As observed (§6) |
| `encoding_delivered` | text | Always `UTF-8/NFC` after normalisation |
| `is_full_or_delta` | enum | `full` / `delta` |
| `delta_since` | timestamptz | Null for `full` |
| `contains_personal_data` | bool | Drives §10 handling |
| `sensitivity_max` | enum `S0`–`S3` | From `DM-002`; drives storage location |
| `chain_of_custody_ref` | text | §7.5 |
| `profile_report_ref` | text | The accepted profile this extract corresponds to |

> **`LPX-26` — an extract with no manifest may not be loaded, staged, or profiled.** It is quarantined
> until a manifest is completed or it is destroyed. This is the rule that makes `DM-013` `RV-02`'s
> R1 identity computable at all: *source = loaded + rejected + excluded* requires an authoritative
> source count, and the manifest is where it comes from.

### 7.3 Integrity

| # | Rule |
|---|---|
| `LPX-27` | Every extract file carries a **SHA-256 hash computed at the point of extraction** and re-verified on arrival in `migration-staging`. A mismatch quarantines the extract |
| — | The manifest itself is hashed and stored separately from the extract |
| — | Extracts are **immutable**. A correction produces a **new** `extract_id`; the superseded extract is retained and marked, never overwritten |
| — | Hashes and manifests are retained for the statutory period applicable to the underlying data (`DA-006`; seven years for finance and statutory domains) |

### 7.4 Acceptance of a profile by the data owner

**`LPX-28`: acceptance is of a statement, not of a document.** The same discipline `DM-013` `RV-11`
applies to reconciliation sign-off.

> **Profile acceptance — `<source_id>` `<source_name>`**
>
> I confirm that:
>
> 1. this source is one I am accountable for, and the datasets listed in §2 of the report are the
>    ones it holds;
> 2. I have read the quality measures in §3 and I accept them as the **measured** position, whatever
>    I previously believed it to be;
> 3. I understand which populations will be **rejected or excluded** at the quality levels reported,
>    and approximately how many records that is;
> 4. I accept the remediation actions in §6 with the owners and dates shown, or I have named
>    different ones;
> 5. I understand that a threshold I set later (`DQ-14`) will be set against **these** numbers.
>
> Role · Name · Date · Signature

| Domain | Acceptor | Source of the accountability |
|---|---|---|
| Party, customer, corporate accounts, catalogue, pricing | **Chief Commercial Officer** | `M33` §16.4 rule 1 reports to the CCO |
| Device, asset, service history, paper archive | **Service Ops Director** | `DM-013` §2.7 |
| Inventory, parts, consignment | **Warehouse Manager** | *ibid.* |
| Finance, tax, banking, fixed assets | **CFO** | *ibid.*; `G3-08` non-delegable |
| HR, payroll, competency | **HR Director** | *ibid.* |
| Contracts, warranty, claims | **CCO** with Finance Director for claims | *ibid.* |
| Configuration, credentials, cron | **CTO** with Security Lead | `M28`, `M29`, `M30` §16.4 |
| Published registers | **CFO** (statutory) / **Master Data Owner** (geography) | `SI-09` |

### 7.5 Chain of custody

Applies to every extract of a source with `sensitivity_max ≥ S2`, and to **all** `PAPER` sources
regardless of sensitivity.

| # | Requirement |
|---|---|
| `LPX-29` | Every transfer of an extract — person to person, system to system, site to site — is recorded with actor, instant, method and destination |
| — | Physical documents leaving a branch for scanning are logged out and logged back, per box, with the receiving party's signature |
| — | Extracts at rest in `migration-staging` are encrypted and access-logged under `SC-010` |
| — | A `PAPER` source whose original must be legally retained (`SRC-031`, `SRC-034`) returns to its custodian; the scan does not replace it |

> The chain-of-custody obligation for `PAPER` is not a data-protection nicety. Contract originals
> and licence documents leaving 51 sites in cardboard boxes is a real operational risk, and `M24`
> §16.4 already requires both the scan and the physical record to be registered.

---

## 8. Freeze Points, Deltas and Re-extraction

### 8.1 Three distinct instants

Confusing them is how records are lost or double-loaded.

| Instant | Meaning | Set by |
|---|---|---|
| **Profile instant** | When the source was measured | The profiling run |
| **Extract instant** | When this copy was taken | The extract manifest |
| **Cut-off instant** | The exact `Asia/Dhaka` moment after which source records are **deltas** | `DM-014` `CV-06`, `CV-07`; `DM-001` `MS-17` |

> **`LPX-30`.** A source may be extracted many times; it has **one cut-off instant per wave**, and it
> is `DM-014`'s to declare. An extract taken after the cut-off is a **delta extract** and is marked
> `is_full_or_delta = delta` with `delta_since` set. There is no such thing as a second full load
> (`MS-17`, `SQ-13`).

### 8.2 Delta capability per source class

**The uncomfortable finding: most of this estate cannot produce a delta.**

| Class | Delta mechanism available? | Consequence |
|---|:--:|---|
| `DB` | **Only if a modification timestamp or an insert-ordered key exists.** Unknown for `SRC-001`–`SRC-003` until profiled | If absent, the delta is by **full re-extract and set difference** in staging — expensive but correct |
| `SS` | **No.** A spreadsheet has no change log | Delta by full re-collection and diff against the prior extract's hash and content. **This means a second 51-branch collection round per wave** |
| `PORTAL` | Sometimes, by date filter | Rate limits apply again |
| `MAIL` | Yes, by date | Straightforward |
| `PAPER` | **No.** Paper created during P2 is the paper contingency (`CV-11`) and is keyed as a catch-up batch | Not a delta problem; an operational one |
| `PEOPLE` | n/a | |
| `PUB` | Yes, by version | |
| `CFG` | n/a — surveyed, rotated | |

> **This is a planning finding, not a design one.** `DM-003` `SQ-13` and BRD `MIG-009` both assume
> delta loading during the parallel run. **For the 14 spreadsheet sources, "delta" means asking 51
> branches for their files again, two weeks after the first time.** `MG-006` must schedule it and
> `MG-001` `Q-02` must resource it. Recorded here as `Q-03`.

### 8.3 Re-extraction and supersession triggers

**`LPX-31`: a profile is superseded — and the source returns to `in_progress` — on any of:**

| # | Trigger |
|:--:|---|
| 1 | A material change in the source (a new branch, a format change, a system upgrade) |
| 2 | A new dataset assigned to this source in `DM-001` |
| 3 | A wave boundary, for any source feeding the next wave (`DM-002` §6) |
| 4 | A measured value in the profile proving wrong at load or reconciliation |
| 5 | More than **six months** since acceptance, for any `SS` source — spreadsheet estates drift |

### 8.4 The profiling sequence — and its one irreversible deadline

**Ordered by consequence of delay, not by ease.**

| Priority | Sources | Why first | Deadline |
|:--:|---|---|---|
| **1** | **`SRC-001`, `SRC-002`** | **Irreversible.** Both are withdrawn at W2 (BRD §6.5); unextracted data is permanently lost. Full extract taken at first contact (`LPX-12`) | **Immediately — the only hard deadline in the plan** |
| **2** | `SRC-008`, `SRC-009`, `SRC-005` | The W1 party and order load; `G1-05`; the `ASM-03` test; the `DQ-14` threshold input | W1 minus 3 months |
| **3** | `SRC-012`, `SRC-011` | Catalogue and pricing — a **W1** load with **no mapping workbook** (`MST-27`). Profiling sizes the problem even while the workbook is unregistered | W1 minus 3 months |
| **4** | `SRC-003`, `SRC-027` | W1 booking submissions and forms in circulation | W1 minus 2 months |
| **5** | `SRC-041`, `SRC-042` | `PUB` geography and holidays — cheap, fast, and every address depends on them | W1 minus 2 months |
| **6** | `SRC-045`…`SRC-048` | `CFG` survey; credentials rotate at W1 | W1 minus 1 month |
| **7** | `SRC-006`, `SRC-007`, `SRC-028` | W2 inventory — profiled to size the **count variance**, not to load | W2 minus 3 months |
| **8** | `SRC-004`, `SRC-021`, `SRC-020`, `SRC-016` | W3 finance; `SRC-004` carries the unresolved chart-of-accounts decision (`M19` `Q-02`) | W3 minus 4 months |
| **9** | `SRC-010`, `SRC-019`, `SRC-024`, `SRC-025` | W4 contracts and claims; `SRC-019` profiling is an explicit W3 prerequisite (`M09`) | W3 |
| **10** | `SRC-013`…`SRC-015`, `SRC-030`, `SRC-038` | W5 HR; **`SRC-038` needs the longest lead time of any source** | W5 minus 6 months |
| **11** | `SRC-017`, `SRC-032`, `SRC-033`, `SRC-035` | W5 assets, ISO, fleet, calibration | W5 minus 3 months |
| **12** | `SRC-026`, `SRC-031` | The paper archive survey — large, and its digitisation runs W3–W6 | W2 |
| **13** | `SRC-036`, `SRC-037`, `SRC-034`, `SRC-022`, `SRC-023`, `SRC-039`, `SRC-040`, `SRC-043`, `SRC-044`, `SRC-018`, `SRC-029` | Later waves and the `PEOPLE`/`PUB` remainder; `SRC-023` is **purge**, profiled only to evidence the destruction | Per wave |

> **`LPX-32`.** Priority 1 is not a scheduling preference. If `SRC-001` and `SRC-002` reach W2
> unextracted, **`M01`'s entire legacy service-order history ceases to exist** and no later decision
> can recover it. It is the only genuinely irreversible deadline in the migration programme and it
> currently sits behind 47 other things in nobody's plan.

---

## 9. The Effort Model

`GV-007` §7.3 excludes migration execution as *"unknowable until `MG-002` completes"*. **That is
true of execution and not of profiling itself** — profiling is estimable now, from the source
classes, and it must be, or it cannot be funded.

### 9.1 The driver per class

| Class | Sources | Effort driver | Elapsed-time driver | Parallelisable |
|---|---:|---|---|:--:|
| `DB` | 4 | Schema discovery on undocumented databases | **Vendor access for `SRC-001`/`SRC-002`** | Partly |
| `SS` | 14 | Variant clustering (typically 4–8 variants, not 51 formats) | **Custodian response rate across 51+ branches** | Poorly |
| `PORTAL` | 5 | Manual paging within rate limits | Credential provisioning across 17+ brands | No |
| `MAIL` | 2 | Human thread triage | — | Partly |
| `PAPER` | 12 | Physical survey at up to 52 locations | **Travel and branch availability** | By region |
| `PEOPLE` | 3 | Instrument design and pilot | **Supervisor/CFO availability** | No |
| `PUB` | 4 | Version pinning | **Adviser engagement** (`AUDIT-011` `DM-09`) | Yes |
| `CFG` | 4 | Inventory | — | Yes |

> **`LPX-33` — report elapsed time separately from effort.** Six person-weeks of `SS` profiling
> spread across a 10-week collection round is a 10-week task. Reporting only the effort figure
> produces a plan that finishes six weeks early on paper and not at all in reality. `GV-007` is
> asked to carry both numbers.

### 9.2 What profiling cannot tell us until it runs

**`LPX-34`: this document does not publish a profiling effort figure.** It publishes the **model**
and the drivers. The figure is produced by the Data Migration Lead against actual custodian and
access positions and submitted to `GV-007` as a costed plan. Publishing a number here, derived from
no measurement, would be exactly the defect `PG-03` exists to prevent and `BEA-04`/`BEA-06` record
the cost of.

**What can be stated now, and should be:**

| Statement | Basis |
|---|---|
| Profiling is **not** a two-week task | 36 of 48 sources need human contact; 12 need site visits |
| Its critical path is **calendar, not compute** | §9.1 |
| It cannot start without **funded custodian time** at 14 named roles | `DM-002` custodian column |
| `SRC-038` alone needs **months** of elapsed time | `M22` §16.4; 500+ assessments |
| It must start **now**, because priority 1 has a W2 expiry | `LPX-32` |

---

## 10. Personal Data and Residency During Profiling

### 10.1 Profiling is processing

**`LPX-35`: reading a source to measure it is a processing act under the Personal Data Protection
Act 2026, and it happens before any migration decision is taken.** This is not a technicality:
profiling `SRC-008` means reading 100,000+ customer records, and profiling `SRC-030` means reading
500+ personnel files including NID copies.

| Rule | Detail |
|---|---|
| `LPX-36` | Profiling of a source with `holds_personal_data = TRUE` is covered by the **same lawful basis** as the migration itself — which is **`MG-001` `Q-05`, unresolved**. Profiling of personal data therefore carries the same block as loading it |
| `LPX-37` | Profiling **outputs** are statistics, never record extracts. A profile report contains counts, rates, distributions and **at most** masked exemplars |
| `LPX-38` | Where an exemplar is needed to illustrate a defect, it is **masked or synthesised**. `DM-013`-style sampled inspection by the business owner happens against the source in situ, not against a copy pasted into a report |
| `LPX-39` | `S3` fields (NID, passport, TIN, biometric, KYC, recovered-data index) are profiled for **presence, completeness and format validity only** — never for value distribution, and never copied into staging (`MST-17`) |
| `LPX-40` | `SRC-023` (recruitment portals) and `SRC-036` (recovery job cards) are **disposition `P`**. They are profiled **only to the extent needed to evidence destruction** — what exists, how much, where. Nothing is extracted |

> **`LPX-39` in practice.** A completeness measure on an NID column asks *"how many rows have a
> value that is 10 or 17 digits?"* — computable without the value leaving the source. A frequency
> distribution asks *"which values occur?"*, which is a copy. The first is permitted; the second is
> not.

### 10.2 Where extracts live

| Sensitivity | Storage | Control |
|:--:|---|---|
| `S0`–`S1` | `migration-staging` | Standard |
| `S2` | `migration-staging`, encrypted at rest, access-logged | `SC-010`; `MG-001` `MST-16` |
| **`S3`** | **Not extracted.** The value is written at load through `CD-233` from the source, in a second pass | `MST-17`; `AR-001` `LB-08` |

> **The `S3` position has a consequence worth stating.** Because classified values never enter
> staging, **they are never profiled for distribution and never cleansed**. A malformed NID in a
> spreadsheet is discovered at the second-pass load, not during profiling. `MG-003` §6 must
> therefore treat the second pass as its own validated load with its own reject handling — it is
> not a backfill of already-clean data.

---

## 11. The Profile Report

### 11.1 Structure

**`LPX-41`: every source produces the same report, whatever its class.** Sections that do not apply
are marked *not applicable, with the reason* — never omitted, per the `RV-01` convention.

| § | Section | Contents |
|:--:|---|---|
| 1 | **Header** | `source_id`, name, class, custodian, profile instant, analyst, access constraint encountered |
| 2 | **Datasets found** | Which `DM-001` datasets this source contributes, and any dataset found that `DM-001` does not list — **a registry breach under `SI-05`** |
| 3 | **Structure** | Objects, fields, types as observed; variant count for `SS`; format sample for `PAPER` |
| 4 | **Volume** | Counted or sampled, with method and interval |
| 5 | **Measures** | P1–P6 per §4, at L1/L2/L3 |
| 6 | **Sentinels and encoding** | The null-equivalent register (§4.3); `encoding_observed` per file/column; the Bengali render result |
| 7 | **Cross-source overlap** | L3 findings — which other sources hold the same entities (§4.2 `LPX-09`) |
| 8 | **Consequences** | What will reject, what will need review, **the estimated review-queue size** |
| 9 | **Remediation** | Actions, owners, dates — source-side cleansing preferred (`MIG-003`) |
| 10 | **Assumption test** | §11.3 |
| 11 | **Acceptance** | The §7.4 form |

### 11.2 The report is written for the data owner

> **`LPX-42`.** The report's audience is the **business owner who signs it**, not the migration team.
> A report whose §8 says *"12.4% of rows fail rule PM-07"* has not communicated. A report that says
> *"approximately 12,400 customer records have no usable mobile number, which means they cannot be
> notified about their repairs, and someone must decide whether they migrate"* has.

### 11.3 The `ASM-03` test — mandatory in every party and device report

`00-04` `ASM-03` assumes *"existing customer and device data exportable at ≥ 80% quality"* and states
the consequence if false: *"migration effort increases materially; manual cleansing programme
required."* `RSK-014` carries the residual at **High/High**.

**`LPX-43`: every profile report for a party or device source contains an explicit `ASM-03` verdict**
— *holds*, *fails*, or *fails on this dimension* — with the measured figure and the definition of
"quality" used. The assumption has been carried since `00-04` was written and has never been tested.
The first party profile is the test, and it must not be allowed to produce a number that nobody maps
back to the assumption.

---

## 12. Governing Rules

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed.

| # | Rule | Class |
|---|---|:--:|
| `LPX-01` | Profiling is a gate, not a phase. No extract, mapping build or gate submission before acceptance | **H** |
| `LPX-02` | 36 of 48 sources are not machine-profilable; plans and estimates reflect that | **C** |
| `LPX-03` | A source is profiled when all six §3 conditions hold | **H** |
| `LPX-04` | "Estimated with a stated method and interval" is acceptable; "unknown" is not | **H** |
| `LPX-05` | Profiling measures the source, never the fit to the target | **C** |
| `LPX-06` | Extract requires `accepted`, not `reported` | **H** |
| `LPX-07` | P3 reports a candidate **count**, not only a rate | **H** |
| `LPX-08` | P6 states "no independent source" where none exists; never omitted | **H** |
| `LPX-09` | L3 cross-**source** profiling is mandatory. Four sources may describe one population | **H** |
| `LPX-10` | The null-equivalent set is discovered per source, never assumed | **H** |
| `LPX-11` | The §4.4 domain/measure combinations may not be waived | **H** |
| `LPX-12` | `SRC-001` and `SRC-002` are fully extracted at first contact, before scoping | **H** |
| `LPX-13` | Every collected file carries an origin record and a hash | **H** |
| `LPX-14` | The `SS` collection round starts before the profiling method is finalised | **S** |
| `LPX-15` | A `PORTAL` profile records the achieved extraction rate | **H** |
| `LPX-16` | `SRC-024`'s unresolvable proportion is reported in currency as well as percent | **C** |
| `LPX-17` | A `PAPER` profile reports physical extent before record counts | **H** |
| `LPX-18` | `PAPER` condition drives digitisation priority upward, not downward | **C** |
| `LPX-19` | A `PEOPLE` profile outputs an effort and elapsed-time model | **H** |
| `LPX-20` | A `PUB` source is profiled for currency and completeness; its verification gate is named | **H** |
| `LPX-21` | A `CFG` profile never records a credential value in any artefact | **H** |
| `LPX-22` | Encoding is detected per file and per column, not per source | **H** |
| `LPX-23` | Bengali encoding is confirmed by a native speaker reading rendered output | **H** |
| `LPX-24` | Normalise to UTF-8 NFC at extract; record the source encoding | **H** |
| `LPX-25` | An extract is point-in-time, immutable, manifested and hashed | **H** |
| `LPX-26` | No manifest, no load, no staging, no profile | **H** |
| `LPX-27` | SHA-256 at extraction, re-verified on arrival; mismatch quarantines | **H** |
| `LPX-28` | Profile acceptance is of a statement, by the named data owner | **H** |
| `LPX-29` | Chain of custody for every `S2+` and every `PAPER` transfer | **H** |
| `LPX-30` | One cut-off instant per wave; later extracts are deltas | **H** |
| `LPX-31` | Five supersession triggers return a profile to `in_progress` | **H** |
| `LPX-32` | Priority 1 (`SRC-001`, `SRC-002`) precedes everything. Its deadline is irreversible | **H** |
| `LPX-33` | Effort and elapsed time are reported separately | **C** |
| `LPX-34` | No profiling effort figure is published without measurement against actual access positions | **H** |
| `LPX-35` | Profiling personal data is processing and carries the same lawful-basis block | **H** |
| `LPX-36` | Profiling of personal data is blocked by `MG-001` `MST-21` until the basis is recorded | **H** |
| `LPX-37` | Profile outputs are statistics, not record extracts | **H** |
| `LPX-38` | Exemplars in reports are masked or synthesised | **H** |
| `LPX-39` | `S3` fields are profiled for presence and format only; never for value distribution | **H** |
| `LPX-40` | Disposition `P` sources are profiled only to evidence destruction | **H** |
| `LPX-41` | Every source produces the same report; inapplicable sections are stated, not omitted | **H** |
| `LPX-42` | The report is written for the business owner who signs it | **C** |
| `LPX-43` | Every party and device report carries an explicit `ASM-03` verdict | **H** |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Who provides hosting-vendor access to `SRC-001` and `SRC-002`, and by when?** The only irreversible deadline in the programme depends on an access request nobody has raised | CTO | **Immediately** | `LPX-12`, `LPX-32`; `M01` legacy history |
| `Q-02` | **Is profiling funded?** 14 custodian roles, 52 site visits, 500+ assessments. `GV-007` excludes migration execution but does not include profiling either | Programme Director with `GV-007` | **W0** | Everything |
| `Q-03` | **How is a spreadsheet delta produced during the parallel run?** §8.2: for 14 `SS` sources it means a second 51-branch collection round per wave, which is in no plan | Data Migration Lead with Branch Operations Lead | **W1 minus 2 months** | `SQ-13`; BRD `MIG-009`; `MG-006` |
| `Q-04` | **Is a Bengali-reading reviewer available at profiling time?** `LPX-23` requires one; `TS-016`-class reviewer shortages are already recorded elsewhere in the estate | Localisation Lead | **W1 minus 3 months** | Encoding verification on every Bengali-bearing source |
| `Q-05` | **`DM-002` `SI-01` blocks on `not_started`; `LPX-06` blocks on anything below `accepted`.** `DM-002` should be updated to match, or the two rules disagree | Programme Content Lead with Data Migration Lead | W1 | Rule consistency across categories |
| `Q-06` | **`SRC-043`/`MD-037`/`MD-043` verification needs an engaged tax adviser with a three-month lead time** (`AUDIT-011` `DM-09`). None is engaged | CFO with Tax Manager | **W3 minus 4 months** | `G3-04`, `G5-01`; `LPX-20` |

---

## 14. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `MG-002-D-01` | The extract gate | `reported` (per `DM-002` `SI-01`) · **`accepted`** | **`accepted`** | A report nobody read is not a control; the data owner's acceptance is the point of `MIG-002` | Tightens `SI-01`; `DM-002` must be updated (`Q-05`) |
| `MG-002-D-02` | When `SRC-001`/`SRC-002` are extracted | At their wave · **at first contact** | **At first contact** | Withdrawal at W2 is irreversible; storage is trivially cheap | A full extract exists before scope is settled — deliberate |
| `MG-002-D-03` | Whether to profile inventory spreadsheets that will never be loaded | Skip them · **profile them** | **Profile them** | The count-versus-spreadsheet variance (`IV-03`) is `DM-013`'s declared baseline and needs the prior measurement | Effort spent on a source with no load path, for a stated reason |
| `MG-002-D-04` | Bengali encoding verification | Detector confidence · **human render check** | **Human render check** | Bijoy-style ASCII-mapped Bengali is valid Windows-1252; no detector can distinguish it | A named Bengali reader is on the profiling critical path (`Q-04`) |
| `MG-002-D-05` | Publishing a profiling effort figure | Publish an indicative figure · **publish the model only** | **Model only** | `PG-03`; an unmeasured figure becomes a baseline | `GV-007` receives a model and must fund a costed plan |

---

## 15. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | "Profiled" has a six-condition definition with an owner-signed acceptance | §3, §7.4 |
| `AC-02` | A profiling method exists for **all eight** source classes, including the four no tool can profile | §5.1–5.8 |
| `AC-03` | Every measure has a formula, a unit and a named downstream decision | §4.1, §4.4 |
| `AC-04` | Bengali encoding handling is specified and its failure mode explained | §6 |
| `AC-05` | The extract manifest is fully specified and mandatory | §7.2, `LPX-26` |
| `AC-06` | The delta capability of every source class is stated, including where none exists | §8.2 |
| `AC-07` | The sequence is ordered by consequence and names the one irreversible deadline | §8.4, `LPX-32` |
| `AC-08` | The effort model is published without an unmeasured effort figure | §9, `LPX-34` |
| `AC-09` | Profiling is treated as processing, with `S3` handling stated | §10 |
| `AC-10` | The `ASM-03` assumption is made testable rather than carried | §11.3, `LPX-43` |

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `MG-001` | The strategy this implements; lifecycle stage 2 |
| Upstream | `DM-002` | The 48-source register this profiles |
| Upstream | `DM-011` | The dimensions adopted under `MST-04` |
| Upstream | `DA-005`, `SC-007`, `SC-010` | Classification, residency, audit logging of extracts |
| Downstream | `DM-004`…`DM-010` | Seven workbooks re-verified against measured structure (`MST-13`) |
| Downstream | **`MG-003`** | Consumes extracts, manifests, sentinel registers and encoding declarations |
| Downstream | **`MG-004`** | The manifest `record_count` is the R1 denominator |
| Downstream | **`MG-005`**, **`MG-006`** | Volumes and extraction rates feed the window arithmetic |
| Downstream | `GV-007` | The effort model; the unblocking of the excluded work stream |
| Downstream | `GV-009` `G1-05` | The at-risk gate this document's execution de-risks |
| Downstream | `RL-006` ⛔ | Decommissioning consumes the extract-complete evidence |

---

## 17. References

**Within this repository**
[`MG-001`](MG-001_Data_Migration_Strategy.md) · [`MG-003`](MG-003_ETL_Design_and_Transformation_Rules_Specification.md) ·
[`MG-004`](MG-004_Reconciliation_and_Validation_Plan.md) · [`MG-005`](MG-005_Mock_Migration_and_Dress_Rehearsal_Plan.md) ·
[`MG-006`](MG-006_Cutover_Plan_and_Runbook.md) · [`MG-007`](MG-007_Rollback_and_Fallback_Plan.md) ·
[`../03_Data_and_Information_Architecture/DA-005_Data_Classification_and_Handling_Standard.md`](../03_Data_and_Information_Architecture/DA-005_Data_Classification_and_Handling_Standard.md) ·
[`../05_Security_Privacy_and_Compliance/SC-010_Audit_Logging_and_Forensic_Readiness_Specification.md`](../05_Security_Privacy_and_Compliance/SC-010_Audit_Logging_and_Forensic_Readiness_Specification.md)

**Workspace**
`../../project_content/12_Data_Migration_Content/DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md` ·
`../../project_content/12_Data_Migration_Content/DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md` ·
`../../project_content/_AUDIT/AUDIT-011_Category_12_DM_Content_Audit.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §6.1, §6.2, §6.5, §11.6

**External standards**

| Source | Used for | Verified |
|---|---|---|
| ISO/IEC 25012:2008 | The six measures of §4.1 | 2026-08-18 |
| ISO 8000-61:2016 | Planning and control process split | 2026-08-18 |
| DAMA-DMBOK 2.0 Ch. 13 §2.3 | L1/L2/L3 profiling levels | 2026-08-18 |
| Johny Morris, *Practical Data Migration* (PDMv2), BCS 2012 | Landscape analysis; business ownership of quality | 2026-08-18 |
| Unicode Standard — normalisation forms NFC/NFD | §6.2 `LPX-24` | 2026-08-18 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Data Migration Lead | Initial issue. Specifies profiling and extract for all eight source classes; sequences the 48 sources; identifies the single irreversible deadline; makes `ASM-03` testable | CTO *(pending — `GV-001` `CC-01`)* |

---

*`MG-002` · Category 09 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
