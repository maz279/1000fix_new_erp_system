---
id: UI-010
title: Accessibility Text Library
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
reviewers: [Accessibility reviewer, Localisation Lead, Design System]
approver: Content Design Lead
content_class: D
purpose: >
  Alt text, ARIA labels, live-region announcements, focus-order narration and screen-reader-only
  text, with Bengali equivalents. WCAG 2.1 AA is contractual under PS-04 and NFR-073; assistive
  technology text is content and must be authored, never generated.
traces_to: [PS-04, 05-06 NFR-073, CG-011, VB-007 §8, TS-016]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: UI-010_Accessibility_Text_Library_BN.md
i18n_namespace: `common.a11y.*`
pinned_to:
  surface: All surfaces
  release: pending first build
  wave: W1
sources:
  - source: W3C WCAG 2.1 SC 1.1.1, 2.4.4, 2.4.6, 3.1.2, 4.1.2, 4.1.3
    verified: 2026-08-15
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011 §4 and §8
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-010 — Accessibility Text Library

> **Accessible names are strings.** They carry keys, they are translated, and they are budgeted
> like any other string (`CG-010` §5, `CG-011` BA-04). They are not a developer detail.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Alt text, ARIA labels, live-region announcements, screen-reader-only text |
| Framework | All |
| Default language | Bilingual — accessible names are user-visible strings (`CG-010` §5) |
| i18n namespace | ``common.a11y.*`` |
| Offline-capable | Bundled with the offline pack on `P02`, `P09`, `P11` |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | Concise; announced aloud (`VB-002` §4.2) |
| Audience | Assistive technology users on every surface |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Concept | Term | Never |
|---|---|---|
| Text alternative | **alt text** | alt tag |
| Programmatic name | **accessible name** | ARIA label (that is one mechanism) |
| Hidden but announced | **screen-reader text** | sr-only, visually hidden |
| Dynamic announcement | **live region** | toast (that is a component) |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Icon-only controls — `common.a11y.icon.*`

The fifteen registered icon-only controls (`VB-007` §5). Every one names the action **and its
object**.

| Control | Key | Accessible name EN | BN |
|---|---|---|---|
| Close | `common.a11y.icon.close` | Close | বন্ধ করুন |
| Search | `common.a11y.icon.search` | Search {scope} | {scope} অনুসন্ধান করুন |
| More actions | `common.a11y.icon.more` | More actions for {object} | {object}-এর আরও ক্রিয়া |
| Sort | `common.a11y.icon.sort` | Sort by {column}, currently {direction} | {column} অনুসারে সাজান, বর্তমানে {direction} |
| Expand row | `common.a11y.icon.expand` | Expand {object} | {object} প্রসারিত করুন |
| Next page | `common.a11y.icon.next` | Next page, {n} of {total} | পরের পাতা, {total}-এর {n} |
| Help | `common.a11y.icon.help` | Help for {field} | {field}-এর সহায়তা |
| Copy | `common.a11y.icon.copy` | Copy {value} | {value} কপি করুন |
| Refresh | `common.a11y.icon.refresh` | Refresh {object} | {object} রিফ্রেশ করুন |
| Filter | `common.a11y.icon.filter` | Filter, {n} applied | ফিল্টার, {n}টি প্রয়োগ করা হয়েছে |
| Scan | `common.a11y.icon.scan` | Scan barcode | বারকোড স্ক্যান করুন |
| Torch | `common.a11y.icon.torch` | Turn torch {on_off} | টর্চ {on_off} করুন |
| Call | `common.a11y.icon.call` | Call {name} | {name}-কে কল করুন |
| Navigate | `common.a11y.icon.navigate` | Navigate to {address} | {address}-এ যান |
| Fullscreen | `common.a11y.icon.fullscreen` | {enter_exit} fullscreen | ফুলস্ক্রিন {enter_exit} |

### 3.2 Live regions — `common.a11y.live.*`

| Event | Key | Announcement EN | Politeness |
|---|---|---|---|
| Record saved | `common.a11y.live.saved` | {object} saved | {object} সংরক্ষিত হয়েছে | polite |
| Validation failed | `common.a11y.live.invalid` | {count} fields need attention | {count}টি ফিল্ডে মনোযোগ দরকার | **assertive** |
| Status changed | `common.a11y.live.status` | {object} is now {status} | {object} এখন {status} | polite |
| Results updated | `common.a11y.live.results` | {count} results | {count}টি ফলাফল | polite |
| Sync state | `common.a11y.live.sync` | {sync_state} | সিঙ্ক অবস্থা: {sync_state} | polite |
| Session expiring | `common.a11y.live.session` | Session ends in {minutes} minutes | সেশন শেষ হবে {minutes} মিনিটে | **assertive** |

### 3.3 Screen-reader-only text — `common.a11y.sr.*`

| Purpose | Key | Text EN | BN |
|---|---|---|---|
| Skip link | `common.a11y.sr.skip` | Skip to main content | মূল বিষয়বস্তুতে যান |
| Table caption | `common.a11y.sr.table` | {object}, {rows} rows, sortable | {object}, {rows} সারি, সাজানো যায় |
| Required marker | `common.a11y.sr.required` | required | আবশ্যক |
| External link | `common.a11y.sr.external` | opens in a new tab | নতুন ট্যাবে খোলে |
| File link | `common.a11y.sr.file` | {format}, {size} | {format} ফরম্যাট, আকার {size} | {format}, {size} |
| Current page | `common.a11y.sr.current` | current page | বর্তমান পাতা |

### 3.4 Alt text patterns — `common.a11y.alt.*`

| Image type | Rule | Example |
|---|---|---|
| Decorative | Empty alt, marked decorative | — |
| Logo | Organisation name only | 1000FiX Services |
| Device photo at intake | Describe the **observable condition** | Laptop lid with a diagonal crack across the upper left |
| Repair evidence, before | Describe what the photo shows as evidence | Mainboard with visible burn mark near the power connector |
| Chart | Short alt plus a data table (`CG-011` AT-06) | Turnaround time by branch, twelve months. Data table follows. |
| Screenshot in help | What to see and where | The Create service order button, top right of the intake screen |

---

## 4. Field labels and help text

Field copy is `UI-003`; this pack adds only surface-specific fields where noted.

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

| # | Rule | SC |
|---|---|:--:|
| **A-01** | Every non-decorative image has a text alternative | 1.1.1 |
| **A-02** | Alt text does not begin "Image of" | — |
| **A-03** | Alt text is under 125 characters | `CG-011` AT-03 |
| **A-04** | Accessible names include the **object**, not just the action | 2.4.6 |
| **A-05** | Accessible names are translated | 3.1.2 |
| **A-06** | Errors are assertive; confirmations are polite | 4.1.3 |
| **A-07** | Screenshots use sample data, redacted (`MM-002`) | — |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

---

## 7. Accessibility text

This library **is** the accessibility text. Its own conformance is verified in `TS-016`.

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Accessible name | No visual budget — but **spoken length matters** | Medium — names with two placeholders are long to hear |
| Live announcement | Under 10 words | Medium |
| Alt text | 125 characters | Low |

> Exceeding a budget is a **design conversation**, not a copy problem to solve by abbreviating
> (`VB-006` §8). Where the Bengali cannot fit, the control goes two-line before it goes
> icon-only (`VB-007` §7.3).

---

## 9. Open questions for design or product

| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | `BN-003` is not written; Bengali here is indicative | **Yes** | Localisation Lead |
| 2 | No build exists, so `pinned_to` cannot be completed (`CG-006` §3) | **Yes** | Platform Engineering |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| [`../01_Voice_Brand_and_Design_Content/VB-007_Iconography_and_Label_Pairing_Register.md`](../../01_Voice_Brand_and_Design_Content/VB-007_Iconography_and_Label_Pairing_Register.md) | The fifteen icon-only controls |
| `CG-011` Accessibility Content Standard | The obligations |
| `TS-016` Accessibility Test Script Pack | Verification |
| `MM-002` Screenshot, Annotation and Redaction Standard | Screenshot alt text |

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
