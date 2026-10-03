---
id: FIX-ERP2-AUDIT-020
title: Category 99 RF — Reference & Registers Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 12 Category 99 RF files; the register-wide reconciliation they make possible for the first time; the checks G1 and G4 that have never been answerable; and the defects Category 99 introduced into itself
mandate: Audit required on completion of Category 99 authoring (rule CM-R9), and required as the closing audit of the 452-file register
extends: AUDIT-001 … AUDIT-019
enumeration_instant: 2026-08-18 00:26 Asia/Dhaka
method: Filesystem enumeration and identifier extraction only (RG-06, CP-11). No figure in this report is projected, and none is taken from what a document says about itself — including what the Category 99 registers say about themselves.
---

# Category 99 `RF` — Reference & Registers Content Audit

### 12 files · **452 of 452 registered content files now written** · the register is complete

---

## 1. Method and result

Checks **A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F7** and **G1–G5** of
`AUDIT_Checklist_Recurring.md`, answered by running the extraction, never by reading a document's
own claim about itself (`RG-06`, `CP-11`). **Enumeration instant 2026-08-18 00:26 Asia/Dhaka.**

Category 99 differs from the nineteen audits before it in one way that shapes this report. The
other categories produce content; **Category 99 produces the instruments that audit content.**
Three of its registers answer checks in this very checklist — `RF-010` answers `G4`, `RF-011`
answers `G5`, `RF-012` answers `G1`. Auditing them therefore means running those checks *and*
checking whether the register that answers them is itself sound.

Six category-specific extractions were run in addition to the standard checklist:

| Extraction | What was compared |
|---|---|
| **X1** | Every identifier prefix in `1000fix_ERP_Module/` and `project_content/` against `RF-001` §4.2 |
| **X2** | Every `FR-` identifier across 67 module and 12 portal files against the denominator `RF-003` declares |
| **X3** | Every `traces_to:` `Mnn` / `Pnn` target across all written files against the coverage counts in `RF-004` §4.3 and `RF-005` §4.4 |
| **X4** | Every `verified:` date across `project_content/` against the enumeration instant |
| **X5** | Every `CD-`, `PD-`, `ST-`, `CR-`, `BL-`, `SRC-`, `AP-`, `WE-` identifier cited in a Category 99 file against its declaring register |
| **X6** | Every Category 99 file's front matter against `CG-002` §4.1, `CG-009` §3, `CG-010` §3.2 and Master Index §4 — gate `F7` |

**14 findings — 2 critical, 5 high, 6 medium, 1 low.** Four were remediated during the audit; ten
remain open. **Nine of the fourteen were raised by the Category 99 registers themselves**, against
work outside Category 99; three are defects Category 99 introduced into itself; two are
register-wide conditions that only became visible once the registers existed.

| Severity | Count | Remediated | Open |
|---|---:|---:|---:|
| Critical | 2 | 0 | **2** |
| High | 5 | 0 | 5 |
| Medium | 6 | 4 | 2 |
| Low | 1 | 0 | 1 |
| **Total** | **14** | **4** | **10** |

---

## 2. The register is complete — 452 of 452

Enumerated by folder at the instant above. **Every category matches its Master Index §4 count
exactly.**

| # | Code | Category | Registered | On disk | ✓ |
|---|:--:|---|---:|---:|:--:|
| 00 | `CG` | Content Governance & Standards | 14 | 14 | ✅ |
| 01 | `VB` | Voice, Brand & Design-System | 10 | 10 | ✅ |
| 02 | `MD` | Master Data & Configuration | 48 | 48 | ✅ |
| 03 | `UI` | UI Copy & Microcopy | 42 | 42 | ✅ |
| 04 | `NT` | Notification & Messaging | 26 | 26 | ✅ |
| 05 | `DT` | Document, Print & Statutory | 44 | 44 | ✅ |
| 06 | `SP` | Process, SOP & Workflow | 34 | 34 | ✅ |
| 07 | `KB` | Knowledge Base | 16 | 16 | ✅ |
| 08 | `TR` | Training & Enablement | 24 | 24 | ✅ |
| 09 | `HC` | Help Centre & Self-Service | 20 | 20 | ✅ |
| 10 | `LG` | Legal, Policy & Compliance | 24 | 24 | ✅ |
| 11 | `BN` | Localisation & Bilingual | 18 | 18 | ✅ |
| 12 | `DM` | Data Migration | 14 | 14 | ✅ |
| 13 | `TS` | Test & Acceptance | 18 | 18 | ✅ |
| 14 | `RP` | Reporting, Analytics & KPI | 16 | 16 | ✅ |
| 15 | `AP` | Integration & Developer | 12 | 12 | ✅ |
| 16 | `CM` | Change Management & Comms | 18 | 18 | ✅ |
| 17 | `OP` | Operations & Runbooks | 16 | 16 | ✅ |
| 18 | `EO` | Ecosystem Onboarding | 14 | 14 | ✅ |
| 19 | `MM` | Multimedia & Asset Specs | 12 | 12 | ✅ |
| **99** | **`RF`** | **Reference & Registers** | **12** | **12** | ✅ |
| | | **Total** | **452** | **452** | ✅ |

**Checks `A1`, `A2`, `A5` and `A6` pass.** Zero files on disk without a register entry; zero
register entries without a file.

> **This is the first time the register has been complete, and it is the least important sentence
> in this report.** 452 files are **written**. **Zero are `Approved`.** Thirty-two Class A and B
> files await unwaivable gate `G6`; 266 await a Bengali counterpart that `CM-R6` makes a
> precondition of approval; and the Programme Content Lead who is the final approver of every
> Class E file **does not exist as a post-holder**. A completion figure that does not say this
> is a figure that will be misread — which is the whole substance of `RF-006` `CD-14` and
> `RF-007` §4.9.

---

## 3. Checks that passed

| Check | Result |
|---|---|
| `A1` File count per category | ✅ 12 `RF` files; all 21 categories reconcile |
| `A2` Total content files | ✅ 452 enumerated against 452 registered |
| `A5` Files on disk with no register entry | ✅ **Zero** |
| `A6` Register entries with no file | ✅ **Zero** — for the first time |
| `B1` Content ID uniqueness | ✅ `RF-001`…`RF-012`, no duplicates |
| `B2` Contiguity | ✅ No gaps |
| `B3` No reused IDs | ✅ `RF-006` §4.8 retirement log present and correctly empty |
| `B4` File name matches ID | ✅ 12 of 12 conform to `<CODE>-<nnn>_<Name>.md` |
| `C1` `purpose:` declared | ✅ 12 of 12 |
| `C2` `traces_to:` declared | ✅ 12 of 12 |
| `C3` `traces_to:` targets resolve | ✅ after `RF-020-04` remediation, §5 |
| `D2` Files in the folder their category declares | ✅ 12 of 12 in `99_Reference_and_Registers/` |
| `D3` No spaces or ampersands in any path | ✅ |
| `D4` Reserved prefixes used correctly | ✅ |
| `D5` Superseded content archived | ✅ n/a — nothing superseded. **`_ARCHIVE/` remains empty and the process untested** (`RF-011` `CR-20`) |
| `E3` Factual claims carry a source and date | ✅ 71 declarations across 12 files, all classed |
| `E4` Verification dates within currency | ✅ **for Category 99** — all 71 are 2026-08-18, none in the future. ❌ register-wide: finding `RF-020-01` |
| `E7` Template conformance | ✅ 12 of 12 use template 1 Generic with the register-table and maintenance-procedure additions `CG-009` §3 requires for `RF` |
| **`F7`** Category-completion reconciliation | ✅ **Passes on all five dimensions** — §4 |
| `G2` Effort actuals against estimate | ✅ Within the §7 allocation of 55–85 person-days for `RF` |

---

## 4. Gate `F7` — the blocking reconciliation

`F7` is the only blocking check in the recurring checklist. A category may not be declared
complete while any derived count differs from its source. Five dimensions, all regenerated from
the files rather than read from a summary.

| Dimension | Source of truth | Declares for `RF` | Enumerated | ✓ |
|---|---|---|---|:--:|
| **File count** | Master Index §1 and §4 | 12 | 12 | ✅ |
| **Priority distribution** | Master Index §1 | `P0` 1 · `P1` 5 · `P2` 5 · `P3` 1 | `P0` 1 · `P1` 5 · `P2` 5 · `P3` 1 | ✅ |
| **Content class** | `CG-002` §4.1 | 12 Class `E` | 12 Class `E` | ✅ |
| **Bilingual split** | `CG-010` §3.2 | 2 bilingual, 10 English-only — `RF-001` and `RF-009` | 2 bilingual (`RF-001`, `RF-009`), 10 English-only | ✅ |
| **Template** | `CG-009` §3 | Template 1 Generic + register table + maintenance procedure | 12 of 12 | ✅ |
| **Wave** | Master Index §4 | `W0` 5 · `W1` 7 | `W0` 5 · `W1` 7 | ✅ |
| **ID contiguity and folder** | `CG-005`, Master Index §3.2 | `RF-001`–`RF-012` in `99_Reference_and_Registers/` | Identical | ✅ |

**`F7` passes.** Category 99 is the first category in the register to pass `F7` on its first run
with zero divergence on any dimension. That is not a virtue of the authoring; it is a consequence
of `F7` having been made blocking after `AUDIT-005`, and of the summary tables being **regenerated
after authoring rather than written ahead of it** (`CP-11`, `CM-R2`).

---

## 5. Findings

| ID | Finding | Sev | Owner | Status |
|---|---|:--:|---|:--:|
| `RF-020-01` | **331 `verified:` dates across 68 files are in the future**; no check compares a date to the present | **Critical** | Programme Content Lead | **Open** |
| `RF-020-02` | **ISO 9001:2015 is replaced on 16 September 2026**; 38 files cite its clauses; nothing in the programme mentions the revision | **Critical** | Quality Manager | **Open** |
| `RF-020-03` | **Check `G1` has never been run and fails**: eight `AUDIT-001` findings unclosed through nineteen subsequent audits with no escalation | High | CTO / CFO | **Open** |
| `RF-020-04` | **`CD-21` cited in two Category 99 files and never declared** | Medium | Programme Content Lead | **Fixed** |
| `RF-020-05` | **Master Index §5 undercounts portal content 3.8×** — 109 stated, 418 enumerated | High | Programme Content Lead | **Open** |
| `RF-020-06` | **The `D-nn` decision space collides across two governance documents**; `D-03` is cited 81 times and resolves two ways | High | CTO | **Open** |
| `RF-020-07` | **Six files cite the repealed Personal Data Protection Ordinance 2025** | High | Legal & Compliance | **Open** |
| `RF-020-08` | **`BRU-SRM-07`'s BDT 5,000 threshold has no stated basis** — VAT-inclusive or exclusive | High | Commercial Director | **Open** |
| `RF-020-09` | **Check `G4` fails**: 452 files name an owner, none names a person | Medium | Programme Content Lead | **Open** |
| `RF-020-10` | **432 content reviews fall due inside six days** | Medium | Programme Content Lead | **Open** |
| `RF-020-11` | **Category 99's own first five files breached `CD-07`**, the open-item rule Category 99 itself created | Medium | Programme Content Lead | **Fixed** |
| `RF-020-12` | **Category 99 states three different file counts and three different open-item counts across its twelve files** | Medium | Programme Content Lead | **Fixed by disclosure** |
| `RF-020-13` | **Master Index §12 and `README.md` cited `AUDIT-020` before it existed** | Medium | Programme Content Lead | **Fixed** |
| `RF-020-14` | **Category 99 contains no relative markdown links at all**; `D1` passes vacuously | Low | Programme Content Lead | **Accepted** |

---

### `RF-020-01` — 331 verification dates are in the future *(Critical)*

**What was found.** Extraction `X4` over all 1,642 `verified:` declarations at the enumeration
instant:

| `verified:` | Declarations | Status |
|---|---:|---|
| 2026-08-12 … 2026-08-18 | 1,311 | Past or present |
| **2026-08-19** | **69** | **Future** |
| **2026-08-20** | **262** | **Future** |

**331 declarations across 68 files** — the whole of Categories 13 `TS`, 14 `RP`, 16 `CM` and 17
`OP` — carry a date that has not occurred. Three audit reports carry the same defect in their own
`date:` and `enumeration_date:`: `AUDIT-014` (2026-08-19), `AUDIT-017` and `AUDIT-019`
(2026-08-20).

**Why it matters.** `CG-012` and `CM-R8` make the verification date *the* control, and `DoD-17`
makes it a Definition of Done item. A future date cannot be a record of a source having been read,
and it silently extends the currency window. More seriously it makes the whole field unusable as
audit evidence: a reader who finds one impossible date must treat all 1,642 as unaudited.

**How it happened.** Not carelessness. The dates are internally consistent with each other and
inconsistent only with the calendar — the Master Index itself records "352 at 2026-08-19" as a
superseded figure. The most probable cause is a nominal date advanced per authoring session rather
than read from the system clock. **Nineteen prior audits did not catch it because no check compares
a date to the present day.** Check `E4` compares verification dates to *the currency policy* — a
window — and a future date passes a window test.

**Remediation instruction.** Correct the 331 declarations to the date the source was actually read;
where unknown, set the file's own `date:` and add `recheck: required`. Correct the three audit
reports' `date:` and `enumeration_date:`. **Add check `A7` to `AUDIT_Checklist_Recurring.md`:**
*no `verified:`, `enumeration_date:` or `date:` value may be later than the audit's own run date.*
Proposed as governance rule **`RG-09`**.

---

### `RF-020-02` — ISO 9001:2015 is replaced inside the delivery window *(Critical)*

**What was found.** Externally verified on 2026-08-18: **ISO 9001:2026 publishes 16 September
2026**, replaces ISO 9001:2015, and carries a three-year transition to **September 2029**. First
certificates to the new edition are not expected before Q3 2027.

**38 content files cite ISO 9001:2015 clause numbers.** Among them `LG-022` (the quality policy set
inspected at every surveillance audit), `DT-043` (the NCR/CAPA and internal-audit forms the
certification body inspects), `SP-029`, `TR-016`, `MD-046`, `KB-012` and `KB-015`. `P11` is the
application auditors will use.

**Nothing in the programme mentions the revision** — not `00-04`, not `LG-022`, not `RF-008`'s
predecessors, not nineteen audits.

**Why it matters.** The programme describes ISO 9001:2015 certification as the company's principal
market differentiator, and the transition falls **entirely inside the 36-month delivery window**.
Every clause citation in those 38 files will reference a superseded edition before Wave 2, and
clause numbering is expected to move.

**How it happened.** `DoD-17` binds *module* specifications to verified regulatory citations.
Nothing bound the content set, and no currency-review cadence existed for standards until `RF-008`
§4.6 created one. This finding is the first output of that cadence, on the day it was written.

**Remediation instruction.** Raise **`PD-21` — ISO 9001:2026 transition plan**, owned by the
Quality Manager with the CEO, needed at W1; it is a certification decision, not a content decision.
**Do not retro-cite the 2026 edition before publication** — that would repeat `RSK-035` in the
opposite direction. Register `ST-21` as a watched instrument in `RF-008`, with `RF-002` §4.5
firing the 38-file re-open on publication.

---

### `RF-020-03` — check `G1` has never been run, and it fails *(High)*

`G1` requires that no finding stay open across three consecutive audits without escalation. It has
never been answerable, because there was no cross-audit index to answer it from. `RF-012` §4.4
`RC-04` supplies one.

**Eight `AUDIT-001` findings have been open since 2026-08-15 and unclosed through all nineteen
subsequent audits.** Category 99 partially discharges three of them:

| Finding | Status after Category 99 |
|---|---|
| `AF-01` portal specifications misfiled | **Fully open** — CTO decision |
| `AF-04` `00-05` decision log absent | **Partially discharged** — `RF-006` now exists on the content side; `00-05` still absent |
| `AF-06` `05-01` requirement count | **Partially discharged** — `RF-003` §4.2 closes the *diagnosis*; the restatement is owed |
| `AF-07` `05-02`/`05-04` module counts | **Fully open** |
| `AF-08` `02-05` effort restatement | **Fully open** |
| `AF-09` content effort absent from the business case | **Fully open** — and now compounded by `RF-007`'s backlog |
| `AF-14` module files cite misfiled portal paths | **Fully open** — depends on `AF-01` |
| `AF-15` `99_Reference/` planned documents absent | **Partially discharged** — `RF-001` supplies the glossary content-side |

**Five fully open; three partially discharged.** Every one requires a decision outside the content
workstream. The escalation `G1` mandates has never happened, because the check could not be run.

**Remediation instruction.** All eight are registered in `RF-011` as risks with named owning roles
— the only mechanism that puts them before the Steering Committee. Adopt rule **`RG-12`**: a
finding open across three consecutive audits is escalated to the risk register, not restated.

---

### `RF-020-05` — Master Index §5 undercounts portal content by 3.8× *(High)*

§5 is headed *"Content Coverage by Portal"* with a column *"Total direct"* summing to **109**.
Extraction `X3` finds **418** file-portal links. `P06` reads as 5 files and has 23 — including all
seven `RP` files without which the portal cannot be built.

§5's own footnote explains the intent — cross-cutting content is not repeated per portal — and that
is defensible for a *cross-reference*. It is not defensible for a table headed "coverage" that
go-live gates read as a count. **Remediation:** rename the column to *"Portal-primary files"*;
`RF-005` §4.4 becomes the coverage map. Logged as `RF-006` `CD-03`.

---

### `RF-020-06` — the `D-nn` decision space collides *(High)*

`00-04` §6 and `_CATEGORY_E_AUDIT_REPORT.md` both number decisions from `D-01`. **`D-03` is cited
81 times across the workspace** and resolves to the marketplace principal-or-agent determination in
one document and to opening-balance methodology in the other.

**Remediation:** `RF-006` `CD-04` allocates `PD-` / `CD-` / `ED-` and deprecates bare `D-nn`.
Implementation requires `00-04` and `_CATEGORY_E_AUDIT_REPORT.md` to be edited by their owners;
`RF-006` maps rather than renames until then.

---

### `RF-020-07` — six files cite a repealed statute *(High)*

Verified sequence: Personal Data Protection **Ordinance** 2025 issued 6 Nov 2025; amended by
Ordinance 23 of 2026 on 5 Feb 2026; **repealed** and replaced by the Personal Data Protection
**Act 2026 (Law 63 of 2026)** in April 2026. Fifty citations use the Act; **six use the repealed
Ordinance**.

The six were correct when written. **This is `RSK-035` recurring four months after its mitigation
was written**, which is the finding — not the six edits. **Remediation:** standardise on the Act,
retaining the Ordinance lineage only where the February 2026 residency amendment is relied on
(`NFR-086a/b/c`, `LG-012`). Logged as `RF-006` `CD-09`.

---

### `RF-020-08` — a hard business rule with an ambiguous trigger *(High)*

Found by populating `RF-009` `WE-01`. `BRU-SRM-07` requires documented customer approval for
estimates **above BDT 5,000** and **no document states whether that is VAT-inclusive or
VAT-exclusive**. At 15% VAT the two bases diverge by 15%: estimates between BDT 4,348 and BDT 5,000
exclusive are above the threshold on one basis and below on the other.

`BRU-SRM-07`, `DT-005`, `MD-029`, `UI-038` and `SP-013` each assume the basis is stated elsewhere.
A rules engine and a branch agent will therefore enforce it differently, and the difference is
invisible until a dispute. **Remediation:** state the basis in `MD-029`; reference it from
`BRU-SRM-07`.

> **This is the argument for worked examples.** Five files specify this rule and none exposed the
> ambiguity. Populating one estimate did, immediately, because a populated field must have a
> value.

---

### `RF-020-09` and `RF-020-10` — checks `G4` and the review peak *(Medium)*

**`G4` fails.** 452 files declare an `owner:` and an `approver:`. **Zero name an individual. Zero
name a deputy.** Only 11 files mention a deputy at all. Four categories — `UI` (42), `BN` (18),
`AP` (11 of 12), `TR` (18 of 24) — have a single owning function each, and therefore 83 files with
one point of failure and no named alternate. `RF-010` §4.1 publishes the name columns **empty**
rather than filling them plausibly, and §4.3 lists the seven unfilled roles the register depends
on.

**The review peak.** 432 files carry a `review_due:` inside six days (2027-02-15…20), because each
was given +6 months at authoring and the set was authored in one week. The Content Design Lead
alone would own 68 reviews in that week and the CFO 33 approvals. **Remediation:** `RF-010` rule
`OW-03` staggers reviews by consuming wave and instrument class.

---

### `RF-020-11` — Category 99 breached its own rule *(Medium, fixed)*

`RF-006` `CD-07` rules that open items are qualified with their owning file — `<ID>-OI-nn` — because
1,278 bare `O-nn` identifiers across 201 files cannot be consolidated or escalated.

**`RF-001` through `RF-005` used the bare form.** Thirty-nine open items in the five files that
were authored before `RF-006` existed.

**Why this is reported rather than quietly corrected.** The failure mode is exactly the one
`AUDIT-018` named: *"three auditors have now fixed the same defect by hand instead of the check
being changed once."* The order of authoring, not the care of the author, produced it — and a
category that rules on open-item form should be the first place the rule is visibly applied.

**Remediation applied.** All 39 converted to `RF-001-OI-nn` … `RF-005-OI-nn`. Verified: zero bare
`O-nn` remain in Category 99.

---

### `RF-020-12` — Category 99 states three different file counts *(Medium, fixed by disclosure)*

| Figure | Stated in | Correct at |
|---:|---|---|
| 429 content files | `RF-001`–`RF-005` | Instant of authoring |
| 443 content files | `RF-008`, `RF-009` | ~2 hours later |
| 449 content files | `RF-010`, `RF-011` | ~1 hour later again |
| **452 content files** | This report | 2026-08-18 00:26 Asia/Dhaka |

Open-item counts diverge the same way: 1,185 / 187 files → 1,230 / 195 → 1,278 / 201.

**Every figure was correct at its own instant.** Category 19 `MM` grew from 0 to 12 files during
the authoring of Category 99 — `MM-001` did not exist at 01:07 and existed at 01:18.

**This is `RG-08` behaving as designed, not a defect** — and it is nonetheless a defect in
*presentation*, because a reader meeting 429 and 452 in the same category will read a
contradiction. **Remediation applied by disclosure:** this section is the reconciliation, and
`RF-006` `CD-14` requires every count to carry its instant and be declared a floor. The individual
figures are **not** retro-edited; doing so would need re-doing at the next enumeration and would
destroy the evidence that the rule works.

---

### `RF-020-13` — the governing documents cited this report before it existed *(Medium, fixed)*

Master Index §12 and `README.md` were updated to record Category 99 complete and **cited
`AUDIT-020`** while `_AUDIT/AUDIT-020_*.md` did not exist. `CM-R1` is register-first; the
equivalent for audits is that a report is cited after it is issued.

**Remediation applied.** This report is issued. Two figures in those updates are corrected in §7:
the Master Index and `README.md` state *"six findings open across seventeen consecutive audits"*;
the enumerated position is **eight findings open across nineteen**, of which five are fully open
and three are partially discharged by Category 99.

---

### `RF-020-14` — no relative links anywhere in Category 99 *(Low, accepted)*

Extraction found **zero** relative markdown links across the twelve files. Check `D1` — *all
internal links resolve* — therefore passes **vacuously**: there are no links to break.

This is a deliberate consequence of `RF-006` `CD-06`, which maintains the registers **by identifier
rather than by filesystem path** so that `RF-005` does not depend on the resolution of `AF-01`.
The cost is that a reader cannot click through. **Accepted**, with the trade-off recorded: while
`AF-01` is open, path-based navigation in a portal register would be wrong half the time, and a
wrong link is worse than no link.

---

## 6. What Category 99 closes

| Closed or advanced | Evidence |
|---|---|
| **`AUDIT-017` `OP-12`** — 94 open decisions with nowhere to be logged; `RF-006` blocking Definition of Done in five categories | `RF-006` written; DoD line dischargeable |
| **`AUDIT-017` `R-05`** — *"write `RF-006` ahead of the rest of Category 99"* | Honoured; `RF-006` is first in every Category 99 dependency chain |
| **`AF-06` / `TS-01` diagnosis** — three "rival" denominators | `RF-003` §4.2: one prose estimate and two counts of different scopes. Denominator **3,350**, scope stated |
| **`AF-15` (partial)** — `99_Reference/` planned documents absent | `RF-001` supplies the glossary content-side |
| **`AF-04` (partial)** — `00-05` absent | `RF-006` supplies the decision log content-side |
| **Check `G1`** — never answerable | `RF-012` §4.4 answers it, and it fails |
| **Check `G4`** — reported as passing | `RF-010` §4.8 answers it, and it fails |
| **Check `G5`** — content risks reviewed | `RF-011` exists; passable after its first review |
| **`AUDIT-018` `EO-04`** — Master Index wave windows disagree with `06-01` in all nine rows | `RF-004` uses `02-02` rather than propagating the disputed table; raised as `PD-18` in `RF-006` |
| **45 wave inversions across seven categories**, never fixed at source | `RF-004` §4.5 states them per module for the first time; `RF-011` `CR-08` gives them an owner who can act |

---

## 7. Remediation applied

| # | Change | File |
|---|---|---|
| 1 | 39 bare `O-nn` open items converted to the qualified `RF-nnn-OI-nn` form (`CD-07`) | `RF-001`…`RF-005` |
| 2 | `PD-21` (ISO 9001:2026 transition) and `PD-22` (WCAG 2.1 vs 2.2) added to the unregistered-decision table; header restated `PD-16`…`PD-22`; totals restated 22 open / seven unregistered | `RF-006` §4.3 |
| 3 | Dangling `CD-21` citations repointed to `PD-22` | `RF-008` §4.7, §Open Items; `RF-011` `CR-14` |
| 4 | `PD-01`…`PD-21` scope reference corrected to `PD-01`…`PD-22` | `RF-011` §4.4 |
| 5 | This report issued, closing the forward reference in Master Index §12 and `README.md` | `_AUDIT/AUDIT-020` |

**Correction required in two documents, not applied here because they are outside this audit's
authorship:** Master Index §12 and `README.md` state *"six findings open across seventeen
consecutive audits"*. The enumerated position is **eight across nineteen** — five fully open,
three partially discharged. Owner: Programme Content Lead.

---

## 8. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Raise `PD-21` ISO 9001:2026 transition at the next Steering Committee.** It has a fixed external deadline the programme does not control — 16 September 2026 | Quality Manager with CEO | **Immediately** |
| **R-02** | **Correct the 331 future-dated verifications and add check `A7` / rule `RG-09`** | Programme Content Lead | W1 |
| **R-03** | **Appoint the Programme Content Lead.** 26 files have no possible approver, 14 content decisions are unratified, and six of the seven other appointment gaps have no one to chase them | **CEO** | **Immediately** |
| **R-04** | **Take the five register-change decisions as one paper** — `TR-025`, `BN-019`, `DM-015`, `DM-016`, `SP-035`; register moves 452 → 457. Two are `P0` | Steering Committee | W1 |
| **R-05** | **Adopt rules `RG-08`…`RG-12`** and add check `A7` | Programme Content Lead | W1 |
| **R-06** | **Escalate the eight never-closed `AUDIT-001` findings to the Steering Committee via `RF-011`**, as `RG-12` requires | CTO / CFO | Next sitting |
| **R-07** | **Apply `OW-03` review staggering before 2027-02-15**, while the dates are still distant | Programme Content Lead | W2 |
| **R-08** | **Re-audit Categories 01 `VB`, 02 `MD`, 03 `UI`, 04 `NT`** — audited by a method that has since found three times as much per category | Programme Content Lead | W2 |
| **R-09** | **Audit Category 19 `MM`** — completed concurrently with Category 99 and not yet audited | Programme Content Lead | W1 |

---

## 9. Closure

Category 99 is **complete on disk — 12 of 12** — and the register is **complete — 452 of 452**.
Gate `F7` passes on all seven dimensions with zero divergence, the first category to do so on its
first run.

**The register being complete is not the finding. This is:**

> **452 content files are written and none of them is approved.** The three checks that measure
> whether content is *governed* rather than merely *present* — `G1` findings escalation, `G4`
> named ownership, `G5` risk review — could not previously be run. Two of the three now run, and
> **both fail**. The third becomes passable only when the register this audit issues is reviewed
> once.
>
> A programme that can now see this is in a better position than one that could not. But the
> instruments Category 99 supplies are diagnostic, not curative. Every one of the ten open
> findings requires a decision, an appointment or a budget that the content workstream cannot
> provide — and the two Critical ones have external deadlines the programme does not control:
> ISO 9001:2026 on **16 September 2026**, and PDPA 2026 compliance by **approximately May 2027**.

**Proposed governance rules from this audit:** `RG-08` (enumeration instants and floors),
`RG-09` (no future dates; check `A7`), `RG-10` (a defect fixed twice by hand is a check defect),
`RG-11` (qualified finding citation), `RG-12` (three-audit findings escalate to risk).

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
*Auditor: Programme Content Lead · Enumeration instant: 2026-08-18 00:26 Asia/Dhaka*
