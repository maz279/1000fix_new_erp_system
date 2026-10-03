---
id: FIX-ERP2-AUDIT-011
title: Category 12 DM — Data Migration Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 14 Category 12 DM files, their citations into the module repository and the primary-doc BRD, cross-register integrity against CG-002 §4.1, CG-009 §3, CG-010 §3.2 and Master Index §4, coverage of the migration domains declared across all 67 module §16.4 sections, and two defects introduced by the authoring of this category
mandate: Audit required on completion of Category 12 authoring (rule CM-R9)
extends: AUDIT-001, AUDIT-002, AUDIT-003, AUDIT-004, AUDIT-005, AUDIT-006, AUDIT-007, AUDIT-008, AUDIT-009, AUDIT-010
---

# Category 12 `DM` — Data Migration Content Audit
### 14 files · 352 of 452 registered content files now written

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F7 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration and extraction, never by reading what a
document says about itself (`RG-06`, `CP-11`). **Enumeration instant 2026-08-18 23:45 Asia/Dhaka.**

Eight category-specific extractions were run:

| Extraction | What was compared |
|---|---|
| **X1** | Every content identifier cited across the 14 files against the 452 register rows |
| **X2** | Every `Mnn` module identifier cited against the 67 files in `03_Modules/` |
| **X3** | Rule-family ownership — every `XX-nn` rule cited in a file other than its owner, resolved back to its defining file |
| **X4** | `SRC-nnn` source identifiers cited across the category against those defined in `DM-002` |
| **X5** | Register filenames against disk, byte for byte, both directions |
| **X6** | Register priority and wave, per row, against each file's own front matter |
| **X7** | **The migration domains declared in all 67 module `§16.4` sections against the 14 registered workbooks** — the coverage test |
| **X8** | Every markdown table's cell count against its header, and every `csv` block against its own header |

**Twelve findings — 2 critical, 3 high, 5 medium, 2 low.** Two were remediated during the audit and
**both were caused by this category's own authoring**; ten are open, and eight of those are owned
outside the content function.

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| Critical | 2 | 0 | 2 |
| High | 3 | 0 | 3 |
| Medium | 5 | 0 | 5 |
| Low | 2 | 2 | 0 |

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | 14 of 14 ✅ |
| **A2** Total written | **352 of 452**, enumerated 2026-08-18 23:45 ✅ |
| **A5** Files on disk with no register entry | Zero ✅ |
| **A6** Register entries with no file | Zero ✅ |
| **B1** ID uniqueness | 14 unique ✅ |
| **B2** Contiguity `DM-001`…`DM-014` | No gaps ✅ |
| **B4** File name matches ID | 14 of 14 ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 14 of 14 ✅ |
| **D1** Internal links resolve | **128 relative links, zero broken** ✅ |
| **D2** Files in their declared folder | 14 flat in `12_Data_Migration_Content/`, matching Master Index §3.2 ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E7** Template conformance | All 10 `TPL_Master_Data_Specification.md` sections present in all 11 template-2 files; all 6 `TPL_Content_File_Front_Matter.md` sections present in all 3 template-1 files; Definition of Done present in all 14 ✅ *(four declared adaptations — see §2.2)* |
| **F1** Front matter complete | **All 24 required keys in the 3 template-1 files; all 26 in the 11 template-2 files. Zero missing, zero unexpected** ✅ |
| **X1** Content-ID citations | **92 distinct identifiers cited, all 92 registered** ✅ |
| **X2** Module citations | **All 67 modules cited; all 67 resolve to a file in `03_Modules/`** ✅ |
| **X3** Rule-family resolution | **Zero unresolved.** Every cross-file rule reference (`MS-`, `SQ-`, `IV-`, `FO-`, `SH-`, `DA-`, `DQ-`, `PM-`, `CW-`, `HP-`, `LT-`, `RV-`, `SI-`, `CV-`) resolves in its owning file ✅ |
| **X4** `SRC-nnn` resolution | **48 defined, 48 cited, zero unresolved** ✅ |
| **X5** Register filenames vs disk | **Byte-identical, both directions** ✅ |
| **X6** Register priority and wave vs front matter | **14 of 14 agree on both** ✅ |
| **X8** Table and CSV structure | Zero malformed table rows; 13 `csv` blocks, zero malformed rows ✅ *(two table defects found and fixed — finding DM-12)* |

> **On the 67-module citation.** Category 12 is the first category to cite **every module in the
> programme**. That is not a stylistic choice: `DM-001` §4.2 assigns a disposition to every dataset
> named in every module's `§16.4`, and there are 67 such sections. The check is therefore a coverage
> test as much as an integrity test, and X7 is where it bites (finding DM-02).

### 2.1 Cross-register reconciliation — gate F7

**All seven dimensions reconcile exactly.**

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---|---:|:--:|
| File count | Master Index §4 | 14 | 14 | ✅ |
| Priority `P0`/`P1`/`P2`/`P3` | Master Index §1 | 6 / 8 / 0 / 0 | 6 / 8 / 0 / 0 | ✅ |
| Wave per file | Master Index §4 rows | 14 rows | All 14 match | ✅ |
| Content class A/B/C/D/E | `CG-002` §4.1 | 0 / 0 / 11 / 0 / 3 | 0 / 0 / 11 / 0 / 3 | ✅ |
| Bilingual / English-only | `CG-010` §3.2 | 0 / 14 | 0 / 14 | ✅ |
| Template allocation | `CG-009` §3 | 11 Master Data Spec / 3 generic | 11 / 3 | ✅ |
| Subfolder allocation | Master Index §3.2 | 14 flat | 14 flat | ✅ |

**Two dimensions produce different three-file sets, and both are correct.**

| Register | The three files | Basis |
|---|---|---|
| `CG-002` §4.1 — content class `E` | **`DM-001`, `DM-002`, `DM-003`** | Consequence of error is *inconsistency and rework*, not a wrong transaction. These three are planning registers |
| `CG-009` §3 — template 1 | **`DM-001`, `DM-003`, `DM-014`** | Structure. `DM-002` is a dataset register and takes the Master Data Specification; `DM-014` is a procedure and takes the generic template |

This is recorded explicitly because a future author or auditor comparing the two would reasonably
treat one as an error and "harmonise" it. **They measure different things.** `DM-002` is a class-`E`
governance register that happens to have a schema; `DM-014` is a class-`C` operational procedure
that happens not to. Both allocations follow their own register correctly, and neither should be
changed to match the other.

### 2.2 Declared template adaptations

Four files apply `TPL_Master_Data_Specification.md` to something that is not a business dataset.
Each declares the interpretation in a conformance note at the head of the file rather than adapting
silently:

| File | What it actually governs | How the template was answered |
|---|---|---|
| `DM-002` | A register of **source systems the ERP extracts from** | §2 is the register's own schema; §7 states source volumes rather than target rows |
| `DM-011` | A **rule register** | §2 is the rule schema; §4 validates the register itself |
| `DM-012` | A **pack of 35 load templates** | Answered at pack level; §9 carries the register plus two worked template headers |
| `DM-013` | A **report specification and its control register** | Answered at specification level |

**This is the fourth template-adaptation family in four categories.** `AUDIT-008` KB-10 found it in
`TPL_Knowledge_Article.md`, `AUDIT-009` TR-11 in `TPL_Training_Course_Pack.md`, `AUDIT-010` HC-11 in
`TPL_Help_Article.md`. All four adapted a *content-type* template to a *register or specification*,
and all four declared it. **The recommendation made three times by `AUDIT-008` R-05, `AUDIT-009` R-09
and `AUDIT-010` R-10 — add a specification variant to `_templates/`, or amend `CG-009` §3 once — now
has a fourth instance behind it.** It is not restated as a new finding here; it is escalated in §6.

---

## 3. Findings

### DM-01 — Migration has a content specification and no technical specification

**Severity: CRITICAL · Status: OPEN · Owner: CTO**

**What was found.** The Master Index registers Category 12 as *"the content half"* of the gap left by
`06-03_Data_Migration_Strategy.md`, which the module repository lists as **planned**.
`FOLDER_STRUCTURE.md` reserves the filename. **The file does not exist**, enumerated 2026-08-18.

The fourteen files delivered here specify *what* moves, *from where*, *in what order*, *mapped how*,
*validated against what*, *proven by which report*, and *under which freeze*. They stop — deliberately
and repeatedly — at the boundary of the technical mechanism, because a content file cannot own it:

| Unspecified | Assumed by | Requirement that demands it |
|---|---|---|
| ETL / orchestration platform, retry semantics, checkpointing, idempotency keys | `DM-003` §4.6 | — |
| Staging-layer architecture | `DM-011` `DQ-03` — *"cleansing happens in the source or the staging layer"* | `05-02` §12 `MIG-02` |
| Environment topology and masking mechanism | `DM-012` `LT-17` | `05-06` `NFR-086c` |
| **Rollback mechanics and their measured duration** | `DM-003` `SQ-08`, `DM-014` `CV-13`, trigger `T4` | BRD `MIG-007` — a **rehearsed** rollback plan |
| **Merge reversibility** for the burn-down period | `DM-011` `DQ-20` | — |
| Delta-capture mechanism during the parallel run | `DM-003` `SQ-13`, `DM-014` §4.8 | BRD `MIG-009` |
| **The migration tooling itself**, delivered to the Company, repeatable and re-runnable | Every load | **BRD `MIG-008`** |

**Why it is Critical.** `AUDIT_Checklist_Recurring.md` defines Critical as *"a required artefact
assumed present when absent"*. **Nine of the fourteen files assume a contract that no document
states.** The sharpest instance is trigger `T4` in `DM-014`: fallback fires when *"the remaining
window is shorter than the measured rollback duration"* — a rule that cannot be evaluated, because
nothing specifies how a rollback is performed, and no rollback has been rehearsed.

`05-06` `OPS-07` already requires migrations to be *"forward-only, tested against a production-sized
dataset, and reversible by a documented procedure"*. **The documented procedure is the missing
document.**

**Remediation instruction.** Commission `06-03_Data_Migration_Strategy.md` before the first dry run,
scoped to exactly the seven items above so that it complements rather than duplicates Category 12.
`CG-013` does not apply — this is an architecture gap, not a legal one — but it belongs at Steering
Committee because it is on the W1 critical path. Recorded as `DM-001` `O-01`, `DM-003` `O-01`,
`DM-011` `O-05`, `DM-013` `O-05`, `DM-014` `O-01` — **five files record it independently**, which is
evidence the constraint is real rather than an authoring artefact.

---

### DM-02 — Two migration domains are declared by the modules and registered by nobody

**Severity: CRITICAL · Status: OPEN · Owner: Programme Content Lead with CTO**

**What was found.** Extraction **X7** compared the migration domains declared across all 67 module
`§16.4` sections against the seven registered mapping workbooks (`DM-004`…`DM-010`). **Two domains
have no workbook, and both are large.**

| Domain | Volume | Load wave | Declared by | Covered by |
|---|---|:--:|---|---|
| **Document and paper archive** | **500,000+ paper service records**; ~3,000–5,000 contract originals; 7 years of statutory financial records; employee files; ISO records; 17+ brand authorisation documents | **W3–W6** | `M24` §16.4 | **Nothing** |
| **Catalogue and pricing** | ~1,200 service descriptions; **~18,000 parts rows with an estimated 30–40% duplication**; **~60,000 OEM part references**; ~4,000 brand/model references; **~1,200 price points across 51+ inconsistent branch sheets**; ~400 brand rate lines | **W1** *(catalogue)*, **W3** *(pricing)* | `M37` §16.4, `M11` §16.4 | **Nothing** |

`DM-006` §2.6 maps evidence **linkage** — which document belongs to which order — and says so
explicitly. It does not map the document estate. `DM-007` maps **stock against parts** and depends on
`MD-022` already containing the parts; it does not map the ~18,000-row catalogue into existence.

**Why it is Critical, and why it is a register change rather than a gap in the files.** The
`MD` category specifies catalogue and price data as **authored seed content**; `M37` §16.4 and
`M11` §16.4 specify the same data as **migrated, from 51+ inconsistent spreadsheets, landing in
`Draft` for owner approval**. Both statements are in force and they describe different work. `M37`
calls its own version *"the single largest change-management task of Wave 1"*.

**Nobody owns the seam.** The consequence is not that a file is missing; it is that at W1 either the
catalogue is authored from nothing while 18,000 legacy rows sit unmigrated, or 18,000 rows are
migrated against no mapping specification. `M11` further requires that **where source price points
conflict, the migration does not pick one silently** — every conflict goes to the CCO for decision.
That rule needs a workbook to live in.

**This is the second consecutive category to require a register change.** `AUDIT-009` TR-01 found
that the statutory induction curriculum for 800+ employees had no owning file and that `TR-025` must
be registered. This finding is the same shape at larger volume.

**Remediation instruction.** Register **two new files** under `CM-R1` — the IDs are free, `CG-005`
reserves `DM-015`…`DM-060`:

| Proposed | Title | Pri | Wave | Owner | Traces to |
|---|---|:--:|:--:|---|---|
| `DM-015` | Field Mapping Workbook — Catalogue, Parts and Pricing | **P0** | W1 | Data Migration + Commercial | `M37`, `M11`, `MD-019`, `MD-022`, `MD-029` |
| `DM-016` | Field Mapping Workbook — Documents and Paper Archive | P1 | W3 | Data Migration + Quality | `M24`, `M23`, `M40` |

That takes Category 12 to **16 files** and the register total to **454** — or **455** with the
`TR-025` change `AUDIT-009` requires. §5 does **not** apply the change; a register change is the
Programme Content Lead's act under `CM-R1`, not an auditor's.

---

### DM-03 — Every load is blocked, because no source has been profiled

**Severity: HIGH · Status: OPEN · Owner: Data Migration Lead with the domain owners**

**What was found.** `DM-002` registers **48 legacy sources**. Enumerated 2026-08-18, **`profiling_status`
is `not_started` on all 48.**

Three independent authorities require profiling before any load, and the category implements all
three as hard rules:

| Authority | Requirement | Implemented as |
|---|---|---|
| `05-02` §12 `MIG-01` | *"Every migration is preceded by a profiling report quantifying completeness, validity and duplication"* | `MS-04` |
| BRD `MIG-002` | Profiling reported **to the data owner** | `DQ-02` |
| `M33` §16.4 rule 1 | Duplicate rate, completeness and validity measured on the source **before any load**, reported to the CCO | `PM-16`, `SI-01` |

**Why it matters.** `ASM-03` assumes the customer and device estate is exportable at **≥ 80%
quality** and states plainly what happens if it is false: *"Migration effort increases materially;
manual cleansing programme required."* `RSK-014` carries the residual at **High/High**. Nothing has
tested the assumption, and profiling is the test.

Two consequences are specific and time-bound:

1. **The device population is unknown to a factor of two.** `M17` §16.4 estimates *"300,000–600,000
   distinct devices"*. The W1 window, the stewardship burn-down and the provisional-identity backlog
   are all unsizeable until it is counted.
2. **Two sources cannot be re-extracted after W2.** BRD §6.5 withdraws `station.1000fix.com`
   (`SRC-001`) and the legacy tracker `123.0.26.238` (`SRC-002`) at W2. `SI-07` blocks the wave gate
   while a decommissioned source is still active, and neither has been profiled or extracted.

**Remediation instruction.** Profile all 48 sources, starting with `SRC-001`, `SRC-002` and `SRC-008`,
before any further mapping work is confirmed. The profiling report is the input to finding DM-04's
thresholds and to the effort re-forecast `ASM-03` implies. Recorded as `DM-002` DoD *(open)*,
`DM-004` §6, `DM-005` `O-01`, `DM-006` `O-05`, `DM-011` `O-02`.

---

### DM-04 — The match thresholds are unset, and the queue they create is unsized

**Severity: HIGH · Status: OPEN · Owner: Master Data Owner with four domain owners**

**What was found.** `DM-011` §2.6 specifies four threshold bands — auto-merge ≥ 0.95, review
0.80–0.95, weak candidate 0.65–0.80, no match < 0.65 — with an asymmetric rule for the customer
domain (`DQ-15`: a pass-3 fuzzy score never auto-merges a party, whatever its value).

`DQ-14` requires the thresholds **signed before the first load**; `DQ-05` forbids changing a control
after a load has run; `DQ-16` requires the **resulting review-queue size to be computed and accepted**
before a threshold is set. **None of the three has happened.** The four accountable owners — CCO,
CFO, Service Ops Director, HR Director — have not been asked.

**Why it matters.** This is the one decision in the category that cannot be deferred and cannot be
retaken. `DQ-20` keeps merges reversible **only through the burn-down window**; after that a merged
pair is one customer. The trade-off is asymmetric in consequence:

| Error | Recoverable? | Consequence |
|---|---|---|
| **False merge** — two customers become one | Only within the burn-down | One person's service history, addresses and contact details exposed to another. Under the **Personal Data Protection Act 2026** that is a personal-data incident, not a data-quality defect |
| **False split** — one customer stays two | Yes, continuously | Degraded service, split history, duplicated marketing |

And the queue is not a rounding error. `DM-011` §7 states the arithmetic without inventing the input:
a 15% duplicate rate on 100,000 parties, with a third of candidate pairs landing in the review band,
is **thousands of human decisions**, each requiring someone who can recognise a customer.

**Remediation instruction.** Take the profiling output from DM-03, compute the queue size at three
candidate thresholds, and have each domain owner sign their own. Do not set a threshold before its
queue is priced. Recorded as `DM-011` `O-04` and `O-06`, `DM-013` `O-01`.

---

### DM-05 — The largest business commitment in the programme is in no plan

**Severity: HIGH · Status: OPEN · Owner: Programme Director with Warehouse Manager and CFO**

**What was found.** `DM-001` §4.2.4 enumerates **twelve datasets whose opening position is
established by a physical count or survey, not by a load** — disposition `C`. The position is not the
content function's invention: four modules state it as **non-negotiable** and cite each other.

| Wave | What must physically happen | Scale |
|:--:|---|---|
| **W1** | Branch storage survey; devices held counted | 51+ branches; ~5,000 devices |
| **W2** | **Stock counted at every location; 200–400 vans recalled and counted; 17+ brand consignment balances confirmed in writing** | 10,000 SKUs × up to 51 sites |
| **W3** | **Cash counted and witnessed at every location**; cheque stock counted; bank balances taken from the bank's own statement | 51+ branches; 200–400 field floats; 12–25 accounts |
| **W5** | **Full fixed-asset physical verification**; test-equipment audit at every branch and workshop; driver licences verified against the physical document | 8,000–20,000 assets |
| **W6** | IT-asset physical audit across 51+ branches, workshop, warehouse and corporate office | ~2,500 assets |
| **W7** | Site infrastructure and safety-equipment survey | 1,500–4,000 assets |
| **W8** | E-waste backlog, item by item through the full gate | All held stock |

**Three of the twelve have no count instruction and no named owner at all** — `M45` test equipment
(W5), `M49` fixed assets (W5), `M66` IT assets (W6). `DM-012` §2.5 issues four count-sheet templates
and records that two more are outstanding for exactly this reason.

**Why it matters.** `06-01` §Resourcing allocates **Data Owners at 20% through W1–W5**. Against that
allocation the category also places: 500+ individual leave-balance agreements, 500+ supervisor
competency assessments, 50 written customer balance confirmations, 17+ brand confirmations, and a
two-week parallel run plus one full parallel month-end close on top of a normal close.

`M15` calls its own count *"the single largest operational commitment M15 asks of the business"*.
`M66` says the equivalent audit *"is a business commitment, not a software task"*. **Neither appears
in any schedule, and counting is performed by branch staff who have never done a formal count** —
which is why `DM-014` `CV-20` makes a rehearsal count at representative branches mandatory before W2.

**Remediation instruction.** Build a single physical-verification programme spanning W1–W8, resourced
separately from the migration team, with training, a rehearsal count, and zone sequencing that keeps
field service running during van recall. Name owners for the three unowned counts. Recorded as
`DM-001` `O-06` and `O-08`, `DM-005` `O-04`, `DM-007` `O-01` and `O-06`, `DM-008` `O-04`,
`DM-014` `O-02` and `O-03`.

---

### DM-06 — The register's wave column has two definitions in force

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead**

**What was found.** The Master Index defines **Wave** twice, and both definitions are live:

| Location | Definition |
|---|---|
| §0 Reading key | *"`W1`–`W9` — the delivery wave that **consumes** it"* |
| §1 note under *Distribution by wave* | *"Where a content file is needed before the wave that consumes it (**master data and migration content almost always are**), the wave shown is the **build wave**"* |

The note names this category explicitly, so the intent is discoverable — but only by a reader who
finds it. For four files the two readings diverge by up to two waves:

| File | Register wave | Load wave per the owning module | Divergence |
|---|:--:|:--:|:--:|
| `DM-005` Device and asset | W1 | W1–W3 *(`M17` §16.4)* | 0–2 |
| `DM-007` Inventory and parts | W1 | **W2** *(`M15` §16.4, `06-01` W2)* | 1 |
| `DM-008` Finance and open items | W1 | **W3** *(`M19`, `M20`, `M50`, `M52` §16.4)* | **2** |
| `DM-010` Contracts, warranty and claims | W2 | **W4** *(`M08`, `M09` §16.4)* | **2** |

**Why it is reported rather than silently reconciled.** A delivery planner reading `DM-008` at W1
schedules a finance data load nine months before the finance modules exist. A content planner
reading the same row schedules the workbook's authoring, correctly. **Both are reading the register
as written.**

**This is not the wave-sequencing error `AUDIT-008`, `-009` and `-010` found seven times.** Those
were files scheduled *after* their consumers. This is a **definitional ambiguity in the register
itself**, and stating that distinction matters: "correcting" these four rows to their load waves
would break the build-wave logic the §1 note establishes for the whole category.

**How it is contained.** `MS-22` requires every Category 12 workbook to state **both** waves in its
§1, and all seven workbooks do. The containment is on the artefacts; the ambiguity remains in the
register.

**Remediation instruction.** Amend the Master Index §0 reading key to state that for `MD` and `DM`
the wave column is the **build** wave, and add the load wave to the four divergent rows as a
parenthetical. Recorded as `DM-008` `O-08` and `DM-010` `O-07`.

---

### DM-07 — The quality gate arrives one wave after the loads it must score

**Severity: MEDIUM · Status: OPEN · Owner: Master Data Owner with CTO**

**What was found.** `M64` §16.4 defines its own migration contribution precisely:

> *"Its migration contribution is a **quality assessment gate on every other module's load**: each
> migration batch is scored against its domain rules before acceptance, and records failing a
> blocking rule are rejected to a remediation queue rather than loaded."*

**`M64` is a W2 module** (`02-02` §Register). `DM-003` §4.4 loads tiers `X1`–`X5` — party, party
dependants, asset, commercial and service — **at W1**. The gate that is supposed to score every batch
before acceptance does not exist when the first five tiers are accepted.

**Why it matters.** `M64`'s gate is not a report; it is the mechanism that keeps failing records out
of the operational model. Without it at W1, either W1 loads proceed ungated, or they are gated by
something that produces evidence `M64` cannot later compare against.

`DM-011` `DQ-26` specifies an interim gate — same three severities, same rejection behaviour, same
queue, results **re-scored by `M64` when it arrives**. That is the right containment and **it has no
build owner and appears in no plan**, which is why this is reported rather than closed.

**This is the fourth consecutive category with a mechanism-after-consumer sequencing error.**
`AUDIT-008` found three (`KB-013` safety data at W5 feeding W2 guides; `KB-014` norms at W5 feeding
W1 costing; `M61` at W6 feeding W2 sets). `AUDIT-009` found two. `AUDIT-010` found two, plus a
dependency variant, and concluded in §7 that *"the register was sequenced by when a file's subject
matures rather than by when its consumers need it"*. **This instance is not a content-register defect
at all — it is a module-register defect of the same shape**, which extends `AUDIT-010`'s conclusion
from the content register to the module register.

**Remediation instruction.** Either advance the `M64` quality-rule engine to W1, or fund and own the
`DQ-26` interim gate with a declared re-scoring obligation at W2. Recorded as `DM-003` `O-05` and
`DM-011` `O-01`.

---

### DM-08 — An English-only category whose audience is 51+ branches of Bengali-first staff

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with Localisation Lead**

**What was found.** `CG-010` §3.2 classifies all 14 `DM` files as **English-only**, with the reason
*"technical mapping worked by the migration team"*. For twelve of the fourteen that is exactly right.

For two it is right about the file and wrong about the audience:

| Artefact | Who fills it in or acts on it |
|---|---|
| **Six `DM-012` load templates** — stock count, van count, cash count, fixed-asset verification, and two outstanding | **Storekeepers, cashiers and branch staff at 51+ sites** |
| **Twelve `DM-014` cutover communications** | **Branch managers and every operational function at 51+ sites**, including the instruction to stop transacting at an exact instant |

`DM-014` `CV-09` already requires every freeze instant and instruction reaching branch staff to be
stated in Bengali and English, and `DM-012` `LT-06` requires a Bengali completion guide for
branch-filled templates. **Neither is enforceable**: the owning files are `CM-012` Branch Readiness
and `CM-013` Customer Migration, and **Category 16 `CM` held zero files at enumeration 2026-08-18.**

**Why it is Medium and not Low.** A count sheet filled in wrongly at 51 sites produces an opening
inventory position that is wrong at 51 sites, and finding DM-05 already establishes that the counters
have never done a formal count. The language of the instruction is part of the control.

**Why the rule is not wrong.** `CG-010`'s classification governs the **content file**; it does not
follow that the **instruction to a storekeeper** is English-only. The gap is between two correct
rules, which is why it is reported as a seam rather than as a breach.

**Remediation instruction.** Either register the branch-facing completion guide and cutover
instruction set as bilingual artefacts in `CM` and `TR`, or add a note to `CG-010` §3.2 recording
that `DM-012` and `DM-014` have bilingual dependants outside the category. Recorded as `DM-012`
`O-04` and `DM-014` `O-04`.

---

### DM-09 — Two statutory verification gates are unperformed, and both are on a wave gate

**Severity: MEDIUM · Status: OPEN · Owner: CFO with Tax Manager**

**What was found.** Two `MD` registers carry an explicit external-verification gate, and Category 12
depends on both:

| Register | Gate | State |
|---|---|---|
| `MD-037` Tax code, VAT rate and Mushak mapping | Every rate carries `verified_by` and `verified_on` as **G6 evidence** | **No adviser engaged** |
| `MD-043` Payroll elements and tax slabs | Slabs load **`active = FALSE` until G6 verification is recorded** | **No adviser engaged** |

The dependency is not advisory:

- `DM-008` implements `G3-04` — *Mushak invoices accepted with **zero NBR exceptions*** — and
  `FO-12` requires the **Mushak 6.3 sequence to continue across cutover without a gap or a reset**,
  agreed with the tax consultant, recorded, and asserted immediately after go-live. `M51` §16.4
  states the consequence: *"the first thing an NBR audit looks for, and it cannot be corrected
  afterwards."*
- `DM-009` implements `G5-01` — *first payroll run processed, validated and paid with **zero
  errors***. With slabs inactive there is a payroll structure and no payroll calculation.

**Why it matters.** These are not content deliverables. Under `CG-012` `EV-01`, Class A statutory
content requires a **P1 primary source** with no waiver, and `CG-002` §5.1 makes external
verification a distinct RACI row. **The verification is the gate; authoring the register did not
discharge it**, and `AUDIT-007` already recorded 26 `DT` files blocked on the same G6 gate.

**Remediation instruction.** Engage the tax adviser now, not at W3. The `MD-037` verification is a
precondition of the `DM-008` W3 load and the `MD-043` verification of the `DM-009` W5 load, and both
carry three-month lead times. Recorded as `DM-008` `O-03` and `O-06`, `DM-009` `O-04`.

---

### DM-10 — The transparency notice arrives one wave after the processing it must cover

**Severity: MEDIUM · Status: OPEN · Owner: Legal Counsel with Chief Data Officer**

**What was found.** At W1, `DM-004` and `DM-005` process **100,000+ customer records, 100,000+
addresses and an estimated 300,000–600,000 device records** into a new controller environment.

Two obligations attach:

| Obligation | Source |
|---|---|
| Personal data migrated **only with a lawful basis recorded**, and **transparency notice obligations addressed for migrated data subjects** | BRD `MIG-015` |
| A transparency notice **before or during processing**, stating categories, purposes, retention, transfers and the withdrawal procedure | `05-06` §PDPA `NFR-092` |

`LG-008` Privacy Notice and Consent Copy and `LG-012` Cross-Border Data Transfer and Residency
Statement **were both written on 2026-08-17 and stand at `Draft`. Both are registered at W2.**

**Two things therefore remain open, and the files existing closes neither:**

1. **A W2 notice does not discharge an obligation attaching to W1 processing.**
2. **Neither file determines a lawful basis for a bulk controller-side migration.** `LG-008` is
   customer-facing consent copy. `M33` §16.4 rule 2 and `MS-20` correctly prohibit *inferring*
   consent from prior dealings — which means the migration proceeds on some *other* basis, and no
   document names it.

**This extends `AUDIT-010` HC-01 rather than repeating it.** That finding concerned mining customer
transcripts at W2. This one concerns migrating the customer base itself **at W1** — one wave earlier,
at a population two orders of magnitude larger, on the same unconfirmed footing. `CG-013` legal
escalation applies to both.

**Remediation instruction.** Confirm the lawful basis for the migration processing, and move the
notice obligation to W1 or record why W2 is compliant. This cannot be closed by the content
function. Recorded as `DM-001` `O-03`, `DM-004` `O-01`, `DM-009` `O-05` and `O-07`.

---

### DM-11 — The audit's own category created a third `DM` identifier space

**Severity: LOW · Status: FIXED (during this audit) · Owner: Data Migration**

**What was found.** `DM-012` originally numbered its 35 load templates `TPL-DM-000`…`TPL-DM-034`.
Extraction **X1** returned twenty-one "unregistered content identifiers" — `DM-000`, `DM-015` …
`DM-034` — because a repository-wide search for `DM-0nn` matches the substring inside `TPL-DM-015`.

`CG-005` §3.2 **reserves `DM-015`…`DM-060` for future Data Migration content files.** A future
`DM-015` would therefore collide, on any grep, with a load template — which is precisely the failure
mode `CG-005` §3.3 registered when it recorded the existing collision between content `DM-001`…`DM-014`
and `05-02`'s modelling standards `DM-01`…`DM-15`.

**How it was fixed.** Renamed to `MLT-nnn` (Migration Load Template) across 52 occurrences. `MLT-`
was verified free across `project_content/`, `1000fix_ERP_Module/` and `primary-doc/` before
allocation. `DM-012` §3 now records the rejected name and the reason, so the decision is not
re-taken.

**Why it is reported and not quietly fixed.** `AUDIT_Checklist_Recurring.md`: *"Findings are
reported, not quietly fixed. Where the auditor's own prior work caused a finding, that is stated."*
Category 12 authoring created it; extraction caught it before issue; prose review would not have.

**Remediation instruction.** None outstanding. **Note for `CG-005`:** the `DM` space has now attracted
two collision attempts. A third is likely, and a standing note in §3.3 warning against any
`*-DM-nnn` construction would cost one line.

---

### DM-12 — A summary figure was written ahead of its derivation, and nine absence claims decayed within hours

**Severity: LOW · Status: FIXED (during this audit) · Owner: Programme Content Lead**

**What was found — two defects of the same family.**

**(a) A summary written ahead of its derivation.** `DM-001` §4.8 summarised the disposition register
as `M` 54 · `A` 12 · `N` **24** · `C` 12 · `L` 20 · `P` 4, and `MS-11` restated *"Twenty-four such
datasets exist"*. Enumerating the §4.2.3 table returned **22**. The dependent claim — *"Thirty-six of
the datasets are produced by people, not by pipelines"* — was consequently wrong by two.

**This is exactly the failure gate F7 exists for.** The gate note records three prior instances
(`AUDIT-002`, `AUDIT-003`, `AUDIT-005`) of *"a summary table written before the derivation it
summarises, and never reconciled against it"*. **This is the fourth.** Corrected to 22 and 34, both
carrying their enumeration date.

Extraction **X8** additionally found **two malformed markdown table rows** (a 4-cell row under a
5-cell header in `DM-006`; a 3-cell row under a 2-cell header in `DM-007`). Both fixed. `AUDIT-009`
TR-05 found the same defect class in `TR-022`.

**(b) Nine absence claims decayed during authoring.** Category 12 was authored while Categories 10
`LG`, 11 `BN` and 13 `TS` were being authored **concurrently**. Nine statements of the form
*"`X` is unwritten — Category `n` not started"* were **true when written and false within hours**:

| Claim | Written as | State at 2026-08-18 23:45 |
|---|---|---|
| `LG-008`, `LG-012` | *unwritten* | Written, `Draft`, **W2** |
| `LG-013`, `LG-015` | *unwritten* | Written, `Draft` |
| `BN-003`, `BN-004`, `BN-006` | *unwritten* | Written, `Draft`, W1 |
| `TS-018` | *unwritten* | Written, `Draft`, W1 |
| Categories 10, 11, 13 | *not started* | **10 complete (24), 11 complete (18), 13 complete (18)** |

**All nine were corrected**, and — importantly — **correcting them did not close the underlying
concerns; it sharpened them.** `LG-008` existing revealed that it is registered at **W2** while the
processing is **W1** (finding DM-10). `TS-018` existing revealed that two severity scales now exist
and have never been reconciled (`DM-013` `O-02`). `BN-004` existing revealed that it was authored for
product content and says nothing about **record matching** (`DM-011` `O-03`).

**Proposed rule `RG-09`.** Proposed rule `RG-07` already requires every completeness figure to carry
an enumeration date. **A claim of absence is a completeness figure with a denominator of one**, and
it decays the same way — faster, in a repository under concurrent authoring. Every statement that a
file, dataset or decision does not exist should carry the instant it was checked. All corrected
claims in Category 12 now do.

**Remediation instruction.** None outstanding on the files. `RG-09` is offered to the Programme
Content Lead in §6.

---

## 4. Inbound findings resolved

| Finding | Source | Resolution |
|---|---|---|
| **`AUDIT-010` §7** — *"the register was sequenced by when a file's subject matures rather than by when its consumers need it"*, with the observation that the remaining twelve categories would inherit the defect | `AUDIT-010` closure | **Partially discharged, and re-scoped.** Category 12 inherited **no** content-register sequencing error of that shape: X6 confirms all 14 rows agree with their files on wave and priority, and the four apparent divergences (DM-06) are a *definitional* ambiguity, not a mis-sequencing. What Category 12 did inherit is the same defect **in the module register** — `M64`'s gate at W2 against W1 loads (DM-07). The conclusion therefore extends: the sequencing basis needs correcting in `02-02` as well as in the content register |
| **`AUDIT-008` R-05 · `AUDIT-009` R-09 · `AUDIT-010` R-10** — add a specification variant to `_templates/`, or amend `CG-009` §3 once | Three prior audits | **Fourth instance recorded (§2.2).** Four files applied a content-type template to a register or specification; all four declared the adaptation and all four pass E7. The recommendation is escalated, not restated |
| **`AUDIT-010` HC-01** — customer conversation data scheduled to be mined before its legal basis is confirmed | `AUDIT-010` | **Extended, not resolved.** DM-10 finds the same class of exposure one wave earlier, at the customer base itself rather than its transcripts. The two should be answered together by Legal Counsel with the CDO |

---

## 5. Remediation applied during this audit

| # | Change | File |
|---|---|---|
| 1 | 35 load-template identifiers renamed `TPL-DM-nnn` → `MLT-nnn`; the rejected name and reason recorded (DM-11) | `DM-012` |
| 2 | Disposition `N` count corrected **24 → 22** by enumeration; the dependent "thirty-six" corrected to **thirty-four**; both now carry the enumeration date (DM-12a) | `DM-001` §4.8, `MS-11` |
| 3 | Two malformed markdown table rows corrected (DM-12a) | `DM-006` §2.2, `DM-007` §2.5 |
| 4 | Nine decayed absence claims corrected across six files, each now carrying its enumeration instant, with the residual concern restated rather than dropped (DM-12b) | `DM-001`, `DM-004`, `DM-009`, `DM-010`, `DM-011`, `DM-013`, `DM-014` |
| 5 | Master Index §1 completion figure regenerated: 278 → **352 of 452**, enumerated 2026-08-18 23:45 | Master Index §1 |
| 6 | Master Index §12 status: Category 12 row added; the stale *"Categories 07–99 not started"* row replaced with *"Categories 14–19, 99"* | Master Index §12 |
| 7 | `AUDIT-011` added to the `_AUDIT` folder tree | Master Index §3.2 |
| 8 | README completion figure, category status rows and audit list updated | README |

> **Not applied.** The register change required by **DM-02** — registering `DM-015` and `DM-016` — is
> deliberately **not** made here. `CM-R1` places register changes with the Programme Content Lead, and
> an auditor who edits the register they are auditing removes the control.

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Commission `06-03_Data_Migration_Strategy.md`**, scoped to the seven items in DM-01 so it complements Category 12 rather than duplicating it. Nine files assume a contract it would state | **CTO** | **W0 — before the first dry run** |
| **R-02** | **Register `DM-015` catalogue/parts/pricing and `DM-016` documents/paper archive** (DM-02), taking the register to 454 — or 455 with `AUDIT-009`'s `TR-025` | **Programme Content Lead with CTO** | **W1 — `DM-015` is P0** |
| **R-03** | **Profile all 48 registered sources**, beginning with the two that decommission at W2 and cannot be re-extracted (DM-03) | Data Migration Lead with domain owners | **W1 — immediately** |
| **R-04** | **Price the review queue at three candidate thresholds, then have each domain owner sign their own** (DM-04). Do not set a threshold before its queue is sized | Master Data Owner with CCO, CFO, Service Ops Director, HR Director | **W1 — before the first load** |
| **R-05** | **Establish a physical-verification programme spanning W1–W8**, resourced separately, with training, a rehearsal count and zone sequencing; name owners for the three unowned counts (DM-05) | **Programme Director** with Warehouse Manager and CFO | **W2 minus 3 months** |
| **R-06** | Amend the Master Index §0 reading key to state that `MD` and `DM` waves are **build** waves, and add load waves to the four divergent rows (DM-06) | Programme Content Lead | W1 |
| **R-07** | **Advance the `M64` quality gate to W1, or fund and own the `DQ-26` interim gate** with a declared re-scoring obligation (DM-07). **Fourth consecutive category with a mechanism-after-consumer error — the sequencing basis needs correcting in `02-02`, not only in the content register** | Master Data Owner with CTO | **W1** |
| **R-08** | Register the branch-facing completion guide and cutover instruction set as bilingual `CM`/`TR` artefacts, or note the dependency in `CG-010` §3.2 (DM-08) | Programme Content Lead with Localisation Lead | **W2 — before the count** |
| **R-09** | **Engage the tax adviser for the `MD-037` and `MD-043` G6 verifications** (DM-09). Both carry three-month lead times and both sit on a wave gate | **CFO with Tax Manager** | **W3 minus 3 months** |
| **R-10** | **Confirm the lawful basis for migrating 100,000+ data subjects at W1 and resolve the W1/W2 notice misalignment** (DM-10). Answer together with `AUDIT-010` R-01 | **Legal Counsel with CDO** | **W1 — before the first party load** |
| **R-11** | **Adopt proposed rule `RG-09`: a claim of absence carries the instant it was checked** (DM-12b). Nine claims in this category decayed within hours of being written, under concurrent authoring | Programme Content Lead | Next governance revision |
| **R-12** | **Add a specification variant to `_templates/`, or amend `CG-009` §3 once** — **fourth request**, superseding `AUDIT-008` R-05, `AUDIT-009` R-09 and `AUDIT-010` R-10 | Content Design | **W2** |
| **R-13** | **Name one accessibility reviewer for all content categories** — **fourth request**, carried from `AUDIT-010` R-09. `DM-012` count sheets are print artefacts used in poorly lit store rooms and are subject to `CG-011` | Content Design Lead | **W1** |

---

## 7. Closure

Category 12 is **complete as specified**: 14 of 14 files written, all seven cross-register dimensions
reconciling exactly, 128 internal links resolving, and every one of 92 content identifiers, 67 module
identifiers, 48 source identifiers and every cross-file rule reference resolving to its owning
register.

**Four observations belong in front of the Steering Committee.**

**First, this category is the content half of a specification that has no other half.** DM-01 is not
a gap inside Category 12; it is the observation that fourteen files describe a migration whose
tooling, staging, environments and rollback are specified nowhere. `05-06` `OPS-07` requires a
migration to be *"reversible by a documented procedure"* and BRD `MIG-007` requires that procedure
**rehearsed**. Neither can be satisfied by a document that does not exist, and the fallback trigger
`DM-014` `T4` is currently unevaluable in consequence.

**Second, the migration's largest cost is not technical and is not funded.** Thirty-four of the
datasets that must exist at go-live are produced by **people, not pipelines** — twenty-two authored
from nothing, twelve established by physical count across 51+ sites in three separate waves. Against
that, `06-01` allocates data owners at 20%. `M15`, `M45`, `M49`, `M50` and `M66` each describe their
own count as a business commitment rather than a software task, in near-identical language. **Five
modules independently reaching the same conclusion is a programme position that has never been
costed.**

**Third, DM-02 makes this the second consecutive category to require a register change** — and the
larger of the two. `AUDIT-009` found one missing training file. This audit finds two missing
migration domains covering 500,000+ paper records and ~80,000 catalogue, part and price rows, both
declared by their owning modules and registered by nobody. The register total moves to 454, or 455
with `TR-025`.

**Fourth, three recommendations have now been made four times** — the template variant (R-12), the
accessibility reviewer (R-13), and the sequencing basis (R-07, now shown to affect the module
register as well as the content register). Check **G1** states that no finding should remain open
across three consecutive audits without escalation. **All three passed that threshold at `AUDIT-010`
and have now passed it again.**

| Rule | Status |
|---|---|
| `CM-R1` register-first | ✅ All 14 registered before authoring; zero divergence both directions |
| `CM-R9` audit on category completion | ✅ This report |
| `CP-11` counted, not estimated | ⚠ **One summary was written ahead of its derivation and corrected (DM-12a) — fourth instance of the F7 failure** |
| `RG-06` never read what a document says about itself | ✅ Every check by extraction; the `N` count error was found this way |
| Proposed `RG-08` — quote register titles, never paraphrase | ✅ **Held. 92 of 92 identifiers resolve** |
| Gate **F7** category-completion reconciliation | ✅ **Seven dimensions, zero divergence** |
| Check **G1** — findings open across three audits | ⚠ **Three recommendations have now been made four times (§6 R-07, R-12, R-13)** |
| Proposed **`RG-09`** — a claim of absence carries the instant it was checked | ⚠ **New. Offered in R-11 on the evidence of DM-12b** |

> **Concurrency note.** Categories 10 `LG`, 11 `BN` and 13 `TS` were authored **during** this
> category's authoring and audit. Every figure in this report carries the enumeration instant
> **2026-08-18 23:45 Asia/Dhaka**, and the completion figure of 352 was true at that instant. This is
> the first audit in the series run against a repository under concurrent change, and it is the
> direct evidence behind proposed rule `RG-09`.

> **Index note.** This report and `AUDIT-001` through `AUDIT-013` must be indexed in `RF-012` when
> Category 99 `RF` is authored.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
