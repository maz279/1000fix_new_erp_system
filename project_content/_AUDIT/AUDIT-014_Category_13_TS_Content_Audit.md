---
id: FIX-ERP2-AUDIT-014
title: Category 13 TS — Test & Acceptance Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 18 Category 13 TS files, their citations into the module repository and the content register, cross-register integrity, gate F7, and the audit-trail integrity of the _AUDIT folder itself
mandate: Audit required on completion of Category 13 authoring (rule CM-R9)
extends: AUDIT-001 … AUDIT-013
enumeration_date: 2026-08-19
method: Filesystem enumeration and identifier extraction only (RG-06, CP-11). No figure in this report is projected, and none is taken from what a document says about itself — including what this category's own files say about themselves.
---

# Category 13 `TS` — Test & Acceptance Content Audit
### 18 files · 352 of 452 registered content files now written

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F7 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration and extraction. **Enumeration date
2026-08-19.**

Eight category-specific extractions were run:

| Extraction | What was compared |
|---|---|
| **X1** | Every content identifier cited against the 452 register rows |
| **X2** | Every `BRU-` identifier against `05-05`, with module-scoped families checked against their owning module |
| **X3** | Every `FR-<MOD>-nnn` identifier against its module's §5 table |
| **X4** | Every `KPI-` identifier against `06-02` |
| **X5** | Every gate criterion `Gn-nn` against `06-02` §4, **and the criteria counted** |
| **X6** | Every `NFR-`, `SOD-`, `EA-`, `DI-`, `AS-`, `OPS-`, `AUT-`, `PRU-` identifier against its declared range |
| **X7** | Register filenames against disk, byte for byte; register table structure, cell counts per row |
| **X8** | The `05-04` §2 portal access matrix enumerated cell by cell, to verify `TS-017`'s derived 77/379 split |

**Seventeen findings — 1 critical, 6 high, 7 medium, 3 low.** Three were remediated during the
audit; fourteen are open, and eleven of those are owned outside the content function.

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| Critical | 1 | 0 | 1 |
| High | 6 | 0 | 6 |
| Medium | 7 | 1 | 6 |
| Low | 3 | 2 | 1 |

> **Two findings in this report are against the auditor's own authoring** (TS-15, TS-16). That is
> stated because the convention inherited from audit `00-07` requires it: where the auditor's prior
> work caused a finding, the cause matters more than the fix.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | 18 of 18 ✅ |
| **A2** Total written | **352 of 452**, enumerated 2026-08-19 ✅ |
| **A5** Files on disk with no register entry | Zero ✅ |
| **B1** ID uniqueness | 18 unique ✅ |
| **B2** Contiguity `TS-001`…`TS-018` | No gaps ✅ |
| **B4** File name matches ID | 18 of 18 ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 18 of 18 ✅ |
| **D1** Internal links resolve | **13 relative links, zero broken** ✅ |
| **D2** Files in their declared subfolder | **18 flat**, matching Master Index §3.2 — Category 13 declares no subfolders ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E7** Template conformance | **All six `TPL_Test_Script.md` sections present in all 15 test-script files; all six `TPL_Content_File_Front_Matter.md` sections present in all 3 generic files** ✅ *(pack-level application — see finding TS-14)* |
| **F1** Front matter complete | **All 24 required keys present in all 18** ✅ |
| **X1** Content-ID citations | **244 distinct identifiers cited, 243 registered** — the one exception is a deliberate proposal, finding TS-13 ⚠ |
| **X2** `BRU-` citations | **137 distinct rules cited; 136 resolve in `05-05`**; `BRU-QMS-09` resolves in `M23` §9 ✅ *(attribution corrected — TS-16)* |
| **X3** `FR-` citations | All resolve. `FR-KMS-*` → `M61`, `FR-CAI-*` → `M32`, `FR-QMS-*` → `M23`, `FR-LMS-*` → `M22`, `FR-WSR-*` → `M31`, `FR-DMS-*` → `M24`, `FR-GRC-*` → `M60` ✅ |
| **X4** `KPI-` citations | **52 distinct, all resolve in `06-02`** ✅ |
| **X5** Gate criteria | **59 distinct cited, all 59 resolve** ✅ — but the *count* was wrong, finding TS-15 |
| **X6** Range checks | **87 distinct `NFR-` cited, all within `NFR-001`…`NFR-101`**; `SOD-01`…`12`, `EA-01`…`12`, `DI-01`…`08`, `AS-01`…`15`, `OPS-01`…`08`, `AUT-001`…`060` all in range; `AUT-QMS-*`, `AUT-ITS-*`, `AUT-P06-*`, `PRU-P06-*` resolve to `M23`, `M66` and `P06` ✅ |
| **X7** Register filenames vs disk | **Byte-identical, both directions.** All Category 13 register rows carry 8 cells against an 8-cell header — **no malformed rows** ✅ |
| **X8** Portal-matrix derivation | **`05-04` §2 enumerated: 456 cells, 77 granted, 379 denied.** `TS-017` §1.1's derived split is **exact** ✅ |

> **On `BRU-QMS-09`.** `05-05` §10 carries `BRU-QMS-01`…`05`; `M23` §9 carries `BRU-QMS-01`…`20`.
> This is the fourth module-scoped rule family the programme has met — after `BRU-CAI-*` (`M32`),
> `BRU-KMS-*` (`M61`) and `BRU-LMS-*` (which *is* in `05-05`) — and the first where a family is
> **partially** in `05-05` and continues in its module. `AUDIT-010` recorded the pattern; this is the
> variant that will catch the next author out.

### 2.1 Cross-register reconciliation — gate F7

**All seven dimensions reconcile exactly.**

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---|---:|:--:|
| File count | Master Index §4 | 18 | 18 | ✅ |
| Priority `P0`/`P1`/`P2`/`P3` | Master Index §1 | 5 / 12 / 1 / 0 | 5 / 12 / 1 / 0 | ✅ |
| Wave per file | Master Index §4 rows | W1×5, W2×9, W3×2, W4×1, W5×1 | All 18 match | ✅ |
| Content class A/B/C/D/E | `CG-002` §4.1 | 0 / 0 / 0 / 4 / 14 | 0 / 0 / 0 / 4 / 14 | ✅ |
| Bilingual / English-only | `CG-010` §3.2 | 7 / 11 | 7 / 11 | ✅ |
| Template allocation | `CG-009` §3, §3.1 | 15 Test Script / 3 generic | 15 / 3 | ✅ |
| Subfolder allocation | Master Index §3.2 | 18 flat | 18 flat | ✅ |

`CG-009` §3 allocates template 1 to **`TS-001`, `TS-002` and `TS-018`**; those are exactly the three
carrying `TPL_Content_File_Front_Matter.md`, and `CG-009` §3.1's coverage table independently states
that template 11 governs **15** files. ✅

**The four class-`D` files are `TS-002`, `TS-006`, `TS-011` and `TS-016`** — the four whose failure
mode is a *content* failure rather than a process failure: a persona nobody recognises, a script
nobody reads, an external task nobody outside the company can complete, and an accessibility claim
with no evidence. All four are also in the bilingual seven, and all four are approved by the Content
Design Lead per `CG-002` §5.4. The allocation is recorded here so it is not later reassigned.

**The bilingual seven are `TS-002`, `TS-006`, `TS-008`, `TS-009`, `TS-011`, `TS-015` and `TS-016`.**
`CG-010` §3.2's rationale — *"scripts executed by Bengali-speaking business users, plus the bilingual
and accessibility packs"* — resolves against headcount: `TS-006` covers 526–1,022 people of whom five
of ten roles are Bengali-first; `TS-008` covers 116–231 Bengali-first people of 135–274; `TS-009`
covers 51+ cashiers; `TS-011` covers the customer, seller and courier audiences; `TS-015` covers
275–635 field staff. **The three English-only UAT packs — `TS-007`, `TS-010` — are head-office
functions**, and each carries its Bengali obligation as in-pack assertions on the artefacts their
Bengali-reading subjects receive, rather than as a second language edition.

---

## 3. Findings

### TS-01 — Category 13's central deliverable has no denominator

**Severity: CRITICAL · Status: OPEN · Owner: Enterprise Architecture with CTO**

**What was found.** `TS-001` is the requirement-to-script traceability standard, and `TX-01` makes
the category's core claim: *a requirement with no script resolving to it is untested.* Reporting
that requires a total. **The repository holds three, all current:**

| Figure | Source | Basis |
|---:|---|---|
| **2,930** | `README.md`; `02-02` §3; the v2.0 BRD | Counted by enumeration, 2026-08-13 |
| **~2,352** | `05-01`'s own title | Superseded 30-module basis — audit finding `AF-06`, **still open** |
| **2,985 + 358 = 3,343** | `03_Modules/_MODULE_SET_AUDIT_REPORT.md` §115, §522 | Recounted; **explicitly states it supersedes the README's 2,930** |

The Master Index's Category 13 preamble adds a fourth form, *"2,900+ requirements"*.

**Why it is Critical.** `AUDIT_Checklist_Recurring.md` defines Critical as *"a required artefact
assumed present when absent"*. The required artefact is an agreed requirement baseline, and **every
coverage figure in this category assumes one.** A coverage percentage computed on 2,930 and one
computed on 3,343 differ by roughly **12 points at identical testing**, which is more than enough to
move a Go/No-Go. `06-02` `G4-10` is worse: *"every v1.0 BRD requirement demonstrated as delivered or
formally superseded"* is a traceability query, and there is nothing to query it against.

`TS-001` §4.4 handles it as honestly as a content file can — it requires every coverage figure to
carry its denominator inline and refuses to emit a bare percentage — but **that is mitigation, not
resolution.**

**Remediation instruction.** Enterprise Architecture to declare one governing figure, reconcile
`05-01`'s title and the `_MODULE_SET_AUDIT_REPORT` restatement to it, and record the decision. This
closes `AF-06` and it is a precondition of the first coverage statement, not of the first gate.
Recorded as `TS-001` `O-04`.

---

### TS-02 — Nine of eighteen files are consumed a wave before they exist

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead with QA Lead**

**What was found.** Extraction of each file's registered wave against the `06-02` §4 gate criteria it
evidences:

| File | Registered | First consumed | Named criterion |
|---|:--:|:--:|---|
| `TS-003` SIT A–D | W2 | **W1** | `G1-02` full service-order lifecycle end to end at Month 4 |
| `TS-004` SIT E–G | W3 | **W1/W2** | `G1-05` migration reconciliation; `G2-06` inventory accuracy by count |
| `TS-005` SIT H–K | W4 | **W1** | `G1-06` SSO and role framework; `G1-07` audit trail complete |
| `TS-008` UAT supply chain | W3 | **W2** | `G2-06`, `G2-07` van-stock variance |
| `TS-012` E2E pack | W2 | **W1** | `G1-02`, `G1-03` timed walk-in intake |
| `TS-013` Regression and smoke | W2 | **W1** | Monthly production cadence from `P03` go-live (`06-01` §5) |
| `TS-014` Performance | W2 | **W1** | `G1-10` performance targets met for delivered screens |
| `TS-016` Accessibility | W2, **`P2`** | **W1** | `05-06` §11 audit *before each portal release*; `P03` ships W1 |
| `TS-017` Security and privacy | W2 | **W1** | `G1-06`, `G1-07`, **`G1-09` zero critical or high security findings** |

**Half the category is late against its own consumers, and the concentration is not random: seven of
the nine are consumed at `G1`.** `G1` is the gate with the most criteria (12 of 70) and it falls at
Month 4.

**This is the fourth consecutive category with the same defect.** `AUDIT-008` found three instances
in `KB`, `AUDIT-009` two in `TR`, `AUDIT-010` two in `HC` plus a dependency variant, and this audit
finds nine. **Twenty instances across four categories is not a series of oversights.** `AUDIT-010` §7
already concluded that the register was sequenced by *when a file's subject matures* rather than by
*when its consumers need it*; Category 13 is the proof, because a test pack's consumer is a gate with
a published date.

**`TS-016` carries a second error on the priority axis.** It is registered `P2` while `PS-04` WCAG
2.1 AA is contractual and `NFR-073` is `P1`. A `P2` on a contractual requirement is a scale error,
not a judgement.

**Remediation instruction.** Correct all nine waves and `TS-016`'s priority, **or** record a
documented exception per file with the retrofit accepted. **Do not correct them one at a time** —
`AUDIT-010` R-02 did that for two `HC` files and the pattern recurred here at four times the volume.
The sequencing basis needs correcting once, register-wide, before Categories 14–19 and 99 are
authored. Recorded as `O-01` in each of the nine files.

---

### TS-03 — `AUDIT-011` is cited in four places and does not exist

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead**

**What was found.** Enumeration of `_AUDIT/` against every reference to it:

| Location | States |
|---|---|
| Master Index §3.2 folder tree | `AUDIT-011_Category_12_DM_Content_Audit.md` listed as present |
| Master Index §12 | Category 12 *"audited, `AUDIT-011`"*, with three findings summarised |
| README §Start here | A **markdown link** to `_AUDIT/AUDIT-011_Category_12_DM_Content_Audit.md` — *"12 findings, 9 open"* |
| README Category 12 row | *"audited, `AUDIT-011`"* |

**`_AUDIT/` contains no `AUDIT-011`.** It holds `AUDIT-001`…`AUDIT-010`, `AUDIT-012`, `AUDIT-013` and
the recurring checklist. The README link is broken — the first broken relative link in this
repository since `AUDIT-005` NT-02 was closed.

**Why it matters, and why it is not merely tidiness.** Category 12 `DM` is recorded as audited, with
a finding count, a critical finding and an open-findings tally, **and the report those figures came
from cannot be read.** Three consequences: check `D1` fails; check `G1` (findings open across three
audits) cannot be run for `DM`; and Category 12's `DM-01` critical finding — that
`06-03_Data_Migration_Strategy.md` does not exist — is quoted in two places with no evidence behind
it. `TS-004` `O-05` and `TS-009` `O-04` both depend on `DM-007` and `DM-008`, so this is not an
isolated register defect.

**How it happened.** `AUDIT-012` finding `BN-24` records the cause exactly: the Category 11 audit was
*issued* as `AUDIT-011`, the register had **concurrently** allocated `AUDIT-011` to Category 12, and
the Category 11 report was renumbered to `AUDIT-012` to respect the register. **The renumbering was
correct and the reserved slot was never filled.** `CP-02` was preserved; the artefact was not
produced.

**Remediation instruction.** Either produce `AUDIT-011` for Category 12 `DM`, or — if the Category 12
audit was in fact performed and folded into another report — correct all four references and remove
the reserved ID under `CP-02` (marked `WITHDRAWN`, never recycled). **Until one of those happens, the
DM findings quoted in the register have no source.** This audit deliberately took `AUDIT-014` rather
than filling the gap, because writing a Category 12 audit under a Category 13 mandate would create a
second unverifiable report.

---

### TS-04 — The NFR identifier space has four defects, and this category is named after it

**Severity: HIGH · Status: OPEN · Owner: Enterprise Architecture with CTO**

**What was found.** Extraction `X6` resolved 87 distinct `NFR-` citations. All 87 are in range, and
in resolving them four defects in `05-06` surfaced:

| # | Defect |
|---|---|
| 1 | **`NFR-090`, `NFR-091` and `NFR-092` are each used twice for unrelated requirements.** §6.3 assigns them to Personal Data Protection Act obligations — consent basis, consent standard, transparency notice, all `P0`. §7 assigns the same three to maintainability — **unit-test coverage ≥ 80% and 100% of financial calculations**, module runbook, distributed tracing |
| 2 | **`05-06`'s own title reads "NFR-001 … NFR-092"** and the document contains 101 |
| 3 | **`NFR-088` and `NFR-089` appear a second time** as two stray rows at the end of the §6.4 residency table |
| 4 | **The Master Index traces `TS-014` to "`05-06` NFR-001…044"**, implying 44 requirements; the performance section is `NFR-001`…`005` **plus** `NFR-031`…`044`, and the document holds 101 |

**Why it matters here specifically.** `TS-014` names its scripts after the target they verify —
`PERF-NFR-037-02`. **An ambiguous identifier produces an ambiguous script name**, and a gate claim of
the form *"`NFR-090` met"* is unfalsifiable: it could mean unit-test coverage passed or that consent
processing is lawful. `TS-005` `SIT-I-008`/`-009` cite the §6.3 meanings and `TS-014` §1.1 cites the
§7 meaning, so **both readings are now in the content set.**

Defect 1 also hides something: **`NFR-090` §7's unit-test coverage gate is the only `05-06` §11
coverage standard with no gate criterion in `06-02` §4.** Nothing verifies it at `G1`–`G9`. Recorded
as `TS-014` `O-07`.

**Remediation instruction.** Renumber the §7 maintainability trio to free identifiers, correct the
document title, delete the §6.4 strays, and restate the Master Index's `TS-014` trace. Recorded as
`TS-014` `O-02` and `TS-005` `O-05`.

---

### TS-05 — `TS-017` is 100% blocked on 38 accounts that do not exist

**Severity: HIGH · Status: OPEN · Owner: `M29` owner with Security Lead**

**What was found.** `TS-017` derives approximately **734 cases** from `05-04` by set arithmetic, and
extraction `X8` confirms its core figure exactly: **456 portal-matrix cells, 77 granted, 379 denied.**
`SC-01` forbids sampling the 379, because `05-04` §10 criterion 6 makes negative testing a condition
of releasing a role.

**Every one of those cases needs an account holding exactly the permissions its role holds, and no
account exists for any of the 38 roles.** Six files record it independently:

| File | Where |
|---|---|
| `TS-002` `O-04` | The data-side statement: 11 personas describe *whom the data is about*; 38 roles describe *who executes* |
| `TS-003` `O-02`, `TS-004` `O-03` | SIT precondition |
| `TS-006` precondition 7, `TS-011` precondition 9 | UAT precondition |
| **`TS-017` `O-02`** | *"not a precondition but the entire pack"* |

**Why it matters.** `06-02` `G1-06` requires the role framework operating **for all delivered roles**
at Month 4 and `G1-09` requires zero critical or high security findings. Both are evidenced only by
`TS-017`. **Six independent records of the same gap is evidence the constraint is real rather than an
authoring artefact.**

**Remediation instruction.** Specify and provision the 38 role accounts per environment, with record
rules, field restrictions and SoD constraints applied, before `SIT` entry. This is `M29`
configuration work, not test preparation, and it is on the critical path of four packs.

---

### TS-06 — Three packs cannot be executed at all, for want of physical resources

**Severity: HIGH · Status: OPEN · Owner: Programme Manager with CTO**

**What was found.** Three packs require physical conditions that no programme document allocates:

| Pack | Requires | Rule |
|---|---|---|
| **`TS-006`** | A 1366×768 laptop, a thermal receipt printer, a barcode scanner, a signature pad, a mid-range Android 11 device with 3 GB RAM | Precondition 10; `O-04` |
| **`TS-008`** | 40 labelled real parts across 3 locations, one serialised, one expired-shelf-life, one hazardous; the branch's own scanner and label printer; a vehicle for custody scripts | `UA-23`; `O-02` |
| **`TS-015`** | **Six named locations** including a no-signal basement and a moving vehicle, **three mobile operators**, three floor-spec devices, full-shift durations, on-device instrumentation, real technicians as executors, a server-side observer, and an `SP-030` safety briefing for testers | §2.2 `L-01`…`L-08`; `O-02` |

**Why it matters.** These are not preferences. `06-02` `G1-03` requires walk-in intake timed under
three minutes **by branch staff** on 20 samples; `G2-06` requires inventory accuracy **verified by
count**; `G2-02` and `G2-03` require 24-hour offline operation and 30-second sync **measured in the
field**, and `05-06` §1 gives "Field test" as the measurement method for `NFR-036` and `NFR-037`.
**Each of those is a physical activity written into an acceptance gate.** `TS-008` `UA-23` states the
consequence plainly: a stock script that does not touch stock proves the system will record whatever
it is told.

`TS-015` also raises a question nobody has answered: **testers will work at six locations, in a
moving vehicle and on customer premises, deliberately without connectivity — and therefore without a
means of contact.** `SP-030` governs technicians and does not mention test personnel (`TS-015`
`O-06`).

**Remediation instruction.** Allocate the hardware, the goods, the locations, the devices and the
people, as a named line in the wave plan. **Three packs and five gate criteria depend on it**, and it
cannot be improvised in the week before a gate.

---

### TS-07 — The category specifies roughly 1,600 executable items against 1 QA FTE

**Severity: HIGH · Status: OPEN · Owner: Programme Manager with CTO**

**What was found.** Enumerated from the files, not estimated:

| Pack | Enumerated items |
|---|---:|
| `TS-003` + `TS-004` + `TS-005` SIT | 148 scenarios |
| `TS-006` … `TS-011` UAT | 352 scripts |
| `TS-012` E2E | 18 scenarios, 20 executions |
| `TS-013` Regression | ~189 permanent-core cases + per-release derived sets |
| `TS-014` Performance | 37 scenarios |
| `TS-015` Offline | 33 field scripts |
| `TS-016` Accessibility | **189** (21 × 9 portals), **per portal release** |
| `TS-017` Security and privacy | **~734 derived cases**, no sampling permitted |
| **Total** | **~1,700 items**, several sets repeating per release |

`06-01` §4 provides **1 QA Engineer FTE at W1 and at W2**, rising to 2 from W3. `06-01` §4 also names
business availability as *"the binding constraint on the programme"*.

**Why it matters.** `TS-016` `AX-01` requires an automated scan **and** a manual audit before every
portal release, against `06-01` §5's monthly production cadence — that alone is not feasible for one
person across nine portals, and `TS-016` `O-06` says so. `TS-017` `SC-01` forbids sampling 379
denials. **The arithmetic does not close, and the packs are honest about it rather than silently
scoping down** (`TS-001` `O-08`, `TS-016` `O-06`, `TS-017` `O-06`).

**Remediation instruction.** Either resource the QA function against the enumerated volume, or agree
a documented risk-based reduction with the exclusions **logged at each gate** under `TS-013` `RS-13`.
Silent truncation reported as a full pass is the outcome this finding exists to prevent.

---

### TS-08 — Two authoritative end-to-end scenario sets exist and disagree

**Severity: MEDIUM · Status: OPEN · Owner: Enterprise Architecture with Programme Content Lead**

**What was found.** The register describes `TS-012` as *"one end-to-end scenario per revenue stream"*
and traces it to `README` §Fourteen Revenue Streams. **`05-06` §11 independently enumerates fifteen
critical journeys covered by end-to-end tests.** The lists are not the same and neither contains the
other: `05-06` omits four revenue streams (warranty extension sale, spare parts and accessories,
backup subscription, advertising and boost) and adds four journeys that are not revenue streams
(procure-to-pay, payroll, complaint-to-CAPA, month-end close). It also splits stream 2 across three
journeys and merges streams 10 and 11 into one.

`TS-012` §1.1 reconciles them to **18 scenarios in 20 executions** and proves the coverage in both
directions with zero orphans.

**Why it is reported rather than treated as resolved.** The reconciliation is sound, but **the two
source documents still disagree with each other and with the register.** A future reader finding
"18" beside a register that says "one per revenue stream" and a specification that says fifteen will
reasonably treat one as an error — most likely by deleting the four support scenarios, which carry
more `P0` business rules than any other group in the pack.

**Remediation instruction.** Add a cross-reference from `05-06` §11 to `TS-012`, and restate the
register row. Recorded as `TS-012` `O-02`.

---

### TS-09 — Category 13 has no class-`C` allocation, and that is correct

**Severity: MEDIUM · Status: FIXED (declared) · Owner: Programme Content Lead**

**What was found.** `CG-002` §4.1 allocates Category 13 as **0 A / 0 B / 0 C / 4 D / 14 E**. Several
packs' failure modes read as class `C` operational-critical — *"wrong transaction, wrong dispatch,
wrong stock, wrong pay"* is a fair description of what `TS-004`, `TS-008`, `TS-009` and `TS-010`
exist to prevent.

**The allocation is nevertheless right, and the reasoning is recorded so it is not "corrected".**
Class is assigned by the consequence of the *content* being wrong, not by the consequence of the
process it describes. **Test content never itself transacts.** A wrong SIT scenario causes a defect
to be missed; the wrong *transaction* is caused by the code the scenario failed to catch. The
consequence of wrong test content is therefore bounded by the process it verifies, and `CG-002` §6
matches — it gives Category 13 the approver class **"E / D"** with the QA Lead accountable.

**Why it was reported.** A future auditor comparing `TS-009`'s statutory subject matter against a
zero in the `A` and `C` columns would reasonably reclassify it, which would move the approver from
the QA Lead to the CFO plus the Business Owners Forum and change the review path for fourteen files.

**Remediation instruction.** None to the allocation. Add a note to `CG-002` §4.1 recording why
Category 13 carries no `A`, `B` or `C` files.

---

### TS-10 — Six roles have no course pack and one 51+-headcount role has no SOP

**Severity: MEDIUM · Status: OPEN · Owner: L&D Lead with Business Process Analysts**

**What was found.** `UA-03` requires an executor to be trained before execution and `UA-15` requires
each script to name the `SP` procedure it performs, so a UAT failure can be diagnosed to the system,
the procedure or the training. Building those two columns required resolving every `SP` and `TR`
identifier against the files on disk, and the resolution found gaps:

| Role | Headcount | Missing |
|---|---:|---|
| `R06` Branch Manager | **51+** | **No SOP.** `06B` holds 28 SOPs and none is the branch manager's procedure; the nearest are `SP-019` cash and `SP-032` checklists |
| `R05` Operations Director | 1–2 | No course pack |
| `R13` Remote Support Engineer | 15–40 | No course pack |
| `R14` Data Services Technician | 5–12 | No course pack — **and the only role with `T5` restricted-data access** |
| `R28` Warranty Claims Officer | 4–10 | No course pack — **and it runs the entire claim pipeline against a `KPI-038` leakage target** |
| `R25` Retail / Refurbishment Officer | 5–15 | No course pack |
| `R23` Marketing Manager | 2–4 | No course pack **and no SOP** |
| `R03` CFO, `R29` Cashier | 1, **51+** | No course pack |

**Why it matters.** Nine roles across three packs cannot satisfy `UA-03`, and eleven of `TS-006`'s
twelve `R06` scripts have no `SP` to diagnose against. `AUDIT-009` already recorded *"four roles on
declared interim routes; three roles unregistered in `MD-009`"* — **this is the same gap seen from the
test side, and the test side is where it becomes blocking**, because an untrained executor measures
training rather than the system.

**Remediation instruction.** This is a Category 06 and Category 08 register decision, not a Category
13 one: register the missing SOP and course packs, or record the interim routes explicitly per role.
Recorded as `TS-006` `O-05`/`O-07`, `TS-007` `O-05`, `TS-009` `O-05`.

---

### TS-11 — Category 13 was recorded as complete before any of its files existed

**Severity: MEDIUM · Status: FIXED · Owner: Programme Content Lead**

**What was found.** At the start of this audit, both the Master Index and the README recorded
Category 13 as *"Complete — 18 of 18, all at `Draft`"* with an enumeration stamp of **2026-08-18**,
and the §1 completion figure of **352 of 452** counted `13 TS (18)` among its components.

**On 2026-08-18 the folder `13_Test_and_Acceptance_Content/` was empty.** The 18 files were authored
on 2026-08-19 and enumerated for the first time in this report.

**Why it matters.** The figure is now true, but it was true by the coincidence of the authoring
finishing shortly after the claim. **This is precisely the failure gate F7 was written to prevent** —
a summary written before the derivation it summarises — and it is the fifth recorded instance of it,
after `AUDIT-002`, `AUDIT-003`, `AUDIT-005` and `AUDIT-012` `BN-19`. The variant here is new and
worse: the previous four were *stale* figures that lagged reality; this one **led** it. A completion
figure that anticipates authoring is unfalsifiable at the moment it is written, and `CP-11` exists to
prohibit exactly that.

**Remediation applied.** Enumeration stamps re-dated to 2026-08-19 with the derivation recorded; a
Category 13 status row added to Master Index §12; the README Category 13 row restated against the
counted figure. See §5.

---

### TS-12 — Four Category 99 and 14 dependencies block work that starts at W1

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with BI Lead**

**What was found.** Four unwritten files are named as operative preconditions by Category 13:

| Unwritten | Needed by | Consequence |
|---|---|---|
| **`RF-003`** traceability register | `TS-001` `TX-24`, `O-02` | 18 packs carry 18 local traceability tables and no consolidated coverage view exists — `G4-10` unanswerable |
| **`RF-006`** decision log | `TS-018` `TR-10`, `O-03` | Precedent-setting triage decisions have nowhere to go. **This is the exposure `AF-04` recorded for the module repository's missing `00-05`, and `RF-006` was created in this register specifically so content would not repeat it** |
| **`RP-001`** KPI dictionary | `TS-005` `O-04`, `TS-012` `O-03`, `TS-006` `O-06` | `SL-26` requires analytics outcomes recomputed independently — of what? |
| **`RP-004`** operational dashboards | `TS-006` `O-06` | `UAT-R06-001` asks a branch manager to judge an undesigned screen |

**`RP-001` is now blocked-on by five files across four categories** — `HC-008` `O-01`, `TR-011`
`O-01`, `TS-005` `O-04`, `TS-006` `O-06`, `TS-012` `O-03`.

**Remediation instruction.** Sequence `RP-001`, `RF-003` and `RF-006` ahead of the remaining
categories. `AUDIT-010` R-06 already asked for `RP-001` at W1; **this is the second request and the
dependency count has grown from two files to five.**

---

### TS-13 — One proposed identifier is cited before registration

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead**

**What was found.** Extraction `X1` resolved **244 distinct content identifiers cited across the 18
files; 243 are registered.** The exception is **`SP-035`**, cited in `TS-006` `O-05` as the identifier
a branch-management SOP would take if one were registered.

**Why it is reported.** `CM-R1` is register-first: a content file requires a register entry *before*
the file is created, and by extension an ID should not be cited before allocation. The citation is
explicitly conditional — *"either `SP-035` is registered or the register records the gap
deliberately"* — and it follows the precedent `AUDIT-009` `TR-01` set for `TR-025` and `AUDIT-012`
`BN-01` set for `BN-019`. **Three categories have now proposed a new file by citing an unallocated
ID**, which makes it a register-process question rather than three authoring lapses.

**Remediation instruction.** Either allocate `SP-035` (taking Category 06 to 35 files) or record the
`R06` SOP gap as accepted. Separately, `CG-005` should state how a proposed-but-unallocated ID is to
be written, so extraction can distinguish a proposal from an error. **`TR-025`, `BN-019` and `SP-035`
are now three outstanding register changes that between them would take the total from 452 to 455.**

---

### TS-14 — `TPL_Test_Script.md` has no pack-level or library variant

**Severity: LOW · Status: FIXED (declared and contained) · Owner: Content Design**

**What was found.** `CG-009` §3 allocates template 11 to 15 `TS` files. That template is designed
for **one test script** — traceability, preconditions, a per-step grid, exit criteria, defects,
sign-off. **None of the 15 is a single script.** Three are scenario libraries, six are role packs, one
is an end-to-end pack, and the rest are per-target or per-portal packs enumerating between 33 and 734
items.

**How it was contained.** All 15 retain every template section in order, answered at pack or library
level with the interpretation declared in a conformance note, and each addition justified where it
appears. **`E7` passes on all 15.** §3 Scripts becomes the enumeration plus a step pattern; §5 and §6
become the recording and signature obligations.

**This is the fourth occurrence of the same template-set defect.** `AUDIT-008` KB-10 found it in
`TPL_Knowledge_Article.md`, `AUDIT-009` TR-11 in `TPL_Training_Course_Pack.md`, `AUDIT-010` HC-11 in
`TPL_Help_Article.md`. **Four categories have now adapted four templates the same way.**

**Remediation instruction.** Add a **specification / pack variant** to `_templates/` usable across
`KB`, `TR`, `HC` and `TS`, or amend `CG-009` §3 once to permit the declared adaptation. Combines with
`AUDIT-008` R-05, `AUDIT-009` R-09 and `AUDIT-010` R-10 — **this recommendation has now been made four
times and has passed check `G1`'s escalation threshold twice over.**

---

### TS-15 — The auditor's own gate-criteria count was estimated, not counted

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** `TS-001` §1 and §5, and `TS-018`'s source block and §5, each stated that `06-02`
§4 sets *"87 named criteria"*. **Extraction `X5` counted 70**: `G1` 12, `G2` 10, `G3` 9, `G4` 10,
`G5` 7, `G6` 6, `G7` 6, `G8` 5, `G9` 5.

`TS-018` §4.5's own per-gate table carried the correct per-gate numbers, which sum to 70. **So one
file contained both the right derivation and the wrong summary of it, two sections apart** — the
exact internal inconsistency `AUDIT-005` found when a corrected figure was restated two lines below
the row that had just changed.

**Why it is reported rather than quietly fixed.** It was authored by this auditor, in the file whose
own rule `TX-24` requires coverage figures to be counted rather than estimated. **A traceability
standard that estimates its own denominator is the finding, not the typo.**

**Remediation applied.** All four occurrences corrected to **70**, with the per-gate derivation and
an enumeration date inline so the figure can be re-checked without re-counting.

---

### TS-16 — A module-scoped rule was cited without attribution

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Extraction `X2` resolved 137 `BRU-` citations. **136 resolve in `05-05`;
`BRU-QMS-09` does not** — it exists only in `M23` §9, as does `AUT-QMS-06`. `TS-003` `SIT-B-009` cited
both without naming their owning module, while `TS-018`'s source block attributed the same rule to
`M23` §9 correctly.

`AUDIT-010` X2 established the convention for module-scoped families (`BRU-CAI-*` → `M32`,
`BRU-KMS-*` → `M61`). **`BRU-QMS-*` is the first family that is *partially* in `05-05` — rules 01–05 —
and continues to 20 in its module**, which is why the citation slipped: the prefix resolves, the
number does not.

**Remediation applied.** `TS-003` `SIT-B-009` now states that `BRU-QMS-09` and `AUT-QMS-06` resolve
in `M23` §9 and §12 rather than in `05-05`. The partial-family pattern is recorded in §2 of this
report so the next author meets it in the audit trail rather than in an extraction.

---

### TS-17 — Still no accessibility reviewer, for the fourth consecutive category

**Severity: LOW · Status: OPEN · Owner: Content Design Lead**

**What was found.** `TS-016` cannot be executed without a named accessibility reviewer, and
additionally requires **a Bengali-speaking assisted tester** with their own assistive technology —
nine of its `P0` scripts depend entirely on that one person (`AX-02`, `CG-011` §8.2, `VB-009`
`AC-06`).

**No accessibility reviewer is named.** `TR-003` `O-02`, `HC-002` `O-04`, `HC-016` `O-04`,
`AUDIT-009` TR-03 and `AUDIT-010` HC-10 all record it; `AUDIT-010` R-09 escalated it under check
`G1` for having reached three consecutive audits. **This is the fourth request.**

**Why the severity is Low and the risk is not.** It is a resourcing gap on a known contractual
requirement (`PS-04`) rather than a content defect — but `TS-016` is the file that turns the
conformance claim into evidence, and it has no executor. The Bengali assisted tester is a **separate**
sourcing task from the reviewer, and it has never been raised before.

**Remediation instruction.** Name the reviewer once, for all content categories, and source the
Bengali assisted tester as a distinct action. Recorded as `TS-016` `O-02` and `O-03`.

---

## 4. Inbound findings resolved

| Finding | Source | Resolution |
|---|---|---|
| **`TR-001` `O-06`** and **`TR-003` `O-01`** — *"the sandbox and training test data (`TS-002`) is a Category 13 deliverable that Category 08 depends on. **Every practical exercise in every pack assumes it exists.** Category 13 is unstarted"* | `AUDIT-009` category work | **Partially resolved.** `TS-002` now exists and specifies the pack: 11 personas mapped to the `HC-001` §4.1 audiences, name and address sets with labelled match answers, all seven operator prefixes, reserved synthetic statutory blocks, device identities, 99 approval-boundary amounts and an 11-part Bengali stress set with stated collation order. **A `TRAIN` volume profile and a per-cohort reset rule are specified for Category 08's benefit** (`TD-15`). **The specification is not the data**: `TS-002` `O-07` records that generation must be scheduled, and `O-06` that Bengali authoring is unresourced. `TR-003` `DS-14`'s screenshot requirement is now satisfiable in principle |
| **`TR-005`** practical-assessment data reference | `AUDIT-009` | Resolved by the same `TRAIN` profile |
| **`AUDIT-010` HC-05 / `AUDIT-008` KB-05** — the `M61` W6 offline mechanism against earlier consumers | Prior audits | **Extended, not resolved.** `TS-015` `OFF-020`, `OFF-021` and `OFF-018` and `TS-005` `SIT-I-010`/`-012` add four more consumers. `TS-015` `O-03` states the sharpest form of it: **`04-00` `P02` non-negotiable 7 says no feature may require a connection, and offline knowledge is a listed `P02` capability**, so a W6 mechanism makes a W2 non-negotiable unmeetable. **Folded into `AUDIT-008` R-03 rather than raised separately** |
| **`AUDIT-013` LG-01** — gate F3 fails: `DT-031` maps nine `MD-028` fields that do not exist | `AUDIT-013` | **Confirmed from the test side.** `TS-007` `UAT-R22-010` verifies a service credit computed from a measured SLA breach and `TS-007` `O-06` records that `LG-015` does not exist, so the credit has no contractual counterpart. **Category 13 cannot test its way past F3** |

---

## 5. Remediation applied during this audit

| # | Change | File |
|---|---|---|
| 1 | Gate-criteria count corrected 87 → **70**, with the per-gate derivation and an enumeration date inline (TS-15) | `TS-001` §1, §5; `TS-018` sources, §5 |
| 2 | `BRU-QMS-09` and `AUT-QMS-06` attributed to `M23` §9 and §12 (TS-16) | `TS-003` §3.3 |
| 3 | Master Index §1 completion note re-stamped: enumeration date **2026-08-19**, Category 13 counted rather than anticipated (TS-11) | Master Index §1 |
| 4 | **Category 13 status row added** to Master Index §12 | Master Index §12 |
| 5 | `AUDIT-014` added to the `_AUDIT/` folder tree in §3.2 | Master Index §3.2 |
| 6 | README completion note re-stamped and the Category 13 row restated against the counted figure | README |
| 7 | `AUDIT-014` added to the README audit list | README |

**Not remediated, deliberately:** the missing `AUDIT-011` (TS-03). Writing a Category 12 audit under a
Category 13 mandate would produce a second report nobody had mandated; the four broken references are
reported instead.

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Declare one governing requirement total** and reconcile `05-01`'s title and the `_MODULE_SET_AUDIT_REPORT` restatement to it (TS-01). Closes `AF-06`. **No coverage figure can be quoted until this is done** | **Enterprise Architecture with CTO** | **W1 — before the first coverage statement** |
| **R-02** | **Correct the register's sequencing basis once, register-wide**, and with it the nine Category 13 waves and `TS-016`'s priority (TS-02). **Do not patch file by file** — that was `AUDIT-010` R-02 and the pattern recurred here at four times the volume | Programme Content Lead | **W1 — before Categories 14–19, 99 are authored** |
| **R-03** | **Produce `AUDIT-011` for Category 12 `DM`, or withdraw the ID and correct all four references** (TS-03). Until then the `DM` findings quoted in the register and README have no source and the README carries a broken link | Programme Content Lead | **W1** |
| **R-04** | **Resolve the four `NFR` identifier defects** — the `NFR-090`/`091`/`092` double allocation first (TS-04) — and restate the Master Index's `TS-014` trace | Enterprise Architecture with CTO | **W1 — before a pack cites an NFR by number** |
| **R-05** | **Specify and provision the 38 role accounts per environment** (TS-05). `TS-017`'s ~734 cases, `G1-06` and `G1-09` all depend on it | `M29` owner with Security Lead | **W1 — before SIT entry** |
| **R-06** | **Allocate the physical test resources** — counter hardware, staged stock, six field locations, three operators, floor-spec devices, and an `SP-030` briefing covering test personnel (TS-06) | Programme Manager with CTO | **W2 — before `G2`** |
| **R-07** | **Resource QA against the enumerated ~1,700 items, or agree a documented risk-based reduction with exclusions logged at every gate** (TS-07) | Programme Manager with CTO | **W1** |
| **R-08** | **Cross-reference `05-06` §11 to `TS-012` and restate the register's E2E row** (TS-08) | Enterprise Architecture | W2 |
| **R-09** | **Register the missing `R06` SOP and the six missing course packs, or record the interim routes per role** (TS-10). Third category to surface this | L&D Lead with Business Process Analysts | **W1** |
| **R-10** | **Sequence `RP-001`, `RF-003` and `RF-006` ahead of the remaining categories** (TS-12). `RP-001` is now blocked-on by five files across four categories — **second request** | BI Lead with Programme Content Lead | **W1** |
| **R-11** | **Decide `SP-035`, and state in `CG-005` how a proposed-but-unallocated ID is written** (TS-13). `TR-025`, `BN-019` and `SP-035` together would take the register from 452 to 455 | Programme Content Lead | W2 |
| **R-12** | **Add a specification / pack variant to `_templates/`, or amend `CG-009` §3 once** (TS-14) — **fourth request**, superseding `AUDIT-008` R-05, `AUDIT-009` R-09 and `AUDIT-010` R-10 | Content Design | **W2** |
| **R-13** | **Name one accessibility reviewer for all content categories** (TS-17) — **fourth request** — **and separately source a Bengali-speaking assisted tester**, which has not been requested before | Content Design Lead | **W1** |

---

## 7. Closure

Category 13 is **complete as specified**: 18 of 18 files written, all seven cross-register dimensions
reconciling exactly, 13 internal links resolving, and every one of 244 content identifiers, 137
`BRU-` rules, 87 `NFR-`, 52 `KPI-`, 59 gate criteria and every `FR-`, `SOD-`, `EA-`, `DI-`, `AS-`,
`OPS-`, `AUT-` and `PRU-` identifier resolving to its owning register. `TS-017`'s derived 77/379
portal-cell split was independently re-enumerated from `05-04` §2 and is exact.

**Four observations belong in front of the Steering Committee.**

**First, this category cannot report what it exists to report.** TS-01 is not a documentation defect.
Category 13's purpose is to convert 2,900-odd requirements into scripts and then state what
proportion has been proven, and the programme holds three current totals differing by up to 991
requirements. `TS-001` refuses to emit a bare percentage, which is the correct content response and
also an admission that the register cannot yet do its job. **`G4-10` — every v1.0 requirement
demonstrated as delivered or formally superseded — is currently unanswerable.**

**Second, the sequencing defect is now measured rather than suspected.** `AUDIT-008` found three
instances, `AUDIT-009` two, `AUDIT-010` two plus a variant, and this audit **nine — half the
category, seven of them consumed at `G1`.** Twenty instances across four consecutive categories is a
register-wide property. Category 13 is where it becomes undeniable, because a test pack's consumer is
not a judgement about maturity but a gate with a published date. **`AUDIT-010` §7 predicted that the
remaining twelve categories would inherit the defect unless the basis was corrected once. Four
categories later, it has.**

**Third, three of the eighteen files cannot be executed at all** — not delayed, not degraded.
`TS-017` has no accounts, `TS-015` has no field logistics, `TS-008` has no stock or hardware, and
`TS-016` has no reviewer. Between them they evidence `G1-06`, `G1-07`, `G1-09`, `G1-10`, `G2-02`,
`G2-03`, `G2-06` and `G2-07`. **The first two gates are currently unevidenceable, and the cause is
resourcing rather than content.**

**Fourth, the audit trail itself now has a hole.** TS-03 is the first finding in fourteen audits
about the `_AUDIT` folder rather than about content. `AUDIT-011` is cited in four places, one of them
a live markdown link, and does not exist — while Category 12's critical finding is quoted from it in
two documents. The cause was a correct decision (renumbering to respect a register allocation)
followed by an unfilled slot, which is a more instructive failure than a careless one: **`CP-02` was
honoured and the artefact was still lost.**

| Rule | Status |
|---|---|
| `CM-R1` register-first | ✅ All 18 registered before authoring; zero divergence both directions. ⚠ One proposed ID cited (TS-13) |
| `CM-R2` figures regenerated by enumeration | ⚠ **Failed before this audit and now corrected** — the completion figure led the authoring (TS-11) |
| `CM-R8` every claim sourced and dated | ✅ External facts — operator prefixes, NID forms, 13-digit e-BIN, Mushak 6.3 mandatory fields — carry sources and verification dates |
| `CM-R9` audit on category completion | ✅ This report |
| `CP-02` IDs permanent, never reused | ✅ Honoured — **and TS-03 shows honouring it is not sufficient** |
| `CP-11` counted, not estimated | ⚠ **Two breaches found and fixed** (TS-11, TS-15); all figures now enumerated 2026-08-19 |
| `RG-06` never read what a document says about itself | ✅ Every check by extraction, **including against this category's own files** |
| Gate **F7** category-completion reconciliation | ✅ **Seven dimensions, zero divergence** |
| Check **D1** all internal links resolve | ⚠ **Fails repository-wide** — the README link to `AUDIT-011` (TS-03) |
| Check **G1** findings open across three audits | ⚠ **Three recommendations past the threshold: R-12 template variant (4th), R-13 accessibility reviewer (4th), R-10 `RP-001` (2nd but now five dependants)** |

> **Index note.** This report and `AUDIT-001` through `AUDIT-013` must be indexed in `RF-012` when
> Category 99 `RF` is authored. `AUDIT-011` must be resolved before that index is written, or the
> index will record a report that does not exist.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
