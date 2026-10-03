---
id: UI-016
title: P06 Analytics and Executive Dashboard Copy Pack
project: 1000FiX ERP System v2.0
content_type: UI copy pack
template: TPL_UI_Copy_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design
reviewers: [Localisation Lead, Design System, Accessibility reviewer, owning business function]
approver: Content Design Lead
content_class: D
purpose: >
  Metric names, filter labels, drill-path labels and definitional tooltips. An imprecise metric name
  produces a confidently wrong decision, and P06 commits management to making 100% of decisions on
  live data rather than compiled spreadsheets.
traces_to: [P06, UI-001, UI-003, UI-004, MD-027, VB-002]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: UI-016_P06_Analytics_and_Executive_Dashboard_Copy_Pack_BN.md
i18n_namespace: `p06.*`
pinned_to:
  surface: P06
  release: pending first build
  wave: W4
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview and the per-portal capability sets
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-016 — P06 Analytics and Executive Dashboard Copy Pack

> **A metric name that is imprecise produces a confidently wrong decision** (`VB-002` X-01).
> Every metric name here comes from `RP-001`; this pack cites, it never invents.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P06 — executives, directors, branch and functional managers (25–60) |
| Framework | Metabase + Grafana (embedded) |
| Default language | English |
| i18n namespace | ``p06.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 15 words (`VB-002` X-01) (`VB-002` §4.2) |
| Audience | executives, directors, branch and functional managers (25–60) |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Term | Entity | Note |
|---|---|---|
| Per `CG-004` §4 | — | This pack cites approved terms; it never invents |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Metric labels — `p06.metric.*`

All names are cited from `RP-001`. Every one is one click from its definition.

| Metric | Key | Label EN | Tooltip (definition summary) |
|---|---|---|---|
| Turnaround time | `p06.metric.tat` | Turnaround time | Intake to release, business hours, per `MD-028` calendar |
| First-time fix | `p06.metric.ftf` | First-time fix | Resolved without a second visit or return |
| Rework rate | `p06.metric.rework` | Rework rate | Repeat order, same device and fault, within 30 days (`BRU-SRM-06`) |
| SLA attainment | `p06.metric.sla` | SLA attainment | Within target, clock paused per `MD-028` |
| Revenue by stream | `p06.metric.revenue_bl` | Revenue by business line | One of the fourteen (`MD-036`) |
| Utilisation | `p06.metric.utilisation` | Technician utilisation | Productive minutes ÷ available minutes |

### 3.2 Qualifiers — `p06.qualifier.*`

| Situation | Key | Label EN |
|---|---|---|
| Partial period | `p06.qualifier.partial` | Partial period — {days} of {total} days |
| Small denominator | `p06.qualifier.small_n` | Based on {n} records — treat with caution |
| Definition changed | `p06.qualifier.changed` | Definition changed on {date}; earlier periods are not comparable |
| Provisional | `p06.qualifier.provisional` | Provisional — {reason} |

> **Qualifiers appear on the tile, not in a footnote** (`VB-002` X-03).

### 3.3 Drill and filter — `p06.nav.*`

| Element | Key | English |
|---|---|---|
| Drill down | `p06.nav.drill` | View {level} |
| Back up | `p06.nav.up` | Back to {level} |
| Compare | `p06.nav.compare` | Compare with {period} |
| Branch league | `p06.nav.league` | Branch league table |

---

## 4. Field labels and help text

Shared field copy is `UI-003`.

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

| Trigger | Key | Message EN | Class |
|---|---|---|:--:|
| No data | `p06.error.no_data` | No data for {filter}. Try a wider period or a different branch. | **S** |
| Out of scope | `p06.error.scope` | You can see {your_scope}. This view needs a wider scope. | **H** |
| Stale | `p06.error.stale_data` | Data last refreshed {time}. The pipeline is catching up. | **S** |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Labels | Every input has a visible persistent label | 3.3.2 |
| Errors | Identified in text, with a remedy | 3.3.1, 3.3.3 |
| Status | Colour is never the only signal (`VB-008`) | 1.4.1 |
| Language | `lang` declared; script changes marked | 3.1.1, 3.1.2 |
| Accessible names | From `UI-010`, translated | 1.1.1, 4.1.2 |
| Tables | Real header cells; data not layout | 1.3.1 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Button | 20 | Medium — Bengali verbs run long |
| Column header | 24 | **High** at 1366×600 density |
| Field label | 36 | Medium |
| Alert body | 200 | Low |

> Exceeding a budget is a **design conversation**, not a copy problem to solve by abbreviating
> (`VB-006` §8). Where the Bengali cannot fit, the control goes two-line before it goes
> icon-only (`VB-007` §7.3).

---

## 9. Open questions for design or product

| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | `BN-003` not written; Bengali indicative | **Yes** | Localisation Lead |
| 2 | No build exists; `pinned_to` incomplete | **Yes** | Platform Engineering |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| `RP-001` KPI Dictionary and Metric Definition Standard | **The authority for every metric name** |
| `RP-007` Chart, Label and Visualisation Standard | Chart labelling |
| `RP-011` Branch League Table Definition | Scoring rules |

---

## 11. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:` and `i18n_namespace:`
- [x] Conforms to `TPL_UI_Copy_Pack.md`
- [x] Every string has an i18n key conforming to `UI-001` (`CG-008` UI-a)
- [x] No string concatenated across a translatable boundary (`CG-003` S-05, `BN-005`)
- [x] Every error message follows the three-part structure and states a remedy (`CG-008` UI-c)
- [x] Error messages expose no internal detail (`CG-008` UI-d)
- [x] Message class matches the `05-05` rule class — H blocks, A names the authoriser, S warns
- [x] Empty, loading and offline states covered, not only the happy path (`CG-008` UI-f)
- [x] Destructive actions state the consequence; buttons are verbs, not OK/Cancel (`CG-008` UI-g)
- [x] Character budget recorded per slot, with Bengali expansion assessed (`CG-008` UI-h)
- [x] Status labels come from `MD-027`, not invented locally (`CG-008` UI-i, `T-06`)
- [x] Accessibility text authored here, not left to the implementer (`CG-011` AT-01)
- [x] All internal links resolve
- [ ] Bengali counterpart written and signed off **in context** (`BN-018`) — **outstanding; blocks `Approved`** (`CM-R6`)
- [ ] `BN-003` terminology confirmed — **outstanding; §2 indicative until then**
- [ ] Pinned to a release and verified against the build (`CG-008` UI-j) — **outstanding; no build yet**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
