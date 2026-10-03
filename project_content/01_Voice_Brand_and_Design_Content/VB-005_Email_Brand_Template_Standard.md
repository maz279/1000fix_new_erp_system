---
id: VB-005
title: Email Brand Template Standard
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Brand Lead
author: Brand with Platform Engineering and Content Design
reviewers: [Content Design Lead, Localisation Lead, Platform Engineering, Accessibility reviewer]
approver: Content Design Lead
content_class: D
purpose: >
  Defines the master email shell for the six NT email libraries — dark-mode behaviour, Bengali
  font fallback, plain-text parity and client rendering limits. Email clients in Bangladesh
  render Bengali web fonts inconsistently and Outlook renders through the Word engine; the
  fallback must be designed, not discovered after 250,000 customers receive a broken message.
traces_to: [NT-009, NT-010, NT-011, NT-012, NT-013, NT-014, VB-003, VB-009, CG-011, MM-011]
priority: P2
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000_fix_corporate_website project_content CB-001 Brand Guidelines Document v1.0 §3 colour, §4 typography, §7 digital guidelines
    verified: 2026-08-15
    class: P1
  - source: Email client rendering behaviour — Outlook desktop renders via the Word HTML engine; Gmail sanitises CSS and renders in its own DOM; custom web fonts are reliably supported only in Apple Mail
    verified: 2026-08-15
    class: P3
    note: Industry-reported behaviour, corroborated across multiple independent technical sources. Converts to P1 (direct observation) on completion of the §13 baseline client testing, which is mandatory before any template ships.
  - source: Dark mode handling — Outlook applies data-ogsc attributes; Apple Mail honours prefers-color-scheme; Gmail applies partial or no inversion depending on client
    verified: 2026-08-15
    class: P3
    note: As above. No template may be approved on the P3 evidence alone.
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 localisation standards
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# VB-005 — Email Brand Template Standard

> **Email is the least controllable surface the ERP has.** Outlook desktop renders through the
> Microsoft Word HTML engine. Gmail renders inside its own DOM and strips CSS it dislikes.
> Custom web fonts load reliably only in Apple Mail. Dark mode is applied three different ways
> by three different clients, none of which asks permission.
>
> **Design for the worst renderer and let the best ones look better.**

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | The visual and structural shell for every email the ERP sends |
| **What it does not govern** | Message content and templates (`NT-009`…`NT-014`); the notification strategy (`NT-001`); asset production specs (`MM-011`) |
| **What breaks without it** | Six template libraries, six shells, and a Bengali customer receiving a message in a substituted font that renders conjuncts as boxes |

---

## 2. Scope

**In scope:** transactional, operational and lifecycle email from the ERP to customers,
corporate users, vendors, sellers, brand partners and employees.

**Out of scope:** marketing email from the website programme; SMS, WhatsApp, push and in-app
(`NT` category); the email brand shell used by Marketing, which retains `CB-001` §7.

---

## 3. Client baseline

Design decisions follow from what actually renders. This is the assumed baseline.

| Client | Engine | Web fonts | Dark mode | Design consequence |
|---|---|:--:|---|---|
| **Outlook desktop (Windows)** | Word HTML | ❌ | Partial inversion, adds `data-ogsc` | **The constraining client.** Tables, no flexbox, no grid, no `max-width` reliability |
| Outlook.com / new Outlook | Own | ❌ | Partial inversion | As above for layout |
| **Gmail web and app** | Own DOM, CSS sanitised | ❌ | Varies by platform; often no-op | No `<style>` reliability on some paths; inline critical CSS |
| **Apple Mail / iOS Mail** | WebKit | ✅ | Honours `prefers-color-scheme` | The only client where the brand can render fully |
| Android Gmail | Own | ❌ | Varies | Bengali falls back to the system font |
| Yahoo / other | Mixed | ❌ | Varies | Assume Outlook-level capability |

| # | Rule |
|---|---|
| **CB-01** | **Table-based layout.** No flexbox, no grid, no CSS positioning |
| **CB-02** | **Inline the critical CSS.** A `<style>` block is an enhancement, never the only carrier |
| **CB-03** | Assume no web font. Design at the fallback and treat the web font as a bonus |
| **CB-04** | Assume dark mode may be applied without permission, and design so the result is legible either way |
| **CB-05** | Every email is tested on Outlook desktop, Gmail web, Gmail Android and Apple Mail iOS before release |

---

## 4. The master shell

```
┌────────────────────────────────────────────┐
│              (preheader, hidden)            │  Preview text — 40–90 chars
├────────────────────────────────────────────┤
│  ▌ 1000FiX          [logo 140px]           │  Header — 64px, #1E5F8A rule
├────────────────────────────────────────────┤
│                                            │
│  Subject restated as an H1                 │  Body — 600px max width
│                                            │
│  One-sentence summary of what happened.    │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │ KEY FACTS TABLE                      │  │  Fact block
│  │ Reference    SR-2026-114882          │  │
│  │ Device       Dell Latitude 5420      │  │
│  │ Amount       BDT 3,200.00            │  │
│  └──────────────────────────────────────┘  │
│                                            │
│      [ PRIMARY ACTION ]                    │  Single CTA, bulletproof button
│                                            │
│  What happens next, in one or two lines.   │
│                                            │
├────────────────────────────────────────────┤
│  Need help? Hotline 16743                  │  Support block
├────────────────────────────────────────────┤
│  1000FiX Services Limited                  │  Footer
│  Address · why you received this ·         │
│  manage preferences · unsubscribe*         │
└────────────────────────────────────────────┘
```

\* Unsubscribe appears on lifecycle and marketing email only. **Transactional email carries a
"manage preferences" link but no unsubscribe** — the recipient cannot opt out of a payment
receipt (`NT-002`).

| Zone | Rule |
|---|---|
| **Preheader** | 40–90 characters, hidden, never left as "View this email in your browser". It is the second thing in the inbox after the subject |
| **Header** | 64px tall, logo 140px wide, 2px `#1E5F8A` rule beneath. No image-only header |
| **Body** | 600px maximum width, single column, 24px padding |
| **Fact block** | The transactional facts as a two-column table. **This is the part that gets screenshotted and forwarded** |
| **CTA** | **One primary action per email.** Bulletproof button (§6) |
| **Support block** | Hotline 16743 always. It is the fallback when the link fails |
| **Footer** | Legal entity, address, why they received it, preference link |

| # | Rule |
|---|---|
| **SH-01** | **One email, one action.** A second CTA halves the first |
| **SH-02** | The email is comprehensible with **images disabled**. Many clients block images by default |
| **SH-03** | No content exists only inside an image (`CG-011` AT-07) |
| **SH-04** | Single column. Multi-column collapses unpredictably in Outlook |
| **SH-05** | The transactional fact is in the fact block, not in prose. It is what the recipient screenshots |

---

## 5. Colour in email

Constrained by `VB-003` §3 contrast findings **and** by dark-mode inversion.

| Element | Light | Dark | Note |
|---|---|---|---|
| Page background | `#F8F9FA` | `#1A1D20` | Never pure white — inversion artefacts are worse |
| Card background | `#FFFFFF` | `#212529` | |
| Body text | `#212529` | `#E9ECEF` | 15.4:1 / 12.6:1 |
| Secondary text | `#495057` | `#ADB5BD` | 8.2:1 |
| **Link text** | `#1E5F8A` | `#7FC4E8` | **Never `#39B1DF`** — 2.46:1 fails (`VB-003` BC-01) |
| Header rule | `#1E5F8A` | `#39B1DF` | Brand blue is safe as a rule on dark |
| Button fill | `#1E5F8A` | `#39B1DF` | |
| Button text | `#FFFFFF` on `#1E5F8A` (6.9:1) | `#212529` on `#39B1DF` (6.3:1) | **Text colour flips with the theme** |
| Success accent | `#28A745` fill, `#212529` text | as light | |
| Warning accent | `#FFC107` fill, `#212529` text | as light | Yellow text is never used (1.63:1) |
| Error accent | `#DC3545` fill, `#FFFFFF` text | as light | |
| Divider | `#E9ECEF` | `#343A40` | |

| # | Rule |
|---|---|
| **CL-01** | **Never use `#39B1DF` for text on a light background.** It fails all text contrast |
| **CL-02** | Every colour pair in this table is stated with its measured ratio. A new pair is not introduced without measuring it |
| **CL-03** | Set both `background-color` and `color` explicitly on every element. Setting only one produces black-on-black under inversion |
| **CL-04** | Use `@media (prefers-color-scheme: dark)` with `!important` for Apple Mail |
| **CL-05** | Provide `data-ogsc` / `data-ogsb` overrides for Outlook |
| **CL-06** | Accept that Gmail may not honour either. The light palette must survive naive inversion — which is why the background is `#F8F9FA` rather than `#FFFFFF` |
| **CL-07** | The logo ships in two versions: full colour for light, reversed for dark, swapped by media query with the light version as the fallback |

---

## 6. Buttons

Outlook does not render CSS-styled anchors reliably. Use the VML "bulletproof" pattern.

| Property | Value |
|---|---|
| Height | 44px minimum — a touch target |
| Padding | 14px vertical, 28px horizontal |
| Corner radius | 4px |
| Fill | `#1E5F8A` light, `#39B1DF` dark |
| Text | 16px, 600 weight, `#FFFFFF` light, `#212529` dark |
| Width | Auto, maximum 320px; full width below 480px |
| Label | A verb phrase, ≤ 4 words (`VB-006`) |

| # | Rule |
|---|---|
| **BT-01** | VML fallback for Outlook, standard anchor for everything else |
| **BT-02** | The destination URL appears in plain text beneath the button in the plain-text part, and in the support block where the action is critical |
| **BT-03** | A button is never the only route. A recipient who cannot click still has the hotline and the reference |
| **BT-04** | Button label describes the action, never "Click here" (`CG-011` LK-02) |

---

## 7. Typography and the Bengali fallback

**The hardest problem in this file.** 22 of the 26 `NT` files are bilingual; the email libraries
`NT-009`…`NT-014` reach customers, employees and sellers in Bengali.

### 7.1 The stack

```css
/* Latin */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
             Roboto, Helvetica, Arial, sans-serif;

/* Bengali */
font-family: 'Hind Siliguri', 'Noto Sans Bengali', 'Nirmala UI',
             'Vrinda', 'SolaimanLipi', sans-serif;
```

| Position | Font | Where it comes from | Renders? |
|---|---|---|---|
| 1 | **Hind Siliguri** | Web font; Apple Mail only | Best. UI-designed, 820 glyphs, full conjunct coverage |
| 2 | **Noto Sans Bengali** | **Android system default** | Good. The realistic fallback for most Bangladeshi recipients |
| 3 | Nirmala UI | Windows system | Acceptable. The Outlook desktop fallback |
| 4 | Vrinda | Older Windows | Poor conjuncts; legible |
| 5 | SolaimanLipi | Commonly installed in Bangladesh | Good where present |
| 6 | `sans-serif` | Anything | May render conjuncts as boxes |

### 7.2 Rules

| # | Rule |
|---|---|
| **BF-01** | **Design at position 2, not position 1.** Noto Sans Bengali on Android is the realistic majority case |
| **BF-02** | Hind Siliguri and Noto Sans Bengali have different metrics. Line height is set so **both** fit — `1.7` minimum, per the website design-system reference and `VB-009` |
| **BF-03** | Never set a fixed pixel height on a container holding Bengali. Let it grow |
| **BF-04** | Bengali body text is **16px minimum in email**, one step above the English 15px |
| **BF-05** | Bengali is never set in an image to guarantee the font. It breaks `CG-011` AT-07 and image blocking |
| **BF-06** | Every bilingual template is **rendered and inspected** on Gmail Android and Outlook desktop before release. Conjunct breakage is only visible by looking |
| **BF-07** | Where the Bengali subject line risks truncation, the essential fact goes **first** |

### 7.3 Type scale

| Element | English | Bengali | Weight | Line height |
|---|---:|---:|---:|---:|
| H1 (subject restated) | 22px | 24px | 700 | 1.3 / **1.4** |
| H2 | 18px | 20px | 600 | 1.35 / 1.45 |
| Body | 15px | **16px** | 400 | 1.6 / **1.7** |
| Fact table | 15px | 16px | 400/600 | 1.5 / 1.6 |
| Caption / footer | 13px | 14px | 400 | 1.5 / 1.6 |
| Button | 16px | 16px | 600 | 1.2 |

**Nothing below 13px English or 14px Bengali.**

---

## 8. Plain-text parity

Every HTML email ships a plain-text alternative. It is not a courtesy; it is what renders in
low-bandwidth clients, accessibility tools and some corporate mail filters.

| # | Rule |
|---|---|
| **PT-01** | The plain-text part carries **the same facts** as the HTML. Never a stub saying "view in browser" |
| **PT-02** | The CTA appears as a full URL on its own line |
| **PT-03** | The fact block appears as `Label: value` lines |
| **PT-04** | Hotline 16743 appears in every plain-text part |
| **PT-05** | Bengali plain text is UTF-8 and is checked for mojibake in at least one non-Unicode-native client |
| **PT-06** | Maximum 72 characters per line for English; Bengali is not hard-wrapped, which breaks conjuncts |

---

## 9. Accessibility

`CG-011` applies to email in full.

| # | Rule |
|---|---|
| **AC-01** | `lang` attribute set on the document; language changes marked (`CG-011` BA-02) |
| **AC-02** | Every image has alt text; decorative images have empty alt |
| **AC-03** | The logo's alt text is "1000FiX Services" |
| **AC-04** | Link text describes the destination (`CG-011` LK-01) |
| **AC-05** | Real headings, in order, not styled paragraphs |
| **AC-06** | Fact block is a real table with header cells |
| **AC-07** | Colour is never the only signal — status is stated in words |
| **AC-08** | Minimum 44px touch targets |
| **AC-09** | Every colour pair meets AA at its stated size (§5) |

---

## 10. Deliverability constraints on design

Design choices affect whether the email arrives at all.

| # | Rule |
|---|---|
| **DL-01** | Total HTML under **102 KB**. Gmail clips above this, hiding the footer and the unsubscribe link |
| **DL-02** | Images hosted, not embedded. Total image weight under 200 KB |
| **DL-03** | Image-to-text ratio no higher than 40% |
| **DL-04** | No background images carrying essential content |
| **DL-05** | Transactional and marketing send from separate subdomains and IPs, so marketing reputation cannot affect a password reset |
| **DL-06** | SPF, DKIM and DMARC configured on every sending domain |
| **DL-07** | The `From` name is consistent — recipients filter on it |

---

## 11. Do and do not

| Do not | Do |
|---|---|
| Use `#39B1DF` for link or body text | Use `#1E5F8A` light, `#7FC4E8` dark |
| Put the reference number only in an image | Put it in the fact block as text |
| Assume Hind Siliguri loads | Design at Noto Sans Bengali |
| Set a fixed height on a Bengali container | Let it grow |
| Send HTML without a plain-text part | Always ship both, with the same facts |
| Use two CTAs | One primary action |
| Exceed 102 KB | Trim; Gmail clips |
| Set only `color` and not `background-color` | Set both, or dark mode makes it invisible |
| Test only in Apple Mail | Test Outlook desktop, Gmail web, Gmail Android, Apple Mail iOS |
| Include unsubscribe on a payment receipt | Include "manage preferences" only |

---

## 12. Dependencies

| Depends on | Why |
|---|---|
| `VB-003` §3 | Contrast findings that exclude `#39B1DF` from text |
| `VB-009` | Bengali type sizes and line heights |
| `NT-001` | Which events send email at all |
| `NT-002` | Transactional versus marketing, which decides the footer |
| `MM-011` | Asset production specification implementing this |
| `CG-011` | Accessibility obligations |

---

## 13. Enforcement

| Check | Mechanism | When |
|---|---|---|
| Rendering across the four baseline clients | Email rendering test service + manual | Every template change |
| Dark mode in all three modes | Rendering test | Every template change |
| Bengali conjunct rendering, Gmail Android and Outlook desktop | **Manual visual inspection** | Every bilingual template |
| HTML under 102 KB | Automated | Every render |
| Plain-text part present and factually equal | Automated presence, manual parity | Every template |
| Contrast of every colour pair | Automated | Every shell change |
| Alt text on every image | Automated | Every template |
| Single CTA | Manual, gate G1 | Every template |

---

## 14. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave |
| Out-of-cycle trigger | A client rendering change; a deliverability incident; a `CB-001` revision; a new email library |
| Owner | Brand Lead with Platform Engineering |
| Test account set | One account per baseline client, held by Platform Engineering |

---

## 15. Related documents

| Document | Relationship |
|---|---|
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](VB-003_Brand_Application_in_Enterprise_UI.md) | Contrast findings |
| [`VB-004_Print_and_PDF_Brand_Template_Standard.md`](VB-004_Print_and_PDF_Brand_Template_Standard.md) | Print counterpart |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](VB-009_Bengali_Typography_and_Brand_Standard.md) | Bengali type |
| [`VB-006_Design_System_Content_Standards.md`](VB-006_Design_System_Content_Standards.md) | Button label rules |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | §9 |
| `NT-009` … `NT-014` | The six email libraries using this shell |
| `NT-002` Notification Preference and Consent Copy | Footer and unsubscribe rules |
| `MM-011` Email and HTML Asset Specification | Production specification |

---

## 16. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Client baseline with Outlook as the constraining renderer, master shell, dark-mode colour pairs with measured ratios, bulletproof buttons, six-position Bengali font stack designed at the Android fallback, plain-text parity, deliverability constraints | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Client baseline stated, with the constraining client named
- [x] Every colour pair carries its measured contrast ratio
- [x] Dark mode addressed for all three client behaviours
- [x] Bengali fallback designed at the realistic position, not the ideal one
- [x] Plain-text parity required with factual equality
- [x] Deliverability constraints included as design constraints
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; the **templates** using this shell are bilingual
- [ ] Named approver recorded — **pending**
- [ ] Client test account set established — **outstanding, Platform Engineering**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
