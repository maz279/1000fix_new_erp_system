---
id: UI-002
title: Global Navigation and Label Register
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
reviewers: [Localisation Lead, Design System, all portal owners, Enterprise Architecture]
approver: Content Design Lead
content_class: D
purpose: >
  Every menu, tab, breadcrumb, section and page title across all surfaces, bilingual. Navigation
  labels are the vocabulary users learn first; inconsistency here undermines every training course
  and every help article that cites a label.
traces_to: [CG-004, PS-06, VB-006 §4.3, UI-001, TR-022, HC-002]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: UI-002_Global_Navigation_and_Label_Register_BN.md
i18n_namespace: `common.nav.*`
pinned_to:
  surface: All twelve portals
  release: pending first build
  wave: W1
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P03 — fourteen role-scoped workspaces
    verified: 2026-08-15
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-004 §4 controlled vocabulary
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-002 — Global Navigation and Label Register

> **Navigation labels are nouns; buttons are verbs** (`VB-006` `NV-01`). This register holds the
> nouns.
>
> Every help article and training slide cites these labels verbatim in bold (`CG-003` X-03). A
> label change is therefore a co-ordinated edit across `HC`, `TR` and `TS` content.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Menus, tabs, breadcrumbs, section and page titles across every surface |
| Framework | All — Odoo OWL, Next.js, React Native, Flutter |
| Default language | Bengali default on customer and field surfaces (`PS-03`) |
| i18n namespace | ``common.nav.*`` |
| Offline-capable | Applies to `P02`, `P09`, `P11` (`PS-08`) |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | Per surface — see `VB-002` §4.2 (`VB-002` §4.2) |
| Audience | All surfaces |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Navigation label | Names the object | Entity | Never |
|---|---|---|---|
| Service orders | `fix.service.order` | `M01` | Jobs, tickets, cases |
| Dispatch | `fix.dispatch.job` | `M02` | Assignments, routing |
| Workshop | `fix.work.order` | `M31` | Bench, lab |
| Devices | `fix.asset` | `M17` | Units, machines |
| Parts | `fix.part` | `M15` | Spares, components |
| Contracts | `fix.contract` | `M08` | Agreements, deals |
| Warranty | `fix.warranty.register` | `M09` | Guarantees |
| Customers | `fix.party` + role | `M33` | Clients, consumers |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### Global chrome — present on every surface — `common.nav.chrome`

| Element | Key | English | Bengali | Max | Notes |
|---|---|---|---|---:|---|
| Product name | `common.nav.chrome.product` | 1000FiX | 1000FiX | — | Never transliterated (`VB-009` BR-01) |
| Search | `common.nav.chrome.search` | Search | অনুসন্ধান | 24 | Placeholder states scope (`VB-006` SF-01) |
| Notifications | `common.nav.chrome.notifications` | Notifications | বিজ্ঞপ্তি | 24 |  |
| Help | `common.nav.chrome.help` | Help | সহায়তা | 24 | Opens `HC` for this surface |
| Language | `common.nav.chrome.language` | বাংলা / English | বাংলা / English | 24 | Always shows the **other** language |
| Account | `common.nav.chrome.account` | Account | অ্যাকাউন্ট | 24 |  |
| Sign out | `common.nav.chrome.signout` | Sign out | সাইন আউট | 24 | Never "Log out" (CG-004 4.8) |

### Admin workspace switcher — `P03` — `ws.nav.switcher`

| Element | Key | English | Bengali | Max | Notes |
|---|---|---|---|---:|---|
| Switcher label | `ws.nav.switcher.title` | Workspaces | ওয়ার্কস্পেস | 24 | One click from home (`P03` design requirement) |
| Service intake | `ws.nav.switcher.intake` | Service intake | সার্ভিস ইনটেক | 24 | → `UI-023` |
| Dispatch | `ws.nav.switcher.dispatch` | Dispatch | ডিসপ্যাচ | 24 | → `UI-024` |
| Branch | `ws.nav.switcher.branch` | Branch | ব্রাঞ্চ | 24 | → `UI-025` |
| Workshop | `ws.nav.switcher.workshop` | Workshop | ওয়ার্কশপ | 24 | → `UI-026` |
| Inventory | `ws.nav.switcher.inventory` | Inventory | ইনভেন্টরি | 24 | → `UI-027` |
| Procurement | `ws.nav.switcher.procurement` | Procurement | প্রকিউরমেন্ট | 24 | → `UI-028` |
| Finance | `ws.nav.switcher.finance` | Finance | ফাইন্যান্স | 24 | → `UI-029` |
| HR | `ws.nav.switcher.hr` | HR | এইচআর | 24 | → `UI-030` |
| Quality | `ws.nav.switcher.quality` | Quality | কোয়ালিটি | 24 | → `UI-031` |
| Contracts | `ws.nav.switcher.contracts` | Contracts | চুক্তি | 24 | → `UI-032` |
| Warranty | `ws.nav.switcher.warranty` | Warranty | ওয়ারেন্টি | 24 | → `UI-033` |
| Marketplace | `ws.nav.switcher.marketplace` | Marketplace | মার্কেটপ্লেস | 24 | → `UI-034` |
| Managed services | `ws.nav.switcher.msp` | Managed services | ম্যানেজড সার্ভিস | 24 | → `UI-035` |
| System | `ws.nav.switcher.system` | System | সিস্টেম | 24 | → `UI-036` |

### Customer portal primary navigation — `P01` — `p01.nav.primary`

| Element | Key | English | Bengali | Max | Notes |
|---|---|---|---|---:|---|
| Home | `p01.nav.primary.home` | Home | হোম | 24 |  |
| Book a service | `p01.nav.primary.book` | Book a service | সার্ভিস বুক করুন | 24 | Verb — the one nav exception, it is the primary action |
| My services | `p01.nav.primary.orders` | My services | আমার সার্ভিস | 24 | Customer term, not "service orders" (`CG-004` §5) |
| My devices | `p01.nav.primary.devices` | My devices | আমার ডিভাইস | 24 |  |
| Contracts | `p01.nav.primary.contracts` | My contracts | আমার চুক্তি | 24 |  |
| Shop | `p01.nav.primary.shop` | Shop | শপ | 24 |  |
| Support | `p01.nav.primary.support` | Support | সহায়তা | 24 |  |


---

## 4. Field labels and help text

Not applicable — navigation labels carry no fields. Field copy is `UI-003`.

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

| Trigger | Key | Message EN | Remedy stated? | Class |
|---|---|---|:--:|:--:|
| Workspace not permitted | `common.nav.error.no_access` | This workspace is not part of your role. Ask your manager if you need access to {workspace}. | ✔ | **H** |
| Surface unavailable | `common.nav.error.surface_down` | {surface} is unavailable. Other workspaces are working normally. We are restoring it. | ✔ | **S** |

---

## 6. Confirmations and destructive actions

Navigation carries no destructive actions. Sign-out confirmation is in `UI-005`.

---

## 7. Accessibility text

| Element | Accessible name EN | BN | Behaviour |
|---|---|---|---|
| Workspace switcher | Switch workspace, currently {workspace} | ওয়ার্কস্পেস পরিবর্তন, বর্তমানে {workspace} | Announces the current location (`CG-011` ST-02) |
| Current nav item | {label}, current page | {label}, বর্তমান পাতা | Current location stated in **text**, not only colour (`VB-006` NV-04) |
| Breadcrumb | Breadcrumb | ব্রেডক্রাম্ব | Landmark; truncates the middle, never the last item |
| Language toggle | Switch to {other_language} | {other_language}-এ পরিবর্তন করুন | Marks its own `lang` (`CG-011` BA-02) |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Longest BN string | Risk |
|---|---:|---|---|
| Primary nav | 24 | সার্ভিস বুক করুন (16) | Low |
| Workspace switcher | 24 | ম্যানেজড সার্ভিস (16) | Low |
| Breadcrumb | 30 | — | Middle truncation permitted; last item never |
| Page title | — | — | `title-page` 20px (`VB-003` §7) |

> Exceeding a budget is a **design conversation**, not a copy problem to solve by abbreviating
> (`VB-006` §8). Where the Bengali cannot fit, the control goes two-line before it goes
> icon-only (`VB-007` §7.3).

---

## 9. Open questions for design or product

| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | `P01` uses "Book a service" — a verb in a noun position. Confirmed as a deliberate exception? | No | Content Design Lead |
| 2 | `CG-004` §10 item 2 — is "booking" or "service order" the customer-facing term? This register assumes "My services" | **Yes** — `UI-011`, `UI-037` | `M01` owner with Content Design |
| 3 | Do all fourteen workspaces appear for every `P03` user, greyed where unpermitted, or only permitted ones? | Yes | `M29` owner + Content Design |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| [`UI-001_UI_String_Architecture_and_i18n_Key_Standard.md`](UI-001_UI_String_Architecture_and_i18n_Key_Standard.md) | Key scheme |
| [`UI-005_System_Permission_and_Session_Message_Library.md`](UI-005_System_Permission_and_Session_Message_Library.md) | Access messages |
| `CG-004` Terminology Standard | The nouns this register uses |
| `VB-006` §4.3 | Navigation component contract |
| `MD-027` Status and Lifecycle State Label Register | State labels shown in nav counters |

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
