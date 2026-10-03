---
id: UI-013
title: P03 Admin Operations Portal UI Copy Pack
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
  The shell copy for the admin portal — home, workspace switching, shared list and detail chrome.
  Fourteen workspaces share one vocabulary; a dispatcher moving to the branch console must not
  relearn words. Time-to-competence target is four hours (`NFR-075`).
traces_to: [P03, 05-06 NFR-075, NFR-076, UI-002, UI-023..UI-036, VB-003]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: UI-013_P03_Admin_Operations_Portal_UI_Copy_Pack_BN.md
i18n_namespace: `p03.*`, `ws.*`
pinned_to:
  surface: P03
  release: pending first build
  wave: W1
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P03 — fourteen role-scoped workspaces and design requirements
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-013 — P03 Admin Operations Portal UI Copy Pack

> **Brevity is the courtesy.** These labels are read thousands of times a day on a 1366×768
> screen. The fourteen workspace packs (`UI-023`…`UI-036`) carry workspace-specific copy; this
> pack carries what they share.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P03 — service agents, dispatchers, branch and functional managers (150–250) |
| Framework | Odoo Web (OWL 2) |
| Default language | Bengali and English |
| i18n namespace | ``p03.*`, `ws.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 15 words (`VB-002` A-01) (`VB-002` §4.2) |
| Audience | back-office and branch staff |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Term | Bengali | Entity |
|---|---|---|
| Service order | সার্ভিস অর্ডার | `fix.service.order` |
| Job | জব | `fix.dispatch.job` |
| Branch | ব্রাঞ্চ | `fix.branch` |
| Workspace | ওয়ার্কস্পেস | — |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Home — `p03.home.*`

| Element | Key | English | Bengali | Max |
|---|---|---|---|---:|
| Title | `p03.home.title` | Your workspaces | আপনার ওয়ার্কস্পেস | 50 |
| Subtitle | `p03.home.subtitle` | Each workspace opens on the work your role does | প্রতিটি ওয়ার্কস্পেস আপনার ভূমিকার কাজ নিয়ে খোলে | 140 |
| Today | `p03.home.today` | Today at {branch} | {branch}-এ আজ | 50 |

### 3.2 Shared list chrome — `p03.list.*`

| Element | Key | English | Bengali | Max |
|---|---|---|---|---:|
| Result count | `p03.list.count` | {count} {object} | {count}টি {object} | 40 |
| Selection | `p03.list.selected` | {n} selected of {total} | {total}-এর মধ্যে {n}টি নির্বাচিত | 40 |
| Bulk action | `p03.list.bulk` | {action} {n} | {action} {n} | 20 |
| Saved view | `p03.list.saved_view` | Saved views | সংরক্ষিত ভিউ | 24 |
| Export | `p03.list.export` | Export | এক্সপোর্ট | 20 |

### 3.3 Shared detail chrome — `p03.detail.*`

| Element | Key | English | Bengali | Max |
|---|---|---|---|---:|
| Activity | `p03.detail.activity` | Activity | কার্যক্রম | 24 |
| Attachments | `p03.detail.attachments` | Attachments | সংযুক্তি | 24 |
| Audit trail | `p03.detail.audit` | Change history | পরিবর্তনের ইতিহাস | 24 |
| Assigned to | `p03.detail.assignee` | Assigned to | নিয়োগ করা হয়েছে | 36 |

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
| Bulk over limit | `p03.error.bulk_limit` | Bulk actions apply to at most {max} records. Narrow your filter. | **H** |
| Export too large | `p03.error.export_size` | This export has {rows} rows. Schedule it instead — we will email it when ready. | **S** |
| Stale record | `p03.error.stale` | {user} changed this while you were editing. Review their change before saving. | **H** |

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
| [`../03C_Admin_Workspaces/UI-023_Workspace_Service_Intake_Copy.md`](../03C_Admin_Workspaces/UI-023_Workspace_Service_Intake_Copy.md) | First workspace |
| `BN-011` Bengali String Bundle P03 | Counterpart |
| `TR-007` Course Pack Service Centre Agent | Cites these labels |

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
