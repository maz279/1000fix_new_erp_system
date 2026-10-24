---
id: RP-010
title: Board and Management Pack Template
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Finance Manager with the CEO office and Programme Manager
reviewers: [CEO, CFO, CTO, CCO, Operations Director, Company Secretary, BI Lead, Programme Manager]
approver: CFO with CEO
content_class: D
purpose: >
  The standing contents and order of the monthly management pack and the quarterly board pack — what
  is in it, who owns each section, how long each may be, and what is deliberately excluded. Packs
  assembled ad hoc consume days of effort every month and vary in ways that hide trends: a section
  that appears when performance is good and disappears when it is not is worse than no section, and a
  pack whose order changes cannot be read across quarters. The programme also commits to cutting
  manual management reporting effort by 90%, which is only measurable against a defined pack.
traces_to: [06-02, 06-02 §3, 06-02 §4, 06-02 §5, 06-02 §6, P06, 04-00 P06, RP-001, RP-002, RP-003, RP-008, RP-009, RP-011, RP-014, RP-015, RP-016, TS-018, SP-020, CG-006, M24, 05-02 §10]
priority: P2
wave: W5
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §6 Benefit Tracking Discipline — the PMO publishes a KPI dashboard monthly with benefit owners commenting on variance; the Steering Committee reviews benefit realisation quarterly and agrees corrective action; post-implementation benefits audit at Month 42; §4 wave gate Go/No-Go criteria; §5 programme success criteria
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P06 KPIs — manual management reporting effort −90%; decisions made on live data rather than compiled spreadsheets, 100% of management reviews; weekly usage by managers > 90%
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Board and Management Pack Template

| Item | Value |
|---|---|
| Packs | **2** — monthly management pack, quarterly board pack |
| Monthly length | **≤ 12 pages** |
| Quarterly length | **≤ 20 pages** |
| Assembly | **Generated from `P06`**, not compiled (§4.5) |
| Wave | W5 · `P2` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` table addition applied as the section schema in §4.2. All six sections retained in order.

---

## 1. Purpose

`04-00` `P06` commits to **100% of management reviews running on live data** and to cutting manual
management reporting effort by **90%**. `06-02` §6 requires a monthly KPI dashboard with owner
commentary and a quarterly Steering review of benefit realisation.

**Those two commitments pull in opposite directions unless the pack is defined.** A live dashboard and
a monthly pack are not naturally the same thing: the pack is a point-in-time artefact that a board
reads, annotates and minutes against, and if it is assembled by hand from dashboards then the 90%
effort reduction never arrives. The pack must be **generated** from the same views, with commentary
added — which requires knowing exactly what is in it.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| Standing contents | Sections appear and disappear with performance. A missing section is read as an answer |
| Fixed order | The pack cannot be read across quarters, and trend-spotting is the board's main function |
| Length limits | The pack grows until the board reads the first three pages, which is the pathology `04-00`'s 90% target exists to remove |
| Named section owners | Assembly falls to Finance, who then own commentary on operations they do not run |
| A generation rule | Manual compilation persists and the 90% reduction is unmeasurable |
| An exclusion list | Every director's preferred metric is added and none is ever removed |

---

## 2. Scope

**In scope.** The contents, order, ownership, length and generation method of the monthly management
pack and the quarterly board pack; the wave-gate pack variant; distribution, classification and
retention; and the exclusion list.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Commentary structures and wording | **`RP-008`** — this file says which commentary appears where; `RP-008` says how it is written |
| The dashboards the pack is generated from | `RP-003` |
| Metric definitions | `RP-001` |
| Statutory filings | `RP-009` — a filing is not a pack section; §4.4 item 7 reports *whether* filings were made |
| Board minutes, agendas and resolutions | Company Secretary |
| Gate Go/No-Go decisions and their forms | **`TS-018`** §4.5 — §4.6 states the seam |
| Export marking | `RP-014` |
| Report catalogue | `RP-002` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Board and CEO** | The quarterly pack |
| **Executive team** `R01`–`R05` | The monthly pack |
| **Section owners** | What they owe each month and by when |
| **Finance Manager** | Assembly and the production calendar |
| **Company Secretary** | The quarterly pack as a board paper |
| **Programme Manager** | The programme and benefit sections |
| **BI Lead** | What must be generable from `P06` |

---

## 4. Content

### 4.1 Rules

| # | Rule |
|---|---|
| **BP-01** | **Standing contents.** Every section appears every period, whether or not it has good news. A section with nothing to report says "no exceptions" |
| **BP-02** | **Fixed order.** The order does not change between periods; a new section is inserted at a decided position and the change is minuted |
| **BP-03** | **Length is capped and enforced** — 12 pages monthly, 20 quarterly. A section exceeding its allowance displaces another, and the displacement is a decision |
| **BP-04** | **Every section has one named owner** who writes its commentary (`RP-008` `NR-06`) |
| **BP-05** | **Generated, not compiled** (§4.5). Every number comes from a `P06` view; commentary is added, numbers are not re-typed |
| **BP-06** | **No number appears in a pack that is not on a dashboard.** A pack-only number has no owner, no definition and no drill |
| **BP-07** | **Every metric is named by its `RP-001` identifier**, and a `Provisional` metric is labelled as such (`KD-22`, `NR-10`) |
| **BP-08** | **Every number carries a comparator** — prior period, target or baseline (`XD-12`) |
| **BP-09** | **A metric with no measured baseline is not presented as a trend** (`KD-20`, `NR-11`) |
| **BP-10** | **Exceptions only in the body; completeness in the appendix.** The board reads exceptions; the full metric set is appended for reference and is not walked through |
| **BP-11** | **Prior decisions are revisited first** (§4.4 item 1). A pack that never returns to last quarter's decision is a pack with no accountability |
| **BP-12** | **Bad news goes first within its section.** A section opening with achievements and closing with a miss has buried the miss |
| **BP-13** | **The pack is classified and marked** (`05-02` §10, `RP-014`); the quarterly pack is `S2` at minimum |
| **BP-14** | **The pack and its commentary are retained together** as a record (`M24`, `NFR-088`), because the Month 42 benefits audit reads the explanations |
| **BP-15** | **Production effort is measured every month** against the `04-00` 90%-reduction target. **An unmeasured effort target is never met** |

### 4.2 The section schema

| Field | Content |
|---|---|
| `section` | Name and fixed position |
| `owner` | One named role (`BP-04`) |
| `source` | The `RP-003` view or `RP-002` report it is generated from (`BP-05`) |
| `pages` | Allowance (`BP-03`) |
| `commentary` | Which `RP-008` template applies |
| `cadence` | Monthly · quarterly · both |
| `classification` | `S1`–`S3` |

### 4.3 The monthly management pack — 12 pages

| # | Section | Owner | Source | Pages | Commentary |
|---:|---|---|---|:--:|---|
| 1 | **Decisions and actions outstanding** | Programme Manager | `TS-018` register + prior pack | 1 | — |
| 2 | **Executive summary** | CEO office | `RP-003` `E1` | 1 | `RP-008` `N4` |
| 3 | **Group performance** — the nine `E1` slots | CFO | `E1` | 1 | — |
| 4 | **Revenue streams** — 14 rows, exceptions annotated | CCO | `E2` | 2 | `N2` extract |
| 5 | **Financial position** | CFO | `E3` | 2 | `N2` |
| 6 | **Service delivery** | Operations Director | `E4` | 1 | `N1` |
| 7 | **Statutory position** — filings made, on time, clean; exceptions first | CFO | `RP-009` calendar | 0.5 | `N2` item 5 |
| 8 | **Quality** | Quality Manager | Quality console `C9` | 1 | `N3` |
| 9 | **People** — headcount, attendance, certification currency, payroll control | HR Manager | HR console `C8` | 0.5 | Exceptions only |
| 10 | **Platform and data quality** | CTO | `E7` + `RP-016` | 1 | Exceptions only |
| 11 | **Benefit realisation** | Programme Manager | `RP-015` + `E7` slot 7 | 1 | `N5` |
| 12 | **Appendix — full metric set** | BI Lead | `RP-001` | not counted | — |

**Section 1 is first and it is deliberate.** `BP-11`: the pack opens with what was decided last month
and what happened. A pack that opens with performance invites a review of performance; a pack that
opens with outstanding decisions invites a decision.

**Section 7 is half a page and it is never dropped.** `KPI-057` and `KPI-058` target zero, so in a
good month it reads *"all filings made on time, zero adjustments, zero findings"* — one line. `BP-01`
keeps it there so that the month it is not one line, the absence is impossible.

### 4.4 The quarterly board pack — 20 pages

The monthly pack plus five quarterly sections, in this order:

| # | Section | Owner | Pages |
|---:|---|---|:--:|
| 1 | **Decisions and actions outstanding**, including last quarter's board decisions | Company Secretary with Programme Manager | 1 |
| 2 | **Executive summary — quarterly variant** | CEO office | 1 |
| 3–12 | The monthly sections, quarter-to-date | as monthly | 10 |
| 13 | **Benefit realisation against the `06-02` §3.2 curve**, by benefit line, with `N5` per line | Programme Manager | 2 |
| 14 | **Programme position** — wave gate status, open-defect profile, deferral register (`TS-018`) | Programme Manager | 1.5 |
| 15 | **Risk** — movements, new risks, and `RSK-032` PDPA exposure | CTO with Legal Counsel | 1 |
| 16 | **Strategic items** — the two or three matters requiring board direction | CEO | 2 |
| 17 | **Branch league** — quarterly, per `RP-011` `LT-11` | Operations Director | 1 |
| 18 | Appendix | BI Lead | not counted |

**Section 17 is quarterly and only quarterly.** `RP-011` `LT-11` prohibits monthly league publication
because monthly ranking noise invites gaming; the board pack is the only place the league is
published, and it appears four times a year.

### 4.5 Generation, not compilation

`BP-05` and `BP-15` together are how the 90% target is met.

| Step | Method | Effort |
|---|---|---|
| 1 | Every number rendered from its `P06` view at a fixed cut-off (`RP-013` schedule) | **Automated** |
| 2 | Commentary written by section owners into the `RP-008` field schema | Owner time, ~20–30 hours total (`RP-008` `O-04`) |
| 3 | Assembly — sections placed in fixed order with fixed allowances | **Automated** |
| 4 | Review — Finance Manager checks completeness, not content | 2 hours |
| 5 | Classification, marking and distribution (`RP-014`) | **Automated** |
| 6 | **Effort recorded** against the `04-00` baseline (`BP-15`) | 10 minutes |

**Step 3 being automated is what makes the length caps real.** A hand-assembled pack absorbs an
over-long section silently; a generated one rejects it and forces the `BP-03` displacement decision.

> **The baseline for the 90% reduction does not exist.** `04-00` sets −90% and `06-02` §6 requires
> every baseline measured and signed off before the wave begins. **Nobody has measured the current
> effort of producing a management pack**, so the target has no denominator — the same defect
> `RP-015` addresses across the KPI set. `O-02`.

### 4.6 The seam with `TS-018` gate packs

| | **Management / board pack** *(this file)* | **Gate acceptance pack** (`TS-018` §4.5) |
|---|---|---|
| Purpose | Run the business and the programme | Take a Go/No-Go decision |
| Cadence | Monthly and quarterly | Nine times, at gates |
| Audience | Board and executive | Programme Manager, CTO, business owners, Steering |
| Contains | Performance, benefits, risk | Criteria, coverage, defect profile, deferrals, statutory and accessibility position |

**Section 14 of the quarterly pack reports the gate position; it does not replace the gate form.** A
board reading a summarised gate position is informed; a board taking a Go decision from a summary is
taking it without the evidence. `TS-018` `CP-G4` already forbids a conditional pass on statutory or
`S1` items, and that decision belongs on the gate form.

### 4.7 Excluded from both packs

| Excluded | Why |
|---|---|
| **Any named individual's performance** | `RP-008` `NR-14`; and a board pack is a discoverable document |
| **Named customers** | No board decision needs one; `05-02` §10 `S2` |
| **Any `S3` field** | `BRU-DAT-11` (`M62` §9); `05-02` §10 |
| **A metric not on a dashboard** | `BP-06` — no owner, no definition, no drill |
| **A section requested for one period only** | `BP-01` standing contents; a one-off goes to the strategic items section as a paper, not as a new section |
| **Unsourced external benchmarks** | `CG-012`; `RP-008` prohibitions |
| **A trend on an unbaselined metric** | `BP-09` |
| **Slideware** — decorative charts with no comparator | `RP-007` `CH-13` |
| **The full metric set in the body** | `BP-10` — it is the appendix |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **[`RP-003`](RP-003_Dashboard_Specification_Pack_Executive.md)** | Every number is generated from `E1`–`E7` (`BP-05`, `BP-06`) |
| **[`RP-008`](RP-008_Report_Narrative_and_Commentary_Template_Set.md)** | The commentary structures each section carries |
| **[`RP-015`](RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md)** | Baselines for `BP-08`/`BP-09` and section 11/13 |
| [`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md) | Metric identifiers and provisional labelling |
| [`RP-009`](RP-009_Statutory_and_Regulatory_Report_Format_Register.md) | The statutory position in section 7 |
| [`RP-011`](RP-011_Branch_League_Table_Definition_and_Scoring_Rules.md) | The quarterly league, section 17 |
| [`RP-013`](RP-013_Scheduled_Report_and_Subscription_Catalogue.md) | The fixed cut-off and scheduled generation |
| [`RP-014`](RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) | Classification and marking (`BP-13`) |
| [`RP-016`](RP-016_Data_Quality_Scorecard_Definition.md) | Data-quality position in section 10 |
| [`TS-018`](../13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md) | The programme position in section 14, and the seam in §4.6 |
| `06-02` §3, §4, §5, §6 | Benefits, gates, success criteria, tracking discipline |
| `M24`, `NFR-088` | Retention of the pack with its commentary |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually, and after any board request for a new section (`BP-02`) |
| Trigger for out-of-cycle review | A new benefit line; a new statutory obligation; a gate added; a length breach recurring; the effort measure moving the wrong way |
| Owner | Finance Manager with the CEO office |
| Data file | `RP-010_Pack_Sections.csv` — monthly and quarterly section registers with owner, source, allowance |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`06-02` §6 requires a monthly KPI dashboard with owner commentary from the first wave a benefit is realisable — W2 — and a quarterly Steering benefit review throughout.** This file is **W5**, so roughly three years of packs would be produced before the template exists. `RP-008` `O-01` records the same exposure for the commentary half | Programme Content Lead with Finance | **W2 — the monthly pack is needed from the first Steering review** |
| **O-02** | **The 90%-reduction target has no baseline.** `04-00` sets −90% on manual management reporting effort and `06-02` §6 requires every baseline measured and signed off **before** the wave begins. **Nobody has measured what producing a management pack costs today**, so `BP-15` has nothing to measure against and the target is unfalsifiable. `RP-015` should carry it | Programme Manager with Finance | **W0 — via `RP-015`** |
| **O-03** | **`BP-05` generation depends on `P06`, which is W4, and on `RP-013` scheduling, which is W4.** Packs produced before W4 are compiled by hand, which is the state the target exists to remove — so the interim packs will *raise* the baseline the reduction is measured from unless the pre-W4 effort is recorded separately | BI Lead with Finance Manager | **W4** |
| **O-04** | **Section 11 and quarterly section 13 report benefit realisation, and most benefit lines will read `NOT MEASURED`.** 44 of 95 baselines are absent (`RP-001` `O-06`). **A board pack section that reads "not measured" against a BDT 876 lac benefit case every month is the correct output and an uncomfortable one**, and the Steering Committee should see it deliberately rather than discover it | Programme with Finance | **W5** |
| **O-05** | **No section owner has agreed their allowance.** `BP-03` caps section length and `BP-04` names one owner each; neither has been reviewed with the ten owners involved. A cap set by the content function is the first thing a director overrides | Finance Manager with each section owner | **W5** |
| **O-06** | **`BP-13` requires the pack classified, and `RP-014` is W4 while this file is W5** — consistent. But **the quarterly board pack is a discoverable document in a dispute**, and whether `S2` is the right floor for a pack containing branch-level margin and league rankings is a Legal question nobody has asked | Legal Counsel with CFO | W5 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the section schema
- [x] **The two `04-00` commitments identified as pulling in opposite directions unless the pack is generated rather than compiled**
- [x] Fifteen rules stated, including standing contents, fixed order, enforced length and bad-news-first
- [x] Monthly pack specified — 12 sections, 12 pages, owner and source per section
- [x] Quarterly pack specified — 18 sections, 20 pages, with the five quarterly additions
- [x] **Decisions-outstanding placed first in both packs, with the reason**
- [x] **The statutory section kept at half a page and never dropped, so its absence becomes impossible**
- [x] A six-step generation method with effort measured against the `04-00` target
- [x] **The seam with `TS-018` gate packs stated — a board is informed by a gate summary, it does not decide from one**
- [x] Nine exclusions each carrying its reason
- [x] League publication limited to quarterly, consistent with `RP-011` `LT-11`
- [x] All internal links resolve
- [x] Six open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` packs needed from W2 against a W5 file — outstanding**
- [ ] **`O-02` the 90%-reduction target has no baseline — outstanding; unfalsifiable as written**
- [ ] **`O-04` benefit sections will read `NOT MEASURED` — outstanding; a Steering matter**
- [ ] Named approvers recorded — **pending CFO and CEO**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
