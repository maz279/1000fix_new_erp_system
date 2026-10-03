---
id: UI-006
title: Empty State and First-Run Copy Library
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
reviewers: [Localisation Lead, Design System, Accessibility reviewer, portal owners]
approver: Content Design Lead
content_class: D
purpose: >
  Zero-data, no-results, filtered-to-nothing, not-yet-configured and first-login copy for every
  list and dashboard. On day one of every wave, every screen is empty — empty states are the first
  thing 800+ internal users ever see of this system.
traces_to: [VB-006 §5.6, CG-011, UI-002, HC-016, CM-005]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: UI-006_Empty_State_and_First_Run_Copy_Library_BN.md
i18n_namespace: `common.empty.*`, `common.firstrun.*`
pinned_to:
  surface: All surfaces
  release: pending first build
  wave: W1
sources:
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-006 §5.6 — four kinds of empty state
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-006 — Empty State and First-Run Copy Library

> **On day one of every wave, every screen is an empty state.** They are not an edge case; they
> are the launch experience.
>
> Four kinds, and they are different copy (`VB-006` ES-01): **nothing yet**, **no results**,
> **not configured**, **no permission**.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Zero-data, no-results, not-configured, no-permission and first-login copy |
| Framework | All — Odoo OWL, Next.js, React Native, Flutter |
| Default language | Bengali default on customer and field surfaces (`PS-03`) |
| i18n namespace | ``common.empty.*`, `common.firstrun.*`` |
| Offline-capable | Applies to `P02`, `P09`, `P11` (`PS-08`) |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | Per surface — see `VB-002` §4.2 (`VB-002` §4.2) |
| Audience | All surfaces |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Kind | When | Never confused with |
|---|---|---|
| Nothing yet | The collection is genuinely empty | No results |
| No results | A filter or search excluded everything | Nothing yet |
| Not configured | Master data or setup is missing | Nothing yet |
| No permission | Data exists but is out of scope | Nothing yet — never reveal existence |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Nothing yet — `common.empty.none_yet.*`

| Surface | Key | Heading EN | Body EN | Action |
|---|---|---|---|---|
| Customer services | `p01.empty.orders` | No services yet | When you book a service it will appear here with live status. | Book a service |
| Customer devices | `p01.empty.devices` | No devices registered | Register a device to see its warranty and service history. | Register a device |
| Technician jobs | `p02.empty.jobs` | No jobs assigned | Your jobs for today will appear here. Pull down to refresh. | — |
| Dispatch queue | `ws.empty.dispatch_queue` | No unassigned jobs | Every job in your zones is assigned. | — |
| Workshop bench | `ws.empty.workshop` | No jobs on the bench | Jobs appear here when they are received at the workshop. | — |
| Invoices | `ws.empty.invoices` | No invoices in this period | Invoices appear here once orders are completed and billed. | — |

### 3.2 No results — `common.empty.no_results.*`

| Key | Heading EN | Body EN | Action |
|---|---|---|---|
| `common.empty.no_results.search` | No matches for "{query}" | Check the spelling, or search by reference, mobile number or serial number. | Clear search |
| `common.empty.no_results.filter` | No records match these filters | {filter_count} filters are applied. | Clear all filters |
| `common.empty.no_results.date` | Nothing in {period} | Try a wider date range. | Change dates |

> The filter count is stated so the user can see **why** nothing is shown (`VB-006` ES-03).

### 3.3 Not configured — `common.empty.not_configured.*`

| Key | Heading EN | Body EN | Action |
|---|---|---|---|
| `common.empty.not_configured.master_data` | {dataset} is not set up yet | {owner_role} configures this. Until then, {consequence}. | Contact {owner_role} |
| `common.empty.not_configured.price_list` | No price list for {segment} | Pricing is set by Commercial. Estimates cannot be created for this segment until it is. | — |
| `common.empty.not_configured.zone` | This area is not covered yet | We do not offer on-site service here. You can use pick and drop, or visit {nearest_branch}. | See delivery options |

### 3.4 No permission — `common.empty.no_permission.*`

| Key | Heading EN | Body EN |
|---|---|---|
| `common.empty.no_permission.list` | You do not have access to this | {role} can view this. Ask your manager if you need access. |

> **Never** states how many records exist, or that any do (`ES-05`, `UI-005` S-01).

### 3.5 First run — `common.firstrun.*`

| Surface | Key | Heading EN | Body EN |
|---|---|---|---|
| `P01` first login | `p01.firstrun.welcome` | Welcome to 1000FiX | Book a service, track it live, and keep your device history in one place. |
| `P02` first login | `p02.firstrun.welcome` | Your jobs, offline | Everything here works without a connection. Your work syncs when you reconnect. |
| `P03` first login | `ws.firstrun.welcome` | Choose your workspace | Each workspace opens on the work your role actually does. |
| `P09` first login | `p09.firstrun.welcome` | Today's manifest | Scan, deliver, collect. Works offline. |

---

## 4. Field labels and help text

Field copy is `UI-003`. This library carries no field labels.

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

Empty states carry no validation. Errors are `UI-004`.

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Heading | A real heading in the page hierarchy | 1.3.1 |
| Illustration | Decorative, empty alt (`MM-005`) | 1.1.1 |
| Action | A button with a verb label, not a bare link | 2.4.4 |
| Announcement | List transitioning to empty is announced politely | 4.1.3 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Heading | 50 | Low |
| Body | 140 | **Medium** — `not_configured.master_data` has three placeholders |
| Action | 24 | Low |

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
| [`UI-005_System_Permission_and_Session_Message_Library.md`](UI-005_System_Permission_and_Session_Message_Library.md) | No-permission wording |
| `VB-006` §5.6 | The component contract |
| `MM-005` Illustration and Empty-State Artwork Brief | Artwork |
| `CM-005` Wave Launch Communication Kit | Day-one context |

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
