---
id: VB-008
title: Status Colour and Label Semantics Register
project: 1000FiX ERP System v2.0
content_type: Register
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Design System Lead
author: Design System with Content Design
reviewers: [Content Design Lead, Enterprise Architecture, Accessibility reviewer, Localisation Lead, BI Lead]
approver: Content Design Lead
content_class: D
purpose: >
  Fixes how a human recognises a system state. MD-027 defines what the states are; this register
  defines the colour, glyph and label each one wears, identically on twelve portals, in reports,
  in print and in both languages. Divergent status colours across portals cause operational
  error - a dispatcher and a branch manager looking at the same job must see the same thing.
traces_to: [MD-027, 05-02 DM-10, 05-05, VB-003, VB-007, CG-011, RP-007, CG-004]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: VB-008_Status_Colour_and_Label_Semantics_Register_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 DM-10 — explicit state selection field with the transition map declared in one place
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §1 rule classification H / A / S / C
    verified: 2026-08-15
    class: P1
  - source: 1000_fix_corporate_website project_content CB-001 §3.4 functional colours
    verified: 2026-08-15
    class: P1
  - source: W3C WCAG 2.1 SC 1.4.1 (use of colour), SC 1.4.3 (contrast minimum), SC 1.4.11 (non-text contrast); ratios computed 2026-08-15
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# VB-008 — Status Colour and Label Semantics Register

> **Status is the highest-frequency information in an ERP.** A dispatcher scans 200 job states
> before lunch. A branch manager reads a WIP board every hour. A customer refreshes a tracking
> page. **All three must be reading the same vocabulary.**
>
> `MD-027` owns *what the states are*. This file owns *how a human recognises them*.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | Colour, glyph and label treatment for every lifecycle state, on every surface |
| **What it does not govern** | Which states exist and their transitions (`MD-027`, `05-02` DM-10); the icon glyph library (`VB-007` §6.3); chart colour (`RP-007`) |
| **What breaks without it** | Green meaning "complete" in one workspace and "on track" in another, and a state shown only by colour to a colour-blind dispatcher |

---

## 2. The three-signal rule

> **Colour · glyph · label. Always all three. No exceptions.**

| # | Rule | Basis |
|---|---|---|
| **TS-01** | Every status carries a **text label**. Colour is never the only signal | WCAG SC 1.4.1, `CG-011` CL-01 |
| **TS-02** | Every status carries a **glyph** whose shape differs from its neighbours, so it survives greyscale, monochrome print and colour-blind vision | `VB-007` SI-02 |
| **TS-03** | The **label is the meaning**; colour and glyph are speed aids |
| **TS-04** | Content never instructs by colour: not "the red rows", but "the breached rows, shown in red" | `CG-011` CL-03 |
| **TS-05** | A status must be readable in **greyscale**. Print the board in black and white; if it is unusable, the design is wrong |

---

## 3. The semantic palette

**This palette is deliberately not the brand palette.** `VB-003` §3 measured the `CB-001`
functional colours and four of them fail WCAG AA as text. The values below are derived to pass.

### 3.1 The eight semantic tokens

| Token | Text / border | On white | Fill tint | Text on tint | Meaning |
|---|---|---:|---|---:|---|
| `status-neutral` | `#495057` | **8.18** | `#E9ECEF` | 6.90 | Not started, informational, no action implied |
| `status-progress` | `#1E5F8A` | **6.86** | `#E8F4FC` | 5.9 | Under way, on track |
| `status-success` | `#146C43` | **6.45** | `#D1E7DD` | 4.97 | Completed successfully, no further action |
| `status-warning` | `#8A6100` | **5.54** | `#FFF3CD` | 5.00 | At risk, action advisable |
| `status-error` | `#B02A37` | **6.50** | `#F8D7DA` | 4.86 | Failed, breached, or blocked by a hard rule |
| `status-info` | `#0F6674` | **6.62** | `#CFF4FC` | 5.67 | Waiting on someone else; no fault |
| `status-hold` | `#59359A` | **8.75** | `#E2D9F3` | 6.44 | Deliberately paused; distinct from failure |
| `status-inactive` | `#6C757D` | **4.69** | `#F8F9FA` | 4.5 | Archived, cancelled, superseded, closed |

### 3.2 Why these values, not `CB-001` §3.4

| `CB-001` functional colour | Ratio on white | Verdict | Replaced by |
|---|---:|---|---|
| Success Green `#28A745` | 3.13 | Large text only — fails as a badge label | `#146C43` at 6.45 |
| Warning Yellow `#FFC107` | **1.63** | Fails everything | `#8A6100` at 5.54 |
| Error Red `#DC3545` | 4.53 | Passes on pure white only; no margin | `#B02A37` at 6.50 |
| Info Blue `#17A2B8` | 3.04 | Large text only, marginal | `#0F6674` at 6.62 |

| # | Rule |
|---|---|
| **SP-01** | **The `CB-001` functional colours remain valid as fills** — a green success banner background, a yellow warning stripe. They are **not valid as text or as a small badge label** |
| **SP-02** | Tints alone are 1.1–1.4:1 against white and are not distinguishable as fills without help. **Every tinted badge carries a 1px border in its text colour**, which is ≥ 4.69:1 and comfortably passes the 3:1 non-text threshold |
| **SP-03** | `status-hold` is purple because the alternative — reusing warning yellow — conflates "someone paused this deliberately" with "this is going wrong". They lead to different actions |
| **SP-04** | Eight tokens. Adding a ninth requires a Design System and Content Design decision and an `RF-006` entry |

### 3.3 Dark theme

| Token | Text | Fill | Note |
|---|---|---|---|
| `status-neutral` | `#ADB5BD` | `#343A40` | |
| `status-progress` | `#7FC4E8` | `#1C3A4D` | Brand blue is safe as text on dark (6.26:1) |
| `status-success` | `#75C69A` | `#12351F` | |
| `status-warning` | `#E8B84B` | `#3D2E08` | |
| `status-error` | `#E88A93` | `#3D171B` | |
| `status-info` | `#6BC5D6` | `#0C2F35` | |
| `status-hold` | `#B79BE0` | `#241A3D` | |
| `status-inactive` | `#868E96` | `#2B2F33` | |

---

## 4. The state register

Every state maps to exactly one token. Internal state names come from `05-02` DM-10 transition
maps; customer-facing labels come from `MD-027`.

> **Bengali labels below are indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

### 4.1 Service order — `fix.service.order` (`M01`)

| Internal state | Token | Glyph | Internal label | Customer-facing label | Bengali (customer) |
|---|---|---|---|---|---|
| `draft` | neutral | ○ circle | Draft | — *(not shown)* | — |
| `submitted` | info | ⏱ clock | Submitted | Booking received | বুকিং গৃহীত হয়েছে |
| `scheduled` | progress | ▸ chevron | Scheduled | Scheduled | সময় নির্ধারিত |
| `in_transit` | progress | ➤ arrow | In transit | On the way to us | আমাদের পথে |
| `received` | progress | ▸ chevron | Received | Received at service centre | সার্ভিস সেন্টারে গৃহীত |
| `diagnosing` | progress | ▸ chevron | Diagnosing | Being checked | পরীক্ষা করা হচ্ছে |
| `awaiting_approval` | info | ⏱ clock | Awaiting approval | Waiting for your approval | আপনার অনুমোদনের অপেক্ষায় |
| `awaiting_parts` | hold | ⏸ pause | Awaiting parts | Waiting for a part | পার্টসের অপেক্ষায় |
| `in_repair` | progress | ▸ chevron | In repair | Being repaired | মেরামত করা হচ্ছে |
| `qc_pending` | info | ⏱ clock | QC pending | Final checks | চূড়ান্ত পরীক্ষা |
| `ready` | success | ✓ tick | Ready | Ready for collection | সংগ্রহের জন্য প্রস্তুত |
| `completed` | success | ✓ tick | Completed | Completed | সম্পন্ন |
| `on_hold` | hold | ⏸ pause | On hold | On hold | স্থগিত |
| `sla_breached` | error | ! circle | SLA breached | Delayed | বিলম্বিত |
| `cancelled` | inactive | ⊘ slash | Cancelled | Cancelled | বাতিল |
| `rework` | warning | ↻ arrows | Rework | Being re-checked | পুনরায় পরীক্ষা |

> **`sla_breached` shows the customer "Delayed", not "SLA breached".** The customer has no SLA;
> they have a promise we did not keep. The internal label carries the contractual meaning; the
> customer label carries the human one. This is `TS-03` and `CG-004` `T-06` working together.

### 4.2 Estimate — `fix.estimate` (`M01`, `M36`)

| Internal state | Token | Glyph | Internal label | Customer-facing label |
|---|---|---|---|---|
| `draft` | neutral | ○ | Draft | — |
| `sent` | info | ⏱ | Sent | Waiting for your approval |
| `approved` | success | ✓ | Approved | Approved |
| `part_approved` | warning | ◑ half | Part-approved | Partly approved |
| `declined` | error | ✕ | Declined | Declined |
| `expired` | inactive | ⊘ | Expired | Expired |
| `revised` | warning | ↻ | Revised | Updated estimate sent |

### 4.3 Warranty claim — `fix.warranty.claim` (`M09`)

| Internal state | Token | Glyph | Label |
|---|---|---|---|
| `draft` | neutral | ○ | Draft |
| `submitted` | info | ⏱ | Submitted to brand |
| `info_requested` | warning | ! triangle | Information requested |
| `approved` | success | ✓ | Approved |
| `part_approved` | warning | ◑ | Part-approved |
| `rejected` | error | ✕ | Rejected |
| `reconciled` | success | ✓ | Reconciled |
| `written_off` | inactive | ⊘ | Written off |

### 4.4 Consignment — `fix.consignment` (`M03`)

| Internal state | Token | Glyph | Internal label | Customer-facing label |
|---|---|---|---|---|
| `booked` | info | ⏱ | Booked | Collection booked |
| `assigned` | progress | ▸ | Assigned | Rider assigned |
| `collected` | progress | ➤ | Collected | Collected |
| `in_transit` | progress | ➤ | In transit | On the way |
| `delivered` | success | ✓ | Delivered | Delivered |
| `exception` | error | ! circle | Exception | We could not complete this |
| `returned` | warning | ↩ | Returned to origin | Returned |

### 4.5 Invoice and payment (`M20`)

| Internal state | Token | Glyph | Label |
|---|---|---|---|
| `draft` | neutral | ○ | Draft |
| `posted` | progress | ▸ | Posted |
| `sent` | info | ⏱ | Sent |
| `part_paid` | warning | ◑ | Partly paid |
| `paid` | success | ✓ | Paid |
| `overdue` | error | ! circle | Overdue |
| `disputed` | error | ! circle | Disputed |
| `credited` | inactive | ⊘ | Credited |
| `void` | inactive | ⊘ | Void |

### 4.6 Contract — `fix.contract` (`M08`)

| Internal state | Token | Glyph | Label |
|---|---|---|---|
| `draft` | neutral | ○ | Draft |
| `pending_approval` | info | ⏱ | Pending approval |
| `active` | success | ✓ | Active |
| `expiring` | warning | ! triangle | Expiring soon |
| `expired` | inactive | ⊘ | Expired |
| `suspended` | hold | ⏸ | Suspended |
| `terminated` | inactive | ⊘ | Terminated |
| `renewed` | success | ✓ | Renewed |

### 4.7 Cross-cutting states

Apply anywhere the concept appears. **Never re-coloured locally.**

| Concept | Token | Glyph | Label |
|---|---|---|---|
| Offline | warning | ☁ cloud-slash | Offline |
| Syncing | progress | ↻ | Syncing |
| Sync failed | error | ! circle | Sync failed |
| Unsaved changes | warning | ● dot | Unsaved changes |
| Locked by another user | hold | 🔒 padlock | Locked by *(name)* |
| No permission | inactive | 🔒 padlock | No access |
| Certification expired | error | ! circle | Certification expired |
| Certification expiring | warning | ! triangle | Expires in *(n)* days |
| Verified | success | ✓ | Verified |
| Unverified | neutral | ○ | Not verified |
| Provisional | warning | ◑ | Provisional |

---

## 5. Application by surface

| Surface | Treatment |
|---|---|
| **Badge** (`VB-006` §6.3) | Tint fill + 1px border in the text colour + text colour + glyph. 14-char budget |
| **Table status cell** | Glyph + label, text colour only, **no fill** — fills in a dense table destroy row scanning (`VB-003` §5) |
| **Timeline / tracker** | Glyph + label + colour; completed steps also carry the word "Complete" |
| **Alert / banner** | Tint background, 4px left border in the text colour, glyph + title + body (`VB-006` §5.3) |
| **Chart series** | `RP-007` governs; where a chart encodes status, it uses these tokens and **labels the series directly** |
| **Print** | **Greyscale.** Glyph + label only. Token colour is not printed (`VB-004` §5) |
| **Thermal receipt** | Label only, monospace, bold for error and warning |
| **Email** | Tint fill + dark text (`VB-005` §5). Never coloured text on white |
| **Push / SMS** | Label only, in words |
| **`P02` / `P09` mobile** | Larger glyph, high-contrast text, no tint fill — sunlight legibility |
| **Screen reader** | Label announced; glyph is decorative; colour is not announced |

---

## 6. Rules

| # | Rule |
|---|---|
| **SR-01** | One token per state. A state does not change colour by surface, only its **treatment** changes |
| **SR-02** | A state that exists in `MD-027` and is not in this register is a defect. Both files are updated together |
| **SR-03** | Customer-facing labels come from `MD-027`; internal labels come from the module's transition map. **Never show an internal state name to a customer** (`CG-004` `T-06`) |
| **SR-04** | `status-error` is reserved for **failure, breach, or a hard-rule block** (`05-05` class **H**). It is not used for "needs attention" |
| **SR-05** | `status-warning` maps to approved-override (**A**) and soft (**S**) rule classes, and to at-risk conditions |
| **SR-06** | `status-hold` means a human paused this deliberately. Never used for a system failure |
| **SR-07** | `status-info` means waiting on someone else with no fault implied. It is the correct token for "awaiting customer approval" — the customer has done nothing wrong |
| **SR-08** | Never invent a shade. The eight tokens are the palette |
| **SR-09** | Never use the brand blue `#39B1DF` as a status colour. At 2.46:1 it fails text and non-text contrast on light (`VB-003` §3) |
| **SR-10** | Bengali status labels are the same length budget as any badge — 14 characters (`VB-006` §8). Where a Bengali label exceeds it, the badge goes two-line rather than truncating (`VB-007` BL-04) |

---

## 7. Accessibility

| # | Rule | SC |
|---|---|---|
| **AC-01** | Colour is never the only signal | **1.4.1** |
| **AC-02** | Text colour meets 4.5:1 against its background at badge sizes | 1.4.3 |
| **AC-03** | Badge borders and glyphs meet 3:1 non-text contrast | 1.4.11 |
| **AC-04** | Glyph shapes differ between adjacent severities — triangle for warning, circle for error | 1.4.1 |
| **AC-05** | Status changes are announced to assistive technology as a polite live region | 4.1.3 |
| **AC-06** | The status label is part of the accessible name of any control it sits on | 1.1.1 |
| **AC-07** | Colour-blind check: the register is verified under deuteranopia, protanopia and tritanopia simulation | 1.4.1 |
| **AC-08** | Greyscale check: the register is verified printed in black and white | 1.4.1 |

---

## 8. Do and do not

| Do not | Do |
|---|---|
| Show a coloured dot with no label | Dot + glyph + label |
| Use green for "on track" and also for "complete" | `status-progress` for under way, `status-success` for complete |
| Use red for "needs attention" | Red is failure or breach. Use warning |
| Show a customer "SLA breached" | Show "Delayed"; keep the contractual term internal |
| Fill a table cell with a status colour | Text colour and glyph only in dense tables |
| Print in colour and hope | Design the greyscale version |
| Invent a ninth token for a new module | Map to one of the eight |
| Use `#FFC107` as warning text | It is 1.63:1. Use `#8A6100` |
| Use the brand blue for status | It fails contrast |
| Truncate a Bengali status label | Two-line badge |

---

## 9. Dependencies

| Depends on | Why |
|---|---|
| `MD-027` Status and Lifecycle State Label Register | The authoritative state list and customer-facing labels |
| `05-02` DM-10 | The transition maps that define internal state names |
| `05-05` | Rule classes H/A/S/C, which drive `SR-04` and `SR-05` |
| `VB-007` §6.3 | Status glyphs |
| `VB-003` §3 | Contrast constraints |
| `BN-003` | Authoritative Bengali labels |
| `RP-007` | Chart application |

---

## 10. Enforcement

| Check | Mechanism | When |
|---|---|---|
| Every `MD-027` state has a register row | Automated cross-file check | Every commit |
| No status shown without a text label | Component lint | Every commit |
| Token contrast in both themes | Automated token audit | Every design-system release |
| No brand blue used as a status | Automated | Every commit |
| Only the eight tokens in use | Automated | Every commit |
| Greyscale legibility | Visual review | Every design-system release |
| Colour-blind simulation | Visual review | Every design-system release |
| Bengali badge truncation | Visual regression | Every release |
| Internal state name never shown to a customer | `AUDIT_Checklist_Recurring.md` §F2 | Every wave |

---

## 11. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per design-system release, and whenever `MD-027` changes |
| Out-of-cycle trigger | A new state machine; an accessibility finding; a `CB-001` revision |
| Owner | Design System Lead |
| Bengali counterpart | `VB-008_Status_Colour_and_Label_Semantics_Register_BN.md` — required, not yet written |
| Open dependency | `MD-027` and `BN-003` — §4 is provisional until both exist |

---

## 12. Related documents

| Document | Relationship |
|---|---|
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](VB-003_Brand_Application_in_Enterprise_UI.md) | Why the semantic palette is not the brand palette |
| [`VB-006_Design_System_Content_Standards.md`](VB-006_Design_System_Content_Standards.md) | Badge, alert and table components |
| [`VB-007_Iconography_and_Label_Pairing_Register.md`](VB-007_Iconography_and_Label_Pairing_Register.md) | Status glyphs |
| [`VB-004_Print_and_PDF_Brand_Template_Standard.md`](VB-004_Print_and_PDF_Brand_Template_Standard.md) | Greyscale print treatment |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | §7 |
| [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | `T-06` internal versus customer-facing |
| `MD-027` Status and Lifecycle State Label Register | The authoritative state source |
| `RP-007` Chart, Label and Visualisation Standard | Chart application |
| `UI-004` Validation and Error Message Library | Error states in messages |

---

## 13. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Three-signal rule, eight-token semantic palette derived to pass AA with measured ratios, light and dark themes, state register for six lifecycles plus cross-cutting states, per-surface application, ten rules, accessibility with colour-blind and greyscale verification | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Every token carries its measured contrast ratio, computed 2026-08-15
- [x] The divergence from `CB-001` §3.4 is justified with the failing ratios, not asserted
- [x] Three-signal rule stated as absolute
- [x] Internal versus customer-facing labels separated, with `sla_breached` worked as the example
- [x] Per-surface treatment covers print, thermal, email and mobile, not only screen
- [x] All internal links resolve
- [ ] Bengali counterpart written and signed off in context — **outstanding; blocks `Approved`**
- [ ] `MD-027` and `BN-003` confirmation — **outstanding; §4 provisional until then**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
