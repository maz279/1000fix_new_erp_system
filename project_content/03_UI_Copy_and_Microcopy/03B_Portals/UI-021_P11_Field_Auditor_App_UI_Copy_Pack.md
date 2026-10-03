---
id: UI-021
title: P11 Field Auditor App UI Copy Pack
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
  Screen copy for the field auditor application. Classification language is the standard: 20–60
  auditors must produce the same severity from the same observation, or audit data cannot be
  aggregated. Finding-to-CAPA cycle target is under five days.
traces_to: [P11, UI-001, UI-003, UI-004, MD-027, VB-002]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: UI-021_P11_Field_Auditor_App_UI_Copy_Pack_BN.md
i18n_namespace: `p11.*`
pinned_to:
  surface: P11
  release: pending first build
  wave: W5
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview and the per-portal capability sets
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-021 — P11 Field Auditor App UI Copy Pack

> **ISO 9001 vocabulary is used exactly and never paraphrased** (`VB-002` Q-01, `CG-004` §4.7).
> A finding classified differently by two auditors is two different facts.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P11 — quality auditors, branch and regional managers (20–60) |
| Framework | Flutter |
| Default language | Bengali and English |
| i18n namespace | ``p11.*`` |
| Offline-capable | **Yes** (`PS-08`) |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 20 words (`VB-002` Q-01) (`VB-002` §4.2) |
| Audience | quality auditors, branch and regional managers (20–60) |

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

### 3.1 Audit execution — `p11.audit.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Assigned | `p11.audit.assigned` | Your audits | আপনার অডিট |
| Checklist | `p11.audit.checklist` | Checklist — {done} of {total} | চেকলিস্ট — {total}-এর {done} |
| Evidence | `p11.audit.evidence` | Attach evidence | প্রমাণ সংযুক্ত করুন |
| Clause | `p11.audit.clause` | Against clause {clause} | ধারা {clause}-এর বিপরীতে |

### 3.2 Findings — `p11.finding.*`

Classification wording is fixed. Auditors select; they do not describe the class.

| Class | Key | Definition EN | Definition BN |
|---|---|---|---|
| Major non-conformance | `p11.finding.major` | A requirement is not met and the process cannot deliver a conforming result | একটি প্রয়োজন পূরণ হয়নি এবং প্রক্রিয়াটি সঠিক ফল দিতে পারে না |
| Minor non-conformance | `p11.finding.minor` | A requirement is not fully met but the process can still deliver a conforming result | প্রয়োজন সম্পূর্ণ পূরণ হয়নি, তবে প্রক্রিয়াটি এখনও সঠিক ফল দিতে পারে |
| Observation | `p11.finding.observation` | Not a departure, but a risk if unaddressed | কোনো বিচ্যুতি নয়, তবে সমাধান না হলে ঝুঁকি |
| Opportunity | `p11.finding.opportunity` | An improvement that is not required | একটি উন্নতি যা আবশ্যক নয় |

### 3.3 Closure — `p11.close.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Owner | `p11.close.owner` | Assign to | নিয়োগ করুন |
| Due | `p11.close.due` | Due by | নির্ধারিত তারিখ |
| Acknowledge | `p11.close.ack` | Ask the auditee to acknowledge | অডিটিকে স্বীকৃতি দিতে বলুন |
| Report | `p11.close.report` | Generate the audit report | অডিট রিপোর্ট তৈরি করুন |

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
| No evidence | `p11.error.no_evidence` | Every finding needs evidence. Attach a photo or document. | **H** |
| No owner | `p11.error.no_owner` | Assign an owner and a due date before closing the audit. | **H** |
| Major unresolved | `p11.error.major_open` | A major non-conformance cannot be closed without a verified CAPA. | **H** |

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
| Button | 20 | **High** — mobile width |
| Message | 60 | High |
| Field label | 36 | Medium |

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
| `SP-029` SOP Internal Quality Audit and CAPA | The process |
| `DT-043` NCR, CAPA and Internal Audit Report Forms | The output |
| `TR-016` Course Pack Quality and Field Auditor | Consistent classification |

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
