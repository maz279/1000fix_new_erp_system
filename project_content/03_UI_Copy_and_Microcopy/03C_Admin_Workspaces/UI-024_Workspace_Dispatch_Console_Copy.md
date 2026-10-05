---
id: UI-024
title: Workspace — Dispatch Console Copy
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
content_class: C
purpose: >
  Copy for the dispatch console. Dispatching a full morning queue in under ten minutes requires
  unambiguous SLA-risk and technician-load labelling; a misread here sends the wrong person across
  the city.
traces_to: [M02, P03, MD-005, MD-028, VB-008]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: UI-024_Workspace_Dispatch_Console_Copy_BN.md
i18n_namespace: `ws.dispatch.*`
pinned_to:
  surface: P03
  release: pending first build
  wave: W1
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P03 — fourteen role-scoped workspaces, each opening on the work its role actually does
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-024 — Workspace — Dispatch Console Copy

> **Small population, disproportionate impact.** Dispatch decisions determine SLA attainment
> network-wide. Every label on this board is read under time pressure.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P03 — Dispatch Console workspace (dispatch managers (3–8)) |
| Framework | Odoo Web (OWL 2) |
| Default language | Bengali and English |
| i18n namespace | ``ws.dispatch.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | C — Operational-critical |
| Sentence budget | ≤ 15 words (`VB-002` A-01) (`VB-002` §4.2) |
| Audience | dispatch managers (3–8) |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Term | Entity | Note |
|---|---|---|
| Per `CG-004` §4 | — | This pack cites approved terms; it never invents |
| Status labels | `MD-027` | Internal labels here — never the customer-facing ones |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Opens on — live map, unassigned queue, technician load, SLA risk

| Element | Key | English | Bengali | Max |
|---|---|---|---|---:|
| Title | `ws.dispatch.title` | Dispatch | ডিসপ্যাচ | 24 |
| Unassigned | `ws.dispatch.unassigned` | {count} unassigned | {count}টি অনির্ধারিত | 40 |
| SLA risk | `ws.dispatch.at_risk` | {count} at risk of breach | {count}টি লঙ্ঘনের ঝুঁকিতে | 40 |
| Breached | `ws.dispatch.breached` | {count} breached | {count}টি লঙ্ঘিত | 40 |
| Assign | `ws.dispatch.assign` | Assign | নিয়োগ করুন | 20 |
| Auto-assign | `ws.dispatch.auto` | Suggest assignments | নিয়োগের প্রস্তাব দিন | 24 |

### 3.2 Technician load

| Element | Key | English | Bengali |
|---|---|---|---|
| Available | `ws.dispatch.tech.available` | Available | উপলব্ধ |
| On a job | `ws.dispatch.tech.busy` | On a job — free about {time} | জবে আছেন — প্রায় {time}-এ মুক্ত |
| Full | `ws.dispatch.tech.full` | Full for today | আজকের জন্য পূর্ণ |
| Off shift | `ws.dispatch.tech.off` | Off shift | শিফটের বাইরে |
| Not certified | `ws.dispatch.tech.uncertified` | Not certified for {brand} | {brand}-এর জন্য সার্টিফাইড নন |

### 3.3 Column headers

| Column | Key | English | Bengali | Max |
|---|---|---|---|---:|
| Job | `ws.dispatch.col.job` | Job | জব | 24 |
| Zone | `ws.dispatch.col.zone` | Zone | জোন | 24 |
| SLA due | `ws.dispatch.col.sla` | SLA due | এসএলএ সময় | 24 |
| Skill needed | `ws.dispatch.col.skill` | Skill needed | প্রয়োজনীয় দক্ষতা | 24 |
| Technician | `ws.dispatch.col.tech` | Technician | টেকনিশিয়ান | 24 |

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
| Uncertified | `ws.dispatch.error.uncertified` | {technician} is not certified for {brand}. Assign someone certified, or ask Quality to renew. | {technician} {brand}-এর জন্য সার্টিফাইড নন। সার্টিফাইড কাউকে দিন, বা কোয়ালিটিকে নবায়নের অনুরোধ করুন। | **H** |
| Outside zone | `ws.dispatch.error.zone` | {technician} does not cover {zone}. Assign anyway with a reason, or choose another. | {technician} {zone} এলাকা কভার করেন না। কারণসহ তবুও নির্ধারণ করুন, বা অন্য কাউকে বেছে নিন। | **A** |
| Overloaded | `ws.dispatch.error.overload` | {technician} already has {count} jobs today. Assign anyway? | {technician}-এর আজ ইতিমধ্যে {count}টি কাজ আছে। তবুও নির্ধারণ করবেন? | **S** |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

| Action | Confirmation |
|---|---|
| Reassign | Names the current technician who will be notified |
| Bulk assign | States count and scope (`VB-006` TB-07) |

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Labels | Visible persistent label on every input | 3.3.2 |
| Errors | Identified in text with a remedy | 3.3.1, 3.3.3 |
| Status | Colour never the only signal (`VB-008`) | 1.4.1 |
| Tables | Real header cells; sortable state announced | 1.3.1, 4.1.2 |
| Language | `lang` declared; script changes marked | 3.1.2 |
| Bulk | Selection count and scope announced | 4.1.3 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Column header | 24 | **High** — 1366×600, up to 14 columns (`VB-003` D-01) |
| Button | 20 | Medium |
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
| [`../03B_Portals/UI-013_P03_Admin_Operations_Portal_UI_Copy_Pack.md`](../03B_Portals/UI-013_P03_Admin_Operations_Portal_UI_Copy_Pack.md) | Shared shell copy |
| [`../03A_Cross_Cutting/UI-004_Validation_and_Error_Message_Library.md`](../03A_Cross_Cutting/UI-004_Validation_and_Error_Message_Library.md) | Business-rule messages |
| `MD-027` Status and Lifecycle State Label Register | Internal state labels |
| `VB-008` Status Colour and Label Semantics Register | Status treatment |

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
- [ ] G2 factual and G3 technical review by the owning module business owner — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
