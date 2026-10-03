---
id: MM-011
title: Email and HTML Asset Specification
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Brand Lead with Platform Engineering
author: Brand with Platform Engineering, Content Design and Localisation
reviewers: [Brand Lead, Chief Technology Officer, Content Design Lead, Localisation Lead, Accessibility reviewer, Chief Data Officer, Programme Content Lead]
approver: Content Design Lead with Brand Lead
content_class: D
purpose: >
  The production specification for every image, markup partial and font decision that goes into an
  ERP email — the asset half of the shell VB-005 designs. Email is the least controllable surface
  the programme has: Outlook renders through the Word HTML engine, Gmail sanitises CSS and clips
  above 102 KB, custom fonts load reliably only in Apple Mail, and three clients apply dark mode
  three different ways without asking. VB-005 decides what the email looks like; nothing states
  what the assets inside it must be, how they are hosted, or what happens when an image URL in a
  three-year-old payment receipt stops resolving. Six template libraries reaching customers,
  employees, vendors, sellers and brand partners will otherwise each solve it differently.
traces_to: [VB-005, VB-003, VB-006, VB-009, NT-001, NT-002, NT-003, NT-009, NT-010, NT-011, NT-012, NT-013, NT-014, NT-025, NT-026, CG-003, CG-008, CG-010, CG-011, CG-012, BN-006, BN-014, CM-009, CM-005, LG-008, LG-011, MM-001, MM-004, MM-005, MM-009, MM-010, MM-012, TS-016, M24, 04-00 PS-03, 04-00 PS-04, 05-06 §9, 05-06 NFR-073]
priority: P2
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-005_Email_Brand_Template_Standard.md §3 client baseline and CB-01…CB-05, §4 the master shell and SH-01…SH-05, §5 colour with dark-mode pairs and CL-01…CL-07, §6 bulletproof buttons BT-01…BT-04, §7 the six-position Bengali font stack and BF-01…BF-07, §8 plain-text parity PT-01…PT-06, §9 accessibility AC-01…AC-09, §10 deliverability DL-01…DL-07, §13 enforcement
    verified: 2026-08-18
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md §2.1 the six-rank Bengali font stack, TF-04 email designs at rank 2, BR-06 Bengali is never rendered as an image; §3 email Bengali body floor 16px
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md §4 AT-01…AT-08 text alternatives, AT-07 text in an image is duplicated in the alternative, LK-01…LK-05 link text, CL-01 colour is never the only signal
    verified: 2026-08-18
    class: P1
  - source: Email client rendering behaviour as at 2026 — Outlook desktop on Windows renders through the Microsoft Word HTML engine and supports neither web fonts nor modern layout; Gmail renders in its own DOM and sanitises CSS; custom web fonts load reliably only in Apple Mail; dark mode is applied by Outlook through data-ogsc attributes, honoured by Apple Mail through prefers-color-scheme, and applied partially or not at all by Gmail depending on platform; Gmail clips messages above roughly 102 KB
    verified: 2026-08-18
    class: P3
    note: Industry-reported behaviour carried forward from VB-005, which classifies the same facts as P3 and states that no template may be approved on P3 evidence alone. Converts to P1 on completion of the §4.9 client test matrix, which is mandatory before any asset ships.
  - source: Modern raster format support — WebP and AVIF support is effectively universal in browsers but is not reliable across email clients, and the Word rendering engine used by Outlook desktop does not support them
    verified: 2026-08-18
    class: P3
    note: As above. This is why §4.3 excludes both formats from email while MM-001 §4.4 makes them the primary web chain.
supersedes: none
review_due: 2027-02-18
---

# Email and HTML Asset Specification

| Item | Value |
|---|---|
| Governs | Every image, markup partial, font decision and hosted asset used in ERP email |
| Shell authority | [`VB-005`](../01_Voice_Brand_and_Design_Content/VB-005_Email_Brand_Template_Standard.md) — **this file produces the assets `VB-005` designs a home for** |
| Consumers | The six `NT` email libraries — `NT-009` … `NT-014` — plus [`CM-009`](../16_Change_Management_and_Comms/CM-009_Internal_Newsletter_and_Update_Template.md) and [`CM-005`](../16_Change_Management_and_Comms/CM-005_Wave_Launch_Communication_Kit.md) |
| Audience | Platform Engineering, email template implementers, Brand, Localisation |
| Language | English — the specification. **22 of the 26 `NT` files are bilingual** (`CG-010` §3.2) |
| Wave | W2 · Months 5–8 (`06-01` §3) — **and `CM-005` records a W1 need. See `O-01`** |
| Content class | **D** — user-facing (`CG-002` §4.1) |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. The `CG-009` `MM` **deliverable specification table** is §4.8.
> §7 Open Items added per category convention.

---

## 1. Purpose

`VB-005` §12 names this file as *"asset production specification implementing this"*, and §1 draws
the boundary from its own side: it governs the shell and *"does not govern … asset production
specs (`MM-011`)"*.

Its opening position is the constraint everything here follows from:

> **"Email is the least controllable surface the ERP has … Design for the worst renderer and let
> the best ones look better."**

**What a template implementer still does not know:**

| Absent | Consequence |
|---|---|
| Image formats permitted in email | An AVIF logo that renders in the designer's browser and as a broken-image icon in Outlook |
| Density and dimension rules | A 140 px logo supplied at 140 px, blurred on every retina phone |
| Dark-mode asset variants | `CL-07` requires two logos swapped by media query; nobody produced the reversed one |
| A Bengali font decision in production terms | Bengali set in an image to guarantee the face — which `VB-009` `BR-06` and `VB-005` `BF-05` both prohibit |
| A hosting and permanence rule | **A payment receipt from 2026 whose logo URL 404s in 2029** |
| Weight budgets per asset | `DL-01`'s 102 KB clip reached by the header image alone, hiding the footer and the preference link |
| A partial and build contract | Six libraries, six shells — the exact failure `VB-005` §1 says it exists to prevent |

**Consequence of absence (`CP-03`).** Six template libraries reaching 250,000+ customers a month,
500+ employees, the vendor base, 500–2,000 sellers and 17+ brand partners, each solving image
format, dark mode, Bengali and hosting separately — and a transactional email estate whose assets
decay silently, because **nobody ever looks at an email they sent three years ago.**

**What this file is not.** It is not the shell (`VB-005`), not the message content
(`NT-009`…`NT-014`), not the notification strategy or consent (`NT-001`, `NT-002`), and not the
print specification (`MM-010`).

---

## 2. Scope

**In scope.** The email asset inventory; image formats, dimensions and density; dark-mode asset
variants; the Bengali font strategy in production terms; the image-off and alt-text contract;
weight and deliverability budgets; hosting, caching and **URL permanence**; the HTML partial kit
and build; the client test matrix; the deliverable specification; and rules `EA-01`…`EA-30`.

**Out of scope.**

| Subject | Owned by |
|---|---|
| The shell, zones, colour pairs, buttons, plain-text parity, deliverability policy | [`VB-005`](../01_Voice_Brand_and_Design_Content/VB-005_Email_Brand_Template_Standard.md) |
| Message content and the six libraries | [`NT-009`](../04_Notification_and_Messaging/04C_Email/NT-009_Email_Template_Library_Customer_Transactional.md) … [`NT-014`](../04_Notification_and_Messaging/04C_Email/NT-014_Email_Template_Library_Internal_and_HR.md) |
| Which events send email at all | [`NT-001`](../04_Notification_and_Messaging/NT-001_Notification_Strategy_and_Event_Channel_Matrix.md) |
| Transactional versus marketing, and the footer that follows | [`NT-002`](../04_Notification_and_Messaging/NT-002_Notification_Preference_and_Consent_Copy.md) |
| Quiet hours, throttling and frequency | [`NT-003`](../04_Notification_and_Messaging/NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md) |
| Failure and fallback copy | [`NT-025`](../04_Notification_and_Messaging/NT-025_Notification_Failure_and_Fallback_Copy.md) |
| Template governance and change log | [`NT-026`](../04_Notification_and_Messaging/NT-026_Message_Template_Governance_and_Change_Log.md) |
| The Bengali message pack | [`BN-014`](../11_Localisation_Bengali/BN-014_Bengali_Notification_and_SMS_Pack.md) |
| Tracking pixels and cookie-equivalent technologies | [`LG-011`](../10_Legal_Policy_and_Compliance/LG-011_Cookie_and_Tracking_Policy.md) — **see `EA-27`** |
| Print and PDF attachments | [`MM-010`](MM-010_PDF_and_Print_Template_Design_Specification.md); `DT-001` §6.3 governs the attachment, `VB-005` governs the carrying email |
| Format, metadata, acceptance in general | [`MM-001`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) |
| Hosting naming, versioning, retirement | [`MM-012`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) |

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **Email template implementer** | The asset and markup contract to build against | Before implementation |
| **Platform Engineering** | Hosting, CDN, cache, permanence, the build and lint | Continuously |
| **Brand** | That the shell survives the clients | At each library release |
| **Content Design** | What the copy can rely on being visible when images are off | Per template |
| **Localisation Lead** | §4.4 — the Bengali position, and why no Bengali is ever an image | At review |
| **Accessibility reviewer** | §4.5 | At acceptance |
| **Chief Data Officer** | `EA-27` — the tracking-pixel position | At review |

---

## 4. Content

### 4.1 The asset inventory

**Deliberately short.** `VB-005` `SH-02` requires the email to be comprehensible with images
disabled, and `SH-03` prohibits content existing only inside an image — which means **almost
nothing in an ERP email needs to be an image at all.**

| # | Asset | Required? | Notes |
|---:|---|---|---|
| **E1** | **Logo — light theme** | ✔ | 140 px wide (`VB-005` §4) |
| **E2** | **Logo — dark theme, reversed** | ✔ | `CL-07`; **the one most often missing** |
| **E3** | Status or severity icon | Optional | From `MM-004` at PNG @2×; **paired with the word, never alone** |
| **E4** | Footer marks — legal entity, ISO, hotline | Optional | Text preferred (`EA-04`) |
| **E5** | Payment-method marks | Optional | Only in checkout-adjacent email; **co-branding follows `VB-003` `LG-06`** |
| **E6** | Illustration | **Rare** | Lifecycle and campaign email only; never transactional |
| **E7** | Photography | **Rare** | `CM-009` newsletter and campaign only; never transactional |
| **E8** | **Spacer, background and decorative images** | **✖ Prohibited** | `EA-05` |
| **E9** | **Any image containing text** | **✖ Prohibited** | `EA-06` |
| **E10** | **Animated GIF** | **✖ by default** | `EA-07` |

| # | Rule |
|---|---|
| **EA-01** | **Every image is optional to comprehension.** If removing an image removes information, the information is in the wrong place (`VB-005` `SH-02`, `SH-03`) |
| **EA-02** | **The fact block is never an image.** `VB-005` `SH-05` calls it *"the part that gets screenshotted and forwarded"* — it is a real table, in real text, in the plain-text part too |
| **EA-03** | **A transactional email carries at most two images**: the logo and, where genuinely needed, one status icon. Nothing else |
| **EA-04** | **Footer marks are text.** A row of certification logos is 40 KB of the 102 KB budget for information a line of text carries better |
| **EA-05** | **No spacer images, no background images carrying content, no decorative imagery in transactional email** (`VB-005` `DL-04`) |
| **EA-06** | **No image contains text** — WCAG SC 1.4.5, `CG-011` `AT-07`, `VB-005` `SH-03`. **This includes the logo's wordmark, which is a logo and therefore the permitted exception** (`MM-001` `RA-04`) |
| **EA-07** | **Animated GIFs are used only where motion is the message**, never in transactional email, and **the first frame must carry the whole meaning** — Outlook desktop shows the first frame only |

### 4.2 Dimensions and density

| Asset | Display size | **Supplied at** | Rule |
|---|---|---|---|
| Logo light / dark | 140 × 40 px | **280 × 80 px (@2×)** | `EA-08` |
| Status icon | 24 × 24 px | 48 × 48 px | |
| Footer mark | ≤ 90 px wide | @2× | |
| Illustration (lifecycle only) | ≤ 552 px wide | @2× | 600 px body minus 24 px padding each side |
| Photograph (newsletter only) | ≤ 552 px wide | @2× | |

| # | Rule |
|---|---|
| **EA-08** | **Every image is supplied at 2× and displayed at 1×, with `width` and `height` set explicitly in HTML attributes** — not only in CSS, which Outlook's Word engine ignores |
| **EA-09** | **No image exceeds 552 px displayed width.** `VB-005` §4 sets a 600 px body with 24 px padding; a wider image forces a horizontal scroll in Outlook |
| **EA-10** | **@3× is not supplied for email.** The weight cost exceeds the visible benefit at these display sizes, and `DL-01`'s clip threshold is unforgiving |
| **EA-11** | **Images are never resized by the client.** A supplied dimension that does not match the declared display size renders differently in each engine |

### 4.3 Formats — and why email is the exception

`MM-001` §4.4 makes **AVIF → WebP → JPEG/PNG** the web delivery chain. **Email is excluded from
it**, and the exclusion is stated here so it is not read as an oversight.

| Format | Email | Reason |
|---|---|---|
| **PNG-24** | **✔ Default for logos, icons, line art** | Universal support; alpha channel |
| **JPEG** | ✔ Photography only | Universal support |
| **GIF** | Conditional (`EA-07`) | Only client-safe animation format |
| **WebP** | **✖** | Not reliable across clients; unsupported by the Word engine |
| **AVIF** | **✖** | As above, more so |
| **SVG** | **✖** | Blocked or stripped by most clients, including Gmail |
| **Base64-embedded images** | **✖** | Inflates HTML against `DL-01`'s 102 KB clip; blocked by several clients |

| # | Rule |
|---|---|
| **EA-12** | **PNG-24 is the default email image format and SVG is never used**, which is the exact inverse of every other surface in this programme (`MM-001` §4.4, `MM-004` `IC-32`). **The inversion is deliberate and is stated so a later implementer does not "correct" it** |
| **EA-13** | **Images are hosted and referenced by URL, never embedded** (`VB-005` `DL-02`) |
| **EA-14** | **Alpha-channel PNGs are checked against both themes.** A transparent logo that looks correct on white becomes invisible when a client inverts the background — the most common dark-mode asset failure |

### 4.4 Dark mode and the Bengali font strategy

#### 4.4.1 Dark-mode assets

| # | Rule |
|---|---|
| **EA-15** | **Two logo assets ship: full colour for light, reversed for dark**, swapped by `prefers-color-scheme` media query **with the light version as the fallback** (`VB-005` `CL-07`). A client that honours neither gets the light logo, which must therefore be legible on a dark background too — **or the logo sits on its own solid light-background block** |
| **EA-16** | **The reversed asset is authored, not generated by inversion** (`MM-001` `CS-08`) |
| **EA-17** | **Every element sets both `background-color` and `color` explicitly** (`VB-005` `CL-03`). Setting only one produces black-on-black under naive inversion |
| **EA-18** | **The light palette must survive naive inversion** — which is why `VB-005` §5 sets the page background to `#F8F9FA` rather than `#FFFFFF`. **Assets are checked under forced inversion, not only under the media query** |
| **EA-19** | **Icons and marks are supplied in both themes or in a theme-neutral form.** A `#212529` glyph on a transparent background disappears in dark mode; `MM-004` `IC-20`'s `currentColor` approach is unavailable here, because email images cannot inherit |

#### 4.4.2 Bengali — a font problem with no image solution

`VB-009` §2.1 ranks six Bengali faces; `VB-005` `BF-01` designs at **rank 2, Noto Sans Bengali**,
the Android system default, because *"custom fonts load reliably only in Apple Mail."*

| # | Rule |
|---|---|
| **EA-20** | **Bengali is never rendered as an image to guarantee a font** (`VB-009` `BR-06`, `VB-005` `BF-05`, `CG-011` `AT-07`). This removes the only apparent solution to the problem and is correct: an image of Bengali cannot be translated, resized, read aloud, or shown when images are off |
| **EA-21** | **The font stack is declared, in order, on every text element** — `'Hind Siliguri', 'Noto Sans Bengali', 'Nirmala UI', 'Vrinda', 'SolaimanLipi', sans-serif` (`VB-005` §7.1) — and the layout is designed at rank 2 |
| **EA-22** | **Line height accommodates both rank 1 and rank 2 metrics**, minimum **1.7** (`VB-005` `BF-02`, `VB-009` §4) |
| **EA-23** | **No fixed pixel height on any container holding Bengali** (`BF-03`, `VB-009` `MM-02`) |
| **EA-24** | **Bengali body is 16 px minimum in email** (`BF-04`, `VB-009` §3), one step above the English 15 px |
| **EA-25** | **Every bilingual template is rendered and visually inspected on Gmail Android and Outlook desktop before release** (`BF-06`). **Conjunct breakage is only visible by looking**, and a broken conjunct in a payment receipt reaches 250,000 people |

### 4.5 Image-off, alt text and accessibility

| # | Rule |
|---|---|
| **EA-26** | **Every image carries alt text; decorative images carry empty alt** (`VB-005` `AC-02`). The logo's alt text is **"1000FiX Services"** (`AC-03`) |
| **EA-27** | **Alt text is bilingual on bilingual templates** — it is a user-visible string (`CG-010` §5, `CG-011` `AT-05`) |
| **EA-28** | **Alt text is styled**, so that when images are blocked the alternative renders in the correct colour and size rather than as unstyled default text |
| **EA-29** | **The email is proof-read with images disabled** as a release step, not as a spot check. Many clients block images by default and this is the state a large share of recipients see first |
| **EA-30** | **Colour is never the only signal**; status is stated in words (`VB-005` `AC-07`, `CG-011` `CL-01`) |
| **EA-31** | **Buttons are markup, never images** — the VML bulletproof pattern (`VB-005` §6). **An image button is invisible with images off, which is the moment the recipient most needs the action** |
| **EA-32** | **Minimum 44 px touch targets** (`VB-005` `AC-08`, WCAG SC 2.5.5) |

### 4.6 Weight, hosting and permanence

#### 4.6.1 Budgets

| Budget | Ceiling | Authority |
|---|---:|---|
| **Total HTML** | **102 KB** | `VB-005` `DL-01` — Gmail clips above this, hiding the footer and the preference link |
| Total image weight | **200 KB** | `DL-02` |
| **Logo** | **≤ 12 KB** | `EA-33` |
| Status icon | ≤ 4 KB | |
| Illustration | ≤ 60 KB | |
| Photograph | ≤ 120 KB | |
| Image-to-text ratio | **≤ 40%** | `DL-03` |

| # | Rule |
|---|---|
| **EA-33** | **The 102 KB ceiling is a hard limit measured on the rendered HTML**, and the footer is the part that gets clipped — **which is where the preference link and the legal entity live** (`NT-002`) |
| **EA-34** | **The image budget is spent on the logo and nothing else in transactional email** (`EA-03`) |

#### 4.6.2 Hosting and permanence — the section this file exists for

> **`EA-35`: an ERP email is read years after it is sent.** A payment receipt, a warranty
> certificate notification or a payout statement is retrieved from a mailbox as evidence long
> after the campaign that shares its assets has been retired. **A hosted image URL in a
> transactional email is a permanent commitment.**

| # | Rule |
|---|---|
| **EA-36** | **Transactional email assets are served from a stable, owned, short domain path that is never restructured** — the same commitment `DT-044` `PL-06` makes for the label payload domain, and for the same reason: **changing it invalidates everything already issued** |
| **EA-37** | **A published asset URL is immutable** (`MM-012` §4.4). A change is a **new URL**; the old one continues to resolve. **Overwriting the file at a URL changes emails already delivered**, which for a payment receipt is a change to a record |
| **EA-38** | **Transactional and marketing assets are served from separate paths**, matching `VB-005` `DL-05`'s separation of sending domains — so a marketing asset retirement cannot break a receipt |
| **EA-39** | **Asset retirement never deletes a transactional asset.** `MM-012` §4.7's retirement flow **excludes** the transactional email path; assets there are retired from *use* and retained in *service* indefinitely |
| **EA-40** | **Cache headers are long and explicit**; assets are versioned in the path rather than by query string, which several proxies strip |
| **EA-41** | **A quarterly link check runs across every asset URL referenced by a live template**, and a 404 is an incident, not a backlog item |

### 4.7 The HTML partial kit and the build

| # | Partial | Contents |
|---:|---|---|
| **P1** | **Document shell** | Doctype, `lang`, meta, conditional comments, reset, `data-ogsc`/`data-ogsb` dark-mode hooks |
| **P2** | **Preheader** | Hidden 40–90 character block (`VB-005` §4) |
| **P3** | **Header** | 64 px, logo light/dark swap, 2 px `#1E5F8A` rule |
| **P4** | **Body container** | 600 px max width, 24 px padding, single column |
| **P5** | **Fact block** | Two-column real table with header cells (`AC-06`) |
| **P6** | **Bulletproof button** | VML for Outlook, anchor elsewhere (`VB-005` §6) |
| **P7** | **Support block** | Hotline 16743 |
| **P8** | **Footer** | Entity, address, why received, preference link, unsubscribe **where applicable only** |
| **P9** | **Plain-text template** | The parity part (`VB-005` §8) |

| # | Rule |
|---|---|
| **EA-42** | **One partial kit. Six libraries consume it and none forks it** — the failure `VB-005` §1 names: *"six template libraries, six shells"* |
| **EA-43** | **Table-based layout, critical CSS inlined at build time**, `<style>` treated as an enhancement (`VB-005` `CB-01`, `CB-02`) |
| **EA-44** | **The plain-text part is generated as a first-class deliverable and carries the same facts** (`VB-005` `PT-01`…`PT-06`) — never a stub, always with the hotline and the full CTA URL |
| **EA-45** | **Bengali plain text is UTF-8 and is checked for mojibake** (`PT-05`); **Bengali is never hard-wrapped**, which breaks conjuncts (`PT-06`) |
| **EA-46** | **The build lints**: total size, image weight, alt-text presence, banned link text, contrast pairs, single CTA, both `color` and `background-color` set, font stack present, no SVG, no base64, no fixed height on a Bengali container |
| **EA-47** | **`unsubscribe` appears on lifecycle and marketing email only.** A recipient cannot opt out of a payment receipt (`VB-005` §4, `NT-002`) — and the partial makes this a build-time decision, not an author's |
| **EA-48** | **No tracking pixel in transactional email without a `LG-011` position.** An open-tracking pixel is a tracking technology; **`LG-011` governs it, `LG-008` §4.2 must carry a purpose for it, and neither currently does** — `O-05` |

### 4.8 Deliverable specification

**The `CG-009` §3 required addition for Category 19.**

| Attribute | Specification |
|---|---|
| **Master format** | **PNG-24** for logos, icons and line art; **JPEG** for photography; **no SVG, no WebP, no AVIF, no base64** |
| **Derived formats** | None — email consumes the delivered asset directly (`EA-13`) |
| **Dimensions** | Supplied **@2×**, displayed ≤ 552 px wide; `width`/`height` set as HTML attributes |
| **Colour** | sRGB, profile embedded; **light and dark variants both authored** (`EA-15`, `EA-16`) |
| **Compression** | **Logo ≤ 12 KB · icon ≤ 4 KB · illustration ≤ 60 KB · photograph ≤ 120 KB · total images ≤ 200 KB · total HTML ≤ 102 KB** |
| **Text in image** | **None**, logo wordmark excepted (`EA-06`) |
| **Alt text** | Mandatory, **bilingual**, styled; logo alt = "1000FiX Services" |
| **Fonts** | **Not embedded. Declared as a stack and designed at rank 2** (`EA-21`) |
| **Hosting** | Stable owned path, **immutable URL**, versioned in the path, long cache, **transactional path never deleted** (`EA-36`…`EA-39`) |
| **Metadata** | XMP title, description, `dc:relation` = owning `NT-` library, theme variant, licence |
| **Naming** | `MM-012` §4.3, carrying the theme variant |
| **Markup** | The nine partials in §4.7, plus the plain-text template |
| **Evidence** | **Rendering results across the §4.9 client matrix**, in both themes, with images on and off, in both languages |

### 4.9 The client test matrix

**Nothing ships on a preview tool alone.** `VB-005` `CB-05` and §13 require this and record the
test account set as outstanding.

| Client | Engine | Themes | Images | Language |
|---|---|---|---|---|
| **Outlook desktop (Windows)** | Word HTML | Light + partial inversion | On + off | EN + **BN** |
| Outlook.com / new Outlook | Own | Light + inversion | On + off | EN + BN |
| **Gmail web** | Own DOM, CSS sanitised | Light + varies | On + off | EN + BN |
| **Gmail Android** | Own | Varies | On + off | **BN — the conjunct case** |
| **Apple Mail iOS** | WebKit | Light + dark | On + off | EN + BN |
| Yahoo / other | Mixed | Assume Outlook-level | On + off | EN |

| # | Rule |
|---|---|
| **EA-49** | **The matrix is executed in full before any library releases**, and **Bengali rendering on Gmail Android and Outlook desktop is manual visual inspection** (`VB-005` `BF-06`, §13) |
| **EA-50** | **A client behaviour discovered during testing amends this file**, not the template. That is how a P3 evidence base becomes P1 |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`VB-005_Email_Brand_Template_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-005_Email_Brand_Template_Standard.md) | The shell, the client baseline, the colour pairs, the buttons, the Bengali stack, plain-text parity, deliverability — everything this file produces assets for |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) · [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](../11_Localisation_Bengali/BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | The six-rank stack, the email floor, `BR-06`'s never-as-an-image rule |
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) · [`VB-006_Design_System_Content_Standards.md`](../01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md) | Contrast findings; co-branding `VB-003` `LG-06`; the button-label contract |
| [`NT-001_Notification_Strategy_and_Event_Channel_Matrix.md`](../04_Notification_and_Messaging/NT-001_Notification_Strategy_and_Event_Channel_Matrix.md) · [`NT-002_Notification_Preference_and_Consent_Copy.md`](../04_Notification_and_Messaging/NT-002_Notification_Preference_and_Consent_Copy.md) · [`NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md`](../04_Notification_and_Messaging/NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md) | Which events send; the footer and unsubscribe decision `EA-47` builds in; frequency |
| [`NT-009_Email_Template_Library_Customer_Transactional.md`](../04_Notification_and_Messaging/04C_Email/NT-009_Email_Template_Library_Customer_Transactional.md) · [`NT-010_Email_Template_Library_Corporate_and_B2B.md`](../04_Notification_and_Messaging/04C_Email/NT-010_Email_Template_Library_Corporate_and_B2B.md) · [`NT-011_Email_Template_Library_Vendor_and_Supplier.md`](../04_Notification_and_Messaging/04C_Email/NT-011_Email_Template_Library_Vendor_and_Supplier.md) · [`NT-012_Email_Template_Library_Seller_and_Partner.md`](../04_Notification_and_Messaging/04C_Email/NT-012_Email_Template_Library_Seller_and_Partner.md) · [`NT-013_Email_Template_Library_Brand_Partner_Claims.md`](../04_Notification_and_Messaging/04C_Email/NT-013_Email_Template_Library_Brand_Partner_Claims.md) · [`NT-014_Email_Template_Library_Internal_and_HR.md`](../04_Notification_and_Messaging/04C_Email/NT-014_Email_Template_Library_Internal_and_HR.md) | The six consumers of the partial kit |
| [`NT-025_Notification_Failure_and_Fallback_Copy.md`](../04_Notification_and_Messaging/NT-025_Notification_Failure_and_Fallback_Copy.md) · [`NT-026_Message_Template_Governance_and_Change_Log.md`](../04_Notification_and_Messaging/NT-026_Message_Template_Governance_and_Change_Log.md) | Fallback behaviour; where a template change is recorded |
| [`BN-014_Bengali_Notification_and_SMS_Pack.md`](../11_Localisation_Bengali/BN-014_Bengali_Notification_and_SMS_Pack.md) | The Bengali message content rendered through these partials |
| [`CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) · [`TS-016_Accessibility_Test_Script_Pack.md`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md) | §4.5 obligations and where they are verified |
| [`CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) · [`CG-012_Content_Sourcing_and_Evidence_Rules.md`](../00_Content_Governance_and_Standards/CG-012_Content_Sourcing_and_Evidence_Rules.md) | Alt text as a user-visible string; the P3 evidence position on client behaviour |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md) · [`LG-011_Cookie_and_Tracking_Policy.md`](../10_Legal_Policy_and_Compliance/LG-011_Cookie_and_Tracking_Policy.md) | `EA-48` — the tracking-pixel position and the purpose that would have to exist |
| [`CM-005_Wave_Launch_Communication_Kit.md`](../16_Change_Management_and_Comms/CM-005_Wave_Launch_Communication_Kit.md) · [`CM-009_Internal_Newsletter_and_Update_Template.md`](../16_Change_Management_and_Comms/CM-009_Internal_Newsletter_and_Update_Template.md) | Two consumers outside `NT`; **both record `MM` as holding zero files** |
| [`MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) | §4.4 — the web chain this file deliberately inverts; metadata; acceptance |
| [`MM-004_Icon_Set_Requirements.md`](MM-004_Icon_Set_Requirements.md) · [`MM-005_Illustration_and_Empty_State_Artwork_Brief.md`](MM-005_Illustration_and_Empty_State_Artwork_Brief.md) · [`MM-009_Photography_Brief_Branches_Workshop_and_Field.md`](MM-009_Photography_Brief_Branches_Workshop_and_Field.md) | The sources of E3, E6 and E7, rasterised for email |
| [`MM-010_PDF_and_Print_Template_Design_Specification.md`](MM-010_PDF_and_Print_Template_Design_Specification.md) | PDF attachments carried by email; the print counterpart |
| [`MM-012_Digital_Asset_Management_and_Naming_Standard.md`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) | Naming, immutability, and the retirement exclusion `EA-39` requires |
| `M24` | Where an issued email and its attachment are retained |
| `04-00` `PS-03`, `PS-04` · `05-06` §9 | Bengali default, AA, locale formats |

| Depended on by |
|---|
| `NT-009`…`NT-014` · `CM-005` · `CM-009` · `BN-014` · the email build pipeline |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per wave**, matching `VB-005` §14 |
| Trigger for out-of-cycle review | A client rendering change · a deliverability incident · a broken asset URL · a new email library · a `VB-005` revision · a dark-mode behaviour change |
| Owner | **Brand Lead with Platform Engineering** |
| Approver | Content Design Lead with Brand Lead (`CG-002` §5.4, class D) |
| Enforcement | §4.7's build lint on every template change; the §4.9 matrix before every library release; **quarterly link check across every live asset URL** (`EA-41`) |
| Effectiveness measure | **Broken asset URLs in live templates: target zero.** Templates clipped by Gmail: target zero. Bengali conjunct defects found in production: target zero |
| Change log | [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) — **written; Category 99 completed 2026-08-18**. Every decision under this file is logged there |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is registered at W2 and [`CM-005`](../16_Change_Management_and_Comms/CM-005_Wave_Launch_Communication_Kit.md) `O-05` records a W1 need**, naming `MM-010` and `MM-011` as *"the layout authority for K1–K5; without them each wave's assets are laid out to taste"*. `CM-009` records the same absence. **`VB-005` is itself W2, so the shell and the assets are aligned — the misalignment is with the `CM` consumers.** `AUDIT-018` `EO-03` asked for the sequencing basis to be corrected once, register-wide; **reported, not patched** | Programme Content Lead with Change Lead | **W1 — reported, not patched** |
| **O-02** | **No email client test account set exists.** `VB-005` §14 assigns it to Platform Engineering and records it as outstanding; `MM-001` `O-07` records the same gap for devices and printers. **Without it §4.9 cannot run, and both this file's and `VB-005`'s client-behaviour sources stay at `class: P3`** — which `VB-005` states means *"no template may be approved on the P3 evidence alone"* | Platform Engineering | **W2 — before any library releases** |
| **O-03** | **No asset hosting domain, path convention or permanence commitment exists.** `EA-36`…`EA-39` place a **permanent** obligation on Platform Engineering — the same shape as `DT-044` `PL-06`, which is also recorded as outstanding. **A transactional asset path that is later restructured breaks every receipt already delivered**, and there is no way to fix that retrospectively | Chief Technology Officer with Platform Engineering | **W2 — before the first transactional send** |
| **O-04** | **The Bengali email rendering position rests on `class: P3` evidence** carried from `VB-005`. `EA-25` requires manual inspection on Gmail Android and Outlook desktop; **until `O-02` is resolved, `EA-21`'s stack ordering and `EA-22`'s line height are designed against reported behaviour rather than observed behaviour** | Localisation Lead with Platform Engineering | **W2** |
| **O-05** | **The tracking-pixel position is undecided** (`EA-48`). `LG-011` governs tracking technologies and `LG-008` §4.2 requires a stated purpose before processing begins (`PI-02`, `BRU-GRC-16`); **no purpose covering email open-tracking exists in the inventory.** Marketing will ask for it; the answer must exist before the first library ships, not after | Chief Data Officer with Legal Counsel | **W2** |
| **O-06** | **No accessibility reviewer is named** for §4.5 — the **twelfth** file to record it. `EA-29`'s images-off proof-read has no owner | Content Design Lead | **W2** |
| **O-07** | **`EA-15`'s dark-logo fallback has an unresolved edge.** Where a client honours neither the media query nor `data-ogsc` **and** inverts the background, the light logo lands on dark. §4.4.1 offers two mitigations — a legible-both-ways light logo, or a solid light block behind it — and **neither has been chosen**; the second is a shell decision belonging to `VB-005` | Brand Lead with Platform Engineering | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections in order; the `CG-009` `MM` deliverable table at §4.8; §7 added per category convention
- [x] **Asset inventory kept deliberately short, following `VB-005` `SH-02`/`SH-03` to their conclusion — almost nothing in an ERP email should be an image**
- [x] Transactional email capped at two images, with footer marks required to be text
- [x] Dimensions and density fixed, with `width`/`height` as HTML attributes because Outlook ignores CSS
- [x] **Email formally excluded from `MM-001`'s AVIF/WebP chain, with the inversion stated so it is not later "corrected"**
- [x] SVG and base64 prohibited with reasons
- [x] **Dark-mode assets required to be authored in both themes, with the transparent-PNG trap named**
- [x] **Bengali never rendered as an image, removing the only apparent solution and stating why that is correct**
- [x] Font stack, line height, container height and minimum size carried from `VB-005` and `VB-009` by identifier
- [x] Images-off design made a release step; buttons required to be markup, not images
- [x] Weight budgets stated per asset against the 102 KB clip, with the clipped footer's contents named
- [x] **URL permanence treated as the file's central problem, with immutable URLs and a retirement exclusion for the transactional path**
- [x] Nine markup partials specified as one kit six libraries consume without forking
- [x] Build lint enumerated; plain-text parity made a first-class deliverable
- [x] **The tracking-pixel question raised as a privacy position rather than a technical one**
- [x] Client test matrix given with themes, images-off and both languages, and manual Bengali inspection required
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] English-only per `CG-010` §3.2; 22 of the 26 `NT` files it serves are bilingual
- [ ] **`O-02` no client test account set — outstanding; the evidence base stays `P3` and no template may be approved on it**
- [ ] **`O-03` no hosting domain or permanence commitment — outstanding; a restructure would break every delivered receipt**
- [ ] **`O-05` the tracking-pixel position is undecided — outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Brand Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
