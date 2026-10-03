---
id: FIX-ERP2-AUDIT-019
title: Category 16 CM — Change Management & Communications Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-20
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 18 Category 16 CM files, their citations into the module repository and the content register, cross-register integrity, gate F7, and the concurrent-authoring conditions under which the category was written
mandate: Audit required on completion of Category 16 authoring (rule CM-R9)
extends: AUDIT-001 … AUDIT-018
enumeration_date: 2026-08-20
method: Filesystem enumeration and identifier extraction only (RG-06, CP-11). No figure in this report is projected, and none is taken from what a document says about itself — including what this category's own files say about themselves, and including what the register said about other categories while this one was being written.
---

# Category 16 `CM` — Change Management & Communications Content Audit
### 18 files · 428 of 452 registered content files now written

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F7 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration and extraction. **Enumeration date
2026-08-20.**

Nine category-specific extractions were run:

| Extraction | What was compared |
|---|---|
| **X1** | Every content identifier cited, against the 452 register rows |
| **X2** | Every gate criterion `Gn-nn` against `06-02` §4 |
| **X3** | Every `RSK-`, `DEP-`, `ASM-`, `CON-` and `D-` identifier against `00-04` |
| **X4** | Every `BRU-PIC-` and `FR-PIC-` identifier against `M57` |
| **X5** | Every `Rnn` role and `PS-nn` portal standard against `05-04` §1 and `04-00` §3 |
| **X6** | Every cross-category rule citation (`CV-`, `SH-`, `PK-`, `HX-`, `HD-`, `FW-`, `KI-`, `CP-`) against its owning file |
| **X7** | Register filenames against disk, byte for byte; register row cell counts |
| **X8** | **Every absence claim** — each statement that a file, category or artefact does not exist, tested against the filesystem |
| **X9** | Rule-prefix uniqueness within the category, and collision against every `[A-Z]{2}-nn` prefix in `project_content/` |

**Fourteen findings — 1 critical, 5 high, 6 medium, 2 low.** Four were remediated during the
audit; ten are open, and seven of those are owned outside the content function.

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| Critical | 1 | **1** | 0 |
| High | 5 | 1 | 4 |
| Medium | 6 | 2 | 4 |
| Low | 2 | 0 | 2 |

> **The Critical finding is against the auditor's own authoring, and it is the reason this report
> exists in the form it does.** The convention inherited from audit `00-07` requires that where the
> auditor's prior work caused a finding, the cause is stated rather than the fix. `CM-01` is that
> statement.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | 18 of 18 ✅ |
| **A2** Total written | **428 of 452**, enumerated 2026-08-20 ✅ |
| **A5** Files on disk with no register entry | Zero ✅ |
| **B1** ID uniqueness | 18 unique ✅ |
| **B2** Contiguity `CM-001`…`CM-018` | No gaps ✅ |
| **B4** File name matches ID | 18 of 18 ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 18 of 18 ✅ |
| **D1** Internal links resolve | **49 relative links, zero broken** ✅ *(24 before remediation; the increase is `CM-01`'s fix)* |
| **D2** Files in their declared subfolder | **18 flat**, matching Master Index §3.2 — Category 16 declares no subfolders ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E7** Template conformance | All six `TPL_Content_File_Front_Matter.md` sections present in all 18, in order, with §7 Open Items added per category convention (`TR-03`) ✅ |
| **F1** Front matter complete | **All 24 required keys present in all 18** ✅ |
| **X1** Content-ID citations | **128 distinct identifiers cited, 128 registered** ✅ |
| **X2** Gate criteria | **21 distinct cited, all 21 resolve** in `06-02` §4 ✅ |
| **X3** Risk and governance identifiers | **39 distinct `RSK-`/`DEP-`/`ASM-`/`CON-`/`D-` cited, all resolve** in `00-04` ✅ |
| **X4** `M57` identifiers | **13 `BRU-PIC-` and 3 `FR-PIC-` cited, all resolve** ✅ |
| **X5** Roles and portal standards | **34 `Rnn` and 2 `PS-nn` cited, all resolve** ✅ |
| **X6** Cross-category rules | `CV-` ×12 → `DM-014` · `PK-` ×1 → `TR-023` · `HX-` ×6, `HD-` ×4, `FW-` ×1, `KI-` ×4 → `OP-002` · `CP-` ×3 → Master Index §2 — **all resolve after remediation** ✅ *(one `SH-` mis-attribution corrected — `CM-10`)* |
| **X7** Register filenames vs disk | **Byte-identical, both directions.** All 18 register rows carry 8 cells against an 8-cell header ✅ |
| **X9** Rule-prefix integrity | **18 prefixes, all unique within the category, none colliding with any of the 178 `[A-Z]{2}-nn` prefixes already in use** ✅ |

### 2.1 Cross-register reconciliation — gate F7

**All seven dimensions reconcile exactly.**

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---|---:|:--:|
| File count | Master Index §4 | 18 | 18 | ✅ |
| Priority `P0`/`P1`/`P2`/`P3` | Master Index §1 | 0 / 7 / 9 / 2 | 0 / 7 / 9 / 2 | ✅ |
| Wave per file | Master Index §4 rows | W0×4, W1×9, W2×3, W3×1, W4×1 | All 18 match | ✅ |
| Content class A/B/C/D/E | `CG-002` §4.1 | 0 / 0 / 0 / 16 / 2 | 0 / 0 / 0 / 16 / 2 | ✅ |
| Bilingual / English-only | `CG-010` §3.2 | 12 / 6 | 12 / 6 | ✅ |
| Template allocation | `CG-009` §3 | 18 generic | 18 generic | ✅ |
| Subfolder allocation | Master Index §3.2 | 18 flat | 18 flat | ✅ |

**The two class-`E` files are `CM-002` and `CM-003`** — the stakeholder register and the
communication calendar. Both are planning instruments whose failure mode is *"inconsistency,
rework, unmaintainable content"* (`CG-002` §4) rather than a user-facing failure. The remaining
sixteen are class `D`, approved by the Content Design Lead, with **every people-related response in
`CM-011` and every recognition or incentive statement in `CM-017` additionally requiring HR Director
approval** — recorded here so the additional gate is not later dropped as an authoring flourish.

**The six English-only files are `CM-002`, `CM-003`, `CM-004`, `CM-009`, `CM-014` and `CM-018`.**
`CG-010` §3.2's rationale — *"anything reaching branch, field or customer audiences; executive and
PMO material is English"* — resolves as: **three templates** (`CM-004` steering pack, `CM-009`
newsletter, `CM-018` change impact statement), **two PMO planning instruments** (`CM-002`, `CM-003`),
and **one corporate-English file** (`CM-014`, per `CG-010` §3.3's rule that corporate contractual and
technical documents are English).

> **The template allocation carries a risk that is mitigated in the files rather than by the
> allocation.** `CM-009` and `CM-018` are English templates whose **every instance** is bilingual.
> `NL-11` and `CI-14` make that binding; `CM-009` states it three times for that reason. This is
> the same treatment `CG-009` §3 gives `NT-001`, `DT-001` and `HC-002`, so the allocation is
> precedented — but it is the allocation most easily misread as permission to publish in English.

### 2.2 What the category contains

| Measure | Value |
|---|---:|
| Files | 18 |
| Lines | **6,980** |
| Governing rules defined | **313**, across 18 unique prefixes |
| Open items raised | **109** |
| Relative links | 49, all resolving |
| Distinct content identifiers cited | 128 |

---

## 3. Findings

### CM-01 — The category was authored against a stale register, and asserted twenty-four times that four written categories were empty

**Severity: CRITICAL · Status: FIXED during the audit · Owner: Programme Content Lead — the
auditor's own authoring**

**What was found.** Enumeration of `project_content/` on 2026-08-20 returns **428 files**.
Categories 14 `RP` (16), 15 `AP` (12), 17 `OP` (16) and 18 `EO` (14) — **58 files** — are on disk and
at `Draft`.

Category 16 was authored against the register's §12 status table and the README, both of which
stated **352 of 452** and *"Categories 14–19, 99 — Not started"*. The result:

| Claim made in the `CM` files | Files it asserted did not exist | Actually on disk |
|---|---:|---:|
| *"Category 17 `OP` holds zero files"* | 16 | **16** |
| *"Category 18 `EO` holds zero files"* | 14 | **14** |
| *"Category 14 `RP` holds zero files"* | 16 | **16** |
| *"The `OJ-11` monitoring disclosure does not exist"* | `LG-020` §4.6 | **written, at `Draft`** |
| **Total false absence assertions across the category** | **24 statements in 13 of 18 files** | |

**Why it is Critical.** `AUDIT_Checklist_Recurring.md` defines Critical as *"work done against the
wrong artefact, or a required artefact assumed present when absent"*. This is the mirror image and
is no less damaging: **eighteen files were written on the assumption that their principal
dependencies did not exist.** The consequences were not cosmetic —

- **`CM-007` invented a hypercare model** that `OP-002` already owns, and contradicted it on
  duration, on the known-issue log, and on the ageing rule (`CM-02`).
- **`CM-005`, `CM-006`, `CM-007` and `CM-008` printed support routes with no commitment**, when
  `OP-001` §4.7 states them per severity.
- **`CM-011` `OB-09` was recorded as unanswerable** when `OP-014` answers it, and `OB-02` was
  recorded as having no disclosure when `LG-020` §4.6 is the disclosure.
- **`CM-014` and `CM-015` treated the `EO` boundary as hypothetical** when `AUDIT-018` had already
  raised it as a live finding with a recommendation (`CM-09`).
- **`CM-016` reported ten targets without baselines** when `RP-015` had already enumerated **44 of
  95 KPIs with no usable baseline**, a materially larger and better-evidenced statement.

**How it happened, stated plainly.** The register's §12 status table was read and believed. **Rule
`RG-06` exists to prevent exactly that**, and `CP-11` restates it: *"completion percentages are
produced by enumerating the filesystem, never by projecting."* The rule was applied rigorously to
Category 16's own counts and not applied at all to the categories Category 16 depends on. **An
enumeration discipline that covers only the work in front of you is not an enumeration
discipline.**

The condition that made it likely is worth recording because it will recur: **Categories 14, 15,
17 and 18 were being authored concurrently.** `AUDIT-015` through `AUDIT-018` are dated within
sixteen minutes of one another and the register was updated after all four. A category author
reading the register mid-sweep reads a figure that was true when it was written and false when it
was read.

**Remediation applied.** All 24 assertions corrected; 25 relative links added to the four
categories concerned; five open items rewritten from *"the file does not exist"* to the real,
narrower finding that survived contact with the file. Link count rose from 24 to 49. Detail in §5.

**Proposed rule, for `RG-08`'s neighbourhood.** *A category author enumerates every category their
files cite, at the moment of authoring, and records the enumeration date in the file. The register's
status table is not a source for what exists.* Recorded for the Programme Content Lead's decision.

---

### CM-02 — `CM-007` contradicted `OP-002` on three points, and one of them was the exit criteria

**Severity: HIGH · Status: FIXED during the audit · Owner: Programme Content Lead**

**What was found.** `CM-007` was written as the communication half of a hypercare plan it believed
did not exist. `OP-002` exists, is 435 lines, and owns the model. Three direct contradictions:

| Subject | `CM-007` said | `OP-002` says | Governs |
|---|---|---|---|
| **Duration** | Weeks 1–4, exit notice in week 4 | **4–8 weeks per wave, as a minimum** (`HD-01`); 8 weeks for W1, W3 and W5; wave clock runs from the **last** tranche (`HD-03`) | `OP-002` |
| **Known-issue artefact** | A list this file owns, refreshed daily then twice weekly | A **log** `OP-002` §4.6 owns, refreshed **at every evening triage** (`KI-01`), with `CM-007`'s bulletin as a publication destination | `OP-002` for the log |
| **Ageing** | 10 working days → Steering Committee | **20 working days → problem record** (`KI-02`, `SP-031` §8) | `OP-002` |

**Why it matters.** A communication pack that ends in week four, for a hypercare period that runs
eight weeks at three of nine waves, stops broadcasting at the halfway point of the waves that
contain a month-end, a payroll run and a statutory filing.

**Remediation applied.** `CM-007` §4.4 rewritten as the **bulletin**, explicitly downstream of the
`OP-002` log, with the workaround entry condition (`KI-01`), the triage refresh, the `KI-02` ageing
handover and the `KI-03` customer mirroring taken from `OP-002`. §4.6 re-expressed against the
floor-walking period and the exit rather than fixed weeks (`HY-17`). §4.8 bound to `HX-01`…`HX-18`
and the §4.9 exit form, with a new `HY-18` requiring any waived criterion to be named. Rules
extended from 16 to 18.

---

### CM-03 — Two wave calendars are current, and a second content category has now taken the other side

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead with the PMO**

**What was found.** The repository states two different sets of wave months:

| Source | W1 | W2 | W3 | W4 | W5 |
|---|---|---|---|---|---|
| **`06-01` §3, §8 and `06-02` §4** (they agree) | **1–4** | 5–8 | 9–13 | 14–18 | 19–22 |
| **Master Index §1** *"Distribution by wave"* | **3–8** | 8–14 | 14–18 | 18–23 | 23–27 |

`CM-003` anchors to `06-01`/`06-02` and records the divergence as its `O-01`. **`OP-002` §4.3
anchors to the Master Index figures — and cites them to `06-01`.** Its duration table is headed
*"Months (`06-01`)"* and lists W1 as **3–8**.

**Why it is High.** Two `Draft` content files in two categories now schedule against two different
calendars, each believing it follows `06-01`. `CM-003`'s entire method is milestone anchoring
(`CA-01`, `CA-02`), which is robust against a *moved* gate and defenceless against a *wrong* one.

**Remediation instruction.** Enterprise Architecture or the PMO to declare one wave calendar and
correct the loser, once, register-wide. Recorded as `CM-003` `O-01` and cross-referenced here so it
is not corrected in one file at a time — the failure mode `AUDIT-014` TS-02 warned about.

---

### CM-04 — Three source documents state a four-week hypercare window that `OP-002` doubles

**Severity: HIGH · Status: OPEN · Owner: Programme Manager with the Support Lead**

**What was found.** Distinct from `CM-02`, which was a content contradiction. This is a **source**
contradiction that `OP-002` resolved unilaterally:

| Source | States |
|---|---|
| `06-01` §5 | *"Hypercare — four weeks of elevated support after every wave go-live"* |
| `06-01` §6 rollout pattern | `T+4 weeks   Hypercare ends; adoption review` |
| BRD §21.5–21.6 | *"4 weeks after every wave go-live, with a named lead and daily triage"* |
| **`OP-002` §4.3** | **4–8 weeks by wave, minimum not target**, W1/W3/W5 at 8 weeks |

`OP-002`'s reasoning is sound — `HD-02` requires a full business cycle inside the window, and a
month-end does not fit in four weeks — but **the three upstream documents have not been corrected**,
and `CM-003` §4.4 anchors the per-location communication pattern to `06-01` §6's `T+4 weeks`.

**Consequence.** M7 hypercare guidance, M8 adoption statement and the parallel-run reminder are all
scheduled against a window shorter than the one that will run. Recorded as `CM-003` `O-04` and
`CM-007` `O-02`.

---

### CM-05 — The register asks Category 16 for a leaderboard that a Class `H` rule prohibits

**Severity: HIGH · Status: OPEN · Owner: Chief Data Officer (or delegate under `D-15`) with the HR
Director**

**What was found.** The Master Index row for `CM-017` reads: *"Copy for adoption recognition,
**leaderboards**, milestones and incentive announcements."*

`M57` §9 `BRU-PIC-16` is a **Class `H` hard block**, owned by the CDO: *"Peer comparison is
anonymised; no employee sees another employee's individual score."* `BRU-PIC-14` additionally makes
performance ratings sensitivity class `S2`.

**A named individual leaderboard cannot be published.** `M57` provides no waiver route for
`BRU-PIC-16`.

**Why it is High.** The register commissions content that cannot lawfully be produced as described,
and the request is the single most common gamification pattern — it will be asked for repeatedly.

**Remediation applied in the file, not the register.** `CM-017` `RN-08` prohibits individual
leaderboards on any surface in any language, and §4.5 supplies four permitted substitutes:
own-trend, own-position-against-an-anonymised-distribution, own-position-against-target, and
**team or site comparison** — which `P06`'s branch league already does by design. `RN-14` makes team
recognition the designed substitute.

**Remediation instruction, open.** Correct the `CM-017` register row to remove *"leaderboards"* or
to qualify it as team-level. A register row that commissions a prohibited artefact will be honoured
by someone eventually.

---

### CM-06 — `CM-017` delivers a Critical-risk mitigation three waves after the risk

**Severity: HIGH · Status: OPEN · Owner: HR Director with the CFO and the PMO**

**What was found.** `RSK-008` — technician rejection of the mobile app — is rated `H`/`Critical`,
one of five risks `00-04` §1.5 says *"can end the programme"*. Its named mitigation in both `00-04`
§1.2 and BRD §21.5 is **"earnings and incentive visibility as an immediate personal benefit"**.

| Artefact | Wave |
|---|:--:|
| `P02` technician app, where the risk materialises | **W2** |
| `CM-017` recognition and incentive copy | **W2** |
| **`M57` incentive engine and scorecard** | **W5** |
| `M21` HR / salary of record | **W5** |

`BRU-PIC-01` blocks any calculation until a scheme version is approved by the HR Director and CFO.
**There is no scorecard and no incentive engine between W1 and W5**, so the mitigation for a
Critical risk is unavailable for three waves after the risk arrives.

**This is the twenty-first instance of the wave-sequencing defect**, following twenty across four
categories recorded in `AUDIT-008`, `-009`, `-010` and `-014`. It is the first in which the late
artefact is a **Critical-risk mitigation** rather than a test pack or a knowledge article.

**Remediation instruction.** Either bring forward a minimum scorecard-visibility capability to W2,
or record an accepted exception naming what replaces the mitigation for three waves. `CM-017` `O-06`
records that §4.6 named recognition and §4.5 team comparison are the only surfaces available in the
interval, and that neither has a budget.

---

### CM-07 — `CM-018` alone consumes the whole category effort estimate

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with the PMO**

**What was found.** `CM-018` §4.7 derives the effort for the per-role change impact statements from
its own production sequence: 2.5–3.5 days per statement, 3–4 bilingual, across **38 registered
roles** — **95–140 person-days**.

Master Index §7 allocates **90–140 person-days to all eighteen `CM` files**.

**The statements alone exceed the category estimate.** The other seventeen files — including three
that specify recurring production across nine waves — are unbudgeted.

**Why it is Medium rather than High.** The figure is an estimate, explicitly flagged in §7 as *"not
counted"*, and audit finding `AF-09` already escalates that the entire content estimate sits outside
the business case. This finding compounds `AF-09` rather than opening a new exposure — but it is
the first category to derive its own effort and find the register's figure wrong by roughly an order
of magnitude on one file.

**Remediation instruction.** Restate Master Index §7's `CM` row at the next `AF-09` escalation, not
separately. Recorded as `CM-018` `O-01`.

---

### CM-08 — Two enumerations of the external populations now exist, and they do not match

**Severity: MEDIUM · Status: OPEN · Owner: Change Lead with the Support Lead**

**What was found.** `CM-002` §4.3 registers ten external groups (`S18`–`S27`), derived from `04-00`
§2 and `05-04` §1.7. `OP-001` §4.1 independently enumerates **eleven external audiences** and
declares its own enumeration *"the definitive one"*, having found that the register's phrase
*"eleven external audiences"* is nowhere enumerated upstream.

| Divergence | `CM-002` | `OP-001` §4.1 |
|---|---|---|
| **Marketplace seller technicians** | **Absent** | **1,000–4,000** |
| Corporate users | One group, 500–2,000 | **Split**: end users 500–2,000; administrators 50–200 |
| Vendors and suppliers | 200–500 | 200–600 |
| Franchise and channel partners | Absent | 0–30 from W8 |

**Why it matters.** A stakeholder map missing a 1,000–4,000-person population is missing a
population — and it is the population that will actually use `P07` on a job. `CM-015` `O-06` records
the same gap from the transition side.

**Remediation instruction.** Adopt `OP-001` §4.1 as the single external enumeration and re-derive
`CM-002` §4.3 from it. Two files declaring themselves definitive is one too many.

---

### CM-09 — The `CM`-transition versus `EO`-onboarding boundary is stated on one side only

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with Account Management,
Procurement and Marketplace Operations**

**What was found.** `AUDIT-018` had already recorded this from the `EO` side, with recommendation
**R-07**: *"neither register row acknowledges the other"*, listing eleven `EO`↔`CM` overlaps
concentrated in `CM-013`, `CM-014`, `CM-015` and `CM-002`.

Category 16 reached the same conclusion independently. `CM-015` `VT-02` states the boundary —
*whether a commercial relationship already exists* — and `CM-014` `O-01` records that `EO-008` covers
the same approval-chain configuration as its own step 6 and asset B5.

**The convergence is the finding.** Two categories, audited two days apart by the same function,
each identified the overlap and each stated the boundary in its own file. **Neither register row
states it**, and `AUDIT-018` R-07 is open.

**Why it is Medium.** Both sides now describe the boundary in prose, which prevents the immediate
harm. The `TR-023`/`CM-008` precedent shows what happens if it is left there: `AUDIT-009` `TR-08`
recorded that overlap and it survived until `CM-008` §4.2 was authored to close it, one category
later. This is the same pattern with three files instead of one.

**Remediation instruction.** Execute `AUDIT-018` R-07 — add the reciprocal statement to the
`CM-013`, `CM-014` and `CM-015` register rows and to Master Index §5's Onboarding column. Then
mirror `CM-008` §4.2's twelve-row ownership table into the `EO` files, because prose boundaries
decay and tables do not.

---

### CM-10 — `SH-12` was attributed to the wrong owning file

**Severity: MEDIUM · Status: FIXED during the audit · Owner: Programme Content Lead**

**What was found.** `CM-006` §4.5 and `CM-013` §4.1 cited the legacy-reference searchability rule as
*"`DM-014` `SH-12`"* and, in one case, *"`DM-004`"*. `SH-12` belongs to **`DM-006`** — *"the legacy
number is indexed and searchable at the counter and in `P01`"*, Class `H`, implementing
`FR-SRM-088`, with `ERR-SVH-012` as its error.

`DM-014` §4.10 cites `SH-12` correctly; the mis-attribution was introduced by reading `DM-014`'s
citation rather than following it.

**Consequence, now corrected.** `CM-013`'s promise `P1` — *"your old reference still works"* — is the
pack's load-bearing claim, and `DM-006` states in terms that the register's promise *"is kept by
`SH-12` and by nothing else"*. Attributing it to the wrong file would have sent anyone verifying
the claim to a workbook that does not contain it.

**Remediation applied.** Both citations corrected to `DM-006` `SH-12` with `FR-SRM-088` named.
`CM-013` `O-02` and `O-03` rewritten: `O-02` now names the actual blocker — `DM-006` `O-01`, the
unresolved `M01` `Q-04` question of whether 3, 5 or all years of service history migrate — and
`O-03` narrows from *"no confirmed mechanism"* to the accurate *"specified mechanism, no
verification"*, because no `TS` test case exercises the counter or hotline lookup.

---

### CM-11 — Not one of the twelve bilingual files has a Bengali counterpart

**Severity: MEDIUM · Status: OPEN · Owner: Localisation Lead**

**What was found.** Twelve of eighteen files are `bilingual: yes` and each declares a
`bn_counterpart:`. **Zero `_BN.md` files exist in `16_Change_Management_and_Comms/`.** Check **B5**
therefore fails for the category, and `CM-R6` blocks all twelve from `Approved`.

The load is not uniform, and two files carry obligations that no capacity plan has been shown:

| File | Bengali obligation | Difficulty |
|---|---|---|
| `CM-007` | **The known-issue bulletin refreshes at every evening triage** — nightly, in Bengali | Against `CM-003` §4.5's 3-working-day minimum for a short notice. **The cadence and the lead time are in direct conflict** |
| `CM-009` | 36 monthly bilingual issues over three years | Small but permanent; in no capacity plan |
| `CM-005` | Four of six assets Bengali-first, reprinted per wave to 51+ sites | Print and distribution unfunded (`CM-005` `O-04`) |
| `CM-017` | S1 scorecard and earnings copy, Bengali-first | Copy about someone's money |

**Remediation instruction.** `CM-007` `O-05` is the one to resolve first: a nightly bilingual
bulletin either gets a same-day translation route or the bulletin is English at the sites that need
it most. Neither is acceptable as an unstated default.

---

### CM-12 — No Category 16 file can reach `Approved`, and the reasons are not all translation

**Severity: MEDIUM · Status: OPEN · Owner: Content Design Lead with the HR Director**

**What was found.** Gate status derived from `CG-007` §2.1 for class `D` and `E`:

| Gate | Applies to | Blocked because |
|---|---:|---|
| **G1 Editorial** | 18 | Not yet run |
| **G2 Factual** | 18 | Not yet run; **four files depend on decisions that are open** |
| **G4 Linguistic** | 12 | `CM-11` — no Bengali counterpart exists |
| **HR approval** *(additional, not a `CG-007` gate)* | `CM-011`, `CM-017` | Every people-related response and every recognition statement |
| Named approver | 18 | Content Design Lead not appointed to this work |

**Four files cannot pass G2 on content grounds rather than process grounds**, because a factual
review would have to confirm statements the company has not decided:

| File | Cannot be confirmed until |
|---|---|
| `CM-011` `OB-01` job security | `CON-10`'s standing is restated or reaffirmed |
| `CM-011` `OB-05` opening variances | The CFO and Operations Director confirm the amnesty position (`CM-011` `O-01`) |
| `CM-011` `OB-02` monitoring | `LG-020` `AU2` is answered — it **blocks `P02` go-live disclosure** |
| `CM-015` seller commercial statements | `D-03`, `D-09` and `D-10` close |

**Remediation instruction.** Run G1 across all eighteen now — it depends on nothing external. Hold
G2 on the four until their decisions land, and record the hold rather than passing them
conditionally.

---

### CM-13 — The `TR` prefix now carries three unrelated meanings

**Severity: LOW · Status: OPEN · Owner: Programme Content Lead**

**What was found.** Category 16 files cite `TR-` identifiers in three senses:

| Citation | Means | Owned by |
|---|---|---|
| `TR-002`, `TR-022`, `TR-023`, `TR-024` | Category 08 content files | Master Index §4 |
| `TR-01`…`TR-09` | Template register **rules** | `CG-009` §4 |
| `TR-08` | An **audit finding** | `AUDIT-009` |

`CM-004` cites `TR-09` (a template rule) and `CM-008` cites `TR-08` (an audit finding) within four
files of each other, and both look like Category 08 content identifiers.

**Why it is Low.** Every citation in this category is correct and each is disambiguated in context.
The risk is to the next author, not to this one.

**Remediation instruction.** `CG-005` §3.3 already establishes the disambiguation convention —
cite a rule with its owning document prefix. Applying it to `CG-009`'s rules would make them
`CG-009` `TR-09`. Recorded for `CG-005`'s next revision.

---

### CM-14 — The category's own completion figure was stamped while the category was being written

**Severity: LOW · Status: OPEN · Owner: Programme Content Lead**

**What was found.** Master Index §1 states **428 of 452**, *"Enumerated 2026-08-17 16:49 UTC"*, and
§12 records Category 16 as *"Complete on disk — 18 files (enumerated 2026-08-17 16:55 UTC)"*.

The 428 figure is **correct as at this audit's enumeration**, and is confirmed here independently.
But the register's own note discloses the pattern that produced it: *"the 427 figure stamped four
minutes earlier was a floor — it caught 17 `OP` mid-authoring at 15 of 16"*, recorded as `AUDIT-016`
AP-17 and proposed rule `RG-08`.

**A figure that is right by the time it is read, but was a floor when it was written, is still a
projection.** This is the third recorded instance — `AUDIT-014` TS-11, `AUDIT-016` AP-17, and this
one — and the first where the mid-authoring category is the one being audited.

**Remediation instruction.** Adopt proposed rule `RG-08`. This audit's §2 figure is stated with the
enumeration date and was produced by counting `<CODE>-nnn_*.md` across all 21 folders, after all
authoring in this category had stopped.

---

## 4. Findings summary

| ID | Severity | Finding | Owner | Status |
|---|:--:|---|---|:--:|
| **CM-01** | **CRITICAL** | Category authored against a stale register; 24 false absence assertions in 13 files | Programme Content Lead | **Fixed** |
| **CM-02** | High | `CM-007` contradicted `OP-002` on duration, known-issue ownership and ageing | Programme Content Lead | **Fixed** |
| **CM-03** | High | Two wave calendars current; `OP-002` has taken the other side | PMO / Enterprise Architecture | Open |
| **CM-04** | High | Four-week hypercare window in three sources; `OP-002` doubles it for three waves | Programme Manager | Open |
| **CM-05** | High | Register commissions a leaderboard that `BRU-PIC-16` prohibits | CDO with HR Director | Open |
| **CM-06** | High | `CM-017` delivers a Critical-risk mitigation three waves after the risk | HR Director with CFO | Open |
| **CM-07** | Medium | `CM-018` alone consumes the whole category effort estimate | Programme Content Lead | Open |
| **CM-08** | Medium | External population enumerations diverge from `OP-001` §4.1 | Change Lead with Support Lead | Open |
| **CM-09** | Medium | `CM`/`EO` boundary stated on one side only — converges with `AUDIT-018` R-07 | Programme Content Lead | Open |
| **CM-10** | Medium | `SH-12` attributed to `DM-014`/`DM-004` instead of `DM-006` | Programme Content Lead | **Fixed** |
| **CM-11** | Medium | Zero Bengali counterparts for twelve bilingual files; `CM-007`'s cadence is unachievable | Localisation Lead | Open |
| **CM-12** | Medium | No file can reach `Approved`; four blocked on undecided company positions | Content Design Lead with HR | Open |
| **CM-13** | Low | `TR` prefix carries three unrelated meanings | Programme Content Lead | Open |
| **CM-14** | Low | Completion figure stamped mid-authoring — third instance | Programme Content Lead | Open |

---

## 5. Remediation applied during the audit

Every change is listed. Nothing was changed silently.

| # | Change | Files | Finding |
|---:|---|---|---|
| 1 | 24 false absence assertions corrected to accurate references | `CM-002`, `-003`, `-004`, `-005`, `-006`, `-007`, `-008`, `-009`, `-011`, `-012`, `-014`, `-015`, `-016`, `-017` | CM-01 |
| 2 | 25 relative links added into Categories 14, 17 and 18 | as above | CM-01 |
| 3 | `CM-007` §4.4 rewritten as the **bulletin**, downstream of the `OP-002` §4.6 **log** | `CM-007` | CM-02 |
| 4 | `CM-007` §4.6 rhythm re-expressed against the floor-walking period and exit; new rule `HY-17` | `CM-007` | CM-02 |
| 5 | `CM-007` §4.8 bound to `HX-01`…`HX-18` and the §4.9 exit form; new rule `HY-18` on named waivers | `CM-007` | CM-02 |
| 6 | `CM-007` `HY-06`, `HY-11`, `HY-12`, `HY-13` restated against `KI-01`…`KI-04`; rules 16 → 18 | `CM-007` | CM-02 |
| 7 | Route 4 response commitments taken from `OP-001` §4.7 and printed | `CM-007` | CM-01 |
| 8 | Floor-walking model referenced to `OP-002` §4.4 rather than invented | `CM-007` | CM-02 |
| 9 | `SH-12` re-attributed to `DM-006`, with `FR-SRM-088` named | `CM-006`, `CM-013` | CM-10 |
| 10 | `CM-013` `O-02` rewritten to name `DM-006` `O-01` / `M01` `Q-04` as the actual blocker | `CM-013` | CM-10 |
| 11 | `CM-013` `O-03` narrowed from *"no mechanism"* to *"specified, unverified"* | `CM-013` | CM-10 |
| 12 | `CM-011` `O-02` rewritten: the disclosure exists; `LG-020` `AU2` is what blocks it | `CM-011` | CM-01 |
| 13 | `CM-011` `O-03` rewritten: `OP-014` exists; `OP-014-OI-01` and `-OI-02` are what block it | `CM-011` | CM-01 |
| 14 | `CM-004` `O-04` restated from *"no baseline captured"* to `RP-015`'s counted **44 of 95** | `CM-004` | CM-01 |
| 15 | `CM-016` `O-01` restated to the same counted figure | `CM-016` | CM-01 |
| 16 | `CM-016` `O-02` rewritten as the `UP-05` ↔ `RP-001` `KPI-016` reconciliation | `CM-016` | CM-01 |
| 17 | `CM-002` `O-04` rewritten as the `OP-001` §4.1 enumeration divergence | `CM-002` | CM-08 |
| 18 | `CM-014` `O-01` and `CM-015` `O-01` rewritten as boundary findings | `CM-014`, `CM-015` | CM-09 |
| 19 | `CM-015` `O-06` rewritten to name the population divergence and the unaddressed seller technicians | `CM-015` | CM-08 |
| 20 | `CM-006` `O-03` rewritten as the degraded-go-live precedence gap against `OP-004`/`OP-005` | `CM-006` | CM-01 |
| 21 | `CM-005` `O-02` rewritten as the severity-to-card translation gap | `CM-005` | CM-01 |
| 22 | `CM-003` `O-01` extended with the evidence that `OP-002` §4.3 uses the other calendar | `CM-003` | CM-03 |
| 23 | `CM-003` `O-04` rewritten as the M7/M8 anchor error | `CM-003` | CM-04 |
| 24 | Definition-of-Done lines updated in nine files to match the corrected open items | nine files | CM-01 |

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Adopt the proposed enumeration rule in `CM-01`** — a category author enumerates every category their files cite, at authoring time, and records the date. The register's status table is not a source for what exists | Programme Content Lead | **Before Category 19 authoring** |
| **R-02** | **Declare one wave calendar** and correct the loser register-wide, once. Do not correct it file by file | PMO with Enterprise Architecture | **W0** |
| **R-03** | **Reconcile the hypercare window** across `06-01` §5, `06-01` §6, BRD §21.6 and `OP-002` §4.3, and correct the three upstream documents | Programme Manager | **W1 minus 6 weeks** |
| **R-04** | **Correct the `CM-017` register row** to remove or qualify *"leaderboards"* | Programme Content Lead with CDO | **W2** |
| **R-05** | **Decide the W1–W5 recognition gap** — bring forward minimum scorecard visibility, or record what replaces the `RSK-008` mitigation for three waves | HR Director with CFO and PMO | **W2** |
| **R-06** | **Execute `AUDIT-018` R-07** and mirror `CM-008` §4.2's ownership-table form into the `EO` files | Programme Content Lead | **W3** |
| **R-07** | **Adopt `OP-001` §4.1 as the single external population enumeration**; re-derive `CM-002` §4.3 | Change Lead with Support Lead | **W1** |
| **R-08** | **Resolve `CM-007`'s nightly bilingual bulletin** — a same-day Bengali route, or an explicit decision that the bulletin is English at the sites that need it most | Localisation Lead with Support Lead | **W1 minus 3 weeks** |
| **R-09** | **Restate Master Index §7's `CM` effort row** at the next `AF-09` escalation, not separately | Programme Content Lead | Next Steering |
| **R-10** | **Run G1 editorial across all eighteen now**; hold G2 on the four files blocked by undecided positions and record the hold | Content Design Lead | **W0** |
| **R-11** | **Appoint the Change Lead.** Twelve of eighteen files name a role nobody holds as their owner, and `CM-001` `O-05`, `CM-002` `O-06` and `CM-010` `O-05` all reduce to it | CEO with HR Director | **W0** |

---

## 7. Closure

Category 16 is **complete on disk at 18 of 18**, template-conformant, and reconciles exactly on all
seven `F7` dimensions. Its 313 governing rules use 18 prefixes that collide with nothing in the
repository, its 128 content-identifier citations all resolve, and after remediation its 49 relative
links all resolve.

**It also carries the most serious authoring defect recorded in nineteen audits**, and the defect
is not subtle: eighteen files were written believing that fifty-eight of their dependencies did not
exist. Every consequence was found and corrected, and the corrections improved the files — `CM-007`
is materially better bound to `OP-002` than it was to its own invention, and four open items
became narrower and better-evidenced when tested against the files they claimed were absent.

That is the argument for `R-01`. The register's status table was written to be read, and it was
read, and it was wrong by fifty-eight files. **`RG-06` says to count. It does not say to count only
your own work.**

**Three findings in this report are for the Steering Committee rather than the content function:**
the wave calendar (`CM-03`), the leaderboard prohibition against a register row that commissions one
(`CM-05`), and a Critical-risk mitigation arriving three waves after the risk (`CM-06`). None can be
resolved by writing.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
*Next audit: Category 19 `MM` on completion, or the W0 wave boundary, whichever is earlier (`CM-R9`)*
