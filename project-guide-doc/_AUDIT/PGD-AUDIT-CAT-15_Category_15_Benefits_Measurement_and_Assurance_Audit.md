---
id: PGD-AUDIT-CAT-15
title: Category 15 — Benefits, Measurement & Assurance Audit
category: 15 — Benefits, Measurement & Assurance
code: BM
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Enterprise Architecture
subject: BM-002, BM-003, BM-004, BM-005, _CATEGORY_OVERVIEW.md, PGD-000 Category 15 rows
enumeration_timestamp: 2026-08-19 18:09 (+06)
verified_on: 2026-08-19
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# Category 15 `BM` — Benefits, Measurement & Assurance Audit

### 4 documents · 3,935 lines · 251 KB · 76 governing rules · 24 findings raised · **9 defects found and corrected in place**

---

## 1. Method and result

Every figure asserted by the four documents was **re-derived from source at
2026-08-19 18:09 (+06)**, not read back from the document asserting it. Paths were resolved on
disk. Rule and finding identifier spaces were enumerated for gaps and collisions. Arithmetic was
recomputed from its own stated inputs.

| Gate | Test | Result |
|:--:|---|:--:|
| **G1** | Every relative path resolves on disk | **PASS** — 30 of 30 |
| **G2** | Rule identifier spaces complete, no gaps, no duplicates | **PASS** — 76 rules |
| **G3** | Finding identifier spaces contiguous and unique | **PASS** — 24 findings |
| **G4** | Counts re-derived from source reproduce the document's claim | **PASS with 4 defects** — `A-05` |
| **G5** | Arithmetic totals reproduce from their own stated inputs | **PASS with 3 defects** — `A-01`, `A-02`, `A-08` |
| **G6** | Consumed figures match the current state of the source document | **FAIL — `A-01`.** `CO-005` was restated mid-authoring |
| **G7** | Internal `§` references resolve | **PASS with 1 defect** — `A-09` |
| **G8** | Shared figures agree across all four documents | **PASS with 2 defects** — `A-06`, `A-07` |
| **G9** | Front matter complete and standards-basis stated | **PASS** — 4 of 4 |
| **G10** | Identifier spaces do not collide with the estate | **PASS** — §2.5 |
| **G11** | Register rows reconcile to files on disk | **PASS** — §5 |

**Result: 9 defects, all corrected in place before issue.** Four findings raised against material
outside the category, of which one is **HIGH** and concerns a document this category consumes.

> **The audit's most useful output is not the defect list. It is that two of the nine defects —
> `A-02` and `A-05` — are the exact defect classes these documents were written to expose,
> occurring inside the documents that name them.** §3.2 and §3.5.

---

## 2. Checks that passed

### 2.1 Source re-derivation — the counted claims

Every headline count was re-derived from the source file, not from the document.

| Claim | Document | Re-derived | Result |
|---|---|---|:--:|
| 95 registered KPIs, 95 distinct identifiers | `BM-002` §3.1 | `grep -c "^\| KPI-"` → 95; `sort -u` → 95 | ✅ |
| Subsection row counts 10/9/8/9/5/8/9/10 = 68 | `BM-002` §3.1 | `awk` over `### 2.x` headings → identical | ✅ |
| §2.9 = 16 rows, §2.10 = 11 rows, no baseline column | `BM-002` §3.1 | Header extraction confirms column 3 is `Target` in both | ✅ |
| 44 unusable baselines (28/5/4/3/2/2) | `BM-002` §3.2 | Column-4 frequency count → identical | ✅ |
| 24 valued, 15 precise, 9 approximate | `BM-002` §3.3 | Classification pass → identical | ✅ |
| **15 of 95** usable-and-produced; **8** precise-and-produced | `BM-002` §3.5 | Set intersection against `03_Modules`+`04_Portals` → identical | ✅ |
| 250 / 196 / 41 / 54 / 14 identifier reconciliation | `BM-002` §9.1 | Re-run at audit → **250 / 196 / 54** confirmed unchanged | ✅ |
| `RL-006` mentions baseline, KPI, `BM-002` **zero** times | `BM-002` §6.2 | `grep -ciE` → **0** | ✅ |
| BDT 542 / 334 / 876 improvement split | `BM-002` §3.7 | Row-wise sum of `RP-015` §4.8 → identical | ✅ |
| Benefit curve 45/310/645/876/920 → $815.0K at 3 years | `BM-003` §6.2 | Reproduces `CO-005` §10.2 to the dollar | ✅ |
| 2.156× and 3.343× overstatement factors | `BM-003` §3.4 | $1.96M × 110 = 2,156 lac; ÷1,000 and ÷645 | ✅ |
| 502 / 374 / 876 benefit subtotals | `BM-004` §4.2 | Reconciles to `06-02` §3.1 **and** BRD §19.2 | ✅ |
| 9 benefit owners vs 12 objective owners; 1 and 4 divergences | `BM-004` §5.2 | Column extraction from `06-02` §1 and §3.5 → identical | ✅ |
| **"disbenefit" appears in 0 files** | `BM-004` §6.1 | `grep -rli` outside Category 15 → **0** | ✅ |
| 326 findings / 219 open / 19 CRITICAL / 194 owned | `BM-005` §3 | Re-run at audit → **identical** | ✅ |
| **0 findings carry any ageing** | `BM-005` §3.4 | `grep -rhcoiE "days open\|raised on\|finding age"` → **0** | ✅ |
| GV-004 wave-month map 1–4 / 5–8 / 9–13 … | `BM-002` §6.3 | Re-read from `GV-004` §5.2 → identical | ✅ |

> **`BM-005`'s finding counts were stable across two enumerations seventeen hours apart** (326/219
> at both 17:59 and 18:09), while the file count moved. That is a useful negative result: the estate
> is growing in **documents** faster than in **findings**, which is consistent with §3.3's
> observation that detection outpaces remediation.

### 2.2 Rule identifier spaces

| Space | Document | Range | Gaps | Duplicates |
|---|---|---|:--:|:--:|
| `BMR` | `BM-002` | `01`…`18` | none | none |
| `BSC` | `BM-003` | `01`…`20` | none | none |
| `BRP` | `BM-004` | `01`…`20` | none | none |
| `LLR` | `BM-005` | `01`…`18` | none | none |
| | | **76 rules** | | |

**Verification**: 18 + 20 + 20 + 18 = **76** ✓. Each consolidated table holds exactly one row per
rule; `grep -oE "^\| \*\*\`PREFIX-nn\`"` returns 18 / 20 / 20 / 18 with no repeated value.

### 2.3 Finding identifier spaces

| Space | Range | Count | CRITICAL | HIGH | MEDIUM |
|---|---|---:|---:|---:|---:|
| `BMR-F` | `01`…`06` | 6 | — | 3 | 3 |
| `BSC-F` | `01`…`06` | 6 | **1** | 2 | 3 |
| `BRP-F` | `01`…`06` | 6 | — | 3 | 3 |
| `LLR-F` | `01`…`06` | 6 | — | 3 | 3 |
| **Total** | | **24** | **1** | **11** | **12** |

**Verification**: 6 × 4 = **24** ✓ · 1 + 11 + 12 = **24** ✓. Severities extracted from each
finding's own `**Severity: … · Status: …**` line, not from the summary table — which is how `A-02`
was found.

### 2.4 Structural conformance

| Element | `BM-002` | `BM-003` | `BM-004` | `BM-005` |
|---|:--:|:--:|:--:|:--:|
| Front matter complete, `verified_on` present | ✅ | ✅ | ✅ | ✅ |
| `enumeration_timestamp` present | ✅ | ✅ | ✅ | ✅ |
| `rule_space` declared | ✅ | ✅ | ✅ | ✅ |
| Standards conformance table with departures | ✅ | ✅ | ✅ | ✅ |
| Decisions in `<DOC-ID>-D-nn` form (`DL-06`) | ✅ 6 | ✅ 7 | ✅ 7 | ✅ 7 |
| Open questions with owner and needed-by | ✅ 7 | ✅ 7 | ✅ 6 | ✅ 6 |
| Acceptance criteria | ✅ 10 | ✅ 12 | ✅ 12 | ✅ 13 |
| Traceability with direction | ✅ | ✅ | ✅ | ✅ |
| Revision history | ✅ | ✅ | ✅ | ✅ |

**Verification**: decisions 6+7+7+7 = **27** ✓ · open questions 7+7+6+6 = **26** ✓ ·
acceptance criteria 10+12+12+13 = **47** ✓ · 151 tables across the four documents.

**`DL-06` observed.** No document uses the bare `D-nn` form. All 27 decisions carry the
`BM-00n-D-nn` prefix.

### 2.5 Identifier-space collision check — `G10`

The estate's recurring defect class (`H-03`, `H2-04`, `AF-11`, `RP-01`) is a shared identifier space
with no allocating authority. Four checks were run **before** allocation and re-run at audit:

| Candidate | Workspace occurrences before allocation | Verdict |
|---|---:|---|
| `BMR-` | 0 | Allocated |
| `BSC-` | 0 | Allocated |
| `BRP-` | 0 | Allocated |
| `LLR-` | 0 | Allocated |
| **`BL-`** | **193** — `RP-015`'s baseline rules and others | **Rejected.** `BM-002` cites `BL-01`…`BL-12` as *`RP-015`'s*, never as its own |
| **`BM-`** | 0 as a rule prefix | **Rejected.** It is the category's **document** space; using it for rules would reproduce the `MG`/`RL`/`CO`/`CH`/`SV` category-code-versus-rule-prefix ambiguity |

> **This is the first category in the register to record the rule-prefix collision check as an
> explicit pre-allocation step**, and it is recommended as `R-03` for the remaining categories.

---

## 3. Defects found and corrected in place

### 3.1 `CAT15-A-01` — `BM-003` consumed a cost basis that was restated during authoring

**Severity: HIGH · Status: FIXED IN AUDIT · Owner: Enterprise Architecture**

**What was found.** `BM-003` §6 was built on `CO-005` §7 as read at **2026-08-19 ~01:00 (+06)**:

| | As consumed by the draft | **`CO-005` at audit** | Δ |
|---|---:|---:|---:|
| §7.1 line **C** Hypercare — expected | 124 | **177** | +53 |
| §7.1 line **D** Rate escalation — expected | 113 | **117** | +4 |
| **Tier 1 three-year — expected** | **2,501** | **2,558** | **+57** |
| Tier 1 three-year — low / high | 1,403 / 4,353 | **1,488 / 4,330** | |
| **Tier 1 five-year — expected** | **3,192** | **3,249** | +57 |
| Tier 2 five-year — expected | 3,899 | **3,977** | +78 |
| Tier 2 internal resource, Years 1–3 | 660 | **681** | +21 |

`CO-005` re-based its hypercare line from *"4–8 weeks × 9 waves"* to *"pools 1 + 2, 538 PW"*, citing
`SV-005` §5.5 — a Category 11 document issued during the same window.

**Why it is HIGH.** Every discounted figure in `BM-003` derives from these totals. Left uncorrected,
the estate's first NPV would have been computed on a superseded basis and would have disagreed with
`CO-005` by $57K on the three-year total — the precise failure mode `BSC-02` was written to prevent.

**Correction applied.** §6 and §8.1 were **recomputed in full** and re-spliced; §1, §2.2, §5.4,
§8.2, §8.4, §8.5, §8.7, §9.1, §9.2, §10 and §17 were updated. The movement:

| Measure | Before | **After** |
|---|---:|---:|
| Base-case 5-yr NPV @14% | −$951.6K | **−$994.2K** |
| Base-case simple payback | month 90 | **month 92** |
| 3-year ROI | −67% | **−68%** |
| Low-corner NPV | +$689.4K | **+$624.0K** |
| Low-corner IRR | ≈53% | **≈48%** |
| High-corner NPV | −$3,161.0K | **−$3,139.4K** |
| Corner band | $3.85M | **$3.76M** |
| Slippage exposure | $412K/yr | **$513K/yr** |
| Optimism-bias uplift on cost | +74% | **+69%** |

**Additional control adopted.** `BM-003` §6 now opens with a **stated-timestamp banner** naming the
`CO-005` enumeration it consumes. `BSC-02` is unchanged in substance and strengthened in practice.

### 3.2 `CAT15-A-02` — `BM-005`'s severity roll-up: a correct total over a wrong component

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Enterprise Architecture**

`BM-005` §7.4 tabulates the 24 findings this category raised. Two cells were wrong:

| Cell | Published | **Counted** |
|---|---|---|
| `BM-002` row | *2 HIGH, 4 MEDIUM* | **3 HIGH, 3 MEDIUM** |
| Total row | *1 CRITICAL, 10 HIGH, 13 MEDIUM* | **1 CRITICAL, 11 HIGH, 12 MEDIUM** |
| Verification line | *1 + 10 + 13 = 24* ✓ | **1 + 11 + 12 = 24** ✓ |

> **Both the published total and the published verification were internally consistent.** 1 + 10 +
> 13 does equal 24, and 2 + 4 does equal 6. **The arithmetic checked; the component did not.**
>
> **This is `PGD-A2-24` — "a correct total concealing a wrong component" — occurring in the document
> that catalogues `PGD-A2-24` as a defect class, three sections after `BM-002` §3.4 names it.**

**How it was caught, and the lesson.** Not by re-adding the row — that passes. It was caught by
extracting each finding's own `**Severity:**` line from the four source documents and re-tabulating.
**A verification line that re-adds a table's own cells cannot detect a wrong cell.** Recorded as
recommendation `R-01`: a roll-up is verified against its **sources**, not against itself.

### 3.3 `CAT15-A-03` — a ratio with mismatched populations

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Enterprise Architecture**

`BM-005` §8.2 published: *"Practised. **135 of 134 guiding documents carry `verified_on`**."*

A count of 135 against a denominator of 134 is not a near-miss; it is two different populations
compared as one. The 135 was a repository-wide `grep -rl` including non-guiding files; the 134 was a
filename-pattern count taken at a different moment.

**Corrected to:** *"Practised. **All 136 guiding documents carry `verified_on`** (counted
2026-08-19 18:09 +06)."* Re-derived: `ls */[A-Z][A-Z]-[0-9][0-9][0-9]_*.md` → 136; each tested for
the front-matter key → 136.

> **The finding the sentence was making was correct and is strengthened** — the control is
> universally practised in this repository and absent from the module repository. Only its
> arithmetic was wrong.

### 3.4 `CAT15-A-04` — the movement table understated its own movement

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Enterprise Architecture**

`BM-005` §3.6 records the estate moving during this category's authoring — the `RG-08` illustration.
Its own figures were wrong in two cells:

| Cell | Published | **Counted** |
|---|---:|---:|
| Audit documents at the 00:48 enumeration | 35 | **36** |
| Workspace-file movement | +10 | **+12** |

Corrected, and a fourth verification term added (`38 − 36 = +2`). The document's own enumeration was
advanced from 17:59 to **18:09 (+06)** so that one timestamp governs the whole document, and the
audit-document count updated 37 → **38**.

> **A section arguing that counts go stale, whose counts had gone stale between drafting and issue.**
> It is left in the register rather than smoothed away, because it is the strongest argument
> available for ratifying `RG-08` (`BM-005` §8.3 `R3`).

### 3.5 `CAT15-A-05` — all four acceptance criteria miscounted their own evidence

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Enterprise Architecture**

Each document's acceptance criterion for `PG-M10` cited a count of its own `**Verification**`
statements. **All four were wrong**, in both directions:

| Document | Criterion | Claimed | **Counted** | Error |
|---|---|---:|---:|---:|
| `BM-002` | `AC-03` | Fourteen | **13** | −1 |
| `BM-003` | `AC-06` | Twenty-two | **29** | **+7** |
| `BM-004` | `AC-11` | Six | **4** | −2 |
| `BM-005` | `AC-13` | Seven | **8** | +1 |

All four corrected to the counted value.

> **This is `PG-03` — *count, do not consult* — failing inside the acceptance criterion that asserts
> `PG-M10` compliance, in four documents whose central argument is that figures must be counted.**
> The cause is mundane and worth naming: each figure was written **while drafting** and never
> re-derived **at issue**, which is exactly what `PG-03` prohibits and exactly how the estate's
> 1,180 / 2,930 / 3,389 requirement-denominator chain arose.
>
> Recorded as recommendation `R-02`: **a self-descriptive count is computed at issue by command, or
> it is not stated.** The `BM-003` case is the instructive one — it drifted **+7** because §6 and
> §8.1 were rewritten during `A-01`'s correction and the criterion was not re-derived afterwards.

### 3.6 `CAT15-A-06` — a cross-document figure not propagated

**Severity: LOW · Status: FIXED IN AUDIT**

`BM-004` §9.3 cited *"`BM-003` §8.2 prices the slip at ~$412K/yr."* `A-01`'s recomputation moved
that figure to **$513K/yr**. Corrected. A sweep for the other nine superseded figures across all four
documents returned **zero** residual occurrences outside revision-history entries, where they are
required.

### 3.7 `CAT15-A-07` — `DIS-01` cited a superseded internal-resource figure

**Severity: LOW · Status: FIXED IN AUDIT**

`BM-004` `DIS-01` quantified the organisation-wide productivity draw at **$660K** over three years,
from `CO-005` §6.6. `CO-005` restated it to **$681K** (backfill at 30% moving $198K → $204K).
Corrected in three places — the register row, the explanatory note and `BM-004-D-07` — and the BDT
equivalent recomputed from 270 to **279 lac/yr**.

### 3.8 `CAT15-A-08` — a transition figure that was not derivable

**Severity: LOW · Status: FIXED IN AUDIT**

`BM-003` §9.2 traced how the return position moved and stated that restating cost alone took the
published 221% ROI *"to ~−58%"*. Re-derived: with the published benefit of $1.96M against `CO-005`'s
three-year cost, ROI is **($1,960K − $2,558K) ÷ $2,558K = −23%**, not −58%. The −58% could not be
reproduced from any pair of published figures.

Corrected to **−23%**, and the following row from *"−58% becomes −67%"* to **"−23% becomes −68%"**.

> **The chain is more informative corrected than it was wrong**: of the move from +221% to −68%,
> **the cost restatement accounts for 244 points and the benefit correction for 45 more.** The
> benefit correction is smaller than the cost correction and was the one nobody had made.

### 3.9 `CAT15-A-09` — a broken internal reference

**Severity: LOW · Status: FIXED IN AUDIT**

`BM-003` §1.1 pointed at *"§10.4"* for the budget-versus-business-case seam. §10 (The Five Case
Model) has no subsections. Corrected to *"§10 … in the Financial Case row"*, where the seam is
actually stated. All other `§` references in all four documents resolve — 30 external document
references and every internal one.

### 3.10 Defect summary

| ID | Severity | Document | Status |
|---|:--:|---|:--:|
| `CAT15-A-01` | **HIGH** | `BM-003` | FIXED IN AUDIT |
| `CAT15-A-02` | MEDIUM | `BM-005` | FIXED IN AUDIT |
| `CAT15-A-03` | MEDIUM | `BM-005` | FIXED IN AUDIT |
| `CAT15-A-04` | MEDIUM | `BM-005` | FIXED IN AUDIT |
| `CAT15-A-05` | MEDIUM | **all four** | FIXED IN AUDIT |
| `CAT15-A-06` | LOW | `BM-004` | FIXED IN AUDIT |
| `CAT15-A-07` | LOW | `BM-004` | FIXED IN AUDIT |
| `CAT15-A-08` | LOW | `BM-003` | FIXED IN AUDIT |
| `CAT15-A-09` | LOW | `BM-003` | FIXED IN AUDIT |

**1 HIGH · 4 MEDIUM · 4 LOW · 9 total · 9 corrected before issue · 0 open.**

---

## 4. Findings raised against material outside this category

### 4.1 `CAT15-B-01` — `CO-005` was restated without a version increment

**Severity: HIGH · Status: OPEN · Owner: CFO with Enterprise Architecture**

`CO-005` §7.1 lines `C` and `D` changed, moving four published totals, **while its front matter
remained `version: 1.0`, `date: 2026-08-19`, `enumeration_timestamp: 2026-08-19 10:05 (+06)`.**

| Field | Before | After |
|---|---|---|
| §7.1 line C description | *"Hypercare — 4–8 weeks × 9 waves (§6.4)"* | *"Hypercare — pools 1 + 2, 538 PW (§6.4, `SV-005` §5.5)"* |
| Tier 1 three-year expected | $2,501K | **$2,558K** |
| `version` | 1.0 | **1.0 — unchanged** |

**The content change is an improvement** — `CO-005` re-based hypercare on `SV-005`'s pool model,
which is more defensible than a weeks-times-waves estimate. **The configuration behaviour is the
defect.** `CO-005` is consumed by `GV-008`, `CO-003`, `BM-003` and the Board's `D-014` decision. A
consuming document cannot detect a silent restatement; `BM-003` caught it only because this audit
re-read the source rather than trusting its own draft.

**Remediation.** `GV-011` document control requires a version increment on any change to a published
figure, and `CO-005` `TCO-11`'s gate re-baseline should state which figures moved. Recommend
`CO-005` reissue as **1.1** with a revision-history row naming the four totals that changed.
Escalated to `GV-005`.

> **Generalised**: any document that publishes figures consumed elsewhere needs the discipline
> `BM-003` §6 now applies to itself — **name the source's timestamp beside the consumed figure.**
> Recommendation `R-04`.

### 4.2 `CAT15-B-02` — two figures this register published were never counted

**Severity: MEDIUM · Status: FIXED AT THIS ISSUE · Owner: Enterprise Architecture**

`PGD-000` and `15/_CATEGORY_OVERVIEW.md` v1.0 both published:

| Published | Counted | Ratio |
|---|---|---:|
| *"44 of 95 KPI baselines absent"* | **71 of 95** | 1.61× |
| *"roughly BDT 396 lac — about 45%"* | **BDT 542 lac — 62%** | 1.37× |
| *"19+ open findings"* | **219 open** | **11.5×** |

Both files carried these from `AUDIT-015` `RP-02` and from an uncounted impression, respectively.
**Corrected in both at this issue**, with the correction and its cause stated rather than the figure
silently replaced.

`AUDIT-015` `RP-02` itself is **restated, not closed** — its extraction was sound and its numerator
exact; only its denominator was substituted. `BM-002` §9.4 lists the six documents carrying the old
figure.

### 4.3 `CAT15-B-03` — `RL-006` has no baseline-preservation obligation

**Severity: HIGH · Status: OPEN · Owner: Programme Director with the Migration Lead**

Recorded in full as `BM-002` `BMR-F-06` and repeated here because it binds two documents in other
categories. `RL-006` Legacy Decommissioning Plan mentions *baseline*, *KPI* and `BM-002`
**zero times**, yet decommissioning is the foreclosing event for 20 class-`A` baselines and the
record-based class-`B` exercises. New rule **`BMR-09`** and a **`carries_baseline`** field on
`MG-002`'s profiling record are the remediation. Escalated to `GV-005` as `BM-002` `Q-02`.

### 4.4 `CAT15-B-04` — Category 99 rows are behind its files

**Severity: LOW · Status: RESOLVED BY EVENT · Owner: the authoring session**

At the audit enumeration, **five files exist in `99_Reference_Registers_and_Glossary/` whose
`PGD-000` rows are not yet ✅** — `RR-001`, `RR-003`, `RR-004`, `RR-005`, `RR-006`. Category 99 is
being authored concurrently.

**Recorded, not corrected.** `RG-08`'s discipline and this estate's own convention put the row
update with the session that authored the file. The register's recount at §5 therefore states
**134 ✅ at 18:09 (+06)** and will be higher within the hour — which is the condition the timestamp
exists to express.

> **Resolved by event during this audit.** A recount at **2026-08-19 18:32 (+06)** — twenty-three
> minutes after the audit enumeration — returns **140 ✅ of 140**. Category 99 completed and updated
> its own rows, exactly as `RG-08`'s discipline provides. The finding is retained rather than deleted
> because **it was true when counted and false twenty-three minutes later**, which is the clearest
> illustration in this audit of why every figure carries a timestamp.

---

## 5. Register reconciliation

Recounted from all 140 category rows per `PG-M10`, not incremented.

| Status | Rows |
|---|---:|
| ✅ authored | **134** |
| ◐ partial | 2 |
| ⛔ blocking | 2 |
| ⬜ absent | 2 |
| **Total** | **140** |

**Verification**: 134 + 2 + 2 + 2 = **140** ✓.

**Recounted at 2026-08-19 18:32 (+06)**, after Category 99 completed concurrently:

| Status | Rows |
|---|---:|
| ✅ authored | **140** |
| ◐ · ⛔ · ⬜ | **0** |
| **Total** | **140** |

**Verification**: 140 + 0 = **140** ✓. **The register is fully checked for the first time.**

**Rows to files:**

| Measure | Count |
|---|---:|
| Guiding-document files on disk | **138** |
| Register rows | **140** |
| Rows legitimately without a local file | **2** — `CO-001` → `primary-doc/…RFP.md`; `BM-001` → `06-02` |
| **Unreconciled** | **0** |

**Verification**: 140 − 2 = **138** ✓.

> **`BM-001` carries no file in Category 15, and that is the correct outcome.** Its ✅ points at
> `1000fix_ERP_Module/…/06-02`, an existing substantive document. Authoring a `BM-001` file here
> would create a **second KPI register** — precisely the defect `RP-01` records at 250-versus-95.
> The treatment matches `CO-001`, the only other row of its kind. Recorded because "Category 15 has
> four files against five rows" would otherwise read as an omission.

**Category 15 movement:** 1 ✅ / 2 ◐ / 1 ⛔ / 1 ⬜ → **5 ✅**.

---

## 6. What this category changes in the estate

| # | Change | Where |
|---|---|---|
| 1 | **`PGD-A2-10` closed in specification** — the estate's open CRITICAL on the benefit side. `06-02` §3.2 and BRD §19.3 label an **annual** series *"Cumulative"*; the published three-year benefit is a **2.2× overstatement** | `BM-003` §3 |
| 2 | **The first discounted case in the estate.** No document had ever computed an NPV | `BM-003` §5, §6 |
| 3 | **`RP-02` restated** from 44 of 95 to **71 of 95**, with the denominator substitution diagnosed | `BM-002` §3.4 |
| 4 | **The measurement-readiness figure nobody had**: 15 of 95 usable-and-produced; **8** precise-and-produced | `BM-002` §3.5 |
| 5 | **The foreclosure model corrected** — record-based baselines survive go-live and are lost to decommissioning instead, which buys months | `BM-002` §6.1 |
| 6 | **`PIR-27` made releasable per KPI** rather than all-or-nothing at issue | `BM-002` §8.4 |
| 7 | **A disbenefits register**, where the concept did not exist in 796 files | `BM-004` §6 |
| 8 | **A miss rule**, which `PGD-000` names as `BM-004`'s reason for existing | `BM-004` §9 |
| 9 | **`AT-2` staggered-rollout attribution** identified as a free control group that expires at W5 | `BM-004` §8.3 |
| 10 | **The backlog counted**: 219 open of 326, a **33% closure rate**, and **no finding anywhere carries an age** | `BM-005` §3 |
| 11 | **`00-06` §9's two controls and `RG-08` put to a body that can actually ratify them** — `GV-003`, not another audit | `BM-005` §8.3, §9.2 |

---

## 7. Recommendations

| # | Recommendation | Owner | Basis |
|:--:|---|---|---|
| **`R-01`** | **A roll-up is verified against its sources, not against itself.** A verification line that re-adds a table's own cells cannot detect a wrong cell — `A-02` passed its own check | Enterprise Architecture | `A-02`; `PGD-A2-24` |
| **`R-02`** | **A self-descriptive count is computed at issue by command, or it is not stated.** Four acceptance criteria in four documents were wrong because they were written while drafting | All authors | `A-05` |
| **`R-03`** | **Record the rule-prefix collision check as an explicit pre-allocation step** in every category, as §2.5 does | Enterprise Architecture; `RR-002` | `H-03`, `AF-11`, `RP-01` |
| **`R-04`** | **Name the source's enumeration timestamp beside every consumed figure**, as `BM-003` §6 now does | All authors | `A-01`, `B-01` |
| **`R-05`** | **`CO-005` reissues as 1.1** with a revision-history row naming the four totals that moved | CFO | `B-01` |
| **`R-06`** | **Ratify `RG-08`** — recommended for at least the tenth time, and it failed twice inside this category's own authoring (`A-01`, `A-04`). `BM-005` §9.2 diagnoses why: it has been recommended **to audits**, which cannot ratify a programme rule. Land it at `GV-003` | Steering Committee | `BM-005` §8.3 `R3` |
| **`R-07`** | **Fund `BM-002`'s 31.6 person-weeks before W1 go-live.** `BM-003` §7.3: without it the claimable benefit at full run rate is **less than the cost of running the platform** | Steering Committee | `BM-002` §6.6 |

> **`R-06` is the seventh time this audit series has asked for `RG-08`, and this audit is the first
> to say where it should land.** That distinction is the whole content of `LLR-13`: a change proposed
> four or more times is being proposed to someone without the authority to make it.

---

## 8. Closure

| Element | Position |
|---|---|
| Documents audited | **4** — `BM-002`, `BM-003`, `BM-004`, `BM-005` |
| Supporting artefacts audited | `_CATEGORY_OVERVIEW.md`, `PGD-000` Category 15 rows |
| Defects found | **9** — 1 HIGH, 4 MEDIUM, 4 LOW |
| Defects corrected before issue | **9** |
| Defects open | **0** |
| Findings raised outside the category | **4** — 2 HIGH, 1 MEDIUM, 1 LOW |
| Findings this category raised | **24** — 1 CRITICAL, 11 HIGH, 12 MEDIUM, all seeded into `BM-005` §7.4 |
| Register status | **Updated.** 134 ✅ of 140, recounted at 2026-08-19 18:09 (+06) |
| Estate at audit | **796** workspace markdown files; **175** in this repository; **38** audit documents |

**Category 15 is issued.**

### 8.1 Movement during the audit itself

Recorded because it is the third occurrence inside this category's own work, after `A-01` and `A-04`.

| Measure | **18:09 (+06)** | **18:32 (+06)** | Δ |
|---|---:|---:|---:|
| Workspace markdown files | 796 | **799** | **+3** |
| This repository | 175 | **178** | **+3** |
| Guiding-document files | 136 | **138** | **+2** |
| Register rows marked ✅ | 134 | **140** | **+6** |
| Audit documents in this repository | 16 | **17** | **+1** |

**Verification**: 799 − 796 = **+3** ✓ · 178 − 175 = **+3** ✓ · 138 − 136 = **+2** ✓ ·
140 − 134 = **+6** ✓.

> **Twenty-three minutes.** In that window Category 99 completed, the register moved from
> 134 checked to 140, and this audit's §4.4 finding became false. **Every figure above survives
> only because it carries the timestamp it was counted at** — which is the entire content of
> `RG-08`, recommended for at least the tenth time and still unratified. `R-06`.

> **The auditor's own position, recorded because `GV-010` exists for it.** This audit was performed
> by the function that authored the four documents. `AUDIT-019` named that exposure —
> *"1 critical, against the auditor's own authoring"* — and `BM-005` `LLR-15` now requires such
> findings to be flagged `self_raised` so `GV-010` samples them first.
>
> **The evidence that the exposure is real is in this document.** `A-02` and `A-05` are defects a
> self-audit is *least* likely to find, because they are the author's own arithmetic about the
> author's own work, and both passed every internal consistency check the documents contained. They
> were found only by re-deriving from source. **A reviewer who re-adds the tables will not find
> them; a reviewer who recounts will.** That is the instruction to `GV-010`.

---

*`PGD-AUDIT-CAT-15` · Category 15 · 1000FiX ERP System v2.0 · CONFIDENTIAL · counted 2026-08-19 18:09 (+06)*
