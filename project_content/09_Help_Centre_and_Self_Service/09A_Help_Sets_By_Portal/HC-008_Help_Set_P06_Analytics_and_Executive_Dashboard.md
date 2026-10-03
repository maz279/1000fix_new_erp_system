---
id: HC-008
title: Help Set — P06 Analytics and Executive Dashboard
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design with BI
author: Content Design with Business Intelligence
reviewers: [BI Lead, CTO, Finance Manager, Operations Director, Security Lead, Localisation Lead]
approver: Content Design Lead with BI Lead
content_class: D
purpose: >
  The help set for analytics and dashboard users covering metric definitions, drill paths,
  self-service analysis, subscriptions and row-level security. Self-service BI without definitional
  help produces confident misreporting to the board — the failure mode is not that people cannot
  find a number, it is that they find one and are certain it means something it does not.
traces_to: [P06, P03, P04, P08, M25, M62, M29, M61, RP-001, RP-002, HC-001, HC-002, HC-006, UI-016, TR-011]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: HC-008_Help_Set_P06_Analytics_and_Executive_Dashboard_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P06 analytics and executive dashboards; an unlabelled executive dashboard produces confidently wrong decisions
    verified: 2026-08-18
    class: P1
  - source: project_content/08_Training_and_Enablement/08B_Course_Packs/TR-011_Course_Pack_Branch_Manager.md §4 — 51+ managers reading the same number must read it the same way; a metric defined locally is a metric nobody can compare
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P06 Analytics and Executive Dashboard

| Item | Value |
|---|---|
| Portal | `P06` Analytics & Executive Dashboard |
| Audience | **Not a distinct audience** — a mode of use by audiences 3 (internal), 4 (corporate) and 7 (brand partner). See `HC-001` `IA-01` |
| Article type | Help set specification — **Concept predominates**, unusually |
| Reading level target | `CG-011`; business audience including executives |
| Languages | English primary, Bengali parallel (`HS-30`) |
| Related UI copy | `UI-016` `P06` copy pack |

> **Template conformance.** As `HC-003`, applied at set level.
>
> **`PS-14`: this is the only help set where Concept articles outnumber Task articles**, and the
> reason matters. Every other set answers *"how do I do this?"*. This one mostly answers *"what does
> this number mean, and may I rely on it?"* — a question that has no steps.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and shape |
| `UI-016` | Metric names, filter labels and drill-path labels quoted in articles |
| **`RP-001` KPI Dictionary and Metric Definition Standard** | **The authoritative definition of every metric.** This set explains and links; it never defines (`IA-12`) — **unwritten, `O-01`** |
| `RP-002` Report Catalogue by Role and Module | Which report exists for whom |

**`PS-15`: this set never defines a metric.** `RP-001` owns every formula, numerator, denominator,
inclusion, exclusion, grain and source. A help article that restates a definition creates a second
definition, which is the exact failure the whole file exists to prevent (`CP-01`, `IA-12`).

---

## Steps — *the analytics user's questions*

### Block A — Reading a number *(9 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 1 | **What this number means and where it comes from** *(the metric-lookup pattern)* | Concept | **P0** |
| 2 | **Why two reports show different numbers** | Concept | **P0** |
| 3 | **As-at, as-of and the grain of a figure** | Concept | **P0** |
| 4 | What is included and excluded | Concept | **P0** |
| 5 | When the data was last refreshed | Concept | **P0** |
| 6 | Why a number changed after you looked at it | Concept | P1 |
| 7 | Rounding, currency and units | Concept | P1 |
| 8 | Estimates, actuals and forecasts | Concept | P1 |
| 9 | A number looks wrong — what to check first | Troubleshooting | P1 |

### Block B — Using the dashboards *(7 articles)*

Find your dashboard · filter and date ranges · **drill from a summary to the detail** · compare
periods · save a view · share a view · print and export. **2 at P0, 3 at P1, 2 at P2.**

### Block C — Self-service analysis *(6 articles)*

Build a simple report · choose the right dimension · **the joins that will mislead you** ·
performance and query limits · save and reuse · when to ask BI instead. **1 at P0, 3 at P1,
2 at P2.**

### Block D — Access, security and distribution *(6 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 23 | **Why you can see some data and not other data** *(row-level security)* | Concept | **P0** |
| 24 | Your scope — branch, region, account, brand | Concept | **P0** |
| 25 | Subscribe to a report | Task | P1 |
| 26 | Schedule and distribute | Task | P1 |
| 27 | **Sharing a report outside your scope** | Concept | **P0** |
| 28 | Request access to more data | Task | P1 |

**Set total: 28 articles · 12 at P0 · 12 at P1 · 4 at P2 · 0 at P3.**

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Managers across 51+ branches read the same number the same way | **Metric-definition disputes** | Approaching zero |
| Numbers presented to the board are defensible | Board-pack corrections | Approaching zero |
| BI is asked for analysis, not for explanations | BI request mix — explanation vs analysis | Shifting to analysis |
| Row-level security is understood, not worked around | Access requests citing "I can't see X" | Falling |

**`PS-16`: articles 1, 2 and 23 carry this set.** *What does this mean*, *why do two reports
disagree*, and *why can't I see that* are the three questions that consume BI time and produce
wrong decisions. Article 2 in particular prevents the most damaging outcome: two people arguing
from two correct numbers.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Metric disputes continue | Definitions live in help rather than in `RP-001` | **`PS-15` breached** — withdraw the restatement, link instead |
| BI overwhelmed by explanation requests | Article 1 not discoverable at the point of the number | `HC-016` contextual entry from the metric itself |
| People export to spreadsheets and recompute | They do not trust the number, or cannot get the cut they need | Block C; and treat it as a product signal |
| Data shared outside scope | Article 27 absent or unread | **Security matter — `M29`, not a help matter** |
| Numbers quoted without an as-at date | Article 3 not applied | Consider making the as-at date non-dismissible in `UI-016` |

---

## Related

`UI-016` · `RP-001` · `RP-002` · [`HC-006_Help_Set_P04_Corporate_B2B_Portal.md`](HC-006_Help_Set_P04_Corporate_B2B_Portal.md) — corporate users reach analytics through `P04` ·
[`HC-010_Help_Set_P08_Brand_Partner_Portal.md`](HC-010_Help_Set_P08_Brand_Partner_Portal.md) — brand partners see scoped analytics ·
[`../../08_Training_and_Enablement/08B_Course_Packs/TR-011_Course_Pack_Branch_Manager.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-011_Course_Pack_Branch_Manager.md) — module 2 teaches the metric dictionary ·
[`../HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md`](../HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) — the metric tooltip is the primary entry path.

---

## Feedback

Helpfulness per `CG-014`, plus **metric-dispute tracking**: every disagreement about a number is
logged with whether a definition existed and was reachable from the number itself.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Articles required | **28** · written **0** |
| Effort | 28 × 2–4 h = **55–110 hours**, higher per article because each needs BI verification |
| Sequencing | Articles 1, 2, 23 (`PS-16`), then 12 P0 before W4 |
| **Dependency** | **Article 1 is a pattern, not one article** — it is the presentation layer over `RP-001`, and it cannot be authored before `RP-001` exists |
| Bengali | Both; English may be primary (`HS-30`) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`RP-001` KPI Dictionary is unwritten** (Category 14 unstarted). **This set has no substance without it** — `PS-15` forbids defining metrics here, so Block A is a set of links to nothing | BI Lead | **W4 — blocking the entire set** |
| **O-02** | `RP-002` report catalogue is unwritten; Block B cannot name reports | BI Lead | W4 |
| **O-03** | **Whether a metric definition can be surfaced from the number itself** (`HC-016` tooltip → `RP-001`) is a product question that determines whether article 1 is read at all | CTO with BI Lead | **W4** |
| **O-04** | Row-level security scopes (articles 23, 24) depend on `05-04` and `M29` configuration that is not yet defined per report | Security Lead with BI Lead | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] **The audience recorded as a mode rather than a twelfth audience (`HC-001` `IA-01`)**
- [x] The Concept-over-Task inversion stated and explained (`PS-14`)
- [x] **Metric definitions kept in `RP-001` and never restated here (`PS-15`, `IA-12`, `CP-01`)**
- [x] 28 articles enumerated with type and priority
- [x] The three articles carrying the set identified (`PS-16`)
- [x] Row-level security treated as a concept to be understood, with breach routed to security
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `RP-001` — outstanding; the set has no substance without it**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and BI Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
