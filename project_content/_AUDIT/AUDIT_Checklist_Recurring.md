---
id: FIX-ERP2-AUDIT-CHECKLIST
title: Recurring Content Audit Checklist
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-15
status: ACTIVE
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
cadence: Every wave boundary (rule CM-R9)
---

# Recurring Content Audit Checklist

Run at every wave boundary, and before any Steering Committee paper that quotes a completeness
figure. Record results as a new `AUDIT-nnn` file in this folder and index them in `RF-012`.

**Method rule.** Every check below is answered by **enumerating the filesystem or extracting
from files** — never by reading what a document says about itself. This is rule **RG-06**, and
proposed rule **RG-07**: completeness figures are generated, and carry an enumeration date.

---

## A. Counting and completeness

| # | Check | How | Pass condition |
|---|---|---|---|
| A1 | File count per category | `find <folder> -name "<CODE>-*.md" \| wc -l` | Matches the Master Index category table |
| A2 | Total content files | Enumerate all category folders | Matches Master Index §1 |
| A3 | Every stated completeness figure carries an enumeration date | Grep for `%` and "complete" across governance files | No undated figure |
| A4 | No two documents state contradictory counts | Extract every count claim, compare | Zero contradictions |
| A5 | Files on disk with no register entry | Diff filesystem against Master Index IDs | Empty — rule `CM-R1` |
| A6 | Register entries with no file | Diff Master Index IDs against filesystem | Expected only for unstarted work; flag anything marked `Approved` |

## B. Identifier integrity

| # | Check | How | Pass condition |
|---|---|---|---|
| B1 | Content ID uniqueness | Extract all `<CODE>-<nnn>`, sort, deduplicate | No duplicates |
| B2 | Content ID contiguity | Compare count to highest ID per category | Gaps only where an ID is marked `WITHDRAWN` |
| B3 | No reused IDs | Compare against `RF-006` retirement log | No reuse — principle `CP-02` |
| B4 | File name matches its ID | Regex file names against `<CODE>-<nnn>_` | 100% conformance |
| B5 | Bengali counterparts share the stem | Match `_BN.md` files to their source | Every `bilingual: yes` file paired |

## C. Traceability

| # | Check | How | Pass condition |
|---|---|---|---|
| C1 | Every file declares `purpose:` | Extract front matter | 100% — principle `CP-03` |
| C2 | Every file declares `traces_to:` | Extract front matter | 100% — principle `CP-04` |
| C3 | Every `traces_to:` target exists | Resolve `Mnn`, `Pnn`, `FR-` and document references | 100% resolve |
| C4 | Requirements with no content | Diff `05-01` requirement IDs against `RF-003` | Gaps listed and owned |
| C5 | Content with no requirement | Reverse of C4 | Zero, or justified as governance content |

## D. Links and structure

| # | Check | How | Pass condition |
|---|---|---|---|
| D1 | All internal links resolve | Extract every relative path, test against disk | Zero broken |
| D2 | Files are in the folder their category declares | Enumerate by folder | 100% — this is how **AF-01** was found |
| D3 | No spaces or ampersands in any path | Regex all paths | Zero — finding `AF-12` |
| D4 | Reserved prefixes used correctly | Check `_`, `TPL_`, `SUPERSEDED_`, `DRAFT_` | 100% |
| D5 | Superseded content is archived, not deleted | Check `_ARCHIVE/` against `RF-006` retirements | Every retirement has an archived file |

## E. Content quality gates

| # | Check | How | Pass condition |
|---|---|---|---|
| E1 | Every `Approved` file passed the `CG-008` Definition of Done | Check the DoD block | 100% |
| E2 | Every statutory or legal file has a named approver | Extract `approver:` from Category 10 and statutory `DT` files | 100% — rule `CM-R7` |
| E3 | Every factual claim carries a source and verification date | Sample 10% plus all statutory files | 100% on statutory; sample defect rate under 5% |
| E4 | Verification dates are within currency | Compare `verified:` dates to the currency policy | No expired statutory or regulatory citation |
| E5 | Bilingual files have in-context linguistic sign-off | Check `BN-018` sign-off records | 100% of `bilingual: yes` files at `Approved` |
| E6 | Terminology conforms to `CG-004` and `BN-003` | Automated term scan against banned-synonym list | Defect rate under 2% |
| E7 | Template conformance | Compare section headings against `_templates/` | 100% |

## F. Cross-register consistency

| # | Check | How | Pass condition |
|---|---|---|---|
| F1 | Master data referenced by UI copy exists | Cross-check `MD` references in `UI` files | 100% |
| F2 | Status labels are identical across `MD-027`, `VB-008`, `UI-*` and `RP-*` | Extract and compare | Zero divergence |
| F3 | SLA definitions identical across `MD-028`, `DT-031` and `LG-015` | Extract and compare | Zero divergence — these carry financial liability |
| F4 | Error message IDs cited by `MD` validation rules exist in `UI-004` | Cross-check | 100% |
| F5 | Notification templates cited by `NT-001` matrix all exist | Cross-check | 100% |
| F6 | Legal documents do not contradict each other on data protection | Manual review of `LG-008`, `LG-009`, `LG-012` | Zero contradictions |
| **F7** | **Category-completion reconciliation — BLOCKING** | On completing any category, regenerate its derived counts from the files on disk and compare against `CG-002` §4.1 (content class), `CG-009` §3 (template declaration), `CG-010` §3.2 (bilingual split), and the Master Index §4 register (file count, contiguity, priority, wave, subfolder) | **Zero divergence. A category may not be declared complete while any count differs.** Where a summary and its derivation disagree, the derivation governs and the summary is regenerated |

> **Why F7 blocks.** Three separate audits — `AUDIT-002` (`CG-002` §4, `CG-009`), `AUDIT-003`
> (`MD-01`, Master Index priority distribution wrong in 20 of 21 categories) and `AUDIT-005`
> (`NT-01`, `CG-010` §3.2) — found the same failure: **a summary table written before the
> derivation it summarises, and never reconciled against it.** Prose review missed all three;
> enumeration caught all three. Summary tables for the remaining categories must be
> **regenerated after authoring**, never written ahead of it (`CP-11`, `CM-R2`).
>
> **F7 includes a repository-wide sweep.** Correcting a derived figure at its source is not
> the correction. When `AUDIT-005` changed the bilingual total from 268 to 266, the same
> figure was found restated in **eleven further places across four files** — including the
> corrected file's own total row, two lines below the row that had just changed. Every
> derived figure must be grepped across the whole repository after correction, and the
> corrected file must be re-checked for internal self-consistency before the gate passes.

## G. Programme health

| # | Check | How | Pass condition |
|---|---|---|---|
| G1 | Open findings from prior audits have moved | Compare to previous `AUDIT-nnn` | No finding open across three consecutive audits without escalation |
| G2 | Content effort actuals against estimate | Compare to Master Index §7 | Variance under 20%, or re-forecast |
| G3 | `P0` content complete for the wave about to start | Filter register by wave and priority | 100% — this is the go-live gate |
| G4 | Every content file has a named owner and a review date | Check `RF-010` | 100% |
| G5 | Content risks reviewed | Check `RF-011` | Reviewed within the last wave |

---

## Reporting format

Each audit produces one file with:

1. Mandate, scope, method (including the enumeration date)
2. Result line — findings by severity
3. Findings summary table with ID, severity, owner and status
4. Critical and high findings in full, each with: what was found, why it matters, how it
   happened, and the remediation instruction
5. Remediation applied — every change listed
6. Recommendations with named owners and dates
7. Closure, including any proposed governance rule

**Severity definitions**

| Severity | Definition |
|---|---|
| **Critical** | Would cause work to be done against the wrong artefact, or a required artefact to be assumed present when absent |
| **High** | Materially misleading, or a budget or scope exposure |
| **Medium** | Register or cross-document correction required before the affected documents are authoritative |
| **Low** | Precision improvement |

**Findings are reported, not quietly fixed.** Where the auditor's own prior work caused a
finding, that is stated — the cause matters more than the fix. This convention is inherited
from audit `00-07` and applies here without exception.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
