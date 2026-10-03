---
id: UI-001
title: UI String Architecture and i18n Key Standard
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
reviewers: [Platform Engineering, Localisation Lead, Design System, all portal owners]
approver: Content Design Lead
content_class: D
purpose: >
  Defines key naming, namespacing, placeholder and plural rules, string reuse policy and the
  extraction pipeline. Five frameworks with no shared key standard means the same string is
  translated five times and drifts four ways.
traces_to: [M65, PS-03, PS-06, BN-005, CG-003 S-05, VB-006 DS-03]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: UI-001_UI_String_Architecture_and_i18n_Key_Standard_BN.md
i18n_namespace: (defines the namespace scheme itself)
pinned_to:
  surface: All twelve portals
  release: pending first build
  wave: W1
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-03, PS-06
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 localisation standards — UTF-8, ICU bn-BD collation
    verified: 2026-08-15
    class: P1
  - source: i18n industry practice — semantic nested keys, ICU MessageFormat for plurals and gender, namespace-per-feature loading
    verified: 2026-08-15
    class: P3
supersedes: none
review_due: 2027-02-15
---

# UI-001 — UI String Architecture and i18n Key Standard

> **The key is the contract between the developer, the translator and the tester.** A bad key
> scheme cannot be fixed later without re-extracting every string in the product.
>
> This file is authored **before** any portal copy pack, because all 41 other `UI` files use it.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Every user-visible string in the system |
| Framework | All — Odoo OWL, Next.js, React Native, Flutter |
| Default language | Bengali default on customer and field surfaces (`PS-03`) |
| i18n namespace | `(defines the namespace scheme itself)` |
| Offline-capable | Applies to `P02`, `P09`, `P11` (`PS-08`) |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | Per surface — see `VB-002` §4.2 (`VB-002` §4.2) |
| Audience | All surfaces |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Concept | Approved term | Note |
|---|---|---|
| A translatable unit | **string** | Not "label", "text" or "message" generically |
| Its identifier | **key** | Never "id" — `id` is a record identifier |
| A grouping of keys | **namespace** | Loaded as a unit |
| A substituted value | **placeholder** | Never "variable" or "token" in copy contexts |
| The Bengali file | **string bundle** | `BN-009`…`BN-013` |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Key format

```
<surface>.<area>.<component>.<element>[.<state>]
```

| Segment | Rule | Example |
|---|---|---|
| `surface` | Portal or shared scope: `p01`…`p12`, `ws` (admin workspace), `common` | `p01` |
| `area` | Functional area within the surface | `booking` |
| `component` | The screen, dialog or component | `step_device` |
| `element` | The slot | `title`, `cta_primary`, `help` |
| `state` | Optional — the variant | `empty`, `loading`, `error` |

**Examples**

| Key | What it names |
|---|---|
| `p01.booking.step_device.title` | Screen title |
| `p01.booking.step_device.cta_primary` | Primary button |
| `p01.booking.step_device.list.empty` | Empty state |
| `common.error.field.imei_format` | Shared validation message |
| `ws.dispatch.board.column.sla_risk` | Admin workspace column header |
| `p02.job.parts.scan.help` | Technician app field help |

### 3.2 Rules

| # | Rule |
|---|---|
| **K-01** | Keys are **semantic, never the source text.** `common.error.field.imei_format`, never `Enter_the_IMEI_as_15_digits` — the English changes and the key must not |
| **K-02** | Lower snake_case throughout. No camelCase, no hyphens, no Bengali script |
| **K-03** | Maximum five segments. A sixth means the component is doing too much |
| **K-04** | `common.*` is for strings used on **three or more** surfaces. Two surfaces duplicate; three share |
| **K-05** | A key is **permanent**. Changing the English does not change the key; changing the meaning requires a new key and retirement of the old (`CG-005` `ID-03` applied to strings) |
| **K-06** | Namespaces load on demand. A portal never loads another portal's namespace |
| **K-07** | No key is defined in code. Keys are declared in the pack, then implemented (`VB-006` `DS-02`, `DS-03`) |

### 3.3 Namespace allocation

| Namespace | Owner | Pack |
|---|---|---|
| `common.*` | Content Design Lead | `UI-002`…`UI-010` |
| `p01.*` … `p12.*` | Portal owner | `UI-011`…`UI-022` |
| `ws.*` | Content Design Lead | `UI-023`…`UI-036` |
| `flow.*` | Content Design Lead | `UI-037`…`UI-042` |

> A string that appears in both a portal and a flow lives in `flow.*` and the portal references
> it. One canonical wording per fact (`CG-003` §10 X-01).

---

## 4. Field labels and help text

Not applicable — this file defines the standard rather than carrying field copy. The field
label library is `UI-003`.

### 4.1 Placeholder syntax

ICU MessageFormat. Named placeholders only; positional placeholders are prohibited because
Bengali word order differs from English.

```
{count, plural, one {# part} other {# parts}}
{name} approved the estimate on {date, date, medium}
{amount, number, ::currency/BDT}
```

| # | Rule |
|---|---|
| **P-01** | Named placeholders only. `{customer_name}`, never `{0}` |
| **P-02** | Every placeholder is documented in the pack with its source field and an example value |
| **P-03** | **No concatenation across a translatable boundary** (`CG-003` S-05). `"You have " + n + " items"` is prohibited; author the whole sentence per plural form |
| **P-04** | Dates, numbers and currency use ICU formatters, never pre-formatted strings — the locale decides (`BN-007`) |
| **P-05** | A placeholder that could contain user input is escaped at render, and the pack states so |

### 4.2 Plural rules

Bengali (`bn`) uses CLDR categories **`one`** and **`other`**. English uses the same two. Both
are declared explicitly; neither relies on a default.

```json
"common.parts.count": "{n, plural, one {# part} other {# parts}}"
```

| # | Rule |
|---|---|
| **PL-01** | Every count-bearing string uses ICU plural, even where English needs only one form |
| **PL-02** | Zero is authored explicitly where the wording differs — `=0 {No parts}` |
| **PL-03** | Never build a plural by appending "(s)" |

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

| Trigger | Key | Message EN | Remedy stated? | Rule ID |
|---|---|---|:--:|---|
| Key not found at render | `common.error.system.string_missing` | This text could not be loaded. Refresh the page. If it happens again, quote reference {ref}. | ✔ | — |
| Placeholder unresolved | — | **Build failure, never a runtime message.** An unresolved placeholder must fail CI | n/a | `K-07` |

---

## 6. Confirmations and destructive actions

Not applicable — this file carries no user-facing destructive actions.

---

## 7. Accessibility text

| Item | Rule |
|---|---|
| Accessible names are strings | They carry keys and are translated like any other string (`CG-011` BA-04, `CG-010` §5) |
| Namespace | `common.a11y.*` for shared; `<surface>.a11y.*` for surface-specific |
| Language marking | Every string bundle declares its `lang`; mixed-script strings mark the change (`CG-011` BA-02, `VB-009` MX-04) |
| Screen-reader-only text | Authored in `UI-010`, keyed the same way |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Constraint | Rule |
|---|---|
| Budgets live with the component | `VB-006` §8 is the authority; each pack records the slot budget it uses |
| Measurement | **Bengali rendered width**, not character count (`VB-007` §7.1) |
| Enforcement | Automated per commit against the Bengali bundle (`CG-008` §6) |
| Overflow | Two-line before icon-only; never truncate a label (`VB-007` BL-04) |

> Exceeding a budget is a **design conversation**, not a copy problem to solve by abbreviating
> (`VB-006` §8). Where the Bengali cannot fit, the control goes two-line before it goes
> icon-only (`VB-007` §7.3).

---

## 9. Open questions for design or product

| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | Does Odoo OWL support ICU MessageFormat natively, or is an adapter needed? | **Yes** — `p03`, `ws.*` | Platform Engineering |
| 2 | Is the extraction pipeline one tool across five frameworks, or per framework with a shared bundle format? | **Yes** — all packs | Platform Engineering |
| 3 | Do Flutter surfaces (`P02`, `P09`, `P11`) bundle strings at build or fetch at runtime? Offline requires bundling | **Yes** — `UI-009` | Mobile Engineering |
| 4 | Bengali numerals in placeholders — does the ICU number formatter follow the `BN-007` decision? | Yes | Localisation Lead |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| [`UI-002_Global_Navigation_and_Label_Register.md`](UI-002_Global_Navigation_and_Label_Register.md) | First consumer of the scheme |
| [`UI-004_Validation_and_Error_Message_Library.md`](UI-004_Validation_and_Error_Message_Library.md) | `common.error.*` namespace |
| `BN-005` i18n Key, Placeholder and Pluralisation Rules | The localisation-owned counterpart; ratified together |
| `VB-006` Design System Content Standards | `DS-02`, `DS-03` component binding |
| `CG-003` §S-05 | The concatenation prohibition |

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
