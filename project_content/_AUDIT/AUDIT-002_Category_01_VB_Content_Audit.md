---
id: FIX-ERP2-AUDIT-002
title: Category 01 VB — Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-15
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The ten Category 01 VB files, and their consistency against Category 00 CG and the Content Master Index
mandate: Audit required on completion of Category 01 authoring
extends: AUDIT-001_Content_and_Repository_Integrity_Audit.md
---

# Category 01 `VB` — Content Audit
### Ten files · 24 of 452 registered content files now written

---

## 1. Mandate, scope and method

Run on completion of Category 01 authoring, per rule `CM-R9` and the recurring checklist in
`AUDIT_Checklist_Recurring.md`.

### 1.1 Scope

| Area | Files |
|---|---:|
| Category 01 `VB` — the subject of this audit | 10 |
| Category 00 `CG` — checked for consistency with `VB` | 14 |
| Register, README and audit files | 4 |
| **Total examined** | **28** |

### 1.2 Method

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F6 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration and extraction. No finding below
rests on reading what a document says about itself (`RG-06`, `CP-11`).

### 1.3 Result

**5 findings — 0 critical, 1 high, 2 medium, 2 low.** Four were remediated during the audit.
One is escalated because it requires a Brand decision.

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 2 |
| Low | 2 |

---

## 2. Checks that passed

Recorded because a clean check is evidence, not an absence of information.

| Check | Result |
|---|---|
| **A1** File count per category | 10 of 10 ✅ |
| **A2** Total content files | 24 of 452, enumerated 2026-08-15 ✅ |
| **A5** Files on disk with no register entry | Zero ✅ |
| **A6** Register entries claiming a file that does not exist | Zero for `CG` and `VB` ✅ |
| **B1** Content ID uniqueness | No duplicates ✅ |
| **B2** ID contiguity `VB-001`…`VB-010` | Contiguous, no gaps ✅ |
| **B4** File name matches its ID | 10 of 10 ✅ |
| **C1** Every file declares `purpose:` | 10 of 10 ✅ |
| **C2** Every file declares `traces_to:` | 10 of 10 ✅ |
| **C3** Every `traces_to:` target resolves | ✅ |
| **D1** Internal links resolve | **126 links across 28 files, zero broken** ✅ |
| **D2** Files in the folder their category declares | ✅ |
| **D3** No spaces, ampersands or non-ASCII in any path | ✅ |
| **D4** Reserved prefixes used correctly | ✅ |
| **E7** Template conformance | 10 of 10 declare `TPL_Content_File_Front_Matter.md` per `CG-009` §3 ✅ |
| **F1** Front matter complete, no placeholders | 24 required keys present in all 10 ✅ |

### 2.1 Cross-register reconciliation

The three places Category 01 is counted all agree.

| Dimension | Source of the expectation | Expected | Actual | Result |
|---|---|---:|---:|:--:|
| File count | Master Index §1 | 10 | 10 | ✅ |
| Priority `P0` | Master Index §1 distribution table | 3 | 3 | ✅ |
| Priority `P1` | Master Index §1 | 4 | 4 | ✅ |
| Priority `P2` | Master Index §1 | 3 | 3 | ✅ |
| Priority `P3` | Master Index §1 | 0 | 0 | ✅ |
| Content class **D** | `CG-002` §4.1 | 6 | 6 | ✅ |
| Content class **E** | `CG-002` §4.1 | 4 | 4 | ✅ |
| Bilingual | `CG-010` §3.2 | 5 | 5 | ✅ |
| English-only | `CG-010` §3.2 | 5 | 5 | ✅ |
| **Which** files are bilingual | `CG-010` §3.2 names `VB-002`, `VB-007`, `VB-008`, `VB-009`, `VB-010` | — | Identical | ✅ |
| Priority and wave per file | Master Index §4 register rows | — | All 10 match | ✅ |

> This is the reconciliation that `AUDIT-001` findings **AF-02** and **AF-03** existed because
> nobody ran. It is now run per category.

---

## 3. Findings

### VB-01 — The primary brand colour fails WCAG AA text contrast

**Severity: High · Status: ESCALATED · Owner: Brand Lead with CTO**

**What was found.** Contrast ratios were computed from the `CB-001` §3 palette using the WCAG 2.1
relative-luminance formula during authoring of `VB-003`.

| Colour | Hex | On white | Verdict |
|---|---|---:|---|
| **1000FiX Blue** | `#39B1DF` | **2.46** | Fails all text; fails the 3:1 non-text threshold |
| Warm Orange | `#FF8C42` | 2.31 | Fails all text |
| **Warning Yellow** | `#FFC107` | **1.63** | Fails badly |
| 1000FiX Orange | `#F26100` | 3.24 | Large text only |
| Success Green | `#28A745` | 3.13 | Large text only |
| Info Blue | `#17A2B8` | 3.04 | Large text only, marginal |
| Error Red | `#DC3545` | 4.53 | Passes, no margin |

**Why it matters.** `04-00` PS-04 and `05-06` NFR-073 make WCAG 2.1 AA contractual on all web
portals, and `05-06` §11 requires an automated scan **plus a manual audit before each portal
release**. Applying the marketing palette to text unchanged fails that scan on every portal.

At 2.46:1 the primary brand blue fails even SC 1.4.11's 3:1 non-text threshold, so it cannot be
the sole carrier of a border, focus ring or status indicator on a light background either.

**Why it was not found earlier.** The palette is correct for its original purpose — marketing
pages, where the blue is used as a fill behind white display type at large sizes. The failure
appears only when the same palette is applied to 13px operational text.

**Action taken.**

1. `VB-003` §3 records the measured ratios, the six consequences, and three options for Brand.
2. `VB-008` derives an **eight-token semantic palette** that passes AA — `#146C43` success at
   6.45:1, `#8A6100` warning at 5.54:1, `#B02A37` error at 6.50:1, `#0F6674` info at 6.62:1 —
   and states why each replaces its `CB-001` counterpart.
3. `VB-005` and `VB-007` carry the constraint into email and iconography.
4. **Raised as content risk `CR-13`** in `CG-013` §7 — see finding VB-02.

**Escalation.** Changing a brand colour is a Brand decision, not a content one
(`CG-013` T-A19). Brand must rule on one of:

| Option | Consequence |
|---|---|
| **1 — Adopt `#1E5F8A` as the ERP text/link blue; keep `#39B1DF` as a fill-only brand colour** | No brand change, no marketing impact. **Recommended and assumed in `VB-003` until Brand rules** |
| 2 — Darken `#39B1DF` for digital text | Creates a divergence from `CB-001` |
| 3 — Accept documented AA failures | Contradicts `PS-04` and `NFR-073` |

**Blocks:** design-system token approval.

---

### VB-02 — `CR-13` was cited before it existed

**Severity: Medium · Status: FIXED · Owner: Programme Content Lead**

**What was found.** `VB-003` §3.2 and its Definition of Done both reference content risk
`CR-13` in `RF-011`. `CG-013` §7 enumerated `CR-01`…`CR-12` and stated **"All twelve transfer to
`RF-011`"**. `CR-13` existed in a citation and nowhere else.

**Why it matters.** This is the same defect class as `AUDIT-001` **AF-04** — two audits citing
decision `D-14` against a decision log that does not exist — and as `00-06` **C-02**, a
specification written before its register entry. **It is register drift, three files old.**

The mechanism is worth naming: `VB-003` was authored after `CG-013`, discovered a genuine new
risk, and recorded it by forward reference rather than by amending the register. That is exactly
how `M31` came to have a specification and no allocation.

**Fixed.** `CG-013` §7 now carries `CR-13` with its consequence, likelihood, owner and
traceability, and the count is restated as thirteen. A note records when and how it was raised.

**Prevention.** `CG-005` `ID-01` (register-first) already covers content files. It does **not**
cover risk identifiers, which `CG-013` owns. Recommendation **R-02** below extends it.

---

### VB-03 — The banned-term waiver did not permit citing a banned term as a banned example

**Severity: Low · Status: FIXED · Owner: Content Design Lead**

**What was found.** The automated banned-term check flagged legitimate uses:

| Term | File | Context |
|---|---|---|
| "please", "kindly" | `VB-001` §4, §8 | The "never sounds like" table and the worked rewrite showing bad copy |
| "leverage", "utilise", "facilitate" | `VB-001` §4 | The banned corporate-vocabulary row |
| "Please ensure that…" | `VB-002` §7 | A do-not example |

`CG-004` §9 permitted a banned term only inside a direct quotation, a statutory instrument's
wording, a third-party product name, or a code identifier. **A style guide naming the words it
forbids was not covered.**

**Why it matters.** Minor in effect, but it makes the automated check produce guaranteed false
positives on every governance file — and a check that always cries wolf is a check reviewers
learn to ignore.

**Fixed.** `CG-004` §9 waiver extended with a fifth case: *a governance, style or training
document citing the term as a banned example*. The lint exclusion is scoped narrowly — it
applies to do-not tables and worked examples in `Standard`, `Policy` and `Governance` files
only. A banned term used as **instruction** in those same files remains a defect.

---

### VB-04 — Email client rendering claims rested on P3 sources

**Severity: Medium · Status: FIXED · Owner: Brand Lead**

**What was found.** `VB-005` §3 makes specific, load-bearing claims about email client behaviour
— Outlook rendering through the Word engine, Gmail sanitising CSS, web fonts loading only in
Apple Mail, three different dark-mode implementations. These were sourced at class **P3**
(corroborating third-party analysis).

`CG-012` EV-02 states that **P4 reported sources are never a source**, and industry technical
writing sits close to that boundary. The claims are also the basis of the entire design — if
they are wrong, the shell is wrong.

**Why it matters.** This is the `00-07` **H2-13** shape in a different domain: a design resting
on reported behaviour rather than on verified observation.

**Fixed.** The two source entries now carry an explicit note: the classification is P3,
corroborated across independent technical sources, and it **converts to P1 (direct observation)
on completion of the §13 baseline client testing, which is mandatory before any template ships.**
No template may be approved on the P3 evidence alone.

> This is the honest treatment. The claims are almost certainly correct; they are not yet
> *ours* to assert until we have looked.

---

### VB-05 — `MD-027` and `BN-003` do not yet exist, and three `VB` files depend on them

**Severity: Low · Status: OPEN — expected, tracked**

**What was found.** `VB-007` §6, `VB-008` §4 and `VB-010` §8 all carry Bengali labels and state
lifecycle labels that are authoritative in `BN-003` and `MD-027` respectively. Neither exists.

**Why it is Low and not Medium.** All three files mark the dependency explicitly, label the
content **indicative** or **provisional**, state that divergence resolves in favour of the
authoritative file, and list the dependency as an open Definition-of-Done item blocking
`Approved`. This is the correct handling under `CG-012` §6.1 provisional marking — the failure
would have been to present the labels as settled.

**Action.** No fix required. Tracked as a dependency, not a defect. `VB-007`, `VB-008` and
`VB-010` cannot reach `Approved` until `BN-003` and `MD-027` exist — which is already recorded
in each file.

---

## 4. Remediation applied

| # | File changed | Change | Finding |
|---|---|---|---|
| 1 | `CG-013` §7 | Added `CR-13` with consequence, likelihood, owner and traceability; restated the count as thirteen; added a note on when and how it was raised | VB-02 |
| 2 | `CG-004` §9 | Extended the banned-term waiver with a fifth case and a narrowly scoped lint exclusion | VB-03 |
| 3 | `VB-005` front matter | Added notes to both P3 source entries stating the conversion path to P1 and prohibiting approval on P3 evidence alone | VB-04 |
| 4 | Master Index §1, §12; `project_content/README.md` | Written count restated from 14 to 24 by enumeration, dated | A2 |

**Not remediated, by design:** VB-01 (requires a Brand decision under `CG-013` T-A19), VB-05
(expected dependency, correctly marked).

---

## 5. Observations

### 5.1 The cross-register reconciliation now works

Category 01 is counted in four places — the Master Index register, the Master Index statistics,
`CG-002` §4.1 content classes and `CG-010` §3.2 bilingual coverage. **All four agree, and
`CG-010` even names the correct five files individually.**

`AUDIT-001` raised four findings (AF-02, AF-03, AF-05, AF-16) that were all instances of
registers disagreeing with reality. The Category 00 governance set was written specifically to
prevent that, and on its first test it held.

### 5.2 One real defect got through, and it is the same defect as always

VB-02 — citing `CR-13` before creating it — is register drift. `CG-005` `ID-01` forbids exactly
this for content files. It does not extend to the risk, decision and metric identifier spaces
that the `CG` files themselves own.

**Three audits have now found register drift in three different identifier spaces.** The pattern
is not carelessness; it is that register-first is enforced where a rule names it and nowhere
else. Recommendation R-02 closes the gap for content-owned spaces.

### 5.3 The highest-value finding came from computation, not from checking

VB-01 was not found by comparing documents. It was found by taking eight hex values from an
approved brand guideline and running them through a formula. **No consistency check would ever
have surfaced it**, because every document was internally consistent and consistent with every
other document — and all of them were wrong together.

The same was true of `AUDIT-001` AF-09, the unbudgeted content effort. Both came from asking a
question nobody had asked, not from verifying an answer somebody had given.

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Rule on `CR-13`** — the brand-blue contrast failure. Option 1 in `VB-003` §3.2 is recommended and requires no marketing change | Brand Lead with CTO | **Before design-system token approval** |
| **R-02** | Extend register-first (`CG-005` `ID-01`) to every identifier space the content workstream owns — `CR-`, content `D-` decisions in `RF-006`, and content metric IDs. No forward references | Programme Content Lead | Next `CG-005` revision |
| **R-03** | Complete the baseline email client testing and convert the `VB-005` sources from P3 to P1 | Platform Engineering | Before the first `NT` email template |
| **R-04** | Establish the physical printer test set (`VB-004` §14) and the device rendering register (`VB-009` §13). Both are prerequisites for `DT` and `P02` release | Platform Engineering | Before W1 `DT` release |
| **R-05** | Resolve `VB-010` §13 decision 1 — rename "Privileged Program" to "Privilege" — **before `MD-034` is authored**. After that it becomes a master-data migration under `NM-01` | Commercial Lead with Brand | **Before `MD-034`** |
| **R-06** | Author `BN-003` and `MD-027` early in W1; three `VB` files and much of `UI` and `MD` are blocked behind them | Localisation Lead, MDM Lead | Early W1 |
| **R-07** | Add the four numeric reconciliations run in §2.1 to the automated check set, so they run per commit rather than per audit | Platform Engineering | Next CI change |

---

## 7. Closure

| Item | State |
|---|---|
| Files examined | 28 |
| Findings raised | 5 — 0 critical, 1 high, 2 medium, 2 low |
| Remediated in this audit | 4 |
| Open | 1 escalated (VB-01), 1 tracked dependency (VB-05) |
| Cross-register reconciliations run | 11, all passing |
| Links verified | 126, zero broken |
| Content files written | **24 of 452**, enumerated 2026-08-15 |
| Next audit | On completion of the next category, or at the W1 wave boundary |

**Carried forward to `RF-012`.** Open findings from `AUDIT-001` remain open and are not restated
here: **AF-01** portal misfiling, **AF-04** missing decision log, **AF-06** requirement recount,
**AF-07** `05-02`/`05-04` scope, **AF-08** effort reconciliation, **AF-09** content funding,
**AF-14** portal references, **AF-15** missing `99-02`.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
*Audit performed 2026-08-15 · Filesystem enumeration dated 2026-08-15*
