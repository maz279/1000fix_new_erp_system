---
id: VB-006
title: Design System Content Standards
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design with Design System
reviewers: [Design System, Platform Engineering, Localisation Lead, Accessibility reviewer, portal owners]
approver: Content Design Lead
content_class: E
purpose: >
  Binds copy rules to components. PS-06 commits twelve portals to one component library and one
  token set; without a matching copy contract the same button says four things in four
  workspaces. If a component's appearance is defined, what it can say must be defined with it.
traces_to: [04-00 PS-06, 04-00 PS-09, 04-00 PS-11, 05-05 BR-STD-04, 05-05 BR-STD-06, CG-003, CG-011, VB-001, VB-002, VB-008]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-06 (consistent design system, one component library, one token set), PS-09 (every error states what happened and what to do), PS-11 (no business rule client-side)
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §1 BR-STD-04, BR-STD-05, BR-STD-06 rule classification H/A/S/C
    verified: 2026-08-15
    class: P1
  - source: Nielsen Norman Group — content standards in design systems; Indeed Design — content in, for and of design systems
    verified: 2026-08-15
    class: P3
supersedes: none
review_due: 2027-02-15
---

# VB-006 — Design System Content Standards

> **If you define what a button looks like, define what it can say.** `PS-06` puts twelve portals
> on one component library. A component with a specified appearance and an unspecified copy
> contract will be given different copy by each team that consumes it — and the design system
> will have made the divergence *easier*, not harder.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | The copy contract for each component in the shared library |
| **What it does not govern** | The strings themselves (`UI-001`…`UI-042`); visual specification (Design System); voice (`VB-001`); tone per audience (`VB-002`) |
| **What breaks without it** | Four workspaces labelling the same action four ways, and every team re-deciding toast-versus-banner from scratch |

**How to use it.** Before writing copy into a component, read that component's block. Before
adding a component to the library, add its block here.

---

## 2. Scope

**In scope:** every component in the shared library, across Odoo OWL, Next.js, React Native and
Flutter implementations.

**Out of scope:** Metabase and Grafana embedded analytics, which are third-party surfaces —
`RP-007` governs their labelling.

---

## 3. Global rules

Apply to every component before its specific rules.

| # | Rule |
|---|---|
| **DS-01** | **Every component has a copy contract.** A component without one is not released |
| **DS-02** | Copy is a **prop, never hard-coded** in the component |
| **DS-03** | Every string has an i18n key (`UI-001`). No literal strings in components |
| **DS-04** | Character budgets are stated per slot and enforced by the **Bengali** length, not the English (`CG-010` BC-01) |
| **DS-05** | Components never truncate meaning. If it does not fit, the copy is wrong or the component is |
| **DS-06** | Components never invent copy. No default label, no fallback string, no "Item" placeholder reaching production |
| **DS-07** | Sentence case everywhere (`CG-003` §1.2) |
| **DS-08** | No terminal punctuation on labels, buttons, headings, table cells or single-phrase items; full stops on sentences (`CG-003` §5) |
| **DS-09** | Colour is never the only signal; every state carries a text label (`CG-011` CL-01, `VB-008`) |
| **DS-10** | Components enforce **no business rules** (`PS-11`). Client-side validation copy says what the field needs, never what the rule decides |
| **DS-11** | Every interactive component has an accessible name that matches or extends its visible label (`CG-011`) |
| **DS-12** | Every component that can fail has a defined failure copy slot. A component with no failure state is incompletely specified |

---

## 4. Action components

### 4.1 Button

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Label | **20 chars** | Verb or verb phrase. The verb from `CG-004` §4.8 |
| Loading label | 24 chars | Present continuous: "Saving…" |
| Tooltip | 60 chars | Only where the label cannot be self-explanatory. Never restates the label |

| # | Rule |
|---|---|
| **BT-01** | The label names **what will happen**, not the mechanism: "Create service order", not "Submit" |
| **BT-02** | Never "OK", "Yes", "No", "Submit", "Continue" on a consequential action. The verb must be visible without reading the dialog |
| **BT-03** | One primary button per view. Everything else is secondary or tertiary |
| **BT-04** | Destructive buttons carry the destructive verb: "Cancel order", "Void invoice", "Remove seller" |
| **BT-05** | Disabled buttons **must** be accompanied by text explaining why — a disabled control with no explanation is a dead end |
| **BT-06** | Ellipsis only where a further step requiring input follows: "Reassign…" |
| **BT-07** | Never a bare icon button for a destructive or irreversible action (`VB-007`) |

| Do not | Do |
|---|---|
| Submit | Create service order |
| OK | Approve estimate |
| Delete | Archive device |
| Yes | Cancel order |
| Click to continue | Continue to payment |

### 4.2 Link

| # | Rule |
|---|---|
| **LK-01** | Link text describes the destination and works out of context (`CG-011` LK-01, WCAG SC 2.4.4) |
| **LK-02** | Banned: "click here", "here", "read more", "learn more", "this link", bare URLs |
| **LK-03** | The same link text always leads to the same destination (WCAG SC 3.2.4) |
| **LK-04** | A link that downloads states format and size; a link that leaves the ERP says so |
| **LK-05** | Links are for navigation, buttons for actions. Never style one as the other |

### 4.3 Menu item and navigation

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Primary nav | **24 chars** | Noun or noun phrase. The area, not the action |
| Sub-nav | 28 chars | |
| Breadcrumb | 30 chars | Truncate the middle, never the last item |

| # | Rule |
|---|---|
| **NV-01** | Navigation labels are nouns; buttons are verbs |
| **NV-02** | Labels come from `UI-002` and match `CG-004` exactly |
| **NV-03** | Never abbreviate a nav label to fit. Rename the area |
| **NV-04** | The current location is stated in text, not only by colour or weight |

---

## 5. Feedback components

**The most-confused family in enterprise UI.** This table decides which to use.

| Component | Use when | Dismissal | Persists? | Never use for |
|---|---|---|:--:|---|
| **Inline validation** | A specific field is wrong | On correction | No | Anything not field-specific |
| **Toast** | A completed action succeeded, no decision needed | Auto, 5s | No | **Errors, anything the user must act on** |
| **Inline alert** | Something about *this view* needs attention | Manual or on resolution | Yes | Global announcements |
| **Banner** | Something system-wide or page-wide affects the user | Manual, or persists | Yes | Field-level problems |
| **Modal** | The user must decide before continuing | Explicit choice | Yes | Information they could read in place |
| **Empty state** | There is nothing to show | n/a | Yes | Loading |
| **Full-page error** | The view cannot render at all | Retry | Yes | A recoverable failure |

> **The rule that prevents most misuse: if the user must act, it does not auto-dismiss.** A toast
> carrying an error is an error the user may never see.

### 5.1 Inline validation

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Message | **90 chars** | What is wrong and what to enter |

| # | Rule |
|---|---|
| **IV-01** | Names the field by its visible label |
| **IV-02** | States the required format or value, not only that it is wrong (WCAG SC 3.3.3) |
| **IV-03** | Never blames: "Enter the date as DD/MM/YYYY", not "You entered an invalid date" |
| **IV-04** | Appears after the field loses focus or on submit, never on every keystroke |
| **IV-05** | Text, not only a red border (`CG-011` EA-01) |
| **IV-06** | Client-side validation covers **format only**. Business rules are server-side (`PS-11`), and their messages come from `UI-004` |

### 5.2 Toast

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Message | **60 chars** | What happened, past tense |
| Action | 16 chars | Optional. "Undo" is the main legitimate use |

| # | Rule |
|---|---|
| **TO-01** | **Success and neutral confirmations only.** Never errors, never warnings |
| **TO-02** | Past tense, factual: "Estimate sent" |
| **TO-03** | No exclamation marks, no celebration |
| **TO-04** | 5 seconds; longer if it carries an "Undo" |
| **TO-05** | Never carries information the user needs later. Toasts are not a record |
| **TO-06** | Announced to assistive technology as a polite live region |

### 5.3 Inline alert

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Title | **60 chars** | The situation, sentence case, no full stop |
| Body | 200 chars | Cause and remedy |
| Action | 20 chars | The remedy, where actionable |

| # | Rule |
|---|---|
| **AL-01** | Four severities: info, success, warning, error. Each carries an icon **and** a text label (`VB-008`) |
| **AL-02** | Error alerts follow the three-part structure — what happened, why, what next (`CG-003` §3) |
| **AL-03** | Warning alerts state the consequence of proceeding |
| **AL-04** | Never used for a field-specific problem |
| **AL-05** | Error and warning alerts are not auto-dismissible |

### 5.4 Banner

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Message | **120 chars** | The situation and its effect on the user |
| Action | 20 chars | |

| # | Rule |
|---|---|
| **BN-01** | Page- or system-wide only: maintenance windows, degraded services, offline state, expiring certification |
| **BN-02** | States the **effect on the reader**, not the internal condition: "Payments are unavailable. Take payment at the counter and record it here later" |
| **BN-03** | Maximum one banner. If two conditions apply, the more severe wins |
| **BN-04** | Offline banners state what is saved and what is not (`UI-009`) |

### 5.5 Modal and confirmation dialog

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Title | **50 chars** | The action, sentence case, **no question mark** |
| Body | 300 chars | The consequence, in full |
| Primary button | 20 chars | The verb of doing it |
| Secondary button | 20 chars | The verb of not doing it |

| # | Rule |
|---|---|
| **MD-01** | Title is a statement, not a question: "Cancel this service order", not "Are you sure?" |
| **MD-02** | Body states **what will happen**, including anything irreversible and anything the customer will see |
| **MD-03** | Buttons are verbs. **Never OK/Cancel on a destructive action** — a fast reader cannot tell which "cancel" means what |
| **MD-04** | Where `BR-STD-06` applies, the modal captures a reason and the field is marked required |
| **MD-05** | Where an override needs authority, the modal names the role that can grant it |
| **MD-06** | Never used for information the user could read in place |
| **MD-07** | Irreversibility is stated explicitly: "This cannot be undone" |

**Pattern**

> **Cancel this service order**
>
> The customer will be notified by SMS. 4 reserved parts will return to stock. The device is
> still at the branch.
>
> This cannot be undone.
>
> Reason for cancellation (required) ▢
>
> `[Cancel order]` `[Keep order]`

### 5.6 Empty state

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Heading | **50 chars** | What is not here |
| Body | 140 chars | Why, and what to do |
| Action | 24 chars | The first step, where there is one |

| # | Rule |
|---|---|
| **ES-01** | Four kinds, and they are different copy: **nothing yet**, **no results for this filter**, **not configured**, **no permission** |
| **ES-02** | "Nothing yet" states what will appear here and how to create the first one |
| **ES-03** | "No results" names the filter and offers to clear it |
| **ES-04** | "Not configured" names who configures it |
| **ES-05** | "No permission" states what is needed and who grants it, without exposing what exists (`UI-005`) |
| **ES-06** | Never blank. **On day one of every wave, every screen is an empty state** |
| **ES-07** | Never jokey. This is the first thing 800+ internal users see |

### 5.7 Full-page error

| # | Rule |
|---|---|
| **FE-01** | States what failed at the level the user understands, never the technical cause |
| **FE-02** | Offers retry, a route back, and the hotline |
| **FE-03** | Carries a reference the user can quote to support |
| **FE-04** | Never exposes stack traces, model names or internal identifiers (`CG-003` E-02) |

---

## 6. Data components

### 6.1 Table

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Column header | **24 chars** | Noun, sentence case, no full stop |
| Cell | Varies | Value only, never explanation |
| Empty cell | 8 chars | See TB-04 |
| Row count | 40 chars | "142 service orders" |

| # | Rule |
|---|---|
| **TB-01** | Headers name the unit where one applies: "Effort (PW)", "Amount (BDT)" |
| **TB-02** | Numeric columns are right-aligned with tabular figures (`VB-003` TY-03) |
| **TB-03** | Dates use the `05-06` §9 format. Never a relative date alone in a data table |
| **TB-04** | An empty cell means "no value". If the distinction matters, use "—" for not applicable and leave blank for not captured, and **say which in the column tooltip** (`CG-003` §8.1 bans a bare "N/A") |
| **TB-05** | Status cells use `MD-027` labels with `VB-008` semantics |
| **TB-06** | Header is a real `<th>`; the table is data, not layout (`CG-011` ST-05, ST-06) |
| **TB-07** | Bulk-action bars state the selection count and scope: "12 selected of 142" |

### 6.2 Form field

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Label | **36 chars** | Noun, sentence case |
| Help text | 120 chars | Why or what format |
| Placeholder | 40 chars | An example, never a label |
| Unit suffix | 10 chars | |

| # | Rule |
|---|---|
| **FF-01** | Every field has a **visible, persistent label**. Placeholder is never the label (WCAG SC 3.3.2) |
| **FF-02** | Required is marked in **text**, not only by an asterisk or colour |
| **FF-03** | Format requirements appear **before** submission, not only on failure (`CG-011` EA-06) |
| **FF-04** | Help text explains why the field exists or what format it needs — never restates the label |
| **FF-05** | Placeholder shows an example: "01712345678" |
| **FF-06** | Labels come from `UI-003` and match `CG-004` |
| **FF-07** | Optional fields are marked, not required ones, where most fields are required — whichever set is smaller |

### 6.3 Badge and chip

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Badge | **14 chars** | Single state word or short phrase |
| Chip | 24 chars | Filter value or tag |

| # | Rule |
|---|---|
| **BG-01** | Badge text is the `MD-027` customer-facing or internal label, never an abbreviation invented locally |
| **BG-02** | Semantics from `VB-008`. Never the brand palette |
| **BG-03** | Upper case permitted **only** in status badges of 12 characters or fewer (`CG-003` §1.2) |
| **BG-04** | Never colour alone; the word is the signal and the colour reinforces it |
| **BG-05** | A removable chip states what removing it does |

### 6.4 Card

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Title | **50 chars** | The entity, usually its identifier and name |
| Subtitle | 60 chars | The distinguishing fact |
| Body | 200 chars | |

| # | Rule |
|---|---|
| **CD-01** | Title leads with the identifier where the user scans for it: "SR-2026-114882 · Dell Latitude 5420" |
| **CD-02** | The most decision-relevant fact is the subtitle |
| **CD-03** | A card is not a form. If it needs more than three facts, it is a detail view |

---

## 7. Process components

### 7.1 Stepper and wizard

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Step label | **24 chars** | Noun phrase naming the step |
| Step description | 60 chars | |

| # | Rule |
|---|---|
| **ST-01** | Step labels are nouns, not verbs: "Device details", not "Enter device details" |
| **ST-02** | Number of steps is stated up front. `P01` booking is ≤ 3 steps (`04-00` §P01) |
| **ST-03** | Completed steps are labelled complete in text, not only by a tick |
| **ST-04** | The user is told what they can and cannot go back and change |

### 7.2 Progress and loading

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Message | **60 chars** | What is happening |
| Detail | 90 chars | Count or estimate where known |

| # | Rule |
|---|---|
| **PR-01** | Above 2 seconds, say what is happening. Never a bare spinner |
| **PR-02** | Bulk operations show progress and count — `NFR-041` requires feedback on 1,000-record operations |
| **PR-03** | Long operations state whether the user may leave |
| **PR-04** | Never estimate a time the system cannot predict |
| **PR-05** | On failure part-way, state what completed and what did not |

### 7.3 Search and filter

| # | Rule |
|---|---|
| **SF-01** | Search placeholder states the **scope**: "Search service orders" |
| **SF-02** | Active filters are stated in text and individually removable |
| **SF-03** | Result count always shown |
| **SF-04** | Zero results distinguishes "no match" from "no data" (`ES-01`) |
| **SF-05** | Bengali search accommodates phonetic-input spelling variation (`CG-010` BC-10) |

---

## 8. Character budgets — summary

Budgets are **Bengali** lengths (`DS-04`). English will be 20–40% shorter.

| Component | Slot | Budget |
|---|---|---:|
| Button | Label | 20 |
| Menu | Primary nav | 24 |
| Toast | Message | 60 |
| Inline validation | Message | 90 |
| Alert | Title / body | 60 / 200 |
| Banner | Message | 120 |
| Modal | Title / body | 50 / 300 |
| Empty state | Heading / body | 50 / 140 |
| Table | Column header | 24 |
| Form field | Label / help | 36 / 120 |
| Badge | Text | 14 |
| Card | Title / subtitle | 50 / 60 |
| Stepper | Step label | 24 |

Exceeding a budget is a **design conversation**, not a copy problem to solve by abbreviating.

---

## 9. Adding a component

| Step | Action |
|---|---|
| 1 | Design System proposes the component with its visual specification |
| 2 | Content Design writes its copy contract — slots, budgets, rules, do/do-not |
| 3 | Localisation confirms the budgets survive Bengali |
| 4 | Accessibility confirms the accessible-name and live-region behaviour |
| 5 | The block is added to this file **before** the component is released (`DS-01`) |
| 6 | The addition is logged in `RF-006` |

---

## 10. Dependencies

| Depends on | Why |
|---|---|
| `CG-003` | Mechanics every slot follows |
| `CG-004` | The approved verbs and nouns slots carry |
| `CG-011` | Accessible names, live regions, label and error obligations |
| `VB-002` | Sentence budgets per audience, which override these where tighter |
| `VB-008` | Status semantics for badges, alerts and cells |
| `MD-027` | The state labels badges and cells display |
| `UI-001` | i18n keys `DS-03` requires |

---

## 11. Enforcement

| Check | Mechanism | When |
|---|---|---|
| No literal strings in components | Automated lint | Every commit |
| Every string has an i18n key | Automated | Every commit |
| Character budget, measured on the Bengali | Automated | Every commit |
| Banned button labels (`OK`, `Submit`, `Yes`) | Automated | Every commit |
| Banned link text | Automated | Every commit |
| No terminal punctuation on labels | Automated | Every commit |
| Component has a copy contract in this file | Design-system release gate | Every component release |
| Toast used for an error | Manual review, gate G1 | Per surface |
| Disabled control without an explanation | Manual review | Per surface |
| Modal buttons are verbs | Automated pattern + manual | Per surface |

---

## 12. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per design-system release |
| Out-of-cycle trigger | A new component; a budget repeatedly breached; an accessibility finding |
| Owner | Content Design Lead with Design System |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`VB-001_ERP_Product_Voice_and_Tone_Guide.md`](VB-001_ERP_Product_Voice_and_Tone_Guide.md) | The voice components express |
| [`VB-002_Persona_and_Portal_Tone_Matrix.md`](VB-002_Persona_and_Portal_Tone_Matrix.md) | Per-surface budgets that may be tighter |
| [`VB-007_Iconography_and_Label_Pairing_Register.md`](VB-007_Iconography_and_Label_Pairing_Register.md) | Icon-with-label rules for these components |
| [`VB-008_Status_Colour_and_Label_Semantics_Register.md`](VB-008_Status_Colour_and_Label_Semantics_Register.md) | Badge, alert and cell semantics |
| [`../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md`](../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) | Mechanics |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | Accessibility obligations |
| `UI-001` … `UI-010` | The cross-cutting libraries filling these slots |
| `UI-004` Validation and Error Message Library | Server-side rule messages |
| `UI-006` Empty State Library | §5.6 at scale |
| `UI-007` Confirmation and Destructive Action Library | §5.5 at scale |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Twelve global rules, copy contracts for 17 components across action, feedback, data and process families, the feedback-component selection table, Bengali-measured character budgets, component-addition procedure | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Every component family has slots, budgets, rules and do/do-not guidance
- [x] The toast-versus-alert-versus-banner confusion resolved by a selection table with a single decisive rule
- [x] Character budgets stated in Bengali lengths per `DS-04`
- [x] `PS-11` respected — client-side validation is format-only
- [x] Empty states treated as a first-class case with four distinct kinds
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; the **strings** in these components are bilingual
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
