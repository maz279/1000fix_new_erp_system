---
id: FIX-ERP2-AUDIT-015
title: Category 14 RP — Reporting, Analytics & KPI Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-20
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 16 Category 14 RP files, the KPI and report identifier spaces they reconcile, their citations into the module repository and the content register, cross-register integrity, gate F7, and the inbound dependencies carried from five prior categories
mandate: Audit required on completion of Category 14 authoring (rule CM-R9)
extends: AUDIT-001 … AUDIT-014
enumeration_date: 2026-08-20
method: Filesystem enumeration and identifier extraction only (RG-06, CP-11). No figure in this report is projected, and none is taken from what a document says about itself — including this category's own files.
---

# Category 14 `RP` — Reporting, Analytics & KPI Content Audit
### 16 files · **427 of 452** registered content files now written *(floor, enumerated 2026-08-17 16:45 UTC)*

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F7 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration. **Enumeration date 2026-08-20.**

Nine category-specific extractions were run:

| Extraction | What was compared |
|---|---|
| **Y1** | Every `KPI-` identifier in the 79 module and portal specifications against the 95 registered in `06-02` §2 |
| **Y2** | The `00-07` H2-04 "22 collisions" re-tested by extracting how each identifier is *used*, not merely that it appears |
| **Y3** | Every module and portal `§14 Reports & Analytics` row counted, and report names compared for duplication |
| **Y4** | The `06-02` §2 baseline column parsed and classified |
| **Y5** | Module template section numbering verified across all 67 module files |
| **Y6** | Every `BRU-`, `PRU-`, `AUT-`, `NFR-`, `KPI-` and `Gn-nn` identifier cited by Category 14 resolved to its owning register |
| **Y7** | Register filenames against disk; register table structure |
| **Y8** | Relative-link density compared against the four most recently completed categories |
| **Y9** | Front-matter attribute reconciliation across all seven `F7` dimensions |

**Fifteen findings — 2 critical, 5 high, 5 medium, 3 low.** Five were remediated during the audit;
ten are open, and eight of those are owned outside the content function.

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| Critical | 2 | 0 | 2 |
| High | 5 | 0 | 5 |
| Medium | 5 | 2 | 3 |
| Low | 3 | 3 | 0 |

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | 16 of 16 ✅ |
| **A2** Total written | **427 of 452 — a floor**, enumerated 2026-08-17 16:45 UTC. Categories 15, 16 and 18 completed and **17 was caught mid-authoring at 15 of 16** during this audit; 19 and 99 unstarted ⚠ finding RP-15 |
| **A5** Files on disk with no register entry | Zero ✅ |
| **B1** ID uniqueness | 16 unique ✅ |
| **B2** Contiguity `RP-001`…`RP-016` | No gaps ✅ |
| **B4** File name matches ID | 16 of 16 ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 16 of 16 ✅ |
| **D2** Files in their declared subfolder | 16 flat, matching Master Index §3.2 ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E7** Template conformance | **All six `TPL_Content_File_Front_Matter.md` sections present in all 16**, with the `CG-009` `RP` metric-table addition applied in each ✅ |
| **F1** Front matter complete | **All 24 required keys present in all 16** ✅ |
| **Y6** Identifier resolution | **95 `KPI-`, 40 `BRU-`, 28 `NFR-`, all `PRU-P06-*` and `AUT-P06-*`** resolve. `BRU-DAT-01`…`12` resolve in `M62` §9; `BRU-QMS-09` in `M23` §9; all numeric `AUT-` within `AUT-001`…`060` ✅ |
| **Y7** Register filenames vs disk | **Byte-identical, both directions.** All 16 rows carry 8 cells against an 8-cell header ✅ |
| **D1** Internal links resolve | **89 relative links, zero broken** ✅ *(after remediation — finding RP-13)* |

> **On the module-scoped rule families.** `BRU-DAT-*` exists only in `M62` §9 and `BRU-QMS-09` only in
> `M23` §9. This is the fourth and fifth family the programme has met after `BRU-CAI-*` (`M32`),
> `BRU-KMS-*` (`M61`) and `BRU-LMS-*`. `AUDIT-014` TS-16 recorded that `BRU-QMS-*` is the awkward
> case — rules 01–05 in `05-05`, continuing to 20 in `M23`. **All Category 14 citations attribute
> correctly after remediation RP-12.**

### 2.1 Cross-register reconciliation — gate F7

**All seven dimensions reconcile exactly.**

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---|---:|:--:|
| File count | Master Index §4 | 16 | 16 | ✅ |
| Priority `P0`/`P1`/`P2`/`P3` | Master Index §1 | 1 / 6 / 8 / 1 | 1 / 6 / 8 / 1 | ✅ |
| Wave per file | Master Index §4 rows | W0×1, W1×2, W2×1, W3×2, W4×8, W5×2 | All 16 match | ✅ |
| Content class A/B/C/D/E | `CG-002` §4.1 | 1 / 0 / 0 / 10 / 5 | 1 / 0 / 0 / 10 / 5 | ✅ |
| Bilingual / English-only | `CG-010` §3.2 | 5 / 11 | 5 / 11 | ✅ |
| Template allocation | `CG-009` §3 | 16 Generic | 16 | ✅ |
| Subfolder allocation | Master Index §3.2 | 16 flat | 16 flat | ✅ |

**The single class-`A` file is `RP-009`**, the statutory report register — approved by CFO with Legal
Counsel and requiring external verification under `CG-002` §5.1. It is the only file in Category 14
whose failure mode is a penalty rather than a decision, and the allocation is recorded here so it is
not later reassigned.

**The bilingual five resolve directly against `CG-010` §3.2's own rationale** — *"dashboard labels,
report catalogue, chart standards, league table and KPI names reach branch managers"* — which names,
in order, `RP-004`, `RP-002`, `RP-007`, `RP-011` and `RP-001`. Those are exactly the five marked
`bilingual: yes`. ✅

---

## 3. Findings

### RP-01 — The KPI identifier space is more than twice the size of its register, and the audit finding that pointed at it under-described the problem

**Severity: CRITICAL · Status: OPEN · Owner: Enterprise Architecture with CTO**

**What was found.** Extraction `Y1` across the 79 module and portal specifications:

| Position | Count |
|---|---:|
| Registered in `06-02` §2 | **95** |
| Distinct `KPI-` identifiers in use | **250** |
| Defined in a module `§15` KPI table row | 247 |
| **In use but unregistered** — a contiguous block `KPI-110`…`KPI-305` | **196** |
| **Registered but used by no module** | **41** |
| Both registered and used | 54 |
| Unallocated gap `KPI-096`…`KPI-109` | 14 |

**`00-07` H2-04 recorded "22 KPI identifiers used by two or more different modules" and left it
Open.** Extraction `Y2` re-tested each of the 22 by how it is *used* rather than that it appears:

| Category | Finding |
|---|---|
| **Contribution references** | The large majority. `KPI-050` is registered to `M19`; `M15`, `M49`, `M51` and `M29` cite it as a metric they *contribute to* — "supports `KPI-050` (close ≤ 3 days)". **Correct behaviour that H2-04's extraction counted as a collision** |
| **Ownership annotations** | 8 of the 10 divergent names are a parenthetical: *"(workshop contribution)"*, *"(M15 measures; M43 is the primary lever)"*, *"(instrumented here; see register note)"* |
| **Consistent restatement** | 3 identifiers restated with identical name, baseline and both targets |
| **Genuine defects** | **2.** `KPI-018` is one identifier over **two different metrics** — `M03` carries "On-time collection" and "On-time delivery" as separate rows under it. `KPI-013` has a naming inconsistency between `M02` and `M26` |

**The cause is documented in the repository already and was not connected to H2-04.** The Category E
module audit records its own finding **A-02, High**: *"KPI register exhausted. `06-02` §2.6 stops at
KPI-049 and contains no identifiers"* for the modules written afterwards. **Module authors did not
redefine metrics; they ran out of numbers.**

**Why it is Critical.** `AUDIT_Checklist_Recurring.md` defines Critical as *"a required artefact
assumed present when absent"*. The required artefact is a governed metric register, and **123
citations across 68 written content files assume one exists.** Every SOP in `06B`, most `TR` packs,
`KB`, `HC`, `MD`, `BN`, `DM` and `TS` files point at `RP-001`. Until the 196 are ratified, a dashboard
citing `KPI-207` resolves to no owner, no formula and no target.

**Remediation instruction.** Enterprise Architecture to widen the register per `RP-001` §4.3's
allocated ranges, ratify the 196 in module order, split `KPI-018`, and **restate `00-07` H2-04 rather
than closing it** — the finding pointed at a real problem and described a smaller one. Recorded as
`RP-001` `O-01` and `O-03`.

---

### RP-02 — 44 of 95 KPI baselines are absent, and the rule that makes that fatal is already written

**Severity: CRITICAL · Status: OPEN · Owner: CFO with Programme Manager**

**What was found.** Extraction `Y4` parsed the `06-02` §2 baseline column across all 95 KPI rows:

| Baseline value | Count |
|---|---:|
| "unmeasured" | 28 |
| "unknown" | 5 |
| "manual" | 4 |
| the literal word "baseline" | 3 |
| "untracked" | 2 |
| "n/a" | 2 |
| **No usable baseline** | **44 — 46%** |
| Numeric or genuine zero | 51 |

`06-02` §6 states the consequence in its own words: *"Every KPI's baseline is measured and signed off
**before** the relevant wave begins. **A KPI without a baseline cannot claim a benefit.**"*

The benefit case is **BDT 876 lac a year** at base case across 14 lines. `RP-015` §4.8 assesses each
line: roughly **BDT 396 lac depends on improvement benefits whose baselines are weak or absent**;
roughly BDT 334 lac is new-business absolutes that legitimately need none.

**Why it is Critical.** Audit `00-07` H2-10 found **one** absolute KPI target with no baseline and
recorded it Fixed. **The register-wide position is 44 and has never been stated in one place.** Three
further consequences follow immediately: `RP-011` cannot rank on four of its seven league components
(55% of the weight), `RP-012` cannot fire nine of its 24 alerts on a deviation basis, and `RP-003`
`E1` slot 9 cannot compute benefit realisation.

**The timing is worse than the count.** `RP-015` is registered `P1`/**W0** — the earliest wave in the
register — and is being written after Categories 00–13. The earliest benefit is measured from **W2**
(technician productivity, BDT 130 lac). `RP-015` `BL-05` prohibits a post-go-live baseline because it
is contaminated by the system it measures against, **so for the pilot branches that window has
closed.**

**Remediation instruction.** The four class-`B` measurement exercises in `RP-015` §4.5 need an owner,
a schedule and business time before W2. Where a window has closed, the baseline is recorded
`NOT MEASURABLE` and the target restated as an absolute — which changes how it may appear in
`06-02` §3.1. **This is a Steering Committee item, not a content one.** `RP-015` `O-01`, `O-02`, `O-03`.

---

### RP-03 — 1,063 reports are specified and the register's diagnosis of them is wrong in both directions

**Severity: HIGH · Status: OPEN · Owner: BI Lead with Programme Manager**

**What was found.** Extraction `Y3` across all 79 specifications' `§14 Reports & Analytics` sections:

| Measure | Value |
|---|---:|
| Report rows, table headers excluded | **1,063** |
| Specifications | 79 — 67 modules + 12 portals |
| Mean per specification | 13.5 |
| Specifications declaring no reports | 0 |
| Distinct report names | **1,025** |
| Names appearing in more than one specification | **34**, across 72 rows |

The register's justification for `RP-002` reads: *"67 modules each specifying reports independently
produces hundreds of near-duplicate reports nobody owns."* **Both halves need correcting.**

| Claim | Finding |
|---|---|
| "hundreds" | **1,063** — the finance cluster `M19`, `M20`, `M49`–`M54` alone declares 131 |
| "near-duplicate" | **Only 34 recurring names across 72 rows.** Deduplication removes at most 38 rows |

**The real defect is neither.** 1,063 reports have **no owner, no audience, no frequency and no
retention**, and **no document in the programme states the number**. At even 1.5 days of build each
that is over six person-years, against 1 Data/BI Engineer FTE from W4 (`06-01` §4).

**Why it matters beyond volume.** `04-00` `P06` commits to cutting manual management reporting effort
by 90% and to 100% of management reviews on live data. Both are subtraction targets, and **you cannot
subtract from an unenumerated base.**

**Remediation instruction.** `RP-002` §4.4 supplies six rationalisation rules and an expected
disposition profile, **explicitly labelled a hypothesis rather than a finding**. Applying it needs
each module business owner to confirm which of their declared reports supports a real decision —
roughly 265 hours of owner time across eleven functions. The outcome is a scope decision for the
Steering Committee. `RP-002` `O-02`, `O-03`.

---

### RP-04 — The register's trace for `RP-002` names the wrong module section, and the same error already propagated into four `TS` files

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead**

**What was found.** The Master Index traces `RP-002` to **`03_Modules` §12**. Extraction `Y5`
verified section numbering across all 67 module files and `_MODULE_TEMPLATE.md`:

| Section | Actual title | Uniform across |
|---|---|---|
| §12 | **Interfaces** | 67 of 67 |
| **§14** | **Reports & Analytics** | 67 of 67 |
| §15 | **KPIs** | 67 of 67 |
| §17 | **Acceptance Criteria** | 67 of 67 |

So `RP-002`'s trace should read **§14**.

**The same class of error is in the register's Category 13 preamble**, which states *"every module
file ends with §15 Acceptance Criteria"*. §15 is KPIs; §17 is Acceptance Criteria; and no module file
"ends" with either, since §18 and §19 follow.

**That error propagated.** `AUDIT-014` authored Category 13 from the register's wording, and **ten
citations across `TS-001`, `TS-003`, `TS-004` and `TS-006` described §15 as acceptance criteria.**
All ten were corrected to §17 during this audit (remediation RP-11).

**Why it matters.** `RP-002`'s entire derivation is the §14 enumeration; had it been built from §12 it
would have catalogued 79 interface tables as reports. **The register is the instruction authors
follow, and a wrong section number in it produces wrong content twice before anyone checks the
source.**

**Remediation instruction.** Correct both register statements. Recorded as `RP-002` `O-01`.

---

### RP-05 — Category 14's own dependencies invert its waves in five places

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead with BI Lead**

**What was found.** Registered waves against the waves in which each file's consumers need it:

| File | Registered | Needed | By |
|---|:--:|:--:|---|
| `RP-006` semantic layer | W4 | **W1** | `RP-004` `OC-05` — every `P03` panel names a certified dataset; `RP-002` `CT-09` at W2 |
| `RP-007` chart standard | W4 | **W1** | `RP-004` `OC-12` — status encoding on all fifteen consoles at `P03` go-live |
| `RP-016` data-quality scorecard | W3 | **W1** | `RP-004` `C14` panel 6 shows quality-test failures; `DI-06` blocks a refresh on a "failing" test with no definition of failing until W3 |
| `RP-008` commentary | W5 | **W2** | `06-02` §6 requires monthly benefit commentary from the first realisable wave |
| `RP-010` board pack | W5 | **W2** | `06-02` §6 requires the monthly KPI dashboard and quarterly Steering review throughout |

**And `RP-015` is `W0` and is being written after Categories 00–13** — see RP-02.

**This is the fifth consecutive category with the same defect.** `AUDIT-008` found three instances,
`AUDIT-009` two, `AUDIT-010` two, `AUDIT-014` **nine**, and this audit five. **Thirty-one instances
across five categories.** `AUDIT-010` §7 concluded the register was sequenced by *when a file's subject
matures* rather than *when its consumers need it*; `AUDIT-014` R-02 asked for the basis to be
corrected **once, register-wide, before Categories 14–19 and 99 were authored.**

**That recommendation was not actioned, and Category 14 inherited the defect exactly as predicted.**

**Remediation instruction.** `AUDIT-014` R-02 stands and is now overdue. The minimum for Category 14 is
a W1 subset of `RP-006` (five datasets), `RP-007` (stat tiles, sorted bars, status encoding, number
formatting) and `RP-016` (interim thresholds). Recorded as `RP-004` `O-01`, `RP-006` `O-01`, `RP-007`
`O-01`, `RP-016` `O-01`, `RP-008` `O-01`, `RP-010` `O-01`.

---

### RP-06 — The single most-depended-upon file in the register defines 8 of 250 metrics

**Severity: HIGH · Status: OPEN · Owner: BI Lead with Programme Manager**

**What was found.** `RP-001` is cited **123 times across 68 written content files** — every SOP in
`06B`, most `TR` course packs, `KB`, `HC`, `MD`, `CG`, `BN`, `DM` and `TS` files. That is the highest
inbound-citation count of any file in the 452-file register.

**It defines 8 metrics in full, of 250 in use.** `RP-001` §4.9 states this and quantifies the position:
**51 of 250 metrics may claim a benefit today — 20%.**

The dependent files are already blocked on it. `TS-005` `O-04`, `TS-006` `O-06`, `TS-012` `O-03`,
`HC-008` `O-01` and `TR-011` `O-01` each record `RP-001` as an operative blocker. `AUDIT-014` R-10
asked for `RP-001` to be sequenced ahead of the remaining categories — **the second such request, with
the dependant count grown from two files to five.**

**Why the file is not at fault.** `RP-001` is a standard with eight worked examples, and it says so.
Completing 242 definitions requires each metric's business owner to supply formula, numerator,
denominator, inclusions, exclusions and grain — **240–360 hours of owner time across eleven
functions**, which appears in no plan and is not in `06-01` §4's business-side commitment.

**And it is on the critical path twice.** `RP-015` `BL-03` requires a baseline's measurement method to
match the metric's definition, so **metric definition and baseline measurement are one sequenced
activity per metric** (`RP-001` `O-02`, `RP-015` `O-04`). Neither can complete without the other.

**Remediation instruction.** Sequence the ~90 metrics named on `RP-004`'s fifteen consoles first —
**not the executive set** — because `P03` ships at W1 and `P06` at W4. That reverses the natural
assumption and is recorded as `RP-004` `O-03`.

---

### RP-07 — `RP-009` is the category's only statutory file and none of its 21 obligations is externally verified

**Severity: HIGH · Status: OPEN · Owner: CFO with Legal Counsel**

**What was found.** `RP-009` is content class `A`, which under `CG-002` §5.1 requires external
verification, and it registers 21 obligations across NBR, RJSC, labour and data protection.

**No external verification exists for any of them.** Three related positions:

| Position | Source |
|---|---|
| 26 `DT` files blocked on gate `G6` external verification | `AUDIT-007` |
| `TS-009` `O-01` — no statutory reading confirmed, so no finance UAT expected result can be stated | `AUDIT-014` |
| `LG-024`'s obligation register carries uncertainty markers throughout; its licence register is **empty** | `AUDIT-013` |

`06-02` `G3-04` requires *"Mushak invoices accepted with zero NBR exceptions"* at Month 13.

**Two specific gaps this audit found beyond the verification block:**

| Gap | Detail |
|---|---|
| **Six deadlines are placeholders** | `STR-11`, `STR-12`, `STR-13`, `STR-17`, `STR-19`, `STR-20` read *"per the prescribed window"*. **Recorded as unknown rather than guessed**, per `CG-012` — and they are the most likely source of a first missed filing |
| **`STR-16` has no trigger** | The RJSC Schedule X annual return is due **within 21 days of the AGM** — an event-derived deadline. **No module holds an AGM record**; `M60` and `M67` are the candidates and neither specifies one, so the clock has nothing to start it |

**Remediation instruction.** Appoint the external adviser and close `RP-009` `O-01` before `G3`. The
`LG-024` reconciliation (`O-02`) is separate and equally open: **the company does not currently have a
single answer to "what must we submit, hold and disclose?"**

---

### RP-08 — `VB-008` provides no categorical palette, and 51 branches must be charted

**Severity: MEDIUM · Status: OPEN · Owner: Design System owner**

**What was found.** `RP-007` binds all chart colour to `VB-008`'s **eight semantic tokens**
(`status-neutral`, `-progress`, `-success`, `-warning`, `-error`, `-info`, `-hold`, `-inactive`), each
with a published contrast ratio. `PRU-P06-17` and `PS-04` both prohibit colour-only encoding.

**Semantic tokens cannot be used categorically.** Colouring "Chittagong" with `status-error` tells a
manager Chittagong is failing. So there is **no sanctioned colour set for a categorical series**, and
`RP-003` `E1` slot 3 charts fourteen revenue streams while `RP-011` charts 51+ branches.

`RP-007` §4.4 works around it — direct labelling first, then four non-judgemental tokens for a maximum
of four series, then sort-don't-colour beyond four. **That is better practice than a rainbow palette
and it is still a workaround**, and `CH-24`'s requirement for ≥ 3:1 luminance contrast between
adjacent categorical series has no palette to satisfy it with.

**Remediation instruction.** A `VB-008` decision: add a contrast-checked categorical set, or ratify
the labelling-first approach as the standard. `RP-007` `O-02`.

---

### RP-09 — Neither BI tool enforces any standard in this category

**Severity: MEDIUM · Status: OPEN · Owner: BI Lead with Platform Engineering**

**What was found.** Four Category 14 files specify rules that depend on enforcement, and the estate is
Metabase and Grafana (`04-00` `P06`):

| Rule | Enforcement today |
|---|---|
| `RP-007` `CH-07` colour from `VB-008` only | Both tools ship default palettes |
| `RP-007` `CH-04` no unmarked truncated axis | Both offer it as an option |
| `RP-007` `CH-20` Grafana carries no business metric | Convention only |
| `RP-014` `WM-12` marking applied by the platform, never the exporter | **Neither applies marking natively** |
| `RP-013` `SB-05` every delivery logged | Requires configuration |

`AUT-P06-08` rejects a dashboard containing an inline calculation at review. **Nothing rejects a pie
chart with fourteen slices, an unmarked export, or a truncated axis.**

**Remediation instruction.** A theme, a template set and a review gate. `RP-007` `O-05`, `RP-014`
`O-07`.

---

### RP-10 — Two registers this category depends on do not exist as rights or contracts

**Severity: MEDIUM · Status: OPEN · Owner: Enterprise Architecture with Security Lead**

**What was found.** Two structural gaps surfaced while deriving `RP-013` and `RP-014`:

| Gap | Consequence |
|---|---|
| **There is no export right in `05-04`** | The matrix holds portal access, module CRUD and field permissions. `RP-014` `WM-07` requires export to be a **separate grant** from view, and §4.6 proposes one derived from the others. **Without registering it, the implementation default is "can see, can export"** |
| **No module data contract exists** | `M62` `BRU-DAT-10` requires a signed data contract before a module's data enters Silver, and `BRU-DAT-07` stops the pipeline on an unexpected schema change. **67 modules produce into this estate and none has a contract**, so there is no baseline against which a schema change is unexpected |

A third, related: **`SB-11` requires a subscription revoked within one hour of a leaver event, and
nothing connects subscriptions to `AUT-048`.** `KPI-090` measures orphaned accounts; an orphaned
subscription is the same exposure and is unmeasured.

**Remediation instruction.** Register an export right in `05-04`; commission the data contracts; extend
the leaver automation to subscriptions. `RP-014` `O-02`, `RP-006` `O-03`, `RP-013` `O-01`.

---

### RP-11 — The §15 acceptance-criteria error in four `TS` files, corrected

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Extraction `Y5` established that module §15 is **KPIs** and §17 is **Acceptance
Criteria**. `AUDIT-014`'s Category 13 files, written from the register's wording (finding RP-04),
described §15 as acceptance criteria in **ten places** across `TS-001`, `TS-003`, `TS-004` and
`TS-006` — including `TS-001` `TX-02`, which is the rule every script traces under.

**Remediation applied.** All ten corrected to §17. `TS-001` §1 now records all three sections
correctly — §14 Reports & Analytics, §15 KPIs, §17 Acceptance Criteria — because Category 14 needed
§14 and the distinction is what caused the error.

**Reported rather than quietly fixed** because it originated in the register, propagated through an
audit-cleared category, and was caught only when a different category needed the neighbouring section.

---

### RP-12 — Module-scoped rule citations without attribution, corrected

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** `BRU-DAT-01`…`12` exist only in `M62` §9 and `BRU-QMS-09` only in `M23` §9.
Extraction `Y6` found `RP-004`, `RP-007` and `RP-010` citing `BRU-DAT-11` without naming `M62`, against
the attribution convention `AUDIT-010` X2 established and `AUDIT-014` TS-16 reinforced.

**Remediation applied.** Attribution added. `BRU-QMS-09` was already correctly attributed to `M23` §9
in `RP-004`.

**This is the fifth module-scoped family the programme has met.** The pattern is now frequent enough
that `CG-005` should state the citation convention rather than each audit rediscovering it.

---

### RP-13 — Category 14 was authored with zero navigable links against a house convention of 128–380

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Extraction `Y8` compared relative-link density across the four most recently
completed categories:

| Category | Relative links |
|---|---:|
| 09 `HC` | 172 |
| 10 `LG` | 380 |
| 12 `DM` | 128 |
| 13 `TS` | 13 |
| **14 `RP` at first write** | **0** |

Check `D1` passed **vacuously** — zero links, zero broken. Every cross-reference was a code span,
navigable by search only.

**Remediation applied.** 89 relative links added across the Dependencies tables of all 16 files, to
Category 14 siblings and to the fifteen most-cited cross-category files. **All 89 resolve.**

**Category 13's 13 links are also below convention** and were authored by the same auditor;
`AUDIT-014` did not detect it because it did not compare against sibling categories. **The check that
found this was a comparison, not a threshold** — recorded because `D1` as written cannot catch it.

---

### RP-14 — A self-reported identifier error in `RP-006`, corrected

**Severity: MEDIUM · Status: FIXED · Owner: BI Lead**

**What was found.** `RP-006` `SM-08` cited `AUT-P06-59`. `P06`'s automation range is
`AUT-P06-01`…`AUT-P06-10`; the intended reference is `AUT-059` in `05-05` §12.5. **The file reported
its own error as open item `O-07`** before this audit ran, and extraction `Y6` independently confirmed
it as the only unresolved identifier in the category.

**Remediation applied.** Corrected to `AUT-059`. **`O-07` is retained rather than closed**, because
the underlying risk stands: a portal-scoped `AUT-P06-nn` and a programme-scoped `AUT-nnn` differing
only by an infix will be conflated again, and `RP-012` §4.1 already separates four alert families for
the same reason.

### RP-15 — This audit's own completion figure was stale before it was written

**Severity: MEDIUM · Status: FIXED · Owner: Programme Content Lead**

**What was found.** This report was drafted with a headline of **368 of 452** — the 352 counted at
`AUDIT-014` plus Category 14's 16. Re-enumeration immediately before issue returned **427**.

Between the two counts, Categories 15 `AP` (12), 16 `CM` (18) and 18 `EO` (14) were completed and
Category 17 `OP` reached 15 of 16 — **59 files, authored concurrently with this audit.**

**Why it is reported.** `CM-R2` and `CP-11` require completion figures regenerated by enumeration and
never by projection, and **368 was a projection**: a counted figure plus an arithmetic addition,
which is the same defect in a different form. `AUDIT-014` TS-11 found the register claiming Category
13 complete before it existed and called that the first instance of a figure *leading* the work.
**This is the mirror image — a figure computed correctly and overtaken by concurrent authoring.**

**How it was contained.** The figure is now stated as **427 of 452, a floor, with a timestamp to the
minute and the in-flight category named** — the treatment `AUDIT-013` LG-07 established when it
caught Category 10 mid-authoring at 23 of 24.

**Remediation applied.** Headline, check `A2`, and the Master Index and README figures all restated
as a timestamped floor.

---

## 4. Inbound findings resolved

| Finding | Source | Resolution |
|---|---|---|
| **`RP-001` blocked five files across four categories** — `HC-008` `O-01`, `TR-011` `O-01`, `TS-005` `O-04`, `TS-006` `O-06`, `TS-012` `O-03`; `AUDIT-010` R-06 and `AUDIT-014` R-10 both requested it at W1 | Four prior categories | **Partially resolved.** `RP-001` now exists with an eighteen-field schema, the identifier space reconciled, ownership resolved into owner / steward / contributor, and eight metrics defined in full. **242 remain** (`O-02`), so the dependent files remain blocked on content rather than on the standard |
| **`TS-006` `O-06`** — *"`RP-004` operational-console dashboard specification is unwritten, and `UAT-R06-001` accepts 'the branch console tells me whether today is going well'. Without `RP-004` the executor is judging an undesigned screen"* | `AUDIT-014` | **Resolved.** `RP-004` `C3` panel 1 specifies today's numbers — intakes, completions, revenue, cash — scoped to own branch. **That is the design `UAT-R06-001` judges** |
| **`TS-012` `O-03`** — `EE-03` requires every E2E scenario to end in a report and Category 14 was unwritten | `AUDIT-014` | **Resolved for the target.** `RP-002` catalogues reports and `RP-003`/`RP-004` specify the views; the `X7` phase now has a destination. **Not resolved for the metric** — `RP-001` `O-02` |
| **`TS-014` `O-07`** — `NFR-090` §7's unit-test coverage gate has no owner and no gate criterion | `AUDIT-014` | **Not resolved and now better characterised.** `RP-001` §4.2 records the `NFR-090`/`091`/`092` double allocation as one of four defects in the NFR identifier space (`AUDIT-014` TS-04). The coverage gate remains unowned |
| **`AUDIT-013` LG-01** — gate `F3` fails: `DT-031` maps nine `MD-028` fields that do not exist | `AUDIT-013` | **Confirmed from a third side.** `RP-005` `X2` shows service credits to corporate clients on an exportable view and `RP-001` `KD-18` flags the metric contractual. **A credit figure a client can export is a commitment computed on an undefined field** (`RP-005` `O-04`, `RP-001` `O-08`) |

---

## 5. Remediation applied during this audit

| # | Change | File |
|---|---|---|
| 1 | Ten citations of module §15 as acceptance criteria corrected to §17 (RP-11) | `TS-001`, `TS-003`, `TS-004`, `TS-006` |
| 2 | `AUT-P06-59` corrected to `AUT-059`; `O-07` retained with the risk restated (RP-14) | `RP-006` |
| 3 | `BRU-DAT-11` attributed to `M62` §9 (RP-12) | `RP-004`, `RP-010` |
| 4 | **89 relative links added and verified** (RP-13) | All 16 `RP` files |
| 5 | Master Index §1 completion figure regenerated: **427 of 452 (floor)**, enumerated 2026-08-17 16:45 UTC | Master Index §1 |
| 6 | Master Index §12: Category 14 status row added | Master Index §12 |
| 7 | `AUDIT-015` added to the `_AUDIT` folder tree | Master Index §3.2 |
| 8 | README completion figure, Category 14 row and audit list updated | README |

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Widen the `KPI-nnn` register per `RP-001` §4.3 and ratify the 196 unregistered identifiers**; split `KPI-018`; **restate `00-07` H2-04 rather than closing it** (RP-01) | **Enterprise Architecture with CTO** | **W1 — before any dashboard cites a module metric** |
| **R-02** | **Take the 44 absent baselines to the Steering Committee as a benefit-case item**, and commission the four `RP-015` §4.5 measurement exercises (RP-02). Where a window has closed, record `NOT MEASURABLE` and restate the target as an absolute | **CFO with Programme Manager** | **Immediate — the W0 gate has passed** |
| **R-03** | **Sequence `RP-001` definition of the ~90 `RP-004` console metrics first**, ahead of the executive set, because `P03` ships at W1 (RP-06) | BI Lead | **W1** |
| **R-04** | **Action `AUDIT-014` R-02 — correct the register's sequencing basis once, register-wide** (RP-05). It was asked for before Category 14 was authored, was not actioned, and Category 14 inherited five more instances. **Thirty-one across five categories** | Programme Content Lead | **W1 — before Categories 15–19 and 99** |
| **R-05** | **Apply the `RP-002` rationalisation to all 1,063 report rows** and take the residue to Steering as a scope decision (RP-03) | BI Lead with module business owners | **W2 — before any report is built** |
| **R-06** | **Correct the register's `RP-002` trace to §14 and the Category 13 preamble to §17** (RP-04) | Programme Content Lead | **W2** |
| **R-07** | **Appoint the external adviser for `RP-009`**, close the six placeholder deadlines, and reconcile against `LG-024` (RP-07) | CFO with Legal Counsel | **W3 — before `G3`** |
| **R-08** | **Decide the `VB-008` categorical palette question** (RP-08) | Design System owner | W4 |
| **R-09** | **Commission a BI theme, template set and review gate** so `RP-007` and `RP-014` are enforced rather than conventional (RP-09) | BI Lead with Platform Engineering | W4 |
| **R-10** | **Register an export right in `05-04`; commission the 67 module data contracts; extend leaver revocation to subscriptions** (RP-10) | Enterprise Architecture with Security Lead | **W4** |
| **R-11** | **State the module-scoped rule citation convention in `CG-005`** (RP-12) — five families have now been encountered and each audit has rediscovered the rule | Programme Content Lead | W4 |
| **R-12** | **Add a relative-link density check to `AUDIT_Checklist_Recurring.md` `D1`** (RP-13). `D1` as written passes vacuously at zero links; **the check that caught this was a cross-category comparison** | Programme Content Lead | **W2 — and Category 13 needs the same remediation** |
| **R-13** | **Name one accessibility reviewer for all content categories** — **fifth request**, after `AUDIT-009`, `AUDIT-010` R-09, `AUDIT-014` R-13 and `RP-007` `O-03` | Content Design Lead | **W1 — escalated** |

---

## 7. Closure

Category 14 is **complete as specified**: 16 of 16 files written, all seven `F7` dimensions
reconciling exactly, 89 relative links resolving after remediation, and every `KPI-`, `BRU-`, `NFR-`,
`PRU-` and `AUT-` identifier resolving to its owning register.

**Four observations belong in front of the Steering Committee.**

**First, this category found that two of the programme's foundational registers are materially
incomplete, and neither was known to be.** The KPI space is 250 identifiers against a 95-identifier
register (RP-01); the report estate is 1,063 rows that no document has ever counted (RP-03). Both were
discovered by enumeration, and both had an audit finding pointing near them — `00-07` H2-04 described
22 collisions when the problem was an exhausted register, and the `RP-002` register row said "hundreds
of near-duplicates" when the problem is a thousand unowned reports. **A finding that is directionally
right and specifically wrong is harder to act on than no finding at all**, because it closes the
question.

**Second, RP-02 is the finding with money attached.** 44 of 95 KPIs have no baseline, `06-02` §6 says a
KPI without a baseline cannot claim a benefit, and roughly **BDT 396 lac of the 876 lac case** depends
on improvement benefits whose baselines are weak or absent. The remedy is a measurement programme that
must run **before** the consuming wave, and for the W1 and W2 pilot branches that window has already
closed. This is not a content problem and it cannot be fixed by writing.

**Third, `AUDIT-014` R-02 was not actioned and the consequence is now measurable.** That
recommendation asked for the register's sequencing basis to be corrected **once, register-wide, before
Categories 14–19 and 99 were authored** — and named the risk explicitly. Category 14 was authored
next and inherited five more inversions, bringing the total to **thirty-one across five consecutive
categories**. The remaining six categories will inherit it too.

**Fourth, this audit found three defects in its own auditor's prior work** — the §15/§17 error
propagated into four `TS` files (RP-11), Category 13's link density at 13 against a convention of
128–380 (RP-13), and the citation-attribution lapse (RP-12). Two of the three were invisible to the
checks as written: `D1` passes vacuously on zero links, and no check compares a category against its
siblings. **R-12 proposes the fix, and the general point is that a checklist detects what it was
written to detect.**

| Rule | Status |
|---|---|
| `CM-R1` register-first | ✅ All 16 registered before authoring. ⚠ `KPI-096`/`KPI-097` proposed in `RP-001` §4.6 pending allocation — the same proposal pattern as `TR-025`, `BN-019`, `SP-035` |
| `CM-R2` figures regenerated by enumeration | ✅ All Category 14 figures counted 2026-08-20 |
| `CM-R8` every claim sourced and dated | ✅ External sources carry verification dates — WCAG `1.4.11`, the 15 March income-tax deadline, the 21-day RJSC Schedule X derivation |
| `CM-R9` audit on category completion | ✅ This report |
| `CP-01` one asset, one file | ✅ `VB-008` colour, `DM-011` dimensions and `05-02` §10 classification all referenced, none redefined |
| `CP-11` counted, not estimated | ✅ 250 KPIs, 1,063 reports, 44 baselines, 89 links — all enumerated |
| `RG-06` never read what a document says about itself | ✅ Including this category's own files — `RP-006` `O-07` was independently confirmed |
| Gate **F7** category-completion reconciliation | ✅ **Seven dimensions, zero divergence** |
| Check **D1** all internal links resolve | ✅ 89 of 89 — **but the check passes vacuously at zero, R-12** |
| Check **G1** findings open across three audits | ⚠ **Four recommendations past the threshold: R-13 accessibility reviewer (5th), R-04 sequencing basis (2nd, explicitly ignored), R-03/R-01 `RP-001` and the KPI register (3rd), R-11 citation convention (3rd)** |

> **Index note.** This report and `AUDIT-001` through `AUDIT-014` must be indexed in `RF-012` when
> Category 99 `RF` is authored. **`AUDIT-011` was produced during this audit window and is now on
> disk** — `AUDIT-014` TS-03 and R-03 are **closed**, and the README de-link applied then should be
> restored to a live link. Verified by enumeration of `_AUDIT/` at 2026-08-17 16:45 UTC.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
