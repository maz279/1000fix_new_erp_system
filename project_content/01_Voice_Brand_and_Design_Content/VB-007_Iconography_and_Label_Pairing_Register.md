---
id: VB-007
title: Iconography and Label Pairing Register
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
reviewers: [Content Design Lead, Localisation Lead, Accessibility reviewer, Brand]
approver: Content Design Lead
content_class: D
purpose: >
  Fixes which icon may accompany which label, where icon-only controls are prohibited, and how
  much room a Bengali label needs beside an icon. Bengali labels run 20-40% longer than English;
  icon-plus-label layouts that fit in English break in Bengali, and an icon-only control that
  seems obvious in one culture is a guess in another.
traces_to: [MM-004, VB-006, VB-008, CG-011, CG-010, CG-004]
priority: P2
wave: W1
bilingual: yes
bn_counterpart: VB-007_Iconography_and_Label_Pairing_Register_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-06 (one component library, one token set)
    verified: 2026-08-15
    class: P1
  - source: W3C WCAG 2.1 SC 1.1.1 (non-text content), SC 1.4.11 (non-text contrast 3:1), SC 2.5.5 target size
    verified: 2026-08-15
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-003 §3 measured contrast ratios of the CB-001 palette
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# VB-007 — Iconography and Label Pairing Register

> **An icon is a mnemonic, not a message.** It helps a user who already knows what the control
> does find it faster. It does not teach a user who does not. Every rule here follows from that.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | Which icon pairs with which label; where icon-only is allowed and forbidden; Bengali label allowances |
| **What it does not govern** | Icon visual design and production (`MM-004`); status colour semantics (`VB-008`); component copy (`VB-006`) |
| **What breaks without it** | The same action carrying three different icons across three workspaces, and a Bengali label truncating beside an icon that fitted in English |

---

## 2. Scope

**In scope:** all twelve portals, fourteen `P03` workspaces, printed documents where icons appear
(`VB-004`), and email (`VB-005`).

**Out of scope:** brand marks and logos (`VB-003` §8); illustration (`MM-005`); chart symbols
(`RP-007`); barcode and QR (`DT-044`).

---

## 3. The four pairing modes

Every icon in the system is in exactly one mode.

| Mode | Form | Where permitted |
|---|---|---|
| **A — Icon with visible label** | Icon + text, always both | **Default.** Any control, any surface |
| **B — Icon-only with accessible name** | Icon alone, name for assistive tech, tooltip on hover | Only the registered set in §5 |
| **C — Label only** | No icon | Where no registered icon exists |
| **D — Decorative** | Icon alone, marked decorative, no accessible name | Illustrative only, never interactive |

| # | Rule |
|---|---|
| **PM-01** | **Mode A is the default.** Mode B requires registration in §5 |
| **PM-02** | An unregistered icon-only control is a defect, not a design choice |
| **PM-03** | Mode B controls still carry an accessible name (WCAG SC 1.1.1) and a tooltip |
| **PM-04** | Mode D icons are never interactive and never carry meaning that exists nowhere else |
| **PM-05** | Where a control is Mode A in one place and Mode B in another, the **icon and the accessible name are identical** in both |

---

## 4. Icon-only is prohibited for

| Category | Why | Examples |
|---|---|---|
| **Destructive or irreversible actions** | A misread icon here costs a customer's device, a payment or a record | Cancel order, void invoice, archive device, remove seller, delete draft |
| **Financial actions** | Money moved by a guessed icon | Post, refund, write off, approve payment, release payout |
| **Approval and authority actions** | Carries personal accountability | Approve, reject, authorise override, sign |
| **Anything with a legal consequence** | Consent, custody, disclosure | Accept terms, confirm handover, submit claim, issue certificate |
| **First-use or low-frequency controls** | The mnemonic has not formed yet | Anything a user meets less than weekly |
| **Any control on `P01`, `P07`, `P09`, `P12`** | Customer, seller, rider and partner audiences include first-time and low-literacy users | All |
| **Any control in a first-run or onboarding flow** | By definition the user has no priors | All |

> **`P09` rider is absolute.** The audience has the shortest content budget in the system
> (`VB-002` R-01, eight words) and the least tolerance for ambiguity. It is tempting to solve the
> budget with icons. **Do not.** A rider guessing between two icons at a customer's door is a
> custody break.

---

## 5. Registered icon-only controls

**This is the complete list.** Any icon-only control not here is a defect.

| Control | Icon | Accessible name | Tooltip | Permitted on |
|---|---|---|---|---|
| Close | ✕ | Close | Close | All |
| Search | 🔍 magnifier | Search | Search | All |
| More actions | ⋯ horizontal ellipsis | More actions | More actions | `P03`, `P06`, `P10` only |
| Sort column | ▲▼ | Sort by *(column)* | Sort ascending / descending | `P03`, `P04`, `P06`, `P08`, `P10` |
| Expand / collapse row | ▸▾ | Expand row / Collapse row | — | `P03`, `P04`, `P06`, `P10` |
| Previous / next page | ‹ › | Previous page / Next page | — | All |
| Help | ? in circle | Help for *(field)* | Help | All |
| Copy to clipboard | ⧉ | Copy *(value)* | Copy | `P03`, `P04`, `P06`, `P08` |
| Refresh | ↻ | Refresh | Refresh | `P03`, `P06`, `P10` |
| Filter | ⧩ funnel | Filter | Filter | `P03`, `P04`, `P06`, `P08`, `P10` |
| Fullscreen | ⤢ | Enter fullscreen / Exit fullscreen | — | `P06` only |
| Scan | ▤ barcode | Scan | Scan | `P02`, `P09`, `P11` |
| Torch | ☀ | Turn torch on / off | — | `P02`, `P09` |
| Call | ☎ | Call *(name)* | — | `P02`, `P09`, `P10` |
| Navigate | ➤ | Navigate to *(address)* | — | `P02`, `P09` |

| # | Rule |
|---|---|
| **IO-01** | **Fifteen controls. This list only shrinks or grows by decision, never by drift** |
| **IO-02** | Accessible names include the object where one exists: "Sort by turnaround time", not "Sort" |
| **IO-03** | Every entry has a minimum 44 × 44 px touch target |
| **IO-04** | `P02` and `P09` entries — scan, torch, call, navigate — are the **only** icon-only controls on those surfaces, and each is high-frequency and taught in `TR-009` / `TR-020` |
| **IO-05** | Adding a control to this list requires Content Design, Localisation and Accessibility agreement, and a `RF-006` entry |

---

## 6. Icon-to-label register

The canonical pairing. **One icon, one meaning, across twelve portals.**

### 6.1 Object icons — what a thing is

| Object | Icon concept | English label | Bengali label | Entity |
|---|---|---|---|---|
| Service order | Document with wrench | Service order | সার্ভিস অর্ডার | `fix.service.order` |
| Job (dispatch) | Pin with person | Job | জব | `fix.dispatch.job` |
| Work order | Bench | Work order | ওয়ার্ক অর্ডার | `fix.work.order` |
| Estimate | Document with currency | Estimate | এস্টিমেট | `fix.estimate` |
| Invoice | Document with lines | Invoice | ইনভয়েস | `account.move` |
| Payment | Banknote | Payment | পেমেন্ট | `fix.cash.movement` |
| Device | Laptop outline | Device | ডিভাইস | `fix.asset` |
| Part | Cog | Part | পার্টস | `fix.part` |
| Customer | Person | Customer | গ্রাহক | `fix.party` |
| Technician | Person with badge | Technician | টেকনিশিয়ান | `fix.technician.profile` |
| Branch | Building | Branch / service centre | সার্ভিস সেন্টার | `fix.branch` |
| Contract | Document with seal | Contract | চুক্তি | `fix.contract` |
| Warranty | Shield | Warranty | ওয়ারেন্টি | `fix.warranty.register` |
| Claim | Shield with arrow | Claim | ক্লেইম | `fix.warranty.claim` |
| Consignment | Box | Consignment | কনসাইনমেন্ট | `fix.consignment` |
| Complaint | Speech bubble with mark | Complaint | অভিযোগ | `fix.complaint` |

> Bengali labels here are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` §7, `T-07`). Any divergence is resolved in favour of `BN-003`.

### 6.2 Action icons — what happens

| Action | Icon concept | Label | Mode | Note |
|---|---|---|---|---|
| Create | Plus | Create *(object)* | A | Never a bare plus for a consequential create |
| Edit | Pencil | Edit | A | |
| Approve | Tick | Approve | **A only** | Prohibited as icon-only |
| Reject | Cross in circle | Reject | **A only** | |
| Cancel | Slash in circle | Cancel *(object)* | **A only** | Distinct from Close ✕ |
| Archive | Box with arrow | Archive | **A only** | **Never a bin icon** — `CG-004` §4.8: archiving is not deleting |
| Assign | Person with arrow | Assign | A | |
| Dispatch | Arrow from building | Dispatch | A | |
| Escalate | Upward chevron | Escalate | A | |
| Print | Printer | Print | A | |
| Download | Downward arrow to line | Download | A | State format and size (`CG-011` LK-04) |
| Upload | Upward arrow from line | Upload | A | |
| Attach | Paperclip | Attach | A | |
| Sync | Circular arrows | Sync | A | Distinct from Refresh ↻ |
| Sign | Pen with line | Sign | **A only** | Legal consequence |
| Scan | Barcode | Scan | B on `P02`/`P09`/`P11` | |

| # | Rule |
|---|---|
| **AI-01** | **No bin or trash icon exists in this system.** `05-02` DM-06 archives business records; it does not delete them. A bin icon promises something the system does not do |
| **AI-02** | Cancel (an order) and Close (a panel) are different icons and different words. Conflating them is the most common icon defect in ERP UI |
| **AI-03** | Sync and Refresh are different: sync reconciles offline state, refresh re-reads the server |
| **AI-04** | Action icons never appear without their verb except where §5 permits |

### 6.3 Status icons

Status semantics, colours and labels are `VB-008`. This register fixes only the **glyph**.

| Severity | Glyph | Never |
|---|---|---|
| Info | i in circle | A light bulb |
| Success | Tick in circle | A thumbs-up |
| Warning | Exclamation in triangle | A yellow face |
| Error | Exclamation in circle | A skull, a bomb, a sad face |
| Blocked | Padlock | A stop sign with text |
| Pending | Clock | An hourglass — it reads as "loading" |
| Offline | Cloud with slash | A broken wire |

| # | Rule |
|---|---|
| **SI-01** | Status icons are **never** the only signal. Icon **and** colour **and** text label (`CG-011` CL-01) |
| **SI-02** | Warning uses a triangle; error uses a circle. The shape difference must survive greyscale, monochrome print and colour-blind vision |
| **SI-03** | No emoji as a status icon anywhere in the product |

---

## 7. Bengali label allowances

**The layout constraint this file exists for.**

### 7.1 Measured expansion

| English label | Chars | Bengali | Chars | Expansion |
|---|---:|---|---:|---:|
| Search | 6 | অনুসন্ধান | 9 | +50% |
| Approve | 7 | অনুমোদন | 7 | 0% |
| Service order | 13 | সার্ভিস অর্ডার | 14 | +8% |
| Customer | 8 | গ্রাহক | 6 | −25% |
| Technician | 10 | টেকনিশিয়ান | 11 | +10% |
| Cancel order | 12 | অর্ডার বাতিল করুন | 18 | +50% |
| Download report | 15 | রিপোর্ট ডাউনলোড করুন | 21 | +40% |

> **Character count understates the problem.** Bengali conjuncts and matras occupy more
> *rendered width per character* than Latin at the same point size, and Bengali needs a larger
> minimum size (`VB-009`). The practical allowance is on **rendered width**, not character count.

### 7.2 Rules

| # | Rule |
|---|---|
| **BL-01** | Icon-with-label containers are sized for the **Bengali** rendered width, plus 10% headroom |
| **BL-02** | Plan for **+40% rendered width** over English as the working assumption. Measure the actual string before shipping |
| **BL-03** | A label that fits in English and truncates in Bengali is a **layout defect**, not a translation problem. Do not shorten the Bengali to fit |
| **BL-04** | Never truncate a label with an ellipsis in a control. Truncation in a *data cell* is acceptable with a tooltip; truncation in a *label* is not |
| **BL-05** | Where the layout genuinely cannot hold the Bengali, the control moves to icon-above-label (two lines) — not to icon-only |
| **BL-06** | Bengali labels never wrap mid-conjunct. Wrapping is at word boundaries only |
| **BL-07** | Toolbar and action-bar layouts are tested at Bengali width before release; this is where breakage concentrates |
| **BL-08** | Icon and label are vertically centred on the **Bengali** line box, which is taller (`VB-009` line height 1.7) |

### 7.3 Layout patterns by available width

| Available width | Pattern | Note |
|---|---|---|
| Comfortable | Icon + label, horizontal | Default |
| Constrained | Icon above label, two lines | Preferred over icon-only |
| Very constrained | Label only, no icon | **Preferred over icon-only** |
| Registered §5 control | Icon only | Only the fifteen |

> **The order matters.** When space runs out, drop the **icon** before the label. The label
> carries the meaning; the icon carries the speed.

---

## 8. Accessibility

| # | Rule | SC |
|---|---|---|
| **AC-01** | Every non-decorative icon has a text alternative | 1.1.1 |
| **AC-02** | Decorative icons are marked decorative and are not announced | 1.1.1 |
| **AC-03** | Icon-only controls have an accessible name naming the action **and** its object | 1.1.1, 2.4.6 |
| **AC-04** | Icons meet 3:1 non-text contrast against their background | **1.4.11** |
| **AC-05** | Meaning is never carried by icon alone, nor by colour alone | 1.4.1 |
| **AC-06** | Touch targets are at least 44 × 44 px | 2.5.5 |
| **AC-07** | Tooltips are reachable by keyboard and dismissible | 1.4.13 |
| **AC-08** | Accessible names are translated; they are user-visible strings (`CG-010` §5) | 3.1.2 |

> **AC-04 has teeth here.** `VB-003` §3 measured `#39B1DF` at **2.46:1** on white. **A brand-blue
> icon on a white background fails SC 1.4.11.** Icons use `#495057` (8.18:1), `#1E5F8A` (6.86:1),
> or a `VB-008` semantic colour that passes — never the primary brand blue on light.

---

## 9. Do and do not

| Do not | Do |
|---|---|
| Use a bin icon for archive | Use a box-with-arrow, labelled "Archive" |
| Use ✕ for "cancel order" | ✕ is Close. Cancel order has its own icon and label |
| Ship an icon-only Approve button | Approve is always Mode A |
| Use an icon-only control on `P09` | Only the four registered rider controls |
| Size a toolbar to the English label | Size to the Bengali, plus 10% |
| Shorten the Bengali to fit | Widen the container or go two-line |
| Use `#39B1DF` for an icon on white | 2.46:1 fails. Use `#495057` or `#1E5F8A` |
| Use an emoji as a status icon | Use the registered glyph |
| Use a hourglass for "pending" | Use a clock; hourglass reads as loading |
| Add a new icon meaning locally | Register it here first |

---

## 10. Adding an icon

| Step | Action | Who |
|---|---|---|
| 1 | Confirm no registered icon already carries the meaning | Design System |
| 2 | Confirm the label exists in `CG-004` and `BN-003` | Content Design + Localisation |
| 3 | Design the glyph to `MM-004` | Design System |
| 4 | Check 3:1 non-text contrast in all themes | Accessibility |
| 5 | Measure the Bengali label width and confirm the layout holds | Localisation |
| 6 | Register here — object, action or status — with its mode | Design System |
| 7 | Log in `RF-006` | Content Lead |

---

## 11. Dependencies

| Depends on | Why |
|---|---|
| `MM-004` Icon Set Requirements | The visual production specification |
| `VB-008` | Status colour and label semantics |
| `VB-003` §3 | Contrast constraints on icon colour |
| `VB-009` | Bengali line height and minimum sizes affecting alignment |
| `CG-004` | The approved labels icons pair with |
| `BN-003` | The authoritative Bengali labels |
| `CG-011` | Accessibility obligations |

---

## 12. Enforcement

| Check | Mechanism | When |
|---|---|---|
| Icon-only control not in §5 | Automated component lint | Every commit |
| Icon without accessible name | Automated | Every commit |
| Icon contrast below 3:1 | Automated token audit | Every design-system release |
| Bin/trash icon present anywhere | Automated | Every commit |
| Bengali label truncation | Visual regression at Bengali width | Every release |
| Emoji used as an icon | Automated | Every commit |
| Touch target below 44px | Automated | Every release |
| One icon, one meaning | Register review | Every wave audit |

---

## 13. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per design-system release |
| Out-of-cycle trigger | A new icon; a Bengali truncation defect; an accessibility finding |
| Owner | Design System Lead |
| Bengali counterpart | `VB-007_Iconography_and_Label_Pairing_Register_BN.md` — required, not yet written |
| Open dependency | `BN-003` — §6 Bengali labels are indicative until it exists |

---

## 14. Related documents

| Document | Relationship |
|---|---|
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](VB-003_Brand_Application_in_Enterprise_UI.md) | Contrast constraints |
| [`VB-006_Design_System_Content_Standards.md`](VB-006_Design_System_Content_Standards.md) | Components these icons sit in |
| [`VB-008_Status_Colour_and_Label_Semantics_Register.md`](VB-008_Status_Colour_and_Label_Semantics_Register.md) | Status semantics |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](VB-009_Bengali_Typography_and_Brand_Standard.md) | Bengali metrics |
| [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | Approved labels |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | §8 |
| `MM-004` Icon Set Requirements | Visual production |
| `UI-010` Accessibility Text Library | Accessible names at scale |
| `BN-003` Bilingual Terminology Glossary | Authoritative Bengali labels |

---

## 15. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Four pairing modes, seven icon-only prohibition categories, fifteen registered icon-only controls, object/action/status icon register, Bengali width allowances with the drop-icon-before-label rule, accessibility including the brand-blue contrast constraint | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Icon-only permitted set is closed and enumerated
- [x] Prohibition categories cover destructive, financial, approval, legal, low-frequency and external-audience cases
- [x] Bengali allowance stated as rendered width with a working assumption and a measurement requirement
- [x] The drop-icon-before-label rule stated explicitly
- [x] Brand-blue contrast constraint carried through from `VB-003` §3
- [x] No bin icon rule traced to `05-02` DM-06
- [x] All internal links resolve
- [ ] Bengali counterpart written and signed off in context — **outstanding; blocks `Approved`**
- [ ] `BN-003` labels confirmed — **outstanding; §6 indicative until then**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
